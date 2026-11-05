"""The GitHub Pages mirror publishes the same production build that Cloudflare Pages serves."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/pages-mirror.yml'
CATALOG_CHECKS = ROOT / '.github/workflows/validate.yml'


def block(text, header):
    """The lines below `header:` (given with its leading spaces) that are indented further than it."""
    name = header.lstrip(' ')
    indent = len(header) - len(name)
    pattern = '^' + ' ' * indent + re.escape(name) + ':\n((?:(?:' + ' ' * (indent + 1) + '.*)?\n)+)'
    match = re.search(pattern, text, re.MULTILINE)
    return match[1] if match else ''


def toolchain(job):
    return re.findall(r"^ +((?:python|node)-version): '([^']+)'$", job, re.MULTILINE)


class GitHubPagesMirrorWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding='utf-8')
        self.build = block(self.text, '  build')
        self.deploy = block(self.text, '  deploy')

    def test_runs_the_cloudflare_production_build(self):
        production = block(CATALOG_CHECKS.read_text(encoding='utf-8'), '  production')
        command = re.findall(r'^ +run: (python3 scripts/build_production\.py\b.*)$', production, re.MULTILINE)
        self.assertEqual(len(command), 1, 'the production job runs one production build command')
        self.assertEqual(re.findall(r'^ +run: (python3 scripts/build_production\.py\b.*)$', self.build, re.MULTILINE), command)
        self.assertEqual(toolchain(self.build), toolchain(production))
        self.assertEqual(len(toolchain(self.build)), 2)
        steps = self.build.split('\n      - ')
        build_step = next(i for i, step in enumerate(steps) if command[0] in step)
        remove_step = next(i for i, step in enumerate(steps)
                           if re.search(r'(?m)^ +run: rm -f dist/_headers dist/_redirects$', step))
        upload_step = next(i for i, step in enumerate(steps) if 'actions/upload-pages-artifact@' in step)
        self.assertLess(build_step, remove_step)
        self.assertLess(remove_step, upload_step)
        self.assertIn('          path: dist\n', steps[upload_step])

    def test_publishes_only_main_with_least_privilege(self):
        self.assertEqual(block(self.text, 'on'), '  push:\n    branches: [main]\n  workflow_dispatch:\n')
        self.assertEqual(block(self.text, 'permissions'), '  contents: read\n')
        self.assertIn("    if: ${{ !github.event.repository.fork && github.ref == format('refs/heads/{0}', "
                      "github.event.repository.default_branch) }}\n", self.build)
        self.assertNotIn('permissions:', self.build)
        self.assertIn('          persist-credentials: false\n', self.build)
        self.assertIn('    needs: build\n', self.deploy)
        deploy_permissions = block(self.deploy, '    permissions')
        self.assertEqual(deploy_permissions, '      pages: write\n      id-token: write\n')
        self.assertNotRegex(self.text.replace(deploy_permissions, ''), r':\s*write\b')
        self.assertIn('      name: github-pages\n', block(self.deploy, '    environment'))
        self.assertEqual(block(self.text, 'concurrency'), '  group: github-pages\n  cancel-in-progress: false\n')
        self.assertNotIn('secrets.', self.text)
        for job in (self.build, self.deploy):
            self.assertRegex(job, r'(?m)^    timeout-minutes: \d+$')

    def test_actions_are_pinned_to_release_commits(self):
        actions = re.findall(r'uses: (\S+)(.*)', self.text)
        self.assertEqual({name.split('@')[0] for name, _ in actions},
                         {'actions/checkout', 'actions/setup-python', 'actions/setup-node',
                          'actions/upload-pages-artifact', 'actions/deploy-pages'})
        for name, comment in actions:
            self.assertRegex(name, r'@[0-9a-f]{40}$')
            self.assertRegex(comment, r'^ # v\d+\.\d+\.\d+$')


if __name__ == '__main__':
    unittest.main()
