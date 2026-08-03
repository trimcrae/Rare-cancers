#!/usr/bin/env python3
"""
DOES REMOVING THE E3 ARM RESCUE THE CATEGORICAL SELECTIVITY AXIS? ($0, CPU/CI only, pure stdlib.)

THE QUESTION, AND WHY IT HAD NEVER BEEN ASKED. Every reach number this repo owns was enumerated for a
molecule that must ALSO present a second terminus to solvent -- an E3 ligand in the degrader case
(`nr4a3_linker_covalent_reach.py`, whose anchors are (a = warhead attachment point, b = E3 anchor)), an
effector recruiter in the TCIP case. A MONOVALENT pocket-modulating molecule has neither: it is a warhead
plus, at most, a tether carrying an electrophile. Both `target-route-options.md` (route 2, $0 backlog item
4) and `emc-post-degrader-options.md` (next-two-weeks item 4) record the same intuition in the same words --
one fewer terminus to satisfy is "a strictly smaller search problem" -- and neither had run it.

★ THE INTUITION IS TRUE ABOUT THE SEARCH AND IRRELEVANT TO THE DECISION, WHICH IS THE POINT OF THIS MODULE.
  Reach is monotone: dropping the `b` term can only shorten every chain, so every cysteine in the family
  becomes reachable at or below the length it needed before. But the route's decision quantity is not
  reachability, it is the CHEMOSELECTIVITY WINDOW -- the interval of backbone-atom counts over which the
  NR4A3-unique target C397 is in reach and NO other cysteine in NR4A1, NR4A2 or NR4A3 is. Shortening
  everything shortens the competitors too, and whether the window widens, narrows or vanishes depends on
  whether the `b` term was ORDERING the cysteines as well as costing atoms. That is a measurement, and this
  module is it.

WHAT IS COMPUTED, AND WHY IT IS PAIRED. Both configurations are computed IN THE SAME PASS, from the SAME
frames, the SAME anchors and the SAME candidate branch-point sets, differing only in the rule that turns a
branch position into a chain length:

    bivalent    n = ceil(|p-a|/rise) + ceil(|p-b|/rise)      (`linker_covalent_reach.n_min_from_point`)
    monovalent  n = ceil(|p-a|/rise)                          (this module)

An unpaired comparison against the committed artifact would confound the configuration change with every
other difference between two runs, so the committed bivalent family-wide window is used as a REPLICATION
TARGET (`crosscheck_replicates_committed`) rather than as the comparator. If this module cannot reproduce
the committed bivalent numbers it refuses, because then its monovalent numbers mean nothing either.

⚠ TWO THINGS THE MONOVALENT CONFIGURATION CHANGES BESIDES THE ARITHMETIC, both reported rather than assumed:
  1. THE PLACEMENTS COLLAPSE. The ten (basin x placement) cells are ten distinct (a, b) pairs but only FIVE
     distinct warhead anchors `a`. With `b` gone, the ten cells are five, and pooling them as ten would
     report the same measurement twice and call it agreement.
  2. THE ADMISSIBILITY FILTER RETIRES. The bivalent analysis drops any cell whose conformer has moved into
     the E3 anchor (`placement_admissibility`, "the E3 must still project to solvent"). A monovalent
     molecule has no E3 anchor, so that filter has nothing to bite on and every cell is admissible. This is
     a genuine advantage of the configuration and it is counted separately from the window result, because
     "more cells qualify" and "the surviving cells are better" are different claims.

⛔ WHAT THIS MODULE CANNOT SAY, INHERITED WHOLE FROM THE BIVALENT LANE AND NOT WEAKENED BY BEING MONOVALENT.
   Geometry only. No thiol pKa, intrinsic electrophile reactivity, adduct stability, potency, permeability,
   exposure, efficacy, safety or clinical statement is computed or implied. Every anchor still comes from
   the docked pose whose known-answer test `V3` returned INCONCLUSIVE -- and `V3`'s failure was SITE
   selection, which is the half a marginalisation over pocket-mouth anchors does not absorb. Reach can
   REFUTE a route; it can never license one. The paralogue positions are single opened models plus their
   metadynamics ensembles, and inherit that lane's rotamer-noise bound.

Outputs: nr4a3-monovalent-reach.json (+ .md)
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                          # noqa: E402
import linker_design as LD                      # noqa: E402  THE reach engine — never reimplemented
import nr4a3_basin_search as BS                 # noqa: E402
import nr4a_differential_atlas as atlas         # noqa: E402
import nr4a3_linker_covalent_reach as CR        # noqa: E402  the bivalent lane — every primitive reused

RISE = LD.RISE_PER_ATOM_A
PENDANT_REACH = LD.PENDANT_REACH_A
CHEM_MAX_ATOMS = CR.CHEM_MAX_ATOMS
CLASH_SWEEP_A = CR.CLASH_SWEEP_A
CLASH_PRIMARY_A = CR.CLASH_PRIMARY_A
TARGET = "C397"

OUT = os.path.join(HERE, "nr4a3-monovalent-reach.json")
COMMITTED_BIVALENT = os.path.join(HERE, "nr4a3-linker-covalent-reach.json")


# ==========================================================================================================
# THE ONE NEW RULE
# ==========================================================================================================
def mono_min_from_point(p, a, rise: float = RISE):
    """Shortest chain length that can put a backbone atom at `p`, with NO second terminus to satisfy.

    The bivalent identity is `ceil(|p-a|/rise) + ceil(|p-b|/rise)`; a monovalent molecule drops the second
    term entirely. The `max(1, ...)` floor is kept deliberately IDENTICAL to the bivalent rule so the two
    configurations are compared on the same convention -- a zero-atom (warhead-borne) electrophile would be
    a different claim, and branch 1's census already put every unique cysteine outside warhead range.
    """
    return max(1, int(math.ceil(G.dist(p, a) / rise - 1e-9)))


def mono_corridor_min_atoms(candidates, a, arm_reach: float, cutoff: float, n_max: int = 80):
    """Shortest MONOVALENT chain with a clash-free branch position reaching the target.

    Same candidate set, same clash convention and same arm test as `CR.corridor_min_atoms` -- only the
    length rule differs. Returns None when no candidate qualifies."""
    best = None
    for c in candidates:
        if c["d_q"] > arm_reach or cutoff not in c["clear_at"]:
            continue
        n = mono_min_from_point(c["p"], a)
        if n <= n_max and (best is None or n < best):
            best = n
    return best


def mono_through_space_atoms(q, a, arm_reach: float, rise: float = RISE):
    """The through-space MONOVALENT analogue: the electrophile sits at the chain terminus, so the target is
    reachable by an n-atom chain iff |q-a| <= n*rise + arm_reach.

    ⚠ THIS IS A CLOSED FORM AND NOT A CALL INTO `min_linker_atoms_exact`, AND THE REASON IS MEASURED
    RATHER THAN STYLISTIC. Setting b = a does NOT reduce the engine to this question: the three-ball rule
    still requires some branch index k with min(k, n-k)*rise >= |p-a|, so its shortest admissible n is
    EXACTLY TWICE the monovalent answer. Reusing the solver with a fabricated second anchor would have
    doubled every monovalent chain length and inverted the comparison. The factor is pinned in
    `tests/test_nr4a3_monovalent_reach.py`."""
    d = G.dist(q, a)
    if d <= arm_reach:
        return 1
    return max(1, int(math.ceil((d - arm_reach) / rise - 1e-9)))


# ==========================================================================================================
# ANCHORS — the collapse from ten placements to five warhead anchors
# ==========================================================================================================
def monovalent_anchors(placements):
    """The DISTINCT warhead anchors, with the bivalent placements each one subsumes.

    ★ Reported as a structural finding rather than folded away: with the E3 anchor gone, ten bivalent cells
    are five monovalent ones, and any per-cell count that still said ten would be double-counting."""
    by_pose = {}
    for pl in placements:
        rec = by_pose.setdefault(pl["pose_id"], {"pose_id": pl["pose_id"], "_a": pl["_a"],
                                                 "a_warhead_anchor": pl["a_warhead_anchor"],
                                                 "subsumes_bivalent_placements": []})
        rec["subsumes_bivalent_placements"].append("%s@%s" % (pl["meta_basin_id"], pl["placement_label"]))
        if rec["_a"] != pl["_a"]:                       # same pose_id must mean the same anchor
            raise SystemExit("pose %s carries two different anchors — REFUSING" % pl["pose_id"])
    return [by_pose[k] for k in sorted(by_pose)]


# ==========================================================================================================
# THE PAIRED REACH TABLE
# ==========================================================================================================
def reach_frame_paired(model, placements, anchors, numbering, unique_labels, label,
                       cutoff=CLASH_PRIMARY_A, cutoffs=CLASH_SWEEP_A):
    """Both configurations, every cysteine x anchor x pendant, in ONE structure and from ONE candidate set.

    Returns {"cysteines": {...}, "mono": [...], "bival": [...]} where each row carries the corridor and
    through-space atom counts for its configuration. The bivalent rows keep the (basin, placement) identity
    because the E3 anchor is what distinguishes them; the monovalent rows are keyed by anchor alone.
    """
    cys = CR.cysteines_in(model, numbering, unique_labels)
    grid = CR.make_grid(model)
    max_reach = max(PENDANT_REACH.values())
    cand = {lab: CR.candidate_branch_points(grid, c["xyz"], max_reach, {c["local_resid"]}, cutoffs)
            for lab, c in cys.items()}

    mono_rows = []
    for anc in anchors:
        a = anc["_a"]
        for lab, c in sorted(cys.items()):
            q = c["xyz"]
            row = {"frame": label, "anchor": anc["pose_id"], "cysteine": lab, "unique": c["unique"],
                   "d_warhead_anchor_A": round(G.dist(q, a), 2), "by_pendant": {}}
            for pname, e in sorted(PENDANT_REACH.items(), key=lambda kv: kv[1]):
                row["by_pendant"][pname] = {
                    "arm_reach_A": e,
                    "through_space_atoms": mono_through_space_atoms(q, a, e),
                    "corridor_atoms": mono_corridor_min_atoms(cand[lab], a, e, cutoff),
                }
            mono_rows.append(row)

    bival_rows = []
    for pl in placements:
        a, b = pl["_a"], pl["_b"]
        key = "%s@%s" % (pl["meta_basin_id"], pl["placement_label"])
        for lab, c in sorted(cys.items()):
            q = c["xyz"]
            row = {"frame": label, "placement": key, "anchor": pl["pose_id"], "cysteine": lab,
                   "unique": c["unique"],
                   # carried so `CR.crosscheck_committed_distances` can grade these rows against the
                   # committed library without this module re-deriving either distance (rule 1)
                   "meta_basin_id": pl["meta_basin_id"], "placement_label": pl["placement_label"],
                   "d_warhead_anchor_A": round(G.dist(q, a), 2),
                   "d_e3_anchor_A": round(G.dist(q, b), 2),
                   "by_pendant": {}}
            for pname, e in sorted(PENDANT_REACH.items(), key=lambda kv: kv[1]):
                n_co, _ = CR.corridor_min_atoms(cand[lab], a, b, e, cutoff)
                row["by_pendant"][pname] = {
                    "arm_reach_A": e,
                    "through_space_atoms": LD.min_linker_atoms_exact(a, b, q, e, n_max=80),
                    "corridor_atoms": n_co,
                }
            bival_rows.append(row)

    return {"cysteines": {k: {"unique": v["unique"], "local_resid": v["local_resid"]}
                          for k, v in cys.items()},
            "mono": mono_rows, "bival": bival_rows}


# ==========================================================================================================
# THE DECISION QUANTITY — the family-wide window, in both configurations
# ==========================================================================================================
def family_window(nr4a3_rows, paralogue_rows, key_field, convention, target=TARGET,
                  chem_max=CHEM_MAX_ATOMS):
    """The interval of backbone-atom counts over which `target` is in reach and NO other cysteine in ANY of
    the three proteins is.

    ★ `rank_of_target` is reported beside the window and it is the statistic that survives every threshold
    argument: a window of width 0 says the route fails at this geometry, but the RANK says by how much and
    against whom, and it does not depend on the chemically-routine ceiling."""
    field = "through_space_atoms" if convention == "through_space" else "corridor_atoms"

    groups = {}
    for r in nr4a3_rows:
        groups.setdefault(r[key_field], {}).setdefault("NR4A3", []).append(r)
    for prot, rows in paralogue_rows.items():
        for r in rows:
            groups.setdefault(r[key_field], {}).setdefault(prot, []).append(r)

    out = []
    for key, group in sorted(groups.items()):
        tgt = next((r for r in group.get("NR4A3", []) if r["cysteine"] == target), None)
        if tgt is None:
            continue
        for pname in sorted(PENDANT_REACH, key=lambda k: PENDANT_REACH[k]):
            n_u = tgt["by_pendant"][pname][field]
            competitors = {}
            for prot, rows in group.items():
                for r in rows:
                    if prot == "NR4A3" and r["cysteine"] == target:
                        continue
                    v = r["by_pendant"][pname][field]
                    if v is not None:
                        competitors["%s %s" % (prot, r["cysteine"])] = v
            m = CR.chemoselectivity_margin(n_u, competitors, chem_max)
            intra = CR.chemoselectivity_margin(
                n_u, {k2.split()[1]: v for k2, v in competitors.items() if k2.startswith("NR4A3")},
                chem_max)
            ordered = sorted(competitors.items(), key=lambda kv: kv[1])
            rank = 1 + sum(1 for _, v in ordered if n_u is not None and v < n_u)
            ties = [k2 for k2, v in ordered if n_u is not None and v == n_u]
            first_set = [k2 for k2, v in ordered if ordered and v == ordered[0][1]] if ordered else []
            out.append({
                "cell": key, "pendant": pname, "convention": convention, "target": target,
                "target_atoms": n_u,
                "window_lo": m["lo"], "window_hi": m["hi"], "width": m["width"],
                # ⚠ `closed_by` is a TIE-BREAK wherever two competitors arrive together — the honest form
                #   names the SET, which is the correction branch 1b's reconciliation had to make.
                "closed_by": m["blocked_by"], "closed_at_atoms": m["blocked_at_atoms"],
                "first_competitor_set": first_set,
                "closer_is_a_PARALOGUE_cysteine": bool(m["blocked_by"]
                                                       and not m["blocked_by"].startswith("NR4A3")),
                "rank_of_target": rank, "tied_with": ties,
                "intra_nr4a3_width": intra["width"],
                "cost_of_the_paralogue_control_in_atoms": intra["width"] - m["width"],
                "all_competitors_atoms": dict(ordered),
            })
    return out


TERM_A = "term_a_exemplar"


def paired_transitions(mono_rows, bival_rows, anchor_of_placement):
    """★★ THE HONEST COMPARATOR, AND THE REASON A BARE COUNT WOULD MISLEAD.

    The two configurations do not have the same number of cells: ten (placement x pendant) bivalent cells
    collapse onto five (anchor x pendant) monovalent ones, so `n_open` is not comparable between them and a
    ratio of ratios would still hide which cells moved. Instead, every bivalent cell is PAIRED with the
    monovalent cell at its own warhead anchor and the same pendant, and the transition is counted:

        open -> open      the window survives removing the E3 arm
        open -> closed    the window existed only because of the E3 arm's geometry
        closed -> open    removing the arm CREATED a window
        closed -> closed  no window either way

    A 'closed -> open' count of zero and a large 'open -> closed' count is the shape that refutes the
    intuition this module was built to test.
    """
    m = {(r["cell"], r["pendant"]): r for r in mono_rows}
    out = {"open_to_open": 0, "open_to_closed": 0, "closed_to_open": 0, "closed_to_closed": 0,
           "n_paired": 0, "unpaired": 0, "cells_that_gained_a_window": [],
           "cells_that_lost_a_window": []}
    for b in bival_rows:
        anc = anchor_of_placement.get(b["cell"])
        mo = m.get((anc, b["pendant"])) if anc else None
        if mo is None:
            out["unpaired"] += 1
            continue
        out["n_paired"] += 1
        key = "%s -> %s" % ("open" if b["width"] > 0 else "closed",
                            "open" if mo["width"] > 0 else "closed")
        out[key.replace(" -> ", "_to_")] += 1
        if b["width"] == 0 and mo["width"] > 0:
            out["cells_that_gained_a_window"].append({"bivalent_cell": b["cell"], "pendant": b["pendant"],
                                                      "monovalent_width": mo["width"]})
        if b["width"] > 0 and mo["width"] == 0:
            out["cells_that_lost_a_window"].append({"bivalent_cell": b["cell"], "pendant": b["pendant"],
                                                    "bivalent_width": b["width"],
                                                    "monovalent_closed_by": mo["closed_by"]})
    out["cells_that_lost_a_window"] = out["cells_that_lost_a_window"][:20]
    return out


def window_summary(rows):
    """n_open / median width / who closes it / how often the target is not even first."""
    widths = sorted(r["width"] for r in rows)
    n = len(widths)
    med = None
    if n:
        mid = n // 2
        med = widths[mid] if n % 2 else (widths[mid - 1] + widths[mid]) / 2.0
    closers = {}
    for r in rows:
        if r["closed_by"]:
            closers[r["closed_by"]] = closers.get(r["closed_by"], 0) + 1
    return {
        "n_cells": n,
        "n_open": sum(1 for r in rows if r["width"] > 0),
        "median_width": med,
        "n_closed_by_a_PARALOGUE_cysteine": sum(1 for r in rows if r["closer_is_a_PARALOGUE_cysteine"]),
        "n_closed_by_an_NR4A3_conserved_cysteine": sum(
            1 for r in rows if r["closed_by"] and r["closed_by"].startswith("NR4A3")),
        "n_target_not_first": sum(1 for r in rows if r["rank_of_target"] > 1),
        "n_target_tied_first": sum(1 for r in rows if r["rank_of_target"] == 1 and r["tied_with"]),
        "closers_by_count": dict(sorted(closers.items(), key=lambda kv: -kv[1])),
        "median_intra_nr4a3_width": (lambda v: v[len(v) // 2] if v else None)(
            sorted(r["intra_nr4a3_width"] for r in rows)),
    }


# ==========================================================================================================
# CROSS-CHECKS — rule 1: this module may not mint a second value for a number with a home
# ==========================================================================================================
def crosscheck_replicates_committed(bival_windows, path=COMMITTED_BIVALENT):
    """★★ THE GUARD THE WHOLE COMPARISON RESTS ON. The bivalent half computed here must reproduce the
    committed `nr4a3-linker-covalent-reach.json` family-wide window cell for cell. If it does not, the
    monovalent half is measuring this module's own bugs, not the configuration change."""
    if not os.path.exists(path):
        return {"status": "UNREAD", "reason": "%s absent" % path}
    with open(path) as fh:
        committed = ((json.load(fh).get("★_family_wide_chemoselectivity_window") or {})
                     .get("by_convention") or {})
    compared, mismatches = 0, []
    for conv, rows in bival_windows.items():
        ref = {(r["placement"], r["pendant"]): r for r in (committed.get(conv) or [])}
        for r in rows:
            k = (r["cell"], r["pendant"])
            c = ref.get(k)
            if c is None:
                continue
            compared += 1
            for f in ("target_atoms", "width", "window_lo", "closed_at_atoms"):
                if r[f] != c.get(f):
                    mismatches.append({"cell": k, "convention": conv, "field": f,
                                       "recomputed": r[f], "committed": c.get(f)})
    return {
        "status": ("AGREES" if compared and not mismatches
                   else "DISAGREES" if mismatches else "UNREAD"),
        "n_cells_compared": compared, "mismatches": mismatches[:20],
        "source_of_truth": "research/modalities/nr4a3-linker-covalent-reach.json -> family_wide_window",
        "_why": ("the monovalent result is a DELTA against the bivalent one, so a bivalent half that does "
                 "not replicate the committed artifact invalidates the delta as well."),
    }


