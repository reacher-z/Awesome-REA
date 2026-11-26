#!/usr/bin/env python3
"""The Data super-class: exactly one class for each record that reproduces a real thing.

A data point's main output reproduces one named real thing: rebuilt code, a working stand-in or a
reconstructed protocol or format. A benchmark or dataset whose items are reproductions is a data point too.
The class follows the original thing and its main application domain, not the medium the reproduction runs on. data/README.md gives the rule.
"""

# The order is the order every page, README section and API listing shows them in.
DATA_CLASSES = {
    'website': ('Website', '网站'),
    'game-dev': ('Game Dev', '游戏开发'),
    'mobile-app-dev': ('Mobile App Dev', '移动应用开发'),
    '3d-design': ('3D Design', '3D 设计'),
    'software': ('Software', '软件'),
    'animation': ('Animation', '动画'),
    'video': ('Video', '视频'),
    'hardware': ('Hardware', '硬件'),
    'analysis': ('Analysis', '分析'),
}
# Tools, integrations, collections, documentation, learning material and research take no class.
DATA_CLASS_KINDS = frozenset({'case-study', 'project'})
# Tags describe a record without placing it. `protocol` in `targets` is the Protocol tag: never a class.
TAGS = {'protocol': ('Protocol', '协议')}


def is_data_point(record: dict) -> bool:
    return 'class' in record


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
