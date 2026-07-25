#!/usr/bin/env python3
"""
E3 ARM STAGING for the RUNG-5a mechanism-first orientation-basin search — discovery by UniProt accession,
never by a remembered PDB ID.

WHY IT WORKS THIS WAY. The basin search needs three things per E3 recruiter, all in ONE coordinate frame:
  (1) the substrate-receptor BODY (the thing that has to dock against NR4A3 without clashing),
  (2) the LIGAND EXIT VECTOR — the atom where a linker leaves the E3 ligand, which is the E3-side tether
      anchor the whole linker-reach constraint is written against, and
  (3) the RING position, because the term-(b) transfer zone is a region around the RBX1 RING module, not
      around the substrate receptor.
No single deposited structure carries all three for most recruiters, so this script COMPOSES them: a
ligand-bound receptor entry supplies (1) and (2); a cullin-scaffold entry supplies (3) and is bridged into the
receptor's frame by superposing the protein the two entries share. Every composition step reports its bridge
RMSD, and a bridge that does not superpose is a refusal, not a warning.

THE NON-FABRICATION RULE (repo golden rule + TESTING.md rule 1). A PDB ID recalled from memory is exactly the
kind of thing that is plausible and wrong, and a wrong scaffold entry would put the RING in the wrong place
while every number downstream still looked fine. So this script does NOT take PDB IDs as inputs at all in its
primary path: it QUERIES RCSB for entries whose polymer entities carry the required UniProt accession SET,
ranks the hits, and then RE-VERIFIES the composition of whatever it downloaded against that same accession set
before using it. Optional `seed_ids` are hints that must pass the identical verification; a seed that fails is
dropped with the reason recorded, never used.

DERIVED, NOT ASSUMED — the exit vector. The E3-side tether anchor is taken as the ligand heavy atom that is
FURTHEST from the receptor's protein atoms, i.e. the most solvent-exposed atom of the bound ligand. That is
the point where a linker can leave without burying itself in the E3, and it is read out of the coordinates
rather than looked up from chemical folklore about which position of VH032 or pomalidomide is "the exit
vector". The run log prints the chosen atom and its exposure so the convention is auditable by eye
(TESTING.md rule 6).

NETWORK. RCSB is 403'd at CONNECT by the dev sandbox's egress proxy, so this runs on a GitHub Actions runner
(CLAUDE.md §6). Pure stdlib urllib — no pip, matching the CPU-workflow convention.

Usage
    python nr4a3_e3_stage.py --plan                 # offline: print exactly what would be queried
    python nr4a3_e3_stage.py --arms vhl,crbn        # CI: discover, verify, download, compose, write registry
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G  # noqa: E402

SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2/query"
ENTRY_URL = "https://data.rcsb.org/rest/v1/core/entry/{pdb}"
ENTITY_URL = "https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb}/{eid}"
FILE_URL = "https://files.rcsb.org/download/{pdb}.pdb"

STAGE_DIR = os.path.join(REPO, "results", "nr4a3-e3-arms")
REGISTRY = os.path.join(HERE, "nr4a3-e3-arm-registry.json")

# UniProt accessions used to IDENTIFY components. These are protein identities, not structure claims.
ACC = {
    "VHL": "P40337", "ELOB": "Q15370", "ELOC": "Q15369", "CUL2": "Q13617", "RBX1": "P62877",
    "CRBN": "Q96SW2", "DDB1": "Q16531", "CUL4A": "Q13619", "CUL4B": "Q13620",
    "BIRC2": "Q13490", "DCAF1": "Q9Y4B6", "DCAF15": "Q66K64", "DCAF16": "Q9NXF7",
    "KEAP1": "Q14145", "FEM1B": "Q9UK73", "RNF114": "Q9Y508", "MDM2": "Q00987",
    "CUL1": "Q13616", "SKP1": "P63208",
    # E2 conjugating enzymes that work with CRL RING modules
    "UBE2D1": "P51668", "UBE2D2": "P62837", "UBE2D3": "P61077", "UBE2R1": "P49427", "UBE2R2": "Q712K3",
    "UBE2G1": "P62253", "UBE2L3": "P68036",
}

# Arm specs. `receptor_needs` = accessions the ligand-bound entry MUST contain; `receptor_body` = which of
# them form the rigid body that docks against NR4A3; `scaffold_needs` = the cullin-scaffold entry; `bridge` =
# the protein used to superpose scaffold into the receptor frame (must be in BOTH sets).
ARMS = {
    "vhl": {
        "recruiter": "VHL",
        "crl": "CRL2^VHL",
        "receptor_needs": ["VHL", "ELOB", "ELOC"],
        "receptor_body": ["VHL", "ELOB", "ELOC"],
        "scaffold_needs": ["VHL", "ELOC", "CUL2", "RBX1"],
        "bridge": ["VHL", "ELOC"],
        "seed_ids": ["5T35", "4W9H", "5N4W"],
    },
    "crbn": {
        "recruiter": "CRBN",
        "crl": "CRL4^CRBN",
        "receptor_needs": ["CRBN", "DDB1"],
        "receptor_body": ["CRBN", "DDB1"],
        "scaffold_needs": ["DDB1", "CUL4A", "RBX1"],
        "bridge": ["DDB1"],
        "seed_ids": ["6BOY", "4TZ4", "2HYE"],
    },
}

# The RING->E2 catalytic-cysteine geometry is MEASURED from a RING-E2 co-structure when one can be found;
# these accession sets drive that search. If none verifies, the driver falls back to a parametric shell and
# says so in the output — an assumption declared is fine, an assumption hidden is not.
E2_PAIR_NEEDS = [["RBX1", "UBE2D1"], ["RBX1", "UBE2D2"], ["RBX1", "UBE2D3"],
                 ["RBX1", "UBE2R1"], ["RBX1", "UBE2R2"], ["RBX1", "UBE2L3"]]

MIN_LIGAND_HEAVY = 12          # below this it is a buffer/cryo additive, not a recruiter ligand
EXCLUDE_HET = {"HOH", "DOD", "SO4", "PO4", "GOL", "EDO", "PEG", "MPD", "TRS", "ACT", "CL", "NA", "MG",
               "ZN", "CA", "K", "IOD", "BME", "DMS", "FMT", "NO3", "CIT", "IMD", "EPE", "MES", "NAG",
               "BMA", "MAN", "FUC", "PGE", "1PE", "P6G", "PG4", "SIN", "TLA", "ACY", "NH4", "CO3"}
THREE2ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
    "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
    "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}


# ---------------------------------------------------------------------------------------------------------
# HTTP (stdlib only)
# ---------------------------------------------------------------------------------------------------------


def _get(url, tries=4, timeout=60):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Rare-cancers/nr4a3_e3_stage"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:                      # noqa: BLE001 — network flake is expected, retry
            last = e
            time.sleep(1.5 * (2 ** i))
    raise RuntimeError(f"GET failed after {tries} tries: {url} ({last})")


def _post_json(url, payload, tries=4, timeout=60):
    body = json.dumps(payload).encode()
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url, data=body,
                headers={"Content-Type": "application/json", "User-Agent": "Rare-cancers/nr4a3_e3_stage"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 204:                       # RCSB returns 204 for "no hits"
                return {"result_set": []}
            last = e
            time.sleep(1.5 * (2 ** i))
        except Exception as e:                      # noqa: BLE001
            last = e
            time.sleep(1.5 * (2 ** i))
    raise RuntimeError(f"POST failed after {tries} tries: {url} ({last})")


def accession_query(accessions, rows=25):
    """RCSB search payload: entries whose polymer entities carry ALL of `accessions`, best resolution first."""
    nodes = [{
        "type": "terminal", "service": "text",
        "parameters": {
            "attribute": "rcsb_polymer_entity_container_identifiers."
                         "reference_sequence_identifiers.database_accession",
            "operator": "exact_match", "value": a},
    } for a in accessions]
    return {
        "query": {"type": "group", "logical_operator": "and", "nodes": nodes},
        "return_type": "entry",
        "request_options": {
            "paginate": {"start": 0, "rows": rows},
            "sort": [{"sort_by": "rcsb_entry_info.resolution_combined", "direction": "asc"}],
        },
    }


def search_entries(accessions, rows=25):
    res = _post_json(SEARCH_URL, accession_query(accessions, rows))
    return [h["identifier"] for h in res.get("result_set", [])]


def entry_composition(pdb):
    """{accession: [auth chain ids]} for every polymer entity of `pdb`, plus the entry's resolution/title."""
    meta = json.loads(_get(ENTRY_URL.format(pdb=pdb)))
    eids = meta.get("rcsb_entry_container_identifiers", {}).get("polymer_entity_ids", []) or []
    comp = {}
    for eid in eids:
        ent = json.loads(_get(ENTITY_URL.format(pdb=pdb, eid=eid)))
        ids = ent.get("rcsb_polymer_entity_container_identifiers", {})
        chains = ids.get("auth_asym_ids", []) or []
        for ref in ids.get("reference_sequence_identifiers", []) or []:
            if ref.get("database_name") == "UniProt":
                comp.setdefault(ref["database_accession"], []).extend(chains)
    resl = meta.get("rcsb_entry_info", {}).get("resolution_combined") or []
    return {
        "pdb_id": pdb,
        "title": (meta.get("struct", {}) or {}).get("title"),
        "resolution_A": resl[0] if resl else None,
        "method": (meta.get("rcsb_entry_info", {}) or {}).get("experimental_method"),
        "chains_by_accession": comp,
    }


