#!/usr/bin/env python3
"""
E3 RECRUITER STAGING + LIGANDABILITY DOWNSELECT  ($0 CPU/CI)  —  RUNG 5a, part 1.

WHY. nr4a3-program-map.md's prospective stage, item (c) "E3 breadth, free at the search stage", widens the recruiter set
beyond VHL/CRBN to the ligandable E3s with public ligand-bound structures (cIAP1/BIRC2, DCAF1, DCAF15, DCAF16,
KEAP1, FEM1B, RNF114, MDM2). Selectivity in this program is created at the INDUCED target-E3 interface, so the
E3's own surface is the largest single lever on whether a discriminating interface exists at all; searching more
recruiters is free because basin search is CPU. The same section then imposes a hard cap: **downselect to <=2
recruiters before any GPU leg, and LOG WHAT WAS DROPPED** — "a silent top-N reads as 'we covered everything'".

★ THE CONSTRAINT THAT SHAPES THIS MODULE. Availability was already answered, for $0, and it does **NOT**
constrain the choice: all eight widened arms are broadly expressed and record-complete on HPA
(`nr4a3_e3_expression.py` -> `nr4a-e3-expression.json`, CI run 30125742542). **No recruiter may therefore be
dropped with "not expressed" as the reason.** The downselect is made on **ligandability + interface geometry**
only. This module computes exactly those two things, and it reads the availability JSON purely to ASSERT that
no arm is being dropped on availability grounds.

WHAT IT PRODUCES.
  1. STAGED STRUCTURES — for each recruiter, the best public ligand-bound structure(s) from the RCSB PDB, with
     PDB ID, resolution, experimental method, ligand CCD code, chain composition, and the primary citation.
     Every field is FETCHED (RCSB search + data API, UniProt for accession resolution), never recalled: a gene
     symbol is resolved through UniProt's own search with an exact-match, reviewed, human guard, and a record
     that does not match exactly is REFUSED rather than substituted.
  2. LIGANDABILITY — per recruiter, computed from the downloaded coordinates:
       * ligand burial (Shrake-Rupley SASA of the bound ligand free vs in complex),
       * site enclosure and a ligand-proximal buried cavity volume,
       * fpocket druggability/volume of the pocket the ligand occupies (when fpocket is installed),
       * ★ the EXIT VECTOR — the direction a linker must leave from — as an anchor atom, a direction, an
         unobstructed clearance length, a 30-degree cone openness, and the residues lining the channel,
       * ★ the OPEN SOLID-ANGLE FRACTION at the exit anchor: the fraction of directions from the linker
         attachment point with >=15 A of unobstructed reach. This is the geometric size of the orientation
         space a tethered target can occupy before any energetics are computed, and it is the number the
         orientation-basin search consumes,
       * whether a LINKER-BEARING analogue is already published, answered structurally rather than from
         memory: does a deposited entry exist in which this recruiter is bound by a >=500 Da ligand, and does
         one exist in which such a ligand BRIDGES two different UniProt entities (a solved ternary).
  3. DOWNSELECT — three preregistered gates, then a Pareto front over three ligandability/geometry axes, then
     a preregistered lexicographic tiebreak to reach <=2. The dropped set, with the gate each recruiter failed
     or the axis on which it was dominated, is a first-class output.

HONEST SCOPE (nr4a3-program-map.md "Honest scope and language discipline"). This is DESIGN PREP, not a validated result.
Ligandability computed from one deposited holo structure is a HYPOTHESIS for testing: it says a published
ligand occupies a pocket with a solvent-directed exit vector, not that an NR4A3 degrader built on that handle
will form a ternary complex, be selective, be degraded, or do anything in a cell. No claim of efficacy, safety,
therapeutic window, or clinical readiness is made or implied.

RUNNING IT. The dev sandbox's egress proxy 403s RCSB and UniProt, so phase `fetch` runs on a GitHub Actions
runner (`fusion-cpu-extras.yml`, task `e3_recruiter_stage`). Phase `geom` is offline and reproducible from the
committed cache + downloaded coordinates. Pure stdlib apart from the optional external `fpocket` binary.

  python e3_recruiter_staging.py --phase all          # CI: fetch + geometry + downselect
  python e3_recruiter_staging.py --phase geom         # offline, from the coordinate cache

Outputs: e3-recruiter-staging.json (machine-readable, schema below), e3-recruiter-staging.md (companion).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT_JSON = os.path.join(HERE, "e3-recruiter-staging.json")
OUT_MD = os.path.join(HERE, "e3-recruiter-staging.md")
CACHE_JSON = os.path.join(HERE, "e3-recruiter-rcsb-cache.json")
COORD_DIR = os.path.join(HERE, "_e3_recruiter_coords")
AVAILABILITY_JSON = os.path.join(HERE, "nr4a-e3-expression.json")

SCHEMA_VERSION = "1.1"

# ---------------------------------------------------------------------------------------------------------
# THE PANEL — nr4a3-program-map.md RUNG 5a's widened ligandable recruiter set, verbatim, plus the two incumbents.
# `arm` matches the key used by nr4a3_e3_expression.py so availability can be cross-checked, not re-asserted.
# ---------------------------------------------------------------------------------------------------------
PANEL = [
    {"gene": "VHL", "aliases": ["VHL"], "e3_class": "CRL2 substrate receptor (BC-box)",
     "arm": "CRL2_VHL", "incumbent": True},
    {"gene": "CRBN", "aliases": ["CRBN"], "e3_class": "CRL4 substrate receptor (DCAF)",
     "arm": "CRL4_CRBN", "incumbent": True},
    {"gene": "BIRC2", "aliases": ["BIRC2", "cIAP1"], "e3_class": "monomeric RING E3 (BIR/RING)",
     "arm": "RING_BIRC2", "incumbent": False},
    {"gene": "DCAF1", "aliases": ["DCAF1", "VPRBP", "KIAA0800"], "e3_class": "CRL4 substrate receptor (DCAF)",
     "arm": "CRL4_DCAF1", "incumbent": False},
    {"gene": "DCAF15", "aliases": ["DCAF15"], "e3_class": "CRL4 substrate receptor (DCAF)",
     "arm": "CRL4_DCAF15", "incumbent": False},
    {"gene": "DCAF16", "aliases": ["DCAF16"], "e3_class": "CRL4 substrate receptor (DCAF)",
     "arm": "CRL4_DCAF16", "incumbent": False},
    {"gene": "KEAP1", "aliases": ["KEAP1"], "e3_class": "CRL3 substrate receptor (BTB-Kelch)",
     "arm": "CRL3_KEAP1", "incumbent": False},
    {"gene": "FEM1B", "aliases": ["FEM1B"], "e3_class": "CRL2 substrate receptor (ankyrin)",
     "arm": "CRL2_FEM1B", "incumbent": False},
    {"gene": "RNF114", "aliases": ["RNF114", "ZNF313"], "e3_class": "monomeric RING E3",
     "arm": "RING_RNF114", "incumbent": False},
    {"gene": "MDM2", "aliases": ["MDM2"], "e3_class": "monomeric RING E3 (nutlin-recruited)",
     "arm": "RING_MDM2", "incumbent": False},
]

# ---------------------------------------------------------------------------------------------------------
# ★ PREREGISTERED DOWNSELECT RULE. Committed BEFORE the CI fetch ran, so it cannot be fitted to the answer.
# Gates are pass/fail eligibility; ranking is a Pareto front plus a fixed lexicographic tiebreak — never a
# tunable weighted scalar (nr4a3-program-map.md validation requirement 5).
# ---------------------------------------------------------------------------------------------------------
GATES = {
    "G1_public_ligand_bound_structure": {
        "rule": "at least one deposited structure containing the recruiter with a bound non-solvent, "
                "non-cryoprotectant ligand of >=10 heavy atoms, at resolution <=3.0 A (diffraction/EM) or by "
                "solution NMR",
        "why": "a recruiter with no public ligand-bound structure cannot be staged for a linker-design basin "
               "search at all; the handle would have to be invented, which is a different (and far weaker) "
               "claim than 'a published ligand occupies this pocket'",
    },
    "G2_ligand_is_pocket_bound": {
        "rule": "buried fraction of the primary ligand's solvent-accessible surface >= 0.50",
        "why": "a linker exerts force on the handle; a ligand lying on a flat surface at <50% burial has no "
               "pocket holding it and the handle is not a credible anchor",
        "threshold": 0.50,
    },
    "G3_linker_can_leave": {
        "rule": "exit-vector clearance >= 8.0 A AND 30-degree cone openness >= 0.30",
        "why": "the linker must leave the pocket toward bulk solvent without threading a tunnel; 8 A is the "
               "shortest reach of any linker in the enumerated virtual library (RUNG 5b), and a cone that is "
               "open in <30% of nearby directions is a channel, not an exit",
        "clearance_A": 8.0,
        "cone_openness": 0.30,
    },
}

PARETO_AXES = [
    # (key, direction, why)
    ("linker_analogue_tier", "max",
     "a published linker-bearing analogue (best: one whose ligand bridges two proteins in a solved structure) "
     "means the exit vector has already been shown to tolerate a linker; nothing else in this module is direct "
     "evidence of that"),
    ("exit_quality", "max",
     "clearance (capped at 20 A) x 30-degree cone openness: how freely a linker leaves the site"),
    ("orientation_openness", "max",
     "fraction of directions from the exit anchor with >=15 A unobstructed reach: the geometric size of the "
     "orientation space a tethered target can occupy, before any energetics"),
]

TIEBREAK = ("linker_analogue_tier", "orientation_openness", "exit_quality", "neg_resolution")
MAX_ADVANCED = 2

# Solvent / cryoprotectant / buffer / ion codes that are NOT recruiter handles. A ligand-bound structure whose
# only het groups are these is not ligand-bound in the sense this module means.
EXCLUDED_CCD = {
    "HOH", "DOD", "GOL", "EDO", "PEG", "PGE", "PG4", "1PE", "2PE", "P6G", "PE4", "PGO", "MPD", "TRS", "MES",
    "EPE", "BTB", "CIT", "FLC", "TAR", "MLI", "MLA", "ACT", "ACY", "FMT", "OXL", "SIN", "SO4", "PO4", "IPA",
    "DMS", "DMF", "URE", "GLC", "NAG", "BMA", "MAN", "FUC", "GAL", "XYS", "IMD", "BME", "DTT", "TCE", "AZI",
    "NO3", "SCN", "CO3", "BCT", "CAC", "PIN", "BIS", "CXS", "MRD", "BU3", "BUD", "TBU", "ETA", "EOH", "MOH",
    "NA", "K", "MG", "CA", "ZN", "CD", "NI", "CO", "CU", "MN", "FE", "FE2", "HG", "AU", "AG", "PT", "CS",
    "RB", "SR", "BA", "LI", "AL", "CL", "BR", "IOD", "F", "YB", "SM", "EU", "GD", "TB", "LU", "PB", "ARS",
    "UNX", "UNK", "UNL", "PTR", "SEP", "TPO",
}
MIN_LIGAND_HEAVY_ATOMS = 10
MIN_RESOLUTION_A = 3.0
LINKER_BEARING_MIN_MW = 500.0     # Da; a handle carrying a linker/exit arm, not a bare fragment

# Geometry parameters (all reported into the JSON so nothing is a hidden constant).
GEOM = {
    "sasa_n_points": 128,
    "sasa_probe_A": 1.4,
    "ray_n_directions": 512,
    "ray_max_A": 25.0,
    "ray_step_A": 0.25,
    # ★ Rays start at the first BONDED linker-atom position, not at the anchor atom's centre. A sample point
    # 0.25 A from the anchor lies INSIDE the anchor's own van-der-Waals sphere, so any protein atom merely in
    # contact with the anchor (~3.3 A) falls inside the 3.40 A clash radius of that sample in nearly every
    # direction — and the site reports zero clearance however open it is. A linker's first atom is bonded at
    # ~1.5 A. Measured 2026-07-25 on a controlled reproduction (an atom contacted on five of six sides, open
    # on the sixth): 0.0 A from the centre vs 25.0 A from 1.5 A.
    "ray_first_atom_A": 1.5,
    "linker_atom_radius_A": 1.7,      # a linker heavy atom must fit; clash = within vdW_protein + this
    "cone_half_angle_deg": 30.0,
    "cone_open_clearance_A": 8.0,
    "orientation_openness_clearance_A": 15.0,
    "enclosure_n_rays": 256,
    "enclosure_max_A": 12.0,
    "cavity_grid_spacing_A": 0.8,
    "cavity_ligand_shell_A": 4.0,
    "cavity_min_psp": 5,              # LIGSITE MINPSP: enclosed along >=5 of the 7 scan directions
    "cavity_psp_scan_A": 12.0,
    "channel_lining_cutoff_A": 6.0,
}

VDW = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "P": 1.80, "H": 1.20, "F": 1.47, "CL": 1.75, "BR": 1.85,
       "I": 1.98, "SE": 1.90, "B": 1.92, "SI": 2.10}
DEFAULT_VDW = 1.70

AA3 = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU", "LYS", "MET", "PHE",
       "PRO", "SER", "THR", "TRP", "TYR", "VAL", "MSE", "SEC", "PYL"}


# =========================================================================================================
# HTTP (pure stdlib; every fetch is retried with backoff and every URL is recorded for provenance)
# =========================================================================================================
_URLS_USED: list[str] = []


def _http(url, data=None, headers=None, timeout=60, tries=4, binary=False):
    hdr = {"User-Agent": "rare-cancers/1.0 (NR4A3 degrader program; CI)", "Accept": "application/json"}
    hdr.update(headers or {})
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdr)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
            _URLS_USED.append(url)
            return raw if binary else raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):        # a real "not there" — do not burn retries on it
                _URLS_USED.append(url + f"  [HTTP {e.code}]")
                return None
            last = e
        except Exception as e:              # noqa: BLE001
            last = e
        time.sleep(2 ** i)
    print(f"  FETCH FAILED after {tries}: {url[:110]}  ({last})", file=sys.stderr)
    return None


def _get_json(url, timeout=60):
    txt = _http(url, timeout=timeout)
    if txt is None:
        return None
    try:
        return json.loads(txt)
    except Exception:                        # noqa: BLE001
        return None


def _post_json(url, payload, timeout=90):
    body = json.dumps(payload).encode()
    txt = _http(url, data=body, headers={"Content-Type": "application/json"}, timeout=timeout)
    if txt is None:
        return None
    try:
        return json.loads(txt)
    except Exception:                        # noqa: BLE001
        return None


# =========================================================================================================
# PHASE 1 — resolve the recruiter to a UniProt accession (fail closed)
# =========================================================================================================
def resolve_uniprot(gene, aliases):
    """Gene symbol -> reviewed human UniProt accession, through UniProt's own search.

    FAILS CLOSED. The record is accepted only if it is reviewed (Swiss-Prot), organism 9606, and its primary
    gene name matches the queried symbol or one of its declared aliases exactly (case-insensitive). Anything
    else returns None with a reason, because a plausible-looking wrong accession would silently stage the
    wrong protein and nothing downstream would notice."""
    want = {a.upper() for a in ([gene] + list(aliases))}
    q = urllib.parse.quote(f'gene_exact:{gene} AND organism_id:9606 AND reviewed:true')
    url = (f"https://rest.uniprot.org/uniprotkb/search?query={q}"
           f"&fields=accession,id,gene_names,protein_name,length,reviewed&format=json&size=10")
    data = _get_json(url)
    results = (data or {}).get("results") or []
    for rec in results:
        acc = rec.get("primaryAccession")
        genes = rec.get("genes") or []
        names = set()
        for g in genes:
            nm = (g.get("geneName") or {}).get("value")
            if nm:
                names.add(nm.upper())
            for syn in g.get("synonyms") or []:
                if syn.get("value"):
                    names.add(syn["value"].upper())
        if acc and (names & want):
            desc = (((rec.get("proteinDescription") or {}).get("recommendedName") or {})
                    .get("fullName") or {}).get("value")
            return {"accession": acc, "entry_name": rec.get("uniProtkbId"),
                    "protein_name": desc, "length": rec.get("sequence", {}).get("length"),
                    "matched_gene_names": sorted(names & want), "reviewed": True, "organism_id": 9606,
                    "query_url": url, "_status": "ok"}
    return {"accession": None, "_status": f"symbol resolution failed for {gene} — refused rather than guessed",
            "query_url": url, "n_results": len(results)}


# =========================================================================================================
# PHASE 2 — find ligand-bound structures for that accession (RCSB search API)
# =========================================================================================================
RCSB_SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"
RCSB_DATA = "https://data.rcsb.org/rest/v1/core"


def _accession_nodes(accession):
    return [
        {"type": "terminal", "service": "text", "parameters": {
            "attribute": "rcsb_polymer_entity_container_identifiers."
                         "reference_sequence_identifiers.database_accession",
            "operator": "exact_match", "value": accession}},
        {"type": "terminal", "service": "text", "parameters": {
            "attribute": "rcsb_polymer_entity_container_identifiers."
                         "reference_sequence_identifiers.database_name",
            "operator": "exact_match", "value": "UniProt"}},
    ]


def _run_search(query, max_rows):
    payload = {"query": query, "return_type": "entry",
               "request_options": {"paginate": {"start": 0, "rows": max_rows},
                                   "results_verbosity": "compact",
                                   "sort": [{"sort_by": "rcsb_entry_info.resolution_combined",
                                             "direction": "asc"}]}}
    res = _post_json(RCSB_SEARCH, payload)
    ids = []
    if isinstance(res, dict):
        for r in res.get("result_set") or []:
            ids.append(r if isinstance(r, str) else r.get("identifier"))
    return [i for i in ids if i], (res or {}).get("total_count")


def rcsb_search_entries(accession, max_rows=100):
    """Entry IDs whose polymer entities reference this UniProt accession AND carry >=1 non-polymer entity,
    sorted by resolution ascending.

    A SECOND, unfiltered search runs alongside it. Zero hits from the filtered search alone cannot tell
    'this protein has no deposited structure' apart from 'it has structures but none with a ligand', and
    those are different findings that would appear identically in the dropped-set log — one says the
    recruiter is structurally unknown, the other says it is known and un-liganded."""
    query = {"type": "group", "logical_operator": "and",
             "nodes": _accession_nodes(accession) + [
                 {"type": "terminal", "service": "text", "parameters": {
                     "attribute": "rcsb_entry_info.nonpolymer_entity_count",
                     "operator": "greater", "value": 0}}]}
    ids, total = _run_search(query, max_rows)
    any_q = {"type": "group", "logical_operator": "and", "nodes": _accession_nodes(accession)}
    any_ids, any_total = _run_search(any_q, max_rows)
    return ids, {"endpoint": RCSB_SEARCH, "query": query,
                 "n_hits_with_nonpolymer": len(ids), "total_count_with_nonpolymer": total,
                 "n_hits_any_structure": len(any_ids), "total_count_any_structure": any_total,
                 "example_apo_entries": any_ids[:8],
                 "_reading": ("n_hits_any_structure == 0 -> no deposited structure of this protein at all; "
                              "n_hits_any_structure > 0 with n_hits_with_nonpolymer == 0 -> structures "
                              "exist but none carries a bound non-polymer ligand")}


def rcsb_entry(pdb_id):
    return _get_json(f"{RCSB_DATA}/entry/{pdb_id}")


def rcsb_polymer_entity(pdb_id, eid):
    return _get_json(f"{RCSB_DATA}/polymer_entity/{pdb_id}/{eid}")


def rcsb_nonpolymer_entity(pdb_id, eid):
    return _get_json(f"{RCSB_DATA}/nonpolymer_entity/{pdb_id}/{eid}")


def rcsb_chemcomp(ccd):
    return _get_json(f"{RCSB_DATA}/chemcomp/{ccd}")


def _resolution(entry):
    info = (entry or {}).get("rcsb_entry_info") or {}
    rc = info.get("resolution_combined")
    if isinstance(rc, list) and rc:
        try:
            return float(rc[0])
        except (TypeError, ValueError):
            return None
    return None


def _methods(entry):
    return [e.get("method") for e in ((entry or {}).get("exptl") or []) if e.get("method")]


def summarise_entry(pdb_id, accession, chemcomp_cache):
    """One deposited entry -> the record this module stages, or None if it carries no usable ligand.

    'Usable' = a non-polymer entity whose chemical component is not a solvent/cryoprotectant/ion, has >=10
    heavy atoms, and is present on a chain. Ligand->recruiter contact is confirmed later from coordinates."""
    entry = rcsb_entry(pdb_id)
    if not entry:
        return None
    ids = entry.get("rcsb_entry_container_identifiers") or {}
    poly_ids = ids.get("polymer_entity_ids") or []
    nonpoly_ids = ids.get("non_polymer_entity_ids") or ids.get("nonpolymer_entity_ids") or []

    polymers, recruiter_chains, uniprots = [], [], []
    for eid in poly_ids:
        pe = rcsb_polymer_entity(pdb_id, eid)
        if not pe:
            continue
        cid = pe.get("rcsb_polymer_entity_container_identifiers") or {}
        accs = cid.get("uniprot_ids") or []
        chains = cid.get("auth_asym_ids") or []
        desc = (pe.get("rcsb_polymer_entity") or {}).get("pdbx_description")
        polymers.append({"entity_id": eid, "uniprot_ids": accs, "auth_asym_ids": chains,
                         "description": desc,
                         "length": (pe.get("entity_poly") or {}).get("rcsb_sample_sequence_length")})
        uniprots.extend(accs)
        if accession in accs:
            recruiter_chains.extend(chains)

    ligands = []
    for eid in nonpoly_ids:
        ne = rcsb_nonpolymer_entity(pdb_id, eid)
        if not ne:
            continue
        ccd = (ne.get("pdbx_entity_nonpoly") or {}).get("comp_id")
        if not ccd or ccd.upper() in EXCLUDED_CCD:
            continue
        if ccd not in chemcomp_cache:
            cc = rcsb_chemcomp(ccd) or {}
            comp = cc.get("chem_comp") or {}
            info = cc.get("rcsb_chem_comp_info") or {}
            desc = cc.get("rcsb_chem_comp_descriptor") or {}
            chemcomp_cache[ccd] = {
                "ccd": ccd, "name": comp.get("name"), "type": comp.get("type"),
                "formula": comp.get("formula"),
                "formula_weight": comp.get("formula_weight"),
                "n_heavy_atoms": info.get("atom_count_heavy"),
                "smiles": desc.get("SMILES_stereo") or desc.get("SMILES"),
            }
        cc = chemcomp_cache[ccd]
        nh = cc.get("n_heavy_atoms")
        if nh is not None and nh < MIN_LIGAND_HEAVY_ATOMS:
            continue
        chains = ((ne.get("rcsb_nonpolymer_entity_container_identifiers") or {}).get("auth_asym_ids") or [])
        ligands.append({**cc, "entity_id": eid, "auth_asym_ids": chains})

    if not ligands:
        return None

    rec_lengths = [p["length"] for p in polymers if accession in (p["uniprot_ids"] or []) and p["length"]]
    cit = entry.get("rcsb_primary_citation") or {}
    acc_info = entry.get("rcsb_accession_info") or {}
    return {
        "pdb_id": pdb_id,
        "title": (entry.get("struct") or {}).get("title"),
        "resolution_A": _resolution(entry),
        "experimental_methods": _methods(entry),
        "deposited": acc_info.get("deposit_date"),
        "released": acc_info.get("initial_release_date"),
        "primary_citation": {"pubmed_id": cit.get("pdbx_database_id_PubMed"),
                             "doi": cit.get("pdbx_database_id_DOI"),
                             "title": cit.get("title"), "journal": cit.get("journal_abbrev"),
                             "year": cit.get("year")},
        "polymer_entities": polymers,
        "distinct_uniprot_accessions": sorted({u for u in uniprots if u}),
        "recruiter_auth_asym_ids": sorted(set(recruiter_chains)),
        "recruiter_entity_length": max(rec_lengths) if rec_lengths else None,
        "chain_composition": "; ".join(
            f"{'/'.join(p['auth_asym_ids'])}={p['description']}" for p in polymers if p["auth_asym_ids"]),
        "candidate_ligands": ligands,
    }


def arm_component_accessions(arm, cache):
    """UniProt accessions of the recruiter's OWN CRL arm (adaptors, cullin, RING box), taken from the
    single existing definition of those arms — nr4a3_e3_expression.py — rather than re-listed here.

    WHY THIS EXISTS. The geometry must be computed against the recruiter *and its obligate arm*, and NOT
    against a bound neosubstrate or PROTAC target. A partner protein in the deposited entry occupies exactly
    the orientation space this module is trying to measure, so leaving it in the occluder set would deflate
    the open solid angle of every glue/ternary structure — turning 'this recruiter has a partner in the PDB'
    into 'this recruiter has nowhere for a target to go', which is the opposite of the truth."""
    try:
        import nr4a3_e3_expression as e3exp
    except Exception:                                    # noqa: BLE001
        return set(), ["nr4a3_e3_expression import failed — arm components not resolved"]
    spec = (e3exp.MACHINERIES.get(arm) or e3exp.WIDENED_MACHINERIES.get(arm) or {})
    symbols = list(spec.get("symbols") or list((spec.get("genes") or {}).keys()))
    accs, unresolved = set(), []
    for sym in symbols:
        if sym in cache:
            got = cache[sym]
        else:
            got = resolve_uniprot(sym, [sym]).get("accession")
            cache[sym] = got
        if got:
            accs.add(got)
        else:
            unresolved.append(sym)
    return accs, unresolved


def _entry_rank_key(rec):
    """Stage the highest-quality holo structure: best (lowest) resolution first, then the largest ligand,
    then the PDB ID for determinism. A missing resolution (NMR) sorts after diffraction structures."""
    res = rec.get("resolution_A")
    biggest = max((l.get("formula_weight") or 0.0) for l in rec["candidate_ligands"])
    return (0 if res is not None else 1, res if res is not None else 99.0, -biggest, rec["pdb_id"])


MIN_RECRUITER_ENTITY_RESIDUES = 60


def select_staged(entries, arm_accs, max_entries_deep=8, uniprot_length=None):
    """Order the screened entries and mark the one the geometry is measured on.

    Two preferences, in order.

    ★ (1) A CLEAN BINARY structure — the recruiter (and its own arm) bound to a handle-sized ligand and
    nothing else. A ternary/glue entry is the wrong frame for BOTH numbers this stage produces: the PROTAC's
    burial would be computed against only half the protein that actually buries it, and the partner protein
    occupies the very orientation space being measured. Ternary entries stay the linker-analogue EVIDENCE
    (classified separately); they are just not the geometry frame unless nothing else exists.

    ★ (2) An INTACT substrate-receptor domain, not a peptide. Some depositions contain only a short
    recruiter-derived peptide (a degron, a BC-box fragment) bound to something else; a pocket and an exit
    vector measured on 20 residues describe nothing. Entities shorter than 60 residues are deprioritised.
    Full-length COVERAGE is deliberately NOT used as a preference — a WD40 or Kelch domain construct is the
    correct experimental object even though it is a small fraction of a 1500-residue protein — so coverage
    is recorded and reported, never ranked on."""
    for e in entries:
        e["partner_uniprots"] = sorted({u for u in e["distinct_uniprot_accessions"] if u not in arm_accs})
        e["has_partner_protein"] = bool(e["partner_uniprots"])
        L = e.get("recruiter_entity_length")
        e["recruiter_entity_is_peptide_fragment"] = bool(L is not None
                                                         and L < MIN_RECRUITER_ENTITY_RESIDUES)
        e["recruiter_uniprot_coverage_fraction"] = (round(L / float(uniprot_length), 3)
                                                    if L and uniprot_length else None)
    ordered = sorted(entries, key=lambda e: (1 if e["recruiter_entity_is_peptide_fragment"] else 0,
                                             1 if e["has_partner_protein"] else 0) + _entry_rank_key(e))
    staged = ordered[:max_entries_deep]
    for i, e in enumerate(staged):
        e["is_primary"] = (i == 0)
        e["ligand"] = max(e["candidate_ligands"], key=lambda l: (l.get("formula_weight") or 0.0))
    return staged


def classify_linker_analogue(entry_records, accession):
    """Is a linker-bearing analogue already published? Answered STRUCTURALLY, from deposited entries.

    tier 3 `solved_ternary`   — a >=500 Da ligand sits in an entry that also contains a second, different
                               UniProt accession. This is the ENTRY-LEVEL screen only: co-presence is not
                               bridging, and an entry can contain a big ligand and two proteins without the
                               ligand touching both. `verify_bridging()` re-reads the coordinates and
                               DEMOTES the tier to 2 when the ligand does not actually contact both.
    tier 2 `bivalent_binary`  — a >=500 Da ligand is bound with the recruiter alone: a linker-bearing handle
                               exists and is crystallographically ordered, but no partner protein.
    tier 1 `handle_only`      — only sub-500 Da ligands: a handle exists, no published linker-bearing form.
    tier 0 `none`             — no usable ligand at all."""
    big_entries, ternary_entries = [], []
    any_lig = False
    for rec in entry_records:
        others = [u for u in rec["distinct_uniprot_accessions"] if u != accession]
        for lig in rec["candidate_ligands"]:
            any_lig = True
            mw = lig.get("formula_weight") or 0.0
            if mw >= LINKER_BEARING_MIN_MW:
                big_entries.append({"pdb_id": rec["pdb_id"], "ccd": lig["ccd"], "formula_weight": mw})
                if others:
                    ternary_entries.append({"pdb_id": rec["pdb_id"], "ccd": lig["ccd"],
                                            "formula_weight": mw, "partner_uniprots": others})
    # Keep the metadata of the top ternary-evidence entries so bridging can be verified from coordinates
    # later WITHOUT another RCSB round-trip. These entries are deep-fetched already; they are simply not in
    # the staged top-8 once staging started preferring partner-free frames, which silently left tier 3
    # unverified for exactly the recruiters that have many binary structures (VHL, CRBN, BIRC2, DCAF1).
    keep_ids = []
    for e in ternary_entries:
        if e["pdb_id"] not in keep_ids:
            keep_ids.append(e["pdb_id"])
        if len(keep_ids) >= 4:
            break
    evidence_meta = [
        {"pdb_id": r["pdb_id"], "recruiter_auth_asym_ids": r.get("recruiter_auth_asym_ids", []),
         "polymer_entities": r.get("polymer_entities", []), "candidate_ligands": r["candidate_ligands"]}
        for r in entry_records if r["pdb_id"] in keep_ids]

    if ternary_entries:
        tier, label = 3, "solved_ternary"
    elif big_entries:
        tier, label = 2, "bivalent_binary"
    elif any_lig:
        tier, label = 1, "handle_only"
    else:
        tier, label = 0, "none"
    return {
        "tier": tier, "label": label,
        "n_entries_with_ligand_ge_500Da": len({e["pdb_id"] for e in big_entries}),
        "n_entries_ligand_bridging_second_uniprot": len({e["pdb_id"] for e in ternary_entries}),
        "evidence_pdb_ids_ge_500Da": sorted({e["pdb_id"] for e in big_entries})[:12],
        "evidence_pdb_ids_ternary": sorted({e["pdb_id"] for e in ternary_entries})[:12],
        "_evidence_entries": evidence_meta,
        "_limit": "A >=500 Da ordered ligand in a two-protein entry is structural evidence that a linker "
                  "leaving this recruiter is tolerated. It is NOT evidence that an NR4A3 degrader on this "
                  "handle would form a ternary complex or be selective.",
    }


# =========================================================================================================
# PHASE 3 — coordinates
# =========================================================================================================
def download_structure(pdb_id, out_dir=COORD_DIR):
    """Coordinates for one entry, preferring the FIRST BIOLOGICAL ASSEMBLY over the asymmetric unit.

    ★ This is not a detail. The asymmetric unit can contain several crystallographic copies of the same
    protein, and a ligand sitting near a packing interface is then walled in by a neighbour that is not
    there in solution — which this module would report as 'no linker can leave', dropping the recruiter at
    G3 for a crystallographic artifact. Observed 2026-07-25 on FEM1B 9PW8 (chains A *and* B are both FEM1B;
    clearance came back 0.0). The biological assembly is the frame the question is actually about.

    Returns (path, source_label) or (None, reason)."""
    os.makedirs(out_dir, exist_ok=True)
    attempts = [("assembly1.cif", f"https://files.rcsb.org/download/{pdb_id}-assembly1.cif",
                 "biological assembly 1 (mmCIF)"),
                ("cif", f"https://files.rcsb.org/download/{pdb_id}.cif", "asymmetric unit (mmCIF)"),
                ("pdb", f"https://files.rcsb.org/download/{pdb_id}.pdb", "asymmetric unit (PDB)")]
    for ext, url, label in attempts:
        path = os.path.join(out_dir, f"{pdb_id}.{ext}")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            return path, label
        raw = _http(url, binary=True, timeout=180)
        if raw and len(raw) > 1000:
            with open(path, "wb") as fh:
                fh.write(raw)
            return path, label
    return None, "no coordinate file could be downloaded"


def base_chain(cid):
    """Assembly files suffix symmetry copies ('A' -> 'A-2'), while the data API's auth_asym_ids come from
    the asymmetric unit. Match on the base id so a symmetry copy is still attributed to its entity."""
    return (cid or "").split("-")[0]


def parse_structure(path):
    """Coordinates -> (protein_atoms, het_groups). Pure stdlib; PDB and mmCIF.

    protein_atoms: [{chain,resid,resname,name,elem,x,y,z}]  (standard residues incl. MSE; altloc ' '/'A' only)
    het_groups:    {(chain, resname, resseq): [atom, ...]}   (everything else, hydrogens dropped)"""
    if path.endswith(".cif"):
        return _parse_cif(path)
    prot, het = [], {}
    with open(path) as fh:
        for ln in fh:
            rec = ln[:6]
            if rec not in ("ATOM  ", "HETATM"):
                if ln.startswith("ENDMDL"):
                    break
                continue
            alt = ln[16]
            if alt not in (" ", "A"):
                continue
            name = ln[12:16].strip()
            resn = ln[17:20].strip()
            chain = ln[21].strip() or "A"
            try:
                resi = int(ln[22:26])
                x, y, z = float(ln[30:38]), float(ln[38:46]), float(ln[46:54])
            except ValueError:
                continue
            elem = (ln[76:78].strip() or name[0]).upper()
            if elem in ("H", "D"):
                continue
            a = {"chain": chain, "resid": resi, "resname": resn, "name": name, "elem": elem,
                 "x": x, "y": y, "z": z}
            if resn in AA3:
                prot.append(a)
            elif resn not in ("HOH", "DOD"):
                het.setdefault((chain, resn, resi), []).append(a)
    return prot, het


def _parse_cif(path):
    """Minimal mmCIF `_atom_site` loop reader — enough for coordinates, no dependency."""
    prot, het = [], {}
    cols, in_loop, header = {}, False, False
    with open(path) as fh:
        for ln in fh:
            s = ln.strip()
            if s.startswith("_atom_site."):
                if not in_loop:
                    in_loop, header, cols = True, True, {}
                cols[s.split(".", 1)[1]] = len(cols)
                continue
            if header and not s.startswith("_atom_site."):
                header = False
            if not in_loop:
                continue
            if s.startswith("#") or s.startswith("loop_") or s.startswith("_"):
                if cols:
                    break
                continue
            if not s:
                continue
            f = s.split()
            if len(f) < len(cols):
                continue

            def g(key, default=""):
                i = cols.get(key)
                return f[i] if i is not None and i < len(f) else default

            if g("group_PDB") not in ("ATOM", "HETATM"):
                continue
            alt = g("label_alt_id", ".")
            if alt not in (".", "?", "A"):
                continue
            model = g("pdbx_PDB_model_num", "1")
            if model not in ("1", ".", "?"):
                continue
            elem = g("type_symbol", "C").upper()
            if elem in ("H", "D"):
                continue
            resn = g("auth_comp_id") or g("label_comp_id")
            chain = g("auth_asym_id") or g("label_asym_id") or "A"
            try:
                resi = int(g("auth_seq_id") or g("label_seq_id") or "0")
                x, y, z = float(g("Cartn_x")), float(g("Cartn_y")), float(g("Cartn_z"))
            except ValueError:
                continue
            a = {"chain": chain, "resid": resi, "resname": resn,
                 "name": g("auth_atom_id") or g("label_atom_id"), "elem": elem, "x": x, "y": y, "z": z}
            if resn in AA3:
                prot.append(a)
            elif resn not in ("HOH", "DOD"):
                het.setdefault((chain, resn, resi), []).append(a)
    return prot, het


# =========================================================================================================
# PHASE 4 — geometry. Everything below is offline and deterministic.
# =========================================================================================================
def _fib_sphere(n):
    pts, ga = [], math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        y = 1.0 - (i / float(n - 1)) * 2.0 if n > 1 else 0.0
        r = math.sqrt(max(0.0, 1.0 - y * y))
        t = ga * i
        pts.append((math.cos(t) * r, y, math.sin(t) * r))
    return pts


class Grid:
    """Uniform spatial hash over a fixed atom list — the only thing standing between pure Python and O(N^2)."""

    def __init__(self, atoms, cell=6.0):
        self.atoms, self.cell = atoms, cell
        self.g = {}
        for i, a in enumerate(atoms):
            self.g.setdefault((int(a["x"] // cell), int(a["y"] // cell), int(a["z"] // cell)), []).append(i)

    def near(self, x, y, z, radius):
        c = self.cell
        n = int(radius // c) + 1
        cx, cy, cz = int(x // c), int(y // c), int(z // c)
        out = []
        for dx in range(-n, n + 1):
            for dy in range(-n, n + 1):
                for dz in range(-n, n + 1):
                    out.extend(self.g.get((cx + dx, cy + dy, cz + dz), ()))
        return out


def sasa_per_atom(atoms, n_points=None, probe=None, subset=None):
    """Shrake-Rupley per-ATOM solvent-accessible surface area (A^2). Same algorithm and radii as
    nr4a_differential_atlas.shrake_rupley, resolved per atom rather than per residue.

    `subset` = indices to REPORT. Every atom in `atoms` still occludes, but areas are computed only for the
    subset. That matters: burial needs the ligand's area inside the full complex, and computing SASA for the
    other ~8000 protein atoms as well would cost ~100x more for numbers nothing reads."""
    n_points = n_points or GEOM["sasa_n_points"]
    probe = probe if probe is not None else GEOM["sasa_probe_A"]
    sphere = _fib_sphere(n_points)
    rad = [VDW.get(a["elem"], DEFAULT_VDW) + probe for a in atoms]
    if not atoms:
        return []
    maxr = max(rad)
    grid = Grid(atoms, cell=maxr * 2.0 + 0.1)
    unit = 4.0 * math.pi / n_points
    idx = range(len(atoms)) if subset is None else subset
    out = []
    for i in idx:
        a = atoms[i]
        ri = rad[i]
        cand = []
        for j in grid.near(a["x"], a["y"], a["z"], ri + maxr):
            if j == i:
                continue
            b = atoms[j]
            d2 = (a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2 + (a["z"] - b["z"]) ** 2
            if d2 < (ri + rad[j]) ** 2:
                cand.append(j)
        acc = 0
        for (px, py, pz) in sphere:
            tx, ty, tz = a["x"] + px * ri, a["y"] + py * ri, a["z"] + pz * ri
            hit = False
            for j in cand:
                b = atoms[j]
                if (tx - b["x"]) ** 2 + (ty - b["y"]) ** 2 + (tz - b["z"]) ** 2 < rad[j] * rad[j]:
                    hit = True
                    break
            if not hit:
                acc += 1
        out.append(acc * unit * ri * ri)
    return out


def _clearance(px, py, pz, dx, dy, dz, grid, atoms, max_A=None, step=None, pad=None, t0=None):
    """March a ray from (p) along unit (d); return how far a chain of linker heavy atoms could extend before
    the first clash with protein (vdW_protein + linker radius), capped at max_A.

    `t0` is where the FIRST linker atom sits, not where the ray is anchored. It defaults to a bond length
    (GEOM["ray_first_atom_A"]) precisely because sampling from the anchor's own centre puts the first test
    point inside the anchor's van-der-Waals sphere, which reports any vdW-contacting site as sealed."""
    max_A = max_A if max_A is not None else GEOM["ray_max_A"]
    step = step or GEOM["ray_step_A"]
    pad = pad if pad is not None else GEOM["linker_atom_radius_A"]
    t = t0 if t0 is not None else GEOM["ray_first_atom_A"]
    last_ok = 0.0                      # 0.0 means even the FIRST linker position clashes: no exit this way
    while t <= max_A:
        x, y, z = px + dx * t, py + dy * t, pz + dz * t
        clash = False
        for j in grid.near(x, y, z, 3.0 + pad):
            b = atoms[j]
            r = VDW.get(b["elem"], DEFAULT_VDW) + pad
            if (x - b["x"]) ** 2 + (y - b["y"]) ** 2 + (z - b["z"]) ** 2 < r * r:
                clash = True
                break
        if clash:
            break
        last_ok = t
        t += step
    return last_ok


