"""Small WebP thumbnails of the downloaded demo previews, for /resources/ listing rows.

Thumbnails need Pillow with WebP support, pinned in scripts/publish-requirements.txt and installed only by the
publication and IndexNow builds. Without it, or when one image cannot be read, that preview keeps its original file
and the reason is printed; the build never fails over a thumbnail. Thumbnails are cached beside the previews, named
by the source file's SHA-256 and the encoding settings, so repeated builds reuse them.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys
import tempfile

WIDTH = 480
QUALITY = 78
# Bump when the conversion changes, so cached thumbnails are made again.
VERSION = 1
SUFFIX = '.webp'
# Rows show previews in a 16:9 box with object-fit: cover, so a taller image only ever shows its middle band.
ASPECT = 16 / 9


def _pillow():
    try:
        from PIL import Image, ImageOps, features
    except ImportError:
        return None
    if not features.check('webp'):
        return None
    return Image, ImageOps


def _frame(image, Image, ImageOps):
    """The first frame, upright, in RGB or RGBA, cropped to the band the row shows and at most WIDTH px wide."""
    image.seek(0)  # An animated GIF or WebP gives its first frame; the full file stays linked.
    frame = ImageOps.exif_transpose(image)
    if frame.mode.startswith('I'):
        # 16-bit greyscale: scale to 8 bits rather than clip.
        frame = frame.convert('I').point(lambda value: value * (1 / 256)).convert('L')
    elif frame.mode == 'F':
        frame = frame.convert('L')
    transparent = 'A' in frame.getbands() or 'transparency' in frame.info
    frame = frame.convert('RGBA' if transparent else 'RGB')
    tallest = round(frame.width / ASPECT)
    if frame.height > tallest:
        top = (frame.height - tallest) // 2
        frame = frame.crop((0, top, frame.width, top + tallest))
    if frame.width > WIDTH:
        frame = frame.resize((WIDTH, max(1, round(frame.height * WIDTH / frame.width))), Image.LANCZOS)
    return frame


def thumbnail(source: Path, cache: Path) -> Path | None:
    """A WebP of ``source`` at most WIDTH px wide and smaller than it, or None when it cannot be made."""
    modules = _pillow()
    if modules is None:
        return None
    Image, ImageOps = modules
    partial = None
    try:
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        target = cache / f'{digest}-w{WIDTH}-q{QUALITY}-v{VERSION}{SUFFIX}'
        if not target.is_file():
            with Image.open(source) as image:
                frame = _frame(image, Image, ImageOps)
            cache.mkdir(parents=True, exist_ok=True)
            # A unique temporary name keeps two builds sharing the cache from writing into one file.
            handle, partial = tempfile.mkstemp(dir=cache, suffix='.part')
            os.close(handle)
            frame.save(partial, 'WEBP', quality=QUALITY, method=6)
            os.replace(partial, target)
            partial = None
        # A thumbnail is only worth serving when it is smaller than the original.
        return target if target.stat().st_size < source.stat().st_size else None
    except Exception as error:  # noqa: BLE001 - any unreadable image falls back to its original
        print(f'Thumbnail skipped for {source.name}: {type(error).__name__}: {error}', file=sys.stderr)
        return None
    finally:
        if partial is not None:
            Path(partial).unlink(missing_ok=True)


def available() -> bool:
    return _pillow() is not None
