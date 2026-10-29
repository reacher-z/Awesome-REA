"""Keep the generated repository directory free of pages the generator no longer renders."""
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_repository_index
from build_repository_index import CATEGORIES, GENERATED_MARKER


def snapshot(directory):
    return {path.name: path.read_bytes() for path in directory.glob('*.md')}


def setUpModule():
    """Render the index once for both classes; neither test class changes what it returns."""
    global RENDERED
    RENDERED = build_repository_index.rendered_files()


class RepositoryIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rendered = RENDERED

    def run_generator(self, output, *arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(build_repository_index, 'OUTPUT', output), \
                patch.object(build_repository_index, 'rendered_files', return_value=self.rendered), \
                patch.object(sys, 'argv', ['build_repository_index.py', *arguments]), \
                redirect_stdout(stdout), redirect_stderr(stderr):
            code = build_repository_index.main()
        return code, stderr.getvalue()

    def test_category_pages_link_their_website_category_page(self):
        from build_browse_pages import browse_path
        files, _ = self.rendered
        for category, labels in CATEGORIES.items():
            for language, suffix, label in (('en', '', 'On the website'), ('zh', '.zh-CN', '在网站浏览')):
                with self.subTest(category=category, language=language):
                    navigation = files[f'{category}{suffix}.md'].splitlines()[2]
                    self.assertIn(f'[{label}](https://awesomerea.org{browse_path(language, category)})', navigation)
                    self.assertEqual(navigation.count('https://awesomerea.org/'), 1)

    def test_obsolete_pages_fail_check_and_only_generated_ones_are_removed(self):
        tracked = ROOT / 'docs/repositories'
        before = snapshot(tracked)
        files, _ = self.rendered
        pages = {name for name in files if not name.startswith('../')}
        self.assertEqual(len(pages), 2 * (len(CATEGORIES) + 1))
        self.assertEqual(set(before), pages)
        with tempfile.TemporaryDirectory() as directory:
            # Mirror the repository layout so the root README summaries resolve inside the copy.
            output = Path(directory) / 'docs/repositories'
            shutil.copytree(tracked, output)
            for name in ('README.md', 'README.zh-CN.md'):
                shutil.copy2(ROOT / name, Path(directory) / name)
            self.assertEqual(self.run_generator(output, '--check'), (0, ''))

            (output / 'old-category.md').write_text('# Old category\n\n' + GENERATED_MARKER + '\n', encoding='utf-8')
            (output / 'notes.md').write_text('# Maintainer notes\n', encoding='utf-8')
            code, message = self.run_generator(output, '--check')
            self.assertEqual(code, 1)
            self.assertIn('docs/repositories/old-category.md', message)
            self.assertIn('docs/repositories/notes.md', message)

            code, message = self.run_generator(output)
            self.assertEqual(code, 0)
            self.assertFalse((output / 'old-category.md').exists())
            self.assertEqual((output / 'notes.md').read_text(encoding='utf-8'), '# Maintainer notes\n')
            self.assertIn('Kept docs/repositories/notes.md', message)
            self.assertEqual({name: data for name, data in snapshot(output).items() if name != 'notes.md'}, before)
            for name in ('README.md', 'README.zh-CN.md'):
                self.assertEqual((Path(directory) / name).read_bytes(), (ROOT / name).read_bytes())

            code, message = self.run_generator(output, '--check')
            self.assertEqual(code, 1)
            self.assertIn('docs/repositories/notes.md', message)
            self.assertNotIn('old-category.md', message)
            self.assertNotIn('needs regeneration', message)
        self.assertEqual(snapshot(tracked), before)


class RelatedMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, _ = RENDERED

    def line(self, page, repository):
        lines = [line for line in self.files[page].splitlines() if line.startswith(f'- [{repository}](https://github.com/')]
        self.assertEqual(len(lines), 1, repository)
        return lines[0]

    def test_exact_curated_and_paper_matches_link_their_pages_in_both_languages(self):
        cases = [('protocol-analysis{}.md', 'netzob/netzob', ('Curated', '精选'), 'resources/netzob/'),
                 ('protocol-analysis{}.md', 'yapengye/NetPlier', ('Paper', '论文'), 'papers/paper-netplier/')]
        for page, repository, labels, path in cases:
            for suffix, zh in (('', False), ('.zh-CN', True)):
                with self.subTest(repository=repository, zh=zh):
                    line = self.line(page.format(suffix), repository)
                    prefix = 'https://awesomerea.org/' + ('zh/' if zh else '')
                    self.assertRegex(line, re.escape(f" · {labels[zh]}{'：' if zh else ': '}[") + r'[^]]+' + re.escape(f']({prefix}{path})') + '$')
                    self.assertLess(line.index('星标]**' if zh else 'stars]**'), line.index(' · ' + labels[zh]))

    def test_marker_lines_match_related_entries_and_tables_count_them(self):
        marked = [line for name, text in self.files.items() if not name.startswith('../') and not name.startswith('README')
                  for line in text.splitlines() if line.startswith('- [') and 'https://awesomerea.org/' in line]
        english = [line for line in marked if ' · Curated: ' in line or ' · Paper: ' in line]
        chinese = [line for line in marked if ' · 精选：' in line or ' · 论文：' in line]
        self.assertEqual(len(english), len(chinese))
        self.assertEqual(len(marked), len(english) + len(chinese))
        table = [row for row in self.files['README.md'].splitlines() if row.startswith('| [')]
        self.assertEqual(sum(int(row.rsplit('|', 2)[1].replace(',', '')) for row in table), len(english))

    def test_markers_render_titles_literally_and_skip_unmatched_records(self):
        entry = {'kind': 'curated', 'title_en': 'A [b]', 'title_zh': '甲 [乙]', 'href_en': '/resources/a/', 'href_zh': '/zh/resources/a/'}
        paper = {'kind': 'paper', 'title_en': 'P', 'title_zh': '论', 'href_en': '/papers/paper-p/', 'href_zh': '/zh/papers/paper-p/'}
        record = {'related_entries': [paper, entry]}
        self.assertEqual(build_repository_index.related_markers(record, 'en'),
                         ' · Paper: [P](https://awesomerea.org/papers/paper-p/) · Curated: [A \\[b\\]](https://awesomerea.org/resources/a/)')
        self.assertEqual(build_repository_index.related_markers(record, 'zh'),
                         ' · 论文：[论](https://awesomerea.org/zh/papers/paper-p/) · 精选：[甲 \\[乙\\]](https://awesomerea.org/zh/resources/a/)')
        self.assertEqual(build_repository_index.related_markers({}, 'en'), '')

    def test_check_fails_when_a_marker_is_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'docs/repositories'
            shutil.copytree(ROOT / 'docs/repositories', output)
            for name in ('README.md', 'README.zh-CN.md'):
                shutil.copy2(ROOT / name, Path(directory) / name)
            page = output / 'protocol-analysis.md'
            page.write_text(re.sub(r' · Curated: \[Netzob\]\([^)]*\)', '', page.read_text(encoding='utf-8')), encoding='utf-8')
            stderr = io.StringIO()
            with patch.object(build_repository_index, 'OUTPUT', output), \
                    patch.object(build_repository_index, 'rendered_files', return_value=(self.files, 0)), \
                    patch.object(sys, 'argv', ['build_repository_index.py', '--check']), \
                    redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                self.assertEqual(build_repository_index.main(), 1)
            self.assertIn('needs regeneration', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
