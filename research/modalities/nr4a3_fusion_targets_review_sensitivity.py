#!/usr/bin/env python3
"""Sensitivity analyses added in revision: what the size-matched null is, and what it is not.

Offline, CPU-only, pure stdlib, deterministic. Reads two committed artifacts and writes one:

    nr4a3-fusion-targets-inputs.json   (per-sample values, background moments, the seeded 4,000-symbol
                                        null pool, sample annotations)
    nr4a3-fusion-targets.json          (the primary artifact: set definitions, readable membership,
                                        the committed bands this module must reproduce)
        -> nr4a3-fusion-targets-review-sensitivity.json

Every block here answers a specific objection raised against the manuscript's empirical null. Nothing
in this module re-reads a series matrix, touches the network, or supersedes a number the primary
artifact owns: where the two overlap, this module ASSERTS agreement and refuses to write on a
mismatch, which is the same discipline the other producers in this lane use.

Blocks, and the objection each answers.

  1. closed_form            The null is an INDEPENDENCE null. If so, `null_sd x sqrt(n)` is a
                            platform constant and the whole 4,000-draw resampling is reproduced by
                            `offset +/- 1.96 * sigma_platform / sqrt(n_readable)`. Measured here
                            rather than argued, because it decides how the method must be described.
  2. inter_gene_correlation The correction the independence null omits. Mean pairwise correlation
                            rho-bar of each real set's member genes across samples, the variance
                            inflation factor 1 + (n-1)*rho-bar, and the inflated threshold beside the
                            uninflated one. A positive that survives only the uninflated threshold is
                            marked.
  3. set_D_without_shared   Set D shares DKK1, MAN1A1 and NMB with set E, which is derived from the
                            GPL3290 cohort itself. Set D re-scored without them, with its own
                            size-matched null at the reduced size.
  4. per_gene_missingness   The size-1 band is drawn once per platform and applied to genes measured
                            on fewer samples. Redrawn under each gene's own observed sample set.
  5. seed_sensitivity       The 97.5th percentile under 20 further draw seeds. ⚠ This measures
                            MONTE-CARLO error only. The 4,000-symbol pool itself cannot be redrawn
                            from a committed artifact, so pool-composition error is NOT bounded here
                            and the artifact says so rather than implying a completeness it lacks.
  6. matched_nulls          Size matching alone ignores expression level and detection rate. Two
                            further nulls whose draws are matched to the real set's decile
                            composition on each.
  7. t_scale_null           The manuscript quotes a Welch t against a null computed on delta. The
                            null distribution of t itself, at the same set size.
  8. detectability          Replaces the power language. The set-level delta with an exact
                            label-permutation confidence interval, and the smallest true shift this
                            design would place outside the band with 80% probability.
  9. muscle_marker_nulls    The muscle-admixture control reports four differences with no null, in a
                            paper whose thesis is that a difference without a null is uninterpretable.
                            The four markers put through the same size-1 null the class-A genes face.
"""
from __future__ import annotations

import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "nr4a3-fusion-targets-inputs.json")
SECONDARY_PATH = os.path.join(HERE, "emc-expression-panels-inputs.json")
PRIMARY = os.path.join(HERE, "nr4a3-fusion-targets.json")
OUT = os.path.join(HERE, "nr4a3-fusion-targets-review-sensitivity.json")

PLATFORMS = {
    "GPL6244": "GSE24369_series_matrix.txt.gz",
    "GPL3290": "GSE4303-GPL3290_series_matrix.txt.gz",
}
SEED = 20260807
N_DRAWS = 4000
MIN_PER_ARM = 3


# ---------------------------------------------------------------- primitives
def welch(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    se2 = va / na + vb / nb
    if se2 <= 0:
        return None
    t = (ma - mb) / math.sqrt(se2)
    df = se2 ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    return {"delta": ma - mb, "t": t, "df": df, "se": math.sqrt(se2)}


def quantile(sorted_xs, q):
    """Linear-interpolated quantile; matches the convention the primary producer used."""
    if not sorted_xs:
        return None
    if len(sorted_xs) == 1:
        return sorted_xs[0]
    pos = q * (len(sorted_xs) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_xs) - 1)
    frac = pos - lo
    return sorted_xs[lo] * (1 - frac) + sorted_xs[hi] * frac


def pearson(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    xs2 = [p[0] for p in pairs]
    ys2 = [p[1] for p in pairs]
    mx, my = statistics.fmean(xs2), statistics.fmean(ys2)
    sxx = sum((x - mx) ** 2 for x in xs2)
    syy = sum((y - my) ** 2 for y in ys2)
    if sxx <= 0 or syy <= 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs2, ys2))
    return sxy / math.sqrt(sxx * syy)


