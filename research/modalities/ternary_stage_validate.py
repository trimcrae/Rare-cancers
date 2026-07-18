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
    print(f"\n[stage-validate] {'PASS' if ok else 'FAIL'}", flush=True)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
