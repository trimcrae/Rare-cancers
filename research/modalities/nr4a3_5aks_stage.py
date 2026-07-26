#!/usr/bin/env python3
"""RUNG 5a-KS — turn the two co-folded ternaries into the FEP engine's per-leg inputs.

THE CONTRACT. `nr4a3_ternary_fep.py` mounts, per leg, `<leg_id>/complex.pdb` (the protein) and
`<leg_id>/ligands.sdf` (the two morph endpoints, posed). This module produces exactly that for

    5aks_d0_to_d__ternary_nr4a3      CRBN + NR4A3-LBD + construct
    5aks_d0_to_d__ternary_nr4a1      CRBN + NR4A1-LBD + construct

WHY THIS IS NOT `ternary_fep_stage`. That module stages the FROZEN pilot bundle, whose E3 machinery is
VHL + Elongin B + Elongin C — three chains this rung does not have. 5a-KS recruits **CRBN**, a single chain.
Its `E3_ROLES` is a module constant, its manifest is built from `expand_pilot_legs()`, and `load_pilot_legs`
fails closed on any drift from the preregistered leg-id list, so pointing it at these legs would either break
that guard or silently enlarge a preregistered experiment. Separate rung, separate stager.

⚠ AND ITS LIGAND EXTRACTOR IS A STUB. `ternary_fep_stage._extract_ligand_sdf` is `return None` with a
SHAKEOUT-PENDING note — the ternary staging path in this repo has never produced a `ligands.sdf` from a
co-fold. So there was nothing to reuse and this implements it: gemmi splits polymer from non-polymer, RDKit
reads the ligand's heavy-atom coordinates and takes bond orders from the **committed d0 SMILES** via
`AssignBondOrdersFromTemplate`. That template step is what makes a coordinate-only ligand into a chemically
valid SDF, and using the design's own SMILES is what keeps the simulated molecule tied to the design.

BOTH ENDPOINTS COME FROM ONE POSE. `ligands.sdf` is the co-fold pose written twice, retitled `d0` and `d` —
the engine's pose repair re-imposes each endpoint's bond orders and stereo from SMILES and OpenFE's hybrid
topology handles the one-atom perturbation. Two independent co-folds would introduce a pose difference between
the endpoints that the alchemical transformation would have to absorb, contaminating `S` with something that
is not the physical question.

SHAKEOUT STATUS: the pure planner below is unit-tested and is the contract. `stage_from_cofold` needs gemmi +
RDKit + real Boltz output, so it runs on a CI runner, never in the dev sandbox — and it FABRICATES NOTHING: a
missing co-fold, a missing ligand, or a template mismatch is reported and staged as nothing.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import nr4a3_5aks_cofold as K     # noqa: E402  (the pair, the leg ids, the leg map — one home)

E3_ROLE = "CRBN"


def required_inputs_for_leg(lid):
    """The exact input contract for one 5a-KS leg. Pure."""
    spec = K.LEG_MAP.get(lid)
    if not spec:
        raise SystemExit(f"[5aks-stage] {lid} is not a 5a-KS leg — refusing to guess its chain roles")
    return {
        "leg_id": lid,
        "environment": spec["environment"],
        "needs_complex_pdb": True,
        "chain_roles": [E3_ROLE, spec["target"]],
        "ligand_endpoints": ["d0", "d"],
        "source_cofold_species": spec["target"],
    }


def staging_manifest(design_path=None):
    """Every leg's required inputs, plus the co-folds that must exist to supply them. Pure."""
    mp = K.load_pair(design_path) if design_path else K.load_pair()
    legs = [required_inputs_for_leg(lid) for lid in sorted(K.LEG_MAP)]
    return {
        "legs": legs,
        "source_cofolds": sorted({l["source_cofold_species"] for l in legs}),
        "endpoint_smiles": {"d0": mp["d0"]["smiles"], "d": mp["d"]["smiles"]},
        "contract": ("engine mounts <prefix>/<leg_id>/complex.pdb (chain_roles) + <leg_id>/ligands.sdf "
                     "(the ONE co-fold pose written twice, retitled d0 and d). Ternary only: the binary and "
                     "solvent legs cancel algebraically in S — see nr4a3_5aks_reduce."),
    }


def retitle_sdf(sdf_text, name):
    """Set each SDF record's title line to `name`, so OpenFE resolves the pose by `_Name`."""
    out = []
    for blk in sdf_text.split("$$$$"):
        if not blk.strip():
            continue
        lines = blk.lstrip("\n").split("\n")
        lines[0] = name
        out.append("\n".join(lines) + "$$$$\n")
    return "".join(out)


