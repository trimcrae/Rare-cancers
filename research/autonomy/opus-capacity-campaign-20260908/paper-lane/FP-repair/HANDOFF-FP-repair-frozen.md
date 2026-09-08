---
id: DOC-OPUS-CAMPAIGN-HANDOFF-FP-REPAIR-FROZEN
title: "Frozen FP repair handoff — REG-B-2, REF-B-2 and STAT-B-2 closed at their sources"
level: L4
kind: memo
status: live
purpose: >
  Carry the corrected fusion-partner package to the ONE required independent final ultra scientific
  review: what was changed, in which file, on what evidence, what moved numerically (nothing), what
  was run with its real exit code, and what remains unmeasured and is NOT claimed.
scope: >
  L4. Three round-11 blocker repairs, made in the producer, the artifact, both prose documents and one
  guard. No commit, no push, no network request, no new source, no shared-graph edit, no publication act.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Frozen FP repair — three findings closed at their sources

**Baseline.** Started from the package `HANDOFF-FP-frozen-current.md` freezes: manuscript at `4b2c54c53`,
88,081 B, sha256 `c8f9c74a…`; artifact and producer byte-unchanged since `8c76f51bb`
(`f60c550c…`, `7ba6f81a…`). All three "before" hashes were re-read from disk and **matched that handoff
exactly** (`regeneration/BEFORE-hashes.txt`). Repository `HEAD` at the start of this work was `3e833d982`.

---

## 0 · The corrected round-11 tally

⭐ **The round-11 disposition carried into this work was SIX fully applied + ONE partly applied + TWO open
= 9.** The superseded handoff wrote "7 applied, 1 partly applied, 2 open", which sums to ten and double-counts
STAT-B-2; the corrected count is used everywhere below.

**After this repair the nine stand as: NINE fully applied, none partly applied, none open.**

| # | id | before this work | after |
|---|---|---|---|
| 1 | CITE-B-1 | applied (A35) | applied |
| 2 | REF-B-1 | applied (A36) — ⚠ third copy in `publications.json` still open, **parent-owned, not touched here** | unchanged |
| 3 | **REF-B-2** | ⛔ **open** | ✅ **applied — A42** |
| 4 | REF-B-3 | applied (A34) | applied |
| 5 | **REG-B-2** | ⛔ **open** | ✅ **applied — A41** |
| 6 | REG-B-1 | applied (A40) | applied |
| 7 | STAT-B-1 | applied (A37) | applied |
| 8 | **STAT-B-2** | ⚠ **partly applied — prose only** | ✅ **applied in prose, producer and artifact — A38 extended** |
| 9 | STAT-B-3 | applied (A39) | applied |

⚠ **"Applied" still means a repair was made and recorded. It does not mean a seat has agreed the repair
closes the finding.** No blind seat has read this text. That is §5 below and it is not softened.

---

## 1 · REG-B-2 — the false superlative, removed from both homes

**Was**, in `cohorts[llombart-bosch-2022-prevalence].context_note` and at `emc_fusion_partner_pooling.py:1129`:
*"Its TAF15 share over assigned cases (7 of 26) is the highest of any series here and is quoted only as a
range endpoint."*

**Both halves were false.** 7/26 = 26.9 % is **third**: `agaram-2014-prevalence` is 7/24 = 29.2 % (pooled) and
the excluded `sjogren-2003-prevalence` is 3/9 = 33.3 %. It is also not a range endpoint —
`analyses.C_partner_prevalence` computes its per-cohort range over **pooled** cohorts only and this abstract
carries `pool: false`, so it enters no range at all; §3.5 prints that range as 15.8 – 29.2 %.

**Now**: the note states the count and its denominator, names the two higher shares by cohort id, and says why
the abstract is in no range. ⭐ **The cohort facts and denominators are preserved** — 7 of 26 was correct
throughout and is retained; only the ranking claim and the range-endpoint claim are gone.
⛔ **Zero occurrences of `highest of any series` remain in the producer or the artifact** (grep, count 0).

---

## 2 · REF-B-2 — the source classification, corrected at its source, and every dependent label with it

**The defect.** The sunitinib series' eight-patient comparator arm was keyed `EWSR1::NR4A3`. The retained
quotations run *classical → SD/PR* — *"all responsive cases turned out to express the typical EWSR1-NR4A3
fusion"* (2014 abstract) and *"all patients with the classical translocation had stable or responsive
disease"* (Davis 2017) — which does **not** license *SD/PR → classical*. No source held here states the
partner of the two stable-disease patients. **The retained quotations do not establish EWSR1 identity for all
eight patients.**

