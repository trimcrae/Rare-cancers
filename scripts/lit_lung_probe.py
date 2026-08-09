#!/usr/bin/env python3
"""Lung-directed options for a lung-metastasis-dominant sarcoma.

⚠ THE PREMISE IS CONDITIONAL AND THE CONDITION IS NOT YET SETTLED. This retrieval was
commissioned on "if lung failure is the primary driver, research lung treatments". At the
time of writing, the terminal-event corpus has 28 mechanism-naming sentences out of 577,
and they are mixed. That respiratory failure from progressive pulmonary metastases is the
dominant mechanism is an EXPECTATION drawn from EMC's lung-dominant metastatic pattern --
30 to 50 percent distant metastasis, mostly lung -- and not a measurement. The
classification settles it. If the corpus does not support the premise, this retrieval
still stands as the evidence base for a route the portfolio already carries, and the
paper says the premise failed rather than quietly keeping the section.

⛔ THE LADDER SPANS TWO DIFFERENT KINDS OF INTERVENTION AND THE BOUNDARY IS LOAD-BEARING.

  TUMOUR-DIRECTED, acting on the metastases themselves: metastasectomy, stereotactic
  radiotherapy, percutaneous ablation, isolated lung perfusion, inhaled chemotherapy.
  These belong to the existing locoregional and delivery families. They can extend life
  by removing disease and they are NOT supportive care.

  SYMPTOM-DIRECTED, acting on the consequences: airway obstruction, pleural effusion,
  breathlessness, deconditioning, hypoxia. These are the mortality-mechanism family's own
  and they make no claim on the tumour.

Both are retrieved because a patient dying of progressive lung disease may be a candidate
for either, at different times. Conflating them would let evidence for metastasectomy --
which is real, and which the EMC record already carries -- silently license a claim about
supportive care, or the reverse.

⛔ CLASSIFIES AND CONCLUDES NOTHING.

Output: research/literature/emc-lung-probe.json
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lit_probe_common as C  # noqa: E402

OUT = pathlib.Path("research/literature/emc-lung-probe.json")

EMC = ('("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" '
       'OR "chordoid sarcoma")')
SARC = '(sarcoma OR "soft tissue sarcoma")'

QUERIES = [
    # --- (0) is the premise true? -------------------------------------------
    ("sarcoma_respiratory_failure_terminal",
     f'{SARC} AND ("pulmonary metastases" OR "lung metastases") AND '
     f'("respiratory failure" OR "cause of death" OR terminal OR "end of life")',
     "whether progressive lung metastasis is documented as the terminal mechanism in sarcoma"),
    ("emc_pulmonary_burden_natural_history",
     f'{EMC} AND ("pulmonary metastas*" OR "lung metastas*") AND '
     f'(indolent OR "slow growing" OR "natural history" OR "growth rate" OR "doubling time")',
     "how fast EMC lung metastases actually progress, which determines whether local therapy can keep up"),

    # --- (A) TUMOUR-DIRECTED: remove or ablate the metastases ---------------
    ("sarcoma_pulmonary_metastasectomy",
     f'{SARC} AND ("pulmonary metastasectomy" OR "lung metastasectomy") AND '
     f'(survival OR outcome OR "repeat" OR reoperation)',
     "the standard of care for resectable sarcoma lung metastases, and repeat resection"),
    ("emc_metastasectomy_specific",
     f'{EMC} AND (metastasectomy OR "resection of metastases" OR "surgical resection")',
     "EMC-specific metastasectomy evidence, which the clinical registry already partly carries"),
    ("sarcoma_sbrt_lung_metastases",
     f'{SARC} AND ("stereotactic body radiotherapy" OR SBRT OR SABR OR "stereotactic ablative") AND '
     f'(lung OR pulmonary) AND (metastas*)',
     "the non-surgical ablative option for patients who cannot have surgery"),
    ("sarcoma_percutaneous_ablation_lung",
     f'{SARC} AND ("radiofrequency ablation" OR "microwave ablation" OR cryoablation OR '
     f'"percutaneous ablation") AND (lung OR pulmonary)',
     "image-guided ablation, repeatable and lower-morbidity than resection"),
    ("oligometastatic_local_therapy_randomised",
     '(oligometastatic OR oligometastases) AND ("local therapy" OR SABR OR metastasectomy) AND '
     '(randomized OR randomised) AND (survival OR "overall survival")',
     "the randomised evidence that treating limited metastases changes survival at all"),
    ("isolated_lung_perfusion_inhaled_chemo",
     '("isolated lung perfusion" OR "inhaled chemotherapy" OR "aerosolized chemotherapy" OR '
     '"aerosolised chemotherapy") AND (sarcoma OR "pulmonary metastases")',
     "regional delivery, already carried as a route here"),

    # --- (B) SYMPTOM-DIRECTED: the consequences of lung burden --------------
    ("malignant_pleural_effusion_management",
     '"malignant pleural effusion" AND ("indwelling pleural catheter" OR pleurodesis OR talc) AND '
     '(randomized OR randomised OR survival OR "breathlessness")',
     "the one lung complication with a genuinely randomised management literature"),
    ("malignant_airway_obstruction_stent",
     '("central airway obstruction" OR "malignant airway" OR endobronchial) AND '
     '(stent OR bronchoscopy OR laser OR "rigid bronchoscopy") AND (malignan* OR tumour OR tumor)',
     "airway rescue, which is acute and can be definitive for a specific patient"),
    ("cancer_breathlessness_management",
     '(breathlessness OR dyspnoea OR dyspnea) AND (cancer OR malignan*) AND '
     '(opioid OR "handheld fan" OR oxygen OR "non-pharmacological") AND (randomized OR randomised OR trial)',
     "the symptom itself, where randomised evidence exists and is mostly about quality of life"),
    ("home_oxygen_niv_cancer",
     '("home oxygen" OR "long-term oxygen" OR "non-invasive ventilation" OR NIV) AND '
     '(cancer OR malignan* OR "advanced disease") AND (survival OR breathlessness OR outcome)',
     "whether respiratory support changes anything beyond comfort in malignant lung disease"),
    ("pulmonary_rehabilitation_cancer",
     '("pulmonary rehabilitation" OR "exercise training") AND (lung OR pulmonary) AND '
     '(cancer OR metastas*) AND (capacity OR breathlessness OR survival)',
     "deconditioning, which is modifiable and rarely addressed in sarcoma"),
    ("lymphangitic_carcinomatosis",
     '("lymphangitic carcinomatosis" OR "lymphangitis carcinomatosa") AND (management OR treatment OR prognosis)',
     "the diffuse pattern that local therapy cannot address and that kills fastest"),
    ("pulmonary_embolism_cancer_lung_metastases",
     '("pulmonary embolism") AND (cancer OR malignan*) AND (incidence OR mortality OR prophylaxis)',
     "an acute respiratory death that is preventable, unlike progressive tumour burden"),

    # --- (C) how the endpoint would even be measured ------------------------
    ("lung_function_metastatic_burden",
     '("pulmonary function" OR spirometry OR "lung function") AND ("pulmonary metastases" OR '
     '"metastatic burden") AND (decline OR correlation OR predictor)',
     "whether lung burden maps onto measurable respiratory decline, which any such endpoint needs"),
]


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    index = C.run_index(QUERIES)
    summary = C.summarise(index)
    payload = {
        "_readme": (
            "Lung-directed options for a lung-metastasis-dominant sarcoma. A citation index only. "
            "⚠ COMMISSIONED ON A PREMISE THAT WAS NOT YET ESTABLISHED WHEN IT RAN: that respiratory "
            "failure from progressive pulmonary metastases is EMC's dominant terminal mechanism. "
            "That is an expectation from the metastatic pattern, not a measurement, and the "
            "terminal-event classification settles it. THE THREE BLOCKS ARE NOT INTERCHANGEABLE: "
            "(A) TUMOUR-DIRECTED interventions act on the metastases themselves and belong to the "
            "locoregional and delivery families -- they are not supportive care; (B) "
            "SYMPTOM-DIRECTED interventions act on the consequences and make no claim on the "
            "tumour; (C) measurement, without which no endpoint exists. Conflating (A) and (B) "
            "would let metastasectomy evidence license a supportive-care claim or the reverse."
        ),
        "generated_by": "scripts/lit_lung_probe.py",
        "premise_status": (
            "CONDITIONAL. Settled by the terminal-event classification, not by this retrieval. If "
            "the corpus does not support respiratory failure as the dominant mechanism, this index "
            "remains the evidence base for routes the portfolio already carries, and the paper "
            "reports that the premise failed rather than keeping the section anyway."
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
