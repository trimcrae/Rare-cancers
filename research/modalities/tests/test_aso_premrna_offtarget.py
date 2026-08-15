#!/usr/bin/env python3
"""The pre-mRNA screen must find every planted site, classify it, and never inflate a count.

⛔ WHY THESE ARE PLANTED SITES RATHER THAN A FIXTURE OF THE REAL FETCH. This screen exists to close a
compartment the manuscript concedes is unmeasured, so the number it produces will be quoted. A test
that only checked the module runs would be worth nothing: the failure modes that matter are a MISSED
hit (which would report the new compartment as clean, the flattering direction), a hit counted more
than once (three seed blocks per design, so the natural bug inflates by up to threefold), a
compartment misclassified, and a reverse-complement match counted as hybridisable. Each is planted
below at a known coordinate, so a wrong answer is a specific wrong answer.
"""
import os
import random
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

m = pytest.importorskip("aso_premrna_offtarget")

TARGET = "GTCCACGGATATGCCC"          # a real target window: the EWSR1 e1 lead design


def _fixture():
    """One synthetic pre-mRNA: exon 0-99, intron 100-399, exon 400-599, with five planted sites."""
    random.seed(7)
    seq = list("".join(random.choice("ACGT") for _ in range(600)))

    def plant(at, s):
        for i, ch in enumerate(s):
            seq[at + i] = ch

    plant(150, TARGET)                                    # wholly intronic, exact, hybridisable
    plant(90, TARGET)                                     # spans the 99/100 exon-intron boundary
    plant(450, TARGET)                                    # wholly exonic
    plant(250, m._rc(TARGET))                             # reverse complement -> NOT hybridisable
    mm = list(TARGET)
    mm[7] = "A" if mm[7] != "A" else "C"                  # one mismatch, inside the catalytic gap
    plant(500, "".join(mm))

    exons = [[0, 99], [400, 599]]
    text = "".join(seq)
    premrna = {"TEST": {"transcript": "ENST_TEST", "strand": 1, "genomic_start": 1,
                        "genomic_end": len(text), "premrna_nt": len(text), "n_exons": len(exons),
                        "exonic_nt": sum(b - a + 1 for a, b in exons),
                        "exon_spans_0based_inclusive": exons, "sequence": text}}
    designs = [{"_key": "K", "junction_label": "TEST", "antisense_5to3": "X",
                "target_mRNA_5to3": TARGET, "gap_specificity_margin": 3, "gc_percent": 62.5}]
    return designs, premrna


def _hits():
    designs, premrna = _fixture()
    return {h["premrna_start_0based"]: h for h in m.scan(designs, premrna)["K"]["hits"]}


def test_every_planted_site_is_found_exactly_once():
    """A miss is the dangerous direction and a duplicate is the likely one."""
    designs, premrna = _fixture()
    hits = m.scan(designs, premrna)["K"]["hits"]
    starts = sorted(h["premrna_start_0based"] for h in hits)
    assert starts == [90, 150, 250, 450, 500], starts
    assert len(starts) == len(set(starts)), "a window was counted more than once"


def test_the_compartments_are_classified_from_the_exon_spans():
    """The whole value of this screen is the intronic/boundary distinction, so it is asserted."""
    h = _hits()
    assert h[150]["compartment"] == "intronic"
    assert h[90]["compartment"] == "intron_exon_spanning"
    assert h[450]["compartment"] == "exonic"
    assert h[500]["compartment"] == "exonic"


def test_a_reverse_complement_match_is_not_hybridisable():
    """Same rule, and the same reason, as the mature screens' orientation filter."""
    h = _hits()
    assert h[250]["hybridisable"] is False
    assert h[250]["orientation"] == "reverse_complement"
    assert all(h[s]["hybridisable"] for s in (90, 150, 450, 500))


def test_a_reverse_hit_reports_forward_coordinates():
    """Reported on the forward sequence in both orientations, or a reader cannot locate it.

    The planted reverse complement sits at forward offset 250; reported in reverse-strand coordinates
    it would read 334, and nothing in the artifact would say which convention was used.
    """
    h = _hits()
    assert 250 in h and 334 not in h


def test_the_gap_is_resolved_and_a_gap_mismatch_unpairs_it():
    h = _hits()
    assert h[150]["gap_mismatches"] == 0 and h[150]["gap_fully_paired"] is True
    assert h[500]["mismatches"] == 1
    assert h[500]["gap_mismatches"] == 1 and h[500]["gap_fully_paired"] is False


def test_the_clean_set_is_derived_from_the_screens_and_not_listed():
    """Nine sequences typed into the module would be a second home for the paper's headline set."""
    src = open(os.path.join(MOD, "aso_premrna_offtarget.py")).read()
    for seq in ("GGGCATATCCGTGGAC", "GGGCATATCTCTATAA", "CAGGGCATATCTTGCA"):
        assert seq not in src, f"{seq} is hard-coded; derive it from the screens instead"
    clean = m._clean_sequences()
    if not clean:
        pytest.skip("the screens are not present in this checkout")
    assert len(clean) == 9, sorted(clean)


