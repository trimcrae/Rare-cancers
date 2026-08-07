#!/usr/bin/env python3
"""
ALCAM / CD166 — the binder precedent, and the normal-tissue liability the RNA prior did not show.

⭐ WHY THIS EXISTS. ALCAM is the ONE antigen on the 2026-08-07 EMC surface panel that is higher in
EMC than in comparator sarcomas on BOTH readable series, and whose HPA normal-tissue window comes
back RESTRICTED (emc-expression-panels.json -> reads.read_7_SURFACE_ANTIGEN, and
emc-surface-normal-window.json). Two questions decide whether that is a route or a curiosity, and
neither is answerable from expression data: does a binder exist, and is the normal-tissue window
real?

⛔⛔ THE SECOND QUESTION IS WHY THIS FILE MATTERS MORE THAN THE FIRST. The HPA classifier returned
RESTRICTED, and the primary literature retrieved here names ALCAM on MESENCHYMAL STEM CELLS, in
the HAEMATOPOIETIC STEM CELL NICHE, on PERICHONDRIUM, on early CARDIOMYOCYTES, and as the LIGAND
FOR CD6 ON T CELLS. Every one of those is an on-target/off-tumour concern, and none of them
contradicts the HPA label — a bulk normal-tissue RNA atlas measures average abundance across a
tissue, so a molecule on a rare stem-cell compartment or a lymphocyte can be 'tissue enriched' and
still be exactly where you must not put a payload. ⛔ SO `RESTRICTED` IN THAT ARTIFACT MUST NEVER
BE QUOTED AS A SAFETY STATEMENT FOR THIS ANTIGEN, and this module is where the reason lives.

⚠ AND A SECOND DEFLATION, WHICH IS SPECIFIC TO THIS DISEASE. ALCAM is a mesenchymal-lineage
marker. EMC is a mesenchymal tumour and its comparators on GPL6244 are fibroblastic
(LGFMS / desmoid / fibrosarcoma), so an ALCAM elevation could be reporting lineage or
differentiation state rather than anything about EWSR1::NR4A3. Nothing measured discriminates
those, and this file does not pretend otherwise.

VERIFICATION TAGS are used exactly as `cd248_precedent.py` uses them: [FT] = open-access full text
retrieved through CI and present in the `literature-cache` branch; [API] = Europe PMC core record
and abstract only. Every record carries a PMID and, where one exists, a PMCID and a DOI.

Usage:  python3 research/modalities/alcam_precedent.py            # derive + write the artifact
        python3 research/modalities/alcam_precedent.py --check    # re-derive and diff
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cd248_precedent as CD248  # noqa: E402  — the corpus reader has ONE home; see `_corpus`

OUT = os.path.join(HERE, "alcam-precedent.json")

CORPUS_DIR = "literature/alcam-cd166-binder"
CORPUS_QUERY = ('(ALCAM OR CD166 OR "activated leukocyte cell adhesion molecule") AND '
                '(antibody OR "antibody-drug conjugate" OR "CAR T" OR immunotoxin OR '
                'radioligand OR sarcoma)')

#: ⛔ A BROAD QUERY RETRIEVES A LOT THAT IS NOT ABOUT THE ANTIGEN. "CD166" and "sarcoma" and
#: "antibody" co-occur in thousands of papers that never mention ALCAM. Counting EMC mentions
#: across the whole retrieval without this filter would report a denominator that means nothing.
ON_TOPIC = r"\bALCAM\b|\bCD166\b|activated leukocyte cell adhesion"

RECORDS = {
    "founding_1995": {
        "what": "The paper that cloned and characterised ALCAM, as the ligand for CD6.",
        "title": "Cloning, mapping, and characterization of activated leukocyte-cell adhesion "
                 "molecule (ALCAM), a CD6 ligand.",
        "journal": "J Exp Med 1995",
        "pmid": "7760007", "pmcid": "PMC2192054", "doi": None,
        "verification": "[API]",
        "role": "identity of the antigen — and note what the identity IS: a T-cell ligand.",
    },
    "clinical_adc_praluzatamab_ravtansine": {
        "what": "⭐ THE BINDER QUESTION IS ANSWERED, AND IN HUMANS. A CD166-directed "
                "antibody-drug conjugate has been given to patients in a phase I/II trial. For a "
                "program with no wet lab this is the difference between an idea and an option: "
                "the molecule does not have to be raised.",
        "title": "Praluzatamab Ravtansine, a CD166-Targeting Antibody-Drug Conjugate, in Patients "
                 "with Advanced Solid Tumors: An Open-Label Phase I/II Trial.",
        "journal": "Clin Cancer Res 2022",
        "pmid": "35165101", "pmcid": "PMC9365353", "doi": "10.1158/1078-0432.ccr-21-3656",
        "verification": "[API]",
        "format": "a Probody (masked, protease-activated) drug conjugate — CX-2009. ⚠ The MASKING "
                  "is not incidental: a Probody is engineered precisely because the naked "
                  "anti-CD166 antibody's normal-tissue distribution is a problem, which is "
                  "independent corroboration of the liability section below.",
        "⛔_no_efficacy_claim_is_made_here": (
            "This module records that the trial EXISTS and that the agent reached patients. It "
            "does not report or characterise its outcome, and nothing about it is evidence for "
            "any activity in EMC — no sarcoma cohort is claimed and no EMC patient is involved."),
    },
    "imaging_agent": {
        "what": "A PET tracer against the same antigen — the route to a measurement in a patient "
                "that does not require a biopsy assay.",
        "title": "The tumor targeting performance of anti-CD166 Probody drug conjugate CX-2009 "
                 "and its parental derivatives as monitored by 89Zr immuno-PET in xenograft "
                 "bearing mice.",
        "journal": "Theranostics 2020",
        "pmid": "32483421", "pmcid": "PMC7255005", "doi": "10.7150/thno.44334",
        "verification": "[API]",
        "earlier_immunopet": {
            "title": "Enhanced immunoPET of ALCAM-positive colorectal carcinoma using "
                     "site-specific 64Cu-DOTA conjugation.",
            "journal": "Protein Eng Des Sel 2014",
            "pmid": "25095796", "pmcid": "PMC4191443", "doi": "10.1093/protein/gzu030",
            "verification": "[API]",
        },
        "⛔_stage": "preclinical imaging in xenografts.",
    },
    "car_t_in_sarcoma": {
        "what": "⭐ A CAR-T against this antigen, built and tested in a SARCOMA — the modality "
                "RT-CART-SURFACE proposes, against the antigen this read surfaced.",
        "title": "Anti-CD166/4-1BB chimeric antigen receptor T cell therapy for the treatment of "
                 "osteosarcoma.",
        "journal": "J Exp Clin Cancer Res 2019",
        "pmid": "30995926", "pmcid": "PMC6471997", "doi": "10.1186/s13046-019-1147-6",
        "verification": "[API]",
        "⛔_stage": "preclinical, and osteosarcoma is not EMC.",
        "second_car_construct": {
            "title": "CD166-specific CAR-T cells potently target colorectal cancer cells.",
            "journal": "Transl Oncol 2023",
            "pmid": "36327697", "pmcid": "PMC9637812", "doi": "10.1016/j.tranon.2022.101575",
            "verification": "[API]",
        },
    },
    "internalisation_which_an_ADC_requires": {
        "what": "Whether the antigen internalises, which is the property a drug conjugate depends "
                "on and which expression data cannot report.",
        "title": "Internalization and recycling of ALCAM/CD166 detected by a fully human "
                 "single-chain recombinant antibody.",
        "journal": "J Cell Sci 2005",
        "pmid": "15769845", "pmcid": None, "doi": "10.1242/jcs.02280",
        "verification": "[API]",
    },
    "review_theranostic": {
        "title": "The Clinical and Theranostic Values of Activated Leukocyte Cell Adhesion "
                 "Molecule (ALCAM)/CD166 in Human Solid Cancers.",
        "journal": "Cancers (Basel) 2021",
        "pmid": "34680335", "pmcid": "PMC8533996", "doi": "10.3390/cancers13205187",
        "verification": "[API]",
        "⚠_a_review_claim_is_not_a_measurement": "Quoted as the field's framing, not as evidence.",
    },
}

#: ⛔ THE HALF THAT MUST NEVER BE DROPPED.
NORMAL_TISSUE_LIABILITY = {
    "_what": "⛔ WHERE ALCAM IS IN NORMAL BIOLOGY, FROM PRIMARY SOURCES — the axis that decides "
             "whether a surface antigen has a therapeutic window, and the one the HPA RNA prior "
             "cannot resolve.",
    "_why_this_does_not_contradict_the_RESTRICTED_window": (
        "emc-surface-normal-window.json classifies ALCAM RESTRICTED from HPA's 'Tissue enriched' "
        "label, and that classification is correctly derived — its profile matches both of the "
        "artifact's RESTRICTED positive controls. But a BULK normal-tissue RNA atlas reports "
        "average abundance across a whole tissue. A molecule confined to a RARE compartment — a "
        "stem-cell niche, a lymphocyte subset — is diluted to near nothing in bulk and can read "
        "as restricted while sitting exactly where a payload must not go. ⛔ The two readings are "
        "not in conflict; the RNA prior is answering a coarser question, and this section is the "
        "reason it must not be quoted as a safety statement."),
    "hematopoietic_stem_cells_and_the_niche": {
        "title": "CD166 regulates human and murine hematopoietic stem cells and the "
                 "hematopoietic niche.",
        "journal": "Blood 2014",
        "pmid": "24740813", "pmcid": "PMC4110658", "doi": "10.1182/blood-2014-03-565721",
        "verification": "[API]",
        "⛔_why_it_matters": "Marrow toxicity is the classic dose-limiting toxicity of a drug "
                            "conjugate. An antigen that regulates HSCs AND their niche is a "
                            "specific, named haematological risk, not a generic caveat.",
    },
    "mesenchymal_stem_cells_and_perichondrium": {
        "title": "Mesenchymal stem cells in perichondrium express activated leukocyte cell "
                 "adhesion molecule and participate in bone marrow formation.",
        "journal": "J Exp Med 2002",
        "pmid": "12070283", "pmcid": "PMC2193567", "doi": "10.1084/jem.20011700",
        "verification": "[API]",
        "corroborating": {
            "title": "Mesenchymal stem cell surface antigen SB-10 corresponds to activated "
                     "leukocyte cell adhesion molecule and is involved in osteogenic "
                     "differentiation of human mesenchymal stem cells.",
            "journal": "J Bone Miner Res 1998",
            "pmid": "9556065", "pmcid": None, "doi": "10.1359/jbmr.1998.13.4.655",
            "verification": "[API]",
        },
        "⛔_why_it_matters_TWICE": (
            "(1) SAFETY: normal mesenchymal stem cells carry this antigen. "
            "(2) ⚠ AND IT DEFLATES THE EMC READING ITSELF. ALCAM is a mesenchymal-lineage / "
            "MSC marker; EMC is a mesenchymal tumour, and the elevation measured here is against "
            "OTHER SARCOMAS. So the reading could be reporting lineage or differentiation state "
            "rather than anything specific to EWSR1::NR4A3, and nothing measured discriminates "
            "the two. This is the single most important qualification on the whole result."),
    },
    "T_cell_costimulation_via_CD6": {
        "title": "Phenotypic and functional characterization of the CD6-ALCAM T-cell "
                 "co-stimulatory pathway after allogeneic cell transplantation.",
        "journal": "Haematologica 2022",
        "pmid": "35484649", "pmcid": "PMC9614543", "doi": "10.3324/haematol.2021.280444",
        "verification": "[API]",
        "⛔_why_it_matters_for_a_T_CELL_modality_specifically": (
            "ALCAM is the ligand for CD6 on T cells. A CAR-T or T-cell engager directed at ALCAM "
            "is aimed at a molecule that participates in T-cell costimulation, which raises "
            "fratricide and immune-perturbation questions that do not arise for an inert "
            "antigen. That is a modality-specific hazard, and it argues that the conjugate and "
            "radioligand formats are the better-posed ones here — a statement about which "
            "experiment is well-formed, NOT a claim that either works."),
    },
    "dendritic_cell_migration": {
        "title": "ALCAM Mediates DC Migration Through Afferent Lymphatics and Promotes "
                 "Allospecific Immune Reactions.",
        "journal": "Front Immunol 2019",
        "pmid": "31031759", "pmcid": "PMC6473055", "doi": "10.3389/fimmu.2019.00759",
        "verification": "[API]",
    },
    "early_cardiomyocytes": {
        "title": "ALCAM (CD166) is a surface marker for early murine cardiomyocytes.",
        "journal": "Cells Tissues Organs 2006",
        "pmid": "17409743", "pmcid": None, "doi": "10.1159/000099624",
        "verification": "[API]",
        "⚠_species": "murine, and EARLY cardiomyocytes — developmental rather than adult. Recorded "
                     "because the classifier's VITAL_TISSUES list includes heart and this is the "
                     "kind of expression a bulk adult atlas would not surface, not because it is "
                     "an established adult human liability.",
    },
    "⭐_the_independent_corroboration_that_this_is_a_real_problem": (
        "The clinical agent is a PROBODY — a masked, protease-activated conjugate. That "
        "engineering exists to narrow a molecule's exposure in normal tissue. A field that built "
        "a masking technology around this antigen had already concluded its normal-tissue "
        "distribution was the obstacle, and that judgement is embodied in the molecule rather "
        "than merely asserted in a discussion section."),
}


def emc_specific_evidence():
    # ⭐ ONE HOME FOR THE READER. `cd248_precedent._corpus_index` is fail-honest by design; a
    # second copy here would be a second chance to turn an unreadable corpus into a zero.
    rows, why = CD248._corpus_index(CORPUS_DIR)
    if rows is None:
        return {"_status": "UNREAD", "why": why, "corpus_dir": CORPUS_DIR,
                "query": CORPUS_QUERY,
                "⛔_meaning": "An absent reading, not a reading of absence. No count is claimed."}
    topic = re.compile(ON_TOPIC, re.I)
    emc = re.compile("|".join(CD248.EMC_TERMS), re.I)
    on_topic, hits = [], []
    for r in rows:
        blob = " ".join(str(r.get(k) or "") for k in ("title", "abstract"))
        if not topic.search(blob):
            continue
        on_topic.append(r)
        if emc.search(blob):
            hits.append({"pmid": r.get("pmid"), "pmcid": r.get("pmcid"),
                         "year": r.get("year"), "title": r.get("title")})
    return {
        "_status": "READ",
        "corpus_ref": CD248.CORPUS_REF, "corpus_dir": CORPUS_DIR, "query": CORPUS_QUERY,
        "n_records_retrieved": len(rows),
        "n_records_actually_about_the_antigen": len(on_topic),
        "⚠_why_two_denominators": (
            "The query is broad — 'CD166', 'antibody' and 'sarcoma' co-occur in thousands of "
            "papers that never mention this antigen. Counting EMC mentions over the whole "
            "retrieval would use a denominator that means nothing, so the on-topic subset is "
            "computed first and IS the denominator that matters."),
        "n_on_topic_records_mentioning_EMC": len(hits),
        "on_topic_records_mentioning_EMC": hits,
        "verdict": ("⭐ ZERO on-topic records name EMC or its fusion. The ALCAM literature "
                    "contains no EMC observation, so the EMC reading in "
                    "emc-expression-panels.json is the only one that exists."
                    if not hits else
                    "⚠ On-topic records naming EMC ARE present — read them before quoting a gap."),
    }


def derive():
    return {
        "_what": "ALCAM / CD166: the binder precedent behind the one antigen that survived the "
                 "2026-08-07 EMC surface read, and the normal-tissue liability its RNA prior "
                 "could not show.",
        "_execution_model": "$0. A Europe PMC retrieval already performed in CI, plus committed "
                            "artifacts.",
        "_language_discipline": (
            "⛔ NOTHING HERE IS AN EFFICACY, SELECTIVITY, SAFETY, THERAPEUTIC-WINDOW OR CLINICAL-"
            "READINESS CLAIM FOR ALCAM OR ANY ALCAM-DIRECTED AGENT IN EMC. No ALCAM-directed "
            "agent has been given to an EMC patient, no trial outcome is characterised here, and "
            "the EMC evidence for this antigen is a transcript contrast in n=6 and n=10 archival "
            "tumours."),
        "the_emc_reading_this_rests_on": {
            "artifact": "research/modalities/emc-expression-panels.json",
            "address": "reads.read_7_SURFACE_ANTIGEN.cross_platform_board.per_gene.ALCAM",
            "⛔_not_re_typed_here": "The SD, t and percentile figures have their one home there.",
        },
        "binder_precedent": RECORDS,
        "modality_ladder": {
            "_what": "What stage each ALCAM-directed format has reached. ⛔ 'A binder exists' is "
                     "the ONLY thing this establishes.",
            "antibody_drug_conjugate": "REACHED PATIENTS — a phase I/II trial of a CD166-targeting "
                                       "Probody-drug conjugate in advanced solid tumours "
                                       "(binder_precedent.clinical_adc_praluzatamab_ravtansine). "
                                       "No outcome is characterised here and no sarcoma or EMC "
                                       "cohort is claimed.",
            "car_t": "PRECLINICAL (osteosarcoma and colorectal constructs).",
            "immuno_PET": "PRECLINICAL (89Zr and 64Cu tracers in xenografts).",
            "anything_at_all_in_EMC": "NONE. See `emc_specific_evidence`.",
        },
        "normal_tissue_liability": NORMAL_TISSUE_LIABILITY,
        "emc_specific_evidence": emc_specific_evidence(),
        "⛔_the_three_things_that_would_have_to_be_true_and_are_not_known": [
            "THAT THE PROTEIN IS ON THE EMC CELL SURFACE. The EMC evidence is transcript, and "
            "HPA's own subcellular annotation for ALCAM in emc-surface-normal-window.json is "
            "['Vesicles'] with plasma_membrane_confirmed false. IHC or surface proteomics on EMC "
            "tissue would settle it; nothing here does.",
            "THAT THE ELEVATION IS ABOUT EMC RATHER THAN ABOUT MESENCHYMAL LINEAGE. ALCAM is an "
            "MSC marker and the contrast is against other sarcomas. Single-cell or spatial EMC "
            "data would separate tumour cell from stroma; a broader tumour-type panel would test "
            "the lineage confound. Neither is in hand.",
            "THAT A WINDOW EXISTS AT ALL. HSC niche, MSC, perichondrium and CD6/T-cell expression "
            "are all documented, and the clinical agent is masked for that reason.",
        ],
        "⛔_what_this_file_does_NOT_claim": [
            "That ALCAM is a validated EMC target, or a target at all.",
            "That any ALCAM-directed agent works, is safe or is selective — in EMC or anywhere.",
            "That the phase I/II trial produced a positive result; its outcome is not "
            "characterised here.",
            "That a RESTRICTED HPA window is a safety statement. It is not, and for this antigen "
            "the primary literature shows why.",
            "Anything about a patient.",
        ],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--check", action="store_true")
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
    print(f"corpus: {e.get('_status')} retrieved={e.get('n_records_retrieved')} "
          f"on_topic={e.get('n_records_actually_about_the_antigen')} "
          f"EMC-mentioning={e.get('n_on_topic_records_mentioning_EMC')}")
    print(f"verdict: {e.get('verdict') or e.get('why')}")
    for k, v in res["modality_ladder"].items():
        if not k.startswith("_"):
            print(f"  {k:<28} {v[:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
