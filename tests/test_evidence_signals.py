"""Download signals: target installs count, build dependencies and bare release tags do not."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from classify_evidence_classes import github_signals  # noqa: E402

FILLER = 'Documentation for the project. ' * 20
RECORD = {'id': 'foo', 'url': 'https://github.com/acme/foo', 'name': 'Foo', 'kind': 'tool'}


def meta(readme: str, release_count: int = 0, release_asset_count: int = 0) -> dict:
    return {'unavailable': False, 'readme_text': readme, 'readme_bytes': len(readme.encode()),
            'release_count': release_count, 'release_asset_count': release_asset_count,
            'archived': False, 'linked_docs_bytes': 0}


class DownloadSignalTests(unittest.TestCase):
    def test_fenced_install_command_for_the_target_counts(self):
        signals = github_signals(meta('```sh\nbrew install foo\n```\n' + FILLER), RECORD)
        self.assertEqual(signals['download'], 'package')

    def test_inline_build_dependency_does_not_count(self):
        signals = github_signals(meta('Run `pip install ninja` before building.\n' + FILLER), RECORD)
        self.assertIsNone(signals['download'])

    def test_scoped_and_go_install_commands_match_the_repository_name(self):
        self.assertEqual(github_signals(meta('npm install @scope/foo\n' + FILLER), RECORD)['download'], 'package')
        self.assertEqual(github_signals(meta('go install github.com/acme/foo@latest\n' + FILLER), RECORD)['download'], 'package')

    def test_release_tag_without_an_artifact_is_not_a_download(self):
        signals = github_signals(meta(FILLER, release_count=1, release_asset_count=0), RECORD)
        self.assertIsNone(signals['download'])
        self.assertEqual(signals['release_count'], 1)

    def test_release_with_assets_is_a_download(self):
        signals = github_signals(meta(FILLER, release_count=1, release_asset_count=2), RECORD)
        self.assertEqual(signals['download'], 'release-assets')

    def test_direct_artifact_link_is_a_download(self):
        signals = github_signals(meta('[Download](https://example.org/foo.dmg)\n' + FILLER), RECORD)
        self.assertEqual(signals['download'], 'file-links')


if __name__ == '__main__':
    unittest.main()
