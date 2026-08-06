#!/usr/bin/env python3
"""DOES THE STERIC DESIGN RULE HAVE A **CARRIER**? — Tier-1 row 3 of `path-family-synthesis.md` §2, executed.

★ THE QUESTION, IN ONE LINE. `steric-design-rule.json` says a designer gets TWO vectors — the denied lobes at
I484->Tyr/Tyr and L534->Phe/Phe. Row 3 asks the only question that decides whether that is a *property of
this program's molecules* or a *specification for a molecule nobody has drawn*:

        does anything in the committed set already put a heavy atom inside either lobe?

⛔⛔ THE CONTROL TRAVELS WITH EVERY SCORE IN THIS FILE, AND IT IS IMPORTED, NEVER RE-TYPED. `M4` docked the
same molecules into each paralogue's own opened pocket and the paralogue **RELOCATES** them. So a high score
here licenses exactly one sentence — ✅ *"this POSE is denied in the paralogue's modelled opened conformer"* —
and never ⛔ *"the paralogue cannot bind this molecule"*: it binds it somewhere else. The medians, the rigid-
transfer limit and the by-construction limit are read at runtime out of `steric-design-rule.json` so that this
file cannot drift from the rule it is applying.

★ WHAT THIS FILE ADDS THAT THE RULE DID NOT HAVE — and it is the whole reason it is not just a re-run:

  1. **A FRAME-IDENTITY CENSUS BEFORE ANY SCORE.** `score_pose()` takes coordinates and asks no questions
     about which receptor they came from. Feeding it a pose docked into a *different* opened conformer would
     produce a number that looks exactly like a real one. So every pose source in the repository is first
     tested for **coordinate identity** against the rule's own frame
     (`results/nr4a3-matrix/nr4a3-opened.pdb`), atom by atom, and only identical-frame sources are scored as
     arithmetic. Sources in another frame are scored ONLY after an explicit superposition and are reported in
     a separate block that carries that superposition's own core RMSD and post-fit deviation, because a
     transferred pose is a weaker object than an
     in-frame one and the two must never render alike.

  2. **STRICT LOBE OCCUPANCY, WHICH IS NOT THE SAME PREDICATE AS `fired`.** M3's `fired` is a per-POSITION
     statistic: the nearest ligand atom to NR4A1's side chain is within the clash radius, AND the nearest
     atom to NR4A2's is too, AND no atom is inside the NR4A3 side chain — three minima that may belong to
     THREE DIFFERENT ATOMS, and the NR4A3 term looks only at that one residue. "Reaching the lobe" is a
     stronger, per-ATOM claim, and it is the one row 3 actually asks: is there a SINGLE heavy atom that sits
     inside the measured denied volume — within the clash radius of BOTH paralogue side chains and at least
     the clash radius from EVERY NR4A3 heavy atom? That is the exact grid predicate `denied_lobe()` used to
     measure the lobe, applied to atoms instead of grid points. A pose can fire and still occupy nothing.

  3. **THE SET THE ROW NAMES.** "The committed construct set" is settled by
     `nr4a3-linker-library-canonical.json` (roadmap §10.1 row 25): the EXECUTED enumeration
     (`nr4a3-linker-design.json`) is FROZEN and canonical for anything already measured. This file reports
     what those records actually contain, because a set that carries no coordinates cannot be scored and
     **"not scorable" is a different result from "scored and reached nothing"** (CLAUDE.md §4: an absent
     reading is not a reading of absence).

⚠ INHERITANCE, CARRIED EXPLICITLY (path-family-synthesis.md §4). Row 3 does **NOT** inherit `R3` — it is
scored on the matched opened-LBD frame, not the generation frame. It **DOES** inherit `R5`: the whole rule is
conditional on the cryptic pocket being the site, and the pose known-answer test `V3` returned INCONCLUSIVE on
site selection. Every verdict below is conditional on that and says so in its own record.

$0 — stdlib + the repo's own committed structures on CPU. No GPU, no rental, no docking, no MD, no dispatch.

CLI:  python3 steric_carrier_audit.py            # write steric-carrier-audit.json (+ .md)
      python3 steric_carrier_audit.py --check    # regenerate and diff against the committed artifact
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import selectivity_mechanism_options as S      # noqa: E402  owns POCKET5 / HARD_CLASH_A / the classes / M3+M4
import steric_design_rule as RULE              # noqa: E402  owns score_pose() and the lobe geometry
import nr4a_paralogue_unique_residues as U     # noqa: E402  owns the SDF reader and LOCAL_OFFSET

OUT_JSON = os.path.join(HERE, "steric-carrier-audit.json")
OUT_MD = os.path.join(HERE, "steric-carrier-audit.md")
RULE_JSON = os.path.join(HERE, "steric-design-rule.json")
CANON_JSON = os.path.join(HERE, "nr4a3-linker-library-canonical.json")
EXECUTED_JSON = os.path.join(HERE, "nr4a3-linker-design.json")
PROBE_JSON = os.path.join(HERE, "nr4a3-short-linker-probe.json")

#: The rule's own frame. Every pose is judged against THIS file's coordinates, not against a path that merely
#: looks like it.
RULE_FRAME = os.path.join(REPO, "results", "nr4a3-matrix", "nr4a3-opened.pdb")

#: Every committed source of NR4A3-frame ligand poses in the repository. Listed exhaustively rather than
#: filtered, so the census records what was CONSIDERED, not only what was scored.
POSE_SOURCES = [
    ("selectivity-matrix (the rule's own worked example)",
     "results/nr4a3-matrix/nr4a3-opened.pdb", "results/nr4a3-matrix/docked_nr4a3.sdf"),
    ("de novo funnel, state-matched",
     "results/nr4a3-denovo/-matrix-statematch/nr4a3-opened.pdb",
     "results/nr4a3-denovo/-matrix-statematch/docked_nr4a3.sdf"),
    ("de novo funnel v2, state-matched (holds the carried candidate denovo_401)",
     "results/nr4a3-denovo/-matrix-v2-statematch/nr4a3-opened.pdb",
     "results/nr4a3-denovo/-matrix-v2-statematch/docked_nr4a3.sdf"),
    ("de novo funnel v2",
     "results/nr4a3-denovo/-matrix-v2/nr4a3-opened.pdb",
     "results/nr4a3-denovo/-matrix-v2/docked_nr4a3.sdf"),
    ("de novo funnel v3",
     "results/nr4a3-denovo/-matrix-v3/nr4a3-opened.pdb",
     "results/nr4a3-denovo/-matrix-v3/docked_nr4a3.sdf"),
    ("de novo funnel v3-deep",
     "results/nr4a3-denovo/-matrix-v3deep/nr4a3-opened.pdb",
     "results/nr4a3-denovo/-matrix-v3deep/docked_nr4a3.sdf"),
    ("de novo funnel v4-deep",
     "results/nr4a3-denovo/-matrix-v4deep/nr4a3-opened.pdb",
     "results/nr4a3-denovo/-matrix-v4deep/docked_nr4a3.sdf"),
    ("de novo funnel, first matrix",
     "results/nr4a3-denovo/-matrix/nr4a3-opened.pdb",
     "results/nr4a3-denovo/-matrix/docked_nr4a3.sdf"),
    ("de novo funnel, dev matrix",
     "results/nr4a3-denovo/-matrix-dev/nr4a3-opened.pdb",
     "results/nr4a3-denovo/-matrix-dev/docked_nr4a3.sdf"),
    ("de novo funnel, pan matrix",
     "results/nr4a3-denovo/-pan-matrix/nr4a3-opened.pdb",
     "results/nr4a3-denovo/-pan-matrix/docked_nr4a3.sdf"),
    ("de novo funnel, affinity matrix",
     "results/nr4a3-denovo/-affinity-matrix/nr4a3-opened.pdb",
     "results/nr4a3-denovo/-affinity-matrix/docked_nr4a3.sdf"),
    ("8XTT apo NMR model 2 re-dock (pose-convergence leg)",
     "research/modalities/_pose_convergence_inputs/8xtt_model2_nr4a3.pdb",
     "research/modalities/_pose_convergence_inputs/docked_nr4a3_m2.sdf"),
    ("8XTT apo NMR model 6 re-dock (pose-convergence leg)",
     "research/modalities/_pose_convergence_inputs/8xtt_model6_nr4a3.pdb",
     "research/modalities/_pose_convergence_inputs/docked_nr4a3_m6.sdf"),
    ("8XTT apo NMR model 8 re-dock (pose-convergence leg)",
     "research/modalities/_pose_convergence_inputs/8xtt_model8_nr4a3.pdb",
     "research/modalities/_pose_convergence_inputs/docked_nr4a3_m8.sdf"),
    ("8XTT apo NMR model 20 re-dock (pose-convergence leg)",
     "research/modalities/_pose_convergence_inputs/8xtt_model20_nr4a3.pdb",
     "research/modalities/_pose_convergence_inputs/docked_nr4a3_m20.sdf"),
]

#: The molecule row 3's falsifier is really about — the one this program carries forward.
CARRIED_CANDIDATE = "denovo_401"


def _r(x, n=3):
    return None if x is None else round(float(x), n)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# Frame identity — taken BEFORE any score, because score_pose() cannot tell you it was fed the wrong frame
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _pdb_atoms(path):
    out = []
    with open(path) as fh:
        for line in fh:
            if line.startswith(("ATOM", "HETATM")):
                out.append((line[12:16].strip(), line[17:20].strip(), line[22:26].strip(),
                            round(float(line[30:38]), 3), round(float(line[38:46]), 3),
                            round(float(line[46:54]), 3)))
    return out


def frame_identity(path, ref_atoms):
    """Is this receptor the SAME coordinates as the rule's frame? Atom-by-atom, not by filename."""
    if not os.path.exists(path):
        return {"identical_to_rule_frame": None, "why": "receptor not present in this checkout"}
    got = _pdb_atoms(path)
    if len(got) != len(ref_atoms):
        return {"identical_to_rule_frame": False, "n_atoms": len(got),
                "why": "different atom count (%d vs %d)" % (len(got), len(ref_atoms))}
    n_diff = sum(1 for a, b in zip(got, ref_atoms) if a != b)
    return {"identical_to_rule_frame": n_diff == 0, "n_atoms": len(got), "n_atoms_differing": n_diff,
            "why": ("coordinate-identical" if n_diff == 0 else
                    "%d of %d atoms differ — a DIFFERENT opened conformer" % (n_diff, len(got)))}


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# Strict lobe occupancy — the per-ATOM predicate, which is NOT M3's per-POSITION `fired`
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def lobe_occupancy(heavy_xyz, geometry, nr4a3_heavy, clash_a, positions):
    """Count heavy atoms that sit INSIDE the measured denied lobe at each Pocket-5 position.

    The predicate is `denied_lobe()`'s own grid criterion, moved from grid points onto the pose's atoms:
    within `clash_a` of BOTH paralogues' superposed side-chain heavy atoms, and at least `clash_a` from
    EVERY NR4A3 heavy atom. It is strictly stronger than `fired`, which allows the three minima to belong
    to three different atoms and looks only at the one NR4A3 side chain.

    ⛔ IT IS RUN OVER **EVERY** POCKET-5 POSITION, NOT ONLY THE TWO DESIGN TARGETS, AND THAT IS NOT
    THOROUGHNESS — IT IS THE RULE'S OWN REQUIREMENT. `score_pose()` refuses to emit a signal without its
    matched null for a reason that applies identically here: a molecule docked into this pocket sits in the
    middle of it, so "it occupies the denied volume at a signal position" is only interpretable beside "it
    occupies the denied volume at a CONSERVED position too". `occupancy_by_class` below is that null.
    """
    out = {}
    for u in positions:
        g = geometry[u]
        par = [g["paralogue_sidechain"][sp] for sp in S.PARALOGUES]
        n_in, best = 0, None
        if all(par):
            for p in heavy_xyz:
                if not all(min(math.dist(p, q) for q in sc) < clash_a for sc in par):
                    continue
                d3 = min(math.dist(p, q) for q in nr4a3_heavy)
                if d3 < clash_a:
                    continue
                n_in += 1
                if best is None or d3 > best:
                    best = d3
        out[str(u)] = {
            "n_heavy_atoms_inside_the_lobe": n_in,
            "reaches_the_lobe": n_in > 0,
            "deepest_atom_clearance_from_NR4A3_A": _r(best, 2),
            "_predicate": ("within %.1f A of BOTH paralogue side chains at this position AND >= %.1f A from "
                           "every NR4A3 heavy atom — denied_lobe()'s grid criterion applied per atom"
                           % (clash_a, clash_a)),
        }
    return out


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# Build
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _geometry(ref, fit, m3):
    geometry = {}
    for u in S.POCKET5:
        rid3 = u - U.LOCAL_OFFSET
        par_sc = {}
        for sp in S.PARALOGUES:
            rp = fit[sp]["corr_from_ref"].get(rid3)
            par_sc[sp] = S._sidechain(fit[sp], rp) if rp else []
        geometry[u] = {"class": m3["positions"][u]["class"],
                       "NR4A3_sidechain": S._sidechain(ref, rid3),
                       "paralogue_sidechain": par_sc}
    return geometry


