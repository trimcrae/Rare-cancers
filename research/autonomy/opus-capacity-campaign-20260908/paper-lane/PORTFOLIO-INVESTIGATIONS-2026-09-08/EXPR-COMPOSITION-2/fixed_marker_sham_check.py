#!/usr/bin/env python3
"""EXPR-COMPOSITION-2 check 02 — specificity of the CORRECTED (fixed 14-marker) score.

Section D of complete_markers_recompute.py showed that the generic regression predicts
the fixed-marker score's adjusted rate almost exactly. A regression prediction at a single
x is a weak instrument, so this check does the direct, non-parametric version: shams
matched on label correlation to the FIXED score (not to the published NaN-skipping C),
plus a prediction interval for the regression point used in the decomposition.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("N_PERM", "1")     # section C's null is not needed here
os.environ.setdefault("N_SHAM", "300")
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import complete_markers_recompute as R   # re-runs sections A-D silently

P1, P2 = R.P1, R.P2
labs = {p: R.label_of(p) for p in (P1, P2)}
G = len(R.frames()["primary"][0])
syms, src = R.frames()["primary"]
Zp = {p: R.build_matrix(p, syms, src)[0] for p in (P1, P2)}
mset = set(R.MARKERS) | set(R.EXCLUDED)
cand = [i for i, s in enumerate(syms) if s not in mset
        and np.all(np.isfinite(Zp[P1][i])) and np.all(np.isfinite(Zp[P2][i]))]
grp0 = {p: R.build_groups(Zp[p], syms, {"C": R.scores[p]["C"]}, lambda s: "C") for p in (P1, P2)}


def adj_rate(c1, c2):
    ru1, ra1 = R.r_vectors(grp0[P1], G, labs[P1], {"C": c1})
    ru2, ra2 = R.r_vectors(grp0[P2], G, labs[P2], {"C": c2})
    return R.rates(ru1, ru2, ra1, ra2)


rng = np.random.default_rng(R.SHAM_SEED)
rows = []
for _ in range(int(os.environ["N_SHAM"])):
    pick = rng.choice(cand, size=20, replace=False)
    s1 = np.mean(Zp[P1][pick], axis=0)
    s2 = np.mean(Zp[P2][pick], axis=0)
    _, ra, _ = adj_rate(s1, s2)
    rows.append((R.spear(s1, labs[P1]), R.spear(s2, labs[P2]), ra))
rows = np.array(rows)

for tag, key in (("published NaN-skipping C", "C"), ("FIXED 14-marker C", "C_fixed")):
    c1, c2 = R.scores[P1][key], R.scores[P2][key]
    r1, r2 = R.spear(c1, labs[P1]), R.spear(c2, labs[P2])
    u, a, n = adj_rate(c1, c2)
    print("\n%s : label r %+.4f / %+.4f ; unadjusted %.4f -> adjusted %.4f "
          "(attenuation of excess %.4f)" % (tag, r1, r2, u, a, (u - a) / (u - 0.5)))
    for band in (0.10, 0.15, 0.20):
        sel = ((np.abs(np.abs(rows[:, 0]) - abs(r1)) <= band)
               & (np.abs(np.abs(rows[:, 1]) - abs(r2)) <= band))
        k = int(sel.sum())
        if k == 0:
            print("   band +-%.2f : 0 matched shams" % band)
            continue
        sub = rows[sel]
        le = int((sub[:, 2] <= a).sum())
        print("   band +-%.2f : n=%2d matched shams, adjusted rate mean %.4f min %.4f ; "
              "%d attenuate at least as much as the real score ; one-sided p=%.4f"
              % (band, k, sub[:, 2].mean(), sub[:, 2].min(), le, (le + 1) / (k + 1)))

# prediction interval for the generic regression point
x = (np.abs(rows[:, 0]) + np.abs(rows[:, 1])) / 2
y = rows[:, 2]
b = np.polyfit(x, y, 1)
resid = y - np.polyval(b, x)
s = float(np.sqrt((resid ** 2).sum() / (len(y) - 2)))
xbar, sxx = x.mean(), float(((x - x.mean()) ** 2).sum())
print("\nregression adjusted_rate ~ mean|label r| : slope %.4f intercept %.4f  "
      "residual sd %.4f  n=%d" % (b[0], b[1], s, len(y)))
for tag, key in (("published C", "C"), ("FIXED 14-marker C", "C_fixed")):
    c1, c2 = R.scores[P1][key], R.scores[P2][key]
    xs = (abs(R.spear(c1, labs[P1])) + abs(R.spear(c2, labs[P2]))) / 2
    fit = float(np.polyval(b, xs))
    se_mean = s * np.sqrt(1.0 / len(y) + (xs - xbar) ** 2 / sxx)
    _, a, _ = adj_rate(c1, c2)
    print("   %-18s x=%.3f  generic fit %.4f (95%% CI for the mean %.4f-%.4f)  "
          "observed %.4f  gap %+.4f  = %.1f residual sd"
          % (tag, xs, fit, fit - 1.96 * se_mean, fit + 1.96 * se_mean, a, a - fit,
             (a - fit) / s))
