"""Show More progress has its own live region outside the rows that hide when every result is shown."""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'site/index.html').read_text(encoding='utf-8')


class ShowMoreAnnouncementTests(unittest.TestCase):
    def test_browser_announcements(self):
        result = subprocess.run(['node', str(ROOT / 'tests/show_more_announcement_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Show More announcement checks passed', result.stdout)

    def test_live_regions_follow_the_show_more_rows(self):
        for row, region in (('load-more-row', 'more-status'), ('source-more-row', 'source-more-status')):
            with self.subTest(row=row):
                # A live region inside the row would vanish with it on the final page, before it could be read.
                match = re.search(rf'<div class="load-more-row" id="{row}" hidden>.*?</div>\n\s*(<p [^>]*></p>)', HTML)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), f'<p id="{region}" class="sr-only" role="status" aria-live="polite" aria-atomic="true"></p>')


if __name__ == '__main__':
    unittest.main()
