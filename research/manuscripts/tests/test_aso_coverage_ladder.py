#!/usr/bin/env python3
"""The junction-ASO coverage ladder, tied to the two files it is supposed to agree with.

⛔ WHY THIS EXISTS. Three files now carry the same breakpoint counts: `aso_reagent_coverage.py`
(the one home for the 68.4% figure and the 58-case partner denominator), `aso_coverage_ladder.py`
(what each additional reagent buys), and `aso/lit-targets-aso-breakpoint-census.json` (the retrieved
evidence behind every junction). The ladder's own docstring says its first rung "reproduces 68.4%
exactly — which is the check that the two have not drifted", and until this file existed nothing
ran that check. A cross-check nobody executes is a comment.

⚠ WHAT THESE ASSERT, AND WHAT THEY CANNOT. They assert that the three files agree with each other
and that a BOUND is never rendered as a reachable target. They cannot assert that any breakpoint
count is true — that is what the census's verbatim quotes and the corpus index are for, and the
identifier half is `lint_citations.py`'s job. Claim strength and citation provenance are orthogonal
(CLAUDE.md §7), and so is arithmetic consistency, which is this file.

⛔ TWO OF THESE ARE TRIPWIRES RATHER THAN INVARIANTS — `test_the_taf15_intron2_isoform_still_has_no
_count` and `test_tcf12_still_has_no_exon_resolved_breakpoint`. They fail the day a molecule agent
lands a count, and that failure is the POINT: each of those counts changes a published figure, so
the correct response is to re-derive the arm, register the superseded value in pinned-figures.json
in the same commit, and then update the tripwire — never to delete it.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MAN = os.path.dirname(HERE)
LADDER_ART = os.path.join(MAN, "aso", "fusion-junction-aso-coverage-ladder.json")
COVERAGE_ART = os.path.join(MAN, "aso", "fusion-junction-aso-reagent-coverage.json")
CENSUS = os.path.join(MAN, "aso", "lit-targets-aso-breakpoint-census.json")
sys.path.insert(0, MAN)


def _json(path, what):
    if not os.path.exists(path):
        pytest.skip(f"{what} is not present in this checkout")
    return json.load(open(path, encoding="utf-8"))


def _ladder():
    return _json(LADDER_ART, "the coverage ladder artifact")


def _census():
    return _json(CENSUS, "the breakpoint census")


def test_rung_zero_reproduces_the_published_coverage_figure():
    """⛔ THE LOAD-BEARING CROSS-CHECK. Rung 0 is the manuscript's own panel computed on the
    manuscript's own basis, so if it ever stops equalling `aso_reagent_coverage.py`'s figure, one of
    the two has drifted and the ladder's deltas are being read off the wrong baseline.

    Derived on both sides rather than typed on either (CLAUDE.md rule 1.1).
    """
    rung0 = _ladder()["ladder"][0]
    published = _json(COVERAGE_ART, "the reagent-coverage artifact")["coverage"]["percent"]
    assert rung0["kind"] == "rung", rung0["kind"]
    assert rung0["coverage_percent"] == published, (
        f"ladder rung 0 is {rung0['coverage_percent']}% but aso_reagent_coverage.py publishes "
        f"{published}% — the two have drifted. Fix whichever is wrong; do not relax this.")
    assert set(rung0["junctions"]) == {"EWSR1_e12__NR4A3_e3", "TAF15_e6__NR4A3_e3"}, (
        "rung 0 must be the panel the manuscript actually names, or it is not a baseline")


def test_a_bound_is_never_rendered_as_a_reachable_target():
    """⛔ THE DISTINCTION THE LADDER EXISTS TO PRESERVE. A rung is a panel someone could build; a
    bound is an upper limit resting on unnamed transcript types or an inferred exon. Every figure at
    or above 95% in this ladder is a bound, and quoting one as a target is the same denominator
    error the 68.4% correction was made to fix — one level up.
    """
    for row in _ladder()["ladder"]:
        assert row["kind"] in ("rung", "bound"), row["kind"]
        if row["kind"] == "bound":
            assert row["_why_a_bound_and_not_a_rung"], (
                f"{row['panel']!r} is a bound with no stated reason — a bound whose reason is "
                "missing reads exactly like a rung")
        else:
            assert row["_why_a_bound_and_not_a_rung"] is None, row["panel"]
        if row["coverage_percent"] >= 95.0:
            assert row["kind"] == "bound", (
                f"{row['panel']!r} reaches {row['coverage_percent']}% as a RUNG. Nothing in the "
                "retrieved record supports a buildable panel at or above 95%; if that changed, the "
                "evidence belongs in the census first.")


def test_no_rung_claims_a_junction_that_has_no_design_at_all():
    """A rung that silently includes an undesignable junction prices coverage nobody can order."""
    for row in _ladder()["ladder"]:
        if row["kind"] != "rung":
            continue
        undesigned = row["junctions_with_no_design_at_all"]
        designed_unscreened = row["junctions_designed_but_not_yet_screened"]
        assert not (undesigned and not designed_unscreened) or row["what_it_costs"], row["panel"]
        # ⛔ A DESIGNED-BUT-UNSCREENED JUNCTION MUST SAY SO ON ITS OWN RECORD. Collapsing the three
        # states (screened / designed-unscreened / nothing) into two is how an unscreened sequence
        # gets read as a panel member.
        for label, rec in designed_unscreened.items():
            assert "NONE" in rec["offtarget_screens_run"], (label, rec)
            assert rec["antisense_5to3"], label


def test_the_single_series_basis_is_the_pooled_basis_minus_the_second_series():
    """⛔ ONE FACT, ONE PLACE, ACROSS THREE FILES. The ladder retypes two sets of breakpoint counts;
    the census holds the pooled ones and the per-record counts of the second series. If those two
    bases ever stop differing by exactly the second series, one of the three files has been edited
    without the others and every delta on the ladder is suspect.

    Second series: PMID 29937513, whole-transcriptome, five EMC cases each resolved to an exon pair.
    """
    import aso_coverage_ladder as L  # noqa: PLC0415

    urbini = [r for r in _census()["records"] if r["pmid"] == "29937513"]
    assert len(urbini) == 1, "the second breakpoint series is not in the census"
    urbini = urbini[0]
    n_second = urbini["n_ewsr1_cases_with_a_resolved_junction"]
    counts = urbini["counts"]

    single, pooled = L.BASES["single_series"]["EWSR1"], L.BASES["pooled_two_series"]["EWSR1"]
    assert pooled["n"] - single["n"] == n_second, (
        f"pooled EWSR1 denominator {pooled['n']} minus single-series {single['n']} is not the "
        f"{n_second} cases PMID 29937513 reports")
    for junction, k_pooled in pooled["k"].items():
        expect = k_pooled - counts.get(junction, 0)
        assert single["k"][junction] == expect, (
            f"{junction}: single-series basis says {single['k'][junction]}, but pooled "
            f"{k_pooled} minus PMID 29937513's {counts.get(junction, 0)} is {expect}")
    # TAF15 is measured in one series only, so the two bases must be identical there.
    assert L.BASES["single_series"]["TAF15"] == L.BASES["pooled_two_series"]["TAF15"]


def test_the_pooled_counts_match_the_census_and_account_for_every_case():
    """The pooled basis and the census must agree, and the census's arms must sum to its own
    denominator — including the unresolved tumours, which are the reason the top rung is a bound."""
    import aso_coverage_ladder as L  # noqa: PLC0415

    jc = _census()["junction_census"]
    pooled = L.BASES["pooled_two_series"]["EWSR1"]
    total = jc["_unresolved"]["k"]
    for junction, k in pooled["k"].items():
        assert jc[junction]["k"] == k, (junction, jc[junction]["k"], k)
        assert jc[junction]["n"] == pooled["n"], (junction, jc[junction]["n"], pooled["n"])
        total += k
    assert jc["_unresolved"]["n"] == pooled["n"]
    assert total == pooled["n"], (
        f"the census's EWSR1 arms plus its unresolved tumours sum to {total}, not {pooled['n']} — "
        "a case is being counted twice or dropped")


def test_the_taf15_intron2_isoform_still_has_no_count():
    """⛔ TRIPWIRE, NOT AN INVARIANT — AND THE ONE THAT CAN LOWER A PUBLISHED FIGURE.

    The TAF15 arm is priced at 3/3 — every TAF15-rearranged tumour at exon 6 to NR4A3 exon 3 — on a
    three-tumour series. A functional study engineered cells with a second isoform joining exon 6 to
    NR4A3 intron 2 and called it one of the two major isoforms detected in human tumours, so if any
    TAF15 patient carries it, the single TAF15 reagent does not reach them and 68.4% is optimistic
    on that arm. No count has been retrieved, so it is a named risk rather than a correction.

    WHEN THIS FAILS: a count has landed. Re-derive the TAF15 arm, register 68.4% (and any other
    figure that moves) in pinned-figures.json IN THE SAME COMMIT, then update this tripwire.
    """
    intron2 = _census()["junction_census"]["TAF15_e6__NR4A3_intron2"]
    assert intron2["k"] is None and intron2["n"] is None, (
        "a count for the TAF15 intron-2 isoform is now in the census. The TAF15 arm is priced at "
        "3/3 in aso_reagent_coverage.py and aso_coverage_ladder.py and must be re-derived; the "
        "superseded coverage figure goes in pinned-figures.json in the same commit.")


def test_the_tcf12_exon_is_resolved_and_its_distribution_still_is_not():
    """⛔ TRIPWIRE, REWRITTEN 2026-08-15 BECAUSE ITS PREDECESSOR FIRED AND WAS RIGHT TO.

    ⚠ SUPERSEDED, RETAINED: `test_tcf12_still_has_no_exon_resolved_breakpoint`, which asserted
    `junction_census["TCF12"]["k"] is None`. An exon-resolved TCF12::NR4A3 junction WAS retrieved —
    GenBank AF289510.1, the chimeric cDNA deposited with PMID 11156374 — so the tripwire fired
    exactly as designed and the state it guarded is gone.

    ⛔ WHAT REPLACED IT IS NOT A WEAKER VERSION OF THE SAME CHECK. The old one guarded "we do not
    know the exon". This one guards the thing that is STILL true and still decides the top row: one
    TCF12-rearranged tumour has ever been sequenced at this junction, and it is the same tumour the
    junction was defined by, so there is no within-partner FRACTION and the arm must stay priced at
    its ceiling. Promoting the top row to a rung on the strength of a resolved exon would be the
    exact error the old tripwire existed to prevent, arriving from the other direction.

    WHEN THIS FAILS: either a second TCF12 tumour has been resolved (re-derive the arm, register
    every moved figure in pinned-figures.json IN THE SAME COMMIT), or someone has quietly fed 1/1
    into the ladder's bases (do not).
    """
    ladder_mod = __import__("aso_coverage_ladder")
    census = _census()["junction_census"]
    assert "TCF12" not in census, (
        "the placeholder TCF12 entry is back. The junction census now keys this arm by its resolved "
        "junction, TCF12_e5__NR4A3_e3.")
    row = census["TCF12_e5__NR4A3_e3"]
    assert row["k"] == 1 and row["n"] == 1, (
        f"the TCF12 within-partner count moved to {row['k']}/{row['n']}. A second sequenced tumour "
        "changes the arm from 'priced at its ceiling' to measurable — re-derive it deliberately.")
    assert "TCF12" in ladder_mod.PARTNERS_WITH_NO_BREAKPOINT_MEASUREMENT, (
        "TCF12 left PARTNERS_WITH_NO_BREAKPOINT_MEASUREMENT. n=1 is the same tumour the junction "
        "was defined by; treating it as a within-partner fraction manufactures a measurement.")
    for basis in ladder_mod.BASES.values():
        assert "TCF12" not in basis, (
            "TCF12 has been given a breakpoint basis. See the census entry's own note on why 1/1 is "
            "not a within-partner fraction.")
    top = _ladder()["ladder"][-1]
    assert top["kind"] == "bound", (
        "the TCF12 row became a rung. A resolved exon makes the REAGENT available; it does not "
        "measure the arm, and the total above it is still an upper bound.")


def test_the_tcf12_junction_is_tiered_as_published_and_carries_its_deposit():
    """⭐ The other half of the same correction, on the file that decides which junctions the
    manuscript will name a reagent at.

    The tier drives that decision — the EWSR1 exon-13 miss cost real coverage for exactly this
    reason — so a junction whose breakpoint is resolved at NUCLEOTIDE resolution must not still be
    reading `no_published_exon_resolved_breakpoint`.
    """
    tab = _json(os.path.join(os.path.dirname(MAN), "modalities", "aso-per-junction-table.json"),
                "the per-junction reagent table")
    row = next(j for j in tab["junctions"] if j["junction_label"] == "TCF12_e5__NR4A3_e3")
    assert row["clinical_tier"] == "published_exon_resolved_breakpoint", row["clinical_tier"]
    assert any("AF289510" in r for r in row["breakpoint_refs"]), row["breakpoint_refs"]
    assert row["best_available"], "the junction that decides the 95% question has no reagent"


def test_the_tcf12_assignment_artifact_confirms_the_seam_the_panel_designed_on():
    """⛔ THE LOAD-BEARING ONE, AND IT IS ABOUT A SEAM RATHER THAN A LABEL. An exon ORDINAL depends
    on a transcript model and could move under a re-annotation; the twelve bases either side of the
    junction are what every design in the panel hybridises to. This asserts that the deposited
    sequence and the modelled seam are the same string, which is the statement a reagent rests on.
    """
    art = _json(os.path.join(MAN, "aso", "tcf12-breakpoint-assignment.json"),
                "the TCF12 breakpoint assignment artifact")
    t = art["tests"]
    assert t["A_donor_side_ends_at_exactly_one_TCF12_exon"]["exons_matching"] == [5]
    assert t["B_acceptor_side_starts_at_exactly_one_NR4A3_exon"]["exons_matching"] == [3]
    seam = t["C_the_deposited_seam_equals_the_seam_the_panel_designed_on"]
    assert seam["identical"], (seam["modelled_seam"], seam["deposited_seam"])
    assert seam["modelled_junction_label"] == "TCF12_e5__NR4A3_e3"
    prot = t["D_the_protein"]
    assert prot["our_translation_reproduces_the_deposited_one"]
    assert prot["leading_residues_identical_to_TCF12"] == 108
    assert prot["chimera_ends_with_the_entire_NR4A3_protein"]


def test_every_census_identifier_is_a_bare_numeric_pmid():
    """⚠ NOT A PROVENANCE CHECK — `lint_citations.py` owns that, and claim strength is orthogonal to
    citation provenance. This catches the shape errors that make provenance unverifiable: a PMID
    written with a prefix, a PMCID that is not a PMCID, a DOI that is a URL.

    The census is the file in which a PMID was once written from recollection (36404609, actually
    36614077). Every identifier in it is now read from the corpus index; this keeps them in a form
    an index lookup can actually match.
    """
    census = _census()
    for rec in census["records"]:
        pmid = rec["pmid"]
        assert pmid.isdigit(), f"PMID {pmid!r} is not a bare numeric identifier"
        pmcid = rec.get("pmcid")
        if pmcid is not None:
            assert pmcid.startswith("PMC") and pmcid[3:].isdigit(), pmcid
        doi = rec.get("doi")
        if doi is not None:
            assert doi.startswith("10.") and "://" not in doi, doi
    pmids = [r["pmid"] for r in census["records"]]
    assert len(pmids) == len(set(pmids)), "the census lists the same paper twice"


def test_the_census_reports_at_least_as_many_junction_papers_as_it_lists():
    """The retrieval header and the record list must not disagree about how much evidence there is.

    ⚠ Deliberately an inequality. `n_reporting_an_exon_resolved_junction` counts papers reporting a
    junction; the record list also carries papers held for a bound, a ceiling or an assay-panel
    composition, which report no per-case junction at all.
    """
    census = _census()
    n_records = len(census["records"])
    n_junction_papers = census["source"]["n_reporting_an_exon_resolved_junction"]
    assert n_records >= n_junction_papers, (n_records, n_junction_papers)
    assert census["source"]["n_mentioning_emc"] <= census["source"]["n_papers_retrieved"]


PAPER = os.path.join(MAN, "aso", "fusion-junction-aso-research-article.md")


def _paper_flat():
    if not os.path.exists(PAPER):
        pytest.skip("the submission manuscript is not present in this checkout")
    return " ".join(open(PAPER, encoding="utf-8").read().split())


def test_the_manuscripts_best_supported_figure_is_the_artifacts_and_does_not_displace_68_4():
    """§5.1's best-supported-panel paragraph, read off the row that derives it.

    ⛔ THE FAILURE THIS PREVENTS IS A SILENT PROMOTION. The best-supported row and the manuscript's
    published 68.4% answer different questions — one prices a membership-derived set on the whole
    retrieved breakpoint record, the other prices the two named reagents on the single series the
    published figure was computed on. A paper that printed the larger figure without keeping the
    smaller one attached to its own claim would be reporting a better result than it has, so both
    numbers and the sentence separating them are asserted together.
    """
    best = _ladder()["best_supported_buildable_panel"]
    txt = _paper_flat()
    lo, hi = best["coverage_percent_range"]
    assert f"the eight together are {best['coverage_percent']}%" in txt
    assert f"widening that to {lo}–{hi}%" in txt
    assert "That figure supersedes nothing" in txt
    assert "68.4% remains the coverage of the two reagents" in txt
    # membership is a derived count, and the manuscript may not carry a different one
    n = best["panel_membership"]["n_junctions_qualifying"]
    assert n == 8, n
    assert "eight junctions now hold both such a breakpoint and a design carried through all five " \
           "screens" in txt
    # ⛔ THE ZERO-CONTRIBUTING MEMBER MUST BE NAMED AS CONTRIBUTING ZERO. Reading it as a small
    # positive contribution is exactly the error the row's own note refuses.
    zero = best["panel_membership"]["⛔_qualifying_but_contributing_exactly_zero"]["junctions"]
    assert zero == ["PGR_e2__NR4A3_e2"], zero
    assert "*PGR* exon 2 to *NR4A3* exon 2, moves the figure by exactly zero" in txt


def test_the_manuscripts_within_partner_donor_run_is_the_measured_maximum():
    """⛔ A CORRECTION PINNED SO IT CANNOT REVERT. §5.1 read "the longest shared 3′ donor run is
    three nucleotides" across every within-partner pair in the panel. Three is the *EWSR1* maximum;
    the panel-wide within-partner maximum is five, at *TFG* exons 2 and 6. The sentence understated
    the one quantity that decides whether one oligonucleotide could ever serve two breakpoints of a
    partner, in the direction that flatters the argument, so both figures are now derived from the
    multiplexing check rather than typed.
    """
    check = _ladder()["can_better_design_raise_coverage"]
    txt = _paper_flat()
    worst = max(check["within_partner_best_pair_per_partner"],
                key=lambda w: w["shared_3prime_donor_nt"])
    assert worst["shared_3prime_donor_nt"] == check["max_within_partner_shared_donor_nt"]
    assert f"the longest shared 3′ donor run is {_word(worst['shared_3prime_donor_nt'])} " \
           "nucleotides" in txt
    ewsr1 = next(w for w in check["within_partner_best_pair_per_partner"]
                 if w["partner"] == "EWSR1")
    assert f"and {_word(ewsr1['shared_3prime_donor_nt'])} within *EWSR1*" in txt
    # and the two junctions the whole ladder turns on share a single terminal base
    assert check["the_two_junctions_that_matter_most"]["shared_3prime_donor_nt"] == 1
    assert "which agree over a single terminal base" in txt


def _word(n):
    return {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}[n]
