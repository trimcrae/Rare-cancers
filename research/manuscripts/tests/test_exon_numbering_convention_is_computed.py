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

⛔ REPAIRED 2026-08-19 (lane C-b). Three defects in this file, each of which let the axis go
unguarded:

  1. `test_the_printed_exon_counts_are_the_models` NEVER OPENED THE MANUSCRIPT. Its `words`
     parametrize argument was unreferenced — and one value carried a literal newline that could
     never have matched the flattened text anyway. It compared the model against a dict typed three
     lines below it, so it asserted only that a hard-coded triple equalled itself plus the model.
     The prose it exists to police was never read. It now PARSES the §6 sentence and matches every
     printed pair against the model, and requires the sentence to name exactly the genes whose two
     conventions actually differ — so a fourth diverging gene cannot be omitted.
  2. `test_the_index_shift_is_not_assumed_to_equal_the_count_difference` ended in a TAUTOLOGY:
     having asserted `shift == 1` and `total - len(coding) == 2` it then asserted `shift != …`,
     which 1 ≠ 2 already guarantees. Replaced by the per-gene shifts the paragraph actually claims
     — *TCF12* one against a difference of two, *TFG* one, *NR4A3* two — each derived and each
     matched against the printed number.
  3. `test_the_genes_whose_conventions_coincide_really_do` asserted three genes where the sentence
     names FOUR. *PGR* was in neither artifact this file read, so the fourth name in a §6 sentence
     about exon numbering was covered by nothing. *PGR* IS in `emc-construct-inputs.json`, a
     retrieved artifact (`pgr_transcript_fetch.py`, 2026-08-15) that carries the per-exon coding
     content of ENST00000325455 — the same accession §6 names. That artifact reproduces the other
     six genes' counts exactly, which is the reason it can be trusted for the seventh, and the
     agreement is asserted here rather than assumed.
