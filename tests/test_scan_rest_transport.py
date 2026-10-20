"""The REST scanner client keeps credentials on the API origin and bounds retries, offline and without sleeping."""
import contextlib
from email.message import Message
import io
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPSHandler, build_opener as real_build_opener
from urllib.response import addinfourl

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import scan_sources as scanner
from scan_sources import APIOnlyRedirect, GitHub, ScanError, is_api_origin

TOKEN = 'test-token-not-a-credential'
WALL = 1_800_000_000


class Clock:
    """Injected monotonic and wall time; sleeping only advances the counter."""
    def __init__(self):
        self.now, self.sleeps, self.on_first_sleep = 100.0, [], None

    def monotonic(self):
        return self.now

    def time(self):
        return WALL + self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds
        hook, self.on_first_sleep = self.on_first_sleep, None
        if hook:
            hook()


class FakeHTTPS(HTTPSHandler):
    """Replaces the real HTTPS handler; every request is answered by `respond` and logged."""
    handler_order = 100

    def __init__(self, clock, respond):
        super().__init__()
        self.clock, self.respond, self.requests, self.responses = clock, respond, [], []

    def https_open(self, request):
        self.requests.append({'url': request.full_url, 'host': urlsplit(request.full_url).hostname,
                              'authorization': request.get_header('Authorization'), 'at': self.clock.now})
        outcome = self.respond(request, len(self.requests))
        if isinstance(outcome, BaseException):
            raise outcome
        status, headers, body = outcome
        message = Message()
        for key, value in headers.items():
            message[key] = value
        response = addinfourl(io.BytesIO(body), message, request.full_url, status)
        response.msg = 'fake'
        self.responses.append(response)
        return response


def ok(body=b'{"ok": true}', headers=None):
    return 200, headers or {}, body


