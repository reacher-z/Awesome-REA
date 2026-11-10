"""Draw the 1200x630 social cards at build time, in the site's palette and fonts, with the standard library only.

Text comes from scripts/og_glyphs.json, coverage masks of the self-hosted fonts that build_og_glyphs.py
rasterizes; this module composites them onto an RGB canvas and encodes the PNG with zlib. The output depends
only on its inputs, so an unchanged card keeps its bytes and its ?v= revision.
"""
from __future__ import annotations

import base64
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib

GLYPHS = Path(__file__).resolve().parent / 'og_glyphs.json'
WIDTH, HEIGHT = 1200, 630
# site/shell.css, light theme.
PAPER = (0xFA, 0xF3, 0xDD)
GRID = (0xEF, 0xE5, 0xD3)
FRAME = (0xC2, 0xAF, 0xAB)
INK_STRONG = (0x21, 0x26, 0x32)
INK_2 = (0x47, 0x4D, 0x5A)
MAUVE = (0x75, 0x5B, 0x63)
ROSE = (0xF4, 0xAC, 0xB7)
SAGE = (0xE7, 0xEA, 0xDC)
MARGIN = 72
INNER = WIDTH - 2 * MARGIN


@lru_cache(maxsize=1)
def _faces() -> dict:
    return json.loads(GLYPHS.read_text(encoding='utf-8'))


@lru_cache(maxsize=None)
def _mask(face: str, character: str) -> tuple:
    advance, left, top, width, height, data = _faces()[face]['glyphs'][character]
    return advance, left, top, width, height, zlib.decompress(base64.b64decode(data))


