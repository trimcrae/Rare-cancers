#!/usr/bin/env python3
"""Figure — predicted class I coverage as a function of the acceptance threshold, log x-axis.

WHY A LOG AXIS AND NOT A LINEAR ONE. The function's whole shape lives in two decades: every step
below the conventional cut falls between percentile 0.3736 and 0.4580, and the curve then climbs to
90% by 5.0. On a linear axis the four steps the manuscript's argument rests on collapse into a
single vertical line at the left margin and the reader sees a smooth rise — the opposite of the
paper's point. An external reviewer asked for this axis by name.

⛔ NOTHING IS COMPUTED HERE. Every value is read from `coverage-threshold-curve.json`; this script
draws it. If a number in the figure disagrees with the manuscript, the artifact is the arbiter.

⚠ THE CONVENTIONAL CUT IS DRAWN AS A LINE, NOT AS AN ENDPOINT. Marking 0.5 as where the plot stops
would show a threshold and let the reader take it for a property of the junction; the curve runs to
the data's declared ceiling and 0.5 is one annotated vertical among them.

Dependency-free SVG, per this directory's convention. Output: vaccine-threshold-curve.svg
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CURVE = os.path.join(HERE, "..", "..", "modalities", "coverage-threshold-curve.json")
OUT = os.path.join(HERE, "vaccine-threshold-curve.svg")

W, H = 720, 400
L, R, T, B = 74, 24, 20, 56          # margins
PW, PH = W - L - R, H - T - B


def main():
    d = json.load(open(CURVE))
    rows = [r for r in d["curve"] if r["threshold"] > 0]
    conv = d["conventional_threshold"]
    ceiling = d["_ceiling"]["value"]
    steps = d.get("steps") or []

    xlo, xhi = math.log10(0.1), math.log10(ceiling)
    x = lambda t: L + PW * (math.log10(t) - xlo) / (xhi - xlo)          # noqa: E731
    y = lambda c: T + PH * (1 - c)                                      # noqa: E731

    p = []
    for r in rows:
        if r["threshold"] < 0.1:
            continue
        p.append((x(r["threshold"]), y(r["coverage"])))
    # step function: horizontal then vertical, never a diagonal — a diagonal would draw
    # interpolation the data does not contain.
    path = [f"M {p[0][0]:.1f} {p[0][1]:.1f}"]
    for (x0, y0), (x1, y1) in zip(p, p[1:]):
        path.append(f"L {x1:.1f} {y0:.1f} L {x1:.1f} {y1:.1f}")

    g = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    # y grid + labels
    for frac in (0, .25, .5, .75, 1.0):
        yy = y(frac)
        g.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{L+PW}" y2="{yy:.1f}" '
                 f'stroke="#e6e6e6" stroke-width="1"/>')
        g.append(f'<text x="{L-8}" y="{yy+4:.1f}" font-size="12" fill="#333" '
                 f'text-anchor="end">{int(frac*100)}%</text>')
    # x ticks at the decades and the named cuts
    for t, lab in [(0.1, "0.1"), (0.2, "0.2"), (0.5, "0.5"), (1.0, "1"), (2.0, "2"), (5.0, "5")]:
        if t > ceiling:
            continue
        xx = x(t)
        g.append(f'<line x1="{xx:.1f}" y1="{T+PH}" x2="{xx:.1f}" y2="{T+PH+5}" stroke="#666"/>')
        g.append(f'<text x="{xx:.1f}" y="{T+PH+20}" font-size="12" fill="#333" '
                 f'text-anchor="middle">{lab}</text>')

    # the conventional cut, annotated
    xc = x(conv)
    g.append(f'<line x1="{xc:.1f}" y1="{T}" x2="{xc:.1f}" y2="{T+PH}" stroke="#c0392b" '
             f'stroke-width="1.2" stroke-dasharray="5,4"/>')
    g.append(f'<text x="{xc+6:.1f}" y="{T+14}" font-size="12" fill="#c0392b">'
             f'conventional cut, 0.5</text>')

    g.append(f'<path d="{" ".join(path)}" fill="none" stroke="#1f4e79" stroke-width="2"/>')

    # the four steps below the cut, marked
    for st in steps:
        if st["threshold"] > conv:
            continue
        g.append(f'<circle cx="{x(st["threshold"]):.1f}" cy="{y(st["coverage_after"]):.1f}" '
                 f'r="3.2" fill="#1f4e79"/>')

    g.append(f'<line x1="{L}" y1="{T+PH}" x2="{L+PW}" y2="{T+PH}" stroke="#666"/>')
    g.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T+PH}" stroke="#666"/>')
    g.append(f'<text x="{L+PW/2:.0f}" y="{H-14}" font-size="13" fill="#000" '
             f'text-anchor="middle">MHCflurry presentation percentile (log scale)</text>')
    g.append(f'<text x="16" y="{T+PH/2:.0f}" font-size="13" fill="#000" text-anchor="middle" '
             f'transform="rotate(-90 16 {T+PH/2:.0f})">predicted class I coverage</text>')
    g.append("</svg>")
    open(OUT, "w").write("\n".join(g))
    print(f"wrote {OUT} ({len(rows)} points, ceiling {ceiling}, {len(steps)} steps)")


if __name__ == "__main__":
    main()
