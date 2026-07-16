#!/usr/bin/env python3
"""valA_mini staging — fetch a PUBLIC known-answer RBFE system (TYK2, the standard Wang-2015 FEP benchmark)
and stage ONE congeneric edge into the exact input layout the repo's RBFE pipeline consumes, so we can confirm
OUR container build + protocol reproduces a MEASURED ΔΔG (STRATEGY.md RUNG 1, mandatory-change-1A).

Runs in a GitHub Actions runner (unrestricted network + AWS creds) via the rbfe submitter's `mode=stagebench`.
NOT science on NR4A — a build-consistency check against a public measured ΔΔG.

WHAT IT DOES
  1. `git clone --depth 1` the OpenFF protein-ligand-benchmark (public GitHub → reachable from a CI runner;
     the egress-proxy that blocks the dev sandbox does not apply here).
  2. Locate the TYK2 target's protein PDB + ligands SDF (poses in the protein frame) + the experimental
     affinity table — by GLOBBING the tree (robust to the repo's layout drift), never a hardcoded path.
  3. OBSERVE + PRINT the real schema (tree, ligand SD-property keys, a sample of the affinity file) so the
     known-answer ΔΔG is read from the actual published data, not guessed. (Rule: don't fabricate a "known"
     number — extract it.)
  4. Pick ONE edge (a documented small-perturbation pair if present, else the two ligands with the largest
     shared MCS), compute the experimental ΔΔG = ΔG_exp(B) − ΔG_exp(A) from the published affinities.
  5. Write `docked_<receptor>.sdf` (the two records retitled to LIGAND_A/LIGAND_B so the engine resolves them
     by _Name) + `<receptor>-opened.pdb` to s3://<bucket>/<RECEPTOR_PREFIX>/, and a manifest JSON (chosen
     ligands, SMILES, per-ligand ΔG_exp, ΔΔG_exp, units/method, source commit) to the same prefix + stdout.

The RBFE run then uses the SAME setup→simulate(spot_safe=1)→analyze split as Step 0, tag=valA-tyk2,
receptor slot reused as `nr4a3` COSMETICALLY (this is TYK2 data — see manifest.target), restricted via
ONLY_LEGS=solvent,nr4a3. GO/NO-GO: computed ΔΔG_bind within ~1.5–2 kcal/mol of ΔΔG_exp → build sound.
"""
import glob
import json
import math
import os
import subprocess
import sys

REPO = "https://github.com/openforcefield/protein-ligand-benchmark"
TARGET = os.environ.get("VALA_TARGET", "tyk2")
# Preferred canonical edge (well-characterized single-R-group perturbation in the TYK2 ejm series). If either
# name is absent in the fetched data, fall back to an MCS-chosen pair — reported in the manifest.
PREF_A = os.environ.get("VALA_LIG_A", "ejm_31")
PREF_B = os.environ.get("VALA_LIG_B", "ejm_42")
RT_KCAL = 0.001987204259 * 298.15   # kcal/mol at 298.15 K


