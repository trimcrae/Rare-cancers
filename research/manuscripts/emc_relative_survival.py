#!/usr/bin/env python3
"""Relative survival for EMC: disease-attributable mortality without a cause of death.

⭐ WHY THIS EXISTS, AND WHY IT IS THE PAPER'S METHODOLOGICAL SPINE.

The terminal-event corpus establishes that the published record of this disease usually
does not say how its patients died: of 52 classified deaths in the open-access EMC
literature, fewer than a third carry any named mechanism. Every disease-specific survival
figure in that literature therefore rests on somebody having decided a cause, by an
instrument nobody reports.

Relative survival does not need that decision. It compares a cohort's OBSERVED all-cause
survival against the survival EXPECTED for people of the same age and sex in the general
population, and attributes the shortfall to the disease. No individual is ever assigned a
cause. So the defect the corpus documents and the method used to work around it are the
same argument, which is why they belong in one paper.

    relative survival  R(t) = S_observed(t) / S_expected(t)
    excess mortality        = 1 - R(t)
    competing mortality     = all-cause mortality - excess mortality

⚠ WHAT THIS IS AND IS NOT. This is the Ederer II expected-survival convention applied to
PUBLISHED SUMMARY SURVIVAL at fixed horizons -- not to patient-level data, which does not
exist outside the original centres. A full Ederer II estimator matches expected survival
to each patient's own age and sex at each moment of follow-up; with only a cohort median
age and a sex ratio, this computes the expected survival of a synthetic cohort with those
characteristics. That approximation is stated in the output, and it is the single largest
methodological weakness here.

⛔ AND RELATIVE SURVIVAL IS NOT CAUSE OF DEATH. It estimates mortality in EXCESS of
background, which includes deaths caused by the disease, deaths caused by its treatment,
and any elevation in other-cause mortality among people who have it. It replaces one
assumption with a better-characterised one; it does not remove assumptions.

⭐ THE REASON TO RUN IT ANYWAY: it is INDEPENDENT of the cause-split. If a method that
never touches a cause of death lands near a method built entirely out of causes of death,
that convergence is evidence neither could supply alone.

Inputs:  research/manuscripts/emc-mortality-decomposition-inputs.json
         research/literature/emc-host-factor-probe.json   (the life table)
Output:  research/manuscripts/emc-relative-survival.json
"""

from __future__ import annotations

import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
INPUTS = ROOT / "research/manuscripts/emc-mortality-decomposition-inputs.json"
LIFETABLE = ROOT / "research/literature/emc-host-factor-probe.json"
DECOMP = ROOT / "research/manuscripts/emc-mortality-decomposition.json"
OUT = ROOT / "research/manuscripts/emc-relative-survival.json"

# WHO GHO publishes nMx in five-year bands. A cohort starting at 55 passes through
# 55-59 then 60-64, so a ten-year horizon needs exactly the two bands the life-table
# fetch retrieved.
BANDS = [("AGEGROUP_YEARS55-59", 5.0), ("AGEGROUP_YEARS60-64", 5.0)]


def expected_survival(rates: dict, male_fraction: float, years: float) -> dict:
    """Expected survival of a synthetic cohort, by sex, blended.

    ⛔ nMx IS A RATE, NOT A PROBABILITY. Survival over a band of width w at rate m is
    exp(-m*w). Treating nMx as a five-year probability -- which an earlier version of the
    life-table fetch did -- understates mortality by roughly a factor of four and would
    make the disease look responsible for almost every death.
    """
    per_sex = {}
    for sex in ("male", "female"):
        remaining, surv = years, 1.0
        used = []
        for band, width in BANDS:
            if remaining <= 0:
                break
            take = min(width, remaining)
            m = rates[sex][band]["raw_value"]
            surv *= math.exp(-m * take)
            used.append({"band": band, "years_in_band": take, "rate": m})
            remaining -= take
        if remaining > 0:
            return {"status": "HORIZON_EXCEEDS_LIFE_TABLE",
                    "why": (f"{years} years from the cohort's start age needs bands beyond "
                            f"those retrieved; no expected survival is asserted rather than "
                            f"extrapolating the last rate forward.")}
        per_sex[sex] = {"expected_survival": surv, "bands_used": used}
    blended = (male_fraction * per_sex["male"]["expected_survival"]
               + (1 - male_fraction) * per_sex["female"]["expected_survival"])
    return {"status": "OK", "by_sex": per_sex, "blended_expected_survival": blended}


