#!/usr/bin/env python3
"""Check a pull request's commits and body against the repository's commit and review rules.

- No commit message credits Claude: no `Co-Authored-By: Claude` trailer and no "Generated with Claude".
- In a pull request opened by reacher-z or a bot, every commit's author and committer is reacher-z or a bot.
  GitHub records itself as the committer of commits it creates for a person; that committer passes when the
  author does. The merge commit that "Update branch" creates carries the account's profile name with a
  reacher-z address, so it passes on the address; the rebase merge of merge-pr.yml leaves merge commits out
  of main.
- A pull request opened by reacher-z has a "Codex review" section in its body: a Markdown heading named
  Codex review with the review summary under it.

Findings name a commit by its SHA and the field that failed, never the name recorded in it.

    GH_TOKEN=... python3 scripts/check_pr_hygiene.py   # in GitHub Actions, for the pull request of the event
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

MAINTAINER = 'reacher-z'
MAINTAINER_EMAILS = frozenset({'reacher-z@users.noreply.github.com', '68239571+reacher-z@users.noreply.github.com'})
WEB_FLOW = ('GitHub', 'noreply@github.com')
CLAUDE_CREDIT = re.compile(r'co-authored-by:\s*claude|generated\s+with\s+\[?claude', re.I)
HEADING = re.compile(r'^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$')
HTML_COMMENT = re.compile(r'<!--.*?-->', re.S)
# The pull request commits endpoint lists at most 250 commits.
MAX_COMMITS = 250
API_TIMEOUT = 30


def is_maintainer(person: dict) -> bool:
    return person.get('name') == MAINTAINER and person.get('email') in MAINTAINER_EMAILS


def is_bot(person: dict) -> bool:
    name, email = person.get('name') or '', person.get('email') or ''
    return name.endswith('[bot]') and re.fullmatch(r'[0-9]+\+' + re.escape(name) + r'@users\.noreply\.github\.com', email) is not None


def is_web_flow(person: dict) -> bool:
    return (person.get('name'), person.get('email')) == WEB_FLOW


def is_maintainer_or_bot_login(user: dict) -> bool:
    login = user.get('login') or ''
    return login == MAINTAINER or user.get('type') == 'Bot' or login.endswith('[bot]')


def commit_problems(commit: dict, *, check_identity: bool) -> list[str]:
    """Findings for one commit of the pull request commits API."""
    sha = commit['sha'][:12]
    details = commit['commit']
    problems = []
    if CLAUDE_CREDIT.search(details.get('message') or ''):
        problems.append(f'{sha}: the commit message credits Claude (a Co-Authored-By: Claude trailer or '
                        '"Generated with Claude"); remove it.')
    author, committer = details.get('author') or {}, details.get('committer') or {}
    update_branch_merge = (len(commit.get('parents') or []) > 1 and is_web_flow(committer)
                           and author.get('email') in MAINTAINER_EMAILS)
    if check_identity and not update_branch_merge:
        author_ok = is_maintainer(author) or is_bot(author)
        if not author_ok:
            problems.append(f'{sha}: the author must be reacher-z <reacher-z@users.noreply.github.com> or a bot.')
        if not (is_maintainer(committer) or is_bot(committer) or (author_ok and is_web_flow(committer))):
            problems.append(f'{sha}: the committer must be reacher-z <reacher-z@users.noreply.github.com> or a bot.')
    return problems


def codex_review_summary(body: str) -> str:
    """The section under the first heading named Codex review, up to the next heading of the same or a higher
    level, without HTML comments; empty when there is none."""
    lines = HTML_COMMENT.sub('', body or '').splitlines()
    for index, line in enumerate(lines):
        heading = HEADING.match(line)
        if heading and heading[2].casefold() == 'codex review':
            section = []
            for following in lines[index + 1:]:
                next_heading = HEADING.match(following)
                if next_heading and len(next_heading[1]) <= len(heading[1]):
                    break
                section.append(following)
            return '\n'.join(section).strip()
    return ''


def body_problems(pull: dict) -> list[str]:
    if (pull.get('user') or {}).get('login') != MAINTAINER or codex_review_summary(pull.get('body') or ''):
        return []
    return ['The pull request body needs a "Codex review" section: a heading named Codex review with the summary of '
            '`codex review --base origin/main` under it.']


def pull_request_problems(pull: dict, commits: list[dict]) -> list[str]:
    problems = []
    if pull.get('commits', len(commits)) > MAX_COMMITS:
        problems.append(f'The pull request has more than {MAX_COMMITS} commits, more than the check can read; '
                        'squash it into fewer commits.')
    check_identity = is_maintainer_or_bot_login(pull.get('user') or {})
    for commit in commits:
        problems += commit_problems(commit, check_identity=check_identity)
    return problems + body_problems(pull)


def pull_request_commits(repository: str, number: int, token: str) -> list[dict]:
    commits = []
    for page in range(1, MAX_COMMITS // 100 + 2):
        request = urllib.request.Request(
            f'https://api.github.com/repos/{repository}/pulls/{number}/commits?per_page=100&page={page}',
            headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                     'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'Awesome-REA-pr-hygiene'})
        with urllib.request.urlopen(request, timeout=API_TIMEOUT) as response:
            batch = json.load(response)
        commits += batch
        if len(batch) < 100:
            break
    return commits


def main() -> int:
    repository, token = os.environ['GITHUB_REPOSITORY'], os.environ['GH_TOKEN']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise SystemExit('Invalid repository identity')
    with open(os.environ['GITHUB_EVENT_PATH'], encoding='utf-8') as stream:
        pull = json.load(stream)['pull_request']
    problems = pull_request_problems(pull, pull_request_commits(repository, int(pull['number']), token))
    for problem in problems:
        print(f'::error::{problem}')
    if problems:
        return 1
    print(f'Commit and review rules hold for pull request #{pull["number"]}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
