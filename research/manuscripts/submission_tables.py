#!/usr/bin/env python3
"""Generate the submission manuscript's two tables from committed artifacts.

⛔ BOTH TABLES WERE CITED BEFORE EITHER EXISTED (found 2026-08-12). The Results text referred to
"Table 1" and "Table 3" through several revisions and the manuscript contained no table at all —
the kind of gap that survives every linter here, because a cross-reference to a missing float is
neither a false claim nor a style violation, and the prose reads perfectly without it.

GENERATED, NOT TYPED, for the ordinary reason: a table is where a paper's numbers are densest, and
a hand-copied table is the most likely place in a manuscript for an artifact and its report to
diverge. Every cell below is read from `nr4a3-fusion-junction-atlas.json`,
`junction-aso-offtarget-locus-collapse.json`, `offtarget-chance-baseline.json` and the per-junction
screens; nothing is recomputed and nothing is entered by hand.

⚠ Table 3 carries the censoring and orientation caveats INSIDE the table, not only in the caption.
A table is the part of a paper most likely to be read on its own, quoted in a review, or lifted into
a slide, so a count that is an upper bound has to say so where the count is.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "modalities")
OUT = os.path.join(HERE, "aso", "fusion-junction-aso-submission-tables.md")

sys.path.insert(0, os.path.abspath(MOD))
import aso_screen_sets as ass                                            # noqa: E402

sys.path.insert(0, HERE)
#: Imported for ONE fact: the name of the canonical machine-readable sequence file. Rule 1 — the
#: manifest owns that filename, so a rename reaches these captions instead of leaving them pointing
#: at a file the archive no longer carries.
import aso_sequence_manifest as _manifest                                # noqa: E402

#: The geometry Tables 2 to 4 are about — the panel the manuscript reports. ⚠ TABLE 7 IS THE
#: EXCEPTION AND IS SUPPOSED TO BE: it is the gap-length trade, one column per geometry, and it
#: reads `aso-gap-length-tradeoff.json`, which is the artifact that owns the cross-geometry
#: comparison. A per-geometry TABLE built from a per-geometry ARTIFACT is not pooling.
GEOMETRY = ass.MANUSCRIPT_GEOMETRY


#: The deposit inventory. ONE HOME for which files travel together, and the only place this
#: document can learn its own path without typing it.
ARCHIVE_MANIFEST = os.path.join(HERE, "aso", "fusion-junction-aso-archive-manifest.json")

#: ⛔ THE CANONICAL COLUMN A DUPLEX CELL IS, AND THE ONLY THING A LOOSE-CUT VERDICT MAY BE COMPUTED
#: FROM. Table 5's cells now carry the verdict the duplex reading takes at the loose end of the
#: cited range, and a verdict with no canonical home is a claim a reader cannot check: the file to
#: check it in is `fusion-junction-aso-sequences.csv`, and the number to check it against is this
#: column of it. NOTHING IS INVENTED IN THAT FILE — the verdict is a comparison of a column that
#: already exists against a cut `aso-parent-null.json` already reads, so the caption names the
#: column and the reader reproduces it. Asserted against the manifest's own field list, so a rename
#: upstream stops this build rather than leaving a caption pointing at a column that is not there.
DUPLEX_CSV_COLUMN = "mature_parent_duplex_through_gap_bp"
if DUPLEX_CSV_COLUMN not in _manifest._FIELDS:                           # noqa: SLF001
    raise SystemExit(
        f"Table 5's captions name `{DUPLEX_CSV_COLUMN}` as the column its duplex cells are, and "
        f"{os.path.basename(_manifest.OUT_CSV)} no longer carries a column of that name. Re-derive "
        "the manifest, or re-anchor the caption — do not print a verdict whose canonical home is "
        "a column that does not exist.")


def _self_identification():
    """The sentence in which this file names ITSELF and the deposit it belongs to.

    ⛔ NOTHING IN EITHER BUILT PDF NAMES THIS FILE (audit, 2026-08-19). The builder carries a
    filename-substitution map keyed on the deposited names, and the tables document had no name of
    its own anywhere in it — its heading read "Tables — fusion-junction ASO submission", which is a
    description of a section and not an identifier. A reader who is handed the printed tables, or
    who lifts one table out of them, has no way back to the article they belong to, to the
    generator that derives every cell, or to the archive that carries all three.

    ⚠ EVERY NAME IS READ FROM THE MANIFEST, NEVER TYPED. The manifest is the inventory that decides
    which files travel with the deposit, so a rename or a removal upstream reaches this sentence
    rather than leaving it pointing at a file the archive no longer carries. It refuses if this
    document is not in the manifest at all, because the honest failure is louder than a document
    that quietly claims to be part of a deposit that does not list it.
    """
    if not os.path.exists(ARCHIVE_MANIFEST):
        raise SystemExit(
            "this document names itself and the deposit it travels in from "
            f"{os.path.basename(ARCHIVE_MANIFEST)}, which this checkout does not carry. Re-derive "
            "the manifest rather than printing a deposit claim nothing inventories.")
    files = json.load(open(ARCHIVE_MANIFEST, encoding="utf-8"))["files"]
    me = os.path.relpath(OUT, os.path.join(HERE, "..", "..")).replace(os.sep, "/")
    if not any(f["path"] == me for f in files):
        raise SystemExit(
            f"{os.path.basename(OUT)} is not in {os.path.basename(ARCHIVE_MANIFEST)}'s file list, "
            "so it cannot say it travels with the deposit. Re-derive the manifest.")
    article = next((f["path"] for f in files
                    if f["path"].endswith("-research-article.md")), None)
    if not article:
        raise SystemExit(
            f"{os.path.basename(ARCHIVE_MANIFEST)} names no research-article manuscript, so this "
            "document cannot say which article its tables belong to. Re-derive the manifest.")
    return (f"**This file is `{os.path.basename(OUT)}`.** It is the machine-readable copy of the "
            f"numbered tables of `{os.path.basename(article)}`, generated by "
            f"`{os.path.basename(__file__)}` and never hand-edited, and it travels with that "
            f"article in the deposit `{os.path.basename(ARCHIVE_MANIFEST)}` inventories. A table "
            "lifted out of this file is a display item of that article and not a standalone "
            "result; the canonical machine-readable copy of every sequence named below is "
            f"`{os.path.basename(_manifest.OUT_CSV)}`, which is what to order from.")


def _ordering_clause(mixed_geometry=False):
    """What a reader ordering from THIS table has to know: the chemistry, and where the file is.

    ⛔⛔ `mixed_geometry=True` FOR ANY TABLE THAT IS NOT ALL ONE ARCHITECTURE, AND THE DEFAULT ONCE
    SHIPPED A FALSE STATEMENT ABOUT A REAGENT (blind screen of the built manuscript PDF, 2026-08-17,
    filed as a BLOCKER). This clause was written for Tables 2 and 4, which are the 5-6-5 panel and
    nothing else, so it asserted "every sequence in this table is an antisense 16-mer, tiled in the
    5-6-5 … architecture" as a flat fact. It was then applied unchanged to Tables 5 and 7 to close a
    different finding — that those tables printed orderable sequences with no chemistry at all.
    Table 7's whole subject is that the geometry VARIES: its columns are headed 5-6-5 (16-mer),
    5-8-5 (18-mer) and 5-10-5 (20-mer), and its design row prints an 18-mer and a 20-mer. Table 5
    carries a 5-8-5 gap-length control. So the sentence added to make those tables safe to order
    from told a reader that an 18-mer and a 20-mer are 16-mers at 5-6-5.

    ⚠ AND IT IS THE WORST PLACE FOR IT TO BE WRONG. This paper's position is that the geometry, not
    the base string, is the reagent — "the bases alone, ordered as unmodified DNA, are a different
    molecule" is in this very sentence. A caption that misstates the architecture of a named
    oligonucleotide is the exact error the clause exists to prevent, committed by the clause.

    ★ THE LESSON, WHICH IS THE O3 LESSON AGAIN: a remedy pasted uniformly across items it was not
    written for does not become safe by being about safety. Tables that carry a geometry column now
    say so and point at it; only tables that really are one architecture state one.

    ⛔ WHY THE CLAUSE EXISTS AT ALL. Tables 2 and 4 printed bare base strings with neither the
    chemistry nor a pointer to the machine-readable file (blind screen of the built PDF,
    2026-08-17), and they are precisely the tables a laboratory would order from — Table 2 the best
    design at each junction, Table 4 the designs with no sense-strand near-match. A caption that
    prints an orderable sequence and says nothing about the backbone invites an order for unmodified
    DNA, which is a different molecule and one about which nothing measured here holds. A caption
    travels without the banner: a table is the part of a paper most likely to be read on its own.

    ⚠ DERIVED, NOT TYPED. The length and the architecture come from `MANUSCRIPT_GEOMETRY` and the
    filename from the manifest that writes it, so a geometry change or a rename reaches this
    sentence rather than leaving it describing a panel that no longer exists.
    """
    if mixed_geometry:
        opener = ("The sequences in this table are antisense gapmers at more than one geometry, and "
                  "each row's own geometry is the one stated beside it: the architecture gives the "
                  "locked-nucleic-acid (LNA) wing, DNA gap and LNA wing in nucleotides, so 5-6-5 is "
                  "a 16-mer, 5-8-5 an 18-mer and 5-10-5 a 20-mer, each on a phosphorothioate "
                  "backbone that §6 specifies")
    else:
        opener = (f"Every sequence in this table is an antisense {GEOMETRY.oligo_len}-mer, tiled in "
                  # ⚠ "LNA" EXPANDED HERE, AT ITS FIRST USE IN THE TABLES. In the journal build the
                  # abbreviation appears from Table 2 on page 5 and is expanded only in §3 on page
                  # 23 — and a caption is the part of a paper most likely to be read on its own, so
                  # the chemistry note a reader meets first must not itself need a glossary.
                  f"the {GEOMETRY.architecture} locked-nucleic-acid (LNA)/DNA/LNA architecture on a "
                  f"phosphorothioate backbone that §6 specifies")
    #: ⛔ EVERY CAPTION CARRIES THE HANDLING STATEMENT (blind safety screen, 2026-08-19). Tables 2,
    #: 3 and 5 print 69 orderable sequences between them and Table 2 is, by its own caption, "the
    #: table one reagent is chosen from". The Declarations say the prohibition covers "its tables",
    #: but that sentence is fifty pages away and nothing in a table pointed at it.
    return (f"{opener}; the bases alone, ordered as unmodified DNA, are a different molecule. "
            f"Research use only: not for administration to any person or animal (Declarations). "
            f"The canonical machine-readable copy of every sequence is "
            f"`{os.path.basename(_manifest.OUT_CSV)}`, which is what to order from rather than "
            f"this PDF.")


def _load(name):
    p = os.path.join(MOD, name)
    return json.load(open(p)) if os.path.exists(p) else None


_PARENT_CUT_BP = None


def _parent_cut_bp():
    """The base-pair cut every ⚑ in this document is set at, from the artifact that applies it.

    ⛔ IT WAS TYPED IN SIX PLACES (audit, 2026-08-19). `_parent_dup_cell` compared against a literal
    `10`; Table 3's ⚑ note said "ten base pairs"; Table 4's note ⁷ said it again; Table 5's caption a
    fourth time; Table 7 carried it in a row LABEL and in its caption. Six copies of one number whose
    only home is `aso-parent-gap-pairing.json`'s `method.min_duplex_bp` — which is where the screen
    applies it, and which `aso-gap-length-tradeoff.json` already points at rather than restating
    (`thresholds.min_duplex_bp_for_hybrid_binding_domain._home`). Rule 1: a threshold restated is a
    threshold that can move in the screen and not in the caption, and the direction that failure runs
    is a caption promising ten over a column screened at something looser.

    ⚠ IT REFUSES RATHER THAN DEFAULTING. ⚑ is a do-not-order verdict, so rendering markers under a
    criterion no screen actually applied is worse than not rendering the table at all.
    """
    global _PARENT_CUT_BP
    if _PARENT_CUT_BP is None:
        bp = ((_load("aso-parent-gap-pairing.json") or {}).get("method") or {}).get("min_duplex_bp")
        if not bp:
            raise SystemExit(
                "the ⚑ do-not-order marker is set at the parent screen's own criterion, and "
                "aso-parent-gap-pairing.json reports no `method.min_duplex_bp` in this checkout. "
                "Re-derive that artifact rather than marking do-not-order rows at a typed cut.")
        _PARENT_CUT_BP = int(bp)
    return _PARENT_CUT_BP


def _parent_dup_cell(entry):
    """Render a longest-parent-duplex cell, flagging the criterion in place.

    ⛔ The bare number is not enough here. Table 3's † marks JUNCTIONS where no design clears the
    parent screen; a reader therefore reads an unmarked row as clean, and six unmarked rows printed
    designs pairing a wild-type parent through the whole catalytic gap at eleven base pairs. The
    cell carries the gene and an explicit marker at or above the criterion, so the hazard is legible
    on the row rather than inferable from a column this table used not to have.
    """
    if not entry or entry[0] is None:
        return "—"
    bp, gene = entry
    if not bp:
        return "0"
    cell = f"{bp} (*{gene}*)"
    return cell + " ⚑" if bp >= _parent_cut_bp() else cell


def _cut_sensitivity():
    """The same parent screen read at the LOOSE end of the cited range, from the artifact that read it.

    ⛔ THE CAPTIONS TYPED THIS AND ONLY HALF OF IT (audit, 2026-08-19). Table 3's ⚑ note carried
    "175 of the 190" and "181 … at any length" as literals, and Table 2 — the table a reagent is
    actually chosen from — carried the cut caveat nowhere at all. The whole point of the sentence is
    that the marker is a reading at ONE cut: at seven base pairs almost the entire panel is liable
    and only nine of the thirty-eight seams have a design that clears, against thirty-five at ten.
    A number typed into that sentence is a number that can stop matching the screen it describes.

    ⭐ `aso-parent-null.json`'s `cut_sensitivity` block is the one place that reads both cuts, and
    its counts reproduce exactly from `aso-parent-gap-pairing.json`'s per-design runs (190 designs;
    87 at ≥10, 175 at ≥7, 181 non-zero; 35 and 9 junctions clearing). It refuses rather than falling
    back, because the flatter sentence — the one without the caveat — is the wrong thing to print.

    ⚠ THE THIRD NUMBER IS NOT IN THAT BLOCK AND IS NOT INVENTED HERE. "at any length" is the count
    of designs a parent pairs through the whole gap at ANY run length, which `cut_sensitivity` does
    not carry because it is not a cut; its home is `aso-gap-length-tradeoff.json`'s
    `mature_parent_whole_gap_duplex.n_with_any_gap_pairing_window`, which is the same field Table 7's
    "a mature parent can pair the whole gap" row already prints. Read from there, so the note and
    the row cannot come apart.
    """
    cs = (_load("aso-parent-null.json") or {}).get("cut_sensitivity") or {}
    try:
        loose = min(int(c) for c in cs["cuts_bp"] if int(c) < _parent_cut_bp())
        key = str(loose)
        geo = next(g for g in (_load("aso-gap-length-tradeoff.json") or {})["geometries"]
                   if g["architecture"] == GEOMETRY.architecture)
        return {
            "loose_bp": loose,
            "n_designs": int(cs["n_designs"]),
            "n_junctions": int(cs["n_junctions"]),
            "n_liable_loose": int(cs["observed_n_liable"][key]),
            "n_liable_strict": int(cs["observed_n_liable"][str(_parent_cut_bp())]),
            "n_liable_any_length": int(
                geo["mature_parent_whole_gap_duplex"]["n_with_any_gap_pairing_window"]),
            "n_junctions_clearing_loose": int(cs["n_junctions_with_a_clearing_design"][key]),
            "n_junctions_clearing_strict": int(
                cs["n_junctions_with_a_clearing_design"][str(_parent_cut_bp())]),
        }
    except (KeyError, ValueError, StopIteration) as exc:
        raise SystemExit(
            "the ⚑ notes state that the do-not-order marker is a reading at one cut, and the "
            "counts behind that come from aso-parent-null.json's `cut_sensitivity` block, which "
            f"this checkout does not carry usably ({exc}). Re-derive it rather than printing a "
            "marker with no statement of what an unmarked row does and does not mean.") from exc


def _cut_caveat():
    """The one sentence that says what an UNMARKED parent-duplex cell does and does not mean.

    ⛔ IT LIVED IN TABLE 3's ⚑ NOTE ONLY, AND TABLE 3 IS NOT THE TABLE A REAGENT IS CHOSEN FROM
    (audit, 2026-08-19). Table 2's own caption calls itself "the table one reagent is chosen from",
    Table 5 is the table §4 prices, and neither carried any statement that the parent-duplex column
    beside its sequences is a reading at ONE adopted cut — while Table 2 prints fourteen rows at
    eight base pairs and four at nine, every one of them unmarked, and Table 5's highest cell is a
    nine. Under a cut one base pair looser those rows are the panel, not the exceptions.

    ⭐ ONE WORDING, ONE HOME, THREE CAPTIONS. Printed rather than cross-referenced for the same
    reason `_rule_audit_note` is: a caption is the part of a paper most likely to be read on its
    own, and a do-not-order caveat that lives in another table's note is a caveat a lifted table
    does not carry. Every number in it is `_cut_sensitivity`'s.
    """
    cs = _cut_sensitivity()
    cut = _parent_cut_bp()
    return (f"That {_word(cut)}-base-pair cut is a criterion this work ADOPTS rather than measures, "
            f"and the reading moves with it: at {_word(cs['loose_bp'])} base pairs "
            f"{cs['n_liable_loose']} of the {cs['n_designs']} panel designs pair a parent through "
            f"the whole gap against {cs['n_liable_strict']} at {_word(cut)}, "
            f"{cs['n_liable_any_length']} do so at some length, and only "
            f"{_word(cs['n_junctions_clearing_loose'])} of the {cs['n_junctions']} seams have a "
            f"design that clears against {cs['n_junctions_clearing_strict']} at {_word(cut)} "
            "(§2.9). A cell below the cut is a reading at one cut and nothing wider.")


def _rank_stability(per_junction):
    """Table 2's recommendation re-ranked at every cut below the adopted one. [(cut, rows, same, differ)]

    ⛔ THE TABLE A REAGENT IS CHOSEN FROM RANKED ON THE ONE SCREEN THE PAPER SAYS IS ADOPTED RATHER
    THAN MEASURED, AT ONE CUT, AND SAID NOTHING ABOUT WHAT ANOTHER CUT WOULD DO (display-item
    review, 2026-08-19). `parent_is_liability` is the FIRST key of the rank and the eligibility
    test besides, so the cut decides both which design each seam recommends and whether the seam
    gets a recommendation at all — and the caption's cut caveat states the panel-wide rate, which
    is a different quantity from "is the reagent on this row still the reagent".

    ⭐ THE RE-RANK IS THE SAME CODE PATH, NOT AN APPROXIMATION OF IT. `aso_per_junction_table`
    sorts on (liability, pre-mRNA sites, gap-paired loci, −margin, hits) and takes the first design
    that is not liable; the same keys are applied here to the same screened designs with only the
    liability test moved. Nothing is re-screened.

    ⚠ AND IT REFUSES UNLESS IT REPRODUCES THE ARTIFACT AT THE ADOPTED CUT. A re-ranking that cannot
    return the rows the table actually prints is not evidence about any other cut either, so the
    adopted cut is recomputed first and asserted design-for-design against `best_available`.
    """
    cuts = sorted((_load("aso-parent-null.json") or {}).get("cut_sensitivity", {})
                  .get("cut_ladder_bp") or [])
    adopted = _parent_cut_bp()

    def _best(cut, designs):
        ranked = sorted(designs, key=lambda r: (bool((r["parent_duplex_bp"] or 0) >= cut),
                                                r["premrna_gap_paired_hybridisable"] or 0,
                                                r["n_gap_paired_loci"],
                                                -(r["gap_specificity_margin"] or 0),
                                                r["n_gap_paired"]))
        clear = [r for r in ranked if (r["parent_duplex_bp"] or 0) < cut]
        return clear[0] if clear else None

    for j in per_junction["junctions"]:
        want = (j.get("best_available") or {}).get("antisense_5to3")
        got = (_best(adopted, j["designs"]) or {}).get("antisense_5to3")
        if want != got:
            raise SystemExit(
                "Table 2's caption reports whether its recommendation survives a different cut, and "
                f"the re-ranking behind that sentence does not reproduce the artifact at the "
                f"adopted cut: {j['junction_label']} reads {want!r} and re-ranks to {got!r}. The "
                "rank keys have moved in aso_per_junction_table; re-derive rather than printing a "
                "stability claim computed by a rule the table was not built with.")

    out = []
    for cut in cuts:
        if cut >= adopted:
            continue
        rows = same = differ = 0
        for j in per_junction["junctions"]:
            b = _best(cut, j["designs"])
            if b is None:
                continue
            rows += 1
            cur = (j.get("best_available") or {}).get("antisense_5to3")
            same += b["antisense_5to3"] == cur
            differ += b["antisense_5to3"] != cur
        out.append((cut, rows, same, differ))
    return out


def _parent_liability_definition():
    """What "parent liability" IS, operationally, from the screen's own method block.

    ⛔ TABLE 2's PRIMARY SORT KEY WAS NAMED AND NEVER DEFINED (audit, 2026-08-19). The caption said
    designs are "ranked by parent liability first" and nothing in the document said what a parent
    liability is, which parents were searched, in which compartment, or at what length — while the
    same table prints a "longest parent duplex through the gap (bp)" column whose relation to that
    ranking a reader had to guess. The definition is the screen's, so it is read from the screen.
    """
    m = (_load("aso-parent-gap-pairing.json") or {}).get("method") or {}
    parents = list(m.get("parents_searched") or [])
    compartment = str(m.get("compartment") or "")
    if not parents or not compartment:
        raise SystemExit(
            "Table 2's caption defines parent liability from aso-parent-gap-pairing.json's method "
            "block, which no longer names the parents searched or the compartment. Re-derive it "
            "rather than printing a ranking whose first key the document does not define.")
    return parents, compartment


def _expression_cuts():
    """The two legibility cuts, from the module that sets them. One home, never re-typed."""
    sys.path.insert(0, os.path.abspath(MOD))
    from aso_offtarget_tissue_expression import (EXPRESSED_TPM,  # noqa: PLC0415
                                                 PRESENT_TPM)
    return float(PRESENT_TPM), float(EXPRESSED_TPM)


def _hitlist_size():
    """BLAST's per-query hit ceiling, from the module that sets it. One home, never re-typed."""
    try:
        sys.path.insert(0, os.path.abspath(MOD))
        from junction_aso_offtarget import BLAST_HITLIST_SIZE  # noqa: PLC0415
        return int(BLAST_HITLIST_SIZE)
    except Exception:  # noqa: BLE001
        return 50


def _saved_hits():
    """How many hits are stored per design. Same rule as above: ask the module that decides it."""
    try:
        sys.path.insert(0, os.path.abspath(MOD))
        from junction_aso_offtarget import SAVED_HITS_PER_DESIGN  # noqa: PLC0415
        return int(SAVED_HITS_PER_DESIGN)
    except Exception:  # noqa: BLE001
        return 15


HITLIST_SIZE = _hitlist_size()
SAVED_HITS = _saved_hits()

#: Numbers spelt for prose. ONE HOME: the seam count in Table 6's caption used its own inline copy
#: of this map, so a second derived count elsewhere would have grown a second one.
_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
          9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
          15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
          20: "twenty"}


def _word(n):
    return _WORDS.get(n, str(n))


def _chemistry(gap):
    """What a `geometry` cell denotes, derived from the artifact that owns the geometries.

    ⛔ THIS DOCUMENT NEVER STATED THE CHEMISTRY IT IS ABOUT (cold-reader finding, 2026-08-17). Table
    7's `geometry` column read `5-6-5` and `5-8-5`, expanded nowhere; "LNA" appeared twice, inside
    two captions, unexpanded; "phosphorothioate" appeared exactly once, inside Table 6's
    biodistribution aside; and "backbone" appeared not at all. This is the file a laboratory prints
    and orders reagents from, and the bare base sequences in it are orderable as unmodified DNA — a
    different molecule, to which nothing measured here applies. A safety notice that omits the
    chemistry is the one omission that turns a correct table into a wrong order.

    ⚠ DERIVED, NOT TYPED. The geometry strings, the wing and each gap length come from the same
    `geometries` block Table 7's columns come from, so a fourth geometry screened tomorrow is
    explained by this sentence instead of leaving it quietly describing three.
    """
    present = sorted((g for g in gap["geometries"] if g.get("present")),
                     key=lambda g: g["gap_nt"])
    if not present:
        raise SystemExit("the research-use banner: the trade-off artifact reports no present "
                         "geometry, so the sentence that expands the geometry column has nothing "
                         "to expand")
    wings = {g["wing"] for g in present}
    if len(wings) != 1:
        raise SystemExit(
            "the research-use banner explains ONE wing length for every geometry printed here and "
            f"the artifact now reports {sorted(wings)}; re-derive the sentence rather than letting "
            "it describe a wing some column does not have")
    w = _word(wings.pop())
    first = present[0]
    txt = (f"`{first['architecture']}` is {w} LNA nucleotides, a "
           f"{_word(first['gap_nt'])}-nucleotide DNA gap and {w} LNA nucleotides")
    rest = present[1:]
    if rest:
        archs = [f"`{g['architecture']}`" for g in rest]
        gaps = [_word(g["gap_nt"]) for g in rest]
        a = f"{', '.join(archs[:-1])} and {archs[-1]}" if len(archs) > 1 else archs[0]
        b = f"{', '.join(gaps[:-1])} and {gaps[-1]}" if len(gaps) > 1 else gaps[0]
        txt += (f"; {a} the same {w}-nucleotide LNA wings around gaps of {b}"
                if len(archs) > 1 else
                f"; {a} the same {w}-nucleotide LNA wings around a {b}-nucleotide gap")
    return txt


