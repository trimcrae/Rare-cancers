#!/usr/bin/env python3
"""
SYNLETH-3 -- What WOULD decide BAK1 and EGFR on the secondary (>=0.20) screen, and does any of
it exist in this checkout?

Read-only input: research/modalities/depmap-sarcoma-dependency.json (DepMap public 24Q4).
No network, no producer re-run, no fetch of CRISPRGeneEffect.csv, no new data.

Boundary against BIOMARKER-DEP-3: that lane produced a PER-QUANTITY BOUND TABLE (interval
envelopes for named published quantities: EWSR1/MCL1/BCL2L1/BRD9/FLI1/NR4A3 rest_frac,
rest_mean, selectivity, the Fisher p). I produce NO such table and re-bound none of those
quantities. I take exactly TWO screen VERDICTS (BAK1, EGFR at the >=0.20 cut), decompose why
each is undecidable into named components, and compute the critical sample size that would
decide each. Decidability of a verdict, not an interval per quantity.

Sections
  A  independent re-derivation of SYNLETH-2's envelope result (1126 / 943 / 2105; 23/44/0 at
     >=0.80; the two undecidables at >=0.20 and their stored fractions)
  B  anatomy of the undecidability -- three candidate causes separated arithmetically
  C  the minimal additional information that would decide each, quantified
  D  which of that, if any, exists in this checkout
"""
import json, math, os, sys
from scipy.stats import beta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
ART = os.path.join(ROOT, "research/modalities/depmap-sarcoma-dependency.json")

Z = 1.959963984540054
TRAP_CUT, SEC_CUT = 0.80, 0.20
DP = 3
HALF = 0.5 * 10 ** (-DP)          # +/-5e-4 from the 3-dp rounding of the stored fraction


def wilson(p, n, z=Z):
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return (lo, hi)


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


def verdict(cut, lo, hi, label_in="TRAP_CERTAIN", label_out="CLEAR_CERTAIN"):
    if lo >= cut:
        return label_in
    if hi < cut:
        return label_out
    return "FRAGILE"


