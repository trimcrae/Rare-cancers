---
id: DOC-OPUS-CAMPAIGN-B2-PROMOTION-ORIGINALS
title: "B2 two-episode and promotion-lane originals, 2026-09-08"
level: L4
kind: index
status: live
purpose: >
  Describe the second bounded archive of original campaign evidence — B2's two execution episodes and
  the print follow-through, the eight promotion lanes, and the four finding lanes — so a collector can
  verify every member by hash before issuing a receipt.
scope: >
  L4. Original bytes. It does not repeat the earlier 147-member archive, which is already receipted
  and closed.
audience: [maintainers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# B2 and promotion-lane originals

`campaign-b2-promotion-originals-20260908.tar.gz` — 5,496,153 bytes,
sha256 `f1e54e03bf48377a95de88b851de8314ce00202e5d5c638a78b4c4451ccaa5fa`.

223 members, **185 regular files**, **14,003,350 bytes** measured per file. Every member path is
relative; none contains `..`; none is a symlink or other non-regular entry, and nothing was
dereferenced. Per-member hashes ship beside this file (`…SHA256MANIFEST.txt`) and again inside the
archive at `./SHA256MANIFEST.txt`.

⛔ **Verify every member against the manifest before any cleanup. This grants no deletion
authorisation**, and every lane remains in place on the container.
⛔ The earlier 147-member small-originals archive is **closed and receipted**; nothing here repeats it.

## B2, both episodes, and the print follow-through

`lanes/b2-lane/` carries `out/` (the builder, registration, metadata and test diffs, plus the literal
run logs), `legibility/` (`VERDICT.txt`, `ARITHMETIC.txt`, `PLACEMENT-committed.txt`,
`JOURNAL-FULLWIDTH-CORRECTION.diff`, the page and crop PNGs, both render logs, `crop.py`, `inkbox.py`),
`orig/`, `stage/`, `verify/`, `STATE.txt` and the three episode-2 scripts.

Two results are preserved **as failures**, unaltered and correctly labelled:
- `out/BASELINE-fullsuite-INTERRUPTED-NOT-PASSED.txt` — the pre-patch full-suite baseline, killed on
  instruction before completion. Its partial dot-and-F output ends mid-line at 71%. ⛔ It has no EXIT
  marker and none was fabricated. The deselected `committed_artifact` tests were not run and are not
  passed.
- `out/AFTER-fullsuite-OUT-OF-SCOPE-NOT-A-GATE.txt` — the post-patch run that did complete:
  `28 failed, 1695 passed, 4 skipped, 237 deselected, 5 errors`, `EXIT=1`. ⛔ With no completed
  baseline, **no failure in it is attributed to the B2 candidate**, and nothing it surfaced was
  repaired.
- `legibility/VERDICT.txt` — the print QA **FAIL** on the journal column, at 3.03 pt ticks and 2.71 pt
  smallest type, kept alongside the corrected placement rather than replaced by it.

⚠ `lanes/b2-lane/sandbox/` is **deliberately excluded**: 673,696,076 bytes, a duplicated copy of the
repository working tree from episode 1. It stays in place on the container. `SANDBOX-EXCLUDED.txt`
inside the archive records this.

## Promotion and finding lanes

`lanes/pm-methods`, `pm-endpoint` (the frozen handoff, zero edits), `pm-tcip`, `pm-sl`, `pm-mono`,
`pm-deg`, `pm-biomort`, `pm-viral` (the conclusive negative — VP1 is **Vaccine Path**, not a
viral-peptide manuscript, and no such document exists), `ma1-lane` (the legitimate replacement for
that freed slot), `hs1-lane`, `oi1-lane`, `cr2-lane`, `cg1-lane`.

⚠ `lanes/oi1-lane/` is **empty**: that worker needed no working files and said so. Its result survives
as its child JSONL and as the applied producer change.

## Child JSONLs and parent extracts

`child-jsonl/` holds the original transcripts and `.meta.json` for the fourteen children of this
batch. `parent-transcript/B2-PRINT-AND-POLLERS-literal-extracts.md` carries ten literal
`tool_use`/`tool_result` pairs — the builder-patch application, the production build, the stamp and
figure verification, the CTM extraction, the type-size recomputation, the normalised byte-identity
check, and the poller stop — each with its original tool id, both record uuids, both timestamps and
the recorded `is_error` flag. Nothing was re-run to produce them.

## The three Bash pollers

Task ids `b3ulnxyhf`, `bxstzcmgr`, `byub4hlih`, each waiting on an EXIT marker for the interrupted
baseline that will never emit one. All three now read `Terminated`. ⛔ No EXIT marker was fabricated,
no skipped or deselected test was recorded as a pass, and the baseline output they were waiting on is
preserved above exactly as it was written.

## Still open, and named rather than implied

- **`S3 clipped in outgoing PDF`** — Supplementary Table S3 on page 6 of the outgoing PDF is too wide
  for the right-hand column and its TAF15 column is clipped at the page edge. The scoped repair is in
  progress. **Reopening condition: a corrected actual proof showing every source cell and the caption
  within page bounds at unchanged type size.**
- The **6 pt readability threshold remains an asserted convention**, not a sourced venue rule, and the
  venue guidelines' HTTP 403 stays an unresolved retrieval. No route was changed to get around it.
