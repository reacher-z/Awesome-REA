"""Requirement sentences about the catalog's own review are listed for reviewers; the documented phrase is not."""
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
from review_disclaimers import PHRASE_EN, PHRASE_ZH, findings

EDITED = ('rea-aegis-case', 'battleship-port-case', 'sm64ds-decomp-case', 'kartpad-case')


class ReviewDisclaimerTests(unittest.TestCase):
    def test_self_references_are_listed_per_sentence_in_both_languages(self):
        records = [{'id': 'fixture', 'requirements': [
            'Needs Python 3. This collection did not run it.', 'This entry covers the CLI only; this review read docs.',
            'Author results only. ' + PHRASE_EN]},
            {'id': 'plain', 'requirements': 'Needs a user-supplied ROM.'}]
        translations = {'fixture': {'requirements': ['需要 Python 3。本合集未运行。', '仅覆盖命令行；本次只审阅文档。',
                                                     '仅为作者结果。' + PHRASE_ZH]}}
        self.assertEqual(findings(records, translations), [
            ('fixture', 'en', 0, 'This collection did not run it.'),
            ('fixture', 'en', 1, 'This entry covers the CLI only;'),
            ('fixture', 'en', 1, 'this review read docs.'),
            ('fixture', 'zh', 0, '本合集未运行。'),
            ('fixture', 'zh', 1, '本次只审阅文档。'),
        ])

    def test_records_named_in_the_issue_no_longer_carry_review_disclaimers(self):
        records = [record for path in RESOURCE_FILES for record in json.loads(path.read_text(encoding='utf-8'))
                   if record['id'] in EDITED]
        translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))
        self.assertEqual(len(records), len(EDITED))
        self.assertEqual(findings(records, translations), [])

    def test_report_summarizes_and_never_fails(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            status = review_disclaimers.main()
        self.assertEqual(status, 0)
        self.assertRegex(stdout.getvalue().splitlines()[-1],
                         r"^\d+ requirement sentences in \d+ records refer to this catalog's review")


if __name__ == '__main__':
    unittest.main()
