#!/usr/bin/env python3
"""Re-check the VHL arm's staging structure (9GIO) against the structural record — $0, CI-only.

WHY THIS EXISTS. The RUNG-5a E3 downselect advanced **CRBN + VHL**, and the VHL row was scored on **9GIO**
with ligand CCD **3JF**. A manuscript-consolidation pass then noticed that the structural record describes
9GIO as carrying "a covalent compound bound to C77 of VHL" rather than a VH032-class hydroxyproline-pocket
handle, with an attributed fpocket druggability of **0.001**. Those two readings cannot both be right, and
the difference is not cosmetic:

  * a **hydroxyproline-pocket** handle is the canonical VHL recruiter chemistry (VH032/VH298 class). Its exit
    vector is the thing every VHL PROTAC linker leaves from, so an exit vector measured there is meaningful.
  * a **covalent adduct at Cys77** is a different site with a different vector. Ligandability and exit-vector
    numbers measured on it would not describe the recruiter pocket a degrader would actually use.

WHAT THIS DOES NOT AFFECT, stated up front so the result is not over-read: the reported orientation-basin
result consumed **5T35 / 8R5H**, not 9GIO, and the transfer-anchor validation is against 8R5H's observed
UBE2R2 catalytic cysteine (30.76 A, reproduced to 0.09 A). So this cannot move the Tier-2 verdict. What it
can move is the **downselect** — the ligandability + interface-geometry comparison that chose which two
recruiters advance, and in which **BIRC2** was logged as the first drop worth revisiting (tier-3 verified,
best resolution 1.249 A, openness within 0.04 of CRBN).

METHOD. Pure stdlib `urllib` against the RCSB data API (the dev sandbox's egress proxy 403s RCSB, so this
runs on a CI runner). For each ligand instance in 9GIO we take the deposited coordinates, find every polymer
residue with a heavy atom within 4.5 A, and report:
  * which entity/chain the lining residues belong to (is the ligand even on VHL?);
  * whether **Cys77 of VHL** is in that lining, and the closest approach to its S-gamma;
  * whether the canonical hydroxyproline-pocket residues are in that lining;
  * the same measurements on **5T35** (MZ1) as a positive control, since that is the structure the basin
    result actually consumed and is known-good.
A claim is only made where the coordinates support it; anything unfetched is reported as unfetched.
"""
from __future__ import annotations

import json
import math
import os
import sys
import urllib.error
import urllib.request

RCSB_ENTRY = "https://data.rcsb.org/rest/v1/core/entry/{}"
RCSB_NONPOLY = "https://data.rcsb.org/rest/v1/core/nonpolymer_entity/{}/{}"
RCSB_POLY = "https://data.rcsb.org/rest/v1/core/polymer_entity/{}/{}"
CIF = "https://files.rcsb.org/download/{}.cif"

# VHL residue numbering is UniProt P40337. The canonical recruiter pocket (VH032/VH298 class) buries the
# ligand's hydroxyproline against these; Cys77 is the reactive residue a covalent VHL binder would target.
VHL_HYP_POCKET = {97, 98, 99, 100, 101, 106, 107, 108, 109, 110, 111, 112, 115, 117}
VHL_CYS77 = 77
CONTACT_A = 4.5


