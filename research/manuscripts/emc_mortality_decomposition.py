#!/usr/bin/env python3
"""Decompose EMC mortality into disease deaths and everything else.

THE QUESTION. Every one of this repository's sixty-eight treatment routes is aimed at
the same event: a death caused by extraskeletal myxoid chondrosarcoma. None of them has
ever asked what fraction of the deaths after an EMC diagnosis that event actually is.
For a disease whose ten-year disease-specific survival is around 85 percent and whose
patients are diagnosed in their fifties and sixties, the question is not rhetorical --
the answer bounds what a perfect antitumour therapy could buy, and it names a second
population of deaths that no route on the board is pointed at.

WHAT THIS COMPUTES.

  1. A per-series and pooled decomposition of all-cause mortality into the part
     attributable to EMC and the part attributable to everything else, at 5 and 10
     years, from the survival figures already curated and cited in
     research/data/emc-clinical-registry.json.

  2. The ANTITUMOUR CEILING: the number of percentage points of ten-year overall
     survival that a therapy curing every EMC death would add. This is an upper bound
     on the entire antitumour portfolio, and it is computed the only way it can be --
     as the disease-specific mortality that exists to be removed.

  3. The COMPETING SHARE: of the patients dead within a horizon, what fraction died of
     something other than EMC. This is the population the portfolio does not address.

  4. A BACKGROUND-MORTALITY PLAUSIBILITY CHECK, when a life table is available: is the
     observed gap the size an ordinary cohort of this age and sex would show anyway?
     A gap much LARGER than background would mean the two studies were not comparable
     rather than that patients died of other causes, and the decomposition would be an
     artifact. Reported as NOT RUN when no life table has been fetched -- an absent
     reading is not a reading of absence (CLAUDE.md section 4).

WHAT THIS IS NOT. It is not a survival model, not a competing-risks regression, and not
a statement about any individual. The arithmetic is subtraction of published summary
percentages across heterogeneous studies of different eras, countries and selection.
Its output is a BAND with its inputs attached, and every band carries the pairing that
produced it so a reader can see which numbers came from the same patients and which did
not.

⚠ THE ONE DIRECTIONAL BIAS, STATED BECAUSE IT FAVOURS THIS ANALYSIS'S OWN CONCLUSION.
A disease-specific survival curve estimated by censoring other-cause deaths overstates
the cumulative incidence of disease death in the presence of competing risks. So
(1 - DSS) is an OVER-estimate of EMC's share and the competing share computed here is
an UNDER-estimate. The direction is conservative for the claim being made, which is the
only reason it is tolerable to publish the subtraction at all.

Inputs:  research/manuscripts/emc-mortality-decomposition-inputs.json
         research/data/emc-clinical-registry.json  (the one home of every figure)
Output:  research/manuscripts/emc-mortality-decomposition.json
"""

from __future__ import annotations

import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
INPUTS = ROOT / "research/manuscripts/emc-mortality-decomposition-inputs.json"
REGISTRY = ROOT / "research/data/emc-clinical-registry.json"
OUT = ROOT / "research/manuscripts/emc-mortality-decomposition.json"


# ---------------------------------------------------------------------------
# Provenance: every figure must still be findable in the registry
# ---------------------------------------------------------------------------
def registry_text_blob(registry: dict) -> str:
    """The registry, flattened to one searchable string.

    Deliberately crude. The check being made is 'does this verbatim string still exist
    somewhere in the registry', which is the question that catches a silently edited
    figure. A path-precise lookup would be prettier and would fail closed on a
    restructure that changed nothing about the numbers.
    """
    return json.dumps(registry, ensure_ascii=False)


def verify_provenance(spec: dict, blob: str) -> list[str]:
    """Every declared verbatim string must still be present. Returns failures."""
    failures = []
    for s in spec["series"]:
        v = s.get("registry_verbatim")
        if v and v not in blob:
            failures.append(
                f"{s['key']}: registry_verbatim {v!r} no longer appears in the clinical "
                f"registry. Either the registry figure changed (update this input file in "
                f"the same commit, per CLAUDE.md rule 1.3) or the string was mistyped."
            )
    pooled = spec.get("pooled_reference") or {}
    pv = pooled.get("registry_verbatim")
    if pv and pv not in blob:
        failures.append(f"pooled_reference: registry_verbatim {pv!r} not in the registry.")
    return failures


# ---------------------------------------------------------------------------
# The decomposition
# ---------------------------------------------------------------------------
def pct(x: float) -> float:
    return round(100.0 * x, 1)


