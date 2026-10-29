"""Run admission through the trusted reviewer without executing contributor code."""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import review_pr
from test_review_pr import FakeGitHub, added, entry, run_review


class PublicSupplementReviewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = json.loads((ROOT / review_pr.SUPPLEMENT_BATCH).read_text())
        cls.archive_name = cls.batch['source']['archive_filename']
        cls.empty = next(row for row in cls.batch['resources'] if not row['description_en'])

    def trusted_base(self, directory):
        """A held, one-record base permits a small, real admission fixture."""
        root = Path(directory)
        for filename in review_pr.SOURCE_INPUTS:
            destination = root / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / filename, destination)
        archive = root / 'data/source-evidence' / self.archive_name
        archive.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / 'data/source-evidence' / self.archive_name, archive)
        batch = copy.deepcopy(self.batch)
        row = self.empty
        row_hash = hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True,
                                            separators=(',', ':')).encode()).hexdigest()
        batch.update(publication_status='held-for-localization', reviewed_at=None,
                     resources=[row])
        batch['selection'].update(selected_ids=[row['id']], selected_count=1,
                                  record_sha256={row['id']: row_hash})
        for filename, data in (
            (review_pr.SUPPLEMENT_INDEX, {'schema_version': 1, 'batches': [batch['batch_id']]}),
            (review_pr.SUPPLEMENT_BATCH, batch),
            (review_pr.SUPPLEMENT_SCOPE, {}),
        ):
            path = root / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data))
        return root, batch

    def admission(self, batch, *, locales=None, extra_files=()):
        ready = copy.deepcopy(batch)
        ready.update(publication_status='ready', reviewed_at=datetime.now(timezone.utc).isoformat())
        if locales is None:
            locales = {self.empty['id']: {'description_en': '', 'description_zh': ''}}
        contents = {review_pr.SUPPLEMENT_BATCH: json.dumps(ready),
                    review_pr.SUPPLEMENT_LOCALE: json.dumps(locales)}
        files = [entry(filename, added(raw), status='added' if filename == review_pr.SUPPLEMENT_LOCALE
                       else 'modified') for filename, raw in contents.items()]
        return FakeGitHub(files + list(extra_files), contents)

    def test_admission_reads_only_head_json_and_uses_trusted_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root, batch = self.trusted_base(directory)
            github = self.admission(batch, extra_files=[
                entry('scripts/public_source_supplements.py', added('raise RuntimeError("PR code")')),
            ])
            with patch.object(review_pr, 'ROOT', root):
                self.assertEqual(run_review(github)[0], 0)
            self.assertEqual(set(github.fetched()),
                             {review_pr.SUPPLEMENT_BATCH, review_pr.SUPPLEMENT_LOCALE})
            self.assertIn('1 selected records, 1 browsable additions', github.body())

    def test_incomplete_locale_or_capture_change_fails_with_head_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root, batch = self.trusted_base(directory)
            for attack in ('missing-locale', 'changed-capture', 'unknown-source'):
                with self.subTest(attack=attack):
                    github = self.admission(batch, locales={} if attack == 'missing-locale' else None)
                    document = json.loads(github.contents[review_pr.SUPPLEMENT_BATCH])
                    if attack == 'changed-capture':
                        document['resources'][0]['stars'] += 1
                    elif attack == 'unknown-source':
                        document['source']['archive_filename'] = 'untrusted.zip'
                    github.contents[review_pr.SUPPLEMENT_BATCH] = json.dumps(document)
                    with patch.object(review_pr, 'ROOT', root):
                        self.assertEqual(run_review(github)[0], 1)
                    self.assertIn('could not be validated against trusted-base capture evidence',
                                  github.body())

    def test_omitted_diff_and_decoded_private_locale_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root, batch = self.trusted_base(directory)
            github = self.admission(batch)
            github.files[1].pop('patch')
            with patch.object(review_pr, 'ROOT', root):
                self.assertEqual(run_review(github)[0], 0)
            self.assertIn(review_pr.SUPPLEMENT_LOCALE, github.fetched())
            github = self.admission(batch)
            # Assemble the sensitive fixture at runtime; do not commit a real path.
            private = ''.join(('\\u002f', 'home', '\\u002f', 'alice', '\\u002f', 'notes'))
            github.contents[review_pr.SUPPLEMENT_LOCALE] = (
                '{"' + self.empty['id'] + '":{"description_en":"' + private
                + '","description_zh":"说明"}}')
            github.files[1].pop('patch')
            with patch.object(review_pr, 'ROOT', root):
                self.assertEqual(run_review(github)[0], 1)
            self.assertIn('a decoded JSON string', github.body())
            self.assertNotIn('alice', github.body())

    def test_archive_and_unknown_locale_are_rejected_without_fetching_them(self):
        files = [
            entry('data/source-evidence/' + self.archive_name),
            entry(review_pr.SUPPLEMENT_LOCALE.replace('batch-01', 'batch-02'), added('{}')),
        ]
        github = FakeGitHub(files)
        self.assertEqual(run_review(github)[0], 1)
        self.assertEqual(github.fetched(), [])
        self.assertIn('immutable public source archives', github.body())
        self.assertIn('locale file is not in the trusted review allowlist', github.body())

    def test_renaming_trusted_archive_outside_evidence_is_blocked_without_fetch(self):
        github = FakeGitHub([
            entry('docs/evidence.bin', status='renamed',
                  previous_filename='data/source-evidence/' + self.archive_name),
        ])
        self.assertEqual(run_review(github)[0], 1)
        self.assertEqual(github.fetched(), [])
        self.assertIn('immutable public source archives', github.body())

    def test_unknown_locale_without_a_diff_is_not_fetched(self):
        github = FakeGitHub([
            entry(review_pr.SUPPLEMENT_LOCALE.replace('batch-01', 'batch-02')),
        ])
        self.assertEqual(run_review(github)[0], 1)
        self.assertEqual(github.fetched(), [])
        self.assertIn('locale file is not in the trusted review allowlist', github.body())

    def test_archive_renamed_to_allowlisted_json_is_not_fetched(self):
        github = FakeGitHub([
            entry(review_pr.SUPPLEMENT_SCOPE, status='renamed',
                  previous_filename='data/source-evidence/' + self.archive_name),
        ])
        self.assertEqual(run_review(github)[0], 1)
        self.assertEqual(github.fetched(), [])
        self.assertIn('a public archive change is not fetched as review data', github.body())

    def test_baseline_scope_change_revalidates_supplement_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = self.trusted_base(directory)
            held = copy.deepcopy(self.batch)
            held.update(publication_status='held-for-localization', reviewed_at=None)
            (root / review_pr.SUPPLEMENT_BATCH).write_text(json.dumps(held))
            shutil.copyfile(ROOT / review_pr.SUPPLEMENT_SCOPE, root / review_pr.SUPPLEMENT_SCOPE)
            baseline = json.loads((root / review_pr.SOURCE_INDEX).read_text())
            retained = next(r for r in baseline['resources'] if r['id'] == 'scan-1255951226')
            scope = json.loads((root / review_pr.SOURCE_SCOPE).read_text())
            scope[retained['id']] = {
                'decision': 'exclude', 'reason_code': 'outside-scope-fixture',
                'reason_en': 'A fixture exclusion of the previously retained entry.',
                'reason_zh': '测试中排除原来保留的条目。',
                'readme_sha256': retained['readme_sha256'],
                'evidence_url': retained['readme_url'], 'reviewed_at': '2026-10-20',
            }
            github = FakeGitHub([entry(review_pr.SOURCE_SCOPE, added('{}'))],
                                {review_pr.SOURCE_SCOPE: json.dumps(scope)})
            with patch.object(review_pr, 'ROOT', root):
                self.assertEqual(run_review(github)[0], 1)
            self.assertEqual(github.fetched(), [review_pr.SOURCE_SCOPE])
            self.assertIn('could not be validated against trusted-base capture evidence',
                          github.body())


if __name__ == '__main__':
    unittest.main()