def main():
    d = json.load(open(ART))
    recs = records(d)
    res = {"lane": "SYNLETH-3", "input": ART, "data_source": d["data_source"],
           "n_models_total": d["n_models_total"], "n_sarcoma_models": d["n_sarcoma_models"],
           "dependent_threshold": d["dependent_threshold"],
           "boundary_vs_BIOMARKER_DEP_3":
               "no per-quantity bound table is produced or reproduced here; this lane analyses "
               "the DECIDABILITY of two screen verdicts (BAK1, EGFR at the >=0.20 cut) and the "
               "critical n that would decide them"}

    # ================= A. independent re-derivation of SYNLETH-2 =================
    fr = sorted({r["rest_frac_dependent"] for _, r in recs})

    def admissible(n):
        for f in fr:
            hit = False
            k0 = int(round(f * n))
            for k in range(max(0, k0 - 2), min(n, k0 + 2) + 1):
                if round(k / n, DP) == f:
                    hit = True
                    break
            if not hit:
                return False
        return True

    adm = [n for n in range(1, d["n_models_total"] + 1) if admissible(n)]
    nmin, nmax = min(adm), max(adm)
    A = {"n_records": len(recs),
         "n_unique_genes": len({r["gene"] for _, r in recs}),
         "n_distinct_reported_rest_fracs": len(fr),
         "n_admissible": len(adm), "n_min": nmin, "n_max": nmax,
         "n_excluded_within_range": nmax - nmin + 1 - len(adm),
         "SYNLETH_2_reported": {"count": 1126, "n_min": 943, "n_max": 2105},
         "reproduces": (len(adm) == 1126 and nmin == 943 and nmax == 2105)}

    # the two screens at the worst case, exactly as SYNLETH-2 defined them
    part = {}
    for cut, key in ((TRAP_CUT, "ge_0.80"), (SEC_CUT, "ge_0.20")):
        counts, frag = {}, []
        for _, r in recs:
            p = r["rest_frac_dependent"]
            lo = wilson(max(0.0, p - HALF), nmin)[0]
            hi = wilson(min(1.0, p + HALF), nmin)[1]
            v = verdict(cut, lo, hi)
            counts[v] = counts.get(v, 0) + 1
            if v == "FRAGILE":
                frag.append((r["gene"], p))
        part[key] = {"record_counts": counts, "fragile": sorted(frag)}
    A["worst_case_partition"] = part
    A["reproduces_23_44_0"] = (part["ge_0.80"]["record_counts"].get("TRAP_CERTAIN") == 23 and
                               part["ge_0.80"]["record_counts"].get("CLEAR_CERTAIN") == 44 and
                               part["ge_0.80"]["record_counts"].get("FRAGILE", 0) == 0)
    A["reproduces_two_undecidables"] = (
        [g for g, _ in part["ge_0.20"]["fragile"]] == ["BAK1", "EGFR"] and
        dict(part["ge_0.20"]["fragile"]) == {"BAK1": 0.187, "EGFR": 0.205})
    res["A_rederivation"] = A

    TARGETS = {g: p for g, p in part["ge_0.20"]["fragile"]}
    if not TARGETS:
        TARGETS = {"BAK1": 0.187, "EGFR": 0.205}

    # ================= B. anatomy of the undecidability =================
    # Three candidate causes, separated arithmetically:
    #   (1) proximity      -- |p - cut|, the signed distance the evidence must cover
    #   (2) rounding       -- +/-HALF on the stored fraction, independent of n
    #   (3) interval width -- the sampling half-width at the denominator in play
    # A verdict is decided iff (2)+(3) < (1) on the relevant side.
    B = {"cut": SEC_CUT, "components": {}}
    for g, p in sorted(TARGETS.items()):
        prox = abs(p - SEC_CUT)
        side = "above" if p >= SEC_CUT else "below"
        w_min = wilson(p, nmin); w_max = wilson(p, nmax)
        hw_min = (w_min[1] - w_min[0]) / 2.0
        hw_max = (w_max[1] - w_max[0]) / 2.0
        # rounding-only verdict (no sampling model at all): descriptive reading
        desc_lo, desc_hi = p - HALF, p + HALF
        desc = verdict(SEC_CUT, desc_lo, desc_hi)
        B["components"][g] = {
            "stored_rest_frac_dependent": p,
            "side_of_cut": side,
            "1_proximity_|p-cut|": round(prox, 6),
            "2_rounding_halfwidth": HALF,
            "3_sampling_halfwidth_at_n_max_%d" % nmax: round(hw_max, 6),
            "3_sampling_halfwidth_at_n_min_%d" % nmin: round(hw_min, 6),
            "rounding_over_proximity": round(HALF / prox, 4),
            "sampling_at_n_max_over_proximity": round(hw_max / prox, 4),
            "descriptive_interval_from_rounding_alone": [round(desc_lo, 6), round(desc_hi, 6)],
            "descriptive_verdict": desc,
            "dominant_cause": ("sampling interval width against proximity"
                               if hw_max > HALF else "rounding"),
        }
    B["reading"] = ("For both genes the rounding term (5e-4) is smaller than the proximity term, "
                    "so the DESCRIPTIVE verdict -- 'of the non-sarcoma lines this panel screened, "
                    "what fraction scored below -0.5' -- is already decided at 3 dp with margin. "
                    "What is undecidable is the INFERENTIAL verdict, and there the sampling "
                    "half-width at the LARGEST admissible denominator still exceeds the distance "
                    "to the cut. So the cause is (1)+(3), not (2): neither more decimal places nor "
                    "recovery of the denominator can decide these two.")
    res["B_anatomy"] = B

    # ================= C. what WOULD decide each, quantified =================
    C = {}
    for g, p in sorted(TARGETS.items()):
        prox = abs(p - SEC_CUT)
        # (i) decimal places: does any number of dp on the stored fraction decide the inferential
        #     verdict? Shrink the rounding term to 0 and re-test at n_max.
        lo0, hi0 = wilson(p, nmax)
        dp_verdict_exact_fraction = verdict(SEC_CUT, lo0, hi0)
        # smallest dp at which the DESCRIPTIVE verdict is decided
        dp_needed_descriptive = None
        for dp in range(1, 9):
            h = 0.5 * 10 ** (-dp)
            pr = round(p, dp)
            if verdict(SEC_CUT, pr - h, pr + h) != "FRAGILE":
                dp_needed_descriptive = dp
                break
        # (ii) critical n: smallest n at which the Wilson interval (with the +/-HALF widening,
        #      and again with exact fraction) clears the cut
        def decided_at(n, widen):
            h = HALF if widen else 0.0
            lo = wilson(max(0.0, p - h), n)[0]
            hi = wilson(min(1.0, p + h), n)[1]
            return verdict(SEC_CUT, lo, hi) != "FRAGILE"
        n_crit_widened = n_crit_exact = None
        n = 100
        while n <= 5_000_000:
            if n_crit_widened is None and decided_at(n, True):
                n_crit_widened = n
            if n_crit_exact is None and decided_at(n, False):
                n_crit_exact = n
            if n_crit_widened and n_crit_exact:
                break
            n += 1
        # closed form for the exact-fraction case: n > z^2 p(1-p)/prox^2
        n_closed = Z * Z * p * (1 - p) / (prox * prox)
        # Clopper-Pearson cross-check at the critical n
        cp = None
        if n_crit_exact:
            k = int(round(p * n_crit_exact))
            cp = clopper_pearson(k, n_crit_exact)
        C[g] = {
            "stored_rest_frac_dependent": p,
            "decimal_places_needed_for_DESCRIPTIVE_verdict": dp_needed_descriptive,
            "decimal_places_already_stored": DP,
            "more_decimal_places_decide_INFERENTIAL_verdict": False,
            "inferential_verdict_at_n_max_with_EXACT_fraction": dp_verdict_exact_fraction,
            "critical_n_inferential_with_3dp_rounding": n_crit_widened,
            "critical_n_inferential_with_exact_fraction": n_crit_exact,
            "critical_n_closed_form_z2p(1-p)/prox2": round(n_closed, 1),
            "clopper_pearson95_at_critical_n": cp,
            "multiple_of_release_model_count_2105": (round(n_crit_exact / d["n_models_total"], 2)
                                                     if n_crit_exact else None),
            "multiple_of_largest_admissible_denominator": (round(n_crit_exact / nmax, 2)
                                                           if n_crit_exact else None),
        }
    res["C_what_would_decide"] = C

    # ================= D. what exists in this checkout =================
    D = {
        "stored_fraction_at_more_than_3dp": {
            "exists_in_checkout": False,
            "why": "depmap-sarcoma-dependency.json stores rest_frac_dependent rounded to 3 dp and "
                   "retains no count, no n_rest, no dispersion and no order statistic on the rest "
                   "arm (DEP-THRESHOLD C1, re-checked here in A)",
            "would_it_decide_either": False,
            "note": "and it would not help even if it existed -- see C: the rounding term is not "
                    "the binding constraint for either gene",
        },
        "the_exact_rest_arm_denominator": {
            "exists_in_checkout": False,
            "why": "recorded nowhere in the panel artifact; 1126 values remain admissible",
            "would_it_decide_either": False,
            "note": "even the LARGEST admissible denominator (%d) leaves both fragile" % nmax,
        },
        "per_line_CRISPRGeneEffect_matrix": {
            "exists_in_checkout": None,   # filled by the filesystem probe below
            "would_it_decide_either": False,
            "note": "it would remove the rounding term and fix n exactly, but n is bounded by the "
                    "release's own model count (2105) and both critical n exceed that, so the "
                    "matrix would NOT decide either gene inferentially. It WOULD confirm the "
                    "descriptive verdicts, which the stored 3-dp fractions already decide.",
        },
        "a_larger_CRISPR_panel": {
            "exists_in_checkout": False,
            "would_it_decide_either": True,
            "note": "this is the only thing that would, and it is not a fetch of anything that "
                    "exists -- it is more screened cell lines than DepMap 24Q4 contains",
        },
    }
    hits = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if "/.git" in dirpath:
            dirnames[:] = []
            continue
        for fn in filenames:
            if "CRISPRGeneEffect" in fn:
                hits.append(os.path.join(dirpath, fn))
    D["per_line_CRISPRGeneEffect_matrix"]["exists_in_checkout"] = bool(hits)
    D["per_line_CRISPRGeneEffect_matrix"]["filesystem_probe_hits"] = hits
    res["D_availability"] = D

    out = os.path.join(HERE, "undecidability-anatomy.json")
    json.dump(res, open(out, "w"), indent=2)

    # ---------------- printed summary ----------------
    print("A. RE-DERIVATION OF SYNLETH-2")
    print("   records=%d unique_genes=%d distinct_rest_fracs=%d" %
          (A["n_records"], A["n_unique_genes"], A["n_distinct_reported_rest_fracs"]))
    print("   admissible denominators: count=%d min=%d max=%d excluded_in_range=%d  reproduces=%s"
          % (A["n_admissible"], nmin, nmax, A["n_excluded_within_range"], A["reproduces"]))
    print("   >=0.80 at n=%d: %s  reproduces_23/44/0=%s" %
          (nmin, part["ge_0.80"]["record_counts"], A["reproduces_23_44_0"]))
    print("   >=0.20 at n=%d: %s  fragile=%s  reproduces=%s" %
          (nmin, part["ge_0.20"]["record_counts"], part["ge_0.20"]["fragile"],
           A["reproduces_two_undecidables"]))
    print("B. ANATOMY OF THE UNDECIDABILITY (cut 0.20)")
    for g, v in sorted(B["components"].items()):
        print("   %-5s p=%.3f (%s cut)  proximity=%.6f  rounding=%.6f (%.3fx prox)  "
              "sampling_hw@n=%d=%.6f (%.2fx prox)" %
              (g, v["stored_rest_frac_dependent"], v["side_of_cut"], v["1_proximity_|p-cut|"],
               v["2_rounding_halfwidth"], v["rounding_over_proximity"], nmax,
               v["3_sampling_halfwidth_at_n_max_%d" % nmax], v["sampling_at_n_max_over_proximity"]))
        print("         descriptive interval from rounding alone %s -> %s" %
              (v["descriptive_interval_from_rounding_alone"], v["descriptive_verdict"]))
    print("C. WHAT WOULD DECIDE EACH")
    for g, v in sorted(C.items()):
        print("   %-5s dp needed for descriptive verdict = %s (already stored: %d)" %
              (g, v["decimal_places_needed_for_DESCRIPTIVE_verdict"], DP))
        print("         inferential @ n_max with EXACT fraction: %s" %
              v["inferential_verdict_at_n_max_with_EXACT_fraction"])
        print("         critical n (3dp rounding) = %s ; (exact fraction) = %s ; closed form = %.1f"
              % (v["critical_n_inferential_with_3dp_rounding"],
                 v["critical_n_inferential_with_exact_fraction"],
                 v["critical_n_closed_form_z2p(1-p)/prox2"]))
        print("         = %.2fx the whole 24Q4 release (2105 models), %.2fx n_max" %
              (v["multiple_of_release_model_count_2105"],
               v["multiple_of_largest_admissible_denominator"]))
        print("         Clopper-Pearson 95%% at that n: %s" % (v["clopper_pearson95_at_critical_n"],))
    print("D. AVAILABILITY IN THIS CHECKOUT")
    for k, v in D.items():
        print("   %-34s exists=%s  decides=%s" % (k, v["exists_in_checkout"], v["would_it_decide_either"]))
    print("   CRISPRGeneEffect filesystem probe hits: %s" % (hits or "NONE"))
    print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
