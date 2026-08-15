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

sys.path.insert(0, os.path.abspath(MOD))
import aso_screen_sets as ass                                            # noqa: E402

#: The geometry Tables 2 to 4 are about — the panel the manuscript reports. ⚠ TABLE 5 IS THE
#: EXCEPTION AND IS SUPPOSED TO BE: it is the gap-length trade, one column per geometry, and it
#: reads `aso-gap-length-tradeoff.json`, which is the artifact that owns the cross-geometry
#: comparison. A per-geometry TABLE built from a per-geometry ARTIFACT is not pooling.
GEOMETRY = ass.MANUSCRIPT_GEOMETRY


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
    design the Results call free of any sense-strand near-match. Both were true and the table said
    so nowhere: its two hits are both minus-strand. A reader adding a column found a contradiction
    that did not exist, which costs a paper more than an omission does.
    """
    hits = oligo.get("offtargets") or []
    return sum(1 for h in hits if not h.get("is_minus_strand"))


def _deep_lookup():
    """Every 16-mer design's deep-ceiling counts, keyed `(junction_label, sequence)`.

    ⛔ WHY TABLES 2 AND 3 NEEDED THIS COLUMN (round-3 review, 2026-08-14). Both tables are the
    DEFAULT-depth result, and the Results withdraw part of what they print: three Table 2 rows
    showed `0 on the sense strand, 0 gap-spanning loci` for designs carrying 14, 29 and 30 hybridisable
    hits at ten times the ceiling, and every one of Table 3's nine rows printed a zero that §3.10
    withdraws for six of them. The captions said so in prose. **A caption is not where a reader
    checks a number** — the cell is, and a cell that reads clean beside a text that calls the
    design dirty reads as the text being wrong. `GGGCATATCTCTATAA` was the sharpest case: named in
    §4 as withdrawn with 14 gap-spanning risks, and shown in Table 2 with none.

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
    EVERY cell of Table 3's design rows, not just the residual-load one, because the defect it was
    written for (`31.4 / 101 / 0 / 0`, a default-depth re-score pooled with a deep one) hid inside a
    cell shape that looks legitimate: `a / b` is the model-disagreement form and is fine, so a
    reader cannot tell a pooled cell from a real one by looking. Narrowing the guard to one column
    would have made this pass and would have re-opened the hole. The separator is the problem, so
    the separator is what changed.
    """
    out = {}
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
            out[(lab, o["antisense_5to3"])] = {
                "n": o.get("n_offtarget_near_matches"),
                "hyb": _hybridisable(o),
                "gap_loci": o.get("n_loci_with_a_gap_spanning_hit"),
            }
    return out


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
    hdr = ("| junction | designs screened | best gap-level margin | that design | near-matches, "
           "either strand (transcripts → loci) | of the retained hits, on the sense strand² | loci with a "
           "gap-spanning hit | of those, predicted models only¹ | "
           "at the deeper ceiling: near-matches⁵ | of those, on the sense strand⁵ | "
           "loci with a gap-spanning hit⁵ | "
           "≤1-mismatch matches across that junction's designs, median (max) |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|"
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
                        f"submission failed at the remote service | — | — | — | — | — | — | — | "
                        f"— | — | — |")
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
        mark = "" if filtered.get(lab) else " ‡"
        # The hybridisable count is over the RETAINED hits, so on a truncated list it is a lower
        # bound and says so. "≥0" is meaningful in this one column and nowhere else in this table:
        # zero retained sense-strand hits out of a list that was cut short is exactly the state
        # that stops a design being called clean, and printing a bare 0 there would assert the
        # opposite of what the screen knows.
        hyb = hyb_by_j.get(lab, {}).get(best["antisense_5to3"])
        hyb_cell = "—" if hyb is None else f"{'≥' if best['right_censored'] else ''}{hyb}"
        # ⚠ "—" HERE MEANS THE DEEP RE-SCREEN HAS NO READING FOR THIS DESIGN, NOT THAT IT FOUND
        # NOTHING. Three of the 190 records failed at the deeper ceiling; rendering that as 0 would
        # be the flattering direction and the one this table has gone wrong in twice before.
        d = deep.get((lab, best["antisense_5to3"]))
        deep_cell = "— | — | —" if d is None else f"{d['n']} | {d['hyb']} | {d['gap_loci']}"
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
    return "\n".join([hdr, sep] + rows), any(not v for v in filtered.values())


#: Clinical-occurrence tiers, rendered for a reader. The tier vocabulary is owned by
#: `aso_per_junction_table.PUBLISHED_BREAKPOINTS`; this only names the three states.
_TIER_LABELS = {
    "published_exon_resolved_breakpoint": "published",
    "partner_published_this_exon_not_reported": "exon not reported",
    "no_published_exon_resolved_breakpoint": "none published",
}


def table4(per_junction):
    """One best-available reagent per junction, joined across all five screens.

    ⛔ WHY A FOURTH TABLE. Tables 2 and 3 both answer panel-level questions — the representative
    design at each junction, and the panel's cleanest molecules. Neither answers the question a
    reader with a patient has, which is what to order for ONE fusion at ONE exon pair. That was in
    the prose for the junctions the paper discusses and nowhere for the other thirty.

    ⚠ RANKED, NOT SCORED, and the ordering is the artifact's: parent liability disqualifies, then
    pre-mRNA, then gene loci, with ties broken on gap-level margin rather than on raw hits. The two
    axes are printed side by side and never combined.
    """
    hdr = ("| junction | exon-resolved breakpoint | designs clearing the parent screen | best "
           "available design | gap-level margin | longest parent duplex through the gap (bp) | "
           "gap-paired near-matches at the deeper ceiling (transcripts → loci) | genome-wide "
           "gap-paired load, observed/expected |")
    sep = "|---|---|---|---|---|---|---|---|"
    rows = []
    for j in per_junction["junctions"]:
        lab = j["junction_label"].replace("__", "::").replace("_", " ")
        tier = _TIER_LABELS.get(j["clinical_tier"], j["clinical_tier"])
        b = j["best_available"]
        n = f"{j['n_designs_clearing_the_parent_screen']} of {j['n_designs_screened']}"
        if b is None:
            rows.append(f"| {lab} | {tier} | {n} | — | — | — | — | — |")
            continue
        oe = b["genome_oe_gap_paired_le2"]
        rows.append(
            f"| {lab} | {tier} | {n} | 5′-{b['antisense_5to3']}-3′ | "
            f"{b['gap_specificity_margin']} | {b['parent_duplex_bp']} | "
            f"{b['n_gap_paired']} → {b['n_gap_paired_loci']} | "
            f"{'—' if oe is None else f'{oe:.2f}'} |")
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
        raise SystemExit("Table 5: the trade-off artifact reports no present geometry")
    return tuple(g["architecture"] for g in sorted(present, key=lambda g: g["gap_nt"]))


def table5(gap):
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
                    f"Table 5: geometry {arch} is present in the trade-off artifact but has no "
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
                f"Table 5: at {arch} the ten-base-pair duplex count "
                f"({g['n_whose_seam_hybrid_reaches_min_duplex_bp']}) and the ≥5 nt DNA count "
                f"({ge5}, wing {g['wing']}) are no longer the same condition; split the row")

    def row(label, fn, src):
        return f"| {label} | " + " | ".join(str(fn(src[g])) for g in columns) + " |"

    def parent_duplex(d):
        bp = d["mature_parent_duplex_through_whole_gap_bp"]
        return f"{bp} (*{d['mature_parent_duplex_gene']}*)" if bp else "0"

    rows = [
        "| **At the *EWSR1* e12 / *TAF15* e11 / *FUS* e10 junction** | | | |",
        row("design (5′→3′)", lambda d: d["antisense_5to3"], lead),
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
        # ⚠ ONE ROW, NOT TWO, BECAUSE THESE ARE THE SAME CONDITION AND PRINTING BOTH READS AS A
        # COPY-PASTE FAULT. The parent's junction hybrid is the wing plus its share of the gap, and the
        # wing is five at every geometry compared, so "hybrid reaches ten base pairs" and "the DNA
        # run reaches five nucleotides" are the same inequality. Asserted below rather than trusted.
        row("parent pairs ≥5 nt of contiguous gap DNA, a ten-base-pair hybrid",
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
_RULE_LABELS = {
    "gc_in_band": "GC outside 40–60%",
    "no_g_quadruplex_motif": "G-quadruplex motif",
    "no_run_of_four": "homopolymer run of four",
    "no_cpg": "contains a CpG",
}


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


def table6(expr):
    """Where each off-target locus of the two clinically-relevant reagents is expressed.

    ⛔ TWO COMPARTMENTS, NEVER ONE COLUMN. The organs a systemically dosed gapmer distributes to and
    the compartment the tumour sits in are different questions, and a table that merged them — or
    that ranked loci on either — would be inventing the join this work does not make. They are
    printed side by side and never combined, exactly as Table 5 keeps the two directions of the
    gap-length trade apart.

    ⛔ NO RISK COLUMN, AND NO ORDERING BY EXPRESSION. Rows are grouped by junction and then by transcript
    record count, which is annotation depth. Every hit behind this table is at the screen's loosest
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
    per = sorted(expr["per_locus"],
                 key=lambda L: (order.get(L["seams"][0], 99),
                                -L["screen_records"]["n_transcript_records"], L["locus"]))
    for L in per:
        junction = L["seams"][0]
        lab = "" if junction in seen else junction.replace("__", "::").replace("_", " ")
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
        rows.append(f"| {lab} | *{L['locus']}* | "
                    f"{L['screen_records']['n_transcript_records']} | "
                    f"{L['n_designs_hitting_it']} of {n_des.get(junction, '?')} | "
                    + " | ".join(cells) + f" | {soft} | {reading} |")
    hdr = ("| junction | gene locus | transcript records | tiling registers returning it | "
           + " | ".join(tiss) + " | soft-tissue proxy maximum | exposure-organ reading |")
    sep = "|---|---|---|---|" + "---|" * (len(tiss) + 2)
    return "\n".join([hdr, sep] + rows)


