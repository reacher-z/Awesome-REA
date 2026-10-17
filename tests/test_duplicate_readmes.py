"""Identical READMEs are reported for scope review, never excluded on hash equality alone."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from scan_sources import duplicate_readme_report
from source_scope import DUPLICATE_README_REASON, validate_scope

SHARED, OTHER = 'a' * 64, 'b' * 64


def scan(number, full_name, digest=SHARED, stars=0):
    return {'id': f'scan-{number}', 'full_name': full_name, 'scan_status': 'readme-scanned',
            'readme_sha256': digest, 'readme_bytes': 100, 'stars': stars,
            'pushed_at': '2026-10-01T00:00:00Z', 'observed_at': '2026-10-16T00:00:00Z',
            'readme_url': f'https://github.com/{full_name}/blob/main/README.md'}


def fixture():
    # The copy has more stars than the earlier repository; stars must not choose the related record.
    resources = [scan(30, 'copier/Tool', stars=500), scan(10, 'author/tool', stars=1),
                 scan(20, 'templater/other-name'), scan(40, 'excluded/tool'), scan(50, 'unique/tool', OTHER)]
    scope = {'scan-40': {'decision': 'exclude', 'reason_code': 'unrelated-project-purpose',
                         'reason_en': 'Unrelated.', 'reason_zh': '无关。', 'readme_sha256': SHARED,
                         'evidence_url': resources[3]['readme_url'], 'reviewed_at': '2026-10-16'}}
    return {'meta': {'successful_readme_scans': len(resources)}, 'resources': resources}, scope


class DuplicateReadmeReportTests(unittest.TestCase):
    def test_same_named_copies_cite_the_earliest_repository(self):
        document, scope = fixture()
        before = copy.deepcopy((document, scope))
        report = duplicate_readme_report(document, scope)
        self.assertEqual((document, scope), before)
        self.assertEqual((report['successful_readme_scans'], report['distinct_repository_ids'],
                          report['distinct_readme_sha256'], report['identical_readme_groups'],
                          report['proposed_scope_reviews']), (5, 5, 2, 1, 1))
        group = report['groups'][0]
        self.assertEqual(group['shared_repository_names'], ['tool'])
        self.assertEqual([(row['id'], row['scope_status'], row['scope_reason_code']) for row in group['records']], [
            ('scan-10', 'browsable', None), ('scan-20', 'browsable', None), ('scan-30', 'browsable', None),
            ('scan-40', 'excluded', 'unrelated-project-purpose')])
        # The template repository with another name gets no review; the excluded copy keeps its decision.
        self.assertEqual([(row['id'], row['related_source_id'], row['existing_reason_code'],
                           row['proposed_scope_decision'] is not None) for row in group['copy_reviews']],
                         [('scan-30', 'scan-10', None, True), ('scan-40', 'scan-10', 'unrelated-project-purpose', False)])
        proposal = group['copy_reviews'][0]['proposed_scope_decision']
        self.assertEqual((proposal['decision'], proposal['reason_code'], proposal['readme_sha256'],
                          proposal['evidence_url'], proposal['reviewed_at']),
                         ('exclude', DUPLICATE_README_REASON, SHARED, document['resources'][0]['readme_url'], None))
        for field in ('reason_en', 'reason_zh'):
            self.assertIn('scan-10', proposal[field])
            self.assertIn('author/tool', proposal[field])

    def test_copy_decisions_are_bound_to_the_related_readme_hash(self):
        document, scope = fixture()
        proposal = duplicate_readme_report(document, scope)['groups'][0]['copy_reviews'][0]['proposed_scope_decision']
        records = document['resources']

        def errors_for(entry):
            errors = []
            validate_scope(records, {**scope, 'scan-30': entry}, errors)
            return errors

        # An unreviewed proposal cannot be applied as is.
        self.assertTrue(any('reviewed_at' in error for error in errors_for(proposal)))
        reviewed = {**proposal, 'reviewed_at': '2026-10-17'}
        self.assertEqual(errors_for(reviewed), [])
        for changes in (
            {'reason_en': proposal['reason_en'].replace('scan-10', 'scan-50'),
             'reason_zh': proposal['reason_zh'].replace('scan-10', 'scan-50')},  # different README hash
            {'reason_en': proposal['reason_en'].replace('scan-10', 'scan-99'),
             'reason_zh': proposal['reason_zh'].replace('scan-10', 'scan-99')},  # unknown source
            {'reason_zh': proposal['reason_zh'].replace('scan-10', 'scan-20')},  # reasons disagree
            {'reason_en': proposal['reason_en'].replace('scan-10', 'scan-30'),
             'reason_zh': proposal['reason_zh'].replace('scan-10', 'scan-30')},  # cites itself
            {'reason_en': 'A copy.', 'reason_zh': '副本。'},  # cites nothing
        ):
            with self.subTest(changes=changes):
                errors = errors_for({**reviewed, **changes})
                self.assertTrue(errors)
                self.assertTrue(all(error.startswith('scan-30: ' + DUPLICATE_README_REASON) for error in errors), errors)
        # The same related ID also binds when both texts cite it alongside the related name.
        self.assertEqual(errors_for({**reviewed, 'reason_en': reviewed['reason_en'] + ' See scan-10.'}), [])

    def test_command_reports_current_groups_offline(self):
        snapshot, scope_file = ROOT / 'data/source-index.json', ROOT / 'data/source-scope.json'
        before = snapshot.read_bytes(), scope_file.read_bytes()
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/scan_sources.py'), '--duplicate-readme-report', str(snapshot)],
                                capture_output=True, text=True, check=True, env={**os.environ, 'PATH': ''})
        report = json.loads(result.stdout)
        self.assertEqual((snapshot.read_bytes(), scope_file.read_bytes()), before)
        source = json.loads(before[0])
        self.assertEqual(report['successful_readme_scans'], source['meta']['successful_readme_scans'])
        self.assertEqual(report['distinct_repository_ids'], len(source['resources']))
        hashes = {}
        for record in source['resources']:
            hashes.setdefault(record['readme_sha256'], set()).add(record['id'])
        self.assertEqual({row['readme_sha256']: {record['id'] for record in row['records']} for row in report['groups']},
                         {digest: ids for digest, ids in hashes.items() if len(ids) > 1})
        # The groups named in the scan review: two same-named non-fork copy sets, now reviewed as copies of
        # their earliest repository, and one excluded course group. No proposal remains open.
        reviews = {review['id']: (review['related_source_id'], review['existing_reason_code'])
                   for row in report['groups'] for review in row['copy_reviews']}
        self.assertEqual(reviews, {
            **dict.fromkeys(['scan-1421203934', 'scan-1421230756', 'scan-1421230956'], ('scan-1255951226', DUPLICATE_README_REASON)),
            **dict.fromkeys(['scan-1418462661', 'scan-1421214499', 'scan-1421972961', 'scan-1421997475'],
                            ('scan-1337420546', DUPLICATE_README_REASON)),
            'scan-825315675': ('scan-623816748', 'unrelated-project-purpose')})
        self.assertEqual(report['proposed_scope_reviews'], 0)
        scope = json.loads(before[1])
        for identifier, (related, reason) in reviews.items():
            if reason == DUPLICATE_README_REASON:
                self.assertTrue(all(related in scope[identifier][field] for field in ('reason_en', 'reason_zh')), identifier)
        for row in report['groups']:
            for record in row['records']:
                self.assertEqual(record['scope_status'], 'excluded' if record['id'] in scope else 'browsable')
            for review in row['copy_reviews']:
                self.assertEqual(review['proposed_scope_decision'] is None, review['id'] in scope)
                proposal = review['proposed_scope_decision']
                if proposal:
                    errors = []
                    validate_scope(source['resources'], {review['id']: {**proposal, 'reviewed_at': '2026-10-17'}}, errors)
                    self.assertEqual(errors, [], review['id'])


if __name__ == '__main__':
    unittest.main()
