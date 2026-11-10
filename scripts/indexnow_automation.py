#!/usr/bin/env python3
"""Steps of the unattended IndexNow run (.github/workflows/indexnow.yml).

``wait SHA DIST`` waits, bounded, until https://awesomerea.org serves the build in DIST: its public
source-commit.txt must name SHA and its build-manifest.json must equal DIST/build-manifest.json byte for byte,
except for downloaded preview images: where only those differ, the served images and manifest replace DIST's.
Both are read with a query no edge cache has seen, so the GitHub Pages origin answers; then the manifest must
also come through the edge cache, as submit_indexnow.py reads it, which happens once the zone is purged after the
deployment. It writes ``state=live``,
``state=superseded`` (the site serves another commit and SHA is no longer the head of main, so the newer
commit's run notifies) or ``state=pending`` (SHA was not published in time; the scheduled run notifies it) to
$GITHUB_OUTPUT. It exits 1 only when the site serves SHA with bytes this build does not reproduce.

``previous OUT`` downloads the receipt of the newest earlier successful run of the workflow on the default
branch into OUT and writes that build's manifest digest as ``previous_sha256``. It writes an empty value when
there is none or when that manifest uses another format (such as an older HTML normalization), and the run
then notifies every sitemap URL, so its receipt becomes the next baseline.

The token comes from GH_TOKEN and is sent only to api.github.com. Nothing here notifies IndexNow:
submit_indexnow.py does that after verifying every canonical page of the deployment.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import secrets
import sys
import time
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_manifest import HTML_NORMALIZATION, MANIFEST_NAME  # noqa: E402
from scheduled_source_scan import ActionsAPI  # noqa: E402
from submit_indexnow import ORIGIN, fetch_bytes  # noqa: E402

WORKFLOW = 'indexnow.yml'
RECEIPT_ARTIFACT = 'indexnow-receipt'
RECEIPT_FILES = ('receipt.json', MANIFEST_NAME)
SOURCE_COMMIT = 'source-commit.txt'
POLL_SECONDS = 30
WAIT_SECONDS = 25 * 60
# Time for GitHub Pages to serve every file of a deployment once it serves its source-commit.txt.
PROPAGATION_SECONDS = 10 * 60
MAX_COMMIT_BYTES = 256
RECEIPT_PAGES = 5
MAX_RECEIPT_ARCHIVE = 16 * 1024 * 1024
MAX_MANIFEST_BYTES = 8_000_000
# Preview images are downloaded from their upstream hosts during each build, and some hosts send different
# bytes to different runners. No sitemap page is a preview, so these entries never select a URL.
PREVIEWS = 'previews/'
MAX_PREVIEW_BYTES = 8 * 1024 * 1024


def output(name: str, value: str) -> None:
    """Write one step output, or print it outside GitHub Actions."""
    path = os.environ.get('GITHUB_OUTPUT')
    if path:
        with open(path, 'a', encoding='utf-8') as stream:
            stream.write(f'{name}={value}\n')
    print(f'{name}={value}')


def api() -> ActionsAPI:
    repository, token = os.environ.get('GITHUB_REPOSITORY', ''), os.environ.get('GH_TOKEN', '')
    if not token:
        raise ValueError('GH_TOKEN is required')
    return ActionsAPI(repository, token)


def default_head(github) -> str:
    repository = github.get('')
    return github.get(f"branches/{repository['default_branch']}")['commit']['sha']


def uncached(name: str) -> str:
    """A URL of a public file with a query no edge cache has seen, so the origin serves it."""
    return f'{ORIGIN}/{name}?indexnow={secrets.token_hex(8)}'


def differs_only_in_previews(served: bytes, built: bytes) -> bool:
    """Whether two build manifests agree on everything except downloaded preview images."""
    try:
        served, built = json.loads(served), json.loads(built)
    except ValueError:
        return False
    if not (isinstance(served, dict) and isinstance(built, dict)
            and isinstance(served.get('files'), dict) and isinstance(built.get('files'), dict)):
        return False

    def pages(manifest):
        files = {name: entry for name, entry in manifest['files'].items() if not name.startswith(PREVIEWS)}
        return {**manifest, 'files': files}
    return pages(served) == pages(built)



def served_previews(served: bytes, built: bytes, read) -> dict[str, bytes] | None:
    """The preview files the site serves where SERVED differs from BUILT, each matching SERVED's entry, or None."""
    served_files, built_files = json.loads(served)['files'], json.loads(built)['files']
    previews = {}
    for name in sorted(set(served_files) | set(built_files)):
        if served_files.get(name) == built_files.get(name):
            continue
        entry = served_files.get(name)
        if not re.fullmatch(r'previews/(?:thumbs/)?[A-Za-z0-9][A-Za-z0-9._-]*', name) or not isinstance(entry, dict):
            return None
        body = read(uncached(name), MAX_PREVIEW_BYTES)
        if body is None or len(body) != entry.get('bytes') or hashlib.sha256(body).hexdigest() != entry.get('sha256'):
            return None
        previews[name] = body
    return previews


