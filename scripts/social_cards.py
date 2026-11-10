"""Give the homepage, listings, categories and entry pages their own social cards.

After every page is written, write_social_cards() draws one card per destination with og_images.py into
/og/ and points each page's og:image, twitter:image and their alt texts at it. Homepages, /resources/,
/cases/, /papers/, the survey and every /browse/ category get their own card; a resource page uses the card
of its collection section, and a paper page the papers card. Pages without a card here keep social-card.png.
"""
from __future__ import annotations

from collections import Counter
from html import escape
from pathlib import Path
import re

from og_images import write_card

META = re.compile(r'<meta (property|name)="(og:image|og:image:alt|twitter:image|twitter:image:alt)" content="[^"]*">')


def _number(value: int, zh: bool) -> str:
    return f'{value:,}' if not zh else str(value)


def _cards(resources, papers, sections, section_of, browse_categories, browse_counts, survey_title, survey_papers):
    """Card text per key: English on the card, alt text in both languages."""
    sections_count = Counter(section_of(record) for record in resources)
    cases = sum(record['kind'] == 'case-study' for record in resources)
    cards = {
        'home': dict(eyebrow='Reverse engineering catalog', title='Awesome Reverse Engineering Anything',
                     subtitle='Tools, case studies and papers for websites, games, apps, binaries, firmware and protocols.',
                     footer=(f'{len(resources):,} resources', f'{len(papers):,} papers'),
                     zh=('逆向工程目录', f'{len(resources)} 项资源、{len(papers)} 篇论文')),
        'resources': dict(eyebrow='Curated resources', title='Tools, projects and case studies',
                          subtitle='Every entry links its primary sources and the date they were reviewed.',
                          footer=(f'{len(resources):,} resources', f'{len(sections)} sections'),
                          zh=('精选资源', f'{len(resources)} 项资源，{len(sections)} 个分区')),
        'cases': dict(eyebrow='Case studies', title='Reverse-engineering case studies',
                      subtitle='Decompilations, recompilations, ports and protocol reconstructions.',
                      footer=(f'{cases:,} cases',), zh=('案例合集', f'{cases} 个案例')),
        'papers': dict(eyebrow='Research papers', title='Reverse engineering papers and benchmarks',
                       subtitle='Venue, status and date precision as published, with code links.',
                       footer=(f'{len(papers):,} papers',), zh=('研究论文', f'{len(papers)} 篇论文')),
        'survey': dict(eyebrow='Editorial survey', title=survey_title, subtitle='',
                       footer=(f'{survey_papers:,} papers in the snapshot',), zh=('综述', f'快照中 {survey_papers} 篇论文')),
        'browse': dict(eyebrow='Repository directory', title='Browse repositories by category',
                       subtitle='', footer=(f'{len(browse_categories)} categories', f'{sum(browse_counts.values()):,} repositories'),
                       zh=('仓库目录', f'{len(browse_categories)} 个分类，{sum(browse_counts.values())} 个仓库')),
    }
    for slug, (name, _) in sections.items():
        count = sections_count.get(slug, 0)
        cards[f'section-{slug}'] = dict(eyebrow='Category', title=name, subtitle='',
                                        footer=(f'{count:,} curated entries', 'awesomerea.org/resources/'),
                                        zh=('分类', f'{count} 项精选条目'))
    for slug, (name, _) in browse_categories.items():
        count = browse_counts.get(slug, 0)
        cards[f'browse-{slug}'] = dict(eyebrow='Repository category', title=name, subtitle='',
                                       footer=(f'{count:,} repositories', 'awesomerea.org/browse/'),
                                       zh=('仓库分类', f'{count} 个仓库'))
    return cards


def _alt(card: dict, language: str) -> str:
    if language == 'zh':
        eyebrow, facts = card['zh']
        return f'Awesome REA 分享图：{eyebrow}“{card["title"]}”，{facts}。'
    return f'Awesome REA card: {card["eyebrow"].lower()} “{card["title"]}”, {", ".join(card["footer"])}.'


def _card_key(relative: str, resource_sections: dict, browse_categories) -> str | None:
    parts = relative.removeprefix('zh/').split('/')
    if parts[-1] != 'index.html':
        return None
    parts = parts[:-1]
    if parts in ([], ['explore']):
        return 'home'
    head = parts[0]
    if head == 'resources':
        if len(parts) == 2 and parts[1] in resource_sections:
            return f'section-{resource_sections[parts[1]]}'
        return 'resources'
    if head in ('cases', 'papers', 'survey'):
        return head
    if head == 'browse':
        return f'browse-{parts[1]}' if len(parts) == 2 and parts[1] in browse_categories else 'browse'
    return None


def write_social_cards(output: Path, *, resources, papers, sections, section_of, browse_categories,
                       browse_counts, survey_title, survey_papers, site_url) -> int:
    """Draw the cards and repoint every matching page; return how many pages changed."""
    output = Path(output)
    cards = _cards(resources, papers, sections, section_of, browse_categories, browse_counts, survey_title, survey_papers)
    urls = {}
    resource_sections = {record['id']: section_of(record) for record in resources}
    changed = 0
    for page in sorted(output.rglob('index.html')):
        relative = page.relative_to(output).as_posix()
        key = _card_key(relative, resource_sections, browse_categories)
        if key is None or key not in cards:
            continue
        html = page.read_text(encoding='utf-8')
        if 'property="og:image"' not in html:
            continue
        if key not in urls:
            card = {name: value for name, value in cards[key].items() if name != 'zh'}
            urls[key] = write_card(output, key, site_url, **card)
        language = 'zh' if relative.startswith('zh/') else 'en'
        values = {'og:image': urls[key], 'twitter:image': urls[key],
                  'og:image:alt': _alt(cards[key], language), 'twitter:image:alt': _alt(cards[key], language)}
        updated = META.sub(lambda m: f'<meta {m[1]}="{m[2]}" content="{escape(values[m[2]], quote=True)}">', html)
        if updated != html:
            page.write_text(updated, encoding='utf-8')
            changed += 1
    return changed
