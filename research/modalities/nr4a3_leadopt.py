#!/usr/bin/env python3
"""
Scaffold-seeded LEAD-OPTIMISATION around denovo_401 (the program's best SELECTIVE orthosteric binder).

WHY. denovo_401 is selective (the hard part) but a weak absolute binder (ABFE ΔG ≈ −1.2). The prior de-novo
campaigns generated BLIND whole molecules ranked by drug-likeness "promise", never by binding, and never
optimised 401's own (already-selective) chemotype. This module does the missing med-chem move: KEEP 401's
scaffold and DECORATE its growth vectors — primarily the pendant phenyl ring (a classic subpocket-reaching
handle), plus a few terminal-arm variants — with a curated R-group set biased toward the divergent
selectivity handles (hydrophobic groups for L406/I484/L534; H-bonders for T410). The point is to GROW
affinity while preserving the selective core, then let dock + multi-snapshot MM-GBSA (the existing funnel)
say whether any variant beats 401.

WHAT. (1) Enumerate scaffold decorations of denovo_401 (mono-/di-substitution on the phenyl ring + terminal
swaps). (2) RDKit-profile each (reuse warhead_chem_profile.profile), developability-gate implicitly via the
promise score (reuse denovo_funnel.score_molecule, which hard-demotes structural-alert liabilities). (3) Emit
`nr4a3-denovo.json` in the EXACT schema the dock funnel consumes (nr4a3_matrix candidate mode →
denovo_library.top_developable_candidates), so the existing gpu-denovo-dock + mmgbsa pipelines run unchanged.
denovo_401 itself is included as candidate `ref_401` for a same-run, same-frame baseline.

Output (OUTPUT_DIR, default cwd): nr4a3-denovo.json (+ optional S3 upload to s3://<bucket>/<OUTPUT_PREFIX>/
when OUTPUT_PREFIX + AWS creds are set). Pure RDKit / CPU — runs in a GitHub Actions runner.
"""
import json
import os
import sys

REF_401 = "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1"   # denovo_401 (MW 304, selective, clean)

# Curated R-groups (attachment atom FIRST). Split by intent so the enumeration spans the handle chemistry:
#  - hydrophobic -> engage the divergent hydrophobic handles L406 / I484 / L534 (Leu/Ile)
#  - h_bond      -> engage the polar handle T410 (and add a PROTAC-compatible handle where useful)
HYDROPHOBIC = ["F", "Cl", "Br", "C", "CC", "C(C)C", "C1CC1", "C(F)(F)F", "C#N", "c1ccccc1"]
H_BOND = ["O", "OC", "N", "C(N)=O", "OCCO", "OCCN", "S(N)(=O)=O", "c1ccncc1", "C(=O)O", "NC(C)=O"]
RGROUPS = HYDROPHOBIC + H_BOND

# A few terminal-arm variants of 401 (swap/extend the methoxymethyl ether and the neopentyl-alcohol arm),
# to grow affinity along the other pocket direction. Full SMILES (kept scaffold, edited terminus).
TERMINAL_VARIANTS = {
    "term_OH":   "OC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1",            # OMe->OH
    "term_OEt":  "CCOC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1",          # OMe->OEt
    "term_amide":"O=C(N)C[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1",       # CH2OMe->CH2C(=O)NH2
    "term_diol": "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)(O)CO)C1",       # add CH2OH on the tert carbinol arm
    "term_Fol":  "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C(F)(F)F)O)C1",    # Me->CF3 on the carbinol
}


def _phenyl_ring(mol):
    """Return the atom indices of the first all-carbon aromatic 6-ring (401's pendant phenyl)."""
    for ring in mol.GetRingInfo().AtomRings():
        if len(ring) == 6 and all(mol.GetAtomWithIdx(i).GetIsAromatic()
                                  and mol.GetAtomWithIdx(i).GetSymbol() == "C" for i in ring):
            return list(ring)
    return []


def _attach(Chem, base, r_smiles, at_idx):
    """Attach r_smiles (via its atom 0) to base atom at_idx (an aromatic CH), consuming one H. Returns a
    canonical SMILES or None if it can't be built/sanitised."""
    if base.GetAtomWithIdx(at_idx).GetTotalNumHs() < 1:   # read H from the SANITISED base
        return None
    frag = Chem.MolFromSmiles(r_smiles)
    if frag is None:
        return None
    combo = Chem.RWMol(Chem.CombineMols(base, frag))
    combo.AddBond(at_idx, base.GetNumAtoms(), Chem.BondType.SINGLE)   # frag atom0 is at base.GetNumAtoms()
    a = combo.GetAtomWithIdx(at_idx)                      # aromatic CH -> 0 H after substitution
    a.SetNoImplicit(True)
    a.SetNumExplicitHs(0)
    try:
        m = combo.GetMol()
        Chem.SanitizeMol(m)
        return Chem.MolToSmiles(m)
    except Exception:  # noqa: BLE001
        return None


