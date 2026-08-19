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


def test_the_third_series_refusal_rests_on_an_arithmetic_fact_not_an_opinion():
    """⛔ THE REFUSAL THAT COSTS 4.5 POINTS, MADE CHECKABLE.

    PMID 11679947 would raise the buildable figure if pooled, and it is refused under
    POLICY-evidence.md §2.1(3) — its denominator is defined by its own assay's positivity. That is
    not a matter of judgement and this asserts the arithmetic that decides it: the series' EWSR1 arm
    is k = n for the junctions the panel covers, because a tumour with any other junction could not
    have entered a denominator built from that assay's own hits. §2.1(3)'s own example is a cohort
    whose outcome count is structurally 100%; this is one.

    ⛔ AND THE CONTRAST IS ASSERTED TOO, because "this cohort is structurally 100%" only means
    something if the cohort that IS pooled is not. PMID 12378528 names 12 of 15, so k < n there.

    ⚠ THE OTHER ORIGINAL GROUND WAS WITHDRAWN ON 2026-08-15 and is deliberately NOT asserted here:
    the type-nomenclature objection does not reach a series reporting only types 1 and 2, on which
    PMID 9060841, 12598313 and 22567356 agree. A refusal resting on a ground that has fallen is a
    refusal waiting to be overturned for the wrong reason, which is why it now rests on this one.

    WHEN THIS FAILS: someone has pooled the third series or changed its arm. Pooling it moves a
    published figure, so the superseded value goes in pinned-figures.json IN THE SAME COMMIT — and
    the reason had better not be that the number is attractive.
    """
    sens = _ladder()["best_supported_buildable_panel"]["sensitivity_if_the_third_series_were_pooled"]
    struct = sens["⛔_the_structural_100_percent"]
    k, n = struct["okamoto_k_over_n_for_the_covered_junctions"].split("/")
    assert k == n, (
        f"PMID 11679947's covered-junction arm is {k}/{n}. It was {k}=={n} — structurally 100% — "
        "which is the whole §2.1(3) ground for refusing it. If that changed, the refusal needs "
        "re-arguing from the source, not relaxing here.")
    assert struct["is_it_structurally_one_hundred_percent"] is True
    pooled_k, pooled_n = struct["the_same_check_on_the_series_that_IS_pooled"]["PMID 12378528"].split("/")
    assert int(pooled_k) < int(pooled_n), (
        f"the series that IS pooled is now {pooled_k}/{pooled_n}. If its denominator has become "
        "structurally complete too, it fails the same §2.1(3) test and the basis must be re-argued.")
    # the withdrawn ground is recorded as withdrawn, not deleted
    assert sens["_what_it_is"]
    third = _ladder()["best_supported_buildable_panel"]["pooling_admissibility"][
        "third_series_deliberately_not_pooled"]
    withdrawn = third["⭐_2026_08_15_A_SECOND_GROUND_WAS_TESTED_AND_IT_FELL_—_THE_REFUSAL_NARROWED"]
    assert len(withdrawn["three_concordant_primary_definitions_of_types_1_and_2"]) == 3
    assert withdrawn["verdict"].startswith("THE REFUSAL STANDS")


