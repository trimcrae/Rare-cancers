---
id: DOC-FP2-POOLED-DEPENDENCY-PROPAGATION-2026-09-09
title: "Where the withdrawn 73-patient pooled disease-specific-death analysis still propagates"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
lane: FUSION-PARTNER-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# What else still rests on the withdrawn pool?

## Question

The pooled Agaram 2014 + Huang 2023 disease-specific-death quantity over 73 patients
(7/15 = 46.7 % vs 6/58 = 10.3 %, Fisher 0.0034) was withdrawn at
`emc-fusion-partner-stratification.md` §3.3 line 402, and the object no longer exists in the
artifact. **A withdrawal at one section does not propagate itself.** Which other sentences, table
cells, statements and artifact fields still depend on that pool — for its magnitude, its
significance, its sample size, or an inference drawn from it — and which of those the live
Agaram-only quantity (3/7 = 42.9 % vs 1/16 = 6.2 %, descriptive Fisher p 0.0672, 23 patients)
does not carry?

## Merit

Patient relevance is indirect but real: this is the repository's canonical statement of what the
published record supports about the *NR4A3* 5′ partner as a stratification variable, and a stale
`46.7 % vs 10.3 %, p = 0.0034` in a route record or a published view is a stronger prognostic
signal than the evidence carries. The contribution is non-trivial because a partial withdrawal is
the failure mode that looks finished: the withdrawing section is always the one that gets checked.
The evidence is fully attainable — every dependent site is on disk.

## Evidence gap this addresses

The three-pin guard maintenance (`FP-three-pin-2026-09-09`) closed the *artifact-to-prose* binding
for the three numbers. It deliberately scoped itself to guard entries and made no claim about
**downstream inference** or about records outside `pinned-figures.json`. The gap is the
dependency closure: every place the pooled object's magnitude, sample size or significance was
reused as support, whether or not the number itself is printed.

## Step taken

1. **Re-derived the live artifact values from the stored integers before relying on them**
   (`checks/01-rederive-artifact`, exit 0). From `{events: 3, denom: 7}` and `{events: 1, denom: 16}`:
   percentages 42.9 / 6.2, Wilson 95 % bounds 15.8–75.0 and 1.1–28.3, difference −36.6 points,
   Fisher exact two-sided **0.0672** — all matching the stored values exactly. The pooled object is
   confirmed **absent**: `analyses.B_outcome_by_partner.disease_specific_death` does not exist, and
   `pooled_cohorts` is `["agaram-2014-outcome"]` with `cohorts_pooled: 1`.
2. **Enumerated every dependent site** across the manuscript, the artifact, the correction register,
   the dated lane memo, and the canonical graph and its generated views, and classified each (a)/(b)/(c).
3. **Prepared an UNAPPLIED unified diff** for the (b) and (c) sites, preserving each superseded
   sentence verbatim inside a dated 2026-09-09 `Superseded, retained` marker rather than erasing it.

## Result

**The manuscript and its artifact are clean.** Every one of the 20 dependent sites inside
`emc-fusion-partner-stratification.md` and `emc-fusion-partner-pooling.json` is **category (a)** —
the withdrawn figures appear only inside explicit supersession or quarantine markers, the §3.3 table
prints the Agaram-only values, and the abstract, §1.2, §1.3, §2.3a, §3.5, §4.1, §4.7a, §5 and §6 all
already state the one-series position. `systems/graph/publications.json` is likewise already corrected.

**Seven sites outside them still depend on the pool.** Five silently assert it (b), two draw
conclusions the Agaram-only quantity does not carry (c):

| file · line | cat | what it still rests on |
|---|---|---|
| `systems/graph/routes.json` :5504 `closure_note` | **c** | "PROGNOSIS: partly answered — two non-overlapping cohorts and **73 patients** now give a crude magnitude … what is missing there is a size-ADJUSTED analysis". The partial answer was the pool's; with 23 patients a **second event-count cohort** is missing too |
| `systems/graph/routes.json` :5509 `contribution` | **c** | "the PROGNOSIS question, which now has a crude **two-cohort magnitude**"; "the size-adjustment result printed inseparably from **the magnitude it defeats**"; "the review literature's metastasis claim is unestablished in either direction **once both count-bearing cohorts are in**". "Defeats" was separately withdrawn at §3.4 |
| `systems/graph/routes.json` :5555 `remaining_unknowns[3]` | **b** | "the crude two-cohort magnitude that landed 2026-08-08 (**46.7 % TAF15 vs 10.3 % EWSR1**)", plus HR 30.60 and HR 8.14 — themselves withdrawn Huang Table 1 quantities |
| `systems/graph/routes.json` :5556 `remaining_unknowns[4]` | **c** | "the two count-bearing cohorts disagree on sign …, **the pooled gap is 9.2 points** …, and the largest series … reports **P = .728**" — every element is a withdrawn Huang quantity |
| `emc-fusion-partner-correction-register.md` :75 row A10 | **b** | "the outcome pool is **two** cohorts and **73** patients" — contradicted by row A43 in the same file |
| `emc-fusion-partner-correction-register.md` :78 row A13 | **b** | "§4.8 now names **0.0034** as its subject" — 0.0672 is again the live §3.3 value and §4.8 names neither |
| `partner-event-counts-2026-08-08.md` :50 | **b** | "what is now true … **7/15 (46.7 %)** against **6/58 (10.3 %)**", with no supersession marker |

