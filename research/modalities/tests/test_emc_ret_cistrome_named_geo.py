"""THE NAMED-GEO SEED — pinned so the ChIP-only blind spot and the discovery/peak-set confusion stay closed.

⛔ WHAT WENT WRONG. Every GEO query this module ran asked for ChIP. CUT&Tag and CUT&RUN are genome-wide
occupancy assays and are not ChIP, and GEO types GSE254076 (`NR4A3 CUT&Tag`, mouse VSMC) as `Other` — so
neither a DataSet-Type filter nor a ChIP-seq keyword could reach it, and the lane reported that it had
searched GEO for NR4A3 occupancy while a real NR4A3 occupancy dataset sat unretrieved. An absent reading
wearing the costume of an absence of data (CLAUDE.md §4).

⛔ AND THE SECOND HALF WAS ONE STAGE LATER. The supplementary-listing filter used the SAME ChIP-only word
list, so widening the query alone would have retrieved the accession and then discarded its file listing —
producing an artifact that looked like "we looked and there was nothing." Both halves are widened together
or neither is, and `test_the_supplementary_filter_admits_the_same_assays_the_queries_do` is why.

⚠ THIRD, AND THE ONE MOST LIKELY TO BE MISREAD: adding a series to part 1 is DISCOVERY. It does not add a
peak set to part 2 — GSE254076 serves only a `_RAW.tar` — and a discovery that cannot be intersected has to
say so in `peaksets_not_intersected_and_why`, or its absence from the intersected count reads as an
oversight rather than as the finding it is.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import emc_ret_cistrome as M  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(HERE, "emc-ret-cistrome.json")
SEEDED = "GSE254076"


def _art():
    if not os.path.exists(ART):
        pytest.skip("emc-ret-cistrome.json not committed in this tree")
    with open(ART, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_every_named_series_carries_its_own_limitation_and_its_reason_for_being_named():
    """A seeded accession with no stated limitation is how a mouse wild-type dataset comes to read
    as an answer to a human-EMC question."""
    assert M.NAMED_GEO_SERIES, "the seed table is empty"
    for acc, meta in M.NAMED_GEO_SERIES.items():
        assert acc.startswith("GSE"), acc
        assert meta.get("why_named"), f"{acc} does not say why it is named"
        lim = meta.get("⚠ limitation")
        assert lim, f"{acc} carries no limitation"
        assert len(lim) > 60, f"{acc}'s limitation is too thin to constrain a reader"
        assert meta.get("verified_from"), f"{acc} does not name the fetch that verified it"


def test_the_seeded_mouse_series_says_mouse_loudly():
    """This repository's question is HUMAN EMC. The one thing a reader must not be able to miss."""
    lim = M.NAMED_GEO_SERIES[SEEDED]["⚠ limitation"]
    assert "MOUSE" in lim
    assert "10090" in lim, "the taxid is the checkable form of 'mouse'"
    assert "NOT the EWSR1::NR4A3 fusion" in lim
    assert "mm10" in lim


def test_a_cut_and_tag_query_exists_because_every_other_query_asks_for_chip():
    terms = " ".join(t for t, _ in M.GEO_QUERIES).lower()
    assert "cut&tag" in terms or "cutandtag" in terms
    assert "cut&run" in terms or "cutandrun" in terms


def test_the_supplementary_filter_admits_the_same_assays_the_queries_do():
    """Widening the query without widening this filter retrieves the accession and throws its peak
    files away — a silent 'we looked and found nothing'. Read from the source, so the two lists
    cannot drift apart unnoticed."""
    with open(os.path.join(HERE, "emc_ret_cistrome.py"), "r", encoding="utf-8") as fh:
        src = fh.read()
    i = src.index('if not any(t in blob for t in ("chip"')
    window = src[i:i + 400]
    for token in ("cut&tag", "cut&run"):
        assert token in window, f"the supplementary-listing filter still cannot see {token}"


def test_named_series_are_fetched_by_accession_and_never_typed(monkeypatch):
    """The seed table supplies WHY and the LIMITATION. Every FACT must come from GEO."""
    calls = []

    def fake(url):
        calls.append(url)
        if "esearch" in url:
            return {"esearchresult": {"idlist": ["200254076", "308033084", "100024247"]}}
        return {"result": {"200254076": {
            "title": "T", "taxon": "Mus musculus", "n_samples": 4, "gdsType": None,
            "summary": "S", "GPL": None, "GSE": None, "PubMedIds": None,
            "FTPLink": None, "suppFile": None}}}

    monkeypatch.setattr(M, "get_json", fake)
    out = M.fetch_named_geo_series()
    assert out[SEEDED]["_status"] == "read"
    assert out[SEEDED]["title"] == "T", "a fact came from somewhere other than the esummary"
    assert out[SEEDED]["taxon"] == "Mus musculus"
    # the SERIES uid, not the sample (3…) or platform (100…) uids the same query returns
    assert any("id=200254076" in c for c in calls), "summarised the wrong uid as the series"


