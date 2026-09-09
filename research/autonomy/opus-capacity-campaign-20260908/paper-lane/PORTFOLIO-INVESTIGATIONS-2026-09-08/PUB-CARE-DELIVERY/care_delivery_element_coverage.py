#!/usr/bin/env python3
"""Care-delivery data-element coverage matrix over the candidate EMC clinical series.

Reads ONLY files already committed to this repository. No network, no new curation,
no re-run of the closed IPD/KM reconstruction pilot: the numbers-at-risk column is
copied from that pilot's own recorded verdicts and is not recomputed from any figure.

Status vocabulary (mutually exclusive, per series x element):
  REPORTED             a committed artifact holds the value for this series
  EXAMINED_NOT_PRINTED a committed artifact records that this named paper does not print it
  NOT_EXAMINED         no committed artifact records this element for this series
                       (sub-tagged UNRETRIEVED when the series was never retrieved at all)

An element that is NOT_EXAMINED is UNKNOWN, never absent (CLAUDE.md s4).
"""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
def L(rel):
    with open(os.path.join(ROOT, rel)) as fh:
        return json.load(fh)

P_IPD   = "research/modalities/emc-ipd-survival.json"
P_ADM   = "research/literature/emc-km-admissibility-2026-08-27.json"
P_SURG  = "research/modalities/emc-surgical-quality.json"
P_SITE  = "research/modalities/emc-site-curation.json"
P_TIME  = "research/modalities/emc-recurrence-timing.json"
P_COEF  = "research/modalities/emc-prognostic-coefficients.json"

ipd, adm, surg, site, time_, coef = (L(p) for p in (P_IPD, P_ADM, P_SURG, P_SITE, P_TIME, P_COEF))

candidates = {c["source_id"]: c for c in ipd["candidate_sources"]}
verdict = {}
for k, ids in adm["by_verdict"].items():
    for sid in ids:
        verdict[sid] = k

surg_series  = {s["source_id"]: s for s in surg["series"]}
site_series  = {s["source_id"]: s for s in site["series"]}
time_series  = {c["source_id"]: c for c in time_["cohorts"]}
coef_series  = {k: v for k, v in coef["cohorts"].items()}

NE  = ("NOT_EXAMINED", None)
def ne(sid):
    return ("NOT_EXAMINED", "UNRETRIEVED" if verdict.get(sid) == "unreachable" else None)

def margin_dist(sid):
    s = surg_series.get(sid)
    if not s: return ne(sid)
    return ("REPORTED", P_SURG)

def margin_def(sid):
    s = surg_series.get(sid)
    if not s: return ne(sid)
    return ("REPORTED", P_SURG) if s.get("margin_definition_printed") else ("EXAMINED_NOT_PRINTED", P_SURG)

def stage_split(sid):
    s = surg_series.get(sid)
    if not s: return ne(sid)
    return ("REPORTED", P_SURG) if "margin_metastatic" in s else ("EXAMINED_NOT_PRINTED", P_SURG)

def primary_site(sid):
    s = site_series.get(sid)
    if not s: return ne(sid)
    return ("REPORTED", P_SITE) if s.get("primary_site_counts") else ("EXAMINED_NOT_PRINTED", P_SITE)

def median_fu(sid):
    c = time_series.get(sid) or coef_series.get(sid)
    if not c: return ne(sid)
    return ("REPORTED", P_TIME if sid in time_series else P_COEF) if c.get("median_followup_months") is not None \
           else ("EXAMINED_NOT_PRINTED", P_TIME if sid in time_series else P_COEF)

def event_timing(sid):
    c = time_series.get(sid)
    if not c: return ne(sid)
    has = any(e.get("median_months") is not None for e in c.get("events", []))
    return ("REPORTED", P_TIME) if has else ("EXAMINED_NOT_PRINTED", P_TIME)

def cox(sid):
    c = coef_series.get(sid)
    if not c: return ne(sid)
    rows = [r for m in coef["models"] for r in m.get("rows", []) if m.get("cohort") == sid or m.get("source_id") == sid]
    return ("REPORTED", P_COEF) if c.get("endpoints_modelled") else ("EXAMINED_NOT_PRINTED", P_COEF)

def risk_row(sid):
    v = verdict.get(sid)
    if v == "admitted": return ("REPORTED", P_ADM)
    if v == "refused_no_risk_row": return ("EXAMINED_NOT_PRINTED", P_ADM)
    return ("NOT_EXAMINED", "UNRETRIEVED")

# The two fields whose absence emc-surgical-quality.json states UNIVERSALLY.
def treatment_setting(sid):
    return ("EXAMINED_NOT_PRINTED", P_SURG) if sid in surg_series else ne(sid)
def unplanned_excision(sid):
    return ("EXAMINED_NOT_PRINTED", P_SURG) if sid in surg_series else ne(sid)

