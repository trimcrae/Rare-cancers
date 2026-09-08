#!/usr/bin/env python3
"""R1: row-count x last-risk-time crossing over the retained SYNTHETIC control cohort.

READ-ONLY with respect to every repository module. Nothing in research/modalities/ is edited;
km_digitize.py and emc_ipd_survival.py are IMPORTED from their repository paths and used as-is,
including MAX_KM_DEVIATION and REQUIRE_RISK_TABLE. The only capability this harness adds over
run_control() is supplying `risk_times` from outside, instead of the hard-coded local at
km_digitize.py:1429. Same cohort generator (_emc_shaped_cohort), same seedless deterministic
construction, same error measures.

Design is fixed in GRID-DEFINITION.md and is not chosen here:
  R  = printed row count, INCLUDING first and last rows, R >= 2
  L  = last printed risk time, ABSOLUTE, defined separately from R
  t_i = L * i / (R - 1), i = 0..R-1        (interior derived; spacing is a consequence)

Rendering is held FIXED at `clean`: the figure is rendered and read back exactly ONCE and every
cell reuses that reading. The printed risk table cannot change pixels, so one render IS the
fixed-render condition rather than an approximation of it. No degraded render is used anywhere.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time

REPO_MOD = "/home/user/Rare-cancers/research/modalities"
sys.path.insert(0, REPO_MOD)

import km_digitize as kd            # noqa: E402  (imported from the repository, unmodified)
import emc_ipd_survival as ipd_mod  # noqa: E402

T_MAX = 180.0
ROW_COUNTS = [2, 3, 4, 5, 6, 8, 10, 13, 19, 25]
LAST_TIMES = [45.0, 90.0, 135.0, 168.0, 180.0]
SENTINEL_TIMES = [0.0, 24.0, 48.0, 72.0, 96.0, 120.0, 144.0, 168.0]
SENTINEL_EXPECT = {"events_delta_vs_truth": 0,
                   "censored_delta_vs_truth": -7,
                   "internal_max_abs_km_deviation": 0.0009}


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def risk_times(rows: int, last: float) -> list[float]:
    """t_i = L*i/(R-1); first row 0, last row exactly L. R>=2 by definition of a table."""
    if rows < 2:
        raise ValueError("R < 2 is not a table")
    return [last * i / (rows - 1) for i in range(rows)]


def risk_table_from_times(cohort, times):
    """Generator's own definition, km_digitize.py:1290 -- #{r : r.time >= t}."""
    return [[t, sum(1 for r in cohort if r["time"] >= t)] for t in times]


def reconstruct_cell(digitized, risk_table, truth, label):
    curve = {"id": label, "source_id": "control", "endpoint": "os",
             "population": "synthetic control cohort", "time_unit": "months",
             "digitized": digitized, "risk_table": risk_table, "total_events": None,
             "digitized_by": "R1 harness (fixed clean render; risk table varied)"}
    t0 = time.time()
    try:
        rec = ipd_mod.reconstruct(curve)
        q = ipd_mod.assess_quality(curve, rec)
        med = ipd_mod._median_survival(ipd_mod.kaplan_meier(rec["ipd"]))
        out = {"n_reconstructed": rec["n_reconstructed"],
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
               "error": None}
    except Exception as exc:  # noqa: BLE001 -- a crash is a RESULT, recorded not dropped
        out = {"error": f"{type(exc).__name__}: {exc}"}
    out["seconds"] = round(time.time() - t0, 4)
    return out


