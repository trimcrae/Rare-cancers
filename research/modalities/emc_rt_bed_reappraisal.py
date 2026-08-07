#!/usr/bin/env python3
"""EMC radioresistance reappraisal — the arithmetic behind `emc-rt-bed-reappraisal.json`.

WHY THIS EXISTS
---------------
`research/manuscripts/emc-unexplored-treatment-lanes.md` §3.7 registers a live contradiction in
EMC's own published record:

  * "RT does nothing"      — Japanese National Bone and Soft Tissue Tumor Registry, n = 171
                             (134 localized surgical): *"No association was found between
                             (neo)adjuvant radiotherapy and local recurrence rates"*
                             (Masunaga 2025, PMID 40885991 / PMC12398172).
  * "RT does a great deal" — MD Anderson, 41 consecutive localized EMC, median follow-up
                             94 months: 10-year local control 63 % surgery alone vs 100 %
                             combined modality, P = 0.004 (Bishop 2019, PMID 31436747).

and proposes that a **BED (biologically effective dose) regression** resolves it. This module
tests that proposal rather than assuming it. Four instruments, in the order that a reader should
apply them:

  A. CONSISTENCY. Before explaining a difference, test that there IS one. Each series' reported
     association between radiotherapy and LOCAL RECURRENCE is put on one log scale and Cochran's
     Q is computed. (`consistency`)
  B. BED. Compute BED = D·(1 + d/(alpha/beta)) for every EMC radiotherapy exposure with an
     extractable total dose AND dose per fraction, alpha/beta swept explicitly rather than hidden
     in a constant, and compare the BED DISTRIBUTIONS the two contradicting series delivered.
     (`bed_exposures`, `series_bed_comparison`)
  C. IDENTIFIABILITY. Ask whether alpha/beta is estimable at all from this record. (`alpha_beta_identifiability`)
  D. BIAS. Quantify confounding by indication in the direction the registry itself measured it,
     and compute the E-value of what survives. (`indication_bias`)

DISCIPLINE
----------
* Every clinical input carries its source id, a resolvable identifier, and `provenance`
  primary/secondary exactly as `systems/POLICY-evidence.md` §1.3 requires. A number read in a
  review is labelled secondary and carries `primary_ref` text; no identifier is invented for a
  primary that was not fetched.
* Where crude counts exist in NON-OVERLAPPING populations, the pooled proportion is the crude
  denominator-weighted proportion with a Wilson 95 % interval — POLICY-evidence §2.2, the
  repository's standard interval for simple proportions.
* Time-anchored survival (10-year local control) is NEVER merged into a pooled proportion —
  POLICY-evidence §2.4. The MD Anderson arm therefore contributes its published hazard ratio to
  instrument A and NOTHING to the pooled proportion.
* Instrument A is a THIRD combination method (inverse-variance on log effect measures) and says
  so in its own output under `method_note`. It exists to TEST agreement, not to produce a
  headline effect; its pooled value is emitted with `is_headline: false` because the inputs mix
  an unadjusted Cox HR, a multivariable Cox HR and a crude odds ratio.
* ⛔ NOTHING HERE ASSERTS EFFICACY. Every estimate is an observational association between a
  treatment that was ALLOCATED BY INDICATION and an outcome.

Pure stdlib. Usage:

    python3 research/modalities/emc_rt_bed_reappraisal.py            # write the artifact
    python3 research/modalities/emc_rt_bed_reappraisal.py --check    # fail if the artifact drifted
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "research/modalities/emc-rt-bed-reappraisal.json")

# The alpha/beta values the sensitivity sweep runs over. THE ASSUMPTION IS THE SWEEP, NOT A
# CONSTANT: §3.7 of the lanes memo carried "alpha/beta = 10 assumed", and a single assumed value
# is precisely what makes a BED argument unfalsifiable. 10 = classic early-responding tumour;
# 3 = late-responding / cartilage-like; 1.5-2 = the values quoted for chordoma and conventional
# chondrosarcoma; 4 = the value the one EMC brachytherapy report itself used.
ALPHA_BETA_SWEEP = [1.5, 2.0, 3.0, 4.0, 5.0, 10.0]

Z95 = 1.959963984540054


# ---------------------------------------------------------------------------
# sources — one home for every citation used below
# ---------------------------------------------------------------------------

SOURCES = {
    "masunaga2025": {
        "short": "Masunaga 2025",
        "title": "The role of radiotherapy and chemotherapy in extraskeletal myxoid chondrosarcoma",
        "journal": "J Orthop Surg Res",
        "year": 2025,
        "pmid": "40885991",
        "pmcid": "PMC12398172",
        "doi": "10.1186/s13018-025-06245-6",
        "design": "retrospective national registry cohort (Japanese National Bone and Soft Tissue Tumor Registry)",
        "n": 171,
        "study_period": [2002, 2022],
        "verification": "FT",
        "read_from": "literature-cache branch, literature/emc-clinical-sweep-2026-08-07/PMC12398172.txt",
    },
    "bishop2019": {
        "short": "Bishop 2019",
        "title": ("Extraskeletal Myxoid Chondrosarcomas: Combined Modality Therapy With Both "
                  "Radiation and Surgery Improves Local Control"),
        "journal": "Am J Clin Oncol",
        "year": 2019,
        "pmid": "31436747",
        "pmcid": "PMC7771031",
        "doi": "10.1097/COC.0000000000000590",
        "design": "single-institution retrospective, consecutive localized EMC (MD Anderson)",
        "n": 41,
        "study_period": [1990, 2016],
        "verification": "API",
        "read_from": ("Europe PMC core record (abstract) cached at literature-cache "
                      "literature/emc-physical-modalities-r2/epmc_bishop_emc_rt.txt; the full text "
                      "is isOpenAccess=N and was NOT retrieved"),
    },
    "remiszewski2025": {
        "short": "Remiszewski 2025",
        "title": ("From pathogenesis to the patient's bedside: a comprehensive review of "
                  "extraskeletal myxoid chondrosarcoma"),
        "journal": "J Cancer Res Clin Oncol",
        "year": 2025,
        "pmid": "41055792",
        "pmcid": "PMC12504171",
        "doi": "10.1007/s00432-025-06316-5",
        "design": "narrative review",
        "verification": "FT",
        "read_from": "literature-cache branch, literature/emc-clinical-sweep-2026-08-07/PMC12504171.txt",
    },
    "paioli2021": {
        "short": "Paioli 2021",
        "title": ("Extraskeletal Myxoid Chondrosarcoma with Molecularly Confirmed Diagnosis: "
                  "A Multicenter Retrospective Study Within the Italian Sarcoma Group"),
        "journal": "Ann Surg Oncol",
        "year": 2021,
        "pmid": "32572850",
        "pmcid": None,
        "doi": "10.1245/s10434-020-08737-7",
        "design": "three-centre retrospective, localized, NR4A3-rearrangement-confirmed only",
        "n": 67,
        "study_period": [1989, 2016],
        "verification": "API",
        "read_from": ("Europe PMC core record (abstract); the RT-vs-no-RT comparison used here was "
                      "read in Masunaga 2025 and is therefore SECONDARY. Reference identity fixed by "
                      "counting the numbered reference list of the Springer rendering of Masunaga "
                      "2025 (literature/emc-physical-modalities/emc_rt_chemo_role_josr2025.txt): "
                      "reference [9] = Paioli et al."),
    },
    "improta2020": {
        "short": "Improta 2020",
        "title": ("Locally recurrent extraskeletal myxoid chondrosarcoma of the shoulder: "
                  "a case of complete neoadjuvant radiotherapy response"),
        "journal": "Clin Sarcoma Res",
        "year": 2020,
        "pmid": "33308312",
        "pmcid": "PMC7731621",
        "doi": "10.1186/s13569-020-00150-8",
        "design": "case report",
        "n": 1,
        "verification": "FT",
        "read_from": "literature-cache branch, literature/emc-clinical-sweep-2026-08-07/PMC7731621.txt",
    },
    "ishikawa2022": {
        "short": "HDR-ISBT case report 2022",
        "title": ("High-dose-rate interstitial brachytherapy as a suitable option for metastatic "
                  "extraskeletal myxoid chondrosarcoma - a case report"),
        "journal": "J Contemp Brachytherapy",
        "year": 2022,
        "pmid": "35494187",
        "pmcid": "PMC9044308",
        "doi": "10.5114/jcb.2022.115161",
        "design": "case report",
        "n": 1,
        "verification": "FT",
        "read_from": "literature-cache branch, literature/emc-clinical-sweep-2026-08-07/PMC9044308.txt",
    },
    "sabr2025": {
        "short": "SABR oligoprogression case report 2025",
        "title": ("Excellent Response and Persistent Local Control of Metastatic Extraskeletal "
                  "Myxoid Chondrosarcoma Repeatedly Treated with Surgical Excision or Stereotactic "
                  "Radiotherapy Alone: A Case Report"),
        "journal": "Case Rep Oncol",
        "year": 2025,
        "pmid": "41323055",
        "pmcid": "PMC12659415",
        "doi": "10.1159/000548238",
        "design": "case report",
        "n": 1,
        "verification": "FT",
        "read_from": "literature-cache branch, literature/emc-clinical-sweep-2026-08-07/PMC12659415.txt",
    },
    "hayashi2017": {
        "short": "Hayashi 2017 (CIRT)",
        "title": ("Sequential histological findings and clinical response after carbon ion "
                  "radiotherapy for unresectable sarcoma"),
        "journal": "Clin Transl Radiat Oncol",
        "year": 2017,
        "pmid": "29657999",
        "pmcid": "PMC5893521",
        "doi": "10.1016/j.ctro.2017.01.002",
        "design": "case series, 7 patients (1 EMC)",
        "n": 7,
        "verification": "FT",
        "read_from": "literature-cache branch, literature/emc-clinical-sweep-2026-08-07/PMC5893521.txt",
    },
}


# ---------------------------------------------------------------------------
# A. consistency — is there a contradiction to explain?
# ---------------------------------------------------------------------------

def _se_from_ci(lo: float, hi: float, z: float = Z95) -> float:
    """SE of a log effect measure from its reported ratio-scale 95 % CI."""
    return (math.log(hi) - math.log(lo)) / (2.0 * z)


def _log_or_from_2x2(a: int, b: int, c: int, d: int):
    """log OR and its Woolf SE for exposed(a events / b non-events) vs unexposed(c / d)."""
    lor = math.log((a * d) / (b * c))
    se = math.sqrt(1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d)
    return lor, se


def _chi2_sf(x: float, k: int) -> float:
    """Upper tail of chi-square with k df, k in {1, 2, 3, 4}. Closed forms only, no scipy."""
    if x <= 0:
        return 1.0
    if k == 1:
        return math.erfc(math.sqrt(x / 2.0))
    if k == 2:
        return math.exp(-x / 2.0)
    if k == 3:
        return math.erfc(math.sqrt(x / 2.0)) + math.sqrt(2.0 * x / math.pi) * math.exp(-x / 2.0)
    if k == 4:
        return (1.0 + x / 2.0) * math.exp(-x / 2.0)
    raise ValueError("df outside the closed-form set")


def _norm_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def _norm_cdf(z: float) -> float:
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def _wilson(events: int, denom: int, z: float = Z95):
    p = events / denom
    den = 1.0 + z * z / denom
    centre = (p + z * z / (2.0 * denom)) / den
    half = z * math.sqrt(p * (1.0 - p) / denom + z * z / (4.0 * denom * denom)) / den
    return {"p": p, "lo": max(0.0, centre - half), "hi": min(1.0, centre + half)}


def consistency():
    """Instrument A — put every series' RT-vs-no-RT LOCAL-RECURRENCE association on one log scale."""
    studies = []

    # --- Masunaga 2025: univariable Cox HR for (neo)adjuvant RT on local recurrence -------------
    m_hr, m_lo, m_hi = 0.50, 0.11, 2.25
    studies.append({
        "source_id": "masunaga2025",
        "provenance": "primary",
        "arm_labels": ["(neo)adjuvant RT", "no (neo)adjuvant RT"],
        "measure": "hazard_ratio_univariable_cox",
        "point": m_hr, "ci95": [m_lo, m_hi],
        "log_effect": math.log(m_hr), "se_log": _se_from_ci(m_lo, m_hi),
        "crude_counts": {"rt_events": 2, "rt_denom": 24, "nort_events": 14, "nort_denom": 110},
        "quote": ("There was no association between (neo)adjuvant radiotherapy and local recurrence "
                  "rate (HR 0.50 [95% CI: 0.11-2.25]; p = 0.365)"),
        "note": ("Unadjusted. The SAME paper's multivariable model retained only surgical margin. "
                 "Its own crude numbers are 2/24 (8.3%) with RT vs 14/110 (12.7%) without — i.e. the "
                 "point estimate FAVOURS radiotherapy in both the crude table and the Cox model."),
    })

    # --- Bishop 2019: multivariable Cox HR, reported for SURGERY ALONE -> inverted to the RT scale
    b_hr, b_lo, b_hi = 12.7, 1.4, 115.3           # surgery alone vs combined modality
    studies.append({
        "source_id": "bishop2019",
        "provenance": "primary",
        "arm_labels": ["surgery + RT (combined modality)", "surgery alone"],
        "measure": "hazard_ratio_multivariable_cox_inverted",
        "reported_as": {"contrast": "surgery alone vs combined modality",
                        "point": b_hr, "ci95": [b_lo, b_hi], "p": 0.02},
        "point": 1.0 / b_hr, "ci95": [1.0 / b_hi, 1.0 / b_lo],
        "log_effect": -math.log(b_hr), "se_log": _se_from_ci(b_lo, b_hi),
        "crude_counts": None,
        "quote": ("the only significant factor associated with poorer LC was the use of surgery "
                  "alone (10 y LC, 63% vs. 100% for combined modality therapy, P=0.004), which "
                  "remained the only factor also significant on the multivariable analysis "
                  "(P=0.02; hazard ratio [HR], 12.7; 95% confidence interval [CI], 1.4-115.3)"),
        "note": ("The interval spans an 82-fold range. 33 of 41 patients received combined modality "
                 "and 8 did not, and the whole surgery-alone arm carried 5 or fewer local relapses "
                 "(the series reports 5 local relapses in total, at a median of 75 months). Under "
                 "POLICY-evidence §2.4 the 10-year local-control percentages are TIME-ANCHORED and "
                 "are not merged into any pooled proportion; only the hazard ratio enters here."),
    })

    # --- Paioli 2021, read in Masunaga 2025 (secondary): crude 2x2 -------------------------------
    p_lor, p_se = _log_or_from_2x2(1, 9, 7, 10)
    studies.append({
        "source_id": "paioli2021",
        "provenance": "secondary",
        "primary_ref": ("Paioli et al., Ann Surg Oncol 2021;28:1142-50 (reference [9] of Masunaga "
                        "2025). The RT-vs-no-RT comparison below was read in Masunaga 2025, not in "
                        "the Paioli full text, which was not retrieved."),
        "read_in": "masunaga2025",
        "arm_labels": ["surgery + (neo)adjuvant RT", "surgery alone"],
        "measure": "crude_odds_ratio",
        "point": math.exp(p_lor), "ci95": [math.exp(p_lor - Z95 * p_se), math.exp(p_lor + Z95 * p_se)],
        "log_effect": p_lor, "se_log": p_se,
        "crude_counts": {"rt_events": 1, "rt_denom": 10, "nort_events": 7, "nort_denom": 17},
        "quote": ("Another multicenter retrospective study involving only localized and molecularly "
                  "confirmed cases showed a trend toward better local control in the group that "
                  "underwent surgery and (neo)adjuvant radiotherapy than in the surgery-alone group "
                  "(local recurrence rate: 1/10 (10%) vs 7/17 (41%), p = 0.08)"),
        "note": ("27 patients, a subgroup of the 67-patient series; which 27 is not stated in the "
                 "secondary source. Odds ratio, not a hazard ratio — combined here on the log scale "
                 "with the two hazard ratios, which is an approximation and is why this instrument "
                 "is a TEST of agreement rather than a headline effect."),
    })

    ws = [1.0 / s["se_log"] ** 2 for s in studies]
    ys = [s["log_effect"] for s in studies]
    sw = sum(ws)
    pooled = sum(w * y for w, y in zip(ws, ys)) / sw
    se_pooled = 1.0 / math.sqrt(sw)
    q = sum(w * (y - pooled) ** 2 for w, y in zip(ws, ys))
    df = len(studies) - 1
    q_p = _chi2_sf(q, df)
    i2 = max(0.0, (q - df) / q) if q > 0 else 0.0

    # the pairwise test the memo's framing actually rests on
    m, b = studies[0], studies[1]
    diff = m["log_effect"] - b["log_effect"]
    se_diff = math.sqrt(m["se_log"] ** 2 + b["se_log"] ** 2)
    z_mb = diff / se_diff

    for s, w in zip(studies, ws):
        s["inverse_variance_weight"] = w
        s["weight_fraction"] = w / sw

    # POLICY-evidence §2.2 crude pooled proportions, only for the two series that report integer
    # counts in non-overlapping populations (a Japanese national registry and an Italian
    # three-centre series). Bishop 2019 is excluded by §2.4, not by judgement.
    rt_e = 2 + 1
    rt_n = 24 + 10
    no_e = 14 + 7
    no_n = 110 + 17
    pooled_props = {
        "method": ("crude denominator-weighted proportions + Wilson 95% CI, POLICY-evidence §2.2; "
                   "cohorts pooled only where all four §2.1 conditions hold"),
        "included_sources": ["masunaga2025", "paioli2021"],
        "excluded_sources": {
            "bishop2019": ("reports 10-year Kaplan-Meier local control only; POLICY-evidence §2.4 "
                           "forbids merging time-anchored survival into a pooled proportion"),
            "drilon2008": ("EXCLUDED ON A MEASURED DISCORDANCE, not on availability. Two published "
                           "secondary readings of the same primary point in OPPOSITE directions: "
                           "Masunaga 2025 reports 'no difference ... (41 vs. 35%, p = 0.79)' with "
                           "the RT arm at 41%, while the 2020 state-of-the-art review (PMID "
                           "32967265) reports the same series as showing 'a trend of a better local "
                           "recurrence rate in patients treated with surgery combined with "
                           "radiotherapy'. The primary (PMID 18951519, PMC2779719) is not in the "
                           "open-access subset and the Europe PMC fullTextXML endpoint returns 404, "
                           "so the direction of this series' RT effect is UNRESOLVED here."),
        },
        "rt_arm": dict(_wilson(rt_e, rt_n), events=rt_e, denom=rt_n),
        "no_rt_arm": dict(_wilson(no_e, no_n), events=no_e, denom=no_n),
        "per_cohort_rates": {
            "masunaga2025": {"rt": 2 / 24, "no_rt": 14 / 110},
            "paioli2021": {"rt": 1 / 10, "no_rt": 7 / 17},
        },
        "heterogeneity_note": ("POLICY-evidence §2.2 asks for the RANGE rather than an I-squared on "
                               "proportions: the RT-arm local-recurrence rate ranges 8.3-10.0% "
                               "across the two cohorts and the no-RT arm 12.7-41.2%. The no-RT "
                               "spread is wide and is the honest signal — it is compatible with the "
                               "Italian series being enriched for higher-risk surgery-alone cases."),
        "caveat": ("Crude, mixed follow-up, unadjusted, and NOT a causal effect: allocation to "
                   "radiotherapy was by indication in both cohorts."),
    }

    return {
        "question": ("Do the published EMC series actually DISAGREE about the association between "
                     "radiotherapy and local recurrence, or do they only disagree about whether "
                     "their own p-value crossed 0.05?"),
        "method_note": ("Inverse-variance combination on the log effect scale. ⚠ THIS IS A THIRD "
                        "COMBINATION METHOD, distinct from both methods named in "
                        "POLICY-evidence §2 (crude proportions + Wilson; DerSimonian-Laird in "
                        "research/meta/meta-analysis.mjs), because neither of those combines "
                        "hazard ratios. It is used here ONLY to test agreement. Its pooled value "
                        "is emitted with is_headline=false and must not be quoted as an effect "
                        "estimate: the inputs mix an unadjusted Cox HR, a multivariable Cox HR and "
                        "a crude odds ratio, and all three are confounded by indication."),
        "studies": studies,
        "fixed_effect_pooled": {
            "is_headline": False,
            "log_effect": pooled,
            "point": math.exp(pooled),
            "ci95": [math.exp(pooled - Z95 * se_pooled), math.exp(pooled + Z95 * se_pooled)],
            "se_log": se_pooled,
            "z": pooled / se_pooled,
            "p_two_sided": 2.0 * _norm_sf(abs(pooled / se_pooled)),
        },
        "heterogeneity": {"Q": q, "df": df, "p": q_p, "I2": i2,
                          "reading": ("Q tests the null that all three series estimate the SAME "
                                      "association. A large p means the record gives no evidence "
                                      "that they disagree.")},
        "pairwise_registry_vs_mdacc": {
            "log_difference": diff, "se": se_diff, "z": z_mb,
            "p_two_sided": 2.0 * _norm_sf(abs(z_mb)),
            "reading": ("This is the exact comparison the 'contradiction' framing rests on: "
                        "Masunaga 2025 against Bishop 2019."),
        },
        "pooled_proportions_policy_evidence_2_2": pooled_props,
    }


