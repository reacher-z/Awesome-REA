"""Translations stay bound to the source text and omission evidence they were written from."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import localization
from localization import (FINGERPRINT_FIELDS, FINGERPRINT_POLICY, fingerprint_status, source_fingerprint,
                          validate_fingerprints, validate_localizations)
from source_descriptions import capture_description

OMITTED = {'id': 'scan-3', **capture_description('x' * 1001)}
RECORDS = [{'id': 'scan-1', 'description_en': 'Firmware unpacker', 'description_zh': 'Firmware unpacker'},
           {'id': 'scan-2', 'description_en': '', 'description_zh': ''}, OMITTED]
TRANSLATIONS = {'scan-1': {'description_en': 'Firmware unpacker', 'description_zh': '固件解包工具'},
                'scan-2': {'description_en': '', 'description_zh': ''},
                'scan-3': {'description_en': '', 'description_zh': ''}}


def document(bindings):
    return {'schema_version': 1, 'policy': FINGERPRINT_POLICY, 'fields': list(FINGERPRINT_FIELDS), 'fingerprints': bindings}


def bound(records=RECORDS):
    return document({record['id']: source_fingerprint(record) for record in records})


def check(records, translations, binding):
    errors, warnings = [], []
    validate_fingerprints(records, translations, binding, errors, warnings)
    return errors, warnings


class LocaleFingerprintTests(unittest.TestCase):
    def test_fingerprint_covers_text_and_omission_evidence(self):
        self.assertEqual(source_fingerprint(RECORDS[0]), source_fingerprint(dict(RECORDS[0])))
        self.assertNotEqual(source_fingerprint(RECORDS[0]), source_fingerprint({**RECORDS[0], 'description_en': 'Firmware unpacker.'}))
        self.assertNotEqual(source_fingerprint(RECORDS[1]), source_fingerprint(OMITTED))
        changed = {**OMITTED, 'description_omission': {**OMITTED['description_omission'], 'original_characters': 1002}}
        self.assertNotEqual(source_fingerprint(OMITTED), source_fingerprint(changed))
        # Display-only fields do not invalidate a translation.
        self.assertEqual(source_fingerprint(RECORDS[0]), source_fingerprint({**RECORDS[0], 'stars': 9, 'description_zh': ''}))

    def test_changed_source_text_or_omission_marks_only_that_translation_stale(self):
        self.assertEqual(check(RECORDS, TRANSLATIONS, bound()), ([], []))
        changed = [{**RECORDS[0], 'description_en': 'Firmware unpacker and patcher'}, RECORDS[1],
                   {**OMITTED, 'description_omission': {**OMITTED['description_omission'], 'original_sha256': '0' * 64}}]
        errors, warnings = check(changed, TRANSLATIONS, bound())
        self.assertEqual([error.split(':')[0] for error in errors], ['scan-1', 'scan-3'])
        self.assertTrue(all('translation is stale' in error for error in errors))
        self.assertEqual(warnings, [])
        self.assertEqual(fingerprint_status(changed, TRANSLATIONS, bound())['stale'], ['scan-1', 'scan-3'])

    def test_unbound_is_a_warning_and_unknown_or_malformed_bindings_are_errors(self):
        partial = bound(RECORDS[:1])
        self.assertEqual(check(RECORDS, TRANSLATIONS, partial),
                         ([], ['2 repository translations have no source fingerprint; bind them after review with '
                               'python3 scripts/localization.py --bind <id>.']))
        self.assertEqual(check(RECORDS, TRANSLATIONS, None), ([], []))
        unknown = document({**bound()['fingerprints'], 'scan-9': '0' * 64})
        self.assertEqual(check(RECORDS, TRANSLATIONS, unknown)[0],
                         ['scan-9: source fingerprint has no matching source record and translation; remove it.'])
        for broken in ({**bound(), 'policy': 'other'}, {**bound(), 'extra': True},
                       document({'scan-1': 'ABC'}), {**bound(), 'fields': ['description_en']}):
            self.assertEqual(len(check(RECORDS, TRANSLATIONS, broken)[0]), 1)

    def test_empty_and_omitted_descriptions_stay_empty_in_both_languages(self):
        for identifier in ('scan-2', 'scan-3'):
            for field in ('description_en', 'description_zh'):
                with self.subTest(identifier=identifier, field=field):
                    errors = []
                    translations = {**TRANSLATIONS, identifier: {**TRANSLATIONS[identifier], field: '补充说明'}}
                    validate_localizations(RECORDS, translations, errors)
                    self.assertEqual(errors[:1], [f'{identifier}: preserve an empty upstream description'])

    def test_binding_command_writes_only_fingerprints_and_never_rebinds_stale_silently(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data/locales').mkdir(parents=True)
            source = root / 'data/source-index.json'
            source.write_text(json.dumps({'meta': {}, 'resources': RECORDS}), encoding='utf-8')
            shards = [root / name for name in localization.LOCALE_FILES]
            shards[0].write_text(json.dumps(TRANSLATIONS, ensure_ascii=False), encoding='utf-8')
            for shard in shards[1:]:
                shard.write_text('{}', encoding='utf-8')
            untouched = {path: path.read_bytes() for path in [source, *shards]}

            def run(*arguments):
                with contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()):
                    code = localization.main(list(arguments), root=root)
                return code, output.getvalue()

            self.assertEqual(run('--bind', 'scan-1')[0], 0)
            self.assertEqual(list(localization.read_fingerprints(root)['fingerprints']), ['scan-1'])
            records = [{**RECORDS[0], 'description_en': 'Changed upstream text'}, *RECORDS[1:]]
            source.write_text(json.dumps({'meta': {}, 'resources': records}), encoding='utf-8')
            untouched[source] = source.read_bytes()
            code, output = run('--bind-unbound')
            self.assertEqual((code, json.loads(output)['stale_ids']), (1, ['scan-1']))
            self.assertEqual(sorted(localization.read_fingerprints(root)['fingerprints']), ['scan-1', 'scan-2', 'scan-3'])
            self.assertEqual(run('--bind', 'scan-404')[0], 2)
            self.assertEqual(run('--bind', 'scan-1')[0], 0)
            self.assertEqual(run()[0], 0)
            self.assertEqual({path: path.read_bytes() for path in untouched}, untouched)
            self.assertEqual(check(records, TRANSLATIONS, localization.read_fingerprints(root)), ([], []))


if __name__ == '__main__':
    unittest.main()
