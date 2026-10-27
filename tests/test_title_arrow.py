"""Linked collection titles keep their external arrow on the line of the last title word."""
from html import escape
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_browse_pages import icon
from build_discovery_pages import EXTERNAL_TITLE_ARROW, _case_row, _resource_card


class TitleArrowTests(unittest.TestCase):
    def setUp(self):
        translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
        resources = json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))
        self.record = dict(next(r for r in resources if r['kind'] == 'case-study'))
        names = translations.get(self.record['id'], {})
        self.record['name_zh'] = self.record.get('name_zh') or names.get('name', self.record['name'])
        self.record['requirements_zh'] = self.record.get('requirements_zh') or names.get('requirements', self.record['requirements'])

    def test_word_joiner_binds_the_arrow_to_the_title(self):
        self.assertEqual(EXTERNAL_TITLE_ARROW, '<span class="browse-text-arrow" aria-hidden="true">&#8288;↗</span>')
        for language in ('en', 'zh'):
            name = self.record['name_zh'] if language == 'zh' else self.record['name']
            for html in (_resource_card(self.record, language), _case_row(self.record, language, 'game')):
                with self.subTest(language=language, html=html[:40]):
                    self.assertIn(escape(name) + EXTERNAL_TITLE_ARROW + '</a></h3>', html)
                    self.assertEqual(html.count('browse-text-arrow'), 1)

    def test_browse_fallback_icon_uses_the_same_arrow(self):
        self.assertEqual(icon('external', False), EXTERNAL_TITLE_ARROW)
        self.assertNotIn('browse-text-arrow', icon('external', True))

    def test_arrow_stays_inline_so_the_joiner_applies(self):
        css = (ROOT / 'site/browse.css').read_text(encoding='utf-8')
        rule = re.search(r'\.browse-text-arrow\{([^}]*)\}', css)
        self.assertIsNotNone(rule)
        self.assertNotIn('display', rule[1])
        self.assertNotIn('margin', rule[1])
        # On the narrowest phones the badge moves under the title so a long last word keeps its arrow.
        self.assertIn('@media(max-width:380px){.browse-main .card-heading{flex-wrap:wrap;gap:9px}'
                      '.browse-main .card-heading h3{flex-basis:100%}}', css)


if __name__ == '__main__':
    unittest.main()
