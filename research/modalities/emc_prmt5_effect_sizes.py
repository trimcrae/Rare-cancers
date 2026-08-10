#!/usr/bin/env python3
"""Effect sizes, intervals and family-composition sensitivities for the EMC PRMT5/MTAP manuscript.

WHY THIS MODULE EXISTS. `emc-expression-panels.json` reports every contrast as a Welch t and a
difference in units of the array's own probe SD, and `emc-prmt5-multiplicity.json` reports one
family-wise adjusted p per gene over one family. A statistical review of
`emc-mtap-prmt5-hypothesis.md` raised four things that neither artifact carries and that a reader
of a cancer-genetics journal needs:

  1  EFFECT SIZE ON AN INTERPRETABLE SCALE, WITH AN INTERVAL. A t says nothing about how large a
     difference is. Both platforms store values on a log2 scale — single-channel log2 intensity on
     GPL6244, two-colour log2 ratio on GPL3290 — so a difference of means in the array's own units,
     with a Welch interval, is available and is reported here beside the t.
     ⚠ On GPL3290 a "fold" is a ratio of two log-ratios taken against DIFFERENT reference pools, so
     it is a relative difference between arms and not a fold difference in transcript abundance.
     The field is named accordingly and the caveat travels with it.

  2  MINIMUM DETECTABLE EFFECT. A negative is only as strong as the effect the design could have
     seen. For each gene this reports the standardised difference detectable at 80% power against a
     two-sided uncorrected 0.05, converted back to the gene's own log2 scale.

  3  THE FAMILY IS A CHOICE AND IT DETERMINES THE ANSWER. The adjusted p the manuscript reports is
     computed over one family; the same code path over other defensible families gives values three
     orders of magnitude apart. This recomputes the max-statistic correction over four families —
     the genes the paper reports, the curated panel cache, the merged family the paper uses, and
     the merged family restricted to genes measured in every sample — so the manuscript can report
     a range and name which family its inference is over rather than quoting one point from it.

  4  DISCLOSURES THE PROSE ASSERTED WITHOUT A NUMBER. The between-arm variance-ratio distribution
     (a permutation test is exact for exchangeability, not for a location null); the standard-error
     percentile of each reported gene within its family (a large t can come from a small SE rather
     than a large difference); per-class exact tests and sample-overlap counts behind the
     class-separation claim; and the only reference-informative contrast GPL3290 admits, which is
     comparator against comparator.

WHAT THIS IS NOT. Not a re-fetch, not a new measurement, and not a correction of any published
value. Every input is a committed cache. Nothing here asserts efficacy, safety, a therapeutic
window or clinical readiness for any agent.

DOUBLE ENTRY. Every Welch t re-derived here is compared against the committed value in
`emc-expression-panels.json`, and the module refuses to emit if any disagrees.

Usage:
  python3 research/modalities/emc_prmt5_effect_sizes.py           # write the artifact
  python3 research/modalities/emc_prmt5_effect_sizes.py --check   # recompute and diff
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = os.path.join(HERE, "emc-expression-panels.json")
INPUTS = os.path.join(HERE, "emc-expression-panels-inputs.json")
BACKGROUND = os.path.join(HERE, "emc-hypoxia-null-background.json")
MULTI = os.path.join(HERE, "emc-prmt5-multiplicity.json")
OUT = os.path.join(HERE, "emc-prmt5-effect-sizes.json")

P6244 = "GSE24369_series_matrix.txt.gz"
P3290 = "GSE4303-GPL3290_series_matrix.txt.gz"
PLATFORM_LABEL = {P6244: "GPL6244", P3290: "GPL3290"}
VALUE_SCALE = {P6244: "log2 single-channel intensity",
               P3290: "log2 two-colour ratio against a reference pool"}

REPORTED = ("PRMT5", "MAT2A", "WDR77", "MTAP", "CDKN2A", "CDKN2B", "NR4A3", "ENO3", "MKI67")

#: The panel's own minimum arm size. A gene with fewer values in either arm is not scored.
ARM_FLOOR = 3

#: Fixed seed and labelling count for the GPL6244 correction, matching `emc_prmt5_multiplicity.py`
#: so the two artifacts' GPL6244 columns are computed on the same draw.
SEED = 20260810
N_DRAW = 20000


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ── Welch, with an interval ───────────────────────────────────────────────────────────────

def _t_crit(df, p=0.975):
    """Two-sided critical value of Student's t, by bisection on the CDF. stdlib only."""
    lo, hi = 0.0, 200.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _t_cdf(t, df):
    """Student's t CDF via the regularised incomplete beta function."""
    x = df / (df + t * t)
    ib = _betainc(df / 2.0, 0.5, x)
    return 1 - 0.5 * ib if t > 0 else 0.5 * ib


