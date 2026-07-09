#!/usr/bin/env python3
"""Prepare the off-target / anti-target selectivity panel receptors (survivor-INDEPENDENT; run once).

For each target in antitarget_panel.json: fetch the RCSB PDB, isolate the chain that carries the reference
ligand, write a clean receptor PDB (protein ATOM records only — smina reads a plain PDB, as the NR4A dock
does), and define the docking-box CENTER as the centroid of that reference ligand (the orthosteric site) or,
if `box_residues` is given instead, the CA centroid of those residues. Upload each receptor PDB + a manifest
(name -> center) to s3://<bucket>/<OUTPUT_PREFIX>/ so the panel dock reads them exactly like the NR4A dock
reads its release receptors. Pure-stdlib PDB parsing (no rdkit/smina) so it runs on a plain GitHub runner.

A target whose ligand/chain cannot be resolved is DROPPED with a logged warning (never silently emitted as a
bad receptor) — refine its pdb_id/ligand_resname in the panel JSON and re-run.

Env: BUCKET (opt), OUTPUT_PREFIX (default nr4a3-antitarget-panel), AWS creds + AWS_DEFAULT_REGION.
"""
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STD_AA = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU", "LYS", "MET",
          "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "MSE", "SEC", "PYL"}


def _fetch(pdb_id):
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    with urllib.request.urlopen(url, timeout=60) as r:  # noqa: S310 (trusted RCSB host)
        return r.read().decode("utf-8", "replace").splitlines()


def _prep_target(t):
    """Return (receptor_pdb_text, center_xyz, n_res) or raise with a reason."""
    lines = _fetch(t["pdb_id"])
    lig = t.get("ligand_resname")
    box_res = t.get("box_residues")

    # locate the ligand copy (resname `lig`) and its chain -> that chain is the receptor we dock into.
    lig_atoms, lig_chain = [], None
    if lig:
        for ln in lines:
            if ln.startswith("HETATM") and ln[17:20].strip() == lig.strip():
                ch = ln[21]
                if lig_chain is None:
                    lig_chain = ch
                if ch == lig_chain:
                    lig_atoms.append((float(ln[30:38]), float(ln[38:46]), float(ln[46:54])))
        if not lig_atoms:
            raise RuntimeError(f"ligand {lig} not found in {t['pdb_id']}")
    chain = lig_chain if lig_chain is not None else t.get("chain", "A")

    # clean receptor: standard-aa ATOM records of the chosen chain, altloc blank/A, drop hydrogens.
    rec, seen = [], set()
    for ln in lines:
        if not ln.startswith("ATOM"):
            continue
        if ln[21] != chain:
            continue
        if ln[17:20].strip() not in STD_AA:
            continue
        if ln[16] not in (" ", "A"):            # altloc: keep the primary conformer
            continue
        if ln[76:78].strip() == "H" or ln[12:16].strip().startswith("H"):
            continue
        rec.append(ln)
        seen.add(ln[22:27])                     # resSeq+iCode
    if len(seen) < 50:
        raise RuntimeError(f"only {len(seen)} residues on chain {chain} of {t['pdb_id']}")

    if lig_atoms:
        n = len(lig_atoms)
        center = (sum(a[0] for a in lig_atoms) / n, sum(a[1] for a in lig_atoms) / n,
                  sum(a[2] for a in lig_atoms) / n)
    elif box_res:
        want = {int(r) for r in box_res}
        xs = [(float(l[30:38]), float(l[38:46]), float(l[46:54]))
              for l in rec if l[12:16].strip() == "CA" and int(l[22:26]) in want]
        if not xs:
            raise RuntimeError(f"no box_residues CA found in {t['pdb_id']}")
        center = (sum(x[0] for x in xs) / len(xs), sum(x[1] for x in xs) / len(xs),
                  sum(x[2] for x in xs) / len(xs))
    else:
        raise RuntimeError("no ligand_resname or box_residues to center on")
    return "\n".join(rec) + "\n", [round(c, 3) for c in center], len(seen)


def main():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-antitarget-panel")

    spec = json.load(open(os.path.join(HERE, "antitarget_panel.json")))
    ok, manifest = [], {"box_size": spec.get("box_size", 24), "targets": []}
    for t in spec["targets"]:
        try:
            pdb_text, center, n_res = _prep_target(t)
        except Exception as e:  # noqa: BLE001
            print(f"DROP {t['name']:<8} ({t['pdb_id']}): {e}")
            continue
        key = f"{prefix}/{t['name']}.pdb"
        s3.put_object(Bucket=bucket, Key=key, Body=pdb_text.encode())
        manifest["targets"].append({"name": t["name"], "class": t.get("class"),
                                    "pdb_id": t["pdb_id"], "center": center, "n_res": n_res})
        ok.append(t["name"])
        print(f"OK   {t['name']:<8} ({t['pdb_id']}): {n_res} res, center {center} -> s3://{bucket}/{key}")
    s3.put_object(Bucket=bucket, Key=f"{prefix}/panel-manifest.json",
                  Body=json.dumps(manifest, indent=2).encode())
    print(f"\nprepared {len(ok)}/{len(spec['targets'])} panel targets: {ok}")
    print(f"manifest -> s3://{bucket}/{prefix}/panel-manifest.json")
    if len(ok) < len(spec["targets"]):
        print("NOTE: some targets dropped — fix their pdb_id/ligand_resname in antitarget_panel.json and re-run.")


if __name__ == "__main__":
    main()
