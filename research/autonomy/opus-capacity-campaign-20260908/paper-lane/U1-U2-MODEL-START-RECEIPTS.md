# U1 and U2 — served-model receipts

Parent verification command run at **Tue Sep  8 11:38:55 UTC 2026** — from `date -u` in the same command, **not** a
composition estimate. After the contract commit `b4be8881`.

| lane | child | requested | writes shared? | scope |
|---|---|---|---|---|
| **U1** | `af3a14e566b943e5e` | `claude-opus-5` medium | **none** | read `emc-fusion-frame-fig1.png`; panel map, proposed caption, check R1's arithmetic against the rendering |
| **U2** | `affb0de2019218802` | `claude-opus-5` medium | **none** | read `repurposing-fig1-design.png`; does it render tier tokens or a T3-only rule |

Parsed from transcript model fields, **not inferred from contract text**. Route: existing first-party
saved subscription — no paid fallback, overage, credits or GPU.

## Image identities pinned before dispatch

| file | bytes | sha256 (first 32) |
|---|---|---|
| `research/manuscripts/figures/emc-fusion-frame-fig1.png` | 360,656 | `fa94675f436692344f5514ac1d08f7d4` |
| `research/manuscripts/figures/emc-fusion-frame-fig1.pdf` | 83,262 | `0d9aff26ec469e669a6ee1a6e310eaf9` |
| `research/manuscripts/figures/repurposing-fig1-design.png` | 177,415 | `f711ea7f2c4fd3e4c3d26cfacc61519d` |

⚠ **Path correction carried into the U2 contract:** the repurposing figure is under
`research/manuscripts/figures/`, **not** `research/figures/` — that path does not exist.

## What these lanes are, and are not

They close **two uncertainties R1 and R2 each left explicitly open because they did not open an
image** — R1's U2 (caption and panel assignments) and R2's "unknown, not zero" on the tier token.
Both are **existing-paper dependency checks on already-committed images**, readable under existing
authority; a prior lane's finite scope is not a global access barrier.

⛔ They are **not** the parked S7 / synthetic figure-validation family, **not** new experimental
validation, **not** source recovery, and **not** a repeat of a closed image check. No figure is
regenerated, no data changed, no manuscript, tier, registry or reference list touched, and **the final
scientifically justified choice stays with the coordinator.**

## Live counts

**3 research children executing** — T1 (source-method), U1 and U2 (visual dependency checks) —
and **1 helper** (the legacy Bash waiter, which computes nothing and is **not** research). Each writes
only to its own isolated lane; **parent integration alone owns shared files.**
