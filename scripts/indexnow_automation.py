#!/usr/bin/env python3
"""Steps of the unattended IndexNow run (.github/workflows/indexnow.yml).

``wait SHA DIST`` waits, bounded, until https://awesomerea.org serves the build in DIST: its public
build-manifest.json must equal DIST/build-manifest.json byte for byte. The Cloudflare Pages check run on SHA
tells a deployment still in progress from one that failed or that a newer commit replaced. It writes
``state=live`` or ``state=superseded`` to $GITHUB_OUTPUT and exits 1 when the deployment failed, did not go
live in time, or went live with bytes this build does not reproduce.

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
CLOUDFLARE_APP = 'cloudflare-workers-and-pages'
CLOUDFLARE_CHECK = 'Cloudflare Pages'
POLL_SECONDS = 30
WAIT_SECONDS = 25 * 60
# Time for the edge to serve a deployment that Cloudflare Pages reports complete.
PROPAGATION_SECONDS = 3 * 60
MAX_RECEIPT_ARCHIVE = 16 * 1024 * 1024
MAX_MANIFEST_BYTES = 8_000_000


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


def deployment_state(github, sha: str) -> str:
    """'success', 'failure', 'replaced' or 'pending' from the newest Cloudflare Pages check run on ``sha``."""
    runs = github.get(f'commits/{sha}/check-runs?check_name={CLOUDFLARE_CHECK.replace(" ", "%20")}&per_page=30')['check_runs']
    runs = [run for run in runs if (run.get('app') or {}).get('slug') == CLOUDFLARE_APP]
    if not runs:
        return 'pending'
    latest = max(runs, key=lambda run: run['id'])
    if latest.get('status') != 'completed':
        return 'pending'
    conclusion = latest.get('conclusion')
    if conclusion == 'success':
        return 'success'
    return 'replaced' if conclusion in ('cancelled', 'skipped', 'stale', 'neutral') else 'failure'


def default_head(github) -> str:
    repository = github.get('')
    return github.get(f"branches/{repository['default_branch']}")['commit']['sha']


def wait_for_deployment(sha: str, dist: Path, *, github=None, fetch=fetch_bytes, clock=time.monotonic,
                        sleep=time.sleep, wait_seconds=WAIT_SECONDS) -> str:
    """Return 'live' or 'superseded'; raise when the deployment cannot be confirmed as this build."""
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Expected a full commit SHA')
    expected = (Path(dist) / MANIFEST_NAME).read_bytes()
    github = github or api()
    deadline, deployed_since = clock() + wait_seconds, None
    while True:
        try:
            live = fetch(ORIGIN + '/' + MANIFEST_NAME, MAX_MANIFEST_BYTES)
        except Exception as error:  # A transient fetch failure is retried until the deadline.
            print(f'Live manifest not readable yet: {type(error).__name__}', flush=True)
            live = None
        if live == expected:
            return 'live'
        state = deployment_state(github, sha)
        if state == 'failure':
            raise ValueError(f'Cloudflare Pages reports a failed deployment of {sha[:12]}')
        if state in ('success', 'replaced'):
            if default_head(github) != sha:
                # A newer commit is or will be live; its own run notifies everything since the last receipt.
                return 'superseded'
            deployed_since = deployed_since if deployed_since is not None else clock()
            if state == 'replaced' or clock() - deployed_since > PROPAGATION_SECONDS:
                raise ValueError(f'awesomerea.org serves a different build than a fresh build of {sha[:12]}; '
                                 'the site build must be reproducible for IndexNow verification')
        if clock() > deadline:
            raise ValueError(f'The deployment of {sha[:12]} did not go live within {wait_seconds // 60} minutes')
        print(f'Waiting for the deployment of {sha[:12]} (Cloudflare Pages: {state})', flush=True)
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
    runs = github.get(f'actions/workflows/{WORKFLOW}/runs?branch={branch}&status=success&per_page=30')['workflow_runs']
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
            output('state', wait_for_deployment(args.sha, args.dist))
        else:
            output('previous_sha256', previous_receipt(args.directory, current_run=os.environ.get('GITHUB_RUN_ID')))
    except (ValueError, KeyError, OSError, zipfile.BadZipFile, json.JSONDecodeError) as error:
        print(f'::error::{error}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
