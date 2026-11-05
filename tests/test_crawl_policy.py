"""robots.txt names every crawler it welcomes, allows all of them and declares the sitemap index."""
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.robotparser import RobotFileParser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from crawl_policy import (CONTENT_SIGNAL, CRAWLER_GROUPS, CRAWLERS, REQUIRED_AI_CRAWLERS, TRAINING_PREFERENCE_TOKEN,
                          robots_txt)
from validate_discovery import validate_robots

ORIGIN = 'https://awesomerea.org'
URLS = [ORIGIN + path for path in ('/', '/resources/ghidra/', '/zh/papers/', '/llms.txt', '/api/v1/resources.json')]


class CrawlPolicyTests(unittest.TestCase):
    def setUp(self):
        self.text = robots_txt(ORIGIN, ORIGIN + '/sitemap.xml')
        self.parser = RobotFileParser()
        self.parser.parse(self.text.splitlines())

    def test_every_named_and_unnamed_crawler_may_fetch_every_page(self):
        for agent in (*CRAWLERS, TRAINING_PREFERENCE_TOKEN, 'SomeNewBot/2.0', 'Mozilla/5.0'):
            for url in URLS:
                self.assertTrue(self.parser.can_fetch(agent, url), (agent, url))
        self.assertNotRegex(self.text, r'(?im)^\s*disallow\s*:')

    def test_the_goal_crawlers_are_named_explicitly(self):
        named = re.findall(r'(?m)^User-agent: (\S+)$', self.text)
        self.assertLessEqual(set(REQUIRED_AI_CRAWLERS), set(CRAWLERS))
        for token in REQUIRED_AI_CRAWLERS:
            self.assertIn(token, named)
        self.assertEqual(len(CRAWLERS), len(set(CRAWLERS)))
        self.assertEqual(named[0], '*')
        self.assertEqual(named[-1], TRAINING_PREFERENCE_TOKEN)

    def test_tokens_follow_the_rfc_9309_grammar(self):
        for _, tokens in CRAWLER_GROUPS:
            for token in tokens:
                self.assertRegex(token, r'^[A-Za-z_-]+$')
        with self.assertRaises(ValueError):
            import crawl_policy
            original = crawl_policy.CRAWLERS
            try:
                crawl_policy.CRAWLERS = (*original, '360Spider')
                crawl_policy.robots_txt(ORIGIN, ORIGIN + '/sitemap.xml')
            finally:
                crawl_policy.CRAWLERS = original

    def test_groups_repeat_the_allow_rules_and_declare_the_sitemap_index(self):
        # A named group replaces *, so both groups carry the same rules (RFC 9309 2.2.1).
        self.assertEqual(self.text.count(f'Content-Signal: {CONTENT_SIGNAL}'), 2)
        self.assertEqual(self.parser.site_maps(), [ORIGIN + '/sitemap.xml'])
        self.assertTrue(self.text.endswith('Sitemap: https://awesomerea.org/sitemap.xml\n'))
        self.assertIn(f'# Agent-readable index: {ORIGIN}/llms.txt', self.text)

    def test_validator_rejects_a_disallow_a_missing_crawler_or_another_sitemap(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'robots.txt').write_text(self.text, encoding='utf-8')
            validate_robots(output, URLS)
            for broken in (self.text + 'User-agent: GPTBot\nDisallow: /\n',
                           self.text.replace('User-agent: ClaudeBot\n', ''),
                           self.text.replace('/sitemap.xml', '/sitemap-pages.xml'),
                           self.text.replace(f'Content-Signal: {CONTENT_SIGNAL}\n', '', 1)):
                (output / 'robots.txt').write_text(broken, encoding='utf-8')
                with self.assertRaises(AssertionError):
                    validate_robots(output, URLS)


if __name__ == '__main__':
    unittest.main()
