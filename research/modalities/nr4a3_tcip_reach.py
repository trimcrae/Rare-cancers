#!/usr/bin/env python3
"""
DOES THE REACH ENUMERATION ADMIT A TRANSCRIPTIONAL EFFECTOR AS THE SECOND TERMINUS? ($0, CPU/CI only.)

THE ROUTE. `RT-TCIP` (systems/graph/routes.json) proposes spending an NR4A3-LBD binder on REWIRING rather
than degradation: a bivalent molecule whose second terminus recruits a transcriptional effector instead of an
E3 ligase. Its `best_next_action` is *"Run the paired anchor-plus-effector reach enumeration with a
transcriptional-effector second terminus, reusing the E3-free machinery"*, and `PUB-TCIP` is unwritten
because *"the machinery exists and takes one more anchor set"*.

★★ WHAT "ONE MORE ANCHOR SET" ACTUALLY MEANS — MEASURED, NOT RECALLED, AND IT IS NOT WHAT THE PHRASE
   SUGGESTS. The reach modules (`nr4a3_linker_covalent_reach`, `nr4a3_monovalent_reach`) consume exactly TWO
   points per cell: `a`, the warhead exit-vector anchor at the cryptic-pocket mouth, and `b`, the second
   terminus's ligand exit atom (`anchor_e3_xyz`). `a` is target-side and is reused unchanged. `b` is NOT an
   input anyone can type: it is PRODUCED by `nr4a3_basin_search.sample_placements`, which needs a staged
   RIGID BODY — a registry record carrying `receptor_pdb` coordinates and `ligand.exit_atom_xyz`. THAT is the
   anchor set. ⇒ "one more anchor set" is a staged effector STRUCTURE, not a number. Getting one needs RCSB,
   which the dev sandbox's egress proxy 403s, so that step is a CI-only path.

★★ AND IT HAS NOW BEEN WALKED (2026-08-06). ⚠ SUPERSEDED, RETAINED: *"The repository stages four such
   bodies, all E3 recruiters, and **zero transcriptional effectors** … it does not exist in this
   repository."* That was true when this module first ran and is the finding that converted the lead's
   status; it is false now. `nr4a3_effector_stage.py` stages NAMED transcriptional effectors through the
   same schema, chosen out of the route's own motivating paper rather than recalled — EB-TCIP
   (10.1021/jacs.5c05634) "recruits FKBP12(F36V)-tagged EWSR1::FLI1 to DNA sites bound by the
   transcriptional regulator BCL6", through the BI3812 series, so the effector is **BCL6**, a BTB/POZ
   transcriptional repressor. `effector_arm_census` COUNTS what is staged across both registries at run
   time; it asserts no number, and the sentence it prints is built from the count.

⛔ WHAT THAT DOES AND DOES NOT UPGRADE, because this is the exact place a proxy result could be laundered
   into an effector one. UPGRADED: the admissibility statement, which is now computed on a named effector's
   own coordinates (`★_named_effector`). NOT UPGRADED: the paired SIZE comparison, its within-class control
   and the interface-floor ablation, all of which are still computed on the four committed E3 bodies with
   `birc2`/`mdm2` as declared proxies — no effector arm enters those pools, and a test fails the build if
   one ever does.

★★ WHAT IS THEREFORE RUN HERE, AND WHY IT IS THE STRONGER ANSWER RATHER THAN A SUBSTITUTE FOR THE MISSING
   ONE. Read against `sample_placements`, the second-terminus body enters the enumeration ONLY as (i) an
   excluded volume and (ii) a contact count. Nothing in the acceptance test knows or cares what the recruited
   protein DOES. So the question "does the envelope admit an effector" does not need that specific effector:
   it needs the envelope RESOLVED BY BODY SIZE. This module computes it three ways, in one pass, from
   identical anchors, an identical target frame, an identical distance field and the identical sampler:

     body-free      the pure anchor envelope — is there anywhere outside the protein for a second terminus's
                    exit atom to sit, at each linker length. This is the E3-free machinery the route names,
                    and it is second-terminus-INDEPENDENT by construction, which is the "applies unchanged"
                    half of PUB-TCIP's claim made measurable rather than asserted.
     E3 bodies      `vhl` (340 residues, 3 chains) and `crbn` (1183 residues, 2 chains) — the two
                    downselected recruiters, whose committed run this module must replicate or it is
                    measuring its own bugs.
     effector-SIZE  `birc2` (92 residues, 1 chain) and `mdm2` (94 residues, 1 chain) — the two committed
     bodies         single-domain recruiter bodies, used here as SIZE-AND-SHAPE PROXIES for a small-molecule-
                    recruited transcriptional effector domain.

⛔ THE PROXY IS DECLARED AS A PROXY AND IT IS THE MODULE'S LARGEST LIMITATION. BIRC2's BIR3 domain and
   MDM2's p53-binding domain are NOT transcriptional effectors and this module does not say they are. They
   are used for one property only — a ~90-95 residue single-domain ligand-binding body with a solved
   ligand-bound exit vector, i.e. the size class a bromodomain-type effector recruiter falls in. What they
   license is a statement about BODY SIZE, and the body-free envelope above them is what stops any single
   proxy being load-bearing. A statement about a NAMED effector still needs that effector staged.

⛔ WHAT THIS CANNOT SAY. Geometry only. Nothing here is a binding, potency, selectivity, transcriptional-
   activity, efficacy, safety, therapeutic-window or clinical statement, and an "admits" answer is an
   ADMISSION OF VOLUME, never of function. Reach can refute a configuration; it cannot license one. Every
   anchor `a` is conditional on the cryptic pocket being the site, which `V3` left INCONCLUSIVE.

Outputs: nr4a3-tcip-reach.json (+ .md)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import os
import random
import sys
import time
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                       # noqa: E402
import linker_design as LD                   # noqa: E402  the reach engine — never reimplemented
import nr4a3_basin_search as BS              # noqa: E402  THE placement sampler — never reimplemented
import nr4a3_linker_design as NLD            # noqa: E402

# ---- imported, never re-typed (rule 1) -------------------------------------------------------------------
PARAMS = BS.PARAMS
RISE = LD.RISE_PER_ATOM_A                    # 1.25 A per backbone atom
CHEM_MAX_ATOMS = NLD.CHEM_MAX_ATOMS          # 24 — chemically routine upper bound on a bivalent linker
LINKER_MIN_ATOMS = PARAMS["linker_min_atoms"]
SEARCH_MAX_ATOMS = PARAMS["linker_max_atoms"]
GATE_ATOMS = PARAMS["linker_gate_atoms"]
MIN_CLEARANCE = PARAMS["pose_min_clearance_A"]

# The ladder is the committed report ladder PLUS the chemically routine ceiling, which the committed ladder
# stops short of. Nothing new is invented: both ends have a home.
LADDER = sorted(set(PARAMS["linker_report_atoms"]) | {GATE_ATOMS, SEARCH_MAX_ATOMS, CHEM_MAX_ATOMS})

BASINS = os.path.join(HERE, "nr4a3-orientation-basins.json")
REGISTRY = os.path.join(HERE, "nr4a3-e3-arm-registry.json")
# The SECOND registry, written by `nr4a3_effector_stage.py`. It is deliberately a separate file rather than
# extra rows in the one above: `nr4a3_e3_stage.py` REWRITES its registry wholesale on every run, so an
# effector arm merged into it would be silently deleted by the next E3 staging job. Each generator keeps one
# home for its own output (CLAUDE.md rule 1) and this module reads both.
EFFECTOR_REGISTRY = os.path.join(HERE, "nr4a3-effector-arm-registry.json")
UNIQUE_JSON = os.path.join(HERE, "nr4a-paralogue-unique-residues.json")
STRUCT_DIR = os.path.join(REPO, "results", "nr4a3-matrix")
OUT = os.path.join(HERE, "nr4a3-tcip-reach.json")

BASIN_SEED = 20260725                        # the committed run's seed — reproducing its pose ensemble
ENVELOPE_PITCH_A = 1.0                       # deterministic grid pitch for the body-free envelope

# The four staged bodies, partitioned by the ONLY axis this module uses them on: how big they are. The
# partition is asserted here and CHECKED against the measured residue counts in `body_geometry` — a label
# that disagreed with the coordinates would be exactly the "populated field, never measured" failure.
SINGLE_DOMAIN_ARMS = ("birc2", "mdm2")
MULTI_SUBUNIT_ARMS = ("vhl", "crbn")
SINGLE_DOMAIN_MAX_RESIDUES = 200             # the boundary the partition is checked against

E3_PARTNER_CLASS = "E3 ubiquitin-ligase recruiter"
EFFECTOR_PARTNER_CLASS = "transcriptional effector"


def load_registries(registry_path=REGISTRY, effector_registry_path=EFFECTOR_REGISTRY):
    """Every staged arm this repository holds, from both registries, each carrying its OWN partner class.

    ⚠ The class is read from the RECORD, not from which file it came out of, with the E3 registry's records
    defaulting to `E3 ubiquitin-ligase recruiter` because that is what its generator stages and what all four
    of its arms are. The earlier version of this census hard-coded that string for every row — harmless while
    the only registry was the E3 one, and exactly the kind of populated-but-unmeasured field that would have
    labelled a staged effector as a ligase the moment one existed.
    """
    out = {}
    for path, default_class in ((registry_path, E3_PARTNER_CLASS),
                                (effector_registry_path, EFFECTOR_PARTNER_CLASS)):
        if not os.path.exists(path):
            continue
        with open(path) as fh:
            reg = json.load(fh)
        for aid, rec in (reg.get("arms") or {}).items():
            out[aid] = (rec, os.path.relpath(path, REPO), rec.get("partner_class") or default_class)
    return out


# ==========================================================================================================
# THE CENSUS THAT CONVERTS THE LEAD'S STATUS
# ==========================================================================================================
def effector_arm_census(registry_path=REGISTRY, effector_registry_path=EFFECTOR_REGISTRY, struct_root=REPO):
    """Is there a staged TRANSCRIPTIONAL-EFFECTOR arm in this repository? Counted, not recalled.

    A staged arm is a registry record that `nr4a3_basin_search.load_arm_from_registry` can turn into a rigid
    body: it needs `receptor_pdb` coordinates on disk and a `ligand.exit_atom_xyz`. Anything else is not an
    anchor set, whatever it is called — so the count below is of arms that are LOADABLE, not of records that
    exist. A registry row whose coordinates are missing is a record, not an anchor set.
    """
    rows = []
    for aid, (rec, src, klass) in sorted(load_registries(registry_path, effector_registry_path).items()):
        pdb = os.path.join(struct_root, rec.get("receptor_pdb", "") or "")
        present = bool(rec.get("receptor_pdb")) and os.path.exists(pdb)
        rows.append({
            "arm_id": aid,
            "recruiter": rec.get("recruiter"),
            "partner_class": klass,
            "effector_role": rec.get("effector_role"),
            "status": rec.get("status"),
            "registry": src,
            "receptor_pdb": rec.get("receptor_pdb"),
            "receptor_pdb_present": present,
            "has_exit_atom": bool((rec.get("ligand") or {}).get("exit_atom_xyz")),
            "source_pdb_id": ((rec.get("provenance") or {}).get("receptor_entry") or {}).get("pdb_id"),
            "loadable_as_rigid_body": present and bool((rec.get("ligand") or {}).get("exit_atom_xyz")),
        })
    eff = [r for r in rows if r["partner_class"] == EFFECTOR_PARTNER_CLASS and r["loadable_as_rigid_body"]]
    e3 = [r for r in rows if r["partner_class"] == E3_PARTNER_CLASS]
    if eff:
        reading = (
            "%d staged transcriptional-effector arm(s) are loadable as rigid bodies (%s), alongside %d E3 "
            "ubiquitin-ligase recruiters. `PUB-TCIP`'s stated reason for being unwritten — 'the machinery "
            "exists and takes one more anchor set' — is DISCHARGED: the anchor set was a staged structure, "
            "not a number, and it now exists. ⛔ A staged body is an excluded volume and one atom's "
            "coordinates; it is not evidence that this effector binds anything, is recruited, or changes "
            "transcription." % (len(eff), ", ".join("%s (%s)" % (r["arm_id"], r["source_pdb_id"])
                                                    for r in eff), len(e3)))
    else:
        reading = (
            "every staged arm in the registry is an E3 ubiquitin-ligase recruiter. The count of staged "
            "transcriptional-effector arms is 0. `PUB-TCIP`'s stated reason for being unwritten — 'the "
            "machinery exists and takes one more anchor set' — is therefore correct about the machinery and "
            "understates the input: the anchor set is a STAGED STRUCTURE, not a number, and staging one "
            "needs RCSB, which the dev sandbox's egress proxy 403s.")
    return {
        "_question": "how many staged TRANSCRIPTIONAL-EFFECTOR arms does this repository hold?",
        "answer": len(eff),
        "effector_arm_ids": [r["arm_id"] for r in eff],
        "n_staged_arms_total": len(rows),
        "n_loadable": sum(1 for r in rows if r["loadable_as_rigid_body"]),
        "arms": rows,
        "_reading": reading,
        "_what_would_supply_it": (
            "one CI fetch of a ligand-bound transcriptional-effector domain (RCSB is 403'd at the dev "
            "sandbox's egress proxy), staged into the same schema the E3 arms use: receptor_pdb + "
            "ligand.exit_atom_xyz. ⚠ CORRECTED 2026-08-06 against the source rather than recalled: this "
            "string previously guessed that 'the TCIP literature's effector handle is a bromodomain-class "
            "ligand'. The route's own motivating paper (EB-TCIP, 10.1021/jacs.5c05634) states the effector "
            "is BCL6 — a transcriptional repressor engaged through its BTB-domain lateral groove by the "
            "BI3812 series — not a bromodomain. Staged by `nr4a3_effector_stage.py`."),
        "source_of_truth": ["research/modalities/nr4a3-e3-arm-registry.json",
                            "research/modalities/nr4a3-effector-arm-registry.json"],
    }


def staged_effector_arm_ids(effector_registry_path=EFFECTOR_REGISTRY, struct_root=REPO):
    """The effector arm ids the enumeration can actually run — derived from the registry, never a list typed
    into this module. An arm whose coordinates are absent is not in it."""
    if not os.path.exists(effector_registry_path):
        return []
    with open(effector_registry_path) as fh:
        reg = json.load(fh)
    out = []
    for aid, rec in sorted((reg.get("arms") or {}).items()):
        pdb = os.path.join(struct_root, rec.get("receptor_pdb", "") or "")
        if rec.get("status") == "OK" and rec.get("receptor_pdb") and os.path.exists(pdb) \
                and (rec.get("ligand") or {}).get("exit_atom_xyz"):
            out.append(aid)
    return out


# ==========================================================================================================
# BODY GEOMETRY — measured from the committed coordinates, never assumed
# ==========================================================================================================
def body_geometry(arm):
    """The size of a staged body, from its own coordinates.

    Reported as a ball model — centroid, the radius that encloses every CA, and where the ligand exit atom
    sits relative to that ball. ⚠ A ball OVERSTATES an elongated body's excluded volume, so these numbers are
    descriptive: the admissibility test below uses the REAL atom set through the committed sampler, never
    this ball. They exist so "effector-size" is a measured claim rather than a label.
    """
    ca = arm["ca"]
    cen = G.centroid(ca)
    r = [G.dist(cen, p) for p in ca]
    d_anchor = G.dist(cen, arm["anchor"])
    near = min(G.dist(arm["anchor"], p) for p in ca)
    return {
        "arm_id": arm["arm_id"], "recruiter": arm["recruiter"],
        "n_residues": len(ca), "chains": arm["chains"],
        "centroid_A": [round(c, 2) for c in cen],
        "ca_radius_max_A": round(max(r), 2),
        "ca_radius_median_A": round(sorted(r)[len(r) // 2], 2),
        "exit_atom_to_centroid_A": round(d_anchor, 2),
        "exit_atom_to_nearest_CA_A": round(near, 2),
        "size_class": ("single_domain" if len(ca) <= SINGLE_DOMAIN_MAX_RESIDUES else "multi_subunit"),
    }


# ==========================================================================================================
# THE BODY-FREE ANCHOR ENVELOPE — the E3-free machinery, exactly as the sampler tests it
# ==========================================================================================================
def body_free_envelope(a, field3, ladder=LADDER, pitch=ENVELOPE_PITCH_A):
    """The fraction of each linker-length reach shell in which a second terminus's exit atom could sit.

    ★ THE TEST IS THE SAMPLER'S OWN, LIFTED NOT REWRITTEN: `sample_placements` rejects an anchor position
    `ae` when `field3.min_dist(ae) - field3.cell_slack < pose_min_clearance_A`. Same predicate, same field,
    same constant — evaluated on a DETERMINISTIC grid instead of by Monte-Carlo, so this half of the result
    carries no seed and cannot move between runs.

    Deterministic by construction: a lattice, not an RNG. Reported as a fraction of the SHELL between
    `linker_min_atoms` and n, because that is the space the sampler draws from.
    """
    slack = field3.cell_slack
    lo = G.contour_length_from_atoms(LINKER_MIN_ATOMS, RISE)
    out = {}
    n_max = max(ladder)
    hi_max = G.contour_length_from_atoms(n_max, RISE)
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
                pts.append((math.sqrt(d2), field3.min_dist(p) - slack >= MIN_CLEARANCE))
    for n in ladder:
        hi = G.contour_length_from_atoms(n, RISE)
        inside = [ok for d, ok in pts if d <= hi]
        n_tot = len(inside)
        n_ok = sum(1 for ok in inside if ok)
        out[str(n)] = {
            "shell_hi_A": round(hi, 2),
            "n_grid_points": n_tot,
            "n_admissible": n_ok,
            "fraction_admissible": round(n_ok / n_tot, 5) if n_tot else None,
        }
    return out


# ==========================================================================================================
# THE PAIRED PLACEMENT ENVELOPE — the committed sampler, one arm body at a time
# ==========================================================================================================
def placement_envelope_cell(arm, pose, field3, n_atoms, n_samples, seed):
    """One (arm x pose x linker-length) cell, through `nr4a3_basin_search.sample_placements` UNCHANGED.

    The only thing this function does to the engine is hand it a `params` whose `linker_max_atoms` is the
    ladder rung being asked about. That is the sampler's own parameter, used for its own purpose — the shell
    it draws the second-terminus anchor from — so the per-rung answer is the engine's answer, not a
    re-derivation of it.
    """
    p = dict(PARAMS)
    p["linker_max_atoms"] = n_atoms
    acc, stats = BS.sample_placements(arm, pose, field3, random.Random(seed), n_samples, params=p)
    spans = sorted(pl["span_A"] for pl in acc)
    n_needed = [max(1, int(math.ceil(s / RISE - 1e-9))) for s in spans]
    contacts = sorted(pl["n_contact"] for pl in acc)
    return {
        "arm_id": arm["arm_id"], "pose_id": pose["pose_id"], "linker_atoms": n_atoms,
        "shell_hi_A": round(G.contour_length_from_atoms(n_atoms, RISE), 2),
        "n_samples": stats["n_samples"],
        "n_accepted": stats["n_accepted"],
        "acceptance_rate": stats["acceptance_rate"],
        "n_prescreen_rejected": stats["n_prescreen_rejected"],
        "span_A_min": round(spans[0], 2) if spans else None,
        "span_A_median": round(spans[len(spans) // 2], 2) if spans else None,
        "span_A_max": round(spans[-1], 2) if spans else None,
        "min_backbone_atoms_realised": min(n_needed) if n_needed else None,
        "median_backbone_atoms_realised": (n_needed[len(n_needed) // 2] if n_needed else None),
        "n_contact_median": contacts[len(contacts) // 2] if contacts else None,
        "n_contact_max": contacts[-1] if contacts else None,
    }


def _worker(job):
    arm = _ARMS[job["arm_id"]]
    pose = _POSES[job["pose_id"]]
    return placement_envelope_cell(arm, pose, _FIELD, job["n_atoms"], job["n_samples"], job["seed"])


_ARMS: dict = {}
_POSES: dict = {}
_FIELD = None


# ==========================================================================================================
# SUMMARY AND DECISION
# ==========================================================================================================
def wilson(k, n, z=1.96):
    """Wilson 95 % interval on a proportion — the repo's standard for a pooled proportion (POLICY-evidence)."""
    if not n:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(max(p * (1 - p) / n + z * z / (4 * n * n), 0.0)) / d
    return [round(c - h, 8), round(c + h, 8)]


