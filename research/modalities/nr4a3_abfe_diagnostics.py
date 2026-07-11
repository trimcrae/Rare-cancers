#!/usr/bin/env python3
"""ABFE/FEP SI diagnostics for the selectivity ABFE (JCIM review comment 17).

Turns the INTACT ABFE raw data (the small per-window per-iteration reduced-potential jsonl checkpoints under
`s3://<bucket>/nr4a3-abfe*/ckpt/**`) into the supporting-information diagnostics a rigorous ABFE result must
carry: per-replicate ΔG, λ-window MBAR **overlap** matrices, **effective sample sizes** (weight-based AND
autocorrelation-based), and **forward/reverse convergence** traces — all recomputed from the SAME reduced
potentials the committed §4 numbers came from (so they can be cross-checked against the manuscript).

Design:
  * PURE + unit-tested. numpy / pymbar are lazy-imported INSIDE the functions (matching nr4a3_abfe.py), so this
    module imports with no heavy deps; only the diagnostic calls need them.
  * REUSES the engine's own MBAR machinery — `nr4a3_abfe.assemble_ukn` (u_kn assembly), `_solve_mbar` (the
    robust MBAR construction with BAR-init / robust-solver fallbacks), `_dg_slice` (leg ΔG on a sample slice),
    `combine_legs`, `selectivity_ddg`. We do NOT reimplement pymbar. Overlap/ESS come from pymbar's own
    `MBAR.compute_overlap()` / `MBAR.compute_effective_sample_number()`; per-window autocorrelation ESS from
    `pymbar.timeseries.statistical_inefficiency`.
  * The reduced-potential loader `load_leg_we` DEDUPES by iteration index exactly like `reduce_leg` does, so a
    leg's crash/resume/recovery duplicate records don't double-count — the same safeguard the §4 reduction uses.

S3 layout this consumes (produced by nr4a3_abfe_sagemaker.py / entry_abfe.py — see that submitter):
    replicate tag r1 = `nr4a3-abfe`, r2 = `nr4a3-abfe-r2`, r3 = `nr4a3-abfe-r3`
    <tag>/ckpt/complex-<receptor>/  -> nested <receptor>/complex/window_{00..11}.jsonl (+ meta.json w/ SSC)
    <tag>/ckpt/solvent/             -> nested shared/solvent/window_{00..11}.jsonl   (shared ligand-in-water)
  each window_kk.jsonl line = {"w": k, "iter": i, "u": [reduced potential at ALL 12 λ]}  (u already = β·U).
The S3 sync + plotting + git commit live in the driver `nr4a3_abfe_diagnostics_run.py`; this module is IO-free
except `load_leg_we` (reads local jsonl a driver has already synced).
"""
import json
import math
import os

# Committed manuscript §4 numbers (nr4a3-degrader-paper.md, three-replicate 2 ns/window ABFE) — the recomputed
# diagnostics must reproduce these. (mean, between-replicate SD n=3). Raw-engine ΔG_bind and selectivity ΔΔG.
MANUSCRIPT_S4 = {
    "dg_bind": {"nr4a3": (3.5, 1.4), "nr4a1": (8.3, 1.1), "nr4a2": (8.5, 0.7)},
    "ddg": {"nr4a1": (-4.76, 2.03), "nr4a2": (-4.98, 0.68)},
    "note": "raw-engine ΔG_bind (kcal/mol); ΔΔG = ΔG_bind(NR4A3) − ΔG_bind(paralogue); n=3 replicate SD.",
}


# --------------------------------------------------------------------------------------------------------------
# reduced-potential IO (dedup-by-iteration, matching reduce_leg) + ragged→dense conversion
# --------------------------------------------------------------------------------------------------------------
def n_windows():
    """Number of λ-windows/leg, from the engine's DEFAULT schedule (single source of truth for a default run).
    NOTE: a dense-λ REPAIR run uses more windows than this — use detect_K(leg_dir) for those (per-leg, from the
    checkpoint), because the default schedule length would be wrong."""
    from nr4a3_abfe import lambda_schedule
    return len(lambda_schedule())


