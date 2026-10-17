"""Check local Markdown links in list content while ignoring code."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate import prose_only, validate_markdown

FIXTURE = '''# Guide

- Parent
    - [Nested guide](missing-guide.md)

    Continuation paragraph with [a missing file](also-missing.md#nope)
    and [a missing anchor](other.md#nope).
- Item text
continued with [a lazy link](lazy-missing.md).

Paragraph before code.

    [Indented code](indented-missing.md)

```text
[Fenced](fenced-missing.md)
```

Inline `[code](code-missing.md)` and [a real anchor](other.md#real-heading).

1. Step

   ```sh
       [Fenced in item](item-fenced-missing.md)
   ```

       [Item code](item-code-missing.md)
\t- [Tab-indented item](other.md#tab-missing)
'''


class MarkdownLinkTest(unittest.TestCase):
    def errors_for(self, text):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text(text, encoding='utf-8')
            (root / 'other.md').write_text('# Real heading\n', encoding='utf-8')
            errors = []
            validate_markdown(root, errors)
            return errors

    def test_nested_items_and_continuations_are_checked_with_line_numbers(self):
        self.assertEqual(self.errors_for(FIXTURE), [
            'README.md:4: missing local link target: missing-guide.md',
            'README.md:6: missing local link target: also-missing.md#nope',
            'README.md:7: missing Markdown anchor: other.md#nope',
            'README.md:9: missing local link target: lazy-missing.md',
            'README.md:28: missing Markdown anchor: other.md#tab-missing',
        ])

    def test_code_blocks_stay_ignored_and_lines_are_retained(self):
        prose = prose_only(FIXTURE)
        self.assertEqual(prose.count('\n'), FIXTURE.count('\n'))
        for hidden in ('indented-missing', 'fenced-missing', 'item-fenced-missing', 'item-code-missing'):
            self.assertNotIn(hidden, prose)
        self.assertEqual(self.errors_for('Text\n\n    [code](missing.md)\n\n\t[tab code](missing.md)\n'), [])


if __name__ == '__main__':
    unittest.main()
