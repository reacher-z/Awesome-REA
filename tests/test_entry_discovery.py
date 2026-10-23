"""Reviewed detail pages retain evidence and remain discoverable in both languages."""
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_browse_pages import CATEGORIES
from build_discovery_pages import _resource_card, jsonld_script
from build_entry_pages import build_entry_pages
from build_paper_pages import paper_card
from validate_discovery import ORIGIN, expected_entry_routes, validate_route_inventory
from validate_site import Page, validate_entry_outputs


class EntryDiscoveryValidationTests(unittest.TestCase):
    def setUp(self):
        translations = json.loads((ROOT / 'site/translations.zh-CN.json').read_text())
        self.resources = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text())[:2])
        for record in self.resources:
            record['name_zh'] = record.get('name_zh') or translations[record['id']].get('name', record['name'])
            record['requirements_zh'] = record.get('requirements_zh') or translations[record['id']].get('requirements', record['requirements'])
        papers = json.loads((ROOT / 'data/papers.json').read_text())
        self.papers = [deepcopy(next(p for p in papers if p['id'] == identifier))
                       for identifier in ('paper-fuzzware', 'paper-ui2app')]
        self.papers[0].update(publication_date=None, date_precision='year')
        self.html = {}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.detail_urls = build_entry_pages(root, self.resources, self.papers)
            for route in expected_entry_routes(self.resources, self.papers):
                self.html[route] = (root / route.lstrip('/') / 'index.html').read_text()
        for language, prefix in (('en', ''), ('zh', '/zh')):
            self.html[f'{prefix}/resources/'] = '\n'.join(_resource_card(r, language) for r in self.resources)
            self.html[f'{prefix}/papers/'] = '\n'.join(paper_card(p, language, False) for p in self.papers)

    def validate(self, html=None):
        validate_entry_outputs({path: Page(text) for path, text in (html or self.html).items()}, self.resources, self.papers)

    def changed_schema(self, route, mutate):
        html = dict(self.html)
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html[route], re.S)
        schema = json.loads(match[1])
        mutate(schema['@graph'])
        html[route] = html[route][:match.start()] + jsonld_script(schema) + html[route][match.end():]
        return html

    def changed_article(self, route, mutate):
        html = dict(self.html)
        match = re.search(r'(<article\b[^>]*data-entry-kind=[^>]*>)(.*?)(</article>)', html[route], re.S)
        self.assertIsNotNone(match)
        html[route] = html[route][:match.start(2)] + mutate(match[2]) + html[route][match.end(2):]
        return html

    def test_complete_bilingual_details_and_ordinary_links(self):
        self.validate()
        self.assertEqual(len(self.detail_urls), 2 * (len(self.resources) + len(self.papers)))
        for prefix in ('', '/zh'):
            for directory, records in (('resources', self.resources), ('papers', self.papers)):
                page = Page(self.html[f'{prefix}/{directory}/'])
                for record in records:
                    self.assertIn(record['id'], page.ids)
                    self.assertIn(record['url'], page.links)
                    self.assertIn(f"{prefix}/{directory}/{record['id']}/", page.links)
                    link = next(link for link in page.detail_links if link['id'] == record['id'])
                    label = '完整条目' if prefix else 'Full entry'
                    title = ((record.get('name_zh') or record['name']) if prefix else record['name']) if directory == 'resources' else record['title_zh' if prefix else 'title']
                    self.assertEqual(''.join(link['text']), label)
                    self.assertEqual(link['aria_label'], label + ('：' if prefix else ': ') + title)

    def test_resource_disclosure_retains_primary_and_additional_evidence(self):
        for language in ('en', 'zh'):
            for original in self.resources:
                record = deepcopy(original)
                record['additional_evidence_urls'] = ['https://example.org/secondary-evidence']
                html = _resource_card(record, language)
                disclosure = re.search(r'<details class="requirements">(.*?)</details>', html, re.S)[1]
                self.assertIn('使用条件与来源' if language == 'zh' else 'Requirements & sources', disclosure)
                for url in (record['evidence_url'], *record['additional_evidence_urls']):
                    self.assertIn('href="' + escape(url, quote=True) + '"', disclosure)
                for requirement in record['requirements_zh' if language == 'zh' else 'requirements']:
                    self.assertIn(escape(requirement), disclosure)
                self.assertIn(record['verified_at'], disclosure)
                self.assertIn(escape(record['description_' + language]), html.split('<details', 1)[0])

    def test_sitemap_inventory_is_derived_and_rejects_missing_extra_duplicate_pages(self):
        base = [ORIGIN + prefix + path for prefix in ('', '/zh')
                for path in ('/', '/resources/', '/cases/', '/papers/', '/survey/', '/about/', '/benchmark-map/', '/browse/',
                             *(f'/browse/{category}/' for category in CATEGORIES))]
        urls = base + self.detail_urls
        validate_route_inventory(urls, self.resources, self.papers)
        for invalid in (urls[:-1], urls + [urls[-1]], urls + [ORIGIN + '/repositories/scan-123/'],
                        urls + [ORIGIN + '/resources/unknown/']):
            with self.assertRaises(AssertionError):
                validate_route_inventory(invalid, self.resources, self.papers)

    def test_unsafe_or_duplicate_detail_ids_are_rejected(self):
        for identifier in ('../other', 'name/part', 'scan?query', ''):
            with self.assertRaises(AssertionError):
                expected_entry_routes([{'id': identifier}], [])
        with self.assertRaises(AssertionError):
            expected_entry_routes([{'id': 'same'}, {'id': 'same'}], [])
        with self.assertRaises(AssertionError):
            expected_entry_routes([], [{'id': 'not-a-paper'}])

    def test_missing_or_misbound_detail_page_is_rejected(self):
        route = self.detail_urls[0].removeprefix(ORIGIN)
        missing = dict(self.html); missing.pop(route)
        with self.assertRaises(AssertionError): self.validate(missing)
        wrong = dict(self.html)
        wrong[route] = wrong[route].replace('data-entry-id="' + self.resources[0]['id'] + '"', 'data-entry-id="other"')
        with self.assertRaises(AssertionError): self.validate(wrong)

    def test_canonical_and_language_alternatives_are_bound_to_each_record(self):
        route = '/zh/resources/' + self.resources[0]['id'] + '/'
        for before, after in [('rel="canonical"', 'rel="not-canonical"'),
                              ('hreflang="en"', 'hreflang="fr"'), ('<html lang="zh-CN"', '<html lang="en"')]:
            broken = dict(self.html); broken[route] = broken[route].replace(before, after, 1)
            with self.assertRaises(AssertionError): self.validate(broken)

    def test_listing_links_keep_legacy_anchors_and_same_tab_localized_targets(self):
        identifier = self.resources[0]['id']; route = '/zh/resources/'
        for before, after in [(f'href="/zh/resources/{identifier}/"', f'href="/resources/{identifier}/"'),
                              (f'href="/zh/resources/{identifier}/"', f'target="_blank" href="/zh/resources/{identifier}/"'),
                              (f'id="{identifier}"', 'id="missing-anchor"')]:
            broken = dict(self.html); broken[route] = broken[route].replace(before, after, 1)
            with self.assertRaises(AssertionError): self.validate(broken)

    def test_upstream_listing_and_detail_sources_cannot_be_dropped(self):
        identifier = self.resources[0]['id']; evidence = escape(self.resources[0]['evidence_url'], quote=True)
        for route in ('/resources/', f'/resources/{identifier}/'):
            broken = dict(self.html); broken[route] = broken[route].replace('href="' + evidence + '"', 'href="https://example.com/other"')
            with self.assertRaises(AssertionError): self.validate(broken)

    def test_hidden_script_text_cannot_substitute_for_localized_requirements(self):
        identifier = self.resources[0]['id']; requirement = self.resources[0]['requirements_zh'][0]
        route = f'/zh/resources/{identifier}/'; broken = dict(self.html)
        broken[route] = broken[route].replace(escape(requirement), '') + '<script type="application/json">' + json.dumps(requirement, ensure_ascii=False) + '</script>'
        with self.assertRaises(AssertionError): self.validate(broken)

    def test_full_entry_link_label_and_accessible_title_are_required(self):
        for route in ('/resources/', '/zh/papers/'):
            for pattern, replacement in [(r'(class="[^\"]*entry-detail-link[^>]*>)([^<]+)', r'\1Details'),
                                         (r'aria-label="(?:Full entry:|完整条目：)[^\"]*"', 'aria-label="Full entry"')]:
                broken = dict(self.html)
                broken[route], count = re.subn(pattern, replacement, broken[route], count=1)
                self.assertEqual(count, 1)
                with self.assertRaises(AssertionError): self.validate(broken)

    def test_marked_article_requires_one_correctly_localized_h1(self):
        for route in ('/resources/' + self.resources[0]['id'] + '/', '/zh/papers/' + self.papers[1]['id'] + '/'):
            for replacement in ('', '<h1>Wrong title</h1>', r'\g<0>\g<0>'):
                broken = self.changed_article(route, lambda body: re.sub(r'<h1>.*?</h1>', replacement, body, count=1, flags=re.S))
                with self.assertRaises(AssertionError): self.validate(broken)

    def test_head_title_or_outside_article_text_cannot_replace_description(self):
        for directory, record in (('resources', self.resources[0]), ('papers', self.papers[1])):
            for language, prefix in (('en', ''), ('zh', '/zh')):
                route = f"{prefix}/{directory}/{record['id']}/"
                description = escape(record['description_' + language])
                missing = self.changed_article(route, lambda body: body.replace('<p class="entry-description">' + description + '</p>', ''))
                self.assertNotEqual(missing[route], self.html[route])
                for location in ('title', 'outside'):
                    broken = dict(missing)
                    if location == 'title':
                        broken[route] = broken[route].replace('</title>', ' ' + description + '</title>', 1)
                    else:
                        broken[route] = broken[route].replace('<article ', '<p>' + description + '</p><article ', 1)
                    with self.assertRaises(AssertionError): self.validate(broken)

    def test_review_time_is_inside_article_and_matches_full_source_value(self):
        for directory, record in (('resources', self.resources[0]), ('papers', self.papers[1])):
            for prefix in ('', '/zh'):
                route = f"{prefix}/{directory}/{record['id']}/"
                value, day = escape(record['verified_at'], quote=True), record['verified_at'][:10]
                original = f'<time datetime="{value}">{day}</time>'
                for replacement in (f'<span>{day}</span>', f'<time>{day}</time>',
                                    f'<time datetime="2000-01-01">{day}</time>',
                                    f'<time datetime="{value}">2000-01-01</time>'):
                    broken = self.changed_article(route, lambda body: body.replace(original, replacement))
                    self.assertNotEqual(broken[route], self.html[route])
                    with self.assertRaises(AssertionError): self.validate(broken)
                outside = self.changed_article(route, lambda body: body.replace(original, f'<span>{day}</span>'))
                outside[route] += original
                with self.assertRaises(AssertionError): self.validate(outside)

    def test_resource_schema_rejects_invented_authorship_license_or_publication(self):
        route = '/resources/' + self.resources[0]['id'] + '/'
        for field, value in [('author', {'@type': 'Person', 'name': 'Invented'}),
                             ('license', 'https://example.com/license'), ('datePublished', '2026-01-01')]:
            with self.assertRaises(AssertionError):
                self.validate(self.changed_schema(route, lambda graph: graph[-1].update({field: value})))

    def test_paper_schema_keeps_author_order_identifiers_and_date_precision(self):
        year_only = '/papers/paper-fuzzware/'
        with self.assertRaises(AssertionError):
            self.validate(self.changed_schema(year_only, lambda graph: graph[-1].update(datePublished='2020-01-01')))
        identified = '/papers/paper-ui2app/'
        for field, value in [('author', []), ('identifier', []), ('creativeWorkStatus', 'Conference paper')]:
            with self.assertRaises(AssertionError):
                self.validate(self.changed_schema(identified, lambda graph: graph[-1].update({field: value})))

    def test_webpage_and_breadcrumbs_cannot_point_to_other_entries(self):
        route = self.detail_urls[0].removeprefix(ORIGIN)
        for mutate in (lambda graph: graph[0].update(mainEntity={'@id': ORIGIN + '/resources/wrong/#resource'}),
                       lambda graph: graph[1]['itemListElement'][-1].update(item=ORIGIN + '/resources/wrong/')):
            with self.assertRaises(AssertionError): self.validate(self.changed_schema(route, mutate))


if __name__ == '__main__':
    unittest.main()
