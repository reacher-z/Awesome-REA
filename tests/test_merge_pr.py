"""The merge workflow: dispatch-only, rebase with the workflow token, and a guard that checks before it merges."""
import io
import os
from pathlib import Path
import re
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import merge_pr

WORKFLOW = ROOT / '.github/workflows/merge-pr.yml'
HEAD, MAIN = 'a' * 40, 'b' * 40


class FakeGitHub:
    def __init__(self, pull=None, behind=0, statuses=(), runs=None):
        self.pull = {'state': 'open', 'draft': False, 'mergeable': True, 'mergeable_state': 'clean',
                     'base': {'ref': 'main'}, 'head': {'sha': HEAD}, **(pull or {})}
        self.behind, self.statuses, self.runs = behind, list(statuses), runs or {}
        self.requests = []

    def get(self, endpoint):
        self.requests.append(endpoint)
        if endpoint == 'pulls/7':
            return self.pull
        if endpoint == 'branches/main':
            return {'commit': {'sha': MAIN}}
        if endpoint == f'compare/{MAIN}...{HEAD}':
            return {'behind_by': self.behind}
        if endpoint == f'commits/{HEAD}/status':
            return {'statuses': [{'context': name, 'state': state} for name, state in self.statuses]}
        match = re.fullmatch(rf'commits/{HEAD}/check-runs\?check_name=([a-z]+)&per_page=30', endpoint)
        if match:
            return {'check_runs': self.runs.get(match[1], [])}
        raise AssertionError(f'unexpected endpoint {endpoint}')


def run(identifier, conclusion='success', status='completed', app='github-actions'):
    return {'id': identifier, 'status': status, 'conclusion': conclusion, 'app': {'slug': app}}


GREEN_RUNS = {'validate': [run(1)], 'review': [run(2)]}


