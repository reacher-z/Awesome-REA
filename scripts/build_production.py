#!/usr/bin/env python3
"""Validate the collection and browser script before producing deployable files."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from repository_stats import STATS_ENV, write_fresh_stats

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    # Accepted and ignored: the Cloudflare Pages build command may still pass it, and the site loads no icon font now.
    parser.add_argument('--fontawesome-assets-url', help=argparse.SUPPRESS)
    parser.parse_args()
    commands = [
        # The scan mapping is deterministic over the committed scan snapshot.
        [sys.executable, 'scripts/classify_scan_evidence.py'],
        [sys.executable, 'scripts/validate.py'],
        ['node', '--check', 'site/app.js'],
        # Preview images are downloaded into .cache/previews; build_site then
        # copies them into dist so the page never hotlinks an external image.
        [sys.executable, 'scripts/fetch_previews.py'],
    ]
    commands.append(['node', '--check', 'site/site.js'])
    commands.append([sys.executable, 'scripts/build_site.py'])
    commands.append([sys.executable, 'scripts/validate_discovery.py'])
    commands.append([sys.executable, 'scripts/validate_site.py'])
    commands.append([sys.executable, 'scripts/validate_schema_org.py'])
    # Tracked files and the finished dist/ must not name or link the people the maintainer asked to keep out.
    commands.append([sys.executable, 'scripts/privacy_guard.py'])
    with tempfile.TemporaryDirectory() as directory:
        stats, fresh, total = write_fresh_stats(Path(directory))
        print(f'Star counts: {fresh} of {total} read from GitHub.')
        environment = {**os.environ, STATS_ENV: str(stats)}
        for command in commands:
            result = subprocess.run(command, cwd=ROOT, check=False, env=environment)
            if result.returncode:
                print('Production build stopped because a required check failed.', file=sys.stderr)
                return result.returncode
    print('Production checks passed; deployable files are in dist/.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
