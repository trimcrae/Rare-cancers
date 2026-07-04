#!/usr/bin/env python3
"""Plot Yank ABFE ΔG_bind vs HREX iteration with error bars, from a jsonl of {"iter","dg","se"} points
(one per hourly `fep-analyze-aws.yml` dispatch). Error bars are ±1 standard error = the MBAR estimator's
68% confidence interval (16th–84th percentile); a shaded 95% band (±1.96 SE, 2.5th–97.5th pct) is also drawn.

    python plot_fep_convergence.py <points.jsonl> <out.png> [receptor_label]
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def main():
    src, out = sys.argv[1], sys.argv[2]
    label = sys.argv[3] if len(sys.argv) > 3 else "NR4A3"
    pts = [json.loads(l) for l in open(src) if l.strip()]
    pts = [p for p in pts if p.get("iter", -1) >= 0 and "dg" in p]
    pts.sort(key=lambda p: p["iter"])
    if not pts:
        raise SystemExit("no valid points to plot")
    x = np.array([p["iter"] for p in pts], float)
    y = np.array([p["dg"] for p in pts], float)
    e = np.array([p["se"] for p in pts], float)

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.fill_between(x, y - 1.96 * e, y + 1.96 * e, alpha=0.15, color="#4C78A8",
                    label="95% CI (±1.96 SE · 2.5–97.5th pct)")
    ax.errorbar(x, y, yerr=e, fmt="o-", color="#204E8A", ecolor="#4C78A8", capsize=4, lw=1.6,
                label="ΔG ± 1 SE (68% CI · 16–84th pct)")
    ax.axhline(0.0, color="#999", lw=0.8, ls="--")
    # annotate the latest point
    ax.annotate(f"{y[-1]:.1f} ± {e[-1]:.1f}", (x[-1], y[-1]), textcoords="offset points",
                xytext=(8, 8), fontsize=9, color="#204E8A")
    ax.set_xlabel("HREX iteration")
    ax.set_ylabel(r"$\Delta G_{\mathrm{bind}}$ (kcal/mol)")
    ax.set_title(f"{label} ABFE convergence — denovo_401\nerror bars = ±1 SE (MBAR 68% CI, 16–84th percentile)")
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print(f"wrote {out} ({len(pts)} points; latest iter {int(x[-1])} ΔG {y[-1]:.2f} ± {e[-1]:.2f})")


if __name__ == "__main__":
    main()