# ---------------------------------------------------------------------------
# A2. precision — what could each series have detected?
# ---------------------------------------------------------------------------

def schoenfeld_power(events: int, hr: float, frac_exposed: float, alpha: float = 0.05) -> float:
    """Two-sided log-rank power at the given HR, from the Schoenfeld event-count relation."""
    z_a = Z95 if abs(alpha - 0.05) < 1e-12 else -_inv_norm(alpha / 2.0)
    lam = abs(math.log(hr)) * math.sqrt(events * frac_exposed * (1.0 - frac_exposed))
    return _norm_cdf(lam - z_a)


def _inv_norm(p: float) -> float:
    """Acklam's inverse normal CDF — adequate to 1e-9, no scipy."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > ph:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def precision():
    events = 2 + 14
    frac = 24 / 134.0
    own = 0.50
    mdacc = 1.0 / 12.7
    return {
        "question": ("Could the registry have DETECTED the effect it estimated, and could it have "
                     "detected MD Anderson's?"),
        "registry": {
            "source_id": "masunaga2025",
            "local_recurrence_events": events,
            "n_localized_surgical": 134,
            "fraction_receiving_rt": frac,
            "power_at_its_own_point_estimate": {
                "hr": own, "power": schoenfeld_power(events, own, frac)},
            "power_at_the_md_anderson_point_estimate": {
                "hr": mdacc, "power": schoenfeld_power(events, mdacc, frac)},
            "reading": ("With 16 local-recurrence events the registry had roughly one chance in "
                        "five of reaching p < 0.05 at its OWN point estimate, and a high chance at "
                        "MD Anderson's. So 'no association was found' is a statement about power at "
                        "moderate effect sizes, not a measurement of no effect. Its 95% CI lower "
                        "bound of 0.11 does sit just above MD Anderson's point estimate of 0.079 — "
                        "the registry is mildly incompatible with an effect that LARGE while being "
                        "entirely compatible with a real, moderate benefit."),
            "method": ("Schoenfeld's two-sided log-rank relation, power = Phi(|ln HR| * "
                       "sqrt(d * p1 * p2) - 1.96). Assumes proportional hazards and treats the "
                       "reported univariable HR as the log-rank contrast."),
        },
    }


# ---------------------------------------------------------------------------
# B. BED
# ---------------------------------------------------------------------------

def bed(total_dose: float, dose_per_fraction: float, alpha_beta: float) -> float:
    """Linear-quadratic biologically effective dose. No time factor, no repopulation term."""
    return total_dose * (1.0 + dose_per_fraction / alpha_beta)


def _exposure(**kw):
    e = dict(kw)
    d, dpf = e["total_dose_gy"], e["dose_per_fraction_gy"]
    e["bed_gy"] = {str(ab): round(bed(d, dpf, ab), 2) for ab in ALPHA_BETA_SWEEP}
    e["eqd2_gy"] = {str(ab): round(bed(d, dpf, ab) / (1.0 + 2.0 / ab), 2) for ab in ALPHA_BETA_SWEEP}
    return e


def bed_exposures():
    """Every EMC radiotherapy exposure in reach with BOTH a total dose and a dose per fraction."""
    ex = []

    # --- the two contradicting series -----------------------------------------------------------
    ex.append(_exposure(
        exposure_id="masunaga-neoadjuvant-low", source_id="masunaga2025", provenance="primary",
        setting="neoadjuvant, localized primary", n_patients=4,
        total_dose_gy=40.0, dose_per_fraction_gy=2.0, fractions=20,
        dose_is="the LOW end of a stated range",
        quote=("neoadjuvant radiotherapy was administered at a total dose of 40-50 Gy in 2 Gy "
               "fractions in four patients"),
        local_outcome="arm-level only (2/24 local recurrences across all RT recipients)",
        outcome_granularity="arm"))
    ex.append(_exposure(
        exposure_id="masunaga-neoadjuvant-high", source_id="masunaga2025", provenance="primary",
        setting="neoadjuvant, localized primary", n_patients=4,
        total_dose_gy=50.0, dose_per_fraction_gy=2.0, fractions=25,
        dose_is="the HIGH end of a stated range",
        quote=("neoadjuvant radiotherapy was administered at a total dose of 40-50 Gy in 2 Gy "
               "fractions in four patients"),
        local_outcome="arm-level only", outcome_granularity="arm"))
    ex.append(_exposure(
        exposure_id="masunaga-adjuvant-low", source_id="masunaga2025", provenance="primary",
        setting="adjuvant, localized primary", n_patients=20,
        total_dose_gy=50.0, dose_per_fraction_gy=2.0, fractions=25,
        dose_is="the LOW end of a stated range",
        quote="adjuvant radiotherapy at a total dose of 50-66 Gy in 2 Gy fractions in 20 patients",
        local_outcome="arm-level only", outcome_granularity="arm"))
    ex.append(_exposure(
        exposure_id="masunaga-adjuvant-high", source_id="masunaga2025", provenance="primary",
        setting="adjuvant, localized primary", n_patients=20,
        total_dose_gy=66.0, dose_per_fraction_gy=2.0, fractions=33,
        dose_is="the HIGH end of a stated range",
        quote="adjuvant radiotherapy at a total dose of 50-66 Gy in 2 Gy fractions in 20 patients",
        local_outcome="arm-level only", outcome_granularity="arm"))

    # Bishop's doses are read in the Remiszewski review, NOT in the Bishop full text (isOpenAccess=N),
    # and the review states the total dose without a fraction size. Both plausible conventional
    # fraction sizes are therefore carried explicitly instead of one being chosen.
    bishop_quote = ("a single institution series (Bishop et al.) studied 41 consecutive patients "
                    "with localised EMC, of whom 56% (n = 23) received preoperative radiotherapy "
                    "with a median dose of 50 Gy (range, 50-50.4 Gy), 24% (n = 10) received "
                    "postoperative radiotherapy with a median dose of 60 Gy (range, 60-65 Gy), and "
                    "20% (n = 8) underwent surgery alone")
    for dpf in (1.8, 2.0):
        ex.append(_exposure(
            exposure_id=f"bishop-preop-median-d{dpf}", source_id="remiszewski2025",
            provenance="secondary", primary_ref="Bishop et al. 2019 (n = 23 preoperative)",
            setting="preoperative, localized primary", n_patients=23,
            total_dose_gy=50.0, dose_per_fraction_gy=dpf, fractions=round(50.0 / dpf, 1),
            dose_is="stated median (range 50-50.4 Gy); FRACTION SIZE NOT STATED BY THE SOURCE",
            quote=bishop_quote,
            local_outcome="10-year local control 100% in the combined-modality arm (time-anchored)",
            outcome_granularity="arm"))
        ex.append(_exposure(
            exposure_id=f"bishop-postop-median-d{dpf}", source_id="remiszewski2025",
            provenance="secondary", primary_ref="Bishop et al. 2019 (n = 10 postoperative)",
            setting="postoperative, localized primary", n_patients=10,
            total_dose_gy=60.0, dose_per_fraction_gy=dpf, fractions=round(60.0 / dpf, 1),
            dose_is="stated median (range 60-65 Gy); FRACTION SIZE NOT STATED BY THE SOURCE",
            quote=bishop_quote,
            local_outcome="10-year local control 100% in the combined-modality arm (time-anchored)",
            outcome_granularity="arm"))
        ex.append(_exposure(
            exposure_id=f"bishop-postop-max-d{dpf}", source_id="remiszewski2025",
            provenance="secondary", primary_ref="Bishop et al. 2019 (top of the postoperative range)",
            setting="postoperative, localized primary", n_patients=None,
            total_dose_gy=65.0, dose_per_fraction_gy=dpf, fractions=round(65.0 / dpf, 1),
            dose_is="TOP of the stated range; FRACTION SIZE NOT STATED BY THE SOURCE",
            quote=bishop_quote,
            local_outcome="10-year local control 100% in the combined-modality arm (time-anchored)",
            outcome_granularity="arm"))

    # --- case-level exposures, where dose AND a per-lesion outcome both exist --------------------
    ex.append(_exposure(
        exposure_id="improta2020-preop-50-25", source_id="improta2020", provenance="primary",
        setting="preoperative, locally recurrent primary", n_patients=1,
        total_dose_gy=50.0, dose_per_fraction_gy=2.0, fractions=25,
        dose_is="stated exactly",
        quote=("the decision was made for preoperative RT, with a total dose of 50 Gy (fractionated "
               "in 200 cGy/die)"),
        local_outcome="complete pathological response at resection", local_control=True,
        outcome_granularity="lesion"))
    ex.append(_exposure(
        exposure_id="sabr2025-neoadjuvant-60-25", source_id="sabr2025", provenance="primary",
        setting="neoadjuvant, localized primary", n_patients=1,
        total_dose_gy=60.0, dose_per_fraction_gy=2.4, fractions=25,
        dose_is="stated exactly",
        quote="She underwent neoadjuvant radiotherapy (RT), 60 Gy in 25 fractions from June to July 2019",
        local_outcome="subsequent LOCAL relapse at the primary site", local_control=False,
        outcome_granularity="lesion",
        confound=("the relapse followed surgery as well as radiotherapy, so it is not attributable "
                  "to the radiotherapy alone")))
    ex.append(_exposure(
        exposure_id="sabr2025-sabr-40-5", source_id="sabr2025", provenance="primary",
        setting="metastasis-directed SABR (oligoprogression)", n_patients=1,
        total_dose_gy=40.0, dose_per_fraction_gy=8.0, fractions=5,
        dose_is="stated exactly",
        quote="a total dose of 40 Gy, delivered in 5 consecutive fractions of 8 Gy",
        local_outcome="complete response, no relapse in any irradiated site", local_control=True,
        outcome_granularity="lesion"))
    ex.append(_exposure(
        exposure_id="sabr2025-sabr-35-5", source_id="sabr2025", provenance="primary",
        setting="metastasis-directed SABR (dose reduced for bowel constraint)", n_patients=1,
        total_dose_gy=35.0, dose_per_fraction_gy=7.0, fractions=5,
        dose_is="stated exactly",
        quote=("the prescription dose for the third SABR course was lowered to 35 Gy instead of "
               "40 Gy"),
        local_outcome="complete or major response, no relapse in irradiated sites", local_control=True,
        outcome_granularity="lesion"))
    ex.append(_exposure(
        exposure_id="isbt2022-30-2", source_id="ishikawa2022", provenance="primary",
        setting="metastasis-directed HDR interstitial brachytherapy (3 separate sites)", n_patients=1,
        total_dose_gy=30.0, dose_per_fraction_gy=15.0, fractions=2,
        dose_is="stated exactly",
        quote="Dose of HDR-ISBT was 30 Gy/2 fractions in 1 day (only one application)",
        local_outcome="long-term local control at all three treated sites", local_control=True,
        outcome_granularity="lesion",
        author_bed_note=("the report computes its own BED as 142 Gy at alpha/beta = 4 and contrasts "
                         "it with 24 Gy for 8 Gy in 1 fraction; that is the only alpha/beta an EMC "
                         "radiotherapy paper has stated, and it is an assumption, not a measurement")))
    return ex


def series_bed_comparison(exposures):
    """The decisive comparison: do the two contradicting series' BED distributions overlap?"""
    reg = [e for e in exposures if e["source_id"] == "masunaga2025"]
    mda = [e for e in exposures if e.get("primary_ref", "").startswith("Bishop")]
    out = {}
    for ab in ALPHA_BETA_SWEEP:
        k = str(ab)
        r = sorted(e["bed_gy"][k] for e in reg)
        m = sorted(e["bed_gy"][k] for e in mda)
        contains = (r[0] <= m[0]) and (r[-1] >= m[-1])
        out[k] = {
            "registry_bed_range": [r[0], r[-1]],
            "md_anderson_bed_range": [m[0], m[-1]],
            "registry_range_contains_md_anderson_range": contains,
            "registry_max_minus_md_anderson_max": round(r[-1] - m[-1], 2),
        }
    return {
        "question": ("Did the series that found NO benefit deliver a LOWER biologically effective "
                     "dose than the series that found a large one?"),
        "answer": ("No, at every alpha/beta in the sweep. The registry's delivered BED range "
                   "CONTAINS MD Anderson's, and the registry's maximum is the higher of the two. "
                   "A dose explanation therefore requires the null series to have out-dosed the "
                   "positive one, which is not a coherent dose-response account."),
        "by_alpha_beta": out,
        "caveats": [
            ("MD Anderson's fraction size is NOT stated by the source that reports its doses "
             "(a review), so both 1.8 and 2.0 Gy are carried; the conclusion is identical either way."),
            ("Both series report DOSE RANGES at the arm level, not per-patient doses, so these are "
             "range comparisons and not a regression."),
            ("The registry's neoadjuvant 40 Gy floor is below MD Anderson's floor; the comparison "
             "made here is of the ranges as wholes, and the registry's TOP exceeds MD Anderson's "
             "top at every alpha/beta."),
        ],
    }


