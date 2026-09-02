#!/usr/bin/env python3
"""Per-sample 9p21 locus reading for the EMC MTAP/PRMT5 manuscript. ($0, stdlib only)

WHY THIS MODULE EXISTS. `emc-expression-panels.json` reports the MTAP locus as a difference of
group means (Welch's t) and `emc-prmt5-multiplicity.json` corrects that difference for the number
of genes examined. Homozygous 9p21 deletion is not a location shift: it is present in some tumours
and absent in others, so a group mean and a family-wise adjusted p are both mis-specified for the
alternative the manuscript's second rationale actually proposes. A reviewer of
`emc-mtap-prmt5-hypothesis.md` observed that the committed per-sample values hold a candidate
subset on one platform that no group statistic can see, and that the check which discriminates a
deletion from a non-deletion had never been run. It costs nothing: every value it needs is already
in the fetch caches.

WHAT IT COMPUTES.

  1  The per-sample reading of every readable locus gene on both platforms, as the array percentile
     and the within-array z the panel already stores.

  2  CANDIDATE IDENTIFICATION. An EMC tumour is a candidate if its MTAP reading sits below every
     comparator tumour on the same platform. This is the per-sample form of the pre-specified read,
     whose recorded direction is "MTAP DOWN in EMC, at the floor, together with CDKN2A".

  3  THE DISCRIMINATING CHECK, which is the reason the module exists. MTAP and CDKN2A are ~100 kb
     apart on 9p21, and a homozygous deletion that removes MTAP removes CDKN2A with it; the
     converse does not hold, which is why the manuscript cites that asymmetry. So a candidate that
     carries a 9p21 homozygous deletion must ALSO read low for CDKN2A. This counts, per platform,
     how many EMC tumours satisfy the conjunction, over a ladder of CDKN2A thresholds so the answer
     does not depend on one cut. Where the random-background cache carries another 9p21 gene the
     same reading is reported for it.

  4  TWO CONTROLS ON THE CANDIDATE SET, both of which have to fail for the candidates to mean
     anything. (a) A globally dim array produces low percentiles for every gene, so the fraction of
     each sample's cached genes below the 5th percentile of its own array is reported. (b) On a
     two-colour platform a different reference pool shifts every ratio, so the reference label of
     every sample in the arm is reported; a split WITHIN one arm cannot come from the denominator
     if the arm shares one label.

  5  The rank association between MTAP and CDKN2A within the EMC arm, with an exact permutation p
     over all n! rank permutations. Under co-deletion the association is positive; the observed
     sign is the reading of interest and the p is reported so the reading is not over-read.

  6  Binomial one-sided 95% upper bounds on the frequency of a deletion-consistent tumour given the
     observed count, which is what bounds a negative at these sample sizes.

WHAT THIS IS NOT. It is not a copy-number measurement. A transcript is not a copy number, an
archival two-colour log-ratio is not an absolute level, and no threshold used here is a validated
call. It cannot establish that any tumour carries or does not carry a 9p21 deletion. What it can do
is ask whether the per-sample pattern in these caches is the pattern a co-deletion produces, and
report that it is not.

DOUBLE ENTRY. Every per-sample value is read from `emc-expression-panels.json`; the group means
this module re-derives from those per-sample values are compared against the committed Welch
record, and the module refuses to emit if any of them disagrees.

Usage:
  python3 research/modalities/emc_mtap_locus_persample.py           # write the artifact
  python3 research/modalities/emc_mtap_locus_persample.py --check   # recompute and diff
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = os.path.join(HERE, "emc-expression-panels.json")
INPUTS = os.path.join(HERE, "emc-expression-panels-inputs.json")
BACKGROUND = os.path.join(HERE, "emc-hypoxia-null-background.json")
OUT = os.path.join(HERE, "emc-mtap-locus-persample.json")

P6244 = "GSE24369_series_matrix.txt.gz"
P3290 = "GSE4303-GPL3290_series_matrix.txt.gz"
PLATFORM_LABEL = {P6244: "GPL6244", P3290: "GPL3290"}

LOCUS = ("MTAP", "CDKN2A", "CDKN2B")

#: Other genes of the 9p21 neighbourhood that happen to be in the committed random-background
#: cache. They are not a designed panel and no claim rests on them; they are reported because a
#: homozygous deletion large enough to remove MTAP and CDKN2A frequently removes neighbours too,
#: so their reading in a candidate is a second, independent way for the deletion story to fail.
NEIGHBOURHOOD = ("MIR31HG", "MLLT3")

#: The ladder of CDKN2A cuts. "below every comparator" is the same criterion applied to MTAP; the
#: percentile cuts are absolute positions within a sample's own array. The ladder exists so the
#: answer does not depend on one threshold.
CDKN2A_CUTS = ("below_every_comparator", 0.05, 0.10, 0.25, 0.50)

#: The headline conjunction uses an absolute floor criterion rather than "below every comparator",
#: because the comparator arms here read HIGH for CDKN2A: on GPL3290 the lowest comparator sits at
#: the 57th percentile of its own array, so "below every comparator" is not a floor criterion for
#: this gene on this platform and would count a tumour at its array's median. A homozygously
#: deleted gene reads at the floor.
HEADLINE_CDKN2A_CUT = 0.25


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _welch(a, b):
    na, nb = len(a), len(b)
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
    se2 = va / na + vb / nb
    if se2 <= 0:
        return None
    t = (ma - mb) / math.sqrt(se2)
    df = se2 ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    return {"t": round(t, 4), "df": round(df, 1),
            "mean_EMC": round(ma, 4), "mean_comparator": round(mb, 4),
            "delta_EMC_minus_comparator": round(ma - mb, 4)}


def _rows(panels, gene, key):
    rec = panels["gene_reads"].get(gene, {}).get(key)
    if not rec or not rec.get("readable"):
        return None
    return rec


def _spearman_exact(x, y):
    """Spearman rho with an exact two-sided permutation p over all n! rank permutations."""
    n = len(x)
    if n < 3 or n > 10:
        return None

    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(x), ranks(y)
    mx = sum(rx) / n
    my = sum(ry) / n
    cx = [v - mx for v in rx]
    cy = [v - my for v in ry]
    sx = math.sqrt(sum(v * v for v in cx))
    sy = math.sqrt(sum(v * v for v in cy))
    if sx == 0 or sy == 0:
        return None
    rho = sum(a * b for a, b in zip(cx, cy)) / (sx * sy)
    hit = 0
    total = 0
    target = abs(rho) - 1e-12
    for perm in itertools.permutations(range(n)):
        r = sum(cx[i] * cy[perm[i]] for i in range(n)) / (sx * sy)
        total += 1
        if abs(r) >= target:
            hit += 1
    return {"rho": round(rho, 4), "n": n, "n_permutations": total,
            "at_least_as_extreme": hit, "exact_two_sided_p": round(hit / total, 5),
            "_reading": "under 9p21 co-deletion in a subset the association is POSITIVE "
                        "(both genes low in the same tumours); a negative rho is the opposite "
                        "of the co-deletion pattern."}


def _dimness(panels, key):
    """Fraction of each sample's readable cached genes that sit below the 5th percentile of its
    own array. A globally dim array makes every gene look low, so a candidate whose dimness is
    unremarkable is not explained by array quality."""
    low, total, cls = {}, {}, {}
    for _gene, per in panels["gene_reads"].items():
        rec = per.get(key)
        if not rec or not rec.get("readable"):
            continue
        for r in rec["per_sample"]:
            ap = r.get("array_percentile")
            if ap is None:
                continue
            gsm = r["gsm"]
            cls[gsm] = r["class"]
            total[gsm] = total.get(gsm, 0) + 1
            if ap < 0.05:
                low[gsm] = low.get(gsm, 0) + 1
    out = {}
    for gsm in sorted(total, key=lambda g: (cls[g] != "EMC", g)):
        out[gsm] = {"class": cls[gsm], "n_genes_read": total[gsm],
                    "n_below_5th_percentile": low.get(gsm, 0),
                    "frac_below_5th_percentile": round(low.get(gsm, 0) / total[gsm], 4)}
    return out


def _dimness_wide(inputs, panels, key):
    """The same control on the wider fetch cache, which holds ~1,700 genes rather than the panel's
    few hundred. Reported beside the panel figure because a control computed on a narrow gene set
    is itself a narrow control."""
    t = inputs["targets"][key]
    samples = [s["gsm"] for s in t["samples"]]
    cls = {r["gsm"]: r["class"] for r in panels["gene_reads"]["MTAP"][key]["per_sample"]}
    low = {s: 0 for s in samples}
    total = {s: 0 for s in samples}
    for _gene, rec in t["genes"].items():
        for i, ap in enumerate(rec["array_percentile"]):
            if ap is None:
                continue
            total[samples[i]] += 1
            if ap < 0.05:
                low[samples[i]] += 1
    return {"n_genes_in_cache": len(t["genes"]),
            "per_sample": {s: {"class": cls.get(s, "?"), "n_genes_read": total[s],
                               "frac_below_5th_percentile": round(low[s] / total[s], 4)}
                           for s in sorted(samples, key=lambda g: (cls.get(g) != "EMC", g))}}


def _reference_labels(inputs, panels, key):
    t = inputs["targets"][key]
    cls = {r["gsm"]: r["class"] for r in panels["gene_reads"]["MTAP"][key]["per_sample"]}
    per_class = {}
    for s in t["samples"]:
        parts = [p.strip() for p in s.get("annotation_verbatim", "").split("|")]
        label = parts[1] if len(parts) > 1 else ""
        c = cls.get(s["gsm"], "?")
        per_class.setdefault(c, {})
        per_class[c][label] = per_class[c].get(label, 0) + 1
    return per_class


def _neighbourhood(background, panels, key, candidates):
    t = background["targets"].get(key)
    if not t:
        return {}
    order = [r["gsm"] for r in panels["gene_reads"]["MTAP"][key]["per_sample"]]
    # The background cache stores values in the fetch's sample order, which is the inputs order.
    inputs = _load(INPUTS)
    samples = [s["gsm"] for s in inputs["targets"][key]["samples"]]
    cls = {r["gsm"]: r["class"] for r in panels["gene_reads"]["MTAP"][key]["per_sample"]}
    out = {}
    for gene in NEIGHBOURHOOD:
        rec = t["genes"].get(gene)
        if not rec:
            continue
        ap = rec["array_percentile"]
        in_cand = {}
        comparator = []
        for i, gsm in enumerate(samples):
            if ap[i] is None:
                continue
            if gsm in candidates:
                in_cand[gsm] = round(ap[i], 4)
            elif cls.get(gsm) != "EMC":
                comparator.append(round(ap[i], 4))
        out[gene] = {
            "n_probes_mapping": rec.get("n_probes_mapping"),
            "array_percentile_in_the_MTAP_low_candidates": in_cand,
            "comparator_array_percentile_range": [min(comparator), max(comparator)] if comparator else None,
        }
    assert order  # the two orders are only used for class lookup, which is keyed by GSM
    return out


def _binomial_upper_bound(k, n, conf=0.95):
    """One-sided upper bound on p given k successes in n trials, by inverting the binomial tail."""
    if k != 0:
        # General case by bisection on the exact tail; only k = 0 is used by the caller.
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            tail = sum(math.comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(0, k + 1))
            if tail > 1 - conf:
                lo = mid
            else:
                hi = mid
        return round((lo + hi) / 2, 4)
    return round(1 - (1 - conf) ** (1.0 / n), 4)


def compute():
    panels = _load(PANELS)
    inputs = _load(INPUTS)
    background = _load(BACKGROUND)

    res = {
        "_what": "per-sample reading of the 9p21 locus in the two EMC expression series, and the "
                 "MTAP/CDKN2A conjunction that discriminates a homozygous co-deletion from a "
                 "low MTAP transcript with an intact locus.",
        "_why": "a group mean and a family-wise adjusted p are both mis-specified for a subset "
                "event. This asks the per-sample question the manuscript's second rationale "
                "actually poses.",
        "_this_is_not_a_copy_number_measurement": (
            "no threshold here is a validated call, a transcript is not a copy number, and an "
            "archival two-colour log-ratio carries no absolute level. The reading is whether the "
            "pattern is the one a co-deletion produces."),
        "_source_artifacts": [os.path.basename(PANELS), os.path.basename(INPUTS),
                              os.path.basename(BACKGROUND)],
        "_generated_from": panels.get("generated_utc"),
        "per_platform": {},
    }

    for key in (P6244, P3290):
        plat = PLATFORM_LABEL[key]
        mtap = _rows(panels, "MTAP", key)
        cdkn2a = _rows(panels, "CDKN2A", key)
        if not mtap or not cdkn2a:
            continue

        per_gene = {}
        for gene in LOCUS:
            rec = _rows(panels, gene, key)
            if not rec:
                per_gene[gene] = {"readable": False}
                continue
            rows = [{"gsm": r["gsm"], "class": r["class"], "value": r["value"],
                     "z_vs_array": r["z_vs_array"], "array_percentile": r["array_percentile"]}
                    for r in rec["per_sample"]]
            emc = [r for r in rows if r["class"] == "EMC"]
            comp = [r for r in rows if r["class"] != "EMC"]
            check = _welch([r["z_vs_array"] for r in emc], [r["z_vs_array"] for r in comp])
            committed = rec["welch_EMC_vs_comparator"]
            if check is None or abs(check["t"] - committed["t"]) > 0.01:
                raise SystemExit(
                    f"double-entry failure: {gene} on {plat} re-derives t={check} against the "
                    f"committed {committed['t']}")
            per_gene[gene] = {
                "readable": True,
                "n_probes_mapping": rec.get("n_probes_mapping"),
                "probe_ids": rec.get("probe_ids"),
                "EMC_mean_array_percentile": rec["EMC"]["mean_array_percentile"],
                "comparator_mean_array_percentile": rec["comparator"]["mean_array_percentile"],
                "welch_re_derived_here": check,
                "welch_committed": {"t": committed["t"],
                                    "delta_a_minus_b": committed["delta_a_minus_b"]},
                "lowest_comparator_array_percentile": min(r["array_percentile"] for r in comp),
                "lowest_comparator_z": min(r["z_vs_array"] for r in comp),
                "n_EMC_below_every_comparator": sum(
                    1 for r in emc if r["z_vs_array"] < min(x["z_vs_array"] for x in comp)),
                "per_sample": sorted(rows, key=lambda r: (r["class"] != "EMC",
                                                          r["array_percentile"])),
            }

        # 2 — candidates on MTAP
        mrows = per_gene["MTAP"]["per_sample"]
        memc = [r for r in mrows if r["class"] == "EMC"]
        mcomp = [r for r in mrows if r["class"] != "EMC"]
        z_floor = min(r["z_vs_array"] for r in mcomp)
        pct_floor = min(r["array_percentile"] for r in mcomp)
        by_z = {r["gsm"] for r in memc if r["z_vs_array"] < z_floor}
        by_pct = {r["gsm"] for r in memc if r["array_percentile"] < pct_floor}
        candidates = sorted(by_z & by_pct, key=lambda g: next(
            r["array_percentile"] for r in memc if r["gsm"] == g))

        crows = {r["gsm"]: r for r in per_gene["CDKN2A"]["per_sample"]}
        c_comp_floor = min(r["array_percentile"] for r in per_gene["CDKN2A"]["per_sample"]
                           if r["class"] != "EMC")

        cand_detail = []
        for gsm in candidates:
            m = next(r for r in memc if r["gsm"] == gsm)
            c = crows[gsm]
            cand_detail.append({
                "gsm": gsm,
                "MTAP_array_percentile": m["array_percentile"],
                "MTAP_z": m["z_vs_array"],
                "CDKN2A_array_percentile": c["array_percentile"],
                "CDKN2A_z": c["z_vs_array"],
                "CDKN2A_below_every_comparator": c["array_percentile"] < c_comp_floor,
            })

        # 3 — the conjunction, over a ladder of cuts
        conjunction = {}
        for cut in CDKN2A_CUTS:
            if cut == "below_every_comparator":
                n = sum(1 for d in cand_detail if d["CDKN2A_below_every_comparator"])
                label = f"CDKN2A below every comparator (< {round(c_comp_floor, 4)})"
            else:
                n = sum(1 for d in cand_detail if d["CDKN2A_array_percentile"] < cut)
                label = f"CDKN2A below the {int(cut * 100)}th percentile of its own array"
            conjunction[str(cut)] = {"criterion": label,
                                     "n_candidates_also_meeting_it": n,
                                     "of_n_MTAP_low_candidates": len(cand_detail)}

        # 5 — rank association within the EMC arm
        common = [r["gsm"] for r in memc if r["gsm"] in crows]
        rho = _spearman_exact([next(r["z_vs_array"] for r in memc if r["gsm"] == g) for g in common],
                              [crows[g]["z_vs_array"] for g in common])

        rec = {
            "gse": key.split("_")[0].split("-")[0],
            "platform": plat,
            "n_EMC": len(memc),
            "n_comparator": len(mcomp),
            "locus_genes": per_gene,
            "mtap_low_candidates": {
                "_criterion": "an EMC tumour whose MTAP reading is below every comparator tumour "
                              "on the same platform, on BOTH the within-array z and the array "
                              "percentile.",
                "lowest_comparator_MTAP_z": round(z_floor, 4),
                "lowest_comparator_MTAP_array_percentile": round(pct_floor, 4),
                "n_candidates": len(cand_detail),
                "candidates": cand_detail,
                "_agreement_of_the_two_criteria": {
                    "n_by_z": len(by_z), "n_by_percentile": len(by_pct),
                    "n_by_both": len(by_z & by_pct)},
            },
            "the_discriminating_conjunction": {
                "_what": "MTAP and CDKN2A are ~100 kb apart on 9p21 and a homozygous deletion "
                         "removing MTAP removes CDKN2A with it. A candidate carrying such a "
                         "deletion must therefore read low for CDKN2A as well.",
                "headline_criterion": (
                    f"MTAP below every comparator AND CDKN2A below the "
                    f"{int(HEADLINE_CDKN2A_CUT * 100)}th percentile of its own array"),
                "n_deletion_consistent_tumours": sum(
                    1 for d in cand_detail
                    if d["CDKN2A_array_percentile"] < HEADLINE_CDKN2A_CUT),
                "by_cdkn2a_cut": conjunction,
                "_why_below_every_comparator_is_not_the_headline": (
                    "the comparator arms read high for CDKN2A, so on GPL3290 that criterion "
                    "resolves to the 57th percentile and would count a tumour sitting at the "
                    "median of its own array. It is reported in the ladder and is not a floor."),
                "CDKN2A_array_percentile_range_in_the_candidates": (
                    [min(d["CDKN2A_array_percentile"] for d in cand_detail),
                     max(d["CDKN2A_array_percentile"] for d in cand_detail)]
                    if cand_detail else None),
            },
            "within_EMC_rank_association_MTAP_vs_CDKN2A": rho,
            "controls_on_the_candidate_set": {
                "array_dimness_panel_cache": _dimness(panels, key),
                "array_dimness_wide_cache": _dimness_wide(inputs, panels, key),
                "reference_label_per_class": _reference_labels(inputs, panels, key),
            },
            "nine_p21_neighbourhood_in_the_random_background_cache": _neighbourhood(
                background, panels, key, set(candidates)),
        }
        res["per_platform"][key] = rec

    # 6 — binomial bounds on a deletion-consistent tumour, given what was found
    n_by_platform = {PLATFORM_LABEL[k]: v["n_EMC"] for k, v in res["per_platform"].items()}
    found = sum(v["the_discriminating_conjunction"]["n_deletion_consistent_tumours"]
                for v in res["per_platform"].values())
    res["binomial_bounds"] = {
        "_what": "one-sided 95% upper bound on the frequency of a deletion-consistent tumour, "
                 "given the count observed at these sample sizes. This is what bounds the "
                 "negative; it is not a demonstration of absence.",
        "n_deletion_consistent_tumours_found": found,
        "per_platform_n_EMC": n_by_platform,
        "upper_bound_95pc_given_0_of_6": _binomial_upper_bound(0, 6),
        "upper_bound_95pc_given_0_of_10": _binomial_upper_bound(0, 10),
        "upper_bound_95pc_given_0_of_16": _binomial_upper_bound(0, 16),
        "_comparison": "reference [11] of the manuscript records MTAP protein loss reaching up to "
                       "20% in various sarcomas, and does not name this histology.",
    }
    res["_what_this_establishes"] = (
        "On GPL3290 five of ten EMC tumours read below every comparator for MTAP, which a group "
        "mean cannot see. None of them reads low for CDKN2A: all five sit at or above the median "
        "of their own array, and the lowest-MTAP tumour carries the arm's highest CDKN2A. The "
        "pattern is therefore not the one 9p21 homozygous co-deletion produces. On GPL6244 no EMC "
        "tumour is an MTAP low outlier at all.")
    res["_what_this_does_not_establish"] = (
        "that no EMC tumour carries a 9p21 deletion. Sixteen tumours bound the frequency loosely, "
        "MTAP rests on one probe on GPL6244 and two averaged probes on GPL3290 with no per-probe "
        "record committed, and a transcript reading cannot exclude protein loss by a "
        "non-deletional mechanism. Only MTAP immunohistochemistry addresses the state the "
        "MTAP-selected agents are selected on.")
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
        c = rec["mtap_low_candidates"]
        d = rec["the_discriminating_conjunction"]
        print(f"{rec['platform']}: {rec['n_EMC']} EMC, {rec['n_comparator']} comparator; "
              f"{c['n_candidates']} MTAP-low candidate(s)")
        for cand in c["candidates"]:
            print(f"    {cand['gsm']}  MTAP {cand['MTAP_array_percentile'] * 100:5.2f}th pct   "
                  f"CDKN2A {cand['CDKN2A_array_percentile'] * 100:5.2f}th pct")
        print(f"    deletion-consistent (MTAP low AND CDKN2A below the 25th percentile): "
              f"{d['n_deletion_consistent_tumours']}")
        r = rec["within_EMC_rank_association_MTAP_vs_CDKN2A"]
        if r:
            print(f"    within-EMC Spearman rho = {r['rho']:+.4f}, exact p = {r['exact_two_sided_p']}")
    b = res["binomial_bounds"]
    print(f"binomial 95% upper bounds given zero found: 0/6 -> {b['upper_bound_95pc_given_0_of_6']}, "
          f"0/10 -> {b['upper_bound_95pc_given_0_of_10']}, "
          f"0/16 -> {b['upper_bound_95pc_given_0_of_16']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
