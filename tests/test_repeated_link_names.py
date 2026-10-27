"""Repeated README, PDF, Code, Project and BibTeX links are named after their repository or paper."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_browse_pages import repository_card
from build_paper_pages import paper_card
from validate_site import LinkNames, validate_unique_link_names

RECORD = {'id': 'scan-1', 'full_name': 'ReFirmLabs/binwalk', 'name': 'binwalk', 'url': 'https://github.com/ReFirmLabs/binwalk',
          'readme_url': 'https://github.com/ReFirmLabs/binwalk/blob/master/README.md',
          'description_en': 'Firmware Analysis Tool', 'description_zh': '固件分析工具。', 'stars': 1, 'license': 'MIT'}


def paper():
    record = deepcopy(next(row for row in json.loads((ROOT / 'data/papers.json').read_text()) if row['id'] == 'paper-fuzzware'))
    record.update(code_url='https://github.com/fuzzware-fuzzer/fuzzware', project_url='https://fuzzware.example.org/')
    return record


def links(html):
    return {link['text']: link for link in LinkNames(html).links}


class RepeatedLinkNameTests(unittest.TestCase):
    def test_readme_links_name_their_repository(self):
        for language, name in (('en', 'README: ReFirmLabs/binwalk'), ('zh', 'README：ReFirmLabs/binwalk')):
            link = links(repository_card(RECORD, language, False))['README']
            self.assertEqual(link['name'], name)
            self.assertEqual(link['href'], RECORD['readme_url'])
            self.assertTrue(link['name'].startswith(link['text']))

    def test_paper_row_links_name_their_paper_in_the_page_language(self):
        record = paper()
        for language, title, visible in (('en', record['title'], ('PDF', 'Code', 'Project', 'BibTeX')),
                                          ('zh', record['title_zh'], ('PDF', '代码', '项目', 'BibTeX'))):
            found = links(paper_card(record, language, False))
            separator = '：' if language == 'zh' else ': '
            for text in visible:
                self.assertEqual(found[text]['name'], text + separator + title)
                self.assertTrue(found[text]['name'].startswith(found[text]['text']))
            self.assertEqual(found['BibTeX']['href'], f"/papers/citations/{record['id']}.bib")

    def test_listing_check_rejects_one_name_for_different_destinations(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / 'browse' / 'firmware' / 'index.html'
            page.parent.mkdir(parents=True)
            same = '<a href="/a">Docs</a><a href="/a">Docs</a><a href="/b" aria-label="Docs: b">Docs <span aria-hidden="true">↗</span></a>'
            page.write_text(same)
            validate_unique_link_names(root)
            page.write_text(same + '<a href="/c">Docs: <span>b</span></a>')
            with self.assertRaisesRegex(AssertionError, r'/browse/firmware/: Docs: b'):
                validate_unique_link_names(root)

    def test_hidden_symbols_are_not_part_of_the_visible_name(self):
        parsed = LinkNames('<a href="/x">README <span aria-hidden="true">↗<b>!</b></span><img alt=""> tail</a>').links
        self.assertEqual(parsed, [{'href': '/x', 'text': 'README tail', 'name': 'README tail'}])


if __name__ == '__main__':
    unittest.main()
