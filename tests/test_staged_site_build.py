"""A rebuilt deployment replaces old output without sacrificing the last good build."""
from contextlib import ExitStack
import json
from pathlib import Path
import re
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_site
from build_manifest import read_build_manifest

try:
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTFont, woff2
    HAVE_FONT_TOOLS = woff2.haveBrotli
except ImportError:
    HAVE_FONT_TOOLS = False


def file_bytes(directory):
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in directory.rglob('*') if path.is_file()}


def synthetic_font(path, codepoints):
    """Write a fabricated WOFF2 face with one square glyph per code point."""
    names = ['.notdef'] + [f'u{point:04x}' for point in codepoints]
    def square():
        pen = TTGlyphPen(None)
        pen.moveTo((0, 0)); pen.lineTo((0, 500)); pen.lineTo((500, 500)); pen.lineTo((500, 0)); pen.closePath()
        return pen.glyph()
    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder(names)
    builder.setupCharacterMap({point: f'u{point:04x}' for point in codepoints})
    builder.setupGlyf({name: square() for name in names})
    builder.setupHorizontalMetrics({name: (500, 0) for name in names})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable({'familyName': 'Synthetic Icons', 'styleName': 'Regular', 'copyright': 'Synthetic test font'})
    builder.setupOS2()
    builder.setupPost()
    builder.font.flavor = 'woff2'
    builder.save(path)


class StagedSiteBuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source, self.output = self.root / 'site', self.root / 'dist'
        # Real renderers/assets, but only one resource and one paper; no scan snapshot.
        shutil.copytree(ROOT / 'site', self.source)
        data = self.root / 'data'
        data.mkdir()
        resources = json.loads((ROOT / 'data/rea-resources.json').read_text())
        case = next(record for record in resources if record['kind'] == 'case-study')
        paper = json.loads((ROOT / 'data/papers.json').read_text())[0]
        for filename, record in [('rea-resources.json', case), ('papers.json', paper)]:
            (data / filename).write_text(json.dumps([record]))
        (data / 'tool-resources.json').write_text('[]')
        # Exercise the real survey renderer against this same bounded catalog.
        pair = lambda en, zh: {'en': en, 'zh': zh}
        survey = {
            'schema_version': 1, 'version': '1.0', 'date': '2026-10-18',
            'snapshot': {'revision': 'a' * 40, 'papers': 1, 'resources': 1,
                         'cases': 1, 'selected_cases': 1},
            'paper_ids': [paper['id']], 'reference_records': [paper, case],
            'subtitle': pair('A bounded synthesis.', '范围明确的综述。'),
            'description': pair('Methods and evidence.', '方法与证据。'),
            'abstract': pair('A reviewed source [[' + paper['id'] + ']].',
                             '已核查来源 [[' + paper['id'] + ']]。'),
            'disclosure': pair('Editorial synthesis; no new experiments.', '编辑性综述；无新实验。'),
            'reference_note': pair('Original sources.', '原始来源。'),
            'figure_caption': pair('Observe and compare.', '观察与比较。'),
            'findings': [pair('Evidence bounds claims.', '证据限定结论。')],
            'pipeline': [{'title': pair('Observe', '观察'),
                          'text': pair('Retain evidence.', '保留证据。')}],
            'sections': [{'id': 'methods', 'title': pair('Methods', '方法'),
                          'paragraphs': [pair('Compare a documented case.', '比较有文档记录的案例。')],
                          'table': 'cases'}],
            'tables': {'cases': {'caption': pair('Case evidence', '案例证据'),
                'headers': [pair('Case', '案例'), pair('Evidence', '证据')],
                'rows': [{'reference': case['id'], 'label': pair('Case', '案例'),
                          'cells': [pair('Project documentation', '项目文档')]}]}},
        }
        (data / 'survey.json').write_text(json.dumps(survey))
        self.unowned = self.root / 'keep.txt'
        self.unowned.write_bytes(b'Not deployment output\n')
        stack = self.enterContext(ExitStack())
        for name, value in [('ROOT', self.root), ('SOURCE', self.source), ('OUTPUT', self.output)]:
            stack.enter_context(patch.object(build_site, name, value))

    def build(self, **kwargs):
        result = build_site.build_staged_site(**kwargs)
        self.assertEqual(result[:2], (1, 1))
        manifest = read_build_manifest(self.output)
        self.assertTrue(manifest['files']['index.html']['html_sha256'])
        for route in ('survey/index.html', 'zh/survey/index.html'):
            self.assertTrue(manifest['files'][route]['html_sha256'])
        self.assertIn('survey/references.bib', manifest['files'])
        self.assertIn('survey/citation.bib', manifest['files'])
        self.assertNotIn(str(self.root), json.dumps(manifest))
        self.assertEqual(self.unowned.read_bytes(), b'Not deployment output\n')
        self.assertEqual(list((self.root / '.cache').glob('site-build-*')), [])
        return manifest

    def test_deleted_assets_and_nested_files_do_not_survive_rebuild(self):
        (self.source / 'legacy.css').write_text('old css')
        (self.source / 'old').mkdir()
        (self.source / 'old' / 'data.txt').write_text('old nested data')
        first = self.build()
        self.assertIn('legacy.css', first['files'])
        self.assertIn('old/data.txt', first['files'])
        (self.source / 'legacy.css').unlink()
        shutil.rmtree(self.source / 'old')
        second = self.build()
        for path in ('legacy.css', 'old/data.txt'):
            self.assertFalse((self.output / path).exists())
            self.assertNotIn(path, second['files'])
        # A normal repeated build has identical bytes, including its manifest.
        expected = file_bytes(self.output)
        self.build()
        self.assertEqual(file_bytes(self.output), expected)

    def test_late_generation_failure_preserves_prior_valid_output(self):
        self.build()
        expected = file_bytes(self.output)
        (self.source / 'app.js').write_text((self.source / 'app.js').read_text() + '\n// changed asset\n')
        with patch.object(build_site, 'write_build_manifest', side_effect=ValueError('late manifest failure')):
            with self.assertRaisesRegex(ValueError, 'late manifest failure'):
                build_site.build_staged_site()
        self.assertEqual(file_bytes(self.output), expected)
        read_build_manifest(self.output)
        self.assertEqual(list((self.root / '.cache').glob('site-build-*')), [])
        self.assertEqual(self.unowned.read_bytes(), b'Not deployment output\n')

    def test_failed_replacement_restores_prior_valid_output(self):
        self.build()
        expected = file_bytes(self.output)
        rename = Path.rename

        def fail_next(path, target):
            if path.name == 'next':
                raise OSError('replacement failed')
            return rename(path, target)

        with patch.object(Path, 'rename', fail_next):
            with self.assertRaisesRegex(OSError, 'replacement failed'):
                build_site.build_staged_site()
        self.assertEqual(file_bytes(self.output), expected)
        read_build_manifest(self.output)
        self.assertEqual(list((self.root / '.cache').glob('site-build-*')), [])

    def test_failed_rollback_keeps_recoverable_previous_output(self):
        self.build()
        expected = file_bytes(self.output)
        rename = Path.rename

        def fail_next_and_restore(path, target):
            if path.name in {'next', 'previous'}:
                raise OSError('rename failed')
            return rename(path, target)

        with patch.object(Path, 'rename', fail_next_and_restore):
            with self.assertRaisesRegex(RuntimeError, 'prior deployment.*preserved'):
                build_site.build_staged_site()
        preserved = list((self.root / '.cache').glob('site-build-*/previous'))
        self.assertEqual(len(preserved), 1)
        self.assertEqual(file_bytes(preserved[0]), expected)
        read_build_manifest(preserved[0])
        self.assertEqual(self.unowned.read_bytes(), b'Not deployment output\n')

    def test_output_symlink_and_file_are_rejected_without_touching_target(self):
        external = self.root / 'other'
        external.mkdir()
        (external / 'keep.txt').write_text('preserve me')
        self.output.symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink or file'):
            build_site.build_staged_site()
        self.assertEqual(file_bytes(external), {'keep.txt': b'preserve me'})
        self.output.unlink()
        self.output.write_text('unrelated file')
        with self.assertRaisesRegex(ValueError, 'symlink or file'):
            build_site.build_staged_site()
        self.assertEqual(self.output.read_text(), 'unrelated file')
        self.assertFalse((self.root / '.cache').exists())

    def test_cache_symlink_is_rejected_without_touching_target(self):
        external = self.root / 'other'
        external.mkdir()
        (external / 'keep.txt').write_text('preserve me')
        (self.root / '.cache').symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink or file'):
            build_site.build_staged_site()
        self.assertEqual(file_bytes(external), {'keep.txt': b'preserve me'})
        self.assertFalse(self.output.exists())

    def synthetic_package(self, *, omit=()):
        """Fabricated fixtures only: no licensed font data enters the test sources."""
        package = self.root / 'synthetic-icons'
        (package / 'css').mkdir(parents=True)
        (package / 'webfonts').mkdir()
        points = {key: 0xf000 + index for index, key in enumerate(build_site.FONT_AWESOME_ICONS)}
        css = '\n'.join('.fa-' + build_site.FONT_AWESOME_ICONS[key] + '{--fa:"\\' + format(point, 'x') + '";}'
                        for key, point in points.items())
        for name in ('fontawesome.css', 'brands.css', 'light.css'):
            (package / 'css' / name).write_text(css)
        # Each face also holds glyphs the site never draws; the build must drop them.
        unused = list(range(0xe000, 0xe040))
        light = {point for key, point in points.items() if key not in build_site.FONT_AWESOME_BRANDS and key not in omit}
        brands = {points[key] for key in build_site.FONT_AWESOME_BRANDS}
        for name, wanted in (('fa-light-300.woff2', light), ('fa-brands-400.woff2', brands)):
            if HAVE_FONT_TOOLS:
                synthetic_font(package / 'webfonts' / name, sorted(wanted) + unused)
            else:
                (package / 'webfonts' / name).write_bytes(b'synthetic test bytes, not a font')
        return package, light, brands

    def test_synthetic_font_package_stays_separate_across_all_modes(self):
        package, light, brands = self.synthetic_package()
        input_before = file_bytes(package)
        source_before = file_bytes(self.source)
        with ExitStack() as stack:
            if not HAVE_FONT_TOOLS:
                # Without fontTools a copying stand-in still exercises the switches between icon modes.
                stack.enter_context(patch.object(build_site, 'subset_icon_font', lambda source, destination, points: shutil.copy2(source, destination)))
            manifest = self.build(fontawesome_dir=package)
        self.assertIn('fontawesome.css', manifest['files'])
        fonts = ('fa-light-300.woff2', 'fa-brands-400.woff2')
        for name, points in zip(fonts, (light, brands)):
            self.assertNotIn('fonts/' + name, manifest['files'])
            if not HAVE_FONT_TOOLS:
                continue
            subset = self.output / 'fonts' / name
            # Only the site's icon code points ship, as WOFF2 smaller than the input face.
            with TTFont(subset) as font:
                self.assertEqual(set(font.getBestCmap()), points)
                self.assertEqual(font.flavor, 'woff2')
                self.assertEqual(font['name'].getDebugName(0), 'Synthetic test font')
            self.assertLess(subset.stat().st_size, len(input_before['webfonts/' + name]))
        self.assertIn('data-icon-set="fontawesome"', (self.output / 'index.html').read_text())
        self.build(fontawesome_assets_url='https://example.org/icons')
        self.assertIn('https://example.org/icons/fontawesome.css', (self.output / 'index.html').read_text())
        self.assertFalse((self.output / 'fontawesome.css').exists())
        self.assertFalse((self.output / 'fonts').exists())
        self.build()
        html = (self.output / 'index.html').read_text()
        self.assertNotIn('fontawesome.css', html)
        self.assertNotIn('data-icon-set="fontawesome"', html)
        self.assertIn('class="symbol-bank"', html)
        self.assertFalse((self.output / 'fontawesome.css').exists())
        self.assertFalse((self.output / 'fonts').exists())
        self.assertEqual(file_bytes(package), input_before)
        self.assertEqual(file_bytes(self.source), source_before)

    @unittest.skipUnless(HAVE_FONT_TOOLS, 'fontTools with Brotli is needed to subset the icon fonts')
    def test_icon_missing_from_the_font_fails_the_build(self):
        self.build()
        expected = file_bytes(self.output)
        package, _, _ = self.synthetic_package(omit={'globe'})
        globe = 0xf000 + list(build_site.FONT_AWESOME_ICONS).index('globe')
        with self.assertRaisesRegex(ValueError, f'missing icons: U\\+{globe:04X}'):
            build_site.build_staged_site(fontawesome_dir=package)
        self.assertEqual(file_bytes(self.output), expected)

    def test_licensed_fonts_without_font_tools_fail_clearly(self):
        self.build()
        expected = file_bytes(self.output)
        package, _, _ = self.synthetic_package()
        with patch.dict(sys.modules, {'fontTools': None, 'fontTools.subset': None, 'fontTools.ttLib': None}):
            with self.assertRaisesRegex(ValueError, 'requires fontTools with Brotli'):
                build_site.build_staged_site(fontawesome_dir=package)
        self.assertEqual(file_bytes(self.output), expected)

    def test_homepages_carry_unfiltered_target_counts(self):
        # app.js recounts after loading; the build writes the same unfiltered numbers so nothing shifts.
        self.build()
        record = json.loads((self.root / 'data/rea-resources.json').read_text())[0]
        for route in ('index.html', 'zh/index.html'):
            html = (self.output / route).read_text()
            counts = dict(re.findall(r'data-target-count="([a-z]+)">([^<]*)<', html))
            self.assertEqual(counts, {'all': '1', **{target: str(int(target in record['targets']))
                                                     for target in ('website', 'game', 'app', 'binary', 'firmware', 'protocol')}})
            protocol = re.search(r'<button[^>]*data-target="protocol"[^>]*>', html)[0]
            self.assertEqual(' hidden' in protocol, 'protocol' not in record['targets'])

    def test_invalid_font_input_preserves_prior_output(self):
        self.build()
        expected = file_bytes(self.output)
        with self.assertRaisesRegex(ValueError, 'Font Awesome input'):
            build_site.build_staged_site(fontawesome_dir=self.root / 'missing-icons')
        self.assertEqual(file_bytes(self.output), expected)
        read_build_manifest(self.output)
        self.assertEqual(list((self.root / '.cache').glob('site-build-*')), [])


if __name__ == '__main__':
    unittest.main()
