#!/usr/bin/env python3
"""
Convergence + orthogonal-CV analysis of the NR4A3 LBD well-tempered metadynamics (reviewer Major
Comment 5 / review-response §3 P1: "the cryptic-pocket evidence rests on a SINGLE permissive CV
(Rg of Pocket-5 CAs), ONE metad realization, no convergence analysis, and no orthogonal coordinate").

This module answers that critique with four post-processing readouts, each backed by a PURE,
stdlib-only, unit-tested function so the logic is verifiable in CI without a GPU / mdtraj / PLUMED:

  (a) ORTHOGONAL pocket-opening coordinate — a pocket-mouth GATE DISTANCE: the separation between the
      centroids of two clusters of Pocket-5 lining CAs that sit on OPPOSITE walls of the cavity mouth
      (GATE_GROUP_A vs GATE_GROUP_B). Rg measures the overall spread of all 10 lining CAs; the gate
      distance is a DIFFERENT geometric projection (one specific inter-wall opening), so agreement
      between "Rg rises" and "gate widens" is corroboration from a second descriptor, not the same
      number twice. Pure geometry (centroid + distance), so no fpocket/mdpocket binary is required;
      mdpocket volume is still run best-effort by the runner as an additional volumetric orthogonal.

  (b) TIME-BLOCK CONVERGENCE of F(Rg): reconstruct the free-energy profile from the HILLS deposited up
      to 10/20/30/... ns (a pure well-tempered `sum_hills`), then quantify block-to-block change
      (max / mean / RMSD of |ΔF| over the interpretable region, each block re-zeroed at its basin).
      A shrinking block-to-block difference is the standard metadynamics convergence signature.

  (c) RECROSSINGS: how many times the CV traverses a closed<->open boundary and how many separate
      excursions it makes into the druggable Rg window — i.e. is the sampling DIFFUSIVE (many
      recrossings = a well-explored, converged surface) or a single one-way push (weak)?

  (d) REWEIGHTED 2D view F(Rg, gate): last-bias (exp(+V/kT)) reweighting of the biased frames onto the
      2D (Rg, orthogonal-gate) plane, so the opened state can be located in BOTH coordinates at once.

The PURE functions (parse_hills/parse_colvar/reconstruct_fes/block_fes/fes_difference/
count_boundary_crossings/count_region_visits/reweight_2d/centroid/distance/gate_distance_series/
match_series_by_time) take plain numbers and lists — no I/O, no numpy, no mdtraj — and are unit-tested
in tests/test_metad_analysis.py. The runner main() (mdtraj/matplotlib, guarded imports) wires them to
real COLVAR/HILLS/trajectory files for the cheap CPU follow-up job (entry_metad_analysis.py).

Well-tempered reconstruction note: PLUMED's HILLS stores the ACTUAL (already down-scaled) deposited
Gaussian heights, so the bias is V(s)=Σ h_i G_i and the free energy is F(s) = -(γ/(γ-1))·V(s) (+const),
exactly what `plumed sum_hills` computes. `reconstruct_fes` reproduces that so a per-block profile can
be built from a HILLS slice without shelling out to PLUMED.
"""
import json
import math
import os
import sys

KJ_PER_KCAL = 4.184
KB_KJ = 0.00831446261815324           # Boltzmann constant, kJ/mol/K

# NR4A3 Pocket-5 lining residues (AF2/UniProt numbering) — the same set the metad CV uses. The gate
# splits them into two opposite-wall clusters; the gate distance across the mouth is the orthogonal CV.
# GROUP_A = the H4/H5-side cluster (low resnums), GROUP_B = the H11/H12-side cluster (high resnums).
GATE_GROUP_A = [406, 407, 410, 411, 412]
GATE_GROUP_B = [481, 484, 485, 531, 534]

# The metad CV residues (Rg of these CAs) — imported lazily by the runner from nr4a3_metad, restated
# here only as the default for pure helpers/tests that need the full lining set.
CV_RESIDUES = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]

NS_PER_FRAME = 0.05                   # DCDReporter: 25000 steps * 2 fs = 50 ps (matches nr4a3_mdpocket)
PS_PER_NS = 1000.0


