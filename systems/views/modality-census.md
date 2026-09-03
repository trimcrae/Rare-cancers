---
id: DOC-VIEW-MODALITY-CENSUS
title: Modality census — every category of cancer treatment, graded against EMC
level: cross-cutting
kind: generated
status: generated
generator: systems/systems_check.py
purpose: "The denominator the route board is a numerator of: what oncology can do, and which of it reaches this disease."
scope: "All modality classes. Vocabulary: systems/taxonomy/modality.md. Grades classes, never targets."
audience: ["maintainers", "autonomous research agents", "external reviewers"]
date: 2026-08-09
last_verified: 2026-08-09
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# Modality census

> A **search** returns what it queried for, so its silence cannot tell *considered and
> dismissed* apart from *never pointed at*. A **census** enumerates first and grades second,
> which is what makes absence auditable rather than remembered.

> **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness — for
> any class, in any verdict, including the ones that survive.**

**217 modality classes · 19 groups · 4 bands.**

## ⭑ 111 classes no prior search here had pointed at

This is the census's result. `never_searched` is orthogonal to the verdict, and the
orthogonality carries the finding: a class can be unsearched and still not reach EMC —
nobody looked, and now that someone has, it does not — or unsearched **and** live, which
is the residue no prior sweep could have returned. **14 of the 111
are live** (`candidate` or `parked_capability`).

| verdict | classes | of which never searched |
|---|---:|---:|
| ⭑ `candidate` | 20 | 6 |
| ⏸ `parked_capability` | 9 | 8 |
| ✓ `on_board` | 42 | 1 |
| ● `in_clinical_use` | 8 | 0 |
| ✕ `already_rejected` | 33 | 0 |
| ✕ `excluded` | 95 | 86 |
| — `not_applicable` | 10 | 10 |

### By band

⚠ Three of these four bands were **structurally invisible** to every prior search here —
not rejected, never queried — which is the reason the census carries them at all.

| band | classes | never searched |
|---|---:|---:|
| `drug_mechanism` | 162 | 86 |
| `delivery_and_conjugate` | 26 | 18 |
| `physical_locoregional` | 15 | 3 |
| `strategy_and_architecture` | 14 | 4 |

## The live residue

Every class that no prior search reached and that this census did not close. Each
carries the cheapest observation that would move it.

| class | group | verdict | cheapest next step |
|---|---|---|---|
| **MOD-EXPANDED-ACCESS** — Expanded access, compassionate use and off-label registries | `strategy_and_trial_architecture` | ⭑ `candidate` | ⭐ STILL OPEN AND LIVE, $0 — and NOT covered by the registry sweep that graded its route. Map the access pathways and the public outcome registries that accept off-label single-patient reports. It pairs with the reachability result, which is the most actionable finding in the portfolio. |
| **MOD-IMMUNOCYTOKINE** — Immunocytokines (tumour-targeted cytokine fusions) | `antibody_and_antibody_like` | ⭑ `candidate` | ⛔ TAKEN 2026-08-09 AND THE READ CANNOT BE COMPLETED IN PRINCIPLE. The parent genes were read and are abundant but not enriched. The address is a SPLICE VARIANT and a gene-level probe cannot see one, so the isoform question is unreachable by any expression instrument here — not pending. |
| **MOD-INHALED-CHEMO** — Inhaled and aerosolised cytotoxic therapy | `physical_device_locoregional` | ⭑ `candidate` | ⛔ THERE IS NO 'REGISTRY EXTRACTION' TO SHARE — the metastatic-site and burden fields this row assumes were never curated (measured 2026-08-09). It depends on the same re-curation as the other lung-directed rows and cannot be assessed before it. |
| **MOD-ISOLATED-LUNG-PERFUSION** — Isolated lung perfusion and regional pulmonary delivery | `physical_device_locoregional` | ⭑ `candidate` | ⛔ THE FIELDS THIS ROW CALLS 'ALREADY CURATED' DO NOT EXIST (measured 2026-08-09). Metastatic site appears once in one cohort's free-text note and nowhere as data; time-to-metastasis appears nowhere at all. ⭐ The real $0 step is re-curating metastatic site from the open-access primary reports. |
| **MOD-MCL1-BCLXL** — MCL-1 and BCL-xL inhibitors | `ppi_and_undruggable` | ⭑ `candidate` | ⛔ TAKEN 2026-08-09, both halves. The BCL-2 family was read across both cohorts — guardians concordantly LOWER, the MCL-1-specific sensitiser concordantly HIGHER — and the committed ex-vivo screen was re-read. ⭐ The class stays open because abundance cannot measure which protein HOLDS the effectors; that needs BH3 profiling. |
| **MOD-PRMT5-MAT2A** — PRMT5 / MAT2A inhibitors (MTAP-deletion synthetic lethality) | `enzyme_inhibitor_non_kinase` | ⭑ `candidate` | ◐ MOST OF IT TAKEN 2026-08-09 and it became a written paper with five figures. ⛔ TAKEN: both readable series read; the locus cut gene by gene, which CLOSED route 2; an exact permutation test for PRMT5 on both platforms; a proliferation and a chondroid-lineage confound control; and PRMT5's measured GRG motif mapped onto the fusion protein against the two fusions the mechanism was measured in. ⏳ STILL OPEN AND STILL $0: a mode=panels re-fetch to populate the PRMT family, a fuller proliferation set and a genome-wide empirical null — all added to the panel definition on 2026-08-09 but not yet fetched. ⛔ The FOURTH cohort named originally was not read, and the decisive step for route 2 is now a stain rather than a lookup. |
| **MOD-AAV-GENE-THERAPY** — AAV and lentiviral gene therapy | `gene_and_cell_engineering` | ⏸ `parked_capability` | — |
| **MOD-APTAMER** — Aptamers | `nucleic_acid` | ⏸ `parked_capability` | — |
| **MOD-BASE-PRIME-EDITING** — Base and prime editing | `gene_and_cell_engineering` | ⏸ `parked_capability` | — |
| **MOD-EXOSOME** — Extracellular-vesicle delivery | `delivery_and_formulation` | ⏸ `parked_capability` | — |
| **MOD-LNP** — Lipid nanoparticles for oligonucleotide delivery | `delivery_and_formulation` | ⏸ `parked_capability` | — |
| **MOD-MACROCYCLE** — Macrocyclic small molecules for protein-protein interfaces | `ppi_and_undruggable` | ⏸ `parked_capability` | — |
| **MOD-MRNA-THERAPEUTIC** — mRNA therapeutics (non-vaccine) | `nucleic_acid` | ⏸ `parked_capability` | — |
| **MOD-PHOSPHATASE-RECRUIT** — Phosphatase- and enzyme-recruiting chimeras | `degrader_induced_proximity` | ⏸ `parked_capability` | — |

## The census

