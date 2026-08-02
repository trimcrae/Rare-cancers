#!/usr/bin/env python3
"""KNOWN-ANSWER TEST: can this program's docking pipeline recover a pose that is already known? ($0 CPU)

★★ WHY. Everything downstream of `denovo_401` — the ternary, the selectivity argument, the ABFE work —
is anchored to a PREDICTED pose in the NR4A3 ligand-binding domain, produced by docking into a
metadynamics-opened AF2 frame and re-docking into the cavity-bearing conformers of the apo NMR ensemble
8XTT. Nobody has ever asked whether that pipeline can recover a pose that is KNOWN. Until someone does,
every claim resting on the pose rests on the assumption that it can.

This is the same discipline that `selcal_interface_signature.py` applied to the paralogue-selectivity
descriptor: do not trust a readout until it reproduces an answer published before this program existed.

★ THE REGIME MATTERS MORE THAN THE SCORE. Docking a ligand back into the receptor conformation that was
solved WITH it ("self-docking") is a much easier problem than the one this program actually solves, which
is: start from an APO structure whose pocket is not shaped around any ligand, and find the bound pose. So
the benchmark is a cross-dock from apo, and the self-dock appears only as a CONTROL (below) that tells you
whether a failure came from the induced-fit gap or from the docking protocol itself.

──────────────────────────────────────────────────────────────────────────────────────────────────────
⛔ PRE-REGISTERED CRITERION — FIXED IN WRITING BEFORE THE FIRST RUN. DO NOT TUNE.
──────────────────────────────────────────────────────────────────────────────────────────────────────
PRIMARY ENDPOINT. Dock the holo ligand into the APO receptor using the pipeline's own settings — the box,
exhaustiveness and `num_modes` are read at run time out of `nr4a3_warhead.dock_into`, never re-typed —
and measure the symmetry-corrected heavy-atom RMSD of the TOP-RANKED pose to the crystallographic ligand,
after sequence-matched Ca superposition of the apo receptor onto the holo receptor over the pocket-lining
residues.

    RECOVERED      RMSD <= 2.00 A       (`RECOVER_RMSD_A`)
    PARTIAL        2.00 A < RMSD <= 4.00 A  — right region of the protein, wrong pose (`PARTIAL_RMSD_A`)
    NOT RECOVERED  RMSD > 4.00 A

2.00 A is not chosen here: it is the field's standard redocking-success boundary, the same number used by
the Astex/CASF/PDBbind pose-prediction evaluations. 4.00 A is the conventional "wrong pose" boundary in the
same literature. SECONDARY endpoint: fraction of native ligand-contacting receptor residues recovered
(`fnat`), success at >= 0.50 — reported always, and never used to overturn the primary.

CONTROLS, ALSO FIXED IN ADVANCE, because a bare number here would not be interpretable:
  C1 SELF-DOCK into the HOLO receptor, identical settings. **If C1 does not clear 2.00 A the whole
     experiment is INCONCLUSIVE**, not a failure of the apo pipeline: a protocol that cannot recover the
     pose when handed the very conformer the ligand was solved in is being measured on the protocol, not
     on induced fit. Stated this way before running so it cannot become an excuse afterwards.
  C2 RANDOM-IN-BOX NULL, `N_NULL` random rigid placements of the same ligand inside the same box. This is
     the POWER of the criterion: if a random placement clears 2.00 A with non-negligible probability, then
     passing means nothing. `selcal_interface_signature.py` records the opposite failure — a check so
     strict it reported a real recovery as a miss — and both are the same bug, a criterion whose power was
     never measured.
  C3 BLIND vs ORACLE BOX. The pipeline picks its pocket with fpocket and never sees the ligand, so the
     primary endpoint uses the BLIND box. An ORACLE box centred on the crystallographic ligand is run
     alongside **purely as a decomposition**: blind-fails-while-oracle-succeeds means pocket DETECTION
     failed; both failing means pose PLACEMENT failed. The oracle number is never the headline and can
     never turn a NOT RECOVERED into a pass.
  C1b ONE CONTROL PER BLIND ARM (added 2026-08-02 after the first scored panel; the primary endpoint is
     UNCHANGED). C1 as written self-docks through the pipeline's transferred site only. When that site is
     not where the ligand actually binds — 4REF is "TR3 LBD_L449W in complex with Molecule 2", an
     engineered tryptophan mutant whose ligand sits ~19 A from the canonical nuclear-receptor cavity — C1
     fails for a reason that says nothing about whether the DOCKING works, and it drags the independent
     fpocket arm down with it. So each blind arm now carries a self-dock through its own site-selection
     route and is reported against that. This ADDS reporting; it moves no threshold and cannot turn a
     failure into a pass.

★ A PANEL, NOT A PICK. `PANEL_SIZE` candidate pairs are attempted in the pre-registered rank order — one
per distinct crystallographic answer, at most `MAX_PER_PROTEIN` per protein — and EVERY one is reported,
including the ones R2b throws out. There is no early exit on "enough good ones", because an exit conditioned
on results is a way of choosing which results to have. The panel-level answer applies the same C1 rule one
level up: a pair whose control fails is uninterpretable, and the count of those is reported beside the
aggregate rather than averaged into it.

BOTH OUTCOMES, WRITTEN DOWN NOW:
  · RECOVERED  → the pipeline has been shown, once, to recover a crystallographic pose from an apo
    receptor in a nuclear-receptor LBD. That removes one specific reason to disbelieve the NR4A3 pose.
    It does NOT make the NR4A3 pose correct, and it says nothing about selectivity or efficacy.
  · NOT RECOVERED → the assumption under everything anchored to the denovo_401 pose has been tested and
    failed in a comparable regime. That does not prove the NR4A3 pose wrong. It removes the presumption
    that it is right, and the manuscript has to say so wherever "the pose" is currently singular.
  · INCONCLUSIVE → only via C1 or C2, and the reason must be named in the artifact.

⛔ NO THRESHOLD IN THIS MODULE MAY BE CHANGED AFTER THE FIRST RUN. A changed threshold goes in an appendix
with the superseded value retained (CLAUDE.md §1.2), never edited in place.
──────────────────────────────────────────────────────────────────────────────────────────────────────

★ THE BENCHMARK IS SOURCED, NEVER ASSUMED. `mode=source` runs a real RCSB query over a pre-declared list
of nuclear-receptor UniProt accessions, classifies every deposited entry as apo or holo from its own
non-polymer entities, and writes the whole considered set — including the rejects and why — into the
artifact. Selection then applies `SELECTION_RULES` in order. **If nothing passes, that is the finding**:
this module reports "no suitable benchmark exists" and stops, rather than substituting an easy globular
pocket and calling it a control.

⚠ AN INPUT WE COULD NOT READ IS UNREAD, NOT ABSENT — every network or parse failure is recorded in
`refusals` with the URL or path that produced it.

⛔ Claims nothing about NR4A3 selectivity, efficacy or a therapeutic window. Re-scores no leg, moves no
verdict, amends no preregistration.

Output: apo-pose-recovery.json.  MODE=source|select|run (default run). No GPU, no rental.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "apo-pose-recovery.json")
WORK = os.environ.get("APO_RECOVERY_WORK", os.path.join(HERE, "_apo_recovery_work"))

# ---------------------------------------------------------------------------------- fixed thresholds
RECOVER_RMSD_A = 2.00      # field-standard redocking-success boundary
PARTIAL_RMSD_A = 4.00      # field-standard "wrong pose" boundary
FNAT_SUCCESS = 0.50        # secondary endpoint
N_NULL = 200               # random-in-box placements for the power control
NULL_POWER_MAX = 0.05      # if P(random <= RECOVER_RMSD_A) exceeds this, the criterion has no power

# ------------------------------------------------------------------- what counts as a real ligand
#: Non-polymer components that are crystallisation/cryo/buffer matter, not ligands. A structure carrying
#: only these is APO. Standard list; it is the reason a glycerol does not make a structure "holo".
ADDITIVES = {
    "HOH", "DOD", "SO4", "PO4", "GOL", "EDO", "PEG", "PG4", "PGE", "1PE", "2PE", "P6G", "MPD", "ACT",
    "ACY", "FMT", "CIT", "FLC", "TRS", "EPE", "MES", "IMD", "DMS", "TLA", "MLI", "OXL", "BME", "DTT",
    "IOD", "BR", "CL", "NA", "K", "MG", "CA", "ZN", "MN", "FE", "NI", "CO", "CU", "CD", "HG", "PT",
    "AU", "CS", "RB", "SR", "BA", "NH4", "AZI", "NO3", "CO3", "SCN", "UNX", "UNL", "PLM", "MYR",
    "BOG", "LDA", "C8E", "OCT", "HEZ", "BU3", "IPA", "EOH", "MOH", "ACE", "NH2", "SIN", "MRD",
}
LIG_MIN_MW = 200.0         # below this a "ligand" is an additive by another name
LIG_MAX_MW = 800.0         # above this it is a peptide/cofactor/lipid, not the regime being tested
LIG_MIN_HEAVY = 15

# ------------------------------------------------------------------- the family the search runs over
#: Human nuclear-receptor ligand-binding domains, declared BEFORE looking at what is deposited, so the
#: search cannot be steered toward a convenient answer. NR4A2/NR4A1 lead because they are NR4A3's own
#: subfamily and share its defining problem (an LBD reported to lack a classical ligand cavity), which is
#: precisely the regime the NR4A3 work is in.
NR_ACCESSIONS = [
    ("P43354", "NR4A2 / Nurr1",  "NR4A3's closest paralogue; LBD reported to have no classical cavity"),
    ("P22736", "NR4A1 / Nur77",  "NR4A subfamily; the other paralogue this program scores against"),
    ("Q92570", "NR4A3 / NOR-1",  "the target itself — included so its own deposits are counted, not to test on"),
    ("P19793", "RXRA",           "canonical apo LBD with a large holo-vs-apo helix-12 rearrangement"),
    ("P37231", "PPARG",          "apo and holo LBD both deposited; large, plastic pocket"),
    ("P10276", "RARA",           "classic NR apo/holo pair literature"),
    ("P51449", "RORC / RORgt",   "inverse-agonist chemistry with induced-fit pocket changes"),
    ("Q96RI1", "NR1H4 / FXR",    "well-populated apo and holo sets"),
    ("O75469", "NR1I2 / PXR",    "notoriously plastic pocket"),
    ("P11473", "VDR",            "apo/holo pair literature"),
    ("P10828", "THRB",           "apo/holo pair literature"),
    ("P04150", "NR3C1 / GR",     "apo LBD is unstable — included to test the search, not because it will win"),
]

RCSB_SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"
RCSB_GRAPHQL = "https://data.rcsb.org/graphql"

#: Selection rules, applied IN ORDER. Recorded in the artifact so the choice is auditable.
SELECTION_RULES = [
    "R1 HARD  — apo and holo must be the same UniProt accession.",
    "R2 HARD  — the holo ligand must be drug-like: %.0f <= MW <= %.0f, >= %d heavy atoms, not an additive."
    % (LIG_MIN_MW, LIG_MAX_MW, LIG_MIN_HEAVY),
    "R3 HARD  — the apo entry must carry NO drug-like non-polymer entity at all (ions/buffers allowed).",
    "R4 HARD  — apo and holo sequences must align at >= 95 % identity over the common region (same "
    "protein, not a chimera or a distant ortholog).",
    "R5 HARD  — the apo receptor must yield at least one fpocket pocket, or there is nothing to dock into.",
    "R6 RANK  — prefer NR4A subfamily (NR4A2 > NR4A1 > others), because that is NR4A3's own regime.",
    "R7 RANK  — prefer an apo solved by SOLUTION NMR with multiple models, which mirrors 8XTT exactly.",
    "R8 RANK  — prefer better holo resolution, then better apo resolution.",
    "R9 REPORT — measure, do not assume, the apo->holo induced fit (pocket Ca RMSD) and record it.",
    "R2b HARD — the holo ligand must NOT be covalently linked to the receptor (no LINK record joining it "
    "to a protein atom). A non-covalent docking protocol cannot in principle reproduce a covalent pose, so "
    "scoring one would measure the wrong thing. ADDED 2026-08-02 AFTER SOURCING BUT BEFORE ANY RMSD "
    "EXISTED — the first run's primary arm errored at the site transfer, so no recovery number had been "
    "computed when this rule was written. Recorded here rather than edited in silently (CLAUDE.md §1.2).",
]

#: How many distinct benchmark pairs to run. ONE case is thin and invites the reading that the pair was
#: chosen for its answer, so the panel is fixed at three DISTINCT crystallographic answers and every member
#: is reported whatever it returns. The PRIMARY verdict is still the rank-1 pair; the rest are supporting
#: cases, never a menu to pick from.
N_BENCHMARKS = 3

#: At most this many pairs from any one protein, so the panel is not one protein N times.
MAX_PER_PROTEIN = 2

#: How many candidate pairs the panel ATTEMPTS. Every one of them is reported, whatever it returns — there
#: is no early exit on "enough good ones", because an early exit conditioned on results is a way of
#: choosing which results to have. The list is fixed by SELECTION_RULES before any structure is fetched.
PANEL_SIZE = 12

#: Wall-clock budget per candidate pair, and for the panel as a whole. CLAUDE.md §6: the per-unit timeout
#: is the real hang-guard. One pathological ligand — a substructure match that goes exponential, an RCSB
#: fetch that stalls — must cost that pair and no more, and must surface as a REFUSAL with its elapsed
#: time rather than as a killed job with nothing written.
PAIR_BUDGET_S = int(os.environ.get("APO_PAIR_BUDGET_S", "420"))
PANEL_BUDGET_S = int(os.environ.get("APO_PANEL_BUDGET_S", "2700"))


# ==================================================================================================
# NETWORK — every failure becomes a refusal with its URL.
# ==================================================================================================

def _get(url, data=None, timeout=60):
    req = urllib.request.Request(url, data=data,
                                 headers={"Accept": "application/json",
                                          "Content-Type": "application/json",
                                          "User-Agent": "Rare-cancers/apo_pose_recovery"})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return json.loads(fh.read().decode("utf-8"))


def entries_for_accession(acc):
    """[pdb_id] deposited for this UniProt accession, or (None, why). A real query, not a memory."""
    q = {
        "query": {"type": "terminal", "service": "text", "parameters": {
            "attribute": "rcsb_polymer_entity_container_identifiers."
                         "reference_sequence_identifiers.database_accession",
            "operator": "exact_match", "value": acc}},
        "return_type": "entry",
        "request_options": {"paginate": {"start": 0, "rows": 500}, "results_verbosity": "compact"},
    }
    url = RCSB_SEARCH + "?json=" + urllib.parse.quote(json.dumps(q))
    try:
        doc = _get(url)
    except Exception as e:                                    # noqa: BLE001
        return None, "%s: %s (%s)" % (type(e).__name__, e, RCSB_SEARCH)
    return [str(x) for x in doc.get("result_set", [])], None


ENTRY_QUERY = """
query($ids:[String!]!){
  entries(entry_ids:$ids){
    rcsb_id
    struct { title }
    exptl { method }
    rcsb_entry_info { resolution_combined polymer_entity_count_protein nonpolymer_entity_count
                      deposited_model_count }
    polymer_entities {
      entity_poly { pdbx_seq_one_letter_code_can }
      rcsb_polymer_entity_container_identifiers {
        auth_asym_ids
        reference_sequence_identifiers { database_accession database_name }
      }
    }
    nonpolymer_entities {
      rcsb_nonpolymer_entity_container_identifiers { auth_asym_ids }
      nonpolymer_comp {
        chem_comp { id name formula_weight type }
        rcsb_chem_comp_descriptor { SMILES_stereo }
      }
    }
  }
}
"""


def entry_details(ids, batch=40):
    """Full metadata for a list of entry ids, or (None, why). One GraphQL call per batch."""
    out, why = [], None
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        body = json.dumps({"query": ENTRY_QUERY, "variables": {"ids": chunk}}).encode()
        try:
            doc = _get(RCSB_GRAPHQL, data=body)
        except Exception as e:                                # noqa: BLE001
            why = "%s: %s (%s, batch starting %s)" % (type(e).__name__, e, RCSB_GRAPHQL, chunk[0])
            continue
        if doc.get("errors"):
            why = "GraphQL errors: %s" % json.dumps(doc["errors"])[:300]
        out.extend([e for e in (doc.get("data") or {}).get("entries") or [] if e])
    return out, why


# ==================================================================================================
# PURE CLASSIFICATION — no network. Unit-tested in tests/test_apo_pose_recovery.py.
# ==================================================================================================

def drug_like(comp):
    """Is this chem-comp record a real ligand rather than crystallisation matter? (bool, why)."""
    cid = (comp or {}).get("id") or ""
    if not cid:
        return False, "no comp id"
    if cid.upper() in ADDITIVES:
        return False, "%s is on the crystallisation-additive list" % cid
    mw = comp.get("formula_weight")
    if mw is None:
        return False, "%s has no formula weight" % cid
    if mw < LIG_MIN_MW:
        return False, "%s MW %.1f < %.0f" % (cid, mw, LIG_MIN_MW)
    if mw > LIG_MAX_MW:
        return False, "%s MW %.1f > %.0f" % (cid, mw, LIG_MAX_MW)
    ctype = (comp.get("type") or "").upper()
    if "PEPTIDE" in ctype or "SACCHARIDE" in ctype or "RNA" in ctype or "DNA" in ctype:
        return False, "%s type %r is not a small molecule" % (cid, comp.get("type"))
    return True, "%s MW %.1f, type %s" % (cid, mw, comp.get("type"))


def classify_entry(entry, accession):
    """{pdb, method, resolution, n_models, ligands[], apo(bool), seq, ...} from one GraphQL record."""
    info = entry.get("rcsb_entry_info") or {}
    res = (info.get("resolution_combined") or [None])
    ligands, rejected = [], []
    for ne in entry.get("nonpolymer_entities") or []:
        comp = ((ne.get("nonpolymer_comp") or {}).get("chem_comp")) or {}
        desc = ((ne.get("nonpolymer_comp") or {}).get("rcsb_chem_comp_descriptor")) or {}
        ok, why = drug_like(comp)
        rec = {"comp_id": comp.get("id"), "name": comp.get("name"),
               "mw": comp.get("formula_weight"), "type": comp.get("type"),
               "smiles": desc.get("SMILES_stereo"),
               "chains": (ne.get("rcsb_nonpolymer_entity_container_identifiers") or {})
               .get("auth_asym_ids") or [], "why": why}
        (ligands if ok else rejected).append(rec)
    seq, chains = None, []
    for pe in entry.get("polymer_entities") or []:
        ids = (pe.get("rcsb_polymer_entity_container_identifiers") or {})
        accs = [(r or {}).get("database_accession")
                for r in (ids.get("reference_sequence_identifiers") or [])]
        if accession in accs:
            seq = ((pe.get("entity_poly") or {}).get("pdbx_seq_one_letter_code_can") or "").replace("\n", "")
            chains = ids.get("auth_asym_ids") or []
            break
    return {
        "pdb": entry.get("rcsb_id"),
        "title": ((entry.get("struct") or {}).get("title") or "")[:180],
        "method": ((entry.get("exptl") or [{}])[0] or {}).get("method"),
        "resolution_A": res[0] if res else None,
        "n_models": info.get("deposited_model_count"),
        "ligands": ligands,
        "non_ligand_components": [r["comp_id"] for r in rejected],
        "apo": not ligands,
        "sequence": seq,
        "chains": chains,
    }


def pair_candidates(by_acc):
    """[(score, candidate)] apo/holo pairs, ranked by SELECTION_RULES. Pure — takes classified entries."""
    prio = {a: i for i, (a, _n, _w) in enumerate(NR_ACCESSIONS)}
    out = []
    for acc, rec in by_acc.items():
        apos = [e for e in rec["entries"] if e["apo"] and e["sequence"]]
        holos = [e for e in rec["entries"] if e["ligands"] and e["sequence"]]
        if not apos or not holos:
            continue
        for apo in apos:
            for holo in holos:
                lig = max(holo["ligands"], key=lambda l: l.get("mw") or 0)
                cand = {
                    "accession": acc, "protein": rec["name"], "apo": apo["pdb"], "holo": holo["pdb"],
                    "apo_method": apo["method"], "apo_models": apo["n_models"],
                    "apo_resolution_A": apo["resolution_A"], "holo_resolution_A": holo["resolution_A"],
                    "ligand": {k: lig.get(k) for k in ("comp_id", "name", "mw", "smiles")},
                    "apo_title": apo["title"], "holo_title": holo["title"],
                }
                nmr = 1 if (apo["method"] or "").upper().startswith("SOLUTION NMR") else 0
                score = (
                    prio.get(acc, 99),                                    # R6
                    -nmr,                                                 # R7
                    holo["resolution_A"] if holo["resolution_A"] is not None else 9.9,   # R8
                    apo["resolution_A"] if apo["resolution_A"] is not None else 9.9,
                )
                out.append((score, cand))
    out.sort(key=lambda t: t[0])
    return out


# ==================================================================================================
# STRUCTURE HANDLING
# ==================================================================================================

def fetch_pdb(pdb_id, dest):
    import nr4a3_8xtt_benchmark as bm
    return bm.fetch_rcsb(pdb_id, dest)


def protein_only(pdb_text, chain=None):
    """ATOM records of one chain (the largest if unspecified) + END. First MODEL only."""
    lines, cur_chain_counts = [], {}
    for line in pdb_text.splitlines(keepends=True):
        if line.startswith("ENDMDL"):
            break
        if line.startswith("ATOM"):
            cur_chain_counts[line[21]] = cur_chain_counts.get(line[21], 0) + 1
            lines.append(line)
    if not lines:
        return ""
    want = chain or max(cur_chain_counts, key=lambda c: cur_chain_counts[c])
    keep = [l for l in lines if l[21] == want and l[16] in (" ", "A")]
    return "".join(keep) + "END\n"


def ligand_hetatms(pdb_text, comp_id):
    """HETATM lines of the largest copy of `comp_id` (first model), grouped by (chain, resseq)."""
    groups = {}
    for line in pdb_text.splitlines(keepends=True):
        if line.startswith("ENDMDL"):
            break
        if line.startswith("HETATM") and line[17:20].strip().upper() == comp_id.upper():
            if line[16] not in (" ", "A"):
                continue
            groups.setdefault((line[21], line[22:26]), []).append(line)
    if not groups:
        return None, None
    key = max(groups, key=lambda k: len(groups[k]))
    return groups[key], key


#: Words in a deposit title that declare an engineered construct. ⛔ REPORTED, NEVER FILTERED — a rule that
#: removed structures until the benchmark passed would be exactly the tuning this module forbids. But a
#: reader has to SEE it: 4REF ("Crystal Structure of TR3 LBD_L449W in complex with Molecule 2") is a
#: tryptophan point mutant whose ligand sits ~19 A from the canonical nuclear-receptor cavity, and that is
#: what its arms are measuring.
MUTANT_MARKERS = ("MUTANT", "MUTATION", " MUT ", "_L4", "_S4", "_W4", "_F4")


def engineered_flag(*titles):
    """(bool, evidence) — does any deposit title declare an engineered construct? Reported, never gating."""
    hits = [t for t in titles if any(m in (t or "").upper() for m in MUTANT_MARKERS)]
    return bool(hits), hits


def covalent_links(pdb_text, comp_id):
    """LINK records joining `comp_id` to anything else — R2b's evidence, read from the deposit itself.

    A LINK record is how the PDB states a covalent bond between residues, so a ligand appearing in one is
    covalently attached and a non-covalent dock cannot reproduce its pose by construction. Read from the
    file rather than inferred from the ligand's chemistry, because only the depositor knows."""
    out = []
    want = comp_id.upper()
    for line in pdb_text.splitlines():
        if not line.startswith("LINK"):
            continue
        if line[17:20].strip().upper() == want or line[47:50].strip().upper() == want:
            out.append(line.rstrip())
    return out