def relative_survival(observed: float, expected: float) -> dict:
    r = observed / expected
    return {
        "observed_all_cause_survival": round(observed, 4),
        "expected_background_survival": round(expected, 4),
        "relative_survival": round(r, 4),
        "excess_mortality_pct": round(100 * (1 - r), 1),
        "all_cause_mortality_pct": round(100 * (1 - observed), 1),
        "competing_mortality_pct": round(100 * ((1 - observed) - (1 - r)), 1),
        "competing_share_of_deaths_pct": (
            round(100 * ((1 - observed) - (1 - r)) / (1 - observed), 1)
            if observed < 1 else None),
        "relative_survival_above_one": r > 1.0,
        "note_if_above_one": (
            "Relative survival above 1 means the cohort out-lived the general population, which "
            "for a cancer cohort signals selection -- referral centres see fitter patients -- "
            "rather than a protective disease. Reported, never clipped."
        ) if r > 1.0 else None,
    }


def main() -> int:
    spec = json.loads(INPUTS.read_text(encoding="utf-8"))
    lt = json.loads(LIFETABLE.read_text(encoding="utf-8"))["background_mortality"]
    if lt.get("status") != "OK":
        print(f"life table not usable (status {lt.get('status')})", file=sys.stderr)
        return 2

    rates = lt["bands_used"]
    male_fraction = spec["background_mortality"]["cohort_sex_ratio_male"]
    start_age = spec["background_mortality"]["cohort_age_median"]

    rows = []
    for s in spec["series"]:
        for horizon, observed in (s.get("overall_survival") or {}).items():
            years = float(horizon)
            exp = expected_survival(rates, male_fraction, years)
            if exp["status"] != "OK":
                rows.append({"series": s["key"], "label": s["label"],
                             "horizon_years": years, "status": exp["status"],
                             "why": exp["why"]})
                continue
            r = relative_survival(observed, exp["blended_expected_survival"])
            r.update({"series": s["key"], "label": s["label"], "n": s.get("n"),
                      "horizon_years": years, "status": "OK"})
            rows.append(r)

    # ⛔ TWO KINDS OF SERIES MUST LEAVE THE POOLED BAND, AND FOR DIFFERENT REASONS.
    #
    #   (a) relative survival above 1 -- the cohort out-lived the general population, so
    #       there is no excess to apportion. A selection statement, not a disease one.
    #
    #   (b) relative survival at or above 0.99 -- numerically unstable rather than wrong.
    #       The competing share divides a near-zero excess by a small all-cause mortality,
    #       so a rounding difference in the third decimal swings the answer by tens of
    #       percentage points. The Japanese series at 10 years produces 93.7% this way,
    #       from an excess mortality of 0.8%. Publishing that inside a band would let one
    #       unstable ratio set the band's edge.
    #
    # Both are EXCLUDED AND COUNTED, never silently dropped.
    UNSTABLE_RS = 0.99
    excluded = []
    ok = []
    for r in rows:
        if r.get("status") != "OK" or r.get("competing_share_of_deaths_pct") is None:
            continue
        if r["relative_survival_above_one"]:
            excluded.append({"series": r["series"], "horizon_years": r["horizon_years"],
                             "relative_survival": r["relative_survival"],
                             "why": "relative survival above 1 -- cohort out-lived the "
                                    "general population, a selection signal"})
        elif r["relative_survival"] >= UNSTABLE_RS:
            excluded.append({"series": r["series"], "horizon_years": r["horizon_years"],
                             "relative_survival": r["relative_survival"],
                             "competing_share_it_would_have_contributed":
                                 r["competing_share_of_deaths_pct"],
                             "why": f"relative survival >= {UNSTABLE_RS}: the competing share "
                                    f"divides a near-zero excess by a small all-cause mortality "
                                    f"and is numerically unstable, not informative"})
        else:
            ok.append(r)
    shares = sorted(r["competing_share_of_deaths_pct"] for r in ok)
    median_share = shares[len(shares) // 2] if shares else None

    # The independent comparator: the cause-split, which needs a cause of death for every
    # patient and which this method needs none of.
    decomp = json.loads(DECOMP.read_text(encoding="utf-8"))
    direct = decomp.get("direct_cause_split") or []
    direct_shares = [d["competing_share_of_deaths_pct"] for d in direct]

    payload = {
        "_readme": (
            "Relative survival for EMC. Estimates mortality in excess of the general population, "
            "which is disease-attributable mortality obtained WITHOUT assigning a cause of death to "
            "anyone -- the method that answers the defect documented in emc-terminal-events.json, "
            "where fewer than a third of deaths in the published record carry a named mechanism. "
            "⚠ Applied to PUBLISHED SUMMARY SURVIVAL with a cohort median age and sex ratio, not to "
            "patient-level data, so the expected-survival term is that of a synthetic cohort rather "
            "than a true Ederer II match. That approximation is this analysis's largest weakness. "
            "⛔ Excess mortality is not cause of death: it includes deaths from the disease, from its "
            "treatment, and any elevation in other-cause mortality among people who have it."
        ),
        "generated_by": "research/manuscripts/emc_relative_survival.py",
        "method": "Ederer II convention, applied to summary survival at fixed horizons",
        "life_table": {
            "source": lt.get("source"),
            "indicator": lt.get("indicator_name_as_published"),
            "start_age": start_age,
            "male_fraction": male_fraction,
            "⛔_rate_not_probability": (
                "nMx is an age-specific death RATE. Survival over a band of width w is exp(-m*w). "
                "An earlier fetch treated it as a five-year probability and understated background "
                "mortality roughly fourfold, which would have attributed almost every death to EMC."
            ),
        },
        "series": rows,
        "convergence": {
            "⭐_why_this_matters": (
                "Relative survival and the cause-split are INDEPENDENT. One never touches a cause of "
                "death; the other is built entirely out of causes of death. Agreement between them is "
                "evidence neither could produce alone, and disagreement would tell us the cause "
                "attribution in the source papers is unreliable -- which is a publishable finding "
                "either way."
            ),
            "relative_survival_competing_share_pct_range": (
                [shares[0], shares[-1]] if shares else None),
            "relative_survival_competing_share_pct_median": median_share,
            "relative_survival_series_pooled": len(ok),
            "relative_survival_series_excluded": excluded,
            "cause_split_competing_share_pct": direct_shares or None,
            "cause_split_overall_competing_share_pct": (
                decomp.get("direct_cause_split_pooled") or {}
            ).get("competing_share_of_deaths_pct"),
            "reading": (
                "Compare the median of the relative-survival series against the cause-split. They "
                "share no input: one is published all-cause survival divided by a national life "
                "table, the other is counts of patients a registry assigned a cause to. Neither can "
                "be derived from the other, so agreement is convergent evidence and disagreement "
                "would indicate the cause attribution in the source papers is unreliable."
            ),
        },
        "limits": [
            "Expected survival is computed for a synthetic cohort at the median age and sex ratio, not matched to each patient -- the Ederer II approximation, and the largest weakness here.",
            "The life table is a single country and year (US, 2021) applied to cohorts from Japan, Sweden, China, Italy and the United States across five decades. Background mortality differs across all of those.",
            "Published summary survival is read at horizons the original papers chose to report, so the horizons are not a design.",
            "Excess mortality attributes to the disease any elevation in other-cause mortality among its patients, including treatment-caused death, which is a category the cause-split counts separately.",
            "A referral-centre cohort is fitter than the general population, which biases expected survival DOWNWARD relative to the truth and therefore biases excess mortality UPWARD -- against this analysis's own conclusion.",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {OUT.relative_to(ROOT)}")
    for r in rows:
        if r.get("status") != "OK":
            print(f"  {r['label'][:44]:<46} {r['horizon_years']:>4.0f}y  {r['status']}")
            continue
        flag = "  <- relative survival > 1" if r["relative_survival_above_one"] else ""
        print(f"  {r['label'][:44]:<46} {r['horizon_years']:>4.0f}y  "
              f"RS={r['relative_survival']:.3f}  excess={r['excess_mortality_pct']:>5.1f}%  "
              f"competing share={r['competing_share_of_deaths_pct']}%{flag}")
    for e in excluded:
        print(f"  EXCLUDED {e['series']} @{e['horizon_years']:.0f}y (RS={e['relative_survival']}): "
              f"{e['why'][:60]}")
    if shares:
        print(f"\n  relative-survival competing share: {shares[0]}-{shares[-1]}%, "
              f"median {median_share}% over {len(ok)} series-horizons")
    if direct_shares:
        print(f"  cause-split competing share:       {direct_shares}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
