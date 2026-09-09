---
id: DOC-OPUS-CAMPAIGN-ASSESS-TXN-DEPENDENCY
title: "ASSESS-TXN-DEPENDENCY — independent methods and evidence assessment of the TXN-DEPENDENCY claim ledger and its follow-up"
level: L4
kind: independent-assessment
status: live
date: 2026-09-09
last_verified: 2026-09-09
lane: ASSESS-TXN-DEPENDENCY
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
subjects: [TXN-DEPENDENCY, TXN-DEPENDENCY-2]
head_measured_at: 65328136ec847a2ae4192cc8274cb6d5a12a6de2
---

# ASSESS-TXN-DEPENDENCY — independent assessment

Assessor lane. ⛔ Nothing in TXN-DEPENDENCY, TXN-DEPENDENCY-2 or this assessment bears on EMC
efficacy, safety, selectivity, therapeutic window or clinical readiness; a Chronos gene effect is a
screen statistic in non-EMC cancer lines and an unmeasured EMC dependency is unknown, not zero.

## What I measured against

* HEAD at every measurement: **`65328136ec847a2ae4192cc8274cb6d5a12a6de2`** ("Two lanes: a citation
  type refuted at source…", 2026-09-09 01:31:59Z). Measured at open (`checks/01`) and re-derived at
  each use; TXN-DEPENDENCY-2 measured at `b14a84259`, two commits earlier.
* Manuscript `research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md`,
  **clean**, blob `0c6c57f63b89f41e8ef7722d87035fbfa440cb50`, sha256
  `9523555483f00cfee00b6cd4cf64f5615f57c011f1640297bf952399e742b3ba` — byte-identical to the object
  both subject lanes read. 600 lines.
* Work was done on **copies** in the session scratchpad. No subject-lane file was read-modified,
  no capture overwritten, nothing staged, committed or pushed, no preflight, no producer re-run, no
  network, no subagent. Writes confined to this lane.

---

## 1 · Is the ledger's coverage honest? — **SUPPORTED-WITH-QUALIFICATION**

I did not take "83 rows" on trust. I tokenised every numeric literal the manuscript prints outside
§9 References and §10 Declarations and asked, mechanically, whether each token appears anywhere in
the ledger's 83 rows (`checks/02-coverage-census/`).

**277 numeric tokens; 247 appear in the ledger.** The 30 that do not decompose as:

| kind | count | assessment |
|---|---|---|
| section cross-references (`§1.1`, `§1.2`) | 8 | not claims |
| citation years (2012, 2015 ×2, 2017) | 4 | not quantitative claims |
| PMIDs in §4 | 9 | identity claims, not quantities |
| **printed percentage renderings of the Stream B fractions** | **5** | **a real gap** |

The five are `100 %`, `5.5 %`, `18.7 %`, `97.8 %` in the §3 table and `97.8 %` again in the §5
summary table. The ledger grades the fraction forms (`91/91`, `5/91`, `17/91`, `89/91`) and the
underlying stored values, so the *substance* is covered and each percentage is a one-step rounding of
a graded row — but the printed tokens themselves carry no ledger row, and `18.7 %` and `97.8 %` are
independently re-asserted in §3's prose ("18.7 % dependent … against 11.9 % elsewhere",
"**CDC37's 97.8 % is the measured observation**") and §5's table, where a reader meets them as
claims in their own right.

