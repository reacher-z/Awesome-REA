"""The / search shortcut honors prefers-reduced-motion, matching the stylesheet's reduced-motion scroll rule."""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ShortcutMotionTests(unittest.TestCase):
    def test_shortcut_follows_the_motion_preference(self):
        result = subprocess.run(['node', str(ROOT / 'tests/shortcut_motion_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Search shortcut motion checks passed', result.stdout)

    def test_no_script_scroll_hardcodes_smooth_behavior(self):
        # CSS already turns smooth scrolling off for reduced motion; script scrolls must not override it.
        app = (ROOT / 'site/app.js').read_text(encoding='utf-8')
        self.assertNotRegex(app, r'behavior\s*:\s*"smooth"\s*}')
        css = (ROOT / 'site/styles.css').read_text(encoding='utf-8')
        self.assertRegex(css, r'@media\(prefers-reduced-motion:reduce\)\{\s*html\{scroll-behavior:auto\}')


if __name__ == '__main__':
    unittest.main()
