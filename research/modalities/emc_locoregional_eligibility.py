#!/usr/bin/env python3
"""The eligibility denominators the locoregional routes argue from — and the fields that do not exist.

⭐ WHY THIS EXISTS. PUB-LOCOREGIONAL says a disease that is extremity-primary, lung-metastasis-dominant
and slow enough for local control to matter is unusually well matched to physical treatment, and that
"without the eligibility arithmetic the paper would be an argument with no denominator". This computes
that arithmetic from the curated registry, under the repository's binding pooling contract
(systems/POLICY-evidence.md §2 — crude denominator-weighted proportions, Wilson 95%, non-overlapping
populations only, and a cohort's INCLUSION CRITERION never counted as its outcome).

⛔ AND ITS MOST IMPORTANT OUTPUT IS A GAP, NOT A NUMBER. Two of the three quantities the endpoint names
— primary ANATOMICAL SITE distribution and METASTATIC SITE distribution — are not curated fields on any
cohort in the registry. The endpoint's own `why_not_written` says the arithmetic "has not been
extracted", which reads as though extraction were the missing step. It is not: for those two the data
was never entered, so no extraction could produce them, and a paper that assumed otherwise would have
gone looking for a table that is not there. Which quantities ARE computable, and which are not, is
recorded explicitly below so the distinction survives into the manuscript.

⚠ CRUDE, MIXED FOLLOW-UP, HYPOTHESIS-GENERATING. These are during-follow-up proportions with censoring
ignored and follow-up lengths that differ between cohorts (POLICY-evidence §2.4). They are not survival
estimates and are not prognostic for any individual.

⛔ NOTHING HERE ASSERTS EFFICACY, SAFETY, A THERAPEUTIC WINDOW OR CLINICAL READINESS for any
locoregional, radiation or surgical intervention in this disease. An eligibility denominator says how
many patients a strategy could be OFFERED to if it worked. It says nothing about whether it works.

$0 — reads a committed artifact, stdlib only, runs anywhere.
"""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE)) if os.path.basename(
    os.path.dirname(HERE)) == "research" else os.path.dirname(os.path.dirname(HERE))
REGISTRY = os.path.join(os.path.dirname(HERE), "data", "emc-clinical-registry.json")
OUT = os.path.join(HERE, "emc-locoregional-eligibility.json")

# The three quantities PUB-LOCOREGIONAL names, and what the registry can actually answer for each.
# ⚠ This mapping is the point of the file. Do not delete a row because it is negative.
QUANTITIES = {
    "primary_anatomical_site_distribution": {
        "wanted_by": "RT-LIMB-PERFUSION — isolated limb perfusion is only offerable for an extremity "
                     "primary, so the eligible fraction IS the extremity fraction",
        # ⚠ `computable` IS A CLASSIFIER, NOT A SENTENCE. It was briefly set to prose here
        # ("not from the registry, and it no longer has to be") and CI caught it against the guard
        # that pins this field to True / False / "partially" — correctly, because a field a machine
        # reads is not a place to be eloquent. The nuance belongs in `why`, which is prose by design.
        # ⭐ AND THE VALUE FLIPS TO True: the question this field answers is whether the endpoint can
        # HAVE this quantity, not whether the registry happens to carry it. It can, from
        # emc-site-curation.json. ⚠ *Superseded, retained: False.*
        "computable": True,
        "why": "⛔ NO COHORT IN THE REGISTRY CARRIES A SITE FIELD, and that is still true. "
               "`overview.commonSites` is a prose list with no counts behind it, and a prose "
               "ordering cannot become a denominator. ⭐ RESOLVED ELSEWHERE 2026-08-25: the site "
               "tables were transcribed from the primary reports instead, and "
               "`emc-site-curation.json` now owns this quantity. ⚠ *Superseded, retained: "
               "\"computable: False\"* — which was a statement about the REGISTRY and kept being "
               "read as a statement about the literature.",
        "resolved_by": "research/modalities/emc-site-curation.json",
        "what_would_supply_it": "DONE for the two open-access series that print a site table "
                                "(chiusole2020 n=59, masunaga2025 n=171). The other nine candidate "
                                "series are not open access, so their site tables stay unreachable "
                                "at $0 — a paywall, not a missing extraction.",
    },
    "metastatic_site_distribution": {
        "wanted_by": "RT-LUNG-DIRECTED — a lung-directed strategy is offerable only to patients whose "
                     "metastases are lung-confined",
        # ⚠ Classifier, not a sentence — see the note on the row above. Still "partially", and the
        # reason that word survives a second curated series is in `why`.
        "computable": "partially",
        "why": "⚠ ONE COHORT CARRIES A LUNG-CONFINED READING AND IT IS A PRESENTING STRATUM. The "
               "metastatic-at-diagnosis stratum records 27 lung and 2 peritoneal on n = 29 — those "
               "two rows exhaust the cohort, so 27/29 IS a lung-only fraction there. ⭐ A SECOND "
               "SERIES WAS CURATED 2026-08-25 AND IT CANNOT BE ADDED: chiusole2020's metastatic-site "
               "rows are NON-EXCLUSIVE (23 lung + 4 bone + 14 other = 41 over a denominator of 26), "
               "so no lung-CONFINED fraction can be read off it, and the paper's own table and its "
               "running text disagree by one and two patients. ⛔ So the honest state is UNCHANGED "
               "in kind: one presenting cohort, not a pooled distribution.",
        "resolved_by": "research/modalities/emc-site-curation.json (partially)",
        "what_would_supply_it": "a series reporting metastatic sites as MUTUALLY EXCLUSIVE "
                                "categories, or patient-level data. Neither exists in the reachable "
                                "open-access set.",
    },
    "burden_and_timing": {
        "wanted_by": "RT-LUNG-DIRECTED — an oligometastatic threshold is a COUNT of lesions, and "
                     "time-to-metastasis decides whether a local-control strategy has a window",
        "computable": False,
        "why": "⛔ NO LESION COUNTS AND NO TIME-TO-METASTASIS ANYWHERE IN THE REGISTRY. Event counts "
               "and median follow-up exist; per-patient lesion burden and interval-to-metastasis do "
               "not. So the fraction meeting any conventional oligometastatic threshold is NOT "
               "computable here, and the route must stop naming it as an extraction.",
        "what_would_supply_it": "individual-patient data, which none of these series publishes",
    },
    "who_ever_metastasises": {
        "wanted_by": "the whole endpoint — the fraction of localised patients who ever develop distant "
                     "disease is the population any lung-directed or delaying strategy exists for",
        "computable": True,
        "why": "✅ Explicit integer {events, denom} on three non-overlapping poolable cohorts.",
        "what_would_supply_it": None,
    },
    "who_recurs_locally": {
        "wanted_by": "RT-LIMB-PERFUSION and RT-RT-INTENSIFY — both act on local control, so the local "
                     "recurrence rate is the size of the problem they address",
        "computable": True,
        "why": "✅ Explicit integer {events, denom} on four non-overlapping poolable cohorts.",
        "what_would_supply_it": None,
    },
}


