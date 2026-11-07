"""The ingest workflow path: commit scope, dispatched checks, bounded retries, merge and failure tracking."""
import json
import os
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import ingest_discoveries as ingest


class FakeAPI:
    """Record every call; answer from a routing table of (method, endpoint prefix) -> response or exception."""

    def __init__(self, routes):
        self.routes, self.calls = routes, []
        self.repository = 'reacher-z/Awesome-REA'

    def call(self, method, endpoint, payload=None, *, expected=(200, 201, 204)):
        self.calls.append((method, endpoint, payload))
        for (verb, prefix), response in self.routes.items():
            if verb == method and endpoint.startswith(prefix):
                value = response(endpoint, payload) if callable(response) else response
                if isinstance(value, Exception):
                    raise value
                return value
        raise AssertionError(f'unexpected {method} {endpoint}')

    def get(self, endpoint):
        return self.call('GET', endpoint)[1]


class CommitTest(unittest.TestCase):
    def test_only_a_batch_file_is_committed_on_the_named_base(self):
        api = FakeAPI({('GET', 'git/commits/'): (200, {'tree': {'sha': 't' * 40}}),
                       ('POST', 'git/blobs'): (201, {'sha': 'b' * 40}),
                       ('POST', 'git/trees'): (201, {'sha': 'n' * 40}),
                       ('POST', 'git/commits'): (201, {'sha': 'c' * 40}),
                       ('PATCH', 'git/refs/heads/'): (422, None),
                       ('POST', 'git/refs'): (201, {})})
        path = ROOT / 'data/discoveries/run-1-1.json'
        with patch.object(Path, 'read_bytes', return_value=b'{}\n'):
            self.assertEqual(ingest.commit_batch(api, 'a' * 40, path, 'Ingest 1 unreviewed discovery records from scan run 1'), 'c' * 40)
        tree = next(payload for method, endpoint, payload in api.calls if endpoint == 'git/trees')
        self.assertEqual(tree['base_tree'], 't' * 40)
        self.assertEqual([(entry['path'], entry['mode']) for entry in tree['tree']], [('data/discoveries/run-1-1.json', '100644')])
        commit = next(payload for method, endpoint, payload in api.calls if endpoint == 'git/commits')
        self.assertEqual(commit['parents'], ['a' * 40])
        self.assertEqual(api.calls[-1][1:], ('git/refs', {'ref': f'refs/heads/{ingest.BRANCH}', 'sha': 'c' * 40}))
        for other in ('data/tool-resources.json', 'scripts/discoveries.py', 'data/discoveries/README.md'):
            with self.subTest(other), self.assertRaises(ValueError):
                ingest.commit_batch(api, 'a' * 40, ROOT / other, 'x')

    def test_required_checks_are_dispatched_on_the_branch_and_the_trusted_default_branch(self):
        api = FakeAPI({('POST', 'actions/workflows/'): (204, None)})
        ingest.dispatch_checks(api, 'main', 42, 'f' * 40)
        self.assertEqual(api.calls, [
            ('POST', 'actions/workflows/validate.yml/dispatches', {'ref': ingest.BRANCH}),
            ('POST', 'actions/workflows/review.yml/dispatches',
             {'ref': 'main', 'inputs': {'pr_number': '42', 'head_sha': 'f' * 40}})])


