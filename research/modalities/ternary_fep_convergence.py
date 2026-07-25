#!/usr/bin/env python3
"""OpenFE/openmmtools CONVERGENCE ANALYSIS on the committed MultiState .nc (reviewer required change #1, 2026-07-17).

A $0 CPU post-analysis of the RAW sampler trajectory each spot-safe leg commits (`simulation.nc`, written by
rbfe_spot_driver via openmmtools MultiStateReporter). It must run on the seed-0 .nc BEFORE ternary seed-1 is
launched, so a technically-broken leg (poor phase-space overlap, unequilibrated, non-mixing replicas, ligand
escape / collapse) is caught before more GPU spend and before the ΔΔG_coop decision is trusted.

Diagnostics produced per leg (each wrapped so a missing API in a given openmmtools/pymbar version degrades to a
status string instead of crashing the whole analysis):
  * MBAR ΔG end-to-end estimate + error (kT and kcal/mol)
  * MBAR overlap matrix + overlap SCALAR (adjacent-state phase-space overlap; the key RBFE health metric)
  * cumulative FORWARD / REVERSE free-energy time-series (ΔG over increasing fractions of production) — a drift
    between forward and reverse, or a forward/reverse gap outside error, signals non-convergence
  * replica MIXING statistics: state-transition matrix + subdominant eigenvalue (slow-mixing detector) + per-
    replica round-trip count
  * N_eff / statistical inefficiency (equilibration detection: n_equilibration iters, g, effective #samples)
  * structural diagnostics (best-effort, if the checkpoint + mdtraj are present): ligand heavy-atom RMSD vs the
    start (ligand-escape / pose-collapse detector)
  * restraint diagnostics: reported if the system carries restraints (RBFE binding legs here do NOT; noted)

Emits, per leg, a set of boolean HEALTH flags and an overall `technical_failure` that feeds the reducer's
PASS/NO-GO/INDETERMINATE gate (ternary_fep_reduce.calibration_decision(restraint_dominated=...)). Pure analysis —
no MD, no GPU. On CPU with no .nc present it reduces to an honest empty report.
"""
import glob
import json
import math
import os

CKPT = os.environ.get("CKPT_DIR", os.environ.get("OUTPUT_DIR", "/opt/ml/checkpoints"))
IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")

# health thresholds (field-standard-ish; each is decision-relevant, not cosmetic)
OVERLAP_SCALAR_MIN = 0.03      # adjacent-state overlap below this = insufficient phase-space overlap
OVERLAP_BOTTLENECK_MIN = 0.03  # reviewer condition 4: the WEAKEST adjacent-state link (bottleneck) must clear
                               # this — a connected λ-path requires EVERY neighbor pair to overlap, not just a
                               # good scalar average. (We do NOT impose a single universal cutoff on the scalar
                               # alone; connectivity of the whole chain is the real requirement.)
MIX_SUBDOMINANT_MAX = 0.90     # 2nd-largest transition eigenvalue above this = pathologically slow replica mixing
EQUIL_FRACTION_MAX = 0.50      # >50% of iterations spent equilibrating = too little production left
FWD_REV_GAP_MAX_KCAL = 1.0     # |forward - reverse| final ΔG gap above this (kcal) = unconverged
PLATEAU_FULL_HALF_MAX_KCAL = 0.5   # reviewer condition 4: |ΔG(full) - ΔG(final half)| must be <=0.5 (plateau)
QUARTER_BLOCK_MAX_KCAL = 0.5       # reviewer condition 4: |ΔG(3rd quarter) - ΔG(4th quarter)| must be <=0.5
LIG_RMSD_MAX_A = 4.0           # ligand heavy-atom RMSD vs start above this = escape / pose collapse
KT_KCAL = 0.593                # RT at 298 K in kcal/mol (reporting only; MBAR works in kT)


def _find_nc_files():
    """Every committed production simulation.nc under the checkpoint/input trees, keyed by leg tag (parent dir)."""
    out = {}
    for base in (CKPT, IN):
        for f in glob.glob(os.path.join(base, "**", "simulation.nc"), recursive=True):
            tag = os.path.basename(os.path.dirname(f)).replace("_sim_shared", "")
            out.setdefault(tag, f)
    return out


