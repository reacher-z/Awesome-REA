"""Export verified container metadata and classic-style arXiv locators in paper BibTeX."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_paper_pages import bibtex_text
from validate import public_https_error
from validate_papers import validate_papers

PAPERS = {paper['id']: paper for paper in json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))}


def fields(entry):
    """Return the field lines of one generated entry as a name-to-value mapping."""
    result = {}
    for line in entry.splitlines()[1:-1]:
        name, _, value = line.strip().rstrip(',').partition(' = ')
        result[name] = value
    return result


def errors_for(record):
    errors = []
    validate_papers([record], errors, url_check=public_https_error)
    return errors


def paper(status='conference-paper', **updates):
    record = deepcopy(PAPERS['paper-llm4decompile'])
    record.pop('citation', None)
    record.update(publication_status=status, **updates)
    return record


SOURCE = 'https://aclanthology.org/2024.emnlp-main.203/'


class ContainerMetadataTests(unittest.TestCase):
    def test_journal_articles_export_volume_issue_pages_and_article_number(self):
        record = paper('journal-article', venue='Example J.', citation={
            'container_title': 'Example Transactions on Software', 'volume': '46', 'issue': 'FSE',
            'pages': '196-221', 'article_number': 'FSE011', 'publisher': 'Example Society', 'sources': [SOURCE]})
        self.assertEqual(errors_for(record), [])
        entry = fields(bibtex_text(record))
        self.assertEqual((entry['journal'], entry['volume'], entry['number'], entry['pages'], entry['eid'], entry['publisher']),
                         ('{Example Transactions on Software}', '{46}', '{FSE}', '{196--221}', '{FSE011}', '{Example Society}'))
        # Identifier fields, including the biblatex eprint pair, are unchanged.
        self.assertEqual((entry['doi'], entry['eprint'], entry['archivePrefix']),
                         ('{10.18653/v1/2024.emnlp-main.203}', '{2403.05286}', '{arXiv}'))
        self.assertNotIn('series', entry)

    def test_proceedings_use_the_full_container_title_and_series(self):
        record = paper(venue='EX 2026', citation={
            'container_title': 'Proceedings of the 1st Example Conference & Workshop', 'volume': '306',
            'series': 'Proceedings of Example Research', 'pages': '41393-41415', 'publisher': 'EXR', 'sources': [SOURCE]})
        self.assertEqual(errors_for(record), [])
        entry = fields(bibtex_text(record))
        self.assertEqual(entry['booktitle'], r'{Proceedings of the 1st Example Conference \& Workshop}')
        self.assertEqual((entry['volume'], entry['series'], entry['pages'], entry['publisher']),
                         ('{306}', '{Proceedings of Example Research}', '{41393--41415}', '{EXR}'))
        self.assertFalse({'number', 'eid', 'howpublished'} & set(entry))
        # A single page exports unchanged, and an object with only a title still replaces the venue label.
        single = fields(bibtex_text(paper(citation={'container_title': 'Example Proceedings', 'pages': '7', 'sources': [SOURCE]})))
        self.assertEqual((single['booktitle'], single['pages']), ('{Example Proceedings}', '{7}'))

    def test_records_without_container_metadata_export_as_before(self):
        record = paper(publication_date='2024-11')
        self.assertEqual(bibtex_text(record), (
            '@inproceedings{paper-llm4decompile,\n'
            '  title = {{LLM4Decompile: Decompiling Binary Code with Large Language Models}},\n'
            '  author = {{Hanzhuo Tan} and {Qi Luo} and {Jing Li} and {Yuqun Zhang}},\n'
            '  year = {2024},\n'
            '  url = {https://aclanthology.org/2024.emnlp-main.203/},\n'
            '  booktitle = {EMNLP 2024},\n'
            '  doi = {10.18653/v1/2024.emnlp-main.203},\n'
            '  eprint = {2403.05286},\n'
            '  archivePrefix = {arXiv},\n'
            '  month = nov\n'
            '}\n'))
        journal = fields(bibtex_text(paper('journal-article', venue='Example Journal')))
        self.assertEqual(journal['journal'], '{Example Journal}')
        self.assertFalse({'volume', 'number', 'pages', 'eid', 'publisher', 'series'} & set(journal))


class ReviewedContainerRecordTests(unittest.TestCase):
    def test_reviewed_records_export_their_cited_containers(self):
        redraw = fields(bibtex_text(PAPERS['paper-redraw']))
        self.assertEqual((redraw['journal'], redraw['volume'], redraw['number'], redraw['pages']),
                         ('{IEEE Transactions on Software Engineering}', '{46}', '{2}', '{196--221}'))
        declarui = fields(bibtex_text(PAPERS['paper-declarui']))
        self.assertEqual((declarui['journal'], declarui['volume'], declarui['number'], declarui['pages'], declarui['eid']),
                         ('{Proceedings of the ACM on Software Engineering}', '{2}', '{FSE}', '{219--241}', '{FSE011}'))
        self.assertEqual((declarui['doi'], declarui['eprint'], declarui['archivePrefix']),
                         ('{10.1145/3715726}', '{2409.11667}', '{arXiv}'))

    def test_only_reviewed_records_carry_container_metadata(self):
        expected = {'paper-dire', 'paper-resym', 'paper-redraw', 'paper-declarui', 'paper-fuzzware',
                    'paper-firmae', 'paper-vision2web', 'paper-ui2code', 'paper-worldcoder',
                    'paper-jsdeobsbench', 'paper-cascade', 'paper-dcgen', 'paper-code-world-models',
                    'paper-stateinspector', 'paper-halucinator'}
        self.assertEqual({identifier for identifier, record in PAPERS.items() if 'citation' in record}, expected)
        for identifier in sorted(PAPERS.keys() - expected):
            # Records without verified container metadata keep the short venue label.
            with self.subTest(paper=identifier):
                entry = fields(bibtex_text(PAPERS[identifier]))
                self.assertFalse({'volume', 'number', 'series', 'pages', 'eid', 'publisher'} & set(entry))


class ArxivLocatorTests(unittest.TestCase):
    def test_preprints_print_their_arxiv_identifier_in_classic_styles(self):
        for identifier, record in PAPERS.items():
            if record['publication_status'] != 'preprint':
                continue
            with self.subTest(paper=identifier):
                entry = fields(bibtex_text(record))
                self.assertEqual(entry['howpublished'], '{arXiv:' + record['arxiv_id'] + '}')
                self.assertEqual((entry['note'], entry['eprint'], entry['archivePrefix']),
                                 ('{Preprint}', '{' + record['arxiv_id'] + '}', '{arXiv}'))

    def test_accepted_papers_read_as_accepted_without_review_wording(self):
        entry = bibtex_text(paper('conference-accepted', venue='NeurIPS 2026', publication_date=None, date_precision='year'))
        self.assertTrue(entry.startswith('@misc{'))
        self.assertIn('  howpublished = {arXiv:2403.05286},\n', entry)
        self.assertIn('  note = {Accepted to NeurIPS 2026},\n', entry)
        for record in PAPERS.values():
            if record['publication_status'] == 'conference-accepted':
                with self.subTest(paper=record['id']):
                    entry = bibtex_text(record)
                    self.assertIn('  note = {Accepted to ' + record['venue'] + '},\n', entry)
                    self.assertNotIn('verified', entry)
                    self.assertNotIn('proceedings', entry)

    def test_published_entries_do_not_gain_a_locator(self):
        for identifier, record in PAPERS.items():
            if record['publication_status'] in {'conference-paper', 'journal-article'}:
                with self.subTest(paper=identifier):
                    self.assertNotIn('howpublished', fields(bibtex_text(record)))

    def test_preprints_without_arxiv_keep_the_plain_note(self):
        entry = fields(bibtex_text(paper('preprint', arxiv_id=None, arxiv_version_reviewed=None, first_arxiv_date=None)))
        self.assertNotIn('howpublished', entry)
        self.assertEqual(entry['note'], '{Preprint}')


class CitationValidationTests(unittest.TestCase):
    def test_real_records_validate(self):
        errors = []
        validate_papers(list(PAPERS.values()), errors, url_check=public_https_error)
        self.assertEqual(errors, [])

    def test_invalid_container_metadata_is_rejected(self):
        source = 'https://aclanthology.org/2024.emnlp-main.203/'
        valid = {'container_title': 'Proceedings of an Example Conference', 'pages': '1-9', 'sources': [source]}
        self.assertEqual(errors_for(paper(citation=valid)), [])
        cases = {
            'empty object': {},
            'preprint': None,
            'unknown field': valid | {'editor': 'Someone'},
            'missing sources': {key: value for key, value in valid.items() if key != 'sources'},
            'unreviewed source': valid | {'sources': ['https://example.org/metadata']},
            'duplicate source': valid | {'sources': [source, source]},
            'reversed pages': valid | {'pages': '9-1'},
            'en dash pages': valid | {'pages': '1–9'},
            'padded title': valid | {'container_title': ' Proceedings '},
            'issue without volume': valid | {'issue': '2'},
            'non-numeric volume': valid | {'volume': 'two'},
        }
        for name, citation in cases.items():
            record = paper('preprint', citation=valid) if citation is None else paper(citation=citation)
            with self.subTest(case=name):
                self.assertTrue([error for error in errors_for(record) if '.citation' in error], name)


if __name__ == '__main__':
    unittest.main()
