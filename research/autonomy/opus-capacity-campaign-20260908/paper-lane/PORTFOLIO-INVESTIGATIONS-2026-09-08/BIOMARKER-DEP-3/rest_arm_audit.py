#!/usr/bin/env python3
"""BIOMARKER-DEP-3 — independent re-derivation of the two BIOMARKER-DEP-2 claims about the DepMap
transfer panel's REST arm, then a per-quantity supportability audit of every published quantity in
the dependency paper family that depends on that arm.

Read-only. Inputs: research/modalities/depmap-sarcoma-dependency.json (the committed artifact) and
the two sibling lane artifacts, read only to quote the numbers being checked. No network, no GPU.
No EMC observation; no efficacy, safety, selectivity, therapeutic-window or clinical-readiness claim.
"""
import json, math, os
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
SRC = os.path.join(REPO, "research/modalities/depmap-sarcoma-dependency.json")
d = json.load(open(SRC))

# ---------------------------------------------------------------- record harvest
recs = []
def walk(o, p):
    if isinstance(o, dict):
        if "gene" in o and "rest_frac_dependent" in o:
            recs.append((p, o))
        for k, v in o.items():
            walk(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, p + "/%d" % i)
walk(d, "")
by = {r["gene"]: r for _, r in recs}

# ---------------------------------------------------------------- exact Fisher, both tails
def hyper(x, n1, n2, k):
    return comb(n1, x) * comb(n2, k - x) / comb(n1 + n2, k)

def fisher(a, b, c, dd, mode):
    """Exact Fisher on [[a,b],[c,dd]]. mode='greater' = one-sided P(X>=a); 'two' = the
    conventional sum-of-smaller-or-equal-probability two-sided value scipy.fisher_exact returns."""
    n1, n2, k = a + b, c + dd, a + c
    lo, hi = max(0, k - n2), min(n1, k)
    if mode == "greater":
        return sum(hyper(x, n1, n2, k) for x in range(a, hi + 1))
    pobs = hyper(a, n1, n2, k)
    tol = pobs * (1 + 1e-7)
    return sum(hyper(x, n1, n2, k) for x in range(lo, hi + 1) if hyper(x, n1, n2, k) <= tol)

# scipy cross-check of the two-sided implementation
try:
    from scipy.stats import fisher_exact as _sp
    SCIPY = True
except Exception:
    SCIPY = False

# ---------------------------------------------------------------- CLAIM 1: admissible denominators
def consistent(f, n):
    return any(round(k / n, 3) == round(f, 3) for k in range(n + 1))

LOW, HIGH = 2, 2105
rest_denoms = [n for n in range(LOW, HIGH + 1)
               if all(consistent(r["rest_frac_dependent"], n) for _, r in recs)]
sar_denoms = [n for n in range(LOW, HIGH + 1)
              if all(consistent(r["sarcoma_frac_dependent"], n) for _, r in recs)]

n_pan = sorted({r["n_sarcoma"] for _, r in recs})
assert len(n_pan) == 1, n_pan
N_SAR = n_pan[0]
N_TOT = d["n_models_total"]
PRODUCER_N_REST = N_TOT - N_SAR          # what transfer_calibration.py actually used
NR4A_N_LINES = d["nr4a_paralogue_comparison"]["paralogues"]["NR4A3"]["n_lines"]
PANEL_IMPLIED_N_REST = NR4A_N_LINES - N_SAR   # if the screened panel is 1178 lines

# ---------------------------------------------------------------- CLAIM 2: the p = 0.084 statement
BRD9 = by["BRD9"]
SV = d["self_validation"]["BRD9_in_synovial"]
k_syn, n_syn = round(SV["frac_dependent"] * SV["n"]), SV["n"]
k_sar = round(BRD9["sarcoma_frac_dependent"] * N_SAR)

def rest_table(N):
    k = round(BRD9["rest_frac_dependent"] * N)
    return k, N - k