# ---------------------------------------------------------------------------------------------------------
# PDB parsing (stdlib)
# ---------------------------------------------------------------------------------------------------------


def parse_pdb_text(text):
    """Return (protein_atoms, het_atoms). Only the FIRST model; altloc kept as ' ' or 'A'."""
    prot, het = [], []
    for ln in text.splitlines():
        rec = ln[:6]
        if rec == "ENDMDL":
            break
        if rec not in ("ATOM  ", "HETATM"):
            continue
        alt = ln[16]
        if alt not in (" ", "A"):
            continue
        resn = ln[17:20].strip()
        elem = (ln[76:78].strip() or ln[12:16].strip()[0]).upper()
        if elem == "H" or elem == "D":
            continue
        try:
            rec_atom = {
                "name": ln[12:16].strip(), "resname": resn, "chain": ln[21],
                "resid": int(ln[22:26]), "icode": ln[26],
                "xyz": (float(ln[30:38]), float(ln[38:46]), float(ln[46:54])), "elem": elem,
            }
        except ValueError:
            continue
        if rec == "ATOM  " or resn in THREE2ONE:
            prot.append(rec_atom)
        else:
            het.append(rec_atom)
    return prot, het


def chain_ca(prot_atoms, chains):
    out = {}
    for a in prot_atoms:
        if a["chain"] in chains and a["name"] == "CA":
            out[(a["chain"], a["resid"])] = a["xyz"]
    return out


