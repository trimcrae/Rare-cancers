# Cross-paper advance — synthetic family PARKED, three distinct scouts dispatched

Recorded `date -u` 2026-09-08 07:02 UTC. Same session, sole parent collector, `claude-opus-5` medium on the
saved subscription, no overage, deadline 2026-09-09T02:37:19Z unchanged.

## 1. The synthetic / figure-validation family is PARKED, with its exact missing input

**Missing input:** one rendering of PMC8891938's **figures and tables** from a network path not subject to this
session's NCBI egress block. Preserved verbatim, the two outcomes that produced it:

```
{"error_type":"EGRESS_BLOCKED","domain":"pmc.ncbi.nlm.nih.gov","message":"Access to pmc.ncbi.nlm.nih.gov is blocked by the network egress proxy."}
{"error_type":"EGRESS_BLOCKED","domain":"www.ncbi.nlm.nih.gov","message":"Access to www.ncbi.nlm.nih.gov is blocked by the network egress proxy."}
```

Verdict **UNKNOWN**, no content returned, no raw-content artifact (labelled). **Not to be routed around:** no
NCBI retry, no CI or runner route, no different network, model or tool, no other figure-validation route, no
new synthetic sweep, no point-count successor. The unsupported CI escape-hatch claim stays **unacted on**.

⚠ **Correction to my own earlier wording — no claim of perfect contract compliance.** I wrote that S7 "followed
the contract exactly." The pre-dispatch contract says stop **on a fetch failure**; the child attempted **two**
URL forms before stopping. The second attempt was a same-record alternate form and the child recorded both
verbatim, but it is **not** literal compliance with "stop on a fetch failure", and I am recording the
distinction rather than re-auditing it.

⚠ This family's 13–15 candidate rows are **not the whole admitted backlog**, and nothing here claims exhaustion
of any stream.

## 2. Document-block-and-advance applied ACROSS papers — three parallel scouts, distinct streams

Each must **examine actual inputs** and return a **ranked decision with a single recommended next executable
checkpoint**, carrying all six elements: unmet question and why it matters; exact reachable inputs and access
limits; proposed contribution and novelty uncertainty; specific distinction from prior no-gos; finite
acceptance; stop condition. **An honest "nothing qualifies", with per-item reasons and each one's exact missing
condition, is a full result** and outranks a stretched positive.

| child | stream — none examined before in this campaign | why it is separate |
|---|---|---|
| **A1** `ac1b46c710a5d8e84` | `research/hypotheses/candidates.json` — 14 drug/hypothesis candidates with mechanism, regulatory status, EMC-vulnerability claims and per-claim `sourceId`s, plus its producer `build-candidates.mjs` | a hypothesis stream, not the publications graph; never opened in this campaign |
| **A2** `a6675fd70c358f364` | `systems/graph/routes.json` — 83 routes, of which **28 carry no `closure_kind` at all** and 24 are `open`; several graded *"adopt now"*, *"keep, unblock cheaply"*, *"NEAR-TERM LEAD"* | the route layer, tested against each row's own `distinct_from` claim rather than trusting it |
| **A3** `ab2376c8974b3232b` | `systems/graph/strategies.json` (14, each with `thesis`/`next`/`limitations`) + `blockers.json` (21, with `kind` and `owner`) | the portfolio layer **above** routes; blockers separated by kind — authorization vs missing capability vs missing measurement |

**Ranking instruction given to all three: paper merit before tractability.** Easy execution and quota must not
determine rank.

## 3. Exclusions carried into every scout, verbatim in each dispatch

P1–P6 and every disposition (including PUB-CARE-DELIVERY's answered-no and PUB-LOCOREGIONAL's parked
site-denominator); S1/S3; the NR4A Perspective and **every NR4A-labelled route or successor**, P6's proposed
manuscript included; the W25 / GSE243553 / primary-article / Results / novelty hold — the writer is not woken
and its continuation is not retried; every `CLOSED-WORK.md` denied source; GSE4303/GSE28866; PMID 22592656; and
the now-parked synthetic family. **A new title, an old eligible graph row, a changed owner or model, or a
repeated unchanged gate does not make a distinct paper.** P4's and P5's scoped findings are **neither automatic
paper admission nor blanket scientific closure** — their recorded limitations apply as written. No record or
consumer census, no infrastructure audit, no undifferentiated idea list. Routes closed as `premise_false`,
`definitional`, `arithmetic_over_fixed_fact` or `confound_in_the_system` are closed on their merits; a route
closed on `authorization` is blocked on **permission**, to be named, never routed around.

## 4. Ownership, retention, capacity

Separate output ownership per candidate; children write only to their own task-scoped durable directories
**outside** the shared checkout (`/tmp/claude-0/a1-retained/`, `a2-`, `a3-`), hash-verified **before** any
cleanup and not deleted; **the parent alone collects into the repository**. Original source, code, model and
result bytes retained with hashes, failures, refusals and negative results included. ≥10 GiB free (20 GiB at
dispatch). No new session, controller, task system, local pilot, billing, manuscript, publication, PR or merge.

**Capacity:** three started because three streams with real distinct questions and usable inputs were
identified — **not** a target-driven number. Independent useful work is not serialised behind the parked
methods family, and the count expands as defensible work actually appears. **No start is claimed from a target
or an intention: only children with an observed transcript and a verified model are counted.**
