#!/usr/bin/env python3
"""CPU validation driver for smarca2_model.build_smarca2_model on the real Wurz 8G1Q template.

Resolves the SMARCA4 (TARGET_BD) chain of 8G1Q from RCSB, downloads the structure, builds >=2 relaxed
SMARCA4->SMARCA2 models, and asserts the reviewer's item-4 conditions (substituted, >=2 models, divergence_ok).
Fast to iterate on a CPU runner (no GPU); the GPU ternary smoke reuses the SAME smarca2_model code path.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import smarca2_model as sm          # noqa: E402
import ternary_pdb_stage as stg     # noqa: E402

PDB = os.environ.get("VALIDATE_PDB", "8G1Q")
OUT = os.environ.get("VALIDATE_OUT", "/tmp/smarca2_model")


def main() -> int:
    r2c = stg.role_to_chains(PDB)
    acc = r2c.get("_target_acc")
    chains = r2c.get("TARGET_BD") or []
    print(f"[validate] {PDB} target acc={acc} ({stg.TARGET_ACC_NAME.get(acc)}) TARGET_BD chains={chains}", flush=True)
    if not chains:
        print("[validate] no TARGET_BD chain resolved — abort", flush=True)
        return 2
    chain = chains[0]

    import gemmi
    cif = stg._get(stg.RCSB_CIF.format(pdb=PDB), as_json=False)
    st = gemmi.make_structure_from_block(gemmi.cif.read_string(cif).sole_block())
    st.setup_entities()
    src_pdb = os.path.join(OUT, f"{PDB}_full.pdb")
    os.makedirs(OUT, exist_ok=True)
    st.write_pdb(src_pdb)
    print(f"[validate] wrote {src_pdb}; building SMARCA2 model from chain {chain}", flush=True)

    man = sm.build_smarca2_model(src_pdb, chain, OUT, n_models=int(os.environ.get("N_MODELS", "2")))
    print(json.dumps(man, indent=2), flush=True)
    ok = bool(man.get("ok") and man.get("smarca4_to_smarca2_substituted")
              and (man.get("n_relaxed_models") or 0) >= 2 and man.get("divergence_ok"))
    print(f"[validate] item-4 gate: {'PASS' if ok else 'FAIL'}", flush=True)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
