"""ASSESS check: is the attenuation SPECIFIC to a composition-marker score, or does ANY
per-sample covariate that tracks the EMC label as strongly attenuate the concordance just
as much?  Sham scores = mean background z of 20 randomly drawn NON-marker genes, scored
with exactly the lane's own machinery (same frames, same partial correlation, same rate).
Comparison is made under a single no-leave-one-out convention for real C and shams alike."""
import json, os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "EXPR-COMPOSITION"))
import composition_adjusted_contrast as m

SEED = 4242
NDRAW = int(sys.argv[1]) if len(sys.argv) > 1 else 300
rng = np.random.default_rng(SEED)
d = json.load(open(m.SRC))
F = m.frames(d)
syms, src = F["primary"]
cs, packs, labs = {}, {}, {}
for pkey in (m.P1, m.P2):
    plat = d["platforms"][pkey]
    cols = list(plat["EMC_gsms"]) + list(plat["comparator_gsms"])
    cs[pkey] = m.composition_scores(d, pkey, cols)
    ne, nc = len(plat["EMC_gsms"]), len(plat["comparator_gsms"])
    labs[pkey] = np.array([1.0]*ne + [0.0]*nc)
    Z, _, _, _ = m.build_matrix(d, pkey, syms, src)
    packs[pkey] = Z

# candidate sham genes: in the primary frame, non-marker, complete per-sample background z on BOTH
markerset = set(m.MARKERS) | set(m.EXCLUDED)
cand = [i for i, s in enumerate(syms) if s not in markerset
        and np.all(np.isfinite(packs[m.P1][i])) and np.all(np.isfinite(packs[m.P2][i]))]
print("sham candidate genes (primary frame, non-marker, complete on both platforms): %d of %d"
      % (len(cand), len(syms)))

groups = {p: m.build_groups(packs[p], syms, {"C": cs[p][1]["C"]}, lambda s: "C") for p in (m.P1, m.P2)}
G = len(syms)

def rate_for(cov1, cov2):
    a1 = m.adjusted_r(groups[m.P1], G, labs[m.P1], {"C": cov1})
    a2 = m.adjusted_r(groups[m.P2], G, labs[m.P2], {"C": cov2})
    u1 = m.unadjusted_r(groups[m.P1], G, labs[m.P1])
    u2 = m.unadjusted_r(groups[m.P2], G, labs[m.P2])
    both = np.isfinite(u1) & np.isfinite(u2) & np.isfinite(a1) & np.isfinite(a2)
    n = int(both.sum())
    ru = float(((u1 > 0) == (u2 > 0))[both].sum())/n
    ra = float(((a1 > 0) == (a2 > 0))[both].sum())/n
    return ru, ra, n

C1, C2 = cs[m.P1][1]["C"], cs[m.P2][1]["C"]
rC1 = m.spearman(C1, labs[m.P1]); rC2 = m.spearman(C2, labs[m.P2])
ru, raC, n = rate_for(C1, C2)
print("REAL composition score C (no-LOO convention): label spearman %+.3f / %+.3f"
      "  unadjusted %.4f -> adjusted %.4f  (n=%d)" % (rC1, rC2, ru, raC, n))
print("  [lane's published LOO figures: 0.6521 -> 0.5668]\n")

rows = []
for _ in range(NDRAW):
    pick = rng.choice(cand, size=20, replace=False)
    s1 = np.nanmean(packs[m.P1][pick], axis=0); s2 = np.nanmean(packs[m.P2][pick], axis=0)
    if np.std(s1) == 0 or np.std(s2) == 0: continue
    l1 = m.spearman(s1, labs[m.P1]); l2 = m.spearman(s2, labs[m.P2])
    _, ra, _ = rate_for(s1, s2)
    rows.append((l1, l2, ra))
rows = np.array(rows)
print("%d sham scores drawn (seed %d)" % (len(rows), SEED))
print("  |label spearman| GPL6244: median %.3f  p90 %.3f  max %.3f"
      % (np.median(abs(rows[:,0])), np.quantile(abs(rows[:,0]),.9), abs(rows[:,0]).max()))
print("  adjusted rate over ALL shams: mean %.4f sd %.4f  min %.4f  max %.4f"
      % (rows[:,2].mean(), rows[:,2].std(ddof=1), rows[:,2].min(), rows[:,2].max()))
print("  n shams whose adjusted rate <= the real score's %.4f : %d / %d"
      % (raC, int((rows[:,2] <= raC).sum()), len(rows)))

for band in (0.10, 0.15, 0.20):
    sel = (np.abs(np.abs(rows[:,0]) - abs(rC1)) <= band) & (np.abs(np.abs(rows[:,1]) - abs(rC2)) <= band)
    k = int(sel.sum())
    if k == 0:
        print("  matched band +-%.2f on BOTH platforms: 0 shams" % band); continue
    sub = rows[sel]
    print("  matched band +-%.2f on BOTH platforms: n=%d  adjusted rate mean %.4f sd %.4f "
          "min %.4f   n<=real %d  one-sided p=%.4f"
          % (band, k, sub[:,2].mean(), sub[:,2].std(ddof=1) if k > 1 else float('nan'),
             sub[:,2].min(), int((sub[:,2] <= raC).sum()),
             (int((sub[:,2] <= raC).sum())+1)/(k+1)))
# regression of adjusted rate on |label correlation|
x = (np.abs(rows[:,0]) + np.abs(rows[:,1]))/2
b = np.polyfit(x, rows[:,2], 1)
print("\n  adjusted_rate ~ mean|label spearman of the covariate|:  slope %.4f  intercept %.4f  r=%.3f"
      % (b[0], b[1], np.corrcoef(x, rows[:,2])[0,1]))
print("  predicted adjusted rate at the real score's mean |label r| = %.3f : %.4f   (real: %.4f)"
      % ((abs(rC1)+abs(rC2))/2, np.polyval(b, (abs(rC1)+abs(rC2))/2), raC))
