#!/usr/bin/env python3
"""Europe PMC probe for modifiable HOST factors and EMC survival.

THE IDEA BEING TESTED (trimcrae, 2026-08-09): if a common, independently treatable
condition raises the chance of dying after an EMC diagnosis, then the drug for that
condition is a de-facto EMC survival drug for the patients who have it -- a GLP-1
receptor agonist for the obese, and so on. It needs no EMC biology and no new molecule.

WHY IT NEEDS ITS OWN RETRIEVAL. EMC's curated record contains NO host factor at all.
Every prognostic factor in the clinical registry is a property of the TUMOUR (size,
grade, fusion partner, stage, site) or of its TREATMENT (resection completeness), and
the per-patient schema carries age and sex and nothing else about the person. So the
question cannot be answered from this disease's own literature, and the first thing this
probe has to establish is that absence with a real hit count rather than an impression.

⛔ THE TWO COMPARTMENTS THIS PROBE FEEDS ARE NOT THE SAME QUESTION, and conflating them
is how a host-factor argument turns into a bad recommendation:

  A. Does the factor change EMC-SPECIFIC mortality? Almost certainly unmeasurable --
     no EMC data exists, and the sarcoma data is thin and heavily confounded.
  B. Does it change COMPETING mortality? Here the patients are ordinary people of their
     age and sex who happen to have a sarcoma, the deaths in question are NOT cancer
     deaths, and general-population evidence transfers with an assumption far weaker
     than any antitumour route in this repository requires.

The decomposition says compartment B is roughly two of every five deaths in the first
decade. That is the compartment this idea is actually strong in, and the queries below
are split so the two never share a citation.

⚠ AND THE CAUSAL HAZARDS ARE QUERIED DELIBERATELY, NOT AS AN AFTERTHOUGHT. A naive
reading of "BMI versus survival in cancer" reproduces the obesity paradox, in which low
weight looks lethal because disease causes weight loss rather than the other way round.
An analysis that missed that would recommend weight GAIN to cancer patients. The
reverse-causation, collider-bias and Mendelian-randomisation literature is therefore
retrieved alongside the association literature, so the bias registry is built from
sources rather than from memory.

⛔ THIS SCRIPT CLASSIFIES AND CONCLUDES NOTHING. It records what was asked, how many hits
came back and which papers they were.

Output: research/literature/emc-host-factor-probe.json
"""

from __future__ import annotations

import json
import math
import pathlib
import sys
import time
import urllib.parse
import urllib.request

SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OUT = pathlib.Path("research/literature/emc-host-factor-probe.json")
UA = "rare-cancers-research/1.0 (github.com/trimcrae/Rare-cancers; mailto:trimcrae@gmail.com)"

EMC = ('("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" '
       'OR "chordoid sarcoma")')

