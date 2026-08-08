#!/usr/bin/env python3
"""Offline tests for `emc_cohort_search.py`.

The search half needs a network and is not tested here. What IS tested is the half that decides,
because that is the half that can be wrong quietly: a re-deposit of a cohort the manuscript already
reads looks exactly like a fourth cohort, and counting one would inflate the paper's n while every
number in it stayed arithmetically correct.

Three dedup levels and one refusal are pinned below. The refusal is the one that was actually
missing on the first pass -- a series with no sample-level read was being graded NEW.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import emc_cohort_search as M  # noqa: E402


def _series(acc, title="Some sarcoma expression panel", summary="", pubmed=None,
            n_samples="40", entrytype="GSE", parent=None):
    return {"accession": acc, "title": title, "summary": summary, "gdsType": "Expression profiling",
            "taxon": "Homo sapiens", "n_samples": n_samples, "gpl": "GPL570",
            "pubmed": pubmed or [], "entrytype": entrytype, "parent_gse": parent,
            "_found_by": "test"}


def _samples(*titles, start=900000):
    return {"n_gsm_read": len(titles),
            "samples": [{"gsm": f"GSM{start + i}", "title": t, "summary": ""}
                        for i, t in enumerate(titles)]}


def _inp(series, series_samples=None):
    return {"_generated_utc": "2026-01-01T00:00:00Z",
            "queries": [{"term": t, "why": w, "_status": "read", "count_reported_by_geo": 0,
                         "n_ids_returned": 0} for t, w in M.GEO_QUERIES],
            "series": {s["accession"]: s for s in series},
            "series_samples": series_samples or {}}


EMC_TITLES = ("Extraskeletal myxoid chondrosarcoma 1", "Extraskeletal myxoid chondrosarcoma 2",
              "Extraskeletal myxoid chondrosarcoma 3", "Leiomyosarcoma 1", "Leiomyosarcoma 2")


# =================================================================================================
# The three dedup levels
# =================================================================================================
def test_an_accession_already_used_by_the_manuscript_is_excluded():
    res = M.derive(_inp([_series("GSE24369", title="Extraskeletal myxoid chondrosarcoma profiles")],
                        {"GSE24369": _samples(*EMC_TITLES)}))
    c = res["candidates"]["GSE24369"]
    assert c["grade"] == "EXCLUDED"
    assert any("accession already used" in r for r in c["excluded_because"])


def test_a_shared_primary_publication_excludes_even_under_a_new_accession():
    """GSE170983 in one line: a different accession, the same paper, the same tumours."""
    res = M.derive(_inp(
        [_series("GSE999001", title="Transcriptional profiling of lncRNAs across archived cancers, "
                                    "including myxoid chondrosarcoma", pubmed=["22929540"])],
        {"GSE999001": _samples(*EMC_TITLES, start=990000)}))
    c = res["candidates"]["GSE999001"]
    assert c["grade"] == "EXCLUDED"
    assert any("shares a primary publication" in r for r in c["excluded_because"])
    assert res["verdict"]["new_fourth_cohorts"] == []


def test_sample_overlap_excludes_a_redeposit_that_shares_neither_accession_nor_pmid():
    """The last line of defence, and the only one that survives a depositor changing both.

    Built from the REAL GSMs of the Brunner deposit, so it fails if `_known_gsms` ever stops
    covering the 3SEQ arm -- which is the arm a re-deposit would most plausibly duplicate.
    """
    samp = {"n_gsm_read": 4,
            "samples": [{"gsm": g, "title": "Extraskeletal myxoid chondrosarcoma", "summary": ""}
                        for g in ("GSM715466", "GSM715467", "GSM715470", "GSM715472")]}
    res = M.derive(_inp([_series("GSE999002", title="Myxoid chondrosarcoma 3SEQ, re-deposited",
                                 pubmed=["99999999"])],
                        {"GSE999002": samp}))
    c = res["candidates"]["GSE999002"]
    assert c["grade"] == "EXCLUDED"
    assert c["n_gsm_overlapping_a_known_cohort"] == 4
    assert any("already read by an existing cohort" in r for r in c["excluded_because"])


def test_a_curated_GDS_view_of_a_known_series_is_excluded_by_its_parent():
    """`db=gds` returns DataSet records beside the series they are built from, under their own
    accession. Without the parent check a GDS assembled from GSE4303 reads as a new deposit."""
    res = M.derive(_inp(
        [_series("GDS1234", title="Myxoid chondrosarcoma vs other sarcomas",
                 entrytype="GDS", parent="GSE4303")],
        {"GDS1234": _samples(*EMC_TITLES, start=980000)}))
    c = res["candidates"]["GDS1234"]
    assert c["grade"] == "EXCLUDED"
    assert any("curated view of GSE4303" in r for r in c["excluded_because"])


# =================================================================================================
# The refusal
# =================================================================================================
def test_a_single_GSM_record_is_never_a_cohort_and_is_named_to_its_owner():
    """`db=gds` returns individual SAMPLE records as top-level hits. The first real run graded ten
    of them as candidates -- six being GSE24369's own EMC samples, sitting in the ungraded list
    while `_known_gsms` held every one of their accessions. A sample is not a cohort, and burying
    the one record that needed a decision under ten that never could is its own failure."""
    res = M.derive(_inp([_series("GSM600934", title="Extraskeletal myxoid chondrosarcoma 1",
                                 entrytype="GSM", n_samples="")]))
    c = res["candidates"]["GSM600934"]
    assert c["grade"] == "EXCLUDED"
    why = " ".join(c["excluded_because"])
    assert "not a cohort" in why
    assert "GSE24369" in why, "a sample of a cohort already read must say which cohort"


def test_a_platform_record_is_not_a_deposit():
    res = M.derive(_inp([_series("GPL570", title="[HG-U133_Plus_2] Affymetrix Human Genome U133",
                                 entrytype="GPL", n_samples="177506")]))
    assert res["candidates"]["GPL570"]["grade"] == "EXCLUDED"
    assert any("platform record" in r for r in res["candidates"]["GPL570"]["excluded_because"])


def test_a_known_non_cohort_dataset_is_excluded_by_name_not_by_the_floor():
    """GSE11185 is 293 cells carrying a tet-inducible EWS/NOR1 construct. "2 of its 4 samples name
    EMC" is true and tells a reader nothing; the record type is the fact that matters."""
    res = M.derive(_inp(
        [_series("GSE11185", title="Differences between NOR1 and EWS/NOR1", n_samples="4")],
        {"GSE11185": _samples("293-tet-On-EWS/NOR1 without doxycycline",
                              "293-tet-On-EWS/NOR1 with doxycycline", start=281777)}))
    why = " ".join(res["candidates"]["GSE11185"]["excluded_because"])
    assert "CELL-LINE" in why and "not an EMC tumour cohort" in why
    assert "gse11185_wt_vs_fusion" in why, "say where it is already read"


