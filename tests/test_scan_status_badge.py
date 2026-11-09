"""The README scan badge turns the warning colour once the last successful scan is more than six hours old."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import scan_status_badge
from scan_status_badge import COLOR, WARNING_COLOR, badge, parse_time

NOW = datetime(2026, 11, 9, 20, 0, tzinfo=timezone.utc)


class BadgeTests(unittest.TestCase):
    def test_colour_turns_after_six_hours(self):
        for age, color in ((timedelta(0), COLOR), (timedelta(hours=6), COLOR),
                           (timedelta(hours=6, seconds=1), WARNING_COLOR), (timedelta(days=3), WARNING_COLOR)):
            with self.subTest(age=age):
                document = badge(NOW - age, NOW)
                self.assertEqual(document['color'], color)
                self.assertEqual(document['message'], (NOW - age).strftime('%Y-%m-%d %H:%M UTC'))
        self.assertEqual(badge(None, NOW)['message'], 'none yet')
        self.assertEqual(badge(None, NOW)['color'], WARNING_COLOR)

    def test_endpoint_document_shape(self):
        document = badge(parse_time('2026-11-09T17:09:37Z'), NOW)
        self.assertEqual(document, {'schemaVersion': 1, 'label': 'last discovery scan', 'message': '2026-11-09 17:09 UTC',
                                    'color': COLOR, 'labelColor': '2B2F3A'})
        self.assertNotEqual(WARNING_COLOR, COLOR)

    def test_the_file_is_written_only_when_the_badge_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'scan-status.json'
            environment = {'GITHUB_REPOSITORY': 'reacher-z/Awesome-REA', 'GH_TOKEN': 'token'}
            with mock.patch.dict('os.environ', environment), \
                    mock.patch.object(scan_status_badge, 'last_successful_scan', return_value=parse_time('2026-11-09T17:09:37Z')):
                scan_status_badge.main([str(output)])
                first = output.stat().st_mtime_ns
                self.assertEqual(json.loads(output.read_text())['message'], '2026-11-09 17:09 UTC')
                scan_status_badge.main([str(output)])
                self.assertEqual(output.stat().st_mtime_ns, first)


class WorkflowTests(unittest.TestCase):
    def test_the_workflow_commits_only_a_changed_badge_to_the_status_branch(self):
        text = (ROOT / '.github/workflows/scan-status.yml').read_text(encoding='utf-8')
        self.assertIn("    - cron: '23 * * * *'\n", text)
        self.assertIn('    workflows: [Scheduled README discovery]\n    types: [completed]\n', text)
        self.assertIn('name: Scheduled README discovery\n', (ROOT / '.github/workflows/source-scan.yml').read_text(encoding='utf-8'))
        self.assertIn('permissions: {}\n', text)
        self.assertEqual(re.findall(r'^      ([a-z-]+): (read|write)$', text, re.M), [('contents', 'write'), ('actions', 'read')])
        self.assertIn('timeout-minutes: 5', text)
        self.assertIn('run: python3 scripts/scan_status_badge.py "$RUNNER_TEMP/status/scan-status.json"', text)
        # The first run creates the branch; later runs build on it and commit only a changed badge.
        self.assertIn('fetch -q --depth 1 "https://github.com/$GITHUB_REPOSITORY" status; then', text)
        self.assertIn('git rev-parse -q --verify HEAD >/dev/null && git diff --cached --quiet', text)
        self.assertIn('git push "https://github.com/$GITHUB_REPOSITORY" HEAD:status', text)
        self.assertEqual(text.count('persist-credentials: false'), 1)
        self.assertIn("user.email='41898282+github-actions[bot]@users.noreply.github.com'", text)


if __name__ == '__main__':
    unittest.main()
