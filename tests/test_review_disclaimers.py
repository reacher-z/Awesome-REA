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
from review_disclaimers import findings


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


if __name__ == '__main__':
    unittest.main()
