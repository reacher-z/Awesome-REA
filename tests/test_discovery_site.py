"""Website outputs of the unreviewed discovery queue: list pages, feeds, JSON, status and the main feed entries."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import build_discoveries as site
from build_feed import FEED_PAGES, build_feeds
import discoveries
from test_discoveries import capture, make_batch
import test_feed
from validate_site import Page, validate_feeds

ATOM = '{http://www.w3.org/2005/Atom}'


def queue_root(directory, batches):
    folder = Path(directory) / discoveries.DIRECTORY
    folder.mkdir(parents=True)
    for batch in batches:
        (folder / f"{batch['batch_id']}.json").write_bytes(discoveries.batch_bytes(batch))
    return Path(directory)


def sample_queue(directory, published=None):
    first = make_batch([capture(1, observed='2026-11-05T10:00:00.000000Z'), capture(2, observed='2026-11-05T10:01:00.000000Z')],
                       run_id=100, ingested='2026-11-05T11:00:00Z')
    second = make_batch([capture(3), capture(4)], run_id=200, ingested='2026-11-05T17:00:00Z')
    root = queue_root(directory, [first, second])
    return site.discovery_queue(root, published, [], [])


class QueueTest(unittest.TestCase):
    def test_newest_batch_first_and_published_records_are_counted_not_listed(self):
        with tempfile.TemporaryDirectory() as directory:
            published = {'resources': [{'id': capture(1)['id'], 'full_name': capture(1)['full_name']}]}
            queue = sample_queue(directory, published)
        self.assertEqual([row['id'] for row in queue['listed']], ['scan-9000000003', 'scan-9000000004', 'scan-9000000002'])
        self.assertEqual((queue['record_count'], queue['since_published']), (4, 1))
        self.assertEqual(queue['listed'][0]['ingested_at'], '2026-11-05T17:00:00Z')
        self.assertEqual(queue['latest']['batch_id'], 'run-200-1')

    def test_a_rerun_of_an_older_scan_ingested_later_is_the_latest_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            newer_run = make_batch([capture(1, observed='2026-11-05T10:00:00.000000Z')], run_id=200, ingested='2026-11-05T11:00:00Z')
            older_run_later = make_batch([capture(2)], run_id=100, ingested='2026-11-05T17:00:00Z')
            queue = site.discovery_queue(queue_root(directory, [newer_run, older_run_later]), None, [], [])
            report = discoveries.summary(Path(directory))
        self.assertEqual(queue['latest']['batch_id'], 'run-100-1')
        self.assertEqual([row['batch_id'] for row in queue['listed']], ['run-100-1', 'run-200-1'])
        self.assertEqual((report['last_batch_id'], report['last_successful_ingest_at']), ('run-100-1', '2026-11-05T17:00:00Z'))

    def test_batch_exports_cover_every_listed_record(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = sample_queue(directory)
        export = site.export_document(queue, 'https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA')
        paged = []
        for entry in export['batches']:
            batch = next(item for item in queue['batches'] if item['batch_id'] == entry['batch_id'])
            page = site.batch_export(queue, batch)
            self.assertEqual(entry['records_url'], f"https://awesomerea.org/discoveries/batches/{entry['batch_id']}.json")
            self.assertEqual(len(page['resources']), entry['listed_count'])
            paged.extend(row['id'] for row in page['resources'])
        self.assertEqual(paged, [row['id'] for row in queue['listed']])
        with patch.object(site, 'EXPORT_RECORDS', 1):
            self.assertEqual(len(site.export_document(queue, 'https://awesomerea.org', 'x')['resources']), 1)

    def test_exports_label_every_record_unreviewed_and_name_the_last_ingest(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = sample_queue(directory)
        export = site.export_document(queue, 'https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA')
        self.assertEqual((export['version'], export['review_status'], export['verification']), (1, 'unreviewed', 'automated-readme-scan'))
        self.assertEqual(export['generated_at'], '2026-11-05T17:00:00Z')
        self.assertTrue(all(row['review_status'] == 'unreviewed' and row['verification'] == 'automated-readme-scan'
                            for row in export['resources']))
        self.assertEqual(export['batches'][0]['source_file'],
                         'https://github.com/reacher-z/Awesome-REA/blob/main/data/discoveries/run-200-1.json')
        self.assertNotIn('"verification": "source-reviewed"', json.dumps(export))
        status = site.status_document(queue, 'https://awesomerea.org')
        self.assertEqual((status['last_successful_ingest_at'], status['last_scan_run_id'], status['stale_after_hours']),
                         ('2026-11-05T17:00:00Z', 200, 6))
        self.assertEqual(site.badge_document(queue)['message'], '2026-11-05 17:00 UTC')

    def test_list_page_cards_feed_and_llms_section(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = sample_queue(directory)
        for language in ('en', 'zh'):
            html = site.page_content(queue, language, False, 'https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA')
            self.assertEqual(html.count('<article class="source-card browse-repository"'), 4)
            self.assertLess(html.index('scan-9000000003'), html.index('scan-9000000002'))
            self.assertEqual(html.count('<h2 id="batch-'), 2)
            self.assertEqual(html.count('<h3>'), 4)
            self.assertIn(site.NOTE[language == 'zh'].replace('’', '’'), html.replace('&#x27;', "'"))
            feed = ET.fromstring(site.discovery_feed(queue, language, 'https://awesomerea.org'))
            entries = feed.findall(ATOM + 'entry')
            self.assertEqual([entry.findtext(ATOM + 'id') for entry in entries][:1], ['tag:awesomerea.org,2026:discovery:scan-9000000003'])
            self.assertEqual({entry.find(ATOM + 'category').get('term') for entry in entries}, {'unreviewed-discovery'})
            self.assertEqual(entries[0].find(ATOM + 'link').get('href'), capture(3)['url'])
        llms = site.llms_section(queue, 'https://awesomerea.org')
        self.assertTrue(llms.startswith('## Recently discovered repositories (unreviewed)'))
        self.assertIn('(unreviewed automated discovery)', llms)
        self.assertEqual(site.llms_section(None, 'https://awesomerea.org'), '')


class MainFeedTest(unittest.TestCase):
    def test_batch_summaries_join_the_main_feeds_and_validate(self):
        with tempfile.TemporaryDirectory() as data:
            queue = sample_queue(data)
        batches = site.main_feed_batches(queue)
        self.assertEqual([batch['batch_id'] for batch in batches], ['run-200-1', 'run-100-1'])
        resources = [test_feed.resource('dated-tool', '2026-11-05')]
        with tempfile.TemporaryDirectory() as directory:
            test_feed.site(directory)
            for language, route in site.PAGE_PATHS.items():
                path = Path(directory) / route.lstrip('/') / 'index.html'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('<!doctype html><html><head><title>x</title></head><body></body></html>', encoding='utf-8')
            self.assertEqual(build_feeds(directory, resources, [], discovery_batches=batches), ['/feed.xml', '/zh/feed.xml'])
            root = ET.parse(Path(directory) / 'feed.xml').getroot()
            entries = root.findall(ATOM + 'entry')
            self.assertEqual([entry.find(ATOM + 'category').get('term') for entry in entries],
                             ['unreviewed-discovery', 'unreviewed-discovery', 'case-study' if False else resources[0]['kind']])
            self.assertEqual(root.findtext(ATOM + 'updated'), '2026-11-05T17:00:00Z')
            self.assertEqual(entries[0].find(ATOM + 'link').get('href'), 'https://awesomerea.org/discoveries/')
            (Path(directory) / '_headers').write_text('/feed.xml\n  Content-Type: application/atom+xml; charset=utf-8\n'
                                                      '/zh/feed.xml\n  Content-Type: application/atom+xml; charset=utf-8\n', encoding='utf-8')
            pages = {}
            for prefix in ('', '/zh'):
                for page in (*FEED_PAGES, '/discoveries/'):
                    route = (prefix + page) or '/'
                    route = route if route.endswith('/') else route + '/'
                    text = (Path(directory) / route.lstrip('/') / 'index.html').read_text(encoding='utf-8')
                    pages[route] = Page(text)
            for prefix in ('', '/zh'):
                for page in FEED_PAGES[1:]:
                    pages[prefix + page] = pages.pop(prefix + page)
            routes = {f'/{kind}s/{record["id"]}/': None for kind, record in [('resource', resources[0])]}
            for route in [*routes, *('/zh' + route for route in routes)]:
                pages[route] = Page('<!doctype html><html><head></head><body></body></html>')
            validate_feeds(directory, pages, resources, [], batches)
            broken = deepcopy(batches)
            broken[0]['run_id'] = 999
            with self.assertRaises(AssertionError):
                validate_feeds(directory, pages, resources, [], broken)


if __name__ == '__main__':
    unittest.main()