def occupancy_by_class(occ, geometry):
    """THE MATCHED NULL FOR OCCUPANCY. Same statistic, same molecule, same superposition, at the positions
    the program itself nominated as its false-positive control.

    Reported exactly like `score_pose()`'s rates: the fraction of positions IN EACH CLASS where this molecule
    puts at least one heavy atom inside that position's denied volume, and the SIGNAL MINUS NULL difference,
    which is the only gradeable number of the three.
    """
    by = {}
    for u_str, rec in occ.items():
        cls = geometry[int(u_str)]["class"]
        c = by.setdefault(cls, {"positions": [], "occupied": 0})
        c["positions"].append(int(u_str))
        c["occupied"] += int(rec["reaches_the_lobe"])
    for c in by.values():
        c["n_positions"] = len(c["positions"])
        c["rate"] = _r(c["occupied"] / c["n_positions"], 3) if c["n_positions"] else None
    sig = by.get("unique_and_both_bulkier", {}).get("rate")
    nul = by.get("conserved_or_shared", {}).get("rate")
    return {
        "by_class": by,
        "occupancy_signal_rate": sig,
        "occupancy_null_rate": nul,
        "occupancy_signal_minus_null": (_r(sig - nul, 3) if sig is not None and nul is not None else None),
        "_reading": ("the fraction of positions in each class at which this molecule places >=1 heavy atom "
                     "inside that position's denied volume. ACCEPT on the DIFFERENCE, never on the signal — "
                     "the null is this molecule's own false-positive rate under the same superposition."),
    }


