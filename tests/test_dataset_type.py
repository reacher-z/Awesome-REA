"""Benchmarks and datasets are typed Dataset from their reviewed description."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from structured_data import is_benchmark_or_dataset, resource_entity  # noqa: E402


def resource(**changes):
    item = deepcopy(json.loads((ROOT / 'data/tool-resources.json').read_text())[0])
    item.update(changes)
    return item


class DatasetTypeTests(unittest.TestCase):
    def test_reviewed_description_decides_dataset_type(self):
        cases = {
            'A benchmark combining functions from real programs.': True,
            'Example is an experimental benchmark for comparing decompilers.': True,
            'This repository holds Ghidra Function ID datasets.': True,
            'Recognize CPU instruction sets by comparing statistics with a corpus.': False,
            'Example Benchmark compares lifting workflows.': False,
            'A tool to benchmark emulators.': False,
            'A harness for running decompiler benchmarks.': False,
            'Dataset loader and viewer for binaries.': False,
            'A dataset of binary-source function pairs published for a project.': True,
            'Example is a binary decompilation evaluation dataset pairing C source with assembly.': True,
            'Benchmark that asks whether agents can rebuild websites.': True,
        }
        for description, expected in cases.items():
            record = resource(kind='project', name='Example Benchmark' if 'compares' in description else 'Example',
                              description_en=description)
            with self.subTest(description=description):
                self.assertEqual(is_benchmark_or_dataset(record), expected)
                self.assertEqual(resource_entity(record, 'x#resource', 'n', 'd')['@type'] == 'Dataset', expected)
        self.assertFalse(is_benchmark_or_dataset(resource(kind='case-study', description_en='A benchmark of ports.')))



if __name__ == '__main__':
    unittest.main()
