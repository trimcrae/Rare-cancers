#!/usr/bin/env python3
"""Convergence plot for the denovo_401 ABFE selectivity result.
Input: scratchpad/abfe_traces.json = {"NR4A3": [[iter,dg,se],...], "NR4A1": [...], "NR4A2": [...]}
Each trace is the per-iteration MBAR ΔG_bind (kcal/mol) — EVERY iteration is plotted.
Output: scratchpad/abfe_convergence.png
Panel A: ΔG_bind vs iteration, 3 receptors, ±SE band (0 line = binding threshold).
Panel B: selectivity ΔΔG = ΔG_bind(NR4A3) − ΔG_bind(paralog) vs iteration (0 line = non-selective).
"""
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IN = sys.argv[1] if len(sys.argv) > 1 else "scratchpad/abfe_traces.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "scratchpad/abfe_convergence.png"
TITLE = sys.argv[3] if len(sys.argv) > 3 else "denovo_401 ABFE — ΔG_bind convergence"

# colourblind-safe (Okabe-Ito): target highlighted, paralogs muted-but-distinct
COL = {"NR4A3": "#0072B2", "NR4A1": "#D55E00", "NR4A2": "#E69F00"}
data = json.load(open(IN))
arr = {r: np.array(v, dtype=float) for r, v in data.items() if v}


def band(ax, x, y, se, color, label):
    ax.fill_between(x, y - se, y + se, color=color, alpha=0.15, linewidth=0)
    ax.plot(x, y, color=color, lw=1.6, label=label)


fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.8))

for r in ("NR4A3", "NR4A1", "NR4A2"):
    if r not in arr:
        continue
    x, y, se = arr[r][:, 0], arr[r][:, 1], arr[r][:, 2]
    final = f"{y[-1]:+.2f}±{se[-1]:.2f}"
    band(a, x, y, se, COL[r], f"{r}  ({final})")
a.axhline(0, color="#666", lw=0.9, ls="--")
a.set_xlabel("MBAR iteration"); a.set_ylabel("ΔG$_{bind}$ (kcal/mol)")
a.set_title("A. Absolute binding free energy")
a.legend(frameon=False, fontsize=9, title="receptor (final ΔG$_{bind}$)")
a.grid(alpha=0.15)

# ΔΔG = target − paralog, aligned on shared iterations
tgt = arr.get("NR4A3")
if tgt is not None:
    td = {int(i): (d, s) for i, d, s in tgt}
    for p in ("NR4A1", "NR4A2"):
        if p not in arr:
            continue
        xs, dd, ee = [], [], []
        for i, d, s in arr[p]:
            k = int(i)
            if k in td:
                xs.append(k); dd.append(td[k][0] - d)
                ee.append((td[k][1] ** 2 + s ** 2) ** 0.5)
        xs, dd, ee = np.array(xs), np.array(dd), np.array(ee)
        fin = f"{dd[-1]:+.2f}±{ee[-1]:.2f}"
        band(b, xs, dd, ee, COL[p], f"NR4A3 − {p}  ({fin})")
b.axhline(0, color="#666", lw=0.9, ls="--")
b.text(0.98, 0.03, "below 0 = NR4A3-selective", transform=b.transAxes,
       ha="right", va="bottom", fontsize=8, color="#333", style="italic")
b.set_xlabel("MBAR iteration"); b.set_ylabel("ΔΔG (kcal/mol)")
b.set_title("B. Selectivity vs paralogues")
b.legend(frameon=False, fontsize=9)
b.grid(alpha=0.15)

fig.suptitle(TITLE, fontsize=12, y=1.02)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"wrote {OUT}  ({', '.join(f'{r}:{len(arr[r])}pts' for r in arr)})")
