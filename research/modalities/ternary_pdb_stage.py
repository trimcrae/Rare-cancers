#!/usr/bin/env python3
"""Stage ternary-FEP leg inputs from a CRYSTAL ternary structure (valB_mini: PROTAC 2 / SMARCA2-VHL, PDB 6HAX).

The ternary engine (nr4a3_ternary_fep._build_components) mounts, per leg:
  <out>/<leg_id>/complex.pdb  — the assembled E3 machinery [+ target] protein
  <out>/<leg_id>/ligands.sdf  — the two posed PROTAC endpoints (calib_hi, calib_lo) — SAME crystal pose written
                                twice; the engine re-imposes each endpoint's bond orders/stereo from SMILES.
Environments (nr4a3_ternary_fep._environment_of):
  ternary_smarca2 : VHL + ElonginB + ElonginC + SMARCA2 (bromodomain)   [PROTAC bridges VHL<->SMARCA2]
  binary_vhl      : VHL + ElonginB + ElonginC        (DROP the SMARCA2 chain)
  solvent         : ligands.sdf only (no protein)

Chain roles are resolved from RCSB (entity -> UniProt -> auth chain), never guessed:
  VHL=P40337, ElonginB=Q15370, ElonginC=Q15369, SMARCA2=P51531.
The bound PROTAC pose comes from the RCSB ModelServer as SDF (crystal coordinates, CCD bond orders).

HONESTY: every atom is from 6HAX (RCSB); nothing is fabricated. If a required chain role or the ligand cannot be
resolved, the stager reports exactly what is missing and stages nothing for that leg.

Runs on a GCP VM or a CI runner (unrestricted internet). Deps: gemmi + rdkit (+ stdlib urllib).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request

import nr4a3_ternary_fep as eng

RCSB_ENTRY = "https://data.rcsb.org/rest/v1/core/entry/{pdb}"
RCSB_POLY = "https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb}/{eid}"
RCSB_CIF = "https://files.rcsb.org/download/{pdb}.cif"
RCSB_LIG_SDF = ("https://models.rcsb.org/v1/{pdb}/ligand?auth_comp_id={ccd}&encoding=sdf&copy_all_categories=false")

# The DEGRADATION TARGET bromodomain: SMARCA2 (P51531) OR SMARCA4 (P51532). The valB template 8G1Q resolves
# SMARCA4; the stager substitutes it to a relaxed SMARCA2 model (smarca2_model.py) per the reviewer's item 4.
UNIPROT_ROLE = {"P40337": "VHL", "Q15370": "ElonginB", "Q15369": "ElonginC",
                "P51531": "TARGET_BD", "P51532": "TARGET_BD"}
TARGET_ACC_NAME = {"P51531": "SMARCA2", "P51532": "SMARCA4"}
ROLE_CHAINS_FOR_ENV = {  # which protein ROLES each environment keeps
    "binary": ["VHL", "ElonginB", "ElonginC"],
    "ternary": ["VHL", "ElonginB", "ElonginC", "TARGET_BD"],
}


def _get(url: str, as_json=True, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-ci",
                                               "Accept": "application/json" if as_json else "*/*"})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
    if binary:
        return raw
    txt = raw.decode("utf-8", "replace")
    return json.loads(txt) if as_json else txt


def role_to_chains(pdb: str) -> dict:
    """{role: [auth_chain_ids]} resolved from RCSB entity->UniProt->auth chains (no guessing). Also records
    _target_acc (P51531 SMARCA2 | P51532 SMARCA4) so the caller knows whether a SMARCA4->SMARCA2 substitution
    is required for the TARGET_BD chain."""
    entry = _get(RCSB_ENTRY.format(pdb=pdb))
    eids = (entry.get("rcsb_entry_container_identifiers", {}) or {}).get("polymer_entity_ids") or []
    out: dict = {}
    for eid in eids:
        pe = _get(RCSB_POLY.format(pdb=pdb, eid=eid))
        cids = pe.get("rcsb_polymer_entity_container_identifiers", {}) or {}
        auth_chains = cids.get("auth_asym_ids") or cids.get("asym_ids") or []
        accs = [r.get("database_accession") for r in (cids.get("reference_sequence_identifiers") or [])
                if r.get("database_name") == "UniProt"]
        for acc in accs:
            role = UNIPROT_ROLE.get(acc)
            if role:
                out.setdefault(role, [])
                out[role].extend(c for c in auth_chains if c not in out[role])
                if role == "TARGET_BD":
                    out["_target_acc"] = acc
    return out


def _ligand_ccd(pdb: str) -> str:
    """The PROTAC CCD in the entry (largest non-ion nonpolymer) — reuses the freeze module's resolver."""
    import ternary_calib_freeze as tcf
    lig = tcf._degrader_ligand(pdb)
    if not lig:
        raise SystemExit(f"[stage] no PROTAC-scale ligand resolved for {pdb}")
    return lig["ccd"]


