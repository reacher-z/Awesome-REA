"""The first-resource walkthrough quotes its example record exactly and describes outputs the builders really produce."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import collection_section

EXAMPLE = 'r2frida'
GUIDES = {'en': ROOT / 'docs/first-resource.md', 'zh': ROOT / 'docs/first-resource.zh-CN.md'}


def code_blocks(text, language):
    return re.findall(r'^```' + language + r'\n(.*?)^```$', text, re.MULTILINE | re.DOTALL)


def catalog_records():
    return [record for name in ('rea-resources.json', 'tool-resources.json')
            for record in json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))]


class WalkthroughTests(unittest.TestCase):
    def test_both_languages_quote_the_example_record_and_translation_exactly(self):
        records = catalog_records()
        self.assertEqual([record['id'] for record in records].count(EXAMPLE), 1)
        record = next(record for record in records if record['id'] == EXAMPLE)
        translation = json.loads((ROOT / 'site/translations.zh-CN.json').read_text(encoding='utf-8'))[EXAMPLE]
        self.assertEqual(len(translation['requirements']), len(record['requirements']))
        self.assertRegex(record['evidence_url'], r'/blob/[0-9a-f]{40}/')
        for language, path in GUIDES.items():
            with self.subTest(language=language):
                blocks = code_blocks(path.read_text(encoding='utf-8'), 'json')
                self.assertEqual(len(blocks), 2)
                self.assertEqual(json.loads(blocks[0]), record)
                self.assertEqual(json.loads('{' + blocks[1] + '}'), {EXAMPLE: translation})

    def test_both_languages_run_the_same_existing_commands(self):
        commands = [code_blocks(path.read_text(encoding='utf-8'), 'sh') for path in GUIDES.values()]
        self.assertEqual(commands[0], commands[1])
        for script in set(re.findall(r'scripts/([a-z_]+\.py)', ''.join(commands[0]))):
            self.assertTrue((ROOT / 'scripts' / script).is_file(), script)
        self.assertNotIn('fontawesome-dir', ''.join(commands[0]))

    def test_the_output_table_matches_what_the_generators_wrote(self):
        record = next(record for record in catalog_records() if record['id'] == EXAMPLE)
        self.assertEqual(collection_section(record), 'native-binary')
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        entry = readme[readme.index(f'- [**{record["name"]}**]({record["url"]})'):]
        self.assertIn(f'Tool · Also: App · [Requirements & evidence](https://awesomerea.org/resources/{EXAMPLE}/)',
                      entry.split('\n- ', 1)[0])
        self.assertLess(readme.index('<a id="native-binary"></a>'), readme.index(f'(https://awesomerea.org/resources/{EXAMPLE}/)'))
        for page, label in (('dynamic-analysis.md', 'Curated'), ('dynamic-analysis.zh-CN.md', '精选')):
            text = (ROOT / 'docs/repositories' / page).read_text(encoding='utf-8')
            line = next(line for line in text.splitlines() if line.startswith(f'- [nowsecure/r2frida]({record["url"]})'))
            self.assertIn(f'{label}：' if label == '精选' else f'{label}: ', line)

    def test_the_walkthrough_is_linked_from_both_contribution_guides_and_indexes(self):
        for path, target in (('CONTRIBUTING.md', 'docs/first-resource.md'), ('CONTRIBUTING.zh-CN.md', 'docs/first-resource.zh-CN.md')):
            self.assertIn(f']({target})', (ROOT / path).read_text(encoding='utf-8'))
        for index in ('docs/README.md', 'docs/README.zh-CN.md'):
            text = (ROOT / index).read_text(encoding='utf-8')
            self.assertIn('](first-resource.md)', text)
            self.assertIn('](first-resource.zh-CN.md)', text)
        self.assertIn('](first-resource.zh-CN.md)', GUIDES['en'].read_text(encoding='utf-8'))
        self.assertIn('](first-resource.md)', GUIDES['zh'].read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
