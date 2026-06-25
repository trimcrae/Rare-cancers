#!/usr/bin/env python3
"""
Structure-based target assessment for the EWSR1::NR4A3 oncoprotein of EMC.

What this does (all from REAL, downloadable data — nothing here is invented):

  1. Downloads the AlphaFold2 (AFDB) monomer models for:
        - NR4A3 / NOR-1   (UniProt Q92570)   -- the fusion's DNA-binding + ligand-binding portion
        - EWSR1           (UniProt Q01844)   -- the fusion's N-terminal transactivation portion
  2. Reads per-residue pLDDT (AlphaFold confidence, stored in the B-factor column)
     and summarises it per functional region. Low pLDDT over a region is AlphaFold's
     own signal that the region is intrinsically disordered / has no single fold —
     which is exactly the expectation for the EWSR1 SYGQ-rich prion-like domain that
     drives the fusion's aberrant transactivation. We quantify it rather than assert it.
  3. Runs fpocket (open-source cavity detector) on the NR4A3 model and reports every
     detected pocket with its druggability score, so we can ask the central
     small-molecule question objectively: does the NR4A3 ligand-binding domain present
     a tractable pocket, or is it (like its Nurr1/Nur77 paralogues) an "atypical",
     autorepressed LBD with the canonical pocket occluded?

Output: nr4a3-structure-assessment.json  (machine-readable; consumed by the manuscript)

Domain boundaries below come from UniProt/InterPro feature annotations for the two
proteins and are cited in the manuscript. They are approximate region windows used
only to *summarise* a per-residue quantity (pLDDT); no boundary is asserted as a
precise breakpoint.
"""

import json
import os
import subprocess
import sys
import urllib.request

import fpocket_lib as fl

OUT = os.path.join(os.path.dirname(__file__), "nr4a3-structure-assessment.json")

AFDB_API = "https://alphafold.ebi.ac.uk/api/prediction/{acc}"

# UniProt accessions
NR4A3 = "Q92570"   # NOR-1 / NR4A3, human canonical
EWSR1 = "Q01844"   # EWSR1, human canonical


def fetch_pdb(acc, dest):
    """Resolve the model URL via the AFDB API (robust to version changes), then download."""
    api = AFDB_API.format(acc=acc)
    print(f"  resolving AFDB entry {api}")
    with urllib.request.urlopen(api, timeout=60) as r:
        data = json.load(r)
    if not data:
        raise RuntimeError(f"AFDB has no prediction for {acc}")
    url = data[0].get("pdbUrl")
    if not url:
        raise RuntimeError(f"AFDB entry for {acc} has no pdbUrl")
    print(f"  downloading {url}")
    urllib.request.urlretrieve(url, dest)
    return dest

# Approximate functional regions (UniProt feature view; 1-based inclusive).
# Used ONLY to average per-residue pLDDT over a region.
NR4A3_REGIONS = {
    "AF1/N-terminal (disordered)": (1, 260),
    "DNA-binding domain (zinc fingers)": (261, 337),
    "hinge": (338, 372),
    "ligand-binding domain": (373, 626),
}
EWSR1_REGIONS = {
    "SYGQ-rich transactivation / prion-like (N-term)": (1, 264),
    "RNA-recognition motif (RRM)": (361, 442),
    "RGG/zinc-finger C-terminal": (443, 656),
}


def per_residue_plddt(pdb_path):
    """AlphaFold stores pLDDT in the B-factor column; one value per residue."""
    plddt = {}
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith("ATOM"):
                continue
            if line[12:16].strip() != "CA":
                continue
            resseq = int(line[22:26])
            b = float(line[60:66])
            plddt[resseq] = b
    return plddt


def region_summary(plddt, regions):
    out = {}
    for name, (lo, hi) in regions.items():
        vals = [plddt[r] for r in range(lo, hi + 1) if r in plddt]
        if not vals:
            out[name] = {"residues": f"{lo}-{hi}", "n": 0}
            continue
        mean = sum(vals) / len(vals)
        # AFDB pLDDT bands: >90 very high, 70-90 confident, 50-70 low, <50 very low (often disordered)
        frac_disordered = sum(1 for v in vals if v < 50) / len(vals)
        out[name] = {
            "residues": f"{lo}-{hi}",
            "n": len(vals),
            "mean_pLDDT": round(mean, 1),
            "frac_pLDDT_below_50": round(frac_disordered, 3),
            "interpretation": _band(mean),
        }
    return out


def _band(mean):
    if mean >= 90:
        return "very high confidence (well-ordered fold)"
    if mean >= 70:
        return "confident (ordered)"
    if mean >= 50:
        return "low confidence"
    return "very low confidence (predicted intrinsically disordered)"


def _domain_of(resid, regions):
    for name, (lo, hi) in regions.items():
        if lo <= resid <= hi:
            return name
    return "outside annotated regions"


