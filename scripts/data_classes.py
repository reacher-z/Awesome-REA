#!/usr/bin/env python3
"""The Data super-class: exactly one class for each record that reproduces a real thing.

A data point's main output reproduces one named real thing: rebuilt code, a working stand-in or a
reconstructed protocol or format. A benchmark or dataset whose items are reproductions is a data point too.
The class follows the original thing, not the medium the reproduction runs on. data/README.md gives the rule.
"""

# The order is the order every page, README section and API listing shows them in.
DATA_CLASSES = {
    'software': ('Software', '软件'),
    'game': ('Game', '游戏'),
    'apps': ('Apps', '移动应用'),
    'website': ('Website', '网站'),
    'hardware': ('Hardware', '硬件'),
    'science': ('Science', '科学软件'),
}
# The three entries after the classes for every record that is not a data point. None of them counts as data.
NON_DATA_TABS = {
    'tools': ('Tools', '工具'),
    'paper': ('Paper', '论文'),
    'tutorial': ('Tutorial', '教程'),
}
# The README heading over the sections that are not data; Papers keeps its own section.
NON_DATA_HEADING = ('Tools and tutorials', '工具与教程')
# Tools, integrations, collections, documentation, learning material and research take no class.
DATA_CLASS_KINDS = frozenset({'case-study', 'project'})
# Tags describe a record without placing it. `protocol` in `targets` is the Protocol tag: never a class.
TAGS = {'protocol': ('Protocol', '协议')}
# Data points that lead their class and carry the Featured label wherever the class is listed.
FEATURED_DATA = ('websitebench',)
FEATURED_LABEL = ('Featured', '精选')


def paper_data_record(paper: dict) -> dict:
    """A benchmark or dataset paper as a listing row: it files under its class and opens its paper entry."""
    return {'id': paper['id'], 'name': paper['title'], 'name_zh': paper['title_zh'], 'url': paper['url'], 'kind': 'research',
            'class': paper['class'], 'category': 'reconstruction-cases', 'relationship': 'learning', 'targets': paper['targets'],
            'description_en': paper['description_en'], 'description_zh': paper['description_zh'], 'evidence_url': paper['url'],
            'verified_at': paper['verified_at'], 'added_at': paper.get('added_at'), 'route': 'papers'}


def listed_records(resources: list[dict], papers: list[dict]) -> list[dict]:
    """Everything the filter row counts: the curated resources plus the papers that are data points."""
    return resources + [paper_data_record(paper) for paper in papers if 'class' in paper]


def is_data_point(record: dict) -> bool:
    return 'class' in record


def placement_facts(record: dict, zh: bool, targets: dict) -> list[tuple[str, str]]:
    """How an entry page places a record: a data point by its one class and any tag, anything else by its targets."""
    if 'class' in record:
        facts = [(('Data class', '数据类别')[zh], DATA_CLASSES[record['class']][zh])]
        tags = record_tags(record)
        return facts + ([(('Tag', '标签')[zh], ' · '.join(TAGS[tag][zh] for tag in tags))] if tags else [])
    return [(('Targets', '目标')[zh], ' · '.join(targets[target][zh] for target in record['targets']))]


def record_tags(record: dict) -> list[str]:
    targets = record.get('targets')
    return [tag for tag in TAGS if isinstance(targets, list) and tag in targets]


def class_value_errors(record: dict) -> list[str]:
    """The checks a resource and a paper share."""
    value = record.get('class', 'software')
    if isinstance(value, str) and value in DATA_CLASSES:
        return []
    return ['class: use exactly one of ' + ', '.join(DATA_CLASSES)]


def class_errors(record: dict) -> list[str]:
    """Problems with a curated resource's `class`; the field is optional and needs a kind that can hold one."""
    errors = class_value_errors(record)
    if 'class' in record and record.get('kind') not in DATA_CLASS_KINDS:
        errors.append('class: only ' + ' and '.join(sorted(DATA_CLASS_KINDS)) + ' records take a class')
    return errors
