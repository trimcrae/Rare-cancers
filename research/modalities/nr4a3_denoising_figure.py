#!/usr/bin/env python3
"""
Figure 2 — Multi-snapshot MM-GBSA de-noising of the de-novo selectivity harvest (§2.6).

Each candidate's *single-snapshot* NR4A3-selectivity margin (an extreme-value point estimate) is contrasted
with its *multi-snapshot* mean +/- SD (minimize -> short GB Langevin MD -> DeltaG averaged over 10 frames).
A dumbbell per candidate shows how far the single-snapshot value moves under ensemble de-noising: the
single-snapshot best `denovo_393` (+18.34) collapses to ~0 (noise artifact), the negative control
`denovo_924` stays strongly non-selective (method discriminates), and only `denovo_401` (the lead) holds with
a small SD and margin - SD = +9.85 well clear of the multi-snapshot decoy-null 95th percentile (+6.69).

Data are transcribed from the manuscript's §2.6 de-noising table (each value is a committed SageMaker
MM-GBSA run quoted inline); the multi-snapshot decoy null 95th percentile (+6.69) is the §2.6 recalibrated
null. No values are estimated here. Output: nr4a3-denoising.png (+ .pdf).
"""
import os

# --- committed data: manuscript §2.6 de-noising table (single-snapshot -> multi-snapshot mean +/- SD) ---
# columns: label, single-snapshot margin, multi mean, multi SD, role
ROWS = [
    ("denovo_393", 18.34, -2.95, 3.65, "collapses (was single-snapshot best)"),
    ("denovo_111", 15.70, 14.60, 4.10, "holds as neutral (later withdrawn: cation reverses)"),
    ("denovo_780", 14.66, 2.07, 6.36, "within noise of 0"),
    ("denovo_401", 13.92, 12.83, 2.98, "holds — LEAD"),
    ("denovo_924", -19.41, -25.20, 4.55, "negative control (stays non-selective)"),
]
DECOY_NULL_95 = 6.69   # §2.6 multi-snapshot decoy-null 95th percentile (max decoy +7.10)

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    INK = "#1a1a2e"
    MUTED = "#8a8f98"
    SINGLE = "#d97706"    # single-snapshot (amber)
    MULTI = "#2f6fed"     # multi-snapshot de-noised (blue)

    out = os.path.join(HERE, "nr4a3-denoising.png")
    n = len(ROWS)
    ys = list(range(n))[::-1]   # first row at top

    fig, ax = plt.subplots(figsize=(7.4, 4.3), dpi=200)

    # selectivity boundary and decoy null
    ax.axvline(0, color=MUTED, lw=1.0, zorder=1)
    ax.axvspan(-100, DECOY_NULL_95, color="#f2f3f5", zorder=0)
    ax.axvline(DECOY_NULL_95, color=MUTED, lw=1.1, ls="--", zorder=1)
    ax.text(DECOY_NULL_95 + 0.4, ys[0] + 0.62, "multi-snapshot\ndecoy null (95th %ile, +6.69)",
            fontsize=7.6, color=MUTED, ha="left", va="center")

    for (label, single, mean, sd, role), y in zip(ROWS, ys):
        # connector
        ax.plot([single, mean], [y, y], color=MUTED, lw=1.4, zorder=2, alpha=0.7)
        # single-snapshot point
        ax.scatter([single], [y], s=48, color=SINGLE, zorder=4, edgecolor="white", linewidth=1.0)
        # multi-snapshot mean +/- SD
        ax.errorbar([mean], [y], xerr=[sd], fmt="o", color=MULTI, ms=8, capsize=4,
                    elinewidth=1.6, zorder=5, markeredgecolor="white", markeredgewidth=1.0)
        lead = "denovo_401" in label
        ax.text(-40.5, y, label, fontsize=8.6, color=(INK if lead else "#4a4f5a"),
                ha="left", va="center", fontweight=("bold" if lead else "normal"))
        ax.text(-40.5, y - 0.34, role, fontsize=6.9, color=MUTED, ha="left", va="center", style="italic")

    ax.set_yticks([])
    ax.set_xlim(-41, 24)
    ax.set_ylim(-0.7, n - 0.3 + 0.9)
    ax.set_xlabel("NR4A3-selectivity margin  ΔΔG  (kcal/mol; NR4A3 favoured →)", fontsize=10, color=INK)
    ax.set_title("Ensemble de-noising separates a real lead from single-snapshot noise (§2.6)",
                 fontsize=11, color=INK, pad=12)
    ax.grid(True, axis="x", color="#e7e8ec", lw=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)

    legend = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=SINGLE, markersize=8,
               label="single-snapshot margin (point estimate)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=MULTI, markersize=8,
               label="multi-snapshot mean ± SD (10 frames)"),
    ]
    ax.legend(handles=legend, loc="upper left", bbox_to_anchor=(0.02, 1.02),
              frameon=False, fontsize=8.4)

    ax.text(0.0, -0.185, "Values from manuscript §2.6 (each a committed SageMaker MM-GBSA run). Single-trajectory "
            "GB-implicit MD, not FEP; magnitudes inflated — direction/robustness, not affinity.",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.0, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".png", ".pdf"), bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
