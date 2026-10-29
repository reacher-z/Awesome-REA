"""Public downloads retain curation evidence and never package working files."""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from data_downloads import build_data_downloads


class PublicDownloadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.resource = {
            'id': 'sample-project', 'name': 'Sample', 'name_zh': '示例',
            'url': 'https://example.org/project', 'description_en': 'Documented behavior.',
            'description_zh': '已记录的行为。', 'requirements': ['Not runtime-tested.'],
            'requirements_zh': ['未经运行测试。'], 'verification': 'source-reviewed',
            'verified_at': '2026-10-18', 'evidence_url': 'https://example.org/evidence',
        }
        self.paper = {
            'id': 'paper-sample', 'title': 'Sample paper', 'authors': ['B. Author', 'A. Author'],
            'scope_limitations_en': 'A small benchmark.', 'scope_limitations_zh': '小规模评测。',
            'runtime_tested': False, 'verification': 'source-reviewed',
            'citation': {'container_title': 'Proceedings', 'pages': '1–9',
                         'sources': ['https://example.org/proceedings']},
        }
        self.bib = '@misc{sample, title={Sample paper}}\n'

    def build(self, resources=None, papers=None, bibliography=None):
        catalog = {'resources': resources if resources is not None else [self.resource],
                   'meta': {'source_index': {'private_queue': 'DO-NOT-EXPORT'}}}
        return build_data_downloads(self.output, catalog,
                                    papers if papers is not None else [self.paper],
                                    self.bib if bibliography is None else bibliography)

    def test_bundle_is_closed_inventory_not_a_directory_archive(self):
        for name in ('.cache/draft.txt', 'fonts/pro.woff2', 'source-index.json', 'credentials.json'):
            path = self.output / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('DO-NOT-EXPORT')
        self.resource['draft_notes'] = 'DO-NOT-EXPORT'
        self.paper['citation']['private_notes'] = 'DO-NOT-EXPORT'
        manifest = self.build()
        raw = (self.output / 'downloads/awesome-rea-data.zip').read_bytes()
        self.assertEqual(manifest['archive']['sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(manifest['archive']['bytes'], len(raw))
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            self.assertEqual(set(archive.namelist()), {'resources.json', 'papers.json', 'records.jsonl',
                                                      'references.bib', 'README.md', 'manifest.json'})
            for name in archive.namelist():
                content = archive.read(name)
                self.assertNotIn(b'DO-NOT-EXPORT', content)
                self.assertEqual(content, (self.output / 'downloads' / name).read_bytes())
            inner = json.loads(archive.read('manifest.json'))
            for name, item in inner['files'].items():
                self.assertEqual(item['sha256'], hashlib.sha256(archive.read(name)).hexdigest())
                self.assertEqual(item['bytes'], len(archive.read(name)))

    def test_bilingual_evidence_author_order_limits_and_record_types_survive(self):
        descriptor = self.build()
        self.assertEqual(descriptor['counts'], {'resources': 1, 'papers': 1})
        resources = json.loads((self.output / 'downloads/resources.json').read_text())
        papers = json.loads((self.output / 'downloads/papers.json').read_text())
        for source, result in ((self.resource, resources[0]), (self.paper, papers[0])):
            for key, value in source.items():
                self.assertEqual(result[key], value)
        self.assertEqual(resources[0]['entry_url'], 'https://awesomerea.org/resources/sample-project/')
        self.assertEqual(papers[0]['entry_url_zh'], 'https://awesomerea.org/zh/papers/paper-sample/')
        records = [json.loads(line) for line in (self.output / 'downloads/records.jsonl').read_text().splitlines()]
        self.assertEqual(records, [{'record_type': 'resource', **resources[0]},
                                   {'record_type': 'paper', **papers[0]}])
        self.assertEqual((self.output / 'downloads/references.bib').read_text(), self.bib)

    def test_sensitive_allowed_field_or_bibliography_fails_before_output(self):
        sensitive = '/Users/' + 'private-person/work/notes'
        for field in ('description_en', 'requirements', 'bibliography'):
            with self.subTest(field=field):
                record = copy.deepcopy(self.resource)
                bibliography = self.bib
                if field == 'bibliography':
                    bibliography += sensitive
                else:
                    record[field] = [sensitive] if field == 'requirements' else sensitive
                with self.assertRaisesRegex(ValueError, 'values withheld') as error:
                    self.build(resources=[record], bibliography=bibliography)
                self.assertNotIn(sensitive, str(error.exception))
                self.assertFalse((self.output / 'downloads').exists())

    def test_output_is_deterministic_independent_of_input_order(self):
        second = {**self.resource, 'id': 'another-project'}
        original = copy.deepcopy([self.resource, second])
        first = self.build(resources=original)
        first_zip = (self.output / 'downloads/awesome-rea-data.zip').read_bytes()
        other_output = self.output / 'second-build'
        other_output.mkdir()
        second_manifest = build_data_downloads(other_output, {'resources': list(reversed(original))},
                                               [self.paper], self.bib)
        self.assertEqual(first, second_manifest)
        self.assertEqual(first_zip, (other_output / 'downloads/awesome-rea-data.zip').read_bytes())
        self.assertEqual(original, [self.resource, second])

    def test_duplicate_or_path_like_identity_cannot_generate_an_export(self):
        for rows in ([self.resource, self.resource], [{**self.resource, 'id': '../private'}]):
            with self.subTest(rows=len(rows)):
                with self.assertRaisesRegex(ValueError, 'unique canonical IDs'):
                    self.build(resources=rows)
                self.assertFalse((self.output / 'downloads').exists())


if __name__ == '__main__':
    unittest.main()
