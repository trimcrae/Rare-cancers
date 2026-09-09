#!/usr/bin/env python3
"""EXPR-HYPOXIA-1 sensitivity: an ABUNDANCE-MATCHED seeded-background sham control.

The shams in hypoxia_residual_attribution.py are drawn uniformly from the seeded random
background, so their mean array_percentile sits mid-range, while the frozen hypoxia set is
glycolytic and sits high. A per-sample mean of HIGH-percentile genes could track an array's
overall dynamic range rather than hypoxia. This control removes that disanalogy: each sham gene
is drawn from the background genes whose own mean array_percentile (over the labelled samples,
on BOTH platforms) is closest to the hypoxia gene it replaces.

Appends to hypoxia-residual-attribution.json. Does not modify any statistic already written.
"""
import json, os, sys, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hypoxia_residual_attribution as HR
import composition_adjusted_contrast as CC

N_SHAM, SEED, TOL = 300, 20260909, 25   # TOL = rank-neighbourhood half-width in the sorted pool
P1, P2 = HR.P1, HR.P2


def main():
    d = json.load(open(HR.SRC)); h = json.load(open(HR.HYP))
    art = json.load(open(HR.OUT))
    Hset = art["covariates"]["hypoxia_H"]["kept"]
    fr = CC.frames(d)
    cs = {}
    colsof, labof = {}, {}
    for p in (P1, P2):
        plat = d["platforms"][p]
        colsof[p] = list(plat["EMC_gsms"]) + list(plat["comparator_gsms"])
        labof[p] = np.array([1.0]*len(plat["EMC_gsms"]) + [0.0]*len(plat["comparator_gsms"]))
        cs[p] = CC.composition_scores(d, p, colsof[p])
    syms, src = fr["primary"]
    p1, p2 = CC._frame_setup(d, "primary", syms, src, cs)
    g1, g2 = HR.build_groups2(p1["Z"]), HR.build_groups2(p2["Z"])

    def pct(p, s): return HR.percentiles.__wrapped__(p, s) if False else None
    def percentiles(pkey, sym):
        t = h["targets"][pkey]; g = t["genes"].get(sym)
        if g is None: return None
        pos = {s["gsm"]: i for i, s in enumerate(t["samples"])}
        ap = g["array_percentile"]; out = np.full(len(colsof[pkey]), np.nan)
        for i, c in enumerate(colsof[pkey]):
            j = pos.get(c)
            if j is not None and j < len(ap) and ap[j] is not None: out[i] = float(ap[j])
        return out

    pool, level = {}, {}
    for p in (P1, P2):
        keep, rows = [], []
        for s in h["targets"][p]["_random_background_symbols"]:
            if s not in h["targets"][p]["genes"]: continue
            v = percentiles(p, s)
            if v is not None and np.all(np.isfinite(v)): keep.append(s); rows.append(v)
        pool[p] = {"syms": keep, "M": np.array(rows)}
        level[p] = pool[p]["M"].mean(axis=1)
    Hlevel = {p: np.array([percentiles(p, s).mean() for s in Hset]) for p in (P1, P2)}

    nbr = {}
    for p in (P1, P2):
        order = np.argsort(level[p])
        srt = level[p][order]
        nbr[p] = []
        for tgt in Hlevel[p]:
            j = int(np.searchsorted(srt, tgt))
            lo, hi = max(0, j - TOL), min(len(order), j + TOL)
            nbr[p].append(order[lo:hi])

    u1 = HR.adj_r_multi(g1, p1["G"], p1["lab"], [])
    u2 = HR.adj_r_multi(g2, p2["G"], p2["lab"], [])
    both = np.isfinite(u1) & np.isfinite(u2)
    Hcov = {p: np.array([percentiles(p, s) for s in Hset]).mean(axis=0) for p in (P1, P2)}
    a1 = HR.adj_r_multi(g1, p1["G"], p1["lab"], [Hcov[P1]])
    a2 = HR.adj_r_multi(g2, p2["G"], p2["lab"], [Hcov[P2]])
    both &= np.isfinite(a1) & np.isfinite(a2)
    ru = HR.paired_rate(u1, u2, both); rH = HR.paired_rate(a1, a2, both)

    pyr = random.Random(SEED)
    rows = []
    for _ in range(N_SHAM):
        cov, lev = {}, {}
        for p in (P1, P2):
            idx = [pyr.choice(list(n)) for n in nbr[p]]
            cov[p] = pool[p]["M"][idx].mean(axis=0)
            lev[p] = float(pool[p]["M"][idx].mean())
        b1 = HR.adj_r_multi(g1, p1["G"], p1["lab"], [cov[P1]])
        b2 = HR.adj_r_multi(g2, p2["G"], p2["lab"], [cov[P2]])
        r = HR.paired_rate(b1, b2, both)
        lr = [abs(CC.spearman(cov[p], labof[p])) for p in (P1, P2)]
        rows.append((r, float(np.mean(lr)), float(np.mean([lev[P1], lev[P2]]))))
    S = np.array([r[0] for r in rows]); X = np.array([r[1] for r in rows])
    LV = np.array([r[2] for r in rows])
    slope, icpt = np.polyfit(X, S, 1)
    hr = art["covariates"]["association_with_EMC_label"]["H"]
    h_absr = float(np.mean([abs(hr[P1]), abs(hr[P2])]))
    band = {}
    for w in (0.05, 0.10, 0.15):
        m = np.abs(X - h_absr) <= w
        band["pm%.2f" % w] = {"n": int(m.sum()),
                              "mean_adjusted_rate": round(float(S[m].mean()), 4) if m.sum() else None,
                              "min_adjusted_rate": round(float(S[m].min()), 4) if m.sum() else None,
                              "n_at_or_below_H": int((S[m] <= rH).sum()) if m.sum() else None,
                              "one_sided_p": round(float((S[m] <= rH).sum()+1)/(int(m.sum())+1), 4) if m.sum() else None}
    art["abundance_matched_sham_control"] = {
        "_what": ("Sensitivity control: shams drawn from the seeded random background but MATCHED, "
                  "gene by gene, to the mean array_percentile of the hypoxia gene they replace, on "
                  "each platform separately. Removes the disanalogy that the frozen hypoxia set is "
                  "glycolytic and therefore high-abundance while uniform shams are mid-range."),
        "n_sham": int(S.size), "draw_seed": SEED, "neighbourhood_half_width_in_ranks": TOL,
        "mean_abundance_H": {p: round(float(Hlevel[p].mean()), 4) for p in (P1, P2)},
        "mean_abundance_sham": round(float(LV.mean()), 4),
        "mean_abundance_uniform_pool": {p: round(float(level[p].mean()), 4) for p in (P1, P2)},
        "unadjusted_rate": round(ru, 4), "observed_H_adjusted_rate": round(rH, 4),
        "sham_adjusted_rate": {"mean": round(float(S.mean()), 4), "sd": round(float(S.std(ddof=1)), 4),
                               "min": round(float(S.min()), 4), "max": round(float(S.max()), 4)},
        "sham_mean_abs_label_r": {"mean": round(float(X.mean()), 4), "max": round(float(X.max()), 4)},
        "generic_label_correlation_matched_baseline": {
            "slope": round(float(slope), 4), "intercept": round(float(icpt), 4),
            "H_mean_abs_label_r": round(h_absr, 4),
            "generic_prediction_at_H": round(float(icpt + slope*h_absr), 4),
            "H_beats_generic_baseline_by": round(float(icpt + slope*h_absr - rH), 4)},
        "matched_bands_around_H_label_r": band,
        "n_sham_at_or_below_H_overall": int((S <= rH).sum()),
    }
    json.dump(art, open(HR.OUT, "w"), indent=1)
    print("abundance H=%s sham=%.4f uniform=%s" % (art["abundance_matched_sham_control"]["mean_abundance_H"],
          LV.mean(), art["abundance_matched_sham_control"]["mean_abundance_uniform_pool"]))
    print("unadj=%.4f  H=%.4f  sham mean=%.4f sd=%.4f min=%.4f" % (ru, rH, S.mean(), S.std(ddof=1), S.min()))
    print("generic prediction at H = %.4f" % (icpt + slope*h_absr))
    print("bands: %s" % json.dumps(band))
    print("sham label r mean=%.4f max=%.4f ; H=%.4f" % (X.mean(), X.max(), h_absr))
    print("n sham <= H overall: %d/%d" % ((S <= rH).sum(), S.size))


if __name__ == "__main__":
    main()
