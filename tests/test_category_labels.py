"""One category wording: build_readme.CATEGORIES feeds entry pages and, through catalog.json, the homepage."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import CATEGORIES, KIND_LABELS, RELATIONSHIPS
from validate_site import validate_category_labels

APP = (ROOT / 'site/app.js').read_text(encoding='utf-8')


class CategoryLabelTests(unittest.TestCase):
    def test_app_js_has_no_literal_category_map(self):
        # Kind and relationship maps legitimately share a few IDs and Chinese words with categories.
        shared = set(KIND_LABELS) | set(RELATIONSHIPS)
        for category, (english, _) in CATEGORIES.items():
            with self.subTest(category=category):
                self.assertNotIn(english, APP)
                if category not in shared:
                    self.assertIsNone(re.search(r'["\']' + re.escape(category) + r'["\']\s*:', APP))
        self.assertIn('state.categoryLabels = data.category_labels', APP)

    def test_catalog_labels_must_equal_the_python_map(self):
        labels = {category: list(names) for category, names in CATEGORIES.items()}
        cases = {'valid': (labels, 'agent-mcp'),
                 'homepage wording': ({**labels, 'agent-mcp': ['MCP servers', 'MCP 服务']}, 'agent-mcp'),
                 'missing map': (None, 'agent-mcp'),
                 'unknown category': (labels, 'mcp-servers')}
        for name, (category_labels, category) in cases.items():
            catalog = {'resources': [{'id': 'example', 'category': category}]}
            if category_labels is not None:
                catalog['category_labels'] = category_labels
            with self.subTest(case=name), tempfile.TemporaryDirectory() as directory:
                (Path(directory) / 'catalog.json').write_text(json.dumps(catalog), encoding='utf-8')
                if name == 'valid':
                    validate_category_labels(directory)
                else:
                    self.assertRaises(AssertionError, validate_category_labels, directory)

    def test_homepage_filter_and_cards_use_the_catalog_map(self):
        result = subprocess.run(['node', str(ROOT / 'tests/category_labels_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Category labels follow the catalog map in both languages', result.stdout)


if __name__ == '__main__':
    unittest.main()
