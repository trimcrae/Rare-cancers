#!/usr/bin/env python3
"""The off-target tissue-expression read, and the guards that stop it over-claiming.

⛔ WHY THIS EXISTS. This is the one check that most changes what the manuscript can say about its
one clinically-relevant reagent, and it is the check most likely to be misread in the flattering
direction. Three specific misreadings are asserted against here, because each of them produces a
file that looks exactly like a correct one:

  1. an absent row rendering as "not expressed" — the failure CLAUDE.md §4 is written about, and
     the one that would let two uncharacterised loci be reported as clean;
  2. a shifted GCT parse emitting tissue figures that are internally consistent and wrong;
  3. a transcript-record count being read as a risk ranking, which would make ANKS1B and ZNF667 the
     headline finding on the strength of nothing but RefSeq annotation depth.

A finding that arrives with a number attached is exactly the kind that drifts when prose is next
edited, so every locus count here is asserted against the committed screen rather than a remembered
value. A failure means the two have diverged; fix whichever is wrong and do not relax the assertion.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, "aso-offtarget-tissue-expression.json")
SCREEN = os.path.join(MOD, "junction-aso-offtarget-e12n3-deep500-b1.json")
sys.path.insert(0, MOD)

import aso_offtarget_tissue_expression as m  # noqa: E402


def _art():
    if not os.path.exists(ART):
        pytest.skip("the tissue-expression artifact is not present in this checkout")
    return json.load(open(ART, encoding="utf-8"))


def _screen():
    if not os.path.exists(SCREEN):
        pytest.skip("the deep off-target screen is not present in this checkout")
    return json.load(open(SCREEN, encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The locus set — derived, never typed
# ─────────────────────────────────────────────────────────────────────────────────────────────

def test_the_six_loci_are_derived_from_the_committed_screen():
    """⛔ THE ONE TABLE EVERYTHING ELSE HANGS ON. If the screen is re-run and the loci move, this
    fails rather than letting a stale six-row table be read as current."""
    _, rows, prov = m._locus_rows()
    assert prov["n_gap_paired_hybridisable"] == 123
    assert prov["n_loci"] == 6
    got = {r["locus"]: r["n_transcript_records"] for r in rows}
    assert got == {"ANKS1B": 67, "ZNF667": 37, "GMCL1": 9,
                   "LOC105374140": 5, "LOC105370997": 4, "CHST5": 1}
    assert sum(got.values()) == prov["n_gap_paired_hybridisable"]


def test_every_hit_is_two_mismatches_which_is_what_bounds_the_whole_claim():
    """⛔ THE FACT THAT STOPS A SEQUENCE MATCH BECOMING A CLEAVAGE EVENT. All 123 sit at the
    screen's loosest admitted identity. If a stricter class ever appears in this set, the artifact's
    framing paragraph is understating the load and must be rewritten."""
    _, gap_paired = m._screen_hits()
    assert len(gap_paired) == 123
    assert {h["identity"] for h in gap_paired} == {14}
    assert {16 - h["identity"] for h in gap_paired} == {2}
    assert {h["gap_mismatches"] for h in gap_paired} == {0}
    assert not any(h["is_minus_strand"] for h in gap_paired)


def test_the_predicted_model_fraction_is_carried_not_lost():
    """82 of 123 records are computationally predicted gene models. That is a different kind of
    liability from a curated one and the artifact must keep the split."""
    _, rows, _ = m._locus_rows()
    pred = sum(r["n_predicted_records"] for r in rows)
    cur = sum(r["n_curated_records"] for r in rows)
    assert (pred, cur) == (82, 41)
    assert pred + cur == 123


def test_the_locus_of_defect_is_recorded_rather_than_silently_repaired():
    """⛔ THE DEFECT THIS MODULE WORKS AROUND MUST STAY VISIBLE.

    `junction_aso_locus_collapse.locus_of` truncates a definition at its first comma before looking
    for a parenthesised symbol, so `"...germ cell-less 1, spermatogenesis associated (GMCL1), mRNA"`
    never reaches the symbol and all nine GMCL1 records fall to a per-accession fallback. A raw
    `locus_of` census of this reagent therefore returns 14 pseudo-loci where 6 genes exist. This
    module resolves them and RECORDS how many it merged; if it ever stops recording that, a reader
    comparing the two counts has no way to know why they differ.
    """
    from junction_aso_locus_collapse import locus_of
    _, gap_paired = m._screen_hits()
    raw = {locus_of(h) for h in gap_paired}
    assert len(raw) == 14, "the defect this module documents is gone — re-read `gene_of`"
    assert sum(1 for x in raw if x.startswith("acc:")) == 9

    _, _, prov = m._locus_rows()
    assert prov["n_accession_fallbacks_resolved"] == 9
    assert "first comma" in prov["_why_that_last_number_matters"]

    # the discriminating observation, asserted directly so the mechanism cannot be misattributed
    defn = "Homo sapiens germ cell-less 1, spermatogenesis associated (GMCL1), mRNA"
    entry = {"defn": defn, "acc": "NM_178439"}
    assert locus_of(entry).startswith("acc:")
    assert m.gene_of(entry) == ("GMCL1", "full_definition_second_pass")
    # and a definition WITHOUT a comma before the symbol is untouched by the second pass
    ok = {"defn": "Homo sapiens carbohydrate sulfotransferase 5 (CHST5), mRNA", "acc": "NM_024533"}
    assert m.gene_of(ok) == ("CHST5", "locus_of")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The guards
# ─────────────────────────────────────────────────────────────────────────────────────────────

def test_the_selftest_passes_offline():
    """The module's own pre-fetch gate. It asserts the control gate and the absence rule."""
    assert m.selftest() == 0


