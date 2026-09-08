#!/usr/bin/env python3
"""S5 adapter: COHORT-SHAPE sensitivity of S4's density and extent findings.

Derived from S4's executed `sweep.py` (sha256 28aa8e7c1cf17278d935986c1d6b6d934feafd05a03e1fea743d4356d81fd47d);
the cell/arm machinery is reused verbatim, and only the outer loops change.

READ-ONLY with respect to the repository: `research/modalities` is added to sys.path and both
modules are IMPORTED unmodified. No guard is changed anywhere -- MAX_KM_DEVIATION and
REQUIRE_RISK_TABLE are imported, echoed, and used as they stand.

WHAT VARIES HERE, AND WHAT DOES NOT
  * VARIES: the cohort shape (where the censoring sits) -- the one axis S4 held fixed;
    and the rendering/reading SCENARIO (line width, gridlines, matcher tolerance).
  * DOES NOT VARY: the reconstruction algorithm, the acceptance thresholds, the renderer.

VOCABULARY (binding): every arm below is a FIXED PRESPECIFIED SCENARIO. `render_km` is
deterministic, so a repeated identical render is a deterministic repeat and carries no
information. Nothing here is a distribution, a replication, a draw, a variability estimate or a
confidence of any kind, and no statistic presupposing sampling is computed.

RANDOMNESS: none is consumed. `km_digitize._synthetic_cohort` constructs `_Rng(90210 + n)` but
never samples from it (`_ = rng`), and the two explicit cohorts are written out arithmetically.
=> DETERMINISTIC, NO SEED IS USED. This is asserted by re-deriving every cohort twice in-process
   and comparing canonical-JSON sha256 (`determinism_selfcheck` below).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time

REPO_MOD = "/home/user/Rare-cancers/research/modalities"
sys.path.insert(0, REPO_MOD)

import km_digitize as kd              # noqa: E402  -- imported unmodified from the repository
import emc_ipd_survival as ipd_mod    # noqa: E402

T_MAX = 180.0


def cohort_hash(cohort):
    blob = json.dumps(cohort, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def risk_table_from_times(cohort, times):
    """Number at risk == number whose observed time is >= t (km_digitize._cohort_to_figure_inputs)."""
    return [[t, sum(1 for r in cohort if r["time"] >= t)] for t in times]


# ---------------------------------------------------------------------------------------------
# COHORT SHAPES -- four, structurally distinct, all deterministic
# ---------------------------------------------------------------------------------------------
def cohort_emc_anchor():
    """S4's anchor: 59 patients, heavy TERMINAL censoring (5 patients sitting at t_max)."""
    return kd._emc_shaped_cohort()


def cohort_early_censoring():
    """Censoring sits EARLY; events run late. Same n (59) and same event count (18) as the anchor,
    so the shape -- not the size or the event total -- is what differs.

    Written out arithmetically: censor times are 2,4,...,82 (41 values, all < the first event at
    84); event times are 84,90,...,186 clipped to <= 178 by construction below. The last observed
    row is an EVENT here, unlike the anchor, and nothing sits at t_max.
    """
    censored = [float(2 * (i + 1)) for i in range(41)]              # 2 .. 82
    events = [float(84 + 5 * i) for i in range(18)]                 # 84 .. 169
    return ([{"time": t, "event": 1} for t in events]
            + [{"time": t, "event": 0} for t in censored])


def cohort_uniform_censoring():
    """km_digitize._synthetic_cohort(59, 0.30, 180.0) -- times spread across the axis and the
    event flag assigned by pre-sort index, so events and censorings INTERLEAVE across the whole
    follow-up instead of clustering at either end. Same n and ~same event fraction as the anchor.
    """
    return kd._synthetic_cohort(59, 0.30, T_MAX)


def cohort_low_event():
    """km_digitize._synthetic_cohort(59, 0.10, 180.0) -- the same spread of times with far fewer
    events (6 of 59). Tests whether the findings are about censoring placement or event scarcity.
    """
    return kd._synthetic_cohort(59, 0.10, T_MAX)


COHORTS = [
    ("emc_anchor__terminal_censoring", cohort_emc_anchor),
    ("early_censoring", cohort_early_censoring),
    ("uniform_censoring", cohort_uniform_censoring),
    ("low_event", cohort_low_event),
]

