"""Search matching uses one Unicode compatibility and casing contract."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import catalog


class SearchNormalizationTests(unittest.TestCase):
    def test_contract_strips_only_existing_controls_then_normalizes_and_casefolds(self):
        self.assertEqual(catalog.normalize_search_text('\x00剪映／CapCut I\u0307STANBUL\x7f'),
                         ' 剪映/capcut i\u0307stanbul ')
        self.assertEqual(catalog.normalize_search_text('Ｉstanbul'), 'istanbul')

    def test_cli_normalizes_query_and_searchable_record_text_in_every_mode(self):
        records = [
            {'id': 'compatibility-fixture', 'description_zh': '剪映／CapCut in Istanbul'},
            {'id': 'other', 'description_zh': '其他记录'},
        ]
        for mode in ([], ['--papers'], ['--source-index']):
            for query in ('剪映/CapCut', 'ＩSTANBUL'):
                with self.subTest(mode=mode, query=query), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    (root / 'data').mkdir()
                    (root / 'data/source-index.json').write_text(json.dumps({'resources': records}), encoding='utf-8')
                    stdout = io.StringIO()
                    with patch.object(catalog, 'ROOT', root), \
                            patch.object(catalog, 'load_resources', return_value=records), \
                            patch.object(catalog, 'read_papers', return_value=records), \
                            patch.object(catalog, 'read_localizations', return_value={}), \
                            patch.object(catalog, 'read_scope', return_value={}), \
                            patch.object(catalog, 'localized_records', side_effect=lambda rows, _: rows), \
                            patch.object(catalog, 'apply_scope', side_effect=lambda rows, _: rows), \
                            patch.object(catalog, 'with_curated_labels', side_effect=lambda rows, _: rows), \
                            patch.object(sys, 'argv', ['catalog.py', *mode, query, '--json']), \
                            redirect_stdout(stdout):
                        catalog.main()
                    self.assertEqual([record['id'] for record in json.loads(stdout.getvalue())],
                                     ['compatibility-fixture'])


if __name__ == '__main__':
    unittest.main()
