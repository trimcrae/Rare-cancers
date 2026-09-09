#!/usr/bin/env python3
"""Label-permutation null for the two-platform concordance argument (lane KINASE-2).

Lane PUB-KINASE-LEADS built a GENE-RESAMPLING null: draw random genes, ask how often
one is concordant in direction across GSE24369/GPL6244 and GSE4303/GPL3290 at a given
strength.  Answer: 65.2% of random genes are already concordant in direction.  That
number cannot distinguish two explanations:

  (a) the two series are simply correlated with each other -- shared EMC arm identity,
      shared tissue composition, shared probe behaviour -- so ANY gene tends to agree;
  (b) EMC is a coherent contrast, and agreement carries real signal.

Permuting the EMC-vs-comparator LABELS within each platform destroys (b) and leaves the
gene-level data, the missingness, the arm sizes and the platforms' own structure intact.
The gap between the two nulls is the quantity this script produces.

Declared before running (see PREREGISTRATION.md): N_PERM = 2000, SEED = 20260909.
Reads one committed artifact.  Writes one JSON here.  No network, no GPU, no paid API.
Nothing here is an efficacy, safety, selectivity or target-attribution claim: it is a
calibration of a transcript instrument against its own negative.
"""
import json, math, os, sys, time
import numpy as np

REPO = "/home/user/Rare-cancers"
SRC = os.path.join(REPO, "research/modalities/emc-expression-panels.json")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "label-permutation-vs-gene-resampling-null.json")

P1 = "GSE24369_series_matrix.txt.gz"   # GPL6244
P2 = "GSE4303-GPL3290_series_matrix.txt.gz"  # GPL3290

N_PERM = 2000
SEED = 20260909
SMALLER_FRAME = None

LEADS = {
    "RET":   "lead 1 (RET) - the route's own named kinase",
    "SGK1":  "lead 4 (SGK1) - the kinase itself",
    "NDRG1": "lead 4 (SGK1) - the substrate whose abundance carries the claim",
    "ALK":   "lead 2 (ex-vivo screen hit) - named kinase",
    "ROS1":  "lead 2 (ex-vivo screen hit) - named kinase",
    "PRKDC": "lead 3 (DNA-PK) - catalytic subunit",
    "XRCC5": "lead 3 (DNA-PK) - Ku80",
    "XRCC6": "lead 3 (DNA-PK) - Ku70",
    "NR4A3": "positive control - the disease's own driver gene",
    "EGFR":  "negative-direction control named beside lead 2",
    "GFRA1": "RET co-receptor (route's own stated counter-evidence)",
    "GFRA2": "RET co-receptor - the route's counter-evidence gene",
    "GDNF":  "RET ligand",
    "HDAC3": "the class the screen re-read favours",
}


# ---------------------------------------------------------------- matrices
def build_matrix(d, pkey, symbols, source):
    """(G x S) z matrix over the platform's LABELLED samples, NaN for missing.

    source='background' uses background_reads[pkey]['z']; source='curated' uses
    gene_reads[sym][pkey]['per_sample'].  Column order is EMC arm then comparator arm,
    so the observed labelling is simply 'the first n_emc columns'.
    """
    plat = d["platforms"][pkey]
    emc, cmp_ = list(plat["EMC_gsms"]), list(plat["comparator_gsms"])
    cols = emc + cmp_
    G, S = len(symbols), len(cols)
    Z = np.full((G, S), np.nan)
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
    return Z, len(emc), len(cmp_)


