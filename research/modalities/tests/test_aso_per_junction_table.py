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


def test_the_published_junctions_are_tiered_apart_from_the_rest():
    """⚠ ABSENCE OF EVIDENCE IS NOT EVIDENCE OF ABSENCE, AND THE TIERS MUST KEEP THEM APART.
    A TAF15 design at an unreported exon is CONTRADICTED by the resolved ones; a FUS design is
    merely unreported, because no exon-resolved FUS breakpoint has been published at all.
    Collapsing those two into one 'unreported' bucket would let a contradicted design pass as an
    unobserved one.

    ⛔ THIS TEST USED TO ASSERT TWO JUNCTIONS AND WAS ASSERTING A CURATION BUG. EWSR1 e13 is the
    second-most-common EWS/CHN transcript (type 5), named in the same abstract this repository
    already cited for e12 and confirmed independently by a whole-transcriptome cohort
    (PMID 29937513). Tiering it 'this exon not reported' said the opposite of the source, and
    because the tier gates which junctions the manuscript will name a reagent at, the miss cost
    10.6 percentage points of coverage at a junction whose design was already screened. A test
    that pins a wrong curation is worse than no test: it makes the bug look deliberate.

    ⭐ AND IT GREW A FOURTH ON 2026-08-15, FROM A SEQUENCE DATABASE RATHER THAN FROM A PAPER.
    TCF12 e5 sat in the bottom tier because the primary report describes its chimera by residue
    count and names no exon. The same authors deposited the chimeric cDNA (GenBank AF289510.1),
    which resolves the junction to the nucleotide; 295 + 104 retrieved papers could not have found
    it, because it was never published as an exon in prose. Derivation:
    research/manuscripts/tcf12_breakpoint_assignment.py. ⚠ Superseded, retained: this set was
    {EWSR1 e12, EWSR1 e13, TAF15 e6}."""
    published = {j["junction_label"] for j in _art()["junctions"]
                 if j["clinical_tier"] == "published_exon_resolved_breakpoint"}
    assert published == {"EWSR1_e12__NR4A3_e3", "EWSR1_e13__NR4A3_e3",
                         "TAF15_e6__NR4A3_e3", "TCF12_e5__NR4A3_e3",
                         "TFG_e7__NR4A3_e3"}, sorted(published)
    for label in published:
        assert _junction(label)["breakpoint_refs"], f"{label} claims publication with no reference"
    assert _junction("TAF15_e1__NR4A3_e3")["clinical_tier"] == \
        "partner_published_this_exon_not_reported"
    # ⛔ TCF12's OTHER exons moved tier too, and that is the point of the tier rather than a side
    # effect: a design at TCF12 exon 7 is now CONTRADICTED by a resolved exon of its own partner,
    # where before it was merely unobserved. §5.4 of the manuscript names that design as a control.
    assert _junction("TCF12_e7__NR4A3_e3")["clinical_tier"] == \
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


def test_only_the_manuscripts_geometry_reaches_the_table():
    """⛔ THE MERGE DEFECT THIS CATCHES CHANGED THE THREE CLINICALLY CENTRAL ROWS (2026-08-14).

    `_deep_screens` globs `junction-aso-offtarget-*deep500*.json`, and the gap-length work writes
    18-mer 5-8-5 and 20-mer 5-10-5 screens under that pattern. Letting them in did two things, and
    only the first is a pooling complaint. The six re-screened junctions went from 5 designs to 21;
    and `best_available` at the EWSR1 e12, FUS e10 and TAF15 e11 seams moved off the 16-mer this
    paper reports onto an 18-mer — scored, moreover, against `ja.GAP_REGION_1BASED`, which is
    5-6-5's (6, 11), so six of that design's eight catalytic bases were counted as its whole gap.

    A per-junction reagent table that silently answers for a different molecule than the paper
    discusses is worse than one that refuses, so the filter is asserted from both ends: every design
    that reaches the table is the manuscript's length, and the screens on disk really do include
    other lengths, so the test would fail if the filter were quietly matching everything.
    """
    import aso_per_junction_table as P  # noqa: PLC0415
    import junction_aso_locus_collapse as C  # noqa: PLC0415

    pairs = P._deep_screens()
    assert pairs, "no deep screens were read at all"
    lens = {len(seq) for _, seq, _ in pairs}
    assert lens == {C.MANUSCRIPT_OLIGO_LEN}, sorted(lens)

    # the guard is only meaningful if something was actually there to exclude
    import aso_screen_sets as ass  # noqa: PLC0415
    seen = {g.oligo_len for g, ss in ass.iter_geometries(ass.BLAST_SCREEN, root=MOD)
            if any(ass.is_deep(s) for s in ss)}
    assert seen - {C.MANUSCRIPT_OLIGO_LEN}, (
        "no longer-geometry screen is present, so this test proves nothing about the filter")

    for j in _art()["junctions"]:
        b = j["best_available"]
        if b is not None:
            assert len(b["antisense_5to3"]) == C.MANUSCRIPT_OLIGO_LEN, (
                f"{j['junction_label']} recommends a {len(b['antisense_5to3'])}-mer")
