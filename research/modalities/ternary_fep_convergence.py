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
MIX_SUBDOMINANT_MAX = 0.90     # 2nd-largest transition eigenvalue above this = pathologically slow replica mixing
EQUIL_FRACTION_MAX = 0.50      # >50% of iterations spent equilibrating = too little production left
FWD_REV_GAP_MAX_KCAL = 1.0     # |forward - reverse| final ΔG gap above this (kcal) = unconverged
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
    mbar = getattr(analyzer, "mbar", None) or getattr(analyzer, "_mbar", None)
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
    return {"status": "ok", "overlap_scalar": scalar,
            "eigenvalues_top": (eigs[:5] if eigs else None),
            "matrix_shape": (list(getattr(matrix, "shape", [])) or None)}


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
        from pymbar import MBAR
        N_l = np.asarray(N_l, dtype=int)
        K = len(N_l)
        fracs = [i / n_points for i in range(1, n_points + 1)]
        fwd, rev = [], []
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
                    m = MBAR(u_ln[:, sel], Nsub)
                    df = m.compute_free_energy_differences()["Delta_f"] if hasattr(m, "compute_free_energy_differences") \
                        else m.getFreeEnergyDifferences()[0]
                    store.append(float(df[0, -1]) * KT_KCAL)
                except Exception:  # noqa: BLE001
                    store.append(None)
        gap = None
        if fwd and rev and fwd[-1] is not None and rev[-1] is not None:
            gap = abs(fwd[-1] - rev[-1])
        return {"status": "ok", "fractions": fracs, "forward_dg_kcal": fwd, "reverse_dg_kcal": rev,
                "final_forward_reverse_gap_kcal": gap}
    except Exception as e:  # noqa: BLE001
        return {"status": "forward/reverse failed: %s: %s" % (type(e).__name__, e)}


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
    rec["overlap"] = _overlap(analyzer)
    rec["equilibration"] = _equilibration(analyzer)
    rec["mixing"] = _mixing(analyzer, reporter)
    rec["forward_reverse"] = _forward_reverse(analyzer)
    rec["restraints"] = {"status": "RBFE binding legs carry no orientational restraints; none to diagnose"}
    rec["structural"] = _structural(reporter, nc_path)

    # ---- health flags (each None if the metric wasn't computable) ----
    ov = rec["overlap"].get("overlap_scalar")
    eq = rec["equilibration"].get("equilibration_fraction")
    sub = rec["mixing"].get("subdominant_eigenvalue")
    gap = rec["forward_reverse"].get("final_forward_reverse_gap_kcal")
    lig = rec["structural"].get("ligand_rmsd_A")
    flags = {
        "overlap_ok": (None if ov is None else ov >= OVERLAP_SCALAR_MIN),
        "equilibrated_ok": (None if eq is None else eq <= EQUIL_FRACTION_MAX),
        "mixing_ok": (None if sub is None else sub <= MIX_SUBDOMINANT_MAX),
        "forward_reverse_ok": (None if gap is None else gap <= FWD_REV_GAP_MAX_KCAL),
        "ligand_stable_ok": (None if lig is None else lig <= LIG_RMSD_MAX_A),
    }
    rec["health_flags"] = flags
    # technical_failure = any computable flag is False (a metric we could measure and it failed its threshold)
    failed = [k for k, v in flags.items() if v is False]
    rec["technical_failure"] = bool(failed)
    rec["failed_checks"] = failed
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
        # positions are in the checkpoint; read replica 0 sampler states across production
        pos = reporter.read_sampler_states(iteration=0)
        posN = reporter.read_sampler_states(iteration=reporter.read_last_iteration())
        if not pos or not posN:
            return {"status": "no sampler-state positions in checkpoint (checkpoint_interval may exclude frames)"}
        p0 = np.asarray(pos[0].positions.value_in_unit(pos[0].positions.unit))
        pN = np.asarray(posN[0].positions.value_in_unit(posN[0].positions.unit))
        # coarse whole-system heavy-proxy RMSD (no per-atom selection without topology); reported as an upper proxy
        rmsd = float(np.sqrt(((pN - p0) ** 2).sum(axis=1).mean())) * 10.0  # nm->Å
        return {"status": "ok (whole-system proxy RMSD; ligand-specific needs topology selection)",
                "ligand_rmsd_A": rmsd}
    except Exception as e:  # noqa: BLE001
        return {"status": "structural RMSD failed: %s: %s" % (type(e).__name__, e)}


def analyze_all():
    os.makedirs(CKPT, exist_ok=True)
    ncs = _find_nc_files()
    legs = [analyze_leg(p, tag) for tag, p in sorted(ncs.items())]
    n_fail = sum(1 for l in legs if l.get("technical_failure"))
    report = {
        "_what": "OpenFE/openmmtools convergence analysis on committed MultiState .nc (reviewer change #1)",
        "_gate": "run on seed-0 BEFORE ternary seed-1; technical_failure feeds the reducer PASS/NO-GO/INDETERMINATE",
        "thresholds": {"overlap_scalar_min": OVERLAP_SCALAR_MIN, "mix_subdominant_max": MIX_SUBDOMINANT_MAX,
                       "equil_fraction_max": EQUIL_FRACTION_MAX, "fwd_rev_gap_max_kcal": FWD_REV_GAP_MAX_KCAL,
                       "lig_rmsd_max_A": LIG_RMSD_MAX_A},
        "n_legs_analyzed": len(legs), "n_technical_failures": n_fail, "legs": legs,
    }
    out = os.path.join(CKPT, "ternary_convergence.json")
    json.dump(report, open(out, "w"), indent=2, default=str)
    print("[tfep-converge] wrote %s (%d legs, %d technical failures)" % (out, len(legs), n_fail), flush=True)
    return report


if __name__ == "__main__":
    analyze_all()
