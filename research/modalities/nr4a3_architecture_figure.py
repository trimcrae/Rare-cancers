#!/usr/bin/env python3
"""
Figure 6 — Selectivity architecture: the orthosteric cryptic pocket is the LBD's paralogue-divergence hotspot
(§2.7).

Paralogue divergence (fraction of residues differing from NR4A1/NR4A2) is compared across four residue sets of
the NR4A3 LBD: the orthosteric cryptic pocket (the warhead's contact residues), the predicted NR4A3–CRBN
ternary interface, the whole-LBD pocket-residue census, and the non-orthosteric remainder. The warhead pocket
is the *most* divergent zone (70 % vs ≥1 paralogue / 60 % vs both), ~1.6× the LBD-wide average — so binder
selectivity is handle-rich, and the ternary interface is separately divergent on a *different* surface (the
multiplicative-budget point). Selectivity's limit is pocket druggability + affinity-margin robustness, not a
scarcity of divergent handles.

Data transcribed from the manuscript §2.7 selectivity-architecture table (source alignment
nr4a-selectivity.json). The remainder set has no "vs both" value in the table (shown as ≥1 only). No values
estimated. Output: nr4a3-architecture.png (+ .pdf).
"""
import os

# --- committed data: manuscript §2.7 table (percent divergent) ---
# label, n, divergent vs >=1 paralogue (%), divergent vs both (% or None)
ROWS = [
    ("orthosteric cryptic pocket\n(warhead contacts)", 10, 70, 60),
    ("LBD-wide pocket census", 148, 45, 28),
    ("non-orthosteric remainder\n(surface / PPI proxy)", 138, 43, None),
    ("predicted NR4A3–CRBN\nternary interface", 33, 24, 18),
]

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    INK = "#1a1a2e"
    MUTED = "#8a8f98"
    C_ANY = "#9bb7f2"    # lighter blue: divergent vs >=1 paralogue
    C_BOTH = "#2f6fed"   # strong blue: divergent vs both paralogues
    HILITE = "#0f9d58"

    out = os.path.join(HERE, "nr4a3-architecture.png")
    n = len(ROWS)
    ys = list(range(n))[::-1]
    h = 0.34

    fig, ax = plt.subplots(figsize=(7.4, 4.3), dpi=200)

    for (label, nres, any_p, both_p), y in zip(ROWS, ys):
        ax.barh(y + h / 2 + 0.02, any_p, height=h, color=C_ANY, zorder=3)
        ax.text(any_p + 1.2, y + h / 2 + 0.02, f"{any_p}%", va="center", ha="left",
                fontsize=8.2, color=INK)
        if both_p is not None:
            ax.barh(y - h / 2 - 0.02, both_p, height=h, color=C_BOTH, zorder=3)
            ax.text(both_p + 1.2, y - h / 2 - 0.02, f"{both_p}%", va="center", ha="left",
                    fontsize=8.2, color=INK)
        else:
            ax.text(1.5, y - h / 2 - 0.02, "(vs both: n/a)", va="center", ha="left",
                    fontsize=7.2, color=MUTED, style="italic")
        is_pocket = label.startswith("orthosteric")
        ax.text(-2, y, label, va="center", ha="right",
                fontsize=8.4, color=(HILITE if is_pocket else INK),
                fontweight=("bold" if is_pocket else "normal"))
        ax.text(-2, y - 0.30, f"n = {nres}", va="center", ha="right", fontsize=7.0, color=MUTED)

    ax.set_yticks([])
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlabel("residues divergent from paralogue(s)  (%)", fontsize=10, color=INK)
    ax.set_title("The warhead pocket is the LBD's paralogue-divergence hotspot (§2.7)",
                 fontsize=11, color=INK, pad=10)
    ax.grid(True, axis="x", color="#e7e8ec", lw=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)

    legend = [
        Line2D([0], [0], marker="s", color="w", markerfacecolor=C_ANY, markersize=10,
               label="divergent vs ≥1 paralogue"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor=C_BOTH, markersize=10,
               label="divergent vs both paralogues"),
    ]
    ax.legend(handles=legend, loc="lower right", frameon=False, fontsize=8.6)

    ax.text(0.0, -0.185, "Values from manuscript §2.7 table (alignment source nr4a-selectivity.json).\n"
            "Sequence divergence = handle availability, a specification — not a demonstrated binding margin.",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.0, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    fig.savefig(out.replace(".png", ".pdf"), bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
