import json, os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "EXPR-COMPOSITION"))
import composition_adjusted_contrast as m
d = json.load(open(m.SRC))
for pkey, tag in ((m.P1, "GPL6244"), (m.P2, "GPL3290")):
    plat = d["platforms"][pkey]
    emc, cmp_ = list(plat["EMC_gsms"]), list(plat["comparator_gsms"])
    cols = emc + cmp_; ne = len(emc)
    lab = np.array([1.0]*ne + [0.0]*len(cmp_))
    M, S = m.composition_scores(d, pkey, cols)
    A = np.array([M[s] for s in m.MARKERS])          # 20 x samples
    k = np.sum(np.isfinite(A), axis=0)               # markers contributing to C per sample
    print("\n%s  n=%d (EMC %d / comparator %d)" % (tag, len(cols), ne, len(cmp_)))
    print("  markers contributing to C per sample: min %d max %d" % (k.min(), k.max()))
    print("  mean #markers  EMC arm %.2f   comparator arm %.2f" % (k[:ne].mean(), k[ne:].mean()))
    print("  spearman(#markers used, EMC label) = %+.4f" % m.spearman(k.astype(float), lab))
    print("  spearman(C, EMC label)             = %+.4f" % m.spearman(S["C"], lab))
    print("  C finite for every sample? %s" % bool(np.all(np.isfinite(S["C"]))))
    # complete-marker-only score: the 20 markers with NO missingness on this platform
    keep = [s for s in m.MARKERS if np.all(np.isfinite(M[s]))]
    B = np.nanmean(np.array([M[s] for s in keep]), axis=0)
    print("  markers complete on this platform: %d of 20 (%s)" % (len(keep), ",".join(keep)))
    print("  spearman(C_complete_markers_only, EMC label) = %+.4f" % m.spearman(B, lab))
    print("  spearman(C, C_complete_markers_only)         = %+.4f" % m.spearman(S["C"], B))
    per = {r["gsm"]: r.get("z_vs_array") for r in d["gene_reads"]["DCN"][pkey]["per_sample"]}
    miss = [g for g in cols if per.get(g) is None]
    print("  DCN missing on %d samples; of those %d are in the EMC arm"
          % (len(miss), sum(1 for g in miss if g in emc)))
