#!/usr/bin/env python3
"""Two-platform concordance null for the PUB-KINASE-LEADS expression arm.

Question: the endpoint's leads are argued from "moves the same way in EMC on BOTH
array platforms".  How often does a RANDOM gene do that, at the same strength?
This script builds the empirical joint null from the committed background draws
in research/modalities/emc-expression-panels.json and places each lead gene in it.

Reads only.  Writes one JSON to this lane's directory.
No network, no GPU, no new data.  All inputs are committed artifacts.
"""
import json, math, os, sys

REPO = "/home/user/Rare-cancers"
SRC = os.path.join(REPO, "research/modalities/emc-expression-panels.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "two-platform-concordance-null.json")

P1 = "GSE24369_series_matrix.txt.gz"
P2 = "GSE4303-GPL3290_series_matrix.txt.gz"

LEADS = {
    "RET":   "lead 1 (RET) — the route's own named kinase",
    "SGK1":  "lead 4 (SGK1) — the kinase itself",
    "NDRG1": "lead 4 (SGK1) — the substrate whose abundance carries the claim",
    "ALK":   "lead 2 (ex-vivo screen hit) — named kinase",
    "ROS1":  "lead 2 (ex-vivo screen hit) — named kinase",
    "PRKDC": "lead 3 (DNA-PK) — catalytic subunit",
    "XRCC5": "lead 3 (DNA-PK) — Ku80",
    "XRCC6": "lead 3 (DNA-PK) — Ku70",
    "NR4A3": "positive control — the disease's own driver gene",
    "EGFR":  "negative-direction control named beside lead 2",
    "GFRA1": "RET co-receptor (route's own stated counter-evidence)",
    "GFRA2": "RET co-receptor",
    "GDNF":  "RET ligand",
    "HDAC3": "the class the screen re-read favours",
}


def welch(a, b):
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
    se2 = va / na + vb / nb
    if se2 <= 0:
        return None
    t = (ma - mb) / math.sqrt(se2)
    df_num = se2 ** 2
    df_den = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    df = df_num / df_den if df_den > 0 else float("nan")
    return {"t": t, "df": df, "mean_EMC": ma, "mean_comparator": mb, "delta": ma - mb}


def platform_bg_t(d, key):
    """Recompute Welch t (EMC - comparator) for every background gene on one platform."""
    plat = d["platforms"][key]
    bg = d["background_reads"][key]
    gsms = bg["gsms"]
    idx = {g: i for i, g in enumerate(gsms)}
    emc = [idx[g] for g in plat["EMC_gsms"] if g in idx]
    cmp_ = [idx[g] for g in plat["comparator_gsms"] if g in idx]
    out = {}
    for sym, zs in bg["z"].items():
        a = [zs[i] for i in emc if zs[i] is not None]
        b = [zs[i] for i in cmp_ if zs[i] is not None]
        r = welch(a, b)
        if r:
            r["n_EMC"], r["n_comparator"] = len(a), len(b)
            out[sym] = r
    return out, len(emc), len(cmp_)


def main():
    with open(SRC) as fh:
        d = json.load(fh)

    bg1, n1e, n1c = platform_bg_t(d, P1)
    bg2, n2e, n2c = platform_bg_t(d, P2)

    # --- VALIDATION: our recomputed t vs the artifact's own genome_wide_null t ---
    validation = {}
    for key, bg in ((P1, bg1), (P2, bg2)):
        placed = d["platforms"][key]["genome_wide_null"]["placed_wanted_genes"]
        shared = sorted(set(bg) & set(placed))
        diffs = [(s, round(bg[s]["t"], 4), placed[s]["t"],
                  abs(round(bg[s]["t"], 3) - placed[s]["t"])) for s in shared]
        worst = max(diffs, key=lambda x: x[3]) if diffs else None
        validation[key] = {
            "n_genes_compared": len(shared),
            "max_abs_difference_in_t": round(worst[3], 6) if worst else None,
            "worst_gene": worst[0] if worst else None,
            "worst_ours_vs_artifact": [worst[1], worst[2]] if worst else None,
            "n_within_0.002": sum(1 for x in diffs if x[3] <= 0.002),
            "_what_this_checks": ("our Welch t recomputed from background_reads per-sample z "
                                  "against the same statistic the artifact computed genome-wide "
                                  "for its curated genes. Agreement means the null frame below is "
                                  "on the same scale as the lead placements."),
        }

    # --- the joint null frame: genes drawn into BOTH background samples ---
    joint = sorted(set(bg1) & set(bg2))
    rows = []
    for s in joint:
        t1, t2 = bg1[s]["t"], bg2[s]["t"]
        rows.append({"symbol": s, "t1": t1, "t2": t2,
                     "concordant": (t1 > 0) == (t2 > 0),
                     "min_abs_t": min(abs(t1), abs(t2))})
    n = len(rows)
    n_conc = sum(1 for r in rows if r["concordant"])

    def joint_p(t1, t2):
        """Two-sided joint empirical p: fraction of null genes that are concordant in
        direction AND at least this strong on the weaker of the two platforms."""
        m = min(abs(t1), abs(t2))
        k = sum(1 for r in rows if r["concordant"] and r["min_abs_t"] >= m)
        return k, k / n if n else None

    pw1 = d["platforms"][P1]["genome_wide_null"]["placed_wanted_genes"]
    pw2 = d["platforms"][P2]["genome_wide_null"]["placed_wanted_genes"]

    leads = {}
    for g, why in LEADS.items():
        a, b = pw1.get(g), pw2.get(g)
        rec = {"role": why,
               "GPL6244_t": a["t"] if a else None,
               "GPL3290_t": b["t"] if b else None,
               "GPL6244_signed_percentile": a["signed_percentile"] if a else None,
               "GPL3290_signed_percentile": b["signed_percentile"] if b else None,
               "GPL6244_frac_of_array_two_sided": a["frac_of_array_at_least_as_extreme_two_sided"] if a else None,
               "GPL3290_frac_of_array_two_sided": b["frac_of_array_at_least_as_extreme_two_sided"] if b else None}
        if a is None or b is None:
            rec["joint"] = None
            rec["_why_no_joint"] = ("not readable on both platforms — an ABSENT READING, "
                                   "not a reading of absence")
        else:
            conc = (a["t"] > 0) == (b["t"] > 0)
            k, p = joint_p(a["t"], b["t"])
            rec["joint"] = {
                "concordant_direction": conc,
                "min_abs_t": round(min(abs(a["t"]), abs(b["t"])), 3),
                "n_null_genes_at_least_this_concordant_and_strong": k,
                "joint_empirical_p_two_sided": round(p, 5),
                "_reading": ("fraction of randomly drawn genes readable on both platforms that move "
                             "the same way in EMC on both, at least as strongly as this gene does on "
                             "its weaker platform"),
            }
            if not conc:
                rec["joint"]["_note"] = ("DISCORDANT — the joint p is reported for scale only and "
                                         "is not a support statement for this gene")
        leads[g] = rec

    result = {
        "_what": ("An empirical two-platform concordance null for the expression arm of "
                  "PUB-KINASE-LEADS, and the placement of each lead gene in it."),
        "_why": ("Every expression argument in the endpoint's four leads is of the form "
                 "'higher/lower in EMC on both platforms'. That argument has never been given a "
                 "negative: nothing in the repository states how often a RANDOM gene is concordant "
                 "across these two series at the same strength. This file supplies that negative."),
        "_this_is_not": ["a test of activation, phosphorylation or drug response",
                         "a multiple-testing correction (none is applied; the null is empirical)",
                         "evidence of efficacy, safety, selectivity or a therapeutic window",
                         "a replacement for the primary-record gradings in routes.json"],
        "generated_utc_input": d["generated_utc"],
        "source_artifact": "research/modalities/emc-expression-panels.json",
        "platforms": {
            P1: {"platform": "GPL6244", "n_EMC": n1e, "n_comparator": n1c,
                 "n_background_genes_scored": len(bg1),
                 "background_seed": d["background_reads"][P1]["seed"],
                 "background_sampling_frame": d["background_reads"][P1]["sampling_frame"]},
            P2: {"platform": "GPL3290", "n_EMC": n2e, "n_comparator": n2c,
                 "n_background_genes_scored": len(bg2),
                 "background_seed": d["background_reads"][P2]["seed"],
                 "background_sampling_frame": d["background_reads"][P2]["sampling_frame"]},
        },
        "validation": validation,
        "joint_null": {
            "n_genes_in_both_background_draws": n,
            "n_concordant_in_direction": n_conc,
            "frac_concordant_in_direction": round(n_conc / n, 4) if n else None,
            "_the_headline_negative": ("direction agreement alone, with no strength requirement, is "
                                       "reached by this fraction of random genes"),
            "min_abs_t_quantiles_among_concordant": None,
        },
        "leads": leads,
    }

    conc_sorted = sorted((r["min_abs_t"] for r in rows if r["concordant"]))
    if conc_sorted:
        def q(p):
            return round(conc_sorted[min(len(conc_sorted) - 1, int(p * len(conc_sorted)))], 3)
        result["joint_null"]["min_abs_t_quantiles_among_concordant"] = {
            "p50": q(0.5), "p75": q(0.75), "p90": q(0.90), "p95": q(0.95), "p99": q(0.99),
            "max": round(conc_sorted[-1], 3)}

    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=1)
    print("wrote", OUT)
    print("joint null frame n =", n, "; concordant in direction =", n_conc,
          "(%.3f)" % (n_conc / n if n else float('nan')))
    for k, v in validation.items():
        print("validation", k, "n=", v["n_genes_compared"],
              "max|dt|=", v["max_abs_difference_in_t"], "worst=", v["worst_gene"])
    for g, rec in leads.items():
        j = rec["joint"]
        print("%-7s t1=%-8s t2=%-8s %s" % (
            g, rec["GPL6244_t"], rec["GPL3290_t"],
            ("joint p=%.4f conc=%s" % (j["joint_empirical_p_two_sided"], j["concordant_direction"]))
            if j else "NOT READABLE ON BOTH"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
