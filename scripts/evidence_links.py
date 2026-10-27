#!/usr/bin/env python3
"""Label evidence links the same way on detail pages and the paper directory."""
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


def accessible_name(url: str, language: str) -> str | None:
    """Name a compact link by its visible path plus repository and revision, so paths such as
    README.md stay distinct in link lists; full-URL labels need no separate name."""
    label, context = source_label(url, language)
    if not context:
        return None
    owner, repository, _, revision, _ = urlsplit(url).path.lstrip('/').split('/', 4)
    if language == 'zh':
        return f'{label}，GitHub {owner}/{repository}，修订 {revision[:7]}'
    return f'{label}, GitHub {owner}/{repository}, revision {revision[:7]}'


def evidence_link(url: str, href: str, language: str) -> str:
    """Render one evidence link from its validated, escaped href, with the full URL as its title."""
    label, context = source_label(url, language)
    name = accessible_name(url, language)
    aria = f' aria-label="{escape(name, quote=True)}"' if name else ''
    return f'<a href="{href}" title="{href}" target="_blank" rel="noopener"{aria}>{escape(label)}</a>{context}'
