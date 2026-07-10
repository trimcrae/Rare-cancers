#!/usr/bin/env python3
"""PHASE 1 of the metad convergence re-strengthening plan
(research/modalities/nr4a3-metad-convergence-plan.md).

Find the TRUE slow collective variable(s) of NR4A3 pocket opening from the EXISTING trajectories, to test the
round-6 reviewer's leading hypothesis: that Rg is an incomplete reaction coordinate (its only orthogonality
check, the gate distance, is 0.94-0.96 correlated with it, so it cannot see a hidden slow mode).

Method: featurize the pooled metad + release trajectories (pocket-lining Cα pairwise distances, gate-residue
χ1 dihedrals, pocket-lining SASA, and the Rg CV itself), run **TICA** (time-lagged independent component
analysis; deeptime) to extract the slowest modes, and report (i) the implied timescales, (ii) the Pearson
correlation of the slowest independent component (IC1) with Rg — the decisive number: |r|~1 means Rg already
captures the slow mode; |r| well below 1 means there IS a hidden slow coordinate and biasing Rg alone is the
convergence problem. deep-TICA (a small NN featurization) is an optional richer variant.

This module keeps the PURE numeric core (pearson, implied_timescales, redundancy_verdict, dihedral_sincos)
free of mdtraj/deeptime so it is unit-tested in CI; the trajectory featurization + TICA fit run in the
SageMaker job (entry_slow_cv.py), where mdtraj + deeptime are installed.
"""
from __future__ import annotations

import math


# ------------------------- PURE, unit-tested core (numpy only) -------------------------

def pearson(x, y):
    """Pearson correlation r of two 1-D sequences. Pure (numpy)."""
    import numpy as np
    x = np.asarray(x, float); y = np.asarray(y, float)
    if x.size < 2 or y.size < 2 or x.size != y.size:
        raise ValueError("pearson needs two equal-length sequences of length >= 2")
    xm, ym = x - x.mean(), y - y.mean()
    denom = math.sqrt(float((xm * xm).sum()) * float((ym * ym).sum()))
    return 0.0 if denom == 0.0 else float((xm * ym).sum() / denom)


def implied_timescales(eigvals, lag_frames, dt_ns):
    """Convert TICA/VAMP eigenvalues λ (0<λ<1) at a given lag into implied timescales t = -lag/ln(λ),
    returned in ns. λ<=0 or >=1 -> None (undefined). Pure."""
    out = []
    tau = lag_frames * dt_ns
    for lam in eigvals:
        if lam is None or lam <= 0.0 or lam >= 1.0:
            out.append(None)
        else:
            out.append(float(-tau / math.log(lam)))
    return out


def redundancy_verdict(corr_ic1_rg, redundant_above=0.9, informative_below=0.7):
    """Classify whether Rg already captures the slowest mode, from |corr(IC1, Rg)|. Pure.
    'redundant'  -> Rg IS the slow mode (biasing it is fine; convergence is a sampling/heterogeneity issue).
    'partial'    -> Rg captures much but not all of the slow mode.
    'hidden_mode'-> a slow coordinate NOT captured by Rg exists (bias a better CV in Phase 2)."""
    a = abs(corr_ic1_rg)
    if a >= redundant_above:
        return "redundant"
    if a <= informative_below:
        return "hidden_mode"
    return "partial"


def dihedral_sincos(values_rad):
    """Map angles (radians) to (sin, cos) pairs so TICA sees a continuous, periodicity-safe feature. Pure."""
    import numpy as np
    v = np.asarray(values_rad, float)
    return np.stack([np.sin(v), np.cos(v)], axis=-1).reshape(v.shape[0], -1)


# ------------------------- trajectory featurization + TICA (run in the job) -------------------------

