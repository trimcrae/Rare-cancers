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

---

# A2 RESULT — **NO-GO on a distinct paper (0 of 52)**, but it found a real measured defect. Collected 07:23 UTC.

Child `a6675fd70c358f364`, observed transcript model `claude-opus-5`, 07:10:45 → 07:16:38 UTC (5 m 53 s, 24 tool
calls). No repository write, no git operation. Durable artifacts `sha256sum -c` **2 of 2 OK** in
`/tmp/claude-0/a2-retained/` (not deleted) and again after copying to `paper-lane/A2-executed-artifacts/`:
`unclosed-route-census.json` `741593e0…` (34,671 B, all 52 un-closed rows), `A2-DECISION.md` `53bcfd3d…`.

## ⭐ Measured defect — parent-corroborated directly, not taken on the child's word

`research/manuscripts/emc-host-factor-model.json` sets **`competing_share_of_deaths_used = 0.394`**, sourced to
*"within-series (Meis-Kindblom 1999) — the only pairing measured on the same patients."* But the paper's own
Appendix A.1 (`emc-mortality-mechanisms-paper.md:391`) reads verbatim **"Competing share, 39.4 per cent
superseded by 21.7 per cent"**, and its Results table at `:241` carries the adopted value —
`| combined | 163 | 18 | 5 | 21.7 % | 11.0 points |`. **I re-read all three lines myself and confirm them.**

Two consequences: the model's load-bearing denominator is the **superseded** estimator, high by
**39.4 / 21.7 = 1.82×**, inflating every compartment-B band it produces; and the model's source sentence is now
**false**, because `direct_cause_split` *is* a pairing on the same patients and is what the paper adopted.

## The structural reason nothing qualifies

From the two graph files alone: **every un-closed route maps to an endpoint that is `drafted` or
`posted_preprint`**, except the P1–P6 routes and PUB-ASO. The only other non-drafted endpoint,
`PUB-PARKED-MODALITIES`, owns five routes and **all five are `instrument_limit`** — closed on their merits.

⭐ **And a sharp observation about the graph's own novelty field:** only 15 of 52 un-closed routes carry
`distinct_from` at all, and the mortality family carries none. Four claims were tested against the tree and all
four hold — but **`distinct_from` asserts distinctness from another *route*, never from an already-drafted
*manuscript*, and in every case tested the manuscript is what disqualifies the row. A `distinct_from` that
holds is not paper novelty.**

The three tests were kept separate as the correction required. **Zero of 52 pass all three**; the top-merit
route, RT-HOST-FACTOR, passes T1 (distinct) and partly T2 (input) and **fails T3 (non-overlap)** — its endpoint
`PUB-MORTALITY-MECHANISM` is already drafted.

## The scope correction took effect, and the child disclosed its own earlier error

A2 records that its **first pass excluded a block of routes by NR4A label**, that it **retracted that** when the
correction arrived, and that it re-judged all six affected routes on named holds only. Every exclusion in the
final report cites a recorded reason: RT-ASO on the submission-owner freeze; RT-HORMONE-PARTNER and RT-NR2F1 on
**P6's unauthorized manuscript** (the label being incidental); RT-POPULATION-REGISTRY on the user's rejection of
the registry ICD-O paper; P1–P5 routes on their own dispositions.

## Authorization rows — inspected, not bypassed

All four `closure_kind: authorization` rows (RT-ASO-ASK, RT-ATR-PANEL, RT-TRABECTEDIN-PPARG, RT-SSTR2) have a
`next.blocked_on` naming **`BLK-NO-WET-LAB`, not a permission gate** — so the `authorization` label is **partly
stale**. The real boundary is two conditions and both are named: an absent **bench** (a capability, CLAUDE.md
§5) and an un-granted **permission** for the outreach act (CLAUDE.md §3), whose enforcer is the user, not a
script. A2 **did not open `publication-authority.json`**, so whether any current grant covers such an ask is
recorded **UNKNOWN rather than assumed either way**. None becomes executable; none is proposed for revival.

## Recommended checkpoint — explicitly NOT a paper, and not taken here