def het_coords(lines):
    out = []
    for l in lines:
        elem = (l[76:78].strip() or l[12:16].strip()[:1]).upper()
        if elem == "H" or elem == "D":
            continue
        out.append((float(l[30:38]), float(l[38:46]), float(l[46:54])))
    return out


def centroid(points):
    n = float(len(points))
    return tuple(sum(p[i] for p in points) / n for i in range(3))


def residues_near(pdb_text, points, cutoff):
    """{resseq} of protein residues with a heavy atom within `cutoff` of any of `points`."""
    c2 = cutoff * cutoff
    hit = set()
    for line in pdb_text.splitlines():
        if not line.startswith("ATOM"):
            continue
        elem = (line[76:78].strip() or line[12:16].strip()[:1]).upper()
        if elem == "H":
            continue
        try:
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            r = int(line[22:26])
        except ValueError:
            continue
        for (px, py, pz) in points:
            if (x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2 <= c2:
                hit.add(r)
                break
    return hit


# ==================================================================================================
# THE RUN
# ==================================================================================================

def pipeline_dock_params():
    """The docking settings THE PIPELINE uses, read out of its own source — never re-typed here.

    `nr4a3_warhead.dock_into` hard-codes the box size, exhaustiveness and num_modes in the smina command
    it builds. Parsing them out means this benchmark cannot drift away from the pipeline it is testing;
    if someone changes the pipeline's exhaustiveness, this module changes with it and says so."""
    import inspect
    import nr4a3_warhead as wh
    src = inspect.getsource(wh.dock_into)
    out = {}
    for key in ("size_x", "size_y", "size_z", "exhaustiveness", "num_modes"):
        marker = '"--%s", "' % key
        i = src.find(marker)
        if i >= 0:
            out[key] = src[i + len(marker):src.find('"', i + len(marker))]
    out["_read_from"] = "nr4a3_warhead.dock_into source"
    return out


def dock(receptor_pdb, center, ligand_sdf, tag, work, num_modes=None):
    """The pipeline's own dock. `num_modes` override is used ONLY by the diagnostic multi-pose run."""
    import nr4a3_warhead as wh
    wh.OUT = work
    if num_modes is None:
        return wh.dock_into(receptor_pdb, center, ligand_sdf, tag)
    # diagnostic variant: same command, more modes retained
    import nr4a3_dock as ndock
    smina = ndock._which("smina")
    out_sdf = os.path.join(work, "docked_%s.sdf" % tag)
    p = pipeline_dock_params()
    subprocess.run([smina, "-r", receptor_pdb, "-l", ligand_sdf,
                    "--center_x", str(center[0]), "--center_y", str(center[1]),
                    "--center_z", str(center[2]),
                    "--size_x", p.get("size_x", "24"), "--size_y", p.get("size_y", "24"),
                    "--size_z", p.get("size_z", "24"),
                    "--exhaustiveness", p.get("exhaustiveness", "8"),
                    "--num_modes", str(num_modes), "-o", out_sdf],
                   capture_output=True, text=True)
    return {}, out_sdf


def crystal_mol(lines, smiles):
    """The crystallographic ligand as an RDKit molecule with the reference bond graph, or (None, why).

    ⛔ CORRESPONDENCE IS CHEMICAL. The crystal copy carries CCD atom names and the docked copy carries
    RDKit's own; matching by name or by proximity would report a small deviation for a flipped molecule
    (the failure documented in `selcal_cofold_decompose.py`). So the crystal coordinates are posed onto a
    molecule built from the CCD SMILES, and RMSD is then a graph match with automorphisms enumerated."""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    ref = Chem.MolFromSmiles(smiles) if smiles else None
    if ref is None:
        return None, "CCD SMILES unparseable: %r" % (smiles,)
    ref = Chem.RemoveHs(ref)
    xyz = het_coords(lines)
    if len(xyz) != ref.GetNumAtoms():
        # a partially-occupied or alternate-conformer copy; refuse rather than guess a correspondence
        return None, ("crystal copy has %d heavy atoms but the CCD graph has %d — refusing to guess an "
                      "atom correspondence" % (len(xyz), ref.GetNumAtoms()))
    order = _pdb_order_to_ccd(lines, ref)
    if order is None:
        return None, "could not order the crystal atoms onto the CCD graph"
    conf = Chem.Conformer(ref.GetNumAtoms())
    from rdkit.Geometry import Point3D
    for ccd_i, pdb_i in enumerate(order):
        x, y, z = xyz[pdb_i]
        conf.SetAtomPosition(ccd_i, Point3D(x, y, z))
    m = Chem.Mol(ref)
    m.RemoveAllConformers()
    m.AddConformer(conf, assignId=True)
    try:
        Chem.SanitizeMol(m)
    except Exception as e:                                    # noqa: BLE001
        return None, "sanitize failed: %s" % e
    AllChem.AssignStereochemistryFrom3D(m)
    return m, None


def _pdb_order_to_ccd(lines, ref):
    """Index map CCD-atom -> line index, by element-matched graph isomorphism on the distance geometry.

    Both copies are the same component, so a correspondence exists; it is found by building a molecule
    from the crystal coordinates with RDKit's connectivity perception and substructure-matching the CCD
    skeleton onto it — a GRAPH match, so a flipped or mis-ordered deposit still maps correctly."""
    from rdkit import Chem
    from rdkit.Chem import rdDetermineBonds
    heavy = [l for l in lines if (l[76:78].strip() or l[12:16].strip()[:1]).upper() not in ("H", "D")]
    block = ["%d" % len(heavy), "crystal"]
    for l in heavy:
        elem = (l[76:78].strip() or l[12:16].strip()[:1]).title()
        block.append("%s %s %s %s" % (elem, l[30:38].strip(), l[38:46].strip(), l[46:54].strip()))
    try:
        raw = Chem.MolFromXYZBlock("\n".join(block) + "\n")
        if raw is None:
            return None
        rdDetermineBonds.DetermineConnectivity(raw)
    except Exception:                                         # noqa: BLE001
        return None
    skel = Chem.Mol(ref)
    for b in skel.GetBonds():
        b.SetBondType(Chem.BondType.SINGLE)
        b.SetIsAromatic(False)
    for a in skel.GetAtoms():
        a.SetIsAromatic(False)
        a.SetNoImplicit(True)
        a.SetNumExplicitHs(0)
        a.SetFormalCharge(0)
    try:
        Chem.SanitizeMol(skel, Chem.SanitizeFlags.SANITIZE_SYMMRINGS |
                         Chem.SanitizeFlags.SANITIZE_ADJUSTHS, catchErrors=True)
    except Exception:                                         # noqa: BLE001
        pass
    match = raw.GetSubstructMatch(skel, useChirality=False)
    if match and len(match) == ref.GetNumAtoms():
        return list(match)
    return None


def random_in_box_null(mol, center, size, n=N_NULL, seed=20260802):
    """RMSD distribution of `n` random rigid placements of `mol` inside the docking box.

    The POWER of the 2 A criterion. Rotations are drawn from a uniform quaternion so orientations are not
    biased toward the identity, and translations uniformly inside the box, which is exactly the space the
    docking search is allowed to explore."""
    import random
    from rdkit import Chem
    from rdkit.Chem import rdMolAlign
    from rdkit.Geometry import Point3D
    rng = random.Random(seed)
    conf = mol.GetConformer()
    pts = [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
           for i in range(mol.GetNumAtoms())]
    c = centroid(pts)
    local = [(p[0] - c[0], p[1] - c[1], p[2] - c[2]) for p in pts]
    half = [s / 2.0 for s in size]
    vals = []
    for _ in range(n):
        u1, u2, u3 = rng.random(), rng.random(), rng.random()
        q = (math.sqrt(1 - u1) * math.sin(2 * math.pi * u2), math.sqrt(1 - u1) * math.cos(2 * math.pi * u2),
             math.sqrt(u1) * math.sin(2 * math.pi * u3), math.sqrt(u1) * math.cos(2 * math.pi * u3))
        x, y, z, w = q
        R = [[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
             [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
             [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]]
        t = (center[0] + rng.uniform(-half[0], half[0]),
             center[1] + rng.uniform(-half[1], half[1]),
             center[2] + rng.uniform(-half[2], half[2]))
        cand = Chem.Mol(mol)
        cc = cand.GetConformer()
        for i, (lx, ly, lz) in enumerate(local):
            cc.SetAtomPosition(i, Point3D(
                R[0][0] * lx + R[0][1] * ly + R[0][2] * lz + t[0],
                R[1][0] * lx + R[1][1] * ly + R[1][2] * lz + t[1],
                R[2][0] * lx + R[2][1] * ly + R[2][2] * lz + t[2]))
        try:
            vals.append(float(rdMolAlign.CalcRMS(cand, mol)))
        except Exception:                                     # noqa: BLE001
            continue
    vals.sort()
    if not vals:
        return {"n": 0, "p_within_criterion": None}
    return {"n": len(vals), "min_A": round(vals[0], 2), "median_A": round(vals[len(vals) // 2], 2),
            "max_A": round(vals[-1], 2),
            "p_within_criterion": round(sum(1 for v in vals if v <= RECOVER_RMSD_A) / len(vals), 4),
            "_criterion_A": RECOVER_RMSD_A,
            "_note": "uniform random rigid placements of the same ligand in the same box; this is the "
                     "probability that the success criterion is met by chance"}


# ==================================================================================================
# BOX PLACEMENT — three, one of them primary, all declared before the run.
# ==================================================================================================
# ⛔ WHICH BOX IS THE PRIMARY ENDPOINT IS A PRE-REGISTERED CHOICE, and it is the one that mirrors what the
# NR4A3 pipeline actually did. That pipeline did NOT take fpocket's top-ranked pocket: it took the
# ORTHOSTERIC NR cavity ("Pocket 5", nr4a3_dock.py) and used fpocket to confirm it was druggable, then
# transferred that site onto every other receptor — onto 8XTT by sequence alignment
# (nr4a3_8xtt_redock.py) and onto NR4A1/NR4A2 by BLOSUM62 alignment (nr4a3_warhead.py). Granting the
# benchmark the same prior knowledge, by the same transfer, is what makes this a test OF THE PIPELINE
# rather than a test of fpocket's ranking. The fully-agnostic top-druggability box is reported alongside
# it, and the oracle box only as the C3 decomposition.

def nr4a3_lbd_reference(af2_reference_pdb, work):
    """The AF2 NR4A3 LBD window as a standalone PDB, or (None, why).

    ⚠ THE WINDOW MATTERS. `AF-Q92570.pdb` is the FULL-LENGTH model; a global BLOSUM62 alignment of 626
    residues against a ~250-residue LBD construct pays end-gap penalties that can shift the mapping. The
    pipeline never aligns the full-length model either — `nr4a3_matrix`/`nr4a3_warhead` work on the
    LBD-trimmed receptor. So the reference written here is the same window
    (`nr4a3_8xtt_benchmark.LBD_FIRST..LBD_LAST`), and the identity that comes out is REPORTED, not assumed.
    """
    import nr4a3_8xtt_benchmark as bm
    if not os.path.exists(af2_reference_pdb):
        return None, "AF2 reference not on disk: %s" % af2_reference_pdb
    keep = []
    for line in open(af2_reference_pdb, errors="replace"):
        if not line.startswith("ATOM"):
            continue
        try:
            r = int(line[22:26])
        except ValueError:
            continue
        if bm.LBD_FIRST <= r <= bm.LBD_LAST:
            keep.append(line)
    if not keep:
        return None, "no residues in the LBD window %d-%d of %s" % (bm.LBD_FIRST, bm.LBD_LAST,
                                                                    af2_reference_pdb)
    return _write(os.path.join(work, "nr4a3_lbd_reference.pdb"), "".join(keep) + "END\n"), None


def transfer_identity(ref_pdb, receptor_pdb):
    """Aligned-column identity between the two chains, for the record. NEVER a gate here — see below."""
    import nr4a3_8xtt_benchmark as bm
    try:
        _c, _rn, sa, _ca = bm.chain_ca(_read(ref_pdb))
        _c2, _rn2, sb, _ca2 = bm.chain_ca(_read(receptor_pdb))
        ba, bb = bm._biopython_align(sa, sb)
        return round(bm.identity_from_blocks(ba, bb, sa, sb), 4)
    except Exception:                                         # noqa: BLE001
        return None


def pipeline_box(receptor_pdb, af2_reference_pdb, work):
    """PRIMARY box: NR4A3's own Pocket-5 transferred onto this receptor, then Ca centroid.

    ⛔ THE TRANSFER KERNEL IS `nr4a3_warhead.map_pocket_to_paralogue`, NOT `map_uniprot_to_pdb`, and the
    difference is load-bearing — it is the bug the first CI run died on. `map_uniprot_to_pdb` RAISES below
    80 % identity (`MIN_ALIGN_IDENTITY`) because it exists to map Q92570 onto a deposit of the SAME
    protein, where a low identity means a corrupt download. The benchmark receptor is a DIFFERENT protein
    (NR4A2 measured at 0.656 against NR4A3), so that guard fired on the very best candidate and returned
    an error with no science attached. `map_pocket_to_paralogue` is the kernel the pipeline ACTUALLY uses
    to carry Pocket-5 onto NR4A1 and NR4A2 — this identical operation, at this identical identity — and it
    has no such gate. Boxing is then `nr4a3_warhead.pocket_box`, so "the site" means here what it means
    everywhere else in the pipeline.

    Returns (center, detail) or (None, why). Uses NO ligand information."""
    import nr4a3_8xtt_benchmark as bm
    import nr4a3_warhead as wh
    ref, why = nr4a3_lbd_reference(af2_reference_pdb, work)
    if ref is None:
        return None, why
    try:
        mapped = wh.map_pocket_to_paralogue(ref, receptor_pdb, list(bm.POCKET5))
    except Exception as e:                                    # noqa: BLE001
        return None, "Pocket-5 transfer failed: %s: %s" % (type(e).__name__, e)
    ident = transfer_identity(ref, receptor_pdb)
    if not mapped:
        return None, ("no NR4A3 Pocket-5 residue mapped onto this receptor (aligned identity %s) — the "
                      "site transfer the pipeline relies on does not reach this protein" % ident)
    try:
        center, nbox = wh.pocket_box(receptor_pdb, mapped)
    except Exception as e:                                    # noqa: BLE001
        return None, "pocket_box failed on the mapped residues: %s" % e
    return center, {"mapped_residues": sorted(set(mapped)), "n_box_ca": nbox,
                    "nr4a3_aligned_identity": ident,
                    "n_pocket5_transferred": len(set(mapped)), "n_pocket5_source": len(bm.POCKET5),
                    "_source": "NR4A3 Pocket-5 (nr4a3_8xtt_benchmark.POCKET5) carried across by "
                               "nr4a3_warhead.map_pocket_to_paralogue — the pipeline's own transfer"}

def fpocket_boxes(receptor_pdb):
    """([pocket...] ranked by druggability, why) from fpocket on this receptor. No ligand information."""
    import nr4a3_8xtt_benchmark as bm
    import shutil
    if not shutil.which("fpocket"):
        return None, "fpocket not on PATH"
    try:
        pockets = bm.fpocket_pockets_with_residues(receptor_pdb)
    except Exception as e:                                    # noqa: BLE001
        return None, "fpocket failed: %s: %s" % (type(e).__name__, e)
    pockets.sort(key=lambda p: (-(p.get("druggability") or 0), -(p.get("alpha_spheres") or 0)))
    return pockets, None


# ==================================================================================================
# ORCHESTRATION
# ==================================================================================================

def _chain_nearest(pdb_text, points, cutoff=6.0):
    """The protein chain with the most heavy atoms near `points` — the chain the ligand actually binds."""
    c2 = cutoff * cutoff
    counts = {}
    for line in pdb_text.splitlines():
        if line.startswith("ENDMDL"):
            break
        if not line.startswith("ATOM"):
            continue
        try:
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
        except ValueError:
            continue
        for (px, py, pz) in points:
            if (x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2 <= c2:
                counts[line[21]] = counts.get(line[21], 0) + 1
                break
    return max(counts, key=lambda c: counts[c]) if counts else None


def _write(path, text):
    with open(path, "w") as fh:
        fh.write(text)
    return path


def _read(path):
    with open(path, errors="replace") as fh:
        return fh.read()


def _contact_a():
    import inspect
    import nr4a3_warhead as wh
    return float(inspect.signature(wh.handle_contacts).parameters["cutoff"].default)


def _heavy_coords(mol):
    conf = mol.GetConformer()
    return [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
            for i, a in enumerate(mol.GetAtoms()) if a.GetAtomicNum() > 1]


def _transform_mol(mol, R, t):
    import nr4a3_8xtt_benchmark as bm
    from rdkit import Chem
    from rdkit.Geometry import Point3D
    out = Chem.Mol(mol)
    conf = out.GetConformer()
    pts = [(conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, conf.GetAtomPosition(i).z)
           for i in range(out.GetNumAtoms())]
    for i, (x, y, z) in enumerate(bm.apply_transform(pts, R, t)):
        conf.SetAtomPosition(i, Point3D(x, y, z))
    return out


def _top_pose(sdf_path, label):
    from rdkit import Chem
    if not os.path.exists(sdf_path):
        return None, "no pose file at %s" % sdf_path
    for m in Chem.SDMolSupplier(sdf_path, removeHs=True, sanitize=True):
        if m is not None:
            return m, None
    return None, "pose file %s held no readable molecule" % os.path.basename(sdf_path)


def run_benchmark(cand, work, af2_reference_pdb):
    """The whole known-answer test for ONE apo/holo pair. Returns a result dict (never raises)."""
    import nr4a3_8xtt_benchmark as bm
    import nr4a3_dock as ndock
    from rdkit.Chem import rdMolAlign
    os.makedirs(work, exist_ok=True)
    cutoff = _contact_a()
    R_ = {"candidate": cand, "refusals": [], "params": pipeline_dock_params(), "contact_A": cutoff,
          "criterion": {"recovered_rmsd_A": RECOVER_RMSD_A, "partial_rmsd_A": PARTIAL_RMSD_A,
                        "fnat_success": FNAT_SUCCESS, "n_null": N_NULL,
                        "null_power_max": NULL_POWER_MAX}}

    deadline = time.time() + PAIR_BUDGET_S

    def refuse(stage, why):
        R_["refusals"].append({"stage": stage, "evidence": why})
        return R_

    def out_of_time(stage):
        if time.time() > deadline:
            R_["refusals"].append({"stage": stage, "evidence":
                                   "pair exceeded its %ds budget; the arms after this point are UNRUN, "
                                   "not failed" % PAIR_BUDGET_S})
            return True
        return False

    # 1) structures
    try:
        apo_txt = _read(fetch_pdb(cand["apo"], os.path.join(work, cand["apo"] + ".pdb")))
        holo_txt = _read(fetch_pdb(cand["holo"], os.path.join(work, cand["holo"] + ".pdb")))
    except Exception as e:                                    # noqa: BLE001
        return refuse("fetch", "%s: %s" % (type(e).__name__, e))

    # 2) the crystallographic answer
    comp = (cand["ligand"] or {}).get("comp_id")
    links = covalent_links(holo_txt, comp)
    R_["covalent_links"] = links
    if links:
        R_["excluded_by"] = "R2b"
        return refuse("R2b", "%s is COVALENTLY linked in %s (%d LINK record(s)); a non-covalent dock "
                             "cannot reproduce a covalent pose. First: %s"
                             % (comp, cand["holo"], len(links), links[0][:80]))
    lines, key = ligand_hetatms(holo_txt, comp)
    if not lines:
        return refuse("crystal_ligand", "no HETATM copy of %s in %s" % (comp, cand["holo"]))
    xtal_pts = het_coords(lines)
    xtal, why = crystal_mol(lines, (cand["ligand"] or {}).get("smiles"))
    if xtal is None:
        return refuse("crystal_ligand", why)
    R_["crystal"] = {"comp_id": comp, "copy": "chain %s resseq %s" % key, "n_heavy": len(xtal_pts)}
    flag, ev = engineered_flag(cand.get("apo_title"), cand.get("holo_title"))
    R_["engineered_construct"] = {"declared_in_title": flag, "evidence": ev,
                                  "_note": "reported, never filtered — a mutant designed to create or "
                                           "probe a pocket is not the wild-type site the pipeline targets, "
                                           "and a reader must be able to see that from the artifact"}

    # 3) receptors — the holo chain the ligand actually touches, and the apo's largest chain
    holo_chain = _chain_nearest(holo_txt, xtal_pts)
    holo_rec = _write(os.path.join(work, "holo_rec.pdb"), protein_only(holo_txt, holo_chain))
    apo_rec = _write(os.path.join(work, "apo_rec.pdb"), protein_only(apo_txt))
    try:
        _hc, holo_resnums, holo_seq, holo_ca = bm.chain_ca(_read(holo_rec))
        _ac, apo_resnums, apo_seq, apo_ca = bm.chain_ca(_read(apo_rec))
    except Exception as e:                                    # noqa: BLE001
        return refuse("receptor", "chain_ca failed: %s" % e)

    # 4) R4 — apo and holo must be the same protein, measured not assumed
    try:
        apo_to_holo, ident = bm.map_uniprot_to_pdb(apo_seq, apo_resnums, holo_seq, holo_resnums)
    except Exception as e:                                    # noqa: BLE001
        return refuse("alignment", "apo<->holo alignment failed: %s" % e)
    R_["apo_holo_alignment"] = {"identity": round(ident, 4), "n_mapped": len(apo_to_holo)}
    if ident < 0.95:
        return refuse("R4", "apo<->holo sequence identity %.3f < 0.95" % ident)

    # 5) native contacts + the induced fit, measured (R9)
    native = sorted(residues_near(_read(holo_rec), xtal_pts, cutoff))
    R_["native_contact_residues_holo"] = native
    site_apo = [a for a, h in apo_to_holo.items() if h in set(native)]
    try:
        fit = bm.superpose_and_score(apo_ca, {a: holo_ca[h] for a, h in apo_to_holo.items() if h in holo_ca},
                                     list(apo_to_holo.keys()), site_apo, [])
        R_["induced_fit"] = {"global_ca_rmsd_A": round(fit["global_rmsd"], 3),
                             "site_ca_rmsd_A": round(fit["pocket_rmsd"], 3) if fit["pocket_rmsd"] else None,
                             "n_fit": fit["n_fit"], "n_site": fit["n_pocket"],
                             "_note": "apo->holo Ca movement at the ligand site. This is the size of the "
                                      "problem the cross-dock has to solve; it is measured, not assumed."}
    except Exception as e:                                    # noqa: BLE001
        R_["refusals"].append({"stage": "induced_fit", "evidence": str(e)})

    # the evaluation transform: apo frame -> holo frame, fitted on the site Ca (standard practice; it
    # gives the docking no information, because the docking has already happened by the time it is used)
    try:
        common = [a for a in site_apo if a in apo_ca and apo_to_holo[a] in holo_ca]
        Rm, tm = bm.kabsch_transform([apo_ca[a] for a in common],
                                     [holo_ca[apo_to_holo[a]] for a in common])
        R_["evaluation_frame"] = {"fitted_on": "site Ca", "n": len(common)}
    except Exception as e:                                    # noqa: BLE001
        return refuse("evaluation_frame", "site superposition failed: %s" % e)

    # 6) the ligand, prepared exactly as the pipeline prepares one
    sdf = os.path.join(work, "bench_ligand.sdf")
    kept = ndock.make_sdf([(comp, comp, (cand["ligand"] or {}).get("smiles"))], sdf)
    if not kept:
        return refuse("ligand_prep", "RDKit could not build a 3D conformer of %s" % comp)

    # 7) boxes
    boxes = {}
    c, det = pipeline_box(apo_rec, af2_reference_pdb, work)
    boxes["pipeline_apo"] = {"center": c, "detail": det} if c else {"center": None, "why": det}
    ch, deth = pipeline_box(holo_rec, af2_reference_pdb, work)
    boxes["pipeline_holo"] = {"center": ch, "detail": deth} if ch else {"center": None, "why": deth}
    pockets, pwhy = fpocket_boxes(apo_rec)
    if pockets:
        import nr4a3_warhead as wh
        top = pockets[0]
        try:
            tc, _n = wh.pocket_box(apo_rec, top["residues"])
        except Exception as e:                                # noqa: BLE001
            tc = None
            pwhy = "pocket_box on the top fpocket pocket failed: %s" % e
        boxes["fpocket_top_apo"] = {"center": tc, "druggability": top.get("druggability"),
                                    "pocket": top.get("pocket"), "n_pockets": len(pockets)}
        # pocket DETECTION diagnostic: where does the native site rank among the apo's own pockets?
        site_apo_set = set(site_apo)
        ranks = [(i + 1, p) for i, p in enumerate(pockets) if site_apo_set & set(p["residues"])]
        # ⛔ THE DISCRIMINATING OBSERVATION for a pipeline-box failure, and it is free. If the transferred
        # site is itself a well-ranked cavity that simply does not hold THIS ligand, the pipeline looked in
        # a real pocket and the crystal ligand is elsewhere. If it is no cavity at all, the transfer is
        # broken. Those have opposite meanings and must never be reported as one "it failed".
        pl = set((boxes.get("pipeline_apo", {}).get("detail") or {}).get("mapped_residues") or [])
        pranks = [(i + 1, p) for i, p in enumerate(pockets) if pl & set(p["residues"])]
        boxes["pipeline_box_fpocket_rank"] = (
            {"rank_by_druggability": pranks[0][0], "druggability": pranks[0][1].get("druggability"),
             "n_shared_residues": len(pl & set(pranks[0][1]["residues"])),
             "_reads": "the site the pipeline's Pocket-5 transfer selected IS a cavity on this receptor; "
                       "if the primary arm still missed, the crystal ligand is not in it"}
            if pranks else
            {"rank_by_druggability": None,
             "_reads": "the site the pipeline's Pocket-5 transfer selected is not a cavity fpocket finds "
                       "on this receptor at all"})
        boxes["native_site_fpocket_rank"] = (
            {"rank_by_druggability": ranks[0][0], "druggability": ranks[0][1].get("druggability"),
             "n_shared_residues": len(site_apo_set & set(ranks[0][1]["residues"]))}
            if ranks else {"rank_by_druggability": None,
                           "_note": "no fpocket pocket on the APO receptor touches the native ligand site"})
    else:
        boxes["fpocket_top_apo"] = {"center": None, "why": pwhy}
    R_["boxes"] = boxes
    size = tuple(float(R_["params"].get(k, 24)) for k in ("size_x", "size_y", "size_z"))

    def score_pose(mol_in_apo_frame, transform=True):
        m = _transform_mol(mol_in_apo_frame, Rm, tm) if transform else mol_in_apo_frame
        try:
            rms = round(float(rdMolAlign.CalcRMS(m, xtal)), 3)
        except Exception as e:                                # noqa: BLE001
            return {"rmsd_A": None, "why": "%s: %s" % (type(e).__name__, e)}
        got = residues_near(_read(holo_rec), _heavy_coords(m), cutoff)
        nat = set(native)
        return {"rmsd_A": rms,
                "fnat": round(len(got & nat) / len(nat), 3) if nat else None,
                "n_native_contacts": len(nat), "n_recovered": len(got & nat),
                "centroid_distance_A": round(math.dist(centroid(_heavy_coords(m)), centroid(xtal_pts)), 3),
                "verdict": ("RECOVERED" if rms <= RECOVER_RMSD_A else
                            "PARTIAL" if rms <= PARTIAL_RMSD_A else "NOT RECOVERED")}

    # 8) PRIMARY — blind cross-dock from the apo receptor, pipeline box, pipeline settings
    arms = {}
    if boxes["pipeline_apo"].get("center"):
        _s, out_sdf = dock(apo_rec, boxes["pipeline_apo"]["center"], sdf, "apo_pipeline", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["PRIMARY_blind_apo_pipeline_box"] = (score_pose(mol) if mol else {"rmsd_A": None, "why": why})
    else:
        arms["PRIMARY_blind_apo_pipeline_box"] = {"rmsd_A": None,
                                                  "why": boxes["pipeline_apo"].get("why")}
    # 9) secondary blind arm — fully agnostic site choice
    if not out_of_time("blind_apo_fpocket_top_box") and boxes.get("fpocket_top_apo", {}).get("center"):
        _s, out_sdf = dock(apo_rec, boxes["fpocket_top_apo"]["center"], sdf, "apo_fpocket", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["blind_apo_fpocket_top_box"] = (score_pose(mol) if mol else {"rmsd_A": None, "why": why})
    # 10) C3 ORACLE — decomposition only, never the headline
    #     centre the box on the crystallographic ligand, still docking into the APO receptor.
    oracle_center_holo = centroid(xtal_pts)
    try:
        Ri, ti = bm.kabsch_transform([holo_ca[apo_to_holo[a]] for a in common], [apo_ca[a] for a in common])
        oracle_center_apo = bm.apply_transform([oracle_center_holo], Ri, ti)[0]
        _s, out_sdf = dock(apo_rec, oracle_center_apo, sdf, "apo_oracle", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["C3_oracle_box_apo"] = (score_pose(mol) if mol else {"rmsd_A": None, "why": why})
    except Exception as e:                                    # noqa: BLE001
        arms["C3_oracle_box_apo"] = {"rmsd_A": None, "why": "oracle box failed: %s" % e}
    # 11) C1 SELF-DOCK into the holo receptor (same frame as the crystal — no transform).
    #     ★ ONE CONTROL PER BLIND ARM. A single C1 on the pipeline box cannot interpret the fpocket arm:
    #     if the pipeline's transferred site is simply not where this ligand binds, its C1 fails for a
    #     reason that says nothing about whether the DOCKING works. So each blind arm gets a self-dock
    #     through its own site-selection route, and each is then judged against its own control.
    if boxes["pipeline_holo"].get("center"):
        _s, out_sdf = dock(holo_rec, boxes["pipeline_holo"]["center"], sdf, "holo_self", work)
        mol, why = _top_pose(out_sdf, comp)
        arms["C1_self_dock_holo"] = (score_pose(mol, transform=False) if mol
                                     else {"rmsd_A": None, "why": why})
    else:
        arms["C1_self_dock_holo"] = {"rmsd_A": None, "why": boxes["pipeline_holo"].get("why")}
    hp, hwhy = (None, "pair budget spent") if out_of_time("C1_self_dock_holo_fpocket") \
        else fpocket_boxes(holo_rec)
    if hp:
        import nr4a3_warhead as _wh
        try:
            hc, _n = _wh.pocket_box(holo_rec, hp[0]["residues"])
            _s, out_sdf = dock(holo_rec, hc, sdf, "holo_self_fpocket", work)
            mol, why = _top_pose(out_sdf, comp)
            arms["C1_self_dock_holo_fpocket"] = (score_pose(mol, transform=False) if mol
                                                 else {"rmsd_A": None, "why": why})
            boxes["fpocket_top_holo"] = {"center": hc, "druggability": hp[0].get("druggability")}
        except Exception as e:                                # noqa: BLE001
            arms["C1_self_dock_holo_fpocket"] = {"rmsd_A": None, "why": "fpocket self-dock failed: %s" % e}
    else:
        arms["C1_self_dock_holo_fpocket"] = {"rmsd_A": None, "why": hwhy}
    R_["arms"] = arms

    # 12) C2 power
    R_["C2_random_in_box_null"] = random_in_box_null(xtal, oracle_center_holo, size)
    R_["verdict"] = verdict(R_)
    return R_


def verdict(res):
    """The pre-registered decision, applied mechanically to what was measured."""
    arms = res.get("arms") or {}
    primary = arms.get("PRIMARY_blind_apo_pipeline_box") or {}
    c1 = arms.get("C1_self_dock_holo") or {}
    null = res.get("C2_random_in_box_null") or {}
    p_rms, c1_rms = primary.get("rmsd_A"), c1.get("rmsd_A")
    p_null = null.get("p_within_criterion")

    if p_rms is None:
        return {"outcome": "INCONCLUSIVE", "reason": "the primary arm produced no pose",
                "detail": primary.get("why")}
    if c1_rms is None:
        return {"outcome": "INCONCLUSIVE",
                "reason": "C1 self-dock produced no pose, so a primary failure cannot be attributed",
                "detail": c1.get("why"), "primary_rmsd_A": p_rms}
    if c1_rms > RECOVER_RMSD_A:
        fp = arms.get("blind_apo_fpocket_top_box") or {}
        fp_c1 = arms.get("C1_self_dock_holo_fpocket") or {}
        return {"outcome": "INCONCLUSIVE",
                "blind_arms_each_against_its_own_control": {
                    "pipeline_site_transfer": {
                        "blind_apo_rmsd_A": p_rms, "own_control_rmsd_A": c1_rms,
                        "control_passed": False,
                        "_reads": "the protocol cannot recover this ligand even from the receptor it was "
                                  "solved in, THROUGH THIS SITE — so this arm is measuring the site, not "
                                  "the docking"},
                    "fpocket_top_pocket": {
                        "blind_apo_rmsd_A": fp.get("rmsd_A"), "own_control_rmsd_A": fp_c1.get("rmsd_A"),
                        "control_passed": (fp_c1.get("rmsd_A") is not None
                                           and fp_c1["rmsd_A"] <= RECOVER_RMSD_A),
                        "blind_apo_fnat": fp.get("fnat")}},
                "reason": "C1 FAILED: the protocol could not recover the pose even from the HOLO receptor "
                          "(%.2f A > %.2f A), so the primary result measures the docking protocol, not the "
                          "apo->holo induced-fit gap. Pre-registered: this outcome is INCONCLUSIVE, not a "
                          "failure of the apo pipeline." % (c1_rms, RECOVER_RMSD_A),
                "primary_rmsd_A": p_rms, "c1_rmsd_A": c1_rms}
    if p_null is not None and p_null > NULL_POWER_MAX:
        return {"outcome": "INCONCLUSIVE",
                "reason": "C2 FAILED: a random placement in the same box clears %.2f A with probability "
                          "%.3f > %.3f, so the criterion has no power here."
                          % (RECOVER_RMSD_A, p_null, NULL_POWER_MAX),
                "primary_rmsd_A": p_rms}

    band = primary.get("verdict")
    # ★ EACH BLIND ARM AGAINST ITS OWN CONTROL. The primary endpoint is unchanged and stays the pipeline
    # box — moving it after seeing a number would be the tuning this module forbids. But a single verdict
    # line cannot say what the run actually found when one arm's SITE is wrong and another's is right, so
    # every blind arm is also reported beside the self-dock that goes through the same site-selection route.
    fp = arms.get("blind_apo_fpocket_top_box") or {}
    fp_c1 = arms.get("C1_self_dock_holo_fpocket") or {}
    out_arms = {
        "pipeline_site_transfer": {
            "blind_apo_rmsd_A": p_rms, "own_control_rmsd_A": c1_rms,
            "control_passed": c1_rms is not None and c1_rms <= RECOVER_RMSD_A,
            "_site": "NR4A3 Pocket-5 carried across by the pipeline's own paralogue transfer"},
        "fpocket_top_pocket": {
            "blind_apo_rmsd_A": fp.get("rmsd_A"), "own_control_rmsd_A": fp_c1.get("rmsd_A"),
            "control_passed": (fp_c1.get("rmsd_A") is not None
                               and fp_c1["rmsd_A"] <= RECOVER_RMSD_A),
            "blind_apo_fnat": fp.get("fnat"),
            "_site": "the highest-druggability fpocket pocket on the receptor, no NR4A3 information used"},
    }
    out = {"outcome": "RECOVERED" if band == "RECOVERED" else "NOT RECOVERED",
           "blind_arms_each_against_its_own_control": out_arms,
           "band": band, "primary_rmsd_A": p_rms, "primary_fnat": primary.get("fnat"),
           "c1_self_dock_rmsd_A": c1_rms, "null_p_within_criterion": p_null,
           "oracle_rmsd_A": (arms.get("C3_oracle_box_apo") or {}).get("rmsd_A"),
           "fpocket_top_rmsd_A": (arms.get("blind_apo_fpocket_top_box") or {}).get("rmsd_A")}
    if out["outcome"] == "RECOVERED":
        out["sentence"] = (
            "KNOWN-ANSWER RECOVERED: docking into the APO receptor with the pipeline's own site transfer "
            "and smina settings put the ligand %.2f A from the crystallographic pose (criterion <= %.2f A), "
            "recovering %s of the native contacts. The protocol control passed (%.2f A) and a random "
            "placement in the same box clears the criterion with probability %s. This is ONE case: it "
            "removes a specific reason to disbelieve the NR4A3 pose and makes no claim that it is correct."
            % (p_rms, RECOVER_RMSD_A, primary.get("fnat"), c1_rms, p_null))
    else:
        # name which stage failed, using the decomposition — never leave it as a bare number
        oracle = out["oracle_rmsd_A"]
        if oracle is not None and oracle <= RECOVER_RMSD_A:
            stage = ("SITE TRANSFER. Handed the correct site (C3 oracle box) the same docking recovers the "
                     "pose at %.2f A, so what failed is the step that decides WHERE to dock — the same "
                     "sequence transfer of NR4A3's Pocket-5 that boxes 8XTT and the paralogues." % oracle)
        else:
            stage = ("POSE PLACEMENT. Even handed the correct site (C3 oracle box: %s A) the docking does "
                     "not reproduce the crystallographic pose, so the failure is in the search/scoring, "
                     "not in site selection." % oracle)
        out["failing_stage"] = stage
        out["sentence"] = (
            "KNOWN-ANSWER NOT RECOVERED: the pipeline placed the ligand %.2f A from the crystallographic "
            "pose (criterion <= %.2f A; %s band), recovering %s of the native contacts, while the protocol "
            "control passed at %.2f A and the criterion had power (random p=%s). Failing stage: %s "
            "This does not prove the NR4A3 denovo_401 pose wrong. It removes the presumption that it is "
            "right: the pipeline that produced it has now been asked to recover a pose that is known, in a "
            "comparable apo/induced-fit regime, and did not."
            % (p_rms, RECOVER_RMSD_A, band, primary.get("fnat"), c1_rms, p_null, stage))
    return out


# ==================================================================================================
# MODES
# ==================================================================================================

def mode_source():
    """Real RCSB queries -> the full considered set, apo/holo classified, nothing assumed."""
    doc = {"_mode": "source", "_query": {"search": RCSB_SEARCH, "graphql": RCSB_GRAPHQL},
           "accessions_declared": [{"accession": a, "protein": n, "why": w} for a, n, w in NR_ACCESSIONS],
           "selection_rules": SELECTION_RULES, "refusals": [], "by_accession": {}}
    for acc, name, why in NR_ACCESSIONS:
        ids, err = entries_for_accession(acc)
        if ids is None:
            doc["refusals"].append({"accession": acc, "stage": "search", "evidence": err})
            continue
        details, derr = entry_details(ids)
        if derr:
            doc["refusals"].append({"accession": acc, "stage": "entry_details", "evidence": derr})
        entries = [classify_entry(e, acc) for e in details]
        doc["by_accession"][acc] = {
            "name": name, "why_considered": why, "n_entries": len(ids),
            "n_classified": len(entries),
            "n_apo": sum(1 for e in entries if e["apo"]),
            "n_holo": sum(1 for e in entries if e["ligands"]),
            "entries": entries,
        }
    return doc


def mode_select(src):
    ranked = pair_candidates(src.get("by_accession") or {})
    considered = [{"rank": i + 1, "score": list(s), **{k: v for k, v in c.items() if k != "ligand"},
                   "ligand": c["ligand"]} for i, (s, c) in enumerate(ranked[:40])]
    return {"n_pairs_found": len(ranked),
            # ⚠ THE PANEL POOL IS BUILT FROM THE FULL RANKED LIST, NOT FROM `considered_top`. That field is
            # a 40-row excerpt kept for the record, and building the panel from it silently capped the run
            # at four candidates — every one of them NR4A subfamily — so the panel could never reach a
            # nuclear receptor with a canonical orthosteric ligand complex. Measured on CI run 30762378689.
            "panel_pool": _dedup_pairs([c for _s, c in ranked]),
            "considered_top": considered,
            "chosen": ranked[0][1] if ranked else None,
            "selection_rules": SELECTION_RULES,
            "_finding_if_empty": ("No nuclear-receptor LBD in the declared list has BOTH an apo deposit "
                                  "and a drug-like holo deposit that pass the hard rules. That is the "
                                  "finding — no substitute benchmark is used.")}


def main():
    mode = os.environ.get("MODE", "run").strip().lower()
    # The AF2 reference is only needed to TRANSFER NR4A3's Pocket-5 onto the benchmark receptor. The repo
    # already carries the exact model the pipeline used, so the default reads that rather than re-fetching
    # a model that might have been re-predicted since.
    repo_af2 = os.path.join(HERE, "..", "..", "results", "nr4a3-metad-r2", "ckpt", "AF-Q92570.pdb")
    af2 = os.environ.get("AF2_REFERENCE_PDB") or (os.path.abspath(repo_af2)
                                                  if os.path.exists(repo_af2)
                                                  else os.path.join(WORK, "AF-Q92570.pdb"))
    os.makedirs(WORK, exist_ok=True)
    doc = {"_module": "apo_pose_recovery", "_mode": mode,
           "_preregistered_criterion": {
               "primary": "symmetry-corrected heavy-atom RMSD of the top smina pose from the APO receptor "
                          "to the crystallographic ligand, after site-Ca superposition",
               "recovered_A": RECOVER_RMSD_A, "partial_A": PARTIAL_RMSD_A,
               "secondary_fnat": FNAT_SUCCESS,
               "controls": ["C1 self-dock into holo (failure => INCONCLUSIVE)",
                            "C2 random-in-box null (no power => INCONCLUSIVE)",
                            "C3 oracle box (decomposition only, never the headline)"],
               "_frozen": "fixed in the module docstring before the first run; changes go to an appendix"},
           "selection_rules": SELECTION_RULES}
    src = mode_source()
    doc["sourcing"] = {k: v for k, v in src.items() if k != "by_accession"}
    doc["sourcing"]["census"] = {
        a: {"name": r["name"], "n_entries": r["n_entries"], "n_apo": r["n_apo"], "n_holo": r["n_holo"]}
        for a, r in (src.get("by_accession") or {}).items()}
    if mode == "source":
        doc["by_accession"] = src.get("by_accession")
        _emit(doc)
        return
    sel = mode_select(src)
    doc["selection"] = sel
    if mode == "select" or not sel["chosen"]:
        if not sel["chosen"]:
            doc["verdict"] = {"outcome": "NO SUITABLE BENCHMARK",
                              "reason": sel["_finding_if_empty"]}
        _emit(doc)
        return
    if not os.path.exists(af2):
        try:
            import nr4a3_8xtt_redock as rd
            rd._fetch_af2(af2)
        except Exception as e:                                # noqa: BLE001
            doc["verdict"] = {"outcome": "INCONCLUSIVE",
                              "reason": "the AF-Q92570 reference needed for the pipeline's own site "
                                        "transfer could not be fetched: %s" % e}
            _emit(doc)
            return
    # ⛔ A PANEL, NOT A PICK. Candidates are taken in the pre-registered rank order and every one that is
    # attempted is reported, including the ones R2b throws out. The PRIMARY verdict is the first pair that
    # actually runs; the rest are supporting cases. Nothing here can be re-ordered by its answer, because
    # the order is fixed by SELECTION_RULES before any structure is fetched.
    panel, attempted = [], 0
    panel_start = time.time()
    for pair in _panel_candidates(sel):
        attempted += 1
        if time.time() - panel_start > PANEL_BUDGET_S:
            panel.append({"candidate": pair, "refusals": [
                {"stage": "panel_budget",
                 "evidence": "the panel's %ds wall-clock budget was already spent when this pair came up; "
                             "it is UNRUN, not excluded" % PANEL_BUDGET_S}]})
            break
        t0 = time.time()
        res = run_benchmark(pair, os.path.join(WORK, "%s_%s" % (pair["apo"], pair["holo"])), af2)
        res["elapsed_s"] = round(time.time() - t0, 1)
        print("[apo-pose-recovery] %s -> %s (%s): %s in %.0fs"
              % (pair["apo"], pair["holo"], (pair.get("ligand") or {}).get("comp_id"),
                 (res.get("verdict") or {}).get("outcome")
                 or [r["stage"] for r in (res.get("refusals") or [])], res["elapsed_s"]), flush=True)
        panel.append(res)
        if attempted >= PANEL_SIZE:            # bounded: never grind the whole 5-figure candidate list
            break
    doc["panel"] = panel
    ran = [r for r in panel if r.get("verdict")]
    doc["result"] = ran[0] if ran else (panel[0] if panel else None)
    doc["verdict"] = (ran[0]["verdict"] if ran else
                      {"outcome": "INCONCLUSIVE",
                       "reason": "no candidate pair reached a scored arm",
                       "refusals": [r.get("refusals") for r in panel]})
    doc["verdict"]["panel_summary"] = {
            "n_pairs_scored": len(ran),
            "pairs": [{"apo": r["candidate"]["apo"], "holo": r["candidate"]["holo"],
                       "ligand": r["candidate"]["ligand"]["comp_id"],
                       "outcome": r["verdict"]["outcome"],
                       "primary_rmsd_A": r["verdict"].get("primary_rmsd_A")} for r in ran],
            "n_recovered": sum(1 for r in ran if r["verdict"]["outcome"] == "RECOVERED"),
        # ★ THE PANEL-LEVEL ANSWER APPLIES THE SAME PRE-REGISTERED C1 RULE ONE LEVEL UP: a pair whose
        # protocol control fails is uninterpretable, so the panel's answer is over the INTERPRETABLE pairs
        # and the count of uninterpretable ones is reported beside it rather than averaged in.
        "n_interpretable": sum(1 for r in ran
                               if (r["verdict"].get("c1_rmsd_A") is not None
                                   and r["verdict"]["c1_rmsd_A"] <= RECOVER_RMSD_A)),
        "n_uninterpretable_control_failed": sum(1 for r in ran
                                                if r["verdict"]["outcome"] == "INCONCLUSIVE"),
        "n_excluded_covalent_R2b": sum(1 for r in panel if r.get("excluded_by") == "R2b"),
            "_note": "the PRIMARY verdict is the rank-1 pair; these are supporting cases, reported "
                     "whatever they returned",
        }
    _emit(doc)


def _dedup_pairs(cands):
    """ONE PAIR PER DISTINCT HOLO, at most `MAX_PER_PROTEIN` per protein, in rank order.

    ⚠ THE HOLO RULE IS A BUG FIX, NOT A RE-TUNING. It was stated in this module before the first run —
    "three pairs sharing one crystal would be one known answer measured three times" — but the first
    implementation skipped a row only when BOTH its apo and its holo had been seen, so five different apo
    structures against the single holo 5Y41 all entered and the three that scored were three apo receptors
    against ONE crystal (4REF). The per-protein cap exists for the same reason one level up. Neither rule
    can be steered by an answer: both act on a rank order fixed by SELECTION_RULES before any fetch."""
    seen_holo, per_protein, out = set(), {}, []
    for r in cands:
        acc, holo = r.get("accession"), r.get("holo")
        if not r.get("apo") or not holo or holo in seen_holo:
            continue
        if per_protein.get(acc, 0) >= MAX_PER_PROTEIN:
            continue
        seen_holo.add(holo)
        per_protein[acc] = per_protein.get(acc, 0) + 1
        out.append({k: r[k] for k in ("accession", "protein", "apo", "holo", "ligand", "apo_method",
                                      "apo_models", "apo_resolution_A", "holo_resolution_A",
                                      "apo_title", "holo_title") if k in r})
        if len(out) >= PANEL_SIZE:
            break
    return out


def _panel_candidates(sel):
    """The pre-registered panel: the pool built in `mode_select`, or a de-dup of the excerpt as a fallback."""
    pool = sel.get("panel_pool")
    if pool:
        return pool
    rows = list(sel.get("considered_top") or [])
    if sel.get("chosen"):
        rows = [dict(sel["chosen"])] + rows
    return _dedup_pairs(rows)


def _emit(doc):
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=2)
    print(json.dumps({k: doc[k] for k in ("_mode", "verdict") if k in doc}, indent=2))
    print("[apo-pose-recovery] wrote %s" % OUT)


if __name__ == "__main__":
    main()
