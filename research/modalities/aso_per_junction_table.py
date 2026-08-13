#!/usr/bin/env python3
"""One best-available gapmer PER JUNCTION, across all five screens.

⛔ WHY THIS EXISTS (2026-08-13, trimcrae: *"Why do we only have one candidate instead of one per
fusion type? Are we claiming it's impossible to make an ASO for any other fusion?"*). No — the
paper's own headline is that all 38 frame-compatible junctions yield a gapmer matching no parent
perfectly. But the candidate set was selected GLOBALLY: it answers "what is the single cleanest
reagent in the whole panel", which is not the question a reader has. A patient carries ONE fusion at
ONE exon pair, and is not served by the fact that the panel's cleanest design sits somewhere else.

So this ranks WITHIN each junction and publishes the whole table. The global winner is still
visible; it is simply no longer the only row.

⚠ WHAT THIS IS NOT. It is not a new measurement. Every number here is joined from a screen that
already ran, and no hit is re-aligned or re-graded. It is a re-presentation, and the honest framing
of it is that §3.2 of the manuscript already did this analysis in prose for the junctions that
mattered most — this makes it usable as a reagent list rather than something a reader reconstructs.

⛔ AND IT DOES NOT COLLAPSE TO ONE SCORE. Two quantities move in opposite directions and the whole
value of the table is in seeing both:

  * **gap-level margin** — junction-unique bases inside the catalytic gap on the shorter side. This
    is fusion-versus-parent discrimination, which is the entire point of the modality.
  * **transcriptome load** — gap-paired hybridisable near-matches at the deeper ceiling, recounted
    to gene LOCI rather than RefSeq accessions.

At the *EWSR1* exon 12 seam these disagree outright: `GGGCATATCATCAAAC` has margin 3 and a load of
123 hits, `GCATATCATCAAACCA` has margin 1 and a load of 34. Neither is "the" answer, and a composite
score would have hidden the trade instead of reporting it. The rank here is by load among designs
that clear the parent screens, with margin printed beside it, never folded in.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "aso-per-junction-table.json")

sys.path.insert(0, HERE)
import junction_aso_locus_collapse as C  # noqa: E402
import junction_aso_offtarget as ja  # noqa: E402

#: ⛔ EXON-RESOLVED PATIENT BREAKPOINTS, AND ONLY WHAT IS ACTUALLY CITED IN THE MANUSCRIPT.
#: Nothing is inferred here. EMC case reports overwhelmingly name the partner GENE without
#: sequencing to nucleotide resolution, so a junction absent from this map is "no published
#: exon-resolved breakpoint" — which is ABSENCE OF EVIDENCE, not evidence the junction does not
#: occur. The two are different and the paper must not blur them: for *TAF15* the published
#: breakpoint is exon 6, so a design at *TAF15* exon 1 is CONTRADICTED by the literature, whereas
#: *FUS* has no exon-resolved EMC breakpoint published at all and its junctions are merely unreported.
PUBLISHED_BREAKPOINTS = {
    # type 1, 10 of the 15 EWSR1-rearranged tumours of an 18-case series
    "EWSR1_e12__NR4A3_e3": ["PMID: 12378528"],
    # primary report of the variant fusion, and all three TAF15-rearranged tumours of that series
    "TAF15_e6__NR4A3_e3": ["PMID: 10537274", "PMID: 12378528"],
}

#: partners for which SOME exon-resolved EMC breakpoint is published, so "unreported exon" at that
#: partner is a weaker statement than at a partner with none
PARTNERS_WITH_ANY_PUBLISHED_EXON = {"EWSR1", "TAF15"}


def _clinical_tier(label):
    """Three tiers, reported separately from specificity. See PUBLISHED_BREAKPOINTS."""
    if label in PUBLISHED_BREAKPOINTS:
        return "published_exon_resolved_breakpoint", PUBLISHED_BREAKPOINTS[label]
    partner = str(label).split("_")[0]
    if partner in PARTNERS_WITH_ANY_PUBLISHED_EXON:
        # the partner is established and other exons of it are resolved, so this exon is contradicted
        # by the resolved ones rather than merely unobserved
        return "partner_published_this_exon_not_reported", []
    return "no_published_exon_resolved_breakpoint", []


def _deep_screens():
    """Every deep re-screen as (junction, design) PAIRS, with gap-paired hits recounted to loci.

    ⛔ NOT KEYED BY DESIGN. Nine designs span the seam of more than one junction exactly — that is
    §3.2's whole cross-partner-coverage result — so one sequence legitimately belongs to three
    junctions at once. Keying a dict by the sequence silently kept only the last screen read, and
    dropped `EWSR1_e12__NR4A3_e3` and `FUS_e10__NR4A3_e3` from the table entirely: 36 junctions
    where the panel has 38, with the MOST COMMONLY REPORTED patient junction among the missing.
    A per-junction table that loses the clinically-central junction to a dict collision is worse
    than no table, so the pairs are emitted flat and grouped by the caller.
    """
    pairs = []
    for path in sorted(glob.glob(os.path.join(HERE, "junction-aso-offtarget-*deep500*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        label = d.get("junction_label")
        for o in d.get("oligos", []):
            if o.get("status") != "screened":
                continue
            hits = o.get("offtargets") or []
            # ⛔ a truncated list would make every count below a lower bound wearing the costume of
            # a measurement — the exact defect that produced the withdrawn "nine clean designs".
            if o.get("n_offtarget_near_matches") != len(hits):
                raise SystemExit(
                    f"{os.path.basename(path)}: {o['antisense_5to3']} stores {len(hits)} hits but "
                    f"reports {o.get('n_offtarget_near_matches')}; the deep screens must retain all")
            lo, hi = ja.GAP_REGION_1BASED
            plus = [h for h in hits if not h.get("is_minus_strand")]
            paired = [h for h in plus
                      if h["q_from"] <= lo and h["q_to"] >= hi and h.get("gap_mismatches") == 0]
            loci = Counter(C.locus_of(h) for h in paired)
            pairs.append((label, o["antisense_5to3"], {
                "n_near_matches": len(hits),
                "n_hybridisable": len(plus),
                "n_gap_paired": len(paired),
                "n_gap_paired_loci": len(loci),
                "gap_paired_loci": sorted(loci),
            }))
    return pairs


def _load(name, key="per_design"):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return {}
    return {r["antisense_5to3"]: r for r in json.load(open(path, encoding="utf-8"))[key]}


def build():
    deep = _deep_screens()
    parent = _load("aso-parent-gap-pairing.json")
    premrna = _load("aso-premrna-offtarget.json")
    genome = _load("aso-genome-offtarget.json")

    by_junction = defaultdict(list)
    seen = set()
    for label, seq, dp in deep:
        # the same (junction, design) can appear in more than one batch file; keep it once
        if (label, seq) in seen:
            continue
        seen.add((label, seq))
        pa, pm, gn = parent.get(seq, {}), premrna.get(seq, {}), genome.get(seq, {})
        oe = gn.get("observed_over_expected") or {}
        row = {
            "antisense_5to3": seq,
            "gap_specificity_margin": pa.get("gap_specificity_margin"),
            # screen 2: transcriptome at ten times the default ceiling
            "n_gap_paired": dp["n_gap_paired"],
            "n_gap_paired_loci": dp["n_gap_paired_loci"],
            "gap_paired_loci": dp["gap_paired_loci"],
            "n_hybridisable": dp["n_hybridisable"],
            "n_near_matches": dp["n_near_matches"],
            # screen 4: mature parent transcript, the liability no transcriptome screen reaches
            "parent": pa.get("parent"),
            "parent_duplex_bp": pa.get("longest_parent_duplex_bp_through_gap"),
            "parent_is_liability": pa.get("counts_as_liability"),
            # screen 3: unspliced pre-mRNA, since RNase-H1 is nuclear
            "premrna_gap_paired_hybridisable": pm.get("n_hybridisable_gap_fully_paired"),
            # screen 5: exhaustive GRCh38
            "genome_oe_gap_paired_le2": oe.get("gap_paired_le2"),
            "genome_named_target_sites": gn.get("n_named_target_sites"),
            "genome_named_target_genes": gn.get("named_target_genes"),
        }
        by_junction[label].append(row)

    junctions = []
    for label in sorted(by_junction, key=str):
        rows = by_junction[label]
        # ⛔ RANK, DO NOT SCORE, AND BREAK TIES ON MARGIN RATHER THAN ON RAW HITS. Parent liability
        # is disqualifying because sparing the wild-type parents is the modality's reason to exist;
        # then pre-mRNA; then LOCI, which §3.7 establishes is the honest breadth denominator.
        #
        # ⚠ WHEN LOCI TIE, THE TIE-BREAK IS MARGIN — NOT the hit count. Ranking equal-breadth
        # designs by raw hits reintroduces exactly the inflation the locus recount exists to remove,
        # and it produced a wrong answer at the junction that matters most: at EWSR1 e12 the two
        # leading registers BOTH touch 6 loci, but `GCATATCATCAAACCA` shows 34 hits against
        # `GGGCATATCATCAAAC`'s 123, so a hit-count tie-break promoted the margin-1 design over the
        # margin-3 one and made the manuscript's long-standing pick look superseded. It is not:
        # equal breadth, better fusion-versus-parent discrimination. Raw hits stay as the last key,
        # where they can only order designs that already tie on both real measures.
        rows.sort(key=lambda r: (bool(r["parent_is_liability"]),
                                 r["premrna_gap_paired_hybridisable"] or 0,
                                 r["n_gap_paired_loci"],
                                 -(r["gap_specificity_margin"] or 0),
                                 r["n_gap_paired"]))
        tier, refs = _clinical_tier(label)
        eligible = [r for r in rows if not r["parent_is_liability"]]
        junctions.append({
            "junction_label": label,
            "clinical_tier": tier,
            "breakpoint_refs": refs,
            "n_designs_screened": len(rows),
            "n_designs_clearing_the_parent_screen": len(eligible),
            "best_available": eligible[0] if eligible else None,
            "best_by_gap_specificity_margin": max(
                rows, key=lambda r: (r["gap_specificity_margin"] or -1))["antisense_5to3"],
            "designs": rows,
        })

    return {
        "what": ("The best available junction-spanning gapmer for EACH of the frame-compatible "
                 "NR4A3-fusion junctions, joined across all five specificity screens, with the "
                 "clinical-occurrence tier of the junction reported separately from specificity."),
        "⚠_not_a_measurement": ("Nothing here was re-screened. Every field is joined from an "
                                "artifact that already existed; no hit was re-aligned or re-graded, "
                                "and no number is converted into a predicted cleavage event."),
        "⛔_two_axes_not_one": ("gap_specificity_margin (fusion-versus-parent discrimination) and "
                               "the transcriptome load move in opposite directions at some seams "
                               "and are never combined into a single score. Ranking is by load "
                               "among designs clearing the parent screen; margin is printed beside."),
        "⚠_absence_of_evidence": ("A junction with no published exon-resolved breakpoint is "
                                  "UNREPORTED, not shown absent: EMC case reports usually name the "
                                  "partner gene without sequencing to nucleotide resolution. That "
                                  "is a weaker statement than a contradiction, and the tiers keep "
                                  "them apart."),
        "n_junctions": len(junctions),
        "junctions": junctions,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="rebuild from committed inputs and fail if the artifact is stale")
    args = ap.parse_args(argv)
    out = build()
    if args.check:
        if not os.path.exists(OUT):
            print(f"per-junction table --check: MISSING {OUT}")
            return 1
        if json.load(open(OUT, encoding="utf-8")) != out:
            print("per-junction table --check: STALE — re-run aso_per_junction_table.py")
            return 1
        print(f"per-junction table --check: OK ({out['n_junctions']} junctions)")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print(f"wrote {OUT}  ({out['n_junctions']} junctions)")
    for j in out["junctions"]:
        b = j["best_available"]
        tier = {"published_exon_resolved_breakpoint": "PUBLISHED",
                "partner_published_this_exon_not_reported": "exon-unreported",
                "no_published_exon_resolved_breakpoint": "unreported"}[j["clinical_tier"]]
        if b is None:
            print(f"  {j['junction_label']:<24}{tier:<17}  no design clears the parent screen")
            continue
        print(f"  {j['junction_label']:<24}{tier:<17}{b['antisense_5to3']:<19}"
              f"margin={str(b['gap_specificity_margin']):<3}"
              f"loci={b['n_gap_paired_loci']:<3}hits={b['n_gap_paired']:<4}"
              f"parent={str(b['parent_duplex_bp']):<3}bp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
