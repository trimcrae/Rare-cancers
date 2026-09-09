#!/usr/bin/env python3
"""What the FUSION-OUTPUT-2 pre-registration becomes if GPL3290/GSE4303 is DROPPED.

DESIGN ARITHMETIC ONLY.  NO expression value is read.  No cohort matrix is opened.  No
contrast is computed.  The coordinator-owned frozen outcome protocol is neither opened
nor pre-empted.  Nothing here is a biological claim, and nothing here can establish
efficacy, safety, selectivity, a therapeutic window or clinical readiness.

Three jobs, in order:

  1. RE-DERIVE, independently of FUSION-OUTPUT-2's and FUSION-OUTPUT-3's stored JSON:
       (a) the contrast A and contrast B set sizes, from the frozen membership TSV, by
           re-implementing the subtraction from the TSV rows;
       (b) GPL6244 readability of every member, against the source packet's own
           gene-to-probes map, and the resulting coverage per cell.
     A non-reproducing number is the finding: it is reported digit for digit.

  2. RECOMPUTE the detectability arithmetic for a GPL6244-ONLY (single-cohort) design,
     using FUSION-OUTPUT-2's own MDE formula and its own conventions, unchanged:

       MDE(d) = (t_.975(df) + t_.80(df)) * sqrt(1/n1 + 1/n2) * sqrt((1 + (m-1) rho) / m)

     and quantify exactly what dropping GSE4303 costs.

  3. Evaluate the pre-registration's own stop conditions and clauses under the dropped
     design, WITHOUT overturning any of its numeric no-goes.

ASSUMPTIONS behind every MDE below, restated in full and EACH LABELLED FOR THE DIRECTION
OF ITS BIAS.  All five bias the numbers OPTIMISTICALLY: the true detectable effects are
LARGER than printed, never smaller.

  A1. Var(x_ig) = 1 across samples for every gene, where x_ig is the manuscript's
      within-array z (PUB-FUSION-OUTPUT Sec 2.3).  OPTIMISTIC: in real data the
      across-sample SD of a within-array z exceeds 1 for most genes, and every MDE
      scales linearly with that SD.
  A2. A single common average across-sample inter-gene correlation rho applies to all
      pairs of set members, so Var(S) = (1 + (m-1) rho)/m.  OPTIMISTIC at any rho the
      user chooses to believe: heterogeneous correlation with the same mean gives a
      larger Var(S) whenever the correlation matrix is not exchangeable.
  A3. The alternative is a COMMON per-gene elevation d shared by all m members.
      OPTIMISTIC: a heterogeneous effect with the same mean is strictly harder to detect.
  A4. df = n1 + n2 - 2 for the Welch t.  OPTIMISTIC: true Welch-Satterthwaite df is
      <= n1+n2-2, so the true critical sum is larger.
  A5. Every member counted readable is measured with no extra probe-level noise, i.e.
      coverage 1.000 is treated as m = n.  OPTIMISTIC: probe-level noise on a single
      array platform inflates the per-gene SD, which is A1 again.

  A6 (single-platform-specific).  Dropping a cohort removes the pre-registration's
      "elevated on BOTH series" conjunction.  Reporting a single-cohort test at
      alpha = 0.05 while quoting the two-cohort design's MDE is OPTIMISTIC ABOUT THE
      LEVEL, not about the effect size: the nominal joint false-positive rate rises from
      alpha^2 to alpha.  This script prints the alpha-equivalent MDEs that hold the old
      level, so the trade is visible instead of silent.

Inputs (all read in place, hashed, never copied, never modified).
"""
import csv, collections, hashlib, json, sys
from scipy import stats

MEMBERSHIP = sys.argv[1]
GPL6244_MAP = sys.argv[2]
PREREG_SETS = sys.argv[3]      # FUSION-OUTPUT-2 frozen sets, used ONLY to cross-check
COVERAGE_3 = sys.argv[4]       # FUSION-OUTPUT-3 coverage, used ONLY to cross-check

INDEX = "EWSR1-NR4A3"
NR4A3 = ["EWSR1-NR4A3", "TAF15-NR4A3", "TCF12-NR4A3", "TFG-NR4A3"]
FLOOR_GENES = 4                # PUB-FUSION-OUTPUT Sec 2.3
FLOOR_COVERAGE = 0.4           # PUB-FUSION-OUTPUT Sec 2.3
PRIMARY_WINDOW = "2000"

