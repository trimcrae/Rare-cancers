#!/usr/bin/env python3
"""
LOCOREGIONAL-2 -- extend the PUB-LOCOREGIONAL counted-event ledger from k=1 to k=2.

The prior lane (PUB-LOCOREGIONAL/FINDING.md) established that the entire counted-event
evidence base for the surgery+RT vs surgery-alone local-control contrast in EMC was FIVE
local recurrences in ONE non-poolable series, because masunaga2025 printed arm sizes and a
hazard ratio but no per-arm event count. Its named next step was to obtain that split by an
ordinary permitted read of PMC12398172.

That read was performed (PubMed/PMC MCP, 2026-09-09; see
checks/01-pubmed-mcp-fulltext-PMC12398172/). The split IS directly reported -- in the
Results body text, not in Table 2. This script records the extended ledger.

NOTHING here is reconstructed from a hazard ratio, an arm size, a p-value or a curve.
Every count below is a printed integer.

Read-only over committed inputs plus the verbatim retrieved sentence. stdlib only.
No efficacy, safety, tolerability or therapeutic-window claim is made or supported.

Usage:  python3 rt_contrast_ledger_k2.py            # write the artifact
        python3 rt_contrast_ledger_k2.py --check    # re-derive and compare byte-for-byte
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
PRIOR = os.path.join(REPO, "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                           "PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-LOCOREGIONAL/"
                           "rt-local-control-contrast-ledger.json")
OUT = os.path.join(HERE, "rt-local-control-contrast-ledger-k2.json")

# Same closed form and same z as research/modalities/emc_locoregional_eligibility.py:141-149
# and as the prior lane's ledger, so the two artifacts are directly comparable.
Z = 1.959963984540054

def wilson(events, denom):
    if denom == 0:
        return None
    p = events / denom
    d = 1 + Z * Z / denom
    c = p + Z * Z / (2 * denom)
    h = Z * math.sqrt(p * (1 - p) / denom + Z * Z / (4 * denom * denom))
    return [round(100 * (c - h) / d, 1), round(100 * (c + h) / d, 1)]

def fisher_two_sided(a, b, c, d):
    """2x2 [[a,b],[c,d]]; two-sided Fisher exact by summing tables no more probable."""
    n = a + b + c + d
    r1, c1 = a + b, a + c
    def prob(x):
        return (math.comb(r1, x) * math.comb(n - r1, c1 - x)) / math.comb(n, c1)
    lo = max(0, c1 - (n - r1)); hi = min(r1, c1)
    p0 = prob(a)
    return sum(prob(x) for x in range(lo, hi + 1) if prob(x) <= p0 * (1 + 1e-9))

def fragility(ev_a, n_a, ev_b, n_b):
    """How many events must move from the higher-rate arm to non-events before the
    two-sided Fisher p crosses 0.05 (or, if p already >0.05, None). Descriptive only."""
    p = fisher_two_sided(ev_a, n_a - ev_a, ev_b, n_b - ev_b)
    if p > 0.05:
        return None
    k = 0
    a = ev_a
    while a > 0:
        a -= 1
        k += 1
        if fisher_two_sided(a, n_a - a, ev_b, n_b - ev_b) > 0.05:
            return k
    return None

def build():
    prior = json.load(open(PRIOR))

    # ---- the two series, each with PRINTED arm-level integers --------------------
    bishop = dict(
        source_id="bishop2019",
        design="US single-institution retrospective (MD Anderson, 1990-2016)",
        arm_sizes={"surgery_plus_RT": 33, "surgery_alone": 8},
        arm_events={"surgery_plus_RT": 1, "surgery_alone": 4},
        events_total_printed=5,
        median_followup_months=94,
        endpoint_as_printed="local control (10-year actuarial headline; crude relapse count in text)",
        counts_are_printed_integers=True,
        how_the_split_is_known=(
            "printed as an integer sentence: '5 patients (12%) with local relapse ... 4 of the 5 "
            "had surgery alone' -- transcribed in research/modalities/emc-radiotherapy-contradiction"
            ".json -> estimates[0].events_note / .printed_in. NOT re-verified against the paper in "
            "this lane; transcription fidelity is inherited."),
        registry_pool_flag=False,
        registry_context_reason=("population-overlap (US single institution; likely within SEER / "
                                 "US Sarcoma Collaborative)"),
    )
    masunaga = dict(
        source_id="masunaga2025",
        design="Japanese National Bone and Soft Tissue Tumor Registry, 2002-2022",
        arm_sizes={"neoadjuvant_or_adjuvant_RT": 24, "no_perioperative_RT": 110},
        arm_events={"neoadjuvant_or_adjuvant_RT": 2, "no_perioperative_RT": 14},
        events_total_printed=16,
        median_followup_months=38,
        endpoint_as_printed=("local recurrence (crude count in text); local recurrence-free "
                             "survival for the Table 2 hazard ratio"),
        counts_are_printed_integers=True,
        how_the_split_is_known=(
            "NEWLY OBTAINED 2026-09-09 by an ordinary permitted read of the open-access full text "
            "via the PubMed/PMC MCP route (PMC12398172, PMID 40885991, "
            "doi:10.1186/s13018-025-06245-6). It is NOT in Table 2 -- it is in the Results body "
            "text under 'Patients without metastases at diagnosis'. VERBATIM: 'Of the 24 patients "
            "who received (neo)adjuvant radiotherapy, two (8.3%) experienced local recurrence, and "
            "of the 110 patients who did not receive (neo)adjuvant radiotherapy, 14 (12.7%) "
            "experienced local recurrence.' Integers printed as words with percentages in "
            "parentheses. NOT derived from the HR, the arm sizes, the p-value or Fig. 2."),
        registry_pool_flag=True,
        registry_context_reason=None,
    )

    # ---- internal arithmetic checks on the newly obtained split ------------------
    checks = {
        "masunaga_arm_events_sum_equals_printed_total": (
            masunaga["arm_events"]["neoadjuvant_or_adjuvant_RT"]
            + masunaga["arm_events"]["no_perioperative_RT"] == masunaga["events_total_printed"]),
        "masunaga_arm_sizes_sum_equals_analysed_cohort_n": (
            sum(masunaga["arm_sizes"].values()) == 134),
        "masunaga_printed_percentages_match_the_printed_integers": {
            "RT_arm": {"printed_pct": 8.3, "recomputed": round(100 * 2 / 24, 1)},
            "no_RT_arm": {"printed_pct": 12.7, "recomputed": round(100 * 14 / 110, 1)},
            "agree": round(100 * 2 / 24, 1) == 8.3 and round(100 * 14 / 110, 1) == 12.7,
        },
        "masunaga_total_local_recurrence_rate_matches_printed_11_9pct": (
            round(100 * 16 / 134, 1) == 11.9),
        "bishop_arm_events_sum_equals_printed_total": (
            sum(bishop["arm_events"].values()) == bishop["events_total_printed"]),
        "bishop_arm_sizes_sum_equals_cohort_n": sum(bishop["arm_sizes"].values()) == 41,
        "note": ("These are consistency checks on numbers PRINTED IN THE PAPER. Recomputing a "
                 "percentage from printed integers to confirm they agree is verification, not the "
                 "forbidden reverse move of deriving an integer from a percentage."),
    }

    # ---- per-series 2x2s, reported as SIZES ------------------------------------
    def two_by_two(s, rt_key, no_rt_key):
        ert, nrt = s["arm_events"][rt_key], s["arm_sizes"][rt_key]
        eno, nno = s["arm_events"][no_rt_key], s["arm_sizes"][no_rt_key]
        p = fisher_two_sided(ert, nrt - ert, eno, nno - eno)
        return {
            "series": s["source_id"],
            "surgery_plus_RT": {"events": ert, "n": nrt,
                                "crude_pct": round(100 * ert / nrt, 1),
                                "wilson95": wilson(ert, nrt)},
            "surgery_alone": {"events": eno, "n": nno,
                              "crude_pct": round(100 * eno / nno, 1),
                              "wilson95": wilson(eno, nno)},
            "fisher_exact_two_sided_p": round(p, 4),
            "fragility_events": fragility(eno, nno, ert, nrt),
            "median_followup_months": s["median_followup_months"],
            "not_an_effect_estimate": (
                "Reported to show the SIZE of the table. Treatment was assigned by indication in "
                "both series; there is no randomisation and no adjustment here."),
        }

    t_bishop = two_by_two(bishop, "surgery_plus_RT", "surgery_alone")
    t_masunaga = two_by_two(masunaga, "neoadjuvant_or_adjuvant_RT", "no_perioperative_RT")

    # ---- admissibility of a pool, decided rather than asserted -------------------
    admissibility = {
        "rule_source": "systems/POLICY-evidence.md 2.1, 2.2, 2.3, 2.4",
        "2_1_1_confirmed_EMC": {
            "bishop2019": "yes (single-institution sarcoma centre series)",
            "masunaga2025": "pathologically diagnosed EMC, national registry; molecular "
                            "confirmation not stated for every case",
            "verdict": "met, with masunaga2025's confirmation basis recorded as histopathological",
        },
        "2_1_2_explicit_integer_counts": {
            "bishop2019": "MET (1/33, 4/8 printed as integers)",
            "masunaga2025": "NOW MET (2/24, 14/110 printed as integers in the Results text). "
                            "This is the criterion that failed at k=1 and no longer fails.",
            "verdict": "met for both",
        },
        "2_1_3_outcome_not_the_inclusion_criterion": {
            "verdict": "met -- both cohorts are localised-at-diagnosis surgically treated "
                       "patients; local recurrence is an outcome, not an entry criterion",
        },
        "2_1_4_and_2_3_non_overlapping_population": {
            "verdict": "met FOR THIS CONTRAST",
            "reasoning": (
                "bishop2019 carries registry pool:false for population-overlap with SEER / the US "
                "Sarcoma Collaborative. Neither ussc2022 nor remiszewski2025 nor seer270_2022 nor "
                "uMich2023 contributes ANY arm-level local-recurrence event to this contrast, so "
                "no patient can be counted twice by summing bishop2019 with masunaga2025. "
                "POLICY-evidence 2.3 names this exact pair as permissible: 'Distinct populations "
                "(e.g. a Japanese registry and a US single institution) may be pooled.'"),
            "binding_restriction": (
                "This ruling is scoped to the surgery+RT vs surgery-alone contrast ONLY. "
                "bishop2019 must still NEVER be summed into any total that also contains "
                "ussc2022, remiszewski2025, seer270_2022 or uMich2023, and this ledger does not "
                "change the registry's pool flags, which remain as committed."),
        },
        "2_4_endpoint_class": {
            "what_is_pooled": ("crude during-follow-up local-recurrence counts -- the event-rate "
                               "class that 2.4 permits to be pooled, labelled 'crude, mixed "
                               "follow-up'"),
            "what_is_NOT_pooled": [
                "bishop2019's 10-year ACTUARIAL local control (100% vs 63%) -- time-anchored, "
                "2.4 forbids merging it",
                "masunaga2025's LOCAL RECURRENCE-FREE SURVIVAL hazard ratio 0.50 (0.11-2.25) -- "
                "time-to-event, per row only",
                "any cross-study odds ratio, risk ratio, hazard ratio, significance test or "
                "heterogeneity statistic -- 2.2 sanctions a crude pooled proportion with a Wilson "
                "interval and side-by-side per-cohort rates, nothing more",
            ],
        },
        "verdict": "ADMISSIBLE at k=2 for a crude pooled per-arm local-recurrence PROPORTION",
    }

    # ---- the pool: per-arm proportions only, no pooled effect --------------------
    rt_ev = bishop["arm_events"]["surgery_plus_RT"] + masunaga["arm_events"]["neoadjuvant_or_adjuvant_RT"]
    rt_n = bishop["arm_sizes"]["surgery_plus_RT"] + masunaga["arm_sizes"]["neoadjuvant_or_adjuvant_RT"]
    no_ev = bishop["arm_events"]["surgery_alone"] + masunaga["arm_events"]["no_perioperative_RT"]
    no_n = bishop["arm_sizes"]["surgery_alone"] + masunaga["arm_sizes"]["no_perioperative_RT"]

    pooled = {
        "k_series": 2,
        "total_counted_local_recurrence_events_carrying_the_contrast": rt_ev + no_ev,
        "total_patients_carrying_the_contrast": rt_n + no_n,
        "surgery_plus_RT": {"events": rt_ev, "n": rt_n,
                            "crude_pct": round(100 * rt_ev / rt_n, 1),
                            "wilson95": wilson(rt_ev, rt_n)},
        "surgery_alone_or_no_perioperative_RT": {"events": no_ev, "n": no_n,
                                                 "crude_pct": round(100 * no_ev / no_n, 1),
                                                 "wilson95": wilson(no_ev, no_n)},
        "heterogeneity_shown_not_summarised": {
            "surgery_plus_RT_rate_range_pct": [t_bishop["surgery_plus_RT"]["crude_pct"],
                                               t_masunaga["surgery_plus_RT"]["crude_pct"]],
            "surgery_alone_rate_range_pct": [t_masunaga["surgery_alone"]["crude_pct"],
                                             t_bishop["surgery_alone"]["crude_pct"]],
            "comment": ("The no-RT arms differ by a factor of about four between the two series "
                        "(50.0% vs 12.7%). POLICY-evidence 2.2: a wide range means the pooled "
                        "point estimate hides real between-study variation. No I-squared is "
                        "computed; the honest signal is how much the two series disagree."),
        },
        "dominance_disclosure": ("masunaga2025 supplies 134 of the 175 patients (77%) and 16 of "
                                 "the 21 events (76%). The pool is a Japanese national registry "
                                 "with one US single-institution series added."),
        "mixed_follow_up_disclosure": ("median follow-up 94 months (bishop2019) vs 38 months "
                                       "(masunaga2025). Censoring is ignored. A crude proportion "
                                       "under materially shorter follow-up understates the "
                                       "lifetime recurrence risk, and the two series are not on a "
                                       "common time axis."),
        "deliberately_absent": ("No pooled odds ratio, risk ratio, hazard ratio, risk difference, "
                                "cross-study p-value, I-squared or random-effects estimate is "
                                "computed. The contrast between these two numbers is CONFOUNDED BY "
                                "INDICATION IN BOTH SERIES AND IN OPPOSITE-SIGN WAYS (see "
                                "confounding_direction) and is not interpretable as an effect."),
    }

    confounding = {
        "bishop2019": ("Direction not established by any quantity read here. The prior lane "
                       "recorded treatment assigned by indication with no adjustment."),
        "masunaga2025_measured_and_printed": (
            "VERBATIM: 'Of the 24 patients who received (neo)adjuvant radiotherapy, 10 (41.7%) "
            "had R1 or R2 surgical margins, whereas only 20 (18.2%) of the 110 patients who did "
            "not receive (neo)adjuvant radiotherapy had R1 or R2 surgical margins.' The paper "
            "also states radiotherapy 'is administered to prevent local recurrence in patients "
            "with close surgical margins'. R1/R2 margin is that paper's ONLY significant "
            "multivariable risk factor for local recurrence (HR 4.76 [1.72-13.15], p=0.003). So "
            "the irradiated arm was systematically the higher-risk arm."),
        "why_this_matters": ("Channelling of higher-risk patients into the RT arm biases a crude "
                             "unadjusted comparison AGAINST radiotherapy in masunaga2025. That is "
                             "a reason the crude numbers cannot be read as an effect in either "
                             "direction -- it is not a licence to reinterpret them as favourable."),
        "authors_own_limitation_verbatim": (
            "'First, as this was a retrospective study, there was an indication bias for "
            "(neo)adjuvant radiotherapy and chemotherapy use.'"),
    }

    published_model_level_estimates = {
        "note": ("Recorded for completeness at the level the papers publish them. NOT pooled, NOT "
                 "converted, NOT combined with the counted events above."),
        "bishop2019": {"quantity": "10-year actuarial local control", "surgery_plus_RT_pct": 100,
                       "surgery_alone_pct": 63, "p": 0.004,
                       "caveat": ("100% is a statement about a censored horizon, not that the arm "
                                  "had no local relapses -- the same paper counts one relapse "
                                  "among those 33 (prior lane, section 4.3).")},
        "masunaga2025": {"quantity": "local recurrence-free survival, univariate Cox",
                         "hr": 0.50, "ci95": [0.11, 2.25], "p": 0.365,
                         "authors_conclusion_verbatim": ("'the local control effect of "
                                                         "(neo)adjuvant radiotherapy is limited'")},
        "masunaga2025_disease_specific_survival_row": {
            "quantity": "disease-specific survival, univariate Cox, (neo)adjuvant radiotherapy",
            "hr": 5.05, "ci95": [1.34, 19.04], "p": 0.017,
            "why_recorded": ("Recorded so the ledger does not present only the favourable-looking "
                             "row. It did NOT survive the paper's own multivariate model (trunk "
                             "site and tumour size did). Given the measured margin imbalance this "
                             "row is at least as likely to reflect indication bias as anything "
                             "else. NO safety claim is made or supported: this is a size, and an "
                             "unadjusted univariate one."),
        },
    }

    leads_not_admitted = [
        {
            "what": ("A THIRD per-arm local-recurrence split with printed integers: 1/10 (10%) "
                     "with surgery + (neo)adjuvant RT vs 7/17 (41%) with surgery alone, p=0.08."),
            "where_found": ("masunaga2025 Discussion, quoting 'another multicenter retrospective "
                            "study involving only localized and molecularly confirmed cases'."),
            "why_not_admitted": (
                "SECONDARY PROVENANCE. POLICY-evidence 1.3 forbids laundering a citation: a count "
                "read out of another paper's discussion is not a primary read, and the reference "
                "number is stripped from the retrieved full text, so the primary study is "
                "UNIDENTIFIED. Admitting it would raise k on an unverified identity."),
            "next_step_if_wanted": (
                "Resolve the reference from the article's reference list (not returned by this "
                "route) or from the publisher DOI, then read that primary directly. "
                "chiusole2020 (European two-institution series, n=49) is a PLAUSIBLE BUT "
                "UNVERIFIED candidate -- 27 localised molecularly confirmed cases would be a "
                "subset of 49. This is a guess and is recorded as one; it has NOT been checked."),
            "k_if_admitted_after_verification": 3,
        },
        {
            "what": "drilon2008: surgery+RT vs surgery alone local recurrence 41% vs 35%, p=0.79.",
            "where_found": "masunaga2025 Discussion; registry cohort drilon2008 (n=87).",
            "why_not_admitted": ("PERCENTAGE-ONLY. POLICY-evidence 2.1(2) forbids deriving counts "
                                 "from a published percentage for pooling. Matches the registry's "
                                 "existing contextReason 'percentage-only'."),
        },
    ]

    return {
        "_id": "LOCOREGIONAL-2-RT-CONTRAST-LEDGER-K2-2026-09-09",
        "_continues": "PUB-LOCOREGIONAL-RT-CONTRAST-LEDGER-2026-09-08",
        "_question": ("Is a per-arm local-recurrence EVENT COUNT for the surgery+RT vs surgery-"
                      "alone contrast DIRECTLY REPORTED anywhere in masunaga2025 (PMC12398172), "
                      "and if so what does the counted-event evidence base become?"),
        "_answer": ("YES -- directly reported in the Results body text, not in Table 2. "
                    "k moves from 1 to 2. The counted-event base moves from 5 events in 1 "
                    "non-poolable series to 21 events in 2 series that POLICY-evidence 2.3 "
                    "permits to be pooled for this contrast."),
        "_not_medical_advice": ("Nothing here asserts efficacy, safety, tolerability, a "
                                "therapeutic window or clinical readiness for radiotherapy or any "
                                "other local treatment. Both series are retrospective with "
                                "treatment assigned by indication; one of them measures and prints "
                                "the resulting imbalance. Sizes are reported; effects are not."),
        "_retrieval_provenance": {
            "route": "PubMed / PubMed Central MCP server (mcp__PubMed__get_full_text_article)",
            "pmcid": "PMC12398172", "pmid": "40885991",
            "doi": "10.1186/s13018-025-06245-6",
            "doi_url": "https://doi.org/10.1186/s13018-025-06245-6",
            "retrieved": "2026-09-09",
            "attribution_required_by_tool": ("Information from this article is retrieved from "
                                             "PubMed and must be cited to PubMed with the DOI."),
            "license_recorded_in_registry": "CC-BY-NC-ND-4.0",
            "no_direct_http_fetch_attempted": True,
            "check_record": "checks/01-pubmed-mcp-fulltext-PMC12398172/",
        },
        "_inputs": {
            "prior_ledger": ("research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                             "PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-LOCOREGIONAL/"
                             "rt-local-control-contrast-ledger.json"),
            "registry": "research/data/emc-clinical-registry.json",
            "policy": "systems/POLICY-evidence.md",
            "new_primary_read": "PMC12398172 full text (PubMed MCP)",
        },
        "_forbidden_move_not_made": (
            "No event count anywhere in this artifact is reconstructed from a hazard ratio, an arm "
            "size, a p-value, a confidence interval or a Kaplan-Meier curve. The masunaga2025 "
            "split is a printed integer sentence. Figure 2 was not read for numbers and carries no "
            "numbers-at-risk table in the retrieved text."),
        "k_counted_event_series": {"before": 1, "after": 2,
                                   "moved": True,
                                   "prior_lane_recorded_value": prior.get(
                                       "total_counted_local_events_carrying_the_RT_contrast")},
        "arm_level_event_ledger": [bishop, masunaga],
        "internal_consistency_checks": checks,
        "per_series_2x2_reported_as_sizes": [t_bishop, t_masunaga],
        "pool_admissibility": admissibility,
        "crude_pooled_per_arm_proportions": pooled,
        "confounding_direction": confounding,
        "published_model_level_estimates_not_pooled": published_model_level_estimates,
        "leads_found_but_not_admitted": leads_not_admitted,
        "what_the_manuscript_may_now_say": [
            ("The counted-event evidence base for the adjuvant-radiotherapy local-control contrast "
             "in EMC is 21 local recurrences among 175 localised, surgically treated patients in "
             "two series -- an MD Anderson single-institution cohort and the Japanese national "
             "registry."),
            ("Both series' arm-level counts are now available as printed integers: 1/33 vs 4/8 "
             "(bishop2019) and 2/24 vs 14/110 (masunaga2025)."),
            ("The two series disagree sharply in the size of the crude difference. The "
             "non-irradiated arms recur at 50.0% (4/8) and 12.7% (14/110) respectively; the "
             "irradiated arms at 3.0% (1/33) and 8.3% (2/24)."),
            ("In the larger series the irradiated arm was the systematically higher-risk arm: "
             "41.7% R1/R2 margins versus 18.2%, against an R1/R2 margin hazard ratio of 4.76 "
             "(1.72-13.15) for local recurrence."),
            ("The two published model-level estimates are a 10-year actuarial local control of "
             "100% vs 63% (p=0.004) and a local recurrence-free survival hazard ratio of 0.50 "
             "(0.11-2.25, p=0.365); the first is a censored-horizon statement, not a claim of zero "
             "relapses in that arm."),
            ("Within-series, the crude difference is significant only in the smaller series and "
             "only against an eight-patient comparator arm: Fisher two-sided p=0.0032 with a "
             "fragility of 2 in bishop2019, versus p=0.74 in masunaga2025. The entire apparent "
             "signal in the counted-event evidence rests on four recurrences among eight "
             "non-irradiated patients at one institution."),
            ("Pooled crudely across both series and labelled as such -- crude, unadjusted, mixed "
             "follow-up (94 vs 38 months median), no censoring -- 3/57 (5.3%, Wilson 1.8-14.4) of "
             "irradiated patients and 18/118 (15.3%, Wilson 9.9-22.8) of non-irradiated patients "
             "had a recorded local recurrence. These are descriptive proportions of two "
             "differently-selected groups, not two arms of a trial."),
            ("No randomised evidence exists, no adjusted comparison of irradiated versus "
             "non-irradiated patients exists in either series, and neither the pooled proportions "
             "nor either 2x2 supports an efficacy claim."),
        ],
        "what_it_still_may_not_say": [
            "That adjuvant radiotherapy improves local control in EMC.",
            "That it does not -- the evidence is not adequate for a negative efficacy claim either.",
            "Any pooled effect size, pooled p-value, pooled hazard ratio or heterogeneity statistic.",
            "Any statement about radiotherapy and survival built on the DSS hazard ratio of 5.05.",
            "RT-RT-INTENSIFY remains REFUTED. RT-METASTASECTOMY remains DO-NOT-WRITE. "
            "Nothing in this ledger reopens either.",
        ],
        "verdict": (
            "The prior lane's bounded no-go was CONDITIONAL on a missing arm-level split, and that "
            "condition is now resolved in the affirmative. k=2. A crude pooled per-arm PROPORTION "
            "is admissible under POLICY-evidence 2.1-2.4 for this contrast; a pooled EFFECT "
            "ESTIMATE remains inadmissible and is not computed. The manuscript's honest sentence "
            "changes from 'five local recurrences in one non-poolable series' to '21 local "
            "recurrences in two series, unadjusted, with the irradiated arm measurably "
            "higher-risk in the larger of them'."),
    }

def main():
    data = build()
    text = json.dumps(data, indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print("CHECK FAIL: artifact missing:", OUT); return 1
        cur = open(OUT, encoding="utf-8").read()
        if cur == text:
            print("CHECK MATCH: re-derived artifact is byte-identical to the committed one.")
            return 0
        print("CHECK MISMATCH: re-derived artifact differs from the committed one.")
        return 1
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    p = data["crude_pooled_per_arm_proportions"]
    print("k:", data["k_counted_event_series"])
    print("pooled surgery+RT      :", p["surgery_plus_RT"])
    print("pooled no perioperative RT:", p["surgery_alone_or_no_perioperative_RT"])
    print("total counted events   :", p["total_counted_local_recurrence_events_carrying_the_contrast"])
    for t in data["per_series_2x2_reported_as_sizes"]:
        print(t["series"], "RT", t["surgery_plus_RT"]["events"], "/", t["surgery_plus_RT"]["n"],
              "| noRT", t["surgery_alone"]["events"], "/", t["surgery_alone"]["n"],
              "| fisher p =", t["fisher_exact_two_sided_p"], "| fragility =", t["fragility_events"])
    print("consistency checks:", json.dumps(data["internal_consistency_checks"], ensure_ascii=False)[:400])
    print("wrote", OUT)
    return 0

if __name__ == "__main__":
    sys.exit(main())
