#!/usr/bin/env python3
"""What fraction of molecularly confirmed EMC could the two named reagents actually engage?

⛔ WHY THIS EXISTS, AND WHAT IT CORRECTS. The submission manuscript said the two reagents cover
"about 95% of molecularly confirmed cases", in the abstract and again in section 5.1. That number is
wrong, and the manuscript contained everything needed to see it was wrong. 95% is PARTNER
prevalence — 79% EWSR1 plus 16% TAF15 of 58 molecularly confirmed cases (PMID 36948401). The
reagents are not partner-specific. They are JUNCTION-specific: every design in the paper is a
16-mer spanning one exon pair, section 5.4 says so in terms ("every design here is specific to one
exon pair, and none is valid for an unverified junction"), and section 3.2 shows what happens when
the exon assumption fails — the multi-partner oligonucleotide shares a single donor base with the
TAF15 junction patients are actually reported to carry.

So the partner prevalence has to be DISCOUNTED BY THE BREAKPOINT DISTRIBUTION, and the discount is
published: PMID 12378528 sequenced 18 EMCs and found EWSR1 exon 12 to NR4A3 exon 3 in 10 of its 15
EWSR1-rearranged tumours, and TAF15 exon 6 to NR4A3 exon 3 in all three of its TAF15-rearranged
tumours. That is roughly two thirds, not 95%.

⚠ THE ERROR WAS NOT ARITHMETIC, IT WAS A DENOMINATOR SWAP, which is why no check caught it. Every
figure in the sentence was individually true and correctly cited; they were multiplied against the
wrong population. Raised by external review, 2026-08-15.

WHAT THIS IS NOT.
  · Not a coverage measurement. No patient in either cohort was screened with either reagent, and
    nothing here says a reagent that matches a junction works against it.
  · Not a pooled estimate in the sense POLICY-evidence.md governs. The two inputs come from
    different cohorts and are combined MULTIPLICATIVELY, not pooled: partner prevalence from a
    58-case series, breakpoint distribution from an 18-case series. Section 2.3 of that policy is
    about double-counting patients across overlapping cohorts and does not reach this.
  · Not free of an assumption, and the assumption is stated in the artifact: that the breakpoint
    distribution WITHIN EWSR1-rearranged tumours is the same in the 58-case cohort as in the
    18-case one. Nothing here tests that, and the two cohorts are 21 years apart.
  · Not a small-denominator problem that a wider interval fixes. The TAF15 arm rests on three
    tumours. Three.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "aso", "fusion-junction-aso-reagent-coverage.json")

#: PMID 36948401 (Huang 2023, Modern Pathology) — 58 FISH-confirmed EMCs. Counts, not percentages,
#: so the arithmetic below is not carrying a rounding of someone else's rounding.
PARTNER_COHORT = {
    "pmid": "36948401",
    "n": 58,
    "counts": {"EWSR1": 46, "TAF15": 9, "TCF12": 2, "no_identified_partner": 1},
    "verbatim": ("fusion distribution reported as 46 EWSR1::NR4A3 (79%), 9 TAF15::NR4A3 (16%), "
                 "2 TCF12::NR4A3 (3%), 1 NR4A3-rearranged with no identified partner (2%)"),
    "source": "research/literature/no-wet-lab-archetypes-2026-08-12.json",
}

#: PMID 12378528 (Panagopoulos 2002, Genes Chromosomes Cancer) — 18 EMCs, breakpoints by RT-PCR and
#: sequencing. The verbatim sentences are in research/manuscripts/aso/lit-targets-aso-verify.json.
BREAKPOINT_COHORT = {
    "pmid": "12378528",
    "n": 18,
    "verbatim": ("Fifteen cases had an EWS/CHN fusion transcript and three had an RBP56/CHN "
                 "transcript. The most frequent EWS/CHN transcript (type 1; 10 tumors), involved "
                 "fusion of EWS exon 12 with CHN exon 3 ... In all tumors with RBP56/CHN fusion, "
                 "exon 6 of RBP56 was fused to exon 3 of CHN."),
    "source": "research/manuscripts/aso/lit-targets-aso-verify.json",
    "arms": {
        # reagent junction -> (tumours with THIS junction, tumours rearranged for that partner)
        "EWSR1_e12__NR4A3_e3": {"k": 10, "n": 15},
        "TAF15_e6__NR4A3_e3": {"k": 3, "n": 3},
    },
}


def wilson(k, n, z=1.96):
    """Wilson score interval, the repository's fixed convention for a proportion."""
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def build():
    n_cohort = PARTNER_COHORT["n"]
    arms = []
    point = lo = hi = 0.0
    for junction, bp in BREAKPOINT_COHORT["arms"].items():
        partner = junction.split("_")[0]
        n_partner = PARTNER_COHORT["counts"][partner]
        share = n_partner / n_cohort
        frac = bp["k"] / bp["n"]
        f_lo, f_hi = wilson(bp["k"], bp["n"])
        arms.append({
            "reagent_junction": junction,
            "partner": partner,
            "partner_share_of_cohort": round(share, 4),
            "partner_share_counts": f"{n_partner}/{n_cohort}",
            "partner_share_wilson95": wilson(n_partner, n_cohort),
            "breakpoint_fraction_within_partner": round(frac, 4),
            "breakpoint_fraction_counts": f"{bp['k']}/{bp['n']}",
            "breakpoint_fraction_wilson95": [f_lo, f_hi],
            "contribution_to_coverage": round(share * frac, 4),
            "contribution_range": [round(share * f_lo, 4), round(share * f_hi, 4)],
        })
        point += share * frac
        lo += share * f_lo
        hi += share * f_hi

    partner_only = sum(PARTNER_COHORT["counts"][a["partner"]] for a in arms) / n_cohort

    return {
        "_what": ("The fraction of molecularly confirmed EMC the two named reagents could engage, "
                  "with the partner prevalence discounted by the published breakpoint "
                  "distribution — because the reagents are junction-specific, not "
                  "partner-specific."),
        "_why": ("The manuscript claimed 'about 95% of molecularly confirmed cases' in its abstract "
                 "and section 5.1. 95% is PARTNER prevalence and the reagents are junction-"
                 "specific, which the manuscript states itself in section 5.4. Raised by external "
                 "review, 2026-08-15."),
        "_what_this_is_not": [
            "Not a coverage measurement. No patient was screened with either reagent, and a "
            "sequence that matches a junction is not thereby active against it.",
            "Not a pooled proportion. Two cohorts, combined multiplicatively rather than pooled; "
            "POLICY-evidence.md section 2.3 governs double-counted patients and does not reach a "
            "product of a prevalence and a conditional fraction.",
            "Not assumption-free. It assumes the breakpoint distribution within EWSR1-rearranged "
            "tumours is the same in the 58-case cohort as in the 18-case one, 21 years apart. "
            "Nothing here tests that.",
            "Not rescued by the interval. The TAF15 arm rests on three tumours.",
        ],
        "_cost": "$0 — arithmetic over two retrieved bibliographic records.",
        "inputs": {"partner_prevalence": PARTNER_COHORT, "breakpoint_distribution":
                   BREAKPOINT_COHORT},
        "arms": arms,
        "coverage": {
            "point_estimate": round(point, 4),
            "percent": round(100 * point, 1),
            "plain_language": "roughly two thirds",
            "range_from_breakpoint_intervals": [round(lo, 4), round(hi, 4)],
            "percent_range": [round(100 * lo, 1), round(100 * hi, 1)],
            "_how_the_range_is_built": (
                "Coverage is increasing in both breakpoint fractions, so the endpoints compose "
                "exactly when each fraction is taken to its own Wilson bound. That treats the two "
                "arms as moving together and is therefore CONSERVATIVE — wider than a treatment "
                "that let them vary independently. Partner shares are held at their point "
                "estimates because they rest on 58 cases against 15 and 3; their own intervals "
                "are reported per arm so a reader can see that they are not what drives the "
                "width."),
            "_the_superseded_figure": {
                "value": round(100 * partner_only, 1),
                "what_it_actually_is": ("partner prevalence — the ceiling a reagent set could "
                                        "reach if every patient's breakpoint fell at the modelled "
                                        "exon pair"),
                "why_it_was_wrong_here": ("the reagents are specific to one exon pair each; "
                                          "section 3.2 of the manuscript shows a design missing "
                                          "the reported TAF15 junction by all but a single donor "
                                          "base"),
            },
        },
    }


def main(argv=None):
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    art = build()
    new = json.dumps(art, indent=1, sort_keys=False) + "\n"
    if "--check" in argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != new:
            print("fusion-junction-aso-reagent-coverage.json is stale; re-run without --check",
                  file=sys.stderr)
            return 1
        print("reagent-coverage artifact is current")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(new)
    c = art["coverage"]
    print(f"wrote {os.path.basename(OUT)}: {c['percent']}% "
          f"({c['percent_range'][0]}-{c['percent_range'][1]}%), against the superseded "
          f"{c['_the_superseded_figure']['value']}%", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
