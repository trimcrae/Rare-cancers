#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — frozen R1-R4 readout kernels + GO/NO-GO verdict (prereg §4-5).

Pure-Python geometry (no numpy/MD deps) so the SCORING logic is unit-tested offline and identical on every leg.
The MD driver feeds these real trajectory frames (lists of (x,y,z) tuples, Å); here we only define the metrics
and the frozen thresholds.

  R1 interface_rmsd_stable   — heavy-atom RMSD of the E3∩target interface vs the start; stable if plateau < 4.0 Å
                               and contacts never decay to 0.
  R2 recruitment            — sustained interface contact count over > 50% of production frames -> "recruited".
  R3 lys_presentation       — min target-Lys-Nζ -> catalytic-proxy distance distribution (geometry only).
  R4 covnoncov_sensitivity  — does the covalent/noncovalent Δ FLIP the recruitment verdict?
  verdict                   — applies the frozen §5 GO/NO-GO across the panel's per-leg readouts.
"""
from __future__ import annotations

# Frozen thresholds (prereg §4). Do not move once a leg has run.
INTERFACE_RMSD_STABLE_A = 4.0        # R1: interface RMSD plateau below this = stable
CONTACT_CUTOFF_A = 4.5               # R2/R1: heavy-atom contact distance
RECRUITED_FRAME_FRACTION = 0.50      # R2: fraction of production frames with >0 interface contacts to be "recruited"


def _dist(a, b) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def contact_count(coords_a, coords_b, cutoff=CONTACT_CUTOFF_A) -> int:
    """Number of a-atom / b-atom pairs within `cutoff` Å (the interface contact metric). O(len_a*len_b)."""
    c2 = cutoff * cutoff
    n = 0
    for pa in coords_a:
        for pb in coords_b:
            if (pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2 + (pa[2] - pb[2]) ** 2 <= c2:
                n += 1
    return n


def rmsd(frame, ref) -> float:
    """Positional RMSD (no superposition — frames are pre-aligned to the E3 frame by the driver)."""
    if len(frame) != len(ref) or not frame:
        raise ValueError("rmsd: frame/ref length mismatch or empty")
    return (sum(_dist(f, r) ** 2 for f, r in zip(frame, ref)) / len(frame)) ** 0.5


def interface_rmsd_stable(interface_frames, ref, tail_fraction=0.5) -> dict:
    """R1: per-frame interface RMSD vs ref; 'stable' if the tail-average plateau < INTERFACE_RMSD_STABLE_A.
    `interface_frames` = list of frames, each a list of interface-atom (x,y,z)."""
    series = [rmsd(fr, ref) for fr in interface_frames]
    tail = series[max(0, int(len(series) * (1 - tail_fraction))):] or series
    plateau = sum(tail) / len(tail)
    return {"rmsd_series_mean": round(sum(series) / len(series), 3),
            "plateau_A": round(plateau, 3),
            "stable": plateau < INTERFACE_RMSD_STABLE_A}


def recruitment(per_frame_contacts) -> dict:
    """R2: 'recruited' if > RECRUITED_FRAME_FRACTION of frames have any interface contact. Also returns the
    mean contact count (a recruitment-strength proxy) for the cov-vs-noncov and cov-vs-C551A comparisons."""
    n = len(per_frame_contacts)
    if n == 0:
        raise ValueError("recruitment: no frames")
    frac = sum(1 for c in per_frame_contacts if c > 0) / n
    return {"frames": n, "frac_frames_in_contact": round(frac, 3),
            "mean_contacts": round(sum(per_frame_contacts) / n, 2),
            "recruited": frac > RECRUITED_FRAME_FRACTION}


def lys_presentation(lys_nz_coords_per_frame, catalytic_proxy) -> dict:
    """R3: distribution of the min target-Lys-Nζ -> catalytic-proxy distance across frames (geometry only)."""
    mins = [min(_dist(nz, catalytic_proxy) for nz in frame) for frame in lys_nz_coords_per_frame if frame]
    if not mins:
        return {"min_A": None, "median_A": None, "note": "no surface Lys found"}
    s = sorted(mins)
    return {"min_A": round(s[0], 2), "median_A": round(s[len(s) // 2], 2), "max_A": round(s[-1], 2)}


def covnoncov_sensitivity(cov_recruit: dict, noncov_recruit: dict) -> dict:
    """R4 (the crux): does removing the covalent tether FLIP the recruitment verdict? Small Δ + same verdict =>
    covalency does not swamp the ternary readout; a flip => it does."""
    flipped = cov_recruit["recruited"] != noncov_recruit["recruited"]
    return {"cov_recruited": cov_recruit["recruited"], "noncov_recruited": noncov_recruit["recruited"],
            "mean_contacts_cov": cov_recruit["mean_contacts"], "mean_contacts_noncov": noncov_recruit["mean_contacts"],
            "verdict_flipped": flipped,
            "covalency_swamps": flipped}


def panel_verdict(legs: dict) -> dict:
    """Apply the frozen §5 GO/NO-GO. `legs` maps leg-id -> its readout dict, expecting at least:
      cov_nr4a1{recruitment, interface}, noncov_nr4a1{recruitment}, warhead_only{recruitment},
      recruiter_epimer{recruitment}, cov_c551a{recruitment}, sensitivity{covalency_swamps}.
    Returns {go: bool, reasons: [...]} — every failing criterion is named."""
    reasons, ok = [], True

    def need(cond, msg):
        nonlocal ok
        if not cond:
            ok = False
            reasons.append(msg)

    cov = legs.get("cov_nr4a1", {})
    noncov = legs.get("noncov_nr4a1", {})
    sens = legs.get("sensitivity", {})
    # 1 assembles + stable
    need(cov.get("interface", {}).get("stable") is True, "cov_nr4a1 interface not stable (R1)")
    # 2 covalency doesn't swamp
    need(cov.get("recruitment", {}).get("recruited") is True, "cov_nr4a1 not recruited (R2)")
    need(noncov.get("recruitment", {}).get("recruited") is True, "noncov_nr4a1 not recruited (R2)")
    need(sens.get("covalency_swamps") is False, "covalency SWAMPS the signal — R4 verdict flipped")
    # 3 controls behave
    need(legs.get("warhead_only", {}).get("recruitment", {}).get("recruited") is False,
         "warhead_only recruited despite no E3 moiety — readout artifact")
    need(legs.get("recruiter_epimer", {}).get("recruitment", {}).get("recruited") is False,
         "inactive epimer engaged VHL — negative control failed")
    c551a = legs.get("cov_c551a", {}).get("recruitment", {}).get("mean_contacts")
    cov_mc = cov.get("recruitment", {}).get("mean_contacts")
    if c551a is not None and cov_mc is not None:
        need(c551a < cov_mc, "cov_c551a not weaker than cov_nr4a1 — covalent engagement not demonstrated")
    return {"go": ok, "reasons": reasons or ["all frozen §5 criteria met"]}
