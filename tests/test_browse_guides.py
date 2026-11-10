"""Repository category pages open with a definition, a comparison table and questions computed from their own records."""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from html import unescape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_browse_pages import build_browse_pages
from build_repository_index import CATEGORIES
import browse_guides


def record(index, **extra):
    return {'id': f'scan-{index}', 'full_name': f'owner/tool-{index}', 'name': f'tool-{index}',
            'url': f'https://github.com/owner/tool-{index}', 'description_en': 'A disassembler.',
            'description_zh': '一个反汇编器。', 'stars': 1000 - index * 100, 'license': ('MIT', 'GPL-3.0', 'NOASSERTION')[index % 3],
            'pushed_at': f'2026-0{index % 9 + 1}-15T08:00:00Z', 'targets': ['binary'], 'category': 'native-analysis',
            'scan_status': 'readme-scanned', **extra}


CURATED = [{'kind': 'curated', 'id': 'ghidra', 'title_en': 'Ghidra', 'title_zh': 'Ghidra',
            'href_en': '/resources/ghidra/', 'href_zh': '/zh/resources/ghidra/'}]


def build(output):
    resources = [record(index, **({'related_entries': CURATED} if index == 0 else {})) for index in range(8)]
    document = {'meta': {'schema_version': 1, 'status': 'complete', 'completed_at': '2026-10-20T00:00:00Z'},
                'resources': resources}
    build_browse_pages(output, document, curated_count=1, site_url='https://awesomerea.org',
                       repository_url='https://github.com/reacher-z/Awesome-REA', styles_href='/styles.css',
                       browse_styles_href='/browse.css', favicon_href='/favicon.svg',
                       social_image_href='https://awesomerea.org/social-card.png', data_revision='0' * 16,
                       scan_classes={'scan-0': 1, 'scan-1': 2, 'scan-2': 3})


class BrowseGuideTests(unittest.TestCase):
    def test_every_category_has_a_definition_in_both_languages_within_sixty_words(self):
        self.assertEqual(set(browse_guides.DEFINITIONS), set(CATEGORIES))
        self.assertEqual(set(browse_guides.QUESTION_NAMES), set(CATEGORIES))
        for english, chinese in browse_guides.DEFINITIONS.values():
            self.assertLessEqual(len(english.split()), 60)
            self.assertTrue(chinese.endswith('。'))

    def test_category_page_shows_definition_table_and_questions_before_the_cards(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build(output)
            for prefix, zh in (('', False), ('zh/', True)):
                text = (output / prefix / 'browse/native-analysis/index.html').read_text()
                self.assertIn(browse_guides.definition('native-analysis', zh), text)
                guide = text.index('<section class="browse-guide"')
                self.assertLess(text.index('browse-definition'), guide)
                self.assertLess(guide, text.index('<article class="source-card'))
                table = re.search(r'<table>(.*?)</table>', text, re.S)[1]
                rows = re.findall(r'<th scope="row"><a href="([^"]+)">', table)
                self.assertEqual(rows, [f'https://github.com/owner/tool-{index}' for index in range(browse_guides.ROWS)])
                self.assertIn('1,000', table)
                blocks = [json.loads(block) for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)]
                faq = [block for block in blocks if block['@type'] == 'FAQPage']
                self.assertEqual(len(faq), 1)
                questions = faq[0]['mainEntity']
                self.assertTrue(3 <= len(questions) <= 5, len(questions))
                visible = unescape(re.sub(r'<[^>]+>', '', text[guide:text.index('<article class="source-card')]))
                for question in questions:
                    self.assertIn(question['name'], visible)
                    self.assertIn(question['acceptedAnswer']['text'], visible)
                answers = ' '.join(question['acceptedAnswer']['text'] for question in questions)
                self.assertIn('tool-0', answers)
                markdown = (output / prefix / 'browse/native-analysis/index.md').read_text()
                self.assertIn(browse_guides.definition('native-analysis', zh), markdown)
                for question in questions:
                    self.assertIn('**' + question['name'] + '**', markdown)
                empty = (output / prefix / 'browse/firmware/index.html').read_text()
                self.assertNotIn('FAQPage', empty)
                self.assertNotIn('browse-guide', empty)
                self.assertNotIn('FAQPage', (output / prefix / 'browse/index.html').read_text())

    def test_questions_count_licenses_and_unidentified_licenses_from_the_records(self):
        records = [record(index) for index in range(6)]
        english = dict(browse_guides.faqs('native-analysis', 'native-binary', records, {}, False, '2026-10-20'))
        self.assertEqual(english['Which licenses do these repositories use?'],
                         'The most common license identifiers are MIT (2) and GPL-3.0 (2). 2 of 6 have no identified license.')
        self.assertNotIn('Which of these repositories have a curated entry?', english)


    def test_questions_are_full_sentences_and_examples_use_short_names(self):
        records = [record(index, **({'related_entries': [dict(CURATED[0], title_en='LibrePods: AirPods features on Android and Linux')]} if index == 0 else {})) for index in range(4)]
        classes = {'scan-0': 1, 'scan-1': 2, 'scan-2': 3}
        english = dict(browse_guides.faqs('android', 'Android app', records, classes, False, '2026-10-20'))
        chinese = dict(browse_guides.faqs('android', 'Android 应用', records, classes, True, '2026-10-20'))
        self.assertEqual(english['How many of these repositories document installation and usage in their README?'],
                         '1 of 4 documents both installation and usage in their README (scan class C1). '
                         '1 is missing one of the two (C2) and 1 has no usable README documentation (C3). 1 has no README scan class.')
        self.assertIn('这些仓库中有多少在 README 中写明了安装和用法？', chinese)
        self.assertIn('哪些 Android 应用类仓库的星标最多？', chinese)
        curated = english['Which of these repositories have a curated entry?']
        self.assertIn('href="/resources/ghidra/">owner/tool-0</a>', curated)
        self.assertNotIn('AirPods', curated)


if __name__ == '__main__':
    unittest.main()