def _read(path):
    with open(path) as fh:
        return fh.read()


def pocket_residues_by_number(out_dir, stem_base):
    """{pocket_number(1-based): sorted[resid]} with the residue-file -> pocket mapping DERIVED from
    the data via fpocket_lib (alpha-sphere fingerprints), not assumed from the filename. This is the
    fix for the off-by-one that previously read pocket{N}_atm.pdb for "Pocket N" and mis-attributed
    residues. Returns (residues_by_number, parsed_info)."""
    import glob
    import re
    info = fl.parse_info(_read(os.path.join(out_dir, stem_base + "_info.txt")))
    out_pdb = os.path.join(out_dir, stem_base + "_out.pdb")
    out_coords = fl.out_pdb_sphere_coords(_read(out_pdb)) if os.path.exists(out_pdb) else {}
    file_res, counts, coords = {}, {}, {}
    for f in glob.glob(os.path.join(out_dir, "pockets", "pocket*_atm.pdb")):
        fidx = int(re.search(r"pocket(\d+)_atm", f).group(1))
        file_res[fidx] = fl.parse_atm_residues(_read(f))
        vert = os.path.join(out_dir, "pockets", f"pocket{fidx}_vert.pqr")
        c = fl.pqr_sphere_coords(_read(vert)) if os.path.exists(vert) else frozenset()
        coords[fidx], counts[fidx] = c, len(c)
    mapping = fl.map_files_to_pockets(info, counts, coords, out_coords)   # raises on ambiguity
    return {mapping[fidx]: res for fidx, res in file_res.items()}, info


def run_fpocket(pdb_path, regions):
    """Run fpocket; report per-pocket druggability and localise the top pocket to a domain, with the
    residue<->pocket mapping derived from data (fpocket_lib), not assumed."""
    try:
        subprocess.run(["fpocket", "-f", pdb_path], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        print("  fpocket not installed; skipping pocket detection", file=sys.stderr)
        return {"available": False, "pockets": []}
    except subprocess.CalledProcessError as e:
        print("  fpocket failed:", e.stderr, file=sys.stderr)
        return {"available": False, "pockets": []}

    stem = pdb_path[:-4] if pdb_path.endswith(".pdb") else pdb_path
    out_dir, stem_base = stem + "_out", os.path.basename(stem)
    resids_by_num, info = pocket_residues_by_number(out_dir, stem_base)

    pockets = [{"pocket": f"Pocket {num}", "druggability": meta["druggability"],
                "alpha_spheres": meta["alpha_spheres"],
                "n_lining_residues": len(resids_by_num.get(num, []))}
               for num, meta in info.items()]
    pockets.sort(key=lambda p: (p.get("druggability") or 0), reverse=True)

    top_locale = None
    if pockets:
        topnum = int(pockets[0]["pocket"].split()[-1])
        resids = resids_by_num.get(topnum, [])
        if resids:
            from collections import Counter
            doms = Counter(_domain_of(r, regions) for r in resids)
            top_locale = {
                "pocket": pockets[0]["pocket"],
                "druggability": pockets[0]["druggability"],
                "resid_min": resids[0], "resid_max": resids[-1],
                "n_lining_residues": len(resids),
                "domain_distribution": dict(doms),
                "dominant_domain": doms.most_common(1)[0][0],
            }
    return {"available": True, "n_pockets": len(pockets), "top_pocket_locale": top_locale,
            "pockets": pockets, "pocket_residues": resids_by_num}


def assess(acc, regions, with_fpocket):
    """Fetch + analyse one protein; never raises (records an error instead)."""
    work = os.environ.get("RUNNER_TEMP", "/tmp")
    try:
        pdb = fetch_pdb(acc, os.path.join(work, f"AF-{acc}.pdb"))
        plddt = per_residue_plddt(pdb)
        out = {
            "uniprot": acc,
            "length": max(plddt) if plddt else None,
            "regions": region_summary(plddt, regions),
        }
        if with_fpocket:
            out["fpocket"] = run_fpocket(pdb, regions)
            best = (out["fpocket"]["pockets"] or [{}])[0]
            out["top_pocket_druggability"] = best.get("druggability")
        return out
    except Exception as e:  # noqa: BLE001 — keep the pipeline alive, surface the error in JSON
        print(f"  ERROR assessing {acc}: {e}", file=sys.stderr)
        return {"uniprot": acc, "error": str(e)}


def main():
    result = {
        "_note": "AlphaFold2 (AFDB) confidence + fpocket cavity analysis. "
                 "pLDDT is AlphaFold's per-residue confidence; <50 typically marks "
                 "intrinsic disorder. Druggability score is fpocket's 0-1 estimate "
                 "(>0.5 commonly considered druggable).",
        "NR4A3": assess(NR4A3, NR4A3_REGIONS, with_fpocket=True),
        "EWSR1": assess(EWSR1, EWSR1_REGIONS, with_fpocket=False),
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
