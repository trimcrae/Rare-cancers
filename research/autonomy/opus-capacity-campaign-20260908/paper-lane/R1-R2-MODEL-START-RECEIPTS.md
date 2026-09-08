# R1 and R2 — served-model receipts, parsed from the child transcripts

Verified by the parent 2026-09-08 ~11:31 UTC, after the contract commit `cc23cd1d`.

| lane | child | requested | writes to repo? | scope |
|---|---|---|---|---|
| **R1** | `a6a41bcc67e17cc38` | `claude-opus-5` medium | **none** — lane only | ATR: a **proposed** reconciliation patch grounded in the committed module, artifact, test, changelog and figure |
| **R2** | `aefc59707cb2a5225` | `claude-opus-5` medium | **none** — lane only | repurposing: does one case report meet the paper's **own** T3 definition, and what changes if not |

Parsed from transcript model fields, **not inferred from contract text**. Route: existing first-party
saved subscription — no paid fallback, no overage, no credits, no GPU.

**Neither writes anything shared**, so they cannot collide with each other or with any future writing
lane, and **parent integration alone owns shared files**. Neither creates an approval queue, and the
scientific coordinator retains the final version and integration decision.

## Actual concurrency

**2 research children executing. 1 helper** (the legacy Bash waiter — computes nothing, **not**
research). Completed lanes are **not** counted as running; current research count before these two
was **zero**.

## Why 2 right now, and what would raise it

I am not claiming a blocked campaign. The correction is taken: **a specific new computational or
source question with usable evidence qualifies** — a task need not begin from a known manuscript
defect, and the two papers examined do not speak for the rest of the rank.

What actually bounds the number this minute is that each further lane needs a **distinct question with
inputs already permitted here**, and the near candidates each fail that test on a *measured* ground,
not a presumed one:

- **care-delivery** — its open caveat ("which fields a free-text term search covers is not established
  here") is a genuine question, but settling it needs a trial-registry field probe; **no such route is
  admitted**, and no committed artifact records the search's field coverage.
- **mtap-prmt5** — its two remaining blockers are publisher-level confirmation and cross-version
  identity, both requiring routes measured as not exposing the assets.
- **surface-targets** — the DFSP-only sensitivity analysis is the one remaining computational task and
  is **explicitly out of scope** by standing instruction, repeatedly restated.
- **tcip** — inspected: the `min_contact_residues` naming hazard is **already disclosed in the
  manuscript** with both counts reported, so there is no defect and no ready question there.

⭐ These are findings, not excuses, and each is falsifiable. If R1 or R2 surfaces a scientific question
answerable from committed inputs, it becomes a lane immediately.


---

# Timestamp correction, appended 2026-09-08 11:30 UTC — original header preserved

**The header's "~11:31 UTC" was a composition estimate, not an observed time**, and it is inconsistent:
it postdates the local observation at 11:26:53. Corrected from the actual record:

| event | actual |
|---|---|
| parent's model-check command (`date -u` in the same command) | **2026-09-08 11:25:20 UTC** |
| R1 first transcript event | 11:24:5x Z (from the retained JSONL) |
| R2 first transcript event | **11:24:53 Z**; last **11:27:49 Z** |

This is the same error class already corrected for the E1 contract ("08:18"), the H1 receipt
("09:17/09:18"), the M1 receipt ("~10:54") and the N1 pair ("~10:56/10:57"). **No finding, bound or
term changes.** Full child event spans are taken from the originals at collection, and **future
current timestamps come from `date -u`, not from composition.**