class Platform:
    """One array platform's z-matrix, arms, null pool and set membership."""

    def __init__(self, label, inputs, primary):
        self.label = label
        key = PLATFORMS[label]
        self.key = key
        t = inputs["targets"][key]
        p = primary["platforms"][key]
        self.n_samples = t["n_samples"]
        self.bg = t["background_per_sample"]
        self.gsms = [s["gsm"] for s in t["samples"]]
        self.offset = p["global_offset"]["welch"]["delta_a_minus_b"]
        self.universe = p["n_distinct_symbols_on_platform"]
        self.pool_spec = p["null_pool_spec"]

        # arms, taken from the primary artifact's own per-sample class labels (one home for the
        # grouping) and mapped onto this matrix by GSM, because the two files order samples
        # differently and GSE24369 excludes 7 samples from both arms.
        per_sample = primary["gene_reads"]["ENO3"][key]["per_sample"]
        cls = {s["gsm"]: s["class"] for s in per_sample}
        self.classes = [cls.get(g) for g in self.gsms]
        self.emc = [i for i, c in enumerate(self.classes) if c == "EMC"]
        self.cmp = [i for i, c in enumerate(self.classes) if c is not None and c != "EMC"]

        self.z_gene = {g: self._z(v["values"]) for g, v in t["genes"].items()}
        # ⚠ A GENE THIS MODULE CANNOT SEE IS NOT AN ABSENT GENE. `PYGM` is a muscle marker the
        # confound module reads and this module's own input cache does not carry, because the two
        # caches were built for different gene lists. `nr4a3_fusion_targets_confounds.py` already
        # unions them for exactly this reason; the same union is done here, guarded on the sample
        # order and the per-sample background matching exactly, so a merged gene is on one scale
        # with the rest. Without this, a marker would silently drop out of a control panel.
        self.merged_from_secondary = []
        sec = SECONDARY.get("targets", {}).get(key)
        if sec and [s["gsm"] for s in sec["samples"]] == self.gsms:
            same_bg = all(abs(a["mean"] - b["mean"]) < 1e-9 and abs(a["sd"] - b["sd"]) < 1e-9
                          for a, b in zip(sec["background_per_sample"], self.bg))
            if same_bg:
                for g, v in sec["genes"].items():
                    if g not in self.z_gene:
                        self.z_gene[g] = self._z(v["values"])
                        self.merged_from_secondary.append(g)
        self.z_pool = {g: self._z(v) for g, v in t["null_pool_values"].items()}
        self.pool_symbols = sorted(self.z_pool)

    def _z(self, values):
        out = []
        for i, v in enumerate(values):
            if v is None:
                out.append(None)
            else:
                out.append((v - self.bg[i]["mean"]) / self.bg[i]["sd"])
        return out

    def sample_scores(self, symbols, source=None):
        """Per-sample mean z over the readable members of a set. None where a sample has none."""
        src = source if source is not None else self.z_gene
        rows = [src[s] for s in symbols if s in src]
        out = []
        for i in range(self.n_samples):
            vals = [r[i] for r in rows if r[i] is not None]
            out.append(statistics.fmean(vals) if vals else None)
        return out

    def contrast(self, scores, emc=None, cmp_=None):
        emc = self.emc if emc is None else emc
        cmp_ = self.cmp if cmp_ is None else cmp_
        a = [scores[i] for i in emc if scores[i] is not None]
        b = [scores[i] for i in cmp_ if scores[i] is not None]
        if len(a) < MIN_PER_ARM or len(b) < MIN_PER_ARM:
            return None
        w = welch(a, b)
        if w:
            w["n_EMC"], w["n_comparator"] = len(a), len(b)
        return w

    def null_deltas(self, size, seed=SEED, n_draws=N_DRAWS, pool=None):
        pool = pool if pool is not None else self.pool_symbols
        rng = random.Random(seed)
        out = []
        for _ in range(n_draws):
            draw = rng.sample(pool, size)
            c = self.contrast(self.sample_scores(draw, source=self.z_pool))
            if c:
                out.append(c["delta"])
        return sorted(out)

    def band(self, deltas):
        return quantile(deltas, 0.025), quantile(deltas, 0.975)


def emp_p(deltas, observed):
    """Two-sided empirical p with +1/+1 smoothing, the convention the primary producer uses."""
    centre = statistics.fmean(deltas)
    extreme = sum(1 for d in deltas if abs(d - centre) >= abs(observed - centre))
    return round((extreme + 1) / (len(deltas) + 1), 5)


