"""
Pure geometry for the NR4A3 selectivity-handle "pocket-facing" check — no numpy / mdtraj / fpocket
imports, following the repo rule (TESTING.md #3): the geometry logic lives in a pure, dependency-free
module so it is unit-testable locally (no GPU/AWS/binaries) and the SageMaker job runs the *tested* code.

THE QUESTION. The 30 ns metadynamics opens the NR4A3 orthosteric pocket to fpocket druggability ~0.93
(Gate 2). But a druggable *cavity volume* is not the same as a *designable* pocket: the registered Gate-2
pass condition (nr4a3-druggability-prereg.md) also requires that the 7 NR4A3-vs-NR4A1/NR4A2 selectivity
handles (L406, T407, T410, R412, I484, I531, L534) stay pocket-facing in the opened, druggable frames —
not splayed outward as an opening artifact. If they point away, the selectivity-handle design spec (and
the warhead screen's handle-contact scoring) rests on sand. This module decides "pocket-facing" per
handle per frame from coordinates alone.

DEFINITION (rotamer/scale tolerant). A handle side chain is "pocket-facing" in a frame if its side-chain
heavy-atom centroid points, from the backbone CA, toward the cavity centroid: the CA->sidechain vector
has a positive component along the CA->cavity vector (angle < 90 deg, i.e. cos > 0). We also report a
signed `depth` = dist(CA, cavity) - dist(sidechain, cavity) (positive => side chain sits deeper toward
the cavity than the backbone, i.e. inward).
"""


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a):
    return _dot(a, a) ** 0.5


def centroid(points):
    """Centroid of a list of (x, y, z) points; None if empty."""
    pts = list(points)
    if not pts:
        return None
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n, sum(p[2] for p in pts) / n)


def facing(ca, sidechain_pts, cavity_center):
    """Is this residue's side chain pocket-facing?

    `ca`: residue CA coordinate (x, y, z).
    `sidechain_pts`: list of side-chain heavy-atom coordinates (excludes backbone N/CA/C/O and H).
    `cavity_center`: the cavity centroid to face toward.

    Returns a dict {facing: bool, cos: float, depth: float} or None if it cannot be decided
    (no side chain — e.g. glycine — or a degenerate zero-length vector)."""
    if ca is None or cavity_center is None:
        return None
    sc = centroid(sidechain_pts)
    if sc is None:
        return None  # no side chain (glycine) — undecidable, reported as None
    v_side = _sub(sc, ca)
    v_cav = _sub(cavity_center, ca)
    ns, nc = _norm(v_side), _norm(v_cav)
    if ns == 0.0 or nc == 0.0:
        return None
    cos = _dot(v_side, v_cav) / (ns * nc)
    depth = _norm(_sub(cavity_center, ca)) - _norm(_sub(cavity_center, sc))
    return {"facing": cos > 0.0, "cos": round(cos, 4), "depth": round(depth, 4)}


def summarize(frames, handle_ids, d_star=0.53, min_handles_facing=4):
    """Aggregate per-frame, per-handle facing into the Gate-2 handle-facing readout.

    `frames`: list of {"frame": int, "druggability": float|None, "facing": {handle_id: bool|None}}.
    `handle_ids`: the handle residue ids (the 7 selectivity handles).
    `d_star`: calibrated druggable threshold (Gate 0). Frames with druggability >= d_star are the
        "druggable" subset the registered condition is actually about.
    `min_handles_facing`: how many of the handles must face in for a frame to "keep the handles".

    CRITERION (pre-stated, reported with the numbers regardless of outcome): the registered Gate-2
    handle-facing sub-condition is CONFIRMED if a majority (>50%) of druggable frames keep at least
    `min_handles_facing` of the handles pocket-facing. INCONCLUSIVE if there are no druggable frames in
    the sample (e.g. fpocket unavailable) — the per-handle frac_facing_all is still reported."""
    n_handles = len(handle_ids)
    drug_frames = [f for f in frames
                   if f.get("druggability") is not None and f["druggability"] >= d_star]

    per_handle = {}
    for h in handle_ids:
        all_vals = [f["facing"].get(h) for f in frames]
        dr_vals = [f["facing"].get(h) for f in drug_frames]
        n_all = sum(1 for v in all_vals if v is not None)
        k_all = sum(1 for v in all_vals if v is True)
        n_dr = sum(1 for v in dr_vals if v is not None)
        k_dr = sum(1 for v in dr_vals if v is True)
        per_handle[h] = {
            "n_frames_resolved": n_all,
            "n_facing": k_all,
            "frac_facing_all": round(k_all / n_all, 3) if n_all else None,
            "n_druggable_resolved": n_dr,
            "n_facing_druggable": k_dr,
            "frac_facing_druggable": round(k_dr / n_dr, 3) if n_dr else None,
        }

    def n_facing(f):
        return sum(1 for h in handle_ids if f["facing"].get(h) is True)

    drug_counts = [n_facing(f) for f in drug_frames]
    frac_drug_keep = (sum(1 for c in drug_counts if c >= min_handles_facing) / len(drug_counts)
                      if drug_counts else None)
    mean_drug_facing = (sum(drug_counts) / len(drug_counts)) if drug_counts else None
    confirmed = bool(drug_counts) and frac_drug_keep is not None and frac_drug_keep > 0.5

    criterion = (f"Gate-2 handle-facing CONFIRMED if a majority (>50%) of druggable "
                 f"(fpocket >= D*={d_star}) frames keep >= {min_handles_facing} of {n_handles} "
                 f"selectivity handles pocket-facing.")
    if not drug_frames:
        verdict = ("INCONCLUSIVE — no druggable frames in the sample (or fpocket unavailable); "
                   "see per-handle frac_facing_all for the geometric-only signal.")
    elif confirmed:
        verdict = "CONFIRMED — the opened druggable pocket keeps the selectivity handles facing in."
    else:
        verdict = ("NOT CONFIRMED — handles splay outward in the druggable frames; the handle-based "
                   "selectivity spec (and the warhead handle-contact score) is not supported by the "
                   "opened ensemble.")

    return {
        "d_star": d_star,
        "min_handles_facing": min_handles_facing,
        "n_handles": n_handles,
        "n_frames": len(frames),
        "n_druggable_frames": len(drug_frames),
        "per_handle": per_handle,
        "mean_handles_facing_druggable": (round(mean_drug_facing, 2)
                                          if mean_drug_facing is not None else None),
        "frac_druggable_frames_keeping_handles": (round(frac_drug_keep, 3)
                                                  if frac_drug_keep is not None else None),
        "criterion": criterion,
        "verdict": verdict,
        "confirmed": confirmed,
    }
