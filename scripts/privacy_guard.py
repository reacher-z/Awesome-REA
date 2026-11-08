#!/usr/bin/env python3
"""Fail when a protected personal identifier appears in tracked files or in the built website.

At the repository owner's request, two people are not named or linked anywhere in this collection, its
generated files or its website: not by name in either order or written as one word, nor by a GitHub handle,
personal site or scholar profile. This module stores only a random salt and SHA-256 digests of the protected
word grams. It never stores, prints or logs the protected text: a match reports a file, a line and its kind.

Each text is decoded (HTML entities, JSON \\u escapes, percent-encoding), folded with NFKD, stripped of
accents, lowercased and split into words at every other character. A protected single word, such as a handle
or a name written as one word, matches anywhere, also with trailing digits. A protected two-word gram matches
when its words are adjacent inside one list item: quotes, semicolons, brackets, braces, tags, pipes, middle
dots, list markers and blank lines separate items, so the surname ending one listed name and the given name
starting the next never form a pair, while "Given Family", "Family Given" and "Family, Given" do. The
name-field keys of citation formats (given-names, family-names) are skipped between the two words.

File paths and archive member names are checked the same way, and a path component that matches is printed
as <redacted>. UTF-16 and UTF-32 text is decoded. Zip and tar archives and gzip, bzip2 and xz streams are read
in full within size and nesting bounds; an archive that cannot be read within them, or one in a format the
standard library cannot read (7z, rar, zstd, brotli), fails the check. Every other file, binary or not, is
read as text, so readable strings in images or documents are checked; text drawn as pixels is not. No
archive is exempt: compressed members are read like any other file.

    python3 scripts/privacy_guard.py            # git-tracked files, then dist/ when it exists
    python3 scripts/privacy_guard.py PATH ...   # only these files or directories
"""
from __future__ import annotations

import argparse
import bz2
from dataclasses import dataclass
import gzip
import hashlib
import html
import io
import lzma
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import unicodedata
from urllib.parse import unquote
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
SALT = bytes.fromhex('9b5c46ad6b8ee9149e030519d31a8f5f')
# sha256(SALT + gram) for each protected gram: two-word names in both orders and joined, a GitHub handle,
# a personal domain and a scholar profile ID (each as a word pair and joined).
PROTECTED = frozenset({
    '1a1cae2191be71b3d767e1150ca1a34b91a0f33e4d3b953240fac64050653548',
    '49d889239abe7ea37ddc287fbcf9bc294f8026faf68e59c10a5cd9b5e36638d7',
    '633beaf43ee8598d8edcadf5f1015a0d331ec4c0a831a9286041f83039bd7dac',
    '6cf60137f65a36e68b7f01c8d56bd33790d930126589ed5daa088205bc4aba30',
    '715d266bcb3d084067e80535232bbe93d20c81f7c722436925edec01a4dc65dc',
    '7458b90b0bcdef4059b134f342b92ac4022d8a07d2d297de6342c77fda0763cf',
    '989bbd290d8d586d1eb2cd5e69509fe0d6013778af80f9ce2e3e3c5a875c3143',
    'b435edcc6be032b49941644f82684b257f64310176d32cf040c708430e4a2b25',
    'b643191f4de95daa5800a03eca03df24b4eb2288ba6fed4e2c3f9db0994c010b',
    'bb40243acbf9780106b40e7ea81f0ea9549d0e97e6b2d7760f6ca1fd81b9a4b7',
    'c7b58072e2edf30190dcd2d543c06f61b4c6108dc9a3487cfc576e04d75688d5',
    'c8f33142ae0b53bf7e3b6d4eefd281f9226c0144c9853d15ac36661c9ce3968b',
    'f171d1c3588451656c479f332b53779234d0049e45490ce85b9caa75a967e900',
})
# sha256(SALT + word) for each word of the two-word grams. A file is searched for adjacent pairs only when it
# contains two of these words that together form a protected gram.
PARTS = frozenset({
    '076c5ec8cc60177d9035ba66bf7411a4ca5e46fd994d46875ea6461aed9f6b2b',
    '3e33fff1250e5444d85eb8471bc04125bb32a5faffec740d48ce13553c0a9993',
    '5172cf7bd3fd9cc48dbdcf096d9ae724e63409dba9b50c1c3f50774772877e8d',
    '883b45d8e3e98e0bc7092b2bba7808623f1bff2f1086cc01633a9dc08028bd08',
    '896cf3a45fa7ff30be97fb7d8b690270ddc4732061474250bce599859d7fa21c',
    'cba5e15625297266273d86b6e728bb4a4b56efb064f5519b686f227c3666b1a5',
    'e877f26db44c2cd4880de1c10e3a8fa6f9eacd835681fd0f5d99ed4e7c78d743',
})