def _sh(cmd, **kw):
    print(f"[valA-stage] $ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, check=True, **kw)


def _clone(workdir):
    dest = os.path.join(workdir, "plb")
    if not os.path.isdir(dest):
        _sh(["git", "clone", "--depth", "1", REPO, dest])
    sha = subprocess.run(["git", "-C", dest, "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    return dest, sha


def _find_target_dir(plb):
    # glob for a directory named exactly TARGET anywhere in the tree (layout drifts across versions)
    cands = [d for d in glob.glob(os.path.join(plb, "**", TARGET), recursive=True) if os.path.isdir(d)]
    if not cands:
        cands = [d for d in glob.glob(os.path.join(plb, "**", f"*{TARGET}*"), recursive=True)
                 if os.path.isdir(d)]
    if not cands:
        sys.exit(f"[valA-stage] could not locate target dir for '{TARGET}' under {plb}")
    # prefer the shallowest match
    cands.sort(key=lambda p: p.count(os.sep))
    return cands[0]


def _tree(root, maxdepth=3):
    out = []
    base = root.rstrip("/").count(os.sep)
    for dirpath, dirs, files in os.walk(root):
        depth = dirpath.count(os.sep) - base
        if depth > maxdepth:
            dirs[:] = []
            continue
        out.append("  " * depth + os.path.basename(dirpath) + "/")
        for f in sorted(files):
            out.append("  " * (depth + 1) + f)
    return "\n".join(out)


def _read(p):
    with open(p, "r", errors="replace") as fh:
        return fh.read()


def main():
    workdir = os.environ.get("VALA_WORKDIR", "/tmp/valA")
    os.makedirs(workdir, exist_ok=True)
    plb, sha = _clone(workdir)
    tdir = _find_target_dir(plb)
    print(f"[valA-stage] target dir: {tdir}  (source {REPO}@{sha})", flush=True)
    print("[valA-stage] ===== target tree =====\n" + _tree(tdir), flush=True)

    # locate the pieces by glob (robust to layout)
    pdbs = sorted(glob.glob(os.path.join(tdir, "**", "*.pdb"), recursive=True))
    sdfs = sorted(glob.glob(os.path.join(tdir, "**", "*.sdf"), recursive=True))
    ymls = sorted(glob.glob(os.path.join(tdir, "**", "*.yml"), recursive=True)
                  + glob.glob(os.path.join(tdir, "**", "*.yaml"), recursive=True)
                  + glob.glob(os.path.join(tdir, "**", "*.json"), recursive=True)
                  + glob.glob(os.path.join(tdir, "**", "*.csv"), recursive=True))
    print("[valA-stage] PDBs:", *pdbs, sep="\n  ", flush=True)
    print("[valA-stage] SDFs:", *sdfs, sep="\n  ", flush=True)
    print("[valA-stage] data files:", *ymls, sep="\n  ", flush=True)

    # ---- OBSERVE ligand SDF schema (print names + SD-property keys of the first records) ----
    try:
        from rdkit import Chem
    except Exception as e:  # noqa: BLE001
        sys.exit(f"[valA-stage] rdkit unavailable in the runner ({e}); add it to the workflow pip install")

    # choose the ligands SDF = the one with the most records (the multi-ligand file)
    lig_sdf, recs = None, []
    for s in sdfs:
        rr = [m for m in Chem.SDMolSupplier(s, removeHs=False) if m is not None]
        if len(rr) > len(recs):
            lig_sdf, recs = s, rr
    if not recs:
        sys.exit("[valA-stage] no ligand records parsed from any SDF")
    print(f"[valA-stage] ligands SDF: {lig_sdf}  ({len(recs)} records)", flush=True)
    names = [m.GetProp("_Name") if m.HasProp("_Name") else f"rec{i}" for i, m in enumerate(recs)]
    print("[valA-stage] ligand names:", names, flush=True)
    print("[valA-stage] first-record SD keys:", list(recs[0].GetPropNames()), flush=True)
    for m in recs[:3]:
        props = {k: m.GetProp(k) for k in m.GetPropNames()}
        print(f"[valA-stage]   {m.GetProp('_Name') if m.HasProp('_Name') else '?'}: {props}", flush=True)

    # print heads of the data files so the affinity schema is visible in the log
    for y in ymls:
        head = _read(y)[:1500]
        print(f"[valA-stage] ===== {os.path.relpath(y, tdir)} (head) =====\n{head}", flush=True)

    # ---- extract experimental ΔG per ligand (best-effort across known PLB schemas) ----
    def _dg_exp(mol):
        """Return (dG_kcal, how) from a ligand record's SD props, trying common PLB keys."""
        props = {k.lower(): mol.GetProp(k) for k in mol.GetPropNames()}
        for k in ("dg_exp", "exp_dg", "measured_dg", "dg", "affinity_dg[kcal/mol]"):
            if k in props:
                try:
                    return float(props[k].split()[0]), f"SD:{k}"
                except ValueError:
                    pass
        for k in ("ki", "ic50", "exp_ki", "ki (nm)", "ic50 (nm)"):
            if k in props:
                try:
                    v = float(props[k].split()[0])
                    # assume nM if the key mentions nM; PLB commonly stores nM
                    ki_m = v * 1e-9
                    return RT_KCAL * math.log(ki_m), f"SD:{k}=-RTln"
                except (ValueError, ZeroDivisionError):
                    pass
        for k in ("pic50", "pki", "pactivity"):
            if k in props:
                try:
                    p = float(props[k].split()[0])
                    return -RT_KCAL * math.log(10) * p, f"SD:{k}=-2.303RT*p"
                except ValueError:
                    pass
        return None, None

    by_name = {n: m for n, m in zip(names, recs)}

    def _pick_edge():
        if PREF_A in by_name and PREF_B in by_name:
            return PREF_A, PREF_B, "preferred"
        # fall back: two ligands with the largest MCS (most-congeneric)
        from rdkit.Chem import rdFMCS
        best, pair = -1, (names[0], names[1] if len(names) > 1 else names[0])
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                try:
                    mcs = rdFMCS.FindMCS([recs[i], recs[j]], timeout=5)
                    if mcs.numAtoms > best:
                        best, pair = mcs.numAtoms, (names[i], names[j])
                except Exception:  # noqa: BLE001
                    continue
        return pair[0], pair[1], f"mcs({best})"

    a_name, b_name, how_edge = _pick_edge()
    molA, molB = by_name[a_name], by_name[b_name]
    dgA, howA = _dg_exp(molA)
    dgB, howB = _dg_exp(molB)
    ddg_exp = (dgB - dgA) if (dgA is not None and dgB is not None) else None
    print(f"[valA-stage] EDGE {a_name}->{b_name} ({how_edge}); "
          f"ΔG_exp: {a_name}={dgA} ({howA}), {b_name}={dgB} ({howB}); ΔΔG_exp={ddg_exp}", flush=True)

    # ---- retitle the two records to the names the RBFE engine will request, write the docked SDF ----
    lig_a = os.environ.get("RBFE_LIGAND_A", f"{TARGET}_{a_name}")
    lig_b = os.environ.get("RBFE_LIGAND_B", f"{TARGET}_{b_name}")
    receptor = os.environ.get("VALA_RECEPTOR_SLOT", "nr4a3")  # cosmetic reuse of the slot; data is TARGET
    protein_pdb = pdbs[0] if pdbs else None
    if protein_pdb is None:
        sys.exit("[valA-stage] no protein PDB found in target dir")

    outdir = os.path.join(workdir, "staged")
    os.makedirs(outdir, exist_ok=True)
    w = Chem.SDWriter(os.path.join(outdir, f"docked_{receptor}.sdf"))
    for nm, mol in ((lig_a, molA), (lig_b, molB)):
        mol.SetProp("_Name", nm)
        w.write(mol)
    w.close()
    # copy protein PDB
    with open(protein_pdb, "r", errors="replace") as fh, \
         open(os.path.join(outdir, f"{receptor}-opened.pdb"), "w") as out:
        out.write(fh.read())

    manifest = {
        "_what": "valA_mini public known-answer RBFE benchmark (build-consistency; NOT NR4A science)",
        "target": TARGET, "source": f"{REPO}@{sha}",
        "receptor_slot_cosmetic": receptor, "note_slot": "receptor slot reused; DATA IS %s" % TARGET.upper(),
        "ligand_a": lig_a, "ligand_b": lig_b, "edge_selection": how_edge,
        "dG_exp_a_kcal": dgA, "dG_exp_b_kcal": dgB, "ddG_exp_kcal": ddg_exp,
        "dG_method_a": howA, "dG_method_b": howB,
        "smiles_a": Chem.MolToSmiles(Chem.RemoveHs(molA)), "smiles_b": Chem.MolToSmiles(Chem.RemoveHs(molB)),
        "go_no_go": "computed ΔΔG_bind within ~1.5-2 kcal/mol of ddG_exp_kcal -> build sound (GO)",
    }
    with open(os.path.join(outdir, "valA_manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print("[valA-stage] MANIFEST\n" + json.dumps(manifest, indent=2), flush=True)

    # ---- upload to S3 (RECEPTOR_PREFIX) ----
    dest = os.environ.get("RECEPTOR_PREFIX", "valA-tyk2-bench").rstrip("/")
    if os.environ.get("VALA_NO_UPLOAD") == "1":
        print("[valA-stage] VALA_NO_UPLOAD=1 — skipping S3 upload (dry run).", flush=True)
        return
    import boto3
    import sagemaker
    s3 = boto3.client("s3")
    bucket = sagemaker.Session().default_bucket()
    for fn in (f"docked_{receptor}.sdf", f"{receptor}-opened.pdb", "valA_manifest.json"):
        s3.upload_file(os.path.join(outdir, fn), bucket, f"{dest}/{fn}")
        print(f"[valA-stage] uploaded s3://{bucket}/{dest}/{fn}", flush=True)
    print(f"[valA-stage] DONE. Now: setup->simulate(spot_safe=1)->analyze with "
          f"receptor_prefix={dest} tag=valA-tyk2 ligand_a={lig_a} ligand_b={lig_b} "
          f"only_legs=solvent,{receptor}. Then reduce; compare ΔΔG_bind to ddG_exp_kcal={ddg_exp}.", flush=True)


if __name__ == "__main__":
    main()