QUERIES: list[tuple[str, str, str]] = [
    # (key, query, what a result would mean)

    # --- (0) does EMC's own record contain ANY host factor? -------------------
    # Expected: near zero. That is the finding, and it is why everything below is a
    # transfer. An absence asserted without a hit count is an impression.
    ("emc_any_host_factor",
     f'{EMC} AND (obesity OR "body mass index" OR BMI OR diabetes OR smoking OR '
     f'comorbidity OR "performance status" OR sarcopenia OR frailty)',
     "any EMC paper relating a host characteristic to outcome"),
    ("emc_comorbidity_outcome",
     f'{EMC} AND (comorbidity OR "Charlson" OR "performance status" OR ECOG OR Karnofsky)',
     "EMC outcome analysed against comorbidity burden or performance status"),

    # --- (A) host factors and CANCER-SPECIFIC outcome, in sarcoma ------------
    # The weak compartment. Sarcoma cohorts are small and every estimate here is
    # confounded; the point of retrieving it is to size the uncertainty honestly.
    ("sarcoma_obesity_survival",
     '(sarcoma OR "soft tissue sarcoma") AND (obesity OR "body mass index" OR BMI) AND '
     '(survival OR mortality OR outcome OR prognosis)',
     "body mass and sarcoma-specific survival"),
    ("sarcoma_sarcopenia_body_composition",
     '(sarcoma OR "soft tissue sarcoma") AND (sarcopenia OR "skeletal muscle index" OR '
     '"body composition" OR "muscle mass") AND (survival OR prognosis OR outcome)',
     "CT-measured body composition as a sarcoma prognostic factor -- a real and growing literature"),
    ("sarcoma_comorbidity_survival",
     '(sarcoma OR "soft tissue sarcoma") AND ("Charlson" OR comorbidity OR "performance status") '
     'AND (survival OR mortality)',
     "comorbidity burden and sarcoma survival"),
    ("sarcoma_diabetes_metformin",
     '(sarcoma OR chondrosarcoma) AND (diabetes OR metformin OR hyperglycaemia OR hyperglycemia) '
     'AND (survival OR outcome OR prognosis)',
     "diabetes and metformin in sarcoma outcome"),
    ("sarcoma_smoking_outcome",
     '(sarcoma OR "soft tissue sarcoma") AND (smoking OR tobacco) AND (survival OR outcome OR complication)',
     "smoking and sarcoma outcome"),

    # --- (B) modifiable factors and NON-CANCER mortality ---------------------
    # The strong compartment. These are ordinary deaths in ordinary people, and the
    # evidence base is enormous compared with anything sarcoma-specific.
    ("glp1_all_cause_mortality",
     '(semaglutide OR tirzepatide OR liraglutide OR "GLP-1 receptor agonist") AND '
     '("all-cause mortality" OR "cardiovascular outcomes" OR survival) AND '
     '(randomized OR randomised OR trial)',
     "GLP-1 receptor agonists and all-cause or cardiovascular mortality -- the trial evidence behind the idea as posed"),
    ("glp1_cancer_patients",
     '(semaglutide OR tirzepatide OR "GLP-1 receptor agonist") AND (cancer OR oncology OR tumour OR tumor)',
     "GLP-1 agents specifically in cancer populations, including safety signals"),
    ("obesity_all_cause_mortality_cohort",
     '(obesity OR "body mass index") AND "all-cause mortality" AND (cohort OR "pooled analysis" OR '
     '"meta-analysis") AND adults',
     "the background association this whole argument rests on"),
    ("cancer_survivor_cardiovascular_mortality",
     '("cancer survivors") AND ("cardiovascular mortality" OR "cardiovascular disease") AND '
     '(competing OR "cause of death" OR excess)',
     "cardiovascular death as a competing cause in cancer survivors -- the compartment-B population"),
    ("statin_cardiovascular_primary_prevention",
     '(statin) AND ("primary prevention") AND ("all-cause mortality" OR "cardiovascular events") AND '
     '(randomized OR randomised OR "meta-analysis")',
     "a second modifiable competing-mortality lever with randomised evidence"),
    ("smoking_cessation_mortality_benefit",
     '("smoking cessation") AND ("all-cause mortality" OR survival) AND (cohort OR trial OR "meta-analysis")',
     "the largest single modifiable competing-mortality lever"),
    ("cardio_oncology_anthracycline_late_cardiac",
     '(anthracycline OR doxorubicin) AND (cardiotoxicity OR cardiomyopathy) AND '
     '("long-term" OR late OR survivors) AND (mortality OR incidence)',
     "the treatment-related half of competing mortality, which is modifiable by not giving the drug"),

    # --- (C) the causal-inference hazards ------------------------------------
    # ⛔ Retrieved on purpose. A host-factor analysis that skips these produces
    # confident, wrong, and potentially harmful advice.
    ("obesity_paradox_cancer",
     '("obesity paradox") AND (cancer OR oncology) AND (survival OR mortality)',
     "the single most likely way to get this analysis backwards"),
    ("reverse_causation_weight_loss_cancer",
     '("reverse causation" OR "reverse causality") AND (weight OR BMI OR "body mass") AND '
     '(cancer OR mortality)',
     "disease causing weight loss, rather than weight protecting against disease"),
    ("mendelian_randomization_bmi_cancer",
     '("Mendelian randomization" OR "Mendelian randomisation") AND (BMI OR adiposity) AND '
     '(cancer OR survival OR mortality)',
     "the design that separates a causal effect of adiposity from confounding"),
    ("collider_bias_index_event",
     '("collider bias" OR "index event bias" OR "selection bias") AND (prognosis OR survival) AND '
     '(cohort OR epidemiology)',
     "why conditioning on having the disease distorts risk-factor estimates"),
    ("immortal_time_bias_pharmacoepi",
     '("immortal time bias" OR "time-dependent bias") AND (pharmacoepidemiology OR "cohort study") AND '
     '(survival OR mortality)',
     "the bias that manufactures survival benefits for any drug taken by people who lived longer"),
    ("competing_risks_methods",
     '("competing risks") AND ("cumulative incidence" OR "subdistribution hazard" OR Fine AND Gray) AND '
     '(cancer OR oncology)',
     "the correct estimator for a two-compartment mortality model"),
    ("transportability_generalizability_trial",
     '(transportability OR generalizability OR "external validity") AND ("randomized trial" OR '
     '"randomised trial") AND ("target population" OR "real-world")',
     "the formal question of whether an effect measured elsewhere applies to this population"),
    ("healthy_user_bias_confounding_by_indication",
     '("healthy user" OR "healthy adherer" OR "confounding by indication") AND '
     '(pharmacoepidemiology OR "observational study")',
     "why statin and metformin survival associations are usually overstated"),
    # --- (E) the two absent factors, and the PRIMARY trials -------------------
    # Added 2026-09-04 (AUT-224, CYC-0106). The first run of this probe returned
    # relevance-ranked 2025-2026 syntheses, so emc-host-factor-inputs.json could
    # enter no landmark trial and nothing at all for diabetes or hypertension.
    # These queries sort by citation count so the primary randomised evidence
    # surfaces instead of the newest review of it. No trial is named: a hit is
    # what anchors, never a title typed from memory.
    # ⚠ THIRD FORM, AND THE SECOND DIAGNOSIS WAS WRONG (runs 33902213247 and
    # 33902748042, read from the committed artifacts). Run 1: every query written
    # `... AND sort_cited:y` with PUB_TYPE:"Randomized Controlled Trial" returned
    # hitCount 0. Run 2's two controls -- "blood pressure" AND PUB_TYPE:"Randomized
    # Controlled Trial", title-case and lowercase -- BOTH returned 71,557, so the
    # filter spelling was never the cause. What run 2 showed instead: every query
    # still written `AND sort_cited:y` returned dozens of hits on topics with
    # thousands (blood-pressure treatment vs all-cause mortality: 59, topped by AHA
    # statistics reports), so the sort flag joined with AND is being read as a
    # restricting term. Europe PMC documents the flag as a bare, space-separated
    # suffix on the query string. Block E now uses that form, and the two controls
    # below differ ONLY in how the flag is joined, so the next artifact records the
    # mechanism rather than another guess.
    ("bp_treatment_all_cause_mortality_cited",
     '(antihypertensive OR "blood pressure lowering" OR "blood pressure reduction") AND '
     '("all-cause mortality" OR "total mortality") AND '
     '(randomised OR randomized OR "meta-analysis" OR PUB_TYPE:"Randomized Controlled Trial") sort_cited:y',
     "the most-cited randomised or pooled evidence that treating blood pressure lowers all-cause death"),
    ("glycaemic_control_metformin_all_cause_mortality_cited",
     '(metformin OR "intensive glycemic control" OR "intensive glycaemic control" OR "glucose lowering") AND '
     '("all-cause mortality" OR "total mortality") AND '
     '(randomised OR randomized OR "meta-analysis" OR PUB_TYPE:"Randomized Controlled Trial") sort_cited:y',
     "the most-cited randomised or pooled evidence on glucose-lowering treatment and all-cause death"),
    ("glp1_obesity_cvot_primary_trial_cited",
     '(semaglutide OR tirzepatide OR liraglutide) AND (obesity OR overweight) AND '
     '("cardiovascular outcomes" OR "all-cause mortality" OR "cardiovascular death") AND '
     'PUB_TYPE:"Randomized Controlled Trial" sort_cited:y',
     "the primary obesity cardiovascular-outcome trials of incretin therapy, most-cited first"),
    ("statin_primary_prevention_pooled_trials",
     '(statin OR statins) AND "primary prevention" AND ("all-cause mortality" OR "vascular mortality") AND '
     '(PUB_TYPE:"Meta-Analysis" OR "individual participant data" OR "trialists") sort_cited:y',
     "the pooled primary-prevention statin trial evidence on death, not events"),
    ("smoking_cessation_mortality_cited",
     '("smoking cessation" OR "quit smoking" OR "stopped smoking") AND '
     '("all-cause mortality" OR survival) AND '
     '(randomised OR randomized OR "meta-analysis" OR "prospective cohort") sort_cited:y',
     "the most-cited cessation-and-mortality evidence, trial or cohort, in any population"),
    ("sarcoma_host_factor_survival_cited",
     'TITLE:sarcoma AND (obesity OR "body mass index" OR diabetes OR smoking OR '
     'comorbidity OR sarcopenia) AND (survival OR mortality) sort_cited:y',
     "the most-cited sarcoma host-factor survival analyses, title-restricted so citation sorting cannot surface unrelated records"),
    ("sort_flag_joined_with_and_control",
     '"blood pressure" AND "all-cause mortality" AND sort_cited:y',
     "CONTROL, not evidence: the sort flag joined with AND. Compare its hitCount with the next row; a large gap means AND turns the flag into a restricting term"),
    ("sort_flag_bare_suffix_control",
     '"blood pressure" AND "all-cause mortality" sort_cited:y',
     "CONTROL, not evidence: the same query with the flag as a bare suffix, the documented form; its hitCount should equal the unsorted count"),
    ("sort_flag_absent_control",
     '"blood pressure" AND "all-cause mortality"',
     "CONTROL, not evidence: the same query with no sort flag at all -- the reference hitCount the two rows above are read against"),
]