def detect_K(leg_dir):
    """Auto-detect a leg's actual λ-window count FROM ITS CHECKPOINT — the dense-repair schedule has more
    windows than the default engine schedule, so n_windows() mis-reads repair runs (the bug that crashed the
    validate gate: "window 0 sample has 16 energies, expected 12"). K == the width of a reduced-potential
    vector `u` (each sample is evaluated at all K λ-states). Falls back to the max window-file index + 1, then
    the default n_windows(). Pure (filesystem read only)."""
    import glob
    files = sorted(glob.glob(os.path.join(leg_dir, "window_*.jsonl")))
    for p in files:
        try:
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    u = json.loads(line).get("u")
                    if u:
                        return len(u)
        except Exception:  # noqa: BLE001 — torn file; try the next
            continue
    idxs = []
    for p in files:
        b = os.path.basename(p)
        try:
            idxs.append(int(b[len("window_"):-len(".jsonl")]))
        except Exception:  # noqa: BLE001
            pass
    return (max(idxs) + 1) if idxs else n_windows()


def load_leg_we(leg_dir, K=None):
    """Read one leg's per-window jsonl → we[k] = [u_at_all_λ, ...] for window k, DEDUPED by iteration index.

    A window's log can hold duplicate records for the same iteration (crash/resume/recovery cycles); we keep one
    sample per iter (the last-written), sorted by iter — identical to `nr4a3_abfe.reduce_leg`, so the diagnostics
    see exactly the samples the §4 ΔG reduction saw. Missing window files contribute an empty list.

    K defaults to the leg's OWN detected window count (detect_K), so a dense-λ repair run (more windows than the
    default schedule) is read correctly instead of crashing on the width mismatch."""
    K = K or detect_K(leg_dir)
    we = [[] for _ in range(K)]
    for k in range(K):
        p = os.path.join(leg_dir, "window_%02d.jsonl" % k)
        if not os.path.exists(p):
            continue
        by_iter = {}
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    by_iter[int(r["iter"])] = [float(x) for x in r["u"]]
                except Exception:  # noqa: BLE001 — torn/partial last line
                    continue
        we[k] = [by_iter[i] for i in sorted(by_iter)]
    return we


def we_to_ukln(we, K=None):
    """Ragged per-window samples → the classic pymbar u_kln array (K, K, N_max) + N_k.

    u_kln[k, l, n] = reduced potential of sample n drawn from state k, evaluated at state l. Windows with fewer
    than N_max samples are zero-padded on the sample axis; the padding is never read because N_k bounds each
    state's real sample count. Returns (u_kln ndarray, N_k list)."""
    import numpy as np
    K = K or len(we)
    N_k = [len(w) for w in we]
    n_max = max(N_k) if N_k else 0
    u = np.zeros((K, K, n_max), dtype=float)
    for k in range(K):
        for n, sample in enumerate(we[k]):
            if len(sample) != K:
                raise ValueError("window %d sample has %d energies, expected %d" % (k, len(sample), K))
            u[k, :, n] = sample
    return u, N_k


def ukln_to_ukn(u_kln, N_k=None):
    """Classic (K, K, N_max) u_kln → pymbar-4 flat (K, N_total) u_kn + N_k (only the first N_k[k] samples of
    each state are taken, so a padded/ragged u_kln is handled). Inverse-ish of we_to_ukln for the MBAR call."""
    import numpy as np
    u_kln = np.asarray(u_kln, dtype=float)
    K = u_kln.shape[0]
    if u_kln.shape[1] != K:
        raise ValueError("u_kln must be (K, K, N); got %r" % (u_kln.shape,))
    n_max = u_kln.shape[2]
    N_k = [int(n) for n in (N_k if N_k is not None else [n_max] * K)]
    if any(n > n_max for n in N_k):
        raise ValueError("N_k %r exceeds sample axis %d" % (N_k, n_max))
    u_kn = np.zeros((K, sum(N_k)), dtype=float)
    col = 0
    for k in range(K):
        for n in range(N_k[k]):
            u_kn[:, col] = u_kln[k, :, n]
            col += 1
    return u_kn, N_k


def _mbar_from_ukln(u_kln, N_k=None, tag="diag"):
    """Build a solved pymbar MBAR from a u_kln (reuses the engine's robust `_solve_mbar`)."""
    import numpy as np
    from nr4a3_abfe import _solve_mbar
    u_kn, N_k = ukln_to_ukn(u_kln, N_k)
    return _solve_mbar(np.asarray(u_kn), np.asarray(N_k), tag=tag)


