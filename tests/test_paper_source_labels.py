"""/papers/ rows label primary sources exactly as the paper detail pages do, keeping every href in order."""
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

    def test_directory_rows_match_detail_pages_and_keep_every_href_in_order(self):
        record = paper()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_entry_pages(root, [], [record])
            for language in ('en', 'zh'):
                card = paper_card(record, language, False)
                items = source_items(card)
                hrefs = [unescape(re.search(r'href="([^"]+)"', item)[1]) for item in items]
                self.assertEqual(hrefs, record['evidence_urls'])
                for item in items:
                    href = re.search(r'href="([^"]+)"', item)[1]
                    self.assertIn(f'title="{href}"', item)
                    self.assertIn('target="_blank" rel="noopener"', item)
                detail = (root / entry_path('paper', record['id'], language).lstrip('/') / 'index.html').read_text()
                self.assertEqual(items, source_items(detail))
                self.assertIn('>src/agent.py#L10-L20</a>', items[0])
                self.assertIn('GitHub · example/world-models · ' + ('修订' if language == 'zh' else 'Revision'), items[0])
                self.assertIn('>' + OTHER + '</a>', items[1])
                self.assertNotIn('entry-source-context', items[1])

    def test_repeated_urls_stay_in_the_directory_list(self):
        # The detail page lists each source once; the directory keeps the record's list untouched.
        record = paper(evidence_urls=[PINNED, OTHER, PINNED])
        items = source_items(paper_card(record, 'en', False))
        self.assertEqual([unescape(re.search(r'href="([^"]+)"', item)[1]) for item in items], record['evidence_urls'])


if __name__ == '__main__':
    unittest.main()