def _overlap(analyzer):
    """MBAR overlap matrix + scalar. pymbar 3 and 4 differ; try both. Overlap scalar = 1 - 2nd-largest eigenvalue
    of the overlap matrix (the Perron eigenvalue is 1); higher = better adjacent-state overlap."""
    # `analyzer.mbar` is a LAZY openmmtools descriptor, not an attribute: touching it builds the MBAR object,
    # which reads the end thermodynamic states, which DESERIALIZES class references out of the .nc. On an
    # OpenFE trajectory that path imports openfe, so a bare getattr can raise ModuleNotFoundError (or any
    # deserialization error) rather than return None — and this function is called OUTSIDE a try in
    # analyze_leg, so it took the whole report down with it (GH run 30155345102). The module docstring promises
    # every diagnostic degrades to a status string; that promise did not hold here. It does now.
    try:
        mbar = getattr(analyzer, "mbar", None) or getattr(analyzer, "_mbar", None)
    except Exception as e:  # noqa: BLE001
        return {"status": "mbar construction failed: %s: %s" % (type(e).__name__, e)}
    if mbar is None:
        return {"status": "no mbar object on analyzer"}
    try:
        ov = mbar.compute_overlap()          # pymbar 4
    except AttributeError:
        ov = mbar.computeOverlap()           # pymbar 3
    if isinstance(ov, dict):
        matrix = ov.get("matrix"); eig = ov.get("eigenvalues"); scalar = ov.get("scalar")
    else:  # pymbar 3 returned (scalar, eigenvalues, matrix)
        scalar, eig, matrix = ov
    try:
        eigs = sorted([float(e) for e in eig], reverse=True)
        scalar = float(scalar) if scalar is not None else (1.0 - eigs[1] if len(eigs) > 1 else None)
    except Exception:  # noqa: BLE001
        eigs = None
    bottleneck = overlap_matrix_bottleneck(matrix)
    return {"status": "ok", "overlap_scalar": scalar,
            "eigenvalues_top": (eigs[:5] if eigs else None),
            "matrix_shape": (list(getattr(matrix, "shape", [])) or None),
            "min_adjacent_overlap": bottleneck.get("min_adjacent_overlap"),
            "bottleneck_pair": bottleneck.get("bottleneck_pair"),
            "connected": bottleneck.get("connected")}


def overlap_matrix_bottleneck(matrix):
    """Reviewer condition 4 — the overlap MATRIX bottleneck, not just the scalar. Return the WEAKEST adjacent
    (i, i+1) overlap and whether every adjacent link clears OVERLAP_BOTTLENECK_MIN (a connected λ-path). A single
    near-zero neighbor pair disconnects the thermodynamic path even when the scalar/average looks acceptable, so
    this — not a universal cutoff on the scalar — is the real connectivity requirement. Pure; unit-tested."""
    # Deliberately PURE PYTHON: this is a min over K-1 pairs, and it used to go through numpy, which meant a
    # worker without numpy silently DISABLED the gate (the ImportError branch returned connected=None). A
    # convergence gate that can be switched off by a missing dependency is a gate you cannot rely on, and this
    # arithmetic never needed numpy — so the dependency, and the failure mode with it, is gone.
    try:
        rows = [list(r) for r in matrix]
        K = len(rows)
        if K < 2 or any(len(r) != K for r in rows):
            return {"min_adjacent_overlap": None, "bottleneck_pair": None, "connected": None,
                    "status": "overlap matrix must be square with K >= 2"}
        # each adjacent link's overlap = min of the two directional overlaps O[i,i+1], O[i+1,i]
        links = [(i, min(float(rows[i][i + 1]), float(rows[i + 1][i]))) for i in range(K - 1)]
        i_min, v_min = min(links, key=lambda t: t[1])
        return {"min_adjacent_overlap": v_min, "bottleneck_pair": [i_min, i_min + 1],
                "connected": bool(v_min >= OVERLAP_BOTTLENECK_MIN)}
    except Exception as e:  # noqa: BLE001
        return {"min_adjacent_overlap": None, "bottleneck_pair": None, "connected": None,
                "status": "bottleneck calc failed: %s" % e}


def _forward_reverse(analyzer, n_points=8):
    """Cumulative forward/reverse ΔG time-series. For fractions f in (0,1], run MBAR on the FIRST f (forward) and
    the LAST f (reverse) of production iterations. Returns the series (kcal/mol) + the final forward/reverse gap.
    Uses the analyzer's cached u_kln/N_k where available; degrades to a status string on any version mismatch."""
    try:
        import numpy as np
        # pull the decorrelated energy matrix the analyzer built for MBAR
        u_ln = getattr(analyzer, "_unbiased_decorrelated_u_ln", None)
        N_l = getattr(analyzer, "_unbiased_decorrelated_N_l", None)
        if u_ln is None or N_l is None:
            # fall back to the reduced potential from the reporter
            return {"status": "forward/reverse needs analyzer u_ln cache (not exposed in this version)"}
        N_l = np.asarray(N_l, dtype=int)
        K = len(N_l)
        f_k = _converged_f_k(analyzer)   # seed each slice solve; see _solve_mbar for why a bare MBAR fails here
        fracs = [i / n_points for i in range(1, n_points + 1)]
        fwd, rev, errs = [], [], []
        for f in fracs:
            for series, store in ((True, fwd), (False, rev)):
                Nsub = np.maximum((N_l * f).astype(int), 1)
                cols, offset = [], 0
                for k in range(K):
                    n = int(N_l[k])
                    idx = (np.arange(offset, offset + n) if series
                           else np.arange(offset + n - int(Nsub[k]), offset + n))
                    cols.append(idx[:int(Nsub[k])] if series else idx)
                    offset += n
                sel = np.concatenate(cols)
                try:
                    store.append(_solve_mbar(u_ln[:, sel], Nsub, f_k) * KT_KCAL)
                except Exception as e:  # noqa: BLE001
                    store.append(None)
                    # Record WHY a point is missing. Silent Nones made an all-null series look like a computed
                    # result with status "ok", which is how this diagnostic reported nothing and still passed.
                    if len(errs) < 3:
                        errs.append("%s: %s" % (type(e).__name__, str(e)[:160]))
        # THE GAP MUST BE TAKEN BELOW f = 1. At f = 1 the forward slice (first 100 % of each state's samples) and
        # the reverse slice (last 100 %) are THE SAME SAMPLES, so |fwd[-1] − rev[-1]| is identically ~0 and a
        # threshold on it can never fire. Use the largest fraction strictly below 1 as the headline gap, and also
        # report the worst gap over all f < 1, which is what actually detects drift/hysteresis.
        pairs = [(f, a, b) for f, a, b in zip(fracs, fwd, rev)
                 if f < 1.0 and a is not None and b is not None]
        gap = abs(pairs[-1][1] - pairs[-1][2]) if pairs else None
        gap_at = pairs[-1][0] if pairs else None
        gap_max = max((abs(a - b) for _, a, b in pairs), default=None)
        trivial = None
        if fwd and rev and fwd[-1] is not None and rev[-1] is not None:
            trivial = abs(fwd[-1] - rev[-1])
        n_ok = sum(1 for v in fwd + rev if v is not None)
        return {"status": ("ok" if n_ok else "no point solved — see slice_errors"),
                "fractions": fracs, "forward_dg_kcal": fwd, "reverse_dg_kcal": rev,
                "n_points_solved": n_ok, "n_points_total": 2 * len(fracs),
                "slice_errors": errs or None,
                "final_forward_reverse_gap_kcal": gap, "gap_taken_at_fraction": gap_at,
                "max_forward_reverse_gap_below_full_kcal": gap_max,
                "gap_at_full_fraction_uninformative": trivial}
    except Exception as e:  # noqa: BLE001
        return {"status": "forward/reverse failed: %s: %s" % (type(e).__name__, e)}


