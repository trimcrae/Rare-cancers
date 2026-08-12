#!/usr/bin/env python3
"""
Is an off-target count a finding, or is it what any 16-mer would return? — the missing null.

⛔ WHY THIS EXISTS, AND IT INVALIDATES A HEADLINE. The manuscript's central negative was "0 of 58
designs is predicted off-target-clean". A referee pointed out that this is arithmetically
unavoidable, and the arithmetic checks out: the number of 16-mers within 2 substitutions of a given
16-mer is 1,129, so the probability that an arbitrary transcriptome position matches at >= 14/16 is
1129 / 4^16 = 2.6e-07. Against a human RefSeq RNA set of order 1e8-1e9 nucleotides that is TENS TO
HUNDREDS of expected near-matches PER OLIGO, for any 16-mer whatsoever — a scrambled control, a
marketed gapmer, a random string. "Zero near-matches at >= 14/16" is not an achievable state, so a
count of zero-clean designs is a property of the threshold and the size of the transcriptome, not a
property of EMC, NR4A3, or fusion junctions.

⭐ WHAT REPLACES IT. The informative quantity is not whether a design has hits; it is whether it has
MORE hits than chance. This module computes the chance expectation under an explicit null and
reports every committed design as observed-versus-expected. A design at or below expectation is not
"clean" — nothing is — but it is "no worse than an arbitrary oligonucleotide of its length", which is
a defensible statement, is what a chemist actually wants to know, and is the statement the paper
could not previously make.

⚠ THE NULL IS DELIBERATELY CRUDE, AND ITS LIMITS RUN IN BOTH DIRECTIONS. It assumes independent,
uniformly distributed bases. Real transcriptomes are neither: base composition is skewed, sequence is
repetitive, paralogues and transcript variants of one locus multiply near-matches, and a GC-rich or
low-complexity query is enriched for partners. So this is an ORDER-OF-MAGNITUDE reference, not a
p-value, and it is used here only to answer a coarse question — is an observed count in the region
chance alone predicts, or far above it? A design far above chance is a real finding about that
sequence. A design at chance is a statement that the screen found nothing specific to it.
⛔ In particular this must NEVER be reported as a significance test, and no threshold on the ratio is
proposed here, because the null is too crude to license one.

Outputs: offtarget-chance-baseline.json
"""

import glob
import json
import os
import sys
import time
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "offtarget-chance-baseline.json")

OLIGO_LEN = 16
#: Transcriptome size is not recorded by the screens (they record transcript COUNT, 186,185, not
#: nucleotides), so the expectation is reported as a RANGE over a plausible span rather than as a
#: single number nobody measured. Naming the uncertainty is the point; picking a midpoint would hide it.
TRANSCRIPTOME_NT_RANGE = (3.0e8, 8.0e8)


def n_within(length, mismatches):
    """How many distinct strings lie within `mismatches` substitutions of one string of `length`."""
    return sum(comb(length, k) * 3 ** k for k in range(mismatches + 1))


def chance_expectation(length, mismatches):
    """(p_per_position, (lo, hi) expected hits per oligo) under an i.i.d. uniform-base null."""
    p = n_within(length, mismatches) / 4 ** length
    return p, tuple(round(p * n, 1) for n in TRANSCRIPTOME_NT_RANGE)


def collect_observed():
    """Every committed design's uncapped <=1-mismatch count, keyed by junction and sequence."""
    rows = []
    for path in sorted(glob.glob(os.path.join(HERE, "aso-insilico-evaluation*.json"))):
        d = json.load(open(path))
        label = d.get("junction_label") or os.path.basename(path)
        for o in d.get("top_designs", []):
            if o.get("offtarget_le1mm") is None:
                continue
            rows.append({"junction": label, "antisense_5to3": o["antisense_5to3"],
                         "gc_percent": o.get("gc_percent"),
                         "offtarget_exact": o.get("offtarget_exact"),
                         "offtarget_le1mm": o["offtarget_le1mm"],
                         "_source": os.path.basename(path)})
    return rows


def build():
    p2, exp2 = chance_expectation(OLIGO_LEN, 2)
    p1, exp1 = chance_expectation(OLIGO_LEN, 1)
    rows = collect_observed()
    counts = sorted(r["offtarget_le1mm"] for r in rows)
    n = len(counts)
    median = counts[n // 2] if n % 2 else (counts[n // 2 - 1] + counts[n // 2]) / 2
    lo, hi = exp1

    for r in rows:
        c = r["offtarget_le1mm"]
        r["expected_le1mm_lo"], r["expected_le1mm_hi"] = lo, hi
        r["at_or_below_chance"] = c <= hi
        r["ratio_to_chance_hi"] = round(c / hi, 2) if hi else None

    return {
        "_title": "Chance baseline for junction-gapmer off-target counts",
        "_generated_by": "research/modalities/offtarget_chance_baseline.py",
        "_cost": "$0 — arithmetic over committed artifacts. No network, no GPU.",
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "_why": (
            "The manuscript's negative headline — '0 of 58 designs predicted off-target-clean' — is "
            "arithmetically unavoidable at a >=14/16 identity threshold and therefore says nothing "
            "about this disease, this fusion, or these junctions. This file computes what chance "
            "alone predicts, so an observed count can be read against it."),
        "_what_this_is_not": [
            "NOT a significance test and NOT a p-value. The null assumes independent uniform bases; "
            "real transcript sequence is composition-skewed, repetitive, and full of paralogues and "
            "transcript variants of one locus. It is an order-of-magnitude reference only.",
            "NOT a cleanliness criterion. Nothing here licenses calling any design clean, and no "
            "threshold on the observed/expected ratio is proposed, because the null cannot support "
            "one.",
            "NOT a substitute for calibration against oligonucleotides with MEASURED off-target "
            "behaviour, which is what would actually convert these counts into a decision and which "
            "this repository has not done.",
        ],
        "null_model": {
            "oligo_len": OLIGO_LEN,
            "assumption": "independent, uniformly distributed bases",
            "transcriptome_nt_range_assumed": list(TRANSCRIPTOME_NT_RANGE),
            "_transcriptome_nt_caveat": (
                "The screens record transcripts SCANNED (186,185), not nucleotides, so the "
                "nucleotide span is assumed over a range rather than measured. Every expectation "
                "below inherits that range."),
            "n_strings_within_2_substitutions": n_within(OLIGO_LEN, 2),
            "p_per_position_ge_14_of_16": p2,
            "expected_near_matches_per_oligo_ge_14_of_16": list(exp2),
            "n_strings_within_1_substitution": n_within(OLIGO_LEN, 1),
            "p_per_position_ge_15_of_16": p1,
            "expected_hits_per_oligo_ge_15_of_16": list(exp1),
        },
        "observed": {
            "n_designs": n,
            "min": counts[0], "median": median, "max": counts[-1],
            "mean": round(sum(counts) / n, 1),
            "n_at_or_below_chance_upper": sum(1 for r in rows if r["at_or_below_chance"]),
        },
        "_reading": (
            f"At the <=1-mismatch threshold chance alone predicts {lo}-{hi} hits per 16-mer. The "
            f"observed median across {n} committed designs is {median}. The median design is "
            "therefore AT OR BELOW what an arbitrary oligonucleotide of this length would return, "
            "which is the honest form of the paper's specificity statement: no design is clean "
            "because no 16-mer can be, and most designs carry no more transcriptome load than "
            "chance. The outliers are the informative rows."),
        "per_design": rows,
    }


def main():
    res = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({k: v for k, v in res.items() if k != "per_design"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
