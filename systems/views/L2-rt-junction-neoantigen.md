---
id: DOC-VIEW-RT-JUNCTION-NEOANTIGEN
title: RT-JUNCTION-NEOANTIGEN — Fusion-junction neoantigen (the antigen, shared by three delivery routes)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does the fusion junction produce a peptide the immune system could see — and is it presented?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-JUNCTION-NEOANTIGEN — Fusion-junction neoantigen (the antigen, shared by three delivery routes)

**Family:** [ST-IMMUNO](L1-st-immuno.md) · **state:** ✓ blocked · computed · confidence low · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/target-route-options.md`](../../research/manuscripts/target-route-options.md#route-7--junction-neoantigen-vaccine--tcr-t--soluble-tcr)): ○ drafted — and now carrying a correction owed

## What has to land for this route to move

```mermaid
flowchart LR
  RT_JUNCTION_NEOANTIGEN["✓ RT-JUNCTION-NEOANTIGEN"]:::fam
  BLK_ANTIGEN_COLD[["BLK-ANTIGEN-COLD — EMC is antigen-cold, and the fusion ju…"]]:::perm
  BLK_ANTIGEN_COLD --> RT_JUNCTION_NEOANTIGEN
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_JUNCTION_NEOANTIGEN
  TECH_EMC_EXPRESSION_DATA(["TECH-EMC-EXPRESSION-DATA<br/>expected 2029"]):::tech
  TECH_EMC_EXPRESSION_DATA -.-> BLK_NO_EMC_DATA
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_NO_EMC_DATA
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

⛔ **1 of these is permanent** (`BLK-ANTIGEN-COLD`) — a fact about the biology, drawn double-walled, with no way out by definition. No technology arrives to fix it.

✓ Already cleared by this route: `BLK-NOT-FUSION-SELECTIVE`, `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

The junction is tumour-exclusive at the sequence level. ⚠ Whether ONE peptide is shared across breakpoints is UNSETTLED — the committed analysis found no pan-EMC epitope (the most-shared candidate appears in 2 of 7 junctions and is a weak binder) — and it was computed on seams the corrected exon index does not produce, so even that reading is void pending regeneration.

## Remaining unknowns

- The breakpoint-RESOLVED predictions remain VOID: they span seams the corrected exon index does not produce, and that artifact is not regenerated. The SINGLE-junction artifact WAS regenerated 2026-08-06 at the corrected mRNA junction (EWSR1 e7 :: NR4A3 e3): the seam carries a novel codon (AAT = Asn) from 1 leftover EWSR1 nt plus 2 retained acceptor-5'UTR nt, then NR4A3 Met1 — giving 38 junction peptides, 3 predicted binders and a lead of NMPCVQAQY on HLA-B*15:01. ⛔ Predicted binding is a SCREEN, not presentation and not immunogenicity.
- Whether a junction peptide is presented at all, and at what level — EMC is antigen-cold.
- Whether the peptide-HLA is strong enough to be a target rather than merely present.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Regeneration of the predictions against the corrected exon index | ⛔ none built | yes | — |
| Measured presentation on EMC tissue | ⛔ none built | **no** | BLK-ANTIGEN-COLD, BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-ANTIGEN-COLD** | `fundamental_biological_limit` | *permanent* |
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer
- **BLK-NOT-FUSION-SELECTIVE** — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-VACCINE](L2-rt-vaccine.md) | delivery of the same antigen | `BLK-ANTIGEN-COLD` | the antigen is one object; the vaccine, the TCR-T and the soluble TCR are three different products with different failure modes, and the board has graded them as one row |
| [RT-TCR-IMMTAC](L2-rt-tcr-immtac.md) | delivery of the same antigen | `BLK-ANTIGEN-COLD` | same antigen, engineered-cell or soluble-bispecific product rather than an immunisation |

## Readiness — what this could become today

**`internal_note`**

Half is done and half is not, and the halves must not be read together. The SINGLE-junction artifact (fusion-neoantigen-predictions.json) was regenerated 2026-08-06 against the corrected exon index and its banner is cleared. The breakpoint-RESOLVED artifact is still retracted and its module still carries the transcript/coding slip, so §2 of the neoantigen paper stays withdrawn.

**Missing:**
- regenerated predictions for the breakpoint-RESOLVED artifact (fusion-breakpoint-neoantigens.json), which is still retracted

## Where this route ends — the paper

**[PUB-NEOANTIGEN](L3-publications.md)** — [Targeting the EWSR1::NR4A3 fusion-junction neoantigen in extraskeletal myxoid chondrosarcoma: a fusion-exclusive immunot](../../research/manuscripts/fusion-junction-neoantigen-paper.md)

`primary` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The junction peptide and its presentation predictions, which must be regenerated against the corrected exon index before any of them can be reported.

**The paper would claim:** The fusion junction produces a peptide sequence that is absent from wild-type EWSR1 and wild-type NR4A3 — ⚠ the only novelty test in this repo compares against those two PARENT proteins (`fusion_breakpoints.py:231`) and NO proteome-wide search has ever been run, so 'absent from the normal proteome' is not a claim this work can make, and whether any allele presents it is a prediction that must be regenerated against a corrected exon index before it can be reported at all.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The blocking defect is an input error this program made and can fix for nothing. Waiting on any external capability while a free self-inflicted defect stands unrepaired is the wrong order.

| horizon | effect |
|---|---|
| Six months | None — the fix is available now. |
| Two years | Presentation prediction is improving, but the void result must be repaired first regardless. |
| Cost trend | flat |
| Automation outlook | Fully automatable; it is a regeneration. |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-IMMUNO](L1-st-immuno.md), which is where these are asserted — a family limitation binds every route inside it.*

- EMC is antigen-cold and the fusion junction is a weak peptide-HLA — a property of this tumour and this junction, not of any modality here.
- Surface-antigen selectivity was measured on cell-line surrogates rather than on EMC tissue, so the negatives are as provisional as the positives would have been.
- One route's predicted binders span junction seams that a corrected exon index says do not exist; that result is void and the question is open.

## Closure

`unregenerable_artifact` — ⚠ THE TWO HALVES, KEPT APART: the 26 predicted binders are unusable because they span seams that do not exist — that RESULT is void. The QUESTION is open and one free regeneration answers it.

## Best next action

Regenerate the junction-neoantigen predictions against the corrected exon index, then re-grade. Every predicted binder currently spans a seam no reported junction produces.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

| L4 instrument | cited as | known-answer control |
|---|---|---|
| [INS-HLA-COVERAGE](registers/instruments.md) — HLA population-coverage calculator | **disclosed failing** | `none` |

**L5 objects:** [OBJ-FUS-T1](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-FUS-T2](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-MODEL-E7E3](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

**L5 artifacts:** [ART-HLA-COVERAGE](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-IMMUNO](L1-st-immuno.md) · [← L0](L0-ecosystem.md)
