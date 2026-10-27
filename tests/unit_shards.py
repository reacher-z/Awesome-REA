"""Run one CI shard of the unit tests from the repository root:
CI_TEST_SHARD=0 CI_TEST_SHARDS=3 python3 tests/unit_shards.py

The shard comes from the environment, so the tests see no extra command-line arguments.

Discovery is the same as `python3 -m unittest discover -s tests`. Every test class stays whole in one
shard, so its setUpClass runs once. Classes are dealt heaviest first to the lightest shard, and each
shard runs its tests in discovery order. Every shard computes the same plan and checks that the shards
are non-empty, pairwise disjoint and together equal the whole discovery before it runs its own part.
"""
import os
import sys
import unittest

# Approximate seconds per class on a GitHub-hosted runner, from the unit logs of October 2026.
# They only balance the shards: an unlisted class weighs FALLBACK_SECONDS per test, and the coverage
# checks below never depend on them. Re-measure from a run's timestamped unit logs when shards drift.
WEIGHTS = {
    'test_public_source_supplements.PublicSourceSupplementTests': 140,
    'test_link_fragments.LinkFragmentTest': 49,
    'test_review_supplements.PublicSupplementReviewerTests': 42,
    'test_catalog_revision.CatalogRevisionTests': 26,
    'test_requirement_budget.RequirementBudgetTests': 26,
    'test_evidence_pins.EvidencePinTests': 25,
    'test_review_pr.ReviewerDataSelectionTest': 18,
    'test_readme_size.ReadmeSizeBudgetTest': 12,
    'test_readme_totals.ReadmeTotalsTest': 8,
    'test_repository_index.RepositoryIndexTests': 7,
    'test_repository_index.RelatedMarkerTests': 7,
}
FALLBACK_SECONDS = 0.1


def cases(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from cases(test)
        else:
            yield test


def class_key(test):
    return f'{type(test).__module__}.{type(test).__qualname__}'


def plan(discovered, count):
    """Return `count` sorted lists of indices into `discovered`, one list per shard."""
    groups = {}
    for index, test in enumerate(discovered):
        groups.setdefault(class_key(test), []).append(index)
    weight = {key: WEIGHTS.get(key, FALLBACK_SECONDS * len(indices)) for key, indices in groups.items()}
    shards, loads = [[] for _ in range(count)], [0.0] * count
    for key in sorted(groups, key=lambda key: (-weight[key], key)):
        lightest = min(range(count), key=lambda shard: (loads[shard], shard))
        shards[lightest].extend(groups[key])
        loads[lightest] += weight[key]
    return [sorted(indices) for indices in shards], loads, set(WEIGHTS) - set(groups)


def require(condition, message):
    if not condition:
        sys.exit(f'tests/unit_shards.py: {message}')


def main():
    shard, count = int(os.environ['CI_TEST_SHARD']), int(os.environ['CI_TEST_SHARDS'])
    require(0 <= shard < count, f'shard {shard} is outside 0..{count - 1}')
    discovered = list(cases(unittest.defaultTestLoader.discover('tests')))
    require(discovered, 'no tests were discovered')
    shards, loads, stale = plan(discovered, count)
    members = [set(indices) for indices in shards]
    require(all(members), 'every shard must have at least one test')
    require(set().union(*members) == set(range(len(discovered))), 'the shards must cover every discovered test')
    require(all(members[a].isdisjoint(members[b]) for a in range(count) for b in range(a + 1, count)),
            'no test may run in two shards')
    require(sum(map(len, shards)) == len(discovered), 'every discovered test must run exactly once')
    for key in sorted(stale):
        print(f'::warning::tests/unit_shards.py weighs {key}, which discovery no longer finds.', flush=True)
    selected = [discovered[index] for index in shards[shard]]
    classes = len({class_key(test) for test in selected})
    print(f'Shard {shard + 1}/{count}: {len(selected)} of {len(discovered)} discovered tests in {classes} classes, '
          f'estimated {loads[shard]:.0f}s of {sum(loads):.0f}s', flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
