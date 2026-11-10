"""The shared chrome: every page gets it once, without network, clock or inline styles, and old links still work."""
from __future__ import annotations

from html import unescape
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from build_home import COPY, FEATURED, KIND_CODES, _featured_projects, evidence_label, render_homepage, search_index  # noqa: E402
from homepage_locales import _Document, localized_homepage  # noqa: E402
from open_graph import SITE_ALTERNATE_NAMES, SITE_NAME, website_node  # noqa: E402
from page_metadata import description_problem, title_problem  # noqa: E402
from site_footer import site_footer  # noqa: E402
import site_shell  # noqa: E402

REPOSITORY = 'https://github.com/reacher-z/Awesome-REA'
LEGACY_PAGE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Example</title>
</head>
<body><header class="site-header"><div class="shell header-inner"><a class="brand" href="/">Old</a><a href="/zh/x/" hreflang="zh-CN" data-language-link="zh">中文</a></div></header>
<main><a href="/?view=curated&amp;target=game">Games</a><a href="/zh/?view=curated">中文</a></main>
</body>
</html>
'''


class ShellTests(unittest.TestCase):
    def shelled(self, source: str = LEGACY_PAGE) -> str:
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / 'assets').mkdir()
            for name in ('shell', 'site'):
                suffix = 'css' if name == 'shell' else 'js'
                (site / f'{name}.{suffix}').write_text('/* */', encoding='utf-8')
            (site / 'page').mkdir()
            (site / 'page/index.html').write_text(source, encoding='utf-8')
            self.assertEqual(site_shell.apply_site_shell(site, repository_url=REPOSITORY), 1)
            return (site / 'page/index.html').read_text(encoding='utf-8')

    def test_replaces_the_old_header_and_keeps_the_language_link_attributes(self):
        html = self.shelled()
        self.assertNotIn('header-inner', html)
        self.assertEqual(html.count('<header class="site-header"'), 1)
        self.assertIn('href="/zh/x/"', html)
        self.assertIn('data-language-link="zh"', html)

    def test_marks_the_page_and_loads_the_theme_before_first_paint(self):
        html = self.shelled()
        self.assertRegex(html, r'<html lang="en"[^>]*data-site="rea"')
        self.assertLess(html.index(site_shell.THEME_SCRIPT), html.index('<title>'))
        self.assertEqual(html.count(site_shell.THEME_SCRIPT), 1)

    def test_collection_filter_links_open_the_explorer(self):
        html = self.shelled()
        self.assertIn('href="/explore/?view=curated&amp;target=game"', html)
        self.assertIn('href="/zh/explore/?view=curated"', html)

    def test_page_without_the_old_header_is_left_alone(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / 'shell.css').write_text('', encoding='utf-8')
            (site / 'site.js').write_text('', encoding='utf-8')
            (site / 'plain.html').write_text('<!doctype html><title>Verification</title>', encoding='utf-8')
            self.assertEqual(site_shell.apply_site_shell(site, repository_url=REPOSITORY), 0)

    def test_generated_chrome_uses_no_inline_styles_or_icon_font(self):
        for language in ('en', 'zh'):
            chrome = (site_shell.header(language, '', '', REPOSITORY) + site_shell.mobile_bar(language)
                      + site_shell.palette(language) + site_shell.sprite()
                      + site_footer(language, note='', repository_url=REPOSITORY))
            self.assertNotIn('style=', chrome)
            self.assertNotRegex(chrome, r'\bfa-[a-z]')

    def test_csp_allows_the_theme_script_by_hash(self):
        headers = (ROOT / 'site/_headers').read_text(encoding='utf-8')
        self.assertIn(site_shell.theme_script_hash(), headers)
        self.assertNotIn('awesome-rea.pages.dev', headers)

    def test_star_count_is_compact_so_small_changes_keep_every_page_identical(self):
        self.assertEqual(site_shell.compact_count(1032), '1.0k')
        self.assertEqual(site_shell.compact_count(1049), '1.0k')
        self.assertEqual(site_shell.compact_count(950), '950')

    def test_star_action_is_on_every_header_and_the_phone_bar_in_both_languages(self):
        for language, label in (('en', 'Star on GitHub'), ('zh', '在 GitHub 上加星')):
            for chrome in (site_shell.header(language, '', '', REPOSITORY), site_shell.mobile_bar(language, REPOSITORY)):
                self.assertIn('class="star-btn', chrome)
                self.assertIn(f'href="{REPOSITORY}"', chrome)
                self.assertIn(f'<span class="star-long">{label}</span><span class="star-short">Star</span>', chrome)
                self.assertIn('data-stars="reacher-z/Awesome-REA"', chrome)

    def test_footer_stars_the_sister_catalogue_in_both_languages(self):
        for language in ('en', 'zh'):
            footer = site_footer(language, note='', repository_url=REPOSITORY)
            self.assertIn('href="https://github.com/reacher-z/Awesome-CUA"', footer)
            self.assertIn('data-stars="reacher-z/Awesome-CUA"', footer)

    def test_homepage_features_each_repository_with_websitebench_first(self):
        for language in ('en', 'zh'):
            html = _featured_projects(language)
            order = [html.index(f'https://github.com/{repository}"') for repository in ('TIGER-AI-Lab/WebsiteBench', 'TIGER-AI-Lab/ClawBench', 'reacher-z/Awesome-CUA')]
            self.assertEqual(order, sorted(order))

    def test_footer_fills_the_last_scan_at_runtime_and_stays_byte_stable(self):
        footer = site_footer('en', note='', repository_url=REPOSITORY)
        self.assertIn('data-last-scan', footer)
        self.assertEqual(footer, site_footer('en', note='', repository_url=REPOSITORY))
        self.assertNotRegex(footer, r'datetime="\d')


class HomeTests(unittest.TestCase):
    def test_homepage_definition_matches_readme_and_preserves_discovery_metadata(self):
        origin = 'https://awesomerea.org'
        template = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        app = (ROOT / 'site/app.js').read_text(encoding='utf-8')
        identity = 'Awesome REA (Awesome Reverse Engineering Anything)'
        for language, readme, canonical in (('en', 'README.md', origin + '/'),
                                            ('zh', 'README.zh-CN.md', origin + '/zh/')):
            with self.subTest(language=language), tempfile.TemporaryDirectory() as directory:
                explorer = localized_homepage(template, app, language)
                html = render_homepage(site_dir=Path(directory), explorer_html=explorer, resources=[], papers=[],
                                       discovery_count=0, last_scan=None, language=language, repository_url=REPOSITORY,
                                       repository_export='source-index.json', order={})
                document = _Document(html)
                ledes = [node for node in document.nodes if node['tag'] == 'p' and node['attrs'].get('class') == 'lede']
                self.assertEqual(len(ledes), 1)
                lede = ledes[0]
                prose = html[lede['inner']:lede['close']]
                self.assertTrue(prose.startswith(identity), prose)
                self.assertEqual(prose, (ROOT / readme).read_text(encoding='utf-8').split('\n\n', 2)[1])
                self.assertEqual(lede['parent']['attrs'].get('class'), 'hero-top')
                self.assertEqual(lede['attrs'], {'class': 'lede'})
                self.assertNotIn('<', prose)
                headings = [node for node in document.nodes if node['tag'] == 'h1']
                self.assertEqual(len(headings), 1)
                self.assertEqual(html[headings[0]['inner']:headings[0]['close']], COPY[language]['h1'])
                links = [node['attrs'] for node in document.nodes if node['tag'] == 'link']
                self.assertEqual([link['href'] for link in links if link.get('rel') == 'canonical'], [canonical])
                self.assertEqual({link['hreflang']: link['href'] for link in links if link.get('hreflang')},
                                 {'en': origin + '/', 'zh-CN': origin + '/zh/', 'x-default': origin + '/'})
                meta = {node['attrs'].get('name') or node['attrs'].get('property'): node['attrs'].get('content')
                        for node in document.nodes if node['tag'] == 'meta'}
                title_node = next(node for node in document.nodes if node['tag'] == 'title')
                self.assertIsNone(title_problem(unescape(html[title_node['inner']:title_node['close']])))
                self.assertIsNone(description_problem(meta['description']))
                self.assertEqual(meta['og:site_name'], SITE_NAME)
                self.assertEqual(meta['og:url'], canonical)
                self.assertEqual(meta['description'], meta['og:description'])
                self.assertEqual(meta['description'], meta['twitter:description'])
                self.assertIn(SITE_NAME, prose)
                self.assertIn('Awesome REA', SITE_ALTERNATE_NAMES)
                self.assertEqual(website_node(origin, REPOSITORY)['sameAs'], REPOSITORY)
                self.assertIn(f'href="{REPOSITORY}"', html)
                self.assertIn('href="/zh/about/"' if language == 'zh' else 'href="/about/"', html)

    def test_evidence_label_reads_a_pinned_commit(self):
        label = evidence_label('https://github.com/NationalSecurityAgency/ghidra/blob/' + 'a' * 40 + '/README.md')
        self.assertEqual(label['repo'], 'NationalSecurityAgency/ghidra')
        self.assertEqual(label['sha'], 'a' * 7)

    def test_evidence_label_names_a_host_outside_github(self):
        self.assertEqual(evidence_label('https://www.example.org/docs/')['repo'], 'example.org/docs')

    def test_every_language_has_the_same_copy_keys(self):
        self.assertEqual(set(COPY['en']), set(COPY['zh']))

    def test_search_index_has_no_clock_and_codes_every_kind(self):
        index = search_index([], [], 'en', {})
        self.assertNotIn('generated_at', index)
        self.assertEqual(index['kinds'], list(KIND_CODES))

    def test_featured_records_exist_in_the_catalog(self):
        import json
        known = {record['id'] for name in ('rea-resources.json', 'tool-resources.json')
                 for record in json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))}
        self.assertLess(len(set(FEATURED) - known), 3)

    def test_no_page_template_carries_an_inline_style(self):
        for name in ('build_home.py', 'home_art.py', 'site_shell.py'):
            source = (ROOT / 'scripts' / name).read_text(encoding='utf-8')
            self.assertIsNone(re.search(r'\sstyle="', source), name)


if __name__ == '__main__':
    unittest.main()
