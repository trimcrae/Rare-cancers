#!/usr/bin/env python3
"""Congeneric binary-RBFE PILOT — pure core + abort gate + plan (Track B; RBFE-map plan §"pilot edge").

The single-edge, single-design-frame CONVERGENCE pilot the reviewer authorized (~$5-15). It is deliberately
NOT the lead-opt selectivity readout in rbfe_edges.py (denovo_401->lo_m0_NCCO, 3-receptor, 401-ABFE-anchored):
the pilot asks ONE question — "can a congeneric RBFE even converge on this dynamic, low-population cryptic
pocket without the pocket collapsing during the alchemical MD?" — so it runs the MOST well-behaved perturbation
(5-Br -> 5-NH2, both neutral, single-site) on ONE nr4a3_design frame, no selectivity, no anchor.

Role split mirrors rbfe_edges.py -> nr4a3_rbfe_sagemaker.py: THIS is the pure, unit-tested core (edge/leg
definition, the pre-registered abort gate, the plan); the heavy OpenFE RBFE engine + spot-Training submitter
reuse the existing per-window-checkpoint plumbing. The pilot edge id, the two endpoint SMILES, the single
design frame, and the ABORT criteria are all READ from congeneric-rbfe-map.json (single source of truth) so
this module cannot drift from the frozen map.

HONESTY. No affinity/ddG/GPU-hour/convergence asserted. The abort thresholds are the map's pre-registered
design parameters; the plan's unit_gpu_h is a labeled STUB to calibrate on the pilot (the map itself says
"the repo forbids trusting stub GPU-hour numbers").
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MAP_JSON = os.path.join(HERE, "congeneric-rbfe-map.json")
SERIES_JSON = os.path.join(HERE, "congeneric-warhead-series.json")


def load_map(path=MAP_JSON):
    with open(path) as f:
        return json.load(f)


def _series_smiles(path=SERIES_JSON):
    """{id: smiles} for the anchor + every congeneric compound (for the map-sanity check)."""
    with open(path) as f:
        d = json.load(f)
    out = {}
    anchor = d.get("anchor") or {}
    if anchor.get("id"):
        out[anchor["id"]] = anchor.get("smiles")
    for c in d.get("compounds", []):
        cid = c.get("id") or c.get("name")
        if cid:
            out[cid] = c.get("smiles")
    return out


def pilot_edge(map_path=MAP_JSON, series_path=SERIES_JSON):
    """The frozen pilot edge, resolved from the map + series: endpoints, SMILES, single design frame, and (if
    RDKit present) an MCS map-sanity check. Fails closed (ValueError) if the map's pilot_edge_id does not match
    an edge whose endpoints we can resolve — so a drift in the map is caught, never silently run."""
    m = load_map(map_path)
    pid = m["pilot_edge_id"]
    edge = next((e for e in m.get("edges", []) if e.get("edge_id") == pid), None)
    if edge is None:
        raise ValueError("pilot_edge_id %r not found among map edges" % pid)
    a, b = edge["node_a"], edge["node_b"]
    smi = _series_smiles(series_path)
    if smi.get(a) is None or smi.get(b) is None:
        raise ValueError("pilot endpoints missing SMILES: %r=%r %r=%r" % (a, smi.get(a), b, smi.get(b)))
    frame = m["receptor_frames_spec"]["pilot"]["nr4a3"][0]   # e.g. 'nr4a3_design:top_druggable_frame_1'
    out = {"edge_id": pid, "node_a": a, "node_b": b, "smiles_a": smi[a], "smiles_b": smi[b],
           "perturbation": edge.get("perturbation"), "single_site": edge.get("single_site"),
           "design_frame_role": frame, "receptors": ["nr4a3"],
           "note": "convergence/pocket-stability pilot on ONE nr4a3_design frame; no selectivity, no 401 anchor"}
    try:
        import rbfe_edges  # reuse the MCS sanity helper (RDKit-optional)
        out["map_sanity"] = rbfe_edges.mapping_summary(smi[a], smi[b])
    except Exception:  # noqa: BLE001 — RDKit absent in the dev sandbox
        out["map_sanity"] = {}
    return out


def pilot_legs():
    """The two RBFE morph legs of the single-frame pilot: ONE shared solvent morph (A->B in water, cancels
    common-mode) + ONE complex morph on the nr4a3_design frame. (No per-paralogue complex legs — the pilot is
    convergence, not selectivity.)"""
    return [("solvent", "shared", "solvent"), ("complex-nr4a3_design", "nr4a3", "complex")]


# =============================================================================================================
# pre-registered ABORT gate (RBFE-map abort_criteria — evaluate a pilot result dict)
# =============================================================================================================
def evaluate_abort_gate(result, map_path=MAP_JSON):
    """Evaluate the map's pre-registered abort criteria on a pilot RESULT dict. Pure — no MD. result keys:
      {per_leg_hysteresis_kcal: {leg: float}, min_mbar_overlap: float, cycle_closure_kcal: float|null,
       pocket_survival_frac: float, pocket_volume_below_apo_frac: float|null}.
    Returns {passed, criteria, failures}. A missing/non-finite required field FAILS (fail closed)."""
    ac = load_map(map_path)["abort_criteria"]
    reasons = []

    def _num(x):
        if isinstance(x, bool) or x is None:
            return None
        try:
            f = float(x)
        except (TypeError, ValueError):
            return None
        return f if math.isfinite(f) else None

    hys = result.get("per_leg_hysteresis_kcal") or {}
    worst_hys = None
    for leg, v in hys.items():
        fv = _num(v)
        if fv is None:
            reasons.append("leg %r hysteresis missing/non-finite" % leg)
            continue
        worst_hys = fv if worst_hys is None else max(worst_hys, fv)
    if worst_hys is None:
        reasons.append("no finite per-leg hysteresis supplied")
    elif worst_hys > ac["hysteresis_kcal_max"]:
        reasons.append("worst-leg hysteresis %.3f > %.2f" % (worst_hys, ac["hysteresis_kcal_max"]))

    ov = _num(result.get("min_mbar_overlap"))
    if ov is None or ov < ac["mbar_overlap_min"]:
        reasons.append("min MBAR overlap %r < %.3f" % (ov, ac["mbar_overlap_min"]))

    cc = _num(result.get("cycle_closure_kcal"))
    if cc is not None and abs(cc) > ac["cycle_closure_kcal_max"]:
        reasons.append("cycle closure |%.3f| > %.2f" % (cc, ac["cycle_closure_kcal_max"]))
    # (cycle closure is only defined once cycle-closing edges exist; a single pilot edge may omit it → not
    #  required, but if supplied it must pass.)

    ps = _num(result.get("pocket_survival_frac"))
    if ps is None or ps < ac["pocket_survival_frac_min"]:
        reasons.append("pocket survival %r < %.2f (cryptic pocket collapsing under the morph)"
                       % (ps, ac["pocket_survival_frac_min"]))
    pv = _num(result.get("pocket_volume_below_apo_frac"))
    if pv is not None and pv > 0.5:
        reasons.append("Pocket-5 volume below apo-open across %.2f>0.5 of windows (collapsing)" % pv)

    passed = not reasons
    return {"passed": passed, "failures": reasons,
            "worst_leg_hysteresis": worst_hys, "min_mbar_overlap": ov, "pocket_survival_frac": ps,
            "decision": ("calibrate n_windows/GPU-h from the pilot and schedule the fleet" if passed
                         else "HALT — do NOT fan out the fleet; the RBFE-primary premise is in doubt on this "
                              "cryptic pocket; escalate as a strategy fork (abort_criteria.decision_rule)")}


# =============================================================================================================
# DOCKING / PREP PREFLIGHT (reviewer 2026-07-12, Plan C) — input staging is NOT evidence of binding
# =============================================================================================================
# The 5-Br -> 5-NH2 change is NOT an especially gentle RBFE perturbation: it substantially changes polarity +
# H-bonding and may alter heterocycle microstate preferences. Before the edge is executable, ALL preflight
# conditions must pass; a failure aborts THIS edge -> pick a smaller same-scaffold, same-net-charge transform.
PREFLIGHT_MCS_OVERLAP_MIN = 0.70

def dock_derived_preflight_fields(smiles_a, smiles_b, construct_frozen=True,
                                  residue_numbering="NR4A3 373-626 (nr4a3_design frame)"):
    """Fill the DOCKING-informed subset of the preflight dict from the two endpoint SMILES + a design frame:
    the common-binding-mode/MCS-overlap and net-charge-change checks (via RDKit, when available). The
    remaining fields (atom_map_ok, parameterized_ok, min_ok, max_clash_ok, severe_strain, ligand tautomer/
    protonation enumeration) come from the RBFE/MD prep (Plan B, deferred) — returned in `pending_fep_prep`,
    never guessed. RDKit-optional (returns the mcs/charge fields as None + pending when RDKit is absent, e.g.
    the dev sandbox), so the docking job's poses drive the real values in CI/MD."""
    fields = {"construct_frozen": construct_frozen, "residue_numbering": residue_numbering,
              "docking_grid_identical": True,   # both endpoints docked into the SAME Pocket-5 box + params
              "mcs_overlap_frac": None, "net_charge_a": None, "net_charge_b": None, "charge_correction": False}
    try:
        from rdkit import Chem
        from rdkit.Chem import rdFMCS
        ma, mb = Chem.MolFromSmiles(smiles_a), Chem.MolFromSmiles(smiles_b)
        if ma is not None and mb is not None:
            res = rdFMCS.FindMCS([ma, mb], completeRingsOnly=True, ringMatchesRingOnly=True, timeout=30)
            n = res.numAtoms
            fields["mcs_overlap_frac"] = round(n / float(min(ma.GetNumAtoms(), mb.GetNumAtoms())), 3)
            fields["net_charge_a"] = Chem.GetFormalCharge(ma)
            fields["net_charge_b"] = Chem.GetFormalCharge(mb)
    except Exception:  # noqa: BLE001 — RDKit absent (dev sandbox) or unparseable
        pass
    return {"fields": fields,
            "pending_fep_prep": ["ligand_states_a", "ligand_states_b", "atom_map_ok", "parameterized_ok",
                                 "min_ok", "max_clash_ok", "severe_strain",
                                 "receptor_repairs_documented", "protonation_documented"],
            "note": "docking informs the common-mode/MCS + net-charge checks; the atom-map/param/minimization "
                    "checks come from the RBFE/MD prep (deferred). NOT evidence of binding.",
            "rdkit_available": fields["mcs_overlap_frac"] is not None}


