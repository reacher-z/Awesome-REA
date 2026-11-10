"""The repository metadata refresh writes a snapshot only from a complete, error-free read."""
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import ingest_discoveries  # noqa: E402
import repository_metadata as metadata  # noqa: E402

NODE = {'stargazerCount': 7, 'isArchived': False, 'primaryLanguage': {'name': 'C'}, 'licenseInfo': {'spdxId': 'MIT'},
        'defaultBranchRef': {'target': {'committedDate': '2026-11-01T00:00:00Z'}}}


def response(document):
    return mock.MagicMock(__enter__=lambda self: io.BytesIO(json.dumps(document).encode()), __exit__=lambda *args: False)


class QueryTests(unittest.TestCase):
    def query(self, document, keys=('a/b', 'c/d')):
        with mock.patch.object(metadata, 'urlopen', return_value=response(document)):
            return metadata._query('token', list(keys))

    def test_an_unresolvable_repository_is_left_out(self):
        found = self.query({'data': {'r0': NODE, 'r1': None, 'rateLimit': {'cost': 1, 'remaining': 4000}},
                            'errors': [{'type': 'NOT_FOUND', 'path': ['r1']}]})
        self.assertEqual(found, {'a/b': {'stars': 7, 'committed_at': '2026-11-01T00:00:00Z', 'language': 'C', 'license': 'MIT'}})

    def test_any_other_error_or_an_empty_answer_stops_the_refresh(self):
        for document in ({'data': {'r0': NODE, 'r1': None}, 'errors': [{'type': 'RATE_LIMITED'}]},
                         {'errors': [{'message': 'Something went wrong'}]}, {}):
            with self.subTest(document=document), self.assertRaisesRegex(SystemExit, 'snapshot is unchanged'):
                self.query(document)

    def test_a_low_graphql_budget_stops_the_refresh(self):
        with self.assertRaisesRegex(SystemExit, 'GraphQL points'):
            self.query({'data': {'r0': NODE, 'r1': NODE, 'rateLimit': {'cost': 1, 'remaining': 20}}})


class FetchTests(unittest.TestCase):
    def test_a_run_over_the_cap_reads_nothing(self):
        with mock.patch.object(metadata, 'MAX_REPOSITORIES', 2), mock.patch.object(metadata, '_query') as query, \
                self.assertRaisesRegex(SystemExit, 'per-run cap'):
            metadata.fetch(['a/a', 'a/b', 'a/c'])
        query.assert_not_called()

    def test_a_read_that_loses_many_repositories_is_refused_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'repository-metadata.json'
            old = {'observed_at': '2026-11-01T00:00:00Z', 'source': 'GitHub GraphQL API',
                   'repositories': {f'o/r{index}': {'stars': index} for index in range(10)}}
            path.write_text(json.dumps(old), encoding='utf-8')
            keys = sorted(old['repositories'])
            with mock.patch.object(metadata, 'catalog_keys', return_value=keys), \
                    mock.patch.object(metadata, '_token', return_value='token'), \
                    mock.patch.object(metadata, '_query', side_effect=lambda token, batch: {key: {'stars': 1} for key in batch[:8]}), \
                    self.assertRaisesRegex(SystemExit, 'snapshot is unchanged'):
                metadata.refresh(path)
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')), old)

    def test_only_a_changed_fact_counts_as_a_change(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'repository-metadata.json'
            path.write_text(json.dumps({'observed_at': '2026-11-01T00:00:00Z', 'repositories': {'a/b': {'stars': 1}}}))
            self.assertFalse(metadata.changed({'observed_at': '2026-11-02T00:00:00Z', 'repositories': {'a/b': {'stars': 1}}}, path))
            self.assertTrue(metadata.changed({'observed_at': '2026-11-02T00:00:00Z', 'repositories': {'a/b': {'stars': 2}}}, path))


class WorkflowTests(unittest.TestCase):
    def test_the_workflow_runs_daily_on_the_default_branch_within_the_ingest_budget(self):
        text = (ROOT / '.github/workflows/repository-metadata.yml').read_text(encoding='utf-8')
        self.assertRegex(text, r"(?m)^    - cron: '\d+ \d+ \* \* \*'$")
        self.assertIn('run: python3 scripts/repository_metadata.py publish', text)
        self.assertIn("github.ref == format('refs/heads/{0}', github.event.repository.default_branch)", text)
        self.assertIn('\npermissions:\n  contents: read\n', text)
        minutes = int(re.search(r'(?m)^    timeout-minutes: (\d+)$', text)[1])
        self.assertGreaterEqual(minutes * 60, ingest_discoveries.JOB_SECONDS)
        self.assertNotIn('persist-credentials: true', text)


if __name__ == '__main__':
    unittest.main()
