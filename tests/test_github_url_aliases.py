"""Curated duplicate detection treats GitHub root-URL aliases as one repository."""
from copy import deepcopy
import datetime as dt
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from artifact_links import github_repository
from validate import normalized_url, validate_resources

NOW = dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc)
BASE = {
    'name': 'Alias fixture', 'category': 'native-analysis', 'relationship': 'foundation', 'kind': 'tool',
    'targets': ['binary'], 'description_en': 'A fixture.', 'description_zh': '测试记录。',
    'evidence_url': 'https://github.com/example/alias-fixture/blob/0123456789abcdef0123456789abcdef01234567/README.md',
    'verified_at': '2026-09-30', 'verification': 'source-reviewed', 'requirements': ['Python 3'],
}
ROOT_URL = 'https://github.com/example/alias-fixture'


def duplicate_errors(*urls):
    records = [BASE | {'id': f'alias-fixture-{index}', 'url': url} for index, url in enumerate(urls)]
    before = deepcopy(records)
    errors = []
    blocked = AssertionError('network access during offline validation')
    with patch.object(socket, 'getaddrinfo', side_effect=blocked), patch.object(socket.socket, 'connect', side_effect=blocked):
        validate_resources(records, errors, now=NOW)
    assert records == before, 'validation must not rewrite records'
    return errors


class GitHubURLAliasTests(unittest.TestCase):
    def test_case_trailing_slash_and_git_suffix_are_one_repository(self):
        for alias in (ROOT_URL + '.git', ROOT_URL + '.GIT', ROOT_URL + '/', ROOT_URL + '.git/',
                      'https://github.com/Example/Alias-Fixture', 'https://GitHub.com/example/alias-fixture.git'):
            with self.subTest(alias):
                self.assertEqual(duplicate_errors(ROOT_URL, alias), ["resource 'alias-fixture-1': duplicate canonical URL"])
                self.assertEqual(normalized_url(alias), normalized_url(ROOT_URL))
        # The curated validator and artifact matching use the same root identity.
        self.assertEqual(github_repository(ROOT_URL + '.git'), github_repository(ROOT_URL))

    def test_distinct_paths_and_repositories_stay_distinct(self):
        self.assertEqual(duplicate_errors(
            ROOT_URL,
            ROOT_URL + '/tree/main/docs',
            ROOT_URL + '/blob/main/README.md',
            ROOT_URL + '-plugin',
            'https://github.com/example/alias-fixture.github.io',
            'https://github.com/other/alias-fixture',
            ROOT_URL + '?tab=readme-ov-file',
            'https://alias-fixture.example.org/',
        ), [])

    def test_non_github_hosts_keep_their_path_case_and_suffix(self):
        self.assertEqual(duplicate_errors('https://gitlab.com/example/alias-fixture',
                                          'https://gitlab.com/example/alias-fixture.git'), [])
        self.assertEqual(duplicate_errors('https://example.org/Docs', 'https://example.org/docs'), [])


if __name__ == '__main__':
    unittest.main()
