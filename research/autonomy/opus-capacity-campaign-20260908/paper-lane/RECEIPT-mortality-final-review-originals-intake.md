---
id: DOC-OPUS-CAMPAIGN-RECEIPT-MORTALITY-ORIGINALS
title: "Intake receipt — mortality final-review original inputs"
level: L4
kind: memo
status: live
purpose: >
  Record the verified intake of the completed mortality adverse-review original packet, with hashes
  measured here rather than accepted as relayed.
scope: >
  L4. An intake receipt. It runs no reviewer script, recreates no output, and reopens no held paper.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Intake receipt — mortality final-review originals

## Route and pin

- **Input branch:** `codex/opus-cloud-inputs-20260908`, **exact commit
  `01c6c710385cb5e13312bff0af3c4546c041fa52`** ("Transport unchanged mortality final-review originals").
- **Fast-forward claim, checked here:** `0dda2e6be7903a012d3e4a620738acc0c76e4050` is an ancestor of
  `01c6c710…`.
- ⛔ **The input branch was NOT merged.** Exactly two blobs were extracted with
  `git show <commit>:<path>`; local `HEAD` is otherwise untouched.

## What was retained, and where

Under existing campaign evidence ownership, in `…/opus-capacity-campaign-20260908/collected/`:

| file | bytes | sha256 measured here |
|---|---|---|
| `mortality-final-ultra-original-inputs.zip` | 441,350 | `97b8d692ec08973c50760d592a95ba97be20bc63c5b72ca6e09de5a80176cc8a` |
| `mortality-final-ultra-original-inputs-manifest.json` | 3,439 | `c89fd0db63b746d860806586b4f92c0994a5a2e68180d990d39fb0a77f74e410` |

⭐ **Both match the sent values exactly.**

## Member verification, measured once

- **19 ZIP members.** **18 enumerated originals** summing to **1,700,170 bytes** — the sent figure,
  recomputed from the members themselves — comprising the **16 reviewer top-level originals** plus
  **`root-adjudication.md`** (8,105 B) and **`root-counterexample.json`** (576 B), plus the clearly
  identified NEW `TRANSFER-MANIFEST.json`, which is not one of the 18.
- **`testzip()` returns clean: every member's CRC is intact.**
- **Zero hash mismatches**, checked against the internal `TRANSFER-MANIFEST.json` (18/18) and,
  independently, the adjacent external manifest (19/19).
- **`review/FINAL-SCIENTIFIC-REVIEW.md` is present**, **38,388 bytes**, sha256
  `16b6974acdbe71318ca01f03fe8bc8d7adc7f6f9749670ef16e0b6abe1681a58` — the sent value, and the digest
  root verified.
- Contents also include the independent-check scripts and results, the input and dependency
  manifests, the 1,080,360-byte source inventory, the 469,972-byte structure summary, the
  title-eligible retained sentences, the primary survival evidence and the completion/integrity record.
- ⛔ **Excluded per root, and correctly absent:** the **26 already Git-bound reviewed input copies**.
  No source copy needs re-transport and none was duplicated.

## The counterexample, recomputed here

`root-counterexample.json` is **analytical evidence, not patient data and not an EMC estimate**, and
its own `kind` field says so. Recomputed independently by the parent from its stated parameters: two
independent constant hazards of **0.1 per year** over **5 years** give observed survival
**0.36787944117144233**, expected survival and relative survival **0.6065306597126334**, so
`(RS − OS)/(1 − OS)` = **0.3775406687981454** while the true competing-death share is **0.5** by
symmetry. ⭐ **That reproduces the packet's `manuscript_share` to the last digit**, and it is the
arithmetic behind F3.

## Transfer metadata, as the packet records it

`reviewed_revision` `e21841ea103560d801f4e21f64ee31a68028e232`; review agent
`/root/mortality_final_ultra`; `model_reported_by_coordinator` **`gpt-6-astra`**,
`reasoning_effort_reported_by_coordinator` `ultra`,
`fork_turns_explicitly_requested_by_coordinator` `none`;
`scientific_code_executed_by_transporter: false`; `review_script_reexecuted: false`.

⭐ The manifest states it plainly and correctly: **`transporter_independently_verified_served_model:
false`**. The review's model and its ultra execution are **root-owned**, and this transfer confirms
neither. ⛔ **No backend attestation is invented here.**

⚠ The sole collector's local receipt
`observations/mortality-final-review-original-cloud-transfer.json` (11,576 B, sha
`8366c6c62326d341…3a01d`) is **local only** and is **not** present in the input commit. It is
recorded as relayed and is **not** verified here.

## What was deliberately not done

- ⛔ No reviewer or producer script run, no output recreated, no receipt reconstructed, no cleanup.
- ⛔ No source hunt, no replacement denominator, no rewrite.
- ⛔ The mortality science stays **frozen** at `e21841ea` under the accepted hold. This intake is
  evidence retention only.

## Disposition

F1–F10 and the exact reopening conditions are recorded in
[`HOLD-mortality-causal-ceiling.md`](HOLD-mortality-causal-ceiling.md), written from the retained
`root-adjudication.md` read here rather than from a summary. Under the campaign retention rule this
directory stays intact until a directory-specific collector receipt verifies it; the HLA and
fusion-partner originals from the current batch stay in place for the sole collector and are neither
retired nor recreated.
