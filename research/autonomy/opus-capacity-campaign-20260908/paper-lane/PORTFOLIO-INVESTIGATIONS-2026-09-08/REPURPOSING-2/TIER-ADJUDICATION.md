---
id: DOC-PORTFOLIO-REPURPOSING2-TIER-ADJUDICATION
title: "Does reference [19] meet the repurposing paper's own T3? — adjudication"
level: L4
kind: adjudication
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Tier adjudication — reference [19] against this paper's own T3

Lane `REPURPOSING-2`. ⛔ **Nothing is applied.** No tier, scale, firewall rule, registry entry or
reference was changed by this lane. This is an adjudication of a definition against a fact, prepared
for the coordinator who owns the decision.

## 0 · The fence that governs everything below

⛔ A three-patient subgroup of a mixed-histology trial **that missed both of its primary endpoints**
supports **no efficacy, safety, selectivity or clinical-readiness claim at any tier**. Tier placement
in this paper is a statement about **evidence class**, not about the drug working. Nothing in this
document asserts that cabozantinib works in EMC, and a T3 placement — if the coordinator adopts one —
would still assert nothing of the kind. The paper says this itself: *"The tier states how speculative
a hypothesis is, not the expected effect size."*

## 1 · The definition being judged against, quoted verbatim

From the committed manuscript, `research/manuscripts/repurposing/repurposing-hypotheses.md`
§2.2 (lines 219–226 at `git rev-parse HEAD` = `3faeaa069cf8b6231273cf90bf62d30589152b14`):

> "Each candidate is graded by the strength and proximity of its supporting evidence. **T3 denotes
> prospective or substantial clinical evidence in EMC**; T2, a case-level signal in EMC or in a very
> close relative; T1, a preclinical or in-vitro signal, or a strong analogy in a related
> fusion-driven sarcoma; T0, mechanistic rationale only. The tier states how speculative a hypothesis
> is, not the expected effect size. On the evidence assembled here, no candidate reaches T3: the
> strongest EMC-specific clinical evidence in the menu is a single published case report, which these
> definitions place at T2. **T3 is therefore defined but unoccupied**, and is retained to mark what a
> prospective or substantial EMC clinical result would look like."

Two further committed sentences bind the same words:

> §4 Tranche 1: "The assembled record supplies a case-level signal and does not establish the
> **prospective or substantial EMC clinical evidence** that this paper's definitions require for T3."

> §5 ethics: "only a candidate reaching direct EMC clinical evidence **at T3** may migrate into the
> project's cited clinical registry, **and then only after clinician review**."

## 2 · The fact being judged

