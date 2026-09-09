---
id: DOC-PORTFOLIO-INVESTIGATION-FUSION-OUTPUT-4-SINGLE-PLATFORM-20260909
title: "Dropping GPL3290 rather than waiting for it: the single-platform pre-registration costs zero detectable effect and one guard"
level: L4
kind: design-arithmetic
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# FUSION-OUTPUT-4 — what the pre-registration becomes if GPL3290 is dropped

**Design arithmetic only. No expression value was read, no contrast was computed, the outcome
protocol was not opened, and no biological claim is made anywhere in this lane.** The executable
outcome protocol remains a coordinator-owned frozen gate; nothing here opens it, pre-empts it or
confers authority to run anything. Nothing here can establish efficacy, safety, selectivity, a
therapeutic window or clinical readiness.

## 1 · The question

FUSION-OUTPUT-3 split the pre-registration's platform prerequisite cleanly: **GPL6244 passes both
floors in all six cells**, and **GPL3290 is undeterminable offline in all six** because the
EST-accession bridge is built at run time from GEO and no bridge artifact exists in this checkout.
That leaves a design question, answerable entirely from committed artifacts:

**what does the pre-registration look like if GPL3290/GSE4303 is DROPPED rather than waited for?**

## 2 · Merit

The pre-registration is currently blocked on an artifact nobody in this fence can fetch. Waiting is
not the only option: the arm that is blocked is also the arm the design already graded **circular**
for these very claims and assigned corroborative weight only. Whether a design can proceed without
it is a decision the coordinator will have to make, and it should be made against arithmetic rather
than intuition — because the intuition ("we lose the bigger cohort, so we lose power") turns out to
be wrong in a way that matters, and because the thing actually lost is a *guard*, which is exactly
the kind of loss a design change can make silently. Patient relevance is indirect but real: it
decides whether a scarce EMC-tumour dataset gets spent on a test, and on what evidentiary terms.

## 3 · The evidence gap, and what distinguishes it

The gap is not new data. It is that **no one has costed the drop**. FUSION-OUTPUT-2 computed
detectability for a two-cohort design and declared two prerequisites; FUSION-OUTPUT-3 resolved one
prerequisite and left the other pending on a named missing file. Neither asked what the design's own
numbers become when one arm is removed by decision instead of by measurement. The inputs are all
committed: the frozen membership TSV, the source packet's GPL6244 gene-to-probes map, and
FUSION-OUTPUT-2's own MDE formula and conventions.

## 4 · The step taken

`single_platform_design.py` (scipy analytic, no network, no data matrix) re-derives the sets and the
GPL6244 coverage **from the primary inputs**, recomputes the detectability arithmetic for a
GPL6244-only design using FUSION-OUTPUT-2's formula unchanged, and evaluates each pre-registration
clause under the drop. `selfcheck_mde_agreement.py` compares every recomputed number against
FUSION-OUTPUT-2's published `design-power.json`.

### 4.1 · Re-derivation — every number reproduces exactly

