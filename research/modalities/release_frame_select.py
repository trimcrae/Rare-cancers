#!/usr/bin/env python3
"""Pure frame-selection logic for the NR4A3 docking/MM-GBSA receptor re-anchor (Step 0).

WHY. Every downstream docking / MM-GBSA / FEP / de-novo step needs a NR4A3 receptor conformation. Until
now that conformation was the most-druggable frame of the *biased* metadynamics trajectory — a frame
pulled open by the bias, not a thermally-real state. The unbiased "release" run showed the orthosteric
pocket is a *breathing / induced-fit* site: metastable (3/3 replicas held 5 ns) and druggable in ~24% of
UNBIASED frames (frac>=0.5 = 0.24, frac>=0.53 = 0.20, peak 0.842; static 0.495), at CV Rg ~0.737 nm. So
the right receptor is a *druggable unbiased release frame* (Rg near 0.737, fpocket >= D*), and because the
pocket is dynamic we keep a small druggable SUB-ENSEMBLE (a primary + alternates), not one static frame.

WHAT. This module is the pure decision: given per-frame records {rep, frame, rg, druggability} drawn from
the release trajectories, pick the primary receptor frame and a handful of alternates that span the
druggable sub-ensemble. It has no mdtraj/fpocket/numpy/IO dependency so it is unit-tested directly
(TESTING.md #3: the SageMaker job runs this tested code). The driver (nr4a3_release_druggable.py) supplies
the records (reusing the existing nr4a3-release-pocket druggability series where present, else fpocket) and
does the coordinate extraction once frames are chosen here.

Selection rule (documented so the receptor choice is reproducible and defensible):
  1. Keep only DRUGGABLE frames: druggability >= d_star (default 0.53, the calibrated drug-bound band).
     If none clear d_star, relax to the >=0.5 conventional cutoff and flag it. If still none, return empty
     (the driver then aborts loudly rather than silently anchoring to a non-druggable frame).
  2. PRIMARY = the druggable frame whose CV Rg is closest to target_rg (the unbiased mean of the druggable
     state, ~0.737 nm) — the most representative thermally-real druggable conformation, NOT the peak
     druggability (which is an extreme-value outlier, the red-team F2 caution).
  3. ALTERNATES = up to n_alt further druggable frames chosen to SPREAD across the druggable Rg range
     (farthest-point sampling seeded by the primary), so the sub-ensemble samples the breathing motion
     rather than near-duplicates of the primary. Ties / exhausted spread fall back to highest druggability.
"""


def _key(r):
    """Stable ordering key for a frame record (rep then frame index)."""
    return (int(r.get("rep", 0)), int(r["frame"]))


def select_receptor_ensemble(records, d_star=0.53, target_rg=0.737, n_alt=3, relax_to=0.5):
    """Choose the primary receptor frame + alternates from per-frame release records.

    records: list of dicts, each {"rep": int, "frame": int, "rg": float|None, "druggability": float|None}.
             Records missing druggability or rg are ignored for selection.
    Returns a dict:
      {"primary": <record>, "alternates": [<record>, ...], "d_star_used": float,
       "relaxed": bool, "n_druggable": int, "druggable": [<record sorted>], "reason": str}
    or {"primary": None, "alternates": [], ...} if no druggable frame exists at either threshold.
    """
    usable = [r for r in records
              if r.get("druggability") is not None and r.get("rg") is not None]
    relaxed = False
    thr = d_star
    druggable = [r for r in usable if r["druggability"] >= thr]
    if not druggable and relax_to is not None and relax_to < d_star:
        thr = relax_to
        relaxed = True
        druggable = [r for r in usable if r["druggability"] >= thr]

    base = {"d_star_used": thr, "relaxed": relaxed, "n_druggable": len(druggable),
            "n_usable": len(usable)}
    if not druggable:
        base.update({"primary": None, "alternates": [], "druggable": [],
                     "reason": (f"no release frame reached druggability >= {d_star} (nor the relaxed "
                                f"{relax_to}); receptor re-anchor cannot proceed on this trajectory set")})
        return base

    # Deterministic ordering for reproducibility.
    druggable = sorted(druggable, key=_key)

    # PRIMARY: closest CV Rg to target_rg (the representative druggable conformation). Tie-break: higher
    # druggability, then lower (rep, frame).
    primary = min(druggable,
                  key=lambda r: (abs(r["rg"] - target_rg), -r["druggability"], _key(r)))

    # ALTERNATES: farthest-point spread over CV Rg, seeded by the primary, so the sub-ensemble samples the
    # breathing range. If fewer than needed remain distinct, fall back to highest druggability.
    chosen = [primary]
    pool = [r for r in druggable if _key(r) != _key(primary)]
    while pool and len(chosen) - 1 < n_alt:
        nxt = max(pool, key=lambda r: (min(abs(r["rg"] - c["rg"]) for c in chosen),
                                       r["druggability"], -_key(r)[0], -_key(r)[1]))
        chosen.append(nxt)
        pool = [r for r in pool if _key(r) != _key(nxt)]

    base.update({
        "primary": primary,
        "alternates": chosen[1:],
        "druggable": druggable,
        "reason": (f"{len(druggable)} druggable frame(s) at threshold {thr}"
                   f"{' (relaxed from %.2f)' % d_star if relaxed else ''}; primary at Rg "
                   f"{primary['rg']:.3f} (target {target_rg}), {len(chosen) - 1} alternate(s) spanning "
                   f"the druggable Rg range"),
    })
    return base


def rg_span(records):
    """(min, max) CV Rg over records that have an rg; (None, None) if none. Convenience for reporting."""
    rgs = [r["rg"] for r in records if r.get("rg") is not None]
    return (min(rgs), max(rgs)) if rgs else (None, None)
