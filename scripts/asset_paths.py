"""Content-addressed stylesheet and script paths, which site/_headers caches for a year.

Cloudflare Pages header rules match paths, not query strings, so a changed file gets a new name under
/assets/ instead of a new ?v= query. HTML and JSON keep their revalidation rules.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import shutil

ASSET_DIRECTORY = 'assets'
FINGERPRINTED_SUFFIXES = ('.css', '.js')
# The licensed icon stylesheet keeps its name: the icon-origin deployment and its relative font URLs use it.
UNHASHED_STYLESHEETS = frozenset({'fontawesome.css'})
ASSET_PATH = re.compile(r'/assets/(?P<stem>[a-z0-9-]+)\.(?P<digest>[0-9a-f]{16})(?P<suffix>\.css|\.js)')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def fingerprinted_href(site_dir: Path, filename: str) -> str:
    """Copy site_dir/filename to /assets/<stem>.<sha256 prefix><suffix> and return that root-relative URL.

    A missing file keeps its plain root URL, as the page builders do when they run without site assets."""
    source = Path(site_dir) / filename
    if not source.is_file():
        return '/' + filename
    name = f'{source.stem}.{digest(source.read_bytes())}{source.suffix}'
    target = Path(site_dir) / ASSET_DIRECTORY / name
    target.parent.mkdir(exist_ok=True)
    if not target.is_file():
        shutil.copy2(source, target)
    return f'/{ASSET_DIRECTORY}/{name}'


def remove_unhashed_copies(site_dir: Path, filenames) -> None:
    """Delete root copies of stylesheets and scripts that already have a content-addressed copy under /assets/."""
    for filename in filenames:
        path = Path(site_dir) / filename
        if path.suffix not in FINGERPRINTED_SUFFIXES or filename in UNHASHED_STYLESHEETS or not path.is_file():
            continue
        if (Path(site_dir) / ASSET_DIRECTORY / f'{path.stem}.{digest(path.read_bytes())}{path.suffix}').is_file():
            path.unlink()
