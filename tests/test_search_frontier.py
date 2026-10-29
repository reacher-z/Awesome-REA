"""Partition discovery must not truncate, widen scope, or lose pending identities."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import search_frontier as frontier

BASES = ['topic:reverse-engineering', 'topic:decompiler']
LOW, HIGH = '2026-01-01T00:00:00Z', '2026-01-01T00:00:07Z'


def state(bases=None, low=LOW, high=HIGH):
    return frontier.new_frontier(since=low, until=high, approved_queries=BASES if bases is None else bases)


def repo(identifier, **changes):
    name = f'example/tool-{identifier}'
    return {'id': identifier, 'full_name': name, 'node_id': f'R_{identifier}', 'html_url': 'https://github.com/' + name,
            'private': False, 'fork': False, 'archived': False, 'created_at': LOW, **changes}


def response(items=(), total=None, incomplete=False):
    return {'total_count': len(items) if total is None else total, 'incomplete_results': incomplete, 'items': list(items)}


class PartitionTests(unittest.TestCase):
    def test_request_preserves_scope_and_eligibility_while_adding_dates(self):
        document = state()
        original = copy.deepcopy(document)
        request = frontier.next_request(document)
        self.assertEqual(document, original)
        self.assertEqual(request['per_page'], 100)
        query = parse_qs(urlsplit(request['path']).query)['q'][0]
        self.assertEqual(query, BASES[0] + ' is:public fork:false archived:false created:' + LOW + '..' + HIGH)
        self.assertEqual(query, request['query'])

    def test_result_cap_splits_without_overlap_or_discarding_discovered_items(self):
        document = state([BASES[0]])
        request = frontier.next_request(document)
        outcome = frontier.record_response(document, request, response([repo(1)], total=1001), observed_at=LOW)
        self.assertEqual(outcome['partition_status'], 'split')
        parent, left, right = document['partitions']
        self.assertEqual(left['low'], parent['low'])
        self.assertEqual(left['high'] + 1, right['low'])
        self.assertEqual(right['high'], parent['high'])
        self.assertEqual(len(frontier.pending_candidates(document)), 1)
        frontier.validate_frontier(document, approved_queries=BASES)

    def test_incomplete_and_mismatched_pages_are_split_not_marked_complete(self):
        for payload in (response([repo(1)], incomplete=True), response([repo(1)], total=2)):
            with self.subTest(payload=payload):
                document = state([BASES[0]])
                frontier.record_response(document, frontier.next_request(document), payload)
                self.assertEqual(document['partitions'][0]['status'], 'split')
                self.assertFalse(frontier.summary(document)['traversal_finished'])

    def test_saturated_second_is_blocked_and_never_claims_global_coverage(self):
        document = state([BASES[0]], high=LOW)
        frontier.record_response(document, frontier.next_request(document), response([repo(1)], total=2000))
        self.assertEqual(document['partitions'][0]['status'], 'blocked')
        summary = frontier.summary(document)
        self.assertFalse(summary['traversal_finished'])
        self.assertFalse(summary['global_completeness_established'])
        self.assertFalse(summary['readme_successes_measured_here'])

    def test_exactly_1000_results_can_finish_but_no_page11_is_created(self):
        document = state([BASES[0]])
        for page in range(10):
            request = frontier.next_request(document)
            self.assertEqual(request['page'], page + 1)
            items = [repo(i) for i in range(page * 100 + 1, page * 100 + 101)]
            frontier.record_response(document, request, response(items, total=1000))
        self.assertIsNone(frontier.next_request(document))
        self.assertEqual(frontier.summary(document)['candidate_identities'], 1000)
        self.assertEqual(document['partitions'][0]['status'], 'complete')

    def test_duplicate_ids_across_pages_prevent_false_completion(self):
        document = state([BASES[0]])
        items = [repo(i) for i in range(1, 101)]
        frontier.record_response(document, frontier.next_request(document), response(items, total=200))
        frontier.record_response(document, frontier.next_request(document), response(items, total=200))
        self.assertEqual(document['partitions'][0]['status'], 'split')
        self.assertEqual(len(document['candidates']), 100)

    def test_changed_counts_do_not_restart_old_page_or_claim_completeness(self):
        document = state([BASES[0]])
        frontier.record_response(document, frontier.next_request(document), response([repo(i) for i in range(1, 101)], total=150))
        request = frontier.next_request(document)
        frontier.record_response(document, request, response([repo(101)], total=101))
        self.assertEqual(document['partitions'][0]['status'], 'split')
        with self.assertRaisesRegex(ValueError, 'Stale'):
            frontier.record_response(document, request, response([repo(101)]))


class QueueTests(unittest.TestCase):
    def test_offsets_page_only_due_unacknowledged_candidates_in_fair_order(self):
        document = state([BASES[0]])
        frontier.record_response(document, frontier.next_request(document), response([repo(i) for i in range(1, 9)]))
        frontier.acknowledge_candidates(document, [2, 7], checkpoint_sha256='a' * 64)
        frontier.defer_candidates(document, [1, 4], reason='retry', retry_after_seconds=60, observed_at=LOW)
        moment = frontier.utc_seconds(LOW)
        before = copy.deepcopy(document)
        for instant, expected in ((moment + 1, [3, 5, 6, 8]), (moment + 60, [3, 5, 6, 8, 1, 4])):
            with self.subTest(now=instant):
                pages = [frontier.pending_candidates(document, limit=2, offset=offset, now=instant)
                         for offset in range(0, len(expected) + 2, 2)]
                self.assertEqual([row['id'] for page in pages for row in page], expected)
                self.assertEqual(pages[-1], [])
        self.assertEqual(document, before)
        for offset in (-1, True, 1.5, '1'):
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                frontier.pending_candidates(document, offset=offset)
        with self.assertRaises(ValueError):
            frontier.pending_candidates(document, limit=1001)

    def test_deferred_ineligible_candidates_do_not_starve_unattempted_candidates(self):
        document = state([BASES[0]])
        frontier.record_response(document, frontier.next_request(document), response([repo(1), repo(2), repo(3)]))
        moment = frontier.utc_seconds(LOW)
        frontier.defer_candidates(document, [1, 2], reason='ineligible', retry_after_seconds=86400, observed_at=LOW)
        self.assertEqual([r['id'] for r in frontier.pending_candidates(document, now=moment + 1)], [3])
        self.assertEqual([r['id'] for r in frontier.pending_candidates(document, now=moment + 86400)], [3, 1, 2])
        self.assertIsNone(document['candidates']['1']['checkpoint_sha256'])
        self.assertEqual(document['candidates']['1']['attempts'], 1)
        with self.assertRaises(ValueError):
            frontier.defer_candidates(document, [3], reason='raw error with private text', retry_after_seconds=60)
        with self.assertRaises(ValueError):
            frontier.defer_candidates(document, [3], reason='retry', retry_after_seconds=1)
        frontier.validate_frontier(document, approved_queries=BASES)

    def test_query_observations_preserve_historical_request_times_and_runs(self):
        document = state([BASES[0]])
        request = frontier.next_request(document)
        frontier.record_failure(document, request, reason='http-429', observed_at=LOW, run_id=LOW)
        frontier.record_response(document, frontier.next_request(document, now=frontier.utc_seconds(LOW) + 60),
                                 response([repo(1)]), observed_at=HIGH, run_id=HIGH)
        rows = frontier.query_observations(document)
        self.assertEqual([row['run_id'] for row in rows], [LOW, HIGH])
        self.assertEqual(rows[0]['http_status'], 429)
        self.assertEqual(rows[1]['query'], request['query'])
        self.assertEqual(frontier.query_observations(document, start=1), rows[1:])
        self.assertEqual(frontier.pending_candidates(document)[0]['metadata_observed_at'], HIGH)

    def test_cross_query_duplicates_keep_actual_query_provenance_and_delivery_state(self):
        document = state()
        first = frontier.next_request(document)
        frontier.record_response(document, first, response([repo(1)]), observed_at=LOW)
        second = frontier.next_request(document)
        frontier.record_response(document, second, response([repo(1)]), observed_at=LOW)
        self.assertEqual(len(document['candidates']), 1)
        batch = frontier.pending_candidates(document)
        self.assertEqual(batch[0]['_matched_queries'], [first['query'], second['query']])
        with self.assertRaises(ValueError):
            frontier.acknowledge_candidates(document, [1], checkpoint_sha256='not-a-durable-hash')
        frontier.acknowledge_candidates(document, [1], checkpoint_sha256='a' * 64)
        self.assertEqual(frontier.pending_candidates(document), [])
        self.assertEqual(frontier.summary(document)['candidate_identities'], 1)

    def test_private_malformed_fork_archived_and_out_of_window_items_are_not_persisted(self):
        document = state([BASES[0]])
        bad = [repo(1, private=True, description='private payload'), repo(2, fork=True), repo(3, archived=True),
               repo(4, html_url='https://example.org/'), repo(5, created_at='2025-01-01T00:00:00Z'),
               repo(6, node_id='invalid token!'), repo(True), None]
        result = frontier.record_response(document, frontier.next_request(document), response(bad))
        self.assertEqual(result['rejected_items'], len(bad))
        self.assertEqual(document['candidates'], {})
        self.assertNotIn('private payload', json.dumps(document))
        self.assertNotIn('example.org', json.dumps(document))

    def test_known_scan_ids_are_not_requeued_or_miscounted_as_readme_successes(self):
        document = state([BASES[0]])
        outcome = frontier.record_response(document, frontier.next_request(document), response([repo(1), repo(2)]), known_ids={1})
        self.assertEqual(outcome['new_candidates'], 1)
        self.assertEqual([r['id'] for r in frontier.pending_candidates(document)], [2])
        self.assertEqual(document['partitions'][0]['seen_ids'], [1, 2])

    def test_request_backoff_preserves_cursor_and_other_roots_can_progress(self):
        document = state()
        request = frontier.next_request(document)
        frontier.record_failure(document, request, reason='http-429', retry_after_seconds=300, observed_at=LOW)
        self.assertEqual(document['partitions'][0]['page'], 1)
        following = frontier.next_request(document, now=frontier.utc_seconds(LOW) + 1)
        self.assertNotEqual(following['partition_id'], request['partition_id'])
        frontier.record_response(document, following, response())
        self.assertIsNone(frontier.next_request(document, now=frontier.utc_seconds(LOW) + 1))
        self.assertEqual(frontier.next_request(document, now=frontier.utc_seconds(LOW) + 300)['page'], 1)

    def test_candidate_budget_rejects_page_without_losing_its_cursor_or_any_ids(self):
        document = state([BASES[0]])
        before = copy.deepcopy(document)
        with patch.object(frontier, 'MAX_CANDIDATES', 1), self.assertRaisesRegex(ValueError, 'Candidate budget'):
            frontier.record_response(document, frontier.next_request(document), response([repo(1), repo(2)]))
        self.assertEqual(document, before)

    def test_explicit_query_append_and_date_extension_do_not_restart_completed_work(self):
        document = state([BASES[0]])
        frontier.record_response(document, frontier.next_request(document), response())
        original = copy.deepcopy(document['partitions'][0])
        with self.assertRaises(ValueError):
            frontier.add_queries(document, ['topic:unapproved'], approved_queries=BASES)
        frontier.add_queries(document, [BASES[1]], approved_queries=BASES)
        frontier.extend_until(document, '2026-01-01T00:00:09Z')
        self.assertEqual(document['partitions'][0], original)
        self.assertEqual(len(document['partitions']), 4)
        self.assertEqual(document['partitions'][-1]['low'], frontier.utc_seconds(HIGH) + 1)


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.path = self.root / 'frontier.json'

    def test_saved_page_and_pending_queue_resume_together(self):
        document = state([BASES[0]])
        request = frontier.next_request(document)
        frontier.record_response(document, request, response([repo(i) for i in range(1, 101)], total=150))
        frontier.save_frontier(self.path, document, approved_queries=BASES, cache_root=self.root)
        restored = frontier.load_frontier(self.path, approved_queries=BASES, cache_root=self.root)
        self.assertEqual(frontier.next_request(restored)['page'], 2)
        self.assertEqual(len(frontier.pending_candidates(restored)), 100)
        self.assertEqual(restored, document)

    def test_scope_mutation_unknown_fields_and_duplicate_json_keys_are_rejected(self):
        document = state([BASES[0]])
        document['roots'][0] = 'topic:unapproved'
        with self.assertRaises(ValueError):
            frontier.save_frontier(self.path, document, approved_queries=BASES, cache_root=self.root)
        document = state([BASES[0]]); document['raw_api_body'] = 'not retained'
        with self.assertRaises(ValueError):
            frontier.save_frontier(self.path, document, approved_queries=BASES, cache_root=self.root)
        self.path.write_text('{"schema_version":1,"schema_version":1}', encoding='utf-8')
        with self.assertRaises(ValueError):
            frontier.load_frontier(self.path, approved_queries=BASES, cache_root=self.root)

    def test_state_limit_leaves_existing_file_unchanged_and_cache_paths_are_enforced(self):
        document = state([BASES[0]])
        frontier.save_frontier(self.path, document, approved_queries=BASES, cache_root=self.root)
        before = self.path.read_bytes()
        with patch.object(frontier, 'MAX_STATE_BYTES', 10), self.assertRaises(ValueError):
            frontier.save_frontier(self.path, document, approved_queries=BASES, cache_root=self.root)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertFalse(self.path.with_suffix('.json.tmp').exists())
        with self.assertRaises(ValueError):
            frontier.save_frontier(self.root.parent / 'not-cache.json', document, approved_queries=BASES, cache_root=self.root)
        linked = self.root / 'link.json'; linked.symlink_to(self.path)
        with self.assertRaises(ValueError):
            frontier.load_frontier(linked, approved_queries=BASES, cache_root=self.root)

    def test_unicode_frontier_hash_and_byte_bound_include_the_final_newline(self):
        bases = ['逆向 in:readme']
        document = state(bases)
        expected = (json.dumps(document, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8')
        with patch.object(frontier, 'MAX_STATE_BYTES', len(expected)):
            fingerprint = frontier.save_frontier(self.path, document, approved_queries=bases, cache_root=self.root)
        self.assertEqual(self.path.read_bytes(), expected)
        self.assertEqual(fingerprint, hashlib.sha256(expected).hexdigest())
        with patch.object(frontier, 'MAX_STATE_BYTES', len(expected) - 1), self.assertRaises(ValueError):
            frontier.save_frontier(self.path, document, approved_queries=bases, cache_root=self.root)
        self.assertEqual(self.path.read_bytes(), expected)
        self.assertFalse(self.path.with_suffix('.json.tmp').exists())

    def test_interrupted_frontier_encoding_preserves_previous_bytes_and_state(self):
        document = state()
        frontier.save_frontier(self.path, document, approved_queries=BASES, cache_root=self.root)
        before, original = self.path.read_bytes(), copy.deepcopy(document)

        def interrupted_encoder(encoder, value, *args, **kwargs):
            yield '{"schema_version":1,'
            raise OSError('simulated write interruption')

        with patch.object(json.JSONEncoder, 'iterencode', interrupted_encoder), self.assertRaises(OSError):
            frontier.save_frontier(self.path, document, approved_queries=BASES, cache_root=self.root)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(document, original)
        self.assertFalse(self.path.with_suffix('.json.tmp').exists())

    def test_invalid_query_overrides_cannot_relax_eligibility(self):
        for base in ('topic:decompiler OR topic:games', 'topic:decompiler fork:true', 'topic:decompiler created:>2020-01-01', 'topic:decompiler is:private'):
            with self.subTest(base=base), self.assertRaises(ValueError):
                state([base])

    def test_forged_completion_missing_split_children_and_candidate_provenance_fail(self):
        document = state([BASES[0]])
        document['partitions'][0]['status'] = 'complete'
        with self.assertRaises(ValueError):
            frontier.validate_frontier(document, approved_queries=BASES)
        document = state([BASES[0]])
        frontier.record_response(document, frontier.next_request(document), response([repo(1)], total=1001))
        document['partitions'].pop()
        with self.assertRaises(ValueError):
            frontier.validate_frontier(document, approved_queries=BASES)
        document = state([BASES[0]])
        frontier.record_response(document, frontier.next_request(document), response([repo(1)]))
        document['candidates']['1']['id'] = 2
        document['candidates']['2'] = document['candidates'].pop('1')
        with self.assertRaises(ValueError):
            frontier.validate_frontier(document, approved_queries=BASES)


if __name__ == '__main__':
    unittest.main()
