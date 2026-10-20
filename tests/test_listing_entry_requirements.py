"""/resources/ and /cases/ link each entry's requirements and sources on its entry page instead of inlining them."""
from html import escape
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_discovery_pages import _case_row, _resource_card, build_discovery_pages
from build_entry_pages import _resource_content


def record(identifier, kind='tool', additional=(), requirements=('Needs the original <input> & "rights".', 'Results are author-reported.')):
    return {'id': identifier, 'name': 'Example ' + identifier, 'name_zh': '示例 ' + identifier,
            'url': 'https://example.org/' + identifier, 'kind': kind,
            'category': 'reconstruction-cases' if kind == 'case-study' else 'game-analysis',
            'relationship': 'independent-reconstruction' if kind == 'case-study' else 'foundation', 'targets': ['game'],
            'description_en': 'Describes one reviewed fixture.', 'description_zh': '描述一个已复核的测试条目。',
            'requirements': list(requirements), 'requirements_zh': ['需要原始 <输入> 与 "权利"。', '结果来自作者报告。'][:len(requirements)],
            'evidence_url': 'https://example.org/evidence/' + identifier, 'additional_evidence_urls': list(additional),
            'verified_at': '2026-10-16T12:30:00Z', 'verification': 'source-reviewed'}


TOOL = record('fixture-tool', additional=['https://example.org/notes', 'https://example.org/evidence/fixture-tool'],
              requirements=('One requirement.',))
CASE = record('fixture-case', 'case-study', additional=['https://example.org/method', 'https://example.org/limits'])


class ListingEntryRequirementTests(unittest.TestCase):
    def rendered(self):
        for language in ('en', 'zh'):
            yield language, _resource_card(TOOL, language), TOOL
            yield language, _resource_card(CASE, language), CASE
            yield language, _case_row(CASE, language, 'game'), CASE

    def test_listings_drop_inline_requirements_and_additional_sources(self):
        for language, html, item in self.rendered():
            with self.subTest(language=language, html=html[:40]):
                self.assertNotIn('<details', html)
                for requirement in item['requirements_zh' if language == 'zh' else 'requirements']:
                    self.assertNotIn(escape(requirement), html)
                for url in item['additional_evidence_urls']:
                    if url != item['evidence_url']:
                        self.assertNotIn(url, html)
                for kept in (item['url'], item['evidence_url'], escape(item[f'description_{language}'])):
                    self.assertIn(kept, html)
                self.assertIn(f'datetime="{item["verified_at"]}"', html)
                self.assertIn(item['verified_at'][:10], html)

    def test_requirements_link_counts_what_the_entry_page_lists(self):
        expected = {('en', 'fixture-tool'): ('1 requirement · 2 sources', 'Example fixture-tool: 1 requirement and 2 sources on the full entry'),
                    ('en', 'fixture-case'): ('2 requirements · 3 sources', 'Example fixture-case: 2 requirements and 3 sources on the full entry'),
                    ('zh', 'fixture-tool'): ('1 项使用条件 · 2 个来源', '示例 fixture-tool：完整条目中的 1 项使用条件与 2 个来源'),
                    ('zh', 'fixture-case'): ('2 项使用条件 · 3 个来源', '示例 fixture-case：完整条目中的 2 项使用条件与 3 个来源')}
        for language, html, item in self.rendered():
            with self.subTest(language=language, id=item['id']):
                link = re.search(r'<a class="(?:resource|case)-requirements-link" href="([^"]+)" aria-label="([^"]+)">([^<]+)<span aria-hidden="true">&nbsp;→</span></a>', html)
                self.assertIsNotNone(link)
                self.assertEqual(link[1], f"{'/zh' if language == 'zh' else ''}/resources/{item['id']}/#entry-requirements")
                text, label = expected[language, item['id']]
                self.assertEqual((link[3], link[2]), (text, label))
                # The destination section exists and holds every requirement and every source the count describes.
                content = _resource_content(item, language)[2]
                self.assertIn('<h2 id="entry-requirements">', content)
                section = content.split('<h2 id="entry-requirements">', 1)[1].split('</section>', 1)[0]
                requirements = item['requirements_zh' if language == 'zh' else 'requirements']
                self.assertEqual(section.count('<li>'), len(requirements))
                for requirement in requirements:
                    self.assertIn(escape(requirement), section)
                sources = content.split('<ol class="entry-sources">', 1)[1].split('</ol>', 1)[0]
                self.assertEqual(sources.count('<li>'), int(re.search(r'(\d+) (?:source|个来源)', text)[1]))
                for url in (item['evidence_url'], *item['additional_evidence_urls']):
                    self.assertIn(url, sources)

    def test_built_listings_work_without_scripts_or_disclosures(self):
        with TemporaryDirectory() as directory:
            output = Path(directory)
            build_discovery_pages(output, {'meta': {}, 'resources': [TOOL, CASE]}, None)
            for route in ('resources', 'zh/resources', 'cases', 'zh/cases'):
                html = (output / route / 'index.html').read_text(encoding='utf-8')
                with self.subTest(route=route):
                    main = html.split('<main', 1)[1].split('</main>', 1)[0]
                    self.assertNotIn('<details class="requirements"', main)
                    self.assertNotIn('<details class="case-evidence"', main)
                    self.assertEqual(re.findall(r'<script(?![^>]*application/ld\+json)', html), [], 'no script is needed to reach requirements')
                    prefix = '/zh' if route.startswith('zh/') else ''
                    for item in ([TOOL, CASE] if route.endswith('resources') else [CASE]):
                        self.assertEqual(main.count(f'href="{prefix}/resources/{item["id"]}/#entry-requirements"'), 1)


if __name__ == '__main__':
    unittest.main()