class WaitAndMergeTest(unittest.TestCase):
    def test_check_results_follow_the_commit_statuses_that_protection_counts(self):
        def answers(statuses, runs):
            def respond(endpoint, payload):
                if endpoint.endswith('/status'):
                    return 200, {'statuses': [{'context': name, 'state': state} for name, state in statuses.items()]}
                name = re.search(r'check_name=([a-z]+)', endpoint)[1]
                return 200, {'check_runs': runs.get(name, [])}
            return FakeAPI({('GET', 'commits/'): respond})
        run = lambda identifier, status, conclusion, app='github-actions': {'id': identifier, 'status': status, 'conclusion': conclusion, 'app': {'slug': app}}
        api = answers({'validate': 'success', 'review': 'success'}, {})
        self.assertEqual(ingest.check_results(api, 'f' * 40), {'validate': ('completed', 'success'), 'review': ('completed', 'success')})
        # A green check run alone is not enough: protection waits for the status.
        api = answers({'validate': 'pending'}, {'validate': [run(1, 'completed', 'success')], 'review': [run(2, 'in_progress', None)]})
        self.assertEqual(ingest.check_results(api, 'f' * 40), {'validate': ('pending', None), 'review': ('pending', None)})
        # A failed run that reported no status, or a failed status, ends the wait as a failure.
        api = answers({'review': 'error'}, {'validate': [run(1, 'completed', 'success'), run(3, 'completed', 'failure'),
                                                         run(9, 'completed', 'success', 'other-app')]})
        self.assertEqual(ingest.check_results(api, 'f' * 40), {'validate': ('completed', 'failure'), 'review': ('completed', 'failure')})
        self.assertEqual(ingest.check_results(answers({}, {}), 'f' * 40), {'validate': ('missing', None), 'review': ('missing', None)})
        # A rerun on the same commit: the newest status comes first and decides.
        rerun = FakeAPI({('GET', 'commits/'): lambda endpoint, payload: (200, {'statuses': [
            {'context': 'validate', 'state': 'success'}, {'context': 'review', 'state': 'success'},
            {'context': 'validate', 'state': 'failure'}]})})
        self.assertEqual(ingest.check_results(rerun, 'f' * 40)['validate'], ('completed', 'success'))

    def test_a_moving_default_branch_means_rebuild_not_merge(self):
        api = FakeAPI({('GET', 'commits/'): (200, {'check_runs': []}),
                       ('GET', 'branches/main'): (200, {'commit': {'sha': 'e' * 40}})})
        with self.assertRaises(ingest.Retry):
            ingest.wait_for_checks(api, 'f' * 40, 'main', 'a' * 40, deadline=float('inf'))

    def test_a_check_still_queued_after_the_old_14_minutes_is_waited_for(self):
        # Run 42223736734 gave up 36 seconds before `validate` passed: its jobs had queued for 11 minutes.
        started, clock = 1000.0, [1000.0]

        def statuses(endpoint, payload):
            done = clock[0] - started >= 15 * 60
            return (200, {'statuses': [{'context': name, 'state': 'success'} for name in ingest.CHECK_NAMES] if done else [],
                          'check_runs': []})

        api = FakeAPI({('GET', 'commits/'): statuses, ('GET', 'branches/main'): (200, {'commit': {'sha': 'a' * 40}})})
        with patch.object(ingest.time, 'monotonic', lambda: clock[0]), \
                patch.object(ingest.time, 'sleep', lambda seconds: clock.__setitem__(0, clock[0] + seconds)):
            results = ingest.wait_for_checks(api, 'f' * 40, 'main', 'a' * 40, ingest.check_deadline(started))
        self.assertEqual(results, dict.fromkeys(ingest.CHECK_NAMES, ('completed', 'success')))

    def test_the_wait_ends_in_time_to_merge_within_the_job_limit(self):
        started, clock = 1000.0, [1000.0]
        api = FakeAPI({('GET', 'commits/'): (200, {'statuses': [], 'check_runs': []}),
                       ('GET', 'branches/main'): (200, {'commit': {'sha': 'a' * 40}})})
        with patch.object(ingest.time, 'monotonic', lambda: clock[0]), \
                patch.object(ingest.time, 'sleep', lambda seconds: clock.__setitem__(0, clock[0] + seconds)), \
                self.assertRaisesRegex(RuntimeError, 'did not finish in time'):
            ingest.wait_for_checks(api, 'f' * 40, 'main', 'a' * 40, ingest.check_deadline(started))
        waited = clock[0] - started
        self.assertGreaterEqual(waited, 38 * 60)
        self.assertLessEqual(waited + ingest.MERGEABILITY_WAIT_SECONDS, 44 * 60)

    def test_merge_rebases_the_checked_head_and_retries_when_it_is_outdated(self):
        api = FakeAPI({('PUT', 'pulls/7/merge'): (200, {'sha': 'm' * 40})})
        self.assertEqual(ingest.merge(api, 7, 'f' * 40, 'Ingest 2 unreviewed discovery records from scan run 5'), 'm' * 40)
        # A rebase keeps the one commit with its fixed message and its bot author; never squash or merge commits.
        self.assertEqual(api.calls[0][2], {'merge_method': 'rebase', 'sha': 'f' * 40})
        for status in (405, 409):
            stale = FakeAPI({('PUT', 'pulls/7/merge'): ingest.ApiError(status, 'Base branch was modified')})
            with self.subTest(status), self.assertRaises(ingest.Retry):
                ingest.merge(stale, 7, 'f' * 40, 'x')
        moved = FakeAPI({('PUT', 'pulls/7/merge'): ingest.ApiError(405, 'Head branch is out of date'),
                         ('GET', 'branches/main'): (200, {'commit': {'sha': 'e' * 40}})})
        with self.assertRaises(ingest.Retry):
            ingest.merge(moved, 7, 'f' * 40, 'x', 'main', 'a' * 40)
        self.assertEqual(sum(endpoint == 'pulls/7/merge' for _, endpoint, _ in moved.calls), 1)
        broken = FakeAPI({('PUT', 'pulls/7/merge'): ingest.ApiError(403, 'Resource not accessible')})
        with self.assertRaises(ingest.ApiError):
            ingest.merge(broken, 7, 'f' * 40, 'x')

    def test_a_refused_merge_on_a_current_branch_is_asked_again(self):
        answers = iter([ingest.ApiError(405, 'Pull Request is not mergeable'), (200, {'sha': 'm' * 40})])
        api = FakeAPI({('PUT', 'pulls/7/merge'): lambda endpoint, payload: next(answers),
                       ('GET', 'branches/main'): (200, {'commit': {'sha': 'a' * 40}})})
        with patch.object(ingest.time, 'sleep') as sleep:
            self.assertEqual(ingest.merge(api, 7, 'f' * 40, 'x', 'main', 'a' * 40), 'm' * 40)
        self.assertEqual(sleep.call_count, 1)
        always = FakeAPI({('PUT', 'pulls/7/merge'): ingest.ApiError(405, 'Pull Request is not mergeable'),
                          ('GET', 'branches/main'): (200, {'commit': {'sha': 'a' * 40}})})
        with patch.object(ingest.time, 'sleep'), self.assertRaises(ingest.Retry):
            ingest.merge(always, 7, 'f' * 40, 'x', 'main', 'a' * 40)
        self.assertEqual(sum(endpoint == 'pulls/7/merge' for _, endpoint, _ in always.calls), ingest.MERGE_REQUESTS)

    def test_mergeability_is_awaited_after_the_checks(self):
        states = iter(['blocked', 'unknown', 'clean'])
        api = FakeAPI({('GET', 'pulls/7'): lambda endpoint, payload: (200, {'mergeable_state': next(states), 'head': {'sha': 'f' * 40}}),
                       ('GET', 'branches/main'): (200, {'commit': {'sha': 'a' * 40}})})
        with patch.object(ingest.time, 'sleep') as sleep:
            self.assertEqual(ingest.wait_until_mergeable(api, 7, 'f' * 40, 'main', 'a' * 40), 'clean')
        self.assertEqual(sleep.call_count, 2)
        behind = FakeAPI({('GET', 'pulls/7'): (200, {'mergeable_state': 'behind', 'head': {'sha': 'f' * 40}})})
        with self.assertRaises(ingest.Retry):
            ingest.wait_until_mergeable(behind, 7, 'f' * 40, 'main', 'a' * 40)
        stuck = FakeAPI({('GET', 'pulls/7'): (200, {'mergeable_state': 'blocked', 'head': {'sha': 'f' * 40}}),
                         ('GET', 'branches/main'): (200, {'commit': {'sha': 'a' * 40}})})
        clock = iter(range(0, 10_000, 30))
        with patch.object(ingest.time, 'sleep'), patch.object(ingest.time, 'monotonic', lambda: next(clock)), \
                self.assertRaisesRegex(RuntimeError, 'branch protection did not accept them'):
            ingest.wait_until_mergeable(stuck, 7, 'f' * 40, 'main', 'a' * 40)

    def test_pull_request_title_and_body_state_the_records_stay_unreviewed(self):
        source = {'repository': 'reacher-z/Awesome-REA', 'run_id': 5, 'run_attempt': 1, 'artifact_name': 'readme-scan-checkpoint-1',
                  'artifact_digest': 'sha256:' + 'b' * 64, 'checkpoint_sha256': 'c' * 64, 'head_sha': 'a' * 40}
        body = ingest.pull_request_body(12, source, ROOT / 'data/discoveries/run-5-1.json', 1)
        self.assertIn('`data/discoveries/run-5-1.json` with 12 exact README capture records', body)
        self.assertIn('`unreviewed`', body)
        self.assertIn('## Validation', body)
        self.assertEqual(ingest.LABEL.format(count=12, run=5), 'Ingest 12 unreviewed discovery records from scan run 5')


