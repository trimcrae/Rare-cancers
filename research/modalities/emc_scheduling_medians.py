#!/usr/bin/env python3
"""The two-population scheduling model for EMC, calibrated to FOUR SEPARATE MEDIANS.

WHY THIS EXISTS
---------------
RT-SCHEDULING's named next input was "the pooled progression-free-survival data already curated
here". ⛔ There is no such pool and there cannot be one: `systems/POLICY-evidence.md` s2.4 never
merges time-anchored endpoints, and `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`
-> `analyses.A7_the_pool_that_is_refused` refuses the neighbouring pool explicitly rather than by
omission. What exists instead is FOUR EMC-specific median progression-free-survival figures whose
DISPERSION IS REPORTED FOUR DIFFERENT WAYS:

    pazopanib_phase2                 19.0 months, 95% CI 11.0-27.0
    sunitinib_nivolumab_immunosarc2  13.2 months, 95% CI  5.7-20.7
    anthracycline_italian_rcn         8.0 months, OBSERVED RANGE 2-10 (not a confidence interval)
    chiusole_metastatic_chemo         9.0 months, NO interval, NO range, NO number at risk

This module carries each of the four as its OWN parameter with its OWN interval OF ITS OWN KIND,
and carries the fourth as what it is: a point with no width. It never pools them, never ranks them,
never differences them and computes no test statistic over them.

⛔⛔ THE ONE THING THIS FILE REFUSES MOST FIRMLY IS A ZERO-WIDTH INTERVAL. `[9.0, 9.0]` renders
identically to a precisely-measured quantity and is the single easiest way for a missing dispersion
to become a fabricated one. The Chiusole arm therefore emits `interval: null` with
`propagated: false` and a reason string, everywhere, at every level of the output.

WHAT IT COMPUTES
----------------
  L1  ANALYTIC, per arm. Under the model, an observed median time to progression bounds the net
      growth rate of whatever compartment eventually progressed:  r_R >= ln(theta) / T_median,
      equivalently a doubling time  T_double <= T_median * ln(2)/ln(theta).  It is a BOUND and not
      an estimate because any time spent reaching nadir shortens the regrowth phase. Intervals are
      propagated by mapping the source's own interval endpoints through the same monotone
      transform -- and only where the source published an interval to map.
  L2  NUMERICAL, per arm. The two-population competitive Lotka-Volterra system is integrated and
      r_R is fitted by bisection so that the simulated time to progression equals that arm's median,
      over a grid of the parameters no EMC series reports (initial resistant fraction f0, fitness
      cost of resistance). This measures, rather than asserts, WHICH parameters the medians pin.
  L3  The identifiability verdict that falls out of L2, and the misattributed-figure roster, which
      is read from the source artifact and stands on its own.

⛔ WHAT THIS FILE ASSERTS ABOUT ANY DRUG: NOTHING. No efficacy, no comparative effectiveness, no
safety, no therapeutic window, no clinical readiness, and no recommendation of any kind including a
negative one. Every quantity below is a property of a MODEL given a published median. Adaptive
scheduling has never been tested in EMC or in any sarcoma.

⛔ NO PREDICTED PROGRESSION-FREE SURVIVAL IS EMITTED FOR ANY SCHEDULE. The sibling model
`emc_adaptive_pazopanib.py` refuses that for a stated reason (every rate parameter is unmeasured in
EMC in vivo) and this file does not weaken the refusal -- it explains it, by measuring which
parameter the four medians actually constrain and showing it is not the one the adaptive question
turns on.

ONE HOME. Every median, interval, quote and citation below is READ AT RUN TIME from
`research/manuscripts/endpoint/emc-systemic-therapy-pooling.json`, which owns them. Nothing is
retyped here; the source file's sha256 is recorded in the artifact so a reader can prove which bytes
these parameters came from.

METHOD SCOPE, DECLARED UP FRONT (CLAUDE.md s5, breadth-first / standard-depth). Deterministic ODE
integration, RK-free explicit Euler at dt = 1 day matching the sibling model's integrator, one
progression rule (RECIST 1.1 nadir), two burden-unit conventions because that is a real degree of
freedom, bisection to 1e-6/day. NO bootstrap, NO Monte Carlo, NO replicate seeds, NO sensitivity
layer beyond the declared grid. If a reader wants more, the grid is the place to widen; nothing
here is tuned.

Pure stdlib. Usage:

    python3 research/modalities/emc_scheduling_medians.py            # write the artifact
    python3 research/modalities/emc_scheduling_medians.py --check    # fail if the artifact drifted
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "research/manuscripts/endpoint/emc-systemic-therapy-pooling.json")
SRC_REL = "research/manuscripts/endpoint/emc-systemic-therapy-pooling.json"
OUT = os.path.join(REPO, "research/modalities/emc-scheduling-medians.json")

DAYS_PER_MONTH = 365.25 / 12.0

# ---------------------------------------------------------------------------
# 0 - the progression rule, and the one modelling choice that moves every number
# ---------------------------------------------------------------------------
#
# RECIST 1.1 calls progressive disease a >=20 % increase in the SUM OF LONGEST DIAMETERS over the
# smallest sum recorded on study (the nadir), with a >=5 mm absolute minimum, or an unequivocal new
# lesion. A two-population model's state variables are BURDENS, so the 20 % has to be expressed in
# burden units, and the conversion is a declared choice rather than a fact:
#
#   diameter convention  theta = 1.20    (burden read as if it were the RECIST sum itself)
#   volume convention    theta = 1.20^3  (isotropic spherical growth: a 20 % diameter rise is a
#                                         72.8 % volume rise)
#
# Both are reported for every arm because the choice is worth exactly a factor of
# ln(1.2^3)/ln(1.2) = 3 on every rate this file computes -- see `convention_vs_data` in the output,
# where that factor is compared against the spread of the four medians themselves.
THETA_CONVENTIONS = {
    "diameter_1.20": 1.20,
    "volume_1.728": 1.20 ** 3,
}

# The model captures the SIZE criterion only. A new lesion is progression under RECIST 1.1 and has
# no representation in a two-compartment burden model at all; that shortens real PFS relative to the
# model's, in the same direction as the nadir effect, and is recorded rather than corrected.

# ---------------------------------------------------------------------------
# 1 - inputs, read from the artifact that owns them
# ---------------------------------------------------------------------------

# Dispersion kinds. The whole point of this module is that these three are NOT interchangeable.
DISPERSION_KINDS = {
    "ci95": {
        "what_it_is": "a 95% confidence interval on the median, published by the source",
        "may_be_propagated": True,
        "how": ("mapped endpoint-for-endpoint through the same monotone transform used for the "
                "point. A monotone reparameterisation of an interval preserves its coverage, so "
                "the result is a 95% interval FOR THE TRANSFORMED PARAMETER -- conditional on the "
                "model that does the transforming, whose own error the interval does not cover."),
    },
    "observed_range": {
        "what_it_is": ("the minimum and maximum progression-free time OBSERVED among that cohort's "
                       "patients"),
        "may_be_propagated": True,
        "how": ("mapped the same way, and the result is a range of PER-PATIENT rates, NOT an "
                "uncertainty interval on the arm's median rate. ⛔ It must never be read as a "
                "confidence interval: an observed range widens with sample size where a "
                "confidence interval narrows, so the two move in OPPOSITE directions and quoting "
                "one as the other inverts what the number means."),
    },
    "none": {
        "what_it_is": "the source prints no interval, no range and no number at risk",
        "may_be_propagated": False,
        "how": ("nothing is propagated. The transformed point is emitted with `interval: null` and "
                "`propagated: false`. ⛔ A zero-width interval is NOT emitted, because "
                "`[x, x]` is indistinguishable in every downstream reading from a quantity "
                "measured to arbitrary precision."),
    },
}


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _dispersion_kind(row):
    """Classify an A5 row's dispersion WITHOUT trusting its prose label."""
    if row.get("median_pfs_ci95"):
        return "ci95"
    if row.get("median_pfs_observed_range"):
        return "observed_range"
    return "none"