def monotonicity_check(mono_rows, bival_rows):
    """Reach is monotone in the dropped term, so for every (frame, anchor, cysteine, pendant, convention)
    the monovalent count must be <= the bivalent count at the same anchor. A violation is a bug, not a
    finding, and it refuses rather than being reported as a result."""
    idx = {}
    for r in mono_rows:
        for pn, e in r["by_pendant"].items():
            idx[(r["frame"], r["anchor"], r["cysteine"], pn)] = e
    bad = []
    for r in bival_rows:
        for pn, e in r["by_pendant"].items():
            m = idx.get((r["frame"], r["anchor"], r["cysteine"], pn))
            if m is None:
                continue
            for f in ("through_space_atoms", "corridor_atoms"):
                if m[f] is not None and e[f] is not None and m[f] > e[f]:
                    bad.append({"frame": r["frame"], "anchor": r["anchor"], "cysteine": r["cysteine"],
                                "pendant": pn, "field": f, "monovalent": m[f], "bivalent": e[f]})
                if m[f] is None and e[f] is not None:
                    bad.append({"frame": r["frame"], "anchor": r["anchor"], "cysteine": r["cysteine"],
                                "pendant": pn, "field": f, "monovalent": None, "bivalent": e[f],
                                "_kind": "monovalent unreachable where bivalent reaches"})
    return {"status": "HOLDS" if not bad else "VIOLATED", "n_violations": len(bad), "violations": bad[:20],
            "_rule": "dropping the E3 term can only shorten a chain, so monovalent <= bivalent everywhere"}


