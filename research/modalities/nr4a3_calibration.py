#!/usr/bin/env python3
"""
fpocket calibration / sanity panel — does our pocket pipeline over-call NR4A3 druggability?

MOTIVATION. Our AF2 NR4A3 orthosteric pocket scores fpocket druggability 0.495 (borderline). A
reviewer (rightly) asks: is that number trustworthy, given NR4A receptors are "undruggable", and given
our same pipeline reported a 0.80 *top* pocket for Nurr1/NR4A2 (whose classical pocket is famously
occluded)? This panel calibrates the pipeline against ground truth so the 0.495 is interpretable in
absolute terms, and localizes that 0.80.

It runs the SAME fpocket pipeline on a panel of nuclear-receptor LBDs and reports, per structure:
  - every pocket's druggability + alpha-sphere count + lining-residue span,
  - the MAX druggability anywhere on the structure,
  - for holo structures, the druggability of the pocket that actually overlaps the BOUND LIGAND
    (found by alpha-sphere<->ligand-atom proximity) — i.e. the experimentally validated site.

Panel (all verified PDB IDs / UniProt accessions):
  AF2 models (our inputs):   NR4A3 Q92570, NR4A2 P43354 (Nurr1), NR4A1 P22736 (Nur77)
  NR4A crystals:             1OVL Nurr1 LBD apo, occluded/collapsed pocket (Wang 2003 Nature 423:555)
                             5Y41 Nurr1 LBD + prostaglandin-A1 (de Vera/Munoz-Tello; surface/Cys566)
                             4JGV Nur77 LBD + THPN (surface pocket)
  Druggable-NR controls:     2PRG PPARgamma LBD + rosiglitazone (classic large orthosteric pocket)
                             1ERE ERalpha LBD + 17beta-estradiol (classic orthosteric pocket)

Interpretation the panel enables:
  * Where does fpocket put a KNOWN druggable orthosteric NR pocket (PPARg/ERa ligand site)? That is the
    reference for "0.5 means druggable" in OUR hands.
  * Does our NR4A2 AF2 model over-call vs the 1OVL crystal (model max vs crystal max)?
  * Where do real NR4A ligands actually bind (holo ligand-site pockets) — classic orthosteric or
    surface/cryptic? (Bears on whether the cryptic-pocket route is the right framing.)

Output: nr4a3-calibration.json. CPU only (fpocket). Run via gpu-calibration-aws.yml.
"""
import json
import os
import subprocess
import sys

import fpocket_lib as fl
import pocket_tracking as pt   # harmonized, score-independent orthosteric-pocket tracking
from nr4a3_structure import fetch_pdb as fetch_afdb   # AFDB API resolver (reused)

POCKET5_LINING = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]  # fixed Pocket-5 lining (Q92570)

OUT = os.path.join(os.path.dirname(__file__), "nr4a3-calibration.json")
WORK = os.environ.get("RUNNER_TEMP", "/tmp")

# Non-ligand HETATM groups to ignore when picking "the bound ligand" (waters, ions, common buffers).
_NOT_LIGAND = {
    "HOH", "WAT", "DOD", "NA", "CL", "K", "MG", "CA", "ZN", "MN", "NI", "CD", "FE", "CO", "CU",
    "SO4", "PO4", "NO3", "CO3", "ACT", "FMT", "GOL", "EDO", "PEG", "PG4", "1PE", "2PE", "MPD",
    "DMS", "BME", "TRS", "EPE", "MES", "IOD", "BR", "IMD", "CAC", "FLC", "CIT", "TLA", "ACY",
}

PANEL = [
    {"id": "NR4A3_AF2_Q92570", "src": "afdb", "key": "Q92570", "category": "nr4a_model",
     "note": "our target NOR-1/NR4A3 LBD (AF2)"},
    {"id": "NR4A2_AF2_P43354", "src": "afdb", "key": "P43354", "category": "nr4a_model",
     "note": "Nurr1/NR4A2 LBD (AF2) — model whose top pocket scored 0.80"},
    {"id": "NR4A1_AF2_P22736", "src": "afdb", "key": "P22736", "category": "nr4a_model",
     "note": "Nur77/NR4A1 LBD (AF2)"},
    {"id": "NR4A2_1OVL", "src": "rcsb", "key": "1OVL", "category": "nr4a_crystal_apo",
     "note": "Nurr1 LBD apo, occluded pocket (Wang 2003)"},
    {"id": "NR4A2_5Y41", "src": "rcsb", "key": "5Y41", "category": "nr4a_crystal_holo",
     "note": "Nurr1 LBD + prostaglandin-A1"},
    {"id": "NR4A1_4JGV", "src": "rcsb", "key": "4JGV", "category": "nr4a_crystal_holo",
     "note": "Nur77 LBD + THPN"},
    {"id": "PPARG_2PRG", "src": "rcsb", "key": "2PRG", "category": "druggable_control_holo",
     "note": "PPARgamma LBD + rosiglitazone (known druggable orthosteric pocket)"},
    {"id": "ERA_1ERE", "src": "rcsb", "key": "1ERE", "category": "druggable_control_holo",
     "note": "ERalpha LBD + 17beta-estradiol (known druggable orthosteric pocket)"},
]