def test_the_pooled_partner_sensitivity_is_read_from_the_module_that_owns_it():
    """⛔ ONE FACT, ONE PLACE, ACROSS TWO PAPERS' MODULES. The pooled EMC partner prevalence belongs
    to `emc_fusion_partner_pooling.py`, which built it for the TAF15 prognostic synthesis against
    POLICY-evidence.md §2.1-§2.3. The coverage ladder reads it. If the ladder ever carries counts
    that artifact does not, someone has retyped a clinical proportion into a second home — which is
    the failure mode rule 1 exists for, and it would let the two drift silently.

    ⛔ THE DENOMINATORS ARE DELIBERATELY DIFFERENT AND THAT IS ALSO ASSERTED. The pooling artifact
    pools over PARTNER-ASSIGNED cases; coverage must include the partner-unassigned residue, because
    a tumour whose partner nobody named is exactly a tumour no junction reagent can engage. The
    reconstruction must close on the cohorts' own published totals.
    """
    import json as _json  # noqa: PLC0415

    pool = _json.load(open(os.path.join(MAN, "fusion-partner", "emc-fusion-partner-pooling.json"),
                           encoding="utf-8"))
    sens = _ladder()["best_supported_buildable_panel"][
        "sensitivity_if_the_partner_denominator_is_pooled"]
    prev = [c for c in pool["cohorts"] if c["endpoint"] == "partner_prevalence" and c.get("pool")]
    expect = {}
    for c in prev:
        for label, v in c["counts"].items():
            expect[label.split("::")[0]] = expect.get(label.split("::")[0], 0) + v
    assert sens["pooled_partner_counts"] == expect, (
        "the ladder's pooled partner counts disagree with the artifact it claims to read them "
        "from. One of the two has been hand-edited.")
    assert sens["n_partner_assigned"] == sum(expect.values())
    assert sens["n_partner_unassigned"] == sum(c["not_partner_assigned"] for c in prev)
    assert sens["n_molecularly_confirmed_total"] == sum(c["n_tested"] for c in prev)
    assert (sens["n_partner_assigned"] + sens["n_partner_unassigned"]
            == sens["n_molecularly_confirmed_total"]), (
        "the coverage denominator does not account for its own cases")
    # the pooling artifact's own headline denominator is the assigned one, and must NOT be the
    # denominator coverage is priced on
    assert (pool["analyses"]["C_partner_prevalence"]["pooled"]["EWSR1::NR4A3"]["denom"]
            == sens["n_partner_assigned"] < sens["n_molecularly_confirmed_total"]), (
        "the residue has stopped being added back, so this row is now computing coverage of "
        "partner-assigned EMC while calling it coverage of EMC — the denominator swap that put "
        "95% in the manuscript's abstract")


def test_the_ceiling_crosses_95_percent_on_one_basis_and_not_the_other():
    """⛔ TRIPWIRE, NOT AN INVARIANT — AND IT GUARDS THE LADDER'S HEADLINE RESULT.

    The ladder's answer to "is 95% reachable?" is basis-dependent, and that was not known until the
    partner denominator was tested on 2026-08-15. On the single 58-case series the arithmetic
    ceiling is ABOVE 95%, so 95% is reachable in principle and reaching it requires the TCF12 arm.
    On the four-series pooled partner denominator the ceiling is BELOW 95%, so no panel of any size
    reaches it — because more than five percent of molecularly confirmed EMC has no named partner to
    build a junction reagent against.

    Both are asserted together because the pair IS the result. Quoting either alone overstates what
    is known: the single-series ceiling makes 95% look like a panel-design problem, and the pooled
    one makes it look settled, and neither is true on its own.

    WHEN THIS FAILS: a cohort entered or left the partner pool and moved the ceiling across 95%.
    That changes what the paper can say about its own target, so re-derive it deliberately and
    register every moved figure in pinned-figures.json IN THE SAME COMMIT.
    """
    best = _ladder()["best_supported_buildable_panel"]
    single = best["distance_to_the_arithmetic_ceiling"]["ceiling_percent"]
    pooled = best["sensitivity_if_the_partner_denominator_is_pooled"]["arithmetic_ceiling_percent"]
    assert single > 95.0, (
        f"the single-series ceiling is now {single}%, at or below 95%. The ladder's 'crossing 95% "
        "REQUIRES the TCF12 arm' result is stated on this basis and must be re-derived.")
    assert pooled < 95.0, (
        f"the pooled-partner ceiling is now {pooled}%, at or above 95%. The sensitivity's "
        "load-bearing consequence — that no panel of any size reaches 95% on the wider basis — no "
        "longer holds and the row's own wording must change with it.")
    assert pooled < single, (pooled, single)
    # and the buildable figure itself must not have been quietly re-based onto the wider denominator
    assert best["basis"] == "pooled_two_series", best["basis"]