# ---------------------------------------------------------------------------
# C. is alpha/beta identifiable?
# ---------------------------------------------------------------------------

def alpha_beta_identifiability(exposures):
    """The memo proposes fitting local control against BED 'with alpha/beta free'. Can that run?"""
    usable = [e for e in exposures if e.get("outcome_granularity") == "lesion"]
    curative = [e for e in usable if "metastasis-directed" not in e["setting"]]
    metdir = [e for e in usable if "metastasis-directed" in e["setting"]]
    d_cur = sorted({e["dose_per_fraction_gy"] for e in curative})
    d_met = sorted({e["dose_per_fraction_gy"] for e in metdir})
    separated = max(d_cur) < min(d_met)

    # the same lesion-level exposures, ranked by BED, at the two extremes of the sweep
    def order(ab):
        return [e["exposure_id"] for e in sorted(usable, key=lambda x: -x["bed_gy"][str(ab)])]

    return {
        "question": "Is alpha/beta for EMC estimable from the published radiotherapy record?",
        "verdict": "NO — not estimable. It is aliased with treatment setting.",
        "why": ("BED = D(1 + d/(alpha/beta)) admits alpha/beta only through the DOSE PER FRACTION d. "
                "Identifying it therefore requires exposures that differ in d while being comparable "
                "in everything else. In the EMC record, d takes conventional values (1.8-2.4 Gy) in "
                "every curative-intent primary-site exposure and hypofractionated values (7-15 Gy) in "
                "every metastasis-directed exposure, with NO OVERLAP. Fraction size is therefore "
                "perfectly separated from setting, target volume and tumour burden. Any alpha/beta "
                "fitted to these data would be estimating 'ablative treatment of small "
                "oligometastatic nodules controls them better than adjuvant treatment of a bulky "
                "operative bed', which is true of every histology and says nothing about EMC's "
                "intrinsic fractionation sensitivity."),
        "lesion_level_exposures": len(usable),
        "dose_per_fraction_curative_intent": d_cur,
        "dose_per_fraction_metastasis_directed": d_met,
        "perfectly_separated": separated,
        "exposures_with_a_within_setting_fractionation_contrast": 0,
        "bed_ranking_at_alpha_beta_10": order(10.0),
        "bed_ranking_at_alpha_beta_1_5": order(1.5),
        "ranking_is_alpha_beta_dependent": order(10.0) != order(1.5),
        "the_one_suggestive_contrast": {
            "description": ("Within ONE patient (sabr2025), neoadjuvant 60 Gy in 25 fractions to "
                            "the primary was followed by local relapse, while 40 Gy in 5 fractions "
                            "and 35 Gy in 5 fractions to metastatic nodules produced durable local "
                            "control. At alpha/beta = 10 those exposures have almost identical BED "
                            "(74.4 vs 72.0 vs 84.0 Gy10); at alpha/beta = 3 they separate sharply "
                            "(108.0 vs 146.7 vs 116.7 Gy3). A LOW alpha/beta is the only value at "
                            "which BED orders these outcomes correctly."),
            "bed10": {"neoadj_60_25": bed(60, 2.4, 10), "sabr_40_5": bed(40, 8, 10),
                      "sabr_35_5": bed(35, 7, 10)},
            "bed3": {"neoadj_60_25": bed(60, 2.4, 3), "sabr_40_5": bed(40, 8, 3),
                     "sabr_35_5": bed(35, 7, 3)},
            "why_it_is_not_evidence": ("n = 1, and the contrast is confounded by everything that "
                                       "differs between a bulky operated primary and a sub-centimetre "
                                       "metastatic nodule. It is a hypothesis generator and is "
                                       "reported as one."),
        },
        "consequence_for_the_memo": ("§3.7's proposed 'BED meta-regression ... with alpha/beta free' "
                                     "cannot be executed on the existing record. That is a "
                                     "definitional closure of the method, not a gap that more "
                                     "literature retrieval would fill: no EMC exposure exists in "
                                     "which fractionation varied within one treatment setting."),
    }


