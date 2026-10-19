"""Detail pages cross-link a resource and a paper only when they describe the same work."""
from html.parser import HTMLParser
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_entry_pages import build_entry_pages, entry_path, matching_entries
from test_entry_pages import paper, resource

PAPER = 'https://doi.org/10.1145/1234567.7654321'


class RelatedSection(HTMLParser):
    """Collect the links and text inside the Related entries section."""
    def __init__(self, text):
        super().__init__()
        self.depth, self.sections, self.links, self.text = 0, 0, [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section' and attrs.get('aria-labelledby') == 'entry-related':
            self.sections += 1
            self.depth = 1
        elif tag == 'section' and self.depth:
            self.depth += 1
        if self.depth and tag == 'a':
            self.links.append(attrs.get('href'))

    def handle_endtag(self, tag):
        if tag == 'section' and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.text.append(data)


def fixtures():
    papers = [paper('paper-fuzzware', id='paper-example', url=PAPER, doi='10.1145/1234567.7654321',
                    code_url='https://github.com/example-org/example-tool')]
    resources = [
        resource(id='repository-match', url='https://github.com/Example-Org/example-tool'),
        resource(id='doi-match', url=PAPER.replace('https://doi.org/', 'https://dx.doi.org/')),
        # Citing the paper as evidence, sharing its title or pointing inside the repository is not the same work.
        resource(id='evidence-only', url='https://github.com/someone/other-tool', evidence_url=PAPER),
        resource(id='name-only', name=papers[0]['title'], url='https://example.org/tool'),
        resource(id='repository-subpath', url='https://github.com/example-org/example-tool/tree/main/docs'),
    ]
    return resources, papers


class RelatedEntryTests(unittest.TestCase):
    def test_only_exact_repository_or_publication_matches_pair_entries(self):
        resources, papers = fixtures()
        matches = matching_entries(resources, papers)
        self.assertEqual({key: [(kind, row['id']) for kind, row in rows] for key, rows in matches.items()}, {
            ('resource', 'doi-match'): [('paper', 'paper-example')],
            ('resource', 'repository-match'): [('paper', 'paper-example')],
            ('paper', 'paper-example'): [('resource', 'doi-match'), ('resource', 'repository-match')],
        })

    def test_detail_pages_link_counterparts_in_both_directions_and_languages(self):
        resources, papers = fixtures()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            build_entry_pages(root, resources, papers)
            read = lambda kind, identifier, language: RelatedSection(
                (root / entry_path(kind, identifier, language).lstrip('/') / 'index.html').read_text(encoding='utf-8'))
            for language in ('en', 'zh'):
                for identifier in ('repository-match', 'doi-match'):
                    section = read('resource', identifier, language)
                    self.assertEqual(section.sections, 1)
                    self.assertEqual(section.links, [entry_path('paper', 'paper-example', language)])
                    self.assertIn(papers[0]['title_zh' if language == 'zh' else 'title'], ''.join(section.text))
                section = read('paper', 'paper-example', language)
                self.assertEqual(section.links, [entry_path('resource', identifier, language)
                                                 for identifier in ('doi-match', 'repository-match')])
                text = ''.join(section.text)
                self.assertNotIn('REA', text)
                self.assertNotRegex(text.casefold(), r'test|verified|运行|验证')
                for identifier in ('evidence-only', 'name-only', 'repository-subpath'):
                    page = (root / entry_path('resource', identifier, language).lstrip('/') / 'index.html').read_text(encoding='utf-8')
                    self.assertEqual(RelatedSection(page).sections, 0)
                    self.assertNotIn('entry-related', page)


if __name__ == '__main__':
    unittest.main()