def wilson(events: int, denom: int, z: float = 1.959963984540054):
    """Wilson score interval — POLICY-evidence §2.2 names it, and names why: it behaves at small n."""
    if denom == 0:
        return None, None, None
    p = events / denom
    d = 1 + z * z / denom
    centre = (p + z * z / (2 * denom)) / d
    half = z * math.sqrt(p * (1 - p) / denom + z * z / (4 * denom * denom)) / d
    return p, max(0.0, centre - half), min(1.0, centre + half)


def pool(cohorts, outcome):
    """Crude denominator-weighted pool over the `pool: true` cohorts that report `outcome`.

    ⛔ §2.1 rule 3 is enforced structurally, not by trusting the data: a cohort whose inclusion
    criterion IS the outcome is dropped by name, because its rate is 100% by construction and pooling
    it would silently inflate the estimate.
    """
    used, skipped = [], []
    for c in cohorts:
        rec = c.get(outcome)
        if not c.get("pool"):
            skipped.append((c["label"], "pool: false — " + str(c.get("contextReason") or "context")))
            continue
        # ⚠ THE INCLUSION-CRITERION CHECK RUNS FIRST, DELIBERATELY. Ordered after the missing-field
        # check it is a NO-OP on today's data — the metastatic-at-diagnosis cohort happens to carry no
        # metastasis counts, so the field check would exclude it first and the structural rule would
        # never fire, never be exercised, and never be seen to be wrong. It is the rule that MATTERS
        # (a 100%-by-construction rate silently inflating a pool), so it is the reason recorded, and
        # `tests/test_locoregional_eligibility.py` curates a count onto that cohort to prove it bites.
        if outcome == "metastasis" and (c.get("criteria") or {}).get("stage") == "distant":
            skipped.append((c["label"], "⛔ inclusion criterion IS the outcome (POLICY-evidence §2.1.3)"))
            continue
        if not isinstance(rec, dict) or "events" not in rec or "denom" not in rec:
            skipped.append((c["label"], f"no explicit integer {outcome} counts"))
            continue
        used.append(c)
    ev = sum(c[outcome]["events"] for c in used)
    dn = sum(c[outcome]["denom"] for c in used)
    p, lo, hi = wilson(ev, dn)
    per = {c["label"]: round(100 * c[outcome]["events"] / c[outcome]["denom"], 1) for c in used}
    rates = sorted(per.values())
    return {
        "outcome": outcome,
        "events": ev, "denom": dn,
        "percent": round(100 * p, 1) if p is not None else None,
        "ci95_lo_percent": round(100 * lo, 1) if lo is not None else None,
        "ci95_hi_percent": round(100 * hi, 1) if hi is not None else None,
        "interval": "Wilson score, 95%",
        "estimator": "crude denominator-weighted proportion, during-follow-up, censoring ignored "
                     "(POLICY-evidence §2.2, §2.4)",
        "cohorts_pooled": [c["label"] for c in used],
        "source_ids": sorted({c["sourceId"] for c in used}),
        "per_cohort_percent": per,
        "heterogeneity_range_percent": [rates[0], rates[-1]] if rates else None,
        "⚠_heterogeneity_note": "The range is the honest signal; I² is deliberately not computed "
                                "(POLICY-evidence §2.2). A wide range means the point estimate hides "
                                "real between-study variation.",
        "cohorts_excluded": {lbl: why for lbl, why in skipped},
        "dominance": (max(per, key=lambda k: dict(
            (c["label"], c[outcome]["denom"]) for c in used)[k]) if used else None),
    }


