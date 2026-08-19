#!/usr/bin/env python3
"""The §2.5/§2.7/§6 genomics numbers are recomputed from the screen outputs, not trusted.

⛔ WHY THIS EXISTS. A genomics reviewer working from the artefacts outward found four statements in
this manuscript that were each internally consistent and each not what the files say:

  1. §2.5 placed nine pre-mRNA sites "six or seven nucleotides into intron 2". They sit six or seven
     nucleotides from its 3′ END — intron 2 is 2,208 nucleotides long, so a reader following the
     sentence looks 2,200 nucleotides away from the site.
  2. §2.5 called them "19 sites". They are 19 DESIGNS reading 11 sites; the design/site/locus
     conflation is the single most repeated defect in this paper's history.
  3. §2.7 compared a 52.5% masked-hit share against the whole assembly's 51.4%. A hit can only fall
     in a window free of ambiguous bases, and the masked share of the sequence actually scanned is a
     BAND, not a point — inside which 52.5% falls, so the difference has no readable sign.
  4. §6 defined a near-match in substitutions while the alignment screen returns gapped alignments
     and the identity filter admits them.

★ WHAT THIS FILE ASSERTS is the artefact side of each, and then that the prose says it. The failure
mode being guarded is not arithmetic — every one of those numbers was arithmetically fine — it is a
sentence drifting away from the file it was read out of while nothing recomputes the reading.
"""
from __future__ import annotations

import collections
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
PAPER = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-research-article.md")
MODALITIES = os.path.join(REPO, "research", "modalities")
PREMRNA = os.path.join(MODALITIES, "aso-premrna-offtarget.json")
GENOME = os.path.join(MODALITIES, "aso-genome-offtarget.json")

OLIGO_NT = 16


def _paper() -> str:
    if not os.path.exists(PAPER):
        pytest.skip("the manuscript is not present in this checkout")
    return " ".join(open(PAPER, encoding="utf-8").read().split())


def _load(path):
    if not os.path.exists(path):
        pytest.skip(f"{os.path.basename(path)} is not present in this checkout")
    return json.load(open(path, encoding="utf-8"))


def _premrna_strict_class():
    """The 19: a hybridisable pre-mRNA site pairing the whole gap, outside a mature exon."""
    d = _load(PREMRNA)
    designs, sites = collections.defaultdict(set), collections.defaultdict(set)
    for rec in d["per_design"]:
        key = (rec["junction_label"], rec["antisense_5to3"])
        for hit in rec["hits"]:
            if not (hit.get("hybridisable") and hit.get("gap_fully_paired")):
                continue
            if hit["compartment"] == "exonic":
                continue
            designs[hit["compartment"]].add(key)
            sites[hit["compartment"]].add((hit["gene"], hit["premrna_start_0based"]))
    return d, designs, sites


def test_the_intron_two_sites_are_placed_at_the_end_of_the_intron_not_its_start():
    d, designs, sites = _premrna_strict_class()
    spanning = sites["intron_exon_spanning"]
    assert {g for g, _ in spanning} == {"NR4A3"}, spanning
    exons = d["genes"]["NR4A3"]["exon_spans_0based_inclusive"]
    intron2_start, exon3_start = exons[1][1] + 1, exons[2][0]
    intron2_len = exon3_start - intron2_start
    offsets = sorted(exon3_start - s for _, s in spanning)
    assert offsets == [6, 7], (
        f"the intron-2 sites are now {offsets} nucleotides from the exon-3 boundary; §2.5 says six "
        "or seven")
    assert intron2_len == 2208, intron2_len
    txt = _paper()
    assert "last six or seven nucleotides of intron 2" in txt, (
        "§2.5 must place these sites at the 3′ end of intron 2 — measured from its 5′ end they are "
        f"{intron2_len - 7} and {intron2_len - 6} nucleotides in, which is not where a reader looks")
    assert f"an intron {intron2_len:,} nucleotides long" in txt


