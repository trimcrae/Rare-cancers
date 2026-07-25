#!/usr/bin/env python3
"""
NR-V04 covalent panel — PRE-SPEND staging check ($0 CPU, no GPU).

Before paying for a corrected re-run, answer on a free runner the three things that decide whether the run can
produce an interpretable result at all. Each is a real measurement on the real inputs, not a code review.

  1. Does every leg STAGE from the co-fold prefix the re-run would use — i.e. does identify_chains resolve the
     254-residue NR4A LBD as the degradation target, with VHL/EloB/EloC accounted for and no 14-3-3 contaminant?
  2. For each covalent leg, how far is the nearest TARGET-CHAIN Cys Sg from the warhead electrophile? The panel's
     `warhead_only` legs tethered celastrol to an Elongin C cysteine 12.44 A away because the co-fold never posed
     free celastrol in the NR4A1 pocket. That is an INPUT defect; no chain-split fix repairs it, and the driver
     now fails closed above MAX_COVALENT_TETHER_A. If it recurs on the clean co-fold, the leg is unrunnable and
     the prereg's control #3 cannot be evaluated — which must be known BEFORE the spend, not after.
  3. How large is the corrected E3<->target interface in the staged (unsolvated) complex, and — for the matched
     active/epimer pair — is it different at all? R2's frozen rule is "BSA > 0 sustained over > 50 % of frames",
     and every one of the 17 completed legs returned recruited=True, so this bounds what R2 could ever separate.

Exit code is 0 either way: this is a diagnostic that produces a verdict, not a gate that hides one.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nrv04_covalent_panel import PANEL  # noqa: E402
from nrv04_ligands import LIGANDS  # noqa: E402

# `nrv04_ternary.py` writes one co-fold system per ligand; the launcher maps panel ligand -> system subdir.
LIGAND_TO_SYSTEM = {"nrv04": "nr4a1", "nrv04_epimer": "neg_inactive", "celastrol": "neg_celastrol"}


def _pull_model(s3, bucket, prefix, system, dest):
    """Download the first `_model_0.cif` under <prefix>/<system>/ (the launcher's own selection rule)."""
    base = f"{prefix.rstrip('/')}/{system}/"
    keys, tok = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": base}
        if tok:
            kw["ContinuationToken"] = tok
        r = s3.list_objects_v2(**kw)
        keys += [o["Key"] for o in r.get("Contents", []) if o["Key"].endswith("_model_0.cif")]
        if not r.get("IsTruncated"):
            break
        tok = r["NextContinuationToken"]
    if not keys:
        raise FileNotFoundError(f"no _model_0.cif under s3://{bucket}/{base}")
    key = sorted(keys)[0]
    os.makedirs(dest, exist_ok=True)
    local = os.path.join(dest, "model_0.cif")
    s3.download_file(bucket, key, local)
    return key, local


def _interface_from_pdb(pdb_path, target_chain, e3_chains, cutoff_nm=0.45):
    """Heavy-atom contacts across the identified E3<->target interface in the STAGED complex (pre-solvation,
    pre-hydrogen). Same 0.45 nm cutoff the driver's R2 uses, so the magnitudes are comparable."""
    import numpy as np
    from scipy.spatial import cKDTree
    tg, e3 = [], []
    for line in open(pdb_path):
        if line[:6].strip() not in ("ATOM", "HETATM"):
            continue
        if line[76:78].strip() == "H" or line[12:16].strip().startswith("H"):
            continue
        xyz = (float(line[30:38]) / 10.0, float(line[38:46]) / 10.0, float(line[46:54]) / 10.0)
        (tg if line[21] == target_chain else e3 if line[21] in e3_chains else []).append(xyz)
    if not tg or not e3:
        return {"target_heavy": len(tg), "e3_heavy": len(e3), "contacts": 0}
    n = sum(len(p) for p in cKDTree(np.array(e3)).query_ball_tree(cKDTree(np.array(tg)), cutoff_nm))
    return {"target_heavy": len(tg), "e3_heavy": len(e3), "contacts": int(n)}


def check_leg(leg, cif, workdir):
    """Stage one leg and measure everything that decides whether it can be run."""
    from nrv04_covalent_assemble import assemble_leg
    from nrv04_covalent_md import MAX_COVALENT_TETHER_A, _reactive_cys_by_geometry
    out = {"leg_id": leg.leg_id, "ligand": leg.ligand, "covalent": leg.covalent, "mutation": leg.mutation}
    try:
        res = assemble_leg(cif, leg, LIGANDS[leg.ligand], workdir)
    except Exception as e:  # noqa: BLE001
        out["stage"] = "FAIL"
        out["error"] = f"{type(e).__name__}: {e}"
        return out
    ch = res["chains"]
    out["stage"] = "OK"
    out["chains"] = ch
    complex_pdb = os.path.join(res["out"], "complex.pdb")
    ligand_sdf = os.path.join(res["out"], "ligand.sdf")
    out["ligand_atoms"] = res["ligand_atoms"]

    # (2) the warhead question — target-chain-restricted, exactly as the fixed driver now does it
    try:
        c, r, d, diag = _reactive_cys_by_geometry(open(complex_pdb).read(), ligand_sdf, "C6",
                                                  target_chain=ch["target_chain"])
        out["reactive_cys"] = {"chain": c, "resid": r, "dist_A": round(d, 2), "diagnostics": diag}
        out["covalent_leg_runnable"] = (not leg.covalent) or d <= MAX_COVALENT_TETHER_A
        if leg.covalent and d > MAX_COVALENT_TETHER_A:
            out["blocker"] = (f"the nearest target-chain Cys Sg is {d:.2f} A from the warhead electrophile, "
                              f"beyond the {MAX_COVALENT_TETHER_A} A preformed-adduct limit — this co-fold did "
                              f"not pose the warhead in the NR4A1 pocket, so the covalent leg cannot be built "
                              f"from it")
    except SystemExit as e:
        out["reactive_cys"] = {"error": str(e)}
        out["covalent_leg_runnable"] = False
        out["blocker"] = str(e)

    # (3) the interface R2 would see
    out["interface_staged"] = _interface_from_pdb(complex_pdb, ch["target_chain"], set(ch["e3_chains"]))
    return out


def main(argv=None):
    import argparse
    import boto3
    ap = argparse.ArgumentParser(description="Free pre-spend staging check for the corrected NR-V04 panel.")
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET", ""))
    ap.add_argument("--cofold-prefix", default=os.environ.get("NRV04_COFOLD_PREFIX") or "nrv04-covalent-cofold")
    ap.add_argument("--out", default="research/modalities/nrv04-prespend-check.json")
    args = ap.parse_args(argv)
    if not args.bucket:
        raise SystemExit("set --bucket or $VAST_CKPT_BUCKET")

    s3 = boto3.client("s3")
    doc = {"bucket": args.bucket, "cofold_prefix": args.cofold_prefix, "legs": [], "cofold_models": {}}
    cache = {}
    for leg in PANEL:
        system = LIGAND_TO_SYSTEM[leg.ligand]
        if system not in cache:
            try:
                key, local = _pull_model(s3, args.bucket, args.cofold_prefix, system, f"/tmp/cf_{system}")
                cache[system] = local
                doc["cofold_models"][system] = key
            except Exception as e:  # noqa: BLE001
                cache[system] = None
                doc["cofold_models"][system] = f"ERROR {type(e).__name__}: {e}"
        if cache[system] is None:
            doc["legs"].append({"leg_id": leg.leg_id, "stage": "FAIL",
                                "error": doc["cofold_models"][system]})
            continue
        doc["legs"].append(check_leg(leg, cache[system], f"/tmp/stage_{leg.leg_id}"))

    staged = [l for l in doc["legs"] if l.get("stage") == "OK"]
    blocked = [l for l in doc["legs"] if l.get("blocker") or l.get("stage") != "OK"]
    doc["summary"] = {
        "n_legs": len(doc["legs"]), "n_staged": len(staged), "n_blocked": len(blocked),
        "blocked_legs": [{"leg_id": l["leg_id"], "why": l.get("blocker") or l.get("error")} for l in blocked],
        "all_legs_runnable": not blocked,
    }
    with open(args.out, "w") as f:
        json.dump(doc, f, indent=2)
    print(json.dumps(doc, indent=2), flush=True)
    print("\n=== PRE-SPEND SUMMARY ===", flush=True)
    for l in doc["legs"]:
        rc = l.get("reactive_cys") or {}
        print(f"  {l['leg_id']:18s} stage={l.get('stage'):5s} target="
              f"{(l.get('chains') or {}).get('target_chain')} "
              f"reactive_cys={rc.get('chain')}:{rc.get('resid')}@{rc.get('dist_A')}A "
              f"iface_contacts={(l.get('interface_staged') or {}).get('contacts')} "
              f"{'BLOCKED: ' + l['blocker'] if l.get('blocker') else ''}", flush=True)
    print(f"  all_legs_runnable = {doc['summary']['all_legs_runnable']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