# Inline HTML phrasing tags do not separate words on screen ("Orla <em>Venn</em>" reads as one name), so they are
# removed before matching; block tags such as <li>, <p> and <td> still separate items.
INLINE_MARKUP = re.compile(r'</?(?:a|abbr|b|bdi|bdo|cite|code|data|del|dfn|em|font|i|ins|kbd|mark|q|s|samp|small|span'
                           r'|strike|strong|sub|sup|time|tt|u|var|wbr)(?:\s[^<>]*)?/?>|<!--.*?-->', re.I | re.S)
# Separators between list items and fields: a pair never spans one. Each becomes a record-separator byte.
HARD_CHARS = re.compile(r'["“”„‟«»「」『』;；<>{}()\[\]|·•、\x00]')
LIST_BREAK = re.compile(r'\n(?=[ \t]*(?:[-*+>]|\d+[.)])[ \t])')
BLANK_LINE = re.compile(r'\n[ \t]*\n')
SEPARATOR = '\x1e'
# Characters that NFKD maps to ASCII letters or digits (accented and full-width Latin, ligatures, combining
# marks); other non-ASCII text, such as CJK, only separates words.
# Latin-1 letters, superscript digits and ordinals, Latin Extended, combining marks, Latin Extended Additional,
# super- and subscripts, enclosed alphanumerics, ligatures and full-width digits and letters. Punctuation, such
# as the middle dot and full-width commas and colons, stays out, so ordinary Chinese and English text costs nothing.
LATINISH_RANGES = ((0x00AA, 0x00AA), (0x00B2, 0x00B3), (0x00B9, 0x00BA), (0x00C0, 0x02AF), (0x0300, 0x036F),
                   (0x1AB0, 0x1AFF), (0x1DC0, 0x1EFF), (0x2070, 0x209F), (0x2460, 0x24FF), (0xFB00, 0xFB06),
                   (0xFE20, 0xFE2F), (0xFF10, 0xFF19), (0xFF21, 0xFF3A), (0xFF41, 0xFF5A))
COMBINING_RANGES = ((0x0300, 0x036F), (0x1AB0, 0x1AFF), (0x1DC0, 0x1DFF), (0x20D0, 0x20FF), (0xFE20, 0xFE2F))


def _character_class(ranges) -> str:
    return '[' + ''.join(f'{re.escape(chr(low))}-{re.escape(chr(high))}' for low, high in ranges) + ']'


