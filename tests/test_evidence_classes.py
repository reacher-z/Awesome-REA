"""Evidence-class data coverage: every curated entry carries a valid class 0-3."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EvidenceClassDataTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / 'data/evidence-classes.json').read_text(encoding='utf-8'))
        self.catalog_ids = []
        self.catalog = {}
        for filename in ('rea-resources.json', 'tool-resources.json'):
            for record in json.loads((ROOT / 'data' / filename).read_text(encoding='utf-8')):
                self.catalog_ids.append(record['id'])
                self.catalog[record['id']] = record

    def test_schema_and_counts_agree(self):
        self.assertEqual(self.document['schema_version'], 1)
        meta = self.document['meta']
        self.assertEqual(meta['spec_version'], 'evidence-class-v2')
        entries = self.document['entries']
        counts = {}
        for entry in entries:
            counts[entry['evidence_class']] = counts.get(entry['evidence_class'], 0) + 1
        self.assertEqual({str(key): value for key, value in counts.items()}, meta['class_counts'])
        self.assertEqual(meta['entry_count'], len(entries))
        self.assertEqual(meta['override_count'], sum(entry['basis'] == 'override' for entry in entries))

    def test_every_curated_entry_has_one_class(self):
        classified = {entry['id'] for entry in self.document['entries']}
        self.assertEqual(classified, set(self.catalog_ids),
                         'data/evidence-classes.json must cover exactly the curated catalog IDs')
        for entry in self.document['entries']:
            self.assertIn(entry['evidence_class'], (0, 1, 2, 3), entry['id'])
            self.assertIn(entry['basis'], ('github-rest', 'gitlab-rest', 'page-fetch', 'override'), entry['id'])
            self.assertTrue(entry['reason'], entry['id'])
            self.assertIn('code', entry['signals'], entry['id'])

    def test_class_zero_is_a_full_software_reconstruction(self):
        self.assertTrue(any(entry['evidence_class'] == 0 for entry in self.document['entries']))
        for entry in self.document['entries']:
            if entry['evidence_class'] != 0:
                continue
            record = self.catalog[entry['id']]
            self.assertEqual(record['kind'], 'case-study', entry['id'])
            self.assertNotIn('binary', record.get('targets', []), entry['id'])

    def test_overrides_exist_in_catalog_and_carry_notes(self):
        path = ROOT / 'data/evidence-class-overrides.json'
        document = json.loads(path.read_text(encoding='utf-8'))
        overrides = {entry['id']: entry for entry in document['entries']}
        entries = {entry['id']: entry for entry in self.document['entries']}
        self.assertTrue(overrides, 'the review pass recorded boundary corrections; keep the file')
        for entry_id, correction in overrides.items():
            self.assertIn(entry_id, entries, entry_id)
            self.assertEqual(entries[entry_id]['basis'], 'override', entry_id)
            self.assertEqual(entries[entry_id]['evidence_class'], correction['evidence_class'], entry_id)
            self.assertTrue(correction.get('note'), f'{entry_id} override needs a reason')


if __name__ == '__main__':
    unittest.main()