# ---------------------------------------------------------------- blocks
def block_closed_form(plats, primary):
    out = {
        "_question": "Is the resampled band reproduced by a closed form, and does that make the null "
                     "an independence null?",
        "_reading": "null_sd x sqrt(n) is constant across set size on both platforms, which is the "
                    "signature of a null with no inter-gene correlation term. The band is therefore "
                    "the sampling distribution of a mean of n independent gene-level contrasts.",
        "per_platform": {},
    }
    for label, P in plats.items():
        rows = []
        for setname, byplat in primary["set_scores"].items():
            v = byplat.get(P.key, {})
            nc = v.get("null_calibration")
            if not nc:
                continue
            n = v["n_genes_readable"]
            rows.append({"set": setname, "n": n, "null_sd": nc["null_sd"],
                         "null_sd_x_sqrt_n": round(nc["null_sd"] * math.sqrt(n), 5),
                         "band": [nc["null_q025"], nc["null_q975"]]})
        rows.sort(key=lambda r: r["n"])
        prods = [r["null_sd_x_sqrt_n"] for r in rows]
        sigma = round(statistics.fmean(prods), 4)
        for r in rows:
            hw = 1.96 * sigma / math.sqrt(r["n"])
            pred = [round(P.offset - hw, 5), round(P.offset + hw, 5)]
            r["closed_form_band"] = pred
            r["max_abs_edge_error"] = round(max(abs(pred[0] - r["band"][0]),
                                                abs(pred[1] - r["band"][1])), 5)
            r["max_rel_edge_error"] = round(r["max_abs_edge_error"] / (1.96 * sigma / math.sqrt(r["n"])), 4)
        out["per_platform"][label] = {
            "sigma_platform": sigma,
            "global_offset": P.offset,
            "null_sd_x_sqrt_n_range": [min(prods), max(prods)],
            "null_sd_x_sqrt_n_spread_fraction": round((max(prods) - min(prods)) / statistics.fmean(prods), 4),
            "worst_relative_band_edge_error": max(r["max_rel_edge_error"] for r in rows),
            "closed_form": "band = global_offset +/- 1.96 * sigma_platform / sqrt(n_readable)",
            "sets": rows,
        }
    out["_residual"] = ("The 3-5% decline of null_sd x sqrt(n) at the largest set sizes is the "
                        "finite-population correction for sampling without replacement from a "
                        "4,000-symbol pool: 1 - (n-1)/(N-1) with N = 4000 predicts the direction and "
                        "roughly the magnitude.")
    return out


def block_correlation(plats, primary):
    out = {
        "_question": "How much does the independence null understate the threshold for a set whose "
                     "genes are correlated?",
        "_method": "rho-bar is the mean of all pairwise Pearson correlations between member genes' "
                   "per-sample z. Two versions are reported. `rho_bar_raw` uses the values as they "
                   "are, over both arms together. `rho_bar_residual` centres each gene within each "
                   "arm first, so a correlation that is only the two arms differing cannot inflate "
                   "it — this is the quantity a correlation-corrected competitive test needs, and "
                   "it is the one the inflated threshold uses. VIF = 1 + (n-1)*rho-bar; the "
                   "inflated threshold is the uninflated one times sqrt(VIF) when VIF > 1.",
        "⚠_why_both": "for a set that really does separate the arms, the raw version counts the "
                      "set's own effect as co-regulation and manufactures a large inflation. Set D "
                      "is the worked example: raw rho-bar is several times the residual one.",
        "per_platform": {},
    }
    for label, P in plats.items():
        rows = {}
        for setname, byplat in primary["set_scores"].items():
            v = byplat.get(P.key, {})
            nc = v.get("null_calibration")
            if not nc:
                continue
            members = [g for g in v["genes_readable"] if g in P.z_gene]
            n = len(members)

            def arm_centred(zs):
                out_ = list(zs)
                for arm in (P.emc, P.cmp):
                    vals = [zs[i] for i in arm if zs[i] is not None]
                    if not vals:
                        continue
                    m = statistics.fmean(vals)
                    for i in arm:
                        if out_[i] is not None:
                            out_[i] = out_[i] - m
                return out_

            resid = {g: arm_centred(P.z_gene[g]) for g in members}
            cors, cors_r = [], []
            for i in range(n):
                for j in range(i + 1, n):
                    r = pearson(P.z_gene[members[i]], P.z_gene[members[j]])
                    if r is not None:
                        cors.append(r)
                    rr = pearson(resid[members[i]], resid[members[j]])
                    if rr is not None:
                        cors_r.append(rr)
            if not cors or not cors_r:
                continue
            rho_raw = statistics.fmean(cors)
            rho = statistics.fmean(cors_r)
            vif = 1 + (n - 1) * rho
            obs = nc["observed_delta"]
            thr = nc["null_q975"] if obs >= 0 else nc["null_q025"]
            infl = thr * math.sqrt(vif) if vif > 1 else thr
            rows[setname] = {
                "n_readable": n,
                "rho_bar_raw": round(rho_raw, 4),
                "rho_bar": round(rho, 4),
                "variance_inflation_factor": round(vif, 3),
                "observed_delta": obs,
                "threshold_uninflated": thr,
                "threshold_inflated": round(infl, 5),
                "fraction_of_uninflated_threshold": round(abs(obs / thr), 3) if thr else None,
                "fraction_of_inflated_threshold": round(abs(obs / infl), 3) if infl else None,
                "clears_uninflated": abs(obs) > abs(thr),
                "clears_inflated": abs(obs) > abs(infl),
            }
        out["per_platform"][label] = rows
    return out