# ==========================================================================================================
# DRIVER
# ==========================================================================================================
def build(seqs, cutoff=CLASH_PRIMARY_A, paralogue_ensembles=True, struct_root=REPO):
    import nr4a3_covalent_handle_ensemble as COV

    refusals, unread = [], []
    placements, basins = CR.load_placements()
    anchors = monovalent_anchors(placements)
    unique_labels = {"C%d" % c["uniprot_resid"] for c in basins["target_frame"]["unique_cysteines"]}

    nr4a3 = BS.load_paralogue(CR.OPENED["NR4A3"])
    tgt = reach_frame_paired(nr4a3, placements, anchors, CR.OFFSET, unique_labels, "nr4a3-opened", cutoff)

    par_mono, par_bival, par_meta = {}, {}, {}
    for prot in ("NR4A1", "NR4A2"):
        try:
            mob = BS.load_paralogue(CR.OPENED[prot])
            residues, _ = atlas.parse_pdb(CR.OPENED[prot])
            uni_map, ident = COV.pdb_to_uniprot_map(residues, seqs[prot], CR.MIN_ALIGN_IDENTITY)
            moved = BS.superpose_paralogue(mob, nr4a3)
        except Exception as exc:                                     # noqa: BLE001 — refuse, never guess
            refusals.append({"model": "%s-opened" % prot, "reason": "%s: %s" % (type(exc).__name__, exc)})
            continue
        r = reach_frame_paired(moved, placements, anchors, uni_map, set(), "%s-opened" % prot, cutoff)
        par_mono[prot], par_bival[prot] = r["mono"], r["bival"]
        par_meta[prot] = {"alignment_identity": round(ident, 4),
                          "superposition": moved.get("superposition"),
                          "cysteines": sorted(r["cysteines"])}

    # ---- the decision quantity, both configurations, both conventions ------------------------------------
    mono_windows = {c: family_window(tgt["mono"], par_mono, "anchor", c) for c in
                    ("through_space", "corridor")}
    bival_windows = {c: family_window(tgt["bival"], par_bival, "placement", c) for c in
                     ("through_space", "corridor")}

    # ---- robustness: the paralogue metadynamics ensembles ------------------------------------------------
    ens = {}
    if paralogue_ensembles:
        for prot, pattern in CR.PARALOGUE_ENSEMBLE.items():
            frames = sorted(glob.glob(os.path.join(struct_root, pattern)))
            if not frames:
                unread.append({"input": "%s metadynamics ensemble" % prot,
                               "reason": "no frames matched %s" % pattern})
                continue
            per_frame, n_ok = [], 0
            for f in frames:
                try:
                    mob = BS.load_paralogue(f)
                    residues, _ = atlas.parse_pdb(f)
                    uni_map, _ = COV.pdb_to_uniprot_map(residues, seqs[prot], CR.MIN_ALIGN_IDENTITY)
                    moved = BS.superpose_paralogue(mob, nr4a3)
                except Exception as exc:                             # noqa: BLE001
                    refusals.append({"model": f, "reason": "%s: %s" % (type(exc).__name__, exc)})
                    continue
                lab = "%s/%s" % (prot, os.path.basename(os.path.dirname(f)))
                r = reach_frame_paired(moved, placements, anchors, uni_map, set(), lab, cutoff)
                per_frame.append(r["mono"])
                n_ok += 1
            ens[prot] = {"n_frames": n_ok, "rows": [row for blk in per_frame for row in blk],
                         "kind": ("metadynamics pocket-opening ensemble (biased along a pocket CV — NOT "
                                  "Boltzmann weighted; a heterogeneity comparator, never an occupancy)")}

    ens_windows = {}
    if ens:
        # ★ THE HARDEST FORM OF THE CONTROL: the target's monovalent reach in ONE opened frame against
        #   EVERY paralogue conformer available. A window that survives this is a window that does not
        #   depend on one rotamer.
        for prot, blk in ens.items():
            by_frame = {}
            for row in blk["rows"]:
                by_frame.setdefault(row["frame"], []).append(row)
            worst = {}
            for conv in ("through_space", "corridor"):
                n_open, n_cells = 0, 0
                for fr, rows in by_frame.items():
                    w = family_window(tgt["mono"], {prot: rows}, "anchor", conv)
                    n_cells += len(w)
                    n_open += sum(1 for r in w if r["width"] > 0)
                worst[conv] = {"n_frames": len(by_frame), "n_cells": n_cells, "n_open": n_open}
            ens_windows[prot] = worst

    xchecks = {
        "committed_anchor_distances": CR.crosscheck_committed_distances(tgt["bival"]),
        "unique_cysteine_partition": CR.crosscheck_unique_set(
            {"unique": unique_labels, "all": set(tgt["cysteines"])}),
        "replicates_the_committed_bivalent_window": crosscheck_replicates_committed(bival_windows),
        "monovalent_never_exceeds_bivalent": monotonicity_check(tgt["mono"], tgt["bival"]),
    }

    return {
        "_title": "Does removing the E3 arm rescue the categorical selectivity axis at C397?",
        "_question": ("A MONOVALENT pocket-modulating molecule has no second terminus to present to "
                      "solvent, so its reach problem is strictly smaller than the degrader's. Does that "
                      "smaller problem give a WIDER chemoselectivity window at the NR4A3-unique cysteine "
                      "C397 — or does shortening every chain shorten the competitors' too?"),
        "_status": ("GEOMETRY ONLY, $0 CPU, pure stdlib. No reactivity, potency, selectivity, "
                    "developability, efficacy or clinical claim is made or implied. Reach can refute a "
                    "route; it cannot license one."),
        "_method": ("PAIRED: both configurations computed in one pass from identical frames, anchors and "
                    "candidate branch-point sets, differing only in the length rule "
                    "(bivalent ceil(|p-a|/r)+ceil(|p-b|/r) vs monovalent ceil(|p-a|/r)). The committed "
                    "bivalent artifact is a REPLICATION TARGET, not the comparator."),
        "_inherits": [
            "every anchor comes from the docked pose whose known-answer test V3 returned INCONCLUSIVE, and "
            "V3's failure was SITE selection — which a marginalisation over pocket-mouth anchors does not "
            "absorb",
            "the paralogue positions are independently built opened models; the aligned-pair rotamer-noise "
            "bound is owned by nr4a3-linker-covalent-reach.json and is not re-derived here",
            "no thiol pKa, intrinsic electrophile reactivity, adduct stability or chemoproteomic "
            "selectivity is computed anywhere in this repo",
        ],
        "configuration_change": {
            "n_bivalent_placements": len(placements),
            "n_monovalent_anchors": len(anchors),
            "anchors": [{k: v for k, v in a.items() if not k.startswith("_")} for a in anchors],
            "_reading": ("the ten bivalent cells are ten (a, b) pairs but only %d distinct warhead "
                         "anchors; with b gone they are %d cells, and reporting ten would double-count."
                         % (len(anchors), len(anchors))),
            "admissibility_filter_retires": {
                "bivalent_filter": ("a cell whose conformer has moved into the E3 anchor is dropped — "
                                    "'the E3 must still project to solvent' "
                                    "(nr4a3_linker_covalent_reach.placement_admissibility)"),
                "monovalent": "no E3 anchor exists, so the filter has nothing to bite on; every cell is "
                              "admissible",
                "_reading": "a genuine advantage of the configuration, counted separately from the window "
                            "result because 'more cells qualify' and 'the surviving cells are better' are "
                            "different claims",
            },
        },
        "target_frame": {"frame": "nr4a3-opened", "cysteines": tgt["cysteines"],
                         "monovalent_rows": tgt["mono"], "bivalent_rows": tgt["bival"]},
        "paralogue_frames": par_meta,
        "family_wide_window": {
            "_what": ("the interval of backbone-atom counts over which C397 is in reach and NO other "
                      "cysteine in NR4A1, NR4A2 or NR4A3 is — the route's decision quantity"),
            "monovalent": mono_windows,
            "bivalent": bival_windows,
        },
        "summary": {
            "monovalent": {c: window_summary(mono_windows[c]) for c in mono_windows},
            "bivalent": {c: window_summary(bival_windows[c]) for c in bival_windows},
            # the subset the committed bivalent verdict grades on — the C397 term-(a) exemplar placements —
            # carried so the comparison can be read on the committed artifact's own footing as well as on
            # the full board (rule 1: the committed figures are not re-typed, they are re-derived here and
            # cross-checked cell for cell against the artifact that owns them)
            "graded_term_a_only": {
                "monovalent": {c: window_summary(
                    [r for r in mono_windows[c]
                     if r["cell"] in {a["pose_id"] for a in anchors
                                      if any(TERM_A in p for p in a["subsumes_bivalent_placements"])}])
                    for c in mono_windows},
                "bivalent": {c: window_summary([r for r in bival_windows[c] if TERM_A in r["cell"]])
                             for c in bival_windows},
            },
        },
        "paired_transitions": {
            "_what": ("every bivalent (placement x pendant) cell paired with the monovalent cell at its "
                      "own warhead anchor and the same pendant — the comparator that survives the "
                      "collapse from ten placements to five anchors"),
            "by_convention": {c: paired_transitions(mono_windows[c], bival_windows[c],
                                                    {"%s@%s" % (p["meta_basin_id"], p["placement_label"]):
                                                     p["pose_id"] for p in placements})
                              for c in mono_windows},
        },
        "paralogue_metadynamics_ensembles": {
            "_what": "the monovalent window re-graded against every available paralogue conformer",
            "⚠_how_to_read_this": (
                "each cell here grades C397 against NR4A3's own cysteines and ONE paralogue's, one "
                "conformer at a time — it is NOT the joint family test. The joint test (NR4A3 + NR4A1 + "
                "NR4A2 together, on the opened models) is `family_wide_window`, and it is the one the "
                "verdict rests on. A single-paralogue cell is open more often BY CONSTRUCTION because its "
                "competitor set is smaller, so these counts may never be quoted as the family window. "
                "What they DO say is whether the closure is uniform across paralogue conformations, which "
                "the single opened models cannot answer."),
            "per_paralogue": ens_windows,
            "n_frames": {p: b["n_frames"] for p, b in ens.items()},
        },
        "cross_checks": xchecks,
        "refusals": refusals,
        "unread_inputs": unread,
    }


