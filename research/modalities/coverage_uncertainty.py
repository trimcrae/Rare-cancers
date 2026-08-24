#!/usr/bin/env python3
"""
What the population-coverage number's uncertainty ACTUALLY is, on three axes the pooled
point estimate does not carry.

⛔ WHY THIS EXISTS. `hla_coverage.py` reports a Wilson 95% CI on each pooled allele frequency and
propagates it into a coverage interval. That interval was withdrawn from the manuscript, correctly:
it is the sampling error of a frequency pooled over hundreds of unrelated study populations, and
sampling error is not the uncertainty a reader of a coverage figure cares about. Withdrawing it left
the paper reporting a bare point estimate on a step function, which eight successive external
reviews of `aixiv.260822.000005` named as a weakness — most sharply as "the lack of a confidence
interval means there is no sense of the variance of the final estimate" and "the alternative of
reporting point estimates on a step function is also statistically weak."

This module answers that WITHOUT reintroducing a statistic that does not mean what it looks like.
It computes three things, each of which is the honest answer to a different question:

  1. THE WITHIN-LOCUS EXACT FORM. The published formula is C = 1 - prod_a (1 - f_a)^2 over the
     presenting ALLELES. That treats two alleles at the same locus as independent, and they are not:
     a diploid genome carries at most two alleles at HLA-B, so B*07:02 and B*15:01 COMPETE for the
     same two slots. Under Hardy-Weinberg at the locus the exact non-carrier probability is
     (1 - sum_a f_a)^2, not prod_a (1 - f_a)^2, and because (1 - f1 - f2) < (1 - f1)(1 - f2) the
     published form is a LOWER bound rather than an approximation of unknown sign. The direction is
     the point: the paper's headline coverage figure cannot be too high for this reason.

  2. DISTRIBUTION-FREE BOUNDS ACROSS LOCI (Fréchet–Hoeffding). The remaining assumption is
     independence BETWEEN loci, which linkage disequilibrium violates — two reviews said so and
     neither the paper nor they could say by how much. It is boundable exactly and without data:
     for events with marginal probabilities p_L, P(union) lies in
     [max_L p_L, min(1, sum_L p_L)] whatever the dependence structure. Positive LD (carriers
     clustering in the same people) pushes coverage toward the lower bound; negative LD toward the
     upper. That is a complete answer to "you assumed independence": the assumption is not load-
     bearing beyond an interval this reports, and the interval is exact rather than modelled.

  3. THE BETWEEN-POPULATION SPREAD, which is the uncertainty that actually bites. HLA frequencies
     differ by an order of magnitude between populations; the pooled figure is a 2N-weighted average
     over AFND's study populations and is not the coverage of any real clinic. So recompute C inside
     each AFND population from that population's OWN frequencies and report the empirical
     distribution.

     ⛔ AND ONLY IN POPULATIONS THAT MEASURED THE WHOLE PANEL. An allele absent from a population's
     AFND record was not measured there; scoring it zero manufactures a low-coverage population out
     of a reporting gap. Both readings are emitted — complete-panel populations (the estimate) and
     absent-as-zero over all populations (a floor) — and the count of each is stated, because the
     gap between them is itself the reader's warning about how much of the spread is biology and how
     much is coverage of the database.

Output: coverage-uncertainty.json
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from hla_coverage import (AFND_CITATION, AFND_TSV_URL, fetch)  # noqa: E402

COVERAGE = os.path.join(HERE, "hla-coverage.json")
OUT = os.path.join(HERE, "coverage-uncertainty.json")

#: A population's record has to be big enough that its own frequencies mean something. AFND
#: publishes samples down to a handful of individuals; a 20-person study's carrier frequency has a
#: sampling error wider than the between-population spread this module is trying to measure, which
#: would put the noise it is meant to exclude straight back into the distribution.
MIN_N = 50


def locus_of(allele):
    """`HLA-B*07:02` -> `B`; `DRB1*14:01` -> `DRB1`. The competing-slots grouping."""
    return allele.replace("HLA-", "").split("*", 1)[0]


def published_form(freqs):
    """C = 1 - prod_a (1 - f_a)^2, over alleles. The formula the manuscript prints."""
    non = 1.0
    for f in freqs.values():
        non *= (1.0 - f) ** 2
    return 1.0 - non


def per_locus_carrier(freqs):
    """`locus -> P(carry >=1 presenting allele AT that locus)`, exact under HWE at the locus."""
    by_locus = {}
    for allele, f in freqs.items():
        by_locus.setdefault(locus_of(allele), 0.0)
        by_locus[locus_of(allele)] += f
    #: A summed frequency can exceed 1 only through a data error; clamp so the square stays a
    #: probability and let the caller see the raw sum in the record.
    return {loc: 1.0 - (1.0 - min(s, 1.0)) ** 2 for loc, s in by_locus.items()}, by_locus


def within_locus_exact(freqs):
    """C = 1 - prod_L (1 - sum_{a in L} f_a)^2. Exact at each locus, independent ACROSS loci."""
    carriers, _ = per_locus_carrier(freqs)
    non = 1.0
    for p in carriers.values():
        non *= (1.0 - p)
    return 1.0 - non


def hardy_weinberg_free_bounds(summed_frequency):
    """Carrier frequency at ONE locus without assuming Hardy-Weinberg, given the allele frequency.

    ⛔ HWE IS THE ASSUMPTION UNDER THE ASSUMPTION, AND v1.9's REVIEWER NAMED IT: the within-locus
    "exact" form is exact only in the sense that it stops treating same-locus alleles as independent
    events — it still reads a carrier frequency off an allele frequency through (1 - p)^2, which is
    Hardy-Weinberg, and nothing here tests HWE. AFND publishes allele frequencies rather than genotype
    counts, so it cannot be tested from this source at all. It can be BOUNDED from the same source,
    exactly, which is the honest thing available.

    Write p for the summed frequency of the presenting alleles at the locus — a fraction of
    CHROMOSOMES. Every arrangement of those copies into people lies between two extremes:
      * every copy paired in a homozygote: each carrier holds two, so carriers = p;
      * no homozygotes at all: each carrier holds one, so carriers = min(1, 2p).
    Hardy-Weinberg's 1 - (1 - p)^2 = 2p - p^2 lies inside that interval for every p, near its top
    when p is small. So the HWE step is worth at most min(1, 2p) - p here, and a reader who rejects
    HWE outright can take the interval instead of the point.
    """
    p = min(max(summed_frequency, 0.0), 1.0)
    return p, min(1.0, 2.0 * p)


def frechet_bounds(freqs):
    """Exact bounds on the union under ANY dependence between loci (Fréchet–Hoeffding)."""
    carriers, _ = per_locus_carrier(freqs)
    p = list(carriers.values())
    if not p:
        return None, None
    return max(p), min(1.0, sum(p))


def intersection_bounds(p_a, p_b):
    """Exact bounds on P(A and B) given the two marginals, under ANY dependence (Fréchet).

    ⛔ THE COMBINED CD8-AND-CD4 FIGURE IS AN INTERSECTION, NOT A UNION, AND THE BOUNDS INVERT.
    §B4 multiplies the class I and class II coverages and then says the independence this assumes is
    "an approximation whose direction is not known without haplotype frequencies" — true, and the
    magnitude is boundable even though the direction is not. For an intersection the Fréchet bounds
    are [max(0, p_a + p_b - 1), min(p_a, p_b)], and the UPPER one is the useful half: a construct
    needing an allele of each class can never reach more patients than its scarcer arm alone,
    whatever the linkage between chromosome 6 loci. That ceiling holds without any haplotype data.
    """
    return max(0.0, p_a + p_b - 1.0), min(p_a, p_b)


def afnd_by_population(alleles):
    """`population -> {allele: f}` and `population -> n`, for the alleles asked about."""
    want = {a.replace("HLA-", ""): a for a in alleles}
    text = fetch(AFND_TSV_URL)
    if not text or "alleles_over_2n" not in text:
        return None, None
    import csv
    import io
    freqs, sizes = {}, {}
    for row in csv.DictReader(io.StringIO(text), delimiter="\t"):
        if row.get("group") != "hla":
            continue
        raw = row.get("allele")
        if raw not in want:
            continue
        try:
            af, n = float(row["alleles_over_2n"]), int(row["n"])
        except (ValueError, TypeError, KeyError):
            continue
        if n <= 0 or not (0.0 <= af <= 1.0):
            continue
        pop = row.get("population", "")
        #: One population can appear more than once for one allele across AFND studies. Pool by
        #: sample size rather than taking whichever row parsed last.
        key = (pop, want[raw])
        prev = freqs.setdefault(pop, {})
        if want[raw] in prev:
            n0 = sizes.get(key, 0)
            prev[want[raw]] = (prev[want[raw]] * n0 + af * n) / (n0 + n)
            sizes[key] = n0 + n
        else:
            prev[want[raw]] = af
            sizes[key] = n
    pop_n = {}
    for (pop, _allele), n in sizes.items():
        pop_n[pop] = max(pop_n.get(pop, 0), n)
    return freqs, pop_n


def quantiles(xs):
    """Min, quartiles, median and max of a sorted sample, by linear interpolation."""
    if not xs:
        return {}
    s = sorted(xs)

    def q(p):
        if len(s) == 1:
            return s[0]
        i = p * (len(s) - 1)
        lo = int(i)
        hi = min(lo + 1, len(s) - 1)
        return s[lo] + (s[hi] - s[lo]) * (i - lo)

    return {"min": round(s[0], 4), "p25": round(q(0.25), 4), "median": round(q(0.5), 4),
            "p75": round(q(0.75), 4), "max": round(s[-1], 4), "n": len(s)}


def analyse(name, freqs, by_pop, pop_n):
    """Every reading for ONE presenting-allele set."""
    carriers, sums = per_locus_carrier(freqs)
    lo, hi = frechet_bounds(freqs)
    published = published_form(freqs)
    exact = within_locus_exact(freqs)

    complete, floor = [], []
    n_complete = 0
    for pop, fs in by_pop.items():
        if pop_n.get(pop, 0) < MIN_N:
            continue
        here = {a: fs.get(a, 0.0) for a in freqs}
        floor.append(within_locus_exact(here))
        if all(a in fs for a in freqs):
            complete.append(within_locus_exact(here))
            n_complete += 1

    hwe_free = {loc: hardy_weinberg_free_bounds(s) for loc, s in sums.items()}
    #: The union under BOTH freedoms at once: no Hardy-Weinberg inside a locus, no independence
    #: between them. Lower is the largest locus lower bound (a union is at least any one of its
    #: parts); upper is the capped sum (a union is at most the sum of its parts).
    joint_lo = max((lo for lo, _hi in hwe_free.values()), default=0.0)
    joint_hi = min(1.0, sum(hi for _lo, hi in hwe_free.values()))

    return {
        "alleles": sorted(freqs),
        "pooled_allele_frequencies": {a: round(f, 5) for a, f in sorted(freqs.items())},
        "per_locus_carrier_frequency": {loc: round(p, 4) for loc, p in sorted(carriers.items())},
        "per_locus_summed_allele_frequency": {loc: round(s, 5) for loc, s in sorted(sums.items())},
        "coverage_published_form": round(published, 4),
        "coverage_within_locus_exact": round(exact, 4),
        "understatement_of_published_form_pp": round(100 * (exact - published), 2),
        "ld_bounds_across_loci": [round(lo, 4) if lo is not None else None,
                                  round(hi, 4) if hi is not None else None],
        "ld_bound_width_pp": round(100 * (hi - lo), 2) if lo is not None else None,
        "per_locus_carrier_bounds_without_hardy_weinberg": {
            loc: [round(b[0], 4), round(b[1], 4)] for loc, b in sorted(hwe_free.items())},
        "bounds_without_hardy_weinberg_or_independence": [round(joint_lo, 4), round(joint_hi, 4)],
        "between_population": {
            "complete_panel": quantiles(complete),
            "absent_scored_zero_floor": quantiles(floor),
            "populations_measuring_every_presenting_allele": n_complete,
            "populations_with_any_measurement": len(floor),
        },
        "_name": name,
    }


def main():
    with open(COVERAGE, encoding="utf-8") as fh:
        cov = json.load(fh)
    g = cov["global"]
    afs = {a: v["allele_frequency"] for a, v in g["allele_frequencies"].items()}

    sets = {
        "class_i_any_strong_binder": g["all_strong_binder_alleles"],
        "class_i_e7e3_public": g["e7e3_public_epitope_alleles"],
        "class_ii_cd4_helper": g["class_ii_cd4_helper_alleles"],
    }
    every = sorted({a for s in sets.values() for a in s})
    by_pop, pop_n = afnd_by_population(every)
    if by_pop is None:
        raise SystemExit("AFND could not be fetched — no uncertainty reading is possible, and an "
                         "empty artifact would read as a measured absence of spread. Nothing "
                         "written.")

    out = {
        "_note": __doc__.strip().split("\n\n")[0],
        "_source": AFND_CITATION,
        "_source_url": AFND_TSV_URL,
        "_min_population_n": MIN_N,
        "_reading_order": [
            "coverage_published_form is what the manuscript prints.",
            "coverage_within_locus_exact corrects the same-locus independence error; it is >= the "
            "published form, so the published figure cannot be too high for that reason.",
            "ld_bounds_across_loci hold under ANY linkage disequilibrium between loci and are "
            "exact, not modelled.",
            "between_population is the empirical spread of the same quantity recomputed inside "
            "each AFND study population, and is the widest of the three by a large margin.",
        ],
        "sets": {},
    }
    for name, alleles in sets.items():
        if not alleles:
            continue
        freqs = {a: afs[a] for a in alleles if a in afs}
        if not freqs:
            continue
        out["sets"][name] = analyse(name, freqs, by_pop, pop_n)

    #: The combined CD8-and-CD4 eligibility fraction, which §B4 computes as a product. Read the two
    #: arms out of the SAME artifact the manuscript quotes them from, so the bound cannot come to be
    #: about a different pair of numbers than the product it bounds.
    c_i, c_ii = g["coverage_any_strong_binder_allele"], g["coverage_cd4_classii"]
    lo, hi = intersection_bounds(c_i, c_ii)
    out["combined_class_i_and_class_ii"] = {
        "_note": "An INTERSECTION: the fraction carrying >=1 presenting allele of each class. The "
                 "manuscript computes it as a product, which assumes independence between HLA-A/B "
                 "and DRB1 on chromosome 6. These bounds hold under any dependence whatever.",
        "coverage_class_i": round(c_i, 4),
        "coverage_class_ii": round(c_ii, 4),
        "product_under_independence": round(c_i * c_ii, 4),
        "bounds_under_any_dependence": [round(lo, 4), round(hi, 4)],
        "ceiling_is_the_scarcer_arm": round(hi, 4),
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=False)
        fh.write("\n")
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}")
    comb = out["combined_class_i_and_class_ii"]
    print(f"  combined CD8 and CD4: product {comb['product_under_independence']:.4f}; "
          f"bounds under any dependence {comb['bounds_under_any_dependence']}")
    for name, rec in out["sets"].items():
        bp = rec["between_population"]["complete_panel"]
        print(f"  {name}: published {rec['coverage_published_form']:.4f} -> exact "
              f"{rec['coverage_within_locus_exact']:.4f} "
              f"(+{rec['understatement_of_published_form_pp']:.2f} pp); "
              f"LD bounds {rec['ld_bounds_across_loci']}; "
              f"between-population median {bp.get('median')} "
              f"[{bp.get('min')}, {bp.get('max')}] over n={bp.get('n')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
