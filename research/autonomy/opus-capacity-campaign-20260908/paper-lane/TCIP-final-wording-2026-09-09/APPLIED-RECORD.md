---
id: DOC-OPUS-CAMPAIGN-TCIP-FINAL-WORDING-APPLIED-20260909
title: "TCIP six exact wording replacements — parent direct application"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# TCIP final wording — applied by the sole parent, 2026-09-09

Root disposition read IN FULL (`ROOT-DISPOSITION.md`, 5,098 B,
`94eb5f8e8e68c490e94fad23f0a90565ad57a4aba31396360b53f35d83b0d7ce`). Parent direct application; no
new author, reviewer, checker, sampler, census, statistic, source retrieval or broad test was
commissioned, and no publication clearance is claimed.

## Capsule intake, verified before anything was applied

Input ref `codex/opus-cloud-inputs-20260908`, exact commit
`9bceb53c2997dad0435c0ac6e92985445225582c` (base `7ecef60f1d3924d3bb4f8486943a104bec68f080`).

| object | bytes | sha256 | git blob |
|---|---:|---|---|
| `tcip-six-wording-original-inputs.zip` | 69,320 | `e9463b752ea4944c08cde46cf0ff6a09dd982e05ffec2a603d21b5c5480897de` | `348aa610bbcec80ef65c14cda79b1bf3f673f370` |
| `…-manifest.json` | 1,990 | `8ba288ad02babfc190d215db191f4f4880241c548eab295dc6976cf4451d23b1` | `9e06ab47ee8ba7e5e070ce71d95ce6494f8c1404` |

All checks pass and were run by the parent, not taken from the routing summary: **7 of 7 ZIP
members CRC-clean** (`testzip()` returns None), **zero unsafe member paths** (no `/` prefix, no `..`
traversal), and every member byte-count and sha256 identical to the manifest. Six originals total
**186,870 bytes**, matching `original_total_bytes`.

## Before-state, checked against BINDINGS.json

All three live files matched their recorded `before` identities EXACTLY, so there were no unrelated
intervening changes to preserve around:

| file | live before | recorded before |
|---|---|---|
| main | 55,272 B `f4954098…` | 55,272 B `f4954098…` |
| SI | 37,757 B `b7d97906…` | 37,757 B `b7d97906…` |
| `systems/graph/publications.json` | 70,224 B `800e844f…` | 70,224 B `800e844f…` |

## Application

The parent applied `TCIP-six-exact-wording-replacements.patch` (17,119 B,
`7e44c745ba51235d…`) with `git apply` — the actual patch, not a copy of the proposed files.
`git apply --check -v` exit **0** beforehand; `git apply` exit **0**. Six hunks: 3 main, 2 SI, 1
graph, 18 insertions / 18 deletions.

Resulting identities, and each is byte-identical to the capsule's `proposed/` copy (`cmp -s`):

| file | after | matches BINDINGS `proposed` |
|---|---|---|
| main | 55,373 B `997e822f8ac20964101cab29d818daa9ba4db72a7566f880e6749902922303a4` | yes |
| SI | 37,788 B `ba56996044b006b2214209700f30875cb84dd68daccc1e87c424a290e0545667` | yes |
| graph | 70,230 B `1697b5ffe738733b21d8675a9076f227c47698b6078260edc438de086f8bef88` | yes |

`APPLIED-DIFF.patch` (17,761 B, `8a8d553d937c8af7…`) is the ACTUAL diff the working tree carried
after application.

## Graph invariance, re-derived by the parent

`systems/graph/publications.json`: **416 leaves before, 416 after; 0 added, 0 removed, 1 changed,
and 0 of the changed leaves is non-string.** The list still holds **33 entries**. The file
round-trips byte-exactly at `indent=2` both before and after, so nothing was silently reformatted.
The single changed leaf is `[29]/what_it_would_claim` on `PUB-TCIP`, and the change is exactly
residual 1: "shared-stream covariance cannot be estimated from the held marginals and no
design-aware interval for the ABLATION ratio exists" becomes "empirical cross-arm covariance cannot
be estimated from the retained marginal counts; no ratio interval is reported for that ABLATION".
No unrelated entry moved.

## What the six replacements say, and what they do not

