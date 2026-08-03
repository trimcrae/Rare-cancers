"""Invariants for the two SCOPE rungs (`R13`/`R14`) and the steric-exclusion DESIGN RULE.

These pin the three things that would silently go wrong if someone edited either module:

  1. THE DESIGN RULE AND THE MEASUREMENT MUST STAY THE SAME OBJECT. `steric_design_rule.score_pose` is
     supposed to be M3's predicate applied one molecule at a time. If it drifts, the "design rule" starts
     recommending substituents on a statistic nobody measured — and nothing would say so.
  2. A SIGNAL MAY NEVER BE EMITTED WITHOUT ITS NULL. NR4A3's absence of clash is guaranteed by construction,
     so a bare signal rate is not gradeable. This is the one property the whole mechanism's honesty rests on.
  3. THE SCOPE RUNGS MUST STAY OUT OF THE PINNED LADDER TOTAL. They are claim-ceiling conditions, not spine
     steps. Folding them in would move a total `vast_cost_model.py` derives and `lint_consistency` checks,
     and the failure would be a wrong number rather than an error.

Fast by construction: the committed artifacts are READ, never regenerated (the lobe grid takes seconds).
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.abspath(os.path.join(HERE, ".."))
if MOD not in sys.path:
    sys.path.insert(0, MOD)

import scope_rung_cost as SRC  # noqa: E402
import steric_design_rule as SDR  # noqa: E402


def _art(name):
    path = os.path.join(MOD, name)
    if not os.path.exists(path):
        pytest.skip("%s not committed" % name)
    with open(path) as fh:
        return json.load(fh)


# ── 1 · the design rule is the same object as the measurement ────────────────────────────────────────────
def test_scorer_reproduces_the_measurement_it_operationalises():
    art = _art("steric-design-rule.json")
    w = art["worked_example"]
    assert w["reproduces_M3"] is True, (
        "the per-candidate scorer no longer reproduces M3's own rates over M3's own poses, so the design "
        "rule and the measurement have become different objects — regenerate and investigate before use")
    assert w["pooled_signal_rate"] > w["pooled_null_rate"]


def test_score_pose_never_emits_a_signal_without_its_null():
    """A pose that fires everywhere still gets a null back. The refusal is structural, not conditional."""
    geometry = {
        1: {"class": "unique_and_both_bulkier", "NR4A3_sidechain": [(50.0, 0.0, 0.0)],
            "paralogue_sidechain": {"NR4A1": [(0.0, 0.0, 0.0)], "NR4A2": [(0.0, 0.0, 0.5)]}},
        2: {"class": "conserved_or_shared", "NR4A3_sidechain": [(50.0, 0.0, 0.0)],
            "paralogue_sidechain": {"NR4A1": [(0.0, 0.0, 0.0)], "NR4A2": [(0.0, 0.0, 0.5)]}},
    }
    out = SDR.score_pose([(0.0, 0.0, 0.0)], geometry, 3.0)
    assert out["signal_rate"] == 1.0 and out["null_rate"] == 1.0
    assert out["signal_minus_null"] == 0.0, "a molecule that fires everywhere must score ZERO net signal"
    assert "by_position_class" in out and set(out["by_position_class"]) == {
        "unique_and_both_bulkier", "conserved_or_shared"}


def test_a_pose_that_also_clashes_with_nr4a3_does_not_count():
    """The predicate is paralogue-ONLY. A ligand atom NR4A3 also denies is not an exclusion, it is a clash."""
    geometry = {1: {"class": "unique_and_both_bulkier", "NR4A3_sidechain": [(0.0, 0.0, 1.0)],
                    "paralogue_sidechain": {"NR4A1": [(0.0, 0.0, 0.0)], "NR4A2": [(0.0, 0.0, 0.5)]}}}
    assert SDR.score_pose([(0.0, 0.0, 0.0)], geometry, 3.0)["signal_rate"] == 0.0


def test_the_design_target_bar_is_measured_not_the_hardcoded_floor():
    """The bar must be the null class's own largest lobe. If someone re-tunes the absolute floor upward and
    it starts binding, the rule has quietly acquired a chosen threshold — which is the one number a reader
    could not grade."""
    art = _art("steric-design-rule.json")
    assert art["null_volume_ceiling_A3"] > SDR.MIN_LOBE_VOLUME_A3, (
        "the absolute sanity floor now exceeds the measured null ceiling, so the design-target bar is a "
        "CHOSEN number again")
    for u in art["design_targets"]:
        lobe = art["denied_lobes"][str(u)]
        assert lobe["class"] == "unique_and_both_bulkier"
        assert lobe["volume_A3"] > art["null_volume_ceiling_A3"]


def test_the_control_travels_with_every_emitted_rule():
    """M4's relocation control caps what the rule may claim. It must be present and non-empty, because a
    score reported without it reads as 'the paralogue cannot bind this' — which is not what was measured."""
    art = _art("steric-design-rule.json")
    ctl = art["⛔_control"]
    assert ctl["median_centroid_shift_A"], "the M4 relocation control is missing from the design rule"
    assert set(ctl["median_centroid_shift_A"]) == {"NR4A1", "NR4A2"}
    assert all(v > 1.0 for v in ctl["median_centroid_shift_A"].values())
    assert "NOT that the paralogue fails to bind" in ctl["⛔_what_this_score_is_not"]


# ── 2 · the scope rungs are priced from evidence and stay out of the pinned total ─────────────────────────
def test_scope_rungs_are_not_in_the_pinned_ladder():
    """The regression this exists to catch is somebody 'tidying' these into the ladder artifact, which would
    move the pinned total silently rather than fail loudly."""
    ladder = _art("vast-ladder-repricing.json")["ladder"]
    for name in ladder:
        assert "R13" not in name and "R14" not in name, (
            "a scope rung has been folded into the derived ladder: %s" % name)


def test_scope_rung_totals_are_derived_from_their_own_rows():
    art = _art("scope-rung-cost.json")
    rows = art["rungs"].values()
    assert abs(sum(r.get("plan_usd", 0.0) for r in rows)
               - art["totals_for_these_four_rungs_only"]["plan_usd"]) < 1e-6


def test_scope_rung_market_rate_is_read_from_the_ladder_not_typed():
    art, ladder = _art("scope-rung-cost.json"), _art("vast-ladder-repricing.json")
    assert art["market"]["plan_usd_per_reference_gpu_h"] == ladder["plan_usd_per_reference_gpu_h"]
    assert art["market"]["range_usd_per_reference_gpu_h"] == ladder["range_usd_per_reference_gpu_h"]


def test_cofold_basis_is_measured_on_the_reference_card():
    """The co-fold price needs no card ratio ONLY because every counted rental was on the reference card.
    If a non-reference card ever enters that ledger slice, the basis silently acquires a missing conversion."""
    b = _art("scope-rung-cost.json")["bases"]["cofold_per_model"]
    assert b["all_on_reference_card"] is True, (
        "the co-fold basis now mixes cards (%s) — it needs an explicit ratio, not a straight sum" % b["cards"])
    assert b["n_rentals"] > 0 and b["ref_gpu_h_per_model"] > 0


def test_the_metadynamics_rung_declares_its_refusal_rather_than_hiding_it():
    """A rung whose $/ns exceeds the buy line must SAY so. The failure mode this guards is a rung that
    prints a price, reads as buyable, and would be refused at launch."""
    r = [v for k, v in _art("scope-rung-cost.json")["rungs"].items() if k.startswith("R14-b")][0]
    assert r["usd_per_ns"] is not None and r["multiple_of_buy_line"] is not None
    over = r["usd_per_ns"] >= _art("scope-rung-cost.json")["market"]["approved_buy_line_usd_per_ns"]
    assert r["⛔_WOULD_BE_REFUSED_BY_THE_STANDING_RATE_LINE"] is over


def test_the_cofold_rung_refuses_a_usd_per_ns_instead_of_inventing_one():
    """Inference produces no nanoseconds. An invented $/ns in that column is exactly the fabricated figure
    CLAUDE.md §1 exists to prevent — the cell must be an explained refusal."""
    r = [v for k, v in _art("scope-rung-cost.json")["rungs"].items() if k.startswith("R13-b")][0]
    assert r["usd_per_ns"] is None
    assert "no denominator" in r["_why_no_usd_per_ns"]


def test_both_requirements_keep_an_explicitly_unpriceable_tier():
    """Pricing part of a requirement must never read as pricing all of it."""
    un = _art("scope-rung-cost.json")["unpriceable"]
    assert any(k.startswith("R13") for k in un) and any(k.startswith("R14") for k in un)
    assert all("NOT PRICED" in v for v in un.values())


def test_free_tiers_are_free_and_need_no_nod():
    rungs = _art("scope-rung-cost.json")["rungs"]
    for key in [k for k in rungs if k.startswith(("R13-a", "R14-a"))]:
        assert rungs[key]["plan_usd"] == 0.0
        assert rungs[key]["needs_authorization"] is False


def test_pure_price_helpers():
    p = SRC.price(10.0, 0.1, [0.05, 0.3])
    assert p == {"ref_gpu_h": 10.0, "plan_usd": 1.0, "range_usd": [0.5, 3.0]}