def block_set_d(plats, primary):
    D = primary["set_definitions"]["D_filion_table1_emc_vs_137_sarcomas"]["genes"]
    E = set(primary["set_definitions"]["E_filion_table2_overlap_with_subramanian"]["genes"])
    shared = sorted(set(D) & E)
    out = {
        "_question": "Set D is offered as an independent benchmark. It shares genes with set E, which "
                     "is defined from a top-50 list derived on GPL3290 itself.",
        "shared_with_set_E": shared,
        "per_platform": {},
    }
    for label, P in plats.items():
        readable = primary["set_scores"]["D_filion_table1_emc_vs_137_sarcomas"][P.key]["genes_readable"]
        kept = [g for g in readable if g not in E]
        full = P.contrast(P.sample_scores(readable))
        red = P.contrast(P.sample_scores(kept))
        nd_full = P.null_deltas(len(readable))
        nd_red = P.null_deltas(len(kept))
        b_full, b_red = P.band(nd_full), P.band(nd_red)
        committed = primary["set_scores"]["D_filion_table1_emc_vs_137_sarcomas"][P.key]["null_calibration"]
        out["per_platform"][label] = {
            "n_readable_full": len(readable),
            "n_shared_and_readable": len(readable) - len(kept),
            "shared_and_readable": [g for g in readable if g in E],
            "full": {
                "n": len(readable), "observed_delta": round(full["delta"], 5),
                "band": [round(b_full[0], 5), round(b_full[1], 5)],
                "fraction_of_threshold": round(abs(full["delta"] / b_full[1 if full["delta"] >= 0 else 0]), 3),
                "committed_observed_delta": committed["observed_delta"],
                "reproduces_committed_delta": abs(round(full["delta"], 4) - committed["observed_delta"]) <= 5e-4,
            },
            "without_shared_genes": {
                "n": len(kept), "observed_delta": round(red["delta"], 5),
                "band": [round(b_red[0], 5), round(b_red[1], 5)],
                "p_empirical_two_sided": emp_p(nd_red, red["delta"]),
                "fraction_of_threshold": round(abs(red["delta"] / b_red[1 if red["delta"] >= 0 else 0]), 3),
            },
        }
    return out


def block_missingness(plats, primary):
    genes = ["ENO3", "PPARG", "SEMA3C", "NR4A3", "PLAGL1", "SGK1"]
    out = {
        "_question": "The size-1 band is drawn once per platform. Genes measured on fewer samples "
                     "have a wider sampling distribution and are graded against a band that is too "
                     "narrow for them.",
        "_method": "for each gene, the size-1 null is redrawn over the same 4,000-symbol pool "
                   "restricted to the samples on which that gene has a value, so the null carries "
                   "the gene's own arm sizes. A pool symbol missing from those samples is dropped "
                   "from that draw, exactly as the real gene would be.",
        "per_platform": {},
    }
    for label, P in plats.items():
        rows = {}
        for g in genes:
            if g not in P.z_gene:
                continue
            z = P.z_gene[g]
            obs_idx = {i for i, v in enumerate(z) if v is not None}
            emc = [i for i in P.emc if i in obs_idx]
            cmp_ = [i for i in P.cmp if i in obs_idx]
            committed = primary["gene_reads"][g][P.key]
            if len(emc) < MIN_PER_ARM or len(cmp_) < MIN_PER_ARM:
                rows[g] = {"n_EMC": len(emc), "n_comparator": len(cmp_),
                           "state": "NOT_MEASURABLE — below the three-per-arm floor"}
                continue
            w = welch([z[i] for i in emc], [z[i] for i in cmp_])
            rng = random.Random(SEED)
            deltas = []
            for _ in range(N_DRAWS):
                s = rng.choice(P.pool_symbols)
                zz = P.z_pool[s]
                a = [zz[i] for i in emc if zz[i] is not None]
                b = [zz[i] for i in cmp_ if zz[i] is not None]
                if len(a) >= MIN_PER_ARM and len(b) >= MIN_PER_ARM:
                    deltas.append(statistics.fmean(a) - statistics.fmean(b))
            deltas.sort()
            lo, hi = P.band(deltas)
            plat_band = committed.get("null_calibration", {})
            rows[g] = {
                "n_EMC": len(emc), "n_comparator": len(cmp_),
                "observed_delta": round(w["delta"], 5),
                "platform_wide_band": [plat_band.get("null_q025"), plat_band.get("null_q975")],
                "own_missingness_band": [round(lo, 5), round(hi, 5)],
                "band_width_ratio_own_over_platform": (
                    round((hi - lo) / (plat_band["null_q975"] - plat_band["null_q025"]), 3)
                    if plat_band.get("null_q975") is not None else None),
                "p_empirical_two_sided_own_band": emp_p(deltas, w["delta"]),
                "outside_own_band": w["delta"] < lo or w["delta"] > hi,
                "outside_platform_band": (
                    plat_band.get("null_q025") is not None
                    and (w["delta"] < plat_band["null_q025"] or w["delta"] > plat_band["null_q975"])),
            }
        out["per_platform"][label] = rows
    return out


