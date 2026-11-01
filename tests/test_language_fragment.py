"""Static language links keep the reader's card or section: the script loads where needed and IDs match across languages."""
from collections import Counter
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_site
from language_fragment import HEADER, add_language_fragment_script, language_fragment_script

IDS = re.compile(r'\sid="([^"]+)"')


class LanguageFragmentTests(unittest.TestCase):
    def test_browser_logic(self):
        result = subprocess.run(['node', str(ROOT / 'tests/language_fragment_ui.cjs')], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Static language fragment checks passed', result.stdout)

    def test_built_pages_load_the_script_and_share_ids_with_their_counterpart(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'dist'
            build_site.build_site(output)
            tag = language_fragment_script(output)
            self.assertEqual((output / 'language-fragment.js').read_bytes(), (ROOT / 'site/language-fragment.js').read_bytes())
            kinds = Counter()
            for page in sorted(output.rglob('*.html')):
                route = page.relative_to(output).as_posix()
                html = page.read_text(encoding='utf-8')
                header = HEADER.search(html)
                expected = route not in ('index.html', 'zh/index.html') and bool(header) and 'hreflang=' in header.group(0)
                with self.subTest(route=route):
                    self.assertEqual(html.count(tag), int(expected))
                    self.assertNotIn('language-fragment.js', html.replace(tag, ''))
                if not expected or route.startswith('zh/'):
                    continue
                counterpart = output / 'zh' / route
                self.assertTrue(counterpart.is_file(), route)
                with self.subTest(route=route, check='ids'):
                    # The script carries a fragment only when it names an element on the current page.
                    self.assertEqual(set(IDS.findall(html)), set(IDS.findall(counterpart.read_text(encoding='utf-8'))))
                parts = route.split('/')
                kinds[parts[0] + ('/<id>' if parts[0] in ('resources', 'papers', 'browse') and len(parts) > 2 else '')] += 1
            for kind in ('browse', 'browse/<id>', 'resources', 'resources/<id>', 'papers', 'papers/<id>', 'cases', 'about', 'survey'):
                self.assertGreater(kinds[kind], 0, kind)
            self.assertNotIn('language-fragment.js', (output / '404.html').read_text(encoding='utf-8'))

    def test_pages_are_changed_once(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'language-fragment.js').write_text('/* fixture */\n', encoding='utf-8')
            (output / 'zh').mkdir()
            linked = '<html><head><title>x</title></head><body><header class="site-header"><a hreflang="zh-CN" href="/zh/x/">中文</a></header></body></html>'
            for route in ('index.html', 'zh/index.html', 'page.html'):
                (output / route).write_text(linked, encoding='utf-8')
            (output / 'plain.html').write_text('<html><head></head><body><header class="site-header"></header></body></html>', encoding='utf-8')
            self.assertEqual(add_language_fragment_script(output), 1)
            self.assertIn(language_fragment_script(output) + '\n</head>', (output / 'page.html').read_text(encoding='utf-8'))
            for route in ('index.html', 'zh/index.html', 'plain.html'):
                self.assertNotIn('<script', (output / route).read_text(encoding='utf-8'))
            with self.assertRaises(ValueError):
                add_language_fragment_script(output)


if __name__ == '__main__':
    unittest.main()
