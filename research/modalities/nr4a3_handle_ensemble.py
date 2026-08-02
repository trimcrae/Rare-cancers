#!/usr/bin/env python3
"""IS THE CATEGORICAL CHEMISTRY AXIS A SINGLE POINT OF FAILURE? — C397 across a real NR4A3 ensemble.

WHAT THIS ANSWERS. The 12-pose basin search found that all **7** term-(a) meta-basins reach **C397 and only
C397**: neither C420 nor C559 is reached by any basin at the 12-atom practical linker gate. The program's
covalent-capture axis therefore rests on ONE residue evaluated in ONE static opened conformer, and two
quantities that decide it were single-frame numbers:

  * C397's solvent exposure -- RSA 0.395 in `nr4a3-opened.pdb`, quoted in nr4a3-program-map.md as the reason C397 is a
    usable handle and C559 (RSA 0.095) is not. A single frame gives no idea whether that is a robust property
    of the fold or a feature of one snapshot.
  * the exit-anchor-to-SG distances that drive the E3-INDEPENDENT term-(a) envelope (C397 opens at a 10-atom
    linker; C420 at 16; C559 at 20). Those are geometry of the same one frame.

Both are answerable for **$0** from evidence this repo already owns and has never used for this question:
`results/nr4a3-pocket-reharmonize/` holds **100 real NR4A3 conformers** -- 25 metadynamics frames and 75
unbiased release frames (3 replicas x 25) -- written by MDTraj from the same 254-residue construct, with the
same atom composition and the same residue numbering as `nr4a3-opened.pdb`. So the identical Shrake-Rupley
routine that produced the 0.395 can be run on each of them, and the identical E3-independent envelope can be
recomputed per conformer.

WHAT IS AND IS NOT ANSWERED HERE.
  * IS: the NR4A3-side distribution of exposure and of reach for all three unique cysteines, plus the unique
    lysines, over an ensemble that includes UNBIASED dynamics. Reported per ensemble, never pooled blindly,
    because the metadynamics frames are BIASED along the pocket-opening CV and their exposure statistics are
    not a Boltzmann sample.
  * IS NOT: anything about NR4A1/NR4A2 dynamics. Matched paralogue MD ensembles do not exist in this repo and
    would be a GPU spend. The categorical claim on the paralogue side is a SEQUENCE fact (NR4A1/NR4A2 carry no
    nucleophile at the aligned positions), which no amount of NR4A3 dynamics can weaken -- so the risk this
    script quantifies is one-sided: whether the NR4A3 handle is reliably *there*, not whether the paralogues
    might acquire one.
  * IS NOT: a claim that a reachable cysteine is a reactive one. Reach and exposure are necessary, not
    sufficient; intrinsic nucleophilicity, pKa and local electrostatics are untested here.

Pure stdlib, ~2 s per frame; the whole ensemble runs in a few minutes on one core.

Usage
    python nr4a3_handle_ensemble.py                 # all ensembles, writes the JSON beside this file
    python nr4a3_handle_ensemble.py --n-poses 12
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import basin_geom as G                      # noqa: E402
import nr4a_differential_atlas as ATLAS     # noqa: E402
import nr4a3_basin_search as B              # noqa: E402

ENSEMBLE_ROOT = os.path.join(REPO, "results", "nr4a3-pocket-reharmonize")
REFERENCE = os.path.join(REPO, "results", "nr4a3-matrix", "nr4a3-opened.pdb")
OUT = os.path.join(HERE, "nr4a3-handle-ensemble.json")

# The metadynamics frames are BIASED along the pocket-opening collective variable. They are kept because they
# are the conformers the druggability case was made on, but they are never pooled with the unbiased set -- a
# biased ensemble's exposure histogram is not a population estimate.
ENSEMBLES = {
    "metad_biased": ("metad", True),
    "release_rep0": ("release_rep0", False),
    "release_rep1": ("release_rep1", False),
    "release_rep2": ("release_rep2", False),
}


D_STAR = 0.53          # the pinned orthosteric-druggability threshold from pocket-reharmonize-summary.json


def druggability_by_frame(subdir):
    """Per-frame orthosteric druggability from the SAME reharmonized pocket analysis these conformers came
    from, keyed by the frame index embedded in each directory name (`fp_<index>_<hash>`).

    WHY THIS JOIN IS THE POINT. Term (a) needs a conformer to do TWO things at once: present the cryptic
    pocket the warhead occupies, AND put C397 within a linker's reach of a dockable E3 anchor. Reported
    separately, 'the pocket opens in X % of frames' and 'C397 is reachable in Y % of frames' say nothing about
    whether it is the SAME frames. If the two were anti-correlated, the term-(a) claim would be conditional on
    a conformational state that excludes the warhead binding at all -- and no marginal statistic would show
    it."""
    p = os.path.join(ENSEMBLE_ROOT, subdir, "pocket_analysis_summary.json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p))
    ser = ((d.get("druggability_timeseries") or {}).get("series")) or []
    return {int(s["frame"]): s.get("orthosteric_druggability") for s in ser if "frame" in s}


def frame_index(dirname):
    try:
        return int(dirname.split("_")[1])
    except (IndexError, ValueError):
        return None


def frame_paths(subdir):
    d = os.path.join(ENSEMBLE_ROOT, subdir)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name, "frame.pdb")
        if os.path.exists(p):
            out.append((name, p))
    return out


def quantiles(xs):
    if not xs:
        return {}
    s = sorted(xs)
    n = len(s)

    def q(f):
        if n == 1:
            return s[0]
        i = f * (n - 1)
        lo = int(math.floor(i))
        hi = min(lo + 1, n - 1)
        return s[lo] + (s[hi] - s[lo]) * (i - lo)
    return {"n": n, "min": round(s[0], 4), "p10": round(q(0.10), 4), "median": round(q(0.50), 4),
            "p90": round(q(0.90), 4), "max": round(s[-1], 4),
            "mean": round(sum(s) / n, 4),
            "sd": round(st.pstdev(s), 4) if n > 1 else 0.0}


def analyse_frame(path, handles, pocket_local, n_poses, seed, n_mc):
    """One conformer: exposure of every handle, plus the E3-independent term-(a) envelope recomputed on it."""
    residues, atoms = ATLAS.parse_pdb(path)
    sasa = ATLAS.shrake_rupley(atoms)
    rsa = ATLAS.residue_rsa(residues, sasa)

    heavy = [a for a in atoms if a["elem"] in B.HEAVY]
    by_res = {}
    for a in heavy:
        by_res.setdefault(a["resid"], []).append(a)
    field = G.SquaredDistanceField([(a["x"], a["y"], a["z"]) for a in heavy], cell=0.9, clamp=8.0)

    side = []
    for rid in pocket_local:
        for a in by_res.get(rid, []):
            if a["name"] not in B.BACKBONE:
                side.append((a["x"], a["y"], a["z"]))
    centroid = G.centroid(side)

    def xyz(rid, name):
        for a in by_res.get(rid, []):
            if a["name"] == name:
                return (a["x"], a["y"], a["z"])
        return None

    rec = {"frame": os.path.basename(os.path.dirname(path)), "handles": {}}
    cys_for_env = []
    for h in handles:
        p = xyz(h["local_resid"], h["atom"])
        row = {"rsa": round(rsa.get(h["local_resid"], 0.0), 4),
               "dist_to_pocket_centroid_A": (round(G.dist(p, centroid), 2) if p else None)}
        rec["handles"][h["label"]] = row
        if p and h["kind"] == "cys":
            cys_for_env.append({"uniprot_resid": h["uniprot_resid"], "xyz": p})

    # the pose ensemble is rebuilt PER CONFORMER: the pocket mouth moves with the pocket, so transplanting one
    # frame's anchors onto another frame would measure the wrong thing (and could place anchors inside atoms).
    rng = random.Random(seed)
    reactive = {"pocket_centroid": centroid}
    poses = B.build_pose_ensemble({"atoms_by_res": by_res}, reactive, field, n_poses, rng)
    rec["n_poses"] = len(poses)
    if poses and cys_for_env:
        env = B.term_a_feasibility_envelope(poses, cys_for_env, field, rng, n_mc=n_mc)
        for cid, e in env["per_cysteine"].items():
            rec["handles"].setdefault(cid, {})
            rec["handles"][cid]["shortest_linker_atoms"] = e["shortest_linker_with_any_feasible_anchor"]
            rec["handles"][cid]["min_exit_anchor_to_SG_A"] = e["dist_exit_anchor_to_SG_A"]["min"]
            rec["handles"][cid]["frac_anchor_space_at_gate_12"] = \
                e["by_linker_atoms"][12]["mean_fraction_of_anchor_space"]
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--unique-json", default=os.path.join(HERE, "nr4a-paralogue-unique-residues.json"))
    ap.add_argument("--n-poses", type=int, default=12)
    ap.add_argument("--n-mc", type=int, default=12000)
    ap.add_argument("--seed", type=int, default=20260725)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--limit", type=int, default=0, help="debug: only this many frames per ensemble")
    args = ap.parse_args(argv)

    u = json.load(open(args.unique_json))
    pocket_local = [x - B.UNIPROT_OFFSET for x in u["cryptic_pocket_uniprot"]]
    handles = []
    for entry, kind in ((u["nr4a3_unique_cysteines"], "cys"), (u["nr4a3_unique_lysines"], "lys")):
        for c in entry:
            g = c.get("geometry") or {}
            if "local_resid" not in g:
                continue
            handles.append({"label": ("C" if kind == "cys" else "K") + str(c["resnum"]),
                            "kind": kind, "uniprot_resid": c["resnum"],
                            "local_resid": g["local_resid"], "atom": g["reactive_atom"],
                            "reference_rsa": g["rsa"]})
    print(f"[hens] handles: {[h['label'] for h in handles]}", flush=True)

    todo = [("reference_opened_model", [("nr4a3-opened", REFERENCE)], False)]
    for name, (sub, biased) in ENSEMBLES.items():
        fps = frame_paths(sub)
        if args.limit:
            fps = fps[:args.limit]
        todo.append((name, fps, biased))

    res = {
        "_title": "NR4A3 categorical-handle exposure and reach across a real conformer ensemble",
        "_status": "DESIGN PRIORITISATION. Nothing here is a claim about binding, reactivity, degradation, "
                   "efficacy or safety.",
        "_method": "Identical Shrake-Rupley SASA / Tien-max-ASA RSA to the one that produced the committed "
                   "single-frame numbers, and the identical E3-independent term-(a) feasibility envelope, "
                   "recomputed independently on each conformer with its own pocket centroid and its own "
                   "warhead exit-vector pose ensemble.",
        "_limits": [
            "NR4A3 ONLY. No matched NR4A1/NR4A2 ensembles exist in this repo; building them is a GPU spend "
            "and is NOT done here. The paralogue side of the categorical claim is a SEQUENCE fact "
            "(no nucleophile at the aligned positions), which NR4A3 dynamics cannot weaken -- so the risk "
            "quantified here is one-sided.",
            "The metadynamics ensemble is BIASED along the pocket-opening CV; its statistics are reported "
            "separately and are NOT a Boltzmann population estimate. The unbiased release replicas are.",
            "Exposure and reach are NECESSARY, not sufficient: nothing here tests thiol pKa, intrinsic "
            "nucleophilicity, local electrostatics or electrophile promiscuity.",
            "The envelope is an E3-INDEPENDENT UPPER BOUND. A cysteine that opens at a given linker length "
            "here has not been shown reachable by any real recruiter at that length.",
            "The frames are LBD-only, as every model in this program is.",
        ],
        "parameters": {"n_poses": args.n_poses, "n_mc": args.n_mc, "seed": args.seed,
                       "linker_gate_atoms": B.PARAMS["linker_gate_atoms"],
                       "linker_report_atoms": B.PARAMS["linker_report_atoms"],
                       "electrophile_arm_A": B.PARAMS["electrophile_arm_A"]},
        "reference_single_frame": {h["label"]: h["reference_rsa"] for h in handles},
        "ensembles": {},
    }

    for name, fps, biased in todo:
        rows = []
        drug = druggability_by_frame(ENSEMBLES[name][0]) if name in ENSEMBLES else {}
        for i, (fid, path) in enumerate(fps):
            rows.append(analyse_frame(path, handles, pocket_local, args.n_poses, args.seed + i, args.n_mc))
            fi = frame_index(fid)
            rows[-1]["frame_index"] = fi
            rows[-1]["orthosteric_druggability"] = drug.get(fi)
            print(f"[hens] {name} {fid}: "
                  + " ".join(f"{k}(rsa={v.get('rsa')},L={v.get('shortest_linker_atoms')})"
                             for k, v in rows[-1]["handles"].items() if k.startswith("C")), flush=True)
        summary = {}
        for h in handles:
            lab = h["label"]
            summary[lab] = {
                "rsa": quantiles([r["handles"][lab]["rsa"] for r in rows if lab in r["handles"]]),
                "dist_to_pocket_centroid_A": quantiles(
                    [r["handles"][lab]["dist_to_pocket_centroid_A"] for r in rows
                     if r["handles"].get(lab, {}).get("dist_to_pocket_centroid_A") is not None]),
            }
            if h["kind"] == "cys":
                ls = [r["handles"][lab].get("shortest_linker_atoms") for r in rows if lab in r["handles"]]
                opened = [x for x in ls if x is not None]
                summary[lab]["shortest_linker_atoms"] = {
                    "n_frames": len(ls),
                    "n_frames_open_at_or_below_gate_12": sum(1 for x in opened if x <= 12),
                    "frac_frames_open_at_or_below_gate_12": (round(sum(1 for x in opened if x <= 12) / len(ls), 3)
                                                             if ls else None),
                    "n_frames_never_open_within_20": len(ls) - len(opened),
                    "distribution": quantiles([float(x) for x in opened]),
                    "_MC_CONVERGENCE": (
                        "⚠ `n_frames_open_at_or_below_gate_12` / `frac_...` ARE converged; "
                        "`n_frames_never_open_within_20` and `distribution` ARE NOT at the default n_mc and "
                        "must not be quoted as physical fractions. The envelope estimates a FRACTION OF "
                        "ANCHOR SPACE by Monte Carlo, and the exact three-ball rule admits a strictly smaller "
                        "set than the relaxed one it replaced, so the same budget resolves a rarer event. "
                        "Measured on one fixed frame over n_mc in {12000, 48000, 150000} x two seeds "
                        "(2026-07-25): C397 reads 10 atoms in every run and its feasible fraction at 12 atoms "
                        "is 0.041-0.064, never zero -- the GATE verdict is robust. But C559 reads CLOSED at "
                        "12000 on both seeds and 20 atoms at 48000 and above, and C420 reads 20 at one 12000 "
                        "draw and 16 everywhere else. Raise --n-mc before quoting anything past the gate."),
                }
                summary[lab]["min_exit_anchor_to_SG_A"] = quantiles(
                    [r["handles"][lab]["min_exit_anchor_to_SG_A"] for r in rows
                     if r["handles"].get(lab, {}).get("min_exit_anchor_to_SG_A") is not None])
        res["ensembles"][name] = {"biased": biased, "n_frames": len(rows),
                                  "summary": summary, "frames": rows}

    # pooled UNBIASED view -- the one that is a population estimate
    pooled = {}
    unb = [n for n, e in res["ensembles"].items() if n.startswith("release_rep")]
    for h in handles:
        lab = h["label"]
        vals = [f["handles"][lab]["rsa"] for n in unb for f in res["ensembles"][n]["frames"]
                if lab in f["handles"]]
        pooled[lab] = {"rsa": quantiles(vals)}
        if h["kind"] == "cys":
            ls = [f["handles"][lab].get("shortest_linker_atoms") for n in unb
                  for f in res["ensembles"][n]["frames"] if lab in f["handles"]]
            opened = [x for x in ls if x is not None]
            pooled[lab]["shortest_linker_atoms"] = {
                "n_frames": len(ls),
                "n_frames_open_at_or_below_gate_12": sum(1 for x in opened if x <= 12),
                "frac_frames_open_at_or_below_gate_12": (round(sum(1 for x in opened if x <= 12) / len(ls), 3)
                                                         if ls else None),
                "n_frames_never_open_within_20": len(ls) - len(opened),
                "distribution": quantiles([float(x) for x in opened]),
                "_MC_CONVERGENCE": (
                    "⚠ `n_frames_open_at_or_below_gate_12` / `frac_...` ARE converged; "
                    "`n_frames_never_open_within_20` and `distribution` ARE NOT at the default n_mc and "
                    "must not be quoted as physical fractions. The envelope estimates a FRACTION OF "
                    "ANCHOR SPACE by Monte Carlo, and the exact three-ball rule admits a strictly smaller "
                    "set than the relaxed one it replaced, so the same budget resolves a rarer event. "
                    "Measured on one fixed frame over n_mc in {12000, 48000, 150000} x two seeds "
                    "(2026-07-25): C397 reads 10 atoms in every run and its feasible fraction at 12 atoms "
                    "is 0.041-0.064, never zero -- the GATE verdict is robust. But C559 reads CLOSED at "
                    "12000 on both seeds and 20 atoms at 48000 and above, and C420 reads 20 at one 12000 "
                    "draw and 16 everywhere else. Raise --n-mc before quoting anything past the gate."),
            }
    res["pooled_unbiased"] = {"_what": "the 3 unbiased release replicas pooled; the metadynamics ensemble is "
                                       "deliberately excluded because it is biased along the pocket CV",
                              "n_replicas": len(unb), "summary": pooled}

    # ---- JOINT feasibility: is the pocket open in the SAME conformers where C397 is reachable? -----------
    joint = {}
    for scope, names in (("pooled_unbiased", unb), ("metad_biased", ["metad_biased"])):
        cells = {}
        for lab in ("C397", "C420", "C559"):
            n = a = b = ab = 0
            for nm in names:
                for f in res["ensembles"][nm]["frames"]:
                    d = f.get("orthosteric_druggability")
                    L = f["handles"].get(lab, {}).get("shortest_linker_atoms")
                    if d is None:
                        continue
                    n += 1
                    A = d >= D_STAR                                  # pocket druggable
                    Bq = (L is not None and L <= B.PARAMS["linker_gate_atoms"])   # cysteine at the gate
                    a += A
                    b += Bq
                    ab += (A and Bq)
            if n:
                cells[lab] = {
                    "n_frames": n,
                    "P_pocket_druggable": round(a / n, 3),
                    "P_reachable_at_gate": round(b / n, 3),
                    "P_BOTH": round(ab / n, 3),
                    "P_both_if_independent": round((a / n) * (b / n), 3),
                    "P_reachable_GIVEN_druggable": (round(ab / a, 3) if a else None),
                    "_reading": "P_BOTH materially below P_both_if_independent would mean the handle and the "
                                "pocket are anti-correlated, i.e. term (a) is conditional on a conformational "
                                "state that excludes the warhead. Equal or above means they are compatible.",
                }
        joint[scope] = cells
    res["joint_pocket_and_handle"] = {
        "d_star": D_STAR,
        "_what": "The mechanism needs ONE conformer to present the cryptic pocket AND put the cysteine within "
                 "linker reach. Marginal percentages cannot answer that; this is the joint distribution over "
                 "the same frames, with the independence product as the reference.",
        "_limits": ["Druggability comes from the reharmonized fpocket analysis at the pinned d* = 0.53, on the "
                    "same frames; nothing here re-derives it.",
                    "25 frames per replica is a small n for a joint statistic — read the direction and the "
                    "magnitude of any anti-correlation, not a precise probability."],
        "by_ensemble": joint,
    }
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"[hens] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
