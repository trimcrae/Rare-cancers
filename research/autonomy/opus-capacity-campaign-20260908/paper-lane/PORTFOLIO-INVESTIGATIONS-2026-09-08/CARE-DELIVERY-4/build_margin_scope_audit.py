#!/usr/bin/env python3
"""CARE-DELIVERY-4 — re-derive the margin element from committed artifacts and
test the scope of CARE-DELIVERY-3's sentence "no trial series prints a margin at all".

Reads only. Writes only margin-element-scope-audit.json in this lane's directory.
No clinical, efficacy or safety claim is made or implied by anything here, and no
association between setting, referral or excision planning and any outcome is asserted.
"""
import hashlib, json, os, subprocess, sys

REPO = "/home/user/Rare-cancers"
LANE = os.path.dirname(os.path.abspath(__file__))
INV = os.path.dirname(LANE)
V3 = os.path.join(INV, "CARE-DELIVERY-3", "care-delivery-element-coverage-v3.json")
V3F = os.path.join(INV, "CARE-DELIVERY-3", "FINDING.md")
IPD = os.path.join(REPO, "research/modalities/emc-ipd-survival.json")
SQ = os.path.join(REPO, "research/modalities/emc-surgical-quality.json")

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def load(p):
    with open(p) as f:
        return json.load(f)

v3, ipd, sq = load(V3), load(IPD), load(SQ)
mat = v3["coverage_matrix"]
ELT = "surgical_margin_distribution"

# ---------------------------------------------------------------- 1. re-derive
# Independently recount the margin element straight off the matrix rows.
buckets = {"REPORTED": [], "EXAMINED_NOT_PRINTED": [], "NOT_EXAMINED": []}
for sid, row in mat.items():
    buckets[row["elements"][ELT]["status"]].append(sid)
rederived = {
    k: {"n_series": len(v), "series": sorted(v),
        "patients": sum(mat[s]["n"] for s in v)}
    for k, v in buckets.items()
}
stated = v3["element_counts"][ELT]
recount_checks = []
for k in buckets:
    for f in ("n_series", "patients"):
        recount_checks.append({
            "claim": f"element_counts.{ELT}.{k}.{f}",
            "stated": stated[k][f], "rederived": rederived[k][f],
            "verdict": "REPRODUCES" if stated[k][f] == rederived[k][f] else "MISMATCH"})
    recount_checks.append({
        "claim": f"element_counts.{ELT}.{k}.series (as a set)",
        "stated": sorted(stated[k]["series"]), "rederived": rederived[k]["series"],
        "verdict": "REPRODUCES" if sorted(stated[k]["series"]) == rederived[k]["series"] else "MISMATCH"})

# poolable set, re-derived from the matrix cells rather than from v3's summary block
scale = v3["⭐_margin_distributions_are_not_all_on_one_scale"]
poolable_stated = sorted(scale["on_the_printed_R0_R1_R2_scale"]["series"])
pat_stated = scale["on_the_printed_R0_R1_R2_scale"]["patients_with_a_margin_value"]
# masunaga: operated = registered - no_surgery, from emc-surgical-quality.json itself
sq_ser = {s["source_id"]: s for s in sq["series"]}
mas = sq_ser["masunaga2025"]
mas_operated = sum(mas["margin_all_registered"][k] for k in ("R0", "R1", "R2"))
chi_field = sq_ser["chiusole2020"]["margin_field_available_for"]
dri_den = mat["drilon2008"]["elements"][ELT]["derived"]["denominator"]
dri_sum = sum(mat["drilon2008"]["elements"][ELT]["derived"][k] for k in ("R0", "R1", "R2"))
poolable_rederived = {"masunaga2025": mas_operated, "chiusole2020": chi_field, "drilon2008": dri_den}
pool_checks = [
    {"claim": "poolable series set", "stated": poolable_stated,
     "rederived": sorted(poolable_rederived),
     "verdict": "REPRODUCES" if poolable_stated == sorted(poolable_rederived) else "MISMATCH"},
    {"claim": "masunaga2025 operated-with-a-margin = R0+R1+R2 of margin_all_registered",
     "stated": pat_stated["masunaga2025"], "rederived": mas_operated,
     "verdict": "REPRODUCES" if pat_stated["masunaga2025"] == mas_operated else "MISMATCH"},
    {"claim": "chiusole2020 = emc-surgical-quality margin_field_available_for",
     "stated": pat_stated["chiusole2020"], "rederived": chi_field,
     "verdict": "REPRODUCES" if pat_stated["chiusole2020"] == chi_field else "MISMATCH"},
    {"claim": "drilon2008 denominator = R0+R1+R2 of the quoted verbatim sentence",
     "stated": pat_stated["drilon2008"], "rederived": dri_sum,
     "verdict": "REPRODUCES" if pat_stated["drilon2008"] == dri_sum == dri_den else "MISMATCH"},
    {"claim": "emc-surgical-quality.counts.operated_patients_with_a_margin_recorded "
              "= masunaga operated + chiusole field-available (its own two-series scope)",
     "stated": sq["counts"]["operated_patients_with_a_margin_recorded"],
     "rederived": mas_operated + chi_field,
     "verdict": "REPRODUCES" if sq["counts"]["operated_patients_with_a_margin_recorded"]
                == mas_operated + chi_field else "MISMATCH"},
    {"claim": "emc-surgical-quality.counts.series = len(series array)",
     "stated": sq["counts"]["series"], "rederived": len(sq["series"]),
     "verdict": "REPRODUCES" if sq["counts"]["series"] == len(sq["series"]) else "MISMATCH"},
]

