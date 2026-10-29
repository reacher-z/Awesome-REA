#!/usr/bin/env python3
"""Summarize saved awesome-lint findings per rule for the non-required README lint report."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / 'tests/awesome-lint/allowlist.json'


def read_allowlist(path=ALLOWLIST):
    """Rules that fail the job, and findings recorded as linter false positives with a reason."""
    config = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(config, dict) or set(config) != {'enforced_rules', 'false_positives'}:
        raise ValueError('allowlist needs exactly enforced_rules and false_positives')
    rules, entries = config['enforced_rules'], config['false_positives']
    if not isinstance(rules, list) or any(not isinstance(rule, str) or not rule for rule in rules):
        raise ValueError('enforced_rules must list rule IDs')
    if not isinstance(entries, list):
        raise ValueError('false_positives must be a list')
    keys = set()
    for entry in entries:
        if (not isinstance(entry, dict) or set(entry) != {'rule', 'reason', 'why'}
                or any(not isinstance(value, str) or not value.strip() for value in entry.values())):
            raise ValueError('each false positive needs a rule, the exact linter reason and why it is correct')
        if (entry['rule'], entry['reason']) in keys:
            raise ValueError('false positives must be unique')
        keys.add((entry['rule'], entry['reason']))
    return set(rules), keys


def summarize(report, enforced, false_positives):
    """Return the Markdown job summary and the findings that fail an enforced rule."""
    findings = report['findings']
    allowed = [(item['rule'], item['reason']) in false_positives for item in findings]
    totals, recorded = Counter(item['rule'] for item in findings), Counter()
    for item, known in zip(findings, allowed):
        recorded[item['rule']] += known
    failing = [item for item, known in zip(findings, allowed) if item['rule'] in enforced and not known]
    lines = ['## awesome-lint report', '',
             f"`{report['linter']}` on `{report['input']}`: {len(findings)} finding(s), "
             f"{sum(allowed)} of them recorded false positives.", '',
             'This report is not a required check. '
             + (f"It fails only on unrecorded findings of the enforced rules: {', '.join(f'`{rule}`' for rule in sorted(enforced))}."
                if enforced else 'No rule is enforced yet, so findings never fail it.'), '']
    if findings:
        lines += ['| Rule | Findings | Recorded false positives |', '| --- | ---: | ---: |']
        lines += [f'| `{rule}`{" (enforced)" if rule in enforced else ""} | {count} | {recorded[rule]} |'
                  for rule, count in sorted(totals.items(), key=lambda pair: (-pair[1], pair[0]))]
        lines.append('')
    unused = sorted(false_positives - {(item['rule'], item['reason']) for item in findings})
    if unused:
        lines += ['Recorded false positives not seen in this run: '
                  + '; '.join(f'`{rule}` {reason}' for rule, reason in unused) + '.', '']
    lines += ['Every finding, with its line and message, is in the `awesome-lint-report` workflow artifact. '
              'Recorded false positives and enforced rules are listed in `tests/awesome-lint/allowlist.json`.', '']
    return '\n'.join(lines), failing


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('findings', type=Path, help='JSON written by tests/awesome-lint/lint.mjs')
    parser.add_argument('--summary', type=Path, help='append the Markdown summary here, such as $GITHUB_STEP_SUMMARY')
    parser.add_argument('--allowlist', type=Path, default=ALLOWLIST)
    args = parser.parse_args(argv)
    enforced, false_positives = read_allowlist(args.allowlist)
    try:
        report = json.loads(args.findings.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        text, failing = '## awesome-lint report\n\nNo findings file was produced; check the lint step log. No count or clean result can be inferred.\n', None
    else:
        text, failing = summarize(report, enforced, false_positives)
    print(text)
    if args.summary:
        with args.summary.open('a', encoding='utf-8') as output:
            output.write(text + '\n')
    if failing is None:
        return 1
    for item in failing:
        print(f"{item['file']}:{item['line']}:{item['column']} {item['rule']}: {item['reason']}", file=sys.stderr)
    return 1 if failing else 0


if __name__ == '__main__':
    raise SystemExit(main())