def block_plateau_flags(dg_full, dg_final_half, dg_q3, dg_q4):
    """Pure: reviewer condition 4 dG(t) plateau checks. full-vs-final-half and 3rd-vs-4th-quarter block ΔG must
    each agree within threshold (a flat tail = the estimate has plateaued). None where a block is unavailable."""
    plateau = (None if (dg_full is None or dg_final_half is None)
               else abs(dg_full - dg_final_half) <= PLATEAU_FULL_HALF_MAX_KCAL)
    quarters = (None if (dg_q3 is None or dg_q4 is None)
                else abs(dg_q3 - dg_q4) <= QUARTER_BLOCK_MAX_KCAL)
    return {"full_vs_final_half_delta_kcal": (None if (dg_full is None or dg_final_half is None)
                                              else abs(dg_full - dg_final_half)),
            "q3_vs_q4_delta_kcal": (None if (dg_q3 is None or dg_q4 is None) else abs(dg_q3 - dg_q4)),
            "plateau_full_vs_half_ok": plateau, "quarter_block_ok": quarters}


def _solve_mbar(u_kn, N_k, initial_f_k=None):
    """Build an MBAR on a SUB-SLICE of an already-analysed trajectory and return Delta_f, in kT.

    Why this exists: a bare `MBAR(u_kn, N_k)` on a slice reliably failed on the real valB legs with pymbar's
    `ParameterError: Should have \\sum_n W_nk = 1. Actual column sum for state 0 was 11.94` (K = 12) — the
    self-consistency check on the weight matrix, i.e. the SOLVER did not converge, not a corrupt trajectory.
    openmmtools' own MBAR on the identical data converged fine (ΔG 47.51 ± 0.045 kcal/mol) because it seeds and
    solves differently. The stock error text ends with "This generally indicates the free energies are not
    converged", which reads as a verdict on the physics; on the evidence (full MBAR converged, overlap matrix
    connected at 0.109 min-adjacent) it is a verdict on this solver call. So: seed from the analyser's already
    converged f_k and ask for the robust solver, falling back through older pymbar signatures.
    """
    import numpy as np
    from pymbar import MBAR
    attempts = []
    if initial_f_k is not None:
        attempts.append({"initial_f_k": np.asarray(initial_f_k, dtype=float),
                         "solver_protocol": "robust"})
        attempts.append({"initial_f_k": np.asarray(initial_f_k, dtype=float)})
    attempts.append({"solver_protocol": "robust"})
    attempts.append({})
    last = None
    for kw in attempts:
        try:
            m = MBAR(u_kn, N_k, **kw)
            df = (m.compute_free_energy_differences()["Delta_f"]
                  if hasattr(m, "compute_free_energy_differences") else m.getFreeEnergyDifferences()[0])
            return float(df[0, -1])
        except Exception as e:  # noqa: BLE001  (TypeError = signature; ParameterError = non-convergence)
            last = e
    raise last if last is not None else RuntimeError("MBAR slice solve failed with no exception recorded")


def _slice_indices(N_l, lo_frac, hi_frac):
    """Column indices + per-state counts for the [lo_frac, hi_frac) portion of EACH state's samples."""
    import numpy as np
    N_l = np.asarray(N_l, dtype=int)
    cols, offset, Nsub = [], 0, []
    for k in range(len(N_l)):
        n = int(N_l[k])
        a = offset + int(n * lo_frac)
        b = max(offset + int(n * hi_frac), a + 1)
        cols.append(np.arange(a, min(b, offset + n)))
        Nsub.append(len(cols[-1]))
        offset += n
    return np.concatenate(cols), np.asarray(Nsub, dtype=int)


