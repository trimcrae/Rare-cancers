---
id: DOC-EMC-VACCINE-PATH-STOPPING-RULE
title: "Pre-registered stopping rule — the EMC fusion-junction vaccine preprint"
level: L3
kind: memo
status: live
canonical_for:
  - when the vaccine-path hardening cycle stops and the preprint may be posted
purpose: >
  Fix, before any review round's findings are known, the condition under which adversarial
  hardening of PUB-VACCINE-PATH stops and the manuscript may be posted. It exists so that the
  decision to stop is made against a rule rather than against a tally the results themselves
  suggested.
scope: >
  Process only. It makes no scientific claim about the manuscript's subject and states no result.
audience: [maintainers, external reviewers]
related: [DOC-EMC-VACCINE-DEVELOPMENT-PATH]
date: 2026-08-22
last_verified: 2026-08-22
---

# Pre-registered stopping rule — the EMC fusion-junction vaccine preprint

**Written 2026-08-22, at 08:13 ET, BEFORE round 1's seats returned.** That timing is the whole point.
A stopping rule composed after the findings are in is a justification wearing a rule's costume, and
this repository has the counter-example that makes the precaution non-theoretical: the ASO series'
round-7 pre-registered prediction — that no coverage gap remained — was falsified one round later,
when round 8 filed 24 blocker-grade charges against a document no seat had ever read.

Subject: [`emc-vaccine-development-path.md`](./emc-vaccine-development-path.md) (`PUB-VACCINE-PATH`),
aimed at a bioRxiv preprint. Round 1 is the first adversarial review this document has ever had.

## 1 · The rule

**Hardening stops when one round returns NO BLOCKERS AND NO P1s**, where that round's seats include
a regression lens reading the previous round's repairs.

Three riders, each of which has cost this repository a round before:

- **⛔ A zero-blocker round with live P1s in it is not converged.** It is a round whose repairs have
  not yet been reviewed.
- **⛔ A round whose findings are ALL damage from the previous round's repairs does not license
  another round.** It licenses tightening the edit discipline — replace-don't-append, re-derive
  every number in any proposed replacement, verify per edit — because another round against
  undisciplined edits converts repair damage into more repair damage.
- **⛔ A round in which a seat died does not count as a round.** Liveness is the last event's
  timestamp *and* type; a seat that died leaves a board indistinguishable from a seat that is
  thinking.

## 2 · What must additionally be true before posting, independent of the round count

These are gates, not findings, so no round can retire them by not mentioning them.

1. **Every figure the manuscript prints is bound by a guard to the artifact that produces it**, and
   that guard has been mutation-tested including single-site mutations — a figure stated at three
   sites and corrupted at one must fail.
2. **Every reference identifier is corroborated in-repo or by a `verify-refs` run**, not written from
   recollection. No entry may remain under a "requiring verification before submission" heading at
   the moment of posting: either it is verified, or the claim it supports comes out.
3. **The author block carries a real name, affiliation statement and ORCID** — no placeholder.
4. **`PREFLIGHT_FULL=1 ./scripts/preflight.sh` passes**, exit code unmasked.
5. **The manuscript's main text has not grown across the hardening series.** Measured at the round-1
   pin and at the final pin, against `987c50f2`'s 7,154 words.

## 3 · The prediction this rule commits to, so it can be falsified

Registered before round 1's findings were read, in the same spirit as the ASO series' falsified
round-7 prediction:

> **Prediction.** Round 1 will file at least one BLOCKER, and the highest-yield seat will be the
> instrument-coverage lens rather than any prose lens — because this document has never been
> reviewed, and because the repository's own recurring defect is an instrument bound to one document
> while reporting on both.

The outcome is recorded in the round-1 ledger whether it holds or fails.