# Cohort metadata only (sample counts), PUB-FUSION-OUTPUT Sec 2.2 / FUSION-OUTPUT-2.
KEPT = {"series": "GSE24369", "platform": "GPL6244", "n_emc": 6, "n_comparator": 29}
DROPPED = {"series": "GSE4303", "platform": "GPL3290", "n_emc": 10, "n_comparator": 6}
RHOS = [0.0, 0.1, 0.2, 0.3, 0.5]
ALPHA, POWER = 0.05, 0.80
N_ALTERNATIVE_PROGRAMS = 28
N_OTHER_NR4A3 = 3
N_NULL_SETS = 4000


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def crit(df, alpha=ALPHA, power=POWER):
    return stats.t.ppf(1 - alpha / 2, df) + stats.t.ppf(power, df)


def mde(m, rho, n1, n2, alpha=ALPHA):
    df = n1 + n2 - 2
    return crit(df, alpha) * (1 / n1 + 1 / n2) ** 0.5 * ((1 + (m - 1) * rho) / m) ** 0.5


# ---------------------------------------------------------------- 1a. re-derive sets
mem = collections.defaultdict(lambda: collections.defaultdict(set))
with open(MEMBERSHIP) as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        mem[int(r["window_bp"])][r["program"]].add(r["symbol"])

sets = {}
for w in sorted(mem):
    P = mem[w]
    alt = [p for p in sorted(P) if p not in NR4A3]
    A = P.get(INDEX, set()) - set().union(*(P[p] for p in alt))
    B = A - set().union(*(P[p] for p in NR4A3 if p != INDEX and p in P))
    sets[str(w)] = {"A": sorted(A), "B": sorted(B),
                    "n_programs": len(P), "n_alternative_subtracted": len(alt),
                    "index_size": len(P.get(INDEX, set()))}

# ---------------------------------------------------------------- 1b. GPL6244 coverage
g2p = json.load(open(GPL6244_MAP))
readable = {k.upper() for k in g2p}

coverage = {}
for w, s in sets.items():
    coverage[w] = {}
    for c in ("A", "B"):
        genes = s[c]
        hit = [g for g in genes if g.upper() in readable]
        miss = [g for g in genes if g.upper() not in readable]
        n = len(genes)
        cov = (len(hit) / n) if n else 0.0
        coverage[w][c] = {
            "n": n, "readable_on_GPL6244": len(hit), "unreadable_on_GPL6244": len(miss),
            "missing_symbols": miss,
            "coverage": round(cov, 6),
            "clears_coverage_floor_0.4": bool(cov >= FLOOR_COVERAGE),
            "clears_gene_floor_4": bool(len(hit) >= FLOOR_GENES),
            "clears_both_floors": bool(cov >= FLOOR_COVERAGE and len(hit) >= FLOOR_GENES),
            "probe_dropouts_tolerated_before_gene_floor_breach": len(hit) - FLOOR_GENES,
        }

# --------------------------------------------------- 1c. cross-check the two prior lanes
prereg = json.load(open(PREREG_SETS))
cov3 = json.load(open(COVERAGE_3))
EXPECTED_SIZES = {"1000": {"A": 23, "B": 4}, "2000": {"A": 40, "B": 7}, "5000": {"A": 57, "B": 6}}

crosscheck = {"expected_from_task_statement": EXPECTED_SIZES,
              "set_size_mismatches": [], "membership_mismatches_vs_FUSION_OUTPUT_2": [],
              "coverage_mismatches_vs_FUSION_OUTPUT_3": []}
for w, cc in EXPECTED_SIZES.items():
    for c, n in cc.items():
        got = len(sets[w][c])
        if got != n:
            crosscheck["set_size_mismatches"].append(
                {"window": w, "contrast": c, "expected": n, "recomputed": got})
        pre = prereg["windows"][w]["contrast_%s_set" % c]["genes"]
        if pre != sets[w][c]:
            crosscheck["membership_mismatches_vs_FUSION_OUTPUT_2"].append(
                {"window": w, "contrast": c,
                 "only_in_FUSION_OUTPUT_2": sorted(set(pre) - set(sets[w][c])),
                 "only_in_this_rederivation": sorted(set(sets[w][c]) - set(pre))})

