"""Evidence links carry the same compact labels on curated, case and entry pages."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import build_discovery_pages
from build_entry_pages import _sources
from evidence_links import source_label

REVISION = '0123456789abcdef0123456789abcdef01234567'
PINNED = f'https://github.com/example/tool/blob/{REVISION}/docs/reverse-engineering/very/long/path/notes.md#L10-L20'
TREE = f'https://github.com/example/tool/tree/{REVISION}/src'
OTHER = ['https://github.com/example/tool/wiki/Protocol', 'https://example.org/post?id=1']


class Links(HTMLParser):
    """Collect each link's attributes and accessible text (aria-hidden content excluded)."""
    def __init__(self):
        super().__init__()
        self.links, self.stack, self.hidden = [], [], 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.stack.append(attrs.get('aria-hidden') == 'true')
        self.hidden += self.stack[-1]
        if tag == 'a':
            self.links.append({**attrs, 'text': ''})
            self.open = True

    def handle_endtag(self, tag):
        self.hidden -= self.stack.pop()
        if tag == 'a':
            self.open = False

    def handle_data(self, data):
        if getattr(self, 'open', False) and not self.hidden:
            self.links[-1]['text'] += data


def links(content):
    parser = Links()
    parser.feed(content)
    return parser.links


class EvidenceLabelTests(unittest.TestCase):
    def test_only_commit_pinned_github_paths_get_compact_labels(self):
        label, context = source_label(PINNED, 'en')
        self.assertEqual(label, 'docs/reverse-engineering/very/long/path/notes.md#L10-L20')
        self.assertIn('GitHub · example/tool · Revision <span title="' + REVISION + '">0123456</span>', context)
        self.assertIn('修订', source_label(TREE, 'zh')[1])
        self.assertEqual(source_label(TREE, 'zh')[0], 'src')
        for url in OTHER + [f'https://github.com/example/tool/blob/main/README.md', PINNED.replace('#', '?plain=1#')]:
            self.assertEqual(source_label(url, 'en'), (url, ''))

    def test_curated_and_case_pages_name_links_like_entry_pages(self):
        additional = [PINNED, TREE, *OTHER]
        record = {
            'id': 'labelled-case', 'name': 'Labelled case', 'name_zh': '标注案例', 'url': 'https://example.org/case',
            'description_en': 'A case.', 'description_zh': '一个案例。', 'category': 'reconstruction-cases',
            'relationship': 'independent-reconstruction', 'targets': ['game'], 'kind': 'case-study',
            'requirements': ['Own copy.'], 'requirements_zh': ['自备副本。'], 'evidence_url': 'https://example.org/evidence',
            'additional_evidence_urls': additional, 'verified_at': '2026-10-17T01:02:03Z', 'verification': 'source-reviewed'}
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'index.html').write_text('<link rel="stylesheet" href="https://awesome-rea.pages.dev/fontawesome.css">')
            build_discovery_pages(output, {'resources': [record], 'meta': {'site_url': 'https://awesomerea.org'}}, None)
            for language, prefix in (('en', ''), ('zh', 'zh/')):
                entry = [link['text'] for link in links(_sources([record['evidence_url'], *additional], language))]
                self.assertEqual(entry, [source_label(url, language)[0] for url in [record['evidence_url'], *additional]])
                for page in ('resources', 'cases'):
                    with self.subTest(language=language, page=page):
                        content = (output / prefix / page / 'index.html').read_text()
                        self.assertIsNone(re.search(r'(Additional source|补充来源) \d', content), 'numbered evidence names remain')
                        rendered = [link for link in links(content) if link.get('href') in additional]
                        # Same order and targets as the record; each name equals the entry-page label.
                        self.assertEqual([link['href'] for link in rendered], additional)
                        self.assertEqual([link['text'].strip() for link in rendered], entry[1:])
                        for link in rendered:
                            self.assertEqual((link['title'], link['target'], link['rel']), (link['href'], '_blank', 'noopener noreferrer'))
                        self.assertEqual(content.count('GitHub · example/tool · ' + ('修订' if language == 'zh' else 'Revision')), 2)


if __name__ == '__main__':
    unittest.main()
