"""Stylesheets and scripts are served from content-addressed /assets/ paths that may be cached for a year."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from asset_paths import fingerprinted_href, remove_unhashed_copies
from validate_site import header_rules, validate_fingerprinted_assets

HEADERS = '''/*
  X-Frame-Options: DENY
/
  Cache-Control: no-cache, must-revalidate
/catalog.json
  Cache-Control: no-cache, must-revalidate
/assets/*
  Cache-Control: public, max-age=31536000, immutable
'''


def short_hash(data):
    return hashlib.sha256(data).hexdigest()[:16]


class FingerprintedAssetTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def test_href_names_a_copy_by_content(self):
        self.write('styles.css', 'body{margin:0}')
        href = fingerprinted_href(self.root, 'styles.css')
        self.assertEqual(href, f'/assets/styles.{short_hash(b"body{margin:0}")}.css')
        self.assertEqual((self.root / href.lstrip('/')).read_text(encoding='utf-8'), 'body{margin:0}')
        self.assertEqual(fingerprinted_href(self.root, 'styles.css'), href)
        self.write('styles.css', 'body{margin:1px}')
        self.assertNotEqual(fingerprinted_href(self.root, 'styles.css'), href)
        self.assertEqual(fingerprinted_href(self.root, 'missing.js'), '/missing.js')

    def test_only_fingerprinted_root_copies_are_removed(self):
        for name in ('app.js', 'legacy.css', 'fontawesome.css', 'favicon.svg'):
            self.write(name, name)
        fingerprinted_href(self.root, 'app.js')
        fingerprinted_href(self.root, 'fontawesome.css')
        remove_unhashed_copies(self.root, ['app.js', 'legacy.css', 'fontawesome.css', 'favicon.svg'])
        self.assertFalse((self.root / 'app.js').exists())
        for name in ('legacy.css', 'fontawesome.css', 'favicon.svg'):
            self.assertTrue((self.root / name).exists(), name)

    def site(self, head):
        self.write('_headers', HEADERS)
        self.write('index.html', f'<!doctype html><html><head>{head}</head><body></body></html>')

    def test_content_addressed_references_pass(self):
        self.write('styles.css', 'a{}')
        self.write('app.js', 'void 0;')
        styles, script = fingerprinted_href(self.root, 'styles.css'), fingerprinted_href(self.root, 'app.js')
        remove_unhashed_copies(self.root, ['styles.css', 'app.js'])
        self.site(f'<link rel="stylesheet" href="{styles}"><link rel="stylesheet" href="https://awesome-rea.pages.dev/fontawesome.css">'
                  f'<link rel="icon" href="/favicon.svg?v=1"><script src="https://awesomerea.org{script}" defer></script>')
        validate_fingerprinted_assets(self.root)

    def test_unhashed_or_mismatched_references_fail(self):
        self.write('styles.css', 'a{}')
        styles = fingerprinted_href(self.root, 'styles.css')
        (self.root / 'styles.css').unlink()
        wrong = f'/assets/styles.{"0" * 16}.css'
        self.write(wrong.lstrip('/'), 'a{}')
        for head, message in ((f'<link rel="stylesheet" href="{styles}?v=1">', 'Unhashed'),
                              ('<script src="/app.js?v=0123456789abcdef"></script>', 'Unhashed'),
                              ('<link rel="stylesheet" href="papers.css">', 'Unhashed'),
                              (f'<link rel="stylesheet" href="{wrong}">', 'does not match its content')):
            with self.subTest(head=head):
                self.site(head)
                with self.assertRaisesRegex(AssertionError, message):
                    validate_fingerprinted_assets(self.root)
        (self.root / wrong.lstrip('/')).unlink()

    def test_stray_root_scripts_and_missing_or_misplaced_rules_fail(self):
        self.site('')
        self.write('paper-search.js', 'void 0;')
        with self.assertRaisesRegex(AssertionError, 'outside /assets/: paper-search.js'):
            validate_fingerprinted_assets(self.root)
        (self.root / 'paper-search.js').unlink()
        self.write('_headers', HEADERS.replace('/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n', ''))
        with self.assertRaisesRegex(AssertionError, r'/assets/\* needs Cache-Control'):
            validate_fingerprinted_assets(self.root)
        self.write('_headers', HEADERS.replace('/catalog.json\n  Cache-Control: no-cache, must-revalidate',
                                               '/catalog.json\n  Cache-Control: public, max-age=31536000, immutable'))
        with self.assertRaisesRegex(AssertionError, 'Only content-addressed assets may be immutable: /catalog.json'):
            validate_fingerprinted_assets(self.root)

    def test_site_headers_cache_assets_and_revalidate_html_and_data(self):
        rules = header_rules((ROOT / 'site/_headers').read_text(encoding='utf-8'))
        self.assertEqual(rules['/assets/*']['cache-control'], 'public, max-age=31536000, immutable')
        for route in ('/', '/index.html', '/catalog.json', '/papers.json', '/source-index.json', '/source-browser.json'):
            self.assertEqual(rules[route]['cache-control'], 'no-cache, must-revalidate', route)


if __name__ == '__main__':
    unittest.main()
