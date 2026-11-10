"""Small WebP thumbnails of the downloaded demo previews, for listing rows and cards.

Thumbnails need Pillow, which only the publish job installs. Without it, or when one image cannot be read,
that preview keeps its original file and the reason is printed; the build never fails over a thumbnail.
Thumbnails are cached beside the previews, named by the source file's SHA-256, so repeated builds reuse them.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

WIDTH = 480
QUALITY = 78
SUFFIX = '.webp'


def _pillow():
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return None
    return Image, ImageOps


def thumbnail(source: Path, cache: Path) -> Path | None:
    """A WebP of ``source`` at most WIDTH px wide, or None when it cannot be made."""
    modules = _pillow()
    if modules is None:
        return None
    Image, ImageOps = modules
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    target = cache / f'{digest}-{WIDTH}{SUFFIX}'
    if target.is_file():
        return target if target.stat().st_size < source.stat().st_size else None
    try:
        with Image.open(source) as image:
            image.seek(0)  # An animated GIF or WebP gives its first frame; the full file stays linked.
            frame = ImageOps.exif_transpose(image)
            frame = frame.convert('RGBA' if 'A' in frame.getbands() or frame.mode == 'P' else 'RGB')
            if frame.width > WIDTH:
                frame = frame.resize((WIDTH, max(1, round(frame.height * WIDTH / frame.width))), Image.LANCZOS)
            cache.mkdir(parents=True, exist_ok=True)
            partial = target.with_suffix('.part')
            frame.save(partial, 'WEBP', quality=QUALITY, method=6)
            partial.replace(target)
    except Exception as error:  # noqa: BLE001 - any unreadable image falls back to its original
        print(f'Thumbnail skipped for {source.name}: {type(error).__name__}: {error}', file=sys.stderr)
        return None
    # A thumbnail is only worth serving when it is smaller than the original.
    if target.stat().st_size >= source.stat().st_size:
        return None
    return target


def available() -> bool:
    return _pillow() is not None
