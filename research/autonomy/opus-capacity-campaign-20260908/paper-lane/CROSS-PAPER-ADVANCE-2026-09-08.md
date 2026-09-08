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

---

# ⛔ SCOPE CORRECTION appended 2026-09-08 07:16 UTC — a label is not a hold

**I over-broadened, and it is withdrawn.** Section 3 above told the scouts to exclude *"every NR4A-labelled
route or successor."* That manufactures a blanket closure out of a **name**. This disease is NR4A3-driven, so
excluding by label would have closed most of the science by accident — which **no actual hold does**. The
over-broad instruction was withdrawn **in flight** to all three running scouts; **no restart, no re-plan, no new
audit**, and no scout was replaced.

## The actual named holds and closures, preserved exactly

Each stays in force, unchanged, and none may be retried, reworded or rerouted:

| held / closed item | recorded reason |
|---|---|
| **The NR4A Perspective** — one specific refused review | *"generic biology-access refusal with no causal passage identified. Closed without probes, rephrasing or rerouting. Do not recreate that restricted review under a new worker or paper label."* |
| **P6's proposed NR4A3 negative-results / architecture manuscript** and its claim corrections | explicitly not authorized by the orchestrator; its assertion of being different from the restricted Perspective does not authorize it |
| **Writer / W25 / GSE243553 / primary-article / Results / novelty continuation** | safety-blocked with **unknown scope**; the writer is not woken, the continuation is not retried, the hold is not reinterpreted |
| **Fresh full-genome access probe** | restricted; unchanged |
| `CLOSED-WORK.md` denied sources; GSE4303/GSE28866; PMID 22592656 | as recorded there |
| **Synthetic figure-validation family** | parked above, with its exact missing input |

**Rule now in force for all three scouts: excluding a candidate requires citing the specific hold or closure and
its recorded reason. "NR4A-labelled" is not a reason.**

## Two further corrections delivered with it

1. **Distinct does not mean eligible.** Showing a candidate is a separate question is **necessary, not
   sufficient**. It must separately pass: required input actually reachable; real scientific merit; and
   non-overlap with `drafted`/`posted` endpoints. The scouts now report those as **separate tests**, saying
   which each candidate passes or fails.
2. **An old graph `authorization` row is not itself the current permission boundary.** The scouts inspect the
   row's **actual recorded reason** and `owner` and say whether it still describes the standing authorization
   and the real enforcer, or is a stale record of a boundary that has since changed. **That is inspection, not
   bypass** — no real gate is routed around, weakened or tested, and a genuinely missing authorization is named
   as the missing condition and stopped there.

**This correction changes no safety or network hold and supplies no permission for any held continuation.**

## Worker counts — the legacy row named explicitly

| row | kind | counted as |
|---|---|---|
| **A1** `ac1b46c710a5d8e84` | research child, running, observed transcript model `claude-opus-5` | research |
| **A2** `a6675fd70c358f364` | research child, running, observed transcript model `claude-opus-5` | research |
| **A3** `ab2376c8974b3232b` | research child, running, observed transcript model `claude-opus-5` | research |
| **legacy Bash waiter, "Block until pass 2 finishes"** | old shell helper, **not research** — it computes nothing and produces no scientific output | **helper** |

**Active research children: 3. Helpers: 1 (the legacy waiter).** Not four research. Model evidence for all
three is the observed set in each child's own transcript, `['claude-opus-5']`, not the dispatch parameter.
No start is claimed from a target or an intention.

---

# A1 RESULT — **NO-GO, 0 of 14.** Collected 2026-09-08 07:20 UTC.

Child `ac1b46c710a5d8e84`, observed transcript model `claude-opus-5`, ran 07:10:25 → 07:14:45 UTC (4 m 20 s,
17 tool calls). No repository write, no git operation — `git status --porcelain` empty at its start and end.
Durable artifacts verified by the child (`sha256sum -c`, 2/2 OK), then **re-verified by the parent both in
`/tmp/claude-0/a1-retained/` (not deleted) and after copying** into `paper-lane/A1-executed-artifacts/`:
`DECISION.md` `52bcb3be…`, `candidate-adjudication.json` `9f1d2900…`.

