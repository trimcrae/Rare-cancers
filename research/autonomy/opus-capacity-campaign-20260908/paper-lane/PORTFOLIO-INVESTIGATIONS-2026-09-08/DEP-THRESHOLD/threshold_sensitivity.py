#!/usr/bin/env python3
"""
DEP-THRESHOLD — how much of the DepMap sarcoma panel's published structure is an artifact of
the -0.5 binarisation cut, and of reading `selectivity` without its complement
`rest_frac_dependent`?

Sole input (read-only): research/modalities/depmap-sarcoma-dependency.json
No network. No re-run of the producer. No new data. Deterministic.

Three parts.

  A. COMPUTABILITY AUDIT. For every retained record, enumerate the thresholds t at which
     frac(gene effect < t) is EXACTLY recoverable from what the artifact retains. The answer
     decides whether a threshold sweep exists at all. We do not invent a distribution.

  B. DISTRIBUTION-FREE BOUNDS. Where a point value is not recoverable, a rigorous interval
     still is. Given a per-arm mean mu, the single recorded fraction p = P(X < t0) at
     t0 = -0.5, and an assumed support [L, U] on the Chronos gene-effect scale, the set of
     distributions consistent with those constraints has an exactly computable range for
     q = P(X < t) at any other t. Derivation in `bounds_frac()`. These are BOUNDS, not
     estimates; where they are wide, that width is the result.

  C. CORRECTED READING. Every selectivity reported beside rest_frac_dependent, with the
     EWSR1/CDK7/CDK9 pan-essential trap flagged, and the rank disagreement between
     selectivity (a mean shift) and delta_frac (the actual dependent-fraction margin)
     measured.

Output: threshold-sensitivity.json
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
SRC = os.path.join(REPO, "research", "modalities", "depmap-sarcoma-dependency.json")
OUT = os.path.join(HERE, "threshold-sensitivity.json")

T0 = -0.5                      # the published binarisation cut
SWEEP = [-2.0, -1.5, -1.0, -0.75, -0.5, -0.25, 0.0, 0.25]
# Assumed support of the Chronos gene-effect scale. STATED ASSUMPTION, not a retained field.
SUPPORTS = {"default": (-4.0, 1.5), "narrow": (-3.0, 1.0), "wide": (-6.0, 2.0)}


# ---------------------------------------------------------------------------- B: bounds
def bounds_frac(mu, p, t, t0=T0, L=-4.0, U=1.5):
    """Exact range of q = P(X < t) over all distributions on [L, U] with E[X] = mu and
    P(X < t0) = p.

    Split the mass into A = {X < t0} (mass p) and B = {X >= t0} (mass 1 - p).

    t < t0 (a STRICTER cut): {X < t} is a sub-part of A, so 0 <= q <= p. With mass q of A
    below t and p - q of A in [t, t0), and B anywhere in [t0, U], the attainable mean range
    for a given q is
        [ q*L + (p-q)*t + (1-p)*t0 ,  q*t + (p-q)*t0 + (1-p)*U ].
    Requiring mu to lie in it gives
        q >= (p*t + (1-p)*t0 - mu) / (t - L)     and     q <= (p*t0 + (1-p)*U - mu) / (t0 - t).

    t > t0 (a LOOSER cut): {X < t} contains all of A, so p <= q <= 1. With mass q - p of B in
    [t0, t) and 1 - q of B in [t, U], and A anywhere in [L, t0), the attainable mean range is
        [ p*L + (q-p)*t0 + (1-q)*t ,  p*t0 + (q-p)*t + (1-q)*U ],
    both endpoints decreasing in q, giving
        q >= (p*L - p*t0 + t - mu) / (t - t0)    and     q <= (p*(t0 - t) + U - mu) / (U - t).

    t == t0 returns the recorded point exactly. Returns (lo, hi), or None if infeasible
    (which would mean mu, p and [L, U] are mutually inconsistent).
    """
    eps = 1e-12
    if abs(t - t0) < eps:
        return (p, p)
    if t < t0:
        lo = max(0.0, (p * t + (1 - p) * t0 - mu) / (t - L))
        hi = min(p, (p * t0 + (1 - p) * U - mu) / (t0 - t))
    else:
        lo = max(p, (p * L - p * t0 + t - mu) / (t - t0))
        hi = min(1.0, (p * (t0 - t) + U - mu) / (U - t))
    lo, hi = max(0.0, min(1.0, lo)), max(0.0, min(1.0, hi))
    if lo > hi + 1e-9:
        return None
    return (round(lo, 4), round(min(hi, 1.0), 4))


def width(b):
    return None if b is None else round(b[1] - b[0], 4)


# ---------------------------------------------------------------------------- load
def load(path):
    with open(path) as fh:
        return json.load(fh)


def collect_gene_records(d):
    """Every per-gene record carrying the sarcoma/rest split, with its provenance path."""
    recs = []
    for grp, lst in d["genes_by_group"].items():
        for r in lst:
            recs.append({"path": f"genes_by_group/{grp}", "group": grp, **r})
    for r in d.get("context_genes", []):
        recs.append({"path": "context_genes", "group": "context", **r})
    for k, v in d.get("fusion_addiction_proxy", {}).items():
        if isinstance(v, dict) and "selectivity" in v:
            recs.append({"path": f"fusion_addiction_proxy/{k}", "group": "fusion_proxy", **v})
    # de-duplicate on (gene, sarcoma_mean, selectivity): the same gene may be echoed
    seen, uniq = set(), []
    for r in recs:
        key = (r["gene"], r["sarcoma_mean"], r["selectivity"])
        if key in seen:
            r["duplicate_of_earlier_record"] = True
        else:
            seen.add(key)
        uniq.append(r)
    return uniq


# ---------------------------------------------------------------------------- A: audit
def computability_audit(d, recs):
    """Which thresholds are EXACTLY computable from the retained fields, per record class."""
    per_gene_fields = sorted(set().union(*[set(r.keys()) for r in recs]) - {"path", "group",
                                                                           "duplicate_of_earlier_record"})
    dispersion_fields = [f for f in per_gene_fields
                         if any(k in f for k in ("sd", "std", "var", "quantile", "q25", "q75",
                                                 "iqr", "median", "min", "max", "values", "per_line"))]
    audit = {
        "published_threshold": d["dependent_threshold"],
        "per_gene_record_fields": per_gene_fields,
        "dispersion_or_order_statistic_fields_present": dispersion_fields,
        "n_gene_records_with_sarcoma_rest_split": len(recs),
        "n_unique_genes": len(set(r["gene"] for r in recs)),
        "exactly_computable_thresholds": {},
        "verdict": None,
    }

    # (i) the 2-arm panel records: one fraction each arm, at one cut, plus a mean. Nothing else.
    audit["exactly_computable_thresholds"]["panel_gene_records (sarcoma & rest arms)"] = {
        "thresholds": [T0],
        "why": ("each record retains sarcoma_mean, rest_mean, selectivity, and ONE fraction per "
                "arm evaluated at the fixed cut -0.5, plus n_sarcoma. A fraction at any other "
                "cut is a functional of the per-line distribution, and no order statistic, "
                "quantile, SD or per-line value is retained for these records."),
        "n_records": len(recs),
    }

    # (ii) the NR4A paralogue block retains median and min -> two extra exact points, pan-panel only
    nr4a = {}
    for g, r in d["nr4a_paralogue_comparison"]["paralogues"].items():
        pts = {
            f"t <= {r['min_gene_effect']} (min_gene_effect)": 0.0,
            f"t = {r['median_gene_effect']} (median_gene_effect)": 0.5,
            f"t = {T0}": r["frac_dependent"],
        }
        nr4a[g] = {"exact_points": pts, "n_lines": r["n_lines"],
                   "arm": "whole panel (NOT split into sarcoma / rest)"}
    audit["exactly_computable_thresholds"]["nr4a_paralogue_comparison"] = {
        "thresholds": "3 exact points per paralogue (see per-gene), because median and min are retained",
        "per_gene": nr4a,
        "why": ("median_gene_effect fixes P(X < median) = 0.5 and min_gene_effect fixes "
                "P(X < t) = 0 for all t <= min. These are the only records in the artifact that "
                "retain order statistics. They are pan-panel, so they cannot enter a "
                "sarcoma-vs-rest selectivity sweep."),
        "usable_for_selectivity_sweep": False,
    }

    # (iii) subtype blocks: mean + one fraction, no dispersion
    subt = {}
    for block in ("self_validation", "BRD9_by_fusion_sarcoma_subtype", "fusion_addiction_proxy"):
        for k, v in d.get(block, {}).items():
            if isinstance(v, dict) and "mean_gene_effect" in v:
                subt[f"{block}/{k}"] = {"n": v["n"], "fields": sorted(v.keys())}
    audit["exactly_computable_thresholds"]["subtype_blocks"] = {
        "thresholds": [T0], "records": subt,
        "why": "mean_gene_effect + frac_dependent at -0.5 + n. No dispersion, no order statistics.",
    }

    audit["verdict"] = (
        "A THRESHOLD SWEEP OF frac_dependent IS NOT COMPUTABLE FROM THIS ARTIFACT. Exactly one "
        "threshold, the published -0.5, is evaluable for every record carrying the sarcoma/rest "
        "split — i.e. for the entire selectivity panel and every subtype block. The only records "
        "with additional exact points are the three NR4A paralogues (median and min retained), and "
        "those are pan-panel, so they cannot be turned into a selectivity sweep. Any other "
        "threshold would require a per-line distribution that the producer discards at "
        "depmap_sarcoma_dependency.py stats(); reconstructing one would be inventing data."
    )
    return audit


# ---------------------------------------------------------------------------- invariance
def invariance_classification(recs):
    """Which published quantities move with the threshold at all."""
    return {
        "threshold_INVARIANT_by_construction": {
            "quantities": ["sarcoma_mean", "rest_mean", "selectivity (= rest_mean - sarcoma_mean)"],
            "n_gene_records": len(recs),
            "argument": ("selectivity is a difference of two arithmetic means over all lines in "
                         "each arm. The cut -0.5 does not enter its definition "
                         "(depmap_sarcoma_dependency.py stats(): "
                         "'selectivity': round(float(r.mean() - s.mean()), 3)). Therefore EVERY "
                         "gene's selectivity value, its sign, and the complete selectivity rank "
                         "order are exactly threshold-stable — trivially, not empirically. No "
                         "selectivity rank can flip under a different cut."),
            "consequence": ("the -0.5 cut is NOT the source of the selectivity artifact. The "
                            "selectivity artifact is an INTERPRETATION defect (reading a mean "
                            "shift as a therapeutic window without its complement), not a "
                            "binarisation defect. These are two different failures and the "
                            "distinction matters for what has to be repaired."),
        },
        "threshold_BOUND_and_uncheckable": {
            "quantities": ["sarcoma_frac_dependent", "rest_frac_dependent",
                           "delta_frac (= sarcoma_frac_dependent - rest_frac_dependent)",
                           "subtype frac_dependent", "self_validation _pass_criterion",
                           "'dependency in the large majority of lines'",
                           "'near-universal dependency' / 'pan-essential' verdicts"],
            "argument": ("each is P(X < t) at the single retained t = -0.5. Its value at any "
                         "other t is a functional of a discarded distribution. Its "
                         "threshold-stability can be BOUNDED (part B) but not evaluated."),
        },
    }


# ---------------------------------------------------------------------------- C: corrected reading
def trap_class(sel, sar_f, rest_f):
    """The EWSR1/CDK7/CDK9 trap: a large |selectivity| sitting on top of a near-universal
    dependency, where the mean shift is a change in the DEPTH of an essentiality both arms
    already have, not a margin between a dependent and a non-dependent arm."""
    delta = round(sar_f - rest_f, 4)
    if rest_f >= 0.80:
        sev = "PAN_ESSENTIAL_TRAP"
    elif rest_f >= 0.50:
        sev = "MAJORITY_ESSENTIAL_OUTSIDE_SARCOMA"
    elif rest_f >= 0.20:
        sev = "SUBSTANTIAL_ESSENTIALITY_OUTSIDE_SARCOMA"
    else:
        sev = "clear_of_trap"
    caught = sev != "clear_of_trap"
    return delta, sev, caught


def spearman(a, b):
    n = len(a)
    ra, rb = rank(a), rank(b)
    mean_a, mean_b = sum(ra) / n, sum(rb) / n
    num = sum((x - mean_a) * (y - mean_b) for x, y in zip(ra, rb))
    den = (sum((x - mean_a) ** 2 for x in ra) * sum((y - mean_b) ** 2 for y in rb)) ** 0.5
    return round(num / den, 4) if den else None


def rank(vals):
    order = sorted(range(len(vals)), key=lambda i: -vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def main():
    d = load(SRC)
    recs = collect_gene_records(d)
    uniq = [r for r in recs if not r.get("duplicate_of_earlier_record")]

    out = {
        "_note": ("DEP-THRESHOLD: threshold-sensitivity and pan-essential-trap audit of "
                  "research/modalities/depmap-sarcoma-dependency.json. Serves the converged "
                  "defect found by PUB-BIOMARKER-DEP (the -0.5 binarisation carries the argument "
                  "and is validated by nothing) and PUB-SYNLETH (selectivity must be read beside "
                  "rest_frac_dependent). Offline, read-only, producer not re-run."),
        "generated_by": "threshold_sensitivity.py",
        "input": "research/modalities/depmap-sarcoma-dependency.json",
        "input_data_source": d["data_source"],
        "not_an_EMC_measurement": ("no DepMap line in this panel is EMC. Nothing here is an "
                                   "efficacy, safety, selectivity, therapeutic-window or "
                                   "clinical-readiness claim for either route."),
        "A_computability_audit": computability_audit(d, uniq),
        "B_threshold_invariance": invariance_classification(uniq),
    }

    # ---- self-check: integrality of the recorded fractions at n_sarcoma
    integ = []
    for r in uniq:
        k = r["sarcoma_frac_dependent"] * r["n_sarcoma"]
        integ.append(abs(k - round(k)) < 0.05)
    out["A_computability_audit"]["self_check_fraction_integrality"] = {
        "n_pass": sum(integ), "n_total": len(integ),
        "why": "sarcoma_frac_dependent * n_sarcoma should be an integer count; confirms the "
               "recorded fractions are exact counts over the same 91-line denominator.",
    }

    # ---- B: bounds sweep
    bounds = {}
    for name, (L, U) in SUPPORTS.items():
        per_gene = {}
        for r in uniq:
            g = r["gene"]
            row = {}
            for t in SWEEP:
                bs = bounds_frac(r["sarcoma_mean"], r["sarcoma_frac_dependent"], t, L=L, U=U)
                br = bounds_frac(r["rest_mean"], r["rest_frac_dependent"], t, L=L, U=U)
                if bs is None or br is None:
                    row[str(t)] = {"infeasible": True}
                    continue
                dlo, dhi = bs[0] - br[1], bs[1] - br[0]
                if dhi - dlo < 1e-9:
                    sign = ("determined_exactly_zero" if abs(dlo) < 1e-9 else
                            "determined_sarcoma_more_dependent" if dlo > 0 else
                            "determined_rest_more_dependent")
                elif dlo > 0:
                    sign = "sarcoma_more_dependent"
                elif dhi < 0:
                    sign = "rest_more_dependent"
                else:
                    sign = "UNDETERMINED"
                row[str(t)] = {
                    "sarcoma_frac_bounds": bs, "rest_frac_bounds": br,
                    "sarcoma_bound_width": width(bs), "rest_bound_width": width(br),
                    "delta_frac_bounds": [round(dlo, 4), round(dhi, 4)],
                    "delta_frac_sign": sign,
                }
            per_gene[g] = row
        bounds[name] = {"support_assumed_[L,U]": [L, U], "per_gene": per_gene}

    # how many genes have a sign-determined delta_frac at each threshold, per support
    determined = {}
    for name, blk in bounds.items():
        determined[name] = {}
        for t in SWEEP:
            signs = [row[str(t)].get("delta_frac_sign") for row in blk["per_gene"].values()]
            n_det = sum(1 for x in signs if x not in (None, "UNDETERMINED"))
            n_zero = sum(1 for x in signs if x == "determined_exactly_zero")
            n_nonzero_det = n_det - n_zero
            widths = [row[str(t)]["sarcoma_bound_width"] for row in blk["per_gene"].values()
                      if row[str(t)].get("sarcoma_bound_width") is not None]
            dwidths = sorted(round(row[str(t)]["delta_frac_bounds"][1]
                                   - row[str(t)]["delta_frac_bounds"][0], 4)
                             for row in blk["per_gene"].values()
                             if row[str(t)].get("delta_frac_bounds"))
            determined[name][str(t)] = {
                "n_genes_delta_frac_fully_determined": n_det,
                "n_of_those_determined_to_be_exactly_zero": n_zero,
                "n_genes_with_a_determined_NON_ZERO_delta_frac": n_nonzero_det,
                "n_genes_UNDETERMINED": len(signs) - n_det,
                "n_genes": len(blk["per_gene"]),
                "median_sarcoma_frac_bound_width": round(sorted(widths)[len(widths) // 2], 4) if widths else None,
                "median_delta_frac_bound_width": dwidths[len(dwidths) // 2] if dwidths else None,
            }
    out["C_distribution_free_bounds"] = {
        "method": ("exact range of P(X < t) over all distributions on an assumed support [L, U] "
                   "consistent with the retained mean and the ONE retained fraction at -0.5. "
                   "See bounds_frac() docstring for the derivation. [L, U] is a STATED "
                   "ASSUMPTION about the Chronos gene-effect scale, not a retained field; three "
                   "supports are reported so its influence is visible."),
        "sweep_thresholds": SWEEP,
        "summary_sign_determination": determined,
        "bounds": bounds,
    }

    # ---- D: corrected reading
    table = []
    for r in uniq:
        delta, sev, caught = trap_class(r["selectivity"], r["sarcoma_frac_dependent"],
                                        r["rest_frac_dependent"])
        table.append({
            "gene": r["gene"], "group": r["group"], "path": r["path"],
            "selectivity": r["selectivity"],
            "sarcoma_mean": r["sarcoma_mean"], "rest_mean": r["rest_mean"],
            "sarcoma_frac_dependent": r["sarcoma_frac_dependent"],
            "rest_frac_dependent": r["rest_frac_dependent"],
            "delta_frac_at_-0.5": delta,
            "trap_class": sev, "caught_by_pan_essential_trap": caught,
            "n_sarcoma": r["n_sarcoma"],
        })
    table.sort(key=lambda x: -x["selectivity"])
    for i, row in enumerate(table, 1):
        row["rank_by_selectivity"] = i
    by_delta = sorted(table, key=lambda x: -x["delta_frac_at_-0.5"])
    for i, row in enumerate(by_delta, 1):
        row["rank_by_delta_frac"] = i
    for row in table:
        row["rank_shift_selectivity_minus_deltafrac"] = (row["rank_by_selectivity"]
                                                         - row["rank_by_delta_frac"])

    rho = spearman([r["selectivity"] for r in table], [r["delta_frac_at_-0.5"] for r in table])
    caught_rows = [r for r in table if r["caught_by_pan_essential_trap"]]
    out["D_corrected_reading"] = {
        "rule": ("a selectivity value is only a candidate therapeutic margin when the arm it is "
                 "selective AGAINST is largely non-dependent. Read every selectivity beside "
                 "rest_frac_dependent."),
        "trap_definition": {
            "PAN_ESSENTIAL_TRAP": "rest_frac_dependent >= 0.80 — a near-universal dependency "
                                  "outside sarcoma; selectivity measures depth, not margin",
            "MAJORITY_ESSENTIAL_OUTSIDE_SARCOMA": "0.50 <= rest_frac_dependent < 0.80",
            "SUBSTANTIAL_ESSENTIALITY_OUTSIDE_SARCOMA": "0.20 <= rest_frac_dependent < 0.50",
            "clear_of_trap": "rest_frac_dependent < 0.20",
        },
        "n_records": len(table),
        "n_caught_by_trap": len(caught_rows),
        "genes_caught_by_trap": [{"gene": r["gene"], "selectivity": r["selectivity"],
                                  "rest_frac_dependent": r["rest_frac_dependent"],
                                  "sarcoma_frac_dependent": r["sarcoma_frac_dependent"],
                                  "delta_frac_at_-0.5": r["delta_frac_at_-0.5"],
                                  "trap_class": r["trap_class"],
                                  "rank_by_selectivity": r["rank_by_selectivity"],
                                  "rank_by_delta_frac": r["rank_by_delta_frac"]}
                                 for r in sorted(caught_rows, key=lambda x: -x["selectivity"])],
        "spearman_selectivity_vs_delta_frac": rho,
        "top10_by_selectivity": [r["gene"] for r in table[:10]],
        "top10_by_delta_frac": [r["gene"] for r in by_delta[:10]],
        "table": table,
    }

    # ---- E: one-sided monotone stability of each published verdict
    # P(X < t) is non-decreasing in t. So for t < -0.5 every fraction can only fall, and for
    # t > -0.5 it can only rise. That makes each BINARY verdict stable in exactly one direction.
    mono = []
    for r in uniq:
        sf, rf = r["sarcoma_frac_dependent"], r["rest_frac_dependent"]
        if sf >= 0.90:
            v = "pan/near-universally dependent in sarcoma"
            stab = "STABLE only under a LOOSER cut (t > -0.5); a stricter cut can only lower it"
        elif sf <= 0.10:
            v = "not a dependency in sarcoma"
            stab = "STABLE only under a STRICTER cut (t < -0.5); a looser cut can only raise it"
        else:
            v = "intermediate dependent fraction"
            stab = "not stable in either direction as a binary verdict"
        d = round(sf - rf, 4)
        mono.append({
            "gene": r["gene"], "sarcoma_frac_dependent": sf, "rest_frac_dependent": rf,
            "binary_verdict_at_-0.5": v, "one_sided_stability": stab,
            "delta_frac_at_-0.5": d,
            "margin_verdict_stability": ("delta_frac is a DIFFERENCE of two fractions and is "
                                         "monotone in NEITHER direction: it is unstable to a cut "
                                         "change either way, and part C shows the retained "
                                         "summaries cannot bound it usefully at any other cut"),
        })
    out["E_one_sided_monotone_stability"] = {
        "rule": ("P(X < t) is non-decreasing in t. A 'pan-essential' verdict (frac ~ 1) therefore "
                 "survives any LOOSER cut and is unverifiable under a stricter one; a "
                 "'non-dependent' verdict (frac ~ 0) survives any STRICTER cut and is "
                 "unverifiable under a looser one; and a MARGIN (delta_frac, the quantity both "
                 "papers actually argue from) survives NEITHER."),
        "n_pan_essential_in_sarcoma_frac_ge_0.90": sum(1 for m in mono if m["sarcoma_frac_dependent"] >= 0.90),
        "n_non_dependent_in_sarcoma_frac_le_0.10": sum(1 for m in mono if m["sarcoma_frac_dependent"] <= 0.10),
        "n_intermediate": sum(1 for m in mono if 0.10 < m["sarcoma_frac_dependent"] < 0.90),
        "per_gene": mono,
    }

    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"wrote {OUT}")

    # ---- stdout report
    a = out["A_computability_audit"]
    print("\n=== A. COMPUTABILITY AUDIT ===")
    print("published cut:", a["published_threshold"])
    print("per-gene retained fields:", a["per_gene_record_fields"])
    print("dispersion/order-statistic fields on gene records:",
          a["dispersion_or_order_statistic_fields_present"] or "NONE")
    print("fraction-integrality self-check: %d/%d" % (
        a["self_check_fraction_integrality"]["n_pass"], a["self_check_fraction_integrality"]["n_total"]))
    print("VERDICT:", a["verdict"])

    print("\n=== B. THRESHOLD INVARIANCE ===")
    print("invariant:", out["B_threshold_invariance"]["threshold_INVARIANT_by_construction"]["quantities"])
    print("bound    :", out["B_threshold_invariance"]["threshold_BOUND_and_uncheckable"]["quantities"])

    print("\n=== C. DISTRIBUTION-FREE BOUNDS (default support [-4.0, 1.5]) ===")
    print(f"{'t':>7}{'det':>6}{'of which =0':>13}{'det NON-ZERO':>14}{'undet':>8}"
          f"{'med frac width':>16}{'med dfrac width':>17}")
    for t in SWEEP:
        st = determined["default"][str(t)]
        print(f"{t:>7}{st['n_genes_delta_frac_fully_determined']:>6}"
              f"{st['n_of_those_determined_to_be_exactly_zero']:>13}"
              f"{st['n_genes_with_a_determined_NON_ZERO_delta_frac']:>14}"
              f"{st['n_genes_UNDETERMINED']:>8}{st['median_sarcoma_frac_bound_width']:>16}"
              f"{st['median_delta_frac_bound_width']:>17}")
    print("support sensitivity (n determined NON-ZERO delta_frac at t=-1.0):",
          {k: determined[k]["-1.0"]["n_genes_with_a_determined_NON_ZERO_delta_frac"] for k in SUPPORTS})
    print("\nworked examples at the default support, the genes the two papers argue from:")
    for g in ("EWSR1", "BCL2L1", "MCL1", "FLI1", "BRD9", "CDK7"):
        row = bounds["default"]["per_gene"].get(g)
        if not row:
            continue
        for t in (-1.0, -0.25):
            e = row[str(t)]
            print(f"  {g:<8} t={t:<6} sarcoma_frac in {e['sarcoma_frac_bounds']}  "
                  f"rest_frac in {e['rest_frac_bounds']}  delta in {e['delta_frac_bounds']}  "
                  f"-> {e['delta_frac_sign']}")

    print("\n=== D. CORRECTED READING — selectivity BESIDE rest_frac_dependent ===")
    print(f"{'gene':<10}{'sel':>8}{'sar_f':>8}{'rest_f':>8}{'dfrac':>8}  {'rank_sel':>8}{'rank_df':>8}  trap")
    for r in table:
        print(f"{r['gene']:<10}{r['selectivity']:>8.3f}{r['sarcoma_frac_dependent']:>8.3f}"
              f"{r['rest_frac_dependent']:>8.3f}{r['delta_frac_at_-0.5']:>8.3f}  "
              f"{r['rank_by_selectivity']:>8}{r['rank_by_delta_frac']:>8}  "
              f"{'' if not r['caught_by_pan_essential_trap'] else r['trap_class']}")
    print(f"\ntrap-caught: {len(caught_rows)}/{len(table)}   "
          f"spearman(selectivity, delta_frac) = {rho}")
    print("top10 by selectivity:", out["D_corrected_reading"]["top10_by_selectivity"])
    print("top10 by delta_frac :", out["D_corrected_reading"]["top10_by_delta_frac"])

    e = out["E_one_sided_monotone_stability"]
    print("\n=== E. ONE-SIDED MONOTONE STABILITY OF THE BINARY VERDICTS ===")
    print(e["rule"])
    print("pan-essential-in-sarcoma (frac >= 0.90):", e["n_pan_essential_in_sarcoma_frac_ge_0.90"],
          "| non-dependent (frac <= 0.10):", e["n_non_dependent_in_sarcoma_frac_le_0.10"],
          "| intermediate:", e["n_intermediate"], "| of", len(e["per_gene"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