def table3(collapse, chance, thermo, graded):
    """The designs the paper's headline rests on, one row each.

    ⛔ WHY THIS TABLE WAS MISSING AND WHY THAT MATTERED. The headline result — nine designs with no
    sense-strand near-match — had no table, and Table 2's convention is the highest-gap-level-margin
    design per junction, which is a different selection: only four of the nine appear there, and
    Table 2's six zero-gap-spanning junctions are not the same six. So a reader sent to a table to
    check the central claim could not find five of the molecules it is about, and would find two
    junctions (FUS e8, TCF12 e9) whose Table 2 row shows a gap-spanning locus for a DIFFERENT
    design at the same junction. Prose naming nine sequences is not a substitute for a table.
    """
    ddg = {r["antisense_5to3"]: r for r in thermo["per_design"]}
    le1 = {}
    for r in chance["per_design"]:
        le1.setdefault(r["antisense_5to3"], (r.get("offtarget_exact"), r.get("offtarget_le1mm")))
    deep = _deep_lookup()
    hdr = ("| design | junction | GC (%) | gap-level margin | ΔΔG°37 (kcal/mol) | near-matches, "
           "either strand | of those, on the sense strand | exact / ≤1-mismatch matches | residual "
           "cleavage load, both bounds³ | conventional rules failed⁴ | "
           "at the deeper ceiling: near-matches | of those, on the sense strand | "
           "loci with a gap-spanning hit | survives⁵ |")
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
        deep_cell = "— | — | —" if d is None else f"{d['n']} | {d['hyb']} | {d['gap_loci']}"
        verdict = "not re-screened" if d is None else ("yes" if d["hyb"] == 0 else "**no**")
        rows.append(
            f"| 5′-{seq}-3′ | {lab.replace('__', '::').replace('_', ' ')} | "
            f"{o.get('gc_percent')} | {t.get('gap_specificity_margin', '—')} | "
            f"{t.get('ddg37_discrimination', '—')} | {o.get('n_offtarget_near_matches')} | "
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
    disagree, say so" fold below then joined them, and Table 3's residual-load column read
    `31.4 / 101 / 0 / 0` for `GGGCATATCTCTATAA` — the deep screen's bounds and the default screen's,
    in one cell, in a table whose legend says in its first sentence that it is the default-depth
    result. Six of the nine rows moved that way. It stayed invisible only because the 53 deeper
    re-scores are generated by step 0 of `scripts/regenerate_aso_chain.sh` and never committed
    (the Methods release them ungraded), so the cell was wrong only in a tree where someone had just
    run the chain — which is every tree in which this table gets regenerated.

    ⭐ A FILTER, NOT A WIDER KEY, AND THE REASON IS THE ONE ABOVE IT. Table 3 already picks ONE
    geometry rather than keying by it, because the legend fixes the geometry; the legend fixes the
    depth in the same sentence, so depth is filtered the same way. Adding depth to the key would
    leave `table3` to CHOOSE at lookup time, and choosing at lookup is precisely what failed — the
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
    per_junction = _load("aso-per-junction-table.json")
    gap = _load("aso-gap-length-tradeoff.json")
    expr = _load("aso-offtarget-tissue-expression.json")
    if not (atlas and collapse and chance and thermo and per_junction and gap and expr):
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
    n_expr_seams_txt = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}.get(_n_seams, str(_n_seams))
    # The exposure tissues are named by the artifact, so a fourth one added upstream reaches this
    # sentence instead of leaving it quietly describing three.
    _et = expr["method"]["exposure_tissues"]
    lo_cut_txt = (", ".join(t.lower() for t in _et[:-1]) + " and " + _et[-1].lower()
                  if len(_et) > 1 else _et[0].lower())

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

