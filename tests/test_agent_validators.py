"""The agent-format validators reject missing twins, stale records, oversized llms.txt and missing headers."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from agent_files import add_front_matter
from agent_formats import alternate_links, json_text, paper_markdown, paper_record, resource_markdown, resource_record
from test_agent_formats import PAPER, RESOURCE
from validate_agent_formats import TWIN_LISTINGS, validate_agent_headers, validate_llms, validate_twins
from validate_site import header_rules

ORIGIN = 'https://awesomerea.org'


def page(path, markdown, json_href=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'<!doctype html><html><head>{alternate_links(markdown=markdown, json_href=json_href)}</head><body></body></html>',
                    encoding='utf-8')


class TwinValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name)
        self.routes = set()
        for prefix in ('', '/zh'):
            language = 'zh' if prefix else 'en'
            for kind, record, render in (('resource', RESOURCE, resource_markdown), ('paper', PAPER, paper_markdown)):
                route = f"{prefix}/{kind}s/{record['id']}/"
                page(self.output / route.lstrip('/') / 'index.html', route + 'index.md', f"/{kind}s/{record['id']}/record.json")
                (self.output / route.lstrip('/') / 'index.md').write_text(render(record, language, site_url=ORIGIN), encoding='utf-8')
                self.routes.add(route)
            for listing in TWIN_LISTINGS:
                route = prefix + listing
                page(self.output / route.lstrip('/') / 'index.html', route + 'index.md')
                (self.output / route.lstrip('/') / 'index.md').write_text(f'# Listing\n\n- HTML: <{ORIGIN}{route}>\n', encoding='utf-8')
                self.routes.add(route)
        add_front_matter(self.output, ORIGIN, {}, '2026-11-10')
        (self.output / 'resources/ghidra/record.json').write_text(json_text(resource_record(RESOURCE, ORIGIN)), encoding='utf-8')
        (self.output / 'papers/paper-x/record.json').write_text(json_text(paper_record(PAPER, ORIGIN)), encoding='utf-8')

    def test_complete_twins_pass(self):
        validate_twins(self.output, self.routes, [RESOURCE], [PAPER])

    def test_a_stale_record_a_missing_link_or_an_orphan_twin_fails(self):
        record = self.output / 'resources/ghidra/record.json'
        original = record.read_text(encoding='utf-8')
        record.write_text(original.replace('Ghidra', 'Ghidra (renamed)', 1), encoding='utf-8')
        with self.assertRaisesRegex(AssertionError, 'record.json differs'):
            validate_twins(self.output, self.routes, [RESOURCE], [PAPER])
        record.write_text(original, encoding='utf-8')
        page(self.output / 'zh/papers/paper-x/index.html', '/zh/papers/paper-x/index.md')
        with self.assertRaisesRegex(AssertionError, 'JSON twin'):
            validate_twins(self.output, self.routes, [RESOURCE], [PAPER])
        page(self.output / 'zh/papers/paper-x/index.html', '/zh/papers/paper-x/index.md', '/papers/paper-x/record.json')
        orphan = self.output / 'resources/retired/index.md'
        orphan.parent.mkdir(parents=True)
        orphan.write_text('# Retired\n', encoding='utf-8')
        with self.assertRaisesRegex(AssertionError, 'without an indexed page'):
            validate_twins(self.output, self.routes, [RESOURCE], [PAPER])


class LlmsValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name)
        (self.output / 'resources').mkdir()
        (self.output / 'resources/index.md').write_text('# Resources\n', encoding='utf-8')
        (self.output / 'zh').mkdir()
        self.index = (f'# Awesome REA\n\n> Summary.\n\n## Collections\n\n- [Resources]({ORIGIN}/resources/index.md): All.\n\n'
                      f'## Optional\n\n- [Full]({ORIGIN}/llms-full.txt): Everything.\n')
        (self.output / 'llms.txt').write_text(self.index, encoding='utf-8')
        for name, prefix in (('llms-full.txt', ''), ('zh/llms-full.txt', '/zh')):
            (self.output / (prefix.lstrip('/') or '.') / 'llms-full').mkdir(parents=True)
            (self.output / (prefix.lstrip('/') or '.') / 'llms-full/part-1.txt').write_text(
                f'# Full: part 1 of 1\n\n- <{ORIGIN}{prefix}/resources/ghidra/>\n- <{ORIGIN}{prefix}/papers/paper-x/>\n', encoding='utf-8')
            (self.output / name).write_text(f'# Full\n\n- [part 1]({ORIGIN}{prefix}/llms-full/part-1.txt): x\n', encoding='utf-8')

    def test_valid_files_pass_and_each_rule_fails(self):
        validate_llms(self.output, [RESOURCE], [PAPER])
        for broken, message in ((self.index.replace('## Optional', '## Extra'), 'Optional'),
                                (self.index.replace('> Summary.', 'Summary.'), 'blockquote'),
                                (self.index.replace('/resources/index.md', '/missing/index.md'), 'missing file'),
                                (self.index + '- x\n' * 30_000, 'exceeds')):
            (self.output / 'llms.txt').write_text(broken, encoding='utf-8')
            with self.assertRaisesRegex(AssertionError, message):
                validate_llms(self.output, [RESOURCE], [PAPER])
        (self.output / 'llms.txt').write_text(self.index, encoding='utf-8')
        (self.output / 'zh/llms-full/part-1.txt').write_text('# Full\n', encoding='utf-8')
        with self.assertRaisesRegex(AssertionError, 'lacks entries'):
            validate_llms(self.output, [RESOURCE], [PAPER])


class HeaderValidatorTests(unittest.TestCase):
    def test_site_headers_serve_the_agent_formats(self):
        text = (ROOT / 'site/_headers').read_text(encoding='utf-8')
        validate_agent_headers(header_rules(text))
        with self.assertRaisesRegex(AssertionError, '/api/'):
            validate_agent_headers(header_rules(text.replace('/api/*\n  Access-Control-Allow-Origin: *\n', '/api/*\n')))
        with self.assertRaisesRegex(AssertionError, 'index.md'):
            validate_agent_headers(header_rules(text.replace(':splat/>', ':splat>')))
        # Cloudflare Pages allows 100 rules.
        self.assertLessEqual(len(header_rules(text)), 100)


if __name__ == '__main__':
    unittest.main()
