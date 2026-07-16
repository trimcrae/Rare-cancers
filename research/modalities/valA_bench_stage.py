#!/usr/bin/env python3
"""valA_mini staging — fetch a PUBLIC known-answer RBFE system (TYK2, the standard Wang-2015 FEP benchmark)
and stage ONE congeneric edge into the exact input layout the repo's RBFE pipeline consumes, so we can confirm
OUR container build + protocol reproduces a MEASURED ΔΔG (STRATEGY.md RUNG 1, mandatory-change-1A).

Runs in a GitHub Actions runner (unrestricted network + AWS creds) via the rbfe submitter's `mode=stagebench`.
NOT science on NR4A — a build-consistency check against a public measured ΔΔG.

PIPELINE
  1. `git clone --depth 1` the OpenFF protein-ligand-benchmark (public GitHub → reachable from a CI runner).
  2. Locate the TYK2 target's protein PDB + ligands SDF (poses in the protein frame) + the affinity data files
     by GLOBBING the tree (robust to layout drift).
  3. Read the experimental ΔG per ligand from the REAL published data (measurement: type/unit/value in the
     ligand yml, else SD props) and convert Ki/IC50/pIC50 → kcal/mol. Never guess a "known" number.
  4. Pick the deterministic edge lig_ejm_31 → lig_ejm_42 (well-characterized TYK2 pair; MCS fallback if absent),
     compute ΔΔG_exp = ΔG(B) − ΔG(A).
  5. Write docked_<slot>.sdf (2 records retitled to LIGAND_A/LIGAND_B so the engine resolves by _Name) +
     <slot>-opened.pdb + valA_manifest.json to s3://<bucket>/<RECEPTOR_PREFIX>/.

2026-07-16 v2 fixes (from the v1 CI log): ligand names carry a `lig_` prefix (v1 matched `ejm_31`→miss→wrong
MCS pair); affinities are NOT in the SDF (v1 dumped every 03_edges/*.yml and buried the schema). v2 uses the
prefix, parses the ligand measurement yml, and only dumps ligand/affinity data (not the edge-map files).
"""
import glob
import json
import math
import os
import subprocess
import sys

REPO = "https://github.com/openforcefield/protein-ligand-benchmark"
TARGET = os.environ.get("VALA_TARGET", "tyk2")
PREF_A = os.environ.get("VALA_LIG_A", "lig_ejm_31")   # note the real PLB `lig_` prefix
PREF_B = os.environ.get("VALA_LIG_B", "lig_ejm_42")
RT_KCAL = 0.001987204259 * 298.15   # kcal/mol at 298.15 K
_UNIT = {"m": 1.0, "molar": 1.0, "mm": 1e-3, "um": 1e-6, "µm": 1e-6, "nm": 1e-9, "pm": 1e-12}


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
    cands = [d for d in glob.glob(os.path.join(plb, "**", TARGET), recursive=True) if os.path.isdir(d)]
    if not cands:
        cands = [d for d in glob.glob(os.path.join(plb, "**", f"*{TARGET}*"), recursive=True)
                 if os.path.isdir(d)]
    if not cands:
        sys.exit(f"[valA-stage] could not locate target dir for '{TARGET}' under {plb}")
    cands.sort(key=lambda p: p.count(os.sep))
    return cands[0]


def _read(p):
    with open(p, "r", errors="replace") as fh:
        return fh.read()


def _dg_from_measurement(meas):
    """PLB measurement dict {type, unit, value} → (ΔG kcal/mol, how). None if unparseable."""
    if not isinstance(meas, dict):
        return None, None
    typ = str(meas.get("type", "")).lower()
    val = meas.get("value")
    unit = str(meas.get("unit", "")).lower().replace(" ", "")
    try:
        val = float(val)
    except (TypeError, ValueError):
        return None, None
    if typ in ("pic50", "pki", "pkd", "pactivity"):
        return -RT_KCAL * math.log(10) * val, f"{typ}=-2.303RT*p"
    if typ in ("ki", "kd", "ic50", "ec50"):
        f = _UNIT.get(unit)
        if f is None:
            return None, f"{typ} unit={unit}?"
        molar = val * f
        if molar <= 0:
            return None, f"{typ} value<=0"
        return RT_KCAL * math.log(molar), f"{typ}({unit})=RTln"
    if typ in ("dg", "deltag") and unit in ("kcal/mol", "kcalmol-1", "kcal", ""):
        return val, f"{typ} direct"
    return None, f"unhandled type={typ} unit={unit}"


