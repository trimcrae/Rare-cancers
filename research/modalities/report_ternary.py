#!/usr/bin/env python3
"""Read-only report on the Boltz-2 ternary outputs in S3 (s3://<bucket>/<prefix>/).

Two kinds of answer:
  (1) CONTROL — did Boltz-2 recover the known CRBN + lenalidomide geometry (glutarimide seating in CRBN's
      tri-tryptophan pocket, W380/W386/W400)? This is the in-distribution sanity check.
  (2) TERNARIES — for each NR4A{3,1,2}-LBD + CRBN + PROTAC complex, a **degradation-geometry** read: does
      the PROTAC bridge both proteins, and does the NR4A LBD present a solvent-exposed lysine near CRBN
      (a geometric proxy for ubiquitin-transfer competence)? Compared across paralogues, this is the
      ternary contribution to *degradation* selectivity (paper §2.7) — the red-team F18 result.

Boltz models only NR4A-LBD + CRBN (not the full CRL4^CRBN + E2~Ub), so the Lys-near-CRBN distance is an
honest geometric PROXY for degradability, not a definitive call. Prints Boltz confidence + geometry per
complex. No AWS GPU; boto3 + gemmi only. Env: AWS creds, OUTPUT_PREFIX (default nr4a3-ternary),
TRITRP (default 380,386,400).
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
LYS_DIST_BINS = (8.0, 12.0, 16.0)   # Å; NR4A Lys NZ within these of CRBN = candidate ubiquitination site


def _download(prefix, dest):
    import boto3
    s3 = boto3.client("s3")
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


def _confidence_for(root, stem):
    """Print Boltz confidence JSON(s) whose path contains `stem`."""
    conf = [c for c in sorted(glob.glob(os.path.join(root, "**", "confidence*.json"), recursive=True))
            if stem in c]
    if not conf:
        print("    (no confidence JSON found)")
        return
    for c in conf:
        try:
            d = json.load(open(c))
        except Exception as e:  # noqa
            print(f"    {os.path.basename(c)}: unreadable ({e})")
            continue
        keys = ("confidence_score", "ptm", "iptm", "ligand_iptm", "protein_iptm",
                "complex_plddt", "complex_iplddt")
        vals = {k: round(d[k], 4) for k in keys if k in d and isinstance(d[k], (int, float))}
        print(f"    confidence: {vals}")


def _first_model(root, stem):
    models = [m for m in sorted(glob.glob(os.path.join(root, "**", "*.cif"), recursive=True)) if stem in m] \
        or [m for m in sorted(glob.glob(os.path.join(root, "**", "*.pdb"), recursive=True)) if stem in m]
    ranked = [m for m in models if "model_0" in m or "rank_1" in m or "_0." in m] or models
    return ranked[0] if ranked else None


def _chains_ligand(model):
    """Return (protein_chains: {chain_name: [(resname, resnum, {atomname: pos})]}, ligand_atom_positions)."""
    prot, lig = {}, []
    for chain in model:
        residues = []
        for res in chain:
            if res.name in STANDARD_AA:
                atoms = {a.name: a.pos for a in res if a.element.name != "H"}
                residues.append((res.name, res.seqid.num, atoms))
            else:
                for a in res:
                    if a.element.name != "H":
                        lig.append(a.pos)
        if residues:
            prot[chain.name] = residues
    return prot, lig


def _min_dist(a_positions, b_positions):
    if not a_positions or not b_positions:
        return None
    return min(pa.dist(pb) for pa in a_positions for pb in b_positions)


def tritrp_check(model):
    """Control geometry: ligand closest approach to the CRBN tri-Trp cluster."""
    prot, lig = _chains_ligand(model)
    trp = {}
    for residues in prot.values():
        for name, num, atoms in residues:
            if name == "TRP" and num in TRI_TRP:
                trp[num] = list(atoms.values())
    if not lig:
        print("    (no ligand atoms found)"); return
    if not trp:
        print(f"    (no tri-Trp {TRI_TRP} residues found — check numbering)"); return
    alld = []
    for num, atoms in sorted(trp.items()):
        d = _min_dist(lig, atoms)
        alld.append(d)
        print(f"    ligand <-> W{num}: {d:.2f} A")
    overall = min(alld)
    n8 = sum(1 for d in alld if d <= 8.0)
    verdict = ("SEATED in the tri-Trp pocket" if overall <= 5.0 and n8 >= 2
               else "NEAR the tri-Trp pocket" if overall <= 8.0 else "NOT near the tri-Trp pocket")
    print(f"    -> closest {overall:.2f} A; {n8}/{len(alld)} Trp within 8 A -> **{verdict}**")


def degradation_geometry(model):
    """NR4A ternary read: PROTAC bridging + closest exposed NR4A Lys to CRBN (ubiquitination proxy).
    Assigns the SMALLER protein chain as the NR4A LBD (~254 aa) and the larger as CRBN (~442 aa)."""
    prot, lig = _chains_ligand(model)
    if len(prot) < 2:
        print(f"    (expected 2 protein chains, found {len(prot)}) — cannot assign NR4A/CRBN"); return None
    by_size = sorted(prot.items(), key=lambda kv: len(kv[1]))
    nr4a_name, nr4a = by_size[0]
    crbn_name, crbn = by_size[-1]
    nr4a_atoms = [p for _, _, atoms in nr4a for p in atoms.values()]
    crbn_atoms = [p for _, _, atoms in crbn for p in atoms.values()]
    print(f"    chains: NR4A-LBD='{nr4a_name}' ({len(nr4a)} res), CRBN='{crbn_name}' ({len(crbn)} res)")

    # (a) PROTAC bridging
    d_nr4a = _min_dist(lig, nr4a_atoms)
    d_crbn = _min_dist(lig, crbn_atoms)
    bridges = d_nr4a is not None and d_crbn is not None and d_nr4a <= 4.5 and d_crbn <= 4.5
    print(f"    PROTAC bridging: <->NR4A {d_nr4a:.2f} A, <->CRBN {d_crbn:.2f} A "
          f"-> {'BRIDGES both' if bridges else 'does NOT bridge both (<=4.5 A each)'}")

    # (b) closest exposed NR4A Lys NZ to CRBN (ubiquitination-site proxy)
    lys = [(num, atoms["NZ"]) for name, num, atoms in nr4a if name == "LYS" and "NZ" in atoms]
    if not lys:
        print("    (no lysines resolved on the NR4A chain)")
        return {"nr4a_chain": nr4a_name, "crbn_chain": crbn_name, "bridges": bridges,
                "lig_to_nr4a": d_nr4a, "lig_to_crbn": d_crbn, "closest_lys": None}
    lys_d = sorted(((num, _min_dist([nz], crbn_atoms)) for num, nz in lys), key=lambda t: t[1])
    closest_num, closest_d = lys_d[0]
    counts = {b: sum(1 for _, d in lys_d if d <= b) for b in LYS_DIST_BINS}
    print(f"    NR4A lysines: {len(lys)}; closest Lys NZ -> CRBN = K{closest_num} at {closest_d:.2f} A")
    print(f"    NR4A Lys NZ within CRBN {LYS_DIST_BINS} A: "
          + ", ".join(f"{b:g}A:{counts[b]}" for b in LYS_DIST_BINS))
    verdict = ("productive-geometry proxy MET (bridged + Lys within 16 A of CRBN)"
               if bridges and closest_d <= 16.0 else
               "partial (bridged, no Lys within 16 A)" if bridges else "not bridged")
    print(f"    -> {verdict}")
    return {"nr4a_chain": nr4a_name, "crbn_chain": crbn_name, "bridges": bridges,
            "lig_to_nr4a": d_nr4a, "lig_to_crbn": d_crbn,
            "closest_lys": closest_num, "closest_lys_dist": closest_d, "lys_counts": counts,
            "verdict": verdict}


def main():
    if not os.environ.get("AWS_ACCESS_KEY_ID"):
        sys.exit("AWS creds required")
    try:
        import gemmi
    except ImportError:
        sys.exit("pip install gemmi")
    prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-ternary")
    with tempfile.TemporaryDirectory() as tmp:
        if not _download(prefix, tmp):
            sys.exit(f"nothing under s3 prefix {prefix}")
        prep = glob.glob(os.path.join(tmp, "**", "nr4a3-ternary-prep.json"), recursive=True)
        if prep:
            print("\n=== prep ===")
            print(json.dumps(json.load(open(prep[0])).get("targets", {}), indent=2))

        # control
        print("\n=== CONTROL: CRBN + lenalidomide (tri-Trp) ===")
        cm = _first_model(tmp, "nr4a3-ternary-control")
        if cm:
            print(f"  model: {os.path.relpath(cm, tmp)}")
            _confidence_for(tmp, "nr4a3-ternary-control")
            tritrp_check(gemmi.read_structure(cm)[0])
        else:
            print("  (no control model found)")

        # ternaries
        summary = {}
        for name in ("nr4a3", "nr4a1", "nr4a2"):
            stem = f"{name}-ternary-protac"
            print(f"\n=== TERNARY: {name.upper()}-LBD + CRBN + PROTAC ===")
            m = _first_model(tmp, stem)
            if not m:
                print("  (no model found — not run?)"); continue
            print(f"  model: {os.path.relpath(m, tmp)}")
            _confidence_for(tmp, stem)
            summary[name] = degradation_geometry(gemmi.read_structure(m)[0])

        if summary:
            print("\n=== degradation-geometry summary (closest NR4A Lys NZ -> CRBN) ===")
            for name, s in summary.items():
                if s and s.get("closest_lys_dist") is not None:
                    print(f"  {name.upper()}: K{s['closest_lys']} @ {s['closest_lys_dist']:.2f} A, "
                          f"bridges={s['bridges']}")


if __name__ == "__main__":
    main()