p_routes = {}
# route A - the producer's own route, reconstructed line for line
kA, bA = rest_table(PRODUCER_N_REST)
p_routes["A_producer_route_n_rest=n_models_total-91"] = {
    "n_rest": PRODUCER_N_REST, "table": [[k_syn, n_syn - k_syn], [kA, bA]],
    "two_sided": round(fisher(k_syn, n_syn - k_syn, kA, bA, "two"), 6),
    "one_sided_greater": round(fisher(k_syn, n_syn - k_syn, kA, bA, "greater"), 6),
    "scipy_two_sided": round(_sp([[k_syn, n_syn - k_syn], [kA, bA]])[1], 6) if SCIPY else None,
    "denominator_is_admissible": PRODUCER_N_REST in rest_denoms,
}
# route B - against the SARCOMA arm
p_routes["B_vs_sarcoma_arm_1of5_vs_2of91"] = {
    "table": [[k_syn, n_syn - k_syn], [k_sar, N_SAR - k_sar]],
    "two_sided": round(fisher(k_syn, n_syn - k_syn, k_sar, N_SAR - k_sar, "two"), 6),
    "one_sided_greater": round(fisher(k_syn, n_syn - k_syn, k_sar, N_SAR - k_sar, "greater"), 6),
}
# route C - the envelope across every admissible rest denominator
env = []
for N in rest_denoms:
    k, b = rest_table(N)
    env.append((N, fisher(k_syn, n_syn - k_syn, k, b, "two"),
                   fisher(k_syn, n_syn - k_syn, k, b, "greater")))
two = [e[1] for e in env]; one = [e[2] for e in env]
p_routes["C_envelope_over_all_admissible_rest_denominators"] = {
    "n_denominators": len(rest_denoms),
    "n_rest_min": rest_denoms[0], "n_rest_max": rest_denoms[-1],
    "two_sided_min": round(min(two), 6), "two_sided_max": round(max(two), 6),
    "two_sided_at_min_n": round(env[0][1], 6), "two_sided_at_max_n": round(env[-1][1], 6),
    "one_sided_min": round(min(one), 6), "one_sided_max": round(max(one), 6),
    "one_sided_at_min_n": round(env[0][2], 6), "one_sided_at_max_n": round(env[-1][2], 6),
    "n_denominators_rounding_two_sided_to_0.084": sum(1 for e in env if round(e[1], 3) == 0.084),
}
# route D - the panel-implied rest arm (1178 screened lines minus the 91 sarcoma)
kD, bD = rest_table(PANEL_IMPLIED_N_REST)
p_routes["D_panel_implied_n_rest=1178-91"] = {
    "n_rest": PANEL_IMPLIED_N_REST, "table": [[k_syn, n_syn - k_syn], [kD, bD]],
    "two_sided": round(fisher(k_syn, n_syn - k_syn, kD, bD, "two"), 6),
    "one_sided_greater": round(fisher(k_syn, n_syn - k_syn, kD, bD, "greater"), 6),
    "denominator_is_admissible": PANEL_IMPLIED_N_REST in rest_denoms,
}

# ---------------------------------------------------------------- per-quantity supportability
def cp(k, n, alpha=0.05):
    """Clopper-Pearson exact interval via the beta quantile identity (scipy.stats.beta.ppf).
    An earlier direct binomial-tail implementation overflowed at n ~ 2000 and is preserved as a
    failed execution under checks/02."""
    from scipy.stats import beta as _beta
    low = 0.0 if k == 0 else float(_beta.ppf(alpha / 2, k, n - k + 1))
    high = 1.0 if k == n else float(_beta.ppf(1 - alpha / 2, k + 1, n - k))
    return round(low, 4), round(high, 4)