def main():
    with open(REGISTRY, encoding="utf-8") as fh:
        reg = json.load(fh)
    cohorts = reg["registry"]["cohorts"]
    cites = reg["registry"]["citations"]

    metastasis = pool(cohorts, "metastasis")
    recurrence = pool(cohorts, "recurrence")

    out = {
        "_what": "Eligibility denominators for the locoregional and radiation routes, pooled from the "
                 "curated EMC clinical registry under the repository's binding evidence contract.",
        "_no_clinical_claim": "⛔ Nothing here asserts efficacy, safety, a therapeutic window or "
                              "clinical readiness for any locoregional, radiation or surgical "
                              "intervention. An eligibility denominator says how many patients a "
                              "strategy could be offered to IF it worked.",
        "_method": {
            "contract": "systems/POLICY-evidence.md §2 (binding)",
            "estimator": "crude denominator-weighted proportions",
            "interval": "Wilson score, 95%",
            "heterogeneity": "range of per-cohort rates; I² deliberately not computed",
            "endpoint_kind": "during-follow-up proportions, mixed and differing follow-up, censoring "
                             "ignored — NOT survival estimates and NOT prognostic for an individual",
            "not_used": "the DerSimonian–Laird random-effects pooler in research/meta/meta-analysis.mjs "
                        "— POLICY-evidence's own warning is that quoting one where the other is meant "
                        "is a real error; this is the simple-proportion case its §2 governs",
        },
        "_source": "research/data/emc-clinical-registry.json (registry.cohorts, dataStatus: "
                   + str(reg["registry"].get("dataStatus")) + ")",
        "_generated_by": "research/modalities/emc_locoregional_eligibility.py",
        "⛔_what_the_registry_cannot_answer": QUANTITIES,
        "who_ever_metastasises": metastasis,
        "who_recurs_locally": recurrence,
        "citations_of_pooled_cohorts": {
            sid: {k: v for k, v in cites[sid].items()
                  if k in ("short", "title", "journal", "year", "pmid", "pmcid", "doi")}
            for sid in sorted(set(metastasis["source_ids"]) | set(recurrence["source_ids"]))
            if sid in cites},
        "_limits": [
            "⚠ ONE SERIES CONTRIBUTES THE LARGEST DENOMINATOR TO BOTH POOLS, which POLICY-evidence "
            "§2.2 requires be disclosed rather than buried in a weighted mean.",
            "The pooled series differ in era, referral pattern and follow-up. One is explicitly a "
            "consultation series, i.e. selected toward diagnostically difficult tumours, which is a "
            "selection this pooling cannot correct for.",
            "⛔ Distant metastasis and LOCAL recurrence are different endpoints with different "
            "clinical meaning, and one cohort reports locoregional recurrence specifically while "
            "others report recurrence without qualifying it. The pooled recurrence figure is "
            "therefore a mixture and is the weaker of the two.",
            "Crude proportions over mixed follow-up systematically UNDERSTATE lifetime event rates in "
            "a disease whose metastases appear over many years, which is precisely this disease. The "
            "direction of that bias is stated because it runs against the routes' own argument and "
            "must not be quietly omitted.",
        ],
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}")
    for key in ("who_ever_metastasises", "who_recurs_locally"):
        r = out[key]
        print(f"  {key:24} {r['events']:3}/{r['denom']:3} = {r['percent']}% "
              f"(95% CI {r['ci95_lo_percent']}–{r['ci95_hi_percent']}%), "
              f"{len(r['cohorts_pooled'])} cohorts, per-cohort range "
              f"{r['heterogeneity_range_percent']}")
    print("  ⛔ not computable from the registry: "
          + ", ".join(k for k, v in QUANTITIES.items() if v["computable"] is not True))


if __name__ == "__main__":
    main()
