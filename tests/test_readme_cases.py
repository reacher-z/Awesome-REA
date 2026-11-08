"""The README keeps recent cases while the generated case files hold the complete catalog."""
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import (CASE_FILES, COLLECTION_SECTIONS, METHOD_SECTIONS, READMES, RECENT_CASES,
                          case_method, collection_section, method_groups, recent_cases, render_cases)
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
                # Sub-heading anchors ({section}-cases, {section}-tools, method groups) live inside the block,
                # so cut at the next section-level anchor instead of the next anchor of any kind.
                rest = text.split(f'<a id="{section}"></a>', 1)[1] if records else ''
                cuts = [rest.find(f'\n<a id="{key}"></a>') for key in COLLECTION_SECTIONS if key != section]
                block = rest[:min((cut for cut in cuts if cut >= 0), default=len(rest))]
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
            text = (ROOT / name).read_text(encoding='utf-8')
            ids = re.findall(r'^- .*resources/([a-z0-9-]+)/\)</sub>$', text, re.M)
            expected = [record for record in self.records if record['kind'] == 'case-study']
            self.assertEqual(Counter(ids), Counter(record['id'] for record in expected))
            for section in COLLECTION_SECTIONS:
                cases = [record for record in self.groups[section] if record['kind'] == 'case-study']
                if not cases:
                    continue
                block = text.split(f'<a id="{section}"></a>', 1)[1].split('\n<a id="', 1)[0]
                # Method headings introduce anchors, so inspect the range through the next section instead.
                following = [key for key in COLLECTION_SECTIONS if key != section and f'<a id="{key}"></a>' in text
                             and text.index(f'<a id="{key}"></a>') > text.index(f'<a id="{section}"></a>')]
                if following:
                    block = text.split(f'<a id="{section}"></a>', 1)[1].split(f'<a id="{following[0]}"></a>', 1)[0]
                self.assertEqual(set(re.findall(r'^- .*resources/([a-z0-9-]+)/\)</sub>$', block, re.M)),
                                 {record['id'] for record in cases})
            self.assertIn(f"](../{READMES[language]}#{'资源' if language == 'zh' else 'resources'})", text)
            self.assertIn('cases.zh-CN.md' if language == 'en' else 'cases.md', text)
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
            text = render_cases([original, duplicate], language)
            self.assertEqual(text.count(f']({original["url"]})'), 1)
            self.assertIn('**' + original['name'].split(':', 1)[0], text)
            self.assertIn(f'/resources/{duplicate["id"]}/)', text)


if __name__ == '__main__':
    unittest.main()
