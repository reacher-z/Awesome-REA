"""Markdown twins for the indexed pages that no builder writes one for.

Listings, categories and entries get a twin from their own builder (agent_formats.py). Every other page in the
sitemap, such as the homepages, the survey, /about/ and /contribute/, gets one here after all pages are written:
its <main> converted to Markdown (headings, paragraphs, lists, tables, code and links), opening with the H1 and
the page's address, plus the `<link rel="alternate" type="text/markdown">` that announces it.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urljoin

from agent_formats import MARKDOWN, MARKDOWN_TYPE

# Controls, scripts and their labels; live star counts (data-stars) stay out so a twin depends only on the data.
SKIP = {'script', 'style', 'svg', 'template', 'noscript', 'button', 'form', 'select', 'textarea', 'dialog', 'label', 'legend'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
BLOCKS = {'p', 'div', 'section', 'article', 'header', 'footer', 'nav', 'aside', 'figure', 'figcaption', 'dl', 'dt', 'dd',
          'details', 'summary', 'ul', 'ol', 'table', 'blockquote'}


class _Markdown(HTMLParser):
    """Collect <main> as Markdown lines; everything outside <main> is ignored."""

    def __init__(self, base: str):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.lines: list[str] = []
        self.buffer: list[str] = []
        self.depth = 0           # inside <main>
        self.hidden = 0
        self.lists: list[str] = []
        self.heading = 0
        self.links: list[str | None] = []
        self.pre = False
        self.row: list[str] | None = None
        self.rows: list[list[str]] = []
        self.header_cells = 0
        self.h1: str | None = None

    def flush(self, prefix: str = '') -> None:
        text = re.sub(r'\s+', ' ', ''.join(self.buffer)).strip()
        self.buffer = []
        if text:
            self.lines += [prefix + text, '']

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'main':
            self.depth += 1
            return
        if not self.depth:
            return
        if self.hidden:
            self.hidden += tag not in VOID
            return
        if (tag in SKIP or 'hidden' in values or values.get('aria-hidden') == 'true' or values.get('role') == 'tooltip'
                or 'data-stars' in values or 'star-btn' in (values.get('class') or '').split()):
            self.hidden += tag not in VOID
            return
        if re.fullmatch(r'h[1-6]', tag):
            self.flush()
            self.heading = int(tag[1])
        elif tag in ('ul', 'ol'):
            self.flush(self._indent())
            self.lists.append(tag)
        elif tag == 'li':
            self.flush(self._indent())
        elif tag == 'tr':
            self.row = []
        elif tag in ('td', 'th'):
            self.buffer = []
            if tag == 'th' and not self.rows:
                self.header_cells += 1
        elif tag == 'pre':
            self.flush()
            self.pre = True
        elif tag == 'br':
            self.buffer.append(' ')
        elif tag == 'a':
            href = values.get('href')
            self.links.append(urljoin(self.base, href) if href and not href.startswith(('#', 'javascript:')) else None)
            self.buffer.append('[')
        elif tag == 'code' and not self.pre:
            self.buffer.append('`')
        elif tag in ('span', 'time', 'data') and not self.pre:
            self.buffer.append(' ')
        elif tag in BLOCKS and self.row is None:
            self.flush(self._indent())

    def handle_endtag(self, tag):
        if tag == 'main':
            self.flush()
            self.depth -= 1
            return
        if not self.depth:
            return
        if self.hidden:
            self.hidden -= 1
            return
        if re.fullmatch(r'h[1-6]', tag) and self.heading:
            text = re.sub(r'\s+', ' ', ''.join(self.buffer)).strip()
            if self.heading == 1 and self.h1 is None:
                self.h1 = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
                self.buffer = []
            else:
                self.flush('#' * max(2, self.heading) + ' ')
            self.heading = 0
        elif tag in ('ul', 'ol'):
            self.flush(self._indent())
            if self.lists:
                self.lists.pop()
        elif tag == 'li':
            self.flush(self._indent())
        elif tag in ('td', 'th') and self.row is not None:
            self.row.append(re.sub(r'\s+', ' ', ''.join(self.buffer)).strip().replace('|', '\\|'))
            self.buffer = []
        elif tag == 'tr' and self.row is not None:
            if any(self.row):
                self.rows.append(self.row)
            self.row = None
        elif tag == 'table':
            self._table()
        elif tag == 'pre':
            code = ''.join(self.buffer).strip('\n')
            self.buffer = []
            self.pre = False
            if code.strip():
                self.lines += ['```', code, '```', '']
        elif tag == 'a' and self.links:
            href = self.links.pop()
            label = ''.join(self.buffer)
            start = label.rfind('[')
            inner = re.sub(r'\s+', ' ', label[start + 1:]).strip()
            self.buffer = [label[:start], (f'[{inner}]({href})' if href and inner else inner) + ' ']
        elif tag == 'code' and not self.pre:
            self.buffer.append('`')
        elif tag in ('span', 'time', 'data') and not self.pre:
            # Inline boxes that the stylesheet separates ("53" "papers in the snapshot").
            self.buffer.append(' ')
        elif tag in BLOCKS and self.row is None:
            self.flush(self._indent())

    def handle_data(self, data):
        if self.depth and not self.hidden:
            self.buffer.append(data)

    def _indent(self) -> str:
        return '  ' * (len(self.lists) - 1) + '- ' if self.lists else ''

    def _table(self) -> None:
        rows, self.rows, self.header_cells = self.rows, [], 0
        if not rows:
            return
        width = max(len(row) for row in rows)
        rows = [row + [''] * (width - len(row)) for row in rows]
        self.lines += ['| ' + ' | '.join(rows[0]) + ' |', '|' + ' --- |' * width]
        self.lines += ['| ' + ' | '.join(row) + ' |' for row in rows[1:]]
        self.lines.append('')


def page_markdown(html: str, canonical: str, language: str) -> str | None:
    """The page's <main> as Markdown, or None when it has no <main> or no H1."""
    parser = _Markdown(canonical)
    parser.feed(html)
    parser.close()
    if not parser.h1:
        return None
    body = re.sub(r'\n{3,}', '\n\n', '\n'.join(parser.lines)).strip()
    address = ('- 网页：' if language == 'zh' else '- HTML: ') + f'<{canonical}>'
    return f'# {parser.h1}\n\n{address}\n\n{body}\n'


def write_page_twins(output: Path, routes: list[str], site_url: str) -> list[str]:
    """Write a twin for every indexed route whose page links none; return the routes that got one."""
    output = Path(output)
    added = []
    for route in routes:
        page = output / route.lstrip('/') / 'index.html'
        if not route.endswith('/') or not page.is_file():
            continue
        html = page.read_text(encoding='utf-8')
        head, separator, rest = html.partition('</head>')
        if not separator or f'type="{MARKDOWN_TYPE}"' in head:
            continue
        markdown = page_markdown(html, site_url + route, 'zh' if route.startswith('/zh/') else 'en')
        if markdown is None:
            continue
        (page.parent / MARKDOWN).write_text(markdown, encoding='utf-8')
        link = f'<link rel="alternate" type="{MARKDOWN_TYPE}" href="{route}{MARKDOWN}" title="Markdown">'
        page.write_text(head + link + '\n' + separator + rest, encoding='utf-8')
        added.append(route)
    return added
