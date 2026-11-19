"""/resources/ rows show a small WebP of a demo preview and link the original; without Pillow they show the original."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import preview_thumbs
from build_home import preview_figure


class PreviewFigureTests(unittest.TestCase):
    RECORD = {'name': 'Tool', 'name_zh': '工具', 'preview': '/previews/tool.png', 'preview_kind': 'image',
              'preview_thumb': '/previews/thumbs/tool.webp'}

    def test_rows_show_the_thumbnail_and_link_the_original(self):
        html = preview_figure(self.RECORD, 'en', thumb=True)
        self.assertIn('<a class="card-preview-link" href="/previews/tool.png" aria-label="Full-size demo screenshot: Tool">'
                      '<img src="/previews/thumbs/tool.webp"', html)
        self.assertIn('loading="lazy"', html)
        self.assertIn('aria-label="完整演示截图：工具"', preview_figure(self.RECORD, 'zh', thumb=True))

    def test_a_video_still_shows_its_thumbnail_without_a_link(self):
        html = preview_figure({**self.RECORD, 'preview_kind': 'video'}, 'en', thumb=True)
        self.assertIn('<img src="/previews/thumbs/tool.webp"', html)
        self.assertNotIn('card-preview-link', html)

    def test_without_a_thumbnail_or_outside_rows_the_original_shows(self):
        for record, thumb in ((self.RECORD, False), ({**self.RECORD, 'preview_thumb': None}, True)):
            html = preview_figure(record, 'zh', thumb=thumb)
            self.assertIn('<img src="/previews/tool.png"', html)
            self.assertNotIn('card-preview-link', html)


@unittest.skipUnless(preview_thumbs.available(), 'Pillow is installed only in the publish job')
class ThumbnailTests(unittest.TestCase):
    def setUp(self):
        from PIL import Image
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.wide = self.root / 'wide.png'
        # Noise keeps the PNG large, as real screenshots are.
        Image.effect_noise((1600, 900), 64).convert('RGB').save(self.wide)
        self.gif = self.root / 'anim.gif'
        frames = [Image.new('P', (960, 540), color) for color in (10, 200)]
        frames[0].save(self.gif, save_all=True, append_images=frames[1:], duration=100)

    def test_wide_image_becomes_a_480_px_webp_and_is_cached(self):
        from PIL import Image
        cache = self.root / 'thumbs'
        made = preview_thumbs.thumbnail(self.wide, cache)
        self.assertIsNotNone(made)
        with Image.open(made) as image:
            self.assertEqual((image.format, image.width, image.height), ('WEBP', 480, 270))
        self.assertLess(made.stat().st_size, self.wide.stat().st_size)
        self.assertEqual(preview_thumbs.thumbnail(self.wide, cache), made)
        self.assertIn(f'-w{preview_thumbs.WIDTH}-q{preview_thumbs.QUALITY}-v{preview_thumbs.VERSION}', made.name)
        self.assertEqual(list(cache.glob('*.part')), [])

    def test_a_tall_image_keeps_the_band_the_row_shows(self):
        from PIL import Image
        tall = self.root / 'tall.png'
        Image.effect_noise((800, 4000), 64).convert('RGB').save(tall)
        with Image.open(preview_thumbs.thumbnail(tall, self.root / 'thumbs')) as image:
            self.assertEqual(image.size, (480, 270))

    def test_animated_gif_gives_its_first_frame(self):
        from PIL import Image
        made = preview_thumbs.thumbnail(self.gif, self.root / 'thumbs')
        if made is not None:
            with Image.open(made) as image:
                self.assertEqual(image.width, 480)
                self.assertEqual(getattr(image, 'n_frames', 1), 1)

    def test_a_missing_file_falls_back_without_raising(self):
        with mock.patch('sys.stderr'):
            self.assertIsNone(preview_thumbs.thumbnail(self.root / 'missing.png', self.root / 'thumbs'))

    def test_an_unreadable_file_falls_back_to_its_original(self):
        broken = self.root / 'broken.png'
        broken.write_bytes(b'not an image')
        with mock.patch('sys.stderr') as stderr:
            self.assertIsNone(preview_thumbs.thumbnail(broken, self.root / 'thumbs'))
        self.assertIn('broken.png', ''.join(str(call) for call in stderr.write.call_args_list))


class WithoutPillowTests(unittest.TestCase):
    def test_no_pillow_means_no_thumbnail(self):
        with mock.patch.object(preview_thumbs, '_pillow', return_value=None):
            self.assertFalse(preview_thumbs.available())
            self.assertIsNone(preview_thumbs.thumbnail(Path(__file__), Path('/nonexistent')))


if __name__ == '__main__':
    unittest.main()
