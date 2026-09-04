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
    # NOT APPLICABLE is a third thing, distinct from both "failed" and "never measured". The solvent leg has no
    # receptor, so the ligand-escape check has no referent there; leaving it as None would park that leg on
    # diagnostics_complete=False forever, and flagging it False fabricates a hard FAIL (which it did once).
    if ((rec["structural"].get("ligand") or {}).get("check_applicable") is False):
        flags.pop("ligand_stable_ok", None)
        rec["ligand_check_not_applicable"] = ("solvent leg — no receptor, so ligand escape / pose collapse is "
                                              "undefined; the check is skipped, not passed and not failed")
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


# =============================================================================================================
# LIGAND IDENTIFICATION — the missing half of the mandated pose check (defect #7, closed 2026-07-25).
#
# The prereg names a LIGAND heavy-atom RMSD. Every implementation so far measured something else and compared it
# to LIG_RMSD_MAX_A: first an unaligned whole-system RMSD over ~146 k atoms (79 Å, dominated by bulk water), then
# a superposed whole-SOLUTE RMSD over the 7388-atom analysis subset (15 Å, a four-chain assembly that one global
# rotation cannot fit). The second manufactured a hard FAIL. The reason neither was the ligand is that nothing in
# the committed artifacts (`simulation.nc`, `checkpoint.chk`, `COMMITTED.json`) is a topology file — there is no
# PDB, no residue table, no atom names. So the ligand had to be *derived*.
#
# It can be, exactly, from the hybrid System openmmtools serializes into the .nc: bonded connectivity partitions
# every particle into molecules, and in a solvated ternary assembly there is exactly ONE molecule that is neither
# a monatomic ion, nor water, nor a protein-sized chain. That is the PROTAC. This is an identification, not a
# heuristic ranking, and it FAILS CLOSED: if the count of candidates is not exactly one, no ligand is returned
# and the flag stays unmeasured. A second, fully independent identification from interatomic distances alone
# (no System, no bond table) is run as a cross-check, and disagreement is reported rather than hidden.
#
# WHY BONDS *AND* CONSTRAINTS: with `constraints=HBonds` OpenMM removes the X–H entries from HarmonicBondForce
# and represents them as constraints, so a bonds-only graph shatters every heavy atom's hydrogens into isolated
# singletons and the size classification collapses. And WHY CustomBondForce: OpenFE's HybridTopologyFactory moves
# the alchemical region's bonds into a softcore CustomBondForce, so a HarmonicBondForce-only graph would split
# the ligand itself — precisely the molecule we are trying to find.
LIG_MIN_ATOMS = 15             # smaller than any PROTAC; larger than an ion, a water, or a lone counter-ion pair
LIG_MAX_ATOMS = 500            # ~30 residues; every protein chain in this assembly is far larger
PROTEIN_MIN_ATOMS = 1000       # a component at least this big is treated as a protein chain (fit target)
# ⚠ NO FIXED HEAVY-ATOM MASS CUTOFF. This constant used to be 2.5 Da with a comment asserting that HMR was off
# in the ternary lane, so anything above deuterium had to be a heavy atom. THE REAL TRAJECTORY REFUTED THAT
# (GH run 30167976061): the identified ligand's mass histogram is {3: 51, 6: 5, 8: 6, 10: 18, 12: 18, 14: 8,
# 16: 3, 32: 1} — 51 atoms at ~3 Da are HYDROGENS UNDER HMR (1.008 -> 3.024), and 6/8/10 are the carbons that
# donated the mass (12.011 - n_H x 2.016 for n_H = 3/2/1). So a 2.5 Da cutoff called every hydrogen heavy and
# the "heavy-atom RMSD" silently ran over all 110 atoms. The emitted n_heavy is what made it visible, exactly as
# the old comment promised — but a constant that depends on an unverified simulation setting is the wrong shape.
# The hydrogen mass is now MEASURED PER SYSTEM from the ligand's own graph (see _hydrogen_mass_da), which works
# at any HMR factor and needs nothing asserted.
HEAVY_MASS_MARGIN = 1.3        # heavy = mass > (measured hydrogen mass) x this. 1.3 separates an HMR'd H (3.02)
                               # from the lightest possible heavy atom, a fully HMR'd methyl carbon (5.96).
BOND_CUTOFF_NM = 0.19          # cross-check graph only: 1.9 Å covers C–C 1.53, C–S 1.82, S–S 2.05 marginally;
                               # shorter than any nonbonded contact between distinct molecules


def molecules_from_edges(n_atoms, edges):
    """Partition [0, n_atoms) into connected components under `edges` (union-find). Pure stdlib — this is the
    part that decides which atoms are 'the ligand', so it is unit-testable without openmm, numpy or a .nc.
    Returns a list of sorted index lists, largest first."""
    parent = list(range(n_atoms))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in edges:
        if not (0 <= i < n_atoms and 0 <= j < n_atoms):
            continue
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj
    groups = {}
    for i in range(n_atoms):
        groups.setdefault(find(i), []).append(i)
    return sorted(groups.values(), key=lambda c: (-len(c), c[0]))


def classify_components(components, subset_indices=None):
    """Bucket molecular components by size, and pick the ligand — or refuse. FAILS CLOSED by construction: the
    ligand is returned ONLY when exactly one component satisfies every criterion. Zero candidates and two
    candidates both return ligand=None with the reason and the full size histogram, so a caller can never
    mistake 'could not identify' for 'identified'.

    `subset_indices` (the reporter's analysis-particle set) is an ADDITIONAL requirement, not a filter: the
    ligand must be fully retained in the stored subset, otherwise its positions do not exist and no RMSD is
    computable from this trajectory."""
    subset = set(subset_indices) if subset_indices is not None else None
    sizes = {}
    for c in components:
        sizes[len(c)] = sizes.get(len(c), 0) + 1
    cands, rejected_not_retained = [], 0
    for c in components:
        if not (LIG_MIN_ATOMS <= len(c) <= LIG_MAX_ATOMS):
            continue
        if subset is not None and not set(c).issubset(subset):
            rejected_not_retained += 1
            continue
        cands.append(c)
    info = {
        "n_components": len(components),
        "size_histogram": dict(sorted(sizes.items(), key=lambda kv: -kv[0])[:12]),
        "n_monatomic": sizes.get(1, 0),
        "n_water_sized": sizes.get(3, 0),
        "protein_components": [len(c) for c in components if len(c) >= PROTEIN_MIN_ATOMS],
        "n_ligand_sized_candidates": len(cands),
        "n_candidates_rejected_not_retained_in_subset": rejected_not_retained,
        "criteria": {"min_atoms": LIG_MIN_ATOMS, "max_atoms": LIG_MAX_ATOMS,
                     "protein_min_atoms": PROTEIN_MIN_ATOMS},
    }
    if len(cands) != 1:
        info["ligand"] = None
        info["status"] = ("ligand NOT identified: %d components fall in [%d, %d] atoms and are fully retained in "
                          "the analysis subset — the identification requires exactly 1, so it refuses rather "
                          "than pick" % (len(cands), LIG_MIN_ATOMS, LIG_MAX_ATOMS))
        return info
    info["ligand"] = list(cands[0])
    info["status"] = "ok"
    return info