def wait_for_deployment(sha: str, dist: Path, *, github=None, fetch=fetch_bytes, clock=time.monotonic,
                        sleep=time.sleep, wait_seconds=WAIT_SECONDS) -> str:
    """Return 'live', 'superseded' or 'pending'; raise when the site serves SHA with other bytes."""
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Expected a full commit SHA')
    expected = (Path(dist) / MANIFEST_NAME).read_bytes()
    github = github or api()
    deadline, differs_since = clock() + wait_seconds, None

    def read(url, limit):
        try:
            return fetch(url, limit)
        except Exception as error:  # A transient fetch failure is retried until the deadline.
            print(f'{url.split("?")[0]} not readable yet: {type(error).__name__}', flush=True)
            return None

    while True:
        served = read(uncached(SOURCE_COMMIT), MAX_COMMIT_BYTES)
        served = served.decode('ascii', 'replace').strip() if served is not None else None
        if served == sha:
            origin = read(uncached(MANIFEST_NAME), MAX_MANIFEST_BYTES)
            build, previews = expected, {}
            if origin is not None and origin != expected and differs_only_in_previews(origin, expected):
                # The served preview bytes, verified against the served manifest, take the place of this build's.
                previews = served_previews(origin, expected, read)
                build = origin if previews is not None else expected
            if origin == build:
                differs_since = None
                # submit_indexnow.py verifies through the edge cache, which keeps the previous build until it is purged.
                if read(ORIGIN + '/' + MANIFEST_NAME, MAX_MANIFEST_BYTES) == build:
                    if previews:
                        for name, body in previews.items():
                            (Path(dist) / name).write_bytes(body)
                        (Path(dist) / MANIFEST_NAME).write_bytes(build)
                        print(f'The site serves {len(previews)} downloaded preview image(s) with other bytes; '
                              'DIST now holds the served copies', flush=True)
                    return 'live'
                status = 'the edge cache still serves the previous build'
            elif origin is not None:
                differs_since = differs_since if differs_since is not None else clock()
                if clock() - differs_since > PROPAGATION_SECONDS:
                    raise ValueError(f'awesomerea.org serves {sha[:12]} with a different build than a fresh build of it; '
                                     'the site build must be reproducible for IndexNow verification')
                status = 'its manifest differs from this build'
            else:
                status = 'its manifest is not readable'
        else:
            differs_since = None
            if served is not None and default_head(github) != sha:
                # The publication follows the head of main; that commit's own run notifies everything since the last receipt.
                return 'superseded'
            status = f'it serves {(served or "nothing readable")[:12]}'
        if clock() > deadline:
            return 'pending'
        print(f'Waiting for awesomerea.org to serve {sha[:12]}: {status}', flush=True)
        sleep(POLL_SECONDS)