Section-level coverage is otherwise dense and proportionate: §2 124/127, §1.1 28/29, §1.2 14/15,
§8 17/18, §6 7/7. §4 is the thinnest — 3 of 11 tokens, one ledger row (`L-NRD-1`) — but the eight
uncovered tokens there are all PMIDs, and the two real quantities §4 prints (fifteen dated queries,
Q15's 25 unscreened hits) *are* graded.

**Verdict.** No class of quantitative claim was silently dropped, and the FINDING discloses its own
scope boundary ("Coverage is the manuscript's quantitative claims. Qualitative statements, hedges and
the §4 literature readings were not graded beyond the numbers they carry") — which is exactly what I
measured it doing. The qualification is the five ungraded percentage renderings, one of which
(97.8 %) the manuscript elevates to a named "measured observation".

## 2 · Does the known-answer control actually control? — **SUPPORTED-WITH-QUALIFICATION**

I re-read the DepMap artifact independently (`checks/03`) and reproduce the control's values exactly:
CDK7 `sarcoma_mean −1.847`, `selectivity +0.085`, `rest_frac_dependent 0.999`; CDK9 `−1.464`,
`+0.017`, `0.994`; `n_models_total 2105`, `n_sarcoma_models 176`, and **`n_sarcoma = 91` in all 67
gene records** in the file, not merely the five. The control is real and it passes.

**What it controls:** the READ-BACK path — JSON load, key traversal, transcription — which carries
15 READ-BACK + 14 READ-BACK-from-artifact rows.

**What it does not control, and the FINDING's sentence over-reaches on this:**

* the **14 RECOMPUTED-from-retained-per-sample-`z`** Stream A rows (Welch rebuild),
* the **14 RECOMPUTED conditional-arithmetic** rows (p-values and intervals from rounded Δ/t/df),
* the **`git hash-object` identity path — which is precisely where all three MISMATCHes live.**

The FINDING writes: "The harness is therefore not reporting from a broken instrument, and the three
MISMATCHes above stand as findings rather than as harness artefacts." The control it has just
described touches none of the machinery that produced those three verdicts. The conclusion is
nevertheless **true**, but it is carried by other evidence:

* `checks/04-head-moved-during-run` is the actual control for the hash path — but it preserves only
  **three of ten** objects, while the FINDING states "At this lane's starting HEAD (`1e35538`) all
  ten §8 identities matched (check 04)". That sentence's evidence is not in the check it cites.
* I supplied the missing evidence (`checks/05-all-ten-identities-two-heads/`): parsing the ten ids
  **out of §8 itself** and resolving each at `1e35538da` and at `65328136e` — **all ten match at
  `1e35538da`; exactly the same three drift now.** The claim is correct; its citation was not.

One further methods point: the ledger's harness **hard-codes** the ten declared ids as Python
constants (`rederive_claims.py` lines 467-476) rather than parsing §8, so an identity row compares a
*transcription* to the tree. I checked the transcription against the manuscript table — it is exact
— but the method is transcription-dependent and a transcription slip would surface as a spurious
MISMATCH.

Also noted, without prejudice: the ledger stamps `repo_head: 99672905a…`, a fourth commit that the
FINDING's provenance paragraph does not name (it names `1e35538`, `6466168`, `7a62238`). The
timeline is consistent — `99672905a` at 01:12:24Z, `7a6223875` at 01:13:03Z (`checks/08`) — so this
is an incomplete provenance narration, not a contradiction.

## 3 · Is "it breaks no printed number — it bounds them" established or asserted? — **SUPPORTED-WITH-QUALIFICATION**

This is the load-bearing sentence, so I went looking for a counterexample rather than for
confirmation.

**The structural argument, verified.** Every Stream B quantity the manuscript prints is either read
back from `depmap-sarcoma-dependency.json` or an integer determined by a value read back from it.
The missing per-line Chronos matrix therefore cannot *move* a printed number; it can only fail to
*confirm* the artifact, which the ledger explicitly places outside its scope and §8 discloses.
`checks/03` confirms the retained store's shape: **no `n_rest` key exists in any of the 67 gene
records**, so `B-NRD-2` names the missing input correctly, and the printed rest fractions
(99.9 / 99.4 / 5.2 / 11.9 / 98.7 %) are genuinely bounded — quoted without a recoverable
denominator, exactly as §1.2 and §3 say.

**The sharpest candidate I could construct — and it survives, but not for the stated reason.**
The strongest place for the missing matrix to bite is the unique-integer inference behind
`91/91`, `100 %`, §3's "CDK7 and CDK9 cross the −0.5 threshold in **every** screened
sarcoma-lineage line", and §6 U2's "in all 91 screened lines". Those rest on
`sarcoma_frac_dependent`, which for CDK7 and CDK9 is stored as the literal **`1.0`**. Taken at face
value, `1.0` at one decimal is compatible with **k ∈ {87, 88, 89, 90, 91}** (`checks/03`) — five
integers, not one, and 87/91 would falsify the word "every". Uniqueness is recovered only from the
producer's rounding rule, `round(float((s < DEPENDENT_THRESHOLD).mean()), 3)` at
`research/modalities/depmap_sarcoma_dependency.py:257` (`checks/04-producer-rounding-rule/`; blob
`fc0a0cc0…`, a §8-pinned identity that **MATCHes**), under which the ±0.005 band admits **k = 91
only**. The other three genes are unique from the stored literal alone (`0.055 → 5`, `0.187 → 17`,
`0.978 → 89`).

So the manuscript's own sentence — "The integer counts are the unique integers compatible with the
stored rounded fractions" — and the ledger's `B-CDK7-INT` / `B-CDK9-INT` rows are **correct but
under-stated**: for two of the five genes uniqueness depends on a *third* object (the producer
source), not on the stored fraction, and neither the manuscript nor the ledger says so. That is a
disclosure gap in the chain, not a broken number. I found no printed quantity that the missing
per-line matrix can move.

**Verdict.** "Bounds them, does not break them" is *established* for the Stream B quantities as
printed, with the qualification that the CDK7/CDK9 integer bound is producer-source-dependent and
that nothing here verifies the artifact against DepMap at all — a point the FINDING makes plainly.

## 4 · Is TXN-DEPENDENCY-2's recommendation right? — **SUPPORTED-WITH-QUALIFICATION**

**Premises verified.** The §8 sentence is quoted verbatim and correctly: "Each is the Git blob SHA-1
of the exact object this paper was read against" (`checks/06`). The forecast sentence really does
enumerate two objects by name and is really closed ("Two of the objects above — X and Y"). And the
argument's practical premise holds: **all three superseded blobs still resolve today** —
`git cat-file -t` returns `blob` for `b45a35a4…`, `18625608…` and `8728c34d…` (`checks/06`). So
keeping the read-against ids does cost the reader nothing, and overwriting them would make the
manuscript assert it read an object it did not read. On the letter, the recommendation is right.

**The other side, which the follow-up owes and does not fully pay.**

1. *The producer drift may be entailed rather than uncovered.* §8's own "Fixed versions" paragraph
   states that `census-route-expression-grading.json` is "produced by
   `research/modalities/census_route_expression_grading.py`". An annotation-only correction applied
   to a **generated** JSON that did *not* also move its producer would be reverted the next time the
   producer ran. On that reading the producer's blob moving with its output is a *consequence* of the
   forecast correction being coherently implemented, not an unannounced third change. TXN-DEPENDENCY-2
   is literally right that the enumeration is closed, and it does flag the data-vs-code asymmetry
   honestly ("for a producer, the same assurance requires either reading the code or re-running it")
   — but "genuinely uncovered by §8's forecast" reads as more surprising than the pairing warrants.
   ⚠ I did not re-run the producer either, so I cannot upgrade this past a reading of §8's text.
2. *A reading under which updating is correct.* If the table's function were "the objects a reader
   should fetch to reproduce this today", overwriting would be the honest act and variant A right.
   §8 forecloses that reading in the sentence that introduces the table — but the reading is
   available in principle, and it is the one a reader arriving from the "Artifact map" (which links
   **paths**, not ids) would naturally hold. Variant B's dated note is what keeps those two halves of
   §8 from disagreeing.
3. *Variant B's guarantee is conditional.* "Git retains the old blobs" holds only while the
   superseding commits stay reachable. A squashed history, a shallow clone or a non-Git export of
   this manuscript would leave a superseded id unresolvable. Variant B naming the superseding commit
   is therefore load-bearing, not decorative.

**Verdict.** The recommendation (prefer supersession, owner's act, neither diff applied) is right,
and its central argument — an identity that tracks the tree stops being a check — is correct.
Qualified on point 1: the producer-script drift is *unenumerated*, which is weaker than *unforecast*.
⛔ I did not apply, re-check or modify either diff.

## 5 · What would falsify the ledger? — a concrete runnable test, and I ran it

**The test.** Single-leaf mutation sensitivity. Copy the harness and the four input artifacts into a
sandbox, re-point `ROOT`/`LANE`, run once to fix a baseline, perturb **one** stored leaf, re-run, and
diff the verdict lines. A ledger whose REPRODUCES verdicts are real must flip **exactly** the rows
keyed to that leaf and no others; a ledger that echoes its own quoted values, or whose comparisons
are loose, will flip nothing or will flip broadly.

**Result** (`checks/07-mutation-falsification/`). Mutating `HSP90AB1.sarcoma_frac_dependent`
`0.187 → 0.198` — chosen because it moves the unique compatible integer 17 → 18 — flips exactly
three rows and nothing else:

```
< REPRODUCES B-HSP90AB1        -> > MISMATCH B-HSP90AB1
< REPRODUCES B-HSP90AB1-INT    -> > MISMATCH B-HSP90AB1-INT
< REPRODUCES ID-depmap-sarcoma-dependency.json -> > MISMATCH ID-...
```

The third is correct behaviour, not noise: mutating the file changes its blob identity, and the
harness's identity row caught it. **79 of 82 verdicts held.** This is a positive control the subject
lane did not run — the known-answer control tests only agreement, this tests disagreement — and the
harness passes it.

⚠ The sandbox baseline itself reports 71/5/7 rather than 75/5/3, because I copied only the four JSON
artifacts the harness reads and not the five producer/definition files it hashes; those four extra
MISMATCHes are absent-file artefacts of the sandbox and are preserved as they occurred, not
suppressed.

**The falsifying tests I did *not* run, for the owner:** (a) extend the mutation sweep to every leaf
the 83 rows cite and require a bijection between leaves and flipped rows; (b) re-derive the §8 ids by
**parsing the manuscript** instead of the hard-coded constants, which would close the transcription
dependency named in §2 above.

---

## Verdict summary

| # | question | verdict |
|---|---|---|
| 1 | ledger coverage honest | **SUPPORTED-WITH-QUALIFICATION** — 247/277 non-reference numeric tokens graded; the 5 real gaps are the printed percentage renderings 100 / 5.5 / 18.7 / 97.8 % (×2) |
| 2 | known-answer control actually controls | **SUPPORTED-WITH-QUALIFICATION** — it controls the read-back path only, not the recompute or hash paths where the three MISMATCHes live; the FINDING's "all ten matched (check 04)" is true but check 04 shows three, so I re-derived all ten |
| 3 | "breaks no printed number, it bounds them" | **SUPPORTED-WITH-QUALIFICATION** — no printed number the missing matrix can move; but CDK7/CDK9's `91/91` is unique only under the producer's 3-dp rounding rule, since the stored literal `1.0` admits k ∈ {87…91} at face value |
| 4 | TXN-DEPENDENCY-2's recommendation | **SUPPORTED-WITH-QUALIFICATION** — supersession is right and the superseded blobs still resolve; but the producer drift is *unenumerated* rather than *unforecast*, since §8 itself names that script as the producer of the corrected JSON |
| 5 | what would falsify the ledger | **SUPPORTED** — single-leaf mutation test defined and executed; exactly 3 keyed rows flip, 79/82 hold |

**Nothing I checked contradicts a printed number in the manuscript, and none of the three MISMATCHes
is a number.** I found no fabricated value, no manufactured agreement, and no suppressed failure in
either subject lane; both preserve their failing executions (TXN-DEPENDENCY `checks/01` exit 1
`TypeError`; TXN-DEPENDENCY-2 `checks/01` exit 1 at here-doc EOF) with the real exit codes.

## Limitations

* ⛔ This is an assessment of **two lanes' methods and evidence**, not a review of the manuscript, not
  a re-derivation of its claims from raw inputs, and not a check of the artifacts against DepMap or
  GEO — impossible here and correctly declared NOT-RE-DERIVABLE-LOCALLY by the subject lane.
  ⛔ No DepMap `CRISPRGeneEffect.csv` fetch was attempted; that is the parents' open gap.
* ⛔ No producer was re-run, so leaf-invariance of `census_route_expression_grading.py`'s output was
  not reproduced here either; my point 4.1 is a reading of §8's text.
* My coverage census is token-level and mechanical. A number the manuscript states in words
  ("fifteen", "Sixteen", "four different claims") is not counted as a token; I read those sections
  and found their quantities graded, but the census cannot prove that exhaustively.
* The mutation test exercised **one** leaf. A full leaf-to-row bijection was not attempted.
* HEAD can move again. Every identity in this document was re-derived at `65328136e`; re-hash before
  relying on any of them.

## Stop condition — met

Five questions answered with verdicts, one falsification test defined and executed, all attempts
preserved under `checks/` with real exit codes. No repair proposed, no diff prepared or applied, no
subject-lane file modified, no capture overwritten. Choosing and applying a §8 disposition remains
the manuscript owner's act.
