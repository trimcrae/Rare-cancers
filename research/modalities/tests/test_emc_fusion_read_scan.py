"""The scanner must be unable to invent a junction, and unable to miss one it can see.

Both directions are asserted because they cost different things. A false junction would put a
fabricated breakpoint into the ASO panel — the worst outcome this route has. A false negative
would retire a deposit that still holds an answer. Everything here is offline arithmetic over the
committed transcript sequences; no network, no aligner, no reference download.
"""

import gzip
import io
import json
import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import emc_fusion_read_scan as M  # noqa: E402


@pytest.fixture(scope="module")
def genes():
    return M.load_genes()


@pytest.fixture(scope="module")
def sc(genes):
    return M.JunctionScanner(genes)


def _fastq(reads):
    out = []
    for i, r in enumerate(reads):
        out.append(f"@read{i} some description\n{r}\n+\n{'I' * len(r)}\n")
    return "".join(out)


def _seam(genes, donor_gene, donor_exon, site):
    n3 = genes["NR4A3"]
    left = M.exon_seq(genes[donor_gene], donor_exon)[-70:]
    if site == "NR4A3_intron2_start":
        right = M.intron_seq(n3, 2)[:70]
    elif site == "NR4A3_exon2_start":
        right = M.exon_seq(n3, 2)[:70]
    else:
        right = M.exon_seq(n3, 3)[:70]
    return (left + right).upper()


def test_the_module_selftest_passes():
    assert M.selftest() == 0


def test_committed_exon_spans_sum_to_the_committed_exonic_length(genes):
    # If this drifts, every seam this module builds is silently off. It is the one assumption
    # the whole method rests on and it is checked against a number the source file states itself.
    for name, g in genes.items():
        total = sum(
            len(M.exon_seq(g, i)) for i in range(1, len(g["exon_spans_0based_inclusive"]) + 1)
        )
        assert total == g["exonic_nt"], f"{name}: exon spans sum to {total}, file says {g['exonic_nt']}"


@pytest.mark.parametrize(
    "donor_gene,donor_exon,site",
    [
        ("EWSR1", 7, "NR4A3_exon2_start"),
        ("EWSR1", 12, "NR4A3_exon3_start"),
        ("EWSR1", 13, "NR4A3_exon3_start"),
        ("TAF15", 6, "NR4A3_exon3_start"),
        ("TAF15", 6, "NR4A3_intron2_start"),
        ("TCF12", 5, "NR4A3_exon3_start"),
        ("TFG", 3, "NR4A3_exon3_start"),
    ],
)
def test_a_known_seam_is_recovered_and_named_correctly(sc, genes, donor_gene, donor_exon, site):
    sc.reset()
    sc._scan_text(_fastq([_seam(genes, donor_gene, donor_exon, site)]))
    hits = {(j["donor"], j["acceptor_site"]) for j in sc.junctions.values()}
    assert (f"{donor_gene}_exon{donor_exon}", site) in hits, f"got {hits}"


def test_the_wildtype_nr4a3_transcript_is_never_called_a_fusion(sc, genes):
    # The common case in any NR4A3-expressing tumour. A scanner that calls this a fusion would
    # report a breakpoint in every sample it ever saw.
    n3 = genes["NR4A3"]
    reads = [
        (M.exon_seq(n3, i)[-70:] + M.exon_seq(n3, i + 1)[:70]).upper()
        for i in range(1, n3["n_exons"])
    ]
    sc.reset()
    sc._scan_text(_fastq(reads))
    assert sc.junctions == {}, f"wild-type NR4A3 junctions were called fusions: {list(sc.junctions)}"


def test_random_sequence_produces_no_junction(sc):
    random.seed(11)
    reads = ["".join(random.choice("ACGT") for _ in range(150)) for _ in range(400)]
    sc.reset()
    sc._scan_text(_fastq(reads))
    assert sc.junctions == {}


def test_a_partner_read_with_no_nr4a3_produces_no_junction(sc, genes):
    # An EWSR1 read that never reaches NR4A3 must not be called a fusion.
    g = genes["EWSR1"]
    reads = [M.exon_seq(g, i)[:150].upper() for i in range(1, 10) if len(M.exon_seq(g, i)) >= 60]
    sc.reset()
    sc._scan_text(_fastq(reads))
    assert sc.junctions == {}


def test_too_little_donor_flank_is_refused(sc, genes):
    n3 = genes["NR4A3"]
    for n_donor in range(0, M.MIN_FLANK):
        read = (M.exon_seq(genes["EWSR1"], 12)[-n_donor:] if n_donor else "") + M.exon_seq(n3, 3)[:70]
        sc.reset()
        sc._scan_text(_fastq([read.upper()]))
        assert not sc.junctions, f"{n_donor} nt of donor was enough to call a junction"


def test_exactly_the_minimum_flank_is_accepted(sc, genes):
    read = (
        M.exon_seq(genes["EWSR1"], 12)[-M.MIN_FLANK :] + M.exon_seq(genes["NR4A3"], 3)[: M.MIN_FLANK]
    ).upper()
    sc.reset()
    sc._scan_text(_fastq([read]))
    assert {j["donor"] for j in sc.junctions.values()} == {"EWSR1_exon12"}


