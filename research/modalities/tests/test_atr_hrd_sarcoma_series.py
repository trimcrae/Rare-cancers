"""Offline tests for the GSE299349 characterisation.

The derive half must be exercisable with NO network, because the fetch half only runs in CI and a
broken derive would otherwise be discovered after the fetch had already spent its time.

The two things worth pinning are the two ways this module could lie:
  1. a short token matching inside a longer word ("emc" in "chemical", "atm" in "treatment"),
     which would fabricate an EMC sample out of a growth protocol;
  2. a missing document being reported as a negative answer rather than as CANNOT_DETERMINE.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import atr_hrd_sarcoma_series as M  # noqa: E402


SOFT = """^SERIES = GSE000000
!Series_title = Targeting FOO in bar with baz
!Series_summary = We treated cells and measured chemical stuff.
!Series_overall_design = Two arms.
!Series_platform_id = GPL11154
!Series_sample_id = GSM1
!Series_sample_id = GSM2
^PLATFORM = GPL11154
!Platform_title = Illumina HiSeq 2000 (Homo sapiens)
!Platform_technology = high-throughput sequencing
!Platform_organism = Homo sapiens
^SAMPLE = GSM1
!Sample_title = Line A, chemical treatment
!Sample_source_name_ch1 = osteosarcoma cell line
!Sample_growth_protocol_ch1 = Cells grown in DMEM; chemical reagents from the third supplier.
!Sample_characteristics_ch1 = treatment: DMSO
!Sample_type = SRA
!Sample_library_strategy = RNA-Seq
^SAMPLE = GSM2
!Sample_title = Line B, ceralasertib 1 uM
!Sample_source_name_ch1 = extraskeletal myxoid chondrosarcoma tumour
!Sample_characteristics_ch1 = fusion: EWSR1-NR4A3
!Sample_characteristics_ch1 = treatment: ceralasertib (AZD6738), viability measured
!Sample_type = SRA
!Sample_library_strategy = RNA-Seq
"""


def _inp(**over):
    d = {
        "series": "GSE000000",
        "fetched_utc": "2026-01-01T00:00:00Z",
        "fetches": {},
        "soft_all_brief": SOFT,
        "ftp_matrix_listing": '<a href="GSE000000_series_matrix.txt.gz">m</a>',
        "ftp_suppl_listing": '<a href="GSE000000_counts.csv.gz">c</a>',
        "series_pmids": [],
    }
    d.update(over)
    return d


def test_short_tokens_do_not_match_inside_words():
    """'emc' inside 'chemical' and 'atm' inside 'treatment' must not create a hit. GSM1 has both
    words and no real EMC/ATM content; GSM2 is the real one."""
    r = M.derive(_inp())
    q2 = r["q2_emc_or_nr4a3_sample"]
    assert q2["answer"] == "EMC_OR_NR4A3_SAMPLE_PRESENT"
    assert q2["samples_with_a_strong_EMC_or_NR4A3_term"] == ["GSM2"]
    assert "GSM1" not in q2["samples_with_any_EMC_token"], (
        "'chemical' must not register as an EMC sample")
    hrd_samples = r["q3_selection_biomarker"]["samples_with_an_HRD_term"]
    assert "GSM1" not in hrd_samples, "'treatment' must not register as an ATM/HRD term"


def test_sample_level_parse_and_counts():
    r = M.derive(_inp())
    assert r["readable"] is True
    assert r["n_samples_parsed"] == 2
    accs = [s["accession"] for s in r["samples"]]
    assert accs == ["GSM1", "GSM2"]
    # repeated SOFT keys must all survive
    g2 = [s for s in r["samples"] if s["accession"] == "GSM2"][0]
    assert len(g2["characteristics"]) == 2
    assert r["processed_matrix"]["state"] == "PROCESSED_MATRIX_PRESENT"


def test_atri_and_fet_detection():
    r = M.derive(_inp())
    q1 = r["q1_atr_inhibitor_response_data"]
    assert q1["samples_naming_an_ATR_inhibitor"] == ["GSM2"]
    assert r["fet_fusion_status_recoverable"]["answer"] == "FUSION_TERMS_PRESENT_IN_SAMPLE_METADATA"


def test_missing_document_is_cannot_determine_not_a_negative():
    """The whole point of CLAUDE.md §4: an absent reading is not a reading of absence."""
    r = M.derive(_inp(soft_all_brief=None))
    assert r["readable"] is False
    assert r["verdict"] == "SERIES_METADATA_NOT_READABLE"
    for q in ("q1_atr_inhibitor_response_data", "q2_emc_or_nr4a3_sample", "q3_selection_biomarker"):
        assert r[q]["answer"] == "CANNOT_DETERMINE"


def test_unreadable_ftp_listings_do_not_become_no_matrix():
    r = M.derive(_inp(ftp_matrix_listing=None, ftp_suppl_listing=None))
    assert r["processed_matrix"]["state"] == "CANNOT_DETERMINE"


def test_derive_is_json_serialisable():
    json.dumps(M.derive(_inp()), sort_keys=True)