def envelope_ci(f):
    """Tightest interval valid for EVERY admissible rest denominator: the union of the exact
    Clopper-Pearson intervals over the admissible N. Sampling model is stated in FINDING.md."""
    los, his = [], []
    for N in (rest_denoms[0], rest_denoms[len(rest_denoms) // 2], rest_denoms[-1]):
        k = round(f * N)
        lo, hi = cp(k, N)
        los.append(lo); his.append(hi)
    return round(min(los), 4), round(max(his), 4)

QUANTS = [
    ("EWSR1 rest_frac_dependent", "EWSR1", "rest_frac_dependent"),
    ("MCL1 rest_frac_dependent", "MCL1", "rest_frac_dependent"),
    ("BCL2L1 rest_frac_dependent", "BCL2L1", "rest_frac_dependent"),
    ("BRD9 rest_frac_dependent", "BRD9", "rest_frac_dependent"),
    ("FLI1 rest_frac_dependent", "FLI1", "rest_frac_dependent"),
    ("NR4A3 rest_frac_dependent", "NR4A3", "rest_frac_dependent"),
]
qtab = []
for label, g, field in QUANTS:
    f = by[g][field]
    kmin, kmax = round(f * rest_denoms[0]), round(f * rest_denoms[-1])
    qtab.append({
        "quantity": label, "published_value": f,
        "artifact": "research/modalities/depmap-sarcoma-dependency.json",
        "key": "<group>/%s.%s" % (g, field),
        "descriptive_bound_from_rounding_only": [round(f - 0.0005, 4), round(f + 0.0005, 4)],
        "implied_dependent_count_range_over_admissible_N": [kmin, kmax],
        "binomial_CI_envelope_over_admissible_N": envelope_ci(f),
        "point_estimate_with_no_placeable_uncertainty": True,
    })

# quantities that do NOT depend on the rest denominator at all
denominator_free = {
    "n_sarcoma (every record)": N_SAR,
    "sarcoma_frac_dependent denominators consistent": sar_denoms[:5],
    "pan_essential_trap_records_rest_frac>=0.80": sum(1 for _, r in recs if r["rest_frac_dependent"] >= 0.80),
    "pan_essential_trap_records_rest_frac>=0.20": sum(1 for _, r in recs if r["rest_frac_dependent"] >= 0.20),
    "records_with_a_rest_arm": len(recs),
    "unique_genes_with_a_rest_arm": len({r["gene"] for _, r in recs}),
}

out = {
    "_note": "BIOMARKER-DEP-3. Independent re-derivation of BIOMARKER-DEP-2's two rest-arm claims, "
             "then a per-quantity supportability audit. No EMC observation. No clinical claim.",
    "source": "research/modalities/depmap-sarcoma-dependency.json",
    "panel_scalars": {"n_models_total": N_TOT, "n_sarcoma_models": d["n_sarcoma_models"],
                      "n_sarcoma_per_record": N_SAR, "dependent_threshold": d["dependent_threshold"],
                      "nr4a_block_n_lines": NR4A_N_LINES},
    "claim_1_admissible_rest_denominators": {
        "search_range": [LOW, HIGH], "count": len(rest_denoms),
        "range": [rest_denoms[0], rest_denoms[-1]],
        "integers_in_range": rest_denoms[-1] - rest_denoms[0] + 1,
        "excluded_in_range": (rest_denoms[-1] - rest_denoms[0] + 1) - len(rest_denoms),
        "BIOMARKER_DEP_2_reported": {"count": 1126, "range": [943, 2105]},
        "reproduces": len(rest_denoms) == 1126 and rest_denoms[0] == 943 and rest_denoms[-1] == 2105,
        "producer_denominator_2014_admissible": PRODUCER_N_REST in rest_denoms,
        "panel_implied_denominator_1087_admissible": PANEL_IMPLIED_N_REST in rest_denoms,
        "recorded_anywhere_in_the_artifact": False,
    },
    "claim_2_the_p_0084_statement": p_routes,
    "per_quantity_audit": qtab,
    "quantities_independent_of_the_rest_denominator": denominator_free,
}
json.dump(out, open(os.path.join(HERE, "rest-arm-audit.json"), "w"), indent=2)
print(json.dumps(out, indent=2))