# =================================================================================================
# The positive control
# =================================================================================================
def test_the_negative_is_withheld_if_the_queries_miss_a_cohort_the_manuscript_already_reads():
    """"No fourth cohort exists" and "this search is broken" produce the same empty list. The only
    thing that separates them is whether the same queries recover the cohorts that DO exist."""
    res = M.derive(_inp([_series("GSE24369", title="LGFMS profiling")]))
    pc = res["positive_control"]
    assert pc["passes"] is False
    assert set(pc["not_recovered"]) == {"GSE4303", "GSE28866"}
    assert res["verdict"]["positive_control_passes"] is False
    assert res["verdict"]["headline"].startswith("WITHHELD"), res["verdict"]["headline"]
    assert "uninterpretable" in res["verdict"]["headline"]


def test_the_positive_control_passes_when_all_three_cohorts_come_back():
    res = M.derive(_inp([_series(a, title=f"{a} record") for a in M.POSITIVE_CONTROLS]))
    assert res["positive_control"]["passes"] is True
    assert res["verdict"]["headline"].startswith("No fourth EMC expression cohort was found")
    assert res["positive_control"]["recovered_by_these_queries"] == M.POSITIVE_CONTROLS


def test_recovery_and_exclusion_are_both_required_of_a_positive_control():
    """Recovery proves the queries reach EMC deposits; exclusion proves the guard recognises what
    is already used. A control that was recovered and then COUNTED would be the worst outcome."""
    res = M.derive(_inp([_series(a, title=f"{a} record") for a in M.POSITIVE_CONTROLS]))
    for a in M.POSITIVE_CONTROLS:
        assert res["candidates"][a]["grade"] == "EXCLUDED"
    assert res["verdict"]["new_fourth_cohorts"] == []


