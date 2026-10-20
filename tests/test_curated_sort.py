"""Run the curated Sort control checks through the actual homepage script in the offline VM."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CuratedSortTests(unittest.TestCase):
    def check_group(self, group):
        result = subprocess.run(['node', str(ROOT / 'tests/curated_sort_ui.cjs'), group],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Curated sort passed: ' + group, result.stdout)

    def test_default_order_is_unchanged(self):
        self.check_group('defaultOrderIsUnchanged')

    def test_name_order_follows_the_active_language(self):
        self.check_group('nameOrderFollowsTheActiveLanguage')

    def test_review_order_is_newest_displayed_date_first(self):
        self.check_group('reviewOrderIsNewestDisplayedDateFirst')

    def test_control_round_trips_through_the_url(self):
        self.check_group('controlRoundTripsThroughTheURL')

    def test_show_more_continues_the_chosen_order(self):
        self.check_group('showMoreContinuesTheChosenOrder')

    def test_both_homepages_offer_the_localized_control(self):
        html = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        self.assertIn('<label for="curated-sort" data-i18n="curatedSortLabel">Sort</label>', html)
        for value, key in (('featured', 'curatedSortFeatured'), ('name', 'curatedSortName'), ('reviewed', 'curatedSortReviewed')):
            self.assertIn(f'<option value="{value}" data-i18n="{key}">', html)


if __name__ == '__main__':
    unittest.main()
