"""The shared chrome: every page gets it once, without network, clock or inline styles, and old links still work."""
from __future__ import annotations

from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from build_home import COPY, FEATURED, KIND_CODES, _featured_projects, evidence_label, search_index  # noqa: E402
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
