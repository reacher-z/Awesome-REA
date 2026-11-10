"""Resource pages: copy-as-Markdown, record JSON, citation, repository facts and the star line."""
from copy import deepcopy
from html import unescape
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_entry_pages import build_entry_pages, entry_path, resource_citation  # noqa: E402
import repository_metadata  # noqa: E402
from repository_metadata import repository_facts, repository_key  # noqa: E402


def resource(**changes):
    item = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text())[0])
    item.update(id='example-resource', name='Example & {resource}_1', name_zh='示例资源', url='https://github.com/example/tool',
                requirements=['A host.'], requirements_zh=['一台主机。'])
    item.update(changes)
    return item


def snapshot(directory, repositories):
    path = Path(directory) / 'repository-metadata.json'
    path.write_text(json.dumps({'observed_at': '2026-11-09T20:00:00Z', 'repositories': repositories}), encoding='utf-8')
    return path


class RepositoryMetadataTests(unittest.TestCase):
    def test_only_repository_roots_have_keys(self):
        self.assertEqual(repository_key('https://github.com/NationalSecurityAgency/ghidra'), 'nationalsecurityagency/ghidra')
        self.assertEqual(repository_key('https://github.com/a/b.git'), 'a/b')
        for url in ('https://github.com/a/b/tree/main', 'https://gitlab.com/a/b', 'http://github.com/a/b', ''):
            self.assertIsNone(repository_key(url))

    def test_malformed_facts_are_dropped_and_a_missing_file_yields_nothing(self):
        with TemporaryDirectory() as tmp:
            path = snapshot(tmp, {'example/tool': {'stars': -1, 'committed_at': 'yesterday', 'language': '<b>',
                                                   'license': 'NOASSERTION', 'archived': 'yes'},
                                  'example/good': {'stars': 1234, 'language': 'C++', 'license': 'Apache-2.0'}})
            self.assertEqual(repository_facts({'url': 'https://github.com/example/tool'}, path), {})
            self.assertEqual(repository_facts({'url': 'https://github.com/Example/Good'}, path),
                             {'stars': 1234, 'language': 'C++', 'license': 'Apache-2.0', 'observed_at': '2026-11-09T20:00:00Z'})
            self.assertEqual(repository_facts({'url': 'https://github.com/example/good'}, Path(tmp) / 'missing.json'), {})


class ResourcePageToolTests(unittest.TestCase):
    def render(self, record, repositories=None):
        with TemporaryDirectory() as tmp:
            path = snapshot(tmp, repositories or {})
            facts = lambda item: repository_metadata.repository_facts(item, path)
            with mock.patch('build_entry_pages.repository_facts', facts):
                build_entry_pages(Path(tmp), [record], [])
            return {language: (Path(tmp) / entry_path('resource', record['id'], language).lstrip('/') / 'index.html').read_text()
                    for language in ('en', 'zh')}

    def test_tools_link_the_markdown_twin_and_record_json_in_both_languages(self):
        pages = self.render(resource())
        for language, (copy, view) in {'en': ('Copy as Markdown', 'View JSON'), 'zh': ('复制为 Markdown', '查看 JSON')}.items():
            tools = re.search(r'<div class="entry-tools">.*?</div>', pages[language])[0]
            self.assertIn(f'href="index.md" type="text/markdown" data-copy-url', tools)
            self.assertIn(copy, tools)
            self.assertIn(f'href="/resources/example-resource/record.json" type="application/json">{view}</a>', tools)
            self.assertIn('href="#cite"', tools)

    def test_citation_comes_from_record_fields_and_escapes_bibtex(self):
        record = resource(verified_at='2026-10-17T01:02:03Z')
        bibtex, plain = resource_citation(record, 'https://awesomerea.org/resources/example-resource/')
        self.assertTrue(bibtex.startswith('@misc{example-resource,\n'))
        self.assertIn(r'title = {{Example \& \{resource\}\_1}}', bibtex)
        self.assertIn('url = {https://github.com/example/tool}', bibtex)
        self.assertIn('urldate = {2026-10-17}', bibtex)
        self.assertNotIn('author', bibtex)
        self.assertEqual(plain, 'Example & {resource}_1. https://github.com/example/tool (accessed 2026-10-17). '
                                'Awesome REA entry: https://awesomerea.org/resources/example-resource/')
        pages = self.render(resource(name='DAILA', verified_at='2026-10-17T01:02:03Z'))
        self.assertIn('title = &#123;{DAILA}}', pages['en'])
        pages = self.render(record)
        for language in ('en', 'zh'):
            cite = pages[language][pages[language].index('id="cite"'):]
            cite = cite[:cite.index('</section>')]
            self.assertEqual(cite.count('data-copy="#cite-'), 2)
            self.assertNotRegex(cite, r'\{\{[A-Z_]+\}\}')
            self.assertIn(re.sub(r'\s+', ' ', bibtex.split('\n')[1].strip()), unescape(cite))
        self.assertIn('（访问于 2026-10-17）', unescape(pages['zh']))

    def test_one_star_line_after_the_citation_and_before_about(self):
        pages = self.render(resource())
        for language, text in {'en': 'Useful? Star Awesome REA on GitHub', 'zh': '有帮助？在 GitHub 上为 Awesome REA 加星'}.items():
            page = pages[language]
            self.assertEqual(page.count('class="entry-star"'), 1)
            self.assertIn(text, page)
            self.assertLess(page.index('id="cite"'), page.index('class="entry-star"'))
            self.assertLess(page.index('class="entry-star"'), page.index('id="entry-review"'))
            self.assertNotIn('noreferrer', page)

    def test_repository_row_shows_dated_facts_only_when_the_snapshot_has_them(self):
        facts = {'example/tool': {'stars': 61234, 'committed_at': '2026-11-01T10:00:00Z', 'language': 'Java', 'license': 'Apache-2.0'}}
        pages = self.render(resource(), facts)
        row = re.search(r'<div class="entry-repo".*?</p></div>', pages['en'])[0]
        self.assertEqual(re.findall(r'<dt>([^<]+)</dt>', row), ['Stars', 'Last commit', 'Language', 'License (GitHub)'])
        self.assertIn('61.2k', row)
        self.assertIn('<dd>2026-11-01</dd>', row)
        self.assertIn('GitHub data as of 2026-11-09', row)
        self.assertEqual(pages['en'].count('<time '), 1)
        self.assertIn('许可（GitHub 识别）', pages['zh'])
        self.assertNotIn('entry-repo', self.render(resource())['en'])


if __name__ == '__main__':
    unittest.main()
