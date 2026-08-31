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

#: ⭐ THE SECOND SET EXISTS SO NEITHER FIGURE LOSES ITS HOME (round 8).
#: 68.4% is the coverage of the TWO reagents the papers name, and the extended report and SI cite it
#: in four places. A third design at a published breakpoint — EWSR1 exon 13, the type-5 transcript,
#: "the second most common (type 5; two cases)" in the same sentence of PMID 12378528 that supplies
#: the exon-12 count — is already designed and screened, and adding it raises stated coverage. Both
#: are true of different reagent sets, so both are emitted: replacing one with the other would strand
#: every document citing the figure it no longer computes.
WITH_THIRD_DESIGN = dict(BREAKPOINT_COHORT["arms"], **{
    "EWSR1_e13__NR4A3_e3": {"k": 2, "n": 15},
})


def wilson(k, n, z=1.96):
    """Wilson score interval, the repository's fixed convention for a proportion."""
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def _coverage(arm_map):
    """Point estimate and breakpoint-interval range for one reagent set."""
    n_cohort = PARTNER_COHORT["n"]
    arms = []
    point = lo = hi = 0.0

    # ⛔⛔ AGGREGATE WITHIN A PARTNER BEFORE TAKING A BOUND, AND BEFORE COUNTING ITS PREVALENCE.
    # With one arm per partner the two are the same thing, and they stop being the same the moment a
    # partner carries two reagent junctions. Summing a Wilson bound per arm gives
    # wilson(10,15) + wilson(2,15), which is WIDER than wilson(12,15) and ran past 100% on the first
    # three-arm draft (42.9-112.8%); and `partner_only` summed EWSR1's 46 once PER ARM, returning
    # 1.741 as a "fraction". Both are fixed by grouping first: one fraction and one interval per
    # partner, then one prevalence weight per DISTINCT partner.
    grouped = {}
    for junction, bp in arm_map.items():
        partner = junction.split("_")[0]
        g = grouped.setdefault(partner, {"k": 0, "n": bp["n"], "junctions": []})
        assert g["n"] == bp["n"], (
            f"{partner}: arms disagree on the within-partner denominator "
            f"({g['n']} vs {bp['n']}) — they must be read off the same cohort")
        g["k"] += bp["k"]
        g["junctions"].append(junction)

    for partner, g in grouped.items():
        n_partner = PARTNER_COHORT["counts"][partner]
        share = n_partner / n_cohort
        frac = g["k"] / g["n"]
        f_lo, f_hi = wilson(g["k"], g["n"])
        junction = ", ".join(g["junctions"])
        bp = {"k": g["k"], "n": g["n"]}
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

    partner_only = sum(PARTNER_COHORT["counts"][p] for p in grouped) / n_cohort
    return arms, point, lo, hi, partner_only


def build():
    arms, point, lo, hi, partner_only = _coverage(BREAKPOINT_COHORT["arms"])
    third_arms, t_point, t_lo, t_hi, _ = _coverage(WITH_THIRD_DESIGN)

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
        "if_a_third_published_breakpoint_were_added": {
            "_what": ("The same arithmetic over a THIRD design at EWSR1 exon 13 — the type-5 "
                      "transcript, 'the second most common (type 5; two cases)' in the same "
                      "sentence of PMID 12378528 that supplies the exon-12 count. That design is "
                      "already in the panel and already screened; this block prices what naming it "
                      "would buy, and asserts nothing about whether it should be named."),
            "⛔_not_the_coverage_of_the_named_reagents": (
                "The papers name TWO reagents and their coverage is the `coverage` block above. "
                "This block is a THREE-reagent set and must never be quoted as the coverage of the "
                "two, which is the substitution that would strand every document citing 68.4%."),
            "reagent_junctions": sorted(WITH_THIRD_DESIGN),
            "arms": third_arms,
            "point_estimate": round(t_point, 4),
            "percent": round(100 * t_point, 1),
            "range_from_breakpoint_intervals": [round(t_lo, 4), round(t_hi, 4)],
            "percent_range": [round(100 * t_lo, 1), round(100 * t_hi, 1)],
            "gain_percentage_points": round(100 * (t_point - point), 1),
            "why_it_is_not_named_in_the_papers": (
                "This junction is third by reported prevalence and the selection takes the first "
                "two. That is the papers' own stated reason and it is the only one."),
            "⚠_the_reason_this_field_used_to_give_is_withdrawn": (
                "Until 2026-08-31 this field read: \"It carries no test article: none of the five "
                "in the ASO papers' section 4 spans EWSR1 exon 13 to NR4A3 exon 3, so naming it "
                "would put a reagent in front of a laboratory with nothing to test it in.\" The "
                "papers' test-articles section now argues that under the parsimonious reading — a "
                "donor joined to NR4A3's non-coding exon 2 sits upstream of that gene's initiation "
                "codon and yields no chimeric transcription factor — USZ20-EMC1 carries EWSR1 exon "
                "13 joined to exon 3, which is THIS design's junction. So a test article for it "
                "may well exist, and the retired sentence said the opposite INSIDE the deposit "
                "both papers cite. ⛔ THIS DOES NOT PROMOTE THE DESIGN: that reading is an "
                "inference and not a determination — the source report carries no sequenced "
                "exon-exon boundary, no transcript accession and no junction sequence — so it "
                "removes a reason rather than supplying one. Retained rather than deleted "
                "(CLAUDE.md rule 1.2); found by round 26's arithmetic seat."),
        },
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
