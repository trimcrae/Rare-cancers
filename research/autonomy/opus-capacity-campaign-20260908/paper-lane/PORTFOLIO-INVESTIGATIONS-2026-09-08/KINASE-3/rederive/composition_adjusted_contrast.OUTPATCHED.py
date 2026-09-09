#!/usr/bin/env python3
"""EXPR-COMPOSITION: is the broad two-platform EMC expression contrast tumour/stroma
composition, or EMC biology?

Rank-based composition adjustment of the contrast KINASE-2 validated. Everything that
governs the answer -- the 22-symbol marker list, the primary 20-marker score, the
leave-one-out rule, the seed, the permutation counts, the statistics and the ordering --
is frozen in PREREGISTRATION.md, written before any statistic was read.

Order, enforced here and not overridable by a flag:
  1. KNOWN-ANSWER GATE against ../KINASE-2/label-permutation-vs-gene-resampling-null.json.
     0 mismatches required; exit 2 otherwise, computing no adjustment.
  2. NEGATIVE CONTROL: a permuted composition score must not attenuate.
  3. The adjusted statistics and their label-permutation null, both frames.

"Composition score" means the frozen marker-transcript score of PREREGISTRATION.md sec.2.
It is not a measured cell fraction. Nothing here is an efficacy, safety, selectivity,
therapeutic-window, target-attribution or clinical-readiness claim.
"""
import json, os, sys, time
import numpy as np

REPO = "/home/user/Rare-cancers"
SRC = os.path.join(REPO, "research/modalities/emc-expression-panels.json")
HERE = "/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/EXPR-COMPOSITION"
K2 = os.path.join(HERE, "..", "KINASE-2", "label-permutation-vs-gene-resampling-null.json")
OUT = "/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/KINASE-3/rederive/composition-adjusted-contrast.REDERIVED.json"

P1 = "GSE24369_series_matrix.txt.gz"          # GPL6244
P2 = "GSE4303-GPL3290_series_matrix.txt.gz"   # GPL3290

SEED = 20260909
N_PERM = 2000
N_PERM_COMP_NC = 500
PREREG_SHA = "6386ac165562140e7bfeb1eb83944a2f17b3f057943c21d9b843b021041ec8ad"

STROMAL = ["COL1A1", "COL1A2", "COL3A1", "DCN", "LUM", "FN1", "POSTN", "THY1",
           "FAP", "PDGFRB", "ACTA2", "PECAM1", "VWF"]
IMMUNE = ["PTPRC", "CD68", "CD3E", "CD8A", "MS4A1", "HLA-DRA", "B2M"]
MARKERS = STROMAL + IMMUNE                     # the 20-marker primary score
EXCLUDED = ["MKI67", "EPCAM"]                  # frozen out of the primary score

LEADS = ["RET", "SGK1", "NDRG1", "ALK", "ROS1", "PRKDC", "XRCC5", "XRCC6",
         "NR4A3", "EGFR", "GFRA1", "GFRA2", "GDNF", "HDAC3"]


# ----------------------------------------------------------------- KINASE-2 code path
def build_matrix(d, pkey, symbols, source):
    plat = d["platforms"][pkey]
    emc, cmp_ = list(plat["EMC_gsms"]), list(plat["comparator_gsms"])
    cols = emc + cmp_
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
    return Z, len(emc), len(cmp_), cols