# --------------------------------------------------------------------------------------------------
# Pure parsers (stdlib only)
# --------------------------------------------------------------------------------------------------
def parse_hills(path):
    """Read a PLUMED METAD HILLS file -> list of {time, center, sigma, height, biasfactor} (one CV).

    HILLS columns for a 1-D CV are `time  <cv>  sigma_<cv>  height  biasf`. Comment/blank lines
    (starting `#`) are skipped. Missing/short lines are ignored (fail-soft on a truncated tail — a
    spot kill can leave a half-written final line)."""
    out = []
    for line in _iter_lines(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        f = s.split()
        try:
            rec = {"time": float(f[0]), "center": float(f[1]), "sigma": float(f[2]),
                   "height": float(f[3])}
            rec["biasfactor"] = float(f[4]) if len(f) > 4 else 0.0
        except (ValueError, IndexError):
            continue
        out.append(rec)
    return out


def parse_colvar(path, cv_col=1, bias_col=2):
    """Read a PLUMED COLVAR file -> (times, cv_values, bias_values) as three parallel lists.

    The metad run PRINTs `time  rg  metad.bias` (cv_col=1, bias_col=2). Robust to comment/blank lines
    and a truncated final row. Rows missing the requested columns are skipped."""
    times, cvs, biases = [], [], []
    for line in _iter_lines(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        f = s.split()
        try:
            t = float(f[0]); c = float(f[cv_col]); b = float(f[bias_col])
        except (ValueError, IndexError):
            continue
        times.append(t); cvs.append(c); biases.append(b)
    return times, cvs, biases


def _iter_lines(path):
    with open(path) as fh:
        for line in fh:
            yield line


# --------------------------------------------------------------------------------------------------
# (b) F(Rg) reconstruction + time-block convergence (pure)
# --------------------------------------------------------------------------------------------------
def reconstruct_fes(hills, grid_min, grid_max, grid_bin, biasfactor=None, upto_time=None):
    """Pure well-tempered `sum_hills`: F(Rg) = -(γ/(γ-1))·Σ_i h_i·exp(-(Rg-c_i)²/(2σ_i²)), zeroed at
    its minimum, on a uniform grid of (grid_bin+1) points in [grid_min, grid_max].

    hills: list from parse_hills. biasfactor: γ; if None, taken from the first hill's `biasfactor`
    column (0/absent -> non-tempered, factor 1). upto_time: include only hills with time <= this
    (PLUMED time units, ps) -> the profile as it stood at that block boundary. Returns [(rg, F_kJ)]
    or [] if no hills qualify."""
    hs = hills if upto_time is None else [h for h in hills if h["time"] <= upto_time]
    if not hs:
        return []
    if biasfactor is None:
        biasfactor = hs[0].get("biasfactor", 0.0)
    n = grid_bin + 1
    step = (grid_max - grid_min) / grid_bin
    grid = [grid_min + i * step for i in range(n)]
    bias = [0.0] * n
    for h in hs:
        c, sig, ht = h["center"], h["sigma"], h["height"]
        inv2s2 = 1.0 / (2.0 * sig * sig)
        for i in range(n):
            d = grid[i] - c
            bias[i] += ht * math.exp(-d * d * inv2s2)
    factor = biasfactor / (biasfactor - 1.0) if biasfactor and biasfactor > 1.0 else 1.0
    fe = [-factor * v for v in bias]
    fmin = min(fe)
    return [(grid[i], fe[i] - fmin) for i in range(n)]


def block_fes(hills, block_ns, grid_min, grid_max, grid_bin, biasfactor=None,
              ns_per_time_unit=1.0 / PS_PER_NS):
    """{block_end_ns: F(Rg)} for cumulative blocks at block_ns, 2*block_ns, ... up to the last hill.

    ns_per_time_unit converts the HILLS `time` column to ns (PLUMED here uses ps -> 1/1000). The final
    (full-length) block is always included even if it isn't a clean multiple of block_ns."""
    if not hills:
        return {}
    t_last_ns = max(h["time"] for h in hills) * ns_per_time_unit
    out = {}
    k = 1
    while k * block_ns < t_last_ns - 1e-9:
        end_ns = k * block_ns
        fes = reconstruct_fes(hills, grid_min, grid_max, grid_bin, biasfactor,
                              upto_time=end_ns / ns_per_time_unit)
        if fes:
            out[round(end_ns, 3)] = fes
        k += 1
    out[round(t_last_ns, 3)] = reconstruct_fes(hills, grid_min, grid_max, grid_bin, biasfactor)
    return out


def fes_difference(fes_a, fes_b, region=None):
    """Block-to-block change between two F(Rg) profiles on the SAME grid. Each profile is re-zeroed to
    its own minimum over `region` (a (rg_lo, rg_hi) tuple; None = whole grid) before differencing, so
    the metric is the change in SHAPE, not an overall offset. Returns {max_dF_kJ, mean_dF_kJ, rmsd_kJ,
    n_points}. Points are paired by index (identical grids); the shorter length wins if they differ."""
    n = min(len(fes_a), len(fes_b))
    if n == 0:
        return {"max_dF_kJ": None, "mean_dF_kJ": None, "rmsd_kJ": None, "n_points": 0}

    def _in_region(rg):
        return region is None or (region[0] <= rg <= region[1])

    idx = [i for i in range(n) if _in_region(fes_a[i][0]) and _in_region(fes_b[i][0])]
    if not idx:
        return {"max_dF_kJ": None, "mean_dF_kJ": None, "rmsd_kJ": None, "n_points": 0}
    amin = min(fes_a[i][1] for i in idx)
    bmin = min(fes_b[i][1] for i in idx)
    diffs = [abs((fes_a[i][1] - amin) - (fes_b[i][1] - bmin)) for i in idx]
    mean = sum(diffs) / len(diffs)
    rmsd = math.sqrt(sum(d * d for d in diffs) / len(diffs))
    return {"max_dF_kJ": round(max(diffs), 3), "mean_dF_kJ": round(mean, 3),
            "rmsd_kJ": round(rmsd, 3), "n_points": len(idx)}


def block_convergence(blocks, region=None):
    """Consecutive-block differences from a {end_ns: fes} dict (block_fes output). Returns a list of
    {from_ns, to_ns, ...fes_difference...} ordered by time — the quantitative convergence trace the
    reviewer asked for (block-to-block |ΔF| should shrink toward zero)."""
    ends = sorted(blocks)
    out = []
    for a, b in zip(ends[:-1], ends[1:]):
        d = fes_difference(blocks[a], blocks[b], region=region)
        d.update({"from_ns": a, "to_ns": b})
        out.append(d)
    return out


# --------------------------------------------------------------------------------------------------
# (c) recrossings / transitions (pure)
# --------------------------------------------------------------------------------------------------
def count_boundary_crossings(series, boundary, deadband=0.0):
    """Number of times the CV crosses `boundary` (closed<->open transitions). With deadband>0 a
    hysteresis band [boundary-deadband, boundary+deadband] filters thermal chatter: a crossing counts
    only once the CV moves from decisively below (< boundary-deadband) to decisively above
    (> boundary+deadband) or vice-versa. Returns the integer count."""
    lo, hi = boundary - deadband, boundary + deadband
    state = None            # "below" / "above"
    crossings = 0
    for x in series:
        if x < lo:
            new = "below"
        elif x > hi:
            new = "above"
        else:
            continue        # inside the deadband: hold current state
        if state is not None and new != state:
            crossings += 1
        state = new
    return crossings


def count_region_visits(series, lo, hi):
    """Number of separate excursions into the window [lo, hi] (a 'visit' begins when the CV enters
    from outside and ends when it leaves). Also returns the fraction of samples inside. Returns
    {visits, frac_inside, n}."""
    visits, inside_prev, inside_count = 0, False, 0
    for x in series:
        inside = lo <= x <= hi
        if inside and not inside_prev:
            visits += 1
        inside_count += 1 if inside else 0
        inside_prev = inside
    n = len(series)
    return {"visits": visits, "frac_inside": round(inside_count / n, 4) if n else 0.0, "n": n}


# --------------------------------------------------------------------------------------------------
# (a) orthogonal gate-distance geometry (pure)
# --------------------------------------------------------------------------------------------------
def centroid(points):
    """Mean (x, y, z) of a non-empty list of 3-tuples/lists."""
    n = len(points)
    if n == 0:
        raise ValueError("centroid of empty point set")
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    sz = sum(p[2] for p in points)
    return (sx / n, sy / n, sz / n)


def distance(a, b):
    """Euclidean distance between two 3-tuples."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def gate_distance_series(group_a_frames, group_b_frames):
    """Per-frame centroid-to-centroid distance between two CA clusters (the pocket-mouth gate).

    group_a_frames / group_b_frames: parallel lists, one entry per frame, each a list of CA xyz
    3-tuples for that group in that frame. Returns [gate_distance_per_frame]. Raises on a frame count
    mismatch (fail-loud rather than silently truncating)."""
    if len(group_a_frames) != len(group_b_frames):
        raise ValueError(f"gate group frame counts differ: {len(group_a_frames)} vs "
                         f"{len(group_b_frames)}")
    return [distance(centroid(a), centroid(b))
            for a, b in zip(group_a_frames, group_b_frames)]


# --------------------------------------------------------------------------------------------------
# (d) time-matching + 2D last-bias reweighting (pure)
# --------------------------------------------------------------------------------------------------
def match_series_by_time(target_times, ref_times, ref_values):
    """For each t in target_times, the ref_value at the nearest ref_time. Used to attach the COLVAR
    bias (printed every 1 ps) to trajectory frames (every 50 ps). ref_times must be sorted ascending;
    returns a list aligned with target_times. Empty ref -> all None."""
    import bisect
    if not ref_times:
        return [None] * len(target_times)
    out = []
    for t in target_times:
        j = bisect.bisect_left(ref_times, t)
        if j <= 0:
            out.append(ref_values[0])
        elif j >= len(ref_times):
            out.append(ref_values[-1])
        else:
            out.append(ref_values[j] if (ref_times[j] - t) < (t - ref_times[j - 1])
                       else ref_values[j - 1])
    return out


def reweight_2d(samples, kT, x_bins, y_bins, x_range=None, y_range=None):
    """Last-bias reweighted 2D free energy F(x, y) from biased samples.

    samples: list of (x, y, bias_kJ). Weight w = exp(+bias/kT) (Tiwary-Parrinello last-bias estimator).
    Bins the weighted samples on an x_bins × y_bins grid; F = -kT·ln(Σw per cell), zeroed at the global
    minimum. Empty cells -> None. Returns {F (row-major y then x), x_edges, y_edges, x_bins, y_bins,
    kT, n_samples}. Rows missing a bias are dropped."""
    pts = [(x, y, b) for (x, y, b) in samples if b is not None]
    if not pts:
        return {"F": [], "x_edges": [], "y_edges": [], "x_bins": x_bins, "y_bins": y_bins,
                "kT": kT, "n_samples": 0}
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x_lo, x_hi = x_range if x_range else (min(xs), max(xs))
    y_lo, y_hi = y_range if y_range else (min(ys), max(ys))
    x_lo, x_hi = _pad_range(x_lo, x_hi)
    y_lo, y_hi = _pad_range(y_lo, y_hi)
    xw = (x_hi - x_lo) / x_bins
    yw = (y_hi - y_lo) / y_bins
    weight = [[0.0] * x_bins for _ in range(y_bins)]
    for x, y, b in pts:
        ix = min(x_bins - 1, max(0, int((x - x_lo) / xw)))
        iy = min(y_bins - 1, max(0, int((y - y_lo) / yw)))
        weight[iy][ix] += math.exp(b / kT)
    fe = [[(-kT * math.log(w) if w > 0 else None) for w in row] for row in weight]
    finite = [v for row in fe for v in row if v is not None]
    fmin = min(finite) if finite else 0.0
    fe = [[(None if v is None else round(v - fmin, 3)) for v in row] for row in fe]
    x_edges = [round(x_lo + i * xw, 4) for i in range(x_bins + 1)]
    y_edges = [round(y_lo + i * yw, 4) for i in range(y_bins + 1)]
    return {"F": fe, "x_edges": x_edges, "y_edges": y_edges, "x_bins": x_bins, "y_bins": y_bins,
            "kT": kT, "n_samples": len(pts)}


def _pad_range(lo, hi, frac=0.02):
    """Nudge a degenerate/edge range so binning is well-defined (lo<hi with a hair of padding)."""
    if hi <= lo:
        hi = lo + 1.0
    pad = (hi - lo) * frac
    return lo - pad, hi + pad


# --------------------------------------------------------------------------------------------------
# Runner (mdtraj / matplotlib — guarded imports; NOT part of the pure, tested surface)
# --------------------------------------------------------------------------------------------------
def _resolve_ca_indices(prot, residues, lbd_first):
    """CA atom indices (0-based, into prot) for `residues` (AF2 numbering), via the tested resolver."""
    import residue_map as rm
    resseqs = [r.resSeq for r in prot.topology.residues]
    positions, numbering = rm.resolve_positions(resseqs, residues, lbd_first)
    residues_list = list(prot.topology.residues)
    idx = []
    for i in positions:
        ca = next((a.index for a in residues_list[i].atoms if a.name == "CA"), None)
        if ca is not None:
            idx.append(ca)
    return idx, numbering


def main():
    in_dir = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
    out_dir = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")
    struct_dir = os.environ.get("STRUCTURE_DIR", in_dir)
    dcd_name = os.environ.get("DCD_NAME", "nr4a3-lbd-metad.dcd")
    block_ns = float(os.environ.get("BLOCK_NS", "10"))
    os.makedirs(out_dir, exist_ok=True)

    # metad params (grid + biasfactor + temperature + CV residues) straight from the run's own module,
    # so the reconstruction grid matches the HILLS exactly and nothing is hand-transcribed.
    import nr4a3_metad as M
    lbd_first = M.LBD_FIRST
    metad = M.METAD
    kT = KB_KJ * metad["temp"]

    hills_path = os.path.join(in_dir, "HILLS")
    colvar_path = os.path.join(in_dir, "COLVAR")
    top = os.path.join(struct_dir, "nr4a3-lbd-solvated.pdb")
    dcd = os.path.join(in_dir, dcd_name)

    summary = {"trajectory": dcd_name, "block_ns": block_ns,
               "orthogonal_cv": "pocket-mouth gate distance (centroid CA {A} <-> {B})".format(
                   A=GATE_GROUP_A, B=GATE_GROUP_B),
               "gate_group_a": GATE_GROUP_A, "gate_group_b": GATE_GROUP_B,
               "metad_params": metad}

    # ---- (b) time-block convergence of F(Rg) from HILLS -----------------------------------------
    if os.path.exists(hills_path):
        hills = parse_hills(hills_path)
        blocks = block_fes(hills, block_ns, metad["grid_min"], metad["grid_max"], metad["grid_bin"],
                           biasfactor=metad["biasfactor"])
        # interpretable region: inside the walls, excluding the sum_hills-referenced edges
        region = (metad["lower_wall"], metad["upper_wall"])
        conv = block_convergence(blocks, region=region)
        summary["convergence"] = {
            "n_hills": len(hills),
            "block_end_ns": sorted(blocks),
            "region_rg_nm": list(region),
            "block_to_block": conv,
            "final_block_to_block_max_dF_kJ": conv[-1]["max_dF_kJ"] if conv else None,
            "note": ("Each block re-zeroed at its basin over the wall region before differencing; a "
                     "shrinking block-to-block |ΔF| is the metadynamics convergence signature."),
        }
        # persist the per-block profiles for plotting/figure reuse
        with open(os.path.join(out_dir, "fes_blocks.json"), "w") as fh:
            json.dump({str(k): v for k, v in blocks.items()}, fh)
        _plot_blocks(blocks, out_dir)
    else:
        summary["convergence"] = {"ran": False, "reason": f"no HILLS at {hills_path}"}

    # ---- (c) recrossings from the COLVAR Rg trace -----------------------------------------------
    if os.path.exists(colvar_path):
        _times, rg_series, bias_series = parse_colvar(colvar_path)
        # boundary midway between the closed basin (~0.48) and the open frontier; druggable window
        boundary = float(os.environ.get("RG_BOUNDARY", "0.90"))
        drug_lo = float(os.environ.get("DRUG_RG_LO", "0.70"))
        drug_hi = float(os.environ.get("DRUG_RG_HI", "1.10"))
        summary["recrossings"] = {
            "n_colvar_samples": len(rg_series),
            "boundary_rg_nm": boundary,
            "closed_open_crossings": count_boundary_crossings(rg_series, boundary,
                                                              deadband=5 * metad["sigma"]),
            "druggable_window_rg_nm": [drug_lo, drug_hi],
            "druggable_window_visits": count_region_visits(rg_series, drug_lo, drug_hi),
            "note": ("closed<->open crossings use a 5σ hysteresis deadband; many crossings / repeat "
                     "druggable-window visits = diffusive, well-explored sampling."),
        }
    else:
        summary["recrossings"] = {"ran": False, "reason": f"no COLVAR at {colvar_path}"}
        rg_series = bias_series = None

    # ---- (a)+(d) orthogonal gate distance per frame + 2D reweight -------------------------------
    summary["orthogonal"] = _orthogonal_and_2d(top, dcd, colvar_path, lbd_first, kT, out_dir, summary)

    # ---- mdpocket volumetric orthogonal (best-effort) -------------------------------------------
    summary["mdpocket_volume"] = _mdpocket_best_effort(top, dcd, out_dir)

    with open(os.path.join(out_dir, "metad_analysis_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    _print_headline(summary)


def _orthogonal_and_2d(top, dcd, colvar_path, lbd_first, kT, out_dir, summary):
    try:
        import numpy as np
        import mdtraj as md
    except ImportError as e:  # noqa: BLE001
        return {"ran": False, "reason": f"needs mdtraj+numpy: {e}"}
    if not (os.path.exists(top) and os.path.exists(dcd)):
        return {"ran": False, "reason": f"missing {top} or {dcd}"}
    t = md.load(dcd, top=top)
    prot = t.atom_slice(t.topology.select("protein"))
    a_idx, _ = _resolve_ca_indices(prot, GATE_GROUP_A, lbd_first)
    b_idx, _ = _resolve_ca_indices(prot, GATE_GROUP_B, lbd_first)
    cv_idx, _ = _resolve_ca_indices(prot, CV_RESIDUES, lbd_first)
    if len(a_idx) < 2 or len(b_idx) < 2 or len(cv_idx) < 3:
        return {"ran": False, "reason": "could not resolve gate/CV CA atoms on the trajectory"}

    n = prot.n_frames
    a_frames = [[tuple(prot.xyz[fi, ai, :]) for ai in a_idx] for fi in range(n)]
    b_frames = [[tuple(prot.xyz[fi, bi, :]) for bi in b_idx] for fi in range(n)]
    gate = gate_distance_series(a_frames, b_frames)
    # per-frame Rg of the metad CV CAs (same coordinate as fes.dat), pure geometry
    sub = prot.xyz[:, cv_idx, :]
    c = sub.mean(axis=1, keepdims=True)
    rg_frame = np.sqrt(((sub - c) ** 2).sum(axis=2).mean(axis=1))
    frame_times_ps = [fi * NS_PER_FRAME * PS_PER_NS for fi in range(n)]

    np.save(os.path.join(out_dir, "gate_distance_nm.npy"), np.array(gate))
    np.save(os.path.join(out_dir, "cv_rg_per_frame_nm.npy"), rg_frame)

    corr = _pearson([float(x) for x in rg_frame], gate)
    out = {"ran": True, "n_frames": n,
           "gate_distance_nm": {"min": round(min(gate), 4), "max": round(max(gate), 4),
                                "mean": round(sum(gate) / n, 4)},
           "corr_rg_gate": None if corr is None else round(corr, 3),
           "corr_note": ("Pearson r of Rg vs the gate distance across frames. A clear positive r means "
                         "the orthogonal descriptor CORROBORATES opening (both grow together) while "
                         "being a distinct projection; |r|~1 would mean it is redundant with Rg.")}

    # (d) 2D last-bias reweight onto (Rg, gate), if the COLVAR bias is available
    if os.path.exists(colvar_path):
        _ct, _crg, cbias = parse_colvar(colvar_path)
        frame_bias = match_series_by_time(frame_times_ps, _ct, cbias)
        samples = [(float(rg_frame[i]), gate[i], frame_bias[i]) for i in range(n)]
        rw = reweight_2d(samples, kT, x_bins=int(os.environ.get("FES2D_XBINS", "40")),
                         y_bins=int(os.environ.get("FES2D_YBINS", "40")))
        with open(os.path.join(out_dir, "fes2d_rg_gate.json"), "w") as fh:
            json.dump(rw, fh)
        _plot_fes2d(rw, out_dir)
        out["reweight_2d"] = {"ran": rw["n_samples"] > 0, "n_samples": rw["n_samples"],
                              "x_bins": rw["x_bins"], "y_bins": rw["y_bins"],
                              "note": ("F(Rg, gate) via last-bias exp(+V/kT) reweighting of the biased "
                                       "frames; locates the opened state in BOTH coordinates. Written "
                                       "to fes2d_rg_gate.json + fes2d_rg_gate.png.")}
    else:
        out["reweight_2d"] = {"ran": False, "reason": "no COLVAR bias for reweighting"}
    return out


def _pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def _mdpocket_best_effort(top, dcd, out_dir):
    import shutil
    import subprocess
    if not shutil.which("mdpocket"):
        return {"ran": False, "reason": "mdpocket binary not on PATH"}
    if not (os.path.exists(top) and os.path.exists(dcd)):
        return {"ran": False, "reason": "missing trajectory/topology"}
    try:
        r = subprocess.run(
            ["mdpocket", "--trajectory_file", dcd, "--trajectory_format", "dcd", "-f", top],
            cwd=out_dir, capture_output=True, text=True, timeout=3600)
        return {"ran": True, "returncode": r.returncode, "stdout_tail": r.stdout[-1500:],
                "note": "mdpocket transient-pocket density grids written to OUTPUT_DIR; a volumetric "
                        "orthogonal to the gate distance."}
    except Exception as e:  # noqa: BLE001
        return {"ran": False, "reason": str(e)}


def _plot_blocks(blocks, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.figure(figsize=(8, 4))
        for end_ns in sorted(blocks):
            fes = blocks[end_ns]
            plt.plot([p[0] for p in fes], [p[1] for p in fes], lw=0.9, label=f"{end_ns:g} ns")
        plt.xlabel("Rg of Pocket-5 CAs (nm)"); plt.ylabel("F (kJ/mol)")
        plt.title("F(Rg) convergence over cumulative metad blocks"); plt.legend(fontsize=7)
        plt.tight_layout(); plt.savefig(os.path.join(out_dir, "fes_convergence.png"), dpi=130)
    except Exception as e:  # noqa: BLE001
        print(f"  block plot skipped: {e}", file=sys.stderr)


def _plot_fes2d(rw, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        F = np.array([[np.nan if v is None else v for v in row] for row in rw["F"]])
        plt.figure(figsize=(6, 5))
        plt.imshow(F, origin="lower", aspect="auto",
                   extent=[rw["x_edges"][0], rw["x_edges"][-1], rw["y_edges"][0], rw["y_edges"][-1]])
        plt.colorbar(label="F (kJ/mol)")
        plt.xlabel("Rg of Pocket-5 CAs (nm)"); plt.ylabel("pocket-mouth gate distance (nm)")
        plt.title("Reweighted F(Rg, gate)")
        plt.tight_layout(); plt.savefig(os.path.join(out_dir, "fes2d_rg_gate.png"), dpi=130)
    except Exception as e:  # noqa: BLE001
        print(f"  2D FES plot skipped: {e}", file=sys.stderr)


def _print_headline(summary):
    c = summary.get("convergence", {})
    r = summary.get("recrossings", {})
    o = summary.get("orthogonal", {})
    print(f"  CONVERGENCE: blocks={c.get('block_end_ns')} final block-to-block max|ΔF|="
          f"{c.get('final_block_to_block_max_dF_kJ')} kJ/mol", flush=True)
    if r.get("closed_open_crossings") is not None:
        print(f"  RECROSSINGS: closed<->open crossings={r.get('closed_open_crossings')}; "
              f"druggable-window visits={(r.get('druggable_window_visits') or {}).get('visits')}",
              flush=True)
    if o.get("ran"):
        print(f"  ORTHOGONAL: gate {o['gate_distance_nm']}; corr(Rg,gate)={o.get('corr_rg_gate')}; "
              f"2D reweight n={o.get('reweight_2d', {}).get('n_samples')}", flush=True)


if __name__ == "__main__":
    main()
