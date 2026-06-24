#!/usr/bin/env python3
"""Two-axis portfolio map for the EMC treatment roadmap.

Renders every treatment route on the two axes used in the roadmap/strategy docs:
  x = near-term readiness (parked/down-weighted -> available now)
  y = impact ceiling & driver-directedness (low -> highest)

This REPLACES the old single-tier `portfolio.svg` (a hand-emitted SVG, banned by
AGENTS.md). It uses a real plotting library; regenerate after editing the data and
*view the PNG* before committing (AGENTS.md -> "Making figures").

  python3 portfolio_quadrant.py        # writes portfolio-quadrant.png

Data mirrors the two-axis table in:
  research/manuscripts/emc-treatment-roadmap.md (Sec 3)
  research/manuscripts/emc-treatment-strategy.md ("The ranking")
Keep the three in sync.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = os.path.join(os.path.dirname(__file__), "portfolio-quadrant.png")

# readiness (x): 0 parked/down-weighted, 1 to build, 2 confirm-gated, 3 available now
# impact   (y): 0 low, 1 moderate, 2 high, 3 highest
NOW, CONFIRM, BUILD, DOWN = "now", "confirm", "build", "down"
COLOR = {NOW: "#2e7d32", CONFIRM: "#1565c0", BUILD: "#6a1b9a", DOWN: "#757575"}
BAND_LABEL = {
    NOW: "Available now (approved, EMC evidence)",
    CONFIRM: "Confirm-gated (needs one EMC test)",
    BUILD: "To build (discover / engineer / validate)",
    DOWN: "Down-weighted / parked",
}

# label, x, y, band, flagship?, (dx, dy, ha)
ROUTES = [
    ("TKI + checkpoint inhibitor", 3, 1.00, NOW, False, (-0.12, 0.02, "right")),
    ("Trabectedin", 3, 1.55, NOW, False, (-0.12, 0.0, "right")),
    ("Carfilzomib + anthracycline", 3, 0.35, NOW, False, (-0.12, 0.0, "right")),
    ("B7-H3 ADC / bispecific", 2, 1.80, CONFIRM, False, (0.12, -0.02, "left")),
    ("PRAME ImmTAC / cell therapy", 2, 2.30, CONFIRM, False, (0.12, 0.0, "left")),
    ("FAP radioligand therapy", 2, 1.32, CONFIRM, False, (0.12, 0.0, "left")),
    ("NR4A3 degrader (PROTAC)", 1, 3.00, BUILD, True, (0.12, 0.0, "left")),
    ("Fusion-junction ASO / siRNA", 1, 2.60, BUILD, True, (0.12, 0.0, "left")),
    ("B7-H3 / CD56 CAR-T", 1, 2.05, BUILD, False, (0.12, 0.0, "left")),
    ("PPARG modulation (TZDs)", 1, 0.55, BUILD, False, (0.12, 0.0, "left")),
    ("TCR-T / ImmTAC", 0, 0.62, DOWN, False, (0.12, 0.0, "left")),
    ("Synthetic-lethal / BRD9", 0, 0.18, DOWN, False, (0.12, 0.0, "left")),
    ("Fusion-junction vaccine", 0, 1.02, DOWN, False, (0.12, 0.0, "left")),
]

fig, ax = plt.subplots(figsize=(11.5, 7.6))

# faint quadrant guides
for gx in (0.5, 1.5, 2.5):
    ax.axvline(gx, color="#e0e0e0", lw=1, zorder=0)
for gy in (1.5,):
    ax.axhline(gy, color="#eeeeee", lw=1, zorder=0)

for label, x, y, band, flag, (dx, dy, ha) in ROUTES:
    ax.scatter(
        x, y,
        s=320 if flag else 150,
        marker="*" if flag else "o",
        color=COLOR[band],
        edgecolor="black", linewidth=1.1 if flag else 0.6,
        zorder=5,
    )
    ax.annotate(
        label, (x, y), xytext=(x + dx, y + dy),
        ha=ha, va="center",
        fontsize=10.5, fontweight="bold" if flag else "normal",
        color="black", zorder=6,
    )

# flagship callout
ax.annotate(
    "flagship: hits the\nEWSR1::NR4A3 driver",
    (1, 3.0), xytext=(1.45, 3.30), ha="left", va="center",
    fontsize=9, style="italic", color="#6a1b9a",
)

# label the deliberately-empty top-right corner — that gap is the message
ax.annotate(
    "(empty: nothing is both\nready and high-ceiling)",
    (3.55, 3.25), ha="center", va="center",
    fontsize=9.5, style="italic", color="#9e9e9e",
)

ax.set_xlim(-0.7, 3.95)
ax.set_ylim(-0.35, 3.55)
ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels([
    "Parked /\ndown-weighted", "To build", "Confirm-\ngated", "Available\nnow",
], fontsize=10)
ax.set_yticks([0, 1, 2, 3])
ax.set_yticklabels(["Low", "Moderate", "High", "Highest"], fontsize=10)
ax.set_xlabel("Axis A  —  near-term readiness  →", fontsize=12, labelpad=8)
ax.set_ylabel("Axis B  —  impact ceiling & driver-directedness  →", fontsize=12, labelpad=8)
ax.set_title(
    "EMC treatment routes on two axes (readiness × impact)\n"
    "No route is both ready and high-ceiling — that gap is the point",
    fontsize=13, fontweight="bold", pad=12,
)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

legend_items = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markeredgecolor="black",
           markersize=10, label=BAND_LABEL[b])
    for b, c in COLOR.items()
]
legend_items.append(
    Line2D([0], [0], marker="*", color="w", markerfacecolor="#6a1b9a",
           markeredgecolor="black", markersize=15, label="flagship (EMC-specific driver-directed)")
)
ax.legend(handles=legend_items, loc="upper center", bbox_to_anchor=(0.5, -0.13),
          ncol=2, fontsize=9, frameon=True, framealpha=0.95, borderpad=0.8)

fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("wrote", OUT)