def welch_t(Z, a_idx, b_idx):
    """Vectorised Welch t (group A - group B) per row, NaN where undefined."""
    A, B = Z[:, a_idx], Z[:, b_idx]
    out = np.full(Z.shape[0], np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        na = np.sum(~np.isnan(A), axis=1); nb = np.sum(~np.isnan(B), axis=1)
        ma = np.nanmean(np.where(np.isnan(A), np.nan, A), axis=1)
        mb = np.nanmean(np.where(np.isnan(B), np.nan, B), axis=1)
        va = np.nanvar(A, axis=1, ddof=1); vb = np.nanvar(B, axis=1, ddof=1)
        se2 = va / na + vb / nb
        ok = (na >= 2) & (nb >= 2) & np.isfinite(se2) & (se2 > 0)
        out[ok] = (ma[ok] - mb[ok]) / np.sqrt(se2[ok])
    return out


# ---------------------------------------------------------------- nulls
def concordance(t1, t2):
    ok = np.isfinite(t1) & np.isfinite(t2)
    conc = ok & ((t1 > 0) == (t2 > 0))
    return ok, conc, np.minimum(np.abs(t1), np.abs(t2))


def frame_report(name, d, symbols, source, rng):
    """Both nulls on one frame.  Returns a dict and the pooled permuted draws."""
    Z1, n1e, n1c = build_matrix(d, P1, symbols, source)
    Z2, n2e, n2c = build_matrix(d, P2, symbols, source)
    obs1 = welch_t(Z1, np.arange(n1e), np.arange(n1e, n1e + n1c))
    obs2 = welch_t(Z2, np.arange(n2e), np.arange(n2e, n2e + n2c))
    ok, conc, mn = concordance(obs1, obs2)
    n_ok = int(ok.sum())
    obs_rate = float(conc.sum()) / n_ok

    fin = ok
    r_pear = float(np.corrcoef(obs1[fin], obs2[fin])[0, 1])
    rk1 = np.argsort(np.argsort(obs1[fin])); rk2 = np.argsort(np.argsort(obs2[fin]))
    r_spear = float(np.corrcoef(rk1, rk2)[0, 1])

    S1, S2 = Z1.shape[1], Z2.shape[1]
    rates, pears, spears = [], [], []
    pool_conc, pool_min = [], []
    seen1, seen2 = set(), set()
    for _ in range(N_PERM):
        p1 = rng.permutation(S1); p2 = rng.permutation(S2)
        a1, b1 = p1[:n1e], p1[n1e:]
        a2, b2 = p2[:n2e], p2[n2e:]
        seen1.add(tuple(sorted(a1.tolist()))); seen2.add(tuple(sorted(a2.tolist())))
        t1 = welch_t(Z1, a1, b1); t2 = welch_t(Z2, a2, b2)
        o, c, m = concordance(t1, t2)
        if o.sum() == 0:
            continue
        rates.append(float(c.sum()) / float(o.sum()))
        pool_conc.append(c[o]); pool_min.append(m[o])
        pears.append(float(np.corrcoef(t1[o], t2[o])[0, 1]))
        rr1 = np.argsort(np.argsort(t1[o])); rr2 = np.argsort(np.argsort(t2[o]))
        spears.append(float(np.corrcoef(rr1, rr2)[0, 1]))
    rates = np.array(rates)
    pool_conc = np.concatenate(pool_conc); pool_min = np.concatenate(pool_min)
    # sorted min|t| among CONCORDANT permuted draws -> joint p by binary search
    perm_conc_sorted = np.sort(pool_min[pool_conc])
    n_pool = int(pool_min.size)

    def q(a, p):
        return float(np.quantile(a, p))

    rep = {
        "frame": name,
        "n_genes_scored_on_both_platforms": n_ok,
        "platform_arms": {"GPL6244": {"n_EMC": n1e, "n_comparator": n1c},
                          "GPL3290": {"n_EMC": n2e, "n_comparator": n2c}},
        "gene_resampling_null": {
            "_randomises": "which GENE you look at; the EMC/comparator labels are the real ones",
            "concordance_rate": round(obs_rate, 4),
            "n_concordant": int(conc.sum()),
            "pearson_r_t1_t2": round(r_pear, 4),
            "spearman_r_t1_t2": round(r_spear, 4),
            "min_abs_t_quantiles_among_concordant": {
                k: round(q(mn[conc], p), 3) for k, p in
                (("p50", .5), ("p75", .75), ("p90", .90), ("p95", .95), ("p99", .99))},
        },
        "label_permutation_null": {
            "_randomises": "which samples are called EMC, within each platform, arm sizes fixed",
            "n_permutations": int(rates.size),
            "seed": SEED,
            "distinct_label_assignments_drawn": {"GPL6244": len(seen1), "GPL3290": len(seen2)},
            "exact_label_space_size": {
                "GPL6244": math.comb(S1, n1e), "GPL3290": math.comb(S2, n2e)},
            "concordance_rate_mean": round(float(rates.mean()), 4),
            "concordance_rate_sd": round(float(rates.std(ddof=1)), 4),
            "concordance_rate_quantiles": {k: round(q(rates, p), 4) for k, p in
                                           (("p2.5", .025), ("p50", .5), ("p97.5", .975))},
            "concordance_rate_max_over_permutations": round(float(rates.max()), 4),
            "n_permutations_at_least_as_concordant_as_observed": int((rates >= obs_rate).sum()),
            "p_observed_concordance_vs_permutation": round(
                float((rates >= obs_rate).sum() + 1) / (rates.size + 1), 5),
            "pearson_r_t1_t2_mean": round(float(np.mean(pears)), 4),
            "pearson_r_t1_t2_p97.5": round(q(np.array(pears), .975), 4),
            "spearman_r_t1_t2_mean": round(float(np.mean(spears)), 4),
            "pooled_draws": n_pool,
            "min_abs_t_quantiles_among_concordant_permuted": {
                k: round(q(perm_conc_sorted, p), 3) for k, p in
                (("p50", .5), ("p75", .75), ("p90", .90), ("p95", .95), ("p99", .99))},
        },
    }
    obs_pack = {"t1": obs1, "t2": obs2, "ok": ok, "conc": conc, "min": mn,
                "n_ok": n_ok, "symbols": symbols}
    perm_pack = {"conc_sorted": perm_conc_sorted, "n_pool": n_pool}
    return rep, obs_pack, perm_pack


def place(m, obs_pack, perm_pack):
    """Joint empirical p of a gene with weaker-platform strength m, under both nulls."""
    o = obs_pack
    k_gene = int(np.sum(o["conc"] & (o["min"] >= m)))
    p_gene = k_gene / o["n_ok"]
    k_perm = int(perm_pack["conc_sorted"].size -
                 np.searchsorted(perm_pack["conc_sorted"], m, side="left"))
    p_perm = k_perm / perm_pack["n_pool"]
    return {"n_null_genes_at_least_this_concordant_and_strong": k_gene,
            "joint_p_gene_resampling": round(p_gene, 5),
            "n_permuted_draws_at_least_this_concordant_and_strong": k_perm,
            "joint_p_label_permutation": round(p_perm, 5),
            "ratio_gene_resampling_over_label_permutation":
                (round(p_gene / p_perm, 3) if p_perm > 0 else None)}


def main():
    t_start = time.time()
    with open(SRC) as fh:
        d = json.load(fh)
    rng = np.random.default_rng(SEED)

    bg1 = d["background_reads"][P1]["z"]; bg2 = d["background_reads"][P2]["z"]
    prim_syms = sorted(set(bg1) & set(bg2))
    rep_p, obs_p, per_p = frame_report("primary: genes in BOTH committed random background draws",
                                       d, prim_syms, "background", rng)

    cur_syms = sorted(g for g, v in d["gene_reads"].items()
                      if v.get(P1, {}).get("readable") and v.get(P2, {}).get("readable"))
    rep_c, obs_c, per_c = frame_report("secondary: curated gene_reads genes readable on both",
                                       d, cur_syms, "curated", rng)

    global SMALLER_FRAME
    SMALLER_FRAME = min(d["platforms"][P1]["genome_wide_null"]["n_symbols_scored"],
                        d["platforms"][P2]["genome_wide_null"]["n_symbols_scored"])
    pw1 = d["platforms"][P1]["genome_wide_null"]["placed_wanted_genes"]
    pw2 = d["platforms"][P2]["genome_wide_null"]["placed_wanted_genes"]
    cur_idx = {s: i for i, s in enumerate(cur_syms)}

    leads = {}
    for g, why in LEADS.items():
        a, b = pw1.get(g), pw2.get(g)
        rec = {"role": why,
               "GPL6244_t_artifact": a["t"] if a else None,
               "GPL3290_t_artifact": b["t"] if b else None}
        if a is None or b is None:
            rec["placement"] = None
            rec["_why_no_placement"] = ("not readable on both platforms - an ABSENT READING, "
                                        "not a reading of absence")
            leads[g] = rec
            continue
        conc = (a["t"] > 0) == (b["t"] > 0)
        m = min(abs(a["t"]), abs(b["t"]))
        rec["concordant_direction"] = conc
        rec["min_abs_t"] = round(m, 3)
        rec["placement_primary_frame"] = place(m, obs_p, per_p)
        rec["placement_primary_frame"]["approx_genes_on_smaller_platform_as_concordant_and_strong"] = round(
            rec["placement_primary_frame"]["joint_p_gene_resampling"] * SMALLER_FRAME)
        rec["placement_secondary_frame"] = place(m, obs_c, per_c)
        if g in cur_idx:
            i = cur_idx[g]
            rec["_recomputed_t_from_per_sample_z"] = {
                "GPL6244": round(float(obs_c["t1"][i]), 3),
                "GPL3290": round(float(obs_c["t2"][i]), 3)}
        if not conc:
            rec["_note"] = ("DISCORDANT - joint p reported for scale only; it is not a support "
                            "statement for this gene under either null")
        leads[g] = rec

    runtime = round(time.time() - t_start, 1)
    result = {
        "_what": ("Two nulls for the same statistic, side by side: the gene-resampling null lane "
                  "PUB-KINASE-LEADS built, and the label-permutation null it named as the next "
                  "work. Both score 'moves the same way in EMC on both array platforms, at least "
                  "this strongly on the weaker platform'."),
        "_why": ("The gene-resampling null cannot separate (a) the two series being correlated "
                 "with each other from (b) EMC being a coherent contrast whose agreement carries "
                 "signal. Permuting the EMC/comparator labels within each platform destroys (b) "
                 "and preserves the rest of the data. The gap between the two nulls is the "
                 "quantity that was missing."),
        "_this_is_not": [
            "a test of activation, phosphorylation, protein level or drug response",
            "a multiple-testing correction (none applied; both nulls are empirical)",
            "evidence of efficacy, safety, selectivity or a therapeutic window",
            "a target-attribution claim for any gene, in either direction",
        ],
        "declared_before_running": {"n_permutations": N_PERM, "seed": SEED,
                                    "prereg": "PREREGISTRATION.md in this directory"},
        "runtime_seconds": runtime,
        "source_artifact": "research/modalities/emc-expression-panels.json",
        "source_generated_utc": d["generated_utc"],
        "background_seeds": {P1: d["background_reads"][P1]["seed"],
                             P2: d["background_reads"][P2]["seed"]},
        "genome_frame_sizes_scored": {
            "GPL6244": d["platforms"][P1]["genome_wide_null"]["n_symbols_scored"],
            "GPL3290": d["platforms"][P2]["genome_wide_null"]["n_symbols_scored"],
            "_used_for": ("scaling a gene-resampling joint p to an approximate count of genes on "
                          "the smaller platform - a crowding figure, not a multiplicity correction")},
        "seed_stability": {
            "_checked_in": "checks/04-seed-stability-and-crowding-rerun",
            "seeds_tried": [20260909, 1, 42, 987654321, 20260908],
            "n_permutations_per_seed": 500,
            "permuted_concordance_mean_range": [0.4957, 0.5013],
            "_reading": ("the permuted concordance rate does not move with the seed; the gap to "
                         "the observed 0.6520 is not a sampling accident")},
        "frames": {"primary": rep_p, "secondary": rep_c},
        "leads": leads,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=1)

    # ---- console report
    print("wrote", OUT, "| runtime %.1fs" % runtime)
    for tag, rep in (("PRIMARY", rep_p), ("SECONDARY", rep_c)):
        g_, l_ = rep["gene_resampling_null"], rep["label_permutation_null"]
        print("\n%s FRAME (n=%d genes on both platforms)" % (tag, rep["n_genes_scored_on_both_platforms"]))
        print("  gene-resampling concordance   = %.4f   pearson r(t1,t2) = %.4f" %
              (g_["concordance_rate"], g_["pearson_r_t1_t2"]))
        print("  label-permutation concordance = %.4f  sd %.4f  95%% [%.4f, %.4f]  max %.4f" %
              (l_["concordance_rate_mean"], l_["concordance_rate_sd"],
               l_["concordance_rate_quantiles"]["p2.5"], l_["concordance_rate_quantiles"]["p97.5"],
               l_["concordance_rate_max_over_permutations"]))
        print("  permuted pearson r(t1,t2) mean = %.4f ; p(observed concordance) = %s ; perms %d "
              "(distinct GPL6244 %d / GPL3290 %d of %d)" %
              (l_["pearson_r_t1_t2_mean"], l_["p_observed_concordance_vs_permutation"],
               l_["n_permutations"], l_["distinct_label_assignments_drawn"]["GPL6244"],
               l_["distinct_label_assignments_drawn"]["GPL3290"],
               l_["exact_label_space_size"]["GPL3290"]))
    print("\n%-7s %-6s %-9s %-9s %-11s %-11s %s" %
          ("gene", "conc", "t GPL6244", "t GPL3290", "p_gene-res", "p_label-perm", "ratio"))
    order = sorted((g for g in leads if leads[g].get("placement_primary_frame")),
                   key=lambda g: leads[g]["placement_primary_frame"]["joint_p_gene_resampling"])
    for g in order:
        r = leads[g]; p = r["placement_primary_frame"]
        print("%-7s %-6s %-9.3f %-9.3f %-11.4f %-11.5f %s" %
              (g, "yes" if r["concordant_direction"] else "NO",
               r["GPL6244_t_artifact"], r["GPL3290_t_artifact"],
               p["joint_p_gene_resampling"], p["joint_p_label_permutation"],
               p["ratio_gene_resampling_over_label_permutation"]))
    for g in leads:
        if not leads[g].get("placement_primary_frame"):
            print("%-7s NOT READABLE ON BOTH PLATFORMS - absent reading, not a reading of absence" % g)
    return 0


if __name__ == "__main__":
    sys.exit(main())
