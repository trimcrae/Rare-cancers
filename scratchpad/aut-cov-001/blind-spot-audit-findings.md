---
id: DOC-AUT-COV-001-AUDIT
title: AUT-COV-001 blind-spot audit — full findings, including what was NOT fixed this round
level: —
kind: memo
status: historical
canonical_for: []
purpose: Record a dispatched seat's full audit of claim_coverage.py's census pattern for notation blind spots, including the reusable shapes found but deliberately not built this pass.
scope: One seat's working log for ledger item AUT-COV-001 (2026-08-28) — not a durable reference; a future hardening round should read it rather than re-audit from zero.
audience: [autonomous research agents]
date: 2026-08-28
last_verified: 2026-08-28
---

SEAT=AUT-COV-001-seat
WORKTREE=/home/user/Rare-cancers/.claude/worktrees/agent-a4027037beeede805

# AUT-COV-001 blind-spot audit — full findings, including what was NOT fixed this round

## Method

1. Read `research/manuscripts/claim_coverage.py` in full, especially `_pin_patterns()`,
   `_test_patterns()`, `is_selective()`, `census()`.
2. Read the CYC-0013 commit (`70c5288c1`) that first found this class of gap on
   `emc-fusion-partner-stratification.md`: `_CENSUS_STATS` in
   `test_fusion_partner_prose_matches_its_artifact.py` added four notation predicates
   (`n = N`, a p-value in both printed forms, `HR`, a measurement in cm/months).