def test_an_unread_arm_can_never_become_a_biological_statement():
    """⛔ THE FAILURE CLAUDE.md §4 NAMES. A locus with no reference row must read as `readable:
    false` with a reason, never as a zero and never as 'not expressed'."""
    art = m.derive(m._empty_inputs())
    for p in art["per_locus"]:
        exp = p["exposure_compartment_liver_kidney"]
        assert exp["readable"] is False
        assert exp["values"] is None
        assert "reason" in exp
        assert p["tier"] in ("NOT_MEASURED", "NOT_MEASURABLE_UNCHARACTERISED")
    s = art["summary"]
    assert s["loci_expressed_in_an_exposure_organ"] == []
    assert len(s["loci_whose_exposure_question_is_unanswerable_from_public_data"]) == 6


def test_a_failed_known_answer_control_withholds_every_locus_verdict():
    """⛔ A COLUMN SHIFT IN A WIDE MATRIX IS INVISIBLE IN THE NUMBERS AND FATAL TO ALL OF THEM.
    A run whose controls land in the wrong tissue must emit no exposure figure at all."""
    bad = m._empty_inputs()
    bad["arm_a_gtex"] = {
        "_status": "read",
        "tissues": ["Liver", "Kidney - Cortex"],
        "rows": {"ALB": [{"gencode_id": "x", "symbol": "ALB", "values": [1.0, 900.0]}],
                 "ANKS1B": [{"gencode_id": "y", "symbol": "ANKS1B", "values": [500.0, 500.0]}]},
    }
    art = m.derive(bad)
    assert art["method"]["known_answer_controls"]["passed"] is False
    for p in art["per_locus"]:
        assert p["tier"] == "NOT_MEASURED"
        assert p["exposure_compartment_liver_kidney"]["readable"] is False
        assert "withheld" in p["exposure_compartment_liver_kidney"]["reason"]


def test_the_two_compartments_are_never_merged():
    """⭐ THE SPLIT IS THE ANSWER. A liver figure and a soft-tissue figure answer different
    questions, and an artifact that averaged them would destroy both."""
    art = m.derive(m._empty_inputs())
    assert m.EXPOSURE_TISSUES == ["Liver", "Kidney - Cortex", "Kidney - Medulla"]
    assert not set(m.EXPOSURE_TISSUES) & set(m.TUMOUR_COMPARTMENT_PROXY_TISSUES)
    for p in art["per_locus"]:
        assert p["exposure_compartment_liver_kidney"]["block"] == "exposure_liver_kidney"
        assert (p["tumour_compartment_normal_tissue_proxy"]["block"]
                == "tumour_compartment_normal_tissue_proxy")
        assert "tumour_compartment_emc_tumours" in p


