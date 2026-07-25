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

DERIVED, NOT ASSUMED — the exit vector. The E3-side tether anchor is read out of the coordinates rather than
looked up from chemical folklore about which position of VH032 or pomalidomide is "the exit vector": the
ligand's atoms are split by WHICH PROTEIN EACH IS CLOSER TO, and the anchor is the E3-side atom furthest from
the recruiter — the last atom before the linker departs. The split matters because the best ligand-bound
recruiter structures turn out to be PROTAC ternaries (the E3-side moiety is only part of the bound ligand),
and a naive "most exposed atom" rule returns a point on the OTHER warhead. The run log prints the chosen atom
and its exposure so the convention is auditable by eye (TESTING.md rule 6).

MEASURED, NOT ASSUMED — the transfer geometry. The E2 catalytic cysteine is identified by proximity to
UBIQUITIN'S C-TERMINUS (which it carries as a thioester), a question with a unique structural answer; the
function refuses rather than guessing if no ubiquitin chain is present. The same solved ubiquitylation
assembly then yields the substrate-lysine-to-catalytic-cysteine distance, which calibrates the transfer-zone
parameter the basin search would otherwise have to assume. And because that assembly is itself a complete CRL,
it doubles as a KNOWN-ANSWER CHECK on this script's own composition: where an arm shares a bridge protein with
it, the composed RING position is compared against the directly observed one and the displacement reported.

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

# ---------------------------------------------------------------------------------------------------------
# LANE-1 ADAPTER — consume the widened recruiter set without duplicating its work.
#
# A parallel lane stages the ligandable recruiter panel (VHL, CRBN, BIRC2, DCAF1, DCAF15, DCAF16, KEAP1,
# FEM1B, RNF114, MDM2) with UniProt resolution, ligandability and an exit-vector analysis, and downselects
# it. What it does NOT produce is the thing the basin search moves: a receptor BODY in a coordinate frame
# together with the RING that the transfer zone hangs off. This adapter takes its recruiter list and its
# per-recruiter structure choices as INPUTS and stages the geometry here.
#
# THE STRUCTURAL DISTINCTION THAT MATTERS, and that a flat recruiter list hides: a CULLIN-RING recruiter
# (VHL, CRBN, the DCAFs, KEAP1, FEM1B) is a substrate receptor bolted onto a cullin scaffold, so its RING is
# 40-70 A away on a separate polypeptide and has to be composed in. A MONOMERIC RING E3 (BIRC2, MDM2,
# RNF114) carries its own RING in the SAME chain.
#
# ⚠ AND THE OBVIOUS INFERENCE FROM THAT IS WRONG — checked by staging them, not by reasoning. "Same chain"
# looks like it should mean "no composition needed, so the transfer zone is better determined". It does not.
# The ligandable structures of these recruiters are SMALL FRAGMENTS: 4HY4 gives BIRC2 residues 255-346, 15 %
# of a 618-residue protein (the BIR3 / SMAC-mimetic domain), and 6Q9L gives MDM2 residues 18-111, 19 % of 491
# (the p53-binding / nutlin domain). The catalytic RING is hundreds of residues away at the C-terminus, and
# the two domains are separately-crystallised fragments joined by a long unstructured region that no
# deposited structure spans. So the RING is attached by a several-hundred-residue flexible tether and its
# position is LESS determined than a composed CRL RING, not more — both arms come back
# PARTIAL_no_transfer_geometry. Lane 1's ligandability Pareto advanced exactly these two, and it cannot see
# this, because it never asks where the RING is.
CRL_CLASS_SPECS = {
    "CRL2": {"obligate_partners": ["ELOB", "ELOC"], "scaffold_needs": ["ELOC", "CUL2", "RBX1"],
             "bridge": ["ELOC"]},
    "CRL4": {"obligate_partners": ["DDB1"], "scaffold_needs": ["DDB1", "CUL4A", "RBX1"], "bridge": ["DDB1"]},
    "CRL3": {"obligate_partners": [], "scaffold_needs": ["CUL3", "RBX1"], "bridge": ["CUL3"]},
    "MONOMERIC_RING": {"obligate_partners": [], "scaffold_needs": None, "bridge": None},
}


def classify_e3(e3_class_text: str) -> str:
    t = (e3_class_text or "").upper()
    if "CRL2" in t:
        return "CRL2"
    if "CRL4" in t:
        return "CRL4"
    if "CRL3" in t:
        return "CRL3"
    if "MONOMERIC" in t or "RING" in t:
        return "MONOMERIC_RING"
    return "UNKNOWN"


ASSEMBLY_URL = "https://files.rcsb.org/download/{pdb}.pdb1"


def adopt_lane1_anchor(pdb, arm_chains, anchor_xyz, exit_direction, log=None):
    """Consume the E3 lane's recruiter-side anchor — but VERIFY the coordinate frame rather than trust it.

    WHY VERIFY. The lane computes `anchor_xyz` on **biological assembly 1 (mmCIF)**, and this script downloads
    the **asymmetric unit** PDB. Those are not always the same frame: a biological assembly can be generated
    from the AU by crystallographic symmetry operators, in which case a coordinate handed across is silently
    in the wrong place — and every distance downstream would still look perfectly reasonable. This is the same
    silent-success class as everything else fixed in this lane, so it gets the same treatment: the anchor is
    accepted only if it actually LANDS ON a ligand heavy atom in the frame we loaded.

    Returns (adopted_dict_or_None, info). A frame mismatch is a REFUSAL with the measured miss distance, not a
    warning, and the caller then falls back to its own derived exit vector.
    """
    for url, kind in ((ASSEMBLY_URL.format(pdb=pdb), "biological assembly 1"),
                      (FILE_URL.format(pdb=pdb), "asymmetric unit")):
        try:
            text = _get(url).decode("utf-8", "replace")
        except (NotAvailable, RuntimeError):
            continue
        prot, het = parse_pdb_text(text)
        cand = [a for a in het if a["resname"] not in EXCLUDE_HET]
        if not cand:
            continue
        d, best = min(((G.dist(anchor_xyz, a["xyz"]), a) for a in cand), key=lambda t: t[0])
        if d <= 0.5:
            if log:
                log(f"[e3stage]   lane-1 anchor VERIFIED against the {kind}: lands on {best['resname']}."
                    f"{best['name']} at {d:.2f} A")
            return ({"source": "e3_lane", "pdb_id": pdb, "frame": kind,
                     "anchor_xyz": list(anchor_xyz), "exit_direction": list(exit_direction),
                     "matched_atom": f"{best['resname']}.{best['name']}",
                     "match_distance_A": round(d, 3)},
                    {"ok": True, "frame": kind, "miss_A": round(d, 3)})
        nearest = (d, kind)
    return None, {"ok": False, "reason": f"lane-1 anchor does not land on a ligand atom in any frame we can "
                                         f"load (nearest {nearest[0]:.1f} A in the {nearest[1]})"}