def load_inputs():
    """Read the four EMC medians, their cohort records and their citations from the owner file."""
    src = json.load(open(SRC, encoding="utf-8"))
    a5 = src["analyses"]["A5_time_to_event_never_pooled"]

    # cohort key -> the record carrying its counts, provenance and quote. The four medians live in
    # two different lists in the source: three are pooled cohorts, and Chiusole is context-only
    # because its RESPONSE counts are percentages -- its MEDIAN is a separate object and is
    # EMC-specific, which is why it is in A5 at all.
    by_key = {}
    for c in src["cohorts"]:
        by_key[c["key"]] = ("cohorts", c)
    for c in src["context_only_no_extractable_counts"]:
        by_key[c["key"]] = ("context_only_no_extractable_counts", c)

    arms = []
    for row in a5["emc_specific_medians"]:
        where, coh = by_key[row["cohort"]]
        cite = src["citations"][coh["sourceId"]]
        kind = _dispersion_kind(row)
        interval = (row.get("median_pfs_ci95") if kind == "ci95"
                    else row.get("median_pfs_observed_range") if kind == "observed_range"
                    else None)
        arms.append({
            "arm": row["cohort"],
            "regimen": row["regimen"],
            "regimen_class": coh.get("regimen_class"),
            "median_pfs_months": row["median_pfs_months"],
            "dispersion": {
                "kind": kind,
                "interval_months": interval,
                "as_the_source_reports_it": row["dispersion_reported_as"],
                "may_be_propagated": DISPERSION_KINDS[kind]["may_be_propagated"],
            },
            "provenance_of_this_median": _median_provenance(row["cohort"], coh),
            "design_tier": coh.get("design_tier"),
            "n_started": coh.get("n_started"),
            "source": {
                "sourceId": coh["sourceId"],
                "short": cite.get("short"),
                "pmid": cite.get("pmid"),
                "pmcid": cite.get("pmcid"),
                "doi": cite.get("doi"),
                "year": cite.get("year"),
                "type": cite.get("type"),
                "read_from": f"{SRC_REL} -> {where}[{row['cohort']}] and analyses."
                             f"A5_time_to_event_never_pooled.emc_specific_medians",
            },
            "continuous_exposure_assumption": _exposure_note(coh.get("regimen_class")),
        })
    return src, a5, arms


def _median_provenance(key, coh):
    """⭐ THE FOUR MEDIANS DO NOT SHARE A PROVENANCE GRADE, AND THE TIGHTEST INTERVAL IS THE ONE
    READ OUT OF A REVIEW. Recorded per arm because flattening it is exactly the error this module
    exists to avoid: an interval's WIDTH and the standing of the document it was read from are
    independent, and only the width is visible in a plot."""
    if key == "pazopanib_phase2":
        return ("SECONDARY FOR THE MEDIAN. The cohort's response counts are primary (the trial "
                "report), but the source row states the median PFS of 19 months (95% CI 11-27) is "
                "read from the Remiszewski 2025 review's account of the same trial. The sibling "
                "model research/modalities/emc_adaptive_pazopanib.py records the same thing "
                "independently: the primary abstract does not state a median PFS.")
    if key == "sunitinib_nivolumab_immunosarc2":
        return ("PRIMARY BUT CONFERENCE ABSTRACT ONLY. The median and its CI are quoted verbatim "
                "from the abstract; no full paper exists against which to check them, and the "
                "source row records two internal inconsistencies elsewhere in the same abstract.")
    if key == "anthracycline_italian_rcn":
        return ("PRIMARY. 'Median PFS was 8 (range 2-10) months' is quoted from the primary report "
                "(Clin Sarcoma Res 2013;3:16), which the source row resolved from a review's "
                "free-text reference and confirmed against the Europe PMC record.")
    if key == "chiusole_metastatic_chemo":
        return ("PRIMARY, FULL TEXT, VERIFIED THREE WAYS -- and with no dispersion of any kind. "
                "The source row records three independent HTTP 200 acquisitions of the sentence "
                "(Europe PMC full-text XML, PMC HTML, publisher landing page) under GitHub Actions "
                "run 31276131242. ⭐ This arm is therefore the BEST-VERIFIED median in the set and "
                "the ONE THAT CANNOT BE PROPAGATED. Verification standing and dispersion "
                "availability are orthogonal, and a model that ranks arms by interval width has "
                "silently ranked them by how their sources chose to typeset a result.")
    return "UNKNOWN"


def _exposure_note(regimen_class):
    """Whether 'continuous exposure until progression' is a fair reading of the arm."""
    if regimen_class == "cytotoxic chemotherapy":
        return ("APPROXIMATE. The calibration below reads the median as time under continuous drug "
                "exposure ending at progression. Cytotoxic chemotherapy is given for a bounded "
                "number of cycles, so part of this arm's progression-free time is OFF treatment "
                "and the fitted rate is a blend of on- and off-treatment growth. Recorded per arm "
                "rather than corrected; it is one more reason the four arms are not comparable.")
    return ("FAIR. Continuously dosed oral agents taken until progression, which is what the "
            "calibration assumes.")