def featurize_trajectory(traj, lining_resseqs, gate_resseqs):
    """Build the feature matrix (n_frames x n_features) for one mdtraj trajectory:
      - pairwise Cα distances among the pocket-lining residues (the pocket's shape),
      - sin/cos of χ1 for the gate residues (rotameric gating),
      - SASA of the lining residues (solvent exposure / dewetting proxy),
      - the Rg of the lining Cα (the current CV), appended LAST so its column index is known.
    Returns (features, rg_series). Uses mdtraj + numpy (job only)."""
    import numpy as np
    import mdtraj as md
    top = traj.topology

    def ca_indices(resseqs):
        idx = []
        for rs in resseqs:
            sel = top.select(f"resSeq {int(rs)} and name CA")
            if len(sel):
                idx.append(int(sel[0]))
        return idx

    ca = ca_indices(lining_resseqs)
    # pairwise Cα distances among lining residues
    pairs = [(ca[i], ca[j]) for i in range(len(ca)) for j in range(i + 1, len(ca))]
    dists = md.compute_distances(traj, pairs) if pairs else np.zeros((traj.n_frames, 0))

    # χ1 (sin/cos) for gate residues that have it
    chi1_idx, _ = md.compute_chi1(traj)
    # keep only χ1 whose residue is in the gate set
    gate = set(int(g) for g in gate_resseqs)
    keep = [k for k, quad in enumerate(chi1_idx)
            if top.atom(int(quad[0])).residue.resSeq in gate]
    if keep:
        _, chi1 = md.compute_chi1(traj)
        chi1 = chi1[:, keep]
        chi = dihedral_sincos_2d(chi1, np)
    else:
        chi = np.zeros((traj.n_frames, 0))

    # SASA of the lining residues (sum over their atoms)
    try:
        sasa_res = md.shrake_rupley(traj, mode="residue")
        res_index = {top.residue(r).resSeq: r for r in range(top.n_residues)}
        cols = [res_index[int(rs)] for rs in lining_resseqs if int(rs) in res_index]
        sasa = sasa_res[:, cols].sum(axis=1, keepdims=True) if cols else np.zeros((traj.n_frames, 1))
    except Exception:
        sasa = np.zeros((traj.n_frames, 1))

    # Rg of the lining Cα (the current CV) — appended last
    if ca:
        sub = traj.atom_slice(ca)
        rg = md.compute_rg(sub)
    else:
        rg = md.compute_rg(traj)
    rg = np.asarray(rg, float).reshape(-1, 1)

    feats = np.concatenate([dists, chi, sasa, rg], axis=1)
    return feats, rg.reshape(-1)


def dihedral_sincos_2d(chi1_2d, np):
    """sin/cos expansion for a (n_frames x n_dihedrals) angle array -> (n_frames x 2*n_dihedrals)."""
    return np.concatenate([np.sin(chi1_2d), np.cos(chi1_2d)], axis=1)


def run_tica(features, lag_frames, n_components=5):
    """Fit TICA (deeptime) on one or MORE trajectories. `features` may be a single (n_frames x n_feat) array
    or a LIST of such arrays (one per trajectory; deeptime estimates the time-lagged covariance across the
    list without stitching frames across trajectory boundaries). Returns dict with eigenvalues, a per-trajectory
    projection LIST (each n_frames x n_components), and n_components. Job only (deeptime)."""
    from deeptime.decomposition import TICA
    import numpy as np
    data = features if isinstance(features, list) else [features]
    data = [np.asarray(f, float) for f in data]
    est = TICA(lagtime=int(lag_frames), dim=int(n_components))
    model = est.fit_fetch(data)                                   # list of trajectories, not stacked
    proj = [np.asarray(model.transform(f)) for f in data]         # project each trajectory separately
    eig = getattr(model, "singular_values", None)
    if eig is None:
        eig = getattr(model, "eigenvalues", None)
    return {"eigenvalues": [float(v) for v in (list(eig) if eig is not None else [])],
            "projection": proj, "n_components": int(n_components)}


if __name__ == "__main__":  # tiny smoke of the pure core
    assert abs(pearson([1, 2, 3], [2, 4, 6]) - 1.0) < 1e-9
    assert redundancy_verdict(0.95) == "redundant"
    assert redundancy_verdict(0.5) == "hidden_mode"
    print("nr4a3_slow_cv pure-core smoke OK")
