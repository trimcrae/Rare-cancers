#!/usr/bin/env python3
"""C04 — PARALOGUE-MATCHED CRYPTIC-POCKET DRUGGABILITY. The harmonized detector, pointed at the NR4A1 and
NR4A2 conformer ensembles that have been committed to this repo since 2026-07-26 and never scored.

WHY THIS EXISTS
---------------
`nr4a3-pocket-reharmonize-summary.json` has EIGHT rows and every one of them is NR4A3. The premise of the
entire non-covalent route — that the cryptic orthosteric pocket is itself a paralogue discriminator — has
therefore never been measured against a paralogue. `nr4a-paralogue-dynamics.json -> ensemble_census` records
`results/nr4a1-pocket-ensemble` and `results/nr4a2-pocket-ensemble` with 100 frames each in EXACTLY NR4A3's
subset structure (metad 25 + release_rep0/1/2 25 each), and those frames are committed. So the contrast is a
$0 CPU job on frame-matched data.

WHAT IS MATCHED, AND WHAT IS NOT
--------------------------------
* MATCHED: the frames (100 per species, identical subset structure, produced by one lane), the detector
  (`pocket_tracking`, score-INDEPENDENT site identity + fpocket scoring), the acceptance thresholds
  (`pocket_tracking.match_params()`), D* (`pocket_tracking.D_STAR`), and — because every species is scored in
  ONE process against ONE fpocket build — the fpocket binary itself.
* NOT matched to the COMMITTED NR4A3 table: that table records `fpocket_version: "4.0"`, and this run pins
  whatever the CI environment resolves (recorded per run). ⚠ THAT IS WHY NR4A3'S OWN 100 FRAMES ARE RE-SCORED
  HERE rather than quoting the committed rows: the contrast that carries the conclusion is the one computed
  inside this run, and the committed rows are used only as a REPRODUCTION CHECK, reported as such.
* The site definition is NR4A3's prespecified Pocket-5 lining set mapped onto each paralogue by the same
  BLOSUM62 Needleman-Wunsch construction `nr4a3_metad._resolve_target` uses to put the metadynamics CV on the
  homologous paralogue pocket — i.e. we ask "is NR4A3's site open in the paralogue", not "does the paralogue
  have any druggable cavity". Those are different questions and only the first is the route's premise.

WHAT A RESULT HERE LICENSES — AND WHAT IT DOES NOT
--------------------------------------------------
Licenses a paralogue-matched CONFORMATIONAL-SELECTION statement with no free energy in it: "the site that must
open to bind is detected at rate X and reaches D* at rate Y, on matched ensembles and one detector."
Does NOT license (a) dG_open — a detection fraction is not an opening penalty and must never be reported as
one; (b) evidence of ABSENCE — at these ensemble sizes a paralogue that never opens is weak evidence, so this
supports a RANKING, never a categorical exclusion; (c) any claim about binding, reactivity, degradation,
efficacy or safety.

REFUSALS ARE RECORDED, NOT SCORED (CLAUDE.md §4). A frame whose PDB cannot be read, whose numbering cannot be
mapped, or on which fpocket fails is counted in `refusals` with its reason and is EXCLUDED from n_propagated —
an absent reading is not a reading of absence, and a frame we could not read is not a frame with no pocket.

Usage
    python paralogue_pocket_contrast.py --species NR4A1,NR4A2,NR4A3          # needs fpocket on PATH
    python paralogue_pocket_contrast.py --limit 2                            # smoke: 2 frames per subset
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import nr4a3_basin_search as B                # noqa: E402  (PDB model loader + the NR4A3 offset)
import nr4a_paralogue_dynamics as PD          # noqa: E402  (construct_frame / homologous_pocket / wilson95)
import nr4a3_structure as NS                  # noqa: E402  (fpocket output -> {pocket_number: residues})
import pocket_tracking as pt                  # noqa: E402  (THE harmonized detector — not re-implemented)

SPECIES = ("NR4A3", "NR4A1", "NR4A2")
SUBSETS = ("metad", "release_rep0", "release_rep1", "release_rep2")
BIASED = {"metad"}
OUT = os.path.join(HERE, "paralogue-pocket-contrast.json")
COMMITTED_NR4A3 = os.path.join(HERE, "nr4a3-pocket-reharmonize-summary.json")


# ---------------------------------------------------------------------------------------------------------
# pure helpers
# ---------------------------------------------------------------------------------------------------------
def ca_by_resseq(pdb_path):
    """{resSeq: (x,y,z)} CA coords (Angstrom) from a frame PDB — the SAME reader
    `nr4a3_release_druggable._ca_by_resseq_from_pdb` uses, so the reference centroid is built identically."""
    ca = {}
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith("ATOM") or line[12:16].strip() != "CA":
                continue
            if line[16] not in (" ", "A"):
                continue
            try:
                ca[int(line[22:26])] = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
            except ValueError:
                continue
    return ca


def pool_detections(dets, d_star=pt.D_STAR):
    """Sum counts across detection dicts and RECOMPUTE the fractions (never average them). PURE.
    Same arithmetic as `nr4a3_pocket_reharmonize.pool_detection`, restated here only because that module's
    copy takes the reharmonize entry shape."""
    ds = [d for d in dets if d]
    if not ds:
        return None
    n_prop = sum(d.get("n_propagated") or 0 for d in ds)
    n_det = sum(d.get("n_detected") or 0 for d in ds)
    n_ge = sum(d.get("n_ge_dstar") or 0 for d in ds)
    return {"d_star": d_star, "n_propagated": n_prop, "n_detected": n_det, "n_ge_dstar": n_ge,
            "detection_fraction": (n_det / n_prop) if n_prop else None,
            "frac_ge_among_detected": (n_ge / n_det) if n_det else None,
            "frac_ge_among_propagated": (n_ge / n_prop) if n_prop else None}


def contrast_rows(by_species_subset):
    """Fold {species: {subset: detection}} into the flat table this artifact publishes. PURE."""
    rows = []
    for sp in SPECIES:
        per = by_species_subset.get(sp, {})
        for sub in SUBSETS:
            d = per.get(sub)
            if d:
                rows.append({"species": sp, "ensemble": sub, "biased": sub in BIASED, **d})
        pooled = pool_detections([per.get(s) for s in SUBSETS if s not in BIASED])
        if pooled:
            rows.append({"species": sp, "ensemble": "release_unbiased_pooled", "biased": False, **pooled})
    return rows


# ---------------------------------------------------------------------------------------------------------
# impure: fpocket on one frame, through the harmonized gate
# ---------------------------------------------------------------------------------------------------------
def fpocket_candidates(frame_pdb, workroot):
    """Run fpocket on ONE frame and return its candidate cavities as `pocket_tracking.match_pocket` wants
    them. Raises on any failure so the caller can record a REFUSAL rather than score a frame it could not
    read (CLAUDE.md §4: an absent reading is not a reading of absence)."""
    d = tempfile.mkdtemp(prefix="ppc_", dir=workroot)
    try:
        pdb = os.path.join(d, "frame.pdb")
        shutil.copyfile(frame_pdb, pdb)
        subprocess.run(["fpocket", "-f", pdb], check=True, capture_output=True, text=True, timeout=600)
        resids_by_num, info = NS.pocket_residues_by_number(os.path.join(d, "frame_out"), "frame")
        return [{"residues": sorted(int(r) for r in res),
                 "druggability": info[num]["druggability"], "pocket_number": num}
                for num, res in resids_by_num.items()]
    finally:
        shutil.rmtree(d, ignore_errors=True)


def score_frame(frame_pdb, species, seqs, ref, ref_pocket_local, workroot):
    """One frame -> (druggability_or_None, diagnostic). `druggability is None` means DETECTED-FAILED (the
    detector ran and no cavity cleared the gate); a raised exception means REFUSED (we could not read it)."""
    model = B.load_paralogue(frame_pdb)
    offset, pocket_local, missing = PD.construct_frame(model, species, seqs, ref, ref_pocket_local)
    if not pocket_local:
        raise ValueError("homologous pocket mapped to 0 residues")
    ca = ca_by_resseq(frame_pdb)
    span = (min(pocket_local), max(pocket_local))
    reference = pt.orthosteric_reference(ca, lining_residues=sorted(pocket_local), span=span)
    cands = fpocket_candidates(frame_pdb, workroot)
    hit = pt.match_pocket(cands, reference, ca_by_resnum=ca, **pt.match_params())
    diag = {"n_candidates": len(cands), "n_lining_mapped": len(pocket_local),
            "n_lining_unmapped": len(missing), "local_to_uniprot_offset": offset,
            "reference_lining_present": reference["n_lining_present"]}
    if hit is None:
        return None, {**diag, "matched": False}
    return hit.get("druggability"), {**diag, "matched": True, "match": hit.get("_match"),
                                     "pocket_number": hit.get("pocket_number")}


def frame_paths(species, subset):
    root = {"NR4A3": os.path.join(REPO, "results", "nr4a3-pocket-reharmonize"),
            "NR4A1": os.path.join(REPO, "results", "nr4a1-pocket-ensemble"),
            "NR4A2": os.path.join(REPO, "results", "nr4a2-pocket-ensemble")}[species]
    return sorted(glob.glob(os.path.join(root, subset, "*", "frame.pdb")))


def committed_nr4a3_rows():
    """The committed NR4A3 table, quoted ONLY as a reproduction check. Its one home stays
    `nr4a3-pocket-reharmonize-summary.json`; nothing is re-typed here."""
    if not os.path.exists(COMMITTED_NR4A3):
        return None
    d = json.load(open(COMMITTED_NR4A3))
    want = {"metad_frames": "metad", "release_rep0": "release_rep0", "release_rep1": "release_rep1",
            "release_rep2": "release_rep2", "release_unbiased_pooled": "release_unbiased_pooled"}
    out = {}
    for r in d.get("rows", []):
        k = want.get(r.get("ensemble"))
        if k:
            out[k] = {kk: r.get(kk) for kk in ("n_propagated", "n_detected", "detection_fraction",
                                               "n_ge_dstar", "frac_ge_among_detected",
                                               "frac_ge_among_propagated")}
    return {"_source": os.path.relpath(COMMITTED_NR4A3, REPO), "fpocket_version": d.get("fpocket_version"),
            "d_star": d.get("d_star"), "match_params": d.get("match_params"), "rows": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--species", default=",".join(SPECIES))
    ap.add_argument("--subsets", default=",".join(SUBSETS))
    ap.add_argument("--limit", type=int, default=0, help="smoke: cap frames per subset")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args(argv)

    t0 = time.time()
    species = [s for s in args.species.split(",") if s]
    subsets = [s for s in args.subsets.split(",") if s]
    workroot = tempfile.mkdtemp(prefix="ppc_root_")

    fp_version = pt.resolved_fpocket_version()
    try:
        probe = subprocess.run(["fpocket", "-h"], capture_output=True, text=True, timeout=60)
        fp_available = True
        fp_banner = ((probe.stdout or "") + (probe.stderr or "")).strip().splitlines()[:1]
    except Exception as ex:  # noqa: BLE001
        raise SystemExit(f"  ABORT: fpocket is not runnable ({ex}). This lane's whole content is the "
                         "detector's answer; running without it would emit a table of refusals wearing the "
                         "shape of a result.")

    seqs = json.load(open(PD.SEQ_CACHE))
    ref = B.load_paralogue(PD.STATIC_MODEL["NR4A3"])
    u = json.load(open(PD.UNIQUE_JSON))
    ref_pocket_local = [x - B.UNIPROT_OFFSET for x in u["cryptic_pocket_uniprot"]]

    per_frame, refusals = [], []
    by_species_subset = {}
    for sp in species:
        by_species_subset[sp] = {}
        for sub in subsets:
            paths = frame_paths(sp, sub)
            if args.limit:
                paths = paths[: args.limit]
            n_found = len(paths)
            scores, n_prop = [], 0
            for p in paths:
                tag = f"{sp}/{sub}/{os.path.basename(os.path.dirname(p))}"
                try:
                    drug, diag = score_frame(p, sp, seqs, ref, ref_pocket_local, workroot)
                except Exception as ex:  # noqa: BLE001
                    refusals.append({"frame": tag, "reason": f"{type(ex).__name__}: {ex}"})
                    print(f"  [ppc] REFUSED {tag}: {ex}", flush=True)
                    continue
                n_prop += 1
                per_frame.append({"frame": tag, "species": sp, "ensemble": sub,
                                  "druggability": drug, **diag})
                if drug is not None:
                    scores.append(drug)
            det = pt.detection_report(scores, d_star=pt.D_STAR, n_propagated=n_prop)
            det["n_frames_found"] = n_found
            det["n_refused"] = n_found - n_prop
            by_species_subset[sp][sub] = det
            print(f"  [ppc] {sp:>5} {sub:>13}: found={n_found} scored={n_prop} detected={det['n_detected']} "
                  f"detfrac={det['detection_fraction']} >=D*={det['n_ge_dstar']}", flush=True)

    rows = contrast_rows(by_species_subset)
    res = {
        "_title": "C04 — paralogue-matched cryptic-pocket druggability: the harmonized detector over the "
                  "committed NR4A1 / NR4A2 / NR4A3 conformer ensembles",
        "_status": "DESIGN PRIORITISATION / instrument reading. $0 CPU. Nothing here is a claim about "
                   "binding, reactivity, degradation, efficacy or safety.",
        "_what_this_measures": "Whether NR4A3's prespecified Pocket-5 site is DETECTED, and whether it "
                               "reaches D*, in NR4A1 and NR4A2 under the IDENTICAL harmonized fpocket "
                               "protocol, per matched subset, both denominators.",
        "_licenses": "A paralogue-matched conformational-selection RANKING statement with no free energy in "
                     "it.",
        "_does_not_license": [
            "dG_open — a detection fraction is not an opening penalty and must never be reported as one.",
            "Evidence of ABSENCE. At these ensemble sizes a paralogue that never opens is weak evidence; "
            "this supports a ranking, never a categorical exclusion.",
            "Any statement about binding, reactivity, degradation, selectivity in vivo, efficacy or safety.",
            "Anything about a cavity the paralogue may have ELSEWHERE. The site definition is NR4A3's "
            "Pocket-5 mapped by alignment, so a paralogue row of 0 means 'NR4A3's site did not open here', "
            "not 'this protein has no druggable cavity'.",
        ],
        "_generated": {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                       "et": time.strftime("%Y-%m-%d %I:%M %p ET", time.localtime(time.time() - 4 * 3600)),
                       "generator": "research/modalities/paralogue_pocket_contrast.py"},
        "detector": {
            "module": "research/modalities/pocket_tracking.py",
            "site_definition": "FIXED prespecified Pocket-5 lining set (score-independent), mapped onto each "
                               "species by BLOSUM62 Needleman-Wunsch — nr4a_paralogue_dynamics.homologous_pocket",
            "pocket5_lining_uniprot_nr4a3": u["cryptic_pocket_uniprot"],
            "match_params": pt.match_params(),
            "d_star": pt.D_STAR,
            "fpocket_version_resolved": fp_version,
            "fpocket_banner": fp_banner,
            "fpocket_available": fp_available,
            "⚠_version_note": "The committed NR4A3 table was produced under a DIFFERENT fpocket build "
                              "(see committed_nr4a3_reproduction_check.fpocket_version). That is exactly why "
                              "NR4A3's own frames are re-scored here: the contrast that carries the "
                              "conclusion is computed inside THIS run, under ONE build.",
        },
        "ensembles": {"subsets": list(SUBSETS), "biased_subsets": sorted(BIASED),
                      "roots": {sp: os.path.relpath(os.path.dirname(os.path.dirname(
                          (frame_paths(sp, SUBSETS[0]) or ["x/y/z"])[0])), REPO) for sp in species}},
        "rows": rows,
        "refusals": refusals,
        "n_refusals": len(refusals),
        "committed_nr4a3_reproduction_check": committed_nr4a3_rows(),
        "per_frame": per_frame,
        "runtime_s": round(time.time() - t0, 1),
    }
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=2)
    print(f"  [ppc] wrote {args.out} in {res['runtime_s']} s ({len(refusals)} refusals)", flush=True)
    return res


if __name__ == "__main__":
    main()