LATINISH = re.compile(_character_class(LATINISH_RANGES) + '+')
# Soft hyphens and zero-width characters do not separate words on screen: they are removed, not split on.
INVISIBLE = re.compile(_character_class(((0x00AD, 0x00AD), (0x200B, 0x200D), (0x2060, 0x2060), (0xFEFF, 0xFEFF))))
COMBINING = re.compile(_character_class(COMBINING_RANGES))
# Escapes that would otherwise glue to the next word (%20Name, \\u0020Name): blanked when collecting words, decoded
# before pairing them. HTML entities need no blanking: their & # ; already separate words.
ESCAPE_GAPS = re.compile(r'%[0-9A-Fa-f]{2}|\\u[0-9A-Fa-f]{4}')
# Escapes that can encode a letter or digit, ASCII or Latin: a text with one is also read decoded.
LETTER_ESCAPE = re.compile(
    r'%(?:3[0-9]|[46][1-9A-Fa-f]|[57][0-9Aa]|[Cc][3-9]|[Ee]1%[Bb][89ABab]|[Ee][Ff]%[Bb][CDcd])'
    r'|\\u(?:00(?:3[0-9]|[4-7][0-9A-Fa-f]|[C-Fc-f][0-9A-Fa-f])|0[12][0-9A-Fa-f]{2}|1[Ee][0-9A-Fa-f]{2}'
    r'|[Ff][Ff][0-5][0-9A-Fa-f])'
    r'|&#0*(?:4[89]|5[0-7]|6[5-9]|[78][0-9]|9[0789]|1[01][0-9]|12[0-2]|19[2-9]|[2-5][0-9]{2});'
    r'|&#[xX]0*(?:3[0-9]|[4-7][0-9A-Fa-f]|[C-Fc-f][0-9A-Fa-f]|[12][0-9A-Fa-f]{2}|1[Ee][0-9A-Fa-f]{2}'
    r'|[Ff][Ff][0-5][0-9A-Fa-f]);'
    r'|&[A-Za-z]{1,2}(?:acute|grave|circ|uml|tilde|ring|cedil|slash|caron|macr|breve|ogon|dot|strok|lig);'
    r'|&(?:shy|zwj|zwnj|ZeroWidthSpace);|&#0*(?:173|820[345]|8288|65279);|&#[xX]0*(?:[aA][dD]|200[bBcCdD]|2060|[fF][eE][fF][fF]);'
    r'|%[Cc]2%[Aa][Dd]|%[Ee]2%80%8[BbCcDd]|\\u(?:00[aA][dD]|200[bBcCdD]|2060|[fF][eE][fF][fF])')
JSON_ESCAPE = re.compile(r'\\u([0-9A-Fa-f]{4})')
PERCENT_RUN = re.compile(r'(?:%[0-9A-Fa-f]{2})+')
# ASCII letters lowercased; digits, newlines and the separator byte kept; every other byte a space.
FOLD = bytes(c if 48 <= c <= 57 or 97 <= c <= 122 or c in (10, 0x1e) else c + 32 if 65 <= c <= 90 else 32
             for c in range(256))
# For pairing: letter case, commas and ampersands kept as well, so that author lists can be told from
# "Family, Given".
FOLD_PAIRS = bytes(c if 48 <= c <= 57 or 65 <= c <= 90 or 97 <= c <= 122 or c in (10, 0x1e, 44, 38) else 32
                   for c in range(256))
# A name stored as separate fields of one flat JSON object, as in CSL-JSON {"given": ..., "family": ...}.
JSON_OBJECT = re.compile(r'\{[^{}]{1,4000}\}')
JSON_FIELD = re.compile(r'"([A-Za-z_ -]{2,24})"\s*:\s*"([^"\\]{1,200})"')
# Honorifics before and post-nominals after a "Family, Given" name: their neighbours do not make it a list.
TITLES = frozenset({b'dr', b'prof', b'professor', b'mr', b'mrs', b'ms', b'mx', b'miss', b'sir', b'dame', b'rev', b'hon'})
SUFFIXES = frozenset({b'phd', b'md', b'jr', b'sr', b'ii', b'iii', b'iv', b'esq', b'dphil', b'msc', b'mba', b'frs'})
GIVEN_KEYS = frozenset({'given', 'givenname', 'givennames', 'first', 'firstname', 'forename'})
FAMILY_KEYS = frozenset({'family', 'familyname', 'familynames', 'last', 'lastname', 'surname'})
# Name-field keys of citation formats, allowed between the two words of a pair.
FIELD_WORDS = (b'given', b'family', b'names', b'name', b'first', b'last', b'middle', b'surname')
# Compression read through the standard library: (magic bytes, file suffixes, opener).
COMPRESSED = ((b'\x1f\x8b', ('.gz', '.tgz'), lambda raw: gzip.GzipFile(fileobj=raw, mode='rb')),
              (b'BZh', ('.bz2', '.tbz2'), bz2.BZ2File), (b'\xfd7zXZ\x00', ('.xz', '.txz'), lzma.LZMAFile))
