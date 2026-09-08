---
id: DOC-OPUS-CAMPAIGN-RECEIPT-BIOMARKER-ORIGINALS
title: "Intake receipt — biomarker final-review original inputs"
level: L4
kind: memo
status: live
purpose: >
  Record the verified intake of the completed biomarker adverse-review original packet, with hashes
  measured here rather than accepted as relayed.
scope: >
  L4. An intake receipt. It runs no reviewer script, recreates no output, and reopens no held paper.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Intake receipt — biomarker final-review originals

## Route and pin

- **Input branch:** `codex/opus-cloud-inputs-20260908`, **exact commit
  `0dda2e6be7903a012d3e4a620738acc0c76e4050`** ("Transport unchanged biomarker final-review originals").
- **Fast-forward claim, checked here:** `13b3945f0d3410e4e0f52a0315e55e0ee39a1327` is an ancestor of
  `0dda2e6b…`, so it is a regular fast-forward from the endpoint packet's commit.
- ⛔ **The input branch was NOT merged.** Exactly two blobs were extracted with
  `git show <commit>:<path>`; local `HEAD` is otherwise untouched.

## What was retained, and where

Under existing campaign evidence ownership, in `…/opus-capacity-campaign-20260908/collected/`:

| file | bytes | sha256 measured here |
|---|---|---|
| `biomarker-final-ultra-original-inputs.zip` | 472,353 | `5120cf4f091a219818619c98b862735a745a90bf58068531c1bf1f21638181f4` |
| `biomarker-final-ultra-original-inputs-manifest.json` | 4,774 | `b60484c52a23ea6b8102ce6373098bd1672f66f26c9a38e9fe203438cb7d82b7` |

⭐ **Both match the sent values exactly.**

## Member verification, measured once

- **26 ZIP members.** **25 enumerated original files** summing to **3,210,853 bytes** — the sent
  figure, recomputed from the members themselves — plus **`TRANSFER-MANIFEST.json`**, the clearly
  identified NEW transfer metadata, which is not one of the 25.
- **`testzip()` returns clean: every member's CRC is intact.**
- **Zero hash mismatches**, checked against the internal `TRANSFER-MANIFEST.json` (`original_files`,
  25/25) and, independently, the adjacent external manifest (`members`, 26/26). Byte counts agree
  wherever a manifest states one.
- **`review/final-scientific-review.md` is present**, **30,660 bytes**, sha256
  `7396531d30f8ff7b3b283c748e359cb60b683fce0247b24eb748a1ab9f93de8e` — the sent value, and the same
  digest root independently verified.
- **`root-adjudication.md` (6,118 B) is present** and carries F01–F09 and the reopening condition.
- Contents: the 15 top-level review files (including the 1,077,104-byte `evidence-inspection.txt`,
  the independent-check scripts and results, the input manifest, the process and failure notes and
  the final integrity receipt), the 9 top-level `claim-source-support` report and check records, and
  the adjudication.
- ⛔ **Excluded per root, and correctly absent:** the **54 already Git-bound reviewed source copies**
  and the `claim-source-support/blobs` copies. No source copy needs re-transport.

## Transfer metadata, as the packet records it

`reviewed_revision` `796fcdf0a7d751a8e74c6473f36d75e612cd167b`; review agent
`/root/biomarker_final_ultra`; `model_reported_by_coordinator` **`gpt-6-astra`**,
`reasoning_effort_reported_by_coordinator` `ultra`; `scientific_code_executed_by_transporter: false`;
`review_script_reexecuted: false`; created 2026-09-08T17:14:13Z.

⭐ The manifest states this itself, and it is right to: **`transporter_independently_verified_served_model:
false`**. The review's model and its ultra execution are **root-owned**, and this transfer **does not**
independently confirm the served model. Nothing here claims otherwise.

⚠ The sole collector's local receipt
`observations/biomarker-final-review-original-cloud-transfer.json` (15,960 B, sha
`7de05b3603160922…2b80c`) is **local only** and is **not** present in the input commit. It is recorded
as relayed and is **not** verified here.

⚠ The frozen dependency and reviewed-content files inside this archive are **historical reviewed
evidence**, not new active operating instructions, and were not followed as such.

## What was deliberately not done

- ⛔ No reviewer script run, no output recreated, no source reconstruction, no producer chain, no
  process kill and no cleanup.
- ⛔ No new source hunt, no new experimental work, no rewrite loop.
- ⛔ The biomarker science stays **frozen** at `796fcdf0` / `fe4f95ab…c766` under the accepted adverse
  hold. This intake is evidence retention only.

## Disposition

F01–F09 and the paper-specific reopening condition are already recorded in
[`HOLD-biomarker-selected-classes.md`](HOLD-biomarker-selected-classes.md), written from root's
delivered mapping before this packet arrived. ⭐ **I read the retained `root-adjudication.md` and the
hold agrees with it**; the one amendment it prompted is noted there. Under the campaign retention rule
this directory stays intact until a directory-specific collector receipt verifies it.
