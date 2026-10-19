"""Keep arXiv DOIs bound to their arXiv ID and to preprint records only."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_paper_pages import bibtex_text, scholarly_article
from validate import public_https_error
from validate_papers import arxiv_doi_warnings, validate_papers

PAPERS = {paper['id']: paper for paper in json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))}
# Records this rule was applied to; the rest of the catalog is checked only by the advisory lines.
PREPRINTS_WITH_ARXIV_DOI = ('paper-crackmebench', 'paper-sre-bench', 'paper-humans-machines-sre',
                            'paper-sok-ai-binary-reversing', 'paper-gamereplica')


def paper(status='preprint', **updates):
    record = deepcopy(PAPERS['paper-llm4decompile'])
    record.pop('citation', None)
    record.update(id='paper-arxiv-doi-fixture', title='arXiv DOI fixture', title_zh='arXiv DOI 测试记录',
                  url='https://arxiv.org/abs/2403.05286', publication_status=status,
                  doi='10.48550/arXiv.2403.05286')
    record.update(updates)
    return record


def errors_for(record):
    errors = []
    validate_papers([record], errors, url_check=public_https_error)
    return errors


class ArxivDoiValidationTests(unittest.TestCase):
    def test_matching_arxiv_doi_is_accepted_in_any_case(self):
        self.assertEqual(errors_for(paper()), [])
        self.assertEqual(errors_for(paper(doi='10.48550/ARXIV.2403.05286')), [])

    def test_arxiv_doi_must_name_the_record_arxiv_id(self):
        for doi, updates in (('10.48550/arXiv.2403.05287', {}),
                             ('10.48550/arXiv.2403.05286v2', {}),
                             ('10.48550/2403.05286', {}),
                             ('10.48550/arXiv.2403.05286',
                              {'arxiv_id': None, 'arxiv_version_reviewed': None, 'first_arxiv_date': None})):
            with self.subTest(doi=doi, updates=updates):
                errors = errors_for(paper(doi=doi, **updates))
                self.assertEqual(sum('an arXiv DOI must be 10.48550/arXiv.<arxiv_id>' in error for error in errors), 1)

    def test_publisher_dois_are_not_affected(self):
        record = paper('conference-paper', doi='10.18653/v1/2024.emnlp-main.203')
        self.assertEqual(errors_for(record), [])
        self.assertEqual(arxiv_doi_warnings([record]), [])


class ArxivDoiWarningTests(unittest.TestCase):
    def test_preprint_without_its_arxiv_doi_is_reported_without_failing(self):
        record = paper(doi=None)
        self.assertEqual(errors_for(record), [])
        warnings = arxiv_doi_warnings([record])
        self.assertEqual(len(warnings), 1)
        self.assertIn('1 arXiv preprint(s) leave doi null', warnings[0])
        self.assertTrue(warnings[0].endswith(': paper-arxiv-doi-fixture'))

    def test_accepted_or_published_paper_with_an_arxiv_doi_is_reported_without_failing(self):
        for status in ('conference-accepted', 'conference-paper', 'journal-article'):
            with self.subTest(status=status):
                record = paper(status)
                self.assertEqual(errors_for(record), [])
                warnings = arxiv_doi_warnings([record])
                self.assertEqual(len(warnings), 1)
                self.assertIn('accepted or published paper(s) store an arXiv DOI', warnings[0])

    def test_conforming_and_malformed_inputs_produce_no_lines(self):
        no_arxiv = paper(doi=None, arxiv_id=None, arxiv_version_reviewed=None, first_arxiv_date=None)
        self.assertEqual(arxiv_doi_warnings([paper(), paper('conference-paper', doi=None), no_arxiv,
                                             'not a record', {}]), [])
        self.assertEqual(arxiv_doi_warnings(None), [])


class AppliedRecordTests(unittest.TestCase):
    def test_edited_preprints_carry_their_arxiv_doi_in_citations(self):
        for identifier in PREPRINTS_WITH_ARXIV_DOI:
            record = PAPERS[identifier]
            with self.subTest(paper=identifier):
                doi = '10.48550/arXiv.' + record['arxiv_id']
                self.assertEqual((record['publication_status'], record['doi']), ('preprint', doi))
                self.assertIn('https://api.datacite.org/dois/' + doi, record['evidence_urls'])
                self.assertNotIn('pending', record['metadata_notes'])
                self.assertNotIn('待注册', record['metadata_notes_zh'])
                self.assertIn('  doi = {' + doi + '},\n', bibtex_text(record))
                self.assertIn({'@type': 'PropertyValue', 'propertyID': 'DOI', 'value': doi},
                              scholarly_article(record, 'en')['identifier'])

    def test_accepted_programbench_keeps_doi_for_a_publisher_doi(self):
        record = PAPERS['paper-programbench']
        self.assertEqual((record['publication_status'], record['doi']), ('conference-accepted', None))
        self.assertNotIn('doi = ', bibtex_text(record))
        self.assertIn('  eprint = {2605.03546},\n', bibtex_text(record))


if __name__ == '__main__':
    unittest.main()
