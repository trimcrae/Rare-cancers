#!/usr/bin/env python3
"""Pure orchestration logic for the spot-priced, parallel selectivity FEP (no IO / no OpenMM → unit-tested).

The FEP is embarrassingly parallel over **units = (receptor, leg, window)**. This module:
  - enumerates the units for a selectivity FEP (receptors × legs × λ-windows),
  - balances them across K spot Training-job shards,
  - computes the RESUME set (which units are still pending given the checkpoints already in S3),
  - does the ΔG_bind / ΔΔG bookkeeping (leg ΔGs → per-receptor binding ΔG → paralogue ΔΔG).

Design notes are in nr4a3-fep-plan.md. Everything here is deterministic and side-effect-free so the driver /
submitter / reducer can be tested without AWS or a GPU.
"""

# Default selectivity-FEP shape: absolute binding FEP per receptor, two alchemical legs.
RECEPTORS = ("nr4a3", "nr4a1", "nr4a2")
LEGS = ("complex", "solvent")          # ΔG_bind = ΔG_solvent(decouple) − ΔG_complex(decouple) + restraint_corr


def unit_id(receptor, leg, window):
    """Stable string id for a (receptor, leg, window) unit — used as the checkpoint/result filename stem."""
    return f"{receptor}__{leg}__w{int(window):03d}"


def enumerate_units(receptors=RECEPTORS, legs=LEGS, n_windows=12):
    """All atomic work units for the FEP, in a stable order. Each is a dict; unit_id() is its key."""
    if n_windows < 2:
        raise ValueError("n_windows must be >= 2 (need endpoints for a λ schedule)")
    units = []
    for r in receptors:
        for leg in legs:
            for w in range(n_windows):
                lam = w / (n_windows - 1)          # linear λ 0..1 (protocol may remap; this is the schedule id)
                units.append({"id": unit_id(r, leg, w), "receptor": r, "leg": leg,
                              "window": w, "lambda": round(lam, 6)})
    return units


def assign_shards(units, n_shards):
    """Balance units across n_shards shards (greedy round-robin by count). Returns list[list[unit]] of length
    min(n_shards, len(units)) with sizes differing by at most 1. Deterministic (input order preserved)."""
    if n_shards < 1:
        raise ValueError("n_shards must be >= 1")
    k = min(n_shards, len(units))
    shards = [[] for _ in range(k)]
    for i, u in enumerate(units):
        shards[i % k].append(u)
    return shards


def pending_units(units, done_ids):
    """Resume filter: the units whose id is NOT already in done_ids (the set of completed checkpoints in S3)."""
    done = set(done_ids or ())
    return [u for u in units if u["id"] not in done]


def shard_plan(receptors=RECEPTORS, legs=LEGS, n_windows=12, n_shards=8, done_ids=()):
    """Full plan: (pending units sharded across up to n_shards, summary counts). The submitter launches one
    spot job per non-empty shard; a resumed run re-plans over only the pending units."""
    units = enumerate_units(receptors, legs, n_windows)
    pend = pending_units(units, done_ids)
    shards = assign_shards(pend, n_shards) if pend else []
    return {
        "n_units_total": len(units),
        "n_units_pending": len(pend),
        "n_shards": len(shards),
        "shards": shards,
        "per_shard_sizes": [len(s) for s in shards],
    }


# ---- reduction bookkeeping (leg ΔGs -> binding ΔG -> selectivity ΔΔG) ----

def binding_dg(leg_dg, restraint_corr=0.0):
    """ΔG_bind for one receptor from its two decoupling-leg ΔGs.
    Convention: each leg ΔG is ΔG(λ:0→1) = decoupling (interactions ON→OFF). Then
        ΔG_bind = ΔG_decouple(solvent) − ΔG_decouple(complex) + restraint_correction.
    (Standard double-decoupling / ABFE identity; restraint_corr is the analytical free energy of releasing the
    Boresch restraint to standard state, ≥ 0, supplied by the compute step.)"""
    if "solvent" not in leg_dg or "complex" not in leg_dg:
        raise ValueError("need both 'solvent' and 'complex' leg ΔG to form ΔG_bind")
    return leg_dg["solvent"] - leg_dg["complex"] + restraint_corr


def selectivity_ddg(binding_by_receptor, reference="nr4a3"):
    """ΔΔG selectivity of the reference receptor vs each other: ΔΔG = ΔG_bind(ref) − ΔG_bind(other).
    MORE NEGATIVE ΔG_bind = tighter; a NR4A3-selective binder has ΔG_bind(NR4A3) < ΔG_bind(paralogue),
    i.e. ΔΔG < 0. Returns {other: ΔΔG} (negative = reference-selective)."""
    if reference not in binding_by_receptor:
        raise ValueError(f"reference {reference} missing from binding ΔGs")
    ref = binding_by_receptor[reference]
    return {r: round(ref - dg, 4) for r, dg in binding_by_receptor.items() if r != reference}


def combine_error(sd_ref, sd_other):
    """Propagate independent per-receptor ΔG_bind SDs into the ΔΔG SD (quadrature)."""
    return (sd_ref ** 2 + sd_other ** 2) ** 0.5
