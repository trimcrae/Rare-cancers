"""Unit tests for the PocketMiner permutation null (review comment 8)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nr4a3_pocketminer_null as pn  # noqa: E402


def test_enriched_target_gives_small_p():
    # target residues 1,2,3 are the highest scorers → should be highly enriched
    scores = {i: (1.0 if i <= 3 else 0.1) for i in range(1, 31)}
    obs, null, p, pool = pn.permutation_pvalue(scores, [1, 2, 3], n_perm=2000, seed=1)
    assert obs == 1.0
    assert null < 0.3
    assert p < 0.01
    assert pool == 27  # 30 - 3 target


def test_non_enriched_target_gives_large_p():
    scores = {i: 0.5 for i in range(1, 31)}   # flat → target never beats null strictly
    obs, null, p, pool = pn.permutation_pvalue(scores, [1, 2, 3], n_perm=2000, seed=1)
    assert abs(obs - null) < 1e-9
    assert p > 0.5   # all null means equal obs → all count as >=


def test_deterministic_with_seed():
    scores = {i: (i % 7) / 7.0 for i in range(1, 51)}
    r1 = pn.permutation_pvalue(scores, [1, 8, 15], n_perm=1000, seed=42)
    r2 = pn.permutation_pvalue(scores, [1, 8, 15], n_perm=1000, seed=42)
    assert r1 == r2


def test_exclude_shrinks_pool():
    scores = {i: 0.5 for i in range(1, 31)}
    _, _, _, pool = pn.permutation_pvalue(scores, [1, 2], n_perm=100, seed=1, exclude=frozenset(range(20, 31)))
    assert pool == 30 - 2 - 11   # minus target(2) minus excluded(20..30 = 11)


def test_contiguous_null_runs():
    scores = {i: (1.0 if i <= 3 else 0.1) for i in range(1, 31)}
    obs, null, p, nw = pn.contiguous_pvalue(scores, [1, 2, 3])
    assert obs == 1.0 and nw > 0 and p < 0.2


def test_max_statistic_target_is_global_best_window():
    # residues 1-3 are the unique top window; the max-over-windows null can never beat it -> p is the floor 1/(n+1)
    scores = {i: (1.0 if i <= 3 else 0.1) for i in range(1, 31)}
    obs, p, nw = pn.max_statistic_pvalue(scores, [1, 2, 3], n_perm=2000, seed=1)
    assert obs == 1.0 and nw == 30 - 3 + 1
    # the null max can only TIE obs (when the three top values happen to land contiguous after a shuffle),
    # never exceed it, so p is small — near the add-one floor but not exactly it.
    assert p < 0.05


def test_max_statistic_more_conservative_than_contiguous():
    # a moderately-enriched target: the familywise max-statistic p must be >= the single-patch contiguous p
    scores = {i: (i % 5) / 5.0 for i in range(1, 61)}
    target = [5, 10, 15]                              # some mid-scoring residues
    _, _, p_contig, _ = pn.contiguous_pvalue(scores, target)
    _, p_max, _ = pn.max_statistic_pvalue(scores, target, n_perm=3000, seed=7)
    assert p_max >= p_contig - 1e-9                   # max-over-patches is never less significant


def test_max_statistic_deterministic():
    scores = {i: (i % 7) / 7.0 for i in range(1, 51)}
    assert pn.max_statistic_pvalue(scores, [1, 8, 15], n_perm=1000, seed=42) == \
           pn.max_statistic_pvalue(scores, [1, 8, 15], n_perm=1000, seed=42)