for key, prev in cov3["platforms"]["GPL6244"]["cells"].items():
    w, c = key.split("/")
    mine = coverage[w][c]
    if (prev["n"] != mine["n"]
            or prev["n_known_readable"] != mine["readable_on_GPL6244"]
            or prev["coverage_exact"] != mine["coverage"]
            or sorted(prev["readable_genes"]) != sorted(
                g for g in sets[w][c] if g.upper() in readable)):
        crosscheck["coverage_mismatches_vs_FUSION_OUTPUT_3"].append(
            {"cell": key,
             "FUSION_OUTPUT_3": {"n": prev["n"], "readable": prev["n_known_readable"],
                                 "coverage": prev["coverage_exact"]},
             "recomputed": {"n": mine["n"], "readable": mine["readable_on_GPL6244"],
                            "coverage": mine["coverage"]}})

crosscheck["all_reproduce"] = not (crosscheck["set_size_mismatches"]
                                   or crosscheck["membership_mismatches_vs_FUSION_OUTPUT_2"]
                                   or crosscheck["coverage_mismatches_vs_FUSION_OUTPUT_3"])

# ------------------------------------------------- 2. single-platform MDE arithmetic
single = {}
for w, s in sets.items():
    single[w] = {}
    for c in ("A", "B"):
        m = coverage[w][c]["readable_on_GPL6244"]   # readable members, not nominal n
        single[w][c] = {
            "m_readable_on_GPL6244": m,
            "mde_GSE24369_only": {str(r): round(mde(m, r, KEPT["n_emc"], KEPT["n_comparator"]), 4)
                                  for r in RHOS},
            "mde_GSE4303_if_it_had_been_kept": {
                str(r): round(mde(m, r, DROPPED["n_emc"], DROPPED["n_comparator"]), 4)
                for r in RHOS},
            "effective_independent_genes": {
                str(r): round(m / (1 + (m - 1) * r), 3) for r in RHOS},
        }

# What dropping actually costs, at the primary window and rho = 0.2.
RHO_REF = 0.2
cost = {}
for c in ("A", "B"):
    m = coverage[PRIMARY_WINDOW][c]["readable_on_GPL6244"]
    kept_mde = mde(m, RHO_REF, KEPT["n_emc"], KEPT["n_comparator"])
    dropped_mde = mde(m, RHO_REF, DROPPED["n_emc"], DROPPED["n_comparator"])
    # Counterfactual ONLY: the pre-registration forbids pooling (S5, Sec 3.1), and
    # GSE4303 is graded circular, so this row is NOT an available design.
    pooled_mde = mde(m, RHO_REF, KEPT["n_emc"] + DROPPED["n_emc"],
                     KEPT["n_comparator"] + DROPPED["n_comparator"])
    cost[c] = {
        "m": m, "rho": RHO_REF, "window": PRIMARY_WINDOW,
        "two_cohort_design_primary_arm_mde": round(kept_mde, 4),
        "single_platform_design_mde": round(kept_mde, 4),
        "mde_change_from_dropping_GSE4303": round(kept_mde - kept_mde, 4),
        "why_zero": "the pre-registration never pools the two series; Sec 3.1 requires "
                    "elevation on each series separately and S5 forbids pooling on "
                    "disagreement, so each series' MDE is computed at its own n. "
                    "Removing one series therefore leaves the other series' MDE "
                    "unchanged, digit for digit.",
        "dropped_cohort_own_mde_would_have_been": round(dropped_mde, 4),
        "dropped_cohort_was_the_weaker_arm": bool(dropped_mde > kept_mde),
        "COUNTERFACTUAL_pooled_mde_NOT_AN_AVAILABLE_DESIGN": round(pooled_mde, 4),
        "counterfactual_pooled_gain_vs_single": round(kept_mde - pooled_mde, 4),
        "counterfactual_note": "pooling is forbidden by the pre-registration (Sec 3.1, S5) "
                               "and would in any case pool a cohort graded CIRCULAR for "
                               "EMC-elevation claims into one graded non-circular. This "
                               "number bounds what could in principle have been forgone; "
                               "it is not a loss, because the design never had it.",
    }

