---
id: DOC-OPUS-CAMPAIGN-RECEIPT-ENDPOINT-ORIGINALS
title: "Intake receipt — endpoint final-review original inputs"
level: L4
kind: memo
status: live
purpose: >
  Record the verified intake of the completed endpoint adverse-review original packet from the small
  input route, with hashes measured here rather than accepted as relayed.
scope: >
  L4. An intake receipt. It runs no reviewer script, re-executes nothing, and reopens no held paper.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Intake receipt — endpoint final-review originals

## Route and pin

- **Input branch:** `codex/opus-cloud-inputs-20260908`, **exact commit
  `13b3945f0d3410e4e0f52a0315e55e0ee39a1327`** ("Transport unchanged endpoint final-review originals").
- **Fast-forward claim, checked here:** `git merge-base --is-ancestor 89304acb… 13b3945f…` returns
  true — `13b3945f` is a descendant of `89304acbcb4dd8986c845b0d581173ca3e8ebf65`.
- ⛔ **The input branch was NOT merged.** Exactly two blobs were extracted from the pinned commit by
  `git show <commit>:<path>`; local `HEAD` and the index are otherwise untouched.

## What was retained, and where

Under existing campaign evidence ownership, in `…/opus-capacity-campaign-20260908/collected/`:

| file | bytes | sha256 measured here |
|---|---|---|
| `endpoint-final-ultra-original-inputs.zip` | 261,273 | `4f62618d46bc9f886da27d59ccf3d50beb825c779b1d36e305238a5d318f8da7` |
| `endpoint-final-ultra-original-inputs-manifest.json` | 7,288 | `d51d01b58c5112292ad5ca03ceca10f0106ab6f63305f10fb3fd82e165ee64a4` |

⭐ **Both match the sent values exactly.**

## Member verification, measured

- **40 ZIP members.** **39 enumerated original source files**, summing to **567,267 bytes** — the
  sent figure, recomputed from the members themselves — plus **`TRANSFER-MANIFEST.json`**, which is
  the separately identified NEW transfer metadata and is not one of the 39.
- **Zero hash mismatches**, checked twice and independently: every one of the 39 against the internal
  `TRANSFER-MANIFEST.json` (`original_files`), and all 40 against the adjacent external manifest's
  `members`. Byte counts agree wherever the manifest states one.
- **`FINAL-SCIENTIFIC-REVIEW.md` is present**, **29,795 bytes**, sha256
  `abb9588b07091ba4b30753e4e00eb9f1e78327613acc952ace89d935b507d806` — the sent value.
- The archive carries the reviewer's scripts, results JSONs, three figure renders with their render
  logs and receipts, the additional frozen inputs, and the frozen dependency copies.

## Transfer metadata, as the packet records it

`TRANSFER-MANIFEST.json` states: `verified_revision` `9c6f4a80fc2fd69ee71ad6124c8de03e6e1af395`;
review agent `/root/endpoint_final_ultra`; model **`gpt-6-astra`**, reasoning effort `ultra`;
`scientific_code_executed_by_transporter: false`; `review_script_reexecuted: false`; exclusions
limited to the edge/browser profile and cache, with no process kill, cleanup or re-execution.

⚠ **That is the transporter's own recorded metadata, quoted, not something verified here.** No
reviewer transcript accompanies this packet, so the served model behind the review is not
independently confirmed by me — unlike this campaign's Claude children, whose models are verified
from their own JSONL.

⚠ The sender's local transfer receipt `observations/endpoint-final-review-original-cloud-transfer.json`
(24,497 B, sha `46bec91050f4…`) is **not present in the pinned commit** — checked. Its identity is
recorded here as relayed and is **not** verified locally.

## What was deliberately not done

- ⛔ No reviewer script run, no result recreated, no figure re-rendered, no producer chain.
- ⛔ No ClinicalTrials.gov fetch and no duplicate cache lookup. The raw-cache availability lookup is
  **CLOSED**: remote `216bd1b5…` holds 12 payloads totalling 157,268,733 B, and one cached payload
  retains group/class/category/measurement/denominator fields. ⚠ **That is availability only** — it
  is **not** validation, and it does **not** reopen the method.
- ⛔ The original **21** frozen endpoint science inputs are untouched and stay frozen. This packet is
  a **separate** set of reviewer-side originals; it neither replaces nor amends them.

## Disposition

Root **ACCEPTS** the completed major-scientific-revision verdict. **F1–F10 and the exact
paper-specific reopening condition stand as recorded** in
[`HOLD-endpoint-extraction-validity.md`](HOLD-endpoint-extraction-validity.md); nothing in this
intake changes them, and this receipt is evidence retention only. Under the campaign retention rule
this directory stays intact until a directory-specific collector receipt verifies it.