def arms_from_lane1(registry_path, only=None):
    """Build ARMS entries from Lane 1's recruiter staging JSON. Refuses a recruiter whose UniProt accession
    Lane 1 itself refused (accession null) — an unresolved identity is not a staging input."""
    reg = json.load(open(registry_path))
    # schema v1.1: the decided rows live under downselect. Tolerate either shape rather than assume one.
    ds = reg.get("downselect") or {}
    # The decided rows come from that lane's own CONSUMER API (`load_advanced`), which it declares stable
    # across schema revisions; the raw JSON shape is explicitly not. Import it if the module sits beside the
    # registry, and if it does not, rebuild the same fields from the registry — and SAY SO, because a quiet
    # fallback would mean consuming a reconstructed row while believing it came from the contract.
    adv_rows = {}
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(registry_path)))
        import e3_recruiter_staging as _e3lane            # noqa: PLC0415
        for r in _e3lane.load_advanced(registry_path):
            adv_rows[r["gene"]] = r
    except Exception as _exc:                             # noqa: BLE001
        print(f"[e3stage] lane-1 consumer API unavailable ({type(_exc).__name__}: {_exc}) — rebuilding the "
              f"rows from the registry", flush=True)
        back = set(ds.get("backfilled_for_e3_choice_sensitivity") or [])
        for gene in (ds.get("advanced") or []):
            rr = (reg.get("recruiters") or {}).get(gene) or {}
            ev = ((rr.get("ligandability") or {}).get("exit_vector")) or {}
            prim = next((s for s in (rr.get("staged_structures") or []) if s.get("is_primary")), None) or {}
            adv_rows[gene] = {
                "gene": gene, "pdb_id": prim.get("pdb_id"),
                "anchor_xyz": ev.get("anchor_xyz"), "exit_direction": ev.get("direction"),
                "backfilled": gene in back,
                "caveats": (["Pareto-dominated; advanced only so the E3 is a controlled variable downstream"]
                            if gene in back else []),
            }
    out = {}
    for gene, rec in (reg.get("recruiters") or {}).items():
        if only and gene not in only:
            continue
        acc = ((rec.get("uniprot") or {}).get("accession"))
        if not acc:
            continue
        cls = classify_e3(rec.get("e3_class"))
        spec_cls = CRL_CLASS_SPECS.get(cls)
        if spec_cls is None:
            continue
        ACC.setdefault(gene, acc)
        seeds = [s["pdb_id"] for s in (rec.get("staged_structures") or [])]
        # schema v1.1 puts the decided row in downselect; prefer it over the raw staged list, because it is
        # the row the lane actually stands behind (with its anchor, its frame and its caveats).
        row = (adv_rows or {}).get(gene)
        if row:
            seeds = [row["pdb_id"]] + [x for x in seeds if x != row["pdb_id"]]
        needs = [gene] + list(spec_cls["obligate_partners"])
        arm = {
            "recruiter": gene,
            "crl": rec.get("arm") or cls,
            "e3_architecture": cls,
            "receptor_needs": needs,
            "receptor_body": needs,
            "seed_ids": seeds,
            "lane1_exit_vector": (rec.get("ligandability") or {}).get("exit_vector"),
            "lane1_row": row,
            "lane1_caveats": (row or {}).get("caveats") or [],
            "lane1_backfilled": bool((row or {}).get("backfilled")),
            "lane1_anchor_xyz": (row or {}).get("anchor_xyz"),
            "lane1_exit_direction": (row or {}).get("exit_direction"),
            "lane1_primary_pdb": next((s["pdb_id"] for s in (rec.get("staged_structures") or [])
                                       if s.get("is_primary")), None),
        }
        if spec_cls["scaffold_needs"] is None:
            arm["self_ring"] = True                 # the RING is in the recruiter's own chain
            arm["scaffold_needs"] = None
            arm["bridge"] = None
        else:
            arm["scaffold_needs"] = needs[:1] + list(spec_cls["scaffold_needs"])
            arm["bridge"] = [b for b in ([gene] + list(spec_cls["bridge"])) if b in ACC]
        out[gene.lower()] = arm
    return out


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


class NotAvailable(RuntimeError):
    """The resource genuinely does not exist (404) — distinct from a transient network failure.

    Load-bearing distinction: large modern assemblies are often deposited with NO legacy PDB-format file, so
    `files.rcsb.org/download/XXXX.pdb` 404s while the entry is perfectly real. That must SKIP the candidate
    and move to the next one, not retry four times and then kill the whole arm — which is exactly what
    happened to the VHL arm on entry 9T32.
    """


def _get(url, tries=4, timeout=60):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Rare-cancers/nr4a3_e3_stage"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise NotAvailable(f"404 (no such resource): {url}") from None
            last = e
            time.sleep(1.5 * (2 ** i))
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
            if e.code == 204:
                return {"result_set": []}
            last = e
            time.sleep(1.5 * (2 ** i))
        except json.JSONDecodeError:
            # RCSB answers a ZERO-HIT search with 204 No Content and an EMPTY BODY, which urllib treats as
            # success — so it never reaches the HTTPError branch above and json.loads('') raises. That made
            # every legitimately-empty search look like four failed network calls: the VHL arm's
            # intact-assembly probes reported "POST failed after 4 tries" for five different E2s when the
            # true answer was simply "no such structure exists". An empty body IS the answer.
            return {"result_set": []}
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


def _min_dist_exact(p, pts):
    best = 1e18
    for q in pts:
        d = G.dist2(p, q)
        if d < best:
            best = d
    return math.sqrt(best)


