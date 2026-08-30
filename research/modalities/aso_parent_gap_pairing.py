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
true of 78 designs in this panel, 56 of them against wild-type NR4A3.

⚠ THAT SENTENCE USED TO RESTATE THE MANUSCRIPT'S OWN CLEAN-DESIGN COUNT and went stale inside the
DEPOSIT (round 23, 2026-08-30). It read "true of five of the nine designs the manuscript calls
clean" — a count from a draft in which nine designs were called clean; the manuscript now says
three, and this file is deposited under the DOI that manuscript prints, so the archive contradicted
the paper it ships with. ⛔ THE FIX IS NOT A NEW NUMBER FOR THE OLD ONE: a module has no business
restating a count whose one home is the paper (rule 1.2). The figures above are this artifact's own,
re-derived from `per_design[].longest_parent_duplex_bp_through_gap` and `.parent`, and they cannot
go stale when the manuscript's selection changes.

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
perfect pairing that CONTAINS the whole gap.

⛔ AND THAT RUN IS NOT THE DUPLEX THE ENZYME ACTS ON. This docstring said it was — "which is the
duplex RNase-H1 would actually see" — while the manuscript's own methods section says the opposite
in terms: "It is not the duplex the enzyme acts on: exactly six of its ten to thirteen base pairs
are the RNA:DNA gap, and the rest are LNA:RNA wing pairs that RNase-H1 does not cleave and its
hybrid-binding domain does not recognise as hybrid, though the catalytic domain's footprint does
extend into them." Both files are in the released archive, so a reviewer who downloads it reads the
claim and its contradiction and cannot tell which the analysis actually made. The code is right; the
sentence describing it was wrong, and it was the more generous of the two. See `MIN_DUPLEX_BP`
below, which states what the run IS: a stated threshold on a contiguous duplex of which exactly six
base pairs are hybrid, not a measured substrate length for a 5-6-5 LNA gapmer.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEQS = os.path.join(HERE, "aso-premrna-sequences.json")

#: ⛔ THE GEOMETRY AND BOTH PATHS FOLLOW THE ENVIRONMENT AS OF 2026-08-13, AND THE THREE MOVE
#: TOGETHER OR NOT AT ALL. `OLIGO_LEN`/`WING` were literals here while every other module in this
#: lane read them from `junction_aso`, so a 5-8-5 or 5-10-5 atlas fed to this screen would have been
#: sliced as a 16-mer: `longest_run_through_gap` would compare positions 5..10 of an 18-mer window
#: against a 16-nt parent window, index past the end of neither string, and return a number that is
#: not about either geometry. A screen that silently reads the wrong six columns of a longer
#: oligonucleotide produces a full, plausible artifact, which is the failure mode this repository
#: keeps paying for.
#: ⚠ DEFAULTS UNCHANGED (16, 5, the committed atlas, the committed output), so `--check` against the
#: committed artifact is bit-for-bit what it was and no existing caller moves.
try:                                                    # noqa: SIM105 — the fallback IS the contract
    sys.path.insert(0, HERE)
    import junction_aso as _ja                          # noqa: PLC0415
    OLIGO_LEN, WING = _ja.OLIGO_LEN, _ja.WING
except Exception:                                       # noqa: BLE001
    OLIGO_LEN = int(os.environ.get("OLIGO_LEN") or 16)
    WING = int(os.environ.get("WING") or 5)

_SUFFIX = os.environ.get("OUT_SUFFIX", "")
ATLAS = os.path.join(HERE, os.environ.get("ATLAS_JSON")
                     or f"nr4a3-fusion-junction-atlas{_SUFFIX}.json")
OUT = os.path.join(HERE, f"aso-parent-gap-pairing{_SUFFIX}.json")

#: 0-based window positions of the DNA gap — `WING`..`OLIGO_LEN - WING`, six wide at the 5-6-5.
GAP = range(WING, OLIGO_LEN - WING)

