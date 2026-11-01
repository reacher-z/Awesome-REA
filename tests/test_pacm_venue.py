"""Label Proceedings of the ACM journal papers one way and cite the journal title in BibTeX."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_paper_pages import bibtex_text, journal_title

PAPERS = {paper['id']: paper for paper in json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))}
# The PACM records reviewed for the venue pattern in data/README.md.
PACM_PAPERS = ('paper-declarui', 'paper-dcgen', 'paper-disco', 'paper-icepre', 'paper-decllm', 'paper-nero')
PACM_VENUE = re.compile(r'(Proceedings of the ACM on [A-Z][A-Za-z ]+) \(([A-Z]+) (\d{4})\)')


def journal_field(record):
    return re.search(r'^  journal = \{(.*)\},$', bibtex_text(record), re.MULTILINE)[1]


class JournalTitleTests(unittest.TestCase):
    def test_conference_issue_is_removed_from_the_journal_title(self):
        self.assertEqual(journal_title('Proceedings of the ACM on Software Engineering (FSE 2025)'),
                         'Proceedings of the ACM on Software Engineering')
        self.assertEqual(journal_title('Proceedings of the ACM on Programming Languages (OOPSLA 2020)'),
                         'Proceedings of the ACM on Programming Languages')

    def test_other_venues_are_unchanged(self):
        for venue in ('IEEE Transactions on Software Engineering', 'Formal Methods in System Design',
                      'Proceedings of the ACM on Software Engineering', 'USENIX Workshop (WOOT 18)',
                      'Journal (with a note)'):
            with self.subTest(venue=venue):
                self.assertEqual(journal_title(venue), venue)

    def test_bibtex_journal_falls_back_to_the_title_without_the_issue(self):
        record = deepcopy(PAPERS['paper-nero'])
        record.pop('citation', None)
        record['venue'] = 'Proceedings of the ACM on Software Engineering (ISSTA 2025)'
        self.assertEqual(journal_field(record), 'Proceedings of the ACM on Software Engineering')
        record['citation'] = {'container_title': 'Cited Journal', 'sources': [record['url']]}
        self.assertEqual(journal_field(record), 'Cited Journal')

    def test_proceedings_keep_their_venue_label_as_booktitle(self):
        record = deepcopy(PAPERS['paper-nero'])
        record.update(publication_status='conference-paper', venue='Example Conference (EXC 2020)')
        self.assertIn('  booktitle = {Example Conference (EXC 2020)},\n', bibtex_text(record))


class PacmRecordTests(unittest.TestCase):
    def test_pacm_records_share_one_venue_pattern_and_cite_the_journal(self):
        for identifier in PACM_PAPERS:
            record = PAPERS[identifier]
            with self.subTest(paper=identifier):
                match = PACM_VENUE.fullmatch(record['venue'])
                self.assertIsNotNone(match, record['venue'])
                journal, issue, year = match.groups()
                self.assertEqual(int(year), record['year'])
                if 'citation' in record:
                    self.assertEqual((record['citation']['container_title'], record['citation']['issue']),
                                     (journal, issue))
                self.assertEqual(record['publication_status'], 'journal-article')
                self.assertTrue(bibtex_text(record).startswith('@article{' + identifier + ',\n'))
                self.assertEqual(journal_field(record), journal)


if __name__ == '__main__':
    unittest.main()
