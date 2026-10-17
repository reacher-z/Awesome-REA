"""Keep shipped stylesheets tied to the generated pages that use them."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_site import validate_stylesheet_references


class StylesheetReferenceTests(unittest.TestCase):
    def build(self, files):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        for name, text in files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text, encoding='utf-8')
        return root

    def test_linked_stylesheets_pass(self):
        root = self.build({
            'index.html': '<link rel="stylesheet" href="styles.css?v=abc">',
            'zh/index.html': '<link rel="stylesheet" href="/styles.css?v=abc">',
            'browse/index.html': '<link rel="stylesheet" href="https://awesomerea.org/browse.css">',
            'styles.css': '', 'browse.css': ''})
        validate_stylesheet_references(root)

    def test_unlinked_stylesheet_fails(self):
        root = self.build({
            'index.html': '<link rel="stylesheet" href="/styles.css"><a href="/discovery.css">CSS</a>',
            'about/index.html': '<link rel="stylesheet" href="https://assets.example.org/discovery.css">',
            'styles.css': '', 'discovery.css': ''})
        with self.assertRaisesRegex(AssertionError, 'discovery.css'):
            validate_stylesheet_references(root)


if __name__ == '__main__':
    unittest.main()
