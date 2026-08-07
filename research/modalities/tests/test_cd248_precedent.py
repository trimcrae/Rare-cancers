"""Offline tests for the CD248 / endosialin precedent record.

⛔ WHAT IS PINNED HERE is not the literature. It is the three ways a "the binders already exist"
record turns into an over-claim, each of which this repository has committed some version of
before:

  1. **The negative trial going quiet.** The only randomised human test of a CD248-directed agent
     in soft-tissue sarcoma read out NEGATIVE. A precedent file that lists the ADC, the
     radioligand and the CAR without that trial is a sales sheet. The failed result must be
     present, and it must be present at the top of the ladder rather than buried in a footnote.
  2. **An unread corpus rendering as a finding of absence.** `emc_specific_evidence` derives
     "zero EMC papers" by reading a branch that may not exist in a given checkout. If the read
     fails, the module must say UNREAD — never zero (CLAUDE.md §4).
  3. **A citation without an identifier.** Everything clinical in this repository carries a PMID,
     PMCID or DOI; a remembered trial is exactly the kind of fact that must never be typed.
"""

import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cd248_precedent as M  # noqa: E402

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def res():
    return M.derive()


# ---------------------------------------------------------------------------------------------
# 1 — THE NEGATIVE TRIAL IS LOAD-BEARING AND CANNOT GO QUIET
# ---------------------------------------------------------------------------------------------
def test_the_randomised_phase2_negative_is_recorded_with_its_numbers(res):
    r = res["records"]["ontuxizumab_randomised_phase2_STS"]
    assert r["pmid"] == "31034598" and r["pmcid"] == "PMC6618088"
    res_fig = r["result_authors_figures"]
    # the effect sizes, not just the word "negative"
    assert "HR 1.07" in res_fig["progression_free_survival"]
    assert "HR 1.23" in res_fig["overall_survival"]
    assert "no enhanced activity" in r["authors_conclusion_verbatim"]
    assert "not warranted" in r["authors_conclusion_verbatim"]


def test_the_modality_ladder_leads_with_the_human_negative_not_the_preclinical_positives(res):
    lad = res["modality_ladder"]
    keys = [k for k in lad if not k.startswith("_")]
    assert keys[0] == "naked_antibody_in_soft_tissue_sarcoma", (
        "the tested-and-negative format must be the first rung a reader meets")
    assert "NEGATIVE" in lad["naked_antibody_in_soft_tissue_sarcoma"]
    for k in ("antibody_drug_conjugate", "radioligand_therapy", "car_t_and_t_cell_engager"):
        assert lad[k].startswith("PRECLINICAL"), k
    assert lad["anything_at_all_in_EMC"].startswith("NONE")


def test_no_efficacy_or_readiness_language_survives_anywhere_in_the_artifact(res):
    blob = json.dumps(res).lower()
    # the artifact TALKS ABOUT these words in its own refusals, so the test targets the
    # constructions that would be claims rather than the bare words
    for forbidden in ("is effective in emc", "works in emc", "is safe in emc",
                      "validated target in emc", "ready for the clinic",
                      "therapeutic window in emc"):
        assert forbidden not in blob, forbidden
    assert "NOTHING HERE IS AN EFFICACY" in res["_language_discipline"]


# ---------------------------------------------------------------------------------------------
# 2 — AN UNREAD CORPUS IS NEVER A ZERO
# ---------------------------------------------------------------------------------------------
def test_an_unreadable_corpus_reports_UNREAD_and_claims_no_count(monkeypatch):
    monkeypatch.setattr(M, "_corpus_index", lambda: (None, "⛔ CORPUS UNREAD — synthetic"))
    e = M.emc_specific_evidence()
    assert e["_status"] == "UNREAD"
    assert "n_records_mentioning_EMC" not in e
    assert "not the same as zero" in e["why"] or "not a reading of absence" in e["⛔_meaning"]


def test_a_readable_corpus_that_contains_EMC_says_so_rather_than_reporting_the_gap(monkeypatch):
    rows = [{"title": "Endosialin in extraskeletal myxoid chondrosarcoma", "abstract": "",
             "pmid": "999", "pmcid": None, "doi": None, "year": 2026},
            {"title": "Endosialin in leiomyosarcoma", "abstract": "", "pmid": "998"}]
    monkeypatch.setattr(M, "_corpus_index", lambda: (rows, None))
    e = M.emc_specific_evidence()
    assert e["_status"] == "READ"
    assert e["n_records_mentioning_EMC"] == 1
    assert e["records_mentioning_EMC"][0]["pmid"] == "999"
    assert "Records naming EMC ARE present" in e["verdict"]


