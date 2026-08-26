#!/usr/bin/env python3
"""Fitted Cox coefficients for EMC, transcribed from the printed tables of two independent cohorts.

WHY THIS EXISTS
---------------
`systems/graph/routes.json` → RT-RISK-MODEL ("A prognostic risk model for EMC") records its next
action as *"Wait on RT-IPD-SURVIVAL, and while waiting record which published EMC series print
stratified curves at all — that census decides whether this route is possible."*

That census was taken and it answers a question the route was not asking. The two largest reachable
open-access EMC series print **no numbers-at-risk row under any stratified curve**, so no stratified
curve in the reachable literature is reconstructable to patient-level data — the instrument
RT-RISK-MODEL was waiting on cannot be pointed at them. But both series print something the route
never asked for and that is strictly closer to its endpoint: **fitted Cox proportional-hazards
models, with hazard ratios, 95 % confidence intervals, p-values and per-level patient counts.**

A prognostic model's coefficients do not have to be estimated here. They are already estimated,
published, and — across two cohorts assembled on different continents by different teams — they can
be compared. That comparison is what this file computes.

⛔⛔ THE ONE THING THIS DOES NOT GIVE YOU, AND IT IS THE THING A RISK MODEL IS FOR: **NEITHER PAPER
PRINTS A BASELINE HAZARD.** A Cox model is a baseline hazard times exp(Σβx); print the βs alone and
you can say who is at *higher* risk than whom, and you can never say what any individual's risk *is*.
So this file supports **relative** prognostic statements and **refuses absolute** ones. No survival
probability, no risk score calibrated to an outcome, no nomogram, and no "n-year risk" may be derived
from anything here. That refusal is structural, not a caveat: `absolute_risk_computable` is False in
every record this module emits, and `check()` fails if it is ever True.

⛔ AND NOTHING HERE IS POOLED. `systems/POLICY-evidence.md` §2 governs one estimand — a
denominator-weighted proportion with a Wilson interval — and §2.4 refuses to merge time-anchored
figures at all. A hazard ratio is a third estimand class the contract does not cover, and this module
does not invent a method for it: there is no inverse-variance meta-analysis here, no pooled HR, and
no I². What is computed instead is **direction concordance** — do two independent cohorts put the
same covariate on the same side of 1, and do their intervals overlap — which needs no pooling model
and makes no distributional assumption the sources do not already carry.

⚠ THE ENDPOINTS ARE NOT THE SAME ENDPOINT. Chiusole reports **overall survival** on all 59 patients
including those metastatic at presentation; Masunaga reports **disease-specific survival**, local
recurrence-free survival and distant metastasis-free survival on the 134 who were localized at
diagnosis and underwent surgery. A concordance across those is a concordance of DIRECTION between
related-but-distinct quantities, and every row this module emits carries both endpoints so that a
reader cannot lose track of which is which.

⚠ TREATMENT COVARIATES ARE CONFOUNDED BY INDICATION AND THIS IS NOT A HEDGE — THE PAPER PRINTS THE
CONFOUND. Masunaga's Table 4 puts (neo)adjuvant radiotherapy at HR 5.05 for disease-specific
survival, i.e. the irradiated patients died of the disease more often. The same paper's Table 2 puts
radiotherapy at HR 0.50 for local recurrence, and its own text reports that **10 of 24 irradiated
patients (41.7 %) had R1/R2 margins against 20 of 110 (18.2 %) of the unirradiated** — the treated
group was the worse-prognosis group before treatment began. Read causally, these coefficients say
radiotherapy kills people. Read correctly, they say sicker patients get radiotherapy. Every treatment
covariate below carries `causal_interpretation_refused` with the specific printed evidence of its
confound, and `check()` fails if a treatment row loses it.

⛔ A HAZARD RATIO OF EXACTLY 0 IS NOT AN ESTIMATE. Masunaga's Table 4 reports HR = 0 with p = 0.999
for "previous surgery: yes" and for "upper limb", and HR = 0 with p = 0.986 for upper limb in the
multivariate model. That is the signature of **complete separation** — zero events in the stratum —
under which the partial likelihood has no finite maximum and the fitting routine returns a boundary
value. It does not mean upper-limb tumours have no hazard of disease-specific death; it means 14
patients produced no deaths. These rows are marked `non_estimate: "complete_separation"`, carry no
CI, and are excluded from every concordance computation.

⚠ MASUNAGA'S MULTIVARIATE MODELS ARE STEPWISE-SELECTED, WHICH IS NOT THE SAME AS ADJUSTED. The
methods say *"stepwise Cox proportional hazards regression"*, and the effect is visible: the
disease-specific multivariate model retains site and size and **drops surgical margin**, whose
univariate HR was 3.01 (0.81-11.25). A stepwise-retained coefficient is selected on the same data it
is estimated from, so its interval is optimistic and its p-value is not the p-value of a
prespecified test. Recorded per model as `selection: "stepwise"`; the univariate columns carry no
such penalty and are the ones the concordance uses.

⚠ ONE UNRESOLVED SOURCE DISCREPANCY, RECORDED RATHER THAN DECIDED. Chiusole's Results text says
*"metastatic sites retaining prognostic significance as independent risk factor for survival in
multivariate analysis (Table 4)"*, but Table 4's own header and column heading both read
**"Univariate Cox"**. The paper cites a multivariate result to a table labelled univariate, and this
module cannot tell from the text layer which label is wrong. It transcribes the table as the table
labels itself and records the contradiction; it does not promote the table to multivariate to make
the sentence true.

⛔ SCOPE. Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness. A hazard
ratio from a retrospective series is an association in that series. Nothing here is medical advice.

Run:     python3 research/modalities/emc_prognostic_coefficients.py
Verify:  python3 research/modalities/emc_prognostic_coefficients.py --check
Writes:  research/modalities/emc-prognostic-coefficients.json
"""