Re-run `emc_host_factor_model.py` with the share from `direct_cause_split`; accept only when the used value
equals the paper's adopted value, the source names `direct_cause_split`, the false "only pairing" sentence is
replaced, every compartment-B figure moves by the recomputed ratio with none quoted outside its band, and
`pytest` (never `python3 -m pytest`) exits 0 on an otherwise unchanged tree. **Stop** if a committed record
shows the within-series estimator was chosen deliberately — then it is a documentation defect and the branch
ends there. **No novelty is claimed**, and whether the band is interesting at 21.7 % rather than 39.4 % is
**UNKNOWN until recomputed**. It is an **owner act on a drafted manuscript**; no campaign worker may take it and
A2 did not.

Unreachable and named: the model's `factors_not_entered` (diabetes/metformin, hypertension) need a **network**
retrieval outside worker authority; host-factor prevalence in a real EMC cohort is blocked on
`BLK-NO-EMC-DATA`. A2 also flags that any write-up in this family must **resolve the key, not the number**, per
W57's recorded 162-vs-577 hazard on route 81. No clinical efficacy, safety, selectivity, therapeutic-window or
readiness claim is made anywhere; there is no wet lab.

---

# A3 RESULT — 8 of 14 strategy `next` fields are STALE; ranked #1 is executable. Collected 07:28 UTC.

Child `ab2376c8974b3232b`, observed transcript model `claude-opus-5`, 07:11:04 → ~07:18 UTC (25 tool calls).
No repository write, no git operation, no network. Durable artifacts `sha256sum -c` **2 of 2 OK** in
`/tmp/claude-0/a3-retained/` (not deleted) and again after copying: `strategy-next-adjudication.json`
`02fc3b6b…` (10,330 B), `authorization-boundary-inspection.md` `c0d21d28…` (3,604 B).
It reported one command's **exit 128** verbatim (a `git rev-parse` run with cwd inside the scratch directory)
rather than smoothing it — the hash verification in that same command completed first.

## The layer has not been re-read in a month, measured

**8 of 14 `next` fields are STALE** — recorded open, already answered by committed artifacts. 9 rows carry
`last_verified: 2026-08-05` and 5 carry `2026-08-09`, while **every artifact that answers a `next` is dated
2026-08-07 or later**, and P1/P3/P5's work today answers three more. A3 correctly refuses to call that a paper:
*"a bookkeeping observation and not a paper — which is why it is not my decision."*

## ⭐ Ranked #1, and parent-corroborated: the awaited input ARRIVED and refuses what it was awaited for

`ST-REPURPOSING.next` reads: *"Watch for a fetchable public EMC expression dataset — the single input that
would convert most of this family from class-inherited argument to measurement."* **The dataset arrived**
(PRJNA1357027 / SRP640302, n=12 FFPE, public since 2025-11-11) and is committed as a gene table —
**parent-verified `gene_counts_sha256 = 8aa3064a97a496a8…`**. And the same artifact **refuses the conversion**,
in its own words, which I read directly: *"⛔ NO DIFFERENTIAL-EXPRESSION RESULT IS COMPUTED OR REPORTED FROM
THIS COHORT, AND THAT IS THE FINDING RATHER THAN A GAP"* — six versus six, five d.f. per arm, one batch, FFPE
spanning 1997–2020, no adjustable covariate.

**So the live question is not "has data arrived" but whether any committed EMC dataset can support a per-agent
expression-based repurposing claim at all.** Parent-verified the coverage gap too: `ST-REPURPOSING` owns **11**
routes, and the existing `emc-fourth-cohort-route-readout.json` adjudicates 16 routes of which **only
`RT-TRABECTEDIN`** is one of them.

## Authorization inspection — the row is NOT stale, and it is a human NO

`BLK-SELECTIVITY-CONTROL-UNAUTHORIZED`'s stated reason **matches the live enforcer exactly**:
`autonomy-state.json → gpu_spend_prohibited` is `active: True`, set `2026-09-02T16:35:00Z` by
`trimcrae, in session`, scoped to *"every GPU rental, fleet, fan-out and dispatch … at any price, including $0
free-credit lanes and including a resume of a previously started run"*, with `gpu_ban.py` failing closed.
**The missing condition is a human authorization that was asked and answered NO — named, and stopped.** A3 also
records the blocker's own warning that re-deriving the price *"has rediscovered the 2026-09-02 mistake rather
than found new work"*, and took no action on it.

