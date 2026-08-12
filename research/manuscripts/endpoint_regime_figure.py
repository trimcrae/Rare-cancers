#!/usr/bin/env python3
"""Figure 1 -- the regime map, drawn. ($0, stdlib, no plotting library)

WHY A HAND-BUILT SVG. The argument is a two-dimensional one and reads badly as a table. matplotlib
is not available in this sandbox and adding it would make the figure unreproducible for anyone
without it, so the SVG is emitted directly. It is deterministic, diffable, and re-derives under
--check like every other artifact here.

WHAT IS DRAWN. The horizontal axis is the sample size a disease actually accrues (log scale,
ClinicalTrials.gov ACTUAL enrolment). The vertical axis is its median objective-response rate. The
two curves are the contours computed in endpoint_regime_map.py:

  the zero-event contour  -- left of it, a trial has better than a one-in-ten chance of observing no
                             responses at all even when the agent works at the observed rate
  the design contour      -- left of it, the trial is smaller than an exact single-stage design
                             against a 5% null requires

A disease plotted to the LEFT of a curve is inside that failure regime. Nothing is shaded as a
"bad" region, because a coordinate is not a verdict on a disease or on a drug.

Usage:
  python3 research/manuscripts/endpoint_regime_figure.py           # regenerate
  python3 research/manuscripts/endpoint_regime_figure.py --check   # verify the committed figure
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from endpoint_regime_map import (  # noqa: E402
    DESIGN_NULL, NO_DESIGN, n_for_90pct_chance_of_one_event, required_n_against_null)

MAP = os.path.join(HERE, "endpoint", "endpoint-regime-map.json")
OUT = os.path.join(HERE, "endpoint", "endpoint-regime-map.svg")
OUT_REL = "research/manuscripts/endpoint/endpoint-regime-map.svg"

W, H = 900, 560
L, R, T, B = 88, 240, 46, 64          # margins; the right margin holds the legend
X0, X1 = 3.0, 1000.0                   # enrolment, log scale
Y0, Y1 = 0.0, 60.0                     # objective response, percent


def sx(n):
    n = min(max(n, X0), X1)
    return L + (math.log10(n) - math.log10(X0)) / (math.log10(X1) - math.log10(X0)) * (W - L - R)


def sy(p):
    p = min(max(p, Y0), Y1)
    return H - B - (p - Y0) / (Y1 - Y0) * (H - B - T)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def contour_path(fn):
    """Trace a contour as (required n, response rate) over a fine grid of rates."""
    pts = []
    p = 1.0
    while p <= 60.0:
        n = fn(p / 100.0)
        if isinstance(n, (int, float)) and n and n <= X1:
            pts.append((sx(n), sy(p)))
        p += 0.5
    return pts


def polyline(pts, stroke, dash=None, width=2.0):
    if not pts:
        return ""
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{d}" fill="none" stroke="{stroke}" '
            f'stroke-width="{width}"{dash_attr} stroke-linejoin="round"/>')


def build():
    with open(MAP) as fh:
        rm = json.load(fh)
    coords = rm["G3_disease_coordinates"]["coordinates"]
    emc = rm["G5_emc_as_the_worked_extreme"]

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    # ---- grid and axes -----------------------------------------------------------------
    for n in (3, 10, 30, 100, 300, 1000):
        x = sx(n)
        out.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{H-B}" stroke="#e8e8e8"/>')
        out.append(f'<text x="{x:.1f}" y="{H-B+18}" font-size="12" fill="#444" '
                   f'text-anchor="middle">{n}</text>')
    for p in range(0, 61, 10):
        y = sy(p)
        out.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#e8e8e8"/>')
        out.append(f'<text x="{L-10}" y="{y+4:.1f}" font-size="12" fill="#444" '
                   f'text-anchor="end">{p}%</text>')
    out.append(f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#333"/>')
    out.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#333"/>')
    out.append(f'<text x="{(L+W-R)/2:.0f}" y="{H-18}" font-size="13" fill="#222" '
               f'text-anchor="middle">Median actual enrolment (log scale)</text>')
    out.append(f'<text x="20" y="{(T+H-B)/2:.0f}" font-size="13" fill="#222" '
               f'text-anchor="middle" transform="rotate(-90 20 {(T+H-B)/2:.0f})">'
               f'Median objective response</text>')

    # ---- contours ----------------------------------------------------------------------
    out.append(polyline(contour_path(n_for_90pct_chance_of_one_event), "#c0392b"))
    design_pts = contour_path(
        lambda p: None if required_n_against_null(p) in (None, NO_DESIGN)
        else required_n_against_null(p))
    out.append(polyline(design_pts, "#2c3e50", dash="6,4"))

    # ---- disease coordinates -----------------------------------------------------------
    for c in coords:
        n, p = c.get("median_actual_enrolment"), c.get("median_objective_response_pct")
        if n is None or p is None:
            continue
        below = c.get("median_trial_is_below_the_design_contour")
        fill = "#c0392b" if below else "#7f8c8d"
        out.append(f'<circle cx="{sx(n):.1f}" cy="{sy(p):.1f}" r="4" fill="{fill}" '
                   f'fill-opacity="0.75"><title>{esc(c["condition"])} — n={n}, '
                   f'{p}%</title></circle>')

    # ---- the worked case ---------------------------------------------------------------
    emc_p = emc["objective_response_pct"]
    emc_n = 22
    ex, ey = sx(emc_n), sy(emc_p)
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="6.5" fill="none" stroke="#111" '
               f'stroke-width="2"/>')
    out.append(f'<line x1="{ex+9:.1f}" y1="{ey:.1f}" x2="{ex+34:.1f}" y2="{ey-16:.1f}" '
               f'stroke="#111" stroke-width="1"/>')
    out.append(f'<text x="{ex+37:.1f}" y="{ey-16:.1f}" font-size="12" fill="#111">'
               f'EMC (n=22, {emc_p}%)</text>')

    # ---- legend ------------------------------------------------------------------------
    lx, ly = W - R + 14, T + 8
    out.append(f'<text x="{lx}" y="{ly}" font-size="13" fill="#111" '
               f'font-weight="bold">Contours</text>')
    out.append(f'<line x1="{lx}" y1="{ly+18}" x2="{lx+26}" y2="{ly+18}" stroke="#c0392b" '
               f'stroke-width="2"/>')
    out.append(f'<text x="{lx+32}" y="{ly+22}" font-size="11" fill="#333">'
               f'90% chance of</text>')
    out.append(f'<text x="{lx+32}" y="{ly+35}" font-size="11" fill="#333">one response</text>')
    out.append(f'<line x1="{lx}" y1="{ly+52}" x2="{lx+26}" y2="{ly+52}" stroke="#2c3e50" '
               f'stroke-width="2" stroke-dasharray="6,4"/>')
    out.append(f'<text x="{lx+32}" y="{ly+56}" font-size="11" fill="#333">'
               f'single-stage design</text>')
    out.append(f'<text x="{lx+32}" y="{ly+69}" font-size="11" fill="#333">'
               f'vs a {int(DESIGN_NULL*100)}% null</text>')
    out.append(f'<text x="{lx}" y="{ly+100}" font-size="13" fill="#111" '
               f'font-weight="bold">Conditions</text>')
    out.append(f'<circle cx="{lx+8}" cy="{ly+116}" r="4" fill="#c0392b" fill-opacity="0.75"/>')
    out.append(f'<text x="{lx+22}" y="{ly+120}" font-size="11" fill="#333">'
               f'below the design</text>')
    out.append(f'<text x="{lx+22}" y="{ly+133}" font-size="11" fill="#333">contour</text>')
    out.append(f'<circle cx="{lx+8}" cy="{ly+152}" r="4" fill="#7f8c8d" fill-opacity="0.75"/>')
    out.append(f'<text x="{lx+22}" y="{ly+156}" font-size="11" fill="#333">at or above it</text>')
    out.append(f'<text x="{lx}" y="{ly+190}" font-size="10.5" fill="#666">'
               f'A point LEFT of a curve is</text>')
    out.append(f'<text x="{lx}" y="{ly+204}" font-size="10.5" fill="#666">'
               f'inside that regime.</text>')

    out.append('</svg>')
    return "\n".join(out) + "\n"


def main(argv):
    svg = build()
    if "--check" in argv:
        if not os.path.exists(OUT):
            print(f"FAIL: {OUT_REL} is missing")
            return 1
        with open(OUT, encoding="utf-8") as fh:
            if fh.read() != svg:
                print(f"FAIL: {OUT_REL} does not re-derive from endpoint-regime-map.json")
                return 1
        print(f"OK: {OUT_REL} re-derives")
        return 0
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {OUT_REL} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