### Cytotoxic chemotherapy

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-ALKYLATOR**<br/>Alkylating agents | ifosfamide | ● `in_clinical_use` | · | on the record — [emc-clinical-registry.json](../../research/data/emc-clinical-registry.json) |
| **MOD-ANTHRACYCLINE**<br/>Anthracyclines | doxorubicin | ● `in_clinical_use` | · | on the record — [emc-clinical-registry.json](../../research/data/emc-clinical-registry.json) |
| **MOD-ANTIMETABOLITE**<br/>Antimetabolites | gemcitabine | ✕ `excluded` | ⭑ **new** | A sarcoma-wide later-line option with no EMC-specific series anywhere in the curated record. … |
| **MOD-DNA-MINOR-GROOVE**<br/>DNA minor-groove binders / fusion-TF displacers | trabectedin | ✓ `on_board` | · | [RT-TRABECTEDIN](L2-rt-trabectedin.md) — Trabectedin (± RT or combination) |
| **MOD-HYPOXIA-PRODRUG**<br/>Hypoxia-activated prodrugs | evofosfamide | ✕ `excluded` | · | [RT-HYPOXIA-PRODRUG](L2-rt-hypoxia-prodrug.md) — Hypoxia-activated prodrugs |
| **MOD-MICROTUBULE-DESTABILIZER**<br/>Microtubule-destabilising agents | eribulin | ✕ `excluded` | ⭑ **new** | Approved in a different sarcoma histology on a lineage-specific result that does not transfer to a fusion-driven myxoid tumour, and no EMC … |
| **MOD-MICROTUBULE-STABILIZER**<br/>Microtubule-stabilising agents | paclitaxel | ✕ `excluded` | ⭑ **new** | No EMC observation, and the mechanism is the most sharply mitosis-coupled in the cytotoxic set. … |
| **MOD-PLATINUM**<br/>Platinum agents | cisplatin | ✕ `excluded` | ⭑ **new** | No EMC-specific evidence exists, and the class holds no standing in soft-tissue sarcoma generally, so there is neither a disease-level nor a … |
| **MOD-RADIOMIMETIC**<br/>Radiomimetic cytotoxics | bleomycin | — `not_applicable` | ⭑ **new** | The class survives clinically in germ-cell and lymphoma regimens on histology-specific grounds with no soft-tissue-sarcoma instance to transfer from. |
| **MOD-TOPO1**<br/>Topoisomerase-I inhibitors | irinotecan | ✕ `excluded` | ⭑ **new** | No EMC report and no sarcoma-class standing that would license a transfer. The class couples its effect to proliferation rate, and EMC is a … |
| **MOD-TOPO2-NON-ANTHRA**<br/>Non-anthracycline topoisomerase-II inhibitors | etoposide | ✕ `excluded` | ⭑ **new** | Carries none of the anthracycline record that puts its sibling class in clinical use here, and no EMC observation exists. … |

### Hormonal and nuclear-receptor

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-AR-ANTAGONIST**<br/>Androgen-receptor antagonists and degraders | enzalutamide | ✕ `excluded` | ⭑ **new** | No androgen-receptor dependency is reported in EMC and none of the known 5′ partners is an androgen-responsive locus, so the partner-imports-an-input … |
| **MOD-AROMATASE**<br/>Aromatase inhibitors | letrozole | ✕ `excluded` | ⭑ **new** | Depletes a ligand for a receptor EMC has not been shown to depend on; the hormone-responsive-partner argument runs through the receptor itself rather … |
| **MOD-GLUCOCORTICOID**<br/>Glucocorticoids | dexamethasone | ✕ `excluded` | ⭑ **new** | Used across oncology for supportive and anti-oedema indications rather than as antitumour therapy in solid sarcoma, and no EMC-directed antitumour … |
| **MOD-GNRH**<br/>GnRH analogues | leuprolide | — `not_applicable` | ⭑ **new** | Acts by suppressing gonadal steroid output for tumours whose growth depends on it, and no such dependency is reported in this disease. |
| **MOD-NR-ORPHAN-AGONIST**<br/>Orphan nuclear-receptor agonism outside the NR4A family | NR2F1 agonists | ⭑ `candidate` | · | [RT-NR2F1](L2-rt-nr2f1.md) — Orphan nuclear-receptor agonism against dormancy escape |
| **MOD-NR4A-AGONIST**<br/>Direct NR4A-family agonism | 6-mercaptopurine | ✓ `on_board` | · | [RT-6MP](L2-rt-6mp.md) — 6-mercaptopurine / AF-1 agonism of the fusion |
| **MOD-PPARG-AGONIST**<br/>PPARγ agonists | pioglitazone | ✓ `on_board` | · | [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) — PPARG downstream-effector (repurpose TZDs) |
| **MOD-RETINOID**<br/>Retinoid differentiation therapy | all-trans retinoic acid | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-RXR-AGONIST**<br/>RXR heterodimer pharmacology | bexarotene | ✓ `on_board` | · | [RT-RXR](L2-rt-rxr.md) — RXR-heterodimer modulation of the fusion |
| **MOD-SERM-SERD**<br/>Selective oestrogen-receptor modulators and degraders | tamoxifen | ✕ `excluded` | · | [RT-HORMONE-PARTNER](L2-rt-hormone-partner.md) — Hormonal therapy for hormone-responsive 5′ fusion partners |
| **MOD-VDR**<br/>Vitamin-D receptor agonists | calcitriol | ✕ `excluded` | ⭑ **new** | No vitamin-D-receptor axis is reported in EMC, and the class has no sarcoma-level antitumour standing to transfer from. |

