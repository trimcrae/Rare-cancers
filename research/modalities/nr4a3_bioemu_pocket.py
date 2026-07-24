#!/usr/bin/env python3
"""
BioEmu cross-check scorer — run the EXACT harmonized orthosteric-pocket detection over a BioEmu-generated
NR4A3 LBD conformational ensemble, so the fraction-of-frames-druggable is directly comparable to the
metadynamics (0.68) and unbiased-release (pooled 0.587) numbers.

WHY (method-watch trigger, 2026-07-20, BioEmu v1.4.0). The cheap-generative-conformational-ensemble trigger
row's action (a): "re-grade the NR4A3 LBD cryptic-pocket ensemble at near-zero cost as a cross-check on the
metadynamics." BioEmu (Microsoft, Science 2025) emulates equilibrium ensembles from sequence on a single GPU
in minutes — an ORTHOGONAL generator (learned, not physics-based enhanced sampling). If it independently opens
the Pocket-5 cryptic site to a druggable state at a comparable frequency, that is an independent-method
corroboration of the cryptic-pocket claim. Integrity guardrail (same as every method-watch row): a cheap
ensemble is a hypothesis generator; this is a cross-check, NOT a replacement for the physics-based evidence,
and BioEmu's ability to sample rare cryptic-opening is itself a limitation to report honestly (see the
write-up), not to assume.

WHAT THIS MODULE DOES (pure CPU, no BioEmu dependency): given a directory of all-atom frame PDBs whose
residues are numbered in UniProt Q92570 numbering (so residues 406..534 are present — the BioEmu launcher
renumbers the 254-residue LBD frames from 1.. to 373..626 before calling this), it runs fpocket per frame,
matches the orthosteric Pocket-5 by the SCORE-INDEPENDENT composite gate against the fixed lining set, and
emits a `harmonized_detection` block in the SAME shape every other ensemble uses (pocket_tracking +
nr4a3_structure — the identical scorers). It is deliberately a thin driver: all scientific logic is the
already-unit-tested shared code, so this cross-check cannot silently diverge from the load-bearing pipeline.

Reuses: pocket_tracking (orthosteric_reference / match_pocket / detection_report / D_STAR / match_params),
nr4a3_structure.pocket_residues_by_number (data-derived file->pocket mapping). Mirrors _fpocket_frame() in
nr4a3_release_druggable.py exactly, operating on PDB files rather than an mdtraj trajectory.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pocket_tracking as pt
import nr4a3_structure as ns

# Fixed, prespecified orthosteric site (UniProt Q92570 numbering) — identical to the release/metad pipeline.
POCKET5_LINING = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]
POCKET5_SPAN = (406, 534)


def _ca_by_resseq_from_pdb(pdb_path):
    """{resSeq: (x,y,z)} CA coords (Angstrom) from a frame PDB — identical to nr4a3_release_druggable."""
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


def score_frame(pdb_path, workdir):
    """fpocket on one frame PDB → matched orthosteric druggability (or None if no cavity matches the
    fixed Pocket-5 gate / fpocket fails). Best-effort; mirrors _fpocket_frame(). `pdb_path` residues must
    be in UniProt numbering (406..534 present)."""
    d = tempfile.mkdtemp(prefix="be_", dir=workdir)
    try:
        local = os.path.join(d, "frame.pdb")
        shutil.copyfile(pdb_path, local)
        subprocess.run(["fpocket", "-f", local], check=True, capture_output=True, text=True, timeout=300)
        resids_by_num, info = ns.pocket_residues_by_number(os.path.join(d, "frame_out"), "frame")
        ca = _ca_by_resseq_from_pdb(local)
        try:
            ref = pt.orthosteric_reference(ca, lining_residues=sorted(POCKET5_LINING), span=POCKET5_SPAN)
        except ValueError:
            return None  # none of the reference lining residues present → numbering catastrophe for this frame
        cands = [{"residues": sorted(int(r) for r in resids),
                  "druggability": info[num]["druggability"]}
                 for num, resids in resids_by_num.items()]
        hit = pt.match_pocket(cands, ref, ca_by_resnum=ca, **pt.match_params())
        return None if hit is None else hit["druggability"]
    except Exception as e:  # noqa: BLE001 — best-effort per frame, exactly like the release scorer
        print(f"  frame {os.path.basename(pdb_path)} fpocket skipped: {e}", file=sys.stderr)
        return None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def score_ensemble(frame_dir, workdir=None):
    """Run harmonized detection over every *.pdb frame in `frame_dir`. Returns (detection_report, per_frame).

    detection_report has the standard both-denominator shape; per_frame lists (name, druggability|None).
    n_propagated = number of frames PROPAGATED (all frames, including un-matched / fpocket-empty)."""
    frames = sorted(glob.glob(os.path.join(frame_dir, "*.pdb")))
    if not frames:
        raise SystemExit(f"no frame PDBs found in {frame_dir}")
    wd = workdir or tempfile.mkdtemp(prefix="bioemu_pocket_")
    os.makedirs(wd, exist_ok=True)
    per_frame, detected_scores = [], []
    for i, f in enumerate(frames):
        drug = score_frame(f, wd)
        per_frame.append({"frame": os.path.basename(f), "druggability": drug})
        if drug is not None:
            detected_scores.append(drug)
        print(f"  [{i + 1}/{len(frames)}] {os.path.basename(f)}: druggability={drug}", flush=True)
    report = pt.detection_report(detected_scores, d_star=pt.D_STAR, n_propagated=len(frames))
    return report, per_frame


def main():
    ap = argparse.ArgumentParser(description="BioEmu ensemble → harmonized NR4A3 Pocket-5 detection cross-check")
    ap.add_argument("--frames", required=True, help="directory of all-atom frame PDBs (UniProt numbering)")
    ap.add_argument("--out", required=True, help="output result JSON path")
    ap.add_argument("--workdir", default=None, help="scratch dir for fpocket (default: system temp)")
    ap.add_argument("--meta", default="{}", help="JSON string of provenance metadata to embed (model/version/etc.)")
    args = ap.parse_args()

    # Force harmonized matching regardless of ambient env — this cross-check is only meaningful harmonized.
    os.environ["POCKET_MATCH_MODE"] = pt.HARMONIZED

    report, per_frame = score_ensemble(args.frames, args.workdir)
    try:
        meta = json.loads(args.meta)
    except json.JSONDecodeError:
        meta = {"_meta_parse_error": args.meta}

    result = {
        "_title": "NR4A3 LBD cryptic Pocket-5 detection over a BioEmu conformational ensemble (metadynamics cross-check)",
        "_method": ("BioEmu equilibrium-ensemble frames → fpocket → harmonized score-independent Pocket-5 match "
                    "(fixed lining set 406,407,410,411,412,481,484,485,531,534; jaccard>=0.25, frac_recovered>=0.30, "
                    "centroid<=8.0 A) → druggability vs D*=0.53. IDENTICAL scorers to the metad/release ensembles "
                    "(pocket_tracking + nr4a3_structure)."),
        "_comparators": {
            "metad_frames": {"frac_ge_among_propagated": 0.68, "n": "17/25"},
            "release_unbiased_pooled": {"frac_ge_among_propagated": 0.5867, "n": "44/75"},
            "8xtt_nmr": {"frac_ge_among_propagated": 0.15, "n": "3/20"},
            "af2_static": {"frac_ge_among_propagated": 0.0, "n": "0/1"},
        },
        "_integrity": ("Cross-check, NOT a replacement for the physics-based evidence. BioEmu is a learned "
                       "equilibrium-ensemble emulator; whether it samples rare cryptic-opening at the correct "
                       "frequency is a known open question — interpret concordance as corroboration of the "
                       "SITE/EXISTENCE, and any under-sampling as a limitation of the emulator, not evidence "
                       "against the pocket."),
        "meta": meta,
        "fpocket_version": pt.resolved_fpocket_version(),
        "match_params": pt.match_params(),
        "harmonized_detection": report,
        "per_frame": per_frame,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=2)
    d = report
    print("\n=== BioEmu cross-check (harmonized Pocket-5) ===")
    print(f"  frames propagated : {d['n_propagated']}")
    print(f"  site detected     : {d['n_detected']} ({d['detection_fraction']})")
    print(f"  >= D*=0.53        : {d['n_ge_dstar']}  "
          f"({d['frac_ge_among_propagated']} of all, {d['frac_ge_among_detected']} of detected)")
    print(f"  metad comparator  : 0.68 (17/25) | release pooled 0.587 (44/75)")
    print(f"  wrote {args.out}")


if __name__ == "__main__":
    main()
