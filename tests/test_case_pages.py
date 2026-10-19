"""Case-directory generation keeps the curated subset readable and source-bound."""
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import build_discovery_pages


def resource(identifier, *, kind='case-study', targets=None, **changes):
    record = {
        'id': identifier, 'name': 'Case ' + identifier, 'name_zh': '案例 ' + identifier,
        'url': 'https://example.org/' + identifier,
        'description_en': 'A bounded reconstruction; original assets are still required.',
        'description_zh': '范围有限的重建；仍需原始素材。',
        'category': 'reconstruction-cases' if kind == 'case-study' else 'game-analysis',
        'relationship': 'independent-reconstruction' if kind == 'case-study' else 'foundation',
        'targets': targets or ['game'], 'kind': kind,
        'requirements': ['Provide your own source material.', 'Results are author-reported.'],
        'requirements_zh': ['自行提供原始材料。', '结果来自作者报告。'],
        'evidence_url': 'https://example.org/evidence/' + identifier,
        'additional_evidence_urls': ['https://example.org/method/' + identifier],
        'verified_at': '2026-10-17T01:02:03Z', 'verification': 'source-reviewed',
    }
    record.update(changes)
    return record


class CaseDocument(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.cases = []
        self.sections = []
        self.links = []
        self.styles = []
        self.tags = []
        self.canonical = []
        self.alternates = {}
        self.current = None
        self.disclosures = 0
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.tags.append(tag)
        if tag == 'section' and 'data-case-section' in values:
            self.sections.append(values['data-case-section'])
        if tag == 'article' and 'data-case-id' in values:
            self.current = {'id': values['data-case-id'], 'section': values['data-case-section'],
                            'text': [], 'links': [], 'times': [], 'description_outside_details': False}
            self.cases.append(self.current)
        if tag == 'details':
            self.disclosures += 1
            if self.current:
                assert 'open' not in values
        if tag == 'a':
            self.links.append(values.get('href'))
            if self.current:
                self.current['links'].append(values.get('href'))
        if self.current and tag == 'p' and values.get('class') == 'case-description':
            self.current['description_outside_details'] = self.disclosures == 0 and 'hidden' not in values
        if self.current and tag == 'time':
            self.current['times'].append(values.get('datetime'))
        if tag == 'link':
            if values.get('rel') == 'canonical':
                self.canonical.append(values['href'])
            if values.get('rel') == 'alternate':
                self.alternates[values['hreflang']] = values['href']
            if values.get('rel') == 'stylesheet':
                self.styles.append(values['href'])

    def handle_endtag(self, tag):
        if tag == 'details':
            self.disclosures -= 1
        if tag == 'article':
            self.current = None

    def handle_data(self, data):
        if self.current:
            self.current['text'].append(data)


def schema(content):
    return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.S)[1])


