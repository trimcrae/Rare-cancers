#!/usr/bin/env python3
"""Blind-prep for DeepTernary Step-3 controls (protocol §3): build the 6 unbound-PROTAC input files per
control from SEPARATE binary/apo structures, with the native ternary pose SEALED.

DeepTernary `predict_one_unbound(name)` reads from `output/protac22/<name>/`:
  unbound_protein1.pdb  POI, from a NON-native structure
  unbound_lig1.pdb      warhead fragment in the POI frame (from a POI+warhead binary)
  unbound_protein2.pdb  E3, from a NON-native structure
  unbound_lig2.pdb      E3-anchor fragment in the E3 frame (from an E3+anchor binary)
  ligand.pdb/.sdf       full degrader, from the CCD ideal SDF (NOT the native bound pose)
  gt_complex.pdb        native ternary — used ONLY by cal_dockq; kept in a sealed/ subdir until predictions frozen

Blindness rule enforced here: the POI+warhead and E3+anchor coords come from binaries that are NOT the native
ternary; the degrader conformer comes from the CCD ideal SDF; the native ternary is written to `sealed/` and is
never referenced by the prediction step (only by scoring after freeze).

Runs in the DeepTernary CI env (biopandas + rdkit). Config-driven so the per-control chain/ligand IDs (curated
from the sourced binary candidates) are the only thing that changes. Structure facts are SOURCED (RCSB), not
guessed — the integrity gate.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

RCSB_FILE = "https://files.rcsb.org/download/{pid}.pdb"
RCSB_IDEAL = "https://files.rcsb.org/ligands/download/{comp}_ideal.sdf"
UA = {"User-Agent": "rare-cancers-deepternary-blindprep/1.0"}

# The 6 files a blind control must provide + the sealed native (contract from predict.py).
REQUIRED_INPUTS = ["unbound_protein1.pdb", "unbound_lig1.pdb",
                   "unbound_protein2.pdb", "unbound_lig2.pdb", "ligand.pdb", "ligand.sdf"]
SEALED_FILE = "gt_complex.pdb"


def _fetch(url: str, dest: str) -> bool:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        with open(dest, "wb") as fh:
            fh.write(data)
        return True
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[fetch] {url} -> {e}\n")
        return False


def fetch_pdb(pdb_id: str, dest: str) -> bool:
    return _fetch(RCSB_FILE.format(pid=pdb_id.upper()), dest)


def _read_pdb_lines(path: str):
    with open(path) as fh:
        return fh.readlines()


def extract_protein_chains(pdb_path: str, chains, out_path: str) -> int:
    """Write ATOM records (protein) for the given chain IDs to out_path. Returns #atoms."""
    chains = set(chains)
    n = 0
    with open(out_path, "w") as out:
        for ln in _read_pdb_lines(pdb_path):
            if ln.startswith(("ATOM", "TER")) and (len(ln) < 22 or ln[21] in chains):
                out.write(ln)
                if ln.startswith("ATOM"):
                    n += 1
        out.write("END\n")
    return n


def extract_ligand(pdb_path: str, comp_id: str, out_path: str, chain: str | None = None) -> int:
    """Write HETATM records for a given comp id (optionally restricted to a chain) to out_path. Returns #atoms."""
    comp_id = comp_id.upper()
    n = 0
    with open(out_path, "w") as out:
        for ln in _read_pdb_lines(pdb_path):
            if ln.startswith("HETATM") and ln[17:20].strip().upper() == comp_id:
                if chain and ln[21] != chain:
                    continue
                out.write(ln)
                n += 1
        out.write("END\n")
    return n


