#!/usr/bin/env python3
"""EXPR-COMPOSITION-2 — independent re-derivation of the assessor's defect and qualification,
and the complete-markers-only recomputation of the EXPR-COMPOSITION headline.

Independent of ../EXPR-COMPOSITION/composition_adjusted_contrast.py: this file imports
nothing from the lane. Ranks and correlations come from scipy.stats. Only the frozen input
JSON, the frozen marker list and the frozen frame definitions are taken from the lane.

Sections
  A  per-marker missingness on both platforms; count-vs-label correlation
  B  complete-markers-only composition score and its label correlation
  C  headline recomputed with a FIXED marker set on every sample (no NaN-skipping)
  D  label-correlation-matched sham covariates: the generic-attenuation regression
"""
import json, os, sys
import numpy as np
from scipy.stats import rankdata as sp_rank, spearmanr

REPO = "/home/user/Rare-cancers"
SRC = os.path.join(REPO, "research/modalities/emc-expression-panels.json")
P1 = "GSE24369_series_matrix.txt.gz"          # GPL6244
P2 = "GSE4303-GPL3290_series_matrix.txt.gz"   # GPL3290
SEED = 20260909
N_PERM = int(os.environ.get("N_PERM", "2000"))
SHAM_SEED = 4242
N_SHAM = int(os.environ.get("N_SHAM", "300"))

STROMAL = ["COL1A1", "COL1A2", "COL3A1", "DCN", "LUM", "FN1", "POSTN", "THY1",
           "FAP", "PDGFRB", "ACTA2", "PECAM1", "VWF"]
IMMUNE = ["PTPRC", "CD68", "CD3E", "CD8A", "MS4A1", "HLA-DRA", "B2M"]
MARKERS = STROMAL + IMMUNE
EXCLUDED = ["MKI67", "EPCAM"]

d = json.load(open(SRC))


def cols_of(pkey):
    p = d["platforms"][pkey]
    e, c = list(p["EMC_gsms"]), list(p["comparator_gsms"])
    return e + c, len(e), len(c)


def label_of(pkey):
    _, ne, nc = cols_of(pkey)
    return np.array([1.0] * ne + [0.0] * nc)


def marker_matrix(pkey):
    cols, _, _ = cols_of(pkey)
    M = {}
    for sym in MARKERS + EXCLUDED:
        per = {r["gsm"]: r.get("z_vs_array") for r in d["gene_reads"][sym][pkey]["per_sample"]}
        M[sym] = np.array([np.nan if per.get(g) is None else per[g] for g in cols], float)
    return M, cols


def build_matrix(pkey, symbols, source):
    cols, ne, nc = cols_of(pkey)
    Z = np.full((len(symbols), len(cols)), np.nan)
    if source == "background":
        gsms = d["background_reads"][pkey]["gsms"]
        pos = {g: i for i, g in enumerate(gsms)}
        take = [pos.get(g) for g in cols]
        zz = d["background_reads"][pkey]["z"]
        for gi, sym in enumerate(symbols):
            row = zz[sym]
            for si, p in enumerate(take):
                if p is not None and row[p] is not None:
                    Z[gi, si] = row[p]
    else:
        for gi, sym in enumerate(symbols):
            per = {r["gsm"]: r.get("z_vs_array") for r in d["gene_reads"][sym][pkey]["per_sample"]}
            for si, g in enumerate(cols):
                v = per.get(g)
                if v is not None:
                    Z[gi, si] = v
    return Z, ne, nc


def frames():
    b1, b2 = d["background_reads"][P1]["z"], d["background_reads"][P2]["z"]
    prim = sorted(set(b1) & set(b2))
    cur = sorted(g for g, v in d["gene_reads"].items()
                 if v.get(P1, {}).get("readable") and v.get(P2, {}).get("readable"))
    return {"primary": (prim, "background"), "secondary": (cur, "curated")}


def spear(a, b):
    return float(spearmanr(a, b).statistic)


# ---------------------------------------------------------------- vectorised rank machinery
def _norm(R):
    R = R - R.mean(axis=1, keepdims=True)
    sd = R.std(axis=1)
    sd = np.where(sd == 0, np.nan, sd)
    return R / sd[:, None]


