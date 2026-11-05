"""An evidence archive withdrawn at the maintainer's request is recorded, expected and never published."""
import copy
from datetime import date
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import public_source_supplements as supplements
import review_pr
from build_discovery_pages import _about_link_groups
from localization import localized_records
from test_review_pr import FakeGitHub, added, entry, run_review

BATCH_NAME = 'public-cloud-39323601991-batch-01'
BATCH = json.loads((ROOT / f'data/source-supplements/{BATCH_NAME}.json').read_text(encoding='utf-8'))
SOURCE = BATCH['source']
REGISTRY = 'data/source-evidence/withdrawn.json'
SELECTION = {'policy': 'strong-reverse-engineering-topics-v1', 'selected_ids': ['scan-1'], 'selected_count': 1,
             'record_sha256': {'scan-1': 'b' * 64}}


def withdrawal(**changes):
    """The withdrawal of the real batch's archive, by its recorded run, digest and size."""
    item = {'archive_filename': SOURCE['archive_filename'], 'artifact_digest': SOURCE['artifact']['digest'],
            'run_id': SOURCE['run']['id'], 'run_attempt': SOURCE['run']['run_attempt'],
            'size_in_bytes': SOURCE['artifact']['size_in_bytes'],
            'batch_selection_sha256': {BATCH_NAME: supplements.digest(BATCH['selection'])}, 'withdrawn_at': '2026-11-05',
            'reason': 'Withdrawn at the maintainer’s request.', 'reason_zh': '应维护者要求撤回。'}
    item.update(changes)
    return item


def registry(*entries):
    return supplements.json_bytes({'schema_version': 1, 'withdrawn': list(entries) or [withdrawal()]})


def one_record_batch():
    """The real batch narrowed to its one record without a description, ready for publication."""
    batch = copy.deepcopy(BATCH)
    record = next(row for row in batch['resources'] if not row['description_en'])
    batch.update(publication_status='ready', reviewed_at='2026-10-20T00:00:00Z', resources=[record])
    batch['selection'].update(selected_ids=[record['id']], selected_count=1,
                              record_sha256={record['id']: supplements.digest(record)})
    return batch


def fixture(directory, *, withdrawn=True, archive=False, batch=None, anchored=None):
    """The real baseline and one ready record of the real batch, its archive withdrawn unless told otherwise.
    The withdrawal fixes the selection of `anchored` (the written batch by default)."""
    root = Path(directory)
    batch = batch or one_record_batch()
    record = batch['resources'][0]
    scope = json.loads((ROOT / f'data/source-supplements/{BATCH_NAME}.scope.json').read_text(encoding='utf-8'))
    files = {
        'data/source-index.json': (ROOT / 'data/source-index.json').read_bytes(),
        'data/source-scope.json': (ROOT / 'data/source-scope.json').read_bytes(),
        'data/source-supplements/index.json': supplements.json_bytes({'schema_version': 1, 'batches': [BATCH_NAME]}),
        f'data/source-supplements/{BATCH_NAME}.json': supplements.json_bytes(batch),
        f'data/locales/source-supplements/{BATCH_NAME}.json': supplements.json_bytes(
            {record['id']: {'description_en': '', 'description_zh': ''}}),
        f'data/source-supplements/{BATCH_NAME}.scope.json': supplements.json_bytes(
            {key: value for key, value in scope.items() if key == record['id']}),
    }
    if withdrawn:
        files[REGISTRY] = registry(withdrawal(batch_selection_sha256={
            BATCH_NAME: supplements.digest((anchored or batch)['selection'])}))
    if archive:
        files['data/source-evidence/' + SOURCE['archive_filename']] = b'archive bytes'
    for name, raw in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return root, batch


