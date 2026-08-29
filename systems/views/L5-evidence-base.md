---
id: DOC-VIEW-L5
title: "L5 — the evidence base: what everything above rests on"
level: L5
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Every modelled object, citation, artifact and pinned claim, and which route, instrument or lane rests on it.
scope: Level 5 only — assumptions, evidence, artifacts and claims. It asserts nothing of its own.
audience: ["maintainers", "autonomous research agents", "external reviewers"]
date: 2026-08-06
last_verified: 2026-08-06
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# L5 — the evidence base

> **The bottom of the hierarchy.** L0 asks what the landscape is; this asks what any of it
> actually rests on. Every row's **cited by** column is the link back UP — computed from the
> edges the routes, instruments, lanes and claims already assert, never written here, so it
> cannot disagree with them.

⚠ **A row citing nothing is not necessarily dead** — it may be registered ahead of the work
that will use it. It IS unreachable from the hierarchy, which is why it is shown rather than
omitted, and why `[L5]` reports the count.

**19 objects · 18 evidence items · 53 artifacts · 14 pinned claims.**

## Objects — the biological and molecular entities the program reasons about

| object | kind | status | cited by |
|---|---|---|---|
| **OBJ-EWSR1-WT**<br/>EWSR1 (wild type) | `wild_type_protein` | `wild_type` | [RT-6MP](L2-rt-6mp.md), [RT-ASO-ASK](L2-rt-aso-ask.md), [RT-EWSR1-PROTEIN](L2-rt-ewsr1-protein.md), [RT-FET-LC-LIGAND](L2-rt-fet-lc-ligand.md) |
| **OBJ-FUS-FUSNR4A3**<br/>FUS::NR4A3 | `fusion_protein` | `reported_breakpoint_unpinned` | [INS-CONSTRUCT-DESIGNS](registers/instruments.md), [RT-ATR-ASSESS](L2-rt-atr-assess.md), [RT-PARTNER-STRAT](L2-rt-partner-strat.md) |
| **OBJ-FUS-T1**<br/>EWSR1::NR4A3 type 1 | `fusion_protein` | `reported` | [INS-CONSTRUCT-DESIGNS](registers/instruments.md), [RT-6MP](L2-rt-6mp.md), [RT-ANDGATE](L2-rt-andgate.md), [RT-ASO](L2-rt-aso.md), [RT-ASO-ASK](L2-rt-aso-ask.md), [RT-ATR-ASSESS](L2-rt-atr-assess.md), [RT-CRISPR-CAS13](L2-rt-crispr-cas13.md), [RT-FUSION-OUTPUT](L2-rt-fusion-output.md), [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md), [RT-PARTNER-STRAT](L2-rt-partner-strat.md), [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md), [RT-RIBOZYME](L2-rt-ribozyme.md), [RT-SYNPROMOTER](L2-rt-synpromoter.md), [RT-TCIP](L2-rt-tcip.md), [RT-TRABECTEDIN](L2-rt-trabectedin.md), [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md), [RT-UBIQ-SELECTIVE](L2-rt-ubiq-selective.md) |
| **OBJ-FUS-T2**<br/>EWSR1::NR4A3 type 2 | `fusion_protein` | `reported` | [INS-CONSTRUCT-DESIGNS](registers/instruments.md), [RT-ASO](L2-rt-aso.md), [RT-ATR-ASSESS](L2-rt-atr-assess.md), [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md) |
| **OBJ-FUS-T5**<br/>EWSR1::NR4A3 type 5 | `fusion_protein` | `reported` | [INS-CONSTRUCT-DESIGNS](registers/instruments.md), [RT-ATR-ASSESS](L2-rt-atr-assess.md) |
| **OBJ-FUS-TAF15**<br/>TAF15::NR4A3 | `fusion_protein` | `reported` | [INS-CONSTRUCT-DESIGNS](registers/instruments.md), [RT-ATR-ASSESS](L2-rt-atr-assess.md), [RT-PARTNER-STRAT](L2-rt-partner-strat.md) |
| **OBJ-FUS-TCF12**<br/>TCF12::NR4A3 | `fusion_protein` | `reported_breakpoint_unpinned` | [INS-CONSTRUCT-DESIGNS](registers/instruments.md), [RT-ATR-ASSESS](L2-rt-atr-assess.md), [RT-PARTNER-STRAT](L2-rt-partner-strat.md) |
| **OBJ-LINE-HEMCSS**<br/>ACH-001519 / H-EMC-SS | `cell_line` | `identity_disputed` | [INS-GEO-SERIES-CHARACTERISE](registers/instruments.md) |
| **OBJ-MODEL-E7E3**<br/>The modelled EWSR1 e7 :: NR4A3 e3 construct | `modelled_construct` | `modelled_not_reported` | [INS-FUSION-OBJECT-INVENTORY](registers/instruments.md), [RT-ATR-ASSESS](L2-rt-atr-assess.md), [RT-EWSR1-PROTEIN](L2-rt-ewsr1-protein.md), [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md), [RT-TCR-IMMTAC](L2-rt-tcr-immtac.md), [RT-VACCINE](L2-rt-vaccine.md) |
| **OBJ-NR4A1-WT**<br/>NR4A1 / Nur77 | `wild_type_protein` | `wild_type` | [RT-ASYMMETRIC](L2-rt-asymmetric.md), [RT-DEGRADER](L2-rt-degrader.md), [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md), [RT-RXR](L2-rt-rxr.md) |
| **OBJ-NR4A2-WT**<br/>NR4A2 / Nurr1 | `wild_type_protein` | `wild_type` | [RT-ASYMMETRIC](L2-rt-asymmetric.md), [RT-DEGRADER](L2-rt-degrader.md), [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md), [RT-RXR](L2-rt-rxr.md) |
| **OBJ-NR4A3-AF1**<br/>NR4A3 AF-1 (N-terminal activation function) | `domain` | `domain` | [RT-6MP](L2-rt-6mp.md), [RT-MONOVALENT](L2-rt-monovalent.md) |
| **OBJ-NR4A3-DBD**<br/>NR4A3 C4 zinc-finger DNA-binding domain | `domain` | `domain` | [RT-DBD](L2-rt-dbd.md), [RT-SYNPROMOTER](L2-rt-synpromoter.md) |
| **OBJ-NR4A3-LBD-CATALOGUE**<br/>Catalogue recombinant NR4A3 LBD (Cayman 40344, UniProt aa 398–626) | `reagent` | `domain` | [RT-COVALENT-PROBE](L2-rt-covalent-probe.md), [RT-MONOVALENT](L2-rt-monovalent.md) |
| **OBJ-NR4A3-LBD-MODELLED**<br/>The modelled NR4A3 ligand-binding domain construct (NR4A3 373–626) | `domain` | `domain` | [RT-ANDGATE](L2-rt-andgate.md), [RT-COVALENT-PROBE](L2-rt-covalent-probe.md), [RT-DEGRADER](L2-rt-degrader.md), [RT-GLUE](L2-rt-glue.md), [RT-MONOVALENT](L2-rt-monovalent.md), [RT-RIPTAC](L2-rt-riptac.md), [RT-TCIP](L2-rt-tcip.md) |
| **OBJ-NR4A3-WT**<br/>NR4A3 / NOR-1 (wild type) | `wild_type_protein` | `wild_type` | [RT-ASO](L2-rt-aso.md), [RT-ASO-ASK](L2-rt-aso-ask.md), [RT-ASYMMETRIC](L2-rt-asymmetric.md), [RT-COVALENT-PROBE](L2-rt-covalent-probe.md), [RT-DEGRADER](L2-rt-degrader.md), [RT-MONOVALENT](L2-rt-monovalent.md), [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md), [RT-RXR](L2-rt-rxr.md) |
| **OBJ-RES-C166**<br/>NR4A3 C166 | `residue` | `residue` | ⚠ **nothing** |
| **OBJ-RES-C397**<br/>NR4A3 C397 | `residue` | `residue` | [RT-COVALENT-PROBE](L2-rt-covalent-probe.md), [RT-DEGRADER](L2-rt-degrader.md), [RT-MONOVALENT](L2-rt-monovalent.md) |
| **OBJ-RES-NR4A1-C551**<br/>NR4A1 C551 | `residue` | `residue` | [RT-COVALENT-PROBE](L2-rt-covalent-probe.md) |