**Table 1. The in-frame junction space across five *NR4A3* fusion partners.** Every
donor-exon × *NR4A3*-acceptor-exon pair was graded against the frame condition before any design was
emitted. The gap-level margin is the number of junction-unique bases inside the six-nucleotide
catalytic gap on the shorter side of the junction. Frame compatibility is an arithmetic property of exon
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
None of these numbers is a measurement of off-target activity.\n\n¹ Counted over the gap-spanning loci only, not over all of that design's near-match loci.\n\n² A near-match count is what the search returned on EITHER strand; a match on the strand opposite the target window cannot be hybridised by an antisense oligonucleotide and is not a liability. Across this corpus {pct}% of apparent gap-spanning hits ({minus} of {tot:,}) are of that kind, which is why the two columns differ and why the raw count alone should not be read as load. This column counts only the {SAVED_HITS} RETAINED hits. The gap-spanning locus column is recounted from those hits wherever they are the complete list, and is exact there; a “≤” marks a truncated design, where the column instead carries the screen's own count over every ranked hit, computed under a locus assignment since corrected that split some genes across accessions and therefore over-counts. The two columns are not in conflict where a truncated design shows “≥0” sense-strand hits and a non-zero gap-spanning locus count: the sense-strand hits are real and simply fall outside the stored window, which is precisely why such a design cannot be called clean.\n\n⁵ The same design re-screened at a tenfold deeper alignment ceiling, with retention raised to match it so that no hit list is truncated. The three columns are the counterparts of the default-depth columns to their left, given beside them rather than in place of them because the default depth is where the corpus-wide counts elsewhere in the paper were computed and the two must stay comparable. Read together they are the paper's censoring result at the level of a single row: a default-depth count is a lower bound whether or not it reached the 50-hit cap, and three junctions whose default cell reads zero in the gap-spanning column carry gap-spanning hits at ten times the depth. A “—” means the deeper re-screen returned no result for that design and is not a count of zero; three of the panel's 190 records failed at this ceiling.{dagger}