Reference **[19]** — O'Sullivan Coyne G, Kummar S, Hu J, Ganjoo K, Chow WA, Do KT, et al., *Clin
Cancer Res* 2022, PMID 34716194, PMC8776602, [DOI](https://doi.org/10.1158/1078-0432.CCR-21-2480).
**Already cited by this manuscript.** According to PubMed Central, verbatim (extracted by the
PUB-REPURPOSING lane, `EVIDENCE-cabozantinib-emc.md`, and not re-fetched here):

- design: single-arm, two-stage, open-label **phase II**, multi-site, all WHO-recognised STS
  subtypes, 60 mg daily, RECIST 1.1;
- Table 1 Diagnosis: *"Extraskeletal myxoid chondrosarcoma  3"* — **3 EMC patients of 54 evaluable**;
- *"Confirmed partial responses to cabozantinib were seen in 6 patients: … 1 patient with
  extraskeletal myxoid chondrosarcoma (EMC) …"*;
- *"The longest response in this trial (now over 99 cycles) was observed in a patient with EMC."*;
- ⛔ *"Neither of the primary efficacy criteria (22% ORR or 54% 6-month PFS) were reached."*;
- ⛔ safety reported for the whole cohort only: Table 3, *"(= 54 total patients)"*.

## 3 · The adjudication

**The definition is ambiguous on exactly the point that decides this case, and I state both readings
rather than picking one.** The ambiguity is not a quibble: the two readings differ on whether the
adjective *prospective* attaches to the **study design** or to an **EMC-directed study**, and the
committed text supports each in a different place.

### Reading A — literal and disjunctive: [19] MEETS T3

T3 requires "prospective **or** substantial clinical evidence in EMC". The disjunction is satisfied
by either limb alone. [19] is a prospective trial; three of its enrolled patients had EMC; it reports
a per-patient EMC outcome. So there exists prospective clinical evidence, obtained in EMC patients,
for cabozantinib. On this reading:

- cabozantinib reaches **T3**;
- §2.2's "**no candidate reaches T3**" and "**T3 is therefore defined but unoccupied**" become false
  as written, as do the matching sentences in §4 Tranche 1, §5 first limitation, and **both the
  Figure 1 alt text and printed caption** ("no candidate in the assembled catalogue currently reaches
  T3");
- the R2/V1 premise *"nothing reaches T3"* — recorded as a **settled** coordinator decision in
  `CONTRACT-V1-repurposing-t2-candidate.md` §3 and `INTEGRATION-repurposing-t2.md` — no longer holds
  on its own terms, **not because the imatinib regrade was wrong** (it was not; see §4 below) but
  because a *different* candidate now occupies the tier that was declared empty.

The strongest textual support for Reading A is §2.2's own gloss: T3 "is retained to mark what a
prospective or substantial EMC **clinical result** would look like." [19] delivers an EMC clinical
result — one confirmed PR in an EMC patient, in a prospective trial.

### Reading B — evidentiary-weight and EMC-directed: [19] FAILS T3, and lands at T2

Both limbs of T3 aim at evidence that can support a conclusion *about EMC*: a prospective study **of**
EMC, or a **substantial** body of EMC clinical evidence. [19] is neither. It is a prospective study of
soft-tissue sarcoma in general, in which EMC is an unplanned three-patient stratum with no
EMC-specific endpoint, no prespecified EMC analysis, no EMC denominator for safety, and a trial-level
result that **missed both primary endpoints**. Three patients is not "substantial" by any reading that
leaves the word work to do — the same yardstick R2 applied when it wrote that "one patient is not
substantial by any reading that leaves the word work to do", contrasting it with the multicentre EMC
phase 2 the paper cites at §1.1. What [19] does supply is *"a case-level signal in EMC"*, which is
**T2, matched exactly**. On this reading:

- cabozantinib is **T2**, alongside imatinib;
- every "no candidate reaches T3" sentence survives, and T3 stays defined but unoccupied;
- what still must change is the **novelty** claim, exactly as PUB-REPURPOSING proposed.

The strongest textual support for Reading B is the manuscript's **own precedent**, in §4.1, for
handling this exact evidentiary shape. Of the class-level proteasome trials it writes:

> "That is a dose-finding trial which is not sarcoma-specific, and whose abstract carries no response
> rate, no comparator and no sarcoma subgroup denominator. **It is not an efficacy result.**"

and concludes that such trials settle *"the novelty claim"* — not the evidence tier. Applying the
paper's own established convention to [19] puts the cabozantinib finding in the **novelty** column,
not in the tier column. A second support: §1.1 uses "the multicentre single-arm phase 2 trial of
pazopanib **in advanced EMC**" as the paper's working exemplar of prospective EMC evidence — an
EMC-only cohort, not an EMC stratum.

### Which reading the committed text favours, and what I will not do

I do **not** pick one, because the sentence genuinely admits both and the choice is the paper owner's.
I record two asymmetries the coordinator should weigh:

1. **Reading B is more consistent with the rest of the committed document** (the §4.1 convention and
   the §1.1 exemplar), and it is the reading under which the paper needs the fewest changes.
2. **Reading A is the more natural reading of §2.2 taken alone**, and a reader who checks [19] against
   §2.2 without reading §4.1 will reach it. That is itself a defect: if the coordinator adopts
   Reading B, §2.2 should be **tightened** so it says so — e.g. that T3 requires prospective clinical
   evidence *from an EMC-directed cohort or analysis*, so that a subgroup of a mixed-histology trial
   is explicitly T2. ⛔ Tightening a definition to exclude a fact that has already been found is only
   legitimate if it states the criterion the paper was **already applying in §4.1** — which it is.
   It must not be done silently, and this lane does not do it.

## 4 · What the adjudication does NOT disturb

- **The imatinib T2 regrade stands under both readings.** R2's argument was that one retrospective
  single-patient case report is neither prospective nor substantial. Nothing found here touches that.
- **The firewall admission rule is untouched and is not triggered under either reading.** Admission
  requires T3 **and clinician review**; T3 is necessary, never sufficient. Even under Reading A,
  cabozantinib reaching T3 admits nothing to the clinical registry, and this lane proposes no registry
  change. ⛔ Any suggestion that a T3 placement licenses patient-facing material would be a misuse of
  this document.
- **The four-tier scale is untouched.** Reading A occupies T3; it does not change the scale's arity.
- **No efficacy claim exists in either direction.** Under Reading A, cabozantinib is T3 *and* the
  trial missed both primary endpoints — those are consistent, because the tier grades evidence class.

## 5 · The one thing that is true under both readings

Cabozantinib's novelty cell is wrong as committed, at **at least** T2, and the three statements
PUB-REPURPOSING identified are false as written regardless of how the tier question resolves. Its
`PROPOSED-UNAPPLIED-repurposing-cabozantinib.diff` is therefore **not blocked** on this adjudication
and can be considered on its own merits. The tier question is a separate, later decision.

## 6 · Stop condition

Reached. The definition is quoted, the fact is quoted, both readings are stated with their textual
support, the consequences of each are enumerated by location, and the decision is left with the
coordinator, who owns the shared manuscript.
