#!/usr/bin/env python3
"""Overlay Yank ABFE ΔG_bind vs HREX iteration for one or more receptors, from jsonl convergence points
({"receptor","iter","dg","se"}, one line per prod segment, emitted by nr4a3_fep._append_conv_point).
Error bars are ±1 standard error = the MBAR estimator's 68% CI (16th–84th percentile); a shaded 95% band
(±1.96 SE, 2.5th–97.5th pct) is drawn per receptor.

    python plot_fep_convergence.py <out.png> <points1.jsonl> [points2.jsonl ...]

Each file may hold points for multiple receptors; series are grouped + colored by the "receptor" field.
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

# NR4A3 = target (warm); paralogues = off-targets we want to SPARE (cool). Distinct, colorblind-safe.
COLORS = {"nr4a3": "#D1495B", "nr4a1": "#2E86AB", "nr4a2": "#3FA34D"}
_FALLBACK = ["#8E7DBE", "#E8A628", "#5C6672"]


def main():
    out = sys.argv[1]
    files = sys.argv[2:]
    if not files:
        raise SystemExit("usage: plot_fep_convergence.py <out.png> <points.jsonl> [...]")
    by_rec = {}
    for fp in files:
        for line in open(fp):
            line = line.strip()
            if not line:
                continue
            p = json.loads(line)
            if p.get("iter", -1) < 0 or "dg" not in p:
                continue
            by_rec.setdefault(p.get("receptor", "nr4a3"), []).append(p)
    if not by_rec:
        raise SystemExit("no valid convergence points to plot")

    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    order = [r for r in ("nr4a3", "nr4a1", "nr4a2") if r in by_rec] + \
            [r for r in by_rec if r not in ("nr4a3", "nr4a1", "nr4a2")]
    for i, rec in enumerate(order):
        pts = sorted(by_rec[rec], key=lambda p: p["iter"])
        x = np.array([p["iter"] for p in pts], float)
        y = np.array([p["dg"] for p in pts], float)
        e = np.array([p["se"] for p in pts], float)
        c = COLORS.get(rec, _FALLBACK[i % len(_FALLBACK)])
        ax.fill_between(x, y - 1.96 * e, y + 1.96 * e, alpha=0.12, color=c)
        ax.errorbar(x, y, yerr=e, fmt="o-", color=c, ecolor=c, capsize=4, lw=1.8,
                    label=f"{rec.upper()}  ({y[-1]:.1f} ± {e[-1]:.1f} @ it{int(x[-1])})")
    ax.axhline(0.0, color="#999", lw=0.8, ls="--")
    ax.set_xlabel("HREX iteration")
    ax.set_ylabel(r"$\Delta G_{\mathrm{bind}}$ (kcal/mol)  — more negative = tighter")
    ax.set_title("denovo_401 ABFE convergence, NR4A3 vs paralogues\n"
                 "error = ±1 SE (MBAR 68% CI, 16–84th pct); shaded = 95% CI (±1.96 SE)")
    ax.legend(fontsize=8, loc="best", title="ΔG_bind ± 1 SE")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print(f"wrote {out} ({sum(len(v) for v in by_rec.values())} points across {len(by_rec)} receptors)")


if __name__ == "__main__":
    main()