def pick_ligand(prot_atoms, het_atoms, body_chains):
    """The recruiter's bound ligand, and the point where a LINKER LEAVES THE E3 — derived, not looked up.

    TWO DEFECTS THIS FUNCTION EXISTS TO AVOID, both found by reading the first run's own output rather than
    by reasoning about it:

    1. THE HIGHEST-RESOLUTION LIGAND-BOUND RECRUITER STRUCTURES ARE PROTAC TERNARIES. The verified VHL entry
       is 5T35 (VHL-EloB-EloC + BRD4-BD2 + a 69-heavy-atom ligand) and the verified CRBN entry is 6BOY
       (CRBN-DDB1 + BRD4-BD1 + a 59-heavy-atom ligand). In both, the bound "ligand" is a WHOLE degrader:
       E3-binder + linker + a second warhead. Taking its most solvent-exposed atom as the E3 exit vector
       returns a point on the OTHER warhead, tens of angstroms away, which would silently anchor the entire
       linker-reach restraint in the wrong place. The fix uses information the structure genuinely contains:
       split the ligand by WHICH PROTEIN EACH ATOM IS CLOSER TO. Atoms nearer the recruiter are the E3-binding
       moiety; the exit vector is the atom of that moiety that is furthest from the recruiter, i.e. the last
       one before the linker departs. With no second protein present (a bare recruiter ligand) this degrades
       exactly to "the most exposed atom", which is the right answer there.

    2. THE FIRST RUN REPORTED BOTH ARMS' EXIT EXPOSURE AS EXACTLY 8.00 A. That is not a coincidence, it is the
       distance field's CLAMP: once several ligand atoms are past 8 A the argmax is degenerate and the choice
       is arbitrary. Ligands have <100 atoms, so distances here are now computed EXACTLY.
    """
    body = [a["xyz"] for a in prot_atoms if a["chain"] in body_chains]
    other = [a["xyz"] for a in prot_atoms if a["chain"] not in body_chains]
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
    rows = []
    for a in atoms:
        d_e3 = _min_dist_exact(a["xyz"], body)
        d_other = _min_dist_exact(a["xyz"], other) if other else float("inf")
        rows.append({"atom": a, "d_e3": d_e3, "d_other": d_other, "on_e3_side": d_e3 <= d_other})
    e3_side = [r for r in rows if r["on_e3_side"]]
    if not e3_side:
        return None
    e3_side.sort(key=lambda r: -r["d_e3"])
    exit_row = e3_side[0]
    return {
        "het_code": key[0], "chain": key[1], "resid": key[2],
        "n_heavy": len(atoms),
        "n_heavy_on_e3_side": len(e3_side),
        "is_protac_ternary": len(e3_side) < len(atoms),
        "atoms": [{"name": r["atom"]["name"], "elem": r["atom"]["elem"], "xyz": list(r["atom"]["xyz"]),
                   "d_e3_A": round(r["d_e3"], 2),
                   "d_other_protein_A": (round(r["d_other"], 2) if r["d_other"] != float("inf") else None),
                   "on_e3_side": r["on_e3_side"]} for r in rows],
        "exit_atom_name": exit_row["atom"]["name"],
        "exit_atom_xyz": list(exit_row["atom"]["xyz"]),
        "exit_atom_dist_to_receptor_A": round(exit_row["d_e3"], 2),
        "exit_atom_dist_to_other_protein_A": (round(exit_row["d_other"], 2)
                                              if exit_row["d_other"] != float("inf") else None),
        "e3_moiety_centroid": list(G.centroid([r["atom"]["xyz"] for r in e3_side])),
        "ligand_centroid": list(G.centroid([a["xyz"] for a in atoms])),
        "_derivation": "ligand atoms split by which protein each is closer to; the exit vector is the "
                       "E3-side atom furthest from the recruiter (exact distances, no grid clamp).",
    }


def _chain_atoms(prot, chain):
    return [a["xyz"] for a in prot if a["chain"] == chain]


def _chains_touch(prot, c1, c2, cutoff=6.0):
    """Do two chains form an interface? Grid-based, so it is cheap enough to run over every candidate pair."""
    a1 = _chain_atoms(prot, c1)
    a2 = _chain_atoms(prot, c2)
    if not a1 or not a2:
        return False
    f = G.SquaredDistanceField(a1, cell=1.5, clamp=8.0)
    return sum(1 for p in a2 if f.min_dist(p) <= cutoff) >= 10


def select_assembly_copy(prot, chains_by_protein, log=None, max_combos=64):
    """Pick ONE spatially coherent copy of a multi-protein complex from an asymmetric unit that may hold several.

    THE BUG THIS EXISTS TO KILL. 5T35 deposits **two** copies of VHL-EloB-EloC (chains B,C,D and F,G,H). Taking
    "every chain annotated as VHL, Elongin B or Elongin C" as the receptor body gives a rigid body that is
    literally two complexes, roughly twice the real size, with a void between them — and every clash test,
    contact count and interface score computed on it would be meaningless. The same defect corrupts the
    bridge: pairing VHL from one copy with Elongin C from the other produced joint superposition RMSDs of
    5.2-7.3 A over 124-237 CA, which is why every VHL scaffold candidate was rejected while the earlier
    single-protein bridge had succeeded at 1.38 A. Neither symptom announces itself as a chain-selection
    problem.

    Derived, not assumed (TESTING.md rule 1): enumerate one chain per protein, keep the combinations whose
    chains MUTUALLY CONTACT, and rank by total contact so the tightest genuine copy wins. Refuses rather than
    guessing if the enumeration is too large or nothing is coherent.
    """
    proteins = sorted(chains_by_protein)
    lists = [sorted(chains_by_protein[p]) for p in proteins]
    n = 1
    for l in lists:
        n *= max(1, len(l))
    if n > max_combos:
        return None, {"ok": False, "reason": f"{n} chain combinations exceeds the {max_combos} cap"}
    if n == 1:
        # Nothing to SELECT — but coherence is still worth measuring and reporting, because a "single copy"
        # whose subunits do not touch is a fact about the entry the caller should see. Refusing here would be
        # wrong (there is no alternative to fall back to); hiding it would be worse.
        only = {p: lists[i][0] for i, p in enumerate(proteins)}
        chs = list(only.values())
        pairs = sum(1 for i in range(len(chs)) for j in range(i + 1, len(chs))
                    if _chains_touch(prot, chs[i], chs[j]))
        expected = len(chs) * (len(chs) - 1) // 2
        return only, {"ok": True, "n_combinations": 1, "single_copy": True,
                      "n_contacting_pairs": pairs, "coherent": pairs == expected,
                      "_note": ("the only chain combination available; accepted, with its coherence reported"
                                if pairs == expected else
                                "WARNING: the only chain combination available and its subunits do NOT all "
                                "contact each other — accepted because there is no alternative, flagged "
                                "because it may not be one assembled complex")}

    def combos(idx=0, cur=None):
        cur = cur or {}
        if idx == len(proteins):
            yield dict(cur)
            return
        for c in lists[idx]:
            cur[proteins[idx]] = c
            yield from combos(idx + 1, cur)

    best, best_score, checked = None, -1, 0
    for combo in combos():
        chs = list(combo.values())
        if len(set(chs)) != len(chs):
            continue
        checked += 1
        score = 0
        coherent = True
        for i in range(len(chs)):
            for j in range(i + 1, len(chs)):
                if _chains_touch(prot, chs[i], chs[j]):
                    score += 1
                else:
                    coherent = False
        if coherent and score > best_score:
            best, best_score = combo, score
    if best is None:
        return None, {"ok": False, "reason": f"no mutually-contacting chain combination among {checked}"}
    info = {"ok": True, "n_combinations_checked": checked, "selected": best,
            "n_contacting_pairs": best_score,
            "_note": "one spatially coherent copy selected from an asymmetric unit that may hold several"}
    if log:
        log(f"[e3stage]   assembly copy selected: {best} ({best_score} contacting chain pairs "
            f"out of {checked} combinations)")
    return best, info