def test_the_soft_tissue_block_is_labelled_a_proxy_and_not_a_tumour_reading():
    """GTEx contains no EMC and no sarcoma. An artifact that let the proxy read as the tumour would
    be reporting normal tissue as disease tissue."""
    art = m.derive(m._empty_inputs())
    why = art["method"]["_why_a_proxy"]
    assert "no reference expression atlas contains that tumour" in why.lower()
    assert any("Not a tumour measurement where it says proxy" in s
               for s in art["_what_this_is_not"])


def test_the_record_count_is_never_presented_as_risk():
    """ANKS1B and ZNF667 carry 104 of 123 records between them. That is RefSeq annotation depth."""
    art = m.derive(m._empty_inputs())
    for p in art["per_locus"]:
        note = p["screen_records"]["⚠_record_count_is_annotation_depth"]
        assert "not expression" in note and "not risk" in note
    assert any("annotation depth" in s for s in art["_what_this_is_not"])
    # and the ordering of per_locus is by record count, so the note must sit on every row
    counts = [p["screen_records"]["n_transcript_records"] for p in art["per_locus"]]
    assert counts == sorted(counts, reverse=True)


def test_the_framing_forbids_the_four_claims_the_language_rules_forbid():
    """CLAUDE.md §1: never imply selectivity, efficacy, safety, a therapeutic window or clinical
    readiness. The artifact states the refusal itself so a reader quoting it carries the limit."""
    art = m.derive(m._empty_inputs())
    f = art["_framing"].upper()
    for word in ("EFFICACY", "SELECTIVITY", "SAFETY", "THERAPEUTIC-WINDOW", "CLINICAL-READINESS"):
        assert word in f
    assert "NECESSARY" in f and "never a sufficient one" in art["_framing"]
    assert "two mismatches" in art["_framing"]


def test_the_present_cut_is_stated_as_a_choice_not_a_measurement():
    art = m.derive(m._empty_inputs())
    assert art["method"]["present_tpm_cut"] == m.PRESENT_TPM
    assert any("STATED legibility cut" in s for s in art["_what_this_is_not"])


def test_a_truncated_screen_is_refused_rather_than_censused():
    """⛔ A LOCUS CENSUS OVER A TRUNCATED HIT LIST IS A LOWER BOUND WEARING THE COSTUME OF A COUNT.

    ⚠ AND THE REAGENT ITSELF CANNOT EXERCISE THIS GUARD, WHICH IS WHY A SIBLING IS USED. At the
    default depth `GGGCATATCATCAAAC` returned 9 near-matches and stored all 9, so pointing this
    test at the reagent skips — a guard that never runs is worth nothing. Its neighbours on the
    same seam ARE truncated (`junction_aso_offtarget` stores `ranked[:15]` while reporting the full
    count), so the refusal is exercised against one of those, on the same committed file.
    """
    shallow = os.path.join(MOD, "junction-aso-offtarget-e12n3.json")
    if not os.path.exists(shallow):
        pytest.skip("the default-depth screen is not present in this checkout")
    d = json.load(open(shallow, encoding="utf-8"))
    truncated = [o["antisense_5to3"] for o in d.get("oligos", [])
                 if len(o.get("offtargets") or []) != o.get("n_offtarget_near_matches")]
    assert truncated, "no oligo in the default-depth screen is truncated — re-read the guard"
    with pytest.raises(RuntimeError, match="truncated"):
        m._screen_hits(path=shallow, reagent=truncated[0])
    # and the reagent's own default-depth record is NOT truncated, so it is accepted there too
    _, gap_paired = m._screen_hits(path=shallow, reagent=m.REAGENT)
    assert len(gap_paired) == 5, (
        "the shallow screen's gap-spanning count for the reagent moved; the manuscript quotes it")


def test_the_artifact_reproduces_from_its_committed_inputs():
    """`--check` is the artifact's own reproduction test; a stale artifact fails here."""
    _art()
    assert m.main(["--check"]) == 0, "the artifact is stale; re-run the script"