def test_the_nineteen_are_designs_and_the_paper_calls_them_designs():
    """⚠ 19 designs at 11 sites. The paper said '19 sites', and site-versus-design conflation is the
    defect that has recurred most often here (17 transcript variants of one locus called 17 loci)."""
    _, designs, sites = _premrna_strict_class()
    n_designs = len(set().union(*designs.values()))
    n_sites = len(set().union(*sites.values()))
    assert (n_designs, n_sites) == (19, 11), (n_designs, n_sites)
    assert len(designs["intron_exon_spanning"]) == 9, designs["intron_exon_spanning"]
    assert len(designs["intronic"]) == 10, designs["intronic"]
    assert len(sites["intron_exon_spanning"]) == 2, sites["intron_exon_spanning"]
    assert {g for g, _ in sites["intronic"]} == {"TCF12"}
    txt = _paper()
    assert "Those 19 designs fall into two classes" in txt, (
        "the 19 are designs, not sites: they read 11 sites between them")
    assert "all nine read the same two sites" in txt, (
        "the nine intron–exon-spanning designs share two sites; saying 'nine sites' overcounts them")


def test_the_repeat_mask_baseline_is_a_band_and_the_paper_prints_that_band():
    """The masked share of SCANNED sequence cannot be a point estimate from these fields.

    A window is dropped if any of its 16 bases is ambiguous, so a maximal run of k such bases drops
    k + 15 windows: the count of dropped windows is an upper bound on the count of ambiguous bases.
    Masked bases are never ambiguous, so masked/(scanned) lies between masked/(assembly) and
    masked/(assembly − dropped windows). 52.5% of hits falls inside that band.
    """
    d = _load(GENOME)
    den = d["denominator"]
    masked, total, with_n = den["softmasked_nt"], den["total_nt"], den["windows_with_N"]
    lo = 100 * masked / total
    hi = 100 * masked / (total - with_n)
    hits = 100 * d["headline"]["stratum_4_repeat_split"]["fraction_of_hits_fully_softmasked"]
    assert lo < hits < hi, (
        f"the masked-hit share {hits:.1f}% now sits OUTSIDE the {lo:.1f}–{hi:.1f}% baseline band; "
        "§2.7 says it falls inside, and the sign of the difference is now readable")
    txt = _paper()
    assert f"{hits:.1f}% of hits fully repeat-masked" in txt
    assert f"lies between {lo:.1f}% and {hi:.1f}%" in txt, (
        f"§2.7 must print the band {lo:.1f}–{hi:.1f}%, not the whole assembly's {lo:.1f}% alone")
    assert f"{with_n:,} windows were" in txt


def test_the_alignment_screen_admits_gapped_alignments_and_the_methods_say_how_many():
    """⛔ The near-match definition is written in substitutions; `blastn` returns gaps anyway.

    ⚠ AND THE FIRST VERSION OF THIS TEST GOT THE NUMBER WRONG IN THE WAY THE LOADER EXISTS TO STOP.
    It globbed `junction-aso-offtarget-*.json`, which pools the 16-mer panel with the 18-mer and
    20-mer geometries AND with the graded re-scores of the same screens — so the same alignment was
    counted twice and three architectures were reported as one. 260/55 became 110/28 once the count
    went through `aso_screen_sets`. The pooled figure was not a rounding difference; it was a
    different population, published as this paper's.
    """
    sys.path.insert(0, MODALITIES)
    try:
        import aso_screen_sets as ass  # noqa: PLC0415
    except ImportError:
        pytest.skip("aso_screen_sets is not importable in this checkout")
    screens = ass.load_screens(ass.MANUSCRIPT_GEOMETRY, ass.BLAST_SCREEN, allow_empty=True)
    gapped = risks = 0

    def walk(node):
        nonlocal gapped, risks
        if isinstance(node, dict):
            qseq = node.get("qseq")
            if isinstance(qseq, str) and ("-" in qseq or "-" in node.get("midline", "")):
                gapped += 1
                if node.get("risk") == "true_cleavage_risk" and not node.get("is_minus_strand"):
                    risks += 1
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for screen in screens:
        walk(screen.artifact)
    assert gapped > 0, (
        "no gapped alignment is left in the released screens. If the screen was re-run ungapped, "
        "delete the §6 disclosure this guards rather than loosening this assertion")
    txt = _paper()
    assert f"{gapped} retained alignments carry a gap" in txt, (
        f"§6 screen 1 must disclose the measured gapped-alignment count, now {gapped}")
    assert f"{risks} of those are counted as sense-strand cleavage risks" in txt, (
        f"the gapped alignments counted as cleavage risks are now {risks}")


