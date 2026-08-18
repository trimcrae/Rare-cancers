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
    return (f"{opener}; the bases alone, ordered as unmodified DNA, are a different molecule. "
            f"The canonical machine-readable copy of every sequence is "
            f"`{os.path.basename(_manifest.OUT_CSV)}`.")


def _load(name):
    p = os.path.join(MOD, name)
    return json.load(open(p)) if os.path.exists(p) else None


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
    showed `0 on the sense strand, 0 gap-spanning loci` for designs carrying 14, 29 and 30 hybridisable
    hits at ten times the ceiling, and every one of Table 4's nine rows printed a zero that §3.10
    withdraws for six of them. The captions said so in prose. **A caption is not where a reader
    checks a number** — the cell is, and a cell that reads clean beside a text that calls the
    design dirty reads as the text being wrong. `GGGCATATCTCTATAA` was the sharpest case: named in
    §4 as withdrawn with 14 gap-spanning risks, and shown in Table 3 with none.

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

    # ⚠ THE COLUMN NAMES ARE THE THIRD THING THIS TABLE GOT WRONG. A column headed "gap-spanning
    # near-matches" was filled with the design's TOTAL near-match count, which is larger — the lead
    # candidate reads 9 there and has 8 gap-spanning. Total near-matches and gap-spanning
    # near-matches are both worth printing and are printed separately; the collapse artifact stores
    # gap-spanning resolved to LOCI but not to transcripts, so that is the column that exists.
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
           "either strand (transcripts → loci) | of the retained hits, on the sense strand¹ | loci with a "
           "gap-spanning hit | of those, predicted models only² | "
           "at the deeper ceiling: near-matches³ | of those, on the sense strand³ | "
           "loci with a gap-spanning hit³ | "
           "≤1-mismatch matches across that junction's designs, median (max) |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|"
    rows = []
    for lab in sorted(by_j):
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
                        f"— | — | — |")
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
        # gap-spanning locus count now comes from the screen, computed over every ranked hit before
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
        cens_gap = "≤" if best.get("n_loci_with_a_gap_spanning_hit_is_from_the_screen") else ""
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
            f"{deep_cell} | {med} ({mx}) |")
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

    def _duplex(bp, gene):
        #: ⚠ `0 bp`, NOT `none` (2026-08-17). This column and Table 7's "mature-parent duplex
        #: through the whole gap (bp)" are the same measurement on the same molecules, and for the
        #: 5-8-5 control they printed "none" here and "0" there — one value, two renderings, in
        #: adjacent display items. `none` is also the weaker of the two words in a paper that
        #: insists an absent reading is not a reading of absence: this IS a reading, the search ran
        #: over all six parent transcripts and returned nothing, and a numeral says so where a word
        #: leaves room for "not screened".
        if not bp:
            return "0 bp"
        return f"{bp} bp (*{gene}*)" if gene else f"{bp} bp"

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
        return (f"| coverage bound | {rung['panel']} | {seq} | — | — | — | — | "
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
        rows.append(f"| {role} | {lab} | 5′-{seq}-3′ | {arch} | {margin} | {load} | "
                    f"{dup} | {cov} | {basis} |")
    for _, rung in pending:                     # a ladder that ends above every named reagent
        rows.append(_bound_row(rung))
    hdr = ("| reagent | junction | sequence | geometry | gap-level margin | gap-paired near-matches "
           "→ loci at the deeper ceiling | longest mature-parent duplex through the gap | "
           "cumulative coverage | basis |")
    return "\n".join([hdr, "|---|---|---|---|---|---|---|---|---|"] + rows), ladder_backed_noncoding


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

    hdr = ("| junction | exon-resolved breakpoint | designs clearing the parent screen | best "
           "available design | gap-level margin | longest parent duplex through the gap (bp) | "
           "gap-paired near-matches at the deeper ceiling (transcripts → loci) | genome-wide "
           "gap-paired load, observed/expected | conventional rules failed |")
    sep = "|---|---|---|---|---|---|---|---|---|"
    rows = []
    for j in per_junction["junctions"]:
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
        row("sense-strand gap-spanning cleavage risks",
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
        row("median gap-spanning cleavage risks",
            lambda d: f"{d['hybridisable_gap_spanning_risks']['median']:g}", matched),
        row("designs carrying none",
            lambda d: f"{d['n_with_zero_hybridisable_gap_spanning_risk']} of "
                      f"{d['n_designs_with_alignment_counts']}", matched),
        row("most risk loci on any one design",
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
        row("…and that duplex reaches ten base pairs, the criterion applied throughout",
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
            soft = f"{hi:.1f} ({tu['max_tissue_in_block']})"
        else:
            soft = "—"
        reading = _EXPOSURE_READING.get(L["tier"], L["tier"])
        mark = " ◆" if L["locus"] in mine.get(junction, ()) else ""
        rows.append(f"| {lab} | *{L['locus']}*{mark} | "
                    f"{L['screen_records']['n_transcript_records']} | "
                    f"{L['n_designs_hitting_it']} of {n_des.get(junction, '?')} | "
                    + " | ".join(cells) + f" | {soft} | {reading} |")
    # ⚠ THE ◆ IS EXPLAINED BY A SYMBOL-KEYED NOTE, NOT BY A SUPERSCRIPT ON THIS HEADER. The header's
    # opening is the anchor `test_table6_record_column_is_named_for_what_the_generator_counts` finds
    # this table by, and a marker inside it would break that guard while changing nothing a reader
    # sees. The symbol lives in the cells it marks, which is where a reader meets it.
    hdr = ("| junction | gene locus | gap-paired hit records | tiling registers returning it⁷ | "
           + " | ".join(tiss) + " | soft-tissue proxy maximum | exposure-organ reading |")
    sep = "|---|---|---|---|" + "---|" * (len(tiss) + 2)
    return "\n".join([hdr, sep] + rows)


def table4(collapse, chance, thermo, graded):
    """The designs the paper's headline rests on, one row each.

    ⛔ WHY THIS TABLE WAS MISSING AND WHY THAT MATTERED. The headline result — nine designs with no
    sense-strand near-match — had no table, and Table 3's convention is the highest-gap-level-margin
    design per junction, which is a different selection: only four of the nine appear there, and
    Table 3's six zero-gap-spanning junctions are not the same six. So a reader sent to a table to
    check the central claim could not find five of the molecules it is about, and would find two
    junctions (FUS e8, TCF12 e9) whose Table 3 row shows a gap-spanning locus for a DIFFERENT
    design at the same junction. Prose naming nine sequences is not a substitute for a table.
    """
    ddg = {r["antisense_5to3"]: r for r in thermo["per_design"]}
    le1 = {}
    for r in chance["per_design"]:
        le1.setdefault(r["antisense_5to3"], (r.get("offtarget_exact"), r.get("offtarget_le1mm")))
    deep = _deep_lookup()
    hdr = ("| design | junction | GC (%) | gap-level margin | ΔΔG°37 (kcal/mol) | near-matches, "
           "either strand | of those, on the sense strand | exact / ≤1-mismatch matches | residual "
           # ⛔ CONTINUES TABLE 3's RUN. Markers are unique across the file so a lifted table cannot
           # collide with its neighbour's notes, and each table's own set is contiguous — see the
           # note on Table 3's header, which used to leave ³ and ⁴ dangling inside Table 3.
           "cleavage load, both bounds⁴ | conventional rules failed⁵ | "
           "at the deeper ceiling: near-matches | of those, on the sense strand | "
           "loci with a gap-spanning hit | survives⁶ |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
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
            f"{', '.join(failed) if failed else 'none'} | {deep_cell} | {verdict} |")
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
    """The share of apparent gap-spanning hits that lie on the minus strand, across the corpus.

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

    def _join(names, fmt="*{}*"):
        """A derived list of gene or junction names, rendered for a sentence rather than typed."""
        xs = [fmt.format(n) for n in names]
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]

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
              "gap-spanning hits. Its numbers are upper bounds and are NOT comparable with the "
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
                 "parent screen” cell reads 0. Do not order the sequence in a marked row.")

    doc = f"""<!-- GENERATED — DO NOT EDIT. Regenerate: python3 research/manuscripts/submission_tables.py -->

# Tables — fusion-junction ASO submission

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

**Table 1. The in-frame junction space across five *NR4A3* fusion partners.** Every
donor-exon × *NR4A3*-acceptor-exon pair was graded against the frame condition before any design was
emitted. The gap-level margin is the number of junction-unique bases inside the six-nucleotide
catalytic gap on the shorter side of the junction. Frame compatibility is an arithmetic property of exon
structure and is not a claim about which junctions patients carry.

{t1}

**Table 2. The best available design at each of the {per_junction["n_junctions"]} in-frame junctions.** Tables 3 and 4
select across the panel; this table selects within each junction, which is the question a patient's
fusion poses. Designs are ranked by parent liability first, since sparing the wild-type parents is
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
near-matches are at the tenfold deeper alignment ceiling, where every hit list is complete. The
genome column is the observed number of gap-paired sites at ≤2 mismatches over the number expected
for an arbitrary 16-mer, so 1.00 is chance. A junction with no design clearing the parent screen is
reported as such rather than given a best row, and Table 3 marks those junctions too, since Table 3
ranks by margin instead and does print a sequence at each of them. The last column is a conventional
design audit, computed for whichever design this table names from the same artifact and by the same
code Table 4 uses. {_rule_audit_note()} It is reported beside the ranking and is never folded
into it: the two orderings select different molecules, which is the disagreement §2.10 is about, and
this is the table one reagent is chosen from. A design the audit does not cover would read “not
audited” rather than blank, since a blank in a rules column reads as breaking none. {_ordering_clause()}

{t2}

**Table 3. Predicted specificity per screened junction.** One row per junction; figures are for the
design with the highest gap-level margin at that junction, which is the ranking the Methods define,
and NOT for that junction's cleanest design — the two are often different molecules, and the
cleanest ones are in Table 4. The margin column is therefore the best among the designs that
RETURNED a screen at this depth: {n_failed} of the panel's {n_attempted} default-depth submissions
failed at the remote service, which is why a junction can show fewer than {_word(_registers)} designs screened
here{margin_up_txt}.{margin_both} Near-match counts are of RefSeq
transcript accessions and are also given collapsed to distinct gene loci, since RefSeq carries one
accession per annotated variant. A “≥” marks a right-censored count, and the two columns are
censored by DIFFERENT caps, which is why an uncensored transcript count here can exceed the retained
{SAVED_HITS}: the alignment screen itself returns at most 50 hits per query, so a transcript count at
50 is a lower bound, while the locus column is recounted from the {SAVED_HITS} hits the screens
RETAIN, so a locus count from a design with more than {SAVED_HITS} hits is a lower bound too. All {sum(1 for s in collapse["screens"] if s.get("junction_label"))} junction screens
are filtered by alignment orientation. `XM_`/`XR_` records are computationally
predicted gene models rather than curated transcripts, and are counted separately for that reason.
None of these numbers is a measurement of off-target activity.\n\n¹ A near-match count is what the search returned on EITHER strand; a match on the strand opposite the target window cannot be hybridised by an antisense oligonucleotide and is not a liability. Across this corpus {pct}% of apparent gap-spanning hits ({minus} of {tot:,}) are of that kind, which is why the two columns differ and why the raw count alone should not be read as load. This column counts only the {SAVED_HITS} RETAINED hits. The gap-spanning locus column is recounted from those hits wherever they are the complete list, and is exact there; a “≤” marks a truncated design, where the column instead carries the screen's own count over every ranked hit, computed under a locus assignment since corrected that split some genes across accessions and therefore over-counts. The two columns are not in conflict where a truncated design shows “≥0” sense-strand hits and a non-zero gap-spanning locus count: the sense-strand hits are real and simply fall outside the stored window, which is precisely why such a design cannot be called clean.\n\n² Counted over the gap-spanning loci only, not over all of that design's near-match loci.\n\n³ The same design re-screened at a tenfold deeper alignment ceiling, with retention raised to match it so that no hit list is truncated. Because no list is truncated, the gap-spanning locus column at this depth is recounted from the complete stored hits under the current locus assignment and is exact; it is not the screen's own stored figure, which was computed before that assignment was corrected and splits any gene whose description carries a comma across one accession per transcript variant. It is therefore the same quantity, counted the same way, as the locus figures in Table 2 and in the Results. The three columns are the counterparts of the default-depth columns to their left, given beside them rather than in place of them because the default depth is where the corpus-wide counts elsewhere in the paper were computed and the two must stay comparable. Read together they are the paper's censoring result at the level of a single row: a default-depth count is a lower bound whether or not it reached the 50-hit cap, and three junctions whose default cell reads zero in the gap-spanning column carry gap-spanning hits at ten times the depth. Three of the panel's 190 records failed at this ceiling; they are absent from the deep set rather than counted as zero in it.{no_deep} {_ordering_clause()}{no_parent}{dagger}

{t3}

**Table 4. The {n_clean} designs with no sense-strand near-match at the default search depth.** Six of
these lose the property when the same junctions are re-screened at a tenfold deeper alignment
ceiling, three of them having returned no near-match at all here; §2.4 reports that
measurement and names the three that survive it. This table is the default-depth result, retained
because it is the depth at which the corpus-wide counts elsewhere in the paper were computed. Every
design that QUALIFIES is listed, at each of the {n_clean_junctions} junctions where one does; this
is not one row per junction, and it is not every design at those junctions, which are tiled by
{_word(_registers)} registers each. A design qualifies only
if its retained hit list is not truncated — no more near-matches than the {SAVED_HITS} the screens store — because the
strand of an unstored hit cannot be recovered, so a truncated list cannot establish that nothing
on the sense strand remains. The underlying search is itself capped, so these are the designs whose
near-match lists are shortest, not the designs whose lists are known to be exhaustive. ΔΔG°37 is the margin by which the fusion duplex is favoured over the best
duplex either parent can form, for an unmodified DNA:RNA hybrid; because the fusion duplex pairs
both LNA wings and each parent duplex only one, it is a lower bound on the modified
oligonucleotide's discrimination rather than an upper one. None of these numbers is a measurement of off-target
activity, and none speaks to cleavage. {_ordering_clause()}\n\n⁴ Under the optimistic five-fold and the pessimistic
no-discrimination bound on RNase-H1 single-mismatch discrimination. A single value means the two
bounds agree.\n\n⁵ {_rule_audit_note()}\n\n⁶ Whether the design still carries no
sense-strand near-match once its junction is re-screened at the tenfold deeper ceiling. The verdict
is computed from the three deep columns beside it, not asserted, so this table cannot come to
disagree with §2.4 about which designs survive. The six that do not are the reason this table's
default-depth zeros must not be read on their own.

{t4}

**Table 5. Every seam the coverage ladder qualifies, with the ladder's bounds and §4's two contrast
arms beside them, what each costs on each screen and what each buys in coverage.** The rows are in the order §4 decides them:
the two lead reagents, the rungs of the coverage ladder above them, the bounds above those, the
remaining junction with a published exon-resolved breakpoint and a reagent through all five deep
screens, the {n_beside_txt} *NR4A3* exon-2 acceptor seams the ladder carries no entry for, reported
beside the panel, and the two contrast arms. Membership is the coverage ladder's and not this table's: every junction its best-supported
buildable panel qualifies — a published exon-resolved breakpoint, and all five specificity screens
run to completion over that junction's designs, each condition read from the table that owns it —
has a row here whether or not §4 names its reagent, and the generator refuses to build if a
qualifying junction has no row. A row can therefore qualify and still buy no coverage,
which is a statement about the denominator and not about the reagent.{premrna_caveat}{exon2_rung} Cumulative coverage is the
coverage of the reagent set through that row, so the two leads are
one rung and carry one figure between them; it is discounted by the breakpoint distribution of a
single series and is not a partner figure, and its interval is composed from each breakpoint
fraction's own Wilson bound rather than from the point estimate. Every rung and every bound prints
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
whole catalytic gap, at the ten-base-pair criterion applied throughout. None of these numbers is a
measurement of off-target activity, and no row is a claim of efficacy. {_ordering_clause(mixed_geometry=True)}

{t5}

**Table 6. Where the off-target loci at the junctions with a published breakpoint are expressed.** Every gene
locus returned by the deeper screens that were READ at {n_expr_seams_txt} of the five junctions with a
published exon-resolved EMC breakpoint, over the tiling registers read at each, against reference
expression data. ⚠ That is not every screen at every junction: at the lead seam only the
multi-partner reagent's own screen is read, so its rows carry a denominator of one, which note ⁷ states per row. The two compartments answer different questions and are
never combined: a systemically dosed phosphorothioate gapmer is taken to distribute predominantly to
liver and kidney — a premise taken from the chemistry, for which no measurement or citation was
retrieved here — so {lo_cut_txt} are read as the exposure compartment, while the soft-tissue column is the normal
tissue of the compartment EMC arises in and stands in for a tumour no reference atlas contains.
Values are median transcripts per million (TPM) from version 8 of the Genotype-Tissue Expression project (GTEx) across each tissue's donors. The two cuts behind the last column are
stated for legibility and are not thresholds of concern: below {lo_cut:g} TPM in all three exposure
tissues reads as below detection, at or above {hi_cut:g} TPM in any of them as the level at which an
off-target hypothesis would have to be tested. Every raw median is released so another cut can be
applied without re-running. Gap-paired hit records are the gap-paired near-matches the deeper
screens returned at that locus, one per accession per design, added up over every design tiled
across the junction; the column totals {_n_records}, which is the gap-paired hit count over the
four junctions of this table and not over the whole 38-junction panel. It is a count of what the search returned and not of how many accessions RefSeq lists for
the gene, so it is not annotation depth and not a property of the locus on its own: a locus that
every register returns is counted once per register. Tiling registers is how many of the designs
tiled across that junction return the locus, which is robustness to where the window is placed; the
two columns therefore move together rather than being independent axes, and neither is ranked on,
neither is expression and neither is affinity. A locus with no reading carries the reason rather
than a zero, because an absent reading is not a reading of absence. Every hit behind this table sits at 14 of 16 identity, the loosest the screen admits, so
nothing here distinguishes these loci from one another on affinity. None of these numbers is a
measurement of cleavage, and no expression figure is a predicted cleavage event.\n\n⁷ The denominator is how many designs at that seam THIS TABLE READS, and not how many junction-spanning registers the seam admits — {_registers} at every junction of this panel (Table 7). At the lead seam the multi-partner reagent's own screen is the only one read, so those rows carry a denominator of one; at the other seams no design is selected and every screened register is read, because a ranking is not a reagent and the union across registers is what the panel has to cover.\n\n◆ A locus returned by the design Table 2 names as the best available at that seam, which is the molecule Table 5 prices and §4 names. The unmarked rows are returned by other registers tiled across the same junction and not by that reagent. The marker identifies and does not rank: every locus keeps its row, the union is still what this table reports, and a reagent's own loci are neither cleaner nor dirtier for being its own.

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
carry a ten-base-pair criterion and they are not the same measurement. “…and that duplex reaches ten
base pairs” is the mature-parent screen, a search over every window of all six parent transcripts,
and it is the row §2.5's 87 of 190 and §2.9's 87 / 88 / 87 are read from. “At the design's own seam”
is arithmetic on the junction itself: because the wing is five throughout, a parent's hybrid at that
seam is five base pairs plus its share of the gap, so pairing five nucleotides of contiguous gap DNA
and reaching a ten-base-pair seam hybrid are the same condition and are reported as one row. ΔG°37 values are for
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
