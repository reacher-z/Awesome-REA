"""Entry pages and /resources/ show each record's evidence class, its observations and its documented demo preview."""
from collections import Counter
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from build_entry_pages import EVIDENCE_REASONS, build_entry_pages, entry_path
from build_home import PINNED
from resource_listing import resource_listing
from test_entry_pages import resource


def page(root, record, language):
    return (root / entry_path('resource', record['id'], language).lstrip('/') / 'index.html').read_text(encoding='utf-8')


class EntryEvidenceClassTest(unittest.TestCase):
    def test_every_classifier_reason_has_bilingual_observation_text(self):
        document = json.loads((ROOT / 'data/evidence-classes.json').read_text(encoding='utf-8'))
        reasons = {entry['reason'] for entry in document['entries']
                   if entry.get('evidence_class') is not None and entry.get('basis') != 'manual-review'}
        self.assertEqual(reasons - EVIDENCE_REASONS.keys(), set())
        self.assertTrue(all(en and zh for en, zh in EVIDENCE_REASONS.values()))

    def test_class_badge_observation_and_guide_in_both_languages(self):
        record = resource(evidence_class=2, evidence_status='observed', scope='partial', runtime_status='not-run')
        notes = {record['id']: {'reason': 'code and docs only: no demo', 'checked_at': '2026-11-09T05:24:25+00:00'}}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_entry_pages(root, [record], [], evidence_notes=notes)
            english, chinese = page(root, record, 'en'), page(root, record, 'zh')
        self.assertIn('<a class="entry-class-link" href="#entry-evidence"><span class="evidence-class evidence-class-2">C2</span>', english)
        self.assertIn('id="entry-evidence">Evidence</h2>', english)
        self.assertIn('Code, documentation and a download method observed; no demo found.', english)
        self.assertIn('<dt>Scope</dt><dd>Partial</dd>', english)
        self.assertIn('<dt>Checked</dt><dd>2026-11-09</dd>', english)
        self.assertIn('/blob/main/docs/evidence-classes.md', english)
        self.assertIn('证据档位', chinese)
        self.assertIn('有代码、文档和下载方式；未发现演示。', chinese)
        self.assertIn('/blob/main/docs/evidence-classes.zh-CN.md', chinese)
        # The evidence section sits between the resource links and the requirements.
        self.assertLess(english.index('class="entry-actions"'), english.index('id="entry-evidence"'))
        self.assertLess(english.index('id="entry-evidence"'), english.index('id="entry-requirements"'))

    def test_class_zero_review_and_preview(self):
        review = {'version': 'README commit 37a01ca8746c121170644a07968d11263ef64407', 'reviewed_at': '2026-11-04',
                  'primary_evidence': 'https://github.com/storytold/photocraft/blob/37a01ca8746c121170644a07968d11263ef64407/README.md'}
        record = resource(evidence_class=0, evidence_status='observed', scope='full', evidence_review=review,
                          preview='/previews/example-resource.jpg', preview_kind='image')
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_entry_pages(root, [record], [])
            text = page(root, record, 'en')
        self.assertIn('evidence-class-0">C0</span> full software reconstruction', text)
        self.assertIn('<figure class="entry-preview"><img src="/previews/example-resource.jpg"', text)
        self.assertIn('<dt>Manual review</dt><dd>2026-11-04 · <a href="https://github.com/storytold/photocraft/blob/37a01ca', text)
        self.assertIn('<dt>Scope</dt><dd>Full reconstruction</dd>', text)

    def test_unknown_source_and_featured_mark(self):
        record = resource(id=PINNED[0], evidence_class=None, evidence_status='unknown', scope='unknown')
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_entry_pages(root, [record], [])
            english, chinese = page(root, record, 'en'), page(root, record, 'zh')
        self.assertIn('evidence-class-unknown">?</span> Source unavailable or unreadable at review time', english)
        self.assertNotIn('<dt>Scope</dt>', english)
        self.assertIn('<span class="entry-featured">Featured</span>', english)
        self.assertIn('<span class="entry-featured">精选</span>', chinese)

    def test_resources_listing_offers_every_class_with_its_count(self):
        records = [resource(id=f'r-{index}', evidence_class=value, evidence_status='observed')
                   for index, value in enumerate((0, 1, 1, 2, 2, 2, 3))]
        records.append(resource(id='r-unknown', evidence_class=None, evidence_status='unknown'))
        groups = {records[0]['category']: records}
        labels = {records[0]['category']: ('Tools', '工具')}
        for language, unknown in (('en', 'Unknown'), ('zh', '未知')):
            html = resource_listing(records, groups, labels, language, 'https://github.com/reacher-z/Awesome-REA')
            self.assertIn('data-class-select', html)
            for key, count in Counter({'0': 1, '1': 2, '2': 3, '3': 1}).items():
                self.assertIn(f'<option value="{key}">C{key} ({count})</option>', html)
            self.assertIn(f'<option value="unknown">{unknown} (1)</option>', html)
            self.assertIn('class="evidence-legend"', html)
            self.assertIn('docs/evidence-classes', html)


if __name__ == '__main__':
    unittest.main()