{t2}

**Table 3. The {n_clean} designs with no sense-strand near-match at the default search depth.** Six of
these lose the property when the same junctions are re-screened at a tenfold deeper alignment
ceiling, three of them having returned no near-match at all here; §3.10 reports that
measurement and names the three that survive it. This table is the default-depth result, retained
because it is the depth at which the corpus-wide counts elsewhere in the paper were computed. Every design at the {n_clean_junctions} junctions
where one exists. A design qualifies only
if its retained hit list is not truncated — no more near-matches than the {SAVED_HITS} the screens store — because the
strand of an unstored hit cannot be recovered, so a truncated list cannot establish that nothing
on the sense strand remains. The underlying search is itself capped, so these are the designs whose
near-match lists are shortest, not the designs whose lists are known to be exhaustive. ΔΔG°37 is the margin by which the fusion duplex is favoured over the best
duplex either parent can form, for an unmodified DNA:RNA hybrid; because the fusion duplex pairs
both LNA wings and each parent duplex only one, it is a lower bound on the modified
oligonucleotide's discrimination rather than an upper one. None of these numbers is a measurement of off-target
activity, and none speaks to cleavage.\n\n³ Under the optimistic five-fold and the pessimistic
no-discrimination bound on RNase-H1 single-mismatch discrimination. A single value means the two
bounds agree.\n\n⁴ Of four conventional antisense design rules: GC within 40–60%, no G-quadruplex
motif, no homopolymer run of four, no CpG dinucleotide.\n\n⁵ Whether the design still carries no
sense-strand near-match once its junction is re-screened at the tenfold deeper ceiling. The verdict
is computed from the three deep columns beside it, not asserted, so this table cannot come to
disagree with §3.10 about which designs survive. The six that do not are the reason this table's
default-depth zeros must not be read on their own.