"""
from __future__ import annotations

import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
PAPER = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-research-article.md")
MOD = os.path.join(REPO, "research", "modalities")
PREMRNA = os.path.join(MOD, "aso-premrna-offtarget.json")
ATLAS = os.path.join(MOD, "nr4a3-fusion-junction-atlas.json")
#: ⭐ THE ONLY ARTIFACT IN THIS REPOSITORY CARRYING *PGR*'s EXON STRUCTURE. Retrieved from Ensembl
#: by research/modalities/pgr_transcript_fetch.py; every gene in it records `is_coding` per
#: transcript exon, so nothing below has to type an exon coordinate.
CONSTRUCT = os.path.join(MOD, "emc-construct-inputs.json")


def _load(path):
    if not os.path.exists(path):
        # ⛔ NOT A SKIP. A missing model is the state in which every claim in §6 is unchecked, which
        # is exactly when this guard has to speak. Skipping would report PASS on the withdrawal axis.
        pytest.fail(f"{os.path.basename(path)} is missing; §6's exon-numbering claims are unchecked")
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


def _construct_exons(gene):
    """(n_transcript_exons, coding indices) for any gene of the construct-input artifact."""
    genes = _load(CONSTRUCT)["genes"]
    assert gene in genes, (
        f"{gene} is not in emc-construct-inputs.json, so §6's claim about its exon numbering rests "
        "on no committed model. Add a retrieved record for it — never type an exon coordinate.")
    exons = genes[gene]["exons"]
    return len(exons), [e["transcript_exon_rank"] for e in exons if e["is_coding"]]


def _paper():
    if not os.path.exists(PAPER):
        pytest.fail("the manuscript is missing; §6's exon-numbering claims are unchecked")
    return " ".join(open(PAPER, encoding="utf-8").read().split())


# ── reading numbers the way §6 writes them ───────────────────────────────────────────────────
#
# The sentence mixes digits and number words in one breath ("21 transcript exons and 19 coding,
# *TFG* eight and seven"), so the parser has to take both or it silently matches half the claim.

_WORDS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
          "fifteen sixteen seventeen eighteen nineteen twenty twenty-one twenty-two twenty-three "
          "twenty-four twenty-five").split()
_NUMBER = r"(?:\d+|" + "|".join(reversed(_WORDS)) + r")"


def _n(token):
    token = token.strip().lower()
    return int(token) if token.isdigit() else _WORDS.index(token)


def _divergent_genes():
    """Genes of the model whose transcript and coding numbering do NOT coincide, and by how much.

    Two conventions coincide exactly when no non-coding exon precedes a coding one. Where they
    differ, the index shift is the count of non-coding exons ahead of the coding sequence — which
    is NOT the count difference, and is the whole point of the paragraph this guards.
    """
    out = {}
    for gene in sorted(_load(PREMRNA)["genes"]):
        total, coding = _coding_exons(gene)
        shift = sum(1 for i in range(1, coding[0]) if i not in coding)
        if shift:
            out[gene] = {"total": total, "coding": len(coding), "shift": shift,
                         "non_coding": [i for i in range(1, total + 1) if i not in coding]}
    return out


def test_the_printed_exon_counts_are_the_models():
    """⛔ THE SENTENCE IS READ. Every printed pair is matched, and the gene set is derived.

    §6 prints "*TCF12* carries 21 transcript exons and 19 coding, *TFG* eight and seven, *NR4A3*
    eight and six" — one leading clause and then an elliptical list. Both forms are parsed, so a
    gene moved between them stays covered.
    """
    txt = _paper()
    where = re.search(r"\*(\w+)\* carries " + _NUMBER + r" transcript exons and " + _NUMBER
                      + r" coding", txt)
    assert where, (
        "§6's exon-count sentence ('*GENE* carries N transcript exons and M coding') is gone. It is "
        "the only place the paper states the two conventions numerically; re-anchor this guard on "
        "whatever sentence replaces it rather than deleting it — this is the withdrawal axis.")
    sentence = txt[where.start():txt.index(".", where.start()) + 1]

    printed = {}
    lead = re.search(r"\*(\w+)\* carries (" + _NUMBER + r") transcript exons and (" + _NUMBER
                     + r") coding", sentence)
    printed[lead.group(1)] = (_n(lead.group(2)), _n(lead.group(3)))
    for gene, total, coding in re.findall(
            r"\*(\w+)\* (" + _NUMBER + r") and (" + _NUMBER + r")\b", sentence):
        printed[gene] = (_n(total), _n(coding))

    model = _divergent_genes()
    assert set(printed) == set(model), (
        f"§6's exon-count sentence names {sorted(printed)}; the committed models say the two "
        f"conventions differ for {sorted(model)}. A gene whose numbering diverges and is not named "
        "here is the withdrawal defect exactly.")
    for gene, (total, coding) in sorted(printed.items()):
        assert (total, coding) == (model[gene]["total"], model[gene]["coding"]), (
            f"§6 prints {gene} as {total} transcript exons and {coding} coding; the model gives "
            f"{model[gene]['total']} and {model[gene]['coding']}.")


def test_the_index_shift_is_not_assumed_to_equal_the_count_difference():
    """⛔ THE DEFECT ITSELF. For *TCF12* the difference is two and the shift is one.

    ⚠ The last assertion here used to be `shift != total - len(coding)` after both had been pinned
    to 1 and 2 — true by arithmetic, checkable by nothing. What replaces it reads the two numbers
    §6 actually prints for this gene and matches each against its own derivation.
    """
    total, coding = _coding_exons("TCF12")
    non_coding = [i for i in range(1, total + 1) if i not in coding]
    assert non_coding == [1, 21], (
        f"*TCF12*'s non-coding exons are now {non_coding}; §6's explanation — that one of the two "
        "is the LAST exon and so does not shift the index — depends on this")
    shift = sum(1 for i in non_coding if i < 5)
    difference = total - len(coding)

    printed = re.search(r"the index shifts by (" + _NUMBER + r") rather than by (" + _NUMBER + r")",
                        _paper())
    assert printed, (
        "§6 no longer states the *TCF12* index shift against the count difference ('the index "
        "shifts by X rather than by Y'). That contrast IS the correction the withdrawal produced.")
    assert (_n(printed.group(1)), _n(printed.group(2))) == (shift, difference), (
        f"§6 prints a shift of {_n(printed.group(1))} against a difference of "
        f"{_n(printed.group(2))}; derived from the model they are {shift} and {difference}.")


def test_the_per_gene_shifts_of_the_other_two_divergent_genes_are_the_models():
    """*TFG* and *NR4A3* are printed as shifting by one and by two, with a reason attached.

    Their shifts are constant across the transcript only because every non-coding exon precedes the
    coding sequence — which is what §6 asserts of them, and is false of *TCF12*. So the structural
    property is checked (all non-coding exons ahead of the first coding one) before the numbers.
    """
    model = _divergent_genes()
    printed = re.search(r"\*(\w+)\* shifts by (" + _NUMBER + r") and \*(\w+)\* by (" + _NUMBER + r")",
                        _paper())
    assert printed, (
        "§6 no longer prints the per-gene index shifts ('*TFG* shifts by one and *NR4A3* by two'). "
        "The count difference is not the shift, so a reader given only the counts cannot recover "
        "them.")
    for gene, value in ((printed.group(1), _n(printed.group(2))),
                        (printed.group(3), _n(printed.group(4)))):
        assert gene in model, f"§6 gives an index shift for {gene}, whose conventions coincide"
        total, coding = _coding_exons(gene)
        assert max(i for i in model[gene]["non_coding"]) < min(coding), (
            f"{gene} now has a non-coding exon AFTER its coding sequence, so its index shift is no "
            "longer one number for the whole transcript and §6's clause 'their non-coding exons all "
            "preceding the coding sequence' is false")
        assert value == model[gene]["shift"], (
            f"§6 prints an index shift of {value} for {gene}; the model gives {model[gene]['shift']}")


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


def test_the_construct_input_models_reproduce_the_screen_models():
    """The *PGR* arm below rests on a second artifact, so the two must agree where both can speak.

    `emc-construct-inputs.json` is retrieved per gene and records `is_coding` per exon;
    `aso-premrna-offtarget.json` + the atlas derive the same thing from spans and UTR/CDS lengths.
    Six genes are in both. If they ever disagree, the *PGR* reading has no standing either.
    """
    for gene in sorted(_load(PREMRNA)["genes"]):
        total, coding = _coding_exons(gene)
        c_total, c_coding = _construct_exons(gene)
        assert (total, coding) == (c_total, c_coding), (
            f"{gene}: the screen models give {total} exons with coding {coding}; "
            f"emc-construct-inputs.json gives {c_total} with coding {c_coding}. Until they agree, "
            "no exon-numbering claim in §6 has one source.")


def test_the_genes_whose_conventions_coincide_really_do():
    """The sentence names four genes as unaffected; a coding first exon is what makes that true.

    ⛔ *PGR* USED TO BE IN THE SENTENCE AND IN NEITHER ARTIFACT THIS FILE READ. It is the donor of
    the one seam of §2.6 outside the five modelled partners, and §6 gives ENST00000325455 for it,
    so a reader reconciling a *PGR*-numbered report is relying on this clause. Its exon structure
    is read from `emc-construct-inputs.json`, and the gene list is DERIVED — a gene that stopped
    coinciding would have to leave the sentence.
    """
    construct = _load(CONSTRUCT)["genes"]
    coincide = set()
    for gene in construct:
        total, coding = _construct_exons(gene)
        if coding and all(i > max(coding) for i in range(1, total + 1) if i not in coding):
            coincide.add(gene)

    txt = _paper()
    tail = "have a coding first exon and the two conventions coincide for them"
    at = txt.find(tail)
    assert at != -1, (
        "§6's 'have a coding first exon and the two conventions coincide for them' clause is gone. "
        "It is the only statement telling a reader which genes need no reconciliation at all.")
    # The subject is the run of emphasised gene names immediately before the verb — taken as a run
    # so that adding or dropping a name changes what this reads, rather than a fixed arity.
    subject = re.search(r"((?:\*\w+\*(?:,\s*|\s+and\s+|\s+))+)$", txt[:at])
    assert subject, f"§6's coincidence clause has no gene list before it: …{txt[max(0, at - 90):at]!r}"
    named = set(re.findall(r"\*(\w+)\*", subject.group(1)))
    assert named == coincide, (
        f"§6 names {sorted(named)} as genes whose two exon conventions coincide; derived from the "
        f"committed models the set is {sorted(coincide)}. A gene named here whose first exon is "
        "non-coding sends a reader to the wrong exon, and one omitted leaves a reconciliation "
        "nobody needed.")
    for gene in sorted(named):
        total, coding = _construct_exons(gene)
        assert coding and coding[0] == 1, (
            f"{gene}'s first exon is no longer coding, so §6's claim that the two conventions "
            "coincide for it is wrong")
