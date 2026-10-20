"""New scan IDs become deterministic review inputs; canonical locale shards are never written."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import locale_review_inputs as review
from locale_review_inputs import LOCALE_FILES, plan, write_inputs
from source_descriptions import capture_description


def record(number, description='Firmware unpacker'):
    return {'id': f'scan-{number}', 'full_name': f'example/tool-{number}', 'url': f'https://github.com/example/tool-{number}',
            'scan_status': 'readme-scanned', **capture_description(description)}


BASE = [record(10), record(20), record(30), record(40)]
SHARDS = {LOCALE_FILES[0]: {'scan-10': {}, 'scan-20': {}}, LOCALE_FILES[1]: {'scan-30': {}}, LOCALE_FILES[2]: {'scan-40': {}}}
NEW = [record(7), record(55, ''), record(60, 'x' * 1001), record(8), record(1000)]


def candidate(records, status='complete'):
    return {'meta': {'status': status}, 'resources': records}


class LocaleReviewInputTests(unittest.TestCase):
    def assigned_ids(self, records):
        return {filename: [row['id'] for row in rows]
                for filename, rows in plan(candidate(records), {'resources': BASE}, SHARDS).items()}

    def test_each_new_id_is_assigned_once_to_the_smallest_shard_in_numeric_order(self):
        expected = {LOCALE_FILES[0]: ['scan-55'], LOCALE_FILES[1]: ['scan-7', 'scan-60'], LOCALE_FILES[2]: ['scan-8', 'scan-1000']}
        self.assertEqual(self.assigned_ids(BASE + NEW), expected)
        shuffled = BASE + NEW
        random.Random(4).shuffle(shuffled)
        self.assertEqual(self.assigned_ids(shuffled), expected)
        for count in (0, 1, 11):
            ids = [value for values in self.assigned_ids(BASE + [record(100 + n) for n in range(count)]).values() for value in values]
            self.assertEqual(sorted(ids), sorted(f'scan-{100 + n}' for n in range(count)))

    def test_inconsistent_or_unfinished_inputs_are_refused(self):
        cases = [
            (candidate(BASE + NEW, 'in-progress'), SHARDS, 'complete scan'),
            (candidate(BASE[1:] + NEW), SHARDS, 'missing baseline records'),
            (candidate(BASE + [record(7), record(7)]), SHARDS, 'unique scan IDs'),
            (candidate(BASE + NEW), {**SHARDS, LOCALE_FILES[2]: {}}, 'cover exactly'),
            (candidate(BASE + NEW), {**SHARDS, LOCALE_FILES[2]: {'scan-40': {}, 'scan-10': {}}}, 'more than one'),
        ]
        for document, shards, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                plan(document, {'resources': BASE}, shards)
        with self.assertRaisesRegex(ValueError, 'duplicate keys'):
            review.parse(b'{"scan-1": {}, "scan-1": {}}', 'shard')

    def test_inputs_carry_source_evidence_only_and_the_manifest_binds_them(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'review'
            manifest = write_inputs(output, plan(candidate(BASE + NEW), {'resources': BASE}, SHARDS),
                                    candidate_sha256='c' * 64, baseline_sha256='b' * 64,
                                    shard_sha256={filename: 'a' * 64 for filename in LOCALE_FILES})
            files = {path.name: path.read_bytes() for path in output.iterdir()}
        self.assertEqual(manifest['inputs'], {name: hashlib.sha256(files[name]).hexdigest()
                                              for name in files if name != 'assignment-manifest.json'})
        self.assertEqual(json.loads(files['assignment-manifest.json']), manifest)
        self.assertEqual((manifest['new_ids'], manifest['translation_required']), (5, 3))
        entries = {entry['id']: entry for name, content in files.items() if name.startswith('review-')
                   for entry in json.loads(content)['entries']}
        self.assertEqual(sorted(entries), sorted(row['id'] for row in NEW))
        self.assertTrue(all('description_en' not in entry and 'description_zh' not in entry for entry in entries.values()))
        self.assertEqual((entries['scan-55']['translation_required'], entries['scan-60']['translation_required']), (False, False))
        self.assertEqual(entries['scan-60']['description_omission'], NEW[2]['description_omission'])
        self.assertEqual(json.loads(files['review-repositories-2.json'])['shard'], LOCALE_FILES[1])

    def test_command_leaves_baseline_shards_untouched_and_refuses_data_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            locales = root / 'locales'
            locales.mkdir()
            for filename, entries in SHARDS.items():
                (locales / Path(filename).name).write_text(json.dumps(entries))
            (root / 'base.json').write_text(json.dumps({'meta': {'status': 'complete'}, 'resources': BASE}))
            (root / 'next.json').write_text(json.dumps(candidate(BASE + NEW)))
            before = {path: path.read_bytes() for path in locales.iterdir()}
            arguments = ['--baseline', str(root / 'base.json'), '--baseline-locales', str(locales), '--candidate', str(root / 'next.json')]
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(review.main(arguments + ['--output', str(root / 'out')]), 0)
            self.assertEqual(json.loads(output.getvalue())['new_ids'], 5)
            self.assertEqual({path: path.read_bytes() for path in locales.iterdir()}, before)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(review.main(arguments + ['--output', str(ROOT / 'data/locales')]), 2)
            self.assertFalse((ROOT / 'data/locales/assignment-manifest.json').exists())

    def test_current_snapshot_against_its_own_revision_has_no_new_ids(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()) as output:
            with contextlib.redirect_stderr(io.StringIO()):
                code = review.main(['--baseline-ref', 'HEAD', '--candidate', str(ROOT / 'data/source-index.json'),
                                    '--output', directory])
            if code == 2:
                self.skipTest('git history is unavailable')
            manifest = json.loads((Path(directory) / 'assignment-manifest.json').read_text())
        self.assertEqual((code, json.loads(output.getvalue())['new_ids'], manifest['new_ids']), (0, 0, 0))


if __name__ == '__main__':
    unittest.main()
