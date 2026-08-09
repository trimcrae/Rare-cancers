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

    emc_host = results.get("emc_any_host_factor", {}).get("hitCount")
    payload = {
        "_readme": (
            "Modifiable host factors and EMC survival. A citation index only -- no full text, "
            "no classification, no conclusion. Each entry records the query verbatim, what a "
            "hit would mean, the total hitCount and the top hits, so a claim can carry a real "
            "PMID and an absence can carry a real zero. THE QUERIES ARE IN FOUR BLOCKS AND THE "
            "BLOCKS ARE NOT INTERCHANGEABLE: (0) whether EMC's own record contains any host "
            "factor at all, (A) host factors versus cancer-specific outcome in sarcoma -- thin "
            "and confounded, (B) modifiable factors versus NON-cancer mortality -- where the "
            "patients are ordinary people and the evidence transfers far better, and (C) the "
            "causal-inference hazards that make a naive reading of block A actively harmful. "
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
            "emc_host_factor_reading": (
                "This is the number that decides whether any of block A can be answered in this "
                "disease directly, or whether every host-factor statement about EMC must be "
                "labelled a transfer. A low count is the expected result and is itself the "
                "finding -- it is the difference between 'nobody has looked' and 'looked and "
                "found nothing', which no amount of reasoning can supply."
            ),
        },
        "queries": results,
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=1))
    if payload["summary"]["n_failed"] == len(QUERIES):
        print("::error::every query failed - the search did not run", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
