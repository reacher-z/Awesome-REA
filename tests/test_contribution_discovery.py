"""Public submission answers remain crawlable, localized and bound to real forms."""
from html.parser import HTMLParser
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import build_discovery_pages
from homepage_locales import _locale_url
from validate_discovery import Document


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.hrefs = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs:
            self.hrefs.append(attrs['href'])


class ContributionDiscoveryTests(unittest.TestCase):
    def test_bilingual_pages_and_llms_route_to_real_submission_forms(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            routes = build_discovery_pages(output, {'meta': {}, 'resources': []}, None)
            llms = (output / 'llms.txt').read_text(encoding='utf-8')
            for language, prefix in (('en', ''), ('zh-CN', '/zh')):
                route = prefix + '/contribute/'
                self.assertIn(route, routes)
                html = (output / route.lstrip('/') / 'index.html').read_text(encoding='utf-8')
                page = Document(html)
                self.assertEqual((page.language, page.h1), (language, 1))
                self.assertEqual([l['href'] for l in page.links if l.get('rel') == 'canonical'],
                                 ['https://awesomerea.org' + route])
                self.assertIn('https://awesomerea.org' + route, llms)
                links = Links(html).hrefs
                forms = [url for url in links if '/issues/new?template=' in url]
                filenames = {parse_qs(urlsplit(url).query)['template'][0] for url in forms}
                self.assertEqual(filenames, {'resource.yml', 'case-study.yml', 'paper.yml',
                                             'broken-resource.yml', 'translation.yml'})
                for url in forms:
                    self.assertEqual(urlsplit(url).path, '/reacher-z/Awesome-REA/issues/new')
                for filename in filenames:
                    self.assertTrue((ROOT / '.github/ISSUE_TEMPLATE' / filename).is_file())
                for path in ('AGENTS.md', 'data/README.md', '.github/PULL_REQUEST_TEMPLATE.md'):
                    self.assertIn('https://github.com/reacher-z/Awesome-REA/blob/main/' + path, links)
                graph = next(g for g in page.graphs if g.get('@type') == 'WebPage')
                self.assertEqual(graph['url'], 'https://awesomerea.org' + route)
                alternates = {l['hreflang']: l['href'] for l in page.links if 'hreflang' in l}
                self.assertEqual(alternates['en'], 'https://awesomerea.org/contribute/')
                self.assertEqual(alternates['zh-CN'], 'https://awesomerea.org/zh/contribute/')

    def test_homepage_language_changes_keep_contribution_routes_and_fragments(self):
        self.assertEqual(_locale_url('/contribute/#prepare', 'https://awesomerea.org', 'zh'),
                         '/zh/contribute/#prepare')
        self.assertEqual(_locale_url('/zh/contribute/', 'https://awesomerea.org', 'en'),
                         '/contribute/')


if __name__ == '__main__':
    unittest.main()
