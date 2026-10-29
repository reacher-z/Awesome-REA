"""Check case-ledger evidence links offline: references, ledger-only losses and the exit status."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_links
from case_coverage import read_case_coverage

GONE_POST = 'https://x.com/gone_author/status/1'
LIVE_POST = 'https://x.com/i/status/2'
GONE_REPO = 'https://github.com/owner/vanished'
FORK = 'https://github.com/other/fork/blob/0123456789abcdef0123456789abcdef01234567/README.md'


def entry(identifier, reason, reported=(), primary=()):
    return {'id': identifier, 'reason_en': reason,
            'reported_source_urls': list(reported), 'primary_evidence_urls': list(primary)}


def ledger(*entries):
    return {'entries': list(entries)}


def dead(url, references):
    return {'url': url, 'status': 'dead', 'http_status': 404, 'reason': 'HTTP 404/410 confirmed by a second request',
            'references': references}


class LedgerReferenceTests(unittest.TestCase):
    def test_both_ledger_fields_get_entry_and_field_references(self):
        references, _ = check_links.ledger_sources(ledger(
            entry('song:a', 'Reviewed.', reported=[GONE_POST], primary=[GONE_POST, FORK]),
            entry('hao-games:row-001', 'Reviewed.', primary=[FORK])))
        self.assertEqual(references[GONE_POST], ['ledger:song:a:reported_source_urls',
                                                 'ledger:song:a:primary_evidence_urls'])
        self.assertEqual(references[FORK], ['ledger:song:a:primary_evidence_urls',
                                            'ledger:hao-games:row-001:primary_evidence_urls'])

    def test_source_urls_add_ledger_references_to_the_catalog_set(self):
        coverage = read_case_coverage(ROOT)
        references = check_links.source_urls(coverage)
        ledger_references, _ = check_links.ledger_sources(coverage)
        for url, expected in ledger_references.items():
            self.assertTrue(set(expected) <= set(references[url]), url)
        self.assertTrue(any(reference.startswith(('resource:', 'paper:', 'benchmark:'))
                            for values in references.values() for reference in values))


class RecordedMissingTests(unittest.TestCase):
    def test_reason_must_name_the_post_or_repository_before_the_not_found_phrase(self):
        self.assertTrue(check_links.records_missing(
            GONE_POST, 'The cited post (@gone_author; its ID dates it 2026-10-12) returned not found from the API.'))
        self.assertTrue(check_links.records_missing(
            GONE_REPO, 'The named repository owner/vanished and its owner account return 404 at review.'))
        self.assertTrue(check_links.records_missing(
            GONE_REPO, 'On 2026-10-18 owner/vanished returned HTTP 404 from the GitHub API.'))
        for url, reason in (
            (GONE_POST, 'The cited post by @gone_author was reviewed.'),
            # Another source in the same entry is the one recorded as missing.
            (GONE_POST, '@gone_author links a repository. GitHub reports as not found the store repository.'),
            ('https://github.com/other/fork', 'The repository owner/vanished returns 404. A fork, other/fork, survives.'),
            # Handle-less X links and other hosts cannot be matched to a sentence, so they stay strict.
            (LIVE_POST, 'The post returned not found.'),
            ('https://example.com/post', 'example.com/post returned not found.'),
        ):
            with self.subTest(url=url, reason=reason):
                self.assertFalse(check_links.records_missing(url, reason))

    def test_a_url_counts_as_recorded_only_when_every_citing_entry_records_it(self):
        reason = 'The cited post (@gone_author) returned not found.'
        _, known = check_links.ledger_sources(ledger(entry('song:a', reason, reported=[GONE_POST])))
        self.assertEqual(known, {GONE_POST})
        _, known = check_links.ledger_sources(ledger(entry('song:a', reason, reported=[GONE_POST]),
                                                     entry('song:b', 'Reviewed.', primary=[GONE_POST])))
        self.assertEqual(known, set())

    def test_recorded_losses_are_separated_while_new_and_catalog_404s_stay_dead(self):
        known = {GONE_POST}
        classify = check_links.classify_ledger_loss
        recorded = classify(dead(GONE_POST, ['ledger:song:a:reported_source_urls',
                                             'ledger:song:a:primary_evidence_urls']), known)
        self.assertEqual(recorded['status'], 'recorded-missing')
        new_404 = classify(dead(FORK, ['ledger:song:a:primary_evidence_urls']), known)
        self.assertEqual(new_404['status'], 'dead')
        shared = classify(dead(GONE_POST, ['ledger:song:a:primary_evidence_urls', 'resource:example:evidence_url']), known)
        self.assertEqual(shared['status'], 'dead')
        reachable = {'url': GONE_POST, 'status': 'ok', 'references': ['ledger:song:a:primary_evidence_urls']}
        self.assertEqual(classify(reachable, known)['status'], 'ok')

    def test_collection_reported_links_are_separated_unless_used_as_evidence(self):
        classify = check_links.classify_ledger_loss
        reported = classify(dead(LIVE_POST, ['ledger:song:a:reported_source_urls',
                                             'ledger:song:b:reported_source_urls']), set())
        self.assertEqual(reported['status'], 'reported-source-missing')
        for references in (['ledger:song:a:reported_source_urls', 'ledger:song:b:primary_evidence_urls'],
                           ['ledger:song:a:reported_source_urls', 'paper:paper-x:evidence_urls'], []):
            with self.subTest(references=references):
                self.assertEqual(classify(dead(LIVE_POST, references), set())['status'], 'dead')


class LinkCheckExitTests(unittest.TestCase):
    def run_main(self, statuses):
        coverage = ledger(entry('song:a', 'The cited post (@gone_author) returned not found.',
                                reported=[GONE_POST, LIVE_POST], primary=[GONE_POST, FORK]))
        fake = lambda url, timeout=15: {'url': url, 'checked_url': url, 'status': statuses.get(url, 'ok'),
                                        'http_status': 404 if statuses.get(url) == 'dead' else 200,
                                        'reason': 'test', 'attempts': []}
        with patch.object(check_links, 'read_case_coverage', return_value=coverage), \
                patch.object(check_links, 'load_resources', return_value=[]), \
                patch.object(check_links, 'check_url', side_effect=fake), \
                patch.object(sys, 'argv', ['check_links.py']), \
                patch('builtins.print') as printed, \
                patch.object(Path, 'read_text', return_value='[]'):  # no benchmark or paper links
            code = check_links.main()
        return code, '\n'.join(' '.join(map(str, call.args)) for call in printed.call_args_list)

    def test_recorded_missing_posts_do_not_fail_the_job(self):
        code, output = self.run_main({GONE_POST: 'dead'})
        self.assertEqual(code, 0)
        self.assertIn('RECORDED-MISSING [404] ' + GONE_POST, output)
        self.assertIn('0 confirmed dead, 1 already recorded missing in the case ledger', output)

    def test_missing_collection_reported_links_are_listed_without_failing(self):
        code, output = self.run_main({LIVE_POST: 'dead'})
        self.assertEqual(code, 0)
        self.assertIn('REPORTED-SOURCE-MISSING [404] ' + LIVE_POST, output)
        self.assertIn('1 missing collection-reported ledger links', output)

    def test_a_new_404_in_primary_evidence_is_reported_and_fails(self):
        code, output = self.run_main({GONE_POST: 'dead', FORK: 'dead'})
        self.assertEqual(code, 1)
        self.assertIn('DEAD [404] ' + FORK, output)
        self.assertIn('1 confirmed dead, 1 already recorded missing', output)


if __name__ == '__main__':
    unittest.main()
