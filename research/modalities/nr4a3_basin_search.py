#!/usr/bin/env python3
"""
RUNG 5a — the MECHANISM-FIRST orientation-basin search. $0 CPU, pure stdlib.

WHAT nr4a3-program-map.md ASKS FOR, and what this implements (§"The prospective stage: mechanism-first, then
orientation-first inverse design"):

    paralogue-unique CHEMISTRY (nucleophile) + paralogue-unique GEOMETRY (lysine)
        -> basins that exploit ONE of them -> productive CRL geometry
        -> interface thermodynamics used to RANK within the survivors
        -> linker requirements -> candidate molecules

For each E3 recruiter this samples many rigid-body placements of the ligase around the warhead-bound NR4A3
LBD under a flexible LINKER-REACH restraint, keeps the placements that are clash-free, form a real interface,
and are bridgeable, clusters them into ~3-8 BASINS, and then scores each basin on the two CATEGORICAL terms
plus the marginal one:

  (a) ELECTROPHILE-REACH — can a linker tethered at the warhead exit vector and the E3 ligand exit vector route
      a pendant mild electrophile onto an NR4A3-UNIQUE cysteine (C397 / C420 / C559)? None of them sits inside
      the pocket, so this is an electrophile on the exit vector or the linker, which in a degrader is
      architecturally free. Answered with the EXACT three-ball / integer-branch-position criterion
      (`linker_design.min_linker_atoms_exact`). ⚠ CORRECTED 2026-07-25: this used the prolate-spheroid
      RELAXATION (`basin_geom.linker_can_visit`), which credits the pendant with shortening the anchor-anchor
      SPAN and so understates every linker requirement by up to 2e/rise ~ 5 backbone atoms. See
      `electrophile_reach` for the derivation and the superseded values, which are carried per record.
      REVERSIBLE-covalent (cyanoacrylamide-type) is the preferred chemistry and the output says so: an
      irreversible adduct makes the degrader stoichiometric and forfeits catalytic turnover.
  (b) TRANSFER-ZONE LYSINE IDENTITY — which lysine does the modelled E2~Ub transfer zone cover? Scored as SET
      MEMBERSHIP, not energy: unique-only highest, unique+conserved next, conserved-only lowest. And, going
      beyond the letter of the spec because it is the question that actually decides selectivity, the SAME
      transform is evaluated against the superposed paralogues, so a basin is only categorical if NR4A3's zone
      covers a unique lysine AND the paralogues' zones cover none.
  (d) POSE-MARGINALISATION — the whole search runs over an ensemble of warhead exit-vector anchors and only
      basins that persist are carried, with the surviving fraction reported. Sequence-level uniqueness of
      C397/K572 is pose-independent; only the REACH estimate is conditional.

And nr4a3-program-map.md load-bearing piece 4 — ACCESSIBILITY IS SEPARATED FROM STABILITY. `P(B_k | d, s)` (can a
linker of a given length reach and hold basin k?) is a worm-like-chain end-to-end probability over the basin's
anchor-anchor spans; the orientation's plausibility is a separate, explicitly UNITLESS contact score. A
favourable basin the linker rarely accesses is irrelevant, and the output reports both rather than a product.

WHAT THE CHEAP SCORER IS AND IS NOT (nr4a3-program-map.md, Tier-2 asymmetry). The interface score here NOMINATES; it
does not decide. Cheap scoring has poor signal-to-noise for a ~1 kcal/mol energy difference — and the marginal
axis needs ~2.0 kcal/mol of true margin against a best-case resolvable 1.12 — so no conclusion in this file
rests on a small score difference between paralogues. What cheap geometry DOES answer reliably is set
membership: "does this basin place an electrophile at C397?", "does its transfer zone cover K572 and no
paralogue lysine?" Those are the terms the gate is read from.

HONEST SCOPE (nr4a3-program-map.md §"Honest scope and language discipline"). Everything is conditional on the
hypothesised cmpd19 binary pose x the chosen receptor frame — a DOUBLE conditionality — and this repo holds no
cmpd19 pose in the matched-model frame, so the warhead exit vector is marginalised over an ensemble rather
than asserted. Outputs are "predicted selective candidate" language only; nothing here implies efficacy,
safety, a therapeutic window, or clinical readiness.

Inputs (all already in-repo, all $0):
  results/nr4a3-matrix/nr4a{3,1,2}-opened.pdb        matched, state-matched opened LBD models
  research/modalities/nr4a-paralogue-unique-residues.json   Tier-0 unique Cys/Lys + the cryptic pocket
  research/modalities/nr4a3-differential-surface-atlas.json Tier-1 RSA + lysine map
  research/modalities/nr4a3-e3-arm-registry.json     E3 arms staged by nr4a3_e3_stage.py (CI; RCSB is
                                                     403'd from the dev sandbox)

Usage
    python nr4a3_basin_search.py --self-test              # synthetic E3, exercises the whole pipeline offline
    python nr4a3_basin_search.py --samples 250000 --n-poses 12
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                      # noqa: E402
import linker_design as LD                  # noqa: E402  (the EXACT reach rule; see `electrophile_reach`)
import nr4a_differential_atlas as ATLAS     # noqa: E402  (reuse the tested SASA + NW aligner)

# ---------------------------------------------------------------------------------------------------------
# PREREGISTERED PARAMETERS. Every threshold the search uses lives here, is written into the output, and is
# stated as a model choice rather than buried in the code. Nothing below is fitted to produce an answer.
# ---------------------------------------------------------------------------------------------------------

PARAMS = {
    # --- linker reach (the tether that makes this an orientation search and not blind docking)
    "linker_min_atoms": 3,
    "linker_max_atoms": 20,          # ~25 A contour; STRATEGY: "the linker already leaves the pocket and
                                     # travels 10-20 A". 20 atoms is a permissive SAMPLING ceiling, not a
                                     # design target — see linker_gate_atoms.
    # THE GATE MUST NOT BE READ AT THE SAMPLING CEILING. At 20 atoms the focal-sum criterion admits almost
    # any cysteine within ~15 A of the anchor midpoint, so "reachable" would be nearly free and term (a)
    # would pass trivially — a gate that cannot fail is not a gate. The categorical limb is therefore read at
    # a PRACTICAL linker length, with the full length profile reported so the choice is visible and a reader
    # can move it.
    "linker_gate_atoms": 12,         # ~15 A contour; a PEG3/short-alkyl linker, mid-range for real degraders
    "linker_report_atoms": [6, 8, 10, 12, 14, 16, 20],
    "linker_rise_per_atom_A": 1.25,  # projected rise of an all-anti sp3 chain (basin_geom.contour_length_from_atoms)
    "linker_persistence_length_A": 4.0,   # PEG/alkyl-like; the accessibility term is swept over this
    "electrophile_arm_A": 3.0,       # a mild pendant electrophile (e.g. a cyanoacrylamide) on a short arm.
                                     # ⚠ PREREGISTERED AND UNCHANGED BY THE 2026-07-25 REACH CORRECTION. It is
                                     # SHORTER than every named building block in the sweep below, so it is
                                     # the conservative reading; moving the gate onto a longer pendant after
                                     # seeing that the correction costs basins would be exactly the tuning
                                     # load-bearing piece 5 forbids. The sweep is reported, never read as the gate.
    "reach_scan_max_atoms": 60,      # ceiling of the EXACT min-length scan. Beyond a PEG6-diacid-scale
                                     # backbone (~24) nothing is a design answer; 60 exists only so an
                                     # unreachable cysteine is reported as unreachable rather than as a number.

    # --- steric acceptance (coarse rigid-body; residue-level, stated as such)
    "hard_clash_A": 3.0,             # a CA/CB centre this close to another protein's heavy atom is an overlap
    "soft_clash_A": 3.6,             # 3.0-3.6 A is relievable by side-chain rotamer adjustment
    "max_soft_clashes": 6,
    "contact_A": 6.0,                # CB within 6.0 A of a target heavy atom = interface residue
    "min_contact_residues": 12,      # below this it is a tethered pair, not an interface

    # --- transfer zone (term (b))
    "e2_cap_half_angle_deg": 60.0,   # the RING-E2 module swings; the zone is an ARC, not a point
    "n_e2_samples": 48,
    "ring_to_e2_cys_A": 25.0,        # overridden by the MEASURED value when the registry has one
    "ring_to_e2_cys_range_A": [18.0, 32.0],   # sensitivity sweep, always reported
    # THE TRANSFER DISTANCE IS CALIBRATED, NOT GUESSED — and the calibration moved it a long way. The default
    # below was an assumption (~10 A, "the lysine has to reach the thioester"). The staging step measures it
    # instead, from a solved CRL ubiquitylation assembly, and gets a NEAREST substrate lysine 17.1 A from the
    # E2 catalytic cysteine. A 10 A zone would therefore have been ~7 A too strict and would have suppressed
    # term (b) across the board. The measured value replaces this at run time when the registry carries one;
    # the sweep spans tighter and looser so the category's dependence on the choice is visible.
    # HONEST LIMIT: a deposited assembly is a snapshot poised for transfer, not the transition state, so the
    # measured distance is an empirically anchored PERMISSIVE radius, not a proof of the productive one.
    "lysine_transfer_A": 10.0,
    "lysine_transfer_sweep_A": [10.0, 14.0, 17.0, 21.0],
    # Spread about an OBSERVED catalytic-cysteine anchor, representing real CRL arm mobility. Kept small and
    # swept: the point of preferring the observed anchor is that it needs far less modelling than the arc.
    "observed_anchor_mobility_A": 8.0,

    # --- clustering. A basin is a TARGET-SURFACE PATCH, identified by the interface fingerprint, NOT an
    # SE(3) micro-cluster: see basin_geom.leader_cluster_by for the measurement that forced this.
    "basin_jaccard_cutoff": 0.5,           # within a pose
    "meta_basin_jaccard_cutoff": 0.6,      # across the pose ensemble (looser: the anchor itself moves)
    "fingerprint_contact_A": 8.0,          # target residue counted as interface if its CB is within this of
                                           # any E3 CB — the standard coarse residue-contact definition
    "max_basins_per_arm": 8,
    "min_basin_members": 5,
    "min_basin_fraction": 0.01,            # ... or 1 % of the accepted set, whichever is larger
    "n_landmarks": 10,

    # --- pose ensemble (term (d))
    "pose_anchor_shell_A": [5.0, 11.0],   # exit-vector anchor sits this far from the cryptic-pocket centroid
    "pose_min_clearance_A": 3.4,          # ... and not inside the protein
    "pose_min_separation_A": 3.0,         # representative anchors must be this far apart from each other
}

# The named-pendant SENSITIVITY sweep, imported rather than restated so RUNG 5a's gate and RUNG 5b's enumerator
# cannot drift apart (CLAUDE.md §1, one fact one place). Read `linker_design.PENDANT_REACH_A` for what each
# entry is and why a sweep over building blocks is not a tunable knob. The GATE is `electrophile_arm_A`.
PARAMS["electrophile_pendant_sweep_A"] = dict(LD.PENDANT_REACH_A)

UNIPROT_OFFSET = 372          # NR4A3 LBD local residue 1 == UniProt 373
HEAVY = ("C", "N", "O", "S", "SE", "P")
HYDROPHOBIC = set("AVLIMFWCY")
POSITIVE = set("KR")
NEGATIVE = set("DE")
POLAR = set("STNQHYWCKRDE")
BACKBONE = {"N", "CA", "C", "O", "OXT"}


# ---------------------------------------------------------------------------------------------------------
# Structure handling
# ---------------------------------------------------------------------------------------------------------


def load_paralogue(path):
    """Parse a matched opened-LBD model into the per-residue representation the search uses.

    Hydrogens are dropped: the models carry them, every distance criterion here is a heavy-atom criterion, and
    leaving them in would make the distance field report H-to-H distances that no steric rule was written for.
    """
    residues, atoms = ATLAS.parse_pdb(path)
    heavy = [a for a in atoms if a["elem"] in HEAVY]
    seq = "".join(aa for _, aa in residues)
    ids = [r for r, _ in residues]
    by_res = {}
    for a in heavy:
        by_res.setdefault(a["resid"], []).append(a)
    ca, cb = {}, {}
    for rid, alist in by_res.items():
        for a in alist:
            if a["name"] == "CA":
                ca[rid] = (a["x"], a["y"], a["z"])
        side = [a for a in alist if a["name"] not in BACKBONE]
        cb[rid] = G.centroid([(a["x"], a["y"], a["z"]) for a in side]) if side else ca.get(rid)
    return {
        "path": path, "residues": residues, "seq": seq, "ids": ids,
        "heavy_xyz": [(a["x"], a["y"], a["z"]) for a in heavy],
        "atoms_by_res": by_res, "ca": ca, "cb": cb,
        "aa_of": {rid: aa for rid, aa in residues},
    }


def atom_xyz(model, resid, name):
    for a in model["atoms_by_res"].get(resid, []):
        if a["name"] == name:
            return (a["x"], a["y"], a["z"])
    return None


def superpose_paralogue(mobile, ref, max_iter=8, min_core=60):
    """Put a paralogue model into the NR4A3 frame using BLOSUM62-aligned CA pairs, with ITERATIVE CORE
    REFINEMENT — and report what the refinement had to throw away.

    WHY THE REFINEMENT, with the diagnostic that forced it. A single global least-squares fit of all 244
    aligned CA pairs gives RMSD 6.38 A for NR4A1 and 4.93 A for NR4A2 — values that would make any
    paralogue comparison built on them meaningless. That is NOT a bad global fit: iterating with outlier
    rejection converges to a 203/244 structured CORE at 1.73 A (NR4A1) and 206/249 at 1.60 A (NR4A2), which
    is normal for 62 %/68 % sequence identity, while the discarded minority deviates by up to 32-37 A. So
    the models agree on the fold and disagree on terminal/loop segments, exactly as independently-built
    opened conformers of a divergent family should.

    THE CONSEQUENCE THAT MUST NOT BE HIDDEN. A paralogue lysine or surface residue sitting in one of those
    discarded segments has an UNRELIABLE position in this frame, so any term-(b) claim about it is
    unreliable too. This function therefore returns a per-residue post-fit deviation map, and the caller
    attaches it to every paralogue lysine so the output can flag which ones are trustworthy.

    This is what makes the comparison MATCHED in the atlas's sense: ONE sampled set of E3 placements is
    evaluated against all three paralogues, so a difference between them cannot be an artefact of three
    independent searches finding different corners of orientation space.
    """
    aln = ATLAS.nw_align(mobile["seq"], ref["seq"])
    pairs = [(i, j) for i, j in aln if i is not None and j is not None]
    mob, rf, ids = [], [], []
    for i, j in pairs:
        ri, rj = mobile["ids"][i], ref["ids"][j]
        if ri in mobile["ca"] and rj in ref["ca"]:
            mob.append(mobile["ca"][ri]); rf.append(ref["ca"][rj]); ids.append((ri, rj))
    R, t, global_rmsd = G.horn_superpose(mob, rf)
    core = list(range(len(mob)))
    core_rmsd = global_rmsd
    for _ in range(max_iter):
        R, t, core_rmsd = G.horn_superpose([mob[k] for k in core], [rf[k] for k in core])
        moved = G.apply_superpose(mob, R, t)
        cut = max(2.0, 2.0 * core_rmsd)
        nxt = [k for k in range(len(mob)) if G.dist(moved[k], rf[k]) <= cut]
        if len(nxt) < min_core or nxt == core:
            break
        core = nxt
    R, t, core_rmsd = G.horn_superpose([mob[k] for k in core], [rf[k] for k in core])
    moved = G.apply_superpose(mob, R, t)
    dev_by_mobile_res = {ids[k][0]: G.dist(moved[k], rf[k]) for k in range(len(mob))}
    devs = sorted(dev_by_mobile_res.values())
    out = dict(mobile)
    out["heavy_xyz"] = G.apply_superpose(mobile["heavy_xyz"], R, t)
    out["ca"] = dict(zip(mobile["ca"], G.apply_superpose(list(mobile["ca"].values()), R, t)))
    out["cb"] = dict(zip(mobile["cb"], G.apply_superpose(list(mobile["cb"].values()), R, t)))
    moved = {}
    for rid, alist in mobile["atoms_by_res"].items():
        pts = G.apply_superpose([(a["x"], a["y"], a["z"]) for a in alist], R, t)
        moved[rid] = [dict(a, x=p[0], y=p[1], z=p[2]) for a, p in zip(alist, pts)]
    out["atoms_by_res"] = moved
    # residue-level correspondence NR4A3 local id -> paralogue local id (for the categorical checks)
    corr = {}
    for i, j in pairs:
        corr[ref["ids"][j]] = mobile["ids"][i]
    out["corr_from_ref"] = corr
    out["deviation_by_res"] = dev_by_mobile_res
    out["superposition"] = {
        "n_ca_pairs": len(mob),
        "global_all_pair_rmsd_A": round(global_rmsd, 3),
        "n_core": len(core),
        "core_fraction": round(len(core) / max(1, len(mob)), 3),
        "core_rmsd_A": round(core_rmsd, 3),
        "post_fit_deviation_A": {"median": round(devs[len(devs) // 2], 2),
                                 "p90": round(devs[int(0.9 * len(devs))], 2),
                                 "max": round(devs[-1], 2)},
        "_note": "Reported as global-vs-core deliberately. The global figure is dominated by a minority of "
                 "terminal/loop positions that the two independently-built opened models genuinely place "
                 "differently; the core figure is the one that says whether the fold-level frame is shared. "
                 "Residues with a large post-fit deviation have UNRELIABLE positions in this frame and any "
                 "claim about them is flagged accordingly.",
    }
    return out


# ---------------------------------------------------------------------------------------------------------
# Reactive-residue and pocket bookkeeping
# ---------------------------------------------------------------------------------------------------------


def load_reactive_map(unique_json, model3):
    """The Tier-0 categorical handles, plus every OTHER lysine and cysteine in the model, so the search can
    ask the discriminating question ('is the covered lysine unique or shared?') rather than only the
    presence question."""
    u = json.load(open(unique_json))
    pocket_local = [x - UNIPROT_OFFSET for x in u["cryptic_pocket_uniprot"]]
    # TWO pocket point sets, both stated rather than conflated:
    #  * `pocket_points` = ALL heavy atoms of the pocket residues — the distance reference, matched to the
    #    Tier-0 artifact's definition so the two files' distances are comparable. (Tier-0 also included
    #    hydrogens, which makes its numbers a few tenths of an angstrom smaller; the models carry H.)
    #  * `pocket_centroid` = centroid of the SIDE-CHAIN heavy atoms only — the cavity itself, which is what
    #    the warhead occupies and therefore what the exit-vector anchor shell should be centred on.
    pocket_pts, pocket_side = [], []
    for rid in pocket_local:
        for a in model3["atoms_by_res"].get(rid, []):
            if a["elem"] not in HEAVY:
                continue
            pocket_pts.append((a["x"], a["y"], a["z"]))
            if a["name"] not in BACKBONE:
                pocket_side.append((a["x"], a["y"], a["z"]))
    unique_cys, unique_lys = [], []
    for entry, bucket in ((u["nr4a3_unique_cysteines"], unique_cys), (u["nr4a3_unique_lysines"], unique_lys)):
        for c in entry:
            g = c.get("geometry") or {}
            if "local_resid" not in g:
                continue
            xyz = atom_xyz(model3, g["local_resid"], g["reactive_atom"])
            if xyz is None:
                continue
            bucket.append({
                "uniprot_resid": c["resnum"], "local_resid": g["local_resid"],
                "atom": g["reactive_atom"], "xyz": xyz, "rsa": g["rsa"], "exposed": g["exposed"],
                "nr4a1_partner": c["partners"]["NR4A1"]["residue"] + str(c["partners"]["NR4A1"]["resnum"]),
                "nr4a2_partner": c["partners"]["NR4A2"]["residue"] + str(c["partners"]["NR4A2"]["resnum"]),
            })
    uniq_lys_ids = {k["local_resid"] for k in unique_lys}
    all_lys = []
    for rid, aa in model3["residues"]:
        if aa != "K":
            continue
        xyz = atom_xyz(model3, rid, "NZ")
        if xyz is None:
            continue
        all_lys.append({"local_resid": rid, "uniprot_resid": rid + UNIPROT_OFFSET, "xyz": xyz,
                        "unique": rid in uniq_lys_ids})
    uniq_cys_ids = {c["local_resid"] for c in unique_cys}
    all_cys = []
    for rid, aa in model3["residues"]:
        if aa != "C":
            continue
        xyz = atom_xyz(model3, rid, "SG")
        if xyz is None:
            continue
        all_cys.append({"local_resid": rid, "uniprot_resid": rid + UNIPROT_OFFSET, "xyz": xyz,
                        "unique": rid in uniq_cys_ids})
    return {
        "pocket_local": pocket_local, "pocket_points": pocket_pts,
        "pocket_centroid": G.centroid(pocket_side),
        "unique_cysteines": unique_cys, "unique_lysines": unique_lys,
        "all_lysines": all_lys, "all_cysteines": all_cys,
    }


def paralogue_lysines(par_model, unreliable_A=4.0):
    """Every lysine NZ of a superposed paralogue, each carrying the post-fit deviation of its own residue so
    a term-(b) claim about a lysine sitting in a badly-superposed loop is visibly untrustworthy rather than
    silently counted."""
    dev = par_model.get("deviation_by_res", {})
    out = []
    for rid, aa in par_model["residues"]:
        if aa != "K":
            continue
        for a in par_model["atoms_by_res"].get(rid, []):
            if a["name"] == "NZ":
                d = dev.get(rid)
                out.append({"local_resid": rid, "xyz": (a["x"], a["y"], a["z"]),
                            "fit_deviation_A": round(d, 2) if d is not None else None,
                            "position_reliable": (d is not None and d <= unreliable_A)})
                break
    return out


# ---------------------------------------------------------------------------------------------------------
# The warhead exit-vector POSE ENSEMBLE (term (d))
# ---------------------------------------------------------------------------------------------------------


def build_pose_ensemble(model3, reactive, field3, n_poses, rng, params=PARAMS):
    """Sample representative WARHEAD EXIT-VECTOR ANCHORS at the mouth of the cryptic pocket.

    WHY AN ENSEMBLE AND NOT A DOCKED POSE. The repo holds no cmpd19 pose in this matched-model frame — cmpd19
    has no solved NR4A3 co-crystal at all, only functional target engagement — so asserting one exit-vector
    point would manufacture precision the evidence does not support. What the basin search actually consumes
    from a warhead pose is ONE point (where the linker leaves) and its direction; so the honest construction
    marginalises over the set of positions a linker could plausibly leave from, given the premise that the
    warhead occupies the cryptic pocket. That premise is the conditionality nr4a3-program-map.md requires be reported,
    and it is a far smaller conditional surface than a single asserted pose.

    An anchor qualifies if it is (i) in the shell around the cryptic-pocket centroid a warhead's exit
    substituent could reach, (ii) not inside the protein, and (iii) solvent-connected, tested by requiring a
    clear straight path outward — otherwise the 'exit vector' points into the protein core and no linker
    leaves. Representatives are then spread by a minimum-separation filter so the ensemble covers the mouth
    instead of clumping.
    """
    lo, hi = params["pose_anchor_shell_A"]
    cen = reactive["pocket_centroid"]
    cands = []
    tries = 0
    while len(cands) < n_poses * 400 and tries < n_poses * 40000:
        tries += 1
        v = G.random_unit_vector(rng)
        r = lo + rng.random() * (hi - lo)
        p = (cen[0] + v[0] * r, cen[1] + v[1] * r, cen[2] + v[2] * r)
        if field3.min_dist(p) < params["pose_min_clearance_A"]:
            continue
        # solvent-connected: stepping 8 A further out along the same ray must stay outside the protein
        out = (p[0] + v[0] * 8.0, p[1] + v[1] * 8.0, p[2] + v[2] * 8.0)
        if field3.min_dist(out) < params["pose_min_clearance_A"]:
            continue
        cands.append((p, v, field3.min_dist(p)))
    # spread: greedy, most-buried-first so anchors hug the pocket mouth rather than floating in bulk solvent
    cands.sort(key=lambda c: c[2])
    chosen = []
    for p, v, clr in cands:
        if all(G.dist(p, q[0]) >= params["pose_min_separation_A"] for q in chosen):
            chosen.append((p, v, clr))
        if len(chosen) >= n_poses:
            break
    return [{"pose_id": f"exitvec_{i:02d}", "anchor_xyz": list(p), "exit_direction": list(v),
             "clearance_A": round(clr, 2),
             "dist_to_pocket_centroid_A": round(G.dist(p, cen), 2)}
            for i, (p, v, clr) in enumerate(chosen)]


# ---------------------------------------------------------------------------------------------------------
# E3 arm loading
# ---------------------------------------------------------------------------------------------------------


def parse_multichain_pdb(path):
    """CHAIN-AWARE PDB parse. The atlas's `parse_pdb` keys residues by residue number ALONE, which is correct
    for a single-chain LBD model and silently WRONG for a multi-chain E3 arm: VHL, Elongin B and Elongin C all
    number from ~1, so their residues would collide and two thirds of the recruiter would vanish. Derived from
    the data, not assumed (TESTING.md rule 1) — the key is (chain, resid, icode)."""
    out = {}
    order = []
    with open(path) as fh:
        for ln in fh:
            if ln[:6] not in ("ATOM  ", "HETATM"):
                continue
            resn = ln[17:20].strip()
            if resn not in ATLAS.THREE2ONE:
                continue
            alt = ln[16]
            if alt not in (" ", "A"):
                continue
            elem = (ln[76:78].strip() or ln[12:16].strip()[0]).upper()
            if elem not in HEAVY:
                continue
            key = (ln[21], int(ln[22:26]), ln[26])
            if key not in out:
                out[key] = {"resname": resn, "aa": ATLAS.THREE2ONE[resn], "atoms": []}
                order.append(key)
            out[key]["atoms"].append((ln[12:16].strip(),
                                      (float(ln[30:38]), float(ln[38:46]), float(ln[46:54]))))
    return order, out


def load_arm_from_registry(rec):
    """Turn one staged registry record into the rigid body + anchors the search moves."""
    path = os.path.join(REPO, rec["receptor_pdb"])
    order, res = parse_multichain_pdb(path)
    keys, ca_l, cb_l, aa_l = [], [], [], []
    for key in order:
        r = res[key]
        cav = next((xyz for nm, xyz in r["atoms"] if nm == "CA"), None)
        if cav is None:
            continue
        side = [xyz for nm, xyz in r["atoms"] if nm not in BACKBONE]
        keys.append(key)
        ca_l.append(cav)
        cb_l.append(G.centroid(side) if side else cav)
        aa_l.append(r["aa"])
    query = ca_l + cb_l
    ring = rec.get("ring") or {}
    return {
        "arm_id": rec["arm_id"], "recruiter": rec["recruiter"], "crl": rec.get("crl"),
        "keys": keys, "ca": ca_l, "cb": cb_l, "n_ca": len(ca_l),
        "aa": aa_l, "query": query,
        "chains": sorted({k[0] for k in keys}),
        "anchor": tuple(rec["ligand"]["exit_atom_xyz"]),
        "ligand_centroid": tuple(rec["ligand"]["ligand_centroid"]),
        "ring": tuple(ring["ring_centroid_xyz"]) if ring.get("ring_centroid_xyz") else None,
        "cullin": tuple(ring["cullin_centroid_xyz"]) if ring.get("cullin_centroid_xyz") else None,
        # The transfer anchor is the point the term-(b) zone is built on. Preferred source: the E2 catalytic
        # cysteine OBSERVED in a solved ubiquitylation assembly and bridged into this receptor's frame, in
        # which case no RING swing has to be modelled at all. Fallback: the composed RING, which the staging
        # step measured to sit 48.6 A from an intact assembly's RING on the CRBN arm — so when the fallback is
        # in use the zone is a MODEL with a very large uncertainty, and the output says so.
        "transfer_anchor": rec.get("transfer_anchor"),
        "tanchor": (tuple(rec["transfer_anchor"]["xyz"])
                    if (rec.get("transfer_anchor") or {}).get("source") == "observed_in_intact_assembly"
                    else None),
        "tanchor_source": (rec.get("transfer_anchor") or {}).get("source", "none"),
        "intact_assembly": rec.get("intact_assembly"),
        "composition_check": rec.get("composition_check"),
        "provenance": rec.get("provenance", {}),
        "ligand_het": rec["ligand"]["het_code"],
        # The E3 lane requires its `caveats` be carried into any downstream report, and it is right to: a
        # recruiter measured with a partner protein removed, or on an asymmetric unit rather than a
        # biological assembly, is usable but must not be reported as if it were clean. `backfilled` is
        # equally load-bearing — a backfilled recruiter is an E3-CHOICE SENSITIVITY CONTROL, not a co-winner,
        # so a difference between it and the front-runner is not a preference this rung may report.
        "lane1": rec.get("lane1") or {},
        "exit_vector_source": rec["ligand"].get("exit_vector_source", {"source": "derived_here"}),
    }


def synthetic_arm(rng, n_res=120):
    """A synthetic globular 'E3' for --self-test and unit tests: a hollow-ish sphere of pseudo-residues with a
    ligand anchor on its surface and a RING offset. Exercises every code path without any network."""
    ca, cb, aa = [], [], []
    for i in range(n_res):
        v = G.random_unit_vector(rng)
        r = 14.0 + rng.random() * 3.0
        p = (v[0] * r, v[1] * r, v[2] * r)
        ca.append(p)
        cb.append((v[0] * (r + 1.4), v[1] * (r + 1.4), v[2] * (r + 1.4)))
        aa.append("AVLIKRDESTNQFWY"[i % 15])
    anchor = (0.0, 0.0, 18.5)
    return {
        "arm_id": "synthetic", "recruiter": "SYNTH", "crl": "SYNTH",
        "keys": [("A", i, " ") for i in range(n_res)], "ca": ca, "cb": cb, "aa": aa, "query": ca + cb,
        "n_ca": n_res, "chains": ["A"],
        "anchor": anchor, "ligand_centroid": (0.0, 0.0, 15.0),
        "ring": (0.0, 0.0, -30.0), "cullin": (0.0, 0.0, -55.0),
        "tanchor": None, "tanchor_source": "composed_ring_MODEL",
        "provenance": {"synthetic": True}, "ligand_het": "SYN",
    }


# ---------------------------------------------------------------------------------------------------------
# The search
# ---------------------------------------------------------------------------------------------------------


def _prescreen_indices(arm, n):
    return G.farthest_point_sample(arm["query"], n)


def sample_placements(arm, pose, field3, rng, n_samples, params=PARAMS, prescreen_n=44):
    """Sample rigid-body placements of `arm` around the fixed target under the linker-reach restraint.

    Parameterisation: the E3's LIGAND EXIT ATOM is placed at a point in the reach shell around the warhead
    exit-vector anchor, then the E3 body is rotated about it with a Haar-uniform rotation. Six DOF, and both
    halves are constrained by the physical tether rather than sampled blind over SE(3) — which is what makes
    this affordable at $0 and what stops the sampler wasting its budget on placements no linker could realise.
    """
    a_t = tuple(pose["anchor_xyz"])
    L_max = G.contour_length_from_atoms(params["linker_max_atoms"], params["linker_rise_per_atom_A"])
    L_min = G.contour_length_from_atoms(params["linker_min_atoms"], params["linker_rise_per_atom_A"])
    hard, soft, contact = params["hard_clash_A"], params["soft_clash_A"], params["contact_A"]
    max_soft, min_contact = params["max_soft_clashes"], params["min_contact_residues"]

    pivot = arm["anchor"]
    q = arm["query"]
    nq = len(q)
    pre = _prescreen_indices(arm, prescreen_n)
    pre_pts = [q[i] for i in pre]
    lm_idx = G.farthest_point_sample(arm["ca"], params["n_landmarks"])
    lm_pts = [arm["ca"][i] for i in lm_idx]

    md = field3.min_dist
    slack = field3.cell_slack
    accepted = []
    n_pre_reject = 0
    for _ in range(n_samples):
        d = L_min + (L_max - L_min) * (rng.random() ** (1.0 / 3.0))    # uniform in the shell VOLUME
        v = G.random_unit_vector(rng)
        ae = (a_t[0] + v[0] * d, a_t[1] + v[1] * d, a_t[2] + v[2] * d)
        if md(ae) - slack < params["pose_min_clearance_A"]:
            continue                                                    # the E3 ligand would be inside NR4A3
        R = G.quat_to_matrix(G.random_quaternion(rng))
        r0, r1, r2 = R
        px, py, pz = pivot
        ox, oy, oz = ae
        bad = False
        for (qx, qy, qz) in pre_pts:
            dx, dy, dz = qx - px, qy - py, qz - pz
            tx = r0[0] * dx + r0[1] * dy + r0[2] * dz + ox
            ty = r1[0] * dx + r1[1] * dy + r1[2] * dz + oy
            tz = r2[0] * dx + r2[1] * dy + r2[2] * dz + oz
            if md((tx, ty, tz)) - slack < hard:
                bad = True
                break
        if bad:
            n_pre_reject += 1
            continue
        n_hard = n_soft = n_contact = 0
        moved = []
        for (qx, qy, qz) in q:
            dx, dy, dz = qx - px, qy - py, qz - pz
            tp = (r0[0] * dx + r0[1] * dy + r0[2] * dz + ox,
                  r1[0] * dx + r1[1] * dy + r1[2] * dz + oy,
                  r2[0] * dx + r2[1] * dy + r2[2] * dz + oz)
            moved.append(tp)
            dd = md(tp) - slack
            if dd < hard:
                n_hard += 1
                if n_hard:
                    break
            elif dd < soft:
                n_soft += 1
            elif dd <= contact:
                n_contact += 1
        if n_hard or n_soft > max_soft or n_contact < min_contact:
            continue
        cb_moved = moved[arm["n_ca"]:]        # `query` is ca_list + cb_list; n_ca is stored, never inferred
        accepted.append({
            "R": R, "anchor_e3": ae, "span_A": d,
            "n_soft": n_soft, "n_contact": n_contact,
            "cb": cb_moved,
            "landmarks": G.transform_points(lm_pts, R, pivot, ae),
            "ring": G.transform_points([arm["ring"]], R, pivot, ae)[0] if arm["ring"] else None,
            "cullin": G.transform_points([arm["cullin"]], R, pivot, ae)[0] if arm["cullin"] else None,
            "tanchor": (G.transform_points([arm["tanchor"]], R, pivot, ae)[0]
                        if arm.get("tanchor") else None),
        })
    return accepted, {"n_samples": n_samples, "n_accepted": len(accepted),
                      "n_prescreen_rejected": n_pre_reject,
                      "acceptance_rate": round(len(accepted) / max(1, n_samples), 6)}


# ---------------------------------------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------------------------------------


class ResidueLookup:
    """Grid of target CB positions -> residue ids, so the chemistry-aware interface score can name the pairs."""

    def __init__(self, cb_by_res, aa_of, cell=6.0):
        self.cell = cell
        self.aa_of = aa_of
        self.grid = {}
        for rid, p in cb_by_res.items():
            if p is None:
                continue
            key = (int(p[0] // cell), int(p[1] // cell), int(p[2] // cell))
            self.grid.setdefault(key, []).append((rid, p))

    def near(self, p, cutoff):
        c = self.cell
        ci, cj, ck = int(p[0] // c), int(p[1] // c), int(p[2] // c)
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for rid, q in self.grid.get((ci + dx, cj + dy, ck + dz), ()):
                        if G.dist(p, q) <= cutoff:
                            out.append(rid)
        return out


def interface_fingerprint(placement, lookup, cutoff):
    """The set of TARGET residues this placement contacts — the basin descriptor. Cheap, low-dimensional, and
    exactly the variable the scored terms depend on."""
    s = set()
    for p in placement["cb"]:
        s.update(lookup.near(p, cutoff))
    return s


def interface_score(placement, arm, lookup, cutoff=8.0):
    """A UNITLESS contact score. It is NOT a free energy and no conclusion rests on a small difference in it.

    Preregistered, fixed weights (never fitted): packing +1 per residue pair, hydrophobic pair +1, salt bridge
    +2, like-charge pair -2, polar pair +0.5, soft clash -4. This exists to RANK placements WITHIN the set the
    categorical terms already selected — nr4a3-program-map.md's "interface thermodynamics used to RANK within the
    survivors, never to create selectivity on its own".
    """
    pack = hydro = salt = repul = polar = 0
    for p, a_aa in zip(placement["cb"], arm["aa"]):
        for rid in lookup.near(p, cutoff):
            t_aa = lookup.aa_of.get(rid, "X")
            pack += 1
            if a_aa in HYDROPHOBIC and t_aa in HYDROPHOBIC:
                hydro += 1
            if (a_aa in POSITIVE and t_aa in NEGATIVE) or (a_aa in NEGATIVE and t_aa in POSITIVE):
                salt += 1
            elif (a_aa in POSITIVE and t_aa in POSITIVE) or (a_aa in NEGATIVE and t_aa in NEGATIVE):
                repul += 1
            elif a_aa in POLAR and t_aa in POLAR:
                polar += 1
    total = pack + hydro + 2 * salt - 2 * repul + 0.5 * polar - 4 * placement["n_soft"]
    return {"total": round(total, 2), "pack": pack, "hydrophobic": hydro, "salt_bridge": salt,
            "like_charge": repul, "polar": polar, "soft_clash": placement["n_soft"]}


def paralogue_sterics(placement, field, params=PARAMS):
    """Re-evaluate ONE placement against a superposed paralogue: does the same orientation still fit?"""
    hard, soft, contact = params["hard_clash_A"], params["soft_clash_A"], params["contact_A"]
    md, slack = field.min_dist, field.cell_slack
    n_hard = n_soft = n_contact = 0
    for p in placement["cb"]:
        dd = md(p) - slack
        if dd < hard:
            n_hard += 1
        elif dd < soft:
            n_soft += 1
        elif dd <= contact:
            n_contact += 1
    return {"n_hard": n_hard, "n_soft": n_soft, "n_contact": n_contact}


def electrophile_reach(placement, pose, cysteines, params=PARAMS, full=True):
    """TERM (a). For each NR4A3 cysteine: can a linker tethered at (warhead exit vector, E3 ligand exit atom)
    put a pendant electrophile of reach `electrophile_arm_A` on its SG?

    ★★ CORRECTED 2026-07-25 — THIS FUNCTION USED THE *RELAXED* RULE AND THAT RULE CREDITS THE PENDANT WITH
    SHORTENING THE SPAN. The published criterion was the prolate-spheroid relaxation

        |q-a| + |q-b| <= n*rise + 2e      (`basin_geom.linker_can_visit`)

    which is a NECESSARY condition, not a sufficient one. Its loophole is visible in one line: by the triangle
    inequality |q-a| + |q-b| >= |a-b|, so for a nucleophile ON the anchor-anchor segment it reduces to
    `span <= n*rise + 2e` — i.e. it lets a pendant arm buy up to 2e/rise = 4.8 -> 5 backbone atoms of SPAN.
    No pendant can do that: the pendant hangs OFF the backbone, and the backbone still has to connect a to b,
    so `n*rise >= span` however long the arm is. Every term-(a) figure computed under the old rule is therefore
    a LOWER BOUND on the length a linker actually needs, understated by up to ~5 atoms.

    The replacement is `linker_design.min_linker_atoms_exact` — the shortest n for which some INTEGER branch
    position k admits a common point of the three balls B(a, k*rise), B(b, (n-k)*rise), B(q, e). That is the
    same kernel RUNG 5b hands to a chemist, so after this correction the repo holds **one** reach rule instead
    of two that disagree, and the number the gate is read on is the number a molecule would be built at.
    The superseded relaxed value is emitted beside it (`*_relaxed_superseded`) so the correction is auditable
    per record rather than only in prose.

    `full=False` computes only reachability at the sampling ceiling — used for the conserved-cysteine control
    set, which needs a fraction, not a length, and is ~10x cheaper.
    """
    a_t = tuple(pose["anchor_xyz"])
    a_e = placement["anchor_e3"]
    arm = params["electrophile_arm_A"]
    rise = params["linker_rise_per_atom_A"]
    n_ceiling = params["linker_max_atoms"]
    span = G.dist(a_t, a_e)
    floor_atoms = int(math.ceil(span / rise))
    out = []
    for c in cysteines:
        s = G.linker_visit_sum(a_t, a_e, c["xyz"])
        relaxed = int(math.ceil(max(0.0, s - 2.0 * arm) / rise))
        if full:
            exact = LD.min_linker_atoms_exact(a_t, a_e, c["xyz"], arm, rise,
                                              n_max=params["reach_scan_max_atoms"])
            reachable = exact is not None and exact <= n_ceiling
        else:
            exact = None
            reachable = LD.pendant_contactable(a_t, a_e, c["xyz"], n_ceiling, arm, rise)
        out.append({
            "uniprot_resid": c["uniprot_resid"], "unique": c.get("unique", True),
            "focal_sum_A": round(s, 2),
            "detour_A": round(G.linker_detour(a_t, a_e, c["xyz"]), 2),
            "span_A": round(span, 2),
            "span_floor_atoms": floor_atoms,
            "min_linker_atoms": exact,
            "min_linker_atoms_relaxed_superseded": relaxed,
            "reachable": reachable,
        })
    return out


def transfer_zone(placement, lys_by_species, rng, params=PARAMS, ring_r=None, transfer_d=None, n_e2=None):
    """TERM (b). Sample the E2~Ub catalytic-cysteine ARC about the transformed RING and ask which lysines of
    EACH species fall in the transfer zone.

    Returns, per species, the set of covered lysines. The discriminating question — the one that decides
    whether a basin is CATEGORICAL rather than merely favourable — is whether NR4A3's zone covers a unique
    lysine while the paralogues' zones cover NONE. Set membership, not energy; and honest limits are written
    into the output: real degraders often ubiquitinate several lysines, and lysine-less substrates can still
    be degraded via N-terminal/Ser/Thr/Cys ubiquitination, so this RAISES THE ODDS, it does not guarantee the
    paralogue is spared.
    """
    d = params["lysine_transfer_A"] if transfer_d is None else transfer_d
    obs = placement.get("tanchor")
    if obs is not None:
        # OBSERVED transfer point: the E2 catalytic cysteine seen in a solved assembly and carried rigidly
        # with the E3 body. No swing arc is modelled — instead the CRL's real conformational mobility is
        # represented by a small isotropic spread about the observed point, whose scale is a parameter and
        # is swept. This is strictly less modelling than the RING-arc fallback below.
        mob = params.get("observed_anchor_mobility_A", 0.0) if ring_r is None else max(0.0, ring_r - 25.0)
        covered = {sp: set() for sp in lys_by_species}
        unreliable = {sp: set() for sp in lys_by_species}
        n_e2s = params["n_e2_samples"] if n_e2 is None else n_e2
        d2 = d * d
        for i in range(n_e2s):
            if mob > 0.0:
                v = G.random_unit_vector(rng)
                rr = mob * (rng.random() ** (1.0 / 3.0))
                e2p = (obs[0] + v[0] * rr, obs[1] + v[1] * rr, obs[2] + v[2] * rr)
            else:
                e2p = obs
            for sp, lys in lys_by_species.items():
                for k in lys:
                    if G.dist2(e2p, k["xyz"]) <= d2:
                        covered[sp].add(k["local_resid"])
                        if k.get("position_reliable") is False:
                            unreliable[sp].add(k["local_resid"])
            if mob == 0.0:
                break
        return {"n_e2_samples": (n_e2s if mob > 0 else 1), "zone_model": "observed_catalytic_cys",
                "covered": {sp: sorted(s) for sp, s in covered.items()},
                "covered_but_unreliably_placed": {sp: sorted(s) for sp, s in unreliable.items() if s},
                "mobility_A": mob, "transfer_d_A": d}
    if placement["ring"] is None or placement["cullin"] is None:
        return None
    r = params["ring_to_e2_cys_A"] if ring_r is None else ring_r
    ring, cul = placement["ring"], placement["cullin"]
    try:
        axis = G.unit(G.sub(ring, cul))
    except ValueError:
        return None
    covered = {sp: set() for sp in lys_by_species}
    unreliable = {sp: set() for sp in lys_by_species}
    n_e2 = params["n_e2_samples"] if n_e2 is None else n_e2
    d2 = d * d
    for _ in range(n_e2):
        v = G.sample_spherical_cap(rng, axis, params["e2_cap_half_angle_deg"])
        e2 = (ring[0] + v[0] * r, ring[1] + v[1] * r, ring[2] + v[2] * r)
        for sp, lys in lys_by_species.items():
            cov = covered[sp]
            for k in lys:
                if G.dist2(e2, k["xyz"]) <= d2:
                    cov.add(k["local_resid"])
                    if k.get("position_reliable") is False:
                        unreliable[sp].add(k["local_resid"])
    return {"n_e2_samples": n_e2, "zone_model": "composed_ring_arc",
            "covered": {sp: sorted(s) for sp, s in covered.items()},
            "covered_but_unreliably_placed": {sp: sorted(s) for sp, s in unreliable.items() if s},
            "ring_to_e2_A": r, "transfer_d_A": d}


def classify_transfer(covered, unique_lys_ids, par_species=("NR4A1", "NR4A2")):
    """Term (b) SET-MEMBERSHIP category. Ordered exactly as nr4a3-program-map.md specifies (unique-only highest,
    unique+conserved next, conserved-only lowest), with the paralogue-bare refinement on top."""
    n3 = set(covered.get("NR4A3", []))
    uniq = n3 & unique_lys_ids
    cons = n3 - unique_lys_ids
    par_any = any(covered.get(sp) for sp in par_species)
    if not n3:
        return "none", 0
    if uniq and not cons and not par_any:
        return "unique_only_paralogues_bare", 5
    if uniq and not par_any:
        return "unique_plus_conserved_paralogues_bare", 4
    if uniq and not cons:
        return "unique_only", 3
    if uniq:
        return "unique_plus_conserved", 2
    return "conserved_only", 1


def basin_accessibility(spans, params=PARAMS):
    """nr4a3-program-map.md load-bearing piece 4 — `P(B_k | d, s)`, kept SEPARATE from the orientation's plausibility.

    For each candidate linker length, the mean worm-like-chain end-to-end density over the basin's
    anchor-anchor spans. A basin whose spans lie beyond a linker's contour length gets exactly zero: that
    linker cannot reach it, however good the interface looks.
    """
    lp = params["linker_persistence_length_A"]
    rise = params["linker_rise_per_atom_A"]
    prof = {}
    for n in range(params["linker_min_atoms"], params["linker_max_atoms"] + 1, 2):
        L = G.contour_length_from_atoms(n, rise)
        z = G.wlc_normalisation(L, lp)
        vals = [G.wlc_pdf(s, L, lp, norm_const=z) for s in spans]
        prof[n] = round(sum(vals) / len(vals), 9) if vals else 0.0
    best = max(prof, key=lambda n: prof[n]) if prof else None
    return {"density_by_linker_atoms": prof, "best_linker_atoms": best,
            "best_density": prof[best] if best is not None else 0.0,
            "persistence_length_A": lp}


# ---------------------------------------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------------------------------------


def run_arm_pose(arm, pose, ctx, rng, n_samples, params=PARAMS):
    """Search + cluster + score one (E3 arm, warhead exit-vector pose) combination."""
    placements, stats = sample_placements(arm, pose, ctx["field3"], rng, n_samples, params)
    if not placements:
        return {"pose_id": pose["pose_id"], "stats": stats, "basins": []}
    for pl in placements:
        pl["score3"] = interface_score(pl, arm, ctx["lookup3"])
        pl["fp"] = interface_fingerprint(pl, ctx["lookup3"], params["fingerprint_contact_A"])
    clusters = G.leader_cluster_by(placements, lambda p: p["fp"], G.jaccard_distance,
                                   1.0 - params["basin_jaccard_cutoff"],
                                   key=lambda p: p["score3"]["total"])
    floor = max(params["min_basin_members"], int(params["min_basin_fraction"] * len(placements)))
    clusters = [c for c in clusters if len(c) >= floor]
    clusters.sort(key=lambda c: -len(c))
    clusters = clusters[: params["max_basins_per_arm"]]

    unique_cys_ids = {c["local_resid"] for c in ctx["reactive"]["unique_cysteines"]}
    unique_lys_ids = {k["local_resid"] for k in ctx["reactive"]["unique_lysines"]}
    basins = []
    for bi, members in enumerate(clusters):
        rep = members[0]
        sample = members[: min(len(members), 60)]
        # --- term (a): unique cysteines AND the conserved-cysteine control set
        reach_unique = [electrophile_reach(m, pose, ctx["reactive"]["unique_cysteines"], params)
                        for m in sample]
        conserved_cys = [c for c in ctx["reactive"]["all_cysteines"] if c["local_resid"] not in unique_cys_ids]
        reach_conserved = [electrophile_reach(m, pose, conserved_cys, params, full=False) for m in sample]
        gate_n = params["linker_gate_atoms"]
        pendant_sweep = params["electrophile_pendant_sweep_A"]
        by_cys = {}
        a_t_pose = tuple(pose["anchor_xyz"])
        for mi_, row in enumerate(reach_unique):
            # zip, not a lookup: `electrophile_reach` returns one record per input cysteine IN ORDER, so the
            # SG coordinate the pendant sweep needs comes from the same object the record was built from.
            for r, cobj in zip(row, ctx["reactive"]["unique_cysteines"]):
                b = by_cys.setdefault(r["uniprot_resid"],
                                      {"hits": 0, "n": 0, "min_atoms": None,
                                       "focal_sums": [], "exacts": [], "relaxeds": [],
                                       "best_i": None, "best_key": None, "best_focal": float("inf"),
                                       "gate_by_pendant": {k: 0 for k in pendant_sweep}})
                b["n"] += 1
                b["hits"] += 1 if r["reachable"] else 0
                ex = r["min_linker_atoms"]
                if ex is not None and (b["min_atoms"] is None or ex < b["min_atoms"]):
                    b["min_atoms"] = ex
                b["focal_sums"].append(r["focal_sum_A"])
                b["exacts"].append(ex)
                b["relaxeds"].append(r["min_linker_atoms_relaxed_superseded"])
                # ★ EXEMPLAR SELECTION IS PART OF THE CORRECTION. The old exemplar was the member with the
                # smallest FOCAL SUM, which under the relaxed rule was the same thing as the shortest linker.
                # Under the exact rule it is not: the span enters, so the member closest to the cysteine can
                # need a LONGER chain than one slightly further away but better placed between the anchors.
                # The exemplar a chemist should design on is the member with the shortest EXACT requirement,
                # with the focal sum only breaking ties.
                key = (ex if ex is not None else 10 ** 6, r["focal_sum_A"])
                if b["best_key"] is None or key < b["best_key"]:
                    b["best_key"], b["best_i"], b["best_focal"] = key, mi_, r["focal_sum_A"]
                for pk, pe in pendant_sweep.items():
                    if LD.pendant_contactable(a_t_pose, sample[mi_]["anchor_e3"], cobj["xyz"],
                                              gate_n, pe, params["linker_rise_per_atom_A"]):
                        b["gate_by_pendant"][pk] += 1
        term_a = {}
        rise, e_arm = params["linker_rise_per_atom_A"], params["electrophile_arm_A"]
        for u, b in by_cys.items():
            profile, profile_old = {}, {}
            for n_at in params["linker_report_atoms"]:
                # Feasibility is MONOTONE in n (a longer chain grows every branch ball, so any witness at n is
                # still a witness at n+1), so the whole length profile is read off the per-member minimum —
                # no second scan, and no chance of the profile and the minimum disagreeing.
                profile[n_at] = round(sum(1 for e in b["exacts"] if e is not None and e <= n_at)
                                      / len(b["exacts"]), 3)
                profile_old[n_at] = round(sum(1 for e in b["relaxeds"] if e <= n_at) / len(b["relaxeds"]), 3)
            term_a[f"C{u}"] = {
                "fraction_reachable_at_sampling_ceiling": round(b["hits"] / b["n"], 3),
                "fraction_reachable_by_linker_atoms": profile,
                "fraction_reachable_at_gate": profile[gate_n],
                "min_linker_atoms": b["min_atoms"],
                "_rule": "EXACT: shortest n with an integer branch position k whose three balls "
                         "B(a,k*rise), B(b,(n-k)*rise), B(SG,%.1f) share a point "
                         "(linker_design.min_linker_atoms_exact). null = not reachable within %d atoms."
                         % (e_arm, params["reach_scan_max_atoms"]),
                # ★ THE SUPERSEDED RULE, CARRIED PER RECORD (CLAUDE.md §1.3: a corrected number keeps its old
                # value registered). These are what RUNG 5a published on 2026-07-25; they credit the pendant
                # with shortening the anchor-anchor SPAN and are LOWER BOUNDS, low by up to 2e/rise ~ 5 atoms.
                "min_linker_atoms_relaxed_superseded": min(b["relaxeds"]),
                "fraction_reachable_by_linker_atoms_relaxed_superseded": profile_old,
                "fraction_reachable_at_gate_relaxed_superseded": profile_old[gate_n],
                # SENSITIVITY, NOT THE GATE: the same 12-atom question asked with each named building block.
                "fraction_reachable_at_gate_by_pendant": {
                    k: round(v / b["n"], 3) for k, v in sorted(b["gate_by_pendant"].items(),
                                                               key=lambda kv: pendant_sweep[kv[0]])},
                "median_focal_sum_A": round(sorted(b["focal_sums"])[len(b["focal_sums"]) // 2], 2),
                # ★ ADDED FOR RUNG 5b (additive only; nothing above is changed). `min_linker_atoms` is a
                # BEST-OF-N over this basin's sampled members, and the member that achieves it is NOT the
                # basin's representative — at the representative placement of all five confirmed meta-basins
                # the C397 requirement is 16-33 atoms against a reported 8-12. A chemist cannot design at a
                # statistic, so the placement that actually achieves the minimum is emitted here, in full, as
                # the geometry RUNG 5b builds the covalent constructs on.
                "exemplar_placement": ({
                    "member_index": b["best_i"],
                    "exact_atoms": b["best_key"][0] if b["best_key"][0] < 10 ** 6 else None,
                    "focal_sum_A": round(b["best_focal"], 3),
                    "anchor_e3_xyz": [round(c, 3) for c in sample[b["best_i"]]["anchor_e3"]],
                    "span_A": round(sample[b["best_i"]]["span_A"], 3),
                    "landmarks": [[round(c, 3) for c in p] for p in sample[b["best_i"]]["landmarks"]],
                    "ring_xyz": ([round(c, 3) for c in sample[b["best_i"]]["ring"]]
                                 if sample[b["best_i"]]["ring"] else None),
                    "transfer_anchor_xyz": ([round(c, 3) for c in sample[b["best_i"]]["tanchor"]]
                                            if sample[b["best_i"]].get("tanchor") else None),
                    "_reading": "the sampled member of this basin needing the SHORTEST EXACT linker to this "
                                "cysteine (focal sum breaks ties). Its landmarks recover the full rigid "
                                "transform (Horn), so the exit-vector geometry and the exact three-ball "
                                "branch-position window can be computed on it. It is a best-of-N member, so "
                                "it is the OPTIMISTIC end of the basin and must be reported as such.",
                    "_selection_changed_2026_07_25": "was the member with the smallest FOCAL SUM. Under the "
                                "relaxed rule those coincided; under the exact rule the span enters, so the "
                                "member nearest the cysteine is not always the one needing the shortest chain.",
                } if b["best_i"] is not None else None),
            }
        cons_reachable = sum(1 for row in reach_conserved for r in row if r["reachable"])
        cons_total = sum(len(row) for row in reach_conserved) or 1

        # --- term (b): transfer zone, at the default and swept
        tz = [transfer_zone(m, ctx["lys_by_species"], rng, params) for m in sample[:40]]
        tz = [t for t in tz if t]
        cat, rank = ("no_ring_geometry", -1)
        tz_summary = None
        if tz:
            agg = {sp: set() for sp in ctx["lys_by_species"]}
            for t in tz:
                for sp, ids in t["covered"].items():
                    agg[sp].update(ids)
            per_member = [classify_transfer(t["covered"], unique_lys_ids) for t in tz]
            best_rank = max(r for _, r in per_member)
            cat = next(c for c, r in per_member if r == best_rank)
            rank = best_rank
            nm = len(per_member)
            tz_summary = {
                "_reading": "Rotation of the E3 about the tether that leaves the interface unchanged is a "
                            "REAL degree of freedom the complex explores, so it is reported as a FREQUENCY "
                            "within the basin rather than split into separate basins. A basin whose transfer "
                            "zone covers a unique lysine in only a small fraction of its placements is a "
                            "weaker nomination than one where it does so in most.",
                "union_covered": {sp: sorted(s) for sp, s in agg.items()},
                "union_covered_uniprot_nr4a3": sorted(x + UNIPROT_OFFSET for x in agg.get("NR4A3", [])),
                "unique_lysines_covered_nr4a3": sorted(
                    x + UNIPROT_OFFSET for x in (agg.get("NR4A3", set()) & unique_lys_ids)),
                "fraction_members_unique_covering": round(sum(1 for _, r in per_member if r >= 3) / nm, 3),
                "fraction_members_unique_and_paralogues_bare": round(
                    sum(1 for _, r in per_member if r >= 4) / nm, 3),
                "fraction_members_any_nr4a3_lysine": round(sum(1 for _, r in per_member if r >= 1) / nm, 3),
                "category_counts": {c: sum(1 for cc, _ in per_member if cc == c)
                                    for c in {cc for cc, _ in per_member}},
                "best_category": cat, "best_rank": rank,
                "_best_rank_warning": "best_rank is a BEST-OF-N statistic — the maximum over this basin's "
                                      "sampled placements, each itself a maximum over the sampled E2 arc — "
                                      "so it is inflated by construction, exactly the winner's-curse "
                                      "artifact a raw Pareto set admits. The unbiased quantities are the "
                                      "fraction_members_* fields; read those, and treat any count built on "
                                      "best_rank as an UPPER BOUND.",
            }
            # sensitivity: does the category survive the swept transfer distance and RING-E2 radius?
            sens = {}
            for d in params["lysine_transfer_sweep_A"]:
                for rr in params["ring_to_e2_cys_range_A"]:
                    ts = [transfer_zone(m, ctx["lys_by_species"], rng, params, ring_r=rr, transfer_d=d,
                                        n_e2=24) for m in sample[:8]]
                    ts = [t for t in ts if t]
                    if not ts:
                        continue
                    ranks = [classify_transfer(t["covered"], unique_lys_ids)[1] for t in ts]
                    sens[f"d{d}_r{rr}"] = max(ranks)
            tz_summary["sensitivity_best_rank"] = sens
            # TWO robustness standards, both reported, because one of the swept values is not a live
            # alternative any more. The 10.0 A transfer distance was this file's own ASSUMPTION and the
            # solved assembly measured 17.1 A, so requiring the category to survive 10.0 A is requiring it to
            # survive a refuted parameter — which no basin can do. Narrowing the sweep after seeing a basin
            # fail it would be moving the goalpost, so instead BOTH are reported and the reader can apply
            # either: the full sweep (including the superseded value, the strictest possible reading) and the
            # calibrated range around the measurement.
            cal_lo, cal_hi = 14.0, 21.0
            cal = {k: v for k, v in sens.items()
                   if cal_lo <= float(k.split("_")[0][1:]) <= cal_hi}
            tz_summary["sensitivity_robust_full_sweep"] = bool(sens) and min(sens.values()) >= 3
            tz_summary["sensitivity_robust_calibrated_range"] = bool(cal) and min(cal.values()) >= 3
            tz_summary["sensitivity_robust"] = tz_summary["sensitivity_robust_full_sweep"]
            tz_summary["_sensitivity_note"] = (
                "full_sweep spans %s A and includes the SUPERSEDED 10.0 A assumption; "
                "calibrated_range spans %.0f-%.0f A around the 17.1 A measured in a solved ubiquitylation "
                "assembly. Both are reported; neither was chosen after seeing a result."
                % (params["lysine_transfer_sweep_A"], cal_lo, cal_hi))
            tz_summary["paralogue_lysines_covered_but_unreliably_placed"] = sorted(
                {f"{sp}:{x}" for t in tz for sp, ids in
                 (t.get("covered_but_unreliably_placed") or {}).items() for x in ids if sp != "NR4A3"})

        # --- paralogue sterics + score on the SAME placements (matched)
        par = {}
        for sp in ("NR4A1", "NR4A2"):
            st = [paralogue_sterics(m, ctx["fields"][sp], params) for m in sample]
            sc = [interface_score(m, arm, ctx["lookups"][sp])["total"] for m in sample]
            par[sp] = {
                "mean_contacts": round(sum(s["n_contact"] for s in st) / len(st), 1),
                "mean_hard_clashes": round(sum(s["n_hard"] for s in st) / len(st), 2),
                "frac_sterically_admissible": round(sum(1 for s in st if s["n_hard"] == 0) / len(st), 3),
                "mean_interface_score": round(sum(sc) / len(sc), 2),
            }
        s3 = [m["score3"]["total"] for m in sample]
        mean3 = sum(s3) / len(s3)
        delta = mean3 - max(par["NR4A1"]["mean_interface_score"], par["NR4A2"]["mean_interface_score"])

        spans = [m["span_A"] for m in members]
        _sorted_spans = sorted(spans)
        # the basin's PATCH: target residues contacted by >= half its placements, and their centroid
        counts = {}
        for m in members:
            for rid in m["fp"]:
                counts[rid] = counts.get(rid, 0) + 1
        core_fp = sorted(r for r, c in counts.items() if c >= 0.5 * len(members))
        patch_pts = [ctx["m3_cb"][r] for r in core_fp if ctx["m3_cb"].get(r)]
        basins.append({
            "basin_id": f"{arm['arm_id']}|{pose['pose_id']}|b{bi}",
            "arm_id": arm["arm_id"], "pose_id": pose["pose_id"],
            "n_members": len(members),
            "population_fraction": round(len(members) / len(placements), 4),
            "interface_patch": {
                "core_residues_local": core_fp,
                "core_residues_uniprot": [r + UNIPROT_OFFSET for r in core_fp],
                "n_core_residues": len(core_fp),
                "patch_centroid": [round(c, 2) for c in G.centroid(patch_pts)] if patch_pts else None,
                "_definition": "target residues whose CB lies within %.1f A of an E3 CB in at least half the "
                               "basin's placements" % params["fingerprint_contact_A"],
            },
            "representative": {
                "anchor_e3_xyz": [round(c, 2) for c in rep["anchor_e3"]],
                "span_A": round(rep["span_A"], 2),
                "ring_xyz": [round(c, 2) for c in rep["ring"]] if rep["ring"] else None,
                "landmarks": [[round(c, 2) for c in p] for p in rep["landmarks"]],
            },
            "span_A": {"min": round(min(spans), 2), "median": round(sorted(spans)[len(spans) // 2], 2),
                       "max": round(max(spans), 2)},
            # ★ ADDED FOR RUNG 5b (additive only). Deciles of the anchor-anchor span, so accessibility can be
            # recomputed as a PROBABILITY over the basin's span window instead of a mean density. The density
            # form's argmax is censored at the top of its scan grid — `best_linker_atoms` reads 19 (the last
            # scanned value) on 188 of 192 basins, and for a 20 A span the true argmax is ~53 backbone atoms.
            # A grid edge is not an optimum, and three quantiles are not enough to integrate over.
            # (sorted ONCE, hoisted — the first version re-sorted inside the comprehension, eleven times per
            # basin. Same output, and the cost was never the reason a run is slow: everything added here
            # touches only the ~10^3 ACCEPTED, CLUSTERED members, against the ~10^6 sampled placements x 44
            # prescreen points the search already does, so the additions are bounded below ~0.001 % of the
            # run. A CI run 28 % longer than its reference is runner variance, not this.)
            "span_A_deciles": [round(_sorted_spans[min(len(spans) - 1, int(q * len(spans) / 10.0))], 2)
                               for q in range(11)],
            "min_linker_atoms_for_span": int(math.ceil(min(spans) / params["linker_rise_per_atom_A"])),
            "stability_surrogate": {
                "_warning": "UNITLESS contact score, NOT a free energy. It ranks within the categorically "
                            "selected set; no conclusion rests on a small difference in it.",
                "nr4a3_mean": round(mean3, 2),
                "nr4a3_components_representative": rep["score3"],
                "paralogues": par,
                "nominal_delta_vs_best_paralogue": round(delta, 2),
            },
            "term_a_electrophile_reach": {
                "unique_cysteines": term_a,
                "conserved_cysteine_control_fraction_reachable": round(cons_reachable / cons_total, 3),
                "_paralogue_note": "NR4A1/NR4A2 carry NO nucleophile at these aligned positions (C397 -> "
                                   "N363/S363, C420 -> Q388/A389, C559 -> Q528/Q528), so term (a) is "
                                   "categorically zero for both paralogues by SEQUENCE, independent of any "
                                   "geometry computed here.",
                "_chemistry_note": "Prefer a REVERSIBLE-covalent (cyanoacrylamide-type) handle: an "
                                   "irreversible adduct makes the degrader stoichiometric and forfeits the "
                                   "catalytic turnover that makes a degrader worth building.",
            },
            "term_b_transfer_zone": tz_summary,
            "accessibility_P_basin_given_linker": basin_accessibility(spans, params),
            "mean_contacts_nr4a3": round(sum(m["n_contact"] for m in sample) / len(sample), 1),
        })
    # ---- THE NULL. Without it, "this basin's transfer zone covers K572" is uninterpretable: if ANY
    # linker-feasible, clash-free placement covers a unique lysine at the same rate, the term has no
    # discriminating power and a basin that scores well is just a placement that exists. The background is
    # computed over the UNCLUSTERED accepted set — the same population the basins were drawn from, with the
    # clustering step (the only thing that could enrich it) removed.
    bg_n = min(len(placements), 200)
    bg = [transfer_zone(m, ctx["lys_by_species"], rng, params) for m in placements[:bg_n]]
    bg = [t for t in bg if t]
    background = None
    if bg:
        cls = [classify_transfer(t["covered"], unique_lys_ids) for t in bg]
        background = {
            "n_placements_scored": len(bg),
            "fraction_unique_covering": round(sum(1 for _, r in cls if r >= 3) / len(cls), 3),
            "fraction_unique_and_paralogues_bare": round(sum(1 for _, r in cls if r >= 4) / len(cls), 3),
            "fraction_any_nr4a3_lysine": round(sum(1 for _, r in cls if r >= 1) / len(cls), 3),
            "_reading": "the rate at which ANY accepted (linker-feasible, clash-free, real-interface) "
                        "placement covers a paralogue-unique lysine. A basin only carries term-(b) "
                        "information insofar as it EXCEEDS this; a basin at the background rate is a "
                        "placement that exists, not a mechanism.",
        }
        for b in basins:
            tz = b.get("term_b_transfer_zone")
            if tz:
                tz["enrichment_over_background"] = (
                    round(tz["fraction_members_unique_covering"] / background["fraction_unique_covering"], 2)
                    if background["fraction_unique_covering"] > 0 else None)
                tz["exceeds_background"] = (
                    tz["fraction_members_unique_covering"] > background["fraction_unique_covering"])
    return {"pose_id": pose["pose_id"], "stats": stats, "basins": basins,
            "term_b_background_null": background}


def marginalise_over_poses(per_pose, params=PARAMS):
    """TERM (d). Cluster basins ACROSS the warhead-pose ensemble and report the surviving fraction.

    Legitimate because the target is fixed in one frame and only the exit-vector anchor moves between poses,
    so two basins from different poses are directly comparable as PLACEMENTS. A meta-basin present in one pose
    out of twelve is a pose artefact; one present in most poses is a real feature of the target surface.
    """
    flat = [b for p in per_pose for b in p["basins"]]
    if not flat:
        return []
    n_poses = len({p["pose_id"] for p in per_pose})
    metas = G.leader_cluster_by(
        flat, lambda b: set(b["interface_patch"]["core_residues_local"]), G.jaccard_distance,
        1.0 - params["meta_basin_jaccard_cutoff"], key=lambda b: b["n_members"])
    out = []
    for mi, members in enumerate(metas):
        poses = sorted({b["pose_id"] for b in members})
        rep = members[0]
        term_a_union = {}
        for b in members:
            for cys, v in (b["term_a_electrophile_reach"]["unique_cysteines"] or {}).items():
                cur = term_a_union.setdefault(cys, {"max_fraction_reachable": 0.0,
                                                    "max_fraction_reachable_at_gate": 0.0,
                                                    "min_linker_atoms": None,
                                                    "min_linker_atoms_relaxed_superseded": 10 ** 6,
                                                    "max_fraction_reachable_at_gate_relaxed_superseded": 0.0,
                                                    "max_fraction_reachable_at_gate_by_pendant": {},
                                                    "n_poses_reachable": 0})
                cur["max_fraction_reachable"] = max(cur["max_fraction_reachable"],
                                                    v["fraction_reachable_at_sampling_ceiling"])
                cur["max_fraction_reachable_at_gate"] = max(cur["max_fraction_reachable_at_gate"],
                                                            v["fraction_reachable_at_gate"])
                if v["min_linker_atoms"] is not None:
                    cur["min_linker_atoms"] = (v["min_linker_atoms"] if cur["min_linker_atoms"] is None
                                               else min(cur["min_linker_atoms"], v["min_linker_atoms"]))
                cur["min_linker_atoms_relaxed_superseded"] = min(
                    cur["min_linker_atoms_relaxed_superseded"], v["min_linker_atoms_relaxed_superseded"])
                cur["max_fraction_reachable_at_gate_relaxed_superseded"] = max(
                    cur["max_fraction_reachable_at_gate_relaxed_superseded"],
                    v["fraction_reachable_at_gate_relaxed_superseded"])
                for pk, pv in v["fraction_reachable_at_gate_by_pendant"].items():
                    cur["max_fraction_reachable_at_gate_by_pendant"][pk] = max(
                        cur["max_fraction_reachable_at_gate_by_pendant"].get(pk, 0.0), pv)
                if v["fraction_reachable_at_gate"] > 0:
                    cur["n_poses_reachable"] += 1
                # ★ ADDED FOR RUNG 5b: carry the member placement that achieves the union's minimum, tagged
                # with the basin and pose it came from — RUNG 5b has to know WHICH pose's exit-vector anchor
                # its covalent construct is designed against, because that is the pose conditionality the
                # construct inherits. Selected on the EXACT requirement since 2026-07-25 (focal sum breaks
                # ties), matching the per-basin exemplar rule.
                ex = v.get("exemplar_placement")
                if ex is not None:
                    key = (ex.get("exact_atoms") if ex.get("exact_atoms") is not None else 10 ** 6,
                           ex["focal_sum_A"])
                    if key < cur.get("_best_key", (10 ** 9, 10 ** 9)):
                        cur["_best_key"] = key
                        cur["_best_focal"] = ex["focal_sum_A"]
                        cur["exemplar_placement"] = dict(ex, basin_id=b["basin_id"], pose_id=b["pose_id"])
        tz_ranks = [b["term_b_transfer_zone"]["best_rank"] for b in members if b["term_b_transfer_zone"]]
        uniq_cov = sorted({u for b in members if b["term_b_transfer_zone"]
                           for u in b["term_b_transfer_zone"]["unique_lysines_covered_nr4a3"]})
        tz_fracs = [b["term_b_transfer_zone"]["fraction_members_unique_covering"]
                    for b in members if b["term_b_transfer_zone"]]
        tz_bare = [b["term_b_transfer_zone"]["fraction_members_unique_and_paralogues_bare"]
                   for b in members if b["term_b_transfer_zone"]]
        patch = sorted(set().union(*[set(b["interface_patch"]["core_residues_local"]) for b in members]))
        out.append({
            "meta_basin_id": f"{rep['arm_id']}|M{mi}",
            "arm_id": rep["arm_id"],
            "interface_patch_uniprot": [r + UNIPROT_OFFSET for r in patch],
            "term_b_mean_fraction_unique_covering": round(sum(tz_fracs) / len(tz_fracs), 3) if tz_fracs else 0.0,
            "term_b_exceeds_background": any(
                (b["term_b_transfer_zone"] or {}).get("exceeds_background") for b in members),
            "term_b_max_enrichment_over_background": max(
                [(b["term_b_transfer_zone"] or {}).get("enrichment_over_background") or 0.0
                 for b in members], default=0.0),
            "term_b_mean_fraction_paralogues_bare": round(sum(tz_bare) / len(tz_bare), 3) if tz_bare else 0.0,
            "n_poses_present": len(poses), "n_poses_total": n_poses,
            "pose_surviving_fraction": round(len(poses) / n_poses, 3),
            "poses": poses,
            "n_member_basins": len(members),
            "total_members": sum(b["n_members"] for b in members),
            "representative_basin_id": rep["basin_id"],
            "representative": rep["representative"],
            "term_a_union": term_a_union,
            "term_b_best_rank": max(tz_ranks) if tz_ranks else -1,
            "term_b_unique_lysines_covered": uniq_cov,
            "stability_surrogate_nominal_delta_range": [
                round(min(b["stability_surrogate"]["nominal_delta_vs_best_paralogue"] for b in members), 2),
                round(max(b["stability_surrogate"]["nominal_delta_vs_best_paralogue"] for b in members), 2)],
            "best_accessibility": max(
                (b["accessibility_P_basin_given_linker"]["best_density"] for b in members), default=0.0),
            "best_linker_atoms": rep["accessibility_P_basin_given_linker"]["best_linker_atoms"],
        })
    out.sort(key=lambda m: (-m["pose_surviving_fraction"], -m["total_members"]))
    return out


def term_a_feasibility_envelope(poses, cysteines, field3, rng, params=PARAMS, n_mc=20000):
    """An E3-INDEPENDENT UPPER BOUND on term (a): at each linker length, what fraction of possible E3-anchor
    placements is compatible with routing a pendant electrophile onto each NR4A3 cysteine?

    WHY THIS IS WORTH ITS OWN ANALYSIS. If term (a) comes back empty, there are two completely different
    reasons and the basin search alone cannot tell them apart:
      (i) the geometry is fine but no E3 body happens to dock in the region where the linker could reach the
          cysteine — a fact about the RECRUITER, fixable by trying another one; or
      (ii) no linker of any credible length can reach that cysteine from the pocket exit vector at all while
          also spanning to an E3 — a fact about the TARGET, which no recruiter choice can fix.
    Distinguishing them is the difference between "widen the E3 panel" and "this mechanism is closed", and it
    is the sort of thing a negative result has to state to be worth publishing.

    The computation needs no E3. Fixing the warhead exit anchor `a`, an n-atom linker with a pendant arm of
    reach e can put the electrophile on the cysteine SG for an E3 anchor at `b` iff some integer branch
    position k admits a common point of B(a, k*rise), B(b, (n-k)*rise), B(SG, e); and `b` must itself be a
    spannable, non-overlapping anchor position. The fraction of the reach shell satisfying both is estimated
    by Monte Carlo, with anchor positions inside the protein rejected exactly as the search rejects them.

    ★ CORRECTED 2026-07-25 alongside `electrophile_reach`. This function used the same relaxed criterion
    (`|SG-a| + |SG-b| <= L + 2e`). Note that the envelope was ALREADY span-correct in one respect the basin
    search was not — it draws the E3 anchor at radius r <= L, so it never admitted an anchor further away than
    the linker is long — which is precisely why the two disagreed and why the disagreement is worth recording:
    the same rule was written twice and only one copy carried the constraint.
    """
    rise, e_arm = params["linker_rise_per_atom_A"], params["electrophile_arm_A"]
    lo_span = G.contour_length_from_atoms(params["linker_min_atoms"], rise)
    out = {}
    for cys in cysteines:
        sg = cys["xyz"]
        per_len = {}
        for n_at in params["linker_report_atoms"]:
            L = G.contour_length_from_atoms(n_at, rise)
            # EARLY-OUT ONLY, and deliberately the LOOSE bound: `L + 2e` is weaker than the exact criterion
            # below, so anything it lets through is still tested properly. Using it here cannot admit a false
            # positive; it only skips poses that are hopeless on the first leg alone. (The exact necessary
            # bound would be `n*rise + e`, but tightening a pure early-out buys nothing and would have to be
            # re-derived if the branch model changed.)
            budget = L + 2.0 * e_arm
            feas_by_pose = []
            for pose in poses:
                a = tuple(pose["anchor_xyz"])
                d_aS = G.dist(a, sg)
                if d_aS > budget:                       # the cysteine is beyond reach from this anchor alone
                    feas_by_pose.append(0.0)
                    continue
                hit = tot = 0
                for _ in range(n_mc // max(1, len(poses))):
                    r = lo_span + (L - lo_span) * (rng.random() ** (1.0 / 3.0)) if L > lo_span else lo_span
                    v = G.random_unit_vector(rng)
                    b = (a[0] + v[0] * r, a[1] + v[1] * r, a[2] + v[2] * r)
                    if field3.min_dist(b) - field3.cell_slack < params["pose_min_clearance_A"]:
                        continue                        # an E3 anchor inside the target is not a placement
                    tot += 1
                    if LD.pendant_contactable(a, b, sg, n_at, e_arm, rise):
                        hit += 1
                feas_by_pose.append(hit / tot if tot else 0.0)
            per_len[n_at] = {
                "mean_fraction_of_anchor_space": round(sum(feas_by_pose) / len(feas_by_pose), 4),
                "max_over_poses": round(max(feas_by_pose), 4),
                "n_poses_with_any": sum(1 for f in feas_by_pose if f > 0),
            }
        first_open = next((n for n in params["linker_report_atoms"]
                           if per_len[n]["max_over_poses"] > 0), None)
        out[f"C{cys['uniprot_resid']}"] = {
            "dist_exit_anchor_to_SG_A": {
                "min": round(min(G.dist(tuple(p["anchor_xyz"]), sg) for p in poses), 2),
                "max": round(max(G.dist(tuple(p["anchor_xyz"]), sg) for p in poses), 2)},
            "by_linker_atoms": per_len,
            "shortest_linker_with_any_feasible_anchor": first_open,
            "geometrically_closed": first_open is None,
        }
    return {
        "_what": "E3-INDEPENDENT upper bound on term (a). A basin can only do as well as this; if the envelope "
                 "is empty at a given linker length, no recruiter choice can rescue that cysteine at that "
                 "length, and the failure is a fact about the TARGET rather than about the E3 panel.",
        "_method": "EXACT three-ball criterion (linker_design.pendant_contactable): some integer branch "
                   "position k gives B(a,k*rise), B(b,(n-k)*rise), B(SG,e) a common point. Monte-Carlo over "
                   "E3-anchor positions b in the reach shell, rejecting positions inside the protein exactly "
                   "as the search does. CORRECTED 2026-07-25 from the relaxed |SG-a| + |SG-b| <= L + 2e.",
        "per_cysteine": out,
    }


def tier2_verdict(metas, per_arm_basins):
    """nr4a3-program-map.md kill-switch TIER 2: 'No basin exploits a categorical handle AND none even nominally
    discriminates NR4A3 => STOP cheaply.'

    Read exactly as written — it is a CONJUNCTION, so a GO needs only one of the two limbs. And the asymmetry
    that makes this usable is stated in the verdict itself: the categorical limbs are geometric set-membership
    questions, which cheap scoring answers reliably; the nominal limb is a cheap ENERGY difference, which it
    does not, so a nominal-only GO is explicitly weaker than a categorical GO.
    """
    cat_a = [m for m in metas
             if any(v.get("max_fraction_reachable_at_gate", 0.0) > 0 for v in m["term_a_union"].values())]
    # Term (b) counts only where the basin BEATS the null. A basin whose transfer zone covers a unique lysine
    # at the same rate as any linker-feasible placement carries no information, and letting it through would
    # turn "a placement exists" into "a mechanism was found".
    cat_b = [m for m in metas if m["term_b_best_rank"] >= 3 and m.get("term_b_exceeds_background", True)]
    nominal = [m for m in metas if m["stability_surrogate_nominal_delta_range"][1] > 0]
    exploits_categorical = bool(cat_a or cat_b)
    discriminates_nominally = bool(nominal)
    go = exploits_categorical or discriminates_nominally
    if exploits_categorical:
        basis = "CATEGORICAL"
    elif discriminates_nominally:
        basis = "NOMINAL_ONLY"
    else:
        basis = "NONE"
    return {
        "gate": "TIER 2 — basin nomination",
        "rule": "No basin exploits a categorical handle AND none even nominally discriminates NR4A3 => STOP.",
        "n_meta_basins": len(metas),
        "n_basins_total": per_arm_basins,
        "n_exploiting_term_a_electrophile_reach": len(cat_a),
        "n_exploiting_term_b_unique_lysine_zone": len(cat_b),
        "_term_b_count_is_an_upper_bound": (
            "counted on term_b_best_rank, a BEST-OF-N statistic that is inflated by construction. Requiring "
            "the basin to beat the null keeps the count meaningful, but it remains optimistic; the unbiased "
            "per-basin quantities are the fraction_members_* fields."),
        "n_nominally_discriminating": len(nominal),
        "basis": basis,
        "pass": go,
        "verdict": (
            "GO — at least one basin exploits a CATEGORICAL handle (paralogue-unique nucleophile within "
            "linker reach and/or a transfer zone covering a paralogue-unique lysine). Proceed to RUNG 5a-KS, "
            "the ligand-side double-difference causal test, on the nominated basin(s)."
            if basis == "CATEGORICAL" else
            "WEAK GO — no basin exploits a categorical handle, but at least one nominally favours NR4A3 on "
            "the cheap contact score. This limb is the MARGINAL axis, which needs ~2.0 kcal/mol of true "
            "margin against a best-case resolvable 1.12 — a cheap contact-score difference is NOT evidence "
            "of it. Treat as a nomination of last resort and expect a negative."
            if basis == "NOMINAL_ONLY" else
            "NO-GO — no basin exploits a categorical handle and none even nominally discriminates NR4A3. "
            "STOP cheaply: no linker matrix, no ensemble refinement, no flagship spend. Publish the honest "
            "negative, which is now stronger because it rules out the mechanisms individually."),
        "asymmetry_note": (
            "Cheap scoring has poor S/N for a ~1 kcal/mol ENERGY difference, so it only nominates. But 'does "
            "this basin place an electrophile at C397 / does its transfer zone cover K572?' is a GEOMETRIC "
            "set-membership question, which cheap scoring answers reliably. A gross absence of signal is an "
            "informative NO-GO; the gate is not trusted to kill a real small wedge."),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--struct-dir", default=os.path.join(REPO, "results", "nr4a3-matrix"))
    ap.add_argument("--registry", default=os.path.join(HERE, "nr4a3-e3-arm-registry.json"))
    ap.add_argument("--unique-json", default=os.path.join(HERE, "nr4a-paralogue-unique-residues.json"))
    # ★ NOT a plain default. `--self-test` runs a SYNTHETIC E3, and with one shared default path it wrote its
    # synthetic result straight over the committed production artifact — observed 2026-07-25, twice in one
    # session, and only caught because `git status` was checked. A lane that ran the self-test and then
    # committed would have replaced the definitive 12-pose result with synthetic numbers under a filename that
    # every downstream consumer (RUNG 5b, nr4a3-program-map.md's Tier-2 block) reads without question. So the self-test
    # gets its own file unless an explicit --out says otherwise.
    ap.add_argument("--out", default=None,
                    help="output path (default: nr4a3-orientation-basins.json, or "
                         "nr4a3-orientation-basins-selftest.json under --self-test)")
    ap.add_argument("--samples", type=int, default=250000, help="rigid-body samples per (arm x pose)")
    ap.add_argument("--n-poses", type=int, default=12, help="size of the warhead exit-vector pose ensemble")
    ap.add_argument("--seed", type=int, default=20260725)
    ap.add_argument("--self-test", action="store_true",
                    help="run against a SYNTHETIC E3 (no registry, no network) to exercise the pipeline")
    ap.add_argument("--arms", default="", help="comma-separated subset of registry arm ids")
    args = ap.parse_args(argv)
    if args.out is None:
        args.out = os.path.join(HERE, "nr4a3-orientation-basins-selftest.json" if args.self_test
                                else "nr4a3-orientation-basins.json")

    t0 = time.time()
    rng = random.Random(args.seed)

    # ---- target side
    m3 = load_paralogue(os.path.join(args.struct_dir, "nr4a3-opened.pdb"))
    m1 = superpose_paralogue(load_paralogue(os.path.join(args.struct_dir, "nr4a1-opened.pdb")), m3)
    m2 = superpose_paralogue(load_paralogue(os.path.join(args.struct_dir, "nr4a2-opened.pdb")), m3)
    print(f"[basin] superposed NR4A1 onto NR4A3: {m1['superposition']}", flush=True)
    print(f"[basin] superposed NR4A2 onto NR4A3: {m2['superposition']}", flush=True)

    fields = {"NR4A3": G.SquaredDistanceField(m3["heavy_xyz"], cell=0.9, clamp=8.0),
              "NR4A1": G.SquaredDistanceField(m1["heavy_xyz"], cell=0.9, clamp=8.0),
              "NR4A2": G.SquaredDistanceField(m2["heavy_xyz"], cell=0.9, clamp=8.0)}
    lookups = {"NR4A3": ResidueLookup(m3["cb"], m3["aa_of"]),
               "NR4A1": ResidueLookup(m1["cb"], m1["aa_of"]),
               "NR4A2": ResidueLookup(m2["cb"], m2["aa_of"])}
    reactive = load_reactive_map(args.unique_json, m3)
    lys_by_species = {"NR4A3": reactive["all_lysines"],
                      "NR4A1": paralogue_lysines(m1), "NR4A2": paralogue_lysines(m2)}
    print(f"[basin] pocket centroid {[round(c,2) for c in reactive['pocket_centroid']]}  "
          f"unique Cys {[c['uniprot_resid'] for c in reactive['unique_cysteines']]}  "
          f"unique Lys {[k['uniprot_resid'] for k in reactive['unique_lysines']]}  "
          f"lysines NR4A3/1/2 = {len(lys_by_species['NR4A3'])}/{len(lys_by_species['NR4A1'])}/"
          f"{len(lys_by_species['NR4A2'])}", flush=True)

    ctx = {"field3": fields["NR4A3"], "fields": fields, "lookup3": lookups["NR4A3"], "lookups": lookups,
           "reactive": reactive, "lys_by_species": lys_by_species, "m3_cb": m3["cb"]}

    poses = build_pose_ensemble(m3, reactive, fields["NR4A3"], args.n_poses, rng)
    print(f"[basin] warhead exit-vector pose ensemble: {len(poses)} anchors "
          f"(shell {PARAMS['pose_anchor_shell_A']} A from the cryptic-pocket centroid)", flush=True)

    # ---- E3 arms
    arms, registry_meta = [], None
    if args.self_test:
        arms = [synthetic_arm(random.Random(1))]
    elif os.path.exists(args.registry):
        reg = json.load(open(args.registry))
        registry_meta = {k: reg[k] for k in ("_title", "_method", "_limits", "staged_at_utc") if k in reg}
        want = {a.strip() for a in args.arms.split(",") if a.strip()}
        for aid, rec in reg.get("arms", {}).items():
            if want and aid not in want:
                continue
            if rec.get("status") != "OK":
                print(f"[basin] arm {aid} skipped: status={rec.get('status')}", flush=True)
                continue
            arms.append(load_arm_from_registry(rec))
        e2 = reg.get("e2_geometry")
        if e2 and e2.get("measured"):
            PARAMS["ring_to_e2_cys_A"] = e2["ring_to_catalytic_cys_A"]
            PARAMS["_transfer_geometry_source"] = {
                "pdb_id": e2["pdb_id"], "title": e2.get("title"), "e2": e2.get("e2"),
                "catalytic_cys": e2.get("catalytic_cys_resid"),
                "identified_by": e2.get("catalytic_cys_identified_by"),
            }
            print(f"[basin] RING->E2 catalytic-Cys distance MEASURED from {e2['pdb_id']}: "
                  f"{e2['ring_to_catalytic_cys_A']} A (replaces the parametric default)", flush=True)
            cal = e2.get("substrate_lysine_calibration")
            if cal and cal.get("nearest_lysine_to_catalytic_cys_A"):
                PARAMS["lysine_transfer_A"] = cal["nearest_lysine_to_catalytic_cys_A"]
                PARAMS["_lysine_transfer_calibrated_from"] = (
                    f"{e2['pdb_id']}: nearest substrate Lys{cal['nearest_lysine_resid']} NZ is "
                    f"{cal['nearest_lysine_to_catalytic_cys_A']} A from the E2 catalytic cysteine")
                print(f"[basin] transfer distance CALIBRATED from {e2['pdb_id']}: nearest substrate lysine "
                      f"sits {cal['nearest_lysine_to_catalytic_cys_A']} A from the catalytic Cys "
                      f"(the 10.0 A default was an assumption and was too strict by ~7 A)", flush=True)
    if not arms:
        raise SystemExit(f"no E3 arms available — run nr4a3_e3_stage.py on CI first (registry: {args.registry})")

    # ---- the search
    results = {}
    for arm in arms:
        per_pose = []
        for pose in poses:
            r = run_arm_pose(arm, pose, ctx, rng, args.samples)
            per_pose.append(r)
            print(f"[basin] {arm['arm_id']} {pose['pose_id']}: accepted "
                  f"{r['stats']['n_accepted']}/{r['stats']['n_samples']} "
                  f"({r['stats']['acceptance_rate']:.2%}) -> {len(r['basins'])} basins", flush=True)
        metas = marginalise_over_poses(per_pose)
        results[arm["arm_id"]] = {
            "recruiter": arm["recruiter"], "crl": arm.get("crl"),
            "ligand_het": arm.get("ligand_het"),
            "provenance": arm.get("provenance"),
            "e3_lane_caveats": (arm.get("lane1") or {}).get("caveats") or [],
            "e3_lane_backfilled": bool((arm.get("lane1") or {}).get("backfilled")),
            "exit_vector_source": arm.get("exit_vector_source"),
            "_role": ("E3-CHOICE SENSITIVITY CONTROL — this recruiter was Pareto-dominated in the E3 lane's "
                      "downselect and advanced only so the E3 is a controlled variable. A difference between "
                      "it and the front-running recruiter is NOT a preference this rung may report."
                      if (arm.get("lane1") or {}).get("backfilled") else
                      "downselected recruiter"),
            "per_pose": per_pose, "meta_basins": metas,
        }
        print(f"[basin] {arm['arm_id']}: {len(metas)} pose-marginalised meta-basins; "
              f"top surviving fraction "
              f"{metas[0]['pose_surviving_fraction'] if metas else 0}", flush=True)

    envelope = term_a_feasibility_envelope(poses, reactive["unique_cysteines"], fields["NR4A3"], rng)
    print("[basin] term-(a) E3-INDEPENDENT feasibility envelope:", flush=True)
    for cys, v in envelope["per_cysteine"].items():
        print(f"[basin]   {cys}: exit-anchor->SG {v['dist_exit_anchor_to_SG_A']['min']}-"
              f"{v['dist_exit_anchor_to_SG_A']['max']} A | shortest linker with ANY feasible E3 anchor: "
              f"{v['shortest_linker_with_any_feasible_anchor']} atoms | "
              f"closed={v['geometrically_closed']}", flush=True)

    all_metas = [m for a in results.values() for m in a["meta_basins"]]
    n_basins = sum(len(p["basins"]) for a in results.values() for p in a["per_pose"])
    gate = tier2_verdict(all_metas, n_basins)

    out = {
        "_title": "RUNG-5a mechanism-first orientation-basin search — NR4A3 vs NR4A1/NR4A2",
        "_status": "DESIGN PRIORITISATION, not a result about binding, degradation, efficacy or safety.",
        "_method": (
            "Rigid-body placement of each staged E3 arm around the fixed, matched opened NR4A3 LBD under a "
            "prolate-spheroid LINKER-REACH restraint anchored at a warhead exit-vector point and the E3 "
            "ligand's derived exit atom; coarse residue-level steric acceptance against a clamped nearest-atom "
            "distance field with a conservative clash bound; leader clustering into basins; then the two "
            "CATEGORICAL terms (electrophile reach to a paralogue-unique cysteine; E2~Ub transfer-zone lysine "
            "identity, evaluated on NR4A3 AND on both superposed paralogues) plus a UNITLESS contact score "
            "used only to rank within survivors. The whole search is marginalised over a warhead "
            "exit-vector pose ensemble and the surviving fraction is reported."),
        "_limits": [
            "DOUBLE CONDITIONALITY: everything is conditional on the hypothesised cmpd19 binary pose x the "
            "chosen receptor frame. This repo holds no cmpd19 pose in the matched-model frame, so the warhead "
            "exit vector is MARGINALISED over an ensemble of pocket-mouth anchors rather than asserted; the "
            "surviving-fraction column is the honest measure of how pose-dependent each basin is.",
            "ONE static opened conformer per paralogue. Both the target surface and C397's exposure (RSA "
            "0.395 in this frame) are conformer-dependent; the matched NR4A1/2 MD-ensemble add-on is the "
            "declared way to test which handles survive dynamics, and it has NOT been run.",
            "The interface score is a UNITLESS contact count with preregistered weights. It is NOT a free "
            "energy, it is NOT calibrated against any measurement, and no conclusion here rests on a small "
            "difference in it. The marginal axis needs ~2.0 kcal/mol of true margin against a best-case "
            "resolvable 1.12 — a cheap score cannot adjudicate that.",
            "Rigid-body, side-chain-rigid, no solvation, no induced fit. A basin is a NOMINATION of a region "
            "of orientation space, not a modelled complex.",
            "TERM (b) IS PROBABILISTIC, NOT ABSOLUTE: real degraders often ubiquitinate several lysines, and "
            "lysine-less substrates can still be degraded via N-terminal/Ser/Thr/Cys ubiquitination. Steering "
            "the transfer zone onto a paralogue-unique lysine RAISES THE ODDS; it does not guarantee the "
            "paralogue is spared.",
            "The E2~Ub transfer zone is an ARC sampled about the RBX1 RING with a swept radius and swept "
            "transfer distance, not a solved CRL conformation. CRL arms are mobile; this is a declared model, "
            "and the per-basin sensitivity sweep is reported so a category that depends on the parameter "
            "choice is visible as such.",
            "LBD-only: hinge/DBD/EWSR1-fusion lysines are absent from these models. The EWSR1 moiety was "
            "checked and contributes only 1-2 lysines, so it is not a design axis, but the LBD lysine set is "
            "not the complete ubiquitination-site set.",
            "A covalent handle is an unresolved liability, not an upgrade: electrophile promiscuity cannot be "
            "checked without chemoproteomics, and it must be reported alongside the parent warhead's "
            "published MYC induction. Prefer REVERSIBLE-covalent chemistry so catalytic turnover survives.",
            "No efficacy, safety, therapeutic-window or clinical claim is made or implied. Surviving basins "
            "are inputs to a PREDICTED SELECTIVE CANDIDATE series, never a selective hit.",
        ],
        "_schema_version": "1.0",
        "_schema": {
            "tier2_gate": "the RUNG-5a verdict. {pass, basis in CATEGORICAL|NOMINAL_ONLY|NONE, verdict, "
                          "n_meta_basins, n_exploiting_term_a_electrophile_reach, "
                          "n_exploiting_term_b_unique_lysine_zone (an UPPER BOUND — best-of-N), "
                          "n_nominally_discriminating, asymmetry_note}",
            "meta_basins_ranked": "pose-marginalised basins across all arms, best first. Per basin: "
                                  "{meta_basin_id, arm_id, pose_surviving_fraction (term (d)), "
                                  "n_poses_present/n_poses_total, total_members, interface_patch_uniprot, "
                                  "term_a_union{C###: min_linker_atoms (EXACT three-ball rule; null = not "
                                  "reachable within reach_scan_max_atoms), max_fraction_reachable_at_gate, "
                                  "and the *_relaxed_superseded twins carrying the 2026-07-25-corrected "
                                  "values so the change is auditable per record}, "
                                  "term_b_best_rank (best-of-N, inflated), "
                                  "term_b_mean_fraction_unique_covering (UNBIASED — read this), "
                                  "term_b_mean_fraction_paralogues_bare, term_b_exceeds_background, "
                                  "term_b_max_enrichment_over_background, term_b_unique_lysines_covered, "
                                  "stability_surrogate_nominal_delta_range (UNITLESS, ranks only), "
                                  "best_accessibility, best_linker_atoms}",
            "term_a_feasibility_envelope": "E3-INDEPENDENT upper bound per unique cysteine: "
                                           "{shortest_linker_with_any_feasible_anchor, "
                                           "geometrically_closed, by_linker_atoms}. Distinguishes 'no "
                                           "recruiter docked there' from 'no linker can reach it'.",
            "arms.<arm>.per_pose[].term_b_background_null": "the NULL — the rate at which ANY accepted "
                                                            "placement covers a unique lysine. A basin "
                                                            "carries term-(b) information only insofar as "
                                                            "it exceeds this.",
            "arms.<arm>.e3_lane_caveats": "carried verbatim from the E3 lane's contract; must be repeated "
                                          "in any downstream report.",
            "arms.<arm>.e3_lane_backfilled": "true = E3-CHOICE SENSITIVITY CONTROL, not a co-winner. A "
                                             "difference between it and the front-runner is NOT a "
                                             "reportable preference.",
            "parameters._lysine_transfer_calibrated_from": "provenance of the transfer distance when it was "
                                                           "measured rather than assumed.",
        },
        "parameters": PARAMS,
        "inputs": {
            "structures": os.path.relpath(args.struct_dir, REPO) + "/nr4a{3,1,2}-opened.pdb",
            "unique_residues": os.path.relpath(args.unique_json, REPO),
            "e3_registry": os.path.relpath(args.registry, REPO) if not args.self_test else "SYNTHETIC",
            "e3_registry_meta": registry_meta,
            "samples_per_arm_pose": args.samples, "n_poses": len(poses), "seed": args.seed,
        },
        "target_frame": {
            "pocket_centroid": [round(c, 3) for c in reactive["pocket_centroid"]],
            "cryptic_pocket_local_resids": reactive["pocket_local"],
            "superposition_NR4A1": m1["superposition"], "superposition_NR4A2": m2["superposition"],
            "unique_cysteines": [{k: v for k, v in c.items() if k != "xyz"}
                                 for c in reactive["unique_cysteines"]],
            "unique_lysines": [{k: v for k, v in k2.items() if k != "xyz"}
                               for k2 in reactive["unique_lysines"]],
            "n_lysines": {sp: len(v) for sp, v in lys_by_species.items()},
        },
        "pose_ensemble": poses,
        "arms": results,
        "meta_basins_ranked": all_metas,
        "term_a_feasibility_envelope": envelope,
        "tier2_gate": gate,
        "runtime_s": round(time.time() - t0, 1),
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)

    print("")
    print(f"[basin] TIER-2 GATE: {'PASS/GO' if gate['pass'] else 'NO-GO'} (basis {gate['basis']})")
    print(f"[basin]   meta-basins {gate['n_meta_basins']}  term(a) {gate['n_exploiting_term_a_electrophile_reach']}"
          f"  term(b) {gate['n_exploiting_term_b_unique_lysine_zone']}"
          f"  nominal {gate['n_nominally_discriminating']}")
    print(f"[basin]   {gate['verdict']}")
    for m in all_metas[:10]:
        ta = ", ".join("%s:%sat(was %d)" % (c, v["min_linker_atoms"] if v["min_linker_atoms"] is not None
                                            else ">%d" % PARAMS["reach_scan_max_atoms"],
                                            v["min_linker_atoms_relaxed_superseded"])
                       for c, v in sorted(m["term_a_union"].items()))
        print(f"[basin]   {m['meta_basin_id']}: poses {m['n_poses_present']}/{m['n_poses_total']} "
              f"({m['pose_surviving_fraction']:.0%})  members {m['total_members']}  "
              f"term(b) rank {m['term_b_best_rank']} uniqueK {m['term_b_unique_lysines_covered']}  "
              f"term(a) [{ta}]")
    print(f"[basin] wrote {os.path.relpath(args.out, REPO)} in {out['runtime_s']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
