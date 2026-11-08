"""Machine-read Data class decisions for discovery records."""
from pathlib import Path
import re

from data_classes import DATA_CLASSES
from strict_json import load_path

FILE = 'data/discovery-classes.json'
ID = re.compile(r'(?:scan-[0-9]+|lead-[0-9a-f]{24})\Z')


def read_classes(root) -> dict:
    path = Path(root) / FILE
    return load_path(path) if path.is_file() else {}


def validate_classes(batches, classes, errors, lead_batches=None) -> None:
    """Check decision shape; former queue IDs remain valid."""
    if not isinstance(classes, dict):
        errors.append(f'{FILE}: expected an object keyed by discovery ID')
        return
    for identifier, row in classes.items():
        where = f'{FILE}: {identifier}'
        if not isinstance(identifier, str) or not ID.fullmatch(identifier):
            errors.append(f'{where}: invalid discovery ID')
        if not isinstance(row, dict):
            errors.append(f'{where}: expected a decision object')
            continue
        decision = row.get('decision')
        if decision not in ('data', 'outside'):
            errors.append(f'{where}: decision must be data or outside')
        allowed = {'decision', 'class', 'reproduced'} if decision == 'data' else {'decision'}
        if set(row) - allowed:
            errors.append(f'{where}: unknown fields: {", ".join(sorted(set(row) - allowed))}')
        if decision == 'data':
            if not isinstance(row.get('class'), str) or row['class'] not in DATA_CLASSES:
                errors.append(f'{where}: class must be exactly one Data class')
            if not isinstance(row.get('reproduced'), str) or not row['reproduced'].strip():
                errors.append(f'{where}: reproduced must be nonempty text')
