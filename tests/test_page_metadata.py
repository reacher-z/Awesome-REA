import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from build_readme import CATEGORIES  # noqa: E402
from page_metadata import (DESCRIPTION_MAX, DESCRIPTION_MIN, TITLE_MAX, description_problem, meta_description, page_title,  # noqa: E402
                           paper_description, resource_description, shorten, title_problem)


class PageTitleTests(unittest.TestCase):
    def test_short_name_keeps_context_and_site(self):
        self.assertEqual(page_title('rr', 'Debugging'), 'rr · Debugging · AwesomeREA.org')

    def test_site_goes_before_the_context(self):
        name = 'A' * 30
        self.assertEqual(page_title(name, 'B' * 20), f'{name} · {"B" * 20}')

    def test_context_goes_when_name_and_context_do_not_fit(self):
        name = 'A' * 40
        self.assertEqual(page_title(name, 'B' * 30), f'{name} · AwesomeREA.org')

    def test_name_stands_alone_rather_than_being_cut(self):
        name = 'A' * 58
        self.assertEqual(page_title(name), name)

    def test_long_name_is_cut_at_a_word(self):
        title = page_title('Decompiling Binary Code with Large Language Models and Many Further Words Here')
        self.assertLessEqual(len(title), TITLE_MAX)
        self.assertTrue(title.endswith('…'))
        self.assertNotIn(' …', title)
        self.assertTrue(title.startswith('Decompiling Binary Code with Large Language'))

    def test_keep_context_never_gives_up_the_context(self):
        name = 'Some Very Long English Project Name That Runs Past The Limit On Its Own'
        title = page_title(name, '二进制', keep_context=True)
        self.assertTrue(title.endswith(' · 二进制'))
        self.assertLessEqual(len(title), TITLE_MAX)
        self.assertEqual(page_title('rr', '二进制', keep_context=True), 'rr · 二进制 · AwesomeREA.org')

    def test_title_problem_names_length_and_separator(self):
        self.assertIsNone(title_problem('rr · Debugging · AwesomeREA.org'))
        self.assertIn('over 60', title_problem('A' * 61))
        self.assertIn('separator', title_problem('rr | AwesomeREA.org'))


class MetaDescriptionTests(unittest.TestCase):
    def test_text_in_range_is_unchanged(self):
        text = 'A' * 100
        self.assertEqual(meta_description(text, 'Never added.'), text)

    def test_facts_extend_a_short_text_only_until_it_fits(self):
        result = meta_description('Short text without a stop', 'A' * 50, 'Never added.')
        self.assertEqual(result, 'Short text without a stop. ' + 'A' * 50)

    def test_chinese_facts_join_without_a_space(self):
        result = meta_description('中文说明', '补' * 70)
        self.assertEqual(result, '中文说明。' + '补' * 70)

    def test_long_text_ends_at_a_sentence(self):
        first = 'First sentence is long enough to pass the minimum length rule of this description field.'
        self.assertEqual(meta_description(first + ' ' + 'Second ' * 40), first)

    def test_version_number_is_not_a_sentence_end(self):
        text = 'A' * 80 + ' supports v1.2 and more ' + 'word ' * 40
        result = meta_description(text)
        self.assertTrue(result.endswith('…'))
        self.assertIn('v1.2', result)

    def test_long_text_without_a_sentence_end_is_cut_at_a_word(self):
        result = meta_description('word ' * 60)
        self.assertLessEqual(len(result), DESCRIPTION_MAX)
        self.assertTrue(result.endswith('word…'))

    def test_chinese_text_is_cut_at_punctuation(self):
        self.assertEqual(shorten('甲' * 30 + '，' + '乙' * 30, 40), '甲' * 30 + '…')

    def test_description_problem_reports_both_limits(self):
        self.assertIsNone(description_problem('A' * DESCRIPTION_MIN))
        self.assertIsNone(description_problem('A' * DESCRIPTION_MAX))
        self.assertIsNotNone(description_problem('A' * (DESCRIPTION_MIN - 1)))
        self.assertIsNotNone(description_problem('A' * (DESCRIPTION_MAX + 1)))


class CatalogDescriptionTests(unittest.TestCase):
    """Every record the catalog holds today fits, in both languages."""

    def test_every_resource_fits_with_recorded_facts(self):
        for name in ('tool-resources.json', 'rea-resources.json'):
            for record in json.loads((ROOT / 'data' / name).read_text(encoding='utf-8')):
                for index, language in enumerate(('en', 'zh')):
                    description = resource_description(record, language, CATEGORIES[record['category']][index])
                    self.assertIsNone(description_problem(description), record['id'])

    def test_every_paper_fits(self):
        document = json.loads((ROOT / 'data' / 'papers.json').read_text(encoding='utf-8'))
        for record in document if isinstance(document, list) else document['papers']:
            for language in ('en', 'zh'):
                self.assertIsNone(description_problem(paper_description(record, language)), record['id'])

    def test_added_facts_come_from_the_record(self):
        record = {'description_zh': '简短说明。', 'verified_at': '2026-10-15T00:00:00Z'}
        description = resource_description(record, 'zh', '二进制分析')
        self.assertIn('二进制分析', description)
        self.assertIn('2026-10-15', description)
        paper = {'description_en': 'Short.', 'venue': 'USENIX Security', 'year': 2025}
        self.assertIn('USENIX Security, 2025', paper_description(paper, 'en'))


if __name__ == '__main__':
    unittest.main()
