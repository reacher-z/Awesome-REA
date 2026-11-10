"""Markdown and JSON twins, alternate links and the full-catalog Markdown."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from agent_formats import (MARKDOWN, alternate_links, collection_markdown, full_catalog_markdown, link, paper_markdown,
                           paper_record, record_json_route, resource_markdown, resource_record)
from build_paper_pages import AUTHORS_OMITTED

ORIGIN = 'https://awesomerea.org'
RESOURCE = {
    'id': 'ghidra', 'name': 'Ghidra', 'name_zh': 'Ghidra', 'url': 'https://github.com/NationalSecurityAgency/ghidra',
    'kind': 'tool', 'category': 'native-analysis', 'relationship': 'foundation', 'targets': ['binary', 'firmware'],
    'group': 'tools', 'description_en': 'Open-source  software\nreverse engineering suite.', 'description_zh': '开源逆向工程套件。',
    'requirements': ['A JDK.', 'Release package.'], 'requirements_zh': ['需要 JDK。', '正式发行包。'],
    'requirement_facets': ['limits', 'prerequisites'],
    'evidence_url': 'https://github.com/NationalSecurityAgency/ghidra/blob/864999d/README.md',
    'additional_evidence_urls': ['https://ghidra-sre.org/', 'https://ghidra-sre.org/'],
    'added_at': '2026-10-16', 'verified_at': '2026-10-15', 'verification': 'source-reviewed',
    'private_note': 'never published',
}
PAPER = {
    'id': 'paper-x', 'title': 'A [Bracketed] Study', 'title_zh': '一项研究', 'authors': [], 'authors_omitted': True,
    'year': 2026, 'publication_date': '2026-10-08', 'date_precision': 'day', 'date_basis': 'arXiv v1',
    'date_basis_zh': 'arXiv v1', 'venue': 'arXiv', 'publication_status': 'preprint', 'arxiv_id': '2610.00001',
    'arxiv_version_reviewed': 'v1', 'first_arxiv_date': '2026-10-08', 'doi': None, 'url': 'https://arxiv.org/abs/2610.00001',
    'pdf_url': 'https://arxiv.org/pdf/2610.00001v1', 'code_url': None, 'project_url': None, 'targets': ['binary'],
    'kind': 'research', 'description_en': 'Studies decompilation.', 'description_zh': '研究反编译。',
    'scope_limitations_en': 'Only x86.', 'scope_limitations_zh': '仅 x86。', 'why_fits_en': 'Decompilation.',
    'why_fits_zh': '反编译。', 'metadata_notes': 'Preprint.', 'metadata_notes_zh': '预印本。',
    'evidence_urls': ['https://arxiv.org/abs/2610.00001'], 'added_at': '2026-10-20', 'verified_at': '2026-10-19',
    'verification': 'source-reviewed', 'runtime_tested': False,
}


class TwinTests(unittest.TestCase):
    def test_resource_markdown_keeps_recorded_facts_sources_and_prerequisites_first(self):
        text = resource_markdown(RESOURCE, 'en', site_url=ORIGIN)
        self.assertTrue(text.startswith('# Ghidra\n\n> Open-source software reverse engineering suite.\n'))
        self.assertIn('- Type: Tool\n', text)
        self.assertIn('- Sources reviewed: 2026-10-15\n', text)
        self.assertIn('- Added to the catalog: 2026-10-16\n', text)
        self.assertIn(f'- Catalog page: <{ORIGIN}/resources/ghidra/>\n', text)
        self.assertIn(f'- Record JSON: <{ORIGIN}/resources/ghidra/record.json>\n', text)
        self.assertIn(f'[简体中文]({ORIGIN}/zh/resources/ghidra/{MARKDOWN})', text)
        # Prerequisites move first; both items keep their facet label.
        self.assertLess(text.index('**Prerequisites:** Release package.'), text.index('**Limits:** A JDK.'))
        # Sources are numbered once each.
        self.assertEqual(text.count('<https://ghidra-sre.org/>'), 1)
        self.assertIn('1. <https://github.com/NationalSecurityAgency/ghidra/blob/864999d/README.md>\n2. <https://ghidra-sre.org/>', text)
        self.assertIn('The description was reviewed against primary sources.', text)
        self.assertNotIn('never published', text)

    def test_unavailable_source_is_a_source_status_fact_in_both_languages(self):
        self.assertNotIn('Source status', resource_markdown(RESOURCE, 'en', site_url=ORIGIN))
        gone = {**RESOURCE, 'source_unavailable': {'checked_at': '2026-11-09T17:20:00Z', 'outcome': 'not-found', 'http_status': 404}}
        self.assertIn('- Sources reviewed: 2026-10-15\n- Source status: Unavailable · HTTP 404 on 2026-11-09\n',
                      resource_markdown(gone, 'en', site_url=ORIGIN))
        self.assertIn('- 来源状态：无法访问 · 2026-11-09 返回 HTTP 404\n', resource_markdown(gone, 'zh', site_url=ORIGIN))
        self.assertEqual(resource_record(gone, ORIGIN)['source_unavailable'], gone['source_unavailable'])

    def test_chinese_twin_and_section_links(self):
        siblings = {'section': 'native-binary', 'siblings': [{'id': 'radare2', 'name': 'radare2', 'name_zh': 'radare2', 'kind': 'tool'}]}
        related = [('paper', PAPER)]
        text = resource_markdown(RESOURCE, 'zh', site_url=ORIGIN, siblings=siblings, related=related)
        self.assertTrue(text.startswith('# Ghidra\n\n> 开源逆向工程套件。\n'))
        self.assertIn('- 类型：工具\n', text)
        self.assertIn(f'[English]({ORIGIN}/resources/ghidra/{MARKDOWN})', text)
        self.assertIn(f'- [radare2]({ORIGIN}/zh/resources/radare2/{MARKDOWN}) · 工具', text)
        self.assertIn(f'- [一项研究]({ORIGIN}/zh/papers/paper-x/{MARKDOWN}) · 研究论文', text)

    def test_paper_twin_names_nobody_when_authors_are_omitted(self):
        for language, label in (('en', AUTHORS_OMITTED[0]), ('zh', AUTHORS_OMITTED[1])):
            text = paper_markdown(PAPER, language, site_url=ORIGIN)
            self.assertIn(f'[{label}](https://arxiv.org/abs/2610.00001)', text)
        named = paper_markdown({**PAPER, 'authors': ['A. Author', 'B. Author'], 'authors_omitted': None}, 'en', site_url=ORIGIN)
        self.assertIn('- Authors: A. Author; B. Author\n', named)
        self.assertIn(f'- BibTeX: <{ORIGIN}/papers/citations/paper-x.bib>', named)
        self.assertNotIn('- DOI:', named)

    def test_link_labels_escape_brackets(self):
        self.assertEqual(link('A [Bracketed] Study', 'https://x.test/'), r'[A \[Bracketed\] Study](https://x.test/)')

    def test_resource_prose_preserves_literal_placeholders_in_twins_and_full_catalog(self):
        for language, source, encoded in (
            ('en', 'Use baserom.<version>.z64, /proc/<pid> & <region>; *BSD* and `raw` [x].',
             r'Use baserom.&lt;version&gt;.z64, /proc/&lt;pid&gt; &amp; &lt;region&gt;; \*BSD\* and \`raw\` \[x\].'),
            ('zh', '使用 baserom.<version>.z64、/proc/<pid> & <region>；*BSD* 与 `raw` [x]。',
             r'使用 baserom.&lt;version&gt;.z64、/proc/&lt;pid&gt; &amp; &lt;region&gt;；\*BSD\* 与 \`raw\` \[x\]。'),
        ):
            with self.subTest(language=language):
                record = deepcopy(RESOURCE)
                record.update(name='<region> & *BSD*', name_zh='<region> & *BSD*')
                record['description_' + language] = source
                record['requirements_zh' if language == 'zh' else 'requirements'] = [source]
                record['requirement_facets'] = ['prerequisites']
                before = deepcopy(record)
                twin = resource_markdown(record, language, site_url=ORIGIN)
                full = full_catalog_markdown([record], [], language, site_url=ORIGIN,
                                             sections={'test': ('Test', '测试')}, section_of=lambda row: 'test',
                                             header='# Catalog\n')
                for output in (twin, full):
                    self.assertIn('# &lt;region&gt; &amp; \\*BSD\\*\n', output)
                    self.assertIn('> ' + encoded + '\n', output)
                    facet = '**前提条件：**' if language == 'zh' else '**Prerequisites:** '
                    self.assertIn('- ' + facet + encoded + '\n', output)
                    self.assertIn('1. <' + record['evidence_url'] + '>', output)
                    self.assertIn('<' + record['url'] + '>', output)
                    self.assertNotIn('<span>', output)
                self.assertEqual(record, before)
                self.assertEqual(resource_record(record, ORIGIN)['description_' + language], source)

    def test_paper_prose_preserves_literal_markup_without_changing_sources(self):
        source = '<region> &amp; *BSD* `raw` [x] \\file'
        encoded = r'&lt;region&gt; &amp;amp; \*BSD\* \`raw\` \[x\] \\file'
        for language in ('en', 'zh'):
            with self.subTest(language=language):
                paper = deepcopy(PAPER)
                paper.update(title=source, title_zh=source, venue=source, authors=[source], authors_omitted=False,
                             date_basis=source, date_basis_zh=source, metadata_notes=source, metadata_notes_zh=source)
                for field in ('description_', 'scope_limitations_', 'why_fits_'):
                    paper[field + language] = source
                before = deepcopy(paper)
                twin = paper_markdown(paper, language, site_url=ORIGIN)
                full = full_catalog_markdown([], [paper], language, site_url=ORIGIN, sections={},
                                             section_of=lambda row: None, header='# Catalog\n')
                for output in (twin, full):
                    self.assertIn('# ' + encoded + '\n', output)
                    self.assertIn('> ' + encoded + '\n', output)
                    self.assertEqual(output.count(encoded), 9 if language == 'zh' else 8)
                    self.assertIn('1. <' + paper['url'] + '>', output)
                    self.assertIn('<' + paper['pdf_url'] + '>', output)
                self.assertEqual(paper, before)

    def test_collection_prose_and_labels_are_literal_but_links_stay_links(self):
        source, encoded = '<pid> & *x* [y]', r'&lt;pid&gt; &amp; \*x\* \[y\]'
        for language in ('en', 'zh'):
            with self.subTest(language=language):
                output = collection_markdown(title=source, description=source, language=language,
                                             canonical=ORIGIN + '/resources/', notes=[source], items=[],
                                             groups=[(source, [{'name': source, 'url': 'https://example.org/approved',
                                                               'meta': source, 'description': source}])])
                self.assertIn('# ' + encoded + '\n', output)
                self.assertIn('> ' + encoded + '\n', output)
                self.assertIn('\n' + encoded + '\n', output)
                self.assertIn('## ' + encoded + '\n', output)
                self.assertIn('- [' + encoded + '](https://example.org/approved)', output)
                self.assertIn(encoded + ' · ' + encoded, output)
                self.assertIn('<' + ORIGIN + '/resources/>', output)

    def test_plain_prose_cannot_introduce_markdown_blocks(self):
        for source, encoded in (('# Heading', r'\# Heading'), ('1. List', r'1\. List'),
                                ('2) List', r'2\) List'), ('- List', r'\- List'), ('+ List', r'\+ List'),
                                ('---', r'\---'), ('===', r'\==='), ('> Quote', '&gt; Quote')):
            with self.subTest(source=source):
                output = paper_markdown({**PAPER, 'scope_limitations_en': source}, 'en', site_url=ORIGIN)
                self.assertIn('## Scope and limitations\n\n' + encoded + '\n', output)

    def test_json_twins_publish_only_recorded_fields_and_their_urls(self):
        value = resource_record(RESOURCE, ORIGIN)
        self.assertNotIn('private_note', value)
        self.assertEqual(value['json_url'], ORIGIN + '/resources/ghidra/record.json')
        self.assertEqual(value['markdown_url_zh'], ORIGIN + '/zh/resources/ghidra/index.md')
        self.assertEqual(value['record_type'], 'resource')
        paper = paper_record(PAPER, ORIGIN)
        self.assertEqual(paper['authors'], [])
        self.assertTrue(paper['authors_omitted'])
        self.assertEqual(paper['bibtex_url'], ORIGIN + '/papers/citations/paper-x.bib')
        self.assertEqual(record_json_route('paper', 'paper-x'), '/papers/paper-x/record.json')

    def test_alternate_links_have_no_hreflang(self):
        html = alternate_links(markdown='/resources/ghidra/index.md', json_href='/resources/ghidra/record.json')
        self.assertEqual(html, '<link rel="alternate" type="text/markdown" href="/resources/ghidra/index.md" title="Markdown">'
                               '<link rel="alternate" type="application/json" href="/resources/ghidra/record.json" title="JSON">')
        self.assertNotIn('hreflang', html)
        self.assertEqual(alternate_links(), '')

    def test_collection_and_full_catalog_markdown(self):
        listing = collection_markdown(title='Curated', description='All entries.', language='en', canonical=ORIGIN + '/resources/',
                                      items=[], groups=[('Native binaries (1)', [{'name': 'Ghidra', 'url': ORIGIN + '/resources/ghidra/index.md', 'meta': 'Tool', 'description': 'Suite.'}])],
                                      json_url=ORIGIN + '/api/v1/resources.json', counterpart=ORIGIN + '/zh/resources/index.md')
        self.assertIn('## Native binaries (1)\n\n- [Ghidra](https://awesomerea.org/resources/ghidra/index.md): Tool · Suite.\n', listing)
        self.assertIn('- JSON: <https://awesomerea.org/api/v1/resources.json>', listing)
        full = full_catalog_markdown([RESOURCE], [PAPER], 'en', site_url=ORIGIN, sections={'native-binary': ('Native binaries', '原生二进制')},
                                     section_of=lambda record: 'native-binary', header='# Full catalog\n\n> Everything.\n')
        self.assertTrue(full.startswith('# Full catalog\n\n> Everything.\n'))
        self.assertIn('### Native binaries (1)', full)
        self.assertIn('#### Ghidra\n', full)
        self.assertIn('### A \\[Bracketed\\] Study\n', full)
        self.assertIn(f'<{ORIGIN}/resources/ghidra/>', full)
        # The review note is stated once, not under every entry, and the twin links are left out.
        self.assertEqual(full.count('The description was reviewed against primary sources.'), 1)
        self.assertNotIn('record.json', full)


if __name__ == '__main__':
    unittest.main()
