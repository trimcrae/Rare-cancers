---
id: DOC-OPUS-CAMPAIGN-FROZEN-MORTALITY
title: "Frozen review handoff — mortality mechanisms and the survival available to therapy"
level: L4
kind: memo
status: live
purpose: >
  Hand the mortality evidence-tier manuscript to root's scientific disposition with its exact
  revision, its producer chain, its declarations, the checks that have and have not run, and every
  boundary judgment the tiering rests on.
scope: >
  L4. A handoff. It authorises no publication act, asserts no green gate, adjudicates nothing, and
  creates no reviewer record.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Frozen handoff — `emc-mortality-mechanisms-paper.md`

## Exact revision and content identity

- **Git revision:** `31587f15`, branch `claude/confident-bardeen-ji76cd`. The package reached this
  state in three commits: `93232c6e` (MD1 round 2, the evidence tiers), `7548bdec` (root's semantic
  correction: a named disease entity is not a named terminal event), `31587f15` (declarations and the
  named producer chain).
- **Manuscript:** `research/manuscripts/emc-mortality-mechanisms-paper.md`, **36,906 bytes**, sha256
  `9d8caa38f921feeaa3457bcc6b493868594fbbeff10c8abeb7a78fb1e935849a`, 4,774 words.
- **Record:** `systems/graph/publications.json` and the manuscript frontmatter make it `kind:
  manuscript`, `level: L3`, canonical for the labelled-instance proportion and its evidence tier, the
  stratified upper bound, the relative-survival convergence, and the absence of any published
  pulmonary growth-rate measurement.

## The producer chain, hashed

Three producers write everything the paper quotes. ⛔ None was re-run to obtain a receipt; the tally
producer was re-run **once**, because the semantic fix below changed what it must emit, and a second
run is byte-identical to the first.

| producer | input | output |
|---|---|---|
| `emc_terminal_events.py` (24,425 B, `b5900f076288e8a6…`) | `emc-terminal-events-classified.json` (21,732 B, `94c48d42b65ed031…`), `research/literature/emc-mortality-probe.json` (597,912 B, `386cd0c9376229d9…`) | `emc-terminal-events.json` (22,853 B, `eda227ecd9259edb…`) |
| `emc_mortality_decomposition.py` (26,246 B, `8ff4850db092690e…`) | `emc-mortality-decomposition-inputs.json` (9,810 B, `f0739ae091959aa5…`) | `emc-mortality-decomposition.json` (11,829 B, `fe47c13b575c0dc0…`) |
| `emc_relative_survival.py` (14,913 B, `15df03964c068b72…`) | `emc-mortality-decomposition-inputs.json` (as above) | `emc-relative-survival.json` (9,406 B, `5eddacdc662980b7…`) |

The classification is **hand-assigned and lives in the input specification, not in the code**. The
tally producer refuses to run at all on three conditions: a quote that is not verbatim against the
retrieval artifact, a row silent on whether its sentence documents a death, and — new here — a
first-tier row silent on whether its sentence names a terminal event or a disease entity. ⭐ The third
refusal was **proved to fire**, by deleting a `stated_type` and a `split_stated_types` entry in a
scratch copy and reading the two error strings back.

## Declarations, as they now stand

**Funding:** none. **Competing interests:** none. **Ethics:** none sought, none obtained, and no
institution or committee has determined whether any is required — ⛔ no determination is invented. The
analysis reads published counts and survival percentages plus a public national life table, with no
new recruitment, no new sampling, no clinical intervention, no patient contact and **no patient-level
record**. **AI assistance:** Claude (Anthropic) and OpenAI models under the author's direction, author
responsible, **not peer reviewed by a human reviewer**.

## The legacy 14/50 wording and the assigned tiers are coherent — recomputed here

⭐ **Re-derived by the parent from the artifact rows, not taken from the worker.** Of 18 rows summing
to **52 summed reported patient instances**, two document no death, leaving **50 documented-death
instances across 14 papers**:

