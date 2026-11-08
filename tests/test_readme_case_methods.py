"""Game case studies are grouped by their reviewed reconstruction method, in a fixed, locale-independent order;
cases without one are listed last, and the validator only warns about them."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import (BEGIN, END, METHOD_HEADINGS, RECONSTRUCTION_METHODS, UNASSIGNED_METHOD, case_method,
                          case_order, collection_section, render_catalog, replace_catalog)
from catalog import load_resources
from validate import missing_method_warnings, validate_resources


def case(identifier, method=None, **changes):
    """A Game case study; without `method` it has no reconstruction_method field at all."""
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0])
    record.update(id=identifier, name=identifier, url=f'https://example.com/{identifier}', kind='case-study',
                  category='reconstruction-cases', relationship='independent-reconstruction', targets=['game'])
    if method is not None:
        record['reconstruction_method'] = method
    record.update(changes)
    return record


def tool(identifier):
    return case(identifier, kind='tool', category='game-analysis', relationship='foundation')


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

    def test_cases_without_a_method_form_a_final_group_only_when_present(self):
        records = [case('pending-b'), case('match', 'matching-decompilation'), case('Pending-a'), tool('game-tool')]
        for language in ('en', 'zh'):
            with self.subTest(language=language):
                rendered = render_catalog(records, language)
                headings = re.findall(r'^##### (.+)$', rendered, re.MULTILINE)
                labels = METHOD_HEADINGS[UNASSIGNED_METHOD][language == 'zh']
                self.assertEqual(labels, 'Other reconstruction methods' if language == 'en' else '其他重建方式')
                self.assertEqual(headings, [METHOD_HEADINGS['matching-decompilation'][language == 'zh'] + ' (1)', labels + ' (2)'])
                self.assertIn(f'<a id="game-{UNASSIGNED_METHOD}"></a>\n##### {labels} (2)\n', rendered)
                self.assertEqual(re.findall(r'example\.com/([\w-]+)\)', rendered), ['match', 'Pending-a', 'pending-b', 'game-tool'])
                # The fallback heading is distinct from the `other` method's, and absent once every case has a method.
                self.assertNotEqual(labels, RECONSTRUCTION_METHODS['other'][language == 'zh'])
                complete = render_catalog([case('match', 'matching-decompilation'), case('misc', 'other'), tool('game-tool')], language)
                self.assertNotIn(labels, complete)
                self.assertNotIn(f'game-{UNASSIGNED_METHOD}', complete)
        self.assertEqual(case_method(case('pending')), UNASSIGNED_METHOD)
        # The group's slug is never a valid value.
        with self.assertRaisesRegex(ValueError, 'reconstruction_method'):
            case_method(case('slug', UNASSIGNED_METHOD))

    def test_validator_rejects_unknown_methods_and_only_warns_about_missing_ones(self):
        for record, expected in ((case('known', 'other'), None),
                                 (case('missing'), None),
                                 (case('unknown', 'guess'), 'use one of'),
                                 (case('slug', UNASSIGNED_METHOD), 'use one of'),
                                 (case('null', None) | {'reconstruction_method': None}, 'use one of'),
                                 (case('app-case', 'port', targets=['app']), 'only case studies listed under Game'),
                                 (tool('game-tool') | {'reconstruction_method': 'port'}, 'only case studies listed under Game')):
            with self.subTest(record=record['id']):
                errors = []
                validate_resources([record], errors)
                if expected:
                    self.assertEqual(len(errors), 1, errors)
                    self.assertIn('.reconstruction_method: ', errors[0])
                    self.assertIn(expected, errors[0])
                else:
                    self.assertEqual(errors, [])
        # A missing method is advisory: one warning names every Game case without one, and nothing else.
        records = [case('missing-b'), case('known', 'other'), case('missing-a'), case('app-case', targets=['app']), tool('game-tool')]
        self.assertEqual(missing_method_warnings(records), [
            '2 Game case studies have no reconstruction_method and are listed under "Other reconstruction methods": '
            'missing-b, missing-a; add one of the methods in data/README.md'])
        self.assertEqual(len(missing_method_warnings(records[:1])), 1)
        self.assertIn('1 Game case study has no reconstruction_method and is listed', missing_method_warnings(records[:1])[0])
        self.assertEqual(missing_method_warnings(records[1:2] + records[3:]), [])

    def test_a_catalog_game_case_without_a_method_is_a_warning_not_an_error(self):
        import validate
        records = load_resources()
        target = next(record for record in records if record['kind'] == 'case-study' and collection_section(record) == 'game')
        changed = [({key: value for key, value in record.items() if key != 'reconstruction_method'}
                    if record is target else record) for record in records]
        errors = []
        validate.validate_resources(changed, errors)
        self.assertEqual([error for error in errors if 'reconstruction_method' in error], [])
        self.assertEqual(len(missing_method_warnings(changed)), 1)
        self.assertIn(target['id'], missing_method_warnings(changed)[0])

    def test_each_game_case_appears_once_under_its_method_in_both_case_files(self):
        cases = [record for record in load_resources()
                 if record['kind'] == 'case-study' and collection_section(record) == 'game']
        self.assertTrue(cases)
        listed = {}
        for language in ('en', 'zh'):
            suffix = '.zh-CN.md' if language == 'zh' else '.md'
            paths = sorted(path for path in (ROOT / 'docs/cases').glob('game*.md')
                           if path.name.endswith(suffix) and (language == 'zh' or not path.name.endswith('.zh-CN.md')))
            text = '\n'.join(path.read_text(encoding='utf-8') for path in paths)
            order = re.findall(r'^- .*resources/([a-z0-9-]+)/\)</sub>$', text, re.MULTILINE)
            expected = [record['id'] for method, block in __import__('build_readme').method_groups(cases)
                        for record in block]
            self.assertEqual(order, expected)
            for method, block in __import__('build_readme').method_groups(cases):
                self.assertIn(f'<a id="game-{method}"></a>', text)
            listed[language] = order
        self.assertEqual(listed['en'], listed['zh'])

    def test_a_stale_order_or_count_is_rewritten(self):
        text = (ROOT / 'README.md').read_text(encoding='utf-8')
        records = load_resources()
        from validate_papers import read_papers
        paper_urls = {paper['url'] for paper in read_papers(ROOT)}
        current = replace_catalog(text, render_catalog(records, 'en', paper_urls))
        lines = current.split('\n')
        start = next(i for i, line in enumerate(lines) if line.startswith('- [**') and i > lines.index('<a id="game"></a>'))
        swapped = lines[:start] + [lines[start + 1], lines[start]] + lines[start + 2:]
        stale_count = current.replace('**By method:**', '**By method:** stale', 1)
        for stale in ('\n'.join(swapped), stale_count):
            self.assertNotEqual(stale, current)
            self.assertEqual(replace_catalog(stale, render_catalog(records, 'en', paper_urls)), current)
        self.assertIn(BEGIN, current)
        self.assertIn(END, current)


if __name__ == '__main__':
    unittest.main()