def fetch_rcsb(pdb_id, dest):
    import urllib.request
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    print(f"  downloading {url}", flush=True)
    urllib.request.urlretrieve(url, dest)
    return dest


def _read(path):
    with open(path) as fh:
        return fh.read()


def ligand_atoms(pdb_path):
    """Coords of the largest non-solvent HETATM group = the bound ligand. Returns (resname, [(x,y,z)])
    or (None, [])."""
    groups = {}
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith("HETATM"):
                continue
            resn = line[17:20].strip()
            if resn in _NOT_LIGAND or line[76:78].strip() == "H":
                continue
            key = (resn, line[21:22], line[22:26])
            try:
                xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
            except ValueError:
                continue
            groups.setdefault(key, []).append(xyz)
    if not groups:
        return None, []
    key = max(groups, key=lambda k: len(groups[k]))
    return key[0], groups[key]


def fpocket_pockets(pdb_path):
    """Run fpocket; return [{pocket, druggability, alpha_spheres, residues, sphere_coords}] with the
    file->pocket mapping derived from data (fpocket_lib), plus alpha-sphere coords for ligand overlap."""
    subprocess.run(["fpocket", "-f", pdb_path], check=True, capture_output=True, text=True)
    import glob
    import re
    stem = pdb_path[:-4] if pdb_path.endswith(".pdb") else pdb_path
    out_dir, base = stem + "_out", os.path.basename(stem)
    info = fl.parse_info(_read(os.path.join(out_dir, base + "_info.txt")))
    out_pdb = os.path.join(out_dir, base + "_out.pdb")
    out_coords = fl.out_pdb_sphere_coords(_read(out_pdb)) if os.path.exists(out_pdb) else {}
    file_res, counts, coords = {}, {}, {}
    for f in glob.glob(os.path.join(out_dir, "pockets", "pocket*_atm.pdb")):
        fidx = int(re.search(r"pocket(\d+)_atm", f).group(1))
        file_res[fidx] = fl.parse_atm_residues(_read(f))
        vert = os.path.join(out_dir, "pockets", f"pocket{fidx}_vert.pqr")
        vtext = _read(vert) if os.path.exists(vert) else ""
        coords[fidx] = fl.pqr_sphere_coords(vtext)
        counts[fidx] = fl.count_pqr_spheres(vtext)
    mapping = fl.map_files_to_pockets(info, counts, coords, out_coords)
    pockets = []
    for fidx, num in mapping.items():
        res = file_res[fidx]
        pockets.append({
            "pocket": num,
            "druggability": info[num]["druggability"],
            "alpha_spheres": info[num]["alpha_spheres"],
            "n_lining_residues": len(res),
            "resid_span": [res[0], res[-1]] if res else None,
            "residues": res,                       # full lining set (for the harmonized Pocket-5 match)
            "sphere_coords": coords[fidx],
        })
    pockets.sort(key=lambda p: (p["druggability"] or 0.0), reverse=True)
    return pockets


def ligand_site(pockets, lig_xyz, cutoff=4.5):
    """The pocket whose alpha-spheres most overlap the bound ligand (>=1 sphere within `cutoff` A of a
    ligand atom). Returns (pocket_dict, n_spheres_near) or (None, 0)."""
    if not lig_xyz:
        return None, 0
    c2 = cutoff * cutoff
    best, best_n = None, 0
    for p in pockets:
        n = 0
        for (sx, sy, sz) in p["sphere_coords"]:
            for (lx, ly, lz) in lig_xyz:
                if (sx - lx) ** 2 + (sy - ly) ** 2 + (sz - lz) ** 2 <= c2:
                    n += 1
                    break
        if n > best_n:
            best, best_n = p, n
    return best, best_n


def _brief(p):
    return None if p is None else {"pocket": p["pocket"], "druggability": p["druggability"],
                                   "alpha_spheres": p["alpha_spheres"],
                                   "resid_span": p["resid_span"]}


