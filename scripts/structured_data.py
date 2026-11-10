"""Schema.org nodes shared by the page builders: the project, the catalog dataset and typed resources.

Every value comes from a record or from the project's own routes. No person is named, and a property
the record does not hold stays absent: curated records hold no license or programming language, because
a host's detected license is an unreviewed signal (docs/artifact-evidence.md).
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit

ORGANIZATION_NAME = 'Awesome REA'
LICENSE_URL = 'https://spdx.org/licenses/MIT.html'
SEARCH_PARAMETER = 'search_term_string'
GITHUB_REPOSITORY_KINDS = {'tool', 'integration', 'project', 'case-study'}
API_TABLES = ('resources', 'papers', 'categories')
# Published file and its media type, as served by Cloudflare Pages or as named by its format.
CATALOG_DOWNLOADS = (('catalog.json', 'application/json'), ('papers.json', 'application/json'),
                     ('downloads/records.jsonl', 'application/x-ndjson'),
                     ('downloads/awesome-rea-data.zip', 'application/zip'),
                     ('downloads/references.bib', 'application/x-bibtex'))
DATASET_TEXT = {
    'en': ('Awesome REA catalog',
           'Curated reverse-engineering tools, projects, case studies, learning resources and research papers '
           'for websites, games, apps, binaries, firmware and communication protocols. Each record keeps its '
           'primary evidence links and source-review date; linked projects and papers retain their own licenses.'),
    'zh': ('Awesome REA 目录数据',
           '精选的逆向工程工具、项目、案例、学习资源与研究论文，覆盖网站、游戏、应用、二进制、固件和通信协议。'
           '每条记录保留一手证据链接与来源复核日期；被链接的项目和论文保留各自的许可。'),
}


def organization_id(site_url: str) -> str:
    return site_url + '/#organization'


def publisher_reference(site_url: str) -> dict:
    return {'@id': organization_id(site_url)}


def organization_node(site_url: str, repository_url: str) -> dict:
    """The project as an entity, defined only on the two homepages and referenced everywhere else."""
    return {'@type': 'Organization', '@id': organization_id(site_url), 'name': ORGANIZATION_NAME, 'url': site_url + '/',
            'alternateName': ['Awesome Reverse Engineering Anything', 'AwesomeREA'], 'logo': site_url + '/favicon.svg',
            'sameAs': [repository_url, 'https://huggingface.co/datasets/TIGER-Lab/AwesomeREA']}


def search_action(site_url: str) -> dict:
    """The homepage search: app.js reads ?q= into the catalog filter."""
    return {'@type': 'SearchAction', 'target': {'@type': 'EntryPoint', 'urlTemplate': f'{site_url}/?q={{{SEARCH_PARAMETER}}}'},
            'query-input': f'required name={SEARCH_PARAMETER}'}


def dataset_id(site_url: str, language: str = 'en') -> str:
    return f"{site_url}{'/zh' if language == 'zh' else ''}/about/#dataset"


def catalog_node(site_url: str) -> dict:
    """The catalog the homepage presents, pointing at the Dataset that /about/ defines."""
    return {'@type': 'DataCatalog', '@id': site_url + '/#catalog', 'name': DATASET_TEXT['en'][0], 'url': site_url + '/',
            'publisher': publisher_reference(site_url), 'dataset': {'@id': dataset_id(site_url)}}


def _download(site_url: str, path: str, media_type: str) -> dict:
    return {'@type': 'DataDownload', 'contentUrl': f'{site_url}/{path}', 'encodingFormat': media_type}


def dataset_node(site_url: str, language: str, date_modified: str | None) -> dict:
    """The downloadable catalog as a Dataset: one DataDownload per published file."""
    name, description = DATASET_TEXT[language]
    downloads = [_download(site_url, path, media_type) for path, media_type in CATALOG_DOWNLOADS]
    for table in API_TABLES:
        downloads += [_download(site_url, f'api/v1/{table}.json', 'application/json'),
                      _download(site_url, f'api/v1/{table}.csv', 'text/csv')]
    node = {'@type': 'Dataset', '@id': dataset_id(site_url, language), 'name': name, 'description': description,
            'url': f"{site_url}{'/zh' if language == 'zh' else ''}/about/", 'inLanguage': ['en', 'zh-CN'],
            'license': LICENSE_URL, 'isAccessibleForFree': True, 'creator': publisher_reference(site_url),
            'publisher': publisher_reference(site_url), 'includedInDataCatalog': {'@id': site_url + '/#catalog'},
            'distribution': downloads}
    if date_modified:
        node['dateModified'] = date_modified
    return node


def _is_github_repository(url: str) -> bool:
    parts = urlsplit(url)
    return parts.netloc.lower() == 'github.com' and len([part for part in parts.path.split('/') if part]) == 2


# The reviewed English description names what a record is in its first sentence: "A benchmark ...",
# "X is a decompilation evaluation dataset ...", "This repository holds ... datasets". The record name is
# removed first, so a name such as "Foo Benchmark" alone never decides the type.
_FUNCTION_WORDS = {'to', 'for', 'of', 'and', 'or', 'with', 'running', 'run', 'runs', 'using', 'that', 'which', 'in', 'on'}
_DATASET_HEAD = re.compile(r'^(?:(?:this|the) (?:repository|project) (?:holds|provides|publishes) |(?P<subject>[\w.+-]+ ){0,4}(?:is|are) )?'
                           r'(?:an? |the )?(?P<modifiers>(?:[\w-]+ ){0,4}?)(?:benchmark|dataset)s?'
                           r'(?= (?:of|for|that|which|pairing|combining|comparing|generated|built|covering|with)\b|[,.:;]|$)', re.I)
DATASET_KINDS = {'project', 'research', 'tool', 'learning-resource', 'documentation', 'collection'}


def is_benchmark_or_dataset(record: dict) -> bool:
    """Whether a resource's reviewed description presents it as a benchmark or dataset."""
    if record.get('kind') not in DATASET_KINDS:
        return False
    first = re.split(r'(?<=[.!?])\s', record.get('description_en', '').strip(), maxsplit=1)[0]
    name = record.get('name', '')
    match = _DATASET_HEAD.search(first.replace(name, 'X').strip() if name else first)
    # Modifiers are adjectives or nouns ("binary decompilation evaluation dataset"); a verb or preposition
    # ("a tool to benchmark", "a harness for running benchmarks") means the record is something else.
    return bool(match) and not _FUNCTION_WORDS & set(match['modifiers'].lower().split())


def resource_entity(record: dict, entity_id: str, name: str, description: str) -> dict:
    """The typed main entity of a curated resource page, built only from fields of the record."""
    kind = record['kind']
    entity = {'@id': entity_id, 'url': record['url'], 'name': name, 'description': description}
    if is_benchmark_or_dataset(record):
        entity['@type'] = 'Dataset'
    elif kind in GITHUB_REPOSITORY_KINDS and _is_github_repository(record['url']):
        entity.update({'@type': 'SoftwareSourceCode', 'codeRepository': record['url']})
    elif kind == 'case-study':
        entity.update({'@type': 'TechArticle', 'headline': name})
    elif kind == 'learning-resource':
        entity['@type'] = 'LearningResource'
    elif kind == 'research':
        entity.update({'@type': 'ScholarlyArticle', 'headline': name})
    else:
        entity['@type'] = 'CreativeWork'
    return entity


def evidence_urls(record: dict) -> list[str]:
    """What a record was reviewed against, which can be the resource's own page."""
    urls = [record.get('evidence_url'), *record.get('evidence_urls', []), *record.get('additional_evidence_urls', [])]
    return list(dict.fromkeys(url for url in urls if url))
