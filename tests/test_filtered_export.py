"""Both homepage collections offer a labeled, bilingual export of every filtered match beside the existing full downloads."""
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from homepage_locales import _ui_strings, localized_homepage

HTML = (ROOT / 'site/index.html').read_text(encoding='utf-8')
APP = (ROOT / 'site/app.js').read_text(encoding='utf-8')


class FilteredExportTests(unittest.TestCase):
    def test_browser_export_logic(self):
        result = subprocess.run(['node', str(ROOT / 'tests/filtered_export_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Filtered export checks passed', result.stdout)

    def test_each_results_line_has_a_hidden_export_button_and_its_own_status(self):
        for prefix, status in (('', 'results-status'), ('source-', 'source-status')):
            with self.subTest(prefix=prefix):
                topline = re.search(rf'<div class="results-topline"><p id="{status}"[^>]*></p>(.*?)</div>\n\s*(<p [^>]*></p>)', HTML)
                self.assertIsNotNone(topline)
                button = re.search(rf'<button id="{prefix}export-matches"[^>]*>', topline.group(1)).group(0)
                for attribute in ('type="button"', 'hidden', 'data-i18n="exportMatches"'):
                    self.assertIn(attribute, button)
                self.assertEqual(topline.group(2), f'<p id="{prefix}export-matches-status" class="export-status" role="status" aria-live="polite"></p>')
        # The full catalog and repository downloads keep their own links.
        self.assertIn('<a id="download-curated-catalog" href="catalog.json" download="awesomerea-curated-catalog.json"', HTML)
        self.assertIn('<a id="download-source-index" href="source-index.json" download="awesomerea-repository-index.json"', HTML)

    def test_label_is_bilingual_and_prerendered(self):
        strings = _ui_strings(APP)
        self.assertEqual(strings['en']['exportMatches'], 'Export matches (JSON) ↓')
        self.assertEqual(strings['zh']['exportMatches'], '导出匹配项（JSON）↓')
        chinese = localized_homepage(HTML, APP, 'zh')
        self.assertEqual(len(re.findall(r'<button id="(?:source-)?export-matches"[^>]*>导出匹配项（JSON）↓</button>', chinese)), 2)


if __name__ == '__main__':
    unittest.main()