def _condemned_designs(noncoding):
    """The designs the main text names as NOT to be carried forward, from the scan that condemns them.

    ⛔ THE BANNER EXCLUDED THEM BY DESCRIPTION AND NEVER PRINTED THEM (cold-reader finding,
    2026-08-17). It said the three designs are not in these tables, which is true and checkable by
    `test_condemned_designs_are_absent_from_the_tables.py` — but a reader who has transcribed a
    sequence cannot check it against a list the document does not carry, and the near neighbours are
    close enough that a transcription slip lands on one: two of the three are register shifts of a
    reagent Table 5 does print. Naming an absent danger without naming the danger is the half of the
    notice that does no work.

    ⭐ READ FROM THE SCAN, NEVER TYPED. `⭐_wild_type_NR4A3_cleavage_liability` is the artifact that
    condemns them — the exhaustive ≤2-mismatch scan of *NR4A3*'s unspliced sequence — and its own
    positive control contributes the third, at the sibling cryptic-exon seam. A fourth design
    condemned upstream therefore reaches this banner without an edit here, which is the property a
    typed list cannot have.

    ⚠ AND THE CONTROL IS ASSERTED BEFORE THE LIST IS BELIEVED. A liability scan that fires on
    nothing is indistinguishable from a clean panel; if its known-positive stops firing, a SHORTER
    do-not-order list is exactly the wrong thing to print, so this refuses to build instead.
    """
    liab = noncoding.get("⭐_wild_type_NR4A3_cleavage_liability") or {}
    ctrl = liab.get("positive_control") or {}
    if not ctrl.get("passed"):
        raise SystemExit(
            "the research-use banner's do-not-order list is read from the wild-type NR4A3 "
            "liability scan, whose positive control is not passing in this checkout. A scan that "
            "no longer detects the one design it is known to have to detect cannot be used to "
            "enumerate the condemned set — fix the scan rather than printing a shorter list.")
    seqs = list(liab.get("designs_cleaving_wild_type_NR4A3") or [])
    seqs += [s for s in (ctrl.get("observed_designs") or []) if s not in seqs]
    if not seqs:
        raise SystemExit(
            "the wild-type NR4A3 liability scan condemns no design in this checkout while its "
            "positive control passes, which is a contradiction: the control's own design is one of "
            "the condemned set. Re-derive before regenerating.")
    return seqs


