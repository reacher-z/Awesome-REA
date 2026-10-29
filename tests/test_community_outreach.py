"""The outreach checklist cites dated official rules, rules out manipulation and keeps tracking public-only."""
import datetime as dt
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'docs/community-outreach.md'
RULES = ('https://news.ycombinator.com/newsguidelines.html', 'https://news.ycombinator.com/showhn.html',
         'https://redditinc.com/policies/reddit-rules')


class CommunityOutreachTests(unittest.TestCase):
    def setUp(self):
        self.text = GUIDE.read_text(encoding='utf-8')

    def section(self, heading):
        return self.text.split(f'\n## {heading}\n', 1)[1].split('\n## ', 1)[0]

    def test_official_rules_are_linked_with_a_review_date_and_no_promise(self):
        for url in RULES:
            self.assertIn(f']({url})', self.text)
        reviewed = re.match(r'# Community outreach\n\nPlatform rules reviewed on (\d{4}-\d{2}-\d{2}) \(UTC\)\.', self.text)
        self.assertIsNotNone(reviewed)
        self.assertLessEqual(dt.date.fromisoformat(reviewed[1]), dt.datetime.now(dt.timezone.utc).date() + dt.timedelta(days=1))
        self.assertIn('does not guarantee that a post is accepted, ranked or kept', self.text)
        # Both documentation indexes show the same review date.
        self.assertIn(f'[Community outreach](community-outreach.md) | English | Current, rules reviewed {reviewed[1]}',
                      (ROOT / 'docs/README.md').read_text(encoding='utf-8'))
        self.assertIn(f'平台规则复核于 {reviewed[1]}', (ROOT / 'docs/README.zh-CN.md').read_text(encoding='utf-8'))

    def test_the_checklist_excludes_manipulation_and_undisclosed_promotion(self):
        checklist = self.section('Before posting')
        for phrase in ('Do not invent or inflate traction', 'Never ask anyone to upvote', 'No coordinated voting',
                       'post the same text to several communities', 'Say that you maintain or contribute',
                       'Never present your own promotion as an independent recommendation', 'Post by hand'):
            self.assertIn(phrase, checklist)
        self.assertIn('it is not a Show HN', self.text)
        self.assertIn('not a task for automation or agents', self.section('Hacker News handoff'))

    def test_tracking_keeps_only_public_post_urls_and_outcomes(self):
        tracking = self.section('Public tracking')
        self.assertIn('the URL of the post you intentionally made public', tracking)
        for excluded in ('logins', 'session cookies', 'tokens', 'private messages', 'moderator mail'):
            self.assertIn(excluded, tracking)

    def test_no_script_posts_to_community_sites(self):
        for path in (ROOT / 'scripts').glob('*.py'):
            source = path.read_text(encoding='utf-8')
            self.assertNotRegex(source, r'news\.ycombinator\.com|reddit\.com/api|oauth\.reddit\.com', path.name)


if __name__ == '__main__':
    unittest.main()