class RunTest(unittest.TestCase):
    """The whole workflow path with the network, Git and subprocesses replaced."""

    def commit(self, github, base, path, title):
        self.heads.append('h' + base[1:])
        return self.heads[-1]

    def run_ingest(self, routes, prepared, *, bases=('a' * 40,)):
        self.heads = getattr(self, 'heads', [])
        api = FakeAPI(routes)
        bases = iter(bases)
        source = {'repository': 'reacher-z/Awesome-REA', 'run_id': 5, 'run_attempt': 1, 'artifact_name': 'readme-scan-checkpoint-1',
                  'artifact_digest': 'sha256:' + 'b' * 64, 'checkpoint_sha256': 'c' * 64, 'head_sha': 'a' * 40}
        environment = {'GITHUB_REPOSITORY': 'reacher-z/Awesome-REA', 'GH_TOKEN': 'token', 'DEFAULT_BRANCH': 'main',
                       'GITHUB_REF': 'refs/heads/main', 'GITHUB_RUN_ID': '5', 'GITHUB_RUN_ATTEMPT': '1'}
        completed = type('Completed', (), {'returncode': 0, 'stdout': json.dumps(prepared) + '\n', 'stderr': ''})
        with patch.dict(os.environ, environment), patch.object(ingest, 'GitHub', return_value=api), \
                patch.object(ingest, 'restore_checkpoint', return_value=(None, {'outcome': 'partial'}, source)), \
                patch.object(ingest, 'refresh_tree', side_effect=lambda branch: next(bases)), \
                patch.object(ingest.subprocess, 'run', return_value=completed), \
                patch.object(ingest, 'run_validators'), patch.object(ingest.time, 'sleep'), \
                patch.object(ingest, 'commit_batch', side_effect=self.commit):
            status = ingest.run()
        return status, api

    def routes(self, *, main_sha='a' * 40, conclusion='success', merge=(200, {'sha': 'm' * 40})):
        checks = lambda endpoint, payload: ((200, {'statuses': [{'context': name, 'state': conclusion} for name in ingest.CHECK_NAMES]})
                                            if endpoint.endswith('/status') else (200, {'check_runs': []}))
        # The fake commit for base B is 'h' + B[1:]; the latest one is the pull request head.
        pull = lambda endpoint, payload: (200, {'mergeable_state': 'clean', 'head': {'sha': self.heads[-1]}})
        return {('GET', 'pulls?'): (200, []), ('POST', 'pulls'): (201, {'number': 7}),
                ('GET', 'pulls/7'): pull,
                ('POST', 'actions/workflows/'): (204, None), ('GET', 'commits/'): checks,
                ('GET', 'branches/main'): (200, {'commit': {'sha': main_sha}}),
                ('PUT', 'pulls/7/merge'): merge, ('DELETE', 'git/refs/heads/'): (204, None)}

    def test_happy_path_opens_dispatches_merges_and_deletes_the_branch(self):
        prepared = {'path': 'data/discoveries/run-5-1.json', 'status': 'selected', 'records': 3}
        status, api = self.run_ingest(self.routes(), prepared)
        self.assertEqual(status, 0)
        endpoints = [(method, endpoint.split('?')[0]) for method, endpoint, _ in api.calls]
        self.assertIn(('POST', 'pulls'), endpoints)
        self.assertEqual(endpoints.count(('POST', 'actions/workflows/validate.yml/dispatches')), 1)
        self.assertEqual(endpoints.count(('POST', 'actions/workflows/review.yml/dispatches')), 1)
        merge = next(payload for method, endpoint, payload in api.calls if endpoint == 'pulls/7/merge')
        self.assertEqual(merge['sha'], 'h' + 'a' * 39)
        self.assertEqual(endpoints[-1], ('DELETE', f'git/refs/heads/{ingest.BRANCH}'))

    def test_an_outdated_branch_is_rebuilt_on_the_new_main_and_merged(self):
        prepared = {'path': 'data/discoveries/run-5-1.json', 'status': 'selected', 'records': 3}
        main = ['a' * 40]
        def merge(endpoint, payload):
            if payload['sha'] == 'h' + 'a' * 39:
                main[0] = 'b' * 40  # another pull request merged while this one was checked
                return ingest.ApiError(405, 'Head branch is out of date')
            return (200, {'sha': 'm' * 40})
        routes = self.routes(merge=merge)
        routes[('GET', 'branches/main')] = lambda endpoint, payload: (200, {'commit': {'sha': main[0]}})
        status, api = self.run_ingest(routes, prepared, bases=('a' * 40, 'b' * 40))
        self.assertEqual(status, 0)
        merges = [payload['sha'] for method, endpoint, payload in api.calls if endpoint == 'pulls/7/merge']
        self.assertEqual(merges, ['h' + 'a' * 39, 'h' + 'b' * 39])

    def test_failed_checks_stop_without_merging(self):
        prepared = {'path': 'data/discoveries/run-5-1.json', 'status': 'selected', 'records': 3}
        with self.assertRaisesRegex(RuntimeError, 'Required checks failed'):
            self.run_ingest(self.routes(conclusion='failure'), prepared)

    def test_nothing_new_opens_no_pull_request_and_a_full_budget_fails(self):
        status, api = self.run_ingest({}, {'path': None, 'status': 'nothing-new', 'records': 0})
        self.assertEqual((status, api.calls), (0, []))
        with self.assertRaisesRegex(RuntimeError, 'budget'):
            self.run_ingest({}, {'path': None, 'status': 'budget-reached', 'records': 0})


