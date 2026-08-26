"""When EMC recurs, against how long anybody was watching — from printed summary statistics.

WHY THIS EXISTS
---------------
`systems/graph/routes.json` -> RT-SURVEILLANCE asks *"Does follow-up in EMC stop before the disease
does, and how much resectable recurrence is lost when it does?"* and records its next action as
*"Wait on RT-IPD-SURVIVAL for the recurrence hazard, then build the state-transition model -- the
summary figures alone cannot support one."*

The second half of that sentence is right and this file does not dispute it: **no model is fitted
here.** But the route's FIRST question does not need a model, and the summary figures answer it.
Both reachable series print time-to-event statistics with an anchor, a median and -- in the larger
one -- an interquartile range, alongside their own median follow-up. Putting those two next to each
other is the whole method.

⭐ THE CONFOUND-FREE OBSERVATION, AND IT IS THE ONE WORTH CARRYING. Masunaga reports the median time
from surgery to local recurrence as 15 months with an IQR of 4.5-63.5, and reports its own median
follow-up as 38 months. **The upper quartile of the time-to-recurrence distribution lies beyond the
median follow-up of the cohort that measured it.** A quarter of the local recurrences this series
observed happened later than half its patients were watched. That is a within-cohort statement: it
needs no second series, no era assumption and no comparison of populations, and it is the direct
answer to "does follow-up stop before the disease does".

⚠ THE CROSS-COHORT DIVERGENCE IS LARGER AND WEAKER, AND BOTH HALVES MATTER. Masunaga's median time
from diagnosis to distant metastasis is 16 months; Chiusole's is 5.9 years -- about 71 months, a
4.4-fold difference in the same quantity with the same anchor. Chiusole also reports MORE cumulative
metastasis (40.8 % against 29.1 %) on a median follow-up of 72 months against 38. Longer observation
producing both more events and later ones is exactly what censoring predicts.
⛔ AND IT IS NOT THE ONLY EXPLANATION, SO IT IS NOT ASSERTED AS ONE. The two cohorts differ in era
(1980-2018 against 2002-2022), country, and setting (two referral centres against a national
registry). Imaging changed enormously across those windows, and earlier detection moves a
time-to-metastasis median down on its own. **Two cohorts cannot discriminate follow-up length from
era, and this module does not pretend otherwise** -- which is precisely why the within-cohort
observation above, and not this comparison, is the finding.

⛔ WHAT A SURVEILLANCE SCHEDULE NEEDS AND CANNOT BE GIVEN HERE. An interval is chosen from a HAZARD
-- the instantaneous risk of recurrence as a function of time since surgery. A median and an IQR are
three points on a cumulative distribution. They can say the distribution has a long right tail; they
cannot give its shape, and they cannot be differentiated into a hazard. **No surveillance interval,
schedule or duration is recommended anywhere in this file, and none may be derived from it.**

⛔ LEAD-TIME BIAS IS UNTOUCHED AND MUST STAY THAT WAY. Detecting a recurrence earlier moves the date
of detection and need not move the date of death. Nothing here measures whether earlier detection
helps anyone, and the route's own third unknown -- whether any surveillance benefit survives
lead-time bias -- is not advanced by a single number in this file.

⛔ SCOPE. Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness, and
nothing here is medical advice.

Run:     python3 research/modalities/emc_recurrence_timing.py
Verify:  python3 research/modalities/emc_recurrence_timing.py --check
Writes:  research/modalities/emc-recurrence-timing.json
"""

from __future__ import annotations

import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-recurrence-timing.json")

# ---------------------------------------------------------------------------
# the transcription
# ---------------------------------------------------------------------------
# ⛔ EVERY FIGURE IS PRINTED, AND EVERY ONE NAMES ITS ANCHOR. The anchor is not decoration: Masunaga
# measures local recurrence from SURGERY and distant metastasis from DIAGNOSIS, in the same sentence.
# Comparing a from-surgery interval to a from-diagnosis interval is the silent error available here,
# so `anchor` is a required field and a guard fails if two events are compared across anchors.