def welch_t(Z, a_idx, b_idx):
    A, B = Z[:, a_idx], Z[:, b_idx]
    out = np.full(Z.shape[0], np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        na = np.sum(~np.isnan(A), axis=1); nb = np.sum(~np.isnan(B), axis=1)
        ma = np.nanmean(A, axis=1); mb = np.nanmean(B, axis=1)
        va = np.nanvar(A, axis=1, ddof=1); vb = np.nanvar(B, axis=1, ddof=1)
        se2 = va / na + vb / nb
        ok = (na >= 2) & (nb >= 2) & np.isfinite(se2) & (se2 > 0)
        out[ok] = (ma[ok] - mb[ok]) / np.sqrt(se2[ok])
    return out


def concordance(t1, t2):
    ok = np.isfinite(t1) & np.isfinite(t2)
    conc = ok & ((t1 > 0) == (t2 > 0))
    return ok, conc, np.minimum(np.abs(t1), np.abs(t2))


def frames(d):
    bg1, bg2 = d["background_reads"][P1]["z"], d["background_reads"][P2]["z"]
    prim = sorted(set(bg1) & set(bg2))
    cur = sorted(g for g, v in d["gene_reads"].items()
                 if v.get(P1, {}).get("readable") and v.get(P2, {}).get("readable"))
    return {"primary": (prim, "background"), "secondary": (cur, "curated")}


# ----------------------------------------------------------------- gate
def known_answer_gate(d, k2):
    """Recompute KINASE-2's OBSERVED statistics. Returns (n_checked, mismatches[])."""
    mism, nchk = [], 0

    def cmp_(label, got, want, tol):
        nonlocal nchk
        nchk += 1
        if want is None or got is None or not np.isfinite(np.float64(got)):
            mism.append({"field": label, "recomputed": got, "kinase2": want,
                         "reason": "undefined"})
            return
        if abs(float(got) - float(want)) > tol:
            mism.append({"field": label, "recomputed": float(got), "kinase2": float(want),
                         "delta": float(got) - float(want), "tol": tol})

    packs = {}
    for fname, (syms, src) in frames(d).items():
        Z1, n1e, n1c, _ = build_matrix(d, P1, syms, src)
        Z2, n2e, n2c, _ = build_matrix(d, P2, syms, src)
        t1 = welch_t(Z1, np.arange(n1e), np.arange(n1e, n1e + n1c))
        t2 = welch_t(Z2, np.arange(n2e), np.arange(n2e, n2e + n2c))
        ok, conc, mn = concordance(t1, t2)
        n_ok = int(ok.sum())
        rep = k2["frames"][fname]
        g = rep["gene_resampling_null"]
        cmp_(fname + ".n_genes_scored_on_both_platforms", n_ok,
             rep["n_genes_scored_on_both_platforms"], 0)
        cmp_(fname + ".n_concordant", int(conc.sum()), g["n_concordant"], 0)
        cmp_(fname + ".concordance_rate", conc.sum() / n_ok, g["concordance_rate"], 5e-5)
        cmp_(fname + ".pearson_r_t1_t2",
             np.corrcoef(t1[ok], t2[ok])[0, 1], g["pearson_r_t1_t2"], 5e-5)
        rk1 = np.argsort(np.argsort(t1[ok])); rk2 = np.argsort(np.argsort(t2[ok]))
        cmp_(fname + ".spearman_r_t1_t2",
             np.corrcoef(rk1, rk2)[0, 1], g["spearman_r_t1_t2"], 5e-5)
        for k, p in (("p50", .5), ("p75", .75), ("p90", .90), ("p95", .95), ("p99", .99)):
            cmp_(fname + ".min_abs_t_quantiles_among_concordant." + k,
                 np.quantile(mn[conc], p),
                 g["min_abs_t_quantiles_among_concordant"][k], 5e-4)
        cmp_(fname + ".platform_arms.GPL6244.n_EMC", n1e,
             rep["platform_arms"]["GPL6244"]["n_EMC"], 0)
        cmp_(fname + ".platform_arms.GPL3290.n_EMC", n2e,
             rep["platform_arms"]["GPL3290"]["n_EMC"], 0)
        packs[fname] = {"ok": ok, "conc": conc, "min": mn, "n_ok": n_ok,
                        "symbols": syms, "t1": t1, "t2": t2}

    # thirteen placed lead genes, gene-resampling joint p on both frames (no RNG involved)
    pw1 = d["platforms"][P1]["genome_wide_null"]["placed_wanted_genes"]
    pw2 = d["platforms"][P2]["genome_wide_null"]["placed_wanted_genes"]
    for gene in LEADS:
        rec = k2["leads"][gene]
        a, b = pw1.get(gene), pw2.get(gene)
        if rec.get("placement_primary_frame") is None:
            nchk += 1
            if a is not None and b is not None:
                mism.append({"field": "leads." + gene + ".placement",
                             "recomputed": "placeable", "kinase2": None})
            continue
        m = min(abs(a["t"]), abs(b["t"]))
        cmp_("leads." + gene + ".min_abs_t", m, rec["min_abs_t"], 5e-4)
        nchk += 1
        if bool((a["t"] > 0) == (b["t"] > 0)) != bool(rec["concordant_direction"]):
            mism.append({"field": "leads." + gene + ".concordant_direction",
                         "recomputed": bool((a["t"] > 0) == (b["t"] > 0)),
                         "kinase2": rec["concordant_direction"]})
        for fname, key in (("primary", "placement_primary_frame"),
                           ("secondary", "placement_secondary_frame")):
            o = packs[fname]
            k_gene = int(np.sum(o["conc"] & (o["min"] >= m)))
            cmp_("leads." + gene + "." + key + ".n_null_genes", k_gene,
                 rec[key]["n_null_genes_at_least_this_concordant_and_strong"], 0)
            cmp_("leads." + gene + "." + key + ".joint_p_gene_resampling",
                 k_gene / o["n_ok"], rec[key]["joint_p_gene_resampling"], 5e-6)
    return nchk, mism, packs


# ----------------------------------------------------------------- rank statistics
def rankdata(x):
    """Average-rank of a 1-D array with no NaN."""
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x), float)
    r[order] = np.arange(1, len(x) + 1)
    # average ties
    xs = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    return r


