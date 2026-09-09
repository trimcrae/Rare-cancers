---
id: DOC-OPUS-CAMPAIGN-TCIP-REPAIR-2-IDENTITIES
title: "TCIP residual repair — before/after identities and artifact hashes"
level: L4
kind: record
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Identities

SHA256 of the actual local bytes, measured in `/home/user/Rare-cancers`, branch
`claude/confident-bardeen-ji76cd`.

## Files changed by this lane

| file | bytes before | SHA256 before | bytes after | SHA256 after |
|---|---:|---|---:|---|
| `research/manuscripts/tcip/tcip-induced-interface-preprint.md` | 51,625 | `d211e11afe565a734282d3830e5223efaf79590add7de36769eb2eac361f0e20` | 55,272 | `f4954098c1aed4cd9521b82b81be07f78c715aec24cea51bb9eecb671408cbcc` |
| `research/manuscripts/tcip/tcip-induced-interface-preprint-si.md` | 35,997 | `72d21e7f4893f3a9103400a64d05304236707aa2e8f27d2057348ea03de2a19e` | 37,757 | `b7d97906c3d7aa15ff8a457ac6f3ad3a4b4e2035973565f74fae951fb8898c9b` |

The "before" columns are the **exact focused-review freeze** named in the root memo, and both files
carried those bytes when this lane began. They are retained verbatim here as
`BEFORE-tcip-induced-interface-preprint.md` and `BEFORE-tcip-induced-interface-preprint-si.md`, whose
hashes equal the before column.

## File NOT changed by this lane

| file | bytes now | SHA256 now | disposition |
|---|---:|---|---|
| `systems/graph/publications.json` | 68,790 | `8dc9b0b9894679277e94d3e283459e9fae63d13b845460bf177a1997db0e1418` | parent-owned; unapplied patch under `patches/`. Applying it gives 70,224 B / `800e844ff1e6b8127c5d4d6811438e820f8c66c4efe11269e1c083d751d1902d`. |
| `research/manuscripts/tcip/tcip-interface-floor-sizing.md` | 22,802 | `241d4295f3edc4ad0288f4d0fcc43bbbe132e137349ad1c3930d19e7c3e454a9` | separately accepted sizing-memo correction; not repeated, not touched. |

## Artifacts produced by this lane

| artifact | bytes | SHA256 |
|---|---:|---|
| `DIFFS/tcip-induced-interface-preprint.md.diff` | 9,598 | `e9f384c168893d455ee5888ebada8c20c2685b6acb842dc7adadd4b666b9831b` |
| `DIFFS/tcip-induced-interface-preprint-si.md.diff` | 7,614 | `8e587fcd995ba51b451a317d9a40ec333d27ed3ccad32c08b7dff2d55bae4747` |
| `patches/0001-PUB-TCIP-retire-modality-general-opening.patch` | 9,397 | `cbd519756e267a65cffdd2280acf56d55c2b83d8e41e9f123144c41440db94a9` |
| `patches/PUB-TCIP-what_it_would_claim-NEW.txt` | 5,241 | `e6f2f99d87fb44893c15bae9eb380fbf65bc88106de31f7b51ce1336d27f7234` |

## Inputs read for this batch

| document | bytes | SHA256 | how read |
|---|---:|---|---|
| root memo `TCIP-focused-residual-root-adjudication-20260908.md` | 6,201 | `e79e2ce888866a24f6c831332ded0cc2485f78354f7e1eb7f6e5bb818fce4f43` | in full |
| returned batch `../TCIP-repair/IDENTITIES.md`, `RESIDUAL-LIMITATIONS.md`, `CHECK-RUN-RECORD.txt` | — | — | in full |
| `research/modalities/nr4a3_tcip_reach.py` → `crosscheck_replicates_committed_acceptance` | — | — | the verdict rule `max(1, ceil(0.05·n))` read directly, not recomputed |
| `research/modalities/nr4a3-tcip-reach.json` → `cross_checks.replicates_the_committed_E3_acceptance` | — | — | status, 24 cells, 5 outside, 1.2 expected — read, not re-run |

The 137-file focused-verification original set and the pinned capsule were **not** re-fetched or
re-hashed: the parent verified them before dispatch and instructed against it.