class WithdrawalRegistryTests(unittest.TestCase):
    def test_an_entry_is_read_by_archive_name_and_must_match_the_source_citing_it(self):
        entries = supplements.parse_withdrawals(registry())
        self.assertEqual(entries, {SOURCE['archive_filename']: withdrawal()})
        self.assertEqual(supplements.withdrawal_for(SOURCE, entries), withdrawal())
        self.assertIsNone(supplements.withdrawal_for(SOURCE, {}))
        for changes in ({'size_in_bytes': SOURCE['artifact']['size_in_bytes'] + 1},
                        {'artifact_digest': SOURCE['artifact']['digest'][:-1] + '0'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                supplements.withdrawal_for(SOURCE, {SOURCE['archive_filename']: withdrawal(**changes)})

    def test_entries_name_their_run_and_digest_and_give_a_dated_bilingual_reason(self):
        name = SOURCE['archive_filename']
        for changes in ({'archive_filename': name.replace('run-', 'Run-')},
                        {'artifact_digest': 'sha256:' + '0' * 64},
                        {'run_id': SOURCE['run']['id'] + 1}, {'run_attempt': 2}, {'size_in_bytes': 0},
                        {'batch_selection_sha256': []}, {'batch_selection_sha256': {BATCH_NAME: 'x'}},
                        {'batch_selection_sha256': {'Bad Name': 'a' * 64}},
                        {'withdrawn_at': '2026-11-5'}, {'withdrawn_at': '2999-01-01'}, {'withdrawn_at': None},
                        {'reason': ''}, {'reason': 'Two\nlines'}, {'reason_zh': 'English only'}, {'note': 'extra'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                supplements.parse_withdrawals(registry(withdrawal(**changes)), today=date(2026, 11, 5))
        missing = withdrawal()
        del missing['reason_zh']
        for document in ({'schema_version': 1, 'withdrawn': []}, {'schema_version': 2, 'withdrawn': [withdrawal()]},
                         {'schema_version': 1, 'withdrawn': [withdrawal(), withdrawal()]},
                         {'schema_version': 1, 'withdrawn': [missing]}):
            with self.subTest(document=document), self.assertRaises(ValueError):
                supplements.parse_withdrawals(supplements.json_bytes(document), today=date(2026, 11, 5))
        # A withdrawal may be dated up to the next UTC day.
        self.assertTrue(supplements.parse_withdrawals(registry(withdrawal(withdrawn_at='2026-11-06')),
                                                      today=date(2026, 11, 5)))

    def test_a_withdrawn_archive_may_not_stay_in_the_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root, _ = fixture(directory, archive=True)
            with self.assertRaises(ValueError):
                supplements.read_withdrawals(root)
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(supplements.read_withdrawals(Path(directory)), {})


class WithdrawnEvidenceTests(unittest.TestCase):
    def test_withdrawn_evidence_loads_nothing_and_cannot_back_a_new_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            root, batch = fixture(directory)
            self.assertIsNone(supplements.load_evidence(root, SOURCE))
            with self.assertRaises(ValueError):
                supplements.prepare_batch(root, 'new-batch', SOURCE, batch['selection']['selected_ids'])

    def test_batches_still_check_their_own_records_ids_and_fingerprints(self):
        baseline_bytes = (ROOT / 'data/source-index.json').read_bytes()
        baseline, baseline_sha = json.loads(baseline_bytes), hashlib.sha256(baseline_bytes).hexdigest()
        supplements.validate_batch(BATCH, baseline, baseline_sha, None)
        changed = copy.deepcopy(BATCH)
        changed['resources'][0]['description_en'] = 'A different claim.'
        with self.assertRaises(ValueError):
            supplements.validate_batch(changed, baseline, baseline_sha, None)
        changed = copy.deepcopy(BATCH)
        changed['selection']['selected_ids'] = list(reversed(changed['selection']['selected_ids']))
        with self.assertRaises(ValueError):
            supplements.validate_batch(changed, baseline, baseline_sha, None)

    def test_a_batch_cannot_change_its_selection_once_its_evidence_is_withdrawn(self):
        original = one_record_batch()
        changed = copy.deepcopy(original)
        changed['resources'][0]['description_en'] = 'A different claim.'
        changed['selection']['record_sha256'] = {row['id']: supplements.digest(row) for row in changed['resources']}
        with tempfile.TemporaryDirectory() as directory:
            root, _ = fixture(directory, batch=changed, anchored=original)
            with self.assertRaisesRegex(ValueError, 'withdrawn'):
                supplements.load_supplements(root)
        with tempfile.TemporaryDirectory() as directory:
            root, _ = fixture(directory, batch=original)
            self.assertEqual(len(supplements.load_supplements(root)['records']), 1)

    def test_publication_lists_the_withdrawal_instead_of_an_archive_and_copies_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root, batch = fixture(directory)
            ready = supplements.load_supplements(root)
            self.assertEqual(ready['withdrawals'], {SOURCE['archive_filename']: withdrawal(
                batch_selection_sha256={BATCH_NAME: supplements.digest(batch['selection'])})})
            document = supplements.compose_published(
                (ROOT / 'data/source-index.json').read_bytes(), ready['baseline_sha256'], ready,
                localized_records(ready['records'], ready['locales']))
            source = document['meta']['capture_sources'][0]
            self.assertIsNone(source['archive_url'])
            self.assertEqual(source['archive_withdrawal'], {'withdrawn_at': '2026-11-05', 'reason': withdrawal()['reason'],
                                                            'reason_zh': withdrawal()['reason_zh']})
            self.assertEqual((source['artifact'], source['files'], source['run']),
                             (SOURCE['artifact'], SOURCE['files'], SOURCE['run']))
            # The document must be self-consistent; validate_site also recomposes it from the data and compares.
            for mutate in (lambda item: item.update(archive_url='/evidence/source-scans/' + SOURCE['archive_filename']),
                           lambda item: item['archive_withdrawal'].update(note='extra'),
                           lambda item: item['archive_withdrawal'].pop('reason_zh'),
                           lambda item: item.pop('archive_withdrawal')):
                changed = copy.deepcopy(document)
                mutate(changed['meta']['capture_sources'][0])
                with self.subTest(), self.assertRaises(ValueError):
                    supplements.validate_published_document(changed)
            supplements.copy_public_evidence(root, root / 'output', ready)
            self.assertFalse((root / 'output').exists())

    def test_every_withdrawn_archive_redirects_to_its_listing_whatever_its_batches_state(self):
        # The rules come from the registry alone, so a batch moved back to held changes nothing here.
        withdrawals = {SOURCE['archive_filename']: withdrawal()}
        run = SOURCE['run']['id']
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / '_redirects').write_text('/curated/ /resources/ 301', encoding='utf-8')
            supplements.write_withdrawn_redirects(output, withdrawals)
            self.assertEqual((output / '_redirects').read_text(encoding='utf-8').splitlines(), [
                '/curated/ /resources/ 301',
                "# Scan evidence withdrawn at the maintainer's request: listed on /about/, not served.",
                f"/evidence/source-scans/{SOURCE['archive_filename']} /about/#scan-evidence-{run}-1 301",
                '/evidence/source-scans/ /about/#about-links-download 301',
                '/evidence/source-scans /about/#about-links-download 301'])
        with tempfile.TemporaryDirectory() as directory:
            # While another archive is still served, the directory itself keeps working.
            output = Path(directory)
            (output / 'evidence/source-scans').mkdir(parents=True)
            supplements.write_withdrawn_redirects(output, withdrawals)
            self.assertNotIn('/evidence/source-scans/ ', (output / '_redirects').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as directory:
            supplements.write_withdrawn_redirects(Path(directory), {})
            self.assertFalse((Path(directory) / '_redirects').exists())

    def test_about_lists_every_withdrawn_run_once_without_a_download(self):
        run = SOURCE['run']['id']
        withdrawals = {SOURCE['archive_filename']: withdrawal()}
        published = {'meta': {'capture_sources': [supplements.source_descriptor(SOURCE, withdrawal())]}}
        with tempfile.TemporaryDirectory() as directory:
            for language, text in (('en', f'Original scan evidence (run {run}) was withdrawn on 2026-11-05'),
                                   ('zh', f'原始扫描证据（运行 {run}）已于 2026-11-05 撤回')):
                # Listed whether its batch is published (ready) or not (held), and only once.
                for index, is_published in ((published, True), (None, False)):
                    html = _about_link_groups(Path(directory), language, 'https://github.com/reacher-z/Awesome-REA',
                                              index, 'source-published.json', is_published, withdrawals)
                    self.assertEqual(html.count(f'id="scan-evidence-{run}-1"'), 1)
                    self.assertIn(f'<span id="scan-evidence-{run}-1" class="about-withdrawn">{text}', html)
                    self.assertNotIn('/evidence/source-scans/', html)


class WithdrawalReviewTests(unittest.TestCase):
    """The trusted reviewer admits deleting an archive only with a new withdrawal naming its exact bytes."""

    def base(self, directory, raw=b'original archive bytes', *, listed=False):
        digest = hashlib.sha256(raw).hexdigest()
        name = f'run-123-attempt-1-{digest[:12]}.zip'
        item = {'archive_filename': name, 'artifact_digest': 'sha256:' + digest, 'run_id': 123, 'run_attempt': 1,
                'size_in_bytes': len(raw), 'batch_selection_sha256': {'example-batch': supplements.digest(SELECTION)},
                'withdrawn_at': '2026-11-05', 'reason': 'Withdrawn at the maintainer’s request.',
                'reason_zh': '应维护者要求撤回。'}
        evidence = Path(directory) / 'data/source-evidence'
        evidence.mkdir(parents=True)
        # One registered batch cites the archive; its selection is what the withdrawal must fix.
        batches = Path(directory) / 'data/source-supplements'
        batches.mkdir(parents=True)
        (batches / 'index.json').write_text(json.dumps({'schema_version': 1, 'batches': ['example-batch']}))
        (batches / 'example-batch.json').write_text(json.dumps({'source': {'archive_filename': name}, 'selection': SELECTION}))
        if listed:
            (evidence / 'withdrawn.json').write_bytes(registry(item))
        else:
            (evidence / name).write_bytes(raw)
        return 'data/source-evidence/' + name, item

    def review(self, root, files, contents=None):
        github = FakeGitHub(files, contents or {})
        with patch.object(review_pr, 'ROOT', root):
            status = run_review(github)[0]
        return status, github.body()

    def test_a_new_withdrawal_admits_removing_exactly_its_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            path, item = self.base(directory)
            files = [entry(path, status='removed'), entry(REGISTRY, added('{}'), status='added')]
            status, body = self.review(Path(directory), files, {REGISTRY: registry(item).decode()})
            self.assertEqual(status, 0, body)
            self.assertIn('withdrawn by their exact trusted-base digest', body)

    def test_a_removal_without_its_exact_withdrawal_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path, item = self.base(directory)
            for files, contents in (
                ([entry(path, status='removed')], {}),
                ([entry(path, status='removed'), entry(REGISTRY, added('{}'), status='added')],
                 {REGISTRY: registry({**item, 'size_in_bytes': item['size_in_bytes'] + 1}).decode()}),
                ([entry(REGISTRY, added('{}'), status='added')], {REGISTRY: registry(item).decode()}),
                ([entry(path), entry(REGISTRY, added('{}'), status='added')], {REGISTRY: registry(item).decode()}),
                ([entry(path, status='removed'), entry(REGISTRY, added('{}'), status='added')], {REGISTRY: '{"schema_version": 1}'}),
                # A withdrawal cannot fix a selection other than the default branch's.
                ([entry(path, status='removed'), entry(REGISTRY, added('{}'), status='added')],
                 {REGISTRY: registry({**item, 'batch_selection_sha256': {'example-batch': 'c' * 64}}).decode()}),
                ([entry(path, status='removed'), entry(REGISTRY, added('{}'), status='added')],
                 {REGISTRY: registry({**item, 'batch_selection_sha256': {}}).decode()}),
            ):
                with self.subTest(files=[(change['filename'], change['status']) for change in files]):
                    status, _ = self.review(Path(directory), files, contents)
                    self.assertEqual(status, 1)

    def test_existing_withdrawals_cannot_change_disappear_or_bring_their_archive_back(self):
        with tempfile.TemporaryDirectory() as directory:
            path, item = self.base(directory, listed=True)
            for files, contents in (
                ([entry(REGISTRY, added('{}'))], {REGISTRY: registry({**item, 'withdrawn_at': '2026-11-04'}).decode()}),
                ([entry(REGISTRY, status='removed')], {}),
                ([entry(path, added('x'), status='added')], {}),
            ):
                with self.subTest(files=[(change['filename'], change['status']) for change in files]):
                    status, _ = self.review(Path(directory), files, contents)
                    self.assertEqual(status, 1)


if __name__ == '__main__':
    unittest.main()
