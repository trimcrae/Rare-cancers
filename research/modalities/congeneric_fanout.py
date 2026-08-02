#!/usr/bin/env python3
"""
STEP 1 FAN-OUT (RUNG 4, `step1_fanout_cmpd19`) — pure core: unit enumeration, scoping, bookkeeping.

WHAT THIS IS. The pilot (`step1_pilot_cmpd19`, RUNG 2) ran ONE congeneric RBFE edge
(`e_zaienne_cmpd19__cw_ev_5nh2`, 5-Br -> 5-NH2) end-to-end on one nr4a3_design druggable frame and CONVERGED
(ddG_bind = +1.84 +/- 0.36 kcal/mol). This module turns the frozen perturbation map
(`congeneric-rbfe-map.json`) into the FAN-OUT unit list the Vast launcher submits 8-wide.

ROLE SPLIT (mirrors rbfe_edges.py -> nr4a3_rbfe.py -> nr4a3_rbfe_sagemaker.py):
  * THIS module is PURE — stdlib only, no rdkit/boto3/openfe, no I/O beyond reading the two frozen JSONs.
    It is unit-tested directly, so the scoping decisions below cannot drift silently.
  * `congeneric_pose_stage.py` (rdkit) builds the common-mode docked poses the units consume.
  * `congeneric_fanout_vast.py` submits/collects the units on Vast.
  * `nr4a3_rbfe.py` is the unchanged OpenFE engine each unit runs.

UNIT = one EDGE at one MICROSTATE LEG on one RECEPTOR FRAME. A unit runs BOTH alchemical legs
(complex-morph + solvent-morph) and reduces them to ddG_bind = dG_complex - dG_solvent (rbfe_edges.ddg_bind),
so one Vast instance produces one ddG. **~13.7 reference-4090 GPU-h per unit** — see the cost block below,
which DERIVES that rather than typing it. (A retracted 5-6 GPU-h figure, taken from a public TYK2 edge rather
than the ~2.6x heavier cmpd19/NR4A3 complex, is recorded in `step1-fanout-lane.md` section 5.)

--------------------------------------------------------------------------------------------------------
SCOPE OF WHAT IS LAUNCHED (read this before quoting a number off this map)
--------------------------------------------------------------------------------------------------------
The frozen map describes THREE multiplicative axes. Only the first is in the priced `step1_fanout`
tranche; the other two are separately-priced follow-on tranches, and this module makes that explicit rather
than silently fanning out 100+ legs:

  AXIS 1 - EDGES x charge-CONSERVING microstate leg -> 19 units.   [TRANCHE 1 - what `default_units()` emits]
      Every one of the map's 19 edges has exactly one dq=0 microstate leg. 19 units x ~13.7 ref GPU-h.

  AXIS 2 - charge-CHANGING microstate legs -> +8 units.            [TRANCHE 2 - BLOCKED, not merely deferred]
      The map's `microstate_policy` requires these, and flags them "for the co-alchemical / analytical charge
      correction". That correction is NOT implemented in `nr4a3_rbfe.py` (no co-alchemical counter-ion, no
      analytical finite-size/Ewald term). Running them without it would produce numbers with an uncontrolled
      offset, so they are EXCLUDED here and `charge_changing_units()` exists to enumerate, not to launch.

  AXIS 4 - INDEPENDENT REPLICATES of named edges -> +N per edge.  [TRANCHE 1R - opt-in, edge-scoped]
      `replicate_units()` / `lane_units()`, requested by `FANOUT_REPLICATE_EDGES` + `FANOUT_REPLICATES`.
      OFF by default and deliberately NOT map-wide: CLAUDE.md §5 defaults "more replicates" to NO, and the
      one place it says YES is a standard-rigor result that is genuinely ambiguous AND decision-relevant —
      which is `cycle_3carbonyl`, the cycle that does not close (see `replicate_units`). At n=0 nothing in
      this axis exists and every unit id is byte-identical to the pre-axis lane.

  AXIS 3 - receptor frames -> x6 (4 NR4A3 conformers + matched NR4A1 + NR4A2 open frames).
      [TRANCHE 3 - the conformer-sensitivity + paralogue-selectivity axis, ~6x the tranche-1 cost]
      TRANCHE 1 runs the PRIMARY frame only (the frame the pilot converged on), so its output is a
      single-conformer CONDITIONAL relative-FE map, NOT a selectivity readout and NOT a sensitivity range.
      `frame_units()` builds the axis-3 units when that tranche is authorized.

HONESTY (carried from the map, do not weaken). cmpd19 has NO solved NR4A3 cocrystal — only functional target
engagement (SMRT/NCoR1 blockade). The binding pose, and with it the "5-position is the linker exit vector"
assignment, are HYPOTHESES. Every ddG this fan-out produces is therefore a CONDITIONAL relative free energy
given a hypothesized pose in a modeled opened conformer — never an affinity, never a selectivity claim, and
(tranche 1) never a sensitivity range. Accuracy is not established here: it rests on valA_mini + OpenFE's
published benchmark for this exact protocol.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:                       # so `import vast_cost_model` works however this is imported
    sys.path.insert(0, HERE)
MAP_JSON = os.path.join(HERE, "congeneric-rbfe-map.json")
SERIES_JSON = os.path.join(HERE, "congeneric-warhead-series.json")

# The receptor frame TRANCHE 1 runs: the single nr4a3_design druggable release frame the pilot converged on.
# (The map's `receptor_frames_spec.pilot.nr4a3` role; the concrete PDB is the one staged under DOCK_PREFIX.)
PRIMARY_FRAME = "nr4a3_design:top_druggable_frame_1"
PRIMARY_RECEPTOR = "nr4a3"

# A microstate species is CHARGED (and so its leg is charge-changing) if its name carries one of these markers.
# The map names species like "neutral", "neutral_acid", "anionic_carboxylate", "cationic_ammonium".
_CHARGED_MARKERS = ("anionic", "cationic")

# ---- cost basis: DERIVED, never typed here ----------------------------------------------------------------
# Both numbers below used to be hand-carried constants in this file and BOTH were wrong, in the same
# direction, at the same time (the ~4x under-estimate reconstructed in
# `research/modalities/step1-fanout-lane.md` section 5). So neither is typed any more:
#
#   * the per-unit reference-GPU-hour figure comes from `vast_cost_model.LADDER_REFERENCE_GPU_H`, which is
#     the single home of every ladder stage's work estimate (nr4a3-program-map.md's rung table renders from it);
#   * the $/reference-GPU-hour comes from the market snapshot `vast-ladder-repricing.json`, regenerated by
#     `vast_cost_model.py` — a MARKET price is never a source constant, it is a measurement with a date on it.
#
# `vast_cost_model` is stdlib-only, so importing it does not break this module's purity contract. The JSON is
# read best-effort: if it is absent (a checkout without the artifact) we fall back to the pinned planning
# number rather than silently printing a band derived from nothing.
import vast_cost_model as _vcm  # noqa: E402  (stdlib-only; see purity note above)

_FANOUT_LADDER_KEY = "step1_fanout (19 RBFE edges @ ~13.7 GPU-h)"
N_TRANCHE1_UNITS = 19


def _ref_gpu_h_per_unit():
    lo, hi = _vcm.LADDER_REFERENCE_GPU_H[_FANOUT_LADDER_KEY]
    return (lo / N_TRANCHE1_UNITS, hi / N_TRANCHE1_UNITS)


def _usd_per_ref_gpu_h():
    """(low, plan, high) $/reference-GPU-hour from the last market snapshot; pinned fallback if absent."""
    try:
        with open(os.path.join(HERE, "vast-ladder-repricing.json")) as fh:
            d = json.load(fh)
        lo, hi = d["range_usd_per_reference_gpu_h"]
        return (float(lo), float(d["plan_usd_per_reference_gpu_h"]), float(hi))
    except Exception:  # noqa: BLE001 — artifact absent/unparseable: fall back, never invent
        return (0.057, 0.1372, 0.3094)


# ~13.7 reference (RTX 4090) GPU-hours per unit, both alchemical legs plus boot/setup. MEASURED on the real
# cmpd19/NR4A3 system (three independent hosts at 12.76 / 13.70 / 14.42 s/iter), NOT on the public TYK2 edge
# whose 5.2 s/iter produced the retracted 5-6 GPU-h figure.
UNIT_GPU_H = _ref_gpu_h_per_unit()
# Planning band, best-offer to median, from the live board. NOT "what we paid last time" — the $0.35-0.39/hr
# this lane realized in wave 1 was a consequence of the retired x1.9 bid policy, not the market.
VAST_4090_USD_PER_H = (_usd_per_ref_gpu_h()[0], _usd_per_ref_gpu_h()[2])


# ---- frozen-input loaders ---------------------------------------------------------------------------------

def load_map(path=MAP_JSON):
    with open(path) as f:
        return json.load(f)


def load_series(path=SERIES_JSON):
    with open(path) as f:
        return json.load(f)


def smiles_registry(map_path=MAP_JSON, series_path=SERIES_JSON):
    """{node_id: SMILES} for every node in the RBFE map, cross-checked against the series file.

    Fails closed on a mismatch: the two frozen JSONs are independently maintained, and a silent SMILES drift
    between them would mean the engine parameterizes a DIFFERENT molecule than the one the map describes —
    which would invalidate every ddG downstream."""
    m = load_map(map_path)
    s = load_series(series_path)
    series = {}
    anchor = s.get("anchor") or {}
    if anchor.get("id"):
        series[anchor["id"]] = anchor.get("smiles")
    for c in s.get("compounds", []):
        series[c["id"]] = c.get("smiles")

    out, drift = {}, []
    for n in m.get("nodes", []):
        if not n.get("in_rbfe_map"):
            continue                      # comparator scaffolds get ABFE, not RBFE edges (map decision)
        nid, smi = n["id"], n.get("smiles")
        if not smi:
            raise ValueError(f"node {nid} has no SMILES in the RBFE map")
        if nid in series and series[nid] != smi:
            drift.append((nid, smi, series[nid]))
        out[nid] = smi
    if drift:
        raise ValueError("SMILES drift between congeneric-rbfe-map.json and congeneric-warhead-series.json: "
                         + "; ".join(f"{n}: map={a!r} series={b!r}" for n, a, b in drift))
    return out


def dominant_microstate(node_id, series_path=SERIES_JSON):
    """The series file's predicted dominant pH-7.4 species string for a node (free text, for the record).
    Returned verbatim so a reader can see WHEN tranche 1's neutral leg is not the dominant species."""
    s = load_series(series_path)
    for c in s.get("compounds", []):
        if c["id"] == node_id:
            return c.get("predicted_dominant_microstate_pH7.4")
    a = s.get("anchor") or {}
    return "neutral" if a.get("id") == node_id else None


