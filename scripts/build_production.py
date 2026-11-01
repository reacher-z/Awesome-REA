#!/usr/bin/env python3
"""Validate the collection and browser script before producing deployable files."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fontawesome-assets-url', help='Existing licensed icon asset origin; no fonts are added to Git')
    args = parser.parse_args()
    commands = [
        [sys.executable, 'scripts/validate.py'],
        ['node', '--check', 'site/app.js'],
        # Preview images are downloaded into .cache/previews; build_site then
        # copies them into dist so the page never hotlinks an external image.
        [sys.executable, 'scripts/fetch_previews.py'],
    ]
    build = [sys.executable, 'scripts/build_site.py']
    if args.fontawesome_assets_url:
        build.extend(['--fontawesome-assets-url', args.fontawesome_assets_url])
    commands.append(build)
    commands.append([sys.executable, 'scripts/validate_discovery.py'])
    commands.append([sys.executable, 'scripts/validate_site.py'])
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            print('Production build stopped because a required check failed.', file=sys.stderr)
            return result.returncode
    print('Production checks passed; deployable files are in dist/.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