class RESTTransportTests(unittest.TestCase):
    def setUp(self):
        blocked = AssertionError('real network access in an offline transport test')
        for target, name in ((socket.socket, 'connect'), (socket, 'getaddrinfo'), (socket, 'create_connection')):
            patcher = patch.object(target, name, side_effect=blocked)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.clock = Clock()
        patcher = patch.object(scanner, 'time', self.clock)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.output = io.StringIO()
        redirect = contextlib.redirect_stdout(self.output)
        redirect.__enter__()
        self.addCleanup(redirect.__exit__, None, None, None)

    def client(self, respond):
        self.https = FakeHTTPS(self.clock, respond)
        # A refused redirect leaves its response for the garbage collector; close test bodies explicitly.
        self.addCleanup(lambda https=self.https: [response.close() for response in https.responses])
        patcher = patch.object(scanner, 'build_opener', lambda *handlers: real_build_opener(*handlers, self.https))
        patcher.start()
        self.addCleanup(patcher.stop)
        return GitHub(TOKEN, requests_per_second=10)

    def assert_sanitized(self, error, reason, status=None):
        self.assertEqual((error.reason, error.status, str(error)), (reason, status, reason))
        self.assertIsNone(error.__cause__)
        self.assertNotIn(TOKEN, str(error) + self.output.getvalue())

    def test_off_origin_redirects_are_refused_before_authorization_is_forwarded(self):
        for location in ('https://evil.example/steal', 'http://api.github.com/repositories/1',
                         'https://api.github.com:8443/repositories/1', 'https://user@api.github.com/repositories/1',
                         'https://api.github.com.evil.example/repositories/1'):
            with self.subTest(location=location):
                api = self.client(lambda request, count: (302, {'Location': location}, b''))
                with self.assertRaises(ScanError) as caught:
                    api.json('/repositories/1')
                self.assert_sanitized(caught.exception, 'refused-non-github-api-redirect', 302)
                self.assertEqual([(row['host'], row['authorization']) for row in self.https.requests],
                                 [('api.github.com', 'Bearer ' + TOKEN)])

    def test_same_origin_redirect_is_followed_on_the_api_host(self):
        def respond(request, count):
            if count == 1:
                return 301, {'Location': 'https://api.github.com/repositories/2'}, b''
            return ok(b'{"id": 2}')
        api = self.client(respond)
        self.assertEqual(api.json('/repos/old/name'), {'id': 2})
        self.assertEqual([row['url'] for row in self.https.requests],
                         ['https://api.github.com/repos/old/name', 'https://api.github.com/repositories/2'])
        self.assertTrue(all(row['host'] == 'api.github.com' for row in self.https.requests))

    def test_origin_check_and_endpoint_validation_need_no_request(self):
        self.assertTrue(is_api_origin('https://api.github.com/repositories/1'))
        for url in ('http://api.github.com/', 'https://api.github.com:444/', 'https://u:p@api.github.com/',
                    'https://API.github.com.evil/', 'https://[::1/', 'ftp://api.github.com/'):
            self.assertFalse(is_api_origin(url), url)
        api = self.client(lambda request, count: ok())
        for path in ('@evil.example/x', 'repositories/1', ':8443/x'):
            with self.assertRaises(ScanError) as caught:
                api.get(path)
            self.assert_sanitized(caught.exception, 'invalid-api-endpoint')
        self.assertEqual(self.https.requests, [])
        with self.assertRaises(ScanError):
            APIOnlyRedirect().redirect_request(None, None, 307, 'redirect', {}, 'https://example.com/')

    def test_primary_limit_pause_is_shared_with_a_concurrent_search(self):
        later = []

        def respond(request, count):
            if count == 1:
                return 403, {'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': str(int(WALL + self.clock.now) + 30),
                             'X-RateLimit-Resource': 'core'}, b'{"message": "API rate limit exceeded"}'
            return ok()
        api = self.client(respond)
        start = self.clock.now
        # Another worker asks for a search while the first request is waiting out the pause.
        self.clock.on_first_sleep = lambda: later.append(api.json('/search/repositories?q=x', search=True))
        self.assertEqual(api.json('/repositories/1'), {'ok': True})
        self.assertEqual(later, [{'ok': True}])
        first, search, retry = self.https.requests
        self.assertEqual((first['url'], retry['url']), ('https://api.github.com/repositories/1',) * 2)
        self.assertTrue(search['url'].startswith('https://api.github.com/search/'))
        self.assertGreaterEqual(search['at'], start + 31)
        self.assertGreaterEqual(retry['at'], start + 31)
        self.assertIn('RATE_LIMIT resource=core retry_seconds=31', self.output.getvalue())

    def test_secondary_limit_without_retry_header_pauses_core_requests_for_a_minute(self):
        later = []

        def respond(request, count):
            if count == 1:
                return 403, {}, b'{"message": "You have exceeded a secondary rate limit"}'
            return ok()
        api = self.client(respond)
        start = self.clock.now
        self.clock.on_first_sleep = lambda: later.append(api.json('/repositories/9'))
        self.assertEqual(api.json('/search/repositories?q=x', search=True), {'ok': True})
        self.assertEqual(later, [{'ok': True}])
        self.assertTrue(all(row['at'] >= start + 60 for row in self.https.requests[1:]))
        self.assertIn('RATE_LIMIT resource=search retry_seconds=60', self.output.getvalue())

    def test_retry_after_header_sets_the_shared_pause(self):
        api = self.client(lambda request, count: (429, {'Retry-After': '45'}, b'') if count == 1 else ok())
        start = self.clock.now
        self.assertEqual(api.json('/repositories/1'), {'ok': True})
        self.assertGreaterEqual(self.https.requests[1]['at'], start + 45)
        self.assertLessEqual(max(self.clock.sleeps), 5)

    def test_rate_limits_server_errors_and_network_failures_stop_after_four_attempts(self):
        cases = [
            ((429, {'Retry-After': '1'}, b''), 'http-429', 429),
            ((403, {'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': str(WALL)}, b''), 'http-403', 403),
            ((503, {}, b'upstream ' + TOKEN.encode()), 'http-503', 503),
            (URLError('connection refused'), 'network-failure', None),
            (TimeoutError('timed out'), 'network-failure', None),
            (ConnectionResetError('reset'), 'network-failure', None),
        ]
        for outcome, reason, status in cases:
            with self.subTest(reason=reason, outcome=type(outcome).__name__):
                self.clock.sleeps.clear()
                api = self.client(lambda request, count: outcome)
                with self.assertRaises(ScanError) as caught:
                    api.json('/repositories/1')
                self.assert_sanitized(caught.exception, reason, status)
                self.assertEqual(len(self.https.requests), 4)
                self.assertLessEqual(max(self.clock.sleeps, default=0), 5)

    def test_client_errors_are_not_retried(self):
        api = self.client(lambda request, count: (404, {}, b'{"message": "Not Found"}'))
        with self.assertRaises(ScanError) as caught:
            api.json('/repositories/1')
        self.assert_sanitized(caught.exception, 'http-404', 404)
        self.assertEqual(len(self.https.requests), 1)

    def test_oversized_and_malformed_responses_have_fixed_error_codes(self):
        with patch.object(scanner, 'MAX_API_BYTES', 8):
            api = self.client(lambda request, count: ok(b'{"a": 12}'))
            with self.assertRaises(ScanError) as caught:
                api.json('/repositories/1')
            self.assert_sanitized(caught.exception, 'api-response-too-large')
            self.assertEqual(len(self.https.requests), 1)
            api = self.client(lambda request, count: ok(b'{"a": 1}'))
            self.assertEqual(api.json('/repositories/1'), {'a': 1})
        for body in (b'{', b'\xff\xfe', b'<html>' + TOKEN.encode()):
            with self.subTest(body=body[:6]):
                api = self.client(lambda request, count: ok(body))
                with self.assertRaises(ScanError) as caught:
                    api.json('/repositories/1')
                self.assert_sanitized(caught.exception, 'invalid-api-json')

    def test_rate_headers_are_recorded_without_credentials(self):
        headers = {'X-RateLimit-Resource': 'core', 'X-RateLimit-Remaining': '4999',
                   'X-RateLimit-Limit': '5000', 'X-RateLimit-Reset': str(WALL + 3600)}
        api = self.client(lambda request, count: ok(headers=headers))
        api.json('/repositories/1')
        self.assertEqual(api.rate, {'core': {'remaining': 4999, 'limit': 5000, 'reset': WALL + 3600}})
        self.assertEqual(self.clock.sleeps, [])


if __name__ == '__main__':
    unittest.main()
