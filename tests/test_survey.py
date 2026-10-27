"""Survey references follow visible order, frozen evidence and editorial identity."""
from copy import deepcopy
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

# Works in the ignored review location and after integration as tests/test_survey.py.
ROOT = next(path for path in Path(__file__).resolve().parents
            if (path / 'scripts/build_survey.py').is_file())
sys.path.insert(0, str(ROOT / 'scripts'))
from build_survey import build_survey, discussion_sections, reference_order, validate_survey
from build_paper_pages import bibtex_text

CATALOG_PAPERS = json.loads((ROOT / 'data/papers.json').read_text())
CATALOG_RESOURCES = (json.loads((ROOT / 'data/rea-resources.json').read_text())
                     + json.loads((ROOT / 'data/tool-resources.json').read_text()))
LOCALIZATIONS = json.loads((ROOT / 'site/translations.zh-CN.json').read_text())
P1, P2, CASE = 'paper-fuzzware', 'paper-ui2app', 'open-scrantic-screensaver-case'


def pair(en, zh):
    return {'en': en, 'zh': zh}


def fixture():
    papers = [deepcopy(next(row for row in CATALOG_PAPERS if row['id'] == identifier))
              for identifier in (P1, P2)]
    resource = deepcopy(next(row for row in CATALOG_RESOURCES if row['id'] == CASE))
    resource['name_zh'] = LOCALIZATIONS[CASE]['name']
    resource['requirements_zh'] = LOCALIZATIONS[CASE]['requirements']
    document = {
        'schema_version': 1, 'version': '1.0', 'date': '2026-10-18',
        'snapshot': {'revision': 'a' * 40, 'papers': 2, 'resources': 1,
                     'cases': 1, 'selected_cases': 1},
        'paper_ids': [P1, P2],
        'reference_records': deepcopy([*papers, resource]),
        'subtitle': pair('A bounded editorial synthesis.', '范围明确的编辑综述。'),
        'description': pair('Evidence before conclusions.', '先看证据，再作结论。'),
        'abstract': pair('Source review does not establish reproduction.', '来源审阅不代表运行复现。'),
        'disclosure': pair('Editorial synthesis; no new experiments.', '编辑性综合分析；无新实验。'),
        'reference_note': pair('References retain their source identities.', '参考条目保留来源身份。'),
        'figure_caption': pair('Observe, reconstruct, compare.', '观察、重建、比较。'),
        'findings': [pair('Checks constrain particular properties.', '检查约束特定性质。')],
        'pipeline': [{'title': pair('Observe', '观察'),
                      'text': pair('Record the available evidence.', '记录可用证据。')}],
        'sections': [
            {'id': 'methods', 'title': pair('Method', '方法'),
             'paragraphs': [pair('A literal <em>claim</em> & its limit.', '字面文本 <em>主张</em> 与边界。')],
             'table': 'cases',
             'bullets': [pair('Later prose [[' + P1 + ']].', '随后正文 [[' + P1 + ']]。')]},
            {'id': 'limits', 'title': pair('Limits', '边界'),
             'paragraphs': [pair('A separate section.', '单独的章节。')]},
        ],
        'tables': {'cases': {
            'caption': pair('Case evidence', '案例证据'),
            'headers': [pair('Case', '案例'), pair('Input', '输入'), pair('Check', '检查')],
            'rows': [{'reference': CASE,
                      'label': pair('Comparison [[' + P2 + ']]', '比较 [[' + P2 + ']]'),
                      'cells': [pair('Original files', '原始文件'),
                                pair('Finite checks', '有限检查')]}],
        }},
    }
    return document, papers, [resource]


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.attributes, self.links, self.ids, self.reference_ids, self.schemas = [], [], [], [], []
        self.anchor = None
        self.schema_text = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.attributes.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.anchor = {**attrs, 'text': ''}
            self.links.append(self.anchor)
        elif tag == 'link':
            self.links.append(attrs)
        if tag == 'li' and attrs.get('class') == 'survey-reference':
            self.reference_ids.append(attrs['data-survey-reference'])
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.schema_text = ''

    def handle_data(self, value):
        if self.anchor is not None:
            self.anchor['text'] += value
        if self.schema_text is not None:
            self.schema_text += value

    def handle_endtag(self, tag):
        if tag == 'a':
            self.anchor = None
        if tag == 'script' and self.schema_text is not None:
            self.schemas.append(json.loads(self.schema_text))
            self.schema_text = None