def hydrogen_mass_da(atom_indices, masses, edges):
    """MEASURE the hydrogen mass in this system instead of assuming it.

    A hydrogen is a TERMINAL atom (graph degree 1 — under constraints=HBonds its X–H bond is a constraint, which
    `_system_edges` reads, so the degree is right) and hydrogens are by far the most common terminal species in
    an organic molecule. So: take the modal mass among the molecule's degree-1 atoms, and require it to also be
    the LIGHTEST mode — otherwise the molecule is something this heuristic should not be guessing about, and we
    say so instead. This is correct at any HMR factor, including none, and needs no simulation setting asserted.

    Returns (hydrogen_mass_da, note) with hydrogen_mass_da None when it cannot be determined."""
    idx = set(atom_indices)
    deg = {i: 0 for i in atom_indices}
    for i, j in edges:
        if i in idx and j in idx:
            deg[i] += 1
            deg[j] += 1
    terminal = [i for i in atom_indices if deg[i] == 1]
    if not terminal:
        return None, "no terminal atoms in the molecular graph — cannot identify hydrogens"
    hist = {}
    for i in terminal:
        hist[round(masses[i], 1)] = hist.get(round(masses[i], 1), 0) + 1
    modal = max(hist.items(), key=lambda kv: (kv[1], -kv[0]))[0]
    # Hydrogen is the lightest atom in the molecule under ANY repartitioning — HMR moves mass FROM heavy atoms
    # TO hydrogens, narrowing the gap (H 3.02 vs a fully repartitioned methyl carbon 5.96) but never inverting
    # it. So requiring the modal terminal mass to also be the molecule's minimum is assumption-free, and it is
    # what refuses a molecule whose terminal atoms are halogens rather than hydrogens.
    lightest = round(min(masses[i] for i in atom_indices), 1)
    if modal != lightest:
        return None, ("the modal terminal mass (%.1f Da) is not the molecule's lightest atom (%.1f Da) — "
                      "refusing to call it hydrogen" % (modal, lightest))
    return modal, ("hydrogen mass measured at %.2f Da from %d terminal atoms (%d of them at this mass); "
                   "%s" % (modal, len(terminal), hist[modal],
                           "consistent with hydrogen-mass repartitioning" if modal > 1.5 else
                           "unrepartitioned hydrogens"))


def _mass_da(m, unit_cache=None):
    """Particle mass in daltons, from an openmm Quantity or a plain number. Duck-typed on purpose: it is what
    lets the identification above be exercised end-to-end by a unit test with a fake System, on a runner with no
    openmm — which is the only way to prove the metric RESPONDS to a displaced ligand rather than merely
    returning a number."""
    v = getattr(m, "value_in_unit", None)
    if v is None:
        return float(m)
    # One identification can contain thousands of quantities. In a runner without OpenMM,
    # unsuccessful imports are not cached by Python and used to scan sys.path twice per atom.
    # The caller's cache lasts for this batch only; subsequent identifications resolve afresh.
    if unit_cache is None:
        unit_cache = {}
    if "dalton" not in unit_cache:
        try:
            from openmm import unit as ommunit
        except Exception:  # noqa: BLE001  (older path, then no-openmm fake)
            try:
                from simtk import unit as ommunit  # type: ignore
            except Exception:  # noqa: BLE001
                ommunit = None
        unit_cache["dalton"] = ommunit.dalton if ommunit is not None else None
    return float(v(unit_cache["dalton"]))


def _system_edges(system):
    """Bonded connectivity of an openmm.System as (i, j) pairs: every bonded force that exposes a bond list, PLUS
    the distance constraints (which is where X–H bonds live under constraints=HBonds). Returns (edges, provenance)
    so the report says which forces actually contributed — a silently-empty force is the failure mode here."""
    edges, prov = [], {}
    for k in range(system.getNumForces()):
        f = system.getForce(k)
        name = type(f).__name__
        get_n, get_p = getattr(f, "getNumBonds", None), getattr(f, "getBondParameters", None)
        if get_n is None or get_p is None:
            continue
        n = int(get_n())
        added = 0
        for b in range(n):
            p = get_p(b)
            try:
                i, j = int(p[0]), int(p[1])
            except Exception:  # noqa: BLE001  (a force whose params are not (i, j, ...) is not a 2-body bond)
                break
            edges.append((i, j))
            added += 1
        if added:
            prov[name] = prov.get(name, 0) + added
    # openmm.System's constraint accessor is getConstraintParameters(index) -> (p1, p2, distance). The first cut
    # of this function called `getConstraint`, which does not exist, and the unit-test fake was written to the
    # same wrong name — so the test passed while the production path raised AttributeError on the real System
    # (GH run 30167699679). That is the same failure shape as the seven defects this module was repairing: a
    # test agreeing with the code rather than with reality. The fake now implements ONLY the documented name.
    getc = getattr(system, "getConstraintParameters", None) or getattr(system, "getConstraint", None)
    n_con = int(system.getNumConstraints())
    if getc is None:
        prov["constraints"] = "UNAVAILABLE — no getConstraintParameters on this System object"
        return edges, prov
    for c in range(n_con):
        p = getc(c)
        edges.append((int(p[0]), int(p[1])))
    prov["constraints"] = n_con
    return edges, prov


def _distance_edges(coords_nm, cutoff_nm=BOND_CUTOFF_NM):
    """INDEPENDENT cross-check connectivity from coordinates alone — no System, no bond table. Cell-list neighbour
    search at a covalent-bond cutoff. Its purpose is to be wrong in different ways than the bond graph: if the
    two identifications agree atom-for-atom, the ligand assignment does not rest on either one being right."""
    import numpy as np
    xyz = np.asarray(coords_nm, dtype=float)
    n = xyz.shape[0]
    cell = {}
    inv = 1.0 / cutoff_nm
    keys = np.floor(xyz * inv).astype(int)
    for i in range(n):
        cell.setdefault(tuple(keys[i]), []).append(i)
    edges = []
    c2 = cutoff_nm * cutoff_nm
    offs = [(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)]
    for i in range(n):
        ki = keys[i]
        for o in offs:
            for j in cell.get((ki[0] + o[0], ki[1] + o[1], ki[2] + o[2]), ()):
                if j <= i:
                    continue
                d = xyz[i] - xyz[j]
                if float(d @ d) <= c2:
                    edges.append((i, j))
    return edges