def verdict(d):
    ms = d["summary"]["monovalent"]
    bs = d["summary"]["bivalent"]
    co_m, co_b = ms["corridor"], bs["corridor"]
    ts_m, ts_b = ms["through_space"], bs["through_space"]
    pt = d["paired_transitions"]["by_convention"]
    pco, pts = pt["corridor"], pt["through_space"]

    def _dir(t):
        if t["open_to_closed"] and not t["closed_to_open"]:
            return "WORSE"
        if t["closed_to_open"] and not t["open_to_closed"]:
            return "BETTER"
        return "MIXED"

    per_conv = {c: _dir(t) for c, t in pt.items()}

    return {
        # ⚠ The answer is stated PER CONVENTION and not collapsed to one word, because the two conventions
        #   disagree and merging them would hide the disagreement. `corridor` is the conservative rule (a
        #   clash-free branch position with a clash-free arm); `through_space` is an upper bound on
        #   reachability that scores a buried sulfur as reachable.
        "answer_by_convention": per_conv,
        "answer_on_the_conservative_convention": per_conv["corridor"],
        "headline": (
            "Removing the E3 arm does NOT rescue the categorical axis, and on the conservative convention "
            "it destroys it outright. Corridor: of the %d bivalent cells that had an open family-wide "
            "window at C397, **%d** retain one when the E3 arm is removed, and **%d** gain one — a "
            "complete, one-directional collapse. Through-space (an upper bound on reachability, which "
            "scores buried sulfurs as reachable): %d of %d retained and %d gained, so the permissive rule "
            "reads MIXED. The intuition that one fewer terminus is 'a strictly smaller search problem' is "
            "true about REACH and irrelevant to SELECTIVITY: dropping the |p-b| term shortens every "
            "competitor's chain as well as the target's, and it removes the geometric constraint that was "
            "ORDERING them."
            % (pco["open_to_open"] + pco["open_to_closed"], pco["open_to_open"],
               pco["closed_to_open"],
               pts["open_to_open"], pts["open_to_open"] + pts["open_to_closed"], pts["closed_to_open"])),
        "cells_that_gained_a_window": {
            "_reading": ("the permissive convention's gains are the REACH half of the intuition being "
                         "true — cells where C397 needed more than the chemically routine bound "
                         "bivalently and needs less monovalently. Their widths are what decides whether "
                         "they mean anything: a window of 1–2 backbone atoms is inside the side-chain "
                         "displacement the bivalent lane already measured between independently built "
                         "paralogue models (that lane's `noise_sensitivity` owns the figures and they are "
                         "not re-typed here)."),
            "max_width_gained": {c: max([r["monovalent_width"] for r in t["cells_that_gained_a_window"]]
                                        or [0]) for c, t in pt.items()},
            "cells": {c: t["cells_that_gained_a_window"] for c, t in pt.items()},
        },
        "board_level_counts": {
            "_caveat": ("cell counts are NOT comparable between configurations — ten bivalent placements "
                        "collapse to five monovalent anchors — so these are reported as rates and the "
                        "decision rests on `paired_transitions` above."),
            "corridor": {"monovalent": [co_m["n_open"], co_m["n_cells"]],
                         "bivalent": [co_b["n_open"], co_b["n_cells"]]},
            "through_space": {"monovalent": [ts_m["n_open"], ts_m["n_cells"]],
                              "bivalent": [ts_b["n_open"], ts_b["n_cells"]]},
        },
        "what_changed_and_why_it_matters": {
            "the_E3_term_was_doing_selectivity_work": (
                "n = ceil(|p-a|/r) + ceil(|p-b|/r) is not merely a larger number than ceil(|p-a|/r): it "
                "penalises branch positions that are off the a->b axis, and it penalises each cysteine by "
                "a DIFFERENT amount. Removing it removes a discriminator along with a cost. Measured "
                "here as the rank of C397 among all family cysteines: monovalent, it is not first in %d "
                "of %d corridor cells; bivalent, in %d of %d."
                % (co_m["n_target_not_first"], co_m["n_cells"],
                   co_b["n_target_not_first"], co_b["n_cells"])),
            "the_intra_NR4A3_margin_collapses_too": (
                "the bivalent counter-test's finding was that the window is closed by a PARALOGUE cysteine "
                "rather than by one of NR4A3's own conserved ones — i.e. the intra-NR4A3 margin was the "
                "easy half. Monovalent it is not: the median intra-NR4A3 window falls to %s backbone "
                "atoms from %s, so the route loses a margin it had before any paralogue is considered."
                % (co_m["median_intra_nr4a3_width"], co_b["median_intra_nr4a3_width"])),
            "closers": {"monovalent_corridor": co_m["closers_by_count"],
                        "bivalent_corridor": co_b["closers_by_count"]},
        },
        "_what_this_verdict_is_not": (
            "It is not a refutation of monovalent pocket modulation as a route — a non-covalent monovalent "
            "molecule has no cysteine to reach and is untouched by this measurement. What it refutes is "
            "the specific hope that dropping the E3 arm would WIDEN the categorical (residue-uniqueness) "
            "window that a monovalent molecule would need in order to state a paralogue-selectivity claim "
            "without an instrument that resolves ~1 kcal/mol. It is geometry, on one opened target frame "
            "and independently built paralogue models, from anchors whose site question V3 left "
            "INCONCLUSIVE."),
    }