def _mbar_dg_on_slice(u_ln, N_l, lo_frac, hi_frac, initial_f_k=None):
    """MBAR ΔG (kcal/mol) over the [lo_frac, hi_frac) portion of EACH state's decorrelated samples. Used for the
    block-plateau tail analysis (reviewer condition 4)."""
    sel, Nsub = _slice_indices(N_l, lo_frac, hi_frac)
    return _solve_mbar(u_ln[:, sel], Nsub, initial_f_k) * KT_KCAL


def _converged_f_k(analyzer):
    """The analyser's already-converged per-state free energies (kT), used to SEED every slice MBAR. Returns None
    if unavailable — the slice solves then just run unseeded, as before."""
    try:
        f_ij, _ = analyzer.get_free_energy()
        return [float(x) for x in f_ij[0, :]]
    except Exception:  # noqa: BLE001
        return None


def _block_plateau(analyzer):
    """dG(t) plateau via block estimates: full production, final half, 3rd quarter, 4th quarter (reviewer
    condition 4). Degrades to a status string if the analyzer's decorrelated energy cache isn't exposed."""
    try:
        u_ln = getattr(analyzer, "_unbiased_decorrelated_u_ln", None)
        N_l = getattr(analyzer, "_unbiased_decorrelated_N_l", None)
        if u_ln is None or N_l is None:
            return {"status": "block plateau needs analyzer u_ln cache (not exposed in this version)"}
        f_k = _converged_f_k(analyzer)
        dg_full = _mbar_dg_on_slice(u_ln, N_l, 0.0, 1.0, f_k)
        dg_half = _mbar_dg_on_slice(u_ln, N_l, 0.5, 1.0, f_k)
        dg_q3 = _mbar_dg_on_slice(u_ln, N_l, 0.5, 0.75, f_k)
        dg_q4 = _mbar_dg_on_slice(u_ln, N_l, 0.75, 1.0, f_k)
        out = {"status": "ok", "dg_full_kcal": dg_full, "dg_final_half_kcal": dg_half,
               "dg_q3_kcal": dg_q3, "dg_q4_kcal": dg_q4}
        out.update(block_plateau_flags(dg_full, dg_half, dg_q3, dg_q4))
        return out
    except Exception as e:  # noqa: BLE001
        return {"status": "block plateau failed: %s: %s" % (type(e).__name__, e)}


def _mixing(analyzer, reporter):
    """Replica state-transition statistics: transition matrix, subdominant eigenvalue (mixing timescale), and
    per-replica round trips between the end states."""
    try:
        import numpy as np
        stats = None
        for name in ("generate_mixing_statistics", "mixing_statistics"):
            fn = getattr(analyzer, name, None)
            if fn is not None:
                stats = fn() if callable(fn) else fn
                break
        tmat = eigs = None
        if stats is not None:
            tmat = getattr(stats, "transition_matrix", None)
            if tmat is None and isinstance(stats, (tuple, list)):
                tmat = stats[0]
            eigs = getattr(stats, "eigenvalues", None)
        subdominant = None
        if eigs is not None:
            ev = sorted([abs(float(x)) for x in np.real(eigs)], reverse=True)
            subdominant = ev[1] if len(ev) > 1 else None
        elif tmat is not None:
            ev = sorted([abs(float(x)) for x in np.linalg.eigvals(np.asarray(tmat))], reverse=True)
            subdominant = ev[1] if len(ev) > 1 else None
        # round trips: how often each replica visited both end states
        roundtrips = None
        try:
            states = reporter.read_replica_thermodynamic_states()   # [n_iter, n_replicas]
            states = np.asarray(states)
            K = states.max() + 1
            rts = []
            for r in range(states.shape[1]):
                seq = states[:, r]
                hi = seq == (K - 1); lo = seq == 0
                rts.append(int(min(hi.sum() > 0, lo.sum() > 0)))   # visited both ends at least once
            roundtrips = int(sum(rts))
        except Exception:  # noqa: BLE001
            pass
        return {"status": "ok", "subdominant_eigenvalue": subdominant,
                "n_replicas_visiting_both_ends": roundtrips,
                "transition_matrix_shape": (list(np.asarray(tmat).shape) if tmat is not None else None)}
    except Exception as e:  # noqa: BLE001
        return {"status": "mixing failed: %s: %s" % (type(e).__name__, e)}


def _equilibration(analyzer):
    """Equilibration detection + effective sample size (N_eff = n_production / statistical_inefficiency)."""
    try:
        n_equil = getattr(analyzer, "n_equilibration_iterations", None)
        g = getattr(analyzer, "statistical_inefficiency", None)
        n_iter = None
        rep = getattr(analyzer, "reporter", None)
        if rep is not None:
            try:
                n_iter = int(rep.read_last_iteration())
            except Exception:  # noqa: BLE001
                n_iter = None
        n_eff = None
        if n_iter and n_equil is not None and g:
            n_eff = max((n_iter - int(n_equil)) / float(g), 0.0)
        equil_frac = (float(n_equil) / n_iter) if (n_equil is not None and n_iter) else None
        return {"status": "ok", "n_iterations": n_iter, "n_equilibration_iterations":
                (int(n_equil) if n_equil is not None else None),
                "statistical_inefficiency": (float(g) if g else None),
                "n_effective_samples": n_eff, "equilibration_fraction": equil_frac}
    except Exception as e:  # noqa: BLE001
        return {"status": "equilibration failed: %s: %s" % (type(e).__name__, e)}


