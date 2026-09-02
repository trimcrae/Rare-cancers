---
id: DOC-SPRINT-DRIVER-04-SESSION-LIMIT
title: "Nine concurrent seats inside a width of twelve, and the limit still bit"
level: L3
kind: incident
status: live
purpose: "What the 2026-09-01 session-limit stall cost, and the measurement showing that `subagent_width` governs concurrency while the limit that fires governs tokens — so a compliant width can still exceed the budget."
scope: "One stall, 21:35-23:20 UTC. The width dial it moved is in autonomy-state.json; the seats' own partial records are the primary evidence for what survived."
audience: [autonomous research agents, maintainers]
date: 2026-09-01
last_verified: 2026-09-01
---

# DRIVER-04 — nine concurrent seats inside a width of twelve, and the limit still bit

**2026-09-01, ~21:35Z.** Seven background agents and one foreground dispatch returned
`rate_limit / HTTP 429: You've hit your session limit · resets 11:20pm (UTC)` within the same
second. The driver session itself was blocked until **23:20Z — one hour forty-five minutes of a
fourteen-hour window**, against a directive whose whole purpose was to spend that window.

## What was running, and what it cost

| seat | state at the kill | recovered? |
|---|---|---|
| S24 MHCflurry calibration | mid-sentence: *"Adding the audit record"* | ⭐ **yes** — 91 insertions were on disk, uncommitted and unpushed; see below |
| PUB-ATR arithmetic | one tool call in | no — nothing written |
| PUB-BIOMARKER-DEP × 5 (arithmetic, hostile-referee, citations, statistics, regression) | 1-3 tool calls in | no — two had written record skeletons carrying `verdict: in_progress` and **zero findings** |
| PUB-ATR blocker fixer | killed on its first API call | no — never started |

**Four PUB-ATR seats had already landed and are unaffected.** Their records are complete, on disk,
and carry the round's findings; that is charter rule 3 (write the findings file *as you go*)
working exactly as the `git reset --hard` incident said it would.

⛔ **But rule 3 has a floor this stall found: a seat killed before its first finding has nothing to
write down.** Two empty skeletons were produced. They were deleted rather than kept, because a
record reading `verdict: in_progress` sitting in `review-seats/` is the shape a reader mistakes for
a seat result — and an absent reading is not a reading of absence.

## ⭐ The measurement: width was compliant and the budget was not

`subagent_width` was **12**. Concurrency at the kill was **9**. The cap was never exceeded, and the
limit fired anyway.

The reason is that the two quantities are different. One completed seat reports its own spend:
**250,016 tokens over 55 tool uses in 961 s** — an ordinary blind seat, not a heavy one. Nine of
those running together is on the order of **2.2M tokens in about sixteen minutes**. `subagent_width`
bounds *how many agents run at once*; the account limit bounds *tokens per window*. Width is a proxy
for burn rate and it is a poor one, because seat cost varies by more than an order of magnitude
while width counts every seat as 1.

★ **This re-reads the incident the dial was created for.** CLAUDE.md records the 107-agent fan-out
as a width failure — 40 completed, 67 errored, the synthesis lost. It was a *burn-rate* failure that
width happened to correlate with. The dial has been governing the wrong variable since it was
introduced, which is why a value of 12 felt safe: nothing was measuring the thing that actually runs
out.

⚠ **What this does NOT claim.** The 107-agent fan-out hit the account *weekly* limit; this stall hit
a *session* limit resetting in under two hours. They are different limits and no claim is made here
that they share a mechanism — only that both are limits on token volume, and that neither is what
`subagent_width` counts.

## The response, and why it is not "spend less"

The standing directive is to convert a week's credits into work in fourteen hours. Spending less is
a failure against it. **The defect is not the spend; it is that the spend was not RECOVERABLE** —
six seats consumed real tokens and produced nothing a later session can read.

So two changes, neither of which lowers the ceiling:

1. **`subagent_width` 12 → 5.** Not because 12 agents is too many, but because a wave that dies
   loses everything still in flight, and a smaller wave loses less. Width moves down faster than it
   moves up (CLAUDE.md §1), and this is the down direction.
2. **Waves, not one fan-out.** The same total spend delivered as sequential waves of 5 converts a
   limit stall from "six seats lost" into "at most five lost, the rest already landed and committed".

⛔ **And the real fix is upstream of both: a seat must produce a durable finding EARLY, not
correctly.** The four surviving ATR records are complete because those seats ran long enough to
finish. The right invariant is that a seat writes its first real finding before its tenth tool call,
so that being killed at minute three still leaves something on disk. That is a change to the seat
prompt contract in `SPRINT-CHARTER.md`, not to a dial.

## What the stall did not lose, and why

S24's 91 insertions were on disk in the shared working tree, uncommitted and absent from its pushed
branch, when its agent died. They carry that seat's central result: probing IEDB for
`parent_source_antigen_name ILIKE *fusion*` returned **988 scoreable pairs across 39 antigen names,
of which zero are somatic fusion breakpoints** — ubiquitin fusion proteins, poxvirus entry-fusion
complexes, vacuolar trafficking, read-through chimeras. The bare word "fusion" is a homonym in
protein nomenclature. Had the driver run any of the commands charter §1a forbids, that finding would
have died with the agent that produced it and nothing would have recorded its absence.