def test_a_series_with_no_sample_level_read_is_ungraded_and_never_new():
    """The defect this test exists for: an accession that is new, a PMID that is new and NO sample
    evidence at all was scoring as a clean pass. An absent reading is not a reading of absence."""
    res = M.derive(_inp([_series("GSE999003",
                                 title="Extraskeletal myxoid chondrosarcoma, expression")]))
    c = res["candidates"]["GSE999003"]
    assert c["grade"] == "UNGRADED_NO_SAMPLE_LEVEL_READ"
    assert c["is_new_fourth_cohort"] is False
    assert c["n_samples_naming_emc"] is None, "an unread count must not render as a number"
    assert res["verdict"]["ungraded_no_sample_level_read"] == ["GSE999003"]
    assert "⚠ incomplete" in res["verdict"], (
        "an ungraded series must be visible in the verdict; a headline that silently omits it is "
        "the failure mode this whole module is built against")


def test_an_ungraded_series_is_not_counted_as_a_fourth_cohort_anywhere():
    res = M.derive(_inp([_series(a, title=f"{a} record") for a in M.POSITIVE_CONTROLS] +
                        [_series("GSE999003", title="Myxoid chondrosarcoma expression")]))
    assert res["verdict"]["new_fourth_cohorts"] == []
    assert "No fourth EMC expression cohort was found" in res["verdict"]["headline"]
    assert res["verdict"]["ungraded_no_sample_level_read"] == ["GSE999003"]


def test_a_generically_titled_sarcoma_deposit_is_read_at_sample_level_before_being_dismissed():
    """The case the module exists to not miss, and the first real run showed the first version
    would have. GEO returned `GSE43632` ("Large scale screening for fusion genes in sarcoma patient
    samples") from a query naming EWSR1/NR4A3 -- so GEO matched it on something -- while the title
    and the captured summary name no EMC token. Dismissing it on prose alone would have been an
    artifact of a 1200-character truncation, in exactly the "EMC hiding in a pan-sarcoma deposit"
    case the docstring warns about. A sample-level read must be able to overrule the prose screen.
    """
    samp = _samples("Extraskeletal myxoid chondrosarcoma 1", "Extraskeletal myxoid chondrosarcoma 2",
                    "Extraskeletal myxoid chondrosarcoma 3", "Synovial sarcoma 1", start=950000)
    res = M.derive(_inp(
        [_series(a, title=f"{a} record") for a in M.POSITIVE_CONTROLS] +
        [_series("GSE999006", title="Large scale screening for fusion genes in sarcoma",
                 summary="Fusion gene screening across sarcoma patient samples.", pubmed=["40000001"])],
        {"GSE999006": samp}))
    c = res["candidates"]["GSE999006"]
    assert c["names_emc_in_prose"] is False, "the premise of the test is a generic title"
    assert c["grade"] == "NEW_CANDIDATE", c["excluded_because"]
    assert res["verdict"]["new_fourth_cohorts"] == ["GSE999006"]


# =================================================================================================
# The floor, and what actually counts as a hit
# =================================================================================================
def test_the_sample_level_token_set_refuses_a_bare_gene_mention():
    """Fail-open direction. A pan-sarcoma deposit annotating every sample `NR4A3 status: negative`
    would score every sample as EMC under the prose token set, and qualify on n alone."""
    assert M.EMC_TOKENS.search("NR4A3 status: negative"), "prose screen should stay broad"
    assert not M.EMC_SAMPLE_TOKENS.search("NR4A3 status: negative")
    assert not M.EMC_SAMPLE_TOKENS.search("NOR-1 immunohistochemistry")
    # Both cohorts already in the paper must still be recognised by their real sample titles.
    assert M.EMC_SAMPLE_TOKENS.search("Extraskeletal myxoid chondrosarcoma 1")
    assert M.EMC_SAMPLE_TOKENS.search("STT3699-Myxoid Chondrosarcoma")


def test_two_emc_samples_do_not_clear_the_floor():
    res = M.derive(_inp(
        [_series("GSE999004", title="Sarcoma panel including myxoid chondrosarcoma")],
        {"GSE999004": _samples("Extraskeletal myxoid chondrosarcoma 1",
                               "Extraskeletal myxoid chondrosarcoma 2",
                               "Leiomyosarcoma 1", "Leiomyosarcoma 2", start=970000)}))
    c = res["candidates"]["GSE999004"]
    assert c["grade"] == "EXCLUDED"
    assert c["n_samples_naming_emc"] == 2
    assert any(f"floor is {M.MIN_EMC_SAMPLES}" in r for r in c["excluded_because"])