def analyze_leg(nc_path, tag):
    """Full convergence analysis of one leg's committed simulation.nc. Returns a diagnostics dict with per-metric
    results + boolean health flags + an overall technical_failure."""
    rec = {"tag": tag, "nc": nc_path}
    try:
        from openmmtools.multistate import MultiStateReporter, MultiStateSamplerAnalyzer
    except Exception as e:  # noqa: BLE001
        rec["status"] = "openmmtools unavailable: %s" % e
        return rec
    try:
        # CHECKPOINT FILENAME. OpenFE/openmmtools defaults the checkpoint to `checkpoint.nc`, but this repo's
        # driver writes `checkpoint.chk` (rbfe_spot_driver PRODUCTION pair `simulation.nc`/`checkpoint.chk`;
        # nr4a3_rbfe._read_last_iters, :1551). So a default-constructed reporter finds no checkpoint storage,
        # positions are unavailable, and read_sampler_states() dies on None.dimensions (a netCDF4 Dataset
        # attribute). Evidence (GH run 30156575387): files_beside_nc = [COMMITTED.json, checkpoint.chk,
        # simulation.nc] with has_checkpoint_storage = false — the file was always there under a name openmmtools
        # never looks for. That is why the mandated ligand-escape / pose-collapse check has never once produced a
        # number, on this lane or any other using the same commit store. Point the reporter at the real file.
        _dir = os.path.dirname(os.path.abspath(nc_path))
        _base = os.path.basename(nc_path).rsplit(".", 1)[0]          # simulation | equilibration
        _cands = ["%s.chk" % _base, "checkpoint.chk", "%s_checkpoint.nc" % _base, "checkpoint.nc"]
        _ckpt = next((c for c in _cands if os.path.isfile(os.path.join(_dir, c))), None)
        reporter = None
        if _ckpt:
            try:
                reporter = MultiStateReporter(nc_path, open_mode="r", checkpoint_storage=_ckpt)
            except Exception as e:  # noqa: BLE001  (older signature / interval mismatch -> fall back)
                rec["checkpoint_open_note"] = "checkpoint_storage=%s rejected (%s: %s); opened without it" % (
                    _ckpt, type(e).__name__, e)
        rec["checkpoint_file"] = _ckpt
        if reporter is None:
            reporter = MultiStateReporter(nc_path, open_mode="r")
        analyzer = MultiStateSamplerAnalyzer(reporter)
    except Exception as e:  # noqa: BLE001
        rec["status"] = "could not open reporter/analyzer: %s: %s" % (type(e).__name__, e)
        return rec
    # MBAR end-to-end ΔG
    try:
        f_ij, df_ij = analyzer.get_free_energy()
        rec["mbar_dg_kt"] = float(f_ij[0, -1]); rec["mbar_dg_err_kt"] = float(df_ij[0, -1])
        rec["mbar_dg_kcal"] = rec["mbar_dg_kt"] * KT_KCAL
        rec["mbar_dg_err_kcal"] = rec["mbar_dg_err_kt"] * KT_KCAL
    except Exception as e:  # noqa: BLE001
        rec["mbar_status"] = "get_free_energy failed: %s: %s" % (type(e).__name__, e)
    # Defence in depth for the module docstring's promise: ONE diagnostic that raises must not delete the other
    # six. Each is a lazy openmmtools/pymbar path that can fail for env reasons entirely unrelated to the
    # trajectory's health, and a report that vanishes tells you nothing about the leg.
    def _safe(name, fn, *a):
        try:
            return fn(*a)
        except Exception as e:  # noqa: BLE001
            return {"status": "%s raised %s: %s" % (name, type(e).__name__, e)}

    rec["overlap"] = _safe("overlap", _overlap, analyzer)
    rec["equilibration"] = _safe("equilibration", _equilibration, analyzer)
    rec["mixing"] = _safe("mixing", _mixing, analyzer, reporter)
    rec["forward_reverse"] = _safe("forward_reverse", _forward_reverse, analyzer)
    rec["block_plateau"] = _safe("block_plateau", _block_plateau, analyzer)
    rec["restraints"] = {"status": "RBFE binding legs carry no orientational restraints; none to diagnose"}
    rec["structural"] = _safe("structural", _structural, reporter, nc_path)

    # ---- health flags (each None if the metric wasn't computable) ----
    ov = rec["overlap"].get("overlap_scalar")
    connected = rec["overlap"].get("connected")
    eq = rec["equilibration"].get("equilibration_fraction")
    sub = rec["mixing"].get("subdominant_eigenvalue")
    gap = rec["forward_reverse"].get("final_forward_reverse_gap_kcal")
    lig = rec["structural"].get("ligand_rmsd_A")
    flags = {
        "overlap_ok": (None if ov is None else ov >= OVERLAP_SCALAR_MIN),
        "overlap_connected_ok": connected,        # reviewer condition 4: no adjacent-state bottleneck
        "equilibrated_ok": (None if eq is None else eq <= EQUIL_FRACTION_MAX),
        "mixing_ok": (None if sub is None else sub <= MIX_SUBDOMINANT_MAX),
        "forward_reverse_ok": (None if gap is None else gap <= FWD_REV_GAP_MAX_KCAL),
        "plateau_full_vs_half_ok": rec["block_plateau"].get("plateau_full_vs_half_ok"),
        "quarter_block_ok": rec["block_plateau"].get("quarter_block_ok"),
        "ligand_stable_ok": (None if lig is None else lig <= LIG_RMSD_MAX_A),
    }
    rec["health_flags"] = flags
    # technical_failure = any computable flag is False (a metric we could measure and it failed its threshold)
    failed = [k for k, v in flags.items() if v is False]
    rec["technical_failure"] = bool(failed)
    rec["failed_checks"] = failed
    # COMPLETENESS, reported SEPARATELY from failure. The frozen rule requires that "all convergence diagnostics
    # pass"; a flag of None means the metric was never obtained, and counting that as satisfied is how the r0 leg
    # returned technical_failure=false while forward/reverse, dG(t) plateau, quarter-block AND ligand drift were
    # all unmeasured. This does NOT retroactively flip technical_failure (that field means MEASURED failures);
    # it exposes the distinction so a reader — and the reducer — can tell "checked and fine" from "never checked".
    unmeasured = [k for k, v in flags.items() if v is None]
    rec["mandatory_unmeasured"] = unmeasured
    rec["diagnostics_complete"] = not unmeasured
    rec["gate_note"] = ("all diagnostics measured and passing" if not unmeasured and not failed else
                        "MEASURED FAILURES: %s" % failed if failed else
                        "no measured failure, but %d diagnostic(s) never computed: %s — the frozen rule's "
                        "'all convergence diagnostics pass' is NOT satisfied by an unmeasured diagnostic"
                        % (len(unmeasured), unmeasured))
    return rec