class TrackerTest(unittest.TestCase):
    def run_report(self, issues, results):
        api = FakeAPI({('GET', 'issues?'): (200, issues), ('PATCH', 'issues/'): (200, {}),
                       ('POST', 'issues/'): (201, {}), ('POST', 'issues'): (201, {'number': 99})})
        environment = {'GITHUB_REPOSITORY': 'reacher-z/Awesome-REA', 'GH_TOKEN': 'token', 'GITHUB_RUN_ID': '123'}
        with patch.dict(os.environ, environment), patch.object(ingest, 'GitHub', return_value=api):
            self.assertEqual(ingest.report('readme-discovery', results), 0)
        return [(method, endpoint.split('?')[0]) for method, endpoint, _ in api.calls], api.calls

    def test_first_failure_opens_one_issue_and_later_failures_only_edit_it(self):
        calls, raw = self.run_report([], {'scan': 'success', 'ingest': 'failure'})
        self.assertEqual(calls, [('GET', 'issues'), ('POST', 'issues')])
        body = raw[-1][2]['body']
        self.assertIn(ingest.tracker_marker('readme-discovery'), body)
        self.assertIn('| Consecutive failed runs | 1 |', body)
        self.assertIn('| ingest job | failure |', body)
        open_issue = {'number': 5, 'state': 'open', 'body': body}
        calls, raw = self.run_report([open_issue], {'scan': 'failure', 'ingest': 'skipped'})
        self.assertEqual(calls, [('GET', 'issues'), ('PATCH', 'issues/5')])
        self.assertIn('| Consecutive failed runs | 2 |', raw[-1][2]['body'])
        self.assertEqual(ingest.tracker_state(raw[-1][2]['body'])['first_failure_at'], ingest.tracker_state(body)['first_failure_at'])

    def test_a_skipped_failed_stage_keeps_the_issue_open(self):
        body = ingest.tracker_marker('readme-discovery') + '\n<!-- tracker-state: {"count": 1, "failed_jobs": ["ingest"]} -->'
        calls, _ = self.run_report([{'number': 5, 'state': 'open', 'body': body}], {'scan': 'success', 'ingest': 'skipped'})
        self.assertEqual(calls, [('GET', 'issues')])
        calls, _ = self.run_report([{'number': 5, 'state': 'open', 'body': body}], {'scan': 'success', 'ingest': 'success'})
        self.assertEqual(calls, [('GET', 'issues'), ('POST', 'issues/5/comments'), ('PATCH', 'issues/5')])

    def test_recovery_comments_and_closes_and_a_new_streak_reopens(self):
        body = ingest.tracker_marker('readme-discovery') + '\n<!-- tracker-state: {"count": 3} -->'
        calls, raw = self.run_report([{'number': 5, 'state': 'open', 'body': body}], {'scan': 'success', 'ingest': 'success'})
        self.assertEqual(calls, [('GET', 'issues'), ('POST', 'issues/5/comments'), ('PATCH', 'issues/5')])
        self.assertEqual(raw[-1][2]['state'], 'closed')
        calls, _ = self.run_report([{'number': 5, 'state': 'closed', 'body': body}], {'scan': 'success', 'ingest': 'skipped'})
        self.assertEqual(calls, [('GET', 'issues')])
        calls, raw = self.run_report([{'number': 5, 'state': 'closed', 'body': body}], {'scan': 'cancelled', 'ingest': 'skipped'})
        self.assertEqual(calls, [('GET', 'issues'), ('PATCH', 'issues/5'), ('POST', 'issues/5/comments')])
        self.assertIn('| Consecutive failed runs | 1 |', raw[1][2]['body'])
        other = {'number': 6, 'state': 'open', 'body': ingest.tracker_marker('artifact-leads')}
        pull = {'number': 7, 'state': 'open', 'body': body, 'pull_request': {}}
        calls, _ = self.run_report([other, pull], {'scan': 'failure'})
        self.assertEqual(calls, [('GET', 'issues'), ('POST', 'issues')])


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / '.github/workflows/source-scan.yml').read_text(encoding='utf-8')
        jobs = self.text.split('\njobs:\n', 1)[1]
        self.jobs = dict(zip(re.findall(r'^  ([a-z]+):$', jobs, re.MULTILINE), re.split(r'^  [a-z]+:$', jobs, flags=re.MULTILINE)[1:]))

    def test_jobs_permissions_and_time_limits(self):
        self.assertEqual(list(self.jobs), ['scan', 'ingest', 'report'])
        self.assertIn('permissions:\n  contents: read\n  actions: read\nconcurrency:\n  group: scheduled-readme-discovery\n  cancel-in-progress: false', self.text)
        writes = {name: re.findall(r'^      ([a-z-]+): write$', job, re.MULTILINE) for name, job in self.jobs.items()}
        self.assertEqual(writes, {'scan': [], 'ingest': ['contents', 'pull-requests', 'actions'], 'report': ['issues']})
        self.assertIn('      checks: read\n      statuses: read\n', self.jobs['ingest'])
        for name, job in self.jobs.items():
            minutes = int(re.search(r'timeout-minutes: ([0-9]+)', job)[1])
            self.assertLessEqual(minutes, 45 if name == 'ingest' else 30, name)
            self.assertIn('persist-credentials: false', job)
        self.assertIn("checkpoint_ready: ${{ steps.scan.outputs.checkpoint_ready }}", self.jobs['scan'])

    def test_ingest_runs_after_a_saved_checkpoint_and_report_always_runs(self):
        ingest_job, report_job = self.jobs['ingest'], self.jobs['report']
        self.assertIn('needs: scan', ingest_job)
        self.assertIn("needs.scan.outputs.checkpoint_ready == 'true'", ingest_job)
        self.assertIn('!github.event.repository.fork', ingest_job)
        self.assertIn("github.ref == format('refs/heads/{0}', github.event.repository.default_branch)", ingest_job)
        self.assertIn('run: python3 scripts/ingest_discoveries.py run', ingest_job)
        self.assertIn('needs: [scan, ingest]', report_job)
        self.assertIn('if: ${{ always() &&', report_job)
        self.assertIn('--tracker readme-discovery --result "scan=$SCAN_RESULT" --result "ingest=$INGEST_RESULT"', report_job)
        for line in self.text.splitlines():
            if line.strip().startswith('run:'):
                self.assertNotIn('${{', line)


if __name__ == '__main__':
    unittest.main()