PAGE_SIZE = 25
SLEEP = 0.34


def get(url: str, tries: int = 3) -> str:
    last = ""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as fh:
                return fh.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(1.5 * (attempt + 1))
    print(f"  ! give up on {url}: {last}", file=sys.stderr)
    return ""


def search(query: str) -> dict:
    params = urllib.parse.urlencode({
        "query": query, "format": "json",
        "pageSize": str(PAGE_SIZE), "resultType": "core",
    })
    raw = get(f"{SEARCH}?{params}")
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def hit_row(r: dict) -> dict:
    return {
        "pmid": r.get("pmid"), "pmcid": r.get("pmcid"), "doi": r.get("doi"),
        "title": r.get("title"),
        "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title")
                   or r.get("journalTitle"),
        "year": r.get("pubYear"), "citedBy": r.get("citedByCount"),
        "isOpenAccess": r.get("isOpenAccess"),
    }


# ---------------------------------------------------------------------------
# Background mortality -- moved here after the first attempt failed
# ---------------------------------------------------------------------------
# ⛔ THE SSA LIFE TABLE WAS TRIED FIRST AND THE RUNNER COULD NOT REACH IT.
# Measured 2026-08-09, run 31334481362: `status: FETCH_FAILED` against
# https://www.ssa.gov/oact/STATS/table4c6.html, so the background-mortality check stayed
# NOT RUN and the competing-mortality decomposition still has no plausibility test.
# Superseded, retained: the SSA URL and the positional HTML parse written for it.
#
# The WHO Global Health Observatory serves the same quantity as JSON from a CDN, with no
# key and no scraping: indicator LIFE_0000000029 is nqx, the probability of dying within
# an age band. It is coarser -- five-year bands rather than single years -- and that is
# fine here, because the question is whether the observed gap is the SIZE age and sex
# explain, not what it is to three decimals.
#
# ⚠ IT IS DELIBERATELY A ONE-SIDED CHECK. A general-population table over-states
# background mortality for a cohort fit enough to have reached and survived a sarcoma
# diagnosis, so it can show the observed gap is too LARGE to be background -- which would
# mean the decomposition is a study-comparability artifact and must not be quoted -- and
# it cannot prove the gap IS background.
GHO = ("https://ghoapi.azureedge.net/api/LIFE_0000000029"
       "?$filter=SpatialDim%20eq%20%27USA%27%20and%20Dim1%20eq%20%27{sex}%27")
