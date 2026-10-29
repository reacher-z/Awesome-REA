"""The advisory literal review flags lost technical literals and accepts equivalent renderings."""
import contextlib
from fractions import Fraction
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import localization
import locale_literals as literals
from locale_literals import chinese_value, findings_for, literal_report, read_exceptions


def kinds(source, translation, field='description_zh'):
    return [(row['kind'], row['literal']) for row in findings_for('scan-1', source, translation, field)]


class LocaleLiteralTests(unittest.TestCase):
    def test_chinese_numerals_and_units_have_values(self):
        for text, value in (('六', 6), ('十', 10), ('十二', 12), ('两百', 200), ('三万', 30000), ('一千零五', 1005), ('两亿', 2 * 10 ** 8)):
            self.assertEqual(chinese_value(text), value, text)
        self.assertEqual(literals.literals('64K, 1.5M and 1,000 items')['numbers'], [64000, 1500000, 1000])

    def test_equivalent_renderings_are_not_findings(self):
        for source, translation in (
                ('64K classes / 570K methods / 188K fields', '6.4 万个类、57 万个方法和 18.8 万个字段'),
                ('Tested on 25K .jsc files with 0 failures', '已测试 2.5 万个 .jsc 文件，失败数为 0'),
                ('A 6-phase workflow for 1,000 samples', '面向 1000 个样本的六阶段工作流'),
                ('Rust engine + 1 file editor', '包含 Rust 引擎和单文件编辑器'),
                ('100% client-side disassembler', '完全在客户端运行的反汇编器'),
                ("Samples (including NDSS'14 cases), 2000-01 release", '样例（包括 NDSS 2014 的案例），2000—2001 年发布'),
                ('Ends 3 Feb 2027', '2027 年 2 月 3 日停止'),
                ('Unity 6 (6000.0.60f1), Lua 5.1, firmware 1.1.2.', 'Unity 6（6000.0.60f1）、Lua 5.1，固件 1.1.2。'),
                ('metadata v22-v31, see https://example.com/docs.', '元数据 v22–v31，参见 https://example.com/docs。'),
                ('高性能GB/T 27930-2023（云快充1.6）协议SDK', '高性能 GB/T 27930-2023（云快充 1.6）协议 SDK'),
                ('radare2-based IL2CPP tool for x86-64', '基于 radare2 的 IL2CPP 工具，适用于 x86-64')):
            with self.subTest(source=source):
                self.assertEqual(kinds(source, translation), [])

    def test_lost_versions_changed_urls_and_suspicious_numbers_are_flagged(self):
        self.assertEqual(kinds('Maintained for Ghidra 12.1.4.', '针对 Ghidra 开发和维护。'), [('version-missing', '12.1.4')])
        self.assertEqual(kinds('Docs at https://example.com/a', '文档见 https://example.org/a'),
                         [('url-missing', 'https://example.com/a'), ('url-added', 'https://example.org/a')])
        self.assertEqual(kinds('Supports 32 architectures', '支持 23 种架构'), [('number-missing', '32'), ('number-added', '23')])
        self.assertEqual(kinds('Supports 32 architectures', 'Supports many architectures', 'description_en'), [('number-missing', '32')])

    def test_source_identifiers_and_typos_are_compared_verbatim(self):
        self.assertEqual(kinds('Unity games (Mono/IIL2CPP)', 'Unity 游戏（Mono/IIL2CPP）'), [])
        self.assertEqual(kinds('Unity games (Mono/IIL2CPP)', 'Unity 游戏（Mono/IL2CPP）'), [('identifier-missing', 'IIL2CPP')])
        self.assertEqual(kinds('An il2cpp dumper for x64dbg', '适用于 x64dbg 的 IL2CPP 转储工具'), [('identifier-case-changed', 'il2cpp')])
        self.assertEqual(kinds('dump_symbols for Node.js', '适用于 Node.js 的 dump_symbols'), [])

    def test_report_is_ordered_by_stable_id_skips_empty_text_and_honors_exceptions(self):
        records = [{'id': 'scan-20', 'description_en': 'Utilities 4 Newbies'},
                   {'id': 'scan-3', 'description_en': 'Ghidra 12.1.4 loader'},
                   {'id': 'scan-7', 'description_en': '', 'description_omission': {'original_characters': 1001}}]
        translations = {'scan-20': {'description_en': 'Utilities 4 Newbies', 'description_zh': '面向新手的工具'},
                        'scan-3': {'description_en': 'Ghidra loader', 'description_zh': 'Ghidra 12.1.4 加载器'},
                        'scan-7': {'description_en': '', 'description_zh': ''}}
        report = literal_report(records, translations, {})
        self.assertEqual([(row['id'], row['field'], row['kind']) for row in report['findings']],
                         [('scan-3', 'description_en', 'version-missing'), ('scan-20', 'description_zh', 'number-missing')])
        exception = {'field': 'description_zh', 'kind': 'number-missing', 'literal': '4',
                     'reason': 'Wordplay for "for".', 'reviewed_at': '2026-10-19'}
        stale = {**exception, 'literal': '5'}
        report = literal_report(records, translations, {'scan-20': [exception, stale]})
        self.assertEqual((report['excepted'], report['records_with_findings']), (1, 1))
        self.assertEqual(report['unused_exceptions'], ['scan-20/description_zh/number-missing/5'])

    def test_command_is_advisory_and_never_rewrites_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data/locales').mkdir(parents=True)
            source = root / 'data/source-index.json'
            source.write_text(json.dumps({'resources': [{'id': 'scan-1', 'description_en': 'Lua 5.1 decompiler'}]}))
            shards = [root / name for name in localization.LOCALE_FILES]
            shards[0].write_text(json.dumps({'scan-1': {'description_en': 'Lua decompiler', 'description_zh': 'Lua 反编译器'}}))
            for shard in shards[1:]:
                shard.write_text('{}')
            before = {path: path.read_bytes() for path in [source, *shards]}
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(literals.main([], root=root), 0)
            self.assertEqual(json.loads(output.getvalue())['counts']['number-missing'], 2)
            self.assertEqual({path: path.read_bytes() for path in before}, before)
            (root / literals.EXCEPTIONS_FILE).write_text(json.dumps({'scan-1': [{'field': 'description_zh', 'kind': 'guess'}]}))
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(literals.main([], root=root), 2)

    def test_repository_exceptions_are_well_formed_and_all_reviewed(self):
        exceptions = read_exceptions(ROOT / literals.EXCEPTIONS_FILE)
        self.assertTrue(exceptions)
        self.assertTrue(all(entry['reason'].strip() for entries in exceptions.values() for entry in entries))


if __name__ == '__main__':
    unittest.main()