# ---------------------------------------------------------------------------
# 2 - L1: the analytic bound, and interval propagation BY KIND
# ---------------------------------------------------------------------------

def _rate_from_time(months, theta):
    """Net exponential growth rate (per month) implied by progression at `months`."""
    return math.log(theta) / months


def l1_calibration(arms):
    """Per arm, per convention: the bound the median places on the progressing compartment.

    r_R >= ln(theta)/T_median, because T_median = t_nadir + ln(theta)/r_R and t_nadir >= 0.
    Equivalently the compartment's volume doubling time is at most T_median * ln2/ln(theta).
    """
    out = []
    for a in arms:
        kind = a["dispersion"]["kind"]
        rec = {
            "arm": a["arm"],
            "median_pfs_months": a["median_pfs_months"],
            "dispersion_kind": kind,
            "by_convention": {},
        }
        for cname, theta in THETA_CONVENTIONS.items():
            point = _rate_from_time(a["median_pfs_months"], theta)
            entry = {
                "progression_threshold_burden_ratio": round(theta, 6),
                "resistant_compartment_growth_rate_lower_bound_per_month": round(point, 6),
                "equivalent_doubling_time_upper_bound_months": round(math.log(2.0) / point, 3),
                "why_a_bound_and_not_an_estimate": (
                    "the median covers time to nadir PLUS the regrowth phase; only the regrowth "
                    "phase is exponential at r_R, so any non-zero time to nadir makes the true "
                    "r_R larger than this. New-lesion progression, which the model cannot "
                    "represent, pushes the same way."),
            }
            if kind == "ci95":
                lo_t, hi_t = a["dispersion"]["interval_months"]
                entry["interval"] = {
                    "kind": "ci95",
                    "propagated": True,
                    "growth_rate_bound_per_month": [round(_rate_from_time(hi_t, theta), 6),
                                                    round(_rate_from_time(lo_t, theta), 6)],
                    "doubling_time_bound_months": [
                        round(math.log(2.0) / _rate_from_time(lo_t, theta), 3),
                        round(math.log(2.0) / _rate_from_time(hi_t, theta), 3)],
                    "reading": ("a 95% interval for the transformed parameter, by equivariance of "
                                "a monotone reparameterisation. It covers the sampling error in "
                                "the median and NOTHING about the model that transformed it."),
                }
            elif kind == "observed_range":
                lo_t, hi_t = a["dispersion"]["interval_months"]
                entry["interval"] = {
                    "kind": "observed_range",
                    "propagated": True,
                    "growth_rate_bound_per_month": [round(_rate_from_time(hi_t, theta), 6),
                                                    round(_rate_from_time(lo_t, theta), 6)],
                    "doubling_time_bound_months": [
                        round(math.log(2.0) / _rate_from_time(lo_t, theta), 3),
                        round(math.log(2.0) / _rate_from_time(hi_t, theta), 3)],
                    "reading": ("⛔ NOT A CONFIDENCE INTERVAL. This is the spread of the "
                               "cohort's own observed progression-free times, re-expressed as "
                               "rates. It describes between-patient variation, widens with "
                               "cohort size, and may not be compared with the two CI arms above "
                               "as though it were the same object."),
                }
            else:
                entry["interval"] = {
                    "kind": "none",
                    "propagated": False,
                    "growth_rate_bound_per_month": None,
                    "doubling_time_bound_months": None,
                    "reading": ("the source prints no interval, no range and no number at risk, so "
                                "no interval exists to propagate and none is manufactured. ⛔ The "
                                "uncertainty on this arm is UNKNOWN, which is not the same as "
                                "small, and `[9.0, 9.0]` is never emitted."),
                }
            rec["by_convention"][cname] = entry
        out.append(rec)
    return out


def convention_vs_data(arms, l1):
    """Is the modelling convention worth more or less than the spread of the data it is applied to?

    Both numbers are DERIVED here, never typed: the convention factor from the two thetas, the data
    spread from the four medians as read out of the source artifact.
    """
    thetas = list(THETA_CONVENTIONS.values())
    conv = math.log(max(thetas)) / math.log(min(thetas))
    meds = [a["median_pfs_months"] for a in arms]
    data = max(meds) / min(meds)
    return {
        "convention_factor_on_every_rate": round(conv, 4),
        "how_it_arises": ("ln(theta_volume)/ln(theta_diameter). Every rate this file computes is "
                          "proportional to ln(theta), so switching burden-unit convention "
                          "multiplies all of them by exactly this."),
        "spread_of_the_four_medians_max_over_min": round(data, 4),
        "median_months_used": sorted(meds),
        "verdict": (
            "THE UNDECLARED MODELLING CHOICE MOVES THE CALIBRATED PARAMETER FURTHER THAN THE FOUR "
            "COHORTS DIFFER FROM EACH OTHER." if conv > data else
            "The four cohorts differ from each other by more than the burden-unit convention "
            "moves the calibrated parameter."),
        "so_what": ("a reader comparing a rate from this model against a rate from any other "
                    "model must check the burden-unit convention FIRST, because it dominates every "
                    "between-arm difference available in this disease's published record. Neither "
                    "convention is 'correct'; both are reported for every arm and neither is "
                    "nominated as the default."),
    }


# ---------------------------------------------------------------------------
# 3 - L2: the two-population model, fitted to each median separately
# ---------------------------------------------------------------------------
#
# dS/dt = r_S S (1 - (S+R)) - delta u(t) S
# dR/dt = r_R R (1 - (S+R))
# Symmetric competition, carrying capacity normalised to 1, drug acts only on S. Same structural
# form as research/modalities/emc-adaptive-pazopanib.json -> competition_model.form, chosen so the
# two models are comparable rather than because any EMC datum supports it.
#
# ⛔ ONE DELIBERATE DIFFERENCE FROM THE SIBLING MODEL, STATED RATHER THAN SLIPPED IN: progression
# here is measured from the NADIR, which is the RECIST 1.1 definition. The sibling measures it from
# the BASELINE burden. Under continuous dosing that makes the sibling's time to progression the
# longer of the two whenever the drug produces any depth of response at all. Both are reported for
# one reference point in `nadir_vs_baseline_rule` so the difference is visible rather than argued.

DT_DAYS = 1.0
HORIZON_DAYS = 365.25 * 25
F0_GRID = [1e-4, 1e-3, 1e-2, 0.05, 0.20]
COST_GRID = [0.0, 0.30]
DELTA_OVER_RS = 3.0
N0_FRAC = 0.5
ADAPTIVE_WITHDRAW_FRACTION = 0.5   # Gatenby-style: stop drug when burden reaches this x baseline


