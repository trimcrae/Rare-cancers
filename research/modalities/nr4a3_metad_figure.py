#!/usr/bin/env python3
"""
Publication figure of the NR4A3 cryptic-pocket free-energy landscape from 60 ns well-tempered metadynamics.

Reads the committed PLUMED sum_hills profile (metad-fes-60ns.dat: Rg nm, F kJ/mol), references F to the basin
minimum, converts to kcal/mol, and plots F(Rg) as a single annotated line — showing the single breathing basin,
the druggable release-frame sitting ~0.6 kcal/mol above the floor, and the expensive wide-open frontier
(~35 kcal/mol). One series → no legend; the key states are direct-labelled. Colorblind-safe single hue,
recessive grid, prints in grayscale. Output: nr4a3-metad-fes.png (+ .pdf).
"""
import os
import sys

import report_metad as rm

HERE = os.path.dirname(os.path.abspath(__file__))
KJ_PER_KCAL = 4.184
DRUGGABLE_RG = 0.737      # unbiased release-frame Rg (§2.2)
FRONTIER_RG = 1.06        # most-open metad frontier


def main():
    fes = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "metad-fes-60ns.dat")
    out = os.path.join(HERE, "nr4a3-metad-fes.png")
    pts = rm.parse_fes(fes)
    if not pts:
        sys.exit(f"no data in {fes}")
    fmin = min(f for _rg, f in pts)
    rg = [p[0] for p in pts]
    fk = [(p[1] - fmin) / KJ_PER_KCAL for p in pts]        # kcal/mol, referenced to the basin minimum (0)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    LINE = "#2f6fed"       # single accessible blue (strong contrast on white; distinct in grayscale)
    INK = "#1a1a2e"
    MUTED = "#8a8f98"
    DRUG = "#0f9d58"       # status-green for the druggable annotation (with a text label, not colour-alone)

    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=200)
    ax.plot(rg, fk, color=LINE, lw=2.2, zorder=3)

    # basin minimum
    imin = min(range(len(fk)), key=lambda i: fk[i])
    ax.scatter([rg[imin]], [fk[imin]], s=42, color=LINE, zorder=4, edgecolor="white", linewidth=1.2)
    ax.annotate(f"resting basin\nRg {rg[imin]:.2f} nm", (rg[imin], fk[imin]),
                textcoords="offset points", xytext=(6, 26), fontsize=9, color=INK,
                ha="left", arrowprops=dict(arrowstyle="-", color=MUTED, lw=1))

    def _at(target):
        j = min(range(len(rg)), key=lambda i: abs(rg[i] - target))
        return rg[j], fk[j]

    # druggable release-frame
    dx, dy = _at(DRUGGABLE_RG)
    ax.scatter([dx], [dy], s=42, color=DRUG, zorder=4, edgecolor="white", linewidth=1.2)
    ax.annotate(f"druggable frame\n+{dy:.1f} kcal/mol", (dx, dy),
                textcoords="offset points", xytext=(-96, 40), fontsize=9, color=DRUG,
                ha="left", arrowprops=dict(arrowstyle="->", color=DRUG, lw=1.2))
    # open frontier
    fx, fy = _at(FRONTIER_RG)
    ax.scatter([fx], [fy], s=42, color=INK, zorder=4, edgecolor="white", linewidth=1.2)
    ax.annotate(f"wide-open frontier\n+{fy:.0f} kcal/mol", (fx, fy),
                textcoords="offset points", xytext=(-30, 14), fontsize=9, color=INK, ha="right")

    ax.set_xlabel("pocket radius of gyration, Rg (nm)  —  closed → open", fontsize=10, color=INK)
    ax.set_ylabel("free energy (kcal/mol, ref. to basin)", fontsize=10, color=INK)
    ax.set_title("NR4A3 cryptic pocket: a single breathing basin (60 ns well-tempered metadynamics)",
                 fontsize=10.5, color=INK, pad=10)
    ax.grid(True, color="#e7e8ec", lw=0.8, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.margins(x=0.02)
    ax.text(0.5, -0.20, "Single biased profile; edge values are sum_hills-referenced at the metad walls and "
            "not physical closed/open energies.", transform=ax.transAxes, ha="center", va="top",
            fontsize=7.2, color=MUTED, wrap=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".png", ".pdf"), bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
