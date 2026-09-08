---
id: DOC-OPUS-CAMPAIGN-CHILD-MODEL-FIELD-RECORD
title: "Child-model field record — actual worker metadata, 2026-09-08"
level: L4
kind: intake-record
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Child-model field record — actual worker metadata

Compact intake record for the campaign's model children. **Only actual model, start and tool
metadata, and exact recorded locators.** No private chain of thought is recorded, quoted or
summarised anywhere here.

## ⚠ What a "Medium effort" session does and does not prove

This cloud session is configured `claude-opus-5` and the campaign was commissioned at medium
effort. **That is a session-level and request-level fact.** The dispatch API accepts a `model`
selector (`opus`) but exposes **no per-child effort field**, and no child returns one. So:

> **Session/request "Opus 5 / Medium" is NOT evidence of an independently encoded per-child effort
> field.** Where this record says a child's effort, it is naming the session and request setting it
> inherited, not a value read back from the worker.

## ⚠ Where runtime and tool counts come from

Runtime and tool counts below are taken **only from the completion record each worker actually
returned** — its measured `duration_ms`, `tool_uses` and `subagent_tokens`. **They are never taken
from the launch request.** A worker still running has **no** runtime or tool count here, and the
cell says so rather than estimating one.

## The rows

| child | model selector | dispatch | status | runtime (measured) | tool uses (measured) | tokens (measured) |
|---|---|---|---|---|---|---|
| **TD1 author repair F1–F11** | `opus` | background agent, this session | **completed** | **1,631,150 ms** (≈27 min 11 s) | **97** | **290,807** |
| **C2 corrected-component owner** | `opus` | background agent, this session | **completed** (integrated at `8f1fe1c5e`) | **not retained** — see below | **not retained** | **not retained** |
| **TCIP F01–F13 author repair** | `opus` | background agent, this session, launched 2026-09-08 after capsule verification | **running at time of writing** | not yet measurable | not yet measurable | not yet measurable |
| **FP R1–R9 residual author** | `opus` | background agent, this session, launched 2026-09-08 after capsule verification | **running at time of writing** | not yet measurable | not yet measurable | not yet measurable |
| **P-ST R1–R8 residual author** | `opus` | background agent, this session, launched 2026-09-08 after capsule verification | **running at time of writing** | not yet measurable | not yet measurable | not yet measurable |

**C2's usage figures are an honest gap, not a zero.** Its completion record passed out of this
session's live context before this record was opened, and I will not reconstruct numbers from the
launch request or from memory. What *is* retained and checkable is its work product and its real
exit codes: `C2-correction/CHECKS-RUNS/RUN-01…RUN-07`, including the preserved failure `RUN-02`
(EXIT=1), and `C2-correction/SHA256-v3-artifacts.txt`.

## Exact recorded locators

| child | contract | artifacts | execution records |
|---|---|---|---|
| TD1 | root memo, transported in-session | `TD1-repair/` (`FINDING-MAP.md`, `INVARIANCE-EVIDENCE.json`, `patches/`, `frozen/`) | `TD1-repair/checks/README.md` — 24 attempts with real exits, including two failed builds and one that exited 0 but was found unsound |
| C2 | `CONTRACT-CORRECTED-C-arm-attribution-v2.md` and root's five-item correction | `C2-correction/` | `C2-correction/CHECKS-RUNS/` (RUN-01…RUN-07; RUN-02 EXIT=1 preserved) |
| TCIP | `TCIP-repair/CONTRACT-TCIP-F01-F13-author-repair.md` | `TCIP-repair/` | `TCIP-repair/checks/` (to be written by the worker) |
| FP | `FP-residual/CONTRACT-FP-R1-R9-residual-author.md` | `FP-residual/` | `FP-residual/checks/` (to be written by the worker) |
| P-ST | `PST-residual/CONTRACT-PST-R1-R8-residual-author.md` | `PST-residual/` | `PST-residual/checks/` (to be written by the worker) |

## Capsule verification performed by the parent before each dispatch

| capsule | pin | members | verification |
|---|---|---|---|
| TCIP `tcip-final-ultra-original-inputs.zip` | `1db3435c52e0d15f340e3060b66d990be5505de6` | 54 | 54/54 CRC-clean and byte-exact against the manifest; 0 unsafe paths; archive 1,136,213 B sha256 `05802bcb…d9304efb`; manifest 11,606 B sha256 `95b16ec7…f80d066d`; root memo 5,859 B `131a610d…`; report 52,425 B `a00bec72…`; addendum 19,411 B `7d2941db…` |
| FP `fp-focused-residual-original-inputs.zip` | `36460a48453db79bf1bc724a6fcf3e7bbd334cf6` | 64 | 64/64 CRC-clean and byte-exact against the manifest; 0 unsafe paths; archive 674,305 B sha256 `1149a609…a457f1f`; manifest 14,195 B sha256 `7419d411…fa855879`; root memo 6,530 B `e33350d9…`; report 44,287 B `834dad86…` |
| P-ST `pst-focused-residual-original-inputs.zip` | `92a3ba93c19ab8e4d4c54e87372b49d1f6c67469` | 44 | 44/44 CRC-clean and byte-exact against the manifest; 0 unsafe paths; archive 361,616 B sha256 `8b99fef7…b7300174`; manifest 9,769 B sha256 `4e58e924…ef814de5`; root memo 5,711 B `d6b16725…`; report 35,567 B `afd48dc5…` |

Both were read from the git object store at their pinned commits with `GIT_NO_LAZY_FETCH=1`, so a
locally absent object would have failed loudly rather than being fetched silently.

## Honest count of working model children

At the time of writing: **3 running model workers** (TCIP author, FP residual author, P-ST residual
author) and **1 integrating parent**. TD1 and C2 have returned. That is the actual count. Dispatch receipts,
queued messages and this record itself are **not** workers and are not counted.