# Archive and compression formats the standard library cannot read: they fail the check as unchecked.
UNSUPPORTED = ((b'7z\xbc\xaf\x27\x1c', '.7z'), (b'Rar!\x1a\x07', '.rar'), (b'\x28\xb5\x2f\xfd', '.zst'), (None, '.br'),
               (None, '.lz4'), (None, '.lzma'))
TEXT_BOMS = ((b'\xff\xfe\x00\x00', 'utf-32-le'), (b'\x00\x00\xfe\xff', 'utf-32-be'), (b'\xff\xfe', 'utf-16-le'),
             (b'\xfe\xff', 'utf-16-be'), (b'\xef\xbb\xbf', 'utf-8'))
# Zip-format files are read as archives whatever their first bytes, so a prepended stub cannot hide members.
ZIP_SUFFIXES = frozenset({'.zip', '.jar', '.apk', '.aar', '.whl', '.egg', '.xpi', '.epub', '.nupkg', '.docx', '.xlsx',
                          '.pptx', '.odt', '.ods', '.odp'})
# Decompression bounds for zip archives: a member or archive beyond them, an archive inside an archive inside
# an archive, or one that cannot be read is reported as unchecked, which fails the check.
MEMBER_LIMIT = 128 * 1024 * 1024
ARCHIVE_LIMIT = 512 * 1024 * 1024
ARCHIVE_DEPTH = 2


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    kind: str

    def __str__(self):
        if self.kind in ('single word', 'word pair'):
            return f'{self.path}:{self.line}: protected identifier ({self.kind})'
        if self.kind == 'file path':
            return f'{self.path}: protected identifier in the file path'
        return f'{self.path}: not checked ({self.kind})'


def digest(salt: bytes, gram: bytes) -> str:
    return hashlib.sha256(salt + gram).hexdigest()


def fold(text: str, table: bytes = FOLD) -> bytes:
    """NFKD-folded, accent-free ASCII bytes, lowercase by default; newlines and separator bytes keep their places."""
    if not text.isascii():
        text = INVISIBLE.sub('', text)
        text = LATINISH.sub(lambda match: COMBINING.sub('', unicodedata.normalize('NFKD', match[0])), text)
    return text.encode('ascii', 'replace').translate(table)


def decoded(text: str) -> str:
    """Resolve JSON, HTML and percent escapes (percent runs as UTF-8)."""
    if '\\u' in text:
        text = JSON_ESCAPE.sub(lambda match: chr(int(match[1], 16)), text)
    if '&' in text:
        text = html.unescape(text)
    if '%' in text:
        text = PERCENT_RUN.sub(lambda match: unquote(match[0], errors='replace'), text)
    return text


def separated(text: str) -> str:
    """Mark every item separator with SEPARATOR, keeping the line count."""
    text = HARD_CHARS.sub(SEPARATOR, text)
    text = LIST_BREAK.sub(SEPARATOR + '\n', text)
    return BLANK_LINE.sub(SEPARATOR + '\n\n', text)


