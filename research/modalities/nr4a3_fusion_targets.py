#!/usr/bin/env python3
"""
WHAT DOES EWSR1::NR4A3 ACTUALLY TRANSCRIBE, AND IS IT UP IN EMC TISSUE?

⭐ WHY THIS LANE EXISTS. Almost everything this repository holds on EWSR1::NR4A3 concerns whether
the protein can be DRUGGED, and every one of those routes terminates in a free-energy measurement
nobody here can make. The transcriptional-output question terminates instead in expression and
sequence facts, which are exactly what $0 can reach. So this module asks the other question: what
does the fusion put into a cell, and does the published answer reproduce in EMC tumour tissue?

⛔⛔ THE ONE THING THIS MODULE IS BUILT TO NOT DO. A gene that is high in EMC is consistent with
the fusion driving it AND with several other things — with EMC's cell of origin, with its myxoid
stroma, with its low cellularity against dense comparator sarcomas, and with a platform-wide offset
between the two arms. **So a raw "HIGHER in EMC" number is not evidence for a target programme.**
Every score here is therefore calibrated against a SIZE-MATCHED EMPIRICAL NULL drawn from the same
platform's own readable genes, and the global EMC-vs-comparator offset over ALL readable genes is
measured and reported beside it. A set that beats the offset and beats its null has said something;
a set that merely rides them has not, and prints so.

⛔ FOUR EVIDENCE CLASSES, NEVER POOLED. `LITERATURE_TARGETS` records, per gene, WHICH protein was
tested and WITH WHAT ASSAY, because a luciferase reporter in a rat cell line and a ChIP peak in a
human one are not the same claim:
    A. `fusion_dna_binding`  — a DNA-binding or promoter assay performed with an NR4A3 FUSION
                               (EWSR1::NR4A3, TAF15::NR4A3 or TFG::NR4A3). The strongest class.
    B. `native_dna_binding`  — the same assay class, native NR4A3. Transfer to the fusion is an
                               ASSUMPTION (the chimera keeps the NR4A3 DBD) and it is a testable one
                               that has already failed once — see `PPARG` and `SEMA3C` below.
    C. `fusion_expression_only` — the gene moves when the fusion is expressed, with no binding
                               assay. Correlative inside the model as well as outside it.
    D. `emc_tumour_expression_only` — measured in EMC tissue, no mechanism.
An aggregate score is emitted PER CLASS. There is no "all published targets" number, because that
number would average a ChIP peak with a microarray row.

⛔ LANGUAGE DISCIPLINE. Nothing here is an efficacy, selectivity, safety, therapeutic-window or
clinical-readiness claim, and nothing here may be written as one. n = 6 and n = 10 tumours, two
decade-old array platforms, uncorrected for multiple testing.

$0 — a GitHub-hosted CPU runner, no GPU, no rental. Pure stdlib. The dev sandbox's egress proxy
403s NCBI/GEO on CONNECT, which is the whole reason this runs in CI (CLAUDE.md §6).

Usage:
    python nr4a3_fusion_targets.py --fetch    # CI: fetch + derive + write both files
    python nr4a3_fusion_targets.py            # derive from the cached inputs (offline)
    python nr4a3_fusion_targets.py --check    # re-derive offline and diff against the artifact
"""

import argparse
import json
import os
import random
import re
import sys
from bisect import bisect_left, bisect_right
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "nr4a3-fusion-targets.json")
INPUTS = os.path.join(HERE, "nr4a3-fusion-targets-inputs.json")

sys.path.insert(0, HERE)
from emc_atr_vulnerability import (  # noqa: E402
    ENRICHR_LIB,
    _classify_sample,
    _geo_matrix_dir,
    _get,
    _get_once,
    _gpl_symbols,
    _norm,
    _parse_series_matrix,
    _welch,
)

FRAMING = (
    "TRANSCRIPTIONAL OUTPUT OF THE EMC FUSION, READ IN EMC TUMOUR TISSUE. Every number here is a "
    "transcript-level reading in archival tumour material on two array platforms, calibrated "
    "against a size-matched empirical null on the same platform. It is NOT evidence of efficacy, "
    "selectivity, safety, a therapeutic window or clinical readiness for any agent named anywhere "
    "in this file, and it cannot become that evidence from public expression data."
)

# =============================================================================================
# THE TWO READABLE SERIES.
# Named, not searched. Both are already characterised — with their probe mapping rates — in
# `emc-atr-vulnerability.json` -> part_b_emc_tumour_signature.series_readability, which is the ONE
# HOME of that characterisation (CLAUDE.md §1). The rates below are quoted from it as the PRIOR
# this run is checked against, and the run records its own measured rate beside them.
#
# ⚠ THE SERIES RECORD IS FETCHED, NOT ASSUMED. §"circularity" below turns on whether GSE4303 is
# the dataset behind Subramanian et al. 2005 — the same cohort one of the candidate gene lists is
# derived from. That is a fact about a GEO record, so it is READ from the GEO record (title,
# summary, contributor, linked PubMed id, verbatim) rather than inferred from sample counts.
# =============================================================================================
TARGETS = [
    {"gse": "GSE24369",
     "matrix_file": "GSE24369_series_matrix.txt.gz",
     "platform_expected": "GPL6244",
     "why": "6 EMC tumours against 29 comparator sarcomas on one Affymetrix Gene ST array, and the "
            "comparator arm is itself FET-rearranged (LGFMS is FUS::CREB3L2), so a difference here "
            "is not merely 'has a FET fusion'.",
     "prior_probe_mapping_rate": 0.932,
     "prior_source": "emc-atr-vulnerability.json -> part_b_emc_tumour_signature."
                     "series_readability.GSE24369.probe_mapping_rate_per_platform.GPL6244"},
    {"gse": "GSE4303",
     "matrix_file": "GSE4303-GPL3290_series_matrix.txt.gz",
     "platform_expected": "GPL3290",
     "why": "10 EMC tumours against 3 DFSP and 3 GIST on the same two-colour cDNA print run. Probes "
            "carry EST accessions only, so the read depends on the accession->symbol bridge.",
     "prior_probe_mapping_rate": 0.582,
     "prior_source": "emc-atr-vulnerability.json -> part_b_emc_tumour_signature."
                     "series_readability.GSE4303.probe_mapping_rate_per_platform.GPL3290"},
]

GEO_ACC = ("https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={}&targ=self&form=text&view=brief")

# =============================================================================================
# THE EVIDENCE-TYPED TARGET TABLE.
#
# Every row was read from a retrieved document — the committed Europe PMC corpora on the
# `literature-cache` branch (`literature/extraskeletal-myxoid-chondrosarcoma/`,
# `literature/nr4a3-cistrome-tight/`, `literature/nr4a3-fusion-partners/`,
# `literature/pparg-direction-emc-2026-08-06/`) — never from memory. `verbatim` is the sentence the
# classification rests on. Where the sentence comes from a REVIEW rather than the primary paper,
# `via` names the review and the row is graded one class lower on `directness_of_the_record`.
#
# ⚠ `factor_tested` IS THE COLUMN THAT MATTERS, and it is not decorative. Filion et al. measured
# both the fusion and native NR4A3 on the same PPARG promoter reporter and found that the NATIVE
# receptor does not activate it. So "NR4A3 binds X" does not license "the fusion drives X in EMC",
# and Brenca et al. found the converse failure in the other direction (TAF15::NR4A3 cannot bind a
# site EWSR1::NR4A3 and native NR4A3 both can). Two independent demonstrations that the transfer
# assumption is real and sometimes false.
# =============================================================================================
FUSION_DNA_BINDING = "fusion_dna_binding"
NATIVE_DNA_BINDING = "native_dna_binding"
FUSION_EXPRESSION = "fusion_expression_only"
EMC_TISSUE_EXPRESSION = "emc_tumour_expression_only"

