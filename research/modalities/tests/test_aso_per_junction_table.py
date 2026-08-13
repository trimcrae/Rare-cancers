#!/usr/bin/env python3
"""One reagent per junction, and the two ways building it went wrong.

⛔ WHY THIS EXISTS (2026-08-13, trimcrae: *"Why do we only have one candidate instead of one per
fusion type? Are we claiming it's impossible to make an ASO for any other fusion?"*). The paper's
candidate set was selected globally, which answers "what is the cleanest reagent in the panel"
rather than "what should be ordered for the fusion this patient has". Both defects asserted below
were introduced while fixing that, and both produced a table that looked complete and was wrong.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, "aso-per-junction-table.json")
sys.path.insert(0, MOD)


def _art():
    if not os.path.exists(ART):
        pytest.skip("the per-junction table is not present in this checkout")
    return json.load(open(ART, encoding="utf-8"))


def _junction(label):
    return next(j for j in _art()["junctions"] if j["junction_label"] == label)


def test_every_frame_compatible_junction_is_present():
    """⛔ THE MULTI-PARTNER COLLISION. Nine designs span more than one seam exactly, so one
    sequence belongs to three junctions at once. Keying the deep screens by design silently kept
    the last screen read and dropped EWSR1 e12 and FUS e10 — 36 junctions where the panel has 38,
    with the most commonly reported patient junction among the missing."""
    a = _art()
    assert a["n_junctions"] == 38, a["n_junctions"]
    labels = {j["junction_label"] for j in a["junctions"]}
    for required in ("EWSR1_e12__NR4A3_e3", "FUS_e10__NR4A3_e3", "TAF15_e11__NR4A3_e3",
                     "TAF15_e6__NR4A3_e3"):
        assert required in labels, f"{required} fell out of the table"


def test_the_multi_partner_design_appears_under_all_three_of_its_junctions():
    """The cross-partner result is only true if one sequence really is filed under three seams."""
    seq = "GCATATCATCAAACCA"
    for label in ("EWSR1_e12__NR4A3_e3", "FUS_e10__NR4A3_e3", "TAF15_e11__NR4A3_e3"):
        assert any(r["antisense_5to3"] == seq for r in _junction(label)["designs"]), label


def test_no_junction_is_untargetable():
    """The paper's headline, restated as a property of the table: designability is universal.
    A junction with no design clearing the parent screen is a real and reportable state, but it
    must never be that NO design exists at all."""
    for j in _art()["junctions"]:
        assert j["n_designs_screened"] > 0, j["junction_label"]


def test_ties_on_locus_breadth_break_on_margin_not_on_raw_hits():
    """⛔ THE TIE-BREAK THAT REINTRODUCED THE INFLATION IT WAS SUPPOSED TO REMOVE.

    At EWSR1 e12 — type 1, the most commonly reported junction — the two leading registers touch
    the SAME number of gene loci (6), which §3.7 establishes is the honest breadth denominator.
    They differ 3.6-fold on raw transcript hits (34 vs 123) purely through isoform and predicted-
    model multiplicity. Breaking the tie on hits promoted the margin-1 design and made the
    manuscript's long-standing pick look superseded; it is not, and the correct tie-break is
    fusion-versus-parent discrimination. If this ever flips back, the paper's lead reagent silently
    changes on an artifact of RefSeq annotation depth."""
    j = _junction("EWSR1_e12__NR4A3_e3")
    rows = {r["antisense_5to3"]: r for r in j["designs"]}
    a, b = rows["GGGCATATCATCAAAC"], rows["GCATATCATCAAACCA"]
    assert a["n_gap_paired_loci"] == b["n_gap_paired_loci"] == 6, (a, b)
    assert a["n_gap_paired"] == 123 and b["n_gap_paired"] == 34
    assert a["gap_specificity_margin"] == 3 and b["gap_specificity_margin"] == 1
    assert j["best_available"]["antisense_5to3"] == "GGGCATATCATCAAAC", j["best_available"]


def test_the_two_published_junctions_are_tiered_apart_from_the_rest():
    """⚠ ABSENCE OF EVIDENCE IS NOT EVIDENCE OF ABSENCE, AND THE TIERS MUST KEEP THEM APART.
    Only EWSR1 e12 and TAF15 e6 carry a published exon-resolved EMC breakpoint. A TAF15 design at
    another exon is CONTRADICTED by the resolved ones; a FUS design is merely unreported, because
    no exon-resolved FUS breakpoint has been published at all. Collapsing those two into one
    'unreported' bucket would let a contradicted design pass as an unobserved one."""
    published = {j["junction_label"] for j in _art()["junctions"]
                 if j["clinical_tier"] == "published_exon_resolved_breakpoint"}
    assert published == {"EWSR1_e12__NR4A3_e3", "TAF15_e6__NR4A3_e3"}, sorted(published)
    for label in published:
        assert _junction(label)["breakpoint_refs"], f"{label} claims publication with no reference"
    assert _junction("TAF15_e1__NR4A3_e3")["clinical_tier"] == \
        "partner_published_this_exon_not_reported"
    assert _junction("FUS_e8__NR4A3_e3")["clinical_tier"] == "no_published_exon_resolved_breakpoint"


def test_both_published_junctions_have_a_usable_reagent():
    """The answer to the question that prompted this file. Neither is clean; both are usable, and
    the table must say so rather than presenting one global winner."""
    for label in ("EWSR1_e12__NR4A3_e3", "TAF15_e6__NR4A3_e3"):
        best = _junction(label)["best_available"]
        assert best is not None, f"no design clears the parent screen at {label}"
        assert best["parent_is_liability"] is False
        assert best["gap_specificity_margin"] == 3, (label, best)


def test_the_table_reproduces_from_committed_inputs():
    import aso_per_junction_table as m  # noqa: E402
    assert m.main(["--check"]) == 0, "aso-per-junction-table.json is stale; re-run the script"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
