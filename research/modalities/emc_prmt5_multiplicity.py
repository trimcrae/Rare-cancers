#!/usr/bin/env python3
"""Multiplicity correction and three disclosure analyses for the EMC PRMT5/MTAP manuscript.

WHY THIS MODULE EXISTS. `emc-expression-panels.json` reports a per-gene Welch t and an exact
permutation p for the labelling of ONE gene, and a genome-wide placement that is explicitly not a
correction. A reviewer of `emc-mtap-prmt5-hypothesis.md` asked the obvious next question — what is
the p once the number of genes examined is accounted for — and it is answerable at no cost from the
fetch cache that is already committed. Nothing here re-fetches, and nothing here can perturb the
artifacts the manuscript's other numbers come from: this module READS
`emc-expression-panels-inputs.json` and `emc-expression-panels.json` and writes one new file.

WHAT IT COMPUTES, and each is a separate question:

  1  max-statistic (Westfall-Young style) permutation FWER correction. Arm labels are permuted
     exactly as the single-gene exact test permutes them; Welch's t is recomputed for EVERY gene in
     the family at every labelling; the maximum |t| across the family is recorded per labelling; a
     gene's adjusted p is the fraction of labellings whose maximum reaches its observed |t|. On
     GPL3290 every one of the C(16,10) = 8,008 labellings is enumerated, so that correction is
     EXACT and carries no sampling error. On GPL6244 C(35,6) = 1,623,160 is too many to enumerate
     against this family, so a fixed-seed sample is drawn and the number of labellings is recorded.

     ⛔ THE FAMILY IS EVERY SYMBOL TWO COMMITTED CACHES HOLD, WHICH IS ABOUT A THIRD OF THE ARRAY.
     The full probe matrix exists only inside the fetch step, so no committed file carries every
     symbol's values. Two do carry a large part: the panel cache holds the ~1,900 genes the reads
     asked for, and `emc-hypoxia-null-background.json` holds, in addition, a SEEDED UNIFORM RANDOM
     SAMPLE of about 4,000 symbols drawn from the platform's whole mapped-symbol universe. The two
     were fetched separately and agree value-for-value on every symbol they share, on identical
     samples and identical per-sample backgrounds, so they merge into one family without mixing two
     reductions. That family is ~5,400 symbols on GPL6244 and ~5,200 on GPL3290.

     Because part of the family is a uniform random sample of the array, the full-array answer can
     be BRACKETED rather than merely bounded below:
       * the adjusted p over the merged family is a LOWER bound, since adding symbols can only
         raise the permuted maximum;
       * an UPPER bound follows from Markov's inequality. Let K be the number of symbols on the
         whole array whose permuted |t| reaches the observed value. P(max over the array reaches
         it) = P(K >= 1) <= E[K], and E[K] is estimated without any independence assumption from
         the random sample's own exceedance count divided by the sampling fraction.
     Both are reported for every gene, together with the growth of the adjusted p with family size
     measured on random symbols alone.

  2  the two-colour reference-channel split on GPL3290. All ten EMC tumours were hybridised against
     a reference the GEO annotation names `CRH-mRNA`, the three DFSP comparators against `CRH` and
     the three GIST comparators against `UHR`. In a two-colour design every value is a ratio to the
     reference channel, so half the comparator arm differs from every EMC tumour in the denominator
     of the measurement. This recomputes the contrast against each half separately.

  3  the samples the classifier dropped. GSE24369 deposits 42 samples; the panel scores 35. This
     re-reads every verbatim annotation, names what fell out, and recomputes the primary contrasts
     with the five solitary fibrous tumours added to the comparator arm.

  4  per-gene missingness, per platform, since the panel path and the genome-wide path apply
     different minimum-arm-size floors and the difference decides whether a gene is scored at all.

⛔ WHAT THIS IS NOT. It is not a re-fetch, not a new measurement and not a claim about any agent. A
corrected p is a statement about how often a labelling of these samples produces a statistic this
large, and about nothing else.

DOUBLE ENTRY. Every observed t used here is re-derived from the cache by this module and compared
against the committed value in `emc-expression-panels.json`. If any gene disagrees the module
refuses to write, because a correction computed on a statistic that is not the published one would
be worse than no correction at all.

USAGE
    python3 emc_prmt5_multiplicity.py            # compute and write emc-prmt5-multiplicity.json
    python3 emc_prmt5_multiplicity.py --check    # recompute and diff against the committed file
"""