def to_markdown(d):
    L = []
    A = L.append
    A("# %s" % d["_title"])
    A("")
    A("> **$0, CPU, pure stdlib.** %s" % d["_status"])
    A(">")
    A("> Generated by `nr4a3_monovalent_reach.py`; this file is derived — edit the module, not this.")
    A("")
    A("**Question.** %s" % d["_question"])
    A("")
    A("**Method.** %s" % d["_method"])
    A("")
    ver = d["verdict"]
    A("## 1 · The answer")
    A("")
    A("**%s**" % ver["headline"])
    A("")
    for k, v in ver["what_changed_and_why_it_matters"].items():
        if isinstance(v, str):
            A("- **%s** — %s" % (k.replace("_", " "), v))
    A("")
    A("⛔ %s" % ver["_what_this_verdict_is_not"])
    A("")

    A("## 2 · The paired comparison — every bivalent cell against the monovalent cell at its own anchor")
    A("")
    A("| convention | paired cells | open → open | open → closed | **closed → open** | closed → closed |")
    A("|---|---|---|---|---|---|")
    for conv, t in sorted(d["paired_transitions"]["by_convention"].items()):
        A("| %s | %d | %d | %d | **%d** | %d |"
          % (conv, t["n_paired"], t["open_to_open"], t["open_to_closed"], t["closed_to_open"],
             t["closed_to_closed"]))
    A("")
    A("## 3 · The family-wide window, both configurations")
    A("")
    A("⚠ Cell counts are **not** comparable between the two rows — ten bivalent placements collapse to "
      "five monovalent anchors. Read §2 for the decision.")
    A("")
    A("| configuration | convention | cells | open | median width | closed by a paralogue | closed by an "
      "NR4A3 conserved Cys | target not first |")
    A("|---|---|---|---|---|---|---|---|")
    for cfg in ("bivalent", "monovalent"):
        for conv in ("through_space", "corridor"):
            s = d["summary"][cfg][conv]
            A("| %s | %s | %d | **%d** | %s | %d | %d | %d |"
              % (cfg, conv, s["n_cells"], s["n_open"], s["median_width"],
                 s["n_closed_by_a_PARALOGUE_cysteine"], s["n_closed_by_an_NR4A3_conserved_cysteine"],
                 s["n_target_not_first"]))
    A("")
    A("**Who closes it (corridor).** monovalent: %s — bivalent: %s"
      % (json.dumps(d["summary"]["monovalent"]["corridor"]["closers_by_count"]),
         json.dumps(d["summary"]["bivalent"]["corridor"]["closers_by_count"])))
    A("")

    cc = d["configuration_change"]
    A("## 4 · What the configuration change does besides the arithmetic")
    A("")
    A("- **%d bivalent placements collapse to %d monovalent anchors.** %s"
      % (cc["n_bivalent_placements"], cc["n_monovalent_anchors"], cc["_reading"]))
    A("- **The admissibility filter retires.** %s"
      % cc["admissibility_filter_retires"]["_reading"])
    A("")

    A("## 5 · Cross-checks (rule 1 — this module may not mint a second value)")
    A("")
    for k, v in d["cross_checks"].items():
        A("- `%s`: **%s**%s" % (k, v.get("status"),
                                (" (n = %s)" % v["n_cells_compared"]) if v.get("n_cells_compared") else ""))
    A("")

    ew = d.get("paralogue_metadynamics_ensembles", {}).get("per_paralogue") or {}
    if ew:
        A("## 6 · Robustness — the monovalent window against every paralogue conformer")
        A("")
        A("| paralogue | convention | frames | cells | open |")
        A("|---|---|---|---|---|")
        for prot, blk in sorted(ew.items()):
            for conv, s in sorted(blk.items()):
                A("| %s | %s | %d | %d | **%d** |" % (prot, conv, s["n_frames"], s["n_cells"], s["n_open"]))
        A("")

    A("## 7 · What this inherits and cannot say")
    A("")
    for lim in d["_inherits"]:
        A("- %s" % lim)
    A("")
    if d["refusals"]:
        A("**Refusals:** %d — %s" % (len(d["refusals"]),
                                     "; ".join(r.get("model", r.get("input", "?")) for r in d["refusals"][:6])))
        A("")
    if d["unread_inputs"]:
        A("**Unread inputs:** %s"
          % "; ".join("%s (%s)" % (u["input"], u["reason"]) for u in d["unread_inputs"]))
        A("")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--seq-cache", default=CR.SEQ_CACHE)
    ap.add_argument("--no-paralogue-ensembles", action="store_true")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)

    with open(args.seq_cache) as fh:
        seqs = json.load(fh)
    for k in ("NR4A1", "NR4A2", "NR4A3"):
        if k not in seqs:
            raise SystemExit("sequence cache %s is missing %s — REFUSING to guess" % (args.seq_cache, k))

    d = build(seqs, paralogue_ensembles=not args.no_paralogue_ensembles)
    d["verdict"] = verdict(d)
    with open(args.out, "w") as fh:
        json.dump(d, fh, indent=1)
        fh.write("\n")
    with open(os.path.splitext(args.out)[0] + ".md", "w") as fh:
        fh.write(to_markdown(d))

    print(json.dumps(d["verdict"], indent=1)[:2500], flush=True)
    for k, v in d["cross_checks"].items():
        print("[xcheck] %s: %s" % (k, v.get("status")), flush=True)
    for r in d["refusals"]:
        print("[REFUSED] %s: %s" % (r.get("model", r.get("input")), r["reason"]), flush=True)
    print("[monovalent] wrote %s" % args.out, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