def test_the_fifth_partner_cohort_is_refused_and_the_refusal_is_priced():
    """⛔ THE REFUSAL THAT COSTS THE HIGHER CEILING, MADE CHECKABLE.

    PMID 12598313 is the only candidate partner cohort that would RAISE the arithmetic ceiling — its
    partner-unassigned residue is zero, and the residue is the whole reason the four-series ceiling
    sits below 95%. A refusal in that direction is exactly the one a reader must be able to audit,
    so three things are asserted rather than described:

      1. it is still refused, and by the module that OWNS the pooling decision, not by this one;
      2. the refusal is priced — the sensitivity it would have produced is present, closes on its
         own totals, and keeps the partner-unassigned residue IN the coverage denominator;
      3. the direction is stated correctly: admitting it raises the ceiling.

    ⛔ AND THE ROBUSTNESS CLAIM IS ASSERTED TOO. `test_the_ceiling_crosses_95_percent_on_one_basis
    _and_not_the_other` guards the four-series ceiling. This guards the strongest perturbation
    anyone has proposed to it: even with the fifth cohort admitted the ceiling stays under 95%. If
    that ever stops being true, the ladder's headline result becomes basis-dependent in a second
    way and must be re-derived, not annotated.

    WHEN THIS FAILS: someone pooled the fifth cohort, or the §2.1(3) ground moved. Either changes
    what the paper can say about 95%, so re-derive it and register every moved figure in
    pinned-figures.json IN THE SAME COMMIT.
    """
    import json as _json  # noqa: PLC0415

    four = _ladder()["best_supported_buildable_panel"][
        "sensitivity_if_the_partner_denominator_is_pooled"]
    fifth = four["fifth_partner_cohort_deliberately_not_pooled"]
    if "_unavailable" in fifth:
        pytest.skip(fifth["_unavailable"])

    pool = _json.load(open(os.path.join(MAN, "fusion-partner", "emc-fusion-partner-pooling.json"),
                           encoding="utf-8"))
    row = next(c for c in pool["cohorts"] if c["id"] == fifth["cohort"]["id"])
    assert row["pool"] is False, (
        f"{row['id']} is now pooled. The ladder's fifth-cohort row prices a REFUSAL; if the refusal "
        "has been lifted the four-series figures are the stale ones and must be rebuilt.")
    assert row["contextReason"] == "outcome-is-the-inclusion-criterion", row["contextReason"]
    assert row["id"] in pool["analyses"]["C_partner_prevalence"]["cohorts_excluded"], (
        "the refusal is not registered in the prevalence analysis' own exclusion list, so a reader "
        "of the pooling artifact cannot see that this cohort was considered at all")

    # (2) priced, and the reconstruction closes on its own totals
    s = fifth["the_sensitivity_it_would_have_produced"]
    assert s["n_partner_assigned"] + s["n_partner_unassigned"] == s["n_molecularly_confirmed_total"]
    assert s["n_partner_assigned"] == four["n_partner_assigned"] + sum(row["counts"].values())
    assert s["n_molecularly_confirmed_total"] == four["n_molecularly_confirmed_total"] + row["n_tested"]
    assert s["n_partner_unassigned"] == four["n_partner_unassigned"] + row["not_partner_assigned"], (
        "the fifth cohort's partner-unassigned residue has stopped being carried into the coverage "
        "denominator. Dropping a residue is the denominator swap that put 95% in the abstract.")
    assert s["n_partner_unassigned"] > 0, (
        "the coverage denominator now contains no partner-unassigned case at all, which would make "
        "the ceiling 100% by construction")

    # (3) direction, and the robustness claim
    assert s["arithmetic_ceiling_percent"] > four["arithmetic_ceiling_percent"], (
        "admitting a zero-residue cohort must RAISE the ceiling. If it does not, the row's own "
        "explanation of why the refusal is conservative is wrong.")
    assert s["arithmetic_ceiling_percent"] < 95.0, (
        f"with the fifth cohort admitted the ceiling is {s['arithmetic_ceiling_percent']}%, at or "
        "above 95%. The sensitivity's conclusion no longer survives its own strongest perturbation "
        "and must be re-derived rather than reworded.")

    # the two §2.3 adjudications this cohort could not be judged without are recorded as settled
    adj = fifth["⭐_the_two_§2.3_adjudications_that_had_to_be_settled_FIRST"]
    assert adj["1_is_its_TCF12_case_the_2000_index_tumour"]["answer"].startswith("YES")
    assert "PATIENT-level" in adj["2_are_its_partner_counts_tumour_level_or_patient_level"]["answer"]
    # and §2.1(3) is decided by arithmetic, not by reading
    arith = fifth["⛔_§2.1(3)_is_DECIDED_BY_ARITHMETIC_NOT_BY_READING"]
    assert (arith["structurally_admitted_previously_reported_patients"]["variant_partner_percent"]
            > arith["freely_admitted_new_patients"]["variant_partner_percent"]), (
        "the structurally-admitted half is no longer enriched for variant partners, which is the "
        "measured fact the §2.1(3) refusal rests on. Re-argue it from the source, do not relax it.")


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
#: ⚠ WIDENED TO THE SUBMISSION, NOT LOOSENED, 2026-08-16. The 2026-08-16 editorial pass generated
#: Table 7 and moved the coverage ladder's SECOND BASIS — the pooled-basis 82.9%, the refused third
#: series, and the two ways a qualifying junction contributes exactly zero — out of the main text and
#: into SI §S6, verbatim. Every string below is still asserted, character for character; what changed
#: is which file of the same submission holds it. Reading only the main text would have made this
#: guard fire on a move it has no opinion about, and the pressure would then have been to delete the
#: assertion rather than to follow the sentence. The property it protects is unchanged and is
#: file-independent: the larger figure may not displace 68.4%, and both must be present with the
#: sentence separating them. Note the abstract-specific pin below still lands in the main text,
#: because the abstract is only there.
SI = os.path.join(MAN, "aso", "fusion-junction-aso-supplementary-information.md")