def _betainc(a, b, x):
    """Regularised incomplete beta I_x(a, b) by continued fraction (Lentz)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1 - x) * b - lbeta)
    if x < (a + 1) / (a + b + 2):
        return front * _betacf(a, b, x) / a
    return 1 - math.exp(math.log(1 - x) * b + math.log(x) * a - lbeta) * _betacf(b, a, 1 - x) / b


def _betacf(a, b, x):
    tiny = 1e-30
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 3e-10:
            break
    return h


def _welch(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
    se2 = va / na + vb / nb
    if se2 <= 0:
        return None
    se = math.sqrt(se2)
    df = se2 ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    return {"n_EMC": na, "n_comparator": nb, "mean_EMC": ma, "mean_comparator": mb,
            "difference": ma - mb, "se": se, "t": (ma - mb) / se, "df": df,
            "sd_EMC": math.sqrt(va), "sd_comparator": math.sqrt(vb)}


def _min_detectable(w, power_z=0.8416, alpha_z=1.9600):
    """Standardised difference detectable at 80% power, two-sided 0.05, at these arm sizes,
    converted back to the gene's own log2 scale using the pooled SD."""
    na, nb = w["n_EMC"], w["n_comparator"]
    pooled = math.sqrt(((na - 1) * w["sd_EMC"] ** 2 + (nb - 1) * w["sd_comparator"] ** 2)
                       / (na + nb - 2))
    d = (alpha_z + power_z) * math.sqrt(1.0 / na + 1.0 / nb)
    return {"standardised_difference": round(d, 4), "pooled_sd_log2": round(pooled, 4),
            "detectable_difference_log2": round(d * pooled, 4),
            "detectable_relative_difference_fold": round(2 ** (d * pooled), 3),
            "_definition": "the smallest true difference this design would detect in 80% of "
                           "repetitions against a two-sided uncorrected 0.05. Against the "
                           "family-wise threshold the paper actually applies it is several times "
                           "larger."}


# ── family-composition sensitivity for the max-statistic correction ───────────────────────

def _sample_classes(panels, key):
    return [r["class"] for r in panels["gene_reads"]["MTAP"][key]["per_sample"]]


# ⛔ THE CORRECTION IS NOT RE-IMPLEMENTED HERE. `emc_prmt5_multiplicity` owns the reduction, the
# arm floor, the labelling draw and the max statistic, and a second implementation of any of them
# would drift from the published value silently. This module imports that one and varies exactly
# one thing: which symbols are in the family.
def _mult():
    sys.path.insert(0, HERE)
    import emc_prmt5_multiplicity as m
    return m