def _ligand_sdf_from_cif(cif_path, template_smiles):
    """Heavy-atom coordinates from the co-fold's non-polymer chain + bond orders from the design's SMILES.

    Returns (sdf_text, None) or (None, reason). Never returns a molecule it could not template-match: a
    silently mis-bonded ligand would run, converge, and give a wrong dG.
    """
    try:
        import gemmi
        from rdkit import Chem
    except Exception as e:  # noqa: BLE001
        return None, f"gemmi/rdkit unavailable (run on a CI runner): {e}"
    try:
        st = gemmi.read_structure(cif_path)
        st.setup_entities()
        lig_atoms = []
        for chain in st[0]:
            for res in chain:
                if res.het_flag == "H" and res.name not in ("HOH", "WAT"):
                    lig_atoms.append((chain.name, res))
        if not lig_atoms:
            return None, "no non-polymer residue in the co-fold CIF — the construct did not co-fold"
        # Boltz emits the ligand as one residue; if several, take the largest by heavy-atom count.
        _chain, res = max(lig_atoms, key=lambda cr: len(cr[1]))
        lines = ["HETATM%5d %-4s %3s %s%4d    %8.3f%8.3f%8.3f  1.00  0.00          %2s" % (
            i + 1, a.name[:4], "LIG", "X", 1, a.pos.x, a.pos.y, a.pos.z, a.element.name.upper())
            for i, a in enumerate(res) if a.element.name != "H"]
        pdb_block = "\n".join(lines) + "\nEND\n"
        raw = Chem.MolFromPDBBlock(pdb_block, removeHs=True, sanitize=False)
        if raw is None:
            return None, "RDKit could not read the extracted ligand coordinates"
        template = Chem.MolFromSmiles(template_smiles)
        if template is None:
            return None, "the design's d0 SMILES did not parse as a template"
        from rdkit.Chem import AllChem
        try:
            mol = AllChem.AssignBondOrdersFromTemplate(template, raw)
        except Exception as e:  # noqa: BLE001
            return None, (f"template match FAILED ({e}) — the co-folded ligand does not match the committed "
                          f"d0 SMILES ({template.GetNumHeavyAtoms()} heavy atoms vs "
                          f"{raw.GetNumAtoms()} extracted). Refusing to stage a mis-bonded ligand.")
        return Chem.MolToMolBlock(mol) + "$$$$\n", None
    except Exception as e:  # noqa: BLE001
        return None, f"co-fold parse failed: {e}"


def _write_protein_pdb(cif_path, out_pdb):
    """Write the co-fold's POLYMER chains (CRBN + the target LBD) to a PDB, dropping the ligand."""
    import gemmi
    st = gemmi.read_structure(cif_path)
    st.setup_entities()
    st.remove_ligands_and_waters()
    st.write_pdb(out_pdb)
    return sorted(ch.name for ch in st[0])


def stage_from_cofold(cofold_dir, out_dir, design_path=None):
    """Assemble both legs' inputs from the co-fold outputs on disk. Fabricates nothing."""
    man = staging_manifest(design_path)
    d0_smiles = man["endpoint_smiles"]["d0"]
    staged, missing = [], []
    for leg in man["legs"]:
        sp = leg["source_cofold_species"]
        pats = [os.path.join(cofold_dir, "**", f"*{sp.lower()}*model_0.cif"),
                os.path.join(cofold_dir, "**", f"*{sp}*model_0.cif"),
                os.path.join(cofold_dir, sp, "*.cif"), os.path.join(cofold_dir, sp.lower(), "*.cif")]
        cif = next((c for p in pats for c in sorted(glob.glob(p, recursive=True))), None)
        if not cif:
            missing.append({"leg": leg["leg_id"], "reason": f"no co-fold CIF for {sp} under {cofold_dir}"})
            continue
        sdf, why = _ligand_sdf_from_cif(cif, d0_smiles)
        if sdf is None:
            missing.append({"leg": leg["leg_id"], "cif": cif, "reason": why})
            continue
        leg_out = os.path.join(out_dir, leg["leg_id"])
        os.makedirs(leg_out, exist_ok=True)
        with open(os.path.join(leg_out, "ligands.sdf"), "w") as fh:
            fh.write(retitle_sdf(sdf, "d0") + retitle_sdf(sdf, "d"))
        chains = _write_protein_pdb(cif, os.path.join(leg_out, "complex.pdb"))
        staged.append({"leg": leg["leg_id"], "cif": cif, "chains": chains,
                       "expected_roles": leg["chain_roles"]})
    return {"staged": staged, "missing": missing, "out_dir": out_dir}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", action="store_true", help="print the pure staging manifest and exit")
    ap.add_argument("--cofold-dir", default=os.environ.get("COFOLD_DIR", ""))
    ap.add_argument("--out-dir", default=os.environ.get("OUTPUT_DIR", "5aks_fep_inputs"))
    args = ap.parse_args(argv)
    if args.manifest or not args.cofold_dir:
        print(json.dumps(staging_manifest(), indent=1))
        return 0
    res = stage_from_cofold(args.cofold_dir, args.out_dir)
    print(json.dumps(res, indent=1))
    if res["missing"]:
        raise SystemExit(f"[5aks-stage] {len(res['missing'])} leg(s) NOT staged — nothing was fabricated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
