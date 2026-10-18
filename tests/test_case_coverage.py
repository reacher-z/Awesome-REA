"""Reject inventory inflation, unsupported review claims and unsafe evidence/mappings."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from case_coverage import coverage_counts, read_case_coverage, validate_case_coverage
from build_case_coverage import linked_repository_count, render
from validate import public_https_error
import review_pr


PIN = 'a' * 40
REPOSITORY = 'https://github.com/example/cases'
FILE = REPOSITORY + '/blob/' + PIN + '/README.md'
RESOURCES = [
    {'id': 'example-list', 'kind': 'collection', 'url': REPOSITORY},
    {'id': 'example-case', 'kind': 'case-study', 'url': 'https://github.com/example/project'},
]


def fixture():
    def entry(identifier, unit, state='pending'):
        linked = state == 'already-curated'
        return {'id': identifier, 'unit_id': unit, 'collection_id': 'one',
                'title': 'Example case', 'collection_urls': [FILE],
                'reported_source_urls': ['https://github.com/example/project'],
                'state': state, 'review_level': 'catalog-mapped' if linked else 'inventory-only',
                'reviewed_at': '2026-01-01', 'reason_en': 'Bounded source review.', 'reason_zh': '有限范围的来源核查。',
                'primary_evidence_urls': ['https://github.com/example/project'] if linked else [],
                'catalog_matches': [{'catalog': 'resource', 'id': 'example-case', 'kind': 'case-study', 'scope': 'full'}] if linked else []}
    return {
        'schema_version': 1, 'reviewed_at': '2026-01-01', 'catalog_revision': PIN,
        'runtime_reproduced': False, 'project_identity_resolution': 'incomplete',
        'collections': [{'id': 'one', 'repository_url': REPOSITORY, 'commit': PIN,
                         'entry_count': 3, 'catalog_resource_id': 'example-list',
                         'locator_templates': ['README.md'],
                         'source_files': [{'path': 'README.md', 'url': FILE, 'git_blob_sha': 'b' * 40,
                                           'sha256': 'c' * 64, 'bytes': 50}]}],
        'entries': [entry('one:first', 'one:first'), entry('one:alias', 'one:first'),
                    entry('one:covered', 'one:covered', 'already-curated')],
        'aliases': [{'unit_id': 'one:first', 'occurrence_ids': ['one:first', 'one:alias'],
                     'basis_en': 'Same reported subject.', 'basis_zh': '相同报告对象。', 'evidence_urls': [FILE]}],
        'counts': {'occurrences': 3, 'inventory_units': 2, 'alias_merges': 1,
                   'occurrences_by_state': {'already-curated': 1, 'pending': 2},
                   'units_by_state': {'already-curated': 1, 'pending': 1},
                   'primary_reviewed_units': 0, 'catalog_linked_occurrences': 1,
                   'distinct_resource_ids': 1, 'distinct_paper_ids': 0, 'unique_projects': None},
    }


class CaseCoverageTests(unittest.TestCase):
    def errors(self, value):
        errors = []
        validate_case_coverage(value, RESOURCES, [], errors, url_check=public_https_error)
        return errors

    def test_valid_inventory_keeps_project_count_unknown(self):
        self.assertEqual(self.errors(fixture()), [])

    def test_repository_links_do_not_merge_occurrences_or_count_subpaths_twice(self):
        document = fixture()
        original = copy.deepcopy(document)
        document['entries'][0]['reported_source_urls'] += [
            'https://github.com/EXAMPLE/Project.git',
            'https://github.com/example/project/blob/' + PIN + '/README.md',
            'https://github.com/example/project/tree/main/subdir',
            'https://github.com/example/another',
            'https://example.org/game',
        ]
        self.assertEqual(linked_repository_count(document['entries']), 2)
        self.assertEqual(coverage_counts(document['entries']), original['counts'])
        self.assertEqual(self.errors(document), [])

    def test_related_mapping_is_visible_without_claiming_full_coverage(self):
        document = fixture()
        entry = document['entries'][2]
        entry['state'] = 'pending'
        entry['catalog_matches'][0]['scope'] = 'related'
        entry['reason_en'] = 'The parent is curated; the separate port remains pending.'
        entry['reason_zh'] = '父项目已收录；独立移植项目仍待核查。'
        document['counts'] = coverage_counts(document['entries'])
        self.assertEqual(self.errors(document), [])
        for zh in (False, True):
            summary = render(document, {row['id']: row for row in RESOURCES}, {}, zh)
            self.assertIn(entry['reason_zh' if zh else 'reason_en'], summary)
            self.assertIn('部分或相关目录映射' if zh else 'Partial or related catalog mappings', summary)

    def test_count_grains_and_boolean_counts_are_rejected(self):
        for key, value in [('inventory_units', 3), ('unique_projects', 2), ('distinct_resource_ids', True)]:
            with self.subTest(key=key):
                document = fixture(); document['counts'][key] = value
                self.assertTrue(self.errors(document))
        document = fixture(); document['counts']['units_by_state']['already-curated'] = True
        self.assertTrue(self.errors(document))

    def test_alias_members_and_states_must_be_explicit(self):
        for mutation in ('missing', 'wrong-member', 'inconsistent-state', 'unrelated-evidence'):
            with self.subTest(mutation=mutation):
                document = fixture()
                if mutation == 'missing': document['aliases'] = []
                elif mutation == 'wrong-member': document['aliases'][0]['occurrence_ids'][1] = 'one:missing'
                elif mutation == 'inconsistent-state': document['entries'][1]['state'] = 'insufficient-evidence'
                else: document['aliases'][0]['evidence_urls'] = ['https://example.org/unrelated']
                self.assertTrue(self.errors(document))

    def test_unit_representatives_cannot_point_into_other_groups(self):
        document = fixture(); document['aliases'] = []
        for entry in document['entries']:
            entry['unit_id'] = entry['id']
        document['counts'] = coverage_counts(document['entries'])
        self.assertEqual(self.errors(document), [])
        document['entries'][0]['unit_id'] = 'one:covered'
        document['entries'][2]['unit_id'] = 'one:first'
        document['counts'] = coverage_counts(document['entries'])
        errors = self.errors(document)
        self.assertEqual(sum('representative must belong to its own inventory unit' in error for error in errors), 2)

    def test_summary_omits_absent_partial_cases_and_aliases(self):
        document = fixture(); document['aliases'] = []
        for entry in document['entries']:
            entry['unit_id'] = entry['id']
        document['counts'] = coverage_counts(document['entries'])
        self.assertEqual(self.errors(document), [])
        for zh in (False, True):
            summary = render(document, {row['id']: row for row in RESOURCES}, {}, zh)
            self.assertIn('当前没有别名合并。' if zh else 'No alias merges are recorded.', summary)
            self.assertIn('当前没有部分目录映射。' if zh else 'No partial catalog mappings are recorded.', summary)
            self.assertNotIn('Plustek', summary)
            self.assertNotIn('decomp.wtf', summary)

    def test_summary_renders_actual_partial_reason_and_alias_basis(self):
        document = fixture()
        document['entries'][2].update({'state': 'pending', 'reason_en': 'Only the input format is covered.',
                                       'reason_zh': '仅覆盖输入格式。'})
        document['entries'][2]['catalog_matches'][0]['scope'] = 'partial'
        document['counts'] = coverage_counts(document['entries'])
        self.assertEqual(self.errors(document), [])
        for zh in (False, True):
            summary = render(document, {row['id']: row for row in RESOURCES}, {}, zh)
            self.assertIn(document['entries'][2]['reason_zh' if zh else 'reason_en'], summary)
            self.assertIn(document['aliases'][0]['basis_zh' if zh else 'basis_en'], summary)
            self.assertIn('`one:first`, `one:alias` → `one:first`', summary)
            self.assertNotIn('decomp.wtf', summary)

    def test_primary_review_table_names_a_record_only_for_full_matches(self):
        document = fixture()
        entry = document['entries'][2]
        entry.update({'state': 'insufficient-evidence', 'review_level': 'primary-source-reviewed', 'title': 'Broader claim'})
        entry['catalog_matches'][0]['scope'] = 'partial'
        document['counts'] = coverage_counts(document['entries'])
        self.assertEqual(self.errors(document), [])
        resources = {row['id']: dict(row, name='Example record') for row in RESOURCES}
        for zh in (False, True):
            summary = render(document, resources, {}, zh)
            self.assertIn('| Broader claim |', summary)
            self.assertNotIn('| Example record |', summary)
        entry.update({'state': 'already-curated'})
        entry['catalog_matches'][0]['scope'] = 'full'
        document['counts'] = coverage_counts(document['entries'])
        self.assertEqual(self.errors(document), [])
        self.assertIn('| Example record |', render(document, resources, {}, False))

    def test_partial_or_unreviewed_match_cannot_claim_full_coverage(self):
        for field, value in [('scope', 'partial'), ('scope', 'related'), ('id', 'missing'), ('kind', 'tool')]:
            document = fixture(); document['entries'][2]['catalog_matches'][0][field] = value
            self.assertTrue(self.errors(document))
        document = fixture(); document['entries'][2]['review_level'] = 'inventory-only'
        self.assertTrue(self.errors(document))

    def test_primary_review_needs_primary_sources_and_never_implies_runtime(self):
        document = fixture(); document['entries'][0]['review_level'] = 'primary-source-reviewed'
        self.assertTrue(self.errors(document))
        document = fixture(); document['runtime_reproduced'] = True
        self.assertTrue(self.errors(document))
        document = fixture(); document['entries'][2]['primary_evidence_urls'] = ['https://example.org/unrelated']
        self.assertTrue(self.errors(document))

    def test_private_paths_and_malformed_url_arrays_fail_safely(self):
        document = fixture(); document['entries'][0]['reason_en'] = '/' + 'Users' + '/example/review'
        self.assertTrue(self.errors(document))
        for key in ('reported_source_urls', 'collection_urls', 'primary_evidence_urls'):
            document = fixture(); document['entries'][0][key] = None
            self.assertTrue(self.errors(document))

    def test_source_pins_and_public_url_boundary(self):
        for url in [REPOSITORY + '/blob/main/README.md', FILE + '?ref=main',
                    REPOSITORY + '/blob/' + PIN + '/../main/README.md',
                    REPOSITORY + '/blob/' + PIN + '/unreceipted.md',
                    'https://example.org/README.md', 'https://localhost/readme']:
            with self.subTest(url=url):
                document = fixture(); document['entries'][0]['collection_urls'] = [url]
                self.assertTrue(self.errors(document))
        document = fixture(); document['entries'][0]['reported_source_urls'] = ['https://name:secret@example.org/']
        self.assertTrue(self.errors(document))
        document = fixture(); document['collections'][0]['source_files'][0]['git_blob_sha'] = 'invalid'
        self.assertTrue(self.errors(document))

    def test_case_file_locator_must_match_its_occurrence_slug(self):
        document = fixture(); document['collections'][0]['locator_templates'] = ['cases/{entry}.md']
        for entry in document['entries']:
            entry['collection_urls'] = [REPOSITORY + '/blob/' + PIN + '/cases/' + entry['id'].split(':')[1] + '.md']
        document['aliases'][0]['evidence_urls'] = [url for entry in document['entries'][:2] for url in entry['collection_urls']]
        self.assertEqual(self.errors(document), [])
        document['entries'][0]['collection_urls'] = document['entries'][1]['collection_urls']
        self.assertTrue(self.errors(document))

    def test_collection_counts_ids_and_unknown_fields(self):
        for mutation in ('count', 'duplicate-id', 'raw-body', 'bad-type'):
            document = fixture()
            if mutation == 'count': document['collections'][0]['entry_count'] = 4
            elif mutation == 'duplicate-id': document['entries'][1]['id'] = 'one:first'
            elif mutation == 'raw-body': document['entries'][0]['readme_body'] = 'Do not publish full source.'
            else: document['entries'][0]['state'] = []
            self.assertTrue(self.errors(document))

    def test_strict_loader_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'data'; path.mkdir()
            (path / 'case-coverage.json').write_text('{"schema_version": 1, "schema_version": 2}')
            with self.assertRaises(ValueError): read_case_coverage(directory)

    def test_trusted_reviewer_fetches_only_changed_json(self):
        document = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'data').mkdir()
            values = {review_pr.CATALOGS[0]: RESOURCES, review_pr.CATALOGS[1]: [], 'data/papers.json': []}
            for filename, value in values.items(): (root / filename).write_text(json.dumps(value))
            with patch.object(review_pr, 'ROOT', root), patch.object(review_pr, 'content_at', return_value=json.dumps(document)) as fetch:
                errors = []
                contents = review_pr.load_review_contents('example/repo', PIN, 'mock', [], {review_pr.CASE_COVERAGE}, errors)
                self.assertEqual(errors, [])
                fetch.assert_called_once_with('example/repo', review_pr.CASE_COVERAGE, PIN, 'mock')
                self.assertEqual(review_pr.review_data(contents, {review_pr.CASE_COVERAGE})[0], [])
        with patch.object(review_pr, 'api') as api:
            with self.assertRaises(ValueError): review_pr.content_at('example/repo', 'scripts/untrusted.py', PIN, 'mock')
            api.assert_not_called()


if __name__ == '__main__':
    unittest.main()
