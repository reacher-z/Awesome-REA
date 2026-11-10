"""Markdown twins written for indexed pages that no builder makes one for."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from page_twins import page_markdown, write_page_twins  # noqa: E402

SITE = 'https://awesomerea.org'


class PageTwinTests(unittest.TestCase):
    def test_main_becomes_markdown_with_heading_and_address(self):
        html = ('<html><head></head><body><nav><a href="/">Skip</a></nav><main><h1>About <span>it</span></h1>'
                '<p>One <a href="/resources/">two</a>.</p><h2>List</h2><ul><li>A</li><li>B <code>c</code></li></ul>'
                '<table><tr><th>K</th><th>V</th></tr><tr><td>a|b</td><td>1</td></tr></table>'
                '<script>x()</script><div hidden>secret</div><label>Sort<select><option>Name</option></select></label>'
                '<p>Star <span data-stars="o/r">1.2k</span></p><span role="tooltip"><b>tip</b></span><p>After <img src="x"> end</p></main></body></html>')
        markdown = page_markdown(html, SITE + '/about/', 'en')
        self.assertTrue(markdown.startswith('# About it\n\n- HTML: <https://awesomerea.org/about/>\n'))
        self.assertIn('One [two](https://awesomerea.org/resources/) .', markdown)
        self.assertIn('## List', markdown)
        self.assertIn('- B `c`', markdown)
        self.assertIn('| K | V |\n| --- | --- |\n| a\\|b | 1 |', markdown)
        self.assertIn('After end', markdown)
        self.assertIn('\nStar\n', markdown)
        for absent in ('Skip', 'x()', 'secret', 'Sort', 'Name', '1.2k', 'tip'):
            self.assertNotIn(absent, markdown)
        self.assertIsNone(page_markdown('<main><p>No heading</p></main>', SITE + '/', 'en'))

    def test_only_pages_without_a_twin_get_one(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            (output / 'about').mkdir()
            (output / 'about/index.html').write_text('<html><head></head><body><main><h1>About</h1></main></body></html>')
            (output / 'resources').mkdir()
            own = '<html><head><link rel="alternate" type="text/markdown" href="/resources/index.md"></head><body><main><h1>R</h1></main></body></html>'
            (output / 'resources/index.html').write_text(own)
            self.assertEqual(write_page_twins(output, ['/about/', '/resources/'], SITE), ['/about/'])
            self.assertIn('<link rel="alternate" type="text/markdown" href="/about/index.md" title="Markdown">',
                          (output / 'about/index.html').read_text())
            self.assertTrue((output / 'about/index.md').read_text().startswith('# About\n'))
            self.assertEqual((output / 'resources/index.html').read_text(), own)
            self.assertFalse((output / 'resources/index.md').exists())



if __name__ == '__main__':
    unittest.main()
