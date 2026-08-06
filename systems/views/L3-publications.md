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

**16 endpoints for 40 routes · 12 with a document · 4 unwritten.**

⭐ **An unwritten paper is a row here, and that is the reason this collection exists.** L3 and L4 are otherwise DOCUMENTS rather than graph rows ([ARCHITECTURE §3](../ARCHITECTURE.md#3--the-hierarchy)), on the sound grounds that copying a file's title into JSON creates a second home for a fact the file owns. That reasoning is intact — a row with a document carries no title and this page reads it back out of the file. What it did not cover is a paper that **does not exist yet**: it has no file, so it has no other home, and leaving it unmodelled made *“this route has no endpoint”* and *“this route's endpoint is not written yet”* look identical.

## The endpoints

*A `—` in the last column means a document exists. It does **not** mean the paper is finished or that the science in it holds — that question belongs to the route pages and their instruments, and this page is careful not to answer it by implication.*

| endpoint | state | aimed at | routes | what is still missing |
|---|---|---|---:|---|
| **PUB-ANDGATE**<br/>[A coincidence-detection ("AND-gate") bivalent degrader for protein-leve…](../../research/manuscripts/fusion-selective-andgate-degrader-paper.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-ASO**<br/>[A fusion-selective antisense oligonucleotide against the EWSR1::NR4A3 b…](../../research/manuscripts/fusion-junction-aso-paper.md) | ◐ `drafted` | `chemrxiv` | 2 | — |
| **PUB-ATR**<br/>[The in-silico ATR vulnerability assessment for EMC](../../research/manuscripts/emc-atr-vulnerability-assessment.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-ATR-PANEL-ASK**<br/>[The EMC arm, pre-built — a collaborator package for the FET / ATM / ATR…](../../research/manuscripts/emc-atr-collaborator-package.md) | ◐ `drafted` | `experimental_proposal` | 1 | — |
| **PUB-DEGRADER**<br/>[In silico design of a paralogue-favoured ligand for a cryptic NR4A3 poc…](../../research/manuscripts/nr4a3-degrader-paper.md) | ◐ `drafted` | `journal_submission` | 5 | — |
| **PUB-EMC-PROGRAM**<br/>[Attacking an "undruggable" fusion oncoprotein by computation alone: a d…](../../research/manuscripts/emc-treatment-roadmap.md) | ◐ `drafted` | `journal_submission` | 2 | — |
| **PUB-HLA-COVERAGE**<br/>[Population coverage of a public EWSR1::NR4A3 fusion-neoantigen immunoth…](../../research/manuscripts/hla-coverage-emc.md) | ◐ `drafted` | `preprint` | 1 | — |
| **PUB-MONOVALENT**<br/>[The monovalent pocket-modulation route — a small molecule that only occ…](../../research/manuscripts/nr4a3-monovalent-pocket-route.md) | ◐ `drafted` | `internal_note` | 1 | — |
| **PUB-NEOANTIGEN**<br/>[Targeting the EWSR1::NR4A3 fusion-junction neoantigen in extraskeletal …](../../research/manuscripts/fusion-junction-neoantigen-paper.md) | ◐ `drafted` | `preprint` | 2 | — |
| **PUB-REPURPOSING**<br/>[Mechanism-based drug-repurposing hypotheses for extraskeletal myxoid ch…](../../research/manuscripts/repurposing-hypotheses.md) | ◐ `drafted` | `preprint` | 3 | — |
| **PUB-SURFACE-TARGETS**<br/>[In-silico surface-antigen prioritisation for extraskeletal myxoid chond…](../../research/manuscripts/emc-surface-target-landscape.md) | ◐ `drafted` | `preprint` | 6 | — |
| **PUB-SYNLETH**<br/>[Degrader vs. synthetic-lethal for EWSR1::NR4A3 EMC — a feasibility comp…](../../research/manuscripts/degrader-vs-synthetic-lethal.md) | ◐ `drafted` | `internal_note` | 1 | — |
| **PUB-CLOSED-ROUTES**<br/>*Seven routes closed on argument rather than on experiment: the negative…* | ○ `unwritten` | `preprint` | 7 | The closures themselves are complete and each is already recorded with its grounds in the route register; … |
| **PUB-METHODS**<br/>*The failure record of a computation-only degrader program: what in-sili…* | ○ `unwritten` | `journal_submission` | 1 | Nothing blocks it. It carries no scientific blocker at all and is the only endpoint in the portfolio that is true regardless of how every other route … |
| **PUB-PARKED-MODALITIES**<br/>*Five modalities parked on a capability that does not exist yet: what wo…* | ○ `unwritten` | `preprint` | 5 | Every route it would cover is parked on a technology nobody has, so the paper has no result to report and would be a horizon scan. … |
| **PUB-TCIP**<br/>*Transcriptional chemically-induced proximity on EWSR1::NR4A3: reach enu…* | ○ `unwritten` | `preprint` | 1 | The paired anchor-plus-effector enumeration has not been run for this configuration, so there is no result to report. … |

## What each one would claim

*One statement per endpoint, written so a reader can disagree with it. If this sentence cannot be written, there is no endpoint — there is an activity.*

### PUB-ANDGATE — A coincidence-detection ("AND-gate") bivalent degrader for protein-level fusion-exclusivity in EWSR1::NR4A3 extraskeleta

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/fusion-selective-andgate-degrader-paper.md`](../../research/manuscripts/fusion-selective-andgate-degrader-paper.md)**

Coincidence detection across both halves of the fusion is a design that would convert a paralogue-selectivity problem into an avidity problem — and it names precisely what does not exist for it to be built, which is a ligand for the EWSR1 half.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NOT-FUSION-SELECTIVE** (`fundamental_biological_limit`) — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)

| route | role | what it contributes |
|---|---|---|
| [RT-ANDGATE](L2-rt-andgate.md) — AND-gate bivalent degrader (avidity coincidence dete | `primary` | The coincidence-detection design and the statement of exactly what does not exist for it to be built. |

### PUB-ASO — A fusion-selective antisense oligonucleotide against the EWSR1::NR4A3 breakpoint junction: RNA-level fusion-exclusivity

**◐ `drafted` · aimed at `chemrxiv` · [`research/manuscripts/fusion-junction-aso-paper.md`](../../research/manuscripts/fusion-junction-aso-paper.md)**

The EWSR1::NR4A3 breakpoint junction is the one truly tumour-exclusive feature of this disease at the RNA level, an oligonucleotide can be designed to read it rather than a shape, and transcriptome-wide specificity screening finds no competing match — with delivery named as the outstanding gate rather than assumed away.

| route | role | what it contributes |
|---|---|---|
| [RT-ASO](L2-rt-aso.md) — Fusion-junction ASO / siRNA (the deliverable) | `primary` | The junction design, the transcriptome-wide specificity screen, and delivery stated as the outstanding gate rather than assumed away. |
| [RT-ASO-ASK](L2-rt-aso-ask.md) — Junction knockdown + parental sparing in EMC lines ( | `contributing` | The decisive experiment, specified inside the paper and sent with it: junction knockdown with wild-type sparing in an EMC line. Without it the paper states a specificity result with no named way to falsify it at a bench. |

### PUB-ATR — The in-silico ATR vulnerability assessment for EMC

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/emc-atr-vulnerability-assessment.md`](../../research/manuscripts/emc-atr-vulnerability-assessment.md)**

A replication-stress vulnerability can be assessed for EMC by inheritance from its FET-fusion class, and the assessment states inside itself that class inheritance is not an EMC measurement — which is what makes it an assessment rather than a finding.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)
- **BLK-CLASS-INHERITANCE** (`insufficient_data`) — Class inheritance, not an EMC measurement — no NR4A3 fusion has been tested for the phenotype

| route | role | what it contributes |
|---|---|---|
| [RT-ATR-ASSESS](L2-rt-atr-assess.md) — The in-silico ATR vulnerability assessment (the comp | `primary` | The computed assessment itself, and the class-inheritance limit stated inside it rather than in a caveat section. |

### PUB-ATR-PANEL-ASK — The EMC arm, pre-built — a collaborator package for the FET / ATM / ATR laser-microirradiation assay

**◐ `drafted` · aimed at `experimental_proposal` · [`research/manuscripts/emc-atr-collaborator-package.md`](../../research/manuscripts/emc-atr-collaborator-package.md) · ships with **PUB-ATR****

Everything a group already running the FET-fusion DSB-recruitment assay would have to derive in order to add EMC as a fourth partner class is pre-built — constructs, controls, predicted outcomes and kill criteria fixed in advance — so the marginal cost of testing the assessment's prediction is the bench time and nothing else.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-WET-LAB** (`requires_external_collaboration`) — No wet lab and no collaborator — an ask needs a self-interested taker before its size matters

| route | role | what it contributes |
|---|---|---|
| [RT-ATR-PANEL](L2-rt-atr-panel.md) — The ATR-inhibitor cell panel in EMC lines (the ask) | `primary` | The costed panel design, its controls and its kill criteria — the half of the ATR question that no computation can supply. |

### PUB-DEGRADER — In silico design of a paralogue-favoured ligand for a cryptic NR4A3 pocket

**◐ `drafted` · aimed at `journal_submission` · [`research/manuscripts/nr4a3-degrader-paper.md`](../../research/manuscripts/nr4a3-degrader-paper.md)**

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

### PUB-EMC-PROGRAM — Attacking an "undruggable" fusion oncoprotein by computation alone: a driver-directed treatment program for EWSR1::NR4A3

**◐ `drafted` · aimed at `journal_submission` · [`research/manuscripts/emc-treatment-roadmap.md`](../../research/manuscripts/emc-treatment-roadmap.md)**

The gap in EMC care is categorical rather than a matter of degree — nothing in clinical use addresses the driver — and a computation-only program can enumerate the driver-directed routes, state a falsifiable kill criterion for each, and place the borrowed standard-of-care agents as context rather than as its own contribution.

| route | role | what it contributes |
|---|---|---|
| [RT-ICI-TKI](L2-rt-ici-tki.md) — Checkpoint inhibitor + anti-angiogenic TKI combinati | `context` | The comparator arm: the most consistently active class in EMC, cited to size the gap rather than analysed. Promoting it to a contribution would overstate what was done. |
| [RT-TRABECTEDIN](L2-rt-trabectedin.md) — Trabectedin (± RT or combination) | `context` | Cited to establish current care and the categorical gap. Explicitly not this program's contribution — it is clinical-evidence synthesis, and a single response must not be overstated. |

### PUB-HLA-COVERAGE — Population coverage of a public EWSR1::NR4A3 fusion-neoantigen immunotherapy in extraskeletal myxoid chondrosarcoma: a r

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/hla-coverage-emc.md`](../../research/manuscripts/hla-coverage-emc.md)**

If a public junction epitope were presented, the fraction of the patient population whose HLA alleles could see it is computable from reference allele frequencies — an eligibility ceiling that constrains every junction-directed immunotherapy route and is reusable independently of whether the epitope itself survives.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-ANTIGEN-COLD** (`fundamental_biological_limit`) — EMC is antigen-cold, and the fusion junction is a weak peptide-HLA

| route | role | what it contributes |
|---|---|---|
| [RT-VACCINE](L2-rt-vaccine.md) — Fusion-junction vaccine / HLA-coverage paper | `primary` | The population-coverage computation, which stands on its own as an eligibility ceiling even while the antigen above it is void. |

### PUB-MONOVALENT — The monovalent pocket-modulation route — a small molecule that only occupies the NR4A3 LBD

**◐ `drafted` · aimed at `internal_note` · [`research/manuscripts/nr4a3-monovalent-pocket-route.md`](../../research/manuscripts/nr4a3-monovalent-pocket-route.md)**

Occupancy of the NR4A3 pocket without recruitment is a distinct route from degradation, and the question of whether occupancy alone changes the fusion's behaviour has never been asked by anyone — so the route is untested rather than refuted.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-R4-BINDS** (`requires_wet_lab`) — R4 — nothing is known to bind the cryptic pocket at all

| route | role | what it contributes |
|---|---|---|
| [RT-MONOVALENT](L2-rt-monovalent.md) — Monovalent LBD pocket modulation — a molecule that o | `primary` | The whole memo: that occupancy without recruitment is a separate question nobody has asked, and what a sized selectivity requirement for it would have to look like. |

### PUB-NEOANTIGEN — Targeting the EWSR1::NR4A3 fusion-junction neoantigen in extraskeletal myxoid chondrosarcoma: a fusion-exclusive immunot

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/fusion-junction-neoantigen-paper.md`](../../research/manuscripts/fusion-junction-neoantigen-paper.md)**

The fusion junction produces a peptide sequence that is absent from wild-type EWSR1 and wild-type NR4A3 — ⚠ the only novelty test in this repo compares against those two PARENT proteins (`fusion_breakpoints.py:231`) and NO proteome-wide search has ever been run, so 'absent from the normal proteome' is not a claim this work can make, and whether any allele presents it is a prediction that must be regenerated against a corrected exon index before it can be reported at all.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-ANTIGEN-COLD** (`fundamental_biological_limit`) — EMC is antigen-cold, and the fusion junction is a weak peptide-HLA

| route | role | what it contributes |
|---|---|---|
| [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md) — Fusion-junction neoantigen (the antigen, shared by t | `primary` | The junction peptide and its presentation predictions, which must be regenerated against the corrected exon index before any of them can be reported. |
| [RT-TCR-IMMTAC](L2-rt-tcr-immtac.md) — Fusion-junction TCR-T / soluble-TCR (ImmTAC) against | `contributing` | The receptor-side delivery option for the junction epitope, and the measured weakness of the junction peptide-HLA that bounds it — a property of this junction rather than of the modality. |

### PUB-REPURPOSING — Mechanism-based drug-repurposing hypotheses for extraskeletal myxoid chondrosarcoma

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/repurposing-hypotheses.md`](../../research/manuscripts/repurposing-hypotheses.md)**

Existing agents not yet reported in EMC can be mapped to EMC's molecular and microenvironmental axes by three independent methods, each candidate graded by an explicit evidence tier — a hypothesis-generating menu that asserts no efficacy for any agent it names.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

| route | role | what it contributes |
|---|---|---|
| [RT-CARFILZOMIB](L2-rt-carfilzomib.md) — Carfilzomib ± anthracycline (± venetoclax) | `primary` | The proteasome-inhibitor hypothesis and the ex-vivo EMC evidence behind it — the only ex-vivo EMC result in the portfolio, and currently the paper's weakest citation. |
| [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) — PPARG downstream-effector (repurpose TZDs) | `contributing` | The downstream-effector axis, carried with its direction flagged unresolved — scoped as unresolved and NOT refuted, which the paper must not conflate. |
| [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) — Trabectedin + a PPARγ agonist (all approved drugs) | `contributing` | The all-approved combination arm, held behind the same unresolved PPARγ direction that bounds the row above it. |

### PUB-SURFACE-TARGETS — In-silico surface-antigen prioritisation for extraskeletal myxoid chondrosarcoma: one cell line, a translocation-sarcoma

**◐ `drafted` · aimed at `preprint` · [`research/manuscripts/emc-surface-target-landscape.md`](../../research/manuscripts/emc-surface-target-landscape.md)**

Surface and stromal antigens can be prioritised for EMC in silico from one cell line and a translocation-sarcoma comparison set, and every resulting negative is bounded by that surrogate basis rather than by an EMC tissue measurement — which is the honest limit of a search run without the disease's own expression data.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

| route | role | what it contributes |
|---|---|---|
| [RT-B7H3](L2-rt-b7h3.md) — B7-H3 (CD276) / CD56 → ADC, bispecific or CAR-T | `primary` | The prioritised surface-antigen ranking and the surrogate basis that bounds its negatives. |
| [RT-CART-SURFACE](L2-rt-cart-surface.md) — CAR-T for EMC (surface-directed) | `contributing` | The cell-product reading of the same ranking, and the finding that the constraint is the antigen and the stroma rather than the CAR. |
| [RT-FAP-RLT](L2-rt-fap-rlt.md) — FAP-targeted radioligand therapy (FAPI-RLT) | `contributing` | The stromal arm, which is the only row on the list that does not require the fusion biology to be solved and is also the least measured. |
| [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md) — PRAME-directed brenetafusp (ImmTAC) / PRAME CAR-TCR | `contributing` | The one antigen on the list whose therapeutic already exists clinically, which turns its row from a discovery into a check. |
| [RT-SSTR2](L2-rt-sstr2.md) — SSTR2 / neuroendocrine theranostic | `contributing` | The theranostic receptor arm, framed as a cheap decisive negative rather than as a lead — there is no computation that strengthens it, only a measurement. |
| [RT-TCRT-CTA](L2-rt-tcrt-cta.md) — TCR-T / engineered T cells vs a cancer-testis antige | `contributing` | The cancer-testis antigen arm ported from synovial sarcoma, downgraded on a measurement rather than on an argument. |

### PUB-SYNLETH — Degrader vs. synthetic-lethal for EWSR1::NR4A3 EMC — a feasibility comparison

**◐ `drafted` · aimed at `internal_note` · [`research/manuscripts/degrader-vs-synthetic-lethal.md`](../../research/manuscripts/degrader-vs-synthetic-lethal.md)**

A BRD9/ncBAF dependency is the best-motivated synthetic-lethal candidate for a FET fusion, and the negative recorded here is bounded by a transfer prior over a single cell line — a statement about the available data, not about the biology.

**Blocks on the PAPER** — deliberately not the same set its routes inherit, because a route can be blocked on a capability while its paper is publishable today as an honest negative:

- **BLK-NO-EMC-DATA** (`insufficient_data`) — EMC is nearly absent from public functional-genomics data (one DepMap line, n = 1, no CRISPR data)

| route | role | what it contributes |
|---|---|---|
| [RT-SYNLETH-DEP](L2-rt-synleth-dep.md) — Synthetic-lethal / dependency partner (BRD9 / ncBAF  | `primary` | The BRD9/ncBAF dependency argument, and the data-bounded negative that follows from a transfer prior over one cell line. |

### PUB-CLOSED-ROUTES — Seven routes closed on argument rather than on experiment: the negative record of an EWSR1::NR4A3 route search

**○ `unwritten` · aimed at `preprint`**

A route can be closed rigorously without an experiment when the closure is definitional or is arithmetic over a fixed measured fact, and separating those permanent closures from the merely instrument-limited ones is what keeps a portfolio from re-litigating settled questions — with wild-type NR4A3 pharmacology failing to transfer to the chimera as the worked example.

**Not written because:** The closures themselves are complete and each is already recorded with its grounds in the route register; what has not been done is the writing that turns seven register entries into one argument a reader outside this repository can use.

| route | role | what it contributes |
|---|---|---|
| [RT-6MP](L2-rt-6mp.md) — 6-mercaptopurine / AF-1 agonism of the fusion | `contributing` | The worked example of wild-type pharmacology failing to transfer to a fusion, which is the single most reusable argument in the set. |
| [RT-DBD](L2-rt-dbd.md) — Target the DBD / DNA binding | `contributing` | The arithmetic-over-a-fixed-fact closure — the clearest case in the register of a route closed by measurement rather than by opinion. |
| [RT-EWSR1-PROTEIN](L2-rt-ewsr1-protein.md) — Target the EWSR1 half at the protein level | `contributing` | A definitional closure: the half of the fusion that is shared with normal cells cannot discriminate for the tumour. |
| [RT-FET-LC-LIGAND](L2-rt-fet-lc-ligand.md) — A ligand for the shared FET low-complexity half | `contributing` | The same definitional closure applied to the shared low-complexity region, which is what makes the pattern a class of argument rather than a one-off. |
| [RT-HDAC-BET](L2-rt-hdac-bet.md) — HDAC / BET to lower fusion expression | `contributing` | A definitional closure on lowering expression of a driver whose expression is not the discriminating feature. |
| [RT-RXR](L2-rt-rxr.md) — RXR-heterodimer modulation of the fusion | `contributing` | A closure resting on a published measurement rather than on argument, with the one observation that would reopen it named and scanned for. |
| [RT-SYNPROMOTER](L2-rt-synpromoter.md) — Fusion-driven synthetic promoter → suicide gene | `contributing` | A closure resting on a premise about this fusion's binding specificity — reopenable on an EMC dataset, and so the paper's example of a closure that is not permanent. |

### PUB-METHODS — The failure record of a computation-only degrader program: what in-silico selectivity prediction could and could not establish

**○ `unwritten` · aimed at `journal_submission`**

A computation-only program can state, with its instruments' known-answer controls attached, exactly which of its selectivity claims its methods were able to support and which they were not — and the disclosed failures are the transferable result, because the field publishes almost none of them.

**Not written because:** Nothing blocks it. It carries no scientific blocker at all and is the only endpoint in the portfolio that is true regardless of how every other route resolves; it is finished when the writing stops.

| route | role | what it contributes |
|---|---|---|
| [RT-METHODS-PAPER](L2-rt-methods-paper.md) — The honest methods paper on the degrader program's o | `primary` | The whole paper: the program's disclosed failures, each with the known-answer control that produced it. |

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

### PUB-TCIP — Transcriptional chemically-induced proximity on EWSR1::NR4A3: reach enumeration for an effector second terminus

**○ `unwritten` · aimed at `preprint`**

The reach enumeration built for E3 recruitment applies unchanged when the second terminus is a transcriptional effector rather than a ligase, and the geometric envelope it returns either does or does not admit an effector at the distances the modality requires.

**Not written because:** The paired anchor-plus-effector enumeration has not been run for this configuration, so there is no result to report. The machinery exists and takes one more anchor set.

| route | role | what it contributes |
|---|---|---|
| [RT-TCIP](L2-rt-tcip.md) — TCIP — transcriptional chemically-induced proximity  | `primary` | The reach enumeration with a transcriptional-effector second terminus, reusing the E3-free machinery — the run that has not happened yet. |

## Every route, and where it ends

*The same edges from the other end. `readiness` is what the ROUTE could become today; `aimed at` is what its PAPER is for — and the gap between the two columns is the honest statement of what is left to do.*

| route | family | readiness today | endpoint | aimed at | role |
|---|---|---|---|---|---|
| [RT-ANDGATE](L2-rt-andgate.md) | [ST-PROXIMITY](L1-st-proximity.md) | `internal_note` | **PUB-ANDGATE** ◐ | `preprint` | `primary` |
| [RT-ASO](L2-rt-aso.md) | [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) | `chemrxiv` | **PUB-ASO** ◐ | `chemrxiv` | `primary` |
| [RT-ASO-ASK](L2-rt-aso-ask.md) | [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) | `experimental_proposal` | **PUB-ASO** ◐ | `chemrxiv` | `contributing` |
| [RT-ATR-ASSESS](L2-rt-atr-assess.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `preprint` | **PUB-ATR** ◐ | `preprint` | `primary` |
| [RT-ATR-PANEL](L2-rt-atr-panel.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `experimental_proposal` | **PUB-ATR-PANEL-ASK** ◐ | `experimental_proposal` | `primary` |
| [RT-6MP](L2-rt-6mp.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-CLOSED-ROUTES** ○ | `preprint` | `contributing` |
| [RT-DBD](L2-rt-dbd.md) | [ST-FUSION-DIRECT](L1-st-fusion-direct.md) | `internal_note` | **PUB-CLOSED-ROUTES** ○ | `preprint` | `contributing` |
| [RT-EWSR1-PROTEIN](L2-rt-ewsr1-protein.md) | [ST-FUSION-DIRECT](L1-st-fusion-direct.md) | `internal_note` | **PUB-CLOSED-ROUTES** ○ | `preprint` | `contributing` |
| [RT-FET-LC-LIGAND](L2-rt-fet-lc-ligand.md) | [ST-FUSION-DIRECT](L1-st-fusion-direct.md) | `internal_note` | **PUB-CLOSED-ROUTES** ○ | `preprint` | `contributing` |
| [RT-HDAC-BET](L2-rt-hdac-bet.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-CLOSED-ROUTES** ○ | `preprint` | `contributing` |
| [RT-RXR](L2-rt-rxr.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-CLOSED-ROUTES** ○ | `preprint` | `contributing` |
| [RT-SYNPROMOTER](L2-rt-synpromoter.md) | [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) | `internal_note` | **PUB-CLOSED-ROUTES** ○ | `preprint` | `contributing` |
| [RT-ASYMMETRIC](L2-rt-asymmetric.md) | [ST-OCCUPANCY](L1-st-occupancy.md) | `reproducible_workflow` | **PUB-DEGRADER** ◐ | `journal_submission` | `contributing` |
| [RT-COVALENT-PROBE](L2-rt-covalent-probe.md) | [ST-OCCUPANCY](L1-st-occupancy.md) | `internal_note` | **PUB-DEGRADER** ◐ | `journal_submission` | `contributing` |
| [RT-DEGRADER](L2-rt-degrader.md) | [ST-PROXIMITY](L1-st-proximity.md) | `preprint` | **PUB-DEGRADER** ◐ | `journal_submission` | `primary` |
| [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md) | [ST-IMMUNO](L1-st-immuno.md) | `preprint` | **PUB-DEGRADER** ◐ | `journal_submission` | `contributing` |
| [RT-UBIQ-SELECTIVE](L2-rt-ubiq-selective.md) | [ST-PROXIMITY](L1-st-proximity.md) | `internal_note` | **PUB-DEGRADER** ◐ | `journal_submission` | `contributing` |
| [RT-ICI-TKI](L2-rt-ici-tki.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-EMC-PROGRAM** ◐ | `journal_submission` | `context` |
| [RT-TRABECTEDIN](L2-rt-trabectedin.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-EMC-PROGRAM** ◐ | `journal_submission` | `context` |
| [RT-VACCINE](L2-rt-vaccine.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-HLA-COVERAGE** ◐ | `preprint` | `primary` |
| [RT-METHODS-PAPER](L2-rt-methods-paper.md) | [ST-DISSEMINATION](L1-st-dissemination.md) | `journal_submission` | **PUB-METHODS** ○ | `journal_submission` | `primary` |
| [RT-MONOVALENT](L2-rt-monovalent.md) | [ST-OCCUPANCY](L1-st-occupancy.md) | `internal_note` | **PUB-MONOVALENT** ◐ | `internal_note` | `primary` |
| [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-NEOANTIGEN** ◐ | `preprint` | `primary` |
| [RT-TCR-IMMTAC](L2-rt-tcr-immtac.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-NEOANTIGEN** ◐ | `preprint` | `contributing` |
| [RT-AF3-INTERFACE](L2-rt-af3-interface.md) | [ST-PROXIMITY](L1-st-proximity.md) | `internal_note` | **PUB-PARKED-MODALITIES** ○ | `preprint` | `contributing` |
| [RT-CRISPR-CAS13](L2-rt-crispr-cas13.md) | [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) | `internal_note` | **PUB-PARKED-MODALITIES** ○ | `preprint` | `contributing` |
| [RT-GLUE](L2-rt-glue.md) | [ST-PROXIMITY](L1-st-proximity.md) | `internal_note` | **PUB-PARKED-MODALITIES** ○ | `preprint` | `contributing` |
| [RT-RIBOZYME](L2-rt-ribozyme.md) | [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) | `internal_note` | **PUB-PARKED-MODALITIES** ○ | `preprint` | `contributing` |
| [RT-RIPTAC](L2-rt-riptac.md) | [ST-PROXIMITY](L1-st-proximity.md) | `internal_note` | **PUB-PARKED-MODALITIES** ○ | `preprint` | `contributing` |
| [RT-CARFILZOMIB](L2-rt-carfilzomib.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-REPURPOSING** ◐ | `preprint` | `primary` |
| [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `internal_note` | **PUB-REPURPOSING** ◐ | `preprint` | `contributing` |
| [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) | [ST-REPURPOSING](L1-st-repurposing.md) | `experimental_proposal` | **PUB-REPURPOSING** ◐ | `preprint` | `contributing` |
| [RT-B7H3](L2-rt-b7h3.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `primary` |
| [RT-CART-SURFACE](L2-rt-cart-surface.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `contributing` |
| [RT-FAP-RLT](L2-rt-fap-rlt.md) | [ST-RADIOLIGAND](L1-st-radioligand.md) | `internal_note` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `contributing` |
| [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md) | [ST-IMMUNO](L1-st-immuno.md) | `experimental_proposal` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `contributing` |
| [RT-SSTR2](L2-rt-sstr2.md) | [ST-RADIOLIGAND](L1-st-radioligand.md) | `experimental_proposal` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `contributing` |
| [RT-TCRT-CTA](L2-rt-tcrt-cta.md) | [ST-IMMUNO](L1-st-immuno.md) | `internal_note` | **PUB-SURFACE-TARGETS** ◐ | `preprint` | `contributing` |
| [RT-SYNLETH-DEP](L2-rt-synleth-dep.md) | [ST-DEPENDENCY](L1-st-dependency.md) | `internal_note` | **PUB-SYNLETH** ◐ | `internal_note` | `primary` |
| [RT-TCIP](L2-rt-tcip.md) | [ST-PROXIMITY](L1-st-proximity.md) | `reproducible_workflow` | **PUB-TCIP** ○ | `preprint` | `primary` |

## What this page deliberately leaves out

- **Whether the science is any good.** `drafted` means a file exists. It says nothing about whether the draft holds up — that is the route pages, their instruments, and whether those instruments recovered a known answer.
- **Every other L3 document.** Only a document that IS a route's endpoint appears here. Memos, plans, red-teams and outreach packages also declare `level: L3` and are not deliverables; `systems_check --check` reports their count as `[B7]` rather than listing them, because warning on them would train the reader to ignore the check.
- **Order.** Nothing on this page ranks the endpoints. What to do next is [the plan](plan.md).

[← L0](L0-ecosystem.md)