def enumerate_variants(Chem):
    """Yield (name, smiles) scaffold-decorated variants of denovo_401 (deduplicated)."""
    base = Chem.MolFromSmiles(REF_401)
    if base is None:
        sys.exit("  ABORT: could not parse denovo_401 reference SMILES")
    ring = _phenyl_ring(base)
    ch_positions = [i for i in ring if base.GetAtomWithIdx(i).GetTotalNumHs() >= 1]
    seen = {Chem.MolToSmiles(base)}
    out = [("ref_401", REF_401)]                 # in-run baseline
    n = 0
    # mono-substitution: each aromatic CH x each R-group
    for pi, idx in enumerate(ch_positions):
        for r in RGROUPS:
            smi = _attach(Chem, base, r, idx)
            if smi and smi not in seen:
                seen.add(smi)
                out.append((f"lo_m{pi}_{_rtag(r)}", smi)); n += 1
    # di-substitution: para-like pairs of SMALL groups (keep MW sane) across two CH positions
    small = ["F", "Cl", "C", "O", "OC", "C#N", "N"]
    for a_i in range(len(ch_positions)):
        for b_i in range(a_i + 1, len(ch_positions)):
            for r1 in small:
                s1 = _attach(Chem, base, r1, ch_positions[a_i])
                if not s1:
                    continue
                m1 = Chem.MolFromSmiles(s1)
                if m1 is None:
                    continue
                ring1 = _phenyl_ring(m1)
                pos1 = [i for i in ring1 if m1.GetAtomWithIdx(i).GetTotalNumHs() >= 1]
                # attach the second small group at a remaining CH
                for r2 in small:
                    if not pos1:
                        break
                    s2 = _attach(Chem, m1, r2, pos1[len(pos1) // 2])
                    if s2 and s2 not in seen:
                        seen.add(s2)
                        out.append((f"lo_d{a_i}{b_i}_{_rtag(r1)}_{_rtag(r2)}", s2)); n += 1
    # terminal-arm variants
    for name, smi in TERMINAL_VARIANTS.items():
        cs = _canon(Chem, smi)
        if cs and cs not in seen:
            seen.add(cs)
            out.append((f"lo_{name}", cs))
    return out


def _rtag(r):
    return "".join(ch for ch in r if ch.isalnum())[:6] or "x"


def _canon(Chem, smi):
    m = Chem.MolFromSmiles(smi)
    return Chem.MolToSmiles(m) if m is not None else None


def main():
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors as Desc, Crippen, Lipinski as Lip, QED, rdMolDescriptors as rdMD
        from rdkit.Chem import RDConfig
        from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
    except ImportError as e:  # noqa: BLE001
        sys.exit(f"  needs rdkit: {e}")
    sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
    import sascorer
    rdkit = (Chem, Desc, Crippen, Lip, QED, rdMD, FilterCatalog, FilterCatalogParams, sascorer)

    import warhead_chem_profile as wc
    import denovo_funnel as funnel

    variants = enumerate_variants(Chem)
    rows = []
    for name, smi in variants:
        prof = wc.profile(smi, rdkit)
        if "error" in prof:
            rows.append({"name": name, "smiles": smi, "error": prof["error"]})
            continue
        # handle_contacts unknown pre-dock -> 0 (the dock computes real contacts); promise still ranks on
        # QED/SA/alerts/size so the developability gate (top_developable_candidates) works downstream.
        rows.append({"name": name, "smiles": smi, **prof,
                     "handle_contacts": 0,
                     "denovo_promise": funnel.score_molecule(prof, 0)})
    rows = funnel.rank(rows)

    n_valid = sum(1 for r in rows if r.get("denovo_promise") is not None)
    res = {"_note": "Scaffold-seeded lead-optimisation of denovo_401 (keep the selective core, decorate the "
                    "phenyl + terminal arms toward the divergent handles). Same schema as nr4a3_denovo.py so "
                    "the existing dock + MM-GBSA funnel consumes it. ref_401 = in-run baseline. Promise is a "
                    "drug-likeness prior; AFFINITY is decided downstream by dock + multi-snapshot MM-GBSA.",
           "reference": "denovo_401", "reference_smiles": REF_401,
           "summary": {"n_generated": len(rows), "n_valid": n_valid,
                       "n_unique_smiles": len({r.get("smiles") for r in rows if r.get("smiles")})},
           "candidates": rows, "_status": "ok"}

    out_dir = os.environ.get("OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "nr4a3-denovo.json")
    json.dump(res, open(out_path, "w"), indent=2)
    print(f"  wrote {out_path}: {len(rows)} variants ({n_valid} valid)", flush=True)
    top = [r for r in rows if r.get("denovo_promise") is not None][:6]
    for r in top:
        print(f"    {r['name']:<18} promise={r['denovo_promise']} QED={r.get('QED')} "
              f"SA={r.get('SAscore')} MW={r.get('MW')} {r['smiles'][:60]}", flush=True)

    # Optional S3 upload so the dock job can read it (OUTPUT_PREFIX + AWS creds in a runner).
    prefix = os.environ.get("OUTPUT_PREFIX")
    if prefix:
        try:
            import boto3
            region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
            acct = boto3.client("sts").get_caller_identity()["Account"]
            bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
            boto3.client("s3").upload_file(out_path, bucket, f"{prefix}/nr4a3-denovo.json")
            print(f"  uploaded -> s3://{bucket}/{prefix}/nr4a3-denovo.json", flush=True)
        except Exception as e:  # noqa: BLE001
            sys.exit(f"  S3 upload failed: {e}")


if __name__ == "__main__":
    main()