ELEMENTS = [
    ("surgical_margin_distribution", margin_dist),
    ("margin_definition_printed",    margin_def),
    ("stage_at_diagnosis_split",     stage_split),
    ("primary_site_distribution",    primary_site),
    ("median_follow_up",             median_fu),
    ("time_to_event_median",         event_timing),
    ("fitted_cox_coefficients",      cox),
    ("numbers_at_risk_row",          risk_row),
    ("treatment_setting_or_referral", treatment_setting),
    ("unplanned_excision_defined",   unplanned_excision),
]

order = sorted(candidates, key=lambda s: -(candidates[s].get("n") or 0))
matrix, elem_counts = {}, {}
for sid in order:
    matrix[sid] = {"n": candidates[sid].get("n"), "retrieval_verdict": verdict.get(sid, "not_in_admissibility_census"), "elements": {}}
    for name, fn in ELEMENTS:
        st, src = fn(sid)
        matrix[sid]["elements"][name] = {"status": st, "evidence": src}

for name, _ in ELEMENTS:
    c = {"REPORTED": [], "EXAMINED_NOT_PRINTED": [], "NOT_EXAMINED": []}
    for sid in order:
        c[matrix[sid]["elements"][name]["status"]].append(sid)
    elem_counts[name] = {k: {"n_series": len(v), "series": v, "patients": sum(candidates[s].get("n") or 0 for s in v)} for k, v in c.items()}

total_patients = sum(candidates[s].get("n") or 0 for s in order)
comparable = {n: elem_counts[n]["REPORTED"]["series"] for n, _ in ELEMENTS if elem_counts[n]["REPORTED"]["n_series"] >= 2}

# Denominator audit of the two universal absence claims.
examined_set = sorted(surg_series)
audit = {
  "claim": "emc-surgical-quality.json: treatment_setting.recorded_in_any_reachable_series == false "
           "and unplanned_excision.recorded_in_any_reachable_series == false",
  "claim_values_read": {
      "treatment_setting": surg["treatment_setting"]["recorded_in_any_reachable_series"],
      "unplanned_excision": surg["unplanned_excision"]["recorded_in_any_reachable_series"],
      "counts.series": surg["counts"]["series"],
  },
  "series_actually_examined_for_these_two_fields": examined_set,
  "n_examined": len(examined_set),
  "candidate_series_total": len(order),
  "series_retrieved_at_least_once_per_admissibility_census":
      sorted(s for s in order if verdict.get(s) in ("admitted", "refused_no_risk_row")),
  "series_with_a_committed_full_text_id_in_emc-ipd-survival":
      sorted(s for s in order if candidates[s].get("full_text_reachable")),
  "series_reachable_by_at_least_one_of_those_two_definitions_and_NOT_examined_for_these_fields":
      sorted(set(s for s in order if verdict.get(s) in ("admitted", "refused_no_risk_row")
                 or candidates[s].get("full_text_reachable")) - set(examined_set)),
}
audit["verdict"] = (
  "OVER-SCOPED. The universal quantifier 'any reachable series' is asserted over an examined set of "
  f"{len(examined_set)} series, while {len(audit['series_reachable_by_at_least_one_of_those_two_definitions_and_NOT_examined_for_these_fields'])} "
  "further series are reachable by the repository's own two definitions of reachable and carry no "
  "committed reading of either field. For those series the two fields are UNKNOWN, not absent."
)

out = {
 "_what": "Care-delivery data-element coverage across the 17 candidate EMC clinical series, and a "
          "denominator audit of the two universal absence claims in emc-surgical-quality.json.",
 "_not_medical_advice": "Nothing here is medical advice and nothing here asserts efficacy, safety, "
                        "selectivity, a therapeutic window or clinical readiness.",
 "_generated_by": "research/autonomy/opus-capacity-campaign-20260908/paper-lane/"
                  "PORTFOLIO-INVESTIGATIONS-2026-09-08/PUB-CARE-DELIVERY/care_delivery_element_coverage.py",
 "_reads_only": [P_IPD, P_ADM, P_SURG, P_SITE, P_TIME, P_COEF],
 "_no_network": "This script opens no socket. Every input is a committed repository file.",
 "_not_a_reopening_of_the_closed_pilot": "The numbers_at_risk_row column is copied verbatim from "
          "emc-km-admissibility-2026-08-27.json's recorded verdicts. No figure was re-read, no curve "
          "digitised and no reconstruction attempted.",
 "candidate_series": len(order), "candidate_patients_sum": total_patients,
 "⛔_patients_are_not_additive": "Series denominators overlap (see overlap_risk in emc-ipd-survival.json) "
          "and are summed here only to weight the accounting, never as an EMC patient count.",
 "coverage_matrix": matrix,
 "element_counts": elem_counts,
 "elements_reported_by_two_or_more_series": comparable,
 "absence_claim_denominator_audit": audit,
}
json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
print()