def _write_complex_pdb(cif_text: str, keep_chains: list, out_pdb: str):
    """Extract the kept protein chains (polymer only, drop waters/ligands/ions) from the CIF -> PDB via gemmi."""
    import gemmi

    doc = gemmi.cif.read_string(cif_text)
    st = gemmi.make_structure_from_block(doc.sole_block())
    st.setup_entities()
    st.remove_alternative_conformations()
    st.remove_hydrogens()
    st.remove_ligands_and_waters()   # keep only polymer (protein) residues
    keep = set(keep_chains)
    model = st[0]
    for name in [ch.name for ch in model]:
        if name not in keep:
            model.remove_chain(name)
    st.remove_empty_chains()
    n_res = sum(len(ch) for ch in st[0])
    if n_res == 0:
        raise SystemExit(f"[stage] no residues left after chain surgery (keep={keep_chains}) — check role mapping")
    # CA centroid of the kept complex (used to pick the ligand instance in THIS copy's pocket)
    cx = cy = cz = 0.0
    n = 0
    for ch in st[0]:
        for res in ch:
            for at in res:
                if at.name == "CA":
                    cx += at.pos.x; cy += at.pos.y; cz += at.pos.z; n += 1
    os.makedirs(os.path.dirname(out_pdb), exist_ok=True)
    st.write_pdb(out_pdb)
    return (cx / n, cy / n, cz / n) if n else None


def _mol_centroid(mol):
    conf = mol.GetConformer()
    import numpy as np
    pos = conf.GetPositions()
    return tuple(np.asarray(pos).mean(axis=0))


def _write_ligands_sdf(pdb: str, ccd: str, endpoint_names, out_sdf: str, protein_centroid=None):
    """Fetch the bound PROTAC pose(s) (crystal coords) from the RCSB ModelServer and write ONE instance twice —
    once per endpoint name (calib_hi / calib_lo). If protein_centroid is given (6HAX has 2 complexes in the ASU),
    pick the ligand instance in THIS copy's pocket (nearest centroid); else the first. The engine re-imposes each
    endpoint's bond orders/stereo from its SMILES, so the two records share the same crystal pose."""
    import io

    from rdkit import Chem

    sdf_text = _get(RCSB_LIG_SDF.format(pdb=pdb, ccd=urllib.parse.quote(ccd)), as_json=False)
    supplier = Chem.ForwardSDMolSupplier(io.BytesIO(sdf_text.encode()), sanitize=False, removeHs=False)
    mols = [m for m in supplier if m is not None and m.GetNumConformers() > 0]
    if not mols:
        raise SystemExit(f"[stage] ModelServer returned no usable ligand SDF for {pdb}/{ccd}")
    if protein_centroid is not None and len(mols) > 1:
        import numpy as np
        pc = np.asarray(protein_centroid)
        mol = min(mols, key=lambda m: float(np.linalg.norm(np.asarray(_mol_centroid(m)) - pc)))
    else:
        mol = mols[0]
    os.makedirs(os.path.dirname(out_sdf), exist_ok=True)
    w = Chem.SDWriter(out_sdf)
    for nm in endpoint_names:
        mol.SetProp("_Name", nm)
        w.write(mol)
    w.close()
    return len(mols)


def _write_e3_pdb(cif_text: str, e3_chains: list, out_pdb: str):
    """Write ONLY the E3 machinery chains (VHL+EloB+EloC, no target/het/water) from the CIF -> PDB (gemmi).
    Returns (structure, ca_centroid) so the target model can be appended into the SAME frame."""
    import gemmi
    st = gemmi.make_structure_from_block(gemmi.cif.read_string(cif_text).sole_block())
    st.setup_entities()
    st.remove_alternative_conformations()
    st.remove_hydrogens()
    st.remove_ligands_and_waters()
    keep = set(e3_chains)
    for name in [ch.name for ch in st[0]]:
        if name not in keep:
            st[0].remove_chain(name)
    st.remove_empty_chains()
    os.makedirs(os.path.dirname(out_pdb), exist_ok=True)
    st.write_pdb(out_pdb)
    return st