Plus two **generated** views that reproduce the stale graph strings and must be **regenerated, not
hand-edited** (CLAUDE.md §7): `systems/views/L2-rt-partner-strat.md` :62 and :113, and
`systems/views/L3-publications.md` :236 — the latter still prints the entire pre-withdrawal endpoint
paragraph, including "*a magnitude this contrast has never had*", and already contradicts the
corrected `publications.json`.

## Artifact

- `pooled-dependency-ledger.json` — machine-readable, one entry per site with file, line or JSON
  path, category, the assertion, and why it fails.
- `UNAPPLIED-pooled-dependency-propagation.diff` — 3 files, 4 hunks covering the 7 (b)/(c) sites, **not applied**.

## Validation

- `checks/01-rederive-artifact` — independent re-derivation of all live values, exit **0**.
- `checks/02-build-diff` — `git diff --no-index`, exit **1** (git's "differences found"; the expected
  value, recorded as measured).
- `checks/03-git-apply-check` — `git apply --check -p1 --verbose`, exit **0**, all three patches
  check clean. `git status --porcelain` on the three targets is **empty**: nothing was applied.
- `checks/04-patched-json-parses` — the patched copy of `routes.json` parses as JSON (83 routes),
  exit **0**.
- `checks/05-ledger-parses` — the ledger parses, exit 0.

## Provenance

Live values re-derived from `emc-fusion-partner-pooling.json` `{events, denom}` integers
(cohort `agaram-2014-outcome`, sourceId `agaram2014`, PMID 24746215). Withdrawal status read from
§3.3 lines 402–409 of the manuscript, `cohorts[huang-2023-outcome].withdrawn_2026_09_08`, and the
settled `FP-three-pin-2026-09-09/RETIREMENT-RECORD-2026-09-09.md`. No source was fetched; no PubMed
or PMC tool was called; no network egress was attempted.

## Limitations

- **The pool stays withdrawn.** Nothing here reinstates a Huang 2023 input, computes a
  Huang-dependent sensitivity, or treats the withdrawal as a finding that Huang's published counts
  are wrong. It is scoped absence.
- **No clinical claim.** 3/7 vs 1/16 is a crude proportion of **recorded** disease-specific-death
  events in one consecutive surgical series over unequal, uncensored observation windows, with one
  further *EWSR1* patient dead of unknown cause outside the numerator. It is not a survival
  probability, not adjusted, not a prognosis, and no efficacy, safety, selectivity,
  therapeutic-window or readiness claim is made or implied.
- **The diff is not applied and I do not own these files.** `routes.json` is the canonical graph and
  the register and memo are shared; only the parent records shared state.
- **The generated views are not in the diff** by design — patching a generated file would be the
  wrong fix and would drift from its source.
- **Scope of the sweep**: the repository's `.md`/`.json`/`.py`/`.mjs` files, excluding this
  campaign's own lane directories (which contain retained before/after snapshots that must not be
  edited) and `CLAUDE-history.md`. A dependency expressed without any of the searched tokens and
  without the words "pool", "cohort", "magnitude" or "count-bearing" could have been missed.
- **Nothing about the FP test suite.** It stands where the retirement record left it (107 failed /
  75 passed, unresolved); this lane did not run or triage it.

## Stop condition

Reached. The dependency closure is enumerated, the (b)/(c) sites have a proved-appliable diff, and
the remaining work is a parent decision: apply the diff to `routes.json`, the register and the
memo, then regenerate `systems/views/`. If the parent declines the graph hunks, the ledger still
records the three stale route strings and the two stale views as known, dated defects.
