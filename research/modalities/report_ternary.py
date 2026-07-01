#!/usr/bin/env python3
"""Read-only report on the Boltz-2 ternary control output in S3 (s3://<bucket>/<prefix>/).

Answers the control's scientific question: did Boltz-2 recover the known CRBN + lenalidomide geometry
(the glutarimide seating in CRBN's tri-tryptophan pocket, W380/W386/W400)? Prints (1) Boltz confidence
scores and (2) a geometry check — the ligand's closest approach to the tri-Trp cluster. No AWS GPU;
boto3 + gemmi only. Env: AWS creds, OUTPUT_PREFIX (default nr4a3-ternary), TRITRP (default 380,386,400).
"""
import glob
import json
import os
import sys
import tempfile

TRI_TRP = [int(x) for x in os.environ.get("TRITRP", "380,386,400").split(",")]
STANDARD_AA = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
    "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
}


def _download(prefix, dest):
    import boto3
    s3 = boto3.client("s3")
    # default SageMaker bucket for the account/region: sagemaker-<region>-<account-id>
    sess_bucket = f"sagemaker-{os.environ.get('AWS_DEFAULT_REGION', 'us-east-2')}-" \
                  f"{boto3.client('sts').get_caller_identity()['Account']}"
    n = 0
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=sess_bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            local = os.path.join(dest, key[len(prefix):].lstrip("/"))
            os.makedirs(os.path.dirname(local), exist_ok=True)
            s3.download_file(sess_bucket, key, local)
            n += 1
    print(f"downloaded {n} objects from s3://{sess_bucket}/{prefix}", flush=True)
    return n


def _report_confidence(root):
    conf = sorted(glob.glob(os.path.join(root, "**", "confidence*.json"), recursive=True))
    if not conf:
        print("  (no confidence JSON found)")
        return
    for c in conf:
        try:
            d = json.load(open(c))
        except Exception as e:  # noqa
            print(f"  {os.path.basename(c)}: unreadable ({e})")
            continue
        keys = ("confidence_score", "ptm", "iptm", "ligand_iptm", "protein_iptm",
                "complex_plddt", "complex_iplddt", "complex_pde", "complex_ipde")
        vals = {k: round(d[k], 4) for k in keys if k in d and isinstance(d[k], (int, float))}
        print(f"  {os.path.basename(c)}: {vals}")


def _geometry_check(root):
    try:
        import gemmi
    except ImportError:
        print("  (gemmi not installed — skipping geometry check)")
        return
    models = sorted(glob.glob(os.path.join(root, "**", "*.cif"), recursive=True)) or \
        sorted(glob.glob(os.path.join(root, "**", "*.pdb"), recursive=True))
    models = [m for m in models if "model_0" in m or "rank_1" in m or "_0." in m] or models
    if not models:
        print("  (no CIF/PDB model found)")
        return
    path = models[0]
    print(f"  model: {os.path.relpath(path, root)}")
    st = gemmi.read_structure(path)
    model = st[0]
    lig_atoms, trp = [], {}
    for chain in model:
        for res in chain:
            if res.name not in STANDARD_AA:               # non-polymer = the ligand
                for a in res:
                    if a.element.name != "H":
                        lig_atoms.append(a.pos)
            elif res.seqid.num in TRI_TRP and res.name == "TRP":
                trp[res.seqid.num] = [a.pos for a in res if a.element.name != "H"]
    if not lig_atoms:
        print("  (no ligand/non-polymer atoms found in the model)")
        return
    print(f"  ligand heavy atoms: {len(lig_atoms)}; tri-Trp residues resolved: "
          f"{sorted(trp)} (expected {TRI_TRP})")
    if not trp:
        print("  (none of the expected tri-Trp residues found at those indices — check numbering)")
        return
    # min ligand-atom → any-tri-Trp-atom distance, and per-Trp closest approach
    alld = []
    for num, atoms in sorted(trp.items()):
        dmin = min(la.dist(ta) for la in lig_atoms for ta in atoms)
        alld.append(dmin)
        print(f"    ligand ↔ W{num}: closest heavy-atom {dmin:.2f} Å")
    overall = min(alld)
    n_within8 = sum(1 for d in alld if d <= 8.0)
    verdict = ("SEATED in/at the tri-Trp pocket" if overall <= 5.0 and n_within8 >= 2
               else "NEAR the tri-Trp pocket" if overall <= 8.0
               else "NOT near the expected tri-Trp pocket")
    print(f"  → closest approach {overall:.2f} Å; {n_within8}/{len(alld)} Trp within 8 Å → **{verdict}**")


def main():
    if not os.environ.get("AWS_ACCESS_KEY_ID"):
        sys.exit("AWS creds required")
    prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-ternary")
    with tempfile.TemporaryDirectory() as tmp:
        if not _download(prefix, tmp):
            sys.exit(f"nothing under s3 prefix {prefix}")
        print("\n=== Boltz confidence ===")
        _report_confidence(tmp)
        print("\n=== geometry check (lenalidomide ↔ CRBN tri-Trp) ===")
        _geometry_check(tmp)


if __name__ == "__main__":
    main()