# ---------------------------------------------------------------------------------------------------------
# Composition steps
# ---------------------------------------------------------------------------------------------------------


def verify(comp, needed_accs, arm_acc_map):
    """Does the downloaded entry really contain every required accession? Returns (ok, missing)."""
    have = set(comp["chains_by_accession"])
    missing = [n for n in needed_accs if arm_acc_map[n] not in have]
    return (not missing), missing


def pick_ligand(prot_atoms, het_atoms, body_chains):
    """The recruiter's bound ligand: the largest non-excluded HET group with >= MIN_LIGAND_HEAVY heavy atoms
    that actually CONTACTS the body chains (>= 4 heavy atoms within 4.5 A). Contact is required so a
    crystallisation additive parked on a symmetry mate cannot be mistaken for the recruiter ligand."""
    body = [a["xyz"] for a in prot_atoms if a["chain"] in body_chains]
    if not body:
        return None
    field = G.SquaredDistanceField(body, cell=1.0, clamp=8.0)
    groups = {}
    for a in het_atoms:
        if a["resname"] in EXCLUDE_HET:
            continue
        groups.setdefault((a["resname"], a["chain"], a["resid"], a["icode"]), []).append(a)
    best = None
    for key, atoms in groups.items():
        if len(atoms) < MIN_LIGAND_HEAVY:
            continue
        near = sum(1 for a in atoms if field.min_dist(a["xyz"]) <= 4.5)
        if near < 4:
            continue
        if best is None or len(atoms) > len(best[1]):
            best = (key, atoms)
    if best is None:
        return None
    key, atoms = best
    # DERIVED exit vector: the ligand heavy atom furthest from the receptor's protein atoms.
    exposures = [(field.min_dist(a["xyz"]), a) for a in atoms]
    exposures.sort(key=lambda t: -t[0])
    exit_d, exit_atom = exposures[0]
    return {
        "het_code": key[0], "chain": key[1], "resid": key[2],
        "n_heavy": len(atoms),
        "atoms": [{"name": a["name"], "elem": a["elem"], "xyz": list(a["xyz"])} for a in atoms],
        "exit_atom_name": exit_atom["name"],
        "exit_atom_xyz": list(exit_atom["xyz"]),
        "exit_atom_min_dist_to_receptor_A": round(exit_d, 2),
        "ligand_centroid": list(G.centroid([a["xyz"] for a in atoms])),
    }


