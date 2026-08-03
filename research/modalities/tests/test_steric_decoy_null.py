"""Unit tests for `C25`'s pure helpers — the parts a decoy background's readability rests on.

⛔ WHY THESE AND NOT OTHERS. Three of the four functions below encode a RULE that was agreed before the
measurement existed, and a silent change to any of them would move a verdict without moving a number that
anyone reads: the verdict thresholds, the tie convention in the percentile, and the modal-value check that
`C24` proved is the difference between a percentile that means something and one that does not.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import steric_decoy_null as SDN  # noqa: E402


# ── the verdict rule ─────────────────────────────────────────────────────────────────────────────────────
def test_grade_needs_enough_graded_rows():
    assert SDN.grade(4, 1.0, 0.0).startswith("UNGRADEABLE")
    assert SDN.grade(0, 1.0, 0.0).startswith("UNGRADEABLE")
    assert SDN.grade(None, 1.0, 0.0).startswith("UNGRADEABLE")


def test_grade_needs_a_high_percentile():
    assert SDN.grade(20, 0.80, 0.0) == "DISTINCTIVE"
    assert SDN.grade(20, 0.75, 0.0) == "DISTINCTIVE"          # the boundary is inclusive, as registered
    assert SDN.grade(20, 0.74, 0.0) == "NOT DISTINGUISHED"


def test_grade_refuses_a_background_whose_modal_outcome_is_the_targets_own():
    """⛔ THE `C24` FAILURE MODE. A 100th-percentile result in a background where most rows return the same
    value the target returns is not evidence, and the rule must refuse it however good the percentile is."""
    assert SDN.grade(20, 1.0, 0.51) == "NOT DISTINGUISHED"
    assert SDN.grade(20, 1.0, 0.50) == "DISTINCTIVE"


def test_grade_without_an_index_value_is_ungradeable_not_negative():
    assert SDN.grade(20, None, 0.0).startswith("UNGRADEABLE")


# ── the percentile tie convention ────────────────────────────────────────────────────────────────────────
def test_percentile_above_does_not_count_ties_as_beaten():
    """A background arm that EQUALS the index is an arm that reproduced it. Counting it as beaten is the
    over-reading this whole exercise exists to prevent."""
    assert SDN.percentile_above(0.75, [0.1, 0.2, 0.75, 0.9]) == 0.5
    assert SDN.percentile_above(0.75, [0.75, 0.75]) == 0.0
    assert SDN.percentile_above(1.0, [0.1, 0.2]) == 1.0


def test_percentile_above_ignores_none_and_empty():
    assert SDN.percentile_above(0.5, []) is None
    assert SDN.percentile_above(0.5, [None, 0.1]) == 1.0


# ── the modal-value check ────────────────────────────────────────────────────────────────────────────────
def test_mode_of_finds_the_modal_value_and_its_frequency():
    m = SDN.mode_of([0.0, 0.0, 0.0, 0.4, 0.9])
    assert m["value"] == 0.0 and m["count"] == 3 and m["n"] == 5
    assert abs(m["frac"] - 0.6) < 1e-9


def test_mode_of_rounds_before_counting():
    m = SDN.mode_of([0.1234, 0.1235, 0.9])
    assert m["count"] == 2 and m["value"] == 0.123


def test_mode_of_empty_is_none():
    assert SDN.mode_of([]) is None
    assert SDN.mode_of([None, None]) is None


# ── the two sequence-index bridges ───────────────────────────────────────────────────────────────────────
def test_the_two_bridges_are_different_and_both_are_needed():
    """⛔ Mixing them mis-keys every class lookup and raises nothing — measured 2026-08-03, it turned M3's
    0.923 / 0.000 / 0.173 into 0.769 / 0.115 / 0.446."""
    model = {"ids": [34, 35, 36, 40], "seq": "ACDE"}
    assert SDN.seq_index_of_rid(model, 36) == 3
    assert SDN.seq_index_of_rid(model, 99) is None
    assert SDN.uniprot_index_of_rid(model, 36) == 36 + 372
    assert SDN.uniprot_index_of_rid(model, None) is None
    assert SDN.seq_index_of_rid(model, 36) != SDN.uniprot_index_of_rid(model, 36)


# ── the answer-blind trio selection ──────────────────────────────────────────────────────────────────────
def _ident(pairs):
    return {k: {"identity": v, "coverage": 0.9} for k, v in pairs.items()}


def test_select_trios_is_answer_blind_deterministic_and_respects_the_band():
    ident = _ident({("A", "B"): 0.60, ("A", "C"): 0.62, ("B", "C"): 0.61,
                    ("A", "D"): 0.20, ("B", "D"): 0.21, ("C", "D"): 0.22})
    sel, n_cand = SDN.select_trios(["A", "B", "C", "D"], ident, 0.61, (0.35, 0.90), 0.6, 10, 2)
    assert n_cand == 1                                   # only ABC has all three pairs inside the band
    assert sel[0]["members"] == ["A", "B", "C"]
    assert abs(sel[0]["mean_identity"] - 0.61) < 1e-9
    # deterministic: same inputs, same output
    assert SDN.select_trios(["A", "B", "C", "D"], ident, 0.61, (0.35, 0.90), 0.6, 10, 2)[0] == sel


def test_select_trios_respects_max_per_protein_and_max_trios():
    accs = ["A", "B", "C", "D", "E", "F"]
    ident = _ident({(a, b): 0.60 for i, a in enumerate(accs) for b in accs[i + 1:]})
    sel, _ = SDN.select_trios(accs, ident, 0.60, (0.35, 0.90), 0.6, 10, 1)
    used = [m for t in sel for m in t["members"]]
    assert len(used) == len(set(used))                   # max_per_protein = 1 admits no repeats
    sel2, _ = SDN.select_trios(accs, ident, 0.60, (0.35, 0.90), 0.6, 1, 2)
    assert len(sel2) == 1


def test_select_trios_rejects_low_coverage():
    ident = {("A", "B"): {"identity": 0.6, "coverage": 0.9},
             ("A", "C"): {"identity": 0.6, "coverage": 0.1},
             ("B", "C"): {"identity": 0.6, "coverage": 0.9}}
    sel, n_cand = SDN.select_trios(["A", "B", "C"], ident, 0.6, (0.35, 0.90), 0.6, 10, 2)
    assert n_cand == 0 and sel == []


# ── the pre-registration itself ──────────────────────────────────────────────────────────────────────────
def test_the_gradeability_floor_is_inherited_from_C24_not_re_chosen():
    """The floor must be `C24`'s own number. If someone re-types it, this fails — which is the point."""
    import categorical_decoy_null as CDN
    inherited = CDN.PREREG["gradeability"]["min_conditioning_events"]
    assert SDN.PREREG["gradeability"]["min_conditioning_events"] == inherited == 20