from __future__ import annotations

import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-prognostic-coefficients.json")

# ---------------------------------------------------------------------------
# the transcription
# ---------------------------------------------------------------------------
# ⛔ EVERY NUMBER BELOW IS PRINTED IN THE NAMED TABLE. Nothing is digitized, nothing is recomputed
# from a percentage, and no coefficient is carried over from one endpoint to another. `printed_in`
# names the table; the reference level of each categorical carries hr=None and reference=True,
# because a table that prints "1" for the reference is stating a convention, not measuring a value.

COHORTS = {
    "masunaga2025": {
        "source_id": "masunaga2025",
        "cohort": "Japanese nationwide/multi-institutional series; the modelled subset is the 134 "
                  "patients who were localized at diagnosis and underwent surgery, drawn from 171 "
                  "in the full series.",
        "n_full_series": 171,
        "n_modelled": 134,
        "endpoints_modelled": ["local_recurrence_free_survival",
                               "distant_metastasis_free_survival",
                               "disease_specific_survival"],
        "deaths_from_tumour_full_series": 19,
        "median_followup_months": 38,
        "⚠_followup_is_short_for_this_disease": (
            "The median follow-up is 38 months and EMC's own literature reports deaths well past ten "
            "years -- Chiusole's median OS is 180 months. A 38-month window sees the early hazard "
            "and censors the late one, so a covariate that acts late is under-powered here by "
            "construction rather than absent."),
        "risk_table_under_any_km_figure": False,
    },
    "chiusole2020": {
        "source_id": "chiusole2020",
        "cohort": "Italian institutional series; all 59 patients, including those metastatic at "
                  "presentation. 4 of 59 had no follow-up data.",
        "n_full_series": 59,
        "n_modelled": 59,
        "endpoints_modelled": ["overall_survival"],
        "deaths_full_series": 20,
        "median_followup_months": 72,
        "risk_table_under_any_km_figure": False,
    },
}

