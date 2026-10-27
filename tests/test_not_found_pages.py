"""Each language has its own 404 page with a script-free homepage search and section links."""
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import build_discovery_pages
from validate_site import validate_not_found_pages

RESOURCE = {'id': 'fixture', 'name': 'Fixture', 'name_zh': '测试', 'url': 'https://example.org/fixture',
            'description_en': 'A fixture.', 'description_zh': '测试条目。', 'category': 'core',
            'relationship': 'foundation', 'targets': ['app'], 'kind': 'tool',
            'requirements': ['None.'], 'requirements_zh': ['无。'],
            'evidence_url': 'https://example.org/fixture/evidence', 'verified_at': '2026-10-17',
            'verification': 'source-reviewed'}


class NotFoundPageTests(unittest.TestCase):
    def build(self, output):
        (output / 'index.html').write_text('<!doctype html>', encoding='utf-8')
        build_discovery_pages(output, {'resources': [RESOURCE], 'meta': {}}, None)

    def test_english_and_chinese_pages_search_their_own_homepage(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            self.build(output)
            validate_not_found_pages(output, (1200, 630))
            for path, lang, prefix, title, other_title in (('404.html', 'en', '', 'Page not found', '页面不存在'),
                                                           ('zh/404.html', 'zh-CN', '/zh', '页面不存在', 'Page not found')):
                with self.subTest(path=path):
                    text = (output / path).read_text(encoding='utf-8')
                    self.assertIn(f'<html lang="{lang}"', text)
                    self.assertIn('<meta name="robots" content="noindex">', text)
                    # One language per page, so no heading line starts with a separator.
                    h1 = re.search(r'<h1>(.*?)</h1>', text)[1]
                    self.assertEqual(h1, title + '<span class="title-dot" aria-hidden="true">.</span>')
                    self.assertNotIn(other_title, text)
                    self.assertIn(f'action="{prefix}/#catalog" method="get"', text)
                    for section in ('resources', 'cases', 'papers', 'browse', 'survey'):
                        self.assertIn(f'href="{prefix}/{section}/"', text)
                    self.assertIn(f'href="{"/" if prefix else "/zh/"}" lang="{"en" if prefix else "zh-CN"}"', text)

    def test_validator_rejects_a_missing_search_or_the_wrong_language(self):
        for path, old, new in (('404.html', 'action="/#catalog"', 'action="https://example.org/"'),
                               ('zh/404.html', '<html lang="zh-CN"', '<html lang="en"'),
                               ('zh/404.html', 'href="/zh/survey/"', 'href="/survey/"'),
                               ('404.html', ' name="q"', ' name="query"')):
            with self.subTest(path=path, old=old), TemporaryDirectory() as directory:
                output = Path(directory)
                self.build(output)
                page = output / path
                page.write_text(page.read_text(encoding='utf-8').replace(old, new), encoding='utf-8')
                with self.assertRaises(AssertionError):
                    validate_not_found_pages(output, (1200, 630))


if __name__ == '__main__':
    unittest.main()
