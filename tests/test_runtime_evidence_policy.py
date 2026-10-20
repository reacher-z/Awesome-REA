"""Runtime and reproduction results are out of scope; nothing points contributors at the removed lab receipts."""
import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
STALE = re.compile(r'lab receipt|verification\.json|(?<![\w-])labs/', re.I)


def tracked(*patterns):
    result = subprocess.run(['git', 'ls-files', '-z', '--', *patterns], cwd=ROOT, capture_output=True, check=True)
    return [ROOT / name for name in result.stdout.decode('utf-8').split('\0') if name]


class RuntimeEvidencePolicyTests(unittest.TestCase):
    def test_no_document_script_or_ignore_rule_points_at_the_removed_labs(self):
        self.assertFalse((ROOT / 'labs').exists())
        files = [ROOT / '.gitignore'] + [path for path in tracked('*.md', 'scripts/*.py', '.github/*')
                                        if path.is_file()]
        self.assertGreater(len(files), 5)
        stale = [f'{path.relative_to(ROOT)}:{number}' for path in files
                 for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1) if STALE.search(line)]
        self.assertEqual(stale, [])

    def test_contributing_guides_state_the_current_policy(self):
        english = (ROOT / 'CONTRIBUTING.md').read_text(encoding='utf-8')
        chinese = (ROOT / 'CONTRIBUTING.zh-CN.md').read_text(encoding='utf-8')
        self.assertIn('Runtime and reproduction results are currently out of scope for catalog records', english)
        self.assertIn('You may describe what you ran in an issue', english)
        self.assertIn('目录记录目前不收录运行或复现结果', chinese)
        self.assertIn('可以在 issue 中说明自己运行了什么', chinese)

    def test_validator_messages_cite_the_policy(self):
        resources = (ROOT / 'scripts/validate.py').read_text(encoding='utf-8')
        papers = (ROOT / 'scripts/validate_papers.py').read_text(encoding='utf-8')
        self.assertIn('runtime and reproduction results are out of scope (see CONTRIBUTING.md)', resources)
        self.assertIn('this catalog records source review, not reproduced experiments', papers)

    def test_records_keep_their_verification_values(self):
        records = [record for name in ('rea-resources.json', 'tool-resources.json')
                   for record in json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))]
        papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
        self.assertEqual({record['verification'] for record in records}, {'source-reviewed'})
        self.assertEqual({paper['runtime_tested'] for paper in papers}, {False})


if __name__ == '__main__':
    unittest.main()
