#!/usr/bin/env python3
"""
STEP 0 — re-anchor the NR4A3 docking/MM-GBSA receptor to a DRUGGABLE *UNBIASED RELEASE* frame.

WHY. Docking / MM-GBSA / FEP / de-novo all need a NR4A3 receptor conformation. Until now that was the
most-druggable frame of the *biased* metadynamics trajectory (nr4a3_warhead.extract_opened_conformer) — a
conformation pulled open by the metad bias, i.e. a biased-MD artifact frame, not a thermally-real state.
The unbiased "release" run (nr4a3_md_release.py) settled that the orthosteric pocket is a BREATHING /
induced-fit site: metastable (3/3 replicas held 5 ns, drift 0.025 nm) AND druggable in ~24% of UNBIASED
frames (frac>=0.5 = 0.24, frac>=0.53 = 0.20, peak 0.842; static 0.495), at CV Rg ~0.737 nm. So the correct
receptor is a *druggable unbiased release frame* (Rg near 0.737, fpocket >= D*), and because the pocket is
dynamic we keep a small druggable SUB-ENSEMBLE (primary + alternates) for downstream scoring against the
breathing motion, not one static frame.

WHAT. (1) Reuse the per-frame druggability already computed on release_rep0.dcd (nr4a3-release-pocket/
pocket_analysis_summary.json -> druggability_timeseries.series: {frame, orthosteric_druggability,
cv_rg_nm}) to build the candidate pool cheaply ("reuse, don't recompute"); fall back to a fresh fpocket
scan over the release trajectories if that summary is absent (FORCE_SCAN=1 forces the scan). (2) Choose the
primary receptor + alternates with the pure, unit-tested release_frame_select (primary = druggable frame
closest to target Rg; alternates spread over the druggable Rg range). (3) Run fpocket ONCE on each CHOSEN
frame to confirm druggability and read the orthosteric pocket's lining residues (the docking box), and
write each as a protein-only receptor PDB. (4) Emit a manifest tying every receptor to its rep/frame, Rg,
druggability, and box residues, so the matrix / MM-GBSA pipelines can re-anchor to it.

This is CPU work (a handful of fpocket calls + Rg over the release trajectory). No GPU, no new MD.

Inputs (mounted by the SageMaker submitter):
  RELEASE_DIR  (env, default /opt/ml/processing/input/release) : release_rep*.dcd
  STRUCTURE_DIR(env, default /opt/ml/processing/input/struct)  : nr4a3-lbd-solvated.pdb (topology)
  POCKET_DIR   (env, default /opt/ml/processing/input/pocket)  : pocket_analysis_summary.json (optional)
Output (env OUTPUT_DIR): nr4a3-release-druggable.json (manifest) + nr4a3-release-druggable.pdb (primary)
  + nr4a3-release-druggable-alt{k}.pdb (alternates) + a small Rg/druggability scatter plot.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

import release_frame_select as rfs
import pocket_tracking as pt   # harmonized, score-independent orthosteric-pocket tracking

LBD_FIRST = 373                               # AF2 LBD start (the trim used in nr4a3_md.py)
POCKET_FIRST, POCKET_LAST = 406, 534          # orthosteric lining span (nr4a3-degrader-design-spec.md)
POCKET5_LINING = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]  # fixed 10-residue lining set
D_STAR = float(os.environ.get("D_STAR", "0.53"))      # calibrated drug-bound band lower edge
TARGET_RG = float(os.environ.get("TARGET_RG", "0.737"))  # unbiased mean Rg of the druggable state
N_ALT = int(os.environ.get("N_ALT", "3"))             # alternates to keep (the breathing sub-ensemble)
N_SCAN_FRAMES = int(os.environ.get("N_SCAN_FRAMES", "25"))  # fpocket sample if we must scan (no summary)

RELEASE_DIR = os.environ.get("RELEASE_DIR", "/opt/ml/processing/input/release")
STRUCTURE_DIR = os.environ.get("STRUCTURE_DIR", "/opt/ml/processing/input/struct")
POCKET_DIR = os.environ.get("POCKET_DIR", "/opt/ml/processing/input/pocket")
OUT = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")


def _rep_index(path):
    """release_rep<k>.dcd -> k (0 if unparseable)."""
    base = os.path.basename(path)
    digits = "".join(ch for ch in base if ch.isdigit())
    return int(digits) if digits else 0


def _load_summary_records():
    """Reuse the existing release-pocket druggability series (computed on release_rep0.dcd) as the
    candidate pool. Returns (records, source_str) or ([], reason) if unavailable."""
    p = os.path.join(POCKET_DIR, "pocket_analysis_summary.json")
    if not os.path.exists(p):
        return [], f"no {p}"
    try:
        summ = json.load(open(p))
    except Exception as e:  # noqa: BLE001
        return [], f"unreadable summary: {e}"
    dts = summ.get("druggability_timeseries", {})
    series = dts.get("series", []) if dts.get("ran") else []
    recs = []
    for s in series:
        d = s.get("orthosteric_druggability")
        rg = s.get("cv_rg_nm")
        if d is not None and rg is not None:
            recs.append({"rep": 0, "frame": int(s["frame"]), "rg": float(rg), "druggability": float(d)})
    src = (f"reused {os.path.basename(p)} (trajectory {summ.get('trajectory')}, "
           f"{len(recs)} frames with druggability+Rg)")
    return recs, src


def _scan_records(dcds, top, np, md):
    """Fallback: fpocket-scan a sample of frames across the release replicas to build the candidate pool
    when the existing summary is missing. Heavier than the reuse path but still CPU/minutes."""
    import nr4a3_structure as ns
    from nr4a3_mdpocket import _cv_rg_series
    target_resseqs = None
    recs = []
    for dcd in dcds:
        rep = _rep_index(dcd)
        t = md.load(dcd, top=top)
        prot = t.atom_slice(t.topology.select("protein"))
        if target_resseqs is None:
            import residue_map as rm
            resseqs = [r.resSeq for r in prot.topology.residues]
            pos, _ = rm.resolve_positions(resseqs, range(POCKET_FIRST, POCKET_LAST + 1), LBD_FIRST)
            target_resseqs = {resseqs[i] for i in pos}
            lpos, _ = rm.resolve_positions(resseqs, POCKET5_LINING, LBD_FIRST)
            _scan_records.lining = {resseqs[i] for i in lpos}
        cv_rg = _cv_rg_series(prot, np)
        n = prot.n_frames
        sample = sorted({int(round(x)) for x in np.linspace(0, n - 1, min(n, N_SCAN_FRAMES))})
        print(f"  [scan] {os.path.basename(dcd)}: {n} frames, sampling {len(sample)}", flush=True)
        for fi in sample:
            drug, _lining = _fpocket_frame(prot, fi, target_resseqs, ns,
                                           lining_resseqs=getattr(_scan_records, "lining", None))
            recs.append({"rep": rep, "frame": fi,
                         "rg": (None if cv_rg is None else round(float(cv_rg[fi]), 4)),
                         "druggability": drug})
    return recs


def _ca_by_resseq_from_pdb(pdb_path):
    """{resSeq: (x,y,z)} CA coords (Angstrom) from a saved frame PDB (fpocket's own coordinates)."""
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


def _fpocket_frame(prot, fi, target_resseqs, ns, lining_resseqs=None):
    """fpocket on a single frame; return (druggability, sorted lining resSeqs) of the detected pocket
    that IS the orthosteric site. (None, []) on any failure (best-effort).

    POCKET_MATCH=harmonized accepts the site via the score-independent composite gate against the fixed
    lining set (`lining_resseqs`); otherwise LEGACY max-span-overlap (>=1 shared with `target_resseqs`)."""
    d = tempfile.mkdtemp(prefix=f"rd_{fi}_", dir=OUT)
    try:
        pdb = os.path.join(d, "frame.pdb")
        prot[fi].save_pdb(pdb)
        subprocess.run(["fpocket", "-f", pdb], check=True, capture_output=True, text=True, timeout=300)
        resids_by_num, info = ns.pocket_residues_by_number(os.path.join(d, "frame_out"), "frame")
        if pt.match_mode() == pt.HARMONIZED:
            ca = _ca_by_resseq_from_pdb(pdb)
            ref_lining = sorted(lining_resseqs) if lining_resseqs else sorted(target_resseqs)
            span = (min(target_resseqs), max(target_resseqs)) if target_resseqs else (0, 0)
            try:
                ref = pt.orthosteric_reference(ca, lining_residues=ref_lining, span=span)
            except ValueError:
                return None, []
            cands = [{"residues": sorted(int(r) for r in resids),
                      "druggability": info[num]["druggability"]}
                     for num, resids in resids_by_num.items()]
            hit = pt.match_pocket(cands, ref, ca_by_resnum=ca, **pt.match_params())
            if hit is None:
                return None, []
            return hit["druggability"], sorted(hit["residues"])
        best_num, best_ov = None, 0
        for num, resids in resids_by_num.items():
            ov = len(target_resseqs.intersection(resids))
            if ov > best_ov:
                best_num, best_ov = num, ov
        if best_num is None:
            return None, []
        return info[best_num]["druggability"], sorted(resids_by_num[best_num])
    except Exception as e:  # noqa: BLE001
        print(f"  frame {fi} fpocket skipped: {e}", file=sys.stderr)
        return None, []
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _extract_receptor(dcd, top, frame, out_pdb, target_resseqs, md, ns, lining_resseqs=None):
    """Load `dcd`, slice protein, save frame `frame` as a receptor PDB, and re-run fpocket on it to
    confirm druggability + read the orthosteric box residues. Returns a dict describing the receptor."""
    t = md.load(dcd, top=top)
    prot = t.atom_slice(t.topology.select("protein"))
    resseqs = [r.resSeq for r in prot.topology.residues]
    prot[frame].save_pdb(out_pdb)
    drug, lining = _fpocket_frame(prot, frame, target_resseqs, ns, lining_resseqs=lining_resseqs)
    return {"pdb": os.path.basename(out_pdb), "rep": _rep_index(dcd), "frame": int(frame),
            "confirmed_druggability": drug, "box_residues": lining,
            "resseq_range": [int(min(resseqs)), int(max(resseqs))]}


def main():
    import numpy as np
    import mdtraj as md
    import residue_map as rm
    import nr4a3_structure as ns

    os.makedirs(OUT, exist_ok=True)
    top = os.path.join(STRUCTURE_DIR, "nr4a3-lbd-solvated.pdb")
    if not os.path.exists(top):
        sys.exit(f"  ABORT: missing topology {top} (mount nr4a3-metad at STRUCTURE_DIR)")
    dcds = sorted(glob.glob(os.path.join(RELEASE_DIR, "release_rep*.dcd")), key=_rep_index)
    if not dcds:
        sys.exit(f"  ABORT: no release_rep*.dcd in {RELEASE_DIR} (mount nr4a3-release at RELEASE_DIR)")
    print(f"  topology={top}; release trajectories: {[os.path.basename(d) for d in dcds]}", flush=True)

    res = {"_note": "STEP 0 receptor re-anchor: a DRUGGABLE UNBIASED RELEASE sub-ensemble for NR4A3 "
                    "docking/MM-GBSA, replacing the biased-metad max-druggability frame. The orthosteric "
                    "pocket is a breathing/induced-fit site (release run: metastable 3/3, druggable ~24% of "
                    "unbiased frames at Rg ~0.737); dock/score against this sub-ensemble, not one frame.",
           "params": {"d_star": D_STAR, "target_rg": TARGET_RG, "n_alt": N_ALT},
           "topology": os.path.basename(top), "trajectories": [os.path.basename(d) for d in dcds]}

    # Candidate pool: reuse the existing release-pocket series, else scan.
    records, src = ([], "FORCE_SCAN set") if os.environ.get("FORCE_SCAN") else _load_summary_records()
    if not records:
        if not shutil.which("fpocket"):
            sys.exit("  ABORT: no reusable druggability summary and fpocket not on PATH for the scan")
        print(f"  candidate pool: {src} -> scanning release trajectories with fpocket", flush=True)
        records = _scan_records(dcds, top, np, md)
        res["candidate_source"] = "fresh fpocket scan over release trajectories"
    else:
        print(f"  candidate pool: {src}", flush=True)
        res["candidate_source"] = src
    rg_lo, rg_hi = rfs.rg_span(records)
    res["candidate_pool"] = {"n": len(records), "rg_min": rg_lo, "rg_max": rg_hi}

    sel = rfs.select_receptor_ensemble(records, d_star=D_STAR, target_rg=TARGET_RG, n_alt=N_ALT)
    res["selection"] = {k: sel[k] for k in ("d_star_used", "relaxed", "n_druggable", "n_usable", "reason")}
    if sel["primary"] is None:
        res["_status"] = "no druggable release frame — receptor re-anchor cannot proceed"
        _write(res)
        sys.exit(f"  ABORT: {sel['reason']}")

    # Map orthosteric target residues onto the trajectory numbering (for the pocket-overlap selection).
    t0 = md.load(dcds[0], top=top)
    prot0 = t0.atom_slice(t0.topology.select("protein"))
    resseqs0 = [r.resSeq for r in prot0.topology.residues]
    pos, numbering = rm.resolve_positions(resseqs0, range(POCKET_FIRST, POCKET_LAST + 1), LBD_FIRST)
    target_resseqs = {resseqs0[i] for i in pos}
    lpos, _ = rm.resolve_positions(resseqs0, POCKET5_LINING, LBD_FIRST)
    lining_resseqs = {resseqs0[i] for i in lpos}
    res["residue_numbering"] = numbering
    res["pocket_match"] = {"mode": pt.match_mode(), "fpocket_version": pt.resolved_fpocket_version(),
                           "match_params": pt.match_params() if pt.match_mode() == pt.HARMONIZED else None}
    # Both-denominator detection over the candidate pool (reviewer P0): detected = frames with a matched
    # orthosteric druggability; n_propagated = all candidate frames considered.
    pool_scores = [r["druggability"] for r in records if r.get("druggability") is not None]
    res["harmonized_detection"] = pt.detection_report(pool_scores, d_star=D_STAR,
                                                      n_propagated=len(records))

    if not shutil.which("fpocket"):
        sys.exit("  ABORT: fpocket not on PATH (needed to confirm + box the chosen receptor frames)")

    chosen = [("primary", sel["primary"], "nr4a3-release-druggable.pdb")]
    for i, alt in enumerate(sel["alternates"], 1):
        chosen.append((f"alt{i}", alt, f"nr4a3-release-druggable-alt{i}.pdb"))

    receptors = []
    by_rep = {}
    for role, rec, fname in chosen:
        rep = int(rec["rep"])
        dcd = next((d for d in dcds if _rep_index(d) == rep), dcds[0])
        info = _extract_receptor(dcd, top, rec["frame"], os.path.join(OUT, fname),
                                 target_resseqs, md, ns, lining_resseqs=lining_resseqs)
        info["role"] = role
        info["selection_rg"] = rec["rg"]
        info["selection_druggability"] = rec["druggability"]
        receptors.append(info)
        print(f"  [{role}] rep{rep} frame {rec['frame']}: Rg={rec['rg']} sel_drug={rec['druggability']} "
              f"confirmed_drug={info['confirmed_druggability']} box_res={len(info['box_residues'])} "
              f"-> {fname}", flush=True)
    res["receptors"] = receptors
    res["selection_primary_receptor"] = "nr4a3-release-druggable.pdb"

    # CONFIRM-FILTER the sub-ensemble. The candidate-pool druggability (reused from the older
    # nr4a3-release-pocket summary) and the fresh CONFIRMATION fpocket run can disagree — single-frame
    # fpocket pocket-detection is fragile and the two summaries may even use different fpocket builds. The
    # *confirmed* score (this run's fpocket, the same method we will box/dock on) governs. Downstream MUST
    # dock against this confirmed sub-ensemble, not every chosen frame.
    drug_sub = [r for r in receptors
                if r["confirmed_druggability"] is not None and r["confirmed_druggability"] >= D_STAR]
    dropped = [r for r in receptors if r not in drug_sub]
    drug_sub_sorted = sorted(drug_sub, key=lambda r: abs((r["selection_rg"] or 1e9) - TARGET_RG))
    res["druggable_subensemble"] = [r["pdb"] for r in drug_sub_sorted]
    # The receptor downstream docking should treat as primary = the confirmed-druggable frame closest to
    # target Rg (normally the selection primary, but promote an alternate if the primary failed confirmation).
    res["docking_primary_receptor"] = drug_sub_sorted[0]["pdb"] if drug_sub_sorted else None
    res["confirm_filter"] = {
        "d_star": D_STAR,
        "n_confirmed_druggable": len(drug_sub),
        "n_dropped": len(dropped),
        "dropped": [{"pdb": r["pdb"], "confirmed_druggability": r["confirmed_druggability"],
                     "selection_druggability": r["selection_druggability"]} for r in dropped],
        "note": ("Sub-ensemble filtered by CONFIRMED fpocket druggability >= D*. Frames whose reused-summary "
                 "druggability did not reproduce on re-extraction are dropped (e.g. a single-frame fpocket "
                 "pocket-detection / fpocket-build discrepancy). Dock/score against druggable_subensemble."),
    }
    res["_status"] = ("ok" if drug_sub else
                      "no chosen frame confirmed druggable (>= D*) on re-extraction — receptor re-anchor "
                      "produced no usable docking receptor; inspect candidate pool / rerun with FORCE_SCAN")
    _write(res)
    _plot(records, sel, np)
    if not drug_sub:
        print("  WARNING: no chosen frame confirmed druggable on re-extraction", file=sys.stderr)
    print(f"  DONE: docking primary={res['docking_primary_receptor']}; "
          f"druggable sub-ensemble={res['druggable_subensemble']} "
          f"({len(dropped)} dropped on confirm); manifest nr4a3-release-druggable.json", flush=True)


def _write(res):
    with open(os.path.join(OUT, "nr4a3-release-druggable.json"), "w") as fh:
        json.dump(res, fh, indent=2)


def _plot(records, sel, np):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        rg = [r["rg"] for r in records if r.get("rg") is not None and r.get("druggability") is not None]
        dr = [r["druggability"] for r in records if r.get("rg") is not None and r.get("druggability") is not None]
        plt.figure(figsize=(7, 4))
        plt.scatter(rg, dr, s=18, c="0.6", label="release frames")
        plt.axhline(sel["d_star_used"], color="r", ls="--", lw=0.7,
                    label=f"D*={sel['d_star_used']}")
        plt.axvline(TARGET_RG, color="b", ls=":", lw=0.7, label=f"target Rg {TARGET_RG}")
        if sel["primary"]:
            plt.scatter([sel["primary"]["rg"]], [sel["primary"]["druggability"]], s=90, c="g",
                        marker="*", label="primary receptor", zorder=5)
        for a in sel["alternates"]:
            plt.scatter([a["rg"]], [a["druggability"]], s=60, c="orange", marker="D", zorder=4)
        plt.xlabel("CV Rg (nm)")
        plt.ylabel("orthosteric-pocket fpocket druggability")
        plt.title("NR4A3 druggable release sub-ensemble (receptor re-anchor)")
        plt.ylim(0, 1)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, "nr4a3-release-druggable.png"), dpi=130)
    except Exception as e:  # noqa: BLE001 — plot is a nicety
        print(f"  plot skipped: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
