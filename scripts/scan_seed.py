#!/usr/bin/env python3
"""Package and explicitly import data-only, gzip-bounded private scan seeds.

The manifest describes existing local evidence. It is never a GitHub Actions
receipt and never claims that its captures were made by the importing run.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
from pathlib import Path
import re
import zlib

import scheduled_source_scan as scheduled

MAX_COMPRESSED_BYTES = 50 * 1024 * 1024
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_EVIDENCE_FRONTIERS = 4
CHECKPOINT = 'scan-seed-checkpoint.json.gz'
FRONTIER = 'scan-seed-frontier.json.gz'
MANIFEST_KEYS = {'schema_version', 'kind', 'created_at', 'files', 'counts', 'selected_frontier', 'evidence_frontiers'}


class BoundedWriter:
    def __init__(self, stream, bound):
        self.stream, self.bound, self.written = stream, bound, 0

    def write(self, value):
        if self.written + len(value) > self.bound:
            raise ValueError('Compressed seed exceeds its Git-safe bound')
        self.written += len(value)
        return self.stream.write(value)

    def flush(self):
        return self.stream.flush()


def compress_file(source, destination, bound):
    expected = scheduled.file_info(source, bound)
    temporary = destination.with_suffix('.tmp')
    try:
        with source.open('rb') as incoming, temporary.open('wb') as output:
            with gzip.GzipFile(filename='', mode='wb', mtime=0,
                               fileobj=BoundedWriter(output, MAX_COMPRESSED_BYTES)) as compressed:
                actual = scheduled.stream_copy(incoming, compressed, bound)
        if actual != expected:
            raise ValueError('Seed source changed while being packaged')
        packed = scheduled.file_info(temporary, MAX_COMPRESSED_BYTES)
        temporary.replace(destination)
        return {'compressed': packed, 'uncompressed': actual}
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def decompress_file(source, destination, description, bound):
    if scheduled.file_info(source, MAX_COMPRESSED_BYTES) != description['compressed']:
        raise ValueError('Compressed seed hash or size does not match the manifest')
    temporary = destination.with_suffix('.tmp')
    try:
        compressed_hash, expanded_hash = hashlib.sha256(), hashlib.sha256()
        compressed_size = expanded_size = 0
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        with source.open('rb') as incoming, temporary.open('wb') as output:
            while block := incoming.read(scheduled.CHUNK_BYTES):
                if compressed_size == 0:
                    # No filename, comment or extra gzip metadata may disclose a local path.
                    if len(block) < 10 or block[:4] != b'\x1f\x8b\x08\x00' or block[4:8] != b'\x00' * 4:
                        raise ValueError('Seed gzip header must be deterministic without optional metadata')
                compressed_size += len(block); compressed_hash.update(block)
                if compressed_size > MAX_COMPRESSED_BYTES or decoder.eof:
                    raise ValueError('Seed gzip exceeds bounds or contains trailing members')
                while block:
                    expanded = decoder.decompress(block, min(scheduled.CHUNK_BYTES, bound - expanded_size + 1))
                    expanded_size += len(expanded); expanded_hash.update(expanded)
                    if expanded_size > bound:
                        raise ValueError('Expanded seed exceeds its byte bound')
                    output.write(expanded)
                    if decoder.unused_data:
                        raise ValueError('Seed gzip contains trailing data or concatenated members')
                    block = decoder.unconsumed_tail
        actual = {'sha256': expanded_hash.hexdigest(), 'bytes': expanded_size}
        compressed = {'sha256': compressed_hash.hexdigest(), 'bytes': compressed_size}
        if not decoder.eof or compressed != description['compressed'] or actual != description['uncompressed']:
            raise ValueError('Expanded seed hash or size does not match the manifest')
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def verify_frontier(document, state):
    scheduled.paired_ack_guard(document, state)
    if not {'scan-' + key for key in state['candidates']} <= scheduled.known_ids(document):
        raise ValueError('Frozen checkpoint must retain all imported frontier identities')


def pack_seed(checkpoint, frontier, evidence_frontiers, destination):
    """Write only validated terminal evidence; never serialize a cache directory."""
    if len(evidence_frontiers) > MAX_EVIDENCE_FRONTIERS:
        raise ValueError('Too many evidence frontiers')
    names = [f'scan-seed-evidence-frontier-{index + 1}.json.gz' for index in range(len(evidence_frontiers))]
    paths = [(CHECKPOINT, checkpoint, scheduled.MAX_SCAN_BYTES), (FRONTIER, frontier, scheduled.MAX_FRONTIER_BYTES)]
    paths.extend((name, path, scheduled.MAX_FRONTIER_BYTES) for name, path in zip(names, evidence_frontiers))
    originals = {name: scheduled.file_info(path, bound) for name, path, bound in paths}
    if sum(item['bytes'] for item in originals.values()) > scheduled.MAX_TOTAL_BYTES:
        raise ValueError('Seed inputs exceed the aggregate evidence bound')
    document, checkpoint_sha = scheduled.read_snapshot(checkpoint)
    selected = scheduled.read_frontier(frontier)
    verify_frontier(document, selected)
    for path in evidence_frontiers:
        state = scheduled.read_frontier(path)
        verify_frontier(document, state)
        del state
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError('Seed destination must be empty; preserve earlier packages')
    files = {name: compress_file(path, destination / name, bound) for name, path, bound in paths}
    if (files[CHECKPOINT]['uncompressed']['sha256'] != checkpoint_sha
            or any(files[name]['uncompressed'] != originals[name] for name in originals)):
        raise ValueError('Seed input changed after validation; package frozen terminal evidence')
    manifest = {'schema_version': 1, 'kind': 'manual-local-union', 'created_at': scheduled.now(),
                'files': files, 'counts': scheduled.counts(document),
                'selected_frontier': FRONTIER, 'evidence_frontiers': names}
    scheduled.write_json(destination / 'manifest.json', manifest)
    scheduled.file_info(destination / 'manifest.json', MAX_MANIFEST_BYTES)
    return manifest


def load_seed(manifest_path, destination):
    manifest, fingerprint = read_manifest(manifest_path)
    if (not isinstance(manifest, dict) or set(manifest) != MANIFEST_KEYS
            or manifest['schema_version'] != 1 or type(manifest['schema_version']) is not int
            or manifest['kind'] != 'manual-local-union' or manifest['selected_frontier'] != FRONTIER
            or not isinstance(manifest['evidence_frontiers'], list)
            or len(manifest['evidence_frontiers']) > MAX_EVIDENCE_FRONTIERS):
        raise ValueError('Invalid private seed manifest')
    expected_extras = [f'scan-seed-evidence-frontier-{index + 1}.json.gz'
                       for index in range(len(manifest['evidence_frontiers']))]
    if manifest['evidence_frontiers'] != expected_extras:
        raise ValueError('Unexpected private seed member names')
    expected_names = {CHECKPOINT, FRONTIER, *expected_extras}
    if not isinstance(manifest['files'], dict) or set(manifest['files']) != expected_names:
        raise ValueError('Missing or unexpected private seed member')
    scheduled.validate_seed_counts(manifest['counts'])
    if (not isinstance(manifest['created_at'], str)
            or scheduled.dt.datetime.fromisoformat(manifest['created_at'].replace('Z', '+00:00')).tzinfo is None):
        raise ValueError('Seed creation time must include its timezone')
    if scheduled.private_json_locations(manifest):
        raise ValueError('Seed manifest contains private material; values withheld')
    for name, description in manifest['files'].items():
        if not isinstance(description, dict) or set(description) != {'compressed', 'uncompressed'}:
            raise ValueError('Invalid private seed member fingerprints')
        for encoding in ('compressed', 'uncompressed'):
            info = description[encoding]
            if (not isinstance(info, dict) or set(info) != {'sha256', 'bytes'}
                    or type(info['bytes']) is not int or info['bytes'] <= 0
                    or not isinstance(info['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', info['sha256'])):
                raise ValueError('Invalid private seed member hash or size')
        bound = scheduled.MAX_SCAN_BYTES if name == CHECKPOINT else scheduled.MAX_FRONTIER_BYTES
        if description['compressed']['bytes'] > MAX_COMPRESSED_BYTES or description['uncompressed']['bytes'] > bound:
            raise ValueError('Private seed member exceeds its size bound')
    if sum(item['uncompressed']['bytes'] for item in manifest['files'].values()) > scheduled.MAX_TOTAL_BYTES:
        raise ValueError('Seed expansion exceeds the aggregate evidence bound')
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError('Seed restore destination must be empty')
    for name, description in manifest['files'].items():
        bound = scheduled.MAX_SCAN_BYTES if name == CHECKPOINT else scheduled.MAX_FRONTIER_BYTES
        decompress_file(manifest_path.parent / name, destination / name.removesuffix('.gz'), description, bound)
    document, checkpoint_sha = scheduled.read_snapshot(destination / CHECKPOINT.removesuffix('.gz'))
    if scheduled.counts(document) != manifest['counts']:
        raise ValueError('Private seed counters disagree with its evidence')
    selected = scheduled.read_frontier(destination / FRONTIER.removesuffix('.gz'))
    verify_frontier(document, selected)
    for name in expected_extras:
        verify_frontier(document, scheduled.read_frontier(destination / name.removesuffix('.gz')))
    return document, checkpoint_sha, selected, manifest, fingerprint


def read_manifest(path):
    """Hash the exact bounded bytes that are parsed, rather than a prior open."""
    scheduled.file_info(path, MAX_MANIFEST_BYTES)
    with path.open('rb') as stream:
        raw = stream.read(MAX_MANIFEST_BYTES + 1)
    if not 0 < len(raw) <= MAX_MANIFEST_BYTES:
        raise ValueError('Private seed manifest exceeds its size bound')
    return scheduled.parse_json(raw.decode('utf-8')), hashlib.sha256(raw).hexdigest()


def import_seed(manifest_path, destination, previous, previous_sha, restored_frontier, *, worker_commit):
    if previous is not None or previous_sha is not None or restored_frontier is not None:
        raise ValueError('Later seed imports need a reviewed version-preserving merge; existing state was not changed')
    incoming, incoming_sha, selected, manifest, manifest_sha = load_seed(manifest_path, destination)
    proof = {'kind': 'manual-local-union', 'imported_at': scheduled.now(), 'manifest_sha256': manifest_sha,
             'checkpoint_sha256': incoming_sha,
             'selected_frontier_sha256': manifest['files'][FRONTIER]['uncompressed']['sha256'],
             'evidence_frontier_sha256': [manifest['files'][name]['uncompressed']['sha256']
                                         for name in manifest['evidence_frontiers']],
             'frontier_policy': 'selected-seed-frontier', 'worker_commit': worker_commit,
             'imported_counts': scheduled.counts(incoming)}
    scheduled.validate_seed_import(proof)
    return incoming, incoming_sha, selected, proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--frontier', type=Path, required=True)
    parser.add_argument('--evidence-frontier', type=Path, action='append', default=[])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = pack_seed(args.checkpoint, args.frontier, args.evidence_frontier, args.output)
    except (ValueError, KeyError, TypeError, OSError, EOFError, RecursionError, zlib.error):
        print('Seed packaging stopped: input validation or size bounds failed; values withheld.')
        return 1
    print('Prepared validated private seed:', manifest['counts']['successful_readme_scans'], 'existing successful captures.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