LITERATURE_TARGETS = [
    # ---------------------------------------------------------------------------------------
    # CLASS A — a DNA-binding / promoter assay performed WITH AN NR4A3 FUSION.
    # ---------------------------------------------------------------------------------------
    {
        "gene": "SEMA3C",
        "evidence_class": FUSION_DNA_BINDING,
        "factor_tested": ["EWSR1::NR4A3", "TAF15::NR4A3", "NR4A3 (native)"],
        "assays": ["in-silico NBRE-like site (MatInspector, GRCh38 chr7)",
                   "chromatin affinity purification + target qPCR (ChAP-qPCR), Strep-tagged"],
        "system": "tBJ/ER transformed HUMAN fibroblasts engineered to express Strep-tagged NR4A3, "
                  "EWSR1-NR4A3 (E-N) or TAF15-NR4A3 (T-N)",
        "species_of_the_cells": "human",
        "citation": "Brenca M, Stacchiotti S, Fassetta K, et al. NR4A3 fusion proteins trigger an "
                    "axon guidance switch that marks the difference between EWSR1 and TAF15 "
                    "translocated extraskeletal myxoid chondrosarcomas. J Pathol "
                    "2019;249(1):90-101. PMID 31020999, PMCID PMC6766969, doi 10.1002/path.5284",
        "verbatim": "ChAP-qPCR experiments confirmed the ability of NR4A3 to bind the predicted "
                    "target on SEMA3C. More interestingly, the ability of NR4A3 to recognize the "
                    "SEMA3C target region was retained by the EWSR1-NR4A3 chimera but was impaired "
                    "by TAF15-NR4A3, in line with transcriptional profiling data.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "SEMA3C is bound by EWSR1::NR4A3 and is reported more abundant in "
                              "EWSR1-translocated than in TAF15-translocated EMC. Both readable "
                              "series pool EMC of unknown fusion type, so a TAF15 fraction DILUTES "
                              "this expectation rather than reversing it.",
        "note": "★ The single best-evidenced direct target of EWSR1::NR4A3: a human cell "
                "background, the actual EWSR1 chimera, and a chromatin-binding assay. It is also "
                "the row that shows the transfer assumption failing in the other direction — the "
                "TAF15 chimera, which is EMC's second-commonest fusion, could not bind it.",
    },
    {
        "gene": "PPARG",
        "evidence_class": FUSION_DNA_BINDING,
        "factor_tested": ["EWSR1::NR4A3", "NR4A3 (native)", "NR4A3-deltaC (native truncated)"],
        "assays": ["predicted perfect NBRE at -675 bp (5' AAAGGTCA 3')",
                   "band-shift (EMSA) with the fusion protein",
                   "2.8 kb human PPARG isoform-1 promoter luciferase reporter",
                   "single-nucleotide NBRE mutant of that reporter"],
        "system": "CFK2 fetal RAT chondrogenic cells, stable EWSR1/NR4A3 lines (et2, et16, et19) "
                  "and transient transfection of wild-type CFK2; HUMAN PPARG promoter construct",
        "species_of_the_cells": "rat (the promoter construct is human)",
        "citation": "Filion C, Motoi T, Olshen AB, et al. The EWSR1/NR4A3 fusion protein of "
                    "extraskeletal myxoid chondrosarcoma activates the PPARG nuclear receptor "
                    "gene. J Pathol 2009;217(1):83-93. PMID 18855877, PMCID PMC4429309, "
                    "doi 10.1002/path.2445",
        "verbatim": "Transient transfections of CFK2 cells with EWSR1/NR4A3 and the wild-type or "
                    "mutated promoter clearly show that this single nucleotide change drastically "
                    "reduces the ability of the fusion protein to activate transcription of PPARG. "
                    "... Thus, the PPARG promoter is a target of aberrant transactivation by the "
                    "EWSR1/NR4A3 fusion protein in EMC tumors.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "Directly transactivated by the fusion, and independently over-"
                              "expressed in EMC tumours in two cohorts.",
        "note": "★★ THE ROW THAT DISPROVES THE TRANSFER ASSUMPTION. Same paper, same reporter: "
                "'the results show that both the native and truncated receptors do not activate "
                "PPARG transcription under the same conditions in which it is readily activated by "
                "the fusion protein.' So a native-NR4A3 cistrome does not predict this target, and "
                "a fusion target need not be a native one. ⚠ The direction of any PHARMACOLOGY on "
                "this axis is NOT settled by this row and has its one home in "
                "`research/manuscripts/pparg-direction-emc.md` §6.",
    },
    {
        "gene": "ENO3",
        "evidence_class": FUSION_DNA_BINDING,
        "factor_tested": ["TFG::NR4A3 (TFG-TEC)"],
        "assays": ["EMSA", "ChIP (endogenous promoter)", "luciferase reporter",
                   "two NGFI-B response element motifs upstream of the putative TSS",
                   "ChIP for histone H3 acetylation at the endogenous promoter"],
        "system": "cultured cell lines over-expressing TFG-TEC (the t(3;9) EMC fusion variant)",
        "species_of_the_cells": "human (human beta-enolase promoter)",
        "citation": "Kim AY, Lim B, Choi J, Kim J. The TFG-TEC oncoprotein induces transcriptional "
                    "activation of the human beta-enolase gene via chromatin modification of the "
                    "promoter region. Mol Carcinog 2016. PMID 26310886, doi 10.1002/mc.22384",
        "verbatim": "EMSAs, ChIP assays, and luciferase reporter assays revealed that TFG-TEC "
                    "upregulates beta-enolase transcription by binding to two NGFI-B response "
                    "element motifs located upstream of the putative transcription start site.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "The repository's instrument POSITIVE CONTROL. It reproduces a "
                              "committed value to three decimals on both platforms.",
        "note": "⚠ THE FUSION TESTED IS TFG::NR4A3, NOT EWSR1::NR4A3. TFG::NR4A3 is a genuine but "
                "rare EMC fusion variant (t(3;9)(q11-12;q22)); the dominant chimera was not the "
                "one assayed. Corroborated in a DIFFERENT direction by Haller et al. 2019 "
                "(PMC6341107), where native human NR4A3 over-expression raised mouse Eno3 mRNA and "
                "protein and ENO3 was higher in NR4A3-driven human AciCC tissue than in normal "
                "parotid — so ENO3 is the one gene here supported by both a fusion binding assay "
                "and a native over-expression readout in tissue.",
    },
    # ---------------------------------------------------------------------------------------
    # CLASS B — a DNA-binding / promoter assay with NATIVE NR4A3 (NOR-1). Transfer to the fusion is
    # an assumption, stated as one on every row.
    # ---------------------------------------------------------------------------------------
    {
        "gene": "CCND1",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["ChIP at the Cyclin D1 promoter", "NBRE site"],
        "system": "hepatocytes; vascular smooth muscle cells; guidewire arterial-injury model in "
                  "NOR-1-deficient mice",
        "species_of_the_cells": "mouse / rat vascular and hepatic cells",
        "citation": "Reviewed in Herring JA, Elison WS, Tessem JS. Function of Nr4a Orphan Nuclear "
                    "Receptors in Proliferation, Apoptosis and Fuel Utilization Across Tissues. "
                    "Cells 2019;8:1373. PMID 31683815, PMCID PMC6912296; and in Haller F, et al. "
                    "Nat Commun 2019;10:368. PMID 30664630, PMCID PMC6341107",
        "via": "review",
        "verbatim": "Chromatin immunoprecipitation (ChIP) revealed that Nr4a3 directly interacts "
                    "with the Cyclin D1 promoter, demonstrating that it is a direct Nr4a3 target "
                    "in hepatocytes.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "A canonical NR4A3 target; Haller et al. list it with ENO3 as one of "
                              "the two 'known NR4A3 target genes' they tested, and both were "
                              "higher in NR4A3-driven human tumour tissue.",
        "note": "The NBRE that Brenca et al. found in the SEMA3C regulatory region is, in their "
                "own words, 'a consensus sequence targeted by NR4A3 to regulate CCND1' — so the "
                "CCND1 and SEMA3C rows rest on the same motif.",
    },
    {
        "gene": "SKP2",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["EMSA", "ChIP", "NBRE site in the SKP2 promoter"],
        "system": "vascular smooth muscle cells",
        "species_of_the_cells": "human/rodent VSMC (the review does not disambiguate)",
        "citation": "Reviewed in Martinez-Gonzalez J, et al. NR4A3: A Key Nuclear Receptor in "
                    "Vascular Biology, Cardiovascular Remodeling, and Beyond. Int J Mol Sci "
                    "2021;22:11371. PMID 34768801, PMCID PMC8583700",
        "via": "review",
        "verbatim": "Electrophoretic mobility shift and chromatin immunoprecipitation assays "
                    "provided evidence that NOR-1 transactivates SKP2 promoter by binding to a "
                    "NBRE site.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "A direct NR4A3 target with two orthogonal binding assays behind it, "
                              "used elsewhere as the POSITIVE CONTROL region for NR4A3 ChIP "
                              "(Zhao X, et al. Int J Biol Sci 2024, PMCID PMC11628324: 'We used "
                              "Skp2 as a positive control for NR4A3 in the ChIP experiment').",
    },
    {
        "gene": "VTN",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["listed by an independent review as a functionally validated direct target",
                   "over-expression + blocking-antibody / silencing rescue of migration",
                   "co-localisation in human atherosclerotic lesions"],
        "system": "vascular smooth muscle cells; independently raised >2-fold by NR4A3 "
                  "over-expression in the human MHCC-LM3 hepatocellular line",
        "species_of_the_cells": "human",
        "citation": "Haller F, et al. Nat Commun 2019;10:368. PMID 30664630, PMCID PMC6341107 "
                    "(target list); Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, "
                    "PMCID PMC8583700 (VSMC); Zhao X, et al. Int J Biol Sci 2024, "
                    "PMCID PMC11628324 (MHCC-LM3)",
        "via": "review",
        "verbatim": "Only few genes including the cell cycle regulator Cyclin D1 (CCND1), the "
                    "metabolic enzyme Enolase 3 (ENO3), the secreted serum and extracellular "
                    "matrix glycoprotein Vitronectin (VTN), and the nuclear receptor and "
                    "transcriptional regulator Peroxisome Proliferator Activated Receptor Gamma "
                    "(PPARG) have been functionally validated as direct targets of NR4A3 or the "
                    "NR4A3-EWSR1 fusion protein in different in vitro cell models.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "One of the four genes an independent review names as functionally "
                              "validated direct targets of NR4A3 or the fusion.",
    },
    {
        "gene": "SMPX",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["promoter deletion", "site-directed mutagenesis of a non-consensus NBRE "
                   "(-167/-160)", "EMSA", "ChIP in differentiating human skeletal myoblasts"],
        "system": "human vascular smooth muscle cells and HSMM myoblasts",
        "species_of_the_cells": "human",
        "citation": "Ferran B, Marti-Pamies I, Alonso J, et al. The nuclear receptor NOR-1 "
                    "regulates the small muscle protein, X-linked (SMPX) and myotube "
                    "differentiation. Sci Rep 2016;6:25944. PMID 27181368, PMCID PMC4867575",
        "verbatim": "By transcriptional studies and DNA-protein binding assays, we identified a "
                    "non-consensus NBRE site in human SMPX promoter, critical for NOR-1 "
                    "responsiveness.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "Four orthogonal assays in HUMAN cells on a HUMAN promoter — the "
                              "most completely worked-out native-NR4A3 target in the table.",
        "note": "★ SPECIES-SPECIFIC BY MEASUREMENT, NOT BY ASSUMPTION: the same paper reports that "
                "'mouse SMPX seems to be unresponsive to NOR-1, as far as no NOR-1 response "
                "elements could be detected in mouse SMPX promoter'. A mouse-derived NR4A3 target "
                "list would have missed this gene entirely.",
    },
    {
        "gene": "CDKN2AIP",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["ChIP at predicted sites in the CDKN2AIP promoter",
                   "luciferase reporter reversed by promoter mutant"],
        "system": "MHCC-LM3 human hepatocellular carcinoma cells",
        "species_of_the_cells": "human",
        "citation": "Zhao X, Min X, Wang Z, et al. NR4A3 inhibits the tumor progression of "
                    "hepatocellular carcinoma by inducing cell cycle G0/G1 phase arrest and "
                    "upregulation of CDKN2AIP expression. Int J Biol Sci 2024. PMID 39664575, "
                    "PMCID PMC11628324, doi 10.7150/ijbs.95174",
        "verbatim": "The results of the luciferase assay further showed that the relative "
                    "luciferase activity of the CDKN2AIP promoter was significantly induced by the "
                    "overexpression of NR4A3, and the luciferase activity was reversed by "
                    "transfection of the mutant.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "Direct binding plus a mutation-reversed reporter, in human cells.",
        "note": "⚠ In that paper NR4A3 is TUMOUR-SUPPRESSIVE. The DIRECTION OF THE TRANSCRIPTIONAL "
                "EFFECT is what this table records; the phenotype it produces is context-dependent "
                "and is NOT transferred to EMC by this row.",
    },
    {
        "gene": "GLS2",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["ChIP-seq + mRNA-seq", "dual-luciferase reporter",
                   "abolished by mutation of the predicted NR4A3 motif"],
        "system": "Schwann cells (diabetic peripheral neuropathy model)",
        "species_of_the_cells": "rat/mouse Schwann cells",
        "citation": "Pang B, Chen S, Bai Y, Zhang Y, Wang Z. NR4A3 alleviates diabetic neuropathy "
                    "via GLS2-mediated mitochondrial repair and Schwann cell differentiation. "
                    "iScience 2026. PMID 42028030, PMCID PMC13099357, "
                    "doi 10.1016/j.isci.2026.115515",
        "verbatim": "Importantly, mutation of the predicted NR4A3-binding motif within the GLS2 "
                    "promoter abolished this transactivation effect.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "Binding plus a motif-mutation-abolished reporter.",
    },
    {
        "gene": "SDHA",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["Cut&Tag", "truncated-promoter dual-luciferase mapping to region R3 "
                   "(predicted element AAAGTCAC)"],
        "system": "neonatal mouse cardiomyocytes; HEK293T for the HUMAN SDHA promoter reporter",
        "species_of_the_cells": "mouse cardiomyocytes; human HEK293T for the reporter",
        "citation": "Peng H, Yuan J, Wang Z, et al. NR4A3 prevents diabetes induced atrial "
                    "cardiomyopathy by maintaining mitochondrial energy metabolism and reducing "
                    "oxidative stress. eBioMedicine 2024;106:105268. PMID 39098108, "
                    "PMCID PMC11334830, doi 10.1016/j.ebiom.2024.105268",
        "verbatim": "We elucidated the specific NR4A3 response element in the SDHA promoter region "
                    "through Cut&Tag assays and dual luciferase-reporter assays.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "Chromatin binding plus a mapped element on the human promoter.",
    },
    {
        "gene": "COX5A",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["Cut&Tag over the promoter", "dual-luciferase reporter"],
        "system": "neonatal mouse cardiomyocytes; HEK293T reporter",
        "species_of_the_cells": "mouse; human reporter construct",
        "citation": "Peng H, et al. eBioMedicine 2024;106:105268. PMID 39098108, "
                    "PMCID PMC11334830",
        "verbatim": "Cut&Tag assay using neonatal mouse cardiomyocytes (NMCMs) was performed to "
                    "identify potential NR4A3 response elements in the promoter regions of Pdp1, "
                    "Sdha, and Cox5a.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "Same experiment as SDHA; the element was mapped for SDHA only, so "
                              "this row is the weaker half of that paper.",
    },
    {
        "gene": "PDP1",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["Cut&Tag over the promoter"],
        "system": "neonatal mouse cardiomyocytes",
        "species_of_the_cells": "mouse",
        "citation": "Peng H, et al. eBioMedicine 2024;106:105268. PMID 39098108, "
                    "PMCID PMC11334830",
        "verbatim": "Cut&Tag assay using neonatal mouse cardiomyocytes (NMCMs) was performed to "
                    "identify potential NR4A3 response elements in the promoter regions of Pdp1, "
                    "Sdha, and Cox5a.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "Chromatin binding only; no reporter mapped for this gene.",
    },
    {
        "gene": "VCAM1",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["binding to the NBRE consensus site"],
        "system": "TNF-stimulated endothelial cells / monocyte adhesion",
        "species_of_the_cells": "human endothelial",
        "citation": "Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, "
                    "PMCID PMC8583700; and PMCID PMC10088923",
        "via": "review",
        "verbatim": "Upon TNF stimulation, NR4A3 mediates monocyte adhesion by inducing the "
                    "expression of VCAM1 and ICAM1 by binding to the NBRE consensus site.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "NBRE-mediated induction, but in an inflammatory endothelial context "
                              "that EMC tumour tissue does not obviously reproduce.",
    },
    {
        "gene": "ICAM1",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["binding to the NBRE consensus site"],
        "system": "TNF-stimulated endothelial cells / monocyte adhesion",
        "species_of_the_cells": "human endothelial",
        "citation": "Reviewed in PMCID PMC8583700 / PMC10088923 / PMC9100886",
        "via": "review",
        "verbatim": "NR4A3 binds to NBRE to induce the expression of VCAM1 and ICAM1 and the "
                    "adhesion of monocytes.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "As VCAM1.",
    },
    {
        "gene": "BIRC3",
        "aliases": ["cIAP2", "API2"],
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["NBRE binding site"],
        "system": "vascular smooth muscle cells / hypoxic endothelium",
        "species_of_the_cells": "human/rodent vascular",
        "citation": "Reviewed in PMCID PMC6912296 and PMC8583700",
        "via": "review",
        "verbatim": "Nr4a3 directly regulates cIAP2 expression in VSMC through an NBRE binding "
                    "site.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "NBRE-mediated; the anti-apoptotic arm of the vascular NOR-1 "
                              "programme.",
    },
    {
        "gene": "NOX1",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["gene silencing", "luciferase reporter", "site-directed mutagenesis", "EMSA"],
        "system": "vascular smooth muscle cells; co-localisation in human atheroma",
        "species_of_the_cells": "human",
        "citation": "Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, "
                    "PMCID PMC8583700",
        "via": "review",
        "verbatim": "Both NOR-1 and NOX-1 co-localize in human atheroma and gene silencing, "
                    "luciferase reporter, site-directed mutagenesis, and EMSA studies confirmed "
                    "the regulation of NOX-1 transcription by NOR-1.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "Four orthogonal assays, human cells.",
    },
    {
        "gene": "TH",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["transient transfection through an NBRE site in the TH promoter"],
        "system": "vascular smooth muscle cells; NOR-1 transgenic mouse aorta",
        "species_of_the_cells": "mouse / VSMC",
        "citation": "Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, "
                    "PMCID PMC8583700",
        "via": "review",
        "verbatim": "Interestingly, transient transfection studies evidenced that NOR-1 regulates "
                    "TH transcriptional activity through a NBRE site located in its promoter.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "NBRE-mediated reporter only.",
    },
    {
        "gene": "LOXL2",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["named a direct NOR-1 target gene in the source review"],
        "system": "cardiac fibroblast-to-myofibroblast switch, NOR-1 transgenic mice",
        "species_of_the_cells": "mouse",
        "citation": "Reviewed in Martinez-Gonzalez J, et al. Int J Mol Sci 2021;22:11371, "
                    "PMCID PMC8583700",
        "via": "review",
        "verbatim": "This response is characterized by the up-regulation of hypertrophic and "
                    "fibrotic markers such as Myh7 and lysyl oxidase-like 2 (LOXL2), both of them "
                    "identified as direct NOR-1 target genes.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "Called direct by the review; the assay class is not stated in the "
                              "sentence, which is why this row sits at the bottom of class B.",
    },
    {
        "gene": "MYH7",
        "evidence_class": NATIVE_DNA_BINDING,
        "factor_tested": ["NR4A3 (native)"],
        "assays": ["named a direct NOR-1 target gene in the source review"],
        "system": "cardiac hypertrophy, NOR-1 transgenic mice",
        "species_of_the_cells": "mouse",
        "citation": "Reviewed in PMCID PMC8583700",
        "via": "review",
        "verbatim": "such as Myh7 and lysyl oxidase-like 2 (LOXL2), both of them identified as "
                    "direct NOR-1 target genes.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "As LOXL2. A cardiac-muscle gene, so a flat read in EMC is "
                              "unsurprising and carries little information either way.",
    },
    # ---------------------------------------------------------------------------------------
    # CLASS C — the gene MOVES when the fusion is expressed, with NO binding assay.
    # ---------------------------------------------------------------------------------------
    {
        "gene": "SGK1",
        "evidence_class": FUSION_EXPRESSION,
        "factor_tested": ["EWSR1::NR4A3"],
        "assays": ["differential display in a tetracycline-regulated fusion line",
                   "co-immunocytochemistry", "immunohistochemistry in 10 fusion-positive EMC"],
        "system": "CFK2 fetal RAT chondrogenic cells with tetracycline-controlled EWS/NOR1",
        "species_of_the_cells": "rat",
        "citation": "Labelle Y, et al. Serum- and glucocorticoid-regulated kinase 1 (SGK1) "
                    "induction by the EWS/NOR1(NR4A3) fusion protein. Biochem Biophys Res Commun "
                    "2006. PMID 16756948, doi 10.1016/j.bbrc.2006.05.134",
        "verbatim": "Using the differential display technique, we have identified the serum- and "
                    "glucocorticoid-regulated kinase 1 (SGK1) mRNA as being up-regulated in the "
                    "presence of EWS/NOR1. ... immunohistochemistry of 10 EMC tumors positive for "
                    "EWS/NOR1 showed that all of them over-express the SGK1 protein.",
        "expected_direction_in_EMC": "FLAT_OR_DOWN_AT_TRANSCRIPT_LEVEL",
        "why_that_direction": "★★ A PRE-REGISTERED DISCORDANCE, NOT A GUESS. Filion et al. 2009 "
                              "state in the same programme: 'our tumor expression microarray data "
                              "suggest a LOWER level of this mRNA in EMC than in other sarcomas ... "
                              "also consistent with the data of Subramanian and colleagues', while "
                              "the PROTEIN is over-expressed — which they attribute to an SGK1 "
                              "isoform lacking the proteasomal degradation signal. So a transcript "
                              "instrument SHOULD read SGK1 flat or down in EMC. This row is "
                              "therefore a NEGATIVE control on the reading direction: if SGK1 came "
                              "back strongly UP, the instrument would be suspect, not the paper.",
    },
    {
        "gene": "PLAGL1",
        "aliases": ["ZAC1", "LOT1"],
        "evidence_class": FUSION_EXPRESSION,
        "factor_tested": ["EWSR1::NR4A3"],
        "assays": ["differential display in a fusion-expressing line", "RT-PCR in six EMC tumours"],
        "system": "CFK2 chondrogenic cells over-expressing EWS/NOR1; human EMC tumours vs "
                  "immortalised and primary human chondrocytes",
        "species_of_the_cells": "rat cells; human tumours",
        "citation": "Filion C, et al. The PLAGL1 gene is down-regulated in human extraskeletal "
                    "myxoid chondrosarcoma tumors. Cancer Lett 2005. PMID 16112421, "
                    "doi 10.1016/j.canlet.2004.12.007",
        "verbatim": "A differential display analysis has identified the PLAGL1 gene as being "
                    "down-regulated in the CFK2(EWS/NOR1) cell line compared to native CFK2 cells. "
                    "RT-PCR analyses show that ... they are strongly down-regulated in six EMC "
                    "tumors.",
        "expected_direction_in_EMC": "DOWN",
        "why_that_direction": "★★ THE DIRECTIONAL FALSIFIER. Every other row in this table predicts "
                              "UP. If the instrument were simply reporting 'EMC differs from dense "
                              "comparator sarcomas', PLAGL1 would drift up with everything else. A "
                              "published DOWN prediction that reads DOWN is the one observation "
                              "here that a global offset cannot manufacture.",
    },
    # ---------------------------------------------------------------------------------------
    # CLASS D — measured in EMC tissue, no mechanism.
    # ---------------------------------------------------------------------------------------
    {
        "gene": "NDRG2",
        "evidence_class": EMC_TISSUE_EXPRESSION,
        "factor_tested": [],
        "assays": ["Affymetrix U133A microarray, 3 fusion-positive EMC vs 137 other sarcomas",
                   "Western blot", "immunohistochemistry in 9/9 EWSR1/NR4A3-positive EMC"],
        "system": "human EMC tumour tissue",
        "species_of_the_cells": "human",
        "citation": "Filion C, et al. J Pathol 2009;217(1):83-93. PMID 18855877, PMCID PMC4429309",
        "verbatim": "we performed immunohistochemistry analyses which confirmed that NDRG2 is "
                    "moderately to strongly expressed in the cytoplasm of EMC tumor cells in 9/9 "
                    "EWSR1/NR4A3-positive EMCs.",
        "expected_direction_in_EMC": "UP",
        "why_that_direction": "Over-expressed in EMC in two independent cohorts. ⛔ NOT a "
                              "transcriptional target of the fusion — Filion et al. examine it as "
                              "a PHOSPHORYLATION substrate of SGK1, which is a different claim.",
    },
]

