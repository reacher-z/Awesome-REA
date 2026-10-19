"""Literal generated prose, checked against frozen GitHub GFM rendering evidence."""
from contextlib import ExitStack
from copy import deepcopy
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_repository_index
from build_readme import plain_text, render_catalog, render_papers
from validate import document_links

FIXTURE = ROOT / 'tests/fixtures/literal_markdown_gfm.json'


class RenderedFixtures(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.current = None
        self.depth = 0
        self.results = {}
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        identifier = attributes.get('id', '').removeprefix('user-content-')
        if tag == 'div' and identifier.startswith('fixture-'):
            self.current = identifier
            self.depth = 1
            self.results[identifier] = {'text': [], 'tags': [], 'links': [], 'spans': []}
        elif self.current:
            if tag == 'div':
                self.depth += 1
            result = self.results[self.current]
            result['tags'].append(tag)
            if tag == 'a':
                result['links'].append(attributes.get('href'))
            if tag == 'span':
                result['spans'].append(attributes)

    def handle_endtag(self, tag):
        if self.current and tag == 'div':
            self.depth -= 1
            if self.depth == 0:
                self.current = None

    def handle_data(self, data):
        if self.current:
            self.results[self.current]['text'].append(data)


class LiteralMarkdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))

    def test_generated_markdown_matches_real_gfm_rendering_fixtures(self):
        # No home-grown Markdown parser or network dependency in the build/tests.
        # Each exact Markdown input below was rendered by GitHub's API; the saved
        # response lets us enforce its literal text and intentional-link contract.
        parsed = RenderedFixtures(self.fixture['html'])
        self.assertEqual(self.fixture['renderer']['mode'], 'gfm')
        self.assertIsNone(self.fixture['renderer']['context'])
        self.assertEqual(hashlib.sha256(self.fixture['html'].encode()).hexdigest(), self.fixture['response_sha256'])
        self.assertEqual({case['context'] for case in self.fixture['cases']},
                         {'paragraph', 'bold-link-title', 'list-description'})
        self.assertEqual(set(parsed.results), {case['id'] for case in self.fixture['cases']})
        for case in self.fixture['cases']:
            with self.subTest(case=case['id']):
                encoded = plain_text(case['source'])
                self.assertEqual(encoded, case['encoded'])
                context = case['context']
                markdown = {
                    'paragraph': encoded,
                    'bold-link-title': '[**' + encoded + '**](https://example.org/approved)',
                    'list-description': '- [**Intentional title**](https://example.org/approved)\n\n  ' + encoded,
                }[context]
                self.assertEqual(markdown, case['markdown'])
                result = parsed.results[case['id']]
                self.assertEqual(' '.join(''.join(result['text']).split()), case['expected_text'])
                self.assertEqual(result['links'], case['expected_hrefs'])
                allowed = {'p', 'span'}
                if context != 'paragraph':
                    allowed.update({'a', 'strong'})
                if context == 'list-description':
                    allowed.update({'ul', 'li'})
                self.assertLessEqual(set(result['tags']), allowed)
                self.assertEqual(result['tags'].count('strong'), int(context != 'paragraph'))
                self.assertTrue(all(attributes == {} for attributes in result['spans']))

    def test_curated_and_paper_renderers_preserve_bilingual_prose_and_urls(self):
        cases = [case for case in self.fixture['cases'] if case['context'] == 'paragraph']
        resource = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text())[0])
        resource.update(id='literal-fixture', category='web-analysis', kind='tool', relationship='foundation',
                        targets=['website'], url='https://example.org/approved')
        paper = deepcopy(json.loads((ROOT / 'data/papers.json').read_text())[0])
        paper.update(id='paper-literal-fixture', targets=['website'], url='https://example.org/paper',
                     pdf_url='https://example.org/paper.pdf', code_url='https://example.org/code')
        for case in cases:
            for language in ('en', 'zh'):
                with self.subTest(case=case['id'], language=language):
                    source, encoded = case['source'], case['encoded']
                    resource.update(name=source, name_zh=source)
                    resource['description_' + language] = source
                    paper['title_zh' if language == 'zh' else 'title'] = source
                    paper['description_' + language] = source
                    paper['scope_limitations_' + language] = source
                    before = deepcopy((resource, paper))
                    catalog = render_catalog([resource], language)
                    bibliography = render_papers([paper], language)
                    self.assertIn('- [**' + encoded + '**](https://example.org/approved)', catalog)
                    self.assertIn('\n\n  ' + encoded + '\n', catalog)
                    self.assertIn('- [**' + encoded + '**](https://example.org/paper)', bibliography)
                    self.assertIn('\n\n  ' + encoded + '\n', bibliography)
                    scope_label = '范围与限制' if language == 'zh' else 'Scope and limits'
                    self.assertIn('**' + scope_label + ':** ' + encoded, bibliography)
                    for url in (paper['pdf_url'], paper['code_url']):
                        self.assertIn('](' + url + ')', bibliography)
                    prefix = 'zh/' if language == 'zh' else ''
                    self.assertIn('](https://awesomerea.org/' + prefix + 'resources/literal-fixture/)', catalog)
                    self.assertIn('](https://awesomerea.org/' + prefix + 'papers/paper-literal-fixture/)', bibliography)
                    self.assertEqual((resource, paper), before)

    def test_literal_source_links_do_not_become_validation_destinations(self):
        for source in ('[frida.re](https://www.frida.re)', '[说明](https://example.org/path)',
                       '![image](https://example.org/image.png)'):
            with self.subTest(source=source):
                rendered = '- [**Tool**](https://example.org/approved) — ' + plain_text(source)
                self.assertEqual(list(document_links(rendered)), [('https://example.org/approved', 1)])

    def test_repository_renderer_uses_literal_labels_and_descriptions_without_mutation(self):
        cases = [case for case in self.fixture['cases'] if case['context'] == 'paragraph']
        records = [{'id':f'fixture-{index}', 'full_name':case['source'], 'url':f'https://example.org/{index}',
                    'description_en':case['source'], 'description_zh':case['source'],
                    'category':'native-analysis', 'stars':None}
                   for index, case in enumerate(cases)]
        before = deepcopy(records)
        with TemporaryDirectory() as temporary, ExitStack() as stack:
            root = Path(temporary)
            (root / 'data').mkdir()
            (root / 'data/source-index.json').write_text(json.dumps({'meta':{'completed_at':'2026-10-17T00:00:00Z'}, 'resources':records}))
            (root / 'data/papers.json').write_text('[]')
            for name in ('README.md', 'README.zh-CN.md'):
                (root / name).write_text(build_repository_index.SUMMARY_BEGIN + '\n' + build_repository_index.SUMMARY_END)
            stack.enter_context(patch.object(build_repository_index, 'ROOT', root))
            stack.enter_context(patch.object(build_repository_index, 'read_localizations', return_value={}))
            stack.enter_context(patch.object(build_repository_index, 'localized_records', side_effect=lambda values, _: values))
            stack.enter_context(patch.object(build_repository_index, 'read_scope', return_value=[]))
            stack.enter_context(patch.object(build_repository_index, 'apply_scope', side_effect=lambda values, _: values))
            stack.enter_context(patch.object(build_repository_index, 'curated_resources', return_value=[]))
            stack.enter_context(patch.object(build_repository_index, 'with_curated_labels', side_effect=lambda values, _: values))
            rendered, count = build_repository_index.rendered_files()
            self.assertEqual(count, len(records))
            for case, record in zip(cases, records):
                expected = '- [' + case['encoded'] + '](' + record['url'] + ') — ' + case['encoded']
                for name in ('native-analysis.md', 'native-analysis.zh-CN.md'):
                    self.assertIn(expected + '\n', rendered[name])
            self.assertEqual(records, before)
            self.assertEqual(json.loads((root / 'data/source-index.json').read_text())['resources'], before)


if __name__ == '__main__':
    unittest.main()