- **Stored labels** (Table 1): 27 mechanism unstated + 8 progressive disease unspecified + 3
  respiratory failure + 3 competing non-cancer + 3 second malignancy + 2 locoregional + 2
  treatment-related + 1 visceral metastasis complication + 1 ambiguous = **50**.
- **The legacy "14"** is 50 − 27 unstated − 8 progressive-unspecified − 1 ambiguous = **14**, and it
  reconciles with the tiers: the 18 broad-tier instances carry 10 mechanism labels (18 − 8
  progressive-unspecified), the 4 first-tier instances carry 4, and 10 + 4 = **14**. Both accountings
  close on the same rows.
- ⚠ Table 1's stored-label column differs from the raw row labels only because the one split row's
  three patients are distributed to competing non-cancer, visceral metastasis complication and
  ambiguous. That is the split, not a re-labelling.

## ⛔ The 4/18/27/1 classification is the worker's interpretation, not accepted evidence

It sums to 50, and **summing correctly is not validation**. Each row's tier is a reading of one
retained sentence, assigned by a worker and re-derived — not re-judged — by the parent. **Root owns
the scientific disposition of the tiering itself.**

**One semantic defect was already found this way and is corrected at `7548bdec`.** Root read the diff
and saw that the first tier's four instances include PMID 32963861, whose quote is "died from
complications of **unresectable colon cancer**" — a **disease entity**, with the complications not
themselves named. The Methods defined the tier broadly (event *or* entity) and then §4.2 and the
Conclusion shortened it to "four of the fifty name a terminal event", which is false for that
instance. The correction distinguishes rather than promotes: every row in the tier now declares
`stated_type`, the artifact reports **3 named_terminal_event / 1 named_disease_entity**, the tier key
is marked legacy and broader than it reads, and no four-mechanism headline exists anywhere in the
paper. ⛔ No quantity moved and no source claim was added: 52/50/14, the tiers 4/18/27/1 and every
stored label are unchanged.

## Unresolved boundary judgments and overlap — the list, not a resolution

1. **The split row (PMID 35775709, n = 3).** One compound sentence, three patients, three different
   tiers. Which patient belongs to which tier is a reading of that sentence.
2. **'Died from non-EMC-related factors' (PMID 35665108, n = 2).** Tiered `assigned_broad_cause_category`
   because the tier definition counts an exclusion as a cause class, while the paper's own prose says
   it "names no cause and does not establish a non-cancer death either". Both statements are in the
   package; whether an exclusion is a cause class is unresolved.
3. **A disease entity inside the first tier at all.** The correction above distinguishes it; it does
   not remove it. Whether the tier should be split into two tiers is root's call.
4. **PMID 41799218**, counted as respiratory failure because that is what the paper names, though the
   initiating event was tumour-embolic ischaemic stroke.
5. **Three rows whose stored label outruns their quote**, retained as legacy filing rather than
   re-assigned (29977924, 35775709's hepatic-metastasis patient, 35665108's two).
6. **Independence is UNKNOWN.** Reviews in this corpus collect earlier cases, so the same patient may
   appear in more than one report. Nothing establishes that the summed instances are unique across
   reports.
7. **Registry overlap.** `aggregate_cause_splits` records the Masunaga strata and **excludes them from
   every pooled total**, because they overlap the localised stratum already used in
   `emc-mortality-decomposition-inputs.json` and pooling would double-count patients.
8. **Inclusion is title-based**: 34 of the 162 papers carrying a death sentence have the disease in
   their title, and every count is restricted to those 34.

⛔ Both record-scope exclusions stand as written and neither asserts survival: PMID 23213584 (a
small-bowel metastasis complication and its palliative management — which also carried a stored
mechanism label, so excluding it moves numerator and denominator together) and PMID 21941486 (a
transition to supportive care). ⛔ The unit throughout is **summed reported patient instances**, not
distinct records and **not unique people**; no rate, incidence or denominator can be formed from them.

## Checks that actually ran, with their exit codes