# ---- unit enumeration -------------------------------------------------------------------------------------

def is_charge_changing(leg):
    """True if this microstate leg changes net charge. Trusts the map's explicit flags first, then falls back
    to the species names, then to net_charge_change — belt and braces, because a leg wrongly classed as
    charge-conserving would be launched WITHOUT the (unimplemented) charge correction."""
    if leg.get("charge_change"):
        return True
    if leg.get("net_charge_change"):
        return True
    for k in ("state_a", "state_b"):
        name = (leg.get(k) or "").lower()
        if any(mark in name for mark in _CHARGED_MARKERS):
            return True
    return False


def unit_id(edge_id, leg_id, receptor=PRIMARY_RECEPTOR, frame=PRIMARY_FRAME, replicate=0):
    """Stable, filesystem/S3/Vast-label-safe id for one fan-out unit. The frame is included ONLY when it is not
    the primary frame, so tranche-1 unit ids (and therefore their S3 result keys) stay stable if tranche 3 is
    later added alongside them.

    ★★ THE REPLICATE INDEX IS OMITTED AT n=0, FOR EXACTLY THE SAME REASON THE PRIMARY FRAME IS
    (2026-07-31, adding the replicate axis). Everything downstream of this string is CONTENT-ADDRESSED by it —
    `result_key` (which is how `congeneric_fanout_vast._pending` decides a unit is finished),
    `checkpoint_prefix` (the spot commit store), the Vast label, the phase marker, the attempts archive. So
    renaming an existing unit does not "relabel" anything: it makes the lane unable to SEE the ddG it already
    bought, and the very next unattended tick re-rents that edge. 18 of the map's 19 edges have a landed
    `ddg.json` under the ids this function produced before the replicate axis existed, so `replicate=0` MUST
    render byte-identically to those — pinned by
    `tests/test_congeneric_fanout.py::test_every_existing_unit_id_is_byte_identical_after_the_replicate_axis`.

    A replicate is a DIFFERENT UNIT, not a re-run of one: it gets its own result key (so it is genuinely
    pending while n=0 stays done), its own checkpoint prefix (so it can never resume into another
    replicate's trajectory), and its own SEED in `unit_env`.

    The suffix goes LAST, after any frame qualifier, so a tranche-3 replicate reads
    `<edge>__<leg>__nr4a1_matched_open_frame__r2` — frame first, then repeat, which is the order the axes
    were added and the order `plan()` reports them in.
    """
    base = f"{edge_id}__{leg_id}"
    if not (receptor == PRIMARY_RECEPTOR and frame == PRIMARY_FRAME):
        tag = frame.split(":")[-1]
        base = f"{base}__{receptor}_{tag}"
    r = int(replicate or 0)
    if r < 0:
        raise ValueError(f"replicate must be >= 0, got {replicate!r}")
    return base if r == 0 else f"{base}__r{r}"


