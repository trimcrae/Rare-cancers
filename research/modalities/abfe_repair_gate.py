#!/usr/bin/env python3
"""ABFE λ-repair TECHNICAL-VALIDITY GATE (NR4A3 degrader; prereg §2 as-written).

Implements `nr4a3-abfe-repair-prereg.md` §2 EXACTLY as an automated, auditable pass/fail on ONE reduced ABFE
leg's per-window reduced-potential checkpoints (the `window_XX.jsonl` produced by `nr4a3_abfe.run_window`). This
is the STOPPING RULE machinery of §1: a repaired dense (16-window) leg is a *technical pilot* — it earns
continuation to r2/r3 only by being **technically valid**, never by a favourable ΔΔG. This module answers
"is leg r1 technically valid?" and NOTHING about the numerical selectivity (that is deliberately out of scope so
the gate cannot be gamed by a favourable number).

Design (mirrors nr4a3_abfe.py / nr4a3_abfe_diagnostics.py):
  * PURE glue + lazy heavy deps. The pure-logic criteria (1 schedule identity, 2 data integrity) and the overlap
    GRAPH-connectivity helper are stdlib-only, so they import and unit-test with NO numpy/pymbar (absent in the
    dev sandbox; present in CI). The MBAR-dependent criteria (3 overlap, 4 ESS, 5 convergence) import
    numpy/pymbar INSIDE the functions and, when those are absent, return {passed: None, available: False} rather
    than crashing — the caller/CLI then reports "requires pymbar" instead of a false verdict.
  * REUSES, never duplicates, the engine + diagnostics MBAR machinery: `nr4a3_abfe_diagnostics.load_leg_we`
    (dedup-by-iteration loader, identical safeguard to `reduce_leg`), `.mbar_overlap`, `.we_to_ukln`,
    `.ess_report`; `nr4a3_abfe.reduce_leg` (per-iteration cumulative trace), `._dg_slice`.
  * Reference schedule = `list(zip(LAMBDA_ELEC_DENSE, LAMBDA_STERICS_DENSE))` from the engine (single source of
    truth), so a drift in the engine schedule is caught here rather than silently accepted.

Prereg §2 criteria implemented (see nr4a3-abfe-repair-prereg.md §2, verbatim intent):
  1. schedule_identity — exactly 16 source windows WITH data; every sample's u is a 16-vector; per-window
     (λ_elec, λ_sterics) values AND order match LAMBDA_*_DENSE. jsonl records NO per-window λ, and the current
     meta.json writer records only n_windows (not the λ list), so λ-identity is verifiable ONLY if a future
     meta.json carries a schedule field. When it cannot be verified from data this gate does NOT silently pass
     it: it passes the checkable DIMENSIONS and raises an explicit flag that λ identity was unverifiable.
  2. data_integrity — all reduced potentials finite (no NaN/inf); samples unique after dedup-by-iteration
     (same dedup as reduce_leg); per-window sample counts + duplicates-removed reported.
  3. connected_overlap — MBAR overlap graph connected end-to-end (states 0..15 reachable via overlap>threshold);
     min adjacent overlap >= 0.03 is a WARNING (reported), and a HARD failure if any adjacent pair is near the
     old 0.003 bottleneck (< 0.01) or the graph is effectively disconnected.
  4. ess — decorrelated effective independent samples per state >= 50 (autocorrelation ESS via pymbar
     statistical inefficiency, from the diagnostics ess_report); states below 50 listed → the single §1
     extension is *eligible*, not an outright technical failure.
  5. convergence — |ΔG(full) − ΔG(second half)| <= 1.0 kcal/mol AND a plateau check on the cumulative ΔG(n)
     trace (last ~third flat within uncertainty, not merely ending low).

Criterion 6 (independent re-implemented reduction) is a SEPARATE audit guard (prereg §2.6/§7/§8) that compares
two reduction code paths on the same data; it is intentionally NOT part of this single-leg gate.

Overall `technically_valid` = criteria 1,2,3,5 all pass AND (criterion 4 passes OR its only failures are
low-ESS states eligible for the single §1 extension). Structured detail is returned so the caller can act on
the extension. `technically_valid` is None (not False) when a MBAR criterion could not be evaluated (no pymbar).

CLI: `python abfe_repair_gate.py <leg_dir> [--schedule dense|standard] [--json]`.
"""
import glob
import json
import math
import os
import sys