def _build_affinity_map(aff_files):
    """Parse every non-edge data file; return {ligand_name: measurement_dict} across known PLB shapes."""
    import yaml
    aff = {}
    for f in aff_files:
        try:
            data = yaml.safe_load(_read(f))
        except Exception as e:  # noqa: BLE001
            print(f"[valA-stage] WARN yaml parse {os.path.basename(f)}: {e}", flush=True)
            continue
        # shape A: {ligname: {measurement: {...}}}   shape B: {"ligands": {ligname: {...}}}
        blocks = data if isinstance(data, dict) else {}
        if "ligands" in blocks and isinstance(blocks["ligands"], dict):
            blocks = blocks["ligands"]
        for k, v in blocks.items():
            if not isinstance(v, dict):
                continue
            meas = v.get("measurement") or v.get("measured") or v.get("affinity") or v
            if isinstance(meas, dict) and ("value" in meas or "type" in meas):
                aff[k] = meas
    return aff


def _sd_measurement(mol):
    """Fallback: pull a measurement from a ligand SDF record's SD properties."""
    props = {k.lower(): mol.GetProp(k) for k in mol.GetPropNames()}
    for typ in ("pic50", "pki"):
        if typ in props:
            try:
                return {"type": typ, "value": float(props[typ].split()[0])}
            except ValueError:
                pass
    for typ in ("ki", "ic50", "kd"):
        for key in (typ, f"{typ}[nm]", f"{typ} (nm)", f"{typ}_nm"):
            if key in props:
                try:
                    return {"type": typ, "unit": "nm", "value": float(props[key].split()[0])}
                except ValueError:
                    pass
    for key in ("dg_exp", "exp_dg", "dg[kcal/mol]", "dg"):
        if key in props:
            try:
                return {"type": "dg", "unit": "kcal/mol", "value": float(props[key].split()[0])}
            except ValueError:
                pass
    return None