def _unit(edge, leg, receptor, frame, smiles, replicate=0):
    a, b = edge["node_a"], edge["node_b"]
    return {
        "unit_id": unit_id(edge["edge_id"], leg["leg_id"], receptor, frame, replicate),
        "replicate": int(replicate or 0),
        "edge_id": edge["edge_id"],
        "leg_id": leg["leg_id"],
        "ligand_a": a,
        "ligand_b": b,
        "smiles_a": smiles[a],
        "smiles_b": smiles[b],
        "state_a": leg.get("state_a"),
        "state_b": leg.get("state_b"),
        "receptor": receptor,
        "frame": frame,
        "edge_class": edge.get("class"),
        "star": edge.get("star"),
        "perturbation": edge.get("perturbation"),
        "common_mode_risk": edge.get("common_mode_risk"),
        "needs_pose_revalidation": bool(edge.get("needs_pose_revalidation")),
        "is_pilot": bool(edge.get("is_pilot")),
        "is_cycle_closure": bool(edge.get("is_cycle_closure")),
        "cycle_id": edge.get("cycle_id"),
        "charge_changing": is_charge_changing(leg),
        "dominant_microstate_b": dominant_microstate(b),
    }


def default_units(map_path=MAP_JSON, series_path=SERIES_JSON):
    """TRANCHE 1: every map edge at its charge-CONSERVING microstate leg, on the primary NR4A3 frame.

    Fails closed if any edge has no dq=0 leg (that would silently drop an edge from the map)."""
    m = load_map(map_path)
    smiles = smiles_registry(map_path, series_path)
    units, missing = [], []
    for e in m.get("edges", []):
        neutral = [lg for lg in (e.get("microstate_legs") or []) if not is_charge_changing(lg)]
        if not neutral:
            missing.append(e["edge_id"])
            continue
        if len(neutral) > 1:
            raise ValueError(f"edge {e['edge_id']} has {len(neutral)} charge-conserving microstate legs; "
                             "tranche 1 assumes exactly one — resolve in the map before fanning out")
        units.append(_unit(e, neutral[0], PRIMARY_RECEPTOR, PRIMARY_FRAME, smiles))
    if missing:
        raise ValueError("edges with NO charge-conserving microstate leg (would be dropped from the fan-out): "
                         + ", ".join(missing))
    return units


def charge_changing_units(map_path=MAP_JSON, series_path=SERIES_JSON):
    """TRANCHE 2 (enumerate-only, BLOCKED): the charge-changing microstate legs. Kept enumerable so the paper
    can state exactly which species were NOT computed and why, but never launched by `default_units()` —
    nr4a3_rbfe.py has no co-alchemical counter-ion or analytical finite-size correction, so these legs would
    carry an uncontrolled offset."""
    m = load_map(map_path)
    smiles = smiles_registry(map_path, series_path)
    return [_unit(e, lg, PRIMARY_RECEPTOR, PRIMARY_FRAME, smiles)
            for e in m.get("edges", [])
            for lg in (e.get("microstate_legs") or []) if is_charge_changing(lg)]


def frame_units(receptor, frame, map_path=MAP_JSON, series_path=SERIES_JSON):
    """TRANCHE 3 (not launched by default): tranche 1's edge set on ANOTHER receptor frame — the
    conformer-sensitivity (NR4A3 conformers) and paralogue (NR4A1/NR4A2 matched open frames) axis. Each extra
    frame costs another full tranche-1 spend, which is why it is a separate authorization."""
    return [dict(u, receptor=receptor, frame=frame,
                 unit_id=unit_id(u["edge_id"], u["leg_id"], receptor, frame, u.get("replicate", 0)))
            for u in default_units(map_path, series_path)]


# ---- TRANCHE 1R: independent replicates of named tranche-1 edges -------------------------------------------
#
# ★★ WHY THIS AXIS EXISTS, AND WHY IT IS EDGE-SCOPED RATHER THAN MAP-WIDE (STRATEGY rank 7).
# Two live caveats, one experiment:
#   1. `cycle_3carbonyl` does not close (the map's own `abort_criteria.cycle_closure_kcal_max` is the ±1.0
#      tolerance it fails). At n=1 per edge, "one of these three edges is wrong" and "three unlucky single
#      draws" are the same observation — `cycle_closure` cannot separate them and neither can a reader.
#   2. This lane owns NO measured replicate SD. The program has exactly one, from the ternary lane, and it is
#      transferred everywhere else — including onto binary RBFE edges it was never measured on.
# Repeating the three edges of the open cycle answers both, and CLAUDE.md §5's breadth-vs-depth rule permits
# it precisely because the standard-rigor result is AMBIGUOUS and the ambiguity is decision-relevant: it
# decides whether those three ddG values may be quoted at all. It does NOT license replicating the map.
#
# ⚠ A REPLICATE IS NOT A RE-RUN. Re-running an edge at the same unit_id would (a) find the existing ddg.json
# and skip, or (b) if forced, resume that edge's own committed trajectory and extend it — which is one
# longer sample, not a second independent one, and would license no SD at all. That is why the index is in
# the id, the seed is in the env, and the seed is in the resume fingerprint.

def replicate_units(edge_ids, replicates=(1,), map_path=MAP_JSON, series_path=SERIES_JSON):
    """Independent repeats of NAMED tranche-1 edges, at replicate indices > 0. PURE.

    `edge_ids` may name edges directly or name a CYCLE (`cycle_3carbonyl`), which expands to that cycle's
    edge list from the frozen map — the only thing anybody actually wants to replicate here is a cycle, and
    re-typing its three edge ids is a transcription error waiting to happen (rule 1: point at the map).
    Fails closed on a name that resolves to nothing, and on replicate 0 (which is not a replicate, it is the
    original unit, and silently returning it would make a "replicate request" a no-op that reads as success).
    """
    reps = sorted({int(r) for r in replicates})
    if not reps:
        raise ValueError("no replicate indices requested")
    if any(r < 1 for r in reps):
        raise ValueError(f"replicate indices must be >= 1 (0 IS the original unit, not a repeat): {reps}")
    wanted = resolve_edge_ids(edge_ids, map_path)
    base = {u["edge_id"]: u for u in default_units(map_path, series_path)}
    m = load_map(map_path)
    edges = {e["edge_id"]: e for e in m.get("edges", [])}
    smiles = smiles_registry(map_path, series_path)
    out = []
    for eid in wanted:
        u0 = base.get(eid)
        if u0 is None:      # an edge with no charge-conserving leg cannot even be in tranche 1
            raise ValueError(f"edge {eid} is not a tranche-1 unit; it cannot be replicated")
        leg = [lg for lg in (edges[eid].get("microstate_legs") or []) if lg["leg_id"] == u0["leg_id"]][0]
        for r in reps:
            out.append(_unit(edges[eid], leg, PRIMARY_RECEPTOR, PRIMARY_FRAME, smiles, replicate=r))
    return out


