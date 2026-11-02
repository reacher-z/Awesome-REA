"""Download signals: target installs count, build dependencies and bare release tags do not."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from classify_evidence_classes import (  # noqa: E402
    artifact_basename_matches_target, collect_target_download_links, github_signals, is_c0_candidate)

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

    def test_prefixed_package_and_flags_match_the_target(self):
        record = {'id': 'rea', 'url': 'https://github.com/morluto/rea', 'name': 'REA', 'kind': 'project'}
        for readme in ('npx rea-agents setup\n', 'npm install --global rea-agents\n',
                       'npx -y rea-agents@latest analyze-javascript-application /tmp/app\n'):
            signals = github_signals(meta(readme + FILLER), record)
            self.assertEqual(signals['download'], 'package', readme)

    def test_get_started_heading_counts_as_install_and_usage(self):
        signals = github_signals(meta('## Get started\nInstall the release package and open the app.\n' + FILLER), RECORD)
        self.assertTrue(signals['docs_full'])

    def test_release_asset_links_on_a_linked_page_are_collected(self):
        payload = meta(FILLER)
        payload['download_links'] = ['https://example.org/releases/download/v1/foo-1.0-macos.dmg']
        signals = github_signals(payload, RECORD)
        self.assertEqual(signals['download'], 'artifact-links')
        self.assertEqual(signals['download_links'], ['https://example.org/releases/download/v1/foo-1.0-macos.dmg'])

    def test_release_assets_stay_the_basis_when_links_are_also_collected(self):
        payload = meta(FILLER, release_count=1, release_asset_count=2)
        payload['download_links'] = ['https://example.org/apps/foo']
        signals = github_signals(payload, RECORD)
        self.assertEqual(signals['download'], 'release-assets')
        self.assertEqual(signals['download_links'], ['https://example.org/apps/foo'])


class CollectedDownloadLinkTests(unittest.TestCase):
    TARGET = 'cadcraft'

    def test_release_asset_direct_link_named_after_the_target_counts(self):
        links = collect_target_download_links(
            '', [('https://github.com/storytold/cadcraft/releases/download/v0.15.1/'
                  'cadcraft-0.15.1-macos-universal.dmg', '')], self.TARGET)
        self.assertEqual(len(links), 1)

    def test_artifact_with_a_different_name_does_not_count(self):
        links = collect_target_download_links(
            '', [('https://example.org/downloads/launcher-1.0.dmg', ''),
                 ('https://github.com/storytold/other/releases/download/v1/other-1.0.msi', '')], self.TARGET)
        self.assertEqual(links, [])

    def test_bare_page_link_is_not_a_download(self):
        links = collect_target_download_links('', [('https://getartcraft.com/apps/cadcraft', '')], self.TARGET)
        self.assertEqual(links, [])

    def test_install_command_for_the_target_is_collected(self):
        links = collect_target_download_links('cargo install cadcraft-cli\n', [], self.TARGET)
        self.assertEqual(links, ['cargo install cadcraft-cli'])

    def test_url_tail_equal_to_the_target_is_a_match(self):
        self.assertTrue(artifact_basename_matches_target('cadcraft', self.TARGET))
        self.assertTrue(artifact_basename_matches_target('cadcraft-0.15.1-macos.dmg', self.TARGET))
        self.assertFalse(artifact_basename_matches_target('photocraft', self.TARGET))

    def test_html_readme_links_feed_the_collector(self):
        readme = ('<h2>Downloads</h2>\n<a href="https://github.com/storytold/cadcraft/releases/download/v0.15.1/'
                  'cadcraft-0.15.1-macos-universal.dmg"><svg>icon</svg> Download</a>\n' + FILLER)
        signals = github_signals(meta(readme), {'id': 'cadcraft', 'url': 'https://github.com/storytold/cadcraft',
                                                'name': 'CADCraft', 'kind': 'tool'})
        # A direct file link inside the README already counts as file-links; the
        # collector additionally records the concrete link for audit.
        self.assertEqual(signals['download'], 'file-links')
        self.assertEqual(len(signals['download_links']), 1)


class ClassZeroCandidateTests(unittest.TestCase):
    def test_clean_room_implementation_is_a_complete_description(self):
        record = {'id': 'wordcraft', 'url': 'https://github.com/storytold/wordcraft',
                  'kind': 'case-study', 'targets': ['app'],
                  'description_en': 'A clean-room Rust implementation of familiar Word workflows.'}
        signals = {'code': True, 'docs': True, 'docs_full': True, 'download': 'release-assets', 'demo': ['image']}
        self.assertTrue(is_c0_candidate(record, signals))


if __name__ == '__main__':
    unittest.main()
