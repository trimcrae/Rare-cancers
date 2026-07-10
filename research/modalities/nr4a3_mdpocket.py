#!/usr/bin/env python3
"""
Cryptic-pocket analysis of the NR4A3 LBD MD trajectory (post-processing for GPU experiment #1).

The orthosteric (warhead-target) pocket is borderline-druggable in the static AF2 model (fpocket
0.495 — Pocket 5, residues 406-534; see ASSUMPTIONS.md), i.e. just under the conventional 0.5 cutoff.
This asks whether MD pushes it over that line, three ways:

  1. SASA of the orthosteric lining residues (406-534) per frame (mdtraj shrake_rupley) — a rise
     suggests the site widening.
  2. **Per-frame fpocket druggability** of the orthosteric pocket — the FEASIBILITY readout: does the
     static 0.495 score cross the druggable >=0.5 threshold at any frame? If breathing reliably pushes
     it over, the small-molecule orthosteric warhead is supported; if it instead collapses, the route
     weakens and the backups (protein binder / AF-2 surface / ASO) gain weight.
  3. (best-effort) mdpocket transient-pocket density across the trajectory.

Inputs (env INPUT_DIR, default /opt/ml/processing/input): nr4a3-lbd-solvated.pdb + nr4a3-lbd-md.dcd
(produced by nr4a3_md.py). Outputs (env OUTPUT_DIR, default /opt/ml/processing/output): a summary
JSON, the per-frame SASA + druggability series, plots, and any mdpocket grids.
"""
import json
import os
import shutil
import subprocess
import sys

import pocket_tracking as pt   # harmonized, score-independent orthosteric-pocket tracking

LBD_FIRST = 373                               # AF2 LBD start (the trim used in nr4a3_md.py)
POCKET_FIRST, POCKET_LAST = 406, 534          # orthosteric lining span (nr4a3-degrader-design-spec.md)
POCKET5_LINING = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]  # fixed 10-residue lining set
NS_PER_FRAME = 0.05                            # DCDReporter wrote every 25000 steps * 2 fs = 50 ps
N_FPOCKET_FRAMES = 25                         # frames sampled for the per-frame fpocket druggability
IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
OUT = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")
# Topology source. Defaults to INPUT_DIR (trajectory + solvated PDB co-located, e.g. nr4a3-md / nr4a3-metad),
# but STRUCTURE_DIR can point elsewhere so we can analyse a trajectory whose solvated PDB lives in a
# DIFFERENT S3 prefix — e.g. the unbiased release run (release_rep*.dcd in nr4a3-release, but the
# nr4a3-lbd-solvated.pdb topology in nr4a3-metad; the release MD was built from that same solvated PDB).
STRUCTURE_DIR = os.environ.get("STRUCTURE_DIR", IN)


