#!/usr/bin/env python3
"""
FREE CPU validation of the FULL system build on a REAL co-fold — no MD, no GPU, no Vast spend.

WHY: every panel leg was crashing in build_system at addSolvent because the co-fold complex.pdb has heavy atoms
only (no hydrogens) and the driver never called addHydrogens. A vacuum env-smoke and the assembler test both
MISS this — only building the real solvated protein+ligand system exercises addHydrogens -> addSolvent ->
createSystem -> covalent-restraint indexing. This script does exactly that on CPU so the class of bug is caught
for $0 before any GPU fan-out. Runs on the nrv04_build_smoke CI task (MD env + AWS creds).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _pull_cofold(bucket, base, system, dest):
    import boto3
    from nrv04_vast_launch import _s3_list
    s3 = boto3.client("s3")
    cifs = _s3_list(s3, bucket, f"{base}/{system}/", suffix="_model_0.cif")
    if not cifs:
        raise SystemExit(f"[build-smoke] no co-fold CIF under {base}/{system}/")
    key = sorted(cifs)[0]
    os.makedirs(dest, exist_ok=True)
    out = os.path.join(dest, "model_0.cif")
    s3.download_file(bucket, key, out)
    print(f"[build-smoke] pulled {key}", flush=True)
    return out


def main():
    from nrv04_covalent_assemble import assemble_leg
    from nrv04_covalent_panel import leg_by_id
    from nrv04_ligands import LIGANDS
    from nrv04_covalent_md import build_system

    bucket = os.environ["VAST_CKPT_BUCKET"]
    base = os.environ.get("NRV04_COFOLD_PREFIX", "nrv04-descriptive-v3").rstrip("/")

    # Two representative legs: cov_nr4a1 (covalent restraint + nr4a1 co-fold) and cov_c551a (C551A mutation path).
    for leg_id, system in [("cov_nr4a1", "nr4a1"), ("cov_c551a", "nr4a1")]:
        leg = leg_by_id(leg_id)
        cif = _pull_cofold(bucket, base, system, f"/tmp/cofold_{leg_id}")
        res = assemble_leg(cif, leg, LIGANDS[leg.ligand], f"/tmp/stage_{leg_id}")
        cpdb = os.path.join(res["out"], "complex.pdb")
        lsdf = os.path.join(res["out"], "ligand.sdf")
        sim, topo, meta = build_system(cpdb, lsdf, leg.covalent,
                                       env_or("COV_LIG_ATOM", "C6"), 551, leg.mutation)
        n = meta["n_atoms"]
        print(f"[build-smoke] {leg_id}: heavy={meta.get('protein_heavy_atoms')} "
              f"after_addH={meta.get('after_addH')} solvated_total={n} covalent_pair={meta.get('covalent_pair')}",
              flush=True)
        if n < 5000:
            raise SystemExit(f"[build-smoke] {leg_id} solvated system implausibly small ({n} atoms)")
        if leg.covalent and "covalent_pair" not in meta:
            raise SystemExit(f"[build-smoke] {leg_id} covalent but no covalent_pair in meta")
    print("BUILD-SMOKE PASS — full solvated system builds from the real co-fold (addHydrogens + addSolvent + "
          "createSystem + covalent restraint).", flush=True)


def env_or(k, d):
    return os.environ.get(k, d)


if __name__ == "__main__":
    sys.exit(main())