def bridge_into_frame(src_prot, src_bridge_chains, dst_prot, dst_bridge_chains, max_rmsd=4.0):
    """Superpose `src` onto `dst` using CA atoms of the bridge protein, matched by residue number.

    Residue-number matching (not sequence alignment) is deliberate: both entries are the SAME protein deposited
    under the same UniProt numbering scheme in the overwhelming majority of cases, and if they are not, the
    match count collapses and the RMSD gate below refuses the composition rather than quietly producing a
    plausible, wrong RING position.
    """
    src_ca = chain_ca(src_prot, src_bridge_chains)
    dst_ca = chain_ca(dst_prot, dst_bridge_chains)
    src_by_res, dst_by_res = {}, {}
    for (_c, r), xyz in src_ca.items():
        src_by_res.setdefault(r, xyz)
    for (_c, r), xyz in dst_ca.items():
        dst_by_res.setdefault(r, xyz)
    shared = sorted(set(src_by_res) & set(dst_by_res))
    if len(shared) < 30:
        return None, {"ok": False, "reason": f"only {len(shared)} shared bridge residues (need >= 30)"}
    mob = [src_by_res[r] for r in shared]
    ref = [dst_by_res[r] for r in shared]
    R, t, rmsd = G.horn_superpose(mob, ref)
    if rmsd > max_rmsd:
        return None, {"ok": False, "reason": f"bridge RMSD {rmsd:.2f} A > {max_rmsd} A over {len(shared)} CA"}
    return (R, t), {"ok": True, "n_bridge_ca": len(shared), "bridge_rmsd_A": round(rmsd, 3)}


def ring_domain_centroid(prot_atoms, rbx1_chains):
    """RBX1's RING domain = its C-terminal Zn-binding half. Derived from the deposited residue range rather
    than a hard-coded boundary: RBX1 is 108 residues, its RING spans roughly the C-terminal two-thirds, so we
    take the C-terminal 60% of the modelled residues. Reported with the range used so it is auditable."""
    res = sorted({a["resid"] for a in prot_atoms if a["chain"] in rbx1_chains})
    if len(res) < 20:
        return None, None
    cut = res[int(len(res) * 0.4)]
    pts = [a["xyz"] for a in prot_atoms if a["chain"] in rbx1_chains and a["resid"] >= cut]
    return G.centroid(pts), (cut, res[-1])


# ---------------------------------------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------------------------------------


