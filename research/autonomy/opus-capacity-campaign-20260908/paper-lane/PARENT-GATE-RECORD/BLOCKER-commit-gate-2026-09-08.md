---
id: DOC-OPUS-CAMPAIGN-PARENT-GATE-BLOCKER-20260908
title: "Blocking condition on the normal immutable return, 2026-09-08"
level: L4
kind: blocker
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Blocking condition on the normal immutable return

Recorded in answer to the launcher's retention check. **Nothing here is a new requirement I
invented, and nothing here is a bypass.** The gate is red, it was red before this parent's work
existed, and I have not cleared it, rerun it, or granted it an amnesty.

## The exact blocking condition

`scripts/preflight.sh` — the repository commit gate named in `CLAUDE.md` §6 — **exits 1**:

```
⛔ a stale generated file ships a claim its own artifacts no longer support:
     claim coverage census        archive manifest
   STALE archive manifest -- rerun 'python3 research/manuscripts/aso_archive_manifest.py'
   Re-run `python3 research/manuscripts/claim_coverage.py --write` and commit the result
PREFLIGHT FAILED -- do not commit.
PINNED_SHA=8f1fe1c5e548dd016c21329d99a16e2db6d9719a+dirty
```

The complete stream is retained verbatim at `preflight3/stdout-and-stderr.txt` (488,132 B, sha256
`49131135a282efab8d99cb6464814d6da31cb657ece6afb5d38cfc65439b6d0f`) with its command and its
measured `EXIT=1`. **That failure stands as a failure.** Its `pytest (pure-logic suites) SKIPPED`
line stands too: a skipped suite is not a pass, and `tests.yml` — not this run — is the authority
there.

## ⭐ The failure is inherited, and it is not mine

Measured, not assumed. I unpacked `git archive HEAD` into a clean directory containing **none** of
this parent's work and ran both checks there:

```
claim_coverage.py --check       at HEAD 8f1fe1c5e  ->  exit 1, 14 drifted rows
aso_archive_manifest.py --check at HEAD 8f1fe1c5e  ->  exit 1
```

Stream retained at `claim_coverage-at-HEAD-stdout.txt`. **Both generated artifacts were already
stale at the current tip of the output branch.** The named drift is in already-committed manuscripts
(`fusion-partner/emc-fusion-partner-stratification.md`,
`methods-record/degrader-methods-failure-record.md`) — the MF1 and FP work that landed earlier.

## Why I cannot clear it now, and will not fake clearing it

Both checks **recompute from the live working tree.** Four admitted authors — TCIP, FP, P-ST and
MF1 — are writing into that tree right now, and three of them are rewriting the very manuscripts the
census harvests. Regenerating either artifact at this moment would commit a generated file built
from **half-written author prose**, which is precisely the defect the gate names.

So the honest position is: **the gate is satisfiable only on a settled tree.** It is not
satisfiable by anything I can do while the authors run, and I will not regenerate into it, rerun
preflight hoping for a different number, or commit over it on my own authority. **Only root can
authorise a dated, named gate exception; I am not taking one.**

## Completed artifacts available for immediate return, on that authorisation

All settled, all on disk, all with original bytes and real execution records. **No active
TCIP / FP / P-ST / MF1 partial work is in this set.**

| artifact | state |
|---|---|
| `INTEGRATION3-endpoint-ledger/` (63 files, staged) | 31/31 checks exit 0; RUN-03 and RUN-04 preserved as real failures; negative control rejected exit 1 with 14 failures; re-derivation byte-identical |
| `P-ST-correction/annotation-correction/APPLIED-2026-09-08/` | F03 applied once; before/after hashes, exact diffs, field map, leaf-by-leaf all-value invariance; apply EXIT=0, verify RUN-01 **EXIT=1 preserved**, RUN-02 EXIT=0, `check_pst_correction.py` **EXIT=1** (53 passed, 1 failed — `packet-manifest-reproduces`, deliberately left failing) |
| the two live files that edit touched | `gse28866-tumour-vs-normal.json` 28,606 B `386a0351…`; `gse28866_tumour_vs_normal.py` 31,856 B `404fe285…` |
| `TD1-repair/` + `research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md` | returned complete; candidate 41,911 B `12c082b3…`, byte-identical to `TD1-repair/frozen/` |
| `FO-pdf-production/DISPOSITION-root-2026-09-08.md` + the corrected `REPAIR-RECORD` | dated qualified disposition; the stale p10–11 claim superseded in place with its original wording retained |
| `CHILD-MODEL-FIELD-RECORD-2026-09-08.md` | compact actual model/start/tool metadata, no private reasoning |
| the four author contracts | `TCIP-repair/`, `FP-residual/`, `PST-residual/`, `MF1-residual/` |
| this record | `PARENT-GATE-RECORD/` |

## Missing original streams, named rather than reconstructed

* C2's completion record — its measured runtime, tool count and token usage passed out of this
  session's live context before the child-model record was opened. **Not reconstructed, not
  estimated, not recorded as zero.** Its work product and its seven real exit codes survive at
  `C2-correction/CHECKS-RUNS/`, including the preserved `RUN-02` EXIT=1.
* The `QA-REPORT.md` root read for the FO disposition (7,698 B, sha256 `d388791c…`) is **not present
  in this worktree** under that name or hash. Recorded as root's reading, not as something I
  verified.

## What I need

Either (a) root's explicit dated authorisation to commit the settled set with the inherited gate
failure named in the commit, or (b) I hold until the four authors return, regenerate both artifacts
once against the settled tree, run the gate once, and return everything together — which also clears
the inherited debt rather than passing it on again.