# Make the sibling engine + diagnostics importable whether this file is run as a script or imported in tests.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nr4a3_abfe import (  # noqa: E402  (engine constants — pure module, json/os only at import)
    LAMBDA_ELEC, LAMBDA_STERICS, LAMBDA_ELEC_DENSE, LAMBDA_STERICS_DENSE,
)

# --- §2 gate thresholds (single place; all overridable per call) ---------------------------------------------
ESS_FLOOR = 50.0            # §2.4 effective independent samples per state
WARN_ADJ_OVERLAP = 0.03     # §2.3 heuristic warning threshold (NOT sufficient proof)
HARD_ADJ_OVERLAP = 0.01     # §2.3 hard floor — no adjacent pair may sit near the old 0.003 bottleneck
OVERLAP_EDGE_THRESHOLD = 0.01  # graph edge exists if overlap > this (end-to-end connectivity test)
HALF_DIFF_TOL = 1.0         # §2.5 |ΔG(full) − ΔG(second half)| ceiling, kcal/mol
PLATEAU_TOL = 0.75          # §2.5 plateau: last-third ΔG spread ceiling (kcal/mol) OR within 2·mean-SE
COMPLETE_FRAC = 0.9         # completeness: a window with < this fraction of the target sample count is
                            # grossly UNDER-SAMPLED (catches 'job said done but a window didn't finish';
                            # 0.9 tolerates the ≤1-checkpoint spot-loss trim, rejects a half-sampled window)


# =============================================================================================================
# reference schedule
# =============================================================================================================
def reference_schedule(schedule="dense"):
    """The expected per-window (λ_elec, λ_sterics) list, from the ENGINE constants (single source of truth).
    `dense` → the 16-window repair schedule (LAMBDA_*_DENSE); `standard` → the 12-window default."""
    if schedule == "dense":
        return list(zip((float(x) for x in LAMBDA_ELEC_DENSE), (float(x) for x in LAMBDA_STERICS_DENSE)))
    if schedule == "standard":
        return list(zip((float(x) for x in LAMBDA_ELEC), (float(x) for x in LAMBDA_STERICS)))
    raise ValueError("schedule must be 'dense' or 'standard', got %r" % (schedule,))


# =============================================================================================================
# PURE stdlib IO — read a leg's windows, deduped by iteration exactly like reduce_leg (no numpy/pymbar)
# =============================================================================================================
def read_windows(leg_dir):
    """Read every `window_NN.jsonl` present in `leg_dir` → {window_index: info}. DEDUPES by iteration index
    (last write wins, sorted by iter) — identical to `nr4a3_abfe.reduce_leg`, so this gate scores exactly the
    samples the ΔG reduction would use. Pure stdlib (no numpy) so criteria 1-2 run in the dev sandbox.

    info = {index, path, n_raw, n_dedup, dup_iters_removed, parse_errors, samples:[(iter, [u...]), ...]}."""
    out = {}
    for p in sorted(glob.glob(os.path.join(leg_dir, "window_*.jsonl"))):
        b = os.path.basename(p)
        try:
            idx = int(b[len("window_"):-len(".jsonl")])
        except ValueError:
            continue
        by_iter, n_raw, parse_errors = {}, 0, 0
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)                          # json.loads accepts NaN/Infinity → kept for
                    it = int(r["iter"])                           # the finiteness check to catch (not error on)
                    u = [float(x) for x in r["u"]]
                except Exception:  # noqa: BLE001 — torn/partial/corrupt line
                    parse_errors += 1
                    continue
                n_raw += 1
                by_iter[it] = u
        samples = [(it, by_iter[it]) for it in sorted(by_iter)]
        out[idx] = {"index": idx, "path": p, "n_raw": n_raw, "n_dedup": len(samples),
                    "dup_iters_removed": n_raw - len(samples), "parse_errors": parse_errors,
                    "samples": samples}
    return out


