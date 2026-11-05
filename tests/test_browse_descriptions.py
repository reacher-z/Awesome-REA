"""Browse metadata must distinguish categories rather than just their counts."""
from html import escape
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_browse_pages import build_browse_pages
from build_repository_index import CATEGORIES
from test_source_browser import full_export
from validate_site import Page
import validate_site


class BrowseDescriptionTests(unittest.TestCase):
    def test_categories_have_distinct_localized_descriptions(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            source = full_export()
            build_browse_pages(output, source, curated_count=1, site_url='https://awesomerea.org',
                               repository_url='https://github.com/reacher-z/Awesome-REA',
                               styles_href='/styles.css', browse_styles_href='/browse.css',
                               favicon_href='/favicon.svg', social_image_href='/social-card.png',
                               data_revision='0' * 16)
            descriptions = []
            for slug, labels in CATEGORIES.items():
                for language in ('en', 'zh'):
                    prefix = 'zh/' if language == 'zh' else ''
                    text = (output / f'{prefix}browse/{slug}/index.html').read_text(encoding='utf-8')
                    page = Page(text)
                    description = page.meta['description']
                    self.assertIn(labels[language == 'zh'], description)
                    self.assertEqual(page.meta['og:description'], description)
                    self.assertIn(f'<p>{escape(description)}</p>', text)
                    entities = list(validate_site.schema_entities(page.schemas, 'CollectionPage'))
                    self.assertEqual(entities[0]['description'], description)
                    if language == 'en':
                        descriptions.append(re.sub(r'[\d,]', '', description))
                    else:
                        count = 2 if slug == 'android' else 0
                        self.assertEqual(description, f'浏览 {count:,} 个{labels[1]}相关仓库，查看项目简介、原始链接与许可证信息。')
            self.assertEqual(len(set(descriptions)), len(CATEGORIES))

    def test_validator_rejects_descriptions_that_only_differ_by_count(self):
        pages = {route: Page(f'<meta name="description" content="{description}">')
                 for route, description in [('/a/', 'Browse 1,234 repositories.'),
                                             ('/b/', 'Browse 67 repositories.')]}
        with self.assertRaisesRegex(AssertionError, 'Duplicate.*description'):
            validate_site.validate_unique_descriptions(pages)
        pages['/b/'] = Page('<meta name="description" content="Browse 67 games.">')
        validate_site.validate_unique_descriptions(pages)


if __name__ == '__main__':
    unittest.main()
