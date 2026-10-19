"""Label each requirements item of a curated record with one facet from a fixed vocabulary.

`requirement_facets` is a list of facet IDs parallel to `requirements`; the Chinese items in
translations.zh-CN.json (or `requirements_zh`) share it, so both languages carry the same facet.
Renderers show the facet as a lead-in and list prerequisites first; item text is never changed.
"""
from __future__ import annotations

from html import escape

# Order is the documentation order; renderers only move prerequisites to the front.
FACETS = {
    'prerequisites': ('Prerequisites', '前提条件'),
    'scope': ('Scope', '范围'),
    'limits': ('Limits', '局限'),
    'testing': ('Testing evidence', '测试证据'),
    'license': ('License', '许可'),
    'attribution': ('Attribution', '署名'),
}
# Kinds whose every requirements item must carry a facet; other records may add them.
REQUIRED_KINDS = {'case-study'}


def _items(value) -> list:
    return [value] if isinstance(value, str) else value if isinstance(value, list) else []


def facet_errors(record: dict, chinese_items) -> list[str]:
    """Return validation messages for one record's facets against its English and Chinese items."""
    facets = record.get('requirement_facets')
    if facets is None:
        return ['requirement_facets: label every requirements item (see data/README.md)'] if record.get('kind') in REQUIRED_KINDS else []
    if not isinstance(facets, list) or not facets or not all(isinstance(facet, str) for facet in facets):
        return ['requirement_facets: use a nonempty list of facet IDs']
    errors = [f'requirement_facets: unknown facet {facet!r}; use one of ' + ', '.join(FACETS)
              for facet in dict.fromkeys(facets) if facet not in FACETS]
    english, chinese = _items(record.get('requirements')), _items(chinese_items)
    if len(facets) != len(english):
        errors.append(f'requirement_facets: {len(facets)} facets for {len(english)} English requirements items')
    if len(chinese) != len(english):
        errors.append(f'requirement_facets: {len(chinese)} Chinese requirements items for {len(english)} English ones, so facets cannot match both languages')
    return errors


def ordered_items(record: dict, items: list[str]) -> list[tuple[str | None, str]]:
    """Pair items with their facets, prerequisites first and otherwise in source order."""
    facets = record.get('requirement_facets') or [None] * len(items)
    pairs = list(zip(facets, items))
    return [pair for pair in pairs if pair[0] == 'prerequisites'] + [pair for pair in pairs if pair[0] != 'prerequisites']


def item_html(facet: str | None, text: str, language: str) -> str:
    """One list item; a labelled item opens with its localized facet in bold."""
    if facet is None:
        return f'<li>{escape(text)}</li>'
    label = FACETS[facet][language == 'zh']
    lead = f'{label}：' if language == 'zh' else f'{label}: '
    return f'<li><strong class="requirement-facet">{escape(lead)}</strong>{escape(text)}</li>'