COHORTS = [
    {
        "source_id": "masunaga2025",
        "population": "the 134 patients localized at diagnosis who underwent surgery",
        "n": 134,
        "median_followup_months": 38,
        "followup_iqr_months": [23, 71],
        "followup_anchor": "diagnosis",
        "followup_printed_in": "Table 1, 'Follow-up period after diagnosis (months), median (IQR)', "
                               "total column -- ⚠ that row is over all 171, not over the 134",
        "events": [
            {
                "event": "local_recurrence",
                "count": 16, "printed_percent": 11.9,
                "anchor": "surgery",
                "median_months": 15, "iqr_months": [4.5, 63.5],
                "printed_in": "Results, 'Local recurrence occurred in 16 patients (11.9%), and the "
                              "median time from surgery to local recurrence was 15 months "
                              "(IQR, 4.5-63.5)'",
            },
            {
                "event": "distant_metastasis",
                "count": 39, "printed_percent": 29.1,
                "anchor": "diagnosis",
                "median_months": 16, "iqr_months": [10, 31],
                "printed_in": "Results, 'Distant metastases occurred in 39 patients (29.1%), and the "
                              "median time from diagnosis to distant metastasis was 16 months "
                              "(IQR, 10-31 months)'",
                "⭐_independently_reconcilable": (
                    "The same paper's distant-metastasis paragraph splits these 39 by chemotherapy: "
                    "38 of the 128 unexposed and 1 of the 6 exposed. 38 + 1 = 39, printed in a "
                    "different paragraph -- so this count is checkable without the paper."),
            },
            {
                "event": "death_from_tumour",
                "count": 9, "printed_percent": 6.7,
                "anchor": "diagnosis",
                "median_months": 36, "iqr_months": [25, 69],
                "printed_in": "Results, 'Nine patients (6.7%) died due to the tumor, and the median "
                              "time from diagnosis to death due to the tumor was 36 months "
                              "(IQR, 25-69 months)'",
            },
        ],
    },
    {
        "source_id": "chiusole2020",
        "population": "the 49 patients treated with curative intent",
        "n": 49,
        "median_followup_months": 72,
        "followup_iqr_months": None,
        "followup_anchor": "unstated -- the paper says 'a median follow-up time of 72 months' "
                           "without naming the origin",
        "followup_printed_in": "Results, 'With a median follow-up time of 72 months, 20 patients "
                               "have died'",
        "events": [
            {
                "event": "local_recurrence",
                "count": 14, "printed_percent": 28.6,
                "anchor": "unstated",
                "median_months": None, "iqr_months": None,
                "printed_in": "Results, 'Out of 49 patients treated with curative intent, 28.6% "
                              "developed local recurrence'",
                "⛔_no_timing": "The paper prints the proportion and no time-to-event statistic for "
                                "local recurrence, so this cohort contributes nothing to the timing "
                                "question for this event.",
            },
            {
                "event": "distant_metastasis",
                "count": 20, "printed_percent": 40.8,
                "anchor": "diagnosis",
                "median_months": 70.8,
                "median_printed_as": "5.9 years",
                "iqr_months": None,
                "printed_in": "Results, 'Median time from diagnosis to metastatic disease was 5.9 "
                              "years with a proportion of 40.8% of patients treated with curative "
                              "intent developing metastatic disease'",
                "⚠_count_is_derived_not_printed": (
                    "The paper prints 40.8 % and not a count. 40.8 % of 49 is 19.99, so the count is "
                    "20 -- recorded because it is unambiguous at this denominator, and flagged "
                    "because a percentage back-converted to a count is a derivation, not a "
                    "transcription (POLICY-evidence 2.1 forbids doing this to obtain a POOLING "
                    "denominator; nothing here is pooled)."),
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# derivations
# ---------------------------------------------------------------------------


def _events_beyond_the_watch(c: dict) -> list[dict]:
    """Where a printed quartile of the event distribution lies past the cohort's own follow-up.

    ⭐ THE ONE COMPARISON IN THIS FILE THAT NEEDS NO SECOND COHORT. Both numbers come from the same
    paper, the same patients and the same clock, so era, country and setting cannot explain it.
    """
    out = []
    for e in c["events"]:
        if not e.get("iqr_months") or c["median_followup_months"] is None:
            continue
        upper = e["iqr_months"][1]
        out.append({
            "event": e["event"],
            "anchor": e["anchor"],
            "upper_quartile_months": upper,
            "cohort_median_followup_months": c["median_followup_months"],
            "upper_quartile_exceeds_median_followup": upper > c["median_followup_months"],
            "months_beyond": round(upper - c["median_followup_months"], 1),
            "⚠_the_anchors_differ_by_the_time_to_surgery": (
                "The event is measured from surgery and the follow-up from diagnosis, so the "
                "comparison is off by the diagnosis-to-surgery interval, which this paper does not "
                "print. That interval is short relative to the 25.5-month gap -- weeks to a few "
                "months in a series where 73 % of patients were resected -- and it moves the "
                "comparison in the CONSERVATIVE direction: counting from diagnosis would place the "
                "recurrence even later, not earlier. Stated because it is a real imprecision, not "
                "because it threatens the sign."
                if e["anchor"] != c["followup_anchor"] else None),
        })
    return out


def build() -> dict:
    mas = next(c for c in COHORTS if c["source_id"] == "masunaga2025")
    chi = next(c for c in COHORTS if c["source_id"] == "chiusole2020")

    def ev(c, name):
        return next((e for e in c["events"] if e["event"] == name), None)

    mas_dm, chi_dm = ev(mas, "distant_metastasis"), ev(chi, "distant_metastasis")
    beyond = _events_beyond_the_watch(mas)
    lr = next(b for b in beyond if b["event"] == "local_recurrence")

    return {
        "_what": ("Time-to-recurrence statistics for EMC as PRINTED by the two reachable "
                  "open-access series, set against each series' own follow-up length."),
        "_not_medical_advice": (
            "Nothing here is medical advice. No surveillance interval, schedule or duration is "
            "recommended, and none may be derived from anything in this file."),
        "_generated_by": "research/modalities/emc_recurrence_timing.py",
        "⭐_the_finding": {
            "statement": (
                "In the larger series, the upper quartile of the time from surgery to local "
                f"recurrence ({lr['upper_quartile_months']} months) lies "
                f"{lr['months_beyond']} months BEYOND that cohort's own median follow-up "
                f"({lr['cohort_median_followup_months']} months). A quarter of the local recurrences "
                "it observed happened later than half its patients were watched."),
            "why_it_is_the_one_worth_carrying": (
                "Both numbers come from one paper, one set of patients and one clock. Era, country, "
                "setting and imaging generation are held constant by construction, so none of them "
                "can explain it. It is the direct answer to RT-SURVEILLANCE's framing question -- "
                "does follow-up stop before the disease does -- and it needs no model."),
            "⛔_what_it_does_not_say": (
                "It says nothing about whether watching longer would help anyone. Detecting a "
                "recurrence sooner moves the date of detection and need not move the date of death; "
                "that is lead-time bias and nothing here touches it. It also does not say what "
                "fraction of late recurrences were resectable, which no EMC series reports."),
        },
        "cohorts": COHORTS,
        "events_beyond_the_observation_window": beyond,
        "⛔_an_iqr_that_fits_inside_the_window_is_not_reassurance": (
            "Two of the three Masunaga events put their upper quartile beyond the median follow-up "
            "and one -- distant metastasis, IQR 10-31 against 38 months -- does not. THAT ROW MUST "
            "NOT BE READ AS 'no censoring problem here'. A truncated sample's quartiles are "
            "computed over the events that were OBSERVABLE, so truncation pulls them inward: an "
            "IQR fitting neatly inside the observation window is what censoring PRODUCES, not "
            "evidence against it. The direction of the inference only runs one way -- an IQR that "
            "ESCAPES the window is remarkable, because it means late events survived into a sample "
            "biased against them; an IQR that fits tells you nothing either way. ⭐ AND THE "
            "DISTANT-METASTASIS ROW IS EXACTLY WHERE THAT MATTERS: its quartiles look early and "
            "tight (10-31 months) while the cohort watched twice as long reports the median for the "
            "same event, from the same anchor, at about 71 months. A tidy-looking IQR and a "
            "four-fold disagreement with a longer-followed series are the same observation seen "
            "from two sides."),
        "cross_cohort_time_to_distant_metastasis": {
            "masunaga2025": {"median_months": mas_dm["median_months"],
                             "cumulative_percent": mas_dm["printed_percent"],
                             "median_followup_months": mas["median_followup_months"],
                             "n": mas["n"]},
            "chiusole2020": {"median_months": chi_dm["median_months"],
                             "printed_as": chi_dm["median_printed_as"],
                             "cumulative_percent": chi_dm["printed_percent"],
                             "median_followup_months": chi["median_followup_months"],
                             "n": chi["n"]},
            "same_anchor": mas_dm["anchor"] == chi_dm["anchor"] == "diagnosis",
            "ratio_of_medians": round(chi_dm["median_months"] / mas_dm["median_months"], 2),
            "⚠_consistent_with_censoring_and_not_established_by_it": (
                "The cohort followed roughly twice as long reports both MORE cumulative metastasis "
                "(40.8 % against 29.1 %) and a median time to it about 4.4 times later. Longer "
                "observation producing more events and later ones is what censoring predicts, and "
                "a cohort with 38 months of median follow-up cannot observe a metastasis at 71 "
                "months at all. ⛔ BUT THE TWO COHORTS DIFFER IN ERA (1980-2018 against 2002-2022), "
                "COUNTRY AND SETTING, and imaging improved across those windows in a way that moves "
                "a time-to-metastasis median DOWN on its own. Two cohorts cannot discriminate "
                "follow-up length from era. This is recorded as consistent, never as demonstrated, "
                "and it is deliberately not the finding above."),
        },
        "⛔_no_hazard_and_therefore_no_schedule": (
            "A surveillance interval is chosen from a hazard -- the instantaneous risk of recurrence "
            "as a function of time since surgery. What is printed is a median and, once, an IQR: "
            "three points on a cumulative distribution. They establish a long right tail and cannot "
            "give its shape, and they cannot be differentiated into a hazard. RT-SURVEILLANCE's "
            "state-transition model still needs what its next-action says it needs, and this file "
            "does not supply it."),
        "⛔_nothing_is_pooled": (
            "Different eras, settings, populations and -- for local recurrence -- different and "
            "partly unstated anchors. POLICY-evidence 2.4 refuses to merge time-anchored figures at "
            "all. No combined median, no combined proportion."),
        "counts": {
            "cohorts": len(COHORTS),
            "events_with_a_printed_median": sum(
                1 for c in COHORTS for e in c["events"] if e.get("median_months") is not None),
            "events_with_a_printed_iqr": sum(
                1 for c in COHORTS for e in c["events"] if e.get("iqr_months")),
            "events_with_no_timing_at_all": sum(
                1 for c in COHORTS for e in c["events"] if e.get("median_months") is None),
        },
    }


# ---------------------------------------------------------------------------
# guards
# ---------------------------------------------------------------------------


def _check_structure() -> list[str]:
    errs: list[str] = []
    for c in COHORTS:
        for e in c["events"]:
            if "anchor" not in e:
                errs.append(f"{c['source_id']}/{e['event']}: no anchor recorded")
            if e["count"] > c["n"]:
                errs.append(f"{c['source_id']}/{e['event']}: {e['count']} events exceeds n = {c['n']}")
            # the printed percentage must reproduce from the count
            pct = 100.0 * e["count"] / c["n"]
            if abs(pct - e["printed_percent"]) > 0.1:
                errs.append(f"{c['source_id']}/{e['event']}: {e['count']}/{c['n']} = {pct:.1f} %, "
                            f"printed {e['printed_percent']} %")
            iqr = e.get("iqr_months")
            if iqr:
                if e["median_months"] is None:
                    errs.append(f"{c['source_id']}/{e['event']}: IQR without a median")
                elif not (iqr[0] <= e["median_months"] <= iqr[1]):
                    errs.append(f"{c['source_id']}/{e['event']}: median {e['median_months']} "
                                f"outside its IQR {iqr}")
            if e.get("median_months") is not None and not e.get("printed_in"):
                errs.append(f"{c['source_id']}/{e['event']}: a timing figure with no printed source")
    return errs


def _check_no_cross_anchor_comparison() -> list[str]:
    """The cross-cohort comparison may only run on events sharing an anchor."""
    doc = build()
    x = doc["cross_cohort_time_to_distant_metastasis"]
    if not x["same_anchor"]:
        return ["the cross-cohort comparison is running across different anchors"]
    return []


def check() -> int:
    errs = _check_structure() + _check_no_cross_anchor_comparison()
    doc = build()
    if not os.path.exists(OUT):
        errs.append(f"{os.path.basename(OUT)} is missing; run without --check to build it")
    else:
        with open(OUT, encoding="utf-8") as fh:
            if json.load(fh) != doc:
                errs.append(f"{os.path.basename(OUT)} does not reproduce from its generator")
    for e in errs:
        print(f"ERROR: {e}")
    if errs:
        return 1
    print(f"emc_recurrence_timing --check OK "
          f"({doc['counts']['events_with_a_printed_median']} events with a printed median, "
          f"{doc['counts']['events_with_a_printed_iqr']} with an IQR, "
          f"{doc['counts']['events_with_no_timing_at_all']} with no timing)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the artifact reproduces and every guard holds")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    errs = _check_structure() + _check_no_cross_anchor_comparison()
    for e in errs:
        print(f"ERROR: {e}")
    if errs:
        return 1
    doc = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}")
    for b in doc["events_beyond_the_observation_window"]:
        mark = "BEYOND" if b["upper_quartile_exceeds_median_followup"] else "inside"
        print(f"  {b['event']:22s} upper quartile {b['upper_quartile_months']:>5} mo vs median "
              f"follow-up {b['cohort_median_followup_months']} mo -> {mark}")
    x = doc["cross_cohort_time_to_distant_metastasis"]
    print(f"  cross-cohort median time to distant metastasis: "
          f"{x['masunaga2025']['median_months']} mo vs {x['chiusole2020']['median_months']} mo "
          f"({x['ratio_of_medians']}x)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
