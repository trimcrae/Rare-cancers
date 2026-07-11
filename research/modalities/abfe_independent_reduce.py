#!/usr/bin/env python3
"""Independent MBAR reduction — a SEPARATELY-WRITTEN cross-check of nr4a3_abfe.reduce_leg (reviewer §2.6/§7).

The prereg's technical-acceptance criterion 6 ("independent reduction") requires that a second,
independently-implemented MBAR input-assembly + reduction reproduce a leg's ΔG to within tolerance on the SAME
data — this guards the *reduction path itself* (K inference, dedup, u_kn/N_k assembly, MBAR call), not just the
raw window data. A single reducer that agrees with itself proves nothing about a bug shared by both uses.

Deliberately does NOT reuse nr4a3_abfe's ``assemble_ukn`` / ``_read_we`` / ``_infer_k`` / ``reduce_leg``: the
window discovery, the dedup-by-iteration, and the u_kn / N_k matrix assembly are all re-derived here from the
window_XX.jsonl on disk. ``compare_reducers`` then runs BOTH reducers on one leg and reports agreement.

numpy + pymbar are imported INSIDE the functions (absent from the free CPU sandbox; present only in the CI
reduce runner), matching the nr4a3_abfe convention. The unit tests import-skip anything that needs pymbar.
"""
import glob
import json
import os
import sys

# kcal/mol per kT (R in kcal/mol/K) — identical constant to nr4a3_abfe so the two reducers are on the same
# energy scale; RT = this * T.
_RT_PER_K = 0.0019872041


def _discover_windows(leg_dir):
    """Contiguous window count K from window_00.jsonl, window_01.jsonl, ... on disk. Independent of any
    schedule env var (matches the data, like a fresh reduce should). Returns K (0 if none)."""
    k = 0
    while os.path.exists(os.path.join(leg_dir, f"window_{k:02d}.jsonl")):
        k += 1
    return k


def _read_window_dedup(path):
    """Read one window's jsonl → list of reduced-potential vectors, ONE per iteration (last record wins on a
    duplicate iter from a crash/resume/recovery cycle), ordered by iteration index. Torn/blank lines skipped."""
    best = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:  # noqa: BLE001 — torn final line on an interrupted upload
                continue
            if "iter" not in rec or "u" not in rec:
                continue
            best[int(rec["iter"])] = [float(x) for x in rec["u"]]
    return [best[i] for i in sorted(best)]


def independent_reduce_leg(leg_dir, temperature_K=300.0):
    """Independently MBAR-reduce ONE leg from its window_XX.jsonl → (dG, SE) in kcal/mol.

    Own implementation end-to-end: discover K from the files, dedup each window by iteration, assemble the
    (K, N_total) reduced-potential matrix u_kn and the (K,) sample-count vector N_k with local code, then solve
    with pymbar.MBAR and return RT·Δf[0, K-1] and its SE. Cross-checks that every sample's u vector has length K
    and fails loudly otherwise (the same corrupt/mixed-leg guard the primary reducer enforces, re-implemented).
    """
    import numpy as np
    from pymbar import MBAR

    K = _discover_windows(leg_dir)
    if K == 0:
        raise FileNotFoundError(f"no window_XX.jsonl found in {leg_dir}")

    per_window = []  # per_window[k] = [u_vec, ...]
    for k in range(K):
        samples = _read_window_dedup(os.path.join(leg_dir, f"window_{k:02d}.jsonl"))
        for s in samples:
            if len(s) != K:
                raise ValueError(f"independent_reduce_leg: {leg_dir}: window {k} has a sample with "
                                 f"{len(s)} reduced potentials but there are {K} windows — corrupt/mixed leg")
        per_window.append(samples)

    N_k = np.array([len(s) for s in per_window], dtype=int)
    if int((N_k == 0).sum()) > 0:
        empty = [k for k in range(K) if N_k[k] == 0]
        raise ValueError(f"independent_reduce_leg: {leg_dir}: windows {empty} have zero samples — "
                         f"MBAR needs samples from every state")

    N_total = int(N_k.sum())
    u_kn = np.zeros((K, N_total), dtype=float)
    col = 0
    for k in range(K):
        for s in per_window[k]:
            for j in range(K):
                u_kn[j, col] = s[j]
            col += 1

    RT = _RT_PER_K * temperature_K
    mbar = MBAR(u_kn, N_k)
    res = mbar.compute_free_energy_differences()
    dg = RT * float(res["Delta_f"][0, K - 1])
    se = RT * float(res["dDelta_f"][0, K - 1])
    return dg, se


def _import_primary_reduce():
    """Import nr4a3_abfe.reduce_leg (the PRIMARY reducer). Ensures this file's dir is importable."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    from nr4a3_abfe import reduce_leg
    return reduce_leg


def compare_reducers(leg_dir, temperature_K=300.0, tol=0.05):
    """Run BOTH the primary (nr4a3_abfe.reduce_leg) and this independent reducer on the SAME leg data and
    report whether they agree. Returns:
        {"primary": {"dg", "se"}, "independent": {"dg", "se"}, "abs_diff", "agree", "tol"}
    `agree` is |primary.dg − independent.dg| ≤ tol (kcal/mol). On the same data the two should be numerically
    near-identical; tol allows only for MBAR solver-config differences (the primary tries robust fallbacks)."""
    reduce_leg = _import_primary_reduce()
    p_dg, p_se = reduce_leg(leg_dir, temperature_K=temperature_K)
    i_dg, i_se = independent_reduce_leg(leg_dir, temperature_K=temperature_K)
    abs_diff = abs(p_dg - i_dg)
    return {"primary": {"dg": p_dg, "se": p_se},
            "independent": {"dg": i_dg, "se": i_se},
            "abs_diff": abs_diff, "agree": abs_diff <= tol, "tol": tol}


def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="independent MBAR reduction cross-check (reviewer §2.6/§7)")
    ap.add_argument("--leg-dir", required=True, help="dir holding window_XX.jsonl")
    ap.add_argument("--temperature-k", type=float, default=300.0)
    ap.add_argument("--compare", action="store_true", help="run BOTH reducers and report agreement")
    ap.add_argument("--tol", type=float, default=0.05)
    a = ap.parse_args()
    if a.compare:
        out = compare_reducers(a.leg_dir, temperature_K=a.temperature_k, tol=a.tol)
        print(f"[abfe-xcheck] primary ΔG = {out['primary']['dg']:+.3f} ± {out['primary']['se']:.3f} | "
              f"independent ΔG = {out['independent']['dg']:+.3f} ± {out['independent']['se']:.3f} | "
              f"|Δ| = {out['abs_diff']:.4f} kcal/mol | agree(≤{a.tol}) = {out['agree']}")
    else:
        dg, se = independent_reduce_leg(a.leg_dir, temperature_K=a.temperature_k)
        print(f"[abfe-xcheck] independent ΔG = {dg:+.3f} ± {se:.3f} kcal/mol")


if __name__ == "__main__":
    _cli()
