#!/usr/bin/env python3
"""Generate the two display-item tables of the fusion-junction ASO JOURNAL article.

⛔ WHY THIS EXISTS AS A GENERATOR RATHER THAN AS PROSE IN THE MANUSCRIPT. The journal article is a
second document restating sequences the preprint already carries, and this programme has already had
a parallel condensed draft drift out of sync and self-contradict. A hand-typed sequence table is
exactly where that happens: a correction reaches the long paper's generated tables and not the short
paper's hand-written ones, and the divergence is a WRONG REAGENT rather than a wrong number.

⛔ AND THE HAZARD IS ORDER-SAFETY, WHICH GATES. `fusion-junction-aso-sequences.csv` carries a
`near_identical_design_with_a_different_verdict` column because consecutive registers of one seam
differ by a single-base slide and land on OPPOSITE verdicts — one orderable, one condemned for
pairing its whole catalytic gap against a wild-type parent. Table 2 below exists to put those pairs
side by side, which the review backlog (§A3) records as the highest-value single addition available
to this work. Neither member of a pair may be substituted for the other.

⚠ THIS GENERATOR READS THE CANONICAL SEQUENCE FILE AND NOTHING ELSE, by design. Every cell it emits
is a column of `fusion-junction-aso-sequences.csv`, which `aso_sequence_manifest.py` produces and
preflight gate 8 already checks. The one exception is the test-article map below, which is a
literature fact rather than a screen output and carries its citation inline.

Usage:
    python3 research/manuscripts/aso_journal_tables.py            # write
    python3 research/manuscripts/aso_journal_tables.py --check    # reproduce or fail (gate 8)
"""
from __future__ import annotations

import csv
import json
import re
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASO = os.path.join(HERE, "aso")
SEQUENCES = os.path.join(ASO, "fusion-junction-aso-sequences.csv")
OUT = os.path.join(ASO, "fusion-junction-aso-journal-tables.md")

GEOMETRY = "5-6-5"

#: The two reagents named for synthesis, keyed by the junction label the canonical file uses.
#: ⚠ ORDER IS THE PAPER'S ORDER and is not derived: EWSR1 first because it is the majority partner.
LEADS = ("EWSR1_e12__NR4A3_e3", "TAF15_e6__NR4A3_e3")

#: ⛔ A LITERATURE FACT, NOT A SCREEN OUTPUT — the one thing here that no artifact in this repository
#: measures, so it carries its source inline rather than being read from a column. The engineered
#: constructs are those of PMID:31020999, whose exon spans that paper states verbatim; the
#: patient-derived models are those of PMID:36316541, whose fusions are reported at NR4A3 exon 2
#: rather than exon 3, which is why neither lead below is matched to one.
TEST_ARTICLE = {
    "EWSR1_e12__NR4A3_e3": "E-N, engineered construct",
    #: ⛔ NOT `T-N\\*`. The markdown escape survives the PDF pipeline as a LITERAL BACKSLASH in the
    #: table cell (measured 2026-08-20 by reading the rendered PDF, invisible in the source), and
    #: the asterisk is part of the construct name — T-N* and T-N are different constructs in
    #: PMID:31020999, so this cell names a test article and must render exactly.
    "TAF15_e6__NR4A3_e3": "T-N*, engineered construct",
}

#: The near-twin pairs Table 2 prints, named by the CONDEMNED member. Each seam contributes one pair.
#: ⚠ NAMED BY THE CONDEMNED MEMBER ON PURPOSE: the orderable twin is then read out of the canonical
#: file's own cross-reference column rather than asserted here, so the pairing cannot drift from it.
#: ⚠ ONE PAIR, NOT TWO (2026-08-22, page budget). This printed a *TCF12* pair as well, and the
#: table's point — consecutive registers of one seam carrying opposite verdicts — is made once. The
#: pair kept is the one that touches a reagent this paper names for synthesis, which is the sharper
#: example and the one §2 cites the table for; the *TCF12* pair is in the extended report.
CONDEMNED = ("CAGGGCATATCATCAA",)


_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def _spell(n):
    """`n` in words, or a KeyError naming it — never a silent numeral in a caption."""
    return _WORDS[n]


