---
id: DOC-OPUS-CAMPAIGN-FP-THREE-PIN-SIDECAR-RETENTION-20260909
title: "FP three-pin guard maintenance — raw sidecars retained, 2026-09-09"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# FP three-pin: the raw sidecars, returned normally

Root observed that the local `7b6` FP guard intake retained the validation NARRATIVE
(`../VALIDATION-2026-09-09.md`) but that the separate raw sidecars and the referenced scratch
`negfix.py` were absent from that changed-file delta. That is correct: the earlier commit carried
the two markdown records only.

**The originals still existed at their recorded paths, so they are preserved here rather than
described.** Nothing was recreated, re-run to impersonate an original, or hunted for across the
filesystem; the check was a direct look at the recorded scratch path.

| file | bytes | sha256 |
|---|---:|---|
| `negfix.py` | 5,123 | `9e7338f7819267bf186457ee4b4dd9ee4571d36edc5886968bde8bce9e129ac9` |
| `apply_edit.py` | 6,791 | `635d8d3eb47eb1113aba4b5a52e257150ca052c3f7f959fad2be7ab4238f1db3` |
| `retired_entries.json` | 2,645 | `0dca0da55d089f949f70baed24681a0ad1e2682f799eadd0371a630d0c10e899` |
| `lint.out` | 51 | `1c7d66cd81731b2725478de4ff28b37db1c9b1501fb2a2538b16404aa66edcd1` |
| `lint.err` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

`negfix.py`'s sha256 matches the value `../VALIDATION-2026-09-09.md` recorded for it exactly, so
this is the same file the negative fixtures were run from, not a lookalike. `lint.out` holds the one
line `lint_consistency: 0 ERROR across 29 target file(s)`; `lint.err` is genuinely empty — 0 bytes,
whose sha256 is the sha256 of the empty string, as shown above. It is retained as a zero-byte
`.txt`-class file, not padded with content it never had.

## What was never retained, stated as unavailable

* The **negative fixtures themselves** do not exist and never did as files. By design `negfix.py`
  copies the artifact and the manuscript into a `tempfile.TemporaryDirectory`, perturbs the copies
  there, and lets the directory be destroyed on exit. The retained `fixtures/` directory beside the
  script is **empty**. What survives is the generator plus its recorded pass/fail table — the
  fixtures are reproducible from the script, but no contemporaneous fixture bytes exist to return.
* No stdout/stderr capture of the `negfix.py` runs themselves was written at the time; the C0–C9
  results survive only as the table in `../VALIDATION-2026-09-09.md`. That table is a contemporaneous
  report, not a retained stream, and is not presented as one.

The parent independently re-ran its own negative fixtures against the UNMODIFIED
`lint_consistency.check_artifact_figures` before committing the pin change (recorded in commit
`91798e2e8`): perturbing either side of each of the three pins fired `A-figure-mismatch` quoting
exactly one captured number, and perturbing the neighbouring local-recurrence row's identical
`1/16 = 6.2 %` correctly did not fire. That is the parent's own check, run fresh, and it is not
offered as a reconstruction of the author's streams.
