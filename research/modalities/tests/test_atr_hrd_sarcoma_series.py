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
!Sample_characteristics_ch1 = tissue: cells
!Sample_characteristics_ch1 = cell type: osteosarcoma
!Sample_characteristics_ch1 = treatment: DMSO
!Sample_type = SRA
!Sample_library_strategy = RNA-Seq
!Sample_supplementary_file_1 = ftp://x/GSM1_a.quant.sf.gz
^SAMPLE = GSM2
!Sample_title = Line B, ceralasertib 1 uM
!Sample_source_name_ch1 = cells
!Sample_characteristics_ch1 = tissue: cells
!Sample_characteristics_ch1 = cell type: extraskelletal myxoid chondrosarcoma
!Sample_characteristics_ch1 = fusion: EWSR1-NR4A3
!Sample_characteristics_ch1 = treatment: ceralasertib (AZD6738), viability measured
!Sample_treatment_protocol_ch1 = ceralasertib 1 uM for 24 h
!Sample_type = SRA
!Sample_library_strategy = RNA-Seq
!Sample_supplementary_file_1 = ftp://x/GSM2_b.quant.sf.gz
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
    assert q2["samples_with_a_strong_EMC_or_NR4A3_term"] == ["GSM2"], (
        "the real deposit misspells it 'extraskelletal', so the match must not depend on the "
        "full disease name being spelled correctly")
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
    assert len(g2["characteristics"]) == 4
    assert r["processed_matrix"]["state"] == "PER_SAMPLE_PROCESSED_QUANTIFICATION_FOR_EVERY_SAMPLE"


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
    """An unreadable listing must never be reported as 'raw reads only'. Two halves:
    a POSITIVE from the samples stands whatever the listing did; a NEGATIVE may only be returned
    when both halves were actually read."""
    # positive survives an unreadable listing
    r = M.derive(_inp(ftp_matrix_listing=None, ftp_suppl_listing=None))
    assert r["processed_matrix"]["state"] == "PER_SAMPLE_PROCESSED_QUANTIFICATION_FOR_EVERY_SAMPLE"
    # with no per-sample processed file AND an unreadable listing, the answer is unknown
    bare = SOFT.replace("!Sample_supplementary_file_1 = ftp://x/GSM1_a.quant.sf.gz\n", "")
    bare = bare.replace("!Sample_supplementary_file_1 = ftp://x/GSM2_b.quant.sf.gz\n", "")
    r2 = M.derive(_inp(soft_all_brief=bare, ftp_matrix_listing=None, ftp_suppl_listing=None))
    assert r2["processed_matrix"]["state"] == "CANNOT_DETERMINE"
    # and when both halves ARE readable and empty, the negative is allowed
    r3 = M.derive(_inp(soft_all_brief=bare, ftp_matrix_listing="", ftp_suppl_listing=""))
    assert r3["processed_matrix"]["state"] == "NO_PROCESSED_DATA_FOUND_RAW_READS_ONLY"


def test_cohort_composition_splits_tumours_from_cell_models():
    """`tissue: cells` + `cell type: X` is a patient-derived model; `tissue: X` is a tumour.
    On GSE299349 this is the difference between 62 tumours and 6 models, and the series'
    overall_design names only the 62 — which is why the split is computed, not inherited."""
    soft = SOFT + (
        "^SAMPLE = GSM3\n"
        "!Sample_title = a tumour\n"
        "!Sample_characteristics_ch1 = tissue: leiomyosarcoma\n"
        "!Sample_type = SRA\n")
    r = M.derive(_inp(soft_all_brief=soft))
    cc = r["cohort_composition"]
    assert cc["n_tumour_samples"] == 1
    assert cc["n_patient_derived_cell_models"] == 2
    assert cc["tumour_subtypes"] == {"leiomyosarcoma": 1}
    assert r["design_vs_contents"]["n_samples_actually_in_the_series"] == 3


def test_derive_is_json_serialisable():
    json.dumps(M.derive(_inp()), sort_keys=True)


def test_quant_parser_reads_a_plain_quant_sf():
    """Pins the bug that failed all 68 samples on run 31006439097: `_get` already gunzips a `.gz`
    URL, so a second gzip.decompress destroyed an intact file and reported `Not a gzipped file
    (b'Na')` — where `Na` is the quant.sf header. The parser must read PLAIN text, and the panel
    must aggregate every transcript of a gene rather than only the first."""
    sf = ("Name\tLength\tEffectiveLength\tTPM\tNumReads\n"
          "NM_006981.4\t3000\t2800\t120.5\t900\n"      # NR4A3
          "NM_173199.3\t3100\t2900\t30.5\t200\n"       # NR4A3, second transcript
          "NM_001101.5\t1800\t1600\t4000.0\t50000\n"   # ACTB
          "NM_000477.7\t2000\t1800\t0.0\t0\n"          # ALB
          "NM_999999.1\t1000\t800\t7.0\t10\n").encode()
    tot, nrows, first, matched = M._parse_quant_sf(sf)
    assert matched == "REFSEQ_ACCESSION"
    assert nrows == 5
    assert round(tot["NR4A3"], 1) == 151.0, "both NR4A3 transcripts must be summed"
    assert tot["ACTB"] == 4000.0 and tot.get("ALB", 0.0) == 0.0
    assert first[0] == "NM_006981.4"


def test_quant_parser_reads_a_symbol_in_name():
    sf = ("Name\tLength\tEffectiveLength\tTPM\tNumReads\n"
          "ENST00000000001.1|ENSG00000119508.1|-|-|NR4A3-201|NR4A3|3000|protein_coding|"
          "\t3000\t2800\t9.5\t80\n").encode()
    tot, _, _, matched = M._parse_quant_sf(sf)
    assert matched == "SYMBOL_IN_NAME"
    assert tot["NR4A3"] == 9.5


def test_identity_check_reports_cannot_determine_when_nothing_read():
    """An unreadable panel must never render as 'the label is not corroborated'."""
    art = M.derive(_inp())
    q = {"per_sample": {"GSM2": {"status": "FAILED after 3 tries: HTTP 500"}}}
    r = M.derive_quant(q, art)
    assert r["verdict"].startswith("CANNOT_DETERMINE")