class Detector:
    def __init__(self, salt: bytes, protected, parts):
        self.salt, self.protected, self.parts = salt, frozenset(protected), frozenset(parts)
        self._seen, self._singles, self._part_words = set(), set(), set()

    @classmethod
    def from_grams(cls, salt: bytes, grams):
        """A detector for plaintext grams. Tests build one from invented names, never from the protected ones."""
        protected, parts = set(), set()
        for gram in grams:
            words = gram.encode().split()
            protected.add(digest(salt, b' '.join(words)))
            if len(words) == 2:
                protected.add(digest(salt, b''.join(words)))
                parts.update(digest(salt, word) for word in words)
        return cls(salt, protected, parts)

    def _learn(self, words: set) -> None:
        for word in words - self._seen:
            # The word itself, then the word without one, two, ... trailing digits, so that digits appended to a
            # protected word, even one that ends in a digit itself, still match.
            stems, stem = [word], word
            while stem[-1:].isdigit() and len(stem) > 3:
                stem = stem[:-1]
                stems.append(stem)
            if any(digest(self.salt, item) in self.protected for item in stems):
                self._singles.add(word)
            if digest(self.salt, word) in self.parts:
                self._part_words.add(word)
        self._seen |= words

    def pair(self, first: bytes, second: bytes) -> bool:
        """Whether these two words, in this order, form a protected gram."""
        return digest(self.salt, first + b' ' + second) in self.protected

    def scan_text(self, text: str, path: str) -> list[Finding]:
        gaps = ESCAPE_GAPS.sub(' ', text) if ('%' in text or '\\u' in text) else text
        variants = [fold(gaps)]
        if ('%' in text or '\\u' in text or '&' in text) and LETTER_ESCAPE.search(text):
            # An escape may hide a letter of a protected word, as in %56 or \u0056 for V.
            variants.append(fold(decoded(text)))
        words = set().union(*(variant.split() for variant in variants))
        self._learn(words)
        inline = False
        if '<' in text and INLINE_MARKUP.search(text):
            # Read the text as displayed too, without inline markup, where a protected word could be split.
            inline = True
            variants.append(fold(INLINE_MARKUP.sub('', gaps)))
            extra = set(variants[-1].split()) - words
            self._learn(extra)
            words |= extra
        findings = set()
        for word in words & self._singles:
            pattern = re.compile(rb'(?<![a-z0-9])' + re.escape(word) + rb'(?![a-z0-9])')
            lines = {variant.count(b'\n', 0, match.start()) + 1 for variant in variants for match in pattern.finditer(variant)}
            findings.update(Finding(path, line, 'single word') for line in lines or {1})
        parts = words & self._part_words
        candidates = [(first, second) for first in parts for second in parts
                      if first != second and self.pair(first, second)]
        if candidates:
            source = decoded(text)
            # Both readings: the markup as written, where links and attributes stay, and the text as displayed.
            sources = [source, INLINE_MARKUP.sub('', source)] if inline else [source]
            fields = b'|'.join(FIELD_WORDS)
            patterns = [re.compile(rb'(?<![a-z0-9])' + re.escape(first) + rb'(?:[ \n,]+(?:' + fields
                                   + rb')(?![a-z0-9]))*[ \n,]+' + re.escape(second) + rb'(?![a-z0-9])')
                        for first, second in candidates]
            for item in sources:
                cased = fold(separated(item), FOLD_PAIRS)
                marked = cased.lower()
                for pattern in patterns:
                    for match in pattern.finditer(marked):
                        if b',' not in match[0] or not self.listed(cased, match):
                            findings.add(Finding(path, marked.count(b'\n', 0, match.start()) + 1, 'word pair'))
            findings.update(self.structured(source, path))
        return sorted(findings)

    @staticmethod
    def listed(cased: bytes, match) -> bool:
        """True for a comma pair inside a visible list of authors, as in "Mia Venn, Orla Kim, Bo Lee": the
        surname of one listed author and the given name of the next, not one "Family, Given" name. Both neighbours
        are capitalized words, a title before or a post-nominal after does not count ("Dr Venn, Orla PhD"), and the
        list continues past them: another comma item before or after, or "and"/"&" with another capitalized name.
        A pair with two capitalized neighbours and nothing more ("Contact Venn, Orla Today") stays a match."""
        left = cased[max(0, match.start() - 120):match.start()]
        right = cased[match.end():match.end() + 120]
        before = re.search(rb'([A-Za-z0-9]+)[ \n]+$', left)
        after = re.match(rb'[ \n]+([A-Za-z0-9]+)', right)
        if not (before and after and before[1][:1].isupper() and after[1][:1].isupper()
                and before[1].lower() not in TITLES and after[1].lower() not in SUFFIXES):
            return False
        continues_left = re.search(rb'[A-Za-z0-9][ \n]*,[ \n]*' + re.escape(before[1]) + rb'[ \n]+$', left)
        continues_right = re.match(rb'[ \n]+' + re.escape(after[1]) + rb'(?:[ \n]*,|[ \n]+(?:and|&))[ \n]+[A-Z]', right)
        return bool(continues_left or continues_right)

    def structured(self, text: str, path: str) -> set[Finding]:
        """Given and family name fields of one flat JSON object that together form a protected name."""
        found = set()
        for item in JSON_OBJECT.finditer(text):
            given, family = [], []
            for key, value in JSON_FIELD.findall(item[0]):
                key = re.sub('[^a-z]', '', key.lower())
                if key in GIVEN_KEYS:
                    given += fold(value).split()
                elif key in FAMILY_KEYS:
                    family += fold(value).split()
            if any(self.pair(a, b) or self.pair(b, a) for a in given for b in family):
                found.add(Finding(path, text.count('\n', 0, item.start()) + 1, 'word pair'))
        return found

    def redact(self, path: str) -> tuple[str, bool]:
        """The path to print, with each component holding a protected identifier replaced, and whether any did."""
        if not self.scan_text(path.replace('/', ' '), ''):
            return path, False
        redacted = '/'.join('<redacted>' if self.scan_text(part, '') else part for part in path.split('/'))
        if redacted == path or self.scan_text(redacted.replace('/', ' '), ''):
            # A word pair split across components, alone or beside a matching component: hide the whole path.
            return '<redacted path>', True
        return redacted, True

    def scan_bytes(self, data: bytes, path: str, depth: int = 0) -> list[Finding]:
        if is_archive(data, path):
            return self.scan_archive(data, path, depth)
        suffix = Path(path).suffix.lower()
        for magic, suffixes, opener in COMPRESSED:
            if data.startswith(magic) or suffix in suffixes:
                return self.scan_compressed(data, path, depth, opener, suffixes)
        if any((magic and data.startswith(magic)) or suffix == ending for magic, ending in UNSUPPORTED):
            return [Finding(path, 0, 'unsupported archive format')]
        if data[257:262] == b'ustar' or suffix == '.tar':
            return self.scan_tar(data, path, depth)
        return self.scan_text(text_of(data), path)

    def scan_compressed(self, data: bytes, path: str, depth: int, opener, suffixes) -> list[Finding]:
        """Decompress every concatenated stream, up to MEMBER_LIMIT bytes, and check the result like any other
        file; a truncated or corrupt stream is unchecked."""
        if depth >= ARCHIVE_DEPTH:
            return [Finding(path, 0, 'archive nested too deeply')]
        try:
            with opener(io.BytesIO(data)) as stream:
                content = stream.read(MEMBER_LIMIT + 1)
        except (OSError, EOFError, ValueError, zlib.error, lzma.LZMAError):
            return [Finding(path, 0, 'unreadable archive')]
        if len(content) > MEMBER_LIMIT:
            return [Finding(path, 0, 'too large to read')]
        lower = path.lower()
        ending = next((item for item in suffixes if lower.endswith(item)), None)
        name = (path[:-len(ending)] + ('.tar' if ending.startswith('.t') else '')) if ending else path + '!'
        return self.scan_bytes(content, name, depth + 1)

    def scan_tar(self, data: bytes, path: str, depth: int = 0) -> list[Finding]:
        """Read each regular member of a tar archive within the same bounds as a zip archive."""
        if depth >= ARCHIVE_DEPTH:
            return [Finding(path, 0, 'archive nested too deeply')]
        findings, total = [], 0
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode='r:') as archive:
                for info in archive:
                    member, named = self.redact(info.name)
                    name = f'{path}!{member}'
                    if named:
                        findings.append(Finding(name, 0, 'file path'))
                    if not info.isfile():
                        continue
                    total += info.size
                    if info.size > MEMBER_LIMIT or total > ARCHIVE_LIMIT:
                        findings.append(Finding(name, 0, 'too large to read'))
                        break
                    findings.extend(self.scan_bytes(archive.extractfile(info).read(), name, depth + 1))
        except (tarfile.TarError, OSError, EOFError):
            findings.append(Finding(path, 0, 'unreadable archive'))
        return findings

    def scan_archive(self, data: bytes, path: str, depth: int = 0) -> list[Finding]:
        """Read each member up to MEMBER_LIMIT bytes; whatever cannot be read within the bounds is unchecked."""
        if depth >= ARCHIVE_DEPTH:
            return [Finding(path, 0, 'archive nested too deeply')]
        findings, total = [], 0
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                for info in archive.infolist():
                    member, named = self.redact(info.filename)
                    name = f'{path}!{member}'
                    if named:
                        findings.append(Finding(name, 0, 'file path'))
                    if info.is_dir():
                        continue
                    with archive.open(info) as member:
                        content = member.read(MEMBER_LIMIT + 1)
                    total += len(content)
                    if len(content) > MEMBER_LIMIT or total > ARCHIVE_LIMIT:
                        findings.append(Finding(name, 0, 'too large to read'))
                        break
                    findings.extend(self.scan_bytes(content, name, depth + 1))
        except (zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, NotImplementedError, EOFError, OSError,
                zlib.error):
            findings.append(Finding(path, 0, 'unreadable archive'))
        return findings