def main():
    workdir = os.environ.get("VALA_WORKDIR", "/tmp/valA")
    os.makedirs(workdir, exist_ok=True)
    plb, sha = _clone(workdir)
    tdir = _find_target_dir(plb)
    print(f"[valA-stage] target dir: {tdir}  (source {REPO}@{sha})", flush=True)

    pdbs = sorted(glob.glob(os.path.join(tdir, "**", "*.pdb"), recursive=True))
    sdfs = sorted(glob.glob(os.path.join(tdir, "**", "*.sdf"), recursive=True))
    data_files = [f for f in (glob.glob(os.path.join(tdir, "**", "*.yml"), recursive=True)
                              + glob.glob(os.path.join(tdir, "**", "*.yaml"), recursive=True)
                              + glob.glob(os.path.join(tdir, "**", "*.json"), recursive=True)
                              + glob.glob(os.path.join(tdir, "**", "*.csv"), recursive=True))
                  if "03_edges" not in f and "edge" not in os.path.basename(f).lower()]
    print("[valA-stage] PDBs:", *pdbs, sep="\n  ", flush=True)
    print("[valA-stage] SDFs:", *sdfs, sep="\n  ", flush=True)
    print("[valA-stage] affinity/data files (edges excluded):", *data_files, sep="\n  ", flush=True)

    try:
        from rdkit import Chem
    except Exception as e:  # noqa: BLE001
        sys.exit(f"[valA-stage] rdkit unavailable in the runner ({e})")

    lig_sdf, recs = None, []
    for s in sdfs:
        rr = [m for m in Chem.SDMolSupplier(s, removeHs=False) if m is not None]
        if len(rr) > len(recs):
            lig_sdf, recs = s, rr
    if not recs:
        sys.exit("[valA-stage] no ligand records parsed")
    names = [m.GetProp("_Name") if m.HasProp("_Name") else f"rec{i}" for i, m in enumerate(recs)]
    by_name = {n: m for n, m in zip(names, recs)}
    print(f"[valA-stage] ligands SDF: {lig_sdf}  ({len(recs)} records)\n  names={names}", flush=True)

    affmap = _build_affinity_map(data_files)
    print(f"[valA-stage] affinity map: {len(affmap)} ligands parsed; keys sample={list(affmap)[:6]}", flush=True)

    def _dg(name, mol):
        meas = affmap.get(name) or _sd_measurement(mol)
        dg, how = _dg_from_measurement(meas) if meas else (None, None)
        return dg, how, meas

    def _pick_edge():
        if PREF_A in by_name and PREF_B in by_name:
            return PREF_A, PREF_B, "preferred"
        from rdkit.Chem import rdFMCS
        best, pair = -1, (names[0], names[min(1, len(names) - 1)])
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                try:
                    n = rdFMCS.FindMCS([recs[i], recs[j]], timeout=5).numAtoms
                    if n > best:
                        best, pair = n, (names[i], names[j])
                except Exception:  # noqa: BLE001
                    continue
        return pair[0], pair[1], f"mcs({best})"

    a_src, b_src, how_edge = _pick_edge()
    molA, molB = by_name[a_src], by_name[b_src]
    dgA, howA, measA = _dg(a_src, molA)
    dgB, howB, measB = _dg(b_src, molB)
    ddg_exp = (dgB - dgA) if (dgA is not None and dgB is not None) else None
    # focused evidence (NOT the whole tree): exactly the two chosen ligands
    print(f"[valA-stage] CHOSEN EDGE {a_src}->{b_src} ({how_edge})", flush=True)
    print(f"[valA-stage]   {a_src}: measurement={measA} -> ΔG_exp={dgA} ({howA})", flush=True)
    print(f"[valA-stage]   {b_src}: measurement={measB} -> ΔG_exp={dgB} ({howB})", flush=True)
    print(f"[valA-stage]   ΔΔG_exp = {ddg_exp} kcal/mol", flush=True)

    lig_a = os.environ.get("RBFE_LIGAND_A", f"{TARGET}_{a_src.replace('lig_', '')}")
    lig_b = os.environ.get("RBFE_LIGAND_B", f"{TARGET}_{b_src.replace('lig_', '')}")
    receptor = os.environ.get("VALA_RECEPTOR_SLOT", "nr4a3")
    if not pdbs:
        sys.exit("[valA-stage] no protein PDB found")

    outdir = os.path.join(workdir, "staged")
    os.makedirs(outdir, exist_ok=True)
    w = Chem.SDWriter(os.path.join(outdir, f"docked_{receptor}.sdf"))
    for nm, mol in ((lig_a, molA), (lig_b, molB)):
        mol.SetProp("_Name", nm)
        w.write(mol)
    w.close()
    with open(os.path.join(outdir, f"{receptor}-opened.pdb"), "w") as out:
        out.write(_read(pdbs[0]))

    manifest = {
        "_what": "valA_mini public known-answer RBFE benchmark (build-consistency; NOT NR4A science)",
        "target": TARGET, "source": f"{REPO}@{sha}",
        "receptor_slot_cosmetic": receptor, "note_slot": f"receptor slot reused; DATA IS {TARGET.upper()}",
        "ligand_a": lig_a, "ligand_b": lig_b, "source_name_a": a_src, "source_name_b": b_src,
        "edge_selection": how_edge,
        "dG_exp_a_kcal": dgA, "dG_exp_b_kcal": dgB, "ddG_exp_kcal": ddg_exp,
        "dG_method_a": howA, "dG_method_b": howB, "measurement_a": measA, "measurement_b": measB,
        "smiles_a": Chem.MolToSmiles(Chem.RemoveHs(molA)), "smiles_b": Chem.MolToSmiles(Chem.RemoveHs(molB)),
        "go_no_go": "computed ΔΔG_bind(A->B) within ~1.5-2 kcal/mol of ddG_exp_kcal -> build sound (GO)",
    }
    with open(os.path.join(outdir, "valA_manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print("[valA-stage] MANIFEST\n" + json.dumps(manifest, indent=2), flush=True)

    if os.environ.get("VALA_NO_UPLOAD") == "1":
        print("[valA-stage] VALA_NO_UPLOAD=1 — dry run, no S3 upload.", flush=True)
        return
    if ddg_exp is None and os.environ.get("VALA_ALLOW_NO_DDG") != "1":
        sys.exit("[valA-stage] ABORT: ΔΔG_exp is None (affinity schema not parsed) — not staging a test with no "
                 "known answer. See the measurement/data dumps above; fix the parser or set VALA_ALLOW_NO_DDG=1.")
    import boto3
    import sagemaker
    s3 = boto3.client("s3")
    bucket = sagemaker.Session().default_bucket()
    dest = os.environ.get("RECEPTOR_PREFIX", "valA-tyk2-bench").rstrip("/")
    for fn in (f"docked_{receptor}.sdf", f"{receptor}-opened.pdb", "valA_manifest.json"):
        s3.upload_file(os.path.join(outdir, fn), bucket, f"{dest}/{fn}")
        print(f"[valA-stage] uploaded s3://{bucket}/{dest}/{fn}", flush=True)
    print(f"[valA-stage] DONE. RBFE: setup->simulate(spot_safe=1)->analyze receptor_prefix={dest} tag=valA-tyk2 "
          f"ligand_a={lig_a} ligand_b={lig_b} only_legs=solvent,{receptor}; reduce; compare ΔΔG_bind to "
          f"ddG_exp={ddg_exp}.", flush=True)


if __name__ == "__main__":
    main()