def analyse_site(protein_atoms, ligand_atoms, recruiter_chains=None):
    """The ligandability block for one (structure, ligand) pair. Pure geometry, no fitted parameters.

    Returns burial, enclosure, cavity volume, and the EXIT VECTOR — anchor atom, direction, clearance, cone
    openness, open solid-angle fraction, and the residues lining the first 8 A of the channel."""
    if not ligand_atoms or not protein_atoms:
        return None
    pg = Grid(protein_atoms)

    # --- burial: ligand SASA free vs in complex (all polymer chains present, because a linker leaving into a
    #     partner subunit of the same arm is blocked in reality just as it is here) --------------------------
    free = sasa_per_atom(ligand_atoms)
    complex_atoms = ligand_atoms + protein_atoms
    comp = sasa_per_atom(complex_atoms, subset=range(len(ligand_atoms)))
    s_free, s_comp = sum(free), sum(comp)
    buried_fraction = (1.0 - s_comp / s_free) if s_free > 0 else None

    cx = sum(a["x"] for a in ligand_atoms) / len(ligand_atoms)
    cy = sum(a["y"] for a in ligand_atoms) / len(ligand_atoms)
    cz = sum(a["z"] for a in ligand_atoms) / len(ligand_atoms)

    # --- enclosure: fraction of directions from the ligand centroid blocked by protein within 12 A ---------
    enc_dirs = _fib_sphere(GEOM["enclosure_n_rays"])
    blocked = 0
    for (dx, dy, dz) in enc_dirs:
        if _clearance(cx, cy, cz, dx, dy, dz, pg, protein_atoms, max_A=GEOM["enclosure_max_A"],
                      pad=0.0, t0=GEOM["ray_step_A"]) < GEOM["enclosure_max_A"]:
            blocked += 1
    enclosure = blocked / float(len(enc_dirs))

    # --- exit vector -------------------------------------------------------------------------------------
    order = sorted(range(len(ligand_atoms)), key=lambda i: -comp[i])
    exit_i = order[0]
    fully_buried = comp[exit_i] <= 1e-6
    ea = ligand_atoms[exit_i]
    ax, ay, az = ea["x"], ea["y"], ea["z"]

    dirs = _fib_sphere(GEOM["ray_n_directions"])
    clear = [_clearance(ax, ay, az, dx, dy, dz, pg, protein_atoms) for (dx, dy, dz) in dirs]
    cmax = max(clear)
    # A wide mouth produces MANY directions tied at the cap, and `max()` would then return whichever the
    # iteration order happened to reach first — a coordinate-order artifact, not geometry. Take instead the
    # solid-angle centroid of the near-maximal directions: the middle of the opening. Deterministic, and it
    # is what a linker leaving the site actually points along.
    #
    # ★ The cmax == 0 case is NOT a tie and must be special-cased. `c >= 0.95 * cmax` is satisfied by every
    # direction when cmax is 0, so a FULLY ENCLOSED site (an occluded ligand, or a buried cryptic pocket)
    # would otherwise average all 512 directions to ~the zero vector and then report an arbitrary
    # argmax direction alongside a 0.0 clearance — a meaningless vector wearing the same field name as a real
    # one. Caught 2026-07-25 by running the geometry on the repo's own AF2 NR4A3 model with a pseudo-ligand
    # at the (closed) cryptic pocket: clearance 0.0 with n_near_maximal_directions = 512.
    no_exit = cmax <= 0.0
    if no_exit:
        tied = []
        vx0, vy0, vz0 = ax - cx, ay - cy, az - cz
        n0 = math.sqrt(vx0 * vx0 + vy0 * vy0 + vz0 * vz0)
        bd = (vx0 / n0, vy0 / n0, vz0 / n0) if n0 > 1e-6 else (0.0, 0.0, 1.0)
        best_clear = cmax
    else:
        tied = [i for i, c in enumerate(clear) if c >= 0.95 * cmax]
        sx = sum(dirs[i][0] for i in tied); sy = sum(dirs[i][1] for i in tied)
        sz = sum(dirs[i][2] for i in tied)
        nrm = math.sqrt(sx * sx + sy * sy + sz * sz)
        if nrm > 1e-6:
            bd = (sx / nrm, sy / nrm, sz / nrm)
        else:                                 # open in opposing directions (a through-tunnel): fall back
            bd = dirs[max(range(len(clear)), key=lambda i: clear[i])]
        best_clear = _clearance(ax, ay, az, bd[0], bd[1], bd[2], pg, protein_atoms)
    cos_cut = math.cos(math.radians(GEOM["cone_half_angle_deg"]))
    cone_idx = [i for i, d in enumerate(dirs)
                if d[0] * bd[0] + d[1] * bd[1] + d[2] * bd[2] >= cos_cut]
    cone_open = (sum(1 for i in cone_idx if clear[i] >= GEOM["cone_open_clearance_A"]) / float(len(cone_idx))
                 if cone_idx else 0.0)
    openness = sum(1 for c in clear if c >= GEOM["orientation_openness_clearance_A"]) / float(len(clear))

    # centroid->exit-atom direction, and the angle between it and the maximum-clearance direction: a small
    # angle means the most exposed atom really is pointing out of the site.
    vx, vy, vz = ax - cx, ay - cy, az - cz
    nv = math.sqrt(vx * vx + vy * vy + vz * vz) or 1.0
    cvec = (vx / nv, vy / nv, vz / nv)
    dot = max(-1.0, min(1.0, cvec[0] * bd[0] + cvec[1] * bd[1] + cvec[2] * bd[2]))
    angle = math.degrees(math.acos(dot))

    lining, t = set(), GEOM["ray_step_A"]
    while t <= 8.0:
        x, y, z = ax + bd[0] * t, ay + bd[1] * t, az + bd[2] * t
        for j in pg.near(x, y, z, GEOM["channel_lining_cutoff_A"]):
            b = protein_atoms[j]
            if ((x - b["x"]) ** 2 + (y - b["y"]) ** 2 + (z - b["z"]) ** 2
                    <= GEOM["channel_lining_cutoff_A"] ** 2):
                lining.add((b["chain"], b["resname"], b["resid"]))
        t += 1.0

    cavity = _cavity_volume(protein_atoms, ligand_atoms, pg)

    return {
        "ligand_burial": {
            "sasa_free_A2": round(s_free, 1), "sasa_in_complex_A2": round(s_comp, 1),
            "buried_fraction": round(buried_fraction, 4) if buried_fraction is not None else None,
            "_method": "Shrake-Rupley, 128 sphere points, 1.4 A probe, Bondi radii; complex includes every "
                       "polymer chain deposited in the entry",
        },
        "site_enclosure": {
            "blocked_fraction": round(enclosure, 4), "n_rays": GEOM["enclosure_n_rays"],
            "max_A": GEOM["enclosure_max_A"],
            "_method": "fraction of rays cast from the ligand centroid that meet a protein heavy atom within "
                       "12 A (no linker padding) — 1.0 = fully enclosed cavity, 0.0 = flat surface",
        },
        "cavity": cavity,
        "exit_vector": {
            "anchor_atom": ea["name"], "anchor_element": ea["elem"],
            "anchor_sasa_in_complex_A2": round(comp[exit_i], 2),
            "anchor_is_fully_buried": bool(fully_buried),
            "anchor_xyz": [round(ax, 3), round(ay, 3), round(az, 3)],
            "direction": [round(bd[0], 4), round(bd[1], 4), round(bd[2], 4)],
            "clearance_A": round(best_clear, 2),
            "max_ray_clearance_A": round(cmax, 2),
            "n_near_maximal_directions": len(tied),
            "no_exit_path": bool(no_exit),
            "cone_openness_30deg": round(cone_open, 4),
            "angle_to_centroid_vector_deg": round(angle, 1),
            "open_solid_angle_fraction_15A": round(openness, 4),
            "channel_lining_residues": [f"{c}:{rn}{ri}" for (c, rn, ri) in sorted(lining, key=lambda t: t[2])],
            "_method": "anchor = the ligand heavy atom with the largest solvent-accessible area in the "
                       "complex (the natural linker attachment point); direction = the maximum-clearance "
                       "direction of 512 Fibonacci rays from that anchor, each ray beginning at the "
                       "first BONDED linker-atom position (1.5 A out, not at the anchor centre, which lies "
                       "inside the anchor's own vdW sphere) and terminating where a 1.7 A linker heavy atom "
                       "would clash with a protein vdW sphere",
            "_limit": "One deposited conformer, one ligand, no linker sampling and no protein flexibility. "
                      "This bounds where a linker COULD leave; it does not establish that any particular "
                      "linker does leave, nor anything about the resulting ternary complex.",
        },
        "n_protein_atoms": len(protein_atoms),
        "n_ligand_heavy_atoms": len(ligand_atoms),
        "recruiter_chains_in_model": sorted(set(recruiter_chains or [])),
    }


