"""Public evidence membership, publication holds and truthful export boundaries."""
import copy
from contextlib import redirect_stdout
import functools
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import public_source_supplements as supplements
from localization import localized_records, read_localizations
from source_scope import apply_scope, read_scope
from source_browser import project_source_browser, validate_source_browser, compact_json_bytes

BATCH_NAME = 'public-cloud-39323601991-batch-01'


def reuses_class_evidence(test):
    """Serve the full evidence re-check from setUpClass to calls with the same source and archive bytes.

    Each decorated test checks an unchanged regular-file copy of the checked-in archive, so load_evidence
    would repeat the identical multi-second check. Such a call gets its own deep copy of the class result;
    any other source or archive still goes through the real load_evidence.
    """
    @functools.wraps(test)
    def run(self):
        check = supplements.load_evidence

        def load(root, source):
            archive = Path(root) / 'data/source-evidence' / source['archive_filename']
            if (source == self.source and archive.is_file() and not archive.is_symlink()
                    and archive.read_bytes() == self.archive):
                return copy.deepcopy(self.evidence)
            return check(root, source)
        with patch.object(supplements, 'load_evidence', load):
            return test(self)
    return run


class PublicSourceSupplementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline_bytes = (ROOT / 'data/source-index.json').read_bytes()
        cls.baseline = json.loads(cls.baseline_bytes)
        cls.baseline_sha = hashlib.sha256(cls.baseline_bytes).hexdigest()
        cls.batch = json.loads((ROOT / f'data/source-supplements/{BATCH_NAME}.json').read_text())
        cls.source = cls.batch['source']
        cls.archive = (ROOT / 'data/source-evidence' / cls.source['archive_filename']).read_bytes()
        cls.evidence = supplements.load_evidence(ROOT, cls.source)
        cls.empty_record = next(row for row in cls.batch['resources'] if not row['description_en'])
        cls.baseline_scope_bytes = (ROOT / 'data/source-scope.json').read_bytes()
        cls.batch_scope = json.loads((ROOT / f'data/source-supplements/{BATCH_NAME}.scope.json').read_text())

    def fixture(self, directory, *, ready=False, count=None, record=None, translations=None):
        root = Path(directory)
        batch = copy.deepcopy(self.batch)
        batch.update(publication_status='held-for-localization', reviewed_at=None)
        if count == 1:
            selected = record or self.empty_record
            batch['resources'] = [copy.deepcopy(selected)]
            batch['selection'].update(
                selected_ids=[selected['id']], selected_count=1,
                record_sha256={selected['id']: supplements.digest(selected)})
        if ready:
            batch.update(publication_status='ready', reviewed_at='2026-10-20T00:00:00Z')
        files = {
            'data/source-index.json': self.baseline_bytes,
            'data/source-scope.json': self.baseline_scope_bytes,
            'data/source-evidence/' + self.source['archive_filename']: self.archive,
            'data/source-supplements/index.json': supplements.json_bytes({'schema_version': 1, 'batches': [BATCH_NAME]}),
            f'data/source-supplements/{BATCH_NAME}.json': supplements.json_bytes(batch),
            f'data/locales/source-supplements/{BATCH_NAME}.json': supplements.json_bytes(translations if translations is not None else {
                row['id']: {'description_en': '', 'description_zh': ''}
                for row in batch['resources'] if not row['description_en']}),
            f'data/source-supplements/{BATCH_NAME}.scope.json': supplements.json_bytes({
                identifier: value for identifier, value in self.batch_scope.items()
                if identifier in batch['selection']['selected_ids']}),
        }
        for name, raw in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        return root

    def canonical_export(self):
        document = copy.deepcopy(self.baseline)
        document['resources'] = apply_scope(
            localized_records(document['resources'], read_localizations(ROOT)), read_scope(ROOT))
        excluded = sum(row.get('scope_status') == 'excluded' for row in document['resources'])
        document['meta']['scope'] = {
            'scanned_count': len(document['resources']), 'excluded_count': excluded,
            'browse_count': len(document['resources']) - excluded,
        }
        return supplements.json_bytes(document)

    @reuses_class_evidence
    def test_real_500_are_held_without_fake_translations(self):
        # The missing-language fixture remains held even after real translations
        # are reviewed and the actual batch is admitted in a later data change.
        with tempfile.TemporaryDirectory() as directory:
            actual = supplements.load_supplements(self.fixture(directory))
            self.assertEqual(actual['records'], [])
            self.assertEqual(actual['ready'], [])
            self.assertEqual(actual['held'], [{'batch_id': BATCH_NAME, 'selected_count': 500,
                                              'missing_localizations': 495}])
        self.assertEqual((ROOT / 'data/source-index.json').read_bytes(), self.baseline_bytes)
        self.assertEqual(self.source['raw_counts']['successful_readme_scans'], 12211)
        self.assertEqual(self.source['integrity_counts'], {
            'qualified': 9194, 'legacy_unknown': 2999, 'mismatched': 18})
        self.assertTrue(all(row['readme_git_sha_matches_content'] is True for row in self.batch['resources']))

    @reuses_class_evidence
    def test_held_candidate_is_reproducible_from_exact_public_ids(self):
        prepared = supplements.prepare_batch(ROOT, BATCH_NAME, self.source,
                                             self.batch['selection']['selected_ids'])
        expected = {**self.batch, 'publication_status': 'held-for-localization', 'reviewed_at': None}
        self.assertEqual(prepared, expected)

    def test_rehashed_row_mutation_and_identity_changes_fail_membership(self):
        for change in (
            lambda batch: batch['resources'][0].update(description_en='A different claim.'),
            lambda batch: batch['resources'][0].update(id='scan-999999999999'),
            lambda batch: batch['resources'].append(copy.deepcopy(batch['resources'][0])),
        ):
            with self.subTest(change=change):
                batch = copy.deepcopy(self.batch)
                change(batch)
                batch['selection'] = {
                    'policy': 'strong-reverse-engineering-topics-v1',
                    'selected_ids': [row['id'] for row in batch['resources']],
                    'record_sha256': {row['id']: supplements.digest(row) for row in batch['resources']},
                    'selected_count': len(batch['resources']),
                }
                with self.assertRaises(ValueError):
                    supplements.validate_batch(batch, self.baseline, self.baseline_sha, self.evidence)

    def test_qualification_is_required_even_with_matching_source_object(self):
        batch, evidence = copy.deepcopy(self.batch), copy.deepcopy(self.evidence)
        row = batch['resources'][0]
        row['readme_git_sha_matches_content'] = False
        evidence['resources'] = [row if original['id'] == row['id'] else original
                                 for original in evidence['resources']]
        batch['selection']['record_sha256'][row['id']] = supplements.digest(row)
        with self.assertRaisesRegex(ValueError, 'qualified'):
            supplements.validate_batch(batch, self.baseline, self.baseline_sha, evidence)

    def test_source_pin_and_semantic_capture_bindings_fail_closed(self):
        source = copy.deepcopy(self.source)
        source['artifact']['id'] += 1
        with self.assertRaisesRegex(ValueError, 'Unapproved'):
            supplements.load_evidence(ROOT, source)
        source = copy.deepcopy(self.source)
        source['snapshot_status'] = 'in-progress'
        with patch.object(supplements, 'APPROVED_SOURCE_DESCRIPTORS', {supplements.digest(source)}):
            with self.assertRaisesRegex(ValueError, 'capture status'):
                supplements.load_evidence(ROOT, source)
        source = copy.deepcopy(self.source)
        source['raw_counts']['failed'] += 1
        source['raw_counts']['attempted_readme_scans'] += 1
        source['raw_counts']['unique_repos'] += 1
        with patch.object(supplements, 'APPROVED_SOURCE_DESCRIPTORS', {supplements.digest(source)}):
            with self.assertRaisesRegex(ValueError, 'Full source counts'):
                supplements.load_evidence(ROOT, source)

    def test_full_three_member_privacy_including_unselected_records(self):
        with zipfile.ZipFile(io.BytesIO(self.archive)) as archive:
            originals = {name: archive.read(name) for name in archive.namelist()}
        private_text = '/' + 'Users' + '/synthetic-person/private-input.txt'
        for changed_name in ('checkpoint.json', 'frontier.json', 'receipt.json'):
            with self.subTest(member=changed_name), tempfile.TemporaryDirectory() as directory:
                members = dict(originals)
                value = json.loads(members[changed_name])
                if changed_name == 'checkpoint.json':
                    self.assertNotIn(value['resources'][-1]['id'], self.batch['selection']['selected_ids'])
                    value['resources'][-1]['description_en'] = private_text
                else:
                    value['unapproved_debug_path'] = private_text
                members[changed_name] = supplements.json_bytes(value)
                receipt = json.loads(members['receipt.json'])
                for name in ('checkpoint.json', 'frontier.json'):
                    receipt['files'][name] = {'sha256': hashlib.sha256(members[name]).hexdigest(),
                                              'bytes': len(members[name])}
                receipt['checkpoint_sha256'] = receipt['files']['checkpoint.json']['sha256']
                members['receipt.json'] = supplements.json_bytes(receipt)
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                    for name, raw in members.items():
                        archive.writestr(name, raw)
                raw = buffer.getvalue()
                source = copy.deepcopy(self.source)
                source['files'] = {name: {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
                                   for name, content in members.items()}
                source['artifact'].update(digest='sha256:' + hashlib.sha256(raw).hexdigest(),
                                          size_in_bytes=len(raw))
                source['archive_filename'] = (
                    f'run-{source["run"]["id"]}-attempt-{source["run"]["run_attempt"]}-'
                    f'{source["artifact"]["digest"][7:19]}.zip')
                path = Path(directory) / 'data/source-evidence' / source['archive_filename']
                path.parent.mkdir(parents=True)
                path.write_bytes(raw)
                with patch.object(supplements, 'APPROVED_SOURCE_DESCRIPTORS', {supplements.digest(source)}):
                    with self.assertRaisesRegex(ValueError, 'privacy'):
                        supplements.load_evidence(Path(directory), source)

    def test_file_bounds_and_symlinked_parent_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            (root / 'data/source-evidence').symlink_to(ROOT / 'data/source-evidence', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                supplements.load_evidence(root, self.source)
            large = root / 'bounded-input'
            large.write_bytes(b'123456789')
            with self.assertRaisesRegex(ValueError, 'byte bound'):
                supplements.bounded_bytes(large, 8)

    def test_prepare_output_parent_traversal_cannot_loop_or_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory, count=1)
            (root / '.cache').mkdir()
            (root / 'other').mkdir()
            bad = root / 'other/../.cache/prepared.json'
            self.assertEqual(bad.resolve(), root.resolve() / '.cache/prepared.json')
            with self.assertRaisesRegex(ValueError, 'parent traversal'):
                supplements.cache_output(root, bad)
            ids = root / 'ids.json'
            ids.write_text(json.dumps([self.empty_record['id']]))
            result = subprocess.run([
                sys.executable, str(ROOT / 'scripts/public_source_supplements.py'),
                '--root', str(root), '--prepare-batch', 'fixture-next',
                '--source-batch', BATCH_NAME, '--ids', str(ids), '--output', str(bad),
            ], timeout=5, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 1)
            self.assertFalse((root / '.cache/prepared.json').exists())
            normal = root / '.cache/prepared.json'
            self.assertEqual(supplements.cache_output(root, normal), normal.resolve())
            (root / '.cache/alias').symlink_to(root / '.cache', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                supplements.cache_output(root, root / '.cache/alias/prepared.json')

    @reuses_class_evidence
    def test_missing_translation_cannot_be_published(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory, ready=True)
            with self.assertRaisesRegex(ValueError, 'complete bilingual coverage'):
                supplements.load_supplements(root)

    def test_duplicate_scope_uses_visible_baseline_without_reclassifying_it(self):
        context = apply_scope(self.baseline['resources'], json.loads(self.baseline_scope_bytes))
        before = copy.deepcopy(context)
        projected = supplements.apply_supplement_scope(
            self.batch['resources'], self.batch_scope, context)
        self.assertEqual(context, before)
        self.assertEqual([row['id'] for row in projected], self.batch['selection']['selected_ids'])
        self.assertEqual(sum(row.get('scope_status') == 'excluded' for row in projected), 26)
        self.assertEqual(len(projected), 500)
        visible_baseline = sum(row.get('scope_status') != 'excluded' for row in context)
        self.assertEqual(visible_baseline + len(projected) - 26, 3309)
        first_id = next(iter(self.batch_scope))
        decision = self.batch_scope[first_id]
        cited = next(iter(set(__import__('re').findall(
            supplements.SOURCE_ID_MENTION, decision['reason_en']))))
        with self.assertRaisesRegex(ValueError, 'only its distinct new IDs'):
            supplements.apply_supplement_scope(
                self.batch['resources'], {cited: decision}, context)
        for field, value, message in (
            ('scope_status', 'excluded', 'remain visible'),
            ('readme_sha256', 'f' * 64, 'source-context'),
            ('full_name', 'Example/different-name', 'same repository name'),
        ):
            changed = copy.deepcopy(context)
            next(row for row in changed if row['id'] == cited)[field] = value
            with self.assertRaisesRegex(ValueError, message):
                supplements.apply_supplement_scope(self.batch['resources'], self.batch_scope, changed)
        changed_scope = copy.deepcopy(self.batch_scope)
        changed_scope[first_id]['reason_en'] = decision['reason_en'].replace(cited, 'scan-999999999999')
        changed_scope[first_id]['reason_zh'] = decision['reason_zh'].replace(cited, 'scan-999999999999')
        with self.assertRaisesRegex(ValueError, 'source-context'):
            supplements.apply_supplement_scope(self.batch['resources'], changed_scope, context)

    @reuses_class_evidence
    def test_ready_empty_description_and_separate_publication_semantics(self):
        # This real source has no description. Empty EN/ZH strings are correct,
        # unlike invented translations for any of the other 495 descriptions.
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory, ready=True, count=1)
            ready = supplements.load_supplements(root)
            additions = localized_records(ready['records'], ready['locales'])
            original = self.canonical_export()
            published = supplements.compose_published(original, self.baseline_sha, ready, additions)
            self.assertEqual(published['resources'][:3000], json.loads(original)['resources'])
            self.assertEqual(published['meta']['canonical_capture']['counts'],
                             supplements.raw_counts(self.baseline))
            self.assertEqual(published['meta']['capture_sources'][0]['raw_counts'],
                             self.source['raw_counts'])
            self.assertEqual(published['meta']['scope']['scanned_count'], 3001)
            self.assertNotIn('current_run', published['meta'])
            self.assertNotIn('completed_at', published['meta'])
            self.assertNotIn('attempted_readme_scans', published['meta'])
            raw = supplements.json_bytes(published)
            browser = project_source_browser(raw)
            self.assertEqual(browser['meta']['schema_version'], 2)
            self.assertEqual(browser['meta']['full_export'], 'source-published.json')
            self.assertEqual(browser['meta']['full_export_sha256'], hashlib.sha256(raw).hexdigest())
            self.assertNotIn('capture_sources', browser['meta'])
            validate_source_browser(raw, compact_json_bytes(browser))
            changed = copy.deepcopy(browser)
            changed['meta']['full_export'] = 'source-index.json'
            with self.assertRaises(ValueError):
                validate_source_browser(raw, compact_json_bytes(changed))
            for mutate in (
                lambda doc: doc['meta'].update(completed_at='2026-10-20T00:00:00Z'),
                lambda doc: doc['meta'].update(status='complete'),
                lambda doc: doc['meta'].update(canonical_export='https://example.com/data.json'),
                lambda doc: doc['meta']['scope'].update(browse_count=5000),
                lambda doc: doc['resources'][-1].update(readme_git_sha_matches_content=False),
            ):
                changed = copy.deepcopy(published)
                mutate(changed)
                with self.assertRaises(ValueError):
                    project_source_browser(supplements.json_bytes(changed))
            supplements.copy_public_evidence(root, root / 'output', ready)
            copied = root / 'output/evidence/source-scans' / self.source['archive_filename']
            self.assertEqual(copied.read_bytes(), self.archive)
            self.assertEqual(original, self.canonical_export())

    @reuses_class_evidence
    def test_composition_preserves_capture_fields_but_allows_faithful_locale_and_labels(self):
        from artifact_links import with_curated_labels
        with tempfile.TemporaryDirectory() as directory:
            record = self.batch['resources'][0]
            chinese, marker, english = record['description_en'].partition('An agent skill')
            self.assertTrue(marker and chinese)
            translations = {record['id']: {
                'description_en': marker + english,
                'description_zh': chinese,
            }}
            root = self.fixture(directory, ready=True, count=1, record=record, translations=translations)
            admitted = supplements.load_supplements(root)
            localized = localized_records(admitted['records'], admitted['locales'])
            baseline = self.canonical_export()
            published = supplements.compose_published(baseline, self.baseline_sha, admitted, localized)
            self.assertEqual(published['resources'][-1]['description_original'], record['description_en'])
            self.assertEqual(published['resources'][-1]['description_en'], marker + english)
            self.assertEqual(published['resources'][-1]['description_zh'], chinese)
            labeled = with_curated_labels(localized, [{
                'id': 'fixture-reviewed-tool', 'url': record['url'], 'verification': 'source-reviewed',
                'targets': ['protocol'], 'category': 'protocol-analysis',
            }])
            supplements.compose_published(baseline, self.baseline_sha, admitted, labeled)
            for mutate in (
                lambda row: row.update(full_name='Different/identity'),
                lambda row: row.update(observed_at='2026-10-20T00:00:00Z'),
                lambda row: row.update(readme_sha256='f' * 64),
                lambda row: row.update(readme_git_sha='f' * 40, readme_content_git_sha='f' * 40),
                lambda row: row.update(description_en='An unsupported replacement.'),
                lambda row: row.update(description_original='A changed upstream description.'),
                lambda row: row.update(topics=['different-topic']),
                lambda row: row.update(unapproved_new_field='extra'),
            ):
                changed = copy.deepcopy(localized)
                mutate(changed[0])
                with self.assertRaises(ValueError):
                    supplements.compose_published(baseline, self.baseline_sha, admitted, changed)

    @reuses_class_evidence
    def test_ready_build_routes_and_curated_machine_boundary(self):
        import build_site
        import validate_site
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            root = self.fixture(directory / 'input', ready=True, count=1)
            ready = supplements.load_supplements(root)
            output = directory / 'site'
            with patch.object(build_site, 'load_supplements', return_value=ready), redirect_stdout(io.StringIO()):
                build_site.build_site(output)
            self.assertTrue((output / 'source-index.json').is_file())
            publication = json.loads((output / 'source-published.json').read_text())
            self.assertEqual(len(publication['resources']), 3001)
            self.assertEqual(publication['meta']['canonical_capture']['counts'],
                             supplements.raw_counts(self.baseline))
            validate_site.validate_source_browser_output(output)
            with patch.object(validate_site, 'OUTPUT', output), \
                    patch.object(validate_site, 'load_supplements', return_value=ready), \
                    redirect_stdout(io.StringIO()):
                validate_site.main()
            for language in ('', 'zh/'):
                homepage = (output / language / 'index.html').read_text()
                self.assertIn('source-published.json', homepage)
                about = (output / language / 'about/index.html').read_text()
                self.assertIn('source-index.json', about)
                self.assertIn('/evidence/source-scans/' + self.source['archive_filename'], about)
                self.assertIn('4 个上游仓库已无法访问' if language else
                              '4 whose upstream repository is no longer available', about)
            with zipfile.ZipFile(output / 'downloads/awesome-rea-data.zip') as archive:
                self.assertEqual(set(archive.namelist()), {
                    'resources.json', 'papers.json', 'records.jsonl', 'references.bib', 'README.md', 'manifest.json'})
                rows = json.loads(archive.read('resources.json'))
                self.assertFalse(any(row['id'].startswith('scan-') for row in rows))
                self.assertEqual(len(rows), len(json.loads((output / 'catalog.json').read_text())['resources']))

    @reuses_class_evidence
    def test_publication_time_normalizes_offsets_and_utc_calendar_date(self):
        import build_repository_index
        for recorded, expected in (
            ('2026-10-20T00:00:00+0000', '2026-10-20T00:00:00Z'),
            ('2026-10-20T00:30:00+01:00', '2026-10-19T23:30:00Z'),
        ):
            with self.subTest(recorded=recorded), tempfile.TemporaryDirectory() as directory:
                root = self.fixture(directory, ready=True, count=1)
                path = root / f'data/source-supplements/{BATCH_NAME}.json'
                batch = json.loads(path.read_text())
                batch['reviewed_at'] = recorded
                path.write_bytes(supplements.json_bytes(batch))
                admitted = supplements.load_supplements(root)
                publication = supplements.compose_published(
                    self.canonical_export(), self.baseline_sha, admitted,
                    supplements.project_additions(admitted))
                self.assertEqual(admitted['ready'][0]['reviewed_at'], recorded)
                self.assertEqual(publication['meta']['published_at'], expected)
                browser = project_source_browser(supplements.json_bytes(publication))
                self.assertEqual(browser['meta']['published_at'], expected)
                with patch.object(build_repository_index, 'load_supplements', return_value=admitted):
                    files, _ = build_repository_index.rendered_files()
                self.assertIn(f'Publication date: **{expected[:10]} UTC**.', files['README.md'])
                self.assertIn(f'发布日期: **{expected[:10]} UTC**.', files['README.zh-CN.md'])
                publication['meta']['published_at'] = recorded
                with self.assertRaisesRegex(ValueError, 'canonical UTC Z'):
                    project_source_browser(supplements.json_bytes(publication))

    @unittest.skipUnless(shutil.which('node'), 'Node is required for the browser contract fixture')
    def test_browser_contract(self):
        result = subprocess.run(['node', str(ROOT / 'tests/public_source_supplement_ui.cjs')],
                                cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