# ---------------------------------------------------------------------------
# D. confounding by indication
# ---------------------------------------------------------------------------

def indication_bias():
    """The registry measured its own indication bias. Correct for it and see which way it moves."""
    p_rt = 10 / 24.0            # R1/R2 margins among RT recipients
    p_no = 20 / 110.0           # R1/R2 margins among non-recipients
    hr_margin = 4.76            # R1/R2 vs R0, local recurrence, same paper, multivariable
    exp_rt = p_rt * hr_margin + (1 - p_rt)
    exp_no = p_no * hr_margin + (1 - p_no)
    bias_factor = exp_rt / exp_no
    observed = 0.50
    corrected = observed / bias_factor

    def e_value(rr):
        r = 1.0 / rr if rr < 1 else rr
        return r + math.sqrt(r * (r - 1.0))

    return {
        "question": ("Which way does the confounding run, and does correcting for the part the "
                     "registry MEASURED move it toward or away from the MD Anderson result?"),
        "source_id": "masunaga2025",
        "measured_imbalance": {
            "r1_r2_margin_fraction_rt_arm": p_rt,
            "r1_r2_margin_fraction_no_rt_arm": p_no,
            "quote": ("Of the 24 patients who received (neo)adjuvant radiotherapy, 10 (41.7%) had "
                      "R1 or R2 surgical margins, whereas only 20 (18.2%) of the 110 patients who "
                      "did not receive (neo)adjuvant radiotherapy had R1 or R2 surgical margins"),
            "margin_hazard_ratio_for_local_recurrence": hr_margin,
        },
        "analytic_correction": {
            "method": ("Multiplicative-hazards bias factor. Under a null radiotherapy effect, the "
                       "margin imbalance alone produces an expected hazard ratio of "
                       "(p_rt*HR_margin + 1 - p_rt) / (p_no*HR_margin + 1 - p_no). Dividing the "
                       "observed HR by that factor removes the part of the confounding the paper "
                       "itself measured."),
            "expected_relative_hazard_rt_arm": exp_rt,
            "expected_relative_hazard_no_rt_arm": exp_no,
            "bias_factor_under_a_null_rt_effect": bias_factor,
            "observed_hr": observed,
            "margin_corrected_hr": corrected,
            "direction": ("TOWARD a larger radiotherapy benefit. The measured confounding hides "
                          "benefit; it does not manufacture it."),
            "assumptions": [
                "proportional and multiplicative hazards",
                "the margin hazard ratio is transportable across the two arms",
                "no other confounder is corrected — this removes ONE measured imbalance only",
                ("the same direction of bias applies in the opposite series: MD Anderson omitted "
                 "radiotherapy in 8 patients, and omission is itself an indication (small, "
                 "superficial, cleanly excised tumours), which biases THAT series toward finding "
                 "no benefit too. Both series are biased the same way, which is why they cannot "
                 "be read as a contradiction between an optimistic and a pessimistic design."),
            ],
        },
        "e_values": {
            "note": ("VanderWeele-Ding E-value on the risk-ratio scale. The local-recurrence risk in "
                     "this cohort is 16/134 = 11.9%, so the hazard ratio is treated as approximating "
                     "a risk ratio; that approximation degrades above roughly 15% and is stated here "
                     "rather than buried."),
            "observed_hr_0_50": e_value(0.50),
            "margin_corrected_hr": e_value(corrected),
            "md_anderson_hr_0_0787": e_value(1.0 / 12.7),
            "md_anderson_ci_bound_hr_0_714": e_value(1.0 / 1.4),
            "reading": ("An unmeasured confounder would have to be associated with BOTH radiotherapy "
                        "receipt and local recurrence at roughly this risk-ratio strength, above and "
                        "beyond the measured margin imbalance, to explain the estimate away."),
        },
    }


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------