def _longest_shared_run(a, b):
    """The longest run of bases two sequences share, in any register. Plain dynamic programming.

    Used only to state, in the banner, how close the nearest printed sequence comes to a condemned
    one — the fact that makes a do-not-order list worth printing rather than a formality.
    """
    best, prev = 0, [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


def _md_table(rendered):
    """(header cells, body rows) of a rendered pipe table — THE ROWS AS PRINTED, not as intended.

    ⛔ EVERY CROSS-TABLE CLAIM BELOW IS MEASURED OFF THE RENDERED TEXT, NEVER OFF THE INPUTS. A
    caption that says "Table 3 marks them do-not-order" is a claim about what a reader FINDS on
    another page, and the only way to be wrong about it is to reason from the artifact both tables
    were built from instead of from the rows each one actually printed. That is exactly how the
    claim below came to be false: Table 4 knew its five ⚑ designs were condemned by the parent
    screen, and inferred — correctly about the SCREEN, falsely about the TABLE — that Table 3 shows
    that verdict, when Table 3 prints one design per junction and four of the five are not it.
    ⚠ The banner's do-not-order run already reads the rendered tables this way (`_printed` in
    `main`), so this is the file's existing idiom rather than a new one.
    """
    lines = [ln for ln in rendered.splitlines() if ln.startswith("|")]
    hdr = [c.strip() for c in lines[0].strip("|").split("|")]
    body = [[c.strip() for c in ln.strip("|").split("|")] for ln in lines[2:]]
    return hdr, body


def _col(hdr, prefix):
    """Index of the one column whose header starts with `prefix`; refuses on nought or several."""
    hits = [i for i, c in enumerate(hdr) if c.startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit(
            f"a caption is generated by reading the column headed “{prefix}…” and the rendered "
            f"header matches it {len(hits)} times ({hdr}). Re-anchor the caption's join rather "
            "than letting it describe a column that moved.")
    return hits[0]


def _seq_in(cell):
    """The bare base string inside a printed `5′-…-3′` cell, or None."""
    m = re.search(r"5′-([ACGT]+)-3′", cell)
    return m.group(1) if m else None


def _records_per_locus(collapse, depth):
    """(median, maximum) RefSeq accession records per distinct gene locus, at one search depth.

    ⛔ A NEAR-MATCH COUNT IS A COUNT OF RECORDS AND EVERY READER TAKES IT FOR A COUNT OF GENES
    (competitor review, 2026-08-19). RefSeq lists one accession per annotated variant, so a match
    to a constitutive exon is returned once per variant: the lead reagent's 123 gap-paired
    near-matches at the deeper ceiling are six loci, not 123 genes. §5 states the size of that
    collapse and states it at the DEFAULT ceiling — and Tables 2, 3 and 4 headline the DEEP one,
    where it is more than twice as large. A reader who applies the paper's own correction to these
    cells still lands nowhere near the gene count.

    ⭐ READ FROM THE COLLAPSE ARTIFACT, WHICH IS WHERE THE FACTOR LIVES. `inflation_factor` is a
    per-design field of `junction-aso-offtarget-locus-collapse.json` and its per-depth medians are
    that file's own summary, computed over the uncensored designs only — a ratio of a truncated
    numerator to a truncated denominator bounds the true ratio in neither direction, which is why
    the censored designs are excluded there and must not be pooled back in here.
    """
    key = {"default": "totals_over_uncensored_oligos_only",
           "deep": "deep_totals_over_uncensored_oligos_only"}[depth]
    tot = collapse.get(key) or {}
    med, mx = tot.get("median_inflation_factor"), tot.get("max_inflation_factor")
    if med is None or mx is None:
        raise SystemExit(
            f"these captions state how many RefSeq accession records a near-match count carries per "
            f"gene locus, and `{key}` of the locus-collapse artifact no longer publishes that "
            "summary. Re-derive the artifact rather than printing a record count with no factor "
            "beside it — a reader takes it for a gene count.")
    return med, mx


def _printed_records_per_locus(rendered, prefix):
    """The `records → loci` cells a table PRINTS, as (median ratio, max ratio, row, records, loci).

    ⚠ MEASURED OFF THE RENDERED ROWS, like every other cross-cell claim in this file, because the
    claim is about what a reader finds in this table's own column and not about the panel the
    artifact summarises. The two are different populations: the artifact's factor is over every
    uncensored design, and a table prints one design per junction.

    ⛔ A CELL CARRYING EITHER CENSORING MARK IS SKIPPED, and that is the same rule the collapse
    artifact applies: a ratio of a truncated numerator to a truncated denominator bounds the true
    ratio in neither direction. Table 3's largest printed quotient is `≥50 → ≥1`, and naming that
    as this table's most inflated cell would report a sampling artefact as a measurement. A cell
    with no locus count is skipped too, since a ratio over nought loci is not a ratio.
    """
    hdr, body = _md_table(rendered)
    i = _col(hdr, prefix)
    seen = []
    for r in body:
        m = re.match(r"^(\d+) → (\d+)$", r[i])
        if not m:
            continue
        n, loci = int(m.group(1)), int(m.group(2))
        if loci:
            #: the row label carries this table's own markers (†, ‡); the caption names the row,
            #: not its verdicts, and a marker lifted out of the grid keys nothing here.
            seen.append((n / loci, r[0].split(" †")[0].split(" ‡")[0].strip(), n, loci))
    if not seen:
        raise SystemExit(
            f"a caption states the record-to-locus ratio of the column headed “{prefix}…” and no "
            "row of the rendered table prints that column as an uncensored `records → loci` pair. "
            "Re-anchor the sentence on the column that carries the pair.")
    seen.sort()
    #: (median ratio, the most inflated cell's row, its records, its loci, how many cells were read).
    #: The maximum RATIO is not returned: the caption prints the two counts it is a ratio of, so a
    #: reader divides the numbers on the page rather than checking an arithmetic claim about them.
    _, row, n, loci = seen[-1]
    return seen[len(seen) // 2][0], row, n, loci, len(seen)


def _records_note(deep, printed=None, at_default=None):
    """The caption sentence that says a near-match count is records and not genes.

    ⛔ ONE SENTENCE, THREE TABLES, because the defect is one defect: Tables 2, 3 and 4 all print a
    RefSeq accession count under a header that says "near-matches", and none of them said how far
    that is from a number of genes. Written once so the three cannot come to disagree about the
    size of a collapse they all report.

    ⚠ AND IT SAYS WHERE THE DIVISION IS NOT AVAILABLE. Only Table 2 prints the deep record count
    beside the loci THOSE RECORDS collapse to. In Tables 3 and 4 the deep locus column counts the
    gap-paired subset alone, so a reader dividing the deep near-match count by the locus cell
    beside it gets a ratio of two different hit sets — the reading that produced a "maximum near
    100" in review, against a true deep maximum well below it.
    """
    def _cell(pair):
        ratio, row, n, loci, rows = pair
        return (f"a median of {ratio:.1f} records per locus over the {rows} rows whose cell carries "
                f"no censoring mark, and most at {row}, whose {n} records are "
                f"{_word(loci)} {'locus' if loci == 1 else 'loci'}")

    med, mx = deep
    out = "RefSeq lists one accession per annotated variant, so "
    if printed:
        out += ("the left half of that cell counts transcript accession RECORDS and not distinct "
                "genes, which is why the collapsed locus count is printed beside it: the two "
                f"differ by {_cell(printed)}")
    elif at_default:
        out += ("a near-match count is a count of transcript accession RECORDS and not of distinct "
                "genes, which is why the default-depth count is given collapsed to distinct gene loci beside "
                "it, and the size of that collapse is measured rather than left to the reader: the "
                f"default-depth pair runs at "
                f"{_cell(at_default)}")
    else:
        out += ("every near-match count in this table is a count of transcript accession RECORDS "
                "and not of distinct genes")
    out += (f". Across the deep screens' uncensored designs, taken over every stored near-match "
            f"rather than the gap-paired subset, the collapse runs at a median of {med} records "
            f"per locus and a maximum of {mx}; §5 gives the same figure at the DEFAULT ceiling, "
            "which is smaller and does not describe a column read at the deeper one.")
    if not printed:
        out += (" **⚠ The deep columns are not a records-and-their-own-loci pair**: the deep locus "
                "column counts only the GAP-PAIRED subset of the records the near-match columns "
                "beside it count, so dividing one by the other is a ratio of two different hit "
                "sets and not a records-per-locus figure.")
    return out


def _flagged_rows_in_table3(t3, t4):
    """What a reader looking up Table 4's ⚑ designs in Table 3 ACTUALLY finds.

    ⛔⛔ TABLE 4's CAPTION SENT A READER TO A TABLE THAT CONTRADICTS IT (measured, 2026-08-19). It
    said its ⚑ rows are the designs "Table 3 marks do-not-order for it". RECOMPUTED over the
    rendered rows: five of Table 4's nine rows carry ⚑, they sit at three junctions, and Table 3
    prints ONE of the five — `GGCATATCAAGCGCTG` at TCF12 e7, which does carry ⚑ there. At the other
    two junctions Table 3 prints a DIFFERENT design and marks it with nothing: `GGGCATATCCGTGGAC`
    at 0 bp for EWSR1 e1 and `GGGCATATCTTGCATA` at 8 bp for TCF12 e9. So four of the five are marked
    nowhere but in Table 4 itself, and a reader who follows the cross-reference to check finds an
    UNMARKED row at two of the three junctions — the flattering direction, and the one that ends in
    an order. Table 3 prints one row per junction, that junction's highest-margin design; whether it
    also happens to be the condemned one is a coincidence of the two rankings, not a property.

    Returns (n_flagged, designs also printed in Table 3, [(junction, Table 3's design cell,
    Table 3's duplex cell) for the junctions where Table 3 prints something else]).
    """
    h4, b4 = _md_table(t4)
    h3, b3 = _md_table(t3)
    i4d, i4j = _col(h4, "design"), _col(h4, "junction")
    i4f = _col(h4, "longest wild-type parent duplex")
    i3d, i3f = _col(h3, "that design"), _col(h3, "longest parent duplex")
    flagged = [(_seq_in(r[i4d]), r[i4j]) for r in b4 if "⚑" in r[i4f]]
    t3_by_junction = {r[0].rstrip(" †‡"): r for r in b3}
    t3_seqs = {_seq_in(r[i3d]) for r in b3} - {None}
    also = sorted({s for s, _ in flagged if s in t3_seqs})
    #: ⚠ THE TEST IS WHETHER THE ROW A READER LANDS ON IS MARKED, NOT WHETHER SOME DESIGN AT THAT
    #: SEAM IS. TCF12 e7 carries two of the five ⚑ designs and Table 3 prints one of them, marked —
    #: so that junction corroborates the cross-reference and must not be listed as contradicting it,
    #: even though its other ⚑ design is printed nowhere but Table 4.
    elsewhere = []
    for j in sorted({j for _, j in flagged}):
        r = t3_by_junction.get(j)
        if r is None:                       # a junction Table 3 has no row for at all
            elsewhere.append((j, None, None))
        elif "⚑" not in r[i3f]:
            elsewhere.append((j, _seq_in(r[i3d]), r[i3f]))
    return len(flagged), also, elsewhere


def _near_twin_warning(t2, t3):
    """The junctions where Table 2 prints a clean design and Table 3 a condemned near-twin of it.

    ⛔ THE HAZARD THE BANNER NAMES, APPLIED TO THE TABLES THEMSELVES (measured, 2026-08-19). The
    do-not-order banner justifies printing three condemned sequences by measuring how close the
    nearest PRINTED sequence comes to one of them. The same measurement was never run BETWEEN the
    tables: at ten junctions Table 3's highest-margin design carries ⚑ while Table 2 names a
    different, uncondemned design at the same seam or none at all, and at seven of those ten the two
    sequences share fifteen of their sixteen contiguous bases — one register apart, four printed
    pages apart in the built PDF, with no warning on either page. A reader who transcribes from the
    wrong table by one row is holding the condemned molecule.

    ⛔ AND THE CAPTION USED TO PRINT THE NARROW COUNT UNDER THE WIDE CLAIM (blind PDF screen,
    2026-08-19, graded BLOCK). It read "At ten junctions Table 3 names a different design from this
    table" — but ten is the count where one of the two is CONDEMNED and the other is not. The two
    tables name a different design at SIXTEEN junctions, because they rank on different keys. A
    reader checking whether their seam is one of the ten, and finding it is not, concluded the two
    tables agree there; at six seams they do not. Both counts are returned now, and the caption
    states the wide one first.

    Returns (n junctions where the two name a different design AT ALL, n of those where one is
    condemned and the other is not, n of those at a shared run of `run` or more, run), with `run`
    measured rather than assumed — the largest shared run the disagreeing pairs reach.
    """
    h2, b2 = _md_table(t2)
    h3, b3 = _md_table(t3)
    i2d = _col(h2, "best available design")
    i3d, i3f = _col(h3, "that design"), _col(h3, "longest parent duplex")
    t2_by_junction = {r[0]: _seq_in(r[i2d]) for r in b2}
    pairs = []
    for r in b3:
        j = r[0].rstrip(" †‡")
        if "⚑" not in r[i3f]:
            continue
        a, b = t2_by_junction.get(j), _seq_in(r[i3d])
        if b is None or a == b:
            continue
        pairs.append((j, a, b, _longest_shared_run(a, b) if a else None))
    runs = [p[3] for p in pairs if p[3] is not None]
    top = max(runs) if runs else 0
    # ⭐ THE WIDE COUNT: every junction both tables give a design for, where those designs differ.
    # Independent of any ⚑, because a reader comparing two tables is comparing SEQUENCES.
    t3_by_junction = {r[0].rstrip(" †‡"): _seq_in(r[i3d]) for r in b3}
    differ = sum(1 for j, a in t2_by_junction.items()
                 if t3_by_junction.get(j) is not None and a is not None
                 and t3_by_junction[j] != a)
    return differ, len(pairs), sum(1 for r in runs if r >= top), top


def _near_match_screen_losses(t4):
    """(rows Table 4's deeper re-screen takes the property away from, how many of those read zero).

    ⛔ THE TITLE'S OWN WITHDRAWAL WAS TYPED (audit, 2026-08-19). "Six of these lose the property"
    and "three of them having returned no near-match at all here" were literals in a caption whose
    whole subject is that the printed column is a default-depth reading — the one class of number
    in this file most likely to move, since it moves whenever a junction is re-screened. Both are
    read off the rendered rows now, so the sentence cannot outlive the measurement it describes.
    """
    hdr, body = _md_table(t4)
    i_v = _col(hdr, "survives the near-match screen")
    i_n = _col(hdr, "near-matches, either strand")
    lost = [r for r in body if "no" in r[i_v]]
    return len(lost), sum(1 for r in lost if r[i_n].strip() == "0")


def _junction_aggregate_column(t3, chance):
    """Where Table 3's one JUNCTION-WIDE column parts company with the design the row names.

    ⛔ THE CAPTION SAID EVERY FIGURE IS THE NAMED DESIGN'S AND ONE COLUMN IS NOT (measured,
    2026-08-19). "figures are for the design with the highest gap-level margin at that junction" is
    true of twelve of Table 3's thirteen columns; the last is headed "≤1-mismatch matches across
    that junction's designs, median (max)" and is an aggregate over every design screened at the
    seam. At EWSR1 e12 the cell reads 2 (22) while the named design's own ≤1-mismatch count is 1 —
    a reader checking the row against the artifact finds a number twice the one printed and a
    maximum twenty-two times it, and has to guess which of the two the rest of the row is.

    Returns (rows where the printed median is not the named design's own value, one such row as
    (junction, printed cell, the named design's own count)) — derived so the example in the caption
    cannot become a row the table no longer has.
    """
    hdr, body = _md_table(t3)
    i_d, i_a = _col(hdr, "that design"), _col(hdr, "≤1-mismatch matches across")
    own = {r["antisense_5to3"]: (r.get("offtarget_le1mm") or 0) for r in chance["per_design"]}
    differing = []
    for r in body:
        seq, cell = _seq_in(r[i_d]), r[i_a]
        m = re.match(r"^(\d+) \((\d+)\)$", cell)
        if seq is None or m is None or seq not in own:
            continue
        if int(m.group(1)) != own[seq]:
            differing.append((r[0].rstrip(" †‡"), cell, own[seq]))
    if not differing:
        raise SystemExit(
            "Table 3's caption distinguishes its one junction-wide column from the twelve that "
            "describe the named design, and no row now shows the two apart. Re-derive the sentence "
            "rather than illustrating a divergence the table no longer has.")
    return len(differing), differing[0]


def _highest_duplex_printed(rendered, prefix):
    """The largest parent-duplex reading any row of a rendered table prints, as an integer.

    ⛔ A CAPTION MAY NOT ASSERT A CRITERION ITS OWN COLUMN NEVER REACHES WITHOUT SAYING SO (audit,
    2026-08-19). Table 5's caption states the ten-base-pair criterion beside a column whose twelve
    cells read 0, 7, 8 and 9 — so the sentence reads as though the column had been FILTERED at ten,
    when what it means is that ten is the cut at which a reading would have been disqualifying. The
    difference decides whether a reader takes a 9 bp row as screened-and-passed or as one base pair
    short of the paper's central negative, and it is the second.
    """
    hdr, body = _md_table(rendered)
    i = _col(hdr, prefix)
    vals = [int(m.group(1)) for r in body if (m := re.match(r"^(\d+) ?bp", r[i]))]
    return max(vals) if vals else 0


def _one_seam_share():
    """(designs whose parent duplex is the ONE recurring wild-type *NR4A3* seam, the *NR4A3*-attributed
    designs, every liable design).

    ⛔ THE DENOMINATOR WAS THE WRONG ONE (audit, 2026-08-19). Table 4's ΔΔG note read "whose duplex
    for 59 of the 87 is not elsewhere in a parent at all but runs past the seam into the wild-type
    *NR4A3* exon-2/exon-3 junction". §2.5 states the same 59 against a different denominator — "Those
    61 are not 61 distinct sites: 59 of them are the same one" — and 61, not 87, is the population
    the property is defined over: it is a property of the designs whose duplex is ATTRIBUTED TO
    *NR4A3*, and 87 is every liable design whatever parent it pairs. The looser figure is not false
    as a subset statement and it is the flattering framing, because it makes a recurrence in one
    parent read as a property of two thirds of the panel.

    ⚠ RECOMPUTED, NOT TAKEN FROM THE PROSE. The 61 *NR4A3*-attributed designs' duplexes start at
    0-based 689, 690, 691 (36 + 18 + 5 = 59 — three register shifts of one window) and at 3412, 3413
    (1 + 1 = 2). "The same site" is therefore defined here as a cluster of starts whose windows
    overlap, never as a typed count.
    """
    pd = (_load("aso-parent-gap-pairing.json") or {}).get("per_design") or []
    cut = _parent_cut_bp()
    liable = [r for r in pd if (r.get("longest_parent_duplex_bp_through_gap") or 0) >= cut]
    attributed = [r for r in liable if r.get("parent") == "NR4A3"]
    starts = sorted(r["parent_start_0based"] for r in attributed)
    if not starts:
        raise SystemExit(
            "Table 4's ΔΔG note says which of the mature-parent duplexes are one recurring site, and "
            "aso-parent-gap-pairing.json reports no wild-type NR4A3 attribution to cluster. "
            "Re-derive it rather than printing a share over a population nothing measures.")
    clusters, cur = [], [starts[0]]
    for prev, nxt in zip(starts, starts[1:]):
        if nxt - prev < GEOMETRY.oligo_len:      # the two duplex windows overlap: one site
            cur.append(nxt)
        else:
            clusters.append(cur)
            cur = [nxt]
    clusters.append(cur)
    return max(len(c) for c in clusters), len(attributed), len(liable)


def _margin_gloss():
    """What the "gap-level margin" column IS, worded once and printed under every table with one.

    ⛔ IT WAS DEFINED IN TABLE 1's CAPTION AND NOWHERE ELSE (audit, 2026-08-19), while Tables 2, 3,
    4 and 5 all print the column — and Table 3 makes it the RANKING every one of its rows is chosen
    by. A caption is the part of a paper most likely to be read on its own, so a column whose
    definition is four tables back is an undefined column in every carrier but one. Printed rather
    than cross-referenced for the same reason `_rule_audit_note` is.

    ⚠ DERIVED FROM THE GEOMETRY, so a gap change reaches the sentence rather than leaving it
    describing a catalytic gap the panel no longer has.
    """
    return (f"The gap-level margin is the count of bases inside the {_word(GEOMETRY.gap_nt)}-nucleotide "
            f"catalytic gap that no wild-type parent carries at that position, taken on the shorter "
            f"side of the junction; it runs from 1 to {GEOMETRY.gap_nt // 2}, the geometry's ceiling "
            f"of half the gap rounded down, and it is a count of bases and not a score.")


def _junction_sort_key(label):
    """Partner alphabetically, then donor exon NUMERICALLY, then acceptor exon numerically.

    ⛔ TABLES 2 AND 3 WERE SORTED AS STRINGS AND NAMED NO KEY (display-item review, 2026-08-19).
    Both opened `EWSR1 e10, e12, e13, e15, e1, e4, e7, e9` — exon 1 filed between exon 15 and exon 4,
    which is what `sorted()` does to `e1` beside `e10` and what no reader looking up a patient's exon
    expects. Neither caption named a sort key at all, so the order looked deliberate. This is the
    one place the key lives, both tables use it, and both captions now name it.
    ⚠ IT REFUSES TO INVENT AN ORDER IT CANNOT READ: a label whose exon parts do not parse sorts on
    the raw string and stays adjacent to its partner rather than being silently moved to an end.
    """
    m = re.match(r"^([A-Za-z0-9]+)_e(\d+)__([A-Za-z0-9]+)_e(\d+)$", label)
    if not m:
        return (label, 0, "", 0, label)
    return (m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), "")


_JUNCTION_SORT_NOTE = ("Rows are in ascending order of partner, then of donor exon number, then of "
                       "*NR4A3* acceptor exon number.")


def _screen(name):
    """The raw per-junction screen behind a collapse row, or None."""
    p = os.path.join(MOD, name)
    return json.load(open(p)) if os.path.exists(p) else None


def _hybridisable(oligo):
    """Retained hits that an antisense oligonucleotide could actually hybridise.

    ⛔ THIS COLUMN EXISTS BECAUSE TABLE 3 READ AS A REFUTATION OF THE PAPER'S HEADLINE. The
    near-match count reported by a screen is STRAND-BLIND — it is what the search returned, either
    strand — while the gap analysis beside it is orientation-filtered. So `GGCATATCAAGCGCTG`
    printed "2 -> 2" in a table whose caption said unmarked rows were orientation-filtered, for a
    design the Results call free of any sense-strand near-match. Both were true and the table said
    so nowhere: its two hits are both minus-strand. A reader adding a column found a contradiction
    that did not exist, which costs a paper more than an omission does.
    """
    hits = oligo.get("offtargets") or []
    return sum(1 for h in hits if not h.get("is_minus_strand"))


def _deep_lookup():
    """Every 16-mer design's deep-ceiling counts, keyed `(junction_label, sequence)`.

    ⛔ WHY TABLES 3 AND 4 NEEDED THIS COLUMN (round-3 review, 2026-08-14). Both tables are the
    DEFAULT-depth result, and the Results withdraw part of what they print: three Table 3 rows
    showed `0 on the sense strand, 0 gap-paired loci` for designs carrying 14, 29 and 30 hybridisable
    hits at ten times the ceiling, and every one of Table 4's nine rows printed a zero that §2.4
    withdraws for six of them. The captions said so in prose. **A caption is not where a reader
    checks a number** — the cell is, and a cell that reads clean beside a text that calls the
    design dirty reads as the text being wrong. `GGGCATATCTCTATAA` was the sharpest case: named in
    §4 as withdrawn with 14 gap-paired risks, and shown in Table 3 with none.

    The default-depth columns STAY, because they are the depth the corpus-wide counts elsewhere in
    the paper were computed at and dropping them would break that correspondence. This adds the
    measurement beside them rather than replacing it.

    ⚠ A design absent from the deep set is not a design with a deep count of zero. Three of the 190
    records failed at the deeper ceiling (FUS e5 twice, TFG e2 once), so they get `—` and never `0`
    — the distinction CLAUDE.md §4 exists for, and the reason this returns None rather than a
    default.

    ⛔ THE THREE VALUES GO IN THREE COLUMNS, NEVER IN ONE `a / b / c` CELL — and the first version of
    this change did exactly that and was caught by
    `test_graded_rescore_depth.py::test_no_residual_load_cell_pools_two_depths`. That guard scans
    EVERY cell of Table 4's design rows, not just the residual-load one, because the defect it was
    written for (`31.4 / 101 / 0 / 0`, a default-depth re-score pooled with a deep one) hid inside a
    cell shape that looks legitimate: `a / b` is the model-disagreement form and is fine, so a
    reader cannot tell a pooled cell from a real one by looking. Narrowing the guard to one column
    would have made this pass and would have re-opened the hole. The separator is the problem, so
    the separator is what changed.

    ⛔⛔ AND THE LOCUS COLUMN WAS THE SCREEN'S OWN FIELD, WHICH IS THE ONE FIELD IN THESE ARTIFACTS
    THAT MAY NOT BE READ (round-5 review, P0.3, fixed 2026-08-16). `n_loci_with_a_gap_spanning_hit`
    was computed at screen time under a `locus_of` that split any gene whose description carries a
    comma into one accession fallback per transcript variant, corrected in 5233cf867 — and the
    correction cannot be backfilled into a committed screen without re-running the search, so every
    committed screen still carries the inflated figure. Reading it here put 30 of the 187 deep
    16-mer records into Tables 3 and 4 over-counted, in the direction that makes a reagent look
    dirtier than the evidence supports, and — worse — put them there BESIDE the corrected figures:
    Table 2 and §3.3 print 1 locus for TCF12 e5 / `GGGCATATCCATCAGA` where Table 3 printed 17, and
    Table 2 prints 6 for the lead `GGGCATATCATCAAAC` where Table 3 printed 14. Same molecule, same
    depth, two numbers, one paper.

    ⭐ THE RECOUNT IS IMPORTED, NOT REIMPLEMENTED. `aso_gap_length_tradeoff.recount_loci` already
    does exactly this — `locus_of` over the stored hits, exact where the stored list is the complete
    one and a LOWER BOUND where it is truncated — and a second copy here is how the two tables come
    to disagree a second time. The deep screens retain every hit by construction
    (`aso_per_junction_table` refuses to build if one does not), so `exact` is true for all 187
    records today; the flag is carried anyway rather than assumed, because "all deep lists are
    complete" is a property of the current corpus and not of this function.
    """
    out = {}
    sys.path.insert(0, os.path.abspath(MOD))
    from aso_gap_length_tradeoff import recount_loci  # noqa: PLC0415
    try:
        screens = ass.load_screens(GEOMETRY, ass.BLAST_SCREEN, select=ass.is_deep)
    except Exception:                                        # noqa: BLE001
        return out                                           # no deep set on disk: columns read "—"
    for s in screens:
        lab = s.junction_label
        if not lab:
            continue
        for o in (s.artifact.get("oligos") or []):
            if o.get("status") != "screened":
                continue
            loci = recount_loci(o)
            out[(lab, o["antisense_5to3"])] = {
                "n": o.get("n_offtarget_near_matches"),
                "hyb": _hybridisable(o),
                "gap_loci": loci["n_loci_with_a_gap_spanning_hit"],
                # ⚠ A RECOUNT OVER A TRUNCATED LIST IS A LOWER BOUND, SO IT TAKES THIS TABLE'S
                # LOWER-BOUND MARKER — "≥", the same one the default-depth distinct-loci column
                # uses — and NOT the "≤" beside it. The two markers are not interchangeable and
                # mean opposite things: "≤" marks a cell still carrying the screen's frozen
                # over-counting figure, "≥" a count made over a sample of the hits. Rendering a
                # lower bound as "≤" would contradict this table's own legend.
                "gap_loci_is_exact": loci["exact"],
            }
    return out


def _deep_cells(d):
    """The three deep columns for one design, or three em-dashes where there is no deep reading.

    ⚠ "—" MEANS THE DEEP RE-SCREEN HAS NO READING FOR THIS DESIGN, NOT THAT IT FOUND NOTHING. Three
    of the 190 records failed at the deeper ceiling; rendering that as 0 would be the flattering
    direction and the one these tables have gone wrong in twice before.
    """
    if d is None:
        return "— | — | —"
    mark = "" if d["gap_loci_is_exact"] else "≥"
    return f"{d['n']} | {d['hyb']} | {mark}{d['gap_loci']}"


def _clean_designs(collapse):
    """The designs with no sense-strand near-match, over a hit list complete enough to say so.

    One home for the predicate the manuscript's headline rests on. The censoring restriction is
    load-bearing and is not a nicety: a design whose stored hits are all minus-strand says nothing
    about the hits it did not store, so it cannot be called clean. Dropping that restriction takes
    the count from nine designs at six junctions to twenty-four at eighteen.
    """
    out = []
    for s in collapse["screens"]:
        lab = s.get("junction_label")
        if not lab or not _orientation_filtered(s.get("orientation")):
            continue
        raw = _screen(s["screen"]) or {}
        for o in raw.get("oligos") or []:
            if o.get("status") != "screened":
                continue
            n = o.get("n_offtarget_near_matches")
            if n is None or n > SAVED_HITS or _hybridisable(o):
                continue
            out.append((lab, o))
    return sorted(out, key=lambda t: (t[0], t[1]["antisense_5to3"]))


def _default_depth_failures(collapse):
    """(submissions that failed at the default depth, records attempted) over the panel.

    ⛔ TABLE 3 AND TABLE 2 PRINTED DIFFERENT "best gap-level margin" FOR THE SAME JUNCTION AND
    NEITHER SAID WHY (cold-reader finding, 2026-08-17). `TCF12 e7::NR4A3 e3` reads margin 2 in
    Table 3 and 3 in Table 2; `TAF15 e12::NR4A3 e3` the same. A column headed *best* margin cannot
    be beaten by a design in the next table without one of the two being wrong.

    Both are right and the reconciliation is censoring, not ranking: the margin-3 design at each of
    those junctions is a `screen_failed` record at the default depth — "Remote end closed connection
    without response" — so it is absent from the collapse the whole of Table 3 is built from, and
    the only visible trace is a `designs screened` cell reading 4 where every other row reads 5.
    Table 2 selects from the deeper re-screens, where all seven of these designs did return.

    So the count is derived here and stated in Table 3's own legend. It is read from the screens the
    collapse names rather than globbed off disk, so it is the population the table is built from and
    cannot drift from it.
    """
    attempted = failed = 0
    for s in collapse["screens"]:
        if not s.get("junction_label"):
            continue
        for o in (_screen(s["screen"]) or {}).get("oligos") or []:
            attempted += 1
            failed += o.get("status") != "screened"
    return failed, attempted


def _deep_depth_failures(per_junction, registers):
    """(deep submissions that failed, records attempted) — and the identity Table 2's denominator rests on.

    ⛔ TABLE 2's "designs clearing the parent screen" DENOMINATOR WAS UNEXPLAINED AND READ AS A
    PARENT-SCREEN FIGURE (built-PDF finding, 2026-08-17). The column prints `n of m`, and m is 5 at
    most junctions, 4 at `TFG e2` and 3 at `FUS e5`. A reader has no way to know that the parent
    screen is offline and exhaustive over all 190 designs: as printed, the two short rows read as
    though the parent screen saw fewer designs at those seams, when what is short is the DEEP
    ALIGNMENT screen that supplies each row's rank key — `aso_per_junction_table._deep_screens` skips
    a record whose `status` is not `screened`, so a design whose deep submission failed at the remote
    service is absent from the junction's row set entirely and cannot be in either half of the cell.

    ⚠ THE IDENTITY IS ASSERTED, NOT TRUSTED, because the sentence this feeds is only true while it
    holds. Every seam of this panel admits the same number of junction-spanning registers, so the
    shortfall summed over the junctions must equal the number of failed deep submissions; if it ever
    does not, some junction is short a design for a reason the legend does not state, and printing
    the legend anyway would explain the shortfall away rather than report it.
    """
    failed = attempted = 0
    try:
        screens = ass.load_screens(GEOMETRY, ass.BLAST_SCREEN, select=ass.is_deep)
    except Exception:                                        # noqa: BLE001
        return 0, 0
    for s in screens:
        if not s.junction_label:
            continue
        for o in (s.artifact.get("oligos") or []):
            attempted += 1
            failed += o.get("status") != "screened"
    shortfall = sum(registers - j["n_designs_screened"] for j in per_junction["junctions"])
    if shortfall != failed:
        raise SystemExit(
            f"Table 2: the panel is short {shortfall} design row(s) against {registers} registers a "
            f"seam, and {failed} deep submission(s) failed; the legend explains the denominator by "
            "the failures alone, so re-derive it before regenerating rather than printing a "
            "sentence that accounts for a shortfall it cannot see")
    return failed, attempted


def _orientation_filtered(status):
    """Whether a screen's counts were actually filtered by alignment orientation.

    Delegated to the owning module so the definition has one home. If that import fails the answer
    is False — an unfiltered count printed as a measurement is the error this marker exists to
    prevent, so the fallback goes to the safe side rather than the convenient one.
    """
    try:
        sys.path.insert(0, os.path.abspath(MOD))
        from junction_aso_offtarget import (  # noqa: PLC0415
            screen_counts_are_orientation_filtered)
        return screen_counts_are_orientation_filtered(str(status or ""))
    except Exception:  # noqa: BLE001
        return False


def table1(atlas):
    """Per partner: the graded junction space and what it yields."""
    pairs = atlas["graded_pairs"]
    panels = {p["junction_label"]: p for p in atlas["panels"]}
    rows = []
    for partner in atlas["partners_scored"]:
        mine = [p for p in pairs if p["donor_symbol"] == partner]
        emit = [p for p in mine if p.get("grade") == "EMITTABLE"]
        pans = [panels[p["junction_label"]] for p in emit if p["junction_label"] in panels]
        gcs = [g for p in pans for g in (p.get("gc_range_fusion_specific") or [])]
        margins = [p.get("best_gap_specificity_margin") for p in pans
                   if p.get("best_gap_specificity_margin") is not None]
        rows.append({
            "partner": partner,
            "donor_exons": len({p["donor_exon_end"] for p in mine}),
            "pairs_graded": len(mine),
            "frame_compatible": len(emit),
            "with_a_fusion_specific_design": sum(1 for p in pans if p.get("n_fusion_specific")),
            "gc_range": f"{min(gcs):.1f}–{max(gcs):.1f}" if gcs else "—",
            "best_gap_margin": max(margins) if margins else "—",
        })
    hdr = ("| 5′ partner | donor exons | exon pairs graded | in-frame | with ≥1 "
           "fusion-specific design | GC range of those designs (%) | best gap-level margin |")
    sep = "|---|---|---|---|---|---|---|"
    body = [f"| *{r['partner']}* | {r['donor_exons']} | {r['pairs_graded']} | "
            f"{r['frame_compatible']} | {r['with_a_fusion_specific_design']} | {r['gc_range']} | "
            f"{r['best_gap_margin']} |" for r in rows]
    n_emit = atlas["n_emittable_junctions"]
    n_des = atlas["n_junctions_with_a_fusion_specific_design"]
    # ⚠ THE LABEL IS DERIVED. It read "all four" while the table listed five partners, because the
    # word was typed when four was true and the atlas later gained TFG.
    tot = (f"| **all {len(rows)} partners** | — | **{len(pairs)}** | **{n_emit}** | **{n_des}** "
           f"| — | — |")
    return "\n".join([hdr, sep] + body + [tot])


def table3(collapse, chance, atlas, per_junction):
    """Per screened junction: predicted load for the design the paper's own ranking selects.

    ⛔ TWO WAYS THIS TABLE WENT WRONG ON ITS FIRST GENERATION, BOTH IN THE FLATTERING DIRECTION.

    (a) It labelled a column "best gap-level margin" and filled it from the screens'
    `specificity_margin`, which is the OLIGO-WIDE margin — a different quantity that runs 6-8 where
    the gap-level margin runs 1-3. Table 1 reads the gap-level field from the atlas, so the two
    tables disagreed about the same design by a factor of nearly three, and the larger number was
    the one that looked better. The distinction between the two is a point the Methods make
    explicitly; a table contradicting it is worse than a table omitting it.

    (b) It picked each junction's representative design by fewest off-target loci. That ranks a
    RIGHT-CENSORED design, whose locus count is a lower bound, above an uncensored one whose count
    is exact — so the design chosen to represent a junction was systematically the one we know least
    about. The representative is now chosen by gap-level margin, which is what the manuscript says
    it ranks by, with the off-target columns describing whichever design that is.
    """
    # ⛔ THIS TABLE PRINTED A NAMED SEQUENCE AT THREE JUNCTIONS WHERE NO DESIGN CLEARS THE PARENT
    # SCREEN (cold-reader finding, 2026-08-17). Table 2 reads `0 of 5`, `0 of 5` and `0 of 4` at
    # TAF15 e14, TCF12 e3 and TFG e2 and prints a dash where the design would be — every design
    # tiled at those seams pairs a wild-type parent gene through the whole catalytic gap. Table 3
    # ranks by gap-level margin instead, so it names the highest-margin design there and prints its
    # sequence like any other row. Its caption warns that its rows are the highest-margin designs
    # rather than the cleanest; it did not warn that at three junctions the row is a design every
    # parent screen condemns. A laboratory with a TCF12 exon-3 fusion reads this table and finds a
    # sequence.
    # ⭐ THE PREDICATE IS TABLE 2's OWN COLUMN, from the artifact that owns it, never a typed list of
    # junctions: a seam that gains a clearing design upstream loses the marker here without an edit.
    no_design_clears = {j["junction_label"] for j in per_junction["junctions"]
                        if j["n_designs_clearing_the_parent_screen"] == 0}

    # ⛔ THE LEGEND ANTICIPATED ONE DIRECTION AND THE TABLE GOES BOTH WAYS (built-PDF finding,
    # 2026-08-17). It told a reader that Table 2 may name a design of HIGHER margin at the same
    # junction — the censoring reconciliation `_default_depth_failures` documents — and at `EWSR1
    # e10` and `EWSR1 e4`, where all five designs returned at this depth, Table 2 names a design of
    # LOWER margin instead. That direction has a different cause and is not a discrepancy: Table 2
    # ranks by parent liability, then pre-mRNA sites, then gene loci, and reaches margin only as a
    # tie-break, so a cleaner design of lower margin outranks this table's highest-margin one. A
    # reader who has been given one explanation and meets the opposite case has to assume one of the
    # two tables is wrong.
    # ⚠ WHICH DIRECTIONS OCCUR IS MEASURED HERE, not asserted in the legend, so a corpus in which one
    # of them stops happening does not leave a sentence explaining a case the table no longer has —
    # the same rule as the ‡, † and ³ blocks.
    best_available_margin = {
        j["junction_label"]: (j.get("best_available") or {}).get("gap_specificity_margin")
        for j in per_junction["junctions"]}
    margin_up = margin_down = False

    gap_margin = {}
    for pan in atlas["panels"]:
        for des in pan.get("designs") or []:
            gap_margin[(pan["junction_label"], des["antisense_5to3"])] = \
                des.get("gap_specificity_margin")

    #: ⛔ TABLE 3 HAD NO PARENT-DUPLEX COLUMN, AND SIX UNMARKED ROWS PAIRED A PARENT THROUGH THE
    #: WHOLE GAP (blind safety screen, 2026-08-19). The † marks JUNCTIONS where nothing clears the
    #: parent screen, so an unmarked row reads as unobjectionable — but the design this table prints
    #: is its highest-MARGIN design, not its cleanest, and six of those pair a wild-type parent
    #: through the entire catalytic gap at eleven base pairs, five of them against wild-type NR4A3,
    #: the transcript the modality exists to spare. §4.5 calls exactly that property "this paper's
    #: central negative", and nothing on the page contradicted the reader's assumption. The column
    #: Table 2 and the CSV already carry now travels with the sequence here too.
    parent_dup = {}
    for r in (_load("aso-parent-gap-pairing.json") or {}).get("per_design") or []:
        parent_dup[(r["junction"], r["antisense_5to3"])] = (
            r.get("longest_parent_duplex_bp_through_gap"), r.get("parent"))

    by_j, filtered = {}, {}
    for s in collapse["screens"]:
        lab = s.get("junction_label")
        if not lab:                              # the modelled reference junctions carry no label
            continue
        by_j.setdefault(lab, []).extend(s["per_oligo"])
        # ⛔ A FILTERED AND AN UNFILTERED ROW MUST NOT RENDER ALIKE (2026-08-12). Twenty junctions
        # were re-screened with orientation parsed and filtered; four older ones were not, and their
        # counts still include minus-strand hits — which across this corpus is half of them. Printed
        # in one table with no marking, a reader comparing TCF12 e17 (filtered, 0) against FUS e5
        # (unfiltered, >=5) would be comparing two different quantities and would reasonably
        # conclude the second is worse. It may not be. The marker says which is which.
        # ⛔ THE SUBSTRING SNIFF THAT USED TO LIVE HERE FAILED OPEN (2026-08-12). It read
        # `"UNPARSED" not in status`, chosen so an unrecognised value would be treated as
        # unfiltered — the safe direction. It was not safe: the audit that followed added a THIRD
        # state, `orientation_parsed_but_labels_are_strand_blind_upper_bounds`, for screens whose
        # `hit_frame` is present and whose labels never used it. That name does not contain
        # "UNPARSED", so the sniff answered `True` and four upper-bound rows rendered as filtered
        # measurements. A test for the absence of one word cannot be a test for the presence of a
        # property. Ask the owning module the positive question instead.
        filtered[lab] = _orientation_filtered(s.get("orientation"))

    # Strand is a per-HIT fact, and the collapse artifact keeps per-oligo summaries only, so the
    # hybridisable count has to come from the screen itself.
    hyb_by_j = {}
    for s in collapse["screens"]:
        lab = s.get("junction_label")
        if not lab:
            continue
        raw = _screen(s["screen"]) or {}
        for o in raw.get("oligos") or []:
            if o.get("status") == "screened":
                hyb_by_j.setdefault(lab, {})[o["antisense_5to3"]] = _hybridisable(o)

    le1 = {}
    for r in chance["per_design"]:
        j = r["junction"]
        if "insilico" in j:
            continue
        le1.setdefault(j, []).append(r.get("offtarget_le1mm") or 0)

    # ⚠ THE COLUMN NAMES ARE THE THIRD THING THIS TABLE GOT WRONG. A column headed "gap-paired
    # near-matches" was filled with the design's TOTAL near-match count, which is larger — the lead
    # candidate reads 9 there and has 8 gap-paired. Total near-matches and gap-paired
    # near-matches are both worth printing and are printed separately; the collapse artifact stores
    # gap-paired resolved to LOCI but not to transcripts, so that is the column that exists.
    deep = _deep_lookup()
    # ⛔ A LEGEND FOR A MARKER NO ROW CARRIES IS WORSE THAN NO LEGEND, AND FOOTNOTE ³ HAD BECOME ONE
    # (cold-reader finding, 2026-08-17). It explained that "—" means the deeper re-screen returned
    # no result — and no cell of this table has carried a "—" since the representative design at
    # every junction gained a deep record. The three deep failures are all at NON-representative
    # designs, so they reach Table 3 nowhere. Same defect the `‡` block was fixed for, same fix:
    # the sentence is emitted only where a row actually carries the marker.
    deep_missing = no_design_clears_marked = False
    hdr = ("| junction | designs screened | best gap-level margin | that design | near-matches, "
           # ⛔ THE MARKERS USED TO RUN ¹ ² ⁵ AND ² ¹ ⁵ ⁵ ⁵ ACROSS THE HEADER (round-7 review,
           # 2026-08-16). ³ and ⁴ belong to Table 4, so a reader of Table 3 hunting for them found
           # nothing, and the two Table 3 markers appeared out of order in the header besides. They
           # now ascend in reading order and run contiguously, and Table 4's continue from them.
           # ⛔ TWO OPPOSITE CENSORING SENSES IN ADJACENT COLUMNS, KEYED ONLY ON PAGE ONE
           # (display-item review, 2026-08-19). "≥" is a floor and "≤" a ceiling, twenty of the
           # thirty-eight rows carry both, and the sentence that says which is which lives in note
           # ¹ under the caption — which is on the FIRST page of a table that runs to three. The
           # builder repeats the <thead> on every continuation page and nothing else, so the sense
           # of each mark belongs in the header of the column that carries it, where a reader
           # meeting the row meets the key.
           "either strand (transcripts → loci; ≥ is a lower bound) | of the retained hits, on the "
           "sense strand¹ (≥ is a lower bound) | loci with a "
           "gap-paired hit (≤ is an upper bound) | of those, predicted models only² | "
           "at the deeper ceiling: near-matches³ | of those, on the sense strand³ | "
           "loci with a gap-paired hit³ | "
           "longest parent duplex through the gap (bp) | "
           "≤1-mismatch matches across that junction's designs, median (max) |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|---|"
    rows = []
    for lab in sorted(by_j, key=_junction_sort_key):
        ol = by_j[lab]
        # ⚠ BOTH ROW MARKERS ARE COMPUTED HERE, ABOVE THE FAILED-SCREEN BRANCH. A junction whose
        # screens all failed still has a Table 2 parent-screen column, so the marker that warns
        # about its designs must not depend on this table having a row body to hang it on.
        mark = "" if filtered.get(lab) else " ‡"
        if lab in no_design_clears:
            mark += " †"
            no_design_clears_marked = True
        # ⛔ A JUNCTION WHOSE EVERY SCREEN FAILED MUST APPEAR AS FAILED, NOT CRASH AND NOT VANISH
        # (2026-08-12). EWSR1 e10 returned 0 of 5 — all five BLAST submissions failed at the remote
        # service — so its `per_oligo` list is empty and `ranked[0]` raised IndexError, which killed
        # the whole generator and silently left the PREVIOUS table on disk. Two failures in one: a
        # table that looked current and was not, and a junction that would otherwise be missing from
        # the paper with no statement that it was ever attempted. An absent reading is not a reading
        # of absence (CLAUDE.md §4), so the row is emitted saying exactly that.
        if not ol:
            rows.append(f"| {lab.replace('__', '::').replace('_', ' ')}{mark} | 0 of 5 — every BLAST "
                        f"submission failed at the remote service | — | — | — | — | — | — | — | "
                        f"— | — | — | — |")
            deep_missing = True
            continue
        ranked = sorted(ol, key=lambda o: -(gap_margin.get((lab, o["antisense_5to3"])) or -1))
        best = ranked[0]
        gm = gap_margin.get((lab, best["antisense_5to3"]))
        ba = best_available_margin.get(lab)
        if gm is not None and ba is not None:
            margin_up = margin_up or ba > gm
            margin_down = margin_down or ba < gm
        # ⛔ THREE COLUMNS SHARED ONE CENSORING MARKER AND ONLY ONE OF THEM EARNED IT
        # (2026-08-12). `right_censored` means the design has more near-matches than the 15 this
        # module retains, and that bounds ONLY the locus recount, which is done from the retained
        # hits. The other two are not bounded by it: the reported near-match count is the screen's
        # complete figure and is bounded instead by BLAST's own 50-hit hitlist, and the
        # gap-paired locus count now comes from the screen, computed over every ranked hit before
        # truncation, so it is exact. Marking an exact 0 as "≥0" is not a harmless over-caution —
        # it is unreadable, because "≥0" is true of every number and says nothing.
        # ⚠ AND THE FROZEN FIGURE IS AN UPPER BOUND, NOT AN EXACT ONE (2026-08-13). The screen's
        # count was computed at screen time, under a `locus_of` that has since been corrected: it
        # split any gene whose description carries a comma into one fallback per accession, so
        # TCF12 e5 printed 17 loci for seventeen variants of PIK3CG. Where the stored list is
        # complete the collapse now recounts with the current rule and the value is exact; only a
        # truncated list still carries the frozen figure, and it is marked "≤" rather than bare.
        cens_loci = "≥" if best["right_censored"] else ""
        cens_near = "≥" if (best["n_transcript_near_matches_reported"] or 0) >= HITLIST_SIZE else ""
        #: ⚠ "≤0" IS SELF-CANCELLING AND READS AS A TYPESETTING ERROR (blind screen, 2026-08-19).
        #: The marker means the screen's own figure may OVER-count, so the printed value is an
        #: upper bound. For a non-negative count an upper bound of zero IS zero — there is
        #: nothing left for the marker to say, and the prose reads those cells as plain zeros
        #: anyway ("its single default-depth zero"). The marker is therefore suppressed at
        #: zero, where it carries no information, and kept everywhere it does.
        cens_gap = ("≤" if (best.get("n_loci_with_a_gap_spanning_hit_is_from_the_screen")
                            and best.get("n_loci_with_a_gap_spanning_hit")) else "")
        vals = sorted(le1.get(lab, []))
        med = vals[len(vals) // 2] if vals else "—"
        mx = max(vals) if vals else "—"
        # The hybridisable count is over the RETAINED hits, so on a truncated list it is a lower
        # bound and says so. "≥0" is meaningful in this one column and nowhere else in this table:
        # zero retained sense-strand hits out of a list that was cut short is exactly the state
        # that stops a design being called clean, and printing a bare 0 there would assert the
        # opposite of what the screen knows.
        hyb = hyb_by_j.get(lab, {}).get(best["antisense_5to3"])
        hyb_cell = "—" if hyb is None else f"{'≥' if best['right_censored'] else ''}{hyb}"
        deep_rec = deep.get((lab, best["antisense_5to3"]))
        deep_missing = deep_missing or deep_rec is None
        deep_cell = _deep_cells(deep_rec)
        rows.append(
            f"| {lab.replace('__', '::').replace('_', ' ')}{mark} | {len(ol)} | "
            f"{gm if gm is not None else '—'} | 5′-{best['antisense_5to3']}-3′ | "
            f"{cens_near}{best['n_transcript_near_matches_reported']} → "
            # "of those" means OF THE GAP-SPANNING LOCI, so it is the intersection of the two
            # named lists, not the whole-design predicted-only count — which is larger and would
            # have overstated how much of the liability sits in predicted annotation.
            f"{cens_loci}{best['n_distinct_loci']} | {hyb_cell} | "
            f"{cens_gap}{best['n_loci_with_a_gap_spanning_hit']} | "
            f"{len(set(best.get('loci_with_a_gap_spanning_hit') or []) & set(best.get('loci_seen_only_as_predicted_models') or []))} | "
            f"{deep_cell} | {_parent_dup_cell(parent_dup.get((lab, best['antisense_5to3'])))} | "
            f"{med} ({mx}) |")
    return ("\n".join([hdr, sep] + rows), any(not v for v in filtered.values()), deep_missing,
            no_design_clears_marked, margin_up, margin_down)


#: Clinical-occurrence tiers, rendered for a reader. The tier vocabulary is owned by
#: `aso_per_junction_table.PUBLISHED_BREAKPOINTS`; this only names the three states.
_TIER_LABELS = {
    "published_exon_resolved_breakpoint": "published",
    "partner_published_this_exon_not_reported": "exon not reported",
    "no_published_exon_resolved_breakpoint": "none published",
}


#: A reference that is a SEQUENCE DEPOSIT rather than a report. `breakpoint_refs` entries are
#: written `"<source>: <accession>"`, and only these sources resolve a breakpoint by carrying the
#: chimeric sequence itself. A source added upstream and not named here reads as a report, which is
#: the safe direction: it withholds the deposit marker rather than asserting one.
_DEPOSIT_ACCESSION = re.compile(r"^\s*(GenBank|RefSeq|ENA|DDBJ|INSDC)\s*:", re.I)


def _tier_cell(j):
    """The clinical-occurrence cell, with a deposit-resolved row marked as one.

    ⛔ TABLE 2's LEGEND CONTRADICTED ITS OWN ROWS (cold-reader finding, 2026-08-17). The legend
    defined “none published” as "no exon-resolved breakpoint has been reported for that partner at
    all", and the table printed `TFG e7::NR4A3 e3` as **published** beside five *TFG* rows reading
    **none published**. Both cannot hold of one partner under that definition, and a reader has no
    way to see which of the two is the loose one.

    Neither is wrong; the labels were. `aso_per_junction_table.PUBLISHED_BREAKPOINTS` resolves the
    *TFG* seam from ONE deposited chimeric mRNA, while `PARTNERS_WITH_ANY_PUBLISHED_EXON`, which
    decides the other five rows, contains only partners a PAPER resolves to an exon. So the three
    tiers are drawn on two different records, and the row that sits on a deposit is the one that has
    to say so.

    ⛔⛔ AND THE FIRST PREDICATE FOR THAT — "no PMID among the refs" — GRADED THE TWO DEPOSIT-
    RESOLVED SEAMS DIFFERENTLY (filed as a MAJOR by two independent blind screens of the built PDF,
    2026-08-17, one per format). *TCF12* e5 carries BOTH `PMID: 11156374` and
    `GenBank: AF289510.1`, so the PMID suppressed the marker and the row printed a bare
    **published** — while §2.3 says in terms that that report "describes a chimera retaining the
    first 108 TCF12 residues, and names no exon; the same authors deposited the chimeric cDNA, and
    that deposit resolves the junction to the nucleotide". `PUBLISHED_BREAKPOINTS`' own note beside
    the entry says the same thing at greater length. *TFG* e7 is the identical situation and printed
    **published (deposit)** only because its refs happen to carry no PMID at all.

    ★ THE PRESENCE OF A PMID IS NOT THE QUESTION; WHAT RESOLVES THE EXON IS. A report can establish
    the fusion and still not name an exon, which is exactly what happened at *TCF12*, so a predicate
    that reads "a paper is cited" as "a paper resolved the exon" answers a different question than
    the label asks. The predicate is now the PRESENCE OF A SEQUENCE ACCESSION among the refs, which
    separates the five published rows correctly and stays derived rather than a typed list of
    junctions: measured over `PUBLISHED_BREAKPOINTS`, the two deposit-resolved seams are exactly the
    two carrying an accession and the other three carry PMIDs alone. A seam whose exon is later
    named in prose loses the marker upstream, where the refs live.
    """
    tier = _TIER_LABELS.get(j["clinical_tier"], j["clinical_tier"])
    if j["clinical_tier"] != "published_exon_resolved_breakpoint":
        return tier
    refs = [str(r) for r in (j.get("breakpoint_refs") or [])]
    if any(_DEPOSIT_ACCESSION.match(r) for r in refs):
        return f"{tier} (deposit)"
    return tier


#: ⛔ TABLE 5 IS A ROW SPEC, NOT A DATA TABLE. Each entry names a reagent's EDITORIAL ROLE and where
#: to READ it from; every number in the rendered row is fetched from the artifact named here and none
#: is typed. The order is the order §4 makes the decisions in: the two leads first, then each rung of
#: the coverage ladder, then the seams reported beside the panel, then the two contrast arms.
#: ⚠ THE ROLE IS THE ONLY EDITORIAL FIELD. If a role and its artifact ever disagree — a "lead reagent"
#: whose junction is no longer in ladder rung 0 — the coverage cell will say so, because the coverage
#: cell is read from the ladder rather than from this list.
_TABLE5_ROWS = (
    ("lead reagent", "panel", "EWSR1_e12__NR4A3_e3", None),
    ("lead reagent", "panel", "TAF15_e6__NR4A3_e3", None),
    ("coverage rung", "panel", "EWSR1_e13__NR4A3_e3", None),
    ("coverage rung", "noncoding", "EWSR1_e7__NR4A3_e2", None),
    ("coverage bound", "panel", "TCF12_e5__NR4A3_e3", None),
    # ⛔ THIS ROW WAS MISSING AND THE TABLE COULD NOT NOTICE (round-7 review, A5-F2, 2026-08-16).
    # TFG e7::NR4A3 e3 qualifies for the best-supported buildable panel on both of the ladder's
    # conditions — `clinical_tier == "published_exon_resolved_breakpoint"` and a reagent through all
    # five deep screens — and the ladder lists it in `⛔_qualifying_but_contributing_exactly_zero`
    # beside PGR e2, which HAS a row. §2.3 resolves this seam exactly as it resolves TCF12 e5, from a
    # deposited chimeric mRNA rather than from a paper, and §2.7 names its margin and parent run
    # among the five published seams. It was absent for no reason but that this list is typed: the
    # spec is editorial, the qualifying set is the artifact's, and nothing compared them. The guard
    # in `table5` now does, so the next qualifying junction cannot be dropped in silence.
    ("published seam in the panel", "panel", "TFG_e7__NR4A3_e3", None),
    ("beside the panel", "noncoding", "EWSR1_e13__NR4A3_e2", None),
    ("beside the panel", "noncoding", "TAF15_e6__NR4A3_e2", None),
    ("beside the panel", "noncoding", "PGR_e2__NR4A3_e2", None),
    ("gap-length control", "geometry", "EWSR1_e12__NR4A3_e3", "5-8-5"),
    ("margin contrast arm", "design", "EWSR1_e12__NR4A3_e3", "GCATATCATCAAACCA"),
)


def _premrna_unscanned_donors(noncoding):
    """(donor genes of Table 5's exon-2 rows the pre-mRNA screen never searched, the genes it did).

    ⛔ TABLE 5's MEMBERSHIP SENTENCE WAS UNTRUE OF ONE OF ITS OWN ROWS (built-PDF finding,
    2026-08-17). The caption said membership needs "five completed deep screens", and the *PGR* row
    has a pre-mRNA compartment the article states plainly is unmeasured — §2.6: the screen's parent
    set does not include *PGR*, whose unspliced sequence the committed cache does not carry.

    ⭐ THE ROW IS NOT AN EXCEPTION AND THE GUARD IS NOT WRONG; THE SENTENCE WAS COUNTING THE WRONG
    THING. `table5`'s guard refuses on a qualifying junction with no ROW, never on a missing screen,
    and the ladder's condition (ii) is read from each source table's own completeness flag —
    `screens_complete`, which the non-canonical-acceptor table sets from `n_screens_outstanding == 0`,
    i.e. five screens that RAN over the seam's designs. A screen can run over a design and search
    nothing of that design's own donor: `screens.premrna.genes` lists the six parents the pre-mRNA
    scan carried sequence for, and *PGR* is a sixth partner outside them. So the condition is a
    statement about screens run, not about compartments measured for every gene a row names, and the
    legend now says which.

    ⚠ READ, NEVER TYPED, and it refuses rather than printing the unqualified sentence: if the screen
    block stops naming its parent set this cannot tell whether a donor was searched, and the flatter
    legend — the one with no caveat — is the wrong thing to fall back to.
    """
    scanned = sorted((noncoding.get("screens") or {}).get("premrna", {}).get("genes") or [])
    if not scanned:
        raise SystemExit(
            "Table 5: the non-canonical-acceptor table's pre-mRNA screen block names no parent set, "
            "so the legend cannot say which of its rows have a pre-mRNA reading of their own donor. "
            "Re-derive that block rather than regenerating a caption that claims five completed "
            "screens for every row.")
    donors = []
    for _, src, label, _ in _TABLE5_ROWS:
        if src != "noncoding":
            continue
        gene = label.split("_")[0]
        if gene not in scanned and gene not in donors:
            donors.append(gene)
    return sorted(donors), scanned


def _ladder_cell(rung):
    """One ladder entry rendered as its (coverage cell, basis cell). One home for the formatting."""
    cell = f"{rung['coverage_percent']:.1f}%"
    lo, hi = rung["coverage_percent_range"]
    if lo != hi:
        cell += f" ({lo:.1f}–{hi:.1f})"
    # ⚠ A RUNG THAT BUYS NOTHING MUST SAY SO IN ITS OWN CELL. Two consecutive rungs print the
    # same cumulative figure when the second adds zero, and a reader who does not compare rows
    # reads the second as having bought it. The delta is in the artifact; print it.
    # ⛔ AND THE DELTA WAS GATED ON `kind == "rung"`, WHICH SUPPRESSED IT WHERE IT MATTERS MOST
    # (round-7 review, B3-F1, 2026-08-16). The two bounds carry +15.9 and +3.4 between the last
    # buildable rung and 98.3%, so the larger of the two steps to the ladder's top figure is the
    # one the table declined to print. A bound's increment is exactly as derived as a rung's.
    delta = rung.get("delta_percent_vs_previous")
    if delta is not None:
        cell += f" (+{delta:.1f})"
    basis = "arithmetic bound" if rung["kind"] == "bound" else "single series, cumulative"
    return cell, basis


def _ladder_coverage(ladder):
    """(junction -> (coverage cell, basis, ladder index), the ladder entries no junction claims).

    ⛔ THE COVERAGE CELL IS THE LADDER'S, NOT THE ROW SPEC'S. A junction's cumulative figure is the
    coverage of the FIRST rung that contains it, because that is what "cumulative through this row"
    means; the two leads are one rung and therefore carry one figure between them, which the caption
    says. A junction that qualifies for the best-supported panel but moves the estimate by nothing
    prints WHY it moves nothing rather than a zero, since the two reasons are different — the partner
    is absent from the 58-case cohort, or the partner is present and this exon pair carries no count
    in the measured within-partner distribution. Both are in the artifact and neither is inferred.

    ⛔⛔ AND FIRST-RUNG-WINS SILENTLY DELETED A LADDER ROW (round-7 review, B3-F1, fixed 2026-08-16).
    The claim was a `setdefault` per junction, so a ladder entry could only reach the table THROUGH a
    junction no earlier entry contained. The 94.8% bound — "every remaining *EWSR1* breakpoint
    covered" — adds no junction at all: it adds THREE UNNAMED reagents at breakpoints the retrieved
    record does not resolve, so its junction list is identical to the rung below it and every one of
    its junctions was already claimed. The row vanished, and with it the fact that 15.9 of the 19.3
    points between the last buildable rung and 98.3% come from an assumption about breakpoints
    nothing here reaches. What was left read as though *TCF12* bought the whole step.
    A ladder entry that no junction claims is returned here so the table can render it on its own
    terms — a bound with no reagent to name is still a row, and its cell is the reason the figure
    above it is not a target.
    """
    out, claimed = {}, set()
    for i, rung in enumerate(ladder["ladder"]):
        cell, basis = _ladder_cell(rung)
        for j in rung["junctions"]:
            if j not in out:
                out[j] = (cell, basis, i)
                claimed.add(i)
    pm = ladder["best_supported_buildable_panel"]["panel_membership"]
    for key, why in (("⛔_in_cohort_but_moving_NOTHING",
                      "partner in the cohort, this exon pair uncounted in it"),
                     ("⛔_qualifying_but_contributing_exactly_zero",
                      "partner absent from the cohort behind the denominator")):
        for j in pm[key]["junctions"]:
            if j not in out:
                out[j] = ("adds nothing", why, None)
    unclaimed = [(i, r) for i, r in enumerate(ladder["ladder"]) if i not in claimed]
    return out, unclaimed


def table5(per_junction, noncoding, gap, ladder):
    """Every junction-spanning reagent §4 names, with what it costs on each screen and what it
    buys in coverage. ⛔ NOT the three controls §4 also requires: none of them has a sequence, a
    geometry or a screen result to print, and the caption says so rather than leaving it silent.

    ⛔ WHY A SEVENTH TABLE. The coverage apparatus was ~1,430 words of prose carrying five
    percentages on two incompatible bases, a ladder, a refused third series and a per-design recital
    of margins, loads and parent duplexes. Every one of those is a cell. What a table cannot carry is
    the two facts the prose keeps: that no oligonucleotide serves two breakpoints of the same
    partner, and that the exon-2 acceptor rows are reported beside the panel and never pooled into
    it — so those stay in prose and everything else moves here.

    ⚠ ROWS FROM FOUR ARTIFACTS, AND THE ROW SAYS WHICH. The panel rows come from the manuscript's
    38-junction table; the exon-2 acceptor rows from the non-canonical-acceptor table, which is a
    different table for a stated reason and is never pooled with the first; the gap-length control
    from the geometry trade-off artifact; the margin arm from the per-design list at its own
    junction. A row's coverage cell always comes from the coverage ladder, never from its screen.
    """
    panel = {j["junction_label"]: j for j in per_junction["junctions"]}
    nonc = {j["junction_label"]: j for j in noncoding["junctions"]}
    lead = gap["lead_reagent_at_the_most_commonly_reported_seam"]["by_geometry"]
    cover, unclaimed = _ladder_coverage(ladder)
    default_arch = GEOMETRY.architecture

    # ⛔ THE ROW SPEC IS TYPED, SO SOMETHING MUST COMPARE IT WITH THE ARTIFACT (round-7, A5-F2).
    # `_TABLE5_ROWS` is an editorial ordering and the set of junctions that BELONG in it is not:
    # the ladder's `panel_membership` names every junction with a published exon-resolved breakpoint
    # AND a reagent through all five deep screens, both conditions read from the tables that own
    # them. TFG e7::NR4A3 e3 satisfied both and was absent for a year of revisions because no check
    # existed. A missing row in a table captioned as complete is unfindable by reading the table.
    qualifying = set(ladder["best_supported_buildable_panel"]["panel_membership"]["junctions"])
    named = {lb for _, src, lb, _ in _TABLE5_ROWS if src in ("panel", "noncoding")}
    if qualifying - named:
        raise SystemExit(
            "Table 5 omits " + ", ".join(sorted(qualifying - named)) + ": the coverage ladder's "
            "best-supported buildable panel qualifies it on a published exon-resolved breakpoint "
            "and five specificity screens run over its designs, and this table's caption claims "
            "every such seam. Add "
            "the row to _TABLE5_ROWS, or state in the caption why it is out of scope.")

    #: The loose end of the cited range, from the block that reads both cuts. Never typed here.
    _loose = _cut_sensitivity()["loose_bp"]

    def _duplex(bp, gene):
        #: ⚠ `0 bp`, NOT `none` (2026-08-17). This column and Table 7's "mature-parent duplex
        #: through the whole gap (bp)" are the same measurement on the same molecules, and for the
        #: 5-8-5 control they printed "none" here and "0" there — one value, two renderings, in
        #: adjacent display items. `none` is also the weaker of the two words in a paper that
        #: insists an absent reading is not a reading of absence: this IS a reading, the search ran
        #: over all six parent transcripts and returned nothing, and a numeral says so where a word
        #: leaves room for "not screened".
        #: ⛔⛔ AND THE ROW CARRIES THE VERDICT AT THE OTHER END OF THE CITED RANGE (display-item
        #: review, 2026-08-19). Box 1 says of the two lead reagents that "their longest parent runs
        #: through the gap are eight and nine base pairs against a criterion of ten, so at the
        #: seven-base-pair end of the range §5 bounds that criterion by, both fall inside the
        #: liability class this paper's central negative is about" — and this table, which is the
        #: table §4 prices and the one a reader picks a reagent out of, printed `8 bp (*TFG*)` and
        #: `9 bp (*TFG*)` with no marker of any kind. The caption's cut caveat states the shift for
        #: the PANEL; it does not tell a reader scanning one row that THIS row is one of them. The
        #: verdict is a comparison against a cut, so it is computed per row rather than asserted,
        #: and it is printed for the clear rows as well: an unannotated cell would once again mean
        #: "not liable" by absence, which is the reading this document exists to refuse.
        if not bp:
            return f"0 bp; clear at {_word(_loose)}"
        cell = f"{bp} bp (*{gene}*)" if gene else f"{bp} bp"
        return cell + ("; liable at " if bp >= _loose else "; clear at ") + _word(_loose)

    def _bound_row(rung):
        """A ladder entry that no junction row carries, rendered on its own terms.

        ⚠ EVERY REAGENT CELL IS AN EM-DASH AND THAT IS THE POINT: the bound is priced on breakpoints
        for which this work names no oligonucleotide, and the count of reagents it would take is the
        artifact's own `n_reagents_additional_unnamed`. A row that filled those cells from anywhere
        would be inventing a panel.
        """
        cell, basis = _ladder_cell(rung)
        n = rung.get("n_reagents_additional_unnamed") or 0
        seq = f"— ({n} further reagents, none named)" if n else "—"
        #: ⚠ AND THE LABEL SAYS WHICH KIND OF BOUND IT IS (display-item review, 2026-08-19).
        #: Two rows carry "coverage bound": one prices breakpoints for which this work names no
        #: oligonucleotide at all, the other is a fully specified orderable reagent with real
        #: screens beside a 98.3% figure. A reader scanning the reagent column met a buildable
        #: 98.3% row. Derived from whether the entry names reagents, never typed.
        role = "coverage bound (no reagent named)" if n else "coverage bound"
        return basis, (f"| {role} | {rung['panel']} | {seq} | — | — | — | — | "
                       f"{cell} | {basis} |")

    # ⛔ TWO MEMBERSHIP CLASSES, NO STATED RULE (built-PDF finding, 2026-08-17). This table calls one
    # *NR4A3* exon-2 acceptor seam a "coverage rung" and the other three "beside the panel", while
    # the caption says exon-2 rows are never pooled into the panel — so the two classes looked like
    # a contradiction, and the rung contributes +0.0 besides, which makes it look like the mistake.
    # ⭐ THE RULE IS THE LADDER'S AND IS COLLECTED HERE RATHER THAN DESCRIBED: a junction the ladder
    # NAMES IN ONE OF ITS ENTRIES carries that entry's cumulative figure, and a junction that
    # qualifies for the best-supported buildable panel but appears in no entry carries "adds
    # nothing". `EWSR1 e7::NR4A3 e2` is in rung 2 — the ladder prices the type 2 transcript on the
    # same single series — while the other three exon-2 seams are in no entry at all. "Pooled into
    # the panel" is a different question with an unchanged answer: none of them is in the 38.
    ladder_backed_noncoding = [label for _, src, label, _ in _TABLE5_ROWS
                               if src == "noncoding" and (cover.get(label) or (None, None, None))[2]
                               is not None]

    rows, pending = [], list(unclaimed)
    for role, src, label, key in _TABLE5_ROWS:
        if src in ("panel", "noncoding"):
            j = (panel if src == "panel" else nonc)[label]
            b = j["best_available"]
            seq, margin, arch = b["antisense_5to3"], b["gap_specificity_margin"], default_arch
            load = f"{b['n_gap_paired']} → {b['n_gap_paired_loci']}"
            dup = _duplex(b["parent_duplex_bp"], b["parent"])
        elif src == "geometry":
            g = lead[key]
            seq, margin, arch = g["antisense_5to3"], g["gap_specificity_margin"], g["architecture"]
            load = (f"{g['alignment_screen']['n_true_cleavage_risk']} → "
                    f"{g['alignment_screen']['loci']['n_loci_with_a_gap_spanning_hit']}")
            dup = _duplex(g["mature_parent_duplex_through_whole_gap_bp"],
                          g["mature_parent_duplex_gene"])
        else:
            d = next(x for x in panel[label]["designs"] if x["antisense_5to3"] == key)
            seq, margin, arch = d["antisense_5to3"], d["gap_specificity_margin"], default_arch
            load = f"{d['n_gap_paired']} → {d['n_gap_paired_loci']}"
            dup = _duplex(d["parent_duplex_bp"], d["parent"])
        # ⚠ A CONTRAST ARM HAS NO COVERAGE AND MUST NOT BORROW ITS JUNCTION'S. Both arms sit at a
        # junction already in the table; printing that junction's cumulative figure again would
        # count the same patients twice, which is the exact error the ladder exists to prevent.
        cov, basis, idx = (("—", "not a coverage row", None) if src in ("geometry", "design")
                           else cover.get(label, ("adds nothing", "not in the ladder", None)))
        # A ladder entry no junction claims goes in ITS OWN PLACE IN THE LADDER, immediately above
        # the first row that carries a later entry — and the contrast arms are not coverage rows, so
        # anything still pending is flushed before them rather than after the table's last figure.
        while pending and (src in ("geometry", "design")
                           or (idx is not None and pending[0][0] < idx)):
            rows.append(_bound_row(pending.pop(0)[1]))
        lab = label.replace("__", "::").replace("_", " ")
        rows.append((basis, f"| {role} | {lab} | 5′-{seq}-3′ | {arch} | {margin} | {load} | "
                            f"{dup} | {cov} | {basis} |"))
    for _, rung in pending:                     # a ladder that ends above every named reagent
        rows.append(_bound_row(rung))
    # ⛔ "cumulative coverage" READ AS PATIENTS COVERED, AND THE DENIAL WAS THIRTY PAGES AWAY
    # (display-item review, 2026-08-19). The top cell reads 98.3% under a bare header, and §4.1's
    # answer to it — "**It is not a coverage measurement.** No patient was screened with either
    # sequence" — is in the body text, which a lifted table does not carry and a continuation page
    # never shows. The header names the NUMERATOR (published junctions the set addresses) and
    # carries §4.1's own denial in §4.1's own words, because a header rides in the <thead> the
    # builder repeats on every page of a table while a caption does not.
    # ⛔ AND THE DUPLEX HEADER NAMES BOTH READINGS ITS CELLS NOW CARRY — see `_duplex`.
    hdr = ("| reagent | junction | sequence | geometry | gap-level margin | sense-strand gap-paired "
           "near-matches → loci at the deeper ceiling | longest mature-parent duplex through the "
           f"gap, and the reading at {_word(_loose)} base pairs | cumulative coverage of published "
           "junctions — not a coverage measurement | basis |")
    return ("\n".join([hdr, "|---|---|---|---|---|---|---|---|---|"] + _classed(rows)),
            ladder_backed_noncoding)


#: ⛔ ONE COLUMN, FOUR MEANINGS, NO MARKER OF ANY KIND (audit, 2026-08-19). Table 5's "cumulative
#: coverage" cell is a measured cumulative fraction on the ladder rows, an arithmetic what-if on the
#: bound rows, a zero contribution on the seams the ladder prices at nothing, and not-applicable on
#: the contrast arms — under one header, in a caption of about a thousand words that a reader
#: scanning a column will not be holding in mind. The classes are announced IN the table now, each
#: with the reading its own cells take.
#: ⭐ THE CLASS IS THE BASIS CELL'S, NEVER THE ROLE LABEL'S, so a row cannot be filed under a
#: heading its own last column contradicts — which is the failure the two membership classes of the
#: exon-2 seams already produced once, when a "coverage rung" and a "beside the panel" row looked
#: like a contradiction of the caption rather than two readings of the ladder.
#: ⚠ IN PLACE, NOT SPLIT. A real split is four tables, and four tables renumber Tables 6 and 7 —
#: a separate pass over every cross-reference in the article, the SI, the figures and the guards.
_TABLE5_CLASSES = {
    "single series, cumulative":
        "MEASURED RUNGS — the cumulative-coverage cell is the coverage of the reagent set through "
        "this row, discounted by one series' breakpoint distribution",
    "arithmetic bound":
        "ARITHMETIC BOUNDS — the cell is what coverage WOULD be if every remaining breakpoint of "
        "that partner were covered, which nothing here measures",
    "not a coverage row":
        "CONTRAST ARMS — not coverage rows; the cell is empty because their junction's coverage is "
        "counted a row above and must not be counted twice",
}
_TABLE5_ADDS_NOTHING = (
    "QUALIFYING SEAMS THE LADDER PRICES AT NOTHING — the cell reads “adds nothing” and the basis "
    "beside it gives which of the two reasons applies")


def _classed(rows):
    """Table 5's rows with a class band above each run of them. See `_TABLE5_CLASSES`."""
    out, seen = [], None
    for basis, line in rows:
        cls = _TABLE5_CLASSES.get(basis, _TABLE5_ADDS_NOTHING)
        if cls != seen:
            out.append(f"| **{cls}** |" + " |" * 8)
            seen = cls
        out.append(line)
    return out


def table2(per_junction, thermo):
    """One best-available reagent per junction, joined across all five screens.

    ⛔ WHY A FOURTH TABLE. Tables 3 and 4 both answer panel-level questions — the representative
    design at each junction, and the panel's cleanest molecules. Neither answers the question a
    reader with a patient has, which is what to order for ONE fusion at ONE exon pair. That was in
    the prose for the junctions the paper discusses and nowhere for the other thirty.

    ⚠ RANKED, NOT SCORED, and the ordering is the artifact's: parent liability disqualifies, then
    pre-mRNA, then gene loci, with ties broken on gap-level margin rather than on raw hits. The two
    axes are printed side by side and never combined.

    ⛔ THE CONVENTIONAL-RULE AUDIT WAS IN TABLE 4 ONLY, WHICH COVERS NINE DESIGNS (cold-reader
    finding, 2026-08-17). §2.10 exists to report that the two rankings disagree — of the nine
    cleanest designs exactly one satisfies all four conventional rules — and this is the table a
    laboratory orders one reagent from. Its best-available rows include a five-G homopolymer, a TTTT
    and an AAAA, every one of them unmarked, so the disagreement §2.10 is about was invisible
    exactly where it is acted on. The column is the same audit, from the same artifact, computed the
    same way as Table 4's; it is printed beside the ranking and never folded into it.

    ⚠ AND A DESIGN THE AUDIT DOES NOT COVER SAYS SO RATHER THAN READING AS A PASS. The thermo
    artifact holds 176 of the panel's 190 designs; every design this table names is among them
    today, but a blank in a rules column reads as "breaks none", which is the flattering direction
    and the one these tables have gone wrong in before.
    """
    rules = {r["antisense_5to3"]: (r.get("design_rules") or {}) for r in thermo["per_design"]}

    def _rules_cell(seq):
        audit = rules.get(seq)
        if not audit:
            return "not audited"
        failed = [_RULE_LABELS.get(k, k) for k, v in audit.items() if v is False]
        return ", ".join(failed) if failed else "none"

    # ⛔ ONE FIELD, THREE NAMES ACROSS THREE TABLES (display-item review, 2026-08-19). The cell
    # under this header is `alignment_screen.n_true_cleavage_risk` — the deep screen's near-matches
    # LESS its minus-strand and gap-disrupted hits (for the lead: 189 − 48 − 18 = 123). Table 7
    # prints that same 123 in a row labelled "sense-strand gap-paired near-matches"; this header
    # and Table 5's said only "gap-paired near-matches", which drops the one qualifier that makes
    # the number a liability rather than a search result — and the caption's genome sentence
    # already distinguishes itself from "the sense-filtered near-match columns beside it", so the
    # columns were being described by a property their own headers did not state.
    hdr = ("| junction | exon-resolved breakpoint | designs clearing the parent screen | best "
           "available design | gap-level margin | longest parent duplex through the gap (bp) | "
           "sense-strand gap-paired near-matches at the deeper ceiling (transcripts → loci) | "
           "genome-wide gap-paired load, observed/expected | conventional rules failed |")
    sep = "|---|---|---|---|---|---|---|---|---|"
    rows = []
    #: ⚠ THE SAME KEY TABLE 3 SORTS ON — see `_junction_sort_key`. The artifact lists its
    #: junctions in string order, so taking them as they come is what filed exon 1 between
    #: exon 15 and exon 4 in both tables at once.
    for j in sorted(per_junction["junctions"],
                    key=lambda j: _junction_sort_key(j["junction_label"])):
        lab = j["junction_label"].replace("__", "::").replace("_", " ")
        tier = _tier_cell(j)
        b = j["best_available"]
        n = f"{j['n_designs_clearing_the_parent_screen']} of {j['n_designs_screened']}"
        if b is None:
            rows.append(f"| {lab} | {tier} | {n} | — | — | — | — | — | — |")
            continue
        oe = b["genome_oe_gap_paired_le2"]
        rows.append(
            f"| {lab} | {tier} | {n} | 5′-{b['antisense_5to3']}-3′ | "
            f"{b['gap_specificity_margin']} | {b['parent_duplex_bp']} | "
            f"{b['n_gap_paired']} → {b['n_gap_paired_loci']} | "
            f"{'—' if oe is None else f'{oe:.2f}'} | {_rules_cell(b['antisense_5to3'])} |")
    return "\n".join([hdr, sep] + rows)


def _geometry_columns(gap):
    """Every geometry the artifact says is PRESENT, ordered by gap length. Derived, never typed.

    ⛔ THIS WAS `_GEOMETRIES = ("5-6-5", "5-8-5", "5-10-5")`, A TYPED LIST — the mirror image of the
    pooling defect and just as quiet (2026-08-14). Pooling makes a table describe two panels at
    once; a typed column list makes it silently OMIT one. A fourth geometry screened tomorrow would
    appear in `aso-gap-length-tradeoff.json`, appear in the artifact's own `geometries` block, and
    never appear in the table generated from it — and `test_table5_cells_are_the_artifacts` types
    the same three names, so the guard would agree with the generator and both would be wrong.
    Rule 1: restating a list instead of pointing at it is how it silently falls short.
    ⚠ ORDER IS BY GAP LENGTH, which is the axis the trade runs along, so the columns cannot be
    re-ordered by a dict-insertion accident. Today this returns exactly the three typed before.
    """
    present = [g for g in gap["geometries"] if g.get("present")]
    if not present:
        raise SystemExit("Table 7: the trade-off artifact reports no present geometry")
    return tuple(g["architecture"] for g in sorted(present, key=lambda g: g["gap_nt"]))


def table7(gap):
    """The gap-length trade, one column per geometry, at the junction and over the corpus.

    ⛔ ROWS ARE QUANTITIES AND COLUMNS ARE GEOMETRIES, because the finding is a TRADE and a trade is
    only visible when the two directions sit in one column. Splitting it into a table per geometry,
    or ranking the geometries, would present as a recommendation what is an accounting of costs on
    both sides — the same reason `aso_gap_length_tradeoff` emits no composite score.

    ⚠ THE THREE BLOCKS ANSWER DIFFERENT QUESTIONS AND HAVE DIFFERENT DENOMINATORS. The junction block is
    one molecule at one junction; the matched-junction block is the six junctions every geometry was
    screened at, which is the only like-for-like alignment comparison available; the corpus block is
    all designs at each geometry, where the geometries are NOT screened at the same junctions and
    the counts are therefore reported per geometry rather than compared. Labelled in the rows.
    """
    lead = gap["lead_reagent_at_the_most_commonly_reported_seam"]["by_geometry"]
    matched = gap["the_trade"]["transcriptome_coincidence_falls_but_it_MUST"][
        "matched_junctions"]["by_geometry"]
    trade, geom = gap["the_trade"], {g["architecture"]: g for g in gap["geometries"]}
    columns = _geometry_columns(gap)

    # ⛔ AND EVERY PRESENT GEOMETRY MUST HAVE A ROW IN BOTH BLOCKS, OR THE TABLE IS SHORT A COLUMN
    # AND SAYS NOTHING ABOUT IT. Deriving the columns only moves the omission one step if a
    # geometry can be present in `geometries` and missing from `by_geometry`.
    for arch in columns:
        for name, src in (("lead reagent", lead), ("matched junctions", matched)):
            if arch not in src:
                raise SystemExit(
                    f"Table 7: geometry {arch} is present in the trade-off artifact but has no "
                    f"{name} row; the table would omit a screened geometry without saying so")

    # ⛔ THE MERGED ROW BELOW RESTS ON AN IDENTITY, SO THE IDENTITY IS CHECKED HERE. With a wing of
    # five, a parent's junction hybrid is five plus its share of the gap, so reaching a ten-base-pair
    # hybrid and reaching a five-nucleotide contiguous DNA run are the same inequality. If a future
    # geometry changes the wing they come apart, and one row would then be silently wrong for one of
    # them — which is exactly the class of error a generated table is supposed to make impossible.
    for arch in columns:
        g = geom[arch]
        ge5 = sum(v for k, v in g["parent_paired_gap_dna_distribution"].items() if int(k) >= 5)
        if not (g["wing"] == 5 and ge5 == g["n_whose_seam_hybrid_reaches_min_duplex_bp"]):
            raise SystemExit(
                f"Table 7: at {arch} the ten-base-pair duplex count "
                f"({g['n_whose_seam_hybrid_reaches_min_duplex_bp']}) and the ≥5 nt DNA count "
                f"({ge5}, wing {g['wing']}) are no longer the same condition; split the row")

    def row(label, fn, src):
        return f"| {label} | " + " | ".join(str(fn(src[g])) for g in columns) + " |"

    def parent_duplex(d):
        #: The same measurement Table 5's `_duplex` renders; the unit lives in this table's row
        #: label rather than in the cell, so the number is bare here and carries `bp` there. A zero
        #: is a measured zero in both — see the note beside `_duplex`.
        bp = d["mature_parent_duplex_through_whole_gap_bp"]
        return f"{bp} (*{d['mature_parent_duplex_gene']}*)" if bp else "0"

    rows = [
        "| **At the *EWSR1* e12 / *TAF15* e11 / *FUS* e10 junction** | | | |",
        # ⛔ THE ONLY BARE SEQUENCE CELLS IN THE DOCUMENT, AND THE PDF TEXT LAYER FUSED THEM WITH THE
        # CELL BELOW (built-PDF finding, 2026-08-17). Every other table wraps its sequences in
        # `5′-…-3′`; this row printed them bare and relied on its ROW LABEL to carry the orientation,
        # which survives in the rendered table and does not survive extraction: pulled out of the
        # deposit PDF, `CAGGGCATATCATCAAACCA` came out immediately adjacent to the numeric cell
        # underneath it, and extractors that drop the cell boundary hand a reader `…CAAACCA3` — a
        # transcribed 20-mer with a trailing digit, ordered as a 21-mer that is not this molecule.
        # The delimiters are what BOUND the string, so they belong in the cell rather than in a label
        # a text extractor is free to separate from it. The label loses the parenthetical it no
        # longer needs to carry.
        row("design", lambda d: f"5′-{d['antisense_5to3']}-3′", lead),
        row("gap-level margin", lambda d: d["gap_specificity_margin"], lead),
        # ⛔ THREE NAMES FOR ONE FIELD, AND THIS ONE ASSERTED WHAT THE CAPTION WITHDRAWS
        # (display-item review, 2026-08-19). `alignment_screen.n_true_cleavage_risk` reads 123 for
        # the lead reagent; Tables 2 and 5 both print that same 123 as "gap-paired near-matches at
        # the deeper ceiling", and this row called it a count of "cleavage risks" four pages away —
        # in a table whose own caption ends "None of these numbers is a measurement of cleavage."
        # The field name is the screen's; the ROW LABEL is the paper's, and it now matches the two
        # tables a reader compares it against.
        row("sense-strand gap-paired near-matches",
            lambda d: d["alignment_screen"]["n_true_cleavage_risk"], lead),
        row("gene loci carrying one",
            lambda d: d["alignment_screen"]["loci"]["n_loci_with_a_gap_spanning_hit"], lead),
        row("near-matches (≤2 mismatches, deeper ceiling)",
            lambda d: d["alignment_screen"]["n_offtarget_near_matches"], lead),
        row("≤1-mismatch matches over 186,185 transcripts",
            lambda d: d["exhaustive_le1mm_matches"], lead),
        row("mature-parent duplex through the whole gap (bp)", parent_duplex, lead),
        row("contiguous DNA a wild-type parent pairs (nt)",
            lambda d: d["parent_paired_gap_dna_nt"], lead),
        row("most stable parent ΔG°37 (kcal/mol)",
            lambda d: f"{d['dg37_most_stable_parent_duplex']:.2f}".replace("-", "−"), lead),
        "| **Over the six junctions screened at every geometry** | | | |",
        row("designs screened", lambda d: d["n_designs_with_alignment_counts"], matched),
        row("median near-matches", lambda d: f"{d['near_matches']['median']:g}", matched),
        row("median sense-strand gap-paired near-matches",
            lambda d: f"{d['hybridisable_gap_spanning_risks']['median']:g}", matched),
        row("designs carrying none",
            lambda d: f"{d['n_with_zero_hybridisable_gap_spanning_risk']} of "
                      f"{d['n_designs_with_alignment_counts']}", matched),
        row("most gap-paired loci on any one design",
            lambda d: d["loci_with_a_gap_spanning_hit"]["max"], matched),
        row("designs with no near-match at all",
            lambda d: f"{d['n_with_no_near_match_at_all']} of "
                      f"{d['n_designs_with_alignment_counts']}", matched),
        "| **Over each geometry's whole design space** | | | |",
        row("junction-spanning registers per junction",
            lambda d: d["junction_spanning_registers_per_seam"], geom),
        row("fusion-specific designs", lambda d: d["n_fusion_specific_designs"], geom),
        f"| best gap-level margin available | " + " | ".join(
            str(trade["improves_with_a_longer_gap"]["best_available_gap_margin"][g])
            for g in columns) + " |",
        row("a mature parent can pair the whole gap",
            lambda d: f"{d['mature_parent_whole_gap_duplex']['n_with_any_gap_pairing_window']} of "
                      f"{d['n_fusion_specific_designs']}", geom),
        # ⛔ THE PAPER'S KEY THRESHOLD-CONTROLLED RESULT WAS IN NO TABLE (round-7 review, 2026-08-16).
        # §2.9 neutralises the gap-length win with "held to the ten-base-pair criterion applied
        # everywhere else here, the liability is flat: 87 of 190, 88 of 266 and 87 of 342" — the
        # sentence the title's "nearly half" survives on — and `88 of 266` appeared NOWHERE in this
        # file. A reviewer spot-checking it found the row above (181/130/87, a different quantity)
        # and the row below (76/228/342, a different quantity again), both plausible and neither the
        # one quoted. Printing the two neighbours of a number and not the number is worse than
        # printing none of the three, because it reads as a contradiction rather than as an omission.
        row(f"…and that duplex reaches {_word(_parent_cut_bp())} base pairs, the criterion "
            "applied throughout",
            lambda d: f"{d['mature_parent_whole_gap_duplex']['n_at_or_above_min_duplex_bp']} of "
                      f"{d['n_fusion_specific_designs']}", geom),
        # ⚠ ONE ROW, NOT TWO, BECAUSE THESE ARE THE SAME CONDITION AND PRINTING BOTH READS AS A
        # COPY-PASTE FAULT. The parent's junction hybrid is the wing plus its share of the gap, and the
        # wing is five at every geometry compared, so "hybrid reaches ten base pairs" and "the DNA
        # run reaches five nucleotides" are the same inequality. Asserted below rather than trusted.
        # ⛔ AND THE LABEL NOW SAYS *WHERE* THAT HYBRID IS (round-7 review, 2026-08-16). It read
        # "parent pairs ≥5 nt of contiguous gap DNA, a ten-base-pair hybrid", which reuses the
        # paper's headline phrase — a ten-base-pair criterion — against a DIFFERENT quantity: this
        # row is the parent's hybrid at the design's OWN seam, an arithmetic property of the
        # junction, while 87 of 190 is the mature-parent SEARCH over every window of all six parents.
        # Two quantities, one form of words, adjacent rows.
        row("at the design's own seam, the parent pairs ≥5 nt of contiguous gap DNA",
            lambda d: f"{d['n_reaching_reported_dna_minimum']['5']} of "
                      f"{d['n_fusion_specific_designs']}", geom),
        row("designs pairing the gap in parent pre-mRNA",
            lambda d: f"{d['premrna_hybridisable_gap_paired']['n_designs_with_at_least_one']} of "
                      f"{d['premrna_hybridisable_gap_paired']['n_designs_screened']}", geom),
        row("median most stable parent ΔG°37 (kcal/mol)",
            lambda d: f"{d['dg37_most_stable_parent_duplex']['median']:.2f}".replace("-", "−"),
            geom),
    ]
    return "\n".join(
        ["| | 5-6-5 (16-mer) | 5-8-5 (18-mer) | 5-10-5 (20-mer) |", "|---|---|---|---|"] + rows)


#: The rule audit's field names are code identifiers; a manuscript table needs the rule, not the key.
#:
#: ⚠ TWO PHRASINGS OF THE SAME RULE, AND BOTH ARE NEEDED. A cell names what the design DID WRONG
#: ("GC outside 40–60%"); the table note names the rule that was APPLIED ("GC within 40–60%"). They
#: are not each other's negation as strings, so neither can be generated from the other — but they
#: must never disagree about WHICH four rules the audit runs, which is why they now sit in one
#: record per rule instead of a cell map here and a hand-typed sentence 500 lines below.
_RULES = (
    ("gc_in_band", "GC outside 40–60%", "GC within 40–60%"),
    ("no_g_quadruplex_motif", "G-quadruplex motif", "no G-quadruplex motif"),
    ("no_run_of_four", "homopolymer run of four", "no homopolymer run of four"),
    ("no_cpg", "contains a CpG", "no CpG dinucleotide"),
)

_RULE_LABELS = {key: violation for key, violation, _ in _RULES}


def _rule_audit_note():
    """The four-rule definition, worded once and printed under every table that audits against it.

    ⛔ WHY IT IS PRINTED TWICE RATHER THAN CROSS-REFERENCED (2026-08-17). Table 2's last column is
    this audit, and its note used to define the column by pointing at Table 4's note ⁵ — four pages
    away in the journal build, and in the manuscript build a different display item entirely. A
    table that cannot be read without another table is not standalone-readable, which is the one
    property a display item has to have. The rules themselves stay a single fact: this function is
    their only home, and `_RULE_LABELS` above draws the cell wording from the same records.
    """
    #: ⚠ A COMPLETE SENTENCE, because it is printed in two positions. As note ⁵ it stands alone
    #: under a column heading; in Table 2's note it runs mid-paragraph, where the older footnote
    #: phrasing ("Of four conventional antisense design rules: …") is a verbless fragment.
    rules = [rule for _, _, rule in _RULES]
    listed = ", ".join(rules[:-1]) + ", and " + rules[-1]
    return (f"The {_word(len(rules))} conventional antisense design rules audited are "
            f"{listed}.")


#: How the expression artifact's tiers read in a table cell. The artifact owns the thresholds and
#: the wording; this maps its enum to a column heading's worth of words and nothing else. A tier the
#: artifact adds later and this dict has not heard of renders as itself rather than silently blank.
_EXPOSURE_READING = {
    "EXPRESSED_IN_AN_EXPOSURE_ORGAN": "at or above the upper cut",
    "LOW_IN_EXPOSURE_ORGANS": "detectable, below the upper cut",
    "BELOW_DETECTION_IN_EXPOSURE_ORGANS": "below the lower cut in all three",
    "NOT_MEASURABLE_UNCHARACTERISED": "no gene model — not measurable",
    "NOT_MEASURED": "no reading taken",
}


def _gap_paired_records(expr):
    """Table 6's record column, totalled — and the guard that it is a HIT count, not a gene property.

    ⛔ THE COLUMN WAS HEADED "transcript records" AND CAPTIONED AS ANNOTATION DEPTH — "how many
    accessions RefSeq lists for the gene" — and it is neither (round-7 review, B2-F5, 2026-08-16).
    `aso_offtarget_tissue_expression._seam_rows` increments `n_transcript_records` once per
    GAP-PAIRED HIT, once for every design tiled at the seam, then merges the per-seam rows by
    addition. So the column sums to the panel's whole gap-paired hit count, and a locus returned by
    five registers is counted five times. *NRP1* is the demonstration: five records over ONE
    accession, because all five of its junction's designs return it. *HNRNPA2B1*'s hundred are fifty
    accessions returned by two designs.

    Under the old label a reader took the column for a property of the GENE, fixed by RefSeq. It is a
    property of what the SEARCH returned, and it is therefore not the independent second axis the
    caption claimed it was — it moves with the register column beside it. The header and the caption
    now name the quantity the code computes.

    ⚠ THE IDENTITY IS ASSERTED, NOT TRUSTED, because the new label is only correct while it holds. If
    the upstream module ever makes this the gene's annotation depth, the sum stops matching the
    panel's hit total and this refuses to build rather than re-acquiring the old defect silently.
    """
    total = sum(L["screen_records"]["n_transcript_records"] for L in expr["per_locus"])
    hits = sum(s["n_gap_paired_hybridisable"] for s in expr["panel"]["panel"])
    if total != hits:
        raise SystemExit(
            f"Table 6: the record column sums to {total} while the panel's screens returned {hits} "
            "gap-paired hits; the column is no longer the per-locus gap-paired hit count its header "
            "names, so the header is wrong again — re-derive the label before regenerating")
    return total


def _reagent_loci(expr, per_junction):
    """{seam: the loci returned by the reagent Table 2 names there}, for Table 6's ◆ marker.

    ⛔ TABLE 6 COULD NOT SUPPORT A CLAIM MADE FROM IT (cold-reader finding, 2026-08-17). §4.1 says
    the *EWSR1* exon-13 reagent's TWO loci are both transcribed at the upper cut — and Table 6 lists
    ELEVEN loci at that seam, because it is the UNION over every register tiled across the junction
    (`aso_offtarget_tissue_expression.PANEL` sets `designs: None` there for a stated reason: the
    union is what the panel has to cover). Nothing in the table said which two were the reagent's,
    so a reader checking the sentence against the table it cites could not.

    ⭐ THE TABLE CAN TELL, AND FROM AN ARTIFACT IT ALREADY HAS. The expression artifact stores each
    seam's per-DESIGN locus list, and `aso-per-junction-table.json` names the best available design
    at each seam — the same molecule Table 5 prices. The intersection is exact, not inferred.

    ⚠ AND IT REFUSES RATHER THAN MARKING NOTHING. A named reagent absent from the designs this table
    reads would leave the ◆ legend describing a marker no row carries, which is the defect footnote ³
    was just cleared of. The union framing is untouched: every locus keeps its row, and the marker
    identifies rather than ranks.
    """
    panel = {j["junction_label"]: j for j in per_junction["junctions"]}
    out = {}
    for seam in expr["panel"]["panel"]:
        lab = seam["junction_label"]
        best = (panel.get(lab) or {}).get("best_available")
        if not best:
            continue
        seq = best["antisense_5to3"]
        mine = [d for d in seam["designs"] if d["antisense_5to3"] == seq]
        if not mine:
            raise SystemExit(
                f"Table 6: the best available design at {lab} ({seq}) is not among the designs this "
                "table reads at that seam, so the ◆ marker its legend defines would mark no row. "
                "Re-derive the marker against whatever design the expression panel now reads.")
        out[lab] = set(mine[0]["loci"])
    return out


def table6(expr, per_junction):
    """Where each off-target locus returned at a junction with a published breakpoint is expressed.

    ⛔ THE TITLE SAID "clinically-relevant reagents" AND THE BANNER ABOVE IT SAYS NONE OF THESE IS A
    MEDICINE OR A CANDIDATE DRUG (cold-reader finding, 2026-08-17). "Clinically-relevant" is defined
    nowhere in this document, asserts of a reagent the relevance the whole deposit is built to deny,
    and trips the repository's language discipline besides. It was also inaccurate twice over: the
    row set is FOUR seams, not two reagents, and what makes those seams different from the other
    thirty-four is a published exon-resolved breakpoint — a property of the junction, from the
    published record, not a property of the molecule. The title now names that.

    ⛔ TWO COMPARTMENTS, NEVER ONE COLUMN. The organs a systemically dosed gapmer distributes to and
    the compartment the tumour sits in are different questions, and a table that merged them — or
    that ranked loci on either — would be inventing the join this work does not make. They are
    printed side by side and never combined, exactly as Table 7 keeps the two directions of the
    gap-length trade apart.

    ⛔ NO RISK COLUMN, AND NO ORDERING BY EXPRESSION. Rows are grouped by junction and then by the
    per-locus gap-paired hit-record count — see `_gap_paired_records` for what that column is and for
    the label it used to carry. Every hit behind this table is at the screen's loosest
    admitted identity, so nothing here distinguishes the loci on affinity, and an expression figure
    is not a predicted cleavage event. The artifact refuses a hazard ordering and so does its table.

    ⚠ AN UNREADABLE LOCUS PRINTS ITS REASON, NEVER A ZERO — an absent reading is not a reading of
    absence, and rendering one as `0.00` would convert it into one.
    """
    tiss = expr["method"]["exposure_tissues"]
    rows, seen = [], set()
    order = {s["junction_label"]: i for i, s in enumerate(expr["panel"]["panel"])}
    # ⚠ THE REGISTER COLUMN NEEDS ITS DENOMINATOR OR THE TWO SEAMS ARE NOT COMPARABLE. One junction
    # contributes a single design and the other five, so a bare "1" and a bare "5" read as a
    # thirteen-fold difference in robustness when one of them is every register there is.
    n_des = {s["junction_label"]: s["n_designs"] for s in expr["panel"]["panel"]}
    mine = _reagent_loci(expr, per_junction)
    per = sorted(expr["per_locus"],
                 key=lambda L: (order.get(L["seams"][0], 99),
                                -L["screen_records"]["n_transcript_records"], L["locus"]))
    for L in per:
        junction = L["seams"][0]
        #: ⛔ THE LABEL IS REPEATED ON EVERY ROW, NOT ONLY THE FIRST OF EACH BLOCK (2026-08-17). It
        #: used to be blanked after the block's first row, which reads well on one page and fails at
        #: a page break: a blind screen of the built journal PDF found the continuation page opening
        #: with two unlabelled loci — one of them the highest liver reading on the page, the sort of
        #: row a reader most wants to attribute — belonging to a block that started overleaf. Tables
        #: 2, 3 and 5 all repeat their row identity across their own breaks, so blanking here was
        #: also out of the document's convention. Where the break falls is a typesetting decision
        #: this generator cannot see, so the label cannot be omitted on the assumption it is visible.
        lab = junction.replace("__", "::").replace("_", " ")
        seen.add(junction)
        ex, tu = L["exposure_compartment_liver_kidney"], L["tumour_compartment_normal_tissue_proxy"]
        if ex.get("readable") and ex.get("values"):
            cells = [f"{ex['values'][t]:.2f}" if ex["values"].get(t) is not None else "—"
                     for t in tiss]
        else:
            cells = ["—"] * len(tiss)
        if tu.get("readable") and tu.get("values"):
            hi = max(tu["values"].values())
            #: ⛔ A CELL READING `0.0` THAT IS NOT ZERO (measured, 2026-08-19). A reviewer read
            #: *SLC17A3*'s `0.0 (Adipose - Subcutaneous)` and *ANKRD26P3*'s `0.0 (Muscle - Skeletal)`
            #: as the argmax of an all-zero set — a tissue name attached to nothing. RECOMPUTED from
            #: `tumour_compartment_normal_tissue_proxy.values`, the two maxima are 0.0258938 and
            #: 0.0149871 TPM: NOT zero, and the tissue is the real argmax. The reviewer's mechanism
            #: is wrong and the symptom is real — one-decimal rounding turned two small non-zero
            #: readings into the one value this document insists never to render for an absent one,
            #: beside exposure columns printed at two decimals where the same numbers would not
            #: have vanished. A reading below the printed precision now says so, and a genuine zero
            #: names no tissue, because a zero maximum is not a maximum AT anywhere.
            soft = (f"0.0 (all {len(tu['values'])} proxies)" if hi == 0 else
                    f"<0.1 ({tu['max_tissue_in_block']})" if round(hi, 1) == 0 else
                    f"{hi:.1f} ({tu['max_tissue_in_block']})")
        else:
            soft = "—"
        reading = _EXPOSURE_READING.get(L["tier"], L["tier"])
        mark = " ◆" if L["locus"] in mine.get(junction, ()) else ""
        # ⛔ A RECORD COUNT IS AN ACCESSION COUNT, AND THE HALF THAT IS CURATED WAS NOT PRINTED
        # ANYWHERE (display-item review, 2026-08-19). The column is annotation depth — one entry per
        # RefSeq transcript variant per register — and RefSeq's `XM_`/`XR_` records are
        # computationally predicted gene models rather than curated transcripts, which Table 3
        # already separates at the default depth and this table did not separate at all. The split
        # decides how a large cell reads: *ANKS1B*'s 67 records are 32 curated and 35 predicted, and
        # over the whole EWSR1 exon-12 seam only 41 of 123 records are curated. Both halves are in
        # the artifact per locus; printing only the total is the choice that makes a locus look
        # deeper-annotated than the curated record supports.
        rows.append(f"| {lab} | *{L['locus']}*{mark} | "
                    f"{L['screen_records']['n_transcript_records']} | "
                    f"{L['screen_records']['n_curated_records']} | "
                    f"{L['n_designs_hitting_it']} of {n_des.get(junction, '?')} | "
                    + " | ".join(cells) + f" | {soft} | {reading} |")
    # ⚠ THE ◆ IS EXPLAINED BY A SYMBOL-KEYED NOTE, NOT BY A SUPERSCRIPT ON THIS HEADER. The header's
    # opening is the anchor `test_table6_record_column_is_named_for_what_the_generator_counts` finds
    # this table by, and a marker inside it would break that guard while changing nothing a reader
    # sees. The symbol lives in the cells it marks, which is where a reader meets it.
    # ⛔ ⁸ NOT ⁷ (2026-08-19). The markers run CONTINUOUSLY across this file — ¹²³ in Table 3, ⁴⁵⁶
    # in Table 4 — precisely so that a table lifted out of the document cannot collide with its
    # neighbour's notes. Table 4 gained a ⁷ this round for its new parent-duplex column, and this
    # header still called ⁷ four pages later: one marker, two definitions, in a file whose whole
    # numbering convention exists to prevent that.
    hdr = ("| junction | gene locus | gap-paired hit records | of those, curated rather than "
           "predicted | tiling registers returning it⁸ | "
           + " | ".join(tiss) + " | soft-tissue proxy maximum | exposure-organ reading |")
    sep = "|---|---|---|---|---|" + "---|" * (len(tiss) + 2)
    return "\n".join([hdr, sep] + rows)


def table4(collapse, chance, thermo, graded):
    """The designs the paper's headline rests on, one row each.

    ⛔ WHY THIS TABLE WAS MISSING AND WHY THAT MATTERED. The headline result — nine designs with no
    sense-strand near-match — had no table, and Table 3's convention is the highest-gap-level-margin
    design per junction, which is a different selection: only four of the nine appear there, and
    Table 3's six zero-gap-paired junctions are not the same six. So a reader sent to a table to
    check the central claim could not find five of the molecules it is about, and would find two
    junctions (FUS e8, TCF12 e9) whose Table 3 row shows a gap-paired locus for a DIFFERENT
    design at the same junction. Prose naming nine sequences is not a substitute for a table.

    ⚠ THAT SAME NON-OVERLAP IS WHY NO SENTENCE HERE MAY SAY WHAT TABLE 3 MARKS. The two tables
    select by different rules over the same designs, so which of this table's rows Table 3 also
    prints is a MEASUREMENT and not an inference — `_flagged_rows_in_table3` takes it off the
    rendered rows of both, and the caption is written from what it returns.
    """
    ddg = {r["antisense_5to3"]: r for r in thermo["per_design"]}
    le1 = {}
    for r in chance["per_design"]:
        le1.setdefault(r["antisense_5to3"], (r.get("offtarget_exact"), r.get("offtarget_le1mm")))
    deep = _deep_lookup()
    # ⛔⛔ THE PARENT-DUPLEX COLUMN IS HERE BECAUSE THIS TABLE CONDEMNED NOTHING AND LOOKED LIKE IT
    # CLEARED EVERYTHING (blind order-walkthrough, 2026-08-19). The parent screen condemns a design
    # where a wild-type parent pairs the whole catalytic gap at the criterion, and FIVE of this
    # table's nine rows are condemned by it — `GCATATCCGTGGACGC` at 12 bp against EWSR1,
    # `GGCATATCCGTGGACG` at 11, `GCATATCAAGCGCTGC` at 12 against TCF12, `GGCATATCAAGCGCTG` at 11,
    # `CAGGGCATATCTTGCA` at 12 against NR4A3 itself — and this table printed every one of them with
    # no marker of any kind and a final column reading "yes". A reader who reached Table 4 first,
    # which its own §2.4 citation invites, met five condemned molecules presented as survivors.
    # ⛔ AND THE FIRST FIX CARRIED A SECOND ERROR: it said Table 3 "marks them do-not-order for it",
    # which is a claim about ANOTHER TABLE'S ROWS and was false of four of the five. RECOMPUTED over
    # the rendered rows (`_flagged_rows_in_table3`): Table 3 prints ONE of them, `GGCATATCAAGCGCTG`
    # at TCF12 e7, marked; at EWSR1 e1 and TCF12 e9 it prints a DIFFERENT design — `GGGCATATCCGTGGAC`
    # at 0 bp and `GGGCATATCTTGCATA` at 8 bp — and marks neither, because Table 3 prints each
    # junction's HIGHEST-MARGIN design and whether that is also the condemned one is a coincidence
    # of two rankings. So the cross-reference sent a reader checking a do-not-order verdict to an
    # unmarked row. The caption's sentence is now generated from the join instead of asserted.
    # ⚠ AND THE VERDICT COLUMN IS RENAMED RATHER THAN LEFT TO CARRY THE WHOLE WEIGHT. "survives"
    # was always a near-match verdict — no sense-strand near-match at the deeper ceiling — and
    # never a statement about the parent screen. The header now says which screen it is.
    hdr = ("| design | junction | GC (%) | gap-level margin | ΔΔG°37 (kcal/mol) | near-matches, "
           "either strand | of those, on the sense strand | exact / ≤1-mismatch matches | residual "
           # ⛔ CONTINUES TABLE 3's RUN. Markers are unique across the file so a lifted table cannot
           # collide with its neighbour's notes, and each table's own set is contiguous — see the
           # note on Table 3's header, which used to leave ³ and ⁴ dangling inside Table 3.
           "cleavage load, both bounds⁴ | conventional rules failed⁵ | "
           "at the deeper ceiling: near-matches | of those, on the sense strand | "
           "loci with a gap-paired hit | longest wild-type parent duplex through the gap (bp)⁷ | "
           "survives the near-match screen⁶ |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
    parent_dup = {}
    for r in (_load("aso-parent-gap-pairing.json") or {}).get("per_design") or []:
        parent_dup[(r["junction"], r["antisense_5to3"])] = (
            r.get("longest_parent_duplex_bp_through_gap"), r.get("parent"))
    rows = []
    for lab, o in _clean_designs(collapse):
        seq = o["antisense_5to3"]
        t = ddg.get(seq) or {}
        ex, l1 = le1.get(seq, ("—", "—"))
        load = graded.get((lab, seq))
        failed = [_RULE_LABELS.get(k, k)
                  for k, v in (t.get("design_rules") or {}).items() if v is False]
        # ⛔ THE VERDICT IS DERIVED FROM THE DEEP COUNTS, NEVER FROM A REMEMBERED LIST OF THREE.
        # Round 2 recorded the survivors by name and the set has already moved once; a hardcoded
        # membership test would go stale silently, which is the failure this whole table is a
        # response to.
        d = deep.get((lab, seq))
        deep_cell = _deep_cells(d)
        verdict = "not re-screened" if d is None else ("yes" if d["hyb"] == 0 else "**no**")
        # ⚠ FIXED TO THE ARTIFACT'S OWN PRECISION, NOT TO JSON'S RENDERING OF IT (built-PDF finding,
        # 2026-08-17). `junction_aso_thermo` rounds this to three decimals; JSON then drops a
        # trailing zero, so 7.980 printed as `7.98` one row above a genuine `7.981` and the column
        # read as a rounding slip in a table where two rows legitimately share a value (10.085 is
        # 32 of the 190 designs — the nearest-neighbour arithmetic returns the same ΔΔG for many
        # registers). The values were the artifact's throughout; only the number of decimals moved.
        ddg_val = t.get("ddg37_discrimination")
        rows.append(
            f"| 5′-{seq}-3′ | {lab.replace('__', '::').replace('_', ' ')} | "
            f"{o.get('gc_percent')} | {t.get('gap_specificity_margin', '—')} | "
            f"{'—' if ddg_val is None else f'{ddg_val:.3f}'} | "
            f"{o.get('n_offtarget_near_matches')} | "
            f"{_hybridisable(o)} | {ex} / {l1} | "
            f"{'—' if load is None else load} | "
            f"{', '.join(failed) if failed else 'none'} | {deep_cell} | "
            f"{_parent_dup_cell(parent_dup.get((lab, seq)))} | {verdict} |")
    return "\n".join([hdr, sep] + rows), len(rows), len({lab for lab, _ in _clean_designs(collapse)})


def _graded_loads():
    """Residual cleavage load per (junction, design) under both literature bounds.

    Printed as one cell because for every design here the two bounds agree, and a reader is owed
    the fact that the OPTIMISTIC and the PESSIMISTIC model return the same number rather than being
    left to assume the paper quoted whichever was kinder.

    ⛔ ONE GEOMETRY, THROUGH THE ONE LOADER — AND THIS CONSUMER WAS MISSED BY THE 2026-08-14
    GEOMETRY SWEEP. It listed the directory and filtered on `startswith("junction-aso-offtarget-")
    and endswith("-graded.json")`, which is a filename rule and therefore not a geometry filter.
    Nothing had fired here yet only because no 18-mer graded artifact existed — and the reason it
    did not is `junction_aso_offtarget.grade_panel`, which was ALSO writing this process's geometry
    onto every re-score it produced. Step 0 of `scripts/regenerate_aso_chain.sh` rescores every
    screen it finds, so the next chain run would have created 18-mer and 20-mer graded artifacts
    mislabelled `oligo_len: 16` and this function would have folded their residual loads into a
    table of the 16-mer panel, keyed by a sequence a reader would take for one of ours. Two latent
    defects composing into one wrong column is exactly what a per-consumer guard cannot see.

    ⛔⛔ ONE DEPTH TOO, BY THE SAME ARGUMENT AND FOR THE SAME TABLE (2026-08-14). The key here is
    `(source_screen, sequence)` and carries no depth, so a default-depth re-score and a deep
    re-score of the SAME junction and the SAME design write to the same key. The "if the two models ever
    disagree, say so" fold below then joined them, and Table 4's residual-load column read
    `31.4 / 101 / 0 / 0` for `GGGCATATCTCTATAA` — the deep screen's bounds and the default screen's,
    in one cell, in a table whose legend says in its first sentence that it is the default-depth
    result. Six of the nine rows moved that way. It stayed invisible only because the 53 deeper
    re-scores are generated by step 0 of `scripts/regenerate_aso_chain.sh` and never committed
    (the Methods release them ungraded), so the cell was wrong only in a tree where someone had just
    run the chain — which is every tree in which this table gets regenerated.

    ⭐ A FILTER, NOT A WIDER KEY, AND THE REASON IS THE ONE ABOVE IT. Table 4 already picks ONE
    geometry rather than keying by it, because the legend fixes the geometry; the legend fixes the
    depth in the same sentence, so depth is filtered the same way. Adding depth to the key would
    leave `table4` to CHOOSE at lookup time, and choosing at lookup is precisely what failed — the
    right value was present in `31.4 / 101 / 0 / 0` the whole time and was still reported wrongly.
    Filtering makes the other depth unreachable rather than merely un-chosen, and `select=` is the
    loader's own documented junction for exactly this ("filters on the artifact's own content (depth,
    junction label, orientation status)").

    ⚠ AND THE FILTER IS ONLY REAL BECAUSE `is_deep` WAS FIXED IN THE SAME PASS. Until then it read
    the shape of a BLAST screen, found neither key on a graded artifact, and returned False for
    every one of them — so this `select` would have kept all 92, changed nothing, and looked right.
    """
    out = {}
    for screen in ass.load_screens(GEOMETRY, ass.GRADED_RESCORE, root=os.path.abspath(MOD),
                                   select=ass.is_default_depth):
        d = screen.artifact
        lab = d.get("source_screen")
        if not lab:
            continue
        per = d.get("per_oligo") or {}
        for model, oligos in per.items():  # noqa: B007 — model name unused, values keyed by seq
            for seq, rec in (oligos or {}).items():
                lo, hi = rec.get("residual_cleavage_load_lo"), rec.get("residual_cleavage_load_hi")
                if lo is None:
                    continue
                prev = out.get((lab, seq))
                cell = f"{lo:g}" if lo == hi else f"{lo:g}–{hi:g}"
                # Both models are folded into one cell; if they ever disagree, say so rather than
                # letting the last one written win.
                out[(lab, seq)] = cell if prev in (None, cell) else f"{prev} / {cell}"
    return out


def _minus_strand_share(collapse):
    """The share of apparent gap-paired hits that lie on the minus strand, across the corpus.

    ⛔ THIS WAS A HARDCODED "47%" IN THIS FILE'S TABLE 3 LEGEND, and it stayed 47% while the corpus
    grew from sixteen junctions to thirty-eight and the true figure became 44%. A generated table is
    supposed to be the one place a number cannot go stale; a literal inside the generator defeats
    the entire point of generating it.
    """
    tot = minus = 0
    for s in collapse["screens"]:
        if not (s.get("junction_label") and _orientation_filtered(s.get("orientation"))):
            continue
        raw = _screen(s["screen"]) or {}
        for o in raw.get("oligos") or []:
            for h in o.get("offtargets") or []:
                if h.get("gap_mismatches") == 0:
                    tot += 1
                    minus += bool(h.get("is_minus_strand"))
    return (round(100 * minus / tot) if tot else None), minus, tot


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    atlas = _load("nr4a3-fusion-junction-atlas.json")
    collapse = _load("junction-aso-offtarget-locus-collapse.json")
    chance = _load("offtarget-chance-baseline.json")
    thermo = _load("junction-aso-thermo.json")
    per_junction = _load("aso-per-junction-table.json")
    gap = _load("aso-gap-length-tradeoff.json")
    expr = _load("aso-offtarget-tissue-expression.json")
    # Table 5's two extra sources. The exon-2 acceptor rows live in their own table for the reason
    # that table states — their junctions are not the manuscript's panel — and the coverage cells
    # come from the ladder, which is the one place that owns the arithmetic.
    noncoding = _load(os.path.join("noncoding-acceptor",
                                   "aso-noncoding-acceptor-screened-table.json"))
    ladder = json.load(open(os.path.join(HERE, "aso",
                                         "fusion-junction-aso-coverage-ladder.json")))
    if not (atlas and collapse and chance and thermo and per_junction and gap and expr
            and noncoding and ladder):
        print("a required artifact is missing", file=sys.stderr)
        return 2

    lo_cut, hi_cut = _expression_cuts()
    # ⛔ THE SEAM COUNT IN TABLE 6's CAPTION IS DERIVED, NEVER TYPED (2026-08-15). It read "the two
    # junctions with a published exon-resolved EMC breakpoint" while `PUBLISHED_BREAKPOINTS` named
    # THREE — the caption had been written when EWSR1 exon 13 was still mis-tiered as unreported,
    # and a hand-typed count cannot notice that its own tiering moved underneath it. The number now
    # comes from the artifact the table is built from, so a seam added or removed upstream reaches
    # this sentence instead of leaving it quietly describing a panel that no longer exists.
    _n_seams = expr["panel"]["n_seams"]
    n_expr_seams_txt = _word(_n_seams)
    # The exposure tissues are named by the artifact, so a fourth one added upstream reaches this
    # sentence instead of leaving it quietly describing three.
    _et = expr["method"]["exposure_tissues"]
    lo_cut_txt = (", ".join(t.lower() for t in _et[:-1]) + " and " + _et[-1].lower()
                  if len(_et) > 1 else _et[0].lower())

    _n_records = _gap_paired_records(expr)
    # ⚠ THE CURATED HALF OF THAT TOTAL, AND THE ONE LOCUS THAT CARRIES MOST OF IT AT THE LEAD SEAM.
    # Derived from the same per-locus block the new column is, so the sentence and the cells cannot
    # come apart. See the note beside the row rendering in `table6`.
    _n_curated = sum(L["screen_records"]["n_curated_records"] for L in expr["per_locus"])
    _cur_top = max(expr["per_locus"], key=lambda L: L["screen_records"]["n_curated_records"])
    # ⚠ TABLE 6's REGISTER DENOMINATOR NEEDS THE NUMBER IT IS *NOT*. "1 of 1" is unreadable beside
    # "2 of 5" unless the note says how many registers the seam admits, and that count belongs to
    # the geometry artifact Table 7 is built from — read, never typed.
    _registers = next(g["junction_spanning_registers_per_seam"] for g in gap["geometries"]
                      if g["architecture"] == GEOMETRY.architecture)
    n_failed, n_attempted = _default_depth_failures(collapse)
    # ⚠ EVERY TABLE IS RENDERED BEFORE THE DOCUMENT IS ASSEMBLED, not interpolated inside it, because
    # the banner now states a fact ABOUT the rendered rows — how close the nearest printed sequence
    # comes to a condemned one — and a header that describes the body cannot be written before the
    # body exists. Nothing else about the output changes.
    t1 = table1(atlas)
    t2 = table2(per_junction, thermo)
    (t3, any_unfiltered, deep_missing, any_no_parent,
     margin_up, margin_down) = table3(collapse, chance, atlas, per_junction)
    t4, n_clean, n_clean_junctions = table4(collapse, chance, thermo, _graded_loads())
    t5, ladder_backed_noncoding = table5(per_junction, noncoding, gap, ladder)
    t6 = table6(expr, per_junction)
    t7 = table7(gap)
    pct, minus, tot = _minus_strand_share(collapse)

    def _join(names, fmt="*{}*"):
        """A derived list of gene or junction names, rendered for a sentence rather than typed."""
        xs = [fmt.format(n) for n in names]
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]

    # ⛔⛔ EVERY CROSS-TABLE SENTENCE BELOW IS MEASURED OFF THE RENDERED ROWS (audit, 2026-08-19).
    # Table 4's caption asserted that Table 3 marks its five ⚑ designs do-not-order; recomputed over
    # what the two tables actually print, ONE of the five is in Table 3 at all, and at two of the
    # three junctions those five sit at, Table 3 prints a different design and marks it with
    # nothing. The claim was true of the SCREEN and false of the TABLE, which is the only kind of
    # cross-reference error a generator built from one artifact cannot catch — see `_md_table`.
    n_t4_flagged, t4_flag_shared, t4_flag_elsewhere = _flagged_rows_in_table3(t3, t4)
    n_lost, n_lost_zero = _near_match_screen_losses(t4)
    n_t2_rows = sum(1 for j in per_junction["junctions"] if j.get("best_available"))
    t2_max_duplex = max(int(b["parent_duplex_bp"] or 0)
                        for j in per_junction["junctions"] if (b := j.get("best_available")))
    t3_agg_n, (t3_agg_junction, t3_agg_cell, t3_agg_own) = _junction_aggregate_column(t3, chance)
    t3_agg_rows = len(_md_table(t3)[1])
    n_differ, n_twin, n_twin_at_run, twin_run = _near_twin_warning(t2, t3)
    # ⛔ A RECORD COUNT PRINTED AS A GENE COUNT, IN ALL THREE OF THESE TABLES (competitor review,
    # 2026-08-19). Every "near-match" cell is a count of RefSeq accessions; §5 states the collapse
    # and states it at the default ceiling, and these tables headline the deep one. Both figures
    # come from the collapse artifact's own per-depth summary, and the per-table ratios are measured
    # off the rendered rows, so a caption cannot claim a factor its own column does not carry.
    _deep_infl = _records_per_locus(collapse, "deep")
    t2_records_note = _records_note(
        _deep_infl, _printed_records_per_locus(t2, "sense-strand gap-paired near-matches"))
    t3_records_note = _records_note(
        _deep_infl, at_default=_printed_records_per_locus(t3, "near-matches, either strand"))
    t4_records_note = _records_note(_deep_infl)
    #: ⚠ A CLASS BAND IS NOT A ROW — see `_classed`. Counted as the rows carrying a basis cell, so
    #: the caption's denominator cannot drift when a class gains or loses a band.
    t5_rows = sum(1 for r in _md_table(t5)[1] if any(c for c in r[1:]))
    # ⛔ ≥ AND ≤ IN ADJACENT COLUMNS, ONE A FLOOR AND ONE A CEILING (display-item review,
    # 2026-08-19). Both senses are defined, in one long note printed once under the caption,
    # and twenty of the thirty-eight rows carry both marks — so a reader scanning the row is
    # asked to hold two opposite conventions from a paragraph they may be pages away from.
    # The counts are measured off the rendered rows so the sentence cannot outlive the marks.
    # ⛔ AND THE ΔΔG NOTE'S DENOMINATOR WAS 87 WHERE §2.5's IS 61 — see `_one_seam_share`.
    n_one_seam, n_nr4a3, n_liable = _one_seam_share()
    _t3_rows = _md_table(t3)[1]
    t3_rows = len(_t3_rows)
    t3_ge = sum(1 for r in _t3_rows if any("≥" in c for c in r))
    t3_le = sum(1 for r in _t3_rows if any("≤" in c for c in r))
    t3_both = sum(1 for r in _t3_rows
                  if any("≥" in c for c in r) and any("≤" in c for c in r))
    t5_max_duplex = _highest_duplex_printed(t5, "longest mature-parent duplex")
    # ⛔ THE DUAL READING BOX 1 APPLIES TO THE TWO LEADS, APPLIED TO EVERY ROW — see `_duplex` in
    # `table5`. RECOMPUTED off the rendered cells rather than asserted, so a row whose duplex moves
    # moves this sentence with it, and the roles are named because the two leads are the rows §4
    # actually asks a reader to synthesise.
    _t5_dup_i = _col(_md_table(t5)[0], "longest mature-parent duplex")
    _t5_dup = [(r[0], r[_t5_dup_i]) for r in _md_table(t5)[1] if re.match(r"^\d+ ?bp", r[_t5_dup_i])]
    _t5_liable = [role for role, cell in _t5_dup if "liable at" in cell]
    t5_loose_reading = (
        f"Every cell that carries a reading carries the verdict the SAME number takes at the loose "
        f"end of that range — that number is the row's `{DUPLEX_CSV_COLUMN}` in "
        f"`{os.path.basename(_manifest.OUT_CSV)}`, so the comparison is reproducible from the "
        f"canonical file and not only here: {_word(len(_t5_liable))} of the "
        f"{_word(len(_t5_dup))} rows that print "
        f"a duplex fall inside the do-not-order class there, and "
        f"{_word(sum(1 for r in _t5_liable if r == 'lead reagent'))} of them are the lead reagents "
        f"§4 names — which is the reading Box 1 states of those two and which no marker on this "
        f"table used to carry."
        if _t5_liable else
        f"Every cell that carries a reading carries the verdict the SAME number takes at the loose "
        f"end of that range — that number is the row's `{DUPLEX_CSV_COLUMN}` in "
        f"`{os.path.basename(_manifest.OUT_CSV)}` — and none of the {_word(len(_t5_dup))} rows "
        f"that print a duplex falls inside the do-not-order class there.")

    # ⛔ TABLE 1 PRINTED TWO COLUMNS THAT ARE THE SAME COLUMN AND SAID NOTHING (audit, 2026-08-19).
    # "in-frame" and "with ≥1 fusion-specific design" agree in every row and in the total, so as
    # printed the second carries no information — and a reader has no way to tell whether that is a
    # measured coincidence or a duplicated cell, which is the worse reading in a table whose whole
    # subject is a filter. It is a coincidence, and a contingent one: the two are different
    # conditions, arithmetic frame compatibility and a design existing at the seam, and the second
    # can only ever be the smaller. THE SENTENCE IS EMITTED FROM THE COMPARISON, so a corpus in
    # which they come apart gets the sentence that describes that instead.
    _t1 = _md_table(t1)
    _i_f, _i_d = _col(_t1[0], "in-frame"), _col(_t1[0], "with ≥1 fusion-specific design")
    _t1_body = [r for r in _t1[1] if not r[0].startswith("**")]
    _agree = [r for r in _t1_body if r[_i_f] == r[_i_d]]
    t1_columns_note = (
        "Both middle columns are printed because they are different conditions and only one of them "
        "is arithmetic: in-frame is a property of the exon lengths, while a fusion-specific design "
        "existing at the seam is a property of the sequence, and it can only ever be the smaller of "
        f"the two. They agree in every one of the {len(_t1_body)} partner rows here, which is a "
        "measurement and not a duplicated cell."
        if len(_agree) == len(_t1_body) else
        f"Both middle columns are printed because they are different conditions — in-frame is a "
        f"property of the exon lengths, a fusion-specific design existing at the seam is a property "
        f"of the sequence — and they part company at "
        f"{len(_t1_body) - len(_agree)} of the {len(_t1_body)} partners.")
    t1_best_margin = max(r[-1] for r in _t1_body if r[-1] not in ("—", ""))
    # ⚠ THE SIZE OF THE SET THOSE TWO COLUMNS SUMMARISE, MEASURED PER PANEL RATHER THAN INFERRED
    # FROM THE REGISTER COUNT. Today every in-frame junction admits exactly one design per register,
    # so the two arithmetics agree; a panel that lost one would leave a caption asserting a
    # multiplication that no longer holds.
    _per_panel = {p.get("n_fusion_specific") for p in atlas["panels"]}
    t1_design_note = (
        f"every one of the {len(atlas['panels'])} in-frame junctions admits "
        f"{_word(next(iter(_per_panel)))}, one per junction-spanning register, so a partner's range "
        f"is over its in-frame count times {_word(_registers)}."
        if len(_per_panel) == 1 else
        f"the {len(atlas['panels'])} in-frame junctions admit between {min(_per_panel)} and "
        f"{max(_per_panel)} apiece, so a partner's range is over a set this table does not size.")

    # ⛔ TABLE 6's "soft-tissue proxy maximum" NAMED NO PROXY (audit, 2026-08-19). The column is a
    # maximum over a set the caption never listed, and the tissue printed in each cell is the argmax
    # — so a reader met six different tissue names down one column with nothing saying they are one
    # panel, and no unit, the TPM sentence beside it covering only the three exposure columns. Read
    # from the same `method` block the exposure tissues are read from.
    _proxies = expr["method"]["tumour_compartment_proxy_tissues"]
    if not _proxies:
        raise SystemExit(
            "Table 6's soft-tissue column is a maximum over `method.tumour_compartment_proxy_tissues` "
            "and the artifact no longer names them. Re-derive it rather than printing a maximum "
            "over a set the caption cannot name.")

    def _flag_where():
        """Where a reader actually finds Table 4's ⚑ verdicts corroborated, and where they do not."""
        shared = (f"{_word(len(t4_flag_shared))} of them — "
                  + _join([f"5′-{s}-3′" for s in t4_flag_shared], "{}")
                  + f" — {'is' if len(t4_flag_shared) == 1 else 'are'} also printed in Table 3 and "
                    f"{'carries' if len(t4_flag_shared) == 1 else 'carry'} ⚑ there"
                  ) if t4_flag_shared else "none of them is printed in Table 3 at all"
        misses = "; ".join(
            f"at {j} it prints {'no row at all' if s is None else f'5′-{s}-3′, reading {d}, unmarked'}"
            for j, s, d in t4_flag_elsewhere)
        n_only = n_t4_flagged - len(t4_flag_shared)
        tail = ("" if not t4_flag_elsewhere else
                f" Table 3 selects each junction's HIGHEST-MARGIN design, which at those seams is a "
                f"different molecule: {misses}. Do not read an unmarked Table 3 row as a clearance "
                f"of a design marked here.")
        return (f"**Those {_word(n_t4_flagged)} verdicts are carried in this table, and mostly "
                f"nowhere else.** Table 3 prints one row per junction, so {shared}; the other "
                f"{_word(n_only)} are marked in no other display item.{tail}")

    t4_flag_where = _flag_where()

    # ⛔ COLUMNS THAT READ THE SAME VALUE IN EVERY ROW, WITH NOTHING SAYING WHETHER THAT IS A
    # MEASUREMENT OR A PLACEHOLDER (display-item review, 2026-08-19). The review named two;
    # RECOMPUTED off the rendered rows there are three, and they do not mean the same thing — one
    # of them is the condition of membership in this table and is therefore constant BY
    # CONSTRUCTION, while the other two are readings that happen to agree across these nine
    # designs. A reader cannot tell those apart from the cells, and the difference decides whether
    # a zero is informative. Measured here rather than asserted, so a column that stops being
    # constant leaves the sentence instead of being described as constant forever.
    _t4h, _t4b = _md_table(t4)
    _deep_from = next((i for i, h in enumerate(_t4h) if h.startswith("at the deeper ceiling")),
                      len(_t4h))
    _t4_const = [(i, _t4h[i], _t4b[0][i]) for i in range(len(_t4h))
                 if len({r[i] for r in _t4b}) == 1 and _t4b[0][i] not in ("", "—")]

    def _t4_name(i, h):
        if sum(1 for x in _t4h if x == h) == 1:
            return f"“{h}”"
        return f"“{h}” ({'at the deeper ceiling' if i >= _deep_from else 'at the default depth'})"

    _t4_sel = [(i, h, v) for i, h, v in _t4_const
               if h.startswith("of those, on the sense strand") and i < _deep_from]
    _t4_rest = [(i, h, v) for i, h, v in _t4_const if (i, h, v) not in _t4_sel]
    t4_constant_columns = ("" if not _t4_const else (
        f"{_word(len(_t4_const)).capitalize()} columns read one value in every row, and they are "
        f"not one kind of fact. "
        + ("".join(f"{_t4_name(i, h)} reads {v} in all {len(_t4b)} rows BY CONSTRUCTION: it is the "
                   f"property membership of this table is defined by. " for i, h, v in _t4_sel))
        + ("" if not _t4_rest else
           ", ".join(f"{_t4_name(i, h)} reads {v}" for i, h, v in _t4_rest)
           + f" in all {len(_t4b)} rows, which is a measurement over these designs and not an "
             f"unfilled cell; neither separates one row from another.")))

    # ⚠ THE SAME MEASUREMENT THE DO-NOT-ORDER BANNER MAKES, RUN BETWEEN THE TABLES RATHER THAN
    # BETWEEN a table and the condemned list. Emitted only while the disagreement exists.
    def _twin(other, here):
        if not n_twin:
            return ""
        return (f"⚠ At {_word(n_differ)} junctions {other} names a DIFFERENT DESIGN from {here}, "
                f"because the two tables rank on different keys. At {_word(n_twin)} of those "
                f"{_word(n_differ)} one of the pair is condemned and the other is not, and at "
                f"{_word(n_twin_at_run)} of those the two share {_word(twin_run)} of their "
                f"{GEOMETRY.oligo_len} contiguous bases — one register apart. Check the junction "
                f"AND the whole sequence against `{os.path.basename(_manifest.OUT_CSV)}` before "
                f"ordering either.")

    t2_twin_warning = _twin("Table 3", "this table")
    twin_warning_t3 = _twin("Table 2", "this table")

    # ⛔ THE PRIMARY SORT KEY WAS NAMED AND NEVER DEFINED — see `_parent_liability_definition`.
    _lia_parents, _lia_compartment = _parent_liability_definition()
    t2_liability = (
        f"A design's parent liability is the length of the longest contiguous duplex any of the "
        f"{_word(len(_lia_parents))} wild-type parent transcripts — {_join(_lia_parents)} — forms "
        f"through its whole catalytic gap, searched in the {_lia_compartment} in the forward "
        f"orientation only, and it disqualifies at {_word(_parent_cut_bp())} base pairs; the "
        "“longest parent duplex through the gap” column is that same length for the design the row "
        "names.")

    # ⛔ TABLE 2 IS ONE ACCEPTOR EXON AND SAID SO NOWHERE (display-item review, 2026-08-19). Its
    # caption calls itself the table that answers "the question a patient's fusion poses", and all
    # 38 of its rows are *NR4A3* exon-3 acceptor seams — so the acceptor half is a constant, the
    # row varies only the donor, and the seams at a different acceptor are missing with no line
    # saying they exist. They do exist, they are graded out of this panel rather than screened and
    # found wanting, and both of the patient-derived models §2.6 names are exon-2 seams. The set is
    # collected from the artifacts that own it — the panel's own acceptors and the non-canonical
    # acceptor table's — so a seam promoted into the panel leaves this sentence rather than being
    # named in it forever.
    def _acceptor(label):
        gene, _, exon = label.partition("_")
        return f"*{gene}* " + ("exon " + exon[1:] if re.fullmatch(r"e\d+", exon) else exon)

    _t2_acc = sorted({j["junction_label"].split("__", 1)[1] for j in per_junction["junctions"]})
    _nc_seams = [j["junction_label"].replace("__", "::").replace("_", " ")
                 for j in sorted(noncoding["junctions"], key=lambda j: _junction_sort_key(
                     j["junction_label"]))]
    _cryptic = ((noncoding.get("⭐_wild_type_NR4A3_cleavage_liability") or {})
                .get("positive_control") or {}).get("control_junction")
    if len(_t2_acc) != 1 or not _nc_seams or not _cryptic:
        raise SystemExit(
            "Table 2's caption states which acceptor seams it does and does not carry, and that "
            f"sentence is read from the panel ({len(_t2_acc)} acceptors), the non-canonical "
            f"acceptor table ({len(_nc_seams)} seams) and the liability scan's control junction "
            f"({_cryptic!r}). One of the three no longer reads, so the caption would either assert "
            "a scope it cannot check or leave the omission silent again. Re-derive them.")
    # ⛔ WHETHER THE RECOMMENDATION SURVIVES ANOTHER CUT — see `_rank_stability`. Reported over the
    # cuts BELOW the adopted one, because those are the ones the paper's own cited range reaches
    # and the only direction in which a printed reagent can become one not to order.
    _stab = [(c, r, s, d) for c, r, s, d in _rank_stability(per_junction)
             if c >= _cut_sensitivity()["loose_bp"]]
    _n_seams_total = len(per_junction["junctions"])
    t2_cut_stability = (
        "⚠ The recommendation is a reading at that one cut, and what moves with the cut is "
        "AVAILABILITY more than identity. Re-ranked on the same screened designs by the same keys, "
        f"the seams that still have a best available design number "
        + "; ".join(
            f"{r} of the {_n_seams_total} at {_word(c)} base pairs, "
            + ("all of them the molecule printed here" if not d else
               f"{_word(d)} of them a different molecule")
            for c, r, s, d in reversed(_stab))
        + ". Nothing was re-screened to say that; only the liability test moved, and a seam that "
          "loses its row loses a reagent rather than gaining a worse one."
        if _stab else "")

    t2_acceptor_scope = (
        f"Every row here is an {_acceptor(_t2_acc[0])} acceptor seam: the acceptor half is the same "
        f"in all {len(per_junction['junctions'])} of them, so what a row "
        f"varies is the donor and not which acceptor a patient's fusion joins to. The seams at "
        f"another acceptor are graded out of this panel rather than screened and found wanting, and "
        f"they are reported elsewhere: the {_word(len(_nc_seams))} *NR4A3* exon-2 acceptor seams — "
        f"{_join(_nc_seams, '{}')} — are in Table 5 and §2.6, and the patient-derived models §3 "
        f"names carry that acceptor rather than this one; the {_cryptic} seam reaches these tables "
        "only through the design the do-not-order list above names.")

    # ⚠ TABLE 2's DENOMINATOR RULE AND THE COUNT BEHIND IT — see `_deep_depth_failures`, which
    # asserts that the shortfall and the failures are the same three records before this is printed.
    n_deep_failed, n_deep_attempted = _deep_depth_failures(per_junction, _registers)
    # ⚠ AND THE ROWS TABLE 5's MEMBERSHIP SENTENCE CANNOT CLAIM FIVE MEASURED COMPARTMENTS FOR.
    unscanned_donors, premrna_genes = _premrna_unscanned_donors(noncoding)
    # ⚠ THE ROW-ORDER SENTENCE COUNTED ALL FOUR EXON-2 SEAMS AS "beside the panel" AND ONE OF THEM
    # IS NOT THERE — it is a rung, several rows higher. Derived from the same two facts the class
    # rule is derived from, so the count and the rule cannot come apart.
    n_beside_txt = _word(sum(1 for _, s, _, _ in _TABLE5_ROWS if s == "noncoding")
                         - len(ladder_backed_noncoding))

    # ⚠ EMITTED PER DIRECTION THAT THE TABLE ACTUALLY SHOWS, never as a pair of sentences describing
    # a case the corpus no longer has. `margin_up` is the censoring reconciliation the paragraph
    # above already sets up; `margin_down` is Table 2's ranking, which is a different cause.
    margin_both = ("" if not margin_down else
                   " Table 2 can also name one of LOWER margin, for a different reason and not a "
                   "disagreement: it ranks by parent liability, then pre-mRNA sites, then gene "
                   "loci, and reaches gap-level margin only as a tie-break, so a cleaner design "
                   "outranks the highest-margin one this table names.")
    margin_up_txt = ("" if not margin_up else
                     ", and why Table 2 — which selects from the deeper re-screens — can name a "
                     "design of HIGHER margin at the same junction")

    # ⚠ SAME RULE: the pre-mRNA caveat is emitted only where a row's donor is outside the set the
    # screen searched, so a re-fetch that closes the gap removes the sentence rather than leaving it
    # describing a limitation the table no longer has.
    premrna_caveat = ("" if not unscanned_donors else
                      " The screen condition counts screens that RAN over a junction's designs and "
                      "not compartments measured for every gene a row names: the pre-mRNA screen behind "
                      f"the exon-2 acceptor rows carried unspliced sequence for {_word(len(premrna_genes))} "
                      f"parent genes — {_join(premrna_genes)} — so a seam whose donor is outside "
                      f"that set has an absent reading of its own donor's introns in that "
                      f"compartment rather than a clean one. {_join(unscanned_donors)} is that case "
                      "here, for the reason §2.6 gives, and the row is in this table on the same "
                      "footing as the others.")

    # ⚠ AND THE TWO MEMBERSHIP CLASSES ARE NAMED FROM THE LADDER — see `table5`. The clause is
    # emitted only while an exon-2 seam is actually one of the ladder's entries.
    exon2_rung = ("" if not ladder_backed_noncoding else
                  " The reagent column is editorial, but which of the two membership classes a row "
                  "falls in is the ladder's decision as well, and it is legible in the last two "
                  "columns: a junction the ladder NAMES IN ONE OF ITS ENTRIES carries that entry's "
                  "cumulative figure and increment, and a junction that qualifies but appears in no "
                  "entry carries “adds nothing” and the reason instead. "
                  "That is why one *NR4A3* exon-2 acceptor seam — "
                  f"{_join([lb.replace('__', '::').replace('_', ' ') for lb in ladder_backed_noncoding], '{}')}"
                  " — is a rung here while the other three are reported beside the panel: the "
                  "ladder prices the type 2 transcript's breakpoint on the same single series, and "
                  "such a rung can still print an increment of zero, because that series never "
                  "named the transcript — an unnamed count rather than a measured absence. Being a "
                  "rung of the ladder is not being pooled into the panel, which is the separate "
                  "statement below and is unchanged.")

    # ⛔ THE DO-NOT-ORDER LIST, AND THE MEASUREMENT THAT SAYS WHY IT HAS TO BE PRINTED. Two of the
    # three condemned designs are register shifts of a reagent Table 5 prints; the run below is how
    # much of one sequence a reader could transcribe correctly and still be holding the other.
    condemned = _condemned_designs(noncoding)
    _printed = sorted(set(re.findall(r"5′-([ACGT]+)-3′", "\n".join([t1, t2, t3, t4, t5, t6, t7]))))
    # ⛔ THE FIRST SAFETY STATEMENT IN THE DOCUMENT READ AS A WHITELIST (display-item review,
    # 2026-08-19). "Do not order these three sequences … and none of them is in any row of these
    # tables" is TRUE and sets exactly the wrong frame: it is the first thing a reader meets, it
    # names three molecules as THE forbidden set, and it then says the tables are clear of them.
    # RECOMPUTED over the rendered rows: fifteen further rows across Tables 3 and 4 — fourteen
    # distinct molecules, one printed in both — carry ⚑ and are also not to be ordered. The ⚑ keys
    # carry the real rule, four and eleven pages later, by which point the frame is set.
    _flag_rows = [ln for t in (t1, t2, t3, t4, t5, t6, t7)
                  for ln in _md_table(t)[1] if any("⚑" in c for c in ln)]
    _flag_seqs = {q for ln in _flag_rows for c in ln if (q := _seq_in(c))}
    flagged_in_tables = (
        f"A further {_word(len(_flag_rows))} rows of these tables — {len(_flag_seqs)} distinct "
        f"molecules, since one is printed twice — are marked ⚑ in their own row and are also NOT to "
        f"be ordered, for the same reason against a wild-type parent that is not always *NR4A3*. "
        f"An unmarked row is not a clearance either; see the ⚑ note under Table 3."
        if len(_flag_rows) != len(_flag_seqs) else
        f"A further {_word(len(_flag_rows))} rows of these tables are marked ⚑ in their own row and "
        f"are also NOT to be ordered, for the same reason against a wild-type parent that is not "
        f"always *NR4A3*. An unmarked row is not a clearance either; see the ⚑ note under Table 3.")
    _run = max((_longest_shared_run(c, p) for c in condemned for p in _printed), default=0)
    _clen = min(len(c) for c in condemned)
    condemned_txt = ", ".join(f"5′-{s}-3′" for s in condemned)

    # ⛔ A LEGEND FOR A MARKER NO ROW CARRIES IS WORSE THAN NO LEGEND (2026-08-13). Every one of the
    # 38 junction screens is orientation-filtered, so `‡` had not been emitted for some time — and
    # the paragraph explaining it stayed, telling a reader to look for upper-bound rows that are not
    # there, and quoting a stale 47% into the bargain. The block is now conditional on a row
    # actually being marked.
    dagger = ("" if not any_unfiltered else
              "\n\n‡ This junction's counts were not filtered by alignment orientation, so they "
              f"still include minus-strand hits — across the filtered corpus, {pct}% of all apparent "
              "gap-paired hits. Its numbers are upper bounds and are NOT comparable with the "
              "unmarked rows.")

    # ⚠ EMITTED ONLY WHERE A CELL CARRIES THE MARKER — see the note beside `deep_missing` in
    # `table3`. The count of failures is derived either way and stays in the sentence above it.
    no_deep = ("" if not deep_missing else
               " A “—” means the deeper re-screen returned no result for that design and is not a "
               "count of zero.")

    # ⚠ SAME RULE AS ‡ AND ³: the paragraph is emitted only where a row actually carries the marker,
    # so a corpus in which every junction gains a clearing design does not leave a legend pointing at
    # a warning that is no longer in the table.
    no_parent = ("" if not any_no_parent else
                 "\n\n† No design screened at this junction clears the parent screen: every one of "
                 "them pairs a wild-type parent gene through the whole catalytic gap, at the "
                 "parent-duplex criterion applied throughout. This table ranks by gap-level margin, "
                 "so the sequence in such a row is that junction's highest-margin design and "
                 "nothing more; it is not a design any screen passes, and Table 2 gives the same "
                 "junction no best-available reagent for that reason — its “designs clearing the "
                 "parent screen” cell reads 0. Do not order the sequence in a marked row."
                 "\n\n⚑ This design pairs a wild-type parent gene through the whole catalytic "
                 f"gap at the {_word(_parent_cut_bp())}-base-pair criterion applied throughout, "
                 "and the gene it pairs "
                 "is named beside the length. The marker is on the DESIGN, where † is on the "
                 "JUNCTION: a row can be unmarked by † and still carry ⚑, because this table "
                 "prints each junction's highest-margin design rather than its cleanest. Do "
                 "not order the sequence in a row marked ⚑ — pairing a parent through the "
                 "whole gap is this paper's central negative (§4.5) and surrenders the only "
                 f"advantage the modality has. An unmarked row is not a clearance. {_cut_caveat()}"
                 f" {twin_warning_t3}")

    doc = f"""<!-- GENERATED — DO NOT EDIT. Regenerate: python3 research/manuscripts/submission_tables.py -->

# Tables — fusion-junction ASO submission

{_self_identification()}

**Research use only, and not for administration to any person or animal.** Every oligonucleotide
sequence named in these tables is a research reagent intended solely for laboratory investigation.
None is a medicine or a candidate drug, none has been synthesised or tested by anyone, and none may
be administered to any human being or animal, compounded for such use, or supplied to any person for
such use. Custom oligonucleotide synthesis is commercially available, so the restriction is on use
rather than on access. A table row is not a recommendation, and the full statement is in the main
text's Declarations.

**Chemistry — what the `geometry` column and Table 7's columns denote.** Every design named in these
tables is a gapmer of locked-nucleic-acid (LNA) wings around a central DNA gap, on a phosphorothioate
backbone, and each geometry is written wing–gap–wing: {_chemistry(gap)}. That architecture is what
the main text's Methods specify, and it is the chemistry every screen, every design rule and every
duplex figure in these tables assumes. The bare base sequence of a row ordered as unmodified DNA is a
different molecule, and nothing reported here is about it.

**Do not order these {_word(len(condemned))} sequences.** The main text names them as NOT to be
carried forward — each pairs its whole catalytic gap against the patient's own un-rearranged *NR4A3*
allele — and none of them is in any row of these tables: {condemned_txt}. They are printed here
because excluding them by description leaves a reader with a transcribed sequence nothing to check it
against, and the margin for a slip is small: the closest sequence these tables DO print shares a run
of {_run} contiguous bases with one of the {_word(len(condemned))}, whose own length is {_clen}.

**⛔ THAT LIST IS NOT THE WHOLE DO-NOT-ORDER SET, AND THESE TABLES ARE NOT A WHITELIST.** {flagged_in_tables}

**Table 1. The in-frame junction space across {_word(len(atlas["partners_scored"]))} *NR4A3* fusion partners.** Every
donor-exon × *NR4A3*-acceptor-exon pair was graded against the frame condition before any design was
emitted. Every design counted here is at the {GEOMETRY.architecture} geometry — a {GEOMETRY.oligo_len}-mer, the architecture the chemistry note above expands — so this table sizes one design space and not the modality. {_margin_gloss()} Frame compatibility is an arithmetic property of exon
structure and is not a claim about which junctions patients carry. A fusion-specific design is one
whose catalytic gap contains at least one base that no wild-type parent carries at that position, so
its gap-level margin is one or more. {t1_columns_note} “GC range of those designs (%)” and “best
gap-level margin” are over that partner's fusion-specific designs: {t1_design_note} The margin
column is a maximum, so a row reading {t1_best_margin} says the partner has a design at the
geometry's ceiling — half the gap rounded down, which Table 7 gives — and nothing about how many.

{t1}

**Table 2. The best available design at each in-frame junction that has one — {n_t2_rows} of the {per_junction["n_junctions"]}.** Table 4
selects across the panel and Table 3 selects within each junction by gap-level margin; this table
selects within each junction by parent liability, which is the question a patient's
fusion poses. {t2_acceptor_scope} {_JUNCTION_SORT_NOTE} {_margin_gloss()} {t2_liability} Designs are ranked by parent liability first, since sparing the wild-type parents is
what the modality exists for, then by pre-mRNA sites, then by distinct gene loci, with ties broken
on gap-level margin rather than on raw hit counts. Nothing was re-screened: every field is joined
from a screen already reported above. The denominator of the “designs clearing the parent screen”
column is not a parent-screen figure: it is how many of that junction's designs RETURNED a deep
alignment screen, which is the screen supplying every rank key here. Each seam of this panel is
tiled by {_word(_registers)} junction-spanning registers (Table 7), and {n_deep_failed} of the
{n_deep_attempted} deep submissions failed at the remote service, so a design whose submission
failed is absent from its junction's row set and appears in neither half of the cell — the only
reason a denominator here reads below {_word(_registers)}, and an identity this generator checks
before building the table. The parent screen itself is offline and exhaustive over every design, so
the numerator alone is what it decided. Whether a junction has a published exon-resolved breakpoint is
reported separately from specificity and never folded into the ranking — “published” means an
exon-resolved EMC breakpoint is reported for that exon pair in prose; “published (deposit)” that the
exon is resolved instead by a deposited chimeric record, which §2.3 describes; “exon not reported”
that a breakpoint of that partner is resolved at a different exon, by either route; and “none
published” that no breakpoint of that partner is resolved to an exon anywhere on the public record.
*TCF12* and *TFG* are both the deposit case, and they are the same case: one seam each, resolved by
a deposited chimeric record — AF289510.1 and AY532911.1 — rather than by an exon named in prose, so
each carries one “published (deposit)” row and reads “exon not reported” elsewhere. That the two are
graded alike is not a statement that their evidence is equally strong: the *TFG* record rests on one
primary sequence plus four patent sequences that are one family from one group, with no report
behind any of them, which §2.3 states and this column does not. “None published” is absence of
evidence: EMC case
reports usually name the partner gene without sequencing to nucleotide resolution. Gap-paired
near-matches are at the tenfold deeper alignment ceiling, where every hit list is complete.
{t2_records_note} The
genome column is the observed number of gap-paired sites at ≤2 mismatches over the number expected
for an arbitrary 16-mer, so 1.00 is chance. It is counted EITHER ORIENTATION against an
either-orientation null, unlike the sense-filtered near-match columns beside it, so it includes
sites on the strand an antisense oligonucleotide cannot pair; §2.7 gives the share for the lead. A junction with no design clearing the parent screen is
reported as such rather than given a best row, and Table 3 marks those junctions too, since Table 3
ranks by margin instead and does print a sequence at each of them. **Clearing the parent screen
means one thing and one thing only: no wild-type parent pairs the whole catalytic gap at
{_word(_parent_cut_bp())} base pairs or more.** {_cut_caveat()} No row of this table reaches the
criterion — the column's highest reading is {t2_max_duplex} base pairs — so no row carries the ⚑ Tables 3 and 4
use, and an unmarked row here is not a clearance on any wider ground. {t2_cut_stability} {t2_twin_warning} The last column is a conventional
design audit, computed for whichever design this table names from the same artefact and by the same
code Table 4 uses. {_rule_audit_note()} It is reported beside the ranking and is never folded
into it: the two orderings select different molecules, which is the disagreement §2.10 is about, and
this is the table one reagent is chosen from. A design the audit does not cover would read “not
audited” rather than blank, since a blank in a rules column reads as breaking none. {_ordering_clause()}

{t2}

**Table 3. Predicted specificity per screened junction.** One row per junction, in Table 2's order. {_JUNCTION_SORT_NOTE} Figures are for the
design with the highest gap-level margin at that junction, which is the ranking the Methods define,
and NOT for that junction's cleanest design — the two are often different molecules, and the
cleanest ones are in Table 4. {_margin_gloss()} Every figure in a row is that named design's own EXCEPT the last
column, which is a median and a maximum over every design screened at the junction and is therefore
a junction aggregate rather than a property of the molecule beside it: at {t3_agg_junction} the cell
reads {t3_agg_cell} while the design the row names returns {t3_agg_own}, and the two part company at
{t3_agg_n} of the {t3_agg_rows} rows. The margin column is therefore the best among the designs that
RETURNED a screen at this depth: {n_failed} of the panel's {n_attempted} default-depth submissions
failed at the remote service, which is why a junction can show fewer than {_word(_registers)} designs screened
here{margin_up_txt}.{margin_both} {t3_records_note} **⚠ The two censoring marks point in OPPOSITE directions and sit on adjacent columns: “≥” is a LOWER bound, because the search was capped, and “≤” an UPPER bound, because the stored figure over-counts.** {t3_ge} of the {t3_rows} rows carry “≥”, {t3_le} carry “≤” and {t3_both} carry both. A “≥” marks a right-censored count, and the two columns are
censored by DIFFERENT caps, which is why an uncensored transcript count here can exceed the retained
{SAVED_HITS}: the alignment screen itself returns at most 50 hits per query, so a transcript count at
50 is a lower bound, while the locus column is recounted from the {SAVED_HITS} hits the screens
RETAIN, so a locus count from a design with more than {SAVED_HITS} hits is a lower bound too. All {sum(1 for s in collapse["screens"] if s.get("junction_label"))} junction screens
are filtered by alignment orientation. `XM_`/`XR_` records are computationally
predicted gene models rather than curated transcripts, and are counted separately for that reason.
None of these numbers is a measurement of off-target activity.\n\n¹ A near-match count is what the search returned on EITHER strand; a match on the strand opposite the target window cannot be hybridised by an antisense oligonucleotide and is not a liability. Across this corpus {pct}% of apparent gap-paired hits ({minus} of {tot:,}) are of that kind, which is why the two columns differ and why the raw count alone should not be read as load. This column counts only the {SAVED_HITS} RETAINED hits. The gap-paired locus column is recounted from those hits wherever they are the complete list, and is exact there; a “≤” marks a truncated design, where the column instead carries the screen's own count over every ranked hit, computed under a locus assignment since corrected that split some genes across accessions and therefore over-counts. The two columns are not in conflict where a truncated design shows “≥0” sense-strand hits and a non-zero gap-paired locus count: the sense-strand hits are real and simply fall outside the stored window, which is precisely why such a design cannot be called clean.\n\n² Counted over the gap-paired loci only, not over all of that design's near-match loci.\n\n³ The same design re-screened at a tenfold deeper alignment ceiling, with retention raised to match it so that no hit list is truncated. Because no list is truncated, the gap-paired locus column at this depth is recounted from the complete stored hits under the current locus assignment and is exact; it is not the screen's own stored figure, which was computed before that assignment was corrected and splits any gene whose description carries a comma across one accession per transcript variant. It is therefore the same quantity, counted the same way, as the locus figures in Table 2 and in the Results. The three columns are the counterparts of the default-depth columns to their left, given beside them rather than in place of them because the default depth is where the corpus-wide counts elsewhere in the paper were computed and the two must stay comparable. Read together they are the paper's censoring result at the level of a single row: a default-depth count is a lower bound whether or not it reached the 50-hit cap, and three junctions whose default cell reads zero in the gap-paired column carry gap-paired hits at ten times the depth. Three of the panel's 190 records failed at this ceiling; they are absent from the deep set rather than counted as zero in it.{no_deep} {_ordering_clause()}{no_parent}{dagger}

{t3}

**Table 4. The {n_clean} designs with no sense-strand near-match at the default search depth — {_word(n_lost)} of them at that depth only, and {_word(n_t4_flagged)} of them not to be ordered.** {_word(n_lost).capitalize()} of
these lose the property when the same junctions are re-screened at a tenfold deeper alignment
ceiling, {_word(n_lost_zero)} of them having returned no near-match at all here; §2.4 reports that
measurement and names the {_word(n_clean - n_lost)} that survive it. This table is the default-depth result, retained
because it is the depth at which the corpus-wide counts elsewhere in the paper were computed. {_margin_gloss()} Every
design that QUALIFIES is listed, at each of the {n_clean_junctions} junctions where one does; this
is not one row per junction, and it is not every design at those junctions, which are tiled by
{_word(_registers)} registers each. A design qualifies only
if its retained hit list is not truncated — no more near-matches than the {SAVED_HITS} the screens store — because the
strand of an unstored hit cannot be recovered, so a truncated list cannot establish that nothing
on the sense strand remains. The underlying search is itself capped, so these are the designs whose
near-match lists are shortest, not the designs whose lists are known to be exhaustive. ΔΔG°37 is the margin by which the fusion duplex is favoured over the better of the
two runs a parent pairs at the junction itself, for an unmodified DNA:RNA hybrid; it does not score the
mature-parent duplexes of §2.5, of which {n_liable} designs of the panel carry one, {n_nr4a3} of them
against wild-type *NR4A3*, and {n_one_seam} of THOSE {n_nr4a3} at one recurring site rather than
anywhere else in a parent — the mature *NR4A3* exon-2/exon-3 seam every design's acceptor half
reaches. Because the fusion duplex pairs
both LNA wings and each parent duplex only one, it is a lower bound on the modified
oligonucleotide's discrimination rather than an upper one. {t4_records_note} None of these numbers is a measurement of off-target
activity, and none speaks to cleavage. **This table condemns nothing and clears nothing.** Its final
column is a verdict from ONE screen, the near-match screen, and {_word(n_t4_flagged)} of these rows carry the ⚑ of
the mature-parent screen: a wild-type parent pairs their whole catalytic gap at the {_word(_parent_cut_bp())}-base-pair
criterion, which is this paper's central negative. {t4_flag_where} A
design can survive every near-match screen here and still be one not to order. {t4_constant_columns}
{_ordering_clause()}\n\n⁴ A DISCRIMINATION-WEIGHTED COUNT OF NEAR-MATCH SITES, and the unit is
sites: each of the design's near-matches enters at one, reduced by the modelled loss of RNase-H1
cleavage at however many mismatches fall in its catalytic gap, and the weights are summed — so a 0
means no near-match survives either weighting, and the column is not a rate, a concentration or a
quantity of cleaved RNA. Computed under the optimistic five-fold and the pessimistic
no-discrimination bound on RNase-H1 single-mismatch discrimination. A single value means the two
bounds agree; where two are printed, the width is TRUNCATION of the saved hit list and not
statistical uncertainty. No RNase-H1 cleavage is measured anywhere in this work.\n\n⁵ {_rule_audit_note()}\n\n⁶ Whether the design still carries no
sense-strand near-match once its junction is re-screened at the tenfold deeper ceiling. The verdict
is computed from the three deep columns beside it, not asserted, so this table cannot come to
disagree with §2.4 about which designs survive. It is a verdict on that screen alone and not on the
parent screen of note ⁷. The {_word(n_lost)} that do not are the reason this table's
default-depth zeros must not be read on their own.\n\n⁷ The longest contiguous duplex a wild-type
parent gene forms through this design's whole catalytic gap, with the gene that forms it. ⚑ marks
{_word(_parent_cut_bp())} base pairs or more, the criterion applied throughout: **do not order a design marked ⚑** —
pairing a parent through the whole gap is this paper's central negative and surrenders the only
advantage the modality has. An unmarked row is not a clearance, only a reading at that one cut. {_cut_caveat()}

{t4}

**Table 5. Every seam the coverage ladder qualifies, with the ladder's bounds and §4's two contrast
arms beside them, what each costs on each screen and what each buys in coverage.** The rows are in the order §4 decides them:
the two lead reagents, the rungs of the coverage ladder above them, the bounds above those, the
remaining junction with a published exon-resolved breakpoint and a reagent through all five deep
screens, the {n_beside_txt} *NR4A3* exon-2 acceptor seams the ladder carries no entry for, reported
beside the panel, and the two contrast arms. {_margin_gloss()} Membership is the coverage ladder's and not this table's: every junction its best-supported
buildable panel qualifies — a published exon-resolved breakpoint, and all five specificity screens
run to completion over that junction's designs, each condition read from the table that owns it —
has a row here whether or not §4 names its reagent, and the generator refuses to build if a
qualifying junction has no row. A row can therefore qualify and still buy no coverage,
which is a statement about the denominator and not about the reagent.{premrna_caveat}{exon2_rung} Cumulative coverage is the
coverage of the reagent set through that row, so the two leads are
one rung and carry one figure between them; it is discounted by the breakpoint distribution of a
single series and is not a partner figure, and its parenthetical range is composed from each
breakpoint fraction's own Wilson bound rather than from the point estimate. That range is a
composed endpoint and carries no nominal coverage level: it is not a confidence interval, and
§4.1 gives the reason the four quantities cannot be composed to one. Every rung and every bound prints
the increment it adds over the row above it, so no figure reads as bought by the row it sits on.
Each coverage figure and each increment is rounded to one decimal independently, from the unrounded
fraction rather than from each other, so a row's figure plus the increment printed on the row below
it need not reproduce that row's figure in the last place. A
bound row is what coverage would be if every remaining breakpoint of that partner were covered,
which nothing measures. A bound that names no reagent still has a row, and the *EWSR1* one is the
larger of the two steps between the last buildable rung and the table's top figure: the three
breakpoints it prices are ones the retrieved record does not resolve to an exon, so no sequence,
geometry or screen result exists for them and every such cell is empty. If those breakpoints are
private rather than recurrent, no stocked panel reaches them at any size. A row that
adds nothing prints why, because the two reasons differ: the partner is absent from the 58-case
cohort behind the denominator, or the partner is present and that exon pair carries no count in the
measured within-partner distribution. The exon-2 acceptor rows are from the non-canonical-acceptor
table and are never pooled into the panel, since the grade that excludes their junctions from the 38
is unchanged. A contrast arm carries no coverage figure and must not borrow its junction's, which is
already counted a row above. The three controls §4 requires have no row and can have none: the
fusion-negative isogenic comparator is a cell line rather than a reagent; the positive control is
specified as a class rather than a sequence, a gapmer against an abundant housekeeping transcript;
and the scrambled control is a draw from a stated shuffling procedure rather than one oligonucleotide.
None of the three therefore has a sequence, a geometry or a screen result for these columns. Gap-paired near-matches are at the tenfold deeper alignment ceiling
where every hit list is complete, and the parent duplex is the longest contiguous run containing the
whole catalytic gap that any wild-type parent forms, whatever its length. None of these numbers is a
measurement of off-target activity, and no row is a claim of efficacy. **The duplex column is not
filtered at the criterion.** A reading of {_word(_parent_cut_bp())} base pairs or more is what
Tables 3 and 4 mark ⚑ and do not order, and no row here reaches it — the highest cell is
{t5_max_duplex} bp — so this table carries no ⚑; that is a statement about these {t5_rows} rows and
not a clearance. {_cut_caveat()} {t5_loose_reading} {_ordering_clause(mixed_geometry=True)}

{t5}

**Table 6. Where the off-target loci at the junctions with a published breakpoint are expressed.** Every gene
locus returned by the deeper screens that were READ at {n_expr_seams_txt} of the five junctions of the
38-junction panel with a published exon-resolved EMC breakpoint, over the tiling registers read at
each, against reference expression data. The four *NR4A3* exon-2 acceptor seams of §2.6 also carry a
published exon-resolved breakpoint and carry no expression reading here, so this is four of nine such
seams in the paper and not four of five. ⚠ That is not every screen at every junction: at the *EWSR1* exon-12 lead seam only the
multi-partner reagent's own screen is read, so its rows carry a denominator of one, which note ⁸ states per row. The two compartments answer different questions and are
never combined: a systemically dosed phosphorothioate gapmer is taken to distribute predominantly to
liver and kidney — a premise taken from the chemistry, for which no measurement or citation was
retrieved here — so {lo_cut_txt} are read as the exposure compartment, while the soft-tissue column is the normal
tissue of the compartment EMC arises in and stands in for a tumour no reference atlas contains.
That column is a MAXIMUM over {_word(len(_proxies))} named proxies — {_join(_proxies, "{}")} — one of
which is a cultured cell line rather than a tissue, and the tissue printed beside each value is the
one the maximum was taken at. Values are median transcripts per million (TPM) from version 8 of the Genotype-Tissue Expression project (GTEx) across each tissue's donors, in every expression column including the soft-tissue maximum. The two cuts behind the last column are
stated for legibility and are not thresholds of concern: below {lo_cut:g} TPM in all three exposure
tissues reads as below detection, at or above {hi_cut:g} TPM in any of them as the level at which an
off-target hypothesis would have to be tested. Every raw median is released so another cut can be
applied without re-running. Gap-paired hit records are the gap-paired near-matches the deeper
screens returned at that locus, one per accession per design, added up over every design tiled
across the junction; the column totals {_n_records}, which is the gap-paired hit count over the
four junctions of this table and not over the whole 38-junction panel. It is a count of what the search returned and not of how many accessions RefSeq lists for
the gene, so it is not annotation depth and not a property of the locus on its own: a locus that
every register returns at one accession is counted once per register, and a locus returned at
several accessions is counted once per accession per register — *HNRNPA2B1*'s hundred records
over two registers are fifty accessions each, which §2.8 works through. The column beside it gives how many of
those records are CURATED RefSeq transcripts rather than the computationally predicted `XM_`/`XR_`
gene models Table 3 also counts separately: {_n_curated} of the {_n_records} records in this table are
curated, and the locus contributing most of them is *{_cur_top['locus']}*, at
{_cur_top['screen_records']['n_curated_records']} of its own
{_cur_top['screen_records']['n_transcript_records']}. Both columns count records the search returned
rather than properties of the locus, so a locus is neither cleaner for having few curated records nor
dirtier for having many; what the split says is how much of a large cell rests on predicted
annotation. Tiling registers is how many of the designs
tiled across that junction return the locus, which is robustness to where the window is placed; the
two columns therefore move together rather than being independent axes, and neither is ranked on,
neither is expression and neither is affinity. A locus with no reading carries the reason rather
than a zero, because an absent reading is not a reading of absence. Every hit behind this table sits at 14 of 16 identity, the loosest the screen admits, so
nothing here distinguishes these loci from one another on affinity. None of these numbers is a
measurement of cleavage, and no expression figure is a predicted cleavage event.\n\n⁸ The denominator is how many designs at that seam THIS TABLE READS, and not how many junction-spanning registers the seam admits — {_registers} at every junction of this panel (Table 7). At the *EWSR1* exon-12 lead seam the multi-partner reagent's own screen is the only one read, so those rows carry a denominator of one; at the other seams no design is selected and every screened register is read, because a ranking is not a reagent and the union across registers is what the panel has to cover.\n\n◆ A locus returned by the design Table 2 names as the best available at that seam, which is the molecule Table 5 prices and §4 names. The unmarked rows are returned by other registers tiled across the same junction and not by that reagent. The marker identifies and does not rank: every locus keeps its row, the union is still what this table reports, and a reagent's own loci are neither cleaner nor dirtier for being its own.

{t6}

**Table 7. Gap length against junction specificity, at one junction and across the design space.** The
same junctions tiled and screened at three gapmer geometries, wing held at five nucleotides so that only
the catalytic gap changes. Inside the gap the junction-unique bases on the shorter side and the
bases one wild-type parent pairs on the longer side are complements: they sum to the gap, which the
generating module asserts for every design rather than assuming. Within one geometry the gap is
fixed, so each nucleotide of gap-level margin is one FEWER nucleotide of contiguous
wild-type-parent duplex; what raises the parent-paired run at every register is a longer gap, which
is the only way past a geometry's ceiling of half its gap rounded down. The two directions are
reported separately and never combined into a score. Near-match counts fall partly for a reason the
instrument guarantees rather than measures: at a fixed budget of two mismatches every locus a longer
design can reach is also reached by each of its own shorter sub-windows, so the set can only shrink,
and two mismatches is a fractionally stricter test at 20 nucleotides than at 16. Only the size of
the fall and which designs reach zero are measurements. The three blocks carry different
denominators and are not comparable across blocks: the junction block is one molecule, the matched-junction
block is the six junctions every geometry was screened at, and the corpus block is each geometry's
whole design space, which is not screened at the same junctions. The exhaustive GRCh38 genome scan
is unavailable at 18 and 20 nucleotides by construction, so no row reports it. Two of the corpus rows
carry a {_word(_parent_cut_bp())}-base-pair criterion and they are not the same measurement. “…and that duplex reaches {_word(_parent_cut_bp())}
base pairs” is the mature-parent screen, a search over every window of all {_word(len(_lia_parents))} parent transcripts,
and it is the row §2.5's 87 of 190 and §2.9's 87 / 88 / 87 are read from. “At the design's own seam”
is arithmetic on the junction itself: because the wing is five throughout, a parent's hybrid at that
seam is five base pairs plus its share of the gap, so pairing five nucleotides of contiguous gap DNA
and reaching a {_word(_parent_cut_bp())}-base-pair seam hybrid are the same condition and are reported as one row. The three near-match rows count what the alignment screen returned on the sense strand, which is what Tables 2 and 5 print under the same name; none of them is a count of cleavage events. ΔG°37 values are for
an unmodified DNA:RNA hybrid; the wing is five at every geometry, so LNA affinity enters each parent
duplex identically and cannot explain a difference between the columns. None of these numbers is a
measurement of cleavage. {_ordering_clause(mixed_geometry=True)}

{t7}
"""
    # ⛔ `--check` EXISTS BECAUSE THE FILE IS MARKED GENERATED AND NOTHING VERIFIED THAT.
    # `-submission-tables.md` carries a GENERATED banner telling a reader not to hand-edit it, and
    # until 2026-08-16 no gate re-derived it. So the banner was an instruction to humans backed by
    # nothing: an edit to any upstream artifact left the committed tables silently stale, and an
    # edit to the tables themselves survived every gate the repository runs. Three deposit artifacts
    # were measured stale in round 7 by exactly that route.
    # ⚠ The comparison is byte-for-byte against the committed file, and the diff is SUMMARISED
    # rather than printed in full — a check that dumps 900 lines gets skimmed, which is the failure
    # mode it exists to prevent.
    if "--check" in (argv or []):
        if not os.path.exists(OUT):
            print(f"⛔ {OUT} does not exist; run without --check to generate it", file=sys.stderr)
            return 1
        have = open(OUT, encoding="utf-8").read()
        if have == doc:
            print(f"OK {os.path.basename(OUT)} reproduces byte-for-byte")
            return 0
        import difflib
        diff = list(difflib.unified_diff(have.splitlines(), doc.splitlines(),
                                         "committed", "regenerated", lineterm="", n=1))
        changed = [ln for ln in diff if ln[:1] in "+-" and ln[:3] not in ("+++", "---")]
        print(f"⛔ {os.path.basename(OUT)} DOES NOT reproduce: {len(changed)} changed line(s). "
              "Re-run this generator and commit the result; never hand-edit the file.",
              file=sys.stderr)
        for ln in changed[:20]:
            print("   " + ln[:160], file=sys.stderr)
        if len(changed) > 20:
            print(f"   … and {len(changed) - 20} more", file=sys.stderr)
        return 1

    open(OUT, "w").write(doc)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

