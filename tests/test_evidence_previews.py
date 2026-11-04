"""Demo preview URLs cover Class 0/1 entries and stay inside their source review."""
import json
import unittest
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EvidencePreviewTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / 'data/evidence-previews.json').read_text(encoding='utf-8'))
        self.classes = {entry['id']: entry['evidence_class']
                        for entry in json.loads((ROOT / 'data/evidence-classes.json').read_text(encoding='utf-8'))['entries']}
        self.targets = {entry_id for entry_id, level in self.classes.items() if level in (0, 1)}

    def test_schema_and_counts_agree(self):
        self.assertEqual(self.document['schema_version'], 1)
        meta = self.document['meta']
        self.assertEqual(meta['spec_version'], 'evidence-preview-v1')
        entries = self.document['entries']
        self.assertEqual(meta['entry_count'], len(entries))
        self.assertEqual(meta['class_entry_count'], len(self.targets))
        self.assertEqual(meta['class_counts'],
                         {'image': sum(entry['kind'] == 'image' for entry in entries),
                          'video': sum(entry['kind'] == 'video' for entry in entries)})
        self.assertEqual(meta['missing_count'], len(meta['missing']))
        self.assertEqual(meta['entry_count'] + meta['missing_count'], meta['class_entry_count'])
        ids = [entry['id'] for entry in entries]
        self.assertEqual(len(ids), len(set(ids)), 'each entry has at most one preview')
        self.assertFalse(set(ids) & set(meta['missing']), 'an entry is either previewed or missing')

    def test_previews_belong_to_class_0_or_1(self):
        for entry in self.document['entries']:
            self.assertIn(entry['id'], self.targets,
                          f"{entry['id']}: previews are only collected for Class 0/1 entries")
            self.assertIn(entry['kind'], ('image', 'video'), entry['id'])
            self.assertIn(entry['basis'], ('readme-image', 'page-image', 'youtube-thumbnail'), entry['id'])
            self.assertTrue(entry['source_url'].startswith(('http://', 'https://')), entry['id'])
            self.assertTrue(entry['checked_at'], entry['id'])

    def test_preview_urls_are_absolute_images(self):
        for entry in self.document['entries']:
            parts = urllib.parse.urlsplit(entry['image_url'])
            self.assertIn(parts.scheme, ('http', 'https'), entry['id'])
            self.assertTrue(parts.hostname, entry['id'])
            if entry['kind'] == 'video':
                self.assertEqual(entry['basis'], 'youtube-thumbnail', entry['id'])
                self.assertEqual(parts.hostname, 'i.ytimg.com', entry['id'])
            else:
                path = entry['image_url'].lower().split('?', 1)[0]
                if not path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.apng')):
                    # GitHub/Discord attachments have no extension; the fetch step
                    # checks the response Content-Type before accepting them.
                    self.assertIn(parts.hostname, {
                        'user-images.githubusercontent.com', 'cloud.githubusercontent.com',
                        'cdn.discordapp.com', 'media.discordapp.net', 'github.com'}, entry['id'])


if __name__ == '__main__':
    unittest.main()
