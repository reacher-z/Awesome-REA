"""Exercise pinned delta planning and single-POST behavior without network access."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import hashlib
from io import StringIO
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import submit_indexnow as indexnow
from build_manifest import html_digest, read_build_manifest, write_build_manifest


def entry(content, html=False):
    value = {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
    if html:
        value['html_sha256'] = html_digest(content)
    return value


class Response:
    def __init__(self, status=200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class IndexNowDeltaTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.dist = self.root / 'dist'
        self.dist.mkdir()
        (self.root / 'site').mkdir()
        self.key = 'f' * 32
        (self.root / 'site/indexnow.txt').write_text(self.key)
        self.urls = [indexnow.ORIGIN + suffix for suffix in ('/stable/', '/', '/new/')]
        for filename, content in {
            'index.html': b'<h1>Current homepage</h1>', 'new/index.html': b'<h1>New</h1>',
            'stable/index.html': b'<h1>Stable</h1>', '404.html': b'<h1>Not found</h1>',
            'app.js': b'console.log("fixture");', 'catalog.json': b'{}',
        }.items():
            path = self.dist / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.write_sitemap(self.urls)
        self.current = write_build_manifest(self.dist)
        self.root_patch = patch.object(indexnow, 'ROOT', self.root)
        self.root_patch.start(); self.addCleanup(self.root_patch.stop)
        self.source_patch = patch.object(indexnow, 'source_revision', return_value={'commit': 'c' * 40, 'worktree_clean': True})
        self.source_patch.start(); self.addCleanup(self.source_patch.stop)

    def write_sitemap(self, urls):
        (self.dist / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                               + ''.join('<url><loc>' + url + '</loc></url>' for url in urls) + '</urlset>')

    def baseline(self, document=None, raw=None):
        path = self.root / 'previous-manifest.json'
        data = raw if raw is not None else json.dumps(document or self.current, sort_keys=True).encode()
        path.write_bytes(data)
        return path, hashlib.sha256(data).hexdigest()

    def delta_args(self, document=None):
        path, sha = self.baseline(document)
        return ['--previous-manifest', str(path), '--previous-manifest-sha256', sha]

    def changed_baseline(self):
        previous = deepcopy(self.current)
        previous['files'].pop('new/index.html')
        previous['files']['index.html'] = entry(b'<h1>Previous homepage</h1>', True)
        # Raw bytes differ, but normalized page content is unchanged.
        previous['files']['stable/index.html']['sha256'] = '1' * 64
        previous['files']['stable/index.html']['bytes'] += 30
        previous['files']['retired/index.html'] = entry(b'<h1>Former file, canonical status unknown</h1>', True)
        previous['files']['404.html'] = entry(b'<h1>Old error page</h1>', True)
        return previous

    def run_main(self, args):
        output = StringIO()
        with patch.object(sys, 'argv', ['submit_indexnow.py', *args]), redirect_stdout(output):
            result = indexnow.main()
        return result, output.getvalue()

    def live_network(self, *, status=200, error=None, broken_url=None):
        events = []
        public = {indexnow.ORIGIN + '/indexnow.txt': self.key.encode()}
        for file in self.dist.rglob('*'):
            if file.is_file():
                public[indexnow.ORIGIN + '/' + file.relative_to(self.dist).as_posix()] = file.read_bytes()
        for url in self.urls:
            public[url] = (self.dist / indexnow.canonical_html_file(url)).read_bytes()
        if broken_url:
            public[broken_url] = b'<h1>Stale deployed content</h1>'

        def fetch(url, limit):
            events.append(('GET', url))
            self.assertIn(url, public)
            self.assertLessEqual(len(public[url]), limit)
            return public[url]

        def post(request, **kwargs):
            self.assertEqual(request.get_method(), 'POST')
            self.assertEqual(request.full_url, indexnow.ENDPOINT)
            payload = json.loads(request.data)
            events.append(('POST', payload))
            if error:
                raise error
            return Response(status)
        return events, fetch, post

    def test_delta_dry_run_is_deterministic_and_never_fetches(self):
        previous = self.changed_baseline()
        args = self.delta_args(previous)
        with patch.object(indexnow, 'fetch_bytes') as fetch, patch.object(indexnow, 'urlopen') as network:
            code, output = self.run_main(args)
        fetch.assert_not_called(); network.assert_not_called()
        self.assertEqual(code, 0)
        report = json.loads(output)
        self.assertEqual(report['added'], [indexnow.ORIGIN + '/new/'])
        self.assertEqual(report['updated'], [indexnow.ORIGIN + '/'])
        self.assertEqual(report['counts']['unchanged'], 1)
        self.assertEqual(report['counts']['selected'], 2)
        self.assertNotIn('unchanged', report); self.assertNotIn('selected', report)
        self.assertEqual(indexnow.manifest_delta(self.current, previous, self.urls)['selected'],
                         [indexnow.ORIGIN + '/', indexnow.ORIGIN + '/new/'])
        self.assertEqual(report['removed_html_candidates'], ['retired/index.html'])
        self.assertEqual(report['other_current_html_changes'], {'added': [], 'updated': ['404.html']})
        self.assertNotIn(self.key, output)
        self.assertNotIn(str(self.root), output)
        self.assertEqual(report['current_manifest_sha256'], hashlib.sha256((self.dist / 'build-manifest.json').read_bytes()).hexdigest())
        self.assertEqual(indexnow.manifest_delta(self.current, previous, self.urls),
                         indexnow.manifest_delta(self.current, previous, list(reversed(self.urls))))

    def test_default_dry_run_and_full_submission_still_use_entire_sitemap(self):
        with patch.object(indexnow, 'fetch_bytes') as fetch, patch.object(indexnow, 'urlopen') as network:
            code, output = self.run_main([])
        fetch.assert_not_called(); network.assert_not_called()
        self.assertEqual(code, 0); self.assertTrue(output.startswith('Dry run: 3 canonical URLs; manifest '))
        events, fetch, post = self.live_network()
        with patch.object(indexnow, 'fetch_bytes', side_effect=fetch), patch.object(indexnow, 'urlopen', side_effect=post) as network:
            code, output = self.run_main(['--submit'])
        self.assertEqual(code, 0); self.assertEqual(network.call_count, 1)
        self.assertEqual(events[-1][1]['urlList'], self.urls)
        self.assertIn('IndexNow HTTP 200: 3 URLs submitted', output)

    def test_filtered_post_follows_full_ownership_manifest_and_page_preflight(self):
        args = self.delta_args(self.changed_baseline()) + ['--submit']
        events, fetch, post = self.live_network()
        with patch.object(indexnow, 'fetch_bytes', side_effect=fetch), patch.object(indexnow, 'urlopen', side_effect=post) as network:
            code, output = self.run_main(args)
        self.assertEqual(code, 0); self.assertEqual(network.call_count, 1)
        self.assertEqual([event[0] for event in events[:-1]], ['GET'] * 7)
        self.assertEqual(events[0][1], indexnow.ORIGIN + '/indexnow.txt')
        self.assertEqual(events[1][1], indexnow.ORIGIN + '/sitemap.xml')
        self.assertEqual(events[2][1], indexnow.ORIGIN + '/build-manifest.json')
        self.assertEqual({event[1] for event in events[3:6]}, set(self.urls))
        self.assertEqual(events[-2][1], indexnow.ORIGIN + '/build-manifest.json')
        payload = events[-1][1]
        self.assertEqual(payload['urlList'], [indexnow.ORIGIN + '/', indexnow.ORIGIN + '/new/'])
        self.assertEqual(payload['host'], 'awesomerea.org')
        self.assertEqual(payload['key'], self.key)
        self.assertIn('IndexNow HTTP 200: 2 URLs submitted', output)
        self.assertNotIn(self.key, output)

    def test_unchanged_page_mismatch_blocks_even_a_filtered_post(self):
        events, fetch, post = self.live_network(broken_url=indexnow.ORIGIN + '/stable/')
        with patch.object(indexnow, 'fetch_bytes', side_effect=fetch), patch.object(indexnow, 'urlopen', side_effect=post) as network:
            with self.assertRaisesRegex(ValueError, 'Deployed HTML differs'):
                self.run_main(self.delta_args(self.changed_baseline()) + ['--submit'])
        network.assert_not_called()
        self.assertTrue(all(event[0] == 'GET' for event in events))

    def test_empty_delta_has_no_preflight_or_post(self):
        with patch.object(indexnow, 'fetch_bytes') as fetch, patch.object(indexnow, 'urlopen') as network:
            code, output = self.run_main(self.delta_args() + ['--submit'])
        self.assertEqual(code, 0); fetch.assert_not_called(); network.assert_not_called()
        report = json.JSONDecoder().raw_decode(output)[0]
        self.assertEqual(report['counts']['selected'], 0)
        self.assertEqual(report['status'], 'no-current-canonical-html-changes')
        self.assertIn('no notification sent', output)

    def test_asset_only_delta_requires_review_without_post(self):
        previous = deepcopy(self.current)
        previous['files']['catalog.json'] = entry(b'{"previous":true}')
        with patch.object(indexnow, 'fetch_bytes') as fetch, patch.object(indexnow, 'urlopen') as network:
            code, output = self.run_main(self.delta_args(previous) + ['--submit'])
        self.assertEqual(code, 1); fetch.assert_not_called(); network.assert_not_called()
        report = json.JSONDecoder().raw_decode(output)[0]
        self.assertTrue(report['non_html_changes_require_review'])
        self.assertEqual(report['non_html_changes']['updated'], ['catalog.json'])
        self.assertEqual(report['counts']['selected'], 0)
        self.assertIn('full-sitemap mode remains available', output)

    def test_unknown_removed_html_is_only_a_filename_not_a_notification(self):
        previous = deepcopy(self.current)
        previous['files']['former.html'] = entry(b'<p>Unknown previous canonical status</p>', True)
        (self.dist / '404.html').unlink()
        self.current = write_build_manifest(self.dist)
        with patch.object(indexnow, 'fetch_bytes') as fetch, patch.object(indexnow, 'urlopen') as network:
            code, output = self.run_main(self.delta_args(previous) + ['--submit'])
        self.assertEqual(code, 0); fetch.assert_not_called(); network.assert_not_called()
        report = json.JSONDecoder().raw_decode(output)[0]
        self.assertEqual(report['removed_html_candidates'], ['404.html', 'former.html'])
        self.assertNotIn(indexnow.ORIGIN + '/former', output)
        self.assertEqual(report['counts']['selected'], 0)

    def test_untrusted_baseline_schema_hash_and_path_fail_before_network(self):
        cases = []
        for key, value in [('schema_version', True), ('algorithm', 'sha1'), ('html_normalization', 'old-rule')]:
            bad = deepcopy(self.current); bad[key] = value; cases.append(bad)
        for bad_path in ['../secret.html', '/absolute.html', 'a/../b.html', 'a//b.html', './index.html',
                         'https://outside.example/index.html', 'a\\b.html', '%2e%2e/index.html', 'a?b.html',
                         '.env', 'safe/.cache/file.html', 'credentials.json', 'fonts/font.woff2']:
            bad = deepcopy(self.current); bad['files'][bad_path] = entry(b'bad', bad_path.endswith('.html')); cases.append(bad)
        for key, value in [('sha256', 'wrong'), ('html_sha256', 'A' * 64), ('bytes', True), ('bytes', -1)]:
            bad = deepcopy(self.current); bad['files']['index.html'][key] = value; cases.append(bad)
        bad = deepcopy(self.current); bad['files']['index.html']['extra'] = 'ignored?'; cases.append(bad)
        bad = deepcopy(self.current); bad['files'].pop('sitemap.xml'); cases.append(bad)
        with patch.object(indexnow, 'fetch_bytes') as fetch, patch.object(indexnow, 'urlopen') as network:
            for document in cases:
                with self.subTest(document=document), self.assertRaises(ValueError):
                    self.run_main(self.delta_args(document) + ['--submit'])
            path, expected = self.baseline()
            with self.assertRaisesRegex(ValueError, 'expected SHA-256'):
                self.run_main(['--previous-manifest', str(path), '--previous-manifest-sha256', '0' * 64, '--submit'])
        fetch.assert_not_called(); network.assert_not_called()

    def test_baseline_duplicate_keys_nonjson_utf8_size_and_symlink_are_rejected(self):
        invalid = [b'{"schema_version":1,"schema_version":1}', b'{"files":NaN}', b'\xff', b'not JSON',
                   b'[' * 1100 + b']' * 1100]
        for raw in invalid:
            path, expected = self.baseline(raw=raw)
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                indexnow.read_previous_manifest(path, expected)
        path, expected = self.baseline(raw=b' ' * (indexnow.MAX_PREVIOUS_MANIFEST_BYTES + 1))
        with self.assertRaisesRegex(ValueError, 'size limit'):
            indexnow.read_previous_manifest(path, expected)
        path, expected = self.baseline()
        link = self.root / 'linked.json'; link.symlink_to(path)
        with self.assertRaisesRegex(ValueError, 'symbolic link'):
            indexnow.read_previous_manifest(link, expected)
        with self.assertRaisesRegex(ValueError, 'regular file'):
            indexnow.read_previous_manifest(self.root, expected)

    def test_both_baseline_arguments_are_required_without_network(self):
        with patch.object(indexnow, 'fetch_bytes') as fetch, patch.object(indexnow, 'urlopen') as network:
            for args in [['--previous-manifest', 'file.json'], ['--previous-manifest-sha256', 'a' * 64]]:
                with self.subTest(args=args), redirect_stderr(StringIO()), self.assertRaises(SystemExit) as error:
                    self.run_main(args)
                self.assertEqual(error.exception.code, 2)
        fetch.assert_not_called(); network.assert_not_called()

    def test_current_sitemap_guards_are_not_bypassed(self):
        for urls in [[indexnow.ORIGIN + '/'] * 2, ['https://other.example/'], [indexnow.ORIGIN + '/?q=bad'],
                     [indexnow.ORIGIN + '/#fragment'], [indexnow.ORIGIN + '/missing/'],
                     [indexnow.ORIGIN + '/' + str(i) + '/' for i in range(10001)]]:
            self.write_sitemap(urls); write_build_manifest(self.dist)
            with self.subTest(urls=urls[:2]), patch.object(indexnow, 'urlopen') as network, self.assertRaises(ValueError):
                self.run_main(['--submit'])
            network.assert_not_called()

    def test_accepted_pending_rejected_and_uncertain_responses_never_retry(self):
        args = self.delta_args(self.changed_baseline()) + ['--submit']
        rate_limit = HTTPError(indexnow.ENDPOINT, 429, 'limited', None, None)
        self.addCleanup(rate_limit.close)
        for status, error, expected in [(202, None, 0), (500, None, 1),
                                        (None, URLError('response unavailable'), 1),
                                        (None, rate_limit, 1)]:
            events, fetch, post = self.live_network(status=status, error=error)
            with self.subTest(status=status, error=type(error).__name__), patch.object(indexnow, 'fetch_bytes', side_effect=fetch), patch.object(indexnow, 'urlopen', side_effect=post) as network:
                code, output = self.run_main(args)
            self.assertEqual(code, expected); self.assertEqual(network.call_count, 1)
            self.assertEqual(sum(event[0] == 'POST' for event in events), 1)
            if status == 202:
                self.assertIn('Key validation pending', output)
                self.assertIn('does not confirm indexing', output)
            if isinstance(error, URLError) and not isinstance(error, HTTPError):
                self.assertIn('unconfirmed', output); self.assertIn('No automatic retry', output)


    # --automatic and --receipt: a receipt binds the verified deployment; asset-only changes notify nothing.

    def test_asset_only_delta_verifies_the_deployment_and_records_a_receipt(self):
        previous = deepcopy(self.current)
        previous['files']['catalog.json'] = {'sha256': '2' * 64, 'bytes': 9}
        receipt = self.root / 'receipt/receipt.json'
        events, fetch, post = self.live_network()
        args = [*self.delta_args(previous), '--submit', '--automatic', '--receipt', str(receipt)]
        with patch.object(indexnow, 'fetch_bytes', side_effect=fetch), patch.object(indexnow, 'urlopen', side_effect=post):
            code, output = self.run_main(args)
        self.assertEqual(code, 0, output)
        self.assertFalse(any(kind == 'POST' for kind, _ in events))
        self.assertTrue(any(url == indexnow.ORIGIN + '/build-manifest.json' for _, url in events))
        recorded = json.loads(receipt.read_text())
        self.assertEqual(recorded['manifest_sha256'], hashlib.sha256((self.dist / 'build-manifest.json').read_bytes()).hexdigest())
        self.assertEqual((recorded['mode'], recorded['submitted_urls'], recorded['indexnow_status']), ('delta', 0, None))
        # Without --automatic the same delta still asks for a review and writes nothing.
        receipt.unlink()
        with patch.object(indexnow, 'fetch_bytes', side_effect=fetch), patch.object(indexnow, 'urlopen', side_effect=post):
            code, _ = self.run_main([*self.delta_args(previous), '--submit', '--receipt', str(receipt)])
        self.assertEqual(code, 1)
        self.assertFalse(receipt.exists())

    def test_a_full_submission_records_its_receipt_and_another_build_directory_works(self):
        moved = self.root / 'deployed'
        self.dist.rename(moved)
        self.dist = moved
        receipt = self.root / 'receipt.json'
        events, fetch, post = self.live_network(status=202)
        with patch.object(indexnow, 'fetch_bytes', side_effect=fetch), patch.object(indexnow, 'urlopen', side_effect=post):
            code, output = self.run_main(['--submit', '--automatic', '--dist', str(moved), '--receipt', str(receipt)])
        self.assertEqual(code, 0, output)
        posts = [payload for kind, payload in events if kind == 'POST']
        self.assertEqual(len(posts), 1)
        self.assertEqual(sorted(posts[0]['urlList']), sorted(self.urls))
        recorded = json.loads(receipt.read_text())
        self.assertEqual((recorded['mode'], recorded['submitted_urls'], recorded['indexnow_status']), ('full', 3, 202))

    def test_sitemap_index_files_are_all_verified_against_the_deployment(self):
        (self.dist / 'sitemap-pages.xml').write_text(
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + ''.join(f'<url><loc>{url}</loc></url>' for url in self.urls) + '</urlset>')
        (self.dist / 'sitemap.xml').write_text('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                               f'<sitemap><loc>{indexnow.ORIGIN}/sitemap-pages.xml</loc></sitemap></sitemapindex>')
        write_build_manifest(self.dist)
        events, fetch, post = self.live_network()
        with patch.object(indexnow, 'fetch_bytes', side_effect=fetch), patch.object(indexnow, 'urlopen', side_effect=post):
            code, output = self.run_main(['--submit'])
        self.assertEqual(code, 0, output)
        fetched = [url for kind, url in events if kind == 'GET']
        self.assertIn(indexnow.ORIGIN + '/sitemap.xml', fetched)
        self.assertIn(indexnow.ORIGIN + '/sitemap-pages.xml', fetched)


if __name__ == '__main__':
    unittest.main()