def test_the_selection_band_is_inherited_not_re_chosen():
    import categorical_decoy_null as CDN
    assert (SDN.PREREG["selection_rule"]["max_pairs"]
            != CDN.PREREG["pair_formation"]["max_pairs"])          # budget IS per-scope, as registered
    assert CDN.PREREG["pair_formation"]["identity_band"] == [0.35, 0.9]


def test_plan_mode_emits_no_statistic(tmp_path, monkeypatch):
    """The pre-registration must be a function of constants alone — no model, no alignment, no result."""
    monkeypatch.setattr(SDN, "PLAN_JSON", str(tmp_path / "plan.json"))
    plan = SDN.mode_plan(None)
    assert "preregistration" in plan
    for banned in ("selected_pairs", "selected_trios", "decoy_rows", "backgrounds", "verdict"):
        assert banned not in plan, f"{banned} must not exist at plan time"


# ── refusing to rank against a default ───────────────────────────────────────────────────────────────────
def test_reference_identity_must_be_measured_not_defaulted():
    """⛔ MEASURED 2026-08-03, run 30840744749: NR4A3 is not a row in the committed 47-receptor ranking, so
    it was never trimmed, the reference identity fell back to a hard-coded 0.6, and the plan published a
    `nr4a3_reference_identities` of `{}` beside a ranking that looked pre-registered. A populated field that
    was never measured is CLAUDE.md §4's sharpest failure; the fallback is now a refusal."""
    import pytest
    with pytest.raises(SystemExit):
        SDN.require_measured_reference_identity({}, [])
    with pytest.raises(SystemExit):
        SDN.require_measured_reference_identity({"NR4A1": {"identity": 0.65}}, ["a", "b"])
    # the only accepted shape: both reference identities, all three family members trimmed
    SDN.require_measured_reference_identity({"NR4A1": {"identity": 0.65}, "NR4A2": {"identity": 0.66}},
                                            ["a", "b", "c"])


# ── the roadmap anchors ──────────────────────────────────────────────────────────────────────────────────
def test_last_register_row_anchor_picks_the_highest_numbered_row():
    text = "| **C9** | x |\n| **C23** | y |\n| **C24** | z |\n| **C7** | w |\n"
    assert SDN.last_register_row_anchor(text) == "| **C24** |"
    assert SDN.last_register_row_anchor("no rows here") is None


def test_register_count_is_counted_from_the_document_not_typed():
    text = "**24 items.** Status: ok\n| **C1** | a |\n| **C24** | b |\n"
    rows, anchor = SDN.register_count(text)
    assert rows == 2 and anchor == "**24 items.**"
    assert SDN.register_count("nothing") == (0, None)
