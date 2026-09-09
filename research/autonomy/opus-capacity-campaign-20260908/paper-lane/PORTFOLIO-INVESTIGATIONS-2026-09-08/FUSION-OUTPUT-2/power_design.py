#!/usr/bin/env python3
"""Pre-registered detectability arithmetic for the two NR4A3-program contrasts.

PRE-REGISTRATION ARTIFACT. Analytic power only. NO expression value is read; no cohort
matrix is opened; no contrast is computed. Every input is a declared assumption or a
count taken from a frozen membership table or from the manuscript's own methods.

Model (stated in full, and every term is an assumption, not a measurement):
  * Per sample i and gene g the manuscript scores a within-array z, x_ig (Sec 2.3).
    Assume Var(x_ig) = 1 across samples for every gene (exact only if the within-array
    z has unit across-sample variance; in real data it does not, so these MDEs are
    optimistic by whatever factor the true per-gene SD exceeds 1).
  * A set score is S_i = mean_g x_ig over the m readable members (Sec 2.3).
  * Assume a common average across-sample correlation rho between set members, so
    Var(S) = (1 + (m-1) rho) / m  and  m_eff = m / (1 + (m-1) rho).
  * Assume the alternative is a COMMON per-gene elevation d (SD units) shared by all m
    members. A heterogeneous effect over the same mean is strictly harder to detect.
  * Test: two-sided Welch t on per-sample set scores, EMC vs comparator, at 80% power,
    with the repository's own MDE convention (W17c): critical sum = t_.975(df)+t_.80(df),
    df taken as n1+n2-2 (Welch df is <= that, so this is again optimistic).

  MDE(d) = (t_.975 + t_.80) * sqrt(1/n1 + 1/n2) * sqrt((1 + (m-1) rho) / m)

Nothing here says the effect exists. It says what size of effect the design could see.
"""
import json, sys
from scipy import stats

# --- gene counts: read from the frozen pre-registered set artifact, not retyped ---
SETS = json.load(open(sys.argv[1]))
COUNTS = {w: {"A": v["contrast_A_set"]["n"], "B": v["contrast_B_set"]["n"]}
          for w, v in SETS["windows"].items()}

# --- cohorts: sample counts only (metadata), from PUB-FUSION-OUTPUT Sec 2.2 Table ---
COHORTS = [
    {"series": "GSE24369", "platform": "GPL6244", "n_emc": 6, "n_comparator": 29,
     "note": "comparator arm is itself FET-rearranged (LGFMS = FUS::CREB3L2); "
             "GPL6244 is the platform the common-platform memberships were built on"},
    {"series": "GSE4303", "platform": "GPL3290", "n_emc": 10, "n_comparator": 6,
     "note": "two-colour cDNA, EST-accession symbol bridge (14,932 symbols); "
             "graded CIRCULAR for PPARG/EMC-elevation claims (manuscript Sec 3.8)"},
]
RHOS = [0.0, 0.1, 0.2, 0.3, 0.5]
POWER, ALPHA = 0.80, 0.05
N_NULL_SETS = 4000   # manuscript's size-matched empirical null, Sec 2.3
N_ALTERNATIVE_PROGRAMS = 28
N_OTHER_NR4A3 = 3

def crit(df, alpha=ALPHA, power=POWER):
    return stats.t.ppf(1 - alpha / 2, df) + stats.t.ppf(power, df)

def mde(m, rho, n1, n2, alpha=ALPHA):
    df = n1 + n2 - 2
    return crit(df, alpha) * (1 / n1 + 1 / n2) ** 0.5 * ((1 + (m - 1) * rho) / m) ** 0.5

out = {
    "artifact": "pre-registered detectability arithmetic",
    "status": "DESIGN ONLY - no expression value read, no contrast computed",
    "assumptions": __doc__.strip(),
    "gene_counts_from": {"path": sys.argv[1], "input_sha256": SETS["input"]["sha256"]},
    "gene_counts": COUNTS,
    "alpha": ALPHA, "power": POWER,
    "normal_critical_sum_for_reference": round(stats.norm.ppf(0.975) + stats.norm.ppf(0.80), 6),
    "cohorts": COHORTS,
    "mde_per_gene_sd_units": {},
    "effective_independent_genes": {
        w: {c: {str(r): round(m / (1 + (m - 1) * r), 3) for r in RHOS}
            for c, m in COUNTS[w].items()} for w in COUNTS},
    "multiplicity_adjusted_mde_rho_0.2_primary_window": {},
    "resolution_limits_of_the_specificity_comparison": {
        "size_matched_empirical_null_4000_sets": {
            "smallest_attainable_p": round(1 / (N_NULL_SETS + 1), 6),
            "meaning": "a set can be at most this extreme against the manuscript's own null"},
        "rank_of_index_program_among_28_alternative_programs": {
            "smallest_attainable_p_one_sided": round(1 / (N_ALTERNATIVE_PROGRAMS + 1), 4),
            "can_reach_alpha_0.05": 1 / (N_ALTERNATIVE_PROGRAMS + 1) < ALPHA},
        "rank_of_EWSR1_program_among_the_4_NR4A3_programs": {
            "smallest_attainable_p_one_sided": round(1 / (N_OTHER_NR4A3 + 1), 4),
            "can_reach_alpha_0.05": 1 / (N_OTHER_NR4A3 + 1) < ALPHA,
            "meaning": "a pure rank statement inside the NR4A3 family cannot reach 0.05 "
                       "at any effect size; only a magnitude test can, and it carries the "
                       "4-7 gene count below"},
    },
    "floor_feasibility": {},
}
for w in sorted(COUNTS, key=int):
    out["mde_per_gene_sd_units"][w] = {}
    for c, m in COUNTS[w].items():
        out["mde_per_gene_sd_units"][w][c] = {
            f"{co['series']}": {str(r): round(mde(m, r, co["n_emc"], co["n_comparator"]), 4)
                                for r in RHOS} for co in COHORTS}
    out["multiplicity_adjusted_mde_rho_0.2_primary_window"][w] = {
        c: {co["series"]: {
            "alpha_0.05": round(mde(m, 0.2, co["n_emc"], co["n_comparator"], 0.05), 4),
            "alpha_0.05_over_28": round(mde(m, 0.2, co["n_emc"], co["n_comparator"], 0.05 / 28), 4),
            "alpha_0.05_over_3": round(mde(m, 0.2, co["n_emc"], co["n_comparator"], 0.05 / 3), 4),
        } for co in COHORTS} for c, m in COUNTS[w].items()}
    out["floor_feasibility"][w] = {
        c: {"n": m, "min_readable_required": 4,
            "probe_dropouts_tolerated_before_the_set_emits_no_number": m - 4,
            "coverage_if_one_gene_unreadable": round((m - 1) / m, 3),
            "coverage_floor_0.4_binding": (m - 1) / m < 0.4}
        for c, m in COUNTS[w].items()}
json.dump(out, sys.stdout, indent=1, sort_keys=True)
print()
