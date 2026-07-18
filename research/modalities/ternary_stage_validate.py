#!/usr/bin/env python3
"""CPU validation of the FULL ternary staging (E3 + relaxed SMARCA2 model + PROTAC pose) from Wurz 8G1Q.

Runs stage_leg for the three valB_mini legs (ternary / binary / solvent) on the 8G1Q template and asserts each
leg's outputs exist and, for the ternary leg, that the SMARCA4->SMARCA2 substitution + >=2-model divergence
(staging_manifest.json / gate item 4) are satisfied. Fast on CPU (SMARCA2_SOLVENT=vacuum). The GPU ternary smoke
runs the SAME stage_leg on the VM (gbn2), so a green here means the paid lane only re-checks the assembly + the
openfe hybrid-topology build.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ternary_pdb_stage as stg  # noqa: E402

OUT = os.environ.get("STAGE_VALIDATE_OUT", "/tmp/stage_val")
TEMPLATE = os.environ.get("VALIDATE_PDB", "8G1Q")
LEGS = ["calib_hi_to_lo__ternary_vhl", "calib_hi_to_lo__binary_vhl", "calib_hi_to_lo__solvent"]


def _forcefield_check(complex_pdb):
    """Parameterize the hydrogenated protein complex with amber14 (OpenFE's protein FF) — the exact
    ForceField.createSystem template match that failed with missing hydrogens. Returns (ok, message)."""
    if not os.path.exists(complex_pdb):
        return False, "complex.pdb missing"
    try:
        from openmm import app
        pdb = app.PDBFile(complex_pdb)
        ff = app.ForceField("amber14-all.xml")
        ff.createSystem(pdb.topology)     # no solvent needed — this is the protein template-match that failed
        n_h = sum(1 for a in pdb.topology.atoms() if a.element is not None and a.element.symbol == "H")
        return True, "system built; %d H atoms, %d total" % (n_h, pdb.topology.getNumAtoms())
    except Exception as e:  # noqa: BLE001
        return False, "%s: %s" % (type(e).__name__, str(e)[:200])


def _protein_atoms(complex_pdb):
    """[(label, x, y, z)] for every atom in the assembled protein, label = 'CHAIN:RESNAME RESSEQ:ATOM'."""
    from openmm import app
    pdb = app.PDBFile(complex_pdb)
    pos = pdb.positions.value_in_unit(__import__("openmm").unit.angstrom)
    out = []
    for at in pdb.topology.atoms():
        r = at.residue
        lbl = f"{r.chain.id}:{r.name}{r.id}:{at.name}"
        p = pos[at.index]
        out.append((lbl, float(p[0]), float(p[1]), float(p[2]), at.residue.chain.id, int(at.residue.index)))
    return out


def _ligand_atoms(ligands_sdf):
    """[(label, x, y, z)] for the first ligand conformer (angstrom), label = 'LIG:ELEM idx'."""
    from rdkit import Chem
    supp = Chem.SDMolSupplier(ligands_sdf, removeHs=False, sanitize=False)
    mol = next((m for m in supp if m is not None), None)
    if mol is None or mol.GetNumConformers() == 0:
        return []
    conf = mol.GetConformer()
    out = []
    for a in mol.GetAtoms():
        p = conf.GetAtomPosition(a.GetIdx())
        out.append((f"LIG:{a.GetSymbol()}{a.GetIdx()}", float(p.x), float(p.y), float(p.z)))
    return out


def _clash_check(complex_pdb, ligands_sdf):
    """Report the closest NON-bonded atom pairs in the assembled starting structure — a near-coincident
    pair (<~0.5 A) is the classic cause of a warmup state-1 SimulationNaNError that survives minimization.
    Checks protein-internal (different residues) AND protein<->ligand. CPU-only; non-fatal on any error."""
    import numpy as np
    prot = _protein_atoms(complex_pdb)
    lig = _ligand_atoms(ligands_sdf)
    print(f"  [clash] protein atoms={len(prot)} ligand atoms={len(lig)}", flush=True)
    P = np.array([(x, y, z) for _, x, y, z, _c, _ri in prot], dtype=float)
    res_idx = np.array([ri for *_r, ri in prot])
    worst_pp = None
    try:
        from scipy.spatial import cKDTree
        tree = cKDTree(P)
        d, nn = tree.query(P, k=2)
        best = []
        for i in range(len(P)):
            j = int(nn[i, 1]); dist = float(d[i, 1])
            if res_idx[i] == res_idx[j]:      # skip intra-residue (legit bonds)
                continue
            best.append((dist, i, j))
        best.sort()
        print(f"  [clash] closest protein-protein (inter-residue) non-bonded pairs:", flush=True)
        seen = set()
        shown = 0
        for dist, i, j in best:
            key = (min(i, j), max(i, j))
            if key in seen:
                continue
            seen.add(key)
            print(f"    d={dist:.3f} A  {prot[i][0]}  <->  {prot[j][0]}", flush=True)
            shown += 1
            if shown >= 8:
                break
        worst_pp = best[0][0] if best else None
    except Exception as e:  # noqa: BLE001
        print(f"  [clash] protein-protein KDTree skipped: {type(e).__name__}: {e}", flush=True)
    worst_pl = None
    if lig:
        L = np.array([(x, y, z) for _, x, y, z in lig], dtype=float)
        # full cross distance (small: |lig| ~110 x |prot| ~7000)
        dmat = np.sqrt(((L[:, None, :] - P[None, :, :]) ** 2).sum(-1))
        flat = np.argsort(dmat, axis=None)[:8]
        print(f"  [clash] closest protein<->ligand pairs:", flush=True)
        for f in flat:
            li, pi = np.unravel_index(f, dmat.shape)
            print(f"    d={dmat[li, pi]:.3f} A  {lig[li][0]}  <->  {prot[pi][0]}", flush=True)
        worst_pl = float(dmat.min())
    print(f"  [clash] SUMMARY worst_protein_protein={worst_pp} A  worst_protein_ligand={worst_pl} A", flush=True)
    return worst_pp, worst_pl


def main() -> int:
    ok = True
    for leg in LEGS:
        print(f"\n=== stage_leg({leg}, {TEMPLATE}) ===", flush=True)
        man = stg.stage_leg(leg, TEMPLATE, OUT)
        print(json.dumps({k: v for k, v in man.items() if k != "smarca2_model"}, indent=2), flush=True)
        d = man["out_dir"]
        for f in (["ligands.sdf"] + (["complex.pdb"] if man["wrote_complex_pdb"] else [])):
            p = os.path.join(d, f)
            sz = os.path.getsize(p) if os.path.exists(p) else 0
            print(f"  {leg}/{f}: {sz} B", flush=True)
            ok = ok and sz > 0
        # staging_manifest.json must exist for every leg
        smp = os.path.join(d, "staging_manifest.json")
        if not os.path.exists(smp):
            print(f"  MISSING staging_manifest.json for {leg}", flush=True)
            ok = False
        if leg.endswith("ternary_vhl"):
            smm = man.get("smarca2_model", {})
            print(f"  [ternary] substituted={smm.get('smarca4_to_smarca2_substituted')} "
                  f"n_models={smm.get('n_relaxed_models')} divergence_ok={smm.get('divergence_ok')} "
                  f"rmsd={smm.get('divergence_ca_rmsd_A')}", flush=True)
            ok = ok and smm.get("smarca4_to_smarca2_substituted") and smm.get("divergence_ok") \
                and (smm.get("n_relaxed_models") or 0) >= 2
            # ENDPOINT BUILD CHECK (rdkit-only, no openfe): the built cmpd1/cmpd4 poses must match the requested
            # SMILES — the bug the GPU-smoke gate caught (cmpd4's N->CH can't be done by bond-order repair).
            import nr4a3_ternary_fep as eng
            from rdkit import Chem
            legspec, _env = eng.leg_spec(leg)
            a, b, sa, sb = eng._morph_endpoints(legspec)
            sdf = os.path.join(d, "ligands.sdf")
            molA = eng._endpoint_pose(sdf, a, sa, sa, Chem)
            molB = eng._endpoint_pose(sdf, b, sb, sa, Chem)
            mA = eng._canon_smiles(molA, Chem) == eng._canon_smiles(sa, Chem)
            mB = eng._canon_smiles(molB, Chem) == eng._canon_smiles(sb, Chem)
            print(f"  [ternary] endpoint build: A(cmpd1) match={mA}  B(cmpd4) match={mB}", flush=True)
            ok = ok and mA and mB
            # DECISIVE H-FIX CHECK ($0, CPU): parameterize the assembled complex.pdb with the SAME amber14 protein
            # forcefield OpenFE's HybridTopologySetupUnit uses. This is the exact operation that raised
            # 'No template found for residue 0 (MET) ... missing 9 H atoms' on the GPU seed-0 leg. If createSystem
            # builds here, the hydrogenation fix is PROVEN without spending the scarce single GCP GPU on a smoke.
            ff_ok, ff_msg = _forcefield_check(os.path.join(d, "complex.pdb"))
            print(f"  [ternary] ForceField.createSystem on hydrogenated complex: ok={ff_ok} ({ff_msg})", flush=True)
            ok = ok and ff_ok
            # CLASH CHECK ($0, CPU): a warmup state-1 SimulationNaNError that survives 25000 min steps + 2fs +
            # 20 integration retries is a near-coincident atom pair in the STARTING structure, not a compute
            # problem (valB seed-0, 2026-07-18). Name the offending residues so the fix targets the real defect.
            try:
                wpp, wpl = _clash_check(os.path.join(d, "complex.pdb"), os.path.join(d, "ligands.sdf"))
            except Exception as e:  # noqa: BLE001
                print(f"  [ternary] clash check errored (non-fatal): {type(e).__name__}: {e}", flush=True)
    print(f"\n[stage-validate] {'PASS' if ok else 'FAIL'}", flush=True)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
