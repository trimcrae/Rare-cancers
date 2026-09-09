#!/usr/bin/env python3
"""BIOMARKER-DEP-2 — re-derive, from the underlying artifact, every number this lane relies on that
a prior lane reported. Read-only on research/modalities/depmap-sarcoma-dependency.json. No network.
⛔ No EMC observation; no efficacy/safety/selectivity/therapeutic-window claim."""
import json, math, os
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
SRC = os.path.join(REPO, "research/modalities/depmap-sarcoma-dependency.json")
d = json.load(open(SRC))
recs = []
def walk(o, p):
    if isinstance(o, dict):
        if "gene" in o and "sarcoma_frac_dependent" in o: recs.append((p, o))
        for k, v in o.items(): walk(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, p + "/%d" % i)
walk(d, "")
from collections import Counter
c = Counter(r["gene"] for _, r in recs)
dups = {g: n for g, n in c.items() if n > 1}
dup_paths = {g: sorted(p.rsplit("/", 1)[0] for p, r in recs if r["gene"] == g) for g in dups}

def consistent(f, n): return any(round(k / n, 3) == round(f, 3) for k in range(n + 1))
sar_denoms = [n for n in range(2, 2106) if all(consistent(r["sarcoma_frac_dependent"], n) for _, r in recs)]
rest_denoms = [n for n in range(2, 2106) if all(consistent(r["rest_frac_dependent"], n) for _, r in recs)]

def fisher_p(a, b, cc, dd):
    n1, n2, k = a + b, cc + dd, a + cc
    tot = comb(n1 + n2, k); p = 0.0
    for x in range(max(0, k - n2), min(n1, k) + 1):
        if x >= a: p += comb(n1, x) * comb(n2, k - x) / tot
    return p
def power(n1, p1, n2, p0, alpha=0.05):
    pw = 0.0
    for a in range(n1 + 1):
        pa = comb(n1, a) * p1 ** a * (1 - p1) ** (n1 - a)
        if pa == 0: continue
        for cc in range(n2 + 1):
            pc = comb(n2, cc) * p0 ** cc * (1 - p0) ** (n2 - cc)
            if pc < 1e-15: continue
            if fisher_p(a, n1 - a, cc, n2 - cc) <= alpha: pw += pa * pc
    return pw
def wilson(k, n, z=1.959963985):
    ph = k / n; den = 1 + z * z / n
    ctr = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return round(ctr - h, 3), round(ctr + h, 3)

by = {}
for _, r in recs: by[r["gene"]] = r
sv = d["self_validation"]["BRD9_in_synovial"]
out = {
 "_note": "Independent re-derivation of prior-lane numbers from the committed artifact. "
          "No EMC observation. No clinical claim.",
 "source": "research/modalities/depmap-sarcoma-dependency.json",
 "record_counts": {"records_with_sarcoma_rest_split": len(recs), "unique_genes": len(c),
                   "duplicate_genes": dups, "duplicate_record_locations": dup_paths},
 "denominator": {
   "n_sarcoma_field_values": sorted({r["n_sarcoma"] for _, r in recs}),
   "sarcoma_denominators_consistent_with_every_rounded_fraction": sar_denoms[:8],
   "sarcoma_smallest_consistent": sar_denoms[0],
   "n_sarcoma_models_in_release": d["n_sarcoma_models"], "n_models_total": d["n_models_total"],
   "rest_denominator_count_consistent": len(rest_denoms),
   "rest_denominator_range": [rest_denoms[0], rest_denoms[-1]],
   "rest_denominator_recorded_anywhere": False},
 "pan_essential_trap": {
   "rest_frac_ge_0.80_records": len([1 for _, r in recs if r["rest_frac_dependent"] >= 0.80]),
   "rest_frac_ge_0.80_unique_genes": len({r["gene"] for _, r in recs if r["rest_frac_dependent"] >= 0.80}),
   "rest_frac_ge_0.20_records": len([1 for _, r in recs if r["rest_frac_dependent"] >= 0.20]),
   "rest_frac_ge_0.20_unique_genes": len({r["gene"] for _, r in recs if r["rest_frac_dependent"] >= 0.20})},
 "spot_genes": {g: by[g] for g in ("EWSR1", "BRD9", "MCL1", "BCL2L1", "CDK7", "FLI1", "NR4A3")},
 "brd9_synovial": {
   "recorded": sv,
   "n_dependent_implied": round(sv["frac_dependent"] * sv["n"]),
   "wilson95_1_of_5": wilson(1, 5),
   "shift_vs_sarcoma_mean": round(by["BRD9"]["sarcoma_mean"] - sv["mean_gene_effect"], 3),
   "distance_of_subtype_mean_from_cut": round(sv["mean_gene_effect"] - d["dependent_threshold"], 3)},
 "exact_fisher_power": {
   "n1=5,p1=0.8,vs n2=91,p0=0.022": round(power(5, 0.8, 91, 0.022), 4),
   "n1=5,p1=0.6,vs n2=91,p0=0.022": round(power(5, 0.6, 91, 0.022), 4),
   "min_n_for_80pct_power_at_p1=0.8": min(n for n in range(1, 8) if power(n, 0.8, 91, 0.022) >= 0.80)},
 "observed_fisher_p_for_brd9_synovial": {
   "vs_sarcoma_background_1of5_vs_2of91": round(fisher_p(1, 4, 2, 89), 4),
   "vs_rest_background_at_smallest_consistent_n": round(fisher_p(1, 4, round(0.017 * rest_denoms[0]), rest_denoms[0] - round(0.017 * rest_denoms[0])), 4),
   "vs_rest_background_at_largest_consistent_n": round(fisher_p(1, 4, round(0.017 * rest_denoms[-1]), rest_denoms[-1] - round(0.017 * rest_denoms[-1])), 4),
   "_comment": "PUB-BIOMARKER-DEP reported 0.084. It reproduces only against the REST arm and only "
               "under an unrecorded assumption about that arm's n; across every denominator the "
               "artifact permits it spans the range above. Against the SARCOMA background it is 0.1497."},
 "dispersion_fields_present_in_gene_records": sorted({k for _, r in recs for k in r}),
}
json.dump(out, open(os.path.join(HERE, "prior-number-rederivation.json"), "w"), indent=2)
print(json.dumps(out, indent=2))
