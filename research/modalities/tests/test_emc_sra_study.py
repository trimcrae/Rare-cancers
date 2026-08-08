"""`emc_sra_study.py` must never turn a transport failure into a finding.

⛔ WHY THIS FILE EXISTS. The module's whole output is a verdict about whether an accession exists,
and the two ways of getting that wrong are not symmetric. Saying "it does not exist" when the proxy
403'd would retire the highest-value lead on the board — `BLK-NO-EMC-DATA` holds more routes than
any other blocker in the portfolio. Saying "it exists" from a loose matcher would put a phantom
cohort into the graph. So the control gate is tested in BOTH directions, and the module's own
`selftest()` is run here as well so the offline invariants can never be skipped into silence by a
CI mode that forgets to call it.

⚠ NOTHING HERE MOCKS THE FUNCTION UNDER TEST. CLAUDE.md §6 records a guard that no-opped into the
previous behaviour and passed every test because every test monkeypatched the seam. These build
synthetic PAYLOADS — the same shape the archives return — and run the real `derive()` over them.
"""

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import emc_sra_study as M  # noqa: E402


def _es(key, count):
    return {"key": key, "_status": "read",
            "json": {"esearchresult": {"count": str(count),
                                       "idlist": [str(i) for i in range(count)]}}}


def _ena(key, rows):
    head = M.ENA_RUN_FIELDS
    body = "\t".join(head) + "\n" + "\n".join(
        "\t".join(str(r.get(h, "")) for h in head) for r in rows)
    return {"key": key, "_status": "read", "body": body}


def _controls(broken=None):
    """Every control answering as expected, except any named in `broken`."""
    out = []
    for key, c in M.CONTROLS.items():
        if key in (broken or {}):
            n = broken[key]
        else:
            n = 0 if c["expect"] == "zero" else 1
        out += [_es(f"{key}_bioproject_esearch", n), _es(f"{key}_sra_esearch", n),
                _ena(f"{key}_ena_read_run", [{"run_accession": "SRR1"}] * n)]
    return out


def _inputs(fetches):
    return {"target_bioproject": M.TARGET_BIOPROJECT,
            "target_sra_study": M.TARGET_SRA_STUDY, "fetches": fetches}


def test_the_modules_own_selftest_passes():
    assert M.selftest() is True


def test_a_clean_absence_is_reported_as_an_absence():
    r = M.derive(_inputs(_controls() +
                         [_es(f"tgt_{M.TARGET_BIOPROJECT}_bioproject_esearch", 0),
                          _es(f"tgt_{M.TARGET_SRA_STUDY}_sra_esearch", 0)]))
    assert r["verdict"]["grade"] == "NOT_FOUND"
    assert r["transport_gate_passed"] is True


@pytest.mark.parametrize("broken", [
    {"ctrl_real_bioproject": 0},        # a known-real record went dark
    {"ctrl_real_sra_study": 0},         # the other known-real record went dark
    {"ctrl_absent": 4},                 # a record that cannot exist came back populated
])
def test_a_failed_control_forbids_the_absence_verdict(broken):
    """⛔ THE ONE THAT MATTERS. Identical invisible target; only the controls differ."""
    r = M.derive(_inputs(_controls(broken) +
                         [_es(f"tgt_{M.TARGET_BIOPROJECT}_bioproject_esearch", 0)]))
    assert r["verdict"]["grade"] == "UNREADABLE_TRANSPORT", (
        "a zero from a search that could not reach the archive was reported as an absence")
    assert list(broken)[0] in r["verdict"]["controls_failed"]
    assert r["transport_gate_passed"] is False


def test_run_count_never_leaks_into_sample_count():
    """12 runs is not 12 patients — six samples sequenced twice must read as six."""
    rows = [{"run_accession": f"SRR{i}", "sample_accession": f"SAMN{i // 2}",
             "experiment_accession": f"SRX{i}", "study_accession": M.TARGET_BIOPROJECT,
             "sample_title": "extraskeletal myxoid chondrosarcoma case",
             "fastq_ftp": f"f{i}.gz", "fastq_bytes": "10"} for i in range(12)]
    r = M.derive(_inputs(_controls() +
                         [_es(f"tgt_{M.TARGET_BIOPROJECT}_bioproject_esearch", 1),
                          _ena(f"tgt_{M.TARGET_BIOPROJECT}_ena_read_run", rows)]))
    v = r["verdict"]
    assert v["n_runs_measured"] == 12
    assert v["n_distinct_samples_measured"] == 6


def test_metadata_without_files_is_not_public_data():
    """An embargoed deposit looks exactly like a public one until the file list is read."""
    rows = [{"run_accession": f"SRR{i}", "sample_accession": f"SAMN{i}",
             "study_accession": M.TARGET_BIOPROJECT,
             "sample_title": "extraskeletal myxoid chondrosarcoma",
             "fastq_ftp": "", "fastq_bytes": ""} for i in range(12)]
    r = M.derive(_inputs(_controls() +
                         [_es(f"tgt_{M.TARGET_BIOPROJECT}_bioproject_esearch", 1),
                          _ena(f"tgt_{M.TARGET_BIOPROJECT}_ena_read_run", rows)]))
    assert r["verdict"]["grade"] == "EMC_BUT_DATA_NOT_PUBLIC"
    assert r["targets"][M.TARGET_BIOPROJECT]["data_availability"]["state"] == \
        "REGISTERED_METADATA_ONLY"


