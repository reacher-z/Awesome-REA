"""Rule-based quality scoring: routing, archive safety and score aggregation."""
import io
import json
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import quality_scoring as quality  # noqa: E402


def record(**overrides):
    base = {
        'id': 'demo-case', 'url': 'https://github.com/acme/demo', 'name': 'Demo',
        'kind': 'case-study', 'targets': ['app'], 'description_en': 'A desktop app.',
        'description_zh': '', 'requirements': [],
    }
    base.update(overrides)
    return base


def evidence(code=True, docs=True, download='release-assets', status='observed'):
    return {
        'evidence_class': 1,
        'basis': 'github-rest',
        'evidence_status': status,
        'signals': {
            'code': code, 'docs': docs, 'docs_full': True, 'download': download,
            'download_links': [], 'demo': ['image'],
        },
    }


def linux_artifact():
    return {
        'name': 'demo-v1.0-aarch64-unknown-linux-gnu.tar.gz',
        'url': 'https://example.org/demo.tar.gz', 'source': 'release-asset',
        'release_tag': 'v1.0', 'platform': 'linux', 'arch': 'arm64',
        'format': 'tar.gz', 'declared_bytes': 10,
    }


def rule_pack():
    return {
        'schema_version': 1, 'entry_id': 'demo-case',
        'sut': {
            'kind': 'release-artifact',
            'artifact': {'name_pattern': 'demo-v*-aarch64-unknown-linux-gnu.tar.gz',
                         'platform': 'linux', 'arch': 'arm64'},
            'sandbox': {'image': 'local/image:1', 'network': False,
                        'timeout_seconds': 30, 'interfaces': ['cli']},
        },
        'rules': [{
            'id': 'version', 'dimension': 'correctness',
            'command': ['/sut/demo', '--version'],
            'expect': {'exit_code': 0, 'stdout_contains': '1.0'},
        }],
    }


class ArtifactTests(unittest.TestCase):
    def test_platform_and_arch_are_read_from_the_filename(self):
        self.assertEqual(quality.platform_for_name('foo-aarch64-apple-darwin.tar.gz'), 'macos')
        self.assertEqual(quality.platform_for_name('foo-x86_64-pc-windows-msvc.zip'), 'windows')
        self.assertEqual(quality.platform_for_name('foo-aarch64-unknown-linux-gnu.tar.gz'), 'linux')
        self.assertEqual(quality.platform_for_name('foo.dmg'), 'macos')
        self.assertEqual(quality.platform_for_name('foo.appinstaller'), 'windows')
        self.assertEqual(quality.arch_for_name('foo-aarch64-apple-darwin.tar.gz'), 'arm64')
        self.assertEqual(quality.arch_for_name('foo-x86_64-pc-windows-msvc.zip'), 'x64')

    def test_artifact_from_url_keeps_only_downloadable_files(self):
        artifact = quality.artifact_from_url(
            'https://example.org/demo-v1-aarch64-unknown-linux-gnu.tar.gz', source='release-asset')
        self.assertEqual(artifact['platform'], 'linux')
        self.assertEqual(artifact['format'], 'tar.gz')
        self.assertIsNone(quality.artifact_from_url('https://example.org/downloads', source='release-asset'))

    def test_select_artifact_uses_pattern_platform_and_arch(self):
        self.assertIsNotNone(quality.select_artifact([linux_artifact()], rule_pack()))
        wrong_arch = dict(linux_artifact(), arch='x64')
        self.assertIsNone(quality.select_artifact([wrong_arch], rule_pack()))


