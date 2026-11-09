"""Review decisions on discovery records: validation, what leaves the queue and what stays held."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import build_discoveries as site
import discoveries
import discovery_reviews as reviews
import discovery_classes as classes
from test_discoveries import capture, make_batch

NOW = datetime(2026, 11, 7, tzinfo=timezone.utc)
COMMIT = 'a' * 40


def decision(number, **changes):
    entry = {'decision': 'exclude', 'reason_code': 'unrelated', 'reason_en': 'Ordinary photo reconstruction.',
             'reason_zh': '普通的照片重建。', 'readme_sha256': capture(number)['readme_sha256'],
             'evidence_url': f'https://github.com/example/repo/blob/{COMMIT}/README.md', 'reviewed_at': '2026-11-06'}
    entry.update(changes)
    return entry


def queue_with(directory, entries, resources=()):
    root = Path(directory)
    folder = root / discoveries.DIRECTORY
    folder.mkdir(parents=True)
    batch = make_batch([capture(1), capture(2), capture(3)], run_id=100, ingested='2026-11-05T17:00:00Z')
    (folder / f"{batch['batch_id']}.json").write_bytes(discoveries.batch_bytes(batch))
    (root / reviews.FILE).write_text(json.dumps(entries), encoding='utf-8')
    return site.discovery_queue(root, None, [], list(resources))


class ValidationTest(unittest.TestCase):
    def problems(self, entries):
        batch = make_batch([capture(1)], run_id=100, ingested='2026-11-05T17:00:00Z')
        errors = []
        reviews.validate_reviews([batch], entries, errors, now=NOW)
        return errors

    def test_a_decision_bound_to_its_scan_passes(self):
        self.assertEqual(self.problems({capture(1)['id']: decision(1)}), [])
        self.assertEqual(self.problems({capture(1)['id']: decision(1, decision='hold', reason_code='insufficient-docs')}), [])
        self.assertEqual(self.problems({capture(1)['id']: decision(1, reason_code='duplicate-curated', duplicate_of='ghidra')}), [])

    def test_lead_fields_and_batch_binding(self):
        lead = {'id': 'lead-' + 'a' * 24, 'observed_at': '2026-11-05T21:00:00Z'}
        entry = decision(1)
        del entry['readme_sha256']
        def problems(identifier, value):
            errors = []
            reviews.validate_reviews([], {identifier: value}, errors, lead_batches=[{'leads': [lead]}], now=NOW)
            return errors
        self.assertEqual(problems(lead['id'], entry), [])
        self.assertIn('not a record', ' '.join(problems('lead-' + 'b' * 24, entry)))
        self.assertIn('missing or unknown fields', ' '.join(problems(lead['id'], {**entry, 'readme_sha256': 'a' * 64})))
        self.assertIn('missing or unknown fields', ' '.join(self.problems({capture(1)['id']: entry})))
        self.assertIn('precedes the lead observation', ' '.join(problems(lead['id'], {**entry, 'reviewed_at': '2026-11-01'})))

    def test_mixed_ids_sort_scan_numbers_then_leads(self):
        values = {'lead-' + 'b' * 24: {}, 'scan-10': {}, 'lead-' + 'a' * 24: {}, 'scan-2': {}}
        self.assertEqual(list(json.loads(reviews.dumps(values))),
                         ['scan-2', 'scan-10', 'lead-' + 'a' * 24, 'lead-' + 'b' * 24])
        self.assertEqual(reviews.dumps({'scan-10': {}, 'scan-2': {}}), '{\n  "scan-2": {},\n  "scan-10": {}\n}\n')

    def test_bad_decisions_are_named(self):
        identifier = capture(1)['id']
        cases = {
            'not a record': ({capture(2)['id']: decision(1)}, 'not a record in a discovery batch'),
            'unknown field': ({identifier: decision(1, extra='x')}, 'missing or unknown fields'),
            'decision': ({identifier: decision(1, decision='promote')}, 'decision must be exclude or hold'),
            'reason': ({identifier: decision(1, decision='hold', reason_code='unrelated')}, 'is not a hold reason'),
            'chinese': ({identifier: decision(1, reason_zh='English only')}, 'must contain Chinese text'),
            'hash': ({identifier: decision(1, readme_sha256='b' * 64)}, 'differs from the scanned snapshot'),
            'unpinned': ({identifier: decision(1, evidence_url='https://github.com/example/repo/blob/main/README.md')}, 'pinned to a commit'),
            'duplicate': ({identifier: decision(1, reason_code='duplicate-curated')}, 'duplicate_of goes with'),
            'stray duplicate': ({identifier: decision(1, duplicate_of='ghidra')}, 'duplicate_of goes with'),
            'list decision': ({identifier: decision(1, decision=['exclude'])}, 'decision must be exclude or hold'),
            'list reason': ({identifier: decision(1, reason_code=['unrelated'])}, 'is not a exclude reason'),
            'future': ({identifier: decision(1, reviewed_at='2026-12-01')}, 'in the future'),
            'early': ({identifier: decision(1, reviewed_at='2026-10-01')}, 'precedes the README scan'),
        }
        for name, (entries, expected) in cases.items():
            with self.subTest(name):
                self.assertTrue(any(expected in problem for problem in self.problems(entries)), self.problems(entries))

    def test_machine_class_decisions(self):
        identifier = capture(1)['id']
        batch = make_batch([capture(1)], run_id=100, ingested='2026-11-05T17:00:00Z')
        valid = {identifier: {'decision': 'data', 'class': 'game', 'reproduced': 'A game engine'},
                 'lead-' + 'a' * 24: {'decision': 'outside'},
                 'scan-9999999999': {'decision': 'outside'}}
        errors = []
        classes.validate_classes([batch], valid, errors)
        self.assertEqual(errors, [])
        cases = {
            'bad ID': ({'wrong': {'decision': 'outside'}}, 'invalid discovery ID'),
            'bad decision': ({identifier: {'decision': 'maybe'}}, 'decision must be data or outside'),
            'missing class': ({identifier: {'decision': 'data', 'reproduced': 'A game'}}, 'class must be exactly one'),
            'multiple classes': ({identifier: {'decision': 'data', 'class': ['game', 'apps'], 'reproduced': 'A game'}}, 'class must be exactly one'),
            'empty reproduced': ({identifier: {'decision': 'data', 'class': 'game', 'reproduced': '  '}}, 'reproduced must be nonempty'),
            'outside class': ({identifier: {'decision': 'outside', 'class': 'game'}}, 'unknown fields'),
            'outside reproduced': ({identifier: {'decision': 'outside', 'reproduced': 'A game'}}, 'unknown fields'),
            'extra': ({identifier: {'decision': 'data', 'class': 'game', 'reproduced': 'A game', 'extra': 1}}, 'unknown fields'),
        }
        for name, (rows, expected) in cases.items():
            with self.subTest(name):
                errors = []
                classes.validate_classes([batch], rows, errors)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_class_file_can_be_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(classes.read_classes(directory), {})


class QueueTest(unittest.TestCase):
    def test_decided_records_leave_the_list_and_are_exported_with_their_reasons(self):
        curated = {'id': 'curated-three', 'url': capture(3)['url'] + '/', 'kind': 'tool', 'name': 'Three'}
        with tempfile.TemporaryDirectory() as directory:
            queue = queue_with(directory, {capture(1)['id']: decision(1, decision='hold', reason_code='insufficient-docs')}, [curated])
        self.assertEqual([row['id'] for row in queue['listed']], [capture(2)['id']])
        self.assertEqual(queue['record_count'], 3)
        self.assertEqual(reviews.counts(queue['decided']), {'curated': 1, 'exclude': 0, 'hold': 1})
        export = reviews.export_document(queue['decided'], '2026-11-05T17:00:00Z')
        by_id = {row['id']: row for row in export['decisions']}
        self.assertEqual(by_id[capture(3)['id']]['curated_id'], 'curated-three')
        self.assertEqual(by_id[capture(1)['id']]['reason_code'], 'insufficient-docs')
        self.assertNotIn('readme_sha256', by_id[capture(1)['id']])

    def test_a_decision_stays_exported_after_the_record_enters_the_repository_index(self):
        root_entries = {capture(1)['id']: decision(1)}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / discoveries.DIRECTORY
            folder.mkdir(parents=True)
            batch = make_batch([capture(1), capture(2)], run_id=100, ingested='2026-11-05T17:00:00Z')
            (folder / f"{batch['batch_id']}.json").write_bytes(discoveries.batch_bytes(batch))
            (root / reviews.FILE).write_text(json.dumps(root_entries), encoding='utf-8')
            published = {'resources': [{'id': capture(1)['id'], 'full_name': capture(1)['full_name']}]}
            queue = site.discovery_queue(root, published, [], [])
        self.assertEqual(reviews.counts(queue['decided'])['exclude'], 1)
        self.assertEqual(queue['since_published'], 0)
        self.assertEqual([row['id'] for row in queue['listed']], [capture(2)['id']])

    def test_the_page_links_review_decisions(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = queue_with(directory, {capture(1)['id']: decision(1)})
        text = site.page_content(queue, 'en', False, 'https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA')
        self.assertIn('Data points: 0 listed, <span data-discovery-shown>0</span> shown here.', text)
        self.assertIn('/discoveries/reviews.json', text)

    def test_status_and_export_count_them(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = queue_with(directory, {capture(1)['id']: decision(1)})
        export = site.export_document(queue, 'https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA')
        self.assertEqual(export['counts']['reviewed'], {'curated': 0, 'exclude': 1, 'hold': 0})
        self.assertEqual(export['status']['reviewed'], export['counts']['reviewed'])
        self.assertEqual(export['counts']['listed'], 2)

    def test_the_scan_never_queues_a_decided_record_again(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            queue_with(directory, {capture(1)['id']: decision(1)})
            batches, _ = discoveries.load_batches(root)
            ids = {record['id'] for batch in batches for record in batch['resources']}
        self.assertIn(capture(1)['id'], ids)


if __name__ == '__main__':
    unittest.main()
