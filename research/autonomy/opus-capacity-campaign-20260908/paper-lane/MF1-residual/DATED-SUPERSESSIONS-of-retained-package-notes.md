---
id: DOC-MF1-RESIDUAL-DATED-SUPERSESSIONS
title: "MF1 residual — dated supersessions of three statements in the retained repair package"
level: L4
kind: memo
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Dated supersessions, 2026-09-08 — three statements in the retained MF1 repair package

⛔ **No retained byte is edited.** Each file named below keeps its exact bytes and its verified SHA-256,
because those identities are cited in the reviewed-input manifest, in the intake receipt and in the
integration execution record. The corrections live here, beside them, dated.

---

## S1 · The "no regeneration needed" patch instruction is WRONG and is withdrawn

**Where:** `MF1-repair/patches/CURRENT-SUMMARY-PATCHES.md`, lines **249–252** (file **11,940 B**,
sha256 `d455f14daabe8937c26233c74ebc05e28bd011d52b3a137c5339de713074658a` — unchanged).

**What it says:** that the census must be regenerated after P1–P6, but the MF1 extraction needs no
regeneration **because it does not read the roadmap**.

**Why it is wrong:** the extraction does not read the roadmap *directly*. It reads
`research/modalities/instrument-census.json`, which is **generated from roadmap §3.1 and §3.2** by
`research/modalities/instrument_census.py`, and it copies that file's `scope_limit` and `result` fields
straight into the reader-facing supplement. The real chain is

> **roadmap current rows → `instrument-census.json` → the MF1 extraction → `MF1-instrument-inventory.md`
> and `degrader-methods-failure-record-SI.md`**

so a roadmap correction reaches the supplement only after the census is regenerated **and** the extraction
is re-run. That missed dependency is exactly how the supplement came to republish three claims the main
text withdraws.

**Correct instruction, 2026-09-08:** the chain above is normative. It is now stated in the manuscript
(§3, *The display chain*) and in `patches/README.md` beside the residual patch. ⚠ The a6 integration
commit repeated the inaccurate instruction; that repetition is superseded here too, and the applied edits
themselves are unaffected.

---

## S2 · The check-summary README overstates two things

**Where:** `MF1-repair/checks/README.md` (retained byte-for-byte; unchanged).

**Two inaccurate statements, corrected:**

1. **"Attempts 2 and 3 both had 2666 errors and no owned-file error."** The retained streams say
   otherwise. `systems_check` ran three times — attempts **05 / 14 / 20** — and returned **exit 1** every
   time, with **2695 / 2667 / 2666 ERROR** respectively. ⛔ **Attempt 14 still reported the MF1 termination
   memo's missing frontmatter — an owned-file error — and attempt 20 no longer did.** The summary is
   wrong for attempt 2 on both the count and the owned-file claim.
2. **"Every command file is exact."** The final extraction's `.cmd` (attempt **22**) is abbreviated:
   `python3 .../extract_mf1_inventory.py (final settle)`. ⛔ **The literal invocation was not recorded and
   is NOT reconstructed here.** A shorthand command file is preserved as shorthand.

⛔ **Nothing was rerun to change any of this**, and no stream was replaced. The full corrected reading of
every retained attempt is in `CHECK-RUN-RECORD.txt` beside this file.

---

## S3 · The reviewer's and the adjudication's combined result-object count

Superseded by `DENOMINATOR-ERRATUM.md` in this directory: **17 is the first-prefix count, 1 is the
chainfix count, and 18 across both is correct.** The original mistaken baseline, the focused report and
the root memo all stay **immutable**; the erratum stands beside them and is not an author-only blame
assignment.

---

⛔ **None of these three supersessions is a gate result, an all-green report or a scientific clearance,
and none of them lifts any hold on the MF1 manuscript.**