def docking_preflight(prep):
    """Evaluate the reviewer's Plan-C preflight on a docking/prep RESULT dict. Pure; fail-closed on missing
    fields. `prep` keys:
      construct_frozen (bool), residue_numbering (str), receptor_repairs_documented (bool),
      protonation_documented (bool), ligand_states_a (list), ligand_states_b (list),
      docking_grid_identical (bool), mcs_overlap_frac (float), atom_map_ok (bool), parameterized_ok (bool),
      net_charge_a (int), net_charge_b (int), charge_correction (bool),
      min_ok (bool), max_clash_ok (bool), severe_strain (bool).
    Returns {passed, failures, decision}. Output is INPUT STAGING, never evidence of binding/selectivity."""
    reasons = []

    def _reqbool(k):
        v = prep.get(k, None)
        if not isinstance(v, bool):
            reasons.append("%s: required boolean missing/non-bool" % k)
            return None
        return v

    if _reqbool("construct_frozen") is not True:
        reasons.append("NR4A3 construct/residue-numbering not frozen")
    if not prep.get("residue_numbering"):
        reasons.append("residue_numbering not documented")
    if _reqbool("receptor_repairs_documented") is not True:
        reasons.append("receptor repairs not documented")
    if _reqbool("protonation_documented") is not True:
        reasons.append("receptor protonation not documented")
    for k in ("ligand_states_a", "ligand_states_b"):
        if not prep.get(k):
            reasons.append("%s: ligand tautomer/protonation states not enumerated" % k)
    if _reqbool("docking_grid_identical") is not True:
        reasons.append("docking grid/constraints not identical for both endpoints")
    mcs = prep.get("mcs_overlap_frac")
    if not isinstance(mcs, (int, float)) or isinstance(mcs, bool) or mcs < PREFLIGHT_MCS_OVERLAP_MIN:
        reasons.append("MCS overlap %r < %.2f (common binding mode not adequate)" % (mcs, PREFLIGHT_MCS_OVERLAP_MIN))
    if _reqbool("atom_map_ok") is not True:
        reasons.append("atom mapping failed")
    if _reqbool("parameterized_ok") is not True:
        reasons.append("parameterization failed")
    # net-charge: must be equal OR an explicit charge correction declared
    ca, cb = prep.get("net_charge_a"), prep.get("net_charge_b")
    if not isinstance(ca, int) or not isinstance(cb, int) or isinstance(ca, bool) or isinstance(cb, bool):
        reasons.append("net charges missing/non-int")
    elif ca != cb and prep.get("charge_correction") is not True:
        reasons.append("unresolved net-charge change (%s -> %s) with no charge_correction" % (ca, cb))
    if _reqbool("min_ok") is not True:
        reasons.append("restrained minimization failed")
    if _reqbool("max_clash_ok") is not True:
        reasons.append("persistent clashes after minimization")
    if prep.get("severe_strain") is True:
        reasons.append("severe ligand strain after minimization")

    passed = not reasons
    return {"passed": passed, "failures": reasons,
            "perturbation_note": "5-Br->5-NH2 is NOT a gentle RBFE edge (polarity/H-bond/microstate change); "
                                 "preflight is mandatory",
            "output_status": "INPUT STAGING ONLY — not evidence of binding or selectivity",
            "decision": ("edge executable — proceed to the RBFE morph" if passed
                         else "ABORT this edge; select a smaller same-scaffold, same-net-charge transformation")}