def _paper_flat():
    if not os.path.exists(PAPER):
        pytest.skip("the submission manuscript is not present in this checkout")
    text = open(PAPER, encoding="utf-8").read()
    if os.path.exists(SI):
        text += "\n" + open(SI, encoding="utf-8").read()
    return " ".join(text.split())


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
    # ⚠ The count is DERIVED from the row, not spelled in this assertion -- it was "eight" until
    # TFG_e7__NR4A3_e3 joined the published tier on a deposited cDNA, and a spelled number here
    # would have had to be chased by hand every time membership moved.
    _WORD = {8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}
    _n = best["panel_membership"]["n_junctions_qualifying"]
    assert f"the {_WORD[_n]} together are {best['coverage_percent']}%" in txt
    # ⚠ "widening that to" -> "widening to" (round 5). The preceding clause used to read "with the
    # same two denominators", which was false: 82.9% pools the EWSR1 arm to 17/20 where 68.4% uses
    # 10/15. Rewriting that clause dropped the "that". The interval itself is unchanged and is what
    # this assertion exists to pin.
    assert f"widening to {lo}–{hi}%" in txt
    # ⭐ THE ABSTRACT'S SECOND COPY OF THIS NUMBER IS GONE, AND THE ASSERTION THAT PINNED IT GOES
    # WITH IT (2026-08-16, editorial pass stage 7). It used to read
    #     assert f"and the whole set is {best['coverage_percent']}%" in txt
    # with the note "THE ABSTRACT IS A SECOND HOME FOR THIS NUMBER … a headline figure that drifts
    # from its own §5.1 is the one a reviewer reads first". That guard existed because the number had
    # TWO homes and could drift between them. The abstract carried four renderings of the coverage
    # percentage — 68.4%, 79.0%, 67.1% and 82.9% (57.5–90.7%) — and the editorial pass cut all four,
    # leaving 82.9% and its interval in SI §S6 alone, priced off this same row. A drift guard whose
    # second home no longer exists cannot fire, and keeping it would have forced the duplicate back
    # into the abstract to satisfy a linter. The first two assertions above still pin the surviving
    # home to the artifact, which is the property that mattered.
    # ⚠ "That figure" -> "The figure" (round 5), same rewrite as the "widening to" pin above. The
    # property — that 82.9% is stated as answering a different question rather than displacing 68.4%
    # — is unchanged, and is what this line exists to hold.
    assert "figure supersedes nothing" in txt
    assert "68.4% remains the coverage of the two reagents" in txt
    # membership is a derived count, and the manuscript may not carry a different one
    n = best["panel_membership"]["n_junctions_qualifying"]
    assert n == _n, (n, _n)
    # ⭐ RE-POINTED AT THE SURVIVING HOME, NOT DELETED (2026-08-16, editorial pass stage 7). This
    # used to read
    #     assert f"{_WORD[n]} junctions now hold both such a breakpoint and a design carried
    #             through all five screens" in txt
    # which pinned the ABSTRACT's recital of the membership count. That recital went with the four
    # coverage renderings the same pass cut from the abstract; SI §S6 states the same derived count
    # and is now its only home. The property guarded is unchanged — the manuscript must carry the
    # count this row derives and no other — so the assertion follows the sentence. Matched
    # case-insensitively because the surviving phrasing opens a sentence.
    #: ⛔ RE-ANCHORED 2026-08-19, AND THE OLD SENTENCE WAS WRONG. It read "nine junctions now
    #: carry both a published exon-resolved breakpoint and a design through all five
    #: screens", while its own next clause says the *PGR* seam is graded on FOUR of the five.
    #: A cross-document audit caught SI §S6 asserting nine where §4.1 says eight-of-nine. The
    #: membership count this row derives is unchanged at nine; what the nine all carry is a
    #: SCREENED design, and eight of them clear all five.
    assert f"{_WORD[n]} junctions now carry a published exon-resolved breakpoint and a " \
           "screened design" in txt.lower()
    # ⛔ THE ZERO-CONTRIBUTING MEMBER MUST BE NAMED AS CONTRIBUTING ZERO. Reading it as a small
    # positive contribution is exactly the error the row's own note refuses.
    # ⛔ EVERY zero-contributor must be named, not just the first. TFG joined this list when a
    # deposited cDNA moved it into the published tier, and a test pinning one name would have let
    # the second go unmentioned in prose while the artifact carried it.
    zero = best["panel_membership"]["⛔_qualifying_but_contributing_exactly_zero"]["junctions"]
    assert zero == ["PGR_e2__NR4A3_e2", "TFG_e7__NR4A3_e3"], zero
    assert "*TFG* exon 7 to *NR4A3* exon 3 is the second" in txt
    # ⚠ ASSERTED AS TWO FRAGMENTS, NOT ONE STRING. Round 5 added the breakpoint citation for this
    # junction between the two halves — "…*NR4A3* exon 2, reported in a single patient,<sup>N</sup>
    # moves the figure by exactly zero" — which broke a contiguous pin without changing anything it
    # was guarding. A superscript is a legitimate thing to insert into any sentence in this paper, so
    # pinning across a spot where one can land makes the assertion fragile rather than strict.
    assert "*PGR* exon 2 to *NR4A3* exon 2" in txt
    assert "moves the figure by exactly zero" in txt


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