GHO_META = "https://ghoapi.azureedge.net/api/Indicator?$filter=IndicatorCode%20eq%20%27LIFE_0000000029%27"

AGE_BANDS = {"AGEGROUP_YEARS55-59": (55, 59), "AGEGROUP_YEARS60-64": (60, 64)}
BAND_YEARS = 5

# ⛔ THE FIRST VERSION OF THIS CALLED THE RETURNED VALUE `nqx` AND USED IT DIRECTLY, AND IT
# WAS A RATE, NOT A PROBABILITY. Measured 2026-08-09, run 31335519304: the fetch reported
# `status: OK` and produced a ten-year mortality from age 55 of 2.4%, which is roughly four
# times too low -- US male life expectancy at 55 is about 25 years, implying ~11-13%. The
# artifact was populated, internally consistent and plausible-looking, and wrong. That is
# CLAUDE.md section 4's exact failure: a populated field is not a measured one.
#
# Two fixes, because fixing only the arithmetic would leave the assumption in place:
#   (1) the indicator's NAME is now fetched from the API and recorded verbatim in the
#       artifact, and whether the value is a rate or a probability is decided FROM THAT
#       NAME rather than from anybody's recollection of what the code means;
#   (2) a known-answer sanity band rejects any result outside a range that basic
#       demography guarantees, so this class of error fails loudly instead of publishing.
SANITY_BAND = (0.05, 0.25)   # 10-year all-cause mortality from age 55, any developed country