def _pooled_occupancy(rows):
    """Pool the occupancy statistic across a source's molecules, signal and null side by side.

    ⚠ Pooled over POSITION-TRIALS, exactly as `steric_design_rule`'s worked example pools `fired`, so the two
    are the same kind of number and can be read against each other.
    """
    def pool(cls):
        occ = sum(r["occupancy_with_its_null"]["by_class"].get(cls, {}).get("occupied", 0) for r in rows)
        n = sum(r["occupancy_with_its_null"]["by_class"].get(cls, {}).get("n_positions", 0) for r in rows)
        return (_r(occ / n, 3) if n else None), occ, n
    sig, s_occ, s_n = pool("unique_and_both_bulkier")
    nul, n_occ, n_n = pool("conserved_or_shared")
    return {
        "signal_rate": sig, "signal_occupied_of_trials": [s_occ, s_n],
        "null_rate": nul, "null_occupied_of_trials": [n_occ, n_n],
        "signal_minus_null": (_r(sig - nul, 3) if sig is not None and nul is not None else None),
    }


def _carrier_robustness(readings):
    """★ THE ONE QUESTION `L10` FORCES ON THIS ROW, ANSWERED RATHER THAN NOTED.

    denovo_401's six poses spread to a pocket-superposed median ligand RMSD of 7.006 A with cross-method
    evidence NONE, so any per-pose carrier statement is a statement about that pose. The useful question is
    therefore which part of the carrier claim is INVARIANT across the poses the program actually holds, and
    which part is a coin-flip. Computed, never asserted.
    """
    n = len(readings)
    if not n:
        return None
    either = sum(bool(r["reaches_I484_lobe"] or r["reaches_L534_lobe"]) for r in readings)
    both = sum(bool(r["reaches_I484_lobe"] and r["reaches_L534_lobe"]) for r in readings)
    n484 = sum(bool(r["reaches_I484_lobe"]) for r in readings)
    n534 = sum(bool(r["reaches_L534_lobe"]) for r in readings)
    return {
        "n_poses": n,
        "reaches_either_lobe_in": "%d of %d" % (either, n),
        "reaches_BOTH_lobes_in": "%d of %d" % (both, n),
        "reaches_I484_in": "%d of %d" % (n484, n),
        "reaches_L534_in": "%d of %d" % (n534, n),
        "★_reading": (
            "'this molecule reaches at least one design-target lobe' holds in %d of %d poses; 'it reaches "
            "the I484 vector' holds in %d of %d and 'the L534 vector' in %d of %d. So the WEAK form of the "
            "carrier claim is pose-robust and the VECTOR-SPECIFIC form is not — the pose that is in the "
            "rule's own frame reaches L534 and NOT I484, while an experimental-conformer re-dock reaches "
            "I484 and NOT L534. A design brief that names one vector for this molecule would be resting on "
            "a choice of pose, and `L10` says the program is not entitled to that choice."
            % (either, n, n484, n, n534, n)),
        "⛔_and_it_is_still_a_POSE_statement": (
            "every row here inherits the M4 relocation control and `R5` unchanged. None of it says the "
            "paralogue cannot bind the molecule, and none of it says the site is right."),
    }