#: A contiguous ASO:RNA heteroduplex shorter than this is not treated as a plausible RNase-H1
#: substrate. ⚠ NOT THE DNA GAP: a hit counts only if all six gap positions are paired, so the
#: DNA:RNA run is 6 bp for EVERY counted hit by construction and this threshold does not test the
#: catalytic DNA requirement at all. What it tests is total hybrid length for hybrid-binding-domain
#: engagement, which is the quantity the anchor below describes.
#: ⚠ STATED, NOT MEASURED — but no longer arbitrary (anchored 2026-08-13). PMID 35664704, committed
#: full text at `literature-cache:literature/aso-rnaseh-mismatch/PMC9136273.txt` and quoted in
#: `research/manuscripts/aso/lit-targets-aso-gap-length.json`: "RNase H1 requires a minimum length
#: of 7 to 10 RNA:DNA hybridized nucleotides to bind with its hybrid binding domain and cleave the
#: RNA downstream." TEN IS THE STRICT END of that range, so this count is a FLOOR: at 7 the same
#: screen returns 175 of 190 rather than 87. That sentence is a discussion-section rationale citing
#: prior work, not a measurement, and nothing measures it for a 5-6-5 LNA gapmer.
#: ⭐ THE RESULT DOES NOT TURN ON THE VALUE, WHICH IS THE POINT WORTH KNOWING. The two designs that
#: survive every screen have a longest run of ZERO — no window of any parent pairs their gap at any
#: length — so the candidate set is threshold-independent. The margin ordering is strictly monotone
#: at every threshold from 6 to 12. And against NR4A3 the histogram is EMPTY at 10 and holds one
#: design at 9, because a duplex at the real mature exon-2/exon-3 junction spans window positions
#: 5..15 and so cannot be shorter than 11 bp: any threshold in [10, 11] returns the same 61.
#: Every design's raw longest run is released so another threshold can be applied without re-running.
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

    gap_nt = len(GAP)
    return {
        "_what": (f"For every junction gapmer, the longest contiguous duplex a MATURE wild-type "
                  f"parent transcript can form that pairs the whole {gap_nt}-nucleotide catalytic "
                  f"gap of a {OLIGO_LEN}-mer {WING}-{gap_nt}-{WING} gapmer."),
        "_why": (f"None of the manuscript's three screens can see this: the alignment screen filters "
                 f"at >={OLIGO_LEN - 2}/{OLIGO_LEN} identity and excludes parent records, the "
                 f"exhaustive scan admits <=1 mismatch, and the pre-mRNA arm searches unspliced "
                 f"sequence and so cannot reach a mature exon-exon junction."),
        # ⛔ THE GEOMETRY IS STATED, NOT LEFT TO BE INFERRED FROM `gap_positions_0based`. Two of the
        # three quantities this screen turns on — how wide the catalytic gap is, and how long a
        # window is compared — are geometry, and until 2026-08-13 they were literals in this module
        # and appeared in the artifact only as a pair of gap indices. A 5-8-5 and a 5-6-5 run would
        # have differed in the artifact by the string "[5, 12]" against "[5, 10]", in a file whose
        # headline count the manuscript quotes.
        "_geometry": {"oligo_len": OLIGO_LEN, "wing": WING, "gap_nt": gap_nt,
                      "architecture": f"{WING}-{gap_nt}-{WING} (LNA-DNA-LNA)",
                      "atlas": os.path.basename(ATLAS),
                      "_note": ("MIN_DUPLEX_BP is an ABSOLUTE hybrid length and does NOT scale with "
                                "the gap. At a gap of 10 the catalytic gap alone is already a 10 bp "
                                "hybrid, so every gap-pairing window clears the threshold by "
                                "construction and `n_with_parent_duplex_through_gap` equals the "
                                "count of gap-pairing windows; at a gap of 6 a window needs four "
                                "further flanking pairs to reach it. Both readings are real and "
                                "they are not the same reading, so compare geometries on the raw "
                                "`longest_parent_duplex_bp_through_gap` distribution as well.")},
        "_what_this_is_not": [
            "Not a measurement of off-target activity. A duplex is necessary for RNase-H1 cleavage, "
            "not sufficient, and nothing here is a cleavage assay.",
            "Not transcriptome-wide. Six parent transcripts only — the same bound the pre-mRNA arm "
            "carries.",
            # ⚠ THE LOOSE-THRESHOLD FIGURE IS COUNTED, NOT REMEMBERED. It was the literal "175 of
            # 190", measured on the 16-mer corpus — correct there and false at any other geometry,
            # in the one bullet that tells a reader the headline count is threshold-dependent.
            f"MIN_DUPLEX_BP is a STATED threshold, not a measured one — though not an arbitrary "
            f"one: 10 is the strict end of the 7-to-10 hybridised nucleotides PMID 35664704 reports "
            f"as the minimum for RNase-H1 hybrid-binding-domain engagement, so this count is a floor "
            f"and returns {sum(1 for r in rows if r['longest_parent_duplex_bp_through_gap'] >= 7)} "
            f"of {len(rows)} at a threshold of 7. Every design's raw longest "
            f"run is released so another threshold can be applied without re-running this.",
            # ⚠ THE COUNT WAS DROPPED, NOT UPDATED (round 23, 2026-08-30). This read "The two
            # designs surviving every screen in the manuscript" while the manuscript said three —
            # a stale restatement of the paper's own number, inside the archive the paper cites.
            # The threshold-independence point never needed the count, and without it the sentence
            # cannot go stale when the selection moves.
            "Not a result that turns on that threshold. Every design that survives every screen "
            "has a longest run of ZERO at any length, and the ordering by gap-level margin is "
            "monotone at every threshold from 6 to 12.",
        ],
        "_cost": "$0 — offline, over two committed artifacts, no network and no credentials.",
        "method": {
            "orientation": "forward only; a reverse-complement match cannot be hybridised",
            "compartment": "mature (spliced) parent transcript",
            "parents_searched": sorted(parents),
            "parent_nt_searched": {g: len(s) for g, s in sorted(parents.items())},
            "gap_positions_0based": [GAP.start, GAP.stop - 1],
            "min_duplex_bp": MIN_DUPLEX_BP,
            "oligo_len": OLIGO_LEN,
            "wing": WING,
            "sources": ["aso-premrna-sequences.json", os.path.basename(ATLAS)],
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