class SurveyTests(unittest.TestCase):
    def assert_rejected(self, document, papers, resources):
        with self.assertRaises((AssertionError, ValueError)):
            validate_survey(document, papers, resources)

    def render(self, document, papers, resources):
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            urls = build_survey(directory, papers, resources, document=document)
            files = {path.relative_to(directory).as_posix(): path.read_text()
                     for path in directory.rglob('*') if path.is_file()}
        return urls, files

    def test_discussion_sections_only_follow_numbered_prose_in_document_order(self):
        document, papers, resources = fixture()
        document['abstract'] = pair('Overview [[' + P2 + ']].', '概述 [[' + P2 + ']]。')
        document['findings'] = [pair('Finding [[' + CASE + ']].', '认识 [[' + CASE + ']]。')]
        document['sections'][0]['paragraphs'].append(
            pair('First [[' + P1 + ']] again [[' + P1 + ']].', '首先 [[' + P1 + ']] 再次 [[' + P1 + ']]。'))
        document['sections'][1]['paragraphs'] = [pair('Another view [[' + P1 + ']].', '另一视角 [[' + P1 + ']]。')]
        validate_survey(document, papers, resources)
        before = deepcopy(document)
        self.assertEqual(discussion_sections(document), {P1: [
            {'section': 'methods', 'title': pair('Method', '方法')},
            {'section': 'limits', 'title': pair('Limits', '边界')},
        ]})
        self.assertEqual(document, before)
        # P2 appears in abstract/table labels/bibliography and CASE in findings/
        # table rows; none of those is a numbered section-prose discussion.
        self.assertNotIn(P2, discussion_sections(document))
        self.assertNotIn(CASE, discussion_sections(document))

    def test_discussion_sections_reject_translation_citation_drift(self):
        document, _, _ = fixture()
        document['sections'][0]['bullets'][0]['zh'] = '遗漏引文。'
        with self.assertRaisesRegex(ValueError, 'matching bilingual citations'):
            discussion_sections(document)

    def test_citations_reject_malformed_unknown_and_outside_frozen_corpus(self):
        for token in ('[[paper-UI2app]]', '[[paper-ui2app]', 'paper-ui2app]]',
                      '[[]]', '[[paper-not-in-the-catalog]]', '[[paper-slade]]'):
            with self.subTest(token=token):
                document, papers, resources = fixture()
                papers.append(deepcopy(next(p for p in CATALOG_PAPERS if p['id'] == 'paper-slade')))
                document['sections'][0]['paragraphs'][0] = pair('Claim ' + token, '主张 ' + token)
                self.assert_rejected(document, papers, resources)

    def test_translation_cannot_change_citation_coverage(self):
        document, papers, resources = fixture()
        document['tables']['cases']['rows'][0]['label']['zh'] = '比较 [[' + P1 + ']]'
        self.assert_rejected(document, papers, resources)

    def test_noninteger_or_invalid_snapshot_counts_are_rejected(self):
        for key in ('papers', 'resources', 'cases', 'selected_cases'):
            valid_count = 2 if key == 'papers' else 1
            for value in (True, False, float(valid_count), str(valid_count), 0, -1):
                with self.subTest(key=key, value=value):
                    document, papers, resources = fixture()
                    document['snapshot'][key] = value
                    self.assert_rejected(document, papers, resources)

    def test_unsafe_reserved_and_colliding_section_ids_are_rejected(self):
        for identifier in ('', '../methods', 'Methods', 'methods" onclick="x',
                           'abstract', 'references', 'citation', 'survey-content',
                           'table-cases', 'heading-methods', 'ref-' + P1):
            with self.subTest(identifier=identifier):
                document, papers, resources = fixture()
                document['sections'][1]['id'] = identifier
                self.assert_rejected(document, papers, resources)
        document, papers, resources = fixture()
        document['sections'][1]['id'] = 'methods'
        self.assert_rejected(document, papers, resources)

    def test_unsafe_table_keys_and_repeated_table_rendering_are_rejected(self):
        for key in ('../extra', 'Extra', 'extra" onclick="x', ''):
            with self.subTest(key=key):
                document, papers, resources = fixture()
                document['tables'][key] = deepcopy(document['tables']['cases'])
                document['sections'][1]['table'] = key
                self.assert_rejected(document, papers, resources)
        document, papers, resources = fixture()
        document['sections'][1]['table'] = 'cases'
        self.assert_rejected(document, papers, resources)

    def test_frozen_reference_records_must_be_complete_and_unambiguous(self):
        for mutation in ('missing', 'duplicate', 'unknown'):
            with self.subTest(mutation=mutation):
                document, papers, resources = fixture()
                if mutation == 'missing':
                    document['reference_records'].pop()
                elif mutation == 'duplicate':
                    document['reference_records'].append(deepcopy(document['reference_records'][0]))
                else:
                    extra = deepcopy(document['reference_records'][0])
                    extra['id'] = 'paper-outside-the-frozen-corpus'
                    document['reference_records'].append(extra)
                self.assert_rejected(document, papers, resources)

    def test_unsafe_frozen_source_urls_are_rejected(self):
        for field, value, record_index in (
                ('url', 'javascript:alert(1)', 0),
                ('pdf_url', 'https://localhost/paper.pdf', 0),
                ('code_url', 'https://name:password@example.org/code', 0),
                ('evidence_url', 'http://example.org/evidence', 2)):
            with self.subTest(field=field, value=value):
                document, papers, resources = fixture()
                document['reference_records'][record_index][field] = value
                self.assert_rejected(document, papers, resources)

    def test_visible_order_includes_label_only_citation_then_table_then_bullets(self):
        document, papers, resources = fixture()
        order = [P2, CASE, P1]
        self.assertEqual(reference_order(document), order)
        before = deepcopy((document, papers, resources))
        _, files = self.render(document, papers, resources)
        for path in ('survey/index.html', 'zh/survey/index.html'):
            with self.subTest(path=path):
                page = Page(files[path])
                self.assertEqual(page.reference_ids, order)
                citations = [link for link in page.links if link.get('class') == 'survey-cite']
                self.assertEqual([link['href'] for link in citations], ['#ref-' + i for i in order])
                self.assertEqual([link['text'] for link in citations], ['[1]', '[2]', '[3]'])
                self.assertEqual(len(page.ids), len(set(page.ids)))
                self.assertLess(files[path].index('</table>'), files[path].index('cite-' + P1 + '-1'))
        self.assertEqual((document, papers, resources), before)

    def test_reference_links_escaping_backlinks_and_number_map_match_both_languages(self):
        document, papers, resources = fixture()
        frozen = {record['id']: record for record in document['reference_records']}
        frozen[P1]['title'] = 'Fuzzware <img src=x onerror=alert(1)> & evidence'
        frozen[P1]['title_zh'] = '固件 <script>alert(1)</script> 与证据'
        frozen[P1]['authors'] = ['An Author <b>literal</b> & Co.']
        frozen[CASE]['url'] = 'https://example.org/project?first=1&second=2'
        frozen[CASE]['evidence_url'] = 'https://github.com/example/project/blob/' + 'f' * 40 + '/README.md#L10-L20'
        document['sections'][1]['paragraphs'][0] = pair('Repeat [[' + P2 + ']].', '再次引用 [[' + P2 + ']]。')
        _, files = self.render(document, papers, resources)
        expected_sources = {record[key] for record in frozen.values()
                            for key in ('url', 'pdf_url', 'code_url', 'evidence_url') if record.get(key)}
        for language, path in (('en', 'survey/index.html'), ('zh', 'zh/survey/index.html')):
            with self.subTest(language=language):
                source, page = files[path], Page(files[path])
                self.assertTrue(expected_sources <= {link.get('href') for link in page.links})
                self.assertIn(escape(frozen[P1]['title_zh' if language == 'zh' else 'title']), source)
                self.assertIn(escape(frozen[P1]['authors'][0]), source)
                self.assertNotIn('<img src=x', source)
                self.assertNotIn('<script>alert(1)</script>', source)
                self.assertNotIn('<em>claim</em>', source)
                citations = [link for link in page.links if link.get('class') == 'survey-cite']
                backlinks = [link['href'][1:] for link in page.links if link.get('class') == 'survey-backlink']
                self.assertCountEqual(backlinks, [link['id'] for link in citations])
                numbers = {P2: '[1]', CASE: '[2]', P1: '[3]'}
                for link in citations:
                    self.assertEqual(link['text'], numbers[link['href'].removeprefix('#ref-')])
                self.assertEqual(sum(link['href'] == '#ref-' + P2 for link in citations), 2)

    def test_frozen_records_survive_live_metadata_changes_and_later_papers(self):
        document, papers, resources = fixture()
        expected_urls, expected_files = self.render(document, papers, resources)
        later_papers, later_resources = deepcopy(papers), deepcopy(resources)
        for record in later_papers:
            record.update(title='Later title', title_zh='后来的标题', authors=['Later author'],
                          venue='Later venue', url='https://example.org/later/' + record['id'])
        later_resources[0].update(name='Later project', name_zh='后来的项目',
                                  evidence_url='https://example.org/later-evidence')
        extra = deepcopy(papers[0])
        extra.update(id='paper-added-after-the-snapshot', title='Later paper', title_zh='后增论文')
        later_papers.append(extra)
        actual_urls, actual_files = self.render(document, later_papers, later_resources)
        self.assertEqual(actual_urls, expected_urls)
        self.assertEqual(actual_files, expected_files)

    def test_two_canonical_locales_and_bibtex_export_only_the_frozen_paper_subset(self):
        document, _, resources = fixture()
        # The fixture freezes two papers while the live catalog has a larger corpus.
        # Adding another live record must not silently enlarge the survey download.
        papers = deepcopy(CATALOG_PAPERS)
        extra = deepcopy(papers[0]); extra['id'] = 'paper-added-after-the-snapshot'
        papers.append(extra)
        urls, files = self.render(document, papers, resources)
        self.assertEqual(urls, ['https://awesomerea.org/survey/', 'https://awesomerea.org/zh/survey/'])
        self.assertEqual(set(files), {'survey/index.html', 'zh/survey/index.html',
                                     'survey/citation.bib', 'survey/references.bib'})
        for language, path, canonical in (('en', 'survey/index.html', urls[0]),
                                           ('zh-CN', 'zh/survey/index.html', urls[1])):
            page = Page(files[path])
            self.assertEqual([x['href'] for x in page.links if x.get('rel') == 'canonical'], [canonical])
            self.assertEqual({x['hreflang']: x['href'] for x in page.links if x.get('rel') == 'alternate'},
                             {'en': urls[0], 'zh-CN': urls[1], 'x-default': urls[0]})
            self.assertIn(('html', {'lang': language}), page.attributes)
        references = files['survey/references.bib']
        keys = re.findall(r'^@\w+\{([^,]+),', references, re.M)
        self.assertEqual(keys, [P2, P1])
        frozen = {r['id']: r for r in document['reference_records']}
        for identifier in (P1, P2):
            self.assertIn(bibtex_text(frozen[identifier]), references)
        self.assertNotIn(CASE, keys)
        self.assertNotIn(extra['id'], references)

    def test_repository_citation_matches_collection_metadata_without_survey_publication_fields(self):
        document, papers, resources = fixture()
        _, files = self.render(document, papers, resources)
        citation = files['survey/citation.bib']
        metadata = (ROOT / 'CITATION.cff').read_text(encoding='utf-8')
        title = re.search(r'^title: (.+)$', metadata, re.M)[1]
        repository = re.search(r'^repository-code: (.+)$', metadata, re.M)[1]
        author_block = re.search(r'^authors:\n(.*?)(?=^\S)', metadata, re.M | re.S)[1]
        authors = []
        for block in re.findall(r'^  - (.*?)(?=^  - |\Z)', author_block, re.M | re.S):
            fields = dict(re.findall(r'^\s*([a-z-]+): (.+)$', block, re.M))
            authors.append('{' + fields['name'] + '}' if 'name' in fields
                           else fields['family-names'] + ', ' + fields['given-names'])
        self.assertTrue(citation.startswith('@misc{awesome-rea,'))
        self.assertIn('author = {' + ' and '.join(authors) + '}', citation)
        self.assertIn('title = {{' + title + '}}', citation)
        self.assertIn('url = {' + repository + '}', citation)
        self.assertIn('howpublished = {GitHub repository}', citation)
        self.assertNotRegex(citation, r'(?m)^\s*(year|version|doi|journal|booktitle|issn)\s*=')
        self.assertNotIn('/survey/', citation)
        self.assertNotIn('Evidence-Centered Survey', citation)
        self.assertNotIn(papers[0]['authors'][0], citation)
        changed = deepcopy(document)
        changed.update(version='9.1', date='2031-01-02')
        _, later_files = self.render(changed, papers, resources)
        self.assertEqual(later_files['survey/citation.bib'], citation)
        self.assertEqual(later_files['survey/references.bib'], files['survey/references.bib'])

    def test_repository_citation_actions_and_legacy_download_are_localized(self):
        document, papers, resources = fixture()
        _, files = self.render(document, papers, resources)
        for path, label in [('survey/index.html', 'Cite the repository'),
                            ('zh/survey/index.html', '引用仓库')]:
            with self.subTest(path=path):
                page = Page(files[path])
                downloads = [link for link in page.links if link.get('href') == '/survey/citation.bib']
                self.assertEqual(len(downloads), 1)
                self.assertEqual(downloads[0]['download'], 'awesome-rea.bib')
                self.assertIn(label, downloads[0]['text'])
                # The desktop and mobile contents lists each link the citation section once.
                self.assertEqual(sum(link.get('href') == '#citation' and link['text'] == label
                                     for link in page.links), 2)
                self.assertEqual(sum(link.get('href') == '#citation' for link in page.links), 2)
                self.assertNotIn('Repository citation', files[path])
                self.assertNotIn('仓库引用信息', files[path])
                self.assertIn('id="citation"><h2>' + label + '</h2>', files[path])
                self.assertIn('https://github.com/reacher-z/Awesome-REA/blob/main/CITATION.cff',
                              {link.get('href') for link in page.links})
                self.assertNotIn('Cite this survey', files[path])
                self.assertNotIn('引用本综述', files[path])
                self.assertNotIn('download="awesome-rea-survey.bib"', files[path])

    def test_byline_parts_are_separate_items_without_inline_separators(self):
        document, papers, resources = fixture()
        _, files = self.render(document, papers, resources)
        for path, version, author in [('survey/index.html', 'Version', 'Awesome REA contributors'),
                                      ('zh/survey/index.html', '版本', 'Awesome REA 贡献者')]:
            with self.subTest(path=path):
                byline = re.search(r'<p class="survey-meta">(.*?)</p>', files[path])[1]
                # The dots are CSS-generated inside each item, so flex spacing is even on both sides.
                self.assertEqual(byline, f'<span>{version} {document["version"]}</span><span><time datetime="{document["date"]}">'
                                         f'{document["date"]}</time></span><span>{author}</span>')

    def test_survey_remains_an_editorial_article_not_a_scholarly_publication(self):
        document, papers, resources = fixture()
        _, files = self.render(document, papers, resources)
        for path in ('survey/index.html', 'zh/survey/index.html'):
            page = Page(files[path])
            graph = page.schemas[0]['@graph']
            self.assertEqual({item['@type'] for item in graph}, {'WebPage', 'Article'})
            article = next(item for item in graph if item['@type'] == 'Article')
            self.assertEqual(article['genre'], 'Editorial survey')
            self.assertEqual(article['author']['@type'], 'Organization')
            self.assertEqual(article['author']['name'], 'Awesome REA contributors')
            self.assertFalse({'doi', 'identifier', 'isPartOf', 'issn'} & article.keys())


if __name__ == '__main__':
    unittest.main()
