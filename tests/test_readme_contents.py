"""Keep README Contents counts tied to the sections the catalog actually renders."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import render_catalog, render_contents


def resource(**changes):
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text(encoding='utf-8'))[0])
    record.update(id='contents-fixture', category='web-analysis', kind='tool',
                  relationship='foundation', targets=['website'], url='https://example.com/tool')
    record.update(changes)
    return record


def paper(**changes):
    record = deepcopy(json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))[0])
    record.update(changes)
    return record


class ReadmeContentsTest(unittest.TestCase):
    def test_counts_follow_rendered_sections(self):
        listed = paper(url='https://example.com/paper')
        records = [
            resource(),
            resource(id='second-web-tool', url='https://example.com/second'),
            resource(id='case', kind='case-study', category='reconstruction-cases',
                     relationship='independent-reconstruction', targets=['game'], url='https://example.com/case'),
            resource(id='paper-copy', kind='research', category='learning', relationship='learning',
                     url=listed['url']),
        ]
        rendered = render_contents(records, [listed], 2864, 'en')
        self.assertIn('[Website](#website) <sub>2</sub>', rendered)
        self.assertIn('[Game](#game) <sub>1</sub>', rendered)
        self.assertIn('[Papers](#papers) <sub>1</sub>', rendered)
        self.assertIn('kind=case-study) <sub>1</sub>', rendered)
        self.assertIn('[Repository index](#full-repository-index) <sub>2,864</sub>', rendered)
        # A research record listed under Papers is not rendered in Learning, so it is not counted there.
        self.assertNotIn('#references-and-learning', rendered)
        self.assertNotIn('#references-and-learning', render_catalog(records, 'en', {listed['url']}))
        # Sections without entries have no anchor, so Contents must not link to them.
        self.assertNotIn('#protocol', rendered)

    def test_chinese_contents_use_chinese_labels_and_anchors(self):
        rendered = render_contents([resource()], [paper()], 10, 'zh')
        self.assertTrue(rendered.startswith('- **目标** · [网站](#website) <sub>1</sub>'))
        self.assertIn('[仓库索引](#完整仓库索引) <sub>10</sub>', rendered)
        self.assertIn('https://awesomerea.org/zh/?view=curated&kind=case-study', rendered)


if __name__ == '__main__':
    unittest.main()
