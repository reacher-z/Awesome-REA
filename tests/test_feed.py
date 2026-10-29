"""Atom feeds list dated curated additions and papers deterministically, never review dates."""
from copy import deepcopy
import datetime as dt
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_feed import FEED_PAGES, FEED_SIZE, build_feeds, feed_entries
# A module import keeps that file's test case out of this module's discovery.
import test_review_date_tolerance as samples
from validate import public_https_error, validate_resources
from validate_papers import validate_papers
from validate_site import Page, validate_feeds

ATOM = '{http://www.w3.org/2005/Atom}'
NOW = dt.datetime(2026, 10, 18, 12, tzinfo=dt.timezone.utc)


def resource(identifier, added_at=None, **changes):
    record = samples.minimal_resource('2026-10-01')
    record.update(id=identifier, name=f'Tool {identifier}', name_zh=f'工具 {identifier}', **changes)
    if added_at:
        record['added_at'] = added_at
    return record


def paper(identifier, added_at=None):
    record = samples.minimal_paper('2026-10-01')
    record.update(id=identifier, title=f'Paper {identifier}', title_zh=f'论文 {identifier}')
    if added_at:
        record['added_at'] = added_at
    return record


def site(directory):
    for prefix in ('', 'zh/'):
        for page in FEED_PAGES:
            path = Path(directory) / (prefix + page.lstrip('/')) / 'index.html'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('<!doctype html><html><head><title>x</title></head><body></body></html>', encoding='utf-8')


class FeedTests(unittest.TestCase):
    def test_entries_use_inclusion_dates_newest_first(self):
        resources = [resource('old', '2026-10-15'), resource('undated'), resource('same-day-a', '2026-10-17'),
                     resource('same-day-b', '2026-10-17', verified_at='2026-10-18')]
        papers = [paper('paper-new', '2026-10-18')]
        entries = feed_entries(resources, papers)
        self.assertEqual([record['id'] for _, record in entries], ['paper-new', 'same-day-b', 'same-day-a', 'old'])
        self.assertEqual(entries[0][0], 'paper')
        many = [resource(f'tool-{index}', f'2026-10-{index % 18 + 1:02d}') for index in range(FEED_SIZE + 5)]
        self.assertEqual(len(feed_entries(many, [])), FEED_SIZE)

    def test_feeds_are_localized_deterministic_and_linked(self):
        resources = [resource('ghidra-like', '2026-10-15', kind='case-study', category='reconstruction-cases',
                              relationship='independent-reconstruction',
                              description_en='Rebuilds <markup> & keeps "quotes".')]
        papers = [paper('paper-example', '2026-10-16')]
        outputs = []
        for _ in range(2):
            with TemporaryDirectory() as directory:
                site(directory)
                self.assertEqual(build_feeds(Path(directory), resources, papers), ['/feed.xml', '/zh/feed.xml'])
                outputs.append({path: (Path(directory) / path).read_bytes() for path in ('feed.xml', 'zh/feed.xml')})
                english = (Path(directory) / 'resources/index.html').read_text(encoding='utf-8')
                chinese = (Path(directory) / 'zh/index.html').read_text(encoding='utf-8')
                self.assertIn('<link rel="alternate" type="application/atom+xml" title="AwesomeREA.org: newly added entries" href="/feed.xml">', english)
                self.assertIn('href="/zh/feed.xml"', chinese)
        self.assertEqual(outputs[0], outputs[1])
        root = ET.fromstring(outputs[0]['zh/feed.xml'])
        self.assertEqual(root.findtext(ATOM + 'updated'), '2026-10-16T00:00:00Z')
        entries = root.findall(ATOM + 'entry')
        self.assertEqual([entry.findtext(ATOM + 'id') for entry in entries],
                         ['https://awesomerea.org/zh/papers/paper-example/', 'https://awesomerea.org/zh/resources/ghidra-like/'])
        self.assertEqual(entries[1].findtext(ATOM + 'title'), '工具 ghidra-like')
        self.assertEqual(entries[1].find(ATOM + 'category').get('label'), '案例')
        english = ET.fromstring(outputs[0]['feed.xml']).findall(ATOM + 'entry')[1]
        self.assertEqual(english.findtext(ATOM + 'summary'), 'Rebuilds <markup> & keeps "quotes".')
        self.assertEqual(english.findtext(ATOM + 'published'), '2026-10-15T00:00:00Z')
        self.assertNotIn(b'2026-10-01', outputs[0]['feed.xml'])

    def test_no_dated_records_write_no_feed_or_link(self):
        with TemporaryDirectory() as directory:
            site(directory)
            self.assertEqual(build_feeds(Path(directory), [resource('undated')], [paper('paper-undated')]), [])
            self.assertFalse((Path(directory) / 'feed.xml').exists())
            self.assertNotIn('atom+xml', (Path(directory) / 'index.html').read_text(encoding='utf-8'))

    def test_site_validator_binds_feeds_to_records_and_pages(self):
        resources, papers = [resource('dated', '2026-10-15'), resource('undated')], [paper('paper-dated', '2026-10-16')]
        with TemporaryDirectory() as directory:
            output = Path(directory)
            site(directory)
            (output / '_headers').write_text((ROOT / 'site/_headers').read_text(encoding='utf-8'), encoding='utf-8')
            build_feeds(output, resources, papers)

            def pages():
                listing = {('/zh' if prefix else '') + (page or '/'): Page((output / (prefix + page.lstrip('/')) / 'index.html').read_text(encoding='utf-8'))
                           for prefix in ('', 'zh/') for page in FEED_PAGES}
                details = {f'{prefix}/{kind}/{identifier}/': Page('<html></html>') for prefix in ('', '/zh')
                           for kind, identifier in (('resources', 'dated'), ('papers', 'paper-dated'))}
                return {**listing, **details}

            validate_feeds(output, pages(), resources, papers)
            with self.assertRaisesRegex(AssertionError, 'entry count'):
                validate_feeds(output, pages(), [*resources, resource('late', '2026-10-17')], papers)
            feed = output / 'zh/feed.xml'
            feed.write_text(feed.read_text(encoding='utf-8').replace('工具 dated', 'Tool dated'), encoding='utf-8')
            with self.assertRaisesRegex(AssertionError, 'differs from its record'):
                validate_feeds(output, pages(), resources, papers)
            cases = output / 'cases/index.html'
            cases.write_text(cases.read_text(encoding='utf-8').replace('href="/feed.xml"', 'href="/zh/feed.xml"'), encoding='utf-8')
            with self.assertRaisesRegex(AssertionError, 'link their language feed'):
                validate_feeds(output, pages(), resources, papers)

    def test_validators_reject_malformed_or_future_inclusion_dates(self):
        for value, valid in (('2026-10-18', True), ('2026-10-19', True), ('2026-10-20', False),
                             ('2026-02-30', False), ('2026-10-18T00:00:00Z', False), (20261018, False)):
            record = samples.minimal_resource('2026-10-01')
            record['added_at'] = value
            errors = []
            validate_resources([record], errors, now=NOW)
            entry = samples.minimal_paper('2026-10-01')
            entry['added_at'] = value
            validate_papers([entry], errors, url_check=public_https_error, now=NOW)
            with self.subTest(value=value):
                self.assertEqual(errors == [], valid, errors)
                self.assertTrue(all('.added_at:' in error for error in errors))
        errors = []
        validate_papers([deepcopy(samples.minimal_paper('2026-10-01'))], errors, url_check=public_https_error, now=NOW)
        self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