def resolve_edge_ids(names, map_path=MAP_JSON):
    """[edge_id] for a list of edge ids and/or cycle ids, in map order, de-duplicated. PURE, fails closed.

    Exact edge id wins outright; then an exact cycle id expands to its `edge_ids`. Nothing else — a
    substring fallback would let `cycle_3` or `amide` silently select a set nobody named, and this list is
    the thing that decides what gets rented."""
    m = load_map(map_path)
    edge_order = [e["edge_id"] for e in m.get("edges", [])]
    edges, cycles = set(edge_order), {c.get("cycle_id"): (c.get("edge_ids") or []) for c in m.get("cycles", [])}
    got, unknown = [], []
    for n in names:
        n = str(n).strip()
        if not n:
            continue
        if n in edges:
            got.append(n)
        elif n in cycles:
            got.extend(cycles[n])
        else:
            unknown.append(n)
    if unknown:
        raise ValueError(f"not an edge id or a cycle id in the frozen map: {unknown} "
                         f"(cycles: {sorted(k for k in cycles if k)})")
    seen, out = set(), []
    for e in edge_order:
        if e in got and e not in seen:
            seen.add(e)
            out.append(e)
    return out


def requested_replicates(env=None):
    """(edge_ids, replicate_indices) this lane has been asked to repeat, from the environment. PURE-ish.

    `FANOUT_REPLICATE_EDGES` — comma-separated edge ids and/or cycle ids. Empty (the default) means NO
    replicate axis at all, and `lane_units()` is then `default_units()` object-for-object.
    `FANOUT_REPLICATES=N` — how many FURTHER independent repeats per named edge, i.e. indices 1..N. It is a
    COUNT OF EXTRA draws, not a total: the map already holds n=0, so `FANOUT_REPLICATES=2` takes those edges
    to three independent samples, which is the ABFE standard CLAUDE.md §5 names ("~3 independent
    replicates + honest replicate-SD error bars")."""
    env = os.environ if env is None else env
    names = [t.strip() for t in (env.get("FANOUT_REPLICATE_EDGES") or "").split(",") if t.strip()]
    if not names:
        return [], []
    n = int((env.get("FANOUT_REPLICATES") or "1").strip() or "1")
    if n < 1:
        raise ValueError(f"FANOUT_REPLICATES must be >= 1 when FANOUT_REPLICATE_EDGES is set, got {n}")
    return names, list(range(1, n + 1))


def lane_units(map_path=MAP_JSON, series_path=SERIES_JSON, env=None):
    """EVERY unit this lane may place right now: tranche 1, plus any requested replicates. PURE-ish.

    ★ ONE ENUMERATION, SO DONE-DETECTION AND PLACEMENT CANNOT DISAGREE. `congeneric_fanout_vast` decides
    "finished" by `result_key` existing and "pending" by its absence, over whatever list it is handed — so a
    replicate that is not in that list is not pending, it is INVISIBLE, and `FANOUT_ONLY` cannot rescue it
    (it filters the pending set and hard-fails on an empty match). With no replicate requested this returns
    exactly `default_units()`, so every existing caller is unchanged."""
    units = default_units(map_path, series_path)
    names, reps = requested_replicates(env)
    if not names:
        return units
    return units + replicate_units(names, reps, map_path, series_path)


def fleet_frames(map_path=MAP_JSON):
    """The map's declared tranche-3 frame axis, as [(receptor, frame_role)]."""
    spec = (load_map(map_path).get("receptor_frames_spec") or {}).get("fleet") or {}
    return [(r, f) for r, frames in spec.items() for f in frames]


# ---- engine wiring ----------------------------------------------------------------------------------------

def unit_env(unit, leg_kind, n_windows=12):
    """The env `nr4a3_rbfe.py` reads for ONE alchemical leg of a unit.

    leg_kind: "complex" (protein+ligand+solvent, per receptor) | "solvent" (ligand-in-water, the shared
    common-mode reference) | "reduce" (CPU combine -> ddG_bind). Mirrors rbfe_edges.rbfe_legs()'s leg kinds.
    RECEPTOR is deliberately the real receptor even on the solvent leg, so the two legs of a unit land in the
    same result namespace (the engine's own solvent leg does not use the protein)."""
    if leg_kind not in ("complex", "solvent", "reduce"):
        raise ValueError(f"leg_kind must be complex|solvent|reduce, got {leg_kind!r}")
    env = {
        "MODE": "reduce" if leg_kind == "reduce" else "splittest",
        "RBFE_TINY": "0",
        "LEG": leg_kind,
        "RECEPTOR": unit["receptor"],
        "LIGAND_A": unit["ligand_a"],
        "LIGAND_B": unit["ligand_b"],
        "N_WINDOWS": str(n_windows),
        "OPENMM_REQUIRE_CUDA": "0" if leg_kind == "reduce" else "1",
    }
    # ★★ SEED IS EMITTED ONLY FOR A REPLICATE, AND THE ABSENCE AT n=0 IS THE LOAD-BEARING PART.
    #
    # `rbfe_spot_checkpoint.SYSTEM_FINGERPRINT_ENV` LISTS "SEED" and hashes it as `str(env.get(k, ""))`, so
    # an UNSET SEED and an empty one hash identically — and that hash is what decides whether a committed
    # generation may be restored. Every generation this lane has ever committed was written with SEED unset,
    # i.e. against the `""` hash. Emitting `SEED=0` here would give each of them a fingerprint MISMATCH and
    # every in-flight leg would refuse to resume after a preemption, throwing away paid GPU hours for a
    # cosmetic default — the exact self-inflicted failure `SYSTEM_FINGERPRINT_ENV_ADDITIVE` was written to
    # avoid. So n=0 emits nothing and hashes as it always did; n>=1 emits its index and hashes differently,
    # which is precisely the refusal we want.
    #
    # SEED == the replicate index (not a derived or random value), matching the ternary lane's SEED=0/1/2.
    # One number, one meaning: the id says `__r2`, the env says `SEED=2`, the fingerprint says `SEED: '2'`.
    rep = int(unit.get("replicate") or 0)
    if rep:
        env["SEED"] = str(rep)
        # A replicate's commit prefix is BRAND NEW, so nothing unstamped can legitimately be sitting in it —
        # which makes the one case `fingerprint_mismatch_reason` deliberately tolerates (a manifest written
        # before provenance stamping) impossible here, and refusing it therefore costs nothing and closes
        # the last path by which a replicate could restore a generation it cannot prove is its own.
        env["RBFE_STRICT_PROVENANCE"] = "1"
    return env


def result_key(unit, prefix):
    """S3 key of a unit's finished ddG JSON (the idempotent-skip / collect target)."""
    return f"{prefix.strip('/')}/{unit['unit_id']}/ddg.json"


def checkpoint_prefix(unit, prefix):
    """S3 prefix holding a unit's per-window checkpoints (spot resume; survives preemption)."""
    return f"{prefix.strip('/')}/{unit['unit_id']}/ckpt"


# ---- planning / bookkeeping -------------------------------------------------------------------------------