# examined set for the margin element = REPORTED u EXAMINED_NOT_PRINTED
examined_margin = sorted(buckets["REPORTED"] + buckets["EXAMINED_NOT_PRINTED"])
audit_examined = sorted(v3["absence_claim_denominator_audit_v3"]["v3_verdict"]
                        ["unplanned_excision"]["series_examined_after_v3"])
pool_checks.append({
    "claim": "margin examined set (REPORTED u EXAMINED_NOT_PRINTED) equals the "
             "six-series examined set the v3 absence audit uses",
    "stated": audit_examined, "rederived": examined_margin,
    "verdict": "REPRODUCES" if audit_examined == examined_margin else "MISMATCH"})

# ------------------------------------------------- 2. design classification
# Verbatim `why_candidate` strings from research/modalities/emc-ipd-survival.json.
# A series is TRIAL-DESIGN only where its own committed description names a
# prospective phase study or a randomised trial. Nothing is inferred from a drug name.
TRIAL_MARKERS = ("prospective", "phase 2", "phase ib/ii", "randomised trial", "randomized trial")
NONTRIAL_MARKERS = ("retrospective", "registry", "population", "database",
                    "single-institution", "multi-institution", "two-institution",
                    "two-referral-centre", "case series", "pathology series",
                    "clinicopathologic", "single-country")
designs = {}
for s in ipd["candidate_sources"]:
    w = s["why_candidate"]
    lw = w.lower()
    trial_hits = [m for m in TRIAL_MARKERS if m in lw]
    nontrial_hits = [m for m in NONTRIAL_MARKERS if m in lw]
    if trial_hits and not nontrial_hits:
        d = "TRIAL_DESIGN"
    elif nontrial_hits and not trial_hits:
        d = "NON_TRIAL_DESIGN"
    elif trial_hits and nontrial_hits:
        d = "MIXED_WORDING"
    else:
        d = "DESIGN_NOT_STATED_IN_THIS_ARTIFACT"
    designs[s["source_id"]] = {
        "n": s["n"], "why_candidate_verbatim": w,
        "design_class": d, "trial_markers_matched": trial_hits,
        "non_trial_markers_matched": nontrial_hits,
        "margin_status_in_v3": mat[s["source_id"]]["elements"][ELT]["status"],
        "retrieval_completeness_recorded": mat[s["source_id"]].get("retrieval_completeness") is not None,
    }

trial_ids = sorted(k for k, v in designs.items() if v["design_class"] == "TRIAL_DESIGN")
trial_by_status = {}
for t in trial_ids:
    trial_by_status.setdefault(designs[t]["margin_status_in_v3"], []).append(t)

# the set CARE-DELIVERY-3's own prose calls "the three trial series"
cd3_called_trials = sorted(v3["series_newly_read_by_this_lane"]) \
    if isinstance(v3.get("series_newly_read_by_this_lane"), list) else \
    ["martinbroto2020immunosarc1", "morioka2016trabectedin", "stacchiotti2013anthracycline"]

phrase = "no trial series prints a margin at all"
in_finding = phrase in open(V3F).read()
in_artifact = phrase in json.dumps(v3, ensure_ascii=False)

