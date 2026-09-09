#!/usr/bin/env python3
"""
SYNLETH-2 — Is the pan-essential-trap screen decidable without the rest-arm denominator?

Read-only input: research/modalities/depmap-sarcoma-dependency.json (DepMap public 24Q4).
No network, no producer re-run, no new data.

Question (synthetic-lethality side, deliberately NOT the per-quantity bound table
BIOMARKER-DEP-3 is producing from the biomarker side):

  PUB-SYNLETH installed a reading rule for this panel -- never read `selectivity` without
  `rest_frac_dependent`, because EWSR1 (+0.373, rest_frac 0.915) is a pan-essential trap.
  DEP-THRESHOLD applied that rule and flagged 22 of 64 gene records.
  BIOMARKER-DEP-2 then found the rest-arm denominator is recorded nowhere.
  Does that indeterminacy actually put the TRAP-SCREEN VERDICTS in doubt?

Sections:
  A  re-derivation of every prior number this lane leans on, from the artifact
  B  admissible rest-arm denominator set, derived here under an explicit stated rule
  C  the envelope argument: Wilson/Clopper-Pearson width is monotone in n, so the union
     over admissible n is the interval at n_min -- an interval CAN be placed, conservatively
  D  decision stability of the trap screen at n_min (worst case), both cut-offs, both methods
  E  the descriptive/inferential split
"""
import json, math, os, sys
from scipy.stats import beta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
ART = os.path.join(ROOT, "research/modalities/depmap-sarcoma-dependency.json")

Z = 1.959963984540054  # two-sided 95%
TRAP_CUT = 0.80        # DEP-THRESHOLD's primary pan-essential-trap cut
SEC_CUT = 0.20         # DEP-THRESHOLD's secondary cut
ROUND_DP = 3
HALF = 0.5 * 10 ** (-ROUND_DP)   # +/- 5e-4 rounding half-width

def wilson(p, n, z=Z):
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)

def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return (float(lo), float(hi))

def records(d):
    out = []
    def walk(o, p=""):
        if isinstance(o, dict):
            if "rest_frac_dependent" in o and "n_sarcoma" in o:
                out.append((p, o))
            else:
                for k, v in o.items():
                    walk(v, p + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, p + "[" + str(i) + "]")
    walk(d)
    return out