def _load_meta(leg_dir):
    p = os.path.join(leg_dir, "meta.json")
    if not os.path.exists(p):
        return None
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def _meta_schedule(meta):
    """Extract a per-window (λ_elec, λ_sterics) list from meta.json IF one is recorded, else None. Accepts a
    `schedule`/`lambda_schedule`/`lambdas` list of pairs, or parallel `lambda_elec`(+`_electrostatics`) /
    `lambda_sterics` lists. (The current writer records only n_windows — hence usually None; forward-compatible
    with an enriched meta.json that records the λ list, per prereg §7's semantic-audit ask.)"""
    if not meta:
        return None
    for key in ("schedule", "lambda_schedule", "lambdas"):
        v = meta.get(key)
        if v:
            try:
                return [(float(a), float(b)) for a, b in v]
            except Exception:  # noqa: BLE001
                pass
    le = meta.get("lambda_elec") or meta.get("lambda_electrostatics")
    ls = meta.get("lambda_sterics")
    if le and ls and len(le) == len(ls):
        try:
            return [(float(a), float(b)) for a, b in zip(le, ls)]
        except Exception:  # noqa: BLE001
            return None
    return None


# =============================================================================================================
# PURE overlap-graph connectivity helper (stdlib; unit-tested WITHOUT a real MBAR solve)
# =============================================================================================================
def adjacent_overlaps(overlap):
    """The K−1 nearest-neighbour overlaps O[i][i+1] (works on a list-of-lists OR a numpy array — pure)."""
    K = len(overlap)
    return [float(overlap[i][i + 1]) for i in range(K - 1)]