def _frozen_heavy_cross_check(n_heavy, n_total):
    """Compare the derived heavy-atom count against the frozen calibration record. Best-effort: an absent file
    is reported, never treated as agreement."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wurz-calib-frozen.json")
    try:
        v = json.load(open(p)).get("validation", {})
        expect = [v.get(k) for k in ("heavy_1", "heavy_4") if v.get(k) is not None]
    except Exception as e:  # noqa: BLE001
        return {"status": "frozen record unreadable (%s: %s) — no cross-check" % (type(e).__name__, e)}
    if not expect:
        return {"status": "frozen record carries no heavy-atom count — no cross-check"}
    ok = n_heavy in expect
    return {"frozen_heavy_atom_counts": expect, "derived_n_heavy": n_heavy, "derived_n_atoms_total": n_total,
            "agree": ok,
            "verdict": ("CONSISTENT — the molecule identified in the .nc has the frozen morph's heavy-atom count"
                        if ok else
                        "INCONSISTENT — derived %d heavy atoms against a frozen %s. Either the wrong molecule "
                        "was identified or the hydrogen measurement is wrong; do not trust the pose RMSD."
                        % (n_heavy, expect))}


def _ligand_atoms(reporter):
    """Resolve the ligand's atom indices for this leg. Returns a dict that ALWAYS records how the answer was
    obtained (or why it was not) — `ligand_atom_indices` is None unless the identification succeeded outright."""
    out = {"provenance": None}
    idx = getattr(reporter, "analysis_particle_indices", None)
    subset = [int(v) for v in idx] if idx is not None else None
    out["n_analysis_particles"] = (len(subset) if subset is not None else 0)
    system = None
    for route in ("read_end_thermodynamic_states", "read_thermodynamic_states"):
        fn = getattr(reporter, route, None)
        if fn is None:
            continue
        try:
            states = fn()
            st = states
            while isinstance(st, (list, tuple)) and st:
                st = st[0]
            system = getattr(st, "system", None)
            if system is not None:
                out["provenance"] = route
                break
        except Exception as e:  # noqa: BLE001
            out.setdefault("route_errors", {})[route] = "%s: %s" % (type(e).__name__, e)
    if system is None:
        out["status"] = ("could not deserialize a System from the reporter (%s) — the ligand cannot be "
                         "identified, so the pose RMSD stays UNMEASURED"
                         % out.get("route_errors", "no route available"))
        out["ligand_atom_indices"] = None
        return out
    n_atoms = int(system.getNumParticles())
    out["n_particles"] = n_atoms
    mass_unit_cache = {}
    masses = [_mass_da(system.getParticleMass(i), mass_unit_cache) for i in range(n_atoms)]
    edges, prov = _system_edges(system)
    out["bond_provenance"] = prov
    out["n_edges"] = len(edges)
    comps = molecules_from_edges(n_atoms, edges)
    info = classify_components(comps, subset)
    out.update({k: v for k, v in info.items() if k != "ligand"})
    lig = info.get("ligand")
    out["ligand_atom_indices"] = lig
    if lig is None:
        return out
    h_mass, h_note = hydrogen_mass_da(lig, masses, edges)
    out["hydrogen_mass_da"] = h_mass
    out["hydrogen_mass_note"] = h_note
    cut = (h_mass * HEAVY_MASS_MARGIN) if h_mass is not None else None
    out["heavy_atom_mass_cutoff_da"] = cut
    heavy = [i for i in lig if cut is not None and masses[i] > cut]
    out["n_ligand_atoms"] = len(lig)
    out["n_ligand_heavy_atoms"] = len(heavy)
    out["ligand_heavy_indices"] = heavy
    # INDEPENDENT CORROBORATION, free and decisive. wurz-calib-frozen.json records validation.heavy_1 = 59 and
    # heavy_4 = 59 for this exact morph — a heavy-atom count established at freeze time by RDKit on the frozen
    # SMILES, with nothing to do with this trajectory, this System, or this graph. If the count derived here
    # matches it, the molecule identified in a 141,968-particle .nc is the Wurz compound-1/4 hybrid, and the
    # hydrogen measurement above is right as well (an H-inclusive count would read 110, not 59).
    out["frozen_heavy_atom_cross_check"] = _frozen_heavy_cross_check(len(heavy), len(lig))
    # Composition, emitted so a human can sanity-check that this is a PROTAC and not, say, a lipid or a mis-split
    # protein loop. Nearest-integer mass buckets; no element assignment is asserted.
    buckets = {}
    for i in lig:
        buckets[int(round(masses[i]))] = buckets.get(int(round(masses[i])), 0) + 1
    out["ligand_mass_histogram_da"] = dict(sorted(buckets.items()))
    out["protein_atom_indices"] = [i for c in comps if len(c) >= PROTEIN_MIN_ATOMS for i in c]
    # The same measured cutoff is applied to the protein: the fit target should be heavy atoms, and the protein
    # is repartitioned by the same HMR setting as the ligand (it is one System). If the ligand's hydrogen mass
    # could not be measured, no cutoff is applied and every protein atom is used — a fit set that is too LARGE
    # is a conservative failure mode; silently fitting on hydrogens-called-heavy is not.
    out["protein_heavy_indices"] = [i for i in out["protein_atom_indices"]
                                    if cut is None or masses[i] > cut]
    out["protein_chain_sizes"] = [len(c) for c in comps if len(c) >= PROTEIN_MIN_ATOMS]
    out["protein_chains"] = [list(c) for c in comps if len(c) >= PROTEIN_MIN_ATOMS]
    return out


def _min_image(A, B, M):
    """Fold B−A into the primitive cell of lattice `M` (rows = lattice vectors). Exact for any triclinic cell,
    reduces to the diagonal case when rectangular. Returns (B_unwrapped, applied)."""
    import numpy as np
    if M is None or abs(float(np.linalg.det(M))) <= 1e-9:
        return B, False
    d = B - A
    d = d - np.round(d @ np.linalg.inv(M)) @ M
    return A + d, True


def _kabsch_rmsd(A, B, fit_rows, meas_rows):
    """RMSD over `meas_rows` after superposing frame B onto frame A using ONLY `fit_rows`. With fit_rows == a
    protein chain and meas_rows == the ligand this is a POSE RMSD in the receptor frame — the quantity the
    prereg's escape/collapse threshold was written for. With fit_rows == meas_rows == the ligand it is the
    ligand's internal conformational change."""
    import numpy as np
    if not fit_rows or not meas_rows:
        return None
    fa, fb = A[fit_rows], B[fit_rows]
    ca, cb = fa.mean(0), fb.mean(0)
    # H = A^T B, so R = V·diag·U^T rotates FRAME A onto FRAME B (the same convention the solute-proxy block
    # above uses). Applying it to B instead of A silently measures the rotation itself: caught by
    # test_pose_rmsd_ignores_rigid_body_motion_of_the_whole_system, which read 45 Å for a pure rigid-body move.
    U, _, Vt = np.linalg.svd((fa - ca).T @ (fb - cb))
    s = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1.0, 1.0, s]) @ U.T
    ma = (A[meas_rows] - ca) @ R.T
    mb = B[meas_rows] - cb
    return float(np.sqrt(((ma - mb) ** 2).sum(axis=1).mean()) * 10.0)   # nm -> Å


CONTACT_CUTOFF_NM = 0.45       # ligand heavy atom within this of any receptor heavy atom at t0 = "in the pocket"


def _contact_ligand_rows(A, lig_rows, prot_rows, cutoff_nm=CONTACT_CUTOFF_NM):
    """The ligand heavy-atom rows that are IN CONTACT with the receptor in reference frame `A`.

    WHY THIS EXISTS -- the third instance of one reasoning error. LIG_RMSD_MAX_A (4 Å) is a POCKET-ESCAPE
    threshold, and this file has already had to retract applying it to atoms that have no pocket twice: once on
    the whole 146 k-particle system (79 Å, dominated by bulk water) and once on the SOLVENT leg's internal RMSD
    (a free PROTAC in water is supposed to explore conformations, so the check was made NOT APPLICABLE rather
    than failed). The BINARY leg is the same error a third time. A PROTAC in a binary complex has ONE warhead in
    the receptor; the linker and the distal warhead are in solvent by construction, because the second protein is
    absent. A whole-ligand pose RMSD over all 59 heavy atoms is then dominated by the free end moving, which is
    the expected physics of the binary state -- not an escape.

    Measured on the real r0 cycle (GH run 30201372471): binary_vhl pose_rmsd max 16.636 Å / median 6.987 Å ->
    technical_failure=TRUE, against ternary_vhl at max 2.765 / median 1.644 in the SAME cycle. The whole-ligand
    observable cannot tell "the bound warhead left its pocket" (a real failure that would invalidate ΔG_binary,
    and with it ΔΔG_coop = ΔG_ternary - ΔG_binary) from "the unbound end moved" (physics). This restricts the
    measurement to the atoms the threshold is actually about.

    Contacts are taken from the REFERENCE frame only, never re-derived at the later frame: a warhead that leaves
    its pocket would drop out of a frame-B contact set and the escape would erase its own evidence. Frame A fixes
    "which atoms were in the pocket to begin with", and the RMSD then answers "are they still where they were".
    """
    import numpy as np
    if not lig_rows or not prot_rows:
        return []
    L = A[lig_rows]
    P = A[prot_rows]
    # chunked to keep the (n_lig x n_prot) distance block small; n_prot is ~thousands of heavy atoms
    keep = np.zeros(len(lig_rows), dtype=bool)
    for i in range(0, len(P), 4096):
        d = np.linalg.norm(L[:, None, :] - P[None, i:i + 4096, :], axis=2)
        keep |= (d.min(axis=1) <= cutoff_nm)
    return [lig_rows[i] for i in range(len(lig_rows)) if keep[i]]


def _replica_coords(state):
    import numpy as np
    p = getattr(state, "positions", None)
    if p is None:
        return None, None
    xyz = np.asarray(p.value_in_unit(p.unit))
    M = None
    bv = getattr(state, "box_vectors", None)
    if bv is not None:
        try:
            M = np.asarray([[float(bv[i][j].value_in_unit(bv.unit)) for j in range(3)] for i in range(3)])
        except Exception:  # noqa: BLE001  (some versions hand back a plain Vec3 list, already in nm)
            try:
                M = np.asarray([[float(bv[i][j]) for j in range(3)] for i in range(3)])
            except Exception:  # noqa: BLE001
                M = None
    return xyz, M


