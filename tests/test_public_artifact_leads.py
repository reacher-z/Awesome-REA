"""Discovery receipts must stay source-bound, private-data-free and uncurated."""
from copy import deepcopy
import base64
import hashlib
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import collect_public_artifact_leads as discovery

PIN = 'a' * 40
POST = 'https://x.com/i/status/2110835101583966520'


class Response(io.BytesIO):
    def __init__(self, raw, headers=None):
        super().__init__(raw)
        self.headers = headers or {}


class Opener:
    def __init__(self, *responses):
        self.responses, self.calls = list(responses), []

    def open(self, request, timeout):
        self.calls.append((request, timeout))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def error(url, status, headers=None):
    return HTTPError(url, status, 'REMOTE_SECRET_BODY', headers or {}, io.BytesIO(b'REMOTE_SECRET_BODY'))


def readme(raw=b'# Project\nhttps://github.com/example/artifact\n'):
    return {'path': 'README.md', 'content': base64.encodebytes(raw).decode(),
            'sha': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()}


class FixtureClient:
    token = 'SENTINEL-NOT-A-REAL-CREDENTIAL'

    def __init__(self, *, private=False, mismatch=False, deny_robots=False, partial_graphql=False):
        self.calls = []
        self.private, self.mismatch, self.deny_robots, self.partial_graphql = private, mismatch, deny_robots, partial_graphql

    def json(self, url, data=None):
        self.calls.append(url)
        if url.endswith('/graphql'):
            result = {'data': {f'r{i}': {'nameWithOwner': repo, 'isPrivate': self.private,
                                       'defaultBranchRef': {'target': {'oid': PIN}}}
                               for i, repo in enumerate(discovery.README_REPOS)}}
            result['data']['upstream'] = None if self.partial_graphql else {'isPrivate': self.private, 'discussions': {'nodes': [
                {'number': 12, 'body': POST + '\nhttps://github.com/EXAMPLE/ARTIFACT\nPRIVATE_BODY_ONLY'},
                {'number': 13, 'body': 'A project request without an artifact.'}]}, 'newest': {'nodes': [
                {'number': 12, 'body': 'Repeated current discussion'},
                {'number': 14, 'body': 'https://github.com/example/fresh'}]}}
            if self.partial_graphql:
                result['errors'] = [{'message': 'REMOTE_SECRET_BODY'}]
            return result
        result = readme()
        if self.mismatch:
            result['sha'] = '0' * 40
        return result

    def fetch(self, url):
        self.calls.append(url)
        if url.endswith('/robots.txt'):
            return b'User-agent: *\nDisallow: /\n' if self.deny_robots else b'User-agent: *\nAllow: /\n'
        if url.startswith('https://' + discovery.X_EMBED_HOST + '/'):
            return json.dumps({'type': 'rich', 'author_url': 'https://x.com/fixture',
                               'html': '<blockquote><p>PRIVATE_TWEET_TEXT</p><a href="' + POST + '">post</a></blockquote>'}).encode()
        if url == discovery.WEB_INDEXES[0]:
            return b'<a href="/zh-cn/cases/demo">case</a>'
        if '/cases/' in url:
            return ('<a href="' + POST + '">original</a><a href="https://github.com/example/web-result">code</a>').encode()
        return b'<a href="https://github.com/example/artifact">project</a>'