## A tempting cross-cut A3 recorded and correctly did NOT take

Placing P5's only concordant cross-platform negative (the PAPS sulfate-donor module) against W02k's
random-panel null would be informative — **and it is forbidden**: further lane-2 statistics on
`emc-expression-panels.json`, with its named reopening input DENIED. It recorded it and stopped, ran no
statistic, and withdrew nothing from P5's finding.

## Parent refinement before execution — A3's "10 uncovered routes" is an upper bound

Of the 11 `ST-REPURPOSING` routes, several are **excluded by named holds, not by label**: `RT-RET` and
`RT-ALK-HIT` are **P4's `PUB-KINASE-LEADS` leads**; `RT-HORMONE-PARTNER` is **P6's unauthorized manuscript**;
`RT-HDAC-BET` is a **parked negative (`AUT-029`)**. The executing worker must apply those exclusions itself and
**report the actual adjudicable count** rather than assuming 10.

---

# ⛔ B1 STOPPED as nonconforming — 2026-09-08 07:23 UTC. And I mis-ranked it.

`TaskStop` issued and confirmed (`killed`). **Not restarted, not replaced by another route, gene or consumer
readability census.**

**Why it was wrong, on its own contract text and not on its name:** B1 adjudicated `required_validation` genes
as READABLE / UNDECIDABLE / UNREAD, **explicitly an instrument state and never a repurposing measurement**. That
is an **input/route inventory** with no separately justified scientific question, contribution, novelty or
acceptance rationale — precisely what the standing cross-paper instruction excludes. **Calling it "the strongest
checkpoint" supplied none of the missing rationale**, and ranking by executability is the error I made: A3
ranked it first among *its* rows, and I promoted that to "strongest available work" without applying the
paper-question test myself. **No genotype, statistic or DE extension is authorized by this stop.**

**Preserved:** the child stopped ~40 s in, before writing anything. `/tmp/claude-0/b1-retained/` exists and is
**empty** — recorded as such, not deleted. Its partial transcript output is retained at
`paper-lane/B1-STOPPED-partial-output.md` (78 bytes, the single line it emitted). **No missing bytes are
claimed to exist; nothing is reconstructed.**

## Distinctions kept exact — none of these is claimed

- **Three repository entry points are not the corpus.** A1, A2 and A3 checked `hypotheses/candidates.json`,
  `routes.json` and `strategies.json` + `blockers.json`. **That is three entry points, and it does not
  establish that public-data or study-development work is exhausted.** No global exhaustion is claimed.
- **A drafted endpoint does not prove every materially distinct question or useful scientific correction is
  closed.** A1's and A2's negatives are scoped to *paper novelty against a drafted manuscript*; they say nothing
  about whether a correction inside one is warranted.
- **Graph eligibility alone does not establish a new paper either.** An `open` route, an un-closed
  `closure_kind`, or a stale `next` field is not a paper question.

## Final counts, actual — not prior running rows

**Active research children: 0.** **Helpers: 1** — the legacy Bash waiter "Block until pass 2 finishes", which
computes nothing and is not research. A1, A2, A3 are **completed and collected**; B1 is **killed**; the only
other subagent row is a 4-hour-old completed one.

Model receipts retained and unchanged: A1 `ac1b46c710a5d8e84`, A2 `a6675fd70c358f364`, A3 `ab2376c8974b3232b`,
each with observed transcript model set exactly `['claude-opus-5']`; their decisions, input provenance,
failures and durable artifacts are committed under `paper-lane/A{1,2,3}-executed-artifacts/`, hash-verified in
both the retained directory and the checkout, with the source directories not deleted.

## ⛔ B1 retention CORRECTED 2026-09-08 07:27 UTC — my earlier description was wrong