def decompose(all_cause_survival: float, disease_specific_survival: float) -> dict:
    """One horizon, one pairing.

    all_cause_mortality  = 1 - S_all
    disease_mortality    = 1 - S_dss           (over-estimate; see the module docstring)
    competing_mortality  = the remainder
    competing_share      = competing / all_cause, i.e. of those who died, how many not of EMC
    """
    m_all = 1.0 - all_cause_survival
    m_dis = 1.0 - disease_specific_survival
    m_comp = m_all - m_dis
    return {
        "all_cause_mortality_pct": pct(m_all),
        "disease_mortality_pct": pct(m_dis),
        "competing_mortality_pct": pct(m_comp),
        "competing_share_of_deaths_pct": pct(m_comp / m_all) if m_all > 0 else None,
        "antitumour_ceiling_pct_points": pct(m_dis),
        "coherent": m_comp >= 0,
        "incoherence_note": (
            None if m_comp >= 0 else
            "Disease-specific mortality exceeds all-cause mortality, which is impossible "
            "within one population and therefore proves these two figures do not describe "
            "one. Reported rather than suppressed: it is the cross-series pairing telling "
            "the reader its own limit."
        ),
    }


def direct_cause_split(spec: dict) -> list[dict]:
    """⭐ THE STRONGEST READING AVAILABLE, AND IT NEEDS NO SURVIVAL CURVE AT ALL.

    When a study reports, for one cohort, how many patients died OF the disease and how
    many died of something else, the competing share is a straight ratio of two counts
    from the same patients under the same ascertainment. There is no estimator mismatch,
    no cross-population pairing and no subtraction of percentages -- the three weaknesses
    that every other figure in this file has to disclose.

    Added 2026-08-09 after the mortality probe pulled the other-cause counts out of
    Masunaga 2025's full text. They had always been in the paper and were not in the
    curated record, because a registry that tracks disease-specific death has no field
    for the deaths that were not.
    """
    out = []
    for s in spec["series"]:
        dd, oc = s.get("disease_death"), s.get("other_cause_death")
        if not dd or not oc:
            continue
        if dd["denom"] != oc["denom"]:
            continue
        deaths = dd["events"] + oc["events"]
        out.append({
            "series": s["key"],
            "label": s["label"],
            "n": dd["denom"],
            "disease_deaths": dd["events"],
            "other_cause_deaths": oc["events"],
            "total_deaths": deaths,
            "all_cause_mortality_pct": pct(deaths / dd["denom"]),
            "disease_mortality_pct": pct(dd["events"] / dd["denom"]),
            "competing_mortality_pct": pct(oc["events"] / dd["denom"]),
            "competing_share_of_deaths_pct": pct(oc["events"] / deaths) if deaths else None,
            "antitumour_ceiling_pct_points": pct(dd["events"] / dd["denom"]),
            "median_followup_months": s.get("median_followup_months"),
            "estimator": (
                "Direct ratio of two death counts on the same patients. No survival curve, no "
                "cross-population pairing, no subtraction of summary percentages."),
            "what_still_limits_it": (
                "Follow-up is finite and shorter than this disease's natural history, so both "
                "counts are censored -- and they are NOT censored equally. EMC deaths keep "
                "accruing for decades while competing deaths accrue immediately, so a short "
                "follow-up flatters the competing share early and the disease share late. This "
                "is a reading at the study's own horizon, not a lifetime split."),
            "pairing_note": s.get("pairing_note"),
        })
    return out


def within_series(spec: dict) -> list[dict]:
    """Pairings where both numbers came from the same patients."""
    out = []
    for s in spec["series"]:
        if s.get("pairing") != "within_series":
            continue
        dd = s.get("disease_death")
        os_curve = s.get("overall_survival") or {}
        if not dd or not os_curve:
            continue
        dss_crude = 1.0 - dd["events"] / dd["denom"]
        # Pair the crude disease-death proportion against the all-cause reading at the
        # horizon closest to the series' own median follow-up -- pairing it against a
        # 15-year reading when follow-up is 9 years would compare a proportion nobody
        # observed against a curve that had run twice as long.
        fu_years = (s.get("median_followup_months") or 0) / 12.0
        horizons = sorted(os_curve, key=lambda h: abs(float(h) - fu_years))
        h = horizons[0]
        d = decompose(os_curve[h], dss_crude)
        d.update({
            "series": s["key"],
            "label": s["label"],
            "n": s["n"],
            "horizon_years": float(h),
            "median_followup_years": round(fu_years, 1),
            "all_cause_survival_pct": pct(os_curve[h]),
            "disease_specific_survival_pct": pct(dss_crude),
            "disease_death_events": f"{dd['events']}/{dd['denom']}",
            "estimator_mismatch": (
                "The all-cause figure is a survival-curve reading at the horizon; the "
                "disease-specific figure is a crude proportion over the whole follow-up. "
                "They are not the same estimator and this decomposition is approximate."
            ),
            "pairing_note": s.get("pairing_note"),
        })
        out.append(d)
    return out


