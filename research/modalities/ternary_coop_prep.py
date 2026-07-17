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
CALIB_TARGET = {"name": "SMARCA2", "acc": "P51531", "domain": "bromodomain",
                "template_pdb": "8G1Q",
                "is_template_smarca2_crystal": False,
                "note": "SMARCA2 bromodomain. Template = Wurz 8G1Q, a 3.73 A SMARCA4-compound1-VHL ternary (NOT a "
                        "SMARCA2 crystal); the SMARCA2 construct is built by substituting the SMARCA4 BD sequence "
                        "with the experimental SMARCA2 BD (P51531) and relaxing >=2 independent models. Recorded "
                        "as an explicit valB_mini limitation (reviewer 2026-07-17 Option-1)."}


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
        return {"role": "target", "name": "SMARCA2", "domain": CALIB_TARGET["domain"],
                "acc": CALIB_TARGET["acc"], "template_pdb": CALIB_TARGET["template_pdb"],
                "is_template_smarca2_crystal": CALIB_TARGET["is_template_smarca2_crystal"],
                "note": "SMARCA2 bromodomain MODELED from the 8G1Q SMARCA4 BD (sequence substitution + relax; "
                        "8G1Q is not a SMARCA2 crystal) — explicit valB_mini limitation."}
    return {"role": "target", "name": tgt, "note": "unresolved target"}


# valB_mini calib edge = the reviewer-approved Wurz cmpd1 -> cmpd4 CONSTITUTIONAL edge (pyridine->benzene linker;
# 8G1Q; ddG_coop_exp=+0.94 kcal/mol, alpha_SPR). The retired PROTAC 2->cis EPIMER file is kept ONLY as an
# endpoint-builder / null-map regression fixture (reviewer 2026-07-17 Option-1), never as the active calib edge.
CALIB_FROZEN_JSON = os.path.join(HERE, "wurz-calib-frozen.json")
CALIB_FROZEN_EPIMER_RETIRED = os.path.join(HERE, "ternary-calib-epimer-frozen.json")


def _load_calib_frozen(path=CALIB_FROZEN_JSON):
    """The reviewer-approved frozen calib edge (Wurz cmpd1 -> cmpd4, 8G1Q). Returns None if absent (keeps the
    harness importable before the freeze CI has run). SMILES are local (no network) — pure + testable."""
    if not os.path.exists(path):
        return None
    try:
        d = json.load(open(path))
    except Exception:  # noqa: BLE001
        return None
    return d if str(d.get("_status", "")).startswith("FROZEN") else None


def _morph_endpoints(leg, resolve_smiles=False):
    """The two alchemical endpoints (A->B) for a leg's morph. NR-V04 active/epimer resolve from the existing
    benchmark chemistry; the calibration hi/lo endpoints resolve from the FROZEN reviewer-approved epimer pair
    (PROTAC 2 -> cis-PROTAC 2, ternary-calib-epimer-frozen.json) — local SMILES, no network. If the freeze file
    is absent they stay `pending`. resolve_smiles=True triggers the (network) NR-V04 SMILES load."""
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
    else:  # calibration hi/lo — resolve from the frozen reviewer-approved Wurz cmpd1->cmpd4 edge (no fabrication)
        frozen = _load_calib_frozen()
        if frozen:
            by_role = {"calib_hi": frozen["calib_hi"]["smiles"], "calib_lo": frozen["calib_lo"]["smiles"]}
            smiles_a, smiles_b = by_role.get(a), by_role.get(b)
            status = "resolved_calib_wurz" if (smiles_a and smiles_b) else "calib_role_unmatched"
        else:
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
