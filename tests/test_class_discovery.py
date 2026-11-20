"""Class-scoped discovery: query profiles, frontier compatibility and followed sources."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import discovery_leads  # noqa: E402
from data_classes import DATA_CLASSES  # noqa: E402
from scan_sources import CLASS_QUERY_BASES, QUERY_BASES, SOURCE_CLASSES  # noqa: E402
import scheduled_source_scan  # noqa: E402
import search_frontier  # noqa: E402


class QueryProfileTests(unittest.TestCase):
    def test_every_class_has_a_query_profile(self):
        self.assertEqual(set(CLASS_QUERY_BASES), set(DATA_CLASSES))
        for name, queries in CLASS_QUERY_BASES.items():
            with self.subTest(name):
                self.assertGreaterEqual(len(queries), 3)
                self.assertEqual(len(set(queries)), len(queries))

    def test_profiles_are_merged_once_into_the_scanner_bases(self):
        self.assertEqual(len(QUERY_BASES), len(set(QUERY_BASES)))
        merged = {query for queries in CLASS_QUERY_BASES.values() for query in queries}
        self.assertEqual(merged & set(QUERY_BASES), merged)

    def test_every_profile_query_passes_frontier_validation(self):
        for name, queries in CLASS_QUERY_BASES.items():
            for query in queries:
                with self.subTest(name=name, query=query):
                    self.assertEqual(search_frontier.checked_base(query), query)

    def test_scheduled_queries_are_distinct_and_include_the_profiles(self):
        approved = scheduled_source_scan.APPROVED_QUERIES
        self.assertEqual(len(approved), len(set(approved)))
        self.assertEqual({query for queries in CLASS_QUERY_BASES.values() for query in queries} & set(approved),
                         {query for queries in CLASS_QUERY_BASES.values() for query in queries})


class FollowedSourceTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / "data" / "discovery-sources.json").read_text(encoding="utf-8"))
        self.problems = discovery_leads.validate_registry(self.document)

    def test_registry_is_valid(self):
        self.assertEqual(self.problems, [])

    def test_every_class_has_a_followed_source(self):
        self.assertEqual(set(DATA_CLASSES) - set(SOURCE_CLASSES.values()), set())

    def test_class_tags_name_real_classes_and_sources(self):
        registry_ids = {source["id"] for source in self.document["sources"]}
        for identifier, name in SOURCE_CLASSES.items():
            self.assertIn(name, DATA_CLASSES, identifier)
            self.assertIn(identifier, registry_ids, identifier)


if __name__ == "__main__":
    unittest.main()