import argparse
import json
import math
import os
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from emc_atr_vulnerability import _classify_sample  # noqa: E402  the one home of the bucket rules

INPUTS = os.path.join(HERE, "emc-expression-panels-inputs.json")
PANEL = os.path.join(HERE, "emc-expression-panels.json")
#: the second committed fetch of the same two matrices. Its `_random_background_symbols` are a
#: seeded uniform random sample of the platform's mapped-symbol universe, which is what lets the
#: correction speak about the whole array rather than only about the genes the panel asked for.
NULLBG = os.path.join(HERE, "emc-hypoxia-null-background.json")
OUT = os.path.join(HERE, "emc-prmt5-multiplicity.json")

P6244 = "GSE24369_series_matrix.txt.gz"
P3290 = "GSE4303-GPL3290_series_matrix.txt.gz"

#: genes the manuscript reports a statistic for, plus its two instrument controls and the
#: cellularity reference. Every one of them gets an adjusted p; nothing is selected after the fact.
REPORTED = ("PRMT5", "MAT2A", "WDR77", "MTAP", "CDKN2A", "CDKN2B", "NR4A3", "ENO3", "MKI67")
METHYLOSOME = ("PRMT5", "WDR77", "RIOK1", "CLNS1A")

#: the panel's own floor. A gene is scored only with at least this many values in each arm; the
#: genome-wide path uses 2, which is why one control is readable there and not here (main text 3.5).
PANEL_ARM_FLOOR = 3

B_SAMPLED = 20000          # labellings drawn on GPL6244, where exhaustive enumeration is too many
SEED = 20260810
FAMILY_STEPS = (50, 100, 250, 500, 1000)


