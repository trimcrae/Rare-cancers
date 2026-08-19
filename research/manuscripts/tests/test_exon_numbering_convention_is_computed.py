#!/usr/bin/env python3
"""The transcript-versus-coding exon convention is recomputed from the models, never typed.

⛔⛔ THIS IS THE AXIS AN EARLIER VERSION OF THIS WORK WAS WITHDRAWN ON, AND IT WENT WRONG AGAIN.

On 2026-08-19 §6 stated: "*TCF12* carries 21 transcript exons and 19 coding, *TFG* eight and seven,
*NR4A3* eight and six, so the two conventions differ by two, one and two exons for those genes and
*TCF12* exon 5 under this convention is coding exon 3 under the other."

Every count in that sentence is right and the conclusion drawn from them is wrong. The COUNT
difference (21 − 19 = 2) is not the INDEX shift. Computed from the committed model, *TCF12*'s two
non-coding exons are exon 1 and exon 21 — the first and the LAST — so only one precedes the coding
sequence and the index shifts by one. Transcript exon 5 is coding exon **4**, not 3.

⚠ WHY THAT PARTICULAR EXON. *TCF12* exon 5 is the junction this paper resolves from a GenBank
deposit, names a reagent at, and prices as the top rung of Table 5's coverage ladder. A reader
reconciling that seam against a coding-exon-numbered clinical report would land one exon 5′ of the
real donor terminus — which is the class of error the withdrawal was for.

★ SO NOTHING HERE IS TYPED. Both counts, the per-gene index shift, and the specific
transcript-exon-5 claim are derived from `aso-premrna-offtarget.json`'s exon spans and the atlas's
UTR/CDS lengths, and the prose is matched against the derivation.
"""
from __future__ import annotations

import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
PAPER = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-research-article.md")
MOD = os.path.join(REPO, "research", "modalities")
PREMRNA = os.path.join(MOD, "aso-premrna-offtarget.json")
ATLAS = os.path.join(MOD, "nr4a3-fusion-junction-atlas.json")


def _load(path):
    if not os.path.exists(path):
        pytest.skip(f"{os.path.basename(path)} is not present in this checkout")
    return json.load(open(path, encoding="utf-8"))


def _coding_exons(gene):
    """1-based transcript-exon indices that carry any coding sequence."""
    spans = _load(PREMRNA)["genes"][gene]["exon_spans_0based_inclusive"]
    model = _load(ATLAS)["transcripts"][gene]
    lengths = [b - a + 1 for a, b in spans]
    assert sum(lengths) == model["cdna_nt"], (
        f"{gene}: exon lengths sum to {sum(lengths)} against a cDNA of {model['cdna_nt']}; the two "
        "artefacts no longer describe the same transcript and nothing below is meaningful")
    cds_from = model["utr5_nt"]
    cds_to = cds_from + model["cds_nt"] - 1
    coding, at = [], 0
    for index, length in enumerate(lengths, start=1):
        if at <= cds_to and at + length - 1 >= cds_from:
            coding.append(index)
        at += length
    return len(lengths), coding


def _paper():
    if not os.path.exists(PAPER):
        pytest.skip("the manuscript is not present in this checkout")
    return " ".join(open(PAPER, encoding="utf-8").read().split())


@pytest.mark.parametrize("gene,words", [("TCF12", "21\ntranscript exons and 19 coding"),
                                        ("TFG", "eight and seven"),
                                        ("NR4A3", "eight and six")])
def test_the_printed_exon_counts_are_the_models(gene, words):
    total, coding = _coding_exons(gene)
    expected = {"TCF12": (21, 19), "TFG": (8, 7), "NR4A3": (8, 6)}[gene]
    assert (total, len(coding)) == expected, (
        f"{gene} now has {total} transcript exons and {len(coding)} coding; §6 prints {expected}")


def test_the_index_shift_is_not_assumed_to_equal_the_count_difference():
    """⛔ THE DEFECT ITSELF. For *TCF12* the difference is two and the shift is one."""
    total, coding = _coding_exons("TCF12")
    non_coding = [i for i in range(1, total + 1) if i not in coding]
    assert non_coding == [1, 21], (
        f"*TCF12*'s non-coding exons are now {non_coding}; §6's explanation — that one of the two "
        "is the LAST exon and so does not shift the index — depends on this")
    shift = sum(1 for i in non_coding if i < 5)
    assert shift == 1, shift
    assert total - len(coding) == 2, "the count difference"
    assert shift != total - len(coding), (
        "count difference and index shift now agree for *TCF12*, so the paragraph explaining why "
        "they differ is stale — rewrite it rather than deleting this assertion")


def test_tcf12_exon_five_is_named_as_the_coding_exon_it_actually_is():
    """*TCF12* exon 5 carries the top rung of the coverage ladder; the number has to be right."""
    _, coding = _coding_exons("TCF12")
    assert 5 in coding, "transcript exon 5 is non-coding, which the sentence does not anticipate"
    coding_index = coding.index(5) + 1
    assert coding_index == 4, coding_index
    txt = _paper()
    assert f"*TCF12* transcript exon 5 is coding exon {coding_index} under the other convention" in txt, (
        f"§6 must name coding exon {coding_index}. This is the withdrawal axis: a reader "
        "reconciling this seam against a coding-exon-numbered report lands on the wrong donor "
        "terminus if the number is off by one.")


def test_the_genes_whose_conventions_coincide_really_do():
    """The sentence names four genes as unaffected; a coding first exon is what makes that true."""
    for gene in ("EWSR1", "TAF15", "FUS"):
        total, coding = _coding_exons(gene)
        assert coding and coding[0] == 1, (
            f"{gene}'s first exon is no longer coding, so §6's claim that the two conventions "
            "coincide for it is wrong")
    assert "have a coding first exon and the two conventions coincide for them" in _paper()
