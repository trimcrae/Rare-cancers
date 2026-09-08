---
id: DOC-MF1-REPAIR-CHECK-ARTIFACTS
title: "MF1 repair — the focused check artifacts, successes and failures alike"
level: L4
kind: memo
status: live
canonical_for: []
purpose: Preserve every check run against the MF1 correction batch's changed files, with the real exit code of each attempt, and attribute each surviving failure honestly.
scope: The checks applicable to the files this repair owns. It is not a full preflight, and it is not publication evidence.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---
# MF1 repair — check artifacts

Each check is stored as four files: `<n>.cmd` (the exact command), `<n>.stdout`, `<n>.stderr`, `<n>.exit`
(the real process exit code, captured with no pipe in the way). ⛔ **No attempt was overwritten**, and no
suite was retried to obtain green: attempts 2 and 3 exist because a **defect the check found was fixed**,
and attempt 1's failures are kept beside them.

⛔ **This is not a full preflight and is not publication evidence.** Only the checks applicable to the
changed owned files were run, as instructed. `PREFLIGHT_FULL` was not run and no publication gate is
claimed.

## What changed between attempts

- **Attempt 1 (01–09).** `systems_check` failed on files this repair created: the generated supplement and
  inventory carried Markdown links copied verbatim out of `instrument-census.json`, whose relative paths
  are written for `research/modalities/` and resolve to nothing from another directory (`K1`), and whose
  roadmap anchors were read as same-file anchors (`K2`); three new memos had no frontmatter (`D4`).
- **The fix.** `extract_mf1_inventory.py` now strips the link wrapper and keeps the label text, so no
  wording changes and no broken link is emitted; frontmatter was added to the three memos.
- **Attempt 2 (10–17) and attempt 3 (19–21).** Re-run after the fix. `systems_check` reports **no error on
  any file this repair owns**. Attempt 3 additionally covers the one-line addition of the supplement to
  `lint_claims.DEFAULT_TARGETS`.

## Results

| check | attempt | exit | reading |
|---|---:|---:|---|
| `lint_consistency.py` | 1 / 2 / 3 | 0 / 0 / 0 | pass |
| `lint_claims.py` (default corpus) | 1 / 2 / 3 | 0 / 0 / 0 | pass — 0 ERROR; attempt 3 includes the new supplement |
| `lint_claims.py` (owned files, 18) | — | 0 | pass — 0 ERROR, 6 WARN, all on withdrawal or quotation contexts |
| `lint_changed_prose.py` | 1 / 2 | 0 / 0 | pass |
| `lint_submission_residue.py` | 1 / 2 | 0 / 0 | pass |
| `lint_readability.py --report` | 1 / 2 | 0 / 0 | advisory report, no gate |
| `extract_mf1_inventory.py` | 1 | 0 | the extraction reruns deterministically |
| `systems_check.py --check` | 1 | **1** | ⛔ **FAILED, and 22 of the errors were this repair's** — see above |
| `systems_check.py --check` | 2 / 3 | **1** / **1** | still 1, on a **pre-existing** repository backlog of 2,666 errors; **zero** of them name a file this repair created or edited (verified by filtering the output for `MF1-repair` and `methods-record/`) |
| `lint_citations.py` | 1 / 2 | **1** / **1** | ⛔ **FAILED, and not this repair's.** All 13 errors are `TYPE CLAIM WITH NO CACHED METADATA` in `reports/W04b`, `W06`, `W09` and `W09e` — other owners' files. No error names a file this repair touched. The four identifiers this batch introduces (`doi:10.1158/0008-5472.can-25-1141`, PMID 17515897, PMID 9092472, PMID 9608532) are **anchored** in tracked JSON (`selcal-verdict.json`, `nr4a2-sparing-bound.json`) and raise nothing |
| `emc_systems_map_check.py --check` | 1 / 2 | **1** / **1** | ⛔ **FAILED, and not this repair's.** Five `O4` errors name surface-target and P-ST files; the sixth (`V1`) says the generated systems map differs from the registry. This repair edited no graph or registry file |

⚠ **A pre-existing failure is still a failure.** The two gates above are red in this tree and were red
before this batch; nothing here was changed to make them green, no baseline was widened, and no guard was
loosened. They are reported so the integrator can see exactly which red is inherited and which is not.

## Checks deliberately NOT run, and why

- `lint_style.py` — its `TARGETS` list is submission texts only and names none of these files. Adding a
  file to that list is a submission decision, and **no publication gate is cleared here**.
- `PREFLIGHT_FULL=1 ./scripts/preflight.sh`, the manuscripts suite, the modalities suite — out of scope
  under this batch's fences (no broad manuscript tests, no ablation sweep). The instruction was to run the
  specific existing checks applicable to the changed owned files after the edits settled, which is what
  the table above is.
- `reviewer_calculations.py` — ⛔ **not rerun.** It is review evidence and contains explicitly illustrative
  quantities.
