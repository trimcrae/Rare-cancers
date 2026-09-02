---
id: DOC-ROUND34-PREPIN-SEAT
title: "One blind seat that reviewed the right bytes at the wrong commit — held outside the directory the publish bar globs"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
scope: >
  Round 34 of PUB-ASO only, and only the one seat that ran before the round's pin was settled.
  It says nothing about any other paper, any other round, or whether round 34 converged.
last_verified: 2026-09-02
purpose: >
  Say why a completed blind-seat record is committed here rather than in
  research/autonomy/review-seats/, which is what clause 1 of the publish bar reads. The seat is
  honest, its findings re-derive, and it reviewed a commit that is not the one being posted. Filing
  it where the bar counts it would turn a review of a different tree into a review of this one.
---

# One blind seat, the right bytes, the wrong commit

⛔⛔ **THIS RECORD IS NOT CLAUSE-1 OR CLAUSE-6 EVIDENCE, AND FILING IT AS SUCH WOULD BE A FALSE
RECORD.** `publish_bar.clause_1_hardening_converged` and `clause_6_independent_adversarial_seat`
both compare `record['reviewed_commit']` against the sha being posted. This seat reviewed
`cbeaac0d2a3019bb45534f5ba0d215e727f3f6d8`. Round 34's pin is
`3d5c709b69bc32a00a7776bf47303771d17d87f5`.

## Why the pin moved out from under it

CYC-0091-91c8e949 pinned `cbeaac0d2` and dispatched this seat **before** proving
`PREFLIGHT_FULL=1` green on that tree. The run then came back `EXIT=1` on exactly one test —
`scripts/tests/test_affected_tests.py::test_the_committed_record_matches_the_committed_gatekeepers`,
stale because `scripts/preflight.sh` had been rewritten after the last stamp. Clause 2 needs a green
FULL run on the commit being posted, so the fix had to land, and landing it moved the tree.

★ **THE ORDER THAT AVOIDS THIS, WRITTEN DOWN BECAUSE IT COST A SEAT:** get a commit whose FULL run
is green, **then** pin, **then** seat it. A pin is a claim that this commit is the one that goes
out, and a commit that has not passed the gate the bar accepts is not yet that commit.

## What it is still worth

⚠ **THE PAPER'S BYTES ARE IDENTICAL AT BOTH COMMITS, AND THAT IS MEASURED RATHER THAN ASSUMED.**
`git diff cbeaac0d2 3d5c709b6` touches `research/autonomy/research-ledger.json` and
`scripts/selector-validation.json` and nothing else; the article, the tables and the supplementary
information hash to `afd60b9e…`, `defbbf6e…` and `37833638…` at both. So this seat read exactly the
text round 34 reviews, and its verdict of **no blockers** is why the pin was allowed to stand rather
than the paper being edited first.

★ **WHAT A SUCCESSOR SHOULD DO WITH IT.** Read its P1 and its P2 list as a work queue — several are
real defects in deposited artifacts and in guards, and none of them gates a paper. ⛔ **Do not move
it into `review-seats/` and do not re-point its `reviewed_commit`:** a seat record is a claim about
what a reviewer read, and editing the sha to fit a bar falsifies it. Round 34's own seats re-derive
their findings at the pin; nothing here is inherited by them, because a successor that inherits its
predecessor's reasoning inherits its mistakes.
