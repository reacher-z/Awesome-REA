"""Offline checks for evidence boundaries and internal artifact navigation."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from artifact_links import (BUILD_CROSS_REFERENCE, CURATED_PRIMARY_CATEGORIES, github_repository,
                            with_artifact_links, with_curated_labels)
from build_browse_pages import repository_card


def source(**changes):
    return {'id': 'scan-1', 'name': 'Owner/Project', 'full_name': 'Owner/Project',
            'url': 'https://github.com/Owner/Project', 'description_en': '', 'description_zh': '',
            'verification': 'automated-readme-scan', 'readme_sha256': 'a' * 64, **changes}


def paper(**changes):
    return {'id': 'paper-example', 'title': 'Example research', 'title_zh': '示例研究',
            'verification': 'source-reviewed', 'code_url': 'https://github.com/owner/project',
            'project_url': None, **changes}


def resource(**changes):
    return {'id': 'example-tool', 'name': 'Example tool', 'name_zh': '示例工具',
            'url': 'https://github.com/owner/project', 'verification': 'source-reviewed', **changes}


class ArtifactLinkTests(unittest.TestCase):
    def test_repository_identity_rejects_guessed_or_unsafe_matches(self):
        for url in ('https://github.com/Owner/Project', 'https://GITHUB.COM/owner/project.git/'):
            self.assertEqual(github_repository(url), 'owner/project')
        for url in ('https://github.com/owner/project/blob/main/README.md',
                    'https://github.com/owner/project/tree/main'):
            self.assertEqual(github_repository(url, artifact=True), 'owner/project')
            self.assertIsNone(github_repository(url))
        for url in ('https://owner.github.io/project/', 'https://gitlab.com/owner/project',
                    'https://github.com.evil.test/owner/project', 'https://secret@github.com/owner/project',
                    'http://github.com/owner/project', 'javascript:alert(1)',
                    'https://github.com:443/owner/project', 'https://github.com/owner/../project',
                    'https://github.com/owner%2Fother/project', 'https://github.com//owner/project',
                    'https://github.com/owner/project/issues/1'):
            with self.subTest(url=url):
                self.assertIsNone(github_repository(url, artifact=True))

    def test_reviewed_artifact_links_work_without_seed_fields_and_preserve_inputs(self):
        records, papers = [source()], [paper()]
        before = copy.deepcopy((records, papers))
        result = with_artifact_links(records, papers, [])
        self.assertEqual((records, papers), before)
        self.assertEqual({k: v for k, v in result[0].items() if k != 'related_entries'}, records[0])
        self.assertEqual(result[0]['description_en'], '')
        self.assertEqual(result[0]['verification'], 'automated-readme-scan')
        self.assertEqual(result[0]['related_entries'][0]['href_zh'], '/zh/papers/#paper-example')

    def test_duplicate_fields_deduplicate_and_input_order_does_not_change_links(self):
        papers = [paper(project_url='https://github.com/owner/project/tree/main'),
                  paper(id='paper-another')]
        resources = [resource()]
        result = with_artifact_links([source()], papers, resources)
        self.assertEqual(result, with_artifact_links([source()], list(reversed(papers)), resources))
        entries = result[0]['related_entries']
        self.assertEqual([(r['kind'], r['id']) for r in entries],
                         [('paper', 'paper-another'), ('paper', 'paper-example'), ('curated', 'example-tool')])
        self.assertEqual(entries[1]['artifact_fields'], ['code_url', 'project_url'])
        self.assertEqual(with_artifact_links(result, papers, resources), result)

    def test_seed_only_references_do_not_guess_repository_transfers(self):
        diagnostics = []
        result = with_artifact_links([source(seed_paper_ids=['paper-example', 'paper-unknown'])],
                                     [paper(code_url='https://github.com/old-owner/project')], [], diagnostics)
        self.assertNotIn('related_entries', result[0])
        self.assertEqual(len(diagnostics), 2)

    def test_mirrors_nested_curated_guides_and_unreviewed_sources_do_not_link(self):
        resources = [resource(url='https://gitlab.com/owner/project',
                              additional_evidence_urls=['https://github.com/owner/project']),
                     resource(id='guide', url='https://github.com/owner/project/blob/main/README.md'),
                     resource(id='unreviewed', verification='automated-readme-scan')]
        self.assertNotIn('related_entries', with_artifact_links([source()],
                         [paper(verification='automated-readme-scan')], resources)[0])
        self.assertNotIn('related_entries', with_artifact_links([source(full_name='Different/Repository')],
                         [paper()], [resource()])[0])

    def test_static_cards_use_localized_same_tab_links_and_escape_titles(self):
        row = with_artifact_links([source()], [paper(title='<script>research</script>')], [resource()])[0]
        for language, prefix, label in (('en', '', 'Related research'), ('zh', '/zh', '相关研究')):
            rendered = repository_card(row, language, False)
            self.assertIn(f'href="{prefix}/papers/#paper-example"', rendered)
            self.assertIn(f'href="{prefix}/resources/#example-tool"', rendered)
            self.assertIn(label, rendered)
            self.assertIn('No description supplied' if language == 'en' else '上游仓库未提供项目简介', rendered)
            self.assertNotIn('<script>research</script>', rendered)
            self.assertNotRegex(rendered, r'class="source-related-link"[^>]*target=')
        row['related_entries'][0]['href_en'] = 'https://example.com/#paper-example'
        with self.assertRaises(ValueError):
            repository_card(row, 'en', False)


def labeled(**changes):
    return source(**{'targets': ['binary'], 'category': 'native-analysis',
                     'classification_origin': 'automatic-metadata', 'classification_reference_ids': [], **changes})


class CuratedLabelTests(unittest.TestCase):
    def test_exact_roots_receive_curated_labels_beside_the_scan_labels(self):
        records = [labeled()]
        resources = [resource(targets=['app', 'protocol'], category='android')]
        before = copy.deepcopy((records, resources))
        row = with_curated_labels(records, resources)[0]
        self.assertEqual((records, resources), before)
        self.assertEqual((row['targets'], row['category']), (['app', 'binary', 'protocol'], 'android'))
        self.assertEqual(row['classification_origin'], BUILD_CROSS_REFERENCE)
        self.assertEqual(row['classification_reference_ids'], ['example-tool'])
        self.assertEqual(row['scan_classification'], {
            'targets': ['binary'], 'category': 'native-analysis',
            'classification_origin': 'automatic-metadata', 'classification_reference_ids': []})
        # Matching curated labels still record the build-time provenance.
        row = with_curated_labels([labeled()], [resource(targets=['binary'], category='native-analysis')])[0]
        self.assertEqual((row['targets'], row['classification_origin']), (['binary'], BUILD_CROSS_REFERENCE))

    def test_scoped_unreviewed_and_mismatched_records_do_not_set_labels(self):
        curated = dict(targets=['game'], category='game-analysis')
        resources = [resource(id='guide', url='https://github.com/owner/project/blob/main/README.md', **curated),
                     resource(id='docs', url='https://github.com/owner/project/tree/main/docs', **curated),
                     resource(id='mirror', url='https://gitlab.com/owner/project', **curated),
                     resource(id='unreviewed', verification='automated-readme-scan', **curated)]
        self.assertEqual(with_curated_labels([labeled()], resources), [labeled()])
        mismatched = labeled(full_name='Different/Repository')
        self.assertEqual(with_curated_labels([mismatched], [resource(**curated)]), [mismatched])

    def test_unmapped_categories_add_targets_without_moving_the_record(self):
        row = with_curated_labels([labeled()], [resource(targets=['app'], category='agent-mcp')])[0]
        self.assertNotIn('agent-mcp', CURATED_PRIMARY_CATEGORIES)
        self.assertEqual((row['targets'], row['category']), (['app', 'binary'], 'native-analysis'))
        self.assertEqual(CURATED_PRIMARY_CATEGORIES['protocol-analysis'], 'protocol-analysis')

    def test_scan_time_cross_references_change_only_for_curated_additions(self):
        scanned = labeled(classification_origin='curated-cross-reference', classification_reference_ids=['example-tool'])
        current = [resource(targets=['binary'], category='native-analysis')]
        self.assertEqual(with_curated_labels([scanned], current), [scanned])
        added = with_curated_labels([scanned], [resource(targets=['binary', 'protocol'], category='native-analysis')])[0]
        self.assertEqual((added['targets'], added['classification_origin']), (['binary', 'protocol'], BUILD_CROSS_REFERENCE))
        self.assertEqual(added['scan_classification']['classification_origin'], 'curated-cross-reference')
        # Removing a curated target never erases a label recorded at scan time.
        self.assertEqual(with_curated_labels([scanned], [resource(targets=[], category='native-analysis')]), [scanned])

    def test_derivation_is_idempotent_order_independent_and_reversible(self):
        resources = [resource(id='b-tool', targets=['game'], category='game-analysis'),
                     resource(id='a-tool', targets=['app'], category='dotnet')]
        once = with_curated_labels([labeled()], resources)
        self.assertEqual(once, with_curated_labels([labeled()], list(reversed(resources))))
        self.assertEqual(once[0]['classification_reference_ids'], ['a-tool', 'b-tool'])
        self.assertEqual(once[0]['category'], 'managed-code')
        self.assertEqual(with_curated_labels(once, resources), once)
        self.assertEqual(with_curated_labels(once, []), [labeled()])

    def test_repository_data_keeps_scan_labels_and_exports_every_exact_match(self):
        source_index = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))['resources']
        resources = [record for name in ('rea-resources.json', 'tool-resources.json')
                     for record in json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))]
        self.assertFalse([record['id'] for record in source_index
                          if 'scan_classification' in record or record.get('classification_origin') == BUILD_CROSS_REFERENCE])
        roots = {}
        for resource_record in resources:
            if github_repository(resource_record['url']):
                roots.setdefault(github_repository(resource_record['url']), []).append(resource_record)
        derived = {record['id']: record for record in with_curated_labels(source_index, resources)}
        matched = [record for record in source_index if github_repository(record['url']) in roots]
        self.assertTrue(matched)
        for record in matched:
            row = derived[record['id']]
            for curated in roots[github_repository(record['url'])]:
                self.assertTrue(set(curated['targets']) <= set(row['targets']), record['id'])
                if curated['category'] in CURATED_PRIMARY_CATEGORIES:
                    self.assertEqual(row['category'], CURATED_PRIMARY_CATEGORIES[curated['category']], record['id'])
            if record['classification_origin'] == 'automatic-metadata':
                self.assertEqual(row['classification_origin'], BUILD_CROSS_REFERENCE, record['id'])


if __name__ == '__main__':
    unittest.main()
