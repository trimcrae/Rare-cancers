#!/usr/bin/env python3
"""Two-axis portfolio map for the EMC treatment roadmap (categorical grid).

Both axes are categorical, so the figure is a labelled grid — NOT a scatter with a
pseudo-continuous scale (an earlier version implied a granular "impact ceiling" we
cannot measure; see git history).

  x = near-term readiness        : down-weighted -> to build -> confirm-gated -> available now
  y = driver-directedness        : generic -> targeted (indirect) -> driver-directed

Axis-B levels are DEFINED, not scored on a vibe:
  - Driver-directed : acts on the EWSR1::NR4A3 fusion product/transcript itself.
  - Targeted        : engages EMC's fusion-driven biology at a point OTHER than the
                      fusion (surface antigen, stroma, a transactivated node, a
                      selective dependency, or fusion-TF displacement for trabectedin).
  - Generic         : a disease-agnostic mechanism (anti-angiogenic, checkpoint,
                      broadly cytotoxic / proteasome).

This REPLACES the old single-tier `portfolio.svg`. Real plotting library; regenerate
and *view the PNG* before committing (AGENTS.md -> "Making figures").

  python3 portfolio_quadrant.py        # writes portfolio-quadrant.png

Keep cell membership in sync with the two-axis table in:
  research/manuscripts/emc-treatment-roadmap.md (Sec 3)
  research/manuscripts/emc-treatment-strategy.md ("The ranking")
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = os.path.join(os.path.dirname(__file__), "portfolio-quadrant.png")

# columns (readiness), left -> right
COLS = ["Parked /\ndown-weighted", "To build", "Confirm-\ngated", "Available\nnow"]
COL_COLOR = ["#757575", "#6a1b9a", "#1565c0", "#2e7d32"]  # by readiness band
# rows (driver-directedness), bottom -> top
ROWS = ["Generic\n(disease-agnostic)",
        "Targeted, indirect\n(EMC target ≠ the fusion)",
        "Driver-directed\n(the fusion itself)"]

# (col, row) -> list of (route, is_flagship)
CELLS = {
    (3, 0): [("TKI + checkpoint inhibitor", False), ("Carfilzomib + anthracycline", False)],
    (3, 1): [("Trabectedin", False)],
    (2, 1): [("B7-H3 ADC / bispecific", False), ("PRAME ImmTAC / cell therapy", False),
             ("FAP radioligand therapy", False)],
    (1, 2): [("NR4A3 degrader (PROTAC)", True), ("Fusion-junction ASO / siRNA", True)],
    (1, 1): [("B7-H3 / CD56 CAR-T", False), ("PPARG modulation (TZDs)", False)],
    (0, 1): [("TCR-T / ImmTAC", False), ("Synthetic-lethal / BRD9", False),
             ("Fusion-junction vaccine", False)],
}

ncol, nrow = len(COLS), len(ROWS)
fig, ax = plt.subplots(figsize=(12.6, 6.6))

for c in range(ncol):
    for r in range(nrow):
        routes = CELLS.get((c, r), [])
        filled = bool(routes)
        ax.add_patch(Rectangle(
            (c, r), 1, 1, facecolor=COL_COLOR[c] if filled else "#fafafa",
            alpha=0.13 if filled else 1.0, edgecolor="#cfcfcf", linewidth=1.0, zorder=1))
        if not routes:
            if (c, r) == (3, 2):
                ax.text(c + 0.5, r + 0.5, "— empty —\nnothing is both\nready and\ndriver-directed",
                        ha="center", va="center", fontsize=9.5, style="italic", color="#9e9e9e")
            continue
        n = len(routes)
        ys = [r + (i + 1) / (n + 1) for i in range(n)][::-1]  # top-to-bottom in cell
        for (name, flag), y in zip(routes, ys):
            ax.text(c + 0.5, y, ("★ " + name) if flag else name,
                    ha="center", va="center",
                    fontsize=9.6 if flag else 9.2,
                    fontweight="bold" if flag else "normal",
                    color=COL_COLOR[c], zorder=3)

# flagship cell outline
ax.add_patch(Rectangle((1, 2), 1, 1, fill=False, edgecolor="#6a1b9a", linewidth=2.4, zorder=4))
ax.text(1.5, 2.97, "flagship", ha="center", va="top", fontsize=8.5, style="italic",
        color="#6a1b9a", zorder=5)

# column headers (readiness) and row labels (directedness)
for c in range(ncol):
    ax.text(c + 0.5, nrow + 0.10, COLS[c], ha="center", va="bottom",
            fontsize=10.5, fontweight="bold", color=COL_COLOR[c])
for r in range(nrow):
    ax.text(-0.08, r + 0.5, ROWS[r], ha="right", va="center", fontsize=10)

ax.annotate("", xy=(nrow + 0.0, -0.001), xytext=(0, -0.001))  # noop keep limits
ax.set_xlim(-1.95, ncol + 0.05)
ax.set_ylim(-0.5, nrow + 0.75)
ax.set_xlabel("Axis A  —  near-term readiness  →", fontsize=12, labelpad=10)
ax.text(-1.92, nrow / 2, "Axis B  —  driver-directedness  →",
        rotation=90, ha="center", va="center", fontsize=12)
ax.set_title(
    "EMC treatment routes on two categorical axes (readiness × driver-directedness)\n"
    "No route is both ready and driver-directed — that gap is the point",
    fontsize=13, fontweight="bold", pad=14)
ax.set_xticks([])
ax.set_yticks([])
for s in ("top", "right", "left", "bottom"):
    ax.spines[s].set_visible(False)

fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("wrote", OUT)