# =============================================================================================================
# MODE=plan — pilot forecast (2 legs; cheap by design)
# =============================================================================================================
def plan(n_windows=12, unit_gpu_h=2.0, spot_hourly=0.50):
    """Dry-run forecast for the single-frame pilot (NO GPU/spend). 2 legs (solvent + complex) × n_windows.
    unit_gpu_h is a labeled STUB (the map forbids trusting it) — calibrate on the pilot itself."""
    edge = pilot_edge()
    legs = pilot_legs()
    n_legs = len(legs)
    gpu_h = n_legs * n_windows * unit_gpu_h
    cost = gpu_h * spot_hourly
    return {
        "edge": "%s -> %s (%s)" % (edge["node_a"], edge["node_b"], edge["perturbation"]),
        "design_frame_role": edge["design_frame_role"],
        "legs": [l[0] for l in legs], "n_legs": n_legs, "n_windows_per_leg": n_windows,
        "unit_gpu_h_STUB": unit_gpu_h,
        "forecast_gpu_h": round(gpu_h, 1), "spot_hourly_usd": spot_hourly,
        "forecast_cost_usd": round(cost, 2),
        "wall_h_if_leg_serial": round(n_windows * unit_gpu_h, 1),
        "honesty": "unit_gpu_h is a PLANNING STUB (the RBFE map forbids trusting stub GPU-hour numbers); "
                   "calibrate on the pilot. No affinity/ddG asserted. Pilot = convergence test, not selectivity.",
        "map_sanity": edge.get("map_sanity", {}),
    }


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Congeneric binary-RBFE pilot: edge + abort gate + MODE=plan.")
    ap.add_argument("--windows", type=int, default=12)
    ap.add_argument("--unit-gpu-h", type=float, default=2.0)
    ap.add_argument("--spot-hourly", type=float, default=0.50)
    ap.add_argument("--edge", action="store_true", help="print the resolved pilot edge and exit")
    args = ap.parse_args(argv)
    if args.edge:
        print(json.dumps(pilot_edge(), indent=2))
        return 0
    print(json.dumps(plan(n_windows=args.windows, unit_gpu_h=args.unit_gpu_h, spot_hourly=args.spot_hourly),
                     indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