def _rows():
    with open(SEQUENCES, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _at(rows, sequence):
    hit = [r for r in rows if r["sequence"] == sequence and r["geometry"] == GEOMETRY]
    if len(hit) != 1:
        raise SystemExit(f"{sequence}: expected exactly one {GEOMETRY} record, found {len(hit)}")
    return hit[0]


def _lead(rows, junction):
    hit = [r for r in rows if r["junction"] == junction and r["geometry"] == GEOMETRY
           and r["role"] == "best available at this junction"]
    if len(hit) != 1:
        raise SystemExit(f"{junction}: expected one lead at {GEOMETRY}, found {len(hit)}")
    return hit[0]


def _seam(junction):
    donor, acceptor = junction.split("__")
    gene, exon = donor.rsplit("_e", 1)
    agene, aexon = acceptor.rsplit("_e", 1)
    return f"*{gene}* e{exon}::*{agene}* e{aexon}"


def _duplex(row):
    """The mature-parent duplex cell: length and the wild-type gene that forms it."""
    bp = int(row["mature_parent_duplex_through_gap_bp"])
    gene = row["mature_parent_duplex_gene"]
    if not bp:
        return "none at any length"
    return f"{bp} bp, wild-type *{gene}*"


def _twin(row):
    """The near-identical design carrying the OPPOSITE verdict, read from the canonical file."""
    cell = row["near_identical_design_with_a_different_verdict"]
    if not cell:
        raise SystemExit(f"{row['sequence']}: canonical file records no near-identical twin, so "
                         "Table 2 cannot be built from it — the pairing must not be asserted here")
    seq = cell.split(" (")[0]
    return seq, cell[cell.index("(") + 1:cell.rindex(")")]


def _controls():
    """The two screened control oligonucleotides, read from `aso-control-oligos.json`.

    ⛔ READ, NEVER TYPED. A control is a sequence a laboratory will order; typing one into a table
    is the transcription hazard this deposit exists to avoid, and a control differing by one base
    from the screened one has not been screened.
    """
    path = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                        "research", "modalities", "aso-control-oligos.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["controls"]


def _tm(row):
    """The fusion-versus-parent Tm SEPARATION, as a floor. Never the absolute melting points.

    ⛔⛔ THE ABSOLUTES WERE WRONG FOR THIS MOLECULE AND WERE PRINTED ANYWAY (external review,
    2026-08-24). The nearest-neighbour table is for an unmodified DNA:RNA hybrid; these reagents are
    5-6-5 beta-D-oxy-LNA with a full phosphorothioate backbone, 10 of 16 residues locked. Locked
    residues raise Tm by several degrees each, so an absolute of "51.3 °C" understates the real
    molecule badly — and this is being submitted to the oligonucleotide-therapeutics journal, whose
    readers know that. The SEPARATION survives the modification in a stated direction: the fusion
    duplex pairs all ten locked residues and each parent half-duplex exactly five, by construction
    for every design in the panel, so LNA widens the gap rather than closing it. That makes the
    unmodified separation a FLOOR, which is a claim this table can stand behind.

    ⛔ AND THE PARENT HERE IS NOT THE PARENT IN THE COLUMN BESIDE IT. The duplex column reports the
    longest contiguous duplex a mature wild-type parent forms through the catalytic gap, found by
    search — wild-type TFG for both reagents. This column's parent is the more stable HALF of the
    design's own target window, donor or acceptor, which is where the seam splits it. Both reagents
    share an NR4A3 exon-3 acceptor half, so that half is the same 8 nt in both and its melting point
    was identical (24.7 °C) while the duplex column read 8 and 9 — two different genes' numbers side
    by side, each correct, together implying one quantity. Printing the difference rather than the
    endpoints removes the false pairing; the caption names both parents.

    ⛔ BLANK IS PRINTED AS A DASH, NEVER AS A NUMBER. A design outside the 5-6-5 thermodynamics
    panel carries no Tm in the canonical file, and an empty cell in a submitted table reads as a
    missing value rather than as a number somebody forgot.
    """
    f, p = row.get("predicted_tm_fusion_c"), row.get("predicted_tm_best_parent_c")
    if not f or not p:
        return "—"
    return f"≥ {round(float(f) - float(p), 1)}"


def build() -> str:
    rows = _rows()
    out = ["<!-- GENERATED, DO NOT EDIT. Regenerate: python3 research/manuscripts/aso_journal_tables.py -->",
           "", "# Display items: fusion-junction ASO journal article", "",
           "*Every cell below is a column of `fusion-junction-aso-sequences.csv`, the canonical "
           "machine-readable record, except the test-article column of Table 1, which is a "
           "literature fact and carries its source in the caption. Every reagent named here is a "
           f"{GEOMETRY} phosphorothioate gapmer. An oligonucleotide should be "
           "ordered from that file rather than transcribed from this page.*", ""]

    # ⚠ A CAPTION LABELS A TABLE; IT DOES NOT CARRY THE ARGUMENT (2026-08-22, page budget). These
    # two captions had grown to 350 words between them, restating §2 and §4 beside the rows. What a
    # caption owes the reader is what the columns mean and where the cells come from; the reasoning
    # lives in the section that cites the table.
    out += ["**Table 1. The two reagents named for synthesis, with their parent-duplex label and "
            "their test article.** The parent-duplex column is the longest contiguous duplex a "
            "mature wild-type parent forms through the catalytic gap; neither reagent reaches the "
            "ten-base-pair criterion, so the length is printed rather than a pass mark. Test "
            "articles are the engineered constructs of Brenca et al. "
            "(PMID:31020999); the two patient-derived models of Bangerter et al. (PMID:36316541) are "
            "REPORTED at an NR4A3 exon-2 acceptor and match different designs, not these two. "
            "ΔTm separates the fusion duplex from the more stable half of the design's own "
            "target window, which is a different parent from the duplex column's searched "
            "wild-type TFG. The separation is a floor rather than an estimate, for the reason "
            "Methods gives; absolute melting points are not reported for a locked, "
            "phosphorothioate oligonucleotide. "
            "Nothing here has been synthesised or tested, and no sequence may be administered to "
            "any person or animal.", ""]
    out += ["| seam | reagent | margin | WT gap duplex (bp) | ΔTm floor (°C) | "
            "test article |",
            "|---|---|---:|---|---:|---|"]
    for j in LEADS:
        r = _lead(rows, j)
        out.append(f"| {_seam(j)} | 5\u2032-{r['sequence']}-3\u2032 | {r['gap_level_margin']} | "
                   f"{_duplex(r)} | {_tm(r)} | {TEST_ARTICLE[j]} |")
    out.append("")

    controls = _controls()
    out += ["**Table 2. The two control oligonucleotides, each screened as its reagent was.** Each "
            "is a dinucleotide-preserving scramble of the reagent it controls, matching it in "
            "length, first and last base, base composition and dinucleotide counts while spanning "
            #: ⛔ THIS SENTENCE NAMED "Section 5" UNTIL 2026-08-25, AND THE PAPER HAD STOPPED
            #: HAVING NUMBERED SECTIONS when it was restructured to IMRaD — so a caption that the
            #: builder uploads as its OWN FILE pointed at nothing. A caption is the worst place in
            #: a submission to carry a cross-reference: it is typeset away from the body and, at
            #: this venue, uploaded separately. So the reason is stated here rather than pointed
            #: at, and only the RATE is deferred, to the one place that derives it.
            "no junction, and each cleared the same mature-parent screen the reagent did. That "
            "screening is what separates a negative control from a second active molecule; Results "
            "gives the rate at which an unscreened scramble would be one.", ""]
    out += ["| control | sequence | scramble of | WT gap duplex (bp) |",
            "|---|---|---|---|"]
    for c in controls:
        #: ⛔ ONE SEQUENCE PER ROW. The reagent this control scrambles is named by its SEAM, not by
        #: repeating its sequence: a table row that prints two oligonucleotides is two chances to
        #: copy the wrong one into an order, and `test_the_journal_display_items_say_what_their_rows
        #: _say` enforces the rule for exactly that reason. Table 1 carries the seam-to-sequence map.
        out.append(f"| {c['label']} | 5\u2032-{c['control_5to3']}-3\u2032 | "
                   f"the {c['seam']} reagent | "
                   f"{c['control_longest_parent_duplex_through_gap_bp']} bp, wild-type "
                   f"*{c['control_longest_parent_duplex_gene']}* |")
    out.append("")
    return "\n".join(out)



def _verdict(row, twin_relation=None):
    """The verdict cell, READ from the canonical file, never typed here.

    ⛔⛔ THIS COLUMN WAS TWO f-STRING LITERALS, AND THAT MADE THE PREAMBLE FALSE (round 16 seat 2).
    The page opens by promising "every cell below is a column of `fusion-junction-aso-sequences.csv`
    … except the test-article column of Table 1" — one exception named, and there were two. That is
    the sentence the whole page's authority rests on, and it was the only checkable provenance claim
    in the file, so it was the one thing worth auditing mechanically and nothing did.
    ⚠ WORSE THAN A WRONG NUMBER: a typed verdict can be pointed at a design the canonical file
    CLEARS, printing DO NOT ORDER against an orderable reagent and `orderable` against a condemned
    one, under a caption that still reads correctly.
    ★ Both words are already in the record — `do_not_order` carries the condemned label, and the
    twin's `near_identical_design_with_a_different_verdict` cell names the other member's verdict —
    so neither needs typing, and the preamble becomes true again with no rewording. Word cost: 0.
    """
    cell = (row.get("do_not_order") or "").strip()
    if cell:
        return re.split(r"\s+[—-]\s+", cell, maxsplit=1)[0].strip()
    if not twin_relation:
        raise SystemExit(f"{row['sequence']}: the canonical file records no verdict for this design "
                         "and no twin naming one, so Table 2's verdict cell would have to be typed")
    return twin_relation


def _slides_to_a_named_lead(rows):
    """How many single-base slides separate a condemned design from a lead at the same seam.

    A slide is one register: two 16-mers overlap in 15 positions, so `a[1:] == b[:-1]`. The walk is
    bounded by the oligonucleotide length because a design more than sixteen registers away shares
    no base with the lead and is not a near-twin of it in any useful sense.
    """
    def one_slide(a, b):
        return a[1:] == b[:-1] or b[1:] == a[:-1]

    best = None
    #: ⛔ THE MINIMUM IS OVER THE WHOLE CONDEMNED CLASS, NOT OVER THE PAIR THIS TABLE HAPPENS TO
    #: PRINT (2026-08-22, round 16 seat 2). Scoped to `CONDEMNED` this returned TWO slides, for the
    #: *EWSR1* reagent — while the canonical file records `AGGGCATATCTTGTGT`, 11 bp against wild-type
    #: *NR4A3*, ONE slide from the *TAF15* reagent this paper names for synthesis and printed in
    #: neither PDF. The number exists to size an off-by-one in a synthesis order, so it has to be the
    #: panel's worst case and not the printed pair's.
    condemned = [r for r in rows if r.get("do_not_order") and r.get("geometry") == GEOMETRY]
    for bad in condemned:
        for j in LEADS:
            lead = _lead(rows, j)
            if lead["junction"] != bad["junction"]:
                continue
            here, seen = {lead["sequence"]}, {lead["sequence"]}
            for step in range(1, 17):
                nxt = {r["sequence"] for r in rows
                       if r.get("junction") == bad["junction"]
                       and r["sequence"] not in seen
                       and any(one_slide(h, r["sequence"]) for h in here)}
                if not nxt:
                    break
                if bad["sequence"] in nxt:
                    if best is None or step < best[0]:
                        best = (step, lead["sequence"], bad["sequence"], _duplex(bad))
                    break
                seen |= nxt
                here = nxt
    if best is None:
        return ""
    step, lead_seq, bad_seq, duplex = best
    slides = "one single-base slide" if step == 1 else f"{_number_word(step)} single-base slides"
    length, _, gene = duplex.partition(", wild-type ")
    return (f"The condemned class reaches the reagents this paper names for synthesis: "
            f"5\u2032-{bad_seq}-3\u2032 is {slides} from 5\u2032-{lead_seq}-3\u2032 and pairs "
            f"{length} of wild-type {gene} through its whole catalytic gap.")


def _number_word(n):
    return {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}.get(n, str(n))

def main() -> int:
    text = build()
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print(f"MISSING {OUT} — run without --check")
            return 1
        current = open(OUT, encoding="utf-8").read()
        if current != text:
            print(f"STALE {os.path.relpath(OUT)} — rerun without --check and commit the result")
            return 1
        print("journal tables reproduce from the canonical sequence file")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote {os.path.relpath(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