def main() -> int:
    t_start = time.time()
    cohort = kd._emc_shaped_cohort()
    truth_steps, _, _ = kd._cohort_to_figure_inputs(cohort, [0.0])
    truth = {"n_patients": len(cohort),
             "n_events": sum(1 for r in cohort if r["event"]),
             "n_censored": sum(1 for r in cohort if not r["event"]),
             "median_survival": ipd_mod._median_survival(ipd_mod.kaplan_meier(cohort))}

    meta = {"design": "row count R x last risk time L, full crossing; see GRID-DEFINITION.md",
            "row_counts": ROW_COUNTS, "last_times": LAST_TIMES, "t_max": T_MAX,
            "cohort_sha256": sha(cohort), "n_cohort": len(cohort), "truth": truth,
            "MAX_KM_DEVIATION_as_imported": ipd_mod.MAX_KM_DEVIATION,
            "REQUIRE_RISK_TABLE_as_imported": ipd_mod.REQUIRE_RISK_TABLE,
            "km_digitize_file": kd.__file__, "emc_ipd_survival_file": ipd_mod.__file__}

    # ---- the fixed clean render, ONCE ----------------------------------------------------
    t0 = time.time()
    fig = kd.render_km(truth_steps, t_max=T_MAX)
    read = kd.extract_series(fig.img, fig.calib, kd.dark_matcher(), series_label="clean")
    meta["render_read_seconds"] = round(time.time() - t0, 4)
    meta["read_ok"] = read["ok"]
    meta["refusal"] = read.get("refusal")
    if read["ok"]:
        meta["curve_error_vs_truth"] = kd.curve_error(read["digitized"], truth_steps, T_MAX)
        meta["digitized_sha256"] = sha(read["digitized"])
        meta["n_digitized_points"] = len(read["digitized"])
    digitized_read = read.get("digitized")
    digitized_exact = [[0.0, 1.0]] + [[t, s] for t, s in truth_steps]

    cells = []

    def cell(block, rows, last, times=None, note=None):
        times = risk_times(rows, last) if times is None else times
        rt = risk_table_from_times(cohort, times)
        rec = {"block": block, "rows": rows, "last_time": last,
               "derived_spacing": round(last / (rows - 1), 6),
               "risk_times": [round(t, 6) for t in times], "risk_table": rt,
               "note": note,
               "exact_coordinate_arm": reconstruct_cell(digitized_exact, rt, truth,
                                                        f"r1_exact::R{rows}::L{last}"),
               "clean_render_arm": (reconstruct_cell(digitized_read, rt, truth,
                                                     f"r1_read::R{rows}::L{last}")
                                    if digitized_read is not None
                                    else {"error": "clean render REFUSED; arm not run"})}
        cells.append(rec)
        return rec

    # ---- SENTINEL FIRST, before any new result is computed --------------------------------
    sent_times = risk_times(8, 168.0)
    sentinel = {"derived_times": [round(t, 6) for t in sent_times],
                "expected_times": SENTINEL_TIMES,
                "times_match_exactly": [round(t, 9) for t in sent_times] == SENTINEL_TIMES,
                "expected_baseline": SENTINEL_EXPECT}
    s_cell = cell("SENTINEL", 8, 168.0, times=sent_times,
                  note="historical run_control() risk_times; must reproduce exact_coordinates_baseline")
    got = {k: s_cell["exact_coordinate_arm"].get(k) for k in SENTINEL_EXPECT}
    sentinel["observed_exact_arm"] = got
    sentinel["reproduces_committed_baseline"] = (got == SENTINEL_EXPECT
                                                 and sentinel["times_match_exactly"])
    meta["sentinel"] = sentinel

    # ---- rounding-trap probe: L = 168.0 (exact) vs L = 0.933*180 = 167.94 -----------------
    cell("ROUNDING_PROBE", 8, 167.94,
         note="0.933*t_max = 167.94 is NOT 168/180*t_max = 168.0; measured, not assumed")

    # ---- PRIMARY DESIGN: full R x L crossing ---------------------------------------------
    for rows in ROW_COUNTS:
        for last in LAST_TIMES:
            cell("crossing", rows, last)

    meta["n_cells"] = len(cells)
    meta["total_seconds"] = round(time.time() - t_start, 4)
    print(json.dumps({"meta": meta, "cells": cells}, indent=1, sort_keys=False))
    # exit code carries the sentinel verdict: 0 pass, 3 sentinel mismatch
    return 0 if sentinel["reproduces_committed_baseline"] else 3


if __name__ == "__main__":
    sys.exit(main())
