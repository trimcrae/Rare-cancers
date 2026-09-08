# MF1 final-review capsule — intake record

**2026-09-08, parent. Delivery of already-created authorized review artifacts through the
established route. ⛔ Not a new scientific source fetch.**

## Verification, all performed before extraction

| item | expected | measured | |
|---|---|---|---|
| input commit | `3b278d85c7cf5960921a9c6d34946b3d6ead87b6` | resolves, type `commit` | ✅ |
| ZIP bytes / sha256 | 59,200 · `9de316b61c912585c7c83771379330f37568a50f227dcf9761b11c8433f74a92` | identical | ✅ |
| manifest bytes / sha256 | 2,834 · `f2fbd8371db9d8fbcf130c04bd6291bf58fa5d256fc481f6f7dff3d40e7a3140` | identical | ✅ |
| final report sha256 | `f4a0aceec8fdea6a1da62de2dc36ef88637c6288c05f1cc7fc318b3c971b32be` | identical | ✅ |
| root memo sha256 | `071fcfc9afd0b99a87b8ad9d8ca260769431d6b222ca60662efb196bf9164365` | identical | ✅ |
| ZIP members | 15 | 15, **CRC all OK**, **zero unsafe paths** (no absolute, no `..`) | ✅ |

Fetched with the normal `git fetch origin codex/opus-cloud-inputs-20260908`; blobs read from the
pinned commit. **No primary checkout or index change was made**, and no worker file was overwritten.

## Extraction
Extracted to a **task-scoped, read-only** directory outside the repository:
`…/scratchpad/mf1-capsule/extracted/` — 15 files, `chmod a-w` applied after extraction.

The 15 members: the complete final report (38,953 B), root's adjudication (6,673 B), the reviewed-input
manifest in JSON and Markdown, the review output manifest, the transfer manifest, the collection log,
four collection/finalisation scripts, and the reviewer's original calculation artifacts —
`reviewer_calculations.py`, `reviewer-calculations.json`, its stdout and its exit file.

⛔ **`reviewer_calculations.py` was NOT rerun and must not be.** Those originals are review evidence,
and they contain **illustrative quantities explicitly excluded as replacement empirical results**.

## Owner launched
One Opus 5 / Medium MF1 repair owner was dispatched immediately on verification, ahead of any parent
housekeeping. It owns the MF1 main, the necessary supplement/provenance inventory and dated
corrective interpretations; **the parent retains integration and all shared roadmap and graph files**,
and receives small current-summary corrections as exact patches.

It was given the read-only capsule path and instructed to read the **actual report and adjudication**
rather than any dispatch summary.

## Status carried
Root accepts **F01–F12**: **MAJOR SCIENTIFIC REVISION**, with enough existing evidence for a useful
narrower retrospective audit. ⛔ The paper is **not** parked, **no replacement baseline review** is
launched, and **no publication gate is cleared**. Source-specific stronger claims stay held unless
their exact retained evidence is identified, and are omitted when unsupported.

⚠ FP, P-ST, TD1 and TCIP remain frozen. Only this MF1 batch is released for repair.
