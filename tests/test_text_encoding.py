"""Read and write catalog text as UTF-8 regardless of the platform locale."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEXT_METHODS = {'read_text', 'write_text'}


def implicit_encoding_calls(source):
    """Yield line numbers of text I/O that would use the locale's encoding."""
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        keywords = {keyword.arg: keyword.value for keyword in node.keywords}
        function = node.func
        if 'encoding' in keywords:
            continue
        if isinstance(function, ast.Attribute) and function.attr in TEXT_METHODS:
            yield node.lineno
        elif isinstance(function, ast.Name) and function.id == 'open':
            mode = node.args[1] if len(node.args) > 1 else keywords.get('mode')
            if not (isinstance(mode, ast.Constant) and 'b' in str(mode.value)):
                yield node.lineno
        elif any(isinstance(keywords.get(name), ast.Constant) and keywords[name].value is True
                 for name in ('text', 'universal_newlines')):
            yield node.lineno


class TextEncodingTest(unittest.TestCase):
    def test_detector_flags_locale_dependent_text_io(self):
        source = '\n'.join([
            "path.read_text()", "path.write_text(value)", "open(name)", "open(name, 'w')",
            "subprocess.run(command, text=True)",
            "path.read_text(encoding='utf-8')", "path.write_text(value, encoding='utf-8')",
            "open(name, 'rb')", "path.read_bytes()", "urlopen(request)",
            "subprocess.run(command, encoding='utf-8')",
        ])
        self.assertEqual(sorted(implicit_encoding_calls(source)), [1, 2, 3, 4, 5])

    def test_scripts_name_utf8_for_every_text_read_and_write(self):
        offenders = [f'{path.relative_to(ROOT)}:{line}'
                     for path in sorted((ROOT / 'scripts').glob('*.py'))
                     for line in implicit_encoding_calls(path.read_text(encoding='utf-8'))]
        self.assertEqual(offenders, [])


if __name__ == '__main__':
    unittest.main()
