"""The site's file for agents (/AGENTS.md, /agents.md, /agents.txt) and the front matter of every Markdown twin.

The repository's own AGENTS.md instructs contributors; the site file lists read commands and facts for agents
that read the catalog. Counts and dates arrive from the build, so the file always matches the pages.
"""
from __future__ import annotations

import re
from pathlib import Path

from sitemaps import dated_path, english_path

BRAND = 'Awesome REA (Awesome Reverse Engineering Anything)'
AGENT_FILES = ('AGENTS.md', 'agents.md', 'agents.txt')
SKIP_TWINS = ('downloads',)


def agents_markdown(site_url: str, repository_url: str, *, resources: int, papers: int, cases: int, repositories: int,
                    updated: str, faq: str = '') -> str:
    s = site_url.rstrip('/')
    return f'''# Awesome REA (Awesome Reverse Engineering Anything): agent guide

> Awesome REA (AwesomeREA.org) is a bilingual (English, Simplified Chinese) catalog of {resources:,} source-reviewed tools, projects, integrations and case studies ({cases:,} of them cases) and {papers:,} research papers on reverse engineering websites, games, apps, native binaries, firmware and communication protocols. It also indexes {repositories:,} browsable repositories found by automated README scans. Data updated {updated}.

## Read an item as Markdown

Every page has a Markdown twin at `<page URL>index.md`, with a YAML front-matter block (title, url, updated, type).

```sh
# curl -sL {s}/<kind>/<id>/index.md
curl -sL {s}/resources/ghidra/index.md
curl -sL {s}/papers/paper-reveree/index.md
curl -sL {s}/zh/resources/ghidra/index.md
```

`<kind>` is `resources` or `papers`; `<id>` is the stable catalog ID from the JSON API or from the URL of the HTML page. Listings, categories and guides follow the same pattern.

```sh
curl -sL {s}/resources/index.md     # all curated resources by section
curl -sL {s}/papers/index.md        # the bibliography
curl -sL {s}/browse/index.md        # repository categories
curl -sL {s}/api/index.md           # API guide
```

A paper entry lists its arXiv id; read the paper itself from a terminal with the Hugging Face CLI:

```sh
hf papers read 2609.01185
```

## JSON API

```sh
curl -sL {s}/resources/<id>/record.json   # one entry, bilingual
curl -sL {s}/papers/<id>/record.json
curl -sL {s}/api/v1/resources.json        # every curated resource (CSV: resources.csv)
curl -sL {s}/api/v1/papers.json           # every paper (CSV: papers.csv)
curl -sL {s}/api/v1/categories.json
curl -sL {s}/api/v1/candidates.json       # automated discoveries and followed-source leads
curl -sL {s}/api/v1/changes.json          # additions of the last 30 days
curl -sL {s}/api/v1/schema.json
curl -sL {s}/feed.json                    # new entries (Atom: {s}/feed.xml)
```

## Search

```sh
open "{s}/resources/?q=<query>"           # search page; filters: kind, target
curl -sL {s}/search-index.json            # the index behind it (Chinese: search-index.zh.json)
python3 scripts/catalog.py <query>        # in a clone of the repository; add --papers
```

## Whole site and dataset

```sh
curl -sL {s}/llms.txt                     # index of Markdown pages
curl -sL {s}/llms-full.txt                # every curated resource and paper in one file
curl -sL {s}/zh/llms-full.txt             # the same in Chinese
curl -sL {s}/sitemap.xml
curl -sLO {s}/downloads/records.jsonl     # one resource or paper per line
curl -sL {s}/data-manifest.json           # file URLs, sizes, SHA-256
git clone {repository_url}.git
hf download TIGER-Lab/AwesomeREA --repo-type dataset
```

## Cite

```bibtex
@misc{{awesome-rea,
  title = {{Awesome Reverse Engineering Anything}},
  author = {{{{Awesome REA}}}},
  year = {{{updated[:4]}}},
  url = {{{s}/}},
  note = {{Accessed {updated}}}
}}
```

Papers have their own BibTeX at `{s}/papers/citations/<id>.bib`; the whole bibliography is `{s}/papers/references.bib`.

## Update cadence

- Curated entries change through reviewed pull requests; each entry carries its source review date.
- Automated scans add repository records continuously; `{s}/discoveries/status.json` reports the last ingest.
- The Hugging Face mirror refreshes every 2 hours.

## Contact

- Suggest a resource, case, paper or correction: https://github.com/reacher-z/Awesome-REA/issues/new/choose
- Source, data format and contribution rules: {repository_url}

{faq}'''


def write_agent_files(output: Path, site_url: str, repository_url: str, **counts) -> None:
    text = agents_markdown(site_url, repository_url, **counts)
    for name in AGENT_FILES:
        (Path(output) / name).write_text(text, encoding='utf-8')


def twin_type(route: str) -> str:
    parts = [part for part in english_path(route).strip('/').split('/') if part]
    if not parts:
        return 'home'
    if len(parts) == 2 and parts[0] in ('resources', 'papers'):
        return 'resource' if parts[0] == 'resources' else 'paper'
    return 'collection' if len(parts) <= 2 else 'page'


def quoted(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def add_front_matter(output: Path, site_url: str, dates: dict[str, str], fallback: str) -> int:
    """Prefix every Markdown twin with title, url, updated and type; return how many were changed."""
    output = Path(output)
    changed = 0
    for path in sorted(output.rglob('index.md')):
        relative = path.parent.relative_to(output)
        if relative.parts[:1] == SKIP_TWINS:
            continue
        text = path.read_text(encoding='utf-8')
        if text.startswith('---\n'):
            continue
        heading = re.match(r'# (.+)\n', text)
        if not relative.parts or relative.parts == ('zh',):
            text = text.replace(heading[0], '# '+BRAND+'\n', 1)
            heading = re.match(r'# (.+)\n', text)
        route = '/' + relative.as_posix().strip('.') + ('/' if relative.parts else '')
        route = route.replace('//', '/')
        updated = dates.get(dated_path(route)) or fallback
        front = ('---\n' f'title: {quoted(heading[1] if heading else route)}\n' f'url: {site_url}{route}\n'
                 f'updated: {updated[:10]}\n' f'type: {twin_type(route)}\n' '---\n\n')
        path.write_text(front + text, encoding='utf-8')
        changed += 1
    return changed
