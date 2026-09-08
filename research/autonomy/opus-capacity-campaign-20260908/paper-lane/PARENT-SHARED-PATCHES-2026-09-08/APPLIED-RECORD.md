---
id: DOC-OPUS-CAMPAIGN-PARENT-SHARED-PATCHES-APPLIED
title: "Parent-owned shared patches applied, 2026-09-08"
level: L4
kind: applied-record
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Parent-owned shared patches — APPLIED

**Ownership checked once before applying:** working tree clean at `f6107376c`, **no author lane
running** (all five returned), sole cloud parent. No competing writer.

## The shared files

| file | before bytes / sha256 | after bytes / sha256 |
|---|---|---|
| `systems/graph/publications.json` | 63,825 / `11b8a785ac95809d844f46f6427601c67f73f9137a063f6d91b4b93ba0d5bf53` | 68,537 / `e31fa506bc2fd8ff7e594c0284aa4e30cd2c5c0da65f7e864e1bc05b0d61c6f9` |
| `research/manuscripts/nr4a3-program-map.md` | 618,584 / `c4c60cec16984c62d8861f145971433a8daa5d3d89c366cafee07e15b31a6663` | 620,062 / `8d92e9e8656de3fa8fa371137772fcc051e5f26da28c4ed6179746a52950af48` |
| `research/modalities/instrument-census.json` | (pre-regen) | 31,770 / `f484afe4bb5795283dab8131cf47d3fe2d4204b401c559a41ad406366228526a` |
| `research/modalities/instrument-census.md` | (pre-regen) | 22,903 / `76847795b561893855fbdc7aa8e1a4dc285a4fa3d88b106dfb56bc0626258829` |

`BEFORE/` holds byte copies of all four.

## Scope, re-derived by the parent rather than taken on trust

**`publications.json` — 416 leaves before, 416 after; 0 added, 0 removed, 3 changed:**

| leaf | entry |
|---|---|
| `$[12].what_it_would_claim` | **PUB-FUSION-PARTNER** |
| `$[12].outcome_potential_why` | **PUB-FUSION-PARTNER** |
| `$[29].what_it_would_claim` | **PUB-TCIP** |

Exactly the two entries and the field counts the two authors reported — two fields for FP, one for
TCIP — and nothing else in the 33-entry graph. The file parses as one JSON document.

**`nr4a3-program-map.md` — 5 single-line replacements, 5 insertions / 5 deletions, at lines 986,
1773, 1778, 1783 and 3246.** These carry the six corrections Q1–Q6 (one line carries two): V11
"adequately powered" withdrawn — the 1/462 floor is discreteness, not power; V16 "registered in
advance" re-attributed to the retained protocol; V16 bound + absent-wedge withdrawn; V20's universal
"not recoverable by any downstream method" withdrawn; the surviving "with a quantified bound" clause
at `:3246` removed; and the `:986` absent-wedge reading withdrawn. **No wholesale rewrite of the
historical roadmap**; each correction is dated in place beside the wording it supersedes.

## The one admitted census update — spent, and only after the source settled

The sequencing the MF1 author filed is exactly what happened, and it is why the allowance was not
wasted:

| run | command | exit |
|---|---|---|
| `07-census-check-after-patch` | `instrument_census.py --check` | **1** — *"has DRIFTED from the roadmap — regenerate it"*, both files |
| `08-census-update` | `instrument_census.py` | **0** — the one admitted update |
| `09-census-check-post` | `instrument_census.py --check` | **0** |

Run 07's exit 1 is the proof that the update was necessary rather than a no-op. **The census was
never hand-edited**; it is generated, and it was corrected at its source.

**Census scope — 384 leaves before, 384 after; 0 added, 0 removed, 4 changed:**
`V11.result`, `V16.result`, `V16.scope_limit`, `V20.scope_limit`. Exactly the four live residue
cells, and no other instrument.

## The MF1 extraction — one non-settled attempt, then the settled one

`10-mf1-extraction-THE-ONE-ADMITTED` ran at **exit 0, stderr empty**: 10 results rows, 22 inventory
rows (route 4 + 16, census 22), 18 manifest inputs, 4 author-current scope overrides (V11, V16, V20,
V5) — **but `inputs NOT bound to their HEAD blob: 1 of 18`.**

That single unbound input is `research/modalities/instrument-census.json` — the file run 08 had just
regenerated and which was not yet committed, so its bytes did not match its HEAD blob at
`f6107376c`. **The binding check did its job.** An extraction whose manifest does not bind to
committed bytes is not settled, so this run is retained as the **pre-settlement attempt**, exactly as
measured, and the settled extraction is re-run after the commit against the final source bytes.
Neither run is relabelled, and no output is reconstructed.

## What was NOT done

⛔ No FP regeneration was repeated — the author's own deterministic run (exit 0, 0 numeric leaves
changed, 13 added, all inside the new `ascertainment_stages` block) already propagated the admitted
source changes, and re-running it would spend an allowance twice for no change.
⛔ No `systems/views/` regeneration, no claim-coverage or archive regeneration, no broad suite, no
biological producer, no renderer, no repeated preflight.
⛔ No guard criterion changed, no green preflight manufactured, and the pushed
`PARENT-GATE-RECORD/` originals are untouched.