class PublicTransportTests(unittest.TestCase):
    def test_default_opener_disables_urllib_automatic_redirects(self):
        opener = Opener()
        with patch.object(discovery, 'build_opener', return_value=opener) as make:
            client = discovery.PublicClient('fixture')
        handler, = make.call_args.args
        self.assertIsInstance(handler, discovery.NoRedirect)
        self.assertIsNone(handler.redirect_request(None, None, 302, '', {}, 'https://gitlab.com/api'))
        self.assertIs(client.opener, opener)

    def test_auth_is_only_sent_to_github_and_cross_origin_redirect_is_refused(self):
        opener = Opener(Response(b'{}'), Response(b'public'),
                        error('https://api.github.com/graphql', 302, {'Location': 'https://gitlab.com/api'}))
        client = discovery.PublicClient('SENTINEL-NOT-A-REAL-CREDENTIAL', opener=opener)
        client.fetch('https://api.github.com/graphql', data=b'{}')
        client.fetch(discovery.WEB_INDEXES[0])
        self.assertEqual(opener.calls[0][0].get_header('Authorization'), 'Bearer SENTINEL-NOT-A-REAL-CREDENTIAL')
        self.assertIsNone(opener.calls[1][0].get_header('Authorization'))
        with self.assertRaisesRegex(discovery.SourceError, 'redirect-blocked'):
            client.fetch('https://api.github.com/graphql')
        self.assertEqual(len(opener.calls), 3)
        with self.assertRaises(discovery.SourceError):
            client.fetch('https://127.0.0.1/latest/meta-data')
        self.assertEqual(len(opener.calls), 3)

    def test_same_origin_redirect_rechecks_route_before_forwarding_credentials(self):
        target = 'https://api.github.com/repos/new/name/readme?ref=' + PIN
        opener = Opener(error('original', 301, {'Location': target}), Response(b'{}'))
        client = discovery.PublicClient('fixture', opener=opener)
        self.assertEqual(client.fetch('https://api.github.com/repos/old/name/readme?ref=' + PIN), b'{}')
        self.assertTrue(all(call[0].get_header('Authorization') == 'Bearer fixture' for call in opener.calls))

    def test_current_public_embed_endpoint_has_no_auth_and_legacy_cross_origin_stays_blocked(self):
        query = 'url=https%3A%2F%2Fx.com%2Fi%2Fstatus%2F2110835101583966520&omit_script=true&dnt=true'
        current = 'https://publish.x.com/oembed?' + query
        opener = Opener(Response(b'{}'), error('legacy', 301, {'Location': current}))
        client = discovery.PublicClient('SENTINEL-NOT-A-REAL-CREDENTIAL', opener=opener)
        client.fetch(current)
        self.assertIsNone(opener.calls[0][0].get_header('Authorization'))
        with self.assertRaisesRegex(discovery.SourceError, 'redirect-blocked'):
            client.fetch('https://publish.twitter.com/oembed?' + query)
        self.assertEqual(len(opener.calls), 2)

    def test_rate_limit_stops_same_host_without_fallback_or_response_body_retention(self):
        opener = Opener(error(discovery.WEB_INDEXES[0], 429, {'Retry-After': '900'}))
        client = discovery.PublicClient(opener=opener)
        for _ in range(2):
            with self.assertRaisesRegex(discovery.SourceError, 'rate-limited'):
                client.fetch(discovery.WEB_INDEXES[0])
        self.assertEqual(len(opener.calls), 1)

    def test_response_request_time_and_quota_bounds(self):
        for headers, expected in (({}, None), ({'X-RateLimit-Remaining': '99'}, 'quota-reserve')):
            opener = Opener(Response(b'{}', headers))
            client = discovery.PublicClient(opener=opener)
            client.fetch('https://api.github.com/graphql')
            if expected:
                with self.assertRaisesRegex(discovery.SourceError, expected):
                    client.fetch('https://api.github.com/graphql')
        with patch.object(discovery, 'MAX_RESPONSE', 3):
            with self.assertRaisesRegex(discovery.SourceError, 'response-too-large'):
                discovery.PublicClient(opener=Opener(Response(b'too long'))).fetch(discovery.WEB_INDEXES[0])
        client = discovery.PublicClient(opener=Opener(), clock=lambda: 0)
        client.requests = discovery.MAX_REQUESTS
        with self.assertRaisesRegex(discovery.SourceError, 'request-budget'):
            client.fetch(discovery.WEB_INDEXES[0])
        client.requests, client.deadline = 0, 0
        with self.assertRaisesRegex(discovery.SourceError, 'time-budget'):
            client.fetch(discovery.WEB_INDEXES[0])

    def test_streaming_response_rechecks_deadline_between_chunks(self):
        points = iter([0, 0, 0, 0, discovery.MAX_SECONDS + 1])
        class Stream(Response):
            def read1(self, size):
                return b'one chunk'
        client = discovery.PublicClient(opener=Opener(Stream(b'')), clock=lambda: next(points))
        with self.assertRaisesRegex(discovery.SourceError, 'time-budget'):
            client.fetch(discovery.WEB_INDEXES[0])