def test_the_type3_limitation_states_unlocated_and_not_undesignable():
    """⛔ A RETRACTED CLAIM MUST NOT REACH THE PAPER. The breakpoint census once recorded EWS/CHN
    type 3 as having "NO exon-to-exon seam ... so no junction-spanning oligonucleotide can be
    specified for it at any length or register". The second half is a claim about RNase-H1 and it is
    refuted by measurement: an intra-exonic genomic breakpoint still yields one definite transcript
    seam, and handing the unchanged builder a donor model cut inside its exon returns the panel's own
    tiling geometry. What such a junction lacks is an exon INDEX — a property of this repository's
    design grammar — and a published nucleotide position.

    The Limitations paragraph is asserted against the artifact that measured it, and the refuted
    wording is asserted ABSENT, because "we corrected the census" is not the same as "the paper never
    said it" and only one of those is checkable.
    """
    art = os.path.join(MAN, "aso", "lit-targets-aso-type3-designability.json")
    d = _json(art, "the type-3 designability artifact")
    txt = _paper_flat()
    assert d["⛔_the_verdict"].startswith("UNLOCATED AND INEXPRESSIBLE — NOT UNDESIGNABLE")
    rows = d["⭐_the_measurement_that_decides_it"]["intra_exonic_probe_rows"]
    assert {r["n_tiled"] for r in rows} == {5}, rows
    assert {r["n_gap_centered"] for r in rows} == {3}, rows
    assert {r["best_gap_specificity_margin"] for r in rows} == {3}, rows
    assert all(r["n_fusion_specific"] == r["n_tiled"] for r in rows), rows
    #: ⚠ "candidates" -> "builder outputs" (vocabulary audit, 2026-08-19). The paper used
    #: "candidate" in three senses: §2.7's screened set of three, Box 1/§4.5's "a candidate,
    #: not a validated reagent" for whatever the procedure emits, and this — five designs the
    #: builder returned that have cleared no screen at all. §4.4 then calls §2.7's three
    #: "mechanism controls rather than candidates", so the word was carrying a verdict it had
    #: not earned here. The count and every property beside it are unchanged.
    assert "returns five builder outputs, all fusion-specific against both parents, three gap-centred " \
           "and a best gap-level margin of 3" in txt
    assert "Such a breakpoint is not undesignable" in txt
    assert "What such a junction lacks is an exon index" in txt
    # ⛔ the refuted sentence, in the forms it could plausibly reappear in
    for dead in ("no junction-spanning oligonucleotide can be specified",
                 "type 3 is undesignable", "has no exon-to-exon seam"):
        assert dead not in txt, f"the refuted type-3 claim is in the manuscript: {dead!r}"
    # and the quantity the artifact refuses to supply must not be supplied
    assert "How many tumours this accounts for is not established by any source" in txt