out = {
  "_what": "Re-derivation of the margin element of the CARE-DELIVERY coverage matrix, and a scope "
           "test of the sentence 'no trial series prints a margin at all' written in "
           "CARE-DELIVERY-3/FINDING.md §7.",
  "_not_medical_advice": "Nothing here is medical advice and nothing here asserts efficacy, safety, "
           "selectivity, a therapeutic window or clinical readiness. No association between "
           "treatment setting, referral or excision planning and any outcome is stated or implied. "
           "No patient was studied; no wet-lab work exists.",
  "_lane": "CARE-DELIVERY-4",
  "_generated_by": "build_margin_scope_audit.py",
  "_reads_only": {
    "care-delivery-element-coverage-v3.json": sha(V3),
    "CARE-DELIVERY-3/FINDING.md": sha(V3F),
    "research/modalities/emc-ipd-survival.json": sha(IPD),
    "research/modalities/emc-surgical-quality.json": sha(SQ),
  },
  "_no_retrieval": "This lane performed NO retrieval of any kind. Every value below is re-derived "
           "from artifacts already committed or already written by an earlier lane. Nothing here is "
           "a new reading of any paper.",
  "part_1_re_derivation_of_the_margin_element": {
    "rederived_from_the_matrix_rows": rederived,
    "checks": recount_checks + pool_checks,
    "all_reproduce": all(c["verdict"] == "REPRODUCES" for c in recount_checks + pool_checks),
  },
  "part_2_design_class_of_all_17_candidate_series": {
    "rule": "A series is TRIAL_DESIGN only where its own committed `why_candidate` string in "
            "research/modalities/emc-ipd-survival.json names a prospective phase study or a "
            "randomised trial, and names no retrospective/registry/institutional design. The rule "
            "is applied mechanically to the verbatim strings; nothing is inferred from a drug name "
            "or from a journal.",
    "trial_markers": list(TRIAL_MARKERS),
    "non_trial_markers": list(NONTRIAL_MARKERS),
    "by_series": designs,
    "trial_design_series": trial_ids,
    "n_trial_design_series": len(trial_ids),
  },
  "part_3_the_scope_test": {
    "sentence_under_test": phrase,
    "where_it_appears": {
      "CARE-DELIVERY-3/FINDING.md": in_finding,
      "care-delivery-element-coverage-v3.json": in_artifact,
      "⭐": "The over-scoped universal lives in the PROSE ONLY. The machine-readable artifact does "
           "not contain it and does not depend on it: v3's own matrix leaves every unexamined "
           "trial series at NOT_EXAMINED. The correction is therefore a prose correction, and no "
           "value in any artifact changes.",
    },
    "trial_design_series_by_margin_status_in_v3": trial_by_status,
    "series_CARE_DELIVERY_3_prose_calls_the_three_trial_series": cd3_called_trials,
    "⚠_one_of_those_three_is_not_a_trial": {
      "series": "stacchiotti2013anthracycline",
      "why_candidate_verbatim": designs["stacchiotti2013anthracycline"]["why_candidate_verbatim"],
      "note": "emc-ipd-survival.json calls it a retrospective centrally-reviewed systemic-therapy "
              "series, and CARE-DELIVERY-3's own §4 heading calls it an Italian Rare Cancer Network "
              "series. 'Trial series' is the wrong category label for it; 'systemic-therapy series' "
              "is the label its evidence supports.",
    },
    "verdict": None,   # filled below
  },
}

# ------------------------------------------------------------------- verdict
examined_trials = trial_by_status.get("EXAMINED_NOT_PRINTED", [])
unexamined_trials = trial_by_status.get("NOT_EXAMINED", [])
reported_trials = trial_by_status.get("REPORTED", [])
out["part_3_the_scope_test"]["verdict"] = {
  "answer": "BOUNDED STATEMENT ABOUT WHAT WAS RETRIEVED — NOT a claim about the papers.",
  "arithmetic": {
    "trial_design_series_among_the_17_candidates": len(trial_ids),
    "of_which_examined_for_the_margin_element": len(examined_trials) + len(reported_trials),
    "of_which_NOT_EXAMINED_for_the_margin_element": len(unexamined_trials),
    "examined": sorted(examined_trials + reported_trials),
    "not_examined": sorted(unexamined_trials),
  },
  "why": "Written as a universal ('no trial series ... at all') the sentence quantifies over every "
         "trial-design series. Exactly one of the four is examined for the margin element. Three "
         "are NOT_EXAMINED — including morioka2016trabectedin, which CARE-DELIVERY-3's own §3 and "
         "§4 record as narrative-only with all tables dropped, and whose margin cell v3 leaves at "
         "NOT_EXAMINED with the explicit note 'This lane therefore asserts NO absence for this "
         "element.' The prose sentence therefore contradicts the artifact the same lane wrote.",
  "⭐_this_is_the_same_defect_the_lineage_was_created_to_fix": "PUB-CARE-DELIVERY's decisive finding "
         "was that emc-surgical-quality.json's `recorded_in_any_reachable_series: false` is a "
         "universal quantifier over an examined set of two. One lane later, the same shape "
         "reappeared in the prose that reports the fix. The defect is a habit of language, not a "
         "one-off error, which is why the correction below is a sentence and not a number.",
  "the_supported_sentence": "Of the four trial-design series among the 17 candidates, one "
         "(martinbroto2020immunosarc1) was examined with its baseline table returned in full and "
         "prints no margin; the other three were not examined for this element. Together with "
         "stacchiotti2013anthracycline — a retrospective systemic-therapy series, not a trial — "
         "that is two systemic-therapy reports examined and no margin printed in either. Whether "
         "any trial series prints a margin is UNKNOWN.",
  "what_does_NOT_change": "The margin element's counts. Four series REPORTED and three poolable on "
         "the R0/R1/R2 scale re-derive exactly (part 1). The examined set for the margin element is "
         "the same six series the absence audit uses. No count, distribution or measured value in "
         "any artifact is added, removed or altered by this lane.",
}

path = os.path.join(LANE, "margin-element-scope-audit.json")
with open(path, "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
    f.write("\n")
print("wrote", path)
print("part 1 all_reproduce:", out["part_1_re_derivation_of_the_margin_element"]["all_reproduce"])
for c in recount_checks + pool_checks:
    print(f"  {c['verdict']:12s} {c['claim']}  stated={c['stated']} rederived={c['rederived']}")
print("trial-design series:", trial_ids)
print("trial series by margin status:", json.dumps(trial_by_status))
print("phrase in v3 FINDING.md:", in_finding, "| in v3 artifact:", in_artifact)