# =============================================================================================
# A NEGATIVE CONTROL THAT IS A PUBLISHED NEGATIVE, NOT A GUESS.
# =============================================================================================
PUBLISHED_NEGATIVE = {
    "gene": "CALD1",
    "claim": "Its promoter was searched for NOR-1 response elements in the same experiment that "
             "found the SMPX site, and NONE were found.",
    "citation": "Ferran B, et al. Sci Rep 2016;6:25944. PMID 27181368, PMCID PMC4867575",
    "verbatim": "While no NOR-1 response elements were detected in the promoter of the caldesmon "
                "encoding gene (CALD1), in silico analysis revealed the presence of four putative "
                "NBRE binding sites in the SMPX promoter.",
    "expected_direction_in_EMC": "NO_EXPECTATION_FROM_NR4A3",
    "why_it_is_here": "⚠ IT IS A CONTROL ON THE MOTIF, NOT ON EMC. CALD1 is a smooth-muscle/"
                      "myofibroblast gene and EMC differs from DFSP/GIST comparators on exactly "
                      "that axis, so a non-flat CALD1 read is NOT evidence against the motif "
                      "logic. What it controls is the inference 'this gene moved, therefore NR4A3 "
                      "bound it' — a gene with no NBRE that moves anyway shows how much movement "
                      "the tissue contrast alone produces.",
}

# =============================================================================================
# PUBLISHED EMC-vs-SARCOMA PROFILING LISTS — a DIFFERENT question, kept apart, and one of the two
# is CIRCULAR against one of the two platforms.
#
# ⛔ THIS IS THE MOST DANGEROUS BLOCK IN THE FILE. Filion et al. 2009 Table 2 lists the genes their
# EMC profile shares with the top 50 of Subramanian et al. 2005 — and Subramanian et al. 2005 is
# the study behind a GEO series with 10 EMC on a 42,000-spot cDNA platform, which is what
# GSE4303/GPL3290 is. Scoring Table 2 on GPL3290 would be scoring a gene list on the data it was
# derived from. Table 1 (EMC vs 137 sarcomas on Affymetrix U133A, MSKCC) does not have that
# problem against EITHER readable series.
#
# ⚠ THE CIRCULARITY IS ASSERTED FROM A FETCHED GEO RECORD, NOT FROM THE SAMPLE COUNTS. `collect()`
# reads the GSE4303 series record and stores its title, summary, contributors and linked PubMed id
# verbatim; `derive()` grades the match. If the record does not name Subramanian, the flag says
# UNCONFIRMED and the block is reported with that word rather than being quietly dropped.
# =============================================================================================
FILION_TABLE1 = [  # top 25 probe sets, all HIGHER in EMC. Two probe sets had no gene symbol.
    "DKK1", "CDH10", "NMB", "LCN1", "PDZRN4", "CORIN", "HTR4", "MAN1A1", "GULP1", "PDE3B",
    "GRIA3", "CHAD", "TYRP1", "MMP16", "HAPLN1", "BCAT1", "EDIL3", "OXR1", "P2RY14", "KCNJ16",
    "CCRL1",
]
FILION_TABLE1_UNMAPPED = ["KIAA1822L (now FAM155A)", "clone 24820 mRNA", "unidentified mRNA"]

FILION_TABLE2 = [  # overlap with Subramanian's top 50 — CIRCULAR against GPL3290
    "DKK1", "NMB", "MAN1A1", "CLCN3", "SOD3", "PHLDA1", "NDRG2", "LRP5", "CTNND2", "SNCA",
    "PPP1R3C", "VCAN", "RNF130", "GCLC", "FADS2", "PAM", "PGAM2", "CPD", "C10orf116", "PPARG",
]
FILION_TABLE2_RENAMES = {"CSPG2": "VCAN", "C10orf116": "ADIRF"}

BRENCA_EWSR1_HIGH = ["SEMA3C", "SEMA3G", "RELN"]
BRENCA_TAF15_HIGH = ["SEMA4D", "SEMA5A", "SEMA6A", "PLXNA1", "PLXNA4", "PLXNC1", "SLIT1", "ROBO1",
                     "CXCR4", "SYP"]

# =============================================================================================
# ⚠ SYMBOLS THAT HAVE BEEN RENAMED SINCE THESE ARRAYS WERE ANNOTATED.
#
# ⛔ WHY THIS IS NOT A LOOKUP TABLE AND MUST NOT BECOME ONE. Adding an alias to the WANTED list
# without a matching re-fetch is the "absent reading is not a reading of absence" failure in a new
# costume: `derive()` would emit a row for a symbol the inputs cache never requested, carrying the
# verdict "no probe on this platform maps to the symbol" — a FALSE reason, because the collector
# never looked. So this map is used for ONE thing only: when a gene comes back unreadable, its row
# says that a documented alias exists and that THIS RUN DID NOT ASK FOR IT. The next fetch can then
# request both spellings deliberately; until it does, the unreadability of the alias is UNKNOWN,
# and the row says the word UNKNOWN rather than implying absence.
#
# The renames are real and they land on genes this module actually asks about: `CCRL1` is 1 of the
# 21 mapped probe sets in Filion Table 1, and `PDP1` and `BIRC3` are class-B direct targets.
# =============================================================================================
SYMBOL_HISTORY = {
    "CCRL1": ["ACKR4", "CCX-CKR"],
    "PDP1": ["PPM2C"],
    "BIRC3": ["API2", "cIAP2", "MIHC"],
    "VCAN": ["CSPG2"],
    "ADIRF": ["C10orf116", "APM2"],
    "NOX1": ["NOH1", "MOX1", "GP91-2"],
    "PLAGL1": ["ZAC1", "LOT1"],
    "SMPX": ["CSRP4"],
    "CDKN2AIP": ["CARF"],
    "HAPLN1": ["CRTL1"],
    "TH": ["TYH"],
    "MYH7": ["CMH1", "MPD1"],
}

CONTROLS = {
    "the_fusion_itself": ["NR4A3"],
    "the_positive_control": ["ENO3"],
    "proliferation_reference": ["MKI67"],
    "fet_family_context": ["EWSR1", "TAF15", "FUS"],
}