def test_a_resolved_record_that_never_names_emc_is_not_a_cohort():
    rows = [{"run_accession": f"SRR{i}", "sample_accession": f"SAMN{i}",
             "study_accession": M.TARGET_BIOPROJECT, "sample_title": "normal liver",
             "fastq_ftp": f"f{i}.gz", "fastq_bytes": "10"} for i in range(12)]
    r = M.derive(_inputs(_controls() +
                         [_es(f"tgt_{M.TARGET_BIOPROJECT}_bioproject_esearch", 1),
                          _ena(f"tgt_{M.TARGET_BIOPROJECT}_ena_read_run", rows)]))
    assert r["verdict"]["grade"] == "RESOLVED_NOT_EMC"


def test_study_prose_alone_can_never_promote_a_lead_to_a_cohort():
    """An absent sample-level read is UNGRADED, never a clean pass — the §4 failure."""
    r = M.derive(_inputs(_controls() + [
        _es(f"tgt_{M.TARGET_BIOPROJECT}_bioproject_esearch", 1),
        {"key": f"tgt_{M.TARGET_BIOPROJECT}_bioproject_esummary", "_status": "read",
         "json": {"result": {"uids": ["1"], "1": {
             "project_acc": M.TARGET_BIOPROJECT,
             "project_title": "extraskeletal myxoid chondrosarcoma cohort"}}}}]))
    assert r["verdict"]["grade"] == "UNGRADED_NO_SAMPLE_LEVEL_READ"
    assert r["targets"][M.TARGET_BIOPROJECT]["emc_evidence"]["n_sample_blobs_read"] == 0


def test_the_strict_sample_token_set_cannot_be_tripped_by_a_negative_fusion_call():
    """`NR4A3: negative` on every sample must not score every sample as EMC."""
    assert M.EMC_TOKENS.search("NR4A3 status: negative")          # loose set may match
    assert not M.EMC_STRICT_TOKENS.search("NR4A3 status: negative")
    assert M.EMC_STRICT_TOKENS.search("Extraskeletal myxoid chondrosarcoma 1")


def test_every_control_is_actually_dispatched_by_the_fetch_code():
    """A control declared in a dict and never queried is a control that does not exist."""
    src = open(os.path.join(MOD, "emc_sra_study.py"), "r", encoding="utf-8").read()
    body = src.split("def _fetch_round(")[1].split("\ndef fetch(")[0]
    assert "for key, c in CONTROLS.items():" in body, (
        "the fetch round no longer iterates CONTROLS — the controls would be declared and never "
        "sent, and the gate would grade payloads that were never requested")
    for suffix in ("_bioproject_esearch", "_sra_esearch", "_ena_read_run"):
        stem = suffix.rsplit("_", 1)[0].lstrip("_")
        assert stem in body, f"the fetch round never issues a {suffix} call for the controls"


def test_the_ena_sample_endpoint_is_never_asked_with_a_project_accession():
    """⛔ Measured 2026-08-08, run 31276593535: passing the project accession to ENA's `sample`
    endpoint returns HTTP 400 for both targets. A 400 and an archive with no samples produce the
    same row count, so the request must be built from sample accessions harvested from the run
    report — asserted here because the failure mode is silent."""
    src = open(os.path.join(MOD, "emc_sra_study.py"), "r", encoding="utf-8").read()
    body = src.split("def _fetch_round(")[1].split("\ndef fetch(")[0]
    assert '"result": "sample"' in body, "the sample endpoint is no longer queried at all"
    seg = body.split('"result": "sample"')[0]
    tail = seg[-400:]
    assert "sample_accs" in tail, (
        "the sample-endpoint request is not built from harvested sample accessions — if it "
        "passes the project accession again, ENA answers 400 and the rows read as zero")
    assert "not_attempted" in body, (
        "a skipped sample query must be recorded as not_attempted, never left absent, or a "
        "missing key reads as a zero-sample deposit")


def test_a_zero_from_the_biosample_term_search_is_labelled_as_a_query_shape():
    """The `biosample` esearch returned 0 for both real accessions while 12 BioSamples existed."""
    src = open(os.path.join(MOD, "emc_sra_study.py"), "r", encoding="utf-8").read()
    fetch_body = src.split("def _fetch_round(")[1].split("\ndef fetch(")[0]
    assert "elink.fcgi" in fetch_body, (
        "nothing asks for BioSamples by LINK; the term search alone returns 0 for a project "
        "accession and that zero would stand unchallenged")
    r = M.derive(_inputs(_controls() +
                         [_es(f"tgt_{M.TARGET_BIOPROJECT}_bioproject_esearch", 1),
                          _es(f"tgt_{M.TARGET_BIOPROJECT}_biosample_esearch", 0)]))
    n = r["targets"][M.TARGET_BIOPROJECT]["ncbi"]
    assert n["biosample_esearch_count"] == 0
    assert "⚠ biosample_esearch_note" in n, "the zero is unlabelled and reads as an absence"
    assert n["biosample_linked_uids"] is None, "an unread link must be None, never 0"


def test_the_committed_artifact_if_present_re_derives_from_its_own_cached_payloads():
    """The published verdict must be a function of the published payloads, not of a past run."""
    out, inp = M.OUT, M.INPUTS
    if not (os.path.exists(out) and os.path.exists(inp)):
        pytest.skip("no committed artifact yet — the fetch has not run")
    with open(inp, "r", encoding="utf-8") as fh:
        cached = json.load(fh)
    with open(out, "r", encoding="utf-8") as fh:
        committed = json.load(fh)
    fresh = M.derive(cached)
    assert fresh["verdict"] == committed["verdict"], (
        "the committed verdict does not re-derive from the committed payloads")
    assert fresh["resolved"] == committed["resolved"]
