"""No tracked file or built page names or links the people the maintainer asked to keep out of the collection.

The protected forms live in scripts/privacy_guard.py only as salted digests. The matching rules are tested
here with invented names, so this file holds no protected text either.
"""
import bz2
import gzip
import lzma
from pathlib import Path
import io
import re
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import privacy_guard
from privacy_guard import PARTS, PINNED_EVIDENCE, PROTECTED, SALT, Detector, default_paths, scan

# Invented forms: a two-word name in either order, a handle, a personal domain and a profile ID.
SAMPLE = Detector.from_grams(b'test-only-salt', ['orla venn', 'venn orla', 'ovenn42', 'orla space', 'xq 7rtaaaaj'])


def kinds(text, path='sample.txt'):
    return [(finding.line, finding.kind) for finding in SAMPLE.scan_text(text, path)]


class PrivacyGuardTests(unittest.TestCase):
    def test_tracked_files_and_the_build_output_hold_no_protected_identifier(self):
        paths = default_paths()
        self.assertGreater(len(paths), 300)
        findings, unread = scan(paths)
        # Only file and line are reported, never the matched words.
        self.assertEqual([str(finding) for finding in findings], [])
        self.assertTrue(all(name.endswith('.zip') for name in unread), unread)

    def test_only_digests_are_stored(self):
        self.assertGreaterEqual(len(SALT), 16)
        for digest in PROTECTED | PARTS | PINNED_EVIDENCE:
            self.assertRegex(digest, r'^[0-9a-f]{64}$')
        self.assertTrue(PARTS and len(PROTECTED) > len(PARTS))
        source = (ROOT / 'scripts/privacy_guard.py').read_text(encoding='utf-8')
        constants = re.findall(r"^\s+'([^']*)',$", source, re.M)
        self.assertEqual(len(constants), len(PROTECTED | PARTS | PINNED_EVIDENCE))
        self.assertTrue(all(re.fullmatch(r'[0-9a-f]{64}', value) for value in constants))

    def test_names_match_in_either_order_case_spacing_or_joined(self):
        for text in ('Contact Orla Venn for details.', 'VENN, ORLA and Bo Kim', 'orla-venn', 'orla_venn', 'Orla.Venn',
                     'Orla\tVenn', 'Orla\nVenn', '{Venn, Orla and Kim, Bo}', '{Orla Venn} and {Bo Kim}',
                     '"author": "Orla Venn"'):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [(1, 'word pair')])
        for text in ('OrlaVenn', 'vennorla', 'orlavenn2024', 'https://example.com/@OrlaVenn', 'ovenn42024', 'OVenn421'):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [(1, 'single word')])

    def test_accents_full_width_letters_and_escapes_are_folded_or_decoded(self):
        for text in ('Órla Vénn', 'Ｏｒｌａ Ｖｅｎｎ', 'Orla&nbsp;Venn', 'Orla&#32;Venn', 'Orla%20Venn',
                     'Orla\\u0020Venn', 'Orla' + chr(0xA0) + 'Venn', 'Orla\\u00a0Venn'):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [(1, 'word pair')])

    def test_escaped_letters_are_decoded_before_words_are_collected(self):
        for text, kind in (('Orla%56enn', 'single word'), ('Orla\\u0056enn', 'single word'), ('OVenn%342', 'single word'),
                           ('Orla V%65nn', 'word pair'), ('Orl&#97; Venn', 'word pair'), ('Orl&#x61; Venn', 'word pair'),
                           ('&Oacute;rla Venn', 'word pair'), ('Orla%20V%C3%A9nn', 'word pair')):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [(1, kind)])

    def test_inline_markup_does_not_split_a_name_but_list_markup_does(self):
        for text, kind in (('<p>Orla <em>Venn</em></p>', 'word pair'), ('<a href="/x">Orla</a> <strong>Venn</strong>', 'word pair'),
                           ('<span class="given">Orla</span> <span class="family">Venn</span>', 'word pair'),
                           ('<p>Or<b>la</b> Venn</p>', 'word pair'), ('<p>Orla<em>Venn</em></p>', 'single word'),
                           ('<i>Venn</i>, <i>Orla</i>', 'word pair'),
                           ('<span>Or</span><span>la</span> <span>Ve</span><span>nn</span>', 'word pair'),
                           ('<b>O</b>Ven<b>n42</b>', 'single word')):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [(1, kind)])
        for text in ('<li>Mia Venn</li><li>Orla Kim</li>', '<td>Mia Venn</td><td>Orla Kim</td>', 'Mia Venn<br>Orla Kim',
                     '<p>Mia <em>Venn</em></p><p><em>Orla</em> Kim</p>'):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [])

    def test_identifiers_in_attributes_of_inline_markup_still_match(self):
        for text, kind in (('<a href="https://orla.space/">site</a>', 'word pair'),
                           ('<p><a href="https://scholar.google.com/citations?user=XQ_7rtAAAAJ">profile</a></p>', 'word pair'),
                           ('<a href="https://github.com/OVenn42"><em>code</em></a>', 'single word'),
                           ('<span title="Orla Venn">author</span>', 'word pair')):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [(1, kind)])

    def test_soft_hyphens_zero_width_characters_and_comments_do_not_split_a_name(self):
        soft, zero = chr(0xAD), chr(0x200B)
        for text in (f'Or{soft}la Venn', f'Orla V{zero}enn', 'Or&shy;la Venn', 'Orla V&#8203;enn', 'Or%C2%ADla Venn',
                     'Orla Ve\\u200bnn', '<p>Or<!-- x -->la Venn</p>'):
            with self.subTest(text=ascii(text)):
                self.assertEqual(kinds(text), [(1, 'word pair')])

    def test_structured_name_fields_count_as_one_name(self):
        for text in ('{"given":"Orla","family":"Venn"}', '{"family": "Venn", "given": "Orla", "sequence": "first"}',
                     '[\n  {"firstName": "Orla",\n   "lastName": "Venn"}\n]'):
            with self.subTest(text=text):
                self.assertEqual([kind for _, kind in kinds(text)], ['word pair'])
        self.assertEqual(kinds('[{"given": "Mia", "family": "Venn"}, {"given": "Orla", "family": "Kim"}]'), [])

    def test_comma_lists_of_authors_do_not_pair_but_family_given_forms_do(self):
        # Inside a visible list of authors, a surname and the next author's given name are two people.
        for text in ('Authors: Mia Venn, Orla Kim, Bo Lee.', 'Ann Fox, Mia Venn, Orla Kim', 'Mia Venn, Orla Kim and Bo Lee',
                     'MIA VENN, ORLA KIM, BO LEE', 'Mia Venn, Orla Kim & Bo Lee'):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [])
        # Otherwise "Family, Given" is one name, with or without capitalized neighbours, titles or suffixes.
        for text in ('Kim, Bo and Venn, Orla', 'Contact Venn, Orla for details.', 'Venn, Orla Mae', 'Venn,Orla',
                     'Dr Venn, Orla PhD', 'Prof. Venn, Orla Kim', 'Mia Venn, Orla Jr.', 'Contact Venn, Orla Today',
                     'Mia Venn, Orla Kim'):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [(1, 'word pair')])

    def test_citation_name_fields_count_as_one_name(self):
        for text in ('authors:\n  - given-names: Orla\n    family-names: Venn\n',
                     'authors:\n  - family-names: Venn\n    given-names: Orla\n'):
            with self.subTest(text=text):
                self.assertEqual([kind for _, kind in kinds(text)], ['word pair'])

    def test_handles_domains_and_profile_ids_match(self):
        self.assertEqual(kinds('Code: https://github.com/OVenn42/tools'), [(1, 'single word')])
        self.assertEqual(kinds('[site](https://orla.space/)'), [(1, 'word pair')])
        self.assertEqual(kinds('https://scholar.google.com/citations?user=XQ_7rtAAAAJ&hl=en'), [(1, 'word pair')])

    def test_adjacent_items_of_a_list_never_pair(self):
        # The surname ending one listed name and the given name starting the next are different people.
        for text in ('["Mia Venn", "Orla Kim"]', '[\n  "Mia Venn",\n  "Orla Kim"\n]', 'Mia Venn; Orla Kim',
                     '- Mia Venn\n- Orla Kim', '1. Mia Venn\n2. Orla Kim', '<li>Mia Venn</li><li>Orla Kim</li>',
                     'Mia Venn and Orla Kim', '{Mia Venn} and {Orla Kim}', 'Mia Venn · Orla Kim', 'Mia Venn | Orla Kim',
                     'Mia Venn\n\nOrla Kim', 'Mia Venn、Orla Kim', 'Mia Venn &quot;Orla Kim'):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [])

    def test_single_words_initials_and_longer_words_do_not_match(self):
        for text in ('Orla', 'Venn diagram', 'O. Venn', 'Orla V.', 'Orla Vennison', 'Orlando Venn', 'ovenn', 'ovenn4'):
            with self.subTest(text=text):
                self.assertEqual(kinds(text), [])

    def test_findings_give_the_line_of_the_match(self):
        self.assertEqual(kinds('one\ntwo\nThree with Orla Venn\nfour OrlaVenn\n'), [(3, 'word pair'), (4, 'single word')])
        self.assertEqual(kinds('"a",\n"b",\n"Venn, Orla"'), [(3, 'word pair')])

    def test_archives_are_read_member_by_member(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('clean.json', '["Mia Venn", "Orla Kim"]')
            archive.writestr('data/papers.json', '{\n"authors": ["Orla Venn"]\n}')
            archive.writestr('image.png', b'\x89PNG\r\n\x1a\n\x00\x00\x00\x1btEXtAuthor\x00Orla Venn\x00')
            archive.writestr('pixels.png', bytes(range(256)) * 16)
        findings = SAMPLE.scan_bytes(buffer.getvalue(), 'bundle.zip')
        self.assertEqual([str(finding) for finding in findings],
                         ['bundle.zip!data/papers.json:2: protected identifier (word pair)',
                          'bundle.zip!image.png:3: protected identifier (word pair)'])

    def test_archives_beyond_the_bounds_or_unreadable_fail_as_unchecked(self):
        def archive(**members):
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as handle:
                for name, content in members.items():
                    handle.writestr(name, content)
            return buffer.getvalue()

        with mock.patch.object(privacy_guard, 'MEMBER_LIMIT', 64):
            findings = SAMPLE.scan_bytes(archive(small='clean text', large='x' * 1000), 'big.zip')
        self.assertEqual([str(finding) for finding in findings], ['big.zip!large: not checked (too large to read)'])
        with mock.patch.object(privacy_guard, 'ARCHIVE_LIMIT', 100):
            findings = SAMPLE.scan_bytes(archive(a='y' * 80, b='z' * 80), 'total.zip')
        self.assertEqual([str(finding) for finding in findings], ['total.zip!b: not checked (too large to read)'])
        nested = archive(inner=archive(deeper=archive(note='Orla Venn')))
        self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(nested, 'nested.zip')],
                         ['nested.zip!inner!deeper: not checked (archive nested too deeply)'])
        self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(b'PK\x03\x04 not an archive', 'bad.zip')],
                         ['bad.zip: not checked (unreadable archive)'])
        self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(b'plain text, not an archive', 'fake.zip')],
                         ['fake.zip: not checked (unreadable archive)'])

    def test_utf16_text_is_decoded_and_text_after_nul_bytes_is_checked(self):
        text = 'Line one\nMaintained by Orla Venn\n'
        for data in (text.encode('utf-16'), text.encode('utf-16-le'), text.encode('utf-16-be'), text.encode('utf-32')):
            with self.subTest(data=data[:4]):
                self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(data, 'note.txt')],
                                 ['note.txt:2: protected identifier (word pair)'])
        self.assertEqual(SAMPLE.scan_bytes(bytes(range(256)) * 4, 'blob.bin'), [])
        # A stray NUL byte does not make a page binary: browsers still render the text after it.
        self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(b'<p>a\x00b</p>\n<p>Orla Venn</p>', 'page.html')],
                         ['page.html:2: protected identifier (word pair)'])

    def test_gzip_and_tar_contents_are_read(self):
        self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(gzip.compress(b'x\nOrla Venn'), 'notes.txt.gz')],
                         ['notes.txt:2: protected identifier (word pair)'])
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w') as archive:
            for name, content in (('a.txt', b'Venn, Orla'), ('docs/orla-venn.md', b'clean'), ('b.txt', b'clean')):
                info = tarfile.TarInfo(name)
                info.size = len(content)
                archive.addfile(info, io.BytesIO(content))
        expected = ['bundle.tar!a.txt:1: protected identifier (word pair)',
                    'bundle.tar!docs/<redacted>: protected identifier in the file path']
        self.assertEqual(sorted(str(finding) for finding in SAMPLE.scan_bytes(buffer.getvalue(), 'bundle.tar')), expected)
        compressed = gzip.compress(buffer.getvalue())
        self.assertEqual(sorted(str(finding) for finding in SAMPLE.scan_bytes(compressed, 'bundle.tgz')), expected)
        self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(b'\x1f\x8b broken', 'bad.gz')],
                         ['bad.gz: not checked (unreadable archive)'])

    def test_every_compressed_stream_is_read_in_full_and_unknown_formats_fail(self):
        joined = gzip.compress(b'clean\n') + gzip.compress(b'Orla Venn\n')
        self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(joined, 'log.gz')],
                         ['log:2: protected identifier (word pair)'])
        truncated = gzip.compress(b'clean words ' * 200 + b'Orla Venn')[:-12]
        self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(truncated, 'cut.gz')],
                         ['cut.gz: not checked (unreadable archive)'])
        for compress, name in ((bz2.compress, 'notes.txt.bz2'), (lzma.compress, 'notes.txt.xz')):
            with self.subTest(name=name):
                self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(compress(b'Venn, Orla'), name)],
                                 ['notes.txt:1: protected identifier (word pair)'])
        for data, name in ((b"7z\xbc\xaf\x27\x1c rest", 'pack.bin'), (b'Rar!\x1a\x07\x00', 'pack.rar'),
                           (b'\x28\xb5\x2f\xfd\x00', 'pack.zst'), (b'opaque', 'page.html.br')):
            with self.subTest(name=name):
                self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(data, name)],
                                 [f'{name}: not checked (unsupported archive format)'])

    def test_archives_behind_a_prepended_stub_are_still_read(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as handle:
            handle.writestr('notes.txt', 'Maintained by Orla Venn')
        bundle = b'#!/bin/sh\nexit 0\n\x00\x01stub' + buffer.getvalue()
        self.assertTrue(zipfile.is_zipfile(io.BytesIO(bundle)))
        self.assertEqual([str(finding) for finding in SAMPLE.scan_bytes(bundle, 'tool.run')],
                         ['tool.run!notes.txt:1: protected identifier (word pair)'])

    def test_file_paths_and_member_names_are_checked_and_never_printed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / 'orla').mkdir()
            (root / 'docs/OVenn42-notes.md').write_text('clean\n', encoding='utf-8')
            (root / 'docs/orla-venn.md').write_text('line one\nOrla Venn\n', encoding='utf-8')
            (root / 'orla/venn.md').write_text('clean\n', encoding='utf-8')
            (root / 'orla/venn').mkdir()
            (root / 'orla/venn/OVenn42.md').write_text('clean\n', encoding='utf-8')
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as archive:
                archive.writestr('data/orlavenn.txt', 'clean')
                archive.writestr(zipfile.ZipInfo('orla-venn/'), '')
            (root / 'bundle.zip').write_bytes(buffer.getvalue())
            findings, _ = scan(sorted(path for path in root.rglob('*') if path.is_file()), root=root, detector=SAMPLE)
        printed = [str(finding) for finding in findings]
        self.assertEqual(sorted(printed), sorted([
            'docs/<redacted>: protected identifier in the file path',
            'docs/<redacted>: protected identifier in the file path',
            'docs/<redacted>:2: protected identifier (word pair)',
            '<redacted path>: protected identifier in the file path',
            '<redacted path>: protected identifier in the file path',
            'bundle.zip!data/<redacted>: protected identifier in the file path',
            'bundle.zip!<redacted>/: protected identifier in the file path',
        ]))
        self.assertFalse(any(re.search('orla|venn', line, re.I) for line in printed), printed)

    def test_the_discovery_ingest_skips_and_rejects_protected_captures(self):
        import discoveries
        from test_discoveries import capture, empty_existing
        with mock.patch.object(discoveries, 'privacy_detector', return_value=SAMPLE):
            records = [capture(1), capture(2, name='orla-venn/re-tools'),
                       capture(3, description_en='Kept by Orla Venn.', description_zh='Kept by Orla Venn.')]
            selected, _, skipped = discoveries.select_records(records, empty_existing(), set(), limit=10)
            self.assertEqual([row['id'] for row in selected], ['scan-9000000001'])
            self.assertEqual(skipped['privacy'], 2)
            self.assertIn('capture names or links a person the collection keeps out',
                          discoveries.record_problems(records[2]))
            self.assertNotIn('capture names or links a person the collection keeps out',
                             discoveries.record_problems(records[0]))

    def test_scan_reports_paths_relative_to_the_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            (root / 'docs/note.md').write_text('Clean line\nMaintained by Orla Venn.\n', encoding='utf-8')
            (root / 'docs/other.md').write_text('Mia Venn; Orla Kim\n', encoding='utf-8')
            findings, unread = scan(sorted(root.rglob('*.md')), root=root, detector=SAMPLE)
            self.assertEqual([str(finding) for finding in findings], ['docs/note.md:2: protected identifier (word pair)'])
            self.assertEqual(unread, [])


if __name__ == '__main__':
    unittest.main()