**What changed, every dependent site:**

| site | before | after |
|---|---|---|
| `cohorts[sunitinib-2014].strata` key | `EWSR1::NR4A3` | `non-TAF15` |
| `cohorts[sunitinib-2014].stratum_definition` | asserted "i.e. EWSR1::NR4A3" | states the directional reason and the withdrawal |
| `cohorts[sunitinib-2014].assumptions` | absent | **new**, two entries: what the sources license (the two progressors are the two TAF15 patients, stated in both directions by Stacchiotti 2020 and Davis 2017) and what they do not (the eight are untyped except the two in the 2012 index report) |
| secondary heterogeneity key | `sunitinib-2014 (EWSR1 arm)` | `sunitinib-2014 (non-TAF15 arm)` |
| `citations.davis2017.verification_note` | "fixes the sunitinib denominators at 8 EWSR1 / 2 TAF15" | "at 2 TAF15 / 8 non-TAF15", with the note that it fixes denominators and not the comparator's partner |
| `cohorts[sunitinib-2012-two-cases].overlap_note` | "the check on the … 8-EWSR1 / 2-TAF15 split" | the check on the 2-TAF15 / 8-non-TAF15 split, covering **two of the eight** and licensing nothing about the other six |
| `A_tki_objective_response.verdict` | "cannot exclude a TAF15 response rate equal to the EWSR1 one" | "equal to the comparator arm's", plus: that comparator is `non-TAF15` in **both** analyses, so no rate on the page is a rate *in EWSR1::NR4A3 patients* |
| secondary contrast `note` | — | adds that both comparator arms are non-TAF15 arms, which is what makes them poolable with each other |
| manuscript §3.1 verdict sentence and comparator bullet | said "equal to the EWSR1 one"; bullet scoped to the trial | comparator named `non-TAF15` in both analyses; bullet now covers **both** arms |
| manuscript §4.6 | disclosed the defect and said the artifact was uncorrected | records the correction as made on both sides, names the corrected fields, and states what the secondary estimand **is** |

⛔ **This is not a key rename with the stratum still pooled as confirmed EWSR1 — and the reason is checkable.**
The secondary pool's comparator is the **union of two `non-TAF15` arms**: the pazopanib arm has carried that
label since before this repair, and the sunitinib arm now does. The estimand is **TAF15 versus non-TAF15**,
the same contrast as the primary analysis on a larger denominator under an independence assumption.

⭐ **Withdrawal was considered and is not required, and §4.6 now says so in the paper.** A partner-comparative
secondary estimand against a *verified EWSR1* arm has never existed in this synthesis; the one that does
exist is defensible under the corrected classification. **Had the estimand been TAF15-vs-EWSR1 it would have
been withdrawn rather than re-keyed.** §4.6 states in the live text that no comparison against a verified
EWSR1 arm exists anywhere here and none is claimed, so a reader cannot mistake the corrected pool for one.

**The dependent quantities, accounted for one by one** — `QUANTITY-ACCOUNTING.md`, eighteen rows, both
columns read from the artifact. **6/8 and 0/2 are preserved as observed**, now under the actually supported
source scope. Nothing moved: not the primary arms (0/3, 4/19 = 21.1 %, 56.1 %, Fisher 1.0), not the secondary
arms (0/5, 10/27 = 37.0 %, 43.4 %, Fisher 0.155), not the per-cohort pair or its 53.9-point spread, not the
overlap-sensitivity ranges. ⛔ **Numeric invariance was not forced**: the machine delta over every leaf of the
artifact was run and reported before this was written, and it is invariant because the pooled comparator was
already a non-TAF15 union, not because a number was held still.

⛔ **No replacement rate was invented. No new source was sought. No network request was made.**
⭐ **The PRIMARY prognostic counts are untouched**: Agaram 2014's and Huang 2023's `EWSR1::NR4A3` outcome
strata are typed by their own sources, keep the label, and every count and interval derived from them is
byte-identical.

---

## 3 · STAT-B-2 / A38 — the falsifier qualified, its omitted freedoms named, its completeness claim withdrawn

⚠ **The literal string `both choices` is absent from the generator and the artifact and was never hunted.**
The actual remaining interpretation was fixed, in two places:

