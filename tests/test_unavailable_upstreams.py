"""Gone or reassigned upstreams are excluded only with a recheck result showing their scanned ID no longer resolves."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from scan_sources import ScanError
from source_availability import check_record
from source_scope import (UNAVAILABLE_UPSTREAM_REASON, apply_scope, exclusion_counts, read_scope,
                          unavailable_clause, validate_scope)

DIGEST = 'c' * 64
REVIEWED = {'scan-1377172300': 'not-found', 'scan-1409072094': 'not-found',
            'scan-1238268014': 'name-reassigned', 'scan-1417013841': 'name-reassigned'}


def scan(number, full_name):
    return {'id': f'scan-{number}', 'full_name': full_name, 'scan_status': 'readme-scanned',
            'readme_sha256': DIGEST, 'observed_at': '2026-10-16T07:14:54.793225Z',
            'readme_url': f'https://github.com/{full_name}/blob/main/README.md'}


class FakeAPI:
    def __init__(self, responses):
        self.responses = responses

    def json(self, path):
        response = self.responses[path]
        if isinstance(response, ScanError):
            raise response
        return copy.deepcopy(response)


def public(number, full_name):
    return {'id': number, 'full_name': full_name, 'html_url': 'https://github.com/' + full_name,
            'private': False, 'fork': False, 'archived': False}


def recheck(record, responses):
    """Produce the evidence through the real recheck classifier, then pin its timestamp."""
    return {**check_record(FakeAPI(responses), record), 'observed_at': '2026-10-17T13:47:10.599033Z'}


GONE = ScanError('http-404', 404)
RECORDS = [scan(1238268014, 'Shellghostt/De-Caffeinator'), scan(1377172300, 'owner/gone-tool')]
REASSIGNED = recheck(RECORDS[0], {'/repositories/1238268014': GONE,
                                  '/repos/Shellghostt/De-Caffeinator': public(1244345068, 'Shellghostt/De-Caffeinator')})
NOT_FOUND = recheck(RECORDS[1], {'/repositories/1377172300': GONE, '/repos/owner/gone-tool': GONE})


def decision(check, en, zh):
    return {'decision': 'exclude', 'reason_code': UNAVAILABLE_UPSTREAM_REASON, 'reason_en': en, 'reason_zh': zh,
            'readme_sha256': DIGEST, 'availability_check': check, 'reviewed_at': '2026-10-17'}


SCOPE = {
    'scan-1238268014': decision(
        REASSIGNED,
        'On 2026-10-17, GitHub returned HTTP 404 for repository ID 1238268014, and the recorded name '
        'Shellghostt/De-Caffeinator now resolves to a different repository, ID 1244345068.',
        '2026-10-17 复查时，GitHub 对仓库 ID 1238268014 返回 HTTP 404，记录的名称 Shellghostt/De-Caffeinator '
        '现已指向另一个仓库（ID 1244345068）。'),
    'scan-1377172300': decision(
        NOT_FOUND,
        'On 2026-10-17, GitHub returned HTTP 404 for both repository ID 1377172300 and the recorded name owner/gone-tool.',
        '2026-10-17 复查时，GitHub 对仓库 ID 1377172300 和记录的名称 owner/gone-tool 均返回 HTTP 404。'),
}


def errors_for(scope, records=RECORDS):
    errors = []
    validate_scope(records, scope, errors)
    return errors


def with_check(identifier, **changes):
    entry = copy.deepcopy(SCOPE[identifier])
    entry['availability_check'].update(changes)
    return {**SCOPE, identifier: entry}


class ValidationTests(unittest.TestCase):
    def test_recheck_results_are_accepted_verbatim_with_the_name_lookup_status(self):
        self.assertEqual((REASSIGNED['outcome'], REASSIGNED['http_status'], REASSIGNED['recorded_name_http_status'],
                          REASSIGNED['recorded_name_repository_id']), ('name-reassigned', 404, 200, 'scan-1244345068'))
        self.assertEqual((NOT_FOUND['outcome'], NOT_FOUND['recorded_name_http_status']), ('not-found', 404))
        self.assertEqual(errors_for(SCOPE), [])
        scoped = apply_scope(RECORDS, SCOPE)
        self.assertEqual([record['scope_status'] for record in scoped], ['excluded', 'excluded'])
        self.assertEqual(exclusion_counts(scoped), (0, 2))

    def test_the_reason_requires_recheck_evidence_instead_of_a_readme_url(self):
        entry = dict(SCOPE['scan-1377172300'])
        del entry['availability_check']
        self.assertTrue(any('missing or unknown fields' in error for error in errors_for({'scan-1377172300': entry})))
        self.assertTrue(any('availability_check recheck result' in error for error in errors_for({'scan-1377172300': entry})))
        url = {**SCOPE['scan-1377172300'], 'evidence_url': RECORDS[1]['readme_url']}
        self.assertTrue(any('missing or unknown fields' in error for error in errors_for({'scan-1377172300': url})))
        # Other reasons keep the README URL binding and cannot carry recheck evidence.
        other = {**SCOPE['scan-1377172300'], 'reason_code': 'unrelated-project-purpose'}
        errors = errors_for({'scan-1377172300': other})
        self.assertTrue(any('missing or unknown fields' in error for error in errors))
        self.assertTrue(any('evidence URL differs' in error for error in errors))
        for field in ('http_status', 'recorded_name_http_status', 'observed_at'):
            with self.subTest(field=field):
                changed = copy.deepcopy(SCOPE)
                del changed['scan-1377172300']['availability_check'][field]
                self.assertTrue(any('availability_check has missing or unknown fields' in error for error in errors_for(changed)))

    def test_records_whose_id_still_resolves_are_rejected(self):
        renamed = {'outcome': 'renamed', 'http_status': None, 'recorded_name_status': 'redirects-to-scanned-id',
                   'recorded_name_http_status': 200}
        for outcome in ('available', 'renamed', 'transferred', 'ineligible', 'inconclusive'):
            with self.subTest(outcome=outcome):
                errors = errors_for(with_check('scan-1377172300', **{**renamed, 'outcome': outcome}))
                self.assertTrue(any('scanned ID no longer resolves' in error for error in errors))
        # Statuses must match the outcome: a resolved ID or name is not a gone upstream.
        for identifier, changes, message in (
                ('scan-1377172300', {'http_status': 200}, 'ID lookup status'),
                ('scan-1377172300', {'http_status': '404'}, 'ID lookup status'),
                ('scan-1377172300', {'http_status': 451}, 'ID lookup status'),
                ('scan-1377172300', {'recorded_name_http_status': 200}, 'recorded-name lookup'),
                ('scan-1377172300', {'recorded_name_status': 'private'}, 'recorded-name lookup'),
                ('scan-1238268014', {'recorded_name_http_status': 404}, 'recorded-name lookup'),
                ('scan-1238268014', {'recorded_name_status': 'redirects-to-scanned-id'}, 'recorded-name lookup'),
                ('scan-1238268014', {'recorded_name_repository_id': 'scan-1238268014'}, 'other repository ID'),
                ('scan-1238268014', {'recorded_name_repository_id': 1244345068}, 'other repository ID'),
                ('scan-1238268014', {'recorded_name_current_full_name': 'someone/else'}, "other repository's current name")):
            with self.subTest(changes=changes):
                self.assertTrue(any(message in error for error in errors_for(with_check(identifier, **changes))))

    def test_evidence_must_belong_to_the_record_and_follow_its_scan(self):
        for changes, message in (({'id': 'scan-1238268014'}, 'must name the scanned ID'),
                                 ({'recorded_full_name': 'owner/other-tool'}, 'must name the scanned ID'),
                                 ({'observed_at': '2026-10-16T07:00:00Z'}, 'follow the README scan'),
                                 ({'observed_at': '2026-10-18T00:00:01Z'}, 'precede the review'),
                                 ({'observed_at': '2026-10-17T13:47:10'}, 'timezone-aware')):
            with self.subTest(changes=changes):
                self.assertTrue(any(message in error for error in errors_for(with_check('scan-1377172300', **changes))))
        timestamped = copy.deepcopy(SCOPE)
        timestamped['scan-1377172300']['reviewed_at'] = '2026-10-17T13:00:00Z'
        self.assertTrue(any('precede the review' in error for error in errors_for(timestamped)))

    def test_both_reasons_state_the_observed_lookup_results(self):
        for field, old, new in (('reason_en', '2026-10-17', '2026-10-16'), ('reason_zh', 'HTTP 404', '404'),
                                ('reason_en', '1377172300', 'this repository'),
                                ('reason_zh', 'owner/gone-tool', '该仓库')):
            with self.subTest(field=field, old=old):
                changed = copy.deepcopy(SCOPE)
                changed['scan-1377172300'][field] = changed['scan-1377172300'][field].replace(old, new)
                self.assertTrue(any(f'{field} must state' in error for error in errors_for(changed)))
        changed = copy.deepcopy(SCOPE)
        changed['scan-1238268014']['reason_zh'] = changed['scan-1238268014']['reason_zh'].replace('（ID 1244345068）', '')
        self.assertTrue(any('reason_zh must state' in error for error in errors_for(changed)))


class WordingTests(unittest.TestCase):
    def test_unavailable_upstreams_are_not_called_out_of_scope(self):
        self.assertEqual(unavailable_clause(0, False), '')
        self.assertEqual(unavailable_clause(0, True), '')
        self.assertEqual(unavailable_clause(3, False, '**'), ' and **3** whose upstream repository is no longer available')
        self.assertEqual(unavailable_clause(3, True), '及 3 个上游仓库已无法访问的条目')
        self.assertEqual(exclusion_counts([{'scope_status': 'excluded'}, {}]), (1, 0))


class CollectionTests(unittest.TestCase):
    """The reviewed records stay in the scan, leave browsing and are never linked by their old names."""

    @classmethod
    def setUpClass(cls):
        cls.records = json.loads((ROOT / 'data/source-index.json').read_text(encoding='utf-8'))['resources']
        cls.scope = read_scope(ROOT)

    def test_reviewed_records_are_excluded_with_gone_outcomes(self):
        self.assertEqual(errors_for(self.scope, self.records), [])
        unavailable = {identifier: entry for identifier, entry in self.scope.items()
                       if entry['reason_code'] == UNAVAILABLE_UPSTREAM_REASON}
        self.assertEqual({identifier: entry['availability_check']['outcome'] for identifier, entry in unavailable.items()},
                         REVIEWED)
        self.assertEqual(unavailable['scan-1238268014']['availability_check']['recorded_name_repository_id'],
                         'scan-1244345068')
        replaced = unavailable['scan-1417013841']['availability_check']
        self.assertEqual((replaced['http_status'], replaced['recorded_name_http_status'],
                          replaced['recorded_name_repository_id']), (404, 200, 'scan-1423698173'))
        historical = next(record for record in self.records if record['id'] == 'scan-1417013841')
        self.assertEqual(historical['observed_at'], '2026-10-16T01:36:34.940061Z')
        self.assertEqual(historical['readme_sha256'],
                         '1530ac107640676f69c7f8654819cc0ead165e2d6c2f006de0d480e1b111e403')
        self.assertNotIn('scan-1423698173', {record['id'] for record in self.records})
        scoped = apply_scope(self.records, self.scope)
        self.assertEqual(len(scoped), 3000)
        self.assertEqual(exclusion_counts(scoped)[1], 4)
        self.assertEqual({record['id'] for record in scoped if record['id'] in REVIEWED
                          and record['scope_status'] == 'excluded'}, set(REVIEWED))

    def test_directories_and_readmes_do_not_link_unavailable_names(self):
        names = [record['full_name'] for record in self.records if record['id'] in REVIEWED]
        self.assertEqual(len(names), 4)
        paths = [ROOT / 'README.md', ROOT / 'README.zh-CN.md', *sorted((ROOT / 'docs/repositories').glob('*.md'))]
        for path in paths:
            text = path.read_text(encoding='utf-8')
            for name in names:
                self.assertNotIn('github.com/' + name, text, f'{path.name} links {name}')
        index = (ROOT / 'docs/repositories/README.md').read_text(encoding='utf-8')
        self.assertIn('**4** whose upstream repository is no longer available', index)


if __name__ == '__main__':
    unittest.main()
