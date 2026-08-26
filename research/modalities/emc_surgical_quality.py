"""Margin status, the first operation and the treatment setting, curated from the primary reports.

WHY THIS EXISTS
---------------
`systems/graph/routes.json` -> RT-SURGICAL-QUALITY asks *"How much of EMC's survival is decided by
whether the first operation cleared the tumour, and by where it was performed?"*, records its next
action as *"Extract margin status, primary site and treatment setting from the open-access EMC
series already cited in the registry"*, and states as its FIRST remaining unknown:

  *"What the positive-margin rate in EMC actually is -- no cohort in the registry carries a margin
  field, and the one dedicated EMC surgical series reports a single positive margin in 13 patients."*

Two reachable open-access series print full margin distributions over 156 and 40 operated patients.
This file transcribes them, and the answer to that unknown is here rather than in a route grade.

⛔ THE DENOMINATOR IS THE WHOLE DIFFICULTY, AND IT IS WHY THIS IS NOT ONE NUMBER. "Positive-margin
rate" has at least three defensible denominators in Masunaga alone -- every registered patient, every
operated patient, and every operated patient who was localized at diagnosis -- and they are not
close: patients who were already metastatic were operated to a positive margin roughly twice as
often. Every rate below therefore names its denominator in its own key, and the module reports the
set rather than electing one.

⭐ WHAT MAKES THIS CHECKABLE RATHER THAN MERELY TRANSCRIBED. Masunaga's Table 1 margin row and the
Cox tables in `emc_prognostic_coefficients.py` are independent printings of overlapping facts:
Table 1 gives R0/R1/R2/no-surgery for all 171 and for the 142 non-metastatic, and the Cox tables
give R0 vs R1-or-R2 for the 134 modelled. Subtracting the 8 non-metastatic patients who had no
surgery must reproduce the Cox tables' 104 and 30 exactly. It does, and a test asserts it -- so a
mistyped count in either module is caught by the other.

⛔ TREATMENT SETTING IS ABSENT FROM BOTH SOURCES, AND THAT IS A READING RATHER THAN A GAP. The route
wants referral-centre and volume-outcome effects. Masunaga is the Japanese National Bone and Soft
Tissue Tumor Registry and prints no centre, no centre volume and no referral status; Chiusole is two
named referral centres with no non-referral comparator, which is a cohort with the exposure held
CONSTANT. So the route's second unknown -- whether treatment at a sarcoma referral centre changes
EMC outcomes specifically -- cannot be advanced by either, and no amount of further curation of
these two papers will change that. `treatment_setting` records the absence explicitly so that a
later session does not re-curate them hoping for it.

⛔ NEITHER SOURCE HAS AN UNPLANNED-EXCISION FIELD, AND THE TWO NEAREST THINGS ARE NOT IT. Masunaga
records "previous surgery" (18 of 171) and an "excisional" biopsy method (10 of 171). An unplanned
excision -- the "whoops procedure", a sarcoma removed by a surgeon who did not know it was one --
would plausibly appear as either. But Masunaga DEFINES its margin terms and does NOT define
"previous surgery", so reading it as unplanned excision is an inference about a field whose meaning
the paper never states, and excisional biopsy is a deliberate diagnostic act that in many series is
planned. Both are recorded as `candidate_proxies` with `is_the_thing: False`.

⛔ NOTHING IS POOLED ACROSS THE TWO COHORTS. `systems/POLICY-evidence.md` 2.3 refuses to pool
populations that may overlap and 2.1 requires comparable denominators; these two share neither an
era (1980-2018 against 2002-2022), a setting (two referral centres against a national registry), nor
a denominator convention (Chiusole's margin denominator is the 40 patients for whom the field was
available, not its 49 treated with curative intent). Each rate stands alone with its own Wilson
interval.

⛔ SCOPE. Margin status is an association with outcome in retrospective series, not a demonstrated
effect of operating differently, and the direction is confounded by everything that makes a tumour
hard to resect. Nothing here asserts efficacy, safety or clinical readiness, and nothing here is
medical advice.

Run:     python3 research/modalities/emc_surgical_quality.py
Verify:  python3 research/modalities/emc_surgical_quality.py --check
Writes:  research/modalities/emc-surgical-quality.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-surgical-quality.json")

sys.path.insert(0, HERE)
from emc_locoregional_eligibility import wilson  # noqa: E402  -- one Wilson, one home

# ---------------------------------------------------------------------------
# the transcription
# ---------------------------------------------------------------------------
# ⛔ EVERY COUNT IS PRINTED. `printed_in` names the table or the sentence it came from. Percentages
# the papers print are recorded ONLY where they disagree with the arithmetic, because a percentage
# recomputed from counts is a derivation and a percentage transcribed is a second home for one fact.

SERIES = [
    {
        "source_id": "masunaga2025",
        "setting": "Japanese National Bone and Soft Tissue Tumor Registry -- a national registry, "
                   "2002-2022",
        "registered": 171,
        "printed_in": "Table 1, 'Surgical margin, n (%)' row, 'Total patients (N = 171)' column",
        "margin_all_registered": {"R0": 117, "R1": 30, "R2": 9, "no_surgery": 15},
        "printed_in_nonmetastatic": "Table 1, same row, 'Metastases at diagnosis: No (N = 142)' column",
        "margin_nonmetastatic": {"R0": 104, "R1": 22, "R2": 8, "no_surgery": 8},
        "printed_in_metastatic": "Table 1, same row, 'Metastases at diagnosis: Yes (N = 29)' column",
        "margin_metastatic": {"R0": 13, "R1": 8, "R2": 1, "no_surgery": 7},
        "margin_definition_printed": (
            "Methods: 'microscopically negative margins were defined as [R0], macroscopically "
            "negative but microscopically positive margins as [R1], and macroscopically positive "
            "margins as [R2]'. ⭐ THE DEFINITION IS PRINTED, WHICH IS NOT THE NORM -- it is what "
            "lets these counts be compared to another series at all, and Chiusole's wording is "
            "compatible with it."),
        "candidate_proxies_for_unplanned_excision": {
            "previous_surgery_yes": 18,
            "previous_surgery_no": 153,
            "excisional_biopsy": 10,
            "biopsy_none": 19,
            "is_the_thing": False,
            "⛔_why_not": (
                "The paper lists 'previous surgery' among the fields extracted from the database and "
                "never defines it, while it DOES define R0/R1/R2 in the same sentence -- so the "
                "omission is visible rather than assumed. An excisional biopsy is a deliberate "
                "diagnostic act. Either could be an unplanned excision and neither is stated to be, "
                "so no unplanned-excision rate is computed from them."),
        },
        "treatment_setting_printed": None,
        "⛔_setting_absent": (
            "No centre, centre volume or referral status is printed for any patient. A national "
            "registry could in principle carry it; this publication does not report it."),
    },
    {
        "source_id": "chiusole2020",
        "setting": "Istituto Oncologico Veneto and Institut Gustave Roussy -- two referral centres, "
                   "1980-2018",
        "registered": 59,
        "printed_in": "Table 2 'Outcome of surgery', corroborated by the Results sentence 'Data on "
                      "extension surgery were available for 40 patients: 26 had radical (R0) "
                      "surgery, 12 patients had surgery with microscopic margin infiltration (R1), "
                      "and 2 patients had macroscopic presence of tumor (R2)'",
        "margin_where_available": {"R0": 26, "R1": 12, "R2": 2},
        "margin_field_available_for": 40,
        "treated_with_curative_intent": 49,
        "⚠_informative_missingness": (
            "The margin field is available for 40 patients while 49 were treated with curative "
            "intent, so 9 are missing -- 18 % of the curative-intent group. The paper does not say "
            "who they are. Missingness in a margin field is not plausibly random: an operation "
            "whose margin nobody recorded is more likely to have happened long ago or elsewhere, "
            "and this series reaches back to 1980. The rate below therefore has a denominator of "
            "40 and is NOT a rate over the curative-intent cohort."),
        "outcome_by_margin": {
            "R0": {"n": 26, "local_recurrence": 2, "metastases": 4},
            "R1": {"n": 12, "local_recurrence": 5, "metastases": 7},
            "R2": {"n": 2, "local_recurrence": None, "metastases": None,
                   "⛔_printed_as_NA": (
                       "Table 2 prints NA for both outcomes at R2. The text accounts for the two "
                       "patients individually -- one was metastatic and had no further surgery, the "
                       "other had no local recurrence after re-excision and radiotherapy -- which "
                       "is why the table refuses a rate over n = 2 rather than printing 50 %.")},
        },
        "⚠_table_vs_text_arithmetic": (
            "Table 2 prints the R0 metastasis rate as 15.2 % and the Results text prints the same "
            "4 of 26 as 15.4 %. 4/26 = 15.38 %, so the text is right. The paper's other three cells "
            "TRUNCATE rather than round -- 2/26 = 7.69 printed 7.6, 5/12 = 41.67 printed 41.6, "
            "7/12 = 58.33 printed 58.3 -- and truncation of 15.38 gives 15.3, not 15.2. So 15.2 % "
            "is anomalous under the paper's own convention and is most likely a typo. RECORDED, NOT "
            "RESOLVED: this module transcribes counts and derives its own percentages, so nothing "
            "here depends on which printing is right. ⛔ This is the THIRD independent table-vs-text "
            "discrepancy found in this source -- emc-site-curation.json records one in its site "
            "counts and emc-prognostic-coefficients.json records the univariate/multivariate label "
            "-- which is itself worth carrying when weighting it."),
        "margin_definition_printed": (
            "Results: R0 as 'radical', R1 as 'surgery with microscopic margin infiltration', R2 as "
            "'macroscopic presence of tumor'. Compatible with Masunaga's explicit definition."),
        "treatment_setting_printed": None,
        "⛔_setting_absent": (
            "Every patient in this series was treated at one of two sarcoma referral centres, so the "
            "exposure the route asks about is held CONSTANT. That is not a missing field; it is a "
            "cohort that cannot answer the question by construction, and it would stay unanswerable "
            "however completely this paper were curated."),
    },
]

# ---------------------------------------------------------------------------
# derivations
# ---------------------------------------------------------------------------


def _rate(events: int, denom: int) -> dict:
    p, lo, hi = wilson(events, denom)
    return {"events": events, "denominator": denom,
            "proportion": round(p, 4), "wilson95": [round(lo, 4), round(hi, 4)]}


def masunaga_rates(s: dict) -> dict:
    """Positive-margin rate over each defensible denominator, none of them elected."""
    def operated(m):
        return m["R0"] + m["R1"] + m["R2"]

    def positive(m):
        return m["R1"] + m["R2"]

    allreg, non, met = (s["margin_all_registered"], s["margin_nonmetastatic"],
                        s["margin_metastatic"])
    return {
        "positive_margin_among_all_operated": _rate(positive(allreg), operated(allreg)),
        "positive_margin_among_operated_localized_at_diagnosis":
            _rate(positive(non), operated(non)),
        "positive_margin_among_operated_metastatic_at_diagnosis":
            _rate(positive(met), operated(met)),
        "not_operated_at_all_among_registered":
            _rate(allreg["no_surgery"], s["registered"]),
        "⭐_the_denominators_are_not_interchangeable": (
            "Patients already metastatic at diagnosis were operated to a positive margin far more "
            "often than patients who were not, so a 'positive-margin rate' quoted without its "
            "denominator can move by nearly twenty points inside one paper. The metastatic figure "
            "rests on 22 operated patients and its interval is correspondingly wide; the direction "
            "is what is worth carrying, not the point estimate."),
        "⚠_this_is_not_a_quality_metric": (
            "A positive margin in a metastatic patient is frequently a deliberate choice -- "
            "debulking, symptom control, or an operation whose goal was never clearance. Reading "
            "any of these rates as surgical performance requires knowing the INTENT of each "
            "operation, which neither paper prints."),
    }


def chiusole_rates(s: dict) -> dict:
    m = s["margin_where_available"]
    operated = m["R0"] + m["R1"] + m["R2"]
    out = {
        "positive_margin_among_those_with_the_field_recorded":
            _rate(m["R1"] + m["R2"], operated),
        "⛔_no_rate_over_the_curative_intent_cohort": (
            "The field is recorded for 40 of the 49 treated with curative intent. A rate over 49 "
            "would require assuming the 9 missing resemble the 40, which informative missingness "
            "makes the least safe assumption available. Not computed."),
    }
    # Outcome by margin, R0 vs R1 only -- R2 is n = 2 and the paper itself refuses a rate there.
    by = s["outcome_by_margin"]
    for arm in ("R0", "R1"):
        a = by[arm]
        out[f"local_recurrence_{arm}"] = _rate(a["local_recurrence"], a["n"])
        out[f"metastases_{arm}"] = _rate(a["metastases"], a["n"])
    out["⭐_the_contrast"] = (
        "Local recurrence 2 of 26 after R0 against 5 of 12 after R1; metastases 4 of 26 against 7 "
        "of 12. Both intervals are wide and both overlap, so this is a DIRECTION from 38 patients, "
        "not an effect size. ⛔ AND IT IS CONFOUNDED IN THE OBVIOUS WAY: whatever made a tumour "
        "impossible to clear -- size, site, proximity to a neurovascular bundle -- is also a reason "
        "it recurs and spreads. The margin is a marker of the tumour as much as of the operation.")
    out["⛔_no_intervals_at_R2"] = "n = 2, and the paper prints NA rather than a rate. Not computed."
    return out


def build() -> dict:
    mas = next(s for s in SERIES if s["source_id"] == "masunaga2025")
    chi = next(s for s in SERIES if s["source_id"] == "chiusole2020")
    mr, cr = masunaga_rates(mas), chiusole_rates(chi)

    return {
        "_what": ("Surgical margin distribution, outcome by margin, and the treatment-setting and "
                  "unplanned-excision fields, curated from the two reachable open-access EMC series."),
        "_not_medical_advice": ("Nothing here is medical advice, and nothing here asserts efficacy, "
                                "safety or clinical readiness. Margin status is an association with "
                                "outcome in retrospective series, not a demonstrated effect of "
                                "operating differently."),
        "_generated_by": "research/modalities/emc_surgical_quality.py",
        "⭐_the_route_question_this_answers": {
            "route": "RT-SURGICAL-QUALITY",
            "unknown": ("What the positive-margin rate in EMC actually is -- no cohort in the "
                        "registry carries a margin field, and the one dedicated EMC surgical series "
                        "reports a single positive margin in 13 patients."),
            "answer": ("Two series print full margin distributions, over 156 and 40 operated "
                       "patients rather than 13. The positive-margin rate is 25.0 % across all of "
                       "Masunaga's operated patients, 22.4 % among those localized at diagnosis, "
                       "40.9 % among those already metastatic, and 35.0 % in Chiusole where the "
                       "field was recorded. ⛔ THE RANGE IS THE RESULT: there is no single EMC "
                       "positive-margin rate, because the denominator choice moves it by more than "
                       "the width of any of the intervals."),
            "⚠_still_open": ("The route's SECOND unknown -- whether a sarcoma referral centre "
                             "changes EMC outcomes -- is not advanced and cannot be by these two "
                             "sources. See treatment_setting."),
        },
        "series": SERIES,
        "masunaga2025_rates": mr,
        "chiusole2020_rates": cr,
        "treatment_setting": {
            "recorded_in_any_reachable_series": False,
            "⛔_this_is_a_reading_not_a_gap": (
                "Masunaga prints no centre, centre volume or referral status; Chiusole is entirely "
                "referral-centre care with no comparator. One does not report the exposure and the "
                "other holds it constant, so neither can answer the referral question and further "
                "curation of them will not change that. Recorded so a later session does not spend "
                "the effort a second time."),
            "what_would_answer_it": (
                "A series that reports where each patient was first operated, or a registry linkage "
                "carrying centre volume. Neither exists among the reachable open-access EMC "
                "literature (emc-km-reachability-census-2026-08-25.json)."),
        },
        "unplanned_excision": {
            "recorded_in_any_reachable_series": False,
            "candidate_proxies": mas["candidate_proxies_for_unplanned_excision"],
        },
        "⛔_nothing_is_pooled": (
            "The two series share neither era (1980-2018 against 2002-2022), setting (two referral "
            "centres against a national registry) nor denominator convention (Chiusole's is the 40 "
            "with the field recorded, not its 49 treated with curative intent). POLICY-evidence 2.1 "
            "requires comparable denominators and 2.3 refuses populations that may overlap. Each "
            "rate stands alone with its own Wilson interval and no combined figure is computed."),
        "counts": {
            "series": len(SERIES),
            "operated_patients_with_a_margin_recorded":
                sum(v for k, v in mas["margin_all_registered"].items() if k != "no_surgery")
                + sum(chi["margin_where_available"].values()),
        },
    }


# ---------------------------------------------------------------------------
# guards
# ---------------------------------------------------------------------------


def _check_structure() -> list[str]:
    errs: list[str] = []
    mas = next(s for s in SERIES if s["source_id"] == "masunaga2025")
    chi = next(s for s in SERIES if s["source_id"] == "chiusole2020")

    # Every Masunaga margin column must partition its own printed denominator.
    for key, denom in (("margin_all_registered", 171),
                       ("margin_nonmetastatic", 142),
                       ("margin_metastatic", 29)):
        got = sum(mas[key].values())
        if got != denom:
            errs.append(f"masunaga {key} sums to {got}, not the printed {denom}")

    # The three columns must also be consistent with each other, cell by cell.
    for cell in ("R0", "R1", "R2", "no_surgery"):
        lhs = mas["margin_nonmetastatic"][cell] + mas["margin_metastatic"][cell]
        rhs = mas["margin_all_registered"][cell]
        if lhs != rhs:
            errs.append(f"masunaga {cell}: non-metastatic + metastatic = {lhs}, total column {rhs}")

    if sum(chi["margin_where_available"].values()) != chi["margin_field_available_for"]:
        errs.append("chiusole margin counts do not sum to the number of patients with the field")
    if chi["margin_field_available_for"] > chi["treated_with_curative_intent"]:
        errs.append("chiusole margin field is recorded for more patients than were treated "
                    "with curative intent")

    # Outcome counts may never exceed their arm.
    for arm, a in chi["outcome_by_margin"].items():
        for k in ("local_recurrence", "metastases"):
            if a[k] is not None and a[k] > a["n"]:
                errs.append(f"chiusole {arm}: {k} = {a[k]} exceeds arm n = {a['n']}")

    # The unplanned-excision proxies must keep saying they are not the thing.
    if mas["candidate_proxies_for_unplanned_excision"].get("is_the_thing") is not False:
        errs.append("the unplanned-excision proxies no longer declare that they are proxies")
    return errs


def cross_check_against_the_cox_tables() -> list[str]:
    """⭐ THE STRONGEST GUARD HERE, BECAUSE IT NEEDS A SECOND MODULE TO AGREE.

    `emc_prognostic_coefficients` transcribes Masunaga's Cox tables, which report the 134 modelled
    patients as R0 = 104 and R1-or-R2 = 30. Those 134 are the 142 non-metastatic patients minus the
    8 who had no surgery. Table 1's margin row and the Cox tables were typed from different pages by
    different passes, so agreement here is a real check and disagreement means one of them is wrong.
    """
    errs: list[str] = []
    try:
        import emc_prognostic_coefficients as pc
    except Exception as exc:  # pragma: no cover - an import failure is itself the finding
        return [f"could not import emc_prognostic_coefficients to cross-check: {exc}"]

    mas = next(s for s in SERIES if s["source_id"] == "masunaga2025")
    non = mas["margin_nonmetastatic"]
    expected = {"R0": non["R0"], "R1_or_R2": non["R1"] + non["R2"]}
    operated = expected["R0"] + expected["R1_or_R2"]

    for m in pc.MODELS:
        if m["source_id"] != "masunaga2025":
            continue
        if m["n"] != operated:
            errs.append(f"{m['model_id']}: modelled n = {m['n']}, but Table 1 gives {operated} "
                        f"non-metastatic operated patients")
        for r in m["rows"]:
            if r["variable"] != "surgical_margin" or r["n"] is None:
                continue
            want = expected.get(r["level"])
            if want is not None and r["n"] != want:
                errs.append(f"{m['model_id']}: surgical_margin/{r['level']} n = {r['n']}, "
                            f"Table 1 implies {want}")
    return errs


def check() -> int:
    errs = _check_structure() + cross_check_against_the_cox_tables()
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
    print(f"emc_surgical_quality --check OK "
          f"({doc['counts']['operated_patients_with_a_margin_recorded']} operated patients with a "
          f"margin recorded, across {doc['counts']['series']} series)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the artifact reproduces and every guard holds")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    errs = _check_structure() + cross_check_against_the_cox_tables()
    for e in errs:
        print(f"ERROR: {e}")
    if errs:
        return 1
    doc = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}")
    for k, v in doc["masunaga2025_rates"].items():
        if isinstance(v, dict):
            print(f"  masunaga  {k}: {v['events']}/{v['denominator']} = {v['proportion']:.3f} "
                  f"[{v['wilson95'][0]:.3f}, {v['wilson95'][1]:.3f}]")
    v = doc["chiusole2020_rates"]["positive_margin_among_those_with_the_field_recorded"]
    print(f"  chiusole  positive margin: {v['events']}/{v['denominator']} = {v['proportion']:.3f} "
          f"[{v['wilson95'][0]:.3f}, {v['wilson95'][1]:.3f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
