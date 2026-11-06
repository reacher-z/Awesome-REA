"""Star counts: read from GitHub by the production build, the recorded number when a read fails."""
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import repository_stats
import site_shell


class ReadStarsTests(unittest.TestCase):
    @staticmethod
    def answering(body):
        return lambda request, timeout: io.BytesIO(body)

    def test_reads_the_public_count(self):
        self.assertEqual(repository_stats.read_stars('a/b', opener=self.answering(b'{"stargazers_count": 75}')), 75)

    def test_failed_or_malformed_reads_give_nothing(self):
        def unreachable(request, timeout):
            raise URLError('offline')
        self.assertIsNone(repository_stats.read_stars('a/b', opener=unreachable))
        for body in (b'not json', b'{}', b'[]', b'{"stargazers_count": "75"}', b'{"stargazers_count": -1}', b'{"stargazers_count": true}'):
            with self.subTest(body=body):
                self.assertIsNone(repository_stats.read_stars('a/b', opener=self.answering(body)))


class RefreshTests(unittest.TestCase):
    def test_a_failed_read_keeps_the_recorded_number(self):
        recorded = {'observed_at': '2026-11-06', 'github_stars': {'a/b': 44, 'c/d': 1032}}
        stats, fresh = repository_stats.refreshed_stats(recorded, read={'a/b': 75, 'c/d': None}.get)
        self.assertEqual(stats['github_stars'], {'a/b': 75, 'c/d': 1032})
        self.assertEqual(fresh, 1)
        self.assertEqual(recorded['github_stars']['a/b'], 44)

    def test_pages_use_the_copy_the_build_hands_them(self):
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / 'stats.json'
            copy.write_text(json.dumps({'github_stars': {'a/b': 75}}), encoding='utf-8')
            with mock.patch.dict(os.environ, {repository_stats.STATS_ENV: str(copy)}):
                self.assertEqual(site_shell.repository_stars('a/b'), 75)
                self.assertIn('data-stars="a/b">75<', site_shell.star_count('a/b', 'ann-count'))
        with mock.patch.dict(os.environ):
            os.environ.pop(repository_stats.STATS_ENV, None)
            self.assertEqual(repository_stats.stats_path(), repository_stats.RECORDED_PATH)


if __name__ == '__main__':
    unittest.main()
