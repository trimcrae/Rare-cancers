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
