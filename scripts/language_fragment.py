"""Let static pages keep the current card or section when a reader switches language."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

SCRIPT = 'language-fragment.js'
HEADER = re.compile(r'<header class="site-header">.*?</header>', re.S)
# The homepages keep their fragment, query and layout through app.js instead.
HOMEPAGES = {'index.html', 'zh/index.html'}


def language_fragment_script(site_dir: Path) -> str:
    """Return the deferred, revisioned tag for the copy of site/language-fragment.js in site_dir."""
    revision = hashlib.sha256((Path(site_dir) / SCRIPT).read_bytes()).hexdigest()[:16]
    return f'<script src="/{SCRIPT}?v={revision}" defer></script>'


def add_language_fragment_script(site_dir: Path) -> int:
    """Load the script on every generated page whose site header has a language link; return the page count.

    The ordinary link already opens the counterpart page without JavaScript; the script only adds a fragment
    that names an element on the current page, relying on both language versions sharing their IDs.
    """
    site_dir = Path(site_dir)
    tag = language_fragment_script(site_dir)
    pages = 0
    for page in sorted(site_dir.rglob('*.html')):
        if page.relative_to(site_dir).as_posix() in HOMEPAGES:
            continue
        html = page.read_text(encoding='utf-8')
        header = HEADER.search(html)
        if not header or 'hreflang=' not in header.group(0):
            continue
        if html.count('</head>') != 1 or tag in html:
            raise ValueError(f'{page}: expected one head without the language fragment script')
        page.write_text(html.replace('</head>', tag + '\n</head>'), encoding='utf-8')
        pages += 1
    return pages
