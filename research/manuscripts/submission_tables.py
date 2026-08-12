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

    by_j = {}
    for s in collapse["screens"]:
        lab = s.get("junction_label")
        if not lab:                              # the modelled reference seams carry no label
            continue
        by_j.setdefault(lab, []).extend(s["per_oligo"])

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
    hdr = ("| junction | designs screened | best gap-level margin | that design | near-matches "
           "(transcripts → loci) | loci with a gap-spanning hit | of those, predicted models only¹ | "
           "≤1-mismatch matches across that junction's designs, median (max) |")
    sep = "|---|---|---|---|---|---|---|---|"
    rows = []
    for lab in sorted(by_j):
        ol = by_j[lab]
        ranked = sorted(ol, key=lambda o: -(gap_margin.get((lab, o["antisense_5to3"])) or -1))
        best = ranked[0]
        gm = gap_margin.get((lab, best["antisense_5to3"]))
        cens = "≥" if best["right_censored"] else ""
        vals = sorted(le1.get(lab, []))
        med = vals[len(vals) // 2] if vals else "—"
        mx = max(vals) if vals else "—"
        rows.append(
            f"| {lab.replace('__', '::').replace('_', ' ')} | {len(ol)} | "
            f"{gm if gm is not None else '—'} | 5′-{best['antisense_5to3']}-3′ | "
            f"{cens}{best['n_transcript_near_matches_reported']} → "
            # "of those" means OF THE GAP-SPANNING LOCI, so it is the intersection of the two
            # named lists, not the whole-design predicted-only count — which is larger and would
            # have overstated how much of the liability sits in predicted annotation.
            f"{cens}{best['n_distinct_loci']} | {cens}{best['n_loci_with_a_gap_spanning_hit']} | "
            f"{len(set(best.get('loci_with_a_gap_spanning_hit') or []) & set(best.get('loci_seen_only_as_predicted_models') or []))} | "
            f"{med} ({mx}) |")
    return "\n".join([hdr, sep] + rows)


def main():
    atlas = _load("nr4a3-fusion-junction-atlas.json")
    collapse = _load("junction-aso-offtarget-locus-collapse.json")
    chance = _load("offtarget-chance-baseline.json")
    if not (atlas and collapse and chance):
        print("a required artifact is missing", file=sys.stderr)
        return 2

    doc = f"""<!-- GENERATED — DO NOT EDIT. Regenerate: python3 research/manuscripts/submission_tables.py -->

# Tables — fusion-junction ASO submission

**Table 1. The frame-compatible junction space across four *NR4A3* fusion partners.** Every
donor-exon × *NR4A3*-acceptor-exon pair was graded against the frame condition before any design was
emitted. The gap-level margin is the number of junction-unique bases inside the six-nucleotide
catalytic gap on the shorter side of the seam. Frame compatibility is an arithmetic property of exon
structure and is not a claim about which junctions patients carry.

{table1(atlas)}

**Table 2. Predicted specificity per screened junction.** One row per junction; figures are for the
design with the highest gap-level margin at that junction, which is the ranking the Methods define. Near-match counts are of RefSeq
transcript accessions and are also given collapsed to distinct gene loci, since RefSeq carries one
accession per annotated variant. A “≥” marks a right-censored count: the screens store the top 15
hits per design, so a design with more is a lower bound. **All gap-resolved counts are upper
bounds**: the BLAST arm did not parse alignment orientation, so minus-strand matches — which an
antisense oligonucleotide cannot hybridise — are included. `XM_`/`XR_` records are computationally
predicted gene models rather than curated transcripts, and are counted separately for that reason.
None of these numbers is a measurement of off-target activity.\n\n¹ Counted over the gap-spanning loci only, not over all of that design's near-match loci.

{table2(collapse, chance, atlas)}
"""
    open(OUT, "w").write(doc)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
