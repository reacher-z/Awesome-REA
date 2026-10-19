"""Detail pages preserve reviewed evidence, localization and safe public identities."""
from copy import deepcopy
from html import unescape
from html.parser import HTMLParser
import json
from urllib.parse import parse_qs, urlsplit
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_entry_pages import MARKER, build_entry_pages, entry_path, feedback_urls
from build_survey import build_survey, discussion_sections


def resource(**changes):
    item = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text())[0])
    item.update(id='example-resource', name='Example resource', name_zh='示例资源',
                requirements=['Original input is required; reproduction is not established.'],
                requirements_zh=['需要原始输入；尚未证实运行复现。'])
    item.update(changes)
    return item


def paper(identifier='paper-fuzzware', **changes):
    item = deepcopy(next(p for p in json.loads((ROOT / 'data/papers.json').read_text()) if p['id'] == identifier))
    item.update(changes)
    return item


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.attributes = []
        self.schema = None
        self.script = False
        self.script_count = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.attributes.append((tag, attrs))
        if tag in {'a', 'link'}:
            self.links.append(attrs)
        if tag == 'script':
            self.script_count += 1
            self.script = attrs.get('type') == 'application/ld+json'

    def handle_data(self, text):
        if self.script:
            self.schema = json.loads(text)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.script = False


