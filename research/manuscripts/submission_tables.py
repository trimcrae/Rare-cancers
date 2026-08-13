#!/usr/bin/env python3
"""Generate the submission manuscript's two tables from committed artifacts.

⛔ BOTH TABLES WERE CITED BEFORE EITHER EXISTED (found 2026-08-12). The Results text referred to
"Table 1" and "Table 2" through several revisions and the manuscript contained no table at all —
the kind of gap that survives every linter here, because a cross-reference to a missing float is
neither a false claim nor a style violation, and the prose reads perfectly without it.

GENERATED, NOT TYPED, for the ordinary reason: a table is where a paper's numbers are densest, and
a hand-copied table is the most likely place in a manuscript for an artifact and its report to
diverge. Every cell below is read from `nr4a3-fusion-junction-atlas.json`,
`junction-aso-offtarget-locus-collapse.json`, `offtarget-chance-baseline.json` and the per-junction
screens; nothing is recomputed and nothing is entered by hand.

⚠ Table 2 carries the censoring and orientation caveats INSIDE the table, not only in the caption.
A table is the part of a paper most likely to be read on its own, quoted in a review, or lifted into
a slide, so a count that is an upper bound has to say so where the count is.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "modalities")
OUT = os.path.join(HERE, "aso", "fusion-junction-aso-submission-tables.md")


def _load(name):
    p = os.path.join(MOD, name)
    return json.load(open(p)) if os.path.exists(p) else None


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


def _screen(name):
    """The raw per-junction screen behind a collapse row, or None."""
    p = os.path.join(MOD, name)
    return json.load(open(p)) if os.path.exists(p) else None


def _hybridisable(oligo):
    """Retained hits that an antisense oligonucleotide could actually hybridise.

    ⛔ THIS COLUMN EXISTS BECAUSE TABLE 2 READ AS A REFUTATION OF THE PAPER'S HEADLINE. The
    near-match count reported by a screen is STRAND-BLIND — it is what the search returned, either
    strand — while the gap analysis beside it is orientation-filtered. So `GGCATATCAAGCGCTG`
    printed "2 -> 2" in a table whose caption said unmarked rows were orientation-filtered, for a
    design the Results call free of any hybridisable near-match. Both were true and the table said
    so nowhere: its two hits are both minus-strand. A reader adding a column found a contradiction
    that did not exist, which costs a paper more than an omission does.
    """
    hits = oligo.get("offtargets") or []
    return sum(1 for h in hits if not h.get("is_minus_strand"))


def _clean_designs(collapse):
    """The designs with no hybridisable near-match, over a hit list complete enough to say so.

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
    hdr = ("| 5′ partner | donor exons | exon pairs graded | frame-compatible | with ≥1 "
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


def table2(collapse, chance, atlas):
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
    gap_margin = {}
    for pan in atlas["panels"]:
        for des in pan.get("designs") or []:
            gap_margin[(pan["junction_label"], des["antisense_5to3"])] = \
                des.get("gap_specificity_margin")

    by_j, filtered = {}, {}
    for s in collapse["screens"]:
        lab = s.get("junction_label")
        if not lab:                              # the modelled reference seams carry no label
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
    hdr = ("| junction | designs screened | best gap-level margin | that design | near-matches, "
           "either strand (transcripts → loci) | of the retained hits, hybridisable² | loci with a "
           "gap-spanning hit | of those, predicted models only¹ | "
           "≤1-mismatch matches across that junction's designs, median (max) |")
    sep = "|---|---|---|---|---|---|---|---|---|"
    rows = []
    for lab in sorted(by_j):
        ol = by_j[lab]
        # ⛔ A JUNCTION WHOSE EVERY SCREEN FAILED MUST APPEAR AS FAILED, NOT CRASH AND NOT VANISH
        # (2026-08-12). EWSR1 e10 returned 0 of 5 — all five BLAST submissions failed at the remote
        # service — so its `per_oligo` list is empty and `ranked[0]` raised IndexError, which killed
        # the whole generator and silently left the PREVIOUS table on disk. Two failures in one: a
        # table that looked current and was not, and a junction that would otherwise be missing from
        # the paper with no statement that it was ever attempted. An absent reading is not a reading
        # of absence (CLAUDE.md §4), so the row is emitted saying exactly that.
        if not ol:
            rows.append(f"| {lab.replace('__', '::').replace('_', ' ')} | 0 of 5 — every BLAST "
                        f"submission failed at the remote service | — | — | — | — | — | — | — |")
            continue
        ranked = sorted(ol, key=lambda o: -(gap_margin.get((lab, o["antisense_5to3"])) or -1))
        best = ranked[0]
        gm = gap_margin.get((lab, best["antisense_5to3"]))
        # ⛔ THREE COLUMNS SHARED ONE CENSORING MARKER AND ONLY ONE OF THEM EARNED IT
        # (2026-08-12). `right_censored` means the design has more near-matches than the 15 this
        # module retains, and that bounds ONLY the locus recount, which is done from the retained
        # hits. The other two are not bounded by it: the reported near-match count is the screen's
        # complete figure and is bounded instead by BLAST's own 50-hit hitlist, and the
        # gap-spanning locus count now comes from the screen, computed over every ranked hit before
        # truncation, so it is exact. Marking an exact 0 as "≥0" is not a harmless over-caution —
        # it is unreadable, because "≥0" is true of every number and says nothing.
        cens_loci = "≥" if best["right_censored"] else ""
        cens_near = "≥" if (best["n_transcript_near_matches_reported"] or 0) >= HITLIST_SIZE else ""
        cens_gap = "" if best.get("n_loci_with_a_gap_spanning_hit_is_from_the_screen") else cens_loci
        vals = sorted(le1.get(lab, []))
        med = vals[len(vals) // 2] if vals else "—"
        mx = max(vals) if vals else "—"
        mark = "" if filtered.get(lab) else " ‡"
        # The hybridisable count is over the RETAINED hits, so on a truncated list it is a lower
        # bound and says so. "≥0" is meaningful in this one column and nowhere else in this table:
        # zero retained hybridisable hits out of a list that was cut short is exactly the state
        # that stops a design being called clean, and printing a bare 0 there would assert the
        # opposite of what the screen knows.
        hyb = hyb_by_j.get(lab, {}).get(best["antisense_5to3"])
        hyb_cell = "—" if hyb is None else f"{'≥' if best['right_censored'] else ''}{hyb}"
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
            f"{med} ({mx}) |")
    return "\n".join([hdr, sep] + rows), any(not v for v in filtered.values())


#: The rule audit's field names are code identifiers; a manuscript table needs the rule, not the key.
_RULE_LABELS = {
    "gc_in_band": "GC outside 40–60%",
    "no_g_quadruplex_motif": "G-quadruplex motif",
    "no_run_of_four": "homopolymer run of four",
    "no_cpg": "contains a CpG",
}


def table3(collapse, chance, thermo, graded):
    """The designs the paper's headline rests on, one row each.

    ⛔ WHY THIS TABLE WAS MISSING AND WHY THAT MATTERED. The headline result — nine designs with no
    hybridisable near-match — had no table, and Table 2's convention is the highest-gap-level-margin
    design per junction, which is a different selection: only four of the nine appear there, and
    Table 2's six zero-gap-spanning junctions are not the same six. So a reader sent to a table to
    check the central claim could not find five of the molecules it is about, and would find two
    junctions (FUS e8, TCF12 e9) whose Table 2 row shows a gap-spanning locus for a DIFFERENT
    design at the same seam. Prose naming nine sequences is not a substitute for a table.
    """
    ddg = {r["antisense_5to3"]: r for r in thermo["per_design"]}
    le1 = {}
    for r in chance["per_design"]:
        le1.setdefault(r["antisense_5to3"], (r.get("offtarget_exact"), r.get("offtarget_le1mm")))
    hdr = ("| design | junction | GC (%) | gap-level margin | ΔΔG°37 (kcal/mol) | near-matches, "
           "either strand | of those, hybridisable | exact / ≤1-mismatch matches | residual "
           "cleavage load, both bounds³ | conventional rules failed⁴ |")
    sep = "|---|---|---|---|---|---|---|---|---|---|"
    rows = []
    for lab, o in _clean_designs(collapse):
        seq = o["antisense_5to3"]
        t = ddg.get(seq) or {}
        ex, l1 = le1.get(seq, ("—", "—"))
        load = graded.get((lab, seq))
        failed = [_RULE_LABELS.get(k, k)
                  for k, v in (t.get("design_rules") or {}).items() if v is False]
        rows.append(
            f"| 5′-{seq}-3′ | {lab.replace('__', '::').replace('_', ' ')} | "
            f"{o.get('gc_percent')} | {t.get('gap_specificity_margin', '—')} | "
            f"{t.get('ddg37_discrimination', '—')} | {o.get('n_offtarget_near_matches')} | "
            f"{_hybridisable(o)} | {ex} / {l1} | "
            f"{'—' if load is None else load} | "
            f"{', '.join(failed) if failed else 'none'} |")
    return "\n".join([hdr, sep] + rows), len(rows), len({lab for lab, _ in _clean_designs(collapse)})


def _graded_loads():
    """Residual cleavage load per (junction, design) under both literature bounds.

    Printed as one cell because for every design here the two bounds agree, and a reader is owed
    the fact that the OPTIMISTIC and the PESSIMISTIC model return the same number rather than being
    left to assume the paper quoted whichever was kinder.
    """
    out = {}
    for name in sorted(os.listdir(os.path.abspath(MOD))):
        if not (name.startswith("junction-aso-offtarget-") and name.endswith("-graded.json")):
            continue
        d = _load(name) or {}
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

    ⛔ THIS WAS A HARDCODED "47%" IN THIS FILE'S TABLE 2 LEGEND, and it stayed 47% while the corpus
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


def main():
    atlas = _load("nr4a3-fusion-junction-atlas.json")
    collapse = _load("junction-aso-offtarget-locus-collapse.json")
    chance = _load("offtarget-chance-baseline.json")
    thermo = _load("junction-aso-thermo.json")
    if not (atlas and collapse and chance and thermo):
        print("a required artifact is missing", file=sys.stderr)
        return 2

    t2, any_unfiltered = table2(collapse, chance, atlas)
    t3, n_clean, n_clean_junctions = table3(collapse, chance, thermo, _graded_loads())
    pct, minus, tot = _minus_strand_share(collapse)

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

    doc = f"""<!-- GENERATED — DO NOT EDIT. Regenerate: python3 research/manuscripts/submission_tables.py -->

# Tables — fusion-junction ASO submission

**Table 1. The frame-compatible junction space across five *NR4A3* fusion partners.** Every
donor-exon × *NR4A3*-acceptor-exon pair was graded against the frame condition before any design was
emitted. The gap-level margin is the number of junction-unique bases inside the six-nucleotide
catalytic gap on the shorter side of the seam. Frame compatibility is an arithmetic property of exon
structure and is not a claim about which junctions patients carry.

{table1(atlas)}

**Table 2. Predicted specificity per screened junction.** One row per junction; figures are for the
design with the highest gap-level margin at that junction, which is the ranking the Methods define,
and NOT for that junction's cleanest design — the two are often different molecules, and the
cleanest ones are in Table 3. Near-match counts are of RefSeq
transcript accessions and are also given collapsed to distinct gene loci, since RefSeq carries one
accession per annotated variant. A “≥” marks a right-censored count: the screens store the top
{SAVED_HITS} hits per design, so a design with more is a lower bound. All {sum(1 for s in collapse["screens"] if s.get("junction_label"))} junction screens
are filtered by alignment orientation. `XM_`/`XR_` records are computationally
predicted gene models rather than curated transcripts, and are counted separately for that reason.
None of these numbers is a measurement of off-target activity.\n\n¹ Counted over the gap-spanning loci only, not over all of that design's near-match loci.\n\n² A near-match count is what the search returned on EITHER strand; a match on the strand opposite the target window cannot be hybridised by an antisense oligonucleotide and is not a liability. Across this corpus {pct}% of apparent gap-spanning hits ({minus} of {tot:,}) are of that kind, which is why the two columns differ and why the raw count alone should not be read as load. This column counts only the {SAVED_HITS} RETAINED hits, whereas the gap-spanning locus column is computed over every ranked hit before truncation and is therefore exact. The two are not in conflict where a truncated design shows “≥0” hybridisable and a non-zero gap-spanning locus count: the hybridisable hits are real and simply fall outside the stored window, which is precisely why such a design cannot be called clean.{dagger}

{t2}

**Table 3. The {n_clean} designs with no hybridisable near-match.** Every design at the {n_clean_junctions} junctions
where one exists, which is the set the Results' cleanliness claim is about. A design qualifies only
if its retained hit list is not truncated — no more near-matches than the {SAVED_HITS} the screens store — because the
strand of an unstored hit cannot be recovered, so a truncated list cannot establish that nothing
hybridisable remains. The underlying search is itself capped, so these are the designs whose
near-match lists are shortest, not the designs whose lists are known to be exhaustive. ΔΔG°37 is the margin by which the fusion duplex is favoured over the best
duplex either parent can form, for an unmodified DNA:RNA hybrid; because the fusion duplex pairs
both LNA wings and each parent duplex only one, it is a lower bound on the modified
oligonucleotide's discrimination rather than an upper one. None of these numbers is a measurement of off-target
activity, and none speaks to cleavage.\n\n³ Under the optimistic five-fold and the pessimistic
no-discrimination bound on RNase-H1 single-mismatch discrimination. A single value means the two
bounds agree.\n\n⁴ Of four conventional antisense design rules: GC within 40–60%, no G-quadruplex
motif, no homopolymer run of four, no CpG dinucleotide.

{t3}
"""
    open(OUT, "w").write(doc)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
