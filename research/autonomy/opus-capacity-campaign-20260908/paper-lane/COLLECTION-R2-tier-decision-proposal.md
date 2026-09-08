# R2 — collection: a reviewable tier-decision PROPOSAL (nothing applied)

Collected 2026-09-08 ~11:30 UTC. ⛔ **Nothing in this record is applied to any manuscript.** R2's
output is a **reviewable candidate**, not a recovered original and not an applied revision. The
**final version and integration decision belongs to the scientific coordinator** under existing
authority — this does not create a per-item human approval queue, and publication permissions remain
separate.

| item | measured |
|---|---|
| child | `aefc59707cb2a5225` |
| model strings | **`claude-opus-5` only** — from transcript model fields |
| tool pairs | **16** (self-reported 9) |
| **full lifetime** | **from the original transcript**, retained in the artifact set |
| shared writes | **none** — verified: `git status` empty at its start and end |

## The verdict: REGRADE TO T2 — and the grade question is decidable on the committed text

**The paper's own definitions, which I re-read at lines 211-213 to confirm the quotation:**

> "T3 denotes **prospective or substantial** clinical evidence in EMC; T2, **a case-level signal in
> EMC** or in a very close relative"

**The evidence under the grade:** one single-patient case report — a *KIT* exon-11-mutant patient with
3 years of stable disease, reference [7]. The other imatinib-adjacent figures (1/20, 2/48) are
**mutation-prevalence**, not treatment evidence, and cannot raise a treatment-evidence tier.

**The argument:** T3 requires *prospective* **or** *substantial*. A retrospective single-patient report
is **neither** — and the same paper contrasts it with multicentre phase-2 evidence. T2's first
disjunct, "a case-level signal in EMC", matches **exactly**, with no analogy needed. So the committed
T3 grade **contradicts the paper's own definition of T3**.

⚠ This is an **internal-consistency** finding only. No efficacy, safety, selectivity or
clinical-readiness claim; R2 did not retrieve or read [7], assessing it as the committed file
characterises it.

## Parent verification of the dependent map

I enumerated every `T3` mention myself: **six** — line 112 (abstract scale), 211 (definition), 275
(figure caption), **416 and 523 (the only two asserting imatinib's grade)**, and 577 (firewall rule).
Table 1 carries **zero** tier tokens, and **§2.7 does not exist** (Methods run 2.1-2.6).

⭐ **So three of the response's named propagation targets — Table 1, §6 and §2.7 — have no counterpart
in the committed file.** That is an observation about the two documents, not a history claim.

## What is decidable, and what is not

- **Decidable:** the grade itself, against the paper's own wording.
- **UNDECIDABLE on committed evidence:** whether the scale should stay four-valued with T3
  defined-but-empty, or collapse to three values as the response describes. That is an **editorial
  choice for the owner**, not an evidential one. R2 drafted both options rather than choosing.

## The registry tension — stated precisely, left unresolved

The committed firewall (§5, 575-578) admits **only T3** to the cited clinical registry, and the Figure
1 caption repeats it. But imatinib **is already in** that registry. **Regrading to T2 would make the
paper assert an admission rule its own registry entry violates.** R2 set out three resolution shapes —
restate the rule by evidence *kind* (as §2.6 already does); keep the tier rule and re-examine the
entry; or separate "cited clinical registry" from "patient-facing material", which the sentence
conflates — and **chose none, applied none**. Correct.

## Explicit UNRESOLVED list, carried forward

1. Scale arity (four-valued vs three-valued). 2. The firewall rule. 3. Whether
`repurposing-fig1-design.png` renders the tier token — **unknown, not zero**; not opened, not
regenerable here. 4. Which draft is canonical. 5. The response's §2.7/Table 1 targets have no
counterpart. 6. The 25-vs-22 reference mismatch — untouched, **no reference added**.

## Deliverables, in the lane only

`MEMO-R2-tier-decision.md`, `CANDIDATE-A-T2.diff`, `CANDIDATE-A-T2-repurposing-hypotheses.md`,
`OPTION-B-scale-collapse-fragments.md`, and both baselines. Retained in
`R2-executed-artifacts/`; `/tmp/claude-0/r2-lane/` intact, nothing deleted.