def overlap_graph_connected(overlap, edge_threshold=OVERLAP_EDGE_THRESHOLD):
    """Is the MBAR overlap graph connected end-to-end? Build an undirected graph with an edge (i,j) whenever
    O[i][j] > edge_threshold (i≠j), BFS from state 0, and check EVERY state 0..K−1 is reachable. This is
    stronger than "min adjacent overlap > x": two windows whose *direct* adjacent overlap dipped low can still
    be bridged by a longer-range overlap, and a genuinely isolated window is caught even if its nominal
    neighbours look fine. Pure stdlib → testable on a synthetic matrix with no pymbar. Returns
    {connected, n_states, reachable, unreachable, edge_threshold}."""
    K = len(overlap)
    if K == 0:
        return {"connected": False, "n_states": 0, "reachable": [], "unreachable": [],
                "edge_threshold": edge_threshold}
    adj = {i: set() for i in range(K)}
    for i in range(K):
        row = overlap[i]
        for j in range(K):
            if i != j and float(row[j]) > edge_threshold:
                adj[i].add(j)
                adj[j].add(i)
    seen, stack = {0}, [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    reachable = sorted(seen)
    unreachable = [i for i in range(K) if i not in seen]
    return {"connected": len(seen) == K, "n_states": K, "reachable": reachable,
            "unreachable": unreachable, "edge_threshold": edge_threshold}


# =============================================================================================================
# availability guard for the MBAR-dependent criteria
# =============================================================================================================
def _mbar_available():
    try:
        import numpy  # noqa: F401
        import pymbar  # noqa: F401
        return True
    except Exception:  # noqa: BLE001 — ModuleNotFoundError in the dev sandbox
        return False


def _unavailable(name):
    return {"passed": None, "available": False,
            "note": "criterion '%s' requires numpy+pymbar (absent in this environment); "
                    "evaluate in CI" % name}


# =============================================================================================================
# CRITERION 1 — schedule identity (pure)
# =============================================================================================================
def crit_schedule_identity(windows, ref_schedule, meta):
    K = len(ref_schedule)
    present = sorted(windows)
    with_data = [i for i in present if windows[i]["n_dedup"] > 0]
    n_with_data = len(with_data)
    contiguous = with_data == list(range(K))          # exactly windows 0..K-1, each with ≥1 sample
    extra = [i for i in present if i >= K]             # e.g. a stray window_16 on a 16-window schedule

    bad_u = []
    for i in with_data:
        for (_it, u) in windows[i]["samples"]:
            if len(u) != K:
                bad_u.append({"window": i, "u_len": len(u)})
                break
    u_ok = not bad_u

    meta_sched = _meta_schedule(meta)
    if meta_sched is not None:
        lambda_match = (meta_sched == ref_schedule)
        lambda_source = "meta.json"
    else:
        lambda_match = None                            # not checkable from the data we have
        lambda_source = "unverifiable"

    meta_nwin = meta.get("n_windows") if meta else None
    meta_nwin_ok = (meta_nwin is None) or (int(meta_nwin) == K)

    dims_ok = contiguous and (n_with_data == K) and u_ok and (not extra) and meta_nwin_ok
    passed = bool(dims_ok and (lambda_match is not False))

    flags = []
    if lambda_match is None:
        flags.append("lambda_identity_could_not_be_verified_from_data: jsonl records no per-window λ and "
                     "meta.json carries no schedule/λ list — only n_windows==%d and u_len==%d were checked; "
                     "per-window (λ_elec,λ_sterics) VALUES+ORDER are NOT confirmed against LAMBDA_*_DENSE" % (K, K))
    if lambda_match is False:
        flags.append("lambda_schedule_in_meta_MISMATCHES_reference (values or order differ from LAMBDA_*_DENSE)")
    if extra:
        flags.append("extra_window_files_beyond_schedule: %r" % extra)
    if not meta_nwin_ok:
        flags.append("meta.n_windows=%r != expected %d" % (meta_nwin, K))

    return {"passed": passed, "available": True,
            "n_windows_expected": K, "n_windows_with_data": n_with_data,
            "windows_present": present, "contiguous_0_to_Kminus1": contiguous,
            "u_length_ok": u_ok, "u_length_violations": bad_u,
            "lambda_identity_source": lambda_source, "lambda_identity_match": lambda_match,
            "lambda_identity_verified_from_data": (lambda_match is True),
            "flags": flags}


# =============================================================================================================
# CRITERION 2 — data integrity (pure)
# =============================================================================================================
def crit_data_integrity(windows, K):
    per_window, nonfinite = [], []
    total_dups = 0
    parse_errs = []
    for i in sorted(windows):
        w = windows[i]
        n_bad = sum(1 for (_it, u) in w["samples"] for x in u if not math.isfinite(x))
        if n_bad:
            nonfinite.append({"window": i, "n_nonfinite_values": n_bad})
        if w["parse_errors"]:
            parse_errs.append({"window": i, "n_parse_errors": w["parse_errors"]})
        total_dups += w["dup_iters_removed"]
        per_window.append({"window": i, "n_raw": w["n_raw"], "n_dedup": w["n_dedup"],
                           "dup_iters_removed": w["dup_iters_removed"], "parse_errors": w["parse_errors"]})

    all_finite = not nonfinite
    no_parse_errors = not parse_errs
    # dedup-by-iteration is applied on read, so within each window every retained sample has a unique iter by
    # construction — assert that invariant explicitly (guards a future loader regression).
    unique_after_dedup = all(len({it for (it, _u) in w["samples"]}) == w["n_dedup"] for w in windows.values())
    passed = bool(all_finite and no_parse_errors and unique_after_dedup)
    return {"passed": passed, "available": True,
            "all_finite": all_finite, "nonfinite_windows": nonfinite,
            "no_parse_errors": no_parse_errors, "parse_error_windows": parse_errs,
            "unique_after_dedup": unique_after_dedup,
            "total_duplicate_iters_removed": total_dups,
            "per_window_sample_counts": per_window}


# =============================================================================================================
# CRITERION 0 — sampling completeness (pure; environment-independent HARD guard)
# =============================================================================================================
def crit_sampling_completeness(windows, K, meta, complete_frac=COMPLETE_FRAC):
    """Every scheduled window must actually have REACHED (near) the target per-window sample count.

    This is the guard against the failure mode where a leg's job exited 'Completed' (SageMaker container
    exit 0 only means exit 0 — NOT that every window ran to n_iter) or a session ASSUMED completion, yet one or
    more windows are far short of the intended n_iter. That is exactly what let an under-sampled window-15
    (1000 of a 2000 target) be briefly mistaken for a finished run: it passed data-integrity (1000 valid
    samples) and ESS (≥50) and only tripped convergence INCIDENTALLY. Completeness is distinct from convergence
    (crit 5): a leg can look 'flat' yet be grossly under-sampled in one window.

    Target per-window count = meta['n_iter'] if recorded (the intended n_iter — now written by run_shard),
    else the MAX dedup count across this leg's windows (a ragged-leg heuristic that works even on legs whose
    meta predates n_iter recording — a lone half-length window still stands out). A window is INCOMPLETE if its
    dedup sample count < complete_frac × target. PURE stdlib (no MBAR) → this HARD-fails an incomplete leg in
    ANY environment, including the dev sandbox, so 'the job said done but a window didn't finish' can never be
    silently promoted."""
    present = sorted(windows)
    counts = {i: windows[i]["n_dedup"] for i in present if windows[i]["n_dedup"] > 0}
    meta_target = None
    if meta and meta.get("n_iter") is not None:
        try:
            v = int(meta.get("n_iter"))
            meta_target = v if v > 0 else None
        except Exception:  # noqa: BLE001
            meta_target = None
    max_count = max(counts.values()) if counts else 0
    target = meta_target if meta_target is not None else max_count
    target_source = "meta.n_iter" if meta_target is not None else "max_window_count(heuristic)"
    threshold = complete_frac * target if target else 0.0

    per_window, incomplete = [], []
    for i in range(K):
        n = counts.get(i, 0)
        ok = (target > 0) and (n >= threshold)
        per_window.append({"window": i, "n_dedup": n, "complete": bool(ok)})
        if not ok:
            incomplete.append({"window": i, "n_dedup": n, "target": target,
                               "fraction_of_target": (round(n / target, 4) if target else None)})
    all_present = len(counts) == K and all(i in counts for i in range(K))
    passed = bool(all_present and not incomplete and target > 0)
    return {"passed": passed, "available": True,
            "target_per_window": target, "target_source": target_source,
            "complete_frac": complete_frac, "threshold_samples": threshold,
            "all_windows_present": all_present, "n_windows_with_data": len(counts),
            "incomplete_windows": incomplete, "per_window_counts": per_window}


# =============================================================================================================
# CRITERION 3 — connected overlap network (MBAR)
# =============================================================================================================
def crit_connected_overlap(leg_dir, K, warn_adj=WARN_ADJ_OVERLAP, hard_adj=HARD_ADJ_OVERLAP,
                           edge_threshold=OVERLAP_EDGE_THRESHOLD):
    if not _mbar_available():
        return _unavailable("connected_overlap")
    import numpy as np  # noqa: F401
    from nr4a3_abfe_diagnostics import load_leg_we, mbar_overlap, we_to_ukln
    try:
        we = load_leg_we(leg_dir, K)
        overlap = mbar_overlap(*we_to_ukln(we, K))
        overlap = overlap.tolist()
        adj = adjacent_overlaps(overlap)
        min_adj = min(adj) if adj else None
        graph = overlap_graph_connected(overlap, edge_threshold=edge_threshold)
        warn = (min_adj is not None) and (min_adj < warn_adj)
        hard_fail = (not graph["connected"]) or (min_adj is None) or (min_adj < hard_adj)
        passed = not hard_fail
        return {"passed": bool(passed), "available": True,
                "min_adjacent_overlap": min_adj, "adjacent_overlaps": adj,
                "connected": graph["connected"], "unreachable_states": graph["unreachable"],
                "warning_min_below_%.3g" % warn_adj: warn,
                "hard_floor": hard_adj, "warn_threshold": warn_adj, "edge_threshold": edge_threshold,
                "note": ("min adjacent overlap %.4f < warn %.3g (heuristic warning, not a failure by itself)"
                         % (min_adj, warn_adj)) if warn and passed else None}
    except Exception as e:  # noqa: BLE001 — an MBAR solve failure IS a technical failure; surface it
        return {"passed": False, "available": True, "error": "%s: %s" % (type(e).__name__, e)}


# =============================================================================================================
# CRITERION 4 — effective sample size (MBAR / decorrelation)
# =============================================================================================================
def crit_ess(leg_dir, K, floor=ESS_FLOOR):
    if not _mbar_available():
        return _unavailable("ess")
    from nr4a3_abfe_diagnostics import load_leg_we, ess_report
    try:
        we = load_leg_we(leg_dir, K)
        rows = ess_report(we, K)
        # §2.4 floor is on DECORRELATED independent samples → autocorrelation ESS (N/g). MBAR weight-based ESS
        # is reported alongside for context but the gate is on the decorrelation-based number.
        below = [{"window": r["window"], "ess_autocorr": r["ess_autocorr"], "g": r["g"],
                  "n_samples": r["n_samples"], "ess_mbar": r["ess_mbar"]}
                 for r in rows if (r["ess_autocorr"] is None or r["ess_autocorr"] < floor)]
        passed = not below
        return {"passed": bool(passed), "available": True, "floor": floor,
                "states_below_floor": below,
                "extension_eligible": bool(below),   # §1: below-floor states trigger the single extension
                "per_state_ess": [{"window": r["window"], "n_samples": r["n_samples"], "g": r["g"],
                                   "ess_autocorr": r["ess_autocorr"], "ess_mbar": r["ess_mbar"]}
                                  for r in rows]}
    except Exception as e:  # noqa: BLE001
        return {"passed": None, "available": True, "extension_eligible": False,
                "error": "%s: %s" % (type(e).__name__, e)}


# =============================================================================================================
# CRITERION 5 — convergence (half-difference + plateau) (MBAR)
# =============================================================================================================
def crit_convergence(leg_dir, K, meta, half_diff_tol=HALF_DIFF_TOL, plateau_tol=PLATEAU_TOL):
    if not _mbar_available():
        return _unavailable("convergence")
    from nr4a3_abfe import reduce_leg, _dg_slice
    from nr4a3_abfe_diagnostics import load_leg_we
    T = float((meta or {}).get("temperature_K", 300.0))
    RT = 0.0019872041 * T
    try:
        we = load_leg_we(leg_dir, K)
        n = min((len(w) for w in we), default=0)
        if n < 4:
            return {"passed": False, "available": True, "note": "too few samples/window (n_min=%d) to assess "
                    "convergence" % n, "n_min": n}
        full = _dg_slice(we, 0, n, K, RT)
        second = _dg_slice(we, n // 2, n, K, RT)
        if full is None or second is None:
            return {"passed": False, "available": True,
                    "note": "an empty window on the full or second-half slice — cannot form ΔG"}
        half_diff = abs(full[0] - second[0])
        half_pass = half_diff <= half_diff_tol

        # plateau: cumulative-from-start ΔG(n) trace; the LAST ~third must be flat within uncertainty (spread
        # <= plateau_tol OR within 2·mean-SE), i.e. genuinely settled — not merely ending at a low value.
        trace = reduce_leg(leg_dir, per_iteration=True)            # [(n, dg, se), ...]
        plateau = _plateau_check(trace, plateau_tol)

        passed = bool(half_pass and plateau["plateau_flat"])
        return {"passed": passed, "available": True,
                "dg_full": full[0], "se_full": full[1],
                "dg_second_half": second[0], "se_second_half": second[1],
                "half_difference": half_diff, "half_difference_tol": half_diff_tol,
                "half_difference_pass": bool(half_pass),
                "plateau": plateau, "n_min": n, "temperature_K": T}
    except Exception as e:  # noqa: BLE001 — a failed reduce/solve is a technical failure
        return {"passed": False, "available": True, "error": "%s: %s" % (type(e).__name__, e)}


def _plateau_check(trace, plateau_tol, frac=1.0 / 3.0):
    """Is the tail of a cumulative ΔG(n) trace flat within uncertainty? Takes the last `frac` of the trace
    points and passes iff their ΔG spread (max−min) <= plateau_tol OR <= 2·mean(SE) over that tail — i.e. the
    estimate has SETTLED, not merely ended at a favourable value. Pure arithmetic (trace already computed)."""
    if not trace or len(trace) < 3:
        return {"plateau_flat": False, "note": "trace too short (%d points) to assess a plateau"
                % (len(trace) if trace else 0), "n_points": (len(trace) if trace else 0)}
    m = max(2, int(math.ceil(len(trace) * frac)))
    tail = trace[-m:]
    dgs = [t[1] for t in tail]
    ses = [t[2] for t in tail]
    spread = max(dgs) - min(dgs)
    mean_se = sum(ses) / len(ses) if ses else 0.0
    flat = (spread <= plateau_tol) or (spread <= 2.0 * mean_se)
    return {"plateau_flat": bool(flat), "tail_points": len(tail), "tail_spread": spread,
            "tail_mean_se": mean_se, "plateau_tol": plateau_tol,
            "tail_first_n": tail[0][0], "tail_last_n": tail[-1][0]}


# =============================================================================================================
# top-level gate
# =============================================================================================================
def evaluate_repair_gate(leg_dir, schedule="dense", floor=ESS_FLOOR, warn_adj=WARN_ADJ_OVERLAP,
                         hard_adj=HARD_ADJ_OVERLAP, edge_threshold=OVERLAP_EDGE_THRESHOLD,
                         half_diff_tol=HALF_DIFF_TOL, plateau_tol=PLATEAU_TOL):
    """Evaluate prereg §2 on ONE reduced ABFE leg directory → structured pass/fail per criterion + an overall
    `technically_valid` verdict. `schedule='dense'` is the repair schedule (16 windows). MBAR criteria (3,4,5)
    return {passed:None, available:False} when numpy/pymbar are absent (dev sandbox); `technically_valid` is
    then None. See module docstring for the exact §2 mapping."""
    ref = reference_schedule(schedule)
    K = len(ref)
    meta = _load_meta(leg_dir)
    windows = read_windows(leg_dir)

    c0 = crit_sampling_completeness(windows, K, meta)
    c1 = crit_schedule_identity(windows, ref, meta)
    c2 = crit_data_integrity(windows, K)
    c3 = crit_connected_overlap(leg_dir, K, warn_adj=warn_adj, hard_adj=hard_adj, edge_threshold=edge_threshold)
    c4 = crit_ess(leg_dir, K, floor=floor)
    c5 = crit_convergence(leg_dir, K, meta, half_diff_tol=half_diff_tol, plateau_tol=plateau_tol)

    criteria = {"0_sampling_completeness": c0, "1_schedule_identity": c1, "2_data_integrity": c2,
                "3_connected_overlap": c3, "4_ess": c4, "5_convergence": c5}

    # SAMPLING-COMPLETENESS is a PURE, environment-independent HARD gate: a leg with a grossly under-sampled
    # window is INVALID regardless of the MBAR criteria (and even when pymbar is absent). This is what makes
    # 'the job exited Completed but a window didn't finish' a definitive FAIL you can catch anywhere — it must
    # short-circuit BEFORE the pymbar-availability deferral, so an incomplete leg never returns None ("deferred")
    # and get mistaken for "not yet failed".
    if c0["passed"] is False:
        technically_valid = False
        overall_note = ("INCOMPLETE leg: windows %s are below %.0f%% of the target %s sample count "
                        "(source: %s). A 'Completed' job status only means the container exited 0 — it does "
                        "NOT prove every window reached the target n_iter; finish the sampling and re-run."
                        % ([w["window"] for w in c0["incomplete_windows"]], 100 * c0["complete_frac"],
                           c0["target_per_window"], c0["target_source"]))
    else:
        # §2 overall rule: 1,2,3,5 must all PASS; criterion 4 must PASS or its failures be low-ESS states
        # eligible for the single §1 extension. Any MBAR criterion that could not be evaluated → verdict None.
        hard = [c1, c2, c3, c5]
        hard_available = all(c.get("available") for c in hard) and c4.get("available")
        if not hard_available:
            technically_valid = None
            overall_note = ("verdict deferred: one or more MBAR criteria (3/4/5) could not be evaluated here "
                            "(numpy/pymbar absent) — run in CI. Pure criteria 0-2 were still evaluated.")
        else:
            hard_pass = all(bool(c.get("passed")) for c in hard)
            c4_ok = bool(c4.get("passed")) or bool(c4.get("extension_eligible"))
            technically_valid = bool(hard_pass and c4_ok)
            overall_note = None

    extension_recommended = bool(c4.get("available") and not c4.get("passed") and c4.get("extension_eligible"))

    return {
        "leg_dir": os.path.abspath(leg_dir),
        "schedule": schedule,
        "n_windows_expected": K,
        "technically_valid": technically_valid,
        "extension_recommended": extension_recommended,
        "extension_detail": (c4.get("states_below_floor") if extension_recommended else None),
        "criteria": criteria,
        "overall_note": overall_note,
        "prereg": "nr4a3-abfe-repair-prereg.md §2 (criterion 6 independent-reduction audit is out of scope of "
                  "this single-leg gate; see prereg §2.6/§7/§8)",
    }


# =============================================================================================================
# CLI
# =============================================================================================================
def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="ABFE λ-repair technical-validity gate (prereg §2).")
    ap.add_argument("leg_dir", help="a reduced ABFE leg directory containing window_NN.jsonl (+ meta.json)")
    ap.add_argument("--schedule", default="dense", choices=["dense", "standard"],
                    help="expected λ schedule (default: dense = 16-window repair)")
    ap.add_argument("--json", action="store_true", help="print the full result dict as JSON")
    args = ap.parse_args(argv)

    res = evaluate_repair_gate(args.leg_dir, schedule=args.schedule)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("ABFE λ-repair gate — %s (schedule=%s, K=%d)" % (res["leg_dir"], res["schedule"],
                                                               res["n_windows_expected"]))
        for name, c in res["criteria"].items():
            p = c.get("passed")
            tag = "PASS" if p is True else ("FAIL" if p is False else "N/A ")
            print("  [%s] %s" % (tag, name))
            for fl in c.get("flags", []) or []:
                print("        flag: %s" % fl)
            for iw in c.get("incomplete_windows", []) or []:
                print("        INCOMPLETE window %s: %s/%s samples (%.0f%% of target %s)"
                      % (iw["window"], iw["n_dedup"], iw["target"],
                         100 * (iw["fraction_of_target"] or 0), c.get("target_source", "?")))
            if c.get("error"):
                print("        error: %s" % c["error"])
            if c.get("note"):
                print("        note: %s" % c["note"])
        tv = res["technically_valid"]
        print("  => technically_valid = %s%s" % (tv, "  (extension recommended for low-ESS states)"
                                                  if res["extension_recommended"] else ""))
        if res["overall_note"]:
            print("     %s" % res["overall_note"])
    # exit code: 0 valid, 1 invalid, 2 deferred (couldn't evaluate)
    tv = res["technically_valid"]
    return 0 if tv is True else (2 if tv is None else 1)


if __name__ == "__main__":
    sys.exit(_cli())
