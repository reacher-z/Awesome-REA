"""The index-to-curated worksheet example quotes the scan and curated records exactly and keeps them separate."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDES = {'en': ROOT / 'docs/promotion-worksheet.md', 'zh': ROOT / 'docs/promotion-worksheet.zh-CN.md'}
SCAN_ID, CURATED_ID = 'scan-272815213', 'capa'


def table_rows(text, header):
    lines = text.splitlines()
    start = lines.index(header)
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith('|'):
            break
        rows.append([cell.strip() for cell in line.strip('|').split('|')])
    return rows


class WorksheetTests(unittest.TestCase):
    def setUp(self):
        index = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))['resources']
        self.scan = next(record for record in index if record['id'] == SCAN_ID)
        catalog = json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))
        self.record = next(record for record in catalog if record['id'] == CURATED_ID)
        self.texts = {language: path.read_text(encoding='utf-8') for language, path in GUIDES.items()}

    def test_both_languages_have_the_same_worksheet_and_example_rows(self):
        headers = {'en': ('| Row | Question | Answer from |', '| Row | Answer |'),
                   'zh': ('| 行 | 问题 | 答案来源 |', '| 行 | 答案 |')}
        counts = {language: [len(table_rows(self.texts[language], header)) for header in headers[language]]
                  for language in headers}
        self.assertEqual(counts['en'], [12, 12])
        self.assertEqual(counts['zh'], counts['en'])

    def test_the_example_quotes_the_unchanged_scan_record(self):
        self.assertEqual(self.scan['verification'], 'automated-readme-scan')
        self.assertEqual(self.scan['url'], self.record['url'])
        for text in self.texts.values():
            for value in (SCAN_ID, self.scan['full_name'], self.scan['observed_at'][:19] + 'Z', self.scan['readme_git_sha'],
                          self.scan['readme_sha256'], f'{self.scan["readme_bytes"]:,}', 'automated-readme-scan',
                          *(f'`{label}`' for label in (*self.scan['targets'], self.scan['category']))):
                self.assertIn(value, text)

    def test_the_example_traces_the_curated_record_to_its_pinned_review(self):
        commit = re.search(r'/blob/([0-9a-f]{40})/README\.md$', self.record['evidence_url'])[1]
        for text in self.texts.values():
            for value in (commit, self.record['url'], self.record['verified_at'], f'`kind: {self.record["kind"]}`',
                          f'`relationship: {self.record["relationship"]}`', f'`category: {self.record["category"]}`'):
                self.assertIn(value, text)
            for target in self.record['targets']:
                self.assertIn(f'`{target}`', text)
        self.assertEqual(self.record['verification'], 'source-reviewed')
        line = next(line for line in (ROOT / 'docs/repositories/native-analysis.md').read_text(encoding='utf-8').splitlines()
                    if line.startswith(f'- [{self.scan["full_name"]}]('))
        self.assertIn(f'Curated: [{self.record["name"]}](https://awesomerea.org/resources/{CURATED_ID}/)', line)

    def test_a_hold_is_an_outcome_and_the_guides_are_linked(self):
        self.assertIn('Hold when the evidence is insufficient', self.texts['en'])
        self.assertIn('证据不足时应暂缓', self.texts['zh'])
        for path, target in (('CONTRIBUTING.md', 'docs/promotion-worksheet.md'),
                             ('CONTRIBUTING.zh-CN.md', 'docs/promotion-worksheet.zh-CN.md'),
                             ('docs/source-scan.md', 'promotion-worksheet.md')):
            self.assertIn(f']({target})', (ROOT / path).read_text(encoding='utf-8'))
        for index in ('docs/README.md', 'docs/README.zh-CN.md'):
            text = (ROOT / index).read_text(encoding='utf-8')
            self.assertIn('](promotion-worksheet.md)', text)
            self.assertIn('](promotion-worksheet.zh-CN.md)', text)


if __name__ == '__main__':
    unittest.main()