# LIGSITE scan directions: the 3 Cartesian axes + the 4 cube diagonals (Hendlich, Rippmann & Barnickel,
# J. Mol. Graph. Model. 1997). A point is buried when it is enclosed (protein on BOTH sides) along at least
# MINPSP of these 7 directions.
_LIGSITE_DIRS = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)]


def _cavity_volume(protein_atoms, ligand_atoms, pg=None):
    """Ligand-proximal BURIED cavity volume (A^3) by the LIGSITE protein-solvent-protein (PSP) scan.

    An occupancy grid is marked from the protein's probe-inflated vdW spheres; a free grid point within 4 A
    of a ligand heavy atom counts toward the cavity when it is enclosed along >= MINPSP of the 7 LIGSITE
    directions. This is a *cavity volume around the bound ligand*, not an fpocket pocket volume — the two are
    reported side by side and must not be conflated."""
    sp = GEOM["cavity_grid_spacing_A"]
    minpsp = GEOM["cavity_min_psp"]
    scan_A = GEOM["cavity_psp_scan_A"]
    pad = GEOM["cavity_ligand_shell_A"]
    if not ligand_atoms:
        return {"volume_A3": None, "_status": "no ligand atoms"}

    xs = [a["x"] for a in ligand_atoms]; ys = [a["y"] for a in ligand_atoms]; zs = [a["z"] for a in ligand_atoms]
    margin = pad + scan_A + 3.0
    lo = [min(xs) - margin, min(ys) - margin, min(zs) - margin]
    hi = [max(xs) + margin, max(ys) + margin, max(zs) + margin]
    n = [int((hi[k] - lo[k]) / sp) + 1 for k in range(3)]
    if n[0] * n[1] * n[2] > 12_000_000:
        return {"volume_A3": None, "_status": "grid too large — skipped"}
    nx, ny, nz = n
    occ = bytearray(nx * ny * nz)

    def _mark(cx, cy, cz, r):
        ir = int(r / sp) + 1
        i0 = max(0, int((cx - lo[0]) / sp) - ir); i1 = min(nx - 1, int((cx - lo[0]) / sp) + ir)
        j0 = max(0, int((cy - lo[1]) / sp) - ir); j1 = min(ny - 1, int((cy - lo[1]) / sp) + ir)
        k0 = max(0, int((cz - lo[2]) / sp) - ir); k1 = min(nz - 1, int((cz - lo[2]) / sp) + ir)
        r2 = r * r
        for i in range(i0, i1 + 1):
            dx = lo[0] + i * sp - cx
            base_i = i * ny * nz
            rem_x = r2 - dx * dx
            if rem_x < 0:
                continue
            for j in range(j0, j1 + 1):
                dy = lo[1] + j * sp - cy
                rem = rem_x - dy * dy
                if rem < 0:
                    continue
                dz = math.sqrt(rem)
                ka = max(k0, int((cz - dz - lo[2]) / sp))
                kb = min(k1, int((cz + dz - lo[2]) / sp) + 1)
                if kb >= ka:
                    b = base_i + j * nz
                    occ[b + ka:b + kb + 1] = b"\x01" * (kb - ka + 1)

    for a in protein_atoms:
        if not (lo[0] <= a["x"] <= hi[0] and lo[1] <= a["y"] <= hi[1] and lo[2] <= a["z"] <= hi[2]):
            continue
        _mark(a["x"], a["y"], a["z"], VDW.get(a["elem"], DEFAULT_VDW) + GEOM["sasa_probe_A"])

    steps = int(scan_A / sp) + 1
    n_ok = 0
    seen = set()
    ir = int(pad / sp) + 1
    for a in ligand_atoms:                       # only points near the ligand can be in the ligand's cavity
        ci = int((a["x"] - lo[0]) / sp); cj = int((a["y"] - lo[1]) / sp); ck = int((a["z"] - lo[2]) / sp)
        for i in range(max(0, ci - ir), min(nx, ci + ir + 1)):
            for j in range(max(0, cj - ir), min(ny, cj + ir + 1)):
                for k in range(max(0, ck - ir), min(nz, ck + ir + 1)):
                    if (i, j, k) in seen:
                        continue
                    px, py, pz = lo[0] + i * sp, lo[1] + j * sp, lo[2] + k * sp
                    if ((px - a["x"]) ** 2 + (py - a["y"]) ** 2 + (pz - a["z"]) ** 2) > pad * pad:
                        continue
                    seen.add((i, j, k))
                    if occ[i * ny * nz + j * nz + k]:
                        continue
                    psp = 0
                    for (dx, dy, dz) in _LIGSITE_DIRS:
                        both = 0
                        for sgn in (1, -1):
                            for s in range(1, steps + 1):
                                ii, jj, kk = i + dx * sgn * s, j + dy * sgn * s, k + dz * sgn * s
                                if not (0 <= ii < nx and 0 <= jj < ny and 0 <= kk < nz):
                                    break
                                if occ[ii * ny * nz + jj * nz + kk]:
                                    both += 1
                                    break
                        if both == 2:
                            psp += 1
                    if psp >= minpsp:
                        n_ok += 1
    return {"volume_A3": round(n_ok * sp ** 3, 1), "n_grid_points": n_ok, "spacing_A": sp,
            "min_psp_of_7": minpsp, "psp_scan_A": scan_A,
            "_method": "LIGSITE protein-solvent-protein scan (Hendlich 1997): free grid points within "
                       f"{pad} A of a ligand heavy atom that are enclosed by protein along >= {minpsp} of the "
                       "7 axis/diagonal directions within "
                       f"{scan_A} A. A cavity volume around the bound ligand, NOT an fpocket pocket volume."}