def test_a_genuinely_new_series_with_enough_emc_samples_is_reported_as_a_candidate():
    """The module must be able to say yes, or a null result from it means nothing."""
    res = M.derive(_inp(
        [_series("GSE999005", title="Extraskeletal myxoid chondrosarcoma versus other sarcomas",
                 pubmed=["40000000"])],
        {"GSE999005": _samples(*EMC_TITLES, start=960000)}))
    c = res["candidates"]["GSE999005"]
    assert c["grade"] == "NEW_CANDIDATE", c["excluded_because"]
    assert c["n_samples_naming_emc"] == 3
    assert res["verdict"]["new_fourth_cohorts"] == ["GSE999005"]
    assert "survived every dedup check" in res["verdict"]["headline"]
    assert "characterising at sample level" in res["verdict"]["headline"], (
        "a surviving candidate is a lead, not a cohort -- the headline must not promote it")


# =================================================================================================
# Bookkeeping that the negative depends on
# =================================================================================================
def test_the_known_gsm_map_covers_all_three_cohorts_the_manuscript_reads():
    """If this map ever silently empties, every overlap check passes and the guard is gone."""
    k = M._known_gsms()
    assert len(k) > 150, len(k)
    assert k.get("GSM600934") == "GSE24369"           # EMC 1, GPL6244 arm
    assert k.get("GSM98495") == "GSE4303"             # STT3699, GPL3290 arm
    assert "GSE170983" in (k.get("GSM715466") or ""), "the 3SEQ arm must map to BOTH accessions"


def test_every_query_is_recorded_including_the_ones_that_return_nothing():
    res = M.derive(_inp([]))
    assert res["query_summary"]["n_queries"] == len(M.GEO_QUERIES)
    assert res["query_summary"]["n_read"] == len(M.GEO_QUERIES)
    assert len(res["queries"]) == len(M.GEO_QUERIES)
    for q in res["queries"]:
        assert q["why"], "a query with no stated reason cannot be graded by a reader"


def test_a_failed_query_is_counted_as_failed_not_as_empty():
    """A 403 and a genuine zero are the same length. They must not read the same."""
    inp = _inp([])
    inp["queries"][0] = {"term": M.GEO_QUERIES[0][0], "why": M.GEO_QUERIES[0][1],
                         "_status": "failed", "error": "HTTPError: 403"}
    res = M.derive(inp)
    assert res["query_summary"]["n_failed"] == 1
    assert res["query_summary"]["n_read"] == len(M.GEO_QUERIES) - 1


def test_the_scope_disclaimer_travels_with_the_verdict():
    """The negative this module most likely returns is bounded, and the bound has to be attached to
    the verdict rather than left in a docstring nobody reads."""
    res = M.derive(_inp([]))
    scope = res["verdict"]["⛔ scope"]
    assert "DEPOSITOR PROSE" in scope
    assert "NOT a statement that no fourth cohort exists" in scope


def test_the_known_cohort_table_names_the_redeposit_as_a_trap_not_as_a_cohort():
    assert set(M.KNOWN_COHORTS) == {"GSE24369", "GSE4303", "GSE28866", "GSE170983"}
    assert "NOT a fourth cohort" in M.KNOWN_COHORTS["GSE170983"]
    assert "22929540" in M.KNOWN_COHORTS["GSE170983"]
    assert "22929540" in M.KNOWN_PMIDS


def test_the_check_diff_ignores_timestamps_only():
    """`--check` must go red on a changed verdict and stay green across a re-run minutes later."""
    a = M.derive(_inp([]))
    b = json.loads(json.dumps(a))
    b["generated_utc"] = "2099-12-31T23:59:59Z"
    assert M._strip(a) == M._strip(b)
    b["verdict"]["new_fourth_cohorts"] = ["GSE999999"]
    assert M._strip(a) != M._strip(b)


@pytest.mark.skipif(not os.path.exists(M.OUT), reason="cohort search not yet fetched")
def test_the_committed_artifact_reproduces_from_its_own_cached_inputs():
    with open(M.INPUTS) as fh:
        inp = json.load(fh)
    with open(M.OUT) as fh:
        have = json.load(fh)
    assert M._strip(M.derive(inp)) == M._strip(have), (
        "the committed verdict does not re-derive from the committed inputs; "
        "re-run emc_cohort_search.py")
