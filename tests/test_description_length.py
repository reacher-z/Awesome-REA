"""English descriptions above the documented limit are reported in one warning, without failing validation."""
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
from validate import DESCRIPTION_LIMIT, description_length_warning

# Shortened from more than 500 characters; they stay within the limit.
TRIMMED = ('dynamorio', 'reva-ghidra-mcp', 'decomp-wtf-agent-decompilation', 'wireshark-mcp',
           'openriseofnations-engine-case', 'decomp-toolkit', 'ps2recomp', 'mcp-windbg',
           'crashlens-rea-crash-triage', 'cheatengine-mcp-bridge',
           'destiny2-build-86657-reconstruction-report-case', 'rizin', 'pwndbg',
           'universal-modder-agent-toolkit', 'blackbox-protobuf', 'project-arwing-star-fox-recomp-case',
           'rkd-telemetry-extractor-case', 'little-planet-sonic-cd-recomp-case', 'wine-uwp-store-apps-case',
           'baocut-design-canvas-case', 'ultrasunnymoon-rea-case')


class DescriptionLengthTests(unittest.TestCase):
    def test_records_over_the_limit_are_named_longest_first_on_one_line(self):
        records = [{'id': 'short', 'description_en': 'x' * 120},
                   {'id': 'at-limit', 'description_en': 'x' * DESCRIPTION_LIMIT},
                   {'id': 'long', 'description_en': 'x' * 420},
                   {'id': 'longest', 'description_en': 'x' * 610},
                   'not a record', {'id': 'missing'}]
        warning = description_length_warning(records)
        self.assertEqual(warning, '2 curated records have English descriptions over 350 characters '
                                  '(target about 300, see data/README.md): longest (610), long (420)')
        self.assertNotIn('\n', warning)
        self.assertIsNone(description_length_warning(records[:2]))

    def test_shortened_descriptions_stay_within_the_limit(self):
        records = {record['id']: record for path in RESOURCE_FILES
                   for record in json.loads(path.read_text(encoding='utf-8'))}
        for identifier in TRIMMED:
            with self.subTest(identifier=identifier):
                self.assertLessEqual(len(records[identifier]['description_en']), DESCRIPTION_LIMIT)
                self.assertRegex(records[identifier]['description_zh'], r'[\u3400-\u9fff]')

    def test_validation_prints_the_warning_and_still_passes(self):
        stderr = io.StringIO()
        with patch.object(validate, 'description_length_warning', return_value='fixture warning'), \
                contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            status = validate.main()
        self.assertEqual(status, 0, stderr.getvalue())
        self.assertIn('Warning: fixture warning', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