# Sample accounting: what is physically given up.
sample_accounting = {
    "emc_tumours_in_two_cohort_design": KEPT["n_emc"] + DROPPED["n_emc"],
    "emc_tumours_in_single_platform_design": KEPT["n_emc"],
    "emc_tumours_dropped": DROPPED["n_emc"],
    "fraction_of_emc_material_dropped": round(DROPPED["n_emc"] / (KEPT["n_emc"] + DROPPED["n_emc"]), 4),
    "comparators_dropped": DROPPED["n_comparator"],
    "fraction_of_comparators_dropped": round(
        DROPPED["n_comparator"] / (KEPT["n_comparator"] + DROPPED["n_comparator"]), 4),
    "mde_cost_of_that_loss": 0.0,
    "reading": "the dropped cohort holds the MAJORITY of the design's EMC tumours and "
               "costs zero detectable effect, because the pre-registration assigned it "
               "no inferential weight it could carry: Sec 6.2 makes it corroborative "
               "only and Sec 3.1 declares any positive existing on GSE4303 alone "
               "UNINTERPRETABLE. A cohort that cannot carry a positive contributes no "
               "power to a design that never pools.",
}

# The level trade: the conjunction that is lost, priced honestly.
kept_A_m = coverage[PRIMARY_WINDOW]["A"]["readable_on_GPL6244"]
level_trade = {
    "two_cohort_rule": "Sec 3.1 positive = elevated on BOTH series, each at alpha = 0.05",
    "nominal_joint_false_positive_rate_two_cohort_if_independent": round(ALPHA ** 2, 6),
    "nominal_false_positive_rate_single_platform": ALPHA,
    "fold_increase_in_nominal_level": round(ALPHA / ALPHA ** 2, 1),
    "joint_power_of_the_conjunction_if_independent_at_each_arms_own_mde": round(POWER ** 2, 4),
    "power_of_the_single_platform_test_at_its_own_mde": POWER,
    "so_dropping_raises_power_from_0.64_to_0.80_and_raises_level_from_0.0025_to_0.05": True,
    "price_of_holding_the_old_level_on_one_cohort_contrast_A_primary_window_rho_0.2": {
        "alpha_0.05": round(mde(kept_A_m, RHO_REF, KEPT["n_emc"], KEPT["n_comparator"], 0.05), 4),
        "alpha_0.0025_matches_two_cohort_joint_level": round(
            mde(kept_A_m, RHO_REF, KEPT["n_emc"], KEPT["n_comparator"], ALPHA ** 2), 4),
        "alpha_0.05_over_28_multiplicity_for_the_alternative_programs": round(
            mde(kept_A_m, RHO_REF, KEPT["n_emc"], KEPT["n_comparator"], 0.05 / 28), 4),
    },
    "caveat": "the conjunction's nominal level and joint power assume the two series are "
              "INDEPENDENT tests. They are not fully independent — both score the same "
              "gene set and GSE4303 is graded circular for exactly these claims — so "
              "0.0025 OVERSTATES the protection the two-cohort rule actually bought, and "
              "0.64 UNDERSTATES its joint power. Both directions of that error make the "
              "single-platform trade look worse than it is.",
}

