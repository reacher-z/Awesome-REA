"""Shared Open Graph blocks, homepage ItemList names and site-wide security headers."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_browse_pages import build_browse_pages
from build_discovery_pages import build_discovery_pages
from build_entry_pages import build_entry_pages
from build_paper_pages import build_paper_pages
from build_survey import build_survey
from homepage_locales import HOMEPAGE_DESTINATIONS, _ui_strings
from open_graph import SOCIAL_CARD, SOCIAL_IMAGE_ALT, open_graph_meta, png_size
from test_source_browser import full_export
from validate_site import (Page, csp_directives, header_rules, validate_catalog_preload, validate_homepage_destinations,
                           validate_open_graph, validate_security_headers)

ORIGIN = 'https://awesomerea.org'
CARD = ORIGIN + '/social-card.png?v=0123456789abcdef'
APP = (ROOT / 'site/app.js').read_text(encoding='utf-8')


def resource():
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text())[0])
    record.update(name_zh='示例资源', requirements_zh=['测试前置条件'])
    return record


def social_page(route, **changes):
    language = 'zh' if route.startswith('/zh/') else 'en'
    block = open_graph_meta(language=language, title='Example page', description='Example description',
                            image_url=CARD, url=ORIGIN + route)
    for old, new in changes.items():
        block = block.replace(old, new)
    return Page(f'<html><head>{block}</head><body><h1>Example page</h1></body></html>')


class OpenGraphTests(unittest.TestCase):
    def test_block_reads_the_card_and_localizes_the_alt_text(self):
        self.assertEqual(png_size(SOCIAL_CARD), (1200, 630))
        for language, locales in (('en', ('en_US', 'zh_CN')), ('zh', ('zh_CN', 'en_US'))):
            page = Page(open_graph_meta(language=language, title='T', description='D', image_url=CARD, url=ORIGIN + '/x/'))
            self.assertEqual((page.meta['og:locale'], page.meta['og:locale:alternate']), locales)
            self.assertEqual((page.meta['og:image:type'], page.meta['og:image:width'], page.meta['og:image:height']), ('image/png', '1200', '630'))
            self.assertEqual(page.meta['og:image:alt'], SOCIAL_IMAGE_ALT[language])
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / 'card.png'
            fake.write_bytes(b'GIF89a' + bytes(30))
            with self.assertRaises(ValueError):
                open_graph_meta(language='en', title='T', description='D', image_url=CARD, url=None, card=fake)

    def test_every_generator_emits_the_shared_block(self):
        papers = json.loads((ROOT / 'data/papers.json').read_text())
        resources = (json.loads((ROOT / 'data/rea-resources.json').read_text())
                     + json.loads((ROOT / 'data/tool-resources.json').read_text()))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_browse_pages(output, full_export(), curated_count=1, site_url=ORIGIN,
                               repository_url='https://github.com/reacher-z/Awesome-REA', styles_href='/styles.css',
                               browse_styles_href='/browse.css', favicon_href='/favicon.svg',
                               social_image_href=CARD, data_revision='0' * 16)
            build_discovery_pages(output, {'resources': [resource()], 'meta': {}}, None)
            build_paper_pages(output, papers, social_image_href=CARD)
            build_entry_pages(output, [resource()], papers[:1], social_image_href=CARD)
            build_survey(output, papers, resources, social_image_href=CARD)
            routes = ['/browse/', '/zh/browse/android/', '/resources/', '/zh/about/', '/papers/', '/zh/papers/',
                      '/survey/', '/zh/survey/',
                      f'/resources/{resource()["id"]}/', f'/zh/papers/{papers[0]["id"]}/']
            for route in routes:
                with self.subTest(route=route):
                    page = Page((output / route.lstrip('/') / 'index.html').read_text())
                    # Discovery pages use their own revisioned asset path; the card URL path is what matters.
                    validate_open_graph(route, page, (1200, 630))
            not_found = Page((output / '404.html').read_text())
            validate_open_graph(None, not_found, (1200, 630))
            self.assertNotIn('og:url', not_found.meta)

    def test_validator_rejects_inconsistent_blocks(self):
        validate_open_graph('/papers/', social_page('/papers/'), (1200, 630))
        broken = {
            'title as alt': social_page('/papers/', **{SOCIAL_IMAGE_ALT['en']: 'Example page'}),
            'missing counterpart': social_page('/papers/', **{'<meta property="og:locale:alternate" content="zh_CN">': ''}),
            'wrong size': social_page('/papers/', **{'content="630"': 'content="600"'}),
            'wrong language alt': social_page('/zh/papers/', **{SOCIAL_IMAGE_ALT['zh']: SOCIAL_IMAGE_ALT['en']}),
        }
        for name, page in broken.items():
            with self.subTest(case=name), self.assertRaises(AssertionError):
                validate_open_graph('/zh/papers/' if 'language' in name else '/papers/', page, (1200, 630))
        with self.assertRaises(AssertionError):
            # The 404 template has no canonical URL to publish.
            validate_open_graph(None, social_page('/404.html'), (1200, 630))


class HomepageDestinationTests(unittest.TestCase):
    def pages(self, names):
        pages = {}
        for route, language in (('/', 'en'), ('/zh/', 'zh')):
            prefix = '/zh' if language == 'zh' else ''
            items = [{'@type': 'ListItem', 'position': index, 'name': names[language][path], 'url': f'{ORIGIN}{prefix}/{path}/'}
                     for index, path in enumerate(HOMEPAGE_DESTINATIONS, 1)]
            schema = {'@context': 'https://schema.org', '@graph': [{'@type': 'CollectionPage', 'mainEntity': {
                '@type': 'ItemList', 'numberOfItems': len(items), 'itemListElement': items}}]}
            pages[prefix + '/'] = Page(f'<script type="application/ld+json">{json.dumps(schema)}</script>')
            for path, labels in HOMEPAGE_DESTINATIONS.items():
                pages[f'{prefix}/{path}/'] = Page(f'<h1>{labels[language == "zh"]}<span class="title-dot" aria-hidden="true">.</span></h1>')
        return pages

    def test_names_must_match_destination_headings(self):
        names = {language: {path: labels[language == 'zh'] for path, labels in HOMEPAGE_DESTINATIONS.items()} for language in ('en', 'zh')}
        validate_homepage_destinations(self.pages(names), APP)
        ui = _ui_strings(APP)
        for language, path, name in (('en', 'browse', ui['en']['browseDirectory']), ('zh', 'papers', ui['zh']['directoryPapers']),
                                     ('en', 'about', 'About the collection and its sources ↗'), ('zh', 'resources', '精选资源')):
            changed = deepcopy(names)
            changed[language][path] = name
            with self.subTest(name=name), self.assertRaises(AssertionError):
                validate_homepage_destinations(self.pages(changed), APP)


class SecurityHeaderTests(unittest.TestCase):
    def test_site_rule_adds_security_headers_and_keeps_existing_rules(self):
        rules = header_rules((ROOT / 'site/_headers').read_text(encoding='utf-8'))
        site = rules.pop('/*')
        self.assertEqual(site['x-frame-options'], 'DENY')
        self.assertEqual(site['strict-transport-security'], 'max-age=2592000')
        directives = csp_directives(site['content-security-policy'])
        self.assertEqual(directives['script-src'], ["'self'", 'https://static.cloudflareinsights.com'])
        self.assertEqual(directives['connect-src'], ["'self'", 'https://cloudflareinsights.com'])
        self.assertEqual(directives['font-src'], ["'self'", 'https://awesome-rea.pages.dev'])
        no_cache = {'cache-control': 'no-cache, must-revalidate'}
        bibtex = {'content-type': 'application/x-bibtex; charset=utf-8'}
        self.assertEqual(rules, {
            '/fonts/*': {'access-control-allow-origin': '*'}, '/fontawesome.css': {'access-control-allow-origin': '*'},
            **{route: no_cache for route in ('/', '/index.html', '/catalog.json', '/catalog-index.json', '/source-index.json',
                                             '/source-browser.json', '/papers.json', '/build-manifest.json')},
            '/papers/references.bib': bibtex, '/papers/citations/*.bib': bibtex,
            **{host: {'x-robots-tag': 'noindex'} for host in ('https://:project.pages.dev/*',
                                                              'https://:version.:project.pages.dev/*')},
        })

    def check(self, html, headers=None):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / '_headers').write_text(headers or (ROOT / 'site/_headers').read_text(encoding='utf-8'), encoding='utf-8')
            (output / 'index.html').write_text(html, encoding='utf-8')
            validate_security_headers(output)

    def test_policy_covers_what_pages_load_and_rejects_new_inline_code(self):
        valid = ('<head><link rel="icon" href="/favicon.svg"><link rel="stylesheet" href="/styles.css?v=1">'
                 '<link rel="stylesheet" href="https://awesome-rea.pages.dev/fontawesome.css">'
                 '<link rel="preload" href="/catalog-index.json?v=1" as="fetch" crossorigin>'
                 '<script type="application/ld+json">{}</script><script src="/app.js?v=1" defer></script></head>'
                 '<body><script id="data" type="application/json">{}</script></body>')
        self.check(valid)
        headers = (ROOT / 'site/_headers').read_text(encoding='utf-8')
        failures = {
            'inline script': valid + '<script>alert(1)</script>',
            'event handler': valid + '<button onclick="go()">Go</button>',
            'style attribute': valid + '<p style="color:red">x</p>',
            'third-party script': valid + '<script src="https://cdn.example.org/widget.js"></script>',
            'unlisted icon origin': valid.replace('awesome-rea.pages.dev', 'icons.example.org'),
            'frame': valid + '<iframe src="/"></iframe>',
            'third-party preload': valid.replace('href="/catalog-index.json?v=1"', 'href="https://cdn.example.org/catalog-index.json"'),
            'untyped preload': valid.replace(' as="fetch"', ''),
        }
        for name, html in failures.items():
            with self.subTest(case=name), self.assertRaises(AssertionError):
                self.check(html)
        for name, changed in {'analytics removed': headers.replace(" https://static.cloudflareinsights.com", ''),
                              'preload': headers.replace('max-age=2592000', 'max-age=2592000; includeSubDomains; preload'),
                              'unsafe inline': headers.replace("script-src 'self'", "script-src 'self' 'unsafe-inline'"),
                              'framing allowed': headers.replace('X-Frame-Options: DENY', 'X-Frame-Options: SAMEORIGIN'),
                              'no policy': headers.replace('Content-Security-Policy:', 'X-Content-Security-Policy:'),
                              'pages.dev indexable': headers.replace('X-Robots-Tag: noindex', 'X-Robots-Tag: all'),
                              'preview indexable': headers.replace('https://:version.:project.pages.dev/*', '/preview/*'),
                              'canonical noindex': headers.replace('X-Frame-Options: DENY', 'X-Frame-Options: DENY\n  X-Robots-Tag: noindex')}.items():
            with self.subTest(case=name), self.assertRaises(AssertionError):
                self.check(valid, changed)
        # A staged rollout may use the Report-Only header with the same policy.
        self.check(valid, headers.replace('Content-Security-Policy:', 'Content-Security-Policy-Report-Only:'))


class CatalogPreloadTests(unittest.TestCase):
    REVISION = '0123456789abcdef'

    def check(self, english, chinese=None):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'zh').mkdir()
            for path, head in (('index.html', english), ('zh/index.html', english if chinese is None else chinese)):
                (output / path).write_text(f'<html data-catalog-revision="{self.REVISION}" lang="en"><head>{head}'
                                           '<script src="/app.js?v=1" defer></script></head><body></body></html>', encoding='utf-8')
            validate_catalog_preload(output)

    def test_preload_must_be_the_revision_stamped_catalog_fetch(self):
        valid = f'<link rel="preload" href="/catalog-index.json?v={self.REVISION}" as="fetch" crossorigin>'
        self.check(valid)
        self.check(valid.replace('crossorigin', 'crossorigin="anonymous"'))
        failures = {
            'missing': '',
            'stale revision': valid.replace(self.REVISION, 'fedcba9876543210'),
            'no CORS mode': valid.replace(' crossorigin', ''),
            'credentialed': valid.replace('crossorigin', 'crossorigin="use-credentials"'),
            'wrong destination': valid.replace('as="fetch"', 'as="script"'),
            'repository payload': valid + valid.replace('catalog-index.json', 'source-browser.json'),
            'complete catalog instead of the index': valid.replace('catalog-index.json', 'catalog.json'),
            'duplicate': valid + valid,
        }
        for name, head in failures.items():
            with self.subTest(case=name), self.assertRaises(AssertionError):
                self.check(head)
            with self.subTest(case=name + ' on /zh/'), self.assertRaises(AssertionError):
                self.check(valid, head)


if __name__ == '__main__':
    unittest.main()
