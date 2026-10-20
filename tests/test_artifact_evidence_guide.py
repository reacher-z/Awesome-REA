"""Every wording example in the artifact and license guide is quoted from the record it names, in both languages."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDES = {'en': ROOT / 'docs/artifact-evidence.md', 'zh': ROOT / 'docs/artifact-evidence.zh-CN.md'}


def table_rows(text):
    """Return (situation, example wording, record ID) for each decision-table row."""
    rows = []
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip('|').split('|')] if line.startswith('|') else []
        if len(cells) == 4 and re.fullmatch(r'`[a-z0-9-]+`', cells[3]):
            quote = re.fullmatch(r'“(.+)”', cells[2])
            rows.append((cells[0], quote[1] if quote else None, cells[3].strip('`')))
    return rows


class ArtifactEvidenceGuideTests(unittest.TestCase):
    def setUp(self):
        self.papers = {paper['id']: paper for paper in json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))}
        self.resources = {record['id']: record for name in ('rea-resources.json', 'tool-resources.json')
                          for record in json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))}
        self.translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))

    def record_text(self, identifier, language):
        if identifier in self.papers:
            paper = self.papers[identifier]
            fields = ('metadata_notes', 'scope_limitations_en') if language == 'en' else ('metadata_notes_zh', 'scope_limitations_zh')
            return ' '.join(paper[field] for field in fields)
        requirements = self.resources[identifier]['requirements'] if language == 'en' else self.translations[identifier]['requirements']
        return ' '.join(requirements) if isinstance(requirements, list) else requirements

    def test_each_example_is_quoted_verbatim_from_its_record(self):
        for language, path in GUIDES.items():
            rows = table_rows(path.read_text(encoding='utf-8'))
            self.assertEqual(len(rows), 11, language)
            for situation, quote, identifier in rows:
                with self.subTest(language=language, record=identifier, situation=situation):
                    self.assertIsNotNone(quote)
                    self.assertIn(quote, self.record_text(identifier, language))

    def test_both_languages_cite_the_same_records_in_the_same_order(self):
        cited = [[identifier for _, _, identifier in table_rows(path.read_text(encoding='utf-8'))] for path in GUIDES.values()]
        self.assertEqual(cited[0], cited[1])

    def test_null_artifact_rows_match_records_without_author_code(self):
        for identifier in ('paper-sprite-game-ui', 'paper-dynpre', 'paper-binmetric', 'paper-gamereplica'):
            self.assertIsNone(self.papers[identifier]['code_url'], identifier)
        self.assertIsNotNone(self.papers['paper-dashboard2code']['code_url'])

    def test_the_guide_is_linked_from_both_contribution_guides_and_indexes(self):
        for path, target in (('CONTRIBUTING.md', 'docs/artifact-evidence.md'), ('CONTRIBUTING.zh-CN.md', 'docs/artifact-evidence.zh-CN.md')):
            self.assertIn(f']({target})', (ROOT / path).read_text(encoding='utf-8'))
        for index in ('docs/README.md', 'docs/README.zh-CN.md'):
            text = (ROOT / index).read_text(encoding='utf-8')
            self.assertIn('](artifact-evidence.md)', text)
            self.assertIn('](artifact-evidence.zh-CN.md)', text)


if __name__ == '__main__':
    unittest.main()