def bridge_into_frame(src_prot, src_chain_map, dst_prot, dst_chain_map, max_rmsd=4.0, min_ca=30):
    """Superpose `src` onto `dst` using the CA atoms of EVERY shared bridge protein AT ONCE.

    WHY ALL OF THEM JOINTLY, and the measurement that forced it. The first run bridged 5N4W into 5T35 on VHL
    alone and got 1.381 A over just **37 CA** — a thin, short lever. The quantity it positions is the RBX1
    RING, which sits ~70 A from the ligand anchor, so a rotational error of even 2-3 deg (well within what 37
    CA at 1.4 A supports) displaces the RING by 2.5-3.7 A and moves the entire term-(b) transfer zone with it.
    Elongin C is present in both entries and adds CAs for free; using the union constrains the rotation far
    better than the recruiter alone. Keys are (bridge_protein, resid), NOT resid alone, because VHL and
    Elongin C both number from ~1 and merging them on residue number would silently pair unrelated residues.

    Residue-number matching within a protein (rather than sequence alignment) is deliberate: both entries
    deposit the same protein under the same UniProt numbering in the overwhelming majority of cases, and if
    they do not, the shared count collapses and the gates below REFUSE the composition rather than quietly
    producing a plausible, wrong RING position.
    """
    src_by, dst_by = {}, {}
    for bname, chains in src_chain_map.items():
        for (c, r), xyz in chain_ca(src_prot, chains).items():
            src_by.setdefault((bname, r), xyz)
    for bname, chains in dst_chain_map.items():
        for (c, r), xyz in chain_ca(dst_prot, chains).items():
            dst_by.setdefault((bname, r), xyz)
    shared = sorted(set(src_by) & set(dst_by))
    if len(shared) < min_ca:
        return None, {"ok": False, "reason": f"only {len(shared)} shared bridge residues (need >= {min_ca})"}
    mob = [src_by[k] for k in shared]
    ref = [dst_by[k] for k in shared]
    R, t, rmsd = G.horn_superpose(mob, ref)
    if rmsd > max_rmsd:
        return None, {"ok": False, "reason": f"bridge RMSD {rmsd:.2f} A > {max_rmsd} A over {len(shared)} CA"}
    per_protein = {}
    for k in shared:
        per_protein[k[0]] = per_protein.get(k[0], 0) + 1
    return (R, t), {"ok": True, "n_bridge_ca": len(shared), "bridge_rmsd_A": round(rmsd, 3),
                    "ca_per_bridge_protein": per_protein}


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
    # A MONOMERIC RING arm has no cullin scaffold and no bridge — both are legitimately None, so they have to
    # be tolerated here rather than concatenated blindly. (They were not: BIRC2 and MDM2, the two recruiters
    # the E3 lane's downselect actually advanced, both died on `list + None` at this line before reaching the
    # guard that handles them a hundred lines below.)
    accs = {k: ACC[k] for k in set((spec.get("receptor_needs") or [])
                                   + (spec.get("scaffold_needs") or [])
                                   + (spec.get("bridge") or []))}

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
        try:
            text = _get(FILE_URL.format(pdb=pdb)).decode("utf-8", "replace")
        except NotAvailable as e:
            rec["rejected"].append({"pdb": pdb, "role": "receptor", "reason": str(e)})
            continue
        prot, het = parse_pdb_text(text)
        cbp = {n: set(comp["chains_by_accession"].get(ACC[n], [])) for n in spec["receptor_body"]}
        cbp = {k: v for k, v in cbp.items() if v}
        copy_sel, copy_info = select_assembly_copy(prot, cbp, log)
        if copy_sel is None:
            rec["rejected"].append({"pdb": pdb, "role": "receptor",
                                    "reason": "assembly-copy selection: " + copy_info["reason"]})
            continue
        body_chains = set(copy_sel.values())
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
        f"exit atom {lig['exit_atom_name']} exposure {lig['exit_atom_dist_to_receptor_A']} A")
    rec["provenance"]["receptor_entry"] = comp
    rec["assembly_copy"] = {"selected_chains": copy_sel, "selection": copy_info}
    rec["_receptor_copy_chains"] = copy_sel

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

    # ---- 1b. THE E3 LANE'S ANCHOR, adopted where it verifies, and CROSS-CHECKED against ours either way.
    # Its anchor is the contract's recruiter-side attachment point, computed on biological assembly 1 with
    # occluders limited to the recruiter's own CRL arm. Ours is derived independently by splitting the ligand
    # on which protein each atom is closer to. Two independent derivations of the same quantity is a free
    # consistency check, so the distance between them is always reported — agreement is evidence, and
    # disagreement is a finding, but neither is allowed to pass unmeasured.
    rec["lane1"] = {"caveats": spec.get("lane1_caveats") or [],
                    "backfilled": bool(spec.get("lane1_backfilled")),
                    "row_pdb_id": (spec.get("lane1_row") or {}).get("pdb_id")}
    l1_anchor = spec.get("lane1_anchor_xyz")
    if l1_anchor and (spec.get("lane1_row") or {}).get("pdb_id") == pdb:
        adopted, info = adopt_lane1_anchor(pdb, body_chains, tuple(l1_anchor),
                                           spec.get("lane1_exit_direction") or [0.0, 0.0, 1.0], log)
        rec["lane1"]["anchor_adoption"] = info
        d_ours = G.dist(tuple(l1_anchor), tuple(lig["exit_atom_xyz"]))
        rec["lane1"]["distance_to_our_derived_exit_atom_A"] = round(d_ours, 2)
        log(f"[e3stage] {arm_id}: lane-1 anchor vs our independently derived exit atom "
            f"({lig['exit_atom_name']}): {d_ours:.2f} A apart "
            f"[adoption {'OK' if info['ok'] else 'REFUSED: ' + info['reason']}]")
        if adopted:
            rec["ligand"]["exit_atom_xyz"] = adopted["anchor_xyz"]
            rec["ligand"]["exit_vector_source"] = adopted
            rec["ligand"]["our_derived_exit_atom_xyz"] = list(lig["exit_atom_xyz"])
    elif l1_anchor:
        rec["lane1"]["anchor_adoption"] = {
            "ok": False,
            "reason": f"lane-1 measured its anchor on {(spec.get('lane1_row') or {}).get('pdb_id')} but the "
                      f"verified receptor entry here is {pdb}; an anchor is only meaningful in its own "
                      f"structure's frame, so it is NOT transplanted"}

    # ---- 2a. PREFERRED: a solved, intact ubiquitylation assembly for this recruiter. Read the transfer
    # geometry straight out of it rather than composing a RING from two unrelated entries.
    intact = None
    try:
        intact = stage_intact_assembly(arm_id, spec, comp, prot, log, recep_copy=copy_sel)
    except Exception as e:                                              # noqa: BLE001
        log(f"[e3stage] {arm_id}: intact-assembly staging failed: {e}")
    rec["intact_assembly"] = intact
    if intact:
        rec["transfer_anchor"] = {
            "source": "observed_in_intact_assembly",
            "xyz": intact["catalytic_cys_xyz_in_receptor_frame"],
            "what": "the E2 catalytic cysteine, observed in a solved ubiquitylation assembly and bridged "
                    "into this receptor's frame — one step closer to the observable than a RING plus a "
                    "modelled swing, and it needs no swing model at all",
            "provenance_pdb": intact["pdb_id"],
            "anchor_to_transfer_point_A": round(
                G.dist(tuple(lig["exit_atom_xyz"]), tuple(intact["catalytic_cys_xyz_in_receptor_frame"])), 2),
        }

    # ---- 2b. the cullin scaffold entry -> RING centroid, bridged into the receptor frame (the FALLBACK,
    # and the thing the composition check measures the error of)
    sneed = spec.get("scaffold_needs")
    if not sneed:
        rec["ring"] = None
        rec["status"] = "OK" if intact else "PARTIAL_no_transfer_geometry"
        return rec
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
        try:
            stext = _get(FILE_URL.format(pdb=spdb)).decode("utf-8", "replace")
        except NotAvailable as e:
            rec["rejected"].append({"pdb": spdb, "role": "scaffold", "reason": str(e)})
            continue
        sprot, _ = parse_pdb_text(stext)
        src_cbp = {b: set(scomp["chains_by_accession"].get(ACC[b], [])) for b in spec["bridge"]}
        src_cbp = {k: v for k, v in src_cbp.items() if v}
        src_sel, src_info = select_assembly_copy(sprot, src_cbp, log)
        src_map, dst_map = {}, {}
        for bname in spec["bridge"]:
            sc = {src_sel[bname]} if (src_sel and bname in src_sel) else set(
                scomp["chains_by_accession"].get(ACC[bname], []))
            dc = {copy_sel[bname]} if bname in copy_sel else set()
            if sc and dc:
                src_map[bname] = sc
                dst_map[bname] = dc
        if not src_map:
            rec["rejected"].append({"pdb": spdb, "role": "scaffold", "reason": "no shared bridge protein"})
            continue
        tr, info = bridge_into_frame(sprot, src_map, prot, dst_map)
        if tr is None:
            rec["rejected"].append({"pdb": spdb, "role": "scaffold", "reason": info["reason"]})
            continue
        bname = "+".join(sorted(src_map))
        R, t = tr
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
        rec["ring"] = None
        rec["status"] = "OK" if intact else "PARTIAL_no_verified_cullin_scaffold"
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
    if not intact:
        rec["transfer_anchor"] = {
            "source": "composed_ring_MODEL",
            "xyz": ring["ring_centroid_xyz"],
            "what": "the RBX1 RING composed from two unrelated entries. The E2 catalytic cysteine is NOT "
                    "observed for this arm, so the transfer zone is an arc sampled about this point.",
            "provenance_pdb": (rec["provenance"].get("scaffold_entry") or {}).get("pdb_id"),
            "anchor_to_transfer_point_A": rec["derived"]["anchor_to_ring_A"],
            "_uncertainty": "A composed RING is one point on a large conformational arc. Measured on the "
                            "CRBN arm, a composed RING sat 48.6 A from the RING of an intact solved assembly "
                            "in the same frame, with both bridges better than 1.5 A. Treat this as a MODEL.",
        }
    rec["status"] = "OK"
    return rec