# ---------------------------------------------------------------------------------------------
# small statistics, matching `fet_ddr_axis_scan._welch`, which is what the panel uses
# ---------------------------------------------------------------------------------------------
def _welch_t(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((y - mb) ** 2 for y in b) / (nb - 1)
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return None
    return (ma - mb) / se, ma - mb


def _z_rows(target):
    """Per-gene z against that sample's whole-array background — the panel's own reduction."""
    n_s = target["n_samples"]
    bg = target["background_per_sample"]
    out = {}
    for g, rec in target["genes"].items():
        v = rec["values"]
        out[g] = [None if (v[i] is None or not bg[i]) else
                  (v[i] - bg[i]["mean"]) / max(1e-9, bg[i]["sd"]) for i in range(n_s)]
    return out


def _classes(target):
    return [_classify_sample(s["annotation_verbatim"]) for s in target["samples"]]


def _arms(classes):
    emc = [i for i, c in enumerate(classes) if c == "EMC"]
    comp = [i for i, c in enumerate(classes)
            if c not in ("EMC", "unclassified", "normal_or_reference")]
    return emc, comp


def _contrast(z, emc, comp, floor=PANEL_ARM_FLOOR):
    a = [z[i] for i in emc if z[i] is not None]
    b = [z[i] for i in comp if z[i] is not None]
    if len(a) < floor or len(b) < floor:
        return None
    w = _welch_t(a, b)
    if not w:
        return None
    return {"t": round(w[0], 3), "delta_a_minus_b": round(w[1], 4),
            "n_EMC": len(a), "n_comparator": len(b)}


# ---------------------------------------------------------------------------------------------
# 1 — the max-statistic permutation correction
# ---------------------------------------------------------------------------------------------
def _t_matrix(np, Z, M, Q, n_all, s_all, q_all, block, A):
    """|Welch t| for a block of genes at every labelling in A, with the panel's arm floor."""
    nA = M[block] @ A
    sA = Z[block] @ A
    qA = Q[block] @ A
    nB = n_all[block][:, None] - nA
    sB = s_all[block][:, None] - sA
    qB = q_all[block][:, None] - qA
    with np.errstate(divide="ignore", invalid="ignore"):
        mA, mB = sA / nA, sB / nB
        vA = (qA - sA * sA / nA) / (nA - 1.0)
        vB = (qB - sB * sB / nB) / (nB - 1.0)
        t = (mA - mB) / np.sqrt(vA / nA + vB / nB)
    bad = (nA < PANEL_ARM_FLOOR) | (nB < PANEL_ARM_FLOOR) | ~np.isfinite(t)
    return np.where(bad, 0.0, np.abs(t))


def _max_statistic(zrows, random_symbols, n_universe, emc, comp, exhaustive, tag):
    """Adjusted p for every reported gene, from the distribution of the family-wide maximum |t|,
    with a Markov upper bound for the whole array estimated off the random symbols.

    Returns None if numpy is unavailable; the caller then declines to write rather than emitting a
    correction computed some other way."""
    try:
        import numpy as np
    except ImportError:  # pragma: no cover - the dev sandbox may lack it
        return None

    idx = sorted(set(emc) | set(comp))
    n = len(idx)
    n_emc = len(emc)
    emc_set = set(emc)

    fam = []
    for g in sorted(zrows):
        row = [zrows[g][i] for i in idx]
        a = [row[k] for k, i in enumerate(idx) if i in emc_set and row[k] is not None]
        b = [row[k] for k, i in enumerate(idx) if i not in emc_set and row[k] is not None]
        if len(a) >= PANEL_ARM_FLOOR and len(b) >= PANEL_ARM_FLOOR and _welch_t(a, b):
            fam.append(g)
    m = len(fam)
    raw = [[zrows[g][i] for i in idx] for g in fam]
    M = np.array([[0.0 if v is None else 1.0 for v in r] for r in raw], dtype=np.float64)
    Z = np.array([[0.0 if v is None else float(v) for v in r] for r in raw], dtype=np.float64)
    Q = Z * Z
    n_all, s_all, q_all = M.sum(axis=1), Z.sum(axis=1), Q.sum(axis=1)

    if exhaustive:
        cols = list(combinations(range(n), n_emc))
        B = len(cols)
        A = np.zeros((n, B), dtype=np.float64)
        for j, c in enumerate(cols):
            A[list(c), j] = 1.0
        rng_note = {"kind": "exhaustive", "n_labelings": B,
                    "_means": "every assignment of the observed values to arms of the observed "
                              "sizes was evaluated, so this correction carries NO sampling error "
                              "from the labellings."}
    else:
        rng = np.random.default_rng(SEED)
        B = B_SAMPLED
        A = np.zeros((n, B), dtype=np.float64)
        for j in range(B):
            A[rng.choice(n, size=n_emc, replace=False), j] = 1.0
        rng_note = {"kind": "sampled", "n_labelings": B, "seed": SEED,
                    "total_labelings_possible": math.comb(n, n_emc),
                    "_means": "a fixed-seed sample of the labellings, because enumerating all of "
                              "them against a family this size is not affordable. The adjusted p "
                              "carries a Monte-Carlo standard error, reported beside it."}

    # thresholds: the observed |t| of every reported gene the panel can score here
    observed = {}
    for g in REPORTED:
        if g in zrows:
            c = _contrast(zrows[g], emc, comp)
            if c:
                observed[g] = c
    thr = np.array([abs(observed[g]["t"]) for g in sorted(observed)], dtype=np.float64)
    thr_genes = sorted(observed)

    rand_pos = [k for k, g in enumerate(fam) if g in random_symbols]
    order_rand = list(rand_pos)
    np.random.default_rng(SEED + 1).shuffle(order_rand)
    order_all = list(range(m))
    np.random.default_rng(SEED + 2).shuffle(order_all)

    CH = 250

    def run(order, want_counts):
        """running family-wide max over `order`, plus (optionally) per-threshold exceedance counts
        and snapshots of the max at the family sizes in FAMILY_STEPS."""
        running = np.zeros(B, dtype=np.float64)
        counts = np.zeros((len(thr), B), dtype=np.float64) if want_counts else None
        snaps, steps, si = {}, [s for s in FAMILY_STEPS if s < len(order)] + [len(order)], 0
        for start in range(0, len(order), CH):
            block = order[start:start + CH]
            t = _t_matrix(np, Z, M, Q, n_all, s_all, q_all, block, A)
            running = np.maximum(running, t.max(axis=0))
            if want_counts:
                for r, c in enumerate(thr):
                    counts[r] += (t >= c - 1e-12).sum(axis=0)
            done = start + len(block)
            while si < len(steps) and done >= steps[si]:
                snaps[steps[si]] = running.copy()
                si += 1
        return running, counts, snaps

    full, _, _ = run(order_all, False)
    rand_max, rand_counts, rand_snaps = run(order_rand, True)

    frac_sampled = len(random_symbols) / n_universe

    def adjusted(t_obs, dist):
        hit = int((dist >= abs(t_obs) - 1e-12).sum())
        if exhaustive:
            return hit / B, hit, None
        p = (hit + 1) / (B + 1)
        return p, hit, math.sqrt(max(p * (1 - p), 1e-12) / B)

    per_gene = {}
    for g in REPORTED:
        if g not in zrows:
            continue
        if g not in observed:
            per_gene[g] = {"_status": "NOT SCORED on this platform under the panel's floor of "
                                      f"{PANEL_ARM_FLOOR} per arm, so there is no panel statistic "
                                      "to adjust. The genome-wide placement uses a floor of 2 and "
                                      "does emit a value; the two are different instruments."}
            continue
        c = observed[g]
        p, hit, se = adjusted(c["t"], full)
        row = thr_genes.index(g)
        e_k = float(rand_counts[row].mean()) / frac_sampled
        rec = {"t": c["t"], "n_EMC": c["n_EMC"], "n_comparator": c["n_comparator"],
               "fwer_adjusted_p_over_the_merged_family": round(p, 4),
               "n_labelings_whose_maximum_reached_it": hit,
               "whole_array_lower_bound": round(p, 4),
               "whole_array_upper_bound_markov_estimate": round(min(1.0, e_k), 4),
               "expected_symbols_on_the_whole_array_reaching_it_per_labeling": round(e_k, 3)}
        if se is not None:
            rec["monte_carlo_se"] = round(se, 4)
        if e_k < p:
            rec["⚠_the_upper_estimate_fell_below_the_measured_lower_bound"] = (
                "which is impossible for the true quantities and means the estimate is not usable "
                "at this threshold. E[K] is estimated from one draw of the random symbols, and at "
                "an observed |t| this far into the tail that draw sees only a handful of "
                "exceedance events, so the estimate is dominated by its own sampling error. Read "
                "the lower bound, which is measured rather than estimated.")
        per_gene[g] = rec

    sens = {}
    if "PRMT5" in observed:
        for size in sorted(rand_snaps):
            p, _, _ = adjusted(observed["PRMT5"]["t"], rand_snaps[size])
            sens[str(size)] = round(p, 4)

    qs = [0.5, 0.9, 0.95, 0.99, 1.0]
    srt = sorted(full.tolist())
    return {
        "_what": "the distribution of the LARGEST |t| in the family, over labellings of the arms. "
                 "A gene's adjusted p is the fraction of labellings whose maximum reaches its "
                 "observed |t| — the standard max-statistic (Westfall-Young style) control of the "
                 "family-wise error rate. The labels are permuted exactly as the single-gene exact "
                 "test permutes them.",
        "family_size_genes": m,
        "_family_composition": (
            f"{m} symbols scoreable under the panel's floor, merged from the panel cache and the "
            f"seeded random background. {len(random_symbols)} of the array's {n_universe} mapped "
            "symbols are a uniform random sample, which is what makes the whole-array bracket "
            "below estimable rather than assumed."),
        "n_random_symbols_in_family": len(rand_pos),
        "n_symbols_on_the_platform": n_universe,
        "sampling_fraction_of_the_array": round(frac_sampled, 4),
        "labelings": rng_note,
        "n_EMC": len(emc), "n_comparator": len(comp),
        "max_abs_t_null": {f"p{int(q * 100)}":
                           round(srt[min(len(srt) - 1, int(round(q * (len(srt) - 1))))], 3)
                           for q in qs},
        "adjusted_p": per_gene,
        "_how_to_read_the_bracket": (
            "LOWER = the adjusted p measured over the merged family, which is a subset of the "
            "array, and adding symbols can only raise it. UPPER = Markov's inequality on the "
            "number K of array symbols whose permuted |t| reaches the observed value: "
            "P(max reaches it) = P(K >= 1) <= E[K], and E[K] is the random sample's mean "
            "exceedance count divided by the sampling fraction. The upper bound needs no "
            "independence assumption; it inherits the sampling error of one random draw of "
            "symbols, and it is loose when the exceedances cluster within labellings."),
        "family_size_sensitivity": {
            "_what": "PRMT5's adjusted p recomputed over nested random subsets of the RANDOM "
                     "symbols alone, smallest first, so the curve is about array symbols rather "
                     "than about the genes these reads asked for.",
            "prmt5_adjusted_p_by_family_size": sens,
        },
        "_tag": tag,
    }


# ---------------------------------------------------------------------------------------------
# 2 — the two-colour reference channel on GPL3290
# ---------------------------------------------------------------------------------------------
def _reference_channel(target, zrows, classes):
    ann = [s["annotation_verbatim"] for s in target["samples"]]

    def channel(a):
        parts = [p.strip() for p in a.split("|")]
        return parts[1] if len(parts) > 1 else None

    ch = [channel(a) for a in ann]
    emc, comp = _arms(classes)
    groups = {}
    for i in comp:
        groups.setdefault(ch[i], []).append(i)
    emc_ch = sorted({ch[i] for i in emc})
    out = {
        "_what": "every value on a two-colour array is a ratio to the reference channel, so a "
                 "comparator hybridised against a different reference differs from an EMC tumour "
                 "in the denominator of the measurement as well as in the biology.",
        "reference_channel_verbatim_per_class": {},
        "emc_reference_channels": emc_ch,
        "⚠_whether_CRH_and_CRH_mRNA_are_the_same_pool_is_not_stated_in_the_record": (
            "The GEO annotation writes the EMC reference as `CRH-mRNA` and the DFSP reference as "
            "`CRH`. Nothing in the deposit says whether those name one pool or two, so the "
            "DFSP contrast is described here as reference-MATCHED-BY-LABEL rather than as "
            "identical, and the GIST contrast as reference-DIFFERENT, which the deposit does say."),
        "split_contrasts": {},
    }
    for i, c in enumerate(classes):
        out["reference_channel_verbatim_per_class"].setdefault(c, {}).setdefault(ch[i], 0)
        out["reference_channel_verbatim_per_class"][c][ch[i]] += 1
    for label, idxs in sorted(groups.items()):
        cls = sorted({classes[i] for i in idxs})
        rec = {"n_comparator": len(idxs), "comparator_classes": cls}
        for g in REPORTED + ("RIOK1", "CLNS1A"):
            if g not in zrows:
                continue
            c = _contrast(zrows[g], emc, idxs)
            rec[g] = c if c else {"_status": "arm below the floor"}
        out["split_contrasts"][label] = rec
    pooled = {}
    for g in REPORTED + ("RIOK1", "CLNS1A"):
        if g in zrows:
            pooled[g] = _contrast(zrows[g], emc, comp)
    out["pooled_for_comparison"] = pooled
    return out


# ---------------------------------------------------------------------------------------------
# 3 — the samples the classifier dropped, and what including them does
# ---------------------------------------------------------------------------------------------
SFT_PATTERN = "solitary fibrous tumor"


def _dropped_samples(target, zrows, classes):
    ann = [s["annotation_verbatim"] for s in target["samples"]]
    gsm = [s["gsm"] for s in target["samples"]]
    emc, comp = _arms(classes)
    excluded = [i for i in range(len(classes)) if i not in emc and i not in comp]
    sft = [i for i in excluded if SFT_PATTERN in ann[i].lower()]
    other = [i for i in excluded if i not in sft]
    out = {
        "_what": "GSE24369 deposits more samples than the panel scores. This is every one of them, "
                 "with the verbatim annotation that decided it.",
        "n_deposited": len(classes),
        "n_analysed": len(emc) + len(comp),
        "class_counts_as_bucketed": {c: classes.count(c) for c in sorted(set(classes))},
        "⚠_one_bucket_name_is_a_substring_artefact": (
            "The six samples bucketed `fibrosarcoma` are annotated `Myxofibrosarcoma` in GEO; the "
            "bucket matches on the substring `fibrosarcoma`. Myxofibrosarcoma is a different "
            "entity, and the manuscript names the samples rather than the bucket."),
        "excluded_samples": [{"gsm": gsm[i], "annotation_verbatim": ann[i],
                              "reason": ("no comparator bucket carries a pattern for this "
                                         "histology, so it fell through to `unclassified`; the "
                                         "exclusion was accidental rather than designed"
                                         if i in sft else
                                         "pooled normal tissue rather than a tumour, so it does "
                                         "not belong in a comparator arm of tumours")}
                             for i in excluded],
        "n_excluded_solitary_fibrous_tumour": len(sft),
        "n_excluded_pooled_normal_tissue": len(other),
        "inclusion_sensitivity": {
            "_what": "the primary contrasts recomputed with the solitary fibrous tumours added to "
                     "the comparator arm. The two pooled skeletal-muscle samples stay out: they "
                     "are normal tissue, not a comparator tumour.",
            "n_comparator_with_them": len(comp) + len(sft),
        },
    }
    widened = sorted(comp + sft)
    for g in REPORTED + ("RIOK1", "CLNS1A"):
        if g not in zrows:
            continue
        base = _contrast(zrows[g], emc, comp)
        wide = _contrast(zrows[g], emc, widened)
        out["inclusion_sensitivity"][g] = {
            "t_as_published": None if base is None else base["t"],
            "t_with_solitary_fibrous_tumours_included": None if wide is None else wide["t"],
        }
    return out


def _excluded_per_sample_z(target, zrows, classes, genes):
    """Per-sample z for the samples the panel's arms leave out, so a figure can draw them.

    ⛔ THE FIGURE CANNOT GET THESE FROM THE PANEL ARTIFACT. `emc-expression-panels.json` carries a
    `per_sample` block only for the samples in an arm, which is precisely why the excluded class was
    invisible in figure 4. They are written here, beside the exclusion record that explains them."""
    ann = [s["annotation_verbatim"] for s in target["samples"]]
    gsm = [s["gsm"] for s in target["samples"]]
    out = {}
    for i, c in enumerate(classes):
        if c not in ("unclassified", "normal_or_reference"):
            continue
        cls = ("solitary_fibrous_tumour" if SFT_PATTERN in ann[i].lower()
               else "pooled_skeletal_muscle_RNA")
        rec = {"gsm": gsm[i], "class": cls, "z_vs_array": {}}
        for g in genes:
            if g in zrows and zrows[g][i] is not None:
                rec["z_vs_array"][g] = round(zrows[g][i], 4)
        out[gsm[i]] = rec
    return {"_what": "z against that array's own probe distribution, for every deposited sample the "
                     "panel's arms exclude. Same reduction as every other z in this work.",
            "samples": out}


def _per_class_medians(target, zrows, classes, genes, label):
    ann = [s["annotation_verbatim"] for s in target["samples"]]
    named = []
    for i, c in enumerate(classes):
        if c == "unclassified":
            c = ("solitary_fibrous_tumour" if SFT_PATTERN in ann[i].lower()
                 else "pooled_skeletal_muscle_RNA")
        if c == "fibrosarcoma":
            c = "myxofibrosarcoma"
        named.append(c)
    rows = {}
    for g in genes:
        if g not in zrows:
            continue
        for i, v in enumerate(zrows[g]):
            if v is not None:
                rows.setdefault(named[i], []).append(v)
    out = {}
    for k, vals in rows.items():
        vs = sorted(vals)
        n = len(vs)
        med = vs[n // 2] if n % 2 else (vs[n // 2 - 1] + vs[n // 2]) / 2
        out[k] = {"median_z": round(med, 4), "n_values": n,
                  "n_samples": named.count(k)}
    return {"_what": label, "genes": list(genes), "per_class": out}


def _missingness(zrows, emc, comp):
    tot = at_least_one = below_floor = 0
    for g, z in zrows.items():
        tot += 1
        idx = sorted(set(emc) | set(comp))
        if any(z[i] is None for i in idx):
            at_least_one += 1
        a = sum(1 for i in emc if z[i] is not None)
        b = sum(1 for i in comp if z[i] is not None)
        if a < PANEL_ARM_FLOOR or b < PANEL_ARM_FLOOR:
            below_floor += 1
    return {"n_genes_cached": tot,
            "n_with_at_least_one_missing_value": at_least_one,
            "frac_with_at_least_one_missing_value": round(at_least_one / tot, 4) if tot else None,
            "n_with_an_arm_below_the_panel_floor": below_floor,
            "frac_with_an_arm_below_the_panel_floor": round(below_floor / tot, 4) if tot else None,
            "_panel_floor": PANEL_ARM_FLOOR,
            "_the_genome_wide_path_uses_2": "so a gene can be unscored by the panel and scored by "
                                            "the genome-wide placement, which is why one control "
                                            "carries a rank and no panel contrast."}


# ---------------------------------------------------------------------------------------------
def _self_check(zrows, emc, comp, panel, key):
    """Every cached gene the panel scored must re-derive to the committed t. No exceptions."""
    checked = mismatched = 0
    worst = None
    for g, z in zrows.items():
        rec = (panel["gene_reads"].get(g) or {}).get(key)
        if not isinstance(rec, dict):
            continue
        w = rec.get("welch_EMC_vs_comparator")
        if not w or w.get("t") is None:
            continue
        c = _contrast(z, emc, comp)
        if c is None:
            mismatched += 1
            worst = worst or (g, None, w["t"])
            continue
        checked += 1
        if abs(c["t"] - w["t"]) > 0.002:
            mismatched += 1
            if worst is None or abs(c["t"] - w["t"]) > abs(worst[1] - worst[2]):
                worst = (g, c["t"], w["t"])
    return {"n_genes_compared": checked, "n_disagreeing": mismatched,
            "worst_disagreement": worst,
            "_what": "the t this module re-derives from the fetch cache against the t committed in "
                     "emc-expression-panels.json, for every gene the panel scored on this "
                     "platform. A correction computed on a statistic that is not the published one "
                     "would be worse than no correction, so a disagreement refuses the write."}


def _merge_caches(panel_target, null_target):
    """One z-row set from two independently fetched caches of the same matrices.

    ⛔ THE MERGE IS REFUSED unless the two caches agree on the samples, on their order, on the
    per-sample background and on every value of every symbol they share. They were fetched days
    apart; if either the probe-to-symbol bridge or the parse had moved between them, combining
    their symbols into one family would silently mix two reductions."""
    if [s["gsm"] for s in panel_target["samples"]] != [s["gsm"] for s in null_target["samples"]]:
        raise SystemExit("REFUSING TO MERGE — the two caches do not carry the same samples")
    if panel_target["background_per_sample"] != null_target["background_per_sample"]:
        raise SystemExit("REFUSING TO MERGE — the two caches disagree on the per-sample background")
    shared = set(panel_target["genes"]) & set(null_target["genes"])
    for g in shared:
        if panel_target["genes"][g]["values"] != null_target["genes"][g]["values"]:
            raise SystemExit(f"REFUSING TO MERGE — the two caches disagree on {g}")
    merged = dict(null_target["genes"])
    merged.update(panel_target["genes"])
    return merged, len(shared)


def compute():
    inp = json.load(open(INPUTS, encoding="utf-8"))
    panel = json.load(open(PANEL, encoding="utf-8"))
    nullbg = json.load(open(NULLBG, encoding="utf-8"))
    res = {
        "_title": "Multiplicity correction and three disclosure analyses for the EMC PRMT5 reading",
        "_generated_by": "research/modalities/emc_prmt5_multiplicity.py",
        "_source": "research/modalities/emc-expression-panels-inputs.json (the committed fetch "
                   "cache) checked against research/modalities/emc-expression-panels.json (the "
                   "committed reads). No network, no re-fetch, no new measurement.",
        "_no_clinical_claim": "Nothing here asserts efficacy, safety, selectivity, a therapeutic "
                              "window or clinical readiness for any agent in any disease.",
        "⛔_an_adjusted_p_is_not_a_result": "It reports how often a labelling of THESE samples "
                                           "produces a statistic this large somewhere in the "
                                           "family. It does not make a hypothesis true, and a "
                                           "value that fails to clear a threshold does not make "
                                           "the underlying reading disappear.",
        "per_platform": {},
    }
    for key, exhaustive in ((P6244, False), (P3290, True)):
        t = inp["targets"][key]
        nt = nullbg["targets"][key]
        classes = _classes(t)
        emc, comp = _arms(classes)
        zrows_panel = _z_rows(t)
        merged_genes, n_shared = _merge_caches(t, nt)
        zrows = _z_rows({"n_samples": t["n_samples"],
                         "background_per_sample": t["background_per_sample"],
                         "genes": merged_genes})
        random_symbols = set(nt["_random_background_symbols"])
        n_universe = nt["_n_symbols_on_platform"]
        chk = _self_check(zrows_panel, emc, comp, panel, key)
        if chk["n_disagreeing"]:
            raise SystemExit(f"REFUSING TO WRITE — {key}: {chk['n_disagreeing']} genes re-derive "
                             f"to a t the committed artifact does not carry ({chk['worst_disagreement']})")
        rec = {
            "platform": t["platform"],
            "gse": t["gse"],
            "n_EMC": len(emc),
            "n_comparator": len(comp),
            "self_check_against_the_committed_reads": chk,
            "cache_merge": {
                "_what": "the panel cache and the seeded random background, checked against each "
                         "other before they were combined",
                "n_symbols_panel_cache": len(t["genes"]),
                "n_symbols_random_background_cache": len(nt["genes"]),
                "n_symbols_shared_and_value_identical": n_shared,
                "n_symbols_merged": len(merged_genes),
            },
            "per_gene_missingness": _missingness(zrows_panel, emc, comp),
        }
        ms = _max_statistic(zrows, random_symbols, n_universe, emc, comp, exhaustive, key)
        if ms is None:
            raise SystemExit("numpy is required for the permutation correction and is absent")
        rec["max_statistic_permutation"] = ms
        if key == P3290:
            rec["reference_channel"] = _reference_channel(t, zrows_panel, classes)
        if key == P6244:
            rec["deposited_samples_and_exclusions"] = _dropped_samples(t, zrows_panel, classes)
            rec["per_class_medians_PRMT5"] = _per_class_medians(
                t, zrows_panel, classes, ("PRMT5",),
                "median z of PRMT5 per class, INCLUDING the classes the panel's arms exclude")
            rec["excluded_sample_z"] = _excluded_per_sample_z(
                t, zrows_panel, classes, METHYLOSOME)
            rec["per_class_medians_methylosome_pooled"] = _per_class_medians(
                t, zrows_panel, classes, METHYLOSOME,
                "median of the four methylosome genes' z pooled, per class, INCLUDING the classes "
                "the panel's arms exclude. Pooled values are not independent observations and no "
                "test is run on them.")
        res["per_platform"][key] = rec
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
        old = json.load(open(OUT, encoding="utf-8"))
        drift = [k for k in res if old.get(k) != res[k]]
        print("REPRODUCES" if not drift else f"DRIFT in: {drift}")
        return 0 if not drift else 1
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    for key, rec in res["per_platform"].items():
        ms = rec["max_statistic_permutation"]
        print(f"{rec['gse']}/{rec['platform']}: family {ms['family_size_genes']} genes, "
              f"{ms['labelings']['n_labelings']} labelings ({ms['labelings']['kind']})")
        for g, v in ms["adjusted_p"].items():
            if "fwer_adjusted_p_over_the_merged_family" in v:
                print(f"    {g:7s} t={v['t']:>8} adjusted p="
                      f"{v['fwer_adjusted_p_over_the_merged_family']:<7} "
                      f"whole-array bracket [{v['whole_array_lower_bound']}, "
                      f"{v['whole_array_upper_bound_markov_estimate']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
