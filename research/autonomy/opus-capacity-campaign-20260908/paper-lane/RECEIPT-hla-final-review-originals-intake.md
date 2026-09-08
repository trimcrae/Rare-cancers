---
id: DOC-OPUS-CAMPAIGN-RECEIPT-HLA-ORIGINALS
title: "Intake receipt — HLA final-review original inputs"
level: L4
kind: memo
status: live
purpose: >
  Record the verified intake of the completed HLA adverse-review original packet, with hashes
  measured here.
scope: >
  L4. An intake receipt. It runs no reviewer script, regenerates nothing, and reopens no held paper.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# Intake receipt — HLA final-review originals

- **Input branch:** `codex/opus-cloud-inputs-20260908`, exact commit
  `d6865129f98d45f4e6205661506daa092024a4e1`; **checked here** to be a descendant of
  `01c6c710385cb5e13312bff0af3c4546c041fa52`.
- ⛔ **Not merged.** Two blobs extracted with `git show <commit>:<path>`; local `HEAD` otherwise
  untouched.

| file | bytes | sha256 measured here |
|---|---:|---|
| `hla-final-ultra-original-inputs.zip` | 65,667 | `5c911f17fc07273c852fb6832230aefc5971c931971f65deac566b4c65087656` |
| `hla-final-ultra-original-inputs-manifest.json` | 3,456 | `6e6ff971fa0c31f7ef13d520a78beceee7eb7824d8c174e796741061d27a070b` |

⭐ **Both match the sent values exactly.**

**Members, verified once.** CRC clean on every member. **19 ZIP members = 18 originals summing to
242,160 bytes** — the sent figure, recomputed from the members — comprising the 16 reviewer top-level
originals plus `received/delta-intake-receipt.json` and `root-adjudication.md`, plus the NEW
`TRANSFER-MANIFEST.json`. **Zero hash mismatches** against the internal manifest (18/18) and,
independently, the external one (19/19). `root-adjudication.md` and the delta intake receipt are both
present.

**Transfer metadata as recorded:** `reviewed_revision` `6cd29f876b11492e01f4e2ea10752e1bf0dbc4f4`,
model reported by the coordinator `gpt-6-astra`. ⭐ The manifest states
`transporter_independently_verified_served_model: false`, and this receipt repeats it: the review's
model and its ultra execution are root-owned and this transfer confirms neither. ⛔ **The 33 already
Git-bound input copies are excluded and were not duplicated.** Both the original failed harness and
results and the corrected 122-pass run's originals are retained as shipped; ⛔ **no first-run stdout
was reconstructed**, no reviewer script re-executed, and nothing regenerated.

**Disposition.** The complete root hold and its exact reopening conditions are already recorded in
[`HOLD-hla-population-coverage.md`](HOLD-hla-population-coverage.md). ⛔ No HLA scientific worker,
figure rebuild, prediction or source fetch follows from this intake; the manuscript stays frozen at
`6cd29f87`.
