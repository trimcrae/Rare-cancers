#!/usr/bin/env python3
"""
First in-silico warhead evidence for the NR4A3 degrader: dock real NR4A-relevant ligands into the
AlphaFold NR4A3 ligand-binding domain (fpocket Pocket-5 site).

This is the CPU-feasible first action from nr4a3-degrader-design-spec.md — characterise the
warhead-binding site with REAL chemical matter (no fabricated structures):
  - Receptor: AlphaFold model AF-Q92570 (NR4A3), the LBD that the EWSR1::NR4A3 fusion retains.
  - Site: fpocket Pocket 5 (residues 406-534) — box centred on those residues' CA centroid.
  - Ligands: REAL SMILES pulled from ChEMBL (named NR4A-relevant compounds + any NR4A3-target
    actives). RDKit makes 3D conformers; smina docks; we report binding scores (kcal/mol).

Honest framing: docking scores are a *site-characterisation prior*, not affinities — they tell us
whether the retained LBD pocket can accommodate drug-like matter and which chemotypes sit best, to
seed warhead design. Everything sourced (ChEMBL + AFDB). Internet + smina/RDKit -> runs in CI.
Output: nr4a3-docking.json
"""

import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "nr4a3-docking.json")
AFDB_PDB = "https://alphafold.ebi.ac.uk/files/AF-Q92570-F1-model_v4.pdb"
CHEMBL = "https://www.ebi.ac.uk/chembl/api/data"
POCKET_RESIDUES = range(406, 535)   # fpocket Pocket 5 (NR4A3 LBD)

# Named, REAL NR4A-relevant compounds — SMILES are fetched from ChEMBL by name (never hard-coded),
# so nothing is fabricated; names that don't resolve are skipped.
LIGAND_NAMES = [
    "celastrol", "cytosporone B", "amodiaquine", "chloroquine",
    "piperlongumine", "resveratrol",
]


def _get(url, timeout=60):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0",
                                                       "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa
            import time
            short = url[:90]
            print("  retry " + str(i + 1) + " " + short + ": " + str(e), file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError("failed: " + url)


def chembl_smiles_by_name(name):
    """Resolve a compound NAME to (chembl_id, canonical_smiles) via ChEMBL — real data only."""
    try:
        url = f"{CHEMBL}/molecule/search?q={urllib.parse.quote(name)}&format=json&limit=1"
        data = json.loads(_get(url))
        mols = data.get("molecules", [])
        if not mols:
            return None
        m = mols[0]
        s = (m.get("molecule_structures") or {}).get("canonical_smiles")
        if s:
            return m.get("molecule_chembl_id"), s
    except Exception as e:  # noqa
        print(f"  chembl name '{name}': {e}", file=sys.stderr)
    return None


def chembl_nr4a3_actives(limit=15):
    """Pull ligands tested against the NR4A3 target itself (real actives), if any."""
    out = []
    try:
        t = json.loads(_get(f"{CHEMBL}/target/search?q=NR4A3&format=json&limit=5"))
        tids = [x["target_chembl_id"] for x in t.get("targets", [])
                if "NR4A3" in (x.get("pref_name", "") + x.get("target_chembl_id", "")) or
                "nuclear receptor subfamily 4" in x.get("pref_name", "").lower()]
        for tid in tids[:2]:
            a = json.loads(_get(f"{CHEMBL}/activity?target_chembl_id={tid}"
                                f"&format=json&limit={limit}"))
            for act in a.get("activities", []):
                smi = act.get("canonical_smiles")
                cid = act.get("molecule_chembl_id")
                if smi and cid:
                    out.append((f"NR4A3-active:{cid}", cid, smi))
    except Exception as e:  # noqa
        print(f"  chembl NR4A3 actives: {e}", file=sys.stderr)
    return out


def pocket_box(pdb_path):
    """Box centre = CA centroid of Pocket-5 residues; size covers the pocket."""
    xs, ys, zs = [], [], []
    for line in open(pdb_path):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            try:
                resi = int(line[22:26])
            except ValueError:
                continue
            if resi in POCKET_RESIDUES:
                xs.append(float(line[30:38])); ys.append(float(line[38:46])); zs.append(float(line[46:54]))
    if not xs:
        raise RuntimeError("no Pocket-5 CA atoms found")
    c = (sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs))
    return c, len(xs)


