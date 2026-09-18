#!/usr/bin/env python3
"""THE PANEL READ IS A PINNED CHOICE, AND THE SELECTION DIAGNOSTIC IS A MEASUREMENT (AUT-PD-167).

⛔⛔ THIS FILE EXISTS BECAUSE A SCHEDULED CI FETCH REVERSED A COMMITTED SCIENTIFIC VERDICT WITH NO
COMMIT, NO GATE AND NO ARGUMENT. `emc-expression-datasets.yml` pushed a widened
`emc-expression-panels.json` (aa6d9d9a9); `ndrg1_panel_attribution.py` widened its entire reading the
moment that block appeared; and the artifact on the trunk then stopped re-deriving from its own
generator. Nobody chose that and nobody could see it until the next commit went red.

★ TWO PROPERTIES ARE PINNED HERE AND THEY ARE DIFFERENT KINDS OF THING.

  1. **THE READ IS A CONSTANT.** Which membership the panels are scored over is `MEMBERSHIP_SOURCE`
     in the module, not a consequence of which files a workflow happened to push. ⚠ The test that
     matters is not "the constant exists" — the historical narrow mode must still decline a wide
     block that is present and readable. The current full-membership/background pin was explicitly
     adopted after the accepted S53 comparison; data availability alone must not select a mode.
  2. **THE SELECTION DIAGNOSTIC ACTUALLY MEASURES SELECTION.** `within_panel_percentile` is what
     diagnoses selection in the historical curated subsets, so a version of it that returned a
     plausible number without looking at the data would be worse than none. It is mutated below
     against subsets built to be maximally and minimally selected, and it must move to both ends.

⚠ Every mutation runs on LOCAL COPIES of the inputs — never the module, never the committed
artifact (research-loop §3).
"""

from __future__ import annotations

import json
import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
sys.path.insert(0, MODALITIES)

import ndrg1_panel_attribution as N  # noqa: E402

BIG = "GSE24369_series_matrix.txt.gz"


@pytest.fixture(scope="module")
def src():
    with open(N.PANELS, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def committed():
    with open(N.OUT, encoding="utf-8") as fh:
        return json.load(fh)


def _wide_cache(src, matrix):
    gr = src["gene_reads"]
    cache = {g: N.sample_z(gr, g, matrix) for g in gr}
    cache = {g: v for g, v in cache.items() if v}
    for g, zs in N.signature_member_z(src, matrix).items():
        if not cache.get(g):
            cache[g] = zs
    return cache


# ----------------------------------------------------------------- 1. the read is a pinned choice
def test_the_pin_is_one_of_the_reads_the_module_implements():
    assert N.MEMBERSHIP_SOURCE in N.MEMBERSHIP_SOURCES


def test_the_wide_block_is_present_so_the_narrow_read_is_a_decline_not_an_absence(src):
    """⛔ IF THIS EVER FAILS, EVERY OTHER TEST HERE IS VACUOUS. A module that declines a block it
    could not read anyway has been proved nothing about."""
    blk = (src.get("signature_member_reads") or {}).get(BIG) or {}
    assert blk.get("z"), (
        "the panels artifact no longer carries `signature_member_reads`, so the pin below is not "
        "being exercised — this suite would pass on a module with the pin deleted")
    assert N.signature_member_z(src, BIG), "the raw reader cannot see a block that is in the file"


def test_the_narrow_pin_declines_the_wide_block_rather_than_failing_to_see_it(src, monkeypatch):
    """★ THE MUTATION FOR PROPERTY 1. `member_z` must return nothing under the narrow pin WHILE
    `signature_member_z` returns the same block it always did. If both came back empty the module
    would be narrow because the data is missing, which is a different and much weaker claim."""
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "curated_only")
    assert N.member_z(src, BIG) == {}
    assert len(N.signature_member_z(src, BIG)) > 0


def test_the_artifact_says_which_read_it_took_and_that_the_other_was_available(committed):
    """The artifact is what a reader holds, and a number under one read is not comparable with the
    same field name under the other. Both facts must be on its face."""
    ms = committed["panel_membership_source"]
    assert ms["pinned"] == N.MEMBERSHIP_SOURCE
    assert ms["wide_block_present"] is True
    assert ms.get("why_pinned"), "a pin with no recorded argument is a preference"


# --------------------------------------------------- 2. the diagnostic measures what it claims to
def test_full_membership_rows_do_not_invent_a_subset_percentile(committed):
    assert committed["panel_membership_source"]["pinned"] == "full_membership_background_null"
    for matrix, s in committed["series"].items():
        if not s.get("subject_readable"):
            continue
        for panel, row in s["panels"].items():
            if not row.get("scored"):
                continue
            assert row["within_panel_percentile"] is None, f"{matrix}/{panel}: full panel given a subset percentile"