def pear(a, b):
    if len(a) < 3:
        return np.nan
    sa, sb = a.std(), b.std()
    if sa == 0 or sb == 0:
        return np.nan
    return float(((a - a.mean()) * (b - b.mean())).mean() / (sa * sb))


def spearman(x, y):
    return pear(rankdata(x), rankdata(y))


def partial_rank(g, lab, covs):
    """First/second-order rank partial correlation of g with lab given covs (list of arrays)."""
    R = [rankdata(g), rankdata(lab)] + [rankdata(c) for c in covs]
    R = np.array(R)
    C = np.corrcoef(R)
    if not np.all(np.isfinite(C)):
        return np.nan
    try:
        P = np.linalg.inv(C)
    except np.linalg.LinAlgError:
        return np.nan
    d0 = P[0, 0] * P[1, 1]
    if d0 <= 0:
        return np.nan
    return float(-P[0, 1] / np.sqrt(d0))


def signed_t(r, n, k):
    if r is None or not np.isfinite(r):
        return np.nan
    df = n - k - 2
    if df <= 0 or abs(r) >= 1:
        return np.nan
    return float(r * np.sqrt(df / (1 - r * r)))


# ----------------------------------------------------------------- vectorised permutation core
# Mathematically identical to partial_rank() above, but the per-gene rank vectors and the
# gene-covariate correlation do not change across permutations, so they are computed once.
# Spearman with a BINARY label equals the Pearson correlation with the binary vector itself
# (rank of a two-valued vector is an affine function of it), so a permutation costs one
# matrix-vector product per group.  checks/05-vectorised-equivalence proves the agreement.

def _norm_rows(R):
    R = R - R.mean(axis=1, keepdims=True)
    sd = R.std(axis=1)
    sd[sd == 0] = np.nan
    return R / sd[:, None]


class Group:
    """Genes sharing a sample-availability pattern AND a covariate vector."""
    __slots__ = ("I", "gidx", "A", "covkey")

    def __init__(self, I, gidx, A, covkey):
        self.I, self.gidx, self.A, self.covkey = I, gidx, A, covkey


def build_groups(Z, syms, cov_lookup, cov_key_for_gene):
    groups, bucket = [], {}
    for i in range(Z.shape[0]):
        ck = cov_key_for_gene(syms[i])
        c = cov_lookup[ck]
        I = np.flatnonzero(np.isfinite(Z[i]) & np.isfinite(c))
        if I.size < 5:
            continue
        bucket.setdefault((tuple(I.tolist()), ck), []).append(i)
    for (Ituple, ck), gidx in bucket.items():
        I = np.array(Ituple)
        R = np.array([rankdata(Z[i][I]) for i in gidx], float)
        groups.append(Group(I, np.array(gidx), _norm_rows(R), ck))
    return groups


def adjusted_r(groups, G, lab, cov_lookup):
    """Vector of composition-adjusted partial r for all G genes (NaN where unscorable)."""
    out = np.full(G, np.nan)
    for g in groups:
        n = g.I.size
        l = lab[g.I].astype(float)
        if l.std() == 0:
            continue
        lh = (l - l.mean()) / l.std()
        c = rankdata(cov_lookup[g.covkey][g.I])
        if c.std() == 0:
            continue
        ch = (c - c.mean()) / c.std()
        r_gl = g.A @ lh / n
        r_gc = g.A @ ch / n
        r_lc = float(ch @ lh / n)
        den = np.sqrt(np.clip((1 - r_gc ** 2) * (1 - r_lc ** 2), 1e-15, None))
        out[g.gidx] = (r_gl - r_gc * r_lc) / den
    return out


