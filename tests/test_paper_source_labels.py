"""Paper detail pages label primary sources and keep every href in order; /papers/ rows link and count them."""
from copy import deepcopy
from html import unescape
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_entry_pages import build_entry_pages, entry_path
from build_paper_pages import paper_card
from evidence_links import source_label

REVISION = 'e17e787b41137793bcef9f860bdfe9e6a1b2c3d4'
PINNED = f'https://github.com/example/world-models/blob/{REVISION}/src/agent.py#L10-L20'
TREE = f'https://github.com/example/world-models/tree/{REVISION}/docs'
OTHER = 'https://arxiv.org/abs/2405.15383'


def paper(**changes):
    record = deepcopy(next(row for row in json.loads((ROOT / 'data/papers.json').read_text()) if row['id'] == 'paper-fuzzware'))
    record.update({'evidence_urls': [PINNED, OTHER, TREE], **changes})
    return record


def source_items(html):
    """Primary-source list items after the localized heading, in order."""
    heading = re.search(r'(?:Primary sources|一手来源)</h[24]>\s*<([ou]l)[^>]*>(.*?)</\1>', html, re.S)
    return re.findall(r'<li>(.*?)</li>', heading[2], re.S)


class PaperSourceLabelTests(unittest.TestCase):
    def test_only_pinned_github_files_and_directories_get_compact_labels(self):
        self.assertEqual(source_label(PINNED, 'en')[0], 'src/agent.py#L10-L20')
        self.assertIn('GitHub · example/world-models · Revision <span title="' + REVISION + '">e17e787</span>', source_label(PINNED, 'en')[1])
        self.assertIn('修订 <span title="' + REVISION + '">e17e787</span>', source_label(TREE, 'zh')[1])
        self.assertEqual(source_label(TREE, 'en')[0], 'docs')
        for url in (OTHER, 'https://github.com/example/world-models/blob/main/README.md',
                    f'https://github.com/example/world-models/blob/{REVISION}/README.md?plain=1',
                    f'https://github.com/example/world-models/commit/{REVISION}/x',
                    'https://gitlab.com/example/world-models/-/blob/' + REVISION + '/README.md'):
            self.assertEqual(source_label(url, 'en'), (url, ''))

    def test_detail_pages_label_sources_and_keep_every_href_in_order(self):
        record = paper()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_entry_pages(root, [], [record])
            for language in ('en', 'zh'):
                detail = (root / entry_path('paper', record['id'], language).lstrip('/') / 'index.html').read_text()
                items = source_items(detail)
                hrefs = [unescape(re.search(r'href="([^"]+)"', item)[1]) for item in items]
                self.assertEqual(hrefs, record['evidence_urls'])
                for item in items:
                    href = re.search(r'href="([^"]+)"', item)[1]
                    self.assertIn(f'title="{href}"', item)
                    self.assertIn('target="_blank" rel="noopener"', item)
                self.assertIn('>src/agent.py#L10-L20</a>', items[0])
                self.assertIn('GitHub · example/world-models · ' + ('修订' if language == 'zh' else 'Revision'), items[0])
                self.assertIn('>' + OTHER + '</a>', items[1])
                self.assertNotIn('entry-source-context', items[1])
                # Compact labels carry the repository and revision in their name; full URLs need none.
                revision = '修订' if language == 'zh' else 'revision'
                separator = '，' if language == 'zh' else ', '
                self.assertIn(f'aria-label="src/agent.py#L10-L20{separator}GitHub example/world-models{separator}{revision} e17e787"', items[0])
                self.assertNotIn('aria-label', items[1])
                # The /papers/ row links that list instead of repeating it, and counts what it holds.
                card = paper_card(record, language, False)
                self.assertIsNone(re.search(r'(?:Primary sources|一手来源)</h[24]>', card))
                for url in record['evidence_urls']:
                    self.assertNotIn(url, card)
                self.assertIn(f'href="{entry_path("paper", record["id"], language)}#entry-sources"', card)
                self.assertIn('id="entry-sources"', detail)
                self.assertIn('3 个来源' if language == 'zh' else '3 sources', card)

    def test_evidence_link_names_are_distinct_on_each_detail_page(self):
        papers = json.loads((ROOT / 'data/papers.json').read_text())
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_entry_pages(root, [], papers)
            for language in ('en', 'zh'):
                for record in papers:
                    destinations = {}
                    for item in source_items((root / entry_path('paper', record['id'], language).lstrip('/') / 'index.html').read_text()):
                        href = unescape(re.search(r'href="([^"]+)"', item)[1])
                        named = re.search(r'aria-label="([^"]+)"', item)
                        name = unescape(named[1]) if named else unescape(re.search(r'>([^<]+)</a>', item)[1])
                        self.assertTrue(name.startswith(unescape(re.search(r'>([^<]+)</a>', item)[1])))
                        destinations.setdefault(name, set()).add(href)
                    self.assertEqual([name for name, hrefs in destinations.items() if len(hrefs) > 1], [], record['id'])

    def test_repeated_urls_are_listed_and_counted_once(self):
        # The detail page lists each source once, and the directory row counts the sources it lists.
        record = paper(evidence_urls=[PINNED, OTHER, PINNED])
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_entry_pages(root, [], [record])
            detail = (root / entry_path('paper', record['id'], 'en').lstrip('/') / 'index.html').read_text()
        self.assertEqual([unescape(re.search(r'href="([^"]+)"', item)[1]) for item in source_items(detail)], [PINNED, OTHER])
        self.assertIn('>2 sources · checked', paper_card(record, 'en', False))
        self.assertIn('>1 source · checked', paper_card(paper(evidence_urls=[OTHER, OTHER]), 'en', False))


if __name__ == '__main__':
    unittest.main()