def text_of(data: bytes) -> str:
    """The decoded text: UTF-16/32 by byte-order mark or by the NUL pattern of ASCII in UTF-16, otherwise UTF-8.
    Binary files are decoded too, so readable strings in them, such as image metadata, are checked as well."""
    for mark, encoding in TEXT_BOMS:
        if data.startswith(mark):
            return data[len(mark):].decode(encoding, 'replace')
    head = data[:8192]
    if b'\x00' not in head:
        return data.decode('utf-8', 'replace')
    even, odd = head[0::2].count(0), head[1::2].count(0)
    if odd > len(head) // 4 and even * 50 < len(head):
        return data.decode('utf-16-le', 'replace')
    if even > len(head) // 4 and odd * 50 < len(head):
        return data.decode('utf-16-be', 'replace')
    return data.decode('utf-8', 'replace')


def is_archive(data: bytes, path: str) -> bool:
    """A zip by its local-header signature, its file suffix or an end-of-central-directory record."""
    if data[:4] == b'PK\x03\x04' or Path(path).suffix.lower() in ZIP_SUFFIXES:
        return True
    return b'PK\x05\x06' in data[-65_557:] and zipfile.is_zipfile(io.BytesIO(data))


def tracked_files(root: Path) -> list[Path]:
    try:
        listed = subprocess.run(['git', 'ls-files', '-z'], cwd=root, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        skip = {'.git', 'node_modules', 'dist', '.cache', '__pycache__', '.venv', '.wrangler'}
        return [path for path in sorted(root.rglob('*'))
                if path.is_file() and not skip.intersection(path.relative_to(root).parts)]
    return [root / os.fsdecode(name) for name in listed.split(b'\x00') if name]


def files_under(path: Path) -> list[Path]:
    return sorted(item for item in path.rglob('*') if item.is_file()) if path.is_dir() else [path]


def default_paths(root: Path = ROOT) -> list[Path]:
    """Tracked files, generated case pages, then the production build when it exists."""
    paths = sorted(set(tracked_files(root)) | set((root / 'docs/cases').glob('*.md')))
    if (root / 'dist').is_dir():
        paths += files_under(root / 'dist')
    return paths


def scan(paths, root: Path = ROOT, detector: Detector | None = None) -> list[Finding]:
    """Findings for these files: every file, archives included, is read."""
    detector = detector or Detector(SALT, PROTECTED, PARTS)
    findings = []
    for path in paths:
        if not path.is_file():
            continue
        data = path.read_bytes()
        name, named = detector.redact(path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path))
        if named:
            findings.append(Finding(name, 0, 'file path'))
        findings.extend(detector.scan_bytes(data, name))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('paths', nargs='*', type=Path, help='files or directories; default: tracked files and dist/')
    args = parser.parse_args(argv)
    paths = [item for path in args.paths for item in files_under(path.resolve())] if args.paths else default_paths()
    findings = scan(paths)
    for finding in findings:
        print(finding, file=sys.stderr)
    if findings:
        print(f'Privacy check failed: {len(findings)} finding(s). Remove each protected identifier, and never copy '
              'the matched text into commits, pull requests, issues or logs.', file=sys.stderr)
        return 1
    print(f'Privacy check passed: {len(paths)} files, no protected identifiers.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
