"""Browse cards show the recorded last-push month as a collection-time snapshot, never an invented or judged date."""
from copy import deepcopy
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_browse_pages import build_browse_pages, repository_card
from test_source_browser import full_export

RECORD = {'id': 'scan-1', 'full_name': 'example/demo', 'name': 'demo', 'url': 'https://github.com/example/demo',
          'description_en': 'Demo.', 'description_zh': '演示。', 'stars': 249, 'license': 'MIT',
          'pushed_at': '2021-01-26T10:20:30Z'}
PUSHED = re.compile(r'<span class="source-card-pushed" title="([^"]+)">([^<]+) <time datetime="([^"]+)">([^<]+)</time></span>')


class BrowseLastPushTests(unittest.TestCase):
    def test_card_footer_shows_the_recorded_month_in_each_language(self):
        for language, label, title in (('en', 'Last push', 'Last push recorded at collection time'),
                                       ('zh', '最近推送', '采集时记录的最近推送时间快照')):
            html = repository_card(RECORD, language, False)
            footer = html[html.index('<div class="source-card-footer">'):]
            self.assertEqual(PUSHED.findall(footer), [(title, label, '2021-01-26T10:20:30Z', '2021-01')])
            self.assertLess(footer.index('README'), footer.index('source-card-pushed'))
            self.assertLess(footer.index('source-card-pushed'), footer.index('source-card-license'))
            for judgement in ('unmaintained', 'inactive', 'stale', 'abandoned', '停止维护', '不活跃'):
                self.assertNotIn(judgement, html)

    def test_missing_or_malformed_push_dates_are_omitted(self):
        for value in (None, '', 'unknown', '2021-01', 20210126, '2021-01-26T00:00:00Z"><script>'):
            record = deepcopy(RECORD)
            if value is None:
                del record['pushed_at']
            else:
                record['pushed_at'] = value
            for language in ('en', 'zh'):
                html = repository_card(record, language, False)
                self.assertNotIn('source-card-pushed', html)
                self.assertNotIn('<time', html)

    def test_every_category_page_card_has_a_push_month_and_the_note_calls_it_a_snapshot(self):
        document = full_export()
        months = {}
        for index, record in enumerate(document['resources']):
            record['pushed_at'] = f'202{index}-0{index + 1}-15T08:00:00Z'
            months[record['id']] = record['pushed_at'][:7]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_browse_pages(output, document, curated_count=1, site_url='https://awesomerea.org',
                               repository_url='https://github.com/reacher-z/Awesome-REA', styles_href='/styles.css',
                               browse_styles_href='/browse.css', favicon_href='/favicon.svg',
                               social_image_href='https://awesomerea.org/social-card.png', data_revision='0' * 16)
            for prefix, note in (('', 'Stars and last-push months are collection-time snapshots and do not indicate whether a project is maintained.'),
                                 ('zh/', '星标和最近推送月份均为采集时快照，不代表项目是否仍在维护。')):
                self.assertIn(note, (output / prefix / 'browse/index.html').read_text())
                cards = 0
                for page in (output / prefix / 'browse').glob('*/index.html'):
                    html = page.read_text()
                    for match in re.finditer(r'<article class="source-card browse-repository" id="([^"]+)"(.*?)</article>', html, re.S):
                        cards += 1
                        self.assertEqual([found[3] for found in PUSHED.findall(match[2])], [months[match[1]]])
                        self.assertIn(note, html)
                self.assertGreater(cards, 0)


if __name__ == '__main__':
    unittest.main()
