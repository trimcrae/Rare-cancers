#!/usr/bin/env python3
"""Freeze the reviewer-approved valB_mini calibration edge: PROTAC 2 -> cis-PROTAC 2 (SMARCA2-VHL).

Reviewer verdict (2026-07-17): the SMARCA2-VHL PROTAC 2 / cis-PROTAC 2 pair is the valB_mini known-answer edge —
a SAME-ASSAY, same-paper (Farnaby et al. 2019) TR-FRET cooperativity contrast (alpha 18 -> 1.0, ~18x) that is
ALSO a single-stereocenter congeneric perturbation (the VHL 4-hydroxyproline trans->cis epimerization that
abolishes VHL binding). PROTAC 2's ternary complex is solved (PDB 6HAX), so ONE crystallographic template
stages both endpoints (the active pose; the engine's pose repair re-imposes each endpoint's stereo from SMILES),
exactly like the NR-V04 active->epimer arm. Preregistered quantitative target:
    ddG_exp = -RT ln(alpha_cis/alpha_active) = -RT ln(1/18) = +1.71 kcal/mol at 298.15 K.

WHAT: fetch PROTAC 2's bound-ligand chemistry from 6HAX (RCSB), then construct cis-PROTAC 2 by inverting the
4-hydroxyproline stereocenter with RDKit (REPORTED explicitly, not silent), validate the two differ only in that
stereo, and emit the frozen pair with provenance + the preregistered target + the reviewer's GO/NO-GO gates. No
chemistry fabricated: the active SMILES is RCSB's; the epimer is a defined single-center inversion of it.
"""
from __future__ import annotations

import json
import math
import os
import sys

import ternary_calib_freeze as tcf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ternary-calib-epimer-frozen.json")

ACTIVE_PDB = "6HAX"                 # PROTAC 2 SMARCA2-VHL ternary (Farnaby et al. 2019, Nat Chem Biol)
ALPHA_ACTIVE, ALPHA_CIS = 18.0, 1.0
RT_298 = 1.987204e-3 * 298.15      # kcal/mol
DDG_EXP = -RT_298 * math.log(ALPHA_CIS / ALPHA_ACTIVE)   # +1.71 kcal/mol (active->cis)

# 4-hydroxyproline substructure: pyrrolidine N-ring with a ring carbon bearing a hydroxyl (the VHL-ligand C4).
HYP_SMARTS = "[NX3;R]1[CX4;R][CX4;R][CX4;R]([OX2H1])[CX4;R]1"


def _epimerize_hydroxyproline(smiles: str) -> dict:
    """Return the cis epimer SMILES by inverting the 4-hydroxyproline stereocenter. Reports the atom inverted."""
    from rdkit import Chem

    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return {"ok": False, "reason": "active SMILES did not parse"}
    Chem.AssignStereochemistry(m, cleanIt=True, force=True)
    patt = Chem.MolFromSmarts(HYP_SMARTS)
    matches = m.GetSubstructMatches(patt)
    if not matches:
        return {"ok": False, "reason": "no 4-hydroxyproline substructure found — cannot define the epimer center"}
    # the OH-bearing ring carbon = the match atom with an -OH neighbour
    c4 = None
    for match in matches:
        for idx in match:
            a = m.GetAtomWithIdx(idx)
            if a.GetSymbol() == "C" and any(nb.GetSymbol() == "O" and nb.GetTotalNumHs() >= 1
                                            for nb in a.GetNeighbors()):
                c4 = idx
                break
        if c4 is not None:
            break
    if c4 is None:
        return {"ok": False, "reason": "found hydroxyproline ring but no OH-bearing stereocenter"}
    a = m.GetAtomWithIdx(c4)
    tag = a.GetChiralTag()
    if tag == Chem.ChiralType.CHI_TETRAHEDRAL_CW:
        a.SetChiralTag(Chem.ChiralType.CHI_TETRAHEDRAL_CCW)
    elif tag == Chem.ChiralType.CHI_TETRAHEDRAL_CCW:
        a.SetChiralTag(Chem.ChiralType.CHI_TETRAHEDRAL_CW)
    else:
        return {"ok": False, "reason": f"hydroxyproline C4 (atom {c4}) is not a defined stereocenter in the input"}
    Chem.AssignStereochemistry(m, cleanIt=True, force=True)
    epi = Chem.MolToSmiles(m)
    return {"ok": True, "epimer_smiles": epi, "inverted_atom_idx": c4,
            "inverted_atom_env": Chem.MolFragmentToSmiles(m, atomsToUse=[c4] + [n.GetIdx() for n in a.GetNeighbors()])}


