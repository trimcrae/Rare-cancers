#!/usr/bin/env python3
"""
CD248 / endosialin / TEM1 — the binder precedent, and the EMC-shaped hole in it. ($0, pure stdlib)

⭐ WHY THIS EXISTS. `emc_surfaceome_scan.py` calls CD248 `selectivity_significant: true` with
`enrichment_vs_rest 2.29` in the sarcoma class — one of very few genes it does — and CD248 appears
in NO prose anywhere in this repository. An unexploited positive sitting inside a committed
artifact is worse than an absent one, because every reader assumes somebody looked. This module is
the looking. Its one home for those DepMap numbers is
`surfaceome-instrument-limits.json -> limits.L2_stromal_floor_demonstrated.genes.CD248`; they are
NOT re-typed here (CLAUDE.md §1).

⛔ WHAT THIS MODULE IS FOR, AND WHAT IT REFUSES TO BE. A surface antigen is only a route if a
BINDER exists — the repository has no wet lab, so an antigen nobody has ever raised an antibody
against is an idea, not an option. So this records the binder precedent AND the clinical outcome
that precedent actually produced, which is a **failed randomised phase 2**. Recording the
programme without recording that it read out negative would be the exact shape of over-claim this
repository's language rules exist to stop.

⛔⛔ THE HEADLINE IS A NEGATIVE ABOUT THE FIELD, NOT A POSITIVE ABOUT THE DRUG. Across a Europe PMC
retrieval of the CD248/endosialin/TEM1 literature, the number of records mentioning extraskeletal
myxoid chondrosarcoma, EWSR1::NR4A3 or chordoid sarcoma is measured, not assumed — see
`emc_specific_evidence`. Every sarcoma reading in this file is a reading in a DIFFERENT sarcoma.

⚠ A NOTE ON THE NAME, because it is a trap this file must not fall into. EMC is NOT a
chondrosarcoma: it has no cartilaginous differentiation and is a distinct entity defined by
EWSR1::NR4A3. A reading in conventional (bone) chondrosarcoma therefore does NOT transfer to EMC,
and one such reading exists in this corpus (`records.sts_ihc_n94`), which is why the caveat is
here rather than left implicit.

VERIFICATION TAGS, used exactly as the rest of the repository uses them:
  [FT]  — open-access full text retrieved through CI and present in the `literature-cache` branch.
  [API] — Europe PMC core record + abstract retrieved through CI. Not open access; no full text.
Every record carries a PMID and, where one exists, a PMCID and a DOI.

Usage:  python3 research/modalities/cd248_precedent.py            # derive + write the artifact
        python3 research/modalities/cd248_precedent.py --check    # re-derive and diff
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "cd248-precedent.json")

#: Where the CI retrieval landed. `fetch-literature.yml` publishes to this branch, not to `main`
#: (CLAUDE.md §7 — check which ref a workflow writes to before quoting its artifact).
CORPUS_REF = "origin/literature-cache"
CORPUS_DIR = "literature/cd248-endosialin-antibody"
CORPUS_QUERY = ('(CD248 OR endosialin OR "tumor endothelial marker 1" OR TEM1) AND '
                '(antibody OR ontuxizumab OR "MORAb-004" OR sarcoma OR "CAR T" OR immunotoxin)')

#: The EMC identity terms. ⛔ `chondrosarcoma` ALONE IS DELIBERATELY NOT HERE: conventional
#: chondrosarcoma is a different disease that shares half a name, so matching it would manufacture
#: EMC evidence out of bone-tumour papers. The fusion is the identity.
EMC_TERMS = [r"extraskeletal myxoid", r"extra-?skeletal myxoid", r"chordoid sarcoma",
             r"EWSR1[\s:/-]*NR4A3", r"\bNR4A3\b", r"EWS[\s:/-]*CHN\b", r"TAF15[\s:/-]*NR4A3"]

# ---------------------------------------------------------------------------------------------
# THE RECORDS. Each was retrieved through CI in the run that produced `CORPUS_DIR`; the quoted
# figures are the authors' own, from the abstract or the open-access full text as tagged.
# ---------------------------------------------------------------------------------------------
RECORDS = {
    "founding_1992": {
        "what": "The paper that identified endosialin, as a cell-surface glycoprotein of tumour "
                "vasculature — the observation the name TEM1 comes from.",
        "title": "Identification of endosialin, a cell surface glycoprotein of vascular "
                 "endothelial cells in human cancer.",
        "journal": "Proc Natl Acad Sci U S A 1992",
        "pmid": "1438285", "pmcid": "PMC50436", "doi": "10.1073/pnas.89.22.10832",
        "verification": "[API]",
        "role": "identity of the antigen",
    },
    "sts_ihc_n514": {
        "what": "⭐ THE MEASUREMENT THAT MAKES CD248 DIFFERENT FROM FAP AND LRRC15. In soft-tissue "
                "sarcoma the TUMOUR CELLS themselves stain, not only the stroma — which is why "
                "the monoculture surfaceome scan could see CD248 at all while LRRC15 sat at the "
                "floor (surfaceome-instrument-limits.json L2).",
        "title": "Endosialin expression in soft tissue sarcoma as a potential marker of "
                 "undifferentiated mesenchymal cells.",
        "journal": "Br J Cancer 2016",
        "pmid": "27434038", "pmcid": "PMC4985356", "doi": "10.1038/bjc.2016.214",
        "verification": "[FT]",
        "design": "immunohistochemistry on a tissue microarray of 514 human soft-tissue sarcomas",
        "tumour_cell_positivity_authors_figures": {
            "undifferentiated_pleomorphic_sarcoma": "89% (104/117)",
            "adult_fibrosarcoma_spindle_cell_sarcoma": "77% (20/26)",
            "synovial_sarcoma": "62% (37/60)",
            "leiomyosarcoma": "51% (94/185)",
            "rhabdomyosarcoma": "31% (39/126)",
        },
        "quote_tumour_vs_stroma": (
            "\"The endosialin cell surface glycoprotein is predominantly expressed by stromal "
            "fibroblasts and pericytes in epithelial neoplasms; however, tumour cell expression "
            "has been reported in small series of sarcomas.\""),
        "⚠_normal_tissue_is_not_blank_in_this_paper": (
            "Its own positive controls are NORMAL tissues: \"Adult non-neoplastic human breast "
            "(positive control) showed … strong endosialin expression on the stromal fibroblasts "
            "surrounding the terminal duct lobular units\" and \"Normal human placenta (positive "
            "control) showed strong endosialin staining on the stromal cells within the placental "
            "villi\". So 'absent from normal adult tissue' is a summary, not a universal — the "
            "normal-tissue axis has to be read, not assumed."),
        "⛔_no_myxoid_or_chondroid_entity_assessed": True,
    },
    "sts_ihc_n94": {
        "what": "A second sarcoma expression series, gene + protein. Included here mainly for the "
                "chondrosarcoma line, because that line is the one most likely to be misread as "
                "an EMC reading.",
        "title": "Endosialin and Associated Protein Expression in Soft Tissue Sarcomas: A "
                 "Potential Target for Anti-Endosialin Therapeutic Strategies.",
        "journal": "Sarcoma 2016",
        "pmid": "27057137", "pmcid": "PMC4748105", "doi": "10.1155/2016/5213628",
        "verification": "[FT]",
        "design": "94 soft-tissue sarcoma samples; IHC and gene expression for endosialin and "
                  "PDGFR-β",
        "quote": "\"Bone sarcomas demonstrated consistently high endosialin and PDGFR-β "
                 "expression with chondrosarcoma having lower expression\"",
        "⛔_this_is_NOT_an_EMC_reading": (
            "That sentence is about conventional bone chondrosarcoma. EMC shares half the name "
            "and neither the lineage nor the genetics — it has no cartilaginous differentiation "
            "and is defined by EWSR1::NR4A3. Carrying this reading across would be a name "
            "collision masquerading as evidence."),
    },
    "ontuxizumab_phase1_fih": {
        "what": "First-in-human phase 1 of the clinical-grade anti-endosialin antibody.",
        "title": "A first-in-human phase I study of MORAb-004, a monoclonal antibody to "
                 "endosialin in patients with advanced solid tumors.",
        "journal": "Clin Cancer Res 2015",
        "pmid": "25398449", "pmcid": "PMC4612616", "doi": "10.1158/1078-0432.ccr-14-1829",
        "verification": "[FT]",
        "result_authors_figures": "36 patients over 10 dose levels (0.0625–16 mg/kg); MTD 12 "
                                  "mg/kg; 18 of 32 evaluable patients achieved disease "
                                  "stability, with minor radiographic responses in 4 (pancreatic "
                                  "neuroendocrine, hepatocellular and sarcoma tumour types).",
        "role": "the antibody is clinically administrable and dose-characterised in humans",
    },
    "ontuxizumab_randomised_phase2_STS": {
        "what": "⛔ THE OUTCOME THAT GOVERNS THIS WHOLE ROUTE. The naked antibody was tested in a "
                "randomised, double-blind, placebo-controlled phase 2 in metastatic soft-tissue "
                "sarcoma, and it did not work.",
        "title": "A phase 1 and randomized controlled phase 2 trial of the safety and efficacy of "
                 "the combination of gemcitabine and docetaxel with ontuxizumab (MORAb-004) in "
                 "metastatic soft-tissue sarcomas.",
        "journal": "Cancer 2019",
        "pmid": "31034598", "pmcid": "PMC6618088", "doi": "10.1002/cncr.32084",
        "verification": "[FT]",
        "design": "part 2: 209 patients randomised 2:1, double-blind, ontuxizumab 8 mg/kg or "
                  "placebo, each with gemcitabine + docetaxel; stratified by 4 histological "
                  "cohorts",
        "result_authors_figures": {
            "progression_free_survival": "4.3 months (95% CI 2.7–6.3) with ontuxizumab + G/D vs "
                                         "5.6 months (95% CI 2.6–8.3) with placebo + G/D; "
                                         "P = .67, HR 1.07 (95% CI 0.77–1.49)",
            "overall_survival": "18.3 months (95% CI 16.2–21.1) vs 21.1 months (95% CI 14.2–not "
                                "reached); P = .32, HR 1.23 (95% CI 0.82–1.82)",
            "by_subtype": "\"No significant differences between the treatment groups occurred for "
                          "any efficacy parameter by sarcoma cohort.\"",
        },
        "authors_conclusion_verbatim": (
            "\"Ontuxizumab plus G/D showed no enhanced activity over chemotherapy alone in "
            "soft-tissue sarcomas\" … \"On the basis of these data, further trials of "
            "ontuxizumab for soft-tissue sarcomas are not warranted.\""),
        "⛔_what_it_does_and_does_not_close": (
            "It closes the NAKED ANTIBODY as a therapeutic in unselected soft-tissue sarcoma. It "
            "does NOT close the ANTIGEN: the trial enrolled without any endosialin expression "
            "selection, and the same authors name antibody-drug conjugates as the follow-on to "
            "evaluate. A target and a mechanism are different claims, and only one of them was "
            "tested here."),
        "⚠_EMC_was_not_a_named_cohort": (
            "The stratification cohorts were liposarcoma, leiomyosarcoma and undifferentiated "
            "pleomorphic sarcoma, with an 'other' cohort that the paper itemises as angiosarcoma "
            "(n=5), spindle cell sarcoma (n=5), peripheral nerve sheath tumour (n=7), synovial "
            "sarcoma (n=20) and 'miscellaneous types' (n=20). EMC is named nowhere. Whether any "
            "EMC patient sat inside those 20 miscellaneous cases is NOT recoverable from the "
            "publication, and this module does not guess."),
    },
    "ontuxizumab_phase1_paediatric": {
        "title": "Phase 1 trial of ontuxizumab (MORAb-004) in children with relapsed or "
                 "refractory solid tumors: A report from the Children's Oncology Group Phase 1 "
                 "Pilot Consortium (ADVL1213).",
        "journal": "Pediatr Blood Cancer 2018",
        "pmid": "29292843", "pmcid": "PMC5867214", "doi": "10.1002/pbc.26944",
        "verification": "[API]",
        "role": "the antibody has paediatric dosing data — relevant because EMC has a wide age "
                "range, and irrelevant to whether it works",
    },
    "adc_preclinical": {
        "what": "The payload-bearing format the failed phase 2 points at. PRECLINICAL.",
        "title": "Generation of a novel Antibody-Drug Conjugate targeting endosialin: potent and "
                 "durable antitumor response in sarcoma.",
        "journal": "Oncotarget 2017",
        "pmid": "28947977", "pmcid": "PMC5601145", "doi": "10.18632/oncotarget.19499",
        "verification": "[FT]",
        "result_authors_figures": "humanised anti-endosialin mAb hMP-E-8.3 conjugated to a "
                                  "duocarmycin derivative; target-dependent killing in "
                                  "endosialin-expressing lines, and long-lasting tumour growth "
                                  "inhibition in a cell-line xenograft model of human "
                                  "osteosarcoma",
        "⛔_stage": "cell lines and a xenograft. No human data. Not an efficacy claim in any "
                    "sarcoma, and nothing at all in EMC.",
    },
    "radioligand_preclinical": {
        "what": "The radioligand-therapy format — the same modality RT-FAP-RLT proposes, with a "
                "different address.",
        "title": "177Lu radiolabeling and preclinical theranostic study of 1C1m-Fc: an anti-TEM-1 "
                 "scFv-Fc fusion protein in soft tissue sarcoma.",
        "journal": "EJNMMI Res 2020",
        "pmid": "32804276", "pmcid": "PMC7431510", "doi": "10.1186/s13550-020-00685-3",
        "verification": "[API]",
        "result_authors_figures": "specific uptake in TEM-1-positive (SK-N-AS) versus negative "
                                  "(HT-1080) xenografts; 1.9-fold higher SPECT/CT signal at 72 h "
                                  "in the positive tumours",
        "dosimetry_follow_on": {
            "title": "From bench to bedside: 64Cu/177Lu 1C1m-Fc anti TEM-1: mice-to-human "
                     "dosimetry extrapolations for future theranostic applications.",
            "journal": "EJNMMI Res 2023",
            "pmid": "37314509", "pmcid": "PMC10267050", "doi": "10.1186/s13550-023-01010-4",
            "verification": "[API]",
        },
        "imaging_agent": {
            "title": "Development of 89Zr-Ontuxizumab for in vivo TEM-1/endosialin PET "
                     "applications.",
            "journal": "Oncotarget 2016",
            "pmid": "26909615", "pmcid": "PMC4914343", "doi": "10.18632/oncotarget.7552",
            "verification": "[API]",
            "⭐_why_this_one_matters_most_to_a_no_wet_lab_program": (
                "A PET agent against this antigen has been built. The measurement every blocked "
                "surface route in this repository is missing — 'any measurement in EMC' — is in "
                "principle obtainable in a patient by IMAGING rather than by a biopsy assay. "
                "That is a route to a measurement that does not need this program to own a lab. "
                "It still needs a clinician, a sponsor and a patient, so it is an outward-facing "
                "step and not a $0 one."),
        },
        "⛔_stage": "preclinical; xenograft biodistribution and dosimetry extrapolation only.",
    },
    "t_cell_engager_and_car_preclinical": {
        "what": "The CAR / T-cell-engager format — the modality RT-CART-SURFACE proposes.",
        "title": "Soluble trivalent engagers redirect cytolytic T cell activity toward tumor "
                 "endothelial marker 1.",
        "journal": "Cell Rep Med 2021",
        "pmid": "34467246", "pmcid": "PMC8385295", "doi": "10.1016/j.xcrm.2021.100362",
        "verification": "[API]",
        "result_authors_figures": "two fully human anti-TEM1 scFvs (1C1m, 7G22) confer cytolytic "
                                  "activity as 2nd-generation CARs and as trivalent engagers; "
                                  "systemic 1C1m-tB prevented establishment of Ewing sarcoma "
                                  "tumours in a xenograft model",
        "⛔_stage": "preclinical. 'Prevents establishment' in a xenograft is not treatment of "
                    "established disease, and Ewing sarcoma is not EMC.",
    },
    "review_2026": {
        "what": "The most recent synthesis, and the source of the 'selectively expressed by "
                "sarcomas' framing this module is careful not to adopt uncritically.",
        "title": "Endosialin (CD248) Cancer Role and Therapeutics: 33 Years on.",
        "journal": "Mol Cancer Ther 2026",
        "pmid": "41711393", "pmcid": None, "doi": "10.1158/1535-7163.mct-25-0759",
        "verification": "[API]",
        "⚠_not_open_access": "No PMCID; abstract only. Nothing in this file rests on its full "
                             "text, and its claims are recorded as the review's, not as measured.",
        "quote": "\"CD248 is highly and selectively expressed by sarcomas and by pericytes in "
                 "tumor vasculature and wound-healing vasculature.\"",
        "⚠_a_review_claim_is_not_a_measurement": (
            "'Selectively expressed' in a review is a summary over the primary series above, "
            "none of which included EMC. It is quoted because it is the field's current framing, "
            "not because it settles anything for this disease."),
    },
}

MODALITY_LADDER = {
    "_what": "What stage each CD248-directed format has actually reached. ⛔ Read this before any "
             "sentence that begins 'CD248 is a validated target'.",
    "naked_antibody_in_soft_tissue_sarcoma": "TESTED IN HUMANS AND NEGATIVE — randomised phase 2, "
                                             "n=209, no PFS or OS benefit "
                                             "(records.ontuxizumab_randomised_phase2_STS).",
    "antibody_drug_conjugate": "PRECLINICAL (cell lines + one osteosarcoma xenograft).",
    "radioligand_therapy": "PRECLINICAL (xenograft biodistribution; human dosimetry by "
                           "extrapolation).",
    "pet_imaging_agent": "PRECLINICAL (89Zr-ontuxizumab).",
    "car_t_and_t_cell_engager": "PRECLINICAL (Ewing sarcoma xenograft, prevention setting).",
    "anything_at_all_in_EMC": "NONE. See `emc_specific_evidence`.",
}


def _corpus_index(corpus_dir=None):
    """Read a CI-retrieved Europe PMC index out of the `literature-cache` branch.

    ⛔ FAIL-HONEST, AND THAT IS THE WHOLE POINT OF DERIVING IT. If the corpus is not reachable
    from this checkout the counts are reported as UNREAD, never as zero — a retrieval that could
    not be read is an absent reading, and 'no EMC papers found' produced by a failed `git show`
    is the exact fabricated negative this repository has been burned by (CLAUDE.md §4).

    ⭐ TAKES THE CORPUS DIRECTORY so sibling precedent modules (`alcam_precedent.py`) reuse this
    reader rather than reimplementing it. The fail-honest behaviour above is the whole reason it
    must not be copied: a second, subtly different reader is a second chance to turn an
    unreadable corpus into a zero.
    """
    path = f"{CORPUS_REF}:{corpus_dir or CORPUS_DIR}/_index.json"
    try:
        raw = subprocess.run(["git", "show", path], cwd=ROOT, capture_output=True,
                             timeout=120).stdout
        rows = json.loads(raw.decode("utf-8", "replace"))
    except Exception as exc:  # noqa: BLE001
        return None, (f"⛔ CORPUS UNREAD — `git show {path}` failed ({str(exc)[:140]}). The "
                      f"EMC-specific count below is UNAVAILABLE, which is NOT the same as zero.")
    if not isinstance(rows, list):
        return None, "⛔ CORPUS UNREAD — the index is not a list of records."
    return rows, None


def emc_specific_evidence():
    rows, why = _corpus_index()
    if rows is None:
        return {"_status": "UNREAD", "why": why,
                "corpus_ref": CORPUS_REF, "corpus_dir": CORPUS_DIR, "query": CORPUS_QUERY,
                "⛔_meaning": "An absent reading, not a reading of absence. No count is claimed."}
    pat = re.compile("|".join(EMC_TERMS), re.I)
    hits = []
    for r in rows:
        blob = " ".join(str(r.get(k) or "") for k in ("title", "abstract"))
        if pat.search(blob):
            hits.append({"pmid": r.get("pmid"), "pmcid": r.get("pmcid"),
                         "doi": r.get("doi"), "year": r.get("year"), "title": r.get("title")})
    return {
        "_status": "READ",
        "corpus_ref": CORPUS_REF, "corpus_dir": CORPUS_DIR, "query": CORPUS_QUERY,
        "n_records_retrieved": len(rows),
        "emc_identity_terms_searched": EMC_TERMS,
        "_why_bare_chondrosarcoma_is_not_a_term": (
            "Conventional chondrosarcoma is a different disease. Including it would return bone "
            "tumour papers and let them read as EMC evidence — a name collision, not a finding."),
        "n_records_mentioning_EMC": len(hits),
        "records_mentioning_EMC": hits,
        "searched_fields": ["title", "abstract"],
        "⚠_scope_of_this_count": (
            "Title and abstract of the retrieved records only. It is evidence that the CD248 "
            "literature does not FOREGROUND EMC; it is not proof that no sentence about EMC "
            "exists in any full text, and it is not a Europe PMC-wide census."),
        "verdict": ("⭐ ZERO records in this retrieval name EMC or its fusion. So every CD248 "
                    "reading above is a reading in a DIFFERENT sarcoma, and the measurement the "
                    "five blocked routes need does not exist in this literature."
                    if not hits else
                    "⚠ Records naming EMC ARE present — read them before quoting the gap."),
    }


def derive():
    res = {
        "_what": "CD248 / endosialin / TEM1: the binder precedent behind a candidate EMC surface "
                 "antigen, and the measured absence of any EMC-specific evidence in it.",
        "_why": ("emc_surfaceome_scan.py calls CD248 selectivity-significant in the sarcoma class "
                 "and no document in this repository mentions it. An unexploited positive inside "
                 "a committed artifact reads exactly like one somebody already checked."),
        "_execution_model": "$0. A Europe PMC retrieval already performed in CI, plus committed "
                            "artifacts. No network from the sandbox, no GPU, no rental.",
        "_language_discipline": (
            "⛔ NOTHING HERE IS AN EFFICACY, SELECTIVITY, SAFETY, THERAPEUTIC-WINDOW OR CLINICAL-"
            "READINESS CLAIM FOR CD248 OR ANY CD248-DIRECTED AGENT IN EMC. The only randomised "
            "human test of a CD248-directed agent in soft-tissue sarcoma was NEGATIVE and is "
            "recorded at full strength. No CD248-directed agent has been given to an EMC patient "
            "on the basis of anything in this repository, and nothing here would justify it."),
        "_the_dependency_that_makes_this_worth_writing": (
            "This repository has no wet lab, so an antigen with no existing binder cannot become "
            "a route no matter how it reads. CD248's value is that the binders EXIST at clinical "
            "grade — antibody, ADC, radioligand, PET tracer, CAR and engager — so the missing "
            "input is a MEASUREMENT rather than a molecule. That is the kind of gap a "
            "computational program can actually close."),
        "instrument_that_flagged_it": {
            "module": "research/modalities/emc_surfaceome_scan.py",
            "one_home_of_its_CD248_numbers": (
                "research/modalities/surfaceome-instrument-limits.json -> "
                "limits.L2_stromal_floor_demonstrated.genes.CD248 (and the "
                "`counter_reading_that_narrows_the_limit` beside it). Not re-typed here."),
            "⚠_what_that_instrument_measured": (
                "DepMap sarcoma cell lines in MONOCULTURE versus other cancer lineages — not EMC "
                "(no verified EWSR1::NR4A3 line is in it) and not versus normal tissue. It is "
                "the reason CD248 is on this list at all, and it settles nothing about EMC."),
            "⭐_why_CD248_survived_a_filter_that_floored_LRRC15": (
                "The same artifact records LRRC15 at frac_expressed 0.0 and CD248 as significant. "
                "Both are called stromal antigens, so the discriminating fact is that mesenchymal "
                "TUMOUR cells genuinely transcribe CD248 — which is independently measured at "
                "protein level in 514 soft-tissue sarcomas (records.sts_ihc_n514). Two "
                "instruments, two populations, same direction."),
        },
        "records": RECORDS,
        "modality_ladder": MODALITY_LADDER,
        "emc_specific_evidence": emc_specific_evidence(),
        "the_emc_read_that_pairs_with_this": {
            "artifact": "research/modalities/emc-expression-panels.json",
            "address": "reads.read_8_SURFACE_ANTIGEN.CD248_followup",
            "⛔_read_its_state_first": "If CD248 comes back NOT_READABLE_ON_EITHER_PLATFORM, that "
                                      "is an instrument statement and the route is unchanged — "
                                      "NOT a negative.",
        },
        "the_normal_tissue_axis": {
            "artifact": "research/modalities/emc-surface-normal-window.json",
            "why_it_is_decisive_for_this_antigen_in_particular": (
                "CD248's own primary literature uses NORMAL breast stroma and NORMAL placenta as "
                "POSITIVE controls (records.sts_ihc_n514). So the 'absent in normal adult tissue' "
                "summary the reviews carry must be checked, not inherited — an antigen shared "
                "with normal fibroblasts and pericytes is an on-target/off-tumour question in "
                "every tissue that has vasculature."),
        },
        "what_would_actually_move_this_route": [
            "The EMC-tumour expression read that pairs with this file — dispatched, $0, and the "
            "only step here that needs nobody outside the program.",
            "IHC on EMC tissue with a validated anti-endosialin antibody. Needs tissue and a "
            "pathologist; not computable.",
            "Single-cell or spatial EMC data, which would separate tumour-cell CD248 from "
            "pericyte/CAF CD248 — the distinction bulk tissue cannot make and the one that "
            "decides which modality is even applicable.",
            "⭐ An imaging read. A PET tracer against this antigen exists "
            "(records.radioligand_preclinical.imaging_agent), so 'a measurement in EMC' is "
            "obtainable without a biopsy assay — but it is an outward-facing, human-subject step "
            "and therefore not this program's to take.",
        ],
        "⛔_what_this_file_does_NOT_claim": [
            "That CD248 is expressed in EMC. No EMC measurement of it exists in this literature "
            "and none is asserted here.",
            "That CD248 is a validated sarcoma target. The one randomised human test was "
            "negative; every positive format is preclinical.",
            "That transcript or IHC positivity in other sarcomas transfers to EMC. It does not, "
            "and the subtype figures in records.sts_ihc_n514 vary from 31% to 89% across five "
            "entities, none of which is EMC.",
            "That a reading in conventional chondrosarcoma is a reading in EMC. It is not — see "
            "records.sts_ihc_n94.",
            "Anything about a patient.",
        ],
    }
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--check", action="store_true",
                    help="re-derive and diff against the committed artifact")
    args = ap.parse_args(argv)
    res = derive()
    if args.check:
        if not os.path.exists(OUT):
            print("no artifact to check against", file=sys.stderr)
            return 1
        old = json.load(open(OUT))
        drift = [k for k in res if old.get(k) != res[k]]
        print("REPRODUCES" if not drift else f"DRIFT in: {drift}")
        return 0 if not drift else 1
    json.dump(res, open(OUT, "w"), indent=2)
    e = res["emc_specific_evidence"]
    print(f"wrote {OUT}")
    print(f"corpus: {e.get('_status')} n={e.get('n_records_retrieved')} "
          f"EMC-mentioning={e.get('n_records_mentioning_EMC')}")
    print(f"verdict: {e.get('verdict') or e.get('why')}")
    for k, v in MODALITY_LADDER.items():
        if not k.startswith("_"):
            print(f"  {k:<42} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