def build_groups(Z, syms, cov_lookup, keyfn):
    bucket = {}
    for i in range(Z.shape[0]):
        ck = keyfn(syms[i])
        I = np.flatnonzero(np.isfinite(Z[i]) & np.isfinite(cov_lookup[ck]))
        if I.size < 5:
            continue
        bucket.setdefault((tuple(I.tolist()), ck), []).append(i)
    out = []
    for (It, ck), gidx in bucket.items():
        I = np.array(It)
        R = np.array([sp_rank(Z[i][I]) for i in gidx], float)
        out.append((I, np.array(gidx), _norm(R), ck))
    return out


def r_vectors(groups, G, lab, cov_lookup):
    """(unadjusted spearman r, composition-adjusted partial rank r) for all G genes"""
    ru = np.full(G, np.nan)
    ra = np.full(G, np.nan)
    for I, gidx, A, ck in groups:
        n = I.size
        l = lab[I].astype(float)
        if l.std() == 0:
            continue
        lh = (l - l.mean()) / l.std()
        c = sp_rank(cov_lookup[ck][I])
        if c.std() == 0:
            continue
        ch = (c - c.mean()) / c.std()
        r_gl = A @ lh / n
        r_gc = A @ ch / n
        r_lc = float(ch @ lh / n)
        den = np.sqrt(np.clip((1 - r_gc ** 2) * (1 - r_lc ** 2), 1e-15, None))
        ru[gidx] = r_gl
        ra[gidx] = (r_gl - r_gc * r_lc) / den
    return ru, ra


def rates(ru1, ru2, ra1, ra2):
    both = np.isfinite(ru1) & np.isfinite(ru2) & np.isfinite(ra1) & np.isfinite(ra2)
    n = int(both.sum())
    u = float(((ru1 > 0) == (ru2 > 0))[both].sum()) / n
    a = float(((ra1 > 0) == (ra2 > 0))[both].sum()) / n
    return u, a, n


def excess_atten(u, a):
    return (u - a) / (u - 0.5)


print("=" * 78)
print("A. PER-MARKER MISSINGNESS OF z_vs_array ON THE LABELLED SAMPLES")
print("=" * 78)
mm = {}
for pkey, tag in ((P1, "GPL6244"), (P2, "GPL3290")):
    M, cols = marker_matrix(pkey)
    mm[pkey] = (M, cols)
    _, ne, nc = cols_of(pkey)
    print("\n%s : %d labelled samples (EMC %d / comparator %d); prereg sec.2 claims all 22 "
          "markers complete" % (tag, len(cols), ne, nc))
    bad = []
    for sym in MARKERS + EXCLUDED:
        k = int(np.sum(~np.isfinite(M[sym])))
        if k:
            in_emc = int(np.sum(~np.isfinite(M[sym][:ne])))
            bad.append((sym, k, in_emc))
    if not bad:
        print("   all 22 markers complete on all samples -- claim HOLDS here")
    for sym, k, ie in sorted(bad, key=lambda x: -x[1]):
        print("   %-8s missing on %2d of %2d samples (%d of them in the EMC arm)"
              % (sym, k, len(cols), ie))
    A20 = np.array([M[s] for s in MARKERS])
    kcount = np.sum(np.isfinite(A20), axis=0)
    lab = label_of(pkey)
    print("   markers entering the NaN-skipping score C per sample: min %d max %d "
          "(EMC arm mean %.2f, comparator arm mean %.2f)"
          % (kcount.min(), kcount.max(), kcount[:ne].mean(), kcount[ne:].mean()))
    if kcount.min() != kcount.max():
        print("   spearman(marker count entering C, EMC label) = %+.4f"
              % spear(kcount.astype(float), lab))
    else:
        print("   spearman(marker count entering C, EMC label) = undefined (count is constant)")

print()
print("=" * 78)
print("B. COMPLETE-MARKERS-ONLY COMPOSITION SCORE")
print("=" * 78)
complete = {}
for pkey, tag in ((P1, "GPL6244"), (P2, "GPL3290")):
    M, cols = mm[pkey]
    complete[pkey] = [s for s in MARKERS if np.all(np.isfinite(M[s]))]
    print("%s: %d of 20 primary markers complete" % (tag, len(complete[pkey])))
FIXED = [s for s in MARKERS if s in complete[P1] and s in complete[P2]]
print("\nFIXED marker set complete on EVERY labelled sample of BOTH platforms: %d markers"
      % len(FIXED))
print("  kept:    %s" % ", ".join(FIXED))
print("  dropped: %s" % ", ".join([s for s in MARKERS if s not in FIXED]))