def simulate(r_r_per_day, cost, f0, theta, adaptive=False, from_nadir=True,
             dt=DT_DAYS, horizon=HORIZON_DAYS):
    """Integrate the two-population system; return time to progression in days.

    r_S is derived from r_R and the fitness cost (r_R = r_S (1-cost)), so the FITTED quantity is the
    resistant compartment's growth rate -- the one an observed time to progression can speak to.
    """
    r_s = r_r_per_day / (1.0 - cost) if cost < 1.0 else r_r_per_day
    delta = DELTA_OVER_RS * r_s
    n0 = N0_FRAC
    s = n0 * (1.0 - f0)
    r = n0 * f0
    u = 1.0
    t = 0.0
    nadir = n0
    steps = int(horizon / dt)
    for _ in range(steps):
        n = s + r
        if n < nadir:
            nadir = n
        ref = nadir if from_nadir else n0
        if n >= ref * theta and t > 0.0:
            return t, False
        if adaptive:
            if u > 0.5 and n <= ADAPTIVE_WITHDRAW_FRACTION * n0:
                u = 0.0
            elif u < 0.5 and n >= n0:
                u = 1.0
        space = 1.0 - n
        ds = r_s * s * space - delta * u * s
        dr = r_r_per_day * r * space
        s = max(0.0, s + dt * ds)
        r = max(0.0, r + dt * dr)
        t += dt
    return horizon, True


def fit_r_r(target_months, cost, f0, theta):
    """Bisect r_R so the simulated time to progression equals this arm's median."""
    target_days = target_months * DAYS_PER_MONTH
    lo, hi = 1e-6, 1.0          # per day
    # time to progression is monotone DECREASING in r_R
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        ttp, censored = simulate(mid, cost, f0, theta)
        if censored or ttp > target_days:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-9:
            break
    return 0.5 * (lo + hi)


def _spread(vals):
    lo, hi = min(vals), max(vals)
    return {"min": round(lo, 6), "max": round(hi, 6),
            "max_over_min": round(hi / lo, 4) if lo > 0 else None}


def l2_fits(arms):
    """For each arm, fit r_R across the grid of parameters no EMC series reports.

    The adaptive-versus-continuous ratio is computed TWICE, under the two progression rules, because
    the choice of rule turns out to decide its sign -- see `adaptive_rule_vs_recist`.
    """
    out = []
    for a in arms:
        rec = {"arm": a["arm"], "median_pfs_months": a["median_pfs_months"], "by_convention": {}}
        for cname, theta in THETA_CONVENTIONS.items():
            grid = []
            for f0 in F0_GRID:
                for cost in COST_GRID:
                    r_r = fit_r_r(a["median_pfs_months"], cost, f0, theta)
                    ttp_mtd, cens_m = simulate(r_r, cost, f0, theta, adaptive=False)
                    ttp_ada, cens_a = simulate(r_r, cost, f0, theta, adaptive=True)
                    b_mtd, bc_m = simulate(r_r, cost, f0, theta, adaptive=False, from_nadir=False)
                    b_ada, bc_a = simulate(r_r, cost, f0, theta, adaptive=True, from_nadir=False)
                    grid.append({
                        "initial_resistant_fraction": f0,
                        "resistance_cost": cost,
                        "fitted_r_R_per_month": round(r_r * DAYS_PER_MONTH, 6),
                        "fitted_doubling_time_months": round(
                            math.log(2.0) / (r_r * DAYS_PER_MONTH), 3),
                        "reproduced_ttp_months": round(ttp_mtd / DAYS_PER_MONTH, 3),
                        "adaptive_ratio_nadir_rule": (None if (cens_m or cens_a)
                                                      else round(ttp_ada / ttp_mtd, 4)),
                        "adaptive_ratio_baseline_rule": (None if (bc_m or bc_a)
                                                         else round(b_ada / b_mtd, 4)),
                        "censored_nadir_rule": bool(cens_m or cens_a),
                        "censored_baseline_rule": bool(bc_m or bc_a),
                    })
            fitted = [g["fitted_r_R_per_month"] for g in grid]
            nad = [g["adaptive_ratio_nadir_rule"] for g in grid
                   if g["adaptive_ratio_nadir_rule"] is not None]
            base = [g["adaptive_ratio_baseline_rule"] for g in grid
                    if g["adaptive_ratio_baseline_rule"] is not None]
            rec["by_convention"][cname] = {
                "grid": grid,
                "fitted_r_R_spread_over_the_whole_grid": _spread(fitted),
                "adaptive_ratio_spread_nadir_rule": _spread(nad) if nad else None,
                "adaptive_ratio_spread_baseline_rule": _spread(base) if base else None,
                "l1_analytic_bound_per_month": round(
                    _rate_from_time(a["median_pfs_months"], theta), 6),
                "l1_bound_is_below_every_fitted_value": all(
                    v >= round(_rate_from_time(a["median_pfs_months"], theta), 6) for v in fitted),
            }
        out.append(rec)
    return out


def verification(arms, l1, l2):
    """Two checks a reader should not have to run by hand, computed rather than asserted.

    (1) Does the numerical fit reproduce the median it was fitted to? The bound is one integration
        step; anything larger means the bisection did not converge.
    (2) Does the analytic L1 bound sit below every numerically fitted rate, as its derivation says
        it must? The two layers are independent -- one is a closed form, one is an ODE integration
        with a nadir-tracking progression rule -- so agreement is a real cross-check and a
        violation would mean one of them is wrong.
    (3) Is a zero-width interval emitted anywhere? It must never be.
    """
    errs, bound_ok = [], True
    for arm_fit, arm in zip(l2, arms):
        for cname in THETA_CONVENTIONS:
            blk = arm_fit["by_convention"][cname]
            bound_ok = bound_ok and blk["l1_bound_is_below_every_fitted_value"]
            for g in blk["grid"]:
                errs.append(abs(g["reproduced_ttp_months"] - arm["median_pfs_months"]))
    step_months = DT_DAYS / DAYS_PER_MONTH
    zero_width = []
    for rec in l1:
        for cname, entry in rec["by_convention"].items():
            iv = entry["interval"]["growth_rate_bound_per_month"]
            if iv is not None and iv[0] == iv[1]:
                zero_width.append(f"{rec['arm']}/{cname}")
    return {
        "n_grid_cells_checked": len(errs),
        "worst_ttp_reproduction_error_months": round(max(errs), 6),
        "one_integration_step_months": round(step_months, 6),
        "fit_converged_within_one_step_everywhere": bool(max(errs) <= step_months + 1e-9),
        "analytic_bound_below_every_numerical_fit": bool(bound_ok),
        "why_that_check_matters": (
            "the closed form and the ODE integration are independent implementations of the same "
            "claim. The derivation says the analytic value is a LOWER bound on the fitted rate, "
            "because the median covers time to nadir as well as the regrowth phase. If a fitted "
            "value ever fell below it, one of the two would be wrong and this file would not know "
            "which."),
        "zero_width_intervals_emitted": zero_width,
        "no_zero_width_interval_emitted": not zero_width,
    }