I wrote that B1 "stopped ~40 s in, before writing anything" and treated the 78-byte file as its partial output.
**Both are wrong and are corrected here.**

**What those 78 bytes actually are:** the child's **last assistant text block** — the single line
*"I'll start by recording the environment state and reading the required inputs."* It is **not** a work
transcript and must not be described as one; my collector extracts the longest assistant text, and at kill time
that was the only one.

**The original transcript exists and contains real work.** At the path pattern you name:
`/root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a02d5523854550079.jsonl`
— **231,694 bytes, sha256 `4fa93cf8534e2c23a2a60080bd846f36c998db89c1ef98fa9aff2bdfe07e999a`**, observed model
set exactly `['claude-opus-5']`, **17 tool_use and 17 tool_result blocks, all Bash**. (The `tasks/*.output` path
is a symlink to this same file.) So B1 had done substantial reading before the stop — the contract documents,
the routes/strategies enumeration, the fourth-cohort quant artifact, the readout generator, and a gene-counts
TSV digest — **not nothing**.

**Retained, original bytes, before any cleanup**, at `paper-lane/B1-STOPPED-artifacts/`:
`ORIGINAL-CHILD-TRANSCRIPT.jsonl` (`4fa93cf8…`, the full original), plus all **17 original tool responses**
extracted unchanged into `original-tool-responses/` with tool name, verbatim input and hash per response in
`INDEX.json`, verified by `sha256sum -c` (**18 of 18 OK**). `/tmp/claude-0/b1-retained/` is genuinely **empty**
— B1 was killed before writing its own durable output — and that emptiness is the accurate statement, distinct
from the transcript, which is not empty.

**No B1 rerun, no new query, no grading, no regenerated output.** The stop stands.

---

# Amendment 2026-09-08 10:23 UTC — what counts as advancing, restated as binding

This amends the existing work-selection record in place. **No new queue, scheduler, runner or
controller is created**; ownership stays with the one parent/launcher and the one local collector.

## The rule

**When the leading paper reaches a real blocker: record the paper-specific blocker, its evidence and
the exact reopening condition — then immediately start the next eligible unfinished paper, in the
same work cycle.** Existing **unpublished drafts are eligible**; a wholly new paper question is never
required, and "already drafted" is not an exclusion.

**Do not wait** for another root or user prompt, a daily boundary, an empty generated queue, or local
artifact collection to finish.

## ⭐ What does NOT count as advancing

A selection, a contract, a start receipt, a model verification, an adjudication, a manifest, or any
other evidence collection **is not substantive execution**. Nor is a status summary, a census, or a
re-review of closed work.

**The bar:** the next paper has an **actual `claude-opus-5` medium task executing** toward a concrete
manuscript or evidence contribution, under a recorded contract with **finite acceptance and stop
conditions**. Anything short of a running child is a stall, however well documented.

## What a blocker record must contain

1. **Which paper**, and which specific claim, item or artifact is blocked.
2. **The evidence** that establishes the block — measured, not inferred. "Blocked" is a claim that
   needs evidence and is usually wrong; take the free reading first.
3. **The exact reopening condition** — what would have to become true, stated so someone else can
   recognise it.

## Current application

- **surface-targets is carried through its remaining ready work.** `K1` (`af7ad52123f8eeccd`,
  `claude-opus-5` medium, contract input `b0f0ffa4`, contract 10:19:28, parent-observed 8 ×
  `claude-opus-5` / 0 others at 10:20:12) is executing on peer review item 4's unresolved figure half.
  It is kept healthy, collected normally, and **not duplicated or restarted**.
- **When surface-targets reaches an actual blocker**, it is recorded per the three points above and
  the next eligible unfinished paper starts immediately.
- **Terminal contracts are not reopened:** F1, G1, H1, I1, J1. Nor is DFSP recomputation, nor any held
  writer, W25, NR4A Perspective, P6, frozen-asset or denied-source scope.

Unchanged: sole launcher and sole local collector, first-party saved subscription with no paid
fallback, the retention rules in CLAUDE.md §8, and the original deadline **2026-09-09T02:37:19Z**,
never extended or reset.