def test_the_genomic_arm_never_falls_back_to_a_transcript_database():
    """⛔ The one thing this arm must not do is become a mature screen wearing a genomic label."""
    assert "refseq_rna" not in m.GENOMIC_DB_CANDIDATES
    assert all("rna" not in db for db in m.GENOMIC_DB_CANDIDATES), m.GENOMIC_DB_CANDIDATES


def test_the_manuscript_matches_the_committed_premrna_screen():
    """§3.8's numbers, tied to the artifact, in both directions.

    ⚠ THIS SECTION IS THE ONLY PLACE THE PAPER REPORTS A COMPARTMENT IT PREVIOUSLY CONCEDED WAS
    UNMEASURED, so its numbers will be the ones a reviewer checks first. They are asserted against the
    artifact rather than against each other, and the two-class structure is asserted too — because the
    interesting half of the finding is not the count but that every intron-exon-spanning site is in
    NR4A3 at one boundary, and every wholly intronic one is in the gene holding most of the introns.
    """
    art = os.path.join(MOD, "aso-premrna-offtarget.json")
    paper = os.path.join(os.path.dirname(MOD), "manuscripts", "aso",
                         "fusion-junction-aso-research-article.md")
    if not (os.path.exists(art) and os.path.exists(paper)):
        pytest.skip("the pre-mRNA screen or the manuscript is not present in this checkout")
    d = __import__("json").load(open(art))
    txt = re.sub(r"\s+", " ", open(paper, encoding="utf-8").read())
    c = d["corpus"]
    assert c["designs"] == 190 and c["with_any_hit"] == 53, c
    assert c["with_hybridisable_gap_paired"] == 19, c
    # Equal by construction is worth asserting: a purely exonic gap-paired site would have been
    # visible to the mature screens, so if these ever diverge the compartment logic has changed.
    assert c["with_a_liability_invisible_to_mature_screens"] == 19, c
    assert "53 have a" in txt and "Nineteen carry one that meets all three conditions" in txt

    classes = {}
    for r in d["per_design"]:
        for h in r["hits"]:
            if h["hybridisable"] and h["gap_fully_paired"] and h["compartment"] != "exonic":
                classes.setdefault((h["gene"], h["compartment"]), 0)
                classes[(h["gene"], h["compartment"])] += 1
    assert classes == {("NR4A3", "intron_exon_spanning"): 9, ("TCF12", "intronic"): 10}, classes
    assert "Nine are intron–exon-spanning, and every one is in *NR4A3*" in txt
    assert "The other ten are wholly intronic and every one is in *TCF12*" in txt

    # The margin trend, which is what makes this a third instrument agreeing with the ranking.
    by_margin = {}
    for r in d["per_design"]:
        n, k = by_margin.get(r["gap_specificity_margin"], (0, 0))
        by_margin[r["gap_specificity_margin"]] = (
            n + 1, k + bool(r["n_invisible_to_mature_screens"]))
    assert by_margin[1] == (76, 12) and by_margin[2] == (76, 7) and by_margin[3] == (38, 0), by_margin
    # ⚠ WHITESPACE-TOLERANT: the manuscript hard-wraps, so any of these phrases can straddle a
    # newline. A test that only passes on one line-break position is a test of the reflow.
    flat = " ".join(txt.split())
    for phrase in (f"margin 1, {by_margin[1][1]} of {by_margin[1][0]} designs carry a pre-mRNA site",
                   f"margin 2, {by_margin[2][1]} of {by_margin[2][0]}",
                   f"margin 3, none of {by_margin[3][0]}"):
        assert phrase in flat, phrase

    # And the headline: the nine clean designs must be clean in this compartment too.
    clean = m._clean_sequences()
    if clean:
        rows = {r["antisense_5to3"]: r for r in d["per_design"]}
        offenders = [q for q in clean if rows.get(q, {}).get("n_invisible_to_mature_screens")]
        assert not offenders, f"a design the paper calls clean carries a pre-mRNA liability: {offenders}"

    # The intronic search space, quoted in the paper as the reason TCF12 holds that whole class.
    intronic = sum(g["premrna_nt"] - g["exonic_nt"] for g in d["genes"].values())
    tcf12 = d["genes"]["TCF12"]["premrna_nt"] - d["genes"]["TCF12"]["exonic_nt"]
    assert f"{tcf12:,} of the {intronic:,} intronic nucleotides" in flat
    assert f"{round(100 * tcf12 / intronic)}% of the search space" in flat