def unadjusted_r(groups, G, lab):
    out = np.full(G, np.nan)
    for g in groups:
        n = g.I.size
        l = lab[g.I].astype(float)
        if l.std() == 0:
            continue
        lh = (l - l.mean()) / l.std()
        out[g.gidx] = g.A @ lh / n
    return out


def conc_rate(r1, r2):
    o = np.isfinite(r1) & np.isfinite(r2)
    if o.sum() == 0:
        return np.nan, 0
    return float((o & ((r1 > 0) == (r2 > 0))).sum()) / float(o.sum()), int(o.sum())


# ----------------------------------------------------------------- composition score
def composition_scores(d, pkey, cols):
    """Per-sample marker z matrix (markers x samples) for the frozen list, plus scores."""
    M = {}
    for sym in MARKERS + EXCLUDED:
        per = {r["gsm"]: r.get("z_vs_array") for r in d["gene_reads"][sym][pkey]["per_sample"]}
        M[sym] = np.array([per.get(g, np.nan) if per.get(g) is not None else np.nan
                           for g in cols], float)
    def mean_over(syms):
        A = np.array([M[s] for s in syms])
        with np.errstate(invalid="ignore"):
            return np.nanmean(A, axis=0)
    return M, {"C": mean_over(MARKERS), "C_stromal": mean_over(STROMAL),
               "C_immune": mean_over(IMMUNE), "MKI67": M["MKI67"], "EPCAM": M["EPCAM"]}


def loo_score(M, gene, base_syms):
    syms = [s for s in base_syms if s != gene]
    with np.errstate(invalid="ignore"):
        return np.nanmean(np.array([M[s] for s in syms]), axis=0)


def gene_stats(z, lab, cvec, M, gene):
    """Unadjusted and adjusted rank statistics for one gene on one platform."""
    ok = np.isfinite(z) & np.isfinite(cvec)
    n = int(ok.sum())
    if n < 5 or len(set(lab[ok].tolist())) < 2:
        return None
    ru = spearman(z[ok], lab[ok])
    ra = partial_rank(z[ok], lab[ok], [cvec[ok]])
    if ru is None or not np.isfinite(ru) or not np.isfinite(ra):
        return None
    return {"n": n, "r_unadj": ru, "r_adj": ra,
            "t_unadj": signed_t(ru, n, 0), "t_adj": signed_t(ra, n, 1),
            "attenuation": (1.0 - abs(ra) / abs(ru)) if abs(ru) > 1e-12 else None}


def _frame_setup(d, fname, syms, src, cs):
    Z1, n1e, n1c, _ = build_matrix(d, P1, syms, src)
    Z2, n2e, n2c, _ = build_matrix(d, P2, syms, src)
    lab1 = np.array([1.0] * n1e + [0.0] * n1c)
    lab2 = np.array([1.0] * n2e + [0.0] * n2c)
    packs = []
    for pkey, Z, lab in ((P1, Z1, lab1), (P2, Z2, lab2)):
        M, S = cs[pkey]
        lookup = {"C": S["C"]}
        for m in MARKERS:
            lookup["LOO:" + m] = loo_score(M, m, MARKERS)
        keyfn = (lambda sym: ("LOO:" + sym) if sym in MARKERS else "C")
        groups = build_groups(Z, syms, lookup, keyfn)
        packs.append({"Z": Z, "lab": lab, "lookup": lookup, "groups": groups,
                      "G": len(syms), "S": Z.shape[1]})
    return packs


