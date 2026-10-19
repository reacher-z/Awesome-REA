"""Keep contributor-facing references aligned with the vocabularies the validators accept."""
from copy import deepcopy
import datetime as dt
import json
from pathlib import Path
import re
import shlex
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import KIND_LABELS, RELATIONSHIPS
from validate import validate_citation, validate_resources
from validate_papers import FIELDS as PAPER_FIELDS, OPTIONAL_FIELDS as OPTIONAL_PAPER_FIELDS, STATUSES as PAPER_STATUSES

# Issue-form labels and the record values a maintainer records for them.
PAPER_FORM_STATUSES = {
    'Published conference or workshop paper': 'conference-paper',
    'Published journal article': 'journal-article',
    'Accepted, proceedings not yet verified': 'conference-accepted',
    'Preprint': 'preprint',
    'Status needs verification': None,
}


def form_options(name, field_id):
    """Read one dropdown's options without a YAML dependency."""
    text = (ROOT / '.github/ISSUE_TEMPLATE' / name).read_text(encoding='utf-8')
    blocks = [block for block in text.split('\n  - type: ') if f'\n    id: {field_id}\n' in block]
    if len(blocks) != 1:
        raise AssertionError(f'{name} should contain one {field_id!r} field')
    return re.findall(r'^        - (.+)$', blocks[0], re.MULTILINE)


def markdown_tables(text):
    tables, current = [], []
    for line in text.splitlines() + ['']:
        if line.startswith('|'):
            current.append(line)
        elif current:
            tables.append(current)
            current = []
    return tables


class ContributorReferenceTests(unittest.TestCase):
    def test_data_readme_lists_every_relationship_once(self):
        text = (ROOT / 'data/README.md').read_text(encoding='utf-8')
        documented = re.findall(r'^- `([a-z0-9-]+)` \(([^)]+)\): \S', text, re.MULTILINE)
        self.assertEqual([value for value, _ in documented], list(RELATIONSHIPS))
        self.assertEqual({value: label for value, label in documented},
                         {value: labels[0] for value, labels in RELATIONSHIPS.items()})
        self.assertNotIn('catalog.py --json`. ', text)
        self.assertIn('python3 scripts/catalog.py --list-categories', text)

    def test_paper_field_table_matches_validator(self):
        text = (ROOT / 'data/README.md').read_text(encoding='utf-8')
        tables = [table for table in markdown_tables(text) if table[0] == '| Field | Value | Meaning |']
        self.assertEqual(len(tables), 1)
        rows = {}
        for row in tables[0][2:]:
            cells = [cell.strip() for cell in row.strip('|').split('|')]
            for field in re.findall(r'`([a-z_]+)`', cells[0]):
                self.assertNotIn(field, rows, field + ' is documented twice')
                rows[field] = cells[1]
        self.assertEqual(set(rows), PAPER_FIELDS | OPTIONAL_PAPER_FIELDS)
        self.assertEqual(set(re.findall(r'`([a-z-]+)`', rows['publication_status'])), PAPER_STATUSES)
        self.assertEqual(re.findall(r'`([a-z]+)`', rows['date_precision']), ['year', 'month', 'day'])
        for field in ('doi', 'arxiv_id', 'arxiv_version_reviewed', 'first_arxiv_date',
                      'code_url', 'project_url', 'publication_date'):
            self.assertIn('null', rows[field], field)
        self.assertEqual((rows['kind'], rows['verification'], rows['runtime_tested']),
                         ('`research`', '`source-reviewed`', '`false`'))

    def test_resource_form_offers_each_kind_once(self):
        options = form_options('resource.yml', 'kind')
        labels = {labels[0]: kind for kind, labels in KIND_LABELS.items()}
        self.assertEqual(sorted(options), sorted(labels))
        record = json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0]
        for kind in labels.values():
            errors = []
            validate_resources([deepcopy(record) | {'kind': kind}], errors)
            self.assertEqual(errors, [], kind)
        self.assertIn('Learning resource', form_options('resource.yml', 'relation'))

    def test_paper_form_maps_each_status_once(self):
        options = form_options('paper.yml', 'status')
        self.assertEqual(sorted(options), sorted(PAPER_FORM_STATUSES))
        statuses = [value for value in PAPER_FORM_STATUSES.values() if value]
        self.assertEqual(sorted(statuses), sorted(PAPER_STATUSES))

    def test_documented_scans_write_outside_data(self):
        text = (ROOT / 'docs/source-scan.md').read_text(encoding='utf-8')
        text = text.replace('\\' + '\n', '')  # Shell line continuations form one command.
        commands = re.findall(r'^python3 scripts/scan_sources\.py .+$', text, re.MULTILINE)
        self.assertGreaterEqual(len(commands), 2)
        for command in commands:
            arguments = shlex.split(command)
            self.assertIn('--output', arguments, command)
            output = arguments[arguments.index('--output') + 1]
            self.assertTrue(output.startswith('.cache/'), command)

    def test_citation_metadata_cites_the_collection_only(self):
        text = (ROOT / 'CITATION.cff').read_text(encoding='utf-8')
        keys = set(re.findall(r'^([a-z-]+):', text, re.MULTILINE))
        self.assertTrue({'cff-version', 'message', 'title', 'type', 'authors', 'license',
                         'url', 'repository-code'} <= keys)
        # No identifier until one is minted; the release fields come from a published tag.
        self.assertFalse(keys & {'doi', 'identifiers', 'preferred-citation'})
        self.assertRegex(text, r'(?m)^version: \d+\.\d+\.\d+\ndate-released: \d{4}-\d{2}-\d{2}$')
        errors = []
        validate_citation(text, errors)
        self.assertEqual(errors, [])
        self.assertIn('license: MIT\n', text)
        self.assertIn('repository-code: https://github.com/reacher-z/Awesome-REA\n', text)
        self.assertIn('name: Awesome REA contributors\n', text)
        self.assertIn('primary sources', text)

    def test_citation_release_fields_are_paired_semantic_and_not_future(self):
        now = dt.datetime(2026, 10, 18, 12, tzinfo=dt.timezone.utc)
        base = 'title: Awesome Reverse Engineering Anything\n'
        for fields, problem in (('', None), ('version: 0.12.0\ndate-released: 2026-10-17\n', None),
                                ('version: 1.0.0\ndate-released: 2026-10-19\n', None),
                                ('version: 0.12.0\n', 'together'), ('date-released: 2026-10-17\n', 'together'),
                                ('version: v0.12.0\ndate-released: 2026-10-17\n', 'MAJOR.MINOR.PATCH'),
                                ('version: 0.12\ndate-released: 2026-10-17\n', 'MAJOR.MINOR.PATCH'),
                                ('version: 0.12.0\ndate-released: 2026-10-20\n', 'future'),
                                ('version: 0.12.0\ndate-released: "2026-10-17"\n', 'unquoted'),
                                ('version: 0.12.0\ndate-released: 2026-02-30\n', 'unquoted')):
            errors = []
            validate_citation(base + fields, errors, now=now)
            with self.subTest(fields=fields):
                if problem is None:
                    self.assertEqual(errors, [])
                else:
                    self.assertEqual(len(errors), 1, errors)
                    self.assertIn(problem, errors[0])


if __name__ == '__main__':
    unittest.main()