def read_receipt(archive: bytes) -> tuple[dict, bytes]:
    """Validate a receipt artifact: exactly the receipt and its manifest, the manifest matching its digest."""
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        members = {info.filename: info for info in bundle.infolist()}
        if set(members) != set(RECEIPT_FILES) or any(info.file_size > MAX_MANIFEST_BYTES for info in members.values()):
            raise ValueError('A receipt artifact must hold only receipt.json and build-manifest.json')
        receipt = json.loads(bundle.read('receipt.json').decode('utf-8'))
        manifest = bundle.read(MANIFEST_NAME)
    if (not isinstance(receipt, dict) or receipt.get('schema_version') != 1 or receipt.get('site') != ORIGIN
            or receipt.get('manifest_sha256') != hashlib.sha256(manifest).hexdigest()):
        raise ValueError('The receipt does not describe its manifest')
    return receipt, manifest


def previous_receipt(directory: Path, *, github=None, current_run: str | None = None) -> str:
    """Save the newest earlier receipt into ``directory``; return its manifest digest, or '' when none exists."""
    github = github or api()
    branch = github.get('')['default_branch']
    runs = []
    # Runs that ended pending or superseded keep no receipt, so look past them: up to 500 successful runs.
    for page in range(1, RECEIPT_PAGES + 1):
        batch = github.get(f'actions/workflows/{WORKFLOW}/runs?branch={branch}&status=success&per_page=100&page={page}')['workflow_runs']
        runs += batch
        if len(batch) < 100:
            break
    for run in sorted(runs, key=lambda item: item['id'], reverse=True):
        if str(run['id']) == str(current_run) or run.get('path', f'.github/workflows/{WORKFLOW}') != f'.github/workflows/{WORKFLOW}':
            continue
        if run.get('head_branch') != branch or run.get('event') not in ('workflow_dispatch', 'schedule'):
            continue
        artifacts = github.get(f"actions/runs/{run['id']}/artifacts?per_page=30")['artifacts']
        for artifact in artifacts:
            if artifact.get('name') != RECEIPT_ARTIFACT or artifact.get('expired'):
                continue
            if not 0 < artifact.get('size_in_bytes', 0) <= MAX_RECEIPT_ARCHIVE:
                continue
            directory.mkdir(parents=True, exist_ok=True)
            archive = directory / 'receipt.zip'
            github.download(f"actions/artifacts/{artifact['id']}/zip", archive)
            receipt, manifest = read_receipt(archive.read_bytes())
            archive.unlink()
            try:
                document = json.loads(manifest.decode('utf-8'))
            except (UnicodeError, json.JSONDecodeError):
                document = {}
            if (not isinstance(document, dict) or document.get('schema_version') != 1
                    or document.get('html_normalization') != HTML_NORMALIZATION):
                # A baseline written under another manifest format cannot be diffed; one full notification
                # makes this run's receipt the new baseline instead of failing every later run.
                print(f"The newest receipt (run {run['id']}) uses another manifest format: every sitemap URL will be notified.")
                return ''
            (directory / MANIFEST_NAME).write_bytes(manifest)
            (directory / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
            print(f"Baseline: receipt of run {run['id']} ({receipt.get('recorded_at')}, manifest {receipt['manifest_sha256'][:16]})")
            return receipt['manifest_sha256']
    print('No earlier receipt: every sitemap URL will be notified.')
    return ''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    wait = commands.add_parser('wait', help='Wait until awesomerea.org serves this build')
    wait.add_argument('sha')
    wait.add_argument('dist', type=Path)
    previous = commands.add_parser('previous', help='Fetch the previous run receipt')
    previous.add_argument('directory', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'wait':
            state = wait_for_deployment(args.sha, args.dist)
            output('state', state)
            if state == 'pending':
                print(f'::warning::awesomerea.org did not serve this build of {args.sha[:12]}, through its edge cache, within '
                      f'{WAIT_SECONDS // 60} minutes; the scheduled run notifies its pages once it does.')
        else:
            output('previous_sha256', previous_receipt(args.directory, current_run=os.environ.get('GITHUB_RUN_ID')))
    except (ValueError, KeyError, OSError, zipfile.BadZipFile, json.JSONDecodeError) as error:
        print(f'::error::{error}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