def test_conventional_chondrosarcoma_alone_is_never_counted_as_EMC(monkeypatch):
    """⛔ A NAME COLLISION IS NOT EVIDENCE. EMC has no cartilaginous differentiation and is a
    different disease from conventional chondrosarcoma. A term list containing bare
    'chondrosarcoma' would turn every bone-tumour paper in the corpus into EMC evidence."""
    assert not any(re.fullmatch(r"\\?b?chondrosarcoma\\?b?", t, re.I) for t in M.EMC_TERMS)
    rows = [{"title": "Endosialin expression in conventional chondrosarcoma of bone",
             "abstract": "cartilaginous tumours", "pmid": "997"}]
    monkeypatch.setattr(M, "_corpus_index", lambda: (rows, None))
    assert M.emc_specific_evidence()["n_records_mentioning_EMC"] == 0


def test_the_chondrosarcoma_reading_in_the_corpus_carries_its_refusal(res):
    r = res["records"]["sts_ihc_n94"]
    refusal = r["⛔_this_is_NOT_an_EMC_reading"]
    assert "conventional bone chondrosarcoma" in refusal
    assert "EWSR1::NR4A3" in refusal
    assert "name collision" in refusal
    # and the quote it refuses is present, so a reader can see what is being refused
    assert "chondrosarcoma having lower expression" in r["quote"]


# ---------------------------------------------------------------------------------------------
# 3 — EVERY CLINICAL RECORD CARRIES AN IDENTIFIER
# ---------------------------------------------------------------------------------------------
def _leaf_records(obj):
    """Any dict carrying a `title` is a citation and must be identified."""
    if isinstance(obj, dict):
        if "title" in obj:
            yield obj
        for v in obj.values():
            yield from _leaf_records(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _leaf_records(v)


def test_every_cited_record_carries_a_pmid_and_a_verification_tag(res):
    n = 0
    for rec in _leaf_records(res["records"]):
        n += 1
        assert rec.get("pmid"), f"no PMID: {rec.get('title')!r}"
        assert rec.get("verification") in ("[FT]", "[API]"), rec.get("title")
    assert n >= 10, f"only {n} citations found — the record has thinned out"


def test_a_full_text_tag_is_only_used_where_a_pmcid_exists(res):
    for rec in _leaf_records(res["records"]):
        if rec.get("verification") == "[FT]":
            assert rec.get("pmcid"), (
                f"{rec.get('title')!r} claims full text but records no PMCID — [FT] means the "
                f"open-access text was retrieved, and without a PMCID it could not have been")


def test_the_review_without_open_access_is_marked_as_abstract_only(res):
    r = res["records"]["review_2026"]
    assert r["pmcid"] is None
    assert r["verification"] == "[API]"
    assert "abstract only" in r["⚠_not_open_access"].lower()
    assert "no pmcid" in r["⚠_not_open_access"].lower()
    assert "settles anything" in r["⚠_a_review_claim_is_not_a_measurement"].lower()


# ---------------------------------------------------------------------------------------------
# 4 — THE DEPMAP NUMBERS ARE POINTED AT, NOT COPIED (CLAUDE.md §1)
# ---------------------------------------------------------------------------------------------
def test_the_surfaceome_scan_numbers_are_referenced_and_not_re_typed(res):
    inst = res["instrument_that_flagged_it"]
    assert "surfaceome-instrument-limits.json" in inst["one_home_of_its_CD248_numbers"]
    blob = json.dumps(res)
    for figure in ("2.29", "0.44", "3.01"):
        assert figure not in blob, (
            f"{figure} is a DepMap surfaceome number with a home elsewhere; point at it, "
            f"do not copy it")


@pytest.mark.committed_artifact
def test_the_home_it_points_at_actually_holds_the_CD248_row():
    path = os.path.join(MOD, "surfaceome-instrument-limits.json")
    if not os.path.exists(path):
        pytest.skip("surfaceome-instrument-limits.json is not present in this checkout")
    d = json.load(open(path))
    row = d["limits"]["L2_stromal_floor_demonstrated"]["genes"]["CD248"]
    assert row["selectivity_significant"] is True
    assert row["enrichment_vs_rest"] > 0


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
