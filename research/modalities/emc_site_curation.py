#!/usr/bin/env python3
"""Anatomical site of the primary and of the metastases, curated from the primary reports.

WHY THIS EXISTS
---------------
`emc-locoregional-eligibility.json` records two gaps and calls one of them the highest-value
curation the locoregional endpoint is waiting on, verbatim:

  * primary anatomical site — *"⛔ NO COHORT IN THE REGISTRY CARRIES A SITE FIELD … a prose ordering
    cannot become a denominator"*; wanted by RT-LIMB-PERFUSION, because isolated limb perfusion is
    offerable only for an extremity primary, so **the eligible fraction IS the extremity fraction**;
  * metastatic site — *"ONE COHORT CARRIES IT AND IT IS IN A NOTE, NOT A FIELD"*; wanted by
    RT-LUNG-DIRECTED, because a lung-directed strategy is offerable only to lung-confined disease.

Both said the same thing about the fix: *"re-curating the pooled series' site tables from their
primary reports — $0 for the open-access ones."* The primary reports are now retrievable
(`scripts/emc_km_figure_fetch.py`), so this file is that curation.

⛔ WHAT THIS IS AND IS NOT. Every count below is TRANSCRIBED from a printed table or a printed
sentence, and each names the exact table it came from. Nothing is digitized, nothing is inferred
from a percentage, and no cohort is pooled with another where the two use incompatible categories.
It computes eligibility DENOMINATORS. It asserts no efficacy, no safety and no clinical readiness,
and an "eligible fraction" is a statement about who a strategy could be OFFERED to, never about
whether it would work.

⚠ THE CATEGORY BOUNDARY IS THE RESULT'S BIGGEST SOFT SPOT, SO IT IS REPORTED TWICE RATHER THAN
DECIDED ONCE. Masunaga classifies shoulder, groin, axilla and buttock — 35 of 171 patients — under
TRUNK, and every one of those is a primary a perfusion service would argue about rather than refuse.
Both a strict and an inclusive extremity fraction are computed and neither is called the answer. The
gap between them is wider than the confidence interval on either, which is the finding: the binding
uncertainty here is a DEFINITION, not a sample size.

Run:     python3 research/modalities/emc_site_curation.py
Verify:  python3 research/modalities/emc_site_curation.py --check
Writes:  research/modalities/emc-site-curation.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-site-curation.json")

sys.path.insert(0, HERE)
from emc_locoregional_eligibility import wilson  # noqa: E402  -- one Wilson, one home

# ---------------------------------------------------------------------------
# the transcription
# ---------------------------------------------------------------------------
# ⛔ EVERY NUMBER HERE IS A PRINTED ONE. `printed_in` names the table or sentence; `verified_against`
# records that the digits were checked against the article PDF's TEXT LAYER and not only against a
# page raster, because a raster is exactly where an OCR-style slip happens and a wrong denominator
# is silent.
SERIES = [
    {
        "source_id": "chiusole2020",
        "n_total": 59,
        "printed_in": "TABLE 1 | Patients' characteristics — 'Primary Location (n. 59)' and "
                      "'Metastatic Sites (n. 26)'",
        "verified_against": "the text layer of the article PDF retrieved via "
                            "europepmc.org/articles/PMC7308468?pdf=render",
        "primary_site_counts": {
            "lower limb": 40, "upper limb": 6, "chest": 3, "abdomen": 7, "other": 3,
        },
        "extremity_strict": ["lower limb", "upper limb"],
        "extremity_inclusive_extra": [],
        "locoregional_treatment_already_given": {
            "printed_in": "TABLE 1 | Patients' characteristics — 'Locoregional Treatment'",
            "counts": {"radiation therapy": 23, "lung metastasectomy": 8,
                       "excision of local recurrence": 14, "radiofrequency ablation": 2},
            "⚠_denominator": "The table prints percentages against 47, not against 59 or 26, and "
                             "does not say what 47 is. The COUNTS are transcribed; the rates are "
                             "not, because a denominator nobody stated cannot be reconstructed.",
        },
        "metastatic": {
            "denominator": 26,
            "denominator_means": "patients with metastatic disease in this series",
            "counts_non_exclusive": {"lung": 23, "bone": 4, "other": 14},
            "⚠_non_exclusive": "23 + 4 + 14 = 41 over a denominator of 26, so a patient may be "
                               "counted in more than one row. A lung-CONFINED fraction cannot be "
                               "read off this table and must not be inferred from it.",
            "⛔_internal_discrepancy": "The running text of the same paper says 'the most frequent "
                                       "metastatic site was the lung (22 patients); 4 patients had "
                                       "bone metastases and 12 patients presented metastases in "
                                       "other sites'. TABLE 1 says 23 lung and 14 other. The two "
                                       "printed statements disagree by one and by two patients "
                                       "respectively. Recorded, NOT resolved — picking the "
                                       "convenient one would be a silent edit to somebody's data.",
        },
    },
    {
        "source_id": "masunaga2025",
        "n_total": 171,
        "printed_in": "Table 1 'Patient characteristics and clinical outcomes…' — 'Tumor site, "
                      "n (%)'; metastatic sites from the 'Patients with metastases at diagnosis' "
                      "paragraph",
        "verified_against": "the text layer of the article PDF retrieved via "
                            "europepmc.org/articles/PMC12398172?pdf=render",
        "primary_site_counts": {
            "lower limb": 100, "upper limb": 16, "trunk": 55,
        },
        "primary_site_subcounts": {
            "lower limb": {"thigh": 61, "knee": 17, "lower leg": 8, "ankle": 4, "foot": 10},
            "upper limb": {"upper arm": 6, "elbow": 3, "forearm": 2, "hand": 5},
            "trunk": {"perineum": 1, "intrathoracic": 1, "chest wall": 5, "neck": 1, "shoulder": 9,
                      "retroperitoneum": 3, "lumbar": 1, "groin": 8, "back": 4,
                      "abdominal wall": 4, "axilla": 3, "buttock": 15},
        },
        "extremity_strict": ["lower limb", "upper limb"],
        # ⛔ THE JUNCTIONAL SITES, AND WHY THEY ARE THE WHOLE UNCERTAINTY. Shoulder, groin, axilla
        # and buttock are filed under TRUNK by this series and are exactly the primaries a perfusion
        # service would argue about. They are 35 of 171 patients — larger than the sampling error on
        # either reading, which is why this artifact refuses to pick one.
        "extremity_inclusive_extra": ["shoulder", "groin", "axilla", "buttock"],
        "locoregional_treatment_already_given": {
            "printed_in": "'Patients with metastases at diagnosis' paragraph",
            "counts": {"metastasectomy": 8},
            "denominator": 29,
            "percent_printed": 27.6,
        },
        "metastatic": {
            "denominator": 29,
            "denominator_means": "patients with distant metastases AT DIAGNOSIS — a presenting "
                                 "cohort, not everyone who ever metastasised",
            "counts_non_exclusive": {"lung": 27, "peritoneal": 2},
            "regional_lymph_node_at_diagnosis": 6,
            "⭐_lung_confined_readable_here": "27 + 2 = 29 over a denominator of 29, so these two "
                                              "rows exhaust the cohort and 27/29 IS a lung-only "
                                              "fraction for THIS presenting cohort. It is one "
                                              "series' metastatic-at-diagnosis stratum and must not "
                                              "be quoted as a pooled distribution.",
        },
    },
]


def _extremity(series: dict, inclusive: bool) -> tuple[int, int]:
    counts = series["primary_site_counts"]
    n = sum(counts[k] for k in series["extremity_strict"])
    if inclusive:
        subs = series.get("primary_site_subcounts", {})
        for extra in series["extremity_inclusive_extra"]:
            for group in subs.values():
                if extra in group:
                    n += group[extra]
    return n, series["n_total"]


def _row(series: dict, inclusive: bool) -> dict:
    ev, dn = _extremity(series, inclusive)
    p, lo, hi = wilson(ev, dn)
    return {"source_id": series["source_id"], "events": ev, "denom": dn,
            "percent": round(100 * p, 1), "ci95_lo_percent": round(100 * lo, 1),
            "ci95_hi_percent": round(100 * hi, 1)}


def build() -> dict:
    out_series, pooled = [], {}
    for inclusive in (False, True):
        rows = [_row(s, inclusive) for s in SERIES]
        ev = sum(r["events"] for r in rows)
        dn = sum(r["denom"] for r in rows)
        p, lo, hi = wilson(ev, dn)
        per = [r["percent"] for r in rows]
        pooled["extremity_inclusive" if inclusive else "extremity_strict"] = {
            "definition": ("limb primaries plus the junctional girdle sites — shoulder, groin, "
                           "axilla and buttock — which one series files under trunk" if inclusive
                           else
                           "limb primaries only, as each series' own top-level category defines them"),
            "events": ev, "denom": dn, "percent": round(100 * p, 1),
            "ci95_lo_percent": round(100 * lo, 1), "ci95_hi_percent": round(100 * hi, 1),
            "estimator": "crude denominator-weighted proportion (POLICY-evidence §2.2)",
            "interval": "Wilson score, 95%",
            "per_cohort_percent": {r["source_id"]: r["percent"] for r in rows},
            "heterogeneity_range_percent": [min(per), max(per)],
            "⚠_heterogeneity_note": "The range is the honest signal; I² is deliberately not "
                                     "computed (POLICY-evidence §2.2).",
        }
    for s in SERIES:
        total = sum(s["primary_site_counts"].values())
        out_series.append({
            **{k: v for k, v in s.items() if k != "metastatic"},
            "primary_site_counts_sum": total,
            "⚠_sum_vs_n": ("the site counts exhaust the series" if total == s["n_total"]
                           else f"site counts sum to {total} against n={s['n_total']}"),
            "metastatic": s["metastatic"],
        })
    return {
        "_what": "Anatomical site of the primary tumour and of the metastases in extraskeletal "
                 "myxoid chondrosarcoma, transcribed from the primary reports of the open-access "
                 "series.",
        "_why": "emc-locoregional-eligibility.json records primary site as NOT computable and "
                "metastatic site as computable only from one free-text note, and names re-curation "
                "from the primary reports as the highest-value step the locoregional endpoint is "
                "waiting on.",
        "_not_medical_advice": "Nothing here is medical advice, and nothing here asserts efficacy, "
                               "safety, a therapeutic window or clinical readiness. An 'eligible "
                               "fraction' says who a strategy could be OFFERED to and nothing about "
                               "whether it would work.",
        "_generated_by": "research/modalities/emc_site_curation.py",
        "_method": {
            "estimator": "crude denominator-weighted proportions",
            "interval": "Wilson score, 95%",
            "contract": "systems/POLICY-evidence.md §2 (binding)",
            "⚠_what_is_pooled": "TWO series, both reporting a site distribution over their whole "
                                "cohort. They are non-overlapping (an Italian two-institution "
                                "series and a Japanese national registry study).",
            "⛔_the_inclusive_pool_is_NOT_symmetric": "Only one of the two series breaks out the "
                                "junctional sites at all. Chiusole reports 'chest 3, abdomen 7, "
                                "other 3' with no shoulder, groin, axilla or buttock row, so any "
                                "junctional primaries it contains are invisible and it contributes "
                                "ZERO extra patients to the inclusive reading. ⇒ The inclusive pool "
                                "applies a category widening to one series and not to the other, "
                                "which biases it DOWNWARD by an unknown amount. The per-cohort "
                                "column, not the pooled figure, is the honest object here.",
        },
        "⚠_these_denominators_DIFFER_from_the_registry_cohorts_AND_BOTH_ARE_RIGHT": {
            "_why_this_is_written_down": "A later reader will notice that this file says n=59 for "
                "chiusole2020 while the clinical registry's cohort says 49, and that it says n=171 "
                "for masunaga2025 while the registry carries 134 + 29 = 163. Neither is an error, "
                "and without this note somebody will 'fix' one of them.",
            "chiusole2020": "The registry cohort is keyed on the SURGICAL subset — Table 1's "
                "'Extension of Surgery (n. 49)'. A site distribution is reported over the whole "
                "series, 'Primary Location (n. 59)', which is the denominator a site fraction needs.",
            "masunaga2025": "The registry carries two strata, 'localised at diagnosis, surgically "
                "treated' (134) and 'metastatic at diagnosis' (29). Table 1's tumour-site column "
                "runs over the whole cohort of 171 — the 8 localised patients who had no surgery "
                "are outside the registry's first stratum and inside the paper's site table.",
            "⛔_the_rule": "An eligibility fraction takes the denominator its own question defines. "
                "A perfusion service asks about every patient with this disease, not only the ones "
                "somebody operated on.",
        },
        "⛔_the_category_boundary": (
            "Masunaga files shoulder (9), groin (8), axilla (3) and buttock (15) under TRUNK. Every "
            "one of those is a primary a perfusion service would argue about rather than refuse "
            "outright, and together they are 35 of 171 patients. Both readings are computed and "
            "NEITHER is called the answer: the gap between them is WIDER than the sampling interval "
            "on either, so the binding uncertainty in this quantity is a definition, not a sample "
            "size. ⛔ Anyone quoting a single extremity fraction for this disease is quoting a "
            "category boundary they did not state."),
        "⭐_local_therapy_of_metastases_is_already_being_given": (
            "Both series record it: masunaga, 8 of 29 patients presenting with distant metastases "
            "(27.6%) underwent metastasectomy; chiusole, 8 lung metastasectomies and 2 "
            "radiofrequency ablations among 59 patients, 26 of whom were metastatic. ⇒ "
            "RT-LUNG-DIRECTED's premise is not hypothetical — a lung-directed local strategy is the "
            "standard of care for a substantial minority of these patients already, and the route's "
            "question is whether perfusion, inhaled delivery or ablation extends it to patients "
            "surgery cannot reach. ⚠ Nothing here says any of it works: these are counts of what was "
            "DONE, with no comparator and no outcome attached."),
        "⛔_what_is_still_not_computable": {
            "lesion_burden": "no series prints per-patient lesion counts, so no oligometastatic "
                             "threshold fraction can be stated. Unchanged by this curation.",
            "time_to_metastasis": "printed as a median in one series (5.9 years, chiusole2020) and "
                                  "nowhere per patient.",
            "lung_confined_fraction_pooled": "readable in ONE series' presenting cohort (27/29) and "
                                             "NOT readable in the other, whose metastatic-site rows "
                                             "are non-exclusive and over-sum their denominator.",
            "the_other_nine_series": "not open access. Europe PMC returns no PMC record and "
                                     "isOpenAccess: N for all nine remaining candidate series, so "
                                     "their site tables are unreachable at $0.",
        },
        "series": out_series,
        "pooled_extremity_fraction": pooled,
    }


def check() -> int:
    if not os.path.exists(OUT):
        print(f"MISSING: {OUT}", file=sys.stderr)
        return 1
    with open(OUT, encoding="utf-8") as fh:
        committed = json.load(fh)
    if committed == build():
        print(f"OK: {os.path.relpath(OUT, HERE)} matches the generator")
        return 0
    print(f"STALE OR HAND-EDITED: {OUT} disagrees with the generator", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    art = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(art, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(art["pooled_extremity_fraction"], indent=2, ensure_ascii=False))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