scores = {}
for pkey, tag in ((P1, "GPL6244"), (P2, "GPL3290")):
    M, cols = mm[pkey]
    lab = label_of(pkey)
    C_nan = np.nanmean(np.array([M[s] for s in MARKERS]), axis=0)      # published, NaN-skipping
    C_pl = np.mean(np.array([M[s] for s in complete[pkey]]), axis=0)   # per-platform complete set
    C_fix = np.mean(np.array([M[s] for s in FIXED]), axis=0)           # one fixed set everywhere
    scores[pkey] = {"C": C_nan, "C_platform_complete": C_pl, "C_fixed": C_fix}
    kc = np.sum(np.isfinite(np.array([M[s] for s in MARKERS])), axis=0)
    print("\n%s  spearman with EMC label:" % tag)
    print("   published NaN-skipping C (20 markers, %d-%d per sample) = %+.4f"
          % (kc.min(), kc.max(), spear(C_nan, lab)))
    print("   platform-complete-markers-only C (%2d markers)        = %+.4f   (corr with C %+.4f)"
          % (len(complete[pkey]), spear(C_pl, lab), spear(C_nan, C_pl)))
    print("   FIXED-both-platforms C (%2d markers)                  = %+.4f   (corr with C %+.4f)"
          % (len(FIXED), spear(C_fix, lab), spear(C_nan, C_fix)))

print()
print("=" * 78)
print("C. HEADLINE RECOMPUTED WITH A FIXED MARKER SET ON EVERY SAMPLE")
print("=" * 78)
print("Convention: no leave-one-out, applied identically to every covariate (this convention"
      "\nreproduces the lane's published 0.6521 -> 0.5668 exactly, so it is not doing the work).")
F = frames()
results = {}
for fname in ("primary", "secondary"):
    syms, src = F[fname]
    packs = {}
    for pkey in (P1, P2):
        Z, ne, nc = build_matrix(pkey, syms, src)
        packs[pkey] = (Z, np.array([1.0] * ne + [0.0] * nc))
    print("\n--- frame: %s (%d genes in frame, source=%s)" % (fname, len(syms), src))
    results[fname] = {}
    for cov_name in ("C", "C_platform_complete", "C_fixed"):
        lut = {p: {"C": scores[p][cov_name]} for p in (P1, P2)}
        grp = {p: build_groups(packs[p][0], syms, lut[p], lambda s: "C") for p in (P1, P2)}
        G = len(syms)
        ru1, ra1 = r_vectors(grp[P1], G, packs[P1][1], lut[P1])
        ru2, ra2 = r_vectors(grp[P2], G, packs[P2][1], lut[P2])
        u, a, n = rates(ru1, ru2, ra1, ra2)
        results[fname][cov_name] = dict(u=u, a=a, n=n, atten=excess_atten(u, a),
                                        grp=grp, lut=lut, packs=packs, G=G)
        print("   covariate %-20s n=%d  unadjusted %.4f -> adjusted %.4f  "
              "drop %.4f  attenuation of excess %.4f"
              % (cov_name, n, u, a, u - a, excess_atten(u, a)))

print("\n--- label-permutation null with the FIXED marker set (%d permutations, seed %d)"
      % (N_PERM, SEED))
for fname in ("primary", "secondary"):
    R = results[fname]["C_fixed"]
    rng = np.random.default_rng(SEED)
    perm = []
    for _ in range(N_PERM):
        q = []
        for p in (P1, P2):
            lab = R["packs"][p][1]
            l = lab[rng.permutation(lab.size)]
            q.append(r_vectors(R["grp"][p], R["G"], l, R["lut"][p]))
        both = np.isfinite(q[0][1]) & np.isfinite(q[1][1])
        perm.append(float(((q[0][1] > 0) == (q[1][1] > 0))[both].sum()) / int(both.sum()))
    perm = np.array(perm)
    pv = (int((perm >= R["a"]).sum()) + 1) / (len(perm) + 1)
    print("   %-9s adjusted rate %.4f   permuted mean %.4f sd %.4f   p = %.4f  (%d/%d >= observed)"
          % (fname, R["a"], perm.mean(), perm.std(ddof=1), pv,
             int((perm >= R["a"]).sum()), len(perm)))

print()
print("=" * 78)
print("D. LABEL-CORRELATION-MATCHED SHAM COVARIATES (independent re-run)")
print("=" * 78)
syms, src = F["primary"]
Zp = {p: build_matrix(p, syms, src)[0] for p in (P1, P2)}
labs = {p: label_of(p) for p in (P1, P2)}
mset = set(MARKERS) | set(EXCLUDED)
cand = [i for i, s in enumerate(syms) if s not in mset
        and np.all(np.isfinite(Zp[P1][i])) and np.all(np.isfinite(Zp[P2][i]))]
