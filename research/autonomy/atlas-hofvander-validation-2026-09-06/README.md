---
id: "DOC-ATLAS-HOFVANDER-CHECKPOINT-20260906"
title: "Frozen metadata and executable tissue RNA checkpoint"
level: "cross-cutting"
kind: "memo"
status: "live"
canonical_for: []
purpose: "Freeze and explain the tissue RNA evidence checkpoint before new target outcomes."
scope: "One public cohort, fixed address panel, overlap-reduced primary EMC."
audience: ["autonomous research agents", "external reviewers"]
date: "2026-09-06"
last_verified: "2026-09-06"
related: []
---

This packet freezes a single-cohort tissue RNA question before selecting target values. protocol.md contains the full estimands and decision rule; metadata-manifest.json retains all704 sample mappings and exact source digests. Source original bytes remain in the root worktree's .cache/emc-atlas-new-source-20260906; source paths are explicit in that manifest. The matrix is hashed as bytes and its header read for alignment; numeric target rows remain unopened to this analysis.

Primary EMC n9 after three explicit reused cases and one recurrence are excluded. The same primary-lesion policy applies to comparators. Original-S1 comparator counts are14 myxoid liposarcoma,13 low-grade fibromyxoid sarcoma and18 synovial sarcoma. Each year-matched contrast uses3 EMC; their union is4 patients. Context comparisons are60 myxofibrosarcomas and10 DFSP; matched DFSP is especially sparse (1 EMC versus3 in2021). Original diagnoses and deposited labels are retained separately. No samplewise-z cache is used as a raw per-gene rank input.

Synthetic-only validation: run `python -B analyze.py --fixture-output fixtures.json` from this directory. It checks half ties, all-zero ties, reversal, missing groups, invalid measurements, year weights, deletion reweighting, equal-histology weighting with unequal sample sizes, allocation pass/failure and bootstrap reproducibility. No empirical background process is running. Runtime used Python3 with numpy/openpyxl in the bundled Codex dependency runtime, routine medium research effort.

To reproduce metadata without values: `python -B metadata.py --source C:/Users/mcrae/.codex/worktrees/8010/EMC-Research/.cache/emc-atlas-new-source-20260906`. A first metadata run hit a Windows path-separator dictionary-key error before writing; corrected to portable slash keys, then metadata and fixtures completed. No scientific result was accessed during this repair.

Coordinator authorization format: JSON with `authorized_by` equal to `coordinator`, `authorized_utc` timestamp, and a `sha256` object mapping protocol.md,metadata-manifest.json,metadata.py,analyze.py to their approved SHA256 digests. `python -B analyze.py --authorization authorization.json` then verifies all four approved files and every pinned source digest, opens target values, and writes results/execution.json plus per-gene evidence and final result.json. Do not execute this mode before the focused protocol decision. The checkpoint does not by itself establish quantitative cross-cohort replication or publication readiness.