# --------------------------------------------------------------------------------------------------------------
# 1. λ-window MBAR overlap matrix
# --------------------------------------------------------------------------------------------------------------
def mbar_overlap(u_kln, N_k=None):
    """λ×λ MBAR overlap matrix O (K×K) from a u_kln. O[i,j] = N_i · Σ_n W_ni W_nj is the standard pymbar
    overlap: O near the value 1/K everywhere ⇒ perfect mixing; a near-block-diagonal O (small ADJACENT
    off-diagonals) ⇒ poorly-overlapping neighbouring λ-windows, i.e. an under-resolved schedule. Delegates to
    pymbar's `MBAR.compute_overlap()` (no reimplementation). Returns a numpy (K,K) array."""
    import numpy as np
    m = _mbar_from_ukln(u_kln, N_k, tag="overlap")
    return np.asarray(m.compute_overlap()["matrix"], dtype=float)


def adjacent_overlaps(overlap):
    """The K−1 nearest-neighbour overlaps O[i, i+1] — the practically-relevant diagnostic (MBAR/BAR only need
    consecutive windows to overlap). Returns a list; `min(...)` of it is the schedule's weakest link."""
    import numpy as np
    o = np.asarray(overlap)
    return [float(o[i, i + 1]) for i in range(o.shape[0] - 1)]


# --------------------------------------------------------------------------------------------------------------
# 2. effective sample size — MBAR weight-based (per state) AND autocorrelation-based (per window)
# --------------------------------------------------------------------------------------------------------------
def effective_sample_size(u_kln, N_k=None):
    """MBAR effective sample number per state = 1 / Σ_n W_nk² (pymbar's `compute_effective_sample_number`).
    This is how many *effective* independent samples inform each λ-state's free energy given the reweighting;
    a state whose ESS ≪ its N_k is contributing little. Returns a numpy (K,) array. Reuses pymbar directly."""
    import numpy as np
    m = _mbar_from_ukln(u_kln, N_k, tag="ess")
    return np.asarray(m.compute_effective_sample_number(), dtype=float)


def autocorr_inefficiency(series):
    """Statistical inefficiency g and autocorrelation ESS = N/g of a 1-D time series, via
    `pymbar.timeseries.statistical_inefficiency`. g ≈ 1 for uncorrelated samples (ESS ≈ N); g ≫ 1 for a slowly
    decorrelating series (ESS ≪ N). Constant/degenerate/too-short series → (1.0, N) (no correlation to estimate).
    Returns (g, ess)."""
    import numpy as np
    s = np.asarray(series, dtype=float)
    n = int(s.size)
    if n < 3 or np.allclose(s, s.flat[0]):
        return 1.0, float(n)
    try:
        from pymbar import timeseries
        g = float(timeseries.statistical_inefficiency(s))
    except Exception:  # noqa: BLE001 — fall back to no-correlation on any estimator failure
        return 1.0, float(n)
    g = max(g, 1.0)
    return g, n / g


def ess_report(we, K=None):
    """Per-window ESS table combining BOTH estimators the review asked for:
      - ess_mbar : MBAR weight-based effective sample number for that λ-state (reweighting efficiency);
      - g, ess_autocorr : statistical inefficiency / autocorrelation ESS of the window's OWN reduced-potential
        time series u(x_n; λ_k) (sampling efficiency within the window).
    Returns [{window, n_samples, ess_mbar, g, ess_autocorr}, ...]."""
    K = K or (len(we) if we else n_windows())
    ess_mbar = effective_sample_size(*we_to_ukln(we, K))
    rows = []
    for k in range(len(we)):
        self_series = [s[k] for s in we[k]]              # u of window-k samples evaluated AT window k
        g, ess_ac = autocorr_inefficiency(self_series)
        rows.append({"window": k, "n_samples": len(we[k]),
                     "ess_mbar": float(ess_mbar[k]) if k < len(ess_mbar) else None,
                     "g": g, "ess_autocorr": ess_ac})
    return rows


# --------------------------------------------------------------------------------------------------------------
# 3. forward / reverse convergence trace
# --------------------------------------------------------------------------------------------------------------
def _default_fractions():
    return [round(0.1 * i, 2) for i in range(1, 11)]      # 0.1 … 1.0