class PublicLeadTests(unittest.TestCase):
    def test_page_budget_is_shared_between_sites_and_rotates_past_first_pages(self):
        pages = [f'https://madewithrea.com/builds/p{i}' for i in range(12)] + [
                 f'https://reamcp.dev/zh-cn/cases/p{i}' for i in range(12)]
        first = discovery.select_case_pages(pages, '2026-11-01T00:17:00Z')
        second = discovery.select_case_pages(pages, '2026-11-01T08:17:00Z')
        self.assertEqual(len(first), discovery.MAX_WEB_CASES)
        self.assertEqual(sum('madewithrea.com' in url for url in first), 4)
        self.assertEqual(sum('reamcp.dev' in url for url in first), 4)
        self.assertNotEqual(set(first), set(second))
        small = discovery.select_case_pages(pages[:1] + pages[12:], '2026-11-01T00:17:00Z')
        self.assertEqual(len(small), discovery.MAX_WEB_CASES)
        self.assertEqual(len(set(small)), len(small))

    def test_canonical_links_drop_tracking_exclude_attachments_and_keep_post_identity(self):
        self.assertEqual(discovery.canonical_lead('https://twitter.com/user/status/2110835101583966520/video/1?ref=x'), ('x-post', POST))
        self.assertIsNone(discovery.canonical_lead('https://github.com/user-attachments/assets/abc'))
        self.assertIsNone(discovery.canonical_lead('https://github.com/user/.git'))
        self.assertIsNone(discovery.canonical_lead('https://password@example.org/case'))
        self.assertFalse(discovery.allowed_fetch('https://api.github.com/repos/a/b/readme?ref=' + PIN + '&ref=other'))
        self.assertFalse(discovery.allowed_fetch('https://@api.github.com/graphql'))

    def test_github_case_aliases_merge_but_case_sensitive_web_slugs_do_not(self):
        collector = discovery.Collector(FixtureClient())
        source = discovery.capture('fixture', discovery.WEB_INDEXES[0], 'web', b'fixture')
        collector.add_links('https://github.com/example/project https://github.com/EXAMPLE/PROJECT '
                            'https://madewithrea.com/builds/A https://madewithrea.com/builds/a', source)
        self.assertEqual(len(collector.leads), 3)

    def test_snapshot_follows_sources_without_storing_text_or_promoting_requests(self):
        report = discovery.Collector(FixtureClient()).collect()
        discovery.validate_report(report)
        self.assertEqual(report['counts']['x_original_excerpts'], 1)
        self.assertTrue(all(lead['verification'] == 'discovery-only' for lead in report['leads']))
        self.assertIn('https://github.com/morluto/rea/discussions/13', [lead['url'] for lead in report['leads']])
        self.assertIn('https://github.com/example/fresh', [lead['url'] for lead in report['leads']])
        self.assertEqual(sum(source['id'] == 'discussion-12' for source in report['sources']), 1)
        serialized = json.dumps(report)
        for value in ('PRIVATE_TWEET_TEXT', 'PRIVATE_BODY_ONLY', FixtureClient.token):
            self.assertNotIn(value, serialized)
        self.assertFalse(report['runtime_tested'])

    def test_private_repos_bad_git_integrity_and_partial_graphql_never_become_captures(self):
        for kwargs in ({'private': True}, {'mismatch': True}, {'partial_graphql': True}):
            with self.subTest(kwargs=kwargs):
                report = discovery.Collector(FixtureClient(**kwargs)).collect()
                self.assertEqual(report['status'], 'partial')
                self.assertGreater(report['counts']['source_errors'], 0)
                if not kwargs.get('partial_graphql'):
                    self.assertFalse(any(source['id'].startswith('readme-') and source['status'] == 'captured' for source in report['sources']))
                    if kwargs.get('private'):
                        self.assertFalse(any(source['id'].startswith('discussion-') for source in report['sources']))
                        self.assertNotIn('https://github.com/morluto/rea/discussions/13', [lead['url'] for lead in report['leads']])
                else:
                    self.assertTrue(any(source['id'].startswith('readme-') and source['status'] == 'captured' for source in report['sources']))

    def test_missing_created_ordering_keeps_available_updated_discussions(self):
        class PartialOrder(FixtureClient):
            def json(self, url, data=None):
                result = super().json(url, data)
                if url.endswith('/graphql'):
                    result['data']['upstream']['newest'] = None
                return result
        report = discovery.Collector(PartialOrder()).collect()
        self.assertEqual(report['status'], 'partial')
        self.assertIn('https://github.com/morluto/rea/discussions/12', [lead['url'] for lead in report['leads']])
        self.assertTrue(any(source['id'] == 'github-newest' and source['status'] == 'error' for source in report['sources']))

    def test_robots_disallow_prevents_page_fetch_and_records_missing_coverage(self):
        client = FixtureClient(deny_robots=True)
        report = discovery.Collector(client).collect()
        self.assertFalse(any(url in client.calls for url in discovery.WEB_INDEXES))
        self.assertEqual(sum(source['error'] == 'robots-disallowed' for source in report['sources']), 2)

    def test_output_hashes_and_publication_barriers_are_validated(self):
        report = discovery.Collector(FixtureClient()).collect()
        for mutate in (lambda d: d['leads'][0].update(verification='source-reviewed'),
                       lambda d: d.update(runtime_tested=True),
                       lambda d: d['leads'][0].update(source_ids=['missing']),
                       lambda d: d['sources'][0].update(raw_body='PRIVATE_BODY'),
                       lambda d: d['counts'].update(unique_url_leads=999)):
            invalid = deepcopy(report); mutate(invalid)
            with self.assertRaises((AssertionError, TypeError, ValueError)):
                discovery.validate_report(invalid)
        with TemporaryDirectory() as temporary, patch.object(discovery, 'ROOT', Path(temporary)):
            output = Path(temporary) / '.cache/leads'
            discovery.write_report(report, output)
            receipt = json.loads((output / 'receipt.json').read_text())
            self.assertEqual(receipt['report_sha256'], discovery.digest((output / 'leads.json').read_bytes()))
            with self.assertRaises(ValueError):
                discovery.write_report(report, Path(temporary) / 'data')

    def test_workflow_is_three_daily_read_only_default_branch_and_artifact_only(self):
        text = (ROOT / '.github/workflows/public-artifact-discovery.yml').read_text()
        self.assertIn("cron: '17 0,8,16 * * *'", text)
        self.assertIn('timezone: America/Los_Angeles', text)
        self.assertIn('github.event.repository.default_branch', text)
        self.assertIn('contents: read', text); self.assertIn('discussions: read', text)
        self.assertNotIn(': write', text); self.assertNotIn('pull_request', text)
        self.assertIn('timeout-minutes: 8', text)
        self.assertIn('steps.collect.outputs.artifact_ready', text)
        self.assertIn('.cache/public-artifact-leads/receipt.json', text)
        self.assertNotIn('path: .cache/', text.split('path: |')[0])


if __name__ == '__main__':
    unittest.main()