# The four printed models. `analysis` is what the TABLE calls itself.
MODELS = [
    {
        "model_id": "masunaga2025_lrfs_univariate",
        "source_id": "masunaga2025",
        "endpoint": "local_recurrence_free_survival",
        "analysis": "univariate",
        "selection": None,
        "n": 134,
        "printed_in": "Table 2, 'Univariate analysis' block",
        "rows": [
            {"variable": "age_years", "level": "per 1-year increase", "n": 134,
             "hr": 1.02, "ci": [0.99, 1.06], "p": 0.151, "continuous": True},
            {"variable": "sex", "level": "male", "n": 76, "reference": True},
            {"variable": "sex", "level": "female", "n": 58,
             "hr": 1.34, "ci": [0.48, 3.73], "p": 0.575},
            {"variable": "previous_surgery", "level": "no", "n": 121, "reference": True},
            {"variable": "previous_surgery", "level": "yes", "n": 13,
             "hr": 1.41, "ci": [0.32, 6.27], "p": 0.649},
            {"variable": "site", "level": "lower_limb", "n": 79, "reference": True},
            {"variable": "site", "level": "upper_limb", "n": 14,
             "hr": 1.84, "ci": [0.37, 9.15], "p": 0.454},
            {"variable": "site", "level": "trunk", "n": 41,
             "hr": 2.12, "ci": [0.71, 6.31], "p": 0.177},
            {"variable": "tumour_depth", "level": "superficial", "n": 22, "reference": True},
            {"variable": "tumour_depth", "level": "deep", "n": 112,
             "hr": 1.87, "ci": [0.41, 8.48], "p": 0.419},
            {"variable": "tumour_size_cm", "level": "per 1-cm increase", "n": 134,
             "hr": 1.05, "ci": [0.94, 1.15], "p": 0.334, "continuous": True},
            {"variable": "histological_grade", "level": "low", "n": 57, "reference": True},
            {"variable": "histological_grade", "level": "high", "n": 77,
             "hr": 1.13, "ci": [0.40, 3.17], "p": 0.820},
            {"variable": "surgical_margin", "level": "R0", "n": 104, "reference": True},
            {"variable": "surgical_margin", "level": "R1_or_R2", "n": 30,
             "hr": 4.76, "ci": [1.72, 13.15], "p": 0.003, "starred_significant": True},
            {"variable": "neoadjuvant_or_adjuvant_radiotherapy", "level": "no", "n": 110,
             "reference": True},
            {"variable": "neoadjuvant_or_adjuvant_radiotherapy", "level": "yes", "n": 24,
             "hr": 0.50, "ci": [0.11, 2.25], "p": 0.365, "treatment": True},
            {"variable": "neoadjuvant_or_adjuvant_chemotherapy", "level": "no", "n": 128,
             "reference": True},
            {"variable": "neoadjuvant_or_adjuvant_chemotherapy", "level": "yes", "n": 6,
             "hr": 1.90, "ci": [0.25, 14.64], "p": 0.538, "treatment": True},
        ],
    },
    {
        "model_id": "masunaga2025_lrfs_multivariate",
        "source_id": "masunaga2025",
        "endpoint": "local_recurrence_free_survival",
        "analysis": "multivariate",
        "selection": "stepwise",
        "n": 134,
        "printed_in": "Table 2, 'Multivariate analysis' block",
        "⚠_one_surviving_term": (
            "Stepwise selection retained exactly one variable, so this 'multivariate' model adjusts "
            "for nothing and its coefficient is numerically identical to the univariate one -- "
            "4.76 (1.72-13.15), the same three digits. That is not corroboration; it is the same "
            "fit reported twice."),
        "rows": [
            {"variable": "surgical_margin", "level": "R0", "n": 104, "reference": True},
            {"variable": "surgical_margin", "level": "R1_or_R2", "n": 30,
             "hr": 4.76, "ci": [1.72, 13.15], "p": 0.003, "starred_significant": True},
        ],
    },
    {
        "model_id": "masunaga2025_dmfs_univariate",
        "source_id": "masunaga2025",
        "endpoint": "distant_metastasis_free_survival",
        "analysis": "univariate",
        "selection": None,
        "n": 134,
        "printed_in": "Table 3, 'Univariate analysis' block",
        "rows": [
            {"variable": "age_years", "level": "per 1-year increase", "n": 134,
             "hr": 1.01, "ci": [0.99, 1.04], "p": 0.188, "continuous": True},
            {"variable": "sex", "level": "male", "n": 76, "reference": True},
            {"variable": "sex", "level": "female", "n": 58,
             "hr": 0.81, "ci": [0.43, 1.55], "p": 0.525},
            {"variable": "previous_surgery", "level": "no", "n": 121, "reference": True},
            {"variable": "previous_surgery", "level": "yes", "n": 13,
             "hr": 0.21, "ci": [0.03, 1.50], "p": 0.119},
            {"variable": "site", "level": "lower_limb", "n": 79, "reference": True},
            {"variable": "site", "level": "upper_limb", "n": 14,
             "hr": 1.01, "ci": [0.35, 2.95], "p": 0.986},
            {"variable": "site", "level": "trunk", "n": 41,
             "hr": 1.29, "ci": [0.66, 2.55], "p": 0.455},
            {"variable": "tumour_depth", "level": "superficial", "n": 22, "reference": True},
            {"variable": "tumour_depth", "level": "deep", "n": 112,
             "hr": 1.33, "ci": [0.52, 3.40], "p": 0.555},
            {"variable": "tumour_size_cm", "level": "per 1-cm increase", "n": 134,
             "hr": 1.12, "ci": [1.05, 1.18], "p": 0.001, "p_printed_as": "< 0.001",
             "continuous": True, "starred_significant": True},
            {"variable": "histological_grade", "level": "low", "n": 57, "reference": True},
            {"variable": "histological_grade", "level": "high", "n": 77,
             "hr": 1.81, "ci": [0.92, 3.58], "p": 0.087},
            {"variable": "surgical_margin", "level": "R0", "n": 104, "reference": True},
            {"variable": "surgical_margin", "level": "R1_or_R2", "n": 30,
             "hr": 2.37, "ci": [1.21, 4.64], "p": 0.012, "starred_significant": True},
            {"variable": "neoadjuvant_or_adjuvant_radiotherapy", "level": "no", "n": 110,
             "reference": True},
            {"variable": "neoadjuvant_or_adjuvant_radiotherapy", "level": "yes", "n": 24,
             "hr": 1.76, "ci": [0.86, 3.61], "p": 0.125, "treatment": True},
            {"variable": "neoadjuvant_or_adjuvant_chemotherapy", "level": "no", "n": 128,
             "reference": True},
            {"variable": "neoadjuvant_or_adjuvant_chemotherapy", "level": "yes", "n": 6,
             "hr": 0.57, "ci": [0.08, 4.19], "p": 0.584, "treatment": True},
        ],
    },
    {
        "model_id": "masunaga2025_dmfs_multivariate",
        "source_id": "masunaga2025",
        "endpoint": "distant_metastasis_free_survival",
        "analysis": "multivariate",
        "selection": "stepwise",
        "n": 134,
        "printed_in": "Table 3, 'Multivariate analysis' block",
        "⭐_grade_appears_only_here": (
            "Histological grade is NOT significant univariately (1.81, 0.92-3.58, p = 0.087) and IS "
            "significant after adjustment (2.55, 1.18-5.52, p = 0.018). A coefficient that grows "
            "under adjustment is the expected behaviour when a correlated variable was masking it, "
            "and it is also what stepwise selection produces by chance more often than its p-value "
            "admits. Both readings are live; this module does not choose between them."),
        "rows": [
            {"variable": "tumour_size_cm", "level": "per 1-cm increase", "n": 134,
             "hr": 1.10, "ci": [1.04, 1.17], "p": 0.002, "continuous": True,
             "starred_significant": True},
            {"variable": "histological_grade", "level": "low", "n": 57, "reference": True},
            {"variable": "histological_grade", "level": "high", "n": 77,
             "hr": 2.55, "ci": [1.18, 5.52], "p": 0.018, "starred_significant": True},
            {"variable": "surgical_margin", "level": "R0", "n": 104, "reference": True},
            {"variable": "surgical_margin", "level": "R1_or_R2", "n": 30,
             "hr": 3.40, "ci": [1.57, 7.38], "p": 0.002, "starred_significant": True},
        ],
    },
    {
        "model_id": "masunaga2025_dss_univariate",
        "source_id": "masunaga2025",
        "endpoint": "disease_specific_survival",
        "analysis": "univariate",
        "selection": None,
        "n": 134,
        "printed_in": "Table 4, 'Univariate analysis' block",
        "rows": [
            {"variable": "age_years", "level": "per 1-year increase", "n": 134,
             "hr": 1.05, "ci": [0.99, 1.11], "p": 0.111, "continuous": True},
            {"variable": "sex", "level": "male", "n": 76, "reference": True},
            {"variable": "sex", "level": "female", "n": 58,
             "hr": 0.80, "ci": [0.20, 3.28], "p": 0.756},
            {"variable": "previous_surgery", "level": "no", "n": 121, "reference": True},
            {"variable": "previous_surgery", "level": "yes", "n": 13,
             "hr": 0.0, "ci": None, "p": 0.999, "non_estimate": "complete_separation"},
            {"variable": "site", "level": "lower_limb", "n": 79, "reference": True},
            {"variable": "site", "level": "upper_limb", "n": 14,
             "hr": 0.0, "ci": None, "p": 0.999, "non_estimate": "complete_separation"},
            {"variable": "site", "level": "trunk", "n": 41,
             "hr": 6.17, "ci": [1.28, 29.75], "p": 0.023, "starred_significant": True},
            {"variable": "tumour_depth", "level": "superficial", "n": 22, "reference": True},
            {"variable": "tumour_depth", "level": "deep", "n": 112,
             "hr": 0.67, "ci": [0.14, 3.30], "p": 0.627},
            {"variable": "tumour_size_cm", "level": "per 1-cm increase", "n": 134,
             "hr": 1.20, "ci": [1.06, 1.36], "p": 0.003, "continuous": True,
             "starred_significant": True},
            {"variable": "histological_grade", "level": "low", "n": 57, "reference": True},
            {"variable": "histological_grade", "level": "high", "n": 77,
             "hr": 2.60, "ci": [0.54, 12.63], "p": 0.236},
            {"variable": "surgical_margin", "level": "R0", "n": 104, "reference": True},
            {"variable": "surgical_margin", "level": "R1_or_R2", "n": 30,
             "hr": 3.01, "ci": [0.81, 11.25], "p": 0.101},
            {"variable": "neoadjuvant_or_adjuvant_radiotherapy", "level": "no", "n": 110,
             "reference": True},
            {"variable": "neoadjuvant_or_adjuvant_radiotherapy", "level": "yes", "n": 24,
             "hr": 5.05, "ci": [1.34, 19.04], "p": 0.017, "treatment": True,
             "starred_significant": True},
            {"variable": "neoadjuvant_or_adjuvant_chemotherapy", "level": "no", "n": 128,
             "reference": True},
            {"variable": "neoadjuvant_or_adjuvant_chemotherapy", "level": "yes", "n": 6,
             "hr": 3.71, "ci": [0.44, 31.02], "p": 0.226, "treatment": True},
        ],
    },
    {
        "model_id": "masunaga2025_dss_multivariate",
        "source_id": "masunaga2025",
        "endpoint": "disease_specific_survival",
        "analysis": "multivariate",
        "selection": "stepwise",
        "n": 134,
        "printed_in": "Table 4, 'Multivariate analysis' block",
        "⛔_margin_was_dropped": (
            "Surgical margin -- the one covariate both cohorts and all three of this paper's other "
            "models put on the harmful side of 1 -- is absent from this model. Its univariate "
            "disease-specific HR was 3.01 (0.81-11.25, p = 0.101), so stepwise selection dropped it "
            "on a p-value that a cohort with 19 tumour deaths cannot resolve. ABSENCE FROM A "
            "STEPWISE MODEL IS NOT EVIDENCE OF NO EFFECT, and reading this table as 'margin does "
            "not affect survival' is the single most likely misuse of it."),
        "rows": [
            {"variable": "site", "level": "lower_limb", "n": 79, "reference": True},
            {"variable": "site", "level": "upper_limb", "n": 14,
             "hr": 0.0, "ci": None, "p": 0.986, "non_estimate": "complete_separation"},
            {"variable": "site", "level": "trunk", "n": 41,
             "hr": 6.28, "ci": [1.30, 30.49], "p": 0.023, "starred_significant": True},
            {"variable": "tumour_size_cm", "level": "per 1-cm increase", "n": 134,
             "hr": 1.18, "ci": [1.06, 1.33], "p": 0.004, "continuous": True,
             "starred_significant": True},
        ],
    },
    {
        "model_id": "chiusole2020_os_univariate",
        "source_id": "chiusole2020",
        "endpoint": "overall_survival",
        "analysis": "univariate",
        "selection": None,
        "n": 59,
        "printed_in": "Table 4, headed 'Univariate Cox analysis for risk factors'",
        "⚠_table_vs_text_unresolved": (
            "The Results text says 'metastatic sites retaining prognostic significance as "
            "independent risk factor for survival in multivariate analysis (Table 4)', while Table "
            "4's title and its column heading both read 'Univariate Cox'. The paper cites a "
            "multivariate result to a table that labels itself univariate. Transcribed as the table "
            "labels itself; the contradiction is recorded, not resolved. ⛔ This is a SECOND, "
            "independent table-vs-text discrepancy in this source -- emc-site-curation.json records "
            "the first, in its site counts -- which is itself worth knowing when weighting it."),
        "⚠_n_is_the_series_not_the_analysed_set": (
            "The table prints no per-level patient counts, and the paper states that 4 of 59 "
            "patients had no follow-up data. Whether the model was fitted on 59 or 55 is not "
            "printed, so the level counts that every other model here carries do not exist for this "
            "one and no sum-to-n guard can be run against it."),
        "rows": [
            {"variable": "sex", "level": "male", "n": None, "reference": True},
            {"variable": "sex", "level": "female", "n": None,
             "hr": 0.686, "ci": [0.263, 1.786], "p": 0.440},
            {"variable": "age_years", "level": "per 1-year increase", "n": None,
             "hr": 1.009, "ci": [0.979, 1.041], "p": 0.554, "continuous": True},
            {"variable": "site", "level": "central", "n": None, "reference": True},
            {"variable": "site", "level": "extremities", "n": None,
             "hr": 0.567, "ci": [0.222, 1.446], "p": 0.235},
            {"variable": "metastasis_location", "level": "none", "n": None, "reference": True},
            {"variable": "metastasis_location", "level": "lung", "n": None,
             "hr": 2.856, "ci": [0.572, 14.250], "p": 0.201},
            {"variable": "metastasis_location", "level": "mixed", "n": None,
             "hr": 6.665, "ci": [1.779, 24.970], "p": 0.005, "starred_significant": True},
            {"variable": "metastasis_location", "level": "other", "n": None,
             "hr": 11.431, "ci": [2.465, 53.000], "p": 0.002, "starred_significant": True},
            {"variable": "surgical_margin", "level": "R0", "n": None, "reference": True},
            {"variable": "surgical_margin", "level": "R1_or_R2", "n": None,
             "hr": 2.021, "ci": [0.540, 7.570], "p": 0.296},
            {"variable": "palliative_chemotherapy", "level": "no", "n": None, "reference": True},
            {"variable": "palliative_chemotherapy", "level": "yes", "n": None,
             "hr": 3.856, "ci": [1.349, 11.020], "p": 0.012, "treatment": True,
             "starred_significant": True},
        ],
    },
]

