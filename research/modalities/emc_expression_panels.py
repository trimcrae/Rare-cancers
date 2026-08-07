#!/usr/bin/env python3
"""
Six targeted expression reads in the two READABLE EMC series — one CI dispatch, six lanes settled.

⭐ WHY THIS EXISTS, AND WHY IT IS NOT `emc_atr_vulnerability.py --refresh-part-b`.
Part B of the ATR assessment reads CONCEPT scores over MSigDB/Reactome/GO gene sets, and its inputs
cache therefore holds per-sample values only for the genes those sets happen to contain. Every one
of the six reads below asks for genes that are NOT in those sets — `ASS1`, `NR2F1`, `CSPG4`, the
chondroitin-sulfate sulfotransferases, `DLL3`/`ASCL1`/`NEUROD1`/`INSM1`, a PPARγ TARGET-gene set,
a published hypoxia metagene. Reading them needs a fresh fetch with a different `want` list, and it
must NOT be able to perturb the committed ATR grading artifact (CLAUDE.md §1: one fact, one home).
So: its own module, its own artifact, its own workflow mode.

⛔ THE SIX READS, AND THE ONE RULE THAT GOVERNS ALL OF THEM.
    1. `ASS1`                      — arginine auxotrophy / ADI-PEG20. One binary answer.
    2. CS/GAG biosynthesis + PAPS  — oncofetal chondroitin sulfate, CSPG4, substrate reduction,
                                     chondroitinase.
    3. PPARγ TARGET-GENE signature — NOT `PPARG` abundance. Abundance is already measured twice,
                                     concordantly (`pparg-direction-emc.md` §6); the missing
                                     measurement is receptor ACTIVITY, i.e. transcriptional output.
    4. NE panel                    — `DLL3`, `ASCL1`, `NEUROD1`, `INSM1`, `HES1`.
    5. Hypoxia metagene            — Buffa / Winter, whichever the fetch resolves.
    6. `NR2F1`                     — the precondition for the dormancy lane.

⛔⛔ THE RULE (CLAUDE.md §4). **AN ABSENT READING IS NOT A READING OF ABSENCE.** A gene with no probe
mapping to it on a platform is reported `readable: false` with the reason, and the verdict sentence
is *"the read could not be taken on this platform"* — NEVER *"the gene is not expressed"*. And a
POPULATED field is not a MEASURED one: every gene row carries `n_probes_mapping` and the actual
probe IDs, which only a real platform annotation can produce, rather than a default that could fill
itself in. A panel score is emitted only when its coverage clears a stated floor, and a panel that
does not clear it emits `UNDERPOWERED` with the coverage rather than a number.

⛔ LANGUAGE DISCIPLINE. An expression reading is not an efficacy, selectivity, safety, therapeutic-
window or clinical-readiness claim, and nothing here may be written as one. Every read is n = 6 and
n = 10 tumours on two decade-old array platforms, uncorrected for multiple testing.

$0 — a GitHub-hosted CPU runner. Pure stdlib. The dev sandbox's egress proxy 403s NCBI/GEO on
CONNECT, which is the whole reason this runs in CI (CLAUDE.md §6).

Usage:
    python emc_expression_panels.py --fetch     # CI: fetch + derive + write both files
    python emc_expression_panels.py             # derive from the cached inputs (offline)
    python emc_expression_panels.py --check     # re-derive offline and diff against the artifact
"""

import argparse
import json
import os
import re
import sys
from bisect import bisect_left
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "emc-expression-panels.json")
INPUTS = os.path.join(HERE, "emc-expression-panels-inputs.json")

sys.path.insert(0, HERE)
from emc_atr_vulnerability import (  # noqa: E402
    ENRICHR_LIB,
    MSIGDB_JSP,
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
    "SIX TARGETED EXPRESSION READS IN EMC TUMOUR TISSUE. Every number here is a transcript-level "
    "reading in archival tumour material on two array platforms. It is NOT evidence of efficacy, "
    "selectivity, safety, a therapeutic window or clinical readiness for any agent named anywhere "
    "in this file, and it cannot become that evidence from public expression data. A gene being "
    "high or low in six or ten tumours is a hypothesis-generating observation."
)

