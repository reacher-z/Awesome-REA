"""Demo preview URLs cover Class 0/1 entries and stay inside their source review."""
import base64
import json
import sys
import unittest
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from build_evidence_previews import carried_forward, github_preview, usable_image, with_raw_image  # noqa: E402
from media_privacy import public_media_url  # noqa: E402


class EvidencePreviewTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / 'data/evidence-previews.json').read_text(encoding='utf-8'))
        self.classes = {entry['id']: entry['evidence_class']
                        for entry in json.loads((ROOT / 'data/evidence-classes.json').read_text(encoding='utf-8'))['entries']}
        self.targets = {entry_id for entry_id, level in self.classes.items() if level in (0, 1)}



    def test_cached_blob_preview_becomes_a_pinned_raw_file(self):
        cached = {'image_url': 'https://github.com/DenSinH/DSHBA/blob/master/files/DSHBA_unlocked.png', 'kind': 'image',
                  'basis': 'readme-image', 'source_url': 'https://github.com/DenSinH/DSHBA', 'revision': 'c' * 40}
        self.assertEqual(with_raw_image(cached)['image_url'],
                         'https://raw.githubusercontent.com/DenSinH/DSHBA/' + 'c' * 40 + '/files/DSHBA_unlocked.png')
    def test_github_blob_image_becomes_a_pinned_raw_file(self):
        base = 'https://raw.githubusercontent.com/DenSinH/DSHBA/' + 'b' * 40 + '/'
        self.assertEqual(usable_image('https://github.com/DenSinH/DSHBA/blob/master/files/DSHBA_unlocked.png', base),
                         'https://raw.githubusercontent.com/DenSinH/DSHBA/' + 'b' * 40 + '/files/DSHBA_unlocked.png')
        self.assertEqual(usable_image('https://github.com/other/repo/blob/main/a.png?raw=true', base),
                         'https://raw.githubusercontent.com/other/repo/main/a.png')
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

    def test_preview_urls_are_public(self):
        for entry in self.document['entries']:
            self.assertTrue(public_media_url(entry['image_url']),
                            f"{entry['id']}: a preview must point at public media")

    def test_private_repositories_are_not_previewed(self):
        for repository in ({'private': True, 'default_branch': 'main'},
                           {'visibility': 'private', 'default_branch': 'main'}):
            self.assertIsNone(github_preview(_FakeClient(repository), 'acme/private'))
        self.assertIsNotNone(github_preview(
            _FakeClient({'private': False, 'visibility': 'public', 'default_branch': 'main'}), 'acme/public'))

    def test_private_attachment_urls_are_refused(self):
        base = 'https://github.com/acme/foo'
        self.assertIsNone(usable_image('https://private-user-images.githubusercontent.com/1/a.png', base))
        self.assertIsNone(usable_image('https://user-images.githubusercontent.com/1/a.png?jwt=secret', base))
        self.assertEqual(usable_image('https://user-images.githubusercontent.com/1/a.png', base),
                         'https://user-images.githubusercontent.com/1/a.png')

    def test_refresh_without_media_keeps_the_existing_preview(self):
        old = {'id': 'x', 'image_url': 'https://raw.githubusercontent.com/o/r/' + '0' * 40 + '/demo.png',
               'kind': 'image', 'basis': 'readme-image', 'source_url': 'https://github.com/o/r'}
        self.assertIs(carried_forward(old), old)
        self.assertIsNone(carried_forward(old, drop_missing=True))
        self.assertIsNone(carried_forward(None))
        self.assertIsNone(carried_forward({**old, 'image_url': 'https://user-images.githubusercontent.com/1/a.png?jwt=x'}))

    def test_validator_accepts_current_data(self):
        from validate import validate_evidence_media
        errors = []
        validate_evidence_media(errors)
        self.assertEqual(errors, [])


class _FakeClient:
    """Just enough of classify_evidence_classes.HttpClient for github_preview."""

    def __init__(self, repository):
        self.repository = repository

    def get(self, url, timeout=30, page=False):
        if url.endswith('/readme'):
            content = base64.b64encode(b'![demo](https://example.com/shot.png)').decode()
            return 200, json.dumps({'content': content}).encode(), {}
        return 200, json.dumps(self.repository).encode(), {}


if __name__ == '__main__':
    unittest.main()
