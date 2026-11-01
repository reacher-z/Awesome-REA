"""/browse/ repository cards keep every fact on one compact meta line under the description."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_browse_pages import repository_card

RECORD = {'id': 'scan-1', 'full_name': 'ReFirmLabs/binwalk', 'name': 'binwalk', 'url': 'https://github.com/ReFirmLabs/binwalk',
          'readme_url': 'https://github.com/ReFirmLabs/binwalk/blob/master/README.md',
          'description_en': 'Firmware Analysis Tool', 'description_zh': '固件分析工具。', 'stars': 14491, 'license': 'MIT',
          'related_entries': [{'kind': 'curated', 'id': 'binwalk', 'title_en': 'Binwalk', 'title_zh': 'Binwalk',
                               'href_en': '/resources/binwalk/', 'href_zh': '/zh/resources/binwalk/'}]}


class BrowseCardDensityTests(unittest.TestCase):
    def test_head_holds_only_the_title_and_the_meta_line_holds_stars_readme_and_license(self):
        for language, stars, license_name in (('en', '14,491 stars', 'MIT'), ('zh', '14,491 星标', 'MIT')):
            html = repository_card(RECORD, language, False)
            head = re.search(r'<div class="source-card-head">(.*?)</div>', html, re.S)[1]
            self.assertTrue(head.startswith('<h2>') and head.endswith('</h2>'))
            self.assertNotIn('source-stars', head)
            meta = re.search(r'<div class="source-card-footer">(.*?)</div>', html, re.S)[1]
            parts = re.findall(r'<(span|a)\b[^>]*>([^<]+)', meta)
            self.assertEqual([text for _, text in parts], [stars, 'README ↗', license_name])
            self.assertIn('title="' + ('采集时的星标快照' if language == 'zh' else 'Stars at collection time') + '"', meta)
            # Order: title, description, related entries, then the meta line.
            positions = [html.index(marker) for marker in ('source-card-head', 'source-card-description', 'source-related', 'source-card-footer')]
            self.assertEqual(positions, sorted(positions))

    def test_cards_without_stars_still_render_readme_and_license(self):
        record = {**RECORD, 'stars': None, 'license': 'NOASSERTION'}
        meta = re.search(r'<div class="source-card-footer">(.*?)</div>', repository_card(record, 'en', False), re.S)[1]
        self.assertNotIn('source-stars', meta)
        self.assertEqual(re.findall(r'>([^<]+)<', meta), ['README ↗', 'License not identified'])

    def test_compact_rules_are_scoped_to_repository_cards(self):
        css = (ROOT / 'site/browse.css').read_text()
        # Curated /resources/ cards share .browse-repository but not .source-card, so they keep their layout.
        rules = re.findall(r'([^{}]+)\{([^}]*)\}', css)
        compact = [selector for selector, body in rules if 'padding:14px' in body and 'browse-repository' in selector]
        self.assertTrue(compact)
        self.assertTrue(all('.source-card.browse-repository' in selector for selector in compact))
        footer = [body for selector, body in rules if selector.strip() == '.browse-repository .source-card-footer']
        self.assertEqual(len(footer), 1)
        self.assertNotIn('border-top', footer[0])


if __name__ == '__main__':
    unittest.main()
