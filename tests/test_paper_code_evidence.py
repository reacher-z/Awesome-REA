"""Papers whose code lives on GitHub cite that repository at the reviewed commit, while code_url keeps moving."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

# Pinned together; each cited only the moving repository root before.
PINNED = ('paper-llm4decompile', 'paper-decompilebench', 'paper-dire', 'paper-dirty', 'paper-resym',
          'paper-crebench', 'paper-design2code', 'paper-interaction2code', 'paper-iwr-bench',
          'paper-dashboard2code', 'paper-remaui', 'paper-revengebench')


class PaperCodeEvidenceTests(unittest.TestCase):
    def test_pinned_papers_cite_their_repository_readme_at_a_commit(self):
        papers = {paper['id']: paper for paper in json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))}
        for identifier in PINNED:
            with self.subTest(identifier=identifier):
                paper = papers[identifier]
                repository = paper['code_url']
                self.assertRegex(repository, r'^https://github\.com/[^/]+/[^/]+$')
                pinned = [url for url in paper['evidence_urls']
                          if re.fullmatch(re.escape(repository) + r'/blob/[0-9a-f]{40}/README\.md', url)]
                self.assertEqual(len(pinned), 1, paper['evidence_urls'])
                # The moving root stays beside the pinned file.
                self.assertIn(repository, paper['evidence_urls'])


if __name__ == '__main__':
    unittest.main()
