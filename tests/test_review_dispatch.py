"""A dispatched review binds to the dispatched commit and runs only the trusted default-branch checkout."""
import contextlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import review_pr
from test_review_pr import NUMBER, REPOSITORY, SHA, FakeGitHub, added, base, entry

MAIN_SHA = 'c' * 40
BRANCH = 'automation/discovery-ingest'


class DispatchGitHub(FakeGitHub):
    """The same in-memory API, with the PR fields a dispatched review checks."""

    def __init__(self, *args, pull=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pull = {'state': 'open', 'head': {'ref': BRANCH, 'repo': {'full_name': REPOSITORY}},
                     'base': {'ref': 'main', 'repo': {'full_name': REPOSITORY}}}
        for key, value in (pull or {}).items():
            self.pull[key] = {**self.pull[key], **value} if isinstance(value, dict) else value

    def __call__(self, repository, endpoint, token, method='GET', payload=None, raw=False):
        result = super().__call__(repository, endpoint, token, method, payload, raw)
        if method == 'GET' and endpoint == f'pulls/{NUMBER}':
            head = {**self.pull['head'], 'sha': result['head']['sha']}
            return {**result, **self.pull, 'head': head}
        return result

    def checks(self):
        return [payload for method, path, payload in self.posted if path == 'check-runs']

    def body(self):
        return [payload for method, path, payload in self.posted if path != 'check-runs'][-1]['body']


def dispatched_review(github, *, inputs=None, ref='refs/heads/main'):
    with tempfile.TemporaryDirectory() as directory:
        event = Path(directory) / 'event.json'
        event.write_text(json.dumps({'inputs': {'pr_number': str(NUMBER), 'head_sha': SHA} if inputs is None else inputs,
                                     'repository': {'default_branch': 'main'}}))
        environment = {'GITHUB_TOKEN': 'test-token', 'GITHUB_REPOSITORY': REPOSITORY, 'GITHUB_EVENT_PATH': str(event),
                       'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_SHA': MAIN_SHA, 'GITHUB_REF': ref,
                       'GITHUB_RUN_ID': '123', 'GITHUB_SERVER_URL': 'https://github.com'}
        output, errors = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, environment), patch.object(review_pr, 'api', github), \
                patch.object(review_pr.urllib.request, 'urlopen', side_effect=AssertionError('network access')), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            try:
                review_pr.main()
                status = 0
            except SystemExit as exit_status:
                status = exit_status.code
            except ValueError as error:
                status = str(error)
    return status, output.getvalue() + errors.getvalue()


def scope_change():
    return [entry(review_pr.SOURCE_SCOPE, added('x'))], {review_pr.SOURCE_SCOPE: base(review_pr.SOURCE_SCOPE)}


class DispatchedReviewTest(unittest.TestCase):
    def test_review_of_the_named_head_reports_the_required_check_on_that_commit(self):
        github = DispatchGitHub(*scope_change())
        status, output = dispatched_review(github)
        self.assertEqual(status, 0, output)
        self.assertIn('**No issues found by these automatic checks.**', github.body())
        self.assertIn(f'trusted default-branch code at `{MAIN_SHA[:12]}`', github.body())
        self.assertEqual([method for method, path, _ in github.posted], ['POST', 'POST'])
        [check] = github.checks()
        self.assertEqual((check['name'], check['head_sha'], check['status'], check['conclusion']),
                         ('review', SHA, 'completed', 'success'))
        self.assertEqual(check['details_url'], f'https://github.com/{REPOSITORY}/actions/runs/123')
        self.assertEqual(check['external_id'], f'pull-request-{NUMBER}')

    def test_findings_fail_both_the_job_and_the_reported_check(self):
        github = DispatchGitHub([entry(review_pr.SOURCE_SCOPE, added('x'))], {review_pr.SOURCE_SCOPE: '{"broken": '})
        status, _ = dispatched_review(github)
        self.assertEqual(status, 1)
        [check] = github.checks()
        self.assertEqual((check['head_sha'], check['conclusion']), (SHA, 'failure'))
        self.assertIn('need attention', check['output']['title'])

    def test_refusals_report_no_check_and_fetch_no_data(self):
        cases = {
            'moved head': ({}, {'inputs': {'pr_number': str(NUMBER), 'head_sha': 'd' * 40}}),
            'closed': ({'state': 'closed'}, {}),
            'fork head': ({'head': {'repo': {'full_name': 'someone/fork'}}}, {}),
            'other base': ({'base': {'ref': 'release'}}, {}),
            'dispatched on a PR branch': ({}, {'ref': f'refs/heads/{BRANCH}'}),
        }
        for name, (pull, overrides) in cases.items():
            with self.subTest(name):
                github = DispatchGitHub(*scope_change(), pull=pull)
                status, output = dispatched_review(github, **overrides)
                self.assertEqual(status, 1, output)
                self.assertIn('Dispatched review refused', output)
                self.assertEqual((github.posted, github.fetched()), ([], []))

    def test_a_head_that_moves_during_review_gets_no_check(self):
        github = DispatchGitHub(*scope_change(), heads=(SHA, 'e' * 40))
        status, output = dispatched_review(github)
        self.assertEqual(status, 1, output)
        self.assertEqual((github.posted, github.checks()), ([], []))

    def test_dispatch_needs_an_explicit_pull_request_and_full_head_sha(self):
        for value in ({}, {'pr_number': '', 'head_sha': SHA}, {'pr_number': '0', 'head_sha': SHA},
                      {'pr_number': '7; true', 'head_sha': SHA}, {'pr_number': '-7', 'head_sha': SHA},
                      {'pr_number': '7'}, {'pr_number': '7', 'head_sha': SHA[:12]}, {'pr_number': '7', 'head_sha': 'main'}):
            with self.subTest(value=value):
                github = DispatchGitHub(*scope_change())
                status, _ = dispatched_review(github, inputs=value)
                self.assertIn('A dispatched review needs', str(status))
                self.assertEqual((github.requests, github.posted), ([], []))


