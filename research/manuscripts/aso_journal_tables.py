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


def build() -> str:
    rows = _rows()
    out = ["<!-- GENERATED — DO NOT EDIT. Regenerate: python3 research/manuscripts/aso_journal_tables.py -->",
           "", "# Display items — fusion-junction ASO journal article", "",
           "*Every cell below is a column of `fusion-junction-aso-sequences.csv`, the canonical "
           "machine-readable record, except the test-article column of Table 1, which is a "
           "literature fact and carries its source in the caption. An oligonucleotide should be "
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
            "Nothing here has been synthesised or tested, and no sequence may be administered to "
            "any person or animal.", ""]
    out += ["| seam | reagent | margin | WT gap duplex (bp) | test article |",
            "|---|---|---:|---|---|"]
    for j in LEADS:
        r = _lead(rows, j)
        out.append(f"| {_seam(j)} | 5′-{r['sequence']}-3′ | {r['gap_level_margin']} | "
                   f"{_duplex(r)} | {TEST_ARTICLE[j]} |")
    out.append("")

    #: ⭐ HOW FAR THE NEAREST CONDEMNED DESIGN SITS FROM A REAGENT WE TELL PEOPLE TO BUY, DERIVED
    #: RATHER THAN TYPED. The caption used to say only that these are "not a reagent this paper
    #: names", which is true and reads as reassurance. It is the opposite: one of the condemned
    #: designs is a register of the SAME seam as a named lead, so the distance between the molecule
    #: to order and a molecule that pairs its whole catalytic gap against wild-type NR4A3 is a
    #: countable number of single-base slides. That number is what makes an off-by-one in a
    #: synthesis order a real hazard rather than a hypothetical one, so it is computed here from the
    #: sequences themselves and cannot drift from them.
    near = _slides_to_a_named_lead(rows)
    #: ⛔⛔ THE CAPTION COUNTS THE ROWS IT SITS OVER, IT DOES NOT ASSERT THEM (2026-08-22, round 14
    #: seat 5, BLOCKER). This read "Four near-identical designs at two seams, two orderable and two
    #: not" as a typed literal while the rows below it are derived from CONDEMNED. Cutting the panel
    #: to one pair for the six-page budget left the caption describing four designs at two seams
    #: over a two-row, one-seam table — and it shipped in both built PDFs. `--check` was clean
    #: throughout, because the generator reproduces its own output faithfully; what it cannot catch
    #: is a sentence inside that output disagreeing with the rows beside it. Same defect as every
    #: other typed count this session: the number went out of date, the content did not.
    n_designs = 2 * len(CONDEMNED)
    n_seams = len({_at(rows, seq)["junction"] for seq in CONDEMNED})
    _cap = (f"{_spell(n_designs)} near-identical designs at "
            f"{_spell(n_seams)} seam{'s' if n_seams != 1 else ''}, half orderable and half not"
            if len(CONDEMNED) > 1 else
            f"{_spell(n_designs)} near-identical designs at one seam, one orderable and one not")
    out += [f"**Table 2. {_cap[0].upper() + _cap[1:]}.** Each "
            "pair is two consecutive registers of one seam differing by a single-base slide, and "
            "the two members carry opposite verdicts: the condemned member pairs its whole "
            "catalytic gap against a wild-type parent at the ten-base-pair criterion and the "
            "orderable member does not. " + near + " Neither may be substituted for the other, and "
            "neither is named for synthesis. The pairing is read from the canonical file's own "
            "cross-reference column.", ""]
    out += ["| seam | design | verdict | margin | WT gap duplex (bp) |",
            "|---|---|---|---:|---|"]
    for seq in CONDEMNED:
        bad = _at(rows, seq)
        twin_seq, relation = _twin(bad)
        good = _at(rows, twin_seq)
        out.append(f"| {_seam(bad['junction'])} | 5′-{bad['sequence']}-3′ | DO NOT ORDER | "
                   f"{bad['gap_level_margin']} | {_duplex(bad)} |")
        out.append(f"| {_seam(good['junction'])} | 5′-{good['sequence']}-3′ | orderable "
                   f"({relation.replace('; orderable','')}) | {good['gap_level_margin']} | "
                   f"{_duplex(good)} |")
    out.append("")
    return "\n".join(out)



def _slides_to_a_named_lead(rows):
    """How many single-base slides separate a condemned design from a lead at the same seam.

    A slide is one register: two 16-mers overlap in 15 positions, so `a[1:] == b[:-1]`. The walk is
    bounded by the oligonucleotide length because a design more than sixteen registers away shares
    no base with the lead and is not a near-twin of it in any useful sense.
    """
    def one_slide(a, b):
        return a[1:] == b[:-1] or b[1:] == a[:-1]

    best = None
    for seq in CONDEMNED:
        bad = _at(rows, seq)
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
    #: `_duplex` renders as "11 bp, wild-type *NR4A3*", which does not read as a noun phrase in the
    #: middle of a sentence; split it so the length and the gene each land where they belong.
    length, _, gene = duplex.partition(", wild-type ")
    #: ⚠ A PARTITIVE OVER A SET OF ONE READS AS A SET OF MANY (round 14 seat 5). "One of the
    #: condemned designs" was written when the panel printed two; with one pair it invites the
    #: reader to look for the others. Phrased from the count, like the caption above it.
    opener = ("One of the condemned designs is" if len(CONDEMNED) > 1
              else "The condemned design is")
    return (f"{opener} not at an unrelated seam: 5\u2032-{bad_seq}-3\u2032 is "
            f"{slides} from 5\u2032-{lead_seq}-3\u2032, a reagent this paper names for synthesis, "
            f"and pairs {length} of wild-type {gene} through its whole catalytic gap.")


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