def adaptive_rule_vs_recist(l2):
    """⛔ A RESULT NOBODY WAS LOOKING FOR, AND IT IS EXACT RATHER THAN NUMERICAL.

    A Gatenby-style adaptive schedule withdraws drug when burden falls to a fixed fraction of
    baseline. That withdrawal DEFINES a nadir. If the burden is then allowed to recover toward
    baseline, the ratio to that nadir reaches 1/fraction -- and RECIST 1.1 calls progression at a
    much smaller ratio. So under a nadir-referenced progression endpoint the schedule's own rule
    manufactures the progression event, before any of the biology the schedule exists to exploit
    can express itself.
    """
    rebound = 1.0 / ADAPTIVE_WITHDRAW_FRACTION
    worst_theta = max(THETA_CONVENTIONS.values())
    nad, base = [], []
    for arm in l2:
        for cname in THETA_CONVENTIONS:
            blk = arm["by_convention"][cname]
            nad += [g["adaptive_ratio_nadir_rule"] for g in blk["grid"]
                    if g["adaptive_ratio_nadir_rule"] is not None]
            base += [g["adaptive_ratio_baseline_rule"] for g in blk["grid"]
                     if g["adaptive_ratio_baseline_rule"] is not None]
    return {
        "the_exact_argument": (
            "the withdrawal trigger is burden <= {} x baseline, so the burden at withdrawal IS the "
            "nadir. Full recovery to baseline is a ratio of {} above that nadir. The largest "
            "progression threshold either burden-unit convention uses is {}. {} > {}, so the "
            "recovery phase crosses the progression threshold BY CONSTRUCTION, under both "
            "conventions, for every parameter value."
            .format(ADAPTIVE_WITHDRAW_FRACTION, round(rebound, 4), round(worst_theta, 4),
                    round(rebound, 4), round(worst_theta, 4))),
        "measured_consequence": {
            "adaptive_over_continuous_nadir_rule": _spread(nad) if nad else None,
            "adaptive_over_continuous_baseline_rule": _spread(base) if base else None,
            "n_grid_cells": len(nad),
            "cells_where_adaptive_is_longer_nadir_rule": sum(1 for v in nad if v > 1.0),
            "cells_where_adaptive_is_longer_baseline_rule": sum(1 for v in base if v > 1.0),
        },
        "what_this_is_and_is_not": (
            "It is a statement about two DEFINITIONS -- a withdrawal rule and an endpoint -- and it "
            "holds whatever the biology is. ⛔ It is NOT evidence that adaptive scheduling would "
            "shorten anyone's disease control: an endpoint that fires on a planned, reversible "
            "rebound is measuring the schedule rather than the disease. ⛔ It is also NOT a defect "
            "found in the sibling model research/modalities/emc-adaptive-pazopanib.json, which "
            "measures progression from BASELINE; under that rule the same grid gives ratios above "
            "1, which is why the rule choice is reported here as a first-class result instead of "
            "being fixed silently in one direction."),
        "the_open_question_this_raises": (
            "which progression definition an adaptive-schedule study in a solid tumour should use, "
            "and whether a burden-fraction withdrawal rule and a nadir-referenced endpoint can "
            "coexist at all. ⛔ NOT ANSWERED HERE, and deliberately not asserted about field "
            "practice: no survey of how adaptive-therapy trials define progression has been done "
            "in this repository, and a claim about what other groups routinely do needs one."),
    }