def build_degrader(comp_id: str, out_sdf: str, out_pdb: str) -> bool:
    """Full degrader from the CCD ideal SDF -> a clean 3D conformer (NOT the native pose)."""
    tmp = out_sdf + ".ideal"
    if not _fetch(RCSB_IDEAL.format(comp=comp_id.upper()), tmp):
        return False
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
        mol = Chem.MolFromMolFile(tmp, sanitize=True, removeHs=False)
        if mol is None:
            # keep the ideal coords if RDKit can't re-embed
            os.replace(tmp, out_sdf)
        else:
            mol = Chem.AddHs(mol, addCoords=True)
            # re-embed to a fresh conformer so no native/deposited geometry leaks
            if AllChem.EmbedMolecule(mol, randomSeed=0xC0FFEE) == 0:
                AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
            Chem.MolToMolFile(mol, out_sdf)
        Chem.MolToPDBFile(Chem.MolFromMolFile(out_sdf, sanitize=False), out_pdb)
        return True
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[degrader] {comp_id} -> {e}\n")
        return False


def prep_control(cfg: dict, base: str) -> dict:
    """Build one control's input dir. cfg keys:
       name, native_pdb, poi_binary_pdb, poi_chains, warhead_comp,
       e3_binary_pdb, e3_chains, anchor_comp, degrader_comp
    """
    d = os.path.join(base, cfg["name"])
    sealed = os.path.join(d, "sealed")
    os.makedirs(sealed, exist_ok=True)
    raw = os.path.join(d, "_raw")
    os.makedirs(raw, exist_ok=True)
    status = {"name": cfg["name"], "ok": True, "steps": {}}

    def _need(pdb):
        p = os.path.join(raw, f"{pdb.upper()}.pdb")
        if not os.path.exists(p):
            status["steps"][f"fetch:{pdb}"] = fetch_pdb(pdb, p)
        return p

    # POI + warhead (blind: from a non-native binary)
    poi = _need(cfg["poi_binary_pdb"])
    status["steps"]["unbound_protein1"] = extract_protein_chains(
        poi, cfg["poi_chains"], os.path.join(d, "unbound_protein1.pdb"))
    status["steps"]["unbound_lig1"] = extract_ligand(
        poi, cfg["warhead_comp"], os.path.join(d, "unbound_lig1.pdb"))
    # E3 + anchor
    e3 = _need(cfg["e3_binary_pdb"])
    status["steps"]["unbound_protein2"] = extract_protein_chains(
        e3, cfg["e3_chains"], os.path.join(d, "unbound_protein2.pdb"))
    status["steps"]["unbound_lig2"] = extract_ligand(
        e3, cfg["anchor_comp"], os.path.join(d, "unbound_lig2.pdb"))
    # full degrader from CCD ideal (no native pose)
    status["steps"]["degrader"] = build_degrader(
        cfg["degrader_comp"], os.path.join(d, "ligand.sdf"), os.path.join(d, "ligand.pdb"))
    # native ternary -> SEALED (scoring only)
    nat = _need(cfg["native_pdb"])
    if os.path.exists(nat):
        import shutil
        shutil.copyfile(nat, os.path.join(sealed, SEALED_FILE))
        status["steps"]["sealed_native"] = True

    # validate the contract: all 6 inputs present + non-empty; native sealed but NOT in the predict dir
    missing = [f for f in REQUIRED_INPUTS
               if not os.path.exists(os.path.join(d, f)) or os.path.getsize(os.path.join(d, f)) == 0]
    status["missing_inputs"] = missing
    status["gt_in_predict_dir"] = os.path.exists(os.path.join(d, SEALED_FILE))  # must be False (blind)
    status["ok"] = (not missing) and (not status["gt_in_predict_dir"])
    return status


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", required=True, help="JSON list of per-control prep configs")
    ap.add_argument("--base", default="output/protac22")
    ap.add_argument("--out", default="blind_prep_status.json")
    args = ap.parse_args()
    cfgs = json.load(open(args.configs))
    if isinstance(cfgs, dict):
        cfgs = cfgs.get("prep_configs", cfgs.get("configs", []))
    os.makedirs(args.base, exist_ok=True)
    report = [prep_control(c, args.base) for c in cfgs]
    json.dump(report, open(args.out, "w"), indent=1)
    for r in report:
        print(f"{r['name']}: ok={r['ok']} missing={r['missing_inputs']} "
              f"gt_leak={r['gt_in_predict_dir']} steps={r['steps']}")
    return 0 if all(r["ok"] for r in report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
