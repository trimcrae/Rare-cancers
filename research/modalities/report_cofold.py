#!/usr/bin/env python3
"""Read-only report on the EWSR1::NR4A3 fusion-junction apo co-fold outputs in S3.

The single question: do the two fused halves FOLD TOGETHER into an ordered interface (a composite pocket
present in neither parent), or does the predictor leave them as independent domains joined by a floppy
linker? For each construct (`seam`, `composite`) it reads the Boltz-2 model + PAE and reports, per the
EWS block vs the NR4A3 block (split at the prep JSON's block_boundary):
  - per-block mean pLDDT (is the NR4A3 core folded? is the EWS side disordered, as expected?),
  - mean INTER-block PAE (low ⇒ the model is confident about their relative position ⇒ folded together;
    high ⇒ independent/floppy — the expected negative),
  - inter-block heavy-atom contacts (do the halves even touch, and is the contact patch ordered?),
  - a verdict on whether a composite fusion-junction interface is predicted.

Boltz apo prediction on a de-novo junction has no cross-seam coevolution, so a "no co-fold" read is
EXPECTED and is a feasibility result, not proof no pocket can form (see fusion_cofold.py header). No GPU;
boto3 + gemmi + numpy only. Env: AWS creds, OUTPUT_PREFIX (default fusion-cofold).
"""
import glob
import json
import os
import sys
import tempfile

STANDARD_AA = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
    "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
}
CONTACT_CUTOFF = 5.0        # Å; heavy-atom cross-block distance counting as a contact
PAE_COUPLED = 12.0          # Å; mean inter-block PAE below this ⇒ predicted rigid relative placement
PLDDT_ORDERED = 70.0        # 0-100; interface residues above this are confidently placed
MIN_IFACE_RES = 8           # ordered contact patch size to call a real interface


def _download(prefix, dest):
    import boto3
    s3 = boto3.client("s3")
    bucket = f"sagemaker-{os.environ.get('AWS_DEFAULT_REGION', 'us-east-2')}-" \
             f"{boto3.client('sts').get_caller_identity()['Account']}"
    n = 0
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            local = os.path.join(dest, key[len(prefix):].lstrip("/"))
            os.makedirs(os.path.dirname(local), exist_ok=True)
            s3.download_file(bucket, key, local)
            n += 1
    print(f"downloaded {n} objects from s3://{bucket}/{prefix}", flush=True)
    return n


def _first_model(root, stem):
    cifs = [m for m in sorted(glob.glob(os.path.join(root, "**", "*.cif"), recursive=True))
            if f"{stem}_model_0" in os.path.basename(m) or (stem in m and "model_0" in m)]
    cifs = cifs or [m for m in sorted(glob.glob(os.path.join(root, "**", "*.cif"), recursive=True))
                    if stem in m]
    return cifs[0] if cifs else None


def _pae(root, stem):
    import numpy as np
    hits = [p for p in glob.glob(os.path.join(root, "**", "*.npz"), recursive=True)
            if "pae" in os.path.basename(p).lower() and stem in p]
    if not hits:
        return None
    d = np.load(hits[0])
    return d[d.files[0]]


def _residues(model):
    """Chain-order list of (resname, {atom: gemmi.Position}) heavy atoms, standard AA only."""
    res = []
    for chain in model:
        for r in chain:
            if r.name in STANDARD_AA:
                res.append((r.name, {a.name: a.pos for a in r if a.element.name != "H"}))
    return res