def main():
    d = json.load(open(ART))
    recs = records(d)
    res = {"input": ART, "data_source": d["data_source"],
           "n_models_total": d["n_models_total"],
           "n_sarcoma_models": d["n_sarcoma_models"],
           "dependent_threshold": d["dependent_threshold"]}

    # ---------- A. re-derivation of prior numbers ----------
    genes = [r[1]["gene"] for r in recs]
    uniq = sorted(set(genes))
    n_sarc = sorted({r[1]["n_sarcoma"] for r in recs})
    fields = sorted({f for _, r in recs for f in r.keys()})
    ews = [r for p, r in recs if r["gene"] == "EWSR1"]
    sarc_integral = all(abs(r["sarcoma_frac_dependent"] * 91 - round(r["sarcoma_frac_dependent"] * 91)) < 0.05
                        for _, r in recs)
    A = {
        "n_records": len(recs), "n_unique_genes": len(uniq),
        "n_sarcoma_values_seen": n_sarc,
        "record_field_names": fields,
        "dispersion_field_present": any(f for f in fields if any(
            t in f for t in ("sd", "median", "min", "max", "q25", "q75", "n_rest", "n_dependent"))),
        "EWSR1_selectivity": sorted({r["selectivity"] for r in ews}),
        "EWSR1_rest_frac_dependent": sorted({r["rest_frac_dependent"] for r in ews}),
        "EWSR1_sarcoma_frac_dependent": sorted({r["sarcoma_frac_dependent"] for r in ews}),
        "sarcoma_frac_x_91_integral_all_records": sarc_integral,
        "duplicated_gene_records": sorted({g for g in genes if genes.count(g) > 1}),
    }
    trap80 = sorted({r["gene"] for _, r in recs if r["rest_frac_dependent"] >= TRAP_CUT})
    trap20 = sorted({r["gene"] for _, r in recs if r["rest_frac_dependent"] >= SEC_CUT})
    A["trap_set_ge_0.80_unique_genes"] = trap80
    A["n_trap_ge_0.80_unique"] = len(trap80)
    A["n_trap_ge_0.80_records"] = sum(1 for _, r in recs if r["rest_frac_dependent"] >= TRAP_CUT)
    A["n_trap_ge_0.20_unique"] = len(trap20)
    A["n_trap_ge_0.20_records"] = sum(1 for _, r in recs if r["rest_frac_dependent"] >= SEC_CUT)
    res["A_rederivation"] = A

    # ---------- B. admissible rest-arm denominators ----------
    # Rule (stated, not inherited): n is admissible iff for EVERY record there is an integer
    # k in [0,n] with round(k/n, 3) == the reported rest_frac_dependent. Upper limit taken as
    # n_models_total = 2105 (the artifact records no CRISPR-arm size); no lower limit imposed.
    fr = sorted({r["rest_frac_dependent"] for _, r in recs})
    def ok(n):
        for f in fr:
            k = round(f * n)
            if k < 0 or k > n:
                return False
            if round(k / n, ROUND_DP) != f:
                # try neighbours, rounding is not always nearest-k
                good = False
                for kk in (k - 1, k + 1):
                    if 0 <= kk <= n and round(kk / n, ROUND_DP) == f:
                        good = True
                        break
                if not good:
                    return False
        return True
    adm = [n for n in range(1, d["n_models_total"] + 1) if ok(n)]
    B = {"rule": "for every record, exists integer k in [0,n] with round(k/n,3)==reported rest_frac_dependent; n<=n_models_total",
         "n_distinct_reported_rest_fracs": len(fr),
         "n_admissible": len(adm),
         "n_min": min(adm) if adm else None,
         "n_max": max(adm) if adm else None,
         "n_excluded_within_range": (max(adm) - min(adm) + 1 - len(adm)) if adm else None,
         "BIOMARKER_DEP_2_reported": {"count": 1126, "span_low": 943, "span_high": 2105},
         }
    B["reproduces_BIOMARKER_DEP_2"] = (len(adm) == 1126 and min(adm) == 943 and max(adm) == 2105)
    res["B_admissible_denominators"] = B
    if not adm:
        json.dump(res, open(os.path.join(os.path.dirname(__file__), "denominator-envelope.json"), "w"), indent=2)
        print("NO ADMISSIBLE DENOMINATOR", file=sys.stderr)
        return 2
    nmin, nmax = min(adm), max(adm)

    # ---------- C. the envelope ----------
    # Wilson half-width is strictly decreasing in n at fixed p, so the union of 95% intervals
    # over the admissible set is the interval at n_min. Demonstrated numerically over the set.
    demo = {}
    for p in (0.915, 0.696, 0.854, 0.80):
        ws = [(n, wilson(p, n)) for n in adm]
        widths = [hi - lo for _, (lo, hi) in ws]
        demo[str(p)] = {
            "width_at_n_min": widths[0], "width_at_n_max": widths[-1],
            "width_monotone_decreasing_over_admissible_set": all(
                widths[i] >= widths[i + 1] - 1e-15 for i in range(len(widths) - 1)),
            "union_over_admissible_equals_interval_at_n_min": (
                abs(min(lo for _, (lo, _) in ws) - wilson(p, nmin)[0]) < 1e-12 and
                abs(max(hi for _, (_, hi) in ws) - wilson(p, nmin)[1]) < 1e-12),
            "inflation_factor_vs_n_max": (widths[0] / widths[-1]) if widths[-1] > 0 else None,
        }
    C = {"n_min": nmin, "n_max": nmax,
         "sqrt_n_max_over_n_min": math.sqrt(nmax / nmin),
         "per_p_demonstration": demo,
         "claim": "an interval CAN be placed without knowing the denominator: the envelope over the "
                  "admissible set is exactly the interval evaluated at n_min, and it is at most "
                  "sqrt(n_max/n_min) times wider than the unknown true one"}
    res["C_envelope"] = C

    # ---------- D. decision stability of the trap screen at the worst case ----------
    def verdict(p, cut, lo, hi):
        if lo >= cut:
            return "TRAP_CERTAIN"
        if hi < cut:
            return "CLEAR_CERTAIN"
        return "FRAGILE"
    D = {"cut_primary": TRAP_CUT, "cut_secondary": SEC_CUT, "evaluated_at_n": nmin,
         "methods": ["wilson95", "clopper_pearson95"], "per_gene": {}}
    for cut, key in ((TRAP_CUT, "ge_0.80"), (SEC_CUT, "ge_0.20")):
        counts = {"wilson95": {}, "clopper_pearson95": {}}
        frag = {"wilson95": [], "clopper_pearson95": []}
        for _, r in recs:
            g, p = r["gene"], r["rest_frac_dependent"]
            # point value is known to +/- HALF regardless of n; take the adverse end for each side
            wlo, whi = wilson(max(0.0, p - HALF), nmin)[0], wilson(min(1.0, p + HALF), nmin)[1]
            k = round(p * nmin)
            k = max(0, min(nmin, k))
            clo, chi = clopper_pearson(k, nmin)
            for m, (lo, hi) in (("wilson95", (wlo, whi)), ("clopper_pearson95", (clo, chi))):
                v = verdict(p, cut, lo, hi)
                counts[m][v] = counts[m].get(v, 0) + 1
                if v == "FRAGILE" and g not in frag[m]:
                    frag[m].append(g)
                D["per_gene"].setdefault(g, {})[key + "_" + m] = v
                D["per_gene"][g]["rest_frac_dependent"] = p
        D[key] = {"record_counts": counts, "fragile_genes": {m: sorted(v) for m, v in frag.items()}}
    # the SYNLETH headline specifically
    p_ews = 0.915
    D["EWSR1_headline"] = {
        "rest_frac_dependent": p_ews,
        "wilson95_at_n_min": wilson(p_ews, nmin),
        "wilson95_at_n_max": wilson(p_ews, nmax),
        "clopper_pearson95_at_n_min": clopper_pearson(round(p_ews * nmin), nmin),
        "trap_verdict_at_worst_case": verdict(p_ews, TRAP_CUT, wilson(max(0.0, p_ews - HALF), nmin)[0],
                                              wilson(min(1.0, p_ews + HALF), nmin)[1]),
    }
    res["D_decision_stability"] = D

    # ---------- E. descriptive vs inferential ----------
    res["E_descriptive_vs_inferential"] = {
        "descriptive_point_value_uncertainty": "+/- %.4f, from 3-dp rounding ALONE, independent of n" % HALF,
        "note": "the fraction of screened non-sarcoma lines that were dependent is pinned to "
                "+/-0.0005 by the rounding, whatever the denominator; the denominator is needed only "
                "to generalise from the screened lines to a population",
        "coverage_caveat": "DepMap's non-sarcoma arm is a convenience cohort, not an iid draw from a "
                           "defined population, so these are NOMINAL sampling intervals and their "
                           "coverage is not guaranteed by the design",
    }

    out = os.path.join(os.path.dirname(__file__), "denominator-envelope.json")
    json.dump(res, open(out, "w"), indent=2, sort_keys=False)

    # ---------- printed summary ----------
    print("A. RE-DERIVATION")
    print("   records=%d unique_genes=%d n_sarcoma=%s" % (A["n_records"], A["n_unique_genes"], A["n_sarcoma_values_seen"]))
    print("   fields=%s" % (",".join(A["record_field_names"])))
    print("   EWSR1 selectivity=%s rest_frac=%s sarcoma_frac=%s" % (A["EWSR1_selectivity"], A["EWSR1_rest_frac_dependent"], A["EWSR1_sarcoma_frac_dependent"]))
    print("   trap>=0.80: %d records / %d unique | >=0.20: %d records / %d unique"
          % (A["n_trap_ge_0.80_records"], A["n_trap_ge_0.80_unique"], A["n_trap_ge_0.20_records"], A["n_trap_ge_0.20_unique"]))
    print("   duplicated gene records: %s" % A["duplicated_gene_records"])
    print("B. ADMISSIBLE DENOMINATORS  count=%d  min=%d  max=%d  excluded_in_range=%d  reproduces_BIOMARKER_DEP_2=%s"
          % (B["n_admissible"], B["n_min"], B["n_max"], B["n_excluded_within_range"], B["reproduces_BIOMARKER_DEP_2"]))
    print("C. ENVELOPE  sqrt(n_max/n_min)=%.4f" % C["sqrt_n_max_over_n_min"])
    for p, v in demo.items():
        print("   p=%-6s width n_min=%.4f  n_max=%.4f  inflation=%.4f  monotone=%s  union==n_min=%s"
              % (p, v["width_at_n_min"], v["width_at_n_max"], v["inflation_factor_vs_n_max"],
                 v["width_monotone_decreasing_over_admissible_set"], v["union_over_admissible_equals_interval_at_n_min"]))
    print("D. TRAP-SCREEN DECISION STABILITY at worst-case n=%d" % nmin)
    for key in ("ge_0.80", "ge_0.20"):
        print("   cut %s  wilson=%s" % (key, D[key]["record_counts"]["wilson95"]))
        print("   cut %s  CP    =%s" % (key, D[key]["record_counts"]["clopper_pearson95"]))
        print("   cut %s  fragile(wilson)=%s" % (key, D[key]["fragile_genes"]["wilson95"]))
        print("   cut %s  fragile(CP)    =%s" % (key, D[key]["fragile_genes"]["clopper_pearson95"]))
    e = D["EWSR1_headline"]
    print("   EWSR1 0.915: wilson@n_min=[%.4f,%.4f] wilson@n_max=[%.4f,%.4f] CP@n_min=[%.4f,%.4f] verdict=%s"
          % (e["wilson95_at_n_min"][0], e["wilson95_at_n_min"][1], e["wilson95_at_n_max"][0],
             e["wilson95_at_n_max"][1], e["clopper_pearson95_at_n_min"][0], e["clopper_pearson95_at_n_min"][1],
             e["trap_verdict_at_worst_case"]))
    print("wrote %s" % out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