def cost_estimate(n_units, gpu_h=UNIT_GPU_H, usd_per_h=VAST_4090_USD_PER_H):
    """(low, high) USD for n units on Vast 4090, from the MEASURED per-leg rate. A band, never a point
    estimate — the underlying measurement is a per-iteration rate x hardcoded phase counts, and the realized
    $/hr is a marketplace bid that moves."""
    return (round(n_units * gpu_h[0] * usd_per_h[0], 2),
            round(n_units * gpu_h[1] * usd_per_h[1], 2))


def cost_plan(n_units, gpu_h=None):
    """The single PLANNING number for n units — the best-10-mean $/reference-GPU-hour, not the band edges.

    The band `cost_estimate` returns spans best-offer to median (a 5.4x spread), which is honest about the
    market but useless for answering "did this cost what we said". This is the number nr4a3-program-map.md's ~$36
    quotes, and it is derived from the same snapshot, so the two cannot drift."""
    gpu_h = gpu_h if gpu_h is not None else UNIT_GPU_H
    return round(n_units * (gpu_h[0] + gpu_h[1]) / 2 * _usd_per_ref_gpu_h()[1], 2)


def reference_ns_per_unit(gpu_h=None):
    """Delivered nanoseconds of MD per unit, on the reference card. PURE.

    The bridge between the ladder (which is denominated in reference GPU-HOURS) and the market guard (which
    must reason in $/ns, because that is the only figure that compares a cheap slow card against an expensive
    fast one). Both terms are derived: the GPU-hours from `vast_cost_model.LADDER_REFERENCE_GPU_H`, the ns/h
    from the validated card table. Nothing here is typed."""
    gpu_h = gpu_h if gpu_h is not None else UNIT_GPU_H
    return (gpu_h[0] + gpu_h[1]) / 2.0 * _vcm.REFERENCE_NS_PER_H


def basis_usd_per_ns():
    """The rung's OWN $/ns basis — what the ladder figure everybody quotes was actually bought at. PURE.

    ★ WHY THE LADDER BASIS AND NOT A NIGHT'S OBSERVATIONS (LANE 21, 2026-07-27). Three reasons, and the
    second is the one that matters:
      1. The **authorisation** ($15-80 for this tranche) was granted against the ladder. A guard whose job is
         "do not spend past what was authorised" has to measure against the thing that was authorised.
      2. Anchoring to recent observations is **self-ratcheting**: a bad night raises the ceiling, so the guard
         comes to permit exactly the market it exists to refuse. Tonight's $0.333/hr median floor would
         quietly become tomorrow's normal, and the rule would decay into a rubber stamp within a week.
      3. It is not stale-by-construction anyway — `plan_usd_per_reference_gpu_h` is regenerated from a real
         snapshot by `vast_cost_model.py`, so the basis does move with the market. It moves when a human runs
         the repricing, which is the point: the market may not raise its own ceiling automatically.
    """
    return _usd_per_ref_gpu_h()[1] / _vcm.REFERENCE_NS_PER_H


def projected_tranche_usd(usd_per_ns, n_units):
    """What `n_units` would cost at an achievable $/ns. PURE. The guard's headline number.

    Deliberately expressed in DOLLARS rather than as a $/ns ratio: the authorisation is a dollar band, and
    "$87 against an $80 ceiling" is a sentence somebody can act on at 3 AM. A ratio is not."""
    if usd_per_ns is None:
        return None
    return round(float(usd_per_ns) * reference_ns_per_unit() * int(n_units), 2)


def market_ceiling_usd(n_units):
    """The most `n_units` may cost before a launch is refused. PURE, and DERIVED — never typed.

    It is the TOP OF THE RUNG'S OWN BAND, `cost_estimate(n)[1]`, i.e. the same number nr4a3-program-map.md publishes
    as the high edge of $15-80. Choosing the band top rather than a hand-picked multiple means the guard
    enforces exactly the authorisation and nothing of its own invention, and it re-derives itself whenever
    the ladder is repriced.

    It also lands where the instruction did, which is a check rather than a coincidence: the band top is
    ~2.26x the plan figure, and trimcrae's phrasing was "pay double per ns"."""
    return cost_estimate(n_units)[1]


def market_verdict(best_usd_per_ns, n_units):
    """(ok, projected_usd, ceiling_usd, ratio_vs_basis) for a fleet of `n_units`. PURE.

    `best_usd_per_ns=None` means the board offered nothing we can price — no benched card, or no offer at
    all. That is a HOLD, not a launch: an unpriceable market is the one case where guessing is worst."""
    ceiling = market_ceiling_usd(n_units)
    if best_usd_per_ns is None:
        return False, None, ceiling, None
    projected = projected_tranche_usd(best_usd_per_ns, n_units)
    basis = basis_usd_per_ns()
    ratio = round(float(best_usd_per_ns) / basis, 3) if basis > 0 else None
    return (projected <= ceiling), projected, ceiling, ratio


def _unit_dollar_ceiling_usd_per_ns():
    """The most ONE unit may cost per nanosecond and still sit inside this rung's authorisation. PURE.

    ★ DERIVED FROM THE EXISTING CEILING, NOT A NEW CONSTANT (rule 1). Both sides of `market_verdict` are
    LINEAR in the unit count — `market_ceiling_usd(n) = n · gpu_h_hi · usd_per_h_hi` and
    `projected_tranche_usd(u, n) = u · reference_ns_per_unit · n` — so the whole `n` cancels and the
    tranche test was only ever a per-unit test wearing a tranche's clothes:

        projected(u, n) <= ceiling(n)   <=>   u <= ceiling(1) / reference_ns_per_unit

    That identity is what makes per-unit placement legitimate rather than a loosening: a unit admitted here
    is admitted on exactly the authorisation the tranche test enforced, just evaluated against the offer it
    will actually occupy instead of against a mean it will not.

    ⚠ IT IS NOT THE §1 DRIFT LINE, and the two must not be confused. CLAUDE.md §1's 1.5x is a REPORTING
    threshold — "a row must SAY it is drifting rather than leaving the reader to divide", explicitly "not a
    hard gate — the fleet-launch gate in the launcher is that". This is that hard gate, and it currently
    sits near 2.25x basis because the rung's own band top does (the band top is ~2.26x the plan figure,
    which is where trimcrae's "pay double per ns" landed). Rows between the two still print `⚠ DRIFT`;
    they are inside the authorisation and flagged, which is what §1 asks for.
    """
    return market_ceiling_usd(1) / reference_ns_per_unit()