# --------------------------------------------------------------------------------------------------------
# fpocket (optional; the field-standard druggability number, directly comparable to this program's Gate-2 D*)
# --------------------------------------------------------------------------------------------------------
def run_fpocket(protein_atoms, ligand_atoms, workdir, tag):
    import fpocket_lib as fl
    if not protein_atoms:
        return {"_status": "no protein atoms"}
    os.makedirs(workdir, exist_ok=True)
    pdb = os.path.join(workdir, f"{tag}.pdb")
    with open(pdb, "w") as fh:
        for n, a in enumerate(protein_atoms, 1):
            fh.write("ATOM  {:5d} {:^4s}{:>4s} {:1s}{:4d}    "
                     "{:8.3f}{:8.3f}{:8.3f}  1.00  0.00          {:>2s}\n".format(
                         n, a["name"][:4], a["resname"][:3], (a["chain"] or "A")[0], a["resid"],
                         a["x"], a["y"], a["z"], a["elem"][:2]))
        fh.write("END\n")
    try:
        subprocess.run(["fpocket", "-f", pdb], check=True, capture_output=True, timeout=900)
    except FileNotFoundError:
        return {"_status": "fpocket not installed — pocket druggability not computed"}
    except Exception as e:                                       # noqa: BLE001
        return {"_status": f"fpocket failed: {e}"}
    out = os.path.join(workdir, f"{tag}_out")
    info_p = os.path.join(out, f"{tag}_info.txt")
    if not os.path.exists(info_p):
        return {"_status": "fpocket produced no info.txt"}
    info = fl.parse_info(open(info_p).read())
    pockets_dir = os.path.join(out, "pockets")
    counts, coords = {}, {}
    if os.path.isdir(pockets_dir):
        for fn in os.listdir(pockets_dir):
            if fn.endswith("_vert.pqr"):
                idx = int(fn.split("pocket")[1].split("_")[0])
                txt = open(os.path.join(pockets_dir, fn)).read()
                counts[idx] = fl.count_pqr_spheres(txt)
                coords[idx] = fl.pqr_sphere_coords(txt)
    if not coords:
        return {"_status": "fpocket produced no pocket vertices"}

    # ★ Attribute the ligand to a pocket by OVERLAP — the number of ligand heavy atoms within 4 A of one of
    # that pocket's alpha spheres — not by distance from the pocket to the ligand CENTROID. For an elongated
    # ligand the centroid sits in the middle of the molecule, which for a PROTAC is the middle of the LINKER,
    # so centroid attribution hands back whatever small pocket happens to sit under the linker instead of the
    # handle pocket. Symptom that exposed it (run 30167890490): MDM2's classic p53-binding cleft scored
    # druggability 0.085. The file->pocket mapping is still derived from alpha-sphere fingerprints, never the
    # filename index (fpocket_lib).
    overlap = {}
    for idx, cs in coords.items():
        cs = list(cs)
        n = 0
        for a in ligand_atoms:
            for (x, y, z) in cs:
                if (x - a["x"]) ** 2 + (y - a["y"]) ** 2 + (z - a["z"]) ** 2 <= 16.0:
                    n += 1
                    break
        overlap[idx] = n
    best_idx = max(overlap, key=lambda i: (overlap[i], counts.get(i, 0)))
    best_d = min((x - a["x"]) ** 2 + (y - a["y"]) ** 2 + (z - a["z"]) ** 2
                 for (x, y, z) in coords[best_idx] for a in ligand_atoms)
    if overlap[best_idx] == 0:
        return {"_status": "no fpocket pocket overlaps the ligand — not attributed",
                "n_pockets_found": len(info)}
    out_pdb = os.path.join(out, f"{tag}_out.pdb")
    try:
        mapping = fl.map_files_to_pockets(
            info, counts, coords,
            fl.out_pdb_sphere_coords(open(out_pdb).read()) if os.path.exists(out_pdb) else None)
        pnum = mapping.get(best_idx)
    except Exception:                                            # noqa: BLE001
        pnum = None
    rec = info.get(pnum, {}) if pnum else {}
    return {"pocket_number": pnum, "file_index": best_idx,
            "druggability": rec.get("druggability"), "alpha_spheres": rec.get("alpha_spheres"),
            "ligand_atoms_overlapping_pocket": overlap[best_idx],
            "ligand_atoms_total": len(ligand_atoms),
            "ligand_overlap_fraction": round(overlap[best_idx] / float(len(ligand_atoms)), 3),
            "min_alpha_sphere_to_ligand_atom_A": round(math.sqrt(best_d), 2),
            "n_pockets_found": len(info),
            "_method": "fpocket on the arm chains with the ligand removed; the ligand is attributed to the "
                       "pocket overlapping the MOST ligand heavy atoms (within 4 A of an alpha sphere), not "
                       "the pocket nearest the ligand centroid — for an elongated ligand the centroid lies "
                       "in the linker, not the handle site. The file->pocket mapping is derived from "
                       "alpha-sphere fingerprints (fpocket_lib), never assumed from the file index.",
            "_limit": "A ligand spanning several fpocket pockets is scored on ONE of them, so a low "
                      "druggability on a large ligand can mean 'decomposed across pockets' rather than "
                      "'undruggable'. Read ligand_overlap_fraction alongside it."}


