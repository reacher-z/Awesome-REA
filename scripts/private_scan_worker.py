#!/usr/bin/env python3
"""Run a pinned public scanner inside a verified private worker repository."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
import zlib

import scheduled_source_scan as scheduled

CONFIG_KEYS = {'schema_version', 'scanner_repository', 'scanner_revision',
               'worker_repository', 'worker_repository_id'}


def git_value(directory, *arguments):
    result = subprocess.run(['git', '-C', str(directory), *arguments], text=True, encoding='utf-8',
                            capture_output=True, check=True)
    return result.stdout.strip()


def require_tracked_bytes(directory, path):
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(directory):
        raise ValueError('Worker evidence must be a tracked regular file inside its checkout')
    relative = str(path.resolve().relative_to(directory))
    git_value(directory, 'ls-files', '--error-unmatch', '--', relative)
    expected = git_value(directory, 'rev-parse', 'HEAD:' + relative)
    if git_value(directory, 'hash-object', '--no-filters', '--', relative) != expected:
        raise ValueError('Worker evidence bytes differ from the pinned worker revision')


def validate_config(path):
    scheduled.file_info(path, 16 * 1024)
    config = scheduled.parse_json(path.read_text(encoding='utf-8'))
    if (not isinstance(config, dict) or set(config) != CONFIG_KEYS
            or type(config['schema_version']) is not int or config['schema_version'] != 1
            or config['scanner_repository'] != 'reacher-z/Awesome-REA'
            or not isinstance(config['scanner_revision'], str)
            or not re.fullmatch('[0-9a-f]{40}', config['scanner_revision'])
            or not isinstance(config['worker_repository'], str)
            or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', config['worker_repository'])
            or type(config['worker_repository_id']) is not int or config['worker_repository_id'] <= 0):
        raise ValueError('Private worker configuration must contain real pinned identities')
    if scheduled.private_json_locations(config):
        raise ValueError('Unexpected private material in worker configuration')
    return config


def run_worker(config_path, directory, *, seed_manifest=None, bootstrap_only=False):
    config = validate_config(config_path)
    repository = os.environ.get('GITHUB_REPOSITORY')
    if (repository != config['worker_repository']
            or os.environ.get('GITHUB_REPOSITORY_ID') != str(config['worker_repository_id'])
            or os.environ.get('GITHUB_EVENT_NAME') not in ('workflow_dispatch', 'schedule')
            or os.environ.get('GITHUB_REF') != 'refs/heads/' + os.environ.get('DEFAULT_BRANCH', '')):
        raise ValueError('Private worker context does not match its pinned identity')
    source = git_value(scheduled.ROOT, 'rev-parse', 'HEAD')
    if source != config['scanner_revision'] or git_value(scheduled.ROOT, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Scanner checkout is not the exact clean pinned revision')
    worker_root = Path(git_value(config_path.parent, 'rev-parse', '--show-toplevel')).resolve()
    if (git_value(worker_root, 'rev-parse', 'HEAD') != os.environ.get('GITHUB_SHA')
            or config_path.resolve() != worker_root / 'scanner.json'
            or git_value(worker_root, 'status', '--porcelain', '--untracked-files=all')):
        raise ValueError('Worker configuration is not from the exact clean run revision')
    require_tracked_bytes(worker_root, config_path)
    if seed_manifest is not None:
        if (os.environ['GITHUB_EVENT_NAME'] != 'workflow_dispatch'
                or seed_manifest.resolve() != worker_root / 'bootstrap/manifest.json'):
            raise ValueError('A seed import must explicitly name the worker bootstrap manifest')
        require_tracked_bytes(worker_root, seed_manifest)
        from scan_seed import read_manifest
        manifest, _ = read_manifest(seed_manifest)
        files = manifest.get('files') if isinstance(manifest, dict) else None
        if (not isinstance(files, dict) or not 2 <= len(files) <= 6
                or any(not isinstance(name, str) or not re.fullmatch(r'scan-seed-(?:checkpoint|frontier|evidence-frontier-[1-4])\.json\.gz', name)
                       for name in files)):
            raise ValueError('Unexpected private seed members')
        for name in files:
            require_tracked_bytes(worker_root, seed_manifest.parent / name)
    if bootstrap_only and seed_manifest is None:
        raise ValueError('Bootstrap-only mode requires a seed import')
    cache = (scheduled.ROOT / '.cache').resolve()
    if not directory.resolve().is_relative_to(cache):
        raise ValueError('Private worker state must remain in ignored scanner cache storage')
    token = os.environ.get('GH_TOKEN', '')
    if not token:
        raise ValueError('The ephemeral repository token is unavailable')
    api = scheduled.ActionsAPI(repository, token, deadline=time.monotonic() + 30)
    actual = api.get('')
    if (actual.get('private') is not True or actual.get('full_name') != repository
            or type(actual.get('id')) is not int or actual['id'] != config['worker_repository_id']
            or actual.get('archived') is not False or actual.get('disabled') is not False):
        raise ValueError('Worker repository is not the expected active private repository')
    if actual.get('default_branch') != os.environ.get('DEFAULT_BRANCH'):
        raise ValueError('Worker branch does not match its actual default branch')
    return scheduled.orchestrate(directory, manual_seed=seed_manifest, bootstrap_only=bootstrap_only,
                                 execution_source={'repository': config['scanner_repository'], 'commit': source})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--seed-manifest', type=Path)
    parser.add_argument('--bootstrap-only', action='store_true')
    args = parser.parse_args()
    try:
        return run_worker(args.config, args.directory, seed_manifest=args.seed_manifest,
                          bootstrap_only=args.bootstrap_only)
    except (ValueError, KeyError, TypeError, OSError, EOFError, RecursionError,
            subprocess.CalledProcessError, json.JSONDecodeError, zlib.error):
        print('Private scan stopped: identity, input, privacy or runtime validation failed; values withheld.')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
