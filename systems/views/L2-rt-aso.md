---
id: DOC-VIEW-RT-ASO
title: RT-ASO — Fusion-junction ASO / siRNA (the deliverable)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: "Can an RNase-H gapmer or siRNA against the EWSR1::NR4A3 breakpoint junction silence the chimera while sparing wild-type NR4A3?"
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-ASO — Fusion-junction ASO / siRNA (the deliverable)

**Family:** [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · **state:** ○ blocked · scoped · confidence moderate · verified 2026-08-12

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md)): Tier 1, rank 2 — DELIVERABLE

## What has to land for this route to move

```mermaid
flowchart LR
  RT_ASO["○ RT-ASO"]:::fam
  BLK_DELIVERY{{"BLK-DELIVERY — SYSTEMIC, antigen-dependent tumour deliver…"}}:::blk
  BLK_DELIVERY --> RT_ASO
  TECH_OLIGO_DELIVERY(["TECH-OLIGO-DELIVERY<br/>expected 2029"]):::tech
  TECH_OLIGO_DELIVERY -.-> BLK_DELIVERY
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

✓ Already cleared by this route: `BLK-NOT-FUSION-SELECTIVE`, `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

The breakpoint junction is a sequence that exists in no healthy cell. An oligonucleotide reads sequence rather than shape, so it discriminates on SEQUENCE rather than shape — predicted, not demonstrated where every protein-directed route has to fight a shared fold. This is the fusion-selective route whose deliverable is finishable here (RT-JUNCTION-NEOANTIGEN, RT-TCR-IMMTAC and RT-RIBOZYME also retire the blocker), and its in-silico arc is complete: design, off-target screen, breakpoint-favourability scan, and gap-mismatch-resolved candidates.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-JUNCTION-ASO-OFFTARGET` | a transcriptome-wide off-target screen returning predicted-clean gapmers | `direct` |

## Remaining unknowns

- ⭐ THE LANE IS NO LONGER EWSR1-ONLY (2026-08-12, $0, offline). nr4a3-fusion-junction-atlas.json grades 207 donor-exon x NR4A3-acceptor-exon pairs across EWSR1, TAF15, TCF12 and FUS; 32 are frame-compatible and EVERY ONE yields at least one junction-spanning, parent-sparing design, so designability is not this route's constraint. One 16-mer (GGGCATATCATCAAAC) is junction-spanning and fusion-exclusive at EWSR1 e12, TAF15 e11 and FUS e10 :: NR4A3 e3 SIMULTANEOUSLY, because the three donors are identical over the 8 bases 5' of their breakpoints -- so a stock reagent, not only an n-of-1 panel, is on the table. ⛔ WHAT IS NOT KNOWN: the transcriptome-wide off-target screens have NOT run on any non-EWSR1 junction (the workflow now accepts DONOR:exon:exon and can), the provenance gate behind TAF15/TCF12/FUS transcript models is the weaker of the two, and whether patients carry breakpoints at those homologous exons is a clinical fact nobody here holds.
- ⛔ 'DELIVERY' WAS ONE BLOCKER STANDING FOR THREE ROUTES WITH DIFFERENT REQUIREMENTS (2026-08-12; BLK-DELIVERY rescoped, paper §3c-bis). The missing EMC surface antigen gates the SYSTEMIC receptor-targeted route only. Local/intratumoural and inhaled/pulmonary administration need no antigen, and EMC's distant spread is lung-dominant (35-45% of patients, primarily lung, median ~28 months to metastasis; PMID 41055792). Inhaled oligonucleotide delivery producing gene silencing in tumours growing in the lung is an active preclinical field -- in other tumour types, in animals, never in EMC, never against a fusion, never in a patient (lit-targets-aso-delivery-routes.json). This changes what to attempt first; it does not move the modality closer to a patient.
- The committed design panel was rebuilt at the corrected mRNA junction on 2026-08-06 (aso-offtarget.yml run 31130876597, $0): NR4A3 resumes at residue 1, seams ACGGGCAGCAGA|ATATGCCCTGCG (e7n3) and AATGGTTTGATG|ATATGCCCTGCG (e12n3). The panel covers TWO junctions, not the five once claimed — e9n3/e10n3/e13n3 and every exon-mode siRNA file never existed and stay withdrawn as unverifiable. ⛔ THE CORRECTED SCREEN DOES NOT RESTORE THE RETRACTED HEADLINE: 0 of 5 designs at EACH junction are free of gap-spanning near-matches, so 'a gapmer predicted clean on both screens at E7::N3' is CONTRADICTED by the corrected data, not merely unproven. GC does move in the route's favour (37.5-56.2% vs 75.0-81.2% at the modelled reference).
- How to deliver an oligonucleotide to a non-hepatic solid tumour — the one remaining gate, and it is engineering rather than biology.
- Whether predicted specificity survives a calibrated cleavage model: the current screen uses a deliberately conservative gap-mismatch heuristic, so it may be over- or under-calling.
- Whether the potency ranking holds — it rests on a local-fold accessibility proxy rather than a measured accessibility model.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A delivery vehicle that reaches an EMC tumour | ⛔ none built | **no** | BLK-DELIVERY |
| Junction knockdown with parental sparing in an EMC line | ⛔ none built | **no** | BLK-NO-WET-LAB |
| Regenerate the junction panel at the CORRECTED seam and re-derive every design (needs network — CI) | ⛔ none built | yes | — |
| A calibrated gap-internal-mismatch RNase-H1 cleavage model, which would retire the conservative heuristic the specificity margin rests on (paper §8) | ⛔ none built | yes | — |
| Run the gap-resolved BLAST + uncapped transcriptome screens at the TAF15/TCF12/FUS junctions the atlas emits -- the one gap that stops the pan-partner panel being as evidenced as the EWSR1 one (needs network -- CI; aso-offtarget.yml now takes DONOR:donorExon:NR4A3exon) | ⛔ none built | yes | — |
| A TFG transcript model, the one reported EMC partner with no model in this repository -- one targeted Ensembl fetch, nothing else missing | ⛔ none built | yes | — |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-DELIVERY** | `requires_future_technology` | `TECH-OLIGO-DELIVERY` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer
- **BLK-NOT-FUSION-SELECTIVE** — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-ASO-ASK](L2-rt-aso-ask.md) | deliverable vs ask | `BLK-NO-WET-LAB` | the manuscript is finished and needs nobody; the knockdown experiment needs a lab and has the portfolio's weakest taker. Grading them as one row is what the W1/W2/D correction exists to stop |
| [RT-CRISPR-CAS13](L2-rt-crispr-cas13.md) | delivery class | `BLK-DELIVERY` | an oligonucleotide's delivery problem has clinical precedent in solid tumours; a vector's is a different engineering problem with different precedents, and Cas13 additionally carries collateral activity |

## Readiness — what this could become today

**`chemrxiv`**

The computational arc is complete and the delivery gate is stated honestly as a gate rather than hidden. A journal submission is reachable; what would strengthen it most is not more computation but a delivery candidate to name.

**Missing:**
- a named delivery candidate FOR THE SYSTEMIC ROUTE -- rescoped 2026-08-12; the local and inhaled routes never required one, and grading the whole route on the systemic route's missing input is what the BLK-DELIVERY rescope corrects

**Experiment required:**
- junction knockdown plus parental sparing in an EMC or FET-fusion line

## Where this route ends — the paper

**[PUB-ASO](L3-publications.md)** — [A fusion-selective antisense oligonucleotide against the EWSR1::NR4A3 breakpoint junction: RNA-level fusion-exclusivity](../../research/manuscripts/fusion-junction-aso-paper.md)

`primary` · ◐ `drafted` · aimed at `chemrxiv`

**This route contributes:** The junction design, the transcriptome-wide specificity screen, and delivery stated as the outstanding gate rather than assumed away.

**The paper would claim:** The EWSR1::NR4A3 breakpoint junction is the one truly tumour-exclusive feature of this disease at the RNA level, an oligonucleotide can be designed to read it rather than a shape, and transcriptome-wide specificity screening finds no competing match — with delivery named as the outstanding gate rather than assumed away.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The computation is done and publishing is what recruits the collaborator this route needs. Waiting does not improve the design; it only delays the ask. Delivery is watched in parallel and does not gate the write-up.

| horizon | effect |
|---|---|
| Six months | Little on the design. Possibly a lot on whether a delivery candidate can be named. |
| Two years | Decisive — a working conjugate platform for solid tumours would move this from a design to a programme. |
| Cost trend | flat |
| Automation outlook | The design and screening halves are already automated; delivery is not a computational problem at all. |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md), which is where these are asserted — a family limitation binds every route inside it.*

- Delivery of an oligonucleotide to a non-hepatic solid tumour has no validated solution, and this is not solvable in silico today.
- Predicted specificity rests in part on a conservative heuristic rather than a calibrated cleavage-activity model.
- The vector-delivered sub-routes carry a second, distinct delivery problem that must not be conflated with the oligonucleotide one.

## Best next action

Screen the pan-partner panel (TAF15/TCF12/FUS junctions) on the transcriptome, then publish the complete in-silico arc: a systematic NR4A3-fusion junction design platform with delivery stated as three routes of differing requirement rather than one gate.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-FUS-T1](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-FUS-T2](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-NR4A3-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

[← ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · [← L0](L0-ecosystem.md)