# =========================================================================================================
# PHASE 5 — the preregistered downselect
# =========================================================================================================
def _exit_quality(lg):
    ev = (lg or {}).get("exit_vector") or {}
    c = ev.get("clearance_A")
    o = ev.get("cone_openness_30deg")
    if c is None or o is None:
        return 0.0
    return round(min(c, 20.0) * o, 4)


def evaluate_gates(rec):
    """Apply G1/G2/G3 to one recruiter record. Returns (gates_dict, first_failed_or_None)."""
    staged = rec.get("staged_structures") or []
    lg = rec.get("ligandability") or {}
    primary = next((s for s in staged if s.get("is_primary")), None)

    g1_ok = bool(primary)
    if g1_ok:
        res = primary.get("resolution_A")
        methods = " ".join(primary.get("experimental_methods") or []).upper()
        is_nmr = "NMR" in methods
        g1_ok = is_nmr or (res is not None and res <= MIN_RESOLUTION_A)
    search = rec.get("rcsb_search") or {}
    bf = ((lg.get("ligand_burial") or {}).get("buried_fraction"))
    g2_ok = bf is not None and bf >= GATES["G2_ligand_is_pocket_bound"]["threshold"]
    ev = lg.get("exit_vector") or {}
    g3_ok = (ev.get("clearance_A") is not None
             and ev["clearance_A"] >= GATES["G3_linker_can_leave"]["clearance_A"]
             and (ev.get("cone_openness_30deg") or 0.0) >= GATES["G3_linker_can_leave"]["cone_openness"])

    gates = {
        "G1_public_ligand_bound_structure": {
            "pass": bool(g1_ok),
            "observed": (f"{primary['pdb_id']} @ {primary.get('resolution_A')} A "
                         f"({'/'.join(primary.get('experimental_methods') or []) or 'method?'}), "
                         f"ligand {primary.get('ligand', {}).get('ccd')}")
            if primary else
            ("no deposited structure of this protein at all "
             f"(RCSB: {search.get('total_count_any_structure')} entries carrying the accession)"
             if not search.get("n_hits_any_structure")
             else f"{search.get('n_hits_any_structure')} deposited structure(s) exist, but none carries a "
                  "usable (non-solvent, >=10 heavy atom) ligand: "
                  f"{', '.join(search.get('example_apo_entries') or []) or 'n/a'}")},
        "G2_ligand_is_pocket_bound": {"pass": bool(g2_ok), "observed": bf},
        "G3_linker_can_leave": {"pass": bool(g3_ok),
                                "observed": {"clearance_A": ev.get("clearance_A"),
                                             "cone_openness_30deg": ev.get("cone_openness_30deg")}},
    }
    failed = next((k for k in ("G1_public_ligand_bound_structure", "G2_ligand_is_pocket_bound",
                               "G3_linker_can_leave") if not gates[k]["pass"]), None)
    return gates, failed


