#!/usr/bin/env python3
"""Label evidence links the same way on detail pages, /resources/ and /cases/."""
from __future__ import annotations

from html import escape
import re
from urllib.parse import urlsplit


def source_label(url: str, language: str) -> tuple[str, str]:
    """Return a link label and optional context HTML for one evidence URL.

    Only immutable GitHub file/directory links get a compact display label (the path, with any
    line anchor) and a context line naming the repository and revision. Every other URL is shown
    in full; the complete URL always remains the link target and title.
    """
    parsed = urlsplit(url)
    parts = parsed.path.lstrip('/').split('/', 4)
    if (parsed.netloc == 'github.com' and not parsed.query and len(parts) == 5
            and parts[0] and parts[1] and parts[4]
            and parts[2] in {'blob', 'tree'} and re.fullmatch(r'[a-f0-9]{40}', parts[3])):
        owner, repository, _, revision, path = parts
        label = path + ('#' + parsed.fragment if parsed.fragment else '')
        revision_label = '修订' if language == 'zh' else 'Revision'
        context = (f' <span class="entry-source-context">GitHub · {escape(owner + "/" + repository)}'
                   f' · {revision_label} <span title="{revision}">{revision[:7]}</span></span>')
        return label, context
    return url, ''


def evidence_link(url: str, href: str, language: str, *, arrow: bool = False) -> str:
    """Render one evidence link from its validated, escaped href, with the full URL as its title.

    An optional ↗ marker stays inside the link but out of its accessible name.
    """
    label, context = source_label(url, language)
    marker = ' <span aria-hidden="true">↗</span>' if arrow else ''
    return f'<a href="{href}" title="{href}" target="_blank" rel="noopener">{escape(label)}{marker}</a>{context}'
