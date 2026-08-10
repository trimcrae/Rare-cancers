#!/usr/bin/env python3
"""
Figure 1 of repurposing-hypotheses.md — the three-method design and the firewall.

Replaces a ```mermaid``` source block that could not be submitted as a figure. Journals want a
raster or vector image, not a diagram DSL a renderer may or may not have; the block also rendered
nowhere in the PDF the reviewer would see, so the manuscript referred to a "Figure 1" that did not
exist as one.

Dependency-free apart from matplotlib, which the repository already carries. Emits PNG and PDF, and
is GREYSCALE-SAFE by construction: every box is distinguished by outline weight and fill lightness
rather than by hue, so the colour charge some journals levy on figures is avoidable without a
redraw. Regenerate with:

    python3 research/manuscripts/figures/repurposing_design_figure.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
STEM = os.path.join(HERE, "repurposing-fig1-design")

# (key, x, y, w, h, text, facecolour, edge width, dashed outline)
#: ⚠ Geometry is explicit and was checked by eye against the rendered PNG. The first layout put the
#: firewall on top of the "not used as a source" node and ran an edge label through both.
BOXES = [
    ("A", 0.02, 0.76, 0.26, 0.14, "Mechanism curation\n(expert, literature)", "#f2f2f2", 1.2, False),
    ("B", 0.02, 0.55, 0.26, 0.14, "Target-to-drug enumeration\n(DGIdb, reproducible)", "#f2f2f2", 1.2, False),
    ("C", 0.02, 0.09, 0.26, 0.14, "Graph foundation model\n(TxGNN, zero-shot)", "#ffffff", 1.0, True),
    ("N", 0.42, 0.09, 0.22, 0.12, "Not used as a source", "#ffffff", 1.0, True),
    ("D", 0.37, 0.585, 0.28, 0.16, "Scored candidate catalogue\n14 existing drugs, tiers T0–T3", "#e0e0e0", 1.8, False),
    ("M", 0.74, 0.66, 0.24, 0.16, "Manuscript and path\nto testing", "#f2f2f2", 1.2, False),
    ("P", 0.74, 0.30, 0.24, 0.14, "Cited clinical registry", "#f2f2f2", 1.2, False),
]
FIREWALL = (0.42, 0.355, 0.18, 0.10)   # x, y, w, h

fig, ax = plt.subplots(figsize=(9.2, 5.0))
ax.set_xlim(0, 1); ax.set_ylim(0.05, 0.95); ax.axis("off")

anchors = {}
for key, x, y, w, h, text, fc, lw, dashed in BOXES:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012",
                                facecolor=fc, edgecolor="#222222", linewidth=lw,
                                linestyle="--" if dashed else "-"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.6,
            color="#111111", linespacing=1.35)
    anchors[key] = {"l": (x, y + h / 2), "r": (x + w, y + h / 2),
                    "t": (x + w / 2, y + h), "b": (x + w / 2, y)}

# the firewall, drawn as a diamond-ish heavy node so it reads as a gate rather than a step
fx, fy, fw, fh = FIREWALL
ax.add_patch(FancyBboxPatch((fx, fy), fw, fh, boxstyle="round,pad=0.006,rounding_size=0.004",
                            facecolor="#ffffff", edgecolor="#111111", linewidth=2.4))
ax.text(fx + fw / 2, fy + fh / 2, "Firewall", ha="center", va="center",
        fontsize=9.2, fontweight="bold", color="#111111")
anchors["F"] = {"l": (fx, fy + fh / 2), "r": (fx + fw, fy + fh / 2),
                "t": (fx + fw / 2, fy + fh), "b": (fx + fw / 2, fy)}


def arrow(a, b, label=None, dashed=False, rad=0.0, lx=0.0, ly=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=13,
                                 linewidth=1.5 if not dashed else 1.1,
                                 linestyle="--" if dashed else "-",
                                 color="#333333" if not dashed else "#777777",
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=3))
    if label:
        ax.text((a[0] + b[0]) / 2 + lx, (a[1] + b[1]) / 2 + ly, label, ha="center", va="center",
                fontsize=7.4, color="#444444", linespacing=1.3,
                bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="none"))


arrow(anchors["A"]["r"], anchors["D"]["l"], rad=-0.12)
arrow(anchors["B"]["r"], anchors["D"]["l"], rad=0.10)
arrow(anchors["C"]["r"], anchors["N"]["l"], dashed=True,
      label="diverged; reported as a limitation,\nno hit promoted", ly=0.075)
arrow(anchors["D"]["b"], anchors["F"]["t"], rad=0.0)
arrow(anchors["F"]["r"], anchors["P"]["l"], rad=-0.10,
      label="T3 plus clinician\nreview only", ly=0.055)
arrow(anchors["D"]["r"], anchors["M"]["l"], rad=0.0)

fig.tight_layout(pad=0.4)
for ext in ("png", "pdf"):
    fig.savefig(f"{STEM}.{ext}", dpi=300, bbox_inches="tight",
                facecolor="white", edgecolor="none")
print(f"wrote {STEM}.png and {STEM}.pdf")