def _structural(reporter, nc_path):
    """Best-effort ligand heavy-atom RMSD vs the first frame (ligand-escape / collapse detector). Requires the
    checkpoint positions + mdtraj; if unavailable, returns a status string (non-blocking)."""
    try:
        import mdtraj  # noqa: F401
    except Exception:  # noqa: BLE001
        return {"status": "mdtraj unavailable — structural RMSD skipped (non-blocking)"}
    try:
        import numpy as np
        # Positions live in the CHECKPOINT, which is written every checkpoint_interval iterations — so an
        # arbitrary iteration (e.g. read_last_iteration(), 2000 against an interval of 40 is fine, but any
        # non-multiple is not) yields sampler states whose .positions is None. Dereferencing that gave
        # "AttributeError: 'NoneType' object has no attribute 'dimensions'", which is how the mandated
        # ligand-escape check reported nothing. Align both reads to the checkpoint grid and check for None.
        interval = int(getattr(reporter, "checkpoint_interval", 0) or 1)
        last = int(reporter.read_last_iteration())
        last_ckpt = (last // interval) * interval if interval > 1 else last
        pos = reporter.read_sampler_states(iteration=0)
        posN = reporter.read_sampler_states(iteration=last_ckpt)
        if not pos or not posN:
            return {"status": "no sampler-state positions in checkpoint (checkpoint_interval may exclude frames)"}
        if getattr(pos[0], "positions", None) is None or getattr(posN[0], "positions", None) is None:
            return {"status": "sampler states carry no positions at iterations 0/%d (checkpoint_interval=%d)"
                              % (last_ckpt, interval)}
        p0 = np.asarray(pos[0].positions.value_in_unit(pos[0].positions.unit))
        pN = np.asarray(posN[0].positions.value_in_unit(posN[0].positions.unit))

        # WHAT THIS NUMBER IS, AND WHAT IT IS NOT. The original implementation took an UNALIGNED, PBC-unwrapped
        # RMSD over EVERY particle — ~146k atoms, overwhelmingly bulk water — and compared it to LIG_RMSD_MAX_A,
        # a threshold written for a LIGAND heavy-atom RMSD. On the real r0 ternary leg that produced
        # ligand_rmsd_A = 78.94 A (GH run 30156744299) and flipped technical_failure to true, which via
        # ternary_fep_reduce._diagnostics_ok() would hand valB_mini a HARD FAIL. 79 A is not a PROTAC leaving an
        # interface: for a box whose edge is ~110-120 A it is what solvent diffusion plus periodic wrapping give
        # over 5 ns with no superposition. Comparing it to a 4 A pose threshold is a category error, and a FAIL
        # manufactured by a mis-specified metric is worse than no metric.
        # So: only compare to the threshold when the quantity IS pose-like — a SUPERPOSED RMSD over the reporter's
        # analysis-particle subset (the solute openmmtools was told to retain). Otherwise report the whole-system
        # number as informational and leave the flag None (unmeasured), which is the honest state.
        idx = getattr(reporter, "analysis_particle_indices", None)
        n_idx = len(idx) if idx is not None else 0
        n_all = int(p0.shape[0])
        if idx is not None and 0 < n_idx < n_all:
            sub = reporter.read_sampler_states(iteration=0, analysis_particles_only=True)
            subN = reporter.read_sampler_states(iteration=last_ckpt, analysis_particles_only=True)
            a = np.asarray(sub[0].positions.value_in_unit(sub[0].positions.unit))
            b = np.asarray(subN[0].positions.value_in_unit(subN[0].positions.unit))

            # MINIMUM IMAGE FIRST — the stored positions are WRAPPED, so part of the solute sits on the far side
            # of the box and its raw displacement is a lattice vector, not motion. Measured on r0's ternary leg
            # (run 30157135654): p50 2.52 Å, p90 6.03 Å, but p99 90.84 Å and max 135.49 Å against a 126.30 Å box
            # edge, with exactly 2.0 % of atoms beyond half a box. sqrt(0.02*100^2 + 0.98*3^2) ~= 14.4 Å recovers
            # the 14.97 Å that was reported, so the whole apparent rearrangement WAS that wrapped 2 % tail. Undo
            # the wrap before superposing and the number measures structure again.
            box = None
            try:
                bv = subN[0].box_vectors
                M = np.asarray([[bv[i][j].value_in_unit(bv.unit) for j in range(3)] for i in range(3)])
                off = float(np.abs(M - np.diag(np.diag(M))).max())
                if off <= 1e-6:                       # orthorhombic: componentwise min-image is exact
                    box = np.diag(M).astype(float)
            except Exception:  # noqa: BLE001
                box = None
            unwrapped = False
            if box is not None and np.all(box > 0):
                d = b - a
                d -= box * np.round(d / box)          # wrap each displacement into [-L/2, L/2]
                b = a + d
                unwrapped = True

            # Kabsch: remove translation, then the optimal rotation — so the number reports internal/pose change
            # rather than the whole complex tumbling and drifting through the box.
            ac, bc = a - a.mean(0), b - b.mean(0)
            U, _, Vt = np.linalg.svd(ac.T @ bc)
            d = np.sign(np.linalg.det(Vt.T @ U.T))
            R = Vt.T @ np.diag([1.0, 1.0, d]) @ U.T
            disp = np.sqrt((((ac @ R.T) - bc) ** 2).sum(axis=1)) * 10.0                  # per-atom, Å
            rmsd = float(np.sqrt((disp ** 2).mean()))
            # WHOSE RMSD IS THIS? On the real valB legs the analysis-particle subset is 7388 of 141968 atoms —
            # the WHOLE SOLUTE (SMARCA2 BD + VHL + EloB + EloC + the PROTAC), not the ligand. So it still must not
            # be judged against LIG_RMSD_MAX_A, a LIGAND pose threshold: a superposed multi-chain assembly cannot
            # be fit by one global rotation when the chains move relative to each other, so the number runs high
            # for reasons that are not pose collapse. Report it, do not fail on it.
            #
            # 14.97 Å (run 30156954406) is nonetheless too large to wave away, and there are two live explanations
            # that this function must not choose between by assertion:
            #   H1 the ternary assembly genuinely rearranged — decision-relevant, since that interface IS what
            #      ΔΔG_coop measures;
            #   H2 one or more chains wrapped across the periodic boundary — pure artifact.
            # The discriminator is the per-atom displacement DISTRIBUTION: a PBC jump is bimodal with a mode near
            # a box edge and leaves most atoms small, whereas real rearrangement moves atoms continuously. So emit
            # the percentiles and the box edge and let the next reader decide on data.
            pct = {("p%d" % p): float(np.percentile(disp, p)) for p in (50, 90, 99)}
            box_nm = (float(box.max()) * 10.0) if box is not None else None
            frac_beyond_half_box = (float((disp > (box_nm / 2.0)).mean()) if box_nm else None)
            # Only judge it against the threshold once the wrap is actually undone. Even then this is the SOLUTE
            # subset (protein assembly + PROTAC), not the ligand alone — so it is a structural-stability measure,
            # a legitimate escape/collapse detector, but not the ligand-pose RMSD the prereg names. Report which
            # it is; leave the pose flag unmeasured until the ligand atom indices come from the hybrid topology.
            return {"status": ("ok (minimum-image-corrected, superposed RMSD over the solute subset — %d of %d "
                               "atoms; structural-stability proxy, NOT the ligand-only pose RMSD)"
                               % (n_idx, n_all)) if unwrapped else
                              ("NOT minimum-image corrected (box unavailable or non-orthorhombic) — the value is "
                               "inflated by periodic wrapping and is informational only"),
                    "solute_superposed_rmsd_A": rmsd, "ligand_rmsd_A": None,
                    "minimum_image_corrected": unwrapped,
                    "solute_stable": (bool(rmsd <= LIG_RMSD_MAX_A) if unwrapped else None),
                    "displacement_percentiles_A": pct, "max_displacement_A": float(disp.max()),
                    "box_edge_A": box_nm, "fraction_atoms_beyond_half_box": frac_beyond_half_box,
                    "n_atoms_used": n_idx, "n_atoms_total": n_all,
                    "superposed": True, "iterations_compared": [0, last_ckpt],
                    "checkpoint_interval": interval}
        rmsd_all = float(np.sqrt(((pN - p0) ** 2).sum(axis=1).mean())) * 10.0
        return {"status": "NOT COMPARABLE to LIG_RMSD_MAX_A — no analysis-particle subset is stored (n_idx=%d of "
                          "%d), so this is an UNALIGNED whole-system value dominated by bulk-solvent diffusion "
                          "and periodic wrapping. Reported for the record only; the flag stays unmeasured. A real "
                          "pose check needs the ligand atom indices from the OpenFE hybrid topology."
                          % (n_idx, n_all),
                "whole_system_unaligned_rmsd_A": rmsd_all, "ligand_rmsd_A": None,
                "superposed": False, "n_atoms_total": n_all,
                "iterations_compared": [0, last_ckpt], "checkpoint_interval": interval}
    except Exception as e:  # noqa: BLE001
        # SELF-DESCRIBING FAILURE. This check has now failed twice with a bare
        # "AttributeError: 'NoneType' object has no attribute 'dimensions'", which names neither the object that
        # was None nor the read that produced it — so it cannot be root-caused from the report, only guessed at.
        # Dump what was actually obtained, so the next run diagnoses instead of re-guessing.
        probe = {}
        try:
            probe["checkpoint_interval"] = int(getattr(reporter, "checkpoint_interval", -1) or -1)
            probe["last_iteration"] = int(reporter.read_last_iteration())
            # THE LIKELY CAUSE, made explicit: positions live in a SEPARATE checkpoint file, not in
            # simulation.nc. With no checkpoint storage the reporter holds None and read_sampler_states()
            # dereferences None.dimensions (a netCDF4 Dataset attribute) — indistinguishable, from the bare
            # message, from a bug in this module. Name it.
            probe["has_checkpoint_storage"] = getattr(reporter, "_storage_checkpoint", None) is not None
            probe["checkpoint_exists_flag"] = bool(getattr(reporter, "_checkpoint_storage_file_exists", None)) \
                if hasattr(reporter, "_checkpoint_storage_file_exists") else None
            probe["files_beside_nc"] = sorted(os.listdir(os.path.dirname(nc_path)))[:12]
        except Exception as pe:  # noqa: BLE001
            probe["reporter_probe_error"] = "%s: %s" % (type(pe).__name__, pe)
        for label, it in (("iter0", 0), ("iter_last_ckpt", probe.get("checkpoint_interval", 1) and
                          (probe.get("last_iteration", 0) // max(probe.get("checkpoint_interval", 1), 1))
                          * max(probe.get("checkpoint_interval", 1), 1))):
            try:
                ss = reporter.read_sampler_states(iteration=it)
                probe[label] = {
                    "requested_iteration": it,
                    "returned": type(ss).__name__,
                    "n_states": (len(ss) if ss is not None else None),
                    "state0_type": (type(ss[0]).__name__ if ss else None),
                    "state0_positions": (type(getattr(ss[0], "positions", None)).__name__ if ss else None),
                    "state0_box_vectors": (type(getattr(ss[0], "box_vectors", None)).__name__ if ss else None),
                }
            except Exception as pe:  # noqa: BLE001
                probe[label] = "read_sampler_states(%s) raised %s: %s" % (it, type(pe).__name__, pe)
        return {"status": "structural RMSD failed: %s: %s" % (type(e).__name__, e), "probe": probe}


def analyze_all():
    os.makedirs(CKPT, exist_ok=True)
    ncs = _find_nc_files()
    legs = [analyze_leg(p, tag) for tag, p in sorted(ncs.items())]
    n_fail = sum(1 for l in legs if l.get("technical_failure"))
    report = {
        "_what": "OpenFE/openmmtools convergence analysis on committed MultiState .nc (reviewer change #1)",
        "_gate": "run on seed-0 BEFORE ternary seed-1; technical_failure feeds the reducer PASS/NO-GO/INDETERMINATE",
        "thresholds": {"overlap_scalar_min": OVERLAP_SCALAR_MIN, "overlap_bottleneck_min": OVERLAP_BOTTLENECK_MIN,
                       "mix_subdominant_max": MIX_SUBDOMINANT_MAX, "equil_fraction_max": EQUIL_FRACTION_MAX,
                       "fwd_rev_gap_max_kcal": FWD_REV_GAP_MAX_KCAL,
                       "plateau_full_half_max_kcal": PLATEAU_FULL_HALF_MAX_KCAL,
                       "quarter_block_max_kcal": QUARTER_BLOCK_MAX_KCAL, "lig_rmsd_max_A": LIG_RMSD_MAX_A},
        "n_legs_analyzed": len(legs), "n_technical_failures": n_fail, "legs": legs,
    }
    out = os.path.join(CKPT, "ternary_convergence.json")
    json.dump(report, open(out, "w"), indent=2, default=str)
    print("[tfep-converge] wrote %s (%d legs, %d technical failures)" % (out, len(legs), n_fail), flush=True)
    return report


if __name__ == "__main__":
    analyze_all()
