---
id: DOC-NEOANTIGEN-5-FINDING
title: "NEOANTIGEN-5 — the EWSR1 accession defect in the junction novelty guard, independently confirmed; NEOANTIGEN-4's fix shown non-altering on committed inputs; and the failing-then-passing test the fix was missing"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# NEOANTIGEN-5 — confirmed from source, proved verdict-identical, and paired failing/passing test

Writes confined to this directory. Nothing applied, added, committed or pushed; no preflight; no
subagents; no network (routes B1/B2/B4/B8/B9 untouched — **no proteome or isoform sequence was
fetched**); R1/R2/R3/R4 not restarted. **No guard, floor, gate, matcher, pin or test is weakened
anywhere in this lane — every change ADDS.**

⛔ Nothing here is an immunogenicity, presentation, efficacy, safety, selectivity,
therapeutic-window or clinical-readiness claim, in either direction. This lane is about one
software guard's coverage.

## 1 · Question

Does the reported `PARENTS` accession defect in `research/modalities/junction_proteome_novelty.py`
reproduce against the source itself; does NEOANTIGEN-4's UNAPPLIED fix change any published
verdict or count on the currently committed inputs; and can a test be written that actually fails
without the fix and passes with it?

## 2 · Merit

`⛔_upstream_filter_check` is the only automated statement this repository makes that its junction
screen's own two-protein novelty filter worked. A guard that can structurally only inspect one of
the two parents reports `consistent` for a whole class of failure it cannot see. That is worth
fixing, and worth fixing in a way that a future regression cannot silently undo — which requires a
test whose failure is demonstrated, not asserted.

## 3 · Evidence gap this closes

NEOANTIGEN-4 found the defect and proposed a one-line fix, but (i) the finding stood on one lane's
report, (ii) the fix was never shown to leave the published numbers untouched, and (iii) the
existing suite passes identically with and without it — so nothing in the repository could catch a
regression. Named inputs: `research/modalities/junction_proteome_novelty.py`,
`research/modalities/tests/test_junction_proteome_novelty.py`,
`research/modalities/junction-proteome-novelty.json`,
`research/modalities/junction-selfsimilarity.json`,
`research/modalities/fet-sequences-cache.json`.

## 4 · Step 1 — the defect reproduces, established from the source (`checks/01`)

| where | accession recorded for EWSR1 |
|---|---|
| `junction_proteome_novelty.py:85` (the guard) | **`P56945`** — `PARENTS = {"P56945": "EWSR1", "Q92570": "NR4A3"}`; referenced only at lines 85, 281, 283 |
| `tests/test_junction_proteome_novelty.py:20` (fixture) | **`P56945-2`**, named `EWS_HUMAN` — the fixture bakes in the same accession, so `test_an_isoform_hit_counts_and_is_flagged_as_a_parent` passes on whichever accession the map happens to hold |
| `junction-selfsimilarity.json` (real recorded proteome hits) | **`Q01844`, `Q01844-2`, `-3`, `-5`, `-6`**, each named `EWS_HUMAN RNA-binding protein EWS` |
| every other module (`fusion_neoantigen.py:78`, `nr4a_paralogue_unique_residues.py:54`, `emc_fet_construct_designs.py:113`, `fusion_idr_features.py`, `nr4a3_structure.py`, `emc_fet_idr_census.py`, `emc_condensate_calvados.py`, `emc-construct-inputs.json`) | **`Q01844`** |

**Confirmed, independently and as described.** The searched proteome names human EWSR1 `Q01844`;
the guard's map does not contain it; `PARENTS` is consulted only in the `parent_hits` loop, so a
junction peptide occurring verbatim in wild-type EWSR1 or an EWSR1 isoform is counted in
`n_found_in_proteome` yet contributes no `parent_protein_hits` entry and does **not** trip `BROKEN`.
This lane does **not** assert what `P56945` designates — that would need a lookup, and the route is
closed.

## 5 · Step 2 — the fix is strengthening, not weakening (`checks/01`, `03`, `04`, `08`)

`PARENTS` is read in exactly one place: the loop that maps accessions **already recorded** in each
peptide's `proteome_hits` onto parent names. Hit/miss classification and all four counts are
computed before it is consulted. Replaying that loop over the committed
`junction-proteome-novelty.json` under both maps (`neoantigen5_guard_replay.py`):

| | n_peptides_tested | n_found_in_proteome | n_novel_proteome_wide | n_binders_found | verdict | parent hits |
|---|---|---|---|---|---|---|
| **BEFORE** (`{P56945, Q92570}`) | 174 | 4 | 170 | 1 | `BROKEN — a parent-filtered peptide matched a parent protein` | DMPCVQAQ, DMPCVQAQY, DMPCVQAQYS, DMPCVQAQYSP — all `Q92570-3` / NR4A3 |
| **AFTER** (`{Q01844, P56945, Q92570}`) | 174 | 4 | 170 | 1 | `BROKEN — a parent-filtered peptide matched a parent protein` | identical, same four, same accessions |

`IDENTICAL: True`. The replay is not free-standing: the **unpatched** replay reproduces the
committed artifact's own `⛔_upstream_filter_check` block and all four counts exactly
(`step2_replay_fidelity… : true`), so it is modelling the audited code path rather than a
paraphrase of it. No committed hit carries any `Q01844*` accession
(`step2_q01844_among_committed_hits: false`), so the added key is simply unreachable on these
inputs. The existing 9-test suite passes on the committed tree (`checks/08`), on an unpatched copy
(`checks/03`) and on a patched copy (`checks/04`) — 9 passed, 9 passed, 9 passed. **The change adds
detection capability and alters no published result.**