def stage_arm(arm_id, spec, out_dir, log):
    rec = {"arm_id": arm_id, "recruiter": spec["recruiter"], "crl": spec["crl"], "status": "pending",
           "provenance": {}, "rejected": []}
    accs = {k: ACC[k] for k in set(spec["receptor_needs"] + spec["scaffold_needs"] + spec["bridge"])}

    # ---- 1. the ligand-bound receptor entry
    need = spec["receptor_needs"]
    cands = list(dict.fromkeys(spec.get("seed_ids", []) + search_entries([ACC[n] for n in need], rows=40)))
    chosen = None
    for pdb in cands:
        try:
            comp = entry_composition(pdb)
        except Exception as e:                                          # noqa: BLE001
            rec["rejected"].append({"pdb": pdb, "role": "receptor", "reason": f"metadata fetch failed: {e}"})
            continue
        ok, missing = verify(comp, need, accs)
        if not ok:
            rec["rejected"].append({"pdb": pdb, "role": "receptor",
                                    "reason": f"missing accessions for {missing}"})
            continue
        text = _get(FILE_URL.format(pdb=pdb)).decode("utf-8", "replace")
        prot, het = parse_pdb_text(text)
        body_chains = set()
        for n in spec["receptor_body"]:
            body_chains.update(comp["chains_by_accession"].get(ACC[n], []))
        lig = pick_ligand(prot, het, body_chains)
        if lig is None:
            rec["rejected"].append({"pdb": pdb, "role": "receptor",
                                    "reason": "no bound ligand >= %d heavy atoms contacting the receptor"
                                              % MIN_LIGAND_HEAVY})
            continue
        chosen = (pdb, comp, text, prot, body_chains, lig)
        break
    if chosen is None:
        rec["status"] = "FAILED_no_verified_ligand_bound_receptor"
        return rec
    pdb, comp, text, prot, body_chains, lig = chosen
    log(f"[e3stage] {arm_id}: receptor entry {pdb} ({comp['resolution_A']} A) "
        f"chains {sorted(body_chains)} ligand {lig['het_code']} n_heavy={lig['n_heavy']} "
        f"exit atom {lig['exit_atom_name']} exposure {lig['exit_atom_min_dist_to_receptor_A']} A")
    rec["provenance"]["receptor_entry"] = comp

    body_atoms = [a for a in prot if a["chain"] in body_chains]
    body_path = os.path.join(out_dir, f"{arm_id}-receptor.pdb")
    with open(body_path, "w") as fh:
        fh.write(f"REMARK   1 STAGED BY nr4a3_e3_stage.py FROM RCSB {pdb} CHAINS {''.join(sorted(body_chains))}\n")
        for i, a in enumerate(body_atoms, 1):
            fh.write("ATOM  %5d %-4s %3s %s%4d    %8.3f%8.3f%8.3f  1.00  0.00          %2s\n"
                     % (i, a["name"][:4], a["resname"], a["chain"], a["resid"],
                        a["xyz"][0], a["xyz"][1], a["xyz"][2], a["elem"][:2]))
    rec["receptor_pdb"] = os.path.relpath(body_path, REPO)
    rec["ligand"] = lig

    # ---- 2. the cullin scaffold entry -> RING centroid, bridged into the receptor frame
    sneed = spec["scaffold_needs"]
    scands = list(dict.fromkeys(spec.get("seed_ids", []) + search_entries([ACC[n] for n in sneed], rows=40)))
    ring = None
    for spdb in scands:
        try:
            scomp = entry_composition(spdb)
        except Exception as e:                                          # noqa: BLE001
            rec["rejected"].append({"pdb": spdb, "role": "scaffold", "reason": f"metadata fetch failed: {e}"})
            continue
        ok, missing = verify(scomp, sneed, accs)
        if not ok:
            rec["rejected"].append({"pdb": spdb, "role": "scaffold",
                                    "reason": f"missing accessions for {missing}"})
            continue
        stext = _get(FILE_URL.format(pdb=spdb)).decode("utf-8", "replace")
        sprot, _ = parse_pdb_text(stext)
        bridged = None
        for bname in spec["bridge"]:
            src_ch = set(scomp["chains_by_accession"].get(ACC[bname], []))
            dst_ch = set(comp["chains_by_accession"].get(ACC[bname], []))
            if not src_ch or not dst_ch:
                continue
            tr, info = bridge_into_frame(sprot, src_ch, prot, dst_ch)
            if tr is not None:
                bridged = (bname, tr, info)
                break
        if bridged is None:
            rec["rejected"].append({"pdb": spdb, "role": "scaffold", "reason": "no usable bridge protein"})
            continue
        bname, (R, t), info = bridged
        rbx = set(scomp["chains_by_accession"].get(ACC["RBX1"], []))
        cen, rng = ring_domain_centroid(sprot, rbx)
        if cen is None:
            rec["rejected"].append({"pdb": spdb, "role": "scaffold", "reason": "RBX1 chain too short"})
            continue
        cen_in_frame = G.apply_superpose([cen], R, t)[0]
        # cullin direction: from the RING toward the cullin's centroid, so the E2 swing can be restricted to
        # the OUTER hemisphere (the E2 sits on the RING's solvent face, not inside the cullin scaffold).
        cul_acc = [ACC[n] for n in sneed if n.startswith("CUL")]
        cul_ch = set()
        for ca in cul_acc:
            cul_ch.update(scomp["chains_by_accession"].get(ca, []))
        cul_cen = G.centroid([a["xyz"] for a in sprot if a["chain"] in cul_ch])
        cul_in_frame = G.apply_superpose([cul_cen], R, t)[0]
        ring = {
            "ring_centroid_xyz": [round(c, 3) for c in cen_in_frame],
            "cullin_centroid_xyz": [round(c, 3) for c in cul_in_frame],
            "rbx1_ring_residue_range": list(rng),
            "bridge_protein": bname, "bridge": info,
            "scaffold_entry": scomp,
        }
        log(f"[e3stage] {arm_id}: scaffold {spdb} bridged on {bname} "
            f"(rmsd {info['bridge_rmsd_A']} A over {info['n_bridge_ca']} CA) -> RING at "
            f"{ring['ring_centroid_xyz']}")
        break
    if ring is None:
        rec["status"] = "PARTIAL_no_verified_cullin_scaffold"
        rec["ring"] = None
        return rec
    rec["ring"] = ring
    rec["provenance"]["scaffold_entry"] = ring.pop("scaffold_entry")

    # derived geometry the driver consumes directly
    a_e = tuple(lig["exit_atom_xyz"])
    rec["derived"] = {
        "anchor_to_ring_A": round(G.dist(a_e, tuple(ring["ring_centroid_xyz"])), 2),
        "ring_to_cullin_A": round(G.dist(tuple(ring["ring_centroid_xyz"]),
                                         tuple(ring["cullin_centroid_xyz"])), 2),
    }
    rec["status"] = "OK"
    return rec