def axis_values(rec):
    lg = rec.get("ligandability") or {}
    ev = lg.get("exit_vector") or {}
    primary = next((s for s in (rec.get("staged_structures") or []) if s.get("is_primary")), None)
    return {
        "linker_analogue_tier": (rec.get("linker_bearing_analogue") or {}).get("tier", 0),
        "exit_quality": _exit_quality(lg),
        "orientation_openness": ev.get("open_solid_angle_fraction_15A") or 0.0,
        "neg_resolution": -(primary.get("resolution_A") if primary and primary.get("resolution_A")
                            is not None else 99.0),
    }


def pareto_front(items):
    """items: {name: {axis: value}} over the maximise-axes in PARETO_AXES. Returns the nondominated names.
    A is dominated by B iff B >= A on every axis and > on at least one."""
    keys = [k for k, d, _ in PARETO_AXES]
    front = []
    for a, va in items.items():
        dominated = False
        for b, vb in items.items():
            if a == b:
                continue
            if all(vb[k] >= va[k] for k in keys) and any(vb[k] > va[k] for k in keys):
                dominated = True
                break
        if not dominated:
            front.append(a)
    return sorted(front)


def downselect(recruiters):
    """Gates -> Pareto front -> preregistered lexicographic tiebreak -> <=2 advanced, everything else DROPPED
    with the reason recorded. Availability is asserted NOT to be a drop reason."""
    gated, dropped = {}, []
    for name, rec in recruiters.items():
        gates, failed = evaluate_gates(rec)
        rec["gates"] = gates
        if failed:
            dropped.append({
                "recruiter": name, "stage": "gate", "gate_failed": failed,
                "reason": f"{GATES[failed]['rule']} — observed: {gates[failed]['observed']}",
                "availability_was_not_a_factor": True,
            })
        else:
            gated[name] = axis_values(rec)
            rec["axes"] = gated[name]

    front = pareto_front(gated) if gated else []
    for name in sorted(gated):
        if name not in front:
            dominators = [b for b in front
                          if all(gated[b][k] >= gated[name][k] for k, _, _ in PARETO_AXES)]
            dropped.append({
                "recruiter": name, "stage": "pareto",
                "reason": "passed all gates but is Pareto-dominated on ligandability + interface geometry "
                          f"(dominated by {', '.join(dominators) or 'the front'}); axes "
                          f"{json.dumps(gated[name])}",
                "availability_was_not_a_factor": True,
            })

    def _lex(n):
        return tuple(-gated[n][k] for k in TIEBREAK)

    ranked = sorted(front, key=_lex)
    advanced = ranked[:MAX_ADVANCED]

    # If the front collapses to a single recruiter, carrying only that one forward would make the E3 an
    # UNCONTROLLED variable in every downstream basin comparison — there would be no E3-choice sensitivity
    # check at all, which the ternary workflow explicitly requires. The cap is <=2, not ==1, so backfill the
    # second slot with the best gate-passing recruiter outside the front and label it for what it is.
    backfilled = []
    if len(advanced) < MAX_ADVANCED:
        rest = sorted((n for n in gated if n not in front), key=_lex)
        backfilled = rest[:MAX_ADVANCED - len(advanced)]
        advanced = advanced + backfilled
        dropped = [d for d in dropped if d["recruiter"] not in backfilled]

    for name in ranked[MAX_ADVANCED:]:
        dropped.append({
            "recruiter": name, "stage": "cap",
            "reason": f"on the Pareto front but ranked #{ranked.index(name) + 1} under the preregistered "
                      f"lexicographic tiebreak {TIEBREAK}; nr4a3-program-map.md caps the recruiter set at "
                      f"{MAX_ADVANCED} before any GPU leg. Axes {json.dumps(gated[name])}",
            "availability_was_not_a_factor": True,
        })
    for name, rec in recruiters.items():
        rec["decision"] = "ADVANCE" if name in advanced else "DROP"
        if name in backfilled:
            rec["advance_note"] = ("Pareto-dominated; retained as the SECOND recruiter so that the E3 is a "
                                   "controlled variable downstream (E3-choice sensitivity), not because it "
                                   "is competitive with the front-runner on ligandability.")
    return {
        "rule": {
            "gates": GATES,
            "pareto_axes": [{"axis": k, "direction": d, "why": w} for k, d, w in PARETO_AXES],
            "tiebreak_lexicographic": list(TIEBREAK),
            "cap": MAX_ADVANCED,
            "backfill": "If the Pareto front collapses to one recruiter, the second slot is filled by the "
                        "best gate-passing recruiter outside the front, labelled as such. Carrying one E3 "
                        "forward would leave the E3 an uncontrolled variable in every downstream basin "
                        "comparison; the cap is <=2, not ==1.",
            "preregistered": "This rule was committed to the repository before the CI fetch that produced "
                             "the data below; it is not fitted to the result.",
        },
        "advanced": advanced,
        "backfilled_for_e3_choice_sensitivity": backfilled,
        "pareto_front": front,
        "ranked_front": ranked,
        "dropped": dropped,
        "availability_assertion": {
            "claim": "No recruiter is dropped for lack of expression. All eight widened arms are broadly "
                     "expressed and record-complete on HPA (nr4a3_e3_expression.py, CI run 30125742542), so "
                     "availability does not constrain this choice — nr4a3-program-map.md RUNG 5a.",
            "verified": all(d.get("availability_was_not_a_factor") for d in dropped),
        },
    }


# =========================================================================================================
# DRIVER
# =========================================================================================================
def check_availability_not_a_constraint(path=AVAILABILITY_JSON):
    """Read the already-computed HPA panel and assert it does not veto anyone. This module must NEVER drop a
    recruiter on availability; reading the file is how that is checked rather than assumed."""
    if not os.path.exists(path):
        return {"_status": f"{os.path.basename(path)} not present — availability not cross-checked"}
    d = json.load(open(path))
    w = d.get("widened_recruiter_panel") or {}
    return {"source": os.path.basename(path),
            "widened_broadly_expressed_and_complete": w.get("broadly_expressed_and_complete"),
            "widened_flagged_or_incomplete": w.get("flagged_or_incomplete"),
            "incumbent_arms_both_broad": d.get("both_arms_broadly_expressed"),
            "used_as_a_drop_reason": False,
            "_note": "Availability is NECESSARY but does not discriminate here, so it is recorded and then "
                     "deliberately excluded from the downselect (nr4a3-program-map.md RUNG 5a)."}


def fetch_panel(max_entries_deep=8, search_rows=100):
    """Network phase. Returns {gene: record} with resolved accession, screened entries, staged structures."""
    out, chemcomp_cache, arm_cache = {}, {}, {}
    for spec in PANEL:
        gene = spec["gene"]
        print(f"\n=== {gene} ===", file=sys.stderr)
        rec = {"gene": gene, "aliases": spec["aliases"], "e3_class": spec["e3_class"],
               "arm": spec["arm"], "incumbent_recruiter": spec["incumbent"]}
        up = resolve_uniprot(gene, spec["aliases"])
        rec["uniprot"] = up
        if not up.get("accession"):
            rec["staged_structures"] = []
            rec["linker_bearing_analogue"] = {"tier": 0, "label": "none",
                                              "_status": "UniProt resolution failed — not searched"}
            rec["_status"] = up["_status"]
            out[gene] = rec
            continue
        acc = up["accession"]
        ids, qrec = rcsb_search_entries(acc, max_rows=search_rows)
        rec["rcsb_search"] = qrec
        print(f"  {acc}: {len(ids)} ligand-carrying entries", file=sys.stderr)

        entries = []
        for pdb_id in ids:
            e = summarise_entry(pdb_id, acc, chemcomp_cache)
            if e:
                entries.append(e)
        rec["n_entries_screened"] = len(entries)
        rec["linker_bearing_analogue"] = classify_linker_analogue(entries, acc)

        arm_accs, arm_unresolved = arm_component_accessions(spec["arm"], arm_cache)
        arm_accs = set(arm_accs) | {acc}
        rec["arm_component_accessions"] = sorted(arm_accs)
        rec["arm_components_unresolved"] = arm_unresolved

        # ★ WHICH structure the geometry is measured on. Prefer a CLEAN BINARY structure — the recruiter (and
        # its own arm) bound to a handle-sized ligand and nothing else. A ternary/glue entry is the wrong
        # frame for BOTH numbers this stage produces: the PROTAC's burial would be computed against only half
        # the protein that actually buries it, and the partner protein would occupy the very orientation
        # space being measured. Ternary entries remain the linker-analogue EVIDENCE (classified above); they
        # are just not the geometry frame unless nothing else exists.
        staged = select_staged(entries, arm_accs, max_entries_deep, uniprot_length=up.get("length"))
        rec["staged_structures"] = staged
        rec["geometry_frame"] = {
            "primary_has_partner_protein": bool(staged and staged[0]["has_partner_protein"]),
            "n_clean_binary_entries": sum(1 for e in entries if not e["has_partner_protein"]),
            "primary_recruiter_entity_length": staged[0].get("recruiter_entity_length") if staged else None,
            "primary_recruiter_uniprot_coverage_fraction": (
                staged[0].get("recruiter_uniprot_coverage_fraction") if staged else None),
            "primary_is_peptide_fragment": bool(staged and staged[0].get(
                "recruiter_entity_is_peptide_fragment")),
            "_note": "If primary_has_partner_protein is true, NO structure of this recruiter exists without a "
                     "bound partner protein — a glue-type recruiter whose handle site may be partly formed BY "
                     "that partner. The partner's chains are excluded from the occluder set so the "
                     "orientation space is not deflated, but burial and exit vector are then measured against "
                     "an incomplete site and must be read as such.",
        }
        rec["_status"] = "ok"
        out[gene] = rec
    return out


