"""The link checker applies the public HTTPS URL check to every redirect hop before following it."""
from email.message import Message
import io
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch
from urllib.request import BaseHandler, ProxyHandler, build_opener
from urllib.response import addinfourl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_links
from check_links import MAX_REDIRECTS, check_url


class FakeHTTPS(BaseHandler):
    """Serve HTTPS responses from a table of URL -> (status, Location); record every request made."""
    handler_order = 100

    def __init__(self, routes):
        self.routes, self.requested = routes, []

    def https_open(self, request):
        url = request.full_url
        self.requested.append(url)
        if url not in self.routes:
            raise AssertionError('unexpected request ' + url)
        status, location = self.routes[url]
        headers = Message()
        if location:
            headers['Location'] = location
        response = addinfourl(io.BytesIO(b'x'), headers, url, status)
        response.msg = 'Moved' if location else 'OK'
        return response

    http_open = https_open


class RedirectTests(unittest.TestCase):
    def check(self, url, routes):
        fake = FakeHTTPS(routes)
        blocked = AssertionError('network access in a unit test')
        # No proxy, no socket: every response comes from the table.
        with patch.object(check_links, 'build_opener', lambda *handlers: build_opener(ProxyHandler({}), *handlers, fake)), \
                patch.object(socket.socket, 'connect', side_effect=blocked), \
                patch.object(socket, 'getaddrinfo', side_effect=blocked), patch.object(check_links.time, 'sleep'):
            return check_url(url), fake.requested

    def test_public_https_publisher_and_github_redirects_are_followed(self):
        result, requested = self.check('https://doi.org/10.1145/3658644.3690307', {
            'https://doi.org/10.1145/3658644.3690307': (302, 'https://dl.acm.org/doi/10.1145/3658644.3690307'),
            'https://dl.acm.org/doi/10.1145/3658644.3690307': (200, None)})
        self.assertEqual((result['status'], result['http_status']), ('ok', 200))
        self.assertEqual(result['attempts'][0]['final_url'], 'https://dl.acm.org/doi/10.1145/3658644.3690307')
        self.assertEqual(len(requested), 2)
        # A renamed repository redirects within GitHub; a relative Location resolves against the current URL.
        result, requested = self.check('https://github.com/old-owner/tool', {
            'https://github.com/old-owner/tool': (301, 'https://github.com/new-owner/tool'),
            'https://github.com/new-owner/tool': (302, '/new-owner/tool/tree/main'),
            'https://github.com/new-owner/tool/tree/main': (200, None)})
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(requested[-1], 'https://github.com/new-owner/tool/tree/main')

    def test_downgrade_credential_and_non_public_literal_redirects_are_refused_before_the_next_request(self):
        for target in ('http://example.org/paper', 'https://user:secret@example.org/paper', 'https://127.0.0.1/admin',
                       'https://10.0.0.8/', 'https://[::1]/', 'https://169.254.169.254/latest/meta-data/',
                       'https://localhost/', 'https://2130706433/', 'https://printer.local/'):
            with self.subTest(target=target):
                result, requested = self.check('https://example.org/start', {'https://example.org/start': (301, target)})
                self.assertEqual(requested, ['https://example.org/start'])
                self.assertEqual((result['status'], result['http_status']), ('inconclusive', 301))
                self.assertTrue(result['reason'].startswith('Redirect not followed: redirect target '), result['reason'])
                attempt = result['attempts'][-1]
                self.assertEqual(attempt['final_url'], 'https://example.org/start')
                self.assertIn('redirect_refused', attempt)
                self.assertNotIn('secret', str(result))
        result, _ = self.check('https://example.org/start', {'https://example.org/start': (301, 'https://user:secret@example.org/p')})
        self.assertEqual(result['attempts'][-1]['refused_redirect_url'], 'https://example.org/p')

    def test_a_refused_hop_later_in_the_chain_stops_there(self):
        result, requested = self.check('https://example.org/a', {
            'https://example.org/a': (302, 'https://example.org/b'), 'https://example.org/b': (302, 'http://example.org/c')})
        self.assertEqual(requested, ['https://example.org/a', 'https://example.org/b'])
        self.assertEqual((result['status'], result['attempts'][-1]['final_url']), ('inconclusive', 'https://example.org/b'))

    def test_the_hop_limit_allows_five_redirects_and_refuses_the_sixth(self):
        def chain(length):
            routes = {f'https://example.org/{n}': (301, f'https://example.org/{n + 1}') for n in range(length)}
            routes[f'https://example.org/{length}'] = (200, None)
            return routes
        result, requested = self.check('https://example.org/0', chain(MAX_REDIRECTS))
        self.assertEqual((result['status'], len(requested)), ('ok', MAX_REDIRECTS + 1))
        result, requested = self.check('https://example.org/0', chain(MAX_REDIRECTS + 1))
        self.assertEqual(result['status'], 'inconclusive')
        self.assertIn(f'more than {MAX_REDIRECTS} redirects', result['reason'])
        self.assertEqual(len(requested), MAX_REDIRECTS + 1)
        self.assertNotIn(f'https://example.org/{MAX_REDIRECTS + 1}', requested)
        # A loop is bounded the same way.
        result, requested = self.check('https://example.org/x', {
            'https://example.org/x': (302, 'https://example.org/y'), 'https://example.org/y': (302, 'https://example.org/x')})
        self.assertEqual((result['status'], len(requested)), ('inconclusive', MAX_REDIRECTS + 1))

    def test_a_missing_page_after_a_redirect_is_still_confirmed_by_a_second_request(self):
        result, requested = self.check('https://example.org/moved', {
            'https://example.org/moved': (301, 'https://example.org/gone'), 'https://example.org/gone': (404, None)})
        self.assertEqual((result['status'], result['http_status']), ('dead', 404))
        self.assertEqual(len(requested), 4)

    def test_an_invalid_starting_url_is_never_requested(self):
        result, requested = self.check('http://example.org/', {})
        self.assertEqual((result['status'], requested), ('inconclusive', []))


if __name__ == '__main__':
    unittest.main()