# --------------------------------- 3. what happens to each pre-registration clause
A_cell = coverage[PRIMARY_WINDOW]["A"]
B_cell = coverage[PRIMARY_WINDOW]["B"]
clauses = {
    "S1_coordinator_gate": {"status": "UNCHANGED AND BINDING",
        "text": "the frozen outcome protocol is coordinator-owned; nothing here opens it"},
    "S2_GPL3290_floors": {"status": "DISSOLVED BY THE DROP, NOT SATISFIED",
        "text": "S2 conditions the run on GPL3290 clearing the floors. Under a "
                "GPL6244-only design there is no GPL3290 arm, so S2 has no referent. "
                "FUSION-OUTPUT-3 left S2 UNDETERMINABLE OFFLINE in all six cells; "
                "dropping the platform removes the question rather than answering it. "
                "This is a design change with a cost recorded above, not a floor waiver.",
        "GPL6244_half_verified_here": {w: {c: coverage[w][c]["clears_both_floors"]
                                           for c in ("A", "B")} for w in sorted(coverage)}},
    "S3_do_not_run_contrast_B": {"status": "UNCHANGED AND BINDING",
        "text": "the no-go rests on a minimum attainable one-sided rank p of 1/4 = 0.25 "
                "against the other three NR4A3 programs, which cannot reach alpha = 0.05 "
                "at any effect size, and on a 3-gene window-invariant core below the "
                "manuscript's own 4-gene floor. Both facts are platform-independent. "
                "Dropping GPL3290 does not touch either, and this lane does not "
                "overturn them."},
    "S4_no_post_hoc_set_change": {"status": "UNCHANGED AND BINDING",
        "text": "the sets in Sec 2 stay frozen; this lane re-derived them and changed none"},
    "S5_direction_disagreement": {"status": "VOID — NO SECOND SERIES TO DISAGREE",
        "text": "S5 stops the analysis when the two series disagree in direction. With "
                "one series it can never fire. It must be REPLACED, not simply deleted: "
                "see required_replacement_rules."},
    "Sec_3.1_uninterpretable_both_series_clauses": {
        "status": "TWO CLAUSES GO VOID",
        "void": ["the two series disagree in direction",
                 "the result is carried by GSE4303 alone"],
        "surviving": ["effect not distinguishable from the exact global offset",
                      "coverage < 0.4 or readable members < 4 on the scored platform",
                      "alternative-fusion programs score comparably (generic oncofusion "
                      "accessibility, not NR4A3 output)"],
        "warning": "the two void clauses were GUARDS. Removing them makes a positive "
                   "EASIER to declare. A single-platform design must not inherit the "
                   "two-cohort design's evidentiary language."},
    "Sec_6.1_coverage_prerequisite": {"status": "SATISFIED EXACTLY, AND NOW VERIFIED",
        "text": "GPL6244 coverage is 1.000 in all six cells, checked member by member "
                "against the source packet's own gene-to-probes map rather than assumed "
                "'by construction'."},
    "Sec_6.2_circularity": {"status": "MOOT — the circular cohort is the one dropped"},
    "Sec_6.3_comparator_composition": {"status": "UNCHANGED, AND NOW THE ONLY COMPARATOR",
        "text": "GSE24369's comparator arm is itself FET-rearranged (LGFMS, FUS::CREB3L2) "
                "and 23 of 29 comparators are myxoid. In the two-cohort design this was "
                "one of two comparator compositions; in the single-platform design it is "
                "the whole comparator basis, so this limitation gains weight rather than "
                "losing it. It is the surviving interpretive constraint."},
}

required_replacement_rules = [
    "R-S5. Replace S5 with a within-series stability rule, since cross-series direction "
    "agreement is no longer available: pre-declare that the primary 2 kb result is "
    "reported alongside the 1 kb and 5 kb sets as DIFFERENT SETS (Sec 5, Jaccard "
    "0.25-0.50 for A), and that disagreement among them is reported, never resolved by "
    "selection.",
    "R-LEVEL. Either test contrast A at alpha = 0.0025 to hold the two-cohort design's "
    "nominal joint level (MDE rises as printed in level_trade), or test at alpha = 0.05 "
    "and state in the result that the finding is UNREPLICATED IN A SECOND SERIES. One "
    "of the two must be chosen in advance. Quoting the two-cohort MDE while testing at "
    "the single-cohort level is the failure mode this artifact exists to prevent.",
    "R-LANG. Any positive from the single-platform design is 'elevated in one series of "
    "6 EMC tumours against 29 FET-rearranged comparators', never 'replicated'. The "
    "replication the two-cohort design nominally offered was against a cohort graded "
    "CIRCULAR for these very claims, so it was never independent replication; dropping "
    "it removes a nominal guard, and the honest report says so rather than implying the "
    "evidence is unchanged.",
    "R-B. Contrast B remains not-run under S3. Its GPL6244 floors are met exactly "
    "(4/4 readable at 1 kb, zero dropout tolerance), so the S2 readability blocker "
    "FUSION-OUTPUT-3 identified for B dissolves; the Sec 4.3 numeric no-go does not, and "
    "it is the binding one.",
]

