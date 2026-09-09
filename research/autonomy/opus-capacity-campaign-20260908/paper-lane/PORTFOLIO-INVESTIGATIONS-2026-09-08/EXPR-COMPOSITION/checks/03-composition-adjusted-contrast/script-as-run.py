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
HERE = os.path.dirname(os.path.abspath(__file__))
K2 = os.path.join(HERE, "..", "KINASE-2", "label-permutation-vs-gene-resampling-null.json")
OUT = os.path.join(HERE, "composition-adjusted-contrast.json")

P1 = "GSE24369_series_matrix.txt.gz"          # GPL6244
P2 = "GSE4303-GPL3290_series_matrix.txt.gz"   # GPL3290

SEED = 20260909
N_PERM = 2000
N_PERM_COMP = 2000

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


def frame_composition(d, fname, syms, src, cs, rng, verbose=True):
    Z1, n1e, n1c, cols1 = build_matrix(d, P1, syms, src)
    Z2, n2e, n2c, cols2 = build_matrix(d, P2, syms, src)
    lab1 = np.array([1.0] * n1e + [0.0] * n1c)
    lab2 = np.array([1.0] * n2e + [0.0] * n2c)
    M1, S1 = cs[P1]; M2, S2 = cs[P2]

    def per_gene(which, Z, lab, M, S, scorekey):
        out = []
        for gi, sym in enumerate(syms):
            cvec = loo_score(M, sym, MARKERS) if (scorekey == "C" and sym in MARKERS) else S[scorekey]
            out.append(gene_stats(Z[gi], lab, cvec, M, sym))
        return out

    A = per_gene(P1, Z1, lab1, M1, S1, "C")
    B = per_gene(P2, Z2, lab2, M2, S2, "C")

    def rates(key):
        u1 = np.array([x[key] if x else np.nan for x in A])
        u2 = np.array([x[key] if x else np.nan for x in B])
        ok = np.isfinite(u1) & np.isfinite(u2)
        conc = ok & ((u1 > 0) == (u2 > 0))
        return (int(ok.sum()), int(conc.sum()),
                float(conc.sum()) / max(int(ok.sum()), 1),
                pear(u1[ok], u2[ok]), spearman(u1[ok], u2[ok]), u1, u2, ok)

    nu, cu, ru_rate, pu, su, u1, u2, oku = rates("r_unadj")
    na, ca, ra_rate, pa, sa, a1, a2, oka = rates("r_adj")
    both = oku & oka
    rate_u_both = float((((u1 > 0) == (u2 > 0)) & both).sum()) / int(both.sum())
    rate_a_both = float((((a1 > 0) == (a2 > 0)) & both).sum()) / int(both.sum())

    # label-permutation null on the ADJUSTED concordance rate (composition stays with its sample)
    perm = []
    for _ in range(N_PERM):
        p1 = rng.permutation(len(lab1)); p2 = rng.permutation(len(lab2))
        l1, l2 = lab1[p1], lab2[p2]
        r1 = np.array([partial_rank(Z1[i][np.isfinite(Z1[i])], l1[np.isfinite(Z1[i])],
                                    [S1["C"][np.isfinite(Z1[i])]])
                       if np.isfinite(Z1[i]).sum() >= 5 else np.nan
                       for i in range(len(syms))])
        r2 = np.array([partial_rank(Z2[i][np.isfinite(Z2[i])], l2[np.isfinite(Z2[i])],
                                    [S2["C"][np.isfinite(Z2[i])]])
                       if np.isfinite(Z2[i]).sum() >= 5 else np.nan
                       for i in range(len(syms))])
        o = np.isfinite(r1) & np.isfinite(r2)
        if o.sum() == 0:
            continue
        perm.append(float((o & ((r1 > 0) == (r2 > 0))).sum()) / float(o.sum()))
    perm = np.array(perm)

    return {
        "frame": fname,
        "n_genes": len(syms),
        "unadjusted": {"n_scored_both": nu, "n_concordant": cu,
                       "concordance_rate": round(ru_rate, 4),
                       "pearson_r_across_platforms": round(pu, 4),
                       "spearman_r_across_platforms": round(su, 4)},
        "composition_adjusted": {"n_scored_both": na, "n_concordant": ca,
                                 "concordance_rate": round(ra_rate, 4),
                                 "pearson_r_across_platforms": round(pa, 4),
                                 "spearman_r_across_platforms": round(sa, 4)},
        "paired_on_identical_gene_set": {
            "n_genes": int(both.sum()),
            "concordance_rate_unadjusted": round(rate_u_both, 4),
            "concordance_rate_adjusted": round(rate_a_both, 4),
            "absolute_change": round(rate_a_both - rate_u_both, 4),
            "attenuation_of_excess_over_0.5": (
                round(1 - (rate_a_both - 0.5) / (rate_u_both - 0.5), 4)
                if abs(rate_u_both - 0.5) > 1e-9 else None),
            "median_per_gene_attenuation_GPL6244": round(float(np.nanmedian(
                [x["attenuation"] for x in A if x and x["attenuation"] is not None])), 4),
            "median_per_gene_attenuation_GPL3290": round(float(np.nanmedian(
                [x["attenuation"] for x in B if x and x["attenuation"] is not None])), 4),
        },
        "label_permutation_null_on_adjusted_rate": {
            "n_permutations": int(perm.size), "seed": SEED,
            "mean": round(float(perm.mean()), 4), "sd": round(float(perm.std(ddof=1)), 4),
            "p2.5": round(float(np.quantile(perm, .025)), 4),
            "p97.5": round(float(np.quantile(perm, .975)), 4),
            "max": round(float(perm.max()), 4),
            "n_at_least_as_concordant_as_observed_adjusted": int((perm >= rate_a_both).sum()),
            "p_observed_adjusted_rate": round(
                float((perm >= rate_a_both).sum() + 1) / (perm.size + 1), 5),
        },
        "_per_gene": {"A": A, "B": B, "syms": syms, "both": both},
        "_mats": (Z1, lab1, S1, M1, Z2, lab2, S2, M2),
    }