UBIQUITIN_ACC = ("P0CG47", "P0CG48", "P62979", "P62987")     # UBB / UBC / RPS27A / UBA52
SCAFFOLD_ACC = {ACC[k] for k in ("RBX1", "CUL1", "CUL2", "CUL4A", "CUL4B", "DDB1", "ELOB", "ELOC", "SKP1",
                                 "VHL", "CRBN")}


def stage_e2_geometry(log):
    """MEASURE the ubiquitin-transfer geometry from a solved CRL ubiquitylation assembly — do not assume it.

    WHAT CHANGED AND WHY (this function's first version was wrong, and its own output showed it). Version 1
    identified the E2's catalytic cysteine as "the SG furthest from the RING centroid". That is a GUESS
    dressed as a measurement: it returned Cys111 of UBE2D1 from PDB 9UUM out of four candidate cysteines
    spanning 27.7-35.4 A, with nothing but a heuristic behind the choice, and every transfer-zone radius
    downstream would have inherited it.

    The discriminating observation is in the structure itself. A CRL ubiquitylation assembly carries
    UBIQUITIN, and the catalytic cysteine is BY DEFINITION the one that carries ubiquitin's C-terminal
    glycine as a thioester. So the catalytic Cys is identified as the E2 cysteine whose SG is nearest
    ubiquitin's C-terminal residue — a structural measurement with a unique answer, not a heuristic. If no
    ubiquitin chain is present the function REFUSES rather than falling back to the guess.

    AND THE BONUS THAT MATTERS MORE THAN THE RADIUS. The same class of structure contains the NEOSUBSTRATE
    being ubiquitylated, so it also yields the quantity term (b) actually needs and which was otherwise an
    assumption: the distance from the E2 catalytic cysteine to the substrate lysine that is about to be
    modified. That converts `lysine_transfer_A` from a declared parameter into a value calibrated against a
    solved assembly, and the full lysine-distance distribution is reported so the calibration is auditable
    rather than a single cherry-picked number.
    """
    seen = set()
    for pair in E2_PAIR_NEEDS:
        try:
            hits = search_entries([ACC[p] for p in pair], rows=15)
        except Exception as e:                                          # noqa: BLE001
            log(f"[e3stage] E2 search failed for {pair}: {e}")
            continue
        for pdb in hits:
            if pdb in seen:
                continue
            seen.add(pdb)
            try:
                comp = entry_composition(pdb)
                ok, _ = verify(comp, pair, ACC)
                if not ok:
                    continue
                ub_acc = [a for a in UBIQUITIN_ACC if a in comp["chains_by_accession"]]
                if not ub_acc:
                    log(f"[e3stage] E2 candidate {pdb}: no ubiquitin chain -> cannot IDENTIFY the catalytic "
                        f"cysteine by measurement; refused (not guessed)")
                    continue
                text = _get(FILE_URL.format(pdb=pdb)).decode("utf-8", "replace")
                prot, _ = parse_pdb_text(text)
                rbx = set(comp["chains_by_accession"].get(ACC["RBX1"], []))
                e2c = set(comp["chains_by_accession"].get(ACC[pair[1]], []))
                ubc = set()
                for a in ub_acc:
                    ubc.update(comp["chains_by_accession"][a])
                cen, rng = ring_domain_centroid(prot, rbx)
                if cen is None:
                    continue
                sgs = [a for a in prot if a["chain"] in e2c and a["resname"] == "CYS" and a["name"] == "SG"]
                ub_res = sorted({a["resid"] for a in prot if a["chain"] in ubc})
                ub_cterm = [a["xyz"] for a in prot
                            if a["chain"] in ubc and a["resid"] == ub_res[-1] and a["name"] in ("C", "CA")]
                if not sgs or not ub_cterm:
                    continue
                ranked = sorted(((min(G.dist(a["xyz"], u) for u in ub_cterm), a) for a in sgs),
                                key=lambda t: t[0])
                d_ub, cat = ranked[0]
                d_ring = G.dist(cat["xyz"], cen)
                # the neosubstrate: any polymer chain that is not CRL scaffold, not the E2, not ubiquitin
                sub_chains = set()
                for acc, chains in comp["chains_by_accession"].items():
                    if acc in SCAFFOLD_ACC or acc in UBIQUITIN_ACC or acc == ACC[pair[1]]:
                        continue
                    sub_chains.update(chains)
                lys = [(G.dist(a["xyz"], cat["xyz"]), a) for a in prot
                       if a["chain"] in sub_chains and a["resname"] == "LYS" and a["name"] == "NZ"]
                lys.sort(key=lambda t: t[0])
                log(f"[e3stage] transfer geometry from {pdb} ({comp['title']}):")
                log(f"[e3stage]   catalytic Cys{cat['resid']} of {pair[1]} identified by proximity to "
                    f"ubiquitin C-term (res {ub_res[-1]}): {d_ub:.1f} A; other Cys "
                    f"{[round(x,1) for x,_ in ranked[1:]]} A")
                log(f"[e3stage]   RING -> catalytic Cys = {d_ring:.1f} A")
                if lys:
                    log(f"[e3stage]   substrate Lys NZ -> catalytic Cys: nearest {lys[0][0]:.1f} A "
                        f"(Lys{lys[0][1]['resid']}), n={len(lys)}, "
                        f"all {[round(x,1) for x,_ in lys[:8]]}")
                return {
                    "measured": True, "pdb_id": pdb, "title": comp["title"],
                    "method": comp.get("method"), "resolution_A": comp.get("resolution_A"),
                    "e2": pair[1], "e2_accession": ACC[pair[1]],
                    "catalytic_cys_resid": cat["resid"],
                    "catalytic_cys_identified_by": "minimum SG-to-ubiquitin-C-terminus distance "
                                                   "(a measurement with a unique answer, not a heuristic)",
                    "catalytic_cys_to_ubiquitin_cterm_A": round(d_ub, 2),
                    "runner_up_cys_to_ubiquitin_cterm_A": [round(x, 2) for x, _ in ranked[1:]],
                    "ring_to_catalytic_cys_A": round(d_ring, 2),
                    "rbx1_ring_residue_range": list(rng),
                    "_composition_check_inputs": {
                        "pdb_id": pdb,
                        "chains_by_accession": comp["chains_by_accession"],
                        "ring_centroid_xyz": [round(c, 3) for c in cen],
                        "catalytic_cys_xyz": [round(c, 3) for c in cat["xyz"]],
                    },
                    "substrate_lysine_calibration": ({
                        "n_substrate_lysines": len(lys),
                        "nearest_lysine_resid": lys[0][1]["resid"],
                        "nearest_lysine_to_catalytic_cys_A": round(lys[0][0], 2),
                        "all_lysine_distances_A": [round(x, 2) for x, _ in lys],
                        "_reading": "the distance a substrate lysine actually sits from the E2 catalytic "
                                    "cysteine in a SOLVED ubiquitylation assembly — the empirical scale for "
                                    "the transfer-zone parameter, reported as a full distribution so the "
                                    "calibration can be checked rather than taken on trust.",
                    } if lys else None),
                }
            except Exception as e:                                      # noqa: BLE001
                log(f"[e3stage] E2 candidate {pdb} failed: {e}")
                continue
    return None