def forward_reverse_dG(we, temperature_K=300.0, fractions=None, K=None):
    """Forward/reverse convergence of a LEG's ΔG (kcal/mol). For each fraction f:
      - forward : MBAR ΔG using the FIRST ⌈f·N⌉ samples of every window (cumulative-from-start);
      - reverse : MBAR ΔG using the LAST  ⌈f·N⌉ samples of every window (cumulative-from-end).
    A converged, equilibrated leg has forward(f) and reverse(f) approaching the SAME value as f→1 and agreeing
    within error across f; a persistent forward↔reverse gap flags equilibration bias / slow modes the pooled
    MBAR SE cannot see. ΔG per slice = RT·Δf[0,K−1] via the engine's `_dg_slice` (same MBAR the reducer uses).
    Returns {forward:[{fraction,n,dg,se}], reverse:[...], n_min, n_windows}. N is the min across windows so every
    window contributes on every slice."""
    from nr4a3_abfe import _dg_slice
    K = K or len(we)
    RT = 0.0019872041 * temperature_K
    fractions = fractions or _default_fractions()
    n = min((len(w) for w in we), default=0)
    fwd, rev = [], []
    seen = set()
    for f in fractions:
        m = max(2, int(math.ceil(f * n)))
        m = min(m, n)
        if m in seen and f != fractions[-1]:
            continue
        seen.add(m)
        rf = _dg_slice(we, 0, m, K, RT)
        if rf:
            fwd.append({"fraction": f, "n": m, "dg": rf[0], "se": rf[1]})
        rr = _dg_slice(we, n - m, n, K, RT)
        if rr:
            rev.append({"fraction": f, "n": m, "dg": rr[0], "se": rr[1]})
    return {"forward": fwd, "reverse": rev, "n_min": n, "n_windows": K}


# --------------------------------------------------------------------------------------------------------------
# per-leg bundle + per-receptor ΔG_bind + per-replicate summary reproducing §4
# --------------------------------------------------------------------------------------------------------------
def leg_diagnostics(we, temperature_K=300.0, K=None, with_convergence=True):
    """All per-leg diagnostics for one leg's `we`: overlap matrix (+ adjacent overlaps + weakest link), the
    per-window ESS table, sample counts, and (optionally) the forward/reverse convergence trace. IO-free."""
    K = K or (len(we) if we else n_windows())
    if not any(we):
        return {"n_windows": K, "n_samples_per_window": [len(w) for w in we], "empty": True}
    ov = mbar_overlap(*we_to_ukln(we, K))
    adj = adjacent_overlaps(ov)
    out = {
        "n_windows": K,
        "n_samples_per_window": [len(w) for w in we],
        "overlap_matrix": ov.tolist(),
        "adjacent_overlaps": adj,
        "min_adjacent_overlap": (min(adj) if adj else None),
        "ess": ess_report(we, K),
    }
    if with_convergence:
        out["convergence"] = forward_reverse_dG(we, temperature_K=temperature_K, K=K)
    return out


def receptor_dg_bind(complex_we, solvent_we, restraint_standard_state_dg, temperature_K=300.0, K=None):
    """ΔG_bind (kcal/mol) for one receptor from its complex + shared-solvent legs' deduped samples, using the
    engine's MBAR reducer (`_dg_slice` over the full slice) + `combine_legs` with the complex-leg Boresch SSC.
    Returns {dg_bind, se, complex_dg, complex_se, solvent_dg, solvent_se, restraint_standard_state_dg}. This
    reproduces exactly what `nr4a3_abfe.reduce_and_report` computes (same dedup, same MBAR, same combination)."""
    from nr4a3_abfe import _dg_slice, combine_legs
    K = K or n_windows()
    RT = 0.0019872041 * temperature_K
    cn = min((len(w) for w in complex_we), default=0)
    sn = min((len(w) for w in solvent_we), default=0)
    c = _dg_slice(complex_we, 0, cn, K, RT) if cn else None
    s = _dg_slice(solvent_we, 0, sn, K, RT) if sn else None
    if c is None or s is None:
        return None
    dg, se = combine_legs(c[0], c[1], s[0], s[1], restraint_standard_state_dg)
    return {"dg_bind": dg, "se": se, "complex_dg": c[0], "complex_se": c[1],
            "solvent_dg": s[0], "solvent_se": s[1], "restraint_standard_state_dg": restraint_standard_state_dg}