def cross_series(spec: dict) -> dict:
    """Pair every all-cause figure against every disease-specific figure, per horizon.

    Cross-population by construction, so the output is a BAND rather than a point
    estimate. ⚠ AND THE BAND IS NOT TAKEN FROM THE TWO EXTREME PAIRINGS, which is how
    this was first written and which produced a headline range of -25% to 57%. Two
    pairings there are degenerate rather than merely wide:

      * a cohort reporting 100% five-year all-cause survival has NO deaths to split, so
        the competing share is undefined, not zero;
      * a pairing whose disease-specific mortality exceeds its all-cause mortality is
        arithmetically impossible within one population, and therefore proves those two
        studies are not describing one.

    Both are findings about the pairing, not readings of the disease, and letting them
    set the edges of the band would have published a negative competing share as though
    it were a lower bound. So every pairing is enumerated, the impossible and undefined
    ones are separated out and COUNTED rather than dropped, and the reported band spans
    only the pairings that are internally coherent.
    """
    all_cause: dict[float, list[tuple[str, float]]] = {}
    disease: dict[float, list[tuple[str, float]]] = {}
    for s in spec["series"]:
        for h, v in (s.get("overall_survival") or {}).items():
            all_cause.setdefault(float(h), []).append((s["key"], v))
        for h, v in (s.get("disease_specific_survival") or {}).items():
            disease.setdefault(float(h), []).append((s["key"], v))

    pooled = spec.get("pooled_reference") or {}
    if pooled.get("value") is not None:
        disease.setdefault(10.0, []).append(("registry_pooled", pooled["value"]))

    out = {}
    for h in sorted(set(all_cause) & set(disease)):
        coherent, impossible, undefined = [], [], []
        for ac_key, ac_v in sorted(all_cause[h], key=lambda kv: kv[1]):
            for ds_key, ds_v in sorted(disease[h], key=lambda kv: kv[1]):
                d = decompose(ac_v, ds_v)
                d.update({
                    "all_cause_source": ac_key,
                    "all_cause_survival_pct": pct(ac_v),
                    "disease_specific_source": ds_key,
                    "disease_specific_survival_pct": pct(ds_v),
                })
                if not d["coherent"]:
                    impossible.append(d)
                elif d["competing_share_of_deaths_pct"] is None:
                    undefined.append(d)
                else:
                    coherent.append(d)

        shares = sorted(x["competing_share_of_deaths_pct"] for x in coherent)
        ceilings = sorted(x["antitumour_ceiling_pct_points"] for x in coherent)
        ac_vals = sorted(v for _, v in all_cause[h])
        ds_vals = sorted(v for _, v in disease[h])
        out[f"{h:g}_year"] = {
            "all_cause_survival_pct_range": [pct(ac_vals[0]), pct(ac_vals[-1])],
            "all_cause_sources": [k for k, _ in sorted(all_cause[h], key=lambda kv: kv[1])],
            "disease_specific_survival_pct_range": [pct(ds_vals[0]), pct(ds_vals[-1])],
            "disease_specific_sources": [k for k, _ in sorted(disease[h], key=lambda kv: kv[1])],
            "pairings_total": len(coherent) + len(impossible) + len(undefined),
            "pairings_coherent": len(coherent),
            "pairings_impossible": len(impossible),
            "pairings_undefined": len(undefined),
            "competing_share_of_deaths_pct_range": [shares[0], shares[-1]] if shares else None,
            "competing_share_of_deaths_pct_median": (
                shares[len(shares) // 2] if shares else None
            ),
            "antitumour_ceiling_pct_points_range": (
                [ceilings[0], ceilings[-1]] if ceilings else None
            ),
            "excluded_pairings": {
                "impossible": [
                    {"all_cause_source": d["all_cause_source"],
                     "disease_specific_source": d["disease_specific_source"],
                     "why": "disease-specific mortality exceeds all-cause mortality"}
                    for d in impossible
                ],
                "undefined": [
                    {"all_cause_source": d["all_cause_source"],
                     "disease_specific_source": d["disease_specific_source"],
                     "why": "all-cause mortality is zero, so there are no deaths to apportion"}
                    for d in undefined
                ],
                "how_to_read_them": (
                    "These are not outliers to be trimmed. Each one is a cross-series "
                    "pairing demonstrating that the two studies it joins cannot describe a "
                    "single population, which is the honest limit of every figure in this "
                    "section. A horizon where most pairings are impossible should not be "
                    "quoted at all."
                ),
            },
        }
    return out


def wilson(events: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval. Used because these counts are 4 and 1 -- a normal
    approximation on four events would produce an interval including negative risk, and a
    point estimate with no interval would make a two-event difference look decisive."""
    if n == 0:
        return (0.0, 1.0)
    p = events / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def horizon_matched_background(spec: dict) -> list[dict]:
    """⭐ THE CHECK THAT DECIDES WHETHER ANY OF THIS IS QUOTABLE.

    Compare the other-cause deaths a study actually observed against what a general
    population of the same age and sex would produce over THAT STUDY'S OWN FOLLOW-UP --
    not over ten years, which is the horizon the decomposition reports and not the one
    the counts were measured at. Matching horizons is the whole point: background
    mortality over three years and over ten differ by a factor of three, so comparing an
    observed three-year count against a ten-year expectation would manufacture a
    four-fold discrepancy out of arithmetic alone.
    """
    bg = spec.get("background_mortality") or {}
    rate = bg.get("blended_annual_rate_55_59")
    out = []
    for row in bg.get("horizon_matched_checks", []):
        events, n = row["observed_other_cause"]
        yrs = row["followup_years"]
        if rate is None:
            out.append({"stratum": row["stratum"], "status": "NOT_RUN",
                        "why": "no life-table rate available"})
            continue
        expected = 1 - math.exp(-rate * yrs)
        observed = events / n
        lo, hi = wilson(events, n)
        out.append({
            "stratum": row["stratum"],
            "followup_years": yrs,
            "observed_other_cause_deaths": f"{events}/{n}",
            "observed_pct": pct(observed),
            "observed_95ci_pct": [pct(lo), pct(hi)],
            "expected_background_pct": pct(expected),
            "ratio_observed_to_expected": round(observed / expected, 2) if expected else None,
            "ratio_95ci": [round(lo / expected, 2), round(hi / expected, 2)] if expected else None,
            "background_inside_observed_ci": lo <= expected <= hi,
            "reading": (
                "A ratio near 1 means the non-EMC deaths in this cohort are what ordinary "
                "background mortality produces, so the competing share is a real reading rather "
                "than an artifact of incomparable studies. A ratio far above 1 would mean the "
                "opposite and would make every competing-share figure here unquotable."),
            "⚠": (
                f"This rests on {events} event(s). The interval is wide and the point estimate is "
                f"not precise -- what the check establishes is CONSISTENCY with background, never "
                f"equality to it."),
        })
    return out


def background_check(spec: dict, cross: dict) -> dict:
    bg = spec.get("background_mortality") or {}
    observed = None
    ten = cross.get("10_year")
    if ten and ten.get("competing_share_of_deaths_pct_median") is not None:
        # The competing-mortality percentage points implied by the median coherent
        # pairing, which is what the background check has to be compared against.
        observed = round(
            ten["competing_share_of_deaths_pct_median"]
            * (100.0 - ten["all_cause_survival_pct_range"][0]) / 100.0, 1)
    if bg.get("ten_year_background_mortality") is None:
        return {
            "status": "NOT_RUN",
            "why": (
                "No life table has been fetched, so the question 'is this gap the size an "
                "ordinary cohort of this age and sex would show anyway' has not been asked. "
                "An absent reading is not a reading of absence: this is NOT evidence that "
                "the gap is unexplained, and it is NOT evidence that it is explained."
            ),
            "what_would_settle_it": (
                "A public period life table (US NCHS or SSA), the cohort's median age and "
                "sex ratio, and the 10-year cumulative probability of death it implies. "
                "The comparison is then: does background mortality account for most of the "
                "observed competing-mortality percentage points, or only a fraction of them?"
            ),
            "observed_competing_mortality_pct_at_10y": observed,
            "cohort_age_median": bg.get("cohort_age_median"),
            "cohort_sex_ratio_male": bg.get("cohort_sex_ratio_male"),
        }
    expected = bg["ten_year_background_mortality"]
    return {
        "status": "RUN",
        "life_table_source": bg.get("life_table_source"),
        "expected_background_mortality_pct_at_10y": pct(expected),
        "observed_competing_mortality_pct_at_10y": observed,
        "ratio_observed_to_expected": (
            round(observed / (100.0 * expected), 2) if observed and expected else None
        ),
        "reading": (
            "A ratio near 1 means the gap is ordinary background mortality and the "
            "decomposition is sound. A ratio far above 1 means the gap is larger than age "
            "and sex explain, which points at study non-comparability rather than at "
            "patients dying of other causes -- in that case the decomposition is an "
            "artifact and must not be quoted."
        ),
    }


def main() -> int:
    spec = json.loads(INPUTS.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    failures = verify_provenance(spec, registry_text_blob(registry))
    if failures:
        for f in failures:
            print(f"PROVENANCE FAIL: {f}", file=sys.stderr)
        return 1

    direct = direct_cause_split(spec)
    within = within_series(spec)
    cross = cross_series(spec)

    payload = {
        "_readme": (
            "Decomposition of mortality after an EMC diagnosis into disease deaths and "
            "deaths from everything else. Generated by "
            "research/manuscripts/emc_mortality_decomposition.py from the cited figures in "
            "research/data/emc-clinical-registry.json, which is their one home. "
            "READ THE PAIRING FIELD ON EVERY ROW. `within_series` rows pair two figures "
            "measured on the same patients and are the only ones that do not cross "
            "populations; `cross_series` rows pair an all-cause figure from one study "
            "against a disease-specific figure from another and are reported as ranges for "
            "that reason. Nothing here asserts efficacy, safety, a therapeutic window or "
            "clinical readiness for any intervention, and nothing here is a prognosis."
        ),
        "generated_by": "research/manuscripts/emc_mortality_decomposition.py",
        "inputs": "research/manuscripts/emc-mortality-decomposition-inputs.json",
        "figures_home": "research/data/emc-clinical-registry.json",
        "directional_bias": (
            "Disease-specific survival estimated by censoring other-cause deaths overstates "
            "the cumulative incidence of disease death under competing risks, so the "
            "competing share reported here is an UNDER-estimate. The bias runs against this "
            "analysis's own conclusion, which is why the subtraction is publishable at all."
        ),
        "direct_cause_split": direct,
        "within_series": within,
        "cross_series": cross,
        "background_mortality_check": background_check(spec, cross),
        "horizon_matched_background_check": horizon_matched_background(spec),
        "reading_guide": {
            "antitumour_ceiling": (
                "The percentage points of survival at the horizon that a therapy preventing "
                "EVERY EMC death would add. It is an upper bound on this repository's entire "
                "sixty-eight-route portfolio taken together, not on any one route."
            ),
            "competing_share_of_deaths": (
                "Of the patients dead at the horizon, the fraction who did not die of EMC. "
                "No route on the board is aimed at this fraction."
            ),
            "what_it_does_not_say": (
                "That competing deaths are preventable. Establishing that requires naming a "
                "specific cause and a specific intervention with a measured effect, which is "
                "a separate question and a separate artifact."
            ),
        },
    }

    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {OUT.relative_to(ROOT)}")
    for row in direct:
        print(f"  DIRECT  {row['label']}: {row['other_cause_deaths']}/{row['total_deaths']} deaths "
              f"were not EMC deaths = {row['competing_share_of_deaths_pct']}% "
              f"(ceiling {row['antitumour_ceiling_pct_points']} pts)")
    for row in within:
        print(f"  within  {row['label']}: at {row['horizon_years']:g}y, "
              f"{row['competing_share_of_deaths_pct']}% of deaths were not EMC deaths "
              f"(antitumour ceiling {row['antitumour_ceiling_pct_points']} pts)")
    for h, row in cross.items():
        print(f"  cross   {h}: competing share {row['competing_share_of_deaths_pct_range']}% "
              f"(median {row['competing_share_of_deaths_pct_median']}%), "
              f"ceiling {row['antitumour_ceiling_pct_points_range']} pts, "
              f"{row['pairings_coherent']}/{row['pairings_total']} pairings coherent "
              f"({row['pairings_impossible']} impossible, {row['pairings_undefined']} undefined)")
    print(f"  background check: {payload['background_mortality_check']['status']}")
    for r in payload["horizon_matched_background_check"]:
        if r.get("status") == "NOT_RUN":
            print(f"  BG {r['stratum']}: NOT RUN"); continue
        print(f"  BG {r['stratum']}: observed {r['observed_pct']}% vs background "
              f"{r['expected_background_pct']}% -> ratio {r['ratio_observed_to_expected']} "
              f"(95% CI {r['ratio_95ci'][0]}-{r['ratio_95ci'][1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