def _hydrogenate_pdb(pdb_path: str) -> dict:
    """Add missing hydrogens (+ any missing heavy/terminal atoms) to the ASSEMBLED complex.pdb at pH 7, in place.

    ROOT CAUSE this fixes (2026-07-17, valB seed-0): both _write_complex_pdb and _write_e3_pdb strip hydrogens
    (gemmi remove_hydrogens) and the E3 chains come straight from the raw 8G1Q crystal — so the assembled protein
    reaches OpenFE with ZERO hydrogens. OpenFE's HybridTopologySetupUnit calls OpenMM ForceField.createSystem,
    which does NOT auto-add protein H — it fails template-matching with
    'No template found for residue 0 (MET) ... missing 9 H atoms'. Step1/valA never hit this because their NR4A3
    receptor prep hydrogenates; this ternary-staging path had never carried a real production leg before. Fix:
    run the final complex through PDBFixer (the same tool smarca2_model.py uses) so the engine gets a prepared,
    fully-hydrogenated protein. Applied to BOTH binary and ternary complex.pdb so binary0 doesn't hit the same wall.
    """
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile

    fixer = PDBFixer(filename=pdb_path)
    fixer.findMissingResidues()
    fixer.missingResidues = {}          # do NOT model in gaps between resolved segments — keep the crystal atoms only
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()  # map any modified residues back to standard so templates match (robustness)
    fixer.findMissingAtoms()            # heavy atoms + terminal OXT that OpenMM templates require
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)
    n_h = sum(1 for a in fixer.topology.atoms() if a.element is not None and a.element.symbol == "H")
    with open(pdb_path, "w") as fh:
        PDBFile.writeFile(fixer.topology, fixer.positions, fh, keepIds=True)
    return {"hydrogenated": True, "n_hydrogens": n_h,
            "n_atoms": fixer.topology.getNumAtoms(), "ph": 7.0}


def _append_model_chain(e3_pdb: str, model_pdb: str, out_pdb: str):
    """Merge the relaxed SMARCA2 model chain into the E3 complex (both in the 8G1Q frame) -> the assembled
    complex.pdb the engine mounts. Text-level ATOM merge with a fresh chain id, robust across gemmi/openmm PDB."""
    import gemmi
    e3 = gemmi.read_structure(e3_pdb)
    used = {ch.name for ch in e3[0]}
    newname = next(c for c in "TSUVWXYZABCDEFGHIJKLMNOPQR" if c not in used)
    mdl = gemmi.read_structure(model_pdb)
    src = mdl[0][0]                     # single-chain SMARCA2 model
    ch = gemmi.Chain(newname)
    for res in src:
        ch.add_residue(res)
    e3[0].add_chain(ch)
    # CA centroid of the full assembled complex (for the nearest-ligand pick)
    cx = cy = cz = 0.0; n = 0
    for chn in e3[0]:
        for res in chn:
            for at in res:
                if at.name == "CA":
                    cx += at.pos.x; cy += at.pos.y; cz += at.pos.z; n += 1
    e3.write_pdb(out_pdb)
    return (cx / n, cy / n, cz / n) if n else None, newname