TIMESERIES_MAX_FRAMES = 25     # bound the reads; 25 frames over a 2000-iteration leg is ample shape resolution


def _contact_pose_timeseries(reporter, last_ckpt, interval, max_frames=TIMESERIES_MAX_FRAMES):
    """Contact-moiety pose RMSD vs the reference frame, as a SERIES over checkpointed iterations, per replica.

    WHY A SERIES. The two-frame number (`ligand`, above) established that the binary leg's BOUND moiety moves
    ~16 Å — not just its solvent-exposed end (GH run 30202934339: contact-moiety max 16.327 Å, median 4.333 Å,
    30-52 of 59 heavy atoms in contact, against the ternary leg's clean 2.835 / 1.653 in the same cycle). That is
    a real measured failure, and it is where a two-frame comparison stops being able to help: `iterations_compared
    [0, 2000]` is consistent with at least three histories that mean different things.

        DISPLACED_AND_STAYED   monotonic-ish departure that does not return -> the ligand left. If this is the
                               binary leg's shape, ΔG_binary is sampling an unbound/misbound state and
                               ΔΔG_coop = ΔG_ternary - ΔG_binary is not recoverable by resampling harder.
        EXCURSION_AND_RETURNED went out and came back -> the endpoint frame caught it out. The trajectory may be
                               usable; the ENDPOINT metric is what is misleading, not the sampling.
        JUMP                   a single-frame discontinuity -> suspect bookkeeping (imaging, replica indexing),
                               not physics. A molecule cannot cross the box in one checkpoint interval.

    Distinguishing them costs nothing: positions for every checkpointed iteration are already in the .nc/.chk the
    caller has open. Nothing here feeds a gate -- the flag stays with the two-frame contact-moiety value. This is
    diagnostic evidence for reading that flag, and it is deliberately kept out of the pass/fail path so that a
    classifier heuristic can never move a verdict.

    Contacts come from the FIRST usable frame, per replica, and are held fixed across the series for the same
    reason the two-frame version does it: a departing atom would drop out of a later frame's contact set and the
    departure would erase its own evidence.
    """
    import numpy as np
    out = {"reference_iteration": None, "frames_requested": 0, "frames_used": 0}
    ident = _ligand_atoms(reporter)
    if ident.get("ligand_atom_indices") is None:
        out["status"] = "ligand not identified: %s" % ident.get("status", "?")
        return out
    subset = [int(v) for v in (getattr(reporter, "analysis_particle_indices", None) or [])]
    row_of = {v: r for r, v in enumerate(subset)}
    lig_rows = [row_of[i] for i in ident["ligand_heavy_indices"] if i in row_of]
    prot_rows = [row_of[i] for i in ident["protein_heavy_indices"] if i in row_of]
    if not lig_rows or not prot_rows:
        out["status"] = ("no receptor in the stored subset (solvent leg) or ligand heavy atoms absent — a pose "
                         "series has no referent here")
        return out

    step = max(interval, 1)
    iters = list(range(0, int(last_ckpt) + 1, step))
    if len(iters) > max_frames:                       # subsample evenly, always keeping first and last
        keep = {0, len(iters) - 1}
        stride = (len(iters) - 1) / float(max_frames - 1)
        keep.update(int(round(i * stride)) for i in range(max_frames))
        iters = [iters[i] for i in sorted(k for k in keep if 0 <= k < len(iters))]
    out["frames_requested"] = len(iters)

    ref = None            # per-replica reference coords
    contact_rows = None   # per-replica contact rows, fixed from the reference frame
    used = []
    series = {}           # replica -> [(iteration, rmsd)]
    lam = {}              # replica -> {iteration: lambda-state index}
    n_states = None
    for it in iters:
        try:
            states = reporter.read_sampler_states(iteration=it, analysis_particles_only=True)
        except Exception:  # noqa: BLE001 — a missing frame is skipped, never faked
            continue
        if not states:
            continue
        coords = []
        for st in states:
            xyz, M = _replica_coords(st)
            coords.append((xyz, M))
        if any(c[0] is None for c in coords):
            continue
        if ref is None:
            ref = [c[0] for c in coords]
            contact_rows = [_contact_ligand_rows(A, lig_rows, prot_rows) for A in ref]
            out["reference_iteration"] = int(it)
            out["n_contact_heavy_per_replica"] = [len(c) for c in contact_rows]
        used.append(int(it))
        # WHICH λ IS EACH REPLICA AT? Replicas exchange λ, not coordinates, so a replica wanders the ladder and
        # "replica 7 departed" says nothing on its own about the Hamiltonian it departed under. In an OpenFE
        # hybrid-topology RBFE BOTH endpoints are physical (state 0 = ligand A fully interacting, state N-1 =
        # ligand B fully interacting) and the softcore/partially-decoupled region is largest in the INTERIOR. So
        # the discriminating question is not "weakly coupled or not" but: does the ligand leave at a PHYSICAL
        # ENDPOINT state (the modelled complex is unstable -> the binary pose/model is wrong) or only in the
        # alchemical interior (a protocol artifact -> the leg may want a restraint and ΔG may be salvageable)?
        # Unavailable is recorded as unavailable; nothing is inferred from a missing assignment.
        try:
            st_idx = reporter.read_replica_thermodynamic_states(iteration=it)
        except Exception:  # noqa: BLE001
            st_idx = None
        if st_idx is not None:
            try:
                seq = [int(v) for v in list(st_idx)]
                n_states = max(n_states or 0, (max(seq) + 1) if seq else 0)
                for k, s in enumerate(seq):
                    lam.setdefault(k, {})[int(it)] = s
            except Exception:  # noqa: BLE001
                pass
        for k in range(min(len(ref), len(coords))):
            if not contact_rows[k]:
                continue
            B, _ = _min_image(ref[k], coords[k][0], coords[k][1])
            v = _kabsch_rmsd(ref[k], B, prot_rows, contact_rows[k])
            if v is not None:
                series.setdefault(k, []).append((int(it), round(float(v), 3)))
    out["frames_used"] = len(used)
    out["iterations"] = used
    if not series:
        out["status"] = ("no checkpointed frame carried usable positions (checkpoint_interval=%d, last=%d) — the "
                         "series is UNAVAILABLE, which is not the same as flat" % (interval, last_ckpt))
        return out

    per_replica, classes = [], {}
    for k in sorted(series):
        vals = [v for _, v in series[k]]
        its = [i for i, _ in series[k]]
        mx = max(vals); mi = its[vals.index(mx)]; fin = vals[-1]
        # gap between consecutive frames: a JUMP is a step larger than everything else combined with a flat rest
        gaps = [abs(vals[j + 1] - vals[j]) for j in range(len(vals) - 1)] or [0.0]
        biggest_gap = max(gaps)
        if mx <= LIG_RMSD_MAX_A:
            cls = "STABLE"
        elif fin >= 0.7 * mx:
            cls = "DISPLACED_AND_STAYED"
        elif fin <= 0.4 * mx:
            cls = "EXCURSION_AND_RETURNED"
        else:
            cls = "INTERMEDIATE"
        # a single frame carrying most of the range, with the rest quiet, is a discontinuity not a trajectory
        if mx > LIG_RMSD_MAX_A and biggest_gap >= 0.8 * mx:
            cls = "JUMP(" + cls + ")"
        classes[cls] = classes.get(cls, 0) + 1
        # λ ATTRIBUTION for this replica: the state it was in at the first frame that exceeds the threshold, and
        # at the end. `None` throughout if the reporter gave no assignment — never guessed.
        lk = lam.get(k) or {}
        first_exceed_it = next((i for i, v in series[k] if v > LIG_RMSD_MAX_A), None)
        rec = {"replica": k, "n_contact_heavy": len(contact_rows[k]),
               "max_A": mx, "iteration_at_max": mi, "final_A": fin,
               "largest_single_frame_step_A": round(biggest_gap, 3),
               "classification": cls, "series": series[k],
               "lambda_at_first_exceed": (lk.get(first_exceed_it) if first_exceed_it is not None else None),
               "lambda_at_max": lk.get(mi), "lambda_at_final": lk.get(its[-1]),
               "lambda_states_visited": (sorted(set(lk.values())) if lk else None)}
        per_replica.append(rec)
    out["per_replica"] = per_replica
    out["class_counts"] = classes
    out["n_lambda_states"] = n_states
    # AGGREGATE THE λ QUESTION. Pool every (replica, frame) whose RMSD exceeds the threshold and ask where on the
    # ladder those frames sit. Endpoint states (0 and N-1) are the PHYSICAL Hamiltonians in a hybrid-topology
    # RBFE, so exceedances there cannot be explained away as softcore behaviour.
    if n_states:
        endpoints = {0, n_states - 1}
        at_endpoint = at_interior = 0
        hist = {}
        for k in sorted(series):
            lk = lam.get(k) or {}
            for i, v in series[k]:
                if v <= LIG_RMSD_MAX_A:
                    continue
                s = lk.get(i)
                if s is None:
                    continue
                hist[s] = hist.get(s, 0) + 1
                if s in endpoints:
                    at_endpoint += 1
                else:
                    at_interior += 1
        out["exceedance_lambda_histogram"] = dict(sorted(hist.items()))
        out["exceedances_at_physical_endpoint_states"] = at_endpoint
        out["exceedances_at_alchemical_interior_states"] = at_interior
        # PERSISTENCE vs INITIATION — two different questions, and the histogram above only answers the first.
        # Replicas exchange λ, so once a replica has departed it keeps contributing over-threshold frames at
        # whatever λ it visits afterwards. The pooled histogram is therefore occupancy-weighted PERSISTENCE of the
        # displaced state, which is informative (a displaced configuration that survives at a physical endpoint is
        # not a softcore artifact) but is NOT evidence about where the departure STARTED.
        #
        # The initiation statistic is one value per replica: the λ it was at on its FIRST over-threshold frame.
        # There are at most n_replicas of these, so it is a small sample and must be read as such — but it is the
        # quantity that separates "the alchemy pushed it out and it never came back" from "it left under a
        # physical Hamiltonian".
        first_hist = {}
        fe_endpoint = fe_interior = 0
        for r in per_replica:
            s = r.get("lambda_at_first_exceed")
            if s is None:
                continue
            first_hist[s] = first_hist.get(s, 0) + 1
            if s in endpoints:
                fe_endpoint += 1
            else:
                fe_interior += 1
        out["first_exceedance_lambda_histogram"] = dict(sorted(first_hist.items()))
        out["first_exceedances_at_physical_endpoint_states"] = fe_endpoint
        out["first_exceedances_at_alchemical_interior_states"] = fe_interior
        out["initiation_note"] = ("first-exceedance counts are one per departing replica (n<=%d), so they are a "
                                  "SMALL SAMPLE — read them as suggestive, not as a rate. Departures initiating at "
                                  "a physical endpoint state cannot be attributed to alchemical softening."
                                  % len(per_replica))
        out["lambda_verdict"] = (
            ("no frame exceeds the threshold, so there is nothing to attribute to a λ state"
             if (at_endpoint + at_interior) == 0 else
             "%d of %d over-threshold (replica, frame) pairs sit at a PHYSICAL ENDPOINT state (0 or %d) — those "
             "cannot be attributed to softcore/alchemical softening, so the modelled complex itself is unstable "
             "there; %d sit in the alchemical interior."
             % (at_endpoint, at_endpoint + at_interior, n_states - 1, at_interior)))
    else:
        out["lambda_verdict"] = ("λ assignments UNAVAILABLE from this reporter — the endpoint-vs-interior question "
                                 "is unanswered, NOT answered in the benign direction")
    ended_out = sum(1 for r in per_replica if r["final_A"] > LIG_RMSD_MAX_A)
    out["n_replicas"] = len(per_replica)
    out["n_replicas_ending_beyond_threshold"] = ended_out
    out["verdict"] = ("%d of %d replicas END beyond the %.1f Å threshold; class counts %s. "
                      "DISPLACED_AND_STAYED dominating means the ligand left and resampling will not fix it; "
                      "EXCURSION_AND_RETURNED dominating means the ENDPOINT metric is what misleads, not the "
                      "sampling; a JUMP prefix means suspect bookkeeping (imaging/indexing), because nothing can "
                      "physically move that far in one checkpoint interval."
                      % (ended_out, len(per_replica), LIG_RMSD_MAX_A, classes))
    out["status"] = "ok — %d frames from iteration %s to %s" % (len(used), used[0], used[-1])
    return out