def block_seeds(plats, primary):
    out = {
        "_question": "How much of the reported threshold is Monte-Carlo noise in the 4,000 draws?",
        "⚠_what_this_does_not_bound": "pool-composition error. The committed artifact carries the "
                                      "4,000 symbols that were drawn and not the platform universe "
                                      "they were drawn from, so a second POOL cannot be drawn here. "
                                      "This is the spread over draw seeds at a fixed pool only.",
        "n_seeds": 20,
        "per_platform": {},
    }
    for label, P in plats.items():
        rows = {}
        for setname in ("A_plus_B_all_dna_binding", "D_filion_table1_emc_vs_137_sarcomas"):
            v = primary["set_scores"][setname][P.key]
            n = v["n_genes_readable"]
            ups = []
            for k in range(20):
                d = P.null_deltas(n, seed=SEED + 1000 + k)
                ups.append(P.band(d)[1])
            committed = v["null_calibration"]["null_q975"]
            obs = v["null_calibration"]["observed_delta"]
            rows[setname] = {
                "n": n,
                "committed_q975": committed,
                "mean_q975_over_seeds": round(statistics.fmean(ups), 5),
                "sd_q975_over_seeds": round(statistics.stdev(ups), 5),
                "range_q975": [round(min(ups), 5), round(max(ups), 5)],
                "relative_sd": round(statistics.stdev(ups) / statistics.fmean(ups), 4),
                "fraction_of_threshold_range": [
                    round(abs(obs) / max(ups), 3), round(abs(obs) / min(ups), 3)],
            }
        out["per_platform"][label] = rows
    return out


