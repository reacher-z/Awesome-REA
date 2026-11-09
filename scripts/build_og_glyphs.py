#!/usr/bin/env python3
"""Rasterize the site's own fonts into scripts/og_glyphs.json for the social-card renderer.

og_images.py draws the 1200x630 cards during every build without third-party packages; it needs the glyphs
as coverage masks. Run this once with Pillow installed after changing a face, a size or the character set
below; the build only reads the JSON it writes.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / 'site/fonts'
OUTPUT = Path(__file__).resolve().parent / 'og_glyphs.json'
CHARACTERS = ''.join(chr(code) for code in range(32, 127)) + '·–—‘’“”…→'
# Face name: (font file, pixel size). Sizes match og_images.py's layout.
FACES = {
    'display': ('eb-garamond-500-core.woff2', 96),
    'display-small': ('eb-garamond-500-core.woff2', 72),
    'wordmark': ('eb-garamond-500-core.woff2', 44),
    'accent': ('eb-garamond-italic-display.woff2', 44),
    'sans': ('ibm-plex-sans-core.woff2', 30),
    'mono': ('ibm-plex-mono-medium.woff2', 20),
}


def main() -> int:
    from PIL import ImageFont
    from fontTools.ttLib import TTFont
    document = {}
    for face, (filename, size) in FACES.items():
        path = FONTS / filename
        font = ImageFont.truetype(str(path), size)
        covered = TTFont(str(path)).getBestCmap()
        ascent, descent = font.getmetrics()
        glyphs = {}
        for character in CHARACTERS:
            if ord(character) not in covered:
                continue
            left, top, right, bottom = font.getbbox(character)
            mask = font.getmask(character)
            width, height = mask.size
            data = bytes(mask) if width and height else b''
            glyphs[character] = [round(font.getlength(character), 3), left, top, width, height,
                                 base64.b64encode(zlib.compress(data, 9)).decode('ascii')]
        document[face] = {'file': filename, 'size': size, 'ascent': ascent, 'descent': descent, 'glyphs': glyphs}
    OUTPUT.write_text(json.dumps(document, separators=(',', ':'), sort_keys=True) + '\n', encoding='utf-8')
    print(f'Wrote {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} bytes).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