## 6 · Step 3 — the paired failing/passing test (`checks/05`, `checks/06`)

New file `research/modalities/tests/test_junction_proteome_novelty_parent_accession.py`
(**added**; the existing test file and its fixture are untouched, so `n_sequences == 3` keeps its
meaning). It uses its own FASTA whose EWSR1 records are **real, committed sequence**: exact
contiguous windows of canonical human EWSR1 from `fet-sequences-cache.json` (`EWSR1`), residues
1–20 (`MASTDYSTYSQAAAQQGYSA`) and 38–57 (`QQSYGTYGQPTDVSYTQAQT`); each test peptide
(`TDYSTYSQA`, `SYGTYGQPT`) occurs exactly once in that canonical sequence and in none of the other
fixture records. The run goes through `main()` end to end with only the network fetch replaced, and
parses via the module's own `_parse_fasta`.

| run | module | result | exit code |
|---|---|---|---|
| `checks/05-newtest-vs-UNPATCHED-must-fail` | committed `PARENTS` | **3 failed, 2 passed** — the wild-type-EWSR1 peptide is found but the verdict stays `consistent` | **1** |
| `checks/06-newtest-vs-PATCHED-must-pass` | patched `PARENTS` | **5 passed** | **0** |

The three that fail without the fix are the map assertion, the canonical-EWSR1 `BROKEN` assertion,
and the `Q01844-2` isoform-prefix assertion. The two that pass either way are deliberate: a
negative control (an unrelated `P00002` hit must still read `consistent`, so the fix does not turn
the guard into a blanket flag) and the retention check on `P56945`. **The deliberate failing run is
preserved in full.**

⚠ The `Q01844-2` record carries a **canonical** EWSR1 window under an isoform accession purely to
exercise the `acc.split("-")[0]` prefix split. It is **not** a claim about isoform EWS-B's real
sequence: no EWSR1 isoform sequence exists in this checkout and that sequence is **UNKNOWN** here.
This is stated in the test's own docstring, not only in this report.

## 7 · Preserved failure — `checks/02` (exit 1), not caused by these tests

The first run of the existing suite on the committed tree exited **1**: the 9 tests all PASSED and
`research/modalities/tests/conftest.py`'s `tracked_tree_guard` then failed at `sessionfinish` with
`the test run CHANGED tracked files that it did not find changed:` and an **empty** file list.
Diagnosis (`checks/07`): a concurrent writer in this shared checkout was modifying tracked files
during the run — `git status` moved from one modified tracked file to two while this lane ran
(`research/manuscripts/dependency/…-dependency.md`, then also
`research/manuscripts/citation-provenance-ledger.json`), neither of them touched by this lane.
`checks/07` and `checks/08` re-run the same suite and exit **0**. The failing run is kept as-is; the
exit codes are real (`run_check.sh` records `$?` of an unpiped command).

## 8 · Artifact · validation · provenance · limitations · stop condition

* **Artifacts.** `UNAPPLIED-01-junction_proteome_novelty-parent-accession.diff` (byte-identical copy
  of NEOANTIGEN-4's diff, carried here so the stack is self-contained),
  `UNAPPLIED-02-add-test_junction_proteome_novelty_parent_accession.diff` (new test file),
  `new_test_test_junction_proteome_novelty_parent_accession.py` (the readable source of diff 02),
  `neoantigen5_guard_replay.py`, `neoantigen5-guard-replay.json`, `run_check.sh`, `checks/01–11`.
* **Validation.** Replay fidelity assert against the committed verdict block; the existing suite
  green on committed, unpatched-copy and patched-copy trees; the new test proved failing (exit 1)
  and passing (exit 0) across the same diff; a negative control inside the new test; every diff
  proved with `git apply --check -v` — **`checks/09` exit 0, `checks/10` exit 0, `checks/11`
  (both together, in order) exit 0**. Nothing was applied: `git status` shows no lane-caused
  modification to any tracked file.
* **Provenance.** Everything read in place from this checkout. Patched module built by running
  NEOANTIGEN-4's diff through `patch -p1` into a scratch tree; a line-filtered diff of the two
  copies shows the `PARENTS` line and its new comment as the only difference. Cost **$0** — no
  network, no GPU, no paid API.
* **Limitations.**
  1. The equivalence in §5 is over the **currently committed** `junction-proteome-novelty.json`
     (174 peptides, 4 hits, all `Q92570-3`). It is not a claim about a future re-run: the whole
     point of the fix is that a future proteome fetch could produce an EWSR1 hit, which would then
     — correctly — flag. It is a claim that **no published number or verdict changes**.
  2. The network fetch path is **not** exercised anywhere in this lane; routes B1/B2 are closed.
  3. `P56945`'s actual identity is not asserted. It is retained, never removed.
  4. The new test's isoform arm exercises the accession-prefix split, not a real isoform sequence
     (§6). Real-isoform coverage needs the networked runner.
  5. Exact substring only. Nothing here speaks to near-self peptides, presentation or immunogenicity.
* **Stop condition.** Reached. The defect is confirmed from source, the fix is proved
  verdict-identical on committed inputs, and the missing test exists with both halves of its
  failing/passing pair recorded. Applying either diff is the owner's call; this lane does not apply,
  commit or push.

## 9 · Next credible independent work (not done, not authorised here)

1. Owner applies both diffs together (`checks/11`) and re-runs the CI novelty job so the guard
   covers both parents with a regression test behind it.
2. On the networked runner, add a fixture built from a **real** EWSR1 isoform sequence, replacing
   the prefix-split stand-in of §6.
3. Audit the remaining accession maps in `research/modalities/` for the same class of defect — a
   guard keyed on an accession no artifact in the repository uses.