def test_the_guanine_tract_counts_beside_the_quadruplex_rule_are_measured():
    """⛔ "every design free of a G-quadruplex motif" passed 190/190 and reported nothing.

    The rule asks for four separate runs of two or more guanines. A 16-mer of this composition
    almost cannot carry that, so the column is silent by construction while the guanine feature the
    panel does carry — a 5′ G-triplet on one register of every junction, and a G5 tract at *EWSR1*
    exon 15 — went unreported. A rule that cannot fail is not evidence, and §2.10 now says so with
    the counts; this recomputes them.
    """
    import re  # noqa: PLC0415

    thermo = os.path.join(MODALITIES, "junction-aso-thermo.json")
    d = _load(thermo)
    seqs = [r["antisense_5to3"] for r in d["per_design"]]
    assert len(seqs) == 190, len(seqs)
    g3 = sum(1 for s in seqs if re.search(r"G{3,}", s))
    g3_five_prime = sum(1 for s in seqs if s.startswith("GGG"))
    g5 = [s for s in seqs if re.search(r"G{5,}", s)]
    assert d["design_rule_audit"]["n_satisfying_each"]["no_g_quadruplex_motif"] == len(seqs), (
        "the quadruplex rule now fails some design; §2.10's explanation of why it is silent no "
        "longer applies")
    txt = _paper()
    assert f"carried by {g3} of the" in txt, f"the G-triplet count is {g3}"
    assert f"5′ end in {g3_five_prime} of them" in txt, f"the 5′ G-triplet count is {g3_five_prime}"
    assert f"four registers of the *EWSR1* exon-15 junction carry a run of five" in txt, (
        f"the G5 designs are now {g5}")
    assert len(g5) == 4, g5


def test_the_corpus_median_is_the_median_and_not_the_upper_central_value():
    """⛔ §2.7 and §4.3 printed 0.98 for a median that is 0.97475.

    `sorted(v)[len(v)//2]` on an even-length list is the UPPER of the two central values, not their
    mean. `junction-aso-thermo.json` already carries a retraction for exactly this convention on
    ΔΔG — and the genome figure, quoted in two sections, had never been checked. One convention
    error, caught once, does not stay caught unless something recomputes every place it could live.
    """
    import statistics  # noqa: PLC0415

    d = _load(GENOME)
    ratios = [p["observed_over_expected"]["le2"] for p in d["per_design"]]
    median = statistics.median(ratios)
    upper_central = sorted(ratios)[len(ratios) // 2]
    assert round(median, 2) != round(upper_central, 2), (
        "the two conventions now agree, so this guard proves nothing; it is kept only while they "
        "differ — check that the population has not changed under it")
    txt = _paper()
    assert f"the median design sits at {median:.2f} of its" in txt
    assert f"corpus median of {median:.2f}" in txt or f"corpus median\nof {median:.2f}" in txt


def test_the_gc_matched_comparison_states_the_rule_it_used():
    """⛔ "Non-*TFG* designs at matched composition run at 1.04" named no matching rule.

    Three defensible readings of "matched composition" give 1.04, 1.10 and 0.89 on this artefact.
    The paper's conclusion survives all three, but a reader cannot check a number whose population
    is not written down — so the rule is in the prose now, and both endpoints are recomputed here.
    """
    d = _load(GENOME)
    per = d["per_design"]

    def is_tfg(rec):
        return any("TFG" in j for j in rec["junction_labels"])

    tfg = [p for p in per if is_tfg(p)]
    other = [p for p in per if not is_tfg(p)]

    def mean(rows):
        return sum(r["observed_over_expected"]["gap_paired_le2"] for r in rows) / len(rows)

    #: Seven of sixteen G or C is 43.75%, which the artefact records rounded to 43.8.
    band = [p for p in other if p["gc_percent"] <= 43.8]
    lo_gc, hi_gc = min(p["gc_percent"] for p in tfg), max(p["gc_percent"] for p in tfg)
    span = [p for p in other if lo_gc <= p["gc_percent"] <= hi_gc]
    txt = _paper()  # already whitespace-flattened, so the manuscript's hard wrap cannot hide a match
    assert f"the {len(band)} of the other {len(other)}" in txt, (
        f"§2.3 must name the matched band's size ({len(band)} of {len(other)})")
    assert f"run at {mean(band):.2f}" in txt, f"the GC-band figure is {mean(band):.3f}"
    assert f"the same figure is {mean(span):.2f}" in txt, (
        f"the whole-span figure is {mean(span):.3f}; §2.3 prints it so the rule's effect is visible")