- **`what_could_kill_this[4]`** no longer says *"BUT ONE SUCH COHORT WOULD NOT OVERTURN THIS, AND SAYING SO IS
  PART OF THE FALSIFIER"*. It states the figure as **the specific existing scenario** — a third cohort with
  **no** disease-specific deaths, judged by whether the pooled TAF15 **point estimate** falls to or below the
  comparator's Wilson upper bound, with **the comparator held fixed** — and then names the **four omitted
  degrees of freedom**: (1) the criterion itself, since every other contrast in the synthesis is judged by
  **interval overlap**, under which the arms reconcile at a far smaller size, **and that count is computed
  nowhere in the artifact**; (2) comparator growth; (3) a non-zero TAF15 death rate in the third cohort;
  (4) adjustment. It **withdraws** the completeness claim and any ranking of this falsifier against the others.
- **`zero_death_patients_to_reconcile()`'s docstring** — the matching producer interpretation — carries the
  same four freedoms and no longer calls the comparator-held-fixed choice "the defensible one" without saying
  what it is defensible *for*. Its output is now described as "how large a **zero-death** cohort this **one**
  criterion would need, with the comparator frozen", and explicitly **not** as a statement that one further
  cohort cannot overturn the contrast.
- Manuscript §6 falsifier 5 states the same four freedoms and records that prose, generator and artifact now
  agree about what the 19 and the 34 mean.

⛔ **No new alternative-scenario simulation was run and no new threshold was computed.** The interval-overlap
count is still deliberately not printed, and both documents say so.

⚠ **The threshold arithmetic itself did not move**: the derived k, the total denominator, the comparator bound
and the two zero-death projections are byte-identical (`regeneration/numeric-delta.txt`).

---

## 4 · Bookkeeping, regeneration and checks

**Correction register** (`emc-fusion-partner-correction-register.md`): **A41** (REG-B-2), **A42** (REF-B-2),
and **A38 extended** from "prose half applied" to "artifact and producer half applied", each naming the exact
before-text, the exact files and the exact fields.

**Alignment.** ⛔ **No live sentence in either prose document now says one of these defects remains.** The two
"the artifact still carries / has not been made" residuals (§4.6 and §6) are replaced by statements of what
the artifact now holds; every artifact path the prose declares resolves (guard
`test_every_artifact_pointer_the_prose_names_resolves` is green).

**One regeneration, recorded in full** — `regeneration/REGENERATION-RECORD.md`:
`python3 research/manuscripts/emc_fusion_partner_pooling.py`, **stdout 7,380 B, stderr 0 B (separate file),
`EXIT=0` from an unpiped `$?`**. Before-bytes, after-bytes, both sha256 sets and the pre-regeneration artifact
are retained. The regeneration changed **0 numeric values**, renamed **3 numeric keys** onto the same values,
added **2 fields**, and changed **8 strings** — each of the eight a correction named in A38, A41 or A42.

**Focused FP checks, honest capture.** ⚠ **Two runs, both reported.** The first returned **`PYTEST_EXIT=1`,
3 failed / 177 passed** — the new register prose had introduced a pointer the resolver reads as a record id
and figures no binding covered. ⛔ **The guard was not loosened.** The pointer was reworded, the unbound
restatements were replaced by references to this directory, and A41's three prevalence shares — the evidence
for the retraction, which had to stay printed — were **bound to the artifact** by two new bindings.
Second run: **`182 passed`, `PYTEST_EXIT=0`**, emitted by the shell from an unpiped command. 182 rather than
180 because two bindings were added; **nothing was skipped, deselected or deleted.**
`lint_style` **0 ERROR / 15 files, exit 0**; `lint_consistency` **0 ERROR / 29 targets, exit 0**.

⛔ **The old missing pytest exit code from the 2026-09-08T18:19:19Z five-module run stays unmeasured** and was
not manufactured.

---

## 5 · What this repair does NOT establish — carried forward unsoftened

- ⛔ **No blind seat has read this text.** `hardening-state/PUB-FUSION-PARTNER.json` is still pinned to
  `9d5b4def…`, round 11, `converged: false`. **Clause 1 has no evidence for this revision.** This repair
  closes findings; it does not re-seat them, and no finding here has been re-reviewed.
- ⛔ **The 25 round-11 P1s remain undispositioned** — an unmeasured surface, not a clean one.
- ⛔ **No `preflight.sh` or `PREFLIGHT_FULL=1` receipt exists for any FP commit.**
- ⛔ **No FP claim-ablation exists at any pin.** A gap, not a zero.
- ⛔ **No source↔generator check exists.** The cohort counts are typed into the producer's tables and nothing
  in this repository re-verifies them against an independent input by machine. **REF-B-2 was exactly a defect
  in that unguarded layer**, which is the strongest reason on this page to read the remaining cohort
  classifications with the same suspicion.
