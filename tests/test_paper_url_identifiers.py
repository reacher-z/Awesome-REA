"""Paper url and pdf_url agree offline with the record's arXiv ID, reviewed version and DOI."""
from copy import deepcopy
import datetime as dt
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import review_pr
from validate import public_https_error
from validate_papers import validate_papers

NOW = dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc)
PAPER = {
    'id': 'paper-url-fixture', 'title': 'URL identifier fixture', 'title_zh': '链接标识测试记录',
    'authors': ['Ada Example', 'Grace Example'], 'year': 2025, 'publication_date': '2025-03',
    'date_precision': 'month', 'date_basis': 'Publisher page.', 'date_basis_zh': '出版方页面。',
    'venue': 'Fixture Conference 2025', 'publication_status': 'conference-paper',
    'arxiv_id': '2501.01234', 'arxiv_version_reviewed': 'v2', 'first_arxiv_date': '2025-01-03',
    'doi': '10.1145/1234567.7654321',
    'url': 'https://doi.org/10.1145/1234567.7654321', 'pdf_url': 'https://arxiv.org/pdf/2501.01234v2',
    'code_url': 'https://github.com/example/url-fixture', 'project_url': None,
    'description_en': 'A fixture paper.', 'description_zh': '一篇测试论文。',
    'scope_limitations_en': 'Fixture only.', 'scope_limitations_zh': '仅用于测试。',
    'why_fits_en': 'It tests URLs.', 'why_fits_zh': '用于测试链接。',
    'metadata_notes': 'Synthetic record.', 'metadata_notes_zh': '合成记录。',
    'targets': ['binary'], 'kind': 'research', 'verification': 'source-reviewed',
    'verified_at': '2026-09-30', 'runtime_tested': False,
    'evidence_urls': ['https://doi.org/10.1145/1234567.7654321', 'https://arxiv.org/abs/2501.01234v2'],
}


def errors_for(**changes):
    record = deepcopy(PAPER) | changes
    errors = []
    validate_papers([record], errors, url_check=public_https_error, now=NOW)
    return errors


class PaperURLIdentifierTests(unittest.TestCase):
    def test_matching_arxiv_and_doi_urls_pass(self):
        self.assertEqual(errors_for(), [])
        for changes in (
            {'url': 'https://arxiv.org/abs/2501.01234', 'pdf_url': 'https://arxiv.org/pdf/2501.01234'},
            {'url': 'https://www.arxiv.org/abs/2501.01234v2/', 'pdf_url': 'https://arxiv.org/pdf/2501.01234v2.pdf'},
            {'url': 'https://arxiv.org/html/2501.01234v2', 'arxiv_version_reviewed': None},
            {'url': 'https://dx.doi.org/10.1145/1234567.7654321'},
            {'url': 'https://doi.org/10.48550/ARXIV.2501.01234', 'doi': '10.48550/arXiv.2501.01234'},
            {'url': 'https://doi.org/10.1145%2F1234567.7654321'},
            {'url': 'https://doi.org/10.48550/arXiv.2501.01234'},
            {'url': 'https://doi.org/10.48550/arXiv.2501.01234', 'doi': '10.48550/arXiv.2501.01234'},
        ):
            with self.subTest(changes):
                self.assertEqual(errors_for(**changes), [])

    def test_publisher_landing_pages_and_other_hosts_are_not_interpreted(self):
        for changes in (
            {'url': 'https://dl.acm.org/doi/10.1145/9999999.9999999'},
            {'pdf_url': 'https://dl.acm.org/doi/pdf/10.1145/9999999.9999999'},
            {'url': 'https://example.org/papers/2502.05555'},
            {'url': 'https://arxiv.org/list/cs.CR/recent'},
        ):
            with self.subTest(changes):
                self.assertEqual(errors_for(**changes), [])

    def test_mismatched_arxiv_urls_fail(self):
        where = "paper 'paper-url-fixture'"
        self.assertEqual(errors_for(url='https://arxiv.org/abs/2502.05555'),
                         [f"{where}.url: links arXiv 2502.05555, but arxiv_id is '2501.01234'"])
        self.assertEqual(errors_for(pdf_url='https://arxiv.org/pdf/2501.01234v1'),
                         [f'{where}.pdf_url: links arXiv 2501.01234v1, but arxiv_version_reviewed is v2'])
        self.assertEqual(errors_for(arxiv_id=None, arxiv_version_reviewed=None, first_arxiv_date=None),
                         [f'{where}.pdf_url: links arXiv 2501.01234, but arxiv_id is None'])

    def test_mismatched_doi_resolver_urls_fail(self):
        where = "paper 'paper-url-fixture'"
        self.assertEqual(errors_for(url='https://doi.org/10.1145/9999999.9999999'),
                         [f"{where}.url: resolves DOI 10.1145/9999999.9999999, but doi is '10.1145/1234567.7654321'"])
        self.assertEqual(errors_for(url='https://doi.org/10.48550/arXiv.2502.05555'),
                         [f"{where}.url: resolves DOI 10.48550/arXiv.2502.05555, but doi is '10.1145/1234567.7654321'"])
        self.assertEqual(errors_for(doi=None, url='https://doi.org/10.1145/1234567.7654321'),
                         [f"{where}.url: resolves DOI 10.1145/1234567.7654321, but doi is None"])

    def test_artifact_dois_in_other_links_are_not_the_paper_doi(self):
        artifact = 'https://doi.org/10.5281/zenodo.1234567'
        self.assertEqual(errors_for(code_url=artifact, project_url=artifact,
                                    evidence_urls=[*PAPER['evidence_urls'], artifact]), [])

    def test_pull_request_review_applies_the_same_rule(self):
        self.assertIs(review_pr.validate_papers, validate_papers)


if __name__ == '__main__':
    unittest.main()