def assess(entry):
    try:
        dest = os.path.join(WORK, f"{entry['id']}.pdb")
        if entry["src"] == "afdb":
            fetch_afdb(entry["key"], dest)
        else:
            fetch_rcsb(entry["key"], dest)
        pockets = fpocket_pockets(dest)
        out = {
            "id": entry["id"], "category": entry["category"], "source": entry["src"],
            "key": entry["key"], "note": entry["note"],
            "n_pockets": len(pockets),
            "max_druggability": pockets[0]["druggability"] if pockets else None,
            "top_pocket": _brief(pockets[0]) if pockets else None,
            "all_pockets": [_brief(p) for p in pockets],
        }
        # For OUR NR4A3 AF2 target, additionally report the score-INDEPENDENT fixed-Pocket-5 match
        # (identity by the composite gate, not by druggability rank) so the calibration is homogeneous
        # with the harmonized main pipeline.
        if entry["key"] == "Q92570" and entry["src"] == "afdb":
            ca = {}
            with open(dest) as fh:
                for line in fh:
                    if line.startswith("ATOM") and line[12:16].strip() == "CA":
                        try:
                            ca[int(line[22:26])] = (float(line[30:38]), float(line[38:46]),
                                                    float(line[46:54]))
                        except ValueError:
                            pass
            try:
                ref = pt.orthosteric_reference(ca, lining_residues=POCKET5_LINING, span=pt.POCKET5_SPAN)
                hit = pt.match_pocket(pockets, ref, ca_by_resnum=ca, **pt.match_params())
                out["harmonized_pocket5_match"] = {
                    "match_mode": pt.match_mode(),
                    "matched_pocket": None if hit is None else hit["pocket"],
                    "matched_druggability": None if hit is None else hit["druggability"],
                    "match_metrics": None if hit is None else hit["_match"],
                }
            except ValueError as e:
                out["harmonized_pocket5_match"] = {"error": str(e)[:200]}
        resn, lig = ligand_atoms(dest)
        if lig:
            site, nnear = ligand_site(pockets, lig)
            out["bound_ligand"] = resn
            out["ligand_site_pocket"] = _brief(site)
            out["ligand_site_spheres_near"] = nnear
            out["ligand_site_druggability"] = site["druggability"] if site else None
        else:
            out["bound_ligand"] = None
        dscore = out.get("ligand_site_druggability")
        print(f"  {entry['id']:18s} max={out['max_druggability']} "
              f"ligand_site={dscore} ({out.get('bound_ligand')})", flush=True)
        return out
    except Exception as e:  # noqa: BLE001 — record, keep the panel alive
        print(f"  ERROR {entry['id']}: {e}", file=sys.stderr, flush=True)
        return {"id": entry["id"], "category": entry["category"], "key": entry["key"],
                "error": str(e)[:300]}


def main():
    results = [assess(e) for e in PANEL]

    def by_cat(cat, field):
        return {r["id"]: r.get(field) for r in results if r.get("category") == cat and "error" not in r}

    summary = {
        "fpocket_version": pt.resolved_fpocket_version(),
        "pocket_match_mode": pt.match_mode(),
        "_note": ("fpocket calibration panel. 'ligand_site_druggability' is the fpocket score of the "
                  "pocket overlapping the experimentally bound ligand (the validated site); for the "
                  "druggable controls (PPARg 2PRG, ERa 1ERE) this is a KNOWN-druggable orthosteric NR "
                  "pocket and sets the reference for what >=0.5 means in our pipeline. Compare the "
                  "NR4A2 AF2 model max vs the 1OVL crystal max to gauge model over-call. Same fpocket "
                  "and file->pocket mapping (fpocket_lib) as the main pipeline."),
        "references": {
            "1OVL": "Wang Z et al., Nature 423:555-560 (2003) — Nurr1 LBD, no canonical pocket",
            "5Y41/5YD6/6DDA": "Nurr1 LBD + prostaglandin-A1 / 5,6-dihydroxyindole co-crystals",
            "de Vera 2019": "de Vera IMS et al., Structure 27(1):66-77 (2019) — Nurr1 pocket is dynamic, "
                            "expands from the collapsed crystal conformation to bind fatty acids",
            "4JGV": "Nur77/NR4A1 LBD + THPN; 6KZ5 + cytosporone-B (surface pockets)",
            "2PRG": "Nolte RT et al., PPARgamma LBD + rosiglitazone",
            "1ERE": "Brzozowski AM et al., Nature 389:753 (1997), ERalpha LBD + 17beta-estradiol",
        },
        "druggable_control_ligand_site": by_cat("druggable_control_holo", "ligand_site_druggability"),
        "nr4a_model_max": by_cat("nr4a_model", "max_druggability"),
        "nr4a_crystal_apo_max": by_cat("nr4a_crystal_apo", "max_druggability"),
        "nr4a_crystal_holo_ligand_site": by_cat("nr4a_crystal_holo", "ligand_site_druggability"),
        "nr4a3_orthosteric_static_af2": 0.495,
        "results": results,
    }
    with open(OUT, "w") as fh:
        json.dump(summary, fh, indent=2)
    print("\nwrote", OUT, flush=True)
    print(json.dumps({k: summary[k] for k in (
        "druggable_control_ligand_site", "nr4a_model_max", "nr4a_crystal_apo_max",
        "nr4a_crystal_holo_ligand_site", "nr4a3_orthosteric_static_af2")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
