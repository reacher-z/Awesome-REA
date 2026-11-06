"""Name the paper and the offending fields in paper schema errors."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import public_https_error
from validate_papers import validate_papers


def paper(**changes):
    record = deepcopy(json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))[0])
    record.update(id='paper-diagnostic-fixture')
    record.update(changes)
    return record


def errors_for(records):
    errors = []
    validate_papers(records, errors, url_check=public_https_error)
    return errors


class PaperDiagnosticsTest(unittest.TestCase):
    def test_schema_errors_name_paper_and_fields(self):
        record = paper(abstract='Not part of the schema.', zz_note='Also unknown.')
        del record['why_fits_zh'], record['doi']
        errors = errors_for([record])
        self.assertIn("paper 'paper-diagnostic-fixture': missing fields doi, why_fits_zh", errors)
        self.assertIn("paper 'paper-diagnostic-fixture': unknown fields abstract, zz_note", errors)
        self.assertIn("paper 'paper-diagnostic-fixture'.why_fits_zh: must be a nonempty string", errors)

    def test_records_without_string_ids_use_their_index(self):
        errors = errors_for([paper(), paper(id=17, abstract='Unknown.')])
        self.assertIn('paper[1]: unknown fields abstract', errors)
        self.assertIn('paper[1].id: must be a nonempty string', errors)

    def test_displayed_text_must_not_name_schema_fields(self):
        errors = errors_for([paper(metadata_notes='No repository was found, so code_url remains null.',
                                   metadata_notes_zh='未找到仓库，因此 code_url 留空。',
                                   scope_limitations_en='The first_arxiv_date and project_url are recorded.')])
        for field, name in (('metadata_notes', 'code_url'), ('metadata_notes_zh', 'code_url'),
                            ('scope_limitations_en', 'first_arxiv_date')):
            self.assertIn(f"paper 'paper-diagnostic-fixture'.{field}: describe {name} in reader terms instead of naming the field", errors)
        self.assertEqual(len(errors), 3)
        plain = paper(metadata_notes='No repository was found, so no code link is listed; see the code_urls_v2 page.')
        self.assertEqual(errors_for([plain]), [])

    def test_catalog_text_uses_reader_terms(self):
        records = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
        self.assertEqual([error for error in errors_for(records) if 'in reader terms' in error], [])

    def test_valid_records_still_pass(self):
        self.assertEqual(errors_for([paper()]), [])


if __name__ == '__main__':
    unittest.main()
