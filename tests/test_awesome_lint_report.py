"""Keep the awesome-lint README report pinned, read-only, non-blocking and honest about false positives."""
import contextlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import awesome_lint_report as report

WORKFLOW = ROOT / '.github/workflows/readme-lint.yml'
STRUCTURAL = {'awesome-heading', 'awesome-toc', 'awesome-list-item'}


def finding(rule, reason, line=1):
    return {'file': 'README.md', 'rule': rule, 'line': line, 'column': 1, 'reason': reason}


FINDINGS = {'linter': 'awesome-lint@2.2.1', 'input': 'README.md', 'findings': [
    finding('double-link', 'Duplicate link', 10), finding('double-link', 'Duplicate link', 20),
    finding('awesome-spell-check', 'Text "webpack" should be written as "Webpack"', 30),
    finding('awesome-spell-check', 'Text "ArchLinux" should be written as "Arch Linux"', 40),
    finding('awesome-toc', 'Multiple Table of Contents lists found', 50),
]}


class AwesomeLintReportTests(unittest.TestCase):
    def run_report(self, findings, allowlist=None):
        with tempfile.TemporaryDirectory() as directory:
            path, summary = Path(directory) / 'findings.json', Path(directory) / 'summary.md'
            if findings is not None:
                path.write_text(json.dumps(findings), encoding='utf-8')
            arguments = [str(path), '--summary', str(summary)]
            if allowlist is not None:
                (Path(directory) / 'allowlist.json').write_text(json.dumps(allowlist), encoding='utf-8')
                arguments += ['--allowlist', str(Path(directory) / 'allowlist.json')]
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                status = report.main(arguments)
            return status, summary.read_text(encoding='utf-8'), stderr.getvalue()

    def test_counts_every_rule_and_separates_recorded_false_positives(self):
        status, summary, _ = self.run_report(FINDINGS)
        self.assertEqual(status, 0)
        self.assertIn('5 finding(s), 1 of them recorded false positives', summary)
        self.assertIn('| `double-link` | 2 | 0 |', summary)
        self.assertIn('| `awesome-spell-check` | 2 | 1 |', summary)
        self.assertIn('| `awesome-toc` | 1 | 0 |', summary)
        self.assertIn('not a required check', summary)
        self.assertIn('`awesome-lint-report` workflow artifact', summary)
        self.assertIn('not seen in this run', summary)
        self.assertIn('Text "Wasm" should be written as "WebAssembly"', summary)
        self.assertNotIn('Text "webpack" should be written as "Webpack";', summary.split('not seen in this run')[1])

    def test_only_unrecorded_findings_of_enforced_rules_fail(self):
        allowlist = {'enforced_rules': ['awesome-toc'], 'false_positives': []}
        status, summary, errors = self.run_report(FINDINGS, allowlist)
        self.assertEqual(status, 1)
        self.assertIn('| `awesome-toc` (enforced) | 1 | 0 |', summary)
        self.assertIn('README.md:50:1 awesome-toc: Multiple Table of Contents lists found', errors)
        self.assertNotIn('double-link', errors)
        allowlist['false_positives'] = [{'rule': 'awesome-toc', 'reason': 'Multiple Table of Contents lists found',
                                         'why': 'Fixture.'}]
        self.assertEqual(self.run_report(FINDINGS, allowlist)[0], 0)

    def test_missing_findings_never_read_as_clean(self):
        status, summary, _ = self.run_report(None)
        self.assertEqual(status, 1)
        self.assertIn('No findings file was produced', summary)
        self.assertNotIn('0 finding(s)', summary)

    def test_allowlist_records_only_reasoned_spell_check_false_positives(self):
        config = json.loads(report.ALLOWLIST.read_text(encoding='utf-8'))
        enforced, keys = report.read_allowlist()
        # Only the structural rules may ever fail the job.
        self.assertLessEqual(enforced, STRUCTURAL)
        self.assertEqual({rule for rule, _ in keys}, {'awesome-spell-check'})
        reasons = ' '.join(reason for _, reason in keys)
        # Correct product names are recorded instead of being rewritten; a real misspelling is not.
        for name in ('webpack', 'ReAct', 'Llama', 'Wasm'):
            self.assertIn(f'Text "{name}"', reasons)
        self.assertNotIn('ArchLinux', reasons)
        self.assertTrue(all(entry['why'].strip() for entry in config['false_positives']))
        for broken in ({'enforced_rules': [], 'false_positives': [{'rule': 'x', 'reason': 'y'}]},
                       {'enforced_rules': [''], 'false_positives': []}, {'false_positives': []},
                       {'enforced_rules': [], 'false_positives': [{'rule': 'x', 'reason': 'y', 'why': 'z'}] * 2}):
            with self.subTest(config=broken), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'allowlist.json'
                path.write_text(json.dumps(broken), encoding='utf-8')
                with self.assertRaises(ValueError):
                    report.read_allowlist(path)

    def test_linter_is_pinned_by_the_lockfile(self):
        package = json.loads((ROOT / 'tests/awesome-lint/package.json').read_text(encoding='utf-8'))
        lock = json.loads((ROOT / 'tests/awesome-lint/package-lock.json').read_text(encoding='utf-8'))
        self.assertEqual(package['devDependencies'], {'awesome-lint': '2.2.1'})
        self.assertEqual(lock['packages']['']['devDependencies'], {'awesome-lint': '2.2.1'})
        self.assertEqual(lock['packages']['node_modules/awesome-lint']['version'], '2.2.1')
        installed = [value for key, value in lock['packages'].items() if key]
        self.assertTrue(installed and all(value.get('integrity', '').startswith('sha512-') for value in installed))

    def test_workflow_is_a_read_only_report_outside_the_required_gate(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('permissions:\n  contents: read\n', text)
        self.assertNotIn(': write', text)
        self.assertNotIn('pull_request_target', text)
        self.assertIn('github_token: ${{ secrets.GITHUB_TOKEN }}', text)
        self.assertIn('npm ci --prefix tests/awesome-lint --ignore-scripts', text)
        self.assertIn('scripts/awesome_lint_report.py .cache/awesome-lint/findings.json --summary "$GITHUB_STEP_SUMMARY"', text)
        self.assertIn('name: awesome-lint-report', text)
        for trigger in ('push', 'pull_request'):
            block = re.search(rf'\n  {trigger}:\n((?:    .*\n)+)', text)[1]
            for path in ("'README*.md'", 'scripts/build_readme.py', "'tests/awesome-lint/**'"):
                self.assertIn(f'      - {path}\n', block)
        self.assertIn('branches: [main]', text.split('\n  pull_request:')[0])
        for action in re.findall(r'uses: (\S+)', text):
            self.assertRegex(action, r'@[0-9a-f]{40}$')
        catalog = (ROOT / '.github/workflows/validate.yml').read_text(encoding='utf-8')
        self.assertIn('needs: [unit, production, browser]\n', catalog)
        self.assertNotIn('awesome-lint', catalog)


if __name__ == '__main__':
    unittest.main()