class EntryPageTests(unittest.TestCase):
    def test_survey_discussion_links_are_localized_and_point_to_rendered_sections(self):
        from test_survey import fixture, pair, P1, P2, CASE
        document, papers, resources = fixture()
        document['sections'][1]['paragraphs'] = [
            pair('A documented case [[' + CASE + ']].', '有文档支持的案例 [[' + CASE + ']]。')]
        before = deepcopy(document)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_survey(root, papers, resources, document=document)
            build_entry_pages(root, resources, papers, survey_discussions=discussion_sections(document))
            for language, prefix in [('en', ''), ('zh', '/zh')]:
                for kind, identifier, section, title in [
                    ('paper', P1, 'methods', 'Method' if language == 'en' else '方法'),
                    ('resource', CASE, 'limits', 'Limits' if language == 'en' else '边界'),
                ]:
                    text = (root / entry_path(kind, identifier, language).lstrip('/') / 'index.html').read_text()
                    page = Page(text)
                    href = f'{prefix}/survey/#{section}'
                    self.assertEqual(sum(link.get('href') == href for link in page.links), 1)
                    self.assertIn('>' + title + '</a>', text)
                    self.assertLess(text.index('id="entry-survey"'), text.index('id="entry-sources"'))
                    survey = (root / prefix.lstrip('/') / 'survey/index.html').read_text()
                    self.assertIn('id="' + section + '"', survey)
                unmentioned = (root / entry_path('paper', P2, language).lstrip('/') / 'index.html').read_text()
                self.assertNotIn('entry-survey', unmentioned)
                self.assertNotIn('/survey/#', unmentioned)
        self.assertEqual(document, before)

    def test_survey_discussion_titles_are_escaped_and_unsafe_anchors_fail_before_writes(self):
        p = paper()
        title = '<img src=x onerror=alert(1)> & evidence'
        sections = {p['id']: [{'section': 'methods', 'title': {'en': title, 'zh': '方法与证据'}}]}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_entry_pages(root, [], [p], survey_discussions=sections)
            text = (root / entry_path('paper', p['id']).lstrip('/') / 'index.html').read_text()
            self.assertNotIn('<img src=x', text)
            self.assertIn('&lt;img src=x onerror=alert(1)&gt; &amp; evidence', text)
        sections[p['id']][0]['section'] = 'methods" onclick="bad'
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, 'safe section IDs'):
                build_entry_pages(root, [], [p], survey_discussions=sections)
            self.assertEqual(list(root.iterdir()), [])

    def test_correction_and_translation_forms_are_prefilled_from_id_and_name(self):
        r = resource(name='R&D "tool" #1 / 100%')
        p = paper()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_entry_pages(root, [r], [p])
            for language, labels in (('en', ['Report an outdated entry', 'Suggest a translation fix']),
                                     ('zh', ['报告条目过时', '建议修正翻译'])):
                for kind, record, name in (('resource', r, r['name']), ('paper', p, p['title'])):
                    text = (root / entry_path(kind, record['id'], language).lstrip('/') / 'index.html').read_text()
                    links = [link for link in Page(text).links if '/issues/new?' in link.get('href', '')]
                    self.assertEqual([link['href'] for link in links], feedback_urls(kind, record))
                    self.assertTrue(all(link['target'] == '_blank' and 'noopener' in link['rel'] for link in links))
                    for link, template, prefix, label in zip(links, ('broken-resource.yml', 'translation.yml'), ('Correction', 'Translation'), labels):
                        url = urlsplit(link['href'])
                        self.assertEqual((url.scheme, url.netloc, url.path), ('https', 'github.com', '/reacher-z/Awesome-REA/issues/new'))
                        self.assertNotIn(' ', url.query)
                        self.assertEqual(parse_qs(url.query), {'template': [template], 'title': [f'{prefix}: {name}'], 'resource': [record['id']]})
                        self.assertIn(label + ' <span aria-hidden="true">↗</span></a>', text)
                    # Both links sit in the entry's review section, before the source list.
                    self.assertLess(text.index('class="entry-feedback"'), text.index('id="entry-sources"'))
                    self.assertGreater(text.index('class="entry-feedback"'), text.index('id="entry-review"' if kind == 'resource' else 'id="entry-citation"'))

    def test_full_bilingual_evidence_and_canonical_identity(self):
        r, p = resource(), paper()
        before = deepcopy((r, p))
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            urls = build_entry_pages(root, [r], [p])
            self.assertEqual(len(urls), 4)
            for language, locale in [('en', 'en'), ('zh', 'zh-CN')]:
                for kind, record in [('resource', r), ('paper', p)]:
                    path = entry_path(kind, record['id'], language)
                    text = (root / path.lstrip('/') / 'index.html').read_text()
                    page = Page(text)
                    self.assertIn(record[f'description_{language}'], unescape(text))
                    self.assertIn(('article', {'class': 'entry-article', 'data-entry-kind': kind, 'data-entry-id': record['id']}), page.attributes)
                    canonical = 'https://awesomerea.org' + path
                    self.assertEqual([x['href'] for x in page.links if x.get('rel') == 'canonical'], [canonical])
                    alternates = {x['hreflang']: x['href'] for x in page.links if x.get('rel') == 'alternate'}
                    self.assertEqual(alternates, {'en': 'https://awesomerea.org' + entry_path(kind, record['id']),
                                                'zh-CN': 'https://awesomerea.org' + entry_path(kind, record['id'], 'zh'),
                                                'x-default': 'https://awesomerea.org' + entry_path(kind, record['id'])})
                    graph = {x['@type']: x for x in page.schema['@graph']}
                    self.assertEqual(graph['WebPage']['inLanguage'], locale)
                    self.assertEqual(graph['WebPage']['url'], canonical)
                    self.assertEqual(graph['BreadcrumbList']['itemListElement'][-1]['item'], canonical)
                    entity = graph['CreativeWork' if kind == 'resource' else 'ScholarlyArticle']
                    self.assertEqual(entity['@id'], canonical + ('#resource' if kind == 'resource' else '#paper'))
                    self.assertEqual(entity['url'], record['url'])
                    self.assertNotIn('dateModified', graph['WebPage'])
                    if kind == 'resource':
                        for requirement in r['requirements_zh' if language == 'zh' else 'requirements']:
                            self.assertIn(requirement, unescape(text))
                        self.assertFalse({'author', 'datePublished', 'license', 'aggregateRating'} & entity.keys())
                    else:
                        for field in ['scope_limitations_' + language, 'why_fits_' + language, 'metadata_notes_zh' if language == 'zh' else 'metadata_notes']:
                            self.assertIn(p[field], unescape(text))
                        self.assertIn('/papers/citations/' + p['id'] + '.bib', text)
                        self.assertEqual([x['name'] for x in entity['author']], p['authors'])
                        self.assertNotIn('identifier', entity)  # Published USENIX paper has no invented DOI/arXiv.
            self.assertEqual((r, p), before)

    def test_acceptance_date_is_not_invented_and_markup_is_escaped(self):
        hostile = '</script><script>alert("bad")</script>'
        r = resource(name='A & B ' + hostile, description_zh='原始说明 ' + hostile)
        p = paper('paper-programbench', title='Research ' + hostile)
        self.assertIsNone(p['publication_date'])
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_entry_pages(root, [r], [p], icon_stylesheet_href='https://awesomerea.org/fontawesome.css')
            for kind, record in [('resource', r), ('paper', p)]:
                text = (root / entry_path(kind, record['id']).lstrip('/') / 'index.html').read_text()
                page = Page(text)
                self.assertEqual(page.script_count, 1)
                self.assertNotIn(hostile, text)
                self.assertIn('data-icon-set="fontawesome"', text)
                for entity in page.schema['@graph']:
                    self.assertNotIn('datePublished', entity)
            zh = (root / entry_path('resource', r['id'], 'zh').lstrip('/') / 'index.html').read_text()
            self.assertIn('原始说明', zh)

    def test_invalid_paths_urls_and_automated_records_fail_before_writes(self):
        bad_records = [resource(id='../escape'), resource(id='bad%2fpath'),
                       resource(url='https://user:secret@example.org/project'),
                       resource(evidence_url='https://127.0.0.1/source'),
                       resource(verification='automated-readme-scan'), resource(requirements_zh=[])]
        for record in bad_records:
            with self.subTest(record=record['id']), TemporaryDirectory() as tmp:
                with self.assertRaises(ValueError):
                    build_entry_pages(Path(tmp), [record], [])
                self.assertEqual(list(Path(tmp).iterdir()), [])
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                build_entry_pages(Path(tmp), [resource(), resource()], [])
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_rebuild_removes_only_owned_stale_detail_pages(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            r, p = resource(), paper()
            build_entry_pages(root, [r], [p])
            for name, body in [('resources/index.html', 'resource listing'), ('papers/index.html', 'paper listing'),
                               ('papers/citations/example.bib', 'citation'), ('resources/unowned/index.html', 'unowned page')]:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body)
            before = (root / entry_path('paper', p['id']).lstrip('/') / 'index.html').read_bytes()
            build_entry_pages(root, [], [p])
            self.assertFalse((root / entry_path('resource', r['id']).lstrip('/')).exists())
            self.assertFalse((root / entry_path('resource', r['id'], 'zh').lstrip('/')).exists())
            self.assertEqual((root / entry_path('paper', p['id']).lstrip('/') / 'index.html').read_bytes(), before)
            self.assertEqual((root / 'resources/index.html').read_text(), 'resource listing')
            self.assertEqual((root / 'papers/index.html').read_text(), 'paper listing')
            self.assertEqual((root / 'papers/citations/example.bib').read_text(), 'citation')
            self.assertEqual((root / 'resources/unowned/index.html').read_text(), 'unowned page')

    def test_output_symlinks_cannot_redirect_generated_pages(self):
        with TemporaryDirectory() as tmp, TemporaryDirectory() as outside:
            root = Path(tmp)
            (root / 'zh').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                build_entry_pages(root, [resource()], [])
            self.assertEqual(list(Path(outside).iterdir()), [])
            self.assertFalse((root / 'resources').exists())


if __name__ == '__main__':
    unittest.main()