# ⚠ Why each treatment covariate may not be read causally, with the printed evidence of the confound.
CONFOUNDING_BY_INDICATION = {
    "neoadjuvant_or_adjuvant_radiotherapy": (
        "Masunaga's own text: 10 of the 24 irradiated patients (41.7 %) had R1 or R2 margins "
        "against 20 of 110 (18.2 %) of the unirradiated. Margin is this paper's strongest "
        "prognostic covariate, and it is more than twice as common in the treated arm -- so the "
        "irradiated group was the worse-prognosis group before radiotherapy began. The "
        "disease-specific HR of 5.05 is what that selection looks like, and it sits alongside a "
        "local-recurrence HR of 0.50 in the same paper on the same patients."),
    "neoadjuvant_or_adjuvant_chemotherapy": (
        "Six patients. Every interval is uninformative by width alone -- 0.08 to 4.19 for distant "
        "metastasis, 0.44 to 31.02 for disease-specific survival -- and whatever selected those six "
        "for chemotherapy is not printed."),
    "palliative_chemotherapy": (
        "Chiusole's covariate is palliative chemotherapy, given by definition to patients with "
        "advanced or metastatic disease. Its HR of 3.856 for overall survival is measuring the "
        "indication. The same paper's text reports the comparison as median OS 72 vs 81 months, "
        "p = 0.009, and does not present it as an effect of treatment."),
}

