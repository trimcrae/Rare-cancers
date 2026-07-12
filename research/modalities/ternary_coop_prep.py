#!/usr/bin/env python3
"""Ternary-cooperativity harness — pure ASSEMBLY / PREP layer (component spec per pilot morph leg).

The testable half of the physics ternary-coop engine: given a frozen pilot morph leg (ternary_coop.PILOT_LEG_MAP),
emit the SYSTEM-ASSEMBLY SPEC the relative-alchemical FEP would build — which protein components are present
(binary vs ternary environment), the E3 machinery (VHL + Elongin B/C), the target LBD, and the two morph
endpoints (SMILES A->B). The heavy OpenFE/OpenMM execution is a SEPARATE engine that consumes this spec; this
layer is pure + unit-tested so the assembly logic (the part most prone to a silent binary/ternary or
component mistake) is verified with no MD/GPU.

Reuses the FROZEN construct definitions from nrv04_ternary.py (VHL=P40337, Elongin B/C, the NR4A LBD ranges)
so the ternary FEP and the co-fold benchmark share one source of truth for the biology. No fabrication: the
calibration-PROTAC endpoints stay `pending` until the Layer-1 calib pair is frozen (numeric alpha curation);
NR-V04 active/epimer endpoints resolve from the existing benchmark chemistry (loaded lazily — network only when
actually requested, never at import).

Cooperativity cycle (why these environments): ddG_coop(A->B) = ddG_alch,ternary(A->B) - ddG_alch,binary(A->B).
So each analogue pair contributes a BINARY-environment morph (E3 + PROTAC, no target) and a TERNARY-environment
morph (E3 + target-LBD + PROTAC). The affinity-knockout / recruitment controls read off the same two legs.
"""
import json
import os

import ternary_coop as tcoop

HERE = os.path.dirname(os.path.abspath(__file__))

# Frozen construct definitions — imported from the co-fold benchmark module so biology is single-sourced.
# (Imported lazily-safe: nrv04_ternary defines these as module constants with no network at import.)
import nrv04_ternary as _nv

E3_VHL = {"recruiter": "VHL", "acc": _nv.VHL, "partners": [("ElonginB", _nv.ELONGIN_B), ("ElonginC", _nv.ELONGIN_C)]}
NR4A_LBD = _nv.TARGETS   # {'NR4A1':{acc,lo,hi,...}, 'NR4A2':..., 'NR4A3':...}

# Target of the SMARCA2-VHL calibration series (bromodomain). Sequence/definition frozen at curation time with
# the calib pair; recorded here as the target identity only.
CALIB_TARGET = {"name": "SMARCA2", "domain": "bromodomain", "note": "exact residue range frozen with the calib pair"}


def _e3_components(with_vbc=True):
    comps = [{"role": "E3_recruiter", "name": E3_VHL["recruiter"], "acc": E3_VHL["acc"]}]
    if with_vbc:
        for nm, acc in E3_VHL["partners"]:
            comps.append({"role": "E3_partner", "name": nm, "acc": acc})
    return comps


def _target_component(leg):
    """The target LBD/domain component for a TERNARY leg (None for a binary leg)."""
    if leg["environment"] != "ternary":
        return None
    tgt = leg.get("target")
    if tgt in NR4A_LBD:
        d = NR4A_LBD[tgt]
        return {"role": "target", "name": tgt, "acc": d["acc"], "lbd_lo": d["lo"], "lbd_hi": d["hi"],
                "lbd_rule": "C-terminal 254 residues (NR4A3 explicit 373-626)"}
    if tgt == "SMARCA2":
        return {"role": "target", "name": "SMARCA2", "domain": CALIB_TARGET["domain"], "acc": None,
                "note": "frozen with the calib pair"}
    return {"role": "target", "name": tgt, "note": "unresolved target"}


def _morph_endpoints(leg, resolve_smiles=False):
    """The two alchemical endpoints (A->B) for a leg's morph. NR-V04 active/epimer resolve from the existing
    benchmark chemistry; the calibration hi/lo endpoints stay `pending` until the Layer-1 calib pair is frozen.
    resolve_smiles=True triggers the (network) NR-V04 SMILES load; default False keeps this pure/testable."""
    morph = leg["morph"]  # e.g. 'NRV04_active -> NRV04_epimer' or 'calib_hi -> calib_lo'
    a, b = [s.strip() for s in morph.split("->")]
    smiles_a = smiles_b = None
    status = "resolved"
    if a.startswith("NRV04") or b.startswith("NRV04"):
        if resolve_smiles:
            try:
                active = _nv.load_nrv04_smiles()
                negs = _nv.load_negative_ligands()
                epimer = negs.get("neg_inactive", (None,))[0]
                smiles_a = active if a.endswith("active") else epimer
                smiles_b = epimer if b.endswith("epimer") else active
            except Exception:  # noqa: BLE001 — network/parse; keep the spec, mark unresolved
                status = "smiles_unresolved (network)"
        else:
            status = "nrv04_endpoints_available_lazy"
    else:  # calibration hi/lo — PENDING the frozen Layer-1 calib pair (no fabrication)
        status = "pending_calib_pair_freeze"
    return {"endpoint_a": a, "endpoint_b": b, "smiles_a": smiles_a, "smiles_b": smiles_b, "status": status}


def assembly_for_leg(leg, resolve_smiles=False):
    """Full component-assembly spec for one pilot morph leg: environment, protein components (E3 [+ target if
    ternary]), the ligand morph endpoints, and the coop-cycle role."""
    comps = _e3_components(with_vbc=True)
    tgt = _target_component(leg)
    if tgt is not None:
        comps.append(tgt)
    return {
        "leg_id": leg["id"], "environment": leg["environment"], "e3": E3_VHL["recruiter"],
        "protein_components": comps,
        "has_target": tgt is not None,
        "morph": _morph_endpoints(leg, resolve_smiles=resolve_smiles),
        "coop_role": ("ternary arm (ddG_alch,ternary)" if leg["environment"] == "ternary"
                      else "binary arm (ddG_alch,binary)"),
        "purpose": leg["purpose"],
    }


def assemble_pilot(resolve_smiles=False):
    """The assembly spec for every frozen pilot leg (reads ternary_coop.load_pilot_legs; drift fails closed)."""
    return [assembly_for_leg(leg, resolve_smiles=resolve_smiles) for leg in tcoop.load_pilot_legs()]


def _cli(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Ternary-coop assembly/prep layer: component spec per pilot leg.")
    ap.add_argument("--resolve-smiles", action="store_true", help="also resolve NR-V04 SMILES (network)")
    args = ap.parse_args(argv)
    print(json.dumps(assemble_pilot(resolve_smiles=args.resolve_smiles), indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