def _get(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers-e3-recheck/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.read()


def _get_json(url: str):
    try:
        return json.loads(_get(url).decode())
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {"_fetch_error": f"{type(exc).__name__}: {exc}"}


def parse_cif_atoms(text: str):
    """Minimal mmCIF atom_site reader. Returns list of dicts. Pure stdlib, loop_-aware."""
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "loop_":
            j = i + 1
            cols = []
            while j < len(lines) and lines[j].strip().startswith("_atom_site."):
                cols.append(lines[j].strip().split(".", 1)[1])
                j += 1
            if cols:
                idx = {c: k for k, c in enumerate(cols)}
                need = ("group_PDB", "label_atom_id", "label_comp_id", "label_asym_id",
                        "auth_asym_id", "auth_seq_id", "Cartn_x", "Cartn_y", "Cartn_z", "type_symbol")
                if all(n in idx for n in need):
                    while j < len(lines):
                        ln = lines[j]
                        if ln.startswith("#") or ln.strip() == "" or ln.strip() == "loop_":
                            break
                        f = ln.split()
                        if len(f) < len(cols):
                            j += 1
                            continue
                        try:
                            out.append({
                                "group": f[idx["group_PDB"]],
                                "atom": f[idx["label_atom_id"]].strip('"'),
                                "comp": f[idx["label_comp_id"]],
                                "asym": f[idx["label_asym_id"]],
                                "auth_asym": f[idx["auth_asym_id"]],
                                "auth_seq": f[idx["auth_seq_id"]],
                                "elem": f[idx["type_symbol"]],
                                "xyz": (float(f[idx["Cartn_x"]]), float(f[idx["Cartn_y"]]),
                                        float(f[idx["Cartn_z"]])),
                            })
                        except (ValueError, IndexError):
                            pass
                        j += 1
                    i = j
                    continue
            i = j
            continue
        i += 1
    return out


def _d(a, b):
    return math.dist(a, b)


def lining_of(atoms, ligand_comp: str):
    """Polymer residues with a heavy atom within CONTACT_A of any ligand heavy atom."""
    lig = [a for a in atoms if a["group"] == "HETATM" and a["comp"] == ligand_comp and a["elem"] != "H"]
    if not lig:
        return None
    poly = [a for a in atoms if a["group"] == "ATOM" and a["elem"] != "H"]
    lining = {}
    for p in poly:
        best = min((_d(p["xyz"], l["xyz"]) for l in lig), default=1e9)
        if best <= CONTACT_A:
            key = (p["auth_asym"], p["auth_seq"], p["comp"])
            lining[key] = min(lining.get(key, 1e9), round(best, 2))
    # closest approach to any Cys SG, whichever chain
    sg = [a for a in poly if a["comp"] == "CYS" and a["atom"] == "SG"]
    cys = []
    for s in sg:
        best = min((_d(s["xyz"], l["xyz"]) for l in lig), default=1e9)
        cys.append((round(best, 2), s["auth_asym"], s["auth_seq"]))
    cys.sort()
    return {"n_ligand_heavy": len(lig), "lining": lining, "nearest_cys_sg": cys[:5]}


def analyse(pdb_id: str, expect_ccd: str | None = None):
    rec = {"pdb_id": pdb_id, "expected_ccd": expect_ccd}
    entry = _get_json(RCSB_ENTRY.format(pdb_id))
    if "_fetch_error" in entry:
        rec["_fetch_error"] = entry["_fetch_error"]
        return rec
    rec["title"] = (entry.get("struct") or {}).get("title")
    rec["resolution_A"] = ((entry.get("rcsb_entry_info") or {}).get("resolution_combined") or [None])[0]
    rec["nonpolymer_ids"] = (entry.get("rcsb_entry_container_identifiers") or {}).get(
        "non_polymer_entity_ids") or []
    rec["polymer_names"] = []
    for pid in ((entry.get("rcsb_entry_container_identifiers") or {}).get("polymer_entity_ids") or []):
        pe = _get_json(RCSB_POLY.format(pdb_id, pid))
        nm = ((pe.get("rcsb_polymer_entity") or {}).get("pdbx_description"))
        rec["polymer_names"].append({"entity": pid, "name": nm,
                                     "chains": (pe.get("rcsb_polymer_entity_container_identifiers") or {})
                                     .get("auth_asym_ids")})
    ligs = []
    for nid in rec["nonpolymer_ids"]:
        ne = _get_json(RCSB_NONPOLY.format(pdb_id, nid))
        comp = (ne.get("pdbx_entity_nonpoly") or {}).get("comp_id")
        ligs.append({"entity": nid, "ccd": comp,
                     "name": (ne.get("pdbx_entity_nonpoly") or {}).get("name")})
    rec["ligands"] = ligs

    try:
        cif = _get(CIF.format(pdb_id)).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        rec["_cif_error"] = f"{type(exc).__name__}: {exc}"
        return rec
    atoms = parse_cif_atoms(cif)
    rec["n_atoms_parsed"] = len(atoms)
    rec["per_ligand"] = {}
    for lg in ligs:
        ccd = lg["ccd"]
        if not ccd or ccd in ("HOH", "DOD"):
            continue
        info = lining_of(atoms, ccd)
        if not info:
            continue
        lining = info["lining"]
        chains = sorted({k[0] for k in lining})
        # which polymer is it on?
        chain_names = {}
        for pn in rec["polymer_names"]:
            for ch in (pn.get("chains") or []):
                chain_names[ch] = pn["name"]
        on = sorted({chain_names.get(c, f"chain {c}") for c in chains})
        seqs = {int(k[1]) for k in lining if k[1].lstrip("-").isdigit()}
        rec["per_ligand"][ccd] = {
            "n_ligand_heavy": info["n_ligand_heavy"],
            "n_lining_residues": len(lining),
            "lining_chains": chains,
            "lining_polymers": on,
            "hyp_pocket_overlap": sorted(seqs & VHL_HYP_POCKET),
            "n_hyp_pocket_overlap": len(seqs & VHL_HYP_POCKET),
            "cys77_in_lining": VHL_CYS77 in seqs,
            "nearest_cys_sg_A": info["nearest_cys_sg"],
        }
    return rec


def main():
    out_dir = os.environ.get("OUTPUT_DIR") or os.path.dirname(os.path.abspath(__file__))
    targets = [("9GIO", "3JF"), ("5T35", None)]
    res = {
        "_title": "VHL arm staging re-check — is 9GIO's ligand in the recruiter pocket or on Cys77?",
        "_why": "The E3 downselect scored VHL on 9GIO. If its ligand is a covalent adduct at Cys77 rather "
                "than a hydroxyproline-pocket handle, the ligandability and exit-vector numbers describe a "
                "site no VHL degrader linker would leave from. 5T35 (MZ1) is the positive control and is the "
                "structure the reported basin result actually consumed.",
        "_method": f"RCSB data API + deposited mmCIF; polymer residues with a heavy atom within {CONTACT_A} A "
                   "of a ligand heavy atom. Pure stdlib.",
        "_limits": [
            "Contact lining is geometry, not an energetic assessment of ligandability.",
            "A covalent linkage is inferred from proximity to a Cys SG, not read from struct_conn.",
            "This CANNOT move the Tier-2 verdict: that result consumed 5T35/8R5H, not 9GIO.",
        ],
        "entries": {},
    }
    for pdb, ccd in targets:
        print(f"[recheck] fetching {pdb} ...", flush=True)
        res["entries"][pdb] = analyse(pdb, ccd)

    g = res["entries"].get("9GIO", {}).get("per_ligand", {})
    verdict = {}
    for ccd, info in g.items():
        on_vhl = any("hippel" in (p or "").lower() or "vhl" in (p or "").lower()
                     for p in info["lining_polymers"])
        verdict[ccd] = {
            "on_VHL": on_vhl,
            "in_hydroxyproline_pocket": info["n_hyp_pocket_overlap"] >= 3,
            "n_hyp_pocket_residues_contacted": info["n_hyp_pocket_overlap"],
            "contacts_Cys77": info["cys77_in_lining"],
            "nearest_cys_sg_A": (info["nearest_cys_sg_A"] or [[None]])[0],
        }
    res["verdict_9GIO"] = verdict
    path = os.path.join(out_dir, "e3-vhl-ligand-recheck.json")
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1)[:4000])
    print(f"[recheck] wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
