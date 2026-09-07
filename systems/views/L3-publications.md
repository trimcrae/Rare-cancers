---
id: DOC-VIEW-L3
title: "L3 — publications: where every route ends"
level: L3
kind: generated
status: generated
generator: systems/systems_check.py
purpose: The terminal deliverable of every route, written or not — what each paper would claim, which routes feed it, and what is missing from the unwritten ones.
scope: Level 3. One row per publication endpoint; the science behind each row is on the route pages.
audience: ["maintainers", "autonomous research agents", "external reviewers"]
date: 2026-08-06
last_verified: 2026-08-06
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# L3 — publications: where every route ends

> **Every route in this portfolio ends in a paper.** With no wet lab and no clinic, the published
> record is the only channel by which any of this work reaches a patient — so the endpoint is a
> property of a route, not an afterthought, and a route that cannot name one is an activity
> rather than an option.
>
> **Nothing here asserts efficacy, safety, a therapeutic window or clinical readiness.** A claim
> below is what the paper would ESTABLISH, at the weight its instruments actually support.

**33 endpoints for 83 routes · 30 with a document · 3 unwritten.**

⭐ **An unwritten paper is a row here, and that is the reason this collection exists.** L3 and L4 are otherwise DOCUMENTS rather than graph rows ([ARCHITECTURE §3](../ARCHITECTURE.md#3--the-hierarchy)), on the sound grounds that copying a file's title into JSON creates a second home for a fact the file owns. That reasoning is intact — a row with a document carries no title and this page reads it back out of the file. What it did not cover is a paper that **does not exist yet**: it has no file, so it has no other home, and leaving it unmodelled made *“this route has no endpoint”* and *“this route's endpoint is not written yet”* look identical.

## The endpoints

*A `—` in the last column means a document exists. It does **not** mean the paper is finished or that the science in it holds — that question belongs to the route pages and their instruments, and this page is careful not to answer it by implication.*

| endpoint | state | aimed at | routes | what is still missing |
|---|---|---|---:|---|
| **PUB-ASO**<br/>[NR4A3 fusion-junction antisense gapmers for extraskeletal myxoid chondr…](../../research/manuscripts/aso/fusion-junction-aso-journal-article.md) | ◉ `posted_preprint` | `journal_submission` | 2 | — |
| **PUB-ANDGATE**<br/>[A coincidence-detection ("AND-gate") bivalent degrader for protein-leve…](../../research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-ATR**<br/>[The in-silico ATR vulnerability assessment for EMC](../../research/manuscripts/dependency/emc-atr-vulnerability-assessment.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-ATR-PANEL-ASK**<br/>[Transcript-level models of the NR4A3 fusions of extraskeletal myxoid ch…](../../research/manuscripts/dependency/emc-atr-collaborator-package.md) | ◐ `drafted` | `experimental_proposal` | 1 | — |
| **PUB-BIOMARKER-DEP**<br/>[Biomarker-selected therapeutic classes in an ultra-rare sarcoma — what …](../../research/manuscripts/dependency/emc-biomarker-selected-classes.md) | ◐ `drafted` | `preprint` | 5 | — |
| **PUB-CLOSED-ROUTES**<br/>[Seven routes closed on argument rather than on experiment — the negativ…](../../research/manuscripts/methods-record/closed-routes-negative-record.md) | ◐ `drafted` | `preprint` | 7 | — |
| **PUB-DEGRADER**<br/>[In silico design of a paralogue-favoured ligand for a cryptic NR4A3 poc…](../../research/manuscripts/degrader/nr4a3-degrader-paper.md) | ◐ `drafted` | `journal_submission` | 5 | — |
| **PUB-EMC-CLASSIFICATION**<br/>[One code, three diseases: what a registry cohort selected on ICD-O-3 mo…](../../research/manuscripts/care-delivery/emc-icdo-9231-classification.md) | ◐ `drafted` | `internal_note` | 2 | ⛔ IT WILL NOT BE. Closed 2026-08-23 on trimcrae's instruction: 'this is not a paper. … |
| **PUB-EMC-PROGRAM**<br/>[Attacking an "undruggable" fusion oncoprotein by computation alone: a d…](../../research/manuscripts/program/emc-treatment-roadmap.md) | ◐ `drafted` | `journal_submission` | 2 | — |
| **PUB-ENDPOINT**<br/>[Objective response and disease control on identical patients: what the …](../../research/manuscripts/endpoint/response-endpoint-indolent-tumours.md) | ◐ `drafted` | `journal_submission` | 1 | — |
| **PUB-FUSION-OUTPUT**<br/>[Almost every gene set reads higher in the index arm: a size-matched emp…](../../research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md) | ◐ `drafted` | `journal_submission` | 1 | — |
| **PUB-FUSION-PARTNER**<br/>[Fusion-variant stratification in EMC (EWSR1::NR4A3 vs TAF15::NR4A3) — a…](../../research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-HLA-COVERAGE**<br/>[Population coverage of a public EWSR1::NR4A3 fusion-neoantigen immunoth…](../../research/manuscripts/neoantigen/hla-coverage-emc.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-METHODS**<br/>[The failure record of a computation-only degrader program: what in-sili…](../../research/manuscripts/methods-record/degrader-methods-failure-record.md) | ◐ `drafted` | `journal_submission` | 1 | — |
| **PUB-MODALITY-CENSUS**<br/>[What oncology can do, and what reaches extraskeletal myxoid chondrosarc…](../../research/manuscripts/modality-census/cancer-modality-census.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-MONOVALENT**<br/>[The monovalent pocket-modulation route — a small molecule that only occ…](../../research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md) | ◐ `drafted` | `internal_note` | 1 | — |
| **PUB-MORTALITY-MECHANISM**<br/>[What kills patients with extraskeletal myxoid chondrosarcoma, and the s…](../../research/manuscripts/emc-mortality-mechanisms-paper.md) | ◐ `drafted` | `preprint` | 6 | — |
| **PUB-MTAP-PRMT5**<br/>[The PRMT5 methylosome in extraskeletal myxoid chondrosarcoma: a fusion-…](../../research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-NEOANTIGEN**<br/>[Targeting the EWSR1::NR4A3 fusion-junction neoantigen in extraskeletal …](../../research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md) | ◐ `drafted` | `preprint` | 2 | — |
| **PUB-REPURPOSING**<br/>[Existing drugs not yet reported in extraskeletal myxoid chondrosarcoma:…](../../research/manuscripts/repurposing/repurposing-hypotheses.md) | ◐ `drafted` | `preprint` | 3 | — |
| **PUB-STRATEGY-ARCH**<br/>[Eligible but unfindable — trials that admit an ultra-rare sarcoma while…](../../research/manuscripts/care-delivery/emc-trial-reachability.md) | ◐ `drafted` | `preprint` | 3 | — |
| **PUB-SURFACE-TARGETS**<br/>[Fixed-panel tissue RNA prioritization in extraskeletal myxoid chondrosa…](../../research/manuscripts/surface-targets/emc-tissue-rna-prioritization.md) | ◐ `drafted` | `preprint` | 6 | — |
| **PUB-SYNLETH**<br/>[Degrader vs. synthetic-lethal for EWSR1::NR4A3 EMC — a feasibility comp…](../../research/manuscripts/dependency/degrader-vs-synthetic-lethal.md) | ◐ `drafted` | `internal_note` | 1 | — |
| **PUB-TCIP**<br/>[The induced-interface floor that proximity design inherits from degrade…](../../research/manuscripts/tcip/tcip-induced-interface-preprint.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-TXN-DEPENDENCY**<br/>[Transcriptional and proteostatic dependency of a fusion transcription f…](../../research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md) | ◐ `drafted` | `preprint` | 2 | — |
| **PUB-VACCINE-PATH**<br/>[A fusion-junction vaccine in extraskeletal myxoid chondrosarcoma: what …](../../research/manuscripts/neoantigen/emc-vaccine-development-path.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-KINASE-LEADS**<br/>*Four kinase observations in extraskeletal myxoid chondrosarcoma that no…* | ◔ `outlined` | `preprint` | 4 | ⚠ ITS BLOCKER IS RETIRED — THE CONSOLIDATION IS DONE AND IT INVERTED THE PAPER. … |
| **PUB-LOCOREGIONAL**<br/>*Anatomical selectivity in an indolent, extremity-primary, lung-metastas…* | ◔ `outlined` | `preprint` | 4 | ⚠ ITS BLOCKER WAS HALF RIGHT, AND THE HALF IT GOT WRONG IS THE INTERESTING ONE. … |
| **PUB-MATRIX-ADDRESS**<br/>*The myxoid matrix as an address rather than an obstacle* | ◔ `outlined` | `preprint` | 4 | ⚠ ITS BLOCKER IS NOW RETIRED AND THE PAPER IS MOSTLY NEGATIVE. All four routes are graded as of 2026-08-09. … |
| **PUB-NR-OUTSIDE-NR4A3**<br/>*Nuclear-receptor pharmacology outside NR4A3 in a NR4A3-driven sarcoma* | ◔ `outlined` | `preprint` | 2 | ⚠ ITS BLOCKER IS RETIRED AND BOTH ROUTES ARE GRADED, BOTH NEGATIVELY, FOR DIFFERENT REASONS. The dormancy route is UNREAD  … |
| **PUB-CARE-DELIVERY**<br/>*What decides survival in extraskeletal myxoid chondrosarcoma, and what …* | ○ `unwritten` | `preprint` | 4 | ⚠ Superseded, retained (rule 1.2): "Its four contributing routes are registered and their evidence is cited but not yet extracted. … |
| **PUB-IPD-SURVIVAL**<br/>*A reconstructed patient-level survival dataset for extraskeletal myxoid…* | ○ `unwritten` | `preprint` | 1 | The paper is unwritten; the science for it now exists. ⚠ *Superseded, retained: "no published figure has been digitized into it yet."* One has  … |
| **PUB-PARKED-MODALITIES**<br/>*Five modalities parked on a capability that does not exist yet: what wo…* | ○ `unwritten` | `preprint` | 5 | Every route it would cover is parked on a technology nobody has, so the paper has no result to report and would be a horizon scan. … |

## What each one would claim

*One statement per endpoint, written so a reader can disagree with it. If this sentence cannot be written, there is no endpoint — there is an activity.*

### PUB-ASO — NR4A3 fusion-junction antisense gapmers for extraskeletal myxoid chondrosarcoma: reagents, test articles and a pre-registrable knockdown experiment

**◉ `posted_preprint` · aimed at `journal_submission` · [`research/manuscripts/aso/fusion-junction-aso-journal-article.md`](../../research/manuscripts/aso/fusion-junction-aso-journal-article.md)**

The NR4A3 fusion junction is the one tumour-exclusive feature of this disease at the RNA level, and two junction-spanning gapmers are named for synthesis against it: 5'-GGGCATATCATCAAAC-3' at EWSR1 exon 12 and 5'-GGGCATATCTTGTGTG-3' at TAF15 exon 6, the best available designs at the two most frequently reported breakpoints. They are what survives a screen that condemns most of the panel: 87 of 190 junction-spanning designs let a mature wild-type parent transcript pair their whole catalytic gap over at least ten contiguous base pairs, and for 61 the longest such duplex is against wild-type NR4A3 itself, and lengthening the catalytic gap raises the margin available only by conceding parent-paired gap DNA, for an arithmetic rather than an empirical reason. Five test articles are named — three engineered constructs and two fusion-positive patient-derived EMC models, the controls and pre-registrable decision threshold for the falsifying experiment are stated, and the design pipeline is released for breakpoints outside the panel. Delivery is named as an outstanding gate rather than assumed away, the named reagents carry stated parent-duplex and off-target loads, and nothing here has been synthesised or tested.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-DELIVERY** (`requires_future_technology`) — SYSTEMIC, antigen-dependent tumour delivery of an oligonucleotide or a vector — NOT delivery as such

| route | role | what it contributes |
|---|---|---|
| [RT-ASO](L2-rt-aso.md) — Fusion-junction ASO / siRNA (the deliverable) | `primary` | The junction design, the transcriptome-wide specificity screen, and delivery stated as the outstanding gate rather than assumed away. |
| [RT-ASO-ASK](L2-rt-aso-ask.md) — Junction knockdown + parental sparing in EMC lines ( | `contributing` | The decisive experiment, specified inside the paper and sent with it: junction knockdown with wild-type sparing in an EMC line. Without it the paper states a specificity result with no named way to falsify it at a bench. |

### PUB-ANDGATE — A coincidence-detection ("AND-gate") bivalent degrader for protein-level fusion-exclusivity in EWSR1::NR4A3 extraskeleta

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md`](../../research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md)**

Coincidence detection across both halves of the fusion is a design that would convert a paralogue-selectivity problem into an avidity problem — and it names precisely what does not exist for it to be built, which is a ligand for the EWSR1 half.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NOT-FUSION-SELECTIVE** (`fundamental_biological_limit`) — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)

| route | role | what it contributes |
|---|---|---|
| [RT-ANDGATE](L2-rt-andgate.md) — AND-gate bivalent degrader (avidity coincidence dete | `primary` | The coincidence-detection design and the statement of exactly what does not exist for it to be built. |

### PUB-ATR — The in-silico ATR vulnerability assessment for EMC

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/dependency/emc-atr-vulnerability-assessment.md`](../../research/manuscripts/dependency/emc-atr-vulnerability-assessment.md)**

A replication-stress vulnerability can be assessed for EMC by inheritance from its FET-fusion class, and the assessment states inside itself that class inheritance is not an EMC measurement — which is what makes it an assessment rather than a finding.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)
- **BLK-CLASS-INHERITANCE** (`insufficient_data`) — Class inheritance, not an EMC measurement — no NR4A3 fusion has been tested for the phenotype

| route | role | what it contributes |
|---|---|---|
| [RT-ATR-ASSESS](L2-rt-atr-assess.md) — The in-silico ATR vulnerability assessment (the comp | `primary` | The computed assessment itself, and the class-inheritance limit stated inside it rather than in a caveat section. |

### PUB-ATR-PANEL-ASK — Transcript-level models of the NR4A3 fusions of extraskeletal myxoid chondrosarcoma, and five pre-specified predictions for a DNA double-strand break recruitment assay

**◐ `drafted` · aimed at `experimental_proposal` · [`research/manuscripts/dependency/emc-atr-collaborator-package.md`](../../research/manuscripts/dependency/emc-atr-collaborator-package.md) · ships with **PUB-ATR****

Everything a group already running the FET-fusion DSB-recruitment assay would have to derive in order to add EMC as a fourth partner class is pre-built — constructs, controls, predicted outcomes and kill criteria fixed in advance — so the marginal cost of testing the assessment's prediction is the bench time and nothing else.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-WET-LAB** (`requires_external_collaboration`) — No wet lab and no collaborator — an ask needs a self-interested taker before its size matters

| route | role | what it contributes |
|---|---|---|
| [RT-ATR-PANEL](L2-rt-atr-panel.md) — The ATR-inhibitor cell panel in EMC lines (the ask) | `primary` | The costed panel design, its controls and its kill criteria — the half of the ATR question that no computation can supply. |

### PUB-BIOMARKER-DEP — Biomarker-selected therapeutic classes in an ultra-rare sarcoma — what the available expression data excludes

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/dependency/emc-biomarker-selected-classes.md`](../../research/manuscripts/dependency/emc-biomarker-selected-classes.md) · ships with **PUB-MODALITY-CENSUS****

Five therapeutic classes are selected by a molecular state rather than by a histology, every selecting feature is readable in expression data already public for this disease, and the useful output is which classes the data rules OUT rather than which it nominates. Four selecting features are absent; the fifth class survives because the instrument cannot reach its question rather than because the data was favourable. The four negatives are deliberately NOT reported as equally strong.

| route | role | what it contributes |
|---|---|---|
| [RT-APOPTOSIS-DEP](L2-rt-apoptosis-dep.md) — Anti-apoptotic dependency beyond BCL-2 (MCL-1, BCL-x | `contributing` | One of six biomarker-selected classes whose selecting feature is readable in expression data already public for this disease, and whose most useful output is exclusion. |
| [RT-ARGININE](L2-rt-arginine.md) — Arginine deprivation (ASS1-silenced tumours) | `contributing` | One of six biomarker-selected classes whose selecting feature is readable in expression data already public for this disease, and whose most useful output is exclusion. |
| [RT-EZH2](L2-rt-ezh2.md) — EZH2 / PRC2 inhibition | `contributing` | One of six biomarker-selected classes whose selecting feature is readable in expression data already public for this disease, and whose most useful output is exclusion. |
| [RT-MDM2](L2-rt-mdm2.md) — MDM2 antagonism (p53 reactivation in a quiet genome) | `contributing` | One of six biomarker-selected classes whose selecting feature is readable in expression data already public for this disease, and whose most useful output is exclusion. |
| [RT-POLQ](L2-rt-polq.md) — POLθ inhibition (microhomology-mediated end joining) | `contributing` | One of six biomarker-selected classes whose selecting feature is readable in expression data already public for this disease, and whose most useful output is exclusion. |

### PUB-CLOSED-ROUTES — Seven routes closed on argument rather than on experiment — the negative record of an EWSR1::NR4A3 route search

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/methods-record/closed-routes-negative-record.md`](../../research/manuscripts/methods-record/closed-routes-negative-record.md)**

A route can be closed rigorously without an experiment when the closure is definitional or is arithmetic over a fixed measured fact, and separating those permanent closures from the merely instrument-limited ones is what keeps a portfolio from re-litigating settled questions — with wild-type NR4A3 pharmacology failing to transfer to the chimera as the worked example.

| route | role | what it contributes |
|---|---|---|
| [RT-6MP](L2-rt-6mp.md) — 6-mercaptopurine / AF-1 agonism of the fusion | `contributing` | The worked example of wild-type pharmacology failing to transfer to a fusion, which is the single most reusable argument in the set. |
| [RT-DBD](L2-rt-dbd.md) — Target the DBD / DNA binding | `contributing` | The arithmetic-over-a-fixed-fact closure — the clearest case in the register of a route closed by measurement rather than by opinion. |
| [RT-EWSR1-PROTEIN](L2-rt-ewsr1-protein.md) — Target the EWSR1 half at the protein level | `contributing` | A definitional closure: the half of the fusion that is shared with normal cells cannot discriminate for the tumour. |
| [RT-FET-LC-LIGAND](L2-rt-fet-lc-ligand.md) — A ligand for the shared FET low-complexity half | `contributing` | The same definitional closure applied to the shared low-complexity region, which is what makes the pattern a class of argument rather than a one-off. |
| [RT-HDAC-BET](L2-rt-hdac-bet.md) — HDAC / BET to lower fusion expression | `contributing` | A definitional closure on lowering expression of a driver whose expression is not the discriminating feature. |
| [RT-RXR](L2-rt-rxr.md) — RXR-heterodimer modulation of the fusion | `contributing` | A closure resting on a published measurement rather than on argument, with the one observation that would reopen it named and scanned for. |
| [RT-SYNPROMOTER](L2-rt-synpromoter.md) — Fusion-driven synthetic promoter → suicide gene | `contributing` | A closure resting on a premise about this fusion's binding specificity — reopenable on an EMC dataset, and so the paper's example of a closure that is not permanent. |

### PUB-DEGRADER — In silico design of a paralogue-favoured ligand for a cryptic NR4A3 pocket

**◐ `drafted` · aimed at `journal_submission` · [`research/manuscripts/degrader/nr4a3-degrader-paper.md`](../../research/manuscripts/degrader/nr4a3-degrader-paper.md)**

A cryptic pocket on the NR4A3 ligand-binding domain can be found and a paralogue-favoured ligand designed into it by computation alone — and the selectivity margin that design would need is larger than the instruments used to predict it can currently resolve, which is reported as the result rather than worked around.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-PARALOGUE-DDG** (`requires_better_simulation_accuracy`) — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** (`requires_better_structure_prediction`) — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

| route | role | what it contributes |
|---|---|---|
| [RT-ASYMMETRIC](L2-rt-asymmetric.md) — Asymmetric selectivity — NR4A1-sparing mandatory, NR | `contributing` | The reframing that separates the two paralogue-sparing requirements instead of treating them as one. Every selectivity statement in the paper is sized against it, so dropping it lets a symmetric restatement back in. |
| [RT-COVALENT-PROBE](L2-rt-covalent-probe.md) — Covalent probe at C397 — as a REAGENT, not a drug | `contributing` | The NR4A3-unique cysteine and its reagent framing, together with the exposure instrument's failure against its own positive control — which is what stops the cysteine being reported as a selectivity result. |
| [RT-DEGRADER](L2-rt-degrader.md) — NR4A3-LBD PROTAC degrader | `primary` | The cryptic-pocket search, the designed paralogue-favoured ligand, and the margin arithmetic on which the paper's central negative rests. |
| [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md) — Ex-vivo pan-NR4A pole (CAR-T manufacturing additive) | `contributing` | The ex-vivo pole — the argument that this family's chemistry has a use that does not depend on solving paralogue selectivity. Without it the paper carries only the blocked application. |
| [RT-UBIQ-SELECTIVE](L2-rt-ubiq-selective.md) — Fusion-selective ubiquitination — discriminate at th | `contributing` | The categorical lysine inventory, carried as a disclosed-limitation supplement because no degradation-geometry claim may rest on a composed assembly. |

### PUB-EMC-CLASSIFICATION — One code, three diseases: what a registry cohort selected on ICD-O-3 morphology 9231/3 actually contains

**◐ `drafted` · aimed at `internal_note` · [`research/manuscripts/care-delivery/emc-icdo-9231-classification.md`](../../research/manuscripts/care-delivery/emc-icdo-9231-classification.md)**

ICD-O-3 morphology code 9231/3 is read by published work as THREE mutually incompatible populations — extraskeletal myxoid chondrosarcoma of soft tissue, a histological subtype of chondrosarcoma of bone, and an intracranial mesenchymal/meningeal tumour — because a morphology code carries no topography; SEER's own validation list has taken the skeletal reading unchanged since 2001; and the resulting contamination is MEASURED here for the first time. Of 595 records carrying 9231/3 in SEER 18 for 1988-2015, 404 had a soft-tissue and 191 a bone primary, so at least 32.1% of a morphology-only 9231/3 pull is bone — about 37.5% adjusted, with both identified biases pushing down. A cohort assembled by querying 9231/3 without a topography restriction, the standard construction in this literature, is not a soft-tissue cohort.

**Not written because:** ⛔ IT WILL NOT BE. Closed 2026-08-23 on trimcrae's instruction: 'this is not a paper. Document what we have, merge to main, and drop it.' The draft survives as a findings NOTE at `document` — same content, no author block, no deposit declarations, no venue, and removed from the prose-style gate's submission-text list. ⚠ WHAT WOULD REOPEN IT, stated so the number alone does not: evidence that the largest and most-cited EMC registry series (PMID 32856598) did NOT restrict on topography. That is the only finding that would give the measurement a consequence, and it needs that paper's Methods section, which is behind a subscription. Nothing else found here supplies one. ⚠ AND AN OVERCLAIM WAS CORRECTED ON THE WAY OUT: the draft asserted that querying without a topography restriction is 'the standard construction in this literature'. That was not supported by the corpus this work assembled, and trimcrae caught it. The note now says the opposite, which is what closed the route.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-REGISTRY-DUA** (`requires_authorization`) — Population cancer-registry microdata (SEER, NCDB) needs a signed data-use agreement

| route | role | what it contributes |
|---|---|---|
| [RT-DIAGNOSTIC-PATHWAY](L2-rt-diagnostic-pathway.md) — The diagnosis itself — code contamination and a name | `contributing` | The whole argument: one code read as two diseases, and a measured cost of diagnostic uncertainty. |
| [RT-POPULATION-REGISTRY](L2-rt-population-registry.md) — Population cancer-registry microdata (SEER, NCDB) | `contributing` | The measurement that would size the contamination the classification paper can currently only demonstrate. |

### PUB-EMC-PROGRAM — Attacking an "undruggable" fusion oncoprotein by computation alone: a driver-directed treatment program for EWSR1::NR4A3

**◐ `drafted` · aimed at `journal_submission` · [`research/manuscripts/program/emc-treatment-roadmap.md`](../../research/manuscripts/program/emc-treatment-roadmap.md)**

The gap in EMC care is categorical rather than a matter of degree — nothing in clinical use addresses the driver — and a computation-only program can enumerate the driver-directed routes, state a falsifiable kill criterion for each, and place the borrowed standard-of-care agents as context rather than as its own contribution.

| route | role | what it contributes |
|---|---|---|
| [RT-ICI-TKI](L2-rt-ici-tki.md) — Checkpoint inhibitor + anti-angiogenic TKI combinati | `context` | The comparator arm: the most consistently active class in EMC, cited to size the gap rather than analysed. Promoting it to a contribution would overstate what was done. |
| [RT-TRABECTEDIN](L2-rt-trabectedin.md) — Trabectedin (± RT or combination) | `context` | Cited to establish current care and the categorical gap. Explicitly not this program's contribution — it is clinical-evidence synthesis. ⛔ There is no single EMC response to overstate: the located record is 0 objective responses in 5 EMC patients across two series. |

### PUB-ENDPOINT — Objective response and disease control on identical patients: what the response summary discards across 552 trial arms

**◐ `drafted` · aimed at `journal_submission` · [`research/manuscripts/endpoint/response-endpoint-indolent-tumours.md`](../../research/manuscripts/endpoint/response-endpoint-indolent-tumours.md)**

An objective-response summary discards a large, measurable share of what a trial observed, and returns nothing at all in almost half of reported arms. Across 552 arms in 138 trials carrying a complete four-cell best-response table, the gap between disease control and objective response has a median of 39.4 percentage points (IQR 20.0-54.3), is identically the stable-disease proportion so each value carries an exact Wilson interval, holds in every constructible stratum (27.2-43.6), and reaches 50 points or more in 194 arms. 251 of 552 arms (45.5%) record zero objective responses, tracking the binomial at the corpus median rate, so an uninformative readout is largely a function of arm size rather than of the agent. Reporting is the binding constraint: of 2851 trials whose registry text names best overall response, 2715 (95.2%) post results without the four categories. Between 31.8% and 73.9% of conditions with a defined comparison have a median trial too small for an exact single-stage design; that is a BOUND rather than a point estimate because the accrual axis pools two populations biased in opposite directions. Remedies exist in four families across 12 disease domains, 7 with a consensus guideline and 5 on a single trial precedent, so the gap is diffusion rather than invention. Extraskeletal myxoid chondrosarcoma is the worked extreme at the 88.9th percentile, a weaker claim about that disease and a stronger one about endpoints. WITHDRAWN 2026-08-09: the zero-event-contour result and its named disease list, which came entirely from trials terminated for failure to accrue. It asserts no efficacy, safety or clinical readiness for any agent.

| route | role | what it contributes |
|---|---|---|
| [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) — Reframe the endpoint systemic-therapy trials are jud | `primary` | The whole paper: 552 arms re-read with both endpoints on one denominator, 44 conditions placed on the two coordinates that decide whether a response readout can work, the audit showing the remedy already exists in four families across 12 domains, and the limitations section that states the natural-history confound at full strength. |

### PUB-FUSION-OUTPUT — Almost every gene set reads higher in the index arm: a size-matched empirical null for small rare-tumour expression series, and what it leaves of the EWSR1::NR4A3 direct-target catalogue

**◐ `drafted` · aimed at `journal_submission` · [`research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md`](../../research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md)**

A gene-set read on a small rare-tumour expression series is uninterpretable until a size-matched random set drawn from the same platform's own genes has been scored beside it — and that calibration, which costs one seeded resampling and is not specific to any disease, refuses the very set this paper assembles. Applied to the EWSR1::NR4A3 direct-target catalogue (three genes across 2,276 retrieved full-text documents), the aggregate reaches 39% and 88% of its null threshold and does NOT clear, while the published EMC phenotype clears the same threshold 11.9-fold and 4.2-fold in the same run. Calibrated, the three genes separate rather than reading alike; the surviving gene is the pre-designated positive control and is therefore not an independent finding. No experiment has measured where an NR4A3 fusion binds, or what chromatin does, in EMC material — a negative the field's own habits sharpen, since it runs exactly that experiment for EWSR1::WT1, EWSR1::ATF1, EWSR1::FLI1, FUS::DDIT3 and (twice) HEY1::NCOA2 — so no gene named can yet be told apart from one merely associated with the disease, and the paper specifies the experiment that would settle it.

| route | role | what it contributes |
|---|---|---|
| [RT-FUSION-OUTPUT](L2-rt-fusion-output.md) — The fusion's transcriptional output, read in EMC tis | `primary` | The whole paper: the evidence-typed catalogue of every published NR4A3 / NR4A3-fusion transcriptional target with the verbatim sentence per gene, the size-matched empirical null that makes any gene-set read on these platforms interpretable, the four instrument controls, the three-cohort per-gene concordance reading with its ceiling, and the measured absence of any retrieved NR4A3-fusion cistrome. |

### PUB-FUSION-PARTNER — Fusion-variant stratification in EMC (EWSR1::NR4A3 vs TAF15::NR4A3) — a partner-stratified pooled synthesis

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md`](../../research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md)**

The NR4A3 5' fusion partner is a candidate - not established - treatment-stratification variable in EMC, and its two halves are in different states. On PROGNOSIS, pooling the two cohorts that publish event counts by partner (73 patients, two continents, no shared authors) gives a crude disease-specific death rate of 7/15 = 46.7% (95% CI 24.8-69.9) with TAF15::NR4A3 against 6/58 = 10.3% (4.8-20.8) with EWSR1::NR4A3 - a magnitude this contrast has never had - reported inseparably from the multivariable analysis in the larger of those cohorts, in which the partner is NOT independent of tumour size and 78% of TAF15 tumours exceed 10 cm, so the partner may be a marker for a big tumour rather than for a biology. On TREATMENT RESPONSE the record supports a DIRECTION and no magnitude at all, because the entire published TAF15::NR4A3 antiangiogenic-TKI experience is three to five patients with no reported responses and a 95% upper bound lying above the comparator arm's own point estimate; a zero-event arm yields no magnitude at any denominator, and nothing in the prognostic result bears on it. The review literature's metastasis claim is supported by neither count-bearing cohort in either direction. It makes no treatment recommendation and asserts no efficacy, safety, therapeutic window or clinical readiness for any agent.

| route | role | what it contributes |
|---|---|---|
| [RT-PARTNER-STRAT](L2-rt-partner-strat.md) — NR4A3 5' fusion partner as a treatment-stratificatio | `primary` | The whole paper: the pooled partner-stratified response, outcome and prevalence figures under one pre-committed method; the separation of the PROGNOSIS question, which now has a crude two-cohort magnitude, from the RESPONSE question, which has a zero-event arm and therefore no magnitude at any denominator; the size-adjustment result printed inseparably from the magnitude it defeats; the finding that the review literature's metastasis claim is unestablished in either direction once both count-bearing cohorts are in; the attribution correction on the field's most-quoted caveat; and the zero-patient-cost ask that follows. ⚠ Superseded, retained: 'the metastasis reversal in the only cohort with event counts' - that reversal was a single-cohort property and the second cohort does not reproduce it (2026-08-08). |

### PUB-HLA-COVERAGE — Population coverage of a public EWSR1::NR4A3 fusion-neoantigen immunotherapy in extraskeletal myxoid chondrosarcoma: a r

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/neoantigen/hla-coverage-emc.md`](../../research/manuscripts/neoantigen/hla-coverage-emc.md)**

If a public junction epitope were presented, the fraction of the patient population whose HLA alleles could see it is computable from reference allele frequencies — an eligibility ceiling that constrains every junction-directed immunotherapy route and is reusable independently of whether the epitope itself survives.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-ANTIGEN-COLD** (`fundamental_biological_limit`) — EMC is antigen-cold, and the fusion junction is a weak peptide-HLA

| route | role | what it contributes |
|---|---|---|
| [RT-VACCINE](L2-rt-vaccine.md) — Fusion-junction vaccine / HLA-coverage paper | `primary` | The population-coverage computation, which stands on its own as an eligibility ceiling even while the antigen above it is void. |

### PUB-METHODS — The failure record of a computation-only degrader program: what in-silico selectivity prediction could and could not establish

**◐ `drafted` · aimed at `journal_submission` · [`research/manuscripts/methods-record/degrader-methods-failure-record.md`](../../research/manuscripts/methods-record/degrader-methods-failure-record.md)**

A computation-only program can state, with its instruments' known-answer controls attached, exactly which of its selectivity claims its methods were able to support and which they were not — and the disclosed failures are the transferable result, because the field publishes almost none of them.

| route | role | what it contributes |
|---|---|---|
| [RT-METHODS-PAPER](L2-rt-methods-paper.md) — The honest methods paper on the degrader program's o | `primary` | The whole paper: the program's disclosed failures, each with the known-answer control that produced it. |

### PUB-MODALITY-CENSUS — What oncology can do, and what reaches extraskeletal myxoid chondrosarcoma — a modality census

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/modality-census/cancer-modality-census.md`](../../research/manuscripts/modality-census/cancer-modality-census.md)**

A complete enumeration of cancer-treatment modality classes, graded one line at a time against a single ultra-rare fusion sarcoma, separates the classes that were considered and dismissed from the classes nobody had pointed at — a distinction a literature search cannot make about itself, and one that changes which work is worth doing next.

| route | role | what it contributes |
|---|---|---|
| [RT-MODALITY-CENSUS](L2-rt-modality-census.md) — The modality census as a publication | `primary` | The paper is the census: a complete enumeration graded line by line against one disease, and the census-versus-search distinction that makes its negative half meaningful. |

### PUB-MONOVALENT — The monovalent pocket-modulation route — a small molecule that only occupies the NR4A3 LBD

**◐ `drafted` · aimed at `internal_note` · [`research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md`](../../research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md)**

Occupancy of the NR4A3 pocket without recruitment is a distinct route from degradation, and the question of whether occupancy alone changes the fusion's behaviour has never been asked by anyone — so the route is untested rather than refuted.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-R4-BINDS** (`requires_wet_lab`) — R4 — nothing is known to bind the cryptic pocket at all

| route | role | what it contributes |
|---|---|---|
| [RT-MONOVALENT](L2-rt-monovalent.md) — Monovalent LBD pocket modulation — a molecule that o | `primary` | The whole memo: that occupancy without recruitment is a separate question nobody has asked, and what a sized selectivity requirement for it would have to look like. |

### PUB-MORTALITY-MECHANISM — What kills patients with extraskeletal myxoid chondrosarcoma, and the survival available to tumour-directed therapy: a cause-of-death and relative-survival analysis of the published record

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/emc-mortality-mechanisms-paper.md`](../../research/manuscripts/emc-mortality-mechanisms-paper.md)**

In extraskeletal myxoid chondrosarcoma the published record does not state a mechanism for most recorded deaths; where it does, competing causes and second malignancies are the largest identifiable category and respiratory failure is not dominant. Between a fifth and a third of deaths after diagnosis are not attributed to the tumour -- a figure relative survival and registry cause attribution agree on despite sharing no input -- so the survival available to all antitumour therapy taken together is bounded at 6.7 percentage points in localised disease against 31.0 in metastatic disease.

| route | role | what it contributes |
|---|---|---|
| [RT-COMPETING-MORTALITY](L2-rt-competing-mortality.md) — Competing (non-EMC) mortality in a decade-scale coho | `contributing` | The arithmetic that bounds every other route in the portfolio: what a perfect antitumour therapy could add, and what it could not touch. |
| [RT-EARLY-PALLIATIVE](L2-rt-early-palliative.md) — Early specialist palliative care and structured symp | `contributing` | The intervention arm of the paper: the only non-antitumour class with randomised survival evidence, and an honest account of how far it can be carried to this disease. |
| [RT-HOST-FACTOR](L2-rt-host-factor.md) — Treating modifiable host conditions as de-facto EMC  | `contributing` | The constructive half of the paper: having bounded what antitumour therapy could achieve, name the interventions that act on the remainder and are already sitting in a pharmacy. |
| [RT-RESPIRATORY-FAILURE](L2-rt-respiratory-failure.md) — Progressive pulmonary metastatic burden and respirat | `contributing` | The mechanism half of the paper: what the terminal event actually is, quoted from the record rather than inferred from the metastatic pattern. |
| [RT-TREATMENT-HARM](L2-rt-treatment-harm.md) — De-escalating cytotoxic therapy that has no measured | `contributing` | The uncomfortable half of the argument: that part of the mortality this portfolio is trying to reduce may be iatrogenic, and that the cheapest intervention is to stop. |
| [RT-VTE-PROPHYLAXIS](L2-rt-vte-prophylaxis.md) — Venous thromboembolism in a lung-metastatic sarcoma  | `contributing` | A mechanism that is plausible, acute and probably small -- carried because a portfolio that only registers the mechanisms it expects to find is not a census. |

### PUB-MTAP-PRMT5 — The PRMT5 methylosome in extraskeletal myxoid chondrosarcoma: a fusion-class rationale that survives, an MTAP-locus rationale that does not, and two inexpensive tests

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md`](../../research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md) · ships with **PUB-MODALITY-CENSUS****

Two independent lines point at the PRMT5 methylosome in extraskeletal myxoid chondrosarcoma and neither has ever been examined in it. One of them closes on the paper's own data and is reported as the negative it is; the other survives and is argued rather than assumed — a peer-reviewed result in a second EWSR1-fusion sarcoma where PRMT5 inhibition acts in a fusion-DEPENDENT way, plus a sequence finding that PRMT5's measured substrate motif is absent from the half of EWSR1 every fusion retains and that the commonest EMC and clear cell fusions keep the same number of sites. The same analysis refuses the response prediction it looks like it licenses. Each route ends at a different inexpensive experiment, and the negative branch of each is worth publishing.

| route | role | what it contributes |
|---|---|---|
| [RT-MTAP-PRMT5](L2-rt-mtap-prmt5.md) — PRMT5 / MAT2A synthetic lethality (MTAP co-deletion) | `primary` | The route IS the paper: two independent routes into the same class, the confounds that could produce each reading without the underlying biology, and the two different cheap experiments that separate them. |

### PUB-NEOANTIGEN — Targeting the EWSR1::NR4A3 fusion-junction neoantigen in extraskeletal myxoid chondrosarcoma: a fusion-exclusive immunot

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md`](../../research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md)**

The fusion junction produces a peptide sequence that is absent from wild-type EWSR1 and wild-type NR4A3 — ⚠ the only novelty test in this repo compares against those two PARENT proteins (`fusion_breakpoints.py:231`) and NO proteome-wide search has ever been run, so 'absent from the normal proteome' is not a claim this work can make, and whether any allele presents it is a prediction that must be regenerated against a corrected exon index before it can be reported at all.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-ANTIGEN-COLD** (`fundamental_biological_limit`) — EMC is antigen-cold, and the fusion junction is a weak peptide-HLA

| route | role | what it contributes |
|---|---|---|
| [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md) — Fusion-junction neoantigen (the antigen, shared by t | `primary` | The junction peptide and its predicted-binding SCREEN, regenerated 2026-08-07 on the transcript model. The publishable finding is now partly NEGATIVE: no pan-EMC epitope, three of five junctions with no strong binder, and a public junction reaching under a tenth of patients. |
| [RT-TCR-IMMTAC](L2-rt-tcr-immtac.md) — Fusion-junction TCR-T / soluble-TCR (ImmTAC) against | `contributing` | The receptor-side delivery option for the junction epitope, and the measured weakness of the junction peptide-HLA that bounds it — a property of this junction rather than of the modality. |

### PUB-REPURPOSING — Existing drugs not yet reported in extraskeletal myxoid chondrosarcoma: a graded candidate menu from three independent generation methods

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/repurposing/repurposing-hypotheses.md`](../../research/manuscripts/repurposing/repurposing-hypotheses.md)**

Existing agents not yet reported in EMC can be mapped to EMC's molecular and microenvironmental axes by three independent methods, each candidate graded by an explicit evidence tier — a hypothesis-generating menu that asserts no efficacy for any agent it names.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

| route | role | what it contributes |
|---|---|---|
| [RT-CARFILZOMIB](L2-rt-carfilzomib.md) — Carfilzomib ± anthracycline (± venetoclax) | `primary` | The proteasome-inhibitor hypothesis and the ex-vivo EMC evidence behind it — the only ex-vivo EMC result in the portfolio, and currently the paper's weakest citation. |
| [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) — PPARG downstream-effector (repurpose TZDs) | `contributing` | The downstream-effector axis, carried with its direction flagged unresolved — scoped as unresolved and NOT refuted, which the paper must not conflate. |
| [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) — Trabectedin + a PPARγ agonist (all approved drugs) | `contributing` | The all-approved combination arm, held behind the same unresolved PPARγ direction that bounds the row above it. |

### PUB-STRATEGY-ARCH — Eligible but unfindable — trials that admit an ultra-rare sarcoma while listing conditions that never name it

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/care-delivery/emc-trial-reachability.md`](../../research/manuscripts/care-delivery/emc-trial-reachability.md)**

For a cancer that will never have a randomised trial, the variables a clinician actually controls — when, in what order, and whether the patient can reach a trial at all — are treatable as research questions, and a portfolio whose every endpoint is a publication needs the step after publication registered as a route.  ⚠ THE DRAFTED PAPER COVERS THE REACHABILITY VARIABLE ONLY. The endpoint's claim spans three variables — scheduling, sequencing and reachability — and the other two are now graded as closed (RT-SCHEDULING definitional, RT-SEQUENCING instrument_limit). Their findings are real and publishable (four medians that cannot be pooled by contract, four PFS figures circulating attributed to agents that did not produce them, and a refusal to pool that is itself the result) but they are NOT in the drafted manuscript yet. ⛔ Recorded here rather than left for a reader to discover, because `drafted` on an endpoint whose paper covers one of its three routes would otherwise read as more finished than it is.

| route | role | what it contributes |
|---|---|---|
| [RT-SCHEDULING](L2-rt-scheduling.md) — Adaptive and metronomic scheduling of existing agent | `contributing` | One of the variables a clinician actually controls in a cancer that will never have a randomised trial — when, in what order, and whether the patient can reach anything. |
| [RT-SEQUENCING](L2-rt-sequencing.md) — Treatment sequencing and line ordering | `contributing` | One of the variables a clinician actually controls in a cancer that will never have a randomised trial — when, in what order, and whether the patient can reach anything. |
| [RT-TRIAL-REACH](L2-rt-trial-reach.md) — Trial reachability and access pathways | `contributing` | One of the variables a clinician actually controls in a cancer that will never have a randomised trial — when, in what order, and whether the patient can reach anything. |

### PUB-SURFACE-TARGETS — Fixed-panel tissue RNA prioritization in extraskeletal myxoid chondrosarcoma

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/surface-targets/emc-tissue-rna-prioritization.md`](../../research/manuscripts/surface-targets/emc-tissue-rna-prioritization.md)**

A fixed panel of 11 therapeutic-address genes, with CHRNA6 as a separate established RNA-marker control, can be assessed using within-cohort tissue RNA ranks and prespecified sarcoma comparators. In the overlap-reduced Hofvander cohort of nine primary EMC specimens, CSPG4 alone meets the frozen tissue-validation allocation rule; its LGFMS contrast agrees with the original GSE24369 array contrast, but year-deletion sensitivity and DFSP context limit generalization. This supports a qualified rationale for EMC tissue protein and compartment validation, not validated surface expression, normal sparing, treatment selection or efficacy. All other fixed-panel results and discordant protein/normal-context evidence are retained.

| route | role | what it contributes |
|---|---|---|
| [RT-B7H3](L2-rt-b7h3.md) — B7-H3 (CD276) / CD56 → ADC, bispecific or CAR-T | `primary` | The prioritised surface-antigen ranking and the surrogate basis that bounds its negatives. |
| [RT-CART-SURFACE](L2-rt-cart-surface.md) — CAR-T for EMC (surface-directed) | `contributing` | The cell-product reading of the same ranking, and the finding that the constraint is the antigen and the stroma rather than the CAR. |
| [RT-FAP-RLT](L2-rt-fap-rlt.md) — FAP-targeted radioligand therapy (FAPI-RLT) | `contributing` | The stromal arm, which is the only row on the list that does not require the fusion biology to be solved and is also the least measured. |
| [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md) — PRAME-directed brenetafusp (ImmTAC) / PRAME CAR-TCR | `contributing` | The one antigen on the list whose therapeutic already exists clinically, which turns its row from a discovery into a check. |
| [RT-SSTR2](L2-rt-sstr2.md) — SSTR2 / neuroendocrine theranostic | `contributing` | The theranostic receptor arm, framed as a cheap decisive negative rather than as a lead — there is no computation that strengthens it, only a measurement. |
| [RT-TCRT-CTA](L2-rt-tcrt-cta.md) — TCR-T / engineered T cells vs a cancer-testis antige | `contributing` | The cancer-testis antigen arm ported from synovial sarcoma, downgraded on a measurement rather than on an argument. |

### PUB-SYNLETH — Degrader vs. synthetic-lethal for EWSR1::NR4A3 EMC — a feasibility comparison

**◐ `drafted` · aimed at `internal_note` · [`research/manuscripts/dependency/degrader-vs-synthetic-lethal.md`](../../research/manuscripts/dependency/degrader-vs-synthetic-lethal.md)**

A BRD9/ncBAF dependency is the best-motivated synthetic-lethal candidate for a FET fusion, and the negative recorded here is bounded by a transfer prior over a single cell line — a statement about the available data, not about the biology.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

| route | role | what it contributes |
|---|---|---|
| [RT-SYNLETH-DEP](L2-rt-synleth-dep.md) — Synthetic-lethal / dependency partner (BRD9 / ncBAF  | `primary` | The BRD9/ncBAF dependency argument, and the data-bounded negative that follows from a transfer prior over one cell line. |

### PUB-TCIP — The induced-interface floor that proximity design inherits from degraders is about twice the interface of the one solved transcriptional CIP

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/tcip/tcip-induced-interface-preprint.md`](../../research/manuscripts/tcip/tcip-induced-interface-preprint.md)**

⛔ NOT AN EMC-SPECIFIC RESULT — DEMOTED 2026-08-07, MEASURED RATHER THAN JUDGED. 'NR4A3' appears 0 times in nr4a3-induced-interface-census.json and 0 times in tcip-interface-floor-sizing.md; '8XTT', NR4A3's only experimental structure, appears 0 times in either OR in nr4a3-tcip-reach.json. Both load-bearing results are free of NR4A3: the 6-7-contact measurement is on 9MZA, a BCL6-p300 lymphoma system, and the 6-of-15 calibration is over published degrader/glue ternaries, none of them NR4A3. The reach enumeration IS NR4A3-anchored but names it three times, all caveats. THE CLAIM IS MODALITY-GENERAL AND THE EMC ANCHOR IS THE SETTING IT WAS COMPUTED IN. THE CLAIM ITSELF: the min_contact_residues floor that induced-proximity tooling applies by default is inherited from degraders; ablating it INVERTS the single-domain/multi-subunit acceptance ratio (0.896 at 12 -> 1.121 at 6 -> 1.254 at 0), so a size penalty read off that floor is an artefact of the wrong modality's parameter; the only deposited chemically-induced TRANSCRIPTIONAL-proximity complex (PDB 9MZA, 2.1 A) has an induced interface of 6-7 contacts across 4 residues per side, roughly half the floor; and the floor is too strict even at home, rejecting 6 of 15 published degrader/glue ternaries. ⚠ WHAT IT MAY NOT CLAIM: the size contrast itself does NOT survive a re-draw (within-class spread exceeds between-class contrast in 8 of 8 rungs), n=1 bounds the floor from ABOVE only, and 'ADMITS' is an excluded-volume statement no tested body has ever failed. ⚠ SUPERSEDED, RETAINED: the prior claim was framed as 'Transcriptional chemically-induced proximity on EWSR1::NR4A3', which implied a disease-specific deliverable it does not carry.

| route | role | what it contributes |
|---|---|---|
| [RT-TCIP](L2-rt-tcip.md) — TCIP — transcriptional chemically-induced proximity  | `primary` | The reach enumeration with an effector-size second terminus, reusing machinery MEASURED to be E3-free (4 of 4 arms byte-identical with every E3-specific field stripped). Run 2026-08-06 (ART-TCIP-REACH). Its reportable finding is not the binary admit — which admits every body tested, including a 1183-residue CRBN-DDB1 assembly — but that the size penalty is a degrader's induced-interface floor rather than steric bulk: ablating the floor inverts the sign. It speaks about a SIZE CLASS, not a named effector. |

### PUB-TXN-DEPENDENCY — Transcriptional and proteostatic dependency of a fusion transcription factor — what a no-wet-lab program can and cannot establish

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md`](../../research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md) · ships with **PUB-MODALITY-CENSUS****

A fusion oncoprotein whose entire mechanism is transactivation, and whose structure is a chimera of two domains that never evolved together, predicts dependencies on the transcriptional machinery and on the chaperone system — and for both, ABUNDANCE AND DEPENDENCY DISAGREE IN OPPOSITE DIRECTIONS. The transcriptional half is the most concordant elevation in the census and closes completely on dependency, being pan-essential with no selectivity. The chaperone half is an internally contradictory elevation that survives weakly for a reason abundance alone could not show. Reading only the first axis would have given a confident and wrong answer in both cases, which is the transferable result.

| route | role | what it contributes |
|---|---|---|
| [RT-CHAPERONE](L2-rt-chaperone.md) — Chaperone dependency of the chimera (HSP90 and co-ch | `primary` | The half of the paper that argues from what the driver IS STRUCTURALLY: a chimera of two domains that never evolved together is a folding problem before it is a signalling one. |
| [RT-TXN-CDK](L2-rt-txn-cdk.md) — Transcriptional CDK dependency (CDK7, CDK9, CDK12/13 | `primary` | The half of the paper that argues from what the driver IS: a transcriptional oncoprotein should be more dependent on the transcriptional machinery than the cell it sits in. |

### PUB-VACCINE-PATH — A fusion-junction vaccine in extraskeletal myxoid chondrosarcoma: what can be established today, and the capabilities that would change it

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/neoantigen/emc-vaccine-development-path.md`](../../research/manuscripts/neoantigen/emc-vaccine-development-path.md)**

That the obstacles between the EWSR1::NR4A3 junction and a therapeutic vaccine are separable and individually falsifiable, and that several of the figures the route has been graded on are properties of the screen rather than of the tumour: predicted class I coverage moves with the allele panel and moves to zero at a 0.125-unit change in an undefended acceptance threshold. It reports two results — that seam-proximal peptides of four of the five in-frame junctions reproduce a normal NR4A3 isoform sequence, withdrawing one predicted binder and exposing an isoform-blind novelty filter; and that the class II arm is negative on the three DRB1 alleles tested while bounding the general availability of helper epitopes hardly at all. It also observes, of this programme's own route ledger and not of the field, that several priming-directed classes were excluded for want of antigen supply while a vaccine is an antigen supply, so the combination was never graded here as a unit. No efficacy, safety, presentation or immunogenicity claim is made.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-ANTIGEN-COLD** (`fundamental_biological_limit`) — EMC is antigen-cold, and the fusion junction is a weak peptide-HLA
- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

| route | role | what it contributes |
|---|---|---|
| [RT-VACCINE-COMBINATION](L2-rt-vaccine-combination.md) — Junction vaccine on a checkpoint and antiangiogenic  | `primary` | The blocker ledger, the staged path and the explicit falsifiers, plus the observation that the standing negative was reached by grading the vaccine alone. |

### PUB-KINASE-LEADS — Four kinase observations in extraskeletal myxoid chondrosarcoma that nobody followed up

**◔ `outlined` · aimed at `preprint`**

Four kinase-directed observations specific to this disease exist in the published and curated record — one reported as expressed and activated, one positive across a small series with an internal control, one an interaction curated on the driver protein itself, one an ex-vivo screen hit — and none has been followed up by anyone, in a disease with no targeted agent.

**Not written because:** ⚠ ITS BLOCKER IS RETIRED — THE CONSOLIDATION IS DONE AND IT INVERTED THE PAPER. All four leads are graded as of 2026-08-09, and reading each one's own primary record demoted THREE of them in ways the leads' prose did not predict: the activation claim behind the strongest lead is a single paywalled abstract sentence with no recoverable denominator, and the approved agents address a molecular state this disease is not reported to be in; the screen hit turns out to sit beside two same-class hits belonging to a class the board already holds, and its named kinases have no probe on either platform so the arrays could never have attributed it; the interaction lead was measured on wild-type protein in a non-sarcoma tissue from one source. The fourth is discordant on the kinase and concordant on its substrate. ⭐ THAT IS THE PAPER NOW, and it is a better one than the consolidation that was planned: four EMC-specific kinase observations that the field has cited or left for one to two decades, each traced to what was actually measured, with the gap between the citation and the measurement stated. ⛔ Superseded, retained: "the consolidation has not been done — three of the four were surfaced two days before this endpoint was registered." ⚠ Two of the four gradings came from records that had been committed since 2026-08-07 and that the routes were registered without reading.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

| route | role | what it contributes |
|---|---|---|
| [RT-ALK-HIT](L2-rt-alk-hit.md) — Follow-up of the ALK/ROS1-class ex-vivo screen hit | `contributing` | One of four kinase observations specific to this disease that exist in the published or curated record and that nobody has followed up. |
| [RT-DNAPK](L2-rt-dnapk.md) — DNA-PK inhibition as an indirect route to the fusion | `contributing` | One of four kinase observations specific to this disease that exist in the published or curated record and that nobody has followed up. |
| [RT-RET](L2-rt-ret.md) — RET-selective inhibitors | `contributing` | One of four kinase observations specific to this disease that exist in the published or curated record and that nobody has followed up. |
| [RT-SGK1](L2-rt-sgk1.md) — SGK1 inhibition | `contributing` | One of four kinase observations specific to this disease that exist in the published or curated record and that nobody has followed up. |

### PUB-LOCOREGIONAL — Anatomical selectivity in an indolent, extremity-primary, lung-metastasising sarcoma

**◔ `outlined` · aimed at `preprint`**

A disease that is extremity-primary, lung-metastasis-dominant and slow enough for local control to matter is unusually well matched to locoregional and radiation-based treatment, and a portfolio containing no physical intervention at all had never assessed any of it.

**Not written because:** ⚠ ITS BLOCKER WAS HALF RIGHT, AND THE HALF IT GOT WRONG IS THE INTERESTING ONE. The arithmetic ran on 2026-08-09 under the repository's binding pooling contract, and it splits cleanly: the SIZE OF THE PROBLEM is computable and now computed — roughly a third of localised patients develop distant disease and a substantial minority recur locally, each pooled over three or four non-overlapping series with its heterogeneity range shown. ⛔ But the ELIGIBILITY criteria are not extractable, because they were never curated: no cohort carries a primary anatomical site field, metastatic site appears once in free text rather than as data, and no cohort records lesion burden or time-to-metastasis. So the paper has its denominator and not its numerator. ⭐ That is still writable and is arguably a better paper: the argument, the sized problem, and an explicit statement of which single curation step would convert it into an eligible fraction — which is $0 for the open-access series. ⛔ Superseded, retained: "the eligibility arithmetic has not been extracted from the curated cohorts yet", which reads as though extraction were the missing step. For two of the three quantities no extraction could have produced them.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

| route | role | what it contributes |
|---|---|---|
| [RT-LIMB-PERFUSION](L2-rt-limb-perfusion.md) — Isolated limb perfusion for extremity disease | `contributing` | One of the anatomical-selectivity strategies a disease that is extremity-primary, lung-metastasis-dominant and indolent is unusually well matched to. |
| [RT-LUNG-DIRECTED](L2-rt-lung-directed.md) — Lung-directed local therapy (regional perfusion, inh | `contributing` | One of the anatomical-selectivity strategies a disease that is extremity-primary, lung-metastasis-dominant and indolent is unusually well matched to. |
| [RT-MDT-LUNG](L2-rt-mdt-lung.md) — Metastasis-directed ablative radiotherapy to lung me | `contributing` | The one anatomical-selectivity strategy in this family that has actually been delivered to patients with this disease, and the reappraisal showing why the evidence said to rule it out was never about it. |
| [RT-RT-INTENSIFY](L2-rt-rt-intensify.md) — Radiotherapy intensification (particle therapy, brac | `contributing` | One of the anatomical-selectivity strategies a disease that is extremity-primary, lung-metastasis-dominant and indolent is unusually well matched to. |

### PUB-MATRIX-ADDRESS — The myxoid matrix as an address rather than an obstacle

**◔ `outlined` · aimed at `preprint`**

The matrix that defines this tumour histologically has been treated in the therapeutic literature almost entirely as a barrier to drug delivery, and it admits at least three distinct handles — an epitope, a biosynthetic pathway and a hypoxic niche — none of which requires the fusion protein to be druggable.

**Not written because:** ⚠ ITS BLOCKER IS NOW RETIRED AND THE PAPER IS MOSTLY NEGATIVE. All four routes are graded as of 2026-08-09. Three of the three handles the title argues for came back unfavourable or unreachable: the biosynthetic premise is not supported as stated, the hypoxia grade was WITHDRAWN the same day it was issued once the confound audit restricted the signature to one platform, and the epitope route's own nominated read gives no capacity support. The fourth is present-but-not-selective and its address is a splice variant a gene-level probe cannot see. ⭐ What makes it still worth writing is that two of the four are UNREACHABLE rather than refuted — the address is a sulfation pattern and an isoform, and neither has a gene — which is a statement about the instrument the field has for glycan and isoform addresses, not only about this disease. ⛔ Superseded, retained: "the expression read that would ground it is committed but ungraded."

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

| route | role | what it contributes |
|---|---|---|
| [RT-HYPOXIA-PRODRUG](L2-rt-hypoxia-prodrug.md) — Hypoxia-activated prodrugs | `contributing` | One of the handles the matrix offers — an epitope, a biosynthetic pathway or a hypoxic niche — none of which requires the fusion protein to be druggable. |
| [RT-IMMUNOCYTOKINE](L2-rt-immunocytokine.md) — Matrix-targeted immunocytokines | `contributing` | One of the handles the matrix offers — an epitope, a biosynthetic pathway or a hypoxic niche — none of which requires the fusion protein to be druggable. |
| [RT-MATRIX-ADDRESS](L2-rt-matrix-address.md) — Oncofetal chondroitin sulfate as a tumour address | `contributing` | One of the handles the matrix offers — an epitope, a biosynthetic pathway or a hypoxic niche — none of which requires the fusion protein to be druggable. |
| [RT-MATRIX-SYNTHESIS](L2-rt-matrix-synthesis.md) — Inhibition of the tumour's glycosaminoglycan biosynt | `contributing` | One of the handles the matrix offers — an epitope, a biosynthetic pathway or a hypoxic niche — none of which requires the fusion protein to be druggable. |

### PUB-NR-OUTSIDE-NR4A3 — Nuclear-receptor pharmacology outside NR4A3 in a NR4A3-driven sarcoma

**◔ `outlined` · aimed at `preprint`**

Two nuclear-receptor routes exist in this disease that do not act on its own receptor — one where a 5′ fusion partner imports a druggable transcriptional input, and one targeting dormancy through a receptor that has the published tool compound this program's own receptor never had.

**Not written because:** ⚠ ITS BLOCKER IS RETIRED AND BOTH ROUTES ARE GRADED, BOTH NEGATIVELY, FOR DIFFERENT REASONS. The dormancy route is UNREAD — its receptor has no probe on either readable platform, an instrument limit that no further expression work can close. The partner route is graded on REACH: a hormone-responsive 5′ partner is reported in one EMC patient in the world literature and in none of the partner-genotyped cases the cited cohorts cover, and the dominant partner has no retrieved druggable input. ⭐ The general mechanism survives and was strengthened by that sweep — the regulatory input a fusion imports is the PARTNER's, never NR4A3's own — which is the claim worth publishing and is a statement about fusion architecture rather than about a drug. ⛔ Superseded, retained: "neither has had its expression lookup run." One has; the other never needed one; and the arithmetic the partner route was waiting on had already been on disk since 2026-08-07.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

| route | role | what it contributes |
|---|---|---|
| [RT-HORMONE-PARTNER](L2-rt-hormone-partner.md) — Hormonal therapy for hormone-responsive 5′ fusion pa | `primary` | The half of the paper where the druggable input is imported by the 5′ partner rather than supplied by the driver's own receptor. |
| [RT-NR2F1](L2-rt-nr2f1.md) — Orphan nuclear-receptor agonism against dormancy esc | `primary` | The half of the paper that targets the disease's clinical problem — late metastasis — through a receptor that has the tool compound this program's own receptor never had. |

### PUB-CARE-DELIVERY — What decides survival in extraskeletal myxoid chondrosarcoma, and what the literature has been looking at instead

**○ `unwritten` · aimed at `preprint`**

In extraskeletal myxoid chondrosarcoma the determinants of survival that have been studied least are the ones that decide it most: the completeness of the first operation, whether the diagnosis was known before it, and whether follow-up outlasts a disease that recurs for decades.

**Not written because:** ⚠ Superseded, retained (rule 1.2): "Its four contributing routes are registered and their evidence is cited but not yet extracted. The paper needs the reconstructed survival dataset (RT-IPD-SURVIVAL) to say anything quantitative; without it, it is an argument with citations rather than a result." ⛔ BOTH HALVES ARE FALSE AS OF 2026-09-01. Six extraction artifacts exist and none of them consumes a reconstruction: 196 operated patients with a margin (research/modalities/emc-surgical-quality.json), 271 patients' primary site (emc-site-curation.json), 45 printed Cox coefficients (emc-prognostic-coefficients.json) and four printed time-to-event statistics (emc-recurrence-timing.json). RT-IPD-SURVIVAL has produced exactly one admissible curve — 11 patients, progression-free survival in advanced disease — which is the wrong shape for this paper and always was.

⭐ THE REAL REASON IT IS UNWRITTEN IS A JUDGEMENT, NOT A GAP. The paper's strongest quantitative claim — that margin decides local recurrence — is the printed conclusion of the abstract of its own largest source (PMID 40885991: "Wide resection is mandatory to reduce the risk of local recurrence of localized EMCs"). The third clause of what_it_would_claim, whether the diagnosis was known before the operation, is unstudiable in EMC from the reachable record: treatment setting is reported by no reachable series. And the working title's second half — "what the literature has been looking at instead" — is an argument with no measurement behind it. ⭐ The one free step that would change this is a term census over the 554-record corpus already committed at literature/emc-care-delivery-and-classification/ on the literature-cache branch, which is now filed as BLK-NO-FIELD-ATTENTION-MEASUREMENT.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-FIELD-ATTENTION-MEASUREMENT** (`insufficient_data`) — The paper's second half — what the literature has been looking at INSTEAD — rests on a corpus-wide term census nobody has run

| route | role | what it contributes |
|---|---|---|
| [RT-METASTASECTOMY](L2-rt-metastasectomy.md) — Pulmonary metastasectomy as a decision rather than a | `contributing` | Plausibly the highest-yield survival intervention available in this disease today, and the one with no literature at all. |
| [RT-RISK-MODEL](L2-rt-risk-model.md) — A prognostic risk model for EMC | `contributing` | The stratification that turns the family's other three routes from observations into decisions. |
| [RT-SURGICAL-QUALITY](L2-rt-surgical-quality.md) — The first operation — margin status, unplanned excis | `contributing` | The largest measured survival association in the disease, and the one nobody here had written down. |
| [RT-SURVEILLANCE](L2-rt-surveillance.md) — Surveillance duration and interval as the interventi | `contributing` | The disease's own natural history turned into a schedule, in the one place where timing and not chemistry decides the outcome. |

### PUB-IPD-SURVIVAL — A reconstructed patient-level survival dataset for extraskeletal myxoid chondrosarcoma

**○ `unwritten` · aimed at `preprint`**

What the published record of an ultra-rare cancer can and cannot yield as patient-level survival data, measured rather than assumed. Of the extraskeletal myxoid chondrosarcoma series reachable at no cost, the two largest print seven Kaplan-Meier curves between them and NO numbers-at-risk row, so neither can be reconstructed at all; one curve carries a risk row and yields 11 patients, reproducing that paper's own printed median; a trial that prints no Kaplan-Meier curve at all yields four more at patient level from its SWIMMER PLOT, which needs no risk table and no inversion; and two further patients are printed outright in a table and need only transcribing. ⛔ THERE IS NO POOLED TIME-TO-EVENT DATASET AT THE END OF THIS, and the reason is what journals print rather than what an instrument can read. ⚠ *Superseded, retained: "Patient-level survival data for extraskeletal myxoid chondrosarcoma, reconstructed from every published Kaplan-Meier curve that prints a numbers-at-risk table — the first pooled time-to-event dataset in this disease, and the input its unanswerable clinical questions were waiting on."* That claim was written before anybody looked at the figures. The figures were looked at on 2026-08-25 and the promised pool is not there to be built.

**Not written because:** The paper is unwritten; the science for it now exists. ⚠ *Superseded, retained: "no published figure has been digitized into it yet."* One has — stacchiotti2013 Figure 2, 11 patients, 9 events, median 7.98 months against the caption's printed 8, a number the reconstruction never saw. What changed is the paper's FINDING rather than its readiness: it is now largely a negative about the reporting practice of a literature, with a method and a small dataset attached. ⛔ CURVES stays empty and a test still enforces it; coordinates reach the program only through a digitizer artifact naming the committed image it read.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-CURATED-CLINICAL-DATA** (`insufficient_data`) — Three of these six clinical fields are absent from the reachable publications, not merely un-extracted — and the other three are now extracted

| route | role | what it contributes |
|---|---|---|
| [RT-IPD-SURVIVAL](L2-rt-ipd-survival.md) — Patient-level survival reconstructed from published  | `contributing` | The dataset every other clinical route in this portfolio stops at the absence of. |

### PUB-PARKED-MODALITIES — Five modalities parked on a capability that does not exist yet: what would have to land, and how it is being watched for

**○ `unwritten` · aimed at `preprint`**

For each parked modality there is a single named capability — a glue design method with a prospective track record, a co-folder benchmarked on assembly, a solid-tumour vector — whose arrival would make the route computable, and stating that capability with its scan trigger converts an indefinite park into a monitored condition.

**Not written because:** Every route it would cover is parked on a technology nobody has, so the paper has no result to report and would be a horizon scan. It is worth writing only once at least one of the watched capabilities lands; until then the scan triggers carry the work.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-VECTOR-DELIVERY** (`requires_future_technology`) — Vector delivery (gene-therapy payload into a solid tumour)
- **BLK-INDUCED-COMPLEX** (`requires_better_structure_prediction`) — An induced ternary/bivalent complex is still required (a second protein must be placed)

| route | role | what it contributes |
|---|---|---|
| [RT-AF3-INTERFACE](L2-rt-af3-interface.md) — AF3 on a druggable interface | `contributing` | A method waiting on a method, with the benchmark that would end the wait stated precisely: inter-chain accuracy on post-training-horizon structures. |
| [RT-CRISPR-CAS13](L2-rt-crispr-cas13.md) — CRISPR/Cas9 intron-targeted fusion disruption; Cas13 | `contributing` | The nuclease arms, whose gate is the vector rather than the nuclease — which is why watching the enzyme literature would be watching the wrong thing. |
| [RT-GLUE](L2-rt-glue.md) — Molecular glue instead of a PROTAC | `contributing` | The capability it waits on: a glue design method with a prospective track record. Until one exists there is no computation whose result would mean anything. |
| [RT-RIBOZYME](L2-rt-ribozyme.md) — Trans-splicing ribozyme → suicide gene, triggered by | `contributing` | The one row gated twice over — delivery, and a technique with no modern clinical footing — and the reason two gates is a different situation from one. |
| [RT-RIPTAC](L2-rt-riptac.md) — RIPTAC — bind the tumour protein, poison an essentia | `contributing` | The row that is dominated on both axes at once — it needs the selectivity the program cannot measure and a chemistry campaign it cannot run. |

## Every route, and where it ends

*The same edges from the other end. `readiness` is what the ROUTE could become today; `aimed at` is what its PAPER is for — and the gap between the two columns is the honest statement of what is left to do.*

| route | family | readiness today | endpoint | aimed at | role |
|---|---|---|---|---|---|
| [RT-ANDGATE](L2-rt-andgate.md) | [ST-PROXIMITY](L1-st-proximity.md) | `internal_note` | **PUB-ANDGATE** ◐ | `preprint` | `primary` |
| [RT-ASO](L2-rt-aso.md) | [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) | `chemrxiv` | **PUB-ASO** ◉ | `journal_submission` | `primary` |
| [RT-ASO-ASK](L2-rt-aso-ask.md) | [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) | `experimental_proposal` | **PUB-ASO** ◉ | `journal_submission` | `contributing` |
| [RT-ATR-ASSESS](L2-rt-atr-assess.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `preprint` | **PUB-ATR** ◐ | `preprint` | `primary` |
| [RT-ATR-PANEL](L2-rt-atr-panel.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `experimental_proposal` | **PUB-ATR-PANEL-ASK** ◐ | `experimental_proposal` | `primary` |
| [RT-APOPTOSIS-DEP](L2-rt-apoptosis-dep.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-BIOMARKER-DEP** ◐ | `preprint` | `contributing` |
| [RT-ARGININE](L2-rt-arginine.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-BIOMARKER-DEP** ◐ | `preprint` | `contributing` |
| [RT-EZH2](L2-rt-ezh2.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-BIOMARKER-DEP** ◐ | `preprint` | `contributing` |
| [RT-MDM2](L2-rt-mdm2.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-BIOMARKER-DEP** ◐ | `preprint` | `contributing` |
| [RT-POLQ](L2-rt-polq.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-BIOMARKER-DEP** ◐ | `preprint` | `contributing` |
| [RT-METASTASECTOMY](L2-rt-metastasectomy.md) | [ST-CARE-DELIVERY](L1-st-care-delivery.md) | `internal_note` | **PUB-CARE-DELIVERY** ○ | `preprint` | `contributing` |
| [RT-RISK-MODEL](L2-rt-risk-model.md) | [ST-CARE-DELIVERY](L1-st-care-delivery.md) | `internal_note` | **PUB-CARE-DELIVERY** ○ | `preprint` | `contributing` |
| [RT-SURGICAL-QUALITY](L2-rt-surgical-quality.md) | [ST-CARE-DELIVERY](L1-st-care-delivery.md) | `internal_note` | **PUB-CARE-DELIVERY** ○ | `preprint` | `contributing` |
| [RT-SURVEILLANCE](L2-rt-surveillance.md) | [ST-CARE-DELIVERY](L1-st-care-delivery.md) | `internal_note` | **PUB-CARE-DELIVERY** ○ | `preprint` | `contributing` |
| [RT-6MP](L2-rt-6mp.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-CLOSED-ROUTES** ◐ | `preprint` | `contributing` |
| [RT-DBD](L2-rt-dbd.md) | [ST-FUSION-DIRECT](L1-st-fusion-direct.md) | `internal_note` | **PUB-CLOSED-ROUTES** ◐ | `preprint` | `contributing` |
| [RT-EWSR1-PROTEIN](L2-rt-ewsr1-protein.md) | [ST-FUSION-DIRECT](L1-st-fusion-direct.md) | `internal_note` | **PUB-CLOSED-ROUTES** ◐ | `preprint` | `contributing` |
| [RT-FET-LC-LIGAND](L2-rt-fet-lc-ligand.md) | [ST-FUSION-DIRECT](L1-st-fusion-direct.md) | `internal_note` | **PUB-CLOSED-ROUTES** ◐ | `preprint` | `contributing` |
| [RT-HDAC-BET](L2-rt-hdac-bet.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-CLOSED-ROUTES** ◐ | `preprint` | `contributing` |
| [RT-RXR](L2-rt-rxr.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-CLOSED-ROUTES** ◐ | `preprint` | `contributing` |
| [RT-SYNPROMOTER](L2-rt-synpromoter.md) | [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) | `internal_note` | **PUB-CLOSED-ROUTES** ◐ | `preprint` | `contributing` |
| [RT-ASYMMETRIC](L2-rt-asymmetric.md) | [ST-OCCUPANCY](L1-st-occupancy.md) | `reproducible_workflow` | **PUB-DEGRADER** ◐ | `journal_submission` | `contributing` |
| [RT-COVALENT-PROBE](L2-rt-covalent-probe.md) | [ST-OCCUPANCY](L1-st-occupancy.md) | `internal_note` | **PUB-DEGRADER** ◐ | `journal_submission` | `contributing` |
| [RT-DEGRADER](L2-rt-degrader.md) | [ST-PROXIMITY](L1-st-proximity.md) | `preprint` | **PUB-DEGRADER** ◐ | `journal_submission` | `primary` |
| [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md) | [ST-IMMUNO](L1-st-immuno.md) | `preprint` | **PUB-DEGRADER** ◐ | `journal_submission` | `contributing` |
| [RT-UBIQ-SELECTIVE](L2-rt-ubiq-selective.md) | [ST-PROXIMITY](L1-st-proximity.md) | `internal_note` | **PUB-DEGRADER** ◐ | `journal_submission` | `contributing` |
| [RT-DIAGNOSTIC-PATHWAY](L2-rt-diagnostic-pathway.md) | [ST-CARE-DELIVERY](L1-st-care-delivery.md) | `internal_note` | **PUB-EMC-CLASSIFICATION** ◐ | `internal_note` | `contributing` |
| [RT-POPULATION-REGISTRY](L2-rt-population-registry.md) | [ST-CARE-DELIVERY](L1-st-care-delivery.md) | `internal_note` | **PUB-EMC-CLASSIFICATION** ◐ | `internal_note` | `contributing` |
| [RT-ICI-TKI](L2-rt-ici-tki.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-EMC-PROGRAM** ◐ | `journal_submission` | `context` |
| [RT-TRABECTEDIN](L2-rt-trabectedin.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-EMC-PROGRAM** ◐ | `journal_submission` | `context` |
| [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) | [ST-DISSEMINATION](L1-st-dissemination.md) | `journal_submission` | **PUB-ENDPOINT** ◐ | `journal_submission` | `primary` |
| [RT-FUSION-OUTPUT](L2-rt-fusion-output.md) | [ST-DISSEMINATION](L1-st-dissemination.md) | `journal_submission` | **PUB-FUSION-OUTPUT** ◐ | `journal_submission` | `primary` |
| [RT-PARTNER-STRAT](L2-rt-partner-strat.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `preprint` | **PUB-FUSION-PARTNER** ◐ | `preprint` | `primary` |
| [RT-VACCINE](L2-rt-vaccine.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-HLA-COVERAGE** ◐ | `preprint` | `primary` |
| [RT-IPD-SURVIVAL](L2-rt-ipd-survival.md) | [ST-CARE-DELIVERY](L1-st-care-delivery.md) | `internal_note` | **PUB-IPD-SURVIVAL** ○ | `preprint` | `contributing` |
| [RT-ALK-HIT](L2-rt-alk-hit.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-KINASE-LEADS** ◔ | `preprint` | `contributing` |
| [RT-DNAPK](L2-rt-dnapk.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-KINASE-LEADS** ◔ | `preprint` | `contributing` |
| [RT-RET](L2-rt-ret.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-KINASE-LEADS** ◔ | `preprint` | `contributing` |
| [RT-SGK1](L2-rt-sgk1.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-KINASE-LEADS** ◔ | `preprint` | `contributing` |
| [RT-LIMB-PERFUSION](L2-rt-limb-perfusion.md) | [ST-LOCOREGIONAL](L1-st-locoregional.md) | `internal_note` | **PUB-LOCOREGIONAL** ◔ | `preprint` | `contributing` |
| [RT-LUNG-DIRECTED](L2-rt-lung-directed.md) | [ST-LOCOREGIONAL](L1-st-locoregional.md) | `internal_note` | **PUB-LOCOREGIONAL** ◔ | `preprint` | `contributing` |
| [RT-MDT-LUNG](L2-rt-mdt-lung.md) | [ST-LOCOREGIONAL](L1-st-locoregional.md) | `internal_note` | **PUB-LOCOREGIONAL** ◔ | `preprint` | `contributing` |
| [RT-RT-INTENSIFY](L2-rt-rt-intensify.md) | [ST-LOCOREGIONAL](L1-st-locoregional.md) | `internal_note` | **PUB-LOCOREGIONAL** ◔ | `preprint` | `contributing` |
| [RT-HYPOXIA-PRODRUG](L2-rt-hypoxia-prodrug.md) | [ST-MICROENV](L1-st-microenv.md) | `internal_note` | **PUB-MATRIX-ADDRESS** ◔ | `preprint` | `contributing` |
| [RT-IMMUNOCYTOKINE](L2-rt-immunocytokine.md) | [ST-MICROENV](L1-st-microenv.md) | `internal_note` | **PUB-MATRIX-ADDRESS** ◔ | `preprint` | `contributing` |
| [RT-MATRIX-ADDRESS](L2-rt-matrix-address.md) | [ST-MICROENV](L1-st-microenv.md) | `internal_note` | **PUB-MATRIX-ADDRESS** ◔ | `preprint` | `contributing` |
| [RT-MATRIX-SYNTHESIS](L2-rt-matrix-synthesis.md) | [ST-MICROENV](L1-st-microenv.md) | `internal_note` | **PUB-MATRIX-ADDRESS** ◔ | `preprint` | `contributing` |
| [RT-METHODS-PAPER](L2-rt-methods-paper.md) | [ST-DISSEMINATION](L1-st-dissemination.md) | `journal_submission` | **PUB-METHODS** ◐ | `journal_submission` | `primary` |
| [RT-MODALITY-CENSUS](L2-rt-modality-census.md) | [ST-DISSEMINATION](L1-st-dissemination.md) | `preprint` | **PUB-MODALITY-CENSUS** ◐ | `preprint` | `primary` |
| [RT-MONOVALENT](L2-rt-monovalent.md) | [ST-OCCUPANCY](L1-st-occupancy.md) | `internal_note` | **PUB-MONOVALENT** ◐ | `internal_note` | `primary` |
| [RT-COMPETING-MORTALITY](L2-rt-competing-mortality.md) | [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) | `preprint` | **PUB-MORTALITY-MECHANISM** ◐ | `preprint` | `contributing` |
| [RT-EARLY-PALLIATIVE](L2-rt-early-palliative.md) | [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) | `internal_note` | **PUB-MORTALITY-MECHANISM** ◐ | `preprint` | `contributing` |
| [RT-HOST-FACTOR](L2-rt-host-factor.md) | [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) | `internal_note` | **PUB-MORTALITY-MECHANISM** ◐ | `preprint` | `contributing` |
| [RT-RESPIRATORY-FAILURE](L2-rt-respiratory-failure.md) | [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) | `internal_note` | **PUB-MORTALITY-MECHANISM** ◐ | `preprint` | `contributing` |
| [RT-TREATMENT-HARM](L2-rt-treatment-harm.md) | [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) | `internal_note` | **PUB-MORTALITY-MECHANISM** ◐ | `preprint` | `contributing` |
| [RT-VTE-PROPHYLAXIS](L2-rt-vte-prophylaxis.md) | [ST-MORTALITY-MECHANISM](L1-st-mortality-mechanism.md) | `internal_note` | **PUB-MORTALITY-MECHANISM** ◐ | `preprint` | `contributing` |
| [RT-MTAP-PRMT5](L2-rt-mtap-prmt5.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `preprint` | **PUB-MTAP-PRMT5** ◐ | `preprint` | `primary` |
| [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-NEOANTIGEN** ◐ | `preprint` | `primary` |
| [RT-TCR-IMMTAC](L2-rt-tcr-immtac.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-NEOANTIGEN** ◐ | `preprint` | `contributing` |
| [RT-HORMONE-PARTNER](L2-rt-hormone-partner.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-NR-OUTSIDE-NR4A3** ◔ | `preprint` | `primary` |
| [RT-NR2F1](L2-rt-nr2f1.md) | [ST-OCCUPANCY](L1-st-occupancy.md) | `internal_note` | **PUB-NR-OUTSIDE-NR4A3** ◔ | `preprint` | `primary` |
| [RT-AF3-INTERFACE](L2-rt-af3-interface.md) | [ST-PROXIMITY](L1-st-proximity.md) | `internal_note` | **PUB-PARKED-MODALITIES** ○ | `preprint` | `contributing` |
| [RT-CRISPR-CAS13](L2-rt-crispr-cas13.md) | [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) | `internal_note` | **PUB-PARKED-MODALITIES** ○ | `preprint` | `contributing` |
| [RT-GLUE](L2-rt-glue.md) | [ST-PROXIMITY](L1-st-proximity.md) | `internal_note` | **PUB-PARKED-MODALITIES** ○ | `preprint` | `contributing` |
| [RT-RIBOZYME](L2-rt-ribozyme.md) | [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) | `internal_note` | **PUB-PARKED-MODALITIES** ○ | `preprint` | `contributing` |
| [RT-RIPTAC](L2-rt-riptac.md) | [ST-PROXIMITY](L1-st-proximity.md) | `internal_note` | **PUB-PARKED-MODALITIES** ○ | `preprint` | `contributing` |
| [RT-CARFILZOMIB](L2-rt-carfilzomib.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-REPURPOSING** ◐ | `preprint` | `primary` |
| [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-REPURPOSING** ◐ | `preprint` | `contributing` |
| [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `experimental_proposal` | **PUB-REPURPOSING** ◐ | `preprint` | `contributing` |
| [RT-SCHEDULING](L2-rt-scheduling.md) | [ST-STRATEGY](L1-st-strategy.md) | `internal_note` | **PUB-STRATEGY-ARCH** ◐ | `preprint` | `contributing` |
| [RT-SEQUENCING](L2-rt-sequencing.md) | [ST-STRATEGY](L1-st-strategy.md) | `internal_note` | **PUB-STRATEGY-ARCH** ◐ | `preprint` | `contributing` |
| [RT-TRIAL-REACH](L2-rt-trial-reach.md) | [ST-STRATEGY](L1-st-strategy.md) | `internal_note` | **PUB-STRATEGY-ARCH** ◐ | `preprint` | `contributing` |
| [RT-B7H3](L2-rt-b7h3.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `primary` |
| [RT-CART-SURFACE](L2-rt-cart-surface.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `contributing` |
| [RT-FAP-RLT](L2-rt-fap-rlt.md) | [ST-RADIOLIGAND](L1-st-radioligand.md) | `internal_note` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `contributing` |
| [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md) | [ST-IMMUNO](L1-st-immuno.md) | `experimental_proposal` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `contributing` |
| [RT-SSTR2](L2-rt-sstr2.md) | [ST-RADIOLIGAND](L1-st-radioligand.md) | `experimental_proposal` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `contributing` |
| [RT-TCRT-CTA](L2-rt-tcrt-cta.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `contributing` |
| [RT-SYNLETH-DEP](L2-rt-synleth-dep.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-SYNLETH** ◐ | `internal_note` | `primary` |
| [RT-TCIP](L2-rt-tcip.md) | [ST-PROXIMITY](L1-st-proximity.md) | `preprint` | **PUB-TCIP** ◐ | `preprint` | `primary` |
| [RT-CHAPERONE](L2-rt-chaperone.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-TXN-DEPENDENCY** ◐ | `preprint` | `primary` |
| [RT-TXN-CDK](L2-rt-txn-cdk.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-TXN-DEPENDENCY** ◐ | `preprint` | `primary` |
| [RT-VACCINE-COMBINATION](L2-rt-vaccine-combination.md) | [ST-IMMUNO](L1-st-immuno.md) | `preprint` | **PUB-VACCINE-PATH** ◐ | `preprint` | `primary` |

## What this page deliberately leaves out

- **Whether the science is any good.** `drafted` means a file exists. It says nothing about whether the draft holds up — that is the route pages, their instruments, and whether those instruments recovered a known answer.
- **Every other L3 document.** Only a document that IS a route's endpoint appears here. Memos, plans, red-teams and outreach packages also declare `level: L3` and are not deliverables; `systems_check --check` reports their count as `[B7]` rather than listing them, because warning on them would train the reader to ignore the check.
- **Order.** Nothing on this page ranks the endpoints. What to do next is [the plan](plan.md).

[← L0](L0-ecosystem.md)