def what_moves_the_answer(arms, l2):
    """⭐ THE RESULT, AND IT REFUTES THE HYPOTHESIS THIS MODULE WAS BUILT ON.

    The prior hypothesis was: under continuous dosing the sensitive compartment is suppressed early,
    so an observed median is close to a direct read-out of the RESISTANT compartment's growth rate
    and says nothing about its SIZE. If true, the four medians would pin the rate cleanly and leave
    the adaptive question -- which the sibling model found runs on the initial resistant fraction --
    untouched. THE GRID DOES NOT SUPPORT IT, and the measurement is below.
    """
    factors = []

    # (a) the burden-unit convention, exact
    thetas = list(THETA_CONVENTIONS.values())
    factors.append({
        "degree_of_freedom": "burden-unit convention (RECIST diameters vs spherical volumes)",
        "who_chooses_it": "the modeller, and it is usually not stated",
        "measured_or_exact": "exact",
        "factor_on_the_calibrated_rate": round(math.log(max(thetas)) / math.log(min(thetas)), 4),
    })

    # (b) the initial resistant fraction, and (c) the fitness cost -- both measured over the grid
    f0_ratios, cost_ratios = [], []
    for arm in l2:
        for cname in THETA_CONVENTIONS:
            g = arm["by_convention"][cname]["grid"]
            for cost in COST_GRID:
                v = [c["fitted_r_R_per_month"] for c in g if c["resistance_cost"] == cost]
                if len(v) > 1:
                    f0_ratios.append(max(v) / min(v))
            for f0 in F0_GRID:
                v = [c["fitted_r_R_per_month"] for c in g
                     if c["initial_resistant_fraction"] == f0]
                if len(v) > 1:
                    cost_ratios.append(max(v) / min(v))
    factors.append({
        "degree_of_freedom": ("initial resistant fraction f0, swept over {} decades "
                              "({} to {})".format(
                                  round(math.log10(max(F0_GRID) / min(F0_GRID)), 2),
                                  min(F0_GRID), max(F0_GRID))),
        "who_chooses_it": "nobody -- it is unmeasured in EMC and no published series reports it",
        "measured_or_exact": "measured over the grid",
        "factor_on_the_calibrated_rate": round(max(f0_ratios), 4),
    })
    factors.append({
        "degree_of_freedom": "fitness cost of resistance, {} to {}".format(min(COST_GRID),
                                                                          max(COST_GRID)),
        "who_chooses_it": "nobody -- unmeasured in EMC",
        "measured_or_exact": "measured over the grid",
        "factor_on_the_calibrated_rate": round(max(cost_ratios), 4),
    })

    meds = [a["median_pfs_months"] for a in arms]
    data_factor = max(meds) / min(meds)
    factors.append({
        "degree_of_freedom": ("THE DATA: the spread of the four published EMC medians "
                              "themselves, {} to {} months".format(min(meds), max(meds))),
        "who_chooses_it": "the published record",
        "measured_or_exact": "exact, from the four medians as read from the owner artifact",
        "factor_on_the_calibrated_rate": round(data_factor, 4),
    })

    beat_data = [f for f in factors
                 if f["factor_on_the_calibrated_rate"] >= data_factor
                 and not f["degree_of_freedom"].startswith("THE DATA")]

    return {
        "the_question": ("A two-population model has five free parameters and a median is one "
                         "constraint. What actually moves the number you get out -- the data, or "
                         "the choices nobody declared?"),
        "free_parameters_in_the_model": {
            "count": 5,
            "names": ["r_S", "r_R", "delta (drug kill rate)", "f0 (initial resistant fraction)",
                      "N0 (initial burden relative to carrying capacity)"],
            "constraints_available": len(arms),
            "and_they_do_not_stack": ("the four medians constrain FOUR DIFFERENT COHORTS on FOUR "
                                      "DIFFERENT REGIMENS. They are four one-constraint problems, "
                                      "not one four-constraint problem, and POLICY-evidence s2.4 "
                                      "is what forbids treating them as the latter. Even taken "
                                      "together they are four constraints on five parameters, and "
                                      "the shortfall is not the point -- the point is the table "
                                      "below."),
        },
        "ranked": sorted(factors, key=lambda f: -f["factor_on_the_calibrated_rate"]),
        "n_undeclared_or_unmeasured_choices_that_move_it_at_least_as_much_as_the_data":
            len(beat_data),
        "verdict": (
            "{} of the three modelling degrees of freedom move the calibrated growth rate at least "
            "as far as the entire spread between the four published EMC cohorts does ({}x). The "
            "model does not see through its own assumptions to the data: a rate quoted from it "
            "without its burden-unit convention and its assumed resistant fraction is not a "
            "quantity at all."
            .format(len(beat_data), round(data_factor, 4))),
        "⛔_the_hypothesis_this_refutes_is_the_one_this_module_was_built_on": (
            "The prior expectation was that under continuous dosing the sensitive compartment is "
            "suppressed early, so a median would read out the resistant compartment's growth RATE "
            "cleanly and carry no information about its SIZE. That would have been a tidy result: "
            "the medians pin the parameter the adaptive question does not turn on. THE GRID DOES "
            "NOT SHOW IT. Sweeping f0 over the grid changes the rate fitted to the SAME median by "
            "up to {}x, because at the modelled initial burden ({} of carrying capacity) logistic "
            "saturation and the depth of the nadir both depend on f0. The medians do not cleanly "
            "identify anything."
            .format(round(max(f0_ratios), 3), N0_FRAC)),
        "what_that_costs_the_route": (
            "calibrating to all four medians does not make a scheduling prediction identifiable, "
            "and adding a fifth median would not either. ⛔ This is a statement about "
            "identifiability, not about whether any schedule would help any patient; the model "
            "makes no such claim in either direction."),
        "what_would_change_it": (
            "not more medians. Serial imaging with per-lesion volumes, or a circulating-tumour-DNA "
            "series through a treatment interruption, would speak to the resistant fraction and to "
            "the burden trajectory directly, and the burden-unit convention stops mattering the "
            "moment volumes rather than diameter sums are the measured quantity. Under "
            "POLICY-evidence s2.7 a Kaplan-Meier curve WITH its numbers-at-risk table can be "
            "inverted to patient-level times, which adds censoring structure and would let these "
            "arms be modelled as distributions rather than as their medians -- but it recovers "
            "times and events and never the resistant fraction, so it does not close this gap "
            "either. research/modalities/emc_ipd_survival.py holds that instrument with an "
            "empty CURVES table."),
    }


def nadir_vs_baseline_rule(arms):
    """Show the progression-rule difference against the sibling model rather than arguing it."""
    a = arms[0]
    theta = THETA_CONVENTIONS["diameter_1.20"]
    r_r = fit_r_r(a["median_pfs_months"], 0.0, 1e-3, theta)
    t_nadir, _ = simulate(r_r, 0.0, 1e-3, theta, from_nadir=True)
    t_base, cens = simulate(r_r, 0.0, 1e-3, theta, from_nadir=False)
    return {
        "reference_arm": a["arm"],
        "convention": "diameter_1.20",
        "fitted_r_R_per_month": round(r_r * DAYS_PER_MONTH, 6),
        "ttp_months_nadir_rule_recist_1_1": round(t_nadir / DAYS_PER_MONTH, 3),
        "ttp_months_baseline_rule": (None if cens else round(t_base / DAYS_PER_MONTH, 3)),
        "baseline_rule_censored_at_horizon": bool(cens),
        "why_this_is_here": (
            "RECIST 1.1 measures progression from the NADIR and this module does the same. The "
            "sibling model research/modalities/emc_adaptive_pazopanib.py measures it from the "
            "BASELINE burden. The two rules are not equivalent whenever the drug produces any "
            "depth of response, and the gap is shown here at one fitted point instead of being "
            "asserted. ⛔ This is a difference in convention, not a defect found in that model, "
            "whose outputs are all dimensionless ratios in which a common rule largely cancels."),
    }


# ---------------------------------------------------------------------------
# 4 - the misattributed figures, which stand on their own
# ---------------------------------------------------------------------------