Re-implemented from `outputs/common-platform-membership.tsv` (subtraction redone from the TSV rows,
not read out of any prior lane's JSON) and checked member by member against
`GPL6244-gene-to-probes.json` (21,407 symbols):

| window | contrast | n | readable on GPL6244 | coverage | both floors |
|---|---|---:|---:|---:|---|
| 1000 | A | 23 | 23 | 1.000 | PASS |
| 1000 | B | 4 | 4 | 1.000 | PASS |
| 2000 | A | 40 | 40 | 1.000 | PASS |
| 2000 | B | 7 | 7 | 1.000 | PASS |
| 5000 | A | 57 | 57 | 1.000 | PASS |
| 5000 | B | 6 | 6 | 1.000 | PASS |

**Zero mismatches** in set size, in gene-by-gene membership against FUSION-OUTPUT-2's frozen sets, or
in coverage against FUSION-OUTPUT-3 (`step_1_crosscheck.all_reproduce = true`; selfcheck exit 0).
Set sizes are 23/4, 40/7, 57/6 as stated. The floors 0.4 and 4 are used exactly as the manuscript
states them; none was lowered, softened or reinterpreted.

### 4.2 · What dropping GSE4303 costs — the central number is zero

Primary window, ρ = 0.2, α = 0.05, FUSION-OUTPUT-2's formula and conventions unchanged:

| | contrast A (m=40) | contrast B (m=7) |
|---|---:|---:|
| two-cohort design, GSE24369 arm | 0.6074 | 0.7259 |
| **single-platform design** | **0.6074** | **0.7259** |
| **change in MDE from the drop** | **0.0000** | **0.0000** |
| GSE4303 arm's own MDE, had it been kept | 0.7297 | 0.8722 |

**The MDE cost of dropping GSE4303 is exactly zero**, because the pre-registration never pools: §3.1
requires elevation on each series separately and S5 forbids pooling on disagreement, so each series'
MDE is computed at its own *n*. Removing one series leaves the other's arithmetic untouched, digit
for digit — the recomputation agrees with `design-power.json` on all 60 MDE values and all 30
*m*<sub>eff</sub> values.

And the dropped arm was **the weaker one at every ρ**: 0.7297 vs 0.6074 for A, 0.8722 vs 0.7259 for B.

**The sample accounting makes the point sharper.** The drop sets aside **10 of the design's 16 EMC
tumours — 62.5% of the EMC material** — and 6 of 35 comparators, and still costs zero detectable
effect. That is not a paradox: **a cohort that cannot carry a positive contributes no power to a
design that never pools.** §6.2 makes GSE4303 corroborative only and §3.1 declares a positive
existing on GSE4303 alone UNINTERPRETABLE, so the pre-registration had already withdrawn from it
every inferential role that power could serve.

**A counterfactual, labelled as one.** Had pooling been permitted — it is not, by §3.1 and S5, and it
would pool a circular cohort into a non-circular one — the pooled MDE would be 0.4046 (A) and 0.4836
(B), i.e. 0.2027 and 0.2423 better. **That is not a loss, because the design never had it.** It is
reported only to bound what a different, forbidden design could in principle have offered.

### 4.3 · What IS lost is a guard, and it is priced

The two-cohort §3.1 positive required elevation **on both series**. One series makes that conjunction
vacuous. Nominal accounting, assuming independent arms:

| | two-cohort conjunction | single platform |
|---|---:|---:|
| nominal joint false-positive rate | 0.0025 | 0.05 (**20×**) |
| joint power at each arm's own MDE | 0.64 | 0.80 |

So the drop **raises power from 0.64 to 0.80 and raises the level from 0.0025 to 0.05**. Holding the
old level on one cohort costs effect size: contrast A at 2 kb, ρ = 0.2 needs **0.8679** per-gene SD
at α = 0.0025, against 0.6074 at α = 0.05 (and 0.8943 at α = 0.05/28 for the 28 alternative
programs). One of those two must be pre-declared.

Both halves of that accounting are themselves optimistic in the direction that flatters the two-cohort
design: the arms are **not** independent — they score the same gene set and GSE4303 is graded circular
for exactly these claims — so 0.0025 **overstates** the protection the conjunction actually bought and
0.64 **understates** its joint power.

### 4.4 · Clause by clause

* **S1 (coordinator gate)** — unchanged and binding.
* **S2 (GPL3290 floors)** — **DISSOLVED BY THE DROP, NOT SATISFIED.** With no GPL3290 arm, S2 has no
  referent. FUSION-OUTPUT-3 left it undeterminable in all six cells; dropping the platform removes
  the question rather than answering it. This is a recorded design change with the cost above, **not
  a floor waiver.**
* **S3 (do not run contrast B)** — unchanged and binding; see §5.
* **S4 (no post-hoc set change)** — unchanged and binding; the sets were re-derived and none changed.
* **S5 (direction disagreement)** — **VOID**: with one series it can never fire. It must be replaced,
  not deleted.
* **§3.1 UNINTERPRETABLE** — two clauses go void ("the two series disagree in direction"; "the result
  is carried by GSE4303 alone"). Three survive (indistinguishable from the exact global offset;
  coverage/member floors on the scored platform; alternative-fusion programs scoring comparably).
  **The two void clauses were guards; their removal makes a positive easier to declare.**
* **§6.1 (coverage)** — satisfied exactly, and now *verified* member by member rather than assumed
  "by construction".
* **§6.2 (circularity)** — moot; the circular cohort is the one dropped.
* **§6.3 (comparator composition)** — unchanged, and **now the whole comparator basis**: FET-vs-FET
  (LGFMS, *FUS::CREB3L2*), 23 of 29 myxoid. This limitation gains weight under the drop. It is the
  surviving interpretive constraint.

**Three replacement rules the artifact records as required** if the drop is adopted: a within-series
window-reporting rule in place of S5; an explicit advance choice between α = 0.0025 (holding the old
level) and α = 0.05 with the result labelled **unreplicated**; and language discipline — any positive
is "elevated in one series of 6 EMC tumours against 29 FET-rearranged comparators", never
"replicated". Quoting the two-cohort MDE while testing at the single-cohort level is the failure mode
this artifact exists to prevent.

## 5 · Runnability, stated plainly

**Contrast A becomes runnable under a single-platform design** — in the design sense only: every
prerequisite a design document can discharge is discharged. Coverage 1.000 with 40 readable members
at the primary window (36 dropouts of headroom); the rank statistic against 28 alternative programs
still reaches α = 0.05 (minimum one-sided *p* = 1/29 = 0.0345); the pending GPL3290 prerequisite and
the circularity prerequisite both disappear with the dropped arm. It is powered for **0.6074** per-gene
SD at ρ = 0.2, α = 0.05 — a large, set-wide elevation, exactly as before. **The run itself remains
gated by S1, which this lane does not open.**

**Contrast B does not become runnable.** The no-go is untouched and is not this lane's to overturn:
minimum attainable one-sided rank *p* = **1/4 = 0.25** against the other three NR4A3 programs, which
**cannot reach α = 0.05 at any effect size**; window-invariant core of **3 genes**, below the
manuscript's own 4-gene floor; and at 1 kb the set is exactly 4 readable genes on GPL6244, so a single
dropout drops it below the floor. Both facts are platform-independent.

**What did change for B:** its readability is now *settled* rather than unknown — all three windows
clear both GPL6244 floors exactly — so FUSION-OUTPUT-3's named dependency on *BAZ2A, FAXC, FBXO21,
FOXA1, HAP1, IDH1, TBX21* dissolves. That removes a blocker without making the contrast informative.
**The S2 readability blocker for B goes away; the §4.3 numeric no-go stays, and it is the binding one.**

## 6 · Artifact · validation · provenance · limitations · stop condition

**Artifact.** `single-platform-design.json`; generators `single_platform_design.py` and
`selfcheck_mde_agreement.py`. Every MDE assumption is restated in the artifact's
`assumptions_every_one_biasing_the_mdes_optimistically` field and each is labelled for the direction
of its bias, as FUSION-OUTPUT-2 did — **A1** unit per-gene z variance, **A2** a single exchangeable ρ,
**A3** a common per-gene effect, **A4** df = *n*₁+*n*₂−2, **A5** coverage 1.000 treated as *m* = *n*,
and **A6** (new, single-platform-specific) the level trade of §4.3. **All six bias the numbers
optimistically: the true detectable effects are larger than printed, never smaller.**

**Validation.** Two independent agreements, both machine-checked. (i) The sets and GPL6244 coverage
are re-derived from the primary inputs by a separately written subtraction and matched gene by gene
against FUSION-OUTPUT-2's frozen sets and FUSION-OUTPUT-3's coverage — zero mismatches. (ii)
`selfcheck_mde_agreement.py` compares all 60 recomputed MDEs and all 30 *m*<sub>eff</sub> values
against `design-power.json` — zero mismatches, exit 0. A discrepancy in either would have been
reported digit for digit and stopped the lane.

**Provenance.** `common-platform-membership.tsv` and `GPL6244-gene-to-probes.json` from the
coordinator-frozen packet `research/autonomy/nr4a3-program-source-2026-09-07`, read in place in the
frozen corpus and hashed by the generator; FUSION-OUTPUT-2's `fusion-program-testsets.json` and
`design-power.json` and FUSION-OUTPUT-3's `platform-coverage.json` read for cross-check only, also
hashed. Full digests in `single-platform-design.json#inputs`. Cohort sample counts are metadata from
PUB-FUSION-OUTPUT §2.2. No network, no GPU, no spend, no expression matrix opened, no outcome protocol
opened. Nothing written outside this lane; no `git add`/commit/push, no preflight, no subagent.

**Limitations.** This is arithmetic about a design, not evidence about EMC. Every MDE rests on the six
optimistic assumptions above. The level accounting in §4.3 assumes independent arms and is therefore
itself approximate in a stated direction. Dropping a platform is a **decision**, not a determination:
it does not answer FUSION-OUTPUT-3's open question, and the GPL3290 bridge remains the named missing
artifact should the coordinator prefer to wait. All of the completed lane's limitations carry forward
verbatim — HEK293T, ectopic, accessibility not occupancy, not EMC material, promoter ±2 kb only,
positive-only BEDs, ~9-fold program-depth asymmetry, and absence from a program is an unread negative
and never a measured zero.

**Stop condition — reached.** The design question is answered from committed artifacts and the
arithmetic reproduces the prior lanes exactly. I stopped at the design boundary: no contrast, no
expression value, no gate.

## 7 · Outcome

**A GPL6244-only pre-registration is available at zero cost in detectable effect and one cost in
evidentiary standard.** The choice the coordinator faces is therefore not "power versus waiting" — it
is "an unreplicated single-series test at a declared level, versus waiting on one missing platform
file whose arm was graded circular and could never have carried a positive anyway." If the drop is
adopted, S2 must be recorded as **dissolved by decision, not satisfied**, and the three replacement
rules adopted with it, so that the guard §3.1 loses is replaced rather than quietly forgotten.
Contrast B stays not-run under S3 either way.
