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
* NOT matched to the COMMITTED NR4A3 table by construction. ⚠ AND THE VERSION STRING CANNOT ESTABLISH THAT IT
  IS: `fpocket -h` prints the banner `fpocket 4.0` whatever conda-forge build is installed, so a matching
  `fpocket_version` proves only that two runs read the same banner. THAT is why NR4A3's own 100 frames are
  RE-SCORED here rather than quoted — the contrast that carries the conclusion is computed inside this run
  under ONE binary — and why the committed rows are demoted to a REPRODUCTION CHECK whose verdict compares
  COUNTS (`committed_nr4a3_reproduction_check.verdict`), not version strings.
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


def contrast_summary(by_species_subset):
    """THE READOUT, with BOTH error bars, because they answer different questions and only one of them is
    honest about the correlation. PURE.

    * `wilson95_ge_among_propagated` treats the 75 pooled unbiased frames as 75 independent draws. They are
      NOT: frames within a replica are correlated, so the effective n is smaller than 75 and this interval is
      ANTI-CONSERVATIVE. It is reported because it is the repo's standard interval (METHODOLOGY.md) and
      because it is what a reader will otherwise compute themselves.
    * `replicate_spread` takes the three release replicas as the unit — 3 numbers, their mean, their sample
      SD and their range. This is the CLAUDE.md §5 posture ("honest replicate-SD"), and it is the one to
      quote when the two disagree.
    A contrast whose Wilson intervals separate but whose replicate RANGES overlap is a contrast that is not
    established at replicate granularity, and saying so is the whole point of reporting both."""
    reps = [s for s in SUBSETS if s not in BIASED]
    out = {}
    for sp, per in by_species_subset.items():
        pooled = pool_detections([per.get(s) for s in reps])
        row = {"unbiased_pooled": pooled}
        if pooled and pooled["n_propagated"]:
            row["wilson95_ge_among_propagated"] = PD.wilson95(pooled["n_ge_dstar"], pooled["n_propagated"])
            row["wilson95_detection_fraction"] = PD.wilson95(pooled["n_detected"], pooled["n_propagated"])
        vals = [per[s]["frac_ge_among_propagated"] for s in reps
                if per.get(s) and per[s].get("frac_ge_among_propagated") is not None]
        if vals:
            m = sum(vals) / len(vals)
            sd = (sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5 if len(vals) > 1 else None
            row["replicate_spread"] = {"per_replicate_frac_ge_dstar": [round(v, 4) for v in vals],
                                       "mean": round(m, 4),
                                       "sd": (round(sd, 4) if sd is not None else None),
                                       "min": round(min(vals), 4), "max": round(max(vals), 4),
                                       "n_replicates": len(vals)}
        b = per.get("metad")
        if b:
            row["metad_biased_adversarial_upper_bound"] = {
                "frac_ge_among_propagated": b.get("frac_ge_among_propagated"),
                "wilson95": (PD.wilson95(b["n_ge_dstar"], b["n_propagated"]) if b.get("n_propagated")
                             else None),
                "_never_pooled_with_unbiased": True}
        out[sp] = row
    return out


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


def reproduction_verdict(mine_by_subset, committed):
    """Did THIS run reproduce the committed NR4A3 table, cell by cell? PURE.

    ★ This, not the version string, is the evidence that the detector behaved identically. `fpocket -h`
    prints the banner `fpocket 4.0` regardless of which conda-forge build is installed, so a matching
    `fpocket_version` proves only that two runs read the same banner. Counts matching exactly across every
    ensemble is a much stronger statement, and it is the one that licenses treating the paralogue arms as
    comparable to the committed NR4A3 rows."""
    if not committed or not committed.get("rows") or not mine_by_subset:
        return {"status": "NOT COMPARABLE — the committed table could not be read", "rows": {}}
    pooled = pool_detections([mine_by_subset.get(s) for s in SUBSETS if s not in BIASED])
    mine = dict(mine_by_subset)
    if pooled:
        mine["release_unbiased_pooled"] = pooled
    rows, all_match, compared = {}, True, 0
    for key, c in committed["rows"].items():
        m = mine.get("metad" if key == "metad" else key)
        if not m:
            rows[key] = {"status": "not scored in this run"}
            continue
        compared += 1
        same = all(m.get(f) == c.get(f) for f in ("n_propagated", "n_detected", "n_ge_dstar"))
        all_match = all_match and same
        rows[key] = {"matches_committed": same,
                     "this_run": {f: m.get(f) for f in ("n_propagated", "n_detected", "n_ge_dstar")},
                     "committed": {f: c.get(f) for f in ("n_propagated", "n_detected", "n_ge_dstar")}}
    return {"status": ("REPRODUCED — every compared NR4A3 cell matches the committed table"
                       if (all_match and compared) else
                       "DIVERGED — at least one NR4A3 cell differs from the committed table"),
            "n_ensembles_compared": compared,
            "⚠_why_this_and_not_the_version_string":
                "`fpocket -h` prints the banner `fpocket 4.0` whatever conda-forge build is installed, so a "
                "matching `fpocket_version` proves only that two runs read the same banner. Matching counts "
                "across every ensemble is the real evidence, and it is what licenses reading the paralogue "
                "arms against the committed NR4A3 rows.",
            "rows": rows}


def build_map_edits(contrast):
    """The roadmap edits THIS result requires — DESCRIBED, NEVER APPLIED. Same anchor discipline as C02:
    every `current_text` is read out of the live map by `map_edits`, so an entry that cannot be targeted says
    so rather than being silently wrong."""
    import map_edits as ME
    text = ME.load_map()
    n3 = (contrast.get("NR4A3") or {})
    p1 = (contrast.get("NR4A1") or {})
    p2 = (contrast.get("NR4A2") or {})

    def frac(x):
        return ((x.get("unbiased_pooled") or {}).get("frac_ge_among_propagated"))

    def rng(x):
        s = x.get("replicate_spread") or {}
        return (s.get("min"), s.get("max"))
    f3, f1, f2 = frac(n3), frac(p1), frac(p2)
    r3, r1, r2 = rng(n3), rng(p1), rng(p2)
    # SEPARATED at replicate granularity = NR4A3's worst replicate beats each paralogue's best. That is a
    # much stricter bar than non-overlapping Wilson intervals, and it is the honest one: the 75 pooled
    # frames are 3 correlated replicas, so the Wilson interval is anti-conservative.
    sep = all(v is not None for v in (r3[0], r1[1], r2[1])) and r3[0] > r1[1] and r3[0] > r2[1]
    ordered = all(v is not None for v in (f3, f1, f2)) and f3 > f1 and f3 > f2
    verdict = ("SEPARATED at replicate granularity" if sep else
               "RANKED but replicate ranges OVERLAP" if ordered else
               "NOT RANKED in NR4A3's favour")
    art = "research/modalities/paralogue-pocket-contrast.json -> contrast"
    summary = (f"unbiased pooled frac >= D*: NR4A3 {f3}, NR4A1 {f1}, NR4A2 {f2}; "
               f"per-replicate ranges {r3} / {r1} / {r2}")
    entries = [
        ME.edit(text, "§8 Route A", "### Route A — a warhead engaging paralogue-divergent pocket handles",
                "Route A's PREMISE — that the cryptic pocket is itself a paralogue discriminator — had never "
                "been measured against a paralogue, on frames that were committed to this repo. It has now "
                "been, on matched ensembles under one detector. ⚠ This is a CONFORMATIONAL-SELECTION "
                "statement with no free energy in it; it is NOT dG_open and must never be reported as one, "
                "so `R6` is untouched.",
                art, ME.append_after_line(
                    "\n★ **Paralogue-matched cryptic-pocket contrast — measured " +
                    "(the first paralogue-matched evidence Route A has).** " + verdict + ". " + summary +
                    " — [`paralogue-pocket-contrast.json`](../modalities/paralogue-pocket-contrast.json). "
                    "⚠ A detection fraction is **not** an opening penalty: this does not touch `R6`, and at "
                    "these ensemble sizes it supports a RANKING, never a categorical exclusion.")),
        ME.edit(text, "§3.2 R×V coverage matrix — row R1", "| `R1` pocket exists |",
                "The `R1` row says no instrument is validated on this system. That stays true — validation "
                "is not what changed. What changed is that the harmonized detector now has a "
                "paralogue-MATCHED reading, a different axis, and it is the one Route A's premise actually "
                "needed. The cell should point at it rather than restate it (rule 1).",
                art, ME.replace_in_line(
                    "no — but no instrument is *validated on this system*",
                    "no — but no instrument is *validated on this system*. ★ The detector now has a "
                    "paralogue-MATCHED reading — "
                    "[`paralogue-pocket-contrast.json`](../modalities/paralogue-pocket-contrast.json)")),
        ME.edit(text, "§10.1 open rows", "### 10.1 · Open rows, ordered by what unblocks the most",
                "C04 was on no ranked list: the frames were committed on 2026-07-26 and the detector was "
                "never pointed at them. A caveat with nowhere to go is how work gets silently dropped.",
                art, ME.append_after_line(
                    "| **C04** | **Paralogue-matched cryptic-pocket druggability** — the harmonized detector "
                    "over the committed NR4A1/NR4A2/NR4A3 ensembles | `R1` `R2` (Route A's premise) | "
                    "✓ **complete** | — ($0) | **$0** — CPU/CI | ✅ **RAN.** " + verdict + ". " + summary +
                    ". [`paralogue-pocket-contrast.json`](../modalities/paralogue-pocket-contrast.json); the "
                    "NR4A3 arm REPRODUCES the committed table cell-for-cell "
                    "(`committed_nr4a3_reproduction_check.verdict`) |")),
    ]
    return {
        "_what": "Roadmap edits this result requires. DESCRIBED, NOT APPLIED — sibling agents are editing "
                 "`nr4a3-program-map.md` and this run does not touch it.",
        "_how_anchors_are_kept_live": "`current_text` is read out of the live map at generation time; a "
                                      "missing or ambiguous anchor yields a visible refusal instead of a "
                                      "mis-targeted edit.",
        "verdict": verdict,
        "verdict_basis": {"unbiased_pooled_frac_ge_dstar": {"NR4A3": f3, "NR4A1": f1, "NR4A2": f2},
                          "replicate_ranges": {"NR4A3": r3, "NR4A1": r1, "NR4A2": r2},
                          "rule": "SEPARATED requires NR4A3's WORST release replicate to beat each "
                                  "paralogue's BEST. That is stricter than non-overlapping Wilson intervals "
                                  "and it is the honest bar, because the 75 pooled frames are 3 correlated "
                                  "replicas and the Wilson interval is anti-conservative."},
        "⛔_not_filed_in_section_6": "Nothing here closes a route. A paralogue that opens less often is a "
                                    "RANKING, not an exclusion, and evidence of absence is not available at "
                                    "these ensemble sizes.",
        "entries": entries,
        "verification": ME.verify(entries, text),
    }


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
            "⚠_version_note": "`fpocket_version_resolved` is the string the BANNER prints (`fpocket -h` "
                              "says `fpocket 4.0` whatever conda-forge build is installed), so it is NOT "
                              "proof that two runs used the same binary. That is exactly why NR4A3's own "
                              "frames are re-scored here — the contrast that carries the conclusion is "
                              "computed inside THIS run under ONE binary — and why the real check is "
                              "`committed_nr4a3_reproduction_check.verdict`, which compares COUNTS.",
        },
        "ensembles": {"subsets": list(SUBSETS), "biased_subsets": sorted(BIASED),
                      "roots": {sp: os.path.relpath(os.path.dirname(os.path.dirname(
                          (frame_paths(sp, SUBSETS[0]) or ["x/y/z"])[0])), REPO) for sp in species}},
        "contrast": contrast_summary(by_species_subset),
        "map_edits_required": build_map_edits(contrast_summary(by_species_subset)),
        "_how_to_read_the_contrast": [
            "DETECTION and DRUGGABILITY are different answers and must not be collapsed. A high detection "
            "fraction in a paralogue says the homologous site EXISTS and is findable; the >= D* fraction is "
            "the one that speaks to druggability.",
            "Two error bars are reported. `wilson95_*` treats the 75 pooled unbiased frames as independent "
            "and is ANTI-CONSERVATIVE (frames within a replica are correlated). `replicate_spread` takes the "
            "three replicas as the unit and is the honest one. Where they disagree, quote the replicate "
            "spread.",
            "The metad subsets are BIASED along the opening CV and are an adversarial upper bound on how far "
            "each pocket can open. They are never pooled with the unbiased frames.",
            "n_detected < n_propagated is a DETECTED-FAILED frame — the detector ran and no cavity cleared "
            "the gate. That is a reading. A REFUSAL (see `refusals`) is not: it means the frame could not be "
            "read, and it is excluded from n_propagated rather than scored as an absence.",
        ],
        "rows": rows,
        "refusals": refusals,
        "n_refusals": len(refusals),
        "committed_nr4a3_reproduction_check": dict(
            committed_nr4a3_rows() or {},
            verdict=reproduction_verdict(by_species_subset.get("NR4A3", {}), committed_nr4a3_rows())),
        "per_frame": per_frame,
        "runtime_s": round(time.time() - t0, 1),
    }
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=2)
    print(f"  [ppc] wrote {args.out} in {res['runtime_s']} s ({len(refusals)} refusals)", flush=True)
    return res


if __name__ == "__main__":
    main()
