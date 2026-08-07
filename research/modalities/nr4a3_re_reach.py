#!/usr/bin/env python3
"""
IS A RESPONSE-ELEMENT-BASED DEGRADER GEOMETRICALLY BUILDABLE? ($0, CPU/CI only, pure stdlib.)

THE IDEA. Every degrader route in this repository puts its target-side warhead in a POCKET on the NR4A3 LBD,
and every one of them inherits that pocket's problems — `V3` left the cryptic pocket INCONCLUSIVE, the
paralogue LBDs are 66-69 % identical, and there is no validated NR4A3 binder. A response-element-based
degrader declines that whole question: the target-side terminus binds the DNA the receptor sits on, and the
second terminus recruits an E3. The anchor is then a sequence, not a pocket, and NR4A3's own undruggability
stops being the blocker.

⛔ AND IT IMPORTS A DIFFERENT, LARGER PROBLEM, WHICH THIS MODULE DOES NOT SOLVE AND MUST NOT BE READ AS
   SOLVING. An NBRE-directed warhead is selective for a DNA SEQUENCE, and NR4A1, NR4A2 and wild-type NR4A3
   read the same NBRE. Sequence-directed DNA binders have their own genome-wide occupancy problem. Nothing
   below addresses either. This module answers ONE question, and it is a question of excluded volume.

THE ANCHOR, WHICH IS WHY THIS IS NEWLY DOABLE. `emc-unexplored-treatment-lanes.md` §4 names PDB 7WNH —
Nurr1 (NR4A2) bound to the NBRE, 3.1 A — as the structure that makes the geometry askable. This repository
already CITED it (`apo-pose-site-in-regime.json`, `r3-site-choice-audit.json`) as an apo reference and had
never had its coordinates on disk. They are fetched by `s4_lane_inputs_fetch.py` on a GitHub Actions runner,
because the dev sandbox's egress proxy 403s RCSB (CLAUDE.md §6).

⚠ IT IS NR4A2, NOT NR4A3, AND THAT IS STATED RATHER THAN GLOSSED. No NR4A3-on-DNA structure exists (NR4A3 has
  exactly one PDB entry — 8XTT, an apo NMR LBD). The NR4A DBDs are 86-94 % identical (Lopez-Garcia 2025's own
  BLAST figures: NOR1 DBD 94.2 % to Nurr1 DBD), and the DNA half of the excluded volume is a B-form duplex
  either way, so the geometry transfers better than most cross-paralogue substitutions in this repository —
  but it is a substitution, and every number here is a number about NR4A2-on-NBRE.

WHAT IS RUN, and every piece is machinery this repository already froze:
  * the excluded volume is `basin_geom.SquaredDistanceField` over the real heavy atoms of one NR4A2 monomer
    (DBD + hinge + LBD, residues 258-598), its NBRE duplex and its structural zincs;
  * the anchor set is not chosen — it is ENUMERATED. Every lattice point around the NBRE core that (a) a
    DNA-binding ligand's exit atom could occupy (within `ANCHOR_MAX_DNA_A` of DNA) and (b) clears the whole
    complex by the sampler's own `pose_min_clearance_A`, then classified by groove and deterministically
    thinned by farthest-point sampling so the anchors SPAN the site instead of clustering;
  * placements come from `nr4a3_basin_search.sample_placements` UNCHANGED, over the same six staged
    second-terminus bodies `nr4a3_tcip_reach.py` uses and the same linker ladder;
  * results are reported in `nr4a3-tcip-reach.json`'s own vocabulary — `shortest_linker_atoms`,
    `admits_at_the_12_atom_gate`, per-rung `acceptance_rate`, `body_free` shell fraction — so the two
    enumerations are directly comparable.

⛔⛔ THE CEILING, CARRIED VERBATIM IN SPIRIT FROM THE TCIP WORK BECAUSE IT IS THE SAME CEILING.
   "`admits` remains a gate that no tested body has failed, so a named effector admitting is not evidence of
   anything beyond excluded volume" (`nr4a3-tcip-reach.json`). ⇒ AN "ADMITS" ANSWER HERE IS AN ADMISSION OF
   VOLUME AND NOTHING ELSE. Reach can REFUTE a configuration; it cannot license one. It says nothing about
   binding, affinity, sequence selectivity, ternary-complex formation, ubiquitin transfer, degradation,
   cellular activity, efficacy, safety, a therapeutic window or clinical readiness.
   ★ SO THIS MODULE ALSO RUNS THE ABLATION THAT CAN COME BACK EITHER WAY (`★_naked_dna_ablation`): the same
   enumeration with the PROTEIN REMOVED. If naked DNA and the full complex admit equally, the protein is not
   constraining the geometry and the "admits" answer carries no information about this site in particular.

Outputs: nr4a3-re-reach.json (+ .md)
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                        # noqa: E402
import linker_design as LD                    # noqa: E402
import nr4a3_basin_search as BS               # noqa: E402  THE sampler — never reimplemented
import nr4a3_linker_design as NLD             # noqa: E402
import nr4a3_tcip_reach as T                  # noqa: E402  the registries, the ladder and the vocabulary

PDB_GZ = os.path.join(HERE, "_s4_lane_inputs", "7WNH.pdb.gz")
OUT = os.path.join(HERE, "nr4a3-re-reach.json")

PARAMS = BS.PARAMS
RISE = LD.RISE_PER_ATOM_A
LADDER = list(T.LADDER)                       # imported, never re-typed (rule 1)
GATE_ATOMS = PARAMS["linker_gate_atoms"]
MIN_CLEARANCE = PARAMS["pose_min_clearance_A"]

SEED = 20260807
ANCHOR_PITCH_A = 1.0
ANCHOR_MAX_DNA_A = 5.0        # an exit atom further than this from DNA is not on a DNA-bound ligand
N_ANCHORS_PER_CLASS = 4       # deterministically farthest-point-sampled WITHIN each groove class
BASE_EDGE_MAX_A = 6.0         # beyond this from a base edge, a point is not in a groove
GROOVE_CLASSES = ("minor", "major", "backbone_or_solvent")
NBRE_CONSENSUS = "AAAGGTCA"   # the NR4A monomeric response element; SEARCHED FOR in the coordinates, never
                              # assumed to be present — a run that cannot find it refuses rather than guesses

# Minor- vs major-groove base-edge atoms. Standard nucleic-acid geometry: which face of the base pair an
# atom presents. Used only to LABEL an anchor, never to accept or reject one.
MINOR_EDGE = {("DA", "N3"), ("DA", "C2"), ("DG", "N3"), ("DG", "N2"),
              ("DT", "O2"), ("DC", "O2")}
MAJOR_EDGE = {("DA", "N6"), ("DA", "N7"), ("DG", "O6"), ("DG", "N7"),
              ("DT", "O4"), ("DT", "C7"), ("DT", "C5M"), ("DC", "N4"), ("DC", "C5")}
DNA_RES = {"DA", "DC", "DG", "DT"}
NT1 = {"DA": "A", "DC": "C", "DG": "G", "DT": "T"}


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# 1 · THE BODY — measured out of the file, not declared
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def parse_pdb(path):
    atoms = []
    src = gzip.open(path, "rt") if path.endswith(".gz") else open(path)
    with src as fh:
        for line in fh:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            res = line[17:20].strip()
            if res == "HOH":
                continue
            name = line[12:16].strip()
            el = (line[76:78].strip() or name[:1]).upper()
            if el == "H":
                continue
            atoms.append({"chain": line[21], "resseq": int(line[22:26]), "res": res, "name": name,
                          "el": el, "xyz": (float(line[30:38]), float(line[38:46]), float(line[46:54])),
                          "hetatm": line.startswith("HETATM")})
    return atoms


def header(path):
    out = {}
    src = gzip.open(path, "rt") if path.endswith(".gz") else open(path)
    with src as fh:
        for line in fh:
            if line.startswith("ATOM"):
                break
            if line.startswith("TITLE"):
                out.setdefault("title", "")
                out["title"] += line[10:].rstrip()
            elif line.startswith("REMARK   2 RESOLUTION"):
                try:
                    out["resolution_A"] = float(line.split()[3])
                except (IndexError, ValueError):
                    pass
            elif line.startswith("EXPDTA"):
                out["method"] = line[10:].strip()
            elif line.startswith("DBREF"):
                f = line.split()
                if len(f) >= 9 and f[5] == "UNP":
                    out.setdefault("uniprot_by_chain", {})[f[2]] = f[6]
                    out.setdefault("uniprot_range_by_chain", {})[f[2]] = [int(f[3]), int(f[4])]
    return out


def chain_sequences(atoms):
    seqs = {}
    for a in atoms:
        if a["res"] in DNA_RES and a["name"] == "P" or (a["res"] in DNA_RES and a["name"] == "C1'"):
            pass
    per = {}
    for a in atoms:
        if a["res"] in DNA_RES:
            per.setdefault(a["chain"], {})[a["resseq"]] = NT1[a["res"]]
    for c, d in per.items():
        seqs[c] = "".join(d[k] for k in sorted(d)), sorted(d)
    return seqs


def revcomp(s):
    return "".join({"A": "T", "T": "A", "G": "C", "C": "G"}[c] for c in reversed(s))


def pick_biological_unit(atoms):
    """One NR4A2 monomer + the ONE DNA DUPLEX it sits on.

    ⛔ NOT 'chain A + chains E and F because the header lists them together'. 7WNH's asymmetric unit holds
    FOUR protein chains and EIGHT DNA chains, and the header's MOL_ID grouping says nothing about which goes
    with which. A body assembled from the wrong chains produces an excluded volume that looks entirely
    reasonable and is wrong — the silent-success class this repository keeps being bitten by
    (`nr4a3_effector_stage.py`'s BTB-dimer note is the same lesson).

    ⛔⛔ AND THE FIRST IMPLEMENTATION OF THIS FUNCTION *WAS* WRONG, WHICH IS WHY IT IS WRITTEN THIS WAY.
       It scored each protein chain by TOTAL DNA contact and took every DNA chain it touched. Measured:
       chain D touches FOUR DNA chains (H, I, N, O) at >= 5 atoms — its own duplex plus a crystal
       neighbour's — so the "biological unit" it returned was a monomer plus TWO duplexes, and the reach
       enumeration launched on it was quietly measuring the excluded volume of a lattice contact. Caught by
       `test_the_biological_unit_is_measured_from_contacts_not_read_off_the_header` asserting the DUPLEX
       COUNT, which no amount of reading the numbers would have caught: 4 chains looked as plausible as 2.
       ⇒ Duplexes are now identified FIRST, by mutual base pairing, and the unit is (protein chain, ONE
       duplex). A protein chain touching two duplexes is a lattice fact, not a stoichiometry.
    """
    prot = sorted({a["chain"] for a in atoms if a["res"] not in DNA_RES and not a["hetatm"]})
    dna = sorted({a["chain"] for a in atoms if a["res"] in DNA_RES})
    by_chain = {}
    for a in atoms:
        by_chain.setdefault(a["chain"], []).append(a["xyz"])

    # 1. group the DNA chains into duplexes by mutual C1'-C1' Watson-Crick pairing
    c1 = {}
    for a in atoms:
        if a["res"] in DNA_RES and a["name"] == "C1'":
            c1.setdefault(a["chain"], []).append(a["xyz"])
    pair_counts = {}
    for i, x in enumerate(dna):
        for y in dna[i + 1:]:
            n = sum(1 for p in c1.get(x, [])
                    if any(G.dist(p, q) <= 11.5 for q in c1.get(y, [])))
            if n:
                pair_counts[(x, y)] = n
    duplexes, used = [], set()
    for (x, y), n in sorted(pair_counts.items(), key=lambda kv: -kv[1]):
        if x in used or y in used or n < 5:
            continue
        duplexes.append(([x, y], n))
        used.update((x, y))

    # 2. protein-DNA heavy-atom contacts, per (protein chain, duplex)
    contacts = {}
    for p in prot:
        f = G.SquaredDistanceField(by_chain[p], cell=1.2, clamp=8.0)
        for d in dna:
            n = sum(1 for x in by_chain[d] if f.min_dist(x) - f.cell_slack <= 4.5)
            if n:
                contacts["%s-%s" % (p, d)] = n

    best, best_p, best_dx = -1, None, None
    for p in prot:
        for chains, _n in duplexes:
            tot = sum(contacts.get("%s-%s" % (p, d), 0) for d in chains)
            if tot > best:
                best, best_p, best_dx = tot, p, sorted(chains)
    other = sorted(d for d in dna
                   if contacts.get("%s-%s" % (best_p, d), 0) >= 5 and d not in (best_dx or []))
    zn = sorted({a["chain"] for a in atoms if a["res"] == "ZN"})
    return {"protein_chain": best_p, "dna_chains": best_dx,
            "n_duplexes_in_asymmetric_unit": len(duplexes),
            "duplex_pairings_by_C1prime": {"%s:%s" % (a, b): n for (a, b), n in sorted(pair_counts.items())},
            "protein_dna_contact_atoms_by_pair": contacts,
            "n_contact_atoms_to_chosen_duplex": best,
            "⚠_other_duplex_chains_this_protein_chain_also_touches": other,
            "⚠_why_those_are_excluded": (
                "a protein chain touching a SECOND duplex is a crystal-lattice contact, not stoichiometry. "
                "Including them inflates the excluded volume with a neighbour that does not exist in "
                "solution — and the first version of this function did exactly that."),
            "zinc_chains_in_file": zn,
            "_method": ("DNA chains grouped into duplexes by mutual C1'-C1' pairing (<= 11.5 A), then the "
                        "(protein chain, duplex) pair with the most protein-DNA heavy-atom contacts at "
                        "4.5 A. Nothing is read off the header.")}


def locate_nbre(atoms, dna_chains):
    """Where is the response element? FOUND in the deposited sequence, on either strand, or the run refuses.

    Returns the nucleotide (chain, resseq) set of the octamer and its base-paired partners, the partners
    being those nucleotides whose C1' sits within `PAIR_C1_A` of a core nucleotide's C1' on the other strand.
    """
    PAIR_C1_A = 11.5                                    # B-form Watson-Crick C1'-C1' is ~10.5 A
    seqs = chain_sequences(atoms)
    missing = [c for c in dna_chains if c not in seqs]
    if missing:
        raise SystemExit("chain(s) %s carry no nucleotides in the atoms given — REFUSING to locate a "
                         "response element in a structure that does not contain the DNA" % missing)
    hit = None
    for c in dna_chains:
        s, nums = seqs[c]
        for target, strand in ((NBRE_CONSENSUS, "+"), (revcomp(NBRE_CONSENSUS), "-")):
            i = s.find(target)
            if i >= 0:
                hit = {"chain": c, "start_resseq": nums[i], "resseqs": nums[i:i + len(target)],
                       "matched": target, "strand_relative_to_consensus": strand,
                       "chain_sequence": s}
                break
        if hit:
            break
    if hit is None:
        raise SystemExit("NBRE consensus %s not found on either strand of %s — REFUSING to place an anchor "
                         "on a response element this structure does not contain" % (NBRE_CONSENSUS, dna_chains))
    c1 = {}
    for a in atoms:
        if a["res"] in DNA_RES and a["name"] == "C1'" and a["chain"] in dna_chains:
            c1[(a["chain"], a["resseq"])] = a["xyz"]
    core = {(hit["chain"], r) for r in hit["resseqs"]}
    partners = set()
    for (ch, rs), p in c1.items():
        if ch == hit["chain"]:
            continue
        for (kc, kr) in core:
            if G.dist(p, c1[(kc, kr)]) <= PAIR_C1_A:
                partners.add((ch, rs))
                break
    hit["core_nucleotides"] = sorted(core)
    hit["paired_partner_nucleotides"] = sorted(partners)
    hit["n_core_nucleotides"] = len(core) + len(partners)
    return hit


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# 2 · THE ANCHOR SET — enumerated, classified, thinned
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def enumerate_anchors(atoms, unit, nbre, field_all):
    core = set(nbre["core_nucleotides"]) | set(nbre["paired_partner_nucleotides"])
    core_atoms = [a for a in atoms if (a["chain"], a["resseq"]) in core]
    core_xyz = [a["xyz"] for a in core_atoms]
    dna_xyz = [a["xyz"] for a in atoms if a["res"] in DNA_RES and a["chain"] in unit["dna_chains"]]
    f_core = G.SquaredDistanceField(core_xyz, cell=0.9, clamp=8.0)
    f_dna = G.SquaredDistanceField(dna_xyz, cell=0.9, clamp=8.0)

    lo = [min(p[i] for p in core_xyz) - ANCHOR_MAX_DNA_A - 1 for i in range(3)]
    hi = [max(p[i] for p in core_xyz) + ANCHOR_MAX_DNA_A + 1 for i in range(3)]
    cand = []
    n_grid = 0
    x = lo[0]
    while x <= hi[0]:
        y = lo[1]
        while y <= hi[1]:
            z = lo[2]
            while z <= hi[2]:
                p = (x, y, z)
                n_grid += 1
                dcore = f_core.min_dist(p) - f_core.cell_slack
                if dcore <= ANCHOR_MAX_DNA_A and field_all.min_dist(p) - field_all.cell_slack >= MIN_CLEARANCE:
                    cand.append((p, dcore, f_dna.min_dist(p) - f_dna.cell_slack))
                z += ANCHOR_PITCH_A
            y += ANCHOR_PITCH_A
        x += ANCHOR_PITCH_A

    # groove labelling — nearest BASE-EDGE atom of a core nucleotide
    edges = []
    for a in core_atoms:
        key = (a["res"], a["name"])
        if key in MINOR_EDGE:
            edges.append((a["xyz"], "minor"))
        elif key in MAJOR_EDGE:
            edges.append((a["xyz"], "major"))
    labelled = []
    for p, dcore, ddna in cand:
        best, lab = 1e9, "backbone_or_solvent"
        for q, g in edges:
            dd = G.dist(p, q)
            if dd < best:
                best, lab = dd, g
        labelled.append({"xyz": [round(v, 3) for v in p], "clearance_A": round(dcore, 3),
                         "dist_to_dna_A": round(ddna, 3),
                         "groove": lab if best <= BASE_EDGE_MAX_A else "backbone_or_solvent",
                         "dist_to_nearest_base_edge_A": round(best, 3)})

    counts = {}
    for a in labelled:
        counts[a["groove"]] = counts.get(a["groove"], 0) + 1

    # ⛔⛔ STRATIFIED BY GROOVE, AND THE FIRST VERSION WAS NOT — WHICH INVALIDATED ITS OWN CONTROL.
    #    It farthest-point-sampled 6 anchors from the whole admissible cloud. Farthest-point sampling
    #    maximises SPREAD, so it selects the OUTERMOST points of the cloud, and the cloud's outer surface is
    #    bulk solvent. Measured on the 2026-08-07 CI run: all 6 chosen anchors came back
    #    `backbone_or_solvent`, 8.3-12.4 A from the nearest base edge — i.e. beside the duplex, not in it.
    #    That is not where a DNA-binding ligand's exit atom sits, and it is exactly why that run's
    #    naked-DNA ablation came back at 1.03-1.04x for two of six bodies: with the anchor already out in
    #    solvent, deleting the receptor barely changes what fits. The weak control was DIAGNOSTIC of the
    #    anchor selection, not of the geometry.
    #    ⇒ Anchors are now drawn PER GROOVE CLASS. The minor and major grooves are where a real
    #    sequence-directed binder (polyamide-class, or the major-groove face NR4A2 itself reads) would put
    #    its exit vector; `backbone_or_solvent` is retained as a DECLARED CONTROL, not as the headline.
    chosen, by_class = [], {}
    for cls in GROOVE_CLASSES:
        pool = [a for a in labelled if a["groove"] == cls]
        pts = [tuple(a["xyz"]) for a in pool]
        idx = G.farthest_point_sample(pts, min(N_ANCHORS_PER_CLASS, len(pts))) if pts else []
        by_class[cls] = {"n_available": len(pool), "n_used": len(idx)}
        for k, i in enumerate(idx):
            rec = dict(pool[i])
            rec["anchor_id"] = "%s_%d" % (cls[:3], k)
            rec["groove_class"] = cls
            chosen.append(rec)
    return {
        "_method": ("every %.1f A lattice point within %.1f A of an NBRE-core heavy atom that also clears "
                    "the WHOLE complex by the sampler's own pose_min_clearance_A (%.2f A). Nothing is "
                    "hand-placed."
                    % (ANCHOR_PITCH_A, ANCHOR_MAX_DNA_A, MIN_CLEARANCE)),
        "n_grid_points_scanned": n_grid,
        "n_admissible_anchor_positions": len(labelled),
        "by_groove": counts,
        "groove_labelling": ("nearest base-edge atom of an NBRE-core nucleotide, within %.1f A; standard "
                             "minor-edge (A N3/C2, G N3/N2, T O2, C O2) and major-edge (A N6/N7, G O6/N7, "
                             "T O4/C7, C N4/C5) atom sets" % BASE_EDGE_MAX_A),
        "n_anchors_used": len(chosen),
        "anchors_per_class": by_class,
        "_thinning": ("farthest-point sampling (basin_geom.farthest_point_sample) WITHIN each groove class "
                      "— deterministic, and stratified so the selection cannot drift into bulk solvent"),
        "⛔_backbone_or_solvent_is_a_control": (
            "those anchors sit beside the duplex rather than in a groove. They are reported so the groove "
            "classes can be read against something, and they are NOT where a sequence-directed warhead's "
            "exit vector would be."),
        "anchors": chosen,
    }


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
# 3 · THE ENUMERATION
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════
def body_free_envelope(a, field, ladder=None, pitch=1.0):
    """Identical predicate to `nr4a3_tcip_reach.body_free_envelope`, evaluated on this target's field."""
    ladder = ladder or LADDER
    slack = field.cell_slack
    lo = G.contour_length_from_atoms(PARAMS["linker_min_atoms"], RISE)
    hi_max = G.contour_length_from_atoms(max(ladder), RISE)
    steps = int(math.floor(hi_max / pitch))
    pts = []
    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            for k in range(-steps, steps + 1):
                dx, dy, dz = i * pitch, j * pitch, k * pitch
                d2 = dx * dx + dy * dy + dz * dz
                if d2 > hi_max * hi_max or d2 < lo * lo:
                    continue
                p = (a[0] + dx, a[1] + dy, a[2] + dz)
                pts.append((math.sqrt(d2), field.min_dist(p) - slack >= MIN_CLEARANCE))
    out = {}
    for n in ladder:
        hi = G.contour_length_from_atoms(n, RISE)
        inside = [ok for d, ok in pts if d <= hi]
        out[str(n)] = {"shell_hi_A": round(hi, 2), "n_grid_points": len(inside),
                       "n_admissible": sum(1 for o in inside if o),
                       "fraction_admissible": round(sum(1 for o in inside if o) / len(inside), 5)
                       if inside else None}
    return out


_STATE = {}


def _cell(job):
    arm = _STATE["arms"][job["arm_id"]]
    field = _STATE[job["field"]]
    p = dict(PARAMS)
    p["linker_max_atoms"] = job["n_atoms"]
    if job.get("no_interface_floor"):
        p["min_contact_residues"] = 0
    pose = {"pose_id": job["anchor_id"], "anchor_xyz": job["anchor_xyz"]}
    acc, st = BS.sample_placements(arm, pose, field, random.Random(job["seed"]), job["n_samples"], params=p)
    spans = sorted(pl["span_A"] for pl in acc)
    need = [max(1, int(math.ceil(s / RISE - 1e-9))) for s in spans]
    return {"arm_id": job["arm_id"], "anchor_id": job["anchor_id"], "linker_atoms": job["n_atoms"],
            "field": job["field"], "no_interface_floor": bool(job.get("no_interface_floor")),
            "shell_hi_A": round(G.contour_length_from_atoms(job["n_atoms"], RISE), 2),
            "n_samples": st["n_samples"], "n_accepted": st["n_accepted"],
            "acceptance_rate": st["acceptance_rate"],
            "n_prescreen_rejected": st["n_prescreen_rejected"],
            "span_A_min": round(spans[0], 2) if spans else None,
            "min_backbone_atoms_realised": min(need) if need else None}


def summarise(cells, geom):
    by_arm = {}
    for c in cells:
        by_arm.setdefault(c["arm_id"], []).append(c)
    out = {}
    for aid, rows in sorted(by_arm.items()):
        per_n, shortest = {}, None
        for n in sorted({r["linker_atoms"] for r in rows}):
            grp = [r for r in rows if r["linker_atoms"] == n]
            n_open = sum(1 for r in grp if r["n_accepted"] > 0)
            acc = sum(r["n_accepted"] for r in grp)
            smp = sum(r["n_samples"] for r in grp)
            per_n[str(n)] = {"n_anchors": len(grp), "n_anchors_with_any_admissible_placement": n_open,
                             "total_accepted": acc,
                             "pooled_acceptance_rate": round(acc / smp, 8) if smp else None}
            if shortest is None and n_open > 0:
                shortest = n
        out[aid] = {
            "recruiter": geom[aid]["recruiter"],
            "partner_class": geom[aid].get("partner_class"),
            "size_class": geom[aid]["size_class"],
            "n_residues": geom[aid]["n_residues"],
            "shortest_linker_atoms": shortest,
            "admits_at_the_%d_atom_gate" % GATE_ATOMS: bool(
                per_n.get(str(GATE_ATOMS), {}).get("n_anchors_with_any_admissible_placement", 0) > 0),
            "per_linker_length": per_n,
        }
    return out


def build(n_samples, procs, arms_wanted=None):
    t0 = time.time()
    if not os.path.exists(PDB_GZ):
        raise SystemExit("%s absent — it is a CI fetch (s4_lane_inputs_fetch.py); the dev sandbox's egress "
                         "proxy 403s RCSB. This is a MISSING READING, not an absent structure." % PDB_GZ)
    atoms = parse_pdb(PDB_GZ)
    hdr = header(PDB_GZ)
    unit = pick_biological_unit(atoms)
    keep = set(unit["dna_chains"]) | {unit["protein_chain"]}
    body = [a for a in atoms if a["chain"] in keep]
    nbre = locate_nbre(body, unit["dna_chains"])

    heavy_all = [a["xyz"] for a in body]
    heavy_dna = [a["xyz"] for a in body if a["res"] in DNA_RES]
    f_all = G.SquaredDistanceField(heavy_all, cell=0.9, clamp=8.0)
    f_dna = G.SquaredDistanceField(heavy_dna, cell=0.9, clamp=8.0)

    anchors = enumerate_anchors(body, unit, nbre, f_all)

    regs = T.load_registries()
    ids = sorted(arms_wanted or regs)
    arms = {aid: BS.load_arm_from_registry(regs[aid][0]) for aid in ids}
    geom = {}
    for aid in ids:
        g = T.body_geometry(arms[aid])
        g["partner_class"] = regs[aid][2]
        geom[aid] = g

    _STATE["arms"] = arms
    _STATE["complex"] = f_all
    _STATE["naked_dna"] = f_dna

    jobs = []
    s = SEED
    for aid in ids:
        for a in anchors["anchors"]:
            for n in LADDER:
                s += 1
                jobs.append({"arm_id": aid, "anchor_id": a["anchor_id"], "anchor_xyz": tuple(a["xyz"]),
                             "n_atoms": n, "n_samples": n_samples, "seed": s, "field": "complex"})
    # the ablation: same anchors, same arms, protein removed. Only the gate rung, to bound the cost.
    abl = []
    for aid in ids:
        for a in anchors["anchors"]:
            s += 1
            abl.append({"arm_id": aid, "anchor_id": a["anchor_id"], "anchor_xyz": tuple(a["xyz"]),
                        "n_atoms": GATE_ATOMS, "n_samples": n_samples, "seed": s, "field": "naked_dna"})
    # the interface-floor ablation, mirroring nr4a3_tcip_reach.interface_floor_ablation's question
    noif = []
    for aid in ids:
        for a in anchors["anchors"]:
            s += 1
            noif.append({"arm_id": aid, "anchor_id": a["anchor_id"], "anchor_xyz": tuple(a["xyz"]),
                         "n_atoms": GATE_ATOMS, "n_samples": n_samples, "seed": s, "field": "complex",
                         "no_interface_floor": True})

    allj = jobs + abl + noif
    if procs > 1:
        import multiprocessing as mp
        with mp.Pool(procs) as pool:
            res = pool.map(_cell, allj, chunksize=4)
    else:
        res = [_cell(j) for j in allj]
    cells = [r for r in res if r["field"] == "complex" and not r["no_interface_floor"]]
    ab_cells = [r for r in res if r["field"] == "naked_dna"]
    nf_cells = [r for r in res if r["no_interface_floor"]]

    free = {a["anchor_id"]: body_free_envelope(tuple(a["xyz"]), f_all) for a in anchors["anchors"]}
    pooled = {}
    for n in LADDER:
        v = [free[k][str(n)]["fraction_admissible"] for k in free
             if free[k][str(n)]["fraction_admissible"] is not None]
        pooled[str(n)] = {"shell_hi_A": free[list(free)[0]][str(n)]["shell_hi_A"],
                          "mean_fraction_admissible": round(sum(v) / len(v), 5) if v else None,
                          "min": round(min(v), 5) if v else None, "max": round(max(v), 5) if v else None}

    anchor_class = {a["anchor_id"]: a["groove_class"] for a in anchors["anchors"]}
    summary = summarise(cells, geom)
    groove_only = [c for c in cells if anchor_class.get(c["anchor_id"]) in ("minor", "major")]
    d = {
        "_title": "Is a response-element-based degrader geometrically buildable? (NBRE anchor, PDB 7WNH)",
        "_question": ("emc-unexplored-treatment-lanes.md §4: 7WNH is already in the repo — the anchor for "
                      "testing whether a response-element-based degrader is geometrically buildable, on the "
                      "linker-reach enumeration the repo already owns."),
        "_status": ("GEOMETRY ONLY, $0 CPU, pure stdlib. No binding, affinity, sequence-selectivity, "
                    "ternary-complex, ubiquitin-transfer, degradation, efficacy, safety, "
                    "therapeutic-window or clinical claim is made or implied."),
        "_method": ("nr4a3_basin_search.sample_placements UNCHANGED against a SquaredDistanceField over the "
                    "real heavy atoms of one NR4A2-NBRE complex; anchors enumerated on a lattice around the "
                    "response element rather than chosen; reported in nr4a3-tcip-reach.json's vocabulary"),
        "_inherits_the_tcip_ceiling": [
            "an `admits` answer is an ADMISSION OF EXCLUDED VOLUME and nothing else",
            "no tested body has ever failed this gate in this repository — see nr4a3-tcip-reach.json "
            "`★_named_effector.⚠_the_gate_still_cannot_fail`. A gate that cannot fail is not evidence; it "
            "is a precondition. That is why the two ablations below, which CAN come back either way, are "
            "run in the same pass and reported beside the headline.",
            "reach can REFUTE a configuration; it cannot license one",
            "every anchor is conditional on a DNA-binding warhead existing that occupies that position. "
            "None is proposed here and none is known for this element.",
        ],
        "structure": {
            "pdb_id": "7WNH", "title": hdr.get("title"), "method": hdr.get("method"),
            "resolution_A": hdr.get("resolution_A"),
            "uniprot_by_chain": hdr.get("uniprot_by_chain"),
            "uniprot_range_by_chain": hdr.get("uniprot_range_by_chain"),
            "⚠_it_is_NR4A2": ("no NR4A3-on-DNA structure exists; NR4A3's only PDB entry is 8XTT, an apo "
                              "NMR LBD with no DNA. Every number here is about NR4A2 on the NBRE. The NR4A "
                              "DBDs are 86-94 % identical and the DNA is B-form either way, but this is a "
                              "SUBSTITUTION and is labelled as one."),
            "biological_unit": unit,
            "n_heavy_atoms_in_body": len(heavy_all),
            "n_dna_heavy_atoms": len(heavy_dna),
        },
        "response_element": nbre,
        "anchor_set": anchors,
        "body_geometry": geom,
        "anchor_envelope_body_free": {"per_anchor": free, "pooled": pooled,
                                      "_what": ("fraction of each reach shell in which a second terminus's "
                                                "exit atom could sit at all, body removed — the sampler's "
                                                "own clearance predicate on a deterministic lattice")},
        "paired_placement_envelope": {"n_cells": len(cells), "n_samples_per_cell": n_samples,
                                      "linker_ladder_atoms": LADDER, "cells": cells},
        "summary": summary,
        "★_summary_groove_anchors_only": summarise(groove_only, geom),
        "_summary_note": ("`summary` pools all three anchor classes; `★_summary_groove_anchors_only` drops "
                          "the solvent-adjacent control anchors and is the one to read. The verdict is "
                          "taken from the groove-only summary."),
        "★_naked_dna_ablation": naked_dna_ablation(cells, ab_cells, geom, anchor_class),
        "★_interface_floor_ablation": interface_floor_ablation(cells, nf_cells),
        "runtime_s": round(time.time() - t0, 1),
    }
    d["verdict"] = verdict(d)
    return d


def naked_dna_ablation(cells, ab, geom, anchor_class):
    """★ THE ABLATION THAT CAN COME BACK EITHER WAY. If removing the 341-residue receptor does not change
    what the enumeration admits, then the receptor is not shaping this geometry and 'admits' is a statement
    about a naked duplex — true, and uninformative about this site.

    ⚠ REPORTED PER GROOVE CLASS, because pooling hides the answer. NR4A2 reads the MAJOR groove of the NBRE,
    so that is where deleting it should matter most; the minor groove is on the other face; and
    `backbone_or_solvent` is beside the duplex, where deleting the receptor should matter least. A pooled
    ratio averages those three different physical situations into one uninterpretable number — which is
    what the first version of this function did.
    """
    at_gate = [c for c in cells if c["linker_atoms"] == GATE_ATOMS]

    def group(rows, key):
        out = {}
        for c in rows:
            k = key(c)
            out.setdefault(k, [0, 0])
            out[k][0] += c["n_accepted"]
            out[k][1] += c["n_samples"]
        return out

    per_arm, per_arm_n = group(at_gate, lambda c: c["arm_id"]), group(ab, lambda c: c["arm_id"])
    per_cls = group(at_gate, lambda c: anchor_class.get(c["anchor_id"], "?"))
    per_cls_n = group(ab, lambda c: anchor_class.get(c["anchor_id"], "?"))

    def ratios_of(a, b):
        """⛔ WITH AN INTERVAL, BECAUSE THE FIRST VERSION HAD NONE AND IT OVER-CLAIMED.
        The 2026-08-07 40k-sample run returned groove ratios of 1.12-1.23 against a 1.08 control and the
        module reported 'the receptor IS shaping the geometry ... by more than at the control'. Those ratios
        rest on ACCEPTED COUNTS of 114-180. A ratio of two independent counts n_b/n_a has
        log-SE = sqrt(1/n_a + 1/n_b) ~= 0.11-0.13 here, so a 95 % interval on 1.23 is roughly [0.96, 1.57]
        and on 1.08 roughly [0.88, 1.34] — FULLY OVERLAPPING. The point estimates ordered the way the
        physics suggests and the sampling could not resolve it, and saying the first without the second is
        exactly the over-claim this repository forbids. The interval is now computed and the reading is
        conditional on it.
        """
        out = {}
        for k in sorted(set(a) | set(b)):
            ka, na = a.get(k, [0, 0])
            kb, nb = b.get(k, [0, 0])
            ra = ka / na if na else None
            rb = kb / nb if nb else None
            ratio = (rb / ra) if (ra and rb) else None
            lo = hi = None
            if ratio and ka > 0 and kb > 0:
                se = math.sqrt(1.0 / ka + 1.0 / kb)          # log-scale SE of a ratio of two Poisson counts
                lo, hi = ratio * math.exp(-1.96 * se), ratio * math.exp(1.96 * se)
            out[k] = {"n_accepted_with_receptor": ka, "n_samples_with_receptor": na,
                      "n_accepted_naked_dna": kb, "n_samples_naked_dna": nb,
                      "acceptance_with_receptor": round(ra, 8) if ra is not None else None,
                      "acceptance_naked_dna": round(rb, 8) if rb is not None else None,
                      "ratio_naked_over_complex": round(ratio, 3) if ratio else None,
                      "ratio_ci95": [round(lo, 3), round(hi, 3)] if lo else None}
        return out

    by_cls = ratios_of(per_cls, per_cls_n)
    groove = {k: v for k, v in by_cls.items() if k in ("minor", "major")}
    gr = [v["ratio_naked_over_complex"] for v in groove.values() if v["ratio_naked_over_complex"]]
    ctrl_row = by_cls.get("backbone_or_solvent") or {}
    ctrl = ctrl_row.get("ratio_naked_over_complex")
    ctrl_ci = ctrl_row.get("ratio_ci95")
    # Does ANY groove class's interval clear the control's interval? That is the only form in which this
    # comparison may be asserted at all.
    separated = bool(ctrl_ci and any(
        (v.get("ratio_ci95") or [0, 0])[0] > ctrl_ci[1] for v in groove.values()))
    return {
        "_what": "the same enumeration at the %d-atom gate with the NR4A2 chain deleted" % GATE_ATOMS,
        "per_arm_pooled_over_anchors": ratios_of(per_arm, per_arm_n),
        "★_per_groove_class": by_cls,
        "groove_ratio_min": min(gr) if gr else None,
        "groove_ratio_max": max(gr) if gr else None,
        "solvent_control_ratio": ctrl,
        "groove_separated_from_control_at_95pct": separated,
        "★_reading": (
            "in the grooves — where a sequence-directed warhead's exit vector would sit — deleting the "
            "receptor multiplies the admitted orientation space by %.2f-%.2fx, against %.2fx at the "
            "solvent-adjacent control anchors. %s"
            % (min(gr), max(gr), ctrl if ctrl else float('nan'),
               ("Every groove class's 95 %% interval clears the control's, so the receptor IS shaping the "
                "geometry at the anchors that matter and this is not merely a statement about a naked "
                "B-form duplex."
                if separated else
                "⛔ THE INTERVALS OVERLAP THE CONTROL'S, SO THIS COMPARISON IS UNRESOLVED AT THIS SAMPLING. "
                "The point estimates order the way the physics suggests — the protein reads the major "
                "groove and its deletion should matter more in a groove than beside the duplex — but the "
                "accepted counts are too few to say so, and an ordering of point estimates is not a "
                "finding. What follows is therefore that the receptor's contribution to this geometry is "
                "SMALL: an `admits` answer here is close to a statement about a naked B-form duplex, which "
                "is true of any DNA sequence. Resolving it needs more samples, not more interpretation."))
            if gr else "no groove anchor was admissible at all — see anchor_set.anchors_per_class"),
    }


def interface_floor_ablation(cells, nf):
    """The sampler's `min_contact_residues` is a DEGRADER's requirement — the recruited body must make an
    induced interface with the target. Reported here exactly as `nr4a3_tcip_reach` reports it, because a
    response-element degrader inherits the same open question about whether that floor is the right one."""
    at_gate = [c for c in cells if c["linker_atoms"] == GATE_ATOMS]
    a = sum(c["n_accepted"] for c in at_gate), sum(c["n_samples"] for c in at_gate)
    b = sum(c["n_accepted"] for c in nf), sum(c["n_samples"] for c in nf)
    ra = a[0] / a[1] if a[1] else None
    rb = b[0] / b[1] if b[1] else None
    return {
        "_what": ("the same cells at the %d-atom gate with min_contact_residues dropped from %d to 0 — i.e. "
                  "clash-only admission, no induced-interface requirement"
                  % (GATE_ATOMS, PARAMS["min_contact_residues"])),
        "acceptance_with_committed_floor": round(ra, 8) if ra is not None else None,
        "acceptance_clash_only": round(rb, 8) if rb is not None else None,
        "ratio": round(rb / ra, 3) if (ra and rb) else None,
        "_reading": ("the committed floor is what most of the refusal is: dropping it multiplies admission "
                     "%sx. The floor is a DEGRADER's requirement and is kept in the headline; a route that "
                     "does not need an induced interface should be read at the clash-only number."
                     % (round(rb / ra, 1) if (ra and rb) else "n/a")),
    }


def verdict(d):
    s = d["★_summary_groove_anchors_only"]
    key = "admits_at_the_%d_atom_gate" % GATE_ATOMS
    admits = [a for a, v in s.items() if v[key]]
    shortest = {a: v["shortest_linker_atoms"] for a, v in s.items()}
    return {
        "answer": "ADMITS" if admits and len(admits) == len(s) else ("PARTIAL" if admits else "REFUSES"),
        "_read_on": ("GROOVE anchors only (minor + major). The solvent-adjacent control anchors are "
                     "excluded from the verdict — see anchor_set.⛔_backbone_or_solvent_is_a_control."),
        "_in_the_tcip_enumerations_vocabulary": (
            "%d of %d staged second-terminus bodies admit at the %d-atom gate; shortest_linker_atoms = %s. "
            "Anchors: %d admissible lattice positions around the NBRE core (%s), %d used across %d classes."
            % (len(admits), len(s), GATE_ATOMS, shortest, d["anchor_set"]["n_admissible_anchor_positions"],
               d["anchor_set"]["by_groove"], d["anchor_set"]["n_anchors_used"],
               len(d["anchor_set"]["anchors_per_class"]))),
        "⛔_and_this_is_the_sentence_that_must_travel_with_it": (
            "AN `ADMITS` ANSWER IS AN EXCLUDED-VOLUME STATEMENT THAT NO TESTED BODY HAS EVER FAILED IN THIS "
            "REPOSITORY. It is therefore NOT evidence of anything beyond excluded volume: not of binding, "
            "not of sequence selectivity, not of ternary-complex formation, not of ubiquitin transfer, not "
            "of degradation, and certainly not of efficacy or safety. What it does is REMOVE a way the "
            "route could have been dead — a linker geometry that could not exist — and that is the only "
            "thing reach enumeration has ever been able to do."),
        "★_what_actually_carries_information_here": [
            d["★_naked_dna_ablation"]["★_reading"],
            d["★_interface_floor_ablation"]["_reading"],
        ],
        "⛔_the_blocker_this_does_not_touch": (
            "an NBRE-directed warhead is selective for a DNA SEQUENCE that NR4A1, NR4A2 and wild-type NR4A3 "
            "all read, and no such warhead exists for this element. The route's binding problem is moved "
            "from a protein pocket to a DNA sequence; it is not removed. Nothing here is a selectivity "
            "claim of any kind."),
        "_what_it_licenses": (
            "one line in the route registry: the response-element anchor is not geometrically refuted at "
            "chemically routine linker lengths, on the only NR4A-on-DNA structure that exists. It is a "
            "precondition cleared, not a result."),
    }


FRONTMATTER = """---
id: DOC-NR4A3-RE-REACH
title: Response-element-anchored degrader — is it geometrically buildable? (NBRE, PDB 7WNH)
level: L4
kind: memo
status: generated
generator: research/modalities/nr4a3_re_reach.py
canonical_for: ["the response-element anchor's linker-reach admissibility"]
purpose: "Answer emc-unexplored-treatment-lanes.md section 4: point the linker-reach enumeration this repository already owns at the NBRE response element instead of at an NR4A3 pocket."
scope: Geometry only. An `admits` answer is an excluded-volume statement that no tested body has ever failed. No binding, sequence-selectivity, ternary-complex, ubiquitin-transfer, degradation, efficacy, safety, therapeutic-window or clinical statement.
audience: [maintainers, autonomous research agents]
date: 2026-08-07
last_verified: unverified
---

"""


def to_markdown(d):
    v = d["verdict"]
    L = [FRONTMATTER.rstrip("\n"), "",
         "# Response-element-based degrader — reach enumeration on the NBRE (PDB 7WNH)", "",
         "> Generated by `nr4a3_re_reach.py`; this file is derived — edit the module, not this.", "",
         "> %s" % d["_status"], "",
         "**Verdict: %s.** %s" % (v["answer"], v["_in_the_tcip_enumerations_vocabulary"]), "",
         "> %s" % v["⛔_and_this_is_the_sentence_that_must_travel_with_it"], "",
         "## Structure", "",
         "- 7WNH · %s · %s A · protein chain %s + DNA %s" % (
             d["structure"]["method"], d["structure"]["resolution_A"],
             d["structure"]["biological_unit"]["protein_chain"],
             d["structure"]["biological_unit"]["dna_chains"]),
         "- %s" % d["structure"]["⚠_it_is_NR4A2"],
         "- NBRE `%s` located on chain %s at %s" % (
             d["response_element"]["matched"], d["response_element"]["chain"],
             d["response_element"]["resseqs"]), "",
         "- anchors: %s admissible lattice positions; %s" % (
             d["anchor_set"]["n_admissible_anchor_positions"], d["anchor_set"]["by_groove"]), "",
         "## Per body (groove anchors only)", "",
         "| arm | class | residues | shortest linker (atoms) | admits at the %d-atom gate |" % GATE_ATOMS,
         "|---|---|---|---|---|"]
    for a, r in sorted(d["★_summary_groove_anchors_only"].items()):
        L.append("| %s | %s | %d | %s | %s |" % (a, r["size_class"], r["n_residues"],
                                                 r["shortest_linker_atoms"],
                                                 r["admits_at_the_%d_atom_gate" % GATE_ATOMS]))
    L += ["", "## What actually carries information", ""]
    L += ["- %s" % x for x in v["★_what_actually_carries_information_here"]]
    L += ["", "## What this does not touch", "", v["⛔_the_blocker_this_does_not_touch"], ""]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--samples", type=int, default=40000, help="placements per (arm x anchor x rung)")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--arms", default="")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)
    ids = [a.strip() for a in args.arms.split(",") if a.strip()] or None
    d = build(args.samples, args.procs, ids)
    with open(args.out, "w") as fh:
        json.dump(d, fh, indent=1)
        fh.write("\n")
    with open(os.path.splitext(args.out)[0] + ".md", "w") as fh:
        fh.write(to_markdown(d))
    print(json.dumps(d["verdict"], indent=1, ensure_ascii=False))
    print("\nruntime %.1fs" % d["runtime_s"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