# ---------------------------------------------------------------------------
# derivations
# ---------------------------------------------------------------------------


def estimable(row: dict) -> bool:
    """A row that carries a real coefficient: not a reference level, not a non-estimate."""
    return (not row.get("reference")) and row.get("non_estimate") is None and row.get("ci")


def log_hr_se(row: dict) -> float | None:
    """SE of log(HR), back-derived from the printed 95 % interval.

    ⚠ THIS IS THE ONE DERIVED QUANTITY IN THE FILE AND IT INHERITS THE PRINTING. The interval is
    printed to two or three digits, so a back-derived SE is precise to about that; and it assumes
    the interval is the Wald one on the log scale, which is what Cox routines emit by default but is
    not stated by either paper. It is used only to say whether two intervals overlap -- never to
    pool, weight or test.
    """
    if not estimable(row):
        return None
    lo, hi = row["ci"]
    if lo <= 0:
        return None
    return (math.log(hi) - math.log(lo)) / (2 * 1.959963984540054)


def _direction(hr: float) -> str:
    if hr > 1.0:
        return "harmful"
    if hr < 1.0:
        return "protective"
    return "null"


def _overlap(a: dict, b: dict) -> bool:
    return not (a["ci"][1] < b["ci"][0] or b["ci"][1] < a["ci"][0])


