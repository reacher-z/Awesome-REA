"""Keep internal #fragment links in the built site pointed at real anchors."""
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_site
import validate_site
from validate_site import Page, validate_link_fragments


class LinkFragmentTest(unittest.TestCase):
    def test_same_and_cross_page_fragments_need_an_id_or_anchor_name(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'about').mkdir()
            home = output / 'index.html'
            about = output / 'about/index.html'
            home.write_text('<h2 id="intro">Intro</h2>', encoding='utf-8')
            about.write_text('<a name="team"></a><h2 id="团队">团队</h2>', encoding='utf-8')
            (output / 'data.json').write_text('{}', encoding='utf-8')
            (output / 'extra.html').write_text('<p id="kept">Not in the sitemap</p>', encoding='utf-8')
            pages = {'/': Page(home.read_text(encoding='utf-8')), '/about/': Page(about.read_text(encoding='utf-8'))}
            valid = [('/', '#intro', home), ('/', '/about/#team', about), ('/about/', '#%E5%9B%A2%E9%98%9F', about),
                     ('/about/', '../#intro', home), ('/', '/data.json#ignored', output / 'data.json'),
                     ('/', '/extra.html#kept', output / 'extra.html')]
            validate_link_fragments(output, pages, valid)
            missing = [('/', '#gone', home), ('/about/', '/#intro-renamed', home), ('/', '/extra.html#lost', output / 'extra.html')]
            with self.assertRaises(AssertionError) as caught:
                validate_link_fragments(output, pages, valid + missing)
            self.assertEqual(str(caught.exception),
                             'Missing link fragment targets: /: #gone; /about/: /#intro-renamed; /: /extra.html#lost')

    def test_built_site_passes_and_a_renamed_section_anchor_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'dist'
            build_site.build_site(output)
            with mock.patch.object(validate_site, 'OUTPUT', output), contextlib.redirect_stdout(io.StringIO()):
                # The current build resolves every internal fragment without an allowlist.
                validate_site.main()
                page = output / 'resources/index.html'
                html = page.read_text(encoding='utf-8')
                self.assertIn('<a id="game"', html)
                page.write_text(html.replace('<a id="game"', '<a id="games"'), encoding='utf-8')
                with self.assertRaisesRegex(AssertionError, r'/resources/: #game(;|$)') as caught:
                    validate_site.main()
            self.assertIn('/: /resources/#game', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