print("sham candidate genes (primary frame, non-marker, complete on both platforms): %d of %d"
      % (len(cand), len(syms)))
G = len(syms)
grp0 = {p: build_groups(Zp[p], syms, {"C": scores[p]["C"]}, lambda s: "C") for p in (P1, P2)}


def adj_rate(c1, c2):
    ru1, ra1 = r_vectors(grp0[P1], G, labs[P1], {"C": c1})
    ru2, ra2 = r_vectors(grp0[P2], G, labs[P2], {"C": c2})
    return rates(ru1, ru2, ra1, ra2)


rC1, rC2 = spear(scores[P1]["C"], labs[P1]), spear(scores[P2]["C"], labs[P2])
u0, a0, n0 = adj_rate(scores[P1]["C"], scores[P2]["C"])
print("REAL C: label spearman %+.3f / %+.3f   unadjusted %.4f -> adjusted %.4f (n=%d)"
      % (rC1, rC2, u0, a0, n0))
rng = np.random.default_rng(SHAM_SEED)
rows = []
for _ in range(N_SHAM):
    pick = rng.choice(cand, size=20, replace=False)
    s1 = np.mean(Zp[P1][pick], axis=0)
    s2 = np.mean(Zp[P2][pick], axis=0)
    if s1.std() == 0 or s2.std() == 0:
        continue
    _, ra, _ = adj_rate(s1, s2)
    rows.append((spear(s1, labs[P1]), spear(s2, labs[P2]), ra))
rows = np.array(rows)
print("%d shams (seed %d): adjusted rate mean %.4f sd %.4f min %.4f max %.4f; %d/%d <= real %.4f"
      % (len(rows), SHAM_SEED, rows[:, 2].mean(), rows[:, 2].std(ddof=1), rows[:, 2].min(),
         rows[:, 2].max(), int((rows[:, 2] <= a0).sum()), len(rows), a0))
for band in (0.10, 0.15, 0.20):
    sel = ((np.abs(np.abs(rows[:, 0]) - abs(rC1)) <= band)
           & (np.abs(np.abs(rows[:, 1]) - abs(rC2)) <= band))
    k = int(sel.sum())
    sub = rows[sel]
    if k == 0:
        print("   band +-%.2f : 0 shams" % band)
        continue
    print("   band +-%.2f : n=%2d  mean %.4f  min %.4f  n<=real %d  one-sided p=%.4f"
          % (band, k, sub[:, 2].mean(), sub[:, 2].min(), int((sub[:, 2] <= a0).sum()),
             (int((sub[:, 2] <= a0).sum()) + 1) / (k + 1)))
x = (np.abs(rows[:, 0]) + np.abs(rows[:, 1])) / 2
b = np.polyfit(x, rows[:, 2], 1)
xC = (abs(rC1) + abs(rC2)) / 2
gen = float(np.polyval(b, xC))
print("\n   regression adjusted_rate ~ mean|label r|: slope %.4f intercept %.4f r=%.3f"
      % (b[0], b[1], np.corrcoef(x, rows[:, 2])[0, 1]))
print("   generic prediction at the real score's mean|label r|=%.3f : %.4f (observed %.4f)"
      % (xC, gen, a0))
print("   total drop %.4f = generic %.4f + composition-specific %.4f"
      % (u0 - a0, u0 - gen, gen - a0))
print("   attenuation of the excess over 0.5: total %.4f | generic %.4f | specific %.4f"
      % (excess_atten(u0, a0), excess_atten(u0, gen), (gen - a0) / (u0 - 0.5)))

aF = results["primary"]["C_fixed"]["a"]
uF = results["primary"]["C_fixed"]["u"]
rF1 = spear(scores[P1]["C_fixed"], labs[P1])
rF2 = spear(scores[P2]["C_fixed"], labs[P2])
xF = (abs(rF1) + abs(rF2)) / 2
genF = float(np.polyval(b, xF))
print("\n   FIXED-marker score: label r %+.3f / %+.3f (mean |r| %.3f); generic prediction %.4f"
      % (rF1, rF2, xF, genF))
print("   FIXED-marker: total drop %.4f = generic %.4f + specific %.4f"
      % (uF - aF, uF - genF, genF - aF))
print("   FIXED-marker attenuation of excess: total %.4f | generic %.4f | specific %.4f"
      % (excess_atten(uF, aF), excess_atten(uF, genF), (genF - aF) / (uF - 0.5)))