# =============================================================================================
# THE PPARgamma ACTIVITY ARMS — pinned VERBATIM, because a set chosen alphabetically is a set
# chosen by accident.
#
# The uncalibrated scores for these sets have their ONE HOME in
# `research/modalities/emc-expression-panels.json` -> signature_scores (read 3). This module
# re-derives them ONLY so that the SAME sets can be put through the null calibration below, and
# `derive()` reports its own number beside that home as a cross-check rather than as a new fact.
# =============================================================================================
PPARG_ARMS = {
    "pparg_KO_DOWN": {
        "library": "TF_Perturbations_Followed_by_Expression",
        "term": "PPARG DEFICIENCY MOUSE GSE23421 CREEDSID GENE 1231 DOWN",
        "arm": "KO_DOWN",
        "meaning": "genes that FALL when PPARG is removed. High in EMC = an engaged receptor.",
    },
    "pparg_OE_UP": {
        "library": "TF_Perturbations_Followed_by_Expression",
        "term": "PPARG OE MOUSE GSE10192 CREEDSID GENE 2731 UP",
        "arm": "OE_UP",
        "meaning": "genes that RISE on over-expression. Independent construction, SAME expected "
                   "direction as KO_DOWN.",
    },
    "pparg_KO_UP_FALSIFIER": {
        "library": "TF_Perturbations_Followed_by_Expression",
        "term": "PPARG DEFICIENCY MOUSE GSE23421 CREEDSID GENE 1231 UP",
        "arm": "KO_UP",
        "meaning": "THE FALSIFIER. Must NOT track the other two. If all three move together the "
                   "contrast is measuring something the sets share.",
    },
    "pparg_chip_chea": {
        "library": "ChEA_2022",
        "term": "PPARG 19300518 ChIP-PET 3T3-L1 Mouse",
        "arm": "CHIP",
        "meaning": "occupancy-derived target set from a published ChIP-PET experiment.",
    },
    "pparg_curated_trrust_human": {
        "library": "TRRUST_Transcription_Factors_2019",
        "term": "PPARG human",
        "arm": "CURATED_HUMAN",
        "meaning": "the ONLY human-derived PPARG set of the five.",
    },
    "adipogenesis_process_proxy": {
        "library": "MSigDB_Hallmark_2020",
        "term": "Adipogenesis",
        "arm": "PROCESS_PROXY_NOT_A_TARGET_SET",
        "meaning": "the composition confound made explicit: a fat-differentiation programme, not a "
                   "PPARgamma target set.",
    },
}

ENRICHR_CITATIONS = {
    "TF_Perturbations_Followed_by_Expression":
        "TF perturbation followed by expression profiling, served via Enrichr (Kuleshov et al., "
        "Nucleic Acids Research 2016); each term names its own source GEO series.",
    "ChEA_2022":
        "ChEA - transcription-factor target sets from published ChIP-X experiments; each term "
        "carries its own source PMID (Lachmann et al., Bioinformatics 2010), via Enrichr.",
    "TRRUST_Transcription_Factors_2019":
        "TRRUST v2 - a manually curated transcriptional regulatory network mined from the "
        "literature (Han et al., Nucleic Acids Research 2018), via Enrichr.",
    "MSigDB_Hallmark_2020":
        "MSigDB Hallmark collection - Liberzon et al., Cell Systems 2015, via Enrichr.",
}

# ---------------------------------------------------------------------------------------------
# Floors and the null.
# ---------------------------------------------------------------------------------------------
MIN_GENES_FOR_A_SET_SCORE = 4
MIN_COVERAGE_FOR_A_SET_SCORE = 0.40
MIN_GROUP_N_FOR_A_CONTRAST = 3
NULL_DRAWS = 4000
NULL_POOL_SIZE = 4000
NULL_SEED = 20260807


def _species_of_term(term):
    """Species DERIVED FROM THE MATCHED TERM, never assumed. The Enrichr term strings for
    TF-perturbation and ChEA sets carry the organism in the name; TRRUST carries 'human'/'mouse'.
    A term that names no organism gets `unstated`, which is a reading of the term and NOT a claim
    that the experiment was human."""
    low = (term or "").lower()
    if re.search(r"\b(mouse|mus musculus|murine)\b", low):
        return "mouse"
    if re.search(r"\b(human|homo sapiens)\b", low):
        return "human"
    if re.search(r"\b(rat|rattus)\b", low):
        return "rat"
    return "unstated in the term"


# =============================================================================================
# FETCH
# =============================================================================================
def _wanted_genes():
    want = set()
    for row in LITERATURE_TARGETS:
        want.add(row["gene"])
    want.add(PUBLISHED_NEGATIVE["gene"])
    want.update(FILION_TABLE1)
    want.update(FILION_TABLE2)
    want.update(BRENCA_EWSR1_HIGH)
    want.update(BRENCA_TAF15_HIGH)
    for genes in CONTROLS.values():
        want.update(genes)
    want.update(FILION_TABLE2_RENAMES.keys())
    want.update(FILION_TABLE2_RENAMES.values())
    return want


def fetch_pparg_arms():
    """Fetch each PPARgamma arm by its VERBATIM pinned term. A term that does not resolve leaves
    the slot UNRESOLVED with the reason; it is NEVER replaced by a near miss, because a substituted
    'control' is not the control it names."""
    out = {"_what": "PPARgamma target-gene sets, each pinned to a verbatim Enrichr term.",
           "_one_home_of_the_uncalibrated_scores":
               "research/modalities/emc-expression-panels.json -> signature_scores (read 3). This "
               "module re-derives them only to put the SAME sets through the null calibration.",
           "slots": {}, "diagnostics": []}
    libs = {}
    for key, spec in PPARG_ARMS.items():
        lib = spec["library"]
        if lib not in libs:
            try:
                text = _get_once(ENRICHR_LIB.format(lib), timeout=240).decode("utf-8", "replace")
                terms = {}
                for line in text.splitlines():
                    parts = line.split("\t")
                    if len(parts) < 3:
                        continue
                    terms[parts[0].strip()] = sorted({
                        p.split(",")[0].strip().upper() for p in parts[2:] if p.strip()})
                libs[lib] = terms
                out["diagnostics"].append({"library": lib, "n_terms": len(terms), "status": "ok"})
            except Exception as exc:  # noqa: BLE001
                libs[lib] = None
                out["diagnostics"].append({"library": lib, "status": f"fetch failed: "
                                                                     f"{str(exc)[:160]}"})
        terms = libs.get(lib)
        rec = {"library": lib, "term_requested_verbatim": spec["term"], "arm": spec["arm"],
               "meaning": spec["meaning"], "citation": ENRICHR_CITATIONS.get(lib),
               "species_derived_from_the_matched_term": _species_of_term(spec["term"])}
        if terms is None:
            rec["resolved"] = False
            rec["why_not"] = ("⛔ LIBRARY NOT RETRIEVED — this slot scored nothing. An absent set "
                              "is an absent READING; it says nothing about the biology it names.")
        elif spec["term"] in terms:
            rec["resolved"] = True
            rec["matched_term_verbatim"] = spec["term"]
            rec["match_kind"] = "exact verbatim"
            rec["genes"] = terms[spec["term"]]
            rec["n_genes"] = len(rec["genes"])
        else:
            rec["resolved"] = False
            near = [t for t in terms if _norm(t) == _norm(spec["term"])]
            rec["why_not"] = ("⛔ TERM NOT PRESENT VERBATIM in this library snapshot. NOT "
                              "substituted with a near miss. An absent set is an absent reading.")
            rec["normalised_matches_seen"] = near[:5]
            rec["n_terms_in_library"] = len(terms)
        out["slots"][key] = rec
    out["n_slots_resolved"] = sum(1 for v in out["slots"].values() if v.get("resolved"))
    return out


def _series_record(gse):
    """The GEO series record, VERBATIM. This is what the circularity flag is graded from."""
    rec = {"gse": gse, "url": GEO_ACC.format(gse)}
    try:
        text = _get_once(rec["url"], timeout=180).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        rec["_status"] = f"fetch failed: {str(exc)[:180]}"
        return rec
    rec["_status"] = "read"
    keep = ("!Series_title", "!Series_summary", "!Series_overall_design", "!Series_pubmed_id",
            "!Series_contributor", "!Series_submission_date", "!Series_platform_id",
            "!Series_type", "!Series_sample_id")
    fields = {}
    for line in text.splitlines():
        for k in keep:
            if line.startswith(k):
                v = line.split("=", 1)[-1].strip()
                if k == "!Series_sample_id":
                    fields.setdefault(k, []).append(v)
                else:
                    fields.setdefault(k, []).append(v[:1500])
    rec["fields_verbatim"] = {k: (v if k != "!Series_sample_id" else
                                  {"n_samples": len(v), "first": v[:3]})
                              for k, v in fields.items()}
    return rec


def _read_target(target, want, null_pool_size, seed):
    """Fetch ONE named series-matrix file, map probes to symbols, and reduce to:
      (a) per-sample values for every WANTED gene, with its probe ids and array percentile;
      (b) the per-sample mean z over ALL mapped symbols — the EXACT global offset, computed over
          the whole universe rather than a sample of it;
      (c) a seeded random NULL POOL of `null_pool_size` mapped symbols with their per-sample
          values, so the size-matched empirical null can be redrawn OFFLINE and audited.

    ⭐ (b) AND (c) ARE THE POINT OF THIS MODULE. Without them, 'HIGHER in EMC' on a platform whose
    two arms differ globally is not a reading about the gene set."""
    gse, mf = target["gse"], target["matrix_file"]
    rec = {"gse": gse, "matrix_file": mf, "why": target["why"],
           "prior_probe_mapping_rate": target["prior_probe_mapping_rate"],
           "prior_source": target["prior_source"]}
    url = _geo_matrix_dir(gse) + mf
    rec["url"] = url
    try:
        raw = _get(url, timeout=900)
    except Exception as exc:  # noqa: BLE001
        rec["_status"] = f"fetch failed: {str(exc)[:200]}"
        return rec
    rec["compressed_bytes"] = len(raw)
    try:
        plat, samples, probes, values = _parse_series_matrix(raw)
    except Exception as exc:  # noqa: BLE001
        rec["_status"] = f"parse failed: {str(exc)[:200]}"
        return rec
    m = re.search(r"(GPL\d+)", mf)
    plat = m.group(1) if m else plat
    rec["platform"] = plat
    rec["platform_expected"] = target["platform_expected"]
    rec["platform_matches_expected"] = (plat == target["platform_expected"])
    sym, diag = _gpl_symbols(plat)
    rec["probe_symbol_mapping"] = diag
    n_s = len(samples)
    rec["n_samples"] = n_s
    rec["n_probes"] = len(probes)
    rec["n_probes_mapped_to_a_symbol"] = sum(1 for p in probes if sym.get(p))
    rec["measured_probe_mapping_rate"] = (round(rec["n_probes_mapped_to_a_symbol"] / len(probes), 4)
                                          if probes else None)
    rec["samples"] = samples

    flat = [v for row in values for v in row if v is not None]
    frac_neg = (sum(1 for v in flat if v < 0) / len(flat)) if flat else 0.0
    rec["frac_negative_values"] = round(frac_neg, 3)
    rec["value_kind"] = ("two-colour log-ratio vs a reference pool (RELATIVE - an absolute level "
                         "is NOT interpretable; only the between-group contrast is)"
                         if frac_neg > 0.15 else
                         "single-channel intensity (an absolute level is interpretable only "
                         "relative to this array's own probe distribution)")

    bg, dist = [], []
    for i in range(n_s):
        col = [row[i] for row in values if i < len(row) and row[i] is not None]
        if len(col) < 50:
            bg.append(None)
            dist.append(None)
            continue
        mu = sum(col) / len(col)
        var = max(1e-12, sum((x - mu) ** 2 for x in col) / len(col))
        bg.append({"mean": round(mu, 4), "sd": round(var ** 0.5, 4), "n": len(col)})
        dist.append(sorted(col))
    rec["background_per_sample"] = bg

    # ---- every mapped symbol, collapsed to one value per sample (mean over its probes) ----
    by_gene = {}
    for pid, row in zip(probes, values):
        g = sym.get(pid)
        if not g:
            continue
        by_gene.setdefault(g, {"probe_ids": [], "rows": []})
        by_gene[g]["probe_ids"].append(pid)
        by_gene[g]["rows"].append(row[:n_s])

    def _collapse(d):
        vals, pct = [], []
        for i in range(n_s):
            got = [r[i] for r in d["rows"] if i < len(r) and r[i] is not None]
            if not got:
                vals.append(None)
                pct.append(None)
                continue
            v = sum(got) / len(got)
            vals.append(round(v, 4))
            pct.append(round(bisect_left(dist[i], v) / len(dist[i]), 4) if dist[i] else None)
        return vals, pct

    rec["n_distinct_symbols_on_platform"] = len(by_gene)

    # (b) the EXACT global offset: per-sample mean z over ALL mapped symbols.
    tot = [0.0] * n_s
    cnt = [0] * n_s
    for g, d in by_gene.items():
        vals, _ = _collapse(d)
        for i in range(n_s):
            if vals[i] is None or not bg[i]:
                continue
            tot[i] += (vals[i] - bg[i]["mean"]) / max(1e-9, bg[i]["sd"])
            cnt[i] += 1
    rec["all_symbol_mean_z_per_sample"] = [round(tot[i] / cnt[i], 6) if cnt[i] else None
                                           for i in range(n_s)]
    rec["all_symbol_n_per_sample"] = cnt
    rec["_all_symbol_mean_z_means"] = (
        "the mean within-sample z over EVERY symbol this platform maps, for that sample. The EMC "
        "vs comparator contrast of THIS vector is the platform's global offset — the amount by "
        "which an arbitrary gene set is expected to differ between the arms for reasons that have "
        "nothing to do with the set.")

    # (c) the seeded null pool.
    rng = random.Random(seed)
    universe = sorted(by_gene)
    pool = sorted(rng.sample(universe, min(null_pool_size, len(universe))))
    rec["null_pool_spec"] = {"seed": seed, "requested": null_pool_size, "drawn": len(pool),
                             "universe": len(universe),
                             "_how": "random.Random(seed).sample over the sorted list of every "
                                     "symbol this platform maps. Sorted first, so the draw is "
                                     "reproducible from the seed alone."}
    genes, null_pool = {}, {}
    for g, d in by_gene.items():
        in_want, in_pool = g in want, g in set(pool)
        if not (in_want or in_pool):
            continue
        vals, pct = _collapse(d)
        if in_want:
            genes[g] = {"probe_ids": sorted(d["probe_ids"])[:12],
                        "n_probes_mapping": len(d["probe_ids"]),
                        "values": vals, "array_percentile": pct}
        if in_pool:
            null_pool[g] = vals
    rec["genes"] = genes
    rec["null_pool_values"] = null_pool
    rec["n_wanted_genes_measured"] = len(genes)
    rec["n_wanted_genes_requested"] = len(want)
    rec["_status"] = "read"
    print(f"  {gse}/{plat}: {n_s} samples, {len(probes)} probes, "
          f"{rec['n_probes_mapped_to_a_symbol']} mapped, {len(by_gene)} symbols; "
          f"{len(genes)}/{len(want)} wanted, null pool {len(null_pool)}", file=sys.stderr)
    return rec


