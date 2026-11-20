"""Bounded fidelity evidence: link selection, signals and failure modes."""
import base64
import json
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import fidelity_scan  # noqa: E402

COMMIT = 'a' * 40


class FakeClient:
    def __init__(self, files):
        self.files = files

    def get(self, url, timeout=30, page=False):
        path = unquote(urlsplit(url).path.split('/contents/', 1)[1])
        if path not in self.files:
            return 404, b'', {}
        text = self.files[path]
        payload = {'content': base64.b64encode(text.encode()).decode(),
                   'html_url': f'https://github.com/example/tool/blob/{COMMIT}/{path}'}
        return 200, json.dumps(payload).encode(), {}


class FidelityScanTests(unittest.TestCase):
    def record(self):
        return {'id': 'example-case',
                'evidence_url': f'https://github.com/example/tool/blob/{COMMIT}/README.md'}

    def test_parse_evidence_requires_a_pinned_blob(self):
        self.assertEqual(fidelity_scan.parse_evidence(self.record()['evidence_url']),
                         ('example', 'tool', COMMIT, 'README.md'))
        for url in ('https://github.com/example/tool', 'https://example.org/readme',
                    'https://github.com/example/tool/blob/main/README.md'):
            with self.subTest(url):
                with self.assertRaises(fidelity_scan.ScanError):
                    fidelity_scan.parse_evidence(url)

    def test_links_are_ranked_and_install_or_license_pages_are_skipped(self):
        text = ('# Tool\n\n[parity report](docs/parity.md)\n[install](docs/INSTALL.md)\n'
                '[known limitations](docs/limits.md)\n[license](LICENSE.md)\n'
                '[other](https://example.org/docs/parity.md)\n')
        links = fidelity_scan.document_links(text, 'README.md')
        self.assertEqual([link['path'] for link in links], ['docs/parity.md', 'docs/limits.md'])
        self.assertEqual(links[0]['score'], 25)

    def test_scan_record_reads_the_readme_and_follows_evidence_documents(self):
        files = {
            'README.md': ('# Tool\n\nSave and reopen round trip is documented.\n\n'
                          '[parity report](docs/parity.md)\n[known limitations](docs/limits.md)\n'),
            'docs/parity.md': 'A differential comparison against the original binary.\n',
            'docs/limits.md': 'Audio is not yet implemented; saving is incomplete.\n',
        }
        result = fidelity_scan.scan_record(self.record(), FakeClient(files))
        self.assertEqual(result['repo'], 'example/tool')
        self.assertEqual(result['commit'], COMMIT)
        self.assertFalse(result['runtime_verified'])
        self.assertEqual([doc['path'] for doc in result['documents']],
                         ['README.md', 'docs/parity.md', 'docs/limits.md'])
        self.assertTrue(result['signals']['workflow'])
        self.assertTrue(any(item['path'] == 'docs/parity.md' for item in result['signals']['comparison']))
        self.assertTrue(any(item['path'] == 'docs/limits.md' for item in result['signals']['limits']))
        self.assertTrue(any('#L1' in item['url'] for item in result['signals']['comparison']))

    def test_unreadable_readme_is_an_error(self):
        with self.assertRaises(fidelity_scan.ScanError):
            fidelity_scan.scan_record(self.record(), FakeClient({}))

    def test_second_hop_is_limited_to_named_evidence_documents(self):
        files = {
            'README.md': '[parity report](docs/parity.md)\n',
            'docs/parity.md': '[coverage table](coverage.md)\n[usage guide](usage.md)\n',
            'docs/coverage.md': 'Feature coverage table.\n',
            'docs/usage.md': 'Usage guide.\n',
        }
        result = fidelity_scan.scan_record(self.record(), FakeClient(files))
        self.assertIn('docs/coverage.md', [doc['path'] for doc in result['documents']])
        self.assertNotIn('docs/usage.md', [doc['path'] for doc in result['documents']])


if __name__ == '__main__':
    unittest.main()