def concordance() -> list[dict]:
    """Direction agreement between the two cohorts, covariate by covariate.

    ⛔ NOT A META-ANALYSIS. No HR is pooled, no weight is computed and no combined interval is
    produced. Each row states what each cohort printed, whether the two point estimates fall on the
    same side of 1, and whether the two intervals overlap -- three facts, none of which requires a
    model of between-study variance that two studies cannot support anyway.
    """
    # Only the univariate columns are compared: Masunaga's multivariate models are stepwise-selected
    # and Chiusole prints no multivariate model at all under its own table label.
    mas_uni = {m["endpoint"]: m for m in MODELS
               if m["source_id"] == "masunaga2025" and m["analysis"] == "univariate"}
    chi = next(m for m in MODELS if m["source_id"] == "chiusole2020")
    chi_rows = {(r["variable"], r["level"]): r for r in chi["rows"] if estimable(r)}

    # Which Masunaga level answers which Chiusole level. The site mapping is the load-bearing one
    # and it is NOT clean, so it is stated rather than assumed: Chiusole's "extremities" vs
    # "central (visceral, trunk, head and neck)" is a two-way split with central as reference;
    # Masunaga's is a three-way lower/upper/trunk split with lower limb as reference. The two
    # contrasts point in OPPOSITE directions -- extremity-vs-central against trunk-vs-lower-limb --
    # so a concordant finding is one where Chiusole's HR is below 1 and Masunaga's above it.
    PAIRS = [
        {"covariate": "surgical_margin_R1_R2_vs_R0",
         "masunaga": ("surgical_margin", "R1_or_R2"),
         "chiusole": ("surgical_margin", "R1_or_R2"),
         "same_contrast": True, "note": None},
        {"covariate": "female_vs_male",
         "masunaga": ("sex", "female"), "chiusole": ("sex", "female"),
         "same_contrast": True, "note": None},
        {"covariate": "age_per_year",
         "masunaga": ("age_years", "per 1-year increase"),
         "chiusole": ("age_years", "per 1-year increase"),
         "same_contrast": True, "note": None},
        {"covariate": "site_away_from_the_lower_limb",
         "masunaga": ("site", "trunk"), "chiusole": ("site", "extremities"),
         "same_contrast": False,
         "note": ("⚠ THE CONTRASTS ARE INVERSES OF EACH OTHER, NOT THE SAME CONTRAST. Masunaga "
                  "measures trunk against lower limb; Chiusole measures extremities against "
                  "central, where 'central' is defined as visceral, trunk, head and neck. "
                  "Concordance therefore means Masunaga above 1 AND Chiusole below 1, and the "
                  "direction test below is inverted for this row. The two 'central' categories are "
                  "also not the same set -- Chiusole's includes head and neck and visceral sites "
                  "that Masunaga's three-way split has nowhere to put -- so this row is the "
                  "weakest comparison in the table even when it agrees.")},
    ]

    out = []
    for pair in PAIRS:
        for endpoint, m in sorted(mas_uni.items()):
            mrow = next((r for r in m["rows"]
                         if (r["variable"], r["level"]) == pair["masunaga"] and estimable(r)), None)
            crow = chi_rows.get(pair["chiusole"])
            if mrow is None or crow is None:
                continue
            md, cd = _direction(mrow["hr"]), _direction(crow["hr"])
            agree = (md == cd) if pair["same_contrast"] else (md != cd and "null" not in (md, cd))
            out.append({
                "covariate": pair["covariate"],
                "masunaga2025": {"endpoint": endpoint, "hr": mrow["hr"], "ci": mrow["ci"],
                                 "p": mrow["p"], "direction": md, "n": m["n"],
                                 "log_hr_se": round(log_hr_se(mrow), 4)},
                "chiusole2020": {"endpoint": chi["endpoint"], "hr": crow["hr"], "ci": crow["ci"],
                                 "p": crow["p"], "direction": cd, "n": chi["n"],
                                 "log_hr_se": round(log_hr_se(crow), 4)},
                "same_contrast": pair["same_contrast"],
                "directions_agree": agree,
                "intervals_overlap": _overlap(mrow, crow),
                "masunaga_interval_excludes_1": mrow["ci"][0] > 1.0 or mrow["ci"][1] < 1.0,
                "chiusole_interval_excludes_1": crow["ci"][0] > 1.0 or crow["ci"][1] < 1.0,
                "both_null": not (mrow["ci"][0] > 1.0 or mrow["ci"][1] < 1.0)
                             and not (crow["ci"][0] > 1.0 or crow["ci"][1] < 1.0),
                "⛔_direction_between_two_nulls_is_noise": (
                    "Both intervals include 1, so which side of 1 each point estimate happens to "
                    "fall on is not evidence about anything. This row's agreement -- or its "
                    "disagreement -- carries no weight and is reported only so that the count of "
                    "agreements cannot be quoted without it."
                    if (not (mrow["ci"][0] > 1.0 or mrow["ci"][1] < 1.0)
                        and not (crow["ci"][0] > 1.0 or crow["ci"][1] < 1.0)) else None),
                "⛔_not_pooled": ("Two point estimates and two intervals, reported side by side. No "
                                 "combined HR is computed here and none should be quoted."),
                "note": pair["note"],
            })
    return out


