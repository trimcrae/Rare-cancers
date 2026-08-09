#!/usr/bin/env python3
"""Figures 2 and 3 -- the two results a reader would act on. ($0, stdlib, no plotting library)

WHY THESE TWO. Figure 1 draws the regime. The paper's other two findings were tables:

  FIGURE 2  the distribution of the disease-control minus objective-response gap across 552 arms.
            A median and an interquartile range in a table hide the shape; the shape is the argument.
  FIGURE 3  how often a response readout returns NOTHING, against arm size, with the binomial
            expectation at the corpus median rate drawn beside it. The agreement between observed
            and expected IS the argument -- it shows that an uninformative readout is a property of
            arm size rather than of the agent under test.

Emitted as SVG directly, for the reason recorded in endpoint_regime_figure.py: matplotlib is absent
here and depending on it would make the figures unreproducible for anyone without it.

Usage:
  python3 research/manuscripts/endpoint_result_figures.py           # regenerate
  python3 research/manuscripts/endpoint_result_figures.py --check   # verify both committed figures
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REREAD = os.path.join(HERE, "orr-dcr-reread.json")
OUT2 = os.path.join(HERE, "endpoint-gap-distribution.svg")
OUT3 = os.path.join(HERE, "endpoint-zero-response.svg")
OUT2_REL = "research/manuscripts/endpoint-gap-distribution.svg"
OUT3_REL = "research/manuscripts/endpoint-zero-response.svg"

W, H = 880, 470
L, R, T, B = 78, 34, 44, 66

INK = "#222222"
GRID = "#e8e8e8"
ACCENT = "#c0392b"
MUTED = "#7f8c8d"
DARK = "#2c3e50"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _frame(title, xlab, ylab):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
            f'<text x="{L}" y="26" font-size="14" fill="{INK}" font-weight="bold">{esc(title)}</text>',
            f'<text x="{(L + W - R) / 2:.0f}" y="{H - 18}" font-size="12.5" fill="{INK}" '
            f'text-anchor="middle">{esc(xlab)}</text>',
            f'<text x="20" y="{(T + H - B) / 2:.0f}" font-size="12.5" fill="{INK}" '
            f'text-anchor="middle" transform="rotate(-90 20 {(T + H - B) / 2:.0f})">'
            f'{esc(ylab)}</text>']


def figure_gap_distribution(rows, summary):
    """Empirical cumulative distribution of the per-arm gap."""
    gaps = sorted(r["gap_pp"] for r in rows)
    n = len(gaps)

    def sx(g):
        return L + (g / 100.0) * (W - L - R)

    def sy(f):
        return H - B - f * (H - B - T)

    out = _frame("Figure 2. Disease control minus objective response, per arm",
                 "Gap (percentage points) — identically the stable-disease proportion",
                 "Cumulative share of arms")
    for g in range(0, 101, 20):
        out.append(f'<line x1="{sx(g):.1f}" y1="{T}" x2="{sx(g):.1f}" y2="{H-B}" stroke="{GRID}"/>')
        out.append(f'<text x="{sx(g):.1f}" y="{H-B+18}" font-size="11.5" fill="#444" '
                   f'text-anchor="middle">{g}</text>')
    for f in (0, 0.25, 0.5, 0.75, 1.0):
        out.append(f'<line x1="{L}" y1="{sy(f):.1f}" x2="{W-R}" y2="{sy(f):.1f}" stroke="{GRID}"/>')
        out.append(f'<text x="{L-10}" y="{sy(f)+4:.1f}" font-size="11.5" fill="#444" '
                   f'text-anchor="end">{int(f*100)}%</text>')

    pts = []
    for i, g in enumerate(gaps):
        pts.append((sx(g), sy(i / n)))
        pts.append((sx(g), sy((i + 1) / n)))
    out.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
               f'" fill="none" stroke="{DARK}" stroke-width="2"/>')

    med = summary["median_gap_pp"]
    q1, q3 = summary["iqr_gap_pp"]
    for val, lab, col in ((q1, f"IQR {q1}", MUTED), (med, f"median {med}", ACCENT),
                          (q3, f"{q3}", MUTED)):
        out.append(f'<line x1="{sx(val):.1f}" y1="{T}" x2="{sx(val):.1f}" y2="{H-B}" '
                   f'stroke="{col}" stroke-width="1.2" stroke-dasharray="5,4"/>')
        out.append(f'<text x="{sx(val)+4:.1f}" y="{T+14}" font-size="11" fill="{col}">{esc(lab)}</text>')

    at50 = summary["arms_at_or_above"]["50"]
    out.append(f'<text x="{L+8}" y="{H-B-14}" font-size="11.5" fill="{INK}">'
               f'{n} arms · {at50} at or above 50 points</text>')
    out.append('</svg>')
    return "\n".join(out) + "\n"


def figure_zero_response(rows, by_size, corpus_median_orr):
    """Observed share of arms with no responses, against arm size, with the binomial expectation."""
    bins = [(1, 4), (5, 9), (10, 19), (20, 39), (40, 10 ** 6)]
    labels = ["1–4", "5–9", "10–19", "20–39", "40+"]
    obs, tot = [], []
    for lo, hi in bins:
        sub = [r for r in rows if lo <= r["n"] <= hi]
        tot.append(len(sub))
        z = len([r for r in sub if r["objective_response"]["events"] == 0])
        obs.append(z / len(sub) if sub else 0.0)

    # ⛔ THE EXPECTATION IS COMPUTED OVER THE ARMS THEMSELVES, NOT AT A BIN MIDPOINT.
    # This was `mids = [2.5, 7, 14, 29, 60]`, one guessed n per bin. For the four bounded bins the
    # guess was close. For the OPEN-ENDED bin it was not: those 90 arms have a median n of 128.5 and
    # a mean of 158.5, against the 60 assumed. The drawn expectation there was 0.8% where the exact
    # value is 0.5% and the observed share is 0.0%, so the guess made the binomial model look like a
    # WORSE fit than it is -- in the figure whose entire argument is that observed and expected
    # agree. An open-ended bin has no midpoint to guess, which is why one was invented.
    # The exact quantity is the mean of (1-p)^n over the arms in the bin: each arm has its own n, and
    # averaging their individual zero-response probabilities is what "expected share of arms with no
    # response" means. It needs no assumption about the bin's shape.
    p = corpus_median_orr / 100.0
    exp = []
    for lo, hi in bins:
        sub = [r for r in rows if lo <= r["n"] <= hi]
        exp.append(sum((1 - p) ** r["n"] for r in sub) / len(sub) if sub else 0.0)

    def sx(i):
        return L + (i + 0.5) * (W - L - R) / len(bins)

    def sy(f):
        return H - B - f * (H - B - T)

    out = _frame("Figure 3. Arms recording no objective response, by arm size",
                 "Evaluable patients in the arm",
                 "Share of arms with zero responses")
    for f in (0, 0.25, 0.5, 0.75, 1.0):
        out.append(f'<line x1="{L}" y1="{sy(f):.1f}" x2="{W-R}" y2="{sy(f):.1f}" stroke="{GRID}"/>')
        out.append(f'<text x="{L-10}" y="{sy(f)+4:.1f}" font-size="11.5" fill="#444" '
                   f'text-anchor="end">{int(f*100)}%</text>')

    bw = (W - L - R) / len(bins) * 0.42
    for i, (o, t, lab) in enumerate(zip(obs, tot, labels)):
        x = sx(i)
        out.append(f'<rect x="{x-bw:.1f}" y="{sy(o):.1f}" width="{bw:.1f}" '
                   f'height="{(H-B)-sy(o):.1f}" fill="{ACCENT}" fill-opacity="0.78"/>')
        out.append(f'<text x="{x-bw/2:.1f}" y="{sy(o)-6:.1f}" font-size="11" fill="{ACCENT}" '
                   f'text-anchor="middle">{round(100*o)}%</text>')
        out.append(f'<text x="{x:.1f}" y="{H-B+18}" font-size="11.5" fill="#444" '
                   f'text-anchor="middle">{lab}</text>')
        out.append(f'<text x="{x:.1f}" y="{H-B+33}" font-size="10" fill="{MUTED}" '
                   f'text-anchor="middle">n={t}</text>')

    for i, e in enumerate(exp):
        x = sx(i)
        out.append(f'<rect x="{x:.1f}" y="{sy(e):.1f}" width="{bw:.1f}" '
                   f'height="{(H-B)-sy(e):.1f}" fill="{DARK}" fill-opacity="0.42"/>')
    out.append('<polyline points="' +
               " ".join(f"{sx(i)+bw/2:.1f},{sy(e):.1f}" for i, e in enumerate(exp)) +
               f'" fill="none" stroke="{DARK}" stroke-width="1.6" stroke-dasharray="5,4"/>')

    lx, ly = W - R - 250, T + 6
    out.append(f'<rect x="{lx-8}" y="{ly-14}" width="248" height="52" fill="#ffffff" '
               f'fill-opacity="0.9" stroke="{GRID}"/>')
    out.append(f'<rect x="{lx}" y="{ly-8}" width="14" height="11" fill="{ACCENT}" '
               f'fill-opacity="0.78"/>')
    out.append(f'<text x="{lx+20}" y="{ly+2}" font-size="11" fill="{INK}">observed</text>')
    out.append(f'<rect x="{lx}" y="{ly+10}" width="14" height="11" fill="{DARK}" '
               f'fill-opacity="0.42"/>')
    out.append(f'<text x="{lx+20}" y="{ly+20}" font-size="11" fill="{INK}">'
               f'binomial at {corpus_median_orr}% response</text>')
    out.append('</svg>')
    return "\n".join(out) + "\n"


def build():
    with open(REREAD) as fh:
        rr = json.load(fh)
    rows = rr["R2_per_arm_rows"]
    summary = rr["R3_distribution_summary"]["all_arms"]
    by_size = rr["R8_zero_response_readouts"]["by_arm_size"]
    orrs = sorted(r["objective_response"]["pct"] for r in rows)
    median_orr = round(orrs[len(orrs) // 2], 1)
    return (figure_gap_distribution(rows, summary),
            figure_zero_response(rows, by_size, median_orr))


def main(argv):
    svg2, svg3 = build()
    pairs = ((OUT2, svg2, OUT2_REL), (OUT3, svg3, OUT3_REL))
    if "--check" in argv:
        for path, svg, rel in pairs:
            if not os.path.exists(path):
                print(f"FAIL: {rel} is missing")
                return 1
            with open(path, encoding="utf-8") as fh:
                if fh.read() != svg:
                    print(f"FAIL: {rel} does not re-derive from orr-dcr-reread.json")
                    return 1
        print(f"OK: {OUT2_REL} and {OUT3_REL} re-derive")
        return 0
    for path, svg, rel in pairs:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"wrote {rel} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