## The decisive fact, independently corroborated by the parent

The stream is **not adjacent to a drafted endpoint — it IS that endpoint's data appendix.**
`systems/graph/publications.json` → `PUB-REPURPOSING` is **`drafted`**, document
`research/manuscripts/repurposing/repurposing-hypotheses.md`; and that manuscript cites
`research/hypotheses/candidates.json` **by path** at its line 545. **Parent-verified both claims directly**
rather than taking them from the child.

## A structural finding that grades every row at once

**No `sourceId` in the file resolves to a retained full text, PDF or extracted passage anywhere in the tree.**
Every one resolves only to a hardcoded object in `build-candidates.mjs:14-28` (`CITES`), whose `verified: true`
is a **hand-set literal** the producer reads only for key inclusion. So the evidence ceiling for the entire
stream is **RETRIEVED metadata plus an author's transcription** — no candidate carries PRIMARY-in-tree
evidence, and every "the source says X" in this lane is a transcription, not a reading.

## Ranking criterion — merit before tractability, applied and reported

Gates in order: (1) not already covered by a drafted/posted endpoint or a recorded closure; (2) would change a
reader's mind; (3) decisive input reachable at $0 without a bench. **Ease of execution was excluded and broke
no tie** — the cheapest row was ranked first *on merit* and still failed gate 1. **All 14 fail gate 1.**

The three shapes of failure: **9 of 14** have an open question that is a **bench experiment** and there is no
wet lab; **3** sit on a recorded closure or a named exclusion; the rest are inside a drafted endpoint with their
decisive clinical sources on the denied or unrecovered list.

## Exclusions cited by their actual reason, not by label — the correction took effect

Only **two** rows were excluded by a named hold, each with its ground stated: `brigatinib-screen-hit` is
**PUB-KINASE-LEADS lead 2**, i.e. P4's own material this campaign; `nr4a3-modulation` is excluded under the
binding NR4A prohibition **and** is independently closed as a parked negative (`AUT-001`). **No row was
excluded for merely mentioning NR4A** — rows 2, 3, 5, 8, 10, 13 and others were judged on coverage and inputs.

## The strongest question in the stream is refused **on the named ground**, not renamed

*"`notTriedInEmc: true` is a disease-level novelty flag that cannot see negative evidence one level up, so
ultra-rare candidate menus systematically over-report novelty."* That is already the drafted paper's own
subject **and already peer-reviewed**: `repurposing-hypotheses-peer-review-2026-08-10.md:44` states it as the
manuscript's central observation, `:314` records the measured version, and `:321` carries it as a standing
requirement over all fourteen candidates. **A new title, owner or model would not make it distinct** — refused
explicitly rather than re-badged.

## The one item with merit and reachable inputs is NOT a paper, and is not taken

Ledger **`AUT-PD-112`** — a correction inside the drafted manuscript, adding the committed class-level
carfilzomib bound (`EV-MAKI-2005`, `EV-BOKLAN-2025`, `research/literature/carfilzomib-class-clinical-2026-08-28.json`).
Its own premise: **no sentence in the manuscript is false today** — the defect is *incompleteness*, invisible
sentence-by-sentence. Access limit recorded: that artifact is **abstract-level only**, PMID 15739208 has no
PMCID, PMC12428389 unfetched, and `EV-MAKI-2005`'s per-histology enrolment denominator is **UNKNOWN and stays
UNKNOWN**; its recorded 0-record EMC query is a **dated observation, not a standing fact**.
⛔ **Not taken:** it is an owner/manuscript act under an active hardening program that reviews a pinned commit.
No campaign worker may take it and A1 did not.

**Nothing here admits a paper, and no efficacy, safety, selectivity, therapeutic-window or readiness claim is
made for any of the 14 agents** — "approved elsewhere" is a regulatory fact only.