class ArchiveSafetyTests(unittest.TestCase):
    def test_tar_with_parent_traversal_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.tar.gz'
            with tarfile.open(path, 'w:gz') as archive:
                info = tarfile.TarInfo('../evil.txt')
                info.size = 4
                archive.addfile(info, io.BytesIO(b'evil'))
            result = quality.extract_archive(path, Path(directory) / 'out')
            self.assertEqual(result['status'], 'blocked')
            self.assertIn('unsafe archive member', result['reason'])
            self.assertFalse((Path(directory) / 'evil.txt').exists())

    def test_zip_with_parent_traversal_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('../evil.txt', 'evil')
            result = quality.extract_archive(path, Path(directory) / 'out')
            self.assertEqual(result['status'], 'blocked')
            self.assertFalse((Path(directory) / 'evil.txt').exists())

    def test_normal_tar_extracts_into_the_fresh_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'good.tar.gz'
            with tarfile.open(path, 'w:gz') as archive:
                info = tarfile.TarInfo('demo')
                info.size = 4
                archive.addfile(info, io.BytesIO(b'demo'))
            out = Path(directory) / 'out'
            result = quality.extract_archive(path, out)
            self.assertEqual(result['status'], 'pass')
            self.assertEqual((out / 'demo').read_bytes(), b'demo')

    def test_appinstaller_rejects_dtd_and_reads_uris(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / 'bad.appinstaller'
            bad.write_text('<!DOCTYPE x [<!ENTITY y SYSTEM "file:///etc/passwd">]><AppInstaller/>')
            self.assertFalse(quality.inspect_appinstaller(bad)['inspectable'])
            good = Path(directory) / 'good.appinstaller'
            good.write_text('<AppInstaller><UpdateSettings><OnLaunch><UpdateAction>'
                            '<Uri>https://example.org/app.msix</Uri></UpdateAction></OnLaunch>'
                            '</UpdateSettings></AppInstaller>')
            report = quality.inspect_appinstaller(good)
            self.assertTrue(report['inspectable'])
            self.assertEqual(report['uris'], ['https://example.org/app.msix'])


class RoutingTests(unittest.TestCase):
    def test_documentation_entries_stop_at_evidence(self):
        route = quality.route_entry(record(kind='documentation'), evidence(), [], None)
        self.assertEqual(route['level'], 'L0-evidence')

    def test_source_only_entries_route_to_static_source_review(self):
        route = quality.route_entry(record(), evidence(download=None), [], None)
        self.assertEqual(route['level'], 'L1-source-static')

    def test_macos_artifact_routes_to_static_and_blocks_runtime(self):
        artifact = {
            'name': 'demo.dmg', 'url': 'https://example.org/demo.dmg', 'source': 'release-asset',
            'platform': 'macos', 'arch': 'universal', 'format': 'dmg', 'declared_bytes': 1,
        }
        route = quality.route_entry(record(), evidence(), [artifact], None)
        self.assertEqual(route['level'], 'L2-artifact-static')
        self.assertEqual(route['blocked'][0]['tool'], 'runtime')

    def test_linux_cli_artifact_without_rule_pack_routes_to_smoke(self):
        route = quality.route_entry(record(), evidence(), [linux_artifact()], None)
        self.assertEqual(route['level'], 'L3-runtime-smoke')
        self.assertEqual(route['blocked'][0]['tool'], 'rule-pack')

    def test_rule_pack_with_sandbox_routes_to_functional_rules(self):
        route = quality.route_entry(record(), evidence(), [linux_artifact()], rule_pack())
        self.assertEqual(route['level'], 'L4-functional-rules')

    def test_unknown_source_routes_to_nothing(self):
        route = quality.route_entry(record(), evidence(status='unknown'), [], None)
        self.assertEqual(route['level'], 'L0-evidence')
        self.assertEqual(route['blocked'][0]['tool'], 'all')


class CandidateInputTests(unittest.TestCase):
    def write_candidates(self, directory, entries):
        path = Path(directory) / 'candidates.json'
        path.write_text(json.dumps({'schema_version': 1, 'entries': entries}), encoding='utf-8')
        return path

    def test_candidates_join_the_scoring_catalog_without_becoming_curated(self):
        entry = {
            'id': 'candidate-case', 'url': 'https://github.com/acme/candidate',
            'name': 'Candidate', 'kind': 'case-study', 'targets': ['app'],
            'evidence': {'evidence_status': 'observed', 'basis': 'source-index',
                         'signals': {'code': True}},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_candidates(directory, [entry])
            catalog = quality.load_catalog(path)
            self.assertEqual(catalog['candidate-case']['catalog_status'], 'candidate')
            self.assertEqual(catalog['woxi-case']['catalog_status'], 'curated')
            evidence = quality.load_evidence(path)
            self.assertTrue(evidence['candidate-case']['signals']['code'])

    def test_a_candidate_cannot_shadow_a_curated_id(self):
        entry = {'id': 'woxi-case', 'url': 'https://example.org/x', 'name': 'X',
                 'kind': 'case-study', 'targets': ['app']}
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_candidates(directory, [entry])
            with self.assertRaises(ValueError):
                quality.load_catalog(path)


class SourceInspectionTests(unittest.TestCase):
    def test_inventory_reads_license_tests_manifest_and_ci(self):
        inventory = quality.source_inventory([
            'LICENSE', 'Cargo.toml', 'requirements-desktop.txt', 'src/main.rs',
            'tests/test_cli.py', '.github/workflows/ci.yml', 'docs/guide.md',
        ])
        self.assertTrue(inventory['license'])
        self.assertTrue(inventory['tests'])
        self.assertEqual(inventory['manifests'], ['Cargo.toml', 'requirements-desktop.txt'])
        self.assertTrue(inventory['ci'])
        self.assertTrue(inventory['docs'])
        self.assertEqual(inventory['source_files'], 2)

    def test_missing_signals_are_partial_not_failures(self):
        results = quality.source_results(['README.md', 'main.py'])
        by_id = {result['id']: result for result in results}
        self.assertEqual(by_id['source-inventory']['status'], 'pass')
        self.assertEqual(by_id['source-license']['status'], 'partial')
        self.assertEqual(by_id['source-tests']['status'], 'partial')
        self.assertEqual(by_id['source-manifests']['status'], 'partial')
        self.assertEqual(by_id['source-ci']['status'], 'partial')

    def test_present_signals_pass(self):
        results = quality.source_results([
            'COPYING', 'pyproject.toml', 'tests/test_app.py', '.gitlab-ci.yml',
        ])
        by_id = {result['id']: result for result in results}
        for key in ('source-license', 'source-tests', 'source-manifests', 'source-ci'):
            self.assertEqual(by_id[key]['status'], 'pass', key)


class RulePackTests(unittest.TestCase):
    def test_the_shipped_woxi_pack_is_valid(self):
        packs = quality.load_rule_packs()
        self.assertIn('woxi-case', packs)
        self.assertEqual(packs['woxi-case']['sut']['sandbox']['image'],
                         'rea-rollout/woxi:0.3.0-arm64')

    def test_a_rule_without_expectation_is_rejected(self):
        document = rule_pack()
        document['rules'][0]['expect'] = {}
        with self.assertRaises(ValueError):
            quality.validate_rule_pack(document)

    def test_an_unknown_dimension_is_rejected(self):
        document = rule_pack()
        document['rules'][0]['dimension'] = 'vibes'
        with self.assertRaises(ValueError):
            quality.validate_rule_pack(document)


class ExpectationTests(unittest.TestCase):
    def test_exact_stdout_and_exit_code(self):
        observed = {'exit_code': 0, 'stdout': '3\n', 'stderr': ''}
        self.assertEqual(quality.expectation_matches({'exit_code': 0, 'stdout_equals': '3'}, observed),
                         (True, 'expectation met'))
        ok, reason = quality.expectation_matches({'stdout_equals': '4'}, observed)
        self.assertFalse(ok)
        self.assertIn('stdout', reason)

    def test_contains_matches_substring(self):
        observed = {'exit_code': 0, 'stdout': 'woxi 0.3.0\n', 'stderr': ''}
        self.assertTrue(quality.expectation_matches({'stdout_contains': '0.3.0'}, observed)[0])


class ScoreTests(unittest.TestCase):
    def test_passing_rules_produce_a_coverage_weighted_score(self):
        results = [
            {'id': 'download', 'dimension': 'artifact_integrity', 'status': 'pass'},
            {'id': 'version', 'dimension': 'correctness', 'status': 'pass'},
            {'id': 'license', 'dimension': 'reproducibility', 'status': 'pass'},
        ]
        score = quality.score_results(results, ['artifact_integrity', 'correctness', 'performance', 'reproducibility'])
        self.assertEqual(score['counts']['passed'], 3)
        self.assertEqual(score['coverage'], 0.75)
        self.assertEqual(score['pass_rate'], 1.0)
        self.assertEqual(score['score'], 75.0)
        self.assertEqual(score['verdict'], 'partially-verified')

    def test_a_failed_rule_is_never_reported_as_verified(self):
        results = [
            {'id': 'version', 'dimension': 'correctness', 'status': 'fail'},
            {'id': 'license', 'dimension': 'reproducibility', 'status': 'pass'},
        ]
        score = quality.score_results(results, ['correctness', 'reproducibility'])
        self.assertEqual(score['verdict'], 'failed')
        self.assertEqual(score['pass_rate'], 0.5)

    def test_blocked_execution_stays_ungraded(self):
        results = [
            {'id': 'download', 'dimension': 'artifact_integrity', 'status': 'blocked'},
            {'id': 'version', 'dimension': 'correctness', 'status': 'blocked'},
        ]
        score = quality.score_results(results, ['artifact_integrity', 'correctness', 'performance'])
        self.assertIsNone(score['score'])
        self.assertEqual(score['verdict'], 'blocked')
        self.assertEqual(score['coverage'], 0.0)

    def test_documentation_only_route_has_no_score(self):
        score = quality.score_results([], ['reproducibility'])
        self.assertIsNone(score['score'])
        self.assertEqual(score['coverage'], 0.0)

    def test_static_route_caps_the_score(self):
        results = [
            {'id': 'download', 'dimension': 'artifact_integrity', 'status': 'pass'},
            {'id': 'artifact-pin', 'dimension': 'reproducibility', 'status': 'pass'},
        ]
        score = quality.score_results(results, ['artifact_integrity', 'reproducibility'], 'L2-artifact-static')
        self.assertEqual(score['score'], 40.0)
        self.assertEqual(score['verdict'], 'artifact-verified')

    def test_thin_coverage_stays_numeric_and_names_its_coverage(self):
        results = [{'id': 'version', 'dimension': 'correctness', 'status': 'pass'}]
        score = quality.score_results(results, ['correctness', 'performance', 'reproducibility'])
        self.assertEqual(score['score'], 33.3)
        self.assertEqual(score['coverage'], 0.333)
        self.assertEqual(score['verdict'], 'partially-verified')


if __name__ == '__main__':
    unittest.main()
