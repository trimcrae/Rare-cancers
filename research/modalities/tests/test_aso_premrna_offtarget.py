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


def test_the_mismatch_ceiling_is_derived_from_the_blast_arms_identity_threshold():
    """<=2 mismatches over 16 nt IS >=14/16. Ask pre-mRNA a stricter question and it looks cleaner
    for that reason alone, which is the most flattering way this screen could be wrong."""
    jo = pytest.importorskip("junction_aso_offtarget")
    ja = pytest.importorskip("junction_aso")
    assert m.MAX_MM == jo.MAX_MISMATCHES_PER_NEAR_MATCH, (m.MAX_MM,)
    assert ja.OLIGO_LEN - m.MAX_MM == jo.NEAR_MATCH_MIN_IDENT
    assert m.MAX_MM == 2 and jo.NEAR_MATCH_MIN_IDENT == 14, "the 16-mer 5-6-5 panel's values moved"
