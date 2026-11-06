"""Page titles and meta descriptions: one separator and one length rule for every generated page.

Search results show about 60 characters of a title and 160 of a description, so the head of a page
carries a fitted version of its text. The full text stays in the visible page and in JSON-LD.
"""
from __future__ import annotations

import re

SEPARATOR = ' · '
SITE_SUFFIX = 'AwesomeREA.org'
TITLE_MAX = 60
DESCRIPTION_MIN = 70
DESCRIPTION_MAX = 160
ELLIPSIS = '…'
# CJK punctuation ends a sentence by itself; ASCII punctuation only before a space, so v1.2 stays whole.
_SENTENCE_END = re.compile(r'[。！？；]|[.!?;](?=\s)')
_BREAK = re.compile(r'\s|[，、：]')
_TRAILING = ' ,;:，、；：-–—·'
_CJK = re.compile(r'[　-〿㐀-鿿＀-￯]')


def _clean(text: str) -> str:
    return ' '.join(text.split())


def shorten(text: str, limit: int) -> str:
    """Cut text to at most ``limit`` characters at the last word or clause break, marked with an ellipsis."""
    text = _clean(text)
    if len(text) <= limit:
        return text
    room = text[:limit - len(ELLIPSIS)]
    breaks = [match.start() for match in _BREAK.finditer(room)]
    cut = breaks[-1] if breaks and breaks[-1] >= limit // 2 else len(room)
    return room[:cut].rstrip(_TRAILING) + ELLIPSIS


def page_title(name: str, context: str | None = None, *, keep_context: bool = False) -> str:
    """The longest of name · context · site, name · context, name · site and name that fits.

    A name too long even alone is shortened. ``keep_context`` never gives up the context, for pages whose
    title needs it, such as the Chinese category that a Chinese page with an English name relies on.
    """
    name = _clean(name)
    options = [(name, SITE_SUFFIX), (name,)]
    if context:
        options[:0] = [(name, context, SITE_SUFFIX), (name, context)]
        if keep_context:
            options = options[:2]
    for parts in options:
        title = SEPARATOR.join(parts)
        if len(title) <= TITLE_MAX:
            return title
    if context and keep_context:
        return SEPARATOR.join((shorten(name, TITLE_MAX - len(SEPARATOR) - len(context)), context))
    return shorten(name, TITLE_MAX)


def meta_description(text: str, *facts: str) -> str:
    """Fit text to 70–160 characters: recorded facts extend a short text, a long one ends at a sentence."""
    result = _clean(text)
    for fact in facts:
        if len(result) >= DESCRIPTION_MIN:
            break
        chinese = bool(_CJK.search(result[-1:]))
        if not re.search(r'[.!?。！？]$', result):
            result += '。' if chinese else '.'
        result += ('' if chinese else ' ') + _clean(fact)
    if len(result) <= DESCRIPTION_MAX:
        return result
    ends = [match.end() for match in _SENTENCE_END.finditer(result[:DESCRIPTION_MAX])]
    if ends and ends[-1] >= DESCRIPTION_MIN:
        return result[:ends[-1]].rstrip()
    return shorten(result, DESCRIPTION_MAX)


def resource_description(record: dict, language: str, category: str) -> str:
    """A curated resource's meta description; every added fact comes from its record or its page."""
    reviewed = record['verified_at'][:10]
    if language == 'zh':
        return meta_description(record['description_zh'], f'Awesome REA 精选目录“{category}”分类收录，{reviewed} 完成来源复核。',
                                '条目页列出使用要求、一手证据与相关内容。')
    return meta_description(record['description_en'], f'Listed under {category} in the Awesome REA catalog; sources reviewed {reviewed}.')


def paper_description(record: dict, language: str) -> str:
    """A paper's meta description; the venue and year are the recorded ones."""
    if language == 'zh':
        return meta_description(record['description_zh'], f'Awesome REA 论文目录收录：{record["venue"]}（{record["year"]}），来源已复核。')
    return meta_description(record['description_en'], f'Listed in the Awesome REA bibliography: {record["venue"]}, {record["year"]}.')


def title_problem(title: str) -> str | None:
    """Why a page title breaks the shared rules, if it does."""
    if len(title) > TITLE_MAX:
        return f'title has {len(title)} characters, over {TITLE_MAX}'
    if ' | ' in title:
        return f'title separator must be "{SEPARATOR.strip()}"'
    return None


def description_problem(description: str) -> str | None:
    """Why a meta description breaks the length rule, if it does."""
    if not DESCRIPTION_MIN <= len(description) <= DESCRIPTION_MAX:
        return f'description has {len(description)} characters, outside {DESCRIPTION_MIN}–{DESCRIPTION_MAX}'
    return None
