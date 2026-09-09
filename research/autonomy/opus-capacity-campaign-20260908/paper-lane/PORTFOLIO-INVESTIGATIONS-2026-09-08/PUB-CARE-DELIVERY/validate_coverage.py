#!/usr/bin/env python3
"""Validate the coverage matrix against the source artifacts' OWN recorded counts.
Each check compares a number this lane derived with a number a committed artifact states
independently. Any mismatch is printed and exits non-zero."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
L = lambda p: json.load(open(os.path.join(ROOT, p)))
cov  = json.load(open(os.path.join(os.path.dirname(__file__), "care-delivery-element-coverage.json")))
surg = L("research/modalities/emc-surgical-quality.json")
site = L("research/modalities/emc-site-curation.json")
adm  = L("research/literature/emc-km-admissibility-2026-08-27.json")
ipd  = L("research/modalities/emc-ipd-survival.json")
ec   = cov["element_counts"]
checks = [
 ("margin series count == emc-surgical-quality counts.series",
  ec["surgical_margin_distribution"]["REPORTED"]["n_series"], surg["counts"]["series"]),
 ("primary-site patients == emc-site-curation pooled denominator",
  ec["primary_site_distribution"]["REPORTED"]["patients"],
  site["pooled_extremity_fraction"]["extremity_strict"]["denom"]),
 ("risk-row REPORTED == admissibility by_verdict.admitted",
  ec["numbers_at_risk_row"]["REPORTED"]["n_series"], len(adm["by_verdict"]["admitted"])),
 ("risk-row EXAMINED_NOT_PRINTED == admissibility refused_no_risk_row",
  ec["numbers_at_risk_row"]["EXAMINED_NOT_PRINTED"]["n_series"], len(adm["by_verdict"]["refused_no_risk_row"])),
 ("risk-row patients examined == admissibility patients_in_series_whose_figures_were_read",
  ec["numbers_at_risk_row"]["REPORTED"]["patients"] + ec["numbers_at_risk_row"]["EXAMINED_NOT_PRINTED"]["patients"],
  adm["totals"]["patients_in_series_whose_figures_were_read"]),
 ("risk-row admitted patients == admissibility patients_in_admitted_series",
  ec["numbers_at_risk_row"]["REPORTED"]["patients"], adm["totals"]["patients_in_admitted_series"]),
 ("candidate series == emc-ipd-survival candidate_sources",
  cov["candidate_series"], len(ipd["candidate_sources"])),
 ("admissibility census covers one fewer series than the candidate list (immunosarc2emc2025, a conference abstract)",
  cov["candidate_series"] - adm["totals"]["candidates"], 1),
]
bad = 0
for name, got, want in checks:
    ok = got == want
    bad += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name}: derived={got} artifact={want}")
print(f"\n{len(checks)-bad}/{len(checks)} checks pass")
sys.exit(1 if bad else 0)