# ★★ THE DRIFT LINE IS THE BUY LINE (trimcrae, 2026-07-27, ruling directly on this ceiling).
#
# He was shown the derived-ceiling algebra below and chose to bind the RATE line on top of it anyway, for the
# reason he had already given that morning about flagged-but-still-purchased rows: *"What's the point of
# tracking that if we don't act on it?"* So a row that prints ⚠ DRIFT is now a row we do not buy — the flag
# and the refusal are the same number, and the gap between "we noticed" and "we declined" is closed.
#
# SUPERSEDED (rule 1, registered rather than deleted): until this ruling, 1.5x was a REPORTING threshold only.
# `inflight_usd_per_ns.py` said so in as many words — "Not a hard gate — the fleet-launch gate in the
# launcher is that" (CLAUDE.md §1 now carries the ruling that replaced it) —
# and the fan-out's hard gate was the derived band top alone, ~2.25x basis. Both framings are quotable from
# the history, so the live rule is stated once, here: **a unit must clear BOTH lines.**
# ★★ THE BUY LINE AND THE ⚠ DRIFT FLAG ARE ONE NUMBER, AND IT IS AN ABSOLUTE RATE (trimcrae, 2026-07-27).
# Imported, never re-typed — `inflight_usd_per_ns.APPROVED_USD_PER_NS` is the rate actually approved and the
# multiple is derived against the CURRENT basis. Two failures this closes:
#   1. A multiple pinned to a moving denominator silently changes the rule. The basis fell 22 % when the
#      throughput table was corrected — no price moved — and a typed 1.5x would have failed every board.
#   2. The flag and the refusal must stay the same number (*"Why are there so many high $/ns rows that are
#      flagged but you're still paying for them?"*). If the buy line moved and the flag did not, rows would
#      print ⚠ DRIFT and be bought — the original complaint, recreated by the fix. tests/
#      test_buy_line_invariant.py fails if they ever diverge.
def drift_buy_line_x_basis():
    """The buy line as a multiple of the CURRENT basis. DERIVED — see `inflight_usd_per_ns.drift_multiple`."""
    from inflight_usd_per_ns import drift_multiple
    return drift_multiple()


def unit_rate_line_usd_per_ns():
    """The §1 drift line as an ABSOLUTE rate — the form that was approved and the form that is invariant
    under a basis correction. Returned straight from the approved constant so no rounding can separate the
    rate line from the multiple the board prints."""
    from inflight_usd_per_ns import APPROVED_USD_PER_NS
    return APPROVED_USD_PER_NS


def unit_ceiling_components():
    """(dollar_ceiling, rate_line, effective, which_binds). PURE.

    Two DIFFERENT constraints, kept separate on purpose — conflating them is what made the last round of
    hold readouts unreadable. The dollar ceiling asks *"does this stay inside the money the rung was
    authorised"*; the rate line asks *"is this a rate we are willing to pay at all"*. A unit must clear BOTH,
    so the effective ceiling is the lower, and a refusal names which one it hit.
    """
    dollar = _unit_dollar_ceiling_usd_per_ns()
    rate = unit_rate_line_usd_per_ns()
    if rate <= dollar:
        return dollar, rate, rate, f"rate line (${rate:.6f}/ns = {drift_buy_line_x_basis():.2f}x basis)"
    return dollar, rate, dollar, "dollar ceiling (the rung's authorised band)"
def unit_usd_per_ns_ceiling():
    """The EFFECTIVE per-unit buy ceiling: the lower of the derived dollar ceiling and the 1.5x rate line.

    `_unit_dollar_ceiling_usd_per_ns` keeps the algebra that showed the tranche test was a per-unit test in
    disguise, and it still binds as the DOLLAR ceiling. Since trimcrae's 2026-07-27 ruling the rate line
    binds on top of it, and at the current basis the rate line is the lower of the two — so this is 1.5x
    basis today, and would revert to the derived figure if a repricing ever pushed the band top below it.
    """
    return unit_ceiling_components()[2]



def place_units(ranked_usd_per_ns, n_wanted, ceiling_usd_per_ns=None):
    """(n_placed, placed, held_reason) — how many of `n_wanted` units the board can take RIGHT NOW. PURE.

    ★★ WHY PER-UNIT AND NOT A FLEET MEAN (trimcrae, 2026-07-27: *"The fanout fleet doesn't all have to run
    at the same time. If 5 GPUs are cheap enough and the rest aren't, only run 5."*). The mean was always
    the wrong statistic for an all-or-nothing decision. On the board that prompted this, two offers sat at
    1.71x and 1.77x basis — cheaper than plenty this lane has happily rented — and were refused because
    offers 8, 9 and 10 at 4.44x, 4.63x and 6.95x dragged the mean to 3.25x. That is declining cheap capacity
    because expensive capacity exists beside it, and CLAUDE.md §6 exists to stop us PAYING a bad rate, not
    to stop us TAKING a good one.

    Splitting is scientifically free here and that is checked, not assumed: every unit has its own S3
    result key (`result_key`) and its own checkpoint prefix (`checkpoint_prefix`), both keyed on `unit_id`;
    the launcher carries no barrier or dependency between units and is already a top-up loop bounded by free
    slots; `cycle_closure` reports a cycle with a missing edge as `incomplete` rather than fabricating one;
    and the only shared object is the read-only staged pose tree, written once and unchanged between ticks —
    which is exactly what keeps the ddG values mutually comparable no matter WHEN each edge runs.

    The ladder cost is therefore unchanged by splitting: identical GPU-hours, spread over more ticks, and a
    tick costs $0. So a partial launch is strictly better than a hold — same science, sooner, at rates that
    pass — and the only thing it may never do is lose the remainder. `place_units` never drops: it returns a
    count, and the caller's pending set is recomputed from S3 every tick, so held units come back by
    construction.

    One unit per offer: two units on one host contend for its GPU, which is why the launcher widens its
    exclusion set as it goes. So the count is capped by how many offers clear, not by how cheap the best is.
    """
    ceiling = unit_usd_per_ns_ceiling() if ceiling_usd_per_ns is None else float(ceiling_usd_per_ns)
    placed = [u for u in ranked_usd_per_ns if u is not None and u <= ceiling][:max(0, int(n_wanted))]
    if placed:
        return len(placed), placed, None
    if not ranked_usd_per_ns:
        return 0, [], ("the board offered nothing this lane can price — an unpriceable market is the one "
                       "case where guessing is worst")
    best = min(u for u in ranked_usd_per_ns if u is not None) if any(
        u is not None for u in ranked_usd_per_ns) else None
    if best is None:
        return 0, [], "no offer on the board carries a benched card, so none can be priced"
    # NAME WHICH CONSTRAINT REFUSED IT. The dollar ceiling and the rate line are different questions —
    # "past the money the rung was authorised" vs "a rate we decline to pay at all" — and a reader who
    # cannot tell them apart cannot tell a repricing problem from a market problem.
    b = basis_usd_per_ns()
    _dollar, _rate, _eff, which = unit_ceiling_components()
    return 0, [], (f"the cheapest offer on the board is ${best:.6f}/ns ({best / b:.2f}x basis), above the "
                   f"${ceiling:.6f}/ns ({ceiling / b:.2f}x) a single unit may cost — refused on the "
                   f"{which}" + (f", which binds below the dollar ceiling of ${_dollar:.6f}/ns "
                                 f"({_dollar / b:.2f}x)" if abs(_eff - _rate) < 1e-12 else ""))


