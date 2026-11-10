"""One build of the site per test process, shared by the tests that only read it.

A test that changes built files, or builds under patched data, builds its own copy instead.
"""
import atexit
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_site  # noqa: E402

_OUTPUT = None


def built_site() -> Path:
    """The dist/ directory of a build of the current sources, made on first use and removed at exit."""
    global _OUTPUT
    if _OUTPUT is None:
        directory = Path(tempfile.mkdtemp(prefix='rea-shared-build-'))
        atexit.register(shutil.rmtree, directory, ignore_errors=True)
        build_site.build_site(directory / 'dist')
        _OUTPUT = directory / 'dist'
    return _OUTPUT
