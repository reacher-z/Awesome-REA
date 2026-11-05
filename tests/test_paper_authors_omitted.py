"""A paper record may leave its author list out: every output then names no one and points to the paper."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_entry_pages import build_entry_pages, entry_path
from build_paper_pages import (AUTHORS_OMITTED, SEARCH_FIELDS, bibtex_text, build_paper_pages, scholarly_article,
                               search_index)
from build_readme import paper_line
from data_downloads import PAPER_FIELDS, projected_records
from validate import public_https_error
from validate_papers import validate_papers
from validate_site import expected_paper_schema, visible_authors

PAPERS = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))


def paper(identifier, **changes):
    record = deepcopy(next(p for p in PAPERS if p['id'] == identifier))
    record.update(changes)
    return record


def omitted(identifier='paper-fuzzware'):
    return paper(identifier, authors=[], authors_omitted=True)


def errors_for(record):
    errors = []
    validate_papers([record], errors, url_check=public_https_error)
    return [error for error in errors if 'authors' in error]


class AuthorsOmittedValidationTests(unittest.TestCase):
    def test_an_empty_list_is_valid_only_with_the_flag(self):
        self.assertEqual(errors_for(omitted()), [])
        self.assertEqual(errors_for(paper('paper-fuzzware')), [])
        self.assertTrue(errors_for(paper('paper-fuzzware', authors=[])))

    def test_the_flag_is_true_and_never_keeps_part_of_the_list(self):
        names = paper('paper-fuzzware')['authors']
        self.assertTrue(errors_for(paper('paper-fuzzware', authors_omitted=True)))
        self.assertTrue(errors_for(paper('paper-fuzzware', authors=names[:1], authors_omitted=True)))
        for value in (False, None, 'true', 1):
            with self.subTest(value=value):
                self.assertTrue(errors_for(paper('paper-fuzzware', authors_omitted=value)))
                self.assertTrue(errors_for(paper('paper-fuzzware', authors=[], authors_omitted=value)))


class AuthorsOmittedOutputTests(unittest.TestCase):
    def test_readme_and_paper_file_lines_link_the_paper_instead_of_a_first_author(self):
        record = omitted()
        for language, label in (('en', AUTHORS_OMITTED[0]), ('zh', AUTHORS_OMITTED[1])):
            with self.subTest(language=language):
                line = paper_line(record, language)
                self.assertIn(f' · [{label}]({record["url"]}) · [PDF]', line)
                self.assertNotIn('et al.', line)
                self.assertNotIn(' 等 ', line)
        listed = paper_line(paper('paper-fuzzware'), 'en')
        self.assertIn(paper('paper-fuzzware')['authors'][0] + ' et al.', listed)
        self.assertNotIn(AUTHORS_OMITTED[0], listed)

    def test_bibtex_has_no_author_field_and_a_note_pointing_to_the_paper(self):
        for identifier in ('paper-fuzzware', 'paper-crackmebench', 'paper-programbench'):
            with self.subTest(identifier=identifier):
                listed, record = paper(identifier), omitted(identifier)
                entry = bibtex_text(record)
                self.assertNotRegex(entry, r'(?m)^\s*author\s*=')
                self.assertRegex(entry, r'(?m)^  note = \{(?:[^{}]*\. )?' + re.escape(AUTHORS_OMITTED[0]) + r'\},?$')
                self.assertIn('  url = {' + record['url'] + '}', entry)
                # Every other field matches the listed record's entry.
                strip = lambda text: [line for line in text.splitlines() if not re.match(r'\s*(author|note) =', line)]
                self.assertEqual(strip(entry), strip(bibtex_text(listed)))
                self.assertRegex(bibtex_text(listed), r'(?m)^  author = \{')

    def test_structured_data_names_no_author(self):
        record = omitted()
        for language in ('en', 'zh'):
            article = scholarly_article(record, language)
            self.assertNotIn('author', article)
            self.assertEqual(article, expected_paper_schema(record, language))
            self.assertIn('author', scholarly_article(paper('paper-fuzzware'), language))

    def test_search_index_marks_the_record_and_lists_no_names(self):
        record, listed = omitted(), paper('paper-crackmebench')
        index = json.loads(search_index([record, listed]))
        self.assertEqual(list(index['papers'][0]), list(SEARCH_FIELDS))
        self.assertEqual((index['papers'][0]['authors'], index['papers'][0]['authors_omitted']), ([], True))
        self.assertEqual((index['papers'][1]['authors'], index['papers'][1]['authors_omitted']), (listed['authors'], None))

    def test_downloads_keep_the_flag(self):
        record, listed = omitted(), paper('paper-crackmebench')
        self.assertIn('authors_omitted', PAPER_FIELDS)
        projected = {row['id']: row for row in projected_records([record, listed], PAPER_FIELDS, 'papers')}
        self.assertEqual((projected[record['id']]['authors'], projected[record['id']]['authors_omitted']), ([], True))
        self.assertNotIn('authors_omitted', projected[listed['id']])

    def test_listing_cards_and_entry_pages_link_the_paper(self):
        records = [omitted(), paper('paper-crackmebench')]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            build_paper_pages(root, records)
            build_entry_pages(root, [], records)
            for language, prefix in (('en', ''), ('zh', 'zh/')):
                label = AUTHORS_OMITTED[language == 'zh']
                self.assertEqual(visible_authors(records[0], language), label)
                listing = (root / prefix / 'papers/index.html').read_text(encoding='utf-8')
                card = re.search(r'<article class="paper-card" id="paper-fuzzware".*?</article>', listing, re.S)[0]
                authors = re.search(r'<p class="paper-authors">(.*?)</p>', card, re.S)[1]
                self.assertRegex(authors, r'^<a href="' + re.escape(records[0]['url']) + r'" target="_blank" rel="noopener" aria-label="[^"]+">'
                                 + re.escape(label))
                self.assertNotIn('lang="en"', authors)
                other = re.search(r'<article class="paper-card" id="paper-crackmebench".*?</article>', listing, re.S)[0]
                self.assertIn('<p class="paper-authors" lang="en">' + '; '.join(records[1]['authors']) + '</p>', other)
                detail = (root / entry_path('paper', 'paper-fuzzware', language).lstrip('/') / 'index.html').read_text(encoding='utf-8')
                self.assertIn(f'<p class="entry-authors"><a href="{records[0]["url"]}" target="_blank" rel="noopener">{label} '
                              '<span aria-hidden="true">↗</span></a></p>', detail)
                self.assertNotRegex(detail, r'"@type":\s*"Person"')
            bibliography = (root / 'papers/references.bib').read_text(encoding='utf-8')
            self.assertEqual(len(re.findall(r'(?m)^  author = ', bibliography)), 1)

    def test_page_builders_reject_an_unmarked_empty_list_or_a_marked_nonempty_one(self):
        for record in (paper('paper-fuzzware', authors=[]),
                       paper('paper-fuzzware', authors_omitted=True)):
            with self.subTest(record=sorted(record)), TemporaryDirectory() as directory:
                with self.assertRaises(ValueError):
                    build_paper_pages(Path(directory), [record])


if __name__ == '__main__':
    unittest.main()
