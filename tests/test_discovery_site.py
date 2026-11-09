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
import discovery_classes
from page_metadata import description_problem
from test_discoveries import capture, make_batch
import test_feed
from validate_site import Page, validate_discovery_outputs, validate_feeds

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
                         ('2026-11-05T17:00:00Z', 200, 9))
        self.assertEqual(tuple(status[key] for key in ('listed', 'data_points', 'other_captures', 'captures_listed')),
                         (4, 0, 0, 4))
        self.assertEqual(site.badge_document(queue)['message'], '2026-11-05 17:00 UTC')

    def test_list_page_cards_feed_and_llms_section(self):
        with tempfile.TemporaryDirectory() as directory:
            queue = sample_queue(directory)
        for language in ('en', 'zh'):
            html = site.page_content(queue, language, False, 'https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA')
            self.assertEqual(html.count('<article class="source-card browse-repository"'), 0)
            self.assertNotIn('<h2 id="class-', html)
            self.assertIn(('暂无数据点。' if language == 'zh' else 'No data points yet.'), html)
            self.assertIn(('4 条待分类记录' if language == 'zh' else '4 not yet classified'), html)
            self.assertIn(site.NOTE[language == 'zh'].replace('’', '’'), html.replace('&#x27;', "'"))
            feed = ET.fromstring(site.discovery_feed(queue, language, 'https://awesomerea.org'))
            entries = feed.findall(ATOM + 'entry')
            self.assertEqual(entries, [])
        llms = site.llms_section(queue, 'https://awesomerea.org')
        self.assertTrue(llms.startswith('## Recently discovered data points'))
        self.assertNotIn('(unreviewed automated discovery)', llms)
        self.assertEqual(site.llms_section(None, 'https://awesomerea.org'), '')

    def test_class_sections_data_first_limit_and_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            root.mkdir(exist_ok=True)
            classifications = {
                capture(1)['id']: {'decision': 'data', 'class': 'game', 'reproduced': 'A <game> engine'},
                capture(2)['id']: {'decision': 'data', 'class': 'software', 'reproduced': 'A desktop app'},
                capture(3)['id']: {'decision': 'outside'},
            }
            (root / 'data').mkdir()
            (root / discovery_classes.FILE).write_text(json.dumps(classifications), encoding='utf-8')
            queue = sample_queue(directory)
        for language, labels in (('en', ('Software', 'Game')),
                                 ('zh', ('软件', '游戏'))):
            html = site.page_content(queue, language, False, 'https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA')
            self.assertEqual(html.count('<article class="source-card browse-repository"'), 2)
            self.assertLess(html.index('id="class-software"'), html.index('id="class-game"'))
            for label in labels:
                count = ' · 显示 1 条，共 1 条' if language == 'zh' else ' · 1 of 1'
                self.assertIn(label.replace('&', '&amp;') + count, html)
            self.assertNotIn('id="class-apps"', html)
            self.assertNotIn('id="class-tools-other"', html)
            self.assertNotIn('id="class-unclassified"', html)
            self.assertNotIn('scan-9000000003', html)
            self.assertNotIn('scan-9000000004', html)
            if language == 'en':
                self.assertIn('A &lt;game&gt; engine', html)
            else:
                self.assertNotIn('A &lt;game&gt; engine', html)
                self.assertNotIn('A desktop app', html)
            self.assertIn(('数据点：共 2 条，本页显示 <span data-discovery-shown>2</span> 条；另有 1 条其他采集记录和 1 条待分类记录'
                           if language == 'zh' else
                           'Data points: 2 listed, <span data-discovery-shown>2</span> shown here. 1 other captures and 1 not yet classified'), html)
            self.assertIn(f'<a href="{site.EXPORT_PATH}">{"原始数据下载" if language == "zh" else "raw download"}</a>', html)
            with patch.object(site, 'CLASS_RECORDS', 0):
                limited = site.page_content(queue, language, False, 'https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA')
                self.assertEqual(limited.count('<article class="source-card browse-repository"'), 0)
            feed = ET.fromstring(site.discovery_feed(queue, language, 'https://awesomerea.org'))
            self.assertEqual([entry.findtext(ATOM + 'id') for entry in feed.findall(ATOM + 'entry')],
                             ['tag:awesomerea.org,2026:discovery:scan-9000000002',
                              'tag:awesomerea.org,2026:discovery:scan-9000000001'])
        exported = site.export_document(queue, 'https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA')['resources']
        self.assertEqual([row['id'] for row in exported], [row['id'] for row in queue['listed']])
        by_id = {row['id']: row for row in exported}
        self.assertEqual([by_id[capture(1)['id']][key] for key in ('data_decision', 'class', 'reproduced')],
                         ['data', 'game', 'A <game> engine'])
        self.assertEqual(by_id[capture(3)['id']]['data_decision'], 'outside')
        self.assertNotIn('class', by_id[capture(3)['id']])
        self.assertNotIn('data_decision', by_id[capture(4)['id']])
        batch = next(item for item in queue['batches'] if item['batch_id'] == 'run-200-1')
        self.assertEqual([row['id'] for row in site.batch_export(queue, batch)['resources']],
                         [capture(3)['id'], capture(4)['id']])
        status = site.status_document(queue, 'https://awesomerea.org')
        self.assertEqual(tuple(status[key] for key in ('listed', 'data_points', 'other_captures', 'captures_listed')),
                         (3, 2, 1, 4))

    def test_site_validator_accepts_class_limited_page_and_data_point_feed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            classes = {capture(number)['id']: {'decision': 'data', 'class': kind, 'reproduced': 'Rebuilt thing'}
                       for number, kind in ((1, 'game'), (2, 'game'), (3, 'software'))}
            classes[capture(4)['id']] = {'decision': 'outside'}
            (root / discovery_classes.FILE).write_text(json.dumps(classes), encoding='utf-8')
            sample_queue(directory)
            output = root / 'site'
            output.mkdir()
            catalog = {'resources': [], 'meta': {'site_url': 'https://awesomerea.org',
                                                'repository_url': 'https://github.com/reacher-z/Awesome-REA'}}
            with patch.object(site, 'CLASS_RECORDS', 1):
                routes, queue = site.write_discoveries(output, catalog, [], None, root=root)
                (output / '_headers').write_text(
                    '/discoveries.json\n  Cache-Control: no-cache, must-revalidate\n'
                    '/discoveries/status.json\n  Cache-Control: no-cache, must-revalidate\n'
                    '/discoveries/badge.json\n  Cache-Control: no-cache, must-revalidate\n'
                    '/discoveries/batches/*\n  Cache-Control: no-cache, must-revalidate\n'
                    '/discoveries/feed.xml\n  Content-Type: application/atom+xml; charset=utf-8\n'
                    '/zh/discoveries/feed.xml\n  Content-Type: application/atom+xml; charset=utf-8\n',
                    encoding='utf-8')
                validate_discovery_outputs(output, dict.fromkeys(routes), queue)
                for route in routes:
                    page = Page((output / route.lstrip('/') / 'index.html').read_text(encoding='utf-8'))
                    self.assertIsNone(description_problem(page.meta['description']))
                # Game has two data points and the list page shows one, so Game gets a page with both.
                self.assertEqual(routes, ['/discoveries/', '/zh/discoveries/', '/discoveries/game/', '/zh/discoveries/game/'])
                export = json.loads((output / 'discoveries.json').read_text(encoding='utf-8'))
                self.assertEqual(export['class_pages'], [{'class': 'game', 'data_points': 2,
                                                          'page': 'https://awesomerea.org/discoveries/game/'}])
                for language, prefix in (('en', ''), ('zh', '/zh')):
                    listing = (output / prefix.lstrip('/') / 'discoveries/index.html').read_text(encoding='utf-8')
                    self.assertEqual(listing.count('data-discovery-more='), 1)
                    self.assertIn(f'href="{prefix}/discoveries/game/" data-discovery-more="game">', listing)
                    self.assertIn('Show all 2<span class="mono">+1</span>' if language == 'en'
                                  else '显示全部 2 条<span class="mono">+1</span>', listing)
                    page = (output / prefix.lstrip('/') / 'discoveries/game/index.html').read_text(encoding='utf-8')
                    self.assertEqual(page.count('<article class="source-card browse-repository"'), 2)
                    self.assertNotIn('data-discovery-more', page)
                    self.assertIn(f'<a href="{prefix}/discoveries/">', page)
            with patch.object(site, 'CLASS_RECORDS', 2):
                self.assertEqual(site.class_pages(queue), [])

    def test_feed_is_newest_first_across_classes_and_page_is_newest_within_class(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            classes = {capture(number)['id']: {'decision': 'data', 'class': kind, 'reproduced': 'Rebuilt thing'}
                       for number, kind in ((1, 'game'), (2, 'game'), (3, 'software'), (4, 'game'))}
            (root / discovery_classes.FILE).write_text(json.dumps(classes), encoding='utf-8')
            queue = sample_queue(directory)
        html = site.page_content(queue, 'en', False, 'https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA')
        self.assertLess(html.index('id="class-software"'), html.index('id="class-game"'))
        self.assertLess(html.index('scan-9000000004'), html.index('scan-9000000002'))
        self.assertLess(html.index('scan-9000000002'), html.index('scan-9000000001'))
        feed = ET.fromstring(site.discovery_feed(queue, 'en', 'https://awesomerea.org'))
        self.assertEqual([entry.findtext(ATOM + 'id').rsplit(':', 1)[-1] for entry in feed.findall(ATOM + 'entry')],
                         [capture(number)['id'] for number in (3, 4, 2, 1)])


class MainFeedTest(unittest.TestCase):
    def test_batch_summaries_join_the_main_feeds_and_validate(self):
        with tempfile.TemporaryDirectory() as data:
            root = Path(data)
            (root / 'data').mkdir()
            classes = {capture(number)['id']: {'decision': 'data', 'class': 'game', 'reproduced': 'Rebuilt game'}
                       for number in (1, 3)}
            (root / discovery_classes.FILE).write_text(json.dumps(classes), encoding='utf-8')
            queue = sample_queue(data)
        batches = site.main_feed_batches(queue)
        self.assertEqual([batch['batch_id'] for batch in batches], ['run-200-1', 'run-100-1'])
        self.assertEqual([[record['id'] for record in batch['records']] for batch in batches],
                         [[capture(3)['id']], [capture(1)['id']]])
        resources = [test_feed.resource('dated-tool', '2026-11-05')]
        with tempfile.TemporaryDirectory() as directory:
            test_feed.site(directory)
            for language, route in site.PAGE_PATHS.items():
                path = Path(directory) / route.lstrip('/') / 'index.html'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('<!doctype html><html><head><title>x</title></head><body></body></html>', encoding='utf-8')
            self.assertEqual(build_feeds(directory, resources, [], discovery_batches=batches), ['/feed.xml', '/zh/feed.xml', '/feed.json', '/zh/feed.json'])
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
