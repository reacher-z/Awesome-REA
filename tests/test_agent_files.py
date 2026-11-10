from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from agent_files import AGENT_FILES, add_front_matter, agents_markdown, write_agent_files  # noqa: E402


class AgentFilesTest(unittest.TestCase):
    def test_guide_lists_commands_and_counts(self):
        text = agents_markdown('https://awesomerea.org', 'https://github.com/reacher-z/Awesome-REA', resources=5191, papers=442,
                               cases=4025, repositories=3309, updated='2026-11-10')
        for needed in ('5,191 source-reviewed', '442 research papers', 'curl -sL https://awesomerea.org/resources/ghidra/index.md',
                       'hf papers read', '@misc{awesome-rea', 'year = {2026}', '/api/v1/resources.json', '/llms-full.txt'):
            self.assertIn(needed, text)

    def test_three_names_one_file(self):
        with tempfile.TemporaryDirectory() as folder:
            write_agent_files(Path(folder), 'https://awesomerea.org', 'https://github.com/x/y', resources=1, papers=1, cases=0,
                              repositories=0, updated='2026-11-10')
            self.assertEqual(len({(Path(folder) / name).read_text() for name in AGENT_FILES}), 1)

    def test_front_matter(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'zh/resources/ghidra').mkdir(parents=True)
            (root / 'zh/resources/ghidra/index.md').write_text('# Ghidra "x"\n\nbody\n')
            (root / 'downloads').mkdir()
            (root / 'downloads/index.md').write_text('# keep\n')
            self.assertEqual(add_front_matter(root, 'https://awesomerea.org', {'/resources/ghidra/': '2026-10-15T00:00:00Z'}, '2026-11-10'), 1)
            self.assertEqual((root / 'zh/resources/ghidra/index.md').read_text(),
                             '---\ntitle: "Ghidra \\"x\\""\nurl: https://awesomerea.org/zh/resources/ghidra/\nupdated: 2026-10-15\ntype: resource\n---\n\n# Ghidra "x"\n\nbody\n')
            self.assertEqual((root / 'downloads/index.md').read_text(), '# keep\n')
            self.assertEqual(add_front_matter(root, 'https://awesomerea.org', {}, '2026-11-10'), 0)


if __name__ == '__main__':
    unittest.main()


class SplitCatalogTest(unittest.TestCase):
    def test_parts_stay_under_the_limit_and_cut_at_headings(self):
        from agent_files import split_blocks, write_full_catalog
        text = '# T\n\n> s\n\n' + ''.join(f'#### Entry {n}\n\n' + 'x' * 100 + '\n' for n in range(50))
        parts = split_blocks(text, 1000)
        self.assertGreater(len(parts), 3)
        self.assertTrue(all(len(part.encode()) <= 1000 for part in parts))
        self.assertTrue(all(part.lstrip().startswith(('# T', '####')) for part in parts))
        with tempfile.TemporaryDirectory() as folder:
            urls = write_full_catalog(Path(folder), 'en', text, title='T', summary='s', faq='## FAQ\n', site_url='https://x.org')
            self.assertGreaterEqual(len(urls), 1)
            self.assertIn('/llms-full/part-1.txt', (Path(folder) / 'llms-full.txt').read_text())

    def test_paper_sections_are_not_cut_points(self):
        from agent_files import split_blocks
        papers = ''.join(f'### Paper {n}\n\n#### Scope\n\n' + 'x' * 100 + '\n\n#### BibTeX\n\n' + 'y' * 100 + '\n' for n in range(20))
        text = '# T\n\n## Curated resources (1)\n\n#### R\n\n' + 'z' * 50 + '\n## Research papers (20)\n\n' + papers
        for part in split_blocks(text, 700):
            self.assertFalse(part.lstrip().startswith('####'))
