"""The /about/ links are grouped by purpose, with each download's format and built size."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import build_discovery_pages, file_size_label
from validate_site import AboutLinkGroups, validate_about_links


class AboutLinkGroupTests(unittest.TestCase):
    def test_file_sizes_use_decimal_megabytes_or_kilobytes(self):
        self.assertEqual([file_size_label(n) for n in (2_345_678, 8_700_000, 680_000, 100_000, 99_400, 12)],
                         ['2.3 MB', '8.7 MB', '0.7 MB', '0.1 MB', '99 KB', '1 KB'])

    def test_about_links_are_grouped_with_sized_downloads_and_marked_github_documents(self):
        resource = {'id': 'fixture', 'name': 'Fixture', 'name_zh': '测试', 'url': 'https://example.org/fixture',
                    'description_en': 'A fixture.', 'description_zh': '测试条目。', 'category': 'core',
                    'relationship': 'foundation', 'targets': ['app'], 'kind': 'tool',
                    'requirements': ['None.'], 'requirements_zh': ['无。'],
                    'evidence_url': 'https://example.org/fixture/evidence', 'verified_at': '2026-10-17',
                    'verification': 'source-reviewed'}
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'index.html').write_text('<!doctype html>', encoding='utf-8')
            for name, size in (('catalog.json', 2_345_678), ('source-index.json', 512_000), ('papers.json', 2)):
                (output / name).write_text('[]' if name == 'papers.json' else 'x' * size, encoding='utf-8')
            build_discovery_pages(output, {'resources': [resource], 'meta': {}}, None)
            validate_about_links(output)
            for prefix, browse, download, methods in (('', 'Browse', 'Download', 'Methods and policy on GitHub'),
                                                      ('/zh', '浏览', '下载', 'GitHub 上的方法与规则')):
                with self.subTest(prefix=prefix):
                    page = (output / prefix.lstrip('/') / 'about/index.html').read_text(encoding='utf-8')
                    for key, heading in (('browse', browse), ('download', download), ('methods', methods)):
                        self.assertIn(f'<h3 id="about-links-{key}">{heading}</h3>', page)
                    groups = AboutLinkGroups(page).groups
                    self.assertEqual([values['href'] for values, _ in groups['browse']],
                                     [prefix + path for path in ('/resources/', '/cases/', '/browse/', '/papers/', '/survey/')])
                    downloads = {values['href']: (values.get('download'), text) for values, text in groups['download']}
                    self.assertEqual(downloads['/catalog.json'],
                                     ('awesomerea-curated-catalog.json', ('精选目录' if prefix else 'Curated catalog') + ' JSON · 2.3 MB ↓'))
                    self.assertEqual(downloads['/source-index.json'][1], ('仓库索引' if prefix else 'Repository index') + ' JSON · 0.5 MB ↓')
                    self.assertEqual(downloads['/papers.json'][1], ('论文元数据' if prefix else 'Paper metadata') + ' JSON · 1 KB ↓')
                    self.assertEqual(len(groups['methods']), 6)
                    # The filter-chip navigation is gone from /about/.
                    self.assertNotIn('browse-category-nav', page)


if __name__ == '__main__':
    unittest.main()
