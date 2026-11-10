"""One shared tokenization leaves every parser as if it had been fed the page itself."""
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import validate_site
from validate_site import (DocumentTitle, FooterLinks, Page, Stylesheets, VisibleBreadcrumb, parse_once,
                           parsed_file)

# The tokenizer's own state; the shared tokenization keeps it on the shared parser.
PARSER_STATE = {*vars(HTMLParser()), '_HTMLParser__starttag_text'}
HTML = '''<!doctype html><html lang="zh-CN"><head><title>A &amp; B</title><!-- note -->
<link rel="stylesheet" href="/assets/site.abc.css"><script>let a = "<b>";</script><style>p{}</style></head>
<body><nav aria-label="当前位置"><a href="/">首页</a><span aria-current="page">页</span></nav><br/>
<?pi data?><![CDATA[x]]><p>&#169; &copy; &nbsp;text</p>
<footer class="site-footer"><a href="/catalog.json">目录 JSON</a></footer></body></html>'''


def state(parser):
    return {key: value for key, value in vars(parser).items() if key not in PARSER_STATE}


class SharedTokensTests(unittest.TestCase):
    def test_each_parser_ends_as_if_fed_alone(self):
        classes = (VisibleBreadcrumb, FooterLinks, Stylesheets, DocumentTitle)
        results = parse_once(HTML, classes)
        for cls in classes:
            with self.subTest(parser=cls.__name__):
                parser, error = results[cls]
                self.assertIsNone(error)
                self.assertEqual(state(parser), state(cls(HTML)))
        self.assertEqual(results[DocumentTitle][0].titles, ['A & B'])
        self.assertEqual(results[FooterLinks][0].footer, [['/catalog.json', '目录 JSON']])

    def test_a_parser_that_raises_keeps_its_error_and_the_others_finish(self):
        html = '<html><body><p id="a" id="b">x</p><title>T</title></body></html>'
        with self.assertRaises(AssertionError) as alone:
            Page(html)
        results = parse_once(html, (Page, DocumentTitle))
        self.assertIsInstance(results[Page][1], AssertionError)
        self.assertEqual(str(results[Page][1]), str(alone.exception))
        self.assertEqual(results[DocumentTitle][0].titles, ['T'])
        self.assertIsNone(results[DocumentTitle][1])

    def test_a_cached_parse_is_used_and_its_error_raised_only_while_main_holds_it(self):
        path = ROOT / 'site' / 'missing-page.html'
        title, _ = parse_once('<title>Kept</title>', (DocumentTitle,))[DocumentTitle]
        validate_site._PARSED[str(path)] = {DocumentTitle: (title, None), Stylesheets: (None, ValueError('stored'))}
        try:
            self.assertIs(parsed_file(DocumentTitle, path), title)
            with self.assertRaisesRegex(ValueError, 'stored'):
                parsed_file(Stylesheets, path)
        finally:
            validate_site._PARSED.clear()
        with self.assertRaises(FileNotFoundError):
            parsed_file(DocumentTitle, path)


if __name__ == '__main__':
    unittest.main()
