"""Both READMEs offer contribution entry points early, and the Chinese one leads to the Chinese guide."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

RESOURCE_FORM = 'https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml'


class ReadmeContributionLinkTest(unittest.TestCase):
    def test_first_screen_links_the_resource_form_and_contributing_section(self):
        for name, contents_heading, anchor in (('README.md', '## Contents', '#contributing'),
                                               ('README.zh-CN.md', '## 目录', '#参与贡献')):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                first_screen = text.split('\n' + contents_heading + '\n', 1)[0]
                self.assertIn(f']({anchor})', first_screen)
                heading = anchor[1:] if name.endswith('zh-CN.md') else 'Contributing'
                self.assertIn(f'\n## {heading}\n', text)

    def test_contributing_section_links_the_resource_form(self):
        # The form is linked once, from the Contributing section: awesome-lint flags a URL repeated in one README.
        for name in ('README.md', 'README.zh-CN.md'):
            text = (ROOT / name).read_text(encoding='utf-8')
            self.assertEqual(text.count(f']({RESOURCE_FORM})'), 1)

    def test_chinese_readme_prefers_the_chinese_guide_and_labels_the_english_one(self):
        zh = (ROOT / 'README.zh-CN.md').read_text(encoding='utf-8')
        self.assertIn('](CONTRIBUTING.zh-CN.md)', zh)
        for label in re.findall(r'\[([^\]]+)\]\(CONTRIBUTING\.md\)', zh):
            self.assertIn('英文', label)
        self.assertIn('](CONTRIBUTING.md)', (ROOT / 'README.md').read_text(encoding='utf-8'))
        self.assertNotIn('](CONTRIBUTING.zh-CN.md)', (ROOT / 'README.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