def misattributed(a5):
    """Read the roster from the owner file and DERIVE its counts rather than typing them."""
    rows = a5["figures_that_are_NOT_emc_medians_but_circulate_as_such"]
    # A figure quoted in months is a median PFS figure; the one quoted as a percentage at a fixed
    # timepoint is a RATE. The route's grade says "four PFS figures"; the roster has five entries.
    # Both are right, and the discriminator is the unit, so it is computed here.
    months = [r for r in rows if r["figure"].strip().endswith("months")]
    other = [r for r in rows if r not in months]
    return {
        "why_this_block_is_here": (
            "RT-SCHEDULING's second claim does not depend on the model at all. It survives whatever "
            "the model does, and it is the finding with the shortest path to a reader."),
        "owner": f"{SRC_REL} -> analyses.A5_time_to_event_never_pooled."
                 f"figures_that_are_NOT_emc_medians_but_circulate_as_such",
        "n_entries_in_the_roster": len(rows),
        "n_that_are_time_valued_pfs_figures": len(months),
        "n_that_are_rates_not_medians": len(other),
        "reconciliation": (
            "the roster holds {} entries and the route's grade says FOUR misattributed PFS "
            "figures. Both are correct: {} of the entries are quoted in MONTHS and are median-PFS "
            "figures, and {} is a PERCENTAGE at a fixed timepoint, which is a progression-free "
            "RATE and a different object. The count is derived here from the unit rather than "
            "carried as a number, so it cannot drift from its own roster."
            .format(len(rows), len(months), len(other))),
        "time_valued": months,
        "rate_valued": other,
        "the_one_that_is_categorically_different": (
            "'8.5 months' attributed to sunitinib in EMC is that series' median FOLLOW-UP, from a "
            "paper whose own text says median progression-free survival was NOT REACHED. A median "
            "follow-up and a median PFS are not the same quantity measured differently; a "
            "not-reached median is a NON-NUMBER, and substituting an available number for it "
            "converts an absence of evidence into a value. POLICY-evidence s2.7(e) names exactly "
            "this by requiring 'not reached' be preserved as a non-number."),
        "not_checked": (
            "whether any of these figures has propagated into treatment guidance, a guideline or a "
            "trial design. RT-SCHEDULING's own remaining_unknowns names that check as the thing "
            "that would raise this finding's weight considerably, and it has not been done here."),
    }


# ---------------------------------------------------------------------------
# 5 - build
# ---------------------------------------------------------------------------