def main():
    import numpy as np
    import mdtraj as md

    top = os.path.join(STRUCTURE_DIR, "nr4a3-lbd-solvated.pdb")
    # DCD_NAME lets the same analysis run on either trajectory: the plain MD (nr4a3-lbd-md.dcd,
    # default) or the metadynamics run (nr4a3-lbd-metad.dcd). Same 50 ps/frame stride either way.
    dcd = os.path.join(IN, os.environ.get("DCD_NAME", "nr4a3-lbd-md.dcd"))
    for p in (top, dcd):
        if not os.path.exists(p):
            sys.exit(f"  ABORT: missing input {p} (expected the MD outputs mounted at INPUT_DIR)")
    os.makedirs(OUT, exist_ok=True)

    print(f"  loading {dcd}", flush=True)
    t = md.load(dcd, top=top)
    prot = t.atom_slice(t.topology.select("protein"))      # strip water/ions
    print(f"  frames={t.n_frames} atoms={t.n_atoms} protein_atoms={prot.n_atoms}", flush=True)

    # Map Pocket-5 onto the trajectory residues via the unit-tested resolver (handles the solvated
    # PDB being renumbered from 1 vs. preserving AF2 numbering — see residue_map.py).
    import residue_map as rm
    prot_residues = list(prot.topology.residues)
    resseqs = [r.resSeq for r in prot_residues]
    pocket_pos, numbering = rm.resolve_positions(resseqs, range(POCKET_FIRST, POCKET_LAST + 1), LBD_FIRST)
    print(f"  residue numbering: {numbering} (resSeq {min(resseqs)}..{max(resseqs)}); "
          f"pocket residues matched: {len(pocket_pos)}", flush=True)
    if not pocket_pos:
        sys.exit(f"  ABORT: could not map Pocket-5 residues {POCKET_FIRST}-{POCKET_LAST} onto the "
                 f"{len(prot_residues)} protein residues (resSeq {min(resseqs)}..{max(resseqs)})")

    # Per-residue SASA, summed over the pocket-lining residues -> one value per frame (nm^2).
    sasa_res = md.shrake_rupley(prot, mode="residue")
    pocket_sasa = sasa_res[:, pocket_pos].sum(axis=1)
    np.save(os.path.join(OUT, "pocket_sasa_nm2.npy"), pocket_sasa)

    time_ns = np.arange(t.n_frames, dtype=float) * NS_PER_FRAME
    # NOTE: frame 0 is the first PRODUCTION frame (AFTER minimisation + 100 ps NVT/NPT equilibration),
    # NOT the raw static AF2 model. So "opening vs baseline" is relative to the equilibrated state; a
    # proper "opening beyond the collapsed static pocket" needs a separate static-model SASA reference
    # (ASSUMPTIONS.md #6). Reported as production-frame-0 baseline, labelled honestly.
    baseline = float(pocket_sasa[0])
    opening = pocket_sasa - baseline
    dcd_name = os.path.basename(dcd)
    biased = "metad" in dcd_name      # metadynamics frames are biased samples, not a free population
    summary = {
        "frames": int(t.n_frames),
        "ns_per_frame": NS_PER_FRAME,
        "trajectory": dcd_name,
        "biased_sampling": biased,
        "sampling_note": ("METADYNAMICS trajectory: frames are BIASED toward pocket opening, so "
                          "per-frame druggability shows whether an OPENED conformation reaches "
                          ">=0.5 (a structural feasibility readout), NOT an unbiased population or "
                          "free energy. Use fes.dat for the energetics." if biased else
                          "Unbiased MD: per-frame druggability reflects spontaneous breathing."),
        "pocket_residue_range": [POCKET_FIRST, POCKET_LAST],
        "residue_numbering": numbering,
        "pocket_residues_matched": len(pocket_pos),
        "pocket_sasa_nm2": {
            "baseline_production_frame0_post_equil": baseline,
            "min": float(pocket_sasa.min()),
            "max": float(pocket_sasa.max()),
            "mean": float(pocket_sasa.mean()),
            "std": float(pocket_sasa.std()),
        },
        "opening_vs_baseline_nm2": {
            "max_increase": float(opening.max()),
            "frac_frames_more_open": float((opening > 0).mean()),
        },
        "interpretation": (
            "max_increase is relative to the equilibrated production-frame-0 (NOT the static AF2 "
            "model). A sustained/transient rise well above thermal noise (std) suggests pocket "
            "opening during MD; a rigorous 'opens beyond the collapsed static pocket' claim needs a "
            "separate static-model SASA reference (ASSUMPTIONS.md #6)."
        ),
    }

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.figure(figsize=(8, 4))
        plt.plot(time_ns, pocket_sasa, lw=0.8)
        plt.axhline(baseline, color="k", ls="--", lw=0.7, label="production frame-0 (post-equil)")
        plt.xlabel("time (ns)")
        plt.ylabel("Pocket-5 SASA (nm$^2$)")
        plt.title(f"NR4A3 LBD Pocket-5 (res {POCKET_FIRST}-{POCKET_LAST}) SASA over MD")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, "pocket_sasa.png"), dpi=130)
    except Exception as e:  # noqa: BLE001 — plot is a nicety, don't fail the job on it
        print(f"  plot skipped: {e}", file=sys.stderr)

    # The feasibility readout: per-frame fpocket druggability of the orthosteric pocket.
    target_resseqs = {resseqs[i] for i in pocket_pos}
    # Fixed 10-residue lining set mapped to the trajectory numbering (score-independent site identity
    # for the harmonized matcher). resolve_positions handles resSeq-preserved vs renumbered-from-1.
    lining_pos, _ = rm.resolve_positions(resseqs, POCKET5_LINING, LBD_FIRST)
    lining_resseqs = {resseqs[i] for i in lining_pos}
    cv_rg_all = _cv_rg_series(prot, np)              # metad-CV Rg per frame (the fes.dat coordinate)
    summary["druggability_timeseries"] = druggability_timeseries(prot, target_resseqs, time_ns, np,
                                                                  cv_rg_all, lining_resseqs=lining_resseqs)
    summary["mdpocket"] = _mdpocket_best_effort(top, dcd)
    # Gate 3 energetics: the metadynamics free-energy profile F(Rg) (fes.dat, from plumed sum_hills) if
    # it was mounted alongside the trajectory. Reports the closed->open cost (the energetic accessibility
    # of the opened druggable state).
    summary["fes"] = read_fes(IN, np)
    # The cheaper question: among the frames that are ALREADY druggable, which has the lowest CV Rg
    # (least opening), and what does F(Rg) cost THERE? A partially-open druggable state may be far
    # cheaper than the fully-open edge that the naive closed->open cost reports.
    summary["lowest_cost_druggable"] = _lowest_cost_druggable(
        summary["druggability_timeseries"], IN, np)

    with open(os.path.join(OUT, "pocket_analysis_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print("  SUMMARY:", json.dumps(summary["pocket_sasa_nm2"]),
          json.dumps(summary["opening_vs_baseline_nm2"]), flush=True)
    dts = summary["druggability_timeseries"]
    if dts.get("ran"):
        print(f"  DRUGGABILITY over MD: max={dts.get('max_druggability')} "
              f"mean={dts.get('mean_druggability')} min={dts.get('min_druggability')} "
              f"frac>=0.5={dts.get('frac_frames_druggable_0.5')} "
              f"frac>=0.53={dts.get('frac_frames_druggable_0.53')} "
              f"crosses_0.5={dts.get('crosses_druggable_0.5')} (static 0.495)", flush=True)
    if summary.get("fes"):
        f = summary["fes"]
        print(f"  GATE3 FES: closed Rg={f.get('rg_closed_min')} -> open Rg={f.get('rg_open_min')}; "
              f"open cost={f.get('open_cost_kcal_mol')} kcal/mol, barrier={f.get('barrier_kcal_mol')} "
              f"kcal/mol", flush=True)
    lcd = summary.get("lowest_cost_druggable", {})
    if lcd.get("ran") and lcd.get("thr_0.5"):
        t = lcd["thr_0.5"]
        print(f"  CHEAPEST DRUGGABLE: druggable (>=0.5) already at CV Rg={t.get('lowest_druggable_rg_nm')} "
              f"nm (drug {t.get('druggability_there')}), F(Rg) cost there={t.get('cost_kcal_mol')} "
              f"kcal/mol (vs {(summary.get('fes') or {}).get('open_cost_kcal_mol')} at the fully-open edge)",
              flush=True)


def read_fes(input_dir, np):
    """Parse the metadynamics free-energy profile F(Rg) (plumed sum_hills 'fes.dat': col0=Rg nm,
    col1=free energy kJ/mol) and report the closed-basin minimum, the opened-state minimum (Rg well
    above the closed basin), the closed->open cost, and the intervening barrier. Best-effort: returns
    None if fes.dat is absent (e.g. analysing the plain MD) or unparseable."""
    p = os.path.join(input_dir, "fes.dat")
    if not os.path.exists(p):
        return None
    rg, fe = [], []
    for line in open(p):
        s = line.strip()
        if not s or s.startswith(("#", "@")):
            continue
        parts = s.split()
        try:
            rg.append(float(parts[0])); fe.append(float(parts[1]))
        except (ValueError, IndexError):
            continue
    if len(rg) < 5:
        return None
    rg = np.array(rg); fe = np.array(fe)
    fe = fe - fe.min()                                  # zero at the global (closed) minimum
    ci = int(fe.argmin()); rg_c = float(rg[ci])
    out = {"rg_closed_min": round(rg_c, 3), "n_points": len(rg),
           "note": "F(Rg) from plumed sum_hills; cost = F(open basin) - F(closed basin); barrier = peak "
                   "F between them. Gate 3 PASS if open cost <= ~5 kcal/mol (transiently accessible)."}
    open_mask = rg >= rg_c + 0.3                        # clearly opened (Rg >= closed + 0.3 nm)
    if open_mask.any():
        idxs = np.where(open_mask)[0]
        oi = int(idxs[int(np.argmin(fe[idxs]))])
        lo, hi = sorted((ci, oi))
        barrier = float(fe[lo:hi + 1].max())
        out.update({
            "rg_open_min": round(float(rg[oi]), 3),
            "open_cost_kJ_mol": round(float(fe[oi]), 2),
            "open_cost_kcal_mol": round(float(fe[oi]) / 4.184, 2),
            "barrier_kJ_mol": round(barrier, 2),
            "barrier_kcal_mol": round(barrier / 4.184, 2),
        })
    return out


def _cv_rg_series(prot, np):
    """metad-CV Rg (nm) per frame: Rg of the CA atoms of CV_RESIDUES (the same coordinate as fes.dat),
    resolved onto the trajectory's (possibly renumbered) residues. None on failure."""
    try:
        import residue_map as rm
        import nr4a3_metad as M
        resseqs = [r.resSeq for r in prot.topology.residues]
        positions, _ = rm.resolve_positions(resseqs, M.CV_RESIDUES, LBD_FIRST)
        residues = list(prot.topology.residues)
        idx = []
        for i in positions:
            ca = next((a.index for a in residues[i].atoms if a.name == "CA"), None)
            if ca is not None:
                idx.append(ca)
        if len(idx) < 3:
            return None
        sub = prot.xyz[:, idx, :]
        c = sub.mean(axis=1, keepdims=True)
        return np.sqrt(((sub - c) ** 2).sum(axis=2).mean(axis=1))
    except Exception as e:  # noqa: BLE001
        print(f"  cv_rg series skipped: {e}", file=sys.stderr)
        return None


def cost_at_rg(input_dir, rg_target, np):
    """F (kcal/mol, zeroed at global min) interpolated at rg_target from fes.dat; None if unavailable."""
    p = os.path.join(input_dir, "fes.dat")
    if not os.path.exists(p):
        return None
    rg, fe = [], []
    for line in open(p):
        s = line.strip()
        if not s or s.startswith(("#", "@")):
            continue
        parts = s.split()
        try:
            rg.append(float(parts[0])); fe.append(float(parts[1]))
        except (ValueError, IndexError):
            continue
    if len(rg) < 5:
        return None
    rg = np.array(rg); fe = np.array(fe); fe = fe - fe.min()
    order = rg.argsort()
    return round(float(np.interp(rg_target, rg[order], fe[order])) / 4.184, 2)


def _lowest_cost_druggable(dts, input_dir, np, thresholds=(0.5, 0.53)):
    """Among sampled frames already druggable (>= each threshold), the lowest CV Rg (least opening) and
    the F(Rg) cost there (kcal/mol) — i.e. is there a CHEAPER partially-open druggable state than the
    fully-open edge the naive closed->open cost reports?"""
    if not dts.get("ran"):
        return {"ran": False}
    rows = [s for s in dts.get("series", [])
            if s.get("orthosteric_druggability") is not None and s.get("cv_rg_nm") is not None]
    out = {"ran": True}
    for thr in thresholds:
        hit = [s for s in rows if s["orthosteric_druggability"] >= thr]
        if not hit:
            out[f"thr_{thr}"] = None
            continue
        lo = min(hit, key=lambda s: s["cv_rg_nm"])
        out[f"thr_{thr}"] = {"lowest_druggable_rg_nm": lo["cv_rg_nm"],
                             "druggability_there": lo["orthosteric_druggability"],
                             "cost_kcal_mol": cost_at_rg(input_dir, lo["cv_rg_nm"], np)}
    return out


def _ca_by_resseq_from_pdb(pdb_path):
    """{resSeq: (x,y,z)} CA coords (Angstrom) from a saved frame PDB — the SAME coordinates fpocket
    reads, so candidate/reference centroids are apples-to-apples. Keeps the first altloc."""
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


def druggability_timeseries(prot, target_resseqs, time_ns, np, cv_rg_all=None, lining_resseqs=None):
    """Per-frame fpocket druggability of the orthosteric pocket. Reuses the tested fpocket_lib mapping
    via nr4a3_structure. Best-effort: never crashes the SASA result. `target_resseqs` are resSeq values
    (trajectory numbering) of the lining SPAN; `lining_resseqs` are the fixed 10-residue lining set in
    the same numbering (used by the HARMONIZED matcher). `cv_rg_all` (optional, per-frame metad-CV Rg in
    nm) is attached so druggability can be correlated with the free-energy coordinate.

    Site identity: POCKET_MATCH=harmonized uses the score-independent composite gate against the fixed
    lining set; otherwise the LEGACY max-span-overlap (>=1 shared) selection. Both denominators are
    reported under 'harmonized_detection'."""
    if not shutil.which("fpocket"):
        return {"ran": False, "reason": "fpocket not on PATH"}
    import tempfile
    import nr4a3_structure as ns

    match_mode = pt.match_mode()
    mparams = pt.match_params()
    fpocket_version = pt.resolved_fpocket_version()
    ref_lining = set(lining_resseqs) if lining_resseqs else set(target_resseqs)
    n = prot.n_frames
    sample = sorted({int(round(x)) for x in np.linspace(0, n - 1, min(n, N_FPOCKET_FRAMES))})
    series = []
    for fi in sample:
        d = tempfile.mkdtemp(prefix=f"fp_{fi}_", dir=OUT)
        pdb = os.path.join(d, "frame.pdb")
        try:
            prot[fi].save_pdb(pdb)
            subprocess.run(["fpocket", "-f", pdb], check=True, capture_output=True, text=True,
                           timeout=300)
            resids_by_num, info = ns.pocket_residues_by_number(os.path.join(d, "frame_out"), "frame")
            match_meta = None
            if match_mode == pt.HARMONIZED:
                ca = _ca_by_resseq_from_pdb(pdb)
                span_lo = min(target_resseqs) if target_resseqs else 0
                span_hi = max(target_resseqs) if target_resseqs else 0
                try:
                    ref = pt.orthosteric_reference(ca, lining_residues=sorted(ref_lining),
                                                   span=(span_lo, span_hi))
                    cands = [{"residues": sorted(int(r) for r in resids),
                              "druggability": info[num]["druggability"]}
                             for num, resids in resids_by_num.items()]
                    hit = pt.match_pocket(cands, ref, ca_by_resnum=ca, **mparams)
                except ValueError:
                    hit = None                                # numbering miss -> no match this frame
                drug = hit["druggability"] if hit is not None else None
                best_ov = hit["_match"]["n_overlap"] if hit is not None else 0
                match_meta = hit["_match"] if hit is not None else None
            else:
                best_num, best_ov = None, 0
                for num, resids in resids_by_num.items():
                    ov = len(target_resseqs.intersection(resids))
                    if ov > best_ov:
                        best_num, best_ov = num, ov
                drug = info[best_num]["druggability"] if best_num is not None else None
            entry = {"frame": fi, "time_ns": round(float(time_ns[fi]), 3),
                     "orthosteric_druggability": drug, "overlap_residues": best_ov,
                     "cv_rg_nm": (None if cv_rg_all is None
                                  else round(float(cv_rg_all[fi]), 4))}
            if match_meta is not None:
                entry["match"] = match_meta
            # WHOLE-SURFACE (off-site) scan: the most druggable pocket this frame that does NOT overlap
            # the orthosteric Pocket-5 target residues — i.e. a DIFFERENT cavity. This is the question
            # the orthosteric-only readout above cannot answer: did the MD open another druggable pocket
            # somewhere else on the LBD surface? (Same fpocket call, no extra cost; residues are in the
            # trajectory's own numbering, identical to overlap_residues.)
            offsite = []
            for num, resids in resids_by_num.items():
                if target_resseqs.intersection(resids):
                    continue                              # overlaps the orthosteric site -> not off-site
                dv = info.get(num, {}).get("druggability")
                if dv is not None:
                    offsite.append((dv, sorted(int(r) for r in resids)))
            if offsite:
                offsite.sort(key=lambda t: t[0], reverse=True)
                dv, res0 = offsite[0]
                entry["offsite_best_druggability"] = dv
                entry["offsite_resid_range"] = [res0[0], res0[-1]]
                entry["offsite_lining_residues"] = res0
            series.append(entry)
        except Exception as e:  # noqa: BLE001 — best-effort per frame
            series.append({"frame": fi, "time_ns": round(float(time_ns[fi]), 3),
                           "error": str(e)[:200]})
        finally:
            shutil.rmtree(d, ignore_errors=True)

    drugs = [s["orthosteric_druggability"] for s in series
             if s.get("orthosteric_druggability") is not None]
    # HARMONIZED both-denominator detection (reviewer P0): n_propagated = ALL sampled frames, detected =
    # frames where a matched orthosteric cavity carried a druggability score.
    detection = pt.detection_report(drugs, d_star=0.53, n_propagated=len(sample))
    out = {"ran": True, "n_frames_sampled": len(sample), "series": series,
           "harmonized_detection": {"match_mode": match_mode, "fpocket_version": fpocket_version,
                                    "match_params": mparams if match_mode == pt.HARMONIZED else None,
                                    **detection},
           "fpocket_version": fpocket_version,
           "max_druggability": max(drugs) if drugs else None,
           "min_druggability": min(drugs) if drugs else None,
           "mean_druggability": round(float(np.mean(drugs)), 3) if drugs else None,
           # The HONEST headline metric (red-team: report the distribution, not the max): what fraction of
           # sampled frames clear the druggable >=0.5 bar, and the drug-bound band (>=0.53).
           "frac_frames_druggable_0.5": round(float(np.mean([d >= 0.5 for d in drugs])), 3) if drugs else None,
           "frac_frames_druggable_0.53": round(float(np.mean([d >= 0.53 for d in drugs])), 3) if drugs else None,
           "crosses_druggable_0.5": bool(any(d >= 0.5 for d in drugs)) if drugs else None,
           "interpretation": ("FEASIBILITY: the orthosteric pocket is borderline in the static model "
                              "(0.495, just under 0.5). Does breathing push it over the druggable "
                              ">=0.5 threshold at any sampled frame (supports the small-molecule "
                              "orthosteric warhead) or collapse it (weakens the route -> lean on the "
                              "designed protein binder, the AF-2 surface cavity, or the junction ASO)?")}
    # WHOLE-SURFACE (off-site) aggregation: is there a DIFFERENT druggable pocket than Pocket-5?
    off = [s for s in series if s.get("offsite_best_druggability") is not None]
    offdrugs = [s["offsite_best_druggability"] for s in off]
    top_off = sorted(off, key=lambda s: s["offsite_best_druggability"], reverse=True)[:5]
    out["offsite_scan"] = {
        "note": ("WHOLE-SURFACE control: the best transient pocket per frame that does NOT overlap the "
                 "orthosteric Pocket-5 target residues. Answers 'did the MD open a DIFFERENT druggable "
                 "pocket?'. A max_offsite_druggability >= 0.5 in a consistent residue span = a candidate "
                 "alternative site worth docking. Residue numbers are in the trajectory's own numbering."),
        "n_frames_with_offsite": len(off),
        "max_offsite_druggability": max(offdrugs) if offdrugs else None,
        "mean_offsite_druggability": round(float(np.mean(offdrugs)), 3) if offdrugs else None,
        "frac_frames_offsite_ge_0.5": round(float(np.mean([d >= 0.5 for d in offdrugs])), 3) if offdrugs else None,
        "top5_offsite": [{"frame": s["frame"], "druggability": s["offsite_best_druggability"],
                          "resid_range": s.get("offsite_resid_range"),
                          "lining_residues": s.get("offsite_lining_residues")} for s in top_off],
    }
    o = out["offsite_scan"]
    print(f"  OFFSITE (whole-surface) scan: max_offsite_drug={o['max_offsite_druggability']} "
          f"mean={o['mean_offsite_druggability']} frac>=0.5={o['frac_frames_offsite_ge_0.5']}; "
          f"top offsite (drug, resid_range): "
          f"{[(t['druggability'], t['resid_range']) for t in o['top5_offsite']]}", flush=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        pts = [(s["time_ns"], s["orthosteric_druggability"]) for s in series
               if s.get("orthosteric_druggability") is not None]
        if pts:
            xs, ys = zip(*pts)
            plt.figure(figsize=(8, 4))
            plt.plot(xs, ys, "o-", lw=0.8, ms=3)
            plt.axhline(0.5, color="r", ls="--", lw=0.7, label="druggable threshold 0.5")
            plt.axhline(0.495, color="k", ls=":", lw=0.7, label="static model 0.495")
            plt.xlabel("time (ns)"); plt.ylabel("orthosteric-pocket fpocket druggability")
            plt.title("NR4A3 orthosteric pocket druggability over MD")
            plt.ylim(0, 1); plt.legend(); plt.tight_layout()
            plt.savefig(os.path.join(OUT, "pocket_druggability.png"), dpi=130)
    except Exception as e:  # noqa: BLE001
        print(f"  druggability plot skipped: {e}", file=sys.stderr)
    return out


def _mdpocket_best_effort(top, dcd):
    """Run mdpocket if available; never fail the job on it (the SASA result stands alone)."""
    if not shutil.which("mdpocket"):
        return {"ran": False, "reason": "mdpocket binary not on PATH"}
    try:
        r = subprocess.run(
            ["mdpocket", "--trajectory_file", dcd, "--trajectory_format", "dcd", "-f", top],
            cwd=OUT, capture_output=True, text=True, timeout=3600)
        return {"ran": True, "returncode": r.returncode,
                "stdout_tail": r.stdout[-1500:], "stderr_tail": r.stderr[-1500:]}
    except Exception as e:  # noqa: BLE001
        return {"ran": False, "reason": str(e)}


if __name__ == "__main__":
    main()