def wave_plan(n_units, width=8, unit_h=None):
    """Wall-clock shape of running n units `width`-wide. Vast rents independent hosts, so `width` is a
    self-imposed concurrency cap (cost/blast-radius control), not a provider quota."""
    unit_h = unit_h if unit_h is not None else UNIT_GPU_H[1]
    waves = -(-n_units // max(1, width))
    return {"n_units": n_units, "width": width, "waves": waves,
            "wall_clock_h_est": round(waves * unit_h, 1)}


def replicate_plan(map_path=MAP_JSON, series_path=SERIES_JSON, env=None):
    """The replicate axis as a dry-run block: which units a replicate request produces, and at what cost.

    Returns None when nothing was requested, so `plan()` carries the key only when it means something —
    a permanently-present `"replicates": {"n_units": 0}` is the kind of always-there zero that stops being
    read. PURE."""
    names, reps = requested_replicates(env)
    if not names:
        return None
    edge_ids = resolve_edge_ids(names, map_path)
    units = replicate_units(names, reps, map_path, series_path)
    lo, hi = cost_estimate(len(units))
    return {
        "requested": names,
        "edges": edge_ids,
        "replicate_indices": reps,
        "n_units": len(units),
        "units": [u["unit_id"] for u in units],
        "seed_per_unit": {u["unit_id"]: unit_env(u, "complex").get("SEED") for u in units},
        "cost_usd_est": [lo, hi],
        "cost_plan_usd": cost_plan(len(units)),
        "independence": "Each replicate is a DISTINCT unit: its own S3 result key (so it is pending while "
                        "the n=0 edge stays done), its own checkpoint prefix, and its own SEED — which is "
                        "part of rbfe_spot_checkpoint's resume fingerprint, so it can never restore another "
                        "replicate's trajectory.",
        "what_it_buys": "A replicate SD for these edges MEASURED ON THIS LANE, and the separation of 'one of "
                        "these edges is wrong' from 'unlucky single draws' for a cycle that does not close. "
                        "It does NOT improve accuracy and does not widen the claim ceiling.",
    }


def plan(map_path=MAP_JSON, series_path=SERIES_JSON, width=8, env=None):
    """Self-describing dry-run plan: what tranche 1 launches, what it deliberately does NOT, and the cost band."""
    units = default_units(map_path, series_path)
    cc = charge_changing_units(map_path, series_path)
    lo, hi = cost_estimate(len(units))
    reps = replicate_plan(map_path, series_path, env)
    return {
        "tranche": "1 — edges x charge-conserving microstate leg, PRIMARY NR4A3 frame only",
        "n_units": len(units),
        "units": [u["unit_id"] for u in units],
        "by_class": _count(units, "edge_class"),
        "by_star": _count(units, "star"),
        "cost_usd_est": [lo, hi],
        "cost_basis": "MEASURED ~3.6 GPU-h complex leg (Vast 4090, instance 45654998) + extrapolated solvent "
                      "leg; x the realized interruptible $/hr band. Band, not a point estimate.",
        "waves": wave_plan(len(units), width),
        "excluded_tranche_2_charge_changing": [u["unit_id"] for u in cc],
        "excluded_tranche_2_reason": "map microstate_policy requires a co-alchemical / analytical charge "
                                     "correction that nr4a3_rbfe.py does not implement",
        "excluded_tranche_3_frames": [f"{r}:{f}" for r, f in fleet_frames(map_path)
                                      if f != PRIMARY_FRAME],
        "excluded_tranche_3_reason": "conformer-sensitivity + paralogue axis; each extra frame is another full "
                                     "tranche-1 spend and a separate authorization",
        "claim_ceiling": "CONDITIONAL relative free energies on a HYPOTHESIZED cmpd19 pose in ONE modeled "
                         "opened conformer. Not affinity, not selectivity, not a sensitivity range.",
        # Present only when a replicate was actually requested (FANOUT_REPLICATE_EDGES) — see replicate_plan.
        **({"replicates": reps} if reps else
           {"replicates_note": "no replicate requested (FANOUT_REPLICATE_EDGES unset); every unit above is "
                               "n=0, single-draw, and the map's uncertainties are within-run MBAR SEs, not "
                               "replicate SDs"}),
    }


def _count(units, key):
    out = {}
    for u in units:
        out[u.get(key)] = out.get(u.get(key), 0) + 1
    return dict(sorted(out.items(), key=lambda kv: str(kv[0])))


def cycle_closure(ddg_by_edge, map_path=MAP_JSON):
    """Thermodynamic-cycle consistency check: the signed ddG round each closed loop must sum to ~0.

    This is the fan-out's INTERNAL-CONSISTENCY readout (the map's `cycles` + `abort_criteria
    .cycle_closure_kcal_max`). It is NOT an accuracy check — a map can close perfectly and still be wrong
    against experiment — but a cycle that does not close means at least one edge in it is unconverged or
    mis-mapped, and its ddG must not be quoted.

    `ddg_by_edge`: {edge_id: ddG_bind}. Edges are directed A->B as written in the map; a loop is traversed by
    following node_a -> node_b and negating any edge walked backwards. Cycles with a missing edge report
    status "incomplete" rather than a fabricated closure."""
    m = load_map(map_path)
    edges = {e["edge_id"]: e for e in m.get("edges", [])}
    out = []
    for cyc in m.get("cycles", []):
        ids = cyc.get("edge_ids") or []
        tol = float(cyc.get("tol_kcal", 1.0))
        have = [i for i in ids if i in ddg_by_edge]
        if len(have) != len(ids):
            out.append({"cycle_id": cyc.get("cycle_id"), "status": "incomplete",
                        "missing": [i for i in ids if i not in ddg_by_edge], "tol_kcal": tol})
            continue
        walked = _walk_cycle(ids, edges, ddg_by_edge)
        if walked is None:
            out.append({"cycle_id": cyc.get("cycle_id"), "status": "not_a_loop", "edge_ids": ids,
                        "tol_kcal": tol})
            continue
        walk_ids, signed = walked
        total = sum(signed)
        out.append({"cycle_id": cyc.get("cycle_id"), "status": "ok" if abs(total) <= tol else "VIOLATION",
                    "sum_kcal": round(total, 3), "tol_kcal": tol,
                    "signed_terms": {i: round(v, 3) for i, v in zip(walk_ids, signed)}})
    return out


def _walk_cycle(ids, edges, ddg_by_edge):
    """Order the loop's edges head-to-tail and return `(ordered_ids, signed_ddG)`, the contribution negated
    where an edge is traversed B->A. Returns None if the ids do not actually form a closed loop.

    The ids are returned WITH the values, and callers must zip against those rather than against the
    declaration order they passed in: the walk reorders the loop, so zipping the caller's `ids` against
    `signed` silently attaches each value to whichever edge happens to sit at that index. That defect shipped
    in `cycle_closure`'s `signed_terms` and was invisible in `sum_kcal`, which is order-independent - it
    mislabelled which edge carried which value in every cycle whose declaration order was not its walk order."""
    remaining = list(ids)
    first = remaining.pop(0)
    start, node = edges[first]["node_a"], edges[first]["node_b"]
    order, signed = [first], [ddg_by_edge[first]]
    while remaining:
        for i, eid in enumerate(remaining):
            e = edges[eid]
            if e["node_a"] == node:
                order.append(eid)
                signed.append(ddg_by_edge[eid])
                node = e["node_b"]
                break
            if e["node_b"] == node:
                order.append(eid)
                signed.append(-ddg_by_edge[eid])
                node = e["node_a"]
                break
        else:
            return None
        remaining.pop(i)
    return (order, signed) if node == start else None


def pending_given(units, done_ids, blocked_ids=()):
    """Units with no result and no block, in lane order. PURE.

    ★ ONE PLACE, SO A DRY RUN AND A BILLING TICK CANNOT DISAGREE. `congeneric_fanout_vast._pending` is this
    function plus the two S3 reads that supply its arguments — nothing else. That matters because the
    question "would a replicate request actually be placed, and would the 18 finished edges stay finished?"
    has to be answerable WITHOUT renting anything, and an answer computed by a second, similar-looking
    expression would be evidence about that expression rather than about the launcher."""
    done, blk = set(done_ids or ()), set(blocked_ids or ())
    return [u for u in units if u["unit_id"] not in done and u["unit_id"] not in blk]


def replicate_stats(results):
    """{edge_id: {n, draws, mean_kcal, sd_kcal}} over ddG results that carry a `replicate` index. PURE.

    `results` is the collected ddg.json list. Every result counts as one draw, INCLUDING the n=0 unit — the
    map's own single sample is the first replicate, not a different kind of thing, and excluding it would
    throw away a third of a three-draw set.

    `sd_kcal` is the SAMPLE standard deviation (n-1) across INDEPENDENT DRAWS and is None below n=2. It is
    reported next to, never merged with, the within-run MBAR SE each draw carries: CLAUDE.md §5 asks for
    "honest replicate-SD, not MBAR-SE" error bars, and the two answer different questions — MBAR-SE asks how
    well ONE trajectory was sampled, replicate SD asks whether a SECOND trajectory lands in the same place.
    """
    by_edge = {}
    for r in results or ():
        eid, v = r.get("edge_id"), r.get("ddg_bind_kcal")
        if eid is None or v is None:
            continue
        by_edge.setdefault(eid, {})[int(r.get("replicate") or 0)] = float(v)
    out = {}
    for eid, draws in sorted(by_edge.items()):
        vals = [draws[k] for k in sorted(draws)]
        n = len(vals)
        mean = sum(vals) / n
        sd = (sum((v - mean) ** 2 for v in vals) / (n - 1)) ** 0.5 if n > 1 else None
        out[eid] = {"n": n, "draws": {f"r{k}": round(draws[k], 3) for k in sorted(draws)},
                    "mean_kcal": round(mean, 3),
                    "sd_kcal": round(sd, 3) if sd is not None else None}
    return out


def rank_by_ddg(ddg_by_edge, anchor="zaienne_cmpd19", map_path=MAP_JSON):
    """Rank the anchor-rooted analogues by conditional relative binding free energy.

    Only edges that START at the anchor are rankable directly (their ddG is B-relative-to-anchor by
    construction); closure edges are consistency checks, not rankings. More NEGATIVE ddG = predicted tighter
    than cmpd19 in the modeled conformer. Conditional on the hypothesized pose — never an affinity."""
    m = load_map(map_path)
    rows = []
    for e in m.get("edges", []):
        if e["node_a"] != anchor or e["edge_id"] not in ddg_by_edge:
            continue
        rows.append({"node": e["node_b"], "edge_id": e["edge_id"],
                     "ddg_bind_kcal": round(ddg_by_edge[e["edge_id"]], 3),
                     "class": e.get("class"), "star": e.get("star"),
                     "perturbation": e.get("perturbation")})
    return sorted(rows, key=lambda r: r["ddg_bind_kcal"])


def fanout_width():
    """The concurrency target: DERIVED from the map, not typed (CLAUDE.md rule 1).

    ★★ THIS NUMBER HAD THREE HOMES AND ALL THREE DISAGREED (2026-07-27, during the ramp trimcrae asked
    for: *"ramp up that parallel usage"*). It was `8` here, `"19"` in `step1-fanout-autoscale.yml`, `"19"`
    again in `fusion-cpu-extras.yml`, and the truth on the ground was **18** — `cw_bio_nmethyl_amide` is
    permanently blocked because no mapper reaches the 20-atom provable floor. So the one knob that decides
    how parallel this lane runs was a hand-carried constant in three files, and the code default was less
    than half the intended width: ANY entry point that forgot to set the env var silently capped the fleet
    at 8 hosts while the workflow's readout talked about 19. That is precisely the drift rule 1 exists to
    stop, and here it was throttling the ramp.

    The derivation. Vast rents INDEPENDENT hosts — there is no shared quota wall, and CLAUDE.md §6's litmus
    test ("is there a result this shard could return that would make me NOT run the rest?") answers NO for a
    congeneric map — so there is no reason for this lane to impose a concurrency cap BELOW its own map. The
    width is therefore the size of the map, and the units that must not be rented are excluded where that
    fact actually lives: `_pending` drops finished units (a ddg.json in S3) and blocked ones (`_load_blocked`,
    also S3). Width is the ceiling; those two are the filter. A blocked unit can never consume a slot, so
    deriving from `len(default_units())` cannot over-rent — it only stops the cap from binding below what
    the lane is allowed to place.

    ⚠ THIS IS NOT "MORE PARALLEL AT ANY PRICE". Width does not buy anything: every unit still has to clear
    the per-unit $/ns gate (`market_gate` -> `congeneric_fanout.place_units`), so raising the cap can only
    let a unit through that the PRICE gate already approved. trimcrae authorised more concurrency, not a
    higher rate, and the rate line is untouched by this.

    `FANOUT_WIDTH` still overrides, for a deliberate narrowing (a shakeout, a blast-radius limit). An
    explicit env var is a choice; a stale constant is not.
    """
    env = (os.environ.get("FANOUT_WIDTH") or "").strip()
    if env:
        return int(env)
    # `lane_units()`, not `default_units()`: with a replicate requested the lane has MORE units it is
    # allowed to place, and a width derived from the map alone would cap the fleet below its own pending
    # set — the same "code default silently narrower than the readout" defect this function exists to stop.
    # With no replicate requested the two are identical, so nothing changes.
    return len(lane_units())


if __name__ == "__main__":
    print(json.dumps(plan(width=fanout_width()), indent=2))