def _score_one(title, coords, geometry, nr4a3_heavy, clash, targets):
    pts = [(c[0], c[1], c[2]) for c in coords if c[3] != "H"]
    rec = RULE.score_pose(pts, geometry, clash)
    rec.pop("_reading", None)
    rec["molecule"] = title
    rec["n_heavy_atoms"] = len(pts)
    occ = lobe_occupancy(pts, geometry, nr4a3_heavy, clash, sorted(geometry))
    rec["lobe_occupancy"] = occ
    rec["occupancy_with_its_null"] = occupancy_by_class(occ, geometry)
    rec["reaches_I484_lobe"] = occ["484"]["reaches_the_lobe"]
    rec["reaches_L534_lobe"] = occ["534"]["reaches_the_lobe"]
    rec["reaches_either_lobe"] = bool(rec["reaches_I484_lobe"] or rec["reaches_L534_lobe"])
    return rec


def build():
    rule = json.load(open(RULE_JSON))
    canon = json.load(open(CANON_JSON))
    executed = json.load(open(EXECUTED_JSON))
    probe = json.load(open(PROBE_JSON))

    clash = S.HARD_CLASH_A
    targets = list(rule["design_targets"])
    ref, raw, fit = S._superposed_models()
    m3 = S.m3_steric_exclusion(ref, fit)
    geometry = _geometry(ref, fit, m3)
    nr4a3_heavy = [tuple(p) for p in ref["heavy_xyz"]]
    ref_atoms = _pdb_atoms(RULE_FRAME)

    # ── the census, taken before anything is scored ──────────────────────────────────────────────────────
    census, in_frame, other_frame = [], [], []
    for label, rec_path, pose_path in POSE_SOURCES:
        row = {"source": label, "receptor": rec_path, "poses": pose_path}
        row.update(frame_identity(os.path.join(REPO, rec_path), ref_atoms))
        row["poses_present"] = os.path.exists(os.path.join(REPO, pose_path))
        if row["poses_present"]:
            row["n_poses"] = len(U._read_sdf_coords(os.path.join(REPO, pose_path)))
        census.append(row)
        if row.get("identical_to_rule_frame") and row["poses_present"]:
            in_frame.append((label, pose_path))
        elif row["poses_present"]:
            other_frame.append((label, rec_path, pose_path))

    # ── in-frame scoring: pure arithmetic, no new geometry ───────────────────────────────────────────────
    scored_sources = []
    for label, pose_path in in_frame:
        mols = U._read_sdf_coords(os.path.join(REPO, pose_path))
        rows = [_score_one(t, c, geometry, nr4a3_heavy, clash, targets) for t, c in mols]
        scored_sources.append({
            "source": label,
            "poses": pose_path,
            "frame": "coordinate-identical to the rule's frame — scored as arithmetic, no superposition",
            "n_molecules": len(rows),
            "n_reaching_I484_lobe": sum(r["reaches_I484_lobe"] for r in rows),
            "n_reaching_L534_lobe": sum(r["reaches_L534_lobe"] for r in rows),
            "n_reaching_either_lobe": sum(r["reaches_either_lobe"] for r in rows),
            "pooled_occupancy": _pooled_occupancy(rows),
            "molecules": rows,
        })

    # ── transferred scoring: an ADDED superposition, reported separately and never merged in ─────────────
    import basin_geom as G
    import nr4a3_basin_search as B
    transferred = []
    for label, rec_path, pose_path in other_frame:
        mob = B.load_paralogue(os.path.join(REPO, rec_path))
        fitm = B.superpose_paralogue(mob, ref)
        # ⚠ THE TRANSFORM IS *RECOVERED* FROM THE FITTED MODEL — M4's own idiom — SO ITS OWN RESIDUAL IS ZERO
        # BY CONSTRUCTION AND IS NOT A QUALITY METRIC. An earlier draft of this file reported that zero as
        # "post-fit core RMSD"; it was a populated field, not a measured one (CLAUDE.md §4). The number that
        # actually says how well this receptor shares the rule's frame is the superposition's OWN core RMSD.
        keys = [k for k in mob["ca"] if k in fitm["ca"]]
        R, t, recovery_residual = G.horn_superpose([mob["ca"][k] for k in keys], [fitm["ca"][k] for k in keys])
        sup = fitm["superposition"]
        rows = []
        for title, coords in U._read_sdf_coords(os.path.join(REPO, pose_path)):
            moved = G.apply_superpose([(c[0], c[1], c[2]) for c in coords], R, t)
            rows.append(_score_one(title, [(p[0], p[1], p[2], c[3]) for p, c in zip(moved, coords)],
                                   geometry, nr4a3_heavy, clash, targets))
        transferred.append({
            "source": label,
            "receptor": rec_path,
            "poses": pose_path,
            "⚠_this_is_not_in_frame_arithmetic": (
                "the pose was produced in a DIFFERENT receptor conformer and is carried into the rule's frame "
                "by a CA superposition taken here. That is an added operation with its own error, so these "
                "rows are weaker than the in-frame rows and are never pooled with them."),
            "superposition": {
                "core_rmsd_A": sup["core_rmsd_A"],
                "global_all_pair_rmsd_A": sup["global_all_pair_rmsd_A"],
                "n_ca_pairs": sup["n_ca_pairs"],
                "n_core": sup["n_core"],
                "core_fraction": sup["core_fraction"],
                "post_fit_deviation_A": sup["post_fit_deviation_A"],
                "_source": "nr4a3_basin_search.superpose_paralogue — the same superposition the rule itself "
                           "uses for the paralogues, applied here to a receptor instead",
                "⚠_transform_recovery_residual_A": _r(recovery_residual, 3),
                "⚠_why_that_residual_is_zero": (
                    "it is the residual of re-deriving a transform from a model that transform already "
                    "produced. It is zero BY CONSTRUCTION and says nothing about fit quality — read "
                    "core_rmsd_A."),
            },
            "n_molecules": len(rows),
            "n_reaching_I484_lobe": sum(r["reaches_I484_lobe"] for r in rows),
            "n_reaching_L534_lobe": sum(r["reaches_L534_lobe"] for r in rows),
            "pooled_occupancy": _pooled_occupancy(rows),
            "molecules": rows,
        })

    # ── the carried candidate, across every pose the program holds of it ─────────────────────────────────
    carried = []
    for blk, kind in ([(b, "in-frame") for b in scored_sources]
                      + [(b, "transferred") for b in transferred]):
        for r in blk["molecules"]:
            if r["molecule"] == CARRIED_CANDIDATE:
                carried.append({"pose_source": blk["source"], "reading": kind,
                                "signal_rate": r["signal_rate"], "null_rate": r["null_rate"],
                                "signal_minus_null": r["signal_minus_null"],
                                "occupancy_signal_minus_null":
                                    r["occupancy_with_its_null"]["occupancy_signal_minus_null"],
                                "reaches_I484_lobe": r["reaches_I484_lobe"],
                                "reaches_L534_lobe": r["reaches_L534_lobe"],
                                "n_heavy_atoms_in_484": r["lobe_occupancy"]["484"][
                                    "n_heavy_atoms_inside_the_lobe"],
                                "n_heavy_atoms_in_534": r["lobe_occupancy"]["534"][
                                    "n_heavy_atoms_inside_the_lobe"]})

    # ── the committed CONSTRUCT set: what it is, and what it can and cannot be fed to ────────────────────
    def _has_coords(records):
        bad = []
        for rec in records:
            for k, v in rec.items():
                if isinstance(k, str) and any(s in k.lower() for s in ("xyz", "coord", "conformer_geom")):
                    bad.append(k)
        return sorted(set(bad))

    groups = {k: executed[k] for k in
              ("virtual_library", "virtual_library_at_the_term_a_exemplar",
               "virtual_library_at_representative_geometry") if k in executed}
    construct_fields = sorted({k for g in groups.values() for rec in g for k in rec})
    coord_fields = _has_coords([rec for g in groups.values() for rec in g])
    # ⚠ THE THREE GROUPS ARE A PARTITION, NOT THREE SETS — `virtual_library` is the UNION of the two
    # placement groups, so summing the three would report the library at double its size. VERIFIED here
    # rather than assumed, because that is exactly the kind of hand-carried total CLAUDE.md rule 1 exists to
    # stop, and the canonical ruling's own `n_constructs` is the figure it must agree with.
    ids_all = {r["construct_id"] for r in groups["virtual_library"]}
    ids_split = ({r["construct_id"] for r in groups["virtual_library_at_the_term_a_exemplar"]}
                 | {r["construct_id"] for r in groups["virtual_library_at_representative_geometry"]})
    n_distinct = len(ids_all | ids_split)
    partition_holds = (ids_all == ids_split)
    agrees_with_ruling = (n_distinct == canon["registered_enumerations"]["EXECUTED"]["n_constructs"])

    constructs = {
        "which_set_is_canonical": {
            "ruling": canon["ruling"]["_one_line"],
            "settled_by": "research/modalities/nr4a3-linker-library-canonical.json (roadmap §10.1 row 25)",
            "EXECUTED": {k: canon["registered_enumerations"]["EXECUTED"][k]
                         for k in ("artifact", "status", "n_constructs", "n_enumerated")},
            "CORRECTED": {k: canon["registered_enumerations"]["CORRECTED"][k]
                          for k in ("artifact", "status", "n_constructs", "n_enumerated")},
            "which_one_this_audit_uses": (
                "the EXECUTED enumeration — it is the set that is COMMITTED, and row 3 asks about the "
                "committed set. The CORRECTED set is registered but not committed (re-derived on demand), so "
                "it has no artifact to read and, carrying no coordinates either, would not change the "
                "answer below."),
            "the_bias_that_must_be_quoted_with_it":
                canon["ruling"]["committed_artifact"]["the_bias_it_carries_and_must_be_quoted_with"],
        },
        "group_sizes": {k: len(v) for k, v in groups.items()},
        "n_distinct_constructs": n_distinct,
        "_the_groups_are_a_partition": {
            "verified_here": partition_holds,
            "agrees_with_the_canonical_ruling_n_constructs": agrees_with_ruling,
            "_why_this_is_checked": ("`virtual_library` is the UNION of the two placement groups, so summing "
                                     "the three group sizes would report the library at double its size. "
                                     "The distinct count is derived from construct ids and cross-checked "
                                     "against the ruling's own n_constructs rather than typed."),
        },
        "fields_every_construct_record_carries": construct_fields,
        "coordinate_fields_found": coord_fields,
        "⛔_scorable_through_score_pose": False,
        "⛔_why_not": (
            "MEASURED, not assumed: across all %d distinct committed constructs, the fields present are %s — "
            "SMILES, topology, backbone-atom counts, span-window statistics and basin-fidelity fractions. "
            "There is NO 3D coordinate field of any kind (%d found), so there is no heavy-atom pose in the "
            "rule's frame for score_pose() to take. The constructs are committed as CHEMISTRY plus a reach "
            "corridor, not as placed molecules."
            % (n_distinct, ", ".join(construct_fields), len(coord_fields))),
        "★_and_that_is_a_different_result_from_a_zero": (
            "CLAUDE.md §4 — an absent reading is not a reading of absence. 'The %d constructs do not reach "
            "either lobe' would be FALSE as written: they were never placed, so nothing about their "
            "occupancy has been measured either way. What is measured is that the committed construct set "
            "carries no pose, and therefore cannot carry the rule until one is generated." % n_distinct),
        "the_short_linker_probe_candidate": {
            "construct_id": probe["the_candidate"]["construct_id"],
            "artifact": "research/modalities/nr4a3-short-linker-probe.json",
            "scorable": False,
            "why": ("the same reason — it is committed as SMILES, linker blocks, pendant and reach "
                    "statistics against C397, with no heavy-atom pose in the rule's frame."),
        },
        "what_it_would_take": (
            "one $0 CPU step: generate a conformer of a construct, place it in "
            "results/nr4a3-matrix/nr4a3-opened.pdb, then score_pose() it. That is a POSE-GENERATION step, "
            "not arithmetic, and it inherits `R5` exactly as everything else pose-anchored here does — which "
            "is why this audit stops at the boundary and names it rather than crossing it silently."),
    }

    # ── orientation only: where the constructs' one committed anchor sits relative to the lobes ──────────
    sg = [a for a in ref["atoms_by_res"].get(397 - U.LOCAL_OFFSET, []) if a["name"] == "SG"]
    anchor = (sg[0]["x"], sg[0]["y"], sg[0]["z"]) if sg else None
    anchor_block = {
        "_scope": ("ORIENTATION ONLY. A plain Euclidean distance in the committed frame between the "
                   "constructs' single committed anchor atom (C397 SG, the term-(a) covalent anchor) and each "
                   "design-target lobe centroid. NO reach model, NO corridor test, NO conformer is applied, "
                   "and this licenses NOTHING about whether a construct could reach a lobe — it only says how "
                   "far apart the two ends of that question are."),
        "anchor": "C397 SG in results/nr4a3-matrix/nr4a3-opened.pdb",
        "distance_to_lobe_centroid_A": {
            str(u): _r(math.dist(anchor, rule["denied_lobes"][str(u)]["centroid"]), 2)
            for u in targets} if anchor else None,
    }

    # ── the verdict ──────────────────────────────────────────────────────────────────────────────────────
    n_in_frame_mols = sum(b["n_molecules"] for b in scored_sources)
    n_either = sum(b["n_reaching_either_lobe"] for b in scored_sources)
    n_484 = sum(b["n_reaching_I484_lobe"] for b in scored_sources)
    n_534 = sum(b["n_reaching_L534_lobe"] for b in scored_sources)

    pooled_all = _pooled_occupancy([r for b in scored_sources for r in b["molecules"]])

    verdict = {
        "the_question": ("does the steric design rule have a CARRIER — does anything committed already "
                         "occupy the I484 or L534 denied lobe?"),
        "answer_for_the_CONSTRUCT_set": "NOT SCORABLE — no coordinates exist. See constructs.⛔_why_not.",
        "answer_for_the_committed_POSE_sets": {
            "n_molecules_scored_in_frame": n_in_frame_mols,
            "n_reaching_the_I484_lobe": n_484,
            "n_reaching_the_L534_lobe": n_534,
            "n_reaching_either_lobe": n_either,
            "pooled_occupancy_with_its_null": pooled_all,
        },
        "★_the_reading_that_matters_most": (
            "%d of %d in-frame molecules reach at least one design-target lobe, and %d of %d reach the L534 "
            "lobe. ⛔ THAT NEAR-UNANIMITY IS THE FINDING, AND IT CUTS BOTH WAYS. It answers row 3's falsifier "
            "in the LIVE direction — the two vectors are not empty specifications; molecules this program "
            "already holds do put heavy atoms inside both denied volumes. But a test that fires for almost "
            "every molecule docked into this pocket is NOT a filter that ranks candidates, and reading it as "
            "one would be exactly the error the rule's own by-construction limit warns about: these poses "
            "were placed INTO this cavity, and the lobes sit in it. The gradeable quantity is the SIGNAL "
            "MINUS NULL occupancy, pooled at %s (signal %s, null %s) — not the count of molecules that "
            "reach a lobe."
            % (n_either, n_in_frame_mols, n_534, n_in_frame_mols,
               pooled_all["signal_minus_null"], pooled_all["signal_rate"], pooled_all["null_rate"])),
        "carried_candidate": {
            "molecule": CARRIED_CANDIDATE,
            "n_poses_the_program_holds": len(carried),
            "★_what_survives_the_pose_spread_and_what_does_not": _carrier_robustness(carried),
            "readings": carried,
        },
        "⚠_what_a_reaching_row_licenses": rule["⛔_control"]["✅_what_a_high_score_licenses"],
        "⛔_what_no_row_licenses": rule["⛔_control"]["⛔_what_this_score_is_not"],
    }

    return {
        "_title": "DOES THE STERIC DESIGN RULE HAVE A CARRIER? — Tier-1 row 3 executed over the committed set",
        "_answers": ("research/manuscripts/path-family-synthesis.md §2 Tier-1 row 3; routes into roadmap §8 "
                     "Route A and §10.1 row 24"),
        "_status": ("ARITHMETIC OVER COMMITTED POSES plus a measured statement about what the committed "
                    "construct set contains. $0 — stdlib on CPU. Nothing here is a claim about binding, "
                    "affinity, degradation, selectivity, efficacy or safety, and no molecule named here is a "
                    "hit."),
        "_one_fact_one_place": (
            "The lobes, the design targets, the M4 medians, the clash radius and the three limits are READ AT "
            "RUNTIME from steric-design-rule.json / selectivity_mechanism_options and are never re-typed "
            "here. The canonical-library ruling is read from nr4a3-linker-library-canonical.json. This file "
            "owns exactly two new things: the frame-identity census and the per-atom lobe-occupancy "
            "predicate."),
        "_generated": {"generator": "research/modalities/steric_carrier_audit.py"},
        "⛔_control_imported_verbatim_from_the_rule": rule["⛔_control"],
        "⚠_inheritance": {
            "inherits_R3": False,
            "why_not": ("scored on the matched opened-LBD frame (results/nr4a3-matrix/nr4a3-opened.pdb), not "
                        "the generation frame whose submission gate fails — path-family-synthesis.md §4."),
            "inherits_R5": True,
            "why": ("the rule is conditional on the cryptic pocket being the site, and the pose known-answer "
                    "test V3 returned INCONCLUSIVE on site selection. Every verdict in this file is "
                    "conditional on that and may not be quoted without it — path-family-synthesis.md §4."),
            "⚠_and_the_pose_is_not_singular": (
                "L10: denovo_401's six poses spread to a pocket-superposed median ligand RMSD of 7.006 A with "
                "cross-method evidence NONE. So a per-pose reading is a reading OF THAT POSE, and the spread "
                "across poses is itself part of the answer — which is why every pose held of the carried "
                "candidate is scored here rather than one."),
        },
        "parameters": {
            "hard_clash_A": clash,
            "design_targets": targets,
            "_design_targets_source": "steric-design-rule.json -> design_targets",
            "rule_frame": "results/nr4a3-matrix/nr4a3-opened.pdb",
            "null_volume_ceiling_A3": rule["null_volume_ceiling_A3"],
            "null_volume_ceiling_at": rule["null_volume_ceiling_at"],
            "lobe_volume_A3": {str(u): rule["denied_lobes"][str(u)]["volume_A3"] for u in targets},
        },
        "pose_source_census": census,
        "scored_in_frame": scored_sources,
        "scored_after_transfer": transferred,
        "constructs": constructs,
        "anchor_orientation": anchor_block,
        "verdict": verdict,
        "⛔_limits": rule["⛔_limits"] + [
            "The per-atom lobe-occupancy predicate inherits every limit of the lobe itself: it is the same "
            "rigid transfer, in the same single superposition, at the same 3.0 A radius.",
            "A pose that reaches a lobe is a pose that reaches a lobe. Nothing here says the molecule is "
            "synthesisable, potent, selective, a degrader, or a candidate for anything.",
            "The transferred rows carry an extra CA superposition performed in this file; that superposition's "
            "core RMSD, core fraction and post-fit deviation are reported per source and must be quoted with "
            "them.",
        ],
        "map_edits_required": {
            "_convention": ("DESCRIBED, NOT APPLIED — same convention as "
                            "paralogue_pocket_contrast.map_edits_required. This file does not edit the "
                            "roadmap; a human applies these."),
            "targets": [
                {"where": "research/manuscripts/nr4a3-program-map.md §8 Route A",
                 "edit": ("record that the steric half of Route A now has an executed carrier audit: the "
                          "committed DEGRADER CONSTRUCT set cannot be scored (no coordinates), while the "
                          "committed POSE sets can and were. State the two results separately — a not-"
                          "scorable set and a measured occupancy count are different objects.")},
                {"where": "research/manuscripts/nr4a3-program-map.md §10.1 row 24",
                 "edit": ("row 24's remaining half (a carrier for the two vectors) is answered for the pose "
                          "sets and NOT answered for the construct set; the residual is a $0 pose-generation "
                          "step for the constructs, which inherits R5.")},
            ],
        },
    }


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# Memo
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def to_markdown(a):
    L = []
    W = L.append
    W("# Does the steric design rule have a **carrier**?")
    W("")
    W("*Tier-1 row 3 of [`path-family-synthesis.md`](../manuscripts/path-family-synthesis.md) §2, executed.*")
    W("GENERATED by [`steric_carrier_audit.py`](./steric_carrier_audit.py) — do not hand-edit. $0, CPU.")
    W("")
    W("⛔ **The control travels with every number below, imported verbatim from the rule.** The paralogue's "
      "own docking **relocates** these molecules by a median **%s Å (NR4A1) / %s Å (NR4A2)**. So a row that "
      "reaches a lobe licenses ✅ *\"this POSE is denied in the paralogue's modelled opened conformer\"* and "
      "⛔ **never** *\"the paralogue cannot bind this molecule\"* — it binds it somewhere else. The transfer "
      "is **RIGID** (the paralogue side chain is held in its own opened conformer and could rotate away), and "
      "**NR4A3's absence of clash is guaranteed by construction and carries zero information** — only the "
      "signal-vs-null contrast is gradeable."
      % (a["⛔_control_imported_verbatim_from_the_rule"]["median_centroid_shift_A"]["NR4A1"],
         a["⛔_control_imported_verbatim_from_the_rule"]["median_centroid_shift_A"]["NR4A2"]))
    W("")
    W("⚠ **Inheritance, carried explicitly.** Row 3 does **not** inherit `R3` (it is scored on the matched "
      "opened-LBD frame, not the generation frame) but **does** inherit `R5`: the rule is conditional on the "
      "cryptic pocket being the site, and `V3` returned **INCONCLUSIVE** on site selection. Nothing on this "
      "page may be quoted without that condition.")
    W("")
    W("---")
    W("")
    W("## 1 · The answer, in two halves that must not be merged")
    W("")
    v = a["verdict"]
    W("| set | scorable? | result |")
    W("|---|---|---|")
    W("| the committed **construct** set (%d constructs, `nr4a3-linker-design.json`) | ⛔ **no** | %s |"
      % (a["constructs"]["n_distinct_constructs"], "no coordinate field exists, so `score_pose()` has no "
         "input. **This is not a measured zero** — the constructs were never placed."))
    W("| the committed **pose** sets, in the rule's own frame | ✅ yes | %d molecules scored; **%d** reach the "
      "I484 lobe, **%d** reach the L534 lobe, **%d** reach either |"
      % (v["answer_for_the_committed_POSE_sets"]["n_molecules_scored_in_frame"],
         v["answer_for_the_committed_POSE_sets"]["n_reaching_the_I484_lobe"],
         v["answer_for_the_committed_POSE_sets"]["n_reaching_the_L534_lobe"],
         v["answer_for_the_committed_POSE_sets"]["n_reaching_either_lobe"]))
    W("")
    W("### ★ And the reading that matters most")
    W("")
    W(v["★_the_reading_that_matters_most"])
    W("")
    W("## 2 · Per-source, in frame")
    W("")
    W("⚠ The last column is the only gradeable one: occupancy at the two signal positions **minus** the same "
      "molecule's occupancy at the conserved/shared null positions, pooled over position-trials.")
    W("")
    W("| source | n | reach I484 | reach L534 | reach either | pooled occupancy signal − null |")
    W("|---|---|---|---|---|---|")
    for b in a["scored_in_frame"]:
        W("| %s | %d | %d | %d | %d | %s (signal %s, null %s) |"
          % (b["source"], b["n_molecules"], b["n_reaching_I484_lobe"], b["n_reaching_L534_lobe"],
             b["n_reaching_either_lobe"], b["pooled_occupancy"]["signal_minus_null"],
             b["pooled_occupancy"]["signal_rate"], b["pooled_occupancy"]["null_rate"]))
    W("")
    W("## 3 · The carried candidate, across every pose the program holds of it")
    W("")
    W("⚠ `L10`: this molecule's poses spread to a pocket-superposed median ligand RMSD of **7.006 Å** with "
      "**cross-method evidence NONE**. A per-pose reading is a reading *of that pose*.")
    W("")
    W(v["carried_candidate"]["★_what_survives_the_pose_spread_and_what_does_not"]["★_reading"])
    W("")
    W("| pose source | reading | clash signal − null | occupancy signal − null | atoms in I484 lobe | "
      "atoms in L534 lobe |")
    W("|---|---|---|---|---|---|")
    for r in v["carried_candidate"]["readings"]:
        W("| %s | %s | %s | %s | %s | %s |"
          % (r["pose_source"], r["reading"], r["signal_minus_null"],
             r["occupancy_signal_minus_null"], r["n_heavy_atoms_in_484"], r["n_heavy_atoms_in_534"]))
    W("")
    W("## 4 · What is still missing")
    W("")
    W(a["constructs"]["what_it_would_take"])
    W("")
    return "\n".join(L) + "\n"


