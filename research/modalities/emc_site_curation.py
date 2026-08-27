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

⭐ EXTENDED 2026-08-27. Two more primary reports were read at $0 and the file's own claim that the
remaining nine candidate series were unreachable was WITHDRAWN as a licence/access conflation — see
`⚠_SUPERSEDED_the_other_nine_series`. bishop2019 (n=41) joins the site pool; drilon2008 is recorded
as context and pooled into nothing, because its site distribution is printed only as percentages.

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
                            "europepmc.org/articles/PMC12398172?pdf=render; re-verified 2026-08-27 "
                            "against the PMC full-text record PMC12398172 (PMID 40885991), which "
                            "confirmed every site subcount and corrected the metastatic-site "
                            "reading",
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
            "⛔_CORRECTED_2026_08_27_this_is_NOT_a_lung_only_fraction": "⚠ *Superseded, retained: "
                "\"27 + 2 = 29 over a denominator of 29, so these two rows exhaust the cohort and "
                "27/29 IS a lung-only fraction for THIS presenting cohort.\"* The primary text was "
                "re-read on 2026-08-27 (PMC12398172, PMID 40885991) and its sentence is: 'A total "
                "of 29 patients had distant metastases at the time of diagnosis. Of these, 27 "
                "patients HAD LUNG METASTASES, and two had peritoneal dissemination.' ⛔ 'Had lung "
                "metastases' is an INVOLVEMENT statement, not a confinement statement, and the "
                "paper never says the 27 had no other site. The rows summing to 29 shows the "
                "categories were assigned one per patient; it does not show the assignment means "
                "lung-ONLY. ⇒ 27/29 is an UPPER BOUND on the lung-confined fraction in this "
                "presenting stratum, and quoting it as a lung-only fraction overstates it. See "
                "`lung_confined_readings`.",
            "⛔_WHY_THE_PMID_IS_RECORDED_HERE_AND_NOT_IN_THE_REGISTRY": "The registry's "
                "masunaga2025 citation carries a PMCID and a DOI but no PMID, and PMID 40885991 is "
                "confirmed above. It was NOT added to research/data/emc-clinical-registry.json, and "
                "the reason is a constraint worth carrying: that file is inside the inventory of "
                "research/manuscripts/aso/fusion-junction-aso-archive-manifest.json, the DOI-"
                "deposited archive (10.5281/zenodo.22061075). ⛔ ANY byte change to it turns the "
                "manifest gate red and forces a re-stamp of a deposited artifact — measured "
                "2026-08-27: a one-line insertion moved the registry from 99,912 to 99,940 bytes "
                "and the archive_content_digest with it. Re-stamping a deposit is not a side effect "
                "a curation step gets to cause, so the identifier lives here, where nothing is "
                "deposited. ⚠ The citation already resolves by PMCID and DOI, so nothing is lost.",
            "⭐_what_the_re_read_did_confirm": "Every site subcount transcribed above was checked "
                "against the same full text and matches: lower limb 61+17+8+4+10 = 100, upper limb "
                "6+3+2+5 = 16, trunk 1+1+5+1+9+3+1+8+4+4+3+15 = 55, and 100+16+55 = 171. The 2026-"
                "08-25 transcription of this table is independently verified.",
            "metastasectomy_breakdown": "'Eight patients (27.6%) underwent metastasectomy, "
                "including six, one, and one who underwent lung, bone, and lymph node resections, "
                "respectively.' ⇒ six LUNG metastasectomies among 29 patients presenting with "
                "distant disease. ⚠ A count of what was done, with no comparator and no outcome.",
        },
    },
    {
        "source_id": "bishop2019",
        "n_total": 41,
        "printed_in": "Results, 'Patient and Tumor Characteristics' — the anatomical breakdown "
                      "printed in the paragraph that introduces Table 1 ('Patient and tumor "
                      "characteristics are listed in [Table 1]'); metastatic sites from the "
                      "'Patterns of Disease Recurrence' paragraph",
        "verified_against": "the PMC full-text record PMC7771031 (PMID 31436747), retrieved "
                            "through the NCBI PMC full-text API",
        "⭐_why_this_series_is_here_at_all": "This artifact previously recorded that the other nine "
            "candidate series were 'not open access … so their site tables are unreachable at $0'. "
            "That claim conflated a LICENCE with an ACCESS ROUTE. The clinical registry itself "
            "carries `pmcid: PMC7771031` for this source next to `openAccess: false`, and the PMC "
            "full-text record serves the whole article body. ⛔ The correct test for reachability "
            "is whether a full-text record exists, not whether the licence is an open one.",
        "⚠_licence": "The PubMed/PMC copyright endpoint returns no licence record for PMID "
                     "31436747 (source: not_available), so the licence is UNKNOWN. Only factual "
                     "counts are transcribed here; no article text is reproduced.",
        "primary_site_counts": {
            "lower extremity": 22, "upper extremity": 10, "trunk": 8, "neck": 1,
        },
        # ⛔ THE SUBSITE ROWS DO NOT SUM TO THIS SERIES' OWN GROUP TOTALS, so they are recorded and
        # used for NOTHING. They are kept out of `primary_site_subcounts` deliberately: that key
        # feeds the inclusive reading, and an addend drawn from an internally inconsistent list
        # would put an unresolved discrepancy inside a pooled fraction.
        "⛔_printed_subsite_rows_that_do_not_sum": {
            "lower extremity": {"thigh": 14, "knee": 2, "leg": 2, "ankle/foot": 3, "groin": 1},
            "upper extremity": {"shoulder": 1, "upper arm": 3, "elbow": 1, "forearm": 3},
            "trunk": {"chest wall": 2, "intrathoracic": 1, "superficial abdomen": 1, "pelvis": 2,
                      "buttocks": 4},
            "⚠_the_discrepancy": "The lower-extremity subsites sum to 22 and match their group. "
                "The upper-extremity subsites sum to 8 against a printed group total of 10, and the "
                "trunk subsites sum to 10 against a printed group total of 8 — the two errors are "
                "equal and opposite. The GROUP totals are the self-consistent set: 22 + 10 + 8 + 1 "
                "= 41 exhausts the cohort and matches the printed percentages (54%, 24%, 20%, 2% "
                "of 41). RECORDED, NOT RESOLVED — one rendering of one article cannot say whether "
                "the slip is the paper's or the transcription channel's, and picking the "
                "convenient reading would be a silent edit to somebody's data.",
            "⛔_consequence": "This series therefore contributes ZERO patients to the inclusive "
                "extremity reading, exactly as chiusole2020 does, and for a different reason.",
            "⚠_and_its_strict_reading_is_already_slightly_inclusive": "Under this series' own "
                "top-level categories, groin sits inside LOWER EXTREMITY and shoulder inside UPPER "
                "EXTREMITY — the two sites masunaga2025 files under TRUNK. The strict pool takes "
                "each series' own category boundary, so this row's 32 is drawn a shade wider than "
                "masunaga's 116. That is the same category boundary this artifact exists to expose, "
                "now visible BETWEEN series rather than only within one.",
        },
        "extremity_strict": ["lower extremity", "upper extremity"],
        "extremity_inclusive_extra": [],
        "locoregional_treatment_already_given": {
            "printed_in": "'Treatment' and 'Outcomes After Relapse' paragraphs",
            "counts": {"combined surgery and radiotherapy": 33, "surgery alone": 8,
                       "surgical resection of metastases": 5},
            "⚠_denominator": "The first two are over n=41 and sum to it. The metastasectomy count "
                             "is over the 13 patients who recurred distantly, not over 41.",
        },
        "metastatic": {
            "denominator": 13,
            "denominator_means": "patients who DEVELOPED distant metastases during follow-up in a "
                                 "cohort that was LOCALISED at diagnosis — an incidence cohort, "
                                 "not a presenting stratum",
            "counts_non_exclusive": {"lung": 12, "bone": 1},
            "⭐_lung_partition_readable_here": "The sentence reads 'Thirteen patients (32%) "
                "developed distant metastases - of which all but one patient (bone) recurred "
                "within the lung (n=12, 92%)'. 12 + 1 = 13 over a denominator of 13, so the rows "
                "exhaust the cohort and this IS an exclusive partition. ⚠ It partitions patients "
                "at the point of distant recurrence and says nothing about whether the 12 stayed "
                "lung-only afterwards, so it is an UPPER BOUND on a lung-confined fraction rather "
                "than a measurement of one — see `lung_confined_readings`.",
        },
    },
]

