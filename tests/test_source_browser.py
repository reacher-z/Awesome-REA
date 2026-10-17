"""Protect browser field parity, source identity, and exclusion boundaries."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from source_browser import compact_json_bytes, project_source_browser, validate_source_browser, write_source_browser


def record(identifier, **changes):
    return {
        'id': identifier, 'name': 'Example/' + identifier, 'full_name': 'Example/' + identifier,
        'url': 'https://github.com/Example/' + identifier,
        'description_en': 'A preserved description.', 'description_zh': '保留的简介。',
        'description_original': 'Original description.', 'description_language': 'bilingual',
        'description_zh_status': 'translated', 'description_localization': 'ai-assisted-translation',
        'description_origin': 'github-repository-description',
        'topics': ['reverse-engineering'], 'targets': ['app'], 'category': 'android',
        'stars': 3, 'license': 'MIT', 'pushed_at': '2026-01-01T00:00:00Z',
        'observed_at': '2026-01-02T00:00:00Z', 'metadata_observed_at': '2026-01-02T00:00:00Z',
        'readme_url': 'https://github.com/Example/' + identifier + '/blob/main/README.md',
        'readme_path': 'README.md', 'readme_sha256': 'a' * 64, 'readme_git_sha': 'b' * 40,
        'readme_bytes': 20, 'scan_status': 'readme-scanned', 'verification': 'automated-readme-scan',
        'requirements': 'See upstream requirements; not manually reviewed.',
        'classification_origin': 'metadata', 'classification_reference_ids': [],
        'matched_queries': ['discovery query'], 'discovery_methods': ['github-search'],
        'unrelated_future_field': 'Do not copy this field automatically.',
        **changes,
    }


def full_export():
    omission = {'reason': 'upstream-description-too-long', 'original_characters': 1001,
                'original_utf8_bytes': 1001, 'original_sha256': 'c' * 64, 'limit_characters': 1000}
    integrity = {'reviewed_at': '2026-01-03T00:00:00Z',
                 'method': 'readme-json-and-raw-match-captured-sha256',
                 'advertised_blob_sha256': 'd' * 64, 'advertised_blob_bytes': 18}
    return {
        'meta': {'schema_version': 1, 'status': 'complete', 'completed_at': '2026-01-02T00:00:00Z',
                 'scope': {'scanned_count': 3, 'excluded_count': 1, 'browse_count': 2},
                 'queries': ['large discovery ledger'], 'resume_history': [{'historical': True}]},
        'resources': [
            record('scan-2', description_en='', description_zh='', description_original='',
                   description_capture_policy='bounded-upstream-v1', description_omission=omission),
            record('scan-3', scope_status='excluded', scope_review={'decision': 'exclude'}),
            record('scan-4', scan_status='failed'),
            record('scan-1', readme_content_git_sha='e' * 40,
                   readme_git_sha_matches_content=False, readme_integrity_review=integrity,
                   related_entries=[{'kind': 'paper', 'id': 'paper-example',
                                     'title_en': 'Research', 'title_zh': '研究',
                                     'href_en': '/papers/#paper-example',
                                     'href_zh': '/zh/papers/#paper-example'}]),
        ],
        'failures': [{'id': 'scan-4'}],
    }


def export_bytes(document):
    return (json.dumps(document, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


class SourceBrowserTests(unittest.TestCase):
    def test_visibility_order_and_full_export_identity(self):
        source = full_export()
        before = copy.deepcopy(source)
        raw = export_bytes(source)
        projected = project_source_browser(raw)
        self.assertEqual(source, before)
        self.assertEqual([record['id'] for record in projected['resources']], ['scan-2', 'scan-1'])
        self.assertEqual(projected['meta'], {
            'schema_version': 1, 'status': 'complete', 'completed_at': source['meta']['completed_at'],
            'scope': source['meta']['scope'], 'full_export': 'source-index.json',
            'full_export_sha256': hashlib.sha256(raw).hexdigest(),
        })
        self.assertNotIn('failures', projected)
        self.assertNotIn('queries', projected['meta'])
        self.assertNotIn('resume_history', projected['meta'])
        for record in projected['resources']:
            self.assertNotIn('matched_queries', record)
            self.assertNotIn('discovery_methods', record)
            self.assertNotIn('unrelated_future_field', record)

    def test_search_details_omission_and_integrity_remain_exact(self):
        source = full_export()
        projected = project_source_browser(export_bytes(source))['resources']
        for original, actual in zip((source['resources'][0], source['resources'][3]), projected):
            for field in ('id', 'name', 'full_name', 'url', 'description_en', 'description_zh',
                          'description_original', 'topics', 'targets', 'category', 'stars', 'license',
                          'pushed_at', 'observed_at', 'metadata_observed_at', 'readme_url',
                          'readme_sha256', 'readme_git_sha', 'readme_bytes', 'scan_status', 'verification'):
                self.assertEqual(actual[field], original[field])
        self.assertEqual(projected[0]['description_omission'], source['resources'][0]['description_omission'])
        self.assertEqual(projected[0]['description_capture_policy'], 'bounded-upstream-v1')
        self.assertEqual(projected[1]['readme_integrity_review'], source['resources'][3]['readme_integrity_review'])
        self.assertEqual(projected[1]['readme_content_git_sha'], 'e' * 40)
        self.assertIs(projected[1]['readme_git_sha_matches_content'], False)
        self.assertEqual(projected[1]['related_entries'], source['resources'][3]['related_entries'])

    def test_build_time_labels_keep_their_scan_provenance(self):
        source = full_export()
        scanned = {'targets': ['app'], 'category': 'android', 'classification_origin': 'metadata',
                   'classification_reference_ids': []}
        source['resources'][3].update(targets=['app', 'protocol'], classification_origin='curated-build-cross-reference',
                                      classification_reference_ids=['example-tool'], scan_classification=scanned)
        projected = project_source_browser(export_bytes(source))['resources'][1]
        self.assertEqual((projected['targets'], projected['classification_origin'], projected['scan_classification']),
                         (['app', 'protocol'], 'curated-build-cross-reference', scanned))
        self.assertNotIn('scan_classification', project_source_browser(export_bytes(full_export()))['resources'][1])

    def test_validator_rejects_field_loss_and_mutated_evidence(self):
        raw = export_bytes(full_export())
        expected = project_source_browser(raw)
        mutations = [
            lambda doc: doc['resources'][0].pop('description_original'),
            lambda doc: doc['resources'][0].pop('description_omission'),
            lambda doc: doc['resources'][1].pop('verification'),
            lambda doc: doc['resources'][1].pop('readme_integrity_review'),
            lambda doc: doc['resources'][1].update(readme_sha256='f' * 64),
            lambda doc: doc['resources'][1]['related_entries'][0].update(title_zh='改变的标题'),
            lambda doc: doc['meta'].update(full_export_sha256='0' * 64),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(expected)
            mutate(changed)
            with self.assertRaisesRegex(ValueError, 'differs from the full export contract'):
                validate_source_browser(raw, compact_json_bytes(changed))

    def test_validator_rejects_excluded_rows_reordering_and_extra_ledgers(self):
        source = full_export()
        raw = export_bytes(source)
        expected = project_source_browser(raw)
        mutations = [
            lambda doc: doc['resources'].append(source['resources'][1]),
            lambda doc: doc['resources'].reverse(),
            lambda doc: doc['resources'].append(doc['resources'][0]),
            lambda doc: doc['meta'].update(queries=['leaked ledger']),
            lambda doc: doc.update(failures=source['failures']),
        ]
        for mutate in mutations:
            changed = copy.deepcopy(expected)
            mutate(changed)
            with self.assertRaisesRegex(ValueError, 'differs from the full export contract'):
                validate_source_browser(raw, compact_json_bytes(changed))

    def test_invalid_full_export_is_not_silently_repaired(self):
        source = full_export()
        source['meta']['scope']['browse_count'] = 3
        with self.assertRaisesRegex(ValueError, 'scope counts'):
            project_source_browser(export_bytes(source))
        source = full_export()
        source['resources'][0].pop('readme_sha256')
        with self.assertRaisesRegex(ValueError, 'missing required browser fields'):
            project_source_browser(export_bytes(source))

    def test_compact_write_stale_removal_and_full_export_preservation(self):
        raw = export_bytes(full_export())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            full_path = output / 'source-index.json'
            full_path.write_bytes(raw)
            expected = write_source_browser(output, raw)
            path = output / 'source-browser.json'
            first = path.read_bytes()
            self.assertEqual(validate_source_browser(raw, first), expected)
            self.assertEqual(first.count(b'\n'), 1)
            self.assertIn('保留'.encode('utf-8'), first)
            write_source_browser(output, raw)
            self.assertEqual(path.read_bytes(), first)
            self.assertEqual(full_path.read_bytes(), raw)
            with self.assertRaisesRegex(ValueError, 'not deterministic compact JSON'):
                validate_source_browser(raw, export_bytes(expected))
            write_source_browser(output, None)
            self.assertFalse(path.exists())
            self.assertEqual(full_path.read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
