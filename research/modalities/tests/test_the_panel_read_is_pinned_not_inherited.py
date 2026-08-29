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
     matters is not "the constant exists" — it is that the wide block IS PRESENT AND READABLE and
     the narrow read is taken anyway. A decline and an absence are different facts (CLAUDE.md §4),
     and only the decline is a choice somebody has to defend.
  2. **THE SELECTION DIAGNOSTIC ACTUALLY MEASURES SELECTION.** `within_panel_percentile` is what
     tells a reader how much the committed verdict is worth, so a version of it that returned a
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


def test_the_pin_declines_the_wide_block_rather_than_failing_to_see_it(src):
    """★ THE MUTATION FOR PROPERTY 1. `member_z` must return nothing under the narrow pin WHILE
    `signature_member_z` returns the same block it always did. If both came back empty the module
    would be narrow because the data is missing, which is a different and much weaker claim."""
    if N.MEMBERSHIP_SOURCE != "curated_only":
        pytest.skip("the pin is not narrow; property 1 is asserted by the constant itself")
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
def test_every_scored_row_carries_the_selection_diagnostic(committed):
    for matrix, s in committed["series"].items():
        if not s.get("subject_readable"):
            continue
        for panel, row in s["panels"].items():
            if not row.get("scored"):
                continue
            w = row.get("within_panel_percentile")
            assert w is not None, f"{matrix}/{panel} is scored with no selection diagnostic"
            assert 0.0 <= w["percentile"] <= 100.0
            assert w["n_panel_full"] > row["n_panel_members"]


def test_the_diagnostic_moves_to_both_ends_when_the_subset_is_built_to_be_selected(src):
    """⛔⛔ THE MUTATION FOR PROPERTY 2, AND IT IS RUN IN BOTH DIRECTIONS ON PURPOSE. A statistic that
    only ever comes back high would pass a one-sided version of this test while measuring nothing.

    Build two subsets of one real panel — the k members that individually track the subject BEST and
    the k that track it WORST — and require the diagnostic to place them at opposite ends. The real
    committed subsets sit between, which is the only reason their percentiles carry information."""
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
def test_the_larger_series_hypoxia_subsets_are_selected_rather_than_thin_but_fair(committed):
    """⛔⛔ THE FINDING THAT COSTS THIS REPOSITORY ITS OWN RESULT, PINNED SO IT CANNOT BE LOST.

    The committed verdict says the larger series separates hypoxia from PPARγ. In that series every
    hypoxia panel's scored subset sits in the UPPER part of its own panel's within-panel
    distribution, while the PPARγ subsets straddle the middle — so the separation is at least partly
    a property of which members the curated roster happened to contain, and the size-matched null
    cannot see that because it draws from a pool rather than from the panel.

    ★ IF THIS EVER GOES GREEN-BY-FAILING — the hypoxia subsets stop being selected — that is the
    verdict becoming trustworthy, and it must be argued in a commit message rather than discovered
    in a manuscript. It is the same instruction the null's own guard carries."""
    rows = [r for r in committed["series"][BIG]["panels"].values() if r.get("scored")]
    hyp = [r["within_panel_percentile"]["percentile"] for r in rows if r["family"] == "hypoxia"]
    ppg = [r["within_panel_percentile"]["percentile"] for r in rows if r["family"] == "pparg"]
    assert hyp and ppg
    assert min(hyp) > 50.0, (
        f"a hypoxia panel's curated subset is now mid-pack or below in its own panel {sorted(hyp)}. "
        "If that is real the verdict may be sounder than this row says — argue it.")
    assert sorted(hyp)[len(hyp) // 2] > sorted(ppg)[len(ppg) // 2], (
        f"hypoxia subsets {sorted(hyp)} are no longer selected relative to PPARγ ones {sorted(ppg)}")


def test_the_artifact_refuses_to_state_the_verdict_without_the_confound(committed):
    """One fact, one place — and the place a reader lands is the verdict. A headline that reads as a
    finished result while the row above says it is conditional is the overclaim this whole cycle is
    about."""
    v = committed["verdict"]
    assert "CONDITIONAL" in v["headline"], "the headline reads as a settled result"
    assert v.get("_weight"), "the verdict carries no statement of its own weight"
    assert "within_panel_percentile" in committed["_what_this_does_not_settle"]