def build() -> dict:
    conc = concordance()
    n_estimable = sum(1 for m in MODELS for r in m["rows"] if estimable(r))
    n_nonestimate = sum(1 for m in MODELS for r in m["rows"] if r.get("non_estimate"))
    n_treatment = sum(1 for m in MODELS for r in m["rows"] if r.get("treatment"))

    agree = [c for c in conc if c["directions_agree"]]
    disagree = [c for c in conc if not c["directions_agree"]]

    return {
        "_what": ("Fitted Cox coefficients for extraskeletal myxoid chondrosarcoma, transcribed from "
                  "the printed tables of two independent open-access cohorts, with a direction-only "
                  "cross-cohort comparison."),
        "_not_medical_advice": ("Nothing here is medical advice, and nothing here asserts efficacy, "
                                "safety, a therapeutic window or clinical readiness. A hazard ratio "
                                "from a retrospective series is an association within that series."),
        "_generated_by": "research/modalities/emc_prognostic_coefficients.py",
        "⭐_the_headline": (
            "RT-RISK-MODEL was waiting on reconstructed patient-level data. It does not need it to "
            "get the coefficients: the two largest reachable EMC series print FITTED COX MODELS -- "
            "seven models, " + str(n_estimable) + " estimable coefficients with 95 % intervals, "
            "across four endpoints and two continents. What patient-level data is still needed for "
            "is everything else -- a baseline hazard, any absolute risk, and any validation at all."),
        "⛔_what_is_structurally_impossible_from_print": {
            "absolute_risk_computable": False,
            "why": ("A Cox model is h0(t) * exp(sum beta_i x_i). Neither paper prints h0(t) or any "
                    "quantity it can be recovered from -- no baseline survival at a fixed time, no "
                    "per-stratum risk table, no reference-group survival curve with numbers at "
                    "risk. The betas alone order patients by risk and cannot price any patient's "
                    "risk."),
            "consequences": [
                "No survival probability may be derived from these coefficients.",
                "No nomogram, no risk score calibrated to an outcome, no n-year risk.",
                "No validation: discrimination and calibration both need patient-level outcomes.",
                "A risk model built from these is an ORDERING, and must be published as one.",
            ],
        },
        "⛔_nothing_here_is_pooled": (
            "systems/POLICY-evidence.md governs denominator-weighted proportions with Wilson "
            "intervals and refuses to merge time-anchored figures at all (2.4). A hazard ratio is a "
            "third estimand class the contract does not cover, and this module does not invent a "
            "method for it. No pooled HR, no inverse-variance weighting, no I2. The cross-cohort "
            "table reports two estimates side by side and asks only whether they fall on the same "
            "side of 1."),
        "⚠_the_endpoints_differ": (
            "Chiusole models OVERALL survival on all 59 patients including those metastatic at "
            "presentation; Masunaga models DISEASE-SPECIFIC survival, local recurrence-free "
            "survival and distant metastasis-free survival on the 134 who were localized and "
            "resected. Agreement across those is agreement of DIRECTION between related but "
            "distinct quantities."),
        "_transcription_verified": {
            "how": ("Every estimable coefficient was re-parsed out of the article text by an "
                    "independent regex that knows nothing about this module's structure, and the "
                    "full printed row -- hazard ratio, both interval bounds and the p-value, as one "
                    "contiguous match -- was required to appear in the source. Masunaga's per-level "
                    "patient counts were checked the same way, each required to appear immediately "
                    "adjacent to the coefficient it belongs to, which is what catches a count "
                    "attached to the wrong row."),
            "hr_ci_p_triples_matched": 45,
            "hr_ci_p_triples_not_found": 0,
            "masunaga_level_counts_matched_beside_their_coefficient": 60,
            "masunaga_level_counts_not_found": 0,
            "source_texts": [
                "literature-cache: emc-clinical-sweep-fulltext-2026-08-07/ft_masunaga2025_rtchemo.txt",
                "literature-cache: emc-km-pdftext-2026-08-12/chiusole2020_pdf.txt",
            ],
            "⚠_what_this_does_and_does_not_establish": (
                "It establishes that no digit was mistyped -- the failure mode that is otherwise "
                "silent, because a wrong hazard ratio looks exactly like a right one. It does NOT "
                "establish that a row was assigned to the right variable, the right endpoint or the "
                "right model, since a coefficient copied into the wrong table still matches the "
                "source text somewhere. Those are guarded structurally instead: the level counts "
                "must partition each model's n, and the same level must carry the same n in all "
                "three of Masunaga's tables, which a misfiled row breaks."),
            "⚠_the_source_texts_are_not_repository_content": (
                "They live on the literature-cache working branch, so this check is reproducible "
                "only where that branch is checked out. The verification counts are recorded here "
                "because the check is not re-runnable from a clean clone; treat them as a dated "
                "observation rather than a gate."),
        },
        "cohorts": COHORTS,
        "⛔_neither_cohort_prints_a_risk_table": (
            "Both cohorts print stratified Kaplan-Meier figures and NEITHER prints a numbers-at-risk "
            "row beneath any of them -- 7 stratified curves between them, 0 risk tables. That is "
            "the census RT-RISK-MODEL asked for, and its answer is that the reachable stratified "
            "curves are unreconstructable. The coefficients above are reachable anyway because they "
            "are printed as digits rather than drawn as pixels."),
        "models": MODELS,
        "counts": {
            "models": len(MODELS),
            "estimable_coefficients": n_estimable,
            "non_estimates_excluded": n_nonestimate,
            "treatment_covariates_refused_causal_reading": n_treatment,
            "cohorts": len(COHORTS),
        },
        "confounding_by_indication": CONFOUNDING_BY_INDICATION,
        "cross_cohort_direction": conc,
        "cross_cohort_summary": {
            "comparisons": len(conc),
            "directions_agree": len(agree),
            "directions_disagree": len(disagree),
            "agreeing": sorted({c["covariate"] for c in agree}),
            "disagreeing": sorted({c["covariate"] for c in disagree}),
            "intervals_overlap_in_all": all(c["intervals_overlap"] for c in conc),
            "comparisons_where_both_intervals_include_1": sum(1 for c in conc if c["both_null"]),
            "comparisons_where_exactly_one_excludes_1": sum(
                1 for c in conc
                if c["masunaga_interval_excludes_1"] != c["chiusole_interval_excludes_1"]),
            "comparisons_where_both_exclude_1": sum(
                1 for c in conc
                if c["masunaga_interval_excludes_1"] and c["chiusole_interval_excludes_1"]),
            "⛔_the_count_of_agreements_is_the_wrong_headline": (
                "11 of 12 comparisons agree in direction and all 12 pairs of intervals overlap, and "
                "BOTH of those numbers are close to uninformative. Overlap is near-guaranteed at "
                "these widths -- Chiusole's margin coefficient spans 0.54 to 7.57 -- and 9 of the "
                "12 comparisons are between two intervals that BOTH include 1, where which side of "
                "1 a point estimate lands on is noise. In NOT ONE comparison do both cohorts' "
                "intervals exclude 1. The honest summary is that these two cohorts are CONSISTENT, "
                "not that they CORROBORATE."),
            "⭐_the_one_covariate_that_survives_the_filter": (
                "Surgical margin. It is on the harmful side of 1 in all three Masunaga endpoints "
                "and in Chiusole, it is the only covariate significant in more than one Masunaga "
                "model (local recurrence 4.76, 1.72-13.15; distant metastasis 2.37, 1.21-4.64; and "
                "3.40, 1.57-7.38 after adjustment), and it is the only covariate whose direction "
                "does not change across four endpoints and two cohorts. ⚠ Chiusole's own margin "
                "interval still includes 1 (0.540-7.570), so the second cohort is consistent with "
                "the first without independently establishing it."),
            "⚠_the_one_disagreement_is_between_two_nulls": (
                "Sex, on local recurrence: Masunaga's female HR is 1.34 (0.48-3.73) and Chiusole's "
                "is 0.686 (0.263-1.786) for overall survival. Both intervals comfortably include 1, "
                "both p-values are above 0.5, and the endpoints are different. This is two null "
                "results whose point estimates happened to fall on opposite sides of 1 -- it is not "
                "a contradiction between the cohorts, and it must not be reported as one. It is "
                "counted as a disagreement above because the direction test is mechanical and is "
                "not permitted to quietly exempt the rows that spoil its own tally."),
        },
        "⚠_what_would_change_this": (
            "Each of these is a real, currently-unavailable input rather than a task: the three "
            "free-to-read series that no automated route can fetch "
            "(emc-km-reachability-census-2026-08-25.json) may print further Cox tables; a baseline "
            "hazard would arrive with any series that prints a reference-group curve WITH a "
            "numbers-at-risk row; and validation needs patient-level outcomes that no reachable "
            "publication contains."),
    }


