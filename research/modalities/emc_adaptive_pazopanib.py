#!/usr/bin/env python3
"""Adaptive scheduling of pazopanib in EMC — the arithmetic behind `emc-adaptive-pazopanib.json`.

WHY THIS EXISTS
---------------
`research/manuscripts/emc-unexplored-treatment-lanes.md` §3.8 argues that EMC is close to an ideal
adaptive-therapy indication on five independent grounds, that the work is $0, and that its
falsifier is itself a publishable question. It also states the deliverable correctly:

    "The deliverable is not 'adaptive therapy works in EMC.' It is: here is the parameter region in
     which it would, and here is exactly what you would have to measure to know which region EMC is
     in."

This module does three things and refuses to do a fourth:

  1. CHECKS EACH OF THE FIVE GROUNDS against what this repository can actually cite, and records
     where a ground is overstated. (`five_grounds`)
  2. RUNS the two-population competitive Lotka-Volterra model over the parameter region, comparing
     continuous maximum-tolerated dosing with a Gatenby-style adaptive schedule, and reports where
     the adaptive arm wins and by how much. (`competition_model`)
  3. RUNS a SECOND model in which resistance is REVERSIBLE PHENOTYPE rather than heritable
     genotype, because that is the mechanism EMC's mutational quietness makes more likely, and the
     two models make opposite predictions about why intermittent dosing would help.
     (`plasticity_model`)
  4. ⛔ REFUSES to emit a predicted progression-free survival for EMC. Every rate parameter in the
     model is UNMEASURED in EMC in vivo (`identifiability`), so a number with a time unit on it
     would be a simulation output wearing clinical clothes.

⛔ NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS. Adaptive
scheduling has never been tested in EMC or in any sarcoma. Deliberately reducing the dose of an
active drug outside a trial can shorten disease control; this analysis is about what would have to
be true, not about what to do.

Pure stdlib. Usage:

    python3 research/modalities/emc_adaptive_pazopanib.py            # write the artifact
    python3 research/modalities/emc_adaptive_pazopanib.py --check    # fail if the artifact drifted
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "research/modalities/emc-adaptive-pazopanib.json")


# ---------------------------------------------------------------------------
# sources
# ---------------------------------------------------------------------------

SOURCES = {
    "stacchiotti2019_pazopanib": {
        "short": "Stacchiotti 2019 (pazopanib phase 2)",
        "title": ("Pazopanib for treatment of advanced extraskeletal myxoid chondrosarcoma: "
                  "a multicentre, single-arm, phase 2 trial"),
        "journal": "Lancet Oncol",
        "year": 2019,
        "pmid": "31331701",
        "doi": "10.1016/S1470-2045(19)30319-5",
        "nct": "NCT02066285",
        "design": "single-arm, open-label phase 2; 11 sites, Spanish/Italian/French sarcoma groups",
        "verification": "API",
        "read_from": ("Europe PMC core record (full abstract) cached at literature-cache "
                      "literature/emc-clinical-sweep-fulltext-2026-08-07/epmc_pazopanib_emc_lancet.txt"),
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
        "read_from": "literature-cache, literature/emc-clinical-sweep-2026-08-07/PMC12504171.txt",
    },
    "zou2023_wgs": {
        "short": "Zou 2023 (matched-trio WGS)",
        "title": ("Whole genome sequencing for metastatic mutational burden in extraskeletal "
                  "myxoid chondrosarcoma"),
        "journal": "Front Mol Med",
        "year": 2023,
        "pmid": "39086683",
        "pmcid": "PMC11285543",
        "doi": "10.3389/fmmed.2023.1152550",
        "design": "n = 1 matched trio (primary, lung metastasis, pelvic metastasis), WGS",
        "verification": "FT",
        "read_from": "literature-cache, literature/emc-clinical-sweep-2026-08-07/PMC11285543.txt",
    },
    "bangerter2023_models": {
        "short": "Bangerter 2023 (USZ ex vivo models)",
        "title": ("Establishment, characterization and functional testing of two novel ex vivo "
                  "extraskeletal myxoid chondrosarcoma models"),
        "journal": "Hum Cell / J Exp Clin Cancer Res (per record)",
        "year": 2023,
        "pmid": "36316541",
        "pmcid": "PMC9813045",
        "design": "two patient-derived ex vivo models (USZ20-EMC1 EWSR1, USZ22-EMC2 TAF15)",
        "verification": "FT",
        "read_from": "literature-cache, literature/emc-clinical-sweep-2026-08-07/PMC9813045.txt",
    },
    "stacchiotti2013_anthracycline": {
        "short": "Stacchiotti 2013 (anthracycline)",
        "title": ("Anthracycline-based chemotherapy in extraskeletal myxoid chondrosarcoma: "
                  "a retrospective study"),
        "journal": "Clin Sarcoma Res",
        "year": 2013,
        "pmid": "24345066",
        "pmcid": "PMC3879193",
        "design": "retrospective, 11 patients, NR4A3-rearrangement confirmed",
        "verification": "FT",
        "read_from": "literature-cache, literature/emc-clinical-sweep-2026-08-07/PMC3879193.txt",
    },
    "stacchiotti2014_sunitinib": {
        "short": "Stacchiotti 2014 (sunitinib)",
        "title": "Activity of sunitinib in extraskeletal myxoid chondrosarcoma",
        "journal": "Eur J Cancer",
        "year": 2014,
        "pmid": "24703573",
        "design": "retrospective series, n = 10",
        "verification": "secondary — figures quoted in emc-unexplored-treatment-lanes.md §3.1/§3.2",
    },
    "zhang2017_adaptive_prostate": {
        "short": "Zhang 2017 (adaptive abiraterone)",
        "title": ("Integrating evolutionary dynamics into treatment of metastatic "
                  "castrate-resistant prostate cancer"),
        "journal": "Nat Commun",
        "year": 2017,
        "pmid": "29180633",
        "design": "pilot, 11 patients; updated eLife 2022, PMID 35762577",
        "verification": "secondary — the clinical anchor cited by emc-unexplored-treatment-lanes.md §3.8",
    },
}


# ---------------------------------------------------------------------------
# 1 · the five grounds, checked
# ---------------------------------------------------------------------------

def five_grounds():
    return [
        {
            "ground": "i",
            "memo_claim": ("There is one active systemic class, so preserving it beats "
                           "deepening it."),
            "verdict": "PARTIALLY OVERSTATED",
            "evidence_for": [
                ("Pazopanib is the only agent with a prospective EMC-specific phase 2 result: "
                 "NCT02066285, 4/22 evaluable RECIST responses (18 %, 95 % CI 1-36) "
                 "[stacchiotti2019_pazopanib, API]."),
            ],
            "evidence_against": [
                ("Anthracycline-based chemotherapy in 10 evaluable molecularly-confirmed EMC gave "
                 "4 partial responses (40 %) and median PFS 8 months "
                 "[stacchiotti2013_anthracycline, FT] — a second class with measured activity, so "
                 "'one active class' is not literally true."),
                ("Sunitinib in n = 10 gave 6 PR / 2 SD / 2 PD [stacchiotti2014_sunitinib, "
                 "secondary] — same class as pazopanib, but it means the anti-angiogenic option is "
                 "not a single agent."),
            ],
            "what_survives": ("The weaker and still-useful form: after anthracycline failure the "
                              "anti-angiogenic class is the only one with prospective EMC evidence, "
                              "and anthracycline's own median PFS of 8 months is short. Losing the "
                              "anti-angiogenic class is close to losing the last measured option."),
        },
        {
            "ground": "ii",
            "memo_claim": ("Pazopanib's profile — ORR ~18 % with median PFS ~19 months — is control "
                           "without shrinkage, the signature of competitive suppression."),
            "verdict": "SUPPORTED, and the trial's entry criterion strengthens it",
            "evidence_for": [
                ("ORR 4/22 = 18 % (95 % CI 1-36) [stacchiotti2019_pazopanib, API]. So 18 of 22 "
                 "evaluable patients never met the RECIST response threshold."),
                ("Median PFS 19 months [remiszewski2025, secondary — the primary abstract does not "
                 "state a median PFS, and the trial's own median follow-up was 27 months "
                 "(IQR 18-30)]."),
                ("⭐ ELIGIBILITY REQUIRED DOCUMENTED RECIST PROGRESSION IN THE PREVIOUS 6 MONTHS, "
                 "verbatim from the primary abstract. So every enrolled patient had measured growth "
                 "within six months of starting, and the on-treatment median PFS was 19 months. The "
                 "drug's measured effect is a change of TEMPO, not cytoreduction — which is exactly "
                 "the regime in which dosing to maximum tolerated buys the least."),
            ],
            "evidence_against": [
                ("The same entry criterion means the trial cohort is by construction the PROGRESSING "
                 "subset of EMC, not the indolent one. Any adaptive-therapy argument built on 'EMC "
                 "is indolent' and calibrated on this trial is mixing two different populations, "
                 "and the memo does not make that distinction."),
            ],
            "what_survives": ("Ground ii is the strongest of the five and is now quantitative: "
                              "82 % of patients had no shrinkage, in a cohort selected for recent "
                              "growth, and still had a long median PFS."),
        },
        {
            "ground": "iii",
            "memo_claim": "The natural history is long enough for oscillation to run.",
            "verdict": "SUPPORTED (secondary)",
            "evidence_for": [
                ("'Median OS for patients with metastatic EMC is in the order of 5-7 years in modern "
                 "series, and the disease often follows an indolent course even without immediate "
                 "systemic treatment' [remiszewski2025, FT, secondary]."),
                ("'In some cases, watchful waiting or delayed therapy is used for slow-growing M1' "
                 "[remiszewski2025, FT] — an existing clinical practice of withholding therapy, "
                 "which is the half of an adaptive schedule that is hardest to introduce."),
            ],
            "evidence_against": [],
            "what_survives": "Ground iii holds. It is the least contested of the five.",
        },
        {
            "ground": "iv",
            "memo_claim": ("Burden is countable: lung nodules on volumetric CT are arguably a better "
                           "control signal than a serum marker."),
            "verdict": "PLAUSIBLE, UNTESTED — an assertion about measurability, not an EMC finding",
            "evidence_for": [
                ("Pulmonary metastases 'remain the most common and are present in up to 50-90 % of "
                 "patients at some point during their disease' [remiszewski2025, FT, secondary], so "
                 "the compartment an adaptive schedule would track is the dominant one."),
            ],
            "evidence_against": [
                ("No EMC study reports volumetric nodule tracking, and no EMC study reports a "
                 "measured in-vivo growth rate at all (see `identifiability`). The claim that "
                 "volumetric CT would be a good control signal in EMC has never been tested in EMC."),
                ("Adaptive abiraterone used PSA — a continuous, cheap, weekly biomarker. CT is "
                 "discrete, expensive and carries dose; the control loop's sampling interval is "
                 "therefore months, not days, and no analysis of whether that is fast enough for "
                 "EMC's tempo exists."),
            ],
            "what_survives": ("The compartment is right and the instrument is untested. This is the "
                              "ground most easily converted into real work: a retrospective "
                              "volumetric re-read of serial EMC chest CTs would produce the first "
                              "in-vivo EMC growth rates and is not a wet-lab task."),
        },
        {
            "ground": "v",
            "memo_claim": ("Patients are on therapy for years, so halving cumulative dose is a claim "
                           "on its own."),
            "verdict": "FOLLOWS FROM ii + iii, and the anchor is real",
            "evidence_for": [
                ("Adaptive abiraterone held 10 of 11 patients in stable oscillation at 47 % of "
                 "standard cumulative dose [zhang2017_adaptive_prostate, secondary]."),
                ("Grade 3 events in the EMC pazopanib trial: hypertension 9/26 (35 %), ALT rise "
                 "6/26 (23 %), AST rise 5/26 (19 %) [stacchiotti2019_pazopanib, API] — a real "
                 "toxicity burden to halve, over a median PFS measured in years."),
            ],
            "evidence_against": [
                ("A cumulative-dose endpoint is not a survival endpoint, and a trial powered on it "
                 "answers a different question from the one a regulator or a clinician asks."),
            ],
            "what_survives": ("Ground v is sound and is the cheapest endpoint to power, which is "
                              "why it is also the least persuasive on its own."),
        },
    ]


# ---------------------------------------------------------------------------
# 2 · the competition model
# ---------------------------------------------------------------------------

DT = 0.5                  # days
HORIZON = 365.25 * 20     # 20 years
PROGRESSION_MULTIPLE = 1.2   # burden threshold, RECIST-flavoured


def simulate(r_s, cost, delta, f0, n0_frac=0.5, adaptive=False,
             mu_on=0.0, mu_off=0.0, turnover=0.0, dt=DT, horizon=HORIZON,
             progression_multiple=PROGRESSION_MULTIPLE):
    """Two-population competitive Lotka-Volterra, K normalised to 1.

    dS/dt = r_S S (1 - (S + R)) - turnover*S - delta u(t) S - mu_on u(t) S + mu_off (1-u(t)) R
    dR/dt = r_R R (1 - (S + R)) - turnover*R + mu_on u(t) S - mu_off (1-u(t)) R
    r_R   = r_S (1 - cost)

    Competition is SYMMETRIC (both populations feel total burden). That is the conservative
    choice: asymmetric competition in which S suppresses R more than R suppresses S manufactures
    an adaptive-therapy advantage by assumption, and no EMC datum supports either direction.

    mu_on / mu_off = 0 gives the heritable-resistance model; non-zero gives reversible plasticity.
    `turnover` is a density-independent death rate applied to both populations.

    Returns a dict with time to progression, whether it was censored at the horizon, whether the
    adaptive rule ever fired, and the time for the resistant fraction to reach 50 %.
    """
    n0 = n0_frac
    s = n0 * (1.0 - f0)
    r = n0 * f0
    r_r = r_s * (1.0 - cost)
    u = 1.0
    t = 0.0
    holidays = 0
    t_half_resistant = None
    threshold = n0 * progression_multiple
    steps = int(horizon / dt)
    for _ in range(steps):
        n = s + r
        if adaptive:
            if u > 0.5 and n <= 0.5 * n0:
                u = 0.0
                holidays += 1
            elif u < 0.5 and n >= n0:
                u = 1.0
        space = 1.0 - n
        ds = (r_s * s * space - turnover * s - delta * u * s
              - mu_on * u * s + mu_off * (1.0 - u) * r)
        dr = r_r * r * space - turnover * r + mu_on * u * s - mu_off * (1.0 - u) * r
        s = max(0.0, s + dt * ds)
        r = max(0.0, r + dt * dr)
        t += dt
        if t_half_resistant is None and (s + r) > 0 and r / (s + r) >= 0.5:
            t_half_resistant = t
        if s + r >= threshold:
            return {"ttp": t, "censored": False, "holidays": holidays,
                    "t_resistant_fraction_50pc": t_half_resistant}
    return {"ttp": horizon, "censored": True, "holidays": holidays,
            "t_resistant_fraction_50pc": t_half_resistant}


F0_GRID = [1e-4, 1e-3, 1e-2, 0.05, 0.10, 0.20, 0.30]
COST_GRID = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]
TURNOVER_GRID = [0.0, 0.2, 0.5]     # density-independent death, as a multiple of r_S
DELTA_GRID = [1.0, 2.0, 3.0, 6.0, 12.0]   # drug kill rate, as a multiple of r_S


def _spread(vals):
    return {"min": min(vals), "max": max(vals)}


def competition_model():
    """Where does adaptive scheduling win, and by how much? Time is reported in DOUBLING TIMES."""
    # r_s is expressed in units of 1/day but the OUTPUT is normalised by the sensitive
    # population's doubling time, because EMC's in-vivo growth rate is unmeasured
    # (`identifiability`). Any absolute time axis would be fabricated.
    r_s = math.log(2.0) / 180.0        # nominal 180-day volume doubling time; a SCALE, not a claim
    dbl = math.log(2.0) / r_s
    delta = 3.0 * r_s                  # drug kills sensitive cells at 3x their intrinsic growth rate

    grid = []
    for f0 in F0_GRID:
        for cost in COST_GRID:
            mtd = simulate(r_s, cost, delta, f0, adaptive=False)
            ada = simulate(r_s, cost, delta, f0, adaptive=True)
            grid.append({
                "initial_resistant_fraction": f0,
                "resistance_cost": cost,
                "ttp_mtd_doubling_times": round(mtd["ttp"] / dbl, 3),
                "ttp_adaptive_doubling_times": round(ada["ttp"] / dbl, 3),
                "adaptive_gain_ratio": round(ada["ttp"] / mtd["ttp"], 4),
                "adaptive_holidays_fired": ada["holidays"],
                "adaptive_rule_never_fired": ada["holidays"] == 0,
                "censored": mtd["censored"] or ada["censored"],
                "t_resistant_fraction_50pc_mtd_doubling_times": (
                    None if mtd["t_resistant_fraction_50pc"] is None
                    else round(mtd["t_resistant_fraction_50pc"] / dbl, 3)),
                "t_resistant_fraction_50pc_adaptive_doubling_times": (
                    None if ada["t_resistant_fraction_50pc"] is None
                    else round(ada["t_resistant_fraction_50pc"] / dbl, 3)),
            })

    live = [g for g in grid if not g["censored"]]
    by_f0 = {}
    for f0 in F0_GRID:
        gs = [g["adaptive_gain_ratio"] for g in live if g["initial_resistant_fraction"] == f0]
        by_f0[str(f0)] = _spread(gs) if gs else None
    by_cost = {}
    for c in COST_GRID:
        gs = [g["adaptive_gain_ratio"] for g in live if g["resistance_cost"] == c]
        by_cost[str(c)] = _spread(gs) if gs else None

    # robustness: does the ordering survive a drug-potency sweep and a cell-turnover sweep?
    delta_sweep = []
    for dm in DELTA_GRID:
        for cost in (0.0, 0.30):
            mtd = simulate(r_s, cost, dm * r_s, 1e-3, adaptive=False)
            ada = simulate(r_s, cost, dm * r_s, 1e-3, adaptive=True)
            delta_sweep.append({"delta_over_r_s": dm, "resistance_cost": cost,
                                "adaptive_gain_ratio": round(ada["ttp"] / mtd["ttp"], 4),
                                "censored": mtd["censored"] or ada["censored"]})
    turnover_sweep = []
    for tv in TURNOVER_GRID:
        for cost in (0.0, 0.10, 0.30):
            mtd = simulate(r_s, cost, delta, 1e-3, adaptive=False, turnover=tv * r_s)
            ada = simulate(r_s, cost, delta, 1e-3, adaptive=True, turnover=tv * r_s)
            turnover_sweep.append({"turnover_over_r_s": tv, "resistance_cost": cost,
                                   "adaptive_gain_ratio": round(ada["ttp"] / mtd["ttp"], 4),
                                   "censored": mtd["censored"] or ada["censored"],
                                   "note": ("CENSORED — at least one arm reached the 20-year "
                                            "horizon, so this ratio is horizon-limited. Where BOTH "
                                            "arms are censored the ratio is exactly 1.0 by "
                                            "construction and is an artefact, not an equality.")
                                   if (mtd["censored"] or ada["censored"]) else None})

    return {
        "question": ("Over what region of (initial resistant fraction, fitness cost of resistance) "
                     "does an adaptive schedule delay progression relative to continuous maximum "
                     "dosing?"),
        "model": {
            "form": ("two-population competitive Lotka-Volterra, carrying capacity normalised to 1, "
                     "symmetric competition, drug acts only on the sensitive population"),
            "why_symmetric_competition": ("Asymmetric competition in which sensitive cells suppress "
                                          "resistant cells more than the reverse manufactures the "
                                          "adaptive advantage by assumption. No EMC datum supports "
                                          "either direction, so the conservative symmetric form is "
                                          "used and the result is a LOWER bound on the adaptive gain."),
            "adaptive_rule": ("Gatenby-style AT-50: withdraw drug when burden falls to 50 % of "
                              "baseline, resume when it returns to baseline."),
            "progression": f"total burden reaches {PROGRESSION_MULTIPLE} x baseline",
            "baseline_burden_fraction_of_K": 0.5,
            "drug_kill_rate": "3 x the sensitive population's intrinsic growth rate (swept below)",
            "integrator": f"forward Euler, dt = {DT} day, horizon {HORIZON / 365.25:.0f} years",
            "time_units": ("SENSITIVE-POPULATION DOUBLING TIMES, not months. EMC's in-vivo growth "
                           "rate is unmeasured, so an absolute time axis would be fabricated."),
        },
        "grid": grid,
        "gain_ratio_spread_by_initial_resistant_fraction": by_f0,
        "gain_ratio_spread_by_resistance_cost": by_cost,
        "delta_robustness_sweep": delta_sweep,
        "turnover_robustness_sweep": turnover_sweep,
        "readings": {
            "the_shape": (
                "⛔ THE MODEL CONTRADICTS THE AXIS THE MEMO PUT THE WEIGHT ON. The adaptive gain is "
                "governed by the INITIAL RESISTANT FRACTION and is very nearly independent of the "
                "fitness cost of resistance: sweeping f0 from 1e-4 to 0.3 moves the gain ratio "
                "across its whole range, while sweeping the cost from 0 to 0.5 at fixed f0 barely "
                "moves it. A cost raises time to progression in BOTH arms by roughly the same "
                "factor, so it cancels in the ratio."),
            "why_a_cost_is_not_required": (
                "In this model form, competitive suppression operates through COMPETITION FOR "
                "SPACE, not through a growth-rate differential. Killing the sensitive population "
                "frees capacity that the resistant population then grows into faster — the "
                "(1 - S - R) term — and that mechanism is present whether or not r_R < r_S. The "
                "memo's stated killer ('resistance may not be fitness-costed ... so competitive "
                "suppression would have nothing to work with') is therefore not what this model "
                "says. ⚠ This is a property of the MODEL FORM and not a theorem: whether a cost of "
                "resistance is necessary is an open and actively contested question in the "
                "adaptive-therapy literature, and a different competition kernel can restore the "
                "requirement. It is reported here because it is what the stated model returns, and "
                "because it changes which measurement is decision-relevant."),
            "where_the_cost_DOES_act": (
                "On the resistant fraction itself, not on time to progression. "
                "`t_resistant_fraction_50pc_*` shows the cost delaying the moment the tumour becomes "
                "majority-resistant. That matters for a containment strategy and for second-line "
                "options; it does not drive the time-to-progression gain."),
            "the_degenerate_corner": (
                "At f0 = 0.3 the adaptive rule NEVER FIRES (`adaptive_rule_never_fired`): the drug "
                "cannot halve total burden because the resistant compartment alone is already close "
                "to the trigger, so the adaptive arm is identical to continuous dosing by "
                "construction. A high resistant fraction does not make adaptive therapy worse — it "
                "makes it unimplementable."),
            "robustness": (
                "The ordering survives a drug-potency sweep over delta = 1-12 x r_S (the gain "
                "saturates above about 3 x) and a cell-turnover sweep. Moderate turnover INCREASES "
                "the gain. High turnover pushes both arms past the 20-year horizon, where the ratio "
                "of 1.0 is a censoring artefact and is flagged as one rather than reported as "
                "equality."),
        },
    }


def plasticity_model():
    """The second mechanism: resistance as a REVERSIBLE phenotype, not a heritable genotype."""
    r_s = math.log(2.0) / 180.0
    dbl = math.log(2.0) / r_s
    delta = 3.0 * r_s
    rows = []
    # switching rates expressed as multiples of r_s so the result is scale-free
    for k_on in (0.0, 0.5, 2.0):
        for k_off in (0.0, 0.5, 2.0):
            mtd = simulate(r_s, 0.0, delta, 1e-3, adaptive=False,
                           mu_on=k_on * r_s, mu_off=k_off * r_s)
            ada = simulate(r_s, 0.0, delta, 1e-3, adaptive=True,
                           mu_on=k_on * r_s, mu_off=k_off * r_s)
            rows.append({
                "switch_to_resistant_on_drug_x_rs": k_on,
                "revert_to_sensitive_off_drug_x_rs": k_off,
                "ttp_mtd_doubling_times": round(mtd["ttp"] / dbl, 3),
                "ttp_adaptive_doubling_times": round(ada["ttp"] / dbl, 3),
                "adaptive_gain_ratio": round(ada["ttp"] / mtd["ttp"], 4),
                "censored": mtd["censored"] or ada["censored"],
            })
    switching = [r for r in rows if r["switch_to_resistant_on_drug_x_rs"] > 0]
    reverting = [r for r in switching if r["revert_to_sensitive_off_drug_x_rs"] > 0]
    non_reverting = [r for r in switching if r["revert_to_sensitive_off_drug_x_rs"] == 0]
    none_at_all = [r for r in rows if r["switch_to_resistant_on_drug_x_rs"] == 0][0]
    return {
        "question": ("If EMC's resistance is a reversible phenotype rather than a selected clone — "
                     "which is what mutational quietness makes more likely — does intermittent "
                     "dosing still help, and for the same reason?"),
        "setup": ("Same model, fitness cost set to ZERO, initial resistant fraction 1e-3, with "
                  "drug-induced switching S->R while on drug and reversion R->S while off drug, "
                  "both expressed as multiples of r_S."),
        "grid": rows,
        "reading": {
            "censoring_warning": ("Rows with censored=true had at least one arm reach the 20-year "
                                  "horizon; their ratios are horizon-limited and the summaries "
                                  "below are computed over UNCENSORED rows only."),
            "gain_no_switching_at_all": none_at_all["adaptive_gain_ratio"],
            "gain_switching_without_reversion_max": max(r["adaptive_gain_ratio"]
                                                        for r in non_reverting
                                                        if not r["censored"]),
            "gain_switching_with_reversion_max_uncensored": max(
                r["adaptive_gain_ratio"] for r in reverting if not r["censored"]),
            "censored_reverting_rows": [r for r in reverting if r["censored"]],
            "conclusion": (
                "Drug-induced switching is the mechanism that most damages the adaptive schedule, "
                "and reversion is what repairs it. If the sensitive population converts to "
                "resistant WHILE ON DRUG and does not convert back, the gain falls below the "
                "no-switching case, because every day of drug exposure manufactures resistance. If "
                "it converts back during a holiday, the gain is restored or exceeded — and the one "
                "cell with slow switching and fast reversion runs past the 20-year horizon "
                "entirely. Reversion of a PRE-EXISTING resistant pool with no drug-induced "
                "switching at all is stronger still. ⭐ That is a "
                "SECOND, independent rationale for intermittent dosing — resensitisation rather "
                "than competitive release — and it has a different observable: competitive release "
                "predicts the resistant fraction falls during a holiday because sensitive cells "
                "outgrow it, while resensitisation predicts it falls because resistant cells become "
                "sensitive again, which shows up as a SECOND RESPONSE ON RE-CHALLENGE. "
                "⚠ At the fastest switching rate tested (2 x r_S) progression arrives before any "
                "holiday can fire and the adaptive arm is identical to continuous dosing — the same "
                "degenerate corner as a high initial resistant fraction."),
        },
    }


# ---------------------------------------------------------------------------
# 3 · mutational quietness — for or against?
# ---------------------------------------------------------------------------

def mutational_quietness():
    return {
        "question": ("EMC's mutational quietness is real. Does it cut FOR or AGAINST the "
                     "competitive-release premise adaptive therapy rests on?"),
        "evidence": [
            ("The only matched EMC trio sequenced end to end: 'While the primary tumor and lung "
             "metastasis had similar somatic variations and CNVs, the pelvic metastasis had more "
             "unique SVs with especially increased mutational burden of SVs in chromosome 2. This "
             "suggests that different molecular drivers appear in more advanced, relapsing EMC "
             "compared with the primary tumor and early lung metastasis.' "
             "[zou2023_wgs, FT, n = 1]"),
            ("EMC's measured tumour mutational burden is 0-2 mutations/Mb "
             "(emc-unexplored-treatment-lanes.md §3.7, citing the repository's curated record)."),
        ],
        "cuts_for": [
            ("⭐ THE DECISIVE ONE, AND IT IS DECISIVE ONLY BECAUSE THE MODEL SAYS WHICH AXIS "
             "MATTERS. A low mutation rate implies a SMALL pre-existing resistant fraction at "
             "treatment start, and `competition_model` shows the initial resistant fraction is the "
             "axis that governs the adaptive gain — the gain ratio runs across its entire range as "
             "f0 moves from 1e-4 to 0.3, and at f0 = 0.3 the adaptive rule cannot even fire."),
            ("Fewer independent resistance mechanisms means a resistant compartment more likely to "
             "be a single coherent phenotype — which is what a two-population model assumes and "
             "what a heterogeneous, highly-mutated tumour violates."),
            ("The fitness cost, which is what the memo expected to be decisive, is very nearly "
             "irrelevant to the time-to-progression gain in this model: it raises time to "
             "progression in both arms by about the same factor and cancels in the ratio. So the "
             "route by which quietness would have cut AGAINST — non-genetic resistance being "
             "cost-free — turns out to act on the axis that does not drive the result."),
        ],
        "cuts_against": [
            ("Pazopanib's target is HOST ENDOTHELIUM, not the tumour cell (the memo's own "
             "falsifier). If the resistant compartment lives in the vasculature or the stroma it is "
             "not a heritable tumour lineage at all, and a two-population TUMOUR-CELL model has no "
             "resistant population to track. Mutational quietness makes this reading more likely, "
             "because it removes the obvious alternative. ⚠ This is not an argument about the "
             "cost — it is an argument that the model's state variables may not exist, which is "
             "worse."),
            ("If resistance is drug-INDUCED phenotype switching that does not revert, "
             "`plasticity_model` shows the adaptive gain falls below the no-switching case: every "
             "day of drug exposure manufactures resistance, and a schedule that dispenses less drug "
             "helps less than a schedule that dispenses none. Quietness raises the probability of "
             "exactly this mechanism."),
        ],
        "net_verdict": {
            "direction": "FOR, on net — and this REVERSES the reading the memo's falsifier implies",
            "why": ("The memo's stated killer is that anti-angiogenic resistance may not be "
                    "fitness-costed, 'so competitive suppression would have nothing to work with'. "
                    "The model does not agree: competitive suppression here operates through "
                    "competition for space, which is present whether or not resistance is costly, "
                    "and the cost cancels in the time-to-progression ratio. What the gain actually "
                    "depends on is the SIZE of the resistant compartment at treatment start — and "
                    "mutational quietness is an argument that it is small. On the axis that "
                    "matters, quietness helps."),
            "the_caveat_that_keeps_it_honest": (
                "⚠ Whether a cost of resistance is REQUIRED is a property of the competition "
                "kernel, not a theorem, and it is contested in the adaptive-therapy literature. "
                "This analysis reports what the stated model returns and flags that a different "
                "kernel can restore the requirement. What is robust across the sweeps run here — "
                "drug potency 1-12 x r_S, cell turnover 0-0.5 x r_S — is the RANK: f0 dominates "
                "cost in every one."),
            "the_counter_evidence_on_the_other_side": (
                "The same WGS trio is the one EMC dataset showing that heritable divergence DOES "
                "occur: the advanced pelvic metastasis carried unique structural variants the "
                "primary and early lung metastasis did not. n = 1, uncontrolled, and not tied to "
                "any treatment exposure — but it is direct evidence against 'EMC does not evolve', "
                "and a tumour that evolves has a resistant compartment for the model to describe."),
        },
    }


# ---------------------------------------------------------------------------
# 4 · what is actually measured in EMC
# ---------------------------------------------------------------------------

def identifiability():
    return {
        "question": "Which of this model's parameters has ever been measured in EMC?",
        "verdict": ("None of the rate parameters. Every one of the five is unmeasured in EMC in "
                    "vivo, which is why this module emits no predicted PFS in months."),
        "parameters": [
            {
                "symbol": "r_S",
                "meaning": "intrinsic growth rate of the drug-sensitive population",
                "measured_in_emc": False,
                "closest_available": ("ex vivo doubling times of 5.09 days (USZ20-EMC1) and 6.05 "
                                      "days (USZ22-EMC2) [bangerter2023_models, FT]"),
                "why_not_usable": ("Those are sarco-sphere culture rates. They imply a volume "
                                   "doubling every ~5-6 days, which is irreconcilable with a "
                                   "disease whose metastatic median OS is 5-7 years. An ex vivo "
                                   "rate cannot be transplanted into an in-vivo model, and doing so "
                                   "silently is how a simulation acquires false precision."),
                "how_to_measure_it_at_zero_cost": ("Volumetric re-read of serial chest CTs in any "
                                                   "EMC cohort with archived imaging. This would "
                                                   "produce the first in-vivo EMC growth rates and "
                                                   "needs no laboratory."),
            },
            {
                "symbol": "c",
                "meaning": "fitness cost of resistance in the absence of drug",
                "measured_in_emc": False,
                "closest_available": "nothing in EMC; nothing in any sarcoma for an anti-angiogenic",
                "how_much_it_matters": ("LESS THAN THE MEMO ASSUMES. In this model form the cost "
                                        "raises time to progression in both arms by about the same "
                                        "factor and cancels in the ratio. It governs the time to "
                                        "majority-resistance, not the adaptive gain."),
            },
            {
                "symbol": "f0",
                "meaning": "resistant fraction at treatment start",
                "measured_in_emc": False,
                "closest_available": ("indirect only — 4/22 RECIST responses in the phase 2 bounds "
                                      "the SENSITIVE fraction at the whole-lesion level, not the "
                                      "cellular one"),
                "how_much_it_matters": ("MOST. It is the axis the adaptive gain actually runs on, "
                                        "and it is the axis EMC's mutational quietness speaks to."),
            },
            {
                "symbol": "delta",
                "meaning": "drug-induced death rate on sensitive cells",
                "measured_in_emc": False,
                "closest_available": ("the trial's tempo change — documented progression within 6 "
                                      "months before enrolment, median PFS 19 months on drug — "
                                      "which constrains delta only jointly with r_S"),
            },
            {
                "symbol": "mu_on / mu_off",
                "meaning": "phenotype-switching rates",
                "measured_in_emc": False,
                "closest_available": "nothing; no EMC re-challenge data of any kind was found",
            },
        ],
        "consequence": ("The honest output of this lane is a PARAMETER REGION and a measurement "
                        "list, exactly as §3.8 said it should be. Any absolute predicted PFS would "
                        "be a statement about the assumed r_S, not about EMC."),
    }


# ---------------------------------------------------------------------------
# 5 · the falsifier
# ---------------------------------------------------------------------------

def falsifier():
    return {
        "the_memo_named_the_wrong_one": {
            "memo_falsifier": ("'anti-angiogenic resistance may not be fitness-costed, because the "
                               "drug's target is host endothelium, not the tumour cell — so "
                               "resistance could be microenvironmental, and competitive suppression "
                               "would have nothing to work with.'"),
            "what_the_model_says": (
                "That sentence conflates two separable claims, and only one of them is fatal. "
                "(a) 'Resistance is not fitness-costed' — the model shows this is NOT fatal: the "
                "cost cancels in the time-to-progression ratio because competitive suppression here "
                "works through competition for space, not through a growth-rate differential. "
                "(b) 'Resistance is microenvironmental rather than a tumour-cell trait' — this IS "
                "fatal, and for a different reason: it means the model's second state variable does "
                "not exist, so there is no resistant population to suppress at any cost. The memo's "
                "falsifier is correct in its conclusion and wrong in its mechanism, and the "
                "difference decides which measurement is worth making."),
        },
        "primary": {
            "statement": ("Does a HERITABLE, TUMOUR-CELL-INTRINSIC resistant compartment exist in "
                          "EMC under pazopanib, and is the tumour close enough to carrying capacity "
                          "for the two compartments to compete? If resistance lives in the host "
                          "vasculature, or if the tumour is far from any resource limit, there is "
                          "no competition to exploit and adaptive scheduling has no mechanistic "
                          "basis in this disease."),
            "why_it_is_the_falsifier_and_not_a_limitation": (
                "Both halves are preconditions for the model to describe anything at all, whereas "
                "every parameter in `identifiability` merely sets the size of the effect. A "
                "precondition that fails cannot be compensated by a favourable parameter value."),
            "the_second_falsifier_the_model_promotes": (
                "Is the initial resistant fraction small? `competition_model` shows the adaptive "
                "gain vanishes as f0 approaches 0.3, and at that value the adaptive rule cannot "
                "fire at all. This is the axis the memo did not weight, and it is the one that "
                "decides the size of the prize."),
        },
        "the_discriminating_observations, in order of cost": [
            {
                "observation": ("In patients who progress on pazopanib and stop it, does the growth "
                                "rate of previously-responding lesions DIFFER from the on-drug "
                                "progression rate?"),
                "discriminates": ("A slower off-drug growth rate is direct evidence of a fitness "
                                  "cost. No change is evidence of c = 0."),
                "cost": "retrospective imaging re-read; no laboratory; no new patients",
            },
            {
                "observation": "Does pazopanib RE-CHALLENGE after a holiday produce a second response?",
                "discriminates": ("A second response is evidence of REVERSION (plasticity model, "
                                  "resensitisation mechanism). No second response is evidence of "
                                  "durable heritable resistance."),
                "cost": ("case-finding in existing EMC cohorts; no EMC re-challenge data of any kind "
                         "was found in this pass"),
            },
            {
                "observation": ("Paired biopsy or ctDNA at progression: is there clonal selection, "
                                "or none?"),
                "discriminates": ("Clonal selection supports a heritable resistant compartment and "
                                  "therefore the two-population model. No clonal change supports "
                                  "phenotypic or microenvironmental resistance."),
                "cost": "requires tissue — the only item here that is not desk-computable",
                "closest_existing_datum": ("the matched trio's advanced pelvic metastasis carried "
                                           "unique structural variants [zou2023_wgs], which is "
                                           "n = 1 and not tied to treatment"),
            },
        ],
        "secondary_falsifier": {
            "statement": ("Is EMC's burden trackable fast enough to close the control loop? An "
                          "adaptive schedule needs a burden readout at an interval short relative "
                          "to the tumour's doubling time. Adaptive abiraterone used weekly PSA; "
                          "EMC would use CT at intervals of months."),
            "status": ("Untested. Also unanswerable until r_S is measured — which is the same free "
                       "imaging re-read named above, so ONE piece of desk work moves both."),
        },
    }


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------

def build():
    return {
        "_schema": "emc-adaptive-pazopanib/1",
        "_generated_by": "research/modalities/emc_adaptive_pazopanib.py",
        "_one_home_for": ("every number in "
                          "research/manuscripts/emc-adaptive-scheduling-pazopanib.md; the prose "
                          "points here and types no arithmetic of its own"),
        "_disclaimer": ("⛔ NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL "
                        "READINESS. Adaptive scheduling has never been tested in EMC or in any "
                        "sarcoma. Reducing the dose of an active drug outside a trial can shorten "
                        "disease control. This artifact describes what would have to be true for a "
                        "hypothesis to hold; it is not a treatment plan and contains no predicted "
                        "survival for any patient."),
        "lane": "emc-unexplored-treatment-lanes.md §3.8 — adaptive scheduling of pazopanib",
        "date": "2026-08-07",
        "sources": SOURCES,
        "five_grounds": five_grounds(),
        "competition_model": competition_model(),
        "plasticity_model": plasticity_model(),
        "mutational_quietness": mutational_quietness(),
        "identifiability": identifiability(),
        "falsifier": falsifier(),
        "verdict": {
            "resolved": False,
            "status": "SURVIVES as a live, well-posed question — and is now narrower than the memo left it",
            "statement": (
                "Four of the five grounds hold, one (a single active systemic class) is overstated "
                "and survives only in a weaker form. Ground ii is strengthened by a fact the memo "
                "did not use: the phase 2 required documented RECIST progression within the "
                "previous six months, so an 18 % response rate with a 19-month median PFS is a "
                "measured change of TEMPO in a cohort selected for growth. On the question the "
                "memo left open, the model returns an answer OPPOSITE to the one its own falsifier "
                "implies: EMC's mutational quietness cuts FOR the adaptive premise, because the "
                "adaptive gain runs on the INITIAL RESISTANT FRACTION — which quietness argues is "
                "small — and is very nearly independent of the fitness cost of resistance, which is "
                "the parameter the memo built its falsifier on. What remains genuinely fatal is not "
                "the absence of a cost but the possible absence of a tumour-cell resistant "
                "compartment at all."),
            "what_is_new_here": [
                "the five grounds checked one by one, with the overstated one named",
                ("the phase 2's entry criterion promoted from fine print to the load-bearing "
                 "quantitative support for ground ii"),
                ("⛔ a demonstration that the adaptive gain is governed by the INITIAL RESISTANT "
                 "FRACTION and is very nearly independent of the fitness cost — the opposite of the "
                 "axis the memo weighted, robust across drug-potency and cell-turnover sweeps"),
                ("the consequent re-answering of the memo's open question: mutational quietness "
                 "cuts FOR, not against"),
                ("a restatement of the falsifier that separates 'resistance is not costly' (not "
                 "fatal) from 'resistance is not a tumour-cell trait' (fatal) — the memo conflated "
                 "them and reached the right conclusion by the wrong mechanism"),
                ("a second model showing that drug-induced, non-reverting phenotype switching is "
                 "the mechanism that most damages the schedule, and that reversion repairs it — "
                 "which supplies a distinct, cheap observable: a second response on re-challenge"),
                ("an explicit statement that no rate parameter of the model has ever been measured "
                 "in EMC in vivo, and that the closest available figures are ex vivo doubling times "
                 "irreconcilable with the clinical tempo"),
            ],
            "the_one_free_step_that_moves_it": (
                "A volumetric re-read of serial chest CTs in any EMC cohort with archived imaging. "
                "It would produce the first in-vivo EMC growth rates, answer the secondary "
                "falsifier about loop speed, and — in patients who stopped pazopanib at progression "
                "— test the primary falsifier by comparing on-drug and off-drug growth rates. It "
                "needs imaging access, which this program does not have, so the honest state is "
                "'blocked on data only a collaborator can supply', not 'blocked on compute'."),
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
        print("emc_adaptive_pazopanib: artifact matches")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    cm = doc["competition_model"]
    print(f"wrote {OUT}")
    print("  gain ratio spread by initial resistant fraction:")
    for k, v in cm["gain_ratio_spread_by_initial_resistant_fraction"].items():
        print(f"    f0={k:<8} {v['min']:.4f} - {v['max']:.4f}")
    print("  gain ratio spread by resistance cost:")
    for k, v in cm["gain_ratio_spread_by_resistance_cost"].items():
        print(f"    c={k:<6} {v['min']:.4f} - {v['max']:.4f}")
    print(f"  quietness verdict: {doc['mutational_quietness']['net_verdict']['direction']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
