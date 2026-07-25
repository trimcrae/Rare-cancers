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
    # ⚠ default was `nrv04-descriptive-v3` until 2026-07-25. Those co-folds carry 14-3-3 epsilon where Elongin B
    # belongs (2026-07-24 audit), so the smoke's default input was a contaminated assembly. identify_chains now
    # rejects it, but a default that is known-wrong is a trap, not a safety net.
    base = os.environ.get("NRV04_COFOLD_PREFIX", "nrv04-covalent-cofold").rstrip("/")

    # ⚠ CHANGED 2026-07-25 (Lane 8). `cov_nr4a1` can no longer BUILD, and that is the correct outcome, not a
    # regression: the covalent site is now IDENTIFIED as the preregistered C551 rather than taken as the nearest
    # target-chain cysteine, and on every co-fold in the bucket C551 is 28.4-39.1 A from the electrophile — far
    # beyond MAX_COVALENT_TETHER_A. Before the fix the smoke "passed" while silently building the restraint onto
    # **C566** at ~9 A. So the smoke now has two jobs:
    #   (a) prove the BUILD PLUMBING still works end-to-end (addHydrogens -> addSolvent -> createSystem), which
    #       the noncovalent legs exercise identically minus the restraint force; and
    #   (b) prove the A1 GATE FIRES on a covalent leg staged from an inadmissible co-fold.
    # A smoke that skipped (b) would go green again the moment the gate broke.
    for leg_id, system, expect in [("noncov_nr4a1", "nr4a1", "build"),
                                   ("cov_c551a", "nr4a1", "build"),
                                   ("cov_nr4a1", "nr4a1", "a1_gate_fires")]:
        leg = leg_by_id(leg_id)
        cif = _pull_cofold(bucket, base, system, f"/tmp/cofold_{leg_id}")
        res = assemble_leg(cif, leg, LIGANDS[leg.ligand], f"/tmp/stage_{leg_id}")
        cpdb = os.path.join(res["out"], "complex.pdb")
        lsdf = os.path.join(res["out"], "ligand.sdf")
        # Pass the IDENTIFIED target chain, so the covalent-site resolution is the production path's exactly.
        # Without it the driver falls back to the geometric search this smoke exists to keep retired.
        args = (cpdb, lsdf, leg.covalent, env_or("COV_LIG_ATOM", "C6"), 551, leg.mutation)
        kwargs = {"target_chain": res["chains"]["target_chain"]}

        if expect == "a1_gate_fires":
            try:
                build_system(*args, **kwargs)
            except SystemExit as e:
                msg = str(e)
                if "preformed-adduct limit" not in msg:
                    raise SystemExit(f"[build-smoke] {leg_id} failed, but NOT on the A1 gate: {msg}")
                print(f"[build-smoke] {leg_id}: A1 gate fired as required -> {msg}", flush=True)
                continue
            raise SystemExit(
                f"[build-smoke] {leg_id} BUILT a covalent system from a co-fold whose preregistered C551 Sg is "
                f"~28 A from the electrophile. The A1 gate did not fire — either the site resolution regressed to "
                f"'nearest cysteine' (which lands on C566 at ~9 A) or MAX_COVALENT_TETHER_A was raised. Both are "
                f"recorded deviations, not fixes.")

        sim, topo, meta = build_system(*args, **kwargs)
        n = meta["n_atoms"]
        print(f"[build-smoke] {leg_id}: heavy={meta.get('protein_heavy_atoms')} "
              f"after_addH={meta.get('after_addH')} solvated_total={n} covalent_pair={meta.get('covalent_pair')} "
              f"cys={meta.get('reactive_cys')}", flush=True)
        if n < 5000:
            raise SystemExit(f"[build-smoke] {leg_id} solvated system implausibly small ({n} atoms)")
        if leg.covalent and "covalent_pair" not in meta:
            raise SystemExit(f"[build-smoke] {leg_id} covalent but no covalent_pair in meta")
    print("BUILD-SMOKE PASS — the solvated system builds from the real co-fold (addHydrogens + addSolvent + "
          "createSystem), AND the A1 admissibility gate fires on the covalent leg.", flush=True)


def env_or(k, d):
    return os.environ.get(k, d)


if __name__ == "__main__":
    sys.exit(main())