def stage_intact_assembly(arm_id, spec, recep_comp, recep_prot, log, recep_copy=None):
    """Find a SOLVED, INTACT ubiquitylation assembly for this recruiter and read the transfer geometry
    straight out of it, instead of composing the RING from two unrelated entries.

    WHY THIS EXISTS — the composition check falsified the composed model, and the number is not small. For the
    CRBN arm, the RING composed from a CRBN-DDB1 entry plus a DDB1-CUL4A-RBX1 crystal (bridged on 808 DDB1
    CA at 1.17 A, i.e. an excellent bridge) sits **48.6 A** from the RING of an intact, substrate-engaged
    CRL4-CRBN cryo-EM assembly placed in the same frame. Both superpositions are good; the discrepancy is
    not error, it is CONFORMATION — CRL4 is a rotational scaffold whose DDB1 propeller pivots on the cullin,
    so an unengaged crystal scaffold and a substrate-engaged assembly put the RING in genuinely different
    places. A composed RING is therefore one arbitrary point on a very large arc, not a placement.

    Two consequences, both adopted here rather than argued around:
      * where an intact assembly exists, the transfer zone is anchored on the OBSERVED E2 CATALYTIC CYSTEINE
        bridged into the receptor's frame — one step closer to the observable than the RING, and it needs no
        swing model at all (for CRBN this is 12.0 A from the ligand exit vector);
      * where one does not, the composed RING is still used, but it is FLAGGED as a model with the 48.6 A
        figure attached as the honest scale of its uncertainty.
    """
    obligate = [n for n in spec["receptor_needs"]]
    for e2name in ("UBE2D1", "UBE2D2", "UBE2D3", "UBE2R1", "UBE2R2", "UBE2G1", "UBE2L3"):
        need = [spec["recruiter"], e2name]
        try:
            hits = search_entries([ACC[n] for n in need], rows=10)
        except Exception as exc:                                        # noqa: BLE001
            log(f"[e3stage] {arm_id}: intact-assembly search failed for {e2name}: {exc}")
            continue
        for pdb in hits:
            try:
                comp = entry_composition(pdb)
                ok, _ = verify(comp, need, ACC)
                if not ok:
                    continue
                ub_acc = [a for a in UBIQUITIN_ACC if a in comp["chains_by_accession"]]
                if not ub_acc:
                    continue
                try:
                    text = _get(FILE_URL.format(pdb=pdb)).decode("utf-8", "replace")
                except NotAvailable:
                    continue
                aprot, _ = parse_pdb_text(text)
                e2c = set(comp["chains_by_accession"].get(ACC[e2name], []))
                ubc = set()
                for a in ub_acc:
                    ubc.update(comp["chains_by_accession"][a])
                sgs = [a for a in aprot if a["chain"] in e2c and a["resname"] == "CYS" and a["name"] == "SG"]
                ub_res = sorted({a["resid"] for a in aprot if a["chain"] in ubc})
                ub_ct = [a["xyz"] for a in aprot
                         if a["chain"] in ubc and a["resid"] == ub_res[-1] and a["name"] in ("C", "CA")]
                if not sgs or not ub_ct:
                    continue
                ranked = sorted(((min(G.dist(a["xyz"], u) for u in ub_ct), a) for a in sgs), key=lambda t: t[0])
                d_ub, cat = ranked[0]
                acbp = {b: set(comp["chains_by_accession"].get(ACC[b], [])) for b in obligate}
                acbp = {k: v for k, v in acbp.items() if v}
                asel, _ainfo = select_assembly_copy(aprot, acbp)
                src_map, dst_map = {}, {}
                for bname in obligate:
                    sc = {asel[bname]} if (asel and bname in asel) else set(
                        comp["chains_by_accession"].get(ACC[bname], []))
                    dc = ({recep_copy[bname]} if (recep_copy and bname in recep_copy)
                          else set(recep_comp["chains_by_accession"].get(ACC[bname], [])))
                    if sc and dc:
                        src_map[bname], dst_map[bname] = sc, dc
                if not src_map:
                    continue
                tr, binfo = bridge_into_frame(aprot, src_map, recep_prot, dst_map)
                if tr is None:
                    continue
                R, t = tr
                cys_frame = G.apply_superpose([cat["xyz"]], R, t)[0]
                rbx = set(comp["chains_by_accession"].get(ACC["RBX1"], []))
                ring_frame = None
                if rbx:
                    cen, _rng = ring_domain_centroid(aprot, rbx)
                    if cen:
                        ring_frame = G.apply_superpose([cen], R, t)[0]
                log(f"[e3stage] {arm_id}: INTACT assembly {pdb} ({comp['title'][:70]}) bridged on "
                    f"{binfo['n_bridge_ca']} CA @ {binfo['bridge_rmsd_A']} A -> observed E2 catalytic "
                    f"Cys{cat['resid']} placed directly in the receptor frame (Ub C-term {d_ub:.1f} A)")
                return {
                    "pdb_id": pdb, "title": comp["title"], "method": comp.get("method"),
                    "resolution_A": comp.get("resolution_A"),
                    "e2": e2name, "catalytic_cys_resid": cat["resid"],
                    "catalytic_cys_to_ubiquitin_cterm_A": round(d_ub, 2),
                    "bridge": binfo,
                    "catalytic_cys_xyz_in_receptor_frame": [round(c, 3) for c in cys_frame],
                    "ring_xyz_in_receptor_frame": ([round(c, 3) for c in ring_frame] if ring_frame else None),
                }
            except Exception as exc:                                    # noqa: BLE001
                log(f"[e3stage] {arm_id}: intact candidate {pdb} failed: {exc}")
                continue
    return None


