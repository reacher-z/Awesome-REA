"""The paper form separates publication, date and artifact evidence and accepts unresolved metadata."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FORM = ROOT / '.github/ISSUE_TEMPLATE/paper.yml'


def fields():
    """Map each field ID to (type, block) without a YAML dependency."""
    result = {}
    for block in FORM.read_text(encoding='utf-8').split('\n  - type: ')[1:]:
        identifier = re.search(r'^    id: (\S+)$', block, re.MULTILINE)
        if identifier:
            result[identifier[1]] = (block.split('\n', 1)[0].strip(), block)
    return result


def required(block):
    return re.search(r'^    validations:\n      required: (true|false)$', block, re.MULTILINE)[1] == 'true'


class PaperFormFieldTests(unittest.TestCase):
    def test_dates_distinguish_publisher_arxiv_and_event_dates_with_sources(self):
        kind, block = fields()['dates']
        self.assertEqual(kind, 'textarea')
        for phrase in ('Publisher publication date', 'arXiv first submission and version checked',
                       'Conference or event dates', 'not the publisher\'s publication date', 'name the source'):
            self.assertIn(phrase, block)
        self.assertIn('YYYY, YYYY-MM or YYYY-MM-DD', block)

    def test_artifacts_record_their_author_source_and_can_be_unavailable_or_restricted(self):
        kind, block = fields()['artifact_status']
        self.assertEqual(kind, 'dropdown')
        self.assertIn('      multiple: true', block)
        options = re.findall(r'^        - (.+)$', block, re.MULTILINE)
        for expected in ('Not available', 'Unknown', 'Hosted demo or service only', 'Announced or promised, not yet available'):
            self.assertIn(expected, options)
        self.assertTrue(any(option.startswith('Access-restricted') for option in options))
        _, links = fields()['artifacts']
        for phrase in ('where the authors provide it', 'access-restricted or unavailable',
                       'may differ from the version evaluated in the paper', 'linked from:'):
            self.assertIn(phrase, links)

    def test_unresolved_metadata_can_be_submitted_without_claiming_a_source_review(self):
        form = fields()
        self.assertEqual({name for name, (_, block) in form.items() if required(block)},
                         {'url', 'title', 'status', 'relevance', 'evidence'})
        for name in ('publication_evidence', 'dates', 'artifact_status', 'artifacts'):
            self.assertFalse(required(form[name][1]), name)
        self.assertIn('Status needs verification', form['status'][1])
        intro = FORM.read_text(encoding='utf-8').split('\n  - type: ')[1]
        self.assertIn('answer "unknown"', intro)
        self.assertIn('A suggestion is not a source review', intro)
        self.assertIn('"unknown"', form['evidence'][1])


if __name__ == '__main__':
    unittest.main()
