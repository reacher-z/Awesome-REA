"""The paper update guide's worked example matches the bibliography and both languages give the same steps."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDES = {'en': ROOT / 'docs/paper-updates.md', 'zh': ROOT / 'docs/paper-updates.zh-CN.md'}


def example_rows(text):
    """Map each field cell of the worked-example table to its (before, after) cells."""
    lines = text.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith('| Field | Before') or line.startswith('| 字段 | 更新前'))
    rows = {}
    for line in lines[start + 2:]:
        if not line.startswith('|'):
            break
        field, before, after = [cell.strip() for cell in line.strip('|').split('|')]
        rows[field] = (before, after)
    return rows


class PaperUpdateGuideTests(unittest.TestCase):
    def setUp(self):
        self.papers = {paper['id']: paper for paper in json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))}
        self.texts = {language: path.read_text(encoding='utf-8') for language, path in GUIDES.items()}

    def test_the_worked_example_keeps_one_record_and_matches_its_current_fields(self):
        paper = self.papers['paper-crebench']
        self.assertEqual([identifier for identifier in self.papers if 'crebench' in identifier], ['paper-crebench'])
        for language, text in self.texts.items():
            rows = example_rows(text)
            with self.subTest(language=language):
                self.assertEqual(len(rows), 9)
                self.assertTrue(rows['`id`'][1].startswith('`paper-crebench`'))
                self.assertEqual(rows['`id`'][0], '`paper-crebench`')
                self.assertEqual(rows['`publication_status`'], ('`conference-accepted`', f'`{paper["publication_status"]}`'))
                self.assertEqual(rows['`url`'][1], f'`{paper["url"]}`')
                self.assertTrue(rows['`pdf_url`'][1].startswith(f'`{paper["pdf_url"]}`'))
                arxiv = next(value for field, value in rows.items() if field.startswith('`arxiv_id`'))
                self.assertEqual(arxiv[0], f'`{paper["arxiv_id"]}`、`{paper["first_arxiv_date"]}`、`{paper["arxiv_version_reviewed"]}`'
                                 if language == 'zh' else
                                 f'`{paper["arxiv_id"]}`, `{paper["first_arxiv_date"]}`, `{paper["arxiv_version_reviewed"]}`')
                self.assertIsNone(paper['doi'])
                self.assertTrue(rows['`doi`'][1].startswith('`null`'))
                self.assertEqual((paper['date_precision'], paper['publication_date']), ('year', None))
                self.assertIn(paper['verified_at'], text)
                for url in ('https://openreview.net/forum?id=tLYdf8hWJB', 'https://arxiv.org/abs/2604.03750'):
                    self.assertIn(url, paper['evidence_urls'])
        self.assertIn('2026-07-08', paper['metadata_notes'])
        self.assertIn('not used as a publication date', paper['metadata_notes'])

    def test_the_same_work_and_follow_up_examples_match_the_records(self):
        dire, dirty = self.papers['paper-dire'], self.papers['paper-dirty']
        self.assertIn("'Naming'", dire['metadata_notes'])
        self.assertIn("'Renaming'", dire['metadata_notes'])
        self.assertIn('deprecated', dire['metadata_notes'])
        self.assertNotEqual((dire['title'], dire['arxiv_id']), (dirty['title'], dirty['arxiv_id']))
        for text in self.texts.values():
            self.assertIn('`paper-dirty`', text)
            self.assertIn('`paper-dire`', text)

    def test_both_languages_name_the_same_existing_commands_and_are_linked(self):
        commands = [re.findall(r'^```sh\n(.*?)^```$', text, re.MULTILINE | re.DOTALL) for text in self.texts.values()]
        self.assertEqual(commands[0], commands[1])
        self.assertIn('python3 scripts/validate_papers.py', commands[0][0])
        for script in re.findall(r'scripts/([a-z_]+\.py)', commands[0][0]):
            self.assertTrue((ROOT / 'scripts' / script).is_file(), script)
        for path, target in (('CONTRIBUTING.md', 'docs/paper-updates.md'), ('CONTRIBUTING.zh-CN.md', 'docs/paper-updates.zh-CN.md')):
            self.assertIn(f']({target})', (ROOT / path).read_text(encoding='utf-8'))
        for index in ('docs/README.md', 'docs/README.zh-CN.md'):
            text = (ROOT / index).read_text(encoding='utf-8')
            self.assertIn('](paper-updates.md)', text)
            self.assertIn('](paper-updates.zh-CN.md)', text)


if __name__ == '__main__':
    unittest.main()
