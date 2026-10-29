"""Both READMEs offer contribution entry points early, and the Chinese one leads to the Chinese guide."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import CONTENTS_BEGIN, CONTENTS_END, render_contents

RESOURCE_FORM = 'https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml'


class ReadmeContributionLinkTest(unittest.TestCase):
    def test_first_screen_links_the_resource_form_and_contributing_section(self):
        for name, contents_heading, anchor in (('README.md', '## Contents', '#contributing'),
                                               ('README.zh-CN.md', '## 目录', '#参与贡献')):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                first_screen = text.split('\n' + contents_heading + '\n', 1)[0]
                self.assertIn(f']({RESOURCE_FORM})', first_screen)
                self.assertIn(f']({anchor})', first_screen)
                heading = anchor[1:] if name.endswith('zh-CN.md') else 'Contributing'
                self.assertIn(f'\n## {heading}\n', text)

    def test_generated_contents_link_the_contributing_section(self):
        self.assertTrue(render_contents([], [], 0, 'en').rstrip().endswith('· [Contributing](#contributing)'))
        self.assertTrue(render_contents([], [], 0, 'zh').rstrip().endswith('· [参与贡献](#参与贡献)'))
        for name, link in (('README.md', '[Contributing](#contributing)'), ('README.zh-CN.md', '[参与贡献](#参与贡献)')):
            text = (ROOT / name).read_text(encoding='utf-8')
            self.assertIn(link, text.split(CONTENTS_BEGIN, 1)[1].split(CONTENTS_END, 1)[0])

    def test_chinese_readme_prefers_the_chinese_guide_and_labels_the_english_one(self):
        zh = (ROOT / 'README.zh-CN.md').read_text(encoding='utf-8')
        self.assertIn('](CONTRIBUTING.zh-CN.md)', zh)
        for label in re.findall(r'\[([^\]]+)\]\(CONTRIBUTING\.md\)', zh):
            self.assertIn('英文', label)
        self.assertIn('](CONTRIBUTING.md)', (ROOT / 'README.md').read_text(encoding='utf-8'))
        self.assertNotIn('](CONTRIBUTING.zh-CN.md)', (ROOT / 'README.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