def _looks_like_a_rate(indicator_name: str) -> bool:
    """Rate (nMx, deaths per person-year) versus probability (nqx). Decided from the
    published name, never assumed."""
    n = (indicator_name or "").lower()
    if "nqx" in n or "probability" in n:
        return False
    if "nmx" in n or "rate" in n or "per 1000" in n or "per 100 000" in n:
        return True
    return True    # ⚠ default to RATE: it is the reading the measured values support


def _band_probability(value: float, is_rate: bool) -> float:
    """A five-year death probability from whichever quantity the API actually serves."""
    if not is_rate:
        return value
    # Standard actuarial conversion from a constant hazard over the band.
    return 1.0 - math.exp(-BAND_YEARS * value)


def fetch_life_table(start_age: int = 55, years: int = 10,
                     male_fraction: float = 0.66) -> dict:
    # What the API actually serves, read rather than assumed.
    meta_raw = get(GHO_META)
    indicator_name = ""
    try:
        vals = json.loads(meta_raw).get("value", []) if meta_raw else []
        indicator_name = (vals[0].get("IndicatorName") or "") if vals else ""
    except (json.JSONDecodeError, IndexError, AttributeError):
        indicator_name = ""
    is_rate = _looks_like_a_rate(indicator_name)

    per_sex, notes = {}, {}
    for key, sex in (("male", "SEX_MLE"), ("female", "SEX_FMLE")):
        raw = get(GHO.format(sex=sex))
        if not raw:
            return {"status": "FETCH_FAILED", "source": GHO.format(sex=sex),
                    "why": "the WHO GHO life table could not be retrieved; the check stays NOT RUN"}
        try:
            rows = json.loads(raw).get("value", [])
        except json.JSONDecodeError:
            return {"status": "PARSE_FAILED", "source": GHO.format(sex=sex),
                    "why": "the GHO response was not JSON"}

        best = {}
        for r in rows:
            band = r.get("Dim2")
            if band not in AGE_BANDS or r.get("NumericValue") is None:
                continue
            if band not in best or (r.get("TimeDim") or 0) > (best[band].get("TimeDim") or 0):
                best[band] = r
        missing = [b for b in AGE_BANDS if b not in best]
        if missing:
            return {"status": "PARSE_FAILED", "source": GHO.format(sex=sex),
                    "bands_missing": missing,
                    "why": ("the bands this cohort needs were not in the response; no background "
                            "figure is asserted rather than extrapolating from the ones present")}
        surv = 1.0
        for band in AGE_BANDS:
            surv *= (1.0 - _band_probability(float(best[band]["NumericValue"]), is_rate))
        per_sex[key] = 1.0 - surv
        notes[key] = {b: {"raw_value": best[b]["NumericValue"],
                          "band_probability": round(_band_probability(
                              float(best[b]["NumericValue"]), is_rate), 5),
                          "year": best[b].get("TimeDim")} for b in AGE_BANDS}

    blended = male_fraction * per_sex["male"] + (1 - male_fraction) * per_sex["female"]

    lo, hi = SANITY_BAND
    if not (lo <= blended <= hi):
        return {
            "status": "IMPLAUSIBLE",
            "source": "WHO Global Health Observatory, indicator LIFE_0000000029",
            "indicator_name_as_published": indicator_name,
            "interpreted_as": "rate" if is_rate else "probability",
            "computed_blended_10y_mortality": round(blended, 4),
            "sanity_band": list(SANITY_BAND),
            "why": ("The computed ten-year all-cause mortality from age 55 falls outside a range "
                    "basic demography guarantees for any developed country, which means the "
                    "quantity was misinterpreted rather than that the population is unusual. "
                    "NOTHING is asserted; the background check stays NOT RUN. This guard exists "
                    "because the first version of this fetch reported OK with a figure four times "
                    "too low, and a populated field is not a measured one."),
        }

    return {
        "status": "OK",
        "source": "WHO Global Health Observatory, indicator LIFE_0000000029, USA",
        "indicator_name_as_published": indicator_name,
        "interpreted_as": "rate (converted to a band probability)" if is_rate else "probability",
        "conversion": ("5q = 1 - exp(-5 * m), the constant-hazard conversion from an annual death "
                       "rate to a five-year death probability") if is_rate else "used directly",
        "start_age": start_age, "horizon_years": years, "male_fraction": male_fraction,
        "cumulative_mortality_male": round(per_sex["male"], 4),
        "cumulative_mortality_female": round(per_sex["female"], 4),
        "cumulative_mortality_blended": round(blended, 4),
        "sanity_band_passed": list(SANITY_BAND),
        "bands_used": notes,
        "limits": (
            "A general-population period table, and an EMC cohort is not the general population: "
            "it is selected for having reached and survived a sarcoma diagnosis, so its non-cancer "
            "mortality is biased DOWNWARD relative to this figure. The check is therefore one-sided "
            "-- it can show the observed gap is too large to be background, and cannot prove the "
            "gap is background."
        ),
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = {}
    for key, q, means in QUERIES:
        print(f"[query] {key}", file=sys.stderr)
        data = search(q)
        res = (data.get("resultList") or {}).get("result", []) if data else []
        results[key] = {
            "query": q,
            "a_hit_would_mean": means,
            "hitCount": data.get("hitCount") if data else None,
            "retrieved": len(res),
            "hits": [hit_row(r) for r in res],
        }
        time.sleep(SLEEP)

    life_table = fetch_life_table()
    print(f"[life-table] {life_table.get('status')}", file=sys.stderr)
    emc_host = results.get("emc_any_host_factor", {}).get("hitCount")
    payload = {
        "_readme": (
            "Modifiable host factors and EMC survival. A citation index only -- no full text, "
            "no classification, no conclusion. Each entry records the query verbatim, what a "
            "hit would mean, the total hitCount and the top hits, so a claim can carry a real "
            "PMID and an absence can carry a real zero. THE QUERIES ARE IN FIVE BLOCKS AND THE "
            "BLOCKS ARE NOT INTERCHANGEABLE: (0) whether EMC's own record contains any host "
            "factor at all, (A) host factors versus cancer-specific outcome in sarcoma -- thin "
            "and confounded, (B) modifiable factors versus NON-cancer mortality -- where the "
            "patients are ordinary people and the evidence transfers far better, and (C) the "
            "causal-inference hazards that make a naive reading of block A actively harmful, and (E) "
            "the two factors the first run could not enter (blood pressure, glucose) plus the PRIMARY "
            "trials behind blocks A and B, restricted by publication type and sorted by citation count. "
            "Nothing here asserts that any intervention changes any outcome in EMC."
        ),
        "generated_by": "scripts/lit_host_factor_probe.py",
        "the_idea_under_test": (
            "If a common, independently treatable condition raises the chance of death after an "
            "EMC diagnosis, the drug for that condition is a de-facto EMC survival drug for the "
            "patients who have it. The claim is strongest where the deaths it prevents are NOT "
            "cancer deaths, because that is where evidence from the general population applies "
            "with the weakest assumption."
        ),
        "summary": {
            "n_queries": len(QUERIES),
            "n_zero": sum(1 for v in results.values() if v["hitCount"] == 0),
            "n_failed": sum(1 for v in results.values() if v["hitCount"] is None),
            "emc_host_factor_hitCount": emc_host,
            "background_mortality_status": life_table.get("status"),
            "emc_host_factor_reading": (
                "This is the number that decides whether any of block A can be answered in this "
                "disease directly, or whether every host-factor statement about EMC must be "
                "labelled a transfer. A low count is the expected result and is itself the "
                "finding -- it is the difference between 'nobody has looked' and 'looked and "
                "found nothing', which no amount of reasoning can supply."
            ),
        },
        "queries": results,
        "background_mortality": life_table,
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=1))
    if payload["summary"]["n_failed"] == len(QUERIES):
        print("::error::every query failed - the search did not run", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