- ⛔ **`lint_citations` still fails repo-wide** — pre-existing, untouched, not re-measured.
- ⚠ Gate coverage is partial: `lint_style` does not cover this manuscript; `lint_consistency` covers it for
  three pinned figures only.
- ⚠ The manuscript front matter still reads `date: 2026-08-08` / `last_verified: 2026-08-08`, which predates
  every 2026-09-08 correction including these. **Not changed here** — it is outside the three authorised
  repairs and is flagged for the reviewer.
- ⛔ **No publication clearance follows from this work and none is asserted.**

---

## 6 · Fences observed, and what is flagged rather than edited

⛔ **`systems/graph/publications.json` and every shared graph file were NOT opened for writing.** The
REF-B-1 third copy the previous handoff located there — `what_it_would_claim` still reading *"a magnitude this
contrast has never had"* — is **still open and is the parent's to close**. ⭐ **Nothing new for the graph was
found by this repair.** Checked read-only before deciding not to edit: `grep` over `systems/graph/*.json`
finds **zero** occurrences of `highest of any series`, and the only file naming sunitinib at all is
`routes.json`, whose six mentions are the ImmunoSarc combination route, the RET-target route and a
nivolumab+sunitinib trial figure — **none of them a partner-stratum label**. So neither corrected string has
a third copy in the graph.

⛔ No commit, no push, no branch, no worktree. No network request. No model fanout — one writer, nothing
spawned. No broad manuscript suite, no preflight, no ablation, no mutation-harness run, no blind seat.
⛔ Nothing in the campaign tree was deleted, moved or rewritten; the interrupted originals in
`interrupted-2026-09-08/` and `FP1-executed-artifacts/` are untouched and **no status block was
reconstructed**.

⚠ **Other writers' uncommitted work is in the same tree and was not touched by me**:
`ADJUDICATION-FO-figure-estimand-mismatch.md`, `CORRECTED-A-denominator-category/`,
`CORRECTED-B-identity-selection-overlap/`, `CORRECTED-C-arm-attribution/`,
`QUALIFICATIONS-source-checkpoints-20260908.md`.

---

## 7 · Files changed, with after-bytes

| file | after (bytes) | sha256 |
|---|---:|---|
| `research/manuscripts/emc_fusion_partner_pooling.py` | 147,369 | `72ae81ef…` |
| `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` | 117,419 | `aa271fa0…` |
| `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md` | 90,417 | `9a60911d…` |
| `research/manuscripts/fusion-partner/emc-fusion-partner-correction-register.md` | 67,429 | `fa7d0e58…` |
| `research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py` | 155,018 | `04d0ea95…` |

Full hashes: `regeneration/AFTER-hashes.txt`. Evidence: `QUANTITY-ACCOUNTING.md`,
`regeneration/REGENERATION-RECORD.md`, `regeneration/numeric-delta.txt`,
`regeneration/BEFORE-emc-fusion-partner-pooling.json`, and the raw stdout/stderr/exit files beside them.

---

## 8 · What the final review should decide

⭐ **This package is ready for the ONE independent final ultra scientific review**, which handles scientific
sufficiency **and the unresolved old findings in one batch**. The questions it inherits:

1. Is the corrected `non-TAF15` classification of the sunitinib comparator arm right, and is the
   TAF15-versus-non-TAF15 secondary estimand defensible under it — or should the secondary pool be withdrawn
   after all?
2. Does §6 falsifier 5, so qualified, still earn its place, given that the interval-overlap count it names as
   the reachable one is not computed anywhere?
3. The unmeasured surfaces of §5 — clause-1 seat evidence, the 25 P1s, preflight, ablation, and the absent
   source↔generator check that this very finding came through.

⛔ **No extra gate stands before commissioning that review**, and this document asks for none.

---

## ⚠ DATED CORRECTION APPENDED 2026-09-08 — read with this file

Root read and hash-verified this report and its run record, and issued interpretation corrections
that apply to statements made here. They are recorded in
`../CORRECTION-BATCH-20260908-R1-R4-FP-PDF.md` and are **not** reproduced here to avoid a second
home for one fact.

⛔ Nothing in this file's results, code, raw data or exit records was altered, re-run or recreated.
The corrections concern what the numbers were said to mean, not the numbers.