def _mean_sd(values):
    """(mean, sample SD [ddof=1], n). SD is None for n<2. Matches the manuscript's between-replicate SD (n−1)."""
    vals = [float(v) for v in values]
    n = len(vals)
    if n == 0:
        return None, None, 0
    mean = sum(vals) / n
    if n < 2:
        return mean, None, n
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    return mean, var ** 0.5, n


def per_replicate_summary(dg_bind_by_rep, target="nr4a3"):
    """Reproduce the §4 three-replicate result from per-replicate per-receptor ΔG_bind.

    dg_bind_by_rep = {rep_label: {receptor: dg_bind_float}}  (e.g. {"r1": {"nr4a3": 2.6, ...}, ...}).
    Returns:
      per_receptor : {receptor: {values:{rep:dg}, mean, sd, n}}                          → the ΔG_bind ± SD line
      ddg          : {other: {per_rep:{rep:ΔΔG}, mean, sd, n, direction_unanimous}}       → ΔΔG(target−other) ± SD
                     ΔΔG = ΔG_bind(target) − ΔG_bind(other); NEGATIVE ⇒ target-selective. direction_unanimous =
                     every replicate agrees on the sign (the §4 'unanimous direction' claim).
    Pure arithmetic (uses nr4a3_abfe.selectivity_ddg only for the sign convention)."""
    reps = sorted(dg_bind_by_rep)
    receptors = sorted({r for rep in dg_bind_by_rep.values() for r in rep})
    per_receptor = {}
    for rec in receptors:
        vals = {rep: dg_bind_by_rep[rep][rec] for rep in reps if rec in dg_bind_by_rep[rep]}
        mean, sd, n = _mean_sd(vals.values())
        per_receptor[rec] = {"values": vals, "mean": mean, "sd": sd, "n": n}
    ddg = {}
    for other in receptors:
        if other == target:
            continue
        per_rep = {}
        for rep in reps:
            d = dg_bind_by_rep[rep]
            if target in d and other in d:
                per_rep[rep] = d[target] - d[other]        # ΔΔG(target − other); <0 ⇒ target tighter
        mean, sd, n = _mean_sd(per_rep.values())
        ddg[other] = {"per_rep": per_rep, "mean": mean, "sd": sd, "n": n,
                      "direction_unanimous": (n > 0 and (all(v < 0 for v in per_rep.values())
                                                         or all(v > 0 for v in per_rep.values())))}
    return {"target": target, "replicates": reps, "per_receptor": per_receptor, "ddg": ddg}


def check_against_manuscript(summary, tol_mean=0.6, tol_sd=0.5):
    """Cross-check a per_replicate_summary against the committed §4 numbers (MANUSCRIPT_S4). Returns a list of
    {quantity, recomputed, expected, delta, within_tol} rows and an overall `consistent` flag. tol_mean/tol_sd
    default to ~0.5 kcal/mol — the recomputed value should land essentially on the manuscript number; a larger
    gap means the diagnostics are reading different data than §4 and MUST be flagged (do NOT silently accept)."""
    rows = []

    def _cmp(name, got, exp, tol):
        ok = (got is not None and exp is not None and abs(got - exp) <= tol)
        rows.append({"quantity": name, "recomputed": got, "expected": exp,
                     "delta": (None if (got is None or exp is None) else round(got - exp, 3)),
                     "tol": tol, "within_tol": bool(ok)})

    for rec, (em, esd) in MANUSCRIPT_S4["dg_bind"].items():
        pr = summary.get("per_receptor", {}).get(rec, {})
        _cmp("dg_bind[%s].mean" % rec, pr.get("mean"), em, tol_mean)
        _cmp("dg_bind[%s].sd" % rec, pr.get("sd"), esd, tol_sd)
    for other, (em, esd) in MANUSCRIPT_S4["ddg"].items():
        dd = summary.get("ddg", {}).get(other, {})
        _cmp("ddg[nr4a3-%s].mean" % other, dd.get("mean"), em, tol_mean)
        _cmp("ddg[nr4a3-%s].sd" % other, dd.get("sd"), esd, tol_sd)
    return {"rows": rows, "consistent": all(r["within_tol"] for r in rows)}