def build():
    ex = bed_exposures()
    cons = consistency()
    return {
        "_schema": "emc-rt-bed-reappraisal/1",
        "_generated_by": "research/modalities/emc_rt_bed_reappraisal.py",
        "_one_home_for": ("every number in research/manuscripts/emc-radioresistance-reappraisal.md; "
                          "the prose points here and types no arithmetic of its own"),
        "_disclaimer": ("⛔ NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL "
                        "READINESS. Every estimate is an observational association from cohorts in "
                        "which radiotherapy was allocated by indication, and no randomised trial of "
                        "radiotherapy in EMC exists."),
        "lane": "emc-unexplored-treatment-lanes.md §3.7 — the radioresistance reappraisal",
        "date": "2026-08-07",
        "sources": SOURCES,
        "alpha_beta_sweep": ALPHA_BETA_SWEEP,
        "consistency": cons,
        "precision": precision(),
        "bed_exposures": ex,
        "series_bed_comparison": series_bed_comparison(ex),
        "alpha_beta_identifiability": alpha_beta_identifiability(ex),
        "indication_bias": indication_bias(),
        "verdict": {
            "resolved": True,
            "resolved_by": "not BED",
            "statement": (
                "The contradiction does not survive being stated as a contradiction. All three EMC "
                "series that report an association between radiotherapy and local recurrence point "
                "the SAME way, and Cochran's Q over them gives no evidence that they disagree. The "
                "difference the memo describes is a difference between a significant and a "
                "non-significant result, not between two estimates. BED is refuted as the "
                "explanation on its own terms: the series that found nothing delivered the WIDER "
                "and, at the top, HIGHER biologically effective dose, at every alpha/beta tested. "
                "And alpha/beta for EMC is not estimable from the published record at all, because "
                "fraction size is perfectly confounded with treatment setting."),
            "what_survives_as_a_real_open_question": (
                "The MAGNITUDE. The registry's data are mildly incompatible with an effect as large "
                "as MD Anderson's and entirely compatible with a moderate one; after removing the "
                "one confounder the registry measured, its own estimate moves toward MD Anderson's. "
                "Nothing here establishes a causal effect, and confounding by indication runs in the "
                "same direction in every available series, so every estimate is a lower bound of "
                "unknown tightness."),
            "what_would_change_it": (
                "A per-patient dose-and-outcome table from any EMC series — none of the four "
                "cohorts publishes one — or a single EMC cohort in which fraction size varied "
                "within one treatment setting, which would make alpha/beta identifiable for the "
                "first time."),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="fail if the committed artifact differs from a fresh build")
    a = ap.parse_args()
    doc = build()
    text = json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    if a.check:
        if not os.path.exists(OUT):
            print(f"MISSING {OUT}", file=sys.stderr)
            return 1
        if open(OUT, encoding="utf-8").read() != text:
            print(f"DRIFT: {OUT} differs from a fresh build of {__file__}", file=sys.stderr)
            return 1
        print("emc_rt_bed_reappraisal: artifact matches")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    v = doc["verdict"]
    h = doc["consistency"]["heterogeneity"]
    print(f"wrote {OUT}")
    print(f"  Cochran Q = {h['Q']:.3f}, df = {h['df']}, p = {h['p']:.3f}, I2 = {h['I2']:.3f}")
    print(f"  resolved={v['resolved']} by {v['resolved_by']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