{t3}

**Table 4. The best available design at each of the {per_junction["n_junctions"]} in-frame junctions.** Tables 2 and 3
select across the panel; this table selects within each junction, which is the question a patient's
fusion poses. Designs are ranked by parent liability first, since sparing the wild-type parents is
what the modality exists for, then by pre-mRNA sites, then by distinct gene loci, with ties broken
on gap-level margin rather than on raw hit counts. Nothing was re-screened: every field is joined
from a screen already reported above. Whether a junction has a published exon-resolved breakpoint is
reported separately from specificity and never folded into the ranking — “published” means an
exon-resolved EMC breakpoint is reported for that exon pair, “exon not reported” that the partner
has a resolved breakpoint at a different exon, and “none published” that no exon-resolved breakpoint
has been reported for that partner at all. The last of those is absence of evidence: EMC case
reports usually name the partner gene without sequencing to nucleotide resolution. Gap-paired
near-matches are at the tenfold deeper alignment ceiling, where every hit list is complete. The
genome column is the observed number of gap-paired sites at ≤2 mismatches over the number expected
for an arbitrary 16-mer, so 1.00 is chance. A junction with no design clearing the parent screen is
reported as such rather than given a best row.

{table4(per_junction)}

**Table 5. Gap length against junction specificity, at one junction and across the design space.** The
same junctions tiled and screened at three gapmer geometries, wing held at five nucleotides so that only
the catalytic gap changes. Inside the gap the junction-unique bases on the shorter side and the
bases one wild-type parent pairs on the longer side are complements: they sum to the gap, which the
generating module asserts for every design rather than assuming. Each nucleotide of gap-level margin
therefore costs one nucleotide of contiguous wild-type-parent duplex, and the two directions are
reported separately and never combined into a score. Near-match counts fall partly for a reason the
instrument guarantees rather than measures: at a fixed budget of two mismatches every locus a longer
design can reach is also reached by each of its own shorter sub-windows, so the set can only shrink,
and two mismatches is a fractionally stricter test at 20 nucleotides than at 16. Only the size of
the fall and which designs reach zero are measurements. The three blocks carry different
denominators and are not comparable across blocks: the junction block is one molecule, the matched-junction
block is the six junctions every geometry was screened at, and the corpus block is each geometry's
whole design space, which is not screened at the same junctions. The exhaustive GRCh38 genome scan
is unavailable at 18 and 20 nucleotides by construction, so no row reports it. Because the wing is
five throughout, a parent's junction hybrid is five base pairs plus its share of the gap, so pairing
five nucleotides of contiguous gap DNA and reaching a ten-base-pair hybrid are the same condition
and are reported as one row. ΔG°37 values are for
an unmodified DNA:RNA hybrid; the wing is five at every geometry, so LNA affinity enters each parent
duplex identically and cannot explain a difference between the columns. None of these numbers is a
measurement of cleavage.

{table5(gap)}

**Table 6. Where the clinically-relevant reagents' off-target loci are expressed.** Every gene
locus returned by the deeper screens at the {n_expr_seams_txt} junctions with a published exon-resolved EMC breakpoint,
read against reference expression data. The two compartments answer different questions and are
never combined: a systemically dosed phosphorothioate gapmer distributes predominantly to liver and
kidney, so {lo_cut_txt} address exposure, while the soft-tissue column is the normal
tissue of the compartment EMC arises in and stands in for a tumour no reference atlas contains.
Values are GTEx v8 median TPM across each tissue's donors. The two cuts behind the last column are
stated for legibility and are not thresholds of concern: below {lo_cut:g} TPM in all three exposure
tissues reads as below detection, at or above {hi_cut:g} TPM in any of them as the level at which an
off-target hypothesis would have to be tested. Every raw median is released so another cut can be
applied without re-running. Tiling registers is how many of the designs tiled across that junction
return the locus, which is robustness to where the window is placed and is a different axis from the
record count beside it; neither is ranked on. Transcript records are how many accessions RefSeq
lists for the gene, that is annotation depth, not expression and not affinity. A locus with no
reading carries the reason rather than a zero, because an absent reading is not a reading of
absence. Every hit behind this table sits at 14 of 16 identity, the loosest the screen admits, so
nothing here distinguishes these loci from one another on affinity. None of these numbers is a
measurement of cleavage, and no expression figure is a predicted cleavage event.

{table6(expr)}
"""
    open(OUT, "w").write(doc)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
