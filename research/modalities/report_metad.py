#!/usr/bin/env python3
"""
Reduce a well-tempered-metadynamics free-energy profile F(Rg) (PLUMED `sum_hills` fes.dat) to the handful of
numbers the paper's cryptic-pocket §2.1-2.2 actually cites: the basin minimum, whether a *separate* opened
minimum exists (Gate 1), and the energetic cost from the basin to candidate opened-Rg states (Gate 3).

INPUT  fes.dat  — PLUMED sum_hills output: comment lines (`#! ...`) then columns `rg  file.free  der_rg`,
                  with LENGTH=nm, ENERGY=kJ/mol (the units the metad run declares). Pass the cumulative-run
                  file; the manifest's cumulative_ns is the sampling behind it.
OUTPUT dict / JSON: basin (rg*, F*), single-basin verdict, and ΔG(basin→Rg) at the druggable-frame Rg and the
                  open frontier, in kJ/mol AND kcal/mol.

HONEST-READING GUARDS baked in (this profile is a *single biased* F(Rg); the paper states these too):
  - F at the sampled EDGES is referenced to ~0 by sum_hills and coincides with the metad walls, so it is NOT a
    physical "closed"/"open" free energy — only the BASIN and the PROFILE SHAPE between well-sampled points are
    meaningful. `edge_caveat` is always emitted.
  - "single-basin" = no second local minimum on the OPENED side of the global min deeper than `min_prominence`
    kJ/mol; a bumpy plateau is not a basin. This is the Gate-1 (genuine two-state opening) test.

Pure/stdlib; unit-tested on the committed 60 ns profile. Not a network/GPU job — run locally or in CI.
"""
import json
import sys

KJ_PER_KCAL = 4.184


def parse_fes(path):
    """Read a PLUMED sum_hills fes.dat → [(rg_nm, F_kJ)]. Skips `#`/blank lines; takes cols 0,1."""
    pts = []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        f = s.split()
        try:
            pts.append((float(f[0]), float(f[1])))
        except (ValueError, IndexError):
            continue
    pts.sort()
    return pts


def _local_minima(pts, prominence):
    """Indices of local minima with at least `prominence` (kJ) rise to the higher neighbouring maximum on each
    side (a real well, not numerical wiggle). Endpoints excluded."""
    n = len(pts)
    out = []
    for i in range(1, n - 1):
        if pts[i][1] <= pts[i - 1][1] and pts[i][1] <= pts[i + 1][1]:
            left_max = max(p[1] for p in pts[:i]) if i else pts[i][1]
            right_max = max(p[1] for p in pts[i + 1:])
            if min(left_max, right_max) - pts[i][1] >= prominence:
                out.append(i)
    return out


def analyze(pts, druggable_rg=0.737, frontier_rg=1.06, min_prominence=5.0):
    """Reduce F(Rg) to the paper's cryptic-pocket numbers.
      druggable_rg: the unbiased release-run druggable frame Rg (§2.2); ΔG(basin→here) = Gate-3 accessibility.
      frontier_rg : the most-open metad-frontier Rg; ΔG(basin→here) = the (over-read) 'naive opening cost'.
      min_prominence (kJ): a second minimum must clear this to count as a *separate opened basin* (Gate 1)."""
    if len(pts) < 5:
        return {"_status": "too few points"}
    imin = min(range(len(pts)), key=lambda i: pts[i][1])
    rg_star, f_star = pts[imin]
    minima = _local_minima(pts, min_prominence)
    opened_minima = [i for i in minima if pts[i][0] > rg_star + 1e-9]

    def dg_to(target_rg):
        j = min(range(len(pts)), key=lambda i: abs(pts[i][0] - target_rg))
        kj = pts[j][1] - f_star
        return {"rg": round(pts[j][0], 3), "dG_kJ": round(kj, 1), "dG_kcal": round(kj / KJ_PER_KCAL, 1)}

    return {
        "basin_min": {"rg_nm": round(rg_star, 3), "F_kJ": round(f_star, 1)},
        "rg_range_nm": [round(pts[0][0], 3), round(pts[-1][0], 3)],
        "n_points": len(pts),
        "single_basin": len(opened_minima) == 0,
        "separate_opened_minima_rg": [round(pts[i][0], 3) for i in opened_minima],
        "gate1_verdict": ("weak (basin-breathing only: no separate opened minimum)"
                          if not opened_minima else "two-state (separate opened minimum present)"),
        "dG_basin_to_druggable_frame": dg_to(druggable_rg),
        "dG_basin_to_open_frontier": dg_to(frontier_rg),
        "edge_caveat": ("F at the sampled edges is sum_hills-referenced to ~0 and coincides with the metad "
                        "walls, so edge values are NOT physical closed/open free energies; only the basin and "
                        "the profile shape between well-sampled points are interpretable. Single biased F(Rg)."),
    }


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "fes.dat"
    res = analyze(parse_fes(path))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