class CasePageTests(unittest.TestCase):
    def build(self, resources):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name)
        (output / 'index.html').write_text('<link rel="stylesheet" href="https://awesome-rea.pages.dev/fontawesome.css">')
        (output / 'cases.css').write_bytes((ROOT / 'site/cases.css').read_bytes())
        catalog = {'resources': resources, 'meta': {'site_url': 'https://awesomerea.org'}}
        original = deepcopy(catalog)
        paths = build_discovery_pages(output, catalog, None)
        self.assertEqual(catalog, original)
        self.assertEqual(set(paths), {'/resources/', '/zh/resources/', '/cases/', '/zh/cases/', '/about/', '/zh/about/'})
        return output

    def test_subset_grouping_localized_links_and_itemlist_order(self):
        game = resource('multi-game', targets=['binary', 'game'])
        web = resource('multi-web', targets=['game', 'website'])
        tool = resource('ordinary-tool', kind='tool')
        output = self.build([game, tool, web])
        for language, prefix in [('en', ''), ('zh', 'zh/')]:
            with self.subTest(language=language):
                content = (output / prefix / 'cases/index.html').read_text()
                page = CaseDocument(content)
                self.assertEqual(page.sections, ['website', 'game'])
                self.assertEqual([row['id'] for row in page.cases], ['multi-web', 'multi-game'])
                self.assertEqual([row['section'] for row in page.cases], ['website', 'game'])
                self.assertIn('data-case-count="2" data-curated-count="3"', content)
                self.assertNotIn('data-case-id="ordinary-tool"', content)
                structured = schema(content)
                self.assertEqual(structured['@type'], 'CollectionPage')
                self.assertEqual(structured['inLanguage'], 'en' if language == 'en' else 'zh-CN')
                items = structured['mainEntity']['itemListElement']
                self.assertEqual(structured['mainEntity']['numberOfItems'], 2)
                for index, (item, record, rendered) in enumerate(zip(items, [web, game], page.cases), 1):
                    self.assertEqual(item['position'], index)
                    self.assertEqual(item['url'], f'https://awesomerea.org/{prefix}resources/{record["id"]}/')
                    self.assertEqual(item['description'], record['description_' + language])
                    self.assertTrue(rendered['description_outside_details'])
                    self.assertIn(record['url'], rendered['links'])
                    self.assertIn(record['evidence_url'], rendered['links'])
                    self.assertIn(record['additional_evidence_urls'][0], rendered['links'])
                    self.assertEqual(rendered['times'], [record['verified_at']])
                self.assertIn('Binary · Game' if language == 'en' else '二进制 · 游戏', content)
                self.assertIn('Game · Website' if language == 'en' else '游戏 · 网站', content)
                self.assertIn('https://example.org/ordinary-tool', (output / prefix / 'resources/index.html').read_text())

    def test_literal_prose_evidence_and_native_disclosure_are_preserved(self):
        record = resource('quoted-case', name='Case <A> & "B"', name_zh='案例 <甲> 与 "乙"',
                          description_en='Literal <script>text()</script>, *scope* & limits.',
                          description_zh='字面 <script>文本()</script>、*范围* 与限制。',
                          requirements=['Keep <original> & "rights".'], requirements_zh=['保留 <原始> 与 "权利"。'])
        output = self.build([record])
        for language, prefix in [('en', ''), ('zh', 'zh/')]:
            content = (output / prefix / 'cases/index.html').read_text()
            page = CaseDocument(content)
            self.assertNotIn('img', page.tags)
            # Collection and breadcrumb JSON-LD only, never contributed markup.
            self.assertEqual(content.count('<script'), content.count('<script type="application/ld+json">'))
            self.assertEqual(page.tags.count('script'), 2)
            text = ''.join(page.cases[0]['text'])
            self.assertIn(record['name' if language == 'en' else 'name_zh'], text)
            self.assertIn(record['description_' + language], text)
            self.assertIn(record['requirements' if language == 'en' else 'requirements_zh'][0], text)
            self.assertIn('independent' if language == 'en' else '本合集', content)
            self.assertEqual(schema(content)['mainEntity']['itemListElement'][0]['description'], record['description_' + language])

    def test_shell_styles_empty_subset_and_navigation_are_bilingual(self):
        output = self.build([resource('tool', kind='tool')])
        css_hash = hashlib.sha256((ROOT / 'site/cases.css').read_bytes()).hexdigest()[:16]
        for language, prefix in [('en', ''), ('zh', 'zh/')]:
            content = (output / prefix / 'cases/index.html').read_text()
            page = CaseDocument(content)
            self.assertEqual(page.cases, [])
            self.assertEqual(page.canonical, [f'https://awesomerea.org/{prefix}cases/'])
            self.assertEqual(page.alternates, {'en': 'https://awesomerea.org/cases/',
                                             'zh-CN': 'https://awesomerea.org/zh/cases/',
                                             'x-default': 'https://awesomerea.org/cases/'})
            self.assertIn('https://awesome-rea.pages.dev/fontawesome.css', page.styles)
            self.assertIn('/cases.css?v=' + css_hash, page.styles)
            self.assertIn('class="shell browse-main cases-main"', content)
            self.assertIn('data-case-count="0" data-curated-count="1"', content)
            self.assertEqual(schema(content)['mainEntity']['numberOfItems'], 0)
            self.assertNotIn('cases-nav', content)
            self.assertIn(f'/{prefix}resources/', page.links)
            search = '/zh/?view=curated&kind=case-study#catalog' if language == 'zh' else '/?view=curated&kind=case-study&lang=en#catalog'
            self.assertIn(search, page.links)
            self.assertIn(f'/{prefix}cases/', CaseDocument((output / prefix / 'about/index.html').read_text()).links)
        llms = (output / 'llms.txt').read_text()
        self.assertIn('https://awesomerea.org/cases/', llms)
        self.assertIn('https://awesomerea.org/zh/cases/', llms)


if __name__ == '__main__':
    unittest.main()