def frame_composition(d, fname, syms, src, cs, rng):
    p1, p2 = _frame_setup(d, fname, syms, src, cs)
    ru1 = unadjusted_r(p1["groups"], p1["G"], p1["lab"])
    ru2 = unadjusted_r(p2["groups"], p2["G"], p2["lab"])
    ra1 = adjusted_r(p1["groups"], p1["G"], p1["lab"], p1["lookup"])
    ra2 = adjusted_r(p2["groups"], p2["G"], p2["lab"], p2["lookup"])

    both = np.isfinite(ru1) & np.isfinite(ru2) & np.isfinite(ra1) & np.isfinite(ra2)
    rate_u, n_u = conc_rate(ru1, ru2)
    rate_a, n_a = conc_rate(ra1, ra2)
    rate_u_b = float((both & ((ru1 > 0) == (ru2 > 0))).sum()) / int(both.sum())
    rate_a_b = float((both & ((ra1 > 0) == (ra2 > 0))).sum()) / int(both.sum())
    att = np.where(np.abs(ru1[both]) > 1e-12, 1 - np.abs(ra1[both]) / np.abs(ru1[both]), np.nan)
    att2 = np.where(np.abs(ru2[both]) > 1e-12, 1 - np.abs(ra2[both]) / np.abs(ru2[both]), np.nan)

    perm = []
    for _ in range(N_PERM):
        l1 = p1["lab"][rng.permutation(p1["S"])]
        l2 = p2["lab"][rng.permutation(p2["S"])]
        q1 = adjusted_r(p1["groups"], p1["G"], l1, p1["lookup"])
        q2 = adjusted_r(p2["groups"], p2["G"], l2, p2["lookup"])
        r, n = conc_rate(q1, q2)
        if n:
            perm.append(r)
    perm = np.array(perm)

    return {
        "frame": fname,
        "n_genes_in_frame": len(syms),
        "unadjusted": {"n_scored_both": n_u, "concordance_rate": round(rate_u, 4),
                       "pearson_r_across_platforms": round(
                           pear(ru1[both], ru2[both]), 4)},
        "composition_adjusted": {"n_scored_both": n_a, "concordance_rate": round(rate_a, 4),
                                 "pearson_r_across_platforms": round(
                                     pear(ra1[both], ra2[both]), 4)},
        "paired_on_identical_gene_set": {
            "n_genes": int(both.sum()),
            "concordance_rate_unadjusted": round(rate_u_b, 4),
            "concordance_rate_adjusted": round(rate_a_b, 4),
            "absolute_change": round(rate_a_b - rate_u_b, 4),
            "attenuation_of_excess_over_0.5": (
                round(1 - (rate_a_b - 0.5) / (rate_u_b - 0.5), 4)
                if abs(rate_u_b - 0.5) > 1e-9 else None),
            "median_per_gene_attenuation_GPL6244": round(float(np.nanmedian(att)), 4),
            "median_per_gene_attenuation_GPL3290": round(float(np.nanmedian(att2)), 4),
            "n_genes_whose_direction_flips_on_GPL6244": int(
                ((ru1[both] > 0) != (ra1[both] > 0)).sum()),
            "n_genes_whose_direction_flips_on_GPL3290": int(
                ((ru2[both] > 0) != (ra2[both] > 0)).sum()),
        },
        "label_permutation_null_on_adjusted_rate": {
            "_randomises": ("which samples are called EMC, within each platform, arm sizes fixed; "
                            "the composition score stays attached to its sample"),
            "n_permutations": int(perm.size), "seed": SEED,
            "mean": round(float(perm.mean()), 4), "sd": round(float(perm.std(ddof=1)), 4),
            "p2.5": round(float(np.quantile(perm, .025)), 4),
            "p97.5": round(float(np.quantile(perm, .975)), 4),
            "max": round(float(perm.max()), 4),
            "n_at_least_as_concordant_as_observed_adjusted": int((perm >= rate_a_b).sum()),
            "p_observed_adjusted_rate": round(
                float((perm >= rate_a_b).sum() + 1) / (perm.size + 1), 5),
        },
        "_r": {"ru1": ru1, "ru2": ru2, "ra1": ra1, "ra2": ra2, "syms": syms,
               "p1": p1, "p2": p2},
    }


def negative_control(d, syms, src, cs, rng, n_perm):
    """Permute the composition score across samples; the real labels stay. Must NOT attenuate."""
    p1, p2 = _frame_setup(d, syms and "primary" or "", syms, src, cs)
    obs = conc_rate(adjusted_r(p1["groups"], p1["G"], p1["lab"], p1["lookup"]),
                    adjusted_r(p2["groups"], p2["G"], p2["lab"], p2["lookup"]))[0]
    draws = []
    for _ in range(n_perm):
        L1 = {k: v[rng.permutation(p1["S"])] for k, v in p1["lookup"].items()}
        L2 = {k: v[rng.permutation(p2["S"])] for k, v in p2["lookup"].items()}
        draws.append(conc_rate(adjusted_r(p1["groups"], p1["G"], p1["lab"], L1),
                               adjusted_r(p2["groups"], p2["G"], p2["lab"], L2))[0])
    return obs, np.array(draws)


