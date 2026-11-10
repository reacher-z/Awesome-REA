"""Run one CI shard of the unit tests from the repository root:
CI_TEST_SHARD=0 CI_TEST_SHARDS=3 python3 tests/unit_shards.py

The shard comes from the environment, so the tests see no extra command-line arguments.

Discovery is the same as `python3 -m unittest discover -s tests`. Every test class stays whole in one
shard, and so does every module that defines setUpModule, so each class or module fixture runs once; the
classes that read the shared build of tests/shared_build.py form one group, so the site is built once.
These groups are dealt heaviest first to the lightest shard, and each shard runs its tests in discovery
order. Every shard computes the same plan and checks that the shards
are non-empty, pairwise disjoint and together equal the whole discovery before it runs its own part.
"""
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shared_build  # noqa: E402

# Approximate seconds per group on a GitHub-hosted runner, measured from the timestamped unit logs of a run of this
# change on top of #4402 (November 2026); the shared-build group is the sum of its classes. They only balance the
# shards: an unlisted group weighs FALLBACK_SECONDS per test, and the coverage checks below never depend on them.
# Re-measure from a run's timestamped unit logs when shards drift.
WEIGHTS = {
    'shared_build': 400,
    'test_public_source_supplements.PublicSourceSupplementTests': 375,
    'test_staged_site_build.StagedSiteBuildTests': 144,
    'test_discovery_leads.TrustedReviewTest': 36,
    'test_discovery_ingest.TrackerTest': 33,
    'test_review_pr.ReviewerDataSelectionTest': 31,
    'test_discoveries.TrustedReviewTest': 25,
    'test_readme_secondary_targets.ReadmeSecondaryTargetTest': 25,
    'test_catalog_revision.CatalogRevisionTests': 20,
    'test_requirement_budget.RequirementBudgetTests': 19,
    'test_evidence_pins.EvidencePinTests': 18,
    'test_discoveries.BatchValidationTest': 9,
    'test_review_supplements.PublicSupplementReviewerTests': 7,
    'test_review_pr.PrivateFileRulesTest': 6,
    'test_paper_files.PaperFileTest': 6,
    'test_privacy_guard.PrivacyGuardTests': 6,
    'test_discovery_leads.LayersAndExportTest': 5,
    'test_rest_readme_validation.RecoveryProvenanceTests': 5,
    'test_scheduled_source_scan.NestedSchemaTests': 4,
    'test_evidence_withdrawal.WithdrawnEvidenceTests': 4,
    'test_readme_case_methods.ReadmeCaseMethodTests': 4,
    'test_section_target_counts.SectionCountReconciliationTests': 4,
}
FALLBACK_SECONDS = 0.05


def cases(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from cases(test)
        else:
            yield test


SHARED_BUILD_GROUP = 'shared_build'


def group_key(test):
    module = type(test).__module__
    # Tests that read the per-process build of tests/shared_build.py run in one shard, which builds the site once.
    if getattr(sys.modules.get(module), 'built_site', None) is shared_build.built_site:
        return SHARED_BUILD_GROUP
    if hasattr(sys.modules.get(module), 'setUpModule'):
        return module
    return f'{module}.{type(test).__qualname__}'


def plan(discovered, count):
    """Return `count` sorted lists of indices into `discovered`, one list per shard."""
    groups = {}
    for index, test in enumerate(discovered):
        groups.setdefault(group_key(test), []).append(index)
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
    groups = len({group_key(test) for test in selected})
    print(f'Shard {shard + 1}/{count}: {len(selected)} of {len(discovered)} discovered tests in {groups} groups, '
          f'estimated {loads[shard]:.0f}s of {sum(loads):.0f}s', flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