def validate_composition_against_solved_assembly(arms, e2, log):
    """KNOWN-ANSWER CHECK on this script's own two-structure composition.

    Every arm's RING position is COMPOSED — a ligand-bound receptor entry plus a separate cullin-scaffold
    entry, bridged by superposition. Nothing so far says that composition lands the RING where a real,
    intact assembly puts it, and the RING is what the entire term-(b) transfer zone hangs off.

    The E2-geometry step happens to retrieve exactly the structure that can answer it: a complete solved CRL
    ubiquitylation assembly. Where an arm shares a bridge protein with that assembly, we superpose the
    assembly into the arm's frame and measure how far the DIRECTLY OBSERVED RING sits from the COMPOSED one.
    A small displacement means the composition reproduces an intact CRL; a large one means it does not, and
    the transfer zone built on it must be treated as a model rather than a placement. Either way it is
    measured and reported, not assumed.
    """
    info = e2.get("_composition_check_inputs")
    if not info:
        return
    try:
        text = _get(FILE_URL.format(pdb=info["pdb_id"])).decode("utf-8", "replace")
        aprot, _ = parse_pdb_text(text)
    except Exception as exc:                                            # noqa: BLE001
        log(f"[e3stage] composition check skipped: {exc}")
        return
    for aid, rec in arms.items():
        ring = rec.get("ring")
        if rec.get("status") != "OK" or not ring:
            continue
        spec = ARMS[aid]
        recep = (rec.get("provenance") or {}).get("receptor_entry", {})
        src_map, dst_map = {}, {}
        sel = rec.get("_receptor_copy_chains") or {}
        for bname in spec["bridge"]:
            s = set(info["chains_by_accession"].get(ACC[bname], []))
            d = ({sel[bname]} if bname in sel
                 else set((recep.get("chains_by_accession") or {}).get(ACC[bname], [])))
            if s and d:
                src_map[bname], dst_map[bname] = s, d
        if not src_map:
            rec["composition_check"] = {"possible": False,
                                        "reason": f"{info['pdb_id']} shares no bridge protein with this arm"}
            continue
        try:
            path = os.path.join(REPO, rec["receptor_pdb"])
            with open(path) as fh:
                dprot, _ = parse_pdb_text(fh.read())
        except Exception as exc:                                        # noqa: BLE001
            rec["composition_check"] = {"possible": False, "reason": str(exc)}
            continue
        tr, binfo = bridge_into_frame(aprot, src_map, dprot, dst_map)
        if tr is None:
            rec["composition_check"] = {"possible": False, "reason": binfo["reason"]}
            continue
        R, t = tr
        obs_ring = G.apply_superpose([tuple(info["ring_centroid_xyz"])], R, t)[0]
        obs_cys = G.apply_superpose([tuple(info["catalytic_cys_xyz"])], R, t)[0]
        comp_ring = tuple(ring["ring_centroid_xyz"])
        anchor = tuple(rec["ligand"]["exit_atom_xyz"])
        rec["composition_check"] = {
            "possible": True,
            "reference_pdb": info["pdb_id"], "reference_title": e2.get("title"),
            "bridge": binfo,
            "composed_ring_xyz": [round(c, 2) for c in comp_ring],
            "observed_ring_xyz": [round(c, 2) for c in obs_ring],
            "ring_displacement_A": round(G.dist(comp_ring, obs_ring), 2),
            "anchor_to_composed_ring_A": round(G.dist(anchor, comp_ring), 2),
            "anchor_to_observed_ring_A": round(G.dist(anchor, obs_ring), 2),
            "anchor_to_observed_catalytic_cys_A": round(G.dist(anchor, obs_cys), 2),
            "_reading": "How far this script's COMPOSED RING sits from the RING of an intact solved CRL "
                        "assembly placed in the same frame. The term-(b) transfer zone hangs off the RING, so "
                        "this is the error bar on the zone's placement — reported whatever it says.",
        }
        log(f"[e3stage] {aid} composition check vs {info['pdb_id']}: composed RING is "
            f"{rec['composition_check']['ring_displacement_A']} A from the observed one "
            f"(bridge {binfo['n_bridge_ca']} CA @ {binfo['bridge_rmsd_A']} A); anchor->RING composed "
            f"{rec['composition_check']['anchor_to_composed_ring_A']} vs observed "
            f"{rec['composition_check']['anchor_to_observed_ring_A']} A")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arms", default="vhl,crbn", help="comma-separated arm ids from ARMS")
    ap.add_argument("--lane1-registry", default="",
                    help="path to the E3 lane's recruiter-staging JSON; its recruiters are added as arms "
                         "(the CRL architecture per recruiter is supplied here, since that lane's output is "
                         "a flat recruiter list and the RING geometry depends on the architecture)")
    ap.add_argument("--lane1-only", default="",
                    help="comma-separated recruiter GENE symbols to take from the lane-1 registry "
                         "(default: all of them). Use the lane's own downselect to choose.")
    ap.add_argument("--out-dir", default=STAGE_DIR)
    ap.add_argument("--registry", default=REGISTRY)
    ap.add_argument("--plan", action="store_true", help="offline: print the queries, touch no network")
    args = ap.parse_args(argv)

    if args.lane1_registry:
        only = {g.strip().upper() for g in args.lane1_only.split(",") if g.strip()} or None
        added = arms_from_lane1(args.lane1_registry, only=only)
        ARMS.update(added)
        print(f"[e3stage] lane-1 registry {args.lane1_registry}: added arms {sorted(added)}")
        for k, v in sorted(added.items()):
            print(f"[e3stage]   {k}: {v['recruiter']} ({v['e3_architecture']}) "
                  f"self_ring={v.get('self_ring', False)} seeds={v['seed_ids'][:4]}")
        if not args.arms.strip():
            args.arms = ",".join(sorted(added))

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
            if s.get("scaffold_needs"):
                print(f"    scaffold query : accessions {[ACC[n] for n in s['scaffold_needs']]} "
                      f"({s['scaffold_needs']})")
                print(f"    bridge on      : {s['bridge']}")
            else:
                print("    scaffold query : NONE — monomeric RING E3, so the RING is in the recruiter's own "
                      "chain and no cullin scaffold is composed in (none of the measured 48.6 A composition "
                      "uncertainty is inherited)")
            print("    intact-assembly query : recruiter + each E2, ubiquitin REQUIRED — the preferred "
                  "transfer-geometry source")
            print(f"    seed hints (must still verify): {s['seed_ids'][:6]}")
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
            import traceback
            log(f"[e3stage] arm {a} FAILED: {type(e).__name__}: {e}")
            log(traceback.format_exc())
            arms[a] = {"arm_id": a, "status": f"FAILED_{type(e).__name__}", "error": str(e)}
    e2 = stage_e2_geometry(log)
    if e2:
        validate_composition_against_solved_assembly(arms, e2, log)

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
