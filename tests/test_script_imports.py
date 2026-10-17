"""Import every pipeline script so CI catches errors in scripts that no other step runs."""
import importlib
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))


class ScriptImportTests(unittest.TestCase):
    def test_every_script_imports_offline_without_running_main(self):
        names = sorted(path.stem for path in SCRIPTS.glob('*.py'))
        for expected in ('build_production', 'check_links', 'review_pr', 'submit_indexnow'):
            self.assertIn(expected, names)
        # Importing must not reach the network; `main()` only runs under `__main__`.
        blocked = AssertionError('network access while importing a script')
        with patch.object(socket.socket, 'connect', side_effect=blocked), \
                patch.object(socket, 'getaddrinfo', side_effect=blocked):
            for name in names:
                with self.subTest(script=name):
                    module = importlib.import_module(name)
                    self.assertEqual(Path(module.__file__).resolve(), SCRIPTS / f'{name}.py')


if __name__ == '__main__':
    unittest.main()