def collect():
    print("fetching PPARgamma arms (verbatim terms)...", file=sys.stderr)
    arms = fetch_pparg_arms()
    want = _wanted_genes()
    for rec in arms["slots"].values():
        want.update(rec.get("genes") or [])
    print(f"  {arms['n_slots_resolved']}/{len(PPARG_ARMS)} arms resolved; "
          f"{len(want)} distinct genes wanted", file=sys.stderr)
    inp = {"_generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "pparg_arms": arms,
           "n_genes_wanted": len(want),
           "null_draws": NULL_DRAWS,
           "series_records": {t["gse"]: _series_record(t["gse"]) for t in TARGETS},
           "targets": {}}
    for t in TARGETS:
        print(f"reading {t['gse']} {t['matrix_file']}...", file=sys.stderr)
        inp["targets"][t["matrix_file"]] = _read_target(t, want, NULL_POOL_SIZE, NULL_SEED)
    return inp


# =============================================================================================
# DERIVE
# =============================================================================================
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _group_indices(samples):
    classes = [_classify_sample(s["annotation_verbatim"]) for s in samples]
    emc = [i for i, c in enumerate(classes) if c == "EMC"]
    comp = [i for i, c in enumerate(classes)
            if c not in ("EMC", "unclassified", "normal_or_reference")]
    return classes, emc, comp


def _z_from_values(tgt, vals):
    n_s = tgt["n_samples"]
    bg = tgt["background_per_sample"]
    return [None if (vals[i] is None or not bg[i]) else
            (vals[i] - bg[i]["mean"]) / max(1e-9, bg[i]["sd"]) for i in range(n_s)]


def _zrow(tgt, gene):
    return _z_from_values(tgt, tgt["genes"][gene]["values"])


def _global_offset(tgt, emc, comp):
    """The contrast of the ALL-SYMBOL mean-z vector. This is the number every set score has to
    beat before it means anything."""
    v = tgt.get("all_symbol_mean_z_per_sample") or []
    if not v:
        return {"measured": False,
                "why": "⛔ NOT MEASURED in this inputs cache — the all-symbol vector is absent, so "
                       "no set score below can be offset-corrected. An absent reading."}
    a = [v[i] for i in emc if i < len(v) and v[i] is not None]
    b = [v[i] for i in comp if i < len(v) and v[i] is not None]
    if len(a) < MIN_GROUP_N_FOR_A_CONTRAST or len(b) < MIN_GROUP_N_FOR_A_CONTRAST:
        return {"measured": False, "why": f"n_EMC={len(a)}, n_comparator={len(b)}"}
    w = _welch(a, b)
    return {
        "measured": True, "welch": w,
        "n_symbols_per_sample": tgt.get("all_symbol_n_per_sample"),
        "reading": (f"Across EVERY symbol this platform maps, the EMC arm sits "
                    f"{abs(w['delta_a_minus_b'])} SD units "
                    f"{'ABOVE' if w['delta_a_minus_b'] > 0 else 'BELOW'} the comparator arm "
                    f"(t={w['t']}). ⚠ Any gene set on this platform is expected to show about "
                    f"this much difference FOR NO SET-SPECIFIC REASON."),
    }


def _null_scores(tgt, size, emc, comp, draws, seed):
    """`draws` random gene sets of exactly `size` drawn from the platform's own null pool, each
    scored the same way a real set is. Returns the empirical distribution of the EMC-comparator
    delta."""
    pool = tgt.get("null_pool_values") or {}
    keys = sorted(pool)
    if len(keys) < max(size, MIN_GENES_FOR_A_SET_SCORE) or size < 1:
        return None
    n_s = tgt["n_samples"]
    zc = {g: _z_from_values(tgt, pool[g]) for g in keys}
    rng = random.Random(seed * 1000003 + size)
    deltas = []
    for _ in range(draws):
        pick = rng.sample(keys, size)
        rows = [zc[g] for g in pick]
        per = [_mean([r[i] for r in rows]) for i in range(n_s)]
        a = [per[i] for i in emc if per[i] is not None]
        b = [per[i] for i in comp if per[i] is not None]
        if len(a) < MIN_GROUP_N_FOR_A_CONTRAST or len(b) < MIN_GROUP_N_FOR_A_CONTRAST:
            continue
        deltas.append(_mean(a) - _mean(b))
    if len(deltas) < draws // 2:
        return None
    deltas.sort()
    n = len(deltas)

    def q(p):
        return deltas[min(n - 1, max(0, int(round(p * (n - 1)))))]

    mu = sum(deltas) / n
    sd = (sum((d - mu) ** 2 for d in deltas) / max(1, n - 1)) ** 0.5
    return {"n_draws": n, "set_size": size, "pool_size": len(keys),
            "mean": round(mu, 5), "sd": round(sd, 5),
            "q025": round(q(0.025), 5), "q50": round(q(0.50), 5), "q975": round(q(0.975), 5),
            "_sorted": deltas}


def _empirical_p(sorted_deltas, observed):
    """Two-sided empirical p from a sorted null, +1/+1 smoothed so it can never be 0 — a p of 0
    from 4000 draws would be a claim the draws cannot support."""
    n = len(sorted_deltas)
    n_ge = n - bisect_left(sorted_deltas, observed)   # draws >= observed
    n_le = bisect_right(sorted_deltas, observed)      # draws <= observed
    p_right = (n_ge + 1) / (n + 1)
    p_left = (n_le + 1) / (n + 1)
    return round(p_right, 5), round(p_left, 5), round(min(1.0, 2 * min(p_right, p_left)), 5)


def _score_set(genes, tgt, emc, comp, what, null_cache, draws=NULL_DRAWS, seed=NULL_SEED):
    """Mean within-sample z over the READABLE members, EMC vs comparator, THEN calibrated against
    a size-matched empirical null from the same platform.

    ⛔ COVERAGE IS REPORTED WHETHER OR NOT A SCORE IS EMITTED, and a list below the floor emits
    UNDERPOWERED rather than a number."""
    genes = sorted(set(genes))
    have = tgt.get("genes") or {}
    readable = [g for g in genes if g in have]
    cov = round(len(readable) / len(genes), 3) if genes else None
    base = {"n_genes_requested": len(genes), "n_genes_readable": len(readable), "coverage": cov,
            "genes_readable": sorted(readable)[:300],
            "genes_not_readable": sorted(set(genes) - set(readable))[:300],
            "_not_readable_means": "no probe on this platform maps to the symbol. It is NOT a "
                                   "statement that the gene is unexpressed."}
    if len(readable) < MIN_GENES_FOR_A_SET_SCORE or (cov or 0) < MIN_COVERAGE_FOR_A_SET_SCORE:
        base["score"] = None
        base["verdict"] = (f"⛔ UNDERPOWERED — {len(readable)}/{len(genes)} genes readable on "
                           f"{tgt.get('platform')} (coverage {cov}); the floor for {what} is "
                           f"{MIN_GENES_FOR_A_SET_SCORE} genes and {MIN_COVERAGE_FOR_A_SET_SCORE} "
                           f"coverage. NO SCORE EMITTED. This is an instrument limit, not a "
                           f"reading of the biology.")
        return base
    rows = [_zrow(tgt, g) for g in readable]
    n_s = tgt["n_samples"]
    per_sample = [_mean([r[i] for r in rows]) for i in range(n_s)]
    a = [per_sample[i] for i in emc if per_sample[i] is not None]
    b = [per_sample[i] for i in comp if per_sample[i] is not None]
    base["EMC_mean_score"] = round(_mean(a), 4) if a else None
    base["comparator_mean_score"] = round(_mean(b), 4) if b else None
    if len(a) < MIN_GROUP_N_FOR_A_CONTRAST or len(b) < MIN_GROUP_N_FOR_A_CONTRAST:
        base["score"] = None
        base["verdict"] = (f"⛔ UNDERPOWERED — n_EMC={len(a)}, n_comparator={len(b)}; the floor is "
                           f"{MIN_GROUP_N_FOR_A_CONTRAST} per group.")
        return base
    w = _welch(a, b)
    base["score"] = w
    base["raw_verdict"] = (f"{'HIGHER' if w['delta_a_minus_b'] > 0 else 'LOWER'} in EMC by "
                           f"{abs(w['delta_a_minus_b'])} SD units (t={w['t']}, df={w['df']}, "
                           f"n_EMC={len(a)}, n_comparator={len(b)}, {len(readable)}/{len(genes)} "
                           f"genes readable). ⚠ RAW — read the null calibration below before "
                           f"quoting this. Uncorrected for multiple testing.")
    size = len(readable)
    key = (tgt.get("matrix_file"), size)
    if key not in null_cache:
        null_cache[key] = _null_scores(tgt, size, emc, comp, draws, seed)
    null = null_cache[key]
    if not null:
        base["null_calibration"] = {
            "computed": False,
            "why": "⛔ NULL NOT COMPUTED — the platform's null pool is absent or smaller than the "
                   "set. Without it this row is a raw contrast on a platform with a global "
                   "offset, and must not be read as set-specific.",
        }
        base["verdict"] = base["raw_verdict"] + " ⛔ NO NULL — NOT INTERPRETABLE as set-specific."
        return base
    d = w["delta_a_minus_b"]
    p_right, p_left, p_two = _empirical_p(null["_sorted"], d)
    z_vs_null = (d - null["mean"]) / null["sd"] if null["sd"] > 0 else None
    beats = d > null["q975"]
    below = d < null["q025"]
    base["null_calibration"] = {
        "computed": True,
        "n_draws": null["n_draws"], "set_size": null["set_size"], "pool_size": null["pool_size"],
        "null_mean_delta": null["mean"], "null_sd": null["sd"],
        "null_q025": null["q025"], "null_q50": null["q50"], "null_q975": null["q975"],
        "observed_delta": d,
        "z_vs_null": round(z_vs_null, 3) if z_vs_null is not None else None,
        "p_empirical_two_sided": p_two,
        "p_empirical_right_tail": p_right,
        "p_empirical_left_tail": p_left,
        "_how": (f"{null['n_draws']} random gene sets of exactly {null['set_size']} symbols drawn "
                 f"from this platform's own seeded null pool ({null['pool_size']} symbols), each "
                 f"scored EXACTLY as the real set is. The p-value is the fraction of draws at "
                 f"least as extreme, +1/+1 smoothed. It absorbs the global offset by construction: "
                 f"a random set carries the offset too."),
        "verdict": ("SET-SPECIFIC — outside the 95% band of size-matched random sets on this "
                    "platform, in the UP direction" if beats else
                    "SET-SPECIFIC — outside the 95% band, in the DOWN direction" if below else
                    "⛔ NOT DISTINGUISHABLE FROM A RANDOM GENE SET of the same size on this "
                    "platform. The raw contrast above is what an arbitrary set of this size does "
                    "here; it is NOT evidence about this set."),
    }
    base["verdict"] = base["raw_verdict"] + " || NULL: " + base["null_calibration"]["verdict"]
    return base