def build():
    src, a5, arms = load_inputs()
    l1 = l1_calibration(arms)
    l2 = l2_fits(arms)
    kinds = sorted({a["dispersion"]["kind"] for a in arms})
    n_propagable = sum(1 for a in arms if a["dispersion"]["may_be_propagated"])
    return {
        "_schema": "emc-scheduling-medians/1",
        "_generated_by": "research/modalities/emc_scheduling_medians.py",
        "_do_not_hand_edit": (
            "Every median, interval, quote, citation and count here is read at run time from "
            f"{SRC_REL} and recomputed by the generator. To change an input, change it in that "
            "file and regenerate; a hand edit will be silently overwritten and will not carry the "
            "provenance the number arrived with."),
        "_input_artifact": {
            "path": SRC_REL,
            "sha256": _sha256(SRC),
            "why_the_digest_is_here": (
                "so a reader can prove which bytes these four medians came from without "
                "re-deriving them, and so a change to the owner file is a byte comparison rather "
                "than an argument."),
        },
        "title": ("The two-population scheduling model for extraskeletal myxoid chondrosarcoma, "
                  "calibrated to four medians carried separately - one of which has no dispersion "
                  "at all"),
        "route": "RT-SCHEDULING",
        "ledger_item": "AUT-060",

        "what_this_is_not": {
            "not_a_pool": ("no quantity here combines two arms. POLICY-evidence s2.4 never merges "
                           "time-anchored endpoints and the owner artifact refuses the "
                           "neighbouring pool explicitly (analyses.A7_the_pool_that_is_refused)."),
            "not_a_ranking": ("the four arms are different regimens, different lines, different "
                              "eras, different countries and two different response-assessment "
                              "standards. They are printed in the order the owner file prints "
                              "them and no ordering is implied."),
            "not_a_test": ("no test statistic and no p-value is computed anywhere in this file, "
                           "for the reasons the owner artifact already states."),
            "not_a_prediction": ("no progression-free survival is emitted for any schedule, "
                                 "adaptive or continuous. Every rate parameter of this model is "
                                 "unmeasured in EMC in vivo, so a number with a time unit on it "
                                 "would be a simulation output wearing clinical clothes."),
            "asserts_nothing_about_any_drug": (
                "no efficacy, comparative-effectiveness, safety, therapeutic-window or "
                "clinical-readiness statement is made about pazopanib, sunitinib, nivolumab, "
                "anthracyclines, ifosfamide, trabectedin, apatinib or any other agent, and no "
                "treatment recommendation of any kind, including a negative one. Adaptive "
                "scheduling has never been tested in EMC or in any sarcoma."),
        },

        "method": {
            "policy": "systems/POLICY-evidence.md s2.4 (time-to-event carried per row, never "
                      "merged) and s2.6(f) (a median-to-rate conversion is a labelled DISPLAY "
                      "quantity and may never be an input to a summary).",
            "s2_6f_compliance": (
                "every rate in this file is a per-arm display quantity. No summary anywhere in the "
                "output takes a rate as an input: the only cross-arm objects computed are (a) the "
                "max/min ratio of the four MEDIANS in `convention_vs_data`, which is a ratio of "
                "the published times themselves, and (b) worst-case variation ratios in "
                "`identifiability`, which are properties of the MODEL's response to its own "
                "parameter grid and contain no patient data."),
            "model": ("two-population competitive Lotka-Volterra, carrying capacity normalised to "
                      "1, symmetric competition, drug acts only on the sensitive population - the "
                      "same structural form as research/modalities/emc-adaptive-pazopanib.json so "
                      "the two are comparable."),
            "progression_rule": ("RECIST 1.1 size criterion measured from the NADIR. New-lesion "
                                 "progression has no representation in a two-compartment burden "
                                 "model and is not modelled; it shortens real progression-free "
                                 "time relative to the model's."),
            "burden_unit_conventions": {k: round(v, 6) for k, v in THETA_CONVENTIONS.items()},
            "integrator": f"explicit Euler, dt = {DT_DAYS} day, horizon "
                          f"{round(HORIZON_DAYS / 365.25, 1)} years",
            "fit": "bisection on r_R to 1e-9/day against each arm's own median",
            "grid": {"initial_resistant_fraction": F0_GRID, "resistance_cost": COST_GRID,
                     "delta_over_r_S": DELTA_OVER_RS, "initial_burden_fraction_of_K": N0_FRAC},
            "scope_declared_up_front": (
                "deterministic integration, one progression rule, two burden conventions, one "
                "parameter grid. No bootstrap, no Monte Carlo, no replicate seeds, no reactive "
                "sensitivity layer. CLAUDE.md s5: run each test to its field standard and stop."),
            "identification_assumption": (
                "the observed MEDIAN of a cohort's progression-free times is identified with the "
                "single deterministic time to progression of one model trajectory. That is the "
                "standard median-calibration assumption and it is false in detail: the median of a "
                "distribution of times is not the time of the median parameter set. It is stated "
                "here rather than buried because it, and not the arithmetic, is the weakest joint "
                "in the chain."),
        },

        "the_parameterisation_this_file_exists_for": {
            "statement": ("four medians, four parameters, four intervals of THREE DIFFERENT KINDS, "
                          "and one arm with no interval at all."),
            "dispersion_kinds_present": kinds,
            "n_arms": len(arms),
            "n_arms_whose_interval_can_be_propagated": n_propagable,
            "n_arms_carried_as_a_point_with_no_width": len(arms) - n_propagable,
            "kind_definitions": DISPERSION_KINDS,
            "⛔_the_error_this_blocks": (
                "emitting [9.0, 9.0] for the Chiusole arm. A zero-width interval is "
                "indistinguishable downstream from a quantity measured to arbitrary precision, so "
                "the arm with the WEAKEST dispersion reporting would plot as the STRONGEST. The "
                "artifact emits null with a reason instead, at every level."),
            "⭐_and_the_inversion_worth_noticing": (
                "the arm with no dispersion is the best-verified median in the set - Chiusole's 9 "
                "months was re-acquired three independent ways at HTTP 200 after this repository "
                "had asserted, wrongly and twice, that the paper reported no median at all. The "
                "arm with the tightest interval, pazopanib's 19 months (95% CI 11-27), is read "
                "from a REVIEW's account of the trial rather than from the trial report. Interval "
                "width and evidentiary standing are orthogonal, and only the width is visible in a "
                "plot."),
        },

        "arms": arms,
        "L1_analytic_calibration": l1,
        "convention_vs_data": convention_vs_data(arms, l1),
        "L2_fitted_two_population_model": l2,
        "L3_what_moves_the_answer": what_moves_the_answer(arms, l2),
        "adaptive_rule_vs_recist": adaptive_rule_vs_recist(l2),
        "nadir_vs_baseline_rule": nadir_vs_baseline_rule(arms),
        "verification": verification(arms, l1, l2),
        "misattributed_figures": misattributed(a5),

        "what_this_lets_the_program_say": {
            "1_the_specification_is_now_executed_not_only_correct": (
                "RT-SCHEDULING's grade said the route's named input does not exist and that what "
                "does exist is 'exactly a parameters-as-intervals model with one parameter that "
                "has no interval at all'. That was a specification. This file is that model, and "
                "the parameterisation survives contact with the arithmetic: three kinds of "
                "dispersion coexist in one output and the fourth arm propagates nothing."),
            "2_a_bound_where_there_was_no_number": (
                "each arm's median bounds the growth rate of whatever compartment progressed, in "
                "months, per arm, with that arm's own interval of that arm's own kind. The "
                "repository previously held these four medians as literature figures and nothing "
                "downstream of them."),
            "3_the_modelling_choices_dominate_the_data": (
                "ranked in `L3_what_moves_the_answer`: the burden-unit convention and the "
                "unmeasured initial resistant fraction each move the calibrated rate at least as "
                "far as the entire spread between the four published cohorts. A rate quoted from a "
                "model of this disease without both of those stated is not a quantity. That is the "
                "headline, it is a negative, and it is reported at full strength."),
            "4_a_definitional_collision_nobody_had_noticed": (
                "a burden-fraction withdrawal rule and a nadir-referenced RECIST endpoint cannot "
                "coexist: the withdrawal defines the nadir and the planned rebound crosses the "
                "progression threshold by construction, under both burden conventions and at every "
                "parameter value (`adaptive_rule_vs_recist`, an exact argument rather than a "
                "numerical one). Any future adaptive-schedule proposal in this disease has to say "
                "what its progression endpoint is before it says anything else."),
            "5_the_misattributed_figures_stand_alone": (
                "they need no model, they are counted from their own roster by unit, and their "
                "weight is bounded by one check nobody has run - whether any of them reached "
                "treatment guidance."),
            "at_what_weight": (
                "MODEL OUTPUT ON PUBLISHED SUMMARY STATISTICS. Four single-arm cohorts, two of "
                "them retrospective, one median read from a review, one from a conference "
                "abstract, one with no dispersion at all, all identified with a deterministic "
                "trajectory under an assumption stated in `method.identification_assumption`. "
                "Nothing here is evidence about a patient. ⭐ The two findings that do NOT depend "
                "on the burden-unit convention are the strongest ones: the ranking in "
                "`L3_what_moves_the_answer` (the convention is one of the ranked rows, not an "
                "input to the ranking) and `adaptive_rule_vs_recist` (which holds under both "
                "conventions and at every parameter value). Every rate with a unit on it is "
                "convention-dependent and must be quoted with its convention or not at all."),
        },

        "not_a_recommendation": (
            "This is a model of published summary statistics and its own uncertainty. It is not "
            "clinical advice, it does not rank treatments, and it must not be read as endorsing or "
            "discouraging any therapy or any schedule. EMC care belongs with a specialist sarcoma "
            "centre."),
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
        print("emc_scheduling_medians: artifact matches")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote {OUT}")
    print("  arms and their dispersion kinds:")
    for arm in doc["arms"]:
        d = arm["dispersion"]
        iv = d["interval_months"]
        print(f"    {arm['arm']:<32} {arm['median_pfs_months']:>5} mo  "
              f"{d['kind']:<15} {iv if iv else 'NO INTERVAL - carried as a point'}")
    cv = doc["convention_vs_data"]
    print(f"  convention factor {cv['convention_factor_on_every_rate']} vs data spread "
          f"{cv['spread_of_the_four_medians_max_over_min']}")
    print("  what moves the calibrated rate (ranked):")
    for f in doc["L3_what_moves_the_answer"]["ranked"]:
        print(f"    {f['factor_on_the_calibrated_rate']:>7}x  {f['degree_of_freedom']}")
    ar = doc["adaptive_rule_vs_recist"]["measured_consequence"]
    print(f"  adaptive longer than continuous in {ar['cells_where_adaptive_is_longer_nadir_rule']}"
          f"/{ar['n_grid_cells']} cells under the RECIST nadir rule, "
          f"{ar['cells_where_adaptive_is_longer_baseline_rule']}/{ar['n_grid_cells']} under the "
          f"baseline rule")
    v = doc["verification"]
    print(f"  verification: {v['n_grid_cells_checked']} cells, worst fit error "
          f"{v['worst_ttp_reproduction_error_months']} mo (one step = "
          f"{v['one_integration_step_months']}), analytic bound below every fit = "
          f"{v['analytic_bound_below_every_numerical_fit']}, zero-width intervals = "
          f"{len(v['zero_width_intervals_emitted'])}")
    mis = doc["misattributed_figures"]
    print(f"  misattributed roster: {mis['n_entries_in_the_roster']} entries = "
          f"{mis['n_that_are_time_valued_pfs_figures']} median-PFS + "
          f"{mis['n_that_are_rates_not_medians']} rate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
