---
id: DOC-OPUS-CAMPAIGN-PARENT-VERIFY-COPIES-20260909
title: "Parent re-execution copies — duplicates, retained rather than deleted"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# `_PARENT-VERIFY-*` — what these are, and why they are still here

Three directories, `_PARENT-VERIFY-MORTALITY-2`, `_PARENT-VERIFY-NEOANTIGEN-3` and
`_PARENT-VERIFY-CARE-DELIVERY-3`, are the parent's re-execution copies of three lanes. They exist
because those lanes' generators resolve the repo root by counting parent directories, so a copy in a
scratchpad resolves to the wrong root — the first attempt died on
`/tmp/research/literature/emc-mortality-probe.json`. A copy at the SAME directory depth runs
correctly, which is why they sit here beside the lanes rather than outside the tree.

**They are byte-identical duplicates of the committed lanes.** That is the measured result, not an
assumption: `genre-stratified-rates.json`, `reclassification-sensitivity.json`,
`genre-classification.json` and `neoantigen3-correspondence.json` all came back with the same
sha256 after re-execution, and `validate_v3.py` returned 131 passed / 0 failed. The parent's own
stdout for those runs, which IS unique, is committed separately under
`PARENT-VERIFICATION-2026-09-09/reruns/`.

An earlier record said these would be left untracked. They are committed instead. Nothing unique
would be lost by removing them, but campaign retention does not turn on whether the parent judges a
set redundant — a directory is released by a receipt naming it, and no such receipt exists for
these. Retaining a duplicate costs disk; deleting campaign evidence on my own judgement costs the
rule. The rule wins.
