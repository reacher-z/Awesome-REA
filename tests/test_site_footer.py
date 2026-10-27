"""Every page renders the same footer links, and each site-wide download keeps one name per language."""
from copy import deepcopy
import json
from pathlib import Path
import re
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
from homepage_locales import _ui_strings, localized_homepage
from site_footer import SECTION_LINKS, download_label, footer_downloads, site_footer
from test_source_browser import full_export
from validate_site import FooterLinks, validate_shared_footer

ORIGIN = 'https://awesomerea.org'
REPOSITORY = 'https://github.com/reacher-z/Awesome-REA'
APP = (ROOT / 'site/app.js').read_text(encoding='utf-8')


def resource():
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text())[0])
    record.update(name_zh='示例资源', requirements_zh=['测试前置条件'])
    return record


class SharedFooterTests(unittest.TestCase):
    def build(self, output):
        papers = json.loads((ROOT / 'data/papers.json').read_text())
        resources = (json.loads((ROOT / 'data/rea-resources.json').read_text())
                     + json.loads((ROOT / 'data/tool-resources.json').read_text()))
        build_browse_pages(output, full_export(), curated_count=1, site_url=ORIGIN, repository_url=REPOSITORY,
                           styles_href='/styles.css', browse_styles_href='/browse.css', favicon_href='/favicon.svg',
                           social_image_href=ORIGIN + '/social-card.png', data_revision='0' * 16)
        build_discovery_pages(output, {'resources': [resource()], 'meta': {}}, None)
        build_paper_pages(output, papers)
        build_entry_pages(output, [resource()], papers[:1])
        build_survey(output, papers, resources)

    def test_every_generated_page_type_renders_the_shared_footer(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            self.build(output)
            validate_shared_footer(output, REPOSITORY, 'source-index.json')
            for route in ('browse/', 'zh/browse/android/', 'resources/', 'zh/cases/', 'about/', 'zh/papers/',
                          'survey/', 'zh/survey/', f'resources/{resource()["id"]}/', '404.html'):
                with self.subTest(route=route):
                    path = output / route if route.endswith('.html') else output / route / 'index.html'
                    page = FooterLinks(path.read_text(encoding='utf-8'))
                    zh = route.startswith('zh/')
                    self.assertEqual([text for _, text in page.footer][:6],
                                     [chinese if zh else english for _, english, chinese in SECTION_LINKS])
                    self.assertIn(('/zh' if zh else '') + '/survey/', [href for href, _ in page.footer])

    def test_validator_rejects_a_changed_footer_or_a_second_download_name(self):
        for route, pattern, replacement in (
                ('about/index.html', r'(<footer[^>]*>.*?)>Editorial survey<', r'\1>Survey<'),
                ('zh/papers/index.html', r'<a href="/zh/survey/">专题综述</a>', ''),
                # A hero button that renames the repository download, as /browse/ once did.
                ('browse/index.html', r'(class="browse-download"[^>]*>)Repository index JSON ↓', r'\1Download full JSON ↓')):
            with self.subTest(route=route), tempfile.TemporaryDirectory() as directory:
                output = Path(directory)
                self.build(output)
                page = output / route
                text = page.read_text(encoding='utf-8')
                changed = re.sub(pattern, replacement, text, count=1, flags=re.S)
                self.assertNotEqual(changed, text)
                page.write_text(changed, encoding='utf-8')
                with self.assertRaises(AssertionError):
                    validate_shared_footer(output, REPOSITORY, 'source-index.json')

    def test_footer_uses_one_label_per_download_in_both_languages(self):
        for export in ('source-index.json', 'source-published.json'):
            for language in ('en', 'zh'):
                footer = FooterLinks(site_footer(language, note='', repository_url=REPOSITORY, repository_export=export))
                self.assertEqual([href for href, _ in footer.downloads], list(footer_downloads(export)))
                self.assertEqual([text for _, text in footer.downloads],
                                 [download_label(path, language) for path in footer_downloads(export)])
        with self.assertRaises(ValueError):
            site_footer('en', note='', repository_url=REPOSITORY, repository_export='../private.json')

    def test_homepage_footer_template_matches_the_shared_footer_in_both_languages(self):
        strings = _ui_strings(APP)
        template = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        for language in ('en', 'zh'):
            html = localized_homepage(template, APP, language)
            page = FooterLinks(html)
            prefix = '/zh' if language == 'zh' else ''
            shared = [prefix + path for path, _, _ in SECTION_LINKS] + list(footer_downloads('source-index.json')) + [REPOSITORY]
            self.assertEqual([href for href, _ in page.footer][:len(shared)], shared)
            names = [text for _, text in page.footer][:len(shared)]
            self.assertEqual(names[:6], [chinese if language == 'zh' else english for _, english, chinese in SECTION_LINKS])
            self.assertEqual(names[6:10], [download_label(path, language) for path in footer_downloads('source-index.json')])
            # app.js relabels the repository link for a published selection with the shared name.
            self.assertEqual(strings[language]['downloadPublishedSourceData'], download_label('/source-published.json', language))


if __name__ == '__main__':
    unittest.main()