def _gene_read(gene, tgt, classes, emc, comp, null_cache):
    plat = tgt.get("platform")
    g = (tgt.get("genes") or {}).get(gene)
    if not g:
        out = {
            "readable": False, "platform": plat, "n_probes_mapping": 0,
            "why_not_readable": (
                f"No probe on {plat} maps to the symbol {gene}. The platform's probe->symbol "
                f"mapping covers {tgt.get('n_probes_mapped_to_a_symbol')} of {tgt.get('n_probes')} "
                f"probes, so a symbol can be missing because the array carries no probe for it OR "
                f"because that probe's identifier did not resolve."),
            "verdict": (f"⛔ NOT READABLE on {plat} — the read could not be taken. This says "
                        f"NOTHING about whether {gene} is expressed in EMC."),
        }
        alias = SYMBOL_HISTORY.get(gene)
        if alias:
            out["documented_aliases"] = alias
            out["alias_status"] = "UNKNOWN"
            out["_alias_note"] = (
                f"⚠ {gene} has documented former symbol(s) {alias}. These arrays predate the "
                f"rename, so the platform may annotate the probe under an old spelling. "
                f"THIS RUN DID NOT REQUEST THE ALIAS, so whether it is present is UNKNOWN — not "
                f"absent. A future fetch should request both spellings deliberately; adding one "
                f"to the wanted list without a re-fetch would produce a row asserting a reason "
                f"the collector never checked.")
            out["verdict"] += (f" ⚠ ALIAS UNCHECKED: former symbol(s) {'/'.join(alias)} were not "
                               f"requested in this run.")
        return out
    n_s = tgt["n_samples"]
    z = [None if x is None else round(x, 4) for x in _zrow(tgt, gene)]
    vals, pct = g["values"], g["array_percentile"]
    samples = tgt["samples"]
    a = [z[i] for i in emc if z[i] is not None]
    b = [z[i] for i in comp if z[i] is not None]
    emc_pct = [pct[i] for i in emc if pct[i] is not None]
    out = {
        "readable": True, "platform": plat,
        "n_probes_mapping": g["n_probes_mapping"], "probe_ids": g["probe_ids"],
        "value_kind": tgt["value_kind"],
        "n_EMC_with_a_value": len(a), "n_comparator_with_a_value": len(b),
        "EMC": {"mean_z": round(_mean(a), 4) if a else None,
                "mean_array_percentile": round(_mean(emc_pct), 4) if emc_pct else None},
        "comparator": {"mean_z": round(_mean(b), 4) if b else None},
        "per_sample": [{"gsm": samples[i]["gsm"], "class": classes[i], "value": vals[i],
                        "z_vs_array": z[i], "array_percentile": pct[i]}
                       for i in range(n_s) if i in emc or i in comp],
    }
    if len(a) >= MIN_GROUP_N_FOR_A_CONTRAST and len(b) >= MIN_GROUP_N_FOR_A_CONTRAST:
        w = _welch(a, b)
        out["welch_EMC_vs_comparator"] = w
        out["_sign"] = "delta_a_minus_b > 0 means HIGHER in EMC than in the comparator sarcomas."
        # A single gene is calibrated against the SIZE-1 null: how far out is one gene, given how
        # much the whole platform's genes move between these two arms?
        key = (tgt.get("matrix_file"), 1)
        if key not in null_cache:
            null_cache[key] = _null_scores(tgt, 1, emc, comp, NULL_DRAWS, NULL_SEED)
        null = null_cache[key]
        if null:
            _pr, _pl, _p2 = _empirical_p(null["_sorted"], w["delta_a_minus_b"])
            out["null_calibration"] = {
                "computed": True, "n_draws": len(null["_sorted"]),
                "null_mean_delta": null["mean"], "null_sd": null["sd"],
                "null_q025": null["q025"], "null_q975": null["q975"],
                "p_empirical_two_sided": _p2,
                "_how": "the same empirical null at set size 1 — i.e. the distribution of the "
                        "EMC-comparator delta for a SINGLE randomly chosen gene on this platform.",
            }
        else:
            out["null_calibration"] = {"computed": False,
                                       "why": "⛔ null pool absent from the inputs cache."}
    else:
        out["welch_EMC_vs_comparator"] = None
        out["_underpowered"] = (f"n_EMC={len(a)}, n_comparator={len(b)}; the floor is "
                                f"{MIN_GROUP_N_FOR_A_CONTRAST} per group.")
    out["verdict"] = _gene_verdict(out)
    return out


def _gene_verdict(r):
    w = r.get("welch_EMC_vs_comparator")
    pctile = (r["EMC"] or {}).get("mean_array_percentile")
    present = (f"EMC samples sit at the {round(pctile * 100)}th percentile of this array's probe "
               f"distribution" if pctile is not None else "array percentile not computable")
    if not w:
        return (f"READABLE on {r['platform']} ({r['n_probes_mapping']} probe(s)); {present}. "
                f"No group contrast — {r.get('_underpowered')}")
    d, t = w["delta_a_minus_b"], w["t"]
    nc = r.get("null_calibration") or {}
    tail = ""
    if nc.get("computed"):
        band = f"[{nc['null_q025']}, {nc['null_q975']}]"
        tail = (f" || NULL(size 1): 95% band of a random single gene here is {band}; "
                f"p_emp={nc['p_empirical_two_sided']}"
                f"{'  — OUTSIDE the band' if (d > nc['null_q975'] or d < nc['null_q025']) else ''}")
    return (f"READABLE on {r['platform']} ({r['n_probes_mapping']} probe(s)); {present}. "
            f"{'HIGHER' if d > 0 else 'LOWER'} in EMC by {abs(d)} SD units of the array "
            f"(t={t}, df={w['df']}, n_EMC={r['n_EMC_with_a_value']}, "
            f"n_comparator={r['n_comparator_with_a_value']}). ⚠ Uncorrected for multiple "
            f"testing.{tail}")


def _mapping_rate_reading(tgt):
    diag = tgt.get("probe_symbol_mapping") or {}
    acc = diag.get("accession_resolution_rate")
    out = {"probe_level_rate": tgt.get("measured_probe_mapping_rate"),
           "accession_resolution_rate": acc,
           "prior_accession_resolution_rate": tgt["prior_probe_mapping_rate"],
           "prior_source": tgt["prior_source"],
           "_the_two_rates_measure_different_things": (
               "probe_level_rate = fraction of probes ON THIS MATRIX carrying a symbol; "
               "accession_resolution_rate = fraction of the platform's distinct GenBank ACCESSIONS "
               "that resolved. Only the second is comparable to the prior, which is what that "
               "field records. Comparing the first against the prior manufactures a drift warning "
               "(measured 2026-08-07, run 31182233077).")}
    if acc is None:
        out["reading"] = ("⚠ NO ACCESSION-RESOLUTION RATE IN THIS RUN, so the like-for-like "
                          "comparison against the prior COULD NOT BE MADE. An absent reading, not "
                          "agreement.")
        return out
    delta = acc - tgt["prior_probe_mapping_rate"]
    out["abs_difference_vs_prior"] = round(abs(delta), 4)
    out["reading"] = ("consistent with the prior characterisation" if abs(delta) <= 0.05 else
                      f"⚠ MOVED {'UP' if delta > 0 else 'DOWN'} by {abs(round(delta, 3))} against "
                      f"the prior, compared LIKE FOR LIKE. A wider or narrower accession bridge "
                      f"changes WHICH genes are readable — read this before any number below it.")
    return out


def _circularity_reading(inp):
    """⛔ IS GSE4303 THE SUBRAMANIAN 2005 COHORT? Graded from the FETCHED series record, never from
    sample counts. Filion Table 2 is the overlap between Filion's own EMC profile and Subramanian's
    top 50; if GSE4303 is Subramanian's data then scoring Table 2 on GPL3290 is scoring a gene list
    on the data it came from."""
    rec = (inp.get("series_records") or {}).get("GSE4303") or {}
    f = rec.get("fields_verbatim") or {}
    if rec.get("_status") != "read" or not f:
        return {"graded": False,
                "verdict": "⛔ SERIES RECORD NOT READ — the circularity question is UNANSWERED, "
                           "not answered negatively. Every Filion-Table-2 score on GPL3290 below "
                           "must be read as POSSIBLY CIRCULAR.",
                "record_status": rec.get("_status")}
    blob = " ".join(v if isinstance(v, str) else " ".join(map(str, v))
                    for k, v in f.items() if k != "!Series_sample_id"
                    for v in (f[k] if isinstance(f[k], list) else [f[k]])).lower()
    hits = {k: (k.lower() in blob) for k in
            ("Subramanian", "myxoid chondrosarcoma", "West", "Rubin", "van de Rijn")}
    pmids = f.get("!Series_pubmed_id") or []
    out = {"graded": True,
           "series_title_verbatim": (f.get("!Series_title") or [None])[0],
           "series_pubmed_id_verbatim": pmids,
           "series_contributor_verbatim": f.get("!Series_contributor"),
           "name_hits_in_the_record": hits,
           "subramanian_2005_pmid": "15920699",
           "_what_would_confirm": "the series record naming PMID 15920699, or naming Subramanian "
                                  "among the contributors."}
    confirmed = ("15920699" in [str(p) for p in pmids]) or hits.get("Subramanian")
    out["confirmed_same_cohort"] = bool(confirmed)
    out["verdict"] = (
        "⛔ CONFIRMED CIRCULAR: GSE4303 is the Subramanian et al. 2005 cohort, so Filion Table 2 "
        "(the overlap with Subramanian's top 50) is a gene list DERIVED FROM THIS DATA. Its score "
        "on GPL3290 is not a test and is reported for completeness only. Filion Table 1 and "
        "GSE24369 are unaffected."
        if confirmed else
        "⚠ NOT CONFIRMED from the record. The cohort description matches (10 EMC, cDNA platform, "
        "same era) but the record does not name the study, so the circularity is POSSIBLE and "
        "UNRESOLVED — treat Filion Table 2 on GPL3290 as suspect rather than clean.")
    return out


def derive(inp):
    res = {
        "_what": "What EWSR1::NR4A3 is published to transcribe, scored in EMC tumour tissue "
                 "against a size-matched empirical null on the same platform.",
        "_framing": FRAMING,
        "_the_rule_that_governs_every_row": (
            "⛔ AN ABSENT READING IS NOT A READING OF ABSENCE. A gene with no probe is "
            "`readable: false` and its verdict says the READ could not be taken — never that the "
            "gene is unexpressed. And a POPULATED FIELD IS NOT A MEASURED ONE: every readable gene "
            "carries `n_probes_mapping`, its real probe ids and an `array_percentile` that can "
            "only come from the full parsed distribution of that sample's probes."),
        "_the_second_rule": (
            "⛔ A RAW 'HIGHER IN EMC' IS NOT A RESULT. Read `global_offset` for the platform first, "
            "then the `null_calibration` on the row. A set that does not clear its size-matched "
            "null has told you what an arbitrary gene set does on that platform, nothing more."),
        "_language_discipline": (
            "No efficacy, selectivity, safety, therapeutic-window or clinical-readiness claim is "
            "made or implied for any agent, target or gene named here."),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "evidence_table": {
            "_what": "Every published claim that EWSR1::NR4A3, another NR4A3 fusion, or native "
                     "NR4A3 transcriptionally activates a named gene — with the assay, the cell "
                     "system, the species, the citation and the verbatim sentence the "
                     "classification rests on.",
            "_evidence_classes": {
                FUSION_DNA_BINDING: "a DNA-binding or promoter assay performed WITH AN NR4A3 "
                                    "FUSION. The strongest class.",
                NATIVE_DNA_BINDING: "the same assay class with NATIVE NR4A3. Transfer to the "
                                    "fusion is an assumption — see the PPARG and SEMA3C rows, "
                                    "where it is measured and fails in both directions.",
                FUSION_EXPRESSION: "the gene moves when the fusion is expressed; no binding assay.",
                EMC_TISSUE_EXPRESSION: "measured in EMC tissue; no mechanism.",
            },
            "rows": LITERATURE_TARGETS,
            "published_negative_control": PUBLISHED_NEGATIVE,
            "n_rows": len(LITERATURE_TARGETS),
            "counts_by_class": {c: sum(1 for r in LITERATURE_TARGETS
                                       if r["evidence_class"] == c)
                                for c in (FUSION_DNA_BINDING, NATIVE_DNA_BINDING,
                                          FUSION_EXPRESSION, EMC_TISSUE_EXPRESSION)},
            "provenance": "Read from the committed Europe PMC corpora on the `literature-cache` "
                          "branch: literature/extraskeletal-myxoid-chondrosarcoma (694 files), "
                          "literature/nr4a3-cistrome-tight (462), literature/nr4a3-fusion-partners, "
                          "literature/pparg-direction-emc-2026-08-06 (766). No claim here is from "
                          "memory; every row carries the sentence it was read from.",
        },
        "pparg_arms": inp.get("pparg_arms"),
        "series_records": inp.get("series_records"),
        "platforms": {},
        "gene_reads": {},
        "set_scores": {},
        "controls": {},
    }
    circ = _circularity_reading(inp)
    res["circularity_reading"] = circ

    sets = _build_sets(res, circ)
    res["set_definitions"] = {k: {kk: vv for kk, vv in v.items() if kk != "genes"}
                              | {"n_genes": len(v["genes"]), "genes": sorted(v["genes"])}
                              for k, v in sets.items()}

    # ⚠ PER-GENE READS ARE SCOPED TO THE NAMED GENES, NOT TO EVERY SET MEMBER. The PPARgamma arms
    # carry ~900 genes between them and their per-sample rows would swamp the artifact for no
    # gain — those sets are read as SETS. Every gene that is named in the evidence table, in a
    # control, in a published EMC profile or in a Brenca axon-guidance list gets its own row.
    every_gene = sorted(_wanted_genes())
    null_cache = {}
    for mf, tgt in (inp.get("targets") or {}).items():
        if tgt.get("_status") != "read":
            res["platforms"][mf] = {"_status": tgt.get("_status"), "gse": tgt.get("gse"),
                                    "_means": "⛔ THIS PLATFORM WAS NOT READ. Nothing below is a "
                                              "reading of absence on it."}
            continue
        classes, emc, comp = _group_indices(tgt["samples"])
        res["platforms"][mf] = {
            "_status": "read", "gse": tgt["gse"], "platform": tgt["platform"],
            "platform_matches_expected": tgt["platform_matches_expected"],
            "why_this_platform": tgt["why"],
            "n_samples": tgt["n_samples"], "n_probes": tgt["n_probes"],
            "n_probes_mapped_to_a_symbol": tgt["n_probes_mapped_to_a_symbol"],
            "n_distinct_symbols_on_platform": tgt.get("n_distinct_symbols_on_platform"),
            "value_kind": tgt["value_kind"],
            "n_EMC": len(emc), "n_comparator": len(comp),
            "class_counts": {c: classes.count(c) for c in sorted(set(classes))},
            "n_wanted_genes_measured": tgt["n_wanted_genes_measured"],
            "probe_mapping": _mapping_rate_reading(tgt),
            "null_pool_spec": tgt.get("null_pool_spec"),
            "global_offset": _global_offset(tgt, emc, comp),
        }
        for g in every_gene:
            res["gene_reads"].setdefault(g, {})[mf] = _gene_read(g, tgt, classes, emc, comp,
                                                                 null_cache)
        for name, spec in sets.items():
            res["set_scores"].setdefault(name, {})[mf] = _score_set(
                spec["genes"], tgt, emc, comp, name, null_cache)

    res["controls"] = _controls(res)
    res["reads"] = _assemble_reads(res, sets)
    res["_what_this_cannot_conclude"] = _cannot_conclude()
    res["_limits"] = _limits()
    return res