def _validate_pair(active: str, epimer: str) -> dict:
    """The two must share the SAME 2D constitution (identical connectivity) and differ ONLY in stereo."""
    from rdkit import Chem

    ma, me = Chem.MolFromSmiles(active), Chem.MolFromSmiles(epimer)
    flat_a = Chem.MolToSmiles(Chem.MolFromSmiles(Chem.MolToSmiles(ma)), isomericSmiles=False)
    flat_e = Chem.MolToSmiles(Chem.MolFromSmiles(Chem.MolToSmiles(me)), isomericSmiles=False)
    same_constitution = flat_a == flat_e
    differ_in_stereo = Chem.MolToSmiles(ma) != Chem.MolToSmiles(me)
    return {"same_2d_constitution": same_constitution, "differ_in_stereo": differ_in_stereo,
            "n_heavy": ma.GetNumHeavyAtoms(),
            "congeneric_edge": bool(same_constitution and differ_in_stereo),
            "note": "an active->epimer edge is a 0-heavy-atom perturbation (pure stereocenter inversion) — the "
                    "cleanest possible congeneric RBFE morph; the mapper maps every heavy atom."}


def freeze() -> dict:
    lig = tcf._degrader_ligand(ACTIVE_PDB)
    if not lig:
        return {"_status": "INCOMPLETE — RCSB returned no PROTAC-scale ligand for 6HAX", "active_pdb": ACTIVE_PDB}
    active_smiles = lig.get("smiles_stereo") or lig["smiles"]
    epi = _epimerize_hydroxyproline(active_smiles)
    result = {
        "_status": "FROZEN" if epi.get("ok") else "INCOMPLETE — could not define the cis epimer",
        "_provenance": "PROTAC 2 SMILES from RCSB 6HAX; cis-PROTAC 2 = defined single-stereocenter inversion "
                       "of the VHL 4-hydroxyproline; alpha values from Farnaby et al. 2019 (same TR-FRET table).",
        "reviewer_approval": "valB_mini per reviewer 2026-07-17 conditional approval (modified Option A).",
        "calib_hi": {"role": "calib_hi", "name": "PROTAC_2", "state": "active", "pdb": ACTIVE_PDB,
                     "ccd": lig["ccd"], "smiles": active_smiles, "mw": lig.get("mw"),
                     "alpha_TR_FRET": ALPHA_ACTIVE, "source": f"RCSB {ACTIVE_PDB} / Farnaby 2019"},
        "calib_lo": {"role": "calib_lo", "name": "cis_PROTAC_2", "state": "epimer_inactive",
                     "modeled_from": ACTIVE_PDB, "smiles": epi.get("epimer_smiles"),
                     "alpha_TR_FRET": ALPHA_CIS, "epimerization": epi,
                     "note": "cis-4-hydroxyproline; abolishes VHL binding (weak/non-binder) — the reviewer's "
                             "cis-endpoint diagnostics (ligand RMSD, VHL contact occupancy, restraint work + "
                             "sensitivity) MUST be reported; a pass produced only by forcibly retaining the "
                             "active crystallographic pose is NOT a pass."},
        "morph": "PROTAC_2 -> cis_PROTAC_2 (active -> epimer)",
        "preregistered_target": {
            "ddG_exp_kcal_per_mol": round(DDG_EXP, 3), "temperature_K": 298.15,
            "formula": "ddG_exp = -RT ln(alpha_cis/alpha_active) = -RT ln(1/18)",
            "alpha_active": ALPHA_ACTIVE, "alpha_cis": ALPHA_CIS},
        "prereg_gates": {
            "GO_to_valB_full": ["positive sign", "combined uncertainty excludes zero",
                                "estimate within 1.0 kcal/mol of +1.71", "independent repeats AND fwd/rev agree "
                                "within ~0.5 kcal/mol", "overlap + sampling diagnostics pass"],
            "NO_GO": ["converged wrong sign", "converged error > 1.0 kcal/mol",
                      "strong dependence on restraints or initialization"],
            "INDETERMINATE_not_a_pass": ["CI includes zero", "unresolved hysteresis",
                                         "cis endpoint cannot be represented as a defensible thermodynamic state"],
            "scope": "valB_mini GATES spending on valB_full; it does NOT by itself authorize the NR4A flagship "
                     "matrix. valB_full must add >=1 all-binding graded congeneric edge (e.g. Wurz 1->4)."},
    }
    if epi.get("ok"):
        result["validation"] = _validate_pair(active_smiles, epi["epimer_smiles"])
    return result


def main() -> int:
    r = freeze()
    with open(OUT, "w") as f:
        json.dump(r, f, indent=2)
    print(json.dumps(r, indent=2), flush=True)
    print(f"[epimer-freeze] wrote {OUT}", flush=True)
    ok = r.get("validation", {}).get("congeneric_edge")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
