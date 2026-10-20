"""The resource form asks for a duplicate search and the submitter's own connection, separately from REA status."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FORM = ROOT / '.github/ISSUE_TEMPLATE/resource.yml'


def fields():
    """Split the form into (type, id, block) without a YAML dependency."""
    text = FORM.read_text(encoding='utf-8')
    result = []
    for block in text.split('\n  - type: ')[1:]:
        kind = block.split('\n', 1)[0].strip()
        identifier = re.search(r'^    id: (\S+)$', block, re.MULTILINE)
        result.append((kind, identifier[1] if identifier else None, block))
    return result


def field(identifier):
    matches = [(kind, block) for kind, name, block in fields() if name == identifier]
    if len(matches) != 1:
        raise AssertionError(f'resource.yml should contain one {identifier!r} field')
    return matches[0]


def required(block):
    return re.search(r'^    validations:\n      required: (true|false)$', block, re.MULTILINE)[1] == 'true'


class ResourceFormPromptTests(unittest.TestCase):
    def test_duplicate_search_is_acknowledged_and_an_existing_record_can_be_named(self):
        kind, block = field('duplicate_check')
        self.assertEqual(kind, 'checkboxes')
        self.assertRegex(block, r'\n        - label: .*searched.*\n          required: true')
        kind, block = field('existing_id')
        self.assertEqual(kind, 'input')
        self.assertFalse(required(block))
        self.assertIn('/resources/<id>/', block)
        self.assertIn('instead of requesting a second entry', block)
        order = [name for _, name, _ in fields()]
        self.assertLess(order.index('url'), order.index('duplicate_check'))
        self.assertLess(order.index('duplicate_check'), order.index('existing_id'))

    def test_affiliation_is_separate_from_the_relationship_and_implies_nothing(self):
        kind, block = field('affiliation')
        self.assertEqual(kind, 'dropdown')
        options = re.findall(r'^        - (.+)$', block, re.MULTILINE)
        self.assertIn('None', options)
        self.assertIn('Prefer not to say', options)
        self.assertTrue(any('maintain' in option for option in options))
        for option in options:
            self.assertNotRegex(option.casefold(), r'official|endorse|verified|tested|rea\b')
        self.assertIn('does not imply endorsement, official REA status or runtime verification', block)
        _, relation = field('relation')
        self.assertIn('Your personal connection is asked separately', relation)
        order = [name for _, name, _ in fields()]
        self.assertEqual(order.index('affiliation'), order.index('relation') + 1)

    def test_the_form_never_asks_for_personal_identity(self):
        self.assertIn('No real name, employer or account details are needed', field('affiliation')[1])
        for kind, name, block in fields():
            label = re.search(r'^      label: (.+)$', block, re.MULTILINE)
            if label:
                self.assertNotRegex(label[1].casefold(), r'\b(name|e-?mail|employer|company|handle|account)\b', name)


if __name__ == '__main__':
    unittest.main()