def _family_adjusted_p(m, zrows, family, emc, comp, A, gene):
    """Max-statistic FWER adjusted p for `gene` over `family`, on the labelling matrix `A`,
    using `emc_prmt5_multiplicity`'s own arm-floor-zeroed |t| kernel."""
    import numpy as np
    idx = sorted(set(emc) | set(comp))
    emc_set = set(emc)
    fam = []
    for g in sorted(family):
        row = [zrows[g][i] for i in idx]
        a = [row[k] for k, i in enumerate(idx) if i in emc_set and row[k] is not None]
        b = [row[k] for k, i in enumerate(idx) if i not in emc_set and row[k] is not None]
        if len(a) >= ARM_FLOOR and len(b) >= ARM_FLOOR and m._welch_t(a, b):
            fam.append(g)
    if gene not in fam:
        return None
    raw = [[zrows[g][i] for i in idx] for g in fam]
    M = np.array([[0.0 if v is None else 1.0 for v in r] for r in raw], dtype=np.float64)
    Z = np.array([[0.0 if v is None else float(v) for v in r] for r in raw], dtype=np.float64)
    Q = Z * Z
    n_all, s_all, q_all = M.sum(axis=1), Z.sum(axis=1), Q.sum(axis=1)
    block = np.arange(len(fam))
    obs_col = np.zeros((len(idx), 1), dtype=np.float64)
    for k, i in enumerate(idx):
        if i in emc_set:
            obs_col[k, 0] = 1.0
    observed = float(m._t_matrix(np, Z, M, Q, n_all, s_all, q_all, block, obs_col)[
        fam.index(gene), 0])
    hits = 0
    step = max(1, 4_000_000 // max(1, len(fam)))
    for start in range(0, A.shape[1], step):
        chunk = A[:, start:start + step]
        mx = m._t_matrix(np, Z, M, Q, n_all, s_all, q_all, block, chunk).max(axis=0)
        hits += int((mx >= observed - 1e-12).sum())
    return {"observed_abs_t": round(observed, 4), "family_size_genes": len(fam),
            "n_labelings": int(A.shape[1]), "at_least_as_extreme": hits,
            "fwer_adjusted_p": round(hits / A.shape[1], 6)}


def _labelling_matrix(m, n, n_emc, exhaustive):
    """The same labellings `emc_prmt5_multiplicity` uses: exhaustive on GPL3290, the same
    fixed-seed draw of `B_SAMPLED` on GPL6244."""
    import numpy as np
    from itertools import combinations
    if exhaustive:
        cols = list(combinations(range(n), n_emc))
        A = np.zeros((n, len(cols)), dtype=np.float64)
        for j, c in enumerate(cols):
            A[list(c), j] = 1.0
        return A
    rng = np.random.default_rng(m.SEED)
    A = np.zeros((n, m.B_SAMPLED), dtype=np.float64)
    for j in range(m.B_SAMPLED):
        A[rng.choice(n, size=n_emc, replace=False), j] = 1.0
    return A


# ── per-class tests behind the class-separation claim ─────────────────────────────────────

def _per_class(panels, multi, gene, key):
    """Exact permutation of the means, EMC against each deposited class separately."""
    import itertools
    rec = panels["gene_reads"][gene][key]
    by_class = {}
    for r in rec["per_sample"]:
        if r["z_vs_array"] is not None:
            by_class.setdefault(r["class"], []).append(r["z_vs_array"])
    excluded = ((multi.get("per_platform") or {}).get(key) or {}).get("excluded_sample_z") or {}
    for s in (excluded.get("samples") or {}).values():
        v = (s.get("z_vs_array") or {}).get(gene)
        if v is not None:
            by_class.setdefault(s["class"], []).append(v)
    emc = by_class.get("EMC") or []
    out = {}
    for cls, vals in sorted(by_class.items()):
        if cls == "EMC" or not vals:
            continue
        pool = emc + vals
        n, k = len(pool), len(emc)
        obs = abs(sum(emc) / k - sum(vals) / len(vals))
        total = math.comb(n, k)
        if total > 2_000_000:
            out[cls] = {"n_class": len(vals), "note": "labelling count too large to enumerate"}
            continue
        hit = 0
        for c in itertools.combinations(range(n), k):
            sel = set(c)
            a = [pool[i] for i in sel]
            b = [pool[i] for i in range(n) if i not in sel]
            if abs(sum(a) / k - sum(b) / len(b)) >= obs - 1e-12:
                hit += 1
        out[cls] = {"n_class": len(vals),
                    "median_EMC_minus_class": round(
                        _median(emc) - _median(vals), 4),
                    "mean_EMC_minus_class": round(sum(emc) / k - sum(vals) / len(vals), 4),
                    "labelings": total, "at_least_as_extreme": hit,
                    "exact_two_sided_p": round(hit / total, 6),
                    "bonferroni_within_figure_x4": round(min(1.0, 4 * hit / total), 5)}
    # sample overlap, which is what "separates" has to mean at the sample level
    comparator_tumours = [v for c, vals in by_class.items() if c not in ("EMC",)
                          for v in vals if not c.startswith("pooled")]
    out["_overlap"] = {
        "n_comparator_tumour_samples": len(comparator_tumours),
        "n_at_or_above_the_lowest_EMC_sample": sum(1 for v in comparator_tumours
                                                   if v >= min(emc)) if emc else None,
        "n_normal_muscle_above_the_EMC_median": sum(
            1 for c, vals in by_class.items() if c.startswith("pooled")
            for v in vals if v > _median(emc)) if emc else None,
        "_note": "these tests carry no correction for the number of genes on the array, so they "
                 "do not bear on the family-wise result.",
    }
    return out


def _median(v):
    s = sorted(v)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def compute():
    panels = _load(PANELS)
    inputs = _load(INPUTS)
    background = _load(BACKGROUND)
    multi = _load(MULTI)

    res = {
        "_what": "effect sizes with intervals, minimum detectable effects, the family-composition "
                 "sensitivity of the multiplicity correction, and four disclosures the manuscript "
                 "prose asserted without a number.",
        "_this_asserts_nothing_about_any_agent": (
            "every quantity is a property of two archival expression deposits."),
        "_source_artifacts": [os.path.basename(p) for p in (PANELS, INPUTS, BACKGROUND, MULTI)],
        "per_platform": {},
    }

    for key in (P6244, P3290):
        plat = PLATFORM_LABEL[key]
        classes = _sample_classes(panels, key)
        n = len(classes)
        emc_idx = [i for i, c in enumerate(classes) if c == "EMC"]
        comp_idx = [i for i, c in enumerate(classes) if c != "EMC"]

        # 1 + 2 — effect sizes and minimum detectable effects, on the array's own log2 scale
        eff = {}
        for gene in REPORTED:
            rec = panels["gene_reads"].get(gene, {}).get(key)
            if not rec or not rec.get("readable"):
                eff[gene] = {"readable": False}
                continue
            a = [r["value"] for r in rec["per_sample"] if r["class"] == "EMC"
                 and r["value"] is not None]
            b = [r["value"] for r in rec["per_sample"] if r["class"] != "EMC"
                 and r["value"] is not None]
            w = _welch(a, b)
            za = [r["z_vs_array"] for r in rec["per_sample"] if r["class"] == "EMC"
                  and r["z_vs_array"] is not None]
            zb = [r["z_vs_array"] for r in rec["per_sample"] if r["class"] != "EMC"
                  and r["z_vs_array"] is not None]
            wz = _welch(za, zb)
            if w is None or wz is None:
                eff[gene] = {"readable": True, "_status": "arm too small to score"}
                continue
            committed = (rec.get("welch_EMC_vs_comparator") or {}).get("t")
            scored = (len(za) >= ARM_FLOOR and len(zb) >= ARM_FLOOR
                      and committed is not None)
            if scored and abs(wz["t"] - committed) > 0.01:
                raise SystemExit(f"double-entry failure: {gene} on {plat} re-derives "
                                 f"t={wz['t']:.4f} against committed {committed}")
            tc = _t_crit(w["df"])
            eff[gene] = {
                "readable": True,
                "n_probes_mapping": rec.get("n_probes_mapping"),
                "value_scale": VALUE_SCALE[key],
                "n_EMC_with_a_value": w["n_EMC"], "n_comparator_with_a_value": w["n_comparator"],
                "scored_by_the_panel": scored,
                "difference_log2": round(w["difference"], 4),
                "ci95_log2": [round(w["difference"] - tc * w["se"], 4),
                              round(w["difference"] + tc * w["se"], 4)],
                "relative_difference_fold": round(2 ** w["difference"], 3),
                "ci95_relative_difference_fold": [
                    round(2 ** (w["difference"] - tc * w["se"]), 3),
                    round(2 ** (w["difference"] + tc * w["se"]), 3)],
                "sd_EMC_log2": round(w["sd_EMC"], 4),
                "sd_comparator_log2": round(w["sd_comparator"], 4),
                "t_on_the_log2_scale": round(w["t"], 4),
                "t_committed_on_the_z_scale": committed,
                "minimum_detectable_effect": _min_detectable(w),
            }

        # 4a — between-arm variance ratios across every scored gene
        ratios = []
        for gene, per in panels["gene_reads"].items():
            rec = per.get(key)
            if not rec or not rec.get("readable"):
                continue
            za = [r["z_vs_array"] for r in rec["per_sample"] if r["class"] == "EMC"
                  and r["z_vs_array"] is not None]
            zb = [r["z_vs_array"] for r in rec["per_sample"] if r["class"] != "EMC"
                  and r["z_vs_array"] is not None]
            if len(za) < ARM_FLOOR or len(zb) < ARM_FLOOR:
                continue
            ma, mb = sum(za) / len(za), sum(zb) / len(zb)
            va = sum((x - ma) ** 2 for x in za) / (len(za) - 1)
            vb = sum((x - mb) ** 2 for x in zb) / (len(zb) - 1)
            if vb > 0:
                ratios.append(va / vb)
        ratios.sort()
        outside = sum(1 for r in ratios if r < 0.5 or r > 2.0)

        # 4b — SE percentile of each reported gene within the correction's family
        cache = inputs["targets"][key]["genes"]
        se_all = []
        for _sym, rec in cache.items():
            vals = rec.get("values")
            if not vals:
                continue
            a = [vals[i] for i in emc_idx if vals[i] is not None]
            b = [vals[i] for i in comp_idx if vals[i] is not None]
            if len(a) < ARM_FLOOR or len(b) < ARM_FLOOR:
                continue
            w = _welch(a, b)
            if w:
                se_all.append(w["se"])
        se_all.sort()
        se_pct = {}
        for gene in REPORTED:
            e = eff.get(gene, {})
            if not e.get("readable") or "difference_log2" not in e:
                continue
            rec = panels["gene_reads"][gene][key]
            a = [r["value"] for r in rec["per_sample"] if r["class"] == "EMC"
                 and r["value"] is not None]
            b = [r["value"] for r in rec["per_sample"] if r["class"] != "EMC"
                 and r["value"] is not None]
            w = _welch(a, b)
            below = sum(1 for s in se_all if s < w["se"])
            se_pct[gene] = round(below / len(se_all), 4) if se_all else None

        res["per_platform"][key] = {
            "gse": inputs["targets"][key]["gse"],
            "platform": plat,
            "value_scale": VALUE_SCALE[key],
            "_fold_caveat_on_two_colour": (
                "on GPL3290 every value is a log2 ratio to a reference pool and the arms do not "
                "share one, so a 'fold' is a relative difference between arms and not a fold "
                "difference in transcript abundance."
                if key == P3290 else None),
            "effect_sizes": eff,
            "between_arm_variance_ratios": {
                "_what": "var(EMC)/var(comparator) of the within-array z, across every gene the "
                         "panel scores on this platform. A permutation test is exact for the null "
                         "of exchangeability, not for a null of equal means; when the arms differ "
                         "in scale, rejection can be produced by that difference.",
                "n_genes": len(ratios),
                "frac_outside_0.5_to_2": round(outside / len(ratios), 4) if ratios else None,
                "p10": round(ratios[int(0.10 * len(ratios))], 4) if ratios else None,
                "p50": round(ratios[int(0.50 * len(ratios))], 4) if ratios else None,
                "p90": round(ratios[int(0.90 * len(ratios))], 4) if ratios else None,
            },
            "standard_error_percentile_within_the_family": {
                "_what": "the fraction of scored genes on this platform whose Welch standard "
                         "error is smaller than this gene's. A t can be large because the "
                         "difference is large or because the standard error is small.",
                "n_genes_in_the_reference_set": len(se_all),
                "per_gene": se_pct,
            },
        }

    # 3 — family-composition sensitivity, both platforms, on the owning module's own machinery
    m = _mult()
    fam = {}
    for key, exhaustive in ((P6244, False), (P3290, True)):
        plat = PLATFORM_LABEL[key]
        t = inputs["targets"][key]
        nt = background["targets"][key]
        merged_genes, _n_shared = m._merge_caches(t, nt)
        classes = m._classes(t)
        emc, comp = m._arms(classes)
        idx = sorted(set(emc) | set(comp))
        zrows_merged = m._z_rows({**t, "genes": merged_genes})
        zrows_panel = m._z_rows(t)
        complete = {g for g, row in zrows_merged.items()
                    if all(row[i] is not None for i in idx)}
        A = _labelling_matrix(m, len(idx), len(emc), exhaustive)
        rows = {}
        for name, family in (
                ("the_genes_the_paper_reports", [g for g in REPORTED if g in zrows_merged]),
                ("the_curated_panel_cache", list(zrows_panel)),
                ("the_merged_family_the_paper_uses", list(zrows_merged)),
                ("the_merged_family_complete_cases_only", sorted(complete))):
            r = _family_adjusted_p(m, zrows_merged, family, emc, comp, A, "PRMT5")
            if r:
                rows[name] = r
        fam[plat] = {
            "_labelings": {"kind": "exhaustive" if exhaustive else "fixed-seed sample",
                           "n": int(A.shape[1]), "seed": None if exhaustive else m.SEED},
            "_computed_by": "emc_prmt5_multiplicity's own reduction, arm floor and max-statistic "
                            "kernel, with the family as the only thing varied.",
            "PRMT5_adjusted_p_by_family": rows,
            "_reading": "the adjusted p is a property of the family, not of the data. A single "
                        "value quoted without its family is uninterpretable.",
        }
    res["family_composition_sensitivity"] = fam

    # 4c — per-class tests behind the class-separation claim (GPL6244 only; GPL3290 has 3+3)
    res["per_class_tests_GPL6244"] = _per_class(panels, multi, "PRMT5", P6244)

    # 4d — the only reference-informative contrast GPL3290 admits
    rec = panels["gene_reads"]["PRMT5"][P3290]
    dfsp = [r["z_vs_array"] for r in rec["per_sample"] if r["class"] == "DFSP"]
    gist = [r["z_vs_array"] for r in rec["per_sample"] if r["class"] == "GIST"]
    w = _welch(dfsp, gist)
    res["reference_informative_contrast_GPL3290"] = {
        "_what": "DFSP (reference `CRH`) against GIST (reference `UHR`). Neither shares the EMC "
                 "arm's `CRH-mRNA` label, so this is the only contrast on the platform in which "
                 "the reference pool differs and the disease class is held to the comparator arm.",
        "gene": "PRMT5", "n_DFSP": len(dfsp), "n_GIST": len(gist),
        "t_DFSP_vs_GIST": round(w["t"], 4) if w else None,
        "_reading": "a t near zero says the two reference pools do not move this gene between the "
                    "two comparator halves. It does not make either half reference-matched to EMC.",
    }

    # 4e — the two comparator arrays that carry MKI67 on GPL3290
    mk = panels["gene_reads"]["MKI67"][P3290]
    comp = sorted([r for r in mk["per_sample"]
                   if r["class"] != "EMC" and r["z_vs_array"] is not None],
                  key=lambda r: r["z_vs_array"])
    mk_emc = [r["z_vs_array"] for r in mk["per_sample"]
              if r["class"] == "EMC" and r["z_vs_array"] is not None]
    res["MKI67_GPL3290_basis"] = {
        "_what": "the cellularity control's GPL3290 reading, by sample, because the contrast is "
                 "carried by the comparator arm's two most extreme arrays rather than by high "
                 "proliferation in EMC.",
        "n_EMC_with_a_value": len(mk_emc),
        "comparator_z_ascending": [round(r["z_vs_array"], 3) for r in comp],
        "EMC_z_range": [round(min(mk_emc), 3), round(max(mk_emc), 3)],
        "EMC_mean_array_percentile": mk["EMC"]["mean_array_percentile"],
        "comparator_mean_array_percentile": mk["comparator"]["mean_array_percentile"],
    }

    # 4f — cache sizes, because the manuscript described the family by the caches it merges
    res["cache_sizes"] = {}
    for key in (P6244, P3290):
        t = inputs["targets"][key]
        merged_genes, _n = m._merge_caches(t, background["targets"][key])
        zr = m._z_rows({**t, "genes": merged_genes})
        classes = m._classes(t)
        emc, comp = m._arms(classes)
        scored = sum(1 for row in zr.values()
                     if sum(1 for i in emc if row[i] is not None) >= ARM_FLOOR
                     and sum(1 for i in comp if row[i] is not None) >= ARM_FLOOR)
        res["cache_sizes"][PLATFORM_LABEL[key]] = {
            "n_symbols_the_two_caches_hold": len(zr),
            "n_symbols_that_clear_the_arm_floor_and_enter_the_family": scored,
            "n_dropped_by_the_arm_floor": len(zr) - scored,
        }
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--check", action="store_true",
                    help="recompute and diff against the committed artifact")
    args = ap.parse_args(argv)
    res = compute()
    if args.check:
        if not os.path.exists(OUT):
            print("no artifact to check against", file=sys.stderr)
            return 1
        old = _load(OUT)
        drift = [k for k in res if old.get(k) != res[k]]
        drift += [k for k in old if k not in res]
        print("REPRODUCES" if not drift else f"DRIFT in: {sorted(set(drift))}")
        return 0 if not drift else 1
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    for key, rec in res["per_platform"].items():
        print(f"{rec['platform']} ({rec['value_scale']}):")
        for gene, e in rec["effect_sizes"].items():
            if not e.get("readable") or "difference_log2" not in e:
                continue
            print(f"    {gene:<7} {e['difference_log2']:+.3f} log2 "
                  f"[{e['ci95_log2'][0]:+.3f}, {e['ci95_log2'][1]:+.3f}]  "
                  f"{e['relative_difference_fold']:.2f}x  MDE "
                  f"{e['minimum_detectable_effect']['detectable_relative_difference_fold']:.2f}x")
    for plat, f in res["family_composition_sensitivity"].items():
        print(f"{plat} PRMT5 adjusted p by family:")
        for name, r in f["PRMT5_adjusted_p_by_family"].items():
            print(f"    {name:<42} n={r['family_size_genes']:>5}  p={r['fwer_adjusted_p']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
