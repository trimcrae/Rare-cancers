"""⛔ A SEQUENCE PRINTED WITH AN EXON IS AN ORDER, AND THE CANONICAL FILE DECIDES WHICH EXON.

This paper's central warning is that a reagent selected for one acceptor is not valid for the other,
and it says so in the same paragraph in which it names reagents. Until 2026-08-22 every named
reagent in §4 was labelled by DONOR exon alone — "5′-AGTGGGCTCTCCACGG-3′ at *EWSR1* exon 13" — in
the one paragraph whose subject is that the ACCEPTOR index is unsettled. Both were joined to *NR4A3*
exon 2 and the text said "Reagents exist at both acceptors" immediately before naming them, so a
reader took the pair as covering both readings.

⛔ AND ONE LABEL NAMED TWO MOLECULES. "*TAF15* exon 6" is §2's `GGGCATATCTTGTGTG`, joined to exon 3,
AND §4's `AGTGGGCTCTTGTGTG`, joined to exon 2 — a different molecule at a different acceptor, in a
paper that says substituting one for the other is the error class its own withdrawn version arose
from.

★ THE CHECK IS AGAINST THE CANONICAL FILE, NEVER AGAINST THE OTHER DOCUMENT. Every sequence the
manuscripts print is a row of `fusion-junction-aso-sequences.csv`, whose `junction` column carries
both exons. This guard reads that column and asks whether the sentence around the sequence agrees
with it — so a design that moves seams cannot leave a stale exon standing beside it.
"""
from __future__ import annotations

import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
SEQ_CSV = os.path.join(ASO, "fusion-junction-aso-sequences.csv")

#: Both manuscripts, because a sequence printed in either is a sequence someone can order.
PAPERS = ("fusion-junction-aso-journal-article.md",
          "fusion-junction-aso-journal-tables.md")

#: `EWSR1_e13__NR4A3_e2` -> ("EWSR1", "13", "NR4A3", "2")
_JUNCTION = re.compile(r"^([A-Z0-9]+)_e(\d+)__([A-Z0-9]+)_e(\d+)$")


def _rows():
    with open(SEQ_CSV, encoding="utf-8") as fh:
        rows = list(csv.DictReader(ln for ln in fh if not ln.startswith("#")))
    assert rows, f"{SEQ_CSV} carries no rows"
    return rows


def _by_sequence():
    out = {}
    for r in _rows():
        m = _JUNCTION.match(r["junction"] or "")
        if m:
            out.setdefault(r["sequence"], set()).add(m.groups())
    return out


def _flat(path):
    with open(path, encoding="utf-8") as fh:
        return re.sub(r"[*_`]", "", " ".join(fh.read().split()))


def _attributions(text, seq, span=160):
    """The clause that attributes `seq`, stopping before the NEXT sequence.

    ⚠ THE WINDOW MUST END AT THE NEXT 5′, AND THE FIRST DRAFT OF THIS FILE DID NOT DO THAT. Reagents
    are printed in pairs — "5′-A-3′ at EWSR1 exon 12 and 5′-B-3′ at TAF15 exon 6" — so a fixed-width
    window after A reaches into B's attribution and reports A as printed at B's exon. It filed three
    such findings against correct prose, which is the false-positive direction that gets a guard
    switched off rather than obeyed.
    """
    for m in re.finditer(re.escape(seq) + r"-3′?", text):
        tail = text[m.end(): m.end() + span]
        tail = re.split(r"5′|[.;:]", tail, maxsplit=1)[0]
        yield tail


def test_no_printed_sequence_is_given_an_exon_its_own_row_contradicts():
    """⛔ THE EXON BESIDE A SEQUENCE, AGAINST THE EXON IN ITS ROW."""
    known = _by_sequence()
    wrong = []
    for name in PAPERS:
        path = os.path.join(ASO, name)
        if not os.path.exists(path):
            continue
        text = _flat(path)
        for seq, junctions in known.items():
            # every "…SEQ…" followed, within one clause, by a "<GENE> exon <n>" attribution
            for tail in _attributions(text, seq):
                for gene, exon in re.findall(r"\b([A-Z][A-Z0-9]{2,})\s+exon\s+(\d+)", tail):
                    ok = any((gene == d and exon == de) or (gene == a and exon == ae)
                             for d, de, a, ae in junctions)
                    if not ok:
                        seams = ", ".join(f"{d} e{de}::{a} e{ae}" for d, de, a, ae in sorted(junctions))
                        wrong.append(f"{name}: {seq} is printed at {gene} exon {exon}; "
                                     f"the canonical file puts it at {seams}")
    assert not wrong, (
        "a manuscript prints a sequence beside an exon that is not one of its own:\n  "
        + "\n  ".join(wrong)
        + "\n\nfusion-junction-aso-sequences.csv is the file a laboratory orders from, and its "
          "`junction` column is the answer. Fix the sentence, never the CSV.")


def test_a_donor_exon_label_that_names_two_molecules_is_disambiguated():
    """⛔ ONE LABEL, ONE MOLECULE — OR THE ACCEPTOR HAS TO BE SAID.

    "TAF15 exon 6" is a complete address only if this paper prints one reagent there. It prints two,
    at different acceptors. Wherever a donor label is shared, every sentence naming a sequence under
    it must also name that sequence's acceptor exon, because the paper's own rule is that a reagent
    selected for one acceptor is not valid for the other.
    """
    known = _by_sequence()
    by_donor = {}
    for seq, junctions in known.items():
        for d, de, a, ae in junctions:
            by_donor.setdefault((d, de), set()).add((seq, a, ae))
    shared = {k: v for k, v in by_donor.items() if len({(a, ae) for _s, a, ae in v}) > 1}

    unaddressed = []
    for name in PAPERS:
        path = os.path.join(ASO, name)
        if not os.path.exists(path):
            continue
        text = _flat(path)
        for (donor, dexon), members in sorted(shared.items()):
            for seq, acc, aexon in sorted(members):
                for tail in _attributions(text, seq):
                    if not re.search(rf"\b{donor}\s+exon\s+{dexon}\b", tail):
                        continue  # not labelled by the shared donor here
                    if not re.search(rf"exon\s+{aexon}\b", tail):
                        unaddressed.append(
                            f"{name}: {seq} is labelled '{donor} exon {dexon}', which this paper "
                            f"also uses for a different molecule at another acceptor, and its own "
                            f"acceptor ({acc} exon {aexon}) is not named in the same clause")
    assert not unaddressed, (
        "a shared donor label is printed without the acceptor that distinguishes the molecule:\n  "
        + "\n  ".join(unaddressed)
        + "\n\nThis paper states that substituting a reagent across acceptors is the error class "
          "its own withdrawn version arose from. A label that names two molecules is that "
          "substitution waiting to happen.")
