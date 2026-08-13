#!/usr/bin/env python3
"""Can a MATURE wild-type parent transcript pair a junction gapmer's catalytic gap in full?

⛔ WHY THIS EXISTS. Three screens stand behind the manuscript's cleanliness claim and NONE of them
can answer this question, which is the one the modality actually turns on:

  · the gap-resolved alignment screen drops every hit below >=14/16 identity, AND drops parent-gene
    records outright (`junction_aso_offtarget.is_parent`), because each parent matches one wing by
    construction and would otherwise swamp the list;
  · the exhaustive transcript scan admits <=1 mismatch, far stricter than the duplexes below;
  · the pre-mRNA arm searches UNSPLICED sequence, in which an exon is followed by an intron — so it
    structurally cannot see a MATURE exon-exon junction. It found the wild-type NR4A3
    intron-2/exon-3 route and could not, by construction, find the mature exon-2/exon-3 one.

So a parent duplex that pairs the whole six-nucleotide DNA gap at 11 or 12 contiguous base pairs is
invisible to all three, while being exactly what RNase-H1 needs. That is not a hypothetical: it is
true of five of the nine designs the manuscript calls clean, one of them against wild-type NR4A3.

⛔⛔ AND IT IS THE GAP-LEVEL MARGIN'S BLIND SPOT, NOT AN UNRELATED RISK. The margin counts bases that
are junction-unique AT THE SEAM — donor-side bases inside the gap. It never asks whether a parent
happens to carry those same bases somewhere else in its own transcript. At margin 1 exactly one
donor base sits in the gap, so a parent needs one lucky base to pair the whole gap; at margin 3 it
needs three. The margin is therefore a PREDICTOR of this liability rather than a guarantee against
it, and the numbers below are what that costs: 50 of 76 designs at margin 1 versus 8 of 38 at
margin 3.

WHAT THIS IS NOT
  · Not a measurement of off-target activity. A duplex is necessary for RNase-H1 cleavage and is not
    sufficient, and nothing here is a cleavage assay.
  · Not genome-wide, and not transcriptome-wide. It searches the six parent transcripts of this
    panel and says nothing about any other gene, which is the same bound the pre-mRNA arm carries.
  · Not a claim that a short duplex is a liability. `MIN_DUPLEX_BP` is a stated threshold, not a
    measured one, and every design's longest run is released so a reader can pick another.

METHOD. Mature parent transcripts are spliced from the committed unspliced sequence and exon spans
(`aso-premrna-sequences.json`) — the same records the pre-mRNA arm used, so the two arms cannot
disagree about what a parent is. Every 16-nucleotide window of every mature parent is compared to
every design's target window in the FORWARD orientation only, because a reverse-complement match
cannot be hybridised by an antisense oligonucleotide (the manuscript's own orientation rule). A hit
counts only if all six gap positions are paired; its size is then the longest contiguous run of
perfect pairing that CONTAINS the whole gap, which is the duplex RNase-H1 would actually see.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEQS = os.path.join(HERE, "aso-premrna-sequences.json")
ATLAS = os.path.join(HERE, "nr4a3-fusion-junction-atlas.json")
OUT = os.path.join(HERE, "aso-parent-gap-pairing.json")

OLIGO_LEN = 16
WING = 5
#: 0-based window positions of the DNA gap in a 5-6-5 16-mer.
GAP = range(WING, OLIGO_LEN - WING)

#: A contiguous DNA:RNA duplex shorter than this is not treated as a plausible RNase-H1 substrate.
#: ⚠ STATED, NOT MEASURED. It is reported alongside every design's raw longest run so that a reader
#: who prefers another threshold can apply it without re-running anything.
MIN_DUPLEX_BP = 10


def mature_parents():
    """gene -> spliced transcript, built from the same records the pre-mRNA arm used."""
    genes = json.load(open(SEQS, encoding="utf-8"))["genes"]
    out = {}
    for g, v in genes.items():
        seq = v["sequence"]
        spliced = "".join(seq[a:b + 1] for a, b in v["exon_spans_0based_inclusive"])
        if len(spliced) != v["exonic_nt"]:                 # a splice that disagrees with the record
            raise RuntimeError(f"{g}: spliced {len(spliced)} nt against exonic_nt {v['exonic_nt']}")
        out[g] = spliced
    return out


def longest_run_through_gap(window, target):
    """Longest contiguous perfect match that COVERS the whole gap, or 0 if the gap is not paired."""
    if any(window[k] != target[k] for k in GAP):
        return 0
    lo = GAP.start
    while lo - 1 >= 0 and window[lo - 1] == target[lo - 1]:
        lo -= 1
    hi = GAP.stop - 1
    while hi + 1 < OLIGO_LEN and window[hi + 1] == target[hi + 1]:
        hi += 1
    return hi - lo + 1


def best_parent_duplex(target, parents):
    """(longest run through the gap, gene, 0-based start) over every mature parent, forward only."""
    best = (0, None, None)
    for gene, seq in parents.items():
        for i in range(len(seq) - OLIGO_LEN + 1):
            run = longest_run_through_gap(seq[i:i + OLIGO_LEN], target)
            if run > best[0]:
                best = (run, gene, i)
    return best


def build():
    parents = mature_parents()
    atlas = json.load(open(ATLAS, encoding="utf-8"))
    rows = []
    for panel in atlas["panels"]:
        for d in panel.get("designs") or []:
            if not d.get("fusion_specific"):
                continue
            run, gene, start = best_parent_duplex(d["target_mRNA_5to3"], parents)
            rows.append({
                "junction": panel["junction_label"],
                "antisense_5to3": d["antisense_5to3"],
                "gap_specificity_margin": d["gap_specificity_margin"],
                "longest_parent_duplex_bp_through_gap": run,
                "parent": gene,
                "parent_start_0based": start,
                "counts_as_liability": run >= MIN_DUPLEX_BP,
            })

    liable = [r for r in rows if r["counts_as_liability"]]
    by_margin = {}
    for r in rows:
        m = str(r["gap_specificity_margin"])
        b = by_margin.setdefault(m, {"n_designs": 0, "n_with_parent_duplex": 0})
        b["n_designs"] += 1
        b["n_with_parent_duplex"] += 1 if r["counts_as_liability"] else 0
    by_parent = {}
    for r in liable:
        by_parent[r["parent"]] = by_parent.get(r["parent"], 0) + 1

    return {
        "_what": ("For every junction gapmer, the longest contiguous duplex a MATURE wild-type "
                  "parent transcript can form that pairs the whole six-nucleotide catalytic gap."),
        "_why": ("None of the manuscript's three screens can see this: the alignment screen filters "
                 "at >=14/16 identity and excludes parent records, the exhaustive scan admits <=1 "
                 "mismatch, and the pre-mRNA arm searches unspliced sequence and so cannot reach a "
                 "mature exon-exon junction."),
        "_what_this_is_not": [
            "Not a measurement of off-target activity. A duplex is necessary for RNase-H1 cleavage, "
            "not sufficient, and nothing here is a cleavage assay.",
            "Not transcriptome-wide. Six parent transcripts only — the same bound the pre-mRNA arm "
            "carries.",
            "MIN_DUPLEX_BP is a STATED threshold, not a measured one. Every design's raw longest "
            "run is released so another threshold can be applied without re-running this.",
        ],
        "_cost": "$0 — offline, over two committed artifacts, no network and no credentials.",
        "method": {
            "orientation": "forward only; a reverse-complement match cannot be hybridised",
            "compartment": "mature (spliced) parent transcript",
            "parents_searched": sorted(parents),
            "parent_nt_searched": {g: len(s) for g, s in sorted(parents.items())},
            "gap_positions_0based": [GAP.start, GAP.stop - 1],
            "min_duplex_bp": MIN_DUPLEX_BP,
            "sources": ["aso-premrna-sequences.json", "nr4a3-fusion-junction-atlas.json"],
        },
        "corpus": {
            "n_designs": len(rows),
            "n_with_parent_duplex_through_gap": len(liable),
            "by_gap_specificity_margin": by_margin,
            "which_parent_supplies_it": dict(sorted(by_parent.items())),
        },
        "per_design": sorted(rows, key=lambda r: (r["junction"], r["antisense_5to3"])),
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    new = json.dumps(art, indent=1, sort_keys=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("aso-parent-gap-pairing.json is stale; re-run without --check", file=sys.stderr)
            return 1
        print("parent gap-pairing artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    c = art["corpus"]
    print(f"wrote {os.path.basename(OUT)}: {c['n_with_parent_duplex_through_gap']} of "
          f"{c['n_designs']} designs have a mature parent duplex of >= {MIN_DUPLEX_BP} bp pairing "
          f"the whole gap; by margin {c['by_gap_specificity_margin']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