def _glyph(face: str, character: str) -> tuple:
    glyphs = _faces()[face]['glyphs']
    if character not in glyphs:
        character = {'‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '-', '·': '-', '…': '.', '→': '>'}.get(character, '?')
        if character not in glyphs:
            character = '?'
    return _mask(face, character)


def measure(face: str, text: str) -> int:
    return round(sum(_glyph(face, character)[0] for character in text))


def wrap(face: str, text: str, width: int) -> list[str]:
    lines, current = [], ''
    for word in text.split():
        candidate = f'{current} {word}' if current else word
        if current and measure(face, candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    return [*lines, current] if current else lines


class Canvas:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT, background=PAPER):
        self.width, self.height = width, height
        self.pixels = bytearray(bytes(background) * (width * height))

    def rect(self, x0: int, y0: int, x1: int, y1: int, color) -> None:
        x0, x1 = max(0, x0), min(self.width, x1)
        row = bytes(color) * max(0, x1 - x0)
        for y in range(max(0, y0), min(self.height, y1)):
            start = (y * self.width + x0) * 3
            self.pixels[start:start + len(row)] = row

    def blend(self, x: int, y: int, color, alpha: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height and alpha:
            i = (y * self.width + x) * 3
            p = self.pixels
            for c in range(3):
                p[i + c] = (color[c] * alpha + p[i + c] * (255 - alpha) + 127) // 255

    def text(self, face: str, text: str, x: int, top: int, color) -> int:
        """Draw ``text`` with its line box starting at ``top``; return the advance width."""
        pen = float(x)
        for character in text:
            advance, left, glyph_top, width, height, data = _glyph(face, character)
            origin_x, origin_y = round(pen) + left, top + glyph_top
            for row in range(height):
                line = data[row * width:(row + 1) * width]
                for column, alpha in enumerate(line):
                    if alpha:
                        self.blend(origin_x + column, origin_y + row, color, alpha)
            pen += advance
        return round(pen - x)

    def ring(self, cx: float, cy: float, radius: float, thickness: float, color) -> None:
        reach = int(radius + thickness) + 2
        for y in range(int(cy) - reach, int(cy) + reach + 1):
            for x in range(int(cx) - reach, int(cx) + reach + 1):
                distance = abs(((x + .5 - cx) ** 2 + (y + .5 - cy) ** 2) ** .5 - radius)
                coverage = max(0.0, min(1.0, thickness / 2 + .5 - distance))
                self.blend(x, y, color, int(coverage * 255))

    def png(self) -> bytes:
        def chunk(kind: bytes, body: bytes) -> bytes:
            return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xFFFFFFFF)
        stride = self.width * 3
        raw = b''.join(b'\x00' + bytes(self.pixels[y * stride:(y + 1) * stride]) for y in range(self.height))
        header = struct.pack('>IIBBBBB', self.width, self.height, 8, 2, 0, 0, 0)
        return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')


def _paper(canvas: Canvas) -> None:
    """Blueprint grid inside a drafted frame, as on the site's title blocks."""
    for x in range(0, WIDTH, 30):
        canvas.rect(x, 0, x + 1, HEIGHT, GRID)
    for y in range(0, HEIGHT, 30):
        canvas.rect(0, y, WIDTH, y + 1, GRID)
    canvas.rect(36, 36, WIDTH - 36, 38, FRAME)
    canvas.rect(36, HEIGHT - 38, WIDTH - 36, HEIGHT - 36, FRAME)
    canvas.rect(36, 36, 38, HEIGHT - 36, FRAME)
    canvas.rect(WIDTH - 38, 36, WIDTH - 36, HEIGHT - 36, FRAME)


def _masthead(canvas: Canvas) -> None:
    cx, cy = MARGIN + 16, 92
    canvas.ring(cx, cy, 11, 2.2, MAUVE)
    canvas.rect(cx - 17, cy - 1, cx + 18, cy + 1, MAUVE)
    canvas.rect(cx - 1, cy - 17, cx + 1, cy + 18, MAUVE)
    x = MARGIN + 46
    x += canvas.text('wordmark', 'Awesome ', x, 62, INK_STRONG)
    canvas.text('accent', 'REA', x, 62, MAUVE)
    domain = 'AWESOMEREA.ORG'
    canvas.text('mono', domain, WIDTH - MARGIN - measure('mono', domain), 80, INK_2)


def render_card(*, eyebrow: str, title: str, subtitle: str = '', footer: tuple[str, ...] = ()) -> bytes:
    """One card: masthead, eyebrow, display title (two lines at most), a subtitle and a title-block footer strip."""
    canvas = Canvas()
    _paper(canvas)
    _masthead(canvas)
    face = 'display'
    lines = wrap(face, title, INNER)
    if len(lines) > 2 or any(measure(face, line) > INNER for line in lines):
        face = 'display-small'
        lines = wrap(face, title, INNER)[:2]
    line_height = 104 if face == 'display' else 80
    subtitle_lines = wrap('sans', subtitle, INNER - 80)[:2] if subtitle else []
    block = 38 + len(lines) * line_height + (20 + 42 * len(subtitle_lines) if subtitle_lines else 0)
    top = 150 + max(0, (370 - block) // 2)
    canvas.rect(MARGIN, top + 4, MARGIN + 12, top + 16, ROSE)
    canvas.text('mono', eyebrow.upper(), MARGIN + 24, top - 2, MAUVE)
    y = top + 38 - (14 if face == 'display' else 8)
    for line in lines:
        canvas.text(face, line, MARGIN - 4, y, INK_STRONG)
        y += line_height
    y += 20 if face == 'display' else 16
    for line in subtitle_lines:
        canvas.text('sans', line, MARGIN, y, INK_2)
        y += 42
    # Title-block strip: a sage band with mono cells, like the site footer.
    canvas.rect(38, 520, WIDTH - 38, HEIGHT - 38, SAGE)
    canvas.rect(38, 520, WIDTH - 38, 522, FRAME)
    x = MARGIN
    for index, cell in enumerate(footer):
        if index:
            canvas.rect(x - 28, 522, x - 26, HEIGHT - 38, FRAME)
        x += canvas.text('mono', cell.upper(), x, 544, INK_STRONG if index == 0 else INK_2) + 56
    return canvas.png()


def card_slug(value: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    if not slug:
        raise ValueError('Social cards need a nonempty slug')
    return slug


def write_card(output: Path, slug: str, site_url: str, **card) -> str:
    """Write /og/<slug>.png and return its absolute URL with a content revision."""
    data = render_card(**card)
    path = Path(output) / 'og' / f'{card_slug(slug)}.png'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return f'{site_url}/og/{card_slug(slug)}.png?v={hashlib.sha256(data).hexdigest()[:16]}'
