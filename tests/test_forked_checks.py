"""Checks run in forked workers give the result of running them one after another."""
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import forked_checks


def square(value):
    if value == 7:
        raise AssertionError('seven')
    return value * value


def fail(message):
    raise AssertionError(message)


class ForkedChecksTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(forked_checks, 'workers', return_value=4)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_ordered_map_keeps_the_order_and_raises_at_the_failing_item(self):
        values = list(range(200))
        self.assertEqual(list(forked_checks.ordered_map(abs, [-value for value in values], chunksize=8)), values)
        seen = []
        with self.assertRaisesRegex(AssertionError, '^seven$'):
            for value in forked_checks.ordered_map(square, range(40), chunksize=2):
                seen.append(value)
        self.assertEqual(seen, [value * value for value in range(7)])

    def test_run_all_reports_the_first_failing_check_in_order(self):
        with self.assertRaisesRegex(AssertionError, '^second$'):
            forked_checks.run_all([lambda: None, lambda: fail('second'), lambda: None, lambda: fail('fourth')])
        forked_checks.run_all([lambda: None, lambda: None])

    def test_checks_see_the_state_of_the_caller(self):
        state = {'pages': 3}
        with self.assertRaisesRegex(AssertionError, '^3 pages$'):
            forked_checks.run_all([lambda: None, lambda: fail(f'{state["pages"]} pages')])

    def test_one_cpu_runs_everything_in_this_process(self):
        calls = []
        with mock.patch.object(forked_checks, 'workers', return_value=1):
            forked_checks.run_all([lambda: calls.append(1), lambda: calls.append(2)])
            self.assertEqual(list(forked_checks.ordered_map(abs, [-1, -2, -3], chunksize=1)), [1, 2, 3])
        self.assertEqual(calls, [1, 2])


if __name__ == '__main__':
    unittest.main()