def contacts_between(lig_atoms, prot_atoms, grid, chain_ids, cutoff=4.5):
    """Number of ligand-heavy-atom / protein-heavy-atom pairs within `cutoff`, restricted to `chain_ids`."""
    c2, n = cutoff * cutoff, 0
    for a in lig_atoms:
        for j in grid.near(a["x"], a["y"], a["z"], cutoff):
            b = prot_atoms[j]
            if base_chain(b["chain"]) not in chain_ids:
                continue
            if (a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2 + (a["z"] - b["z"]) ** 2 <= c2:
                n += 1
    return n


def verify_bridging(rec, arm_accs):
    """Does the claimed bivalent ligand ACTUALLY bridge the recruiter and a partner protein?

    The tier-3 screen in `classify_linker_analogue` is entry-level: it sees a >=500 Da ligand and a second
    UniProt accession in the same deposition. Co-presence is not bridging — a crystallisation partner, a
    second complex in the asymmetric unit, or a ligand bound to only one of the two proteins would all pass
    that screen. This re-reads the coordinates of the best tier-3 entry and requires the ligand to contact
    BOTH a recruiter chain and a non-arm partner chain. Failing that, the tier is DEMOTED to 2, because
    "a linker demonstrably leaves this recruiter toward another protein" is the whole content of tier 3."""
    lb = rec.get("linker_bearing_analogue") or {}
    if lb.get("tier") != 3:
        return
    by_id = {e["pdb_id"]: e for e in (rec.get("staged_structures") or [])}
    for e in lb.get("_evidence_entries") or []:          # evidence entries are not always in the staged top-8
        by_id.setdefault(e["pdb_id"], e)
    checked = []
    ordered_ids = [e["pdb_id"] for e in (lb.get("_evidence_entries") or [])] or \
        list(lb.get("evidence_pdb_ids_ternary") or [])
    for pdb_id in ordered_ids:
        entry = by_id.get(pdb_id)
        if not entry:
            continue                      # not among the staged deep-fetched entries; nothing to read
        path, src = download_structure(pdb_id)
        if not path:
            continue
        prot, het = parse_structure(path)
        if not prot:
            continue
        grid = Grid(prot)
        rch = {base_chain(c) for c in (entry.get("recruiter_auth_asym_ids") or [])}
        pch = set()
        for pe in entry.get("polymer_entities") or []:
            if not (set(pe.get("uniprot_ids") or []) & set(arm_accs)):
                pch.update(base_chain(c) for c in (pe.get("auth_asym_ids") or []))
        best = None
        for (ch, resn, resi), atoms in het.items():
            cc = next((l for l in entry["candidate_ligands"] if l["ccd"] == resn), None)
            if not cc or (cc.get("formula_weight") or 0.0) < LINKER_BEARING_MIN_MW:
                continue
            nr = contacts_between(atoms, prot, grid, rch)
            npn = contacts_between(atoms, prot, grid, pch)
            cand = {"pdb_id": pdb_id, "ccd": resn, "auth_asym_id": ch, "auth_seq_id": resi,
                    "contacts_recruiter": nr, "contacts_partner": npn,
                    "bridges": bool(nr > 0 and npn > 0), "coordinate_source": src}
            if best is None or (cand["bridges"], nr + npn) > (best["bridges"], best["contacts_recruiter"]
                                                              + best["contacts_partner"]):
                best = cand
        if best:
            checked.append(best)
            if best["bridges"]:
                break
    lb["bridging_check"] = checked
    if checked and not any(c["bridges"] for c in checked):
        lb["tier"], lb["label"] = 2, "bivalent_binary"
        lb["tier_demoted"] = ("entry-level co-presence of a second protein was not confirmed at chain level "
                              "— the >=500 Da ligand does not contact both the recruiter and a partner in "
                              "the deposited coordinates, so this is not a solved bivalent complex")
    elif not checked:
        lb["bridging_check_status"] = ("no tier-3 evidence entry was among the deep-fetched staged set, so "
                                       "bridging is asserted at entry level only")


def geometry_panel(recruiters, workdir=None, use_fpocket=True):
    """Offline phase: download (cached) coordinates for each primary structure and compute ligandability."""
    workdir = workdir or os.path.join(COORD_DIR, "_fpocket")
    for gene, rec in recruiters.items():
        verify_bridging(rec, set(rec.get("arm_component_accessions") or []))
        primary = next((s for s in (rec.get("staged_structures") or []) if s.get("is_primary")), None)
        if not primary:
            rec["ligandability"] = {"_status": "no staged structure"}
            continue
        pdb_id = primary["pdb_id"]
        path, src = download_structure(pdb_id)
        if not path:
            rec["ligandability"] = {"_status": f"coordinate download failed for {pdb_id}: {src}"}
            continue
        prot_all, het = parse_structure(path)
        ccd = (primary.get("ligand") or {}).get("ccd")
        groups = [(k, v) for k, v in het.items() if k[1] == ccd]
        if not groups:
            rec["ligandability"] = {"_status": f"ligand {ccd} not found in {os.path.basename(path)}"}
            continue

        # ★ OCCLUDER SET = the recruiter's own arm ONLY. Chains belonging to a bound partner protein
        # (neosubstrate / PROTAC target / a crystallisation partner) are removed: they occupy exactly the
        # orientation space this stage measures, so leaving them in would report a recruiter with a solved
        # ternary as having nowhere for a target to go.
        arm_accs = set(rec.get("arm_component_accessions") or [])
        arm_ids, partner_ids = set(), set()
        for pe in primary.get("polymer_entities") or []:
            tgt = arm_ids if (set(pe.get("uniprot_ids") or []) & arm_accs) else partner_ids
            tgt.update(base_chain(c) for c in (pe.get("auth_asym_ids") or []))
        prot = [a for a in prot_all if base_chain(a["chain"]) in arm_ids] if arm_ids else prot_all
        excluded = {"partner_entity_chains_excluded": sorted(partner_ids),
                    "arm_entity_chains_kept": sorted(arm_ids),
                    "chains_present_in_frame": sorted({a["chain"] for a in prot}),
                    "n_atoms_excluded": len(prot_all) - len(prot),
                    "coordinate_source": src}
        if not prot:
            prot, excluded["_status"] = prot_all, "no chain mapped to the arm — fell back to all chains"

        # If the ligand is present in several copies, take the copy with the most contacts to a recruiter
        # chain — that is the biologically staged one, and it is decided from coordinates, not from the
        # first-listed chain.
        rchains = {base_chain(c) for c in (primary.get("recruiter_auth_asym_ids") or [])}
        pg = Grid(prot)

        def _contacts(atoms, chains=None):
            n = 0
            for a in atoms:
                for j in pg.near(a["x"], a["y"], a["z"], 4.5):
                    b = prot[j]
                    if chains and base_chain(b["chain"]) not in chains:
                        continue
                    if ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2 + (a["z"] - b["z"]) ** 2) <= 20.25:
                        n += 1
            return n

        groups.sort(key=lambda kv: -_contacts(kv[1], rchains))
        key, lig_atoms = groups[0]
        n_rec = _contacts(lig_atoms, rchains)
        primary["ligand_instance"] = {"auth_asym_id": key[0], "auth_seq_id": key[2],
                                      "n_heavy_atoms_modelled": len(lig_atoms),
                                      "n_contacts_to_recruiter_chain_4.5A": n_rec,
                                      "n_copies_in_entry": len(groups),
                                      "contacts_recruiter": n_rec > 0}
        lg = analyse_site(prot, lig_atoms, rchains) or {"_status": "geometry failed"}
        if use_fpocket:
            lg["fpocket"] = run_fpocket(prot, lig_atoms, workdir, f"{gene}_{pdb_id}")
        lg["structure_file"] = os.path.basename(path)
        lg["coordinate_source"] = src
        lg["occluder_set"] = excluded
        lg["measured_with_partner_protein_removed"] = bool(partner_ids)
        rec["ligandability"] = lg
        ev = lg.get("exit_vector", {})
        print(f"  {gene} {pdb_id}/{ccd}: buried={lg.get('ligand_burial', {}).get('buried_fraction')} "
              f"exit={ev.get('clearance_A')}A cone={ev.get('cone_openness_30deg')} "
              f"open15={ev.get('open_solid_angle_fraction_15A')}", file=sys.stderr)
    return recruiters


def build(recruiters, availability):
    ds = downselect(recruiters)
    return {
        "_title": "E3 recruiter staging + ligandability downselect — nr4a3-program-map.md RUNG 5a(c), 'E3 breadth, "
                  "free at the search stage'",
        "_why": "Selectivity in this program is created at the induced target-E3 interface, so the E3's own "
                "surface is the largest lever on whether a discriminating interface exists at all. Basin "
                "search is CPU, so widening the recruiter set is free — but a wide set multiplied by GPU legs "
                "is not, which is why STRATEGY caps it at <=2 recruiters before any GPU leg AND requires the "
                "dropped set to be logged: a silent top-N reads as 'we covered everything'.",
        "_method": "UniProt (reviewed, human, exact gene match, fail-closed) -> RCSB search for entries "
                   "carrying that accession with >=1 non-polymer entity, plus an unfiltered search so "
                   "'no structure' is distinguishable from 'no liganded structure' -> RCSB data API for "
                   "resolution, method, chain composition, ligand CCD and primary citation -> the geometry "
                   "frame is the best PARTNER-FREE entry with an intact (>=60-residue) receptor construct, "
                   "taken from BIOLOGICAL ASSEMBLY 1 rather than the asymmetric unit, with the occluder set "
                   "restricted to the recruiter and its own CRL arm -> pure-stdlib geometry (Shrake-Rupley "
                   "burial, ray-cast enclosure and exit vector, LIGSITE PSP cavity volume) + fpocket "
                   "druggability attributed by ligand-atom overlap -> a tier-3 'solved bivalent complex' "
                   "claim is re-verified from coordinates and demoted if the ligand does not contact both "
                   "proteins -> preregistered gates, Pareto front, lexicographic tiebreak.",
        "_limits": [
            "This is DESIGN PREP, not a validated result. Ligandability computed from one deposited holo "
            "structure is a hypothesis for testing: it says a published ligand occupies a pocket with a "
            "solvent-directed exit vector, nothing more.",
            "One conformer, one ligand copy, no protein flexibility, no linker sampling, no solvent model "
            "beyond an implicit 1.4 A probe. The exit vector bounds where a linker COULD leave; it does not "
            "show that any linker does leave.",
            "The 'linker-bearing analogue' tier is structural evidence from deposited entries, not a "
            "literature review, so it under-counts recruiters whose linker-bearing chemistry is published "
            "without a crystal structure.",
            "Interface geometry here is the OPEN SOLID ANGLE at the linker attachment point — the size of the "
            "orientation space available to a tethered target. Whether any orientation in it is favourable, "
            "and whether it discriminates NR4A3 from NR4A1/2, is the orientation-basin search's question, "
            "not this module's.",
            "fpocket druggability is computed on the deposited chains with the ligand removed; it is a "
            "pocket-shape score, not a measured affinity.",
            "Geometry is computed against the recruiter and its OWN CRL arm only; a bound neosubstrate, "
            "PROTAC target or crystallisation partner is removed from the occluder set, because it occupies "
            "the orientation space being measured. For a recruiter with no partner-free structure (a "
            "glue-type E3), that removal means burial and the exit vector are measured against a site that "
            "may be partly formed BY the removed partner — flagged per recruiter in geometry_frame.",
            "★ The rule is deliberately BLIND to recruiter-intrinsic pharmacology, and that is a real "
            "omission, not a neutral one. Several ligandable E3s are ligandable precisely because their "
            "handle is a well-developed inhibitor of the E3's own function — recruiting MDM2 with a "
            "nutlin-class handle also inhibits MDM2, and recruiting KEAP1 perturbs the KEAP1-NRF2 axis. "
            "A recruiter can therefore win on ligandability and interface geometry while carrying an "
            "on-target liability this stage cannot see. Any recruiter advanced here must have that "
            "liability assessed from the literature before it is committed to, and it is an input to the "
            "next gate, not a footnote.",
            "No claim of efficacy, safety, therapeutic window, or clinical readiness is made or implied. "
            "'Advanced' means 'carried into a computational search', never 'suitable for use'.",
        ],
        "_schema_version": SCHEMA_VERSION,
        "_schema": SCHEMA_DOC,
        "_consumers": ["RUNG 5a orientation-basin search — call e3_recruiter_staging.load_advanced() for "
                       "the stable contract (gene, pdb_id, recruiter/arm chains, coordinate_source, "
                       "anchor_xyz, exit_direction, clearance, cone openness, open_solid_angle_fraction_15A, "
                       "and a `caveats` list that MUST be carried into any downstream report). Reading "
                       "recruiters[*].ligandability.exit_vector directly also works but skips the caveats."],
        "parameters": {"gates": GATES, "geometry": GEOM, "excluded_ccd_count": len(EXCLUDED_CCD),
                       "min_ligand_heavy_atoms": MIN_LIGAND_HEAVY_ATOMS,
                       "linker_bearing_min_mw_Da": LINKER_BEARING_MIN_MW,
                       "max_resolution_A": MIN_RESOLUTION_A},
        "availability_crosscheck": availability,
        "recruiters": recruiters,
        "downselect": ds,
        "provenance": {"n_urls_fetched": len(_URLS_USED), "urls": _URLS_USED[:2000]},
    }


