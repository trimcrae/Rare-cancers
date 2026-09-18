#!/usr/bin/env python3
"""Preserve NDRG1 subject-exclusion and size-matched background controls (AUT-PROP-048).

Current result checks bind the accepted S53 full-membership/background reading. Neither series
meets the original joint separation criterion, but the smaller series retains five of six hypoxia
panels above their own nulls. This does not identify a mechanism or establish absence of signal.

The self-inclusion mutation retains its original curated membership on both sides of the paired
comparison. It tests contamination by the subject without confounding that change with membership.
Other checks use the current scoring cache, panel-specific nulls and unchanged joint criterion.
Mutations operate on local copies or pytest-restored attributes, never the committed artifact.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
sys.path.insert(0, MODALITIES)

import ndrg1_panel_attribution as N  # noqa: E402

BIG = "GSE24369_series_matrix.txt.gz"      # 35 samples, mixed histologies
SMALL = "GSE4303-GPL3290_series_matrix.txt.gz"  # 16 samples, mixed histologies


@pytest.fixture(scope="module")
def committed():
    with open(N.OUT, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def src():
    with open(N.PANELS, encoding="utf-8") as fh:
        return json.load(fh)


def _cache(src, matrix):
    return N.scoring_cache(src["gene_reads"], src, matrix)


# ------------------------------------------------------------------ the artifact is what it says
def test_the_committed_artifact_rederives_from_its_generator():
    """⛔ The seeded null makes this checkable at all. An unseeded one would fail here for a reason
    that is not a defect, which is why SEED is part of the module rather than a run-time choice."""
    assert N.main(["--check"]) == 0, (
        "ndrg1-panel-attribution.json does not re-derive. Regenerate it and commit the result.")


def test_the_background_read_preserves_the_measured_discordant_patterns(committed):
    """S53/AUT-PD-185 supplied the measurement authorizing the AUT-PD-170 migration.

    Preserve both the lost separation and the smaller series' remaining pattern. A failed joint
    criterion is not evidence that every panel association disappeared.
    """
    assert committed["panel_membership_source"]["pinned"] == "full_membership_background_null"
    assert committed["series"][BIG]["separates_hypoxia_from_pparg"] is False
    assert committed["series"][SMALL]["separates_hypoxia_from_pparg"] is False
    assert committed["verdict"]["separating_series"] == []
    assert (committed["series"][BIG]["n_hypoxia_above_null_p95"],
            committed["series"][BIG]["n_pparg_above_null_p95"]) == (2, 3)
    assert (committed["series"][SMALL]["n_hypoxia_above_null_p95"],
            committed["series"][SMALL]["n_pparg_above_null_p95"]) == (5, 0)


# ------------------------------------------------------------------ control 1: leave-one-out
def test_including_the_subject_in_its_own_panels_manufactures_the_correlation(src):
    """⛔⛔ THE MUTATION. Put NDRG1 back into the hypoxia panels it belongs to and the correlation
    jumps, because the panel mean now contains the variable it is being correlated against.

    ★ THE ASSERTION IS THE GAP, NOT THE MUTANT'S VALUE. A mutant that merely differed could differ
    by noise; a mutant that rises materially on every panel containing the subject is the signature
    of self-correlation.
    """
    # Preserve the original controlled demonstration on its historical membership. Comparing a
    # curated mutant to today's full-panel score would confound self-inclusion with membership.
    cache = {g: N.sample_z(src["gene_reads"], g, BIG) for g in src["gene_reads"]}
    subject = cache[N.SUBJECT]
    gsms = sorted(subject)
    sig = src["signature_scores"]

    inflated = []
    for panel in sig:
        if N.family_of(panel) != "hypoxia" or BIG not in sig[panel].get("per_platform", {}):
            continue
        readable = (sig[panel]["per_platform"][BIG].get("genes_readable") or [])
        if N.SUBJECT not in readable:
            continue                      # this set does not contain the subject; nothing to mutate
        members = [g for g in readable if cache.get(g)]        # ⛔ subject NOT removed — the mutation
        honest, _ = N.panel_rho([g for g in members if g != N.SUBJECT], subject, gsms, cache)
        mutant, _n = N.panel_rho(members, subject, gsms, cache)
        inflated.append((panel, honest, mutant))

    assert inflated, (
        "no scored hypoxia panel on this platform contains NDRG1, so this mutation exercised "
        "nothing and the leave-one-out has not been shown to matter here")
    for panel, honest, mutant in inflated:
        assert mutant > honest, (
            f"{panel}: including the subject did not raise rho ({mutant:+.3f} vs {honest:+.3f}). "
            "Either the exclusion is not doing what this module claims, or panel_rho is not "
            "reading the members it is given.")


def test_every_current_panel_score_and_count_exclude_the_subject(src, committed):
    """Bind current stored scores, not just reported counts, to explicit subject exclusion."""
    sig = src["signature_scores"]
    for matrix, s in committed["series"].items():
        if not s.get("subject_readable"):
            continue
        cache = _cache(src, matrix)
        for panel, row in s["panels"].items():
            if not row.get("scored"):
                continue
            readable = [g for g in (sig[panel]["per_platform"][matrix].get("genes_readable") or [])
                        if g != N.SUBJECT]
            assert row["n_panel_readable"] == len(readable)
            assert row["n_panel_members"] == len([g for g in readable if cache.get(g)])
            assert row["n_panel_members"] <= row["n_panel_readable"]
            members = [g for g in readable if cache.get(g)]
            rho, n_scored = N.panel_rho(members, cache[N.SUBJECT],
                                       sorted(cache[N.SUBJECT]), cache)
            assert rho is not None
            assert row["rho"] == round(rho, 4), f"{matrix}/{panel}: stored score includes the subject or different members"
            assert row["n_samples_scored"] == n_scored


# ------------------------------------------------------------------ control 2: the size-matched null
def test_the_smaller_series_background_null_is_materially_positive(committed):
    """A substantial random-panel correlation does not itself identify its biological cause."""
    small = committed["series"][SMALL]
    lo, hi = small["null_median_range"]
    assert lo > 0.15, (
        f"the small series' random-panel null median has fallen to {lo:+.3f}. If that is real the "
        "background comparison has changed and needs source-bound review.")
    big_lo, big_hi = committed["series"][BIG]["null_median_range"]
    assert abs(big_hi) < 0.1 and abs(big_lo) < 0.1, (
        f"the LARGER series' null is no longer centred near zero ({big_lo:+.3f}..{big_hi:+.3f}), so "
        "the background comparison has changed and needs source-bound review")


def test_raw_rho_cannot_replace_each_panels_size_matched_null(committed):
    """An above-null panel has a lower raw rho than a failing panel. Thus one global raw-rho
    threshold cannot reproduce these panel-level decisions. This does not make the stronger,
    unsupported claim that a raw threshold cannot happen to reproduce two series-level booleans.
    """
    rows = [r for s in committed["series"].values() if s.get("subject_readable")
            for r in s["panels"].values() if r.get("scored")]
    above = [r["rho"] for r in rows if r["above_null_p95"]]
    below = [r["rho"] for r in rows if not r["above_null_p95"]]
    assert above and below
    assert min(above) < max(below)


def test_a_panel_that_clears_on_the_pparg_side_makes_the_verdict_false(src):
    """★ THE VERDICT IS A JOINT STATEMENT AND MUST FAIL CLOSED. One PPARγ panel clearing its null
    makes 'separates' false however strong the hypoxia side is — otherwise a result where BOTH
    programmes track the subject would be reported as a hypoxia finding."""
    doc = N.build(n_draws=200)
    for matrix, s in doc["series"].items():
        if not s.get("subject_readable"):
            continue
        if s["n_pparg_above_null_p95"] > 0:
            assert s["separates_hypoxia_from_pparg"] is False, (
                f"{matrix}: a PPARγ panel cleared its null and the verdict still says the "
                "programmes separate")
