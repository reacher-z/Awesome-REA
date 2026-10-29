"""Reject paper grouping errors that total bibliography coverage cannot catch."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_site import Page, validate_paper_groups


PAPERS = [
    {'id': 'paper-gamereplica', 'targets': ['game', 'website'], 'year': 2026, 'publication_date': None, 'title': 'Game replica'},
    {'id': 'paper-sprite-game-ui', 'targets': ['game'], 'year': 2025, 'publication_date': None, 'title': 'Sprite'},
    {'id': 'paper-remaui', 'targets': ['app'], 'year': 2015, 'publication_date': None, 'title': 'Remaui'},
    {'id': 'paper-web-example', 'targets': ['website'], 'year': 2024, 'publication_date': None, 'title': 'Web example'},
]
LABELS = {
    'game': ('Game reconstruction and reverse engineering', '游戏重建与逆向工程'),
    'app': ('App reconstruction and analysis', '应用重建与分析'),
    'website': ('Website reconstruction', '网站重建'),
}
# Sections use the README's paper topic keys.
TOPICS = {'game': 'game-reconstruction', 'app': 'app-reconstruction', 'website': 'website-reconstruction'}


def section(target, identifiers, language='en', count=None, label=None):
    label = label or LABELS[target][language == 'zh']
    count = len(identifiers) if count is None else count
    count_text = f'{count} ' + ('篇论文' if language == 'zh' else ('paper' if count == 1 else 'papers'))
    cards = ''.join(f'<article id="{identifier}" data-paper-id="{identifier}"><h3>Paper</h3><p>Text</p></article>' for identifier in identifiers)
    return (f'<section class="paper-section" aria-labelledby="research-{TOPICS[target]}">'
            f'<div class="paper-section-heading"><h2 id="research-{TOPICS[target]}">{label}</h2>'
            f'<span>{count_text}</span></div><div class="paper-grid">{cards}</div></section>')


def correct_document(language='en'):
    return (section('game', ['paper-gamereplica', 'paper-sprite-game-ui'], language)
            + section('app', ['paper-remaui'], language)
            + section('website', ['paper-web-example'], language))


class PaperGroupTests(unittest.TestCase):
    def test_bilingual_primary_target_sections_accept_multitarget_once(self):
        for language in ('en', 'zh'):
            page = Page(correct_document(language))
            validate_paper_groups(page, PAPERS, language)
            self.assertEqual(page.paper_ids.count('paper-gamereplica'), 1)

    def test_secondary_target_misgrouping_fails_despite_total_coverage(self):
        wrong = (section('game', ['paper-sprite-game-ui'])
                 + section('app', ['paper-remaui'])
                 + section('website', ['paper-web-example', 'paper-gamereplica']))
        page = Page(wrong)
        self.assertEqual(set(page.paper_ids), {paper['id'] for paper in PAPERS})
        with self.assertRaisesRegex(AssertionError, 'primary-target grouping'):
            validate_paper_groups(page, PAPERS, 'en')

    def test_duplicate_secondary_target_appearance_fails(self):
        wrong = correct_document().replace(
            section('website', ['paper-web-example']),
            section('website', ['paper-web-example', 'paper-gamereplica']))
        with self.assertRaisesRegex(AssertionError, 'primary-target grouping'):
            validate_paper_groups(Page(wrong), PAPERS, 'en')

    def test_reversed_dates_fail_despite_correct_section_membership(self):
        original = section('game', ['paper-gamereplica', 'paper-sprite-game-ui'])
        reversed_order = section('game', ['paper-sprite-game-ui', 'paper-gamereplica'])
        with self.assertRaisesRegex(AssertionError, 'newest-first ordering'):
            validate_paper_groups(Page(correct_document().replace(original, reversed_order)), PAPERS, 'en')

    def test_incorrect_count_and_untranslated_heading_fail(self):
        for language in ('en', 'zh'):
            original = section('app', ['paper-remaui'], language)
            for replacement, message in (
                (section('app', ['paper-remaui'], language, count=2), 'section count'),
                (section('app', ['paper-remaui'], language, label='Wrong heading'), 'section label'),
            ):
                with self.subTest(language=language, message=message):
                    page = Page(correct_document(language).replace(original, replacement))
                    with self.assertRaisesRegex(AssertionError, message):
                        validate_paper_groups(page, PAPERS, language)

    def test_missing_duplicate_and_misbound_sections_fail(self):
        original = correct_document()
        cases = [
            original.replace(section('app', ['paper-remaui']), ''),
            original + section('app', ['paper-remaui']),
            original.replace('id="research-app-reconstruction"', 'id="research-wrong"'),
        ]
        for document in cases:
            with self.subTest(document=document):
                with self.assertRaises(AssertionError):
                    validate_paper_groups(Page(document), PAPERS, 'en')


if __name__ == '__main__':
    unittest.main()