def _ligand_pose_block(reporter, iter_a, iter_b):
    """THE MANDATED LIGAND-ONLY POSE RMSD, over EVERY replica rather than replica 0.

    Two things this fixes beyond the observable itself. (a) Replica k's sampler state is a CONTINUOUS
    configuration — replicas exchange λ, not coordinates — so replica k at iteration 0 and at iteration N is the
    same trajectory, and 12 replicas give 12 independent escape tests instead of 1. (b) The previous single-replica
    read is what left the residual large-displacement tail undiagnosable: with the whole distribution in hand,
    a tail present in one replica and absent in eleven is an indexing artifact, and one present in all twelve is
    physics. The flag uses the WORST replica: a ligand that leaves the pocket in any replica is a real problem,
    and taking the max cannot manufacture a pass."""
    import numpy as np
    ident = _ligand_atoms(reporter)
    out = {"identification": {k: v for k, v in ident.items()
                              if k not in ("ligand_atom_indices", "ligand_heavy_indices", "protein_atom_indices",
                                           "protein_heavy_indices", "protein_chains")},
           "ligand_rmsd_A": None}
    if ident.get("ligand_atom_indices") is None:
        out["status"] = ident.get("status", "ligand not identified")
        return out
    subset = [int(v) for v in (getattr(reporter, "analysis_particle_indices", None) or [])]
    row_of = {v: r for r, v in enumerate(subset)}
    lig_rows = [row_of[i] for i in ident["ligand_heavy_indices"] if i in row_of]
    prot_rows = [row_of[i] for i in ident["protein_heavy_indices"] if i in row_of]
    chain_rows = [[row_of[i] for i in c if i in row_of] for c in ident.get("protein_chains", [])]
    out["n_ligand_heavy_rows"] = len(lig_rows)
    out["n_protein_heavy_rows"] = len(prot_rows)
    if len(lig_rows) != len(ident["ligand_heavy_indices"]) or not lig_rows:
        out["status"] = ("ligand heavy atoms are not all present in the stored analysis subset (%d of %d) — "
                         "no pose RMSD is computable from this trajectory"
                         % (len(lig_rows), len(ident["ligand_heavy_indices"])))
        return out
    try:
        sa = reporter.read_sampler_states(iteration=iter_a, analysis_particles_only=True)
        sb = reporter.read_sampler_states(iteration=iter_b, analysis_particles_only=True)
    except Exception as e:  # noqa: BLE001
        out["status"] = "read_sampler_states failed: %s: %s" % (type(e).__name__, e)
        return out
    if not sa or not sb:
        out["status"] = "no sampler states at iterations %s/%s" % (iter_a, iter_b)
        return out
    # INDEPENDENT CROSS-CHECK. Re-derive the ligand from frame-0 geometry alone — a covalent-cutoff neighbour
    # graph over the stored subset, no System, no bond table, no force names. It can be wrong in ways the bond
    # graph cannot (a molecule split across the periodic boundary fragments; nothing else at 1.9 Å joins two
    # molecules), so agreement atom-for-atom means the assignment does not rest on either route being right.
    # Disagreement is REPORTED, never silently resolved in favour of the answer we already have.
    lig_all_rows = sorted(row_of[i] for i in ident["ligand_atom_indices"] if i in row_of)
    try:
        A0, _ = _replica_coords(sa[0])
        dcomps = molecules_from_edges(int(A0.shape[0]), _distance_edges(A0))
        dinfo = classify_components(dcomps, None)
        dlig = dinfo.get("ligand")
        out["independent_distance_check"] = {
            "n_components": dinfo["n_components"], "n_candidates": dinfo["n_ligand_sized_candidates"],
            "identified": dlig is not None, "n_atoms": (len(dlig) if dlig else None),
            "agrees_with_bond_graph": (bool(dlig is not None and sorted(dlig) == lig_all_rows)),
            "note": ("two fully independent identifications; disagreement does NOT invalidate the bond-graph "
                     "answer (a PBC-split molecule fragments the distance graph) but must be read before "
                     "trusting the number"),
        }
    except Exception as e:  # noqa: BLE001
        out["independent_distance_check"] = {"status": "%s: %s" % (type(e).__name__, e)}

    per_replica, pose_vals, internal_vals, contact_vals = [], [], [], []
    for k in range(min(len(sa), len(sb))):
        A, _ = _replica_coords(sa[k])
        B, M = _replica_coords(sb[k])
        if A is None or B is None:
            continue
        B, applied = _min_image(A, B, M)
        contact_rows = _contact_ligand_rows(A, lig_rows, prot_rows)
        pose = _kabsch_rmsd(A, B, prot_rows, lig_rows)
        contact = _kabsch_rmsd(A, B, prot_rows, contact_rows)
        internal = _kabsch_rmsd(A, B, lig_rows, lig_rows)
        per_chain = [_kabsch_rmsd(A, B, cr, lig_rows) for cr in chain_rows if cr]
        rec = {"replica": k, "pose_rmsd_A": pose, "internal_rmsd_A": internal,
               "contact_pose_rmsd_A": contact,
               "n_contact_heavy": len(contact_rows),
               "per_chain_pose_rmsd_A": [None if v is None else round(v, 3) for v in per_chain],
               "min_over_chains_A": (min([v for v in per_chain if v is not None]) if any(
                   v is not None for v in per_chain) else None),
               "minimum_image_corrected": applied}
        per_replica.append(rec)
        if pose is not None:
            pose_vals.append(pose)
        if contact is not None:
            contact_vals.append(contact)
        if internal is not None:
            internal_vals.append(internal)
    # ⚠ THE SOLVENT LEG HAS NO POSE CHECK AT ALL, AND FLAGGING ANYTHING THERE MANUFACTURES A FAILURE.
    # First cut of this function flagged the solvent leg on the ligand's INTERNAL RMSD, reasoning that with no
    # receptor to superpose on, internal geometry was the only integrity measure left. On the real r0 solvent
    # leg that returned ligand_stable_ok=FALSE and technical_failure=TRUE (GH run 30167976061) — and via
    # ternary_fep_reduce._diagnostics_ok() that would have handed valB_mini a HARD FAIL. It is wrong for the
    # same reason defect #7 was wrong: a free PROTAC in bulk water is SUPPOSED to explore conformations, so its
    # internal RMSD exceeding a 4 Å POSE-COLLAPSE threshold is physics, not a broken run. LIG_RMSD_MAX_A was
    # written for a ligand escaping a pocket; a leg with no pocket has nothing that check can be about.
    # So the solvent leg's ligand check is NOT APPLICABLE — neither passed, nor failed, nor unmeasured. The
    # internal RMSD is still reported, as information.
    solvent_leg = not prot_rows
    if not pose_vals and not (solvent_leg and internal_vals):
        out["status"] = "positions unavailable on every replica at iterations %s/%s" % (iter_a, iter_b)
        return out
    if solvent_leg:
        out["check_applicable"] = False
    # THE FLAG IS THE CONTACT-MOIETY POSE RMSD, not the whole-ligand one. See _contact_ligand_rows for why: the
    # whole-ligand observable cannot distinguish a bound warhead leaving its pocket (a real failure) from the
    # distal warhead of a PROTAC moving in a BINARY complex (the expected physics of a state with only one
    # protein), and it flagged the r0 binary leg at 16.636 Å for the second reason. Both numbers are reported; the
    # threshold is applied to the one it was written for.
    #
    # NOT A LOOSENING. Three things keep this from being a way to make a failure disappear:
    #   (1) it still takes the WORST replica, so a single escaping replica fails the leg;
    #   (2) if no contact moiety can be determined the check is UNMEASURED, never passed — an empty contact set
    #       means the ligand had no receptor contact in the reference frame at all, which is itself a finding and
    #       must not read as "stable";
    #   (3) the whole-ligand max/median stay in the record, so a large value is still visible and still has to be
    #       explained, it just no longer *silently* decides a gate it cannot decide correctly.
    contact_flag = None if solvent_leg else (float(max(contact_vals)) if contact_vals else None)
    n_contact = [r["n_contact_heavy"] for r in per_replica if r.get("n_contact_heavy") is not None]
    contact_unmeasured = (not solvent_leg) and contact_flag is None
    flagged = None if solvent_leg else contact_flag
    out.update({
        "status": ("NOT APPLICABLE — solvent leg: no receptor, so there is no pose to collapse and no pocket to "
                   "escape. The ligand's internal RMSD over %d replicas is reported as information and is NOT "
                   "compared to LIG_RMSD_MAX_A (a free PROTAC exploring conformations in water is physics)."
                   % len(internal_vals)) if solvent_leg else
                  ("UNMEASURED — no ligand heavy atom is within %.2f nm of the receptor in the reference frame, "
                   "so there is no contact moiety whose displacement the escape threshold could be about. NOT "
                   "passed: a ligand with no receptor contact at t0 is itself a finding."
                   % CONTACT_CUTOFF_NM) if contact_unmeasured else
                  ("ok — CONTACT-MOIETY heavy-atom pose RMSD (receptor-superposed) over %d replicas; the "
                   "whole-ligand value is reported alongside as information" % len(contact_vals)),
        "flagged_observable": ("none (not applicable)" if solvent_leg else
                              "none (no contact moiety)" if contact_unmeasured else
                              "receptor_superposed_contact_moiety_pose_rmsd"),
        "iterations_compared": [int(iter_a), int(iter_b)],
        "n_replicas": len(internal_vals if solvent_leg else pose_vals),
        "ligand_rmsd_A": flagged,                        # the flag: worst replica (conservative)
        "contact_pose_rmsd_max_A": (float(max(contact_vals)) if contact_vals else None),
        "contact_pose_rmsd_median_A": (float(np.median(contact_vals)) if contact_vals else None),
        "n_contact_heavy_min": (int(min(n_contact)) if n_contact else None),
        "n_contact_heavy_max": (int(max(n_contact)) if n_contact else None),
        "contact_cutoff_nm": CONTACT_CUTOFF_NM,
        "whole_ligand_note": ("pose_rmsd_* below are over ALL ligand heavy atoms and are INFORMATION, not the "
                              "flag. In a binary complex they are expected to be large: only one warhead is "
                              "bound, so the linker and distal warhead are in solvent by construction."),
        "pose_rmsd_max_A": (float(max(pose_vals)) if pose_vals else None),
        "pose_rmsd_median_A": (float(np.median(pose_vals)) if pose_vals else None),
        "pose_rmsd_min_A": (float(min(pose_vals)) if pose_vals else None),
        "internal_rmsd_max_A": (float(max(internal_vals)) if internal_vals else None),
        "internal_rmsd_median_A": (float(np.median(internal_vals)) if internal_vals else None),
        "per_replica": per_replica,
    })
    return out


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

        # THE MANDATED OBSERVABLE, computed first and independently of the solute proxy below. Wrapped so that a
        # failure here degrades to a status string and leaves the flag unmeasured — it must never be able to
        # invent either a pass or a fail, which is exactly what the previous two implementations did.
        try:
            ligand = _ligand_pose_block(reporter, 0, last_ckpt)
        except Exception as e:  # noqa: BLE001
            ligand = {"status": "ligand pose block raised %s: %s" % (type(e).__name__, e), "ligand_rmsd_A": None}
        # DISCRIMINATOR for the unexplained large-displacement tail (recorded as cause-unknown on 2026-07-25):
        # adjacent checkpointed frames are one interval apart, so nothing can physically have moved far. A tail
        # that persists between them is a bookkeeping/indexing problem; one that vanishes means iteration 0 is
        # simply not comparable to iteration N (pre-equilibration configuration, or a different NPT box).
        adjacent = None
        if interval > 1 and last_ckpt >= 2 * interval:
            try:
                adjacent = _ligand_pose_block(reporter, last_ckpt - interval, last_ckpt)
            except Exception as e:  # noqa: BLE001
                adjacent = {"status": "adjacent-frame block raised %s: %s" % (type(e).__name__, e)}
        # TIME-RESOLVED, because two frames cannot answer the question the two-frame number RAISES. See
        # _contact_pose_timeseries: a 16 Å endpoint displacement is consistent with a slow unbind, a transient
        # excursion that came back, and a one-off jump, and those have completely different consequences for
        # whether ΔG_binary is usable. Free: the positions for every checkpointed iteration are already inside the
        # .nc/.chk this function has open, so this costs reads and no extra GCS traffic.
        timeseries = None
        try:
            timeseries = _contact_pose_timeseries(reporter, last_ckpt, interval)
        except Exception as e:  # noqa: BLE001
            timeseries = {"status": "timeseries raised %s: %s" % (type(e).__name__, e)}

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
            # The cell is NOT orthorhombic — OpenFE solvates in a reduced-form triclinic box, so componentwise
            # d -= L*round(d/L) is invalid and the first attempt correctly refused to apply it (run 30157333131:
            # minimum_image_corrected=false, "non-orthorhombic"). The general form works for any lattice: take the
            # displacement to FRACTIONAL coordinates, round off whole lattice translations there, and convert back.
            # Exact for the reduced form OpenMM enforces, and it reduces to the diagonal case when the cell is
            # rectangular — so there is no longer a shape this silently skips.
            M = None
            try:
                bv = subN[0].box_vectors
                M = np.asarray([[float(bv[i][j].value_in_unit(bv.unit)) for j in range(3)] for i in range(3)])
            except Exception:  # noqa: BLE001
                try:                                  # some versions hand back a plain Vec3 list (already nm)
                    bv = subN[0].box_vectors
                    M = np.asarray([[float(bv[i][j]) for j in range(3)] for i in range(3)])
                except Exception:  # noqa: BLE001
                    M = None
            unwrapped = False
            if M is not None and abs(float(np.linalg.det(M))) > 1e-9:
                d = b - a
                frac = d @ np.linalg.inv(M)           # rows of M are the lattice vectors
                d = d - np.round(frac) @ M            # fold into the primitive parallelepiped
                # Belt-and-braces neighbour search: after the fold, also try the 27 adjacent lattice translations
                # and keep the shortest per atom. For skewed cells the parallelepiped fold can in general leave a
                # non-minimal image, and this is the standard brute-force fix.
                #
                # ⚠ HONEST NOTE ON WHY IT IS HERE. I added this believing it would explain the residual large
                # displacements in run 30157501491 (after folding: p99 71.5 Å, max 128.1 Å against a 126.3 Å edge)
                # on THIS box — a reduced-form truncated octahedron, rows [126.3,0,0], [0,126.3,0], [63.1,63.1,89.3].
                # That belief is REFUTED by direct test: over 4000 random small displacements plus whole lattice
                # translations on this exact cell, fold-only recovers the true displacement with worst error
                # 0.000 Å — identical to fold + 27-search. So the fold was already minimal here and the search is a
                # no-op on this system; it is retained only as insurance for cells where it is not.
                # ⇒ THE RESIDUAL ~1.3 % TAIL IS THEREFORE NOT A MINIMUM-IMAGE ARTEFACT, AND ITS CAUSE IS UNKNOWN.
                # Candidates NOT yet discriminated: an NPT box that differs between the two frames (the unwrap uses
                # frame N's vectors); iteration 0 being a pre-equilibration configuration rather than the start of
                # production; or read_sampler_states index [0] not referring to the same continuous replica at both
                # iterations. Do not guess between these in a write-up — the discriminator is to compare successive
                # CHECKPOINTED frames (e.g. 1960 vs 2000, one interval apart) where no configuration can have moved
                # far: a tail that persists between adjacent frames is a bookkeeping/indexing problem, one that
                # vanishes means frame 0 is simply not comparable to frame 2000.
                best = (d ** 2).sum(axis=1)
                shifts = [(i, j, k) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)
                          if (i, j, k) != (0, 0, 0)]
                for s in shifts:
                    cand = d + np.asarray(s, dtype=float) @ M
                    n2 = (cand ** 2).sum(axis=1)
                    take = n2 < best
                    if take.any():
                        d[take] = cand[take]
                        best[take] = n2[take]
                b = a + d
                unwrapped = True
            box = (np.abs(M).max(axis=1) if M is not None else None)   # per-vector length scale, for reporting

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
            # it is. As of 2026-07-25 the ligand-only pose RMSD is computed separately (`ligand`, above) from
            # atom indices DERIVED from the serialized hybrid System, so this proxy is now informational only and
            # `ligand_rmsd_A` — the flagged quantity — no longer comes from it.
            return {"status": ("ok (minimum-image-corrected, superposed RMSD over the solute subset — %d of %d "
                               "atoms; structural-stability proxy, NOT the ligand-only pose RMSD)"
                               % (n_idx, n_all)) if unwrapped else
                              ("NOT minimum-image corrected (box unavailable or non-orthorhombic) — the value is "
                               "inflated by periodic wrapping and is informational only"),
                    "solute_superposed_rmsd_A": rmsd,
                    "ligand_rmsd_A": ligand.get("ligand_rmsd_A"),
                    "ligand": ligand, "ligand_adjacent_frame": adjacent,
                    "ligand_contact_pose_timeseries": timeseries,
                    "minimum_image_corrected": unwrapped,
                    "box_matrix_A": ([[round(v * 10.0, 3) for v in row] for row in M.tolist()]
                                     if M is not None else None),
                    "box_is_orthorhombic": (bool(np.abs(M - np.diag(np.diag(M))).max() <= 1e-6)
                                            if M is not None else None),
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
                "whole_system_unaligned_rmsd_A": rmsd_all,
                "ligand_rmsd_A": ligand.get("ligand_rmsd_A"),
                "ligand": ligand, "ligand_adjacent_frame": adjacent,
                    "ligand_contact_pose_timeseries": timeseries,
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


def _ligand_size_cross_check(legs):
    """A FREE, INDEPENDENT check on the ligand identification, available only because the cycle has a solvent leg.

    OpenFE stores 'not water' as the analysis-particle subset. In the SOLVENT leg there is no protein, so that
    subset IS the hybrid ligand and nothing else — the run of 2026-07-25 stored 120 of 5304 particles there. That
    count is a measurement of the ligand's size made by an entirely different route (OpenFE's own selection at
    setup time) than the bond-graph identification used on the complex legs. If the complex legs' identified
    ligand has a different atom count, one of the two is wrong and no pose RMSD from this report should be
    trusted. Reported either way; it costs nothing and it is the only cross-validation the artifacts permit."""
    solvent_n, solvent_subset, complex_n = None, None, {}
    for leg in legs:
        tag = leg.get("tag", "")
        st = (leg.get("structural") or {})
        ident = ((st.get("ligand") or {}).get("identification") or {})
        n_lig = ident.get("n_ligand_atoms")
        if "solvent" in tag:
            # ⚠ COMPARE LIGAND TO LIGAND. The first version took the solvent leg's raw analysis-particle count
            # as "the ligand", on the reasoning that a solvent leg has no protein so 'not water' must be the
            # ligand alone. The real run said otherwise: 120 stored particles against a 110-atom identified
            # ligand (run 30168804028), and the check correctly refused to certify. The 10 extra are the
            # neutralising COUNTER-IONS, which are also 'not water'. So use the solvent leg's own identified
            # ligand and keep the subset size as context, rather than comparing a ligand to a ligand-plus-ions.
            solvent_n = n_lig
            solvent_subset = ident.get("n_analysis_particles")
        elif n_lig is not None:
            complex_n[tag] = n_lig
    if solvent_n is None or not complex_n:
        return {"status": "not computable (need the solvent leg's identified ligand AND at least one complex "
                          "leg's)", "solvent_identified_ligand_atoms": solvent_n,
                "solvent_subset_atoms": solvent_subset, "complex_legs": complex_n}
    agree = all(v == solvent_n for v in complex_n.values())
    return {"_what": "the ligand identified INDEPENDENTLY in each environment — a ~5 k-particle solvent box and "
                     "a ~142 k-particle four-chain ternary assembly are different systems whose hybrid ligand "
                     "must nonetheless have the same atom count",
            "solvent_identified_ligand_atoms": solvent_n,
            "solvent_analysis_subset_atoms": solvent_subset,
            "solvent_subset_minus_ligand": ((solvent_subset - solvent_n)
                                            if (solvent_subset and solvent_n) else None),
            "_subset_note": "the solvent leg's 'not water' subset is ligand PLUS neutralising counter-ions, so "
                            "subset size is NOT the ligand size — comparing the two is what made this check "
                            "fire spuriously on its first run",
            "complex_legs_identified_ligand_atoms": complex_n,
            "agree": agree,
            "verdict": ("CONSISTENT — the ligand identification is corroborated by OpenFE's own atom selection"
                        if agree else
                        "INCONSISTENT — the two routes disagree; do not trust any ligand RMSD in this report "
                        "until the discrepancy is explained")}


def analyze_all():
    os.makedirs(CKPT, exist_ok=True)
    ncs = _find_nc_files()
    legs = [analyze_leg(p, tag) for tag, p in sorted(ncs.items())]
    n_fail = sum(1 for l in legs if l.get("technical_failure"))
    report = {"ligand_size_cross_check": _ligand_size_cross_check(legs)}
    report.update({
        "_what": "OpenFE/openmmtools convergence analysis on committed MultiState .nc (reviewer change #1)",
        "_gate": "run on seed-0 BEFORE ternary seed-1; technical_failure feeds the reducer PASS/NO-GO/INDETERMINATE",
        "thresholds": {"overlap_scalar_min": OVERLAP_SCALAR_MIN, "overlap_bottleneck_min": OVERLAP_BOTTLENECK_MIN,
                       "mix_subdominant_max": MIX_SUBDOMINANT_MAX, "equil_fraction_max": EQUIL_FRACTION_MAX,
                       "fwd_rev_gap_max_kcal": FWD_REV_GAP_MAX_KCAL,
                       "plateau_full_half_max_kcal": PLATEAU_FULL_HALF_MAX_KCAL,
                       "quarter_block_max_kcal": QUARTER_BLOCK_MAX_KCAL, "lig_rmsd_max_A": LIG_RMSD_MAX_A},
        "n_legs_analyzed": len(legs), "n_technical_failures": n_fail, "legs": legs,
    })
    out = os.path.join(CKPT, "ternary_convergence.json")
    json.dump(report, open(out, "w"), indent=2, default=str)
    print("[tfep-converge] wrote %s (%d legs, %d technical failures)" % (out, len(legs), n_fail), flush=True)
    # A COMPACT SUMMARY, because the full report is ~2500 lines of CI log and the four numbers that decide
    # anything were being hunted for by eye. Printed last so it is the tail of the job log.
    # Written to a file as well as printed, because the caller cats the ~2500-line JSON after this and a
    # summary buried 2500 lines up is not a summary. The workflow cats this file LAST.
    lines = ["==== ternary convergence SUMMARY ===="]
    for leg in legs:
        st = (leg.get("structural") or {})
        lg = (st.get("ligand") or {})
        ident = (lg.get("identification") or {})
        xc = (ident.get("frozen_heavy_atom_cross_check") or {})
        def _r(key):
            v = lg.get(key)
            return round(v, 3) if v is not None else "n/a"
        # BOTH observables on the line, with the FLAGGED one first and the whole-ligand one explicitly marked as
        # information. Printing only the flagged value would hide a 16 Å whole-ligand excursion; printing only
        # the whole-ligand value is what made the r0 binary leg read as a technical failure. Which number the
        # threshold is applied to has to be legible from the summary itself.
        lines.append("%-34s complete=%-5s tech_fail=%-5s | ligand n=%s heavy=%s H_mass=%s | "
                     "FLAG contact_pose max=%s med=%s (n_contact=%s-%s) | info whole_ligand_pose max=%s med=%s | "
                     "flagged=%s | frozen-heavy-xcheck=%s"
                     % (leg.get("tag"), leg.get("diagnostics_complete"), leg.get("technical_failure"),
                        ident.get("n_ligand_atoms"), ident.get("n_ligand_heavy_atoms"),
                        ident.get("hydrogen_mass_da"),
                        _r("contact_pose_rmsd_max_A"), _r("contact_pose_rmsd_median_A"),
                        lg.get("n_contact_heavy_min", "n/a"), lg.get("n_contact_heavy_max", "n/a"),
                        _r("pose_rmsd_max_A"), _r("pose_rmsd_median_A"),
                        lg.get("flagged_observable"), xc.get("verdict", "n/a")))
        # The time-resolved shape on its own line, because it is what says whether a large two-frame number means
        # the ligand LEFT or that the endpoint frame merely caught it out — different consequences for whether the
        # leg is salvageable, and not inferable from the numbers above.
        ts = (st.get("ligand_contact_pose_timeseries") or {})
        if ts.get("per_replica"):
            lines.append("%-34s   time-resolved: %s ending beyond %.1f A of %s replicas | classes %s | frames %s (iter %s..%s)"
                         % ("", ts.get("n_replicas_ending_beyond_threshold"), LIG_RMSD_MAX_A,
                            ts.get("n_replicas"), ts.get("class_counts"), ts.get("frames_used"),
                            (ts.get("iterations") or ["?"])[0], (ts.get("iterations") or ["?"])[-1]))
            # WHERE ON THE λ LADDER. Both endpoints are physical in a hybrid-topology RBFE, so exceedances at
            # state 0 or N-1 cannot be blamed on softcore softening — that is the line between "the leg wants a
            # restraint" and "the modelled complex is wrong", and it belongs in the summary.
            ep = ts.get("exceedances_at_physical_endpoint_states")
            if ep is not None:
                lines.append("%-34s   lambda PERSISTENCE (occupancy-weighted, all frames): %s at PHYSICAL ENDPOINT "
                             "states, %s in the alchemical interior (of %s states) | histogram %s"
                             % ("", ep, ts.get("exceedances_at_alchemical_interior_states"),
                                ts.get("n_lambda_states"), ts.get("exceedance_lambda_histogram")))
                # INITIATION is the sharper question and a smaller sample — one value per departing replica.
                lines.append("%-34s   lambda INITIATION (first exceedance per replica, small n): %s at PHYSICAL "
                             "ENDPOINT states, %s in the interior | histogram %s"
                             % ("", ts.get("first_exceedances_at_physical_endpoint_states"),
                                ts.get("first_exceedances_at_alchemical_interior_states"),
                                ts.get("first_exceedance_lambda_histogram")))
            elif ts.get("lambda_verdict"):
                lines.append("%-34s   lambda: %s" % ("", str(ts["lambda_verdict"])[:150]))
        elif ts.get("status"):
            lines.append("%-34s   time-resolved: %s" % ("", str(ts.get("status"))[:150]))
    lines.append("ligand-size cross-check: %s" % report["ligand_size_cross_check"].get(
        "verdict", report["ligand_size_cross_check"].get("status")))
    txt = "\n".join(lines)
    open(os.path.join(CKPT, "ternary_convergence_summary.txt"), "w").write(txt + "\n")
    print(txt, flush=True)
    return report


if __name__ == "__main__":
    analyze_all()
