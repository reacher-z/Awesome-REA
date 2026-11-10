"""Build-time social cards and the Markdown twins written for pages without a builder-made one."""
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from og_images import HEIGHT, WIDTH, render_card  # noqa: E402
from open_graph import open_graph_meta, png_size  # noqa: E402
from social_cards import write_social_cards  # noqa: E402

SITE = 'https://awesomerea.org'


def page(language='en', title='Title'):
    meta = open_graph_meta(language=language, title=title, description='Description', image_url=SITE + '/social-card.png?v=0', url=SITE + '/')
    return f'<!doctype html><html><head>{meta}</head><body><main><h1>{title}</h1><p>Body <a href="/x/">link</a>.</p></main></body></html>'


class CardTests(unittest.TestCase):
    def test_card_is_a_deterministic_1200_by_630_png(self):
        first = render_card(eyebrow='Category', title='Native binaries', footer=('5 entries',))
        self.assertEqual(first, render_card(eyebrow='Category', title='Native binaries', footer=('5 entries',)))
        self.assertTrue(first.startswith(b'\x89PNG\r\n\x1a\n'))
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'card.png'
            path.write_bytes(first)
            self.assertEqual(png_size(path), (WIDTH, HEIGHT))
        idat = first[first.index(b'IDAT') + 4:first.index(b'IEND') - 8]
        self.assertEqual(len(zlib.decompress(idat)), HEIGHT * (WIDTH * 3 + 1))
        self.assertNotEqual(first, render_card(eyebrow='Category', title='Firmware', footer=('5 entries',)))

    def test_committed_default_card_comes_from_the_renderer(self):
        self.assertEqual((ROOT / 'site/social-card.png').read_bytes(), render_card(
            eyebrow='Reverse engineering catalog', title='Awesome Reverse Engineering Anything',
            subtitle='Tools, projects and resources for websites, games, apps, binaries, firmware and protocols.',
            footer=('awesomerea.org',)))

    def test_pages_get_their_category_card_and_localized_alt(self):
        resources = [{'id': 'tool-a', 'kind': 'tool', 'section': 'native-binary'},
                     {'id': 'case-b', 'kind': 'case-study', 'section': 'game'}]
        routes = {'index.html': 'home', 'zh/index.html': 'home', 'resources/index.html': 'resources',
                  'resources/tool-a/index.html': 'section-native-binary', 'zh/resources/case-b/index.html': 'section-game',
                  'browse/firmware/index.html': 'browse-firmware', 'about/index.html': None}
        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            for route in routes:
                (output / route).parent.mkdir(parents=True, exist_ok=True)
                (output / route).write_text(page('zh' if route.startswith('zh/') else 'en'), encoding='utf-8')
            changed = write_social_cards(output, resources=resources, papers=[], section_of=lambda record: record['section'],
                                         sections={'native-binary': ('Native binaries', '原生二进制'), 'game': ('Games', '游戏')},
                                         browse_categories={'firmware': ('Firmware', '固件')}, browse_counts={'firmware': 3},
                                         survey_title='Survey', survey_papers=2, site_url=SITE)
            self.assertEqual(changed, 6)
            for route, key in routes.items():
                html = (output / route).read_text(encoding='utf-8')
                image = re.search(r'property="og:image" content="([^"]+)"', html)[1]
                twitter = re.search(r'name="twitter:image" content="([^"]+)"', html)[1]
                self.assertEqual(image, twitter)
                if key is None:
                    self.assertTrue(image.startswith(SITE + '/social-card.png'))
                    continue
                self.assertRegex(image, rf'^{SITE}/og/{key}\.png\?v=[0-9a-f]{{16}}$')
                self.assertEqual(png_size(output / 'og' / f'{key}.png'), (WIDTH, HEIGHT))
                alt = re.search(r'property="og:image:alt" content="([^"]+)"', html)[1]
                self.assertIn('分享图' if route.startswith('zh/') else 'Awesome REA card', alt)


if __name__ == '__main__':
    unittest.main()
