"""Run the hidden-field match hint checks through the actual homepage script in the offline VM."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MatchContextTests(unittest.TestCase):
    def check_group(self, group):
        result = subprocess.run(['node', str(ROOT / 'tests/match_context_ui.cjs'), group],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Match context passed: ' + group, result.stdout)

    def test_alternate_language_matches_name_their_field(self):
        self.check_group('alternateLanguageMatches')

    def test_requirement_matches_and_visible_text(self):
        self.check_group('requirementsAndVisibleText')

    def test_unicode_and_markup_stay_text(self):
        self.check_group('unicodeAndMarkupStayText')

    def test_repository_cards_quote_real_fields(self):
        self.check_group('repositoryCardsQuoteRealFields')


if __name__ == '__main__':
    unittest.main()