def _build_sets(res, circ):
    fus = [r["gene"] for r in LITERATURE_TARGETS if r["evidence_class"] == FUSION_DNA_BINDING]
    nat = [r["gene"] for r in LITERATURE_TARGETS if r["evidence_class"] == NATIVE_DNA_BINDING]
    fus_expr = [r["gene"] for r in LITERATURE_TARGETS if r["evidence_class"] == FUSION_EXPRESSION]
    t2 = [FILION_TABLE2_RENAMES.get(g, g) for g in FILION_TABLE2]
    sets = {
        "A_fusion_dna_binding_targets": {
            "what": "Genes with a DNA-binding or promoter assay performed WITH AN NR4A3 FUSION.",
            "genes": set(fus),
            "expected": "UP in EMC if the fusion's published output is reproduced in tissue.",
            "caveat": "n=3. Two of the three fusions assayed are not EWSR1::NR4A3 (TFG::NR4A3 for "
                      "ENO3), and one of the three assays is in rat cells (PPARG).",
        },
        "B_native_nr4a3_dna_binding_targets": {
            "what": "Genes with the same assay class but NATIVE NR4A3.",
            "genes": set(nat),
            "expected": "UP only if the transfer assumption holds — which is measured to fail for "
                        "PPARG (native does not activate it) and for TAF15::NR4A3 on SEMA3C.",
            "caveat": "Mostly vascular, cardiac and metabolic tissue contexts that EMC tumour "
                      "tissue does not obviously reproduce.",
        },
        "A_plus_B_all_dna_binding": {
            "what": "Classes A and B pooled — the widest defensible 'direct target' set.",
            "genes": set(fus) | set(nat),
            "expected": "UP.",
            "caveat": "Pools a fusion assay with a native one. Reported because it is the set a "
                      "reader will construct anyway; the per-class scores above are the honest "
                      "ones.",
        },
        "C_fusion_expression_only": {
            "what": "Moves when the fusion is expressed; no binding assay. MIXED DIRECTION — "
                    "SGK1 is predicted flat/down at transcript level and PLAGL1 DOWN, so this set "
                    "must NOT be scored as a coherent up-programme and is here for its members.",
            "genes": set(fus_expr),
            "expected": "NO AGGREGATE EXPECTATION — read the members individually.",
            "caveat": "Scored only so the aggregate can be shown to be meaningless; the member "
                      "reads are the deliverable.",
        },
        "D_filion_table1_emc_vs_137_sarcomas": {
            "what": "The top 25 probe sets over-expressed in EMC vs 137 other translocation "
                    "sarcomas (Affymetrix U133A, MSKCC) — Filion et al. 2009 Table 1.",
            "genes": set(FILION_TABLE1),
            "expected": "UP on BOTH platforms if the published EMC profile replicates. This is an "
                        "INDEPENDENT replication set: it comes from neither readable series.",
            "caveat": "It is an EMC-vs-sarcoma profile, NOT a fusion target list — a gene can be "
                      "in it because of EMC's cell of origin. Two of the 25 probe sets had no "
                      "gene symbol and are absent: " + "; ".join(FILION_TABLE1_UNMAPPED),
            "citation": "Filion C, et al. J Pathol 2009;217(1):83-93. PMID 18855877, "
                        "PMCID PMC4429309, Table 1.",
        },
        "E_filion_table2_overlap_with_subramanian": {
            "what": "The 20 genes Filion's EMC profile shares with the top 50 of Subramanian et "
                    "al. 2005 — Filion et al. 2009 Table 2.",
            "genes": set(t2),
            "expected": "UP.",
            "caveat": "⛔ CIRCULAR ON GPL3290 — " + circ.get("verdict", "circularity ungraded"),
            "citation": "Filion C, et al. J Pathol 2009 Table 2; Subramanian S, et al. J Pathol "
                        "2005;206:433-444, PMID 15920699.",
        },
        "F_brenca_EWSR1_high_axon_guidance": {
            "what": "Axon-guidance genes reported HIGHER in EWSR1-translocated than in "
                    "TAF15-translocated EMC.",
            "genes": set(BRENCA_EWSR1_HIGH),
            "expected": "UP vs non-EMC comparators, DILUTED by whatever TAF15 fraction the EMC "
                        "arms contain — which neither series records.",
            "caveat": "The published contrast is WITHIN EMC. Scoring it against non-EMC "
                      "comparators is a different question and is labelled as one.",
            "citation": "Brenca M, et al. J Pathol 2019;249(1):90-101. PMID 31020999, "
                        "PMCID PMC6766969.",
        },
        "G_brenca_TAF15_high_axon_guidance": {
            "what": "Axon-guidance genes reported HIGHER in TAF15- than in EWSR1-translocated EMC.",
            "genes": set(BRENCA_TAF15_HIGH),
            "expected": "NO CLEAN EXPECTATION. Its value is as the COUNTERPART of set F: if F and "
                        "G both come back equally up, the reading is 'EMC is neural-ish', not "
                        "'the EWSR1 fusion drives class-3 semaphorins'.",
            "caveat": "As set F.",
            "citation": "Brenca M, et al. J Pathol 2019. PMCID PMC6766969.",
        },
    }
    for arm, spec in PPARG_ARMS.items():
        rec = ((res.get("pparg_arms") or {}).get("slots") or {}).get(arm) or {}
        if rec.get("resolved"):
            sets["PPARG_" + arm] = {
                "what": f"PPARgamma activity arm — {spec['meaning']}",
                "genes": set(rec["genes"]),
                "expected": "see `meaning`",
                "caveat": f"species derived from the matched term: "
                          f"{rec.get('species_derived_from_the_matched_term')}",
                "citation": rec.get("citation"),
                "matched_term_verbatim": rec.get("matched_term_verbatim"),
            }
    return sets


def _controls(res):
    """⭐ THE INSTRUMENT IS GRADED BEFORE THE BIOLOGY IS READ. Four checks, and three of them can
    FAIL — which is the point. A panel of set scores is worth nothing until the known answers come
    back."""
    out = {"_why": "A set of scores is worth nothing until the instrument has produced known "
                   "answers on these exact platforms. Read these before anything else.",
           "checks": {}}
    gr = res.get("gene_reads") or {}

    def _delta(gene, mf):
        r = (gr.get(gene) or {}).get(mf) or {}
        w = r.get("welch_EMC_vs_comparator")
        return (w or {}).get("delta_a_minus_b"), (w or {}).get("t"), r.get("readable")

    plats = [mf for mf, p in (res.get("platforms") or {}).items() if p.get("_status") == "read"]

    eno3 = {mf: _delta("ENO3", mf) for mf in plats}
    out["checks"]["positive_control_ENO3"] = {
        "expect": "UP on both platforms. The committed prior is +0.808 SD (t=+3.61) on GPL6244 and "
                  "+3.811 SD (t=+13.22) on GPL3290 — one home: "
                  "research/modalities/emc-expression-panels.json -> gene_reads.ENO3.",
        "measured": {mf: {"delta": v[0], "t": v[1], "readable": v[2]} for mf, v in eno3.items()},
        "pass": all(v[0] is not None and v[0] > 0 for v in eno3.values()),
        "_if_it_fails": "⛔ STOP AND REPORT THE INSTRUMENT, NOT THE BIOLOGY. Every number in this "
                        "file is produced by the same reduction.",
    }
    nr4a3 = {mf: _delta("NR4A3", mf) for mf in plats}
    out["checks"]["the_fusion_itself_NR4A3"] = {
        "expect": "UP in EMC — the chimera places NR4A3 coding sequence under the partner's "
                  "promoter, and NR4A3 immunostaining is the diagnostic marker of EMC.",
        "measured": {mf: {"delta": v[0], "t": v[1], "readable": v[2]} for mf, v in nr4a3.items()},
        "pass": all(v[0] is not None and v[0] > 0 for v in nr4a3.values()),
    }
    plagl1 = {mf: _delta("PLAGL1", mf) for mf in plats}
    out["checks"]["directional_falsifier_PLAGL1"] = {
        "expect": "★★ DOWN. Published as down-regulated by EWS/NOR1 and strongly down in six EMC "
                  "tumours (PMID 16112421). Every other literature row predicts UP, so a global "
                  "offset or a 'EMC differs from dense sarcomas' artefact would push PLAGL1 UP "
                  "with everything else. A DOWN reading is the one observation here that such an "
                  "artefact cannot manufacture.",
        "measured": {mf: {"delta": v[0], "t": v[1], "readable": v[2]} for mf, v in plagl1.items()},
        "pass": all(v[0] is not None and v[0] < 0 for v in plagl1.values()
                    if v[0] is not None) and any(v[0] is not None for v in plagl1.values()),
        "_if_it_fails": "⚠ NOT automatically an instrument failure — PLAGL1 is imprinted and its "
                        "published EMC read is n=6 by RT-PCR against chondrocyte controls, not "
                        "against sarcomas. But a PLAGL1 that reads UP removes the strongest "
                        "argument that the UP rows are not an offset, and must be reported.",
    }
    sgk1 = {mf: _delta("SGK1", mf) for mf in plats}
    out["checks"]["prereg_discordance_SGK1"] = {
        "expect": "★ FLAT OR DOWN at transcript level, despite the protein being over-expressed in "
                  "10/10 EMC by IHC. Filion et al. 2009 state their microarray shows LOWER SGK1 "
                  "mRNA in EMC than in other sarcomas, 'also consistent with the data of "
                  "Subramanian and colleagues', and attribute the protein excess to an isoform "
                  "lacking the proteasomal degradation signal.",
        "measured": {mf: {"delta": v[0], "t": v[1], "readable": v[2]} for mf, v in sgk1.items()},
        "pass": all(v[0] is not None and v[0] < 0.3 for v in sgk1.values() if v[0] is not None),
        "_why_it_is_a_control": "It is the only row in the table whose published transcript "
                                "direction OPPOSES its published protein direction, so it "
                                "discriminates a transcript instrument that is working from one "
                                "that is simply reporting 'EMC is different'.",
    }
    out["all_checks_pass"] = all(bool(c.get("pass")) for c in out["checks"].values())
    out["_reading"] = ("Every known answer came back as published."
                       if out["all_checks_pass"] else
                       "⚠ AT LEAST ONE KNOWN ANSWER DID NOT COME BACK AS PUBLISHED. Read the "
                       "failing check before any set score; a failing ENO3 invalidates the "
                       "instrument, a failing PLAGL1 weakens every UP row, and a failing SGK1 "
                       "suggests the contrast is reading tissue composition.")
    return out