def test_the_mismatch_ceiling_is_derived_from_the_blast_arms_identity_threshold():
    """<=2 mismatches over 16 nt IS >=14/16. Ask pre-mRNA a stricter question and it looks cleaner
    for that reason alone, which is the most flattering way this screen could be wrong."""
    jo = pytest.importorskip("junction_aso_offtarget")
    ja = pytest.importorskip("junction_aso")
    assert m.MAX_MM == jo.MAX_MISMATCHES_PER_NEAR_MATCH, (m.MAX_MM,)
    assert ja.OLIGO_LEN - m.MAX_MM == jo.NEAR_MATCH_MIN_IDENT
    assert m.MAX_MM == 2 and jo.NEAR_MATCH_MIN_IDENT == 14, "the 16-mer 5-6-5 panel's values moved"


def test_the_gap_region_seam_is_live_and_not_a_silent_fallback():
    """⛔ THIS SEAM WAS DEAD FROM THE DAY IT WAS WRITTEN UNTIL 2026-08-13.

    `_gap_region()` imported `GAP_REGION_1BASED` from `junction_aso_offtarget` inside a bare
    `except Exception` and fell back to this module's own hard-coded `GAP_1BASED`. The name had
    never existed there, so the fallback fired on every call — and at the default 16,5 geometry the
    fallback is the RIGHT answer, so no test, no artifact and no run could distinguish a working
    seam from a dead one. Under a `20,5` dispatch the two modules would have disagreed about where
    the catalytic gap is.

    Assert the seam itself, not its result: the constant must exist in the owning module, and
    `_gap_region()` must return that value rather than the local constant that happens to match it.
    """
    import importlib
    import aso_premrna_offtarget as m
    jo = importlib.import_module("junction_aso_offtarget")
    assert hasattr(jo, "GAP_REGION_1BASED"), (
        "the owning module stopped exporting GAP_REGION_1BASED; _gap_region() is dead again")
    assert m._gap_region() == tuple(jo.GAP_REGION_1BASED)


def test_the_gap_region_follows_a_geometry_change_rather_than_the_local_default():
    """The property the docstring promises: change the geometry, the gap moves with it.

    Run in a subprocess with a real environment, because OLIGO_LEN/WING resolve at import — patching
    the constants afterwards would test the patch, not the dispatch path CI takes.
    """
    import subprocess
    import sys as _sys
    code = (
        "import sys; sys.path.insert(0, %r);"
        "import aso_premrna_offtarget as m, junction_aso_offtarget as jo;"
        "print(m._gap_region(), tuple(jo.GAP_REGION_1BASED), m.GAP_1BASED)" % MOD
    )
    env = dict(os.environ, OLIGO_LEN="20", WING="5")
    out = subprocess.run([_sys.executable, "-c", code], capture_output=True, text=True, env=env)
    assert out.returncode == 0, out.stderr
    got, owned, local = out.stdout.strip().split(") (")
    assert got.lstrip("(") == owned, f"_gap_region() did not follow the geometry: {out.stdout}"
    assert got.lstrip("(") != local.rstrip(")"), (
        "at 20,5 the derived gap must differ from the hard-coded 16-mer default; if these are "
        "equal the fallback is live again and the test cannot see it")


def test_the_refseq_scan_counts_nucleotides_and_not_only_records():
    """⛔ THE ONE NUMBER THE MANUSCRIPT NEEDS FROM THIS CORPUS IS ITS SPAN, AND IT WAS NOT COUNTED.

    `offtarget_scan` reads every base of every transcript and reported only `transcripts_scanned`.
    Lacking a nucleotide span, §3.6's chance null carries an ASSUMED 3e8-8e8 nt range, which is what
    makes its headline expectations a 2.7x-wide band ("79-210", "3.4-9.1") instead of single figures.

    Uses the module's own file-reuse seam — an existing gz under RUNNER_TEMP is not re-downloaded —
    so this exercises the real loop rather than a monkeypatched substitute.
    """
    import gzip
    import tempfile
    sys.path.insert(0, MOD)
    import aso_insilico as ai

    recs = {"NM_1": "ACGT" * 10, "NM_2": "TTTT" * 7, "NM_3": "GC" * 13}
    d = tempfile.mkdtemp()
    with gzip.open(os.path.join(d, "grch38_rna.fna.gz"), "wt") as fh:
        for a, s in recs.items():
            fh.write(">%s desc\n%s\n" % (a, s))
    old = os.environ.get("RUNNER_TEMP")
    os.environ["RUNNER_TEMP"] = d
    try:
        cand = {"antisense_5to3": "ACGTACGTACGTACGT", "target_mRNA_5to3": "ACGTACGTACGTACGT"}
        out = ai.offtarget_scan([dict(cand)])
        assert out["transcripts_scanned"] == len(recs)
        assert out["scanned_nt"] == sum(len(s) for s in recs.values())
        # Under max_records the span must be the SUBSET's, never the corpus' — a span reported for
        # sequence that was not scanned would be a denominator nothing was measured against.
        out2 = ai.offtarget_scan([dict(cand)], max_records=2)
        assert out2["scanned_nt"] == len(recs["NM_1"]) + len(recs["NM_2"]), out2
    finally:
        if old is None:
            os.environ.pop("RUNNER_TEMP", None)
        else:
            os.environ["RUNNER_TEMP"] = old