# ---------------------------------------------------------------------------------------------
# RENDER / READ SCENARIOS -- fixed, deterministic, Pillow-free
# `km_digitize.jpeg_roundtrip` (km_digitize.py:1495-1501) needs PIL, which is NOT installed
# (ModuleNotFoundError: No module named 'PIL'); no scenario here touches it.
# ---------------------------------------------------------------------------------------------
READ_SCENARIOS = [
    ("clean__strict_matcher", {}, {}),
    ("line_width_4__strict_matcher", {"line_width": 4}, {}),
    ("gridlines__strict_matcher", {"gridlines": True}, {}),
    ("clean__lenient_matcher_luma175", {}, {"max_luma": 175}),
]


def reconstruct_cell(digitized, risk_table, truth, label):
    """One reconstruction. A crash is a RESULT and is recorded, never dropped. (From S4.)"""
    curve = {"id": label, "source_id": "control", "endpoint": "os",
             "population": "synthetic control cohort", "time_unit": "months",
             "digitized": digitized, "risk_table": risk_table, "total_events": None,
             "digitized_by": "S5 adapter (fixed render scenario, risk table varied)"}
    t0 = time.time()
    try:
        rec = ipd_mod.reconstruct(curve)
        q = ipd_mod.assess_quality(curve, rec)
        med = ipd_mod._median_survival(ipd_mod.kaplan_meier(rec["ipd"]))
        out = {
            "n_reconstructed": rec["n_reconstructed"],
            "n_events": rec["n_events"],
            "n_censored": rec["n_censored"],
            "events_delta_vs_truth": rec["n_events"] - truth["n_events"],
            "censored_delta_vs_truth": rec["n_censored"] - truth["n_censored"],
            "median_survival": med,
            "median_delta_vs_truth": (None if med is None or truth["median_survival"] is None
                                      else round(med - truth["median_survival"], 3)),
            "internal_max_abs_km_deviation": rec["max_abs_km_deviation"],
            "admissible_under_the_floor": q["admissible"],
            "quality_failures": q["failures"],
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        out = {"error": f"{type(exc).__name__}: {exc}"}
    out["seconds"] = round(time.time() - t0, 3)
    return out


def uniform(n_rows, extent_frac):
    last = extent_frac * T_MAX
    if n_rows == 1:
        return [0.0]
    return [round(last * i / (n_rows - 1), 6) for i in range(n_rows)]


def determinism_selfcheck():
    """Re-derive every cohort a second time and compare canonical hashes. Deterministic
    construction is CLAIMED above; this measures it rather than asserting it."""
    out = {}
    for name, fn in COHORTS:
        out[name] = {"hash_first": cohort_hash(fn()), "hash_second": cohort_hash(fn())}
        out[name]["identical"] = out[name]["hash_first"] == out[name]["hash_second"]
    return out


def main():
    t_start = time.time()
    result = {
        "meta": {
            "what": "sensitivity of S4's density and extent findings across FIXED PRESPECIFIED "
                    "cohort shapes and FIXED render/read scenarios",
            "not_a_distribution": "render_km is deterministic; no scenario here is a draw, a "
                                  "replicate or a sample, and no sampling statistic is computed",
            "randomness": "DETERMINISTIC, NO SEED USED -- see determinism_selfcheck",
            "t_max": T_MAX,
            "MAX_KM_DEVIATION_as_imported": ipd_mod.MAX_KM_DEVIATION,
            "REQUIRE_RISK_TABLE_as_imported": ipd_mod.REQUIRE_RISK_TABLE,
            "pillow_available": False,
            "pillow_note": "PIL absent; km_digitize.jpeg_roundtrip (km_digitize.py:1495-1501) "
                           "unavailable and no scenario depends on it",
            "grid_density_rows_at_extent_0_933": [3, 5, 8, 13, 19],
            "grid_extent_at_rows_8": [0.25, 0.5, 0.75, 0.933, 1.0],
            "read_scenarios": [s[0] for s in READ_SCENARIOS],
            "determinism_selfcheck": determinism_selfcheck(),
        },
        "cohorts": [],
        "failures": [],
    }

    for cname, cfn in COHORTS:
        cohort = cfn()
        truth_steps, _, _censor = kd._cohort_to_figure_inputs(cohort, [0.0])
        truth = {
            "n_patients": len(cohort),
            "n_events": sum(1 for r in cohort if r["event"]),
            "n_censored": sum(1 for r in cohort if not r["event"]),
            "median_survival": ipd_mod._median_survival(ipd_mod.kaplan_meier(cohort)),
            "min_time": min(r["time"] for r in cohort),
            "max_time": max(r["time"] for r in cohort),
            "last_observation_is_event": max(cohort, key=lambda r: r["time"])["event"] == 1,
            "n_at_t_max": sum(1 for r in cohort if r["time"] >= T_MAX),
        }
        block = {"cohort": cname, "cohort_sha256": cohort_hash(cohort), "truth": truth,
                 "renders": {}, "cells": []}

        # --- the fixed render/read scenarios, each done ONCE per cohort -----------------------
        reads = {}
        for sname, rkw, mkw in READ_SCENARIOS:
            t0 = time.time()
            try:
                fig = kd.render_km(truth_steps, t_max=T_MAX, **rkw)
                read = kd.extract_series(fig.img, fig.calib, kd.dark_matcher(**mkw),
                                         series_label=sname)
                info = {"seconds": round(time.time() - t0, 3), "ok": read["ok"],
                        "refusal": read.get("refusal"), "error": None}
                if read["ok"]:
                    info["curve_error_vs_truth"] = kd.curve_error(read["digitized"],
                                                                  truth_steps, T_MAX)
                    info["digitized_sha256"] = hashlib.sha256(
                        json.dumps(read["digitized"], sort_keys=True).encode()).hexdigest()
                    info["n_digitized_points"] = len(read["digitized"])
                    reads[sname] = read["digitized"]
                else:
                    reads[sname] = None
                    result["failures"].append(
                        {"kind": "read_refusal", "cohort": cname, "scenario": sname,
                         "refusal": read.get("refusal")})
            except Exception as exc:  # noqa: BLE001 -- a crash is a RESULT
                info = {"seconds": round(time.time() - t0, 3), "ok": False,
                        "error": f"{type(exc).__name__}: {exc}"}
                reads[sname] = None
                result["failures"].append({"kind": "render_or_read_exception", "cohort": cname,
                                           "scenario": sname, "error": info["error"]})
            block["renders"][sname] = info

        digitized_exact = [[0.0, 1.0]] + [[t, s] for t, s in truth_steps]

        def run(axis, params, times):
            rt = risk_table_from_times(cohort, times)
            cell = {"axis": axis, **params,
                    "risk_times": [round(t, 4) for t in times], "risk_table": rt,
                    "n_rows": len(rt), "last_row_time": rt[-1][0],
                    "extent_fraction": round(rt[-1][0] / T_MAX, 4),
                    "exact_arm": reconstruct_cell(digitized_exact, rt, truth,
                                                  f"s5_exact::{cname}::{axis}::{params}"),
                    "read_arms": {}}
            for sname, _rkw, _mkw in READ_SCENARIOS:
                dg = reads.get(sname)
                if dg is None:
                    cell["read_arms"][sname] = {"error": "render/read unavailable; arm NOT RUN"}
                else:
                    cell["read_arms"][sname] = reconstruct_cell(
                        dg, rt, truth, f"s5_read::{cname}::{sname}::{axis}::{params}")
            block["cells"].append(cell)

        # AXIS 1 -- DENSITY at fixed extent 0.933 (S4's extent). Spacing moves with density at
        # fixed extent; that is not independently controllable and is stated, not hidden.
        for n in (3, 5, 8, 13, 19):
            run("density@extent0.933", {"rows": n}, uniform(n, 168.0 / T_MAX))

        # AXIS 2 -- EXTENT at fixed density 8 rows. Spacing moves with extent; density held.
        for e in (0.25, 0.5, 0.75, 0.933, 1.0):
            run("extent@rows8", {"extent": e}, uniform(8, e))

        result["cohorts"].append(block)

    result["meta"]["total_seconds"] = round(time.time() - t_start, 3)
    result["meta"]["n_cohorts"] = len(result["cohorts"])
    result["meta"]["n_cells"] = sum(len(b["cells"]) for b in result["cohorts"])
    result["meta"]["n_reconstructions"] = sum(
        len(b["cells"]) * (1 + len(READ_SCENARIOS)) for b in result["cohorts"])
    print(json.dumps(result, indent=1, sort_keys=False))


if __name__ == "__main__":
    main()
