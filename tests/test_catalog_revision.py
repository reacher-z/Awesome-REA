"""The ledger's catalog_revision is reported, without failing validation, when it is not on the checked-out history."""
import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from case_coverage import catalog_revision_warning
import validate

GIT_ENV = {**os.environ, 'GIT_AUTHOR_NAME': 'Fixture', 'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
           'GIT_COMMITTER_NAME': 'Fixture', 'GIT_COMMITTER_EMAIL': 'fixture@example.invalid',
           'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}


def git(root, *arguments):
    return subprocess.run(['git', '-C', str(root), *arguments], capture_output=True, encoding='utf-8',
                          check=True, env=GIT_ENV).stdout.strip()


class CatalogRevisionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name) / 'repository'
        self.root.mkdir()
        git(self.root, 'init', '-q', '-b', 'main')
        for message in ('first', 'second'):
            git(self.root, 'commit', '-q', '--allow-empty', '-m', message)
        self.on_main = git(self.root, 'rev-parse', 'HEAD~1')
        git(self.root, 'switch', '-q', '-c', 'side', 'HEAD~1')
        git(self.root, 'commit', '-q', '--allow-empty', '-m', 'branch only')
        self.branch_only = git(self.root, 'rev-parse', 'HEAD')
        git(self.root, 'switch', '-q', 'main')

    def tearDown(self):
        self.directory.cleanup()

    def warning(self, revision, root=None):
        return catalog_revision_warning({'catalog_revision': revision}, root or self.root)

    def test_commit_on_the_checked_out_history_is_quiet(self):
        self.assertIsNone(self.warning(self.on_main))
        self.assertIsNone(self.warning(git(self.root, 'rev-parse', 'HEAD')))

    def test_branch_only_and_unknown_commits_are_reported(self):
        self.assertIn('is not an ancestor of HEAD', self.warning(self.branch_only))
        self.assertIn('is not a commit in this clone', self.warning('0' * 40))

    def test_check_is_skipped_without_full_history(self):
        shallow = Path(self.directory.name) / 'shallow'
        git(self.root.parent, 'clone', '-q', '--depth', '1', self.root.as_uri(), str(shallow))
        self.assertEqual(git(shallow, 'rev-parse', '--is-shallow-repository'), 'true')
        self.assertIsNone(self.warning('0' * 40, shallow))
        outside = Path(self.directory.name) / 'not-a-repository'
        outside.mkdir()
        self.assertIsNone(self.warning('0' * 40, outside))

    def test_malformed_values_are_left_to_the_ledger_validator(self):
        for document in ({'catalog_revision': 'main'}, {'catalog_revision': None}, {}, []):
            with self.subTest(document=document):
                self.assertIsNone(catalog_revision_warning(document, self.root))

    def test_validation_prints_the_warning_and_still_passes(self):
        stderr = io.StringIO()
        with patch.object(validate, 'catalog_revision_warning', return_value='fixture warning'), \
                contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            status = validate.main()
        self.assertEqual(status, 0, stderr.getvalue())
        self.assertIn('Warning: case coverage fixture warning', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
