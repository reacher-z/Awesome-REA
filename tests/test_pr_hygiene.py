"""Pull request commits keep the maintainer's identity and no Claude credit; maintainer PRs carry a Codex review."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_pr_hygiene import codex_review_summary, commit_problems, pull_request_problems

MAINTAINER = {'name': 'reacher-z', 'email': 'reacher-z@users.noreply.github.com'}
MAINTAINER_ID = {'name': 'reacher-z', 'email': '68239571+reacher-z@users.noreply.github.com'}
ACTIONS = {'name': 'github-actions[bot]', 'email': '41898282+github-actions[bot]@users.noreply.github.com'}
WEB_FLOW = {'name': 'GitHub', 'email': 'noreply@github.com'}
OTHER = {'name': 'Orla Venn', 'email': 'orla@example.org'}
BODY = '## Problem\n\nSlow checks.\n\n## Codex review\n\nNo P0 or P1 findings.\n'


def commit(sha='a' * 40, author=MAINTAINER, committer=MAINTAINER, message='Speed up the site checks', parents=1):
    return {'sha': sha, 'parents': [{'sha': str(index)} for index in range(parents)],
            'commit': {'author': author, 'committer': committer, 'message': message}}


def pull(login='reacher-z', body=BODY, user_type='User', commits=1):
    return {'number': 7, 'user': {'login': login, 'type': user_type}, 'body': body, 'commits': commits}


class CommitTests(unittest.TestCase):
    def test_maintainer_and_bot_commits_pass(self):
        for author, committer in ((MAINTAINER, MAINTAINER), (MAINTAINER_ID, MAINTAINER_ID), (ACTIONS, ACTIONS),
                                  (MAINTAINER, ACTIONS), (ACTIONS, WEB_FLOW), (MAINTAINER_ID, WEB_FLOW)):
            with self.subTest(author=author['name'], committer=committer['name']):
                self.assertEqual(commit_problems(commit(author=author, committer=committer), check_identity=True), [])

    def test_claude_credit_fails_in_any_case_and_for_any_opener(self):
        for message in ('Fix\n\nCo-Authored-By: Claude <noreply@anthropic.com>', 'Fix\n\nco-authored-by:  claude opus',
                        'Fix\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)', 'GENERATED WITH CLAUDE'):
            for check_identity in (True, False):
                with self.subTest(message=message, check_identity=check_identity):
                    problems = commit_problems(commit(message=message), check_identity=check_identity)
                    self.assertEqual(len(problems), 1)
                    self.assertTrue(problems[0].startswith('aaaaaaaaaaaa: the commit message credits Claude'))
        self.assertEqual(commit_problems(commit(message='Co-Authored-By: Bo Kim <bo@example.org>'), check_identity=True), [])

    def test_other_identities_fail_without_naming_them(self):
        cases = [
            (OTHER, MAINTAINER, ['author']),
            (MAINTAINER, OTHER, ['committer']),
            (OTHER, WEB_FLOW, ['author', 'committer']),
            ({'name': 'reacher-z', 'email': 'orla@example.org'}, MAINTAINER, ['author']),
            ({'name': 'Orla Venn', 'email': 'reacher-z@users.noreply.github.com'}, MAINTAINER, ['author']),
            ({'name': 'helper[bot]', 'email': 'helper@example.org'}, MAINTAINER, ['author']),
            ({'name': 'helper[bot]', 'email': '1+other[bot]@users.noreply.github.com'}, MAINTAINER, ['author']),
        ]
        for author, committer, fields in cases:
            with self.subTest(author=author, committer=committer):
                problems = commit_problems(commit(author=author, committer=committer), check_identity=True)
                self.assertEqual([re.match(r'aaaaaaaaaaaa: the (\w+) must be', problem)[1] for problem in problems], fields)
                self.assertFalse(any('Orla' in problem or 'example.org' in problem for problem in problems))

    def test_update_branch_merges_pass_on_the_maintainer_address(self):
        # GitHub writes the account's profile name into the merge commit of "Update branch".
        for name in ('reacher-z', 'Orla Venn'):
            merge = commit(author={'name': name, 'email': MAINTAINER_ID['email']}, committer=WEB_FLOW,
                           message="Merge branch 'main' into topic", parents=2)
            self.assertEqual(commit_problems(merge, check_identity=True), [])
        for author, committer, parents in ((OTHER, WEB_FLOW, 2), ({'name': 'Orla Venn', 'email': MAINTAINER_ID['email']}, WEB_FLOW, 1),
                                           ({'name': 'Orla Venn', 'email': MAINTAINER_ID['email']}, OTHER, 2)):
            with self.subTest(author=author, committer=committer, parents=parents):
                self.assertTrue(commit_problems(commit(author=author, committer=committer, parents=parents), check_identity=True))

    def test_identity_is_checked_only_for_maintainer_and_bot_pull_requests(self):
        contribution = [commit(author=OTHER, committer=OTHER)]
        self.assertEqual(pull_request_problems(pull(login='orla-venn', body=''), contribution), [])
        self.assertEqual(len(pull_request_problems(pull(), contribution)), 2)
        self.assertEqual(len(pull_request_problems(pull(login='dependabot[bot]', user_type='Bot', body=''), contribution)), 2)

    def test_more_commits_than_the_api_lists_fail(self):
        problems = pull_request_problems(pull(commits=251), [commit()])
        self.assertEqual(len(problems), 1)
        self.assertIn('more than 250 commits', problems[0])


class CodexReviewTests(unittest.TestCase):
    def test_maintainer_pull_requests_need_a_filled_codex_review_section(self):
        self.assertEqual(pull_request_problems(pull(), [commit()]), [])
        for body in ('', '## Problem\n\nSlow.\n', '## Codex review\n\n## Checks\n\nAll pass.',
                     '## Codex review\n\n<!-- paste the summary -->\n', 'Codex review: none', None):
            with self.subTest(body=body):
                problems = pull_request_problems(pull(body=body), [commit()])
                self.assertEqual(len(problems), 1)
                self.assertIn('"Codex review" section', problems[0])

    def test_heading_level_case_and_closing_hashes_do_not_matter(self):
        for body in ('# codex review\nNo findings.', '### Codex Review ###\n\nFixed one P1.\n## Next',
                     'Intro\n\n   ## CODEX REVIEW\n- P2 kept: see above'):
            with self.subTest(body=body):
                self.assertTrue(codex_review_summary(body))
        self.assertEqual(codex_review_summary('## Codex review\nNo findings.\n## Checks\nAll pass.'), 'No findings.')
        self.assertEqual(codex_review_summary('## Codex review\n### Summary\nNo findings.\n# Checks\nAll pass.'),
                         '### Summary\nNo findings.')
        self.assertEqual(codex_review_summary('### Codex review\n## Checks\nAll pass.'), '')

    def test_other_openers_need_no_codex_review(self):
        self.assertEqual(pull_request_problems(pull(login='orla-venn', body=''), [commit()]), [])
        self.assertEqual(pull_request_problems(pull(login='github-actions[bot]', user_type='Bot', body=''),
                                               [commit(author=ACTIONS, committer=ACTIONS)]), [])


class WorkflowTests(unittest.TestCase):
    def test_the_check_reads_the_pull_request_without_running_its_code(self):
        text = (ROOT / '.github/workflows/pr-hygiene.yml').read_text(encoding='utf-8')
        self.assertIn('  pull_request_target:\n    types: [opened, edited, synchronize, reopened, ready_for_review]\n', text)
        self.assertIn('ref: ${{ github.event.pull_request.base.sha }}', text)
        self.assertNotIn('head.sha', text)
        self.assertNotIn('github.event.pull_request.body', text)
        self.assertEqual(re.findall(r'^      ([a-z-]+): (read|write)$', text, re.M), [('contents', 'read'), ('pull-requests', 'read')])
        self.assertIn('persist-credentials: false', text)
        self.assertIn('timeout-minutes: 5', text)
        self.assertIn('run: python3 scripts/check_pr_hygiene.py', text)


if __name__ == '__main__':
    unittest.main()
