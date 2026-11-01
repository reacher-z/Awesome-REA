"""Keep the optional link-back badge served from one stable URL and documented with a real entry."""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_site import LISTED_BADGE
from validate_site import validate_listed_badge

BADGE_URL = 'https://awesomerea.org/badges/' + LISTED_BADGE
HEADERS = '/*\n  X-Frame-Options: DENY\n/badges/*\n  Content-Type: image/svg+xml\n'


class ListedBadgeTests(unittest.TestCase):
    def build(self, badge=None, headers=HEADERS):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / '_headers').write_text(headers, encoding='utf-8')
        if badge is not None:
            (root / 'badges').mkdir()
            (root / 'badges' / LISTED_BADGE).write_bytes(badge)
        return root

    def test_served_badge_matches_the_repository_asset(self):
        validate_listed_badge(self.build((ROOT / 'assets' / LISTED_BADGE).read_bytes()))

    def test_missing_changed_or_untyped_badges_fail(self):
        original = (ROOT / 'assets' / LISTED_BADGE).read_bytes()
        for root, message in ((self.build(), 'must be served'),
                              (self.build(original.replace(b'Awesome REA</text>', b'Other</text>')), 'differs'),
                              (self.build(original, headers='/*\n  X-Frame-Options: DENY\n'), 'image/svg'),
                              (self.build(original, headers=HEADERS.replace('image/svg+xml', 'text/plain')), 'image/svg')):
            with self.subTest(message=message), self.assertRaisesRegex(AssertionError, message):
                validate_listed_badge(root)

    def test_both_guides_document_optional_listing_without_certification(self):
        for name, optional, scope in (('CONTRIBUTING.md', 'optional', 'does not certify'),
                                      ('CONTRIBUTING.zh-CN.md', '可选', '不认证')):
            text = (ROOT / name).read_text(encoding='utf-8')
            with self.subTest(guide=name):
                self.assertIn('[![Featured by Awesome REA](' + BADGE_URL
                              + ')](https://github.com/reacher-z/Awesome-REA)', text)
                self.assertIn(optional, text)
                self.assertIn(scope, text)
        # Listing never depends on the badge, so no form or template asks for it.
        for path in sorted((ROOT / '.github').rglob('*')):
            if path.is_file() and path.suffix in {'.md', '.yml', '.yaml'}:
                self.assertNotIn('featured-by', path.read_text(encoding='utf-8'), path.name)



if __name__ == '__main__':
    unittest.main()