def _assemble_reads(res, sets):
    """The four questions this module was built to answer, each with its verdict assembled from
    the rows above rather than typed."""
    plats = [mf for mf, p in (res.get("platforms") or {}).items() if p.get("_status") == "read"]

    def _row(name, mf):
        return ((res.get("set_scores") or {}).get(name) or {}).get(mf) or {}

    def _specific(name):
        """Did this set clear its size-matched null on any platform, and on which?"""
        out = {}
        for mf in plats:
            r = _row(name, mf)
            nc = r.get("null_calibration") or {}
            out[mf] = {"raw_delta": (r.get("score") or {}).get("delta_a_minus_b"),
                       "raw_t": (r.get("score") or {}).get("t"),
                       "coverage": r.get("coverage"),
                       "null_computed": nc.get("computed"),
                       "p_empirical": nc.get("p_empirical_two_sided"),
                       "beats_null": (nc.get("computed") and
                                      (r.get("score") or {}).get("delta_a_minus_b") is not None and
                                      r["score"]["delta_a_minus_b"] > nc.get("null_q975", 1e9)),
                       "verdict": r.get("verdict")}
        return out

    reads = {
        "read_1_does_the_fusion_direct_target_set_reproduce_in_EMC_tissue": {
            "question": "Do the genes with a DNA-binding assay against an NR4A3 FUSION read HIGH "
                        "in EMC tumours, beyond what a random gene set of the same size does on "
                        "the same platform?",
            "set": "A_fusion_dna_binding_targets",
            "per_platform": _specific("A_fusion_dna_binding_targets"),
            "members": sorted(sets["A_fusion_dna_binding_targets"]["genes"]),
            "how_to_read_it": "n=3 genes. The AGGREGATE is underpowered by construction and the "
                              "per-gene reads in `gene_reads` carry the weight. A three-gene set "
                              "that clears a three-gene null is a real reading; a three-gene set "
                              "that does not is not evidence of absence.",
        },
        "read_2_does_the_native_NR4A3_target_set_transfer": {
            "question": "Do native-NR4A3 direct targets — mostly vascular and cardiac — read high "
                        "in EMC?",
            "set": "B_native_nr4a3_dna_binding_targets",
            "per_platform": _specific("B_native_nr4a3_dna_binding_targets"),
            "how_to_read_it": "⚠ A NEGATIVE HERE IS INFORMATIVE AND A POSITIVE IS AMBIGUOUS. "
                              "Filion et al. measured native NR4A3 failing to activate the PPARG "
                              "promoter the fusion activates, so these genes are NOT expected to "
                              "transfer wholesale. If they read high anyway, the likeliest reason "
                              "is that they are proliferation and matrix genes.",
        },
        "read_3_does_the_published_EMC_profile_replicate": {
            "question": "Does the independent published EMC-vs-sarcoma profile (Filion Table 1, "
                        "Affymetrix U133A, neither readable series) replicate here?",
            "sets": ["D_filion_table1_emc_vs_137_sarcomas",
                     "E_filion_table2_overlap_with_subramanian"],
            "per_platform_table1": _specific("D_filion_table1_emc_vs_137_sarcomas"),
            "per_platform_table2_CIRCULAR_ON_GPL3290":
                _specific("E_filion_table2_overlap_with_subramanian"),
            "circularity": res.get("circularity_reading"),
            "how_to_read_it": "⭐ THIS IS THE STRONGEST TEST IN THE FILE, and it is not a test of "
                              "the fusion. Table 1 was derived on a platform and cohort neither "
                              "readable series shares, so replication here is a genuine "
                              "cross-cohort, cross-platform reproduction of the EMC transcriptional "
                              "phenotype. It says the instrument reads EMC; it does NOT say the "
                              "fusion drives those genes.",
        },
        "read_4_pparg_ACTIVITY_resolved_or_bounded": {
            "question": "Is PPARgamma transcriptionally ACTIVE in EMC, or is the KO_DOWN / OE_UP "
                        "disagreement telling us the read cannot be taken here?",
            "arms": {k: _specific("PPARG_" + k) for k in PPARG_ARMS
                     if ("PPARG_" + k) in sets},
            "arms_unresolved": [k for k in PPARG_ARMS if ("PPARG_" + k) not in sets],
            "species_of_each_arm": {
                k: (((res.get("pparg_arms") or {}).get("slots") or {}).get(k) or {})
                .get("species_derived_from_the_matched_term") for k in PPARG_ARMS},
            "how_to_read_it": (
                "The arms must AGREE to be quotable: KO_DOWN and OE_UP are independent "
                "constructions with the SAME expected direction, and KO_UP is the falsifier that "
                "must move the OTHER way. Read each arm's `beats_null` first: an arm that does not "
                "clear its size-matched null has not measured PPARgamma activity, it has measured "
                "the platform. Two arms that both fail their null cannot 'disagree' about biology "
                "— that is the shape of noise around a null, and it is a BOUND on the question "
                "rather than an answer to it."),
            "the_abundance_question_is_elsewhere": "PPARG ABUNDANCE in EMC is already settled and "
                                                   "has one home: "
                                                   "research/manuscripts/pparg-direction-emc.md "
                                                   "§6. This read is about ACTIVITY only.",
        },
    }
    return reads


def _cannot_conclude():
    return {
        "_read_this_before_quoting_anything_above": True,
        "1_up_in_EMC_is_not_driven_by_the_fusion": (
            "⛔ THE CENTRAL LIMIT. A target gene that reads high in EMC is consistent with the "
            "fusion driving it — and equally consistent with (a) EMC's cell of origin expressing "
            "it, (b) the myxoid, hypocellular architecture of EMC against dense comparator "
            "sarcomas, (c) a platform-wide offset between the arms, and (d) the gene being a "
            "generic proliferation or matrix gene. The null calibration removes (c) and part of "
            "(d). It does NOT remove (a) or (b), and nothing available at $0 does."),
        "1b_no_fusion_cistrome_exists_in_the_retrieved_literature": {
            "_this_is_a_SEARCH_RESULT_not_an_assumption": True,
            "question": "Has anyone applied a GENOME-WIDE chromatin method (ChIP-seq, CUT&RUN, "
                        "CUT&Tag, ChIP-exo, ChIP-PET, ATAC-seq) to an NR4A3 FUSION — EWSR1::NR4A3, "
                        "TAF15::NR4A3 or TFG::NR4A3?",
            "corpora_searched": {
                "extraskeletal-myxoid-chondrosarcoma": {"fulltext_files": 693,
                                                        "index_records": 1369},
                "nr4a3-cistrome-tight": {"fulltext_files": 461, "index_records": 792},
                "nr4a3-fusion-partners": {"fulltext_files": 345, "index_records": 530},
                "nr4a3-lbd-vs-af1": {"fulltext_files": 13},
                "pparg-direction-emc-2026-08-06": {"fulltext_files": 764, "index_records": 978},
            },
            "totals": {"fulltext_documents_scanned": 2276, "catalogued_records": 3669,
                       "documents_naming_both_a_cistrome_method_and_NR4A3_NOR1_TEC": 153},
            "result": "ZERO. Not one sentence in 2,276 retrieved documents applies a genome-wide "
                      "chromatin method to an NR4A3 chimera. The only chromatin experiment "
                      "performed with a fusion anywhere in this corpus is Brenca et al.'s "
                      "ChAP-qPCR — TARGET-SPECIFIC amplification at ONE locus (SEMA3C), not a "
                      "genome-wide map.",
            "⛔_how_to_state_it": "‘No EWSR1::NR4A3 cistrome has been retrieved in 2,276 documents "
                                 "across five committed corpora’ — a bounded negative about a "
                                 "SEARCH. It is NOT ‘no such dataset exists’: this searched "
                                 "retrieved full text, not all of PubMed, and a dataset can be "
                                 "deposited without a paper. AN ABSENT READING IS NOT A READING "
                                 "OF ABSENCE.",
            "why_it_matters": "It is the reason the discriminator below has to reach for a "
                              "NON-fusion tumour's cistrome, and the reason that substitution "
                              "must carry Filion's native-does-not-activate-PPARG measurement "
                              "beside it. It also means a fusion cistrome is an OPEN, unclaimed "
                              "experiment rather than a dataset someone forgot to fetch.",
            "reproduce": "research/modalities/nr4a3_fusion_targets.py header names the corpora; "
                         "they are on the `literature-cache` branch under `literature/`.",
        },
        "2_what_would_discriminate": [
            "★ A CISTROME IN THE RIGHT CELL. An NR4A3 ChIP-seq peak set with the FUSION expressed, "
            "intersected with these expression reads: a gene that is up in EMC AND carries a "
            "fusion-bound NBRE within its regulatory region is driven; a gene that is up with no "
            "peak is correlated. The nearest available dataset is Haller et al. 2019 "
            "(PMID 30664630) — NR4A3 ChIP-seq in three human AciCC tumours plus H3K27ac/H3K4me3/"
            "CTCF, processed data at Zenodo doi 10.5281/zenodo.1483691 (OPEN) and raw at EGA "
            "EGAS00001002795 (CONTROLLED ACCESS). ⚠ AciCC carries NATIVE NR4A3 up-regulated by "
            "enhancer hijacking, NOT a fusion, so it answers 'where does the NR4A3 DBD go in a "
            "human tumour' and not 'where does EWSR1::NR4A3 go'. Given Filion's measurement that "
            "native NR4A3 does NOT activate the PPARG promoter the fusion activates, that gap is "
            "real and must be stated whenever this dataset is used.",
            "A knockdown or degradation of the fusion in a genuinely fusion-positive EMC model, "
            "with RNA-seq. No such experiment exists in the literature (see "
            "research/manuscripts/nr4a3-emc-biology-evidence.md, 'the decisive gap'), and the one "
            "EMC line most used is recorded here as not carrying the fusion on the curated record.",
            "Fusion-type-stratified EMC expression data. Brenca et al. 2019 show class-3 vs "
            "class-4-6 semaphorins separating EWSR1- from TAF15-translocated EMC; neither readable "
            "series records which fusion each EMC sample carries, so that axis is unreadable here "
            "and every EMC arm below is a MIXTURE.",
            "Motif-level evidence at $0: an NBRE scan of the promoters of the genes that read high, "
            "against a matched background. That is sequence work, needs no new data, and is NOT "
            "done in this module — it is the obvious next free step.",
        ],
        "3_coordination_note": (
            "⚠ A SIBLING LANE IS WORKING THE NR4A3 CISTROME/ChIP-seq ANGLE FOR RET SPECIFICALLY. "
            "This module deliberately does NOT fetch any cistrome dataset. What it needs from that "
            "lane, stated so it can be supplied rather than duplicated: a peak set with (i) the "
            "factor and construct that was ChIPped, (ii) the genome build, (iii) peak coordinates "
            "or nearest-gene assignments. Given those, `read_1` and `read_2` become "
            "peak-intersected in one offline pass with no new fetch."),
        "4_no_therapeutic_claim": (
            "Nothing here supports a claim of efficacy, selectivity, safety, a therapeutic window "
            "or clinical readiness for any agent, and expression data cannot become that "
            "evidence."),
    }


def _limits():
    return [
        "n = 6 EMC (GPL6244) and n = 10 EMC (GPL3290). Every contrast is small-sample and "
        "uncorrected for multiple testing; t statistics are reported, exact p-values are not, "
        "because this lane has no scipy.",
        "GPL3290 is a two-colour cDNA array read as log-ratios against a reference pool: only the "
        "BETWEEN-GROUP contrast is interpretable, never an absolute level.",
        "The comparator arms differ between platforms — 29 mixed sarcomas including FET-rearranged "
        "LGFMS on GPL6244, versus 3 DFSP + 3 GIST on GPL3290. A gene can move on one and not the "
        "other for that reason alone.",
        "Fusion type is not recorded in either series, so every EMC arm mixes EWSR1::NR4A3 with "
        "whatever TAF15::NR4A3 and rarer variants it contains. Brenca et al. 2019 show those "
        "variants differ transcriptionally, so the mixture attenuates any fusion-specific signal.",
        "Probe->symbol mapping on GPL3290 runs through an EST accession bridge; a gene unreadable "
        "there may be absent from the bridge rather than from the array.",
        "The empirical null is drawn from a seeded random pool of the platform's mapped symbols, "
        "not from the full symbol universe. The pool size, seed and universe are recorded per "
        "platform so the draw is reproducible and auditable.",
        "The null controls for the platform-wide offset and for set SIZE. It does NOT control for "
        "gene-gene correlation within a real pathway, which makes a real set's variance larger "
        "than a random set's — so the empirical p is ANTI-CONSERVATIVE for coherent sets and "
        "should be read as a screen, not a test.",
    ]


# =============================================================================================
# CLI
# =============================================================================================
def _summarise(res):
    print("=" * 100, file=sys.stderr)
    c = res.get("controls") or {}
    print("INSTRUMENT CONTROLS FIRST:", file=sys.stderr)
    for name, chk in (c.get("checks") or {}).items():
        print(f"  {'PASS' if chk.get('pass') else 'FAIL'}  {name}", file=sys.stderr)
        for mf, m in (chk.get("measured") or {}).items():
            print(f"        {mf[:26]:28s} delta={m.get('delta')} t={m.get('t')} "
                  f"readable={m.get('readable')}", file=sys.stderr)
    print(f"  -> {c.get('_reading')}", file=sys.stderr)
    print("-" * 100, file=sys.stderr)
    for mf, p in (res.get("platforms") or {}).items():
        if p.get("_status") != "read":
            print(f"{mf}: {p.get('_status')}", file=sys.stderr)
            continue
        go = p.get("global_offset") or {}
        print(f"{p['gse']}/{p['platform']}: EMC={p['n_EMC']} comp={p['n_comparator']} "
              f"symbols={p.get('n_distinct_symbols_on_platform')}", file=sys.stderr)
        print(f"   GLOBAL OFFSET: {go.get('reading') or go.get('why')}", file=sys.stderr)
    print("-" * 100, file=sys.stderr)
    for name, per in (res.get("set_scores") or {}).items():
        print(f"{name}", file=sys.stderr)
        for mf, r in per.items():
            print(f"   {mf[:26]:28s} {str(r.get('verdict'))[:190]}", file=sys.stderr)
    print("=" * 100, file=sys.stderr)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true",
                    help="CI: fetch GEO + Enrichr, derive, write both files.")
    ap.add_argument("--check", action="store_true",
                    help="Re-derive offline from the inputs cache and diff against the artifact.")
    a = ap.parse_args(argv)

    if a.fetch:
        inp = collect()
        with open(INPUTS, "w") as fh:
            json.dump(inp, fh, indent=1, sort_keys=True)
        print(f"wrote {INPUTS}", file=sys.stderr)
    else:
        if not os.path.exists(INPUTS):
            print(f"no inputs cache at {INPUTS}; run with --fetch in CI", file=sys.stderr)
            return 2
        inp = json.load(open(INPUTS))

    res = derive(inp)
    if a.check:
        if not os.path.exists(OUT):
            print("no artifact to check against", file=sys.stderr)
            return 2
        old = json.load(open(OUT))
        drift = []
        for k in ("controls", "set_scores", "circularity_reading"):
            if json.dumps(old.get(k), sort_keys=True) != json.dumps(res.get(k), sort_keys=True):
                drift.append(k)
        if drift:
            print(f"DRIFT in: {', '.join(drift)}", file=sys.stderr)
            return 1
        print("offline re-derive matches the artifact", file=sys.stderr)
        return 0

    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(f"wrote {OUT}", file=sys.stderr)
    _summarise(res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
