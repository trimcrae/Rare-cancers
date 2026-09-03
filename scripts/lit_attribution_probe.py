#!/usr/bin/env python3
"""How does anyone decide a death was caused by the cancer?

THE QUESTION BEHIND IT (trimcrae, 2026-08-09). Every figure in the EMC mortality analysis
turns on the disease-specific / other-cause split, and the analysis has so far taken that
split from papers that assert it. Nobody has asked what the papers were DOING when they
assigned a cause -- what instrument, what rule, and how well it performs. If the
instrument is unreliable, every disease-specific survival figure in sarcoma inherits that
unreliability, including the ones this repository's own registry curates.

FOUR THINGS THIS RETRIEVES, and they are not interchangeable:

  (1) THE REGISTRY ALGORITHMS. SEER publishes a cause-specific death classification that
      combines the death certificate's underlying cause with the patient's tumour
      sequence and site. It is the nearest thing to a standard, it is documented, and its
      known failure modes are published.

  (2) DEATH CERTIFICATES THEMSELVES, and how badly they perform. This is the raw input to
      (1), it is completed by a clinician under time pressure, and its accuracy against
      autopsy or expert review is a measured quantity in cancer.

  (3) ⭐ RELATIVE AND NET SURVIVAL -- the methods that sidestep attribution ENTIRELY by
      comparing a cohort's observed survival against the survival expected in a matched
      general population. The excess is attributed to the disease without anyone ever
      deciding what any individual died of. This is the methodological answer to the
      defect the terminal-event corpus documents, which is why it is retrieved here
      rather than treated as a separate topic.

  (4) TRIAL DEATH ADJUDICATION. In an interventional setting a death gets a causality
      assessment against the intervention (CTCAE grade 5 and its attribution
      categories), which is a different instrument again, applied by different people to
      a different question.

⛔ CLASSIFIES AND CONCLUDES NOTHING. Records what was asked, how many hits, which papers.

Output: research/literature/emc-attribution-probe.json
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lit_probe_common as C  # noqa: E402

OUT = pathlib.Path("research/literature/emc-attribution-probe.json")

SARC = '(sarcoma OR "soft tissue sarcoma" OR chondrosarcoma)'

QUERIES = [
    # --- (1) registry algorithms -------------------------------------------
    ("seer_cause_specific_death_classification",
     '"cause-specific death classification" OR ("SEER" AND "cause of death" AND '
     '("cause-specific survival" OR "cancer-specific survival") AND (algorithm OR definition OR misclassification))',
     "the documented SEER rule for calling a death cancer-caused, and its failure modes"),
    ("cancer_specific_survival_misclassification",
     '("cancer-specific survival" OR "disease-specific survival") AND '
     '(misclassification OR bias OR "cause of death" AND (accuracy OR validity))',
     "how wrong the disease-specific endpoint is when the cause is misassigned"),
    ("registry_cause_of_death_coding_quality",
     '(registry OR registries) AND "cause of death" AND (coding OR quality OR accuracy OR concordance) '
     'AND (cancer OR neoplasm)',
     "the data-quality literature on the field every disease-specific figure rests on"),

    # --- (2) death certificates --------------------------------------------
    ("death_certificate_accuracy_cancer",
     '"death certificate" AND (accuracy OR validity OR agreement OR concordance) AND '
     '(cancer OR neoplasm OR malignancy)',
     "how well the raw input performs against autopsy or expert review"),
    ("death_certificate_autopsy_discrepancy",
     '(autopsy OR necropsy) AND "cause of death" AND (discrepancy OR disagreement OR error)',
     "the reference-standard comparison, where one exists at all"),

    # --- (3) the methods that avoid attribution ----------------------------
    ("relative_survival_methods",
     '("relative survival" OR "net survival") AND (methods OR estimator OR "Ederer" OR "Hakulinen" OR '
     '"Pohar Perme")',
     "the estimator that needs no cause of death -- this analysis's methodological spine"),
    ("net_survival_pohar_perme",
     '("Pohar Perme" OR "unbiased estimator of net survival" OR "net survival") AND '
     '(population-based OR "cancer registry")',
     "the modern unbiased net-survival estimator specifically"),
    ("excess_mortality_modelling",
     '("excess mortality" OR "excess hazard") AND (model OR modelling OR modeling) AND '
     '("cancer registry" OR population-based)',
     "excess-hazard regression, the modelled form of the same idea"),
    ("relative_survival_rare_cancer",
     '("relative survival" OR "net survival") AND ("rare cancer" OR "rare cancers" OR RARECARE)',
     "whether the method has been applied at the sample sizes a rare cancer actually has"),
    ("life_table_expected_survival_choice",
     '("expected survival" OR "life table") AND ("relative survival") AND (Ederer OR Hakulinen OR method)',
     "which expected-survival convention to use, which changes the answer"),

    # --- (4) trial adjudication --------------------------------------------
    ("ctcae_grade5_attribution",
     '(CTCAE OR "common terminology criteria") AND (attribution OR causality) AND '
     '(death OR "grade 5" OR "fatal")',
     "how an interventional trial decides a death was treatment-caused"),
    ("adjudication_committee_cause_of_death",
     '("adjudication committee" OR "endpoint adjudication" OR "clinical events committee") AND '
     '"cause of death"',
     "the most rigorous instrument that exists, and what it costs to run"),

    # --- (5) does sarcoma have any of this? --------------------------------
    ("sarcoma_cause_of_death_attribution",
     f'{SARC} AND "cause of death" AND (attribution OR classification OR "disease-specific" OR competing)',
     "whether the sarcoma literature has ever examined its own cause attribution"),
    ("sarcoma_registry_cause_of_death_field",
     '(RARECARE OR EUROCARE OR NETSARC OR "National Bone and Soft Tissue Tumor Registry" OR '
     '"US Sarcoma Collaborative" OR "sarcoma registry") AND (survival OR "cause of death" OR outcome)',
     "the named registries that could in principle answer this for sarcoma"),
    ("sarcoma_relative_survival",
     f'{SARC} AND ("relative survival" OR "net survival" OR "excess mortality")',
     "whether anyone has run the attribution-free method on this disease class"),
    ("sarcoma_competing_risk_analysis",
     f'{SARC} AND ("competing risk" OR "competing risks" OR "cumulative incidence function")',
     "prior competing-risk work in sarcoma, which is the design this analysis approximates"),
    ("emc_cause_attribution",
     '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma") AND '
     '("cause of death" OR "disease-specific survival" OR "died of disease" OR "competing")',
     "anything at all in EMC specifically -- expected to be very thin"),
]


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    index = C.run_index(QUERIES)
    summary = C.summarise(index)
    payload = {
        "_readme": (
            "How a death gets called cancer-caused, and how well that works. A citation index "
            "only -- no full text, no classification, no conclusion. FIVE BLOCKS, NOT "
            "INTERCHANGEABLE: (1) registry algorithms such as SEER's cause-specific death "
            "classification, (2) the death certificates those algorithms consume and their "
            "measured accuracy, (3) relative and net survival, which estimate disease-attributable "
            "mortality WITHOUT deciding any individual's cause and are therefore the "
            "methodological answer to the defect this project documented, (4) trial death "
            "adjudication, a different instrument for a different question, and (5) whether the "
            "sarcoma and EMC literatures contain any of it. Nothing here asserts that any "
            "attribution in this repository is right or wrong; it establishes what the "
            "instruments are so that claim can be made from sources."
        ),
        "generated_by": "scripts/lit_attribution_probe.py",
        "why_it_matters_here": (
            "Every disease-specific survival figure this project quotes -- including the "
            "stratified antitumour ceiling, which is its headline -- inherits whatever error the "
            "cause-assignment instrument carries. An analysis that reports the ceiling without "
            "characterising that instrument is quoting a number more precisely than its input "
            "supports."
        ),
        "summary": summary,
        "queries": index,
    }
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))
    if summary["n_failed"] == summary["n_queries"]:
        print("::error::every query failed - the search did not run", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
