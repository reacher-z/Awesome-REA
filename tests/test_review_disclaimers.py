"""Requirement sentences about the catalog's own review are listed for reviewers."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from catalog import RESOURCE_FILES
import review_disclaimers
from review_disclaimers import banned_sentences, defensive_sentences, findings


class ReviewDisclaimerTests(unittest.TestCase):
    def test_self_references_are_listed_per_sentence_in_both_languages(self):
        records = [{'id': 'fixture', 'requirements': [
            'Needs Python 3. This collection did not run it.', 'This entry covers the CLI only; this review read docs.',
            'Author results only. Not run or reproduced for this catalog.']},
            {'id': 'plain', 'requirements': 'Needs a user-supplied ROM.'}]
        translations = {'fixture': {'requirements': ['需要 Python 3。本合集未运行。', '仅覆盖命令行；本次只审阅文档。',
                                                     '仅为作者结果。本目录未运行或复现。']}}
        self.assertEqual(findings(records, translations), [
            ('fixture', 'en', 0, 'This collection did not run it.'),
            ('fixture', 'en', 1, 'This entry covers the CLI only;'),
            ('fixture', 'en', 1, 'this review read docs.'),
            ('fixture', 'en', 2, 'Not run or reproduced for this catalog.'),
            ('fixture', 'zh', 0, '本合集未运行。'),
            ('fixture', 'zh', 1, '本次只审阅文档。'),
            ('fixture', 'zh', 2, '本目录未运行或复现。'),
        ])

    def test_report_summarizes_and_never_fails(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            status = review_disclaimers.main()
        self.assertEqual(status, 0)
        self.assertRegex(stdout.getvalue().splitlines()[-1],
                         r"^\d+ requirement sentences in \d+ records refer to this catalog's review")

    def test_banned_phrasings_are_found_in_requirements_and_paper_notes(self):
        records = [{'id': 'tool', 'requirements': ['Needs Python 3. This collection did not run it.']},
                   {'id': 'plain', 'requirements': 'This entry pins the reviewed commit.'}]
        translations = {'tool': {'requirements': ['需要 Python 3。本合集未运行。']}}
        papers = [{'id': 'paper', 'metadata_notes': 'No runtime reproduction is claimed.', 'metadata_notes_zh': '本合集未复现。'}]
        self.assertEqual([(identifier, field) for identifier, field, _ in banned_sentences(records, translations, papers)],
                         [('tool', 'requirements'), ('tool', 'requirements (zh)'),
                          ('paper', 'metadata_notes'), ('paper', 'metadata_notes_zh')])

    def test_the_catalog_uses_no_banned_phrasing(self):
        records = [record for path in RESOURCE_FILES for record in json.loads(path.read_text(encoding='utf-8'))]
        translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
        papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
        self.assertEqual(banned_sentences(records, translations, papers), [])

    def test_defensive_phrasings_are_found_in_every_visible_field(self):
        records = [{'id': 'tool', 'description_en': 'A decompiler. Its output does not imply source recovery.',
                    'requirements': ['Needs Python 3.', 'No REA use is established.']},
                   {'id': 'plain', 'description_en': 'A decompiler that emits C.', 'requirements': ['Needs Python 3.']}]
        translations = {'tool': {'requirements': ['需要 Python 3。', '输出不代表恢复了源码。']}}
        papers = [{'id': 'paper', 'scope_limitations_en': 'Passing tests is not evidence of equivalence.',
                   'metadata_notes_zh': '会议日期并非出版日期。', 'date_basis_zh': '采用年份，不主张更精确的日期。'}]
        ledger = [{'id': 'lead', 'reason_en': 'Retain the lead; neither asserts runtime behavior.', 'reason_zh': '保留线索。'}]
        reviews = {'scan-1': {'reason_en': 'A CTF archive.', 'reason_zh': '列入合集不意味着已经验证。'}}
        self.assertEqual([(identifier, field) for identifier, field, _ in
                          defensive_sentences(records, translations, papers, ledger, reviews)],
                         [('tool', 'description_en'), ('tool', 'requirements'), ('tool', 'requirements (zh)'),
                          ('paper', 'scope_limitations_en'), ('paper', 'metadata_notes_zh'), ('paper', 'date_basis_zh'),
                          ('lead', 'reason_en'),
                          ('scan-1', 'reason_zh')])

    def test_plain_statements_of_scope_pass_the_defensive_check(self):
        records = [{'id': 'tool', 'description_en': 'The output is a GBA ROM, and the README says it is not a PC port.',
                    'requirements': ['MIT. Original game data keeps its owners’ rights.', 'Other versions are untested.']}]
        papers = [{'id': 'paper', 'date_basis': 'Publication year from the official proceedings.'}]
        self.assertEqual(defensive_sentences(records, {}, papers), [])

    def test_the_catalog_text_uses_no_defensive_phrasing(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        from case_coverage import read_case_coverage
        from discovery_reviews import read_reviews
        records = [record for path in RESOURCE_FILES for record in json.loads(path.read_text(encoding='utf-8'))]
        translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
        papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
        self.assertEqual(defensive_sentences(records, translations, papers, read_case_coverage(ROOT)['entries'],
                                             read_reviews(ROOT)), [])

    def test_banned_sentences_skips_malformed_values_for_the_schema_checks(self):
        records = [{'id': 'no-requirements'}, {'id': 'number', 'requirements': 3}]
        self.assertEqual(banned_sentences(records, {'number': 'bad'}, [{'id': 'p', 'metadata_notes': 3}]), [])

    def test_a_study_limitation_in_chinese_is_allowed(self):
        paper = {'id': 'p', 'scope_limitations_zh': '本次未发布数据集。'}
        self.assertEqual(banned_sentences([], {}, [paper]), [])


if __name__ == '__main__':
    unittest.main()
