"""Independent recomputation of EXPR-COMPOSITION's headline numbers with scipy,
using a copy of the lane's data-loading code but scipy's own Spearman and an
OLS-residual partial correlation instead of the lane's hand-rolled formulas."""
import json, os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "EXPR-COMPOSITION"))
import composition_adjusted_contrast as m
from scipy.stats import spearmanr

d = json.load(open(m.SRC))
F = m.frames(d)
cs = {}
for pkey in (m.P1, m.P2):
    plat = d["platforms"][pkey]
    cols = list(plat["EMC_gsms"]) + list(plat["comparator_gsms"])
    cs[pkey] = m.composition_scores(d, pkey, cols)

# 1. composition score vs label, scipy
for pkey, tag in ((m.P1, "GPL6244"), (m.P2, "GPL3290")):
    plat = d["platforms"][pkey]
    ne, nc = len(plat["EMC_gsms"]), len(plat["comparator_gsms"])
    lab = np.array([1.0]*ne + [0.0]*nc)
    C = cs[pkey][1]["C"]; ok = np.isfinite(C)
    print("scipy spearman(C,label) %-8s = %+.4f   (lane: %s)" %
          (tag, spearmanr(C[ok], lab[ok]).statistic,
           {"GPL6244": "-0.5780", "GPL3290": "-0.5041"}[tag]))

def partial_scipy(g, lab, c):
    """rank partial via OLS residuals on ranks -- an independent route to the same quantity"""
    from scipy.stats import rankdata as rd
    R = np.vstack([rd(g), rd(lab), rd(c)]).astype(float)
    R = (R - R.mean(axis=1, keepdims=True))
    X = R[2]; X = X / np.linalg.norm(X)
    rg = R[0] - X*(R[0] @ X); rl = R[1] - X*(R[1] @ X)
    if rg.std() == 0 or rl.std() == 0: return np.nan
    return float(np.corrcoef(rg, rl)[0, 1])

for fname in ("primary", "secondary"):
    syms, src = F[fname]
    ru = {}; ra = {}
    for pkey in (m.P1, m.P2):
        plat = d["platforms"][pkey]
        ne, nc = len(plat["EMC_gsms"]), len(plat["comparator_gsms"])
        lab = np.array([1.0]*ne + [0.0]*nc)
        Z, _, _, _ = m.build_matrix(d, pkey, syms, src)
        M, S = cs[pkey]
        u = np.full(len(syms), np.nan); a = np.full(len(syms), np.nan)
        for i, sym in enumerate(syms):
            cvec = m.loo_score(M, sym, m.MARKERS) if sym in m.MARKERS else S["C"]
            ok = np.isfinite(Z[i]) & np.isfinite(cvec)
            if ok.sum() < 5 or len(set(lab[ok].tolist())) < 2: continue
            if np.std(Z[i][ok]) == 0: continue
            u[i] = spearmanr(Z[i][ok], lab[ok]).statistic
            a[i] = partial_scipy(Z[i][ok], lab[ok], cvec[ok])
        ru[pkey] = u; ra[pkey] = a
    both = np.isfinite(ru[m.P1]) & np.isfinite(ru[m.P2]) & np.isfinite(ra[m.P1]) & np.isfinite(ra[m.P2])
    n = int(both.sum())
    cu = float(((ru[m.P1] > 0) == (ru[m.P2] > 0))[both].sum())/n
    ca = float(((ra[m.P1] > 0) == (ra[m.P2] > 0))[both].sum())/n
    att = 1 - (ca-0.5)/(cu-0.5)
    pu = np.corrcoef(ru[m.P1][both], ru[m.P2][both])[0,1]
    pa = np.corrcoef(ra[m.P1][both], ra[m.P2][both])[0,1]
    print("%-10s scipy: n=%d  unadj %.4f -> adj %.4f  attenuation-of-excess %.4f  pearson %.4f -> %.4f"
          % (fname, n, cu, ca, att, pu, pa))
