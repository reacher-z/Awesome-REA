"""README paper lines show the venue and year once, with the first author, in their metadata."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_readme import PAPER_STATUSES, paper_venue, plain_text, render_papers


def paper(**changes):
    record = deepcopy(json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))[0])
    record.update(id='paper-venue-fixture', targets=['website'], code_url='https://example.com/code')
    record.update(changes)
    return record


def visible_line(rendered, record):
    """The metadata that follows the opening sentence on the paper's one README line."""
    line = next(line for line in rendered.splitlines() if line.startswith('- ') and f']({record["url"]}) - ' in line)
    return line.split(' <sub>', 1)[1].removesuffix('</sub>')


class ReadmePaperVenueTest(unittest.TestCase):
    def test_year_is_added_only_when_the_venue_lacks_it(self):
        self.assertEqual(paper_venue(paper(venue='ACM CCS 2022', year=2022)), 'ACM CCS 2022')
        self.assertEqual(paper_venue(paper(venue='arXiv', year=2026)), 'arXiv 2026')
        self.assertEqual(paper_venue(paper(venue='Formal Methods in System Design', year=2022)),
                         'Formal Methods in System Design 2022')
        # A workshop's two-digit edition number is not a year.
        self.assertEqual(paper_venue(paper(venue='USENIX Workshop (WOOT 18)', year=2018)),
                         'USENIX Workshop (WOOT 18) 2018')
        self.assertEqual(paper_venue(paper(venue='Proceedings 12018', year=2018)), 'Proceedings 12018 2018')

    def test_visible_line_shows_venue_status_and_year_once(self):
        for venue, year, status in [('NDSS 2023', 2023, 'conference-paper'), ('arXiv', 2026, 'preprint'),
                                    ('Formal Methods in System Design', 2022, 'journal-article')]:
            record = paper(venue=venue, year=year, publication_status=status)
            before = deepcopy(record)
            for language, index in (('en', 0), ('zh', 1)):
                with self.subTest(venue=venue, language=language):
                    rendered = render_papers([record], language)
                    line = visible_line(rendered, record)
                    author = record['authors'][0] + (' 等' if index else ' et al.')
                    self.assertTrue(line.startswith(f'{plain_text(paper_venue(record))} · '
                                                    f'{PAPER_STATUSES[status][index]} · {plain_text(author)} · [PDF]('), line)
                    self.assertEqual(len(re.findall(rf'(?<!\d){year}(?!\d)', line)), 1, line)
                    self.assertIn('](https://example.com/code)', line)
                    self.assertIn(f'papers/{record["id"]}/)', line)
                    self.assertNotIn('<details>', rendered)
            self.assertEqual(record, before)

    def test_generated_readmes_show_every_venue_on_the_paper_line(self):
        papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
        for name, index in (('README.md', 0), ('README.zh-CN.md', 1)):
            text = (ROOT / name).read_text(encoding='utf-8')
            for record in papers:
                with self.subTest(readme=name, paper=record['id']):
                    line = visible_line(text, record)
                    status = PAPER_STATUSES[record['publication_status']][index]
                    self.assertTrue(line.startswith(f'{plain_text(paper_venue(record))} · {status} · '), line)


if __name__ == '__main__':
    unittest.main()