def negative_control(d, syms, src, cs, rng, n_perm):
    """Permute the composition score across samples; labels stay real. Must not attenuate."""
    Z1, n1e, n1c, _ = build_matrix(d, P1, syms, src)
    Z2, n2e, n2c, _ = build_matrix(d, P2, syms, src)
    lab1 = np.array([1.0] * n1e + [0.0] * n1c)
    lab2 = np.array([1.0] * n2e + [0.0] * n2c)
    C1 = cs[P1][1]["C"]; C2 = cs[P2][1]["C"]

    def rate(c1, c2):
        r1 = np.array([partial_rank(Z1[i][np.isfinite(Z1[i])], lab1[np.isfinite(Z1[i])],
                                    [c1[np.isfinite(Z1[i])]])
                       if np.isfinite(Z1[i]).sum() >= 5 else np.nan for i in range(len(syms))])
        r2 = np.array([partial_rank(Z2[i][np.isfinite(Z2[i])], lab2[np.isfinite(Z2[i])],
                                    [c2[np.isfinite(Z2[i])]])
                       if np.isfinite(Z2[i]).sum() >= 5 else np.nan for i in range(len(syms))])
        o = np.isfinite(r1) & np.isfinite(r2)
        return float((o & ((r1 > 0) == (r2 > 0))).sum()) / float(o.sum())

    obs = rate(C1, C2)
    draws = np.array([rate(C1[rng.permutation(len(C1))], C2[rng.permutation(len(C2))])
                      for _ in range(n_perm)])
    return obs, draws


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

    rng = np.random.default_rng(SEED)
    F = frames(d)

    # composition scores (per platform, on the platform's labelled sample order)
    cs = {}
    for pkey in (P1, P2):
        plat = d["platforms"][pkey]
        cols = list(plat["EMC_gsms"]) + list(plat["comparator_gsms"])
        cs[pkey] = composition_scores(d, pkey, cols)

    # how strongly does the composition score itself track the EMC label?
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
                "mean_EMC": round(float(np.nanmean(v[:ne])), 4),
                "mean_comparator": round(float(np.nanmean(v[ne:])), 4),
                "n": int(ok.sum())}

    # ---------------- 2. NEGATIVE CONTROL (primary frame)
    prim_syms, prim_src = F["primary"]
    nc_rng = np.random.default_rng(SEED)
    obs_rate_adj, nc_draws = negative_control(d, prim_syms, prim_src, cs, nc_rng, 200)
    unadj_rate_prim = None  # filled after frame pass
    negctl = {
        "_what": ("the composition score is shuffled across samples within platform; the real "
                  "EMC labels stay. A shuffled score carries no composition information, so the "
                  "adjusted concordance rate must return to the unadjusted rate - it must NOT "
                  "attenuate."),
        "n_permutations": int(nc_draws.size),
        "observed_adjusted_rate_real_score": round(obs_rate_adj, 4),
        "permuted_score_adjusted_rate_mean": round(float(nc_draws.mean()), 4),
        "permuted_score_adjusted_rate_sd": round(float(nc_draws.std(ddof=1)), 4),
        "permuted_score_adjusted_rate_p2.5": round(float(np.quantile(nc_draws, .025)), 4),
        "permuted_score_adjusted_rate_p97.5": round(float(np.quantile(nc_draws, .975)), 4),
        "permuted_score_adjusted_rate_min": round(float(nc_draws.min()), 4),
    }
    print("NEGATIVE CONTROL (primary frame, %d permuted composition scores)" % nc_draws.size)
    print("  adjusted rate with the REAL score     = %.4f" % obs_rate_adj)
    print("  adjusted rate with a PERMUTED score   = %.4f (sd %.4f) 95%% [%.4f, %.4f]"
          % (nc_draws.mean(), nc_draws.std(ddof=1),
             np.quantile(nc_draws, .025), np.quantile(nc_draws, .975)))

    # ---------------- 3. ADJUSTED STATISTICS AND NULL, both frames
    out_frames = {}
    for fname in ("primary", "secondary"):
        syms, src = F[fname]
        r = frame_composition(d, fname, syms, src, cs, rng)
        out_frames[fname] = r
        print("\n%s FRAME  (n=%d genes)" % (fname.upper(), r["n_genes"]))
        print("  unadjusted concordance = %.4f  (cross-platform pearson r %.4f)"
              % (r["unadjusted"]["concordance_rate"],
                 r["unadjusted"]["pearson_r_across_platforms"]))
        print("  ADJUSTED   concordance = %.4f  (cross-platform pearson r %.4f)"
              % (r["composition_adjusted"]["concordance_rate"],
                 r["composition_adjusted"]["pearson_r_across_platforms"]))
        p = r["paired_on_identical_gene_set"]
        print("  paired on %d genes: %.4f -> %.4f  (change %+0.4f; excess-over-0.5 attenuation %s)"
              % (p["n_genes"], p["concordance_rate_unadjusted"], p["concordance_rate_adjusted"],
                 p["absolute_change"], p["attenuation_of_excess_over_0.5"]))
        n = r["label_permutation_null_on_adjusted_rate"]
        print("  label-permutation null on the ADJUSTED rate: mean %.4f sd %.4f max %.4f  p=%s"
              % (n["mean"], n["sd"], n["max"], n["p_observed_adjusted_rate"]))

    negctl["primary_frame_unadjusted_rate_for_comparison"] = \
        out_frames["primary"]["paired_on_identical_gene_set"]["concordance_rate_unadjusted"]
    negctl["verdict"] = (
        "PASS - the permuted score does not attenuate"
        if abs(float(nc_draws.mean()) - negctl["primary_frame_unadjusted_rate_for_comparison"]) <
           abs(out_frames["primary"]["paired_on_identical_gene_set"]["concordance_rate_adjusted"]
               - negctl["primary_frame_unadjusted_rate_for_comparison"]) or
           abs(out_frames["primary"]["paired_on_identical_gene_set"]["absolute_change"]) < 0.005
        else "FAIL - the permuted score attenuates as much as the real one")
    print("  negative-control verdict: %s" % negctl["verdict"])

    # ---------------- lead genes
    leads_out = {}
    for gene in LEADS:
        rec = {"in_frames": {}}
        for fname in ("primary", "secondary"):
            r = out_frames[fname]
            if gene not in r["_per_gene"]["syms"]:
                continue
            i = r["_per_gene"]["syms"].index(gene)
            A, B = r["_per_gene"]["A"][i], r["_per_gene"]["B"][i]
            if A is None or B is None:
                rec["in_frames"][fname] = {"_status": "not scorable on both platforms in this frame"}
                continue
            k2rec = k2["leads"].get(gene, {})
            entry = {}
            for tag, x in (("GPL6244", A), ("GPL3290", B)):
                entry[tag] = {
                    "n_samples": x["n"],
                    "unadjusted_spearman_r_with_EMC_label": round(x["r_unadj"], 4),
                    "unadjusted_t": round(x["t_unadj"], 3),
                    "composition_score_used": ("leave-one-out (gene is a frozen marker)"
                                               if gene in MARKERS else "C (20 markers)"),
                    "composition_adjusted_partial_r": round(x["r_adj"], 4),
                    "composition_adjusted_t": round(x["t_adj"], 3),
                    "attenuation_1_minus_ratio_abs_r": (round(x["attenuation"], 4)
                                                        if x["attenuation"] is not None else None),
                    "sign_flipped_by_adjustment": bool((x["r_unadj"] > 0) != (x["r_adj"] > 0)),
                }
            entry["concordant_unadjusted"] = bool((A["r_unadj"] > 0) == (B["r_unadj"] > 0))
            entry["concordant_adjusted"] = bool((A["r_adj"] > 0) == (B["r_adj"] > 0))
            entry["kinase2_welch_t"] = {
                "GPL6244": k2rec.get("GPL6244_t_artifact"),
                "GPL3290": k2rec.get("GPL3290_t_artifact")}
            rec["in_frames"][fname] = entry
        if not rec["in_frames"]:
            rec = {"_status": ("not present in either frame's scored gene set - an ABSENT READING, "
                               "not a reading of absence")}
        leads_out[gene] = rec

    for f in out_frames.values():
        f.pop("_per_gene", None); f.pop("_mats", None)

    result = {
        "_question": ("Is the broad two-platform EMC expression contrast that KINASE-2 validated "
                      "tumour/stroma composition, or EMC biology? This lane holds a frozen "
                      "marker-transcript composition score constant and asks what is left."),
        "_this_is_not": [
            "a measured cell fraction or a deconvolution - 'composition score' means the frozen "
            "marker-transcript score of PREREGISTRATION.md sec.2, in undeconvolved bulk tissue",
            "a separation of composition from biology: markers are themselves transcripts, and a "
            "composition score in a mesenchymal tumour is partly the tumour's own programme",
            "evidence of efficacy, safety, selectivity, a therapeutic window or clinical readiness",
            "a target-attribution claim for any gene, in either direction",
            "a multiple-testing correction (none applied)",
        ],
        "declared_before_any_statistic_was_read": {
            "prereg": "PREREGISTRATION.md in this directory",
            "markers_primary_score_20": MARKERS,
            "markers_excluded_from_primary_score": EXCLUDED,
            "leave_one_out_rule": "a gene that is itself a frozen marker is never adjusted for a "
                                  "score containing itself",
            "seed": SEED, "n_perm_label": N_PERM, "n_perm_composition_negative_control": 200,
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