class GuardTest(unittest.TestCase):
    def test_a_ready_current_checked_pull_request_returns_its_head(self):
        self.assertEqual(merge_pr.guard(FakeGitHub(runs=GREEN_RUNS), 7, 'main'), HEAD)
        # Automation pull requests report their dispatched checks as commit statuses.
        statuses = [('validate', 'success'), ('review', 'success')]
        self.assertEqual(merge_pr.guard(FakeGitHub(statuses=statuses), 7, 'main'), HEAD)

    def test_refusals_name_the_condition(self):
        cases = {
            'is not open': {'pull': {'state': 'closed'}},
            'is a draft': {'pull': {'draft': True}},
            'does not target main': {'pull': {'base': {'ref': 'release'}}},
            'is not mergeable': {'pull': {'mergeable': False}},
            'is behind main': {'behind': 2},
        }
        for reason, changes in cases.items():
            with self.subTest(reason), self.assertRaisesRegex(merge_pr.Refused, reason):
                merge_pr.guard(FakeGitHub(runs=GREEN_RUNS, **changes), 7, 'main')

    def test_every_required_check_must_have_succeeded_on_the_head(self):
        cases = {
            'missing review': {'runs': {'validate': [run(1)]}},
            'failed validate': {'runs': {'validate': [run(1), run(3, 'failure')], 'review': [run(2)]}},
            'running review': {'runs': {'validate': [run(1)], 'review': [run(2, None, 'in_progress')]}},
            'other app': {'runs': {'validate': [run(1, app='some-app')], 'review': [run(2)]}},
            'failed status beats a green run': {'runs': GREEN_RUNS, 'statuses': [('validate', 'failure')]},
            'pending status': {'statuses': [('validate', 'pending'), ('review', 'success')]},
        }
        for name, changes in cases.items():
            with self.subTest(name), self.assertRaisesRegex(merge_pr.Refused, 'required checks'):
                merge_pr.guard(FakeGitHub(**changes), 7, 'main')
        # The newest status of a context decides, as GitHub lists the newest first.
        rerun = FakeGitHub(statuses=[('validate', 'success'), ('review', 'success'), ('validate', 'failure')])
        self.assertEqual(merge_pr.guard(rerun, 7, 'main'), HEAD)

    def test_an_unknown_mergeability_is_awaited_then_refused(self):
        for pull, reason in (({'mergeable': None, 'mergeable_state': 'unknown'}, 'is not mergeable'),
                             ({'mergeable_state': 'blocked'}, "'blocked', not mergeable under branch protection")):
            github = FakeGitHub(pull=pull, runs=GREEN_RUNS)
            clock = iter(range(0, 1000, 30))
            with self.subTest(pull), patch.object(merge_pr.time, 'sleep'), \
                    patch.object(merge_pr.time, 'monotonic', lambda: next(clock)), self.assertRaisesRegex(merge_pr.Refused, reason):
                merge_pr.guard(github, 7, 'main')
            self.assertGreater(github.requests.count('pulls/7'), 1)

    def test_a_recomputing_pull_request_is_merged_once_ready(self):
        github = FakeGitHub(runs=GREEN_RUNS)
        states = iter(['unknown', 'blocked', 'unstable'])
        original = github.get
        def get(endpoint):
            value = original(endpoint)
            return {**value, 'mergeable_state': next(states)} if endpoint == 'pulls/7' else value
        github.get = get
        with patch.object(merge_pr.time, 'sleep') as sleep:
            self.assertEqual(merge_pr.guard(github, 7, 'main'), HEAD)
        self.assertEqual(sleep.call_count, 2)

    def test_main_prints_only_the_head_and_refuses_bad_input(self):
        environment = {'GITHUB_REPOSITORY': 'reacher-z/Awesome-REA', 'GH_TOKEN': 'token', 'DEFAULT_BRANCH': 'main'}
        for value in ('', '0', '7; true', 'abc'):
            with self.subTest(value), patch.dict(os.environ, {**environment, 'PR': value}), \
                    redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(merge_pr.main(), 1)
                self.assertIn('positive pull request number', errors.getvalue())
        output = io.StringIO()
        with patch.dict(os.environ, {**environment, 'PR': '7'}), patch.object(merge_pr, 'GitHub', return_value=FakeGitHub(runs=GREEN_RUNS)), \
                redirect_stdout(output):
            self.assertEqual(merge_pr.main(), 0)
        self.assertEqual(output.getvalue(), HEAD + '\n')
        with patch.dict(os.environ, {**environment, 'PR': '7'}), patch.object(merge_pr, 'GitHub', return_value=FakeGitHub(behind=1)), \
                redirect_stderr(io.StringIO()) as errors, redirect_stdout(io.StringIO()) as printed:
            self.assertEqual(merge_pr.main(), 1)
        self.assertEqual(printed.getvalue(), '')
        self.assertIn('Refused: pull request #7 is behind main', errors.getvalue())


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding='utf-8')

    def test_dispatch_only_with_a_required_pull_request_number(self):
        trigger = self.text.split('\non:\n', 1)[1].split('\npermissions:\n', 1)[0]
        self.assertEqual(trigger, '  workflow_dispatch:\n    inputs:\n      pr:\n'
                                  '        description: Number of the pull request to merge\n'
                                  '        required: true\n        type: number')
        self.assertIn("if: ${{ github.ref == format('refs/heads/{0}', github.event.repository.default_branch) }}", self.text)
        self.assertIn('concurrency:\n  group: merge-pr-${{ inputs.pr }}\n  cancel-in-progress: false\n', self.text)
        self.assertIn('    timeout-minutes: 10\n', self.text)

    def test_only_the_merge_job_writes(self):
        self.assertIn('\npermissions:\n  contents: read\nconcurrency:', self.text)
        job = self.text.split('\njobs:\n', 1)[1]
        self.assertEqual(re.findall(r'^  ([a-z-]+):$', job, re.MULTILINE), ['merge'])
        permissions = re.search(r'\n    permissions:\n((?:      .*\n)+)', job)[1]
        granted = re.findall(r'^      ([a-z-]+): ([a-z]+)$', permissions, re.MULTILINE)
        self.assertEqual(granted, [('contents', 'write'), ('pull-requests', 'write'), ('checks', 'read'), ('statuses', 'read')])

    def test_the_guard_runs_before_a_rebase_merge_of_the_checked_head(self):
        guard = self.text.index('python3 scripts/merge_pr.py')
        merge = self.text.index('if gh pr merge "$PR" --rebase --match-head-commit "$HEAD_SHA" -R "$GITHUB_REPOSITORY"; then')
        self.assertLess(guard, merge)
        self.assertIn('head=$(python3 scripts/merge_pr.py)\n', self.text)
        # The base is read again right before every merge attempt.
        self.assertLess(self.text.index('--jq .base.ref)" != "$DEFAULT_BRANCH" ]; then'), merge)
        self.assertIn('HEAD_SHA: ${{ steps.guard.outputs.head }}', self.text)
        self.assertEqual(merge_pr.REQUIRED_CHECKS, ('validate', 'review'))
        for forbidden in ('--squash', '--merge ', '--admin', '--auto'):
            self.assertNotIn(forbidden, self.text)
        self.assertIn('persist-credentials: false', self.text)
        # The branch is deleted only while it still points at the merged head: a push with a lease on it.
        self.assertIn('push --force-with-lease="refs/heads/$ref:$merged_head"', self.text)
        self.assertIn('origin ":refs/heads/$ref"', self.text)
        self.assertNotIn('-X DELETE', self.text)
        # Inputs reach the shell only through env, never through ${{ }} inside a run script.
        lines = self.text.splitlines()
        for index, line in enumerate(lines):
            if line.strip().startswith('run:'):
                script = [line]
                if line.strip() == 'run: |':
                    indent = len(line) - len(line.lstrip())
                    for following in lines[index + 1:]:
                        if following.strip() and len(following) - len(following.lstrip()) <= indent:
                            break
                        script.append(following)
                self.assertNotIn('${{', '\n'.join(script))
        for action in re.findall(r'^\s+- uses: (\S+)', self.text, re.MULTILINE):
            self.assertRegex(action, r'@[0-9a-f]{40}$')


if __name__ == '__main__':
    unittest.main()