def test_a_failed_named_fetch_carries_no_facts(monkeypatch):
    """A hand-written stand-in for a failed fetch is the fabricated-record failure gate 4 exists for."""
    monkeypatch.setattr(M, "get_json", lambda url: None)
    out = M.fetch_named_geo_series()
    row = out[SEEDED]
    assert row["_status"] == "series_uid_not_returned"
    assert "title" not in row and "taxon" not in row


def test_the_merge_refuses_when_no_named_accession_could_be_read(tmp_path, monkeypatch):
    """An endpoint that is down and an accession that does not exist are indistinguishable here."""
    p = tmp_path / "inputs.json"
    p.write_text(json.dumps({"geo": {"series": {"GSE1": {}}}}))
    monkeypatch.setattr(M, "INPUTS", str(p))
    monkeypatch.setattr(M, "fetch_named_geo_series",
                        lambda: {SEEDED: {"_status": "esummary_failed"}})
    before = p.read_text()
    assert M.fetch_named_geo_into_cache() == 4
    assert p.read_text() == before


def test_the_merge_refuses_when_there_is_no_cache_to_merge_into(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "INPUTS", str(tmp_path / "absent.json"))
    assert M.fetch_named_geo_into_cache() == 4


def test_the_merge_refuses_a_cache_holding_no_geo_series_at_all(tmp_path, monkeypatch):
    p = tmp_path / "inputs.json"
    p.write_text(json.dumps({"geo": {"series": {}}}))
    monkeypatch.setattr(M, "INPUTS", str(p))
    assert M.fetch_named_geo_into_cache() == 4


def test_a_series_serving_no_peak_file_is_named_as_not_intersected():
    cache = {"geo_supplementary": {SEEDED: {"_status": "read", "n_files": 3,
                                            "files": ["GSE254076_RAW.tar", "filelist.txt"],
                                            "peak_like": []}}}
    rows = M._named_geo_not_intersected(cache)
    k = f"{SEEDED}:no_peak_file_served"
    assert k in rows
    assert "DISCOVERY" in rows[k]
    assert "MOUSE" in rows[k]


def test_an_unreadable_listing_is_an_absent_reading_not_a_finding():
    cache = {"geo_supplementary": {SEEDED: {"_status": "listing_failed"}}}
    rows = M._named_geo_not_intersected(cache)
    assert "ABSENT READING" in rows[f"{SEEDED}:supplementary"]


def test_a_series_that_does_serve_peaks_drops_out_of_the_not_intersected_dict():
    cache = {"geo_supplementary": {SEEDED: {"_status": "read", "n_files": 1,
                                            "files": ["x.narrowPeak.gz"],
                                            "peak_like": ["x.narrowPeak.gz"]}}}
    assert M._named_geo_not_intersected(cache) == {}


@pytest.mark.committed_artifact
def test_the_committed_artifact_carries_the_seeded_series_with_its_limitation():
    a = _art()
    s = (a["part_1_datasets"]["geo"].get("series") or {}).get(SEEDED)
    assert s, f"{SEEDED} is not in the committed artifact's GEO series"
    assert s["_status"] == "read"
    assert s["taxon"] == "Mus musculus"
    assert "MOUSE" in s["⚠ limitation"]
    assert "NAMED_GEO_SERIES" in s["_found_by"]


@pytest.mark.committed_artifact
def test_the_seeded_series_is_not_counted_among_the_intersected_peak_sets():
    """⛔ THE ONE THAT MATTERS. A mouse discovery must never inflate the peak-set count the RET
    reading is quoted from."""
    a = _art()
    p2 = a["part_2_intersection"]
    assert not any(SEEDED in k for k in p2["per_peakset"]), (
        f"{SEEDED} entered per_peakset; it serves no peak file and cannot have been intersected")
    assert any(SEEDED in k for k in p2["peaksets_not_intersected_and_why"]), (
        f"{SEEDED} is absent from per_peakset with no stated reason — which reads as an oversight")