def analyse(model, pae, boundary):
    """boundary = number of leading (EWS) residues; the rest are the NR4A3 block."""
    import numpy as np
    # per-residue pLDDT from CA B-factors
    plddt = []
    ca_present = []
    for chain in model:
        for r in chain:
            if r.name in STANDARD_AA:
                ca = next((a for a in r if a.name == "CA"), None)
                plddt.append(ca.b_iso if ca else float("nan"))
                ca_present.append(ca is not None)
    plddt = np.array(plddt, dtype=float)
    scale = 100.0 if np.nanmax(plddt) <= 1.5 else 1.0       # normalise 0-1 → 0-100 if needed
    plddt = plddt * scale
    n = len(plddt)
    ews = slice(0, boundary)
    core = slice(boundary, n)
    res = _residues(model)

    # inter-block contacts (ordered patch)
    ews_res, core_res = res[ews], res[core]
    c2 = CONTACT_CUTOFF * CONTACT_CUTOFF
    iface_ews = []
    for i, (_rn, atoms) in enumerate(ews_res):
        touch = False
        for pa in atoms.values():
            for _rn2, atoms2 in core_res:
                for pb in atoms2.values():
                    dx, dy, dz = pa.x - pb.x, pa.y - pb.y, pa.z - pb.z
                    if dx * dx + dy * dy + dz * dz <= c2:
                        touch = True
                        break
                if touch:
                    break
            if touch:
                break
        if touch:
            iface_ews.append(i)
    iface_plddt = float(np.nanmean([plddt[i] for i in iface_ews])) if iface_ews else float("nan")

    # inter-block PAE
    inter_pae = None
    if pae is not None and pae.shape[0] == n and pae.shape[1] == n:
        block = np.concatenate([pae[ews, core].ravel(), pae[core, ews].ravel()])
        inter_pae = float(np.nanmean(block))

    ordered_iface = (len(iface_ews) >= MIN_IFACE_RES and iface_plddt >= PLDDT_ORDERED)
    coupled = inter_pae is not None and inter_pae < PAE_COUPLED
    folds_together = ordered_iface and (coupled if inter_pae is not None else True)
    verdict = ("COMPOSITE INTERFACE PREDICTED — halves fold together (ordered contact patch + confident "
               "relative placement); fpocket the interface next"
               if folds_together else
               "NO CO-FOLD — halves are independent/floppy (small or low-confidence contact patch"
               + (f", inter-block PAE {inter_pae:.1f} Å high" if inter_pae is not None else "")
               + "); no composite junction pocket at this construct")
    return {
        "n_residues": n,
        "ews_block_plddt": round(float(np.nanmean(plddt[ews])), 1),
        "nr4a3_block_plddt": round(float(np.nanmean(plddt[core])), 1),
        "inter_block_pae": round(inter_pae, 2) if inter_pae is not None else None,
        "n_interface_ews_residues": len(iface_ews),
        "interface_plddt": round(iface_plddt, 1) if iface_ews else None,
        "folds_together": folds_together,
        "verdict": verdict,
    }


def main():
    if not os.environ.get("AWS_ACCESS_KEY_ID"):
        sys.exit("AWS creds required")
    try:
        import gemmi  # noqa
        import numpy  # noqa
    except ImportError:
        sys.exit("pip install gemmi numpy")
    import gemmi
    prefix = os.environ.get("OUTPUT_PREFIX", "fusion-cofold")
    with tempfile.TemporaryDirectory() as tmp:
        if not _download(prefix, tmp):
            sys.exit(f"nothing under s3 prefix {prefix}")
        prep_files = glob.glob(os.path.join(tmp, "**", "fusion-cofold-prep.json"), recursive=True)
        prep = json.load(open(prep_files[0])) if prep_files else {"constructs": {}}
        print("\n=== prep ===")
        print(json.dumps(prep.get("constructs", {}), indent=2))

        result = {"breakpoint": prep.get("breakpoint"), "constructs": {}}
        for name, meta in prep.get("constructs", {}).items():
            print(f"\n=== CONSTRUCT: {name} ({meta.get('hypothesis', '')}) ===")
            m = _first_model(tmp, name)
            if not m:
                print("  (no model found — not run?)")
                continue
            print(f"  model: {os.path.relpath(m, tmp)}")
            model = gemmi.read_structure(m)[0]
            boundary = meta.get("block_boundary")
            r = analyse(model, _pae(tmp, name), boundary)
            result["constructs"][name] = r
            print(f"  EWS block pLDDT {r['ews_block_plddt']} | NR4A3 block pLDDT {r['nr4a3_block_plddt']} "
                  f"| inter-block PAE {r['inter_block_pae']} Å")
            print(f"  ordered EWS↔NR4A3 contacts: {r['n_interface_ews_residues']} EWS residues "
                  f"(mean pLDDT {r['interface_plddt']})")
            print(f"  → {r['verdict']}")

        print("\n=== RESULT JSON (copy to fusion-cofold-result.json) ===")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