def test_the_diagnostic_moves_to_both_ends_when_the_subset_is_built_to_be_selected(src):
    """⛔⛔ THE MUTATION FOR PROPERTY 2, AND IT IS RUN IN BOTH DIRECTIONS ON PURPOSE. A statistic that
    only ever comes back high would pass a one-sided version of this test while measuring nothing.

    Build two subsets of one real panel — the k members that individually track the subject BEST and
    the k that track it WORST — and require the diagnostic to place them at opposite ends. The real
    historical curated subsets sit between; current full membership correctly has no subset percentile."""
    cache = _wide_cache(src, BIG)
    subject_z = cache[N.SUBJECT]
    gsms = sorted(subject_z)
    pp = src["signature_scores"]["hypoxia_elvidge"]["per_platform"][BIG]
    full = [g for g in (pp.get("genes_readable") or []) if g != N.SUBJECT and cache.get(g)]
    assert len(full) > 40, "this panel is too thin on this platform for the mutation to mean anything"

    by_rho = sorted(full, key=lambda g: N.panel_rho([g], subject_z, gsms, cache)[0] or 0.0)
    k = 19
    worst, best = by_rho[:k], by_rho[-k:]
    lo = N.within_panel_percentile(worst, full, subject_z, gsms, cache, random.Random(N.SEED))
    hi = N.within_panel_percentile(best, full, subject_z, gsms, cache, random.Random(N.SEED))
    assert lo["percentile"] < 5.0, f"a deliberately worst subset scored {lo['percentile']}"
    assert hi["percentile"] > 95.0, f"a deliberately best subset scored {hi['percentile']}"


def test_a_subset_that_is_the_whole_panel_has_no_percentile_at_all(src):
    """An absent reading is not a reading of absence. When the scored members ARE the full readable
    membership there is no distribution to sit in, and the field must be None rather than 50."""
    cache = _wide_cache(src, BIG)
    subject_z = cache[N.SUBJECT]
    gsms = sorted(subject_z)
    pp = src["signature_scores"]["hypoxia_elvidge"]["per_platform"][BIG]
    full = [g for g in (pp.get("genes_readable") or []) if g != N.SUBJECT and cache.get(g)]
    assert N.within_panel_percentile(full, full, subject_z, gsms, cache,
                                     random.Random(N.SEED)) is None


# ------------------------------------------------------------------------- 3. the finding, pinned
def test_the_historical_curated_hypoxia_subsets_are_selected(src, monkeypatch):
    """⛔⛔ THE FINDING THAT COSTS THIS REPOSITORY ITS OWN RESULT, PINNED SO IT CANNOT BE LOST.

    The historical curated-only verdict said the larger series separates hypoxia from PPARγ. Every
    hypoxia panel's scored subset sits in the UPPER part of its own panel's within-panel
    distribution, while the PPARγ subsets straddle the middle — so the separation is at least partly
    a property of which members the curated roster happened to contain, and the size-matched null
    cannot see that because it draws from a pool rather than from the panel.

    A changed selection diagnostic requires an explanation; it would not by itself establish that
    the historical separation was mechanistically informative."""
    monkeypatch.setattr(N, "MEMBERSHIP_SOURCE", "curated_only")
    historical = N.build(n_draws=1)  # Selection diagnostic uses its separate original seeded draws.
    rows = [r for r in historical["series"][BIG]["panels"].values() if r.get("scored")]
    hyp = [r["within_panel_percentile"]["percentile"] for r in rows if r["family"] == "hypoxia"]
    ppg = [r["within_panel_percentile"]["percentile"] for r in rows if r["family"] == "pparg"]
    assert hyp and ppg
    assert min(hyp) > 50.0, (
        f"a hypoxia panel's curated subset is now mid-pack or below in its own panel {sorted(hyp)}. "
        "If that is real the verdict may be sounder than this row says — argue it.")
    assert sorted(hyp)[len(hyp) // 2] > sorted(ppg)[len(ppg) // 2], (
        f"hypoxia subsets {sorted(hyp)} are no longer selected relative to PPARγ ones {sorted(ppg)}")


def test_the_artifact_verdict_agrees_with_its_declared_joint_results(committed):
    """The source and joint results must agree; prose is reviewed separately, not by a keyword."""
    v = committed["verdict"]
    assert v["separating_series"] == sorted(m for m, s in committed["series"].items()
                                         if s.get("separates_hypoxia_from_pparg"))
    assert v.get("_weight"), "the verdict carries no statement of its own weight"