def paired_body_size_comparison(cells, free_pooled, geom):
    """★★ THE DECISION QUANTITY, AND WHY THE BINARY ONE IS NOT IT.

    "Does the envelope admit a body of effector size" is answered YES at every rung by every body tested,
    which makes it a gate that cannot fail — exactly what the basin search's own parameter block warns about
    at its sampling ceiling. What DOES discriminate is how much orientation space each body gets, and whether
    dropping from a multi-subunit CRL to a single-domain effector-size body WIDENS it, NARROWS it, or leaves
    it unchanged. Three readings, all of which can come back either way:

      `acceptance_rate`     accepted placements per sample drawn from the shell — the size of the admissible
                            orientation space, body included.
      `body_cost`           acceptance divided by the BODY-FREE fraction of that shell, i.e. P(the body fits
                            and makes an interface | its exit atom is somewhere it could sit). This is the
                            body's own marginal cost, with the target's shape divided out.
      `size_ratio`          pooled effector-size acceptance / pooled E3 acceptance, with Wilson intervals. A
                            ratio whose interval contains 1 is a measurement of NO DIFFERENCE, and that is a
                            result about the modality, not a failure to find one.
    """
    out = {}
    for n in sorted({c["linker_atoms"] for c in cells}):
        rung = [c for c in cells if c["linker_atoms"] == n]
        free = free_pooled[str(n)]["mean_fraction_admissible"]
        blk = {"shell_hi_A": free_pooled[str(n)]["shell_hi_A"],
               "body_free_mean_fraction_admissible": free, "by_size_class": {}}
        for cls, ids in (("single_domain", SINGLE_DOMAIN_ARMS), ("multi_subunit", MULTI_SUBUNIT_ARMS)):
            grp = [c for c in rung if c["arm_id"] in ids]
            k = sum(c["n_accepted"] for c in grp)
            s = sum(c["n_samples"] for c in grp)
            rate = k / s if s else None
            blk["by_size_class"][cls] = {
                "arms": sorted({c["arm_id"] for c in grp}),
                "n_accepted": k, "n_samples": s,
                "acceptance_rate": round(rate, 8) if rate is not None else None,
                "acceptance_ci95": wilson(k, s),
                "body_cost": round(rate / free, 6) if rate is not None and free else None,
                "n_contact_median": (lambda v: v[len(v) // 2] if v else None)(
                    sorted(c["n_contact_median"] for c in grp if c["n_contact_median"] is not None)),
            }
        # ★★ THE CONTROL THAT DECIDES WHETHER THE SIZE CONTRAST MAY BE CALLED A SIZE EFFECT AT ALL, and it
        #    is not the contrast itself. Each size class holds TWO bodies. If two bodies of the SAME size
        #    differ from each other by as much as the classes differ, then "size class" is not the variable
        #    doing the work and the pooled ratio is confounded — a between-group difference smaller than the
        #    within-group spread is not a group effect, whatever its p-value. Computed per rung so it cannot
        #    be quoted at whichever rung flatters it.
        per_arm = {}
        for c in rung:
            slot = per_arm.setdefault(c["arm_id"], [0, 0])
            slot[0] += c["n_accepted"]
            slot[1] += c["n_samples"]
        blk["per_arm_acceptance_rate"] = {a: round(k / s, 8) for a, (k, s) in sorted(per_arm.items()) if s}
        for cls, ids in (("single_domain", SINGLE_DOMAIN_ARMS), ("multi_subunit", MULTI_SUBUNIT_ARMS)):
            v = [blk["per_arm_acceptance_rate"][a] for a in ids if a in blk["per_arm_acceptance_rate"]]
            blk["by_size_class"][cls]["within_class_spread_ratio"] = (
                round(max(v) / min(v), 3) if v and min(v) else None)

        a = blk["by_size_class"]["single_domain"]
        b = blk["by_size_class"]["multi_subunit"]
        blk["size_ratio_single_over_multi"] = (
            round(a["acceptance_rate"] / b["acceptance_rate"], 3)
            if a["acceptance_rate"] and b["acceptance_rate"] else None)
        between = (max(a["acceptance_rate"], b["acceptance_rate"])
                   / min(a["acceptance_rate"], b["acceptance_rate"])
                   if a["acceptance_rate"] and b["acceptance_rate"] else None)
        within = [x for x in (a.get("within_class_spread_ratio"), b.get("within_class_spread_ratio"))
                  if x is not None]
        blk["between_class_contrast_ratio"] = round(between, 3) if between else None
        blk["within_class_spread_exceeds_between_class_contrast"] = bool(
            between is not None and within and max(within) > between)
        blk["intervals_overlap"] = bool(
            a["acceptance_ci95"][0] is not None and b["acceptance_ci95"][0] is not None
            and a["acceptance_ci95"][0] <= b["acceptance_ci95"][1]
            and b["acceptance_ci95"][0] <= a["acceptance_ci95"][1])
        out[str(n)] = blk
    return out


def summarise(cells, geom):
    """Per arm: the shortest linker length at which ANY placement is admissible, and where it saturates."""
    by_arm = {}
    for c in cells:
        by_arm.setdefault(c["arm_id"], []).append(c)
    out = {}
    for aid, rows in sorted(by_arm.items()):
        by_n = {}
        for r in rows:
            by_n.setdefault(r["linker_atoms"], []).append(r)
        per_n = {}
        shortest = None
        for n in sorted(by_n):
            grp = by_n[n]
            n_open = sum(1 for r in grp if r["n_accepted"] > 0)
            tot_acc = sum(r["n_accepted"] for r in grp)
            tot_smp = sum(r["n_samples"] for r in grp)
            per_n[str(n)] = {
                "n_poses": len(grp),
                "n_poses_with_any_admissible_placement": n_open,
                "total_accepted": tot_acc,
                "pooled_acceptance_rate": round(tot_acc / tot_smp, 8) if tot_smp else None,
                "min_backbone_atoms_realised": min(
                    [r["min_backbone_atoms_realised"] for r in grp
                     if r["min_backbone_atoms_realised"] is not None] or [None]) if any(
                    r["min_backbone_atoms_realised"] is not None for r in grp) else None,
            }
            if shortest is None and n_open > 0:
                shortest = n
        out[aid] = {
            "size_class": geom[aid]["size_class"],
            "n_residues": geom[aid]["n_residues"],
            "shortest_linker_atoms_with_any_admissible_placement": shortest,
            "admits_within_the_gate_%d_atoms" % GATE_ATOMS: bool(shortest is not None and shortest <= GATE_ATOMS),
            "admits_within_the_search_ceiling_%d_atoms" % SEARCH_MAX_ATOMS: bool(
                shortest is not None and shortest <= SEARCH_MAX_ATOMS),
            "admits_within_the_chemically_routine_%d_atoms" % CHEM_MAX_ATOMS: bool(
                shortest is not None and shortest <= CHEM_MAX_ATOMS),
            "by_linker_atoms": per_n,
        }
    return out


def required_distances():
    """THE DISTANCES THE MODALITY REQUIRES — every one of them read from a committed source.

    ⚠ NO TCIP-SPECIFIC LINKER LENGTH IS AVAILABLE TO THIS MODULE, and inventing one would be the exact
    failure this repository keeps paying for. `EV-EB-TCIP-2025` is the route's only cited TCIP source and it
    is an auto-captured lead that has not cleared `verify-refs` (systems/AUDIT-2026-08-06-routes.md, "Left
    open deliberately"), so nothing may be quoted from it. What is used instead are the repository's OWN
    committed bounds on a bivalent linker, which are modality-agnostic by construction — the same numbers the
    E3 configuration was enumerated at, which is precisely what makes the comparison paired.
    """
    return {
        "rise_per_backbone_atom_A": RISE,
        "linker_min_atoms": LINKER_MIN_ATOMS,
        "gate_atoms": GATE_ATOMS,
        "search_ceiling_atoms": SEARCH_MAX_ATOMS,
        "chemically_routine_ceiling_atoms": CHEM_MAX_ATOMS,
        "span_at_gate_A": round(G.contour_length_from_atoms(GATE_ATOMS, RISE), 2),
        "span_at_search_ceiling_A": round(G.contour_length_from_atoms(SEARCH_MAX_ATOMS, RISE), 2),
        "span_at_chemically_routine_ceiling_A": round(
            G.contour_length_from_atoms(CHEM_MAX_ATOMS, RISE), 2),
        "sources": {
            "rise / min / gate / search ceiling": "nr4a3_basin_search.PARAMS (committed, preregistered)",
            "chemically routine ceiling": "nr4a3_linker_design.CHEM_MAX_ATOMS (PEG6-diacid scale)",
        },
        "⚠_no_tcip_specific_distance_is_used": (
            "the route's only TCIP citation is an unverified auto-captured lead, so no published TCIP linker "
            "length enters this module. If one is later verified it can only tighten the ceiling, never "
            "loosen it, so an 'admits' answer read at 24 atoms is the permissive reading and an 'admits at "
            "the 12-atom gate' answer is the one that survives any tightening."),
    }


# ==========================================================================================================
# CROSS-CHECKS — rule 1: this module may not mint a second value for a number with a home
# ==========================================================================================================
def crosscheck_pose_ensemble(poses, basins_path=BASINS):
    """The 12 warhead anchors recomputed here must be the committed ones, bit for bit."""
    with open(basins_path) as fh:
        d = json.load(fh)
    ref = {p["pose_id"]: p["anchor_xyz"] for p in d["pose_ensemble"]}
    worst, n = 0.0, 0
    for p in poses:
        q = ref.get(p["pose_id"])
        if q is None:
            continue
        n += 1
        worst = max(worst, max(abs(x - y) for x, y in zip(p["anchor_xyz"], q)))
    return {"status": "AGREES" if n and worst < 1e-9 else "DISAGREES" if n else "UNREAD",
            "n_compared": n, "max_abs_delta_A": worst,
            "source_of_truth": "research/modalities/nr4a3-orientation-basins.json -> pose_ensemble"}


def crosscheck_committed_anchors_admissible(field3, basins_path=BASINS):
    """★ THE GUARD THE BODY-FREE ENVELOPE RESTS ON. Every second-terminus anchor the committed search
    ACCEPTED must pass this module's anchor test. If one did not, the envelope would be excluding positions
    the engine itself already admitted, and every number below would be too small."""
    with open(basins_path) as fh:
        d = json.load(fh)
    pts = []
    for m in d["meta_basins_ranked"]:
        rep = m.get("representative") or {}
        if rep.get("anchor_e3_xyz"):
            pts.append((m["meta_basin_id"] + "@representative", tuple(rep["anchor_e3_xyz"])))
        for cys, blk in (m.get("term_a_union") or {}).items():
            ex = (blk or {}).get("exemplar_placement") or {}
            if ex.get("anchor_e3_xyz"):
                pts.append(("%s@%s_exemplar" % (m["meta_basin_id"], cys), tuple(ex["anchor_e3_xyz"])))
    slack = field3.cell_slack
    bad = []
    for lab, p in pts:
        clr = field3.min_dist(p) - slack
        if clr < MIN_CLEARANCE:
            bad.append({"placement": lab, "clearance_A": round(clr, 3)})
    return {"status": "HOLDS" if pts and not bad else "VIOLATED" if bad else "UNREAD",
            "n_committed_anchors_tested": len(pts), "n_failing": len(bad), "failures": bad[:20],
            "_rule": "a committed accepted anchor must be admissible under this module's anchor test",
            "source_of_truth": "research/modalities/nr4a3-orientation-basins.json -> meta_basins_ranked"}


def crosscheck_replicates_committed_acceptance(cells, basins_path=BASINS):
    """The E3 half must replicate the committed acceptance rates, or the effector-size half is measuring this
    module's own bugs rather than the body-size change.

    Compared at the committed run's own shell (`linker_max_atoms`), with a normal-approximation 95 % interval
    on this module's rate — the two runs use different sample counts and different RNG streams, so an EXACT
    match would be evidence of a bug, not of agreement.
    """
    with open(basins_path) as fh:
        d = json.load(fh)
    ref = {}
    for aid, blk in d["arms"].items():
        for pp in blk.get("per_pose", []):
            ref[(aid, pp["pose_id"])] = pp["stats"]["acceptance_rate"]
    rows, n_out = [], 0
    for c in cells:
        if c["linker_atoms"] != SEARCH_MAX_ATOMS:
            continue
        r = ref.get((c["arm_id"], c["pose_id"]))
        if r is None:
            continue
        k, n = c["n_accepted"], c["n_samples"]
        p = k / n
        se = math.sqrt(max(p * (1 - p), 1e-12) / n)
        lo, hi = p - 1.96 * se, p + 1.96 * se
        inside = lo <= r <= hi
        n_out += 0 if inside else 1
        rows.append({"arm": c["arm_id"], "pose": c["pose_id"], "committed_rate": r,
                     "recomputed_rate": round(p, 6), "ci95": [round(lo, 6), round(hi, 6)],
                     "committed_inside_ci": inside})
    # ⚠ A 95 % INTERVAL IS EXPECTED TO EXCLUDE ~5 % OF TRUE VALUES, so "n_out > 0" is not by itself a
    #   disagreement — reporting it as one would manufacture a failure, which is the mirror image of the
    #   fabricated-verdict failure this repo already paid for. The expected count is stated beside the
    #   observed one and the status is graded against it, not against zero.
    expected = 0.05 * len(rows)
    status = ("UNREAD" if not rows else
              "AGREES" if n_out <= max(1, math.ceil(expected)) else "DISAGREES")
    return {"status": status,
            "n_cells_compared": len(rows), "n_committed_outside_ci95": n_out,
            "n_expected_outside_ci95_by_chance": round(expected, 2),
            "_reading": ("%d of %d committed rates fall inside this module's recomputed 95 %% interval; %d "
                         "outside against %.2f expected by chance at a 95 %% level. That is agreement, and "
                         "a status of DISAGREES here would require materially more than the interval's own "
                         "false-positive rate." % (len(rows) - n_out, len(rows), n_out, expected)),
            "cells": rows,
            "source_of_truth": "research/modalities/nr4a3-orientation-basins.json -> arms[*].per_pose[*].stats",
            "_why": ("the effector-size result is a DELTA against the E3 one, so an E3 half that does not "
                     "replicate the committed artifact invalidates the delta as well.")}


def interface_floor_ablation(arms, poses, field3, n_atoms=None, floors=None, n_samples=30000, seed=777):
    """★★ THE ROOT CAUSE OF THE SIZE CONTRAST, MEASURED BY A CONTROLLED REPRODUCTION RATHER THAN EXPLAINED.

    The pooled single-domain pool accepts LESS than the multi-subunit pool at every rung. There is an obvious
    story — a smaller body cannot put as many residues within contact distance, so it fails the sampler's
    `min_contact_residues` floor more often — and this repository's rule is that an obvious story is a
    HYPOTHESIS until an observation discriminates it. The observation that does: re-run the identical cells
    with the floor lowered, changing nothing else. If the floor is the cause, the contrast must move with it;
    if the cause were steric bulk, lowering an INTERFACE requirement could not touch it.

    ⚠ WHY THIS IS DECISION-RELEVANT AND NOT HOUSEKEEPING. `min_contact_residues = 12` is a DEGRADER-derived
    parameter — the basin search's own comment is "below this it is a tethered pair, not an interface", and a
    PROTAC needs a cooperative target·E3 interface for the ternary to be productive. Whether a
    transcriptional CIP needs the same induced interface, or only needs the two proteins co-localised, is a
    question this repository has never asked. If the ablation moves the answer, then the TCIP result at the
    committed floor is a result about a DEGRADER'S interface requirement applied to a non-degrading modality,
    and it must be reported at both settings rather than at the inherited one alone.
    """
    n_atoms = GATE_ATOMS if n_atoms is None else n_atoms
    floors = (PARAMS["min_contact_residues"], 6, 0) if floors is None else floors
    rows = {}
    for floor in floors:
        per_arm = {}
        for aid, arm in sorted(arms.items()):
            k = s = 0
            for i, p in enumerate(poses):
                pr = dict(PARAMS)
                pr["linker_max_atoms"] = n_atoms
                pr["min_contact_residues"] = floor
                _, st = BS.sample_placements(arm, p, field3, random.Random(seed + i), n_samples, params=pr)
                k += st["n_accepted"]
                s += st["n_samples"]
            per_arm[aid] = {"n_accepted": k, "n_samples": s, "acceptance_rate": round(k / s, 8)}
        def pool(ids):
            k = sum(per_arm[a]["n_accepted"] for a in ids if a in per_arm)
            s = sum(per_arm[a]["n_samples"] for a in ids if a in per_arm)
            return (k / s if s else None), wilson(k, s)
        sd, sd_ci = pool(SINGLE_DOMAIN_ARMS)
        ms, ms_ci = pool(MULTI_SUBUNIT_ARMS)
        rows[str(floor)] = {
            "min_contact_residues": floor, "per_arm": per_arm,
            "single_domain_acceptance": round(sd, 8) if sd else None, "single_domain_ci95": sd_ci,
            "multi_subunit_acceptance": round(ms, 8) if ms else None, "multi_subunit_ci95": ms_ci,
            "ratio_single_over_multi": round(sd / ms, 3) if sd and ms else None,
        }
    committed = rows[str(PARAMS["min_contact_residues"])]["ratio_single_over_multi"]
    steric = rows["0"]["ratio_single_over_multi"] if "0" in rows else None
    inverts = bool(committed is not None and steric is not None
                   and (committed - 1.0) * (steric - 1.0) < 0)
    return {
        "_what": ("the same cells at the same linker length with ONLY the sampler's interface floor "
                  "changed — floor 0 is the pure steric question (clearance + clash), the committed floor "
                  "adds the degrader's induced-interface requirement"),
        "linker_atoms": n_atoms, "samples_per_arm_pose": n_samples,
        "committed_floor": PARAMS["min_contact_residues"],
        "by_floor": rows,
        "ratio_at_the_committed_floor": committed,
        "ratio_with_no_interface_floor": steric,
        "★_the_sign_inverts": inverts,
        "★_reading": (
            "at the committed floor the single-domain pool accepts %s× the multi-subunit pool; with the "
            "interface floor removed it accepts %s×. %s" % (
                committed, steric,
                ("The sign INVERTS, so the single-domain penalty is entirely the interface floor and not "
                 "steric bulk: on clash alone the smaller body gets MORE orientation space, exactly as the "
                 "'one fewer/smaller terminus is a smaller problem' intuition says. The committed floor is "
                 "a DEGRADER'S requirement, so a TCIP read at that floor is being charged for an induced "
                 "interface nobody has shown the modality needs."
                 if inverts else
                 "The sign does NOT invert, so the contrast survives removing the interface requirement and "
                 "is not an artefact of a degrader-derived parameter."))),
        "⛔_what_this_does_not_settle": (
            "which floor is right for a transcriptional CIP. This module measures the answer at both and "
            "refuses to pick — `BLK-UNSIZED-REQUIREMENT` is the route's own record that nobody has written "
            "the specification down, and an interface floor is exactly that kind of unwritten requirement."),
        "source_of_the_committed_floor": "nr4a3_basin_search.PARAMS['min_contact_residues']",
    }


def crosscheck_acceptance_is_e3_free(arms, poses, field3, n_samples=40000, seed=4242):
    """★★ THE CLAIM `PUB-TCIP` RESTS ON, TURNED INTO A CONTROLLED EXPERIMENT INSTEAD OF A READING.

    PUB-TCIP would claim *"the reach enumeration built for E3 recruitment applies unchanged when the second
    terminus is a transcriptional effector rather than a ligase"*. Read against `sample_placements` that
    looks true — the acceptance test is clearance, hard clash, soft-clash budget and contact count, none of
    which mentions a ligase — but "I read the code and it looked E3-free" is a HYPOTHESIS, and this
    repository's rule is that a mechanism claim needs the observation that discriminates.

    So: run each arm twice from the same seed, once as staged and once with every E3-SPECIFIC field
    (`ring`, `cullin`, `tanchor`, `transfer_anchor`, `crl`) removed. If the acceptance test consulted any of
    them the two runs would differ. Byte-identical accepted counts and spans is the observation; anything
    else refutes the claim and this module must say so.
    """
    rows, bad = [], []
    for aid, arm in sorted(arms.items()):
        stripped = dict(arm)
        for k in ("ring", "cullin", "tanchor"):
            stripped[k] = None
        stripped["crl"] = None
        stripped["transfer_anchor"] = None
        a_acc, a_st = BS.sample_placements(arm, poses[0], field3, random.Random(seed), n_samples)
        b_acc, b_st = BS.sample_placements(stripped, poses[0], field3, random.Random(seed), n_samples)
        same = (a_st["n_accepted"] == b_st["n_accepted"]
                and [round(p["span_A"], 9) for p in a_acc] == [round(p["span_A"], 9) for p in b_acc]
                and [p["n_contact"] for p in a_acc] == [p["n_contact"] for p in b_acc])
        rows.append({"arm": aid, "n_accepted_staged": a_st["n_accepted"],
                     "n_accepted_e3_fields_stripped": b_st["n_accepted"], "identical": same})
        if not same:
            bad.append(aid)
    return {
        "status": "HOLDS" if rows and not bad else "REFUTED" if bad else "UNREAD",
        "n_samples_per_run": n_samples, "arms_disagreeing": bad, "rows": rows,
        "_claim_tested": ("the placement acceptance test is E3-free: removing every E3-specific field from "
                          "the arm changes no accepted placement"),
        "_why_this_is_not_a_code_reading": ("a mechanism read off source is a hypothesis; this is the "
                                            "controlled reproduction that discriminates it"),
    }


def crosscheck_exit_vector_comparability(census, registries=None):
    """★ IS THE NAMED EFFECTOR'S ARM COMPARABLE TO THE FOUR COMMITTED ONES, on the property that would
    otherwise confound the comparison?

    The sampler places a body by putting its LIGAND EXIT ATOM in the reach shell and rotating the body about
    that point. So how far the exit atom sits from its own body's surface is not a detail: it is a fixed
    offset that displaces the whole body relative to the target before any rotation happens. If a new arm's
    exposure sits outside the range of the arms it is being compared with, a difference in its acceptance is
    uninterpretable — the CHEMICAL MATTER is doing work the protein is being credited with.

    ⚠ AND THE SIGN OF THAT EFFECT IS NOT PREDICTABLE, WHICH IS WHY THIS CHECK REPORTS COMPARABILITY AND NOT A
    CORRECTION. An earlier draft of this docstring asserted that a far-dangling exit atom is "admitted more
    easily FOR THAT REASON ALONE" — a plausible story, and the first data that could speak to it contradicted
    the direction: `brd4_bd1` at 13.65 Å accepted LESS than `bcl6` at 5.44 Å, because a large offset also
    pushes the body out of the shell it has to sit in. Two mechanisms with opposite signs, so the honest
    output is "not comparable", never "comparable after allowing for it".

    Measured, not assumed, and reported whichever way it comes out.
    """
    regs = registries if registries is not None else load_registries()
    rows = []
    for aid, (rec, _src, klass) in sorted(regs.items()):
        lig = rec.get("ligand") or {}
        if lig.get("exit_atom_dist_to_receptor_A") is None:
            continue
        rows.append({"arm_id": aid, "partner_class": klass,
                     "ligand_het": lig.get("het_code"), "ligand_n_heavy": lig.get("n_heavy"),
                     "exit_atom_exposure_A": lig["exit_atom_dist_to_receptor_A"]})
    ref = [r["exit_atom_exposure_A"] for r in rows if r["partner_class"] == E3_PARTNER_CLASS]
    if not ref:
        return {"status": "UNREAD", "reason": "no committed E3 arm to calibrate against", "rows": rows}
    lo, hi = min(ref), max(ref)
    for r in rows:
        r["inside_the_committed_E3_range"] = bool(lo <= r["exit_atom_exposure_A"] <= hi)
    eff = [r for r in rows if r["partner_class"] == EFFECTOR_PARTNER_CLASS]
    outside = [r for r in eff if not r["inside_the_committed_E3_range"]]
    named = [r["arm_id"] for r in eff if r["inside_the_committed_E3_range"]]
    return {
        "status": "AGREES" if eff and not outside else ("FLAGS" if outside else "UNREAD"),
        "committed_E3_exposure_range_A": [lo, hi],
        "effector_arms_inside_that_range": named,
        "effector_arms_outside_it": [{"arm_id": r["arm_id"], "exit_atom_exposure_A": r["exit_atom_exposure_A"]}
                                     for r in outside],
        "rows": rows,
        "_reading": ("the exit-atom offset displaces a body relative to the target before any rotation, so "
                     "an arm whose exposure sits outside the committed arms' range is NOT COMPARABLE with "
                     "them and its acceptance may not be pooled with or ranked against theirs. ⚠ The SIGN "
                     "is not predictable and is not claimed: a larger offset both moves the body clear of "
                     "the target (easier) and pushes it out of the shell it must sit in (harder). This does "
                     "not invalidate such an arm — it bounds what may be said with it."),
    }


def named_effector_reading(cells, summary, geom, free_pooled, effector_ids, census):
    """What the enumeration can now say about a NAMED effector, kept strictly apart from the size-class
    statement it does not replace.

    ⛔ THE DISCIPLINE THIS FUNCTION EXISTS TO ENFORCE. `birc2` and `mdm2` are size-and-shape PROXIES; the
    route memo forbids naming an effector on their basis, and nothing here may launder a proxy number into an
    effector one. So the proxy pooling above is left exactly as it was — its arm lists are explicit tuples
    and no effector arm enters them — and every named-effector number is computed here, from that arm's own
    cells, and reported beside the proxy pools rather than merged into them.
    """
    out = {"_what": ("per-rung admissibility for each STAGED, NAMED transcriptional effector, computed from "
                     "that arm's own cells only"),
           "effector_arms": {}, "_still_a_size_class_statement": [], "by_linker_atoms": {}}
    if not effector_ids:
        out["status"] = "NO_NAMED_EFFECTOR_STAGED"
        out["_reading"] = ("no transcriptional-effector arm is staged, so every statement this module makes "
                           "about an effector is a statement about a SIZE CLASS, carried by two explicit "
                           "proxies (birc2, mdm2) that are not transcriptional effectors.")
        return out
    by_class = {r["arm_id"]: r for r in census["arms"]}
    for aid in effector_ids:
        if aid not in summary:
            continue
        row = by_class.get(aid, {})
        out["effector_arms"][aid] = {
            "effector": row.get("recruiter"),
            "effector_role": row.get("effector_role"),
            "source_pdb_id": row.get("source_pdb_id"),
            "n_residues": geom[aid]["n_residues"],
            "chains": geom[aid]["chains"],
            "size_class_by_residue_count": geom[aid]["size_class"],
            "shortest_linker_atoms_with_any_admissible_placement":
                summary[aid]["shortest_linker_atoms_with_any_admissible_placement"],
            "admits_within_the_%d_atom_gate" % GATE_ATOMS:
                summary[aid]["admits_within_the_gate_%d_atoms" % GATE_ATOMS],
            "admits_within_the_chemically_routine_%d_atoms" % CHEM_MAX_ATOMS:
                summary[aid]["admits_within_the_chemically_routine_%d_atoms" % CHEM_MAX_ATOMS],
        }
    for n in sorted({c["linker_atoms"] for c in cells}):
        free = free_pooled[str(n)]["mean_fraction_admissible"]
        blk = {}
        for aid in effector_ids:
            grp = [c for c in cells if c["linker_atoms"] == n and c["arm_id"] == aid]
            if not grp:
                continue
            k = sum(c["n_accepted"] for c in grp)
            s = sum(c["n_samples"] for c in grp)
            rate = k / s if s else None
            blk[aid] = {
                "n_poses": len(grp),
                "n_poses_with_any_admissible_placement": sum(1 for c in grp if c["n_accepted"] > 0),
                "acceptance_rate": round(rate, 8) if rate is not None else None,
                "acceptance_ci95": wilson(k, s),
                "body_cost": round(rate / free, 6) if rate and free else None,
            }
        if blk:
            out["by_linker_atoms"][str(n)] = blk
    out["status"] = "STAGED"
    out["_still_a_size_class_statement"] = [
        "the PAIRED SIZE COMPARISON (`★_paired_body_size_comparison`) and everything derived from it — the "
        "within-class spread control, the pooled single/multi ratio and the interface-floor ablation — are "
        "computed on the four committed bodies ONLY. `birc2` and `mdm2` remain size-and-shape PROXIES there "
        "and nothing about a named effector may be read off them.",
        "the interface-floor ablation is a statement about the SAMPLER's inherited degrader parameter, not "
        "about any effector; it is unchanged by staging one.",
        "`admits` remains a gate that no tested body has failed, so a named effector admitting is not "
        "evidence of anything beyond excluded volume.",
    ]
    return out


def crosscheck_size_partition(geom):
    """The `single_domain` / `multi_subunit` labels must agree with the measured residue counts."""
    bad = []
    for aid in SINGLE_DOMAIN_ARMS:
        if geom.get(aid, {}).get("size_class") != "single_domain":
            bad.append({"arm": aid, "expected": "single_domain", "measured": geom.get(aid, {}).get("size_class")})
    for aid in MULTI_SUBUNIT_ARMS:
        if geom.get(aid, {}).get("size_class") != "multi_subunit":
            bad.append({"arm": aid, "expected": "multi_subunit", "measured": geom.get(aid, {}).get("size_class")})
    return {"status": "AGREES" if not bad else "DISAGREES", "mismatches": bad,
            "_rule": "a size label is checked against the coordinates, never trusted because it was typed"}


# ==========================================================================================================
# VERDICT
# ==========================================================================================================
def verdict(summary, envelope_free, required, paired, ablation=None, named=None):
    eff = [a for a in SINGLE_DOMAIN_ARMS if a in summary]
    e3 = [a for a in MULTI_SUBUNIT_ARMS if a in summary]
    shortest_eff = [summary[a]["shortest_linker_atoms_with_any_admissible_placement"] for a in eff]
    shortest_e3 = [summary[a]["shortest_linker_atoms_with_any_admissible_placement"] for a in e3]
    live_eff = [s for s in shortest_eff if s is not None]
    live_e3 = [s for s in shortest_e3 if s is not None]
    admits = bool(live_eff) and min(live_eff) <= CHEM_MAX_ATOMS
    at_gate = bool(live_eff) and min(live_eff) <= GATE_ATOMS
    n_rungs = len(paired)
    n_overlap = sum(1 for b in paired.values() if b["intervals_overlap"])
    ratios = [b["size_ratio_single_over_multi"] for b in paired.values()
              if b["size_ratio_single_over_multi"] is not None]
    gate_blk = paired.get(str(GATE_ATOMS), {})
    named = named or {}
    named_arms = named.get("effector_arms") or {}
    # ⛔ THE SENTENCE IS BUILT FROM THE COUNT, NOT TYPED. Whether this module may name an effector at all is
    #   a function of what is staged, and a hand-written "no named effector has been staged" would go on
    #   reading true for as long as nobody remembered to change it — the exact failure mode this file's own
    #   `★_reading` was rewritten to avoid.
    if named_arms:
        named_shortest = {a: v["shortest_linker_atoms_with_any_admissible_placement"]
                          for a, v in named_arms.items()}
        live_named = [s for s in named_shortest.values() if s is not None]
        what_it_is_not = (
            "It is not evidence that %s binds anything, is recruited, is retained on chromatin, or changes "
            "transcription. It is an excluded-volume statement: a body of this shape has somewhere to sit "
            "while its partner ligand occupies the NR4A3 cryptic pocket. ⛔ And it does NOT upgrade the "
            "size-class result: `birc2` and `mdm2` remain size-and-shape proxies, the paired size "
            "comparison is still computed on the four E3 bodies alone, and nothing measured on a proxy may "
            "be restated as an effector result. The route's paralogue-discrimination requirement is "
            "untouched by geometry and is not addressed here at all."
            % ", ".join(sorted(v["effector"] for v in named_arms.values() if v.get("effector"))))
    else:
        named_shortest, live_named = {}, []
        what_it_is_not = (
            "It is not evidence that any transcriptional effector binds, is recruited, is retained on "
            "chromatin, or changes transcription. It is an excluded-volume statement: a body of the stated "
            "size has somewhere to sit while its partner ligand occupies the NR4A3 cryptic pocket. The "
            "effector bodies are SIZE PROXIES and not effectors; no NAMED effector has been staged. And the "
            "second half of the route's requirement set — paralogue discrimination on the binder — is "
            "untouched by geometry and is not addressed here at all.")
    return {
        "★_the_named_effector": {
            "_what": ("what the enumeration can say about a NAMED transcriptional effector, as opposed to a "
                      "body of effector SIZE. This is the distinction the route memo turns on."),
            "status": named.get("status", "NO_NAMED_EFFECTOR_STAGED"),
            "n_named_effectors_enumerated": len(named_arms),
            "effectors": {a: {"effector": v.get("effector"), "source_pdb_id": v.get("source_pdb_id"),
                              "n_residues": v.get("n_residues"),
                              "shortest_linker_atoms": v.get(
                                  "shortest_linker_atoms_with_any_admissible_placement"),
                              "admits_at_the_%d_atom_gate" % GATE_ATOMS: v.get(
                                  "admits_within_the_%d_atom_gate" % GATE_ATOMS)}
                          for a, v in sorted(named_arms.items())},
            "answer": ("ADMITS" if live_named and min(live_named) <= CHEM_MAX_ATOMS
                       else "DOES NOT ADMIT" if live_named else "NOT ASKED — none staged"),
            "⚠_the_gate_still_cannot_fail": (
                "a named effector admitting is the same gate the proxies already passed at every rung. What "
                "changed is WHOSE excluded volume was tested, not how discriminating the test is."),
            "_what_remains_a_size_class_statement": named.get("_still_a_size_class_statement", []),
        },
        "★_the_size_axis": {
            "_what": ("the paired comparison that can return either way: does a single-domain "
                      "effector-size second terminus get MORE, LESS or the SAME admissible orientation "
                      "space as a multi-subunit E3, from identical anchors in the same pass?"),
            "n_rungs": n_rungs,
            "n_rungs_where_the_95pct_intervals_overlap": n_overlap,
            "size_ratio_single_over_multi_min": min(ratios) if ratios else None,
            "size_ratio_single_over_multi_max": max(ratios) if ratios else None,
            "★_n_rungs_where_the_WITHIN_class_spread_exceeds_the_BETWEEN_class_contrast": sum(
                1 for b in paired.values() if b.get("within_class_spread_exceeds_between_class_contrast")),
            "★_root_cause": (ablation or {}).get("★_reading"),
            # ⚠ DERIVED, NOT TYPED. An earlier version of this string asserted "the single-domain pool is
            #   lower at EVERY rung". That was true of one run and false of the next — the direction at the
            #   shortest rung is inside the noise. A hand-written summary of a sampled result is a number
            #   with no home, so the count is computed here and the sentence is built from it.
            "★_reading": (
                "the single-domain pool accepts LESS than the multi-subunit pool at %d of %d rungs and MORE "
                "at %d, and the contrast is NOT larger than the spread between two bodies of the SAME size "
                "at %d of %d rungs — so it may not be reported as a size law. Two ~90-residue single-domain "
                "bodies differ from each other by more than the classes differ from each other, which says "
                "the controlling variable is the individual body's shape and exit-vector geometry rather "
                "than how big it is. `per_arm_acceptance_rate` at each rung is where that is visible."
                % (sum(1 for r in ratios if r < 1.0), len(ratios),
                   sum(1 for r in ratios if r >= 1.0),
                   sum(1 for b in paired.values()
                       if b.get("within_class_spread_exceeds_between_class_contrast")),
                   n_rungs)),
            "at_the_%d_atom_gate" % GATE_ATOMS: {
                "single_domain_acceptance": (gate_blk.get("by_size_class", {})
                                             .get("single_domain", {}).get("acceptance_rate")),
                "multi_subunit_acceptance": (gate_blk.get("by_size_class", {})
                                             .get("multi_subunit", {}).get("acceptance_rate")),
                "ratio": gate_blk.get("size_ratio_single_over_multi"),
                "intervals_overlap": gate_blk.get("intervals_overlap"),
            },
        },
        "question": ("does the geometric envelope admit a second terminus of transcriptional-effector SIZE "
                     "at the linker distances this repository's own records call chemically routine?"),
        "answer": "ADMITS" if admits else "DOES NOT ADMIT",
        "admits_at_the_%d_atom_gate" % GATE_ATOMS: at_gate,
        "shortest_linker_atoms": {
            "effector_size_bodies": {a: summary[a]["shortest_linker_atoms_with_any_admissible_placement"]
                                     for a in eff},
            "E3_bodies": {a: summary[a]["shortest_linker_atoms_with_any_admissible_placement"] for a in e3},
        },
        "the_body_free_upper_bound": (
            "the anchor envelope is second-terminus-INDEPENDENT and is reported separately: it is what "
            "'the enumeration applies unchanged' means operationally, and every body result sits under it."),
        "⚠_the_binary_answer_is_not_the_finding": (
            "every body tested is admitted at every rung of the ladder, down to the shortest, so 'does the "
            "envelope admit an effector' is a gate that cannot fail — the same warning the basin search's "
            "own parameter block attaches to reading a reach gate at its sampling ceiling. The finding is "
            "the SIZE AXIS above: what the enumeration measures when the second terminus changes from a "
            "ligase to an effector-size body."),
        "required_distances": required,
        "⛔_what_this_answer_is_not": what_it_is_not,
        "_e3_comparator": ("the same test on the two downselected E3 bodies, run in the same pass from the "
                           "same anchors, is the paired comparator; %s"
                           % ("both admit" if len(live_e3) == len(e3) and live_e3 else
                              "not every E3 body admits")),
    }


# ==========================================================================================================
# MAP EDITS — described, never applied (the `map_edits_required` convention)
# ==========================================================================================================
def _strip_emphasis(s):
    """Markdown emphasis and code ticks removed, whitespace collapsed — so `retires **only `R12`**` and
    `retires only R12` compare equal. Used ONLY by the applied-edit check; see `map_edits_required`."""
    return " ".join(s.replace("*", "").replace("`", "").replace("_", "").split())


#: ⛔⛔ THE CORRECTION CONVENTION QUOTES THE TEXT IT RETIRES, AND A LIVE-ANCHOR SEARCH CANNOT TELL THAT
#: QUOTE FROM THE REAL THING (AUT-068, 2026-08-28). CLAUDE.md rule 1.2 REQUIRES a corrected passage to
#: carry its superseded wording — "Superseded, retained: '<the old sentence>'" — so applying a described
#: edit the way this repository mandates leaves `current_text` still findable in the file, and the PENDING
#: test below reads that retained quote as evidence the edit is still owed. Measured the day this landed:
#: all four remaining PENDING rows were false, and one of them had been applied weeks earlier.
#: ★ So a line is searched only UP TO its supersession marker. Text before the marker is live; the quoted
#: text after it is the retired version, by construction.
#: ⚠ WHAT THIS DELIBERATELY DOES NOT HANDLE, said rather than left to be discovered: a supersession quote
#: that WRAPS onto following lines is only skipped on the line carrying the marker, so a continuation line
#: can still match. Narrowing it further would need a quote parser, and a wrong one would suppress a real
#: PENDING — the direction that loses work. This trims the false positives it can prove and no more.
_SUPERSEDED_MARKERS = ("Superseded, retained", "superseded, retained", "SUPERSEDED, retained")


def _live_part(line):
    """The part of `line` that is a live assertion — everything before any supersession marker."""
    cut = len(line)
    for m in _SUPERSEDED_MARKERS:
        i = line.find(m)
        if i != -1:
            cut = min(cut, i)
    return line[:cut]


def _anchor_check(rel_path, needle, normalise=False, live_only=False):
    """Anchor discipline (the `map_edits` convention): a described edit must name text that is ACTUALLY in
    the live file. An entry that cannot be targeted says so rather than being silently wrong.

    `live_only` restricts the search to the live part of each line (see `_live_part`). It is passed for the
    PENDING question — "is the text I intend to replace still standing?" — and never for the APPLIED one,
    where a match anywhere is what is being asked.
    """
    p = os.path.join(REPO, rel_path)
    if not os.path.exists(p):
        return {"file_present": False, "current_text_found": False, "line": None}
    with open(p) as fh:
        lines = fh.read().split("\n")
    # ⚠ MEASURED ON THE NEEDLE AS GIVEN, BEFORE NORMALISATION, AND THE ORDER IS THE WHOLE POINT.
    #   `_strip_emphasis` COLLAPSES WHITESPACE, newlines included, so a multi-line needle stops looking
    #   multi-line the moment it is normalised — the first version of this tested after that call, the
    #   branch below never ran, and the row it exists for stayed unresolvable while the code read correct.
    multiline = "\n" in needle
    if normalise:
        needle = _strip_emphasis(needle)
    # ⛔ A MULTI-LINE NEEDLE CAN NEVER MATCH A LINE-AT-A-TIME SEARCH, AND ONE OF THESE EDITS IS ONE
    #   (AUT-068, 2026-08-28). `RT-TCIP.artifacts` proposes `"ART-TCIP-REACH",\n    "ART-TCIP-EFFECTOR-ARMS"`
    #   — a two-line JSON fragment. Searched per line it is absent however correctly it was applied, and the
    #   row could only ever read STALE_ANCHOR. Whitespace between the two tokens is not meaningful in JSON
    #   (the file's own indent differs from the proposal's), so both sides are whitespace-collapsed and the
    #   whole file is searched. Single-line needles keep the exact per-line path, which reports the LINE.
    if multiline:
        hay = "\n".join(_live_part(ln) for ln in lines) if live_only else "\n".join(lines)
        hay = _strip_emphasis(hay) if normalise else hay
        found = " ".join(needle.split()) in " ".join(hay.split())
        return {"file_present": True, "current_text_found": found, "line": None,
                "matched_ignoring_markdown_emphasis": bool(normalise),
                "matched_across_lines_ignoring_whitespace": True}
    for i, ln in enumerate(lines, 1):
        hay = _live_part(ln) if live_only else ln
        hay = _strip_emphasis(hay) if normalise else hay
        if needle in hay:
            return {"file_present": True, "current_text_found": True, "line": i,
                    "matched_ignoring_markdown_emphasis": bool(normalise)}
    return {"file_present": True, "current_text_found": False, "line": None}


def map_edits_required(census, summary):
    """★★ THE STATE OF A DESCRIBED EDIT IS DERIVED FROM THE FILE, NOT CARRIED IN A TYPED `status` STRING
    (2026-08-06 — this function's own convention failed on its first real success).

    A described-not-applied edit has a life cycle, and the first version of this only modelled its start.
    When another lane APPLIED four of these edits, their `current_text` correctly vanished from the files —
    and the anchor check, which only ever asked "is the text I want to replace still there?", reported
    `current_text_found: false` for all four. That is indistinguishable from the failure the check exists to
    catch (an edit naming text that was never in the file), so a lane doing exactly what was asked turned
    the build red and read as drift.

    ⛔ THE FIX IS NOT TO RELAX THE CHECK — it is to ask the second question the file can also answer. Both
    texts are looked for, and the state falls out:

      PENDING          `current_text` is present  → the edit is still owed, exactly as described.
      APPLIED          `current_text` is gone AND `proposed_text` is present → someone did it. Verified in
                       the file, not asserted by a status string, and NOT a failure.
      ⚠ STALE_ANCHOR   neither is present → the file moved in a way neither text matches. THIS is the real
                       defect, and it is now the only thing that can fail the build.
    """
    edits = _map_edits(census, summary)
    for e in edits:
        f = e["file"].split(" (")[0]
        if not e.get("current_text"):
            e["anchor_check"] = None
            e["state"] = "NO_ANCHOR"
            continue
        cur = _anchor_check(f, e["current_text"], live_only=True)
        # ⚠ THE APPLIED CHECK IS EMPHASIS-INSENSITIVE AND THE PENDING ONE IS NOT, DELIBERATELY.
        #   A lane that applies a described edit is free to bold or code-format it — the roadmap's Q12 fix
        #   landed as "retires **only `R12`**" against a proposal of "retires only `R12`" — and an exact
        #   match would have called a correctly applied edit STALE. The PENDING check stays exact, because
        #   there the question is "is the text I intend to replace literally still here", and a fuzzy yes
        #   would send someone to edit a line that no longer says what they think.
        prop = _anchor_check(f, e["proposed_text"], normalise=True) if e.get("proposed_text") else None
        e["anchor_check"] = cur
        e["applied_check"] = prop
        # ⛔⛔ AN ADDITIVE EDIT'S ANCHOR SURVIVES ITS OWN APPLICATION, SO ITS PRESENCE PROVES NOTHING
        #   (AUT-068, 2026-08-28). `RT-TCIP.artifacts` was described as `"ART-TCIP-REACH"` ->
        #   `"ART-TCIP-REACH", "ART-TCIP-EFFECTOR-ARMS"`. The old string is a SUBSTRING of the new one, so
        #   it is still in the file after a correct application and the PENDING test below matched it —
        #   before the edit and after it alike. That row could never reach APPLIED by any action, which is
        #   the "reports while measuring nothing" shape this repository keeps paying for: a reader chasing
        #   it would re-apply an edit that was already there.
        # ★ So when the anchor cannot discriminate, the APPLIED question is the only one that can, and it
        #   decides alone. This narrows what PENDING means; it never suppresses a STALE_ANCHOR.
        additive = bool(e.get("proposed_text")) and e["current_text"] in e["proposed_text"]
        # ⚠ AND THE SUPPRESSION IS NARROWER THAN "IGNORE THE ANCHOR WHEN IT IS ADDITIVE", BECAUSE THE FIRST
        #   VERSION OF IT WAS THAT AND MADE A ROW WORSE. The `closure_kind` row proposes `open — NO EDIT
        #   REQUIRED` against a current text of `open`, so it is additive too — and with the anchor simply
        #   ignored it fell through to STALE_ANCHOR, the one state that fails the build, for a row whose
        #   whole point is that nothing is owed. An uninformative anchor is only overridden by a POSITIVE
        #   applied reading; with none, the row stays PENDING, which is the direction that loses nothing.
        applied = bool(prop and prop["current_text_found"])
        if not cur["file_present"]:
            e["state"] = "FILE_MISSING"
        elif cur["current_text_found"] and not (additive and applied):
            e["state"] = "PENDING"
        elif applied:
            e["state"] = "APPLIED"
            e["_applied_note"] = ("the text this edit asked for is IN the file and the text it asked to "
                                  "replace is gone — applied by another lane, verified here by reading the "
                                  "file rather than by trusting a status field")
        else:
            e["state"] = "STALE_ANCHOR"
    return edits


def _map_edits(census, summary):
    return [
        {
            "file": "research/manuscripts/nr4a3-program-map.md",
            "anchor": "Q12 row of the open-questions table, and the modality fork row",
            "current_text": "`R4` `R5` `R7` (retires `R9` `R10` `R12`)",
            "evidence_r9_r10_are_not_retired": [
                "R9 is 'OUR ternary is correctly assembled' (roadmap requirement table) — not "
                "'our ternary WITH AN E3'; its instrument V2 is a general ternary generator",
                "R10 is 'A ternary forms' — a TCIP is bivalent and induces a target·molecule·effector "
                "complex, so a ternary is exactly what it needs",
                "R12 is 'The ternary is compatible with DEGRADATION — productive unique-lysine geometry', "
                "which is the only one a non-degrading modality removes",
                "systems/graph/routes.json RT-TCIP: blockers_retired = [BLK-TERNARY-GEOMETRY] alone, "
                "blockers_inherited includes BLK-INDUCED-COMPLEX, and required_validation carries "
                "'A ternary geometry for the induced complex' as feasible_today=false",
            ],
            "proposed_text": "`R4` `R5` `R7` `R9` `R10` (retires `R12`)",
            "why": ("R9 is 'OUR ternary is correctly assembled' and R10 is 'a ternary forms'. A TCIP is "
                    "bivalent and induces a target-molecule-effector complex, so both survive; only R12 "
                    "('the ternary is compatible with DEGRADATION — productive unique-lysine geometry') is "
                    "retired by not degrading. The graph already encodes the correct version — "
                    "RT-TCIP.blockers_retired is [BLK-TERNARY-GEOMETRY] alone while BLK-INDUCED-COMPLEX is "
                    "inherited — so the roadmap and the graph currently disagree."),
            "evidence": ("systems/graph/routes.json RT-TCIP.blockers_retired / blockers_inherited; "
                         "systems/AUDIT-2026-08-06-routes.md 'Left open deliberately'; and "
                         "research/manuscripts/program/target-route-options.md route 6, which states BOTH readings "
                         "in one section ('retires R9 ... R10 and R12 outright' and 'it inherits the same "
                         "induced-complex modelling problem as R9')"),
            "status": "DESCRIBED, NOT APPLIED — the roadmap is off-limits to this lane",
        },
        {
            "file": "research/manuscripts/program/path-family-synthesis.md",
            "anchor": "Tier 3 table, row 12 (TCIP)",
            "current_text": "retires `R9`/`R10`/`R12`; keeps `R4`/`R5`/`R7`",
            "proposed_text": "retires `R12`; keeps `R4`/`R5`/`R7`/`R9`/`R10`",
            "why": "same correction, same evidence; this file mirrors the roadmap's claim",
            "status": "DESCRIBED, NOT APPLIED",
        },
        {
            "file": "research/manuscripts/nr4a3-program-map.md",
            "anchor": "THE MODALITY at C397 — the modality fork row",
            "current_text": "Picking **TCIP** keeps `R4` `R5` `R7` and retires the same three.",
            "proposed_text": ("Picking **TCIP** keeps `R4` `R5` `R7` `R9` `R10` and retires only `R12` — a "
                              "TCIP is bivalent and still induces a ternary, so it retires the "
                              "ubiquitin-transfer half and nothing else."),
            "why": "same correction as the Q12 row; this row states it a second time by reference",
            "status": "DESCRIBED, NOT APPLIED",
        },
        {
            "file": "research/manuscripts/program/target-route-options.md",
            "anchor": "§2 route register, row 6",
            "current_text": "Keeps `R4` `R5` `R7`; **retires `R9` `R10` `R12`**",
            "proposed_text": "Keeps `R4` `R5` `R7` `R9` `R10`; **retires `R12`**",
            "why": "same correction; this is the register row the roadmap's Q12 points at",
            "status": "DESCRIBED, NOT APPLIED",
        },
        {
            "file": "research/manuscripts/program/target-route-options.md",
            "anchor": "Route 6 — TCIP, prose",
            "current_text": "so it retires `R9`",
            # ⛔ THE PROPOSAL IS RECORDED AS THE WORDING THAT WAS ACTUALLY ADOPTED, NOT THE ONE FIRST
            #   DRAFTED (AUT-068, 2026-08-28). The correction landed weeks ago and the file now reads
            #   "**`R9` and `R10` survive unchanged**: a TCIP is bivalent ...", with the retired sentence
            #   kept beneath it as rule 1.2 requires. The original proposal — "so it retires `R12`, and
            #   `R9`/`R10` survive unchanged" — was never used verbatim, so the applied check could not
            #   find it and the row read STALE_ANCHOR: an edit "verified while targeting nothing", which
            #   is the one state that fails the build. ⚠ The FIX IS NOT TO REWORD THE LIVE FILE TO MATCH
            #   A DESCRIPTION. The prose is correct and clearer than the proposal; a described edit exists
            #   to be checked against the file, so when the two disagree and the FILE is right, the
            #   description is what moves. Superseded, retained: "so it retires `R12`, and `R9`/`R10`
            #   survive unchanged".
            "proposed_text": "`R9` and `R10` survive unchanged",
            "why": ("this section contradicts itself two paragraphs later — 'It inherits the same "
                    "induced-complex modelling problem as `R9` (an assembled ternary-like complex nobody has "
                    "built), which is the roadmap's largest gap'. Both sentences cannot stand, and the "
                    "second one is the one the graph agrees with."),
            "status": "DESCRIBED, NOT APPLIED",
        },
        {
            "file": "systems/graph/routes.json",
            "anchor": "RT-TCIP.readiness.why_not_higher / .missing",
            # ⚠ REWRITTEN 2026-08-06 (second pass). Superseded, retained: this entry asked for "The
            #   enumeration machinery exists and takes one more anchor set." to become a sentence saying
            #   the effector arm was still MISSING. The graph lane applied it — and then the arm was
            #   staged, so the APPLIED text is itself stale, in the same direction. Both texts are derived
            #   from the census below rather than typed, so the next state change cannot go stale silently.
            "current_text": "What it cannot yet name is an effector",
            "proposed_text": ("It can now name an effector: %d transcriptional-effector bodies are staged "
                              "(%s) and the enumeration runs on them, so the admissibility statement is no "
                              "longer proxy-carried. What is still proxy-carried is the SIZE comparison, "
                              "which is computed on the four E3 bodies alone."
                              % (census["answer"], ", ".join(census["effector_arm_ids"]) or "none")),
            "why": ("'one more anchor set' reads as an input someone can type. Measured, it is a staged "
                    "structure with coordinates and a ligand exit vector, and the count of them is now %d "
                    "(%s). `readiness.missing` should drop 'a staged transcriptional-effector body' and "
                    "keep every other entry."
                    % (census["answer"], ", ".join(census["effector_arm_ids"]) or "none")),
            "status": "DESCRIBED, NOT APPLIED — systems/graph is off-limits to this lane",
        },
        {
            "file": "systems/graph/routes.json",
            "anchor": "RT-TCIP.artifacts",
            # ⚠ Superseded, retained: this asked for `[]` → `["research/modalities/nr4a3-tcip-reach.json"]`.
            #   The graph lane applied it as the ID `ART-TCIP-REACH`, which is the register's convention and
            #   is better than what was asked for. The remaining edit is the SECOND artifact.
            "current_text": "\"ART-TCIP-REACH\"",
            "proposed_text": "\"ART-TCIP-REACH\",\n    \"ART-TCIP-EFFECTOR-ARMS\"",
            "why": ("the route now also holds a staged-input artifact of its own — the effector arm "
                    "registry that made the named-effector statement possible. The full proposed "
                    "artifacts.json record is in research/modalities/nr4a3-tcip-route-memo.md section 10."),
            "status": "DESCRIBED, NOT APPLIED",
        },
        {
            "file": "systems/graph/artifacts.json",
            "anchor": "ART-TCIP-REACH.note — the trailing 'no effector arm is staged' clause",
            "current_text": "no effector arm is staged in this repository",
            "proposed_text": ("they alone carry the paired size comparison. From 2026-08-06 the enumeration "
                              "ALSO runs %d NAMED transcriptional effectors staged in "
                              "ART-TCIP-EFFECTOR-ARMS; the admissibility statement is upgraded for those "
                              "arms and the size comparison is NOT. Superseded, retained: 'no effector arm "
                              "is staged in this repository.'" % census["answer"]),
            "why": ("the registered note asserts a count that is now wrong, and it is the note a reader "
                    "consults to decide whether this artifact may be quoted about an effector at all."),
            "status": "DESCRIBED, NOT APPLIED — systems/graph is off-limits to this lane",
        },
        {
            "file": "systems/graph/routes.json (ALREADY CORRECT — recorded so it is not 'fixed' twice)",
            "anchor": "RT-TCIP.closure_kind",
            "current_text": "open",
            "proposed_text": "open — NO EDIT REQUIRED",
            "why": ("the 2026-08-06 route audit found this filed as `instrument_limit` with no instruments "
                    "and nothing failed, and the same pass corrected it. Measured on this branch it reads "
                    "`open`. The half of that audit finding that is still live is the R9/R10 claim above."),
            "status": "VERIFIED CLOSED — no action",
        },
    ]


# ==========================================================================================================
# MARKDOWN
# ==========================================================================================================
def to_markdown(d):
    L, A = [], None
    A = L.append
    # Frontmatter is EMITTED, never hand-added: systems_check `[D4]` requires purpose/scope/audience/
    # freshness on every tracked document, and this memo is regenerated, so a hand-added block would be
    # dropped on the next run and turn the build red again with no trace of why. ⚠ No generation DATE is
    # stamped here on purpose — a date that changes every run makes `--check` report "does not reproduce"
    # the following day, which is the trap the steric audit hit and had to special-case.
    A("---")
    A("id: DOC-NR4A3-TCIP-REACH")
    A("title: TCIP reach enumeration — does the envelope admit an effector-size second terminus")
    A("level: L4")
    A("kind: memo")
    A("status: generated")
    A("generator: research/modalities/nr4a3_tcip_reach.py")
    A("canonical_for: []")
    A("purpose: \"Run the paired anchor-plus-effector reach enumeration with a transcriptional-effector "
      "second terminus, reusing the E3-free machinery, and report the graded size axis rather than the "
      "binary gate.\"")
    A("scope: Geometry only. No binding, activity, degradation, selectivity or efficacy statement.")
    A("audience: [maintainers, autonomous research agents]")
    A("date: %s" % _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d"))
    A("last_verified: unverified")
    A("---")
    A("")
    A("# %s" % d["_title"])
    A("")
    A("> **$0, CPU, pure stdlib.** %s" % d["_status"])
    A(">")
    A("> Generated by `nr4a3_tcip_reach.py`; this file is derived — edit the module, not this.")
    A("")
    A("**Question.** %s" % d["_question"])
    A("")
    v = d["verdict"]
    A("## 1 · The answer")
    A("")
    A("**%s** — the envelope %s a second terminus of transcriptional-effector size within the %d-backbone-"
      "atom chemically routine ceiling; at the %d-atom gate: **%s**."
      % (v["answer"], "admits" if v["answer"] == "ADMITS" else "does not admit", CHEM_MAX_ATOMS, GATE_ATOMS,
         v["admits_at_the_%d_atom_gate" % GATE_ATOMS]))
    A("")
    nv0 = v.get("★_the_named_effector") or {}
    if (nv0.get("effectors") or {}):
        A("★★ **And it is no longer only a SIZE statement.** %d NAMED transcriptional effector(s) are now "
          "staged and enumerated — %s — so the envelope's answer for them is **%s**, computed from their own "
          "coordinates rather than from a proxy of similar size. **The size-class result is unchanged and is "
          "still carried by proxies; see §1b for exactly which sentences may and may not be upgraded.**"
          % (nv0["n_named_effectors_enumerated"],
             ", ".join("%s (%s, %s)" % (r["effector"], a, r["source_pdb_id"])
                       for a, r in sorted(nv0["effectors"].items())),
             nv0["answer"]))
        A("")
    ne = d.get("★_named_effector") or {}
    named_arms = ne.get("effector_arms") or {}
    A("| body | what it is | size class | residues | shortest linker (backbone atoms) with any admissible "
      "placement |")
    A("|---|---|---|---|---|")
    for aid, s in sorted(d["summary"].items()):
        if aid in named_arms:
            what = "**NAMED transcriptional effector** — %s" % named_arms[aid]["effector"]
        elif aid in SINGLE_DOMAIN_ARMS:
            what = "E3 recruiter, used as an effector-SIZE proxy"
        else:
            what = "E3 recruiter (replication target)"
        A("| `%s` | %s | %s | %d | **%s** |"
          % (aid, what, s["size_class"], s["n_residues"],
             s["shortest_linker_atoms_with_any_admissible_placement"]))
    A("")
    A("⛔ %s" % v["⛔_what_this_answer_is_not"])
    A("")

    if named_arms:
        nv = v["★_the_named_effector"]
        A("## 1b · ★★ The NAMED effector — what changed, and what did not")
        A("")
        A("%s" % ne["_what"])
        A("")
        A("| effector | what it is | source PDB | body | residues | shortest admitting linker | admits at "
          "the %d-atom gate |" % GATE_ATOMS)
        A("|---|---|---|---|---|---|---|")
        for aid, r in sorted(named_arms.items()):
            A("| **%s** (`%s`) | %s | %s | %s | %d | **%s** | %s |"
              % (r["effector"], aid, (r["effector_role"] or "").split(";")[0], r["source_pdb_id"],
                 "+".join(r["chains"]), r["n_residues"],
                 r["shortest_linker_atoms_with_any_admissible_placement"],
                 r["admits_within_the_%d_atom_gate" % GATE_ATOMS]))
        A("")
        A("| linker atoms | " + " | ".join("`%s` acceptance (95 %% CI)" % a for a in sorted(named_arms))
          + " | " + " | ".join("`%s` body cost" % a for a in sorted(named_arms)) + " |")
        A("|---|" + "---|" * (2 * len(named_arms)))
        for n in sorted(ne["by_linker_atoms"], key=int):
            b = ne["by_linker_atoms"][n]
            rates = ["%s [%s, %s]" % (b[a]["acceptance_rate"], b[a]["acceptance_ci95"][0],
                                      b[a]["acceptance_ci95"][1]) if a in b else "—"
                     for a in sorted(named_arms)]
            costs = [str(b[a]["body_cost"]) if a in b else "—" for a in sorted(named_arms)]
            A("| %s | %s | %s |" % (n, " | ".join(rates), " | ".join(costs)))
        A("")
        A("⚠ %s" % nv["⚠_the_gate_still_cannot_fail"])
        A("")
        A("⛔ **What is still a SIZE-CLASS statement and may not be restated as an effector one:**")
        for s in nv["_what_remains_a_size_class_statement"]:
            A("- %s" % s)
        A("")
        ex = (d.get("cross_checks") or {}).get("exit_vector_comparability") or {}
        if ex.get("status") in ("AGREES", "FLAGS"):
            A("### 1c · Is the named arm comparable to the committed four?")
            A("")
            A("%s" % ex["_reading"])
            A("")
            A("| arm | partner class | ligand | heavy atoms | exit-atom exposure (Å) | inside the committed "
              "E3 range |")
            A("|---|---|---|---|---|---|")
            for r in ex["rows"]:
                A("| `%s` | %s | %s | %s | %s | %s |"
                  % (r["arm_id"], r["partner_class"], r["ligand_het"], r["ligand_n_heavy"],
                     r["exit_atom_exposure_A"], r.get("inside_the_committed_E3_range")))
            A("")
            A("Committed E3 exposure range: **%s–%s Å**. Effector arms inside it: %s. Outside it: %s."
              % (ex["committed_E3_exposure_range_A"][0], ex["committed_E3_exposure_range_A"][1],
                 ", ".join("`%s`" % a for a in ex["effector_arms_inside_that_range"]) or "none",
                 ", ".join("`%s` (%s Å)" % (r["arm_id"], r["exit_atom_exposure_A"])
                           for r in ex["effector_arms_outside_it"]) or "none"))
            A("")

    A("## 2 · What \"one more anchor set\" is, measured")
    A("")
    c = d["what_one_more_anchor_set_means"]["census"]
    A("**Staged transcriptional-effector arms in this repository: %d** (of %d staged arms, %d loadable as "
      "rigid bodies)." % (c["answer"], c["n_staged_arms_total"], c["n_loadable"]))
    A("")
    A("| arm | recruiter | partner class | source PDB | loadable |")
    A("|---|---|---|---|---|")
    for r in c["arms"]:
        A("| `%s` | %s | %s | %s | %s |" % (r["arm_id"], r["recruiter"], r["partner_class"],
                                            r["source_pdb_id"], r["loadable_as_rigid_body"]))
    A("")
    A("%s" % c["_reading"])
    A("")

    A("## 3 · The body-free anchor envelope — the E3-free machinery")
    A("")
    A("Fraction of the reach shell in which a second terminus's ligand exit atom can sit at all, pooled over "
      "the 12 committed warhead anchors. Deterministic grid; no RNG.")
    A("")
    A("| linker atoms | shell radius (Å) | mean fraction admissible | min over poses | max over poses |")
    A("|---|---|---|---|---|")
    for n in sorted(d["anchor_envelope_body_free"]["pooled"], key=int):
        r = d["anchor_envelope_body_free"]["pooled"][n]
        A("| %s | %s | **%s** | %s | %s |" % (n, r["shell_hi_A"], r["mean_fraction_admissible"],
                                              r["min_fraction_admissible"], r["max_fraction_admissible"]))
    A("")

    A("## 4 · The paired placement envelope — same anchors, same sampler, %d real bodies" % len(d["summary"]))
    A("")
    A("| linker atoms | " + " | ".join("`%s` (%s)" % (a, d["summary"][a]["size_class"].replace("_", " "))
                                       for a in sorted(d["summary"])) + " |")
    A("|---|" + "---|" * len(d["summary"]))
    for n in sorted({int(k) for a in d["summary"] for k in d["summary"][a]["by_linker_atoms"]}):
        cells = []
        for a in sorted(d["summary"]):
            r = d["summary"][a]["by_linker_atoms"].get(str(n))
            cells.append("%d/%d poses · %d accepted" % (r["n_poses_with_any_admissible_placement"],
                                                        r["n_poses"], r["total_accepted"]) if r else "—")
        A("| %d | %s |" % (n, " | ".join(cells)))
    A("")
    A("Read as: how many of the 12 warhead anchors admit **any** placement of that body at that linker "
      "length, and how many placements were accepted out of the samples drawn.")
    A("")

    A("## 4b · ★ The size axis — the comparison that can return either way")
    A("")
    A("⚠ %s" % d["verdict"]["⚠_the_binary_answer_is_not_the_finding"])
    A("")
    A("| linker atoms | single-domain acceptance (95 % CI) | multi-subunit acceptance (95 % CI) | ratio "
      "single/multi | intervals overlap | single-domain body cost | multi-subunit body cost |")
    A("|---|---|---|---|---|---|---|")
    for n in sorted(d["★_paired_body_size_comparison"], key=int):
        b = d["★_paired_body_size_comparison"][n]
        s, m = b["by_size_class"]["single_domain"], b["by_size_class"]["multi_subunit"]
        A("| %s | %s [%s, %s] | %s [%s, %s] | **%s** | %s | %s | %s |"
          % (n, s["acceptance_rate"], s["acceptance_ci95"][0], s["acceptance_ci95"][1],
             m["acceptance_rate"], m["acceptance_ci95"][0], m["acceptance_ci95"][1],
             b["size_ratio_single_over_multi"], b["intervals_overlap"], s["body_cost"], m["body_cost"]))
    A("")
    A("`body cost` = acceptance ÷ the body-free admissible fraction of the same shell — the body's own "
      "marginal cost with the target's shape divided out.")
    A("")
    A("### 4c · ⛔ The control that stops the row above being read as a size law")
    A("")
    A("%s" % d["verdict"]["★_the_size_axis"]["★_reading"])
    A("")
    arms_o = sorted(d["summary"])
    A("| linker atoms | " + " | ".join("`%s` (%d res)" % (a, d["summary"][a]["n_residues"])
                                       for a in arms_o)
      + " | within-class spread (single / multi) | between-class contrast | within > between |")
    A("|---|" + "---|" * (len(arms_o) + 3))
    for n in sorted(d["★_paired_body_size_comparison"], key=int):
        b = d["★_paired_body_size_comparison"][n]
        pa = b.get("per_arm_acceptance_rate", {})
        A("| %s | %s | %s / %s | %s | **%s** |"
          % (n, " | ".join(str(pa.get(a)) for a in arms_o),
             b["by_size_class"]["single_domain"].get("within_class_spread_ratio"),
             b["by_size_class"]["multi_subunit"].get("within_class_spread_ratio"),
             b.get("between_class_contrast_ratio"),
             b.get("within_class_spread_exceeds_between_class_contrast")))
    A("")

    ab = d.get("★_interface_floor_ablation")
    if ab:
        A("### 4d · ★★ Root cause — the interface floor, ablated")
        A("")
        A("%s" % ab["_what"])
        A("")
        A("| `min_contact_residues` | single-domain acceptance | multi-subunit acceptance | ratio |")
        A("|---|---|---|---|")
        for f in sorted(ab["by_floor"], key=lambda k: -int(k)):
            r = ab["by_floor"][f]
            A("| %s%s | %s | %s | **%s** |"
              % (f, " (committed)" if int(f) == ab["committed_floor"] else "",
                 r["single_domain_acceptance"], r["multi_subunit_acceptance"],
                 r["ratio_single_over_multi"]))
        A("")
        A("**%s**" % ab["★_reading"])
        A("")
        A("⛔ %s" % ab["⛔_what_this_does_not_settle"])
        A("")

    A("## 5 · The distances the modality requires")
    A("")
    for k, val in sorted(d["verdict"]["required_distances"].items()):
        if k.startswith("_") or k == "sources" or k.startswith("⚠"):
            continue
        A("- `%s` = %s" % (k, val))
    A("")
    A("⚠ %s" % d["verdict"]["required_distances"]["⚠_no_tcip_specific_distance_is_used"])
    A("")

    A("## 6 · Cross-checks (rule 1)")
    A("")
    for k, val in d["cross_checks"].items():
        A("- `%s`: **%s**%s" % (k, val.get("status"),
                                (" (n = %s)" % val["n_cells_compared"]) if val.get("n_cells_compared")
                                else (" (n = %s)" % val["n_compared"]) if val.get("n_compared") else ""))
    A("")

    A("## 7 · What this inherits and cannot say")
    A("")
    for lim in d["_inherits"]:
        A("- %s" % lim)
    A("")
    if d["refusals"]:
        A("**Refusals:** %s" % "; ".join("%s — %s" % (r.get("what"), r.get("reason")) for r in d["refusals"]))
        A("")
    return "\n".join(L) + "\n"


# ==========================================================================================================
# DRIVER
# ==========================================================================================================
def build(samples=300000, arms_wanted=None, ladder=LADDER, n_procs=4, struct_dir=STRUCT_DIR,
          ablation_samples=30000):
    global _ARMS, _POSES, _FIELD
    t0 = time.time()
    refusals, unread = [], []

    m3 = BS.load_paralogue(os.path.join(struct_dir, "nr4a3-opened.pdb"))
    field3 = G.SquaredDistanceField(m3["heavy_xyz"], cell=0.9, clamp=8.0)
    reactive = BS.load_reactive_map(UNIQUE_JSON, m3)
    poses = BS.build_pose_ensemble(m3, reactive, field3, 12, random.Random(BASIN_SEED))

    regs = load_registries()
    # The staged NAMED effectors are DERIVED from the effector registry, never a list typed here — a typed
    # list is how an arm that failed to stage gets enumerated anyway, and a `status: OK` a defaulted record
    # could also have written is exactly what this repository has been bitten by. `staged_effector_arm_ids`
    # requires the coordinates to be on disk.
    effector_ids = staged_effector_arm_ids()
    arms, geom = {}, {}
    for aid in (arms_wanted or list(SINGLE_DOMAIN_ARMS) + list(MULTI_SUBUNIT_ARMS) + effector_ids):
        entry = regs.get(aid)
        if entry is None:
            refusals.append({"what": aid, "reason": "not in either registry"})
            continue
        rec = entry[0]
        try:
            arm = BS.load_arm_from_registry(rec)
        except Exception as exc:                                   # noqa: BLE001 — refuse, never guess
            refusals.append({"what": aid, "reason": "%s: %s" % (type(exc).__name__, exc)})
            continue
        arms[aid] = arm
        geom[aid] = body_geometry(arm)

    _ARMS, _POSES, _FIELD = arms, {p["pose_id"]: p for p in poses}, field3

    # ⛔ THE SEED MUST NOT COME FROM `hash()`. Python salts `hash(str)` per PROCESS unless PYTHONHASHSEED is
    #   set, so `hash(aid)` made every cell's seed depend on which interpreter happened to run it — a
    #   sampled artifact that does not reproduce between runs, which is exactly what this lane's own
    #   `ball_grid` docstring refuses ("a sampled reach answer that moved between runs would be unusable as
    #   a gate"). Caught by comparing two full runs: the pooled size ratio moved 0.871 -> 0.869 and the
    #   12-atom-gate ratio 0.871 -> 0.914 with no code change. `zlib.crc32` is a fixed function of the
    #   bytes and is stable across processes, versions and platforms.
    def _arm_salt(name):
        return zlib.crc32(name.encode("utf-8")) % 997

    jobs = [{"arm_id": aid, "pose_id": p["pose_id"], "n_atoms": n, "n_samples": samples,
             "seed": BASIN_SEED + 1000 * n + _arm_salt(aid) + i}
            for aid in sorted(arms) for n in ladder for i, p in enumerate(poses)]

    if n_procs and n_procs > 1:
        import multiprocessing as mp
        with mp.Pool(n_procs) as pool:
            cells = pool.map(_worker, jobs, chunksize=1)
    else:
        cells = [_worker(j) for j in jobs]

    free = {p["pose_id"]: body_free_envelope(tuple(p["anchor_xyz"]), field3, ladder) for p in poses}
    pooled = {}
    for n in ladder:
        fr = [free[pid][str(n)]["fraction_admissible"] for pid in free]
        pooled[str(n)] = {
            "shell_hi_A": free[poses[0]["pose_id"]][str(n)]["shell_hi_A"],
            "mean_fraction_admissible": round(sum(fr) / len(fr), 5),
            "min_fraction_admissible": round(min(fr), 5),
            "max_fraction_admissible": round(max(fr), 5),
            "n_poses_with_any": sum(1 for x in fr if x > 0),
        }

    summary = summarise(cells, geom)
    paired = paired_body_size_comparison(cells, pooled, geom)
    # ★ THE ROOT-CAUSE CONTROL RUNS INSIDE THE BUILD, NOT AS A SEPARATE PASS MERGED IN AFTERWARDS. An
    #   artifact assembled from two commands is an artifact no single command reproduces, and this
    #   repository has already paid for one of those.
    ablation = interface_floor_ablation(arms, poses, field3, n_samples=ablation_samples)
    census = effector_arm_census()
    named = named_effector_reading(cells, summary, geom, pooled,
                                   [a for a in effector_ids if a in arms], census)
    req = required_distances()

    d = {
        "_title": "Does the reach envelope admit a transcriptional-effector second terminus? (RT-TCIP)",
        "_question": ("The reach enumeration was built for E3 recruitment. Does it apply unchanged when the "
                      "second terminus is a transcriptional effector rather than a ligase, and does the "
                      "geometric envelope it returns admit an effector-size body at the linker distances "
                      "this repository's own committed records call chemically routine?"),
        "_status": ("GEOMETRY ONLY, $0 CPU, pure stdlib. No binding, potency, selectivity, transcriptional, "
                    "efficacy, safety, therapeutic-window or clinical claim is made or implied. An 'admits' "
                    "answer is an excluded-volume statement, never an activity one."),
        "_method": ("PAIRED: the body-free anchor envelope and %d real staged bodies computed in one pass "
                    "from identical warhead anchors, an identical target frame, an identical distance field "
                    "and `nr4a3_basin_search.sample_placements` UNCHANGED — only the rigid body differs. The "
                    "committed E3 run is a REPLICATION TARGET, not the comparator." % len(arms)),
        "_inherits": [
            "every warhead anchor is conditional on the cryptic pocket being the site, which `V3` left "
            "INCONCLUSIVE — the `R5` SITE half, carried whole from the E3 lane",
            "⭐ but NOT the `R5` POSE half: the anchors are MARGINALISED over pocket-mouth positions "
            "(`nr4a3_basin_search.build_pose_ensemble`, 12 anchors in a 5–11 Å shell around the pocket "
            "centroid), not taken from a docked pose. `pose-convergence-401.json`'s 7.006 Å median "
            "pocket-superposed ligand RMSD with `cross_method_evidence: NONE` is a statement about a DOCKED "
            "POSE this enumeration does not use, so it is not inherited as a coordinate error here — what is "
            "inherited is the site premise both rest on",
            "one opened NR4A3 model frame; no ensemble, no dynamics, no induced fit of the target",
            "the second-terminus bodies are single deposited conformers, and `birc2`/`mdm2` are NOT "
            "transcriptional effectors — they are size-and-shape proxies, they are labelled so everywhere, "
            "and they alone carry the paired SIZE comparison",
            "⛔ a staged NAMED effector is its LIGAND-BINDING DOMAIN, not the full-length protein: a BCL6 "
            "BTB dimer is not BCL6 and a bromodomain is not BRD4. Everything outside the deposited "
            "construct is absent from the excluded volume, so an admitting answer is an UPPER bound on what "
            "the full protein would allow — and the full protein is what a cell contains",
            "⛔ the DNA and chromatin a transcriptional effector is bound to are absent entirely; a "
            "DNA-bound effector's accessible volume is smaller than a free domain's, and this enumeration "
            "cannot see that",
            "`BLK-INDUCED-COMPLEX` is untouched: nothing here assembles or scores an induced complex, and no "
            "NR4A3 ternary of any kind has been correctly assembled by anyone",
            "the route's paralogue-discrimination requirement (`R7`) is not a geometry question and is not "
            "addressed at all",
        ],
        "what_one_more_anchor_set_means": {
            "_what_the_reach_modules_actually_consume": (
                "two points per cell: `a` (warhead exit-vector anchor, target-side, reused unchanged) and "
                "`b` (the second terminus's ligand exit atom). `b` is not typeable — it is produced by "
                "`nr4a3_basin_search.sample_placements` from a staged RIGID BODY."),
            "_the_input_that_is_missing": (
                "a registry record with `receptor_pdb` coordinates and `ligand.exit_atom_xyz` for a "
                "transcriptional effector. That is the anchor set."),
            "census": census,
        },
        "body_geometry": geom,
        "anchor_envelope_body_free": {
            "_what": ("the fraction of each linker-length reach shell in which a second terminus's exit atom "
                      "can sit at all — the sampler's OWN anchor test on a deterministic grid"),
            "_test": ("field3.min_dist(b) - cell_slack >= pose_min_clearance_A = %.1f Å, the predicate "
                      "`sample_placements` uses, evaluated on a %.1f Å lattice instead of by Monte-Carlo"
                      % (MIN_CLEARANCE, ENVELOPE_PITCH_A)),
            "pooled": pooled,
            "per_pose": free,
        },
        "paired_placement_envelope": {
            "_what": ("every (body x warhead anchor x linker length) cell through the committed sampler, "
                      "unchanged, with `linker_max_atoms` set to the rung being asked about"),
            "samples_per_cell": samples,
            "cells": cells,
        },
        "summary": summary,
        "★_named_effector": named,
        "★_paired_body_size_comparison": paired,
        "★_interface_floor_ablation": ablation,
        "cross_checks": {
            "reproduces_the_committed_pose_ensemble": crosscheck_pose_ensemble(poses),
            "committed_accepted_anchors_are_admissible": crosscheck_committed_anchors_admissible(field3),
            "replicates_the_committed_E3_acceptance": crosscheck_replicates_committed_acceptance(cells),
            "size_labels_match_the_coordinates": crosscheck_size_partition(geom),
            "acceptance_test_is_E3_free": crosscheck_acceptance_is_e3_free(arms, poses, field3),
            "exit_vector_comparability": crosscheck_exit_vector_comparability(census, regs),
        },
        "refusals": refusals,
        "unread_inputs": unread,
        "runtime_s": round(time.time() - t0, 1),
    }
    d["verdict"] = verdict(summary, pooled, req, paired, ablation, named)
    d["map_edits_required"] = map_edits_required(census, summary)
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--samples", type=int, default=300000, help="rigid-body samples per (arm x pose x rung)")
    ap.add_argument("--arms", default="", help="comma-separated subset of registry arm ids")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--only-e3-free-check", action="store_true",
                    help="run ONLY the E3-free acceptance control and merge it into an existing --out")
    ap.add_argument("--only-interface-ablation", action="store_true",
                    help="run ONLY the interface-floor ablation and merge it into an existing --out")
    ap.add_argument("--ablation-samples", type=int, default=30000)
    ap.add_argument("--refresh-derived", action="store_true",
                    help="recompute the DERIVED blocks (summaries, comparisons, cross-check readings, map "
                         "edits, verdict, markdown) from the sampled cells already stored in --out. No "
                         "sampling is re-run, so no number changes — this exists so a reporting fix does "
                         "not require a re-measurement, and it refuses if the cells are absent.")
    args = ap.parse_args(argv)

    if args.refresh_derived:
        with open(args.out) as fh:
            d = json.load(fh)
        cells = (d.get("paired_placement_envelope") or {}).get("cells")
        if not cells:
            raise SystemExit("%s carries no sampled cells — REFUSING to fabricate a derived block" % args.out)
        pooled = d["anchor_envelope_body_free"]["pooled"]
        geom = d["body_geometry"]
        d["summary"] = summarise(cells, geom)
        d["★_paired_body_size_comparison"] = paired_body_size_comparison(cells, pooled, geom)
        d["cross_checks"]["replicates_the_committed_E3_acceptance"] = \
            crosscheck_replicates_committed_acceptance(cells)
        d["cross_checks"]["size_labels_match_the_coordinates"] = crosscheck_size_partition(geom)
        census = effector_arm_census()
        d["what_one_more_anchor_set_means"]["census"] = census
        d["verdict"] = verdict(d["summary"], pooled, required_distances(),
                               d["★_paired_body_size_comparison"],
                               d.get("★_interface_floor_ablation"))
        d["map_edits_required"] = map_edits_required(census, d["summary"])
        with open(args.out, "w") as fh:
            json.dump(d, fh, indent=1)
            fh.write("\n")
        with open(os.path.splitext(args.out)[0] + ".md", "w") as fh:
            fh.write(to_markdown(d))
        for k, v in d["cross_checks"].items():
            print("[xcheck] %s: %s" % (k, v.get("status")), flush=True)
        print("[tcip] refreshed derived blocks in %s from %d stored cells" % (args.out, len(cells)))
        return 0

    if args.only_interface_ablation:
        m3 = BS.load_paralogue(os.path.join(STRUCT_DIR, "nr4a3-opened.pdb"))
        field3 = G.SquaredDistanceField(m3["heavy_xyz"], cell=0.9, clamp=8.0)
        reactive = BS.load_reactive_map(UNIQUE_JSON, m3)
        poses = BS.build_pose_ensemble(m3, reactive, field3, 12, random.Random(BASIN_SEED))
        with open(REGISTRY) as fh:
            reg = json.load(fh)
        arms = {aid: BS.load_arm_from_registry(reg["arms"][aid])
                for aid in list(SINGLE_DOMAIN_ARMS) + list(MULTI_SUBUNIT_ARMS)}
        res = interface_floor_ablation(arms, poses, field3, n_samples=args.ablation_samples)
        with open(args.out) as fh:
            d = json.load(fh)
        d["★_interface_floor_ablation"] = res
        d["verdict"]["★_the_size_axis"]["★_root_cause"] = res["★_reading"]
        with open(args.out, "w") as fh:
            json.dump(d, fh, indent=1)
            fh.write("\n")
        with open(os.path.splitext(args.out)[0] + ".md", "w") as fh:
            fh.write(to_markdown(d))
        print(json.dumps({k: v for k, v in res.items() if k != "by_floor"}, indent=1), flush=True)
        return 0

    if args.only_e3_free_check:
        m3 = BS.load_paralogue(os.path.join(STRUCT_DIR, "nr4a3-opened.pdb"))
        field3 = G.SquaredDistanceField(m3["heavy_xyz"], cell=0.9, clamp=8.0)
        reactive = BS.load_reactive_map(UNIQUE_JSON, m3)
        poses = BS.build_pose_ensemble(m3, reactive, field3, 12, random.Random(BASIN_SEED))
        with open(REGISTRY) as fh:
            reg = json.load(fh)
        arms = {aid: BS.load_arm_from_registry(reg["arms"][aid])
                for aid in list(SINGLE_DOMAIN_ARMS) + list(MULTI_SUBUNIT_ARMS)}
        res = crosscheck_acceptance_is_e3_free(arms, poses, field3)
        with open(args.out) as fh:
            d = json.load(fh)
        d["cross_checks"]["acceptance_test_is_E3_free"] = res
        with open(args.out, "w") as fh:
            json.dump(d, fh, indent=1)
            fh.write("\n")
        with open(os.path.splitext(args.out)[0] + ".md", "w") as fh:
            fh.write(to_markdown(d))
        print(json.dumps(res, indent=1), flush=True)
        return 0

    d = build(samples=args.samples,
              arms_wanted=[a for a in args.arms.split(",") if a] or None,
              n_procs=args.procs)
    with open(args.out, "w") as fh:
        json.dump(d, fh, indent=1)
        fh.write("\n")
    with open(os.path.splitext(args.out)[0] + ".md", "w") as fh:
        fh.write(to_markdown(d))

    print(json.dumps(d["verdict"], indent=1)[:3000], flush=True)
    for k, v in d["cross_checks"].items():
        print("[xcheck] %s: %s" % (k, v.get("status")), flush=True)
    for r in d["refusals"]:
        print("[REFUSED] %s: %s" % (r.get("what"), r.get("reason")), flush=True)
    print("[tcip] wrote %s in %.1f s" % (args.out, d["runtime_s"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
