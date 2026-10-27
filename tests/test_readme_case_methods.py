"""Game case studies are grouped by their reviewed reconstruction method, in a fixed, locale-independent order."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import (BEGIN, END, RECONSTRUCTION_METHODS, case_order, collection_section, render_catalog,
                          replace_catalog)
from catalog import load_resources
from validate import validate_resources


def case(identifier, method, **changes):
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0])
    record.update(id=identifier, name=identifier, url=f'https://example.com/{identifier}', kind='case-study',
                  category='reconstruction-cases', relationship='independent-reconstruction', targets=['game'],
                  reconstruction_method=method)
    record.update(changes)
    return record


def tool(identifier):
    record = case(identifier, None, kind='tool', category='game-analysis', relationship='foundation')
    del record['reconstruction_method']
    return record


class ReadmeCaseMethodTests(unittest.TestCase):
    def test_groups_follow_the_vocabulary_and_names_ignore_case(self):
        records = [case('zeta', 'port'), case('Alpha', 'port'), case('beta', 'port'),
                   case('match', 'matching-decompilation'), tool('game-tool')]
        before = deepcopy(records)
        for language in ('en', 'zh'):
            with self.subTest(language=language):
                rendered = render_catalog(records, language)
                headings = re.findall(r'^(#{4,5}) (.+)$', rendered, re.MULTILINE)
                labels = [names[language == 'zh'] for names in RECONSTRUCTION_METHODS.values()]
                self.assertEqual(headings, [
                    ('####', '案例' if language == 'zh' else 'Case studies'),
                    ('#####', labels[0] + ' (1)'), ('#####', labels[3] + ' (3)'),
                    ('####', '工具、项目与集成' if language == 'zh' else 'Tools, projects and integrations')])
                self.assertIn('<a id="game-port"></a>\n##### ', rendered)
                order = re.findall(r'example\.com/([\w-]+)\)', rendered)
                self.assertEqual(order, ['match', 'Alpha', 'beta', 'zeta', 'game-tool'])
        self.assertEqual(records, before)
        # Without tools the groups sit directly under the section heading.
        self.assertIn('\n#### ' + RECONSTRUCTION_METHODS['port'][0] + ' (1)\n', render_catalog([case('only', 'port')], 'en'))
        with self.assertRaisesRegex(ValueError, 'only: reconstruction_method'):
            render_catalog([case('only', 'guess')], 'en')
        self.assertEqual(sorted([case('b', 'port'), case('A', 'port')], key=case_order)[0]['id'], 'A')

    def test_validator_requires_a_known_method_only_on_game_case_studies(self):
        for record, expected in ((case('known', 'other'), None),
                                 (case('unknown', 'guess'), 'need one of'),
                                 (case('missing', None), 'need one of'),
                                 (case('app-case', 'port', targets=['app']), 'only case studies listed under Game'),
                                 (tool('game-tool') | {'reconstruction_method': 'port'}, 'only case studies listed under Game')):
            with self.subTest(record=record['id']):
                if record.get('reconstruction_method') is None:
                    record.pop('reconstruction_method', None)
                errors = []
                validate_resources([record], errors)
                if expected:
                    self.assertEqual(len(errors), 1, errors)
                    self.assertIn('.reconstruction_method: ', errors[0])
                    self.assertIn(expected, errors[0])
                else:
                    self.assertEqual(errors, [])

    def test_each_game_case_appears_once_under_its_method_in_both_readmes(self):
        cases = [record for record in load_resources()
                 if record['kind'] == 'case-study' and collection_section(record) == 'game']
        self.assertTrue(cases)
        listed = {}
        for name, language in (('README.md', 'en'), ('README.zh-CN.md', 'zh')):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                game = text.split('<a id="game"></a>', 1)[1].split('\n#### ', 2)[1]
                groups = re.split(r'\n<a id="game-([a-z-]+)"></a>\n##### ', game)[1:]
                order = []
                for method, block in zip(groups[::2], groups[1::2]):
                    heading, _, body = block.partition('\n')
                    ids = re.findall(r'^- .*resources/([a-z0-9-]+)/\)</sub>$', body, re.MULTILINE)
                    self.assertEqual(heading, f'{RECONSTRUCTION_METHODS[method][language == "zh"]} ({len(ids)})')
                    expected = sorted((record for record in cases if record['reconstruction_method'] == method), key=case_order)
                    self.assertEqual(ids, [record['id'] for record in expected])
                    order += ids
                self.assertEqual(sorted(order), sorted(record['id'] for record in cases))
                listed[language] = order
        self.assertEqual(listed['en'], listed['zh'])

    def test_a_stale_order_or_count_is_rewritten(self):
        text = (ROOT / 'README.md').read_text(encoding='utf-8')
        records = load_resources()
        from validate_papers import read_papers
        paper_urls = {paper['url'] for paper in read_papers(ROOT)}
        current = replace_catalog(text, render_catalog(records, 'en', paper_urls))
        lines = current.split('\n')
        start = lines.index('<a id="game-port"></a>') + 3
        swapped = lines[:start] + [lines[start + 1], lines[start]] + lines[start + 2:]
        stale_count = current.replace(f"{RECONSTRUCTION_METHODS['port'][0]} (", f"{RECONSTRUCTION_METHODS['port'][0]} (9", 1)
        for stale in ('\n'.join(swapped), stale_count):
            self.assertNotEqual(stale, current)
            self.assertEqual(replace_catalog(stale, render_catalog(records, 'en', paper_urls)), current)
        self.assertIn(BEGIN, current)
        self.assertIn(END, current)


if __name__ == '__main__':
    unittest.main()
