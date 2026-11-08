"""Linked collection titles keep their external arrow on the line of the last title word."""
from html import escape
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_browse_pages import icon, repository_card
from build_discovery_pages import EXTERNAL_TITLE_ARROW, _case_row


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
            for html in (_case_row(self.record, language, 'game'),):
                with self.subTest(language=language, html=html[:40]):
                    self.assertIn(escape(name) + EXTERNAL_TITLE_ARROW + '</a></h3>', html)
                    self.assertEqual(html.count('browse-text-arrow'), 1)

    def test_browse_fallback_icon_uses_the_same_arrow(self):
        self.assertEqual(icon('external', False), EXTERNAL_TITLE_ARROW)
        self.assertNotIn('browse-text-arrow', icon('external', True))

    def test_repository_title_icon_shares_a_no_wrap_span_with_the_last_character(self):
        # The Font Awesome icon is an inline-block; Chrome may break before it even after a word joiner, so the
        # title's last character moves with it. The text-arrow fallback keeps its word joiner after the title.
        record = {'id': 'scan-1', 'name': 'project', 'full_name': 'owner/project', 'url': 'https://github.com/owner/project',
                  'description_en': 'Describes one fixture.', 'description_zh': '描述一个测试条目。', 'stars': 1, 'license': 'MIT'}
        tail = '<span class="title-icon-tail">t' + icon('external', True) + '</span>'
        for language in ('en', 'zh'):
            with self.subTest(language=language):
                html = repository_card(record, language, True)
                self.assertIn('<span class="source-owner">owner/</span><span class="source-project">projec' + tail + '</span></a></h2>', html)
                self.assertEqual(html.count('fa-external'), 1)
                fallback = repository_card(record, language, False)
                self.assertIn('<span class="source-project">project</span>' + EXTERNAL_TITLE_ARROW + '</a></h2>', fallback)
                self.assertNotIn('title-icon-tail', fallback)
        plain = repository_card(dict(record, full_name='single'), 'en', True)
        self.assertIn('singl<span class="title-icon-tail">e' + icon('external', True) + '</span></a></h2>', plain)
        self.assertIn('.title-icon-tail{white-space:nowrap}', (ROOT / 'site/styles.css').read_text(encoding='utf-8'))
        # The homepage repository view builds the same tail.
        script = (ROOT / 'site/app.js').read_text(encoding='utf-8')
        self.assertIn('const tail = node("span","title-icon-tail",chars.pop() ?? ""); tail.append(icon("external",true)); '
                      'const project = node("span","source-project",chars.join("")); project.append(tail);', script)

    def test_arrow_stays_inline_so_the_joiner_applies(self):
        css = (ROOT / 'site/browse.css').read_text(encoding='utf-8')
        rule = re.search(r'\.browse-text-arrow\{([^}]*)\}', css)
        self.assertIsNotNone(rule)
        self.assertNotIn('display', rule[1])
        self.assertNotIn('margin', rule[1])
        # On phones a badge moves under the title only when a title word cannot fit beside it; break-word (not
        # anywhere) keeps the title's min-content at its longest word so flex wrapping can detect that.
        self.assertIn('@media(max-width:700px){.browse-main .card-heading{flex-wrap:wrap;gap:9px 11px}'
                      '.browse-main .card-heading :is(h3,h4){flex:1 1 min-content;overflow-wrap:break-word}}', css)
        # On the narrowest phones the badge moves under the title so a long last word keeps its arrow.
        self.assertIn('@media(max-width:380px){.browse-main .card-heading{flex-wrap:wrap;gap:9px}'
                      '.browse-main .card-heading :is(h3,h4){flex-basis:100%}}', css)


if __name__ == '__main__':
    unittest.main()