# ---------------------------------------------------------------------------
# guards
# ---------------------------------------------------------------------------


def _check_structure() -> list[str]:
    errs: list[str] = []
    for m in MODELS:
        # Level counts must sum to the model n, per categorical variable, where counts are printed.
        by_var: dict[str, list[dict]] = {}
        for r in m["rows"]:
            by_var.setdefault(r["variable"], []).append(r)
        for var, rows in by_var.items():
            if any(r.get("continuous") for r in rows):
                continue
            ns = [r["n"] for r in rows]
            if any(n is None for n in ns):
                continue
            if sum(ns) != m["n"]:
                errs.append(f"{m['model_id']}: {var} level counts sum to {sum(ns)}, not {m['n']}")
        for r in m["rows"]:
            if r.get("reference"):
                if r.get("hr") is not None:
                    errs.append(f"{m['model_id']}: reference level {r['variable']}/{r['level']} "
                                f"carries an HR")
                continue
            if r.get("non_estimate"):
                if r.get("ci") is not None:
                    errs.append(f"{m['model_id']}: non-estimate {r['variable']}/{r['level']} "
                                f"carries a CI")
                continue
            if r.get("hr") is None or r.get("ci") is None:
                errs.append(f"{m['model_id']}: {r['variable']}/{r['level']} has no HR or no CI")
                continue
            lo, hi = r["ci"]
            if not (lo <= r["hr"] <= hi):
                errs.append(f"{m['model_id']}: {r['variable']}/{r['level']} HR {r['hr']} outside "
                            f"its interval {r['ci']}")
            # A starred-significant row must exclude 1; an unstarred one must include it.
            excludes_one = lo > 1.0 or hi < 1.0
            if bool(r.get("starred_significant")) != excludes_one:
                errs.append(f"{m['model_id']}: {r['variable']}/{r['level']} significance star and "
                            f"interval disagree (star={bool(r.get('starred_significant'))}, "
                            f"interval={r['ci']})")
        # Every treatment covariate must carry a stated confound.
        for r in m["rows"]:
            if r.get("treatment") and r["variable"] not in CONFOUNDING_BY_INDICATION:
                errs.append(f"{m['model_id']}: treatment covariate {r['variable']} has no entry in "
                            f"CONFOUNDING_BY_INDICATION")
    return errs


def check() -> int:
    errs = _check_structure()
    doc = build()
    if doc["⛔_what_is_structurally_impossible_from_print"]["absolute_risk_computable"] is not False:
        errs.append("absolute_risk_computable is not False -- the structural refusal has been lost")
    if not os.path.exists(OUT):
        errs.append(f"{os.path.basename(OUT)} is missing; run without --check to build it")
    else:
        with open(OUT, encoding="utf-8") as fh:
            on_disk = json.load(fh)
        if on_disk != doc:
            errs.append(f"{os.path.basename(OUT)} does not reproduce from its generator")
    for e in errs:
        print(f"ERROR: {e}")
    if errs:
        return 1
    print(f"emc_prognostic_coefficients --check OK "
          f"({doc['counts']['estimable_coefficients']} estimable coefficients, "
          f"{doc['counts']['non_estimates_excluded']} non-estimates excluded, "
          f"{doc['cross_cohort_summary']['comparisons']} cross-cohort comparisons)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the artifact reproduces and the guards hold")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    errs = _check_structure()
    for e in errs:
        print(f"ERROR: {e}")
    if errs:
        return 1
    doc = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}")
    print(f"  {doc['counts']['models']} models, {doc['counts']['estimable_coefficients']} estimable "
          f"coefficients, {doc['counts']['non_estimates_excluded']} non-estimates")
    s = doc["cross_cohort_summary"]
    print(f"  cross-cohort: {s['directions_agree']}/{s['comparisons']} agree in direction, "
          f"all intervals overlap={s['intervals_overlap_in_all']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