| check | result | exit |
|---|---|---|
| `lint_style.py` (repo gate, its own TARGETS) | 0 ERROR | 0 |
| `lint_style.py <target>` (explicit path) | clean · 4,774 words, bold 3.6/1000, em-dash 0.2/1000 | 0 |
| `lint_consistency.py` (repo-wide) | 0 ERROR across 29 target files | 0 |
| `lint_claims.py <target>` | 0 ERROR, 1 WARN | 0 |
| `emc_terminal_events.py` | wrote its output; second run byte-identical | 0 |
| `test_emc_supportive_effect_transfer.py` | 11 passed | 0 |

The single `lint_claims` WARN is on "confirmed from the indicator's published name" in Appendix A.2
and **pre-exists at `HEAD`** — measured on the pre-edit file, not assumed.

## Checks that did NOT run, or do not cover this paper — stated rather than implied

- ⛔ **No full `scripts/preflight.sh`, and no `PREFLIGHT_FULL` receipt exists for this revision.**
- ⚠ **This paper is in NEITHER gate's target list.** It is not in `lint_style.TARGETS` and not in
  `lint_consistency`'s 29 targets, and **no pinned figure binds it**. The clean results above are
  explicit-path measurements, not gate coverage. Adding it is an owner decision and is not made here.
- ⚠ **No test binds this manuscript's prose to its artifacts.** The only test in the package is
  `test_emc_supportive_effect_transfer.py`, which exercises a downstream consumer.
- ⚠ `lint_citations.py` exits 1 repo-wide. Four PMIDs cited by this paper — **20818875, 32953543,
  37781179, 38558247** — are **NOT SWEPT (advisory)**: they have no row in the retraction sweep, so
  their retraction status is **UNKNOWN, which is not the same as clean**. No error names this file.
- ⛔ `systems_check.py --check`: 2,394 ERROR / 271 WARN, pre-existing and not cleared.
- ⛔ **No producer was re-run to obtain a receipt**, no new source was retrieved, and no numerator was
  guessed.

## Packaging — eventual, with the line range measured, not assumed

⚠ Lines **37–51** are an HTML comment headed `EDITORIAL, NOT FOR SUBMISSION` (authorship and ORCID
note, venue plan, and a status note on what is *not* in this paper). **Measured on this revision, not
carried over from another paper.** It must be stripped at deposit and it has **not** been stripped
here. ⛔ The endpoint package's handoff once recorded a line range that was four lines too wide and
would have deleted real declarations; that is why this one was counted rather than estimated. The
declarations here sit at the **end** of the file, not adjacent to the editorial block.

## ⭐ CORRECTED 2026-09-08 — the 388-corpus item was already closed

⚠ **This handoff first recorded, as an open item, that the sister memo
`research/manuscripts/emc-mortality-mechanisms.md` §3 twice describes "the same 388-paper retrieved
corpus" with no artifact basis. That status was STALE when written.** Root read the sister memo at
`e21841ea` and no 388 remains; I then checked the live file myself and found **zero** occurrences of
388 in it.

The correction landed earlier, at **`044d3e3c`**, and is specific rather than blanket: the passage now
says a title-level scan of **the 25 records that query itself returned**
(`early_palliative_care_survival.retrieved = 25` in `research/literature/emc-mortality-probe.json`),
expressly **not** a search of the **328**-paper retrieved EMC corpus and not a dedicated sarcoma
palliative-care search. Both numbers are the probe artifact's own.

⛔ Nothing here reopens a number, a source or a producer. Only this handoff's status line was wrong,
and only it is corrected. The escalation record
[`ESCALATIONS-mortality-biomarker.md`](ESCALATIONS-mortality-biomarker.md) is retained as history of
how the item was found, not as a live defect.

## What this handoff is not

⛔ It is not publication permission, not a reviewer record, and not a claim that any gate is green. It
asserts no EMC efficacy, safety, selectivity or clinical readiness, and it makes no claim that any
treatment works. Its central result is about the published record: that record mostly does not say how
its patients died.