def test_both_strands_are_scanned(sc, genes):
    fwd = _seam(genes, "TAF15", 6, "NR4A3_exon3_start")
    for read in (fwd, M.revcomp(fwd)):
        sc.reset()
        sc._scan_text(_fastq([read]))
        assert {j["donor"] for j in sc.junctions.values()} == {"TAF15_exon6"}


def test_a_junction_survives_a_chunk_boundary(genes, monkeypatch):
    """The stream is scanned in chunks; a seam landing on a boundary must still be found.

    This is the defect class that would produce a silent, size-dependent false negative — the
    scan would report zero on a real fusion purely because of where the 8 MB boundary fell.
    """
    seam = _seam(genes, "EWSR1", 12, "NR4A3_exon3_start")
    filler = _fastq(["".join(random.Random(3).choice("ACGT") for _ in range(150))] * 200)
    for pad in range(0, 400, 37):
        text = filler[:pad] + _fastq([seam]) + filler
        raw = text.encode()
        monkeypatch.setattr(M, "CHUNK", 512)
        sc = M.JunctionScanner(genes)
        sc.scan_stream(io.BytesIO(raw))
        assert {j["donor"] for j in sc.junctions.values()} == {"EWSR1_exon12"}, f"lost at pad={pad}"


def test_a_gzipped_stream_is_scanned_end_to_end(genes):
    """Exercises the real path: gzip -> chunked scan -> junction, with depth counted."""
    reads = [
        _seam(genes, "TCF12", 5, "NR4A3_exon3_start"),
        _seam(genes, "TAF15", 6, "NR4A3_intron2_start"),
    ]
    random.seed(5)
    reads += ["".join(random.choice("ACGT") for _ in range(150)) for _ in range(500)]
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(_fastq(reads).encode())
    buf.seek(0)
    sc = M.JunctionScanner(genes)
    sc.scan_stream(gzip.GzipFile(fileobj=buf))
    found = {(j["donor"], j["acceptor_site"]) for j in sc.junctions.values()}
    assert ("TCF12_exon5", "NR4A3_exon3_start") in found
    assert ("TAF15_exon6", "NR4A3_intron2_start") in found


# ------------------------------------------------------------------ the assay gate


def test_the_assay_gate_refuses_a_targeted_probe_assay():
    # ⛔ The measured case: PRJNA1357027's own SRA experiment title. Its reads are 50 nt fixed
    # amplicons, so scanning them would produce a zero that means nothing.
    cap, why = M.assay_is_capable_of_spanning_a_junction(
        ["Targeted RNA-seq (TempO-Seq) of EMC", "RNA-Seq", "TRANSCRIPTOMIC"], 50
    )
    assert cap is False
    assert "TARGETED" in why


def test_the_assay_gate_accepts_whole_transcriptome():
    cap, _ = M.assay_is_capable_of_spanning_a_junction(
        ["Illumina NovaSeq X sequencing: GSM9037837: USZ-23_EMC3", "RNA-Seq", "TRANSCRIPTOMIC"], 151
    )
    assert cap is True


def test_the_assay_gate_says_cannot_determine_rather_than_no():
    # An absent reading is not a reading of absence (CLAUDE.md §4).
    assert M.assay_is_capable_of_spanning_a_junction([], None)[0] is None
    assert M.assay_is_capable_of_spanning_a_junction(["   "], None)[0] is None


def test_a_run_with_no_public_files_is_not_reported_as_a_negative(genes):
    """dbGaP-protected runs must produce a refusal, never 'no junction found'."""
    row = {
        "run_accession": "SRR24994636",
        "library_strategy": "WGS",
        "library_layout": "PAIRED",
        "experiment_title": "Extraskeletal myxoid chondrosarcoma lung metastasis",
        "fastq_ftp": "",
        "submitted_ftp": "Protected file(s). Go to dbGap",
        "read_count": "270869539",
        "base_count": "78720579623",
    }
    out = M.scan_run(row, genes)
    assert out["state"] == "NO_PUBLIC_FILES"
    assert "junctions_found" not in out


def test_a_targeted_assay_run_is_refused_before_any_download(genes):
    row = {
        "run_accession": "SRRTEST",
        "library_strategy": "RNA-Seq",
        "library_source": "TRANSCRIPTOMIC",
        "library_layout": "SINGLE",
        "experiment_title": "Targeted RNA-seq (TempO-Seq) of EMC",
        "fastq_ftp": "ftp.example/x_1.fastq.gz",
        "read_count": "5582928",
        "base_count": "279146400",
    }
    out = M.scan_run(row, genes)
    assert out["state"] == "REFUSED_BY_ASSAY_GATE"
    assert out["assay_capable_of_spanning_a_junction"] is False
    assert "junctions_found" not in out


def test_read_length_is_derived_per_mate_for_paired_runs():
    # 8137395134 / 26945017 = 302 total -> 151 per mate. Getting this wrong would let a 2x25
    # library through the flank check.
    assert M._read_len(
        {"read_count": "26945017", "base_count": "8137395134", "library_layout": "PAIRED"}
    ) == 151.0
    assert M._read_len(
        {"read_count": "5582928", "base_count": "279146400", "library_layout": "SINGLE"}
    ) == 50.0
