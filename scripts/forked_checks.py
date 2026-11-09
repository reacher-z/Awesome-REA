"""Run independent site checks in forked worker processes, with the result of running them one by one.

Workers are forked when the work starts, so each sees the caller's state, including test patches. Where fork is
unavailable or there is one CPU, everything runs in the calling process.
"""
from __future__ import annotations

import concurrent.futures
import multiprocessing
import os

_TASKS: list = []
_FUNCTION = None


def workers() -> int:
    """The CPUs this process may run on."""
    if hasattr(os, 'sched_getaffinity'):
        return len(os.sched_getaffinity(0)) or 1
    return os.cpu_count() or 1


def _context():
    if workers() < 2 or 'fork' not in multiprocessing.get_all_start_methods():
        return None
    return multiprocessing.get_context('fork')


def _run(index: int) -> None:
    _TASKS[index]()


def run_all(checks) -> None:
    """Call every zero-argument check; on failure raise the exception of the first failing check in list order."""
    global _TASKS
    checks = list(checks)
    context = _context()
    if context is None or len(checks) < 2:
        for check in checks:
            check()
        return
    _TASKS = checks
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=min(workers(), len(checks)), mp_context=context)
    try:
        futures = [pool.submit(_run, index) for index in range(len(checks))]
        for future in futures:
            future.result()
    finally:
        pool.shutdown(cancel_futures=True)
        _TASKS = []


def _apply(item):
    try:
        return True, _FUNCTION(item)
    except Exception as error:  # Raised again in the caller at this item's place in the order.
        return False, error


def ordered_map(function, items, chunksize: int = 64):
    """Yield function(item) for each item in order. An exception is raised where its item comes in the order."""
    global _FUNCTION
    items = list(items)
    context = _context()
    if context is None or len(items) < 2 * chunksize:
        yield from map(function, items)
        return
    _FUNCTION = function
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=workers(), mp_context=context)
    try:
        for succeeded, value in pool.map(_apply, items, chunksize=chunksize):
            if not succeeded:
                raise value
            yield value
    finally:
        pool.shutdown(cancel_futures=True)
        _FUNCTION = None
