"""Data records: one class from a fixed vocabulary, on the kinds that hold reproductions, with Protocol as a tag."""
from copy import deepcopy
import datetime as dt
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from data_classes import DATA_CLASS_KINDS, DATA_CLASSES, class_errors, class_value_errors, is_data_point, record_tags
from test_curated_fields import RECORD
from validate import unknown_field_warnings, validate_resources

NOW = dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc)
CASE = deepcopy(RECORD) | {'kind': 'case-study', 'name': 'Field fixture: a rebuilt program', 'category': 'reconstruction-cases',
                           'relationship': 'independent-reconstruction', 'targets': ['app', 'protocol']}


def errors_for(record):
    errors = []
    validate_resources([record], errors, now=NOW)
    return errors


class DataClassVocabularyTests(unittest.TestCase):
    def test_classes_keep_the_owner_order(self):
        self.assertEqual(list(DATA_CLASSES), ['software', 'game', 'apps', 'website', 'science', 'hardware'])

    def test_every_class_has_english_and_chinese_labels(self):
        for labels in DATA_CLASSES.values():
            self.assertEqual(len(labels), 2)
            self.assertTrue(all(labels))

    def test_targets_that_became_tags_or_left_are_not_classes(self):
        for retired in ('protocol', 'firmware', 'binary', 'app'):
            self.assertNotIn(retired, DATA_CLASSES)


class DataClassValidationTests(unittest.TestCase):
    def test_a_record_without_a_class_is_valid(self):
        self.assertEqual(errors_for(deepcopy(CASE)), [])
        self.assertFalse(is_data_point(CASE))

    def test_every_class_passes_on_a_case_study(self):
        for value in DATA_CLASSES:
            with self.subTest(value):
                record = deepcopy(CASE) | {'class': value}
                self.assertEqual(errors_for(record), [])
                self.assertEqual(unknown_field_warnings([record]), [])
                self.assertTrue(is_data_point(record))

    def test_only_case_studies_and_projects_take_a_class(self):
        self.assertEqual(DATA_CLASS_KINDS, {'case-study', 'project'})
        for kind in ('tool', 'integration', 'collection', 'documentation', 'learning-resource', 'research'):
            with self.subTest(kind):
                self.assertEqual(class_errors({'kind': kind, 'class': 'game'}),
                                 ['class: only case-study and project records take a class'])
        self.assertEqual(class_errors({'kind': 'project', 'class': 'website'}), [])

    def test_a_class_is_exactly_one_known_value(self):
        for value in (['game'], ['game', 'hardware'], 'protocol', 'firmware', 'Game', '', None, 3):
            with self.subTest(value):
                record = deepcopy(CASE) | {'class': value}
                self.assertEqual(errors_for(record), ["resource 'field-fixture'.class: use exactly one of "
                                                      'software, game, apps, website, science, hardware'])

    def test_papers_share_the_vocabulary(self):
        self.assertEqual(class_value_errors({'class': 'website'}), [])
        self.assertEqual(class_value_errors({}), [])
        self.assertEqual(len(class_value_errors({'class': ['website']})), 1)


class ProtocolTagTests(unittest.TestCase):
    def test_protocol_in_targets_is_the_tag(self):
        self.assertEqual(record_tags({'targets': ['app', 'protocol']}), ['protocol'])
        self.assertEqual(record_tags({'targets': ['protocol']}), ['protocol'])
        self.assertEqual(record_tags({'targets': ['app']}), [])
        self.assertEqual(record_tags({}), [])


if __name__ == '__main__':
    unittest.main()
