# Actual child model fields and activity evidence — read once from the real transcripts

**2026-09-08 ~20:58 UTC, parent. ⛔ No poller, no waiting model, no auditor. One read of each real
child transcript.**

Root asked that the **requested** Opus 5 / Medium be distinguishable from the **actual runtime model**.
These are the `model` fields as written by the runtime into each child's own transcript, not the
values I passed at dispatch:

| owner | actual `model` | transcript lines | bytes | last write |
|---|---|---:|---:|---|
| MF1 repair (F01–F12) | **`claude-opus-5`** | 168 | 497,346 | 20:57:08 |
| C2 arm confirmation *(highest priority)* | **`claude-opus-5`** | 49 | 197,696 | 20:58:35 |
| A2 denominator flags | **`claude-opus-5`** | 84 | 240,349 | 20:58:48 |
| B2 identity overclaim | **`claude-opus-5`** | 90 | 252,675 | 20:58:40 |
| P-AB2 unicode offsets | **`claude-opus-5`** | 37 | 103,649 | 20:58:49 |
| FO PDF production | **`claude-opus-5`** | 17 | 59,971 | 20:58:50 |

**All six report `claude-opus-5`, matching what was requested.** ⚠ The transcript records the model
id; the **effort** setting is not written into these records, so I can confirm the model from evidence
but **cannot** confirm "Medium" from this source — stating that rather than implying a check I did not
make.

**Activity is real, not queued.** Every one has a growing transcript with a recent write timestamp;
the MF1 owner is furthest along at 168 lines and ~497 KB. ⛔ None of these is a dispatch receipt — a
queued message would leave no transcript.

## Capsule intake recorded with this
The **P-AB2 evidence capsule** was fetched from `codex/opus-cloud-inputs-20260908` at commit
`b9f296433258a28bed8c1f32be3e3be2ab685401` and verified before extraction: ZIP 2,723 B
`870fca8e…`, manifest 892 B `8454155d…`, **3 members, CRC all OK, no unsafe paths**. Both evidence
files match their stated identities exactly — `unicode-comment-counterexample.json` 989 B
`bb0fd14f…` and `retained-two-helper-functions.py` 2,729 B `d9e398f9…`. Extracted read-only with raw
byte writes (no newline translation) and `chmod a-w`.

⚠ **One precise measurement correction, offered as accuracy rather than disagreement.** The capsule
was described as containing unusual **CR CR LF**. The bytes as delivered contain **CRLF only** — 10
in the JSON and 56 in the Python file, with **zero CR-CR sequences** — alongside non-ASCII content
(272 and 15 bytes). Since both sha256 values match exactly, these **are** the originals; only the
description of the ending style differs. ⛔ The operative instruction is unaffected and was followed:
**nothing was restamped or normalised**, which matters especially here because the counterexample
turns on byte-versus-character offsets.
