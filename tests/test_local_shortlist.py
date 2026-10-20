"""The optional shortlist stays in the browser: one key format for both scripts, accessible markup and bilingual text."""
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
PAPERS = (ROOT / 'site/paper-search.js').read_text(encoding='utf-8')


class LocalShortlistTests(unittest.TestCase):
    def test_browser_behaviour(self):
        result = subprocess.run(['node', str(ROOT / 'tests/local_shortlist_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Local shortlist checks passed', result.stdout)

    def test_both_scripts_share_the_storage_key_and_entry_format(self):
        for name in ('SHORTLIST_KEY', 'SHORTLIST_ITEM'):
            definitions = {re.search(rf'const {name} = ([^;]+);', source)[1] for source in (APP, PAPERS)}
            self.assertEqual(len(definitions), 1, name)
        self.assertIn('"awesomerea-shortlist"', APP)
        # Only the three collection data files are fetched; no request is built from saved keys.
        for source in (APP, PAPERS):
            self.assertNotRegex(source, r'fetch\([^)]*shortlist')

    def test_markup_is_hidden_until_storage_works_and_labelled(self):
        trigger = re.search(r'<button type="button" id="shortlist-open"[^>]*>', HTML)[0]
        for attribute in ('aria-haspopup="dialog"', 'aria-controls="shortlist"', ' hidden'):
            self.assertIn(attribute, trigger)
        self.assertIn('<span id="shortlist-count" class="mono">0</span>', HTML)
        self.assertIn('<dialog id="shortlist" class="data-dialog shortlist-dialog" aria-labelledby="shortlist-title" aria-describedby="shortlist-description">', HTML)
        for live in ('<p id="shortlist-status" class="sr-only" role="status" aria-live="polite" aria-atomic="true"></p>',
                     '<p id="shortlist-dialog-status" class="data-copy-status" role="status" aria-live="polite" aria-atomic="true"></p>'):
            self.assertIn(live, HTML)

    def test_every_shortlist_string_is_bilingual_and_prerendered(self):
        strings = _ui_strings(APP)
        keys = {key for key in strings['en'] if key.startswith('shortlist')}
        self.assertGreaterEqual(len(keys), 20)
        self.assertEqual(keys, {key for key in strings['zh'] if key.startswith('shortlist')})
        self.assertTrue(all(strings['zh'][key] != strings['en'][key] for key in keys))
        chinese = localized_homepage(HTML, APP, 'zh')
        for key in ('shortlistOpen', 'shortlistTitle', 'shortlistDescription', 'shortlistEmpty', 'shortlistClear'):
            self.assertTrue(re.search(rf'data-i18n="{key}"[^>]*>{re.escape(strings["zh"][key])}<', chinese), key)
        self.assertTrue(f'aria-label="{strings["zh"]["shortlistClose"]}"' in chinese)


if __name__ == '__main__':
    unittest.main()