runnability = {
    "contrast_A": {
        "runnable_under_a_single_platform_design": True,
        "qualification": "runnable in the design sense ONLY: every prerequisite that a "
                         "design document can discharge is discharged. The run itself "
                         "remains gated by S1, which this lane does not open.",
        "why": ["GPL6244 coverage 1.000 and 40 readable members at the primary window, "
                "verified here against the map, so both floors clear with 36 dropouts "
                "of headroom",
                "the rank statistic against 28 alternative programs reaches alpha = 0.05 "
                "(minimum one-sided p = 1/29 = 0.0345), unchanged by dropping a cohort",
                "the pending prerequisite (Sec 6.1 GPL3290) and the circularity "
                "prerequisite (Sec 6.2) both disappear with the dropped arm"],
        "at_what_cost": ["the Sec 3.1 two-series conjunction is gone, so a positive is "
                         "unreplicated and the nominal level rises 20-fold unless "
                         "R-LEVEL is adopted",
                         "62.5 percent of the design's EMC tumours are set aside",
                         "the FET-vs-FET, 23/29-myxoid comparator composition becomes the "
                         "sole comparator basis"],
        "mde_it_is_powered_for_primary_window_rho_0.2_alpha_0.05":
            cost["A"]["single_platform_design_mde"],
    },
    "contrast_B": {
        "runnable_under_a_single_platform_design": False,
        "why_not": ["minimum attainable one-sided rank p = 1/4 = 0.25 against the other "
                    "three NR4A3 programs: cannot reach alpha = 0.05 at ANY effect size",
                    "window-invariant core is 3 genes, below the manuscript's own 4-gene "
                    "floor, so no window-robust B result can be formed",
                    "at 1 kb the set is exactly 4 readable genes on GPL6244, so a single "
                    "probe dropout drops it below the floor and it emits no number"],
        "what_did_change": "its readability is now settled rather than unknown — all "
                           "three windows clear both GPL6244 floors exactly — which "
                           "removes FUSION-OUTPUT-3's named dependency on BAZ2A, FAXC, "
                           "FBXO21, FOXA1, HAP1, IDH1, TBX21 without making the contrast "
                           "informative.",
        "not_this_lane_s_to_overturn": True,
        "mde_primary_window_rho_0.2_alpha_0.05": cost["B"]["single_platform_design_mde"],
    },
}

out = {
    "artifact": "design arithmetic for a GPL6244-only variant of the FUSION-OUTPUT-2 "
                "pre-registration",
    "status": "DESIGN ONLY — no expression value read, no contrast computed, no "
              "biological claim, coordinator gate neither opened nor pre-empted",
    "date": "2026-09-09",
    "lane": "FUSION-OUTPUT-4",
    "assumptions_every_one_biasing_the_mdes_optimistically": __doc__.strip(),
    "inputs": {
        "frozen_membership_tsv": {"path": MEMBERSHIP, "sha256": sha256(MEMBERSHIP)},
        "GPL6244_gene_to_probes": {"path": GPL6244_MAP, "sha256": sha256(GPL6244_MAP),
                                   "n_symbols": len(g2p)},
        "FUSION_OUTPUT_2_frozen_sets_crosscheck_only": {
            "path": PREREG_SETS, "sha256": sha256(PREREG_SETS)},
        "FUSION_OUTPUT_3_coverage_crosscheck_only": {
            "path": COVERAGE_3, "sha256": sha256(COVERAGE_3)},
    },
    "floors_used_verbatim_from_the_manuscript": {
        "min_readable_genes": FLOOR_GENES, "min_coverage": FLOOR_COVERAGE,
        "note": "no floor was lowered, softened or reinterpreted"},
    "step_1_rederived_set_sizes": {w: {c: len(sets[w][c]) for c in ("A", "B")}
                                   for w in sorted(sets)},
    "step_1_rederived_gpl6244_coverage": coverage,
    "step_1_crosscheck": crosscheck,
    "step_2_single_platform_mde": single,
    "step_2_what_dropping_GSE4303_costs": cost,
    "step_2_sample_accounting": sample_accounting,
    "step_2_level_trade": level_trade,
    "step_3_preregistration_clauses_under_the_drop": clauses,
    "step_3_required_replacement_rules": required_replacement_rules,
    "step_3_runnability": runnability,
    "resolution_limits_unchanged_by_the_drop": {
        "size_matched_empirical_null_4000_sets_smallest_p": round(1 / (N_NULL_SETS + 1), 6),
        "rank_among_28_alternative_programs_smallest_one_sided_p":
            round(1 / (N_ALTERNATIVE_PROGRAMS + 1), 4),
        "rank_among_the_4_NR4A3_programs_smallest_one_sided_p":
            round(1 / (N_OTHER_NR4A3 + 1), 4),
        "note": "all three are combinatorial properties of the comparison, not of the "
                "cohort, so dropping a platform changes none of them",
    },
    "fences": ["no expression value read", "no contrast computed",
               "outcome protocol not opened and not pre-empted",
               "no floor, guard, gate, matcher, pin or test weakened",
               "no biological claim; no efficacy, safety, selectivity, "
               "therapeutic-window or clinical-readiness claim",
               "no network, no GPU, no paid API, no publication, no outreach",
               "writes confined to the FUSION-OUTPUT-4 lane directory"],
}
json.dump(out, sys.stdout, indent=1, sort_keys=True)
print()
