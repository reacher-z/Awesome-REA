"""The README keeps recent cases while the generated case files hold the complete catalog."""
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_readme
from build_readme import (CASE_FILES, COLLECTION_SECTIONS, METHOD_SECTIONS, READMES, RECENT_CASES,
                          CASE_PAGE_BUDGET, README_SIZE_WARNING, case_method, case_order, collection_section, method_groups, recent_cases,
                          render_case_pages)
from catalog import load_resources
from validate_papers import read_papers


class ReadmeCasesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        paper_urls = {paper['url'] for paper in read_papers(ROOT)}
        cls.records = [record for record in load_resources() if record['url'] not in paper_urls]
        cls.groups = defaultdict(list)
        for record in cls.records:
            cls.groups[collection_section(record)].append(record)

    def test_readme_has_recent_cases_and_all_tools(self):
        for language, name in READMES.items():
            text = (ROOT / name).read_text(encoding='utf-8')
            for section in COLLECTION_SECTIONS:
                records = self.groups[section]
                cases = [record for record in records if record['kind'] == 'case-study']
                tools = [record for record in records if record['kind'] != 'case-study']
                expected = recent_cases(cases)
                block = text.split(f'<a id="{section}"></a>', 1)[1].split('\n<a id="', 1)[0] if records else ''
                ids = re.findall(r'^- .*resources/([a-z0-9-]+)/\)</sub>$', block, re.M)
                with self.subTest(language=language, section=section):
                    self.assertLessEqual(len(expected), RECENT_CASES)
                    self.assertEqual([identifier for identifier in ids if identifier in {r['id'] for r in cases}],
                                     [record['id'] for record in expected])
                    self.assertEqual({record['id'] for record in tools} & set(ids), {record['id'] for record in tools})
                    if len(cases) > RECENT_CASES:
                        self.assertIn(f']({CASE_FILES[language]}#{section})', block)

    def test_case_files_have_every_case_once_under_its_section(self):
        for language, name in CASE_FILES.items():
            index = (ROOT / name).read_text(encoding='utf-8')
            paths = sorted((ROOT / 'docs/cases').glob('*.zh-CN.md' if language == 'zh' else '*.md'))
            if language == 'en':
                paths = [path for path in paths if not path.name.endswith('.zh-CN.md')]
            text = '\n'.join(path.read_text(encoding='utf-8') for path in paths)
            ids = re.findall(r'^- .*resources/([a-z0-9-]+)/\)</sub>$', text, re.M)
            expected = [record for record in self.records if record['kind'] == 'case-study']
            self.assertEqual(Counter(ids), Counter(record['id'] for record in expected))
            for section in COLLECTION_SECTIONS:
                cases = [record for record in self.groups[section] if record['kind'] == 'case-study']
                if not cases:
                    continue
                block = '\n'.join(path.read_text(encoding='utf-8') for path in paths
                                  if path.name.startswith(section + '.') or path.name.startswith(section + '-'))
                self.assertEqual(set(re.findall(r'^- .*resources/([a-z0-9-]+)/\)</sub>$', block, re.M)),
                                 {record['id'] for record in cases})
            self.assertIn(f"](../{READMES[language]}#{'数据' if language == 'zh' else 'data'})", index)
            self.assertIn('cases.zh-CN.md' if language == 'en' else 'cases.md', index)
            self.assertIn('../cases' + ('.zh-CN' if language == 'zh' else '') + '.md', text)
            urls = re.findall(r'^- \[\*\*.*?\*\*\]\((https?://[^)]+)\) - ', text, re.M)
            self.assertEqual(len(urls), len(set(urls)))

    def test_method_anchors_and_full_list_links_resolve(self):
        for language in READMES:
            readme = (ROOT / READMES[language]).read_text(encoding='utf-8')
            full = (ROOT / CASE_FILES[language]).read_text(encoding='utf-8')
            for section in METHOD_SECTIONS:
                cases = [record for record in self.groups[section] if record['kind'] == 'case-study']
                for method, records in method_groups(cases):
                    anchor = f'{section}-{method}'
                    self.assertIn(f'<a id="{anchor}"></a>', readme)
                    self.assertIn(f'<a id="{anchor}"></a>', full)
                    self.assertIn(f']({CASE_FILES[language]}#{anchor})', readme)
                    self.assertTrue(all(case_method(record) == method for record in records))
            for anchor in re.findall(r'\]\(' + re.escape(CASE_FILES[language]) + r'#([a-z-]+)\)', readme):
                self.assertIn(f'<a id="{anchor}"></a>', full)

    def test_repeated_case_url_is_linked_once_per_file(self):
        original = next(record for record in self.records if record['kind'] == 'case-study')
        duplicate = deepcopy(original)
        duplicate['id'] = 'duplicate-case-fixture'
        for language in READMES:
            pages = render_case_pages([original, duplicate])
            text = '\n'.join(content for path, content in pages.items() if path.startswith('docs/cases/')
                             and path.endswith('.zh-CN.md' if language == 'zh' else '.md')
                             and (language == 'zh' or not path.endswith('.zh-CN.md')))
            self.assertEqual(text.count(f']({original["url"]})'), 1)
            self.assertIn('**' + original['name'].split(':', 1)[0], text)
            self.assertIn(f'/resources/{duplicate["id"]}/)', text)

    def test_every_generated_case_file_is_below_budget(self):
        for path in [ROOT / name for name in CASE_FILES.values()] + list((ROOT / 'docs/cases').glob('*.md')):
            with self.subTest(path=path):
                self.assertLessEqual(path.stat().st_size, CASE_PAGE_BUDGET)

    def test_readme_budget_leaves_case_pages_unchanged(self):
        with patch.object(build_readme, 'README_SIZE_WARNING', 50_000):
            raised = render_case_pages(self.records)
        self.assertEqual(raised, render_case_pages(self.records))

    def test_large_section_splits_in_both_languages(self):
        original = next(record for record in self.records if record['kind'] == 'case-study'
                        and collection_section(record) == 'game')
        records = [dict(original, id=f'large-case-{number}', url=f'https://example.com/large-{number}',
                        name=f'Large case {number}') for number in range(100)]
        budget = 8_000
        with patch.object(build_readme, 'CASE_PAGE_BUDGET', budget):
            pages = render_case_pages(records)
        for language in ('en', 'zh'):
            suffix = '.zh-CN.md' if language == 'zh' else '.md'
            names = [name for name in pages if re.fullmatch(r'docs/cases/game-\d+' + re.escape(suffix), name)]
            self.assertGreater(len(names), 1)
            self.assertTrue(all(len(pages[name].encode('utf-8')) <= budget for name in names))
            listed = [identifier for name in sorted(names, key=lambda value: int(re.search(r'-(\d+)\.', value)[1]))
                      for identifier in re.findall(r'resources/(large-case-\d+)/', pages[name])]
            self.assertEqual(listed, [record['id'] for record in sorted(records, key=case_order)])


if __name__ == '__main__':
    unittest.main()
