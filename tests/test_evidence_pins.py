"""Wiki and repository-root evidence is reported, without failing validation, when it names no reviewed revision."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from catalog import RESOURCE_FILES
import validate
from validate import evidence_pin_warnings

REVISION = 'f' * 40
PINNED = ('emba', 'fmodel', 'universal-radio-hacker', 'sotn-matching-decomp-case', 'resym-paper',
          'perfect-dark-matching-decomp-case', 'goldeneye-007-matching-decomp-case')


def record(evidence, *additional):
    value = {'id': 'fixture', 'evidence_url': evidence}
    return value | ({'additional_evidence_urls': list(additional)} if additional else {})


class EvidencePinTests(unittest.TestCase):
    def test_unpinned_wiki_pages_and_repository_roots_are_reported(self):
        for evidence, additional, expected in (
            ('https://github.com/owner/project/wiki/Install', (), 'GitHub wiki evidence should end in the reviewed page revision'),
            ('https://github.com/owner/project/wiki', (), 'GitHub wiki evidence should end in the reviewed page revision'),
            ('https://github.com/owner/project', (), 'not the repository root'),
            ('https://github.com/owner/project/', (), 'not the repository root'),
            ('https://codeberg.org/owner/project', (), 'not the repository root'),
            ('https://gitlab.com/group/subgroup/project', (), 'not the repository root'),
            ('https://github.com/owner/project/blob/' + REVISION + '/README.md',
             ('https://gitlab.com/owner/project',), 'additional_evidence_urls: link the README or tree'),
        ):
            with self.subTest(evidence=evidence, additional=additional):
                warnings = evidence_pin_warnings([record(evidence, *additional)])
                self.assertEqual(len(warnings), 1)
                self.assertIn(expected, warnings[0])
                self.assertTrue(warnings[0].startswith("resource 'fixture'."))

    def test_pinned_and_non_repository_evidence_is_quiet(self):
        for evidence in ('https://github.com/owner/project/wiki/Install/' + REVISION,
                         'https://github.com/owner/project/tree/' + REVISION,
                         'https://github.com/owner/project/blob/' + REVISION + '/README.md',
                         'https://gitlab.com/owner/project/-/tree/' + REVISION,
                         'https://github.com/owner/project/releases/tag/v1.0',
                         'https://github.com/owner',
                         'https://sigrok.org/wiki/PulseView',
                         'https://doi.org/10.1145/3658644.3670340'):
            with self.subTest(evidence=evidence):
                self.assertEqual(evidence_pin_warnings([record(evidence)]), [])
        self.assertEqual(evidence_pin_warnings(['not a record', {'id': 'missing-links'}]), [])

    def test_pinned_records_name_a_revision_for_every_wiki_and_repository_link(self):
        # Only the records pinned here: open pull requests may still add unpinned links, which stay warnings.
        records = [item for path in RESOURCE_FILES for item in json.loads(path.read_text(encoding='utf-8'))
                   if item['id'] in PINNED]
        self.assertEqual(sorted(record['id'] for record in records), sorted(PINNED))
        self.assertEqual(evidence_pin_warnings(records), [])

    def test_validation_prints_the_warning_and_still_passes(self):
        stderr = io.StringIO()
        with patch.object(validate, 'evidence_pin_warnings', return_value=['fixture warning']), \
                contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            status = validate.main()
        self.assertEqual(status, 0, stderr.getvalue())
        self.assertIn('Warning: fixture warning', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
