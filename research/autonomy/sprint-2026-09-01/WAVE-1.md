# Wave 1 — dispatched 2026-09-01T18:4xZ (2:4x PM ET)

**12 concurrent seats, one working tree, disjoint owned paths.** Contract:
[`SPRINT-CHARTER.md`](./SPRINT-CHARTER.md). No seat runs a git write command; no seat writes
`research-ledger.json`, `autonomy-state.json` or `amendments.jsonl` — those three are the driver's,
because concurrent writers to any of them collide silently (the ledger's id allocator provably so,
which is why S1 exists).

## The theme

Wave 1 is **the machinery the rest of the sprint runs on**. Ten of the twelve seats are loop
infrastructure and lint tooling, and that ordering is deliberate rather than timid: a sprint that
fans out twelve ways over fourteen hours will write many ledger rows, run many blind seats and
measure many papers against the publish bar. Every one of those acts goes through a piece of
machinery that currently has a known, recorded defect in it. **Fixing the instrument before taking
the readings is the cheap order; the expensive order is discovering at hour ten that the readings
were taken with a broken one.**

Two seats (S11, S12) are science, because the charter's authorisation explicitly reopened non-ASO
work and a wave with no science in it would be the §0 failure — documenting the machine instead of
advancing a route.

## Seats

| seat | items | owns | one line |
|---|---|---|---|
| **S1-IDS** | AUT-PD-171 | `research/autonomy/ids.py`, its tests | The ledger id allocator collides across concurrent sessions while its sibling in the same file does not. **The defect this sprint is most exposed to.** |
| **S2-ESCALATION** | AUT-PD-203, AUT-PD-196 | findings file only — read-only census | Are the thirteen `requires_trimcrae` rows decisions awaiting him, or the loop's own work wearing the costume of one? Measure every clause of every publication behind them. |
| **S3-CITATIONS** | AUT-PD-031, AUT-PD-134, AUT-PD-133 | `line_citations.py`, its tests | A fixer that repairs one copy of a shared fact and is silent about the rest — and a guard that checks fewer than half the citations in its own file. |
| **S4-COVERAGE** | AUT-PD-149, AUT-PD-148, AUT-PD-130 | `claim_coverage`, the ablation harness | What counts as a claim, what can be perturbed to falsify it, and whether the coverage record can go stale unnoticed. A quantity written in words is currently unfalsifiable by construction. |
| **S5-READABILITY** | AUT-PD-142 | `lint_readability.py`, its tests | The sentence splitter does not break before a callout glyph, so it overstates length — and `readable_enough_to_review` is a publish-bar clause. Some papers may be held below the bar by a bug. Blast-radius table required. |
| **S6-COMMITLOOP** | AUT-PD-164, AUT-PD-183, AUT-PD-172 | `preflight.sh`, `affected_tests.py`, CLAUDE.md §6 cost figures | CLAUDE.md says the commit loop costs ~75 s; it may be ~13.5 min. Every session reads that figure before deciding whether it can afford the gate. |
| **S7-CHAIN** | AUT-PD-028, 141, 168, 175, 195, 001, 189 | `regenerate_aso_chain.sh`, the archive manifest tooling | Seven rows, one defect: *an artifact that records a commit sha, produced at a moment that is not the moment it is published*. A manifest naming a rebased-away commit is not stale, it is false — and every guard on it stays green, because a sha is a well-formed sha whether or not anything is at the other end. |
| **S8-HANDOFF** | AUT-PD-169, AUT-PD-173, AUT-PD-174 | `handoff.py`, `continuity.py`, the session-lifecycle modules | Claiming needs a pushed trunk; pushing needs the gate; so no parallel work can start while a gate runs. **Not theoretical tonight — this sprint routed around that deadlock by hand.** |
| **S9-SEATRECORD** | AUT-PD-193, AUT-PROP-006 | `publish_bar.py`, `seat_scratch.py` | A round's roll-up is counted as a sixth seat. This is the instrument the rest of the sprint is measured with, so it is checked before it is used — and it may move only in the stricter direction, because tonight's sprint is a cycle this bar is currently blocking. |
| **S10-SCHEMA** | AUT-PD-030, AUT-PD-181 | `ledger_io.py`, `receipt_schema.py`, the generator | Two dresses on one defect: a fact typed by hand beside the same fact derived by machine, with nothing comparing them. |
| **S11-DDG** | AUT-078 | findings file, new analysis scripts | Why does the fan-out results prefix hold zero `ddg.json` objects? Real-money forensics, and the answer this repository is worst at is the plausible story — including hypothesis (e), that the listing reporting zero was itself wrong. |
| **S12-TWOPOP** | AUT-060 | a new model script + JSON artifact | The two-population model, each median its own parameter interval, **and the median with no denominator carried as exactly that** — not imputed, not pooled, not given a manufactured CI. |

## What wave 1 deliberately does not contain

- **No manuscript prose edits.** S5 measures which sentences are over the ceiling and reports;
  nobody rewrites. Twelve seats in one tree is the wrong shape for editing papers, and CLAUDE.md §6
  records what it cost the last time a mutation window overlapped a commit.
- **No ledger writes.** Every seat proposes rows in its findings file. The driver writes them once,
  after S1 has either fixed the allocator or shown it did not need fixing.
- **No blind adversarial seats yet.** They are wave 2, and they wait on S9 — running the paper
  hardening rounds before checking the instrument that counts them would be taking the readings first.