1. **Four current occurrences** (main 232–234, main 522–523, SI 75–76, graph field): the universal
   impossibility becomes the narrower recorded statement — the empirical cross-arm covariance cannot
   be estimated from the retained marginal counts, and **no ratio interval is reported**. Missing
   joint counts do **not** establish that every conservative interval or bound is unavailable. **No
   interval was calculated**, and the separate main-enumeration discussion is preserved.
2. **SI 105–110**: `1.20 = 24 × 0.05` is retained as the **nominal expectation conditional on an
   assumed 5 % per-comparison noncoverage**, together with the statement that this calibration is
   **not established**. It is no longer said that the actual noncoverage is not 5 % — the held
   records do not establish its value either way. The 19 inside / 5 outside counts, the at-most-two
   verdict rule and the `DISAGREES` status are unsoftened. **No calibration experiment was run.**
3. **Main 421**: "arbitrarily many residues" becomes "may involve more than twelve contributing
   residues", with the cutoff alone imposing **no twelve-residue upper bound**. The accepted
   necessary condition, the lack of equivalence and the exact-twelve range are intact.

## Checks, with real exit codes

Retained under `checks/`, one directory per attempt, each with `command.txt`, `stdout.txt`,
`stderr.txt`, `exit_code.txt`:

| check | result |
|---|---|
| `01-lint_claims-AFTER` | **exit 0**, `0 ERROR, 2 WARN across 2 file(s)` |
| `02-lint_style-report-AFTER` | **exit 0**, reporting `88 ERROR across 2 file(s)` |
| `03-lint_style-check-AFTER` | **exit 1**, `88 ERROR across 2 file(s)` |
| `04-json-parse-graph` | **exit 0**, `parsed OK, entries 33` |
| `00-lint_style-check-BEFORE-on-HEAD-bytes` | **exit 1**, `90 ERROR across 2 file(s)` |

⛔ **THE STYLE COUNT IS 88, NOT 90, AND THE PARENT WILL NOT REPORT IT AS 90.** The instruction was to
preserve the original 90-error enforcing exit 1 and report-only exit 0. The **failure** is preserved
exactly — enforcing still exits 1, report-only still exits 0, nothing was waived, excluded,
baselined or matched away, and `lint_style.py` was not touched. But the **count moved from 90 to
88**, and it moved because of these edits. The parent measured the before-state itself rather than
quoting the earlier record: temporarily restoring the two HEAD blobs into place and running the same
enforcing command reproduces `90 ERROR`, exit 1, identical to the run recorded in
`../TCIP-repair-2/checks/03-lint_style-check-AFTER/`; the patched bytes were then restored and
re-verified by sha256.

The two errors that disappeared are both `bold-midsentence`, in the SI at lines **75** and **107** —
that is, inside the two SI passages residuals 1 and 2 rewrote. The rewritten sentences no longer
carry mid-sentence bold. Rule-class tallies: `bold-midsentence` 73 → 71; `bold-density` 1,
`emdash-density` 1, `glyph` 4, `heading-style` 11 all unchanged. Every other difference in the two
outputs is a line-number shift from the main file losing one line. **The style failure is real, is
not waived by this disposition, and remains outstanding.**

## Dated correction to the repair-2 completion narration — 2026-09-09

My commit `86c1f4f6d`, "TCIP four P2 residues applied, and the parent-owned PUB-TCIP graph field
integrated", and the report I gave alongside it, presented the repair-2 batch as the settled end of
the TCIP residual work. **That was an overstatement.** Root's direct readback at
`301ea10f607696e1624500ad4cf9d405e203cf8e` found the narrowed toolchain-audit correction
*substantially* implemented, with three exact residuals still live across six occurrences: the
universal "no interval can be computed" statement at four current sites, the categorical "per-
comparison noncoverage is not 5 %" in the SI, and "arbitrarily many residues" in the main. Repair-2
was a real advance and its four P2 corrections stand; it was not completion. The original repair-2
reports, patches, run records and `CORRECTIONS.md` are preserved unedited as history — this is a
dated correction beside them, not a rewrite of them.

## Boundary

This is a finite text and JSON correction settled by bounded readback. It does **not** establish
publication readiness, whole-repository green gates, physical interface-floor calibration, or any
EMC efficacy, safety, selectivity or clinical claim. The stronger physical-floor claim stays parked
under its existing reopening requirements. Earlier failures remain historical failures, and the
enforcing style failure above remains open.
