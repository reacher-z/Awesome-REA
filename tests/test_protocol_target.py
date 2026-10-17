"""Keep protocol support explicit and separate from existing target assignments."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
# Shared fixtures also resolve when this module runs on its own from the repository root.
sys.path.insert(1, str(ROOT / 'tests'))
import catalog
from build_readme import TARGETS, collection_section, render_catalog, render_papers
from build_site import TARGETS as BUILD_TARGETS, default_targets, fontawesome_markup
from build_paper_pages import TARGET_LABELS, build_paper_pages
from build_discovery_pages import build_discovery_pages
from source_browser import project_source_browser
from validate import public_https_error, validate_resources, validate_source_index
from validate_papers import TARGETS as PAPER_TARGETS, validate_papers
from validate_site import Page, validate_paper_groups


def paper(**changes):
    record = deepcopy(json.loads((ROOT / 'data/papers.json').read_text())[0])
    record.update(id='paper-protocol-fixture', targets=['protocol'])
    record.update(changes)
    return record


def resource(**changes):
    record = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text())[0])
    record.update(id='protocol-fixture', category='protocol-analysis', kind='tool',
                  relationship='foundation', targets=['protocol'])
    record.update(changes)
    return record


class ProtocolTargetTests(unittest.TestCase):
    def test_target_enums_and_schema_boundaries(self):
        self.assertEqual(set(TARGETS), BUILD_TARGETS)
        self.assertEqual(BUILD_TARGETS, PAPER_TARGETS)
        self.assertEqual(BUILD_TARGETS, set(TARGET_LABELS))
        for targets in (['protocol'], ['app', 'protocol']):
            curated = resource(targets=targets)
            research = paper(); research['targets'] = targets
            errors = []; validate_resources([curated], errors)
            validate_papers([research], errors, url_check=public_https_error)
            self.assertEqual(errors, [])
        for targets in (['protocol', 'protocol'], ['unsupported']):
            errors = []; validate_resources([resource(targets=targets)], errors)
            self.assertTrue(errors)
            research = paper(); research['targets'] = targets
            errors = []; validate_papers([research], errors, url_check=public_https_error)
            self.assertTrue(errors)

    def test_core_default_and_curated_section_precedence(self):
        self.assertEqual(default_targets({'category': 'core'}),
                         ['app', 'binary', 'firmware', 'game', 'website'])
        self.assertEqual(default_targets(resource()), ['protocol'])
        for record, expected in (
            (resource(), 'protocol'),
            (resource(kind='documentation'), 'references-and-learning'),
            (resource(kind='collection'), 'related-collections'),
            (resource(category='agent-mcp'), 'agents-and-mcp'),
            (resource(category='web-analysis', targets=['website', 'protocol']), 'website'),
            (resource(category='reconstruction-cases', kind='case-study'), 'protocol'),
            (resource(category='reconstruction-cases', kind='case-study', targets=['protocol', 'app']), 'app'),
            # Reviewed records whose category would otherwise route them to another section.
            (resource(id='humanify', category='javascript-electron', targets=['website']), 'website'),
            (resource(id='burp-suite-mcp-server', category='agent-mcp', kind='integration', targets=['website', 'app']), 'website'),
            (resource(id='apktool-mcp-server', category='agent-mcp', kind='integration', targets=['app']), 'app'),
            (resource(id='grapefruit', category='dynamic-analysis', targets=['app']), 'app'),
            # Community device cases follow their reviewed targets rather than an ID override.
            (resource(id='picoprint-rea-investigation', category='community-case-studies', kind='case-study',
                      relationship='community-reported-mixed-workflow', targets=['app', 'protocol']), 'app'),
        ):
            with self.subTest(record=record['category'], kind=record['kind']):
                self.assertEqual(collection_section(record), expected)

    def test_bilingual_primary_paper_group_and_agent_override(self):
        primary = paper()
        secondary = paper(); secondary.update(id='paper-app-fixture', targets=['app', 'protocol'])
        with tempfile.TemporaryDirectory() as directory:
            build_paper_pages(Path(directory), [primary, secondary])
            for language, route in [('en', 'papers'), ('zh', 'zh/papers')]:
                page = Page((Path(directory) / route / 'index.html').read_text())
                validate_paper_groups(page, [primary, secondary], language)
                groups = {group['anchor']: group['paper_ids'] for group in page.paper_groups}
                self.assertEqual(groups['research-protocol'], [primary['id']])
                self.assertEqual(groups['research-app'], [secondary['id']])
                self.assertEqual(page.paper_ids.count(primary['id']), 1)
                heading = TARGET_LABELS['protocol'][language == 'zh']
                self.assertIn('### ' + heading, render_papers([primary], language))
        agent = paper(); agent['id'] = 'paper-programbench'
        rendered = render_papers([agent], 'en')
        self.assertIn('### Reverse-engineering agent evaluation', rendered)
        self.assertNotIn('### Protocol inference and analysis', rendered)

    def test_static_curated_section_badges_and_existing_icon_modes(self):
        record = resource()
        record['requirements_zh'] = ['测试前置条件']
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build_discovery_pages(output, {'resources': [record], 'meta': {}}, None)
            for language, route, heading, badge in (
                ('en', 'resources', 'Protocols', 'Protocol'),
                ('zh', 'zh/resources', '协议', '协议'),
            ):
                html = (output / route / 'index.html').read_text()
                self.assertIn('id="heading-protocol"', html)
                self.assertIn(heading, html)
                self.assertIn(badge, html)
                self.assertEqual(html.count('data-resource-id="protocol-fixture"'), 1)
                self.assertIn('<a id="protocol"></a>', render_catalog([record], language))
        html = (ROOT / 'site/index.html').read_text()
        for attribute in ('data-target', 'data-source-target'):
            self.assertEqual(html.count(attribute + '="protocol"'), 1)
        self.assertGreaterEqual(html.count('data-i18n="targetProtocol"'), 2)
        converted = fontawesome_markup(html, 'https://assets.example.org/fontawesome.css')
        self.assertIn('fa-network', converted)
        self.assertNotIn('<use href="#i-network"', converted)

    def test_source_target_support_does_not_reclassify_or_rewrite_evidence(self):
        source = json.loads((ROOT / 'data/source-index.json').read_text())
        original = deepcopy(source)
        source['resources'][0]['targets'] = ['protocol']
        errors = []; validate_source_index(source, errors)
        self.assertEqual(errors, [])
        self.assertEqual({k: v for k, v in source['resources'][0].items() if k != 'targets'},
                         {k: v for k, v in original['resources'][0].items() if k != 'targets'})
        source['resources'][0]['targets'] = ['not-a-target']
        errors = []; validate_source_index(source, errors)
        self.assertTrue(any('target' in error for error in errors))
        # The projection retains target labels without inferring them from category.
        from test_source_browser import full_export, export_bytes
        fixture = full_export(); fixture['resources'][0]['targets'] = ['protocol']
        before = deepcopy(fixture)
        projected = project_source_browser(export_bytes(fixture))
        self.assertEqual(projected['resources'][0]['targets'], ['protocol'])
        self.assertEqual(fixture, before)

    def test_cli_protocol_filter_in_each_mode(self):
        records = [resource(), resource(id='other', targets=['app'])]
        for mode in ([], ['--papers'], ['--source-index']):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); (root / 'data').mkdir()
                (root / 'data/source-index.json').write_text(json.dumps({'resources': records}))
                stdout = io.StringIO()
                with patch.object(catalog, 'ROOT', root), patch.object(catalog, 'load_resources', return_value=records), patch.object(catalog, 'read_papers', return_value=records), patch.object(catalog, 'read_localizations', return_value={}), patch.object(catalog, 'read_scope', return_value={}), patch.object(catalog, 'localized_records', side_effect=lambda rows, _: rows), patch.object(catalog, 'apply_scope', side_effect=lambda rows, _: rows), patch.object(sys, 'argv', ['catalog.py', *mode, '--target', 'protocol', '--json']), redirect_stdout(stdout):
                    catalog.main()
                self.assertEqual([row['id'] for row in json.loads(stdout.getvalue())], ['protocol-fixture'])

    def test_browser_protocol_filters_query_restoration_and_locale_independent_order(self):
        reported = set()
        for locale in ('en_US.UTF-8', 'da_DK.UTF-8', 'zh_CN.UTF-8'):
            with self.subTest(locale=locale):
                result = subprocess.run(['node', str(ROOT / 'tests/protocol_target_ui.cjs')], cwd=ROOT,
                                        env={**os.environ, 'LC_ALL': locale}, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                reported.add(result.stdout.strip().rsplit(' ', 1)[-1])
        # Each run used a different default collation locale, so identical expected orders are meaningful.
        self.assertEqual(reported, {'en-US', 'da-DK', 'zh-CN'})


if __name__ == '__main__':
    unittest.main()