def block_matched(plats, primary):
    out = {
        "_question": "The null matches on set size only. A published target list is biased toward "
                     "well-measured genes; a uniform draw from mapped symbols is not.",
        "_method": "pool symbols are ranked into deciles on two properties measured on this "
                   "platform — mean value across samples, and detection rate (the fraction of "
                   "samples with a value). Each draw reproduces the real set's decile composition "
                   "exactly, so the matched null differs from the uniform one only in composition.",
        "per_platform": {},
    }
    for label, P in plats.items():
        t = IN_RAW["targets"][P.key]
        pool_raw = t["null_pool_values"]
        gene_raw = {g: v["values"] for g, v in t["genes"].items()}

        def mean_value(vs):
            xs = [v for v in vs if v is not None]
            return statistics.fmean(xs) if xs else None

        def detect(vs):
            return sum(1 for v in vs if v is not None) / len(vs)

        for prop, fn in (("expression_decile", mean_value), ("detection_rate_decile", detect)):
            scored = [(s, fn(vs)) for s, vs in pool_raw.items()]
            scored = [(s, x) for s, x in scored if x is not None]
            scored.sort(key=lambda kv: kv[1])
            bins = {}
            edges = []
            m = len(scored)
            for rank, (s, x) in enumerate(scored):
                d = min(9, rank * 10 // m)
                bins.setdefault(d, []).append(s)
            for d in range(10):
                vals = [fn(pool_raw[s]) for s in bins.get(d, [])]
                edges.append([round(min(vals), 4), round(max(vals), 4)] if vals else None)

            def decile_of(x):
                # rank x against the pool's sorted property values
                lo, hi = 0, m
                while lo < hi:
                    mid = (lo + hi) // 2
                    if scored[mid][1] < x:
                        lo = mid + 1
                    else:
                        hi = mid
                return min(9, lo * 10 // m)

            for setname in ("A_plus_B_all_dna_binding", "D_filion_table1_emc_vs_137_sarcomas"):
                v = primary["set_scores"][setname][P.key]
                members = [g for g in v["genes_readable"] if g in gene_raw]
                want = {}
                for g in members:
                    x = fn(gene_raw[g])
                    if x is None:
                        continue
                    want[decile_of(x)] = want.get(decile_of(x), 0) + 1
                rng = random.Random(SEED + 7)
                deltas = []
                feasible = all(len(bins.get(d, [])) >= k for d, k in want.items())
                if feasible:
                    for _ in range(N_DRAWS):
                        draw = []
                        for d, k in want.items():
                            draw.extend(rng.sample(bins[d], k))
                        c = P.contrast(P.sample_scores(draw, source=P.z_pool))
                        if c:
                            deltas.append(c["delta"])
                    deltas.sort()
                    lo_, hi_ = P.band(deltas)
                    obs = v["null_calibration"]["observed_delta"]
                    thr = hi_ if obs >= 0 else lo_
                    rec = {
                        "n": len(members),
                        "decile_composition": {str(k): want[k] for k in sorted(want)},
                        "matched_band": [round(lo_, 5), round(hi_, 5)],
                        "uniform_band": [v["null_calibration"]["null_q025"],
                                         v["null_calibration"]["null_q975"]],
                        "observed_delta": obs,
                        "fraction_of_matched_threshold": round(abs(obs / thr), 3) if thr else None,
                        "fraction_of_uniform_threshold": round(
                            abs(obs / (v["null_calibration"]["null_q975"] if obs >= 0
                                       else v["null_calibration"]["null_q025"])), 3),
                        "p_empirical_two_sided": emp_p(deltas, obs),
                    }
                else:
                    rec = {"n": len(members), "state": "NOT_DRAWABLE — a decile holds fewer pool "
                                                       "symbols than the set needs"}
                out["per_platform"].setdefault(label, {}).setdefault(prop, {})[setname] = rec
            out["per_platform"][label].setdefault("_decile_edges", {})[prop] = edges
    return out


def block_t_null(plats, primary):
    out = {
        "_question": "The manuscript quotes a Welch t for a set and a null computed on delta. What "
                     "does an arbitrary set of the same size print on the t scale?",
        "per_platform": {},
    }
    for label, P in plats.items():
        rows = {}
        for setname in ("A_plus_B_all_dna_binding",):
            v = primary["set_scores"][setname][P.key]
            n = v["n_genes_readable"]
            obs = P.contrast(P.sample_scores(v["genes_readable"]))
            rng = random.Random(SEED)
            ts = []
            for _ in range(N_DRAWS):
                draw = rng.sample(P.pool_symbols, n)
                c = P.contrast(P.sample_scores(draw, source=P.z_pool))
                if c:
                    ts.append(c["t"])
            ts.sort()
            abs_ts = sorted(abs(x) for x in ts)
            rows[setname] = {
                "n": n,
                "observed_t": round(obs["t"], 4),
                "observed_delta": round(obs["delta"], 5),
                "null_t_band_95": [round(quantile(ts, 0.025), 4), round(quantile(ts, 0.975), 4)],
                "null_abs_t_q95": round(quantile(abs_ts, 0.95), 4),
                "fraction_of_random_sets_with_larger_abs_t": round(
                    sum(1 for x in abs_ts if x >= abs(obs["t"])) / len(abs_ts), 4),
                "reading": "an arbitrary set of this size on this platform routinely prints a t of "
                           "this magnitude, so t alone grades nothing here.",
            }
        out["per_platform"][label] = rows
    return out


def block_detectability(plats, primary):
    out = {
        "_question": "Replace 'a bounded negative, not an underpowered one' with an interval.",
        "_method": "the set-level delta with a confidence interval obtained by inverting the exact "
                   "label-permutation test (the interval of shifts applied to the EMC arm that the "
                   "two-sided permutation test does not reject at 0.05), and the smallest true shift "
                   "this design would place outside the size-matched band with 80% probability, "
                   "computed as threshold + 0.8416 * SE of the observed contrast.",
        "_this_is_not_a_power_calculation": "no alternative hypothesis is assumed for the confidence "
                                            "interval; the 80% figure is a detectability statement "
                                            "about a shift of the set score, not about a biological "
                                            "effect size.",
        "per_platform": {},
    }
    for label, P in plats.items():
        rows = {}
        for setname in ("A_plus_B_all_dna_binding", "B_native_nr4a3_dna_binding_targets",
                        "D_filion_table1_emc_vs_137_sarcomas"):
            v = primary["set_scores"][setname][P.key]
            nc = v["null_calibration"]
            scores = P.sample_scores(v["genes_readable"])
            emc = [i for i in P.emc if scores[i] is not None]
            cmp_ = [i for i in P.cmp if scores[i] is not None]
            a = [scores[i] for i in emc]
            b = [scores[i] for i in cmp_]
            w = welch(a, b)

            n_assign_pre = math.comb(len(a) + len(b), len(a))

            def perm_p(shift, n_assign=n_assign_pre):
                """Two-sided permutation p for H0: EMC arm shifted down by `shift`.

                Complete enumeration where the assignment count allows it; otherwise a seeded
                sample of assignments, labelled as sampled rather than quietly presented as exact.
                """
                import itertools
                aa = [x - shift for x in a]
                pooled = aa + b
                na = len(aa)
                obs = abs(statistics.fmean(aa) - statistics.fmean(b))
                total = ge = 0
                if n_assign <= 60000:
                    it = itertools.combinations(range(len(pooled)), na)
                else:
                    rng2 = random.Random(SEED + 31)
                    idx = list(range(len(pooled)))
                    it = (tuple(rng2.sample(idx, na)) for _ in range(20000))
                for combo in it:
                    sset = set(combo)
                    g1 = statistics.fmean([pooled[i] for i in combo])
                    g2 = statistics.fmean([pooled[i] for i in range(len(pooled)) if i not in sset])
                    total += 1
                    if abs(g1 - g2) >= obs - 1e-12:
                        ge += 1
                return ge / total, total

            n_assign = math.comb(len(a) + len(b), len(a))
            ci = None
            exact = n_assign <= 60000
            if True:
                lo, hi = w["delta"] - 6 * w["se"], w["delta"] + 6 * w["se"]
                def not_rejected(s):
                    return perm_p(s)[0] > 0.05
                # bisect each edge of the acceptance interval around the point estimate
                def edge(direction):
                    a0, b0 = w["delta"], (hi if direction > 0 else lo)
                    for _ in range(40):
                        m = (a0 + b0) / 2
                        if not_rejected(m):
                            a0 = m
                        else:
                            b0 = m
                    return round((a0 + b0) / 2, 5)
                ci = [edge(-1), edge(+1)]
            thr = nc["null_q975"] if nc["observed_delta"] >= 0 else nc["null_q025"]
            rows[setname] = {
                "n_readable": v["n_genes_readable"],
                "observed_delta": round(w["delta"], 5),
                "se_of_contrast": round(w["se"], 5),
                "permutation_ci_95": ci,
                "n_distinct_assignments": n_assign,
                "ci_method": ("exact, all assignments enumerated" if exact else
                              "sampled — 20,000 seeded assignments per shift, because the complete "
                              "enumeration at this arm split is too large to invert"),
                "size_matched_threshold": thr,
                "smallest_shift_outside_band_with_80pc_probability": round(
                    abs(thr) + 0.8416 * w["se"], 4),
                "reading": ("effects on this set score larger than the last figure would fall "
                            "outside the size-matched band four times in five; smaller ones are not "
                            "excluded by this design."),
            }
        out["per_platform"][label] = rows
    return out


#: ⚠ CLASS B IS NOT ONE EVIDENCE TYPE, and 16 of the 19 genes in the headline aggregate come from it.
#: The split is by a rule that can be checked against the committed catalogue rather than by taste:
#: a row is B2 when its `citation` field begins "Reviewed in" — that is, no primary assay paper was
#: retrieved and the classification rests on a review's assertion. VTN is the one row the string rule
#: does not settle and it is placed in B2 for a stated reason: its cited primary (Haller et al.) is a
#: target LIST, not the migration assay the row describes, and the row's own assay text is
#: "listed by an independent review as a functionally validated direct target".
CLASS_B1 = ["CDKN2AIP", "COX5A", "GLS2", "PDP1", "SDHA", "SMPX"]
CLASS_B2 = ["BIRC3", "CCND1", "ICAM1", "LOXL2", "MYH7", "NOX1", "SKP2", "TH", "VCAM1", "VTN"]


def block_evidence_split(plats, primary):
    rows = {r["gene"]: r for r in primary["evidence_table"]["rows"]}
    classB = sorted(g for g, r in rows.items() if r["evidence_class"] == "native_dna_binding")
    if sorted(CLASS_B1 + CLASS_B2) != classB:
        sys.exit("REFUSING TO WRITE: the B1/B2 split does not partition class B in the catalogue")
    by_rule = sorted(g for g in classB if str(rows[g]["citation"]).startswith("Reviewed in"))
    classA = primary["set_definitions"]["A_fusion_dna_binding_targets"]["genes"]
    out = {
        "_question": "Class B mixes rows whose primary assay was retrieved with rows resting on a "
                     "review's assertion, and it supplies 16 of the 19 genes in the headline "
                     "aggregate.",
        "_rule": "B2 = the catalogue row's citation begins 'Reviewed in' (no primary assay paper "
                 "retrieved). VTN is assigned to B2 by hand, for the reason recorded in the source.",
        "B1_primary_assay_retrieved": CLASS_B1,
        "B2_review_assertion_only": CLASS_B2,
        "B2_by_the_string_rule_alone": by_rule,
        "genes_the_string_rule_and_the_assignment_disagree_on": sorted(set(by_rule) ^ set(CLASS_B2)),
        "per_platform": {},
    }
    for label, P in plats.items():
        rows_out = {}
        for setname, members in (("A_plus_B1", classA + CLASS_B1),
                                 ("A_plus_B_all_dna_binding", classA + CLASS_B1 + CLASS_B2),
                                 ("B1_only", CLASS_B1), ("B2_only", CLASS_B2)):
            readable = [g for g in members if g in P.z_gene
                        and any(v is not None for v in P.z_gene[g])]
            if len(readable) < 4:
                rows_out[setname] = {"n_readable": len(readable),
                                     "state": "no score — below the four-gene floor"}
                continue
            c = P.contrast(P.sample_scores(readable))
            nd = P.null_deltas(len(readable))
            lo, hi = P.band(nd)
            thr = hi if c["delta"] >= 0 else lo

            def arm_centred(zs):
                out_ = list(zs)
                for arm in (P.emc, P.cmp):
                    vals = [zs[i] for i in arm if zs[i] is not None]
                    if not vals:
                        continue
                    m = statistics.fmean(vals)
                    for i in arm:
                        if out_[i] is not None:
                            out_[i] = out_[i] - m
                return out_

            resid = {g: arm_centred(P.z_gene[g]) for g in readable}
            cors = []
            for i in range(len(readable)):
                for j in range(i + 1, len(readable)):
                    rr = pearson(resid[readable[i]], resid[readable[j]])
                    if rr is not None:
                        cors.append(rr)
            rho = statistics.fmean(cors) if cors else 0.0
            vif = 1 + (len(readable) - 1) * rho
            thr_infl = thr * math.sqrt(vif) if vif > 1 else thr
            rows_out[setname] = {
                "n_requested": len(members), "n_readable": len(readable),
                "genes_not_readable": [g for g in members if g not in readable],
                "observed_delta": round(c["delta"], 5),
                "band": [round(lo, 5), round(hi, 5)],
                "fraction_of_threshold": round(abs(c["delta"] / thr), 3),
                "p_empirical_two_sided": emp_p(nd, c["delta"]),
                "clears": abs(c["delta"]) > abs(thr),
                "rho_bar": round(rho, 4),
                "variance_inflation_factor": round(vif, 3),
                "threshold_inflated": round(thr_infl, 5),
                "fraction_of_inflated_threshold": round(abs(c["delta"] / thr_infl), 3),
                "clears_inflated": abs(c["delta"]) > abs(thr_infl),
            }
        out["per_platform"][label] = rows_out
    return out


def block_muscle(plats, primary):
    markers = ["ACTA1", "MYH7", "MYL1", "PYGM"]
    out = {
        "_question": "The muscle-admixture control reports four percentile differences with no null. "
                     "Put them through the same size-1 null the class-A genes face.",
        "_note": "MYH7 is also a class-B member of this paper's own target catalogue, so its "
                 "flatness cannot be read purely as evidence about admixture.",
        "per_platform": {},
    }
    for label, P in plats.items():
        rows = {}
        for g in markers + ["ENO3"]:
            if g not in P.z_gene:
                rows[g] = {"state": "not readable on this platform"}
                continue
            z = P.z_gene[g]
            obs_idx = {i for i, v in enumerate(z) if v is not None}
            emc = [i for i in P.emc if i in obs_idx]
            cmp_ = [i for i in P.cmp if i in obs_idx]
            if len(emc) < MIN_PER_ARM or len(cmp_) < MIN_PER_ARM:
                rows[g] = {"state": "NOT_MEASURABLE"}
                continue
            w = welch([z[i] for i in emc], [z[i] for i in cmp_])
            rng = random.Random(SEED)
            deltas = []
            for _ in range(N_DRAWS):
                s = rng.choice(P.pool_symbols)
                zz = P.z_pool[s]
                aa = [zz[i] for i in emc if zz[i] is not None]
                bb = [zz[i] for i in cmp_ if zz[i] is not None]
                if len(aa) >= MIN_PER_ARM and len(bb) >= MIN_PER_ARM:
                    deltas.append(statistics.fmean(aa) - statistics.fmean(bb))
            deltas.sort()
            lo, hi = P.band(deltas)
            rows[g] = {
                "n_EMC": len(emc), "n_comparator": len(cmp_),
                "delta_mean_z": round(w["delta"], 4),
                "size_1_band": [round(lo, 5), round(hi, 5)],
                "p_empirical_two_sided": emp_p(deltas, w["delta"]),
                "outside_band": w["delta"] < lo or w["delta"] > hi,
            }
        out["per_platform"][label] = rows
    return out


# ---------------------------------------------------------------- main
def main():
    global IN_RAW, SECONDARY
    IN_RAW = json.load(open(INPUTS))
    SECONDARY = json.load(open(SECONDARY_PATH))
    primary = json.load(open(PRIMARY))
    plats = {lab: Platform(lab, IN_RAW, primary) for lab in PLATFORMS}

    # ⛔ Refuse to write unless this module reproduces the primary artifact's own set deltas from the
    # cached inputs. A sensitivity analysis computed by a second reduction is worth nothing if the
    # second reduction is not the first one.
    parity = {"_what": "every scored set's delta re-derived here and compared with the committed "
                       "value", "rows": [], "worst_abs_difference": 0.0}
    for lab, P in plats.items():
        for setname, byplat in primary["set_scores"].items():
            v = byplat.get(P.key, {})
            nc = v.get("null_calibration")
            if not nc:
                continue
            c = P.contrast(P.sample_scores(v["genes_readable"]))
            diff = abs(round(c["delta"], 4) - nc["observed_delta"])
            parity["rows"].append({"platform": lab, "set": setname,
                                   "recomputed": round(c["delta"], 5),
                                   "committed": nc["observed_delta"], "abs_difference": round(diff, 6)})
            parity["worst_abs_difference"] = max(parity["worst_abs_difference"], diff)
    parity["agrees"] = parity["worst_abs_difference"] <= 5e-4
    if not parity["agrees"]:
        worst = max(parity["rows"], key=lambda r: r["abs_difference"])
        sys.exit(f"REFUSING TO WRITE: re-derived set delta disagrees with the committed artifact: {worst}")

    art = {
        "_what": "sensitivity analyses added in revision. Reads the committed inputs and primary "
                 "artifact; writes no new measurement of any tumour.",
        "_offline": "CPU-only, pure stdlib, no network. Seeded and deterministic.",
        "_language_discipline": "Nothing here asserts efficacy, selectivity, safety, a therapeutic "
                                "window or clinical readiness for any agent, target or gene, and no "
                                "such quantity is computed.",
        "_inputs": {"primary_artifact": "nr4a3-fusion-targets.json",
                    "expression": "nr4a3-fusion-targets-inputs.json"},
        "parity_with_primary_artifact": parity,
        "closed_form": block_closed_form(plats, primary),
        "inter_gene_correlation": block_correlation(plats, primary),
        "set_D_without_genes_shared_with_set_E": block_set_d(plats, primary),
        "per_gene_missingness_nulls": block_missingness(plats, primary),
        "seed_sensitivity": block_seeds(plats, primary),
        "composition_matched_nulls": block_matched(plats, primary),
        "t_scale_null": block_t_null(plats, primary),
        "detectability": block_detectability(plats, primary),
        "muscle_marker_nulls": block_muscle(plats, primary),
        "class_B_evidence_split": block_evidence_split(plats, primary),
    }
    with open(OUT, "w") as fh:
        json.dump(art, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"wrote {OUT}")
    print("parity worst abs difference:", parity["worst_abs_difference"])


if __name__ == "__main__":
    main()