# ---------------------------------------------------------------------------
# context that may NOT be pooled (POLICY-evidence §2.1.2) but must not be dropped
# ---------------------------------------------------------------------------
CONTEXT_NOT_POOLED = [
    {
        "source_id": "drilon2008",
        "pmid": "18951519",
        "pmcid": "PMC2779719",
        "doi": "10.1002/cncr.23978",
        "n_total": 86,
        "verified_against": "the PMC full-text record PMC2779719, retrieved through the NCBI PMC "
                            "full-text API",
        "⛔_why_not_pooled": "PERCENTAGE-ONLY. The site distribution is printed as 'approximately "
            "62% … lower extremities; 17% … upper extremities; 13% … abdomen, retroperitoneum, or "
            "pelvis; and 8% … other areas', with the integer counts living in a table this channel "
            "does not render. POLICY-evidence §2.1.2 forbids deriving counts from a published "
            "percentage, so this series contributes to NO pooled fraction here.",
        "primary_site_percentages_printed": {
            "lower extremities": 62, "upper extremities": 17,
            "abdomen, retroperitoneum, or pelvis": 13, "other": 8,
        },
        "⚠_this_reading_was_already_in_the_repository_and_was_being_read_wrongly": "The 63% "
            "appears in research/literature/emc-rt-lung-mets-findings.json, where it is described "
            "as 'corroborated at 93% of the metastatic-at-presentation subgroup in another' "
            "series. That word is withdrawn there: 93% is an INVOLVEMENT figure and belongs beside "
            "this series' own 80% first-site-lung figure, not beside its 63% confined figure. The "
            "number was not the missing thing; the distinction was.",
        "⭐_the_lung_confined_sentence": "This is the ONLY series in the reachable set that "
            "separates lung-CONFINED from lung-INVOLVED in its own words: 'The first site of "
            "metastasis was the lung in 80% of cases (63% with metastasis confined to the lungs "
            "and 17% with metastasis at other sites concurrent with lung disease).' The metastatic "
            "denominator is itself a percentage — 'A total of 34% of patients were either "
            "diagnosed with or progressed to metastatic disease' — so no integer fraction is "
            "readable and none is reconstructed.",
        "⚠_internal_discrepancy": "The abstract says 87 patients and the Results say '86 "
            "evaluable patients'; the clinical registry carries 87. Recorded, not resolved.",
        "⭐_an_open_item_closed_in_passing": "research/literature/emc-rt-lung-mets-findings.json "
            "records that this series' PMID was NOT confirmed by its probe and 'must not be "
            "written into any manuscript until it is'. It is confirmed here: PMID 18951519, "
            "PMCID PMC2779719, DOI 10.1002/cncr.23978, Cancer 2008, Memorial Sloan-Kettering and "
            "the Royal Marsden, patients treated 1975-2006, data censored 2008-03-01 — retrieved "
            "from PubMed, not from recollection.",
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
            "⚠_what_is_pooled": "THREE series, each reporting a site distribution over its whole "
                                "cohort: an Italian/French two-institution series (n=59), a "
                                "Japanese national registry study (n=171) and a US "
                                "single-institution series (n=41). POLICY-evidence §2.3 names "
                                "exactly this pairing — 'a Japanese registry and a US single "
                                "institution' — as distinct populations that may be pooled.",
            "⭐_why_bishop2019_is_pooled_HERE_and_pool_false_in_the_REGISTRY": "The clinical "
                                "registry marks bishop2019 `pool: false` with "
                                "`contextReason: population-overlap (US single institution; likely "
                                "within SEER / US Sarcoma Collaborative)`. That exclusion bites "
                                "only where an overlap PARTNER is inside the same pool, and "
                                "neither SEER nor the US Sarcoma Collaborative contributes a site "
                                "distribution to this one. ⛔ Pool membership is decided per pool, "
                                "not once per source. The registry's recurrence and metastasis "
                                "pools do contain ussc2022, so its flag stands unchanged there.",
            "⛔_the_inclusive_pool_is_NOT_symmetric": "Only ONE of the three series contributes "
                                "junctional patients to the inclusive reading, and the other two "
                                "are silent for two DIFFERENT reasons. Chiusole reports 'chest 3, "
                                "abdomen 7, other 3' with no shoulder, groin, axilla or buttock "
                                "row, so any junctional primaries it contains are invisible. "
                                "Bishop DOES print a buttock row (4) but its subsite rows do not "
                                "sum to its own group totals, so no addend can be taken from them "
                                "— and it already files groin and shoulder inside its limb groups, "
                                "so part of the widening is baked into its strict count instead. "
                                "⇒ The inclusive pool applies a category widening to one series "
                                "and not to the other two, which biases it DOWNWARD by an unknown "
                                "amount. The per-cohort column, not the pooled figure, is the "
                                "honest object here.",
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
            "bishop2019": "No divergence: the registry cohort and the paper's site breakdown are "
                "both over n=41, the whole series.",
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
            "All three series record it: masunaga, 8 of 29 patients presenting with distant "
            "metastases (27.6%) underwent metastasectomy; chiusole, 8 lung metastasectomies and 2 "
            "radiofrequency ablations among 59 patients, 26 of whom were metastatic; bishop, 5 of "
            "the 13 patients who recurred distantly (38%) underwent surgical resection of "
            "metastases, and that series states in its own words that neither salvage surgery "
            "(p=0.15) nor salvage chemotherapy (p=0.24) was associated with improved "
            "disease-specific survival afterwards. ⇒ "
            "RT-LUNG-DIRECTED's premise is not hypothetical — a lung-directed local strategy is the "
            "standard of care for a substantial minority of these patients already, and the route's "
            "question is whether perfusion, inhaled delivery or ablation extends it to patients "
            "surgery cannot reach. ⚠ Nothing here says any of it works: these are counts of what was "
            "DONE, with no comparator and no outcome attached."),
        "⛔_what_is_still_not_computable": {
            "lesion_burden": "no series prints per-patient lesion counts, so no oligometastatic "
                             "threshold fraction can be stated. Unchanged by this curation, and "
                             "unchanged by the two series added on 2026-08-27.",
            "time_to_metastasis": "printed as a median in one series (5.9 years, chiusole2020) and "
                                  "as a median time to distant metastasis in another (28 months, "
                                  "bishop2019), and nowhere per patient.",
            "lung_confined_fraction_pooled": "STILL NOT POOLABLE, and the reason has changed. Two "
                                             "series now print an EXCLUSIVE two-row partition "
                                             "(masunaga 27 lung / 2 peritoneal on 29; bishop 12 "
                                             "lung / 1 bone on 13) but they describe different "
                                             "presentation strata and may not be summed; one "
                                             "series' rows are non-exclusive and over-sum their "
                                             "denominator (chiusole); and the one series that "
                                             "states a lung-CONFINED fraction in those words "
                                             "prints only percentages (drilon). See "
                                             "`lung_confined_readings`.",
            "⚠_SUPERSEDED_the_other_nine_series": "⛔ WITHDRAWN 2026-08-27. This file previously "
                "said: 'not open access. Europe PMC returns no PMC record and isOpenAccess: N for "
                "all nine remaining candidate series, so their site tables are unreachable at $0.' "
                "TWO of the nine have a PMC full-text record and both were read at $0 on "
                "2026-08-27 — bishop2019 (PMC7771031) and drilon2008 (PMC2779719). The registry "
                "already carried both PMCIDs, next to `openAccess: false`. ⛔ THE ROOT CAUSE IS A "
                "CONFLATION: `openAccess` is a LICENCE field and it was read as an ACCESS "
                "statement. A restrictive licence and an unreachable full text are different "
                "facts, and only the second one blocks a transcription of printed counts.",
            "the_other_seven_series": "NCBI ID conversion returns no PMCID for meisKindblom1999 "
                "(PMID 10366145), ussc2022 (35962783), japan2003 (12599237), china2016 "
                "(27402218), uMich2023 (36825763) and seer270_2022 (35144048); remiszewski2025 is "
                "a REVIEW (PMC12504171) and POLICY-evidence §1.3 forbids laundering a primary's "
                "counts through it. So seven of the nine remain unreachable at $0 — measured on "
                "2026-08-27, not assumed.",
            "a_candidate_series_this_search_surfaced": "Paioli 2020 (PMID 32572850, DOI "
                "10.1245/s10434-020-08737-7, Ann Surg Oncol), 67 molecularly confirmed localised "
                "EMC across three Italian Sarcoma Group centres, 1989-2016, is NOT in the clinical "
                "registry. NCBI returns no PMCID, so its site table is not reachable at $0. "
                "Recorded as a lead, not curated, and NOT assumed to be non-overlapping with "
                "chiusole2020 without checking the institutions.",
        },
        "lung_confined_readings": {
            "_what_this_block_is_for": "RT-LUNG-DIRECTED's eligibility criterion is a LUNG-CONFINED "
                "metastatic pattern. Three reachable series say something about it, no two of them "
                "in the same form, and POLICY-evidence forbids summing them. They are listed "
                "side by side and NOT combined.",
            "⛔_no_pooled_estimate": "There is no pooled lung-confined fraction here and no "
                "confidence interval on one. The rows below are different estimands over different "
                "strata (POLICY-evidence §2.1.3, §2.4).",
            "readings": [
                {"source_id": "masunaga2025", "stratum": "metastatic AT DIAGNOSIS",
                 "events": 27, "denom": 29,
                 "form": "one category per patient, rows exhaust the cohort — but the printed "
                 "words are '27 patients HAD LUNG METASTASES, and two had peritoneal "
                 "dissemination', which states involvement rather than confinement",
                 "⚠_is_an_upper_bound": True},
                {"source_id": "bishop2019",
                 "stratum": "developed distant metastasis during follow-up, localised at diagnosis",
                 "events": 12, "denom": 13, "form": "exclusive two-row partition (lung, bone), "
                 "rows exhaust the cohort",
                 "⚠_is_an_upper_bound": True},
                {"source_id": "drilon2008",
                 "stratum": "diagnosed with or progressed to metastatic disease",
                 "events": None, "denom": None,
                 "form": "PERCENTAGE-ONLY: 63% 'with metastasis confined to the lungs', 17% 'with "
                 "metastasis at other sites concurrent with lung disease', 20% other sites",
                 "⚠_is_an_upper_bound": False},
                {"source_id": "chiusole2020", "stratum": "metastatic disease in the series",
                 "events": None, "denom": 26,
                 "form": "NON-EXCLUSIVE rows (23 lung + 4 bone + 14 other = 41 over 26); no "
                 "lung-confined fraction is readable and none may be inferred",
                 "⚠_is_an_upper_bound": None},
            ],
            "⛔_THE_FINDING_AND_IT_CUTS_AGAINST_THE_ROUTE": "A two-row partition tells you which "
                "site a patient was FILED under; it does not tell you the patient had no other "
                "site — and in masunaga the printed verb is 'had', an involvement word, verified "
                "against the primary text on 2026-08-27. Drilon is the only series that draws the distinction in its own words, and "
                "when it does, 17 of the 80 percentage points of lung involvement turn out to be "
                "lung PLUS another site. ⇒ The 27/29 and 12/13 readings are UPPER BOUNDS on a "
                "lung-confined fraction, not measurements of one, and the only explicit "
                "lung-confined reading in the reachable literature is markedly lower than either. "
                "⚠ Stated because it runs against RT-LUNG-DIRECTED's own argument.",
            "⭐_what_did_improve": "The quantity is now readable in BOTH presentation strata rather "
                "than one — patients metastatic at diagnosis and patients who metastasise later — "
                "which is what a lung-directed strategy needs, because the two groups are offered "
                "it at different points in their disease.",
        },
        "⚠_superseded_retained": {
            "pooled_extremity_fraction_2026_08_25": "Before bishop2019 was added on 2026-08-27 the "
                "pooled extremity fractions were 70.4% (64.2-76.0) strict and 85.7% (80.5-89.6) "
                "inclusive, over 230 patients in two series. Both figures were correct for the "
                "two-series pool and are superseded by the three-series pool computed above. The "
                "per-cohort rows for chiusole2020 and masunaga2025 are unchanged.",
            "⚠_and_the_direction_is_disclosed": "Adding a third series moved the strict reading UP "
                "and the inclusive reading DOWN, which narrows the gap between the two "
                "definitions without closing it. The gap remains the binding uncertainty.",
        },
        "context_not_pooled": CONTEXT_NOT_POOLED,
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