## Evidence — the literature this program cites

⚠ **`misattributed_as` is load-bearing.** Several of these have been cited under a wrong name in this repository's own history; the alias is kept so a future reader who meets the wrong name still lands here.

| id | citation | what it supports | cited by |
|---|---|---|---|
| **EV-BANGERTER-2023**<br/>PMID 36316541 | Bangerter et al. 2023, Hum Cell — ex-vivo drug sensitivity in patient-derived EMC models USZ20-EMC1 and USZ22-EMC2. | The carfilzomib route's only ex-vivo EMC evidence. ⛔ READ THE SCOPE: the 40-drug panel (17 chemotherapies + 23 targeted agents) was screened on USZ20-EMC1 ALONE; carfilzo | [RT-CARFILZOMIB](L2-rt-carfilzomib.md), [RT-PARTNER-STRAT](L2-rt-partner-strat.md) |
| **EV-BOKLAN-2025**<br/>PMID 40941020 | Boklan J, Langevin AM, Bielamowicz K, Neville K, Trippett T, Brown V, DuBois SG, Eshun F, Gelfond J, Zomet A, Narendran A, Lacayo NJ. A Phase I Study  | The only record found in which carfilzomib ITSELF has been given to sarcoma patients: a dose-escalation of carfilzomib with cyclophosphamide and etoposide in relapsed or  | [RT-CARFILZOMIB](L2-rt-carfilzomib.md) |
| **EV-EB-TCIP-2025**<br/>10.1021/jacs.5c05634 | EB-TCIP on EWSR1::FLI1, JACS 2025 — bivalent transcriptional chemically-induced proximity that co-opts a fusion TF. | The TCIP route's mechanism and its stated first limitation — "Due to the dearth of EWSR1::FLI1-specific ligands, we have used a N-FKBP12^F36V-EWSR1::FLI1 model system" —  | [RT-TCIP](L2-rt-tcip.md) |
| **EV-FET-ATR-2023**<br/>PMID 37205599 | FET fusion oncoproteins impair ATM activation at double-strand breaks through their shared N-terminal IDR, leaving the ATR axis load-bearing. | The synthetic-lethality premise the ATR route inherits, and the structural precondition (retain the N-terminal IDR, lose the C-terminal RGG repeats) that emc_fet_idr_cens | [RT-ATR-ASSESS](L2-rt-atr-assess.md), [RT-ATR-PANEL](L2-rt-atr-panel.md) |
| **EV-FILION-2009**<br/>— | Filion C et al. (2009) — the EWSR1::NR4A3 fusion transactivates a PPARG-promoter response element. | That the fusion is a functional transcriptional driver acting through its DNA-binding domain; the fusion→PPARG axis both PPARG routes rest on; the DBD filter in fusion_ob | `OBJ-NR4A3-DBD`, [RT-FUSION-OUTPUT](L2-rt-fusion-output.md), [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md), [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) |
| **EV-HIGUCHI-2023**<br/>PMID 36636023 | Higuchi T et al. (2023) — the only functional test of the PPARγ intervention direction in an EMC model. | The single functional experiment anywhere testing the DIRECTION of PPARγ intervention in EMC; it favours AGONISM. ⛔ Carries a model-identity caveat: it uses H-EMC-SS (OBJ | [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md), [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) |
| **EV-MAKI-2005**<br/>PMID 15739208 | Maki RG, Kraft AS, Scheu K, Yamada J, Wadler S, Antonescu CR, Wright JJ, Schwartz GK. A multicenter Phase II study of bortezomib in recurrent or metas | ⛔ IT DOES NOT SUPPORT RT-CARFILZOMIB — IT BOUNDS IT, and it is the only human read on proteasome inhibition in the parent histology this repository holds. Two arms, Simon | [RT-CARFILZOMIB](L2-rt-carfilzomib.md) |
| **EV-PALMERINI-2022**<br/>PMID 36568164 | Palmerini E, Sanfilippo R, Grignani G, Buonadonna A, Romanini A, Badalamenti G, Ferraresi V, Vincenzi B, Comandone A, Pizzolorusso A, Brunello A, Gels | ⭐ THE SECOND EMC-SPECIFIC TRABECTEDIN RESPONSE DENOMINATOR THAT EXISTS, and the only one carrying an EMC patient with progressive disease on the drug. A post-hoc case ser | [RT-TRABECTEDIN](L2-rt-trabectedin.md) |
| **EV-PIOGLITAZONE-TRABECTEDIN-2019**<br/>10.1158/1078-0432.CCR-19-0976 | Pioglitazone + trabectedin induced adipocyte differentiation and overcame trabectedin resistance in myxoid liposarcoma. Clin Cancer Res 2019;25:7565. | That the combination already worked in the sibling myxoid sarcoma — the class-extension interest that gives the trabectedin+PPARγ route its taker. | [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) |
| **EV-PMC2395470**<br/>— | A counted series: 10 of 15 EWS/CHN tumours were exon 12 :: exon 3; 2 of 15 were type 5. | That type 1 is the commonest reported EWSR1::NR4A3 junction, on a counted series rather than an assertion. | `OBJ-FUS-T1`, `OBJ-FUS-T5`, `OBJ-FUS-TAF15` |
| **EV-PMC3335514**<br/>— | "The most common fusion transcript contains exon 12 of EWSR1 fused to exon 3 of NR4A3 (type 1), whereas exon 7 of EWSR1 is fused to exon 2 of NR4A3 in | The exon-level definitions of EWSR1::NR4A3 type 1 and type 2, and of TAF15::NR4A3. | `OBJ-FUS-T1`, `OBJ-FUS-T2`, `OBJ-FUS-TAF15` |
| **EV-PMC4015728**<br/>— | Agaram NP et al. (2014) — RT-PCR primer design: an EWSR1 exon 12 forward primer with an NR4A3 exon 3 reverse for type 1; an EWSR1 exon 7 forward with  | Independent corroboration of the type 1 and type 2 exon-level junctions. | `OBJ-FUS-T1`, `OBJ-FUS-T2`, [RT-PARTNER-STRAT](L2-rt-partner-strat.md) |
| **EV-PMC4055444**<br/>— | "The most frequent are: type 1, for the fusion between exons 12 of EWS and 3 of CHN, and type 5, between exons 13 of EWS and 3 of CHN." Also: the TCF1 | The type 5 junction; the TAF15::NR4A3 exclusivity; the TCF12::NR4A3 genomic-only breakpoint. | `OBJ-FUS-T1`, `OBJ-FUS-T5`, `OBJ-FUS-TAF15`, `OBJ-FUS-TCF12` |
| **EV-PMC6766969**<br/>— | "E-N, corresponding to EWSR1 (exons 1-12)-NR4A3 (exons 3-8)"; "T-N*, corresponding to the commonest TAF15 (exons 1-6)-NR4A3 (exons 3-8) fusion"; and a | Expressed constructs corroborating type 1 and TAF15::NR4A3; the registered-but-deliberately-unmodelled cryptic-exon TAF15 isoform. | `OBJ-FUS-T1`, `OBJ-FUS-TAF15`, [RT-FUSION-OUTPUT](L2-rt-fusion-output.md), [RT-PARTNER-STRAT](L2-rt-partner-strat.md) |
| **EV-SUBRAMANIAN-2005**<br/>PMID 15920699 | Subramanian S et al. (2005) — expression profiling of EMC; PPARG/PPARGC1A over-expression, and the PPARγ-INHIBITOR proposal. | The independent EMC cohort (10 EMCs) showing PPARG over-expression relative to other sarcomas — one of the two concordant abundance cohorts. ⚠ Its discussion proposes PPA | [RT-FUSION-OUTPUT](L2-rt-fusion-output.md), [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md), [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) |
| **EV-WANSA-2003**<br/>PMID 12709428 | Wansa KDSA et al. J Biol Chem 2003;278(27):24776–90. | NOR-1's AF-1 is delimited to residues 1–112 and SRC-2 modulates AF-1 but not the LBD — the basis on which the 6-mercaptopurine route is closed for the chimera. | `OBJ-NR4A3-AF1`, [RT-6MP](L2-rt-6mp.md) |
| **EV-ZAIENNE-2022**<br/>PMID 35704774 | Zaienne D, Arifi S, Marschner JA, Heering J, et al. Druggability Evaluation of the Neuron Derived Orphan Receptor (NOR-1) Reveals Inverse NOR-1 Agonis | LBD-borne functional modulation of NOR-1/NR4A3; the Gal4-NOR-1-LBD reporter construct (which is itself AF-1-less); the absent paralogue counter-screen; the inverse-agonis | [RT-COVALENT-PROBE](L2-rt-covalent-probe.md), [RT-DEGRADER](L2-rt-degrader.md), [RT-MONOVALENT](L2-rt-monovalent.md) |
| **EV-ZETTERSTROM-1996**<br/>PMID 8961274 | Zetterström RH et al. Mol Endocrinol 1996;10:1656–66. | NR4A3/NOR-1 does not heterodimerise with RXR, unlike NR4A1 and NR4A2 — the verbatim basis on which the RXR-heterodimer route is closed. | [RT-RXR](L2-rt-rxr.md) |

## Artifacts — the files a claim can be checked against

| artifact | path | produced by | cited by |
|---|---|---|---|
| **ART-APO-POSE-SITE** | `research/modalities/apo-pose-site-in-regime.json` | `research/modalities/apo_pose_recovery.py` | `CLM-APO-SITE-IN-REGIME`, [RT-DEGRADER](L2-rt-degrader.md) |
| **ART-ATR-VULNERABILITY** | `research/modalities/emc-atr-vulnerability.json` | `research/modalities/emc_atr_vulnerability.py` | [RT-ATR-ASSESS](L2-rt-atr-assess.md) |
| **ART-CARE-DELIVERY-EVIDENCE** | `research/modalities/emc-care-delivery-evidence.json` | `research/modalities/emc_care_delivery_evidence.py` | [RT-DIAGNOSTIC-PATHWAY](L2-rt-diagnostic-pathway.md), [RT-METASTASECTOMY](L2-rt-metastasectomy.md), [RT-POPULATION-REGISTRY](L2-rt-population-registry.md), [RT-RISK-MODEL](L2-rt-risk-model.md), [RT-SURGICAL-QUALITY](L2-rt-surgical-quality.md), [RT-SURVEILLANCE](L2-rt-surveillance.md) |
| **ART-CENSUS-ROUTE-GRADING** | `research/modalities/census-route-expression-grading.json` | `research/modalities/census_route_expression_grading.py` | [RT-ALK-HIT](L2-rt-alk-hit.md), [RT-APOPTOSIS-DEP](L2-rt-apoptosis-dep.md), [RT-ARGININE](L2-rt-arginine.md), [RT-CHAPERONE](L2-rt-chaperone.md), [RT-EZH2](L2-rt-ezh2.md), [RT-HYPOXIA-PRODRUG](L2-rt-hypoxia-prodrug.md), [RT-IMMUNOCYTOKINE](L2-rt-immunocytokine.md), [RT-MATRIX-ADDRESS](L2-rt-matrix-address.md), [RT-MATRIX-SYNTHESIS](L2-rt-matrix-synthesis.md), [RT-MDM2](L2-rt-mdm2.md), [RT-MTAP-PRMT5](L2-rt-mtap-prmt5.md), [RT-NR2F1](L2-rt-nr2f1.md), [RT-POLQ](L2-rt-polq.md), [RT-RET](L2-rt-ret.md), [RT-SGK1](L2-rt-sgk1.md), [RT-TXN-CDK](L2-rt-txn-cdk.md) |
| **ART-CONSTRUCT-DESIGNS** | `research/modalities/emc-fet-construct-designs.json` | `research/modalities/emc_fet_construct_designs.py` | `CLM-CONSTRUCT-FRAME`, `CLM-CONSTRUCT-TCF12`, `OBJ-FUS-T1`, `OBJ-FUS-T2`, `OBJ-FUS-T5`, `OBJ-FUS-TAF15`, [RT-ATR-ASSESS](L2-rt-atr-assess.md) |
| **ART-CTA-EXPRESSION** | `research/modalities/depmap-target-expression.json` | `research/modalities/depmap_target_expression.py` | [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md), [RT-TCRT-CTA](L2-rt-tcrt-cta.md) |
| **ART-DDR-AXIS-SCAN** | `research/modalities/fet-ddr-axis-scan.json` | `research/modalities/fet_ddr_axis_scan.py` | `CLM-ATRI-GDSC`, `CLM-KO-SATURATION`, [RT-ATR-ASSESS](L2-rt-atr-assess.md) |
| **ART-DECOY-NULL-LBD** | `research/modalities/categorical-decoy-null-lbd.json` | `research/modalities/categorical_decoy_null.py` | `CLM-C397-DECOY-NULL`, [RT-COVALENT-PROBE](L2-rt-covalent-probe.md), [RT-DEGRADER](L2-rt-degrader.md) |
| **ART-DEPMAP-SARCOMA-DEP** | `research/modalities/depmap-sarcoma-dependency.json` | `research/modalities/depmap_sarcoma_dependency.py` | [RT-ALK-HIT](L2-rt-alk-hit.md), [RT-CHAPERONE](L2-rt-chaperone.md), [RT-DNAPK](L2-rt-dnapk.md), [RT-SYNLETH-DEP](L2-rt-synleth-dep.md) |
| **ART-EMC-CLINICAL-REGISTRY** | `research/data/emc-clinical-registry.json` | `hand-curated from published literature; ingestion via scripts/fetch-paper.mjs + scripts/triage-literature.mjs` | [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md), [RT-ICI-TKI](L2-rt-ici-tki.md), [RT-PARTNER-STRAT](L2-rt-partner-strat.md), [RT-TRABECTEDIN](L2-rt-trabectedin.md), [RT-VACCINE-COMBINATION](L2-rt-vaccine-combination.md) |
| **ART-EMC-ENDPOINT-DISCORDANCE** | `research/manuscripts/endpoint/emc-endpoint-discordance.json` | `research/manuscripts/emc_endpoint_discordance.py (stdlib only, CPU, $0; --check re-derives and refuses to write on any drift)` | [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) |
| **ART-EMC-EXPRESSION-PANELS** | `research/modalities/emc-expression-panels.json` | `research/modalities/emc_expression_panels.py` | [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md), [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md), [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) |
| **ART-EMC-PERFUSION-MYXOID-SEARCH** | `research/literature/emc-perfusion-myxoid-search-2026-08-27.json` | `PubMed E-utilities queries through this container's NCBI MCP server, with every query, its record count and its verdict recorded — including the queries that returned nothing` | [RT-LIMB-PERFUSION](L2-rt-limb-perfusion.md) |
| **ART-EMC-RT-LUNG-METS** | `research/literature/emc-rt-lung-mets-findings.json` | `scripts/lit_rt_probe.py, plus hand curation of the retrieved full texts` | [RT-MDT-LUNG](L2-rt-mdt-lung.md) |
| **ART-ENDPOINT-CORPUS** | `research/manuscripts/endpoint/endpoint-corpus.json` | `research/manuscripts/endpoint_corpus.py (stdlib only, CPU, $0; --check re-derives from the literature-cache extraction and refuses to write on drift)` | [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) |
| **ART-ENDPOINT-ORR-DCR-REREAD** | `research/manuscripts/endpoint/orr-dcr-reread.json` | `research/manuscripts/orr_dcr_reread.py (stdlib only, CPU, $0; --check re-derives)` | [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) |
| **ART-ENDPOINT-PLACEBO-CALIBRATION** | `research/manuscripts/endpoint/placebo-arm-calibration.json` | `research/manuscripts/placebo_arm_calibration.py (stdlib only, CPU, $0; --check re-derives)` | [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) |
| **ART-ENDPOINT-PRIOR-ART-AUDIT** | `research/manuscripts/endpoint/endpoint-prior-art-audit.json` | `research/manuscripts/endpoint_prior_art_audit.py (stdlib only, CPU, $0; --check re-derives)` | [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) |
| **ART-ENDPOINT-REGIME-MAP** | `research/manuscripts/endpoint/endpoint-regime-map.json` | `research/manuscripts/endpoint_regime_map.py (stdlib only, CPU, $0; --check re-derives)` | [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) |
| **ART-FET-TRIAL-ELIGIBILITY** | `research/literature/fet-fusion-trial-eligibility-2026-08-07.json` | `a ClinicalTrials.gov API v2 sweep read into JSON from the literature-cache corpus` | [RT-TRIAL-REACH](L2-rt-trial-reach.md) |
| **ART-FUSION-OBJECT-INVENTORY** | `research/modalities/fusion-object-inventory.json` | `research/modalities/fusion_object_inventory.py` | `CLM-BREAKPOINT-FILTER`, `OBJ-EWSR1-WT`, `OBJ-NR4A3-WT`, [RT-EWSR1-PROTEIN](L2-rt-ewsr1-protein.md), [RT-FET-LC-LIGAND](L2-rt-fet-lc-ligand.md) |
| **ART-FUSION-PARTNER-POOLING** | `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` | `research/manuscripts/emc_fusion_partner_pooling.py` | [RT-PARTNER-STRAT](L2-rt-partner-strat.md) |
| **ART-GSE28866-TUMOUR-VS-NORMAL** | `research/modalities/gse28866-tumour-vs-normal.json` | `the GSE28866 supplementary peak-table read (emc-expression-datasets.yml)` | ⚠ **nothing** |
| **ART-HLA-COVERAGE** | `research/modalities/hla-coverage.json` | `research/modalities/hla_coverage.py` | [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md), [RT-TCR-IMMTAC](L2-rt-tcr-immtac.md), [RT-TCRT-CTA](L2-rt-tcrt-cta.md), [RT-VACCINE](L2-rt-vaccine.md) |
| **ART-HORMONE-PARTNER-LANE** | `research/modalities/hormone-partner-lane.json` | `research/modalities/hormone_partner_map.py` | [RT-HORMONE-PARTNER](L2-rt-hormone-partner.md) |
| **ART-HSPA8-PROMOTER-GRADE** | `research/modalities/hspa8-promoter-hormone-grade.json` | `—` | [RT-HORMONE-PARTNER](L2-rt-hormone-partner.md) |
| **ART-ICDO-CONTAMINATION** | `research/modalities/emc-icdo-contamination.json` | `research/modalities/emc_icdo_contamination.py` | [RT-DIAGNOSTIC-PATHWAY](L2-rt-diagnostic-pathway.md) |
| **ART-IDR-CENSUS** | `research/modalities/emc-fet-idr-census.json` | `research/modalities/emc_fet_idr_census.py` | `CLM-IDR-COMPARATIVE`, `CLM-IDR-CONTROLS`, `CLM-IDR-EMC`, [RT-ATR-ASSESS](L2-rt-atr-assess.md) |
| **ART-IPD-SURVIVAL** | `research/modalities/emc-ipd-survival.json` | `research/modalities/emc_ipd_survival.py` | [RT-IPD-SURVIVAL](L2-rt-ipd-survival.md) |
| **ART-JUNCTION-ASO-OFFTARGET** | `research/modalities/junction-aso-offtarget-e12n3.json` | `research/modalities/junction_aso_offtarget.py` | [RT-ASO](L2-rt-aso.md) |
| **ART-LOCOREGIONAL-ELIGIBILITY** | `research/modalities/emc-locoregional-eligibility.json` | `research/modalities/emc_locoregional_eligibility.py` | [RT-LIMB-PERFUSION](L2-rt-limb-perfusion.md), [RT-LUNG-DIRECTED](L2-rt-lung-directed.md), [RT-RT-INTENSIFY](L2-rt-rt-intensify.md) |
| **ART-MONOVALENT-REACH** | `research/modalities/nr4a3-monovalent-reach.json` | `research/modalities/nr4a3_monovalent_reach.py` | `CLM-MONOVALENT-CROSSCHECK`, `CLM-MONOVALENT-VERDICT`, [RT-MONOVALENT](L2-rt-monovalent.md) |
| **ART-NR4A-PARALOGUE-DYNAMICS** | `research/modalities/nr4a-paralogue-dynamics.json` | `research/modalities/nr4a_paralogue_dynamics.py` | [LANE-13](registers/lanes.md) |
| **ART-NRV04-RETRO-CRITERIA-AUDIT** | `research/modalities/nrv04-retro-criteria-audit.json` | `research/modalities/nrv04_retro_criteria_audit.py` | [LANE-8](registers/lanes.md) |
| **ART-NRV04-RETRO-PRESPEND-AUDIT** | `research/modalities/nrv04-retro-prespend-audit.json` | `research/modalities/nrv04_retro_prespend_audit.py` | [LANE-8](registers/lanes.md) |
| **ART-PROGNOSTIC-COEFFICIENTS** | `research/modalities/emc-prognostic-coefficients.json` | `research/modalities/emc_prognostic_coefficients.py` | [RT-RISK-MODEL](L2-rt-risk-model.md) |
| **ART-PUBLISHED-WARHEAD-REGISTRY** | `research/modalities/published-warhead-registry.json` | `—` | ⚠ **nothing** |
| **ART-RECURRENCE-TIMING** | `research/modalities/emc-recurrence-timing.json` | `research/modalities/emc_recurrence_timing.py` | [RT-SURVEILLANCE](L2-rt-surveillance.md) |
| **ART-RET-ACTIVATION-BAR** | `research/modalities/emc-ret-activation-bar.json` | `a Europe PMC retrieval read into JSON by hand from the literature-cache corpus` | [RT-RET](L2-rt-ret.md) |
| **ART-RT-CONTRADICTION** | `research/modalities/emc-radiotherapy-contradiction.json` | `research/modalities/emc_radiotherapy_contradiction.py` | [RT-RT-INTENSIFY](L2-rt-rt-intensify.md) |
| **ART-SELCAL-VERDICT** | `research/modalities/selcal-verdict.json` | `research/modalities/selcal_cofold_validate.py` | [LANE-22](registers/lanes.md) |
| **ART-SITE-CURATION** | `research/modalities/emc-site-curation.json` | `research/modalities/emc_site_curation.py` | [RT-LIMB-PERFUSION](L2-rt-limb-perfusion.md), [RT-LUNG-DIRECTED](L2-rt-lung-directed.md), [RT-METASTASECTOMY](L2-rt-metastasectomy.md) |
| **ART-SURFACE-EXPRESSION** | `research/modalities/emc-surfaceome-scan.json` | `research/modalities/emc_surfaceome_scan.py` | [RT-B7H3](L2-rt-b7h3.md) |
| **ART-SURGICAL-QUALITY** | `research/modalities/emc-surgical-quality.json` | `research/modalities/emc_surgical_quality.py` | [RT-SURGICAL-QUALITY](L2-rt-surgical-quality.md) |
| **ART-SYSTEMIC-THERAPY-POOLING** | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` | `research/manuscripts/emc_systemic_therapy_pooling.py` | [RT-SCHEDULING](L2-rt-scheduling.md), [RT-SEQUENCING](L2-rt-sequencing.md) |
| **ART-TARGET-ROUTE-CENSUS** | `research/modalities/target-route-census.json` | `research/modalities/target_route_census.py` | `CLM-AF1-LC-SWAP`, `CLM-FUSION-MODEL-DISAGREEMENT`, `OBJ-NR4A3-AF1`, `OBJ-NR4A3-DBD`, [RT-6MP](L2-rt-6mp.md), [RT-ASYMMETRIC](L2-rt-asymmetric.md), [RT-DBD](L2-rt-dbd.md), [RT-RXR](L2-rt-rxr.md) |
| **ART-TCIP-EFFECTOR-ARMS** | `research/modalities/nr4a3-effector-arm-registry.json` | `research/modalities/nr4a3_effector_stage.py` | [RT-TCIP](L2-rt-tcip.md) |
| **ART-TCIP-REACH** | `research/modalities/nr4a3-tcip-reach.json` | `research/modalities/nr4a3_tcip_reach.py` | [RT-TCIP](L2-rt-tcip.md) |
| **ART-TRIAL-REACH-ADJUDICATION** | `research/literature/emc-trial-reachability-adjudication-2026-08-09.json` | `per-trial ClinicalTrials.gov API v2 reads, adjudicated against the eligibility text and quoted verbatim` | [RT-TRIAL-REACH](L2-rt-trial-reach.md) |
| **ART-VALB-PSERIES-CHEM** | `research/modalities/valb-pseries-chem.json` | `research/modalities/valb_pseries_chem.py` | [LANE-5](registers/lanes.md) |
| **ART-VALB-TRIANGLE-CLOSURE** | `research/modalities/valb-triangle-closure.json` | `research/modalities/valb_triangle_closure.py` | [LANE-9](registers/lanes.md) |
| **ART-VALB-TRIANGLE-REDUCTION** | `research/modalities/valb-triangle-reduction.json` | `research/modalities/valb_triangle_reduce.py` | [LANE-9](registers/lanes.md) |
| **ART-WETLAB-CONTRACTING-COSTS** | `research/modalities/wetlab-contracting-costs.json` | `research/modalities/wetlab_contracting_costs.py` | ⚠ **nothing** |

## Claims — a document's sentence pinned to the field that has to support it

⭐ **This is the finest grain of traceability the model carries** and the one the brief's *"no orphaned knowledge"* actually cashes out as: not *"this paper cites that paper"* but *"this sentence, in this file, rests on this JSON pointer in this artifact"*.

| claim | document · locator | rests on | field |
|---|---|---|---|
| **CLM-AF1-LC-SWAP** | `research/manuscripts/program/emc-post-degrader-options.md`<br/>the 6-MP closure — 'NOR-1 residues 1–112 sit entirely inside the stretch the fusion replaces' | **ART-TARGET-ROUTE-CENSUS** | `/af1_to_lc_swap` |
| **CLM-APO-SITE-IN-REGIME** | `research/manuscripts/nr4a3-program-map.md`<br/>V3's row — the in-regime site panel by two independent transfer routes | **ART-APO-POSE-SITE** | `/site_panel_in_regime` |
| **CLM-ATRI-GDSC** | `research/manuscripts/program/emc-post-degrader-options.md`<br/>the ATRi-contrast section — the GDSC2 re-cut by FET status | **ART-DDR-AXIS-SCAN** | `/atr_inhibitor_sensitivity_gdsc/by_drug` |
| **CLM-BREAKPOINT-FILTER** | `research/modalities/fusion-object-inventory.md`<br/>'Which chimeras are possible, and which are plausible' | **ART-FUSION-OBJECT-INVENTORY** | `/plausible_breakpoints/n_after_DBD_filter` |
| **CLM-C397-DECOY-NULL** | `research/manuscripts/nr4a3-program-map.md`<br/>V17's row — the second, independently pre-registered decoy-null scope that DOES contain C397 | **ART-DECOY-NULL-LBD** | `/results` |
| **CLM-CONSTRUCT-FRAME** | `research/manuscripts/dependency/emc-atr-collaborator-package.md`<br/>§7.2 'The four constructs — all four are in frame' | **ART-CONSTRUCT-DESIGNS** | `/n_constructs_in_frame` |
| **CLM-CONSTRUCT-TCF12** | `research/manuscripts/dependency/emc-atr-collaborator-package.md`<br/>§7.4 'TCF12 — the negative control checked out' | **ART-CONSTRUCT-DESIGNS** | `/tcf12_negative_control` |
| **CLM-FUSION-MODEL-DISAGREEMENT** | `research/manuscripts/program/target-route-options.md`<br/>§1.3 'the repo held two incompatible models of the fusion protein' | **ART-TARGET-ROUTE-CENSUS** | `/fusion_model_disagreement` |
| **CLM-IDR-COMPARATIVE** | `research/IDEAS.md`<br/>the ATR route row's 'structural precondition is COMPUTED and it holds' sentence | **ART-IDR-CENSUS** | `/emc_vs_measured_fusions_comparative/rows` |
| **CLM-IDR-CONTROLS** | `research/manuscripts/program/emc-post-degrader-options.md`<br/>the positive-control rows beside it (the fusions in which ATM suppression was MEASURED) | **ART-IDR-CENSUS** | `/positive_controls_pass` |
| **CLM-IDR-EMC** | `research/manuscripts/program/emc-post-degrader-options.md`<br/>route 1's RGG-retention table row for EWSR1::NR4A3 | **ART-IDR-CENSUS** | `/emc_canonical_EWSR1_NR4A3/rg_dipeptides_retained` |
| **CLM-KO-SATURATION** | `research/manuscripts/program/emc-post-degrader-options.md`<br/>the DepMap knockout scan reported as a FAILED instrument | **ART-DDR-AXIS-SCAN** | `/knockout_instrument_saturation` |
| **CLM-MONOVALENT-CROSSCHECK** | `research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md`<br/>§3 'its bivalent half replicates the committed artifact cell-for-cell' | **ART-MONOVALENT-REACH** | `/cross_checks` |
| **CLM-MONOVALENT-VERDICT** | `research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md`<br/>§3 'The result' — the E3-arm-free reach enumeration | **ART-MONOVALENT-REACH** | `/verdict/answer_on_the_conservative_convention` |

## Where this sits

[← L0](L0-ecosystem.md) · L2 route pages link down to the rows above · registers: [instruments](registers/instruments.md) · [lanes](registers/lanes.md) · [requirements](registers/requirements.md)