class DispatchWorkflowTest(unittest.TestCase):
    def test_review_dispatch_runs_only_the_default_branch_definition_and_code(self):
        text = (ROOT / '.github/workflows/review.yml').read_text(encoding='utf-8')
        trigger = text.split('\non:\n', 1)[1].split('\npermissions:\n', 1)[0] + '\n'
        self.assertIn('  pull_request_target:\n', trigger)
        self.assertIn('  workflow_dispatch:\n    inputs:\n      pr_number:\n', trigger)
        self.assertIn('      head_sha:\n', trigger)
        self.assertEqual(trigger.count('required: true'), 2)
        self.assertIn('\npermissions:\n  contents: read\nconcurrency:', text)
        self.assertIn('group: review-${{ github.event.pull_request.number || inputs.pr_number }}', text)
        self.assertNotIn('pull_request.head', text)
        jobs = text.split('\njobs:\n', 1)[1]
        self.assertEqual(re.findall(r'^  ([a-z-]+):$', jobs, re.MULTILINE), ['review', 'dispatched-review'])
        review, dispatched = jobs.split('\n  dispatched-review:\n')
        # The required `review` job keeps its pull_request_target trigger, base checkout and permissions.
        self.assertIn("if: ${{ github.event_name == 'pull_request_target' }}", review)
        self.assertIn('ref: ${{ github.event.pull_request.base.sha }}', review)
        self.assertIn('    permissions:\n      contents: read\n      pull-requests: write\n    steps:', review)
        # A dispatch runs only on the default branch, checking out that branch's own commit.
        self.assertIn("if: ${{ github.event_name == 'workflow_dispatch' && github.ref == format('refs/heads/{0}', "
                      "github.event.repository.default_branch) }}", dispatched)
        self.assertNotIn('ref:', dispatched)
        self.assertIn('    permissions:\n      contents: read\n      pull-requests: write\n      checks: write\n', dispatched)
        for job in (review, dispatched):
            self.assertIn('persist-credentials: false', job)
            self.assertIn('run: python3 scripts/review_pr.py', job)
        # Inputs reach the reviewer through its event payload, never through shell interpolation.
        for line in text.splitlines():
            if line.strip().startswith('run:'):
                self.assertNotIn('${{', line)

    def test_catalog_checks_can_be_dispatched_on_a_branch(self):
        text = (ROOT / '.github/workflows/validate.yml').read_text(encoding='utf-8')
        trigger = text.split('\non:\n', 1)[1].split('\npermissions:\n', 1)[0] + '\n'
        self.assertIn('  push:\n    branches: [main]\n', trigger)
        self.assertIn('  pull_request:\n', trigger)
        self.assertIn('  workflow_dispatch:\n', trigger)
        self.assertIn('permissions:\n  contents: read\n', text)
        self.assertNotIn(': write', text)


if __name__ == '__main__':
    unittest.main()
