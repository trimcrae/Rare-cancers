"""Regression tests for the PARENTS accession map of `junction_proteome_novelty`.

⚠ WHY THIS FILE EXISTS, AND WHY IT IS SEPARATE FROM
`test_junction_proteome_novelty.py`. That file's FASTA fixture names the EWSR1 record
`P56945-2`, so its parent-flag test passes on whichever accession `PARENTS` happens to
carry. The proteome this script actually searches names human EWSR1 `Q01844`: every other
module in this repository records `Q01844` (`fusion_neoantigen.py`,
`nr4a_paralogue_unique_residues.py`, `emc_fet_construct_designs.py`,
`emc-construct-inputs.json`), and `junction-selfsimilarity.json`'s own recorded hits name
`Q01844`, `Q01844-2`, `-3`, `-5`, `-6` as `EWS_HUMAN RNA-binding protein EWS`. A `PARENTS`
map without `Q01844` therefore leaves `⛔_upstream_filter_check` able to flag NR4A3 only:
a junction peptide occurring verbatim in wild-type EWSR1 or an EWSR1 isoform would be
counted in `n_found_in_proteome` yet would NOT trip the `BROKEN` verdict.

These tests fail on a map that omits `Q01844` and pass on one that carries it. Nothing in
the existing fixture or its assertions is modified — this file only ADDS, and it uses its
own FASTA so the existing `n_sequences == 3` assertion keeps its meaning.

The EWSR1 sequence used here is REAL: both records are exact, contiguous windows of the
canonical human EWSR1 sequence committed in `research/modalities/fet-sequences-cache.json`
(key `EWSR1`), residues 1-20 and 38-57 respectively. Each test peptide occurs exactly once
in that canonical sequence and in none of the other fixture records.

⚠ The isoform record below carries a REAL CANONICAL EWSR1 window under the accession
`Q01844-2` purely to exercise the accession-prefix split (`acc.split("-")[0]`). It is NOT a
claim about isoform EWS-B's actual sequence: no EWSR1 isoform sequence is present in this
checkout, and that sequence is UNKNOWN here.

⛔ Nothing in this file is an immunogenicity, presentation, efficacy, safety, selectivity,
therapeutic-window or clinical-readiness claim. It tests one guard's coverage, nothing else.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import junction_proteome_novelty as n  # noqa: E402

# Windows of canonical human EWSR1 (UniProt Q01844) as committed in fet-sequences-cache.json.
EWSR1_1_20 = "MASTDYSTYSQAAAQQGYSA"
EWSR1_38_57 = "QQSYGTYGQPTDVSYTQAQT"

FASTA_WITH_WILDTYPE_EWSR1 = (
    ">sp|P00002|BBBB_HUMAN Beta OS=Homo sapiens OX=9606\n"
    "QQIVRTDSLK\n"
    ">sp|Q01844|EWS_HUMAN RNA-binding protein EWS OS=Homo sapiens OX=9606\n"
    f"{EWSR1_1_20}\n"
    ">sp|Q01844-2|EWS_HUMAN Isoform EWS-B of RNA-binding protein EWS OS=Homo sapiens OX=9606\n"
    f"{EWSR1_38_57}\n"
)


def _run_with_fasta(tmp_path, monkeypatch, fasta, peptides, binders=()):
    """Run `main()` end to end against a literal FASTA. Only the network fetch is replaced."""
    bp = {
        "_utc": "2026-08-07T00:56:11Z",
        "n_inframe_junctions": 1,
        "junctions": [{"label": "EWSR1 e7 :: NR4A3 e3", "novel_peptides": list(peptides)}],
        "predicted_binders_ranked": [dict(b) for b in binders],
    }
    src = tmp_path / "fusion-breakpoint-neoantigens.json"
    out = tmp_path / "junction-proteome-novelty.json"
    src.write_text(json.dumps(bp))
    monkeypatch.setattr(n, "BREAKPOINTS", str(src))
    monkeypatch.setattr(n, "OUT", str(out))
    monkeypatch.setattr(n, "fetch_proteome", lambda *a, **k: n._parse_fasta(fasta))
    assert n.main() == 0
    return json.loads(out.read_text())


def test_wildtype_EWSR1_is_a_recognised_parent_accession():
    """Q01844 must be IN the map. Without it the EWSR1 arm of the guard cannot fire at all."""
    assert "Q01844" in n.PARENTS, (
        "PARENTS omits Q01844, the accession under which the searched proteome names human "
        "EWSR1; the upstream-filter check can then only ever flag NR4A3"
    )
    assert n.PARENTS["Q01844"] == "EWSR1"


def test_a_peptide_verbatim_in_wildtype_EWSR1_trips_the_broken_verdict(tmp_path, monkeypatch):
    """The defect this file exists for: a parent-filtered peptide that IS wild-type EWSR1."""
    res = _run_with_fasta(tmp_path, monkeypatch, FASTA_WITH_WILDTYPE_EWSR1, ["TDYSTYSQA"])
    assert res["n_found_in_proteome"] == 1
    hit = res["peptides_found_in_proteome"][0]
    assert [h["accession"] for h in hit["proteome_hits"]] == ["Q01844"]
    chk = res["⛔_upstream_filter_check"]
    assert chk["verdict"].startswith("BROKEN"), (
        "a peptide occurring verbatim in wild-type EWSR1 was counted as found but did not "
        "trip the upstream-filter check"
    )
    assert chk["parent_protein_hits"] == [
        {"peptide": "TDYSTYSQA", "accession": "Q01844", "parent": "EWSR1"}
    ]


def test_an_EWSR1_isoform_accession_is_flagged_as_the_same_parent(tmp_path, monkeypatch):
    """Isoform accessions are `<base>-<n>`; the guard splits on '-', so Q01844-2 must flag too."""
    res = _run_with_fasta(tmp_path, monkeypatch, FASTA_WITH_WILDTYPE_EWSR1, ["SYGTYGQPT"])
    chk = res["⛔_upstream_filter_check"]
    assert chk["verdict"].startswith("BROKEN")
    assert chk["parent_protein_hits"] == [
        {"peptide": "SYGTYGQPT", "accession": "Q01844-2", "parent": "EWSR1"}
    ]


def test_a_non_parent_hit_is_still_reported_consistent(tmp_path, monkeypatch):
    """Negative control: adding Q01844 must not make unrelated hits flag as a parent."""
    res = _run_with_fasta(tmp_path, monkeypatch, FASTA_WITH_WILDTYPE_EWSR1, ["QQIVRTDSL"])
    assert res["n_found_in_proteome"] == 1
    assert res["peptides_found_in_proteome"][0]["proteome_hits"][0]["accession"] == "P00002"
    assert res["⛔_upstream_filter_check"]["verdict"].startswith("consistent")


def test_the_existing_P56945_key_is_retained(tmp_path, monkeypatch):
    """The fix ADDS; it must not drop the key the existing fixture-bound test relies on."""
    assert "P56945" in n.PARENTS and n.PARENTS["P56945"] == "EWSR1"
