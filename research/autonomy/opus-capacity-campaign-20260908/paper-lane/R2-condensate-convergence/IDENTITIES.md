# R2 · Identities — before / after

## Frozen inputs: READ ONLY, byte-identical before and after this task

Verified at 2026-09-08T22:52Z (`checks/` and the commands below). No file in this list was
opened for writing at any point.

| path | bytes | sha256 | before == after |
|---|---|---|---|
| `research/modalities/emc_condensate_calvados.py` | 56611 | `786dd42140d136ef3f41a3ace8ec4789cf9f0f7a0f5d9194927b9a9c51613ac4` | yes |
| `research/modalities/emc-condensate-calvados.json` | 128930 | `5349094c7f99fe1e9fd6faf61d67d6a26ae54b4bacf05a850c9f2f1d8d55cef8` | yes |
| `research/modalities/emc-condensate-calvados-prespecification.md` | 22296 | `002131de4ce574015b77311b1a4973495651907d22f8ededcfe7a00057441cfb` | yes |

`emc-condensate-constructs.json`, `emc-condensate-window-eligibility.json` and
`emc-condensate-composition.json` were not read or written by this task's code paths beyond what
`emc_condensate_calvados.build_constructs()` loads internally, and were not modified.

Contract evidence: `checks/10`, `python3 research/modalities/emc_condensate_calvados.py --selftest`,
**exit 0**, `78/78 checks pass across 13 guard groups`.

## The 55 committed runs

Untouched. Not overwritten, not re-keyed, not deleted. No `trajectory_sha256` was altered. No new
run block was appended, because no run was executed.

## Files created by this task (all new, all inside this artifact directory)

- `PRECONDITION.md`, `PLAN-AND-COST.md`, `FINDING.md`, `IDENTITIES.md`, `CHECK-RUN-RECORD.txt`
- `scripts/sensitivity_second_half.py`, `scripts/drift_bound.py`
- `sensitivity-second-half-panel.json` — the two scored panels (`A_reproduction`,
  `B_second_half`) emitted by the **unaltered** frozen `score()`; a derived reading, not a run record
- `checks/01..12/` — one directory per execution attempt, each with `command.txt`, `stdout.txt`,
  `stderr.txt`, `exit_code.txt`
- `DIFFS/`, `patches/` — see below

## DIFFS and patches

**Empty, deliberately.** No tracked file outside this directory was modified, so there is no
unified diff to record. `patches/` is empty because no change to the frozen module was required:
the sensitivity re-score is achieved by substituting the input value `nu := nu_second_half` in a
copy of the run list before calling `score()`, with the module itself untouched. Placeholder
notes are written into both directories so their emptiness is a recorded decision rather than an
omission.