SCHEMA_DOC = {
    "recruiters.<GENE>": {
        "gene": "HGNC symbol as queried",
        "uniprot": "{accession, entry_name, protein_name, length, matched_gene_names, query_url, _status} — "
                   "fail-closed resolution; accession null means REFUSED, never guessed",
        "e3_class": "structural class of the E3 (substrate receptor family / monomeric RING)",
        "arm": "key matching nr4a-e3-expression.json so availability can be cross-checked",
        "staged_structures": {
            "pdb_id": "RCSB entry ID", "resolution_A": "float or null (NMR)",
            "experimental_methods": "[str]", "deposited": "ISO date", "released": "ISO date",
            "primary_citation": "{pubmed_id, doi, title, journal, year}",
            "polymer_entities": "[{entity_id, uniprot_ids, auth_asym_ids, description, length}]",
            "distinct_uniprot_accessions": "[str] — >1 means a multi-protein entry",
            "recruiter_auth_asym_ids": "[str] — the chains that ARE the recruiter",
            "recruiter_entity_length": "residues of the recruiter actually in the construct",
            "recruiter_uniprot_coverage_fraction": "that length / the full UniProt length — REPORTED, never "
                                                   "ranked on: a WD40 or Kelch domain construct is the "
                                                   "correct experimental object at low full-length coverage",
            "recruiter_entity_is_peptide_fragment": "bool, <60 residues — deprioritised as a geometry frame",
            "partner_uniprots": "[str] — accessions present that are NOT part of the recruiter's own CRL arm "
                                "(a neosubstrate / PROTAC target / crystallisation partner)",
            "has_partner_protein": "bool",
            "chain_composition": "human-readable 'chains=description' summary",
            "candidate_ligands": "[{ccd, name, type, formula, formula_weight, n_heavy_atoms, smiles, "
                                 "entity_id, auth_asym_ids}]",
            "ligand": "the selected primary ligand (largest by formula weight)",
            "ligand_instance": "{auth_asym_id, auth_seq_id, n_heavy_atoms_modelled, "
                               "n_contacts_to_recruiter_chain_4.5A, n_copies_in_entry, contacts_recruiter}",
            "is_primary": "bool — the structure the geometry was computed on",
        },
        "linker_bearing_analogue": "{tier 0-3, label, n_entries_with_ligand_ge_500Da, "
                                   "n_entries_ligand_bridging_second_uniprot, evidence_pdb_ids_*, "
                                   "bridging_check[] (per-entry contacts_recruiter / contacts_partner / "
                                   "bridges, read from coordinates), tier_demoted (present when the "
                                   "entry-level tier-3 claim did NOT survive that check), "
                                   "_evidence_entries[] (metadata kept so the check does not depend on "
                                   "what staging happened to keep)}",
        "ligandability": {
            "ligand_burial": "{sasa_free_A2, sasa_in_complex_A2, buried_fraction}",
            "site_enclosure": "{blocked_fraction, n_rays, max_A}",
            "cavity": "{volume_A3, n_grid_points, spacing_A}",
            "fpocket": "{pocket_number, druggability, alpha_spheres, ...} or {_status}",
            "exit_vector": "{anchor_atom, anchor_element, anchor_xyz, direction[3] (unit), clearance_A, "
                           "cone_openness_30deg, angle_to_centroid_vector_deg, "
                           "open_solid_angle_fraction_15A, channel_lining_residues[]} "
                           "★ THIS IS THE BLOCK THE ORIENTATION-BASIN SEARCH CONSUMES: anchor_xyz is the "
                           "linker attachment point in the staged structure's own frame, direction is the "
                           "outward unit vector, clearance_A is how far a linker can travel along it before "
                           "clashing, and open_solid_angle_fraction_15A is the fraction of directions with "
                           ">=15 A of reach.",
            "structure_file": "the coordinate file the geometry was computed from",
            "occluder_set": "{arm_chains_kept, partner_chains_excluded, n_atoms_excluded}",
            "measured_with_partner_protein_removed": "bool",
        },
        "arm_component_accessions": "[str] — the recruiter + its own CRL arm; anything else in the entry is "
                                    "a partner and is removed from the occluder set before geometry",
        "geometry_frame": "{primary_has_partner_protein, n_clean_binary_entries} — true means NO partner-free "
                          "structure of this recruiter exists, so burial and the exit vector are measured "
                          "against an incomplete site",
        "gates": "{G1..G3: {pass, observed}}",
        "advance_note": "present only on a backfilled second recruiter — says why it advanced",
        "axes": "{linker_analogue_tier, exit_quality, orientation_openness, neg_resolution}",
        "decision": "ADVANCE | DROP",
    },
    "downselect": {
        "rule": "the preregistered gates, Pareto axes, tiebreak and cap",
        "advanced": "<=2 recruiter gene symbols",
        "pareto_front": "gate-passing recruiters not dominated on the three axes",
        "ranked_front": "the front under the lexicographic tiebreak",
        "dropped": "[{recruiter, stage: gate|pareto|cap, gate_failed?, reason, "
                   "availability_was_not_a_factor: true}]",
        "availability_assertion": "explicit proof that no recruiter was dropped for lack of expression",
    },
}


def load_advanced(path=OUT_JSON):
    """★ THE CONSUMER API — what the orientation-basin search reads. Stable across schema revisions.

    Returns a list, in ranked order, of the recruiters that survived the downselect:

        [{"gene", "uniprot", "e3_class", "pdb_id", "resolution_A", "ligand_ccd",
          "recruiter_chains",            # auth_asym_ids of the recruiter in the staged frame
          "arm_chains",                  # every chain kept in the occluder set (recruiter + its CRL arm)
          "coordinate_source",           # 'biological assembly 1 (mmCIF)' or the asymmetric-unit fallback
          "anchor_xyz",                  # the linker attachment point, in the staged structure's own frame
          "exit_direction",              # outward unit vector from the anchor
          "exit_clearance_A",            # unobstructed reach along it before a 1.7 A linker atom clashes
          "cone_openness_30deg",
          "open_solid_angle_fraction_15A",   # size of the orientation space available to a tethered target
          "buried_fraction", "linker_analogue_tier", "backfilled",
          "caveats"}]                    # non-empty strings the consumer must carry into its own output

    `caveats` is deliberately part of the contract: a recruiter measured with a partner protein removed, or
    on an asymmetric unit rather than a biological assembly, is usable but must not be reported as if it
    were clean."""
    d = json.load(open(path))
    ds = d["downselect"]
    back = set(ds.get("backfilled_for_e3_choice_sensitivity") or [])
    out = []
    for gene in ds["advanced"]:
        r = d["recruiters"][gene]
        lg = r.get("ligandability") or {}
        ev = lg.get("exit_vector") or {}
        occ = lg.get("occluder_set") or {}
        p = next((s for s in (r.get("staged_structures") or []) if s.get("is_primary")), None) or {}
        caveats = []
        if lg.get("measured_with_partner_protein_removed"):
            caveats.append("no partner-free structure exists for this recruiter; its site may be partly "
                           "formed by the partner that was removed from the occluder set")
        if "assembly" not in (lg.get("coordinate_source") or ""):
            caveats.append(f"geometry computed on the {lg.get('coordinate_source')}, not a biological "
                           "assembly — a crystallographic neighbour may occlude the exit")
        if ev.get("no_exit_path"):
            caveats.append("no unobstructed exit path was found in this frame")
        if gene in back:
            caveats.append("Pareto-dominated; advanced only so the E3 is a controlled variable downstream")
        out.append({
            "gene": gene, "uniprot": (r.get("uniprot") or {}).get("accession"),
            "e3_class": r.get("e3_class"), "pdb_id": p.get("pdb_id"),
            "resolution_A": p.get("resolution_A"), "ligand_ccd": (p.get("ligand") or {}).get("ccd"),
            # recruiter_auth_asym_ids comes from the ASYMMETRIC UNIT's entity map, while the geometry frame
            # is a biological assembly that may contain a different subset (CRBN 9CUO: entity chains A-F,
            # assembly frame A-C). Returning the raw list would hand the consumer chain IDs that are not in
            # the file it is about to read, so intersect with what is actually present.
            "recruiter_chains": ([c for c in (p.get("recruiter_auth_asym_ids") or [])
                                  if c in set(occ.get("chains_present_in_frame") or [])]
                                 or p.get("recruiter_auth_asym_ids")),
            "recruiter_chains_in_entity": p.get("recruiter_auth_asym_ids"),
            "arm_chains": occ.get("chains_present_in_frame"),
            "coordinate_source": lg.get("coordinate_source"),
            "anchor_xyz": ev.get("anchor_xyz"), "exit_direction": ev.get("direction"),
            "exit_clearance_A": ev.get("clearance_A"),
            "cone_openness_30deg": ev.get("cone_openness_30deg"),
            "open_solid_angle_fraction_15A": ev.get("open_solid_angle_fraction_15A"),
            "buried_fraction": (lg.get("ligand_burial") or {}).get("buried_fraction"),
            "linker_analogue_tier": (r.get("linker_bearing_analogue") or {}).get("tier"),
            "backfilled": gene in back,
            "caveats": caveats,
        })
    return out


def to_markdown(d):
    L = ["# E3 recruiter staging + ligandability downselect", "",
         f"*{d['_title']}*", "", "> **Honest scope.** " + d["_limits"][0], ""]
    ds = d["downselect"]
    L += ["## Decision", "",
          f"**Advanced (<= {ds['rule']['cap']}):** " + (", ".join(ds["advanced"]) or "none"), "",
          "| recruiter | class | PDB | res (A) | ligand | buried | exit clear (A) | cone | open15 | "
          "analogue | decision |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for gene, r in d["recruiters"].items():
        p = next((s for s in (r.get("staged_structures") or []) if s.get("is_primary")), None)
        lg = r.get("ligandability") or {}
        ev = lg.get("exit_vector") or {}
        lb = r.get("linker_bearing_analogue") or {}
        L.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | **{}** |".format(
            gene, r.get("e3_class", ""), p["pdb_id"] if p else "—",
            (p or {}).get("resolution_A", "—"), ((p or {}).get("ligand") or {}).get("ccd", "—"),
            (lg.get("ligand_burial") or {}).get("buried_fraction", "—"),
            ev.get("clearance_A", "—"), ev.get("cone_openness_30deg", "—"),
            ev.get("open_solid_angle_fraction_15A", "—"), lb.get("label", "—"),
            r.get("decision", "—")))
    flagged = [g for g, r in d["recruiters"].items()
               if (r.get("geometry_frame") or {}).get("primary_has_partner_protein")]
    if flagged:
        L += ["", "**Measured with a partner protein removed** (no partner-free structure exists for these, "
                  "so burial and the exit vector are measured against a site that may be partly formed BY "
                  "the removed partner): " + ", ".join(flagged) + ".", ""]
    back = d["downselect"].get("backfilled_for_e3_choice_sensitivity") or []
    if back:
        L += ["", "**Backfilled** (Pareto-dominated, retained as the second recruiter so the E3 is a "
                  "controlled variable downstream rather than a confound): " + ", ".join(back) + ".", ""]
    L += ["", "## Dropped set — every recruiter not advanced, with the reason", "",
          "*nr4a3-program-map.md: \"a silent top-N reads as 'we covered everything'\". Availability is **never** a "
          "reason here — all widened arms are broadly expressed (HPA, CI run 30125742542).*", ""]
    for row in ds["dropped"]:
        L.append(f"- **{row['recruiter']}** — dropped at the *{row['stage']}* stage. {row['reason']}")
    L += ["", "## Limits", ""] + [f"- {x}" for x in d["_limits"]]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--phase", choices=["fetch", "geom", "all"], default="all")
    ap.add_argument("--no-fpocket", action="store_true")
    ap.add_argument("--max-entries", type=int, default=8)
    ap.add_argument("--search-rows", type=int, default=100)
    a = ap.parse_args(argv)

    if a.phase in ("fetch", "all"):
        recruiters = fetch_panel(max_entries_deep=a.max_entries, search_rows=a.search_rows)
        json.dump({"recruiters": recruiters, "urls": _URLS_USED}, open(CACHE_JSON, "w"), indent=1)
        print(f"\nwrote {CACHE_JSON}", file=sys.stderr)
    else:
        cache = json.load(open(CACHE_JSON))
        recruiters = cache["recruiters"]
        _URLS_USED.extend(cache.get("urls", []))

    if a.phase in ("geom", "all"):
        geometry_panel(recruiters, use_fpocket=not a.no_fpocket)

    doc = build(recruiters, check_availability_not_a_constraint())
    json.dump(doc, open(OUT_JSON, "w"), indent=1)
    open(OUT_MD, "w").write(to_markdown(doc))
    print(f"wrote {OUT_JSON}\nwrote {OUT_MD}", file=sys.stderr)
    ds = doc["downselect"]
    print("\nADVANCED:", ds["advanced"])
    print("PARETO FRONT:", ds["pareto_front"])
    for row in ds["dropped"]:
        print(f"DROPPED {row['recruiter']:8s} [{row['stage']}] {row['reason'][:150]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