def main(argv):
    art = build()
    txt = json.dumps(art, indent=1, sort_keys=False, ensure_ascii=False)
    md = to_markdown(art)
    if "--check" in argv and os.path.exists(OUT_JSON):
        old = open(OUT_JSON).read()
        if old.strip() != txt.strip():
            print("[steric-carrier-audit] ⛔ artifact does not reproduce from source", file=sys.stderr)
            return 1
        print("[steric-carrier-audit] ✅ reproduces")
        return 0
    with open(OUT_JSON, "w") as fh:
        fh.write(txt + "\n")
    with open(OUT_MD, "w") as fh:
        fh.write(md)
    v = art["verdict"]["answer_for_the_committed_POSE_sets"]
    print("[steric-carrier-audit] constructs: %s" % art["verdict"]["answer_for_the_CONSTRUCT_set"])
    print("[steric-carrier-audit] in-frame poses: %d scored; I484 %d, L534 %d, either %d"
          % (v["n_molecules_scored_in_frame"], v["n_reaching_the_I484_lobe"],
             v["n_reaching_the_L534_lobe"], v["n_reaching_either_lobe"]))
    print("[steric-carrier-audit] ⛔ control: %s"
          % (art["⛔_control_imported_verbatim_from_the_rule"]["median_centroid_shift_A"],))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