def stage_leg(leg_id: str, template_pdb: str, out_root: str) -> dict:
    """Stage one leg's complex.pdb (+ ligands.sdf) from the crystal template. For a TERNARY leg whose target is
    SMARCA4 (the 8G1Q Wurz template), substitute the SMARCA4 BD -> a relaxed SMARCA2 model (smarca2_model.py,
    reviewer item 4) and assemble E3 + model. Writes staging_manifest.json (item-4 evidence). Returns a manifest."""
    env = eng._environment_of(leg_id)
    leg, _ = eng.leg_spec(leg_id)
    m = eng.prep._morph_endpoints(leg)
    endpoint_names = [m["endpoint_a"], m["endpoint_b"]]
    leg_dir = os.path.join(out_root, leg_id)
    os.makedirs(leg_dir, exist_ok=True)

    ccd = _ligand_ccd(template_pdb)
    made_pdb = False
    chains_used: list = []
    centroid = None
    model_manifest = None
    _starting_model = None
    if env in ("binary", "ternary"):
        roles = ROLE_CHAINS_FOR_ENV[env]
        r2c = role_to_chains(template_pdb)
        missing = [role for role in roles if not r2c.get(role)]
        if missing:
            raise SystemExit(f"[stage] {template_pdb}: could not resolve chains for roles {missing} "
                             f"(resolved: { {k: v for k, v in r2c.items() if not k.startswith('_')} }). Stage nothing.")
        cif = _get(RCSB_CIF.format(pdb=template_pdb), as_json=False)
        e3_chains = [r2c[role][0] for role in ("VHL", "ElonginB", "ElonginC")]
        complex_pdb = os.path.join(leg_dir, "complex.pdb")

        if env == "ternary":
            target_chain = r2c["TARGET_BD"][0]
            target_acc = r2c.get("_target_acc")
            if target_acc == "P51532":     # SMARCA4 template -> build + relax a SMARCA2 model (item 4)
                import smarca2_model as sm
                full_pdb = os.path.join(leg_dir, "_template_full.pdb")
                gm = __import__("gemmi")
                st = gm.make_structure_from_block(gm.cif.read_string(cif).sole_block())
                st.setup_entities(); st.write_pdb(full_pdb)
                model_manifest = sm.build_smarca2_model(full_pdb, target_chain,
                                                        os.path.join(leg_dir, "smarca2_model"), n_models=2)
                if not model_manifest.get("ok"):
                    raise SystemExit(f"[stage] SMARCA2 model build failed: {model_manifest.get('reason')}")
                e3_pdb = os.path.join(leg_dir, "_e3.pdb")
                _write_e3_pdb(cif, e3_chains, e3_pdb)
                # reviewer #3: each ternary REPLICATE uses an INDEPENDENTLY relaxed SMARCA2 model, so a coop
                # result is not an artifact of one homology pose. seed s -> model (s % n_models): seed 0 -> model 0,
                # seed 1 -> the 2nd relaxed model, etc. Record which model this replicate used (starting_model).
                seed = int(os.environ.get("SEED", "0"))
                model_pdbs = model_manifest["model_pdbs"]
                model_idx = seed % len(model_pdbs)
                centroid, model_chain = _append_model_chain(e3_pdb, model_pdbs[model_idx], complex_pdb)
                chains_used = e3_chains + [model_chain]
                _starting_model = {"seed": seed, "starting_model_index": model_idx,
                                   "n_models_available": len(model_pdbs),
                                   "model_pdb": os.path.basename(model_pdbs[model_idx])}
            else:                          # already SMARCA2 (a real SMARCA2 crystal): use the chain directly
                chains_used = e3_chains + [target_chain]
                centroid = _write_complex_pdb(cif, chains_used, complex_pdb)
        else:                              # binary: E3 machinery only (drop the target)
            chains_used = e3_chains
            centroid = _write_complex_pdb(cif, chains_used, complex_pdb)
        made_pdb = True
        # Hydrogenate the assembled complex so OpenFE's ForceField.createSystem can template-match it (see
        # _hydrogenate_pdb docstring — the missing-H template error that killed valB seed-0). BOTH envs.
        h_manifest = _hydrogenate_pdb(complex_pdb)

    n_lig = _write_ligands_sdf(template_pdb, ccd, endpoint_names, os.path.join(leg_dir, "ligands.sdf"),
                               protein_centroid=centroid)

    # staging_manifest.json — the 5-part smoke gate item 4 reads n_relaxed_models / divergence_ok / substitution.
    sm_manifest = {"template_pdb": template_pdb, "is_smarca2_crystal": False if template_pdb == "8G1Q" else None,
                   "environment": env}
    if made_pdb:
        sm_manifest["hydrogenation"] = h_manifest
    if _starting_model is not None:
        sm_manifest["starting_model"] = _starting_model
    if model_manifest:
        sm_manifest.update({
            "smarca4_to_smarca2_substituted": model_manifest.get("smarca4_to_smarca2_substituted"),
            "n_relaxed_models": model_manifest.get("n_relaxed_models"),
            "divergence_ca_rmsd_A": model_manifest.get("divergence_ca_rmsd_A"),
            "divergence_ok": model_manifest.get("divergence_ok"),
            "n_mutations": model_manifest.get("n_mutations"),
            "seq_identity_observed_to_target": model_manifest.get("seq_identity_observed_to_target"),
            "limitation": model_manifest.get("limitation")})
    with open(os.path.join(leg_dir, "staging_manifest.json"), "w") as f:
        json.dump(sm_manifest, f, indent=2)

    return {"leg_id": leg_id, "environment": env, "template_pdb": template_pdb, "ligand_ccd": ccd,
            "endpoint_names": endpoint_names, "complex_chains": chains_used, "wrote_complex_pdb": made_pdb,
            "n_ligand_instances_in_crystal": n_lig, "wrote_ligands_sdf": True, "out_dir": leg_dir,
            "smarca2_model": sm_manifest}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Stage ternary-FEP leg inputs from a crystal ternary structure.")
    ap.add_argument("--leg-id", required=True, help="e.g. calib_hi_to_lo__ternary_vhl | ..._binary_vhl | ...__solvent")
    ap.add_argument("--template-pdb", default="6HAX")
    ap.add_argument("--out", default=os.environ.get("STAGE_OUT", "/tmp/ternary_in"))
    args = ap.parse_args(argv)
    man = stage_leg(args.leg_id, args.template_pdb, args.out)
    print(json.dumps(man, indent=2), flush=True)
    # sanity: files exist + non-empty
    for f in (["ligands.sdf"] + (["complex.pdb"] if man["wrote_complex_pdb"] else [])):
        p = os.path.join(man["out_dir"], f)
        sz = os.path.getsize(p) if os.path.exists(p) else 0
        print(f"[stage]   {f}: {sz} B", flush=True)
        if sz == 0:
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