def main():
    t0 = time.time()
    with open(SRC) as fh:
        d = json.load(fh)
    with open(K2) as fh:
        k2 = json.load(fh)

    # ---------------- 1. KNOWN-ANSWER GATE, first, unconditional
    nchk, mism, packs = known_answer_gate(d, k2)
    print("KNOWN-ANSWER GATE vs ../KINASE-2/label-permutation-vs-gene-resampling-null.json")
    print("  comparisons: %d   mismatches: %d" % (nchk, len(mism)))
    for m in mism:
        print("  MISMATCH", json.dumps(m))
    if mism:
        print("GATE FAILED - no adjustment computed. exit 2")
        return 2
    print("  gate PASSED (0 mismatches)\n")
    if "--gate-only" in sys.argv:
        print("--gate-only: stopping after the gate by request.")
        return 0

    F = frames(d)
    cs = {}
    for pkey in (P1, P2):
        plat = d["platforms"][pkey]
        cols = list(plat["EMC_gsms"]) + list(plat["comparator_gsms"])
        cs[pkey] = composition_scores(d, pkey, cols)

    # does the frozen composition score itself track the EMC label?
    comp_vs_label = {}
    for pkey, tag in ((P1, "GPL6244"), (P2, "GPL3290")):
        plat = d["platforms"][pkey]
        ne, nc = len(plat["EMC_gsms"]), len(plat["comparator_gsms"])
        lab = np.array([1.0] * ne + [0.0] * nc)
        S = cs[pkey][1]
        comp_vs_label[tag] = {}
        for k in ("C", "C_stromal", "C_immune", "MKI67", "EPCAM"):
            v = S[k]; ok = np.isfinite(v)
            comp_vs_label[tag][k] = {
                "spearman_with_EMC_label": round(spearman(v[ok], lab[ok]), 4),
                "mean_z_EMC_arm": round(float(np.nanmean(v[:ne])), 4),
                "mean_z_comparator_arm": round(float(np.nanmean(v[ne:])), 4),
                "n_samples": int(ok.sum())}
    print("COMPOSITION SCORE vs EMC LABEL")
    for tag in comp_vs_label:
        c = comp_vs_label[tag]["C"]
        print("  %-8s C: spearman %.4f  mean z EMC %.3f vs comparator %.3f (n=%d)"
              % (tag, c["spearman_with_EMC_label"], c["mean_z_EMC_arm"],
                 c["mean_z_comparator_arm"], c["n_samples"]))

    # ---------------- 2. NEGATIVE CONTROL (primary frame), before the main result
    prim_syms, prim_src = F["primary"]
    obs_adj, nc_draws = negative_control(d, prim_syms, prim_src, cs,
                                         np.random.default_rng(SEED), N_PERM_COMP_NC)
    print("\nNEGATIVE CONTROL (primary frame, %d permuted composition scores, real labels)"
          % nc_draws.size)
    print("  adjusted rate, REAL score      = %.4f" % obs_adj)
    print("  adjusted rate, PERMUTED score  = %.4f (sd %.4f) 95%% [%.4f, %.4f]"
          % (nc_draws.mean(), nc_draws.std(ddof=1),
             np.quantile(nc_draws, .025), np.quantile(nc_draws, .975)))

    # ---------------- 3. ADJUSTED STATISTICS AND NULL, both frames
    rng = np.random.default_rng(SEED)
    out_frames = {}
    for fname in ("primary", "secondary"):
        syms, src = F[fname]
        r = frame_composition(d, fname, syms, src, cs, rng)
        out_frames[fname] = r
        pr = r["paired_on_identical_gene_set"]
        n = r["label_permutation_null_on_adjusted_rate"]
        print("\n%s FRAME (%d genes in frame, %d scored on both platforms both ways)"
              % (fname.upper(), r["n_genes_in_frame"], pr["n_genes"]))
        print("  concordance  unadjusted %.4f  ->  composition-adjusted %.4f   (change %+.4f)"
              % (pr["concordance_rate_unadjusted"], pr["concordance_rate_adjusted"],
                 pr["absolute_change"]))
        print("  attenuation of the excess over 0.5 = %s" % pr["attenuation_of_excess_over_0.5"])
        print("  cross-platform pearson r  unadjusted %.4f -> adjusted %.4f"
              % (r["unadjusted"]["pearson_r_across_platforms"],
                 r["composition_adjusted"]["pearson_r_across_platforms"]))
        print("  median per-gene attenuation: GPL6244 %.4f  GPL3290 %.4f"
              % (pr["median_per_gene_attenuation_GPL6244"],
                 pr["median_per_gene_attenuation_GPL3290"]))
        print("  label-permutation null on the ADJUSTED rate: mean %.4f sd %.4f max %.4f  p=%s"
              % (n["mean"], n["sd"], n["max"], n["p_observed_adjusted_rate"]))

    unadj_prim = out_frames["primary"]["paired_on_identical_gene_set"]["concordance_rate_unadjusted"]
    adj_prim = out_frames["primary"]["paired_on_identical_gene_set"]["concordance_rate_adjusted"]
    d_real = abs(adj_prim - unadj_prim)
    d_perm = abs(float(nc_draws.mean()) - unadj_prim)
    negctl = {
        "_what": ("the composition score is shuffled across samples within platform while the real "
                  "EMC labels stay. A shuffled score carries no composition information, so the "
                  "adjusted concordance rate must NOT attenuate relative to the unadjusted rate."),
        "n_permutations": int(nc_draws.size),
        "unadjusted_rate_primary_frame": unadj_prim,
        "adjusted_rate_real_score": round(obs_adj, 4),
        "adjusted_rate_permuted_score_mean": round(float(nc_draws.mean()), 4),
        "adjusted_rate_permuted_score_sd": round(float(nc_draws.std(ddof=1)), 4),
        "adjusted_rate_permuted_score_p2.5": round(float(np.quantile(nc_draws, .025)), 4),
        "adjusted_rate_permuted_score_p97.5": round(float(np.quantile(nc_draws, .975)), 4),
        "adjusted_rate_permuted_score_min": round(float(nc_draws.min()), 4),
        "distance_to_unadjusted_real_score": round(d_real, 4),
        "distance_to_unadjusted_permuted_score": round(d_perm, 4),
        "n_permuted_score_draws_at_or_below_the_real_adjusted_rate": int(
            (nc_draws <= obs_adj).sum()),
        "verdict": ("PASS - a permuted composition score does not attenuate"
                    if d_perm < d_real or d_real < 0.005 else
                    "FAIL - a permuted composition score attenuates as much as the real one"),
        "_note_if_no_attenuation": ("when the real score does not attenuate either, this control "
                                    "only shows that the machinery is not manufacturing "
                                    "attenuation; it cannot certify sensitivity to a real one"),
    }
    print("\n  negative-control verdict: %s" % negctl["verdict"])

    # ---------------- lead genes
    leads_out = {}
    for gene in LEADS:
        rec = {"in_frames": {}}
        for fname in ("primary", "secondary"):
            r = out_frames[fname]["_r"]
            if gene not in r["syms"]:
                continue
            i = r["syms"].index(gene)
            entry = {}
            bad = False
            for tag, ru, ra, pk in (("GPL6244", r["ru1"], r["ra1"], r["p1"]),
                                    ("GPL3290", r["ru2"], r["ra2"], r["p2"])):
                if not (np.isfinite(ru[i]) and np.isfinite(ra[i])):
                    entry[tag] = {"_status": "not scorable on this platform in this frame"}
                    bad = True
                    continue
                nn = int(np.isfinite(pk["Z"][i]).sum())
                entry[tag] = {
                    "n_samples": nn,
                    "unadjusted_spearman_r_with_EMC_label": round(float(ru[i]), 4),
                    "unadjusted_t": round(signed_t(float(ru[i]), nn, 0), 3),
                    "composition_score_used": ("leave-one-out C, gene is itself a frozen marker"
                                               if gene in MARKERS else "C (20 markers)"),
                    "composition_adjusted_partial_r": round(float(ra[i]), 4),
                    "composition_adjusted_t": round(signed_t(float(ra[i]), nn, 1), 3),
                    "attenuation_1_minus_ratio_of_abs_r": (
                        round(1 - abs(float(ra[i])) / abs(float(ru[i])), 4)
                        if abs(float(ru[i])) > 1e-12 else None),
                    "sign_flipped_by_adjustment": bool((ru[i] > 0) != (ra[i] > 0)),
                }
            if not bad:
                entry["concordant_unadjusted"] = bool((r["ru1"][i] > 0) == (r["ru2"][i] > 0))
                entry["concordant_adjusted"] = bool((r["ra1"][i] > 0) == (r["ra2"][i] > 0))
            k2rec = k2["leads"].get(gene, {})
            entry["kinase2_welch_t_for_reference"] = {
                "GPL6244": k2rec.get("GPL6244_t_artifact"),
                "GPL3290": k2rec.get("GPL3290_t_artifact")}
            rec["in_frames"][fname] = entry
        if not rec["in_frames"]:
            rec = {"_status": ("not in either frame's scored gene set - an ABSENT READING, not a "
                               "reading of absence")}
        leads_out[gene] = rec

    print("\n%-8s %-24s %-24s %-8s" % ("gene", "GPL6244 r  unadj->adj", "GPL3290 r  unadj->adj",
                                        "conc u/a"))
    for gene in LEADS:
        e = leads_out[gene].get("in_frames", {}).get("secondary")
        if not e or "_status" in e.get("GPL6244", {}) or "_status" in e.get("GPL3290", {}):
            print("%-8s %s" % (gene, "not scorable on both platforms - absent reading"))
            continue
        a, b = e["GPL6244"], e["GPL3290"]
        print("%-8s %+.3f -> %+.3f (att %+.2f) %+.3f -> %+.3f (att %+.2f)  %s/%s"
              % (gene, a["unadjusted_spearman_r_with_EMC_label"],
                 a["composition_adjusted_partial_r"], a["attenuation_1_minus_ratio_of_abs_r"],
                 b["unadjusted_spearman_r_with_EMC_label"],
                 b["composition_adjusted_partial_r"], b["attenuation_1_minus_ratio_of_abs_r"],
                 "y" if e["concordant_unadjusted"] else "N",
                 "y" if e["concordant_adjusted"] else "N"))

    for f in out_frames.values():
        f.pop("_r", None)

    result = {
        "_question": ("Is the broad two-platform EMC expression contrast that KINASE-2 validated "
                      "tumour/stroma composition, or EMC biology? This lane holds a frozen "
                      "marker-transcript composition score constant and asks what is left."),
        "_this_is_not": [
            "a measured cell fraction or a deconvolution - 'composition score' means the frozen "
            "marker-transcript score of PREREGISTRATION.md sec.2, in undeconvolved bulk tissue",
            "a clean separation of composition from biology: markers are themselves transcripts, "
            "and in a mesenchymal tumour a stromal score is partly the tumour's own programme",
            "evidence of efficacy, safety, selectivity, a therapeutic window or clinical readiness",
            "a target-attribution claim for any gene, in either direction",
            "a multiple-testing correction (none applied)",
        ],
        "declared_before_any_statistic_was_read": {
            "prereg": "PREREGISTRATION.md in this directory",
            "prereg_sha256": PREREG_SHA,
            "markers_primary_score_20": MARKERS,
            "markers_excluded_from_primary_score": EXCLUDED,
            "leave_one_out_rule": ("a gene that is itself a frozen marker is never adjusted for a "
                                   "score containing itself"),
            "seed": SEED, "n_perm_label": N_PERM,
            "n_perm_composition_negative_control": N_PERM_COMP_NC,
        },
        "known_answer_gate": {
            "target": "../KINASE-2/label-permutation-vs-gene-resampling-null.json",
            "target_sha256": "f799e5ed962c09ff1bc05d2354c8fb4b12cc803e2aaf0475edaa8bea67edfb65",
            "comparisons": nchk, "mismatches": 0,
            "_scope": ("KINASE-2's OBSERVED statistics only - per-frame n, concordance count and "
                       "rate, cross-platform Pearson and Spearman r, the five min|t| quantiles, "
                       "arm sizes, and every placed lead gene's min|t|, direction and "
                       "gene-resampling joint p on both frames. KINASE-2's permutation quantiles "
                       "are RNG-path dependent and are deliberately NOT part of this gate."),
        },
        "negative_control_permuted_composition_score": negctl,
        "composition_score_vs_EMC_label": comp_vs_label,
        "source_artifact": "research/modalities/emc-expression-panels.json",
        "source_sha256": "59bccb553148c7100172456835957434b1349d701d4e0504e632a367c62a7f8d",
        "source_generated_utc": d["generated_utc"],
        "repo_head_at_lane_start": "1e35538daee86e1a34345340f7562d1e91147fa0",
        "runtime_seconds": round(time.time() - t0, 1),
        "frames": out_frames,
        "leads": leads_out,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=1)
    print("\nwrote", OUT, "| runtime %.1fs" % result["runtime_seconds"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