# ---------------------------------------------------------------------------------------------
# THE TWO READABLE SERIES. Named, not searched — both are already characterised, with their probe
# mapping rates, in `emc-atr-vulnerability.json` -> part_b_emc_tumour_signature.series_readability,
# which is the one home of that characterisation (CLAUDE.md §1). The rates below are quoted from it
# as the PRIOR the fresh run is checked against, and the run records its own measured rate beside
# them: a mapping rate that has moved is a diagnosable event, not a silent one.
#
# ⚠ ONE MATRIX FILE PER SERIES, NAMED. GSE4303 is SEVEN sibling print runs of one clone library and
# only GPL3290 carries a usable EMC-vs-comparator contrast (10 EMC, 3 DFSP, 3 GIST on the same
# array). Fetching the other six would multiply the EST accession->symbol bridge — the expensive,
# failure-prone half — for platforms that carry 2 or 3 samples each and cannot score a contrast.
# ---------------------------------------------------------------------------------------------
TARGETS = [
    {"gse": "GSE24369",
     "matrix_file": "GSE24369_series_matrix.txt.gz",
     "platform_expected": "GPL6244",
     "why": "6 EMC tumours against 29 comparator sarcomas on one Affymetrix Gene ST array, and the "
            "comparator arm is itself FET-rearranged (LGFMS is FUS::CREB3L2).",
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

# ---------------------------------------------------------------------------------------------
# THE PANELS.
#
# ⚠ PROVENANCE IS PER PANEL AND IT IS NOT UNIFORM, SO IT IS STATED PER PANEL. Two kinds appear:
#   * FETCHED  — a published gene set pulled at run time from Enrichr or MSigDB, recorded with the
#                library, the VERBATIM matched term and the upstream citation. These carry the
#                statistical weight.
#   * CURATED  — a pathway-membership list written here. A curated list is NOT a published
#                signature and is labelled as such at the point of use, per the precedent in
#                `emc_atr_vulnerability.fetch_gene_sets`. It exists so the read still has an
#                interpretable anchor if a fetch fails, and so a fetched set can be cross-checked
#                against genes a reader can recognise.
# ---------------------------------------------------------------------------------------------
CURATED = ("⚠ REPO-CURATED pathway-membership list. This is NOT a published gene set or signature. "
           "Any statement resting on it must say so.")

PANELS = {
    "instrument_controls": {
        "read_id": "control",
        "question": "Does this pipeline reproduce readings whose answer is already known, on these "
                    "exact platforms? A panel of six reads is worth nothing until the instrument "
                    "has produced a known answer.",
        "provenance": CURATED,
        "groups": {
            "fusion_and_its_published_direct_target": ["NR4A3", "ENO3"],
            "proliferation_reference": ["MKI67"],
            "fet_family_context": ["EWSR1", "TAF15", "FUS"],
        },
        "expected": {
            "NR4A3": "UP in EMC. EWSR1::NR4A3 places NR4A3 sequence under the partner's promoter, "
                     "and NR4A3 over-expression is the disease-defining event. A read that does "
                     "not recover this is an instrument failure, not a biological finding. ⚠ On a "
                     "3'-biased or EST-annotated array the probe may sit in the region the fusion "
                     "replaces rather than the one it retains — so a NULL here is a probe-"
                     "placement question, not a biological one.",
            "ENO3": "UP in EMC. A published direct transactivation target of an NR4A3 fusion "
                    "through chromatin modification of its promoter (PMID 26310886), and already "
                    "measured up in BOTH of these series from the ATR assessment's cached "
                    "gene-set subset. This is the closest thing to a positive control available.",
            "MKI67": "approximately FLAT in GSE24369. EMC is slow-cycling; a large proliferation "
                     "delta would say the contrast is being driven by cellularity.",
        },
    },
    "arginine_auxotrophy": {
        "read_id": "read_1_ASS1",
        "question": "Is ASS1 low in EMC relative to comparator sarcomas — the biomarker that "
                    "defines an arginine auxotroph and the selection criterion the arginine-"
                    "deprivation agents (ADI-PEG20 / pegargiminase) are given on?",
        "provenance": CURATED + " The urea-cycle / arginine-handling membership is textbook "
                                "biochemistry; the read that matters is the single gene ASS1.",
        "primary_gene": "ASS1",
        "groups": {
            "the_read": ["ASS1"],
            "urea_cycle_context": ["ASL", "ARG1", "ARG2", "OTC", "CPS1", "NAGS"],
            "arginine_transport_and_use": ["SLC7A1", "SLC7A2", "NOS2", "ODC1"],
        },
        "direction_that_supports_the_lane": "ASS1 DOWN in EMC",
        "what_it_cannot_settle": "Transcript level is not protein level, and ASS1 loss in the "
                                 "arginine-deprivation literature is an IHC call. A low transcript "
                                 "read is a reason to stain, not a biomarker call, and it asserts "
                                 "nothing about whether any arginine-depleting agent works in EMC.",
    },
    "cs_gag_paps": {
        "read_id": "read_2_CS_GAG_PAPS",
        "question": "Does EMC carry the chondroitin-sulfate biosynthetic and sulfation machinery "
                    "its matrix implies — and specifically the 4-O-sulfotransferase arm that the "
                    "placental-type oncofetal CS epitope depends on?",
        "provenance": CURATED + " Cross-checked against FETCHED Reactome / GO chondroitin-sulfate "
                                "biosynthesis sets where those resolve; see `signature_sets`.",
        "groups": {
            "gag_linker_tetrasaccharide": ["XYLT1", "XYLT2", "B4GALT7", "B3GALT6", "B3GAT3"],
            "cs_backbone_polymerisation": ["CSGALNACT1", "CSGALNACT2", "CHSY1", "CHSY3",
                                           "CHPF", "CHPF2"],
            "cs_sulfotransferases_4O": ["CHST11", "CHST12", "CHST13", "CHST14"],
            "cs_sulfotransferases_6O": ["CHST3", "CHST7"],
            "cs_sulfotransferases_other": ["CHST15", "UST"],
            "dermatan_epimerase": ["DSE", "DSEL"],
            "paps_module": ["PAPSS1", "PAPSS2", "SLC35B2", "SLC35B3", "BPNT1"],
            "cs_proteoglycan_core_proteins": ["CSPG4", "ACAN", "VCAN", "BCAN", "NCAN", "BGN",
                                              "DCN", "CSPG5", "SRGN", "NG2"],
            "hyaluronan_contrast": ["HAS1", "HAS2", "HAS3", "HYAL1", "HYAL2", "CD44", "HMMR"],
            "gag_catabolism_chondroitinase_context": ["ARSB", "GALNS", "GUSB", "HEXA", "HEXB"],
        },
        "enzyme_annotations": {
            "CHST11": "C4ST-1, chondroitin 4-O-sulfotransferase 1",
            "CHST12": "C4ST-2", "CHST13": "C4ST-3",
            "CHST14": "D4ST-1, dermatan 4-O-sulfotransferase 1",
            "CHST3": "C6ST-1, chondroitin 6-O-sulfotransferase 1", "CHST7": "C6ST-2",
            "CHST15": "GalNAc4S-6ST — makes the 4,6-disulfated (CS-E) unit",
            "UST": "uronyl 2-O-sulfotransferase",
            "PAPSS1": "PAPS synthase 1 — makes the universal sulfate donor",
            "PAPSS2": "PAPS synthase 2",
            "SLC35B2": "PAPS transporter 1 (Golgi)", "SLC35B3": "PAPS transporter 2",
            "CSPG4": "the CSPG4/MCSP protein backbone; `NG2` is the rodent alias and is included "
                     "only so an alias-annotated platform is not silently missed",
            "_provenance": "⚠ Enzyme names are domain knowledge, NOT retrieved in this run. They "
                           "label the groups; they carry no weight in any number.",
        },
        "direction_that_supports_the_lane": "the 4-O arm (CHST11/12/13/14) and the backbone "
                                            "machinery UP in EMC, with the PAPS module present",
        "what_it_cannot_settle": "⛔ A SULFATION PATTERN HAS NO GENE. Transcript levels of "
                                 "sulfotransferases are a proxy for the CAPACITY to make an "
                                 "epitope, never a measurement of the epitope. Nothing here says "
                                 "the placental-type CS epitope is present on EMC tissue; only a "
                                 "stain or a binding assay can say that. It asserts nothing about "
                                 "whether any CS-directed agent binds, works or is safe in EMC.",
    },
    "pparg_target_activity": {
        "read_id": "read_3_PPARG_ACTIVITY",
        "question": "Is PPARγ TRANSCRIPTIONAL OUTPUT elevated in EMC — i.e. is the receptor whose "
                    "gene the fusion demonstrably drives actually DOING anything?",
        "provenance": "FETCHED — see `signature_sets.pparg_*`. The curated core below is a "
                      "labelled cross-check, never the headline. " + CURATED,
        "groups": {
            "abundance_context_NOT_the_read": ["PPARG", "PPARGC1A", "RXRA", "RXRB", "CEBPA",
                                               "CEBPB"],
            "pparg_canonical_direct_targets_curated": ["FABP4", "CD36", "LPL", "PLIN1", "ADIPOQ",
                                                       "ANGPTL4", "PDK4", "CIDEC", "AQP7", "PCK1",
                                                       "ACOX1", "SCD"],
        },
        "abundance_is_not_the_read": (
            "⛔ `PPARG` and `PPARGC1A` appear ONLY as interpretive context and are marked "
            "`is_the_read: false`. PPARG ABUNDANCE in EMC is already measured twice, concordantly "
            "(Subramanian 2005, n=10; Filion 2009, n=3 fusion-verified), and its one home is "
            "`research/manuscripts/pparg-direction-emc.md` §6. Re-reporting abundance as if it were "
            "new would be the second copy of a settled fact. The MISSING measurement, named in that "
            "memo as the one thing nobody has ever done, is receptor ACTIVITY."),
        "direction_reading_rules": (
            "⚠ THIS READ CONSTRAINS THE DIRECTION QUESTION; IT DOES NOT DECIDE IT, AND THE "
            "ASYMMETRY IS THE POINT.\n"
            " * Target genes UP in EMC ⇒ the receptor is transcriptionally ENGAGED. That says the "
            "   axis is live rather than an inert abundance artefact. It does NOT establish "
            "   saturation, which is the only thing that would make an agonist redundant, and "
            "   which no measurement here or in the literature reaches.\n"
            " * Target genes FLAT or DOWN while PPARG abundance is UP ⇒ an abundant receptor with "
            "   no measurable output, i.e. an unoccupied or actively restrained receptor — the "
            "   reading most consistent with agonism having something left to do.\n"
            " ⛔ NEITHER reading establishes that an agonist or an antagonist helps a patient, and "
            "   neither is a claim about any thiazolidinedione, zaltoprofen, trabectedin or any "
            "   combination. The direction question's adjudicated state — UNRESOLVED, leaning "
            "   agonism, T1 with a model-identity caveat — has ONE home and this file does not "
            "   move it: `research/manuscripts/pparg-direction-emc.md`."),
        "what_it_cannot_settle": "Ligand occupancy, receptor activity in the pharmacological sense, "
                                 "and whether any agonist or antagonist has an effect in EMC. A "
                                 "target-gene signature in bulk archival tissue is transcriptional "
                                 "output confounded by cell-type composition — adipose tissue "
                                 "adjacent to a deep soft-tissue tumour expresses the same genes.",
    },
    "neuroendocrine_state": {
        "read_id": "read_4_NE_STATE",
        "question": "Does EMC occupy an SCLC-style neuroendocrine-high state — and specifically, is "
                    "DLL3 readable, and is it up?",
        "provenance": CURATED + " The four-way lineage-TF scheme (ASCL1 / NEUROD1 / POU2F3 / YAP1) "
                                "is Rudin et al., Nature Reviews Cancer 2019 — cited from domain "
                                "knowledge, NOT retrieved in this run; treat as [unverified].",
        "groups": {
            "the_read": ["DLL3", "ASCL1", "NEUROD1", "INSM1", "HES1"],
            "sclc_subtype_lineage_tfs": ["ASCL1", "NEUROD1", "POU2F3", "YAP1"],
            "generic_ne_markers": ["CHGA", "CHGB", "SYP", "NCAM1", "ENO2", "UCHL1"],
            "notch_rest_axis": ["NOTCH1", "NOTCH2", "NOTCH3", "REST", "DLL1", "JAG1"],
        },
        "direction_that_supports_the_lane": "DLL3/ASCL1/INSM1 UP with HES1 DOWN — the ASCL1-high, "
                                            "NOTCH-off configuration",
        "what_it_cannot_settle": "Surface protein presence. DLL3 as a therapeutic address is a "
                                 "SURFACE-protein question and this is a transcript read; the "
                                 "repo's own surfaceome work is where that distinction lives. It "
                                 "asserts nothing about whether any DLL3-directed agent is active "
                                 "or safe in EMC.",
    },
    "hypoxia": {
        "read_id": "read_5_HYPOXIA",
        "question": "Is EMC hypoxic by a published hypoxia metagene — the premise underneath the "
                    "radioresistance framing and the hypoxia-prodrug reasoning?",
        "provenance": "FETCHED — see `signature_sets.hypoxia_*`. Buffa and Winter are both "
                      "attempted by name; whichever resolve are scored SEPARATELY and never "
                      "merged. The curated canonical-HIF-target list is a labelled cross-check.",
        "groups": {
            "hypoxia_canonical_hif_targets_curated": ["CA9", "VEGFA", "SLC2A1", "LDHA", "PGK1",
                                                      "HK2", "ADM", "ANGPTL4", "NDRG1", "BNIP3",
                                                      "P4HA1", "PLOD2", "EGLN3", "ALDOA", "PDK1"],
            "hif_machinery_context": ["HIF1A", "EPAS1", "ARNT", "VHL", "EGLN1", "EGLN2", "HIF1AN"],
        },
        "direction_that_supports_the_lane": "the metagene UP in EMC",
        "what_it_cannot_settle": "⛔ A hypoxia METAGENE is a transcriptional shadow of hypoxia, not "
                                 "an oxygen measurement, and it has never been calibrated in EMC or "
                                 "in any myxoid sarcoma. It also cannot separate tumour-cell "
                                 "hypoxia from a hypovascular matrix compartment. It disciplines "
                                 "the framing; it licenses no radiobiological claim, and no α/β or "
                                 "BED statement follows from it.",
    },
    "nr2f1_dormancy": {
        "read_id": "read_6_NR2F1",
        "question": "Is NR2F1 readable and expressed in EMC at all — the precondition without "
                    "which the dormancy-agonism lane has no target?",
        "provenance": CURATED + " The dormancy-program genes are those NAMED in the primary source "
                                "(Sosa et al., Nature Communications 2015, PMID 25636082) — a "
                                "hand-listed subset, not the paper's signature, and [unverified] "
                                "at the text level in this run.",
        "primary_gene": "NR2F1",
        "groups": {
            "the_read": ["NR2F1"],
            "paralogues_the_selectivity_risk": ["NR2F2", "NR2F6"],
            "nr2f1_dormancy_program_named_genes_curated": ["SOX9", "RARB", "NANOG", "SOX2"],
            "dormancy_associated_context_curated": ["CDKN1A", "CDKN1B", "TGFB2", "THBS1", "DKK1",
                                                    "NR4A1", "NR4A2"],
        },
        "direction_that_supports_the_lane": "NR2F1 PRESENT (readable and not at the array floor). "
                                            "⚠ The lane needs a target that EXISTS, not one that "
                                            "is already high — a dormancy AGONIST acts on a "
                                            "receptor that is present and under-active, so a high "
                                            "reading is not automatically the supportive one.",
        "what_it_cannot_settle": "Whether NR2F1 is druggable in EMC, whether the published tool "
                                 "agonist binds it in this context, and anything at all about "
                                 "paralogue selectivity — which is the risk that sank the "
                                 "flagship lane and is not measurable from expression.",
    },
    # -----------------------------------------------------------------------------------------
    # READ 7 — added 2026-08-07 for the RET cistrome lane.
    #
    # ⭐ WHY IT IS HERE RATHER THAN IN A SEVENTH MODULE. This module already reads 137 genes from
    # these two matrices in one dispatch and its ENO3 control reproduces a committed value; a
    # second module would be a second copy of the whole GEO fetch (CLAUDE.md §1) for the sake of
    # eleven symbols.
    #
    # ⛔ WHAT THIS READ IS FOR, PRECISELY. `emc-ret-lane.md` §3 establishes that the ONLY report
    # of RET *activation* in EMC is one sentence in a paywalled 2014 abstract over "a limited set
    # of samples" of an n = 10 series, with no numerator and no denominator, and that RET in EMC
    # has never been given the blinded-TMA test that decided MET in clear cell sarcoma (PMID
    # 34885165: MET protein 82 %, phospho-MET 4 %). ⛔ NOTHING IN A TRANSCRIPT READ CAN CLOSE
    # THAT GAP — mRNA abundance is the measurement whose insufficiency is the whole point of the
    # MET guard. What this read CAN do, and the only thing it is quoted for:
    #   (a) corroborate or fail to corroborate PMID 28423517's RET-abundance finding in an
    #       INDEPENDENT series and, for the first time, in a second one (GSE4303/GPL3290);
    #   (b) say whether RET's own LIGAND/CO-RECEPTOR module is present at all — the clear cell
    #       sarcoma study failed on ligand absence (HGF 16 %) as much as on phospho-absence, so a
    #       tumour with abundant receptor and no ligand is the same shape of negative;
    #   (c) put RET beside the cistrome lane's target-gene controls (ENO3 already in the control
    #       panel, SEMA3C added here) so an occupancy reading and an abundance reading are on the
    #       same tumours.
    # -----------------------------------------------------------------------------------------
    "ret_axis": {
        "read_id": "read_7_RET",
        "question": "Is RET readable and elevated in EMC in BOTH readable series — and is the "
                    "GDNF-family ligand/co-receptor module that would be needed to engage it "
                    "present at all?",
        "provenance": CURATED + " The GDNF-family membership (four ligands, four GFRα "
                                "co-receptors) is textbook receptor biology; the reads that "
                                "carry weight are the single genes RET, GDNF and GFRA1.",
        "primary_gene": "RET",
        "groups": {
            "the_read": ["RET"],
            "gdnf_family_ligands": ["GDNF", "NRTN", "ARTN", "PSPN"],
            "gfra_co_receptors": ["GFRA1", "GFRA2", "GFRA3", "GFRA4"],
            "alternative_hypothesis_the_vegfr_attribution": ["VEGFA", "KDR", "FLT1", "FLT4",
                                                             "PDGFRA", "PDGFRB", "KIT"],
            "downstream_nodes_the_ccs_tma_stained": ["MAPK1", "MAPK3", "AKT1", "RPS6", "GAB1"],
            "published_nr4a3_target_genes_for_the_cistrome_lane": ["SEMA3C", "ENO3"],
        },
        "direction_that_supports_the_lane": "RET UP in EMC in both series, with at least one "
                                            "GDNF-family ligand and GFRA1 readable and present",
        "what_it_cannot_settle": (
            "⛔ ACTIVATION. This is mRNA abundance. The bar RET in EMC has never been given is a "
            "blinded phospho-RET / ligand / downstream-node tissue microarray with a stated "
            "denominator (the instrument that decided MET in clear cell sarcoma, PMID 34885165), "
            "and no expression series can substitute for it — `emc-ret-lane.md` §3 is the one "
            "home of that finding and this read does not move it. It also cannot separate "
            "tumour-cell RET from stromal or entrapped-nerve RET in a hypocellular, matrix-rich "
            "tumour, which is the RET lane's own falsifier. And it asserts nothing about whether "
            "selpercatinib, pralsetinib or any RET-directed agent binds, works or is safe in "
            "EMC — no EMC patient has ever received one."),
    },
}

# ---------------------------------------------------------------------------------------------
# FETCHED SIGNATURE SETS. Each entry is a list of candidates tried IN ORDER; the first that
# resolves wins for that slot, and every attempt (including every failure) is recorded. Nothing
# here is quoted from memory: a set that does not resolve is reported as unresolved and its slot
# scores nothing, rather than being quietly replaced by a curated stand-in.
#
# ⚠ `enrichr` candidates are (library_key, needle) where the needle is matched against a
# NORMALISED term string; the VERBATIM term that matched is what gets recorded.
# ⚠ `msigdb` candidates are exact MSigDB set names fetched through the .jsp download path — the
# same path `emc_atr_vulnerability` uses, and for the same measured reason: the
# /download_geneset/{NAME}.json endpoint does not exist and 404s for every name (run 30856488704).
# ---------------------------------------------------------------------------------------------
ENRICHR_LIBRARIES = {
    "hallmark": (["MSigDB_Hallmark_2020"],
                 "MSigDB Hallmark collection — Liberzon et al., Cell Systems 2015, served via "
                 "Enrichr (Kuleshov et al., Nucleic Acids Research 2016)"),
    "reactome": (["Reactome_Pathways_2024", "Reactome_2022", "Reactome_2016"],
                 "Reactome — Milacic et al., Nucleic Acids Research 2024, served via Enrichr "
                 "(Kuleshov et al., Nucleic Acids Research 2016)"),
    "gobp": (["GO_Biological_Process_2025", "GO_Biological_Process_2023",
              "GO_Biological_Process_2021"],
             "Gene Ontology biological process — Ashburner et al., Nature Genetics 2000, served "
             "via Enrichr (Kuleshov et al., Nucleic Acids Research 2016)"),
    "chea": (["ChEA_2022", "ChEA_2016"],
             "ChEA — transcription-factor target sets from published ChIP-X experiments; each "
             "term carries its own source PMID in the term string (Lachmann et al., "
             "Bioinformatics 2010), served via Enrichr (Kuleshov et al., NAR 2016)"),
    "trrust": (["TRRUST_Transcription_Factors_2019"],
               "TRRUST v2 — a manually curated transcriptional regulatory network mined from the "
               "literature (Han et al., Nucleic Acids Research 2018), served via Enrichr"),
    "encode_chea": (["ENCODE_and_ChEA_Consensus_TFs_from_ChIP-X"],
                    "ENCODE + ChEA consensus TF target sets, served via Enrichr (Kuleshov et al., "
                    "Nucleic Acids Research 2016)"),
    "tf_perturb": (["TF_Perturbations_Followed_by_Expression"],
                   "TF perturbation followed by expression profiling — genes that MOVE when the "
                   "factor is knocked out / knocked down / over-expressed, served via Enrichr "
                   "(Kuleshov et al., Nucleic Acids Research 2016)"),
}

SIGNATURE_SLOTS = {
    # --- read 3: PPARγ ACTIVITY -----------------------------------------------------------------
    # ⭐ WHY SEVERAL, SCORED SEPARATELY. There is no single canonical "the PPARγ target-gene
    # signature", and picking one would be a choice this file could not defend. Three INDEPENDENT
    # instrument classes are taken instead — ChIP-derived occupancy (ChEA / ENCODE), literature-
    # curated regulation (TRRUST), and perturbation-response (TF_Perturbations) — because
    # concordance ACROSS instrument classes is an argument and one set's value is not.
    # ⛔ `exclude` IS LOAD-BEARING, NOT TIDINESS. `_norm` strips punctuation, so the normalised form
    # of a **PPARGC1A** term — "ppargc1a…" — STARTS WITH "pparg". Without the exclusion the ChEA,
    # ENCODE and perturbation slots would silently resolve to a PGC-1α set and be scored, labelled
    # and consumed as a PPARγ target signature. PGC-1α is a COACTIVATOR of a different family; it is
    # also the gene the 2005 EMC profiling study reports alongside PPARG, so the confusion has a
    # ready-made path into the manuscript. `prefer` is the weaker of the two: among several real
    # PPARG experiments it takes a HUMAN one over a mouse one, and records which rule fired.
    "pparg_chip_chea": {
        "read_id": "read_3_PPARG_ACTIVITY", "role": "pparg_target_set",
        "what": "PPARG target genes from published ChIP-X experiments (ChEA). The matched term "
                "carries the source experiment's own PMID in its name.",
        "enrichr": [("chea", "pparg")], "exclude": ["ppargc"], "prefer": ["human"],
    },
    "pparg_consensus_encode_chea": {
        "read_id": "read_3_PPARG_ACTIVITY", "role": "pparg_target_set",
        "what": "PPARG consensus targets from ENCODE + ChEA ChIP-X.",
        "enrichr": [("encode_chea", "pparg")], "exclude": ["ppargc"], "prefer": ["human"],
    },
    "pparg_curated_trrust": {
        "read_id": "read_3_PPARG_ACTIVITY", "role": "pparg_target_set",
        "what": "PPARG targets from TRRUST v2, a manually curated literature-mined regulatory "
                "network.",
        "enrichr": [("trrust", "ppargh"), ("trrust", "pparg")],
        "exclude": ["ppargc"], "prefer": ["human"],
    },
    # ⭐ THE PERTURBATION SLOT IS SPLIT INTO THREE ARMS, AND THE THIRD IS A DIRECTIONAL CONTROL.
    # ⚠ The first version asked for one term matching "pparg" and got
    # `PPARG DEFICIENCY MOUSE GSE23421 CREEDSID GENE 1231 DOWN` — the right arm, chosen ALPHABETICALLY
    # (measured, run 31182233077). An accident that lands on the correct answer is still an accident,
    # and the twelve alternatives it beat included the exact opposite arm. So the arms are now named
    # by a HARD requirement on the term rather than by preference, and all three are scored:
    #   * KO_DOWN — genes that FALL when PPARG is removed, i.e. PPARγ-DEPENDENT genes. If the
    #               receptor is transcriptionally engaged in EMC these should read HIGH.
    #   * OE_UP   — genes that RISE when PPARG is over-expressed. Independent construction, same
    #               expected direction, so agreement between them is worth more than either alone.
    #   * KO_UP   — genes that RISE when PPARG is removed. ⛔ THE CONTROL: it must NOT move the same
    #               way as KO_DOWN. If both arms read high, the contrast is measuring something the
    #               two sets share — cell-type composition, array behaviour, gene length — and not
    #               PPARγ output at all. A read with no arm that can fail is not a read.
    "pparg_perturbation_KO_DOWN": {
        "read_id": "read_3_PPARG_ACTIVITY", "role": "pparg_target_set",
        "what": "Genes DOWN when PPARG is knocked out / deficient — PPARγ-DEPENDENT genes. High in "
                "EMC is the reading consistent with an engaged receptor.",
        "enrichr": [("tf_perturb", "pparg")], "exclude": ["ppargc"],
        "require_any": ["deficiency", "ko"], "require_suffix": "down",
    },
    "pparg_perturbation_OE_UP": {
        "read_id": "read_3_PPARG_ACTIVITY", "role": "pparg_target_set",
        "what": "Genes UP when PPARG is over-expressed — an independently constructed set with the "
                "same expected direction as KO_DOWN.",
        "enrichr": [("tf_perturb", "pparg")], "exclude": ["ppargc"],
        "require_any": ["oe"], "require_suffix": "up",
    },
    "pparg_perturbation_KO_UP_CONTROL": {
        "read_id": "read_3_PPARG_ACTIVITY", "role": "directional_control_NOT_a_target_set",
        "what": "⛔ THE FALSIFIER. Genes UP when PPARG is knocked out — the arm that should NOT "
                "track the other two. If it moves with them, the contrast is not measuring PPARγ "
                "output and read 3 must not be quoted.",
        "enrichr": [("tf_perturb", "pparg")], "exclude": ["ppargc"],
        "require_any": ["deficiency", "ko"], "require_suffix": "up",
    },
    "adipogenesis_process_proxy": {
        "read_id": "read_3_PPARG_ACTIVITY", "role": "process_proxy_NOT_a_target_set",
        "what": "⚠ HALLMARK_ADIPOGENESIS is a PROCESS, not a PPARγ target set. It is scored here "
                "only because the ATR assessment already scores it as an unrelated control on "
                "these same two matrices, so it is the one axis on which this module can be "
                "checked against a committed independent read.",
        "enrichr": [("hallmark", "adipogenesis")],
    },
    # --- read 7: THE NR4A TARGET-GENE PROGRAM, AND WHETHER *RET* IS IN IT -----------------------
    #
    # ⭐ WHY THESE ARE HERE. The RET cistrome lane (`emc_ret_cistrome.py`) asks whether NR4A3
    # OCCUPIES the RET locus. These slots ask a DIFFERENT and partly better question from a
    # completely independent instrument class: is *RET* in a published NR4A3 target-gene set —
    # and, for the perturbation arms, **does RET MOVE when NR4A3 is perturbed**? Occupancy without
    # a functional readout is what made the ENO3 precedent need luciferase on top of ChIP
    # (PMID 26310886); a perturbation set is the cheap shadow of that missing experiment.
    # Concordance ACROSS instrument classes is an argument; one set's membership is not.
    #
    # ⚠ AND THEY ARE SCORED ACROSS EMC vs COMPARATOR SARCOMAS, which is a second use of the same
    # fetch: if the fusion drives a recognisable NR4A3 program, an NR4A3 target set should read UP
    # in EMC against other sarcomas. That is an INSTRUMENT check on the whole lane — an NR4A3
    # target program that is NOT up in the disease defined by an NR4A3 fusion would say the sets
    # do not transfer to this context, and would discipline every membership claim below.
    #
    # ⛔ ALL THREE PARALOGUES ARE FETCHED, for the same reason the cistrome module reads all
    # three: "RET is an NR4A3 target" means something different if RET is in the NR4A1 and NR4A2
    # sets too. `exclude` carries `nr4a` off the front of nothing here — the three symbols share
    # no prefix with each other under `_norm` — but each slot still hard-requires its own symbol.
    "nr4a3_targets_chea": {
        "read_id": "read_7_RET", "role": "nr4a3_target_set",
        "what": "NR4A3 target genes from published ChIP-X experiments (ChEA). The matched term "
                "carries the source experiment's own PMID in its name, so the provenance of a "
                "membership call is checkable.",
        "enrichr": [("chea", "nr4a3")], "prefer": ["human"],
    },
    "nr4a3_targets_encode_chea": {
        "read_id": "read_7_RET", "role": "nr4a3_target_set",
        "what": "NR4A3 consensus targets from ENCODE + ChEA ChIP-X.",
        "enrichr": [("encode_chea", "nr4a3")], "prefer": ["human"],
    },
    "nr4a3_targets_trrust": {
        "read_id": "read_7_RET", "role": "nr4a3_target_set",
        "what": "NR4A3 targets from TRRUST v2, a manually curated literature-mined regulatory "
                "network — an instrument class independent of both ChIP and perturbation.",
        "enrichr": [("trrust", "nr4a3")], "prefer": ["human"],
    },
    "nr4a3_perturbation_KD_DOWN": {
        "read_id": "read_7_RET", "role": "nr4a3_target_set",
        "what": "⭐ THE FUNCTIONAL ARM. Genes DOWN when NR4A3 is knocked down / out — i.e. genes "
                "that DEPEND on NR4A3. If RET is in this set, RET abundance responds to NR4A3 "
                "loss, which occupancy alone cannot show.",
        "enrichr": [("tf_perturb", "nr4a3")],
        "require_any": ["knockdown", "kd", "deficiency", "ko"], "require_suffix": "down",
    },
    "nr4a3_perturbation_OE_UP": {
        "read_id": "read_7_RET", "role": "nr4a3_target_set",
        "what": "Genes UP when NR4A3 is over-expressed — independently constructed, same expected "
                "direction as KD_DOWN, so agreement between them is worth more than either alone. "
                "⭐ And it is the arm closest to EMC's own biology: the disease-defining event is "
                "NR4A3 sequence placed under a partner's promoter, i.e. over-expression.",
        "enrichr": [("tf_perturb", "nr4a3")],
        "require_any": ["oe", "overexpression"], "require_suffix": "up",
    },
    "nr4a3_perturbation_KD_UP_CONTROL": {
        "read_id": "read_7_RET", "role": "directional_control_NOT_a_target_set",
        "what": "⛔ THE FALSIFIER, on the pattern read 3 already uses. Genes UP when NR4A3 is "
                "removed — the arm that should NOT track the other two. If it moves with them, "
                "the contrast is measuring something the sets share rather than NR4A3 output, and "
                "no membership call below may be quoted.",
        "enrichr": [("tf_perturb", "nr4a3")],
        "require_any": ["knockdown", "kd", "deficiency", "ko"], "require_suffix": "up",
    },
    "nr4a1_targets_chea": {
        "read_id": "read_7_RET", "role": "paralogue_target_set",
        "what": "NR4A1 targets from ChEA — the paralogue arm. A gene in ALL THREE paralogues' "
                "target sets is a family target, not an NR4A3 target, and that distinction is the "
                "whole of this repository's selectivity problem.",
        "enrichr": [("chea", "nr4a1")], "prefer": ["human"],
    },
    "nr4a2_targets_chea": {
        "read_id": "read_7_RET", "role": "paralogue_target_set",
        "what": "NR4A2 targets from ChEA — the third paralogue arm.",
        "enrichr": [("chea", "nr4a2")], "prefer": ["human"],
    },
    # --- read 5: HYPOXIA ------------------------------------------------------------------------
    "hypoxia_buffa": {
        "read_id": "read_5_HYPOXIA", "role": "hypoxia_metagene",
        "what": "The Buffa hypoxia metagene — Buffa et al., British Journal of Cancer 2010. ⚠ It "
                "is NOT certain this set is served under any of the names below; a failure to "
                "resolve is recorded as a failure to RETRIEVE, which says nothing about the "
                "signature's existence or validity.",
        "msigdb": ["BUFFA_HYPOXIA_METAGENE", "BUFFA_HYPOXIA_UP"],
    },
    "hypoxia_winter": {
        "read_id": "read_5_HYPOXIA", "role": "hypoxia_metagene",
        "what": "The Winter hypoxia metagene — Winter et al., Cancer Research 2007, derived in "
                "head-and-neck cancer and the most widely re-used of the microarray-era hypoxia "
                "metagenes.",
        "msigdb": ["WINTER_HYPOXIA_METAGENE", "WINTER_HYPOXIA_UP"],
    },
    "hypoxia_harris": {
        "read_id": "read_5_HYPOXIA", "role": "hypoxia_metagene",
        "what": "The Harris hypoxia set (MSigDB C2), a third independent hypoxia gene set.",
        "msigdb": ["HARRIS_HYPOXIA"],
    },
    "hypoxia_elvidge": {
        "read_id": "read_5_HYPOXIA", "role": "hypoxia_metagene",
        "what": "Elvidge et al. hypoxia-up set (MSigDB C2) — an in-vitro HIF-dependent set, so a "
                "useful contrast to the clinically-derived metagenes above.",
        "msigdb": ["ELVIDGE_HYPOXIA_UP", "ELVIDGE_HYPOXIA_BY_DMOG_UP"],
    },
    "hypoxia_gobp_response": {
        "read_id": "read_5_HYPOXIA", "role": "hypoxia_ontology_term_NOT_a_metagene",
        "what": "⚠ GO 'response to hypoxia' is an ONTOLOGY TERM, not a clinically-derived "
                "metagene, and is a different kind of object from Buffa/Winter. Scored separately "
                "and never pooled with them.",
        "enrichr": [("gobp", "responsetohypoxia"), ("gobp", "cellularresponsetohypoxia")],
    },
    "hypoxia_hallmark": {
        "read_id": "read_5_HYPOXIA", "role": "hypoxia_metagene",
        "what": "HALLMARK_HYPOXIA — the MSigDB hallmark set, which resolves reliably, included so "
                "read 5 cannot come back empty on a retrieval failure alone.",
        "enrichr": [("hallmark", "hypoxia")],
    },
    # --- read 2: CS/GAG cross-check -------------------------------------------------------------
    "cs_biosynthesis_reactome": {
        "read_id": "read_2_CS_GAG_PAPS", "role": "published_cross_check",
        "what": "Reactome chondroitin-sulfate biosynthesis — the published set the curated CS "
                "module is cross-checked against.",
        "enrichr": [("reactome", "chondroitinsulfatebiosynthesis"),
                    ("reactome", "chondroitinsulfatedermatansulfatemetabolism"),
                    ("reactome", "chondroitinsulfate")],
    },
    "cs_biosynthesis_gobp": {
        "read_id": "read_2_CS_GAG_PAPS", "role": "published_cross_check",
        "what": "GO biological process chondroitin-sulfate biosynthesis.",
        "enrichr": [("gobp", "chondroitinsulfatebiosyntheticprocess"),
                    ("gobp", "chondroitinsulfatemetabolicprocess"),
                    ("gobp", "glycosaminoglycanbiosyntheticprocess")],
    },
    # --- read 1: arginine cross-check -----------------------------------------------------------
    "arginine_biosynthesis_gobp": {
        "read_id": "read_1_ASS1", "role": "published_cross_check",
        "what": "GO biological process arginine biosynthesis — context for the single-gene ASS1 "
                "read, not a substitute for it.",
        "enrichr": [("gobp", "argininebiosyntheticprocess"), ("gobp", "argininemetabolicprocess"),
                    ("reactome", "ureacycle")],
    },
    # --- read 4: NE cross-check -----------------------------------------------------------------
    "neuroendocrine_gobp": {
        "read_id": "read_4_NE_STATE", "role": "published_cross_check",
        "what": "GO biological process neuroendocrine / neurosecretion terms — a published anchor "
                "for the five-gene NE read.",
        "enrichr": [("gobp", "neuroendocrinecelldifferentiation"),
                    ("gobp", "regulationofneurotransmittersecretion"),
                    ("gobp", "neuropeptidesignalingpathway")],
    },
}

# A panel score is emitted only when BOTH floors clear. Stated here, once, and applied everywhere.
MIN_GENES_FOR_A_PANEL_SCORE = 3
MIN_COVERAGE_FOR_A_PANEL_SCORE = 0.50
# A fetched multi-gene signature needs more than a hand-listed panel before a mean means anything.
MIN_GENES_FOR_A_SIGNATURE_SCORE = 8
MIN_COVERAGE_FOR_A_SIGNATURE_SCORE = 0.25
# Fewer than this in either arm and no contrast is computed at all.
MIN_GROUP_N_FOR_A_CONTRAST = 3


# ---------------------------------------------------------------------------------------------
# FETCH
# ---------------------------------------------------------------------------------------------
def _species_note(term):
    """⭐ DERIVED FROM THE MATCHED TERM, NEVER TYPED. Measured 2026-08-07 (run 31182233077): EVERY
    PPARG term in `ChEA_2022` and in `TF_Perturbations_Followed_by_Expression` is a MOUSE
    experiment, and `ENCODE_and_ChEA_Consensus_TFs_from_ChIP-X` carries no PPARG term at all. Only
    TRRUST's `PPARG human` is human-derived. That is a real limit on read 3 and it must travel with
    every number the set produces rather than sitting in a footnote — a mouse-derived target set
    applied to human tumour transcripts is an orthology assumption, not a measurement."""
    low = _norm(term)
    for sp in ("human", "mouse", "rat"):
        if sp in low:
            return {
                "species": sp,
                "caveat": (None if sp == "human" else
                           f"⚠ THE SOURCE EXPERIMENT IS {sp.upper()}, NOT HUMAN. The gene symbols "
                           f"are applied to human tumour transcripts by name, which is an "
                           f"ORTHOLOGY ASSUMPTION. It does not invalidate the read; it bounds it, "
                           f"and any sentence quoting this set must carry the bound."),
            }
    return {"species": "not stated in the term", "caveat": None}


def _load_enrichr_libraries(keys):
    """One request per library returns the whole library as TSV: `term\\t\\tGENE\\tGENE\\t...`."""
    libs, diag = {}, {}
    for key in keys:
        names, citation = ENRICHR_LIBRARIES[key]
        for name in names:
            try:
                text = _get_once(ENRICHR_LIB.format(name), timeout=240).decode("utf-8", "replace")
            except Exception as exc:  # noqa: BLE001
                diag.setdefault(key, []).append({"library": name, "error": str(exc)[:160]})
                continue
            terms = {}
            for ln in text.splitlines():
                parts = ln.rstrip("\n").split("\t")
                if len(parts) < 3:
                    continue
                genes = sorted({p.split(",")[0].strip().upper() for p in parts[2:] if p.strip()})
                if genes:
                    terms[parts[0].strip()] = genes
            if terms:
                libs[key] = {"library": name, "citation": citation, "terms": terms}
                diag.setdefault(key, []).append({"library": name, "n_terms": len(terms), "ok": True})
                break
            diag.setdefault(key, []).append({"library": name, "error": "no parsable terms"})
    return libs, diag


def fetch_signature_sets():
    """Resolve every fetched slot, recording EVERY attempt including the failures.

    ⚠ A slot that does not resolve stays unresolved. There is no silent substitution: a hypoxia
    metagene that could not be retrieved must read as *not retrieved*, because "we could not fetch
    Buffa" and "Buffa says EMC is not hypoxic" are different facts, and this repository has already
    been bitten by an instrument failure that rendered like a biological one."""
    keys = sorted({k for slot in SIGNATURE_SLOTS.values()
                   for k, _ in (slot.get("enrichr") or [])})
    libs, lib_diag = _load_enrichr_libraries(keys)
    out = {"_source": "Enrichr-served published collections and the MSigDB .jsp download path; "
                      "every set records its library, its VERBATIM matched term and its citation",
           "_enrichr_library_diagnostics": lib_diag,
           "_libraries_loaded": {k: {"library": v["library"], "n_terms": len(v["terms"]),
                                     "citation": v["citation"]} for k, v in libs.items()},
           "slots": {}}
    for slot, spec in SIGNATURE_SLOTS.items():
        rec = {"read_id": spec["read_id"], "role": spec["role"], "what": spec["what"],
               "candidates_tried": []}
        # MSigDB by exact name first where the slot names one: a named published set beats a
        # substring match against a general-purpose ontology.
        for name in (spec.get("msigdb") or []):
            try:
                txt = _get_once(MSIGDB_JSP.format(name), timeout=120).decode("utf-8", "replace")
            except Exception as exc:  # noqa: BLE001
                rec["candidates_tried"].append({"msigdb": name, "error": str(exc)[:140]})
                continue
            genes = sorted({ln.strip().upper() for ln in txt.splitlines()[2:]
                            if ln.strip() and re.match(r"^[A-Za-z0-9\-_.]+$", ln.strip())})
            if len(genes) >= 5:
                rec.update({"resolved_set": name, "matched_term_verbatim": name, "genes": genes,
                            "n_genes": len(genes),
                            "citation": "MSigDB — Liberzon et al., Cell Systems 2015; the set's own "
                                        "primary source is named in its MSigDB record",
                            "provenance": "MSigDB download_geneset.jsp, fetched at run time"})
                rec["candidates_tried"].append({"msigdb": name, "ok": True, "n_genes": len(genes)})
                break
            rec["candidates_tried"].append({"msigdb": name, "error": f"{len(genes)} usable genes"})
        if not rec.get("genes"):
            excl = spec.get("exclude") or []
            pref = spec.get("prefer") or []
            req_any = spec.get("require_any") or []
            req_suffix = spec.get("require_suffix")
            for libkey, needle in (spec.get("enrichr") or []):
                lib = libs.get(libkey)
                if not lib:
                    rec["candidates_tried"].append({"library_key": libkey, "needle": needle,
                                                    "error": "library not loaded"})
                    continue
                terms = [t for t in lib["terms"] if not any(x in _norm(t) for x in excl)]
                n_excluded = len(lib["terms"]) - len(terms)
                # ⛔ REQUIREMENTS ARE HARD, NOT PREFERENCES, and a slot that cannot meet them stays
                # UNRESOLVED. That is the whole point: `pparg_perturbation_KO_UP_CONTROL` exists to
                # be able to disagree, so silently falling back to whatever term sorts first would
                # hand read 3 a "control" that is not the control it names.
                if req_any:
                    terms = [t for t in terms if any(x in _norm(t) for x in req_any)]
                if req_suffix:
                    terms = [t for t in terms if _norm(t).endswith(req_suffix)]
                # prefix match first, substring second; the verbatim term and every alternative are
                # recorded either way so a reader can see exactly what was scored and what was not.
                hits = sorted(t for t in terms if _norm(t).startswith(needle))
                match_rule = "prefix"
                if not hits:
                    hits = sorted(t for t in terms if needle in _norm(t))
                    match_rule = "substring"
                if not hits:
                    rec["candidates_tried"].append(
                        {"library_key": libkey, "needle": needle, "error": "no term matched",
                         "n_terms_excluded": n_excluded, "require_any": req_any,
                         "require_suffix": req_suffix})
                    continue
                preferred = [t for t in hits if any(p in _norm(t) for p in pref)]
                hit = preferred[0] if preferred else hits[0]
                rec.update({"resolved_set": hit, "matched_term_verbatim": hit,
                            "all_matching_terms_verbatim": hits[:12],
                            "n_matching_terms": len(hits),
                            "species_of_the_source_experiment": _species_note(hit),
                            "selection_rule": (f"{match_rule} match on {needle!r}"
                                               + (f"; REQUIRED any of {req_any}" if req_any else "")
                                               + (f"; REQUIRED suffix {req_suffix!r}"
                                                  if req_suffix else "")
                                               + "; "
                                               + (f"preferred a term containing {pref}"
                                                  if preferred else
                                                  "no preference applied — first alphabetically")
                                               + (f"; {n_excluded} terms excluded by {excl}"
                                                  if excl else "")),
                            "library": lib["library"], "citation": lib["citation"],
                            "genes": lib["terms"][hit], "n_genes": len(lib["terms"][hit]),
                            "provenance": f"Enrichr library {lib['library']}, term matched "
                                          f"verbatim, fetched at run time"})
                rec["candidates_tried"].append({"library_key": libkey, "needle": needle, "ok": True,
                                                "n_terms_matched": len(hits),
                                                "n_terms_excluded": n_excluded})
                break
        if not rec.get("genes"):
            rec["unresolved"] = ("⚠ NOT RETRIEVED. This slot scored nothing. An absent set is an "
                                 "absent READING — it says nothing about the biology it names.")
        out["slots"][slot] = rec
    out["n_slots_resolved"] = sum(1 for r in out["slots"].values() if r.get("genes"))
    out["slots_unresolved"] = sorted(k for k, r in out["slots"].items() if not r.get("genes"))
    return out


def _wanted_genes(sig):
    want = set()
    for panel in PANELS.values():
        for genes in panel["groups"].values():
            want.update(genes)
    for rec in (sig.get("slots") or {}).values():
        want.update(rec.get("genes") or [])
    return want


def _read_target(target, want, sym_diag=None):
    """Fetch ONE named series-matrix file, map probes to symbols, and reduce to the per-sample
    values of every wanted gene, plus each gene's within-sample percentile against the whole array.

    ⚠ `sym_diag` — an already-computed `(sym, diag)` from `_gpl_symbols(platform)`, if the CALLER
    already had to build one. Added 2026-08-07 after the hypoxia-confound background fetch called
    `_gpl_symbols` itself (to learn the platform's symbol universe before it could sample from it)
    and then called this function, which called it AGAIN — two full platform-table downloads and
    parses per platform, on the one platform (GPL3290) whose bridge is the expensive half of the
    whole job. Default None preserves every existing call site exactly.
    ⛔ It is `(sym, diag)`, not `sym` alone, because the diagnostic is what makes a degraded
    annotation visible; accepting the map without the diagnostic would let a caller quietly supply a
    mapping whose provenance this function then could not report.

    ⭐ THE PERCENTILE IS THE FIELD A DEFAULT CANNOT FILL IN. A z-score against the array mean could
    be computed from summary statistics; a percentile requires the full distribution of that
    sample's probe values, so its presence is evidence the matrix was really parsed. It is also the
    only readout here that speaks to "is this gene on at all" rather than "is it different between
    groups" — which is exactly the question reads 1 and 6 ask."""
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
    sym, diag = sym_diag if sym_diag is not None else _gpl_symbols(plat)
    if sym_diag is not None:
        diag = dict(diag, _supplied_by_caller=(
            "this mapping was built by the CALLER and handed in, not fetched here — see "
            "`_read_target`'s `sym_diag`. It is the same `_gpl_symbols` output; what is saved is a "
            "second download and parse of the platform table, not a step of the science."))
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
    rec["value_kind"] = ("two-colour log-ratio vs a reference pool (RELATIVE — an absolute level "
                         "is NOT interpretable; only the between-group contrast is)"
                         if frac_neg > 0.15 else
                         "single-channel intensity (an absolute level is interpretable only "
                         "relative to this array's own probe distribution)")

    # per-sample background over ALL probes, and the sorted distribution for percentiles
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

    by_gene = {}
    for pid, row in zip(probes, values):
        g = sym.get(pid)
        if g and g in want:
            by_gene.setdefault(g, {"probe_ids": [], "rows": []})
            by_gene[g]["probe_ids"].append(pid)
            by_gene[g]["rows"].append(row[:n_s])
    genes = {}
    for g, d in by_gene.items():
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
        genes[g] = {"probe_ids": sorted(d["probe_ids"])[:12],
                    "n_probes_mapping": len(d["probe_ids"]),
                    "values": vals, "array_percentile": pct}
    rec["genes"] = genes
    rec["n_wanted_genes_measured"] = len(genes)
    rec["n_wanted_genes_requested"] = len(want)
    rec["_status"] = "read"
    print(f"  {gse}/{plat}: {n_s} samples, {len(probes)} probes, "
          f"{rec['n_probes_mapped_to_a_symbol']} mapped "
          f"({rec['measured_probe_mapping_rate']}), {len(genes)}/{len(want)} wanted genes measured",
          file=sys.stderr)
    return rec


def collect():
    print("fetching published gene sets...", file=sys.stderr)
    sig = fetch_signature_sets()
    want = _wanted_genes(sig)
    print(f"  {sig['n_slots_resolved']}/{len(SIGNATURE_SLOTS)} slots resolved; "
          f"{len(want)} distinct genes wanted", file=sys.stderr)
    inp = {"_generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "signature_sets": sig,
           "n_genes_wanted": len(want),
           "genes_wanted": sorted(want),
           "targets": {}}
    for t in TARGETS:
        print(f"reading {t['gse']} / {t['matrix_file']}", file=sys.stderr)
        inp["targets"][t["matrix_file"]] = _read_target(t, want)
    return inp


# ---------------------------------------------------------------------------------------------
# DERIVE
# ---------------------------------------------------------------------------------------------
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _group_indices(samples):
    """EMC vs comparator, with `unclassified` and `normal_or_reference` excluded from BOTH — the
    same rule part B uses, so the two artifacts remain comparable."""
    classes = [_classify_sample(s["annotation_verbatim"]) for s in samples]
    emc = [i for i, c in enumerate(classes) if c == "EMC"]
    comp = [i for i, c in enumerate(classes)
            if c not in ("EMC", "unclassified", "normal_or_reference")]
    return classes, emc, comp


def _zrow(tgt, gene):
    """Within-sample standardisation: (gene value − the sample's mean over ALL probes) / that
    sample's SD over all probes. Valid on two-colour log-ratios, and immovable by a sample's
    overall hybridisation intensity — the same reduction part B uses."""
    n_s = tgt["n_samples"]
    bg = tgt["background_per_sample"]
    v = tgt["genes"][gene]["values"]
    return [None if (v[i] is None or not bg[i]) else
            (v[i] - bg[i]["mean"]) / max(1e-9, bg[i]["sd"]) for i in range(n_s)]


def _mapping_rate_reading(tgt):
    """Two DIFFERENT mapping rates, kept apart, and only one of them is comparable to the prior.

    ⛔ THE FIRST VERSION OF THIS FUNCTION COMPARED THE WRONG TWO NUMBERS AND MANUFACTURED A DRIFT
    WARNING ON A RUN WITH NO DRIFT (measured 2026-08-07, run 31182233077). The prior quoted in
    `TARGETS` comes from `emc-atr-vulnerability.json`, and that field is built from
    `probe_symbol_mapping.accession_resolution_rate` — the fraction of distinct **GenBank
    accessions** that resolved to a symbol. This module separately measures the fraction of
    **probes on the matrix** that carry a symbol. Different numerators, different denominators,
    different questions. Compared against each other they printed:
        GPL6244  probe 0.7109 vs prior 0.932  -> "MOVED by 22 points"
        GPL3290  probe 0.6326 vs prior 0.582  -> "MOVED by 5 points"
    while the LIKE-FOR-LIKE figures from the same run were 0.983 (better than the 0.932 prior,
    because the UniGene archive resolved 51,071 accessions) and **0.582 — identical to the prior to
    three decimals.** A guard that cries drift on a clean run is worse than no guard: it trains the
    next reader to skip the line that would have caught a real one.

    So both rates are reported, each named for what it measures, and the drift comparison is made
    ONLY against the accession rate, which is the quantity the prior actually is."""
    diag = tgt.get("probe_symbol_mapping") or {}
    acc = diag.get("accession_resolution_rate")
    probe = tgt.get("measured_probe_mapping_rate")
    out = {
        "probe_level_rate": probe,
        "_probe_level_rate_means": (
            "fraction of the probes ON THIS MATRIX that carry a gene symbol. This is the number "
            "that governs whether a given gene is readable, and it is NOT the figure the prior "
            "records — see below."),
        "accession_resolution_rate": acc,
        "_accession_resolution_rate_means": (
            "fraction of the platform's distinct GenBank accessions that resolved to a symbol. "
            "This IS the quantity `emc-atr-vulnerability.json` records, so it is the only one "
            "comparable to the prior."),
        "prior_accession_resolution_rate": tgt["prior_probe_mapping_rate"],
        "prior_source": tgt["prior_source"],
        "resolution_sources": {k: diag.get(k) for k in (
            "n_distinct_accessions", "n_accessions_resolved_by_curated_dictionary",
            "n_accessions_resolved_by_unigene_archive", "n_accessions_newly_queried",
            "n_accessions_resolved_total", "ncbi_global_budget_exhausted") if k in diag},
    }
    if acc is None:
        out["reading"] = ("⚠ NO ACCESSION-RESOLUTION RATE IN THIS RUN'S DIAGNOSTIC, so the "
                          "like-for-like comparison against the prior COULD NOT BE MADE. That is "
                          "an absent reading, not agreement.")
        return out
    delta = acc - tgt["prior_probe_mapping_rate"]
    out["abs_difference_vs_prior"] = round(abs(delta), 4)
    out["direction_vs_prior"] = ("more accessions resolved than the prior run" if delta > 0 else
                                 "fewer accessions resolved than the prior run" if delta < 0 else
                                 "identical to the prior run")
    # ⚠ THE DIRECTION IS PART OF THE VERDICT, NOT DECORATION. A rate that moved UP and a rate that
    # moved DOWN send a reader to opposite places — one to "what did we gain", one to "what broke" —
    # and a single undirected "MOVED" sentence sent the first reader hunting for a failed fetch that
    # had not happened. Both still flag: an annotation pipeline that changed is worth noticing
    # either way, because the gene list it produces is what every read below rests on.
    if abs(delta) <= 0.05:
        out["reading"] = "consistent with the prior characterisation"
    elif delta > 0:
        out["reading"] = ("⚠ MOVED UP by more than 5 points against the prior, COMPARED LIKE FOR "
                          "LIKE — MORE accessions resolved this run than last. Not a failure, but "
                          "not nothing: a wider bridge changes WHICH genes are readable, so a gene "
                          "readable here and unreadable in the prior run is explained by this line "
                          "and not by the biology.")
    else:
        out["reading"] = ("⚠ MOVED DOWN by more than 5 points against the prior, COMPARED LIKE FOR "
                          "LIKE — FEWER accessions resolved this run. A diagnosable event: a "
                          "changed platform annotation, an exhausted NCBI budget "
                          "(`ncbi_global_budget_exhausted` above), or a failed UniGene fetch. Read "
                          "it BEFORE any number below it, because a gene can be unreadable here "
                          "purely for this reason.")
    return out


def _gene_read(gene, tgt, classes, emc, comp):
    """One gene, one platform. ⛔ The `readable` verdict is the load-bearing field: a gene with no
    probe is NOT READABLE, which is a statement about the platform, never about the gene."""
    plat = tgt.get("platform")
    rate = tgt.get("measured_probe_mapping_rate")
    g = (tgt.get("genes") or {}).get(gene)
    if not g:
        return {
            "readable": False,
            "platform": plat,
            "n_probes_mapping": 0,
            "why_not_readable": (
                f"No probe on {plat} maps to the symbol {gene}. The platform's probe->symbol "
                f"mapping covers {tgt.get('n_probes_mapped_to_a_symbol')} of "
                f"{tgt.get('n_probes')} probes (rate {rate}), so a symbol can be missing because "
                f"the array carries no probe for it OR because that probe's identifier did not "
                f"resolve to a symbol."),
            "verdict": (f"⛔ NOT READABLE on {plat} — the read could not be taken. This says "
                        f"NOTHING about whether {gene} is expressed in EMC."),
        }
    n_s = tgt["n_samples"]
    z = [None if x is None else round(x, 4) for x in _zrow(tgt, gene)]
    vals, pct = g["values"], g["array_percentile"]
    samples = tgt["samples"]
    per_sample = [{"gsm": samples[i]["gsm"], "class": classes[i], "value": vals[i],
                   "z_vs_array": z[i], "array_percentile": pct[i]}
                  for i in range(n_s) if i in emc or i in comp]
    a = [z[i] for i in emc if z[i] is not None]
    b = [z[i] for i in comp if z[i] is not None]
    emc_pct = [pct[i] for i in emc if pct[i] is not None]
    comp_pct = [pct[i] for i in comp if pct[i] is not None]
    out = {
        "readable": True,
        "platform": plat,
        "n_probes_mapping": g["n_probes_mapping"],
        "probe_ids": g["probe_ids"],
        "value_kind": tgt["value_kind"],
        "n_EMC_with_a_value": len(a),
        "n_comparator_with_a_value": len(b),
        "EMC": {"mean_z": round(_mean(a), 4) if a else None,
                "mean_array_percentile": round(_mean(emc_pct), 4) if emc_pct else None},
        "comparator": {"mean_z": round(_mean(b), 4) if b else None,
                       "mean_array_percentile": round(_mean(comp_pct), 4) if comp_pct else None},
        "per_sample": per_sample,
    }
    if len(a) >= MIN_GROUP_N_FOR_A_CONTRAST and len(b) >= MIN_GROUP_N_FOR_A_CONTRAST:
        out["welch_EMC_vs_comparator"] = _welch(a, b)
        out["_sign"] = "delta_a_minus_b > 0 means HIGHER in EMC than in the comparator sarcomas."
    else:
        out["welch_EMC_vs_comparator"] = None
        out["_underpowered"] = (f"n_EMC={len(a)}, n_comparator={len(b)}; the floor is "
                                f"{MIN_GROUP_N_FOR_A_CONTRAST} per group. No contrast computed.")
    out["verdict"] = _gene_verdict(r=out)
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
    direction = "HIGHER in EMC" if d > 0 else "LOWER in EMC"
    strength = ("|t| >= 3" if abs(t) >= 3 else "|t| 2-3" if abs(t) >= 2 else "|t| < 2 — flat")
    return (f"READABLE on {r['platform']} ({r['n_probes_mapping']} probe(s)); {present}. "
            f"{direction} by {abs(d)} SD units of the array ({strength}, t={t}, df={w['df']}, "
            f"n_EMC={r['n_EMC_with_a_value']}, n_comparator={r['n_comparator_with_a_value']}). "
            f"⚠ Uncorrected for multiple testing.")


def _score_gene_list(genes, tgt, emc, comp, min_genes, min_cov, what):
    """Mean within-sample z over the READABLE members of a gene list, then EMC vs comparator.

    ⛔ COVERAGE IS REPORTED WHETHER OR NOT A SCORE IS EMITTED, and a list below the floor emits
    UNDERPOWERED rather than a number — a signature averaged over two surviving probes renders
    exactly like one averaged over forty, which is the failure mode this whole module is built
    against."""
    have = tgt.get("genes") or {}
    readable = [g for g in genes if g in have]
    cov = round(len(readable) / len(genes), 3) if genes else None
    base = {"n_genes_requested": len(genes), "n_genes_readable": len(readable), "coverage": cov,
            "genes_readable": sorted(readable)[:250],
            "genes_not_readable": sorted(set(genes) - set(readable))[:250],
            "_not_readable_means": "no probe on this platform maps to the symbol. It is NOT a "
                                   "statement that the gene is unexpressed."}
    if len(readable) < min_genes or (cov or 0) < min_cov:
        base["score"] = None
        base["verdict"] = (f"⛔ UNDERPOWERED — {len(readable)}/{len(genes)} genes readable on "
                           f"{tgt.get('platform')} (coverage {cov}); the floor for {what} is "
                           f"{min_genes} genes and {min_cov} coverage. NO SCORE EMITTED. This is "
                           f"an instrument limit, not a reading of the biology.")
        return base
    rows = [_zrow(tgt, g) for g in readable]
    n_s = tgt["n_samples"]
    per_sample = [_mean([r[i] for r in rows]) for i in range(n_s)]
    a = [per_sample[i] for i in emc if per_sample[i] is not None]
    b = [per_sample[i] for i in comp if per_sample[i] is not None]
    base["EMC_mean_score"] = round(_mean(a), 4) if a else None
    base["comparator_mean_score"] = round(_mean(b), 4) if b else None
    if len(a) >= MIN_GROUP_N_FOR_A_CONTRAST and len(b) >= MIN_GROUP_N_FOR_A_CONTRAST:
        w = _welch(a, b)
        base["score"] = w
        base["verdict"] = (f"{'HIGHER' if w['delta_a_minus_b'] > 0 else 'LOWER'} in EMC by "
                           f"{abs(w['delta_a_minus_b'])} SD units (t={w['t']}, df={w['df']}, "
                           f"n_EMC={len(a)}, n_comparator={len(b)}, {len(readable)}/{len(genes)} "
                           f"genes readable). ⚠ Uncorrected for multiple testing.")
    else:
        base["score"] = None
        base["verdict"] = (f"⛔ UNDERPOWERED — n_EMC={len(a)}, n_comparator={len(b)}; the floor is "
                           f"{MIN_GROUP_N_FOR_A_CONTRAST} per group.")
    return base


def derive(inp):
    sig = inp.get("signature_sets") or {}
    res = {
        "_what": "Six targeted expression reads in the two readable EMC series — the single CI "
                 "dispatch that section 4 of emc-unexplored-treatment-lanes.md turns on.",
        "_framing": FRAMING,
        "_execution_model": "$0. Public GEO series matrices on a GitHub-hosted CPU runner. No GPU, "
                            "no rental, no wet lab.",
        "_the_rule_that_governs_every_row": (
            "AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4). A gene with no probe "
            "mapping to it is `readable: false` and its verdict says the READ could not be taken. "
            "Nowhere in this artifact does a missing probe become a statement that a gene is not "
            "expressed. Correspondingly, a POPULATED field is not a MEASURED one: every readable "
            "gene carries `n_probes_mapping` and its actual probe IDs, and every value carries an "
            "`array_percentile` that can only come from the full parsed distribution of that "
            "sample's probes."),
        "_language_discipline": (
            "⛔ NOTHING HERE IS AN EFFICACY, SELECTIVITY, SAFETY, THERAPEUTIC-WINDOW OR CLINICAL-"
            "READINESS CLAIM for any agent named in this file. Every read is an expression reading "
            "in n = 6 and n = 10 archival tumours on two array platforms."),
        "_consumers": {
            "_what_this_is": "Other lanes depend on specific reads. Their stable addresses:",
            "read_2_CS_GAG_PAPS": "reads.read_2_CS_GAG_PAPS  (detail: panels.cs_gag_paps)",
            "read_3_PPARG_ACTIVITY": "reads.read_3_PPARG_ACTIVITY  (detail: "
                                     "panels.pparg_target_activity, signature_scores.pparg_*)",
            "read_6_NR2F1": "reads.read_6_NR2F1  (detail: gene_reads.NR2F1)",
            "read_7_RET": "reads.read_7_RET  (detail: gene_reads.RET). Consumed by the RET "
                          "cistrome lane — emc_ret_cistrome.py / emc-ret-cistrome.json — which "
                          "asks the OCCUPANCY half of the same question. ⛔ Abundance is not "
                          "activation; `emc-ret-lane.md` §3 owns that finding.",
            "every_gene": "gene_reads.<SYMBOL>.<matrix_file> — carries `readable`, "
                          "`n_probes_mapping`, `probe_ids`, per-sample values, `array_percentile`, "
                          "the Welch contrast and a verdict sentence.",
            "how_to_tell_absent_from_zero": "read `readable`. NEVER infer absence from a missing "
                                            "key or a null score.",
            "read_the_control_first": "reads.control — if the instrument did not reproduce ENO3, "
                                      "nothing below it should be quoted.",
        },
        "generated_utc": inp.get("_generated_utc"),
        "signature_sets": {k: {kk: vv for kk, vv in v.items() if kk != "genes"}
                           for k, v in (sig.get("slots") or {}).items()},
        "signature_set_fetch_diagnostics": {
            "_enrichr_library_diagnostics": sig.get("_enrichr_library_diagnostics"),
            "_libraries_loaded": sig.get("_libraries_loaded"),
            "n_slots_resolved": sig.get("n_slots_resolved"),
            "slots_unresolved": sig.get("slots_unresolved"),
        },
        "platforms": {},
        "gene_reads": {},
        "panels": {},
        "signature_scores": {},
        "reads": {},
    }

    live = {}
    for mf, tgt in (inp.get("targets") or {}).items():
        if tgt.get("_status") != "read":
            res["platforms"][mf] = {"_status": tgt.get("_status"), "series": tgt.get("gse"),
                                    "verdict": "⛔ THIS PLATFORM WAS NOT READ. Every gene is "
                                               "unread on it — an absent reading, not an absence."}
            continue
        classes, emc, comp = _group_indices(tgt["samples"])
        live[mf] = (tgt, classes, emc, comp)
        counts = {}
        for c in classes:
            counts[c] = counts.get(c, 0) + 1
        drift = _mapping_rate_reading(tgt)
        res["platforms"][mf] = {
            "_status": "read", "series": tgt["gse"], "platform": tgt["platform"],
            "platform_matches_expected": tgt.get("platform_matches_expected"),
            "why_this_platform": tgt["why"],
            "n_samples": tgt["n_samples"], "n_probes": tgt["n_probes"],
            "n_probes_mapped_to_a_symbol": tgt["n_probes_mapped_to_a_symbol"],
            "probe_mapping_rate": drift,
            "probe_mapping_diagnostic": tgt.get("probe_symbol_mapping"),
            "value_kind": tgt["value_kind"],
            "class_counts": dict(sorted(counts.items())),
            "n_EMC": len(emc), "n_comparator": len(comp),
            "EMC_gsms": [tgt["samples"][i]["gsm"] for i in emc],
            "comparator_gsms": [tgt["samples"][i]["gsm"] for i in comp],
            "sample_annotations_verbatim": [
                {"gsm": s["gsm"], "class": classes[i], "annotation": s["annotation_verbatim"][:220]}
                for i, s in enumerate(tgt["samples"])],
            "n_wanted_genes_measured": tgt["n_wanted_genes_measured"],
            "n_wanted_genes_requested": tgt["n_wanted_genes_requested"],
        }

    # --- per gene, per platform ------------------------------------------------------------------
    all_genes = sorted({g for p in PANELS.values() for gs in p["groups"].values() for g in gs})
    for gene in all_genes:
        res["gene_reads"][gene] = {mf: _gene_read(gene, tgt, classes, emc, comp)
                                   for mf, (tgt, classes, emc, comp) in live.items()}

    # --- per panel, per group, per platform ------------------------------------------------------
    for pname, panel in PANELS.items():
        entry = {k: v for k, v in panel.items() if k != "groups"}
        entry["groups"] = {}
        for gname, genes in panel["groups"].items():
            entry["groups"][gname] = {
                "genes_requested": genes,
                "per_platform": {mf: _score_gene_list(genes, tgt, emc, comp,
                                                      MIN_GENES_FOR_A_PANEL_SCORE,
                                                      MIN_COVERAGE_FOR_A_PANEL_SCORE,
                                                      "a curated panel")
                                 for mf, (tgt, classes, emc, comp) in live.items()},
            }
        res["panels"][pname] = entry

    # --- fetched signature sets, scored ----------------------------------------------------------
    for slot, rec in (sig.get("slots") or {}).items():
        genes = rec.get("genes")
        if not genes:
            res["signature_scores"][slot] = {
                "read_id": rec["read_id"], "role": rec["role"], "what": rec["what"],
                "resolved": False, "candidates_tried": rec.get("candidates_tried"),
                "verdict": "⛔ SET NOT RETRIEVED — scored nothing. An absent set is an absent "
                           "reading; it says nothing about the biology it names."}
            continue
        res["signature_scores"][slot] = {
            "read_id": rec["read_id"], "role": rec["role"], "resolved": True,
            "what": rec["what"], "resolved_set": rec.get("resolved_set"),
            "matched_term_verbatim": rec.get("matched_term_verbatim"),
            "all_matching_terms_verbatim": rec.get("all_matching_terms_verbatim"),
            "selection_rule": rec.get("selection_rule"),
            "species_of_the_source_experiment": rec.get("species_of_the_source_experiment"),
            "library": rec.get("library"), "citation": rec.get("citation"),
            "provenance": rec.get("provenance"), "n_genes": rec.get("n_genes"),
            "per_platform": {mf: _score_gene_list(genes, tgt, emc, comp,
                                                  MIN_GENES_FOR_A_SIGNATURE_SCORE,
                                                  MIN_COVERAGE_FOR_A_SIGNATURE_SCORE,
                                                  "a published multi-gene signature")
                             for mf, (tgt, classes, emc, comp) in live.items()},
        }

    res["target_set_membership"] = _target_set_membership(sig)
    res["reads"] = _assemble_reads(res)
    res["_what_this_cannot_conclude"] = [
        "That any agent named in this file works, is safe, is selective, or has a therapeutic "
        "window in EMC. No agent has been given to an EMC patient on the basis of anything here.",
        "That a gene with no probe is unexpressed. It was not read.",
        "That a transcript reading is a protein reading. Every therapeutic address named here — "
        "CSPG4, DLL3, the oncofetal CS epitope, NR2F1 — is a protein or a glycan question.",
        "That n = 6 and n = 10 archival tumours on two decade-old array platforms, uncorrected "
        "for multiple testing, settle anything at the level of a population.",
        "Anything about a patient.",
    ]
    res["_limits"] = [
        "TWO PLATFORMS, DIFFERENT PHYSICS. GPL6244 is single-channel; GPL3290 is two-colour "
        "log-ratio against a reference pool, so on GPL3290 an ABSOLUTE level means 'relative to "
        "the pool' and only the EMC-vs-comparator contrast is interpretable. An `array_percentile` "
        "on GPL3290 is a percentile of log-RATIOS, which is not the same statement as 'expressed'.",
        "DIFFERENT COMPARATOR ARMS. GSE24369's comparators are LGFMS / desmoid / fibrosarcoma; "
        "GSE4303-GPL3290's are DFSP and GIST. A gene can move in one and not the other because "
        "the comparator changed, not because EMC did. Concordance across the two is the argument; "
        "a single-platform result is a lead.",
        "BULK ARCHIVAL TISSUE. EMC is matrix-dominated, so tumour-cell content varies and every "
        "reading is a mixture. Stromal and adipose contamination hits the CS/GAG and PPARγ reads "
        "hardest, and neither can be deconvolved here.",
        "NO MULTIPLE-TESTING CORRECTION anywhere in this artifact, by design: the reads were "
        "specified in advance and are reported with their t and df so a reader can apply their "
        "own. A |t| threshold in a verdict sentence is a readability aid, not a test.",
        "PROBE-LEVEL AMBIGUITY. A symbol with several probes is collapsed by mean, the same "
        "reduction part B uses. Probe-level disagreement is not surfaced.",
        "THE ACCESSION BRIDGE IS THE WEAK LINK ON GPL3290. Its probes carry EST accessions only, "
        "so a gene can be unreadable there purely because its accession did not resolve. That is "
        "why the measured mapping rate is reported against the prior on every run.",
        "SAMPLE CLASSIFICATION IS STRING MATCHING on the verbatim GEO annotation, reused from "
        "`emc_atr_vulnerability._classify_sample`. Every annotation is reproduced in "
        "`platforms.<file>.sample_annotations_verbatim` so a mis-bucketed sample is auditable "
        "offline rather than costing another run.",
    ]
    return res


def _readability_of(res, genes):
    out = {}
    for g in genes:
        rec = res["gene_reads"].get(g) or {}
        out[g] = {mf: {"readable": r.get("readable"),
                       "n_probes_mapping": r.get("n_probes_mapping"),
                       "welch_EMC_vs_comparator": r.get("welch_EMC_vs_comparator"),
                       "EMC_mean_array_percentile": (r.get("EMC") or {}).get(
                           "mean_array_percentile"),
                       "verdict": r.get("verdict")} for mf, r in rec.items()}
    return out


def _slot_summary(res, read_id):
    return {k: {"resolved": v.get("resolved"), "role": v.get("role"),
                "resolved_set": v.get("resolved_set"),
                "matched_term_verbatim": v.get("matched_term_verbatim"),
                "selection_rule": v.get("selection_rule"),
                "species_of_the_source_experiment": v.get("species_of_the_source_experiment"),
                "citation": v.get("citation"), "n_genes": v.get("n_genes"),
                "per_platform": {mf: {"coverage": p.get("coverage"),
                                      "n_genes_readable": p.get("n_genes_readable"),
                                      "n_genes_requested": p.get("n_genes_requested"),
                                      "EMC_mean_score": p.get("EMC_mean_score"),
                                      "comparator_mean_score": p.get("comparator_mean_score"),
                                      "score": p.get("score"), "verdict": p.get("verdict")}
                                 for mf, p in (v.get("per_platform") or {}).items()},
                "verdict": v.get("verdict")}
            for k, v in res["signature_scores"].items() if v.get("read_id") == read_id}


def _panel_summary(res, pname):
    p = res["panels"].get(pname) or {}
    keep = ("n_genes_requested", "n_genes_readable", "coverage", "genes_not_readable",
            "EMC_mean_score", "comparator_mean_score", "score", "verdict")
    return {"question": p.get("question"), "provenance": p.get("provenance"),
            "groups": {g: {"genes_requested": d["genes_requested"],
                           "per_platform": {mf: {k: v for k, v in s.items() if k in keep}
                                            for mf, s in d["per_platform"].items()}}
                       for g, d in (p.get("groups") or {}).items()}}


# The genes whose membership in an NR4A target set is a RESULT rather than context.
MEMBERSHIP_PROBES = ["RET", "ENO3", "SEMA3C", "PPARG", "GDNF", "GFRA1", "VEGFA", "KDR"]


def _target_set_membership(sig):
    """Is *RET* a member of each retrieved NR4A target-gene set?

    ⭐ A DIFFERENT INSTRUMENT CLASS FROM THE CISTROME MODULE, ON PURPOSE. `emc_ret_cistrome.py`
    asks whether NR4A3 OCCUPIES the RET locus in somebody's ChIP-seq. This asks whether RET is in
    a published NR4A3 target set — and for the perturbation arms, whether RET MOVES when NR4A3 is
    perturbed, which occupancy alone cannot show and which is the readout the ENO3 precedent
    needed luciferase for (PMID 26310886). Two instrument classes agreeing is an argument.

    ⛔ MEMBERSHIP IS A CITATION, NOT A MEASUREMENT MADE HERE. Every row carries the VERBATIM
    matched term (which, for ChEA, embeds the source experiment's own PMID) so a reader can go to
    the experiment rather than to this file. And a set that did not resolve is `resolved: false`
    with `member: null` — NEVER `member: false`, because "the set was not retrieved" and "RET is
    not in the set" are different facts and this repository has been burned by exactly that
    conflation (CLAUDE.md §4).
    """
    out = {
        "_what": "Membership of RET (and of the lane's controls) in every retrieved NR4A "
                 "target-gene set, by paralogue and by instrument class.",
        "⛔ _member_null_is_not_member_false": (
            "`member: null` means the SET WAS NOT RETRIEVED. It is an absent reading and says "
            "nothing about whether the gene is a target."),
        "⚠ _what_membership_is_not": (
            "an NR4A3 target set is somebody else's experiment in somebody else's cell type, "
            "almost always wild-type NR4A3 rather than EWSR1::NR4A3. Membership is a PRIOR of "
            "the same kind a ChIP peak is, and non-membership is weak — most sets are small, "
            "thresholded and cell-type specific."),
        "per_slot": {}, "by_gene": {},
    }
    slots = (sig or {}).get("slots") or {}
    for slot, rec in slots.items():
        if rec.get("read_id") != "read_7_RET":
            continue
        genes = rec.get("genes")
        row = {"role": rec.get("role"), "what": rec.get("what"),
               "resolved": bool(genes),
               "matched_term_verbatim": rec.get("matched_term_verbatim"),
               "library": rec.get("library"), "citation": rec.get("citation"),
               "species_of_the_source_experiment": rec.get("species_of_the_source_experiment"),
               "n_genes": rec.get("n_genes")}
        upper = {str(g).upper() for g in (genes or [])}
        row["membership"] = {g: (g in upper if genes else None) for g in MEMBERSHIP_PROBES}
        out["per_slot"][slot] = row
    for g in MEMBERSHIP_PROBES:
        hits = sorted(s for s, r in out["per_slot"].items()
                      if r["resolved"] and r["membership"].get(g))
        unresolved = sorted(s for s, r in out["per_slot"].items() if not r["resolved"])
        out["by_gene"][g] = {
            "in_sets": hits, "n_sets_containing_it": len(hits),
            "n_sets_resolved": sum(1 for r in out["per_slot"].values() if r["resolved"]),
            "sets_not_retrieved": unresolved,
            "verdict": (f"present in {len(hits)} retrieved NR4A target set(s): "
                        f"{', '.join(hits)}" if hits else
                        "not present in any RETRIEVED NR4A target set. ⚠ ABSENT from those sets "
                        "is not absence of regulation — these sets are thresholded, cell-type "
                        "specific, and mostly wild-type NR4A3 rather than the fusion."),
        }
    return out


def _read_entry(res, read_id, panel_key, extra=None):
    panel = PANELS[panel_key]
    entry = {"read_id": read_id,
             "question": panel["question"],
             "platforms_read": [mf for mf, p in res["platforms"].items()
                                if p.get("_status") == "read"],
             "provenance": panel["provenance"],
             "direction_that_supports_the_lane": panel.get("direction_that_supports_the_lane"),
             "what_it_cannot_settle": panel["what_it_cannot_settle"],
             "panels": {panel_key: _panel_summary(res, panel_key)},
             "signature_slots": _slot_summary(res, read_id)}
    entry.update(extra or {})
    return entry


def _assemble_reads(res):
    R = {}
    R["control"] = {
        "read_id": "control",
        "question": PANELS["instrument_controls"]["question"],
        "expected": PANELS["instrument_controls"]["expected"],
        "gene_readability": _readability_of(res, ["NR4A3", "ENO3", "MKI67", "EWSR1", "TAF15",
                                                  "FUS"]),
        "panel": _panel_summary(res, "instrument_controls"),
        "how_to_read_this_first": (
            "⛔ READ THIS BEFORE ANY OF THE SIX. If ENO3 is not clearly higher in EMC on both "
            "platforms, the instrument did not reproduce a reading that is already committed in "
            "emc-atr-vulnerability.json from these same two matrices, and every read below it is "
            "suspect. If NR4A3 is unreadable, that is a probe-placement fact about these arrays, "
            "not a biological one — say so, and do not treat it as a failed control."),
    }
    R["read_1_ASS1"] = _read_entry(
        res, "read_1_ASS1", "arginine_auxotrophy",
        {"the_binary": res["gene_reads"].get("ASS1") or {}})
    R["read_2_CS_GAG_PAPS"] = _read_entry(
        res, "read_2_CS_GAG_PAPS", "cs_gag_paps",
        {"enzyme_annotations": PANELS["cs_gag_paps"]["enzyme_annotations"],
         "CSPG4": res["gene_reads"].get("CSPG4") or {},
         "four_O_vs_six_O": _readability_of(res, ["CHST11", "CHST12", "CHST13", "CHST14",
                                                  "CHST3", "CHST7", "CHST15", "UST"])})
    R["read_3_PPARG_ACTIVITY"] = _read_entry(
        res, "read_3_PPARG_ACTIVITY", "pparg_target_activity",
        {"how_to_read_the_arms": (
            "⛔ CHECK THE CONTROL ARM BEFORE QUOTING ANYTHING. "
            "`pparg_perturbation_KO_DOWN` (PPARγ-dependent genes) and `pparg_perturbation_OE_UP` "
            "are expected to move TOGETHER if the receptor is transcriptionally engaged. "
            "`pparg_perturbation_KO_UP_CONTROL` is expected NOT to. If all three move the same "
            "way, the contrast is measuring something the sets share rather than PPARγ output, "
            "and read 3 must not be quoted."),
         "species_of_each_set": {
             k: v.get("species_of_the_source_experiment")
             for k, v in res["signature_scores"].items()
             if v.get("read_id") == "read_3_PPARG_ACTIVITY"},
         "abundance_is_not_the_read": PANELS["pparg_target_activity"]["abundance_is_not_the_read"],
         "direction_reading_rules": PANELS["pparg_target_activity"]["direction_reading_rules"],
         "abundance_context_only": {
             "_warning": "CONTEXT, NOT A NEW MEASUREMENT. PPARG abundance in EMC has one home: "
                         "research/manuscripts/pparg-direction-emc.md §6.",
             "is_the_read": False,
             "genes": _readability_of(res, ["PPARG", "PPARGC1A", "RXRA"])}})
    R["read_4_NE_STATE"] = _read_entry(
        res, "read_4_NE_STATE", "neuroendocrine_state",
        {"the_five_genes": _readability_of(res, ["DLL3", "ASCL1", "NEUROD1", "INSM1", "HES1"])})
    R["read_5_HYPOXIA"] = _read_entry(res, "read_5_HYPOXIA", "hypoxia")
    R["read_6_NR2F1"] = _read_entry(
        res, "read_6_NR2F1", "nr2f1_dormancy",
        {"the_precondition": res["gene_reads"].get("NR2F1") or {},
         "paralogues": _readability_of(res, ["NR2F2", "NR2F6"])})
    R["read_7_RET"] = _read_entry(
        res, "read_7_RET", "ret_axis",
        {"the_receptor": res["gene_reads"].get("RET") or {},
         "the_ligand_module": _readability_of(res, ["GDNF", "NRTN", "ARTN", "PSPN"]),
         "the_co_receptors": _readability_of(res, ["GFRA1", "GFRA2", "GFRA3", "GFRA4"]),
         "the_alternative_hypothesis": _readability_of(res, ["VEGFA", "KDR", "PDGFRB", "KIT"]),
         "published_nr4a3_targets": _readability_of(res, ["SEMA3C", "ENO3"]),
         "is_RET_in_a_published_NR4A_target_set": (res.get("target_set_membership") or {})
         .get("by_gene", {}).get("RET"),
         "target_set_membership_all_genes": res.get("target_set_membership"),
         "⭐ how_to_read_the_two_instruments_together": (
             "OCCUPANCY (emc-ret-cistrome.json) and MEMBERSHIP/PERTURBATION (here) are "
             "independent instrument classes and the interesting cases are the disagreements. "
             "Both positive is the strongest reading available at $0. Occupancy without "
             "perturbation response is a bound site with no demonstrated output — which is "
             "exactly why the ENO3 precedent needed luciferase on top of ChIP (PMID 26310886). "
             "Perturbation response without occupancy is consistent with an indirect effect. "
             "⛔ Neither, in any combination, is evidence about EWSR1::NR4A3 in an EMC tumour."),
         "⛔ what_a_high_RET_reading_is_not": (
             "it is not activation, and the distinction is the entire content of the "
             "methodological guard this lane carries. PMID 34885165 measured MET protein in 82 % "
             "of clear cell sarcomas and phospho-MET in 4 % of the same blinded 32-case array; "
             "abundance and activation came apart by a factor of twenty in the disease this lane "
             "uses as its comparator. RET in EMC has never been measured that way "
             "(`emc-ret-lane.md` §3)."),
         "⚠ what_a_high_RET_reading_also_cannot_separate": (
             "tumour RET from stromal or entrapped peripheral-nerve RET. EMC is hypocellular and "
             "matrix-rich (PMC6766969), RET is a nerve-lineage receptor, and these are BULK "
             "arrays — so cellular origin is unresolvable here by construction.")})

    for k, v in R.items():
        if k == "control":
            continue
        v["readability_verdict"] = _read_readability_verdict(v)
    return R


def _read_readability_verdict(entry):
    """One record per read saying whether it was TAKEN, PARTIALLY TAKEN or NOT TAKEN, and on which
    platforms — so a consumer never has to infer readability from the presence of a number."""
    plats = entry["platforms_read"]
    scored, unscored = [], []
    for pname, p in (entry.get("panels") or {}).items():
        for gname, g in (p.get("groups") or {}).items():
            for mf, s in (g.get("per_platform") or {}).items():
                (scored if s.get("score") else unscored).append(f"{pname}.{gname}@{mf}")
    for slot, s in (entry.get("signature_slots") or {}).items():
        if not s.get("resolved"):
            unscored.append(f"{slot}: SET NOT RETRIEVED")
            continue
        for mf, p in (s.get("per_platform") or {}).items():
            (scored if p.get("score") else unscored).append(f"{slot}@{mf}")
    if not plats or not scored:
        state = "NOT TAKEN"
    elif unscored:
        state = "PARTIALLY TAKEN"
    else:
        state = "TAKEN"
    return {"state": state, "platforms_read": plats,
            "n_scored_units": len(scored), "n_unscored_units": len(unscored),
            "scored_units": sorted(scored)[:80],
            "unscored_units": sorted(unscored)[:80],
            "_meaning": ("TAKEN = every requested unit produced a contrast. PARTIALLY TAKEN = some "
                         "did and some could not be read on these platforms. NOT TAKEN = the read "
                         "could not be taken at all. ⛔ NOT TAKEN is never a biological negative.")}


# ---------------------------------------------------------------------------------------------
def _summarise(res):
    lines = []
    for mf, p in res["platforms"].items():
        if p.get("_status") != "read":
            lines.append(f"{mf}: NOT READ — {p.get('_status')}")
            continue
        r = p["probe_mapping_rate"] or {}
        lines.append(f"{mf} [{p['platform']}] n={p['n_samples']} EMC={p['n_EMC']} "
                     f"comp={p['n_comparator']} probe_rate={r.get('probe_level_rate')} "
                     f"acc_rate={r.get('accession_resolution_rate')} "
                     f"(prior acc {r.get('prior_accession_resolution_rate')}) "
                     f"genes_measured={p['n_wanted_genes_measured']}"
                     f"/{p['n_wanted_genes_requested']}")
    lines.append("")
    lines.append("INSTRUMENT CONTROLS (read these first):")
    for g, d in res["reads"]["control"]["gene_readability"].items():
        for mf, r in d.items():
            lines.append(f"  {g:<7} {mf[:30]:<32} {str(r['verdict'])[:170]}")
    lines.append("")
    for k, v in res["reads"].items():
        if k == "control":
            continue
        rv = v["readability_verdict"]
        lines.append(f"{k}: {rv['state']} — {rv['n_scored_units']} scored / "
                     f"{rv['n_unscored_units']} unscored")
    lines.append("")
    lines.append("HEADLINE GENES:")
    for g in ("ASS1", "CSPG4", "CHST11", "NR2F1", "DLL3", "ASCL1", "INSM1", "PPARG"):
        for mf, r in (res["gene_reads"].get(g) or {}).items():
            lines.append(f"  {g:<7} {mf[:30]:<32} {str(r.get('verdict'))[:170]}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--fetch", action="store_true",
                    help="fetch from GEO/Enrichr/MSigDB (needs network; run in CI), rewrite the "
                         "inputs cache, then derive")
    ap.add_argument("--check", action="store_true",
                    help="re-derive from the cached inputs and diff against the artifact")
    args = ap.parse_args(argv)

    if args.check:
        if not os.path.exists(INPUTS):
            print("no inputs cache — run --fetch in CI first", file=sys.stderr)
            return 1
        if not os.path.exists(OUT):
            print("no artifact to check against", file=sys.stderr)
            return 1
        res = derive(json.load(open(INPUTS)))
        old = json.load(open(OUT))
        drift = [k for k in res if old.get(k) != res[k]]
        print("REPRODUCES" if not drift else f"DRIFT in: {drift}")
        return 0 if not drift else 1

    if args.fetch:
        inp = collect()
        json.dump(inp, open(INPUTS, "w"), indent=1)
    else:
        if not os.path.exists(INPUTS):
            print("no inputs cache — run --fetch in CI first", file=sys.stderr)
            return 1
        inp = json.load(open(INPUTS))

    res = derive(inp)
    json.dump(res, open(OUT, "w"), indent=2)
    print(_summarise(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
