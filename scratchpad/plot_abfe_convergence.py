#!/usr/bin/env python3
"""Convergence plot for the denovo_401 ABFE selectivity result.
Input JSON (scratchpad/abfe_traces.json) — either legacy or rich form per receptor:
  legacy:  {"NR4A3": [[iter,dg,se],...], ...}
  rich:    {"NR4A3": {"trace": [[iter,dg,se],...], "convergence": {first_half, second_half, drift, block_sd}}, ...}
Every iteration is plotted. Two uncertainties are drawn so they can't be confused:
  * SHADED band = MBAR asymptotic SE (precision of the currently-sampled ensemble; shrinks ~1/√N).
  * CAPPED bar at the right edge = block-SD (drift-aware "actual" uncertainty from contiguous blocks).
Output: scratchpad/abfe_convergence.png
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

COL = {"NR4A3": "#0072B2", "NR4A1": "#D55E00", "NR4A2": "#E69F00"}
raw = json.load(open(IN))

arr, conv = {}, {}
for r, v in raw.items():
    if isinstance(v, dict):
        if v.get("trace"):
            arr[r] = np.array(v["trace"], dtype=float)
            conv[r] = v.get("convergence") or {}
    elif v:
        arr[r] = np.array(v, dtype=float)
        conv[r] = {}


def honest_sd(r):
    c = conv.get(r) or {}
    for key in ("block_sd", "drift"):
        if c.get(key) is not None:
            return float(c[key])
    return None


def band(ax, x, y, se, color, label):
    ax.fill_between(x, y - se, y + se, color=color, alpha=0.15, linewidth=0)
    ax.plot(x, y, color=color, lw=1.6, label=label)


fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 5.0))

for r in ("NR4A3", "NR4A1", "NR4A2"):
    if r not in arr:
        continue
    x, y, se = arr[r][:, 0], arr[r][:, 1], arr[r][:, 2]
    sd = honest_sd(r)
    unc = f"{sd:.2f}" if sd is not None else f"{se[-1]:.2f}"
    band(a, x, y, se, COL[r], f"{r}  ({y[-1]:+.2f} ± {unc})")
    if sd is not None:                                    # honest (block-SD) error bar just past the last iter
        a.errorbar(x[-1] + 0.02 * (x[-1] - x[0]) + 6, y[-1], yerr=sd, fmt="o", ms=4,
                   color=COL[r], capsize=4, elinewidth=1.6, capthick=1.6)
a.axhline(0, color="#666", lw=0.9, ls="--")
a.set_xlabel("MBAR iteration"); a.set_ylabel("ΔG$_{bind}$ (kcal/mol)")
a.set_title("A. Absolute binding free energy")
a.legend(frameon=False, fontsize=9, title="receptor (final ΔG$_{bind}$ ± block-SD)")
a.grid(alpha=0.15)

# ΔΔG = target − paralog, aligned on shared iterations; honest ΔΔG SD = √(sd_t² + sd_p²)
tgt = arr.get("NR4A3")
sd_t = honest_sd("NR4A3")
if tgt is not None:
    td = {int(i): (d, s) for i, d, s in tgt}
    for p in ("NR4A1", "NR4A2"):
        if p not in arr:
            continue
        xs, dd, ee = [], [], []
        for i, d, s in arr[p]:
            k = int(i)
            if k in td:
                xs.append(k); dd.append(td[k][0] - d); ee.append((td[k][1] ** 2 + s ** 2) ** 0.5)
        xs, dd, ee = np.array(xs), np.array(dd), np.array(ee)
        sd_p = honest_sd(p)
        hsd = ((sd_t or 0) ** 2 + (sd_p or 0) ** 2) ** 0.5 if (sd_t or sd_p) else None
        unc = f"{hsd:.2f}" if hsd else f"{ee[-1]:.2f}"
        band(b, xs, dd, ee, COL[p], f"NR4A3 − {p}  ({dd[-1]:+.2f} ± {unc})")
        if hsd:
            b.errorbar(xs[-1] + 6, dd[-1], yerr=hsd, fmt="o", ms=4, color=COL[p],
                       capsize=4, elinewidth=1.6, capthick=1.6)
b.axhline(0, color="#666", lw=0.9, ls="--")
b.text(0.98, 0.03, "below 0 = NR4A3-selective", transform=b.transAxes,
       ha="right", va="bottom", fontsize=8, color="#333", style="italic")
b.set_xlabel("MBAR iteration"); b.set_ylabel("ΔΔG (kcal/mol)")
b.set_title("B. Selectivity vs paralogues")
b.legend(frameon=False, fontsize=9, title="pair (final ΔΔG ± block-SD)")
b.grid(alpha=0.15)

fig.suptitle(TITLE, fontsize=12, y=1.03)
fig.text(0.5, -0.02, "shaded band = MBAR statistical SE (precision, shrinks ~1/√N) · capped bar = "
                     "block-SD drift-aware uncertainty (the honest error)", ha="center", fontsize=8.5,
         color="#444")
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"wrote {OUT}  ({', '.join(f'{r}:{len(arr[r])}pts sd={honest_sd(r)}' for r in arr)})")