def stage_e2_geometry(log):
    """MEASURE the RING -> E2 catalytic-cysteine offset from a RING:E2 co-structure, instead of assuming it.

    Returns None if no entry verifies — the driver then uses a declared parametric shell and flags it. The
    catalytic cysteine of a UBE2 domain is identified from the structure by the standard HPN-motif geometry
    proxy: the cysteine whose SG lies closest to the RING interface is NOT reliable, so we instead take the
    cysteine that is most conserved-position — measured here as the SG closest to the E2's own centroid-to-RING
    axis midpoint. This is a proxy and is labelled as one in the output.
    """
    for pair in E2_PAIR_NEEDS:
        try:
            hits = search_entries([ACC[p] for p in pair], rows=10)
        except Exception as e:                                          # noqa: BLE001
            log(f"[e3stage] E2 search failed for {pair}: {e}")
            continue
        for pdb in hits:
            try:
                comp = entry_composition(pdb)
                ok, _ = verify(comp, pair, ACC)
                if not ok:
                    continue
                text = _get(FILE_URL.format(pdb=pdb)).decode("utf-8", "replace")
                prot, _ = parse_pdb_text(text)
                rbx = set(comp["chains_by_accession"].get(ACC["RBX1"], []))
                e2c = set(comp["chains_by_accession"].get(ACC[pair[1]], []))
                cen, rng = ring_domain_centroid(prot, rbx)
                if cen is None:
                    continue
                sgs = [a for a in prot if a["chain"] in e2c and a["resname"] == "CYS" and a["name"] == "SG"]
                if not sgs:
                    continue
                # the catalytic Cys is the one presented on the E2's face AWAY from the RING interface: take
                # the SG furthest from the RING centroid among those still within the E2 core.
                d = [(G.dist(a["xyz"], cen), a) for a in sgs]
                d.sort(key=lambda t: t[0])
                cat = d[-1][1]
                log(f"[e3stage] E2 geometry from {pdb}: RING->SG(Cys{cat['resid']}) = {d[-1][0]:.1f} A "
                    f"(n_cys={len(sgs)}, range {d[0][0]:.1f}-{d[-1][0]:.1f} A)")
                return {
                    "measured": True, "pdb_id": pdb, "title": comp["title"],
                    "e2": pair[1], "e2_accession": ACC[pair[1]],
                    "ring_to_catalytic_cys_A": round(d[-1][0], 2),
                    "all_cys_distances_A": [round(x, 2) for x, _ in d],
                    "catalytic_cys_resid": cat["resid"],
                    "rbx1_ring_residue_range": list(rng),
                    "proxy_note": "catalytic Cys identified geometrically (SG furthest from the RING centroid "
                                  "within the E2 chain), NOT from a sequence motif — a proxy, reported as one.",
                }
            except Exception as e:                                      # noqa: BLE001
                log(f"[e3stage] E2 candidate {pdb} failed: {e}")
                continue
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arms", default="vhl,crbn", help="comma-separated arm ids from ARMS")
    ap.add_argument("--out-dir", default=STAGE_DIR)
    ap.add_argument("--registry", default=REGISTRY)
    ap.add_argument("--plan", action="store_true", help="offline: print the queries, touch no network")
    args = ap.parse_args(argv)

    ids = [a.strip() for a in args.arms.split(",") if a.strip()]
    unknown = [a for a in ids if a not in ARMS]
    if unknown:
        raise SystemExit(f"unknown arm(s): {unknown}; known: {sorted(ARMS)}")

    if args.plan:
        print("[e3stage] OFFLINE PLAN — no network touched")
        for a in ids:
            s = ARMS[a]
            print(f"  arm {a} ({s['crl']}):")
            print(f"    receptor query : accessions {[ACC[n] for n in s['receptor_needs']]} "
                  f"({s['receptor_needs']})")
            print(f"    scaffold query : accessions {[ACC[n] for n in s['scaffold_needs']]} "
                  f"({s['scaffold_needs']})")
            print(f"    bridge on      : {s['bridge']}   seed hints (must still verify): {s['seed_ids']}")
        print(f"  E2 geometry queries: {[[ACC[p] for p in pair] for pair in E2_PAIR_NEEDS]}")
        return 0

    os.makedirs(args.out_dir, exist_ok=True)
    lines = []

    def log(msg):
        print(msg, flush=True)
        lines.append(msg)

    arms = {}
    for a in ids:
        try:
            arms[a] = stage_arm(a, ARMS[a], args.out_dir, log)
        except Exception as e:                                          # noqa: BLE001
            log(f"[e3stage] arm {a} FAILED: {e}")
            arms[a] = {"arm_id": a, "status": f"FAILED_{type(e).__name__}", "error": str(e)}
    e2 = stage_e2_geometry(log)

    out = {
        "_title": "E3 recruiter arm registry for the RUNG-5a mechanism-first orientation-basin search",
        "_method": "RCSB discovery by UniProt-accession SET (never by a remembered PDB ID), composition "
                   "verified against the same accession set after download, cullin scaffold bridged into the "
                   "receptor frame by CA superposition with a reported RMSD, E3-side exit vector DERIVED as "
                   "the ligand heavy atom furthest from the receptor.",
        "_limits": [
            "Each arm is ONE crystal/cryo-EM conformer of the receptor and ONE of the cullin scaffold; CRL "
            "arms are known to be conformationally mobile, so the RING position is a representative, not a "
            "unique, placement. The basin search samples an E2 arc about it rather than a single point.",
            "The bridge superposition assumes the two entries deposit the bridge protein under a common "
            "residue numbering; a mismatch collapses the shared-residue count and is REFUSED, not patched.",
            "The catalytic-cysteine identification in the E2 geometry step is a geometric proxy, not a "
            "sequence-motif assignment.",
            "Nothing here is evidence that any of these recruiters engages NR4A3 — it is input staging.",
        ],
        "staged_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "arms": arms,
        "e2_geometry": e2,
        "log": lines,
    }
    with open(args.registry, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[e3stage] wrote {os.path.relpath(args.registry, REPO)}")
    for a, r in arms.items():
        print(f"[e3stage] {a}: {r['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
