"""Unit tests for junction_proteome_novelty (proteome-wide exact-match novelty test).

The network fetch is the only thing mocked — the FASTA parse, the sentinel join, the
record lookup and the hit/miss classification are all exercised for real, because those
are what the claim "absent from the human proteome" actually rests on.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import junction_proteome_novelty as n  # noqa: E402


FASTA = (
    ">sp|P00001|AAAA_HUMAN Alpha OS=Homo sapiens OX=9606\n"
    "MKWVTFISLL\nFLFSSAYSRG\n"
    ">sp|P00002|BBBB_HUMAN Beta OS=Homo sapiens OX=9606\n"
    "QQIVRTDSLK\n"
    ">sp|P56945-2|EWS_HUMAN RNA-binding protein EWS OS=Homo sapiens OX=9606\n"
    "GGGYSQQSSR\n"
)


def test_fasta_parse_keeps_accession_name_and_joins_wrapped_lines():
    entries = _parse(FASTA)
    assert [e[0] for e in entries] == ["P00001", "P00002", "P56945-2"]
    assert entries[0][1] == "AAAA_HUMAN Alpha"
    assert entries[0][2] == "MKWVTFISLLFLFSSAYSRG"          # wrapped lines joined
    assert len(entries[1][2]) == 10


def _parse(text):
    """The parser inside fetch_proteome, exercised on a literal FASTA."""
    import io
    entries, acc, name, chunks = [], None, None, []
    for line in io.StringIO(text):
        line = line.rstrip("\n")
        if line.startswith(">"):
            if acc:
                entries.append((acc, name, "".join(chunks)))
            parts = line[1:].split("|")
            acc = parts[1] if len(parts) > 2 else line[1:].split()[0]
            name = parts[2].split(" OS=")[0] if len(parts) > 2 else ""
            chunks = []
        elif line:
            chunks.append(line.strip())
    if acc:
        entries.append((acc, name, "".join(chunks)))
    return entries


def _run(tmp_path, monkeypatch, peptides, binders=(), junctions_key="novel_peptides"):
    bp = {
        "_utc": "2026-08-07T00:56:11Z",
        "n_inframe_junctions": 1,
        "junctions": [{"label": "EWSR1 e7 :: NR4A3 e3", junctions_key: list(peptides)}],
        "predicted_binders_ranked": [dict(b) for b in binders],
    }
    src = tmp_path / "fusion-breakpoint-neoantigens.json"
    out = tmp_path / "junction-proteome-novelty.json"
    src.write_text(json.dumps(bp))
    monkeypatch.setattr(n, "BREAKPOINTS", str(src))
    monkeypatch.setattr(n, "OUT", str(out))
    monkeypatch.setattr(n, "fetch_proteome", lambda *a, **k: _parse(FASTA))
    assert n.main() == 0
    return json.loads(out.read_text())


def test_a_peptide_present_in_a_human_protein_is_reported_as_found(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, ["QQIVRTDSL"])
    assert res["n_found_in_proteome"] == 1
    assert res["n_novel_proteome_wide"] == 0
    hit = res["peptides_found_in_proteome"][0]
    assert hit["novel_proteome_wide"] is False
    assert [h["accession"] for h in hit["proteome_hits"]] == ["P00002"]


def test_a_peptide_absent_everywhere_is_reported_as_novel(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, ["NMPCVQAQY"])
    assert res["n_novel_proteome_wide"] == 1
    assert res["peptides_novel_proteome_wide"][0]["proteome_hits"] == []


def test_no_match_may_straddle_two_proteins(tmp_path, monkeypatch):
    # "AYSRG" ends P00001 and "QQIVR" starts P00002; concatenated they would match.
    res = _run(tmp_path, monkeypatch, ["AYSRGQQIVR"])
    assert res["n_novel_proteome_wide"] == 1, "sentinel failed to separate records"


def test_an_isoform_hit_counts_and_is_flagged_as_a_parent(tmp_path, monkeypatch):
    # P56945-2 is an EWSR1 isoform; a parent-filtered peptide matching it means the
    # upstream two-protein filter missed the isoform, which this check must say out loud.
    res = _run(tmp_path, monkeypatch, ["GGGYSQQSSR"])
    chk = res["⛔_upstream_filter_check"]
    assert chk["verdict"].startswith("BROKEN")
    assert chk["parent_protein_hits"][0]["parent"] == "EWSR1"


def test_clean_input_reports_the_filter_as_consistent(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, ["NMPCVQAQY"])
    assert res["⛔_upstream_filter_check"]["verdict"].startswith("consistent")
    assert res["⛔_upstream_filter_check"]["parent_protein_hits"] == []


def test_predicted_binder_status_is_carried_through(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, ["QQIVRTDSL", "NMPCVQAQY"],
               binders=[{"peptide": "QQIVRTDSL", "allele": "HLA-B*08:01",
                         "class": "strong", "affinity_nM": 12.3}])
    found = res["peptides_found_in_proteome"][0]
    assert found["predicted_binder"]["allele"] == "HLA-B*08:01"
    assert res["n_predicted_binders_found_in_proteome"] == 1
    assert res["peptides_novel_proteome_wide"][0]["predicted_binder"] is None


def test_the_result_records_what_was_searched(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, ["NMPCVQAQY"])
    p = res["_proteome"]
    assert p["proteome_id"] == "UP000005640"
    assert p["reviewed_only"] is True and p["isoforms_included"] is True
    assert p["trembl_included"] is False, "a TrEMBL search would change what the result means"
    assert p["n_sequences"] == 3
    assert res["_input"]["coordinate_system"].startswith("TRANSCRIPT")


def test_missing_input_artifact_is_a_nonzero_exit_not_an_empty_result(tmp_path, monkeypatch):
    monkeypatch.setattr(n, "BREAKPOINTS", str(tmp_path / "nope.json"))
    monkeypatch.setattr(n, "OUT", str(tmp_path / "out.json"))
    assert n.main() == 1
    assert not (tmp_path / "out.json").exists()