### Kinase inhibitors

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-ALK-ROS1**<br/>ALK / ROS1 inhibitors | brigatinib | ✕ `excluded` | ⭑ **new** | [RT-ALK-HIT](L2-rt-alk-hit.md) — Follow-up of the ALK/ROS1-class ex-vivo screen hit |
| **MOD-AURORA-PLK**<br/>Aurora kinase and PLK1 inhibitors | alisertib | ✕ `excluded` | ⭑ **new** | Mitotic kinases whose therapeutic index depends entirely on outpacing the host's proliferating compartments. … |
| **MOD-AXL**<br/>AXL inhibitors | bemcentinib | ✕ `excluded` | ⭑ **new** | No AXL dependency is reported in EMC, and the class's principal rationale is reversal of acquired resistance to a targeted agent this disease does … |
| **MOD-CDK46**<br/>CDK4/6 inhibitors | palbociclib | ✕ `excluded` | ⭑ **new** | Selects on a cell-cycle lesion -- CDKN2A loss, CDK4 amplification, an intact RB axis -- and none is reported in EMC's quiet genome. … |
| **MOD-CSF1R**<br/>CSF1R inhibitors | pexidartinib | ✕ `excluded` | ⭑ **new** | Approved in a sarcoma whose biology is a macrophage-recruiting autocrine loop. … |
| **MOD-DDR-KINASE**<br/>DNA-damage-response kinase inhibition (ATR, CHK1, WEE1) | ceralasertib | ✓ `on_board` | · | [RT-ATR-ASSESS](L2-rt-atr-assess.md) — The in-silico ATR vulnerability assessment (the computed … |
| **MOD-DNAPK**<br/>DNA-PK inhibition | peposertib | ⭑ `candidate` | · | [RT-DNAPK](L2-rt-dnapk.md) — DNA-PK inhibition as an indirect route to the fusion protein |
| **MOD-EGFR**<br/>EGFR inhibitors | cetuximab | ✕ `excluded` | ⭑ **new** | The repository's own differential expression read places EGFR below baseline in EMC with no selectivity signal, which was already decisive enough to … |
| **MOD-FGFR**<br/>FGFR inhibitors | erdafitinib | ✕ `excluded` | ⭑ **new** | Requires an activating fusion, mutation or amplification to select patients, and EMC's rearrangement is at a different locus entirely with no … |
| **MOD-HER2**<br/>HER2-directed inhibitors | trastuzumab | ✕ `excluded` | ⭑ **new** | No amplification or over-expression is reported in EMC, and the genome is quiet and clonal -- the profile in which a receptor amplification would be … |
| **MOD-IGF1R**<br/>IGF-1R inhibitors | teprotumumab | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-IMMUNE-KINASE**<br/>Immune-directed kinase inhibitors (HPK1, TBK1) | HPK1 inhibitors | ✕ `excluded` | ⭑ **new** | Designed to amplify an existing T-cell response. EMC's measured microenvironment is immune-cold with a low mutational burden, which is the registered … |
| **MOD-JAK-STAT**<br/>JAK / STAT inhibitors | ruxolitinib | ✕ `excluded` | ⭑ **new** | No JAK-STAT dependency is reported in EMC, and the class's solid-tumour rationale runs through inflammatory signalling that this tumour's cold, … |
| **MOD-KIT-PDGFR**<br/>KIT / PDGFR inhibitors | imatinib | ● `in_clinical_use` | · | on the record — [emc-clinical-registry.json](../../research/data/emc-clinical-registry.json) |
| **MOD-MAPK**<br/>RAS / RAF / MEK / ERK inhibitors | trametinib | ✕ `excluded` | ⭑ **new** | The class selects on an activating MAPK lesion. EMC's genome is quiet and clonal with a single founding translocation and no reported MAPK driver, so … |
| **MOD-MET**<br/>MET inhibitors | capmatinib | ✕ `excluded` | ⭑ **new** | MET appears in the surfaceome candidate list as expressed rather than as selective, and no MET alteration or dependency is reported in EMC. |
| **MOD-NTRK**<br/>NTRK inhibitors | larotrectinib | ✕ `excluded` | ⭑ **new** | The tumour-agnostic approval is conditioned on an NTRK fusion. EMC's driver is a rearrangement of a different gene, so the agnostic indication does … |
| **MOD-PI3K-AKT-MTOR**<br/>PI3K / AKT / mTOR inhibitors | everolimus | ✕ `excluded` | ⭑ **new** | The class has been tested broadly across soft-tissue sarcoma without establishing a histology this disease belongs to, and no PI3K-pathway lesion or … |
| **MOD-RET**<br/>RET-selective inhibitors | selpercatinib | ✕ `excluded` | · | [RT-RET](L2-rt-ret.md) — RET-selective inhibitors |
| **MOD-SGK1**<br/>SGK1 inhibition | SGK1 inhibitors | ⭑ `candidate` | · | [RT-SGK1](L2-rt-sgk1.md) — SGK1 inhibition |
| **MOD-SRC-BTK**<br/>SRC-family and BTK inhibitors | dasatinib | ✕ `excluded` | ⭑ **new** | Both act on signalling axes with no reported role in EMC; the BTK arm is a lymphoid-lineage class with no solid-sarcoma instance at all. |
| **MOD-TRANSCRIPTIONAL-CDK**<br/>Transcriptional CDK inhibition (CDK7, CDK9, CDK12/13) | CDK7 and CDK9 inhibitors | ✕ `excluded` | · | [RT-TXN-CDK](L2-rt-txn-cdk.md) — Transcriptional CDK dependency (CDK7, CDK9, CDK12/13) |
| **MOD-VEGF-MAB**<br/>Anti-VEGF antibodies and ligand traps | bevacizumab | ✕ `excluded` | ⭑ **new** | The antiangiogenic hypothesis in EMC is already carried by the multi-kinase inhibitors that hold its entire clinical record; … |
| **MOD-VEGFR-TKI**<br/>VEGFR / multi-kinase antiangiogenic inhibitors | pazopanib | ● `in_clinical_use` | · | on the record — [emc-clinical-registry.json](../../research/data/emc-clinical-registry.json) |

### Non-kinase enzyme inhibitors

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-BET**<br/>BET bromodomain inhibitors | BET inhibitors | ✓ `on_board` | · | [RT-HDAC-BET](L2-rt-hdac-bet.md) — HDAC / BET to lower fusion expression |
| **MOD-DNMT**<br/>DNA methyltransferase inhibitors | azacitidine | ⏸ `parked_capability` | · | Hypomethylating agents have a coherent rationale in fusion-driven tumours with quiet genomes. … |
| **MOD-EZH2**<br/>EZH2 / PRC2 inhibitors | tazemetostat | ✕ `excluded` | · | [RT-EZH2](L2-rt-ezh2.md) — EZH2 / PRC2 inhibition |
| **MOD-FASN**<br/>Fatty-acid synthase inhibitors | FASN inhibitors | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-GLUTAMINASE**<br/>Glutaminase inhibitors | telaglenastat | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-HDAC**<br/>Histone deacetylase inhibitors | romidepsin | ✓ `on_board` | · | [RT-HDAC-BET](L2-rt-hdac-bet.md) — HDAC / BET to lower fusion expression |
| **MOD-HSP90**<br/>HSP90 and chaperone inhibitors | HSP90 inhibitors | ⭑ `candidate` | · | [RT-CHAPERONE](L2-rt-chaperone.md) — Chaperone dependency of the chimera (HSP90 and … |
| **MOD-IDH**<br/>IDH inhibitors | ivosidenib | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-LSD1**<br/>LSD1 inhibitors | LSD1 inhibitors | ✕ `excluded` | ⭑ **new** | The class's solid-tumour rationale is lineage-specific to neuroendocrine differentiation, and EMC's reported neuroendocrine features are … |
| **MOD-MENIN**<br/>Menin-MLL inhibitors | revumenib | — `not_applicable` | ⭑ **new** | Selects on a specific leukaemic rearrangement class; the interaction it blocks has no reported role in soft-tissue sarcoma. |
| **MOD-NAMPT-DHODH**<br/>NAMPT and DHODH inhibitors | DHODH inhibitors | ✕ `excluded` | ⭑ **new** | Both starve a biosynthetic pathway whose demand scales with division rate. The class couples its effect to proliferation rate, and EMC is a … |
| **MOD-ODC**<br/>Ornithine decarboxylase inhibitors | eflornithine | ✕ `excluded` | ⭑ **new** | Its oncology use is maintenance in a MYCN-driven paediatric tumour, and polyamine demand tracks proliferation. … |
| **MOD-PARP**<br/>PARP inhibitors | olaparib | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-POLQ**<br/>POLθ inhibitors | POLQ inhibitors | ✕ `excluded` | ⭑ **new** | [RT-POLQ](L2-rt-polq.md) — POLθ inhibition (microhomology-mediated end joining) |
| **MOD-PRMT5-MAT2A**<br/>PRMT5 / MAT2A inhibitors (MTAP-deletion synthetic lethality) | MAT2A inhibitors | ⭑ `candidate` | ⭑ **new** | [RT-MTAP-PRMT5](L2-rt-mtap-prmt5.md) — PRMT5 / MAT2A synthetic lethality (MTAP co-deletion) |
| **MOD-PROTEASOME**<br/>Proteasome inhibitors | carfilzomib | ✓ `on_board` | · | [RT-CARFILZOMIB](L2-rt-carfilzomib.md) — Carfilzomib ± anthracycline (± venetoclax) |
| **MOD-SHP2**<br/>SHP2 allosteric inhibitors | SHP2 inhibitors | ✕ `excluded` | ⭑ **new** | An adaptor node downstream of receptor tyrosine kinases, used to deepen or rescue MAPK blockade. EMC has no MAPK lesion for it to be adjacent to. |
| **MOD-SYNTHETIC-LETHAL**<br/>Synthetic lethality and dependency-screen-derived targets | BRD9 / ncBAF degraders | ✓ `on_board` | · | [RT-SYNLETH-DEP](L2-rt-synleth-dep.md) — Synthetic-lethal / dependency partner (BRD9 / ncBAF via … |
| **MOD-USP1-KAT6**<br/>USP1 and KAT6 inhibitors | USP1 inhibitors | ✕ `excluded` | ⭑ **new** | Both select on lesions defined in other diseases -- homologous-recombination deficiency and a hormone-receptor-positive breast context -- neither of … |
| **MOD-WRN**<br/>WRN helicase inhibitors | WRN inhibitors | ✕ `excluded` | ⭑ **new** | Selects on microsatellite instability. EMC's genome is quiet, clonal and stable -- the opposite of the state this class requires. |
| **MOD-XPO1**<br/>Nuclear export (XPO1) inhibitors | selinexor | ✕ `already_rejected` | · | already ruled — [emerging-modalities-scan-emc.md](../../research/manuscripts/modality-census/emerging-modalities-scan-emc.md#5-briefly-considered-lower-priority) |

### Protein–protein interaction and “undruggable” chemistry

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-BCL2**<br/>BCL-2 inhibitors | venetoclax | ✓ `on_board` | · | [RT-CARFILZOMIB](L2-rt-carfilzomib.md) — Carfilzomib ± anthracycline (± venetoclax) |
| **MOD-CONDENSATE**<br/>Condensate-partitioning small molecules | condensate-partitioning agents | ✕ `already_rejected` | · | already ruled — [emc-post-degrader-options.md](../../research/manuscripts/program/emc-post-degrader-options.md#3b--the-technique-classes-searched-and-where-each-landed) |
| **MOD-COVALENT**<br/>Targeted covalent inhibitors and chemical probes | covalent cysteine ligands | ✓ `on_board` | · | [RT-COVALENT-PROBE](L2-rt-covalent-probe.md) — Covalent probe at C397 — as a REAGENT, not a drug |
| **MOD-DBD-LIGAND**<br/>DNA-binding-domain-directed small molecules | DNA-binding-domain ligands | ✓ `on_board` | · | [RT-DBD](L2-rt-dbd.md) — Target the DBD / DNA binding |
| **MOD-HIF2A**<br/>HIF-2α inhibitors | belzutifan | ✕ `excluded` | ⭑ **new** | The class is built for constitutive HIF-2α stabilisation caused by a specific tumour-suppressor loss. … |
| **MOD-IAP-SMAC**<br/>IAP antagonists / SMAC mimetics | SMAC mimetics | ✕ `excluded` | ⭑ **new** | The mechanism converts inflammatory cytokine signalling into cell death, so it needs a primed inflammatory context to convert. … |
| **MOD-KRAS**<br/>RAS inhibitors | sotorasib | — `not_applicable` | ⭑ **new** | Every agent in the class targets a specific mutant allele, and EMC has no reported RAS mutation. |
| **MOD-LC-DOMAIN-LIGAND**<br/>Ligands for low-complexity and prion-like domains | FET low-complexity ligands | ✓ `on_board` | · | [RT-FET-LC-LIGAND](L2-rt-fet-lc-ligand.md) — A ligand for the shared FET low-complexity half |
| **MOD-MACROCYCLE**<br/>Macrocyclic small molecules for protein-protein interfaces | macrocyclic PPI inhibitors | ⏸ `parked_capability` | ⭑ **new** | A chemotype that reaches interfaces conventional small molecules cannot, which is the right shape for this target -- and it runs into the same wall … |
| **MOD-MCL1-BCLXL**<br/>MCL-1 and BCL-xL inhibitors | MCL-1 inhibitors | ⭑ `candidate` | ⭑ **new** | [RT-APOPTOSIS-DEP](L2-rt-apoptosis-dep.md) — Anti-apoptotic dependency beyond BCL-2 (MCL-1, BCL-xL) |
| **MOD-MDM2-P53**<br/>MDM2 / MDMX antagonists (p53 reactivation) | MDM2 antagonists | ✕ `excluded` | ⭑ **new** | [RT-MDM2](L2-rt-mdm2.md) — MDM2 antagonism (p53 reactivation in a quiet genome) |
| **MOD-NOTCH-GSI**<br/>γ-secretase inhibitors / Notch pathway | nirogacestat | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-STAPLED-PEPTIDE**<br/>Stapled peptides and designed protein binders | RFdiffusion-class binders | ✕ `already_rejected` | · | already ruled — [emc-post-degrader-options.md](../../research/manuscripts/program/emc-post-degrader-options.md#3b--the-technique-classes-searched-and-where-each-landed) |
| **MOD-TEAD-YAP**<br/>TEAD / YAP inhibitors | TEAD palmitoylation inhibitors | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-TF-LBD-OCCUPANCY**<br/>Direct small-molecule occupancy of a transcription-factor ligand-binding domain | monovalent pocket modulators | ✓ `on_board` | · | [RT-MONOVALENT](L2-rt-monovalent.md) — Monovalent LBD pocket modulation  … |
| **MOD-TRAIL-DR5**<br/>Death-receptor agonists | DR5 agonists | ✕ `excluded` | ⭑ **new** | A class with a long record of clinical inactivity across solid tumours and no EMC-specific sensitising feature reported. |
| **MOD-WNT-BETA-CATENIN**<br/>Wnt / β-catenin pathway inhibitors | porcupine inhibitors | ✕ `excluded` | ⭑ **new** | ⛔ THIS EXCLUSION WAS ARGUED, NOT READ, AND THE READING CONTRADICTS ITS PREMISE (2026-08-09). … |

### Degraders and induced proximity

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-ANDGATE**<br/>AND-gate bivalent degraders (avidity coincidence detection) | AND-gate degraders | ✓ `on_board` | · | [RT-ANDGATE](L2-rt-andgate.md) — AND-gate bivalent degrader (avidity coincidence detection) |
| **MOD-AUTOPHAGY-DEGRADER**<br/>Autophagy-targeting chimeras (AUTAC, ATTEC, AUTOTAC) | ATTECs | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-DUBTAC**<br/>DUBTAC / targeted protein stabilisation | DUBTACs | ✕ `excluded` | ⭑ **new** | Stabilises a protein rather than removing it. The driver is a gain-of-function oncoprotein, so the direction of effect is wrong -- the same reasoning … |
| **MOD-LYTAC**<br/>LYTAC / lysosome-targeting chimeras | LYTACs | ✕ `excluded` | ⭑ **new** | The mechanism routes extracellular and membrane proteins to the lysosome. The driver here is a nuclear transcription factor, so the class cannot … |
| **MOD-MOLECULAR-GLUE**<br/>Molecular glue degraders | molecular glues | ✓ `on_board` | · | [RT-GLUE](L2-rt-glue.md) — Molecular glue instead of a PROTAC |
| **MOD-PHOSPHATASE-RECRUIT**<br/>Phosphatase- and enzyme-recruiting chimeras | phosphorylation-directed chimeras | ⏸ `parked_capability` | ⭑ **new** | Extends induced proximity to post-translational marks other than ubiquitin, which is an interesting fit for a transcription factor whose activity is … |
| **MOD-PROTAC**<br/>PROTAC / bivalent degraders | bivalent degraders | ✓ `on_board` | · | [RT-DEGRADER](L2-rt-degrader.md) — NR4A3-LBD PROTAC degrader |
| **MOD-RIBOTAC**<br/>RIBOTAC / RNase-recruiting small molecules | RIBOTACs | ✕ `already_rejected` | · | already ruled — [emc-post-degrader-options.md](../../research/manuscripts/program/emc-post-degrader-options.md#3b--the-technique-classes-searched-and-where-each-landed) |
| **MOD-RIPTAC**<br/>RIPTAC — bind the tumour protein, poison an essential one | RIPTACs | ✓ `on_board` | · | [RT-RIPTAC](L2-rt-riptac.md) — RIPTAC — bind the tumour protein, poison an essential one |
| **MOD-TCIP**<br/>Transcriptional chemical inducers of proximity | TCIPs | ✓ `on_board` | · | [RT-TCIP](L2-rt-tcip.md) — TCIP — transcriptional chemically-induced proximity on … |
| **MOD-TF-PROTAC**<br/>TF-PROTAC (oligonucleotide-directed degradation of a transcription factor) | TF-PROTACs | ✕ `excluded` | ⭑ **new** | An elegant fit on its face -- the targeting arm is the DNA element the transcription factor binds, which sidesteps needing a pocket ligand. … |
| **MOD-UBIQ-SELECTIVE**<br/>Fusion-selective ubiquitination at the transfer step | transfer-step discrimination | ✓ `on_board` | · | [RT-UBIQ-SELECTIVE](L2-rt-ubiq-selective.md) — Fusion-selective ubiquitination  … |

### Nucleic-acid therapeutics

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-APTAMER**<br/>Aptamers | aptamers | ⏸ `parked_capability` | ⭑ **new** | A folded oligonucleotide can in principle bind a protein surface no small molecule reaches, but the target is nuclear and aptamer delivery to an … |
| **MOD-GAPMER-ASO**<br/>Gapmer antisense oligonucleotides | gapmer ASOs | ✓ `on_board` | · | [RT-ASO](L2-rt-aso.md) — Fusion-junction ASO / siRNA (the deliverable) |
| **MOD-HYBRID-INTRON-ASO**<br/>Intron-directed antisense against the fusion pre-mRNA | intron-targeted ASOs | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#35--the-hybrid-intron) |
| **MOD-MIRNA**<br/>miRNA mimics and antagomirs | miRNA mimics | ✕ `excluded` | ⭑ **new** | Acts on networks rather than on a sequence, so it forfeits the one discriminating feature this disease offers -- and no EMC miRNA profile exists to … |
| **MOD-MRNA-THERAPEUTIC**<br/>mRNA therapeutics (non-vaccine) | therapeutic mRNA | ⏸ `parked_capability` | ⭑ **new** | Delivering a coding message -- a dominant-negative, a suicide enzyme, a decoy protein -- is a real format with no EMC instance. … |
| **MOD-RNA-EDITING**<br/>Programmable RNA base editing (ADAR recruitment) | ADAR-recruiting oligonucleotides | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-SARNA-CIRCRNA**<br/>Small activating RNA and circular RNA therapeutics | saRNA | ✕ `excluded` | ⭑ **new** | Both are up-regulating or durability formats. The therapeutic direction needed against a gain-of-function driver is removal, so the class is pointed … |
| **MOD-SIRNA**<br/>siRNA and RNAi | siRNA | ✓ `on_board` | · | [RT-ASO](L2-rt-aso.md) — Fusion-junction ASO / siRNA (the deliverable) |
| **MOD-SPLICE-SWITCH-ASO**<br/>Splice-switching antisense oligonucleotides | splice-switching ASOs | ✕ `excluded` | ⭑ **new** | A mechanistically distinct class from the gapmer route -- redirect splicing rather than degrade the transcript -- and it has never been named here. … |
| **MOD-TF-DECOY**<br/>Transcription-factor decoy oligonucleotides | NBRE decoy oligonucleotides | ✕ `excluded` | ⭑ **new** | Never named here, and it is the obvious idea for a DNA-binding driver: flood the cell with the response element so the transcription factor binds … |

### Gene and cell engineering

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-AAV-GENE-THERAPY**<br/>AAV and lentiviral gene therapy | AAV vectors | ⏸ `parked_capability` | ⭑ **new** | The delivery chassis three registered routes here already depend on, recorded as its own class so the dependency is visible as a modality gap and not … |
| **MOD-BASE-PRIME-EDITING**<br/>Base and prime editing | cytosine base editors | ⏸ `parked_capability` | ⭑ **new** | Distinct from the RNA-editing approach already ruled out here, and not covered by that ruling: a cytosine base editor can install a stop codon, which … |
| **MOD-CAS13**<br/>Cas13 RNA-targeting knockdown | Cas13 | ✓ `on_board` | · | [RT-CRISPR-CAS13](L2-rt-crispr-cas13.md) — CRISPR/Cas9 intron-targeted fusion disruption; … |
| **MOD-CAS9-GENOMIC**<br/>CRISPR nuclease disruption of the genomic fusion | Cas9 intron targeting | ✓ `on_board` | · | [RT-CRISPR-CAS13](L2-rt-crispr-cas13.md) — CRISPR/Cas9 intron-targeted fusion disruption; … |
| **MOD-EPIGENOME-EDITING**<br/>Epigenome editing (targeted transcriptional silencing) | dCas9-KRAB | ✕ `excluded` | ⭑ **new** | Never named here, and worth stating rather than leaving unexamined. Silencing the fusion means silencing a promoter, and the promoter belongs to the … |
| **MOD-ONCOLYTIC-BACTERIA**<br/>Oncolytic and engineered bacteria | engineered anaerobes | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-ONCOLYTIC-VIRUS**<br/>Oncolytic viruses | talimogene laherparepvec | ✕ `already_rejected` | · | already ruled — [emerging-modalities-scan-emc.md](../../research/manuscripts/modality-census/emerging-modalities-scan-emc.md#5-briefly-considered-lower-priority) |
| **MOD-RIBOZYME**<br/>Trans-splicing ribozymes | trans-splicing ribozymes | ✓ `on_board` | · | [RT-RIBOZYME](L2-rt-ribozyme.md) — Trans-splicing ribozyme → suicide gene, triggered by the … |
| **MOD-SYNPROMOTER**<br/>Fusion-responsive synthetic promoters | synthetic promoters | ✓ `on_board` | · | [RT-SYNPROMOTER](L2-rt-synpromoter.md) — Fusion-driven synthetic promoter → suicide gene |

### Antibodies and antibody-likes

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-ADC**<br/>Antibody-drug conjugates | trastuzumab deruxtecan | ✓ `on_board` | · | [RT-B7H3](L2-rt-b7h3.md) — B7-H3 (CD276) / CD56 → ADC, bispecific or CAR-T |
| **MOD-ALT-SCAFFOLD**<br/>Non-immunoglobulin binding scaffolds | nanobodies | ✕ `excluded` | ⭑ **new** | Nanobodies, DARPins and affibodies change size, penetration and manufacturing -- all real advantages in a matrix-dense tumour, and none of them an … |
| **MOD-AOC**<br/>Antibody-oligonucleotide conjugates | antibody-oligonucleotide conjugates | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-BITE**<br/>T-cell-engaging bispecific antibodies | T-cell engagers | ✓ `on_board` | · | [RT-B7H3](L2-rt-b7h3.md) — B7-H3 (CD276) / CD56 → ADC, bispecific or CAR-T |
| **MOD-IMMTAC**<br/>Soluble TCR bispecifics (ImmTAC) | brenetafusp | ✓ `on_board` | · | [RT-TCR-IMMTAC](L2-rt-tcr-immtac.md) — Fusion-junction TCR-T / soluble-TCR (ImmTAC) against the … |
| **MOD-IMMUNOCYTOKINE**<br/>Immunocytokines (tumour-targeted cytokine fusions) | antibody-cytokine fusions | ⭑ `candidate` | ⭑ **new** | [RT-IMMUNOCYTOKINE](L2-rt-immunocytokine.md) — Matrix-targeted immunocytokines |
| **MOD-MASKED-ANTIBODY**<br/>Masked / conditionally activated antibodies | probodies | ✕ `excluded` | ⭑ **new** | Widens the therapeutic margin of an antigen that is expressed in normal tissue too. … |
| **MOD-NAKED-MAB**<br/>Unconjugated monoclonal antibodies | rituximab-class antibodies | ✕ `excluded` | ⭑ **new** | The surfaceome screen returns no antigen that is both selectively enriched in EMC and restricted in normal tissue, so this class has no address to be … |
| **MOD-NK-ENGAGER**<br/>NK-cell engagers | NK-cell engagers | ✕ `excluded` | ⭑ **new** | Substitutes the effector population, which does not address the gate. The surfaceome screen returns no antigen that is both selectively enriched in … |
| **MOD-RADIOIMMUNOCONJUGATE**<br/>Radioimmunoconjugates | radiolabelled antibodies | ✕ `excluded` | ⭑ **new** | Swaps a cytotoxic payload for a radionuclide on the same targeting arm, so it inherits the antigen gate unchanged. … |
| **MOD-TRISPECIFIC**<br/>Trispecific and multispecific engagers | trispecific engagers | ✕ `excluded` | ⭑ **new** | Adds a costimulatory or second-targeting arm to the engager format. It changes the potency and the safety margin of an engagement, not the … |

### Cell therapy

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-ALLO-HSCT**<br/>Allogeneic haematopoietic stem-cell transplant | allogeneic HSCT | — `not_applicable` | ⭑ **new** | A graft-versus-tumour strategy with no role in adult soft-tissue sarcoma and toxicity that an indolent disease could not justify. |
| **MOD-CAR-M**<br/>CAR-macrophages | CAR-macrophages | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-CAR-NK**<br/>CAR-NK cells | CAR-NK | ✕ `excluded` | ⭑ **new** | Substitutes the effector to improve the safety profile; the gate is the antigen and the trafficking, both unchanged. … |
| **MOD-CAR-T-ALLOGENEIC**<br/>Allogeneic / off-the-shelf CAR-T | allogeneic CAR-T | ✕ `excluded` | ⭑ **new** | Changes the manufacturing economics, which matters enormously for an ultra-rare disease, and changes nothing about the antigen. … |
| **MOD-CAR-T-AUTOLOGOUS**<br/>Autologous CAR-T | CAR-T | ✓ `on_board` | · | [RT-CART-SURFACE](L2-rt-cart-surface.md) — CAR-T for EMC (surface-directed) |
| **MOD-GAMMA-DELTA-NKT**<br/>γδ T cells, NKT cells and virus-specific T cells | γδ T cells | ✕ `excluded` | ⭑ **new** | Innate-like effectors proposed for tumours where conventional T cells fail. They still have to enter the tumour, and EMC's infiltrate is sparse and … |
| **MOD-IN-VIVO-CAR-T**<br/>In vivo CAR-T | in vivo CAR-T | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-PAN-NR4A-EXVIVO**<br/>Ex-vivo transcription-factor modulation of a cell product | pan-NR4A modulation | ✓ `on_board` | · | [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md) — Ex-vivo pan-NR4A pole (CAR-T manufacturing additive) |
| **MOD-TCR-T**<br/>TCR-engineered T cells | engineered TCR-T | ✓ `on_board` | · | [RT-TCRT-CTA](L2-rt-tcrt-cta.md) — TCR-T / engineered T cells vs a cancer-testis antigen … |
| **MOD-TIL**<br/>Tumour-infiltrating lymphocyte therapy | TIL therapy | ✕ `already_rejected` | · | already ruled — [emerging-modalities-scan-emc.md](../../research/manuscripts/modality-census/emerging-modalities-scan-emc.md#5-briefly-considered-lower-priority) |

### Vaccines and active immunization

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-DC-VACCINE**<br/>Dendritic-cell vaccines | dendritic-cell vaccines | ✕ `excluded` | ⭑ **new** | Manufacturing-intensive per patient, which an ultra-rare disease can least support, and it presents the same epitopes the registered vaccine route … |
| **MOD-DNA-VACCINE**<br/>DNA vaccines | plasmid DNA vaccines | ✕ `excluded` | ⭑ **new** | A delivery variant of the same junction-epitope hypothesis already on the board, with weaker human immunogenicity data than the formats registered … |
| **MOD-IN-SITU-VACCINATION**<br/>In-situ vaccination (intratumoural priming) | intratumoural adjuvants | ✕ `excluded` | ⭑ **new** | The strategy is designed for cold tumours, which makes it look like a fit here -- and the fit fails for a specific reason worth recording. … |
| **MOD-PEPTIDE-RNA-VACCINE**<br/>Peptide and RNA cancer vaccines | neoantigen vaccines | ✓ `on_board` | · | [RT-VACCINE](L2-rt-vaccine.md) — Fusion-junction vaccine / HLA-coverage paper |
| **MOD-SHARED-ANTIGEN**<br/>Shared / off-the-shelf tumour antigens | shared fusion-junction epitopes | ✓ `on_board` | · | [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md) — Fusion-junction neoantigen (the antigen, shared by three … |
| **MOD-WHOLE-LYSATE**<br/>Whole-tumour-lysate and autologous cell vaccines | autologous lysate vaccines | ✕ `excluded` | ⭑ **new** | Relies on the tumour supplying a diverse antigen repertoire, and EMC's mutational burden is at the very bottom of the range. … |

### Immune modulation

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-ADENOSINE-AXIS**<br/>Adenosine-axis inhibitors (A2AR, CD73, CD39) | A2AR antagonists | ✕ `excluded` | ⭑ **new** | Relieves a suppressive metabolite brake on T cells that are present. EMC's measured microenvironment is immune-cold with a low mutational burden, … |
| **MOD-CD47-SIRPA**<br/>CD47-SIRPα and myeloid checkpoint inhibitors | anti-CD47 | ✕ `excluded` | ⭑ **new** | Acts through macrophage phagocytosis, and the repository's own reading is that translocation-associated sarcomas carry significantly lower macrophage … |
| **MOD-COSTIM-AGONIST**<br/>Costimulatory agonists (OX40, 4-1BB, GITR, CD40) | 4-1BB agonists | ✕ `excluded` | ⭑ **new** | Amplify an ongoing response. EMC's measured microenvironment is immune-cold with a low mutational burden, which is the registered permanent blocker … |
| **MOD-CTLA4**<br/>CTLA-4 inhibitors | ipilimumab | ✕ `excluded` | ⭑ **new** | Broadens an existing repertoire rather than creating one. EMC's measured microenvironment is immune-cold with a low mutational burden, which is the … |
| **MOD-IDO-TDO**<br/>IDO / TDO inhibitors | epacadostat | ✕ `excluded` | ⭑ **new** | A suppression-relief class whose randomised record in an immune-hot disease was negative, applied here to a cold one. … |
| **MOD-INTERFERON**<br/>Interferon-α | interferon-α | ● `in_clinical_use` | · | on the record — [emc-clinical-registry.json](../../research/data/emc-clinical-registry.json) |
| **MOD-MYELOID-REPROGRAM**<br/>Myeloid reprogramming (TREM2, MARCO and related) | anti-TREM2 | ✕ `excluded` | ⭑ **new** | Repolarises tumour macrophages toward an inflammatory phenotype. Same compartment problem as the myeloid checkpoints, plus it still requires a T-cell … |
| **MOD-NEXTGEN-CHECKPOINT**<br/>LAG-3, TIGIT and TIM-3 inhibitors | relatlimab | ✕ `excluded` | ⭑ **new** | Release brakes on T cells that have already recognised something. EMC's measured microenvironment is immune-cold with a low mutational burden, which … |
| **MOD-PD1-PDL1**<br/>PD-1 / PD-L1 checkpoint inhibitors | nivolumab | ✓ `on_board` | · | [RT-ICI-TKI](L2-rt-ici-tki.md) — Checkpoint inhibitor + anti-angiogenic TKI combination |
| **MOD-STING-TLR**<br/>Innate agonists (STING, TLR, RIG-I) | STING agonists | ✕ `excluded` | ⭑ **new** | Explicitly designed to convert cold tumours, so it deserves a stated reason rather than a blanket one. … |
| **MOD-SYSTEMIC-CYTOKINE**<br/>Systemic cytokine therapy (IL-2, IL-12, IL-15) | high-dose IL-2 | ✕ `excluded` | ⭑ **new** | Expands lymphocytes systemically with dose-limiting toxicity and no tumour address. … |
| **MOD-TGFB**<br/>TGF-β pathway inhibitors | TGF-β traps | ✕ `excluded` | ⭑ **new** | Proposed for immune-excluded tumours, which EMC is -- but the exclusion here is a physical chondroitin-sulfate gel rather than a TGF-β-driven … |
| **MOD-TREG-DEPLETION**<br/>Regulatory T-cell depletion | anti-CCR8 | ✕ `excluded` | ⭑ **new** | Removes suppression of an effector population that is sparse to begin with. EMC's measured microenvironment is immune-cold with a low mutational … |

### Tumour microenvironment and stroma

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-CD44-RHAMM**<br/>Hyaluronan-receptor-directed agents | anti-CD44 | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-CS-BIOSYNTHESIS**<br/>Inhibition of tumour glycosaminoglycan biosynthesis | glycosaminoglycan synthesis inhibitors | ✕ `excluded` | · | [RT-MATRIX-SYNTHESIS](L2-rt-matrix-synthesis.md) — Inhibition of the tumour's glycosaminoglycan biosynthesis |
| **MOD-FAP-DIRECTED**<br/>Fibroblast-activation-protein-directed agents | FAP inhibitors | ✓ `on_board` | · | [RT-FAP-RLT](L2-rt-fap-rlt.md) — FAP-targeted radioligand therapy (FAPI-RLT) |
| **MOD-HYALURONIDASE**<br/>Enzymatic matrix depletion | pegvorhyaluronidase alfa | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-INTEGRIN-MMP**<br/>Integrin and matrix-metalloproteinase inhibitors | cilengitide | ✕ `excluded` | ⭑ **new** | Both classes have large negative randomised records across solid tumours including sarcoma, and neither has an EMC-specific rationale that would … |
| **MOD-OFCS-VAR2CSA**<br/>Oncofetal chondroitin sulfate targeting | VAR2CSA-based conjugates | ⭑ `candidate` | · | [RT-MATRIX-ADDRESS](L2-rt-matrix-address.md) — Oncofetal chondroitin sulfate as a tumour address |
| **MOD-STROMAL-NORMALISATION**<br/>Stromal normalisation (LOX / LOXL2, FAK, angiotensin axis) | simtuzumab | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-VASCULAR-DISRUPTING**<br/>Vascular-disrupting agents | combretastatins | ✕ `excluded` | ⭑ **new** | Collapses established tumour vasculature, so its effect scales with how much vasculature there is, and EMC is reported hypovascular. … |

### Metabolic and dietary

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-ARGININE-DEPRIVATION**<br/>Arginine deprivation | pegylated arginine deiminase | ✕ `excluded` | · | [RT-ARGININE](L2-rt-arginine.md) — Arginine deprivation (ASS1-silenced tumours) |
| **MOD-ASPARAGINASE**<br/>Asparaginase | pegaspargase | ✕ `excluded` | ⭑ **new** | The same enzyme-silencing logic as arginine deprivation, but the sensitising defect is a lymphoid lineage property with no solid-sarcoma instance. |
| **MOD-DIETARY-RESTRICTION**<br/>Fasting-mimicking, ketogenic and amino-acid-restriction diets | fasting-mimicking diet | ✕ `excluded` | ⭑ **new** | The mechanism is differential stress resistance between fast-dividing tumour cells and normal tissue. … |
| **MOD-MICROBIOME**<br/>Microbiome modulation | faecal microbiota transplant | ✕ `excluded` | ⭑ **new** | Its evidence base is modulation of checkpoint-inhibitor response, and checkpoint inhibition has no single-agent foothold in EMC to modulate. |

### Radiopharmaceuticals and radiation

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-ALPHA-RLT**<br/>α-emitting radioligand therapy | actinium-225 conjugates | ✓ `on_board` | · | [RT-FAP-RLT](L2-rt-fap-rlt.md) — FAP-targeted radioligand therapy (FAPI-RLT) |
| **MOD-AUGER**<br/>Auger-electron emitters | iodine-125 conjugates | ✕ `excluded` | ⭑ **new** | Requires nuclear-proximal delivery per cell to achieve its very short range, which is the most cell-count-dependent of all radionuclide classes. … |
| **MOD-BETA-RLT**<br/>β-emitting peptide receptor radioligand therapy | lutetium-177 DOTATATE | ✓ `on_board` | · | [RT-SSTR2](L2-rt-sstr2.md) — SSTR2 / neuroendocrine theranostic |
| **MOD-BNCT**<br/>Boron neutron capture therapy | boronophenylalanine BNCT | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-BRACHYTHERAPY**<br/>Brachytherapy | interstitial brachytherapy | ⭑ `candidate` | · | [RT-RT-INTENSIFY](L2-rt-rt-intensify.md) — Radiotherapy intensification (particle therapy, … |
| **MOD-EBRT**<br/>External-beam radiotherapy | adjuvant external-beam radiotherapy | ● `in_clinical_use` | · | on the record — [emc-clinical-registry.json](../../research/data/emc-clinical-registry.json) |
| **MOD-FLASH**<br/>FLASH ultra-high-dose-rate radiotherapy | FLASH radiotherapy | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-PARTICLE-THERAPY**<br/>Proton and carbon-ion therapy | carbon-ion radiotherapy | ⭑ `candidate` | · | [RT-RT-INTENSIFY](L2-rt-rt-intensify.md) — Radiotherapy intensification (particle therapy, … |
| **MOD-RADIOEMBOLIZATION**<br/>Radioembolization and arterial radionuclide delivery | yttrium-90 microspheres | — `not_applicable` | ⭑ **new** | Delivered through a hepatic arterial supply for liver-dominant disease, and EMC's metastatic pattern is lung-predominant. |
| **MOD-RADIOPROTECTOR**<br/>Radioprotectors | amifostine | — `not_applicable` | ⭑ **new** | A normal-tissue toxicity intervention rather than an antitumour one; it changes the tolerable dose and nothing about the tumour. |
| **MOD-RADIOSENSITIZER**<br/>Radiosensitizers | concurrent chemoradiotherapy | ⭑ `candidate` | · | [RT-RT-INTENSIFY](L2-rt-rt-intensify.md) — Radiotherapy intensification (particle therapy, … |

### Physical, device and locoregional

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-CHEMOEMBOLIZATION**<br/>Transarterial chemoembolization and hepatic arterial infusion | transarterial chemoembolization | — `not_applicable` | ⭑ **new** | Selected by liver-dominant disease with an arterial supply to exploit; EMC's pattern is lung-predominant. |
| **MOD-ELECTROCHEMOTHERAPY**<br/>Electrochemotherapy and electroporation | electrochemotherapy | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-HIPEC**<br/>Intraperitoneal and intrathecal regional chemotherapy | HIPEC | — `not_applicable` | ⭑ **new** | Both compartments are selected by a metastatic pattern EMC does not have; its dissemination is haematogenous and lung-predominant. |
| **MOD-HYPERTHERMIA**<br/>Regional hyperthermia | regional hyperthermia | ⭑ `candidate` | · | [RT-RT-INTENSIFY](L2-rt-rt-intensify.md) — Radiotherapy intensification (particle therapy, … |
| **MOD-ILP**<br/>Isolated limb perfusion | TNF-α plus melphalan perfusion | ⭑ `candidate` | · | [RT-LIMB-PERFUSION](L2-rt-limb-perfusion.md) — Isolated limb perfusion for extremity disease |
| **MOD-INHALED-CHEMO**<br/>Inhaled and aerosolised cytotoxic therapy | inhaled cytotoxics | ⭑ `candidate` | ⭑ **new** | [RT-LUNG-DIRECTED](L2-rt-lung-directed.md) — Lung-directed local therapy (regional perfusion, inhaled … |
| **MOD-ISOLATED-LUNG-PERFUSION**<br/>Isolated lung perfusion and regional pulmonary delivery | isolated lung perfusion | ⭑ `candidate` | ⭑ **new** | [RT-LUNG-DIRECTED](L2-rt-lung-directed.md) — Lung-directed local therapy (regional perfusion, inhaled … |
| **MOD-NIR-PIT**<br/>Near-infrared photoimmunotherapy | NIR photoimmunotherapy | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-PDT**<br/>Photodynamic therapy | photodynamic therapy | ✕ `excluded` | ⭑ **new** | Distinct from the photoimmunotherapy already ruled out here, and it fails on the half of that ruling that is about physics rather than about the … |
| **MOD-SURGERY**<br/>Wide local excision and metastasectomy | R0 wide excision | ● `in_clinical_use` | · | [RT-SURGICAL-QUALITY](L2-rt-surgical-quality.md) — The first operation — margin status, unplanned excision and … |
| **MOD-THERMAL-ABLATION**<br/>Percutaneous ablation (radiofrequency, microwave, cryo, focused ultrasound) | percutaneous cryoablation | ⭑ `candidate` | · | [RT-LUNG-DIRECTED](L2-rt-lung-directed.md) — Lung-directed local therapy (regional perfusion, inhaled … |
| **MOD-TTFIELDS**<br/>Tumour-treating fields | alternating electric fields | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-WATCHFUL-WAITING**<br/>Observation and deferred intervention | active surveillance | ● `in_clinical_use` | · | [RT-SURVEILLANCE](L2-rt-surveillance.md) — Surveillance duration and interval as the intervention |

### Host-directed and repurposed non-oncology

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-ANTICOAGULANT**<br/>Anticoagulants and antiplatelet agents | low-molecular-weight heparin | ✓ `on_board` | ⭑ **new** | [RT-VTE-PROPHYLAXIS](L2-rt-vte-prophylaxis.md) — Venous thromboembolism in a lung-metastatic sarcoma … |
| **MOD-BONE-TARGETED**<br/>Bisphosphonates and RANKL inhibitors | denosumab | ✕ `excluded` | ⭑ **new** | Selected by skeletal metastasis, which is not EMC's dominant pattern; despite the name, this tumour is extraskeletal and disseminates to lung. |
| **MOD-COX2-ASPIRIN**<br/>COX-2 inhibitors and aspirin | celecoxib | ✕ `excluded` | ⭑ **new** | Its rationale is inflammation-driven tumour promotion, and EMC's microenvironment is sparse and non-inflamed. |
| **MOD-HERV-DARK-ANTIGEN**<br/>Endogenous retroviral and repeat-derived antigens | HERV-derived epitopes | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-REPURPOSED-NONONC**<br/>Repurposed non-oncology agents (metformin, statins, propranolol, antiparasitics, disulfiram) | metformin | ✕ `excluded` | ⭑ **new** | A large class with a common shape: preclinical breadth, no biomarker, and no randomised solid-tumour confirmation. … |
| **MOD-SCLEROMYXEDEMA-PHARM**<br/>Pharmacology borrowed from mucin-depositing non-cancer disease | IVIG, immunomodulatory imides | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-SENOLYTIC**<br/>Senolytics and pro-senescence therapy | dasatinib plus quercetin | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |

### Delivery, formulation and conjugates

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-BBB-CROSSING**<br/>Blood-brain-barrier-crossing delivery | BBB-penetrant carriers | — `not_applicable` | ⭑ **new** | Selected by central-nervous-system involvement, which is not a feature of EMC's metastatic pattern. |
| **MOD-EXOSOME**<br/>Extracellular-vesicle delivery | engineered exosomes | ⏸ `parked_capability` | ⭑ **new** | An alternative carrier for the same undelivered payloads, at an earlier stage of clinical maturity than the lipid formulations it would compete with. |
| **MOD-INTRATUMOURAL-DEPOT**<br/>Intratumoural depots and sustained-release implants | hydrogel depots | ✕ `excluded` | ⭑ **new** | Solves local exposure for an accessible mass, and EMC's clinical problem is disseminated metastatic disease that a local depot does not reach. |
| **MOD-LNP**<br/>Lipid nanoparticles for oligonucleotide delivery | lipid nanoparticles | ⏸ `parked_capability` | ⭑ **new** | The formulation that would carry the portfolio's oligonucleotide routes to a solid tumour, recorded as a class so the gate is visible as a modality … |
| **MOD-NANOPARTICLE**<br/>Nanoparticle, liposomal and albumin-bound formulations | liposomal doxorubicin | ✕ `excluded` | ⭑ **new** | Reformulation improves exposure and toxicity for an agent whose activity is already established. … |
| **MOD-PDC-SMDC**<br/>Peptide-drug and small-molecule-drug conjugates | peptide-drug conjugates | ✕ `excluded` | ⭑ **new** | Substitutes a smaller targeting arm for an antibody, which improves penetration in dense tissue and changes nothing about what there is to target. … |
| **MOD-POLYMER-CONJUGATE**<br/>Polymer-drug conjugates | polymer-drug conjugates | ✕ `excluded` | ⭑ **new** | Relies on passive retention in leaky vasculature, and EMC is reported hypovascular -- the tumour property the effect depends on. |
| **MOD-PRODRUG-ACTIVATED**<br/>Tumour-activated prodrugs (enzyme- and pH-triggered) | enzyme-activated prodrugs | ✕ `excluded` | ⭑ **new** | Requires a tumour-restricted activating condition. No such enzyme or gradient has been established in EMC. … |

### Treatment strategy and trial architecture

| class | exemplar | verdict | prior | where it lands |
|---|---|---|---|---|
| **MOD-ADAPTIVE-SCHEDULING**<br/>Adaptive and evolution-guided dosing | adaptive pazopanib scheduling | ⭑ `candidate` | · | [RT-SCHEDULING](L2-rt-scheduling.md) — Adaptive and metronomic scheduling of existing agents |
| **MOD-BASKET-ELIGIBILITY**<br/>Biomarker-defined basket eligibility | FET-fusion basket eligibility | ⭑ `candidate` | · | [RT-TRIAL-REACH](L2-rt-trial-reach.md) — Trial reachability and access pathways |
| **MOD-BESPOKE-ASO**<br/>Individualised bespoke antisense programmes | n-of-few bespoke ASO programmes | ✕ `already_rejected` | · | already ruled — [emc-unexplored-treatment-lanes.md](../../research/manuscripts/program/emc-unexplored-treatment-lanes.md#6--considered-and-rejected) |
| **MOD-BIOMARKER-STRATIFICATION**<br/>Biomarker-stratified treatment selection | fusion-partner stratification | ✓ `on_board` | · | [RT-PARTNER-STRAT](L2-rt-partner-strat.md) — NR4A3 5' fusion partner as a treatment-stratification … |
| **MOD-CHRONOTHERAPY**<br/>Chronotherapy | circadian-timed dosing | ✕ `excluded` | ⭑ **new** | Timing delivery to circadian rhythm optimises the tolerability of an agent with established activity, and this disease's problem is the activity … |
| **MOD-COMBINATION**<br/>Rational combination therapy | trabectedin plus a PPARγ agonist | ✓ `on_board` | · | [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) — Trabectedin + a PPARγ agonist (all approved drugs) |
| **MOD-ENDPOINT-REFRAME**<br/>Redefining the response endpoint | growth-modulation endpoints | ✓ `on_board` | · | [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) — Reframe the endpoint systemic-therapy trials are judged on |
| **MOD-EXPANDED-ACCESS**<br/>Expanded access, compassionate use and off-label registries | single-patient expanded access | ⭑ `candidate` | ⭑ **new** | [RT-TRIAL-REACH](L2-rt-trial-reach.md) — Trial reachability and access pathways |
| **MOD-METRONOMIC**<br/>Metronomic dosing | metronomic chemotherapy | ⭑ `candidate` | · | [RT-SCHEDULING](L2-rt-scheduling.md) — Adaptive and metronomic scheduling of existing agents |
| **MOD-N-OF-1**<br/>N-of-1 and single-patient trial design | n-of-1 designs | ✕ `excluded` | · | Probed by the 2026-08-07 sweep's ultra-rare trial-design query. That the census then excluded it on shared-driver grounds stands; … |
| **MOD-SEQUENCING**<br/>Treatment sequencing and line ordering | line-of-therapy ordering | ✕ `excluded` | · | [RT-SEQUENCING](L2-rt-sequencing.md) — Treatment sequencing and line ordering |

---

**Reading a verdict.** `already_rejected` means another document here owns the ruling and
this row only points at it — the argument is deliberately not restated, because a second
home for a reason is a reason that drifts. `excluded` means this census is the thing doing
the closing, so the argument lives in the row. See
[../taxonomy/modality.md](../taxonomy/modality.md) §4.