def make_sdf(ligands, path):
    """ligands: list of (label, id, smiles) -> 3D SDF via RDKit. Returns kept labels."""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    kept = []
    w = Chem.SDWriter(path)
    for label, cid, smi in ligands:
        m = Chem.MolFromSmiles(smi)
        if m is None:
            print(f"  rdkit could not parse {label}", file=sys.stderr); continue
        m = Chem.AddHs(m)
        if AllChem.EmbedMolecule(m, randomSeed=0xf00d) != 0:
            print(f"  embed failed {label}", file=sys.stderr); continue
        try:
            AllChem.MMFFOptimizeMolecule(m)
        except Exception:
            pass
        m.SetProp("_Name", label)
        w.write(m); kept.append((label, cid, smi))
    w.close()
    return kept


def main():
    res = {"_note": "Docking of REAL NR4A-relevant ligands (ChEMBL) into the AlphaFold NR4A3 LBD "
                    "Pocket-5 (residues 406-534), the site retained in EWSR1::NR4A3. Scores are a "
                    "site-characterisation prior (can the retained pocket bind drug-like matter? "
                    "which chemotypes?), NOT affinities. Seeds the warhead design "
                    "(nr4a3-degrader-design-spec.md).",
           "receptor": "AF-Q92570 (AFDB v4)", "pocket": "fpocket Pocket 5 (406-534)"}

    # 1) receptor
    pdb_path = os.path.join(HERE, "AF-Q92570.pdb")
    open(pdb_path, "wb").write(_get(AFDB_PDB, timeout=120))
    center, npocket = pocket_box(pdb_path)
    res["box_center"] = [round(x, 2) for x in center]
    res["n_pocket_CA"] = npocket
    print(f"  box center {res['box_center']} from {npocket} pocket CA", file=sys.stderr)

    # 2) real ligands from ChEMBL
    ligands = []
    for nm in LIGAND_NAMES:
        hit = chembl_smiles_by_name(nm)
        if hit:
            ligands.append((nm, hit[0], hit[1]))
            print(f"  resolved {nm} -> {hit[0]}", file=sys.stderr)
    ligands += chembl_nr4a3_actives()
    res["n_ligands_resolved"] = len(ligands)
    res["ligands"] = [{"label": l, "chembl_id": c, "smiles": s} for l, c, s in ligands]
    if not ligands:
        res["_status"] = "no ligands resolved"
        json.dump(res, open(OUT, "w"), indent=2); return

    # 3) 3D SDF
    try:
        sdf = os.path.join(HERE, "ligands.sdf")
        kept = make_sdf(ligands, sdf)
        res["n_ligands_embedded"] = len(kept)
    except ImportError:
        res["_status"] = "rdkit missing"; json.dump(res, open(OUT, "w"), indent=2); return

    # 4) dock with smina
    smina = _which("smina")
    if not smina or not kept:
        res["_status"] = "smina missing or no ligands"; json.dump(res, open(OUT, "w"), indent=2); return
    out_sdf = os.path.join(HERE, "docked.sdf")
    cmd = [smina, "-r", pdb_path, "-l", sdf,
           "--center_x", str(center[0]), "--center_y", str(center[1]), "--center_z", str(center[2]),
           "--size_x", "24", "--size_y", "24", "--size_z", "24",
           "--exhaustiveness", "8", "--num_modes", "1", "-o", out_sdf]
    print("  smina:", " ".join(cmd), file=sys.stderr)
    p = subprocess.run(cmd, capture_output=True, text=True)
    print(p.stdout[-2000:], file=sys.stderr); print(p.stderr[-1000:], file=sys.stderr)

    # 5) parse minimizedAffinity per ligand from docked.sdf
    scores = []
    if os.path.exists(out_sdf):
        blocks = open(out_sdf).read().split("$$$$")
        for b in blocks:
            bl = b.strip().splitlines()
            if not bl:
                continue
            nm = bl[0].strip()
            a = None
            for j, ln in enumerate(b.splitlines()):
                if "minimizedAffinity" in ln:
                    a = float(b.splitlines()[j+1].strip())
                    break
            if nm and a is not None:
                scores.append({"label": nm, "affinity_kcal_mol": round(a, 2)})
    scores.sort(key=lambda x: x["affinity_kcal_mol"])
    res["docking_scores"] = scores
    res["best"] = scores[0] if scores else None
    res["_status"] = "ok" if scores else "no scores parsed"
    json.dump(res, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps({"box_center": res["box_center"], "n_ligands": len(ligands),
                      "best": res.get("best"), "top5": scores[:5]}, indent=2))


def _which(prog):
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, prog)
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return None


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # always leave a diagnostic so opaque CI failures become visible
        import traceback
        json.dump({"_status": "error", "error": str(exc),
                   "trace": traceback.format_exc()[-1800:]}, open(OUT, "w"), indent=2)
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(0)  # exit 0 so the publish step still uploads the diagnostic JSON
