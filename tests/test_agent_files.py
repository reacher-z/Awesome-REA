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
