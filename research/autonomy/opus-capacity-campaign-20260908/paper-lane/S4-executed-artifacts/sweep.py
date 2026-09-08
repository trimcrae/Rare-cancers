#!/usr/bin/env python3
"""S4 adapter: density / extent / anchoring sweep over the SYNTHETIC control cohort.

READ-ONLY with respect to the repository. This file lives in /tmp/claude-0/s4/ and imports a
byte-identical COPY of research/modalities/km_digitize.py (sha256 verified by the caller).
No guard is changed anywhere: MAX_KM_DEVIATION and every other threshold are used as imported.

The only thing this adapter does that run_control() cannot is supply `risk_times` (and a
first-row anchoring rule) from outside, instead of the hard-coded local at km_digitize.py:1429.

Rendering is held FIXED at the `clean` scenario: the figure is rendered and read back exactly
ONCE, and every cell reuses that same digitized curve. Varying the risk table cannot change the
pixels, so a single render is not an approximation -- it is the fixed-rendering condition.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time

REPO_MOD = "/home/user/Rare-cancers/research/modalities"
sys.path.insert(0, REPO_MOD)          # so the copy can find emc_ipd_survival
sys.path.insert(0, "/tmp/claude-0/s4")

import km_digitize_copy as kd          # noqa: E402
import emc_ipd_survival as ipd_mod     # noqa: E402

T_MAX = 180.0
EPS = 0.01                             # "immediately before" offset for the anchored arm


def cohort_hash(cohort):
    blob = json.dumps(cohort, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def risk_table_from_times(cohort, times):
    """Number at risk == number whose observed time is >= t (km_digitize._cohort_to_figure_inputs)."""
    return [[t, sum(1 for r in cohort if r["time"] >= t)] for t in times]


def reconstruct_cell(digitized, risk_table, truth, label):
    curve = {"id": label, "source_id": "control", "endpoint": "os",
             "population": "synthetic control cohort", "time_unit": "months",
             "digitized": digitized, "risk_table": risk_table, "total_events": None,
             "digitized_by": "S4 adapter (fixed clean render, risk table varied)"}
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
    except Exception as exc:  # noqa: BLE001 -- a crash is a RESULT and is recorded, not dropped
        out = {"error": f"{type(exc).__name__}: {exc}"}
    out["seconds"] = round(time.time() - t0, 3)
    return out


def main():
    t_start = time.time()
    cohort = kd._emc_shaped_cohort()
    truth_steps, _, censor_times = kd._cohort_to_figure_inputs(cohort, [0.0])
    truth = {
        "n_patients": len(cohort),
        "n_events": sum(1 for r in cohort if r["event"]),
        "n_censored": sum(1 for r in cohort if not r["event"]),
        "median_survival": ipd_mod._median_survival(ipd_mod.kaplan_meier(cohort)),
    }
    meta = {
        "cohort_sha256": cohort_hash(cohort),
        "n_cohort": len(cohort),
        "truth": truth,
        "t_max": T_MAX,
        "MAX_KM_DEVIATION_as_imported": ipd_mod.MAX_KM_DEVIATION,
        "REQUIRE_RISK_TABLE_as_imported": ipd_mod.REQUIRE_RISK_TABLE,
        "eps_for_anchored_first_row": EPS,
    }

    # ---- the fixed clean render, done ONCE -------------------------------------------------
    t0 = time.time()
    fig = kd.render_km(truth_steps, t_max=T_MAX)
    read = kd.extract_series(fig.img, fig.calib, kd.dark_matcher(), series_label="clean")
    meta["render_read_seconds"] = round(time.time() - t0, 3)
    meta["read_ok"] = read["ok"]
    meta["refusal"] = read.get("refusal")
    if read["ok"]:
        meta["curve_error_vs_truth"] = kd.curve_error(read["digitized"], truth_steps, T_MAX)
        meta["digitized_sha256"] = hashlib.sha256(
            json.dumps(read["digitized"], sort_keys=True).encode()).hexdigest()
        meta["n_digitized_points"] = len(read["digitized"])
    digitized_read = read.get("digitized")
    digitized_exact = [[0.0, 1.0]] + [[t, s] for t, s in truth_steps]

    cells = []

    def run(axis, params, times, first_row_override=None):
        """One grid cell, run under BOTH arms: exact coordinates and the fixed clean render."""
        rt = risk_table_from_times(cohort, times)
        if first_row_override is not None:
            rt[0] = first_row_override
        base = {"axis": axis, **params, "risk_times": [round(t, 4) for t in times],
                "risk_table": rt, "n_rows": len(rt),
                "last_row_time": rt[-1][0], "extent_fraction": round(rt[-1][0] / T_MAX, 4),
                "spacing_note": ("uniform" if len(rt) > 2 else "two rows only")}
        base["exact_arm"] = reconstruct_cell(digitized_exact, rt, truth,
                                             f"s4_exact::{axis}::{params}")
        if digitized_read is not None:
            base["clean_render_arm"] = reconstruct_cell(digitized_read, rt, truth,
                                                        f"s4_read::{axis}::{params}")
        else:
            base["clean_render_arm"] = {"error": "clean render REFUSED; arm not run"}
        cells.append(base)

    def uniform(n_rows, extent_frac):
        last = extent_frac * T_MAX
        if n_rows == 1:
            return [0.0]
        return [round(last * i / (n_rows - 1), 6) for i in range(n_rows)]

    # AXIS 1 -- DENSITY at fixed extent 0.933 (last row 168, the committed control's extent).
    # Row spacing is 168/(n-1) and therefore MOVES with density: at fixed extent, spacing is not
    # independently controllable. Stated, not hidden.
    for n in (2, 3, 5, 8, 13, 19, 25):
        run("density@extent0.933", {"rows": n}, uniform(n, 168.0 / T_MAX))

    # AXIS 2 -- EXTENT at fixed density 8 rows. Spacing again moves with extent; density is held.
    for e in (0.25, 0.5, 0.75, 0.933, 1.0):
        run("extent@rows8", {"extent": e}, uniform(8, e))

    # AXIS 2b -- CONFOUNDED ON PURPOSE, and labelled: fixed 24-unit spacing, so shortening the
    # extent also removes rows. Density and extent move TOGETHER here. Reported as confounded.
    for last in (24.0, 48.0, 96.0, 144.0, 168.0):
        times = [24.0 * i for i in range(int(last // 24) + 1)]
        run("CONFOUNDED_spacing24_extent_and_density_move_together",
            {"last_row": last, "rows": len(times)}, times)

    # AXIS 3 -- ANCHORING of the first printed row, at fixed density/extent otherwise.
    # printed  : first row at t1 with the POST-event count  #{time > t1}
    # anchored : first row at t1-EPS with the PRE-event count #{time >= t1}
    # The remaining rows are the committed control's own 24-unit grid, those strictly above t1.
    for t1 in (0.0, 6.0, 11.0, 24.0):
        tail = [t for t in (0.0, 24.0, 48.0, 72.0, 96.0, 120.0, 144.0, 168.0) if t > t1]
        n_post = sum(1 for r in cohort if r["time"] > t1)
        n_pre = sum(1 for r in cohort if r["time"] >= t1)
        run("anchoring", {"first_row_time": t1, "mode": "printed", "first_row_n": n_post},
            [t1] + tail, first_row_override=[t1, n_post])
        run("anchoring", {"first_row_time": t1, "mode": "anchored", "first_row_n": n_pre},
            [max(t1 - EPS, 0.0)] + tail, first_row_override=[max(t1 - EPS, 0.0), n_pre])

    meta["total_seconds"] = round(time.time() - t_start, 3)
    meta["n_cells"] = len(cells)
    print(json.dumps({"meta": meta, "cells": cells}, indent=1, sort_keys=False))


if __name__ == "__main__":
    main()