3. Sampled real, uncovered sentences from `nr4a3-degrader-paper.md` (3/966, "coverage in name
   only") and re-read `emc-fusion-partner-stratification.md`'s own uncovered set
   (`claim_coverage.py --uncovered=<path>`) for notation shapes NOT in the existing pattern set.
4. Cross-checked each candidate shape against the wider manuscript corpus with `grep -rl` to
   confirm it is REUSABLE (appears in many documents), not a one-off local phrasing.

## Shape found and FIXED this round

**A fold-change printed with the multiplication sign** (`×`), e.g. this document's own:

    "in it SEMA3C reads **1.8× normal tissue and 1.7× other sarcomas** across 4 EMC libraries"

Confirmed reusable: `grep -rlE "[0-9]\.[0-9]+×"` and `grep -rlE "[0-9]+-fold"` across
`research/manuscripts` hit 40+ files, including three of the ledger's own named zero-coverage
documents (their sentences, not fixed this round — see below):

  * the zero-coverage fusion-output manuscript's own SET-SPECIFIC enrichment:
    "d +1.1311, p_emp ≤ 0.0005, **11.9× threshold**" and "8,501–18,666 peaks, **55–121×** the
    deepest previously available"
  * the degrader-family manuscript with the worst coverage-per-investment ratio (3/966):
    "the **de novo 401** ... margin (+12.83) is barely below its single-snapshot value" region
    uses × implicitly via ratios, and elsewhere "the miss ~34× the statistical uncertainty"

Added to `_CENSUS_STATS` in `test_fusion_partner_prose_matches_its_artifact.py` (a fifth
alternative, `\d+(?:\.\d+)?×`), and the two GSE28866 SEMA3C figures that had sat in
`DECLARED_NOT_ARTIFACT_OWNED` (class "foreign-artifact") were promoted to real bindings against
`research/modalities/gse28866-tumour-vs-normal.json` — the "declared" status was a scoping
convenience (bind()'s `value` callable only ever received the pooling artifact), not evidence the
numbers were actually unbindable. Verified against the artifact's own `ratio_calibration.
per_gene.SEMA3C` block (`emc_over_normal=1.8175`, `emc_over_sarcoma=1.6622`, both round to the
prose's 1.8/1.7) and `per_gene.values.SEMA3C._n_emc_libs=4`.

Deliberately NOT added: the spelled-out "N-fold" word form. This document's two instances of
"-fold" are the WORD form ("differ about two-fold in mean follow-up"), and a digit-anchored
pattern must not match it — that would be a false positive, credited to no binding. A future
guard that wants the spelled-out form needs its own predicate and its own verification against
whichever document actually uses it numerically.

## Shapes found and confirmed reusable, but NOT built into a guard this round (out of scope)

These are real, reusable notation shapes read directly off real sentences. Building a genuine
BINDING for any of them (not just a bare regex — see "why a bare regex is not enough" below)
requires locating and verifying the specific committed artifact behind each occurrence, which is
a much larger, per-document undertaking than one hardening pass can responsibly absorb. Recorded
here so the next session does not have to re-derive them from scratch.

1. **A free-energy value in kcal/mol or kJ/mol, frequently with a ± standard deviation or
   inter-replicate spread** — extremely dense in `nr4a3-degrader-paper.md` (the paper this repo
   has invested the most hardening effort in, and the one CLAUDE.md's own status calls "coverage
   in name only" at 3/966):

       "the absolute ΔG_bind is strongly conformer-dependent (+8.17 ± 0.98 vs +3.5 kcal/mol on
       the AF2-opened conformer, a ≈ 4.7 kcal/mol shift larger than the selectivity margin)"

       "ΔΔG_coop = −0.599 kcal/mol at n = 3 vs a target of +0.944 ... making the miss ~34× the
       statistical uncertainty"

   Pattern shape: `[+-]?\d+(?:\.\d+)?\s*±?\s*\d*(?:\.\d+)?\s*(?:kcal|kJ)/mol`. Reusable across
   every MD/free-energy paper in the degrader and occupancy families (grep confirms
   `nr4a3-degrader-paper.md`, `fusion-selective-andgate-degrader-paper.md`,
   `nr4a3-monovalent-pocket-route.md`, `tcip-induced-interface-preprint.md` all use it).

2. **A distance in Ångström (Å)**, almost always an RMSD or a docking/contact distance:

       "pocket-local Cα-RMSD median 3.56 Å, handle Cα-RMSD 3.44 Å (global 7.63 Å)"

   Pattern shape: `\d+(?:\.\d+)?\s*Å`. Same document family as (1).

3. **A simulation duration in nanoseconds (ns)**:

       "On the committed 60 ns cumulative trajectory (1200 frames at 0.05 ns/frame...)"

   Pattern shape: `\b\d+(?:\.\d+)?\s*ns\b`. Same family.

4. **A confidence/t-interval in bracket form**, e.g.:

       "95 % *t*-interval **[−9.80, +0.28]** kcal/mol"

   Pattern shape: roughly `\[[-+]?\d+\.\d+,\s*[-+]?\d+\.\d+\]` paired with "CI" or "interval" in
   the preceding clause. Confirmed reusable: `grep -rlE "95% CI|95 % CI|CI \["` across
   `research/manuscripts` hits 27 files, including several of the ledger's own zero-coverage
   documents (the ATR/dependency-family manuscript, the endpoint-response manuscript, the
   vaccine-development-path manuscript, the HLA-coverage manuscript).

5. **A dollar-figure spend amount**, e.g. "$73.79 of realised GPU spend against a derived
   authorisation ceiling of $74.91" — already partially covered elsewhere in the repository
   (`systems/tests/test_autonomy_priority.py`'s dollar regex, per a recent amendment in
   `research/autonomy/amendments.jsonl`) but not by `claim_coverage.py`'s own harvested pattern
   set for any manuscript. Lower priority: spend figures are usually singletons rather than
   repeated claims, so the "drift between multiple sites" failure mode this whole census exists
   to catch applies less here.

### Why a bare regex is not enough (why these were not just dropped into `_CENSUS_STATS`)

Adding a notation regex to `_CENSUS_STATS` only produces real coverage inside a guard that ALSO
enforces "every match falls inside a BINDING or a DECLARED span" (see
`test_every_statistical_quantity_is_bound_or_declared`) — the census's own harvester credits a
pattern based on whether it is SELECTIVE (matches few sentences) and present in a test file that
opens the document, not on whether it is actually checked against anything. A kcal/mol or Å
pattern dropped into a NEW guard for `nr4a3-degrader-paper.md` with no real bindings behind it
would be exactly the false-positive failure mode `paper-hardening` §8b documents repeatedly: a
census crediting coverage that is not there. Building it properly means, for each of the ~50-100
occurrences: locating the specific JSON/script artifact named beside it in the prose (most
sentences DO name one — `pocket_analysis_summary.json`, `nr4a3-metad-crossreplica.json`,
`selectivity_calibration.py`, `congeneric-rbfe-map.json`, etc. — this document is unusually good
about naming its own evidence inline), loading and verifying the exact value, and writing a
`bind()` call the way this round did for GSE28866. That is a full hardening round's worth of
per-document work, not a pattern-set extension, and the task instructions explicitly scope this
ledger item to finding the missing NOTATION SHAPES rather than processing every document.

## Shapes checked and found NOT to be a blind spot

* Odds ratios (`OR = N`): `grep -rlE "\bOR ?[:=] ?[0-9]"` returns nothing across
  `research/manuscripts` — not used anywhere in this corpus, so no predicate needed.
* Plain percentages and `events/denom` fractions: already matched by `_CENSUS` in the same guard
  file, though `_CENSUS` itself is discarded by `is_selective()`'s breadth filter on this
  particular (percentage-dense) document — a DIFFERENT, already-diagnosed class of bug
  (`paper-hardening` §8b/§8b.1, "a pattern used with span-intersection logic is not the same
  thing as a standalone selective regex") and explicitly out of scope for this ledger item, which
  is about missing NOTATION, not the selectivity-threshold mechanism.
* A percentage-POINT differential ("the 4.3-point pooled gap", "22.4 points"): already has real
  bindings in this same guard file (`heterogeneity_comparator_arm.spread_percent`, lines ~1313-
  1406) for its live sentences; the one still-uncovered restatement
  ("The 4.3-point pooled gap in the table above is therefore a cancellation...") is a THIRD
  restatement of an already-bound fact rather than a new notation shape, and extending an
  existing, already-dense binding set to a third restatement risked colliding with bindings I did
  not fully trace through this file's ~2100 lines in the time available — recorded here rather
  than attempted blind.

## Preflight gate wiring

`claim_coverage.py`'s docstring and the ledger item make no mention of wiring it into
`scripts/preflight.sh`, and `grep -rn claim_coverage` over `scripts/preflight.sh` and
`.github/workflows/*.yml` returns nothing — it is invoked only by the manuscripts pytest suite
(`test_the_paper_states_what_its_own_claims_depend_on.py::test_claim_coverage_has_not_regressed`,
which DOES run inside `PREFLIGHT_TESTS=1`) and by hand (`python3
research/manuscripts/claim_coverage.py [--write|--uncovered=<path>]`). So the tool IS wired into
the commit-loop gate (the regenerate-and-ratchet test), just not as a standalone preflight step —
consistent with every other generated-deposit-artifact check in this repo (gate 11), and not
something this ledger item's text asks to change. Noted as an observation per the task
instructions, not acted on.
