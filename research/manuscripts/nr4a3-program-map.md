# NR4A3 degrader — the program roadmap

**One document: what is done, what is true, what is blocked, and what is next.**

★ **WHY THIS FILE EXISTS (trimcrae, 2026-08-02): *"I feel like we're not being rigorous and have to cobble
together stuff from prose documents and it's leading to us missing things and having to constantly rediscover
connections."*** The dependencies between claims were real but existed only as prose scattered across
STRATEGY.md, the paper, the preregistrations and a dozen module docstrings — so the same connections kept
being re-derived, and blockers kept being misattributed. This is the graph, and now also the plan that sits
on it.

★ **AND WHY IT IS ONE DOCUMENT (trimcrae, 2026-08-02): *"Ideally the map serves as the new source of truth
and the strategy.md gets folded in with it into one document, just adding color. And then it can link to
appendices that give more history and stuff… It's really like a systems engineering task."*** **Read this
file top to bottom and you have read the whole plan.** STRATEGY.md's live layers — the gate scoreboard, the
landed-gate blocks, the thesis, the language-discipline rules, the validation architecture, the prospective
stage, **THE ORDERED PLAN**, the spend summary, the dependency spine, the open decisions — are **here**, moved
rather than copied, each under the heading and slug it always had. [STRATEGY.md](../../STRATEGY.md) is now two
appendices of pure history: [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims)
(superseded numbers and retracted claims) and
[Appendix B](../../STRATEGY.md#appendix-b--superseded-strategy-framings) (retired plan framings).
[§0.7](#07--what-machines-parse-in-this-file--and-what-is-left-in-strategymd) is the index of what a machine
reads in this file and what still lives there.

⚠ **SUPERSEDED, retained so it is not re-derived:** an earlier pass of this merge left ~2,430 of STRATEGY.md's
3,317 lines in place and *relabelled* them "the appendix set", so *"what do I do next"* still needed two
documents. trimcrae: *"Strategy.md and the mapping document are still different files? What is the role of
strategy anymore?"* The justification given was that seven CI checks parse STRATEGY.md by exact heading string
and 358 inbound references point at it. That constraint was real and it is now **discharged rather than
deferred**: every parser was repointed in the same commit, every moved heading kept its exact string, and no
row number or decision number changed. CLAUDE.md §5 is explicit that engineering effort is free, so
*"repointing seven parsers is expensive"* was never a reason.

⛔ **STATUS VALUES ARE READ FROM COMMITTED ARTIFACTS, NEVER TYPED HERE.** Every cell below points at the
artifact that owns it (CLAUDE.md rule 1). If this file and an artifact disagree, the artifact is right and
this file is the bug.

⛔ **ONE FACT, ONE PLACE — AND A PRICE IS DERIVED, NEVER TYPED.** A roadmap row in
[§10](#10--the-roadmap--one-ordered-list) says whether an item is **priced**, **projected** or **unpriced**,
and links to the rung or ladder row that owns the figure; an honest "unpriced" beats a number invented to
fill a column. The three editing rules this file inherits, unchanged in substance from the document it
absorbed:
1. **One fact, one place.** Every number, gate and decision has exactly one home section; everywhere else
   points at it. If you find yourself restating a cost, delete the restatement.
2. **Corrections go in [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims),
   not inline.** Never quietly drop a superseded number — and never leave the retraction narrative in the
   live text either. One line in the appendix; the live text carries only the current value.
3. **Register the old value when you change a pinned one**, in the same commit, in
   [`pinned-figures.json`](pinned-figures.json). Rules 1–2 are *enforced* by
   [`lint_consistency.py`](lint_consistency.py) in CI. Run it before you commit:
   `python3 research/manuscripts/lint_consistency.py`.

**Keep it current.** When work lands, update the stage's `[ ]/[~]/[x]` marker in
[THE ORDERED PLAN](#the-ordered-plan-spend-gated--read-top-to-bottom-for-whats-next) **and** the mirrored
`status` in [degrader-paper-schedule.json](degrader-paper-schedule.json) — its milestone `id`s match the
stage tags one-for-one; that JSON is a machine MIRROR of this file, not a competing source.

**Companion docs (detail only, subordinate to this file):**
[pricing.md](../compute/pricing.md) — ★ PRICING single source of truth, every cost line linked to its
justifying test · [bid-strategy.md](../compute/bid-strategy.md) — host selection and bidding ·
[reviewer verdict](nr4a3-degrader-reviewer-revisions-2026-07-15.md) (verbatim) ·
[ternary-first strategy note](nr4a3-degrader-strategy-ternary-first.md) (biological/chemotype rationale) ·
[**ternary-selectivity strategy revision 2026-07-24**](nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md)
(evidence behind the mechanism-first search and the six cost levers) ·
[the manuscript](nr4a3-degrader-paper.md) itself.

Rendered version (mermaid + status colouring): published artifact, regenerated from this file's content.

---

## 0 · How to read this

### 0.1 · Four registers, four questions

| register | the question it answers | where |
|---|---|---|
| **Requirements `R*`** | what must be **TRUE** before the paper can present a candidate | [§2](#2--requirements--what-must-be-true) |
| **Instruments `V*`** | which instrument would answer each requirement, and whether it has itself recovered a known answer | [§3](#3--instruments--which-one-answers-each-requirement) |
| **The roadmap** | what to **DO** next, in what order, and what each item is waiting on | [§10](#10--the-roadmap--one-ordered-list) |
| **The closed-route register** | what must **never** be retried, and what would reopen what is merely parked | [§6](#6--the-closed-route-register) |

Everything else on this page is evidence feeding one of those four.

⚠ **Two things are deliberately NOT a fifth register.** The **options registers**
([§0.8](#08--the-six-options-registers--what-they-own-and-the-one-thing-they-may-never-do)) enumerate what
this program *could* do on five axes; they are inputs to the four above and amend none of them. And the
**framing question** ([§13](#13--the-deliverables-framing--an-open-question-with-a-register-and-no-decision)) — *what is the
paper about* — is an open question of trimcrae's, recorded so it is visible, blocking no row.

### 0.2 · Work state — the five glyphs

★ **A state here is WORK STATUS, not evidence quality (trimcrae, 2026-08-02).** An earlier pass coloured this
page by how good the evidence was, which is a different question and not the one you steer by: a claim can
rest on excellent evidence and still be blocked, and a dead end can be *very* well established. These five
states answer "what should I do about this?" — and every node, row and route below carries exactly one.

| state | glyph | means | what to do |
|---|---|---|---|
| **complete** | ✓ | ran, returned, and the result is recorded in a committed artifact | cite it; don't re-run it |
| **in work** | ◐ | dispatched or building right now | wait for it; don't start a second copy |
| **future work** | ○ | not started, and nothing is blocking it except sequence | this is where new effort goes |
| **parked** | ⏸ | failed with today's tools, but a better tool could change the answer | **name the capability** that reopens it — [method-watch.md](../method-watch.md) |
| **dead end** | ✕ | **conclusively proven unworkable** — no future development reopens it | **never retry** — see [§6](#6--the-closed-route-register) |

⛔ **✕ MEANS CONCLUSIVELY PROVEN UNWORKABLE — NOT "WE TRIED IT AND IT DIDN'T WORK" (trimcrae, 2026-08-02:
*"A dead end should be like, we have conclusively proven that avenue can't work"*).** The test is a single
question: **is there any future development that would make us retry this?** If yes, it is not dead. So ✕
requires positive evidence of impossibility — a structural confound no sample size fixes, arithmetic that
cannot reach the criterion, a premise shown false, an artifact that can never be regenerated. A method that
merely *failed* is ⏸ **parked**, and CLAUDE.md §5 is explicit that parked items are "revisit when capability X
lands", not dead. Conflating the two is expensive in both directions: it buries live options, and it invites
re-running things that cannot work.

⚠ **AND THE TEST IS CONCLUSIVENESS, NOT WHAT KIND OF BOX IT IS.** An earlier version of this page marked the
PAPER node ✕, which was wrong — the paper is blocked, and nothing shows it cannot be written. I then
over-corrected into a rule that claims and goals may *never* be ✕, which is also wrong: **a claim that has been
refuted is dead, and should say so.** The reason [§4](#4--the-dependency-graph)'s graph currently carries no ✕
is not that its boxes are exempt — it is that no claim on it has been refuted. If one is, it gets a ✕ like
anything else.

⚠ **And a ✓ never means "the claim is true"** — it means the *work item* finished. Sequence-only co-folding's
known-answer test completed cleanly and returned a clear negative, which is why it is ⏸ rather than ○: the work
is done, the avenue is not. [§3](#3--instruments--which-one-answers-each-requirement) says what each result
supports.

⛔ **A ◐ IS THE MOST EXPENSIVE GLYPH ON THIS PAGE TO GET WRONG, AND IT HAS BEEN WRONG SEVEN TIMES.** ◐ tells
every reader *"don't start a second copy"*, so a ◐ on something nobody has started is an instruction not to do
the work. That error was found and fixed on the §6 critical path (items 4 and 5) and on Route A on 2026-08-02,
and **five further instances survived that fix on this same page** — the graph nodes `PS`, `LK` and `V3`,
Route B's heading, and branch 1b's three question nodes. All are corrected in this pass and registered in
[§12](#12--findings-that-belong-to-other-documents). **The rule that closes it is structural, not vigilance:**
per invariant 5 below, a ◐ must name the running job, and "nothing is billing" is a $0 observation
(`inflight-board-all.md`, the account censuses) that any reader can take before believing one.

### 0.3 · Three orthogonal axes — WORK STATE, AUTHORIZATION, SUFFICIENCY

★★ **THE FIX THAT THIS PAGE KEPT NEEDING (trimcrae, 2026-08-02: *"If it's the highest leverage, it's the
highest leverage. Don't demote it just because I said not to launch it yet."*).** The work-state glyph above
answers *"what should I do about this?"*. It cannot also answer *"how much would it buy?"* or *"am I allowed
to buy it?"* or *"would it finish the job?"* — and every time this page tried to make one glyph carry all
four, it produced a wrong instruction. The failure is always the same shape: an item that was **not
authorized** got written down as **low value**, because the only column available to record "not now" was the
one that grades importance.

**So a row carries three independent readings, and all three can be true at once:**

| axis | question it answers | values | who owns it |
|---|---|---|---|
| **work state** ([§0.2](#02--work-state--the-five-glyphs)) | what should I do about this? | ✓ ◐ ○ ⏸ ✕ | the committed artifact |
| **authorization** | am I allowed to spend on this? | 🔓 **authorized** · 🔒 **not authorized** · **—** ($0, needs none) | trimcrae, via the [ladder](#11--money-authorization-and-gates) |
| **sufficiency** | if it returned tomorrow, what would it actually discharge? | stated in words, per row — never a glyph | the requirement it feeds |

⛔ **THESE ARE ORTHOGONAL, AND THE PAGE MUST NEVER COLLAPSE THEM.** The canonical row, and the one that
forced the rule, is the **CREBBP/BRD4 selectivity ABFE** (`V4`):

> **highest leverage in the program · 🔒 not authorized · would not discharge the paralogue claim** —
> three true statements about one item, none of which is a reason to soften any other.

- **Leverage is earned, not granted.** It is highest-leverage because this program has **no binary
  selectivity control at all** — [§what the SMARCA2/4 null BINDS](#what-this-binds-in-the-words-fixed-before-the-run) is explicit that *"valA validates
  relative FEP **within one pocket**"* — so it would be the first evidence the free-energy engine can resolve
  selectivity **between two different proteins**, which is the capability every paralogue margin on this page
  presupposes. Nothing about a scheduling decision touches that.
- **Authorization is a scheduling fact, not a grade.** [§the standing tally](#the-standing-tally-this-closes): *"**Neither is
  authorized here**"*. A 🔒 says *don't buy it yet*; it says nothing about what it is worth.
- **Sufficiency is scope, not demotion.** [§what the SMARCA2/4 null BINDS](#what-this-binds-in-the-words-fixed-before-the-run): it is a **binary**
  control and *"would **not** discharge §4's paralogue/ternary statement"*. An item can be the
  highest-leverage thing available **and** insufficient on its own.

⚠ **This is the same class of fix as separating dead from parked ([§0.2](#02--work-state--the-five-glyphs))
and work-status from evidence-quality — the third axis, found the same way, by noticing which two things a
single column was being asked to say.**

**Colour is redundant with the glyph, by design** — every mermaid block below defines the same five classes, so
a state is readable without it: `done` #2f8f5b · `work` #3a63b8 · `next` #8d8674 · **`parked` #6f4a9b (dashed
2 3)** · `dead` #b1543a (dashed 5 3). ⏸ and ✕ are both dashed because both mean *stop here*; the dash pattern
and the hue separate "waiting on a capability" from "never again".

### 0.4 · The ID scheme — `R*` requirements and `V*` instruments

★ **THE THING WHOSE ABSENCE CAUSED THIS MERGE.** Nothing in either document had a stable identifier, so nobody
could write *"R7 is blocked by V4"*. That is **why connections kept being re-derived from prose** and why the
same blockers kept being misattributed — including, twice, the misattribution of a whole route's block to its
instrument when a missing physical term was equally responsible.

- **`R1…Rn` — requirements.** One per claim the paper must establish. **Stable forever; never renumber.** A
  retired requirement keeps its number and is marked retired.
- **`V1…Vn` — verification instruments.** One per instrument, same rule. `V1`–`V4` keep the ids the dependency
  graph already used. ⚠ **`VC` is retired as an id and is now `V5`** — it was the only non-numeric node and it
  meant "Val C", which is [validation requirement 1(C)](#validation-architecture-the-five-requirements);
  the mnemonic is carried in `V5`'s row instead. *Superseded, retained: the node id `VC`.*
- **Every requirement, instrument, roadmap row, closed route and branch cites the `R`/`V` it serves.**
- **A requirement with no `V` is a hole and must render as one.** That is this document's main job, and
  [§2.2](#22--requirements-with-no-instrument--the-holes) is the list.
- **An instrument that has not recovered a known answer cannot raise the confidence of any `R` it serves.**
  This is the program's most expensive lesson, stated as a rule the document can enforce rather than as prose
  — invariant 1 below.

### 0.5 · Six invariants — structural, not stylistic

Each is a rule a reader can *check*, and each exists because it was broken.

| # | invariant | what breaking it looks like |
|---|---|---|
| **1** | **A requirement may never be claimed above its instrument's own validation status.** | an ABFE paralogue margin quoted as evidence while the engine's absolute benchmark misses by more than the whole margin (`V7`) |
| **2** | **Work state, authorization and sufficiency stay orthogonal** ([§0.3](#03--three-orthogonal-axes--work-state-authorization-sufficiency)). | the highest-leverage item in the program written down as low-value because it was unauthorized |
| **3** | **✕ means conclusively unworkable, never "not done yet"; ⏸ names the capability that reopens it; 🔒 names the decision it waits on.** | a held item filed as parked, hiding a decision that could be taken today |
| **4** | **A ✓ is a WORK state, never a claim's truth.** | the pocket node marked ○ (which said nobody had looked, and was false), then marked ✓ *"settled enough to build on"* (which elided two open gates, and was also false). Correct is **✓ work complete · claim supported, not settled** |
| **5** | **Every status cell points at a committed artifact. A cell with no artifact says so, in those words.** | ◐ on a lane that does not exist; a number read once off an artifact's first generation and never re-read |
| **6** | **One fact, one place.** Where this page and an appendix both hold a number, this page **links** and does not restate it. | a cost carried in three files, stale in all three |

⚠ **Invariant 5 is the one that catches the others.** Four of the seven wrong ◐ glyphs, the superseded
thiol-occlusion median, and the superseded pose RMSD were all **values that had a committed artifact and were
never re-read against it**. Checking a cell against its artifact costs $0 and is the single highest-yield
audit on this page.

### 0.6 · ⚠ Five different things in this program are called `R`

**Read this before citing anything as "R-something".** The collision is real, it is repo-wide, and it has
already produced one mis-citation.

| written as | means | home |
|---|---|---|
| **`R1`…`R16`** | a **requirement on this page** — what must be true | [§2](#2--requirements--what-must-be-true) |
| **"validation requirement 1–5"** | the external reviewer's five conditions on what a result may claim | [§Validation architecture](#validation-architecture-the-five-requirements) |
| **"lint rule R1–R5"** | the manuscript language-discipline rule families | [`lint_claims.py`](lint_claims.py), CI-enforced |
| **"Arm R1 / Arm R2"** | the two arms of the NR-V04 retrospective panel (R2 retired by AMENDMENT 3) | [prereg](../modalities/nr4a3-nrv04-retrospective-prereg.md) |
| **`R` (closure)** | the cycle-closure statistic — `R = 0.2128` on the valB triangle, `R = +1.307` on `cycle_3carbonyl` | [`valb-triangle-closure.json`](../modalities/valb-triangle-closure.json), `step1-fanout-map.json` |

**So: never write a bare `RN` for anything except a requirement on this page.** Cite the others in words.

### 0.7 · What machines parse in this file — and what is left in STRATEGY.md

**This page is what you read and steer by, and it is now the whole plan.** Seven CI checks parse it **by exact
heading string and text format**; every one of those headings was carried across from STRATEGY.md unchanged,
so the strings below are load-bearing. ⛔ **Rename one and CI goes QUIET, not red**: renaming the ordered
plan's heading makes [`work_ledger`](../modalities/work_ledger.py) print *"NOT SCANNED — the plan is invisible
this run"* and every open item vanishes from the work board with no error.

| section of this file | owns | parsed by |
|---|---|---|
| [`THE ORDERED PLAN (spend-gated)`](#the-ordered-plan-spend-gated--read-top-to-bottom-for-whats-next) | 30 checkbox items, each with a gate, a price and a marker | `work_ledger.scan_plan_items` — heading string, bullet regex, `###` rung sub-headings, bounded by the next `##`. ⚠ the skipped marker is an **en dash**, not a hyphen |
| [`Spend summary`](#spend-summary) + [`Dependency spine`](#dependency-spine) | the pinned total and its derivation, the rung table, the authorisation graph | `lint_consistency.check_derivations` (the total must appear here, in `pricing.md` and in `bid-strategy.md`) + `check_subsets` (the spine's `Cum ~$N` must be a subset of the plan's `Cum. ~$N` — **two deliberately different formats; unifying them raises `X-pattern-found-nothing` as a CI ERROR, by design**) |
| [`Honest scope and language discipline`](#honest-scope-and-language-discipline-apply-everywhere-including-the-manuscript) | the earned-phrase substitutions and the never-imply set | `lint_claims.py` — **21 provenance strings name this section**, and its R1–R5 rules run over the paper, the SI **and this file** |
| [`📊 WHERE WE ARE — the scoreboard`](#-where-we-are--the-scoreboard-in-plain-language) | the gate table, the deliverables table, realised spend, and ⛔ **the one home for "which controls failed"** | `lint_consistency.check_artifact_figures` (three realised-spend figures must equal `realised-spend.json`); written by `realised_spend.py --write` |
| the whole file | every pinned figure | `lint_consistency.check_superseded` — a replaced value may appear only on a line marked superseded |
| [`Validation architecture (the five requirements)`](#validation-architecture-the-five-requirements) | the reviewer's five conditions; the charge-model lane split; *"Val B-mini is the highest-value dollar in the plan"* | — (content cited by ≥6 modules) |
| [`Open decisions`](#open-decisions) | 15 numbered rulings, all closed | **cited by number in 30 files and nothing resolves a decision number — the numbering is FROZEN** |
| [`Program and thesis`](#program-and-thesis) + [`MECHANISM-FIRST`](#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged) | the thesis, and the one home for the margin arithmetic (`~2.0` needed vs `0.60` resolvable vs `1.543` measured) | `tests/test_selectivity_margin_model.py` asserts the derivation |
| [`The prospective stage…`](#the-prospective-stage-mechanism-first-then-orientation-first-inverse-design) | the kill-switch semantics, the four-tier table, the Tier-2 result in full | `e3_recruiter_staging.py` calls its panel "verbatim" |
| [`Spending rules`](#spending-rules) | no pre-authorization · cheapest-decisive-first · GO/NO-GO per rung · PROJECTED never enters the pinned total | — |
| [`GPU economics`](#gpu-economics-full-provenance-in-pricingmd) | a pointer to [pricing.md](../compute/pricing.md), plus the six cost levers | `bid-strategy.md` names it |
| the ✅/❌ landed-gate blocks | each landed gate's numbers, once | one anchor link from the retired re-panel prereg — ⚠ **that heading's slug is load-bearing and must not change** |
| [`★★ WHAT THE LANDED RESULTS CHANGE…`](#-what-the-landed-results-change-about-the-remaining-plan) | the *why* behind the ordering; its ranked list is folded into [§10](#10--the-roadmap--one-ordered-list) | — |
| [`⏱️ IN FLIGHT`](#in-flight-superseded) | ⚠ **NOT LIVE** — a superseded board plus four one-homes; see [§12 finding 6](#12--findings-that-belong-to-other-documents) | live board is [`inflight_usd_per_ns.py`](../modalities/inflight_usd_per_ns.py) / `inflight-board-all.md` |
| [`🌙 OVERNIGHT MONITORING`](#-overnight-monitoring--what-is-covered-by-what-2026-07-26-trimcrae-asked-for-hourly) | ⚠ stale — every lane it describes has closed | — |
| [`Current front`](#current-front) | ⚠ a duplicate that names its own homes and has **zero** inbound references; superseded by [§10](#10--the-roadmap--one-ordered-list). Retained for one statement: the feasibility panel is **WITHDRAWN**, not merely "under correction" | — |

**And what is left in [STRATEGY.md](../../STRATEGY.md) — history, and only history:**

| appendix | owns | why it is not here |
|---|---|---|
| [`Appendix A — superseded numbers and retracted claims`](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) | the correction ledger — every value this program replaced, beside what replaced it | ⚠ **its rows are read as DATA**: [`realised_spend.py`](../modalities/realised_spend.py) sets `"read_from": "STRATEGY.md Appendix A row 35"`, 35 files cite rows by number, and `lint_consistency.is_cleared` reads **that exact heading** as a structural clear — renaming it turns every row into a CI error. **Row numbers and slug frozen.** |
| [`Appendix B — superseded strategy framings`](../../STRATEGY.md#appendix-b--superseded-strategy-framings) | six retired plan framings | CLAUDE.md §5 points here so a retired framing is never re-litigated |

⚠ **Nothing else is there.** A citation naming any other STRATEGY.md section — the scoreboard, the ordered
plan, the spend summary, open decisions, a landed gate — resolves here, under the same heading and the same
slug.

### 0.8 · The six OPTIONS REGISTERS — what they own, and the one thing they may never do

★ **Added 2026-08-03, wiring in a five-axis fan-out (trimcrae: *"Make sure these are all appropriately
documented in the map as they land."*).** Five agents enumerated, in parallel, the options this program has
on five different axes; a sixth file ranks across them. **They landed beside this page rather than in it,
which is precisely the drift this page exists to prevent** — a fact whose only home is a side file gets
re-derived and then contradicted. Everything each of them *decides* is now in the sections below; this table
is the index, and the pointer for anything they own that this page deliberately does not restate.

| register | the question it enumerates | what this page took from it |
|---|---|---|
| [`selectivity-mechanism-options.md`](../modalities/selectivity-mechanism-options.md) / [`.json`](../modalities/selectivity-mechanism-options.json) | **by what mechanism** could paralogue selectivity be argued — 17 enumerated, 9 previously unrecorded, 7 new measurements | two refutations → [§6a](#6a--dead--conclusively-unworkable-never-retry); one grading downgraded to ⏸ → [§6b](#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen); steric exclusion and its control → [§8](#8--the-two-live-routes-to-selectivity--and-where-each-is-actually-blocked) |
| [`instrument-options.md`](../modalities/instrument-options.md) / [`.json`](../modalities/instrument-options.json) | **by what instrument** — 16 candidates, ranked by whether they need a free-energy resolution at all | the double-difference instrument fact → [§3.4](#34--three-instrument-facts-this-page-used-to-be-missing); `R14`'s hole is ~8/9 filled → [§2.2](#22--requirements-with-no-instrument--the-holes) |
| [`target-route-options.md`](target-route-options.md) + [`target-route-census.json`](../modalities/target-route-census.json) | **must the molecule be paralogue-selective at all** — 13 routes, graded by their effect on the requirement | the requirement is **asymmetric** → [§2.4](#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically); three closures → [§6](#6--the-closed-route-register); the per-domain identity table → [§8 Route B](#route-b--a-linker-borne-covalent-handle-at-an-nr4a3-unique-cysteine---blocked-on-r5-nothing-running--serves-r8-r15) |
| [`nr4a3-short-linker-probe.json`](../modalities/nr4a3-short-linker-probe.json) | **does a construct exist at the 12-atom gate** — the candidate molecule, and what forces the library's floor | the candidate and its two defects → [§5 row R15](#5--where-each-requirement-stands), rung [`5b-T`](#the-ordered-plan-spend-gated--read-top-to-bottom-for-whats-next) arm (C), [§10.1 rows 24–25](#101--open-rows-ordered-by-what-unblocks-the-most) |
| [`paper-framing-options.md`](paper-framing-options.md) | **what else this body of work could publish** — 7 framings on six columns | [§13](#13--the-deliverables-framing--an-open-question-with-a-register-and-no-decision), recorded as open and **not decided here** |
| [`path-family-synthesis.md`](path-family-synthesis.md) | the ranked synthesis across the five | read as a reader's guide; every ranking it states is graded independently below |

⛔ **AN OPTIONS REGISTER AMENDS NOTHING.** None of the six changes a gate, a criterion, a price, a rung, a
status or a claim ceiling, and none is a source of truth for anything this page also carries. **They own
their numbers; this page owns the claim, the state and the pointer** — and per invariant 6 a figure that
appears in both is the bug, not the belt-and-braces. Where a register's grade and this page's disagree,
**this page's grade is the one that binds**, and [§6](#6--the-closed-route-register)'s bar is stricter than
any register's: three of the routes their authors marked closed are ⏸ **parked** here, because *"closed by
the measurements we already have"* is not the same statement as *"nothing reopens it"*.

---

## 1 · The thesis, the north star and the operating regime

*Color, not plan. Everything here has one home in an appendix and is linked, never restated.*

★ **NORTH STAR (trimcrae, 2026-07-01):** the **state of the art of what in-silico can do for an
NR4A3-selective degrader** — the most complete, rigorous, honest computational characterization achievable
with **no wet lab**, every result at its true weight. The paper documents *that*, not a ship-when-adequate
minimum.

★ **THE THESIS** ([§Program and thesis](#program-and-thesis)): close-paralogue
degrader selectivity is created at the **induced target–E3 interface** and in differential lysine geometry —
**not at the conserved warhead pocket** — and in every landmark case it was *discovered then rationalized* by a
solved ternary structure, never predicted blind. AKT1/2/3 is the cautionary null.

⚠ **The thesis and this page's own Route A point in different directions, and that tension is real rather than
an error in either.** Route A ([§8](#8--the-two-live-routes-to-selectivity--and-where-each-is-actually-blocked))
is a warhead-pocket route, and the pocket lining is in fact the most divergent object measured here (7 of 10
lining residues differ). What the thesis contributes is the **size** constraint the route must clear, and it
has one home: the margin arithmetic in
[MECHANISM-FIRST](#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged) —
a useful degradation window needs **~2.0 kcal/mol** of true margin against a best-case **resolvable**
difference of **0.60** and an accuracy of **1.543 kcal/mol, wrong sign**. **A passing selectivity benchmark
would not close that gap**, which is why `R7`'s block is three things and not one.

★ **OPERATING REGIME — one researcher, no wet lab, no race.** A self-funded wet-lab program is off the table,
so every next step is either publish-to-convince or in-silico. **GPU spend is not a gate on paper quality**:
run the warranted experiments — including expensive ones — and post only once that work is folded in. Cost is
a reason to sequence and right-size, not to skip a decision-relevant run. Breadth-first, standard-depth: a new
technique that adds an axis of evidence is a default YES; deepening a test past its field standard is a
default NO.

★ **SINGLE DELIVERABLE:** [nr4a3-degrader-paper.md](nr4a3-degrader-paper.md) + its SI **is** both the ChemRxiv
preprint and the JCIM submission. Language discipline —
[§Honest scope](#honest-scope-and-language-discipline-apply-everywhere-including-the-manuscript),
CI-enforced by [`lint_claims.py`](lint_claims.py) over the paper, the SI **and this page**.

⛔ **This is a long-lived program on a rising frontier, not a one-shot.** Parked items are "revisit when
capability X lands", not dead; completed work is worth re-grading as methods improve
([method-watch.md](../method-watch.md)). Guardrail: a coming capability justifies waiting or re-running,
**never** claiming a result before the method supports it.

---

## Program and thesis

*★ **THE ONE HOME** for the thesis and, in [`MECHANISM-FIRST`](#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged) below, for the margin arithmetic (required vs resolvable vs achieved). [§1](#1--the-thesis-the-north-star-and-the-operating-regime) is the one-paragraph version and carries none of the figures. `tests/test_selectivity_margin_model.py` asserts the derivation.*

The goal is the **state of the art of what in-silico methods can do for an NR4A3-selective degrader** — a
complete, rigorous, honest computational characterization for extraskeletal myxoid chondrosarcoma (EMC, driven by
the **EWSR1::NR4A3** fusion), pursued with **no wet lab**. Every result is reported at its true weight; the
deliverable is a preprint + journal submission (ChemRxiv/JCIM) plus targeted outreach, not a ship-when-adequate
minimum. This program is ≈70–80% of repo effort; the broader EMC route portfolio (fusion-junction ASO and other
routes as support/backup) is context beneath it — see
[emc-treatment-strategy.md](emc-treatment-strategy.md) and [IDEAS.md](../IDEAS.md).

**Thesis.** Paralogue selectivity, where achievable, emerges **jointly** from a modest binary warhead preference,
ternary cooperativity, and ubiquitination-compatible geometry — not from binary pocket selectivity alone. Close-
paralogue degrader selectivity is created at the **induced target–E3 interface** and differential lysine geometry
(as in BRD4-vs-BRD2/3, CDK6-vs-CDK4, p38 isoforms), never at the conserved warhead pocket, and in every landmark
case it was *discovered then rationalized by a solved ternary structure* — never predicted blind. There is no
validated prospective selectivity predictor in the field, and AKT1/2/3 is the cautionary null (isoforms too
homologous → only pan-degraders).

### MECHANISM-FIRST is the search order (the thesis above is unchanged)

Selectivity mechanisms are not interchangeable, and the program was pursuing the hardest one exclusively. Two
classes:

- **MARGINAL** — the paralogue is thermodynamically disfavoured. This is the induced-interface wedge. A useful
  degradation window needs **~2.0 kcal/mol** of true margin (median over 27 potency scenarios, range 1.75–2.25;
  [`selectivity_margin_model.py`](../modalities/selectivity_margin_model.py)), against a best-case
  **resolvable** difference of **0.60 kcal/mol** and a **measured** accuracy of **1.543 kcal/mol, wrong sign**.
  **★★ BOTH HALVES OF THAT SENTENCE CHANGED ON 2026-07-30, IN OPPOSITE DIRECTIONS, AND THIS IS THE ONE HOME FOR
  THE CURRENT PAIR.** ⚠ **Superseded, retained: a resolvable difference of `1.12 kcal/mol` at `replicate SD 0.7,
  n = 3`, beside a *literature* accuracy of ~1.7 kcal/mol RMSE** ([Appendix
  A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 53).
  - **PRECISION improved, because the replicate SD stopped being assumed.** 0.60 is
    `minimum_detectable_difference(0.375, 3)` — **DERIVED, never typed**
    ([`selectivity_margin_model.minimum_detectable_difference`](../modalities/selectivity_margin_model.py))
    off the **measured** cycle SD whose one home is the RUNG 2 · replicates row of the scoreboard. The retired
    1.12 was the same function at **SD 0.7 — a number nothing in this program had ever measured.** Two caveats
    that travel with it and must not be dropped: the SD was measured on the **SMARCA2/VHL** calibrator and is
    *transferred* to NR4A exactly as the cost bases are, and it is an **upper** bound on sampling-only scatter
    because it also carries model-swap and independent-solvation variance
    (`valb_failure_propagation.sigma_leg_now_bounded`).
  - **ACCURACY got worse, and it is no longer a literature figure.** The one known-answer test of this exact
    quantity class missed by **1.543 kcal/mol with the wrong sign**, and `R` localises that to an
    **endpoint-state** error — so replicates cannot touch it.
  - **★ SO THE BINDING CONSTRAINT ON THIS AXIS HAS MOVED FROM PRECISION TO ACCURACY.** The axis is no longer
    "near its resolution limit" — the margin it must detect is now **~3.3× the measured noise floor** rather
    than ~1.8×. What it lacks is a calibrated known answer for the *form* the program actually uses. **This
    axis is an UNCALIBRATED confirmation tool, not a blunt one** — a different defect, with a different
    remedy (a calibrator, not more sampling), and [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan)
    carries what follows from it.
- **CATEGORICAL** — ⚠ **NARROWED 2026-07-25/26 (Lane 13, $0, before any flagship spend): the paralogue is
  structurally incapable *AT THE ALIGNED POSITION* — which is NOT the same as "a covalent bond cannot form on
  it at all", and this file asserted the stronger claim.** The sequence fact is exact and unchanged: NR4A1 and
  NR4A2 carry no cysteine where NR4A3 has C397. **What does not follow is that they present no reachable
  nucleophile.** Three measurements:
  - **Only 4 of NR4A3's 20 enumerated cysteines are unique; 16 are SHARED — and one of the shared ones is
    inside the design gate.** Term (a) is built from `unique_cysteines` **only** and summarises the conserved
    set at the 20-atom *sampling ceiling*, never at the 12-atom gate — so *"all term-(a) basins reach C397 and
    only C397"* (3 of them, post-correction) is a statement about **{C397, C420, C559}**, not about every
    cysteine. Scored over **all** of
    them on the same 75 unbiased conformers, **C496 — whose homologue is NR4A1 C465 / NR4A2 C465 — reaches the
    ≤12-atom gate in 29/75 = 0.387** (Wilson 0.285–0.500). **What closes it is BURIAL (RSA median 0.023), not
    geometry.**
  - **Each paralogue's static opened model presents TWO cysteines inside the same gate**, and **NR4A1 C465 opens
    at a 6-atom linker against C397's 10** — i.e. *more* geometrically accessible than NR4A3's own handle.
    (NR4A1 C551, the celastrol site, at 10; NR4A2 C465 at 10, C534 at 12.)
  - **Matched-construct test** (same placement, warhead exit anchor, E3 anchor and budget; **73,867** placements
    over **300** matched conformers, three scopes): reach-only P(a paralogue Cys is also reached | an
    NR4A3-unique one is) = **0.000–0.003 at 12 atoms, 0.054–0.133 at 16, 0.263–0.383 at 20**
    ([`nr4a-paralogue-dynamics.json`](../modalities/nr4a-paralogue-dynamics.json) →
    `categorical_verdict.by_scope[*].by_linker_atoms`, their one home) — and **16–20 is a range this plan
    already contemplates** (C420 needs 16, C559 needs 20, `best_linker_atoms` reads 19).
    ⚠ *Superseded, retained: the pilot pair "0 at 12 atoms, 0.081 at 16, 0.258 at 20" over 5,657 placements,
    static opened models only — retired 2026-07-26 when the matched ensembles landed.*

  **★ SO WHAT ACTUALLY HOLDS THE CATEGORICAL AXIS UP IS EXPOSURE, NOT ABSENCE.** Every paralogue cysteine in
  range sits at RSA **0.011–0.165** against C397's **0.395**, so reach-**and**-exposure still gives **0
  collisions at every length**. But that is **one number per residue from one conformer**, and RSA is the most
  conformationally variable quantity in play — C397's own range over its ensemble is **0.108–0.673**. The
  matched paralogue MD ensembles that turn those single numbers into distributions are **in flight** and the
  verdict is deliberately marked **`VERDICT_NOT_EVALUABLE`** until they land, rather than reported as a clean
  pass computed against zero paralogue frames. *(Not reimplementation drift: the same pipeline reproduces the
  committed handle-ensemble values exactly — C397 0.960 at the gate, C420 0.000, C559 0.000, RSA median 0.416.)*
  **Consequence for the design: keep the linker SHORT.** The discrimination is clean at 12 atoms and degrades
  measurably by 16–20 — so a construct that reaches C397 at 11 atoms is not merely more tractable, it is
  *more selective*, and any design drifting to 16+ atoms trades away the axis it exists to exploit.

  *(Original framing, retained because the sequence fact under it is exact:)* the paralogue is structurally
  *incapable*. NR4A3 carries reactive residues that BOTH
  paralogues lack, verified from full-length UniProt with two independent aligners
  ([`nr4a_paralogue_unique_residues.py`](../modalities/nr4a_paralogue_unique_residues.py) →
  [`nr4a-paralogue-unique-residues.json`](../modalities/nr4a-paralogue-unique-residues.json)):
  **C397** (NR4A1 N363 / NR4A2 S363; **RSA over a 100-conformer MD ensemble: median 0.416, mean 0.405 ± 0.096,
  p10–p90 0.298–0.510 — the committed single-frame 0.395 sits at the MEDIAN**, so the handle is not a lucky
  frame; reachable at the ≤12-atom gate in **72/75 = 96 %** of unbiased frames. Also NOT geometrically closed —
  it opens at a 10-atom linker on an E3-independent bound, so a term-(a) shortfall is about WHERE RECRUITERS
  DOCK, not about the target. **★ But the chemistry axis is ONE RESIDUE DEEP: C420 and C559 reach the gate in
  0/75 unbiased frames** — C420 needs **16** atoms, C559 **20**, and that contour length is paid out of the
  *same* budget that must span to the E3. **Concentration risk, not fragility**, and there is **no geometric
  fallback**; the untested failure modes are chemical — pKa, nucleophilicity, adduct stability, promiscuity.
  A live failure mode that does **not** fire: pocket-druggability and C397 reach are **independent** —
  P(both) = 0.560 against an independence product of 0.563, and P(reachable | druggable) = **0.955**), C420
  (18.3 Å, exposed), C559 (12.8 Å but RSA 0.095 — buried in this conformer, so not currently tether-reachable);
  and exposed unique lysines **K572** (RSA 0.879, 11.5 Å), **K518** (0.413, 13.4 Å), **K592** (0.506, 16.2 Å),
  all in the same 11–16 Å band as the conserved ones — so an E3 can be steered onto a unique lysine instead of a
  shared one. At **zero** thermodynamic margin these give 0.82 (unique lysine) and 0.92 (covalent capture,
  time-integrating form) on the window metric where the interface-only null gives 0.185. **Precedent: the
  field's one demonstrated case of NR4A-family-selective degradation, NR-V04, is most parsimoniously explained
  by a paralogue-unique cysteine — NR4A1 Cys551, which NR4A3 lacks (T579).** That covalency remains a genuine
  confound for the retrospective (RUNG 4); it is *also* the reciprocal handle this program should use.

The program is therefore **mechanism-first, then orientation**: rank basins by whether they place an electrophile
at an NR4A3-unique cysteine and whether their E2~Ub transfer zone covers a unique lysine rather than a conserved
one; use interface thermodynamics to **rank within** the surviving set, never to create selectivity on its own;
test causality with a matched-pair cycle; and **STOP before the flagship spend if no mechanism survives** —
publishing the honest negative, now stronger because it rules out three mechanisms instead of one. The final
deliverable is a **computationally prioritized, structure-defined, retrosynthetically annotated candidate set
with an identified causal selectivity mechanism — degradation experimentally unvalidated.**

*Checked and reported weak, not quietly dropped:* the EWSR1 moiety of the fusion contributes only **1 lysine**
(residues 1–264, K144) or 2 (1–349) — the low-complexity domain is Lys-poor — so fusion-lysine-directed
ubiquitination is a thin handle and is **not** a design axis. It stays a modelling scenario only.

## Honest scope and language discipline (apply everywhere, including the manuscript)

*★ **THE ONE HOME** for what the manuscript may and may not assert. ⚠ **21 provenance strings in [`lint_claims.py`](lint_claims.py) name this section by title**; renaming or dissolving it invalidates all 21 in a CI-enforced linter. Its R1–R5 rules run over the paper, the SI **and this file**.*

Everything is **conditional on the hypothesized cmpd19 binary pose × the chosen receptor frame** — a *double*
conditionality; a wedge surviving only one poorly-supported pose is penalized or dropped. Right-size every claim:

- "selective hit" → **"predicted selective candidate"**; "NR4A3-selective" → **"predicted NR4A-paralogue-selective"**
- "does bind at all" → **"is compatible with the hypothesized conditional bound state"**
- "recovered degradation" → **"produced a surrogate score concordant with the reported outcome"**
- "synthesis-ready matrix" → **"a computationally prioritized, structure-defined, retrosynthetically annotated
  candidate matrix for synthesis and experimental testing"** (only earned once exact structures/stereochem,
  exit-vector chemistry, routes, building-block availability, and physicochemical assessment exist).
- **Never imply** proteome-wide selectivity, EMC efficacy, safety, a therapeutic window, or clinical readiness.
  The parent cmpd19 study reported transcriptional effects **including MYC induction**, so parent-warhead
  pharmacology is a **potential liability**, not evidence of benefit.
- **Novelty is incremental, not landmark.** All-atom alchemical ternary-cooperativity FEP — the same
  `ΔΔG_coop = ternary − binary` cycle, including VHL–BRD4/MZ1 and paralogue-selectivity applications — is an
  active published area (Chen 2023; *JCTC* 2025 `10.1021/acs.jctc.5c00064` / `5c00736`; *JCIM* 2024
  `10.1021/acs.jcim.4c01227`). The paper must cite and benchmark against this prior art. An open-source
  OpenFE-based implementation + the honest NR4A application is an incremental methods contribution.

Enforcement: [`lint_claims.py`](lint_claims.py) implements rules R1–R5 from this section
against the paper + SI and runs in CI on every push. It is sentence-scoped — a disclaimed use of a regulated
word passes; asserting the regulated claim does not.

---

## 📊 WHERE WE ARE — the scoreboard, in plain language

*★ **THE ONE HOME** for every gate's verdict sentence, the deliverables table, realised spend, and ⛔ **which controls failed**. [§3](#3--instruments--which-one-answers-each-requirement) cites this table and must never restate it. Its realised-spend figures are written by `realised_spend.py --write` and CI-checked against `realised-spend.json`.*

*Read this before the IN FLIGHT table. **Every status line in this file, and every lane report, must be
expressible as one of: a gate PASSED, a gate FAILED plus the remediation, or a DELIVERABLE done.** If a finding
cannot be written that way it is a detail, not a headline. trimcrae, 2026-07-26: "a headline should be
something like *we passed n gates*, or *we failed x gate and need to make y remediation*, or *we have a major
deliverable done*" — internal shorthand like "term (a) went 7 → 0" is **not** a headline, it is the evidence
underneath one.*

**As of 2026-08-02 3:30 AM ET · 7 gates passed · 4 failed · 1 DELIVERED BUT NOT GRADED
(the Step 1 fan-out map; ⚠ and one of its three cycles does not close) · 4 deliverables done and 1 PARTIAL ·
NOTHING BILLING on Vast · realised spend $84.49 machine-ledgered.**

> ### ⛔ THE ONE HOME FOR "WHICH CONTROLS FAILED" — READ THIS BEFORE COUNTING NULLS
>
> **Four results are routinely confused with each other, and three of the four are nulls of some kind.**
> They have DIFFERENT statuses and only two are failures. This table exists because summing them into
> "everything came back null" is a category error §5(b) of the paper explicitly wrote itself to prevent:
> *"without it, a predictable null becomes a verdict on the whole program through a category error."*
>
> | # | what it was | result | status |
> |---|---|---|---|
> | 1 | **valB_mini** — the FEP-side cooperativity calibrator (paper §2.11) | ΔΔG_coop = **−0.599** against a target of **+0.944** — the WRONG SIGN in all three preregistered replicates, ~34× the statistical uncertainty, so systematic and not a sampling deficit | ❌ **CONTROL FAILED** |
> | 2 | **selcal SMARCA2/4** — the endpoint-MD-side sensitivity control (§2.12a) | tier **NULL**, exact one-sided *p* = **0.7468**, **zero** technical failures, reference-set floor 0.00216 vs α = 0.05 | ❌ **CONTROL FAILED**, on an adequately-powered design |
> | 3 | **NR-V04 retrospective** — the biological holdout (§2.12) | tier **DISCORDANT**, *p* = 0.392857 — a NON-RESOLUTION, and covalency-confounded (Cys551 is unique to NR4A1) so it could never have been a positive control at ANY *n* | ⚠ **NON-RESOLUTION**, never a candidate control |
> | 4 | **RUNG 5a-KS** — the causal kill-switch (§2.10e) | **S = −0.1297 ± 0.3264 kcal/mol**, indistinguishable from zero | ✅ **NOT A FAILURE — its PREREGISTERED null**, registered in advance as the LIKELY outcome and explicitly NOT a stop |
>
> **Why #4 is not a failure, structurally and not charitably.** The Tier-3 double difference is an ordinary
> non-covalent alchemical quantity: it models no bond in either leg, so it is **structurally incapable of
> testing the categorical mechanism** the paralogue claim actually rests on. It can only see the *marginal*
> wedge, whose expected size (~0.5–1.5 kcal/mol, one partly-buried hydrogen bond) was registered in advance
> as likely to be unresolvable. It came back as a **BOUND** — excluding ≳ 0.65 kcal/mol at 2σ — because its
> design condition (two seeds per arm) was met.
>
> **What IS bad, and it is #1–#3 together, not #4.** After three attempts there is **no working positive
> control** for selectivity detection, and no fourth candidate is staged. That is why every
> paralogue-selectivity statement in the paper is an **unvalidated prediction** — and it is also what makes
> #4 uninformative *about the method*: an uncalibrated instrument returning zero cannot distinguish "there
> is no wedge effect" from "this method cannot resolve the wedge effect".
>
> ⚠ **#1 AND #2 ARE DIFFERENT INSTRUMENTS** and neither invalidates the other's numbers: #1 is alchemical
> ternary FEP, #2 is endpoint-MD E1. They fail differently too — one gets a known answer BACKWARDS, the
> other cannot see a known difference at all.

*The spend figure's as-of is its artifact's, **11:43 AM ET**, and it has not moved because nothing has billed
since: the last lane came off its host at 5:11 PM ET.*

*That spend figure is **DERIVED, never typed** — it is a reading of
[`realised-spend.json`](../modalities/realised-spend.json), which sums each lane's own rental ledger
(`python3 research/modalities/realised_spend.py`). Two things it deliberately keeps apart. **(a)** A further
**+$48.89 attested** is real money **no machine ledger counts**, because the ternary Vast lane has never had
one — so the ledgered figure is a **FLOOR**, the best estimate is **$133.38**, and the artifact carries the
remediation that deletes the gap. ⚠ **The attested block grew on 2026-07-31 by TWO LEAKS of the same class,
not by new work.** Both are one lane going unwatched, and both are ranges. **(i)** Five `cal-*` bench
rentals were orphaned by the 2026-07-27 re-anchor sweep and ran unnoticed until they were
found and destroyed four days later — one of them `running` at `gpu_util 0.0` for ~3.85 days. Its size is
**a range, $20–$39, and must never be quoted as a point estimate**: no ledger covers those rentals, the
figure assumes continuous running which was never observed, and the hosts are destroyed so it is not
recoverable. The mechanism, which is the durable part: the sweep's ledger stopped at instance 46013005 while
the sweep went on renting, and `vast_idle_guard` is LABEL-SCOPED — a lane that stops being dispatched stops
being guarded, and nothing said so. One home for all of it:
[`realised_spend.ATTESTED`](../modalities/realised_spend.py) → `vast_bench_sweep_orphans`.
**(ii)** The NR-V04 retrospective's one genuine Arm E host (instance `45749905`) was rented **6:59 PM ET Fri
Jul 24** and not destroyed until **6:59 AM ET Fri Jul 31** — **156.0 h of rental against a leg that computed
for 1.04 h**, because nothing dispatched that lane's collect for five days. Its size is likewise **a range,
$6.68–$25.83**: the span and the rate are both measured from the instance's own record at reap, but the host
was last seen `exited` after a container start failure, so whether the meter ran for the idle ~4.8 days is
not recoverable now the host is gone. One home:
[`realised_spend.ATTESTED`](../modalities/realised_spend.py) → `nrv04_retro_orphan`; the field that
hid it (`uptime_s` is **billed rental time, never leg time**) is pinned by
[`tests/test_price_ledger_uptime_semantics.py`](../modalities/tests/test_price_ledger_uptime_semantics.py).
⚠ **The jump from $24.46 is a BOOKKEEPING correction, not new spending:**
the step-1 fan-out's ledger lives on the branch that lane runs from, so `main` had been summing a copy that
stopped at 86 rentals while the real one held 197. The money was spent days ago; `main` could not see it.
Superseded pair registered in [§Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 46. **(b) GCP trial credit is a SEPARATE LEDGER and is never summed into
either** (CLAUDE.md §6): it buys wall clock, not headroom. `lint_consistency.py` rule A now holds this line
to the artifact, so the figure cannot drift back into prose. **Superseded, retained: `$0.74 spent`** — a
hand-carried total that stood while the fan-out lane alone had realised twenty times it
([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 39).*

| # | gate | status | what it means in one line |
|---|---|---|---|
| Tier 0 | categorical-axis screen | **PASSED — and now TESTED against paralogue DYNAMICS** | NR4A3 has chemistry the paralogues lack. The narrowing stands (the axis survives on **exposure**, not absence) and LANE 13 has now shown that exposure holds across 300 matched conformers: where the construct reaches an NR4A3-unique cysteine, **no EXPOSED paralogue cysteine is reachable in any scope** |
| Tier 1 | differential surface atlas | **PASSED** | there is a surface to steer an E3 against |
| Tier 2 | basin nomination | **PASSED** — *the covalent limb is no longer under review; it CLEARS* | at least one way to build a selective degrader exists, and the corrected geometry leaves **both** routes open — the covalent one included. It was briefly recorded here as possibly closed; the authoritative corrected+matched run says otherwise, and the block below carries the numbers |
| RUNG 1 | accuracy control (valA_mini) | **PASSED** | our binary free-energy pipeline reproduces a known answer |
| RUNG 2 | cmpd19 pilot | **PASSED** | the pipeline converges on the real target system |
| RUNG 2b | 4 fs speed test | **PASSED — both stages** | every future simulation ~1.56× cheaper. The full cycle reproduces the 2 fs answer to **0.0215 kcal/mol** against a 0.7 tolerance; adopted provisionally at one seed (no replicate-SD). **System identity is now MEASURED and passes** — same alchemical system per arm, the leftover particle-count difference is bulk solvent — but the two arms are independent cross-lane builds, **not** one system with only the timestep changed ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 45) |
| RUNG 2 · closure | **cycle closure — fwd/rev hysteresis** | **PASSED (2026-07-27)** | the calibrator's ternary leg closes on itself, comfortably inside its preregistered ceiling. First time the criterion had both its inputs; a PATH-CLOSURE check, not an accuracy one, so it does not touch the wrong-sign FAIL below. **The numbers live once**, in the §THE FIRST FORWARD/REVERSE HYSTERESIS block below — this row deliberately does not restate them |
| RUNG 2 | **calibration benchmark (valB_mini)** | **FAILED** | wrong sign, and provably **not** fixable by more replicates. **Remediation:** replacement design drafted → refuted by its own free pre-check → second replacement specified at **~$7**. ⚠ **The 4 replicate legs now running do NOT convert this to a PASS** — see the row below |
| RUNG 2 · replicates | **valB_mini r1+r2 — is the FAIL quantified?** | **GATE FAILED, AS PRE-REGISTERED — and it is now quantified.** All 4 legs landed 3:07 AM ET Jul 30; the reduction ran at n=3 | **FAIL on the SIGN, before the replicate SD is ever consulted**: per-replicate ΔΔG_coop = −0.5125 / −1.0097 / −0.2749, mean **−0.599** against a known target of **+0.944**, abs error **1.543** on a 1.0-pass / 2.0-fail band. The decision is **NO-GO** — *"CI is entirely NEGATIVE (−1.103..−0.095) — method resolves the WRONG sign of cooperativity"* · **The durable deliverable is the replicate SD: 0.375 kcal/mol**, against per-leg MBAR SEs of 0.097–0.132 — roughly 3×, which is direct evidence for the paper's standing rule that a within-run MBAR SE speaks to precision and never to reproducibility · ⚠ **One open item for trimcrae, not decided here:** the reduction flags system identity INCONSISTENT because the ternary arm disagrees with ITSELF across seeds (r1 144,447 vs r2 141,740 particles, and binary 90,324 vs 90,720). That survives the 2026-07-30 fix that stopped the check comparing the ternary arm against the binary arm — a comparison meaningless by construction. Whether independently-solvated replicates may differ in water count, and what that does to a replicate SD, is a scientific call |
| RUNG 3 | **NR-V04 covalent feasibility** | **FAILED** | inputs never placed the warhead near its target site. **Remediation:** covalent legs **retired**, panel re-scoped to non-covalent. **~$6–8 not spent** |
| RUNG 4 | **NR-V04 retrospective** | **RAN, AND ANSWERED: Arm E / R1 completed 16/16 and the frozen gate emitted `DISCORDANT`** | The one home for the result is [`nrv04-retro-verdict.json`](../modalities/nrv04-retro-verdict.json); its three preregistered secondaries are [`nrv04-retro-secondaries.json`](../modalities/nrv04-retro-secondaries.json), and both are written up in the paper §2.12 / SI §S12. **What the rung buys is now known and it is a negative:** the retrospective **was** the positive control for paralogue-selectivity detection and it did not resolve, so no selectivity claim in the paper may lean on it. ⚠ **SUPERSEDED, retained — this row previously read "FAILED (blocked) … HELD pending re-check … no verdict stands".** That was true of the 2026-07-31 state and is not true now: the two bugs were fixed and one arm retired *before* the panel ran, and the hold-breach it describes (17 inadmissible smoke legs, $0.75, Appendix A row 57) was withdrawn in full and is a different event from the 16 real legs that later landed. **~$23 of the rung still not spent** |
| RUNG 4 · Step 1 fan-out | **19 congeneric RBFE edges** (LANE 17/21) | **COMPLETE — the lane closed itself at 9:24 PM ET Jul 29 (`pending=0`, `live=0`, every unit carrying a `ddg.json` or on the blocked list). The MAP is delivered; the GATE on what it means is a separate judgement and is NOT claimed here** | **18 edges complete of the 18 computable**, in a 19-edge map, for **$73.79** against a derived authorisation ceiling of $74.91 · **1 edge permanently BLOCKED** (`cw_bio_nmethyl_amide` — no mapper reaches the 20-atom provable floor, measured identical at t20 and t300, so more search time cannot fix it; and the one map that does reach 19 gets there only by mapping a carbon onto a hydrogen, which is the degenerate correspondence the floor exists to reject) · **the edge that was held on a FIXED DEFECT has since LANDED** (`cw_bio_primary_amide`, +0.935 ± 0.500 kcal/mol — two atoms of the staged hybrid system sat at exactly the same coordinates carrying a gradient 7.7e11 times the largest force on any other atom in the box; finite, so the CPU minimiser survived it and every GPU did not. Displacing one by 0.01 A removed it and changed nothing else to six significant figures. It burned 25 rentals on 7 cards before anyone counted the attempts; the de-degenerated geometry reached the execution hosts and the edge computed) · **15 of the 18 are anchor-rooted** and are the only ones readable as tighter-or-weaker than cmpd19; the other 3 join two analogues and close cycles. **The honest denominator is 18 computable edges of a 19-edge map**, derived in `step1-fanout-map.json` (`n_computable`), never typed — and the ranked table is built from that file's `ranking` field, which is restricted to anchor-rooted edges for the reason recorded in the paper's Appendix A · ⚠ **AND ONE OF THE THREE CYCLES DOES NOT CLOSE — a MAP-QUALITY caveat that was landed with the map and had reached no document until 2026-07-30.** `cycle_exitvector_aniline` **R = −0.726** and `cycle_exitvector_ether` **R = −0.756** are inside the ±1.0 tolerance; **`cycle_3carbonyl` sums to R = +1.307 → VIOLATION**. The artifact's own rule is that an open cycle means at least one of its edges is unconverged or mis-mapped, so **the three edges of that loop** (`cw_ms_free_acid` +0.136, `cw_bio_primary_amide` +0.935, `cw_ms_free_acid → cw_bio_primary_amide` +2.106) **carry that reservation wherever they are quoted**. R is a property of the loop and does NOT name the guilty edge; at one replicate per edge it also cannot be separated from three unlucky single draws, which is the same want-of-replicates limit as everywhere else on this lane. Numbers live once, in `step1-fanout-map.json` → `cycle_closure` |

| deliverable | status |
|---|---|
| **The virtual linker library**, chemistry-verified end to end — **54 constructs (36 exemplar + 18 representative), RDKit-verified 54/54**, counts derived from `nr4a3-linker-design.json` → `library_summary` | **DONE** ($0). ⚠ **Superseded, retained: "21 candidate molecules"** — that was the pre-wedge-fix enumeration and it contradicted this file's own library line ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 48) |
| **The matched molecule pair for the decisive causal test** | **DONE** ($0) — that test could not be run at all before 2026-07-26 |
| **The ranked congeneric ΔΔG map** — 18 computable RBFE edges, the paper's §2.9 | **DONE** (2026-07-29, `$73.79` — inside the derived `$74.91` cap). ⚠ **One of its three cycles does NOT close** — the fan-out row above is the one home for that caveat |
| **The generation-matched null** — the winner's-curse / generative-confound control on the de-novo funnel | **PARTIAL, and the partiality is the point ($0).** The **scrambled-objective** arm has run and manufactured **0 survivors of 191** against the real campaign's 1 of 191. ⚠ **That does NOT exclude the confound and must not be quoted as if it did:** zero events in 191 generations bounds the manufactured rate at **≤0.0157 (95 %, rule of three)**, **3× the real campaign's own 0.0052**, and Fisher for 1/191 vs 0/191 gives **p = 0.5**. The artifact's earlier `p = 0.0 / enrichment = ∞` came from reading a zero point estimate as a measured zero and is retired in place in its `_superseded` block ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 52). **The arm that actually addresses the GENERATIVE step — a fresh generation into a paralogue pocket — is UNRUN**, and it is the cheap next thing this control needs |

**Nothing on this board is waiting on trimcrae.** The question that used to sit here — whether the covalent
design route still has candidates — was answered by the corrected+matched Tier 2 run: it **clears**, and the
Tier 2 row above is the one home for that status. (Retained as a heading only because it was quotable; see
Appendix A.)

---

### ✅ PASSED — the covalent design route clears the gate. **3 basins, not 0, and not "missed by one atom".**

⚠ **This block previously read "it missed the gate by ONE ATOM" and that was WRONG — my error, corrected
2026-07-26.** I read a **superseded artifact** and reported its numbers as the corrected result.

| run | samples | runtime | term (a) | term (b) | nominal |
|---|---|---|---|---|---|
| published, pre-correction | 10⁶ | 4294.9 s | **7** | 40 | 28 |
| *what I quoted* — corrected but **under-sampled** | **250 000** | **1082 s** | **0** | **31** | 27 |
| **corrected + MATCHED — authoritative** | 10⁶ | 4303.6 s | **3** | **40** | **28** |

**The signal I missed was sitting in my own table: term (b) had moved, 40 → 31.** Term (b) is computed from
the lysine transfer zone and is **untouched by the reach rule** — it had no business changing at all, and its
movement was proof the run was not comparable rather than merely corrected. I checked provenance on *scope*
(12 poses, 192 basins — which matched) and never on **sample count**, where the 4× runtime gap was visible.
The matched run reproduces published term (b) **and** the nominal limb **exactly**, so only term (a) moved and
the comparison is genuinely rule-attributable. Confirmed-basin patches match at Jaccard **1.000**.

**So the corrected result is 7 → 3, and the gate PASSES.** Three basins clear the preregistered **12-atom**
gate: **`vhl|M2` at 10 atoms** (reach fraction 0.057), **`vhl|M3` at 11** (0.021), **`crbn|M17` at 12** (0.045,
term-b 3.87×). Shortest reach per residue is **C397 10 · C420 16 · C559 27** — *not* the 13/16/31 I reported.
And nothing is rescued by a newly-invented surface: **`crbn|M17` matches `crbn|M0`** — the strongest
nomination — at Jaccard exactly **0.600**, i.e. the gate-passing CRBN placement sits on the strongest basin's
own surface. (`crbn|M0` itself reads 13 and does miss by one.)

**The gate was never moved, and did not need to be.** The design consequence from the collision profile still
stands and is the durable part: reach-only collision is **0.000–0.003 at 12 atoms, 0.054–0.133 at 16 and
0.263–0.383 at 20** across the three matched scopes
([`nr4a-paralogue-dynamics.json`](../modalities/nr4a-paralogue-dynamics.json) →
`categorical_verdict.by_scope[*].by_linker_atoms`, their one home), so every extra linker atom is a
*selectivity* cost, not just a synthesis cost.
⚠ *Superseded, retained: "0 collisions at 12 atoms, 0.081 at 16, 0.258 at 20" — the 5,657-placement
static-model pilot, retired 2026-07-26 by the matched ensembles. Same direction, steeper, and not zero at 12.*
**The honest cut-off is the 12-atom gate itself**, because under the landed ensembles 12 is the only length at
which any scope reads a zero. It is **not** made a gate, for one remaining stated reason: reach-**and**-exposure
is ~0 at every length, so above 12 the axis rests on **burial** rather than on distance — and burial is
adjudicated by `EXPOSED_RSA = 0.25`, which fails its own positive control.
⚠ *Superseded, retained: "the honest cut-off is 14 backbone atoms — the longest length at which reach-only
collision is a measured zero", and the second reason given for not gating, "no enumerated molecule reaches 12
(the shortest is 14)".* **One does** — see
[`nr4a3-short-linker-probe.json`](../modalities/nr4a3-short-linker-probe.json), which enumerates the committed
grid against all three gate-clearing basins and is the one home for what exists at 12 and what forces the
library's floor of 14.

### Library and matched pair — one real defect found and fixed

**The library survives the reach correction with ZERO casualties**, and **no construct ever
"worked" because of the pendant-credit bug** — re-enumeration returns every construct field-for-field
identical. *(It was a 21-construct library at that point; the count is now 54 and the superseded value is
[Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 48.)* The
reason is structural: 5b's enumerator always used the exact three-ball kernel, which pre-dates the correction;
the bug lived in `basin_geom.linker_can_visit`, consumed only by the basin search.

**But the recommended pair's molecules were built for the WRONG RESIDUE.** The preregistered wedge rule
(*NR4A3 must present a donor, both paralogues must not*) was enforced in `matched_pair()` but **not** in
`enumerate_library()`. The record read `wedge_target_residue: T407` while its own d/d₀ carried
`branch_target: C397` — **Asn in NR4A1, Ser in NR4A2, so BOTH paralogues keep an H-bond partner**: exactly the
"S ≈ 0 by construction" trap the rule exists to prevent. The two selections disagreed on **8 of 10** records.
Fixed with one shared `select_wedge_site()` plus a refusal when emitted molecules don't match the reported
site. Cost: 12 constructs. **Library is now 36 exemplar + 18 representative, RDKit-verified 54/54.**

**The pair stands; the shared-LENGTH reading does not.** `crbn|M0` exemplar, 3-(3-pyridyl)-L-Ala vs L-Phe at
**Thr407**, **19 backbone atoms**, **9.04 Å** E3 clearance, 64 heavy atoms, one aromatic C–H→N — every
preserved property re-measured rather than asserted. But on that placement the covalent series sits at 14 and
the wedge pair at 19, and **no single construct carries both.**
**★ THE REASON WAS MEASURED 2026-07-30 AND IT IS NOT THE ONE THIS BLOCK CARRIED.** ⚠ *Superseded, retained:
"a single chain carrying both needs 16, and the segment grid cannot build it (branch floor k=6 against T407's
k∈[2,3] at n=16) — a grid limit, not geometry"
([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 55).* Run against the committed
enumeration, **every clause of that except the branch floor is false**: the grid builds T407 branches at
n=16 **and** C397 branches at n=16, at three shared lengths (16, 18, 20); and **no recorded T407 window is
k∈[2,3]** — the real ones are k∈[2,6] and k∈[4,13], and the enumerator builds inside them. **The blocker is
that `build_smiles` takes ONE `pendant`** — its template has a single branch residue, so no choice of
segments, length or placement can emit a two-mechanism molecule, because there is no second slot. The floor
`k = 3 + SEG2 + tail` is real but **architectural** (the 3 is the branch residue's own N–Cα–C) and no grid
change reaches below it. **What would work is a two-branch template, constructible at n = 18 with the
segments the grid ALREADY has** — so the fix was never a re-grid. Derived, never typed:
[`linker_branch_reach.py`](../modalities/linker_branch_reach.py) →
[`linker-branch-reach.json`](../modalities/linker-branch-reach.json).

---

### 🌙 OVERNIGHT MONITORING — what is covered by what (2026-07-26, trimcrae asked for hourly)

**Three layers, and they cover different things. Stated explicitly because assumed-but-absent coverage is
exactly how `ternary-leg-watchdog.yml` sat UNPARSEABLE for days while everyone believed it was watching.**

| layer | covers | acts autonomously? | verified |
|---|---|---|---|
| `ternary-vast-watchdog.yml` (cron) | the **4 valB_mini replicate legs** (`edge_reps`), which are what is enabled now. ⚠ **NOT the 2 RUNG 5a-KS legs any more** — those are PARKED (`enabled: false` + `_parked_why`) because a relaunch is a new purchase the price gate refuses; and **not** the 4 RUNG 2b legs, which landed | **YES** — relaunches a DIED leg from its last checkpoint; a STALL alerts but does **not** relaunch, because a relaunch would hang the same way and pay for it again | **Exercised repeatedly through 2026-07-27**, including the correction that a leg whose GPU has been reclaimed reads `stopped_and_billing` rather than "advancing". ⚠ **The delivered cron interval is MEASURED, not assumed, and it is not the interval the cron asks for** — [`fleet-supervision-alarm.yml`](../../.github/workflows/fleet-supervision-alarm.yml) is its one home; do not quote a remembered gap here (CLAUDE.md §6) |
| hourly routine → this session | **everything**, incl. the 2 paralogue MD legs, the valB reverse leg, and Lane reports | no — it wakes an agent to judge | fires hourly, persists server-side, survives container restarts |
| `vast-watchdog.yml` (cron) | **any Vast job kind the engine implements** — currently the **2 paralogue MD legs** (`paralogue_md`) and, by construction, `ternary` | **YES** — relaunches a DIED leg from its checkpoint, capped per UTC day, and **withholds** the relaunch while the lane's own workflow is in flight; STALL/FAILED alert but never relaunch | **Exercised live 2026-07-25 10:00–10:05 PM ET** against both legs: verdicts RUNNING, state written and read back (`prev=1014350`, `stall=1` on a frozen tick, `stall=0` on an advance). Merged to `main` 2026-07-26 |
| `vast_idle_guard.py`, acting **from CI** | **all** Vast spend | **YES** — destroys a box that is up and producing no evidence of work (log silent, or restart churn) in ~15 min. Its one inviolable rule: **GPU idleness NEVER condemns a box**, only a measured absence of *writes*, so a legitimately CPU-bound staging phase is safe | ⚠ **This row previously credited the `autoteardown` wrapper with "guaranteeing no idle-GPU billing anywhere". That was FALSE and is retired** (measured 2026-07-27, pinned by `tests/test_vast_idle_guard.py`): an unprivileged container **cannot end itself** — `kill -9 1` returns success while being ignored — so the EXIT trap stops the JOB, not the METER, and a crash-looping container never returns at all. Two 5a-KS legs billed ~53 min at `gpu_util: 0.0`. The guarantee is the CONTROL PLANE's, never the host's |

⚠ **RESOLVED 2026-07-26 — the 2 paralogue MD legs ARE now covered by a cron watchdog**, and the gap had a
**proven cause, not a suspected one.** `vast_watchdog.py` is a **kind registry** over the single shared policy
in `watchdog_policy.py`, which `ternary_vast_watchdog.py` **re-exports** — a test asserts
`tvwd.classify is wp.classify is vw.classify`, so the two monitors cannot drift into disagreeing about whether
a leg is dead. A kind the engine does not implement is **refused at validation time, loudly, aborting the
pass** — never silently skipped. The ternary list is untouched and takes the identical legacy code path.

**Root cause of the outage, from the log rather than inferred:** LANE 13's own long-running watch **died at
8:28 PM ET** on `['nr4a-pdyn-nr4a2-smoke'] made no progress for 8 ticks` — a leg that was **never launched**,
whose signature `(None, None, False)` can never change — **while both real legs were advancing at 60–69 % GPU
utilisation.** `leg_names()` synthesises a `-smoke` name per target regardless of whether one exists;
`real_done` excluded smoke legs and **the stall test did not**. That asymmetry was the whole bug: **a phantom
entry took the monitoring down and left two billed legs uncovered for ~1.5 h.** Fixed
(`watched_for_stalls()`), and the new engine **refuses to watch a smoke leg at all** rather than inherit the
failure mode.

**One trap worth keeping:** the `paralogue_md` progress scalar is `phase_rank × 1e6 + milli-ns`, because the
job's own `done_ns` **resets to zero at the metad→release boundary** — a raw counter would read a healthy
phase transition as a 60 ns regression and stall-alert a good leg.

**✅ `DIED → relaunch` IS NOW PROVEN LIVE, autonomously, on a real leg (2026-07-26 1:42 AM ET).** The
`schedule` pass at that time — not a dispatch, and with no session driving it — found `nr4a-pdyn-nr4a1` with
**no result and no instance**, classified it `DIED`, rented **45878836** on machine 17720 (attempt 1/6 for the
UTC day) and the leg **resumed from its own checkpoint at 33.55 ns** rather than restarting. That is the
watchdog's real success terminus for the recovery path, witnessed end to end, and it happened while the lane's
own watch had been dead for ~5 h — which is precisely the failure this engine was built for.

**Still not proven live:** `FAILED` and the `STALL` escalation. Proving them needs a leg that crashes with a
recorded reason or freezes while alive, and a billed one was not killed to get it; they rest on unit tests plus
the fact that they share `classify()` with the path above.

---

## ✅ LANE 13 — DOES THE CATEGORICAL CASE SURVIVE PARALOGUE DYNAMICS? **YES.** (2026-07-26 2:49 PM ET)

*★ **A LANDED GATE.** Evidence under Tier 0; the one home for the exposure-not-absence narrowing across ensembles. Registers: instrument `V17`, requirement `R8`.*

The assumption Tier 2 passed on was never that NR4A3's cysteines are unique — that is a sequence fact and was
never in doubt. It was that a paralogue does not present some OTHER nucleophile that the SAME linker path
reaches. A degrader does not care which cysteine it labels. That had only ever been checked on one static
conformer per paralogue; this lane checked it on **300 matched conformers** (NR4A3 / NR4A1 / NR4A2, 100 each:
25 metadynamics + 3 × 25 unbiased release) against **73 867 matched E3 placements**.

**P(no paralogue cysteine reachable | the construct reaches an NR4A3-unique cysteine)**, at the preregistered
**12-atom** gate:

| scope | all cysteines | **solvent-exposed only** (RSA > 0.25) |
|---|---|---|
| static opened model | 1.000 | **1.000** |
| **unbiased release ensemble** | 0.99876 | **1.000** |
| metadynamics (biased) | 0.9971 | **1.000** |

**On exposed cysteines the answer is exactly 1.000 in every scope** — `mean_P_any_EXPOSED_cysteine` is **0.0**
for NR4A1 and **0.0** for NR4A2 throughout. The small non-zero co-labelling on the all-cysteine measure
(0.12–0.29 %) is entirely on **buried** paralogue cysteines, which is reachability without labelability.
NR4A2 is essentially absent on every measure (1 × 10⁻⁶ to 7 × 10⁻⁶).

⚠ **STATE IT AS THE RARE-EVENT STATISTIC IT IS.** The conditioning event is thin by construction: a matched
placement reaches an NR4A3-unique cysteine in **~0.04 %** of placements, i.e. **122 hit placements out of
73 867** in the unbiased ensemble. That is what the 2 000 000-sample setting was bought for — 500 k gave
single-digit events — but 122 is a small denominator and the ratio should not be quoted to five figures as
though it were tight. **The defensible claim is the EXPOSED column: zero paralogue co-labelling events, not a
probability estimated near one.**

**Limits, from the artifact's own `_limits`:** reachability and exposure are necessary, not sufficient — no
thiol pKa, nucleophilicity, adduct stability or promiscuity is modelled; each species' conformers are
correlated within a replica, so the effective n is smaller than the frame count; and paralogue conformers are
superposed into the NR4A3 reference frame, carrying a per-frame core-fit residual.

---

## ✅ RUNG 5a-KS LANDED — the causal kill-switch returns its **preregistered null**, S = −0.13 ± 0.33 kcal/mol (2026-08-02 2:15 AM ET)

*★ **A LANDED GATE.** The one home for `S` and its bound. Registers: instrument `V16`, requirement `R11` — and ⛔ `V16` has no known-answer calibrator, which is [§10 row 11](#101--open-rows-ordered-by-what-unblocks-the-most).*

**Headline in the required form: a DELIVERABLE done — the paper's own stated limit *"the causal test has not
been run"* is retired — and the gate returns the outcome it registered as LIKELY, which is explicitly NOT a
stop.**

All four legs landed (n = 2 seeds per arm). Every figure's one home is
[`nr4a3-5aks-reduction.json`](../modalities/nr4a3-5aks-reduction.json):

| | |
|---|---|
| **S** = ΔG_tern(NR4A3) − ΔG_tern(NR4A1) | **−0.1297 ± 0.3264 kcal/mol** (replicate SD, n = 2/arm) |
| NR4A3 arm | mean −10.9439, replicate SD 0.2354, mean MBAR SE 0.0753 |
| NR4A1 arm | mean −10.8142, replicate SD 0.2261, mean MBAR SE 0.0860 |
| reading (fixed in advance) | **S ≈ 0 → the marginal wedge is absent.** Registered as the LIKELY outcome and NOT a stop |
| what it bounds | the design could only resolve **\|S\| ≳ 0.65 kcal/mol** (2σ); it did not |

⚠ **THE ERROR IS THE REPLICATE SD, NOT THE MBAR SE** — the latter is ~0.08/arm, threefold smaller, and
quoting it would understate the uncertainty by exactly the factor the ABFE error-bar standard exists to stop.

**Staging was VERIFIED, not assumed, because one specific defect counterfeits this exact result.** A one-chain
"ternary" leg is a binary leg nobody labelled and would also give S ≈ 0. Both arms check out identically
against their committed manifests — chains `A` (254 res, the NR4A LBD) + `B` (442 res, CRBN) + ligand chain
`L`, with `protocol_hash`, `charge_method`, `setup_cache_version` and `n_windows` agreeing across all four
legs. The trap did not occur.

**Three limits, each able to hide a real effect:** the reducer flags `n_particles` disagreeing across arms
(NR4A1 ≈ 210k vs NR4A3 ≈ 148k — the solvated BOX, not the composition, so size-dependent systematics do not
cancel, which is the one thing a double difference is supposed to buy); the geometry is a **Boltz-2
prediction**, so S is pose-conditional; and ⛔ **the instrument has a failed calibrator** — §2.11's
known-answer benchmark misses with the wrong sign, systematically. **An uncalibrated instrument returning zero
cannot distinguish "no wedge effect" from "cannot resolve the wedge effect",** and it is not reported as
though it could.

⚠ **DO NOT CONFLATE THIS WITH THE SENSITIVITY-CONTROL NULL BELOW.** They are different instruments with
separate failed controls: this is **alchemical ternary FEP** (its calibrator is valB_mini, §2.11, wrong sign);
that is **endpoint-MD E1** (its calibrator is the SMARCA2/4 panel, NULL). Neither result invalidates the
other's numbers, and reading them as one finding would overstate both.

Documented at paper **§2.10e**, with §2.10(d) and the §2.10 closing paragraph re-written from "has not been
run" to "has been run and is NULL".

---

## ❌ GATE FAILED — the SMARCA2/4 sensitivity control returns **NULL** on an adequately-powered design (2026-08-02 10:42 PM ET)

*★ **A LANDED GATE.** Registers: instrument `V11`, requirement `R11`. ⚠ **This heading's slug is load-bearing** — it is the target of the repo's only non-Appendix-A anchor link (`nr4a-repanel-prereg-DRAFT.md:9`) and must not change.*

⚠ **CORRECTION, 2026-08-02 — THE TIMESTAMP IN THE HEADING ABOVE IS WRONG BY A CALENDAR DAY, AND THE HEADING IS DELIBERATELY NOT EDITED.** The verdict's own record is `selcal-verdict.json` `utc: "2026-08-01T02:43:16Z"`, i.e. **2026-08-01 10:43 PM ET**. Root cause, read from the data rather than guessed: **the clock face was converted and the calendar date was not** — `02:43 Z → 10:43 PM` is the correct 12-hour conversion, but the date must roll back from 08-02 to 08-01 and did not (the minute is also off by one). The heading keeps the incorrect stamp because changing it changes the slug the anchor link above depends on. **Superseded, retained: `2026-08-02 10:42 PM ET` as this gate's time.**

**The headline, in the required form: a gate FAILED, and the remediation is that there is none to buy — step 3
is not purchased and the paper's language changes instead.**

This was the **method calibrator** that Open decision 9 named as the program's real gap and that RUNG 3 module 3
adopted on 2026-07-24: the one experiment meant to show that this workflow can discriminate paralogues where
the answer is already known. It has now been run end-to-end and **it did not detect the difference.**

Every figure below has **one home**, [`selcal-verdict.json`](../modalities/selcal-verdict.json), and is
read from it rather than typed:

| | |
|---|---|
| tier | **NULL** — a real negative, reported as one |
| statistic (mean SMARCA2 − mean SMARCA4, model-level E1 plateau) | **+0.4373 Å** (4.9684 vs 4.5311) |
| direction | ⚠ **opposite** to the primary source's prediction, and **all 11 LOMO refits keep that sign** |
| exact one-sided *p*, predicted direction | **0.7468** |
| mirrored *p* | **0.2554** — so NOT WRONG_SIGN either |
| reference set / floor | **462** arrangements, min attainable *p* **0.00216**, α = 0.05 |
| technical failures | **0** in each arm |
| admitted legs / models | **22** legs, **6 vs 5** models |

⚠ **THE DESIGN WAS ADEQUATELY POWERED BY ITS OWN FROZEN CLAUSES — this is not an underpowered miss.** The
reference-set floor is an order of magnitude under α, there were no technical failures, and the panel cleared
the per-arm model floor. The test could have returned significance and did not. That is a **worse** outcome for
the program than RUNG 4's DISCORDANT, which was a non-resolution rather than a negative.

**Two of the 24 designed legs were excluded before scoring, on a MEASURED INPUT FAULT and never on an outcome**
— SMARCA4 seed 3 places two heavy atoms **0.693 Å** apart against a 1.00 Å floor, so the pre-MD audit refused it
reproducibly on five machines before any dynamics existed. The other unfinished unit at that moment audited
**clean at 1.2994 Å** and was **re-run, not excluded**. Full standard and evidence:
[prereg AMENDMENT 1](../modalities/selectivity-sensitivity-control-prereg.md#amendment-1--2026-08-02-measured-input-fault-smarca4-model-3).

### What this BINDS, in the words fixed before the run

The consequence is not being invented now — it was written into
[`selectivity-resolution-options.md`](../modalities/selectivity-resolution-options.md) §4 precisely so it
could not be re-narrated after the fact, and it is machine-carried by `selcal_gate.NEXT_STEP_BY_TIER`:

1. **⛔ STEP 3 (the NR4A1/2/3 re-panel) IS NOT BOUGHT.** It would be money spent to reproduce a failure. The
   draft preregistration [`nr4a-repanel-prereg-DRAFT.md`](../modalities/nr4a-repanel-prereg-DRAFT.md) is
   **retired unrun**, and its own power section already said the design was powered ≤ 0.16 against the
   separations this program has measured — so the tier and the power analysis point the same way.
2. **Every NR4A3 selectivity statement in the paper is an UNVALIDATED PREDICTION**, in the language of §4.
   ⚠ **Carried in THREE places and verified to be, not asserted:** the **Abstract**, **§2.12a** and **§4
   Limitations** — so a reader who never reaches the limitations still meets it. *(This line first said
   "applied in the sentences themselves"; a `grep` showed the phrase existed exactly ONCE in the paper, in
   §2.12a, so the claim was aspirational when written. It is now checked rather than believed.)*
3. **⛔ IT DOES NOT DISTINGUISH "the readout is blunt" from "this pair is hard"** and must never be reported as
   though it did. SMARCA2/SMARCA4 bromodomains are ~80 % identical and the published selectivity turns on a
   single Gln1469 hydrogen bond, so a null is consistent with both an insensitive endpoint and a genuinely
   narrow structural signal.
   ⚠ **AND A THIRD READING, MEASURED 2026-08-02, WHICH BOTH REGISTERED READINGS ASSUMED AWAY.** They share a
   premise nobody had checked — that the simulated complexes were the complexes whose selectivity was
   measured. Scored against the deposited ternaries the panel was *designed around*, all 12 co-folds
   reproduce the internal VHL/EloB/EloC machinery at **DockQ 0.89–0.97** and the degradation-target↔VHL
   interface at **DockQ 0.023–0.046, fnat 0.000** — not one native interface contact recovered, on either
   arm, by either of two independent implementations
   ([`selcal-cofold-vs-crystal.json`](../modalities/selcal-cofold-vs-crystal.json),
   [`selcal-cofold-dockq.json`](../modalities/selcal-cofold-dockq.json)).
   ⛔ **This makes the null WEAKER evidence about the instrument, not a route to re-opening it.** The endpoint
   was never exercised on the complexes in question, so the null bounds the *workflow as run* rather than the
   readout alone, and the failing stage is ternary **generation** rather than ranking. Every paralogue-
   selectivity statement remains an unvalidated prediction; nothing here licenses revisiting one.
   ★ **BOTH HALVES OF THE CONTROL A NEAR-ZERO SCORE REQUIRES ARE NOW MEASURED, so 0.023–0.046 is a
   measurement rather than a property of the scorer** — each objection answered by running it, not by
   argument. **(a) Does anything score HIGH through this harness?** DeepTernary, a dedicated SE(3)-equivariant
   ternary generator, on `6HAX_B_A_FWZ` — a VHL/SMARCA2 PROTAC ternary supplied as complete unbound inputs in
   its own released benchmark — reaches **DockQ 0.618 (CAPRI "Medium"), median 0.438 over 16 scored poses,
   best iRMSD 1.21 Å**, from the same DockQ 2.1.3 build
   ([`selcal-deepternary-poscontrol.json`](../modalities/selcal-deepternary-poscontrol.json)).
   ⛔ 2018 deposit, inside the model's 2023-10-14 horizon, therefore memorisation-permitting **by
   construction**: a positive control on the **harness and instruments**, never on generalisation, and it
   says nothing about NR4A3, degradation or selectivity. **(b) How wrong is 0.03?** Holding VHL fixed and
   displacing the **true** target chain of 9DTY by a known rigid RMSD — everything else perfect, placement
   the only variable — gives **1.000 → 0.948 (0.5 Å) → 0.845 (1 Å) → 0.717 (2 Å) → 0.401 (4 Å) → 0.240
   (8 Å) → 0.085 (16 Å) → 0.026 (32 Å)**
   ([`selcal-dockq-decoy-scale.json`](../modalities/selcal-dockq-decoy-scale.json)). The co-folds sit
   at the **~32 Å** rung — consistent with their independently measured 17.8–21.2 Å interface-RMSD — so they
   are **not a near-miss on placement**, and the generation failure is not a matter of degree.
   ★ **(c) AND THE COMPLEX IS RECOVERABLE IN SILICO — measured on 9DTY ITSELF, which is post-horizon.**
   9DTY and 9DTX are absent from DeepTernary's disclosed 4,471-entry exclusion set and deposited well after
   its 2023-10-14 horizon
   ([`deepternary-leakage-check.json`](../modalities/deepternary-leakage-check.json)). Given the two
   binding sites, the generator reaches **DockQ 0.839 (CAPRI "High"), iRMSD 0.67 Å, fnat 0.83**, best of 16
   seeds, median 0.442, against our co-folds' best 0.038 on the same interface and reference
   ([`selcal-deepternary-headtohead.json`](../modalities/selcal-deepternary-headtohead.json)).
   ⛔ **NOT the same question, and the two numbers are not interchangeable:** the published *unbound*
   protocol superposes both binaries into the native ternary frame and supplies the native degrader pose, so
   the model is told **which pocket each end of the degrader occupies** and predicts the two proteins'
   **relative placement**, which is randomised out of its input. Our co-folds were given sequence and ligand
   and nothing else. ⚠ Best-of-16, and **one arm**: the SMARCA4 arm was refused before any prediction
   (warhead fragment overlap 0.42 against a 0.55 bar) and no SMARCA4 number exists.
   **What it settles:** this ternary is not beyond in-silico reach, so 0.023–0.046 is a property of the
   sequence-only co-folding route used here and not of the problem.
   ★ **(d) AND THE FAILURE IS LOCALISED — THE HALVES ARE RIGHT, THE ASSEMBLY IS NOT.** Superposing each
   co-fold on one protein at a time and measuring the degrader over the native atoms contacting *that*
   protein (correspondence through the reference molecule's atom graph, never by proximity): all 12 sit
   within **3.2 Å** of the crystal in each protein's own frame — target median **1.83 Å**, E3 median
   **1.96 Å** — against an assembled interface scoring what the true complex scores when displaced **32 Å**.
   A factor of **10** ([`selcal-cofold-decompose.json`](../modalities/selcal-cofold-decompose.json)).
   ⇒ **The missing information is the relative placement of the two proteins**, which is exactly what a
   ternary generator is given when handed each end's site. That is the nameable precondition for credible
   NR4A3 ternaries, and it is why (c) matters beyond one number. ⚠ The locus is decided against that measured
   scale, never a bar chosen for the occasion; unreadable scale ⇒ locus reported UNDETERMINED.
   ★★ **(e) A PARALOGUE-SELECTIVITY READOUT THAT PASSES A KNOWN-ANSWER TEST — THE FIRST THIS PROGRAM HAS.**
   The published mechanism for this pair is a hydrogen bond, not a dynamical quantity (Kofink et al.,
   PMC9551036: *"the selectivity-inducing hydrogen bonding between Gln1469 of SMARCA2BD and VCB"*), and a
   bond between two named partners is visible in a deposited structure. Scoring the target↔VCB contact map of
   9DTY and 9DTX and aligning the bromodomains **by sequence** (identity 0.890 over the interface alignment —
   the two deposits number locally vs full-length, so equal numbers are different residues), the descriptor
   finds exactly one position where a glutamine on the SMARCA2 arm makes a **side-chain** polar contact the
   aligned SMARCA4 residue does not: **Gln98 Oε1 → VHL Arg12 Nη2, 2.88 Å**, 34 interface contacts, against
   **Leu1545** (10 contacts), which cannot make that bond
   ([`selcal-interface-signature.json`](../modalities/selcal-interface-signature.json)).
   ⚠ **Side-chain, not any polar contact** — SMARCA4's leucine touches the E3 through its *backbone* amide at
   2.93 Å, and counting that hid the substitution behind an interaction of a different kind (the first version
   of the check did exactly that and reported a real recovery as a failure). ⚠ No hydrogens at these
   resolutions ⇒ "polar contact" is the heavy-atom donor–acceptor proxy, labelled as one.
   ⛔ **It validates ONE contact in ONE pair.** It does **not** validate E1, and it makes no NR4A3 prediction
   correct — applying it to an NR4A3 ternary additionally requires that ternary to be credible, which (d)
   shows this route does not yet supply.
   ★★ **(f) THE VALIDATED DETECTOR, TURNED ON THIS PROGRAM'S OWN NR4A TERNARIES — AND THE ANSWER IS NOT
   YET.** With (e) passed, the same descriptor was applied to the `denovo_401` NR4A1/2/3–CRBN ternaries
   ([`nr4a-ternary-signature.json`](../modalities/nr4a-ternary-signature.json)). It returns **six**
   positions where the NR4A3 model contacts the E3 and both comparators do not — and **five are placement
   artifacts**: GLU104, ARG174, LYS195, ARG219, LEU234 carry the **identical residue in all three
   paralogues**, so they cannot encode a paralogue difference; a contact present in one model and not another
   is three independently-folded structures disagreeing, on the route (d) measures as wrong by a factor of 10.
   **One position is sequence-encoded: GLU208** (Glu → Pro in NR4A1, Tyr in NR4A2).
   ⛔ **And its reproducibility is NOT TESTED**: only `model_0` exists per paralogue, against a bar of 3.
   One model cannot distinguish a determinant from that model's accident — the first readout printed
   *"reproducible across ALL 1 models"*, which is n = 1 wearing the costume of a replication test, and the
   module now refuses that wording outright.
   **⇒ A justified NR4A3-selective-ternary case does not exist today, and exactly two things stand between
   here and one:** (i) **replicate models per paralogue** — a GPU spend, not a re-read, and the cheaper of
   the two; (ii) **the NR4A3 warhead pose**, which is a wet-lab fact: no deposited NR4A3 LBD–ligand complex
   exists, the binder is de novo, and the pocket itself is cryptic (opened by metadynamics), so no in-silico
   route supplies it. GLU208 is a **lead with a validated detector behind it**, not a result.
   ★★ **(g) WHAT IS ACTUALLY MISSING, AFTER (a)–(f) — AND IT IS NARROWER THAN "WE CANNOT DO THIS".**
   Three things had to be true for a justified NR4A3-selective-ternary case, and two of them now are.
   **Is the raw material there?** YES, and it was already measured: the differential-surface atlas finds
   **33 exposed, divergent-vs-both, character-changing handles** on the NR4A3 LBD (of 254 aligned residues;
   137 exposed, 109 divergent) and its gate reads **GO**
   ([`nr4a3-differential-surface-atlas.json`](../modalities/nr4a3-differential-surface-atlas.json)).
   ★ And (e) calibrates how much is enough: the SMARCA2/SMARCA4 selectivity that PRT3789 exploits rests on
   **one** such position (Gln98 → Leu). NR4A3 has 33 candidates where one sufficed.
   **Is there a detector?** YES — (e), validated against a published known answer.
   **Is there a correctly-assembled ternary to point it at?** ⛔ **NO, and this is the whole remaining gap.**
   The existing NR4A ternaries are sequence-only co-folds from the route (d) measures as failing at assembly
   by a factor of 10, and the molecule that produced them is **unrecoverable** — no `_chem_comp_bond` loop in
   any of the three models, and it entered as `$PROTAC_SMILES`
   ([`nr4a-ternary-ligand-provenance.json`](../modalities/nr4a-ternary-ligand-provenance.json)), so
   §2.5's ternary result cannot be replicated or extended at any price.
   ⚠ **A CORRECTION TO A FRAMING USED EARLIER THE SAME DAY:** the assembly method was described as unusable
   on NR4A3 "for want of a binding site". That is wrong and the repo refutes it — `results/nr4a3-matrix/
   nr4a{1,2,3}-opened.pdb` are state-matched opened LBDs, **Gate 3A is supported** (the opened geometry does
   not relax once the bias is removed), and a docked `denovo_401` pose exists in that frame. The site is
   **UNVALIDATED, NOT ABSENT**, and those are different: the generator can be handed our own pose today.
   ⇒ **The next step is therefore in-silico and specified**: rebuild the three paralogue ternaries by the
   assembly route (opened LBD + docked warhead pose as site 1; CRBN + IMiD from a binary crystal as site 2;
   a degrader whose SMILES is **recorded this time**), then re-run (f). What remains genuinely experimental
   is narrower still — whether anything binds the opened pocket at all, which a thermal-shift/SPR/NMR screen
   answers far more cheaply than a co-crystal, and whose NEGATIVE would be equally decisive.
   ⛔ None of (a)–(g) is a positive control for paralogue-selectivity **detection at this program's E1
   endpoint**; that endpoint still has none, and none of them may be read as softening the tally below.
4. **It re-scores no landed leg and changes no ΔΔG.** It is a statement about the instrument.

### The standing tally this closes

**All three** attempts to establish a positive control for this program's selectivity claims have now been run,
and none succeeded: §2.11's cooperativity calibrator (`valB_mini`) failed on **sign**; RUNG 4's NR-V04
retrospective returned **DISCORDANT** (non-resolution, and covalency-confounded so it could never have been a
positive control at any *n*); and this control — the one built specifically to be free of those defects, on
solved structures on both arms — returns **NULL on an adequately-powered design**. Documented in the paper at
§2.12a.

⚠ **"There is no fourth candidate staged" was WRONG and is retired** (2026-08-02; superseded line kept in
[Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims)). It was a statement about the search, not
about the repo, and the search had stopped one stage too early. **Two known-answer tests are already built
and have never been run:**
- **CREBBP vs BRD4(1) / SGC-CBP30** — `selectivity-benchmark.json` + `selectivity_benchmark_prep.py` +
  `stage-selectivity-benchmark-aws.yml`, fully specified with an `abfe_plan` and **no result key**. Both arms
  are real holo crystals with the **same ligand** (4NR7 / 5BT4), so no docking and no pose assumption, and an
  experimental ΔΔG ≈ **2.2 kcal/mol** against a demonstrated ~1.5 kcal/mol band. ⛔ It is a **binary**
  selectivity control and would **not** discharge §4's paralogue/ternary statement — but this program has no
  binary selectivity control either (valA validates relative FEP *within one pocket*).
- **A pmx/GROMACS interface point-mutation ΔΔG** — the only physics lane here that has recovered a published
  known answer (barnase–barstar Y29A **+4.42 ± 1.08** vs +3.4 and Y29F **−0.37 ± 0.18** vs −0.13, both inside
  1.5 kcal/mol, ~$0.21/leg, `triskit23/pmxfep` already baked) and it works on **PPI interfaces**. This
  document's own reading of the selcal null is that SMARCA2/4 selectivity *"turns on a single Gln1469
  hydrogen bond"* — i.e. a point mutation. Conditional on a measured mutational value existing in a primary
  source, which is a $0 check that must precede any spend (Open decision 7).
  ⛔ **THE $0 CHECK RAN ON 2026-08-02 AND THE ANSWER IS NO. THIS ARM IS CLOSED ON EVIDENCE, NOT ON BUDGET.**
  One home for the verdict and every reading behind it:
  [`pmx-mutation-reference-precheck.json`](../modalities/pmx-mutation-reference-precheck.json)
  (generator [`pmx_mutation_reference.py`](../modalities/pmx_mutation_reference.py)) —
  **`STOP_NO_REFERENCE`**. Do not restate its counts here. The Gln1469 contact is documented
  **structurally** (a hydrogen bond in a crystal) and **functionally** (cellular degradation ratios), and
  **neither is a measured interface mutational ΔΔG** — so the run would have had no known answer to be
  scored against, which is the defect that cost this program three withdrawn selectivity claims.
  ⚠ **The nearest measured thing is named rather than hidden, because it is what a reader will ask about:**
  an interface point mutation *has* been measured in this exact system — **VHL R69A** (Farnaby 2019,
  PMC6600871) — but it sits on the **E3 arm** rather than the paralogue-discriminating residue, and its
  reported quantity is a **TR-FRET cooperativity ratio**, not a binding ΔΔG. Converting one into the other
  would fabricate the link this program does not have.

**Authorization is no longer what blocks the pmx arm — evidence is (trimcrae, 2026-08-02: *"pmx only"*).**
The superseded line, retained because it stood until that answer:
*"Neither is authorized here."* The ABFE arm above is **still not authorized**; the pmx arm **was**, and
then failed its own $0 precondition, which is a stronger and more durable reason to leave it unrun.
Neither is a positive control for paralogue *degradation* selectivity. They are recorded because "nothing
is left" was the wrong sentence, and a tally that closes a search is worth exactly as much as the search
behind it.

★ **WHAT WOULD UNBLOCK THE INSTRUMENT — and it is a different question from the one just closed.** The
precheck refuses the *SMARCA2/4 application*. The lane's own stated limitation is separate and now has a
concrete, priced answer: the qualified set **brackets** the wedge (+3.4 hot spot, ~0 near-null) and covers
nothing at the size a paralogue-scale difference has, so
[pricing.md](../compute/pricing.md) records that the confirmatory line *"may not claim to resolve a
paralogue-scale difference"*. Scanning all 7,085 SKEMPI rows for a wedge-sized, charge-conserving,
buildable mutation of 1BRS returns **exactly one** candidate —
[`protfep-wedge-band-candidates.json`](../modalities/protfep-wedge-band-candidates.json), 29
rejected — and it is now defined as `barnase_barstar_W35F` and CI-verified to stage. It is deliberately
**not** in `protfep_bench.QUALIFICATION_SET`, so it cannot flip the engine's committed verdict without a
measurement. ⚠ **It would settle whether THIS ENGINE resolves a ~1 kcal/mol interface effect. It is not a
selectivity control, involves no paralogue, and passing it would license no SMARCA2/4 or NR4A3 claim.**

---

<a id="in-flight-superseded"></a>

## ⏱️ IN FLIGHT — what is actually running right now (as of **2026-07-30 5:30 PM ET**)

*★ **A SUPERSEDED BOARD PLUS FOUR ONE-HOMES.** ⛔ **DO NOT READ THE TABLE AS LIVE STATE.** The live board is [`inflight_usd_per_ns.py`](../modalities/inflight_usd_per_ns.py) / `inflight-board-all.md`.*

⛔ **THIS BOARD IS NOT LIVE, AND IT IS STRUCTURALLY BLIND TO PART OF THE FLEET.** Its own as-of is above; the live board is [`inflight_usd_per_ns.py`](../modalities/inflight_usd_per_ns.py) / `inflight-board-all.md`, which is its one home. Two defects, both recorded rather than patched: it is **stale by days**, and it is **scoped to Vast + GCP**, so **a SageMaker rental is invisible to it by construction** — which is exactly how a 3:16 PM ET ABFE dispatch on 2026-08-02 appeared on no board at all. ⚠ **It is deliberately NOT re-stamped here**: inventing a current state is the failure this board already committed. What is *not* stale is the four one-homes in the prose below the table — the buy-line arithmetic, what `R` decides, the binary-arm departure finding, and the pose-diagnostic status. See [§12 finding 6](#12--findings-that-belong-to-other-documents).

*Every row is a PROGRESS reading — the counter moved since the previous pass — not a liveness ping. Rates are
measured over the stated interval, and **only quoted off a window long enough to swamp the 40-iteration commit
block**; the two withdrawn ETAs in [§Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 19b/19c
are both what happens when that rule is broken.*

**Every GPU row carries `$/ns` and its multiple of the ladder basis, and says whether that multiple is money
going out or money we refused** (CLAUDE.md §1). The basis is **$0.003412/ns**, DERIVED
(`congeneric_fanout.basis_usd_per_ns()`); the buy line is the absolute rate **$0.006539/ns**, which against
that basis is **≈1.92×**. ⚠ **That is NOT a loosening of the 1.5× ruled the same day — it is the identical
dollars per nanosecond.** The basis moved 22 % because the throughput table was re-anchored and widened, not
because any price changed; see [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 40.

**NOTHING IS BILLING. Every lane on this board is off a host.** The closure triangle closed at 5:11 PM ET
on 2026-07-30 — all four legs landed and `R` is computed — which was the last owed GPU work in the fixed
scope. The Step 1 fan-out (LANE 17/21) and the valB_mini replicates (LANE 19) closed earlier the same day —
the rows below say what each returned. The RUNG 5a-KS legs remain **PARKED, not finished**: on no host,
costing nothing. Both LANE-13 paralogue legs and all four RUNG 2b legs have reached their deliverables.

| what | state | ETA (ET) | cost | `$/ns` vs basis |
|---|---|---|---|---|
| ~~**Step 1 fan-out** (LANE 17/21) — 19 congeneric RBFE edges~~ | ✅ **COMPLETE — 18 of 18 computable edges landed; the 19th is not computable and is recorded as such.** Off every host. The ranked table it produced is the paper's §2.9 | — | realised **$73.79** machine-ledgered, against the DERIVED cap **$74.91** (`market_ceiling_usd(19)`) — finished inside its ceiling with **$1.12** to spare | every unit of the lane was bought under the **$0.006539/ns** buy line, and the units that could not be were ⛔ **REFUSED — $0 spent** and re-offered on later ticks rather than dropped |
| ~~**valB_mini r1+r2** (LANE 19) — the 4 replicate legs~~ | ✅ **CLOSED AT n=3 — and the gate FAILED on sign, so the decision is NO-GO.** Off every host. The deliverable is the **cycle SD**, which is the number this lane existed to produce | — | realised is **NOT machine-ledgered on this lane**; the floor and the reason are in [`realised-spend.json`](../modalities/realised-spend.json)'s attested block, which is a defect register, not an accounting category | — (no host) |
| **RUNG 5a-KS** (LANE 16) — the ligand-side causal kill-switch | ✅ **LANDED 2026-08-02 — all four legs (n = 2 seeds/arm). S = −0.1297 ± 0.3264 kcal/mol → the PREREGISTERED NULL: the marginal wedge is absent, registered in advance as the LIKELY outcome and NOT a stop.** Full record, limits and the staging verification: [the gate section above](#-rung-5a-ks-landed--the-causal-kill-switch-returns-its-preregistered-null-s--013--033-kcalmol-2026-08-02-215-am-et) and paper §2.10e. *Superseded, retained: this row previously read PARKED, NOT FINISHED, NOT BILLING since 2026-07-27 — both original legs died on a rotated S3 key and were destroyed, and the lane stayed parked because `relaunch_market_gate` refuses to re-buy above the buy line. It resumed and finished.* | **done — nothing owed** | realised: see [the ledger](../modalities); ladder ~$23 at four legs | ✅ bought inside the line and landed |
| ~~**The closure triangle** (LANE 9/20) — decides whether valB's miss is fixable at all~~ | ✅ **CLOSED. All four legs landed 5:11 PM ET Jul 30 and `R` is computed** — [`valb-triangle-reduction.json`](../modalities/valb-triangle-reduction.json). Off every host | — | the 4-leg tranche was priced against its own **$3.85** ceiling per pass | every rental cleared the **$0.006539/ns** buy line; the leg that finished it ran at **$0.005049/ns · 1.48× basis**. ⚠ **THE DAY'S CHURN — SEVEN HOSTS, 11:41 AM to 4:06 PM ET, ZERO COMMITTED ITERATIONS — WAS NEITHER PRICE NOR CARD SPEED, AND BOTH EARLIER READINGS ARE SUPERSEDED.** Two measured causes. **(1)** A host wedged INSIDE a checkpoint persist: commit-store generation `fa5da1eb` holds `simulation.nc` alone, and `_persist` writes .nc → .chk → manifest — so the board counted a torn generation and read `production/1800` while the next host correctly resumed at 1760, and the leg re-ran the same 40 iterations after every host change with the percentage RISING each time. **(2)** The lane had **11 `workflow_dispatch` inputs against GitHub's cap of 10**, which is SILENT: every placement flag — card floor, bid escalation, uninterruptible tier — arrived EMPTY, so each control was chosen correctly and discarded at the door. Fixes, all with tests: `committed_progress` requires the manifest, `commit_store_audit.py` names which rule refused each generation, the idle guard condemns on byte-identical log CONTENT (its mtime test was vacuous against a 120 s timer sync), `collect` re-places a dead host in the same pass, and CI now fails a workflow that exceeds the input cap or uses GCP auth without `id-token: write` |
| **The restrained binary re-run** (LANE 20) | **HELD ON PURPOSE — and ⚠ NOT behind `R`, which LANDED on 2026-07-30.** Its gate is the **pose diagnostic** (`gpu-ternary-fep-vast.yml task=triangle-converge`, $0): the prereg forbids interpreting `R_binary` without it. **Measured 11:08 AM ET 2026-07-31** — the option reached `main` only that morning (commit `42c99101`) and the `converge` job is `skipped` in every one of the five most recent lane dispatches, so it **has still never run**. Also **not GCP-runnable**: these are the *triangle's* binary legs (2 fs, seed 0, S3-keyed), a different experiment from the r0 calibrator's restrained re-run that landed 2026-07-28 ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 44). **The ternary arm is NOT being re-run restrained** (audit §L.3f) | held pending the pose diagnostic | **$0** | — |
| ~~**valB_mini reverse leg r0**~~ (GCP L4 **on-demand**) | ✅ **LANDED — `production/2000` of 2000; the hysteresis it unlocked is measured in the block below** | — | **$0 real dollars** — expiring GCP trial credit (closes **2026-10-10**). **A SEPARATE LEDGER**: never summed into realised or ladder spend | — |
| ~~LANE 13 categorical-dynamics analysis~~ | ✅ **DONE 2:49 PM — the verdict is above.** Legs, collect and analysis all landed | — | realised **~$4–5** against a ~$4.3 projection | — |

**✅ `R` HAS LANDED (5:11 PM ET, 2026-07-30) AND THE ANSWER IS THE FIRST BRANCH BELOW.** Every number here is
a reading of [`valb-triangle-reduction.json`](../modalities/valb-triangle-reduction.json), never typed:
**`R = 0.2128 kcal/mol`**, decision **`R_CONSISTENT_WITH_ZERO`** — inside the tightest plausible noise floor
(0.216 at `sigma_leg = 0.045`). Read against the mapping below, that says valB_mini's miss is an
**ENDPOINT-STATE error, and more sampling will not fix it.**
The two closures are reported separately as the rule requires — **`R_ternary = −0.0312`**, essentially zero,
against **`R_binary = −0.2440`**, which carries nearly all of it — so this is not a clean `R_coop` hiding two
large cancelling terms. The frozen pre-registered verdict at the original bounds reads
**BINARY_PATH_DEPENDENT, prediction upheld**.
⚠ **THREE LIMITS, NONE OF THEM SMALL PRINT.** *(a)* **n = 1 and NO error bar is quoted or invented** — the
design requires one seed per edge, because a mixed-seed triangle is not a closure, so no replicate SD exists.
*(b)* At the `sigma_leg` upper bound now MEASURED from the n=3 replicates (0.265) the addendum also reads
`R_CONSISTENT_WITH_ZERO`, but at the superseded assumed 0.7 the same design reads **UNDERPOWERED** — and that
divergence is exactly [§Open decisions](#open-decisions) 7, still trimcrae's to settle. *(c)* Closure measures
**INTERNAL CONSISTENCY, NOT ACCURACY**: it is structurally blind to force-field error, the SMARCA4→SMARCA2
homology substitution, NAGL charges and protonation, every one of which is a per-endpoint state function.

**★ WHAT `R` DECIDES, stated the right way round.** The closure triangle exists to answer one question about
valB_mini's miss — **1.543 kcal/mol** at the landed n=3, the one home for which is the RUNG 2 · replicates row
in the scoreboard above — and the two outcomes point in opposite directions:

- **`R` ≈ 0 ⇒ an ENDPOINT-STATE error.** The bias is a per-endpoint state function, it telescopes out of any
  cycle, and **more sampling will NOT fix the miss.**
- **`R` materially non-zero ⇒ a PATH error, and the miss IS fixable** by the protocol changes that address it.

*(I stated this backwards earlier on 2026-07-27; the correction is
[Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 41 and this is the one home for the
mapping.)* `closure_decomposition` splits `R_coop = R_ternary − R_binary` and its own rule is to report both,
never `R_coop` alone.

**★ AND `R_ternary` NOW DECIDES A SECOND THING — whether the parked RUNG 5a-KS resume is worth buying at all.**
`S` is a two-leg difference inside the **ternary** environment, so it inherits that environment's
non-conservative error; `R_ternary` is the only measurement in the program that bounds it. The arithmetic, the
three branches (**ADMIT / HOLD / STOP\_AND\_REDRAW**) and the thresholds are **pre-registered before `R` landed**
and live once, in
[`valb_failure_propagation.s_resolvability_from_R_ternary`](../modalities/valb_failure_propagation.py) →
[`valb-failure-propagation.json`](../modalities/valb-failure-propagation.json) — do not restate them here.
Two properties of that rule that must survive being quoted: a large `R_ternary` at n=1 buys a **hold and a
second draw, never a kill** (`closure_noise_floor`'s own asymmetry — one draw cannot convict), and an ADMIT
bounds the **non-conservative** error class *only*, because closure is blind to per-endpoint state functions.

**⚠ AND THE POWER TO READ `R` AT ALL IS NOW MEASURED RATHER THAN UNKNOWN.** `closure_noise_floor` was written
saying `sigma_leg` is unknown to a factor of **15.6** and that *"nothing in this lane has measured it"* — the
n=3 replicates did. Converting the landed cycle SD through the design's own SD relation bounds `sigma_leg`
**above**, which excludes the range where the triangle was hopeless but leaves its power **mediocre rather than
comfortable** at the worst case. Derived, never typed: `valb_failure_propagation.sigma_leg_now_bounded` /
`power_at_measured_bound`. ⚠ **One consequence needs a $0 decision from trimcrae, and it is deliberately NOT
taken here:** `binary_departure_prereg` demotes a null closure to `UNDERPOWERED` on a hand-set `sigma_leg > 0.2`
proxy that the measured bound now trips — so as frozen, **a null `R` reports UNDERPOWERED and the diagnostic we
have already paid for answers nothing.** Amending a preregistered rule after a failing result is the retune this
program forbids, so the discrepancy is *recorded* (before `R` landed) and routed the same way as the
admits-zero gate defect — see [§Open decisions](#open-decisions).

**Committed if both billing lanes complete: ~$43** (fan-out ~$36 + valB replicates ~$7.32), against the
lane bands quoted in the rung entries below. Every figure in this column is either the LADDER's, quoted from
those entries, or the REALISED figure derived in
[`realised-spend.json`](../modalities/realised-spend.json) —
[pricing.md](../compute/pricing.md) owns the per-unit cost evidence and this board owns nothing.


⚠ **WHY NR4A1's REPLACEMENT HOST APPEARED TO STARVE ITS GPU — kept because the diagnosis outlived the leg,
which finished on that same host.** Three agreeing
intervals (3.4, 3.14, 3.00, the last over a full hour) put the 4080S at **~3.0–3.4 ns/h** against **~5.5–6.0
ns/h** for the same job on a 4090 — a ratio of **0.55**, where the cards' own throughput ratio for this class of workload is ~0.83. The utilisation gap says
the same thing from the other side: **44 % GPU on the 4080S against 75 % on the 4090**, steady across passes.
A card that is merely slower runs *busy*; one that is fed too slowly runs *idle*, and this one is idle. So the
cause is **host-side (CPU/PCIe feeding the PLUMED bias), not the card**.
**A SINGLE `gpu_util = 0.0` IS NOT A STALL — the progress scalar is the authority.** This host has now read 0.0
twice (05:48 AM during startup, 08:36 AM mid-run) and both times the ns counter kept climbing; a re-read seven
minutes after the second put it back at 45 %. Vast's utilisation field is an **instantaneous poll**, so it
catches the process between kernels or during a checkpoint write. The watchdog is right to require the durable
scalar to ADVANCE rather than the box to look busy — which is exactly why it reported "advancing, leaving it
alone" through both. A stall needs a **frozen counter** across two passes, not an idle-looking sample.
**The decision is to leave it alone**, and the reason is arithmetic rather than caution: moving hosts buys
~5 h of wall-clock that nothing is waiting on — the analysis is a MATCHED comparison and cannot start without
NR4A2 either way — at the price of a capacity scramble, whatever progress sits past the last checkpoint, and
a re-rent that can land on another starving host. The extra billed time is **~$0.75**. What *is* worth
carrying forward: machine **17720** should be excluded when the next paralogue leg is launched.

✅ **THE BINARY LEG'S "SLOWDOWN" WAS QUANTISATION — RESOLVED, and the discriminating observation was taken
rather than assumed.** Over 82 min the leg did **320 iterations = 234/h**, back at its baseline, so the "40 in
27 min" was one commit block caught whole. The mechanism is now confirmed rather than merely plausible: **every
delta observed on either leg is an exact multiple of 40** — binary 40, 320; ternary 120, 200 — so the commit
store advances in **blocks of 40 iterations** and a short window measures the block boundary, not the rate.
**The rule this leaves behind is in the table caption: never quote a FEP rate off a window that spans only a
few blocks.** I broke that rule in the same breath as writing it — the ternary leg's "~7:45 AM" came off a
27-minute window carrying exactly 3 blocks, which is why it is now a range off 82- and 109-minute windows
instead. *(Withdrawn ETAs are in [§Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 19b.)*

⚠ **THE −0.534 REFERENCE RESTS ON A BROKEN BINARY ARM — and the 2b gate SURVIVES ANYWAY. Read both halves.**
Measured 2026-07-26 (GH runs 30202934339, 30209580292; audit §L.3–L.3b): in the r0 **binary** leg the ligand's
*receptor-contacting* moiety leaves its pose and does not return in **8 of 12 replicas**, while the **ternary** leg
in the same cycle is **12/12 stable**. So ΔG_binary is not a free energy of the intended bound state, and
**ΔΔG_coop(r0) = −0.534 is not a valid measurement of cooperativity.**

But the 2b gate is a **4 fs-vs-2 fs consistency check**, not an accuracy check against a trusted value — so a
defect the two timesteps *share* cancels out of the comparison, and the gate stays meaningful **on one condition:
the 4 fs cycle's binary arm has to carry the same defect as the 2 fs one.**

**★ THAT CONDITION IS MEASURED, AND SATISFIED — the 4 fs binary arm fails the same way.** Run as a genuine test
that could have gone the other way (a clean 4 fs arm agreeing with a contaminated 2 fs one to 0.02 kcal/mol would
have meant the departure barely moves ΔG_binary, and my claim would have needed substantial softening). It did not
go the other way. GH run 30210676030 (Vast `task=converge`, CPU, $0) vs GH run 30210186711 (GCP, r0):

| | 2 fs (r0) | 4 fs (2b) |
|---|---|---|
| binary `contact_pose` max / med (Å) | 16.327 / 4.333 | **17.622 / 5.358** |
| binary replicas ending beyond 4.0 Å | **8 of 12** | **7 of 12** |
| binary λ initiation, endpoint / interior | 1 / 7 | **1 / 9** |
| **ternary** `contact_pose` max / med (Å) | 2.835 / 1.653 | **2.999 / 1.897** |
| **ternary** replicas beyond 4.0 Å | **0 of 12** | **0 of 12** |

Every feature reproduces — magnitude, replica fraction, class mix, λ signature, and the clean ternary arm — across
a different timestep, a different provider and GPU, a different commit interval and independent runs (audit §L.3d).
So:

- **The RUNG 2b timestep PASS STANDS on its own terms.** The gate asks whether 4 fs reproduces 2 fs; it does, and
  the shared defect cancels from the comparison. **4 fs adoption is not undermined.**
- **The r0 finding is REINFORCED, not softened** — the departure is a systematic property of the binary leg's
  setup, not one bad trajectory.
- **−0.534 and −0.5125 are two precise measurements of the same wrong thing.** Their agreement is evidence of
  *reproducibility*, which is what the gate claims, and not of correctness, which it does not.

Consequences kept separate, because they are independent:
- **RUNG 2 was already FAILED** (wrong sign), so this changes no verdict from pass to fail — it supplies a
  candidate *mechanism*, now on much better footing but **still a hypothesis**. The experimental target is
  **+0.94**; both cycles return ≈ −0.52 to −0.53; both have a reproducibly departed binary arm and a clean ternary
  arm. That co-occurrence is suggestive and it remains **correlational**. **The test is a restrained binary
  re-run:** sign flips positive with a held pose → mechanism established; sign stays negative → the wrong sign has
  another cause and the departure is a separate (real) defect. Do not report the mechanism as settled before that.
- **BOTH cycles need the binary arm re-run**, not only r0 — the 4 fs arm carries the identical defect.
- **IT ALSO BEARS ON THE RESCOPE REPLACEMENT — free pre-check, audit §L.3e.** The specified **synthetic closure
  triangle** (~$6) is 3 edges × (ternary + binary) = 6 legs, and its **three binary legs are the same construction
  that departs**. The design already handles this correctly — `closure_decomposition` splits
  `R_coop = R_ternary − R_binary` and its own rule says to report both, never `R_coop` alone — so **nothing needs
  changing**. What it gains is a **pre-registrable prediction**: *`R_binary` materially non-zero, `R_ternary`
  small.* Both outcomes are informative, and the second argues against my own reading — if `R_binary` is also
  small, the departure's bias is a per-endpoint state function, telescopes out of any cycle, and therefore largely
  cancels from ΔΔG_coop too. **Run the pose diagnostic on the triangle's legs when they land** (`mode=converge` /
  `task=converge`, $0) and do not interpret `R_binary` without it.
  - **⛔ STATUS OF THAT DIAGNOSTIC — MEASURED 2026-07-30, 10:50 PM ET: IT HAS NEVER RUN ON THE TRIANGLE, AND
    UNTIL IT WAS FIXED IT COULD NOT HAVE. This is the single home for that fact.** Two findings, both from
    the Actions API and the workflow source rather than from memory. **(1) It was never dispatched.** Across
    the **137** `gpu-ternary-fep-vast.yml` runs from the legs landing (5:11 PM ET Jul 30) to 10:27 PM ET, the
    `converge` job is `skipped` in every one — zero executions; across the newest **1000** runs, back to
    1:02 PM ET Jul 29, also zero. It has executed **once ever**, GH run 30210676030 on 2026-07-26, which is
    where the RUNG 2b column of the §L.3d table above comes from. **(2) A dispatch would have read the wrong
    legs**, and that is MEASURED, not inferred. The job hardcoded `--mode edge` on its `--fetch-trajectories`
    call, and `unit_id` embeds *both* the timestep and the mode — so it reconstructs `..._dt4.0fs_wu1.0_edge`
    (RUNG 2b) while the triangle wrote `..._dt2.0fs_wu1.0_triangle`; the two id sets are **entirely disjoint**,
    not partially. GH run **30599871712** (10:47 PM ET Jul 30, $0) dispatched `task=converge` and came back
    **green in 3 m 54 s** having analysed `calib_hi_to_lo__{binary,ternary,solvent}_vhl` — the RUNG 2b legs —
    and reproducing §L.3d's numbers exactly. **That is the dangerous shape**: not an empty report that would
    announce itself, but a *plausible, already-published-looking* table returned under a triangle dispatch.
    Fixed by deriving the mode from the
    dispatched task — `ternary_vast_launch.CONVERGE_TASK_MODES`, new `task=triangle-converge`; `task=converge`
    still means `edge` byte-for-byte so §L.3d stays reproducible. **Consequence, and it is the live one:
    `R_binary` is still un-cross-checked by pose data, so the bullet above is unsatisfied and the restrained
    binary re-run's gate is this diagnostic, not `R`** (`R` has landed).
- **★ DECIDED 2026-07-26 (trimcrae delegated: "it's your call"): run the triangle's binary legs UNRESTRAINED.**
  Three reasons, the first on its own decisive:
  1. **Comparability.** The triangle's economy is **r0 reused as T1** — `price_triangle` buys **4 legs, not 6**
     (**$6.83** at n=1). Restrained T2/T3 in a cycle with an unrestrained T1 makes `R` measure the
     *protocol difference*, not path error. To restrain you must re-buy T1 restrained: 6 legs, **~$10.25 (+50 %)**,
     and the reuse that justified the design is gone.
  2. **It answers a question the restrained version cannot** — whether the departure's bias is path-dependent or a
     state function. That determines whether r0's and 2b's **existing** ΔΔG_coop numbers are salvageable at all,
     which is worth far more than $6.
  3. **Sequencing, by this repo's own litmus test** (§"serialize only when one result could cancel the rest"):
     *is there a result this run could return that would make me not run the rest?* **Yes** — if `R_binary` is
     small at low σ_leg, the bias telescopes out of cycles and largely cancels from ΔΔG_coop, making a restrained
     re-run unnecessary *for the cooperativity number*. So unrestrained-first is strictly correct ordering, and a
     restrained binary leg becomes a **separate, later** experiment whose value is conditional on this result.
  **Registered in code, before any leg is bought:** `valb_triangle_closure.binary_departure_prereg()` states the
  prediction, classifies the four outcomes, and — the part that matters — reports **UNDERPOWERED** rather than
  "cancellation" when neither closure resolves at high σ_leg, because σ_leg is known only to a factor of ~15 and at
  σ_leg = 0.5 the power to resolve an r0-sized effect is **~0.22**. 8 tests pin the branch logic, including both
  branches that would count *against* the r0 reading.
  **Still HELD** until the reverse leg reads out, per the rescope hold — the decision is made, the spend is not.
- **ΔΔG_coop cannot be reported from the r0 cycle at all** until the binary arm is re-run — a blocker
  *independent* of the reverse leg's hysteresis result, which concerns the (clean) ternary arm.
- **WHAT TO CHANGE ON THE RE-RUN** (λ attribution, GH run 30210186711, audit §L.3c): the escape is *alchemically
  facilitated but not alchemically confined*. **7 of 8** departures **initiate** in the interior, skewed to the
  upper-λ states where the softcore region is largest (`{7:3, 9:2, 10:1}`), so the softening opens the door — but
  once departed the displaced state **persists at every λ including both physical endpoints**, so the physical
  Hamiltonian does not close it. Consequences: a **restraint on the receptor-contacting moiety** is the obvious
  remedy; the existing trajectory is **contaminated, not merely
  under-converged**, so extending it is not an option; and this does **not** show the binary complex model is
  wrong — an interpretation the persistence numbers alone would have supported and the initiation numbers do not.
  *n = 8 departing replicas — suggestive of an upper-λ mechanism, not a rate.*
  **Built and keyed 2026-07-27** — `ternary_restraint.py` (flat-bottom, λ-independent, default OFF) +
  `gpu-ternary-fep-gcp.yml restrain=1`, which keys the commit prefix (`_rst`) and the commit-manifest fingerprint
  so a restrained leg can never resume an unrestrained trajectory. **Two rulings live in audit §L.3f and are the
  single home for both:** (a) there is **NO standard-state correction** — this is RBFE with a never-decoupled
  ligand, the λ-independent restraint cancels from ΔG(A→B), and importing ABFE's Boresch release term would be
  *wrong* rather than conservative; (b) **only the BINARY arm is re-run restrained** — the ternary arm is measured
  clean in both cycles and both directions and keeps its trajectories. This is a *separate* question from the
  closure triangle's binary legs, decided unrestrained above.

**✅ RUNG 2b — ALL FOUR LEGS LANDED, AND 4 fs REPRODUCES 2 fs.** Reduced 2026-07-26 11:44 AM ET by the
official reducer, inside the parity image that produced the trajectories (`gpu-ternary-fep-vast.yml task=reduce`,
run 30208761567) — not by hand.

| leg | ΔG_morph (kcal/mol) | MBAR SE |
|---|---|---|
| ternary | 47.6131 | 0.1294 |
| binary | 48.1256 | 0.1321 |
| solvent | 47.7982 | 0.1016 |
| probe | 48.1970 | — |

**ΔΔG_coop(4 fs) = −0.5125** against the 2 fs reference **−0.534** → **|Δ| = 0.0215 kcal/mol**, ~33× inside the
ratified 0.7 tolerance and far below the 0.35–0.7 "consistent but weakly discriminating" band. **No NaN on any
leg**, and all three cycle legs share one protocol hash (`35573f24b6c1…`). On the gate's stated terms this is a
**PASS**, and 4 fs is adopted.

⚠ **TWO QUALIFICATIONS THAT ARE NOT OPTIONAL, both from the reducer's own output.**
1. **`system_identity_consistency` is UNKNOWN, not clean.** `n_particles`, `charge_method` and
   `setup_cache_version` are **unrecorded in all three legs**, so the check that the legs describe the same
   SYSTEM could not be made — comparability rests on `protocol_hash`, which by construction covers the OpenFE
   settings and **not** the system. This is precisely the hole that let four reverse-leg attempts run a
   146,020-particle build against a 141,968-particle one on 2026-07-25. The reducer is right to report UNKNOWN
   rather than agreement. **Root cause found and half-fixed:** the leg record wrote the *raw*
   `CHARGE_METHOD` env while the protocol payload hashes the same env **with an `am1bcc` default**, so an unset
   variable produced a hash committing to am1bcc beside an identity record saying `null`; both now write the
   resolved value. `n_particles` and `setup_cache_version` still need the Vast lane to pass them through.
   **✅ THE SYSTEM-IDENTITY QUESTION IS NOW ANSWERED ANYWAY — from the trajectories, since the leg records are
   still silent (measured 2026-07-28, $0 CPU, `ternary-system-census.yml`).** Within every arm the solute is
   identical atom-for-atom and the net charge is zero with an invariant neutralising excess; the legs differ
   only in bulk water and the counter-ions that scale with it, worth ~3e-3 kcal/mol against this gate's 0.7.
   The record and the arithmetic:
   [ternary-4fs-vast-findings.md §2d](../compute/ternary-4fs-vast-findings.md). This does **not** retire
   the leg-record fix — a census is a manual check, and `n_particles` should still be written by the lane.
2. **The reducer's own valB gates return INDETERMINATE** — "need ≥2 independent replicates for a cycle SD",
   n_replicates = 1. That is a different question from the timestep test (it asks whether the *calibrator* is
   certified), but it means **−0.5125 carries no replicate-SD error bar**, and this repo's standard is
   replicate-SD rather than MBAR-SE.

**So: 4 fs is adopted on a single-seed agreement, and the adoption is provisional in exactly the way the gate's
own 0.35–0.7 language anticipates — not because the agreement is marginal (it is not) but because one seed
cannot produce the error bar the standard asks for. The system-identity check HAS since been made and the legs
pass it** (same alchemical system per arm; the residual difference is bulk solvent —
[ternary-4fs-vast-findings.md §2d](../compute/ternary-4fs-vast-findings.md)).

**Why the ternary leg's ETA moved so far:** production runs at roughly **half** warmup's per-iteration cost
(625 steps at 4 fs against warmup's 1250 at 1 fs), so a leg's finish cannot be extrapolated from its warmup
rate. The table's figure is measured on **production** iterations directly. *(The two earlier quotes are in
[§Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 19b.)*

✅ **`vast-watchdog.yml` HAS now fired on cron** — first `schedule` event **2026-07-26 1:42 AM ET**, and it is
the pass that recovered NR4A1 (above). Autonomous coverage of the paralogue legs is therefore claimed, on the
evidence rather than on the trigger block parsing. *(The ternary watchdog's own cron is stretching far worse than that — it fired 9:17 PM then **not for 3h40m**. **"Busy repo" is measurably NOT the cause:** repo Actions load had fallen to **~2 runs/h** in that window. Ruled out with evidence — the file parses, its `run:` block is 368 chars, its registered `state` is `active`, and manual dispatch works every time. The proof it is repo-wide rather than a defect in either watchdog is **`vast-price-sample.yml`**, an unrelated cron, showing the same pattern in the same window: **7:15 PM → 9:01 PM (106 min) → 12:46 AM (225 min)**. So a newly-added `schedule:` proving itself is necessary but **not sufficient** — this repo's crons deliver ~2–4 h regardless of the expression, and no cron expression changes that.)*

## ✅ THE FIRST FORWARD/REVERSE HYSTERESIS THIS PROGRAM HAS EVER MEASURED — **GATE PASSED** (2026-07-27 2:14 PM ET)

*★ **A LANDED GATE.** The one home for the hysteresis numbers; the scoreboard defers to it by name. Registers: instrument `V5`.*

**|ΔG_fwd + ΔG_rev| = 0.325 kcal/mol against the preregistered ceiling of 1.0 → PASS.** The `calib_hi_to_lo`
ternary leg is now complete in both directions, which is what made the criterion measurable at all; every prior
reduction in this lane reported it as unmeasured because no reverse leg had ever run.

| leg (`calib_hi_to_lo__ternary_vhl`, seed 0) | ΔG_morph (kcal/mol) | MBAR SE |
|---|---|---|
| forward | **+47.470131** | 0.110758 |
| reverse | **−47.794736** | 0.086487 |
| **abs(fwd + rev)** | **0.324605** | vs ceiling **1.0** → **PASS** |

⚠ **THE ERROR BARS ABOVE ARE MBAR SEs AND ARE THEREFORE NOT THIS REPO'S STANDARD.** They are quoted because
they are what a single replicate can produce, and they are a **provenance** label, not a magnitude claim: this
program's uncertainty is the **replicate SD**, and at `n_replicates = 1` **there is none** — the reduction
reports `cycle_sd_kcal: null`, not a small number. The hysteresis itself is a *path-closure* check on one
replicate and does not need a replicate SD to be well-posed; the **calibration** verdict does, and it is
INDETERMINATE for exactly that reason.

**Verified to be a genuine reverse run before the number was read**, because the failure mode it guards against
produces the best-looking possible answer: a reverse leg that silently re-reported the forward trajectory
sign-flipped would give a hysteresis of **exactly 0.000**. Four discriminators, all from the artifact — the
opened `.nc` holds **141,968 particles** (`v2pe`, the *same* system as fwd, **not** the 146,020-particle `v1`
build that killed four earlier attempts), the ΔG is **−47.794736** rather than −47.470131, the MBAR SE differs,
and the per-replica pose statistics differ. Full table:
[audit §L.7a](../modalities/ternary-lane-guard-audit-2026-07-25.md).

**What this does and does not change.** It closes one preregistered criterion and nothing else:

- **RUNG 2 (valB_mini) is still FAILED** on the wrong sign, and the calibration gate is still **INDETERMINATE**
  at `n_replicates = 1` — the hysteresis is a *cycle-closure* check, not an accuracy check.
- **ΔΔG_coop still cannot be reported from the r0 cycle**, for the reason already on this board: the binary arm
  is broken and must be re-run. That blocker is independent of this result and is untouched by it.
- **The convergence state is now reported as `MEASURED_FAILURE`, not as unexamined** — the first time the lane
  has said that out loud. It is driven by `ligand_stable_ok` in both directions.

**★ AND THE REVERSE LEG IS THE CONTROL THAT MAKES THE BINARY ARM'S FAILURE SPECIFIC.** The rev leg passes every
health flag — overlap, connectivity, equilibration, mixing, within-leg fwd/rev, plateau, quarter-block — except
`ligand_stable_ok`, at contact-pose max **4.737 Å** against a 4.0 threshold, median **2.529**, **11 of 12
replicas STABLE**, and the single departure **initiating at λ state 11, a physical endpoint**. Set against the
**binary** arm's **8 of 12** replicas departing at **16.6 Å**, a ternary arm that is 12/12 clean forward and
11/12 clean reverse says the departure is **specific to the binary arm's missing second protein**, not a
protocol-wide defect. Clean in *both* directions is what makes that a comparison rather than an assertion.

**How this was nearly lost, and what changed:** the reducer computed 0.325 and the verdict annotation printed
*"NOT MEASURED (no reverse leg reduced)"* — two further layers of the direction-keying/absent-value defect, one
a replicate-count guard suppressing a criterion that needs no replicates, one a reader naming a field the
producer never emitted. Both fixed, 21 tests, the key sweep extracted from the YAML by AST rather than retyped:
[audit §L.7](../modalities/ternary-lane-guard-audit-2026-07-25.md).

---

## 2 · REQUIREMENTS — what must be TRUE

**Sixteen requirements. None is ✓-settled.** Each row carries its work state, its authorization, the
instruments that serve it, and — the column that invariant 1 exists to protect — **the ceiling on what may be
claimed today**, which can never exceed the validation status of the instrument underneath it.

### 2.1 · The register

| id | requirement | work state | auth | served by | ⛔ claim ceiling today |
|---|---|---|---|---|---|
| **R1** | **A druggable pocket exists on NR4A3.** Node `PO` | ✓ work complete | — | `V13` `V14` `V15` | **supported, not settled.** Gate 1 (a two-state cryptic *opening*) FAILED as registered and was reformulated to basin-internal breathing; the existence evidence is experimental and independent (8XTT) — see [§5 row R1](#5--where-each-requirement-stands) |
| **R2** | **That state is thermodynamically accessible at equilibrium** (Gate 3B) | ○ future | — | `V13` — ⚠ its only demonstrated reading is ✕ dead | **unresolved.** Reading Gate 3B off a *single* biased F(Rg) profile is conclusively closed ([§6a](#6a--dead--conclusively-unworkable-never-retry)); no replacement reading has been run |
| **R3** | **The receptor frame `denovo_401` was generated into still qualifies** — the paper's explicit **submission gate** | ✕ **REFUTED 2026-08-03** | — ($0, spent) | `R3`'s own frame-level audit — **built and run** | ⛔ **MEASURED FALSE.** Under the harmonized, score-independent definition the generation frame's mapped orthosteric site is **detected and not druggable**, so the requirement's own statement does not hold. Per the paper, this *"reaches the **generation receptor** … not merely a reported frame-fraction"*. ⚠ **This is the requirement register's FIRST ✕, and [§0.2](#02--work-state--the-five-glyphs) is explicit that *"a claim that has been refuted is dead, and should say so"*** — flagged for trimcrae rather than applied silently, because it changes what the paper may claim about every `denovo_401`-derived result. ⚠ The verdict is **rule-sensitive and the artifact records the sensitivity**. Evidence: [`r3-generation-frame-harmonized.json`](../modalities/r3-generation-frame-harmonized.json) |
| **R4** | **Something binds that pocket.** Node `L` | ○ future | — | ⛔ **none — needs a bench** | **nothing binds the cryptic pocket, of any molecule.** ⚠ Scoping is load-bearing: NR4A3 *is* experimentally ligandable ([§5 row R4](#5--where-each-requirement-stands)); the cryptic site is what has no ligand |
| **R5** | **The binding pose is right.** Node `PS` | ○ future (re-run) | — | `V3` — **INCONCLUSIVE** | **unresolved.** The docking works; the pipeline's **site selection** missed on 6 of 6 pairs, so the pose's weight rests on the site being right and `V3` could not check that |
| **R6** | **The per-paralogue opening penalty does not reverse the margin** — ΔG_open. Node `DGO` | ○ future | 🔒 explicit nod | ⛔ **none built** | ⛔ **every ABSOLUTE ΔΔG on the binder path is conditional on a term nobody has computed.** Validation requirement 2: matched-open comparison can *"miss or REVERSE selectivity"*. ⚠ **Narrowed 2026-08-03, and this page stated it too widely:** the block is on the **absolute** route to `R7`, **not** on a ligand-side *relative* double difference, in which the opening penalty is common to both ligands of a matched pair and cancels inside each protein — [§3.4 fact 3](#34--three-instrument-facts-this-page-used-to-be-missing). ⚠ *Superseded, retained: "every ΔΔG on the binder path".* |
| **R7** | **The binder is paralogue-selective over NR4A1/NR4A2** — ⚠ **and the two halves are NOT the same requirement**: NR4A1-sparing is a hard constraint with a named anti-target genotype, NR4A2-sparing is unbounded in both directions ([§2.4](#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically)). Node `B` | ○ open — the existing result is ⏸ parked | 🔒 (`V4`) | `V4` (no result) · `V6` `V7` `V8` `V9` `V10` | ⛔ **an unvalidated prediction.** Three separate blocks, only one of which is the instrument — see [§8](#8--the-two-live-routes-to-selectivity--and-where-each-is-actually-blocked) |
| **R8** | **A linker geometry is feasible** at an NR4A3-unique cysteine. Node `LK` | ✓ computed — ⚠ **not reconciled to its artifact** | — ($0 CPU) | `V17` (fails its own positive control) + the reach enumeration | **geometry only.** No thiol pKa, reactivity, adduct or degradation quantity; reach is necessary and never sufficient. And it is conditional on `R5` |
| **R9** | **OUR ternary is correctly assembled.** Node `ARCH` | ○ future — **NOT STARTED** | **—** ($0, needs no nod) — rung **`5b-T`**, [priced and gated 2026-08-02](#101--open-rows-ordered-by-what-unblocks-the-most). ⚠ *Superseded, retained: "🔒 unpriced, no rung."* | `V2` — recovered its known answer in scope, **never pointed at our system** | ⛔ **no NR4A3 ternary has been correctly assembled by anyone.** [§what the SMARCA2/4 null BINDS](#what-this-binds-in-the-words-fixed-before-the-run): *"⛔ **NO, and this is the whole remaining gap.**"* ⚠ `5b-T` gives it a route and a gate; it does not make the claim, and its output is **structural, never thermodynamic** |
| **R10** | **A ternary forms.** Node `T` | ○ future | 🔒 (via `R9`) | `V2` (live route) · `V12` ⏸ (the route that built the existing one) | the existing prediction was built by the failing route and its molecule is **unrecoverable**, so it cannot be replicated |
| **R11** | **The ternary adds or preserves selectivity.** Node `TS` | ○ future | 🔒 (via `R9`) | `V1` (passes, in scope) · `V16` (null with a bound, **uncalibrated**) · `V5` ⏸ FAILS · `V11` ⏸ no pass | one sequence-encoded candidate at **1 model per arm against a reproducibility bar of 3** |
| **R12** | **The ternary is compatible with DEGRADATION** — productive unique-lysine geometry. Node `UB` | ○ future | — ($0 screen) | `V18` — ⛔ **no known-answer test exists for it** | categorical input only (**4 NR4A3-unique lysines, 3 exposed**). Validation requirement 5's honest limit: real degraders often ubiquitinate several lysines and lysine-less substrates can still be degraded, so this **raises the odds; it does not guarantee** the paralogue is spared |
| **R13** | **The modelled object is the real biological object — EWSR1::NR4A3 in fusion context**, not an isolated LBD | ○ **not started** | **`R13-a`: —** ($0, needs no nod) · **`R13-b`: 🔒** — [PRICED and GATED 2026-08-03, rung `S`](#rung-s--the-two-scope-rungs-r13-r14-claim-ceiling-conditions-deliberately-off-the-cum-chain). ⚠ *Superseded, retained: "🔒 unpriced".* | ⚠ **an instrument EXISTS and is staged — [`fusion_cofold.py`](../modalities/fusion_cofold.py) (apo Boltz-2 co-fold of the `seam` and `composite` constructs) — but it has never been pointed at the CORRECTED junction, and it serves only the STRUCTURE tier.** ⚠ *Superseded, retained: "⛔ **none — no lane, no rung, no row anywhere**".* | ⛔ **every geometry claim on this page is about an isolated LBD construct.** Validation requirement 5 asks for the fusion-context ensemble, lysines **outside** the LBD (hinge, DBD, fusion partner) and full CRL/E2~Ub ensembles | ⚠ **And the object was mis-specified until 2026-08-03:** an exon off-by-two meant all **7** committed junctions deleted the AF1 and the first zinc finger; the corrected junction is **EWSR1 exon 7 → residue 264 :: NR4A3 exon 3 → residue 1** ([`nr4a3-exon-audit.json`](../modalities/nr4a3-exon-audit.json)), which **strengthens** the C166 note — C166 is present in the disease protein, so the modelled 373–626 construct really does exclude a real NR4A3-unique cysteine. ⛔ The **full** validation-requirement-5 object is still **unpriceable**, and [`scope-rung-cost.json`](../modalities/scope-rung-cost.json) `unpriceable` says why: no particle count for an ~890-residue chimera with a 264-residue IDR, no determined replica count for a disordered region, and **the patient-level breakpoint is not pinned**, so the object is not yet uniquely defined.
| **R14** | **Selectivity claims are bounded to their tested scope** — the AR/MR superfamily cross-binding check | ○ **not started** | **`R14-a`: —** ($0, needs no nod) · **`R14-b`: 🔒 + ⛔ blocked by the rate line** — [PRICED and GATED 2026-08-03, rung `S`](#rung-s--the-two-scope-rungs-r13-r14-claim-ceiling-conditions-deliberately-off-the-cum-chain). ⚠ *Superseded, retained: "🔒 unpriced".* | ⚠ **~8/9 BUILT, NEVER ASSEMBLED** — not "no instrument" ([§2.2](#22--requirements-with-no-instrument--the-holes)) | the selectivity claim is **currently bounded to two paralogues by an unrun check**. SI names MR/AR *"the **sole** sequence-level non-paralogue follow-ups"* that *"must clear"* (SI `:213–219`). ⚠ *Superseded, retained: served by "⛔ **none run**".* | ⭑ **And the missing half is FREE:** `R14-a` (add MR/NR3C2 to the panel, run its never-run cognate-ligand self-control) costs **$0** and needs no nod — so this row has been reading as money-blocked while its highest-value part was startable. ⛔ **That self-control runs FIRST: until it passes, no anti-target margin from this panel may be read, including the one SI §S1 already publishes.**
| **R15** | **The candidate set is chemically constructible and physicochemically plausible** | ✓ work complete for one mechanism per molecule — ⚠ **and a named candidate now exists AT the 12-atom gate** ([§5 row R15](#5--where-each-requirement-stands)) | — ($0) | RDKit enumeration + `V17`-adjacent reach | **one mechanism per molecule.** The two-mechanism construct needs a **two-branch template**, which is a design change to a preregistered enumeration and **the decision has never been asked for** ([§10](#10--the-roadmap--one-ordered-list)). ⛔ **And the library's own provenance is open** — its generator no longer reproduces it, which reaches the causal test article: [§10.1 row 25](#101--open-rows-ordered-by-what-unblocks-the-most) |
| **R16** | **NR4A3 is the right target** (EMC dependence). Node `TG` | ○ future — **DELEGATED** | — | the dTAG degradation test, in the EMC-program paper | not a blocker of this paper. `:2508`: *"This paper's claimed contribution is the target's computational druggability/selectivity, **not EMC efficacy**"* |

⚠ **`R7` is the row every reader should test invariant 1 against.** Its own paralogue ABFE **has run**, at
three independent-seed replicates, and resolved below zero on both paralogues — and the engine that produced it
misses a known **absolute** answer by more than the entire margin (`V7`), has **never** recovered a known
*selectivity* answer (`V4`, no result), carries a λ-overlap defect on **every** leg (`V9`), and is missing a
term that can reverse the sign (`R6`). **A good-looking number under a stack like that cannot raise the
claim.** That is invariant 1, and it is why the paper carries every paralogue-selectivity statement as an
unvalidated prediction.

### 2.2 · Requirements with no instrument — the holes

⛔ **Five requirements have no instrument at all.** They are not "not done yet"; there is nothing built that
could answer them, so no amount of running the existing lanes moves them.

| id | why it is a hole | is it buildable? | named next action |
|---|---|---|---|
| **R3** submission gate — ⚠ **NO LONGER A HOLE: the instrument was built and run on 2026-08-03** | ⛔ **and the hole was mis-stated.** The gap was not reporting granularity: `sagemaker_src/entry_pocket_reharmonize.py` scores `af2_static`, `calibration_nr4a3`, `8xtt_20conformers`, `metad_frames` and `release_rep0..2` and builds **no `release_druggable` entry** — the generation receptor was never an INPUT to the rerun, although `nr4a3_pocket_reharmonize.detection_from_result` implements that kind and the redesign brief's own rerun list ends with *"exact generation receptor frame"*. A per-frame dump would not have closed it either ([`nr4a3_release_druggable.py`](../modalities/nr4a3_release_druggable.py)'s `confirm_filter`: the reused summary and the fresh corroboration *"can disagree"* and the reproduced score governs) | ✅ **built** — [`r3_generation_frame_audit.py`](../modalities/r3_generation_frame_audit.py) + [`r3_score_generation_frame.py`](../modalities/r3_score_generation_frame.py), 15 tests, [`r3-generation-frame-audit.yml`](../../.github/workflows/r3-generation-frame-audit.yml) | ✓ **RUN, $0 — and it FAILED the gate.** See [§10 row 3](#101--open-rows-ordered-by-what-unblocks-the-most). ⚠ *Superseded, retained: "the harmonized artifact reports ensemble-level fractions only … build the frame-level audit; it is the cheapest open item in the program".* |
| **R4** does anything bind | **no in-silico instrument can serve it.** A thermal shift / SPR / NMR fragment screen against the opened site is the only answer | ❌ not in silico | carry it as the standing wet-lab dependency; a negative would redirect the program and is as useful as a positive |
| **R6** ΔG_open per paralogue | nothing has ever computed an opening penalty for any paralogue | ✅ yes — priced in the ladder's OPTIONAL/HELD tier | 🔒 a budget nod. **Otherwise report everything conditional on the open state** — which is $0 and fully defensible |
| **R13** fusion-context object | the entire program models an isolated LBD construct (373–626). C166, one of the four unique cysteines, is already outside it — ✅ and the 2026-08-03 exon audit **strengthens** that: C166 is present in the disease protein under the corrected junction | ✅ in principle — **and the STRUCTURE tier now has a staged instrument** ([`fusion_cofold.py`](../modalities/fusion_cofold.py)); what has no instrument is the **ensemble** tier | ✅ **DONE 2026-08-03 — it has a rung, a gate and a price**: `R13-a` **$0** (sequence inventory at the corrected junction, needs no nod) → `R13-b` **~$0.66** ([rung `S`](#rung-s--the-two-scope-rungs-r13-r14-claim-ceiling-conditions-deliberately-off-the-cum-chain); [`scope-rung-cost.json`](../modalities/scope-rung-cost.json)). **Next action: run `R13-a`.** ⛔ The *full* requirement-5 object stays **unpriceable** and the artifact names the three reasons. ⚠ *Superseded, retained: "⛔ **give it a rung, a gate and a price — it has none.** Nothing on the plan, the spine or the ranked list touches it".* |
| **R14** AR/MR cross-binding | ⚠ **THIS ROW OVERSTATED THE GAP BY ABOUT 8/9THS, AND IT IS THE ONE HOLE ON THIS LIST THAT IS MOSTLY BUILT.** The sequence screen has run and flagged exactly **NR3C2 (MR)** and **AR**; the docking harness has run at anti-target-panel scale; **AR is already a panel target**; `denovo_401` is already staged as an anti-target candidate. What is genuinely missing is **MR/NR3C2 in the panel**, and the SI's *second* requirement — a cryptic-pocket-formation test on AR/MR — which is the same detector as `R3`'s. Evidence and the four pointers: [`instrument-options.md`](../modalities/instrument-options.md) §3.2 (`C08`) | ✅ yes — **and mostly already is** | ✅ **DONE 2026-08-03 — it has rungs, gates and a price** ([rung `S`](#rung-s--the-two-scope-rungs-r13-r14-claim-ceiling-conditions-deliberately-off-the-cum-chain); [`scope-rung-cost.json`](../modalities/scope-rung-cost.json)): **`R14-a` $0, needs no nod** — add MR to the panel and run the never-run cognate-ligand self-control **first**, because until it passes no anti-target margin from this panel may be read, **including SI §S1's**; **`R14-b` ~$3.41** for the matched AR/MR pocket ensembles, ⛔ **registered DO-NOT-LAUNCH** (its `$0.022758/ns` is 3.48× the buy line — *not* drift, but a biased leg judged against an unbiased basis, and no metadynamics-anchored basis exists), behind a **$0 CV-transferability precheck** that can refuse it on evidence (AR/MR sit at ~0.32 overall identity against the paralogues' 0.51/0.58); **`R14-c`**, the FEP half, is **closed here** — it is `V4`'s instrument, so it is downstream of §10.1 row 2, not parallel to it. ⚠ *Superseded, retained: "never run".* |

⚠ **And four more requirements have an instrument that has never returned a usable answer**, which is a
different failure and must not be filed with the above: **`R2`** (`V13`'s only demonstrated reading is ✕
dead), **`R5`** (`V3` INCONCLUSIVE), **`R9`** (`V2` validated but never pointed at our system), **`R11`**
(`V5` failed on sign, `V16` has no calibrator).

**So of sixteen requirements: one is delegated, two are ✓ on the work axis with the claim open, and thirteen
are open — of which nine have either no instrument or no usable instrument answer.**

⚠ **AND ONE OF THE FIVE HOLES IS A DIFFERENT KIND OF HOLE, WHICH THIS SECTION COULD NOT SAY UNTIL THE
INSTRUMENT SWEEP (2026-08-03).** The counts above are all of the form *"has an instrument RETURNED a usable
answer"*, and on that reading `R14` belongs where it sits. But **"no instrument" and "the pieces exist and
nobody assembled them" are opposite work items**, and only the second is free. `R14` is the second:
the screen ran, the harness ran at scale, one of the two targets is already in the panel. `R13` and `R4` are
the first — `R4` genuinely cannot be served in silico at all. **Filing them under one word is how the
cheap one stayed invisible**, which is the same failure as [§10.3](#103--what-taking-the-union-changed)'s
*"a caveat with nowhere to go"*, one layer down. The counts are unchanged because they are still true as
defined; what changed is that `R14`'s row now says which kind it is.

### 2.3 · The claim-ceiling rule, stated so it can be checked

> **A requirement may never be claimed above the validation status of the instrument that produces it.**

Mechanically: take the requirement's row in [§2.1](#21--the-register), read the `V`s in its *served by* column,
look each up in [§3.1](#31--the-instrument-table), and **the weakest one sets the ceiling**. A `V` with **no
result** sets the ceiling at *unvalidated prediction*, whatever the number looks like. A `V` that **failed**
sets it lower still.

⚠ **This is not a stylistic preference; it is the rule the program has paid for.** The paper's own record shows
**at least four** withdrawn *selectivity* results, and the largest of them fell to defects **no known-answer
test could have caught** — which is why the prophylactic is two rules and not one
([§3.3](#33--the-pattern--rewritten-because-the-version-this-page-carried-was-false)).

### 2.4 · The selectivity requirement is ASYMMETRIC — and this page stated it symmetrically

★★ **THIS IS A CHANGE TO THE DESIGN TARGET, NOT A FOOTNOTE, WHICH IS WHY IT SITS IN THE REQUIREMENTS LAYER
(2026-08-03, from the target-route sweep).** `R7`, `R11` and `R12` all read *"selective over NR4A1/NR4A2"*,
one requirement with two comparators. **The biology does not say that.** The two halves have different
evidence, different weights and different remedies, and reading them as one has made the brief harder than
it needs to be in the place where the program is strongest and softer than it should be where the program
is weakest.

| half | what bounds it | what the program holds against it |
|---|---|---|
| **NR4A1 — a HARD constraint** | ⛔ a **named anti-target genotype**: the combined *Nr4a1*⁻/⁻;*Nr4a3*⁻/⁻ mouse, which is precisely the pair a non-selective NR4A3 degrader reconstitutes. Single nulls do not do it. (PMID **17515897**; PMID **29343483**; evidence assembled in [`nr4a3-emc-biology-evidence.md`](nr4a3-emc-biology-evidence.md), numbers in [`nr4a-safety-genetics.json`](../modalities/nr4a-safety-genetics.json)) | **all 7 divergent Pocket-5 lining residues differ; 5 of them engageable** ([§8 Route A](#route-a--a-warhead-engaging-paralogue-divergent-pocket-handles---blocked-nothing-running--serves-r7)) |
| **NR4A2 — UNBOUNDED, in both directions** | ⚠ the *most* constrained paralogue in human population genetics and the most tissue-enhanced, but **no phenotyped KO** — the repo's IMPC query returned nothing for any of the three, and the widely-repeated *"Nurr1 single-KO is neonatal-lethal"* is flagged **UNCONFIRMED** in [`nr4a3-emc-biology-evidence.md`](nr4a3-emc-biology-evidence.md). **Strongly selected against in humans; unbounded for adult transient loss.** | **only 6 of 7 differ (I531 is Ile in NR4A3 *and* NR4A2), so 4 of the 5 engageable handles distinguish it** |

⛔ **AND THE ASYMMETRY RUNS THE OTHER WAY FROM HOW THIS PAGE READ IT.** [§8 Route A](#route-a--a-warhead-engaging-paralogue-divergent-pocket-handles---blocked-nothing-running--serves-r7)
said Route A is *"20 % thinner exactly where it can least afford to be"*, on the strength of NR4A2 being
*"the paralogue carrying the dopaminergic-loss liability one most wants to spare"*. **That premise is an
unbounded claim wearing an evidenced one's costume**: the lethality it rests on is the flagged-UNCONFIRMED
one above. The defensible statement is narrower and more useful — **the program has MORE discriminating
power against the paralogue whose sparing is evidenced-mandatory, and LESS against the one it has no bound
on in either direction.** *(Superseded, retained: "exactly where it can least afford to be" as an
evidenced ranking of the two liabilities.)*

**What this changes, and what it explicitly does not.**

- ✅ **It changes the brief**, at $0 and with no new claim: **hard constraint — spare NR4A1; soft constraint
  — spare NR4A2 as far as the four handles allow, and carry the residual as an exposure question rather than
  a chemistry one.** A narrowing of a requirement inherits no instrument, so nothing on
  [§3](#3--instruments--which-one-answers-each-requirement) has to pass for it to be adopted.
- ⛔ **It does NOT dissolve the requirement**, and the hypothesis that it might is answered **no** for any
  systemic molecule — by that one cited mouse genotype.
- ⛔ **An absent KO is not a safe KO.** *Unbounded* means the liability could be larger than NR4A1's, not
  smaller. Nothing here licenses degrading NR4A2, and the exposure lever is a property of **a molecule that
  does not exist** — this repo holds no measured or predicted CNS-penetration datum for any NR4A candidate.
- **The two $0 observations that would bound the open half** — MGI single-KO phenotypes for *Nr4a1/2/3*
  (the named source after IMPC returned nothing) and HPA per-tissue nTPM (the field is `null` today) — are
  [§10.1 row 26](#101--open-rows-ordered-by-what-unblocks-the-most). Full argument, both directions, and the
  route it came from: [`target-route-options.md`](target-route-options.md) route 1.

---

## 3 · INSTRUMENTS — which one answers each requirement

An instrument that has never recovered a known answer **cannot support a claim**, however good its output
looks. This table is why **selectivity results in this program have had to be withdrawn**.

⛔ **A "PASSES" here means the instrument recovered *that* known answer. It never means the instrument
supports the claim the graph points it at** — the paper spends four separate paragraphs refusing exactly that
reading, so the scope column below is not a footnote, it is the verdict.

### 3.1 · The instrument table

| id | instrument | known-answer test | result | ⚠ what the result does NOT support | state | serves |
|---|---|---|---|---|---|---|
| **V1** | Structural selectivity descriptor (`selcal_interface_signature`) | recover the published SMARCA2 Gln1469↔VCB hydrogen bond, unaided, from two crystals | Gln98 Oε1→Arg12 Nη2 **2.88 Å** vs Leu1545 | *"validates **one contact in one pair**. It does **not** validate E1 … and it makes **no NR4A3 prediction correct**"* (`:2200–2203`) | ✓ **PASSES, in scope** | `R11` |
| **V2** | Ternary generator given both sites (assembly route) | rebuild 6HAX (in-set) and 9DTY (post-horizon) | DockQ 0.618 / **0.839**, iRMSD 0.67 Å | 6HAX is inside the model's 2023-10-14 horizon, so it is *"**memorisation-permitting by construction** … **not** evidence of generalisation"* (`:2140–2142`). 9DTY is **best of 16 seeds, median 0.442**, and **one arm** — the SMARCA4 arm was refused and **no SMARCA4 number exists** (`:2163–2165`) | ✓ **PASSES, in scope** — ⛔ **never pointed at our system** | `R9` `R10` |
| **V3** | Ligand pose prediction (dock + MM-GBSA) | recover a known holo pose in a nuclear receptor from apo | **INCONCLUSIVE by its own pre-registered rule** — the C1 holo self-dock control failed through the pipeline's own box on **6 of 6 pairs across 3 receptors** (17.3–29.3 Å), so the primary arm measured the *site*, not the docking. With an fpocket-chosen box the same protocol reaches **3.04 Å, fnat 0.778, 7 of 9 native contacts** | it cannot grade the docking: the protocol ceiling itself missed (`C1c_self_dock_holo_oracle_box` 2.849 Å against a 2.0 Å criterion) | ✓ complete — **verdict INCONCLUSIVE** | `R5` `R8` |
| **V4** | **Selectivity free energy (ABFE)** — the *selectivity* known-answer test | CREBBP vs BRD4(1) / SGC-CBP30, ΔΔG ≈ 2.2 kcal/mol | **no result. Built and staged with no `result` key; never completed** | it is a **binary** control: even a clean pass *"would **not** discharge §4's paralogue/ternary statement"* ([§what the SMARCA2/4 null BINDS](#what-this-binds-in-the-words-fixed-before-the-run)) | ○ **not started · 🔒 not authorized** — see [§6c](#6c--held--not-refuted-not-parked-waiting-on-a-decision) | `R7` |
| **V5** | Alchemical ternary cooperativity (`valB_mini` ΔΔG_coop) — **validation requirement 1(C), "Val C"** | reproduce a known cooperativity, **+0.944** kcal/mol | **−0.599** — wrong sign in all 3 replicates, ~34× the statistical uncertainty | ⛔ nothing. [§Validation architecture](#validation-architecture-the-five-requirements) calls it *"the highest-value dollar in the plan"* and it **failed**; the closure triangle localises the miss to an **endpoint-state** error, so more sampling will NOT fix it | ✓ complete — **FAILS, systematically** | `R11`  ⚠ **ADDED 2026-08-03 — the binary arm's pose failure is now measured on the CLOSURE TRIANGLE too, not only on the r0 and RUNG-2b cycles:** `task=triangle-converge` ($0) returns **10/12** and **8/12** binary replicas departing beyond 4.0 Å against **1/12** and **0/12** ternary, upholding the pre-registration and returning `BINARY_PATH_DEPENDENT`. This is an instrument fact about `V5`'s **binary environment**, and it does not touch the wrong-sign verdict above — see [§10 row 6](#101--open-rows-ordered-by-what-unblocks-the-most). |
| **V6** | Relative FEP (OpenFE, the congeneric lane) — **validation requirement 1(A), "Val A"** | TYK2 `ejm_31→ejm_42` benchmark ΔΔG **−0.24** | **+0.37**, abs err **0.61** — inside the ~1 kcal/mol band | a **relative** result on a *different* quantity in **one** pocket. [§what the SMARCA2/4 null BINDS](#what-this-binds-in-the-words-fixed-before-the-run): *"valA validates relative FEP **within one pocket**"* — it is **not** a selectivity validation. ⛔ **AND ITS SCOPE IS THE `am1bcc` BINARY LANE ONLY** — see [§3.4](#34--three-instrument-facts-this-page-used-to-be-missing) | ✓ **PASSES, within one pocket, one charge model** | `R7` |
| **V7** | ABFE engine, **absolute** | T4-lysozyme L99A + benzene, experimental **−5.2** kcal/mol | **+1.90 ± 0.09** — *"under-binding by ≈ +7.1 kcal/mol — a failed/strongly-biased absolute benchmark"* (`:1252–1254`) | ⛔ the miss is **larger than the entire selectivity margin the engine is used to compute**, which is why every ABFE **absolute** in the paper is uninterpretable | ✓ complete — **FAILS** | `R7` |
| **V8** | ABFE engine, hydration | methane hydration free energy (FreeSolv), **+2.0** | **+1.60 ± 0.04**, *"approximately reproduced"* (`:2296–2298`) | a solvation smoke test; says nothing about a protein site | ✓ **PASSES, narrowly** | `R7` |
| **V9** | λ-overlap diagnostic on the standing ABFE block | — (a self-check, not a known answer) | ⛔ *"**every leg** — the shared solvent leg and all three complex legs — has at least one soft-core-tail window pair below 0.03"* (`:1265–1268`) | holds the **whole ABFE block provisional**, including the paralogue result in [§5 row R7](#5--where-each-requirement-stands) | ✓ measured — **defect open**, repair 🔒 held **and** ⏸ as framed | `R7` |
| **V10** | Interface-mutation physics (pmx/GROMACS) | barnase–barstar Y29A vs published ΔΔG | +4.42 ± 1.08 vs +3.4 | ⛔ *"**No benchmark yet probes the regime this cross-check would occupy** — resolving ~1 kcal/mol between two closely related receptor states — so the engine is validated for seeing a large effect and for not inventing one where none exists, but **not demonstrated to resolve a small paralogue-scale difference**"* (`:2409–2412`). ⚠ **It also owes a WEDGE-SIZED benchmark**, and Open decision 10 rules it **not an independent second causal line**. ⛔ **AND ITS SMARCA2/4 APPLICATION IS NOW CLOSED ON EVIDENCE, NOT ON BUDGET** — see the row note below | ✓ **PASSES, but not in the regime that matters** · ⛔ its SMARCA2/4 application is **refused by its own $0 precheck** | `R7` |
| **V11** | Interface-stability endpoint (E1) | **two** attempts: NR-V04 retrospective, SMARCA2/4 sensitivity control | *p* = 0.393 (DISCORDANT) · *p* = 0.747 (NULL, adequately powered) | ⏸ parked — **no pass** ([§6b](#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen)). ⛔ **`V5`'s wrong sign is NOT a third E1 failure** — different instrument | ⏸ parked | `R11` |
| **V12** | Sequence-only co-folding (Boltz-2 ternary) | reproduce 9DTY/9DTX from sequence + ligand | DockQ 0.023–0.046 ≈ true structure moved 32 Å | ⏸ parked — **FAILS** ([§6b](#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen)) | ⏸ parked | `R10` |
| **V13** | Cryptic-opening free-energy profile (metadynamics F(Rg); Gates 1 / 3A / 3B) | Gate 1: a genuine **two-state** cryptic opening | ⛔ **FAILED as registered** — F(Rg) is monotonic, *"a single resolved minimum and a rising wall, with no separate opened minimum"*; recorded as *"**failed, and reformulated**, not a 'weak pass'"* (`:387–394`, `:2549`) | ⚠ a failed **mechanism** test is not evidence of absence — the cavity survives as basin-internal breathing. ⛔ Reading Gate 3B off a **single** profile is ✕ dead: three seeds do not reconstruct a common F(Rg) | ✓ ran — **Gate 1 failed as registered · Gate 3A supported · Gate 3B unresolved** | `R1` `R2` |
| **V14** | BioEmu unbiased ensemble cross-check (§2.1) | — (no in-repo known-answer test) | **12.5 %** druggable | ⚠ **an instrument with no known-answer test of its own on this system.** It is an *orthogonal* axis for `R1`, independent of the metadynamics Gate 1 and Gate 3B are argued over — which is its whole value, and also its limit | ✓ ran — **untested as an instrument** | `R1` |
| **V15** | PocketMiner + four permutation nulls (§2.2) | the nulls are the control | p = 0.009 / 0.0001 / 0.036 / **0.74** / 0.014 | ⚠ **one of the five nulls does not support it.** The only independent-method support for the cryptic site is therefore mixed, and this page previously showed it as a clean ✓ | ✓ ran — **mixed** | `R1` |
| **V16** | The causal matched-pair test `S` (RUNG 5a-KS, ligand-side double difference, §2.10e) | ⛔ **none — it has no known-answer calibrator** | **S = −0.1297 ± 0.3264 kcal/mol** — its **preregistered null**, registered in advance as the LIKELY outcome and explicitly **not** a stop. It is a **BOUND**: the design could only have resolved *"a wedge contribution of roughly \|S\| ≳ 0.65 kcal/mol (2σ)"* | ⛔ **`S` may be read as a bound and may NOT be reported as calibrated** (Open decision 13). `S` is non-covalent and therefore **structurally incapable** of testing the categorical mechanism; `S ≈ 0` means the *marginal* wedge is absent, and STOP applies only if the categorical axis has ALSO failed | ✓ complete — **preregistered null, uncalibrated** | `R11` |
| **V17** | The exposure criterion `EXPOSED_RSA = 0.25` | NR4A1 **Cys551** — the one NR4A-family covalent site with literature support | ⛔ **FAILS its own positive control** — RSA **0.165** on the state-matched opened model; **0 of 25** frames in the metadynamics ensemble, median **0.064** | ⛔ **anything adjudicated by this cutoff inherits a demonstrated false negative.** What survives is a threshold-free **rank**: C551 is 3/18 across the family on every accessibility observable, behind NR4A3's C397 and C420 | ✓ measured — **FAILS its positive control; rank-only** | `R8` `R15` |
| **V18** | The transfer-zone lysine-identity term (b) | ⛔ **none exists** | set membership, not energy: *unique-only* > *unique + conserved* > *conserved-only* | bound by two 2026-07-25 measurements: the ubiquitin-transfer distance is **17.1 Å** (the repo's assumed 10 Å was ~7 Å too strict) and **a composed CRL RING carries ~30–50 Å of positional uncertainty**, so ⛔ **no degradation-geometry claim may rest on a RING or E2 that was COMPOSED rather than observed** | ○ screen available — **no known-answer test** | `R12` |
| **V19** | The generation-matched null (winner's-curse / generative confound) | the scrambled-objective arm | **PARTIAL** — 0 manufactured survivors of 191 against the real campaign's 1 of 191. ⚠ that does **not** exclude the confound: rule-of-three bounds the manufactured rate at ≤0.0157, **3×** the real campaign's own 0.0052, Fisher **p = 0.5** | ⛔ **the arm that addresses the GENERATIVE step — a fresh generation into a paralogue pocket — is UNRUN** | ✓ one arm ran — **the decisive arm is ○** | `R7` `R15` |
| **V20** | Single-snapshot MM-GBSA `margin > 0` as a selectivity verdict | 38 unrelated marketed drugs through the identical funnel | ✕ **REFUTED** — 22 of 38 (58 %) score a positive margin, above the de-novo set's own 2 of 11 | ⛔ nothing. A signal smaller than its own noise is not recoverable by any downstream method — [§6a](#6a--dead--conclusively-unworkable-never-retry) | ✕ **dead** | (was `R7`) |

### 3.2 · The R×V coverage matrix — where the holes are

Read down a requirement's column: **the weakest cell sets its ceiling** (invariant 1). A column with no cell
at all is a hole.

| requirement | instruments that serve it | best available status | ⛔ hole? |
|---|---|---|---|
| `R1` pocket exists | `V13` `V14` `V15` | ✓ ran, mixed; one gate failed as registered | no — but no instrument is *validated on this system* |
| `R2` accessibility | `V13` | ⛔ the only demonstrated reading is ✕ dead | **effectively yes** |
| `R3` submission gate | — | — | ⛔ **HOLE** |
| `R4` binds at all | — | — | ⛔ **HOLE — needs a bench** |
| `R5` pose | `V3` | INCONCLUSIVE | **no usable answer** |
| `R6` ΔG_open | — | — | ⛔ **HOLE** |
| `R7` binder selectivity | `V4` `V6` `V7` `V8` `V9` `V10` | `V4` has **no result**; `V7` FAILS; `V9` defect open | no instrument, but **the one that matters is unrun** |
| `R8` linker reach | `V17` + enumeration | `V17` fails its own positive control | rank-only, and conditional on `R5` |
| `R9` our ternary assembled | `V2` | ✓ validated — **never pointed at our system** | **no usable answer** |
| `R10` ternary forms | `V2` `V12` | `V12` ⏸ FAILS | **no usable answer** |
| `R11` ternary adds selectivity | `V1` `V5` `V11` `V16` | `V1` passes in scope; `V5` FAILS; `V11` no pass; `V16` uncalibrated | **no usable answer** |
| `R12` degradation compatible | `V18` | no known-answer test exists | **untested instrument** |
| `R13` real biological object | ⚠ **`V`-less, but no longer rung-less** — [`fusion_cofold.py`](../modalities/fusion_cofold.py) is staged for the STRUCTURE tier | — | ⛔ **HOLE — with a rung and a price as of 2026-08-03** ([rung `S`](#rung-s--the-two-scope-rungs-r13-r14-claim-ceiling-conditions-deliberately-off-the-cum-chain)) |
| `R14` scope bound (AR/MR) | ⚠ **~8/9 built — the parts exist and were never assembled** | — | ⛔ **HOLE — with rungs and a price as of 2026-08-03, and its free half needs no nod** ([rung `S`](#rung-s--the-two-scope-rungs-r13-r14-claim-ceiling-conditions-deliberately-off-the-cum-chain)) |
| `R15` constructibility | RDKit + `V17` + `V19` | ✓ for one mechanism per molecule | design decision outstanding |
| `R16` target is a driver | delegated | — | not this paper's blocker |

⛔ **The readout: 5 requirements with no instrument, 5 more whose instrument has returned no usable answer,
and 0 requirements standing on an instrument validated in the regime the claim needs.**

### 3.3 · The pattern — rewritten, because the version this page carried was false

⚠ **SUPERSEDED, retained so it is not re-derived:** *"Every instrument put to a known-answer test either
passed cleanly or failed cleanly. **Every** claim that later had to be withdrawn came from an instrument that
had never been tested … skipping it has cost **three** retractions."* Both halves fail against this page's own
table and the paper's own census.

**What is actually true, and it is still worth making:**

1. **A known-answer test costs close to nothing and has never once been wasted.** Every instrument put to one
   returned a *readable* verdict — and readable is the whole point. That is the surviving lesson.
2. **But "passed cleanly or failed cleanly" is wrong.** Two rows returned neither: `V3` is **INCONCLUSIVE by
   its own pre-registered rule**, and the NR-V04 retrospective is a **NON-RESOLUTION**
   ([§the scoreboard](#-where-we-are--the-scoreboard-in-plain-language): *"⚠ **NON-RESOLUTION**, never a candidate control"*). A test that
   cannot resolve is a third outcome, and both of these were mis-read as failures at some point.
3. ⛔ **And "every withdrawn claim came from an untested instrument" is REFUTED by the largest retraction in
   the paper.** The NR-V04 per-arm figures fell to a **chain-ordering defect** (Elongin C scored as the
   target), an **nm/Å unit error** and **contaminated inputs** (14-3-3 ε where Elongin B belongs). **No
   known-answer test catches any of those** — the paper says so directly (`:933–936`): the panel persisted no
   trajectory, so the defects were *"each correctable in principle and **none correctable in practice**"*.
   The same is true of the E3-recruiter retraction (a biological-assembly frame defect, `:1600`) and the
   Gate-3B withdrawal (cross-replica divergence, `:403`).
4. **The count is not three.** On the paper's own naming there are **at least four** withdrawn *selectivity*
   results — the MM-GBSA "confirmed selective" headline, `denovo_111`, the negative conclusion that the
   ternary adds no selectivity, and the NR-V04 per-arm figures — and **six** if `denovo_94`/`denovo_57` are
   counted as the paper counts them (`:2610`), plus two further non-selectivity retractions. *"Three"* was
   quoted with no enumeration, in a document whose whole purpose is to stop facts being re-derived from
   prose. ✅ **STRATEGY.md's own *"it is how three selectivity results came to be withdrawn"* is gone** — it
   sat in that file's banner, which was rewritten out of existence when this merge folded the document in.
   Verified by search, not assumed: the phrase appears nowhere outside the audit record that quotes it. Closed
   in [§12](#12--findings-that-belong-to-other-documents).

**So the correct prophylactic is TWO rules, not one:** *(a)* test the instrument against a known answer
before believing it — cheap, and it caught rows 1 and 3; and *(b)* **persist the primary artifact**, because
the defects that cost the most were analysis and input bugs that only a retained trajectory could have let
anyone fix. Rule (b) is the one this page was missing, and it is the more expensive of the two.

### 3.4 · Three instrument facts this page used to be missing

⛔ **1 · `V6`'s accuracy citation does NOT cover the ternary or endpoint lanes, and a reader of this page
alone would have assumed it did.** The lanes split by charge model — **binary RBFE `am1bcc`** · **ternary FEP
NAGL** · **endpoint/covalent MD NAGL** — and the split is physically forced, not sloppiness (AM1-BCC via
AmberTools `sqm` ran **>85 min on a 166-atom recruiter without converging**). Three consequences, all binding:

- **ΔΔG_coop is unaffected by the split** — both morphs run inside one lane at one charge method, so the
  charge model cancels *within* a lane, which is all the argument ever needed.
- **Any CROSS-LANE subtraction is NOT safe**, which is why the protein-mutation wedge carries a hard
  `assert_charge_consistency` refusal.
- ⛔ **OpenFE's published accuracy was measured on `am1bcc`; neither it nor `V6` transfers to a NAGL lane.**
  The accuracy control for the NAGL lane is `V5` — **which failed.** [§Validation architecture](#validation-architecture-the-five-requirements):
  *"do not let a reader infer the OpenFE citation covers the ternary numbers."*

⛔ **2 · The program's flagship causal test `V16` has no known-answer calibrator, and buying one is on nobody's
rung.** It is rank 9 of the ladder's decision-value list and explicitly **unpriced**; Open decision 13 splits
the gap in two — *can a null be read?* ($0, **done**) and *can a non-null be called calibrated?* (paid,
**deferred**). ⚠ Open decision 9b binds any future calibrator: **reference data and structure must sit on the
SAME protein**, because the existing SMARCA calibrator is built on the lowest-resolution structure in the
family (3.73 Å) and on the wrong paralogue.

⛔ **3 · A LIGAND-SIDE DOUBLE DIFFERENCE DOES NOT INHERIT `V6`'s VALIDATION — BUT `R6` CANCELS OUT OF IT, SO
THIS PAGE'S `R6` BLOCK WAS TOO WIDE (added 2026-08-03; the analysis in full is
[`instrument-options.md`](../modalities/instrument-options.md) §2, which is its one home).** The quantity is
`ΔΔΔG ≡ ΔΔG_bind(d₀→d | NR4A3) − ΔΔG_bind(d₀→d | NR4A1)`, built from the same machinery `V6` passed on. Two
findings, and they point in opposite directions:

- **The inheritance FAILS, and it must not be assumed.** The solvent leg cancels **algebraically** — the same
  two molecules, the same box, the same λ schedule — so it drops out before any number is computed. ⛔ But the
  classes it removes are **exactly the classes `V6` also removed**, and what is left standing is exactly what
  `V6` **never measured**: a between-protein comparison. A within-pocket pass therefore says nothing about it,
  and `ΔΔΔG` needs **its own** known-answer test at paralogue scale. ⚠ The cancellation is also **conditional
  and must be enforced, not assumed** — same atom map, same partial charges, same λ schedule on both arms, or
  the ligand and mapping terms stop cancelling too. This repo already enforces and verifies that
  (`nr4a3_rbfe.strip_foreign_partial_charges`, `assert_charge_consistency`).
- ⭑ **But `R6` — the opening penalty nobody has computed — drops out to FIRST ORDER, and this page stated the
  block globally.** Validation requirement 2's *"can miss or REVERSE selectivity"* bites on an **absolute**
  per-paralogue affinity, where `ΔG_bind,obs ≈ ΔG_open + ΔG_bind|open`. In a **relative** quantity the opening
  penalty is common to both ligands of a matched pair and cancels **inside each protein**, before the
  between-protein subtraction is taken. **So `R6` blocks the ABFE route to `R7` and does not block a `ΔΔΔG`
  route to `R11`'s causal question** — a real narrowing of the blocker set, corrected in
  [§2.1 row `R6`](#21--the-register), [§5 row R6](#5--where-each-requirement-stands) and
  [§8 Route A](#-where-route-a-is-blocked--three-things-and-only-one-of-them-is-the-instrument).
- ⚠ **It is an ARGUMENT, not a measurement**, and is recorded as one — the same register this page already
  uses for *"'not implicated' is an argument, not a measurement"*. Its condition: the cancellation holds to
  the extent that `d` and `d₀` select the *same* open sub-state, which is a good approximation for a matched
  pair differing by one small element and a poor one for two dissimilar molecules.
- **What it licenses is a CAUSAL/DESIGN statement** — *"this structural element contributes X more in NR4A3
  than in NR4A1, with both receptors in their modelled open states"* — and **never** an absolute selectivity
  claim (*"N-fold selective"*), which still needs `R6`. ⛔ Nothing here raises a claim ceiling: no `ΔΔΔG` has
  been computed, and the instrument is at *proposed*. Its two **$0** searches for a paralogue-scale benchmark
  are [§10.1 row 27](#101--open-rows-ordered-by-what-unblocks-the-most).

---

## Validation architecture (the five requirements)

*★ **THE EXTERNAL REVIEWER'S FIVE CONDITIONS** on what a result may claim — the constraint layer over [§3](#3--instruments--which-one-answers-each-requirement)'s instrument table. ⚠ **Cite these as "validation requirement 1–5", never as "R1–R5"** — [§0.6](#06---five-different-things-in-this-program-are-called-r) lists five different things in this program called `R`. Mapping onto the registers: requirement 1(A)→`V6`, 1(C)→`V5`, 2→`R6`, 3→`V9`, 4→[§6a](#6a--dead--conclusively-unworkable-never-retry)'s NR-V04 row, 5→`R12` and `R13`.*

These come from the external reviewer's conditional approval ([verbatim
verdict](nr4a3-degrader-reviewer-revisions-2026-07-15.md)) and govern what any result is
allowed to claim.

1. **Three DIFFERENT validations — never let one stand in for another.**
   - **(A) Accuracy control** — a compact *public* RBFE benchmark (measured ΔΔG + supported poses) through the
     *exact* container / protocol / force field / water model / sampling / analysis used for NR4A. Cycle closure,
     fwd/rev agreement, and MBAR overlap are **precision diagnostics, NOT accuracy** — a closed cycle can be
     systematically wrong.
   - **(B) Target-specific precision** — the cmpd19 RBFE, framed as *conditional relative free energies for a
     hypothesized cmpd19 mode within preselected open NR4A conformers.* It tests reproducibility and
     receptor-sensitivity, **not** binding-model correctness (cmpd19 has no measured affinity, no pose).
   - **(C) Ternary known-answer control** — a system with an experimental ternary structure + measured
     binary/ternary affinity/cooperativity + an analogue series (VHL–BRD4 or VHL–SMARCA2). **NR-V04 is a
     biological-selectivity holdout, not the method calibrator.**

2. **Cryptic-pocket thermodynamics are conditional.** An affinity computed in a pre-opened pocket is
   ΔG_bind|open, not the observable ΔG_bind,obs ≈ ΔG_open + ΔG_bind|open. Each paralogue can have a **different
   opening penalty**, so comparing binding only in matched open receptors can miss or REVERSE selectivity.
   Either integrate a converged **ΔG_open per paralogue**, or report everything **explicitly conditional** on the
   chosen open states. Pocket collapse in MD is *evidence the state is unstable*, not an auto-fail; restraint free
   energies must be included or the result stays conditional; **do not** claim "under-sampling means true binding
   is likely stronger" (bias runs both ways). Never pool conformers of unknown population as equally weighted;
   use Boltzmann weighting where estimable, else report sensitivity ranges — never a synthetic "ensemble affinity."

3. **ABFE is HELD and reframed.** T4L-L99A·benzene is an implementation smoke test, **not a transferable
   offset** — report raw ABFE, report the T4L discrepancy separately, apply no offset. ABFE does **not** prove
   cmpd19 "binds at all"; it only asks whether the hypothesized pose is thermodynamically plausible under the
   modeled assumptions. Not worth running until the accuracy benchmark passes, the opening penalty is handled,
   and multiple poses are treated. Step 8 cannot "consume the anchor ABFE per construct" — linker/recruiter
   attachment alters the bound ensemble, so free-cmpd19 ABFE ≠ each degrader's binary affinity. **HELD also means
   the λ-overlap repair of the existing ABFE block is parked, not in flight** — the manuscript must say so.

4. **NR-V04 is covalent.** Celastrol binds NR4A1 **covalently via C551**, so NR-V04 does not validate the
   noncovalent machinery used for cmpd19, and its selectivity may be largely **target-engagement**, not ternary
   cooperativity. Model a **preformed covalent adduct**; add a **noncovalent-vs-covalent sensitivity analysis**,
   an **NR4A1 C551A / nonreactive control**, and **warhead-only + active/inactive recruiter** controls; use
   scoring rules preregistered on control (C). Report only **directional concordance** with the reported
   NR4A1-degraded / NR4A2·3-spared outcome — never "recovered degradation."

5. **The prospective stage is hypothesis PRIORITIZATION, not scoring.** Replace any tunable scalar with **staged
   gates + a Pareto/constraint-satisfaction front** (binary plausibility → ternary thermodynamic/ensemble →
   linker strain → ubiquitination geometry → physicochemical → robust selection), with uncertainty on every
   axis. Model the **real biological object, EWSR1::NR4A3** (not an isolated LBD): fusion-context ensemble;
   lysines **outside** the LBD (hinge, DBD, fusion partner); public EMC VHL/CRBN expression; **full CRL/E2~Ub
   geometry ensembles**. Ternary formation is necessary, not sufficient — productive lysine positioning is a
   distinct requirement.
   **★ TWO MEASUREMENTS LANDED HERE 2026-07-25 (LANE 2, $0), and BOTH correct assumptions the program was
   using — they bind on every ternary / degradation-geometry step, not just 5a:**
   - **The ubiquitin-transfer distance is 17.1 Å, MEASURED** — nearest of 11 substrate lysines in a *solved*
     CRL4–CRBN assembly. The repo's assumed **10 Å was ~7 Å too strict** and, applied as written, **would have
     been the wrong scale and would have MATERIALLY WEAKENED the term-(b) lysine signal.** ⚠ *Corrected
     2026-07-25: an earlier "would have suppressed it entirely" is **contradicted by the committed sweep** —
     84/192 basins still reach rank ≥3 at 10 Å, against 75 at 17 Å.* Any transfer-zone criterion must use the
     measured band.
   - **⚠ A COMPOSED CRL RING CARRIES ~30–50 Å OF POSITIONAL UNCERTAINTY** *(measured on both arms 2026-07-25:
     **VHL 30.18 Å, CRBN 50.14 Å** — the original 48.6 Å was one arm. **NOT IN FORCE in the authoritative
     Tier-2 run**, which anchors both arms on the observed E2 catalytic cysteine rather than a composed RING.)*
     Original finding:** A known-answer check *falsified its
     own construction*: a RING composed from a receptor entry + a cullin scaffold — with **both bridges < 1.5 Å** *(true of the 48.58 Å pair only; CRBN's own-assembly bridge is **1.916 Å** — and CRBN carries two live composed-RING numbers, 48.58 and 50.14, through different bridges, which is a one-fact-one-place hazard)*,
     i.e. each join individually excellent — sat **48.6 Å** from the RING of an intact deposited assembly. This
     is **conformational, not error**: CRLs are genuinely mobile, so a well-fitted composition is still not a
     position. **Consequence: no degradation-geometry claim may rest on a RING or E2 that was COMPOSED rather
     than observed.** The fix in use is to anchor on the **observed E2 catalytic cysteine** from solved
     assemblies (**8R5H** for VHL, **9UUM** for CRBN). Relatedly, the E2 catalytic cysteine had been *guessed*
     by a heuristic; identifying it by proximity to ubiquitin's C-terminus gives **Cys85 at 3.4 Å vs 16.4 Å**
     for the next-nearest — and **overturns the heuristic's answer**.

### Why Val A is nearly free but Val B is load-bearing

**Val A (binary RBFE accuracy) — a citation, not a paid benchmark, FOR THE BINARY LANE ONLY.** We run OpenFE's
*standard* RelativeHybridTopology protocol, already benchmarked (~1.7 kcal/mol over 58 public systems). The only
thing that had made it non-citeable was a self-inflicted deviation — the RBFE env shipped without AmberTools, so
am1bcc charging failed and fell back to the NAGL surrogate. With AmberTools added and `am1bcc` restored, the
**binary RBFE lane** is on the documented reference method → we **cite OpenFE** and run only a ~$0–15
build-consistency smoke (valA_mini, done).

**The charge model is NOT shared across lanes.** The lanes split:

| Lane | Charge model | Evidence |
|---|---|---|
| Binary RBFE (`nr4a3_rbfe.py`) | **am1bcc** | code default; valA_mini/step0/step1_pilot all ran am1bcc |
| Ternary FEP (`nr4a3_ternary_fep.py`) | **NAGL** | **the stored hybrid `System` of every banked valB leg, read 2026-07-29** ([`charge-provenance-forensic.json`](../modalities/charge-provenance-forensic.json)) — *not* the `gpu-ternary-fep-gcp.yml` default or the `CHARGE_METHOD: nagl` log line, which record what was requested ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 47) |
| Endpoint / covalent MD | **NAGL** | `md_settings.py:60` `CHARGE_METHOD = "nagl"` |

The split is **physically forced, not sloppiness**: AM1-BCC via AmberTools `sqm` is intractable on PROTAC-sized
ligands — measured 2026-07-22, `sqm` ran **>85 min on the 166-atom NR-V04 recruiter without converging**
(`md_settings.py:53–60`). NAGL is an ML surrogate *for* am1bcc, so this is a defensible substitution, but it is a
**different Hamiltonian** and must be handled explicitly:

1. **ΔΔG_coop is SAFE — and this is now MEASURED FROM THE SYSTEMS, not read off the configuration
   (2026-07-29, $0, `task=charge-provenance`).** Both morphs of the cooperativity cycle
   (`ternary − binary-of-the-same-PROTAC`) run inside the ternary lane at the same `CHARGE_METHOD`, so the
   charge model cancels; the cancellation argument holds *within* a lane, which is all it ever needed.
   ⚠ **But `CHARGE_METHOD` is what was REQUESTED, and for a while that was the only evidence there was.**
   OpenFE prefers user-supplied charges over its configured `partial_charge_method`, and every relaxed pose
   file on this lane carries a complete per-atom set for its λ=0 endpoint — so a `partial_charge_method = nagl`
   log line proves nothing about what a leg actually sampled, and the failure mode it hides is silent by
   construction ([`nr4a3_rbfe.strip_foreign_partial_charges`](../modalities/nr4a3_rbfe.py), third
   failure mode). Every banked valB leg's stored hybrid `System` was therefore read: the arms of r0, r1 and r2
   carry **identical** alchemical charges (109/109 core atoms), the reverse leg's endpoints are the forward
   leg's swapped, and the inherited set is the protocol's own NAGL set — fixed by the binary arm, which ran
   with **nothing to inherit** and produced the same numbers. One home for the per-leg evidence:
   [`charge-provenance-forensic.json`](../modalities/charge-provenance-forensic.json). Superseded (the
   configuration-only basis): [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 47.
2. **Any CROSS-LANE subtraction is NOT safe.** A quantity built as `(ternary-lane leg) − (binary-lane leg)`
   mixes NAGL against am1bcc, and a charge-model difference is a real potential-energy-surface difference that
   does **not** cancel. Such cycles must pin one `CHARGE_METHOD` across **both** legs — this is why the
   protein-mutation wedge (RUNG 5a-KS confirmatory) carries a hard `assert_charge_consistency` refusal.
   (Timestep differs across lanes too — 2 fs ternary vs 4 fs+HMR binary — but HMR changes only masses, so that
   is a *sampling/precision* difference, not a bias in ΔG.)
3. **Val A's citation does not cover the NAGL lanes.** OpenFE's published ~1.7 kcal/mol accuracy was measured on
   the am1bcc method; valA_mini reproduced a known ΔΔG on am1bcc. Neither transfers to a NAGL ternary lane. The
   accuracy control for the NAGL lane is **Val B** (its own known-answer PROTAC) — which is why valA_full's
   "re-open if am1bcc is forced onto NAGL" trigger is satisfied *by Val B* and not by a separate paid NAGL
   binary benchmark. Say this in the paper; do not let a reader infer the OpenFE citation covers the ternary
   numbers.

**Val B (ternary cooperativity) — genuinely needed, for pipeline-validation.** The general approach is citeable
(prior art above), but you never certify your own container / force field / charge model / ternary wiring by
pointing at someone else's engine's benchmark. NR-V04 cannot calibrate it (no solved ternary; celastrol is
covalent, so it doesn't even exercise the noncovalent morph). The only way to know our cooperativity numbers
mean anything is to run a known-answer PROTAC (VHL–BRD4 / VHL–SMARCA2) through our own pipeline. **Val B-mini is
the highest-value dollar in the plan** — the cheapest gate on the entire prospective ladder.

---

## 4 · The dependency graph

Read upward: a box can only be claimed once everything feeding it holds. **Dashed edges are validation
dependencies** — the instrument that produces a claim must itself have been shown to work. Node glyphs carry
the state, so the graph reads the same without colour. **No node here is ✕ today** — not because claims are
exempt from being dead, but because none of these has been refuted. An unreached claim is ○; the approaches
that *were* conclusively closed are in [§6](#6--the-closed-route-register).
**Node glyphs carry work state only — [§0.3](#03--three-orthogonal-axes--work-state-authorization-sufficiency)'s
authorization and sufficiency axes are read from the register rows, never from the graph**, which is why `V4`
carries its 🔒 inline rather than being demoted to a colour.

⚠ **Four requirements are not drawable here and that is a property of the graph, not of them.** `R3`
(submission gate), `R13` (fusion-context object) and `R14` (AR/MR scope) are **claim-ceiling conditions** that
bound every node rather than feeding one, and `R2` sits inside `R1`. They are in
[§2.1](#21--the-register) and on the roadmap; a graph that showed them as ordinary boxes would imply they can
be discharged in sequence, and they cannot.

```mermaid
graph BT
  P["○ PAPER — a defensible<br/>NR4A-paralogue-selective<br/>degrader candidate"]
  B["○ R7 · BINDER selective<br/>over NR4A1/NR4A2"]
  T["○ R10 · TERNARY forms"]
  UB["○ R12 · Ternary is compatible<br/>with DEGRADATION — productive<br/>unique-lysine geometry"]
  TS["○ R11 · TERNARY adds or<br/>preserves selectivity"]
  TG["○ R16 · Target is a driver (EMC<br/>dependence) — DELEGATED"]
  L["○ R4 · Something BINDS<br/>the NR4A3 pocket"]
  PO["✓ R1 · Pocket exists and<br/>is reachable"]
  DGO["○ R6 · Opening penalty per paralogue<br/>ΔG_open — NEVER MEASURED"]
  PS["○ R5 · POSE — where the<br/>molecule sits"]
  LK["✓ R8 · LINKER geometry<br/>computed — not reconciled"]
  ARCH["○ R9 · OUR ternary correctly<br/>ASSEMBLED — no rung, no price"]
  V1["✓ V1 · Selectivity readout<br/>detects a known answer"]
  V2["✓ V2 · Generator CAN build a<br/>known ternary — not ours"]
  V3["✓ V3 · Pipeline recovers a known<br/>ligand pose — INCONCLUSIVE"]
  V4["○ V4 · Physics recovers a known<br/>SELECTIVITY ddG — 🔒 not authorized"]
  V5["⏸ V5 · Ternary FEP recovers a known<br/>cooperativity — FAILED on sign"]

  PO --> L
  L --> PS
  PS --> B
  DGO --> B
  PS --> LK
  LK --> T
  ARCH --> T
  T --> TS
  T --> UB
  UB --> P
  B --> P
  TS --> P
  TG -.delegated.-> P
  V3 -.validates.-> PS
  V4 -.validates.-> B
  V2 -.validates.-> ARCH
  V1 -.validates.-> TS
  V5 -.validates.-> TS

  classDef done fill:#dff0e4,stroke:#2f8f5b,stroke-width:2px,color:#10231a;
  classDef work fill:#dee7fa,stroke:#3a63b8,stroke-width:2px,color:#111f38;
  classDef next fill:#f0ece1,stroke:#8d8674,stroke-width:1px,color:#2a271f;
  classDef parked fill:#ece3f6,stroke:#6f4a9b,stroke-width:2px,color:#1e1030,stroke-dasharray:2 3;
  classDef dead fill:#f7e6e0,stroke:#b1543a,stroke-width:2px,color:#2e150f,stroke-dasharray:5 3;

  class PO,LK,V1,V2,V3 done;
  class P,B,T,UB,TS,TG,L,ARCH,DGO,PS,V4 next;
  class V5 parked;
```

⚠ **`§4` NOW CARRIES NO ◐ NODE, AND THAT IS A CORRECTION RATHER THAN A DESIGN CHOICE.** Three nodes read ◐
until this pass — `PS`, `LK` and `V3` — and **nothing was running behind any of them**, which under
[§0.2](#02--work-state--the-five-glyphs)'s own semantics was an instruction to every reader not to start work
nobody had started. Each is corrected against its committed artifact:

- **`V3` ◐ → ✓.** [`apo-pose-recovery.json`](../modalities/apo-pose-recovery.json) carries a complete
  `verdict` (`outcome: INCONCLUSIVE`), a 6-pair panel and an elapsed time. **The test ran and returned.** This
  page's own instrument table, claim register and branch-2 question node already said so; only the graph did
  not. *Superseded, retained: the `◐` on `V3` and the phrase "running, not returned".*
- **`PS` ◐ → ○.** The known-answer test returned; the **re-run with the site and docking questions separated
  has not started**. Nothing is billing on any lane.
- **`LK` ◐ → ✓.** [`nr4a3-linker-covalent-reach.json`](../modalities/nr4a3-linker-covalent-reach.json)
  **landed at commit `dc0befd9c`**, which retires the branch-1b banner's *"the artifact this section cites
  does not exist yet"*. ✅ **The hold on quoting branch 1b is DISCHARGED (2026-08-03)** — the prose was reconciled to the landed artifact claim by claim, and the one live contradiction left (the mermaid `PAR` node's "which NR4A3 does NOT have") is corrected in the same pass. ⚠ *Superseded, retained: "**The hold on quoting branch 1b stands for a different and now-measurable reason** — the prose has not been reconciled to the landed artifact."* —
  the prose has not been reconciled to the landed artifact, and at least one disagreement is readable today
  ([§7 branch 1b](#branch-1b--computed-not-reconciled-to-its-artifact)). *Superseded, retained: "the
  artifact this section cites does not exist yet" and the `◐` on `LK`.*

⚠ **PAPER is ○, not ✕ — the goal is blocked, not refuted.** What blocks it:

- **`ARCH` (`R9`) is ○, not ✓ — no NR4A3 ternary has been correctly assembled by anyone.** It is the claim
  *"**our** ternary is correctly assembled"*, which [§what the SMARCA2/4 null BINDS](#what-this-binds-in-the-words-fixed-before-the-run) answers flatly:
  *"⛔ **NO, and this is the whole remaining gap.**"* (`nr4a-ternary-ligand-provenance.json`: `n_recovered: 0`
  of 3 arms.) `V2` is the *instrument* reading — the generator **can** build a known ternary, best-of-16 on
  one arm of one non-NR4A3 system — and keeping the two apart is what makes the dashed edge non-circular:
  a validated instrument that has not yet been pointed at our system. ⚠ **Superseded, retained:** the ✓ on
  `ARCH`, under which one proposition carried four different states across two files (graph ✓, claim register
  ○, critical path ◐, STRATEGY.md ⛔ NO).
- **`PO` (`R1`) is ✓ — the pocket WORK is complete; the pocket CLAIM is supported but not settled.** ★ **This
  node was briefly ○, and that was wrong twice over (trimcrae, 2026-08-02: *"What do you mean by the pocket
  existing doesn't get a checkmark? That makes me think your standard is too high."*).**
  1. **It broke invariant 4.** ✓ is a **work state**, never a claim's truth. ○ means *not started*. An
     enormous amount of pocket work has run and returned: the 8XTT harmonization, the release run, 60 ns of
     metadynamics plus three independent-seed replicas. Rendering that ○ tells a reader nobody
     has looked. That is the same axis-collapse this page keeps catching elsewhere — here, *not settled*
     collapsed into *not started*.
  2. **It misread what Gate 1 refuted.** Gate 1 tested a **two-state cryptic opening**, and what failed is
     that *mechanism*: F(Rg) is monotonic, *"a single resolved minimum and a rising wall, with no separate
     opened minimum"* — so *"'opened **state**' would overstate it"*. The paper reformulates to
     **basin-internal breathing** and keeps the cavity: *"there is one basin whose thermal fluctuations
     **transiently expose a druggable cavity**"* (`nr4a3-degrader-paper.md:387–396`), concordant with de Vera's
     breathing Nurr1 pocket. **A failed mechanism test is not evidence of absence.**
  3. **The existence evidence is EXPERIMENTAL and independent of all of it** — in the deposited apo NMR
     ensemble **8XTT** the orthosteric pocket is matched in **19 of 20** conformers, 3 scoring ≥ D\*, **with no
     simulation bias applied**, and Gate 3A (persistence after bias removal) is supported.
  ⚠ What remains genuinely open belongs to **accessibility and provenance, not existence**: that is `R2`
  (Gate 3B) and `R3` (the submission gate), which is why they have their own ids rather than living as
  footnotes on `R1`. **Superseded, retained:** the `○` on `PO`, and the earlier phrase *"settled enough to
  build on"* which erred in the opposite direction by eliding both open gates.
- **`T` has been split.** It used to read *"TERNARY forms **and is compatible with degradation**"* — two
  claims in one box, and precisely the distinction [§Honest scope](#honest-scope-and-language-discipline-apply-everywhere-including-the-manuscript) validation
  requirement 5 exists to preserve: *"Ternary formation is **necessary, not sufficient** — productive lysine
  positioning is a distinct requirement."* `UB` (`R12`) is now that second claim, and nothing on this page had
  carried it.
- **`DGO` (`R6`) is a way `B` can come out *backwards*.** Validation requirement 2
  ([§MECHANISM-FIRST](#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged)): *"Each paralogue can have a **different opening penalty**, so
  comparing binding only in matched open receptors can **miss or REVERSE selectivity**."* Every ΔΔG on the
  binder path is conditional on a term that has never been computed — so **Route A is not blocked only on its
  instrument**, which is how this page previously read.
- **`V5` is the program's hardest instrument failure and had no node until 2026-08-02.** The ternary
  known-answer control (`valB_mini` ΔΔG_coop, validation requirement 1(C)) **failed on the sign**, and
  [§Validation architecture](#validation-architecture-the-five-requirements) calls it *"the highest-value dollar in the plan"*. It is ⏸ not ✕
  because the closure triangle localises the miss to an **endpoint-state** error, which more sampling cannot
  fix but a different ternary free-energy method could.
- **`TG` (`R16`) is a delegated edge, not a solid one.** The paper (`:2508`) puts the make-or-break dTAG test
  in the EMC-program paper and states *"This paper's claimed contribution is the target's computational
  druggability/selectivity, **not EMC efficacy**"* — so `TG` is a precondition of the *therapeutic* claim,
  not of this paper.

**The refuted *approaches* underneath these are in [§6](#6--the-closed-route-register)
— that is the distinction the states exist to keep visible.**

---

## 5 · Where each requirement stands

The **state** column is the work item that would move the requirement, not a grade on the evidence.

| id | evidence today | what would settle it | state |
|---|---|---|---|
| **R1 · A pocket exists** | in the experimental apo NMR ensemble **8XTT**, the orthosteric pocket is **matched in 19 of 20** conformers, of which **3 score ≥ D\*** — i.e. **3/20 across all deposited conformers**, no simulation bias applied ([`nr4a3-pocket-reharmonize-summary.json`](../modalities/nr4a3-pocket-reharmonize-summary.json), row `8xtt_20conformers`); Gate 3A (persistence after bias removal) supported (`V13`); orthogonal support from `V14` (BioEmu, 12.5 % druggable) and `V15` (PocketMiner, ⚠ 4 of 5 nulls) | ⛔ **NOT settled — and the three open gates now have their own ids.** (i) Pre-registered **Gate 1 (a genuine two-state cryptic *opening*) FAILED as registered** — ⚠ this refutes the *two-state mechanism*, **not the cavity**, which the paper keeps as basin-internal breathing (`:387–394`, `:2549`). (ii) **`R2`** — Gate 3B, equilibrium accessibility. (iii) **`R3`** — the frame-level submission gate | ✓ work complete · claim **supported, not settled** |
| **R2 · The state is equilibrium-accessible** | ⛔ the ~0.6 kcal/mol single-trajectory estimate is **withdrawn**: three independent-seed replicas do not reconstruct a common F(Rg), the basin sits at a different Rg in each, and basin→druggable ΔF differs by many kcal/mol | a reading of Gate 3B that is not a single biased profile — that specific route is ✕ ([§6a](#6a--dead--conclusively-unworkable-never-retry)); the gate itself is open | ○ future — **no usable instrument answer** |
| **R3 · The generation receptor still qualifies** | ⛔ the harmonized artifact reports **ensemble-level fractions only** and does **not** identify which individual frames cleared D\*, so it does not discharge the frame-level check that the **exact release-derived frame `denovo_401` was generated into still qualifies** — and *"if the generation frame does not qualify, the **generation receptor** … is affected"* (`:2259–2265`) | the frame-level dependency audit — **$0-to-cheap, and the cheapest open item in the program** | ○ future — **nothing built** |
| **R4 · Something binds it** — scoped: **the opened cryptic Pocket-5** | ⚠ **Two different questions, and this page previously ran them together.** *Does anything bind NR4A3 at all?* — **yes, published**: a fragment screen against NOR-1/NR4A3 (hit rate <1 %) returned three chemotypes, one elaborated to a **low-micromolar inverse agonist** (Zaienne cmpd19) that shifted NOR-1-regulated gene expression in cells (`:92–99`), and the congeneric lane is anchored on it. *Does anything bind the **cryptic pocket**?* — **nothing, of any molecule**: those results *"leave the binding site **structurally undefined**"* (`:99–101`) | a thermal shift / SPR / NMR fragment screen **against the opened site**. **Cheapest decisive experiment in the program**, and a negative is as useful as a positive. ⚠ The scoping word is load-bearing — dropping it makes this page claim there is no experimental ligand evidence for NR4A3, which the paper's §1 contradicts | ○ future — **needs a wet lab** |
| **R5 · The pose is right** | ⛔ the known-answer test **ran and returned INCONCLUSIVE** ([`apo-pose-recovery.json`](../modalities/apo-pose-recovery.json)) — and its decomposition splits the question in two: the **docking** is fine (**3.04 Å** blind from apo through an fpocket-chosen box, fnat 0.778, 7 of 9 native contacts), the **site selection** is what missed, on 6 of 6 pairs. ⚠ **Superseded, retained: 3.46 Å** — that value was read off an earlier generation of this same artifact (commit `cc4325b68`, `blind_apo_fpocket_top_box` 3.464) and never re-read after regeneration at `060a6a653`; the current arm reads **3.04**, and the oracle-box arm — a *different* arm — reads 3.489 | re-run the primary arm with the site question separated from the docking question — see [§7 branch 2](#7--branches-still-open) | ✓ test complete, claim **unresolved** |
| **R6 · ΔG_open does not reverse the margin** | ⛔ **nothing. Never computed, for any paralogue.** ⚠ **What it blocks was narrowed 2026-08-03:** it is a term in an **absolute** per-paralogue affinity, and it **cancels inside each protein** in a ligand-side *relative* double difference — so it blocks the ABFE route to `R7` and not a `ΔΔΔG` route to `R11`'s causal question ([§3.4 fact 3](#34--three-instrument-facts-this-page-used-to-be-missing)) | a converged opening penalty per paralogue — priced in the ladder's OPTIONAL/HELD tier. Otherwise: **report everything conditional on the open state**, which is $0 and fully defensible | ○ future — 🔒 **explicit nod only** |
| **R7 · The binder is paralogue-selective** | ⚠ **More than this page used to say, and weaker than it sounds.** The paralogue ABFE **has been run and reported at three independent-seed replicates** with exactly the replicate-SD error bars this row used to ask for: ΔΔG(NR4A3−NR4A1) **−4.76 ± 2.03**, ΔΔG(NR4A3−NR4A2) **−4.98 ± 0.68**, both resolved below zero (`:1230–1239`, `:2303`). It is held **provisional and deliberately parked** for a named defect — `V9`, a soft-core-tail λ-overlap failure on *every* leg — *"It is not currently running: the whole ABFE block is **deliberately held** … it is not the next thing worth computing"* (`:1277–1280`). **"Run, reported, consciously parked" ≠ "not started"**, which is what this row said before. The paper's live reading is that selectivity rests on the binder margin **plus the nominated categorical handles**, and it explicitly refuses to write the ternary off (`:2600–2601`; SI `:141–144`) | **Three things, and they are not the same thing.** (1) **The instrument:** `V4`, the CREBBP/BRD4 selectivity known-answer test. *(highest leverage in the program · 🔒 **not authorized** · would **not** discharge this row — it is a **binary** control.)* (2) ⛔ **The missing physical term:** `R6`. A perfect instrument on today's inputs still would not settle this row. (3) ⛔ **The size of the prize versus the resolution** — the margin arithmetic in [§1](#1--the-thesis-the-north-star-and-the-operating-regime). ⚠ **This row is therefore not blocked *only* on the instrument**, which is how the page read before 2026-08-02 | ○ open — ⏸ **the existing result is parked**, not absent |
| **R8 · A linker geometry is feasible** | ✓ computed and committed ([`nr4a3-linker-covalent-reach.json`](../modalities/nr4a3-linker-covalent-reach.json), `dc0befd9c`): only **C397** of the three unique LBD cysteines is within tether range; **C420 is refuted everywhere** (0 of 60 placement×pendant cells, both conventions); ⚠ **C559 is NOT** — it survives at exactly one cell (`vhl|M3@term_a_exemplar | dab_branch`, 2 of 19 conformers) under through-space, and the artifact's `refuted_unique_cysteines` label is built from `best_corridor` alone, so it is stronger than its own data. ✅ **RECONCILED 2026-08-03**, claim by claim — see [§7 branch 1b](#branch-1b--computed-not-reconciled-to-its-artifact) | reconciling the prose to the artifact ($0), then the pose re-run `R5` that every anchor depends on | ✓ work complete · claim **conditional on `R5` and unreconciled** |
| **R9 · Our ternary is correctly assembled** | ⛔ **nothing. `n_recovered: 0` of 3 arms**, and the existing prediction was built by the ⏸ route from a molecule that is unrecoverable | rebuild by the assembly route (`V2`) from a recorded molecule — ⛔ **and it has no rung, no gate and no price** | ○ future — **NOT STARTED · 🔒 unpriced** |
| **R10 · A ternary forms** | predicted for all three paralogues at comparable confidence, built by the failing route — and the molecule used is **unrecoverable**, so it cannot be replicated | `R9`, then rebuild by the assembly route from a recorded molecule | ○ future — the *result* is ✕ ([§6a](#6a--dead--conclusively-unworkable-never-retry), unregenerable), the *route* that built it is ⏸ ([§6b](#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen)), the requirement is open |
| **R11 · The ternary adds selectivity** | one sequence-encoded candidate (Glu208 → Pro in NR4A1, Tyr in NR4A2); five further hits were placement artifacts; reproducibility untested at one model per arm. ⚠ **And the causal test has run**: `V16` returned **S = −0.1297 ± 0.3264**, a preregistered null carrying a bound of \|S\| ≳ 0.65 kcal/mol — *"the **only** test in this program that asks whether a designed element **causes** discrimination"* (`:1782–1783`) | credible ternaries × ≥3 models per paralogue, scored by `V1` — gated on `R9`. And a known-answer calibrator for `V16`, which is unpriced | ○ future |
| **R12 · Ternary is compatible with DEGRADATION** | ⛔ **nothing** — this claim had no row and no node until 2026-08-02, and it is a **distinct requirement** from "a ternary forms" ([§Honest scope](#honest-scope-and-language-discipline-apply-everywhere-including-the-manuscript) validation requirement 5). What exists is the categorical input, not the geometry: **four NR4A3-unique lysines**, of which **K518, K572, K592** are exposed in the LBD at 13.4 / 11.5 / 16.2 Å from the cryptic pocket ([`nr4a-paralogue-unique-residues.json`](../modalities/nr4a-paralogue-unique-residues.json) `gate.exposed_unique_lysines`) | `V18` — *which* lysine does the modelled E2~Ub transfer zone cover? Scored *unique-only* highest, *unique + conserved* next, *conserved-only* lowest; set membership, not energy. Against the **17.1 Å** ubiquitin-transfer distance in a *solved* CRL4–CRBN assembly (the repo's assumed 10 Å was ~7 Å too strict), and requiring a full CRL/E2~Ub ensemble rather than a **composed** RING. ⚠ Honest limit carried from validation requirement 5: real degraders often ubiquitinate several lysines and lysine-less substrates can still be degraded, so this **raises the odds; it does not guarantee** the paralogue is spared | ○ future |
| **R13 · The modelled object is EWSR1::NR4A3** | ⛔ **nothing, anywhere.** Every structure on this page is an isolated LBD construct (373–626) — which is already load-bearing: the fourth unique cysteine, **C166**, is outside it and unavailable to any LBD-anchored design | a fusion-context ensemble; lysines outside the LBD (hinge, DBD, fusion partner); public EMC VHL/CRBN expression; full CRL/E2~Ub geometry ensembles — validation requirement 5, in its own words | ○ **not started** — ✅ **PRICED and GATED 2026-08-03**: `R13-a` **$0** (needs no nod) → `R13-b` **~$0.66** ([rung `S`](#rung-s--the-two-scope-rungs-r13-r14-claim-ceiling-conditions-deliberately-off-the-cum-chain), [`scope-rung-cost.json`](../modalities/scope-rung-cost.json)), with the *full* requirement-5 object explicitly **unpriceable** and the reasons named. ⚠ *Superseded, retained: "🔒 **unpriced, and on no list until this pass**".* |
| **R14 · Scope is bounded (AR/MR)** | ⚠ **more than "nothing run", and this row understated it.** The sequence screen HAS run and flagged exactly **NR3C2 (MR)** and **AR**; the anti-target docking harness has run at panel scale; **AR is already a panel target**; `denovo_401` is already staged against it. ⛔ What has never happened is the **assembly**: MR is not in the panel, the panel's own cognate-ligand self-control has never been run, and the SI's second requirement — a cryptic-pocket-formation test on AR/MR — has no result. Pointers: [`instrument-options.md`](../modalities/instrument-options.md) §3.2. SI names MR and AR *"the **sole** sequence-level non-paralogue follow-ups"* that *"must clear"* (SI `:213–219`). ⚠ *Superseded, retained: "⛔ **nothing run**".* | an energetic cross-binding check against MR and AR — **assembled from parts that exist**, not built from nothing | ○ **not started** — ✅ **PRICED and GATED 2026-08-03**: `R14-a` **$0, no nod** (and its self-control gates SI §S1's own published margin) → `R14-b` **~$3.41**, ⛔ **registered DO-NOT-LAUNCH** on a rate-line question that is a decision for trimcrae, behind a $0 precheck; `R14-c` (FEP) **closed** as downstream of §10.1 row 2 ([rung `S`](#rung-s--the-two-scope-rungs-r13-r14-claim-ceiling-conditions-deliberately-off-the-cum-chain), [`scope-rung-cost.json`](../modalities/scope-rung-cost.json)). ⚠ *Superseded, retained: "🔒 **unpriced**".* |
| **R15 · The candidate set is constructible** | ✓ the virtual linker library is chemistry-verified end to end — **54 constructs (36 exemplar + 18 representative), RDKit-verified 54/54** — plus the matched pair for the causal test. ⚠ `V19`'s decisive arm is unrun, so the generative confound is **narrowed, not excluded**. ★ **AND A NAMED CONSTRUCT NOW EXISTS AT THE 12-ATOM GATE** — `vhlM2@ex_5amide_a2-a3_cyac_me`, InChIKey `RZSRKKSYYBOIEK-ACNWJKEOSA-N`, backbone length re-derived by RDKit, with a SMILES and a retrosynthetic annotation ([`nr4a3-short-linker-probe.json`](../modalities/nr4a3-short-linker-probe.json), which owns every figure about it). ⛔ **The library's floor of 14 was never geometry or chemistry** — the term binding at every gate-clearing basin is `min_member_fraction_comfortable`, a basin-**breadth policy**; the geometric/chemical floor is **11**. ⚠ Its scope is **target-engagement geometry only** — no affinity, no reactivity, no ternary, no degradation — and it is conditional on `R5`'s unresolved **site** selection, since the warhead exit vector is marginalised over pocket-mouth anchors rather than taken from a docked pose | for a *two-mechanism* molecule: the two-branch template, which is a **design change to a preregistered enumeration** and needs an explicit decision that **has never been asked for**. ⛔ **And before either: settle which library is canonical** — the committed one no longer reproduces from its own generator, and the drift reaches the causal test article ([§10.1 row 25](#101--open-rows-ordered-by-what-unblocks-the-most)) | ✓ work complete for one mechanism per molecule |
| **R16 · NR4A3 is the right target** | transfer prior from fusion-addicted sarcomas; near-invariant clonal fusion in a quiet genome; no loss-of-function experiment in any EMC model | the dTAG degradation test — **delegated** to the EMC-program paper | ○ future — **delegated, not a blocker of this paper** |

⚠ **NO REQUIREMENT ON THIS PAGE IS ✓-SETTLED, INCLUDING THE POCKET.** ⚠ **Superseded, retained:** *"Only one
claim on this page is ✓, and it is the bottom one … everything **above the pocket** is either running, waiting
on something running, or waiting on a bench."* That sentence rested on the pocket being settled, and it is not
— Gate 1 failed as registered and an open submission gate reaches the receptor `denovo_401` was generated into.
The honest shape is: **three requirements are ✓ on the work axis with the claim open (`R1`, `R8`, `R15`), one
is run-and-parked (`R7`), one is delegated (`R16`), two had no row at all until 2026-08-02 (`R12`, `R13`), and
the rest are open.** Everything downstream that inherited *"the pocket is settled"* — `R4`, `R5`, `R7`, and
Route A's and Route B's shared anchor set — inherits the open gates instead.

---

## 6 · The closed-route register

**✕ dead · ⏸ parked · 🔒 held · ↩ superseded.**

★ **BUILT BY SWEEP, NOT BY MEMORY (2026-08-02).** The first version of this table held seven hand-picked rows,
which prompted the objection that started this rebuild: ***"I'm a little surprised that nothing is a dead end
at all. I feel like we've had a lot of dead ends both in this whole project and even just today"*** (trimcrae).
The sweep behind the rows below covers **STRATEGY.md Appendix A** (**69** numbered corrections — ids 1–65
plus the lettered sub-rows 19a/19b/19c/19d; counted from the table, not remembered) and **Appendix B**
(6 superseded framings), the **paper's** and **SI's** retracted results,
[`nr4a3-degrader-next-steps.md`](../modalities/nr4a3-degrader-next-steps.md), the modules' own `REFUTED` /
`NOT RECOVERED` / `CANNOT` verdicts, and the operational fact files
([vast-placement-facts.md](../compute/vast-placement-facts.md),
[gcp-gpu-facts.md](../compute/gcp-gpu-facts.md), [bid-strategy.md](../compute/bid-strategy.md)).

⚠ **Superseded, retained — two wrong counts for this appendix have been in circulation.** This page once
scoped its sweep against *"~113 entries"*, and
[`map-merge-inventory.md`](map-merge-inventory.md) records *"**76 rows**"*. Both are wrong, and the
plain **65** is also wrong because it drops the lettered sub-rows. The value read from the table is **69**: one
header, one separator, 69 id-bearing data rows, ids 1–65 with no duplicates plus 19a–19d. ⚠ The inventory's 76
inherits this correction — flagged in [§12](#12--findings-that-belong-to-other-documents), not edited here.

★ **AND SEVEN ROWS WERE ADDED 2026-08-03 FROM A DIFFERENT SOURCE — A FORWARD ENUMERATION, NOT A BACKWARD
SWEEP.** Everything above was found by reading what the program had already tried. The
[options registers](#08--the-six-options-registers--what-they-own-and-the-one-thing-they-may-never-do)
enumerated what it had *not* tried and then measured several of them to a close, which is the only way a
register like this one ever gets a row it could not have remembered. ⛔ **Their grades are not adopted
wholesale.** This page's bar is stricter than any register's, and **three routes their authors marked
closed are ⏸ parked here** — *"closed by the measurements we already have"* answers a different question
from *"is there any future development that would make us retry this?"*. Each of the three says so in its
own row, with the register's wording quoted, so the disagreement is legible rather than silent.

⚠ **THE COUNT IS SMALL ON PURPOSE, AND THE REASON IS THE POINT.** Appendix A is overwhelmingly **↩ superseded
numbers** — a value corrected, a rate re-measured, an ETA that was wrong. Importing those as dead ends would
inflate this table into uselessness and would be exactly as misleading as the under-count it replaced. **A
corrected number is history; a closed avenue is a decision.** Roughly one Appendix A row in ten describes an
*approach* that died, and only those are here.

**The four states, and the one question that separates each from the next:**

| | means | test |
|---|---|---|
| **✕ dead** | positive evidence the avenue **cannot** work | *Is there any future development that would make us retry this?* **No.** |
| **⏸ parked** | it failed with today's tools; a better tool could change the answer | **Yes** — and the row must **name** what has to land ([method-watch.md](../method-watch.md)) |
| **🔒 held** | nothing failed and nothing is missing — it is **waiting on a decision or an authorization** | *Could it run tomorrow if trimcrae said yes?* **Yes** → [§6c](#6c--held--not-refuted-not-parked-waiting-on-a-decision). This state was added 2026-08-02; without it, held work was being written down as parked (hiding a live decision) or as ◐ in work (instructing readers not to start something nobody had started) |
| **↩ superseded** | a number, framing or plan replaced by a better one | not an avenue at all — it lives in [Appendix A / B](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) and is **deliberately not copied here** |

---

### 6a · DEAD — conclusively unworkable, never retry

**✕**

**Science.** Each row answers *no* to the test above, and says which kind of impossibility it is: a **confound
in the system** no instrument sees past, **arithmetic** that cannot reach the criterion, a **premise shown
false**, an **artifact that can never be regenerated**, or a **definitional** contradiction. The italic tag
names the requirement or instrument the route would have served.

| ✕ approach | why nothing reopens it | evidence |
|---|---|---|
| **NR-V04 as the positive control** for paralogue-selectivity detection *(would have served `R7` as an instrument)* | *Confound in the system.* Its selectivity is attributed to a covalent bond at a cysteine NR4A2/NR4A3 **lack**, so a geometry readout passes for the wrong reason. No sample size and no better method fixes a confound that lives in the test system rather than the instrument | Cys551 unique to NR4A1 ([`nrv04-cys-conservation.json`](../modalities/nrv04-cys-conservation.json)); celastrol C6→S **28.42–39.11 Å** against an 8.0 Å limit and a ~1.8 Å bond ([`structural-provenance-census.json`](../modalities/structural-provenance-census.json)) |
| **Crystal-copy MD design for the E1 control** *(`V11`)* | *Arithmetic.* 9DTX's asymmetric unit holds a single ternary, so matched arms are one copy each, the permutation reference set is 2, and the **minimum attainable *p* is 0.5** against α = 0.05 — the test cannot reject however it is run. ⚠ Scoped honestly: this is dead **on the deposits that exist**. A future multi-copy SMARCA4 ternary deposit would change it — that is new *data*, not a capability, and it is on no watch list | 9DTY 8 copies / 9DTX 1; `design.can_reach_alpha: false`, `min_attainable_p: 0.5` ([`selcal-xtal-census.json`](../modalities/selcal-xtal-census.json)) |
| **Covalent warhead at an NR4A3 pocket cysteine** *(would have served `R8`)* | *Definitional.* The only two cysteines inside the pocket band are **conserved in all three paralogues** — a residue the paralogues share cannot discriminate between them. Both are also fully buried, so it fails twice over | C496 (3.33 Å from the pocket) and C536 (6.74 Å) both `unique_vs_both: false`, SG SASA **0.0 Å²** ([`nr4a3-covalent-handle-ensemble.json`](../modalities/nr4a3-covalent-handle-ensemble.json)) |
| **The §2.5 ternary result** *(`R10`)* | *Unregenerable artifact.* The molecule folded is unrecoverable — no bond-order record in any of the three models, and it entered as an unlogged environment variable. That specific **result** can never be replicated or extended by anyone, us included. ⚠ Scoped to the **result**: what is missing is connectivity/regiochemistry, not everything — the SI records a named four-part scheme (warhead–PEG2–succinyl–lenalidomide), formula **C41H56N4O8** and a heavy-atom count matching the models' `n_heavy: 53`. A re-fold could build *a* molecule of that composition; it could not establish it is *the same* one, which is what a replicate comparison needs | `n_recovered: 0` of 3 arms; "no `_chem_comp_bond` loop" on each ([`nr4a-ternary-ligand-provenance.json`](../modalities/nr4a-ternary-ligand-provenance.json)); composition record SI `:69–71` |
| **The NR-V04 covalent panel's per-arm figures** — ⛔ **ALL RETRACTED, MUST NOT BE QUOTED; there is no current per-arm figure.** The retracted values, named so they are recognised and refused rather than re-derived: `recruiter_active` 3/3 vs epimer 1/3; cov 2/3 = noncov 2/3; `cov_c551a` 1/3 | *Unregenerable artifact, the same class and the more expensive lesson.* The panel **persisted no trajectory**, so a chain-ordering defect (Elongin C scored as the target), a chain-blind reactive-cysteine search and an **nm/Å unit error** were *"each correctable in principle and **none correctable in practice**"*. The 17 legs cannot be re-analysed, only re-run. ⚠ The **approach** is not dead — a re-run that strides a heavy-atom trajectory is a live option; only these numbers are closed | paper `:808–811`, `:933–936`, `:2036`; SI `:816–817`; `nrv04_feasibility_covalent.status: "under_correction"`, per-seed fractions marked *"SUPERSEDED and must not be cited — the interface was wrong"* ([degrader-paper-schedule.json](degrader-paper-schedule.json)) |
| **Constrained-embed prep for the ternary generator** *(`V2`)* | *Premise false.* The generator's own unbound protocol **supplies the native pose**, so there was never a generated conformer for us to constrain. Refuted by its released benchmark data, for $0, before it was built | shipped `ligand.pdb` ≡ native, **0.000 Å over 66 heavy atoms** ([`selcal-deepternary-frame.json`](../modalities/selcal-deepternary-frame.json); [Appendix A 65](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims)) |
| **Single-snapshot MM-GBSA `margin > 0` as a selectivity verdict** *(`V20`)* | *Arithmetic, twice.* **(i)** 38 unrelated marketed drugs through the identical funnel score a positive NR4A3 margin **22 of 38 (58 %)** and `confirmed_selective` **15 of 38 (39 %)** — caffeine, ibuprofen, lidocaine, phenytoin among them — while the developability-gated de-novo set reaches only **2 of 11 (18 %)**, i.e. *below* its own null. **(ii)** De-noising the same molecules gives per-margin **SD ≈ 4–6 kcal/mol, larger than the margins themselves**: the best lead, `denovo_393` at **+18.34**, becomes **−2.95 ± 3.65**, while the negative control stays negative, so the tier is discriminating and the harvest is still noise. A signal smaller than its own noise is not recoverable by any downstream method | the 38 committed decoy margins, `DECOY_2026_06_30` in [`selectivity_calibration.py`](../modalities/selectivity_calibration.py) ("`margin > 0` is meaningless"); multi-snapshot reversal in [next-steps.md](../modalities/nr4a3-degrader-next-steps.md); paper §2.5 retraction of "MM-GBSA-confirmed selective" |
| **The valB closure triangle as a *diagnostic* for the wrong-sign miss** *(`V5`)* | *Proof.* Under the live hypothesis (branch A) every named error class is a per-endpoint **state function** or is external to the calculation, and closure is **identically zero** for all of them — so the triangle returns a clean `R` whether or not the program's actual problem exists. It cannot discriminate "the method is right" from "the model is wrong". Under branch B it duplicates the cheaper forward/reverse leg and goes stale on the fix | `branch_A.verdict: "REFUTED for diagnosis"`, `can_closure_see_that_class: false` ([`valb-triangle-closure.json`](../modalities/valb-triangle-closure.json)). ⚠ The triangle still yields a path-error floor and an endpoint-consistency check — those are **not** dead; the *diagnosis* is |
| **The one-pendant linker grid as a route to a two-mechanism molecule** *(`R15`)* | *Architectural.* `build_smiles`'s template carries **one branch residue**, so no choice of segments, length or placement can emit a molecule carrying both a covalent handle and the causal wedge — every sweep over the grid searched a space that structurally cannot contain the answer. The branch floor `k = 3 + SEG2 + tail` is independent of SEG1 and of chain length, and `SEG2 = 0` would form an acylurea, so **no grid change reaches k < 4** | [`linker-branch-reach.json`](../modalities/linker-branch-reach.json) + 7 tests ([`tests/test_linker_branch_reach.py`](../modalities/tests/test_linker_branch_reach.py)); [Appendix A 55](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims). ⚠ The **fix** is a two-branch template at n = 18 with existing segments — that is a live design change, not a re-grid |
| **Reading Gate 3B off a *single* biased F(Rg) profile** *(`R2` via `V13`)* | *Premise false.* Three independent-seed replicas do **not** reconstruct a common F(Rg): the basin sits at a different Rg in each, and the basin→druggable ΔF differs by many kcal/mol. The ~0.6 kcal/mol single-trajectory accessibility estimate is therefore an artifact of one profile, and no single profile can be read that way again. ⚠ **`R2` itself is open, not dead** — only this way of answering it is closed | `_interpretation`: "the replicas do NOT reconstruct a common F(Rg) … Gate 3B is unresolved" ([`nr4a3-metad-crossreplica.json`](../modalities/nr4a3-metad-crossreplica.json)); withdrawn in paper §2.2 |
| **Selectivity from LYSINE AVAILABILITY — the paralogues being lysine-POOR in the transfer zone** *(would have served `R12` via `V18`)* — ⚠ **scoped to the availability form; the uniqueness form is what `R12` actually rests on and is untouched** | *Premise false, then arithmetic.* The premise was that NR4A3's transfer zone reaches a lysine materially more often than the paralogues'. Matched over the same unbiased conformers per species it does not: the NR4A3-vs-NR4A1 gap is **under one replicate-SD** and the NR4A2 direction is a coverage *ratio* near unity, which is not a selectivity mechanism at any precision. And the arithmetic cannot be reached from here — availability-based discrimination needs the paralogue coverage near **zero**, and it is not near zero. ⚠ **What is dead is scarcity, not the term:** the discrimination `R12` claims is the rare **joint** event — covering a *unique* lysine while both paralogue zones stay bare — which this page already states correctly in [§the Tier-2 result](#-tier-2-result-in-full--the-12-pose-run-at-its-corrected-exact-kernel-values-lane-2-2026-07-25-reach-correction-2026-07-26-0-realized--no-gpu) and which no measurement here touches | the matched like-for-like triple, its replicate-SD and the matched-frame win rate: [`selectivity-mechanism-options.md`](../modalities/selectivity-mechanism-options.md) → `M1` / [`.json`](../modalities/selectivity-mechanism-options.json) `measurements.M1`, computed over [`nr4a-paralogue-dynamics.json`](../modalities/nr4a-paralogue-dynamics.json). ⚠ The same measurement carries the **ensemble-label correction** to the triple this page used to quote, and it is **conservative** — matching the ensembles makes the NR4A1 gap *smaller* |
| **CONFORMATIONAL-SELECTION selectivity — "the cryptic pocket opens ONLY in NR4A3"** *(would have served `R1`/`R7` before any chemistry)* — ⚠ **scoped to the CATEGORICAL form. What survives is a measured RANKING, and it is not dead: [§8](#8--the-two-live-routes-to-selectivity--and-where-each-is-actually-blocked)** | *Premise false.* Both paralogues **reach** NR4A3's druggable CV value inside their own matched metadynamics (NR4A1 exactly; NR4A2 within a rounding of it), and under the harmonized detector NR4A3's Pocket-5 site is **DETECTED in essentially every frame of all three species**. "Only NR4A3 has the cryptic site" is therefore not available as an argument, and nothing reopens a set-membership claim whose complement has been observed. ★ **Note WHY the refutation survives an instrument this page grades harshly:** `V13`'s cross-replica reproducibility failed, which destroys any statement about the *population* of the opened state — but a refutation by **existence** needs only that the paralogues reach it, which a biased ensemble can show. ⚠ **Superseded, retained, and it is invariant 5's failure mode caught within the hour:** this row first rested on *"fpocket rates NR4A1's opened frame **more** druggable than NR4A3's (0.981 vs 0.931)"*, which is **one frame per species**. The matched replicated contrast landed the same day and points the **other** way on frequency — so the ✕ rests on **detection**, a set-membership fact, and **not** on any druggability ordering | [`selectivity-mechanism-options.md`](../modalities/selectivity-mechanism-options.md) → `M5` (`S14`); matched ensembles re-read under one detector build in [`paralogue-pocket-contrast.json`](../modalities/paralogue-pocket-contrast.json) (`C04`, $0 CPU, 0 refusals, and it **reproduces the committed NR4A3 rows exactly**) |
| **Relocating the target to the DBD or to DNA binding** *(would have served `R7` by choosing an easier object)* | *Arithmetic, over a fixed sequence fact.* The zinc-finger DBD is far **more** conserved between the paralogues than the LBD the program already targets — the identity ordering is in [§8 Route B](#route-b--a-linker-borne-covalent-handle-at-an-nr4a3-unique-cysteine---blocked-on-r5-nothing-running--serves-r8-r15)'s table — so *"the fusion works through DNA binding, so block that"*, which is the intuitive move, lands on the **worst** available place to stand on this target. The whole family also binds the same NBRE/NurRE elements, so the *functional* site is shared as well as the sequence. No development changes a sequence identity | domain-resolved identities computed from the cached UniProt sequences: [`target-route-census.json`](../modalities/target-route-census.json) `paralogue_identity_by_domain` / `zinc_finger_window`, reasoning in [`target-route-options.md`](target-route-options.md) route 12 |

**Operations.** Compute-side routes that were tried and cannot work. They are here because they cost real
sessions and keep being re-proposed, and because CLAUDE.md §6's rules point at them rather than restating them.

| ✕ approach | why nothing reopens it | evidence |
|---|---|---|
| **Raising the GCP `GPUS_ALL_REGIONS` quota to fan out** | *Unavailable **and** wrong on its own terms.* Repeatedly requested, repeatedly refused for an account this size — and the binding ceiling was never the quota: at ~$292 of remaining credit and ~$0.71/L4-h the **dollar** ceiling is ~411 L4-h, so the 1,824 GPU-h it claimed to unlock was never purchasable. At quota 4 the same credit is simply spent 4× faster. The 1-GPU cap is treated as a fixed property of the lane | [Appendix A 20](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims); [gcp-gpu-facts.md §1](../compute/gcp-gpu-facts.md) |
| **Paying a bid premium to buy host retention on Vast** | *Refutable form, and the market is nowhere near it.* Vast's own documentation puts on-demand renters ahead of every interruptible bid, so a premium buys protection against only part of the hazard; and the break-even needs **105 preemptions/hour per $/hr of premium**, which no market in excess supply delivers. The reload that once justified `×1.9` was **self-inflicted** — our reaper DELETEd paused instances. Retention is bought with checkpoint frequency, which is free | [bid-strategy.md](../compute/bid-strategy.md) F2 / R2 / R5; [Appendix A 3](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) |
| **A durable, cross-lane machine blacklist** | *No evidence could ever retire an entry.* The defect was never that a given host was wrongly excluded — it is that nothing aged out, so the set was a one-way ratchet on the one quantity that must stay wide. The asymmetry decides it: re-learning a bad host costs one **free** failed submit, over-excluding costs capacity on every lane, silently | `DURABLE_EXCLUSIONS_ENABLED = False` ([`vast_machine_blacklist.py`](../modalities/vast_machine_blacklist.py)), held by [`tests/test_blacklist_retired.py`](../modalities/tests/test_blacklist_retired.py); [vast-placement-facts.md §1a′](../compute/vast-placement-facts.md); [Appendix A 59](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) |
| **Anytime-valid sequential stopping as a cost lever on this ladder** | *Arithmetic.* An anytime-valid bound must hold under *every* stopping time, so at n = 2–4 with σ ≈ 0.7 it never fires. The saving on this ladder: **0.8–2.6 %**, against the ~20–25 % claimed. Real for long horizons; a 5-replicate ladder is structurally too short, and no implementation changes that | [`valb_rescope_design.py`](../modalities/valb_rescope_design.py); [Appendix A 17](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) — **do not carry it in any total** |
| **Rescoping the valB calibrator's EDGE at all** *(`V5`)* | *Arithmetic — the telescoping identity, not effort.* Open decision 6: `R ≈ 0` localises the miss to an **endpoint-state** error, which is a property of the model or the reference data, and *"changing the edge changes neither"* | [Open decision 6](#open-decisions) |
| **The valB_mini P-series rescope specifically** *(`V5`)* | *Arithmetic.* **6 of 10** pairs change formal charge (including P1→P4), and the 4 that do not perturb **58–80** heavy atoms against 2 for the running edge. ⚠ **Scoped to the P-series.** The broader statement — that a ≥2 kcal/mol ternary calibrator which is simultaneously small, charge-neutral and mappable may not exist in the public literature — is a **conjecture, not proof**, and must not be filed as ✕ | [`valb-pseries-chem.json`](../modalities/valb-pseries-chem.json); [Appendix A 18](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) |
| **Step 3 — the NR4A1/2/3 re-panel** *(would have served `R11` via `V11`)* | *Arithmetic and tier agree.* The sensitivity control returned NULL, so *"IT IS NOT BOUGHT"* — it would be money spent to reproduce a failure — and the prereg's own power section put this shape at **≤ 0.16** against the separations already measured. Machine-carried by `selcal_gate.NEXT_STEP_BY_TIER` | [`nr4a-repanel-prereg-DRAFT.md`](../modalities/nr4a-repanel-prereg-DRAFT.md), **retired unrun**; [`selcal-verdict.json`](../modalities/selcal-verdict.json) |
| **Switching the GCP lane off the L4** (P100/V100/T4) | *Refuted by measurement.* Both spec tables are WITHDRAWN; the card probe **inverted** them — the workload is compute-bound and the T4 runs ≈**0.31×** the L4 where bandwidth predicted 1.07×, and the price column had compared whole-VM against bare-GPU. *"STAY ON THE L4"* | [Open decision 5](#open-decisions) |

---

### 6b · PARKED — failed with today's tools, with a named trigger to reopen

**⏸**

★ **Parked is not a softer dead.** CLAUDE.md §5 is explicit that these are *"revisit when capability X lands"*,
and [method-watch.md](../method-watch.md) is where the triggers are watched. **Filing one of these as dead
would bury a live option**; filing a dead one here would invite re-running something that cannot work.

| ⏸ approach | how it failed | what has to land to reopen it |
|---|---|---|
| **Sequence-only co-folding to generate ternaries** *(`V12` → `R10`)* | The two halves are assembled wrongly, not approximately: target↔E3 **DockQ 0.023–0.046, fnat 0.000** — zero native interface contacts — while the internal VHL/EloB/EloC machinery scores 0.89–0.97. Two independent DockQ implementations agree | a co-folder evaluated on ternary **assembly** rather than per-chain pocket accuracy. Boltz-2 failing is not the class failing, and the same harness already recognises a correct ternary (DeepTernary, given both sites, reaches **0.839** on the same interface) — so the plumbing is not what missed |
| **E1 interface-stability endpoint as a selectivity readout** *(`V11` → `R11`)* | **Two** independent attempts, no pass: *p* = 0.393 (DISCORDANT) on the NR-V04 retrospective, *p* = 0.747 (NULL) on the SMARCA2/4 control — the second on an **adequately-powered** design with zero technical failures and a reference-set floor of 0.00216 against α = 0.05. Consequence already taken: the NR4A1/2/3 re-panel prereg is **retired unrun** | a readout with power at achievable sampling, or a system whose effect is large enough for E1's resolution. ⚠ Two failures is strong evidence, **not proof of impossibility** — and the SMARCA2/4 null bounds *the workflow as run*, since its co-folds never reproduced the interface under test. ⛔ **`V5`'s wrong sign is NOT a third E1 failure** — it is alchemical ternary FEP, a different instrument, and the scoreboard's control table exists to stop exactly that sum |
| **The 19th congeneric edge (`cw_bio_nmethyl_amide`)** *(`V6`'s lane)* | No available mapper reaches the 20-atom provable floor — best is 19, and the budget is **not** binding (identical maps at t20 and t300), so more search time buys nothing. The one map that does reach 20 gets there by mapping a carbon onto a hydrogen | an atom mapper that reaches the floor **without** a degenerate correspondence. The artifact names the trigger itself: *"not a retry candidate until a mapper reaches 20"* ([`step1-map-diag.json`](../modalities/step1-map-diag.json)) |
| **Charge-changing alchemical edges** *(`V5` `V6`)* | Blocks 8 legs of the step-1 fan-out, and killed the valB rescope's high-contrast route: **6 of 10** P-series pairs change formal charge (including P1→P4), and the 4 that do not perturb **58–80 heavy atoms** against 2 for the running edge | a validated charge-change correction in this lane (co-alchemical ion / finite-size treatment). ⚠ Even with it the P-series stays a poor calibrator on perturbation size alone — the correction reopens the *edges*, not that *design* ([`valb-pseries-chem.json`](../modalities/valb-pseries-chem.json); [Appendix A 18](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims)) |
| **E3 recruiter breadth beyond CRBN + VHL** *(`R9` `R12`)* | Availability was the **wrong constraint**; structural stageability binds. Of 10 recruiters, RNF114 has no deposited structure at all, DCAF16's ligand is 34 % buried with its partner removed (a glue interface, not a handle pocket), and DCAF15 has no partner-free liganded structure. The widening **left CRBN + VHL standing** rather than displacing them — a negative result about the alternatives, not a positive validation of the incumbents | a deposited partner-free liganded structure for one of the blocked recruiters. A real negative to report, not to absorb ([`e3-recruiter-downselect-2026-07-25.md`](../modalities/e3-recruiter-downselect-2026-07-25.md); [Appendix A 19](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims)) |
| **Track A — qualify `denovo_401` as a lead via repaired ABFE** *(`R7`)* | Shelved 2026-07-15 by reviewer verdict; `denovo_401` is a **side comparator / benchmark, not a lead**, and the FEP tier it needs is ceiling-bound and least reliable on a cryptic, induced-fit pocket | cheaper or more reliable free energy on cryptic / induced-fit pockets — an existing [method-watch.md](../method-watch.md) row. Parked, **not deleted** ([Appendix B](../../STRATEGY.md#appendix-b--superseded-strategy-framings)) |
| **perses as the protein-mutation FEP engine** *(`V10`)* | *Licence gate, not a science failure.* Its core protein-mutation path round-trips each residue template through an **OpenEye `OEMol`** (`PolymerProposalEngine.generate_oemol_from_pdb_template` → `oechem.oemolistream`) — commercial and licence-gated, with **no conditional and no RDKit alternative on that path**. Cost of establishing it: **~$0.05**. ⛔ **This does not belong in the dead table**: everything around the engine was engine-agnostic and survived the swap, and **pmx + GROMACS already serves the avenue** and has passed its known-answer benchmark | an OpenEye licence, or an RDKit path on perses' residue-template mapper. ⚠ Reopening it buys nothing today — the avenue is *served*, so this row exists to stop it being re-tried, not to be waited on ([§THE ORDERED PLAN](#the-ordered-plan-spend-gated--read-top-to-bottom-for-whats-next); [Appendix A 8](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims)) |
| **The celastrol–C551 covalent re-fold route** *(`R12`'s NR-V04 analogue)* | Run and refuted for **~$0.05**: deleting the E3 makes seating *worse* (33.6–44.7 Å), and a **steered** co-fold honouring `max_distance: 6.0` never satisfied its own bound on 3 seeds, across 7 clean models, 4 seeds and 3 prefixes | a better co-folder or a hand-placed pose. ⚠ The ladder's own scoping is load-bearing: *"this is a statement about the predictor, not about whether celastrol binds C551"*, which is literature-anchored |
| **The required covalent control set** (preformed adduct, C551A, warhead-only, active/inactive recruiter, noncov-vs-cov) *(validation requirement 4)* | Built, run, and then **retired** when the covalent legs were dropped and the panel was re-scoped to noncovalent | it parks with the re-fold route above. ⚠ **Validation requirement 4 mandates this control set**, so the parking is a live constraint on what NR-V04 may be claimed to have tested — not a tidy-up |
| **E3 recruiter CHOICE as a paralogue-selectivity lever** *(`R12`, via `V18`'s term (b))* — ⚠ **distinct from the recruiter-BREADTH row above: that one asks *which recruiters can be staged*, this one asks *whether the choice discriminates*** | ⛔ **The readout is not stable under a nuisance variable.** Changing only how the E3 arm is *assembled* — no change to recruiter, sampling or criteria — swings the maximum term-(b) enrichment by nearly 3× and halves one recruiter's any-lysine null. The program's single E3-preference claim (*"the discrimination lives on VHL"*) was **retracted the same day for exactly this reason**, and this page already carries that retraction. **A recruiter preference is not measurable at the current staging precision** | **staging precision good enough that a preference survives a restaging** — concretely, an **observed** rather than **composed** CRL/E2~Ub geometry, which is the same trigger `V18` carries (*"no degradation-geometry claim may rest on a RING or E2 that was COMPOSED rather than observed"*). ⚠ **GRADED DOWN TO ⏸ HERE FROM THE REGISTER'S "closed":** [`selectivity-mechanism-options.md`](../modalities/selectivity-mechanism-options.md) grades `S8` **D — blocked**, which is *"the instrument failed"*, not *"nothing reopens it"*. An instability under a nuisance variable is the textbook ⏸: fix the nuisance variable and the measurement becomes possible. Measurement: `M6` there |
| **A molecular glue instead of a PROTAC** *(would have served `R7` `R9` `R10`)* | ⛔ **It removes handles rather than adding them, and it is the modality most dependent on the one capability the field lacks.** A glue has no linker, so it has **no covalent axis and no designed exit vector**: the claim collapses back onto a single induced-interface ΔΔG of the same ~1 kcal/mol size no instrument here resolves, against a PROTAC's three independent mechanisms. And the program's own thesis is that in every landmark case glue selectivity was **discovered then rationalized** by a solved ternary, *never predicted blind*. The repo has also already met a glue interface and classified it **unstageable** (a ligand 34 % buried with its partner removed — *"a glue interface, not a handle pocket"*) | **a validated prospective molecular-glue design or glue-interface selectivity predictor** — a [method-watch.md](../method-watch.md) trigger, because a glue is the modality most likely to arrive from someone else's screen rather than from this program's design. ⚠ **GRADED ⏸ HERE, NOT ✕:** the register's own verdict is *"⏸ watch, do not build"*, and the block is a missing capability, which is the definition of parked ([`target-route-options.md`](target-route-options.md) route 10) |
| **Fusion-selective *ubiquitination*** — discriminating EWSR1::NR4A3 from wild-type NR4A3 at the transfer step rather than the binding step *(would have served `R13`'s object, and would have been a fusion-vs-WT axis rather than a paralogue one)* | ⛔ **The geometry does not reach.** The idea is sound — binding cannot discriminate the fusion from wild-type NR4A3 because the LBD is shared, but *degradation additionally requires a lysine in the transfer zone*, and the two proteins present different N-terminal acceptor sets. It fails because the measured ubiquitin-transfer distance and the exposed NR4A3-unique lysines are **both inside the shared LBD**, while the differential lysines sit ≥100 residues away on the far side of the DBD and hinge. **The idea is sound; the geometry is not** | **a construct whose E3 is anchored somewhere other than the cryptic pocket** — at which point the transfer-zone geometry question re-opens and has to be re-measured. ⚠ **GRADED DOWN TO ⏸ HERE FROM THE REGISTER'S "✕ closed", ON THE REGISTER'S OWN CAVEAT:** *"filed at the roadmap's strict bar this is a route closed by measurements that already exist, not a proof of impossibility"* ([`target-route-options.md`](target-route-options.md) route 13). It is on this page at all only because it is now a *generated* hypothesis with a recorded closure — it was never an open route here |
| **Arm F of the NR-V04 retrospective — the alchemical ΔΔG_coop arm** *(`R11`)* | Never launched. **BLOCKED by calibration addendum condition 7** — *"runs only after the valB calibration PASSes"* — and `V5` **FAILED on the sign**. ⛔ **So the gate that would release it can no longer fire as written**: the closure triangle localises the miss to an **endpoint-state** error, and STRATEGY.md's own reading of that branch is that *"more sampling will **NOT** fix the miss"*. Arm F is therefore not "pending" in any sense a reader should act on — it is parked behind a condition its own instrument cannot now satisfy | a ternary alchemical free-energy method that **passes** the valB known-answer control. Not more sampling of the present one. ⛔ **AND THE DECISION ITSELF IS OUTSTANDING** — Arm E got an explicit ruling ([Open decision 12](#open-decisions)); Arm F never did, so it is **classified here but undecided by the program**. It needs one — held, or explicitly retired. On the roadmap as a $0 decision item ([§10](#10--the-roadmap--one-ordered-list))  ⭑ **AND THE TRIGGER IS UNSCHEDULED — added 2026-08-03, and it is the reason this row is more than bookkeeping.** *"A ternary alchemical free-energy method that passes the valB control"* has **no rung, no gate and no price anywhere in the program**, so it can be neither refused, costed nor sequenced — the *"caveat with nowhere to go"* pattern. ⚠ **[§10 row 11](#101--open-rows-ordered-by-what-unblocks-the-most) is NOT it**: it calibrates the **`S`-shaped** quantity, and [Open decision 9](#open-decisions) is explicit that *"valB_mini calibrated `ΔΔG_coop`, a quantity `S` does not contain (its binary leg cancels algebraically)"*. ✅ **Its structural feasibility is already measured, $0, and favourable:** [Open decision 6](#open-decisions) framed the successor as a **system** question and [`s-calibrator-survey.json`](../modalities/s-calibrator-survey.json) answers the structural half — 8G1Q (the frozen template) is on the **SMARCA4** arm while **8G1P**, same series at **2.7 Å**, is on the **SMARCA2** arm, i.e. a real structure for the arm the repo currently homology-substitutes, which is exactly the class `R` localised the miss to. ⚠ Scoped: a **structural** screen only (*"does NOT assert the entries are interchangeable"*), it supplies no known-answer cooperativity, and it **does not amend [decision 9](#open-decisions)** — it is a route to *satisfying* the gate, not to loosening it. |

---

### 6c · HELD — not refuted, not parked: waiting on a decision

**🔒**

★ **Added 2026-08-02, and it is [§0.3](#03--three-orthogonal-axes--work-state-authorization-sufficiency)'s
authorization axis applied to this register.** These items are neither dead nor parked: nothing about them
failed, no capability is missing, and every one is ready to run. What stops them is that **trimcrae has not
authorized the spend** — which the three states above cannot express, so they were previously either absent
from this page or, worse, rendered as ◐ *in work*. **A held row is a live option with a price tag, and the
only thing it is waiting for is a person.**

⚠ **The distinction that matters when reading these:** ⏸ parked says *"come back when a tool lands"*; ✕ dead
says *"never"*; 🔒 held says *"say the word."* Filing a held item as parked hides a decision that could be
taken today.

| 🔒 held item | serves | what it would buy | why it is held | authorization state |
|---|---|---|---|---|
| **CREBBP vs BRD4(1) / SGC-CBP30 selectivity ABFE** | `V4` → `R7` | the program's **only** binary selectivity control — the first evidence the free-energy engine resolves selectivity **between two proteins**, not just within one pocket. The **highest-leverage unrun item in the program** | [§the standing tally](#the-standing-tally-this-closes) *"**Neither is authorized here**"*. ⛔ And **sufficiency is a separate matter**: it is a **binary** control and *"would **not** discharge §4's paralogue/ternary statement"* ([§what the SMARCA2/4 null BINDS](#what-this-binds-in-the-words-fixed-before-the-run)) | 🔒 **not authorized** |
| **pmx/GROMACS interface point-mutation ΔΔG** *(the SMARCA2/4 application)* | `V10` → `R7` | it *would* have been the paralogue-scale cross-check `V10` has never been benchmarked in | ⛔ **THE $0 PRECHECK RAN ON 2026-08-02 AND RETURNED `STOP_NO_REFERENCE`** ([`pmx-mutation-reference-precheck.json`](../modalities/pmx-mutation-reference-precheck.json)). It **was** authorized (trimcrae, 2026-08-02: *"pmx only"*) and then failed its own precondition, which is a **stronger and more durable** reason to leave it unrun than a budget hold. The Gln1469 contact is documented structurally and functionally and **neither is a measured interface mutational ΔΔG**, so the run would have had no known answer to score against — the exact defect that cost this program its withdrawn selectivity claims. ⚠ **Superseded, retained: 🔓 *authorized, precheck first*.** ★ **What WOULD unblock the instrument is a different question and now has a concrete answer:** `barnase_barstar_W35F`, the single wedge-sized charge-conserving buildable candidate out of 7,085 SKEMPI rows, CI-verified to stage and deliberately **not** in `protfep_bench.QUALIFICATION_SET`. ⚠ It would settle whether **this engine** resolves a ~1 kcal/mol interface effect — it is not a selectivity control, involves no paralogue, and passing it would license no NR4A3 claim | ⛔ **closed on EVIDENCE** — not held, not authorizable today |
| **`dg_open_paralogue`** — converged pocket-opening free energy per paralogue | `R6` | it turns every conditional ΔΔG on the binder path into an unconditional one, and it is the term that can **reverse** selectivity | *"**HELD** — only with an explicit nod. If NOT run, report everything conditional on the open state (fully defensible, $0)"* | 🔒 **explicit nod only** |
| **`abfe_conditional`** — conditional ABFE + the λ-overlap repair | `V9` → `R7` | sharper error bars on the existing ABFE block | **held on a decision AND parked as framed** — the two are not alternatives here: *"HELD — as framed, **not worth running** (interpretability)"*, and validation requirement 3 adds *"**HELD also means the λ-overlap repair of the existing ABFE block is parked, not in flight**"*. Even with a nod, the framing has to change first, and its three technical preconditions (accuracy benchmark passes · opening penalty handled · multiple poses treated) are **all unmet** | 🔒 **explicit nod only**, and ⏸ as framed |
| **`valB_full` — the component-calibration cube** | `V5` → `R11` | the gate under the **entire** prospective ladder (5c and 5d) | ⛔ **Its module 1 has FAILED and [Open decision 9](#open-decisions) declined to amend or decouple it, so this gate cannot fire as written** — *"the prospective NR4A ternary matrix stays unrun and cooperativity claims stay exploratory."* This is the **single largest structural block in the program** and it had no row on this page until this pass | 🔒 **held by a taken decision** |
| **The two-branch template as a design change** | `R15` | the only molecule that can carry the covalent electrophile **and** the causal wedge (n = 18, existing segments) | *"a **DESIGN change to a preregistered enumeration**, not a defect fix… It needs an explicit decision, and it is not taken here."* ⚠ **The decision has never been asked for** | 🔒 **decision never requested** |
| **The restrained binary re-run (LANE 20)** | `V5` | attributes or dissolves the binary arm's departure finding | ✅ **THE HOLD IS DISCHARGED, 2026-08-03.** The $0 pose diagnostic (`task=triangle-converge`) **ran** and found the departure **PRESENT** on both triangle binary legs (10/12 and 8/12 beyond 4.0 Å) with both ternary arms clean — so the departure is now **attributable** rather than assumed, and the prereg's bar on interpreting `R_binary` without it is lifted. What remains is a spend decision on the re-run itself, not an unanswered $0 question. ⚠ **Superseded, retained:** *"HELD ON PURPOSE … which has still never run"* | 🔒 **not authorized** — but no longer held behind a free observation |
| **MM-GBSA rescore of Tier 2** | `V20` | nothing that survives — it would refine the very axis the mechanism-first reframe demoted | *"NOT run, and recommended against"* | 🔒 **held by a reasoned default-no** |
| **Validation A-full** | `V6` | a 10–20-edge public RBFE benchmark | `[–]` **SKIPPED** — redundant with OpenFE's published benchmark; its re-open rider already fired and is discharged by Val B | 🔒 **held-as-skipped**, reversible only if the NAGL/am1bcc split changes |
| **Arm F — alchemical ΔΔG_coop** *(also in [§6b](#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen))* | `R11` | per-paralogue ternary cooperativity | listed here **only** to say it is *not* an authorization waiting to be given: its gate is condition 7, which its own instrument can no longer satisfy. **What is outstanding is a classification decision, not a budget nod** | ⏸ parked · ⛔ **undecided**  ⚠ **AND IT IS NOT 🔒 HELD ON THIS SECTION'S OWN TEST** (*"could it run tomorrow if trimcrae said yes?"*) — **no**: `selectivity_resolution_options.py` records the blocker as *"valB calibration condition 7 — **not a spend decision, a preregistration one**"*, so a budget nod would not release it. The outstanding decision is **classification**, and its unscheduled trigger is in [§6b](#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen). |

Ids and costs are the plan's and the [schedule JSON](degrader-paper-schedule.json)'s
(`dg_open_paralogue`, `abfe_conditional`, both `OPTIONAL/HELD (explicit nod only)` on the dependency spine);
**per invariant 6 no price is retyped here** — the spine and the schedule own them.

---

### 6d · SUPERSEDED — not here, and that is deliberate

**↩**

A corrected number, a replaced framing or a retracted claim is **history, not a closed avenue**, and it has one
home: [STRATEGY.md's Appendix A and Appendix B](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims).
Copying any of it into this table would break invariant 6 and would drown the rows above — which are the ones
that change what anyone does next. **Only the ~1-in-10 Appendix A rows where the *approach* died, rather than
the value, appear in [§6a](#6a--dead--conclusively-unworkable-never-retry) or
[§6b](#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen), each citing its Appendix row.**

⚠ **What this register is still missing, stated rather than left implicit.** The MM-GBSA decoy null's primary
run output lives in S3, not in a committed JSON; what *is* committed is the 38-margin constant
`DECOY_2026_06_30` and the paper's §2.5 text. That is enough to grade the row — the arithmetic can be redone
from the constant — but it is the weakest evidence chain in §6a, and it is the only row here whose refutation
is not readable end-to-end from a committed artifact.

---

## 7 · Branches still open

Question nodes carry the state of **the branch itself**: ✓ answered, ◐ being answered now, ○ not started.
Outcome boxes are grey — they are consequences, not work items.

```mermaid
graph TD
  Q1{"✓ Does NR4A3 have a<br/>ligandable cysteine<br/>the paralogues lack?"}
  Q1 -->|"3 unique in the LBD: C397 C420 C559<br/>but 11-19 A from the pocket"| COV["COVALENT route — only at LINKER<br/>reach, not warhead reach.<br/>Not the NR-V04 mechanism"]
  COV --> Q1B{"✓ Is the LINKER-borne<br/>handle geometrically<br/>available? (branch 1b)"}
  Q1B -->|"C397 only; the window is closed<br/>first by a PARALOGUE cysteine<br/>that NR4A3 lacks"| COVX["Uniqueness runs BOTH ways —<br/>the reciprocal direction had<br/>never been computed"]
  Q1 -->|"the 2 IN the pocket are<br/>conserved AND buried"| NONCOV["NON-COVALENT route — selectivity<br/>from pocket shape (Route A)"]
  Q2{"✓ Does the pipeline recover<br/>a known ligand pose?"}
  Q2 -->|"INCONCLUSIVE — the control<br/>failed on 6 of 6 pairs"| SPLIT["The question was TWO questions.<br/>Docking: 3.04 A, fnat 0.778.<br/>Site selection: missed by 17-29 A"]
  SPLIT --> ANCHOR["So the pose's weight rests on<br/>the SITE being right, which<br/>this test could not check"]
  SPLIT --> STOP["Re-run with site and docking<br/>separated before anything<br/>inherits the pose"]
  Q3{"○ Does anything bind<br/>NR4A3 at all? (wet lab)"}
  Q3 -->|yes| GO["Pocket is real;<br/>the in-silico work has a target"]
  Q3 -->|no| REDIR["Cryptic pocket is an artifact;<br/>redirect the program"]

  classDef done fill:#dff0e4,stroke:#2f8f5b,stroke-width:2px,color:#10231a;
  classDef work fill:#dee7fa,stroke:#3a63b8,stroke-width:2px,color:#111f38;
  classDef next fill:#f0ece1,stroke:#8d8674,stroke-width:1px,color:#2a271f;
  classDef parked fill:#ece3f6,stroke:#6f4a9b,stroke-width:2px,color:#1e1030,stroke-dasharray:2 3;
  classDef dead fill:#f7e6e0,stroke:#b1543a,stroke-width:2px,color:#2e150f,stroke-dasharray:5 3;
  classDef out fill:#f2f2f0,stroke:#9b9b96,stroke-width:1px,color:#2a271f;

  class Q1,Q1B,Q2 done;
  class Q3 next;
  class COV,COVX,NONCOV,SPLIT,ANCHOR,STOP,GO,REDIR out;
```

⚠ **The asymmetry worth noticing:** two of these three branches have a **"no" outcome that SAVES the program
effort**, and both are cheap. Branch 3 is `R4` and needs a bench; branches 1 and 1b were both answered on
2026-08-02 for $0 CPU.

### Branch 1 — ANSWERED 2026-08-02 · serves R8

**✓** ([`nr4a3-covalent-handle-ensemble.json`](../modalities/nr4a3-covalent-handle-ensemble.json))

NR4A3 has **three LBD** cysteines the paralogues lack — C397, C420, C559 — across all 20 conformers
of the experimental 8XTT ensemble. **But uniqueness and pocket-proximity sit on opposite residues:**

⚠ **THE "LBD" QUALIFIER IS LOAD-BEARING, AND ITS ABSENCE MADE TWO DOCUMENTS LOOK LIKE THEY DISAGREED.** The
paper says *"**four** NR4A3-unique cysteines"* (`:1524–1526`) and
[§the hysteresis gate](#-the-first-forwardreverse-hysteresis-this-program-has-ever-measured--gate-passed-2026-07-27-214-pm-et) says *"only **4 of NR4A3's 20** enumerated cysteines are unique"*.
**Both are right, and so is the three — they count over different constructs, and the reconciliation is now
read from the artifact rather than assumed:** [`nr4a-paralogue-unique-residues.json`](../modalities/nr4a-paralogue-unique-residues.json)
gives `summary.n_nr4a3_cysteines: 20`, `n_unique_cysteines_vs_both: 4` **full-length**, and the fourth is
**C166**, which the same artifact marks `in_lbd: false` — *"outside the modelled LBD construct (373–626) — no
geometry"*. So **4 full-length = 3 LBD + C166 outside it**, and C166 is unavailable to any design anchored on
the LBD. ⛔ Neither document stated this; it is recorded here as the one home for the reconciliation.
⚠ **And it is `R13` in miniature**: the construct boundary is not a formatting detail — it removes a real
residue from the design space, and nothing on the plan asks what else it removes.

| | in the pocket | NR4A3-unique | exposed? — **by the module's own `EXPOSED_RSA = 0.25` (`V17`), per conformer** |
|---|---|---|---|
| C496, C536 | **yes** (2.7–6.4 Å) | no — conserved in all three | no — buried (SG SASA ≤ 11 Å²) |
| C397 | no — 10.9–14.1 Å, linker-tether range | **yes** | **yes, 20 of 20** (RSA median 0.464) |
| C420 | no — 16.9–18.9 Å, linker-tether range | **yes** | **mostly — 16 of 20** (RSA median 0.266) |
| C559 | no — 12.2–13.2 Å, linker-tether range | **yes** | ⛔ **NO — 0 of 20** (RSA median 0.205, **max 0.240**, never clears the cutoff) |

⚠ **The "exposed" column is a 2026-08-02 correction, and the old cell was self-refuting.** This table used to
read *"**yes**, and exposed"* across all three — while the paragraph immediately below condemns the positive
control for failing **the identical cutoff**. NR4A3's own C559 fails it in 0 of 20 and was printed as exposed
anyway. ([`nr4a3-covalent-handle-ensemble.json`](../modalities/nr4a3-covalent-handle-ensemble.json)
`ensembles.NR4A3_8xtt_nmr.cysteines`; §MECHANISM-FIRST already had it right —
*"**C559** … buried in this conformer, so **not currently tether-reachable**"*.) **Superseded, retained:** the
blanket *"yes, and exposed"* and the pooled *"11–19 Å"* band, now given per residue.

⛔ **AND THE CRITERIA FAILED THEIR OWN POSITIVE CONTROL — this is instrument `V17`.** NR4A1 **Cys551** — the
site a real degrader is believed to use — does not pass the pre-specified exposure cutoff of
`EXPOSED_RSA = 0.25`. **Two distinct measurements say so, and this page previously merged them into one
sentence that understated the failure:**

| object measured | reading | verdict |
|---|---|---|
| the **state-matched opened model** (n = 1) | RSA **0.165** | below 0.25 |
| the **25-frame NR4A1 metadynamics ensemble** | RSA 0.026–0.223, **median 0.064**, max 0.223 | flagged in **0 of 25** frames |

⚠ **Superseded, retained:** *"does not pass the pre-specified exposure cutoff (RSA 0.165 against 0.25) in 0 of
25 frames"* — which reads as 0.165 in each of 25 frames. The ensemble median is **0.064**, i.e. **2.6× lower**,
so the control fails *harder* than this page used to state, not softer. Keeping them apart matters because the
rank argument below is computed on the **single opened model** pool, not the ensemble.

The thresholds were **not moved**; a test asserts the module holds no local copy of them. What survives is a
threshold-free **rank**: across all 18 NR4A-family LBD cysteines (`control_rank.pool` = the state-matched
opened models), C551 ranks **3/18** on every accessibility observable, and the two above it are NR4A3's C397
and C420.
**So "C397 is flagged in 20/20 conformers" is worth nothing on its own** — the same criteria miss the known
site. The rank is the claim; the cutoff is not.

⛔ **AND THIS FINDING PROPAGATES — it is not confined to branch 1.** Anything on this page adjudicated by the
same `EXPOSED_RSA = 0.25` cutoff inherits a criterion with a **demonstrated false negative on its own
positive control**. That includes **Route B**'s chemical basis and `R8`/`R15`, both of which are now
annotated. ⚠ It also reaches the *paper*, which reports its preregistered **Tier 0** gate as *"**pass on both
axes**"* on the strength of the word **exposed** — adjudicated by this same cutoff — with no mention of the
Cys551 failure anywhere in the paper or SI. **That is a manuscript finding, recorded in
[§12](#12--findings-that-belong-to-other-documents) and not fixed here.**

⚠ Two measurement caveats that change how any published RSA should be read: the thiol's **own HG proton
occludes a median 91.8 %** of the SG surface (n = 16; min 0.21, q1 0.643, q3 1.0, max 1.0, **mean 0.777**;
recomputed from the 16 per-cysteine entries), so protonated-thiol RSA is not the surface a warhead reaches
(both conventions now reported); and SG SASA was quantized at 1.34 Å² by a 96-point sphere until single-atom
measures were moved to 960 points. Ranks were unchanged by the fix.
⚠ **Superseded, retained: the median occlusion figure of 76 %.** It was read off the artifact's **first**
generation (`n: 12, median: 0.764`) and never re-read after the 960-point regeneration ten minutes later
(`n: 16, median: 0.918`). Neither the current median (0.918) nor the current mean (0.777) rounds to 76 %.
This page was the sole home of that number, so nothing else carried the error — and nothing else would have
caught it. ⚠ **It is invariant 5's exact failure mode, and it has now happened twice** — the pose RMSD in
[§5 row R5](#5--where-each-requirement-stands) is the second instance, found by this merge.
⚠ **Not answerable from what exists:** there is no experimental NR4A1/NR4A2 ensemble, so the like-for-like
ensemble comparison is a missing input, not a negative result.

### Branch 1b — COMPUTED, NOT RECONCILED TO ITS ARTIFACT

**✓ computed · ⚠ not reconciled**

⚠ **THE BANNER THIS SECTION CARRIED IS SUPERSEDED, AND WHAT REPLACES IT IS NARROWER.** It read: *"⛔ THE
ARTIFACT THIS SECTION CITES DOES NOT EXIST YET … every figure in this subsection is currently an uncommitted
reported value, not a read one. A CI run has been dispatched to produce it."* **That run landed.**
[`nr4a3-linker-covalent-reach.json`](../modalities/nr4a3-linker-covalent-reach.json) is committed at
`dc0befd9c` and carries a full `verdict` block. *(Provenance note per CLAUDE.md §7: it was committed on the
working branch and reaches `main` with this merge; before that it was branch-only, which is the branch-drift
condition and is why the check was worth taking.)*

✅ **RECONCILED 2026-08-03, CLAIM BY CLAIM, AND THE HOLD IS LIFTED.** Every branch-1b figure below was re-read from the landed artifact one at a time; the corrections are applied in place and the superseded readings are named where they stood. **What survived unchanged:** C420 refuted at 0 of 60 (placement × pendant) cells under both conventions; C559 surviving at exactly one cell (`vhl|M3@term_a_exemplar | dab_branch`, 2 of that cell's 19 conformers, through-space only); the closer being on a paralogue chain in 30 of 30 graded cells under each convention; NR4A1 C505 closing 24 of 30 through-space cells and NR4A2 C534 closing 23 of 30 corridor cells; C505 aligning to NR4A3 **C536** (which NR4A3 HAS) and C534 to NR4A3 **S565** (which it lacks). **What is newly qualified:** `closed_by` is a TIE-BREAK, not a measurement, in **35 of the 93 rows that have a closer at all** — two or more cysteines arrive at the same atom count — so the honest form names the SET that arrives first, never one residue. ⚠ *Superseded, retained: "⛔ BUT DO NOT QUOTE BRANCH 1b's NUMBERS YET, FOR A NEW AND MEASURABLE REASON … result 3 names **NR4A1/NR4A2 C534** as the residue that closes C397's window" — result 3 was corrected before this pass and the banner outlived the error it described.* The prose below was written
from the agent's reported values and **has not been reconciled to the landed artifact**, and at least one
disagreement is readable today: result 3 names **NR4A1/NR4A2 C534** as the residue that closes C397's window,
while the artifact's widest graded cell records `closed_by: "NR4A1 C505"` at 17 backbone atoms (with NR4A2
C534 also at 17 and NR4A1 C534 at 18). The **direction** of the finding is unaffected — the artifact's own
headline is that *"in 30 of the 30 graded cells the FIRST cysteine to come into reach is a PARALOGUE one"* —
but the specific residue, the per-convention cell counts and the window widths must be re-read from the
artifact before any of them is quoted. **That reconciliation is a $0 item on the roadmap
([§10](#10--the-roadmap--one-ordered-list)), and it belongs to the branch-1b pass, not to this merge.**
⚠ Nothing else on this page depends on it: branch 1's cysteine census is a separate, committed artifact.

Branch 1 put the unique cysteines out of *warhead* reach and inside *linker* reach, which is an invitation
rather than an answer: a PROTAC's linker passes through exactly that band, so an electrophile carried there
could ask the warhead only to bind rather than to discriminate. Computed in
[`nr4a3-linker-covalent-reach.json`](../modalities/nr4a3-linker-covalent-reach.json) (+ `.md`) — geometry
only, $0 CPU, and it **owns every number below**.

```mermaid
graph TD
  L{"✓ Can a linker present an electrophile<br/>at an NR4A3-unique cysteine<br/>while the E3 reaches solvent?"}
  L -->|"C420: no, 0 of 60 cells<br/>C559: 1 of 60, through-space only"| DEAD["⏸ at chemically routine<br/>linker length — not ✕: the bound<br/>is routine length, which a non-routine<br/>linker could exceed"]
  L -->|"C397: yes"| WIN{"✓ Does anything else<br/>come into reach first?"}
  WIN -->|"not an NR4A3 conserved<br/>cysteine — C536 is later"| PAR["Closed by a cysteine on a<br/>PARALOGUE chain — C505 aligns to<br/>NR4A3 C536 (NR4A3 HAS it);<br/>only C534 → S565 is one NR4A3 lacks"]

  classDef done fill:#dff0e4,stroke:#2f8f5b,stroke-width:2px,color:#10231a;
  classDef dead fill:#f7e6e0,stroke:#b1543a,stroke-width:2px,color:#2e150f,stroke-dasharray:5 3;
  classDef out fill:#f2f2f0,stroke:#9b9b96,stroke-width:1px,color:#2a271f;

  class L,WIN done;
  class DEAD dead;
  class PAR out;
```

⚠ **`DEAD` is drawn dashed but carries no ✕, deliberately.** It is an *approach* (put the electrophile at
C420 or C559) rather than a claim, so it is eligible — but the bound it failed is "chemically routine linker
length", which a non-routine linker could exceed. Under [§0.2](#02--work-state--the-five-glyphs)'s strict bar
that is ⏸ at best, not ✕. ✅ **Classified 2026-08-03: ⏸, not ✕, and the two cysteines are not equal.** C420 is the strong case — 0 of 60 cells, both conventions, no conformer — but it is still bounded by *routine* length rather than by geometry, so ⏸ is the honest glyph for it too. C559 is weaker still: it survives at one cell. ⚠ **The artifact's own `refuted_unique_cysteines` list is built from `best_corridor` alone** (`nr4a3_linker_covalent_reach.py`, the `live`/`dead` split), so it silently drops the through-space evidence recorded two fields away, and it is stronger than the artifact's own data.

Three results, in the order they change what the program should do:

1. **The recorded architectural blocker does not apply.** A linker-borne electrophile plus an E3 arm was
   taken to need the two-branch template of [`linker_twobranch.py`](../modalities/linker_twobranch.py). It
   does not: `build_smiles` places the E3 at a chain **terminus**, so the single pendant slot is free and
   the committed library already contains such one-branch constructs aimed at C397. Two branches are needed
   only to carry the electrophile *and* the RUNG-5a causal wedge together — a different molecule for a
   different experiment. Read from the enumeration, not recalled, and pinned by a test.
2. **Only C397 survives cleanly.** ⚠ **C420 is refuted everywhere (0 of 60 cells); C559 is NOT** — it
   survives at one cell (`vhl|M3@term_a_exemplar | dab_branch`, 2 of 19 conformers) under through-space, the
   optimistic best-of-N anchor with the longest pendant. The weakest possible form of a survival, but not
   zero. C420 and C559 otherwise need far more backbone atoms than the imported
   chemically-routine bound, at all ten placements of the five basins that survived term-(b), at every
   pendant reach, and under both reach conventions. C420 is closed. C559 is closed under the corridor convention everywhere and at 59 of 60 through-space cells — closed enough to plan against, not closed enough to write down as zero.
3. ⛔ **The counter-test fires from the opposite direction to the one it was designed to check.** The window
   is not closed by an NR4A3 *conserved* cysteine. It is closed first by a cysteine belonging to a **paralogue
   chain** rather than to NR4A3 — 30 of 30 graded cells under each convention. ⚠ **But WHICH one, and whether
   it is a site NR4A3 lacks, differs by convention and must not be merged** ([`categorical-axis-audit.json`](../modalities/categorical-axis-audit.json)):
   under **through-space** the closer is **NR4A1 C505** in **24 of 30** cells, and C505 aligns to NR4A3
   **C536** — so NR4A3 *does* carry a cysteine there and the reciprocal-uniqueness reading does **not** apply
   to it; under **corridor** it is **NR4A2 C534** in **23 of 30**, and C534 aligns to NR4A3 **S565**, which
   NR4A3 genuinely lacks. The reciprocal-uniqueness finding is real but is carried by C534 under one
   convention, not by both closers under both — concordant across both paralogue metadynamics ensembles as ⚠ **And C534 is not the only paralogue-unique cysteine.** NR4A1 **C551** aligns to NR4A3 **T579** and is also a site NR4A3 lacks; it sits far outside the window (30 backbone atoms in the widest graded cell against a closer at 17), so it changes nothing here — but the reciprocal-uniqueness set has two members, not one.
   well as the single opened models. **Uniqueness runs both ways, and the reciprocal direction had never been
   computed anywhere in this repo.** A residue-uniqueness argument built only on "which of MY residues do they
   lack" is therefore incomplete by construction. ⚠ *Which* paralogue cysteine closes it first is exactly the
   figure the reconciliation above must settle.

⚠ **How far these numbers may be trusted.** The paralogue positions come from
three independently built opened models. At aligned cysteine pairs their backbones agree far better than
their side chains, so the artifact reports ΔCA against ΔSG per pair and states the sulfur displacement that
would reopen the window (**6.25 Å** — the median 5.0 atoms of lost window at 1.25 Å per atom) against the largest
displacement observed at any aligned pair (**5.94 Å**). ⚠ **That clears by 0.31 Å, a 5 % margin — and it
cannot cover C534 at all**: the yardstick is built from the 8 ALIGNED cysteine pairs, and C534 has no aligned
NR4A3 partner *because* it is paralogue-unique. So the residue that closes 23 of 30 corridor cells is the one
residue the noise test is structurally unable to bound. The **direction** of result 3 rests on sequence plus fold-level position; the exact
backbone-atom counts do not, and must not be quoted more precisely than that record allows.
⚠ Everything here is conditional on **the cryptic pocket being the right site**, not on a docked ligand pose: the
warhead exit vector is **marginalised** over **12** pocket-mouth anchors precisely because no cmpd19 pose exists
in this frame ([`nr4a3-orientation-basins.json`](../modalities/nr4a3-orientation-basins.json) `_limits[0]`, `inputs.n_poses`).
That is what decides how `V3` bears on it: **`V3`'s failure was SITE selection, on 6 of 6 pairs — not pose
accuracy** — and site selection is exactly what these anchors rest on. A *pose*-accuracy failure is already absorbed
by the marginalisation; a *site*-selection failure voids every reach number here. ⚠ *Superseded, retained: "conditional
on the docked pose the anchors come from, whose known-answer test is `V3` — which returned INCONCLUSIVE."* Reach is a necessary condition for a covalent handle and never a sufficient
one: no thiol pKa, intrinsic reactivity, adduct or degradation quantity is computed, and no selectivity,
efficacy, safety or feasibility claim follows.

---

## 8 · The two live routes to selectivity — and where each is actually blocked

★ **Selectivity has to come from somewhere specific.** Two places are real, they are **complementary rather
than competing**, and a candidate could use both. ⚠ **And there is a third that this page kept omitting** —
the **categorical transfer-zone lysine term** (`V18` → `R12`), which is set membership rather than energy and
is therefore immune to the resolution problem that blocks both routes below. It is not a route to a *binder*,
which is why it sits under `R12` and not here, but a program that presents "two live routes" without it is
under-selling its own strongest categorical argument.

⚠ **AND "TWO" (OR THREE) IS A SHORTLIST, NOT AN ENUMERATION — AND A SHORTLIST CANNOT SHOW WHAT WAS NEVER
CONSIDERED (2026-08-02, $0).** The full enumeration is
[`selectivity-mechanism-options.md`](../modalities/selectivity-mechanism-options.md) /
[`.json`](../modalities/selectivity-mechanism-options.json) — **17 mechanisms, of which 9 had no row, node or
mention anywhere in this program**, each graded on physical basis · instrument · *whether that instrument has
passed a known-answer test **in the needed regime*** · whether a valid positive control could exist here ·
cheapest decisive test. **⛔ It is an OPTIONS REGISTER and amends nothing** — no gate, no criterion, no rung,
no row of [§10.1](#101--open-rows-ordered-by-what-unblocks-the-most). Four of its results bear directly on
this section and are measured, not argued:
- ★ **A new mechanism grades above every non-incumbent option on this page: STERIC EXCLUSION (negative
  design).** At three Pocket-5 positions both paralogues carry a strictly bulkier side chain
  (L406→His/His, I484→Tyr/Tyr, L534→Phe/Phe), so it is answered by **shape** rather than by a ~1 kcal/mol
  ΔΔG — the resolution problem Route A cannot escape. Measured **with its own null**, which is the part that
  matters: paralogue-only clash **0.923** at those three positions against **0.173** at conserved/shared
  ones, and **0.000** at the paralogue-unique-but-not-bulkier positions.
  - ⛔ **AND ITS OWN CONTROL CAPS WHAT IT MAY SAY — read this before the clash number is quoted anywhere.**
    The register ran the discriminating control (`M4`): the paralogue **does not refuse the molecule, it
    RELOCATES it**, by a median of ~5.3 Å in both paralogues. So the exclusion is real **about the POSE and
    says nothing about whether the paralogue binds the molecule at all.** That makes this a **design rule** —
    *grow the substituent into the L406/I484/L534 lobe* — and not a selectivity claim, and it is the honest
    ceiling for any negative-design argument. Two further limits the register states and this page inherits:
    the transfer is **rigid** (the paralogue side chain is held in its own opened conformer and could rotate
    away), and the *absence* of NR4A3 clash is **guaranteed by construction** because these poses were docked
    into NR4A3, so only the between-class contrast is gradeable. It also inherits `R5` — it is conditional on
    the cryptic pocket being the right site.
- ⛔ **Route A's seven divergent handles split.** Six are *categorically* unique (a residue type absent in
  both paralogues); only three of those are bulkier in both paralogues, and those three are the only ones the
  steric test fires on. Uniqueness alone does not create an exclusion.
- ⛔ **A route this page does not list is refuted there on committed data:** the cryptic pocket is **not**
  NR4A3-specific — both paralogues reach NR4A3's druggable CV inside their own matched metadynamics, and
  under the harmonized detector the site is **detected in essentially every frame of all three species**.
  ✅ **Now graded and filed** — ✕ dead in [§6a](#6a--dead--conclusively-unworkable-never-retry), scoped to
  the categorical form.
  - ★ **BUT WHAT SURVIVES IS NO LONGER JUST "the quantitative form is `R6`" — IT IS MEASURED, AND IT IS THE
    ONLY THING ON THIS PAGE THAT DISCRIMINATES THE PARALOGUES WITH NO FREE ENERGY IN IT (landed 2026-08-03,
    $0 CPU, 0 refusals).** Over **matched** unbiased ensembles under one identical harmonized detector build,
    NR4A3 reaches D\* markedly more often than either paralogue, and the run **reproduces the committed NR4A3
    rows exactly** — so the contrast is not an artifact of a re-build. Every figure is owned by
    [`paralogue-pocket-contrast.json`](../modalities/paralogue-pocket-contrast.json).
    ⛔ **It is a RANKING and nothing else, and its own artifact refuses three readings that this page adopts
    verbatim:** it is **not** `R6` — *"a detection fraction is not an opening penalty and must never be
    reported as one"*; it is **not evidence of ABSENCE** — at these ensemble sizes even a paralogue that
    never opened would be weak evidence, so it *"supports a ranking, never a categorical exclusion"*; and a
    paralogue row of zero would mean *"NR4A3's site did not open here"*, **never** *"this protein has no
    druggable cavity"*, because the site definition is NR4A3's Pocket-5 mapped by alignment.
    ⚠ **Superseded, retained, and it is invariant 5's failure mode caught within the hour:** the refutation
    above was first written on *"fpocket rates NR4A1's opened frame **more** druggable (0.981 vs 0.931)"* —
    **one frame per species**, and the matched replicated reading points the other way on frequency. The ✕
    rests on **detection**, which is set membership; it never rested on a druggability ordering, and must
    not be quoted as though it did.
- ⛔ **The `V18` lysine term's intuitive form is refuted there too** — the paralogues are **not** lysine-poor
  (see the like-for-like triple in [§the Tier-2 result](#-tier-2-result-in-full--the-12-pose-run-at-its-corrected-exact-kernel-values-lane-2-2026-07-25-reach-correction-2026-07-26-0-realized--no-gpu)).
  What survives is the rare *joint* event, which this page already states correctly. ✅ **Now graded and
  filed** — ✕ dead in [§6a](#6a--dead--conclusively-unworkable-never-retry), scoped to the availability form.

### Route A — a warhead engaging paralogue-divergent pocket handles · ○ **blocked, nothing running** · serves `R7`

⚠ **Superseded, retained:** this heading read *"◐ **in work**"*. Nothing on Route A is running or has ever
run.

**Chemical basis — divergence: ✓ measured. Facing: ⚠ reported, NOT confirmed.** The two halves have different
provenance and this page used to give both the first one's weight.

- **✓ 7 of 10 divergent, and this is well sourced.** Of the **10 Pocket-5 lining residues, 7 are
  paralogue-divergent** — L406, T407, T410, R412, I484, I531, L534
  ([`nr4a-selectivity.json`](../modalities/nr4a-selectivity.json) pocket 5: `n_residues: 10`,
  `n_divergent: 7`, `selectivity_handles` = exactly those seven; paper §2.4 `:595–599`, word for word).
- **★ AND THE STERIC SUB-AXIS IS NOW A DESIGN RULE WITH TWO VECTORS, NOT SEVEN HANDLES (2026-08-03,
  [§10.1 row 24](#101--open-rows-ordered-by-what-unblocks-the-most)).** Of those seven divergent residues,
  only **I484→Tyr/Tyr (51.9 Å³, reach 4.27 Å)** and **L534→Phe/Phe (60.7 Å³, reach 5.62 Å)** offer a lobe a
  substituent can actually occupy; **L406→His/His fires on clash but offers 2.69 Å³** — less than the
  **conserved** R481's 11.78 Å³, which is the measured bar — and **R412 has the largest lobe of all (68.8 Å³)
  and must not be the top target**, because it is `unique_not_bulkier`, fires at 0.000, and carries the worst
  post-fit deviation in the set. **Volume never overrides class.** Vectors, shape spec and per-candidate
  scorer: [`steric-design-rule.json`](../modalities/steric-design-rule.json).
  ⛔⛔ **AND THE CONTROL TRAVELS WITH IT, ALWAYS: the paralogue's own docking RELOCATES these molecules by a
  median 5.31 Å (NR4A1) / 5.26 Å (NR4A2), so this constrains the POSE, not binding.** It licenses *"this pose
  is denied in the paralogue"* and **never** *"the paralogue cannot bind this molecule"*. The transfer is
  rigid (side chains could rotate away), and NR4A3's absence of clash is guaranteed by construction and
  carries no information — only the between-class contrast is gradeable.
- **⚠ "5 stay pocket-facing" is neither confirmed nor committed.** L406, T410, I484, I531, L534 (T407 and
  R412 mostly splay outward, facing in 0.0 and 0.25 of druggable frames). But **`nr4a-selectivity.json` does
  not own this** — it holds no facing data at all. The owner is `handle_facing_summary.json`, which the paper
  states is *"an **S3-only object that is not committed to this repository**"*, and it was *"computed under
  the **pre-harmonized** tracker and **not** re-run under the harmonized one, so it is **reported but not
  treated as confirmed**, since the set of druggable frames it is computed over is the **superseded** one"*
  (`:552–566`; the number is §2.3, not §2.4). ⛔ **Against this page's own banner** — status is read from
  committed artifacts, never typed — this cell was typed. ⚠ **Superseded, retained:** *"Chemical basis: ✓
  strong, and already measured."*
- ⛔ **And the engageable set is NARROWER against ONE of the two paralogues.** Against NR4A1 all 7
  handles differ. Against **NR4A2 only 6 of 7** differ — **I531 is Ile in both NR4A3 and NR4A2**
  (`nr4a-selectivity.json`: `nr4a3 "I531", nr4a1 "V", nr4a2 "I"`) — so of the 5 engageable handles only
  **4** distinguish NR4A3 from NR4A2 (`:606–611`, repeated at `:2421` and `:2568`), and this page carried
  the caveat nowhere while the paper carries it in three places. ⚠ Note this is
  [§6a](#6a--dead--conclusively-unworkable-never-retry)'s own rule applied to this page's preferred route:
  *"a residue the paralogues share cannot discriminate between them."*
  - ⚠ **CORRECTED 2026-08-03 — the DIRECTION of that thinness was stated as evidenced and is not.** This
    bullet read: *"the engageable set is NARROWER against the paralogue that matters most … That is the
    paralogue carrying the dopaminergic-loss liability one most wants to spare. Route A is 20 % thinner
    exactly where it can least afford to be."* **Superseded, retained** — the ranking it asserts rests on
    NR4A2's lethality, which is flagged **UNCONFIRMED** and has no phenotyped KO, while NR4A1 carries a
    **named anti-target genotype** ([§2.4](#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically)).
    The defensible reading inverts the emphasis without moving a number: **the handle set is complete
    against the paralogue whose sparing is evidenced-mandatory and one short against the paralogue nobody
    has bounded in either direction.** *Unbounded is not smaller* — this narrows the claim, it does not
    relax the design.
- ⚠ Statistical hedging this page also dropped: *"a two-test Bonferroni correction moves p = 0.028 to
  **0.056**, i.e. borderline"*, plus spatial-correlation and selection caveats (`:658–672`).

★ **And all ten are ortholog-invariant across six species spanning ~300 My** — paralogue-divergent yet
species-conserved, which is both a resistance argument and evidence the divergence is functional rather than
drift. ⚠ **Sourcing caveat:** the owning artifact `nr4a-resistance-map.json` is **absent from this branch and
from `main`** — it exists only on `origin/modalities-cache`, and its producer is run with a soft-fail
(`depmap-dependency.yml:59`). Exactly the branch-drift condition in
[§12](#12--findings-that-belong-to-other-documents). *(Where it does live, the content
agrees: all 10 rows `ortholog_conserved_fraction: 1.0`, 5 orthologs + human.)* The **"~300 My"** figure is in
no artifact at all — it is a literature inference carried in prose.

#### ⛔ Where Route A is blocked — three things, and only one of them is the instrument

**This section previously said "Blocked on the INSTRUMENT, not the chemistry — and the instrument is ◐
running." Every clause of that was wrong.** Corrected 2026-08-02:

1. **The instrument (`V4`).** The margin these handles would produce is a free-energy quantity, and the ABFE
   engine has **never recovered a known *selectivity* ΔΔG — i.e. one across two pockets.** ⚠ The unqualified
   form ("never recovered a known ΔΔG") is too strong and [§3.1](#31--the-instrument-table) refutes it: `V6`
   passed *within one pocket*, and `V10` **has** recovered a published known answer.
2. ⛔ **The physics term nobody has computed: `R6`, ΔG_open per paralogue.** Validation requirement 2 says
   matched-open comparison can **"miss or REVERSE selectivity."** **A passing instrument would not fix
   this** — so "blocked on the instrument" was never the whole sentence.
   ⚠ **AND THE BLOCK IS ROUTE A's, NOT THE PROGRAM's (2026-08-03).** `R6` is a term in an **absolute**
   per-paralogue affinity, which is exactly the currency Route A works in. It **cancels inside each protein**
   in a ligand-side *relative* double difference, so it does **not** block that route to `R11`'s causal
   question — [§3.4 fact 3](#34--three-instrument-facts-this-page-used-to-be-missing). Stating the block
   globally made a live route look shut.
3. ⛔ **The size of the prize versus the resolution.** [§the hysteresis gate](#-the-first-forwardreverse-hysteresis-this-program-has-ever-measured--gate-passed-2026-07-27-214-pm-et): a useful
   degradation window needs **~2.0 kcal/mol** of true margin, against a best-case **resolvable** difference
   of **0.60** and an accuracy of **1.543 kcal/mol, wrong sign**. Even a perfectly calibrated
   engine at the current SD resolves 0.60 against a requirement of ~2.0. ⚠ **So a passing CREBBP/BRD4
   benchmark would not settle Route A**, and reading this section without those three numbers invites exactly
   that conclusion.

#### `V4` — the CREBBP/BRD4 selectivity ABFE, read on all three axes at once

> **Highest leverage in the program · 🔒 not authorized · would not discharge the paralogue claim.**

- **LEVERAGE — highest, and this is not softened by anything below it.** It is the **single
  highest-leverage unrun item in the program**, and it earns that independently of scheduling: this program
  has **no binary selectivity control at all** ([§what the SMARCA2/4 null BINDS](#what-this-binds-in-the-words-fixed-before-the-run), *"valA validates
  relative FEP **within one pocket**"*), so it would be the **first** evidence the free-energy engine can
  resolve selectivity **between two different proteins** — the capability every paralogue margin on this page
  presupposes. Both arms are real holo crystals with the **same ligand** (4NR7 / 5BT4), so no docking and no
  pose assumption, against an experimental ΔΔG ≈ **2.2 kcal/mol** (`selectivity-benchmark.json`
  `ddg_kcal_per_mol: −2.19`).
- **AUTHORIZATION — 🔒 not authorized.** [§the standing tally](#the-standing-tally-this-closes): *"**Neither is authorized
  here**."* A scheduling fact. It is **not** a grade, and it must never be recorded as one.
- **SUFFICIENCY — would not discharge `R7`.** [§what the SMARCA2/4 null BINDS](#what-this-binds-in-the-words-fixed-before-the-run): a
  **binary** selectivity control that *"would **not** discharge §4's paralogue/ternary statement"*. Scope,
  not demotion.
- **WORK STATE — ○ not started.** ⛔ **Superseded, retained, and it was a fabrication of status:** *"its
  first leg is now on spot"*, *"solvent leg dispatched"*, *"◐ in work"*, and *"it is the one thing moving."*
  **Nothing is running.** Read live and free on 2026-08-02: **0 in-progress SageMaker training jobs and 0 of
  8 spot instances in use**, at four independent reads between 3:55 and 4:02 PM ET. ⚠ Recorded precisely,
  because the true history is not "nothing ever happened": a dispatch **did** fire at **3:16 PM ET** and
  created training job `sel-cbp30-v1-solvent-2026-08-02-19-16-52-862` (`SPOT: 1`, `ml.g5.xlarge`) against
  STRATEGY.md's non-authorization; it was halted, produced **no result**, and the benchmark artifact still
  has **no `result` key**. The lane's Vast port is committed but explicitly not authorized to run
  (`1130c43ed`). **This page's job is the current state, and the current state is ○ + 🔒.**

### Route B — a linker-borne covalent handle at an NR4A3-unique cysteine · ○ **blocked on `R5`, nothing running** · serves `R8` `R15`

⚠ **Superseded, retained:** this heading read *"◐ **in work"*, and its closing paragraph read *"whose
known-answer test is ◐ running."* **Neither was true.** Nothing on Route B is running; the pose test `V3` ran
and returned INCONCLUSIVE. This is the same correction Route A received on 2026-08-02, applied one section
later — see [§0.2](#02--work-state--the-five-glyphs).

**Chemical basis: ✓ opened 2026-08-02** by the cysteine census above — ⚠ **with the census's own criteria
caveat attached**: the exposure cutoff that adjudicates "exposed" is `V17`, shown in branch 1 to **miss its
own positive control** (NR4A1 Cys551, 0 of 25 frames), so this basis rests on the threshold-free **rank**, not
on the cutoff. And of the three unique LBD cysteines, only **C397 (20/20)** clears it outright; C420 clears
16/20 and **C559 clears 0/20**.

The unique cysteines sit 11–19 Å out — *where a PROTAC's linker passes*, not where its warhead sits. So put
the electrophile on the **linker** and let it react with a residue NR4A1 and NR4A2 do not have. That is the
NR-V04 mechanism relocated to where NR4A3's unique residues actually are.

⛔ **Superseded, retained — Route B's old framing rested on a number borrowed from a different protein.** The
argument used to run *"instead of asking the warhead to discriminate an **~80 %-identical pocket** …"*. That
figure is **SMARCA2/SMARCA4** ([§the SMARCA2/4 gate record](#-gate-failed--the-smarca24-sensitivity-control-returns-null-on-an-adequately-powered-design-2026-08-02-1042-pm-et); paper `:2109`), transplanted onto NR4A.
**Nothing in this repo puts the NR4A paralogue pocket at ~80 % identity.** The NR4A numbers:

| object | reading | identity |
|---|---|---|
| Pocket-5 lining | `n_residues: 10`, `n_divergent: 7` ([`nr4a-selectivity.json`](../modalities/nr4a-selectivity.json)) | **30 % identical** |
| the LBD overall | `n_residues_aligned: 254`, `n_divergent_any: 109`, `pct_divergent_any: 42.9` ([`nr4a3-differential-surface-atlas.json`](../modalities/nr4a3-differential-surface-atlas.json)) | **≈57 % identical**, pooled across both paralogues |

★ **AND THE PER-DOMAIN, PER-PARALOGUE VERSION (2026-08-03, $0 CPU over the cached UniProt sequences) SHARPENS
IT INTO A RESULT THE PROGRAM CAN USE.** The domain-resolved identities — zinc-finger DBD, hinge, LBD, AF1,
each against NR4A1 and against NR4A2 separately — are owned by
[`target-route-census.json`](../modalities/target-route-census.json) (`paralogue_identity_by_domain`,
`zinc_finger_window`) and read out in [`target-route-options.md`](target-route-options.md) finding 1. **Two
consequences, and both are load-bearing:**

1. ✅ **The program is already standing in the most divergent ordered domain of the protein, and the pocket
   lining is more divergent still.** *"Work somewhere easier"* has no destination on this target — which
   turns a premise that read as a liability into a favourable fact.
2. ⛔ **Every route that relocates the target toward the DBD or DNA binding makes the requirement strictly
   worse**, by a wide margin and on arithmetic alone. Closed for that reason in
   [§6a](#6a--dead--conclusively-unworkable-never-retry).

⚠ **The `≈57 %` above is not superseded by these** — it is a different quantity (pooled "divergent in
either paralogue" over the aligned LBD), and both readings stand. The per-paralogue split is what
[§2.4](#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically)'s asymmetric
brief needs and the pooled figure cannot supply.

⚠ **And the borrowed number inverted the argument.** Route B's rhetorical case was *"Route A is asking the
warhead to do something very hard, so use the linker instead"* — argued **sixteen lines after Route A reports
7 of 10 lining residues divergent**. On this page's own numbers that premise is backwards: the pocket lining
is the *most* divergent object here, not the least. **Route B does not need Route A to be hopeless, and it
never did.** It stands on its own mechanism: a **categorical** discriminator — a residue the paralogues do
not have — which is a set-membership fact rather than an energy difference the method cannot resolve. That is
the honest case, and it is a stronger one.

⚠ **A constraint that cuts against the band Route B proposes to work in.**
[§Program and thesis](#program-and-thesis) puts reach-only P(a paralogue Cys is also reached | an NR4A3-unique
one is) at **0.000–0.003 at 12 atoms, 0.054–0.133 at 16, 0.263–0.383 at 20**, and concludes *"**keep the
linker SHORT** … any design drifting to 16+ atoms **trades away the axis it exists to exploit**."*
⚠ *Superseded, retained: the pilot pair "0 at 12 atoms, 0.081 at 16, 0.258 at 20".* Route B places the
electrophile at 11–19 Å, i.e. **into that band**. This is a design constraint on Route B, not a refutation
of it.

★ **Route B's only redundancy — the unique-LYSINE axis (`V18` → `R12`).** The paper is
explicit: *"The program's **only insurance** against a C397-specific chemical failure is the
**unique-lysine** term, not a second cysteine"* (`:1568–1569`). Route B as drawn has a **single point of
failure** — C397 is the one cysteine that survives every test — so the hedge matters. Four NR4A3-unique
lysines exist, of which **K518, K572, K592** are exposed in the LBD (13.4 / 11.5 / 16.2 Å from the cryptic
pocket), and *"a lysine that is not present cannot be ubiquitinated"* is as categorical as the cysteine
argument. It feeds `R12`, not this route's covalent chemistry.

✓ **The geometry block is now COMPUTED, and the counter-test did not kill it** (branch 1b above). The feared
outcome — a **conserved** cysteine always in easier reach than a unique one — did not occur. C397 survives at
routine linker length; C420 and C559 are closed. What *does* close C397's window is a **paralogue** cysteine —
a residue NR4A3 lacks, which is the opposite direction to the one the counter-test was designed to check.
⚠ **Read with branch 1b's reconciliation caveat.**

★ **AND THE ROUTE NOW HAS A NAMED MOLECULE AT ITS OWN GATE (2026-08-03, $0 RDKit/CPU).** Route B has argued
for a short linker since it was written and had **no construct at the 12-atom gate** to point at. One exists:
**`vhlM2@ex_5amide_a2-a3_cyac_me`**, InChIKey **`RZSRKKSYYBOIEK-ACNWJKEOSA-N`** — SMILES committed,
backbone length re-derived by RDKit rather than intended, reaching C397's SG under **both** reach
conventions, with a retrosynthetic annotation over catalogue building blocks. Everything about it —
descriptors, basin fidelity, span window, the four floors, the limits — is owned by
[`nr4a3-short-linker-probe.json`](../modalities/nr4a3-short-linker-probe.json); this page carries only that
it exists and what it does not license.

- ⛔ **The library's floor of 14 was a POLICY, not a fact — and that is the finding.** The term binding at
  every gate-clearing basin is `min_member_fraction_comfortable`, a basin-**breadth** threshold; the
  geometric and chemical floor of the committed building-block grid is **11**. *(Superseded, retained:
  *"no enumerated molecule reaches 12 (the shortest is 14)"* as a statement about geometry.)* A design
  constraint that reads as physics but is a tunable is exactly the kind of fact this page exists to expose.
- ⛔ **DEFECT 1 — the E3 is the wrong one for the rung that needs this.** Rung
  [`5b-T`](#the-ordered-plan-spend-gated--read-top-to-bottom-for-whats-next)'s E3 is **CRBN**, and the
  candidate is **VHL**. The best CRBN construct at the gate reaches C397 **through-space only**; under the
  **corridor** convention — a non-clashing branch position with a clash-free arm to the SG — its floor is
  **14**, above the gate. **The two conventions must not be merged**, and the honest CRBN answer is that a
  gate-length CRBN degrader exists on an upper-bound reach rule and not on the conservative one.
- ⛔ **DEFECT 2 — provenance.** The committed construct library no longer reproduces from its own generator,
  and the drift reaches the **causal test article**, not just the count
  ([§10.1 row 25](#101--open-rows-ordered-by-what-unblocks-the-most)).
- ⛔ **What it does NOT license, stated because a named molecule invites exactly this:** no binding affinity
  of anything to anything; no electrophile reactivity, thiol pKa, adduct stability or chemoproteomic
  selectivity; no ternary, cooperativity or productive geometry; no degradation, efficacy, window, safety or
  clinical readiness; and **no proteome-wide selectivity of any kind** — the comparison set is two paralogues.
  It is a **target-engagement geometry** result and inherits `R5`'s unresolved site question.

⚠ **AND THE CATEGORICAL AXIS IS WIDER THAN C397 — BUT ONLY ON THE RULER THIS PAGE PERMITS, AND BOTH READINGS
ARE CARRIED.** The axis had never been swept past cysteine and lysine. Across 11 reactive classes NR4A3
carries a set of paralogue-unique, alignment-robust LBD positions, most within linker reach
([`selectivity-mechanism-options.md`](../modalities/selectivity-mechanism-options.md) `M2`, which owns the
counts). **The sweep cuts both ways and neither reading is chosen here:**

- ⛔ **Under `V17`'s exposure cutoff, NO new handle clears at all** — the credible set collapses to exactly
  the cysteines and lysines already committed.
- ★ **Under the threshold-free RANK this page mandates instead** ([§3.1 row `V17`](#31--the-instrument-table)),
  **Y419** — a SuFEx tyrosine one residue from C420 — sits **above NR4A1 Cys551**, the family's one
  literature-anchored covalent site and the very false negative that discredited the cutoff.
- ⛔ **M398/M399 fall below the reference on BOTH readings and are dropped, not carried.** Naming them is the
  point: a sweep that only reports what survives is a sweep nobody can grade.
- ⚠ **Limits inherited whole:** sequence uniqueness is exact, but every geometric annotation is **one static
  opened conformer**; and **chemistry credibility is a literature label, not a computed quantity** — no thiol
  or phenol pKa, nucleophilicity, adduct stability or electrophile promiscuity is modelled anywhere. SuFEx
  tyrosine is precedented rather than routine, and **every added handle re-opens the chemoselectivity-window
  question** that C397 already answers badly.

⛔ **What remains blocking is upstream, not here:** every anchor comes from the docked pose, whose known-answer
test `V3` returned **INCONCLUSIVE** — and the re-run that would settle it has not started. Reach is a
necessary condition for a covalent handle and never a sufficient one.

**Why they compose:** a warhead tuned to the four-to-five engageable divergent handles *plus* a covalent linker
handle at a unique cysteine *plus* the categorical lysine term is a far stronger selectivity argument than any
alone — three independent mechanisms, each with its own falsifier.

---

## 9 · Result lanes the graph could not express

★ **Added 2026-08-02.** An audit against the paper found whole result lanes with **no node, row or mention**
anywhere on this page. Some are results rather than dependencies and their absence was arguable; the ones below
are load-bearing, because each either constrains an instrument this page relies on or *is* a dependency the
graph could not express.

| lane | what it is | serves | why the roadmap needs it |
|---|---|---|---|
| **§2.9 congeneric RBFE map** — 18 of 18 computable edges, **$73.79** realised GPU spend | the program's largest completed quantitative lane | `V6` → `R7` | ⛔ **It contains the most concrete evidence about the reliability of the free-energy machinery `V4` and Route A depend on**, and it is *negative*: the `cycle_3carbonyl` triangle (cmpd19 → free acid → primary amide → cmpd19) sums to **R = +1.307 and is a VIOLATION** of tolerance — *"at least one of them is **not converged or not consistently mapped**, and all three are therefore quoted under that reservation"* (`:1405–1423`). Separately, **an independent recomputation of one edge disagrees with the pilot by more than either stated uncertainty**: cmpd19 → 5-NH₂ at **+1.84 ± 0.36** against the fan-out's **+1.064 ± 0.118**, a gap of **≈0.78 kcal/mol** (`:1425–1433`). [§3.1](#31--the-instrument-table) records an *unrun* benchmark for `V4` while the program had already found, on its own system, that two runs of one perturbation differ by several times their own error bars |
| **§2.10e causal matched-pair test** — **S = −0.1297 ± 0.3264 kcal/mol** | *"the **only** test in this program that asks whether a designed element **causes** discrimination"* (`:1782–1783`) | `V16` → `R11` | ⛔ **A dependency, not a result.** It is the causal test of `R11` and of Route B's mechanism, it has **run**, and it returned a preregistered null **with a quantified bound** — the design could only have resolved *"a wedge contribution of roughly **\|S\| ≳ 0.65 kcal/mol** (2σ)"* (`:1798–1800`). A dependency graph with no causal node cannot express the paper's own Tier-2/Tier-3 structure. ⛔ And it has **no calibrator** ([§3.4](#34--three-instrument-facts-this-page-used-to-be-missing)) |
| **§2.1 BioEmu** unbiased ensemble cross-check — **12.5 %** druggable | the honest open-state population estimate | `V14` → `R1` | an **orthogonal evidence axis** for `R1`, independent of the metadynamics that Gate 1 and Gate 3B are argued over |
| **§2.2 PocketMiner** + four permutation nulls (p = 0.009 / 0.0001 / 0.036 / **0.74** / 0.014) | the only **independent-method** support for the cryptic site | `V15` → `R1` | `R1` rests on it, and one of the five nulls (**p = 0.74**) does not support it — a mixed result this page showed as a clean ✓ |
| **`denovo_401`** — the paper's **sole carried candidate** (§2.7, §2.8, §3, §5 Gate 4, SI §S1–S3) | the molecule every downstream claim is about | `R5` `R7` `R15` | it is the subject of `R5` and `R7`, of `V19`'s unrun generative arm, and of the `R3` submission gate that can invalidate the receptor it was generated into |
| **SI §S3 superfamily liability screen** — MR/AR | *"the **sole** sequence-level non-paralogue follow-ups"* that *"must clear"* (SI `:213–219`) | `R14` | a **live gate on claim scope**, not a result: nothing on this page said the selectivity claim is currently bounded to two paralogues by an unrun cross-binding check |
| **The linker library + matched pair** — 54 constructs, RDKit 54/54 | the deliverable `R15` is about | `R15` | it is what a "candidate set" means in the final deliverable, and the two-mechanism decision that would extend it has never been asked for |

---

## The prospective stage: mechanism-first, then orientation-first inverse design

*★ **THE KILL-SWITCH SEMANTICS, the four-tier table and the Tier-2 result in full.** `e3_recruiter_staging.py` reproduces its panel verbatim. Registers: `R11`, `R12`, `R15`.*

The molecule-first approach — enumerate a fixed {warhead×exit×ligase×linker} matrix, model each ternary, score,
and hope the Pareto front contains a selective degrader — is a well-controlled lottery: it *verifies* selectivity
if already present but never asks the design question. Orientation-first fixed that. Putting the **mechanism**
above the orientation fixes what the orientation search is optimising:

```
paralogue-unique CHEMISTRY (nucleophile) + paralogue-unique GEOMETRY (lysine)
    → basins that exploit ONE of them → productive CRL geometry
    → interface thermodynamics used to RANK within the survivors
    → linker requirements → candidate molecules
```

This removes blind linker guessing and preserves everything requirement 5 mandates (Pareto/uncertainty,
EWSR1::NR4A3 fusion context, lysines beyond the LBD, full CRL/E2~Ub ensembles). Four additions to the basin
search, all **$0 CPU** (rationale and evidence: the [2026-07-24
revision](nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md)):

- **(a) Electrophile-reach term** — does the basin's linker path pass within tethering distance of C397 / C420 at
  a geometry a mild electrophile could adopt? Neither sits *inside* the pocket, so this is an electrophile on the
  **exit vector or the linker**, which in a degrader is architecturally free — the linker already leaves the
  pocket and travels 10–20 Å. **Prefer a REVERSIBLE-covalent handle** (cyanoacrylamide-type): an irreversible
  adduct makes the degrader stoichiometric and forfeits catalytic turnover, the property that makes PROTACs
  attractive. Electrophile promiscuity is an unresolved liability with no wet lab to check it, and must be
  reported alongside the parent warhead's MYC induction, not buried. *(C559 is unique and 12.8 Å out but buried
  at RSA 0.095 in this conformer — carried only as a candidate the MD-ensemble add-on could reopen.)*
- **(b) Transfer-zone lysine-identity term** — which lysine does the modelled E2~Ub transfer zone cover? Score
  *unique-only* highest, *unique + conserved* next, *conserved-only* lowest. This is set membership, not energy.
  Honest limit: real degraders often ubiquitinate several lysines and lysine-less substrates can still be
  degraded (N-terminal / Ser / Thr / Cys ubiquitination), so this **raises the odds; it does not guarantee** the
  paralogue is spared.
- **(c) E3 breadth, free at the search stage** — widen beyond VHL/CRBN to the ligandable set with public
  ligand-bound structures (cIAP1/BIRC2, DCAF1, DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2). Since basin search is
  CPU this costs ~nothing and multiplies the chance that *some* E3 surface complements NR4A3's differential
  surface. **Downselect to ≤2 recruiters before any GPU leg, and log what was dropped** — a silent top-N reads as
  "we covered everything". Availability is already answered and does **not** constrain the choice (RUNG 5a).
  **★ DONE 2026-07-25, $0 (CI run 30169233382, 2,919 fetched URLs — every field fetched, none recalled).**
  Staged, assessed and downselected: **CRBN (9CUO, 1.60 Å) + VHL (9GIO, 1.486 Å) advance**, with VHL explicitly a
  **backfill** for E3-choice sensitivity, *not* a co-winner — CRBN is the sole Pareto-front member and the
  CRBN−VHL margin is **0.033** in open solid angle on one conformer each, reported as a tie rather than a
  finding. All eight others are logged with reasons in
  [`e3-recruiter-staging.json`](../modalities/e3-recruiter-staging.json) → `downselect.dropped[]`, each
  carrying an explicit `availability_was_not_a_factor: true`; rationale in
  [e3-recruiter-downselect-2026-07-25.md](../modalities/e3-recruiter-downselect-2026-07-25.md). The rule
  was **preregistered before the fetch**: three gates (public ligand-bound structure ≤3.0 Å; ligand buried
  fraction ≥0.50; exit clearance ≥8 Å with 30° cone openness ≥0.30), then a Pareto front over analogue tier /
  exit quality / open solid angle, then a fixed lexicographic tiebreak — **no tunable scalar**.
  **★ THE FINDING THAT CHANGES HOW THIS ITEM READS: the binding constraint on E3 breadth is STRUCTURAL
  STAGEABILITY, not availability.** HPA says all eight widened arms are available; the **PDB says the panel is
  materially smaller**. **RNF114 has no deposited structure of the protein at all**; **DCAF16**'s ligand is only
  **34 % buried** once its partner is removed — a *glue interface, not a handle pocket* — despite having the
  panel's highest open solid angle (0.736); and **DCAF15** has no partner-free liganded structure, its "solved
  ternary" claim failing coordinate-level verification. **So the widening delivered less breadth than this
  plan's text implied, and it CONFIRMED the incumbents rather than displacing them — a real, publishable
  negative for the E3-breadth argument, and it must be reported as one rather than quietly absorbed.**
  ✅ **THE VHL ARM WAS RE-CHECKED AND IT HOLDS (2026-07-26, $0, CI run 30180602564).** The concern was that
  **9GIO** — the structure the downselect advanced VHL on — is titled *"…with a covalent compound bound to C77
  of VHL"*, which would mean its ligandability and exit-vector numbers described a **covalent Cys77 site** rather
  than the VH032-class **hydroxyproline pocket** every VHL PROTAC linker actually leaves from. **Both
  descriptions are true, of DIFFERENT ligands — and the staging used the right one.** 9GIO carries **two**:

  | ligand | hydroxyproline-pocket residues contacted | contacts Cys77? | nearest Cys77 Sγ |
  |---|---|---|---|
  | **`3JF`** — *the one the staging used* | **10** | **no** | **12.35 Å** |
  | `A1IMD` — the one the title describes | 1 | **yes** | **1.84 Å** |

  `3JF` is `N-acetyl-3-methyl-L-valyl-(4R)-4-hydroxy-N-[4-(4-methyl-1,3-thiazol…]` — the canonical VH032
  hydroxyproline + methylthiazole handle — sitting in the recruiter pocket, **12.35 Å away from Cys77**. The
  covalent compound is `A1IMD`, at **1.84 Å** from the Sγ, i.e. essentially exactly a C–S bond length. **So the
  E3 downselect's VHL row stands, and the attributed fpocket druggability of 0.001 was scored on the wrong
  ligand's site.** *(A useful side-validation: 1.84 Å is what a real covalent adduct measures — which is
  precisely the scale that makes the NR-V04 panel's 28–39 Å at C551 unambiguous rather than borderline.)*
  **BIRC2 is the flagged first recruiter to revisit** at $0 (tier-3 verified, best resolution 1.249 Å, openness
  within 0.04 of CRBN) if CRBN/VHL prove geometrically unpromising — it is already fully staged.
  ⚠ **The downselect is BLIND to recruiter-intrinsic pharmacology by construction.** MDM2 and KEAP1 rank well on
  geometry while their handles are developed inhibitors of the E3's *own* function. Recorded as a **required
  input to the next gate** — a recruiter must not be committed to on geometry alone.
- **(d) Pose-marginalisation, free** — run the basin search over the warhead-**pose ensemble** and carry only
  basins that persist, reporting the surviving fraction. Sequence-level uniqueness of C397/K572 is
  pose-independent; only the *reach* estimate is conditional, which is a far smaller conditional surface than the
  stage currently carries.

Five load-bearing pieces:

1. **A paralogue-differential surface atlas (free, CPU).** NR4A1/2/3 in a **matched** ensemble — homologous
   frames, identical pose hypotheses, protonation, target–E3 transforms, and sampling — mapping E3-reachable,
   solvent-exposed, divergent residues and lysines (LBD / hinge / DBD / fusion partner, separately). Output is a
   discrimination **map**, not three receptor models; states are explicit scenarios unless populations are
   defensibly estimable. **Done** (RUNG 4).
2. **Orientation-space search before real linkers.** For each ligase, sample many relative transforms of
   VHL/CRBN around the warhead-bound target under a flexible linker-reach restraint; keep only interfaces that are
   favorable on NR4A3 and systematically weaker/frustrated on NR4A1/2, bridgeable, clash-free, ensemble-compatible,
   and place an accessible lysine in a productive transfer region. Cluster into **~3–8 basins per ligase**.
3. **Wedges proven by a matched-pair causal cycle — the primary causal test.**
   **PRIMARY: the LIGAND-side double difference, on the lane Val B calibrates.** For a candidate *d* and a
   matched control *d₀* differing only in the element that engages the wedge,
   `S = ΔΔG_coop(d₀→d | NR4A3) − ΔΔG_coop(d₀→d | NR4A1)`. Each term is an ordinary relative alchemical quantity
   *inside one protein*; the difference asks the **design** question — does this structural element create
   paralogue discrimination? It needs **no protein-mutation engine**, makes **no cross-lane subtraction**, and by
   the cancellation identity (cost lever 2) needs **only ternary legs**. This is far stronger than observing
   ΔG_ternary,3 < ΔG_ternary,1.
   **CONFIRMATORY: the reciprocal PROTEIN-mutation cycle.** For a target-surface mutation *m*,
   `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` (the binary leg subtracts mutation effects from the
   target–warhead complex, isolating the recruited-interface effect). A strong wedge shows a favorable NR4A3
   interface, **loss** on NR4A3→NR4A1/2 mutations, **partial gain** on reciprocal NR4A1/2→NR4A3 mutations,
   persistence across frames, and a recognizable steric/electrostatic/H-bond mechanism. Its engine is built and
   its known-answer benchmark **passed 2026-07-25** (RUNG 5a-KS). ⚠ **BUT IT IS NOT AN INDEPENDENT SECOND
   LINE — corrected 2026-07-30, see [Open decisions 10](#open-decisions).** `ΔG_mut^ternary − ΔG_mut^binary`
   is a **ternary-minus-binary contrast, the same shape as the quantity valB_mini failed on**, and its
   benchmark passed on a *protein-mutation* quantity rather than on that shape. Retained as a second line —
   but the paper's headline causal result is not hostage to it. **ADOPTED 2026-07-24 (trimcrae go).**
4. **Separate ACCESSIBILITY from STABILITY.** Estimate `P(B_k | d, s)` (can the linker reach and hold basin *k*?)
   separately from `ΔG_coop(d, B_k, s)` (is the orientation plausible?). A favorable basin the linker rarely
   accesses is irrelevant.
5. **Robust constraint-satisfaction selection.** A candidate advances only if it satisfies preregistered
   constraints across a required fraction of scenarios (binary non-destabilization; basin populated in replicated
   MD; NR4A3 advantage over **both** paralogues under perturbation; ≥1 NR4A3-specific contact survives
   counterfactual mutation; ubiquitin near an accessible NR4A3 lysine in a meaningful CRL-conformer fraction;
   credible unstrained linker). Rank by `P_d = P(all constraints hold)`, robust to dropping any one favorable
   scenario — this kills the best-of-N winner's-curse artifact a raw Pareto set still admits.

### The hard kill-switch — tiered, cheapest-decisive-first

No causally-confirmed NR4A3 wedge ⇒ **STOP**: no linker matrix, no ensemble refinement, no flagship spend;
publish *"we mapped orientation space and no robust NR4A3-discriminating, ubiquitination-compatible basin
survives causal testing."* The *decision* to commit the flagship is cheap, not a gate on the whole tail.

> **★★ CRITICAL SEMANTICS, ADDED 2026-07-25 BEFORE 5a-KS EVER RUNS — A NULL AT TIER 3 DOES *NOT* STOP THE
> PROGRAM, AND THE ROW BELOW USED TO SAY IT DID.** Tier 2's GO was won on the **CATEGORICAL** basis: the
> paralogues have **no nucleophile at the aligned position**, so a covalent bond *cannot form* on them at all.
> But Tier 3's `S` is a **NON-COVALENT** double difference — it models no bond in either leg, so it can only
> ever see the **pre-covalent complex**. **It is therefore structurally incapable of testing the categorical
> mechanism.** What `S` tests is the **MARGINAL** (induced-interface, thermodynamic) wedge — the axis this file
> **previously** described as *"a confirmation tool operating near its limit, not a discovery tool"* — a
> characterisation that **no longer** stands and is **superseded** by measurement ([Appendix
> A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 53); §MECHANISM-FIRST carries the current reading and
> this box does not restate it.
> **So: `S` ≈ 0 ⇒ the MARGINAL wedge is absent, and the claim rests on the CATEGORICAL axis alone. STOP only if
> the categorical axis has ALSO failed.** Writing this down *before* the run is deliberate — a null is a
> **plausible** outcome for the recommended pair (its expected NR4A3 gain is bounded by roughly one partly
> buried H-bond, ~0.5–1.5 kcal/mol), and a pre-registered reading is the only thing
> that stops a predictable null being read after the fact as a verdict on the whole program.
>
> ⚠ **AMENDED 2026-07-30 8:21 PM ET — THE DECISION RULE ABOVE IS UNTOUCHED; ONE SUPPORTING FIGURE IT QUOTED IS
> SUPERSEDED, AND THE CHANGE MAKES A NULL *MORE* INFORMATIVE, NOT LESS.** The box was written against a
> best-case resolvable difference that was **assumed**, and against which the pair's own expected effect sat
> *below* resolution — so a null could not be told apart from a wedge the method simply could not see, and
> "likely" above was doing double duty for both. On the **measured** replicate SD the resolvable difference is
> the figure now carried in §MECHANISM-FIRST, and the pair's expected effect straddles it instead of sitting
> under it. **Consequence, and it is the whole reason this note exists: at an adequate replicate count a null
> now BOUNDS the marginal wedge rather than merely failing to find one** — which is what turns the pre-registered
> reading from an excuse into a result. It also makes the replicate count a *design* question rather than a
> formality; [§Open decisions 11](#open-decisions) is where that is settled. Nothing here loosens the STOP
> condition, and nothing here was changed after seeing an `S` — **no `S` has been computed.**

| tier | test | cost | status |
|---|---|---|---|
| **0** | **Categorical-axis screen.** No paralogue-unique nucleophile within tether range AND no paralogue-unique exposed lysine ⇒ selectivity must come from the marginal axis alone, which sits at the method's resolution limit ⇒ say so and expect a negative | **$0 CPU** | **PASSED — GO on both axes** (C397 at 10.9 Å exit-vector reach; K572/K518/K592 exposed). ⚠ **NARROWED 2026-07-26: "structurally incapable" holds AT THE ALIGNED POSITION only** — 16 of NR4A3's 20 cysteines are shared, each paralogue presents **two** inside the 12-atom gate (NR4A1 C465 at **6** atoms), and the axis survives on **exposure**, not absence. Reach-only collision is **0.000–0.003 at 12 atoms** and rises to **0.054–0.133 at 16** and **0.263–0.383 at 20** across the three matched scopes ⚠ *(superseded, retained: the pilot pair **0.081 at 16** / **0.258 at 20** over 5,657 static placements)*. See §MECHANISM-FIRST |
| **1** | **Differential surface atlas.** No E3-reachable divergent surface ⇒ STOP for free | **$0 CPU** | **PASSED** (46 handles) |
| **2** | **Basin nomination.** No basin exploits a categorical handle *and* none even nominally discriminates NR4A3 ⇒ STOP cheaply | **$0 realized** (budget was $0–50; **no GPU used**) | **✅ GO — CONFIRMED on the full 12-pose run** (CI 30169233690, 55 min, 3:11 PM ET). Basis **CATEGORICAL**. 58 meta-basins / 192 basins; **7** exploit term (a), **40** term (b), **28** nominally discriminating. See the block below |
| **3** | **Pilot ONE causal direction** — the ligand-side double difference `S`, one matched pair, ternary legs in NR4A3 and NR4A1. ⚠ **`S` is NON-COVALENT, so it tests the MARGINAL wedge only. No discrimination ⇒ the marginal wedge is absent and the claim rests on the CATEGORICAL axis alone — STOP only if the categorical axis has ALSO failed** (see the box above; a null is the *likely* outcome for the recommended pair) | **~$12 ($1.6–45)** | pending (RUNG 5a-KS) — **matched pair now DESIGNED**, see RUNG 5b |

Tier 2's asymmetry is what makes it usable: cheap scoring has poor S/N for a ~1 kcal/mol *energy* difference, so
it only **nominates** — but "does this basin place an electrophile at C397 / cover K572?" is a **geometric**
set-membership question, which cheap scoring answers reliably. A gross absence of signal is an informative
NO-GO; it is not trusted to kill a real small wedge.

### ★ Tier-2 result in full — the 12-pose run, at its CORRECTED exact-kernel values (LANE 2, 2026-07-25; reach correction 2026-07-26; **$0 realized — no GPU**)

**GO, basis CATEGORICAL — and "weakly" is part of the verdict, not a hedge to drop when quoting it.**

**★ THE FULL RUN CONFIRMED THE GATE AND CHANGED THE HEADLINE. Both must be reported.** The definitive run
(10⁶ placements × **12** poses × VHL+CRBN) gives **58 meta-basins / 192 basins**, of which **3** exploit
term (a), **40** term (b), and **28** discriminate nominally. Every figure below is the **corrected
exact-kernel** reading, i.e. post-2026-07-26 — ⚠ **this block carried the pre-correction table live for four
days, with its own correction stated 50 lines further down, and the manuscript copied the stale values out of
it. Superseded numbers are in [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 49 and are
NOT restated here.**

| meta-basin | poses | C397 reach (exact) | at-gate reach fraction | term (b) vs background | paralogue zones bare |
|---|---|---|---|---|---|
| `vhl|M2` | 6/12 = 0.50 | **10 atoms** (shortest) | **0.057** | 1.43×, exceeds | 0.008 |
| `vhl|M3` | 9/12 = 0.75 | 11 atoms | 0.021 | 1.4×, exceeds | **0.0** |
| `crbn|M17` | 3/12 = 0.25 | 12 atoms *(at the gate)* | 0.045 | **3.87×**, exceeds | — |
| **`crbn|M0`** ← strongest **nomination** | **11/12 = 0.92** | 13 atoms — **MISSES the gate by one** | **0.000** | **7.5×**, exceeds | 0.032 |
| `vhl|M14` | 3/12 = 0.25 | — | 0.000 | **does NOT exceed** | 0.0 |

**Three things this table says.**
1. **All 3 term-(a) basins reach C397 — and only C397.** Shortest reach per residue across the whole run is
   **C397 10 · C420 16 · C559 27**, so at a 12-atom gate the other two are not near-misses.
   **The categorical chemistry axis rests on a single residue.**
2. **★ THE STRONGEST BASIN AND THE GATE-CLEARING BASINS ARE NOT THE SAME BASINS, and that separation IS the
   result.** `crbn|M0` leads on pose persistence (0.92) and on the *lysine* term (7.5× over background, so it
   is not merely riding CRBN's null) — but under the exact kernel its shortest C397 requirement is **13**
   atoms, so it does not clear the electrophile gate at all. Tier 2 passes CATEGORICAL because `vhl|M2`,
   `vhl|M3` and `crbn|M17` clear it, **not** because the leading basin does. Anyone quoting `crbn|M0` as a
   term-(a) basin is quoting the superseded run.
3. **Reach fractions are 0.021–0.057**, i.e. an electrophile reaches C397 in only **2–6 %** of a basin's
   placements. This is the quantitative form of "weakly", and it is why the gate **nominates** rather than decides.

*Reconciliation note, checked rather than assumed:* `best_linker_atoms` reads **19** on every meta-basin while
the term-(a) gate is 12, which looks like a contradiction and is not — `best_linker_atoms` is the linker length
that best supports **basin accessibility** (`P(B_k | d, s)`), whereas the gate counts
`term_a_union[cys].max_fraction_reachable_at_gate`, whether an **electrophile** reaches that cysteine within 12
atoms. Two different quantities; the 3 reconciles exactly against the gate block.

Per arm, from the same definitive run (rows sum to the 58 / 3 / 40 above, which is how they are checked):

| | VHL *(Lane 1 staged it only as a **sensitivity control**)* | CRBN *(Pareto front)* |
|---|---|---|
| meta-basins | 28 | 30 |
| exploiting **term (a)** at the 12-atom gate | **2** (`vhl\|M2`, `vhl\|M3`) | **1** (`crbn\|M17`) |
| shortest C397 linker (exact) | **10 atoms** | 12 atoms |
| exploiting **term (b)** above the null | 21 | 19 |
| enrichment over null | 1.06–7.37× | 1.07–8.0× |
| null: covers *any* NR4A3 lysine | 0.31–0.48 | 0.77–0.95 |

- **The categorical terms fire in a small MINORITY of placements** — 0.5–8 % cover a unique lysine, term (a)
  reaches gate level in 2–6 % — against the gate's **unique-lysine null of 1.0–7.5 %** (`term_b_background_null.fraction_unique_covering`, 24 arm×pose nulls). **Enrichments, not saturation.** ⚠ *Do not pair one range with both terms — the reach control is a different quantity, and is zero in 184/192 basins.*
- ⚠ **RETRACTED SAME DAY (2026-07-25, LANE 7): "CRBN's null is 0.81–0.96, so most of CRBN's term-(b) signal is
  background — the discrimination lives on VHL."** That inference was wrong **twice over**, and it was recorded
  here earlier today, so it is corrected rather than quietly dropped.
  **(i) Wrong quantity.** 0.81–0.96 is the **any-lysine** null, whereas term (b)'s signal is an enrichment over
  the **unique-lysine** null. The conclusion was drawn from a different denominator than the one the gate uses.
  **(ii) The 0.81–0.96 is itself an EXIT-VECTOR ARTIFACT.** Restaged **assembly-native** (8R5H / 9UUM, every
  bridge **0.0 Å**) and re-run twice at identical settings, CRBN's any-lysine null **halves, 0.858 → 0.399**,
  while VHL's does not move (0.419 → 0.437). The change tracks the manipulated variable and nothing else —
  CRBN's exit vector moved **16.5 Å** between constructions, VHL's only **0.99 Å**.
  **What survives:** the **gate's actual denominator barely moves** (`fraction_unique_covering` 0.040 → 0.035 on
  CRBN, 0.027 → 0.026 on VHL), so **the Tier-2 GO and its published enrichments are UNAFFECTED**, and Tier-2
  passes CATEGORICAL on **both** constructions (native marginally stronger: 3 vs 2 term-(a), 26 vs 22
  discriminating). **What falls is only the claim that the discrimination lives on VHL.** Do not repeat it.
- ⚠ **Term (b)'s discrimination is a RARE JOINT EVENT, not paralogue lysine scarcity (Lane 13, $0).**
  P(the transfer zone covers *any* lysine) is **non-discriminating on the any-lysine measure**, consistent
  with the committed 0.0–0.032 *joint* statistic. The term earns its signal from the coincidence of covering
  a *unique* lysine while both paralogue zones stay bare, not from the paralogues having fewer lysines to
  hit. State it that way; the scarcity reading is wrong.
  ⚠ **LABELS ADDED 2026-08-02 — the triple this bullet used to quote MIXED THREE DIFFERENT ENSEMBLES.**
  It read *"**NR4A3 0.438 / NR4A1 0.387 / NR4A2 0.363**"*, in which **0.438 is NR4A3's pooled-unbiased
  MEDIAN over 75 conformers** while **0.387 and 0.363 are SINGLE static opened models** — three different
  objects presented as one comparison. (The lane doc's own table labels them correctly; this one-line
  restatement dropped the labels.) **No value is withdrawn — each is right for its own ensemble** — but a
  like-for-like triple is what this claim needs, and it is now measured and owned by
  [`selectivity-mechanism-options.json`](../modalities/selectivity-mechanism-options.json) → `measurements.M1`:
  **static 0.4035 / 0.3914 / 0.3650**, **pooled-unbiased 0.4396 / 0.4279 / 0.3692**, with the NR4A3−NR4A1
  gap at **+0.0118 against a replicate-SD of 0.0175** — under one SD. ✅ **The correction is CONSERVATIVE
  for this bullet's conclusion**: matching the ensembles makes the NR4A1 gap *smaller*, so
  "non-discriminating" is if anything understated and nothing downstream changes.
- **`term_b_best_rank` is a best-of-N statistic, inflated by construction** (exactly piece 5's winner's-curse
  artifact), so those counts are **upper bounds**; the unbiased mean fractions lead. One CRBN basin reached
  rank 4 while scoring *below* background and was correctly excluded — **without the null it would have counted.**
- **Shortest gate-clearing nomination `vhl|M2`:** 6/12 poses, C397 reachable at a **10-atom** linker (the
  shortest anywhere in the run), term-(b) enrichment 1.43× with a unique lysine covered and *both* paralogue
  zones bare at 0.008, and its interface patch (UniProt 390–412 + **572**) sits *around K572 itself*.
  **`vhl|M0` survives 5/12 poses** despite a **negative nominal Δ** — under mechanism-first that does not
  disqualify it, and **a scalar score would have hidden it**, which is the clearest vindication yet of
  dropping the tunable scalar; note it does **not** clear the electrophile gate (C397 at 19 atoms). ⚠ *The
  6-pose preview's "`vhl|M2` 5/6" and "`vhl|M0` 6/6 with C397 at 9 atoms" are superseded by the 12-pose run
  and must not be quoted ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 49).*
- **Pose-marginalisation on the 12-pose run:** top CRBN meta-basin **11/12 = 0.92** (`crbn|M0`); top VHL
  **9/12 = 0.75** (`vhl|M3`); the rest spread down to 0.25.
- **★ LINKER TRACTABILITY, ADDED BY RUNG 5b (2026-07-25) — and it does NOT invert the ranking, though a first
  pass said it did.** `min_linker_atoms` is a **best-of-N** over a basin's placements, and the member achieving
  it is **not** the published representative. Measured at the *representative*, C397 needs 14–25 atoms and
  `crbn|M0` looked the least buildable — an apparent inversion of the basin ranking. Re-run with the
  achieving placement emitted explicitly (`exemplar_placement`, $0, 71.6 min), the addition is **purely
  additive to the gate**: it reproduced the counts standing at the time exactly, and the electrophile term
  moved later and separately, in the reach correction below. Exact-kernel figures, at the search's own 3.0 Å
  pendant convention:

  | basin | C397 atoms, representative → exemplar | comfortable length |
  |---|---|---|
  | **`crbn\|M0`** | 33 → **13** | **~15 atoms** (1.1 kT) |
  | `vhl\|M3` | 23 → 11 | ~13–15 |
  | `vhl\|M2` | 16 → 10 | ~12–14 |

  **So the inversion was an artifact of comparing a best-of-N length against a typical placement** — correcting
  it leaves `crbn|M0` **comparable** to the others rather than an outlier. ⚠ It does **not** make it the most
  tractable, and the earlier reading "the strongest basin is among the MOST tractable" is withdrawn
  ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 49), along with the pre-correction
  25 → 11 / 14 → 11 / 15 → 10 row values. Both placements are emitted — exemplar (optimistic), representative
  (typical) — and **neither may be quoted without saying which, nor without its pendant convention**: at the
  longest pendant in the sweep `crbn|M0`'s representative reads 25 rather than 33.
- ✅ **CORRECTED 2026-07-26 (LANE 10) — the C397 reach figures are no longer lower bounds.** They previously
  were, by up to ~5 atoms: RUNG 5a's reach rule credited the pendant with shortening the **span**, which no
  pendant can do (all 576 records were audited and none was internally impossible, so it was a bound, not an
  error). The exact three-ball kernel has since replaced it and every figure was recomputed on the matched
  **10⁶** run. **The correction moved term (a) 7 → 3 and left term (b) 40 and the nominal limb 28
  bit-identical** — the values and the gate verdict are stated once, in the §WHERE WE ARE "the covalent design
  route clears the gate" block above. Quote them from there, not as bounds. ⚠ **This bullet sat 50 lines below
  a table still printing the pre-correction values, and the manuscript copied that table rather than this
  bullet** — a correction is not delivered until the live text above it stops disagreeing with it (rule 2).
  Both are now current; the superseded set is [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 49.
- ⚠ **`best_linker_atoms = 19` on 188/192 basins is the scan's LAST GRID POINT**, not an optimum. Do not read it
  as a converged optimum in either direction.
- **Exit vectors never let the linker run taut** — α = 33–100°, costing 1–3 backbone atoms of detour at minimum.
- **Term (b) is NOT EVALUABLE for BIRC2/MDM2** — their ligandable structures are 15 %/19 % fragments lacking the
  RING. This agrees with Lane 1's CRBN+VHL answer by a different route, and argues for adding
  **ubiquitination-geometry evaluability as an explicit Pareto axis** rather than discovering it downstream.
- **MM-GBSA rescore: NOT run, and recommended against** — it would refine the very axis the mechanism-first
  reframe demoted. **Next spend should be 5a-KS.**
- **✅ RESOLVED 2026-07-25 (LANE 7) — registry A (5T35) is CORRECT, and the Tier-2 result rests on it.** The
  discriminating observation nobody had run: **8R5H** is a solved, *intact* CRL2^VHL ubiquitylation assembly
  holding VHL·EloB·EloC, MZ1 **and** a trapped UBE2R2~Ub **in one frame** — so the disputed distance is
  measurable with **no bridge, no composition, no model**. **Ground truth: exit atom `759.CAE` → UBE2R2
  catalytic Cys93 = 30.76 Å.** Registry A reproduces it at **30.85 Å (miss 0.09 Å)**; registry B (6GMN) gives
  **69.91 Å (miss 39.15 Å)**. Decomposed: Δ mapped E2 cysteine **0.02 Å**, Δ exit vector **50.67 Å** — so the
  disagreement is entirely in the *exit vector*, not the anchor.
  **Root cause, read off the structure:** 6GMN's chosen "recruiter ligand" (F4E) has a 4.5 Å lining of **eight
  Elongin C residues and ZERO VHL residues**, 6.87 Å from the nearest VHL atom. `pick_ligand` tested contact
  against the receptor **body** (recruiter + obligate partners) and **never against the recruiter itself**.
  Fixed and unit-tested; **verified bit-identical** on both consumed arms (5T35 MZ1 2.57 Å, 6BOY dBET6 2.69 Å).
  **⚠ And the tempting explanation was FALSIFIED:** this is **not** a second instance of the 48.6 Å composed-RING
  spread — 8R5H is single-copy and the mapped E2 cysteine agrees to 0.02 Å. **The numeric similarity to 48.6 Å
  was coincidence.** *(Consequence: the feared "~40 Å of transfer-zone variation would weaken term (b) further"
  does not exist, and the VHL basin ranking is unchanged.)*

---

## 10 · THE ROADMAP — one ordered list

**This is the union.** Until this merge, this page's critical path and the ladder's decision-value ranking
**shared zero items**, and neither document contained both. Reconciling them so one document holds the union
was named as *"the single highest-value merge action"*; this section is it.

⛔ **NOTHING ON THIS LIST IS RUNNING.** Not one row is ◐. Evidence, all $0 and all re-checkable:
`inflight-board-all.md` prints `IN-FLIGHT BOARD: no GPU legs.` for all four Vast lanes;
`ternary-vast-account-census.json` reports `n_instances: 0`; `vast-account-reaper.json` returns
`NOTHING-TO-REAP`; the SageMaker account shows 0 in-progress jobs and 0 of 8 spot instances.

⛔ **AND NO PRICE IS RETYPED HERE** (invariant 6). The **price** column says what *kind* of number exists —
**priced** (a figure lives in the plan or the ladder), **PROJECTED** (an estimate deliberately excluded from
the pinned total, per spending rule 4), or **unpriced** (⛔ *no figure exists anywhere*). Follow the link for
the figure.

### 10.1 · Open rows, ordered by what unblocks the most

| # | item | serves | state | auth | price | next action — and what it settles |
|---|---|---|---|---|---|---|
| **1** | **Rebuild the ternaries by the assembly route**, from a molecule whose structure is recorded this time — now **RUNG `5b-T`** in [the ordered plan](#the-ordered-plan-spend-gated--read-top-to-bottom-for-whats-next) | `R9` → `R10` `R11` `R12` | ○ **not started** | **—** ($0, needs no nod) | ✅ **PRICED and GATED, 2026-08-02.** **$0** — DERIVED, not typed: it buys **0.0 reference GPU-h**, so the pinned ladder total is unmoved ([`ternary-rebuild-cost.json`](../modalities/ternary-rebuild-cost.json), regenerated by `ternary_rebuild_cost.py --check`) | **RUN IT — it needs no authorization, and the row-25 hold is DISCHARGED.** ✅ The canonical-library question is settled and **`5b-T` is invariant to which way it went**: its four named degrader candidates are present with **identical SMILES** in BOTH the executed and the corrected enumerations, and `shortest_committed_backbone_atoms` is 14 in both, so no re-derivation changes this rung's inputs ([`nr4a3-linker-library-canonical.json`](../modalities/nr4a3-linker-library-canonical.json) → `release_condition`). Rung `5b-T` carries the spec (5 arms: 2 harness controls incl. a **CRBN** one, 3 paralogues, 16 seeds each, degrader SMILES taken from the recorded library), the pre-flight snap-mask assertion, and a **pre-registered three-arm GO/NO-GO** (sequence-encoded · ≥12 of 16 vs ≤4 of 16, binomial *p* = 0.0384 each tail · tether geometry preserved). ⚠ **Superseded, retained:** *"unpriced — no rung, no gate, no spine row … GIVE IT A RUNG, A GATE AND A PRICE — that is the next action, not running it."* |
| **2** | **`V4` — the CREBBP/BRD4 selectivity known-answer test** | `R7` | ○ not started | 🔒 **not authorized** | ⛔ **unpriced — no rung.** It appears in the ordered plan **nowhere**; only in the gate scoreboard's standing tally and Appendix A 64 | an authorization decision **and** a rung. It settles the **instrument**, not the claim: a **binary** control that would **not** discharge the paralogue statement |
| **3** | **The frame-level generation-receptor dependency audit** | `R3` | ✓ **complete 2026-08-03 — and the gate FAILS** | — | **$0 (realized)** | ⛔ **ANSWERED, AGAINST THE PROGRAM.** The generation frame is named (unbiased release rep 0, frame 95) and scored under the harmonized, score-independent site definition: the mapped orthosteric site **is detected** and is **not druggable** — `GATE_A_FAIL_BELOW_DSTAR`. Per the paper's own sentence this **reaches the generation receptor itself, not merely a reported frame-fraction**. ⚠ The verdict is **rule-sensitive and says so** (two cavities clear the composite gate; the score-independent rule prefers the better-matching, less druggable one) — the thresholds were frozen 2026-07-11, before this datum. One home for every number: [`r3-generation-frame-harmonized.json`](../modalities/r3-generation-frame-harmonized.json); identity + coverage proof: [`r3-generation-frame-audit.json`](../modalities/r3-generation-frame-audit.json); reasoning: [three-row-audit-2026-08-03.md](three-row-audit-2026-08-03.md). ⚠ **Superseded, retained:** *"○ future · $0-to-cheap · the cheapest open item in the program"* |
| **4** | **Re-run the pose known-answer test with SITE and DOCKING separated** | `V3` → `R5` | ○ (the test ✓ ran, INCONCLUSIVE) | — | cheap CPU/CI | `R5`, and every anchor Route B's geometry depends on. The docking is fine; the pipeline's **site selection** missed on 6 of 6 pairs, so the primary arm measured the site |
| **5** | ✅ **Reconcile branch 1b's prose to its landed artifact — DONE 2026-08-03** | `R8` | ✓ | — | **$0** | lifts *"do not quote branch 1b anywhere"*. The artifact landed at `dc0befd9c`; at least one stated residue disagrees with it ([§7](#branch-1b--computed-not-reconciled-to-its-artifact)) |
| **6** | **Run the pose diagnostic `task=triangle-converge`** | `V5` | ✓ **complete 2026-08-03** | — | **$0 (realized — 5 min 45 s on `ubuntu-latest`)** | ✅ **RAN, and the pre-registered prediction is UPHELD.** The triangle's two BINARY legs carry the departure (**10 of 12** and **8 of 12** replicas ending beyond 4.0 Å); both ternary arms are clean (**1 of 12**, **0 of 12**). Departure **PRESENT** → by the workflow's own frozen reading the non-zero `R_binary` is **attributable to it**; `valb_triangle_closure.binary_departure_prereg` returns **`BINARY_PATH_DEPENDENT`, `prediction_upheld: true`**. **This discharges LANE 20's hold** ([§6c](#6c--held--not-refuted-not-parked-waiting-on-a-decision)). Numbers: GH run `30775278345`; reasoning [three-row-audit-2026-08-03.md](three-row-audit-2026-08-03.md) |
| **7** | **Classify Arm F — held, or explicitly retired** | `R11` | ○ **decision — and it is the ONLY thing outstanding** | 🔒 decision, no spend | **$0** | ⚠ **THE WORK STATE IS ALREADY CLASSIFIED and this row must stop implying otherwise: [§6b](#6b--parked--failed-with-todays-tools-with-a-named-trigger-to-reopen) files Arm F ⏸ **parked** with its reopening trigger named, and ✕ is refused on evidence** (nothing shows ΔΔG_coop cannot be computed; a gate that cannot fire is a fact about the **gate**). Per [§0.3](#03--three-orthogonal-axes--work-state-authorization-sufficiency) what is outstanding is the **decision** axis, not the work state — Arm E got a ruling ([Open decision 12](#open-decisions)), Arm F never did. ⭑ **AND THE TRIGGER HAS NO RUNG, NO GATE AND NO PRICE:** Arm F needs a **ΔΔG_coop** calibrator, while row 11 calibrates the **`S`-shaped** quantity — a different one ([Open decision 9](#open-decisions): *"valB_mini calibrated `ΔΔG_coop`, a quantity `S` does not contain"*). Its structural feasibility is already measured at $0 and is favourable ([`s-calibrator-survey.json`](../modalities/s-calibrator-survey.json): 8G1P puts a real structure on the arm the repo homology-substitutes). Reasoning: [three-row-audit-2026-08-03.md](three-row-audit-2026-08-03.md) |
| **8** | **Ask for the two-branch template design decision** | `R15` | ○ **decision** | 🔒 decision, no spend | **$0** | the only architecture that can carry the covalent electrophile **and** the causal wedge. It is a design change to a preregistered enumeration and **has never been put to trimcrae** |
| **9** | **`R13` — the EWSR1::NR4A3 fusion-context object** — now rung **`R13-a`/`R13-b`** in [the ordered plan](#rung-s--the-two-scope-rungs-r13-r14-claim-ceiling-conditions-deliberately-off-the-cum-chain) | `R13` | ○ **not started** | **`R13-a`: —** ($0, needs no nod) · **`R13-b`: 🔒** | ✅ **PRICED and GATED, 2026-08-03.** `R13-a` **$0**; `R13-b` **~$0.66** ($0.28–1.67, 5.81 ref-GPU-h) — DERIVED, not typed, off a **completed 12-model co-fold panel's own billed ledger** ([`scope-rung-cost.json`](../modalities/scope-rung-cost.json), `scope_rung_cost.py --check`). **Excluded from the pinned ladder total**, like pricing.md §C's confirmatory wedge | **RUN `R13-a` — it needs no authorization.** ⚠ **Price the CORRECTED object:** a breakpoint **off-by-two was fixed at source** — NR4A3's first two transcript exons are non-coding, so all **7** committed junctions deleted the AF1 and the first zinc finger; the corrected junction is **EWSR1 exon 7 → residue 264 :: NR4A3 exon 3 → residue 1** ([`nr4a3-exon-audit.json`](../modalities/nr4a3-exon-audit.json)). ⛔ What is **still unpriceable** is validation requirement 5's *full* object (fusion-context + CRL/E2~Ub ensembles): no particle count exists for an ~890-residue chimera with a 264-residue IDR, no replica count is determined for a disordered region, and **the patient-level breakpoint is not pinned**, so the object itself is not yet uniquely defined. ⚠ *Superseded, retained: "⛔ unpriced — on no plan, spine or ranked list."* |
| **10** | **`R14` — the AR/MR superfamily cross-binding check** — now rung **`R14-a`/`R14-b`**, with **`R14-c` closed on the claim-ceiling rule**, in [the ordered plan](#rung-s--the-two-scope-rungs-r13-r14-claim-ceiling-conditions-deliberately-off-the-cum-chain) | `R14` | ○ **not started** | **`R14-a`: —** ($0, needs no nod) · **`R14-b`: 🔒 + ⛔ blocked by the rate line** | ✅ **PRICED and GATED, 2026-08-03.** `R14-a` **$0**; `R14-b` **~$3.41** ($1.10–18.65, 29.87 ref-GPU-h, band 23.2–64.7) — DERIVED from the MEASURED LANE-13 metadynamics rates, not from the card table ([`scope-rung-cost.json`](../modalities/scope-rung-cost.json)). **Excluded from the pinned ladder total** | ⭑ **`R14-a` IS AN ASSEMBLY JOB, NOT A BUILD, AND IT IS THE HIGHER-VALUE HALF** — the screen ran, the harness ran at scale, AR is already a panel target; only MR/NR3C2 is missing, and the panel's **cognate-ligand self-control has never been run.** That control runs FIRST, and **until it passes no anti-target margin from this panel may be read — including the one SI §S1 already publishes.** ⛔ `R14-b` is **registered as blocked**: its `$0.022758/ns` is **3.48× the approved buy line**, but the comparison is *not* like-for-like (a biased leg against an unbiased benchmark), and **no metadynamics-anchored basis exists** — a decision for trimcrae, surfaced now rather than at launch. `R14-c` (the FEP half) is **not costed**: it is `V4`'s instrument, so it is downstream of row 2, not parallel to it |
| **11** | **A known-answer calibrator for the `S`-shaped quantity** | `V16` → `R11` | ○ future | 🔒 | ⛔ **unpriced** (the ladder's own rank 9 says so) | it lets the flagship causal result be reported as *calibrated* rather than only as a bound. Must obey [Open decision 9b](#open-decisions): **reference data and structure on the SAME protein** |
| **12** | **A wedge-sized known-answer benchmark for `V10`** — `barnase_barstar_W35F` | `V10` → `R7` | ○ future | ⛔ **no authorization is outstanding — the SMARCA2/4 application it was authorized for is CLOSED ON EVIDENCE** (`STOP_NO_REFERENCE`) | **priced** in `pricing.md` | ⛔ **Superseded, retained:** this row read *"pmx/GROMACS interface point-mutation ΔΔG · 🔓 AUTHORIZED, behind its $0 primary-source precheck"*. **The precheck ran and refused it**: no measured interface mutational ΔΔG exists for the Gln1469 contact, so there is no known answer to score against. What remains is the *engine* question — whether `V10` resolves a ~1 kcal/mol interface effect at all. The candidate is CI-verified to stage and held out of the qualification set so it cannot flip the engine's verdict without a measurement. ⚠ It is **not** a selectivity control and involves no paralogue |
| **13** | **Replicates on the open cycle** (3 of the 18 fan-out edges) | `V6` → `R7` | ○ future | 🔒 market gate | **priced** in the plan | attributes or dissolves `cycle_3carbonyl`'s **R = +1.307** violation, and gives the binary lane its first replicate SD |
| **14** | **The generative arm of the generation-matched null** | `V19` → `R7` `R15` | ○ future | 🔒 | **PROJECTED**, excluded from the pinned total | the outstanding control on `denovo_401`'s selectivity. The arm that ran addresses the *selection* step; this one addresses the **generative** step |
| **15** | **Matched 8XTT-anchored / crystal-seeded paralogue ABFE legs** | `R7` | ○ future | 🔒 | ⛔ **unpriced** | the paper's **twice-named "decisive follow-up"** (`:1299–1301`, `:2520–2522`): the NR4A3 leg is done in triplicate (+8.17 ± 0.98) but the **matched NR4A1 and NR4A2 legs are not**, so the *selectivity contrast* does not yet exist |
| **16** | **`dg_open_paralogue` — ΔG_open per paralogue** | `R6` → `R7` | ○ future | 🔒 **explicit nod only** | **priced** (OPTIONAL/HELD tier) | whether the binder margin **survives, narrows or reverses**. Nothing else can answer that. If NOT run: report everything conditional on the open state — $0 and fully defensible |
| **17** | **`abfe_conditional` + the λ-overlap repair** | `V9` → `R7` | ○ · ⏸ **as framed** | 🔒 **explicit nod only** | **priced** (OPTIONAL/HELD tier) | sharper error bars on the existing ABFE block. ⛔ Even with a nod the framing must change first, and validation requirement 3's three preconditions are **all unmet** |
| **18** | **≥3 ternary models per paralogue, then `V1`** | `R11` | ○ future | — | ✅ **PRICED — it is the second half of row 1's rung `5b-T`, at $0** | `R11`'s reproducibility bar — currently **1 model per arm against a bar of 3**. `5b-T` reads **all 16** models per arm, which clears the bar five times over and costs seconds of free CPU, and its gate arm (B) turns the bar into a threshold with a stated null instead of a word. ⚠ **Superseded, retained:** *"— (gated on row 1) · unpriced."* |
| **19** | **`valB_full` — the component-calibration cube** | `V5` → `R11` | ○ future | 🔒 ⛔ **its gate cannot fire** | **priced** in the plan | ⛔ **the single largest structural block in the program.** Its module 1 failed and [Open decision 9](#open-decisions) declined to amend or decouple, so **the entire prospective tail (rows 21–22) sits behind a gate that cannot fire.** What it needs is a ternary free-energy method that passes `V5` — not more sampling |
| **20** | **Does anything bind the opened pocket?** | `R4` | ○ future | — | **needs a bench** | the only item that can invalidate the whole non-covalent path — everything above assumes a yes. ⚠ Scoped to the **cryptic pocket**: NR4A3 is already experimentally ligandable |
| **21** | **5c — explicit ternary-ensemble refinement** | `R12` | ○ future | 🔒 (behind row 19) | **priced** | which lysine the ubiquitin actually reaches, per construct, as a distribution over unique-vs-conserved sites |
| **22** | **5d — local ternary FEP** → the final candidate set | `R15` | ○ future | 🔒 (behind rows 19, 21) | **priced** | the prioritized, structure-defined, retrosynthetically annotated candidate set with an identified causal mechanism — degradation experimentally unvalidated |
| **23** | **RUNG 6 — fold results into the paper · final red-team · post & submit** | all | ○ future | **outward-facing — needs trimcrae sign-off** | **$0** | the deliverable |
| **24** | **The steric-exclusion DESIGN RULE** (`S3`) — measurement → design rule, with its control attached | `R7` `R15` | ✅ **work complete 2026-08-03** — claim **capped by its own control, see the last cell** | **—** ($0, no nod) | **$0 · realized $0, no GPU** | ✅ **BUILT: [`steric-design-rule.json`](../modalities/steric-design-rule.json)** (`steric_design_rule.py --check`). It carries two substituent **vectors**, a shape spec and a per-candidate **scorer** that reproduces `M3`'s own 0.923-vs-0.173 over `M3`'s own poses. ★ **Three things the measurement could not show.** (1) **The rule has TWO usable vectors, not three** — only **I484→Tyr/Tyr** (51.9 Å³, reach 4.27 Å) and **L534→Phe/Phe** (60.7 Å³, reach 5.62 Å) clear the bar; **L406→His/His fires on clash but offers 2.69 Å³**, because the space both paralogues deny there is denied by NR4A3 too. (2) **The bar is MEASURED, not chosen** — it is the null class's own largest lobe (**11.78 Å³ at the conserved R481**), which is *larger than L406's*, so on the volume axis too: grade the contrast, never the signal. (3) **The biggest lobe of all (68.8 Å³, R412) must NOT be the top target** — it is `unique_not_bulkier`, fires at 0.000 on the clash test, and carries the worst post-fit deviation in the set, so **volume never overrides class.** ⛔ **THE CONTROL IS ON EVERY RECORD, AND IT CAPS THE CLAIM:** the paralogue's own docking **RELOCATES** these molecules (median **5.31 / 5.26 Å**), so a score means ***"this POSE is denied in the paralogue"* — NEVER *"the paralogue cannot bind this molecule"***. Rigid transfer (side chains could rotate away); NR4A3's absence of clash is **guaranteed by construction** and carries no information. ⚠ Remaining: route the rule into [§8 Route A](#route-a--a-warhead-engaging-paralogue-divergent-pocket-handles---blocked-nothing-running--serves-r7) — a section this pass does not own |
| **25** | ✅ **SETTLED 2026-08-03 — which linker library is CANONICAL — the committed one no longer reproduces from its own generator, and the drift reaches the CAUSAL TEST ARTICLE** | `R15` → `V16`, rung `5b-T` | ○ **decision + $0** | **—** | **$0** | ✅ **RULED, with a controlled A/B: BOTH are canonical, for different jobs.** The committed artifact is **FROZEN as the EXECUTED enumeration** (it is what `V16` was measured on, it is referenced by construct id by `nr4a3-linker-library-chem.json` and rung `5b-T`, and it is fully reproducible — HEAD's generator plus `linker_design.py` at `864a9518f` reproduces it with ZERO structural differences); the **corrected kernel is canonical for all NEW design work** and its enumeration is REGISTERED, not written over the committed one. **Cause, established by A/B and not by reading commit messages:** `382c36947` (2026-08-02 4:24 PM ET) replaced `linker_design.three_ball_min_margin`'s compass search with an exact closed-form solver — 0 mismatches over 160,962 cells against 92 false-disjoint in 118,708 — so the drift is a **one-sided, conservative** correction that ADMITS constructs rather than refuting them. ⛔ **The miss was registration, not geometry:** that commit named `nr4a3-orientation-basins.json`'s `term_a_feasibility_envelope` as built on the old kernel and NOT regenerated, but did not name `nr4a3-linker-design.json`, a second consumer of the same kernel — **and the basins artifact is still unregistered, so that half is open.** Every count, the two registered construct sets, the anti-drift guard and the `5b-T` release predicate: [`nr4a3-linker-library-canonical.json`](../modalities/nr4a3-linker-library-canonical.json) | Re-running the generator today returns a different construct set *and a different recommended 5a-KS matched pair* (a different linker class, a different backbone length, a different SMILES) from the pair `V16` was actually measured on. ✅ **`V16`'s own molecule is NOT lost** — its endpoint SMILES are committed in [`nr4a3-5aks-cofold-prep.json`](../modalities/nr4a3-5aks-cofold-prep.json) and match the committed library, so this is **not** the unregenerable-artifact failure of [§6a](#6a--dead--conclusively-unworkable-never-retry). ⛔ What is broken is that **anyone re-deriving the test article from the code gets a different molecule**, silently — and `5b-T`'s degrader SMILES come down the same chain. Decide: freeze the artifact with a provenance note, or regenerate and re-declare. Evidence: [`nr4a3-short-linker-probe.json`](../modalities/nr4a3-short-linker-probe.json) → `flagged_not_fixed` |
| **26** | **Bound the NR4A2 half of the selectivity requirement** — MGI single-KO phenotypes for *Nr4a1/2/3*, and HPA per-tissue nTPM | `R7` ([§2.4](#24--the-selectivity-requirement-is-asymmetric--and-this-page-stated-it-symmetrically)) | ○ future | **—** ($0, networked → CI) | **$0** | the *only* thing that would bound the unbounded half of the requirement without a bench. IMPC returned nothing for any of the three, MGI is the named remaining source, and the per-tissue nTPM field is `null` today. ⚠ A null result here is as useful as a positive: it converts *"unbounded"* from an unanswered question into a measured absence |
| **27** | **The two $0 searches for a paralogue-scale known answer for the ligand-side ΔΔΔG** | `V6`-adjacent → `R11` | ○ future | **—** ($0) | **$0** | decides whether the program's cheapest well-posed selectivity instrument can be *bought a known answer at the right size*. ⛔ It does not raise any ceiling by itself — a `ΔΔΔG` route needs its **own** validation and inherits none ([§3.4 fact 3](#34--three-instrument-facts-this-page-used-to-be-missing)). A `STOP_NO_REFERENCE` is a good outcome and not a failure |
| **28** | ⛔ **Rule on `nr4a3-orientation-basins.json`'s `term_a_feasibility_envelope`, the OTHER artifact built on the pre-fix 3-ball solver** | `R15` → rung `5b`, and it is an INPUT to the linker library | ○ **decision + $0** | **—** | **$0** | the sibling of row 25 and it did NOT come with it. `382c36947` named this field as built on the wrong kernel and explicitly did not regenerate it; the bias is the same one-sided, conservative under-claim, so nothing here is wrong in the dangerous direction — but `shortest_linker_with_any_feasible_anchor` is quoted downstream and no guard would notice if it moved. Same three outcomes as row 25: freeze with a provenance note, regenerate and re-declare, or register the divergence. Evidence and the worked precedent: [`nr4a3-linker-library-canonical.json`](../modalities/nr4a3-linker-library-canonical.json) |

### 10.2 · The readout — derived from the column, not typed

- **0 of 27 open rows are moving, and 3 of the 27 are now RESOLVED (rows 3, 6, 24).** ⚠ Count DERIVED from §10.1's state column on 2026-08-03, not typed — rows 3 and 6 resolved that day. Row 3 resolved **against** the program: the submission gate FAILS. Not one is ◐, and four independent
  $0 reads say nothing is billing.
  ⚠ *Superseded, retained: "0 of 23" — rows 24–27 were added 2026-08-03 from the options-register fan-out
  ([§0.8](#08--the-six-options-registers--what-they-own-and-the-one-thing-they-may-never-do)).*
- **10 rows wait on a money decision** (🔒 spend): 2, 9, 10, 11, 13, 14, 15, 16, 17, 19 — **unchanged by the
  four additions, every one of which is $0 and needs no nod.** ⚠ **But 9 and 10 are on this list for LESS of
  themselves than they were (2026-08-03):** each is now two rungs, and only the paid tier (`R13-b`, `R14-b`)
  waits on a nod — the `$0` tiers `R13-a` and `R14-a` are startable today, which is why they also appear on
  the no-authorization list below. A row can be on both lists, and pretending otherwise is how the free half
  of a blocked-looking item stays invisible. ⚠ **Superseded,
  retained:** *"11 rows … 1, 2, 9, …"* — **row 1 left this list on 2026-08-02**, not because anything was
  authorized but because pricing it showed there was **nothing to authorize**: the assembly route runs on CPU,
  so the largest open gap in the program turned out to cost **$0**.
- **2 rows wait on a decision that costs nothing at all** (7, 8) ⚠ *Superseded, retained: "3 rows … (7, 8, 25)" — **row 25 was ruled on 2026-08-03**, and the ruling is the reason it left this list, not a deferral.* — and one of those, the two-branch
  template, **has never been put to trimcrae in the first place.** ⚠ *Superseded, retained: "2 rows … (7, 8)".*
  ⭑ **Row 25 is the one to take first of the three**: it is the only one that gets *more expensive* by
  waiting, because rung `5b-T` consumes the artifact it is about.
- ⛔ **0 rows are authorized.** Row 12 was, until its **$0 precheck ran and refused it on evidence** — which
  is a better outcome than a budget hold, because it cannot be reversed by a nod. ⚠ **Superseded, retained:**
  *"1 row is authorized (12), behind a $0 precheck."*
- ⛔ **3 rows have no rung, no gate and no price anywhere in the program** — rows **2, 11, 15** — and for all
  three **the next action is the same $0 act: give it a rung, a gate and a price.** One of the three is the
  program's *highest-leverage unrun item* (row 2). ⚠ **Superseded, retained:** *"5 rows … 2, 9, 10, 11, 15"*,
  and before it *"6 rows … 1, 2, 9, 10, 11, 15 … Two of the six are the program's largest open gap (row 1) and
  its highest-leverage unrun item (row 2)."* Row 1 was priced and gated on 2026-08-02 (rung `5b-T`), and
  **rows 9 and 10 on 2026-08-03** (rung `S`) — row 18 and the `R13`/`R14` rows point at their rungs rather
  than restating them.
  ⭑ **And pricing rows 9 and 10 changed what they ARE, which is the argument for doing this to the other
  three.** Each split into a **$0 tier that needs no nod** and a paid tier — so *"🔒 unpriced"* was hiding
  free work in both cases; `R14-a` in particular is an **assembly job on parts that already exist**, and its
  never-run self-control can reach a result the paper already publishes. Neither of those is visible from a
  row that says *"give it a price"*.
- **10 rows could start today with no authorization and no bench** — **1**, 5, **9 (`R13-a`),
  10 (`R14-a`), 25, 26, 27** at **$0**, 4 cheap, and 18 is the same purchase as 1 — plus row **24**, which
  **was** on this list and is now **done**. ⚠ **Superseded, retained:** *"10 rows … **1**, 3, 5, 6, **24, 25,
  26, 27** at $0, 4 cheap, and 18 …"*, before it *"6 rows … 1, 3, 5, 6 at $0, 4 cheap, and 18 …"*, and before
  that *"4 rows … 3, 5, 6 at $0, and 4 cheap."* ⭑ **Row 1 is
  now the largest of them**: the program's biggest open gap is a $0 CPU job that nobody has to be asked about.
  ⚠ **And the shape of the backlog changed with the four additions, which is the point of counting it:**
  **the free, unauthorized, no-bench tier is now the LARGEST tier on this list** — larger than the money-gated
  one. A program that reads as *"blocked on spend"* is, on its own board, mostly blocked on nobody having
  done the free thing.
- **1 row cannot be bought at all** (20 — it needs a wet lab), and **1 is blocked by a gate that cannot fire**
  (19), which in turn holds 21 and 22.

⚠ **Superseded, retained:** *"Four of the six are moving or done; the two ○ rows are gated on something else …
**There is no row here waiting on a decision.**"* Every clause failed. It was a consequence of the list being
six rows long, not of the backlog being clear.

⚠ **And the second superseded summary, from the eleven-row version:** *"zero are moving. One is done, with two
qualifications. Nine are ○ future. And five of them are waiting on … a decision about money."* True of that
list; the union is 23 rows and 11 wait on money.

### 10.3 · What taking the union changed

| | before | after |
|---|---|---|
| this page's critical path | 11 rows | folded in |
| the ladder's decision-value ranking | 9 ranks + 1 exclusion | folded in; ranks 1–3 and 6 are ✅ done, 4 and 5 have **landed** since it was written |
| items on **neither** list | — | **8 added**: `R3` (row 3), branch-1b reconciliation (5), the $0 pose diagnostic (6), Arm F's classification (7), the two-branch decision (8), `R13` (9), `valB_full`'s unfireable gate (19), and `V4`'s missing rung (2) |
| rows with no price anywhere | not visible — they were prose | **6, and each is now a named $0 next action**. ⚠ **3 of the 6 have since been priced** — row 1 (`5b-T`, 2026-08-02) and rows 9/10 (rung `S`, 2026-08-03); **3 remain** (2, 11, 15) |
| items on **no list at all**, because nobody had enumerated the options (2026-08-03) | — | **4 added**, all $0 and none needing a nod: the steric-exclusion design rule (24), the linker-library provenance decision (25), bounding the NR4A2 half (26), and the ΔΔΔG benchmark searches (27). ⛔ **Every one came from an OPTIONS register rather than from a caveat**, which is a different failure from §10.3's original one: §10.3 fixed *"a caveat with nowhere to go"*; these were **never written down anywhere**, because a shortlist cannot show what was never considered |

★ **The pattern behind all eight additions is one sentence, and [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) is its home:
*"A caveat with nowhere to go is how work gets silently dropped."*** Every added row existed as prose in a
deliverable table, a paper caveat, an audit finding or a preregistration condition, with no rung, no gate and
no price. That is not a filing problem — an item with no rung cannot be scheduled, refused, or costed, so it
is invisible to every mechanism the program uses to decide anything.

---

## THE ORDERED PLAN (spend-gated) — read top-to-bottom for "what's next"

*★ **THE ITEM LAYER, AND THE MOST FRAGILE OBJECT IN THE REPO.** ⚠ **Parsed by [`work_ledger.scan_plan_items`](../modalities/work_ledger.py)** on this heading string, the bullet regex and the `###` rung sub-headings; the skipped marker is an **en dash**, not a hyphen, and the scan ends at the next `##`. Renaming the heading makes the plan invisible with no error; reformatting a bullet makes an open item vanish from the work board. [`degrader-paper-schedule.json`](degrader-paper-schedule.json) is its declared one-for-one machine mirror. [§10](#10--the-roadmap--one-ordered-list) is the ordered view over this layer and never restates a price.*

Legend: `[ ]` pending · `[~]` in progress · `[x]` done · `[–]` skipped · `[!]` result under correction.
**Price** = spot $ for that step on Vast 4090; **Cum.** = running total if GO at every gate to here (mid-range).

### RUNG 0 — free / already done (~$0)

- **`[x]` Charge-model fix — am1bcc on the BINARY path** — **$0.** Added `ambertools>=23` +
  `partial_charge_method="am1bcc"`; the **binary RBFE lane** is on the documented reference method → cite OpenFE.
  The ternary and endpoint-MD lanes run NAGL — a *lane split*, not a shared charge model (see §Val A above).
- **`[x]` Step 0 — RBFE infra shakeout** — **~$1–2 · PASSED.** One OpenFE edge ran end-to-end via the spot-safe
  split and returned a converged **ΔG_morph = −48.75 ± 0.57 kcal/mol** (MBAR); am1bcc charging and the
  warmup→production→commit/restore driver are GPU-validated. **GO.**
- **`[x]` EMC E3-ligase expression** — **$0.** All 10 components of both CRL2^VHL and CRL4^CRBN are broadly
  expressed (HPA), so the VHL-vs-CRBN choice is **not** constrained by machinery availability — decide on
  geometry/selectivity. (No EMC line in HPA — general mesenchymal availability.)
- **`[x]` Steric-exclusion DESIGN RULE (`S3`) — the measurement turned into something a designer runs** — **$0, CPU, no nod, [§10.1 row 24](#101--open-rows-ordered-by-what-unblocks-the-most).** Serves `R7` `R15`. Two substituent vectors, a shape spec and a per-candidate scorer, in [`steric-design-rule.json`](../modalities/steric-design-rule.json) (`python3 research/modalities/steric_design_rule.py --check`; the scorer **reproduces `M3`'s own 0.923-vs-0.173 over `M3`'s own 13 poses**, which is the check that would catch the rule and the measurement having become different objects). ⛔ **AND ITS CONTROL IS ATTACHED TO EVERY RECORD IT EMITS, WHICH IS THE POINT:** the paralogue's own docking **RELOCATES** these molecules by a median **5.31 Å (NR4A1) / 5.26 Å (NR4A2)**, so a high score means ***"this POSE is denied in the paralogue"* and NEVER *"the paralogue cannot bind this molecule"*** — it binds it somewhere else. Also carried on every record: the transfer is **RIGID** (the paralogue side chain is held in its own opened conformer and could rotate away), and **NR4A3's absence of clash is guaranteed by construction** and carries zero information, so only the between-class contrast is gradeable — which is why the scorer refuses to emit a signal without its matched null.
- **`[x]` Pocket-tracking re-analysis** — **$0.** Harmonized detection folded into the paper's Gate-2 wording:
  8XTT **19/20 frames detected, 3 ≥ D\*=0.53** (= 3/19 among detected, 3/20 across all deposited); release
  continuations druggable in 56/40/80 % of frames per replica, **44/75 = 59 % pooled**
  (`nr4a3-pocket-reharmonize-summary.json`).

### RUNG 1 — reference-reproduction smoke (mostly a citation)

- **`[x]` Validation A-mini — build-consistency smoke + cite OpenFE** — **~$0 · Cum. ~$2 · PASS/GO.** The public
  TYK2 `ejm31→ejm42` edge (both legs, 5 ns × 12 windows) gave **ΔΔG_bind = +0.366 vs exp −0.24 → abs err 0.61
  kcal/mol**, inside the 2.0 tolerance. Our container reproduces a known ΔΔG on the standard am1bcc method → cite
  OpenFE's published ~1.7 kcal/mol accuracy. Does not touch NR4A. **GO to Rung 2.**
  *(Scope: this covers the **am1bcc binary lane only**. The old rider "if am1bcc is ever forced to NAGL, Val A
  reverts to a paid ~$25 NAGL benchmark" has in fact **already fired** — every ternary and endpoint lane runs
  NAGL because sqm cannot charge PROTAC-sized ligands. Resolution: **Val B is the NAGL lane's known-answer
  accuracy control**, already on the ladder. What this costs us is the *citation*: OpenFE's accuracy number may
  not be quoted for any ternary result.)*

### RUNG 2 — cheap precision + cheap probes *(only if Rung 1 = GO)*

- **`[x]` Step 1 pilot — cmpd19 conditional RBFE** — **~$2.8 ($0.8–8.5; 1–2 RBFE edges) · Cum. ~$4.** First edge
  `zaienne_cmpd19 → cw_ev_5nh2` (5-Br→5-NH₂) converged: complex ΔG_morph −29.68 ± 0.24, solvent −31.52 ± 0.26 →
  **ΔΔG_bind = +1.84 kcal/mol** (the 5-NH₂ analogue ~1.8 kcal/mol weaker *in the modeled opened pocket*). Proves
  the congeneric-RBFE pipeline converges on the real NR4A3 system without pocket collapse — the pilot's crux is
  cleared. Reproducibility replicas + pose/state sensitivity are carried forward as **fan-out inputs** (they
  refine per-edge `n_windows` and the conditional caveat, and gate the fleet). This is statistical convergence on
  a *hypothesized* pose, **not** an accuracy claim.

- **`[~]` Validation B-mini — all-binding graded cooperativity edge** — **~$8.8 ($3.2–22) · Cum. ~$13.** The Wurz
  SMARCA2–VHL **cmpd 1→4** all-binding graded edge (α 12.8→2.6 ≈ +0.94 kcal/mol; both endpoints are productive
  binders — the cleanest first calibration). Exercises the bespoke `ΔΔG_coop = ternary − binary` cycle that
  cannot be cited away. **GO/NO-GO (verbatim from the prereg in `degrader-paper-schedule.json`; the
  ±1.0 kcal/mol band was deliberately REMOVED on 2026-07-17 because a separation <1 kcal/mol makes a noisy
  positive point estimate INDETERMINATE — do not re-introduce it):** PASS requires **positive sign + CI excludes
  zero + no fwd/rev disagreement + no collapse/escape/restraint-dominated leg + broad consistency with the
  measured +0.94**. valB_mini gates valB_full only — it does **not** authorize the NR4A matrix; until valB_full
  passes, NR4A ternary scores are **exploratory**. *(The cis-epimer PROTAC-2 edge is demoted to the
  negative-endpoint stress module of the cube below — a pass forced by holding an unstable pose is not a pass.)*

  **As-run protocol** (this is what the cost basis and the paper must describe): `NWIN=12` λ-windows ·
  `CHARGE_METHOD=nagl` · `TIMESTEP_FS=2.0` (warmup 1.0 fs) · `TEMPLATE_PDB=8G1Q` · GCP **L4 on-demand**. Both of
  this lane's deviations — timestep and NAGL-vs-am1bcc — are registered in `md_settings.py`'s docstring. The 2 fs
  step is empirical: the cause of the earlier warmup NaN is the **softcore alchemical region in a large, rough
  homology-built assembly**, there is no static predictor, and the fix that works is **plain-MD
  pre-equilibration** (`ternary_preequil.py`), not a smaller timestep. Authority: `ternary-rbfe-runbook.md`
  §1b/§1c.

  **★ r0 IS IN, IT IS THE WRONG SIGN, AND MORE REPLICATES CANNOT FIX IT (2026-07-25). Full analysis +
  recommendation: [valB-mini-r0-verdict-2026-07-25.md](valB-mini-r0-verdict-2026-07-25.md).**
  The first complete cycle (CI 30148463967, re-dumped 30155238348) gives **ΔΔG_coop(r0) = −0.534 kcal/mol**
  against the +0.944 target — wrong sign, 1.478 off, **both of which are r0's own superseded reading and NOT
  the lane's headline** ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 44 and 51; the
  current values are the n=3 mean −0.599 / abs error 1.543 in the scoreboard) — from legs binary **48.0046** / ternary **47.4701** /
  solvent **47.8060**, i.e. the answer is **1.1 % of the numbers being subtracted** (the reduction's own
  `cancellation_ratio` = 0.0111). Protocol hashes are
  **consistent** across the three legs, so the cycle is *not* contaminated by a protocol mismatch; the record's
  `converged: false` is only `n_replicas >= 3` failing at n=1, **not** an MD-convergence finding. Four
  consequences, each verified against the frozen gate rather than asserted:
  - **r1+r2 cannot PASS.** Exhaustive scan of every (r1,r2) over [−4,+8]² through `calibration_gate`: 0 PASS,
    17,276 BORDERLINE, 11,885 FAIL. Condition 3's boundary rule needs a first-round PASS to carry cycle
    SD ≤ 0.25, while one replicate pinned at −0.534 forces SD ≥ 0.69. Buying r1+r2 buys a
    *BORDERLINE-extend-to-5* or a FAIL — neither authorizes NR-V04.
  - **The n=3 round was never decisive.** A *perfectly accurate* method passes first-round only 9 % of the time
    at the repo's own assumed replicate SD of 0.7 (50 % at SD 0.3, 20 % at 0.5, 4 % at 1.0).
  - **The gate admits the null.** `|mean − 0.944| ≤ 1.0` accepts mean = 0.0, so at n ≥ 5 a method predicting **no
    cooperativity change** PASSES (verified: five replicates at +0.05 → PASS). Monte Carlo: PASS 22 % for μ=0 vs
    23 % for a method that is exactly right. **A gate you can pass by predicting nothing cannot validate
    anything.** ⚠ Recorded, deliberately **NOT applied** — amending a preregistered rule after a failing result
    needs an explicit, dated, reviewer-approved defect-fix, not a quiet retune.
  - **Two of three systematic-error detectors were never run; one *could not* run.** No reverse legs exist
    (`antisymmetry_fwd_plus_rev_kcal: null` on all three), there is no redundant edge so no cycle closure, and
    the reviewer's required change #1 (convergence analysis of the committed `.nc`) was **built but never wired
    to any dispatch path** — while `_diagnostics_ok()` returns True when the report is *absent*, so the gate's
    "all diagnostics pass" requirement was satisfied by never measuring it.

  **★ CONVERGENCE READ OUT (2026-07-25, run 30157501491) — r0 IS A MEASUREMENT, NOT A BROKEN RUN, WHICH SETTLES
  THE REPLICATE QUESTION.** Leg `calib_hi_to_lo__ternary_vhl`, seed 0: **2000/2000** production iterations ·
  MBAR ΔG **47.511 ± 0.045** ·
  overlap connected, min-adjacent **0.109** (floor 0.03) · equilibration fraction **0.381** · N_eff **676** ·
  12/12 replicas visiting both ends · **ΔG(t) full-vs-final-half 0.0023**, q3-vs-q4 **0.1255** · **fwd/rev gap
  0.0255** at f=0.875. Replica mixing **0.8915** against a 0.90 ceiling — passes, but **record as marginal**.
  Structurally stable: the alarming 78.9 Å → 14.97 Å solute RMSD is **periodic wrapping** (p50 2.50 Å, p90
  5.91 Å, ~2 % of atoms at ~1 box edge of 126.3 Å; √(0.02·100²+0.98·3²) ≈ 14.4 reproduces it), so the *ternary
  assembly did not rearrange* and the systematic does **not** implicate the SMARCA4→SMARCA2 starting model.
  **Consequence: the statistical error (0.045) is far smaller than the miss — ~34× against the landed n=3 miss
  of 1.543, and ~33× against the superseded 1.478 r0 read that day — so the wrong sign is
  SYSTEMATIC, and replicates shrink variance, not bias.** *(1.478 is r0's reading and is superseded twice over,
  [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 44 and 51; the conclusion is unchanged by
  either correction, which is why it survives being restated at both values.)* Made worse for the replicate case, not better:
  ternary seed *s* uses the *s%n*-th relaxed SMARCA2 model, so r1/r2 are partly *different structures* and their
  spread would conflate sampling noise with homology-model sensitivity.
  **★ THE LAST OPEN DIAGNOSTIC IS NOW CLOSED — `diagnostics_complete: TRUE` (2026-07-25, run 30169056960).** The
  **ligand-only** pose RMSD was the one mandatory metric never measured. No committed artifact is a topology
  file, so the ligand was *derived*: bonded connectivity read from the hybrid System inside the `.nc`
  (HarmonicBondForce + the softcore CustomBondForce + **constraints**, where X–H bonds live) partitions 141,968
  particles into 4 protein chains, 44,860 waters, 248 ions and **exactly one** ligand-sized molecule — a
  fail-closed identification with a single candidate, not a ranked guess. Result: `n=110, heavy=59` · **pose RMSD
  max 2.765 Å, median 1.644 Å** against a 4.0 Å threshold · `ligand_stable_ok: true` · `mandatory_unmeasured: []`.
  Two *independent* corroborations, both consistent: 59 heavy atoms equals `wurz-calib-frozen.json`'s
  `validation.heavy_1 = heavy_4 = 59` (an RDKit count from freeze time, unrelated to this trajectory), and the
  ligand identified separately in the 5k-particle solvent box matches the one found in the 142k-particle assembly.
  **So the ligand did not drift — which removes the last benign explanation for the wrong sign and leaves the
  systematic where the convergence analysis put it: in the model or the reference data, not in the sampling.**
  ⚠ **Seven defects were found in this gating diagnostic on 2026-07-25, every one reporting success while
  measuring nothing** (never wired · missing `openfe` · an unguarded lazy `mbar` that deleted six other metrics ·
  slice-MBAR never converging · a fwd/rev gap taken where it is identically zero · the checkpoint never opened
  because openmmtools wants `checkpoint.nc` and the driver writes `checkpoint.chk` · a ligand-pose threshold
  applied first to bulk solvent then to a four-chain assembly). Two produced *wrong verdicts*: a silent
  `diagnostics_ok=True`, then a fabricated hard FAIL. **This is an argument for spending the next dollar on
  INDEPENDENT checks — reverse legs, cycle closure — not more replicates through the same machinery.**

  **★ THE REVERSE LEG WAS UNREACHABLE — FOUR CALLERS PINNED IT SHUT (2026-07-25, all fixed).** The preregistered
  forward/reverse antisymmetry check (`hysteresis <= 1.0` — **now MEASURED, see the ★★ result immediately
  below; the `null` this block was written against is superseded**) could not be run at
  all, and each blocker was the same shape — *capability present in the engine, unreachable from outside*:
  (a) `MODE=converge` existed in `nr4a3_ternary_fep.main()` but no workflow could dispatch it; (b) the run
  invocation hardcoded `DIRECTION=fwd`; (c) there was no `direction` dispatch input (adding one hit GitHub's
  25-input cap → retired the confirmed-no-op `constrain_ligand_ch`, pinning `CONSTRAIN_LIG='0'` so every existing
  `clig0` commit prefix stays resumable); (d) `ternary-setup-prime-cpu.yml` pinned `DIRECTION: fwd`, and since
  the setup-cache key is `tag=<leg>_<dir>_r<seed>` a rev leg needed its own prime and could never get one while
  the GPU lane fails fast on `RBFE_REQUIRE_PRIMED_SETUP=1`. A `direction`-keyed commit prefix (`_dirrev`, applied
  only when direction≠fwd) now makes it impossible for a rev leg to silently resume the fwd trajectory.
  **Root cause of the rev-only failure (fixed):** `_build_components` passed `base_smiles=sa` to `_endpoint_pose`,
  where that argument means *"the identity of the molecule in the staged crystal SDF."* `sa` is the crystal ligand
  only in the FORWARD direction (calib_hi = cmpd1 = 8G1Q CCD `YHB`); cmpd4 is derived and in no crystal. With A/B
  swapped, the rev leg claimed the crystal held **cmpd4**, `_repair_pose` assigned bond orders against a template
  differing by N→CH, the thiazole lost its aromatic C–H, and NAGL rejected the molecule
  (`RadicalsNotSupportedError`). `CRYSTAL_SMILES` is now captured from the *unswapped* endpoint A; forward
  behaviour is byte-identical; 4 pure-stdlib regression checks added (`tests/test_ternary_crystal_identity.py`),
  one asserting that in rev the crystal must NOT equal endpoint A so the test discriminates the fix from the bug.
  **The forward r0 result is unaffected** — in fwd the argument was correct, `_endpoint_pose` fails closed on a
  SMILES mismatch, and the $0 5-part pre-spend gate's `endpoints_match` check passed.
  **Infrastructure finding worth keeping (fixed):** the setup-cache upload failure was **not** the "transient
  GcsApiError" the code called it — `gcloud storage cp` renders a permission denial as `GcsApiError('')` with an
  empty message, and only the python client showed the truth: **403, `gpu-runner@` lacked
  `storage.objects.create` on the `setupcache/` prefix** while succeeding on `stagecache/` in the same job. Two
  fresh builds died there (fwd 11.5 min, rev 11.7 min, same file) so it was systematic, and retries could never
  help; a 403 now aborts immediately with the real reason. **trimcrae granted the permission 2026-07-25 and a
  per-prefix write probe (`gcp-quota-check.yml`) confirms all four prefixes writable.**

  **★★ THE REVERSE LEG LANDED AND THE ANTISYMMETRY CHECK PASSES — the detector that "could not be run" is now
  a MEASUREMENT (2026-07-28, reduce [run 30353349373](https://github.com/trimcrae/Rare-cancers/actions/runs/30353349373)).**
  `calib_hi_to_lo__ternary_vhl` dir=rev seed 0 reached its result on GCP L4 (free trial credit) at 4:03 PM ET
  2026-07-27, and the reducer reports **`MEASURED |ΔG_fwd + ΔG_rev| = 0.325 ≤ 1.000 (PASS)`**. One home for the
  number: the reduction JSON in `gs://…-rbfe-ckpt/valB-6hax/results/` and that run's `[REDUCE-VERDICT]`
  annotation — never re-typed elsewhere.
  **What it does and does not buy.** It is an *internal-consistency* detector, and it is the first of the three
  systematic-error detectors to return anything at all: the forward and reverse alchemical paths agree to
  0.325 kcal/mol, so the wrong sign on this calibrator is **not** a path/hysteresis artifact. That is a genuine
  narrowing — it removes one of the two remaining benign explanations, exactly as the ligand-pose RMSD removed
  drift — and it leaves the systematic where the convergence analysis put it: **in the model or the reference
  data.** It is emphatically **not** evidence that ΔΔG_coop is right; antisymmetry is a check the sampling can
  pass while the answer stays wrong.
  **The calibrator verdict itself is still `INDETERMINATE`, and for a different reason than before:**
  `n_replicates=1`, `per_replicate_ddG_coop=[-0.522]` against `target=0.944`, so there is no replicate SD and
  the cycle cannot be graded. Cycle closure (the redundant edge) is **RUNNING as of 2026-07-29, 11:24 AM ET** —
  see step 5 below for its status and gate reading; it was the last unrun systematic-error detector.
  ⚠ **−0.522 here, −0.534 in the RUNG 2b timestep rows above, and BOTH are correct — do not "reconcile" them.**
  This line is the calibrator's CURRENT reading, which uses the restrained binary arm (Appendix A 44). RUNG 2b
  compares a 4 fs cycle against the *unrestrained* 2 fs one, so its comparator must stay **−0.534**: swapping
  in −0.522 would measure the restraint rather than the timestep, which is the whole quantity that gate exists
  to isolate. Changing either number in isolation silently breaks the other.
  **The blocker is still r1+r2, but they are no longer blocked — both are RUNNING** (2026-07-29, 11:10 AM ET).
  The partial-charge defect that had them dying on dozens of hosts is fixed and merged to `main`; each arm
  holds an RTX 5090 at **$0.005119/ns · 1.50× basis**, under the buy line. It was never held on price, never
  on capability, and never on anything GCP can supply (`GPUS_ALL_REGIONS = 1` makes GCP strictly serial) —
  that last clause still stands and is why the closure triangle went to Vast too.
  **Superseded, retained** (per rule 1, because the old status is quotable): "withheld by the failure breaker
  … its fix is on `fix/ternary-vast-deaths` and unmerged as of this writing." The branch is merged; the
  breaker's withholding of *these* units ended when the fix landed, and the four TRIANGLE units it was still
  withholding were cleared by `task=supersede-failed leg_only=to_lo2` at 11:18 AM ET — a deliberate gesture
  after the cause was fixed, not a loosening of the breaker, which re-arms on the next fresh `status=failed`.

  **Recommended next steps (spend order) — REVISED 2026-07-25 (LANE 5); steps 1, 2 and the ligand diagnostic are
  DONE, and step 4's named design was REFUTED for $0 before any spend:**
  1. ✅ *done, free* — the convergence analysis above, and now the **ligand-only pose RMSD** (`diagnostics_complete: TRUE`).
  2. ✅ *done, free* — **the admits-zero gate defect fix was already APPLIED in place at 8:25 AM ET**
     (commit `3f11cbf5`, delegated reviewer authority) — not merely proposed. It has since been **independently
     audited** (`valb_gate_audit.py`, calling the shipped gate): **strictly stricter across 20,468/20,468 grid
     points with 0 counterexamples**; **conditioned on r0 the corrected PASS rate is 0.0 % in every cell**
     (superseded rule: up to 71.6 %); an exhaustive 58,081-cell (r1,r2) scan gives **0 PASS under both**, so it
     demonstrably **does not rescue the failing result**; discrimination improves 2.0× → 10–3330×. Ratification
     block: §8 of [valb-gate-defect-fix-audit-2026-07-25.md](valb-gate-defect-fix-audit-2026-07-25.md),
     which states the "applied after an unfavourable result" optic plainly as the risk.
  3. *in flight* — the **reverse** ternary+binary legs, testing |ΔG_fwd + ΔG_rev|.
  4. **⚠ THE NAMED RESCOPE IS DEAD — the P-series cannot carry this calibrator, established for $0 on real data**
     (`valb_pseries_chem.py` → `valb-pseries-chem.json`; RCSB REST + RDKit MCS in the production mapper's own
     container). **6 of 10 pairs change formal charge** — including **P1→P4 (+2.53), which is `charge_change: -1`
     and therefore blocked by the same missing charge correction that blocks 8 legs of `step1_fanout`** — and the
     4 charge-neutral pairs perturb **58–80 heavy atoms** against the **2** of the edge already running. P4's
     structure (9HYO) is also only **3.74 Å**, so it would not have fixed the resolution problem either.
     **General conclusion worth stating in the paper: a ≥2 kcal/mol ternary calibrator that is simultaneously
     small, charge-neutral and mappable may not exist in the public literature** — large cooperativity
     differences are *produced by* large chemical changes.
  5. **★ RECOMMENDED INSTEAD — a synthetic closure TRIANGLE, RE-SCOPED BY ITS OWN $0 PRE-GATE.**
     **`[~]` RUNNING — AND THE FIX IS PROVEN ON THIS LANE, not merely deployed to it (2026-07-29, 12:12 PM
     ET).** Both binary legs have written committed checkpoints (`warmup/64` → `192`), and these are the exact
     units that died 15 and 7 times at `proto.create` on the partial-charge defect. Passing setup and
     committing is the first direct evidence the fix holds for the triangle's own endpoints — the earlier
     evidence was from the 4 fs replicate arms, a different morph. Progress since has been by COMMITTED
     CENSUS, never a watchdog verdict.
     **`[~]` RUNNING 2026-07-29, 11:24 AM ET — all four legs rented in parallel on Vast.** The gate cleared at
     **1.36× basis** (`$0.004637/ns` mean, against the `$0.006539/ns` buy line) on a deep board — 163 offers,
     159 qualifying, 100 priceable — projecting **$7.73 against this rung's $15.40 ceiling**. It had been
     stalled since 2026-07-28 not on price but on the partial-charge defect, which killed the four units on
     15, 15, 7 and 21 separate hosts and left them withheld by `leg_failure_breaker`; the fix landed 10:53 AM
     ET and the stale failed records were superseded at 11:18 AM ET. Cost of that stall being *legible*: the
     triangle gate had no branch for the breaker's exit code, so it printed the block as `HELD on price` —
     fixed in the same session and pinned by `tests/test_gate_exit_codes_render_distinctly.py`.
     **`[x]` BUILT AND RUNNABLE 2026-07-27 (LANE 19).** It was fully costed and fully argued and could not be
     *run*: no leg id, no third endpoint, no launcher mode, no reducer. It now has all four —
     [`valb_triangle_legs.py`](../modalities/valb_triangle_legs.py) (the 4 new legs plus the derived
     third vertex, frozen in [`valb-triangle-frozen.json`](../modalities/valb-triangle-frozen.json)),
     `MODES['triangle']` in [`ternary_vast_launch.py`](../modalities/ternary_vast_launch.py), and
     [`valb_triangle_reduce.py`](../modalities/valb_triangle_reduce.py) → `R`. Venue **Vast**; GCP was
     declined deliberately — its scarce quantity is **GPU-days, not dollars**, and this rung would cost
     ~7.3 SERIAL days of the only GPU to save the plan figure below.
     **Three invariants are enforced in code, not remembered**, because each silently turns `R` from a
     path-error detector into a *protocol-difference* detector: **2 fs** (a mode-level pin that beats the
     lane-wide 4 fs export — r0 is 2 fs and r0 *is* T1), **seed 0** on every leg, and **UNRESTRAINED** binary
     legs matching r0. *(The restrained binary re-run is a DIFFERENT experiment; the two must never be
     conflated or their legs mixed in one reduction.)*
     T1 = cmpd1→cmpd4 **is r0, reused** at coefficient +1 (verified: the triangle closes in T1's as-run
     direction, no sign flip). Evidence:
     [valb-closure-triangle-pregate-2026-07-25.md](valb-closure-triangle-pregate-2026-07-25.md)
     (`valb_triangle_chem.py` in the production mapper's own container + `valb_triangle_closure.py`, 19 tests).
     **Three corrections to the design as originally proposed:**
     - **(i) T3 is a DOUBLE perturbation for all four named cmpd4′ candidates** — X and Y act at different
       sites, so the closing edge carries both, which `rbfe_map.py` forbids *specifically for closing edges*
       (*"Each closing edge is itself a SINGLE-site change (not a double mutation)"*). **Use an AZA-SCAN at the
       linker ring instead:** cmpd1 (aza) → cmpd4 (all-carbon) → cmpd4″ (aza moved) — three vertices at **one**
       site, every edge **single-site, charge-neutral, a pure element change with ZERO heavy dummies**, and
       entirely inside the linker so it touches **no pharmacophore** (all four named candidates land on one).
       Hand-verified from the SMILES: the linker ring is `c4ccnc(c4)` with a carbonyl and a piperazine at the
       substituted positions, leaving **exactly 3 free CH** vertices.
     - **(ii) Price is ~$6.83 at n=1 and ~$27.32 at n=3, not $5.9/$17.6.** Three corrections, and **the largest
       is NOT the iteration basis**: (a) the 2800-iteration/3.5e6-step basis is +16.7 %; (b) solvent legs add
       ~$1.31 if run by default; **(c) T1 has only r0, so an n=3 triangle is 16 legs, not 12 (+33 %) — and it
       silently re-includes the r1/r2 spend the r0 verdict argued against.** At 4 fs everything scales by
       **0.643, not 0.5** → n=1 ≈ $4.39. Every figure is a **ceiling** (the binary leg is charged at the
       ternary rate despite lacking the SMARCA2 bromodomain).
     - **(iii) `_endpoint_pose` cannot build any cmpd4′ today** — it has exactly one mutation path
       (`_pyridine_to_benzene_pose`) and raises `SystemExit("refusing a wrong-molecule leg")` otherwise. The
       claim that "the machinery carries over unchanged" is false; the aza-scan needs a one-line generalisation.
     **Reporting rules that fall out of the algebra:** report **`R_ternary` and `R_binary` SEPARATELY** — since
     `R = R_ternary − R_binary`, a clean `R` can be two large closures cancelling, and both come from the same
     six legs. And **run all three edges at seed 0**: seed *s* selects the *s%n*-th relaxed SMARCA2 model, so
     mixed seeds mean different Hamiltonians, unshared endpoints, and `R` stops being a closure residual at all.
     **★ HONEST LIMIT, SHARPENED FROM "consistency, not accuracy" TO SOMETHING MUCH STRONGER: closure is
     IDENTICALLY ZERO for ANY per-endpoint state-function error.** Writing `ΔΔG_calc = ΔΔG_true + e`, the true
     terms telescope around a cycle so `R = Σe`; and if `e(A→B) = ε(B) − ε(A)` — which is what a *state*
     property gives — that telescopes too. **So closure sees only the NON-CONSERVATIVE part of the error.**
     Invisible to it: **force field, the SMARCA4→SMARCA2 homology model, NAGL charges, protonation, and the
     reference data**. Visible: λ-sampling/hysteresis, endpoint-state inconsistency, inconsistent atom maps.
     *(Verified numerically two ways: max |R| ≈ 1e-14 over 20,000 random state-function draws, non-zero the
     moment a path error is added.)* The known-answer **accuracy** requirement therefore stays **OPEN**.
  6. **⚠ Rev-leg decision tree — and "the triangle is worth buying under either branch" is RETRACTED. It was
     recorded here on 2026-07-25 afternoon and its own pre-gate refuted it the same evening.**
     - **Branch A** (|ΔG_fwd + ΔG_rev| ≈ 0 ⇒ the systematic is in the **model or the reference data**): closure
       is **provably blind to both** by the telescoping identity above. It would return a clean `R` and diagnose
       **nothing**. *Refuted for diagnosis.*
     - **Branch B** (large ⇒ path error): closure is the right *class*, but the reverse leg already establishes
       it for those 2 legs, and the design's own instruction is **"fix the protocol first"** — so a triangle
       bought before the fix measures the **old** protocol. *Redundant, then stale.* Replica mixing **0.8915**
       against the 0.90 ceiling leans toward this branch, i.e. **the worst branch to buy into.**
     - **★ The real reason to buy is narrower and specific.** The fwd/rev pair already in flight **is** a closed
       2-cycle, so the triangle only earns its keep where a 2-cycle cannot reach. Over 4000 draws — state-function
       error: 2-cycle 0.00 / 3-cycle 0.00; symmetric path bias: both 1.00; **antisymmetric per-edge bias:
       2-cycle 0.00, 3-cycle 1.00.** That last row is the triangle's **exclusive** territory, and on an
       equal-cost 4-leg comparison it still beats both alternatives.
     - **Order:** read the rev leg → **Branch B ⇒ fix the protocol, do NOT buy** → **Branch A ⇒ buy the ~$1.31
       SOLVENT-ONLY closure pre-scout first** (2 new legs; T1's solvent leg already ran; a full machinery closure
       — atom maps, endpoint identity, λ schedule, charges — in a ~5k-particle box at **19 %** of the scout
       price, able to falsify the triangle before any 142k-particle leg), then the **~$6.83 n=1 scout**.
       **Do not buy n=3 at ~$27.3 without a separate decision.**

  **★ THREE MEASUREMENTS THAT REORDER THE PROBLEM (LANE 5, $0):** (i) even the *corrected* gate certifies only to
  a **factor of 4.1** (accept band [+0.472, +1.944] on a +0.944 target); (ii) **P(PASS) has a hard ceiling of
  `P(sample SD ≤ 0.75)` = 66.8 % at σ = 0.7, independent of the target** (analytic and MC agree to 0.15 %) — so
  above ~2 kcal/mol **only precision buys anything**; (iii) sweeping the target shows **2.0 kcal/mol is the
  knee**, which *derives* this file's "≳2" from the gate's own arithmetic instead of asserting it. Consequence:
  **redesigning for a tighter cycle SD beats hunting a bigger signal.**

- **`[ ]` Rung 2b — 4 fs adoption + matched re-calibration** — **~$4.4 ($1.6–11) · Cum. ~$17 · PROPOSED, needs a
  go.** **Exact invocation** (three flags, all load-bearing): `mode=preequil` once (cached), then
  `mode=run use_preequil=1 timestep_fs=4.0 warmup_timestep_fs=1.0 reset_commits=1`. `use_preequil=1` because 4 fs
  only held *with* pre-equilibration; `reset_commits=1` because OpenFE refuses to resume a checkpoint whose
  protocol timestep differs ("Sampler in checkpoint does not match Protocol settings"), so a dt change **starts
  clean** — a fresh edge, not a continuation, which is what the ~$4.4 already prices. One edge, three jobs:
  (a) exercises 4 fs over a **full** 2000-iteration production leg (the existing evidence is 40 iterations);
  (b) supplies the **matched-timestep** calibration the runbook requires before any 4 fs production result may be
  quoted; (c) is an independent reproducibility replicate of the 2 fs ΔΔG_coop. **GO/NO-GO:** no NaN across the
  full leg AND ΔΔG_coop consistent with the 2 fs run within replicate SD → adopt 4 fs for every downstream
  ternary leg (**1.56×** cheaper — *not* 2×, see cost lever 1 — and the ladder has ≥6 of them). NaN or a shifted
  ΔΔG → stay at 2 fs.

  **★ THRESHOLD RATIFIED 2026-07-25 (trimcrae delegated judgement): |ΔΔG_coop(4 fs) − (−0.534)| ≤ 0.7 kcal/mol.**
  The frozen wording says "within replicate SD" and **there is no replicate SD** — the 2 fs arm is a single
  cycle. Lane 4 pre-specified **0.7**, the repo's own assumed replicate SD, **before any number existed**.
  Ratified as written, for one reason that outranks the others: **pre-specification is the property that
  matters, and revising a threshold now — after the probe survived — would be precisely the retune this program
  forbids.** Both arms are seed 0, hence the same homology model *index* — and the two lanes each built their
  own copy of it, so what is established is that the two builds have an identical atom set (measured:
  [ternary-4fs-vast-findings.md §2d](../compute/ternary-4fs-vast-findings.md)), not that they started
  from bit-identical coordinates.
  **⚠ AND THE COMPARATOR STAYS THE UNRESTRAINED r0 VALUE.** The r0 cycle now also has a **restrained** binary
  arm ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 44), and swapping that reading in here
  would pair a restrained arm against the 4 fs cycle's unrestrained one — measuring the restraint, not the
  timestep. The restraint is deliberately a different Hamiltonian and is invisible to a composition census
  (it adds a force, not atoms), so this is the one place the like-for-like pairing has to be stated rather
  than inferred.
  **Recorded honestly: 0.7 is LENIENT, and the leniency runs in the unsafe direction.** It is an *assumption*,
  not a measurement, and today's protein-mutation benchmark showed between-setup SD is strongly regime-dependent
  (**±0.175** on a near-null perturbation vs **±1.077** on a hot spot, a 6.2× spread). A 4 fs-vs-2 fs comparison
  on the *same system with only the timestep changed* is a **small**-perturbation regime, so the honest expected
  SD sits near the ±0.175 end — which makes 0.7 roughly 4× wider than the physics warrants. Since a PASS *buys*
  a protocol change, a too-wide band errs toward adopting 4 fs on weak evidence. **Therefore, reporting rule
  (additive, not a loosening): report the actual |Δ|, and a pass landing in the 0.35–0.7 band is
  "consistent but WEAKLY DISCRIMINATING" — adopt provisionally and require the next ternary replicate to
  confirm it, rather than treating 4 fs as settled.**
  **✅ THE PRE-EQUILIBRATION CONFOUND IS RESOLVED (2026-07-25, $0) — the 2 fs baseline WAS pre-equilibrated.**
  The caveat this replaces read: *"`use_preequil` for the 2 fs baseline was never verified — only the workflow
  default of 0 is recorded"*, and it would have made a NO-GO uninterpretable.
  **⚠ BUT THAT DOES NOT MAKE THE TIMESTEP THE ONLY DIFFERENCE, AND THIS ENTRY USED TO SAY IT DID
  ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 45).** Measured 2026-07-28, $0, from the
  committed trajectories themselves: the two arms run the **same alchemical system** — solute identical
  atom-for-atom in every arm, and the neutralising ion excess (i.e. the solute's formal charge) invariant across
  every build — but they are **two independently constructed builds of it**, on different lanes, providers and
  GPUs, each with its own staging, solvation and pre-equilibration. Their ternary boxes differ by 675 bulk
  waters and 4 ions. **A disagreement would therefore still not have been attributable to the timestep alone**;
  the agreement is a cross-lane independent reproduction, which is a different and in one respect stronger
  claim. Evidence, the full composition census and the ΔΔG sizing:
  [ternary-4fs-vast-findings.md §2d](../compute/ternary-4fs-vast-findings.md).
  **How it was settled, and why a cache listing could not do it.** A read-only setup-cache probe (added to
  `gcp-quota-check.yml`, dispatched against this branch — it writes nothing and cannot perturb the concurrent
  GCP leg) shows **three** versions coexisting for the forward leg: `v1`, `v1pe`, **`v2pe`**. So *presence* is
  not the discriminator — several caches legitimately exist and a listing cannot say which one a leg
  **restored**. The decisive field is the leg's own `setup_cache_version`, whose physical fingerprint is the
  **particle count**: `v2pe` (alchemy from the plain-MD-relaxed complex) = **141,968**; `v1` (raw) = **146,020**
  (`ternary_fep_reduce._SYSTEM_IDENTITY_FIELDS`). **The committed r0 forward `.nc` holds 141,968 particles** —
  measured independently by the ligand-identification work, which partitioned exactly that many particles into
  4 chains, 44,860 waters and 248 ions — and `nr4a3_ternary_fep.py:682` records the same fingerprint verbatim
  (*"fwd's 141,968-particle v2pe"*). **⇒ r0 is `v2pe`, pre-equilibrated.**
  *(This is also the fingerprint that caught the four failed reverse attempts, which ran a 146,020-particle `v1`
  build against the forward leg's 141,968-particle `v2pe` — a mismatch `protocol_hash` cannot see.)*
  **Two-stage, per the 2026-07-24 decision:** stage 1 is a **~$1–2 survival probe** (`prod_iters≈200`) asking
  only "does 4 fs survive well past the 40 iterations the runbook demonstrated?"; stage 2 is the full matched
  edge, only on a passing probe. Sequenced **after** valB_mini's 2 fs result, both because the calibration needs
  something to compare against and because dispatching into that lane now risks cancelling another session's run.

### RUNG 3 — expand the benchmarks *(only if Rung 2 probes look promising)*

- **`[–]` Validation A-full (10–20 edges) — SKIPPED · saves ~$50–140.** valA_mini reproduced the known ΔΔG cleanly
  on the standard am1bcc method, so a full re-derivation is redundant with OpenFE's published benchmark. Framing
  that must hold: cite OpenFE for accuracy; present valA_mini as a single-edge build-consistency confirmation, not
  a standalone benchmark.
- **`[ ]` Validation B-full — component-calibration cube** — **~$22.5 ($6–67) · Cum. ~$40.** ★ **Module 3
  (paralogue discrimination) runs on SMARCA2-vs-SMARCA4, not NR-V04** — **ADOPTED 2026-07-24 (trimcrae go)**: a
  close paralogue pair with degrader-level selectivity, solved structures, a **non-covalent** mechanism, and —
  decisively — **already staged in this repo** (8G1Q, `smarca2_model.py`, the frozen Wurz calibration), so it is
  a marginal add-on to the lane valB_mini already runs rather than a new campaign. NR-V04's selectivity is, by
  the repo's own UniProt result, most plausibly **covalent target-engagement**, which makes it a weak calibrator
  for a noncovalent ternary pipeline — exactly why the reviewer demoted it to a biological holdout. It stays the
  holdout. Apply cost lever 2: the paralogue module needs **N ternary legs + 1 shared binary + 1 shared
  solvent**, not N edges. Four separately-calibrated modules, each with its own pass/fail (a failed module →
  qualitative-only; no blanket "validated"): (1) a second all-binding graded cooperativity edge; (2) ternary pose
  recovery (co-fold, ~$0); (3) paralogue discrimination on a public system (the direct analogue of the NR4A ask);
  (4) productive-vs-unproductive ubiquitination geometry (full-CRL MD). Plus the cis-epimer negative-endpoint
  stress module. **GATE:** the prospective ladder never runs unless the **cooperativity + paralogue-discrimination**
  modules pass.
- **`[!]` NR-V04 covalent feasibility panel — ⚠ RESULT UNDER CORRECTION; ITS **GO** DOES NOT STAND** —
  **~$8 (MEASURED as-run, 18 legs) · Cum. ~$48.** Covalent celastrol–NR4A1 (C551) adduct + C551A + noncov/cov
  sensitivity + warhead/recruiter controls; 18 legs (6 systems × 3 seeds), 6 ns each, ~466k atoms; 17/18
  completed, no blow-ups.
  **⚠ THE READOUTS DESCRIBE THE WRONG INTERFACE.** `nrv04_covalent_md._topology_indices` split E3 from target
  POSITIONALLY ("target = last sorted protein chain"), while the co-fold YAML builder writes the target FIRST
  (`proteins = [("A", lbd)] + e3`). The chains are A=254 (NR4A LBD), E=213 (VHL), F=118 (EloB), G=112 (EloC), so
  the rule selected **Elongin C** as the degradation target: R1/R2 measured the **EloC↔rest** interface and R3
  counted **Elongin C's** lysines, not NR4A1's. Proof from the panel's own committed legs — the reactive Cys,
  resolved independently by geometry and sitting on the NR4A1 LBD, is recorded on chain **A** in 12 of 14 legs
  while the positional rule pointed at **G** (CI run 30122828434). The arithmetic reproduces the reported numbers
  exactly; the *interface* is wrong. The superseded science numbers are listed in
  [§Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) and **must not be cited**; the
  infrastructure/pricing record (~$0.43/leg, ~$8/panel) is unaffected.
  **★ STATUS (2026-07-25, LANE 3) — THE WITHDRAWN GO CANNOT BE RECOVERED AT $0, AND IT WAS NEVER AVAILABLE TO
  RECOVER. THE RE-RUN IS `[HELD]`, NOT MERELY UNLAUNCHED.** Four findings, each measured, not argued:
  1. **No trajectory was ever persisted**, so recomputation against the correct chain pair is impossible. A
     read-only S3 census (`nrv04_result_forensics.py`, CI run 30167457977 → `nrv04-result-forensics.json`) finds
     **72 objects / 19 units and `trajectory_objects_found: 0`** — 796 MB of `built_cif` (solvated topology +
     **pre-minimisation** coordinates = one frame), 1.35 GB of `built_system` (forces/parameters, no coordinates
     over time), and 27 kB of `leg_result` scalars **already reduced against the wrong split**. The driver
     reduces each frame in-loop and discards positions, and `_rm_ckpt` deletes the single checkpoint frame on
     clean completion (17/18 legs). The MD must be re-run or nothing.
  2. **The prereg's own frozen `panel_verdict()` returns `go: false` on the panel's own committed legs** —
     *"warhead_only recruited despite no E3 moiety"* and *"inactive epimer engaged VHL"*, i.e. **both negative
     controls came back positive**. All 17 legs returned `frac_frames_in_contact = 1.0`, and R2's frozen rule
     (any contact in >50 % of frames) **cannot be failed by a system started from a co-folded complex** — the one
     leg ever run with the *corrected* split returns `recruited=true` too. The recorded GO ("active 3/3 vs epimer
     1/3") is an **R1 narrative that §5 does not score.** So the chain split changed which interface the numbers
     described; it did **not** manufacture a GO that the frozen rule would otherwise have given.
  3. **The panel's INPUTS were contaminated as well — a third, independent data-invalidating defect.** A census
     of all 12 persisted systems gives `A=254 E=213 F=255 G=112`; a CA-geometry Kabsch match identifies the
     source as `nrv04-descriptive-v3/nr4a1/seed_1` at **RMSD 0.000 Å**, with the clean `nrv04-covalent-cofold`
     **5.884 Å** away. So the panel **simulated 14-3-3 epsilon where Elongin B belongs.** Mechanism:
     `fusion-cpu-extras.yml@786759a9` set `cofold_prefix` default `"nrv04-descriptive-v3"`, so the launcher's
     clean fallback never fired. **⚠ The 2026-07-24 forensics' "the panel is clean on this defect" is RETRACTED**
     — it audited the prefix the *code names*, not the artifact that *ran*.
  4. **A free pre-spend staging check shows the re-run cannot reach the frozen GO on any co-fold in the bucket.**
     All 6 legs stage cleanly with `target=A e3=[E,F,G]` (so the chain fix itself is proven end-to-end for $0),
     but `warhead_only`'s nearest **target-chain** Cys Sγ is **16.39 Å** and `cov_nr4a1`'s is **8.99 Å** — Boltz
     does not seat celastrol against an NR4A1 cysteine in *either* co-fold, so criterion 3 is **unevaluable** on
     every available input. Staged epimer interface 369 contacts vs active 381 (**3 %**) is noise.

  **Consequence: do not pay for the re-run as built.** It is `[HELD]`.

  **★ THE PREREG AMENDMENT IS DONE (2026-07-25, trimcrae-delegated) — and it does NOT authorise the re-run.**
  [AMENDMENT 1](../modalities/nr4a3-nrv04-covalent-feasibility-prereg.md#amendment-1--2026-07-25-dated-defect-fix-trimcrae-delegated)
  is appended to the prereg with the frozen text left **unedited**. The standard applied: a rule may be amended
  only if its *statistic is shown to lack discriminating power*, demonstrated independently of whether we liked
  its answer. Four rulings:
  - **R2 retired as a gating criterion** → descriptive only. `frac_frames_in_contact` took **18 values and one
    distinct value, 1.0**, including `warhead_only` (no E3-binding moiety) and `recruiter_epimer` (inactive
    stereoisomer). Zero variance across the contrast ⇒ cannot score the contrast.
  - **Frozen criterion 3 removed from the GO condition** — it depended entirely on R2 discriminating, so it was
    **unsatisfiable**, and the gate returned NO-GO regardless of the science. Uninformative, not conservative.
  - **`recruiter_epimer` demoted** to a descriptive sensitivity leg — it runs as a full ternary, not the binary
    §3 specifies, and 6 ns from a co-folded pose cannot resolve a binding-affinity difference anyway.
  - **★ NEW BINDING CRITERION A1 — input admissibility, and it FAILS NOW.** A covalent leg must stage its
    electrophilic carbon within bonding distance of the **target-chain** Cys Sγ.
    ⚠ **CORRECTED SAME DAY BY [AMENDMENT 2](../modalities/nr4a3-nrv04-covalent-feasibility-prereg.md):
    A1 was measuring the WRONG CYSTEINE.** It resolved the *nearest* of the construct's **six**, which is
    **C566**, not the preregistered site **C551** (offset 344: co-fold resid 222 = C566, 207 = C551; the panel's
    legs record resid **222** throughout). **At C551 the real distances are 28.46 Å (`cov_nr4a1`) and 36.43 Å
    (`warhead_only`), and 28.42–39.11 Å across ALL 34 co-fold models** — against a ~1.8 Å C–S bond.
    *(Superseded, do not cite: 8.99 / 16.39 Å.)* **This makes A1 more binding, not less: at ~9 Å it was NEARLY
    PASSING an 8.0 Å limit, so a co-fold seating celastrol 7 Å from C566 would have PASSED while the real site
    sat ~28 Å away.** Two further defects shared the root cause and are fixed: the covalent **restraint would
    have been built onto C566**, and **`cov_c551a` was mutating C566** — the control named for removing C551
    engagement was not touching C551 at all. Boltz seats
    celastrol against no NR4A1 cysteine in any co-fold in the bucket, so §5 criterion 2 (*does covalency swamp
    the ternary signal* — the panel's stated crux) is **unevaluable on these inputs**, not merely unmeasured.
    Enforced in code (`nrv04_covalent_md`, `MAX_COVALENT_TETHER_A` default 8.0 Å, override only with a recorded
    deviation) and **retrospective in force** — it binds the NR-V04 retrospective's covalent legs too.

  **Non-rescue, stated as the integrity test:** the amended gate leaves the panel exactly where the unamended one
  did — **`[HELD]`** — because A1 fails on every available input. What changed is *why*: from "a gate that can
  never pass" to "inputs that do not instantiate the contrast." **It converts no NO-GO into a GO.** Stated
  plainly: removing an unsatisfiable criterion *is* a loosening, since GO becomes reachable where it was not;
  the justification is the measured absence of discriminating power, not the unwelcome verdict. Same degenerate
  class as valB_mini's gate that **admits the null** — one always fails, one passes anything.
  **★ SAID, 2026-07-25: the covalent legs are DROPPED and the panel is re-scoped to NONCOVALENT.** The re-fold
  route was **run and refuted** for **$0.05** on Vast (2 systems × 3 seeds), not argued away: deleting the E3
  makes seating *worse* (33.6/36.6/44.7 Å vs ~28 Å ternary, so the ternary arrangement is not the cause), and a
  **steered** co-fold that demonstrably honoured an explicit `max_distance: 6.0` restraint to residue 207
  (~37 → ~15 Å, contacts doubled) **still never satisfied its own 6 Å bound on any of three seeds**, parking
  celastrol near the buried C505. **One predictor** (Boltz-2) fails to produce the pose across 7/7 clean models, 4 seeds and 3 prefixes *(the "2 providers" are compute hosts, not two independent predictors — so this is a Boltz-2 result, not a statement about structure prediction in general)* and no deposited celastrol–NR4A1 structure constrains it, so the only route left is a **hand-placed
  pose** — which fixes the *comparison* without supplying the *evidence*. **This is a statement about the
  predictor, not about whether celastrol binds C551**, which is literature-anchored (Zhang 2018,
  doi:10.1039/C8CC06140H). **Retiring them costs little: Leg 0 already did their job for $0** — the reactive Cys
  is unique to NR4A1 (NR4A2 Tyr, NR4A3 Thr579), which is the covalent confound's actual content — and NR-V04 is
  already a demoted *biological holdout*, so modelling its covalency inverts the ladder.
  *Hypothesis the amendment raises and the re-run can test (not asserted): the superseded covalent-vs-noncovalent
  null (2/3 = 2/3) is what one predicts if the "covalent" leg never carried a bond.* Full evidence:
  [nrv04-covalent-panel-recovery-2026-07-25.md](../modalities/nrv04-covalent-panel-recovery-2026-07-25.md)
  · prior chain forensics
  [nrv04-cofold-chain-forensics-2026-07-24.md](../modalities/nrv04-cofold-chain-forensics-2026-07-24.md).

  **★ FOUR BUGS FOUND HERE PROPAGATE TO THE UNLAUNCHED NR-V04 RETROSPECTIVE (RUNG 4), WHICH SHARES THIS DRIVER —
  both are fixed with regression tests, and the retrospective must not launch on the old code.**
  (i) **`_reactive_cys_by_geometry` was chain-blind** — a second live instance of the *same* defect class as the
  chain split; it is now restricted to the identified target chain, raises above an 8 Å preformed-adduct limit on
  covalent legs, and records its search diagnostics. (ii) **R3 reported NANOMETRES under an Ångström label.**
  OpenMM positions are nm; R1 converted (`* 10.0`), R3 did not, so **every committed R3 is ~10× too small** —
  reading as ubiquitination-competent (~2–4 Å) when the true separation is **~30–49 Å**. Independently
  cross-checked: `warhead_only` reported `min_A` 2.34/2.44 against a t=0 distance of **25.21 Å**.

  **★ HIGHEST-LEVERAGE INFRASTRUCTURE CHANGE FOR THE WHOLE TERNARY PROGRAM (adopted as a requirement, 2026-07-25;
  ✅ IMPLEMENTED 2026-07-30): every MD driver must persist a strided TRAJECTORY.** Tens of MB against the ~112 MB
  System XML the driver *already* uploads — and every analysis defect above (wrong chain split, chain-blind
  cysteine search, the R3 unit error) would then have been correctable for **$0** instead of costing a re-run.
  This is the concrete, general lesson from a panel that produced three data-invalidating defects and left
  nothing to re-derive from. **The requirement stood unimplemented for the whole of that period and the
  retrospective would have inherited the gap** — what shipped, why it is an *analysis-atom* closure rather than
  every heavy atom, and what that does and does not buy, is in
  [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) 4,
  which is the one home; code: [`md_analysis_traj.py`](../modalities/md_analysis_traj.py).

### RUNG 4 — warhead map, differential atlas, retrospective gate

- **`[~]` Step 1 fan-out — cmpd19 congeneric map** — **~$36 ($15–80; ≈19 RBFE edges × ~13.7 ref GPU-h) ·
  Cum. ~$84.** **RESUMED and RUNNING as of 2026-07-27** — the old *"HALTED at ~$2 with 0/19 ΔΔG"* framing is
  retired. **1 edge complete** (`cw_ev_5cooh`, ΔΔG_bind **0.688 ± 0.197** kcal/mol — a within-run MBAR
  uncertainty, **not** a replicate SD), **1 edge permanently BLOCKED** (`cw_bio_nmethyl_amide`: no available
  mapper reaches the **20-atom provable floor** — LOMAP 17/19, Kartograf 18, against a complete 22-atom map
  that exists as a graph fact, and both LOMAP budgets returned in **0.01 s**, so the MCS timeout is measured
  *not* to be the mechanism. A relaunch aborts identically and buys nothing), **17 remaining and being placed
  as the market allows.** Spend, live state and `$/ns` are on the IN FLIGHT board and in
  [`realised-spend.json`](../modalities/realised-spend.json) — not restated here.
  Full record: [step1-fanout-lane.md](../modalities/step1-fanout-lane.md).
  **Scope, if resumed:** the price covers **tranche 1 only** — the 19 edges at their charge-**conserving**
  microstate leg on the **primary frame**. The 8 charge-changing legs are *blocked* (no charge correction
  implemented) and the 6-frame conformer/paralogue axis is a **separate ~6× spend** — so tranche 1 yields a
  single-conformer **conditional** map, **not** the selectivity readout and **not** the sensitivity ranges.
  **Gate:** Val A satisfied (cite OpenFE) AND the Step 1 pilot behaved.
  **Timestep is NOT a lever** — measured free on CPU: the protocol runs at OpenFE's default `constraints=hbonds`
  + HMR 3.0, every X–H is constrained, so all edges are already 4 fs and no 2× saving exists.
  **The "HELD by decision" line that stood here is SUPERSEDED** — the hold was reversed on 2026-07-26 and the
  lane is running; §Open decisions 4 records what retired it.
- **`[ ]` Step 1 fan-out · REPLICATES ON THE OPEN CYCLE — the map's two open caveats share ONE fix** —
  **~$25 (3 edges × 2 further replicates)** · Cum. ~$109. **Added 2026-07-30.** The fan-out delivered 18 edges
  at **one replicate each**, and that single fact is what leaves two separate things unresolvable:
  1. **`cycle_3carbonyl` does not close** (R = +1.307 against a ±1.0 tolerance). The residual is a property of
     the LOOP, so it cannot name the guilty edge — and at n = 1 it also cannot be separated from three unlucky
     single draws. **Its three edges therefore carry a reservation wherever they are quoted**, which is a live
     tax on the paper's §2.9.
  2. **The pilot and the fan-out disagree by ≈0.78 kcal/mol on the SAME nominal perturbation**
     (`cw_ev_5nh2`: +1.84 ± 0.36 vs +1.064 ± 0.118) — several times either stated error. Different lanes and
     settings, so it is not a like-for-like replicate and licenses no reproducibility statistic in either
     direction; it is currently reported as an unreconciled discrepancy.
  **What replicating the three edges of that cycle buys, and why it is one purchase not two:** it attributes
  or dissolves the closure violation, *and* it delivers **the binary lane's first measured replicate SD**. The
  program owns exactly one replicate SD today (0.375, on the **ternary** lane) and transfers it everywhere —
  including into the resolvable-margin figure in §MECHANISM-FIRST and into `S`'s power. A binary-lane number
  would stop that being a transfer.
  **★ THIS IS BRINGING A TEST *TO* ITS FIELD STANDARD, NOT PAST IT** — the distinction CLAUDE.md §5 draws, and
  it matters because "more replicates" is otherwise the thing that rule defaults **NO** to. The repo's own
  stated RBFE/ABFE standard is *"converged fwd/rev + ~3 independent replicates + honest replicate-SD, not
  MBAR-SE error bars"*; this lane shipped at **one**, and the paper says so in three places. Scope is
  deliberately **3 edges of 18**, not the map — the open cycle is the decision-relevant subset.
  **Price, DERIVED not typed:** `realised_usd` **$73.79** over `n_computable` **18** edges
  ([`realised-spend.json`](../modalities/realised-spend.json) →
  [`step1-fanout-map.json`](../modalities/step1-fanout-map.json)) ⇒ ~$4.10/edge × 6 edge-replicates.
  **Gate:** the market, on the same buy line as everything else. **NO-GO reading:** if the replicated cycle
  still fails to close, the defect is mapping or setup rather than sampling, and the three edges are
  **withdrawn from the ranked table** rather than carried with a caveat.
- **`[ ]` The generation-matched null's GENERATIVE arm — control (c), the one that addresses the confound
  actually raised** — **$0 prep + PROJECTED GPU (excluded from the pinned total)** · **Added 2026-07-30.**
  The committed control is the **scrambled-objective** arm, which isolates the winner's curse in the
  **SELECTION** step. The reviewer's confound is the **GENERATIVE** one: `denovo_401` was generated
  *conditioned on the NR4A3 pocket*, and the decoy null it beats was generated for no pocket at all.
  ⚠ **The arm that ran cannot exclude it, and the arithmetic says so out loud:** 0 survivors of 191 bounds
  the manufactured rate at **≤0.0157** (rule of three, 95 %) against the real campaign's own **0.0052** —
  **3×** — with Fisher p = 0.5. **Narrowed, not excluded**, and the deliverable table is the one home for that.
  **What control (c) is:** a *fresh* generation into the **NR4A1** metad-opened pocket, then the identical
  generate → developability → dock → multi-snapshot MM-GBSA → best-of-N funnel. Any NR4A3-selective survivor
  it produces is a manufactured false positive by construction, because the molecules were designed for a
  different pocket. **The driver already supports it** (`nr4a3_generation_matched_null.py MODE=prep-manifest`
  → control receptor manifest; `MODE=reduce` folds the result into the same artifact), and the control
  receptor **exists** — `results/nr4a3-matrix/nr4a1-opened.pdb`, the criterion-matched opened NR4A1 conformer
  §2.5 already uses.
  ✅ **THE $0 HALF IS DONE (2026-07-30): the control receptor and its manifest are staged and committed** —
  `results/nr4a3-genmatched-control-c/`, built by `MODE=prep-manifest`. **The paid half is one generation +
  one funnel pass**, and the lane is launch-ready rather than needing a build first.
  ⚠ **AND STAGING IT SURFACED A TRAP THAT WOULD HAVE INVALIDATED THE CONTROL SILENTLY.** The two committed
  NR4A1 artifacts describing this pocket **do not share a residue numbering** — the LANE-13 release ensemble
  carries `cv_residues` in UniProt numbering, the matrix's opened conformer is renumbered — so handing one
  artifact's numbers to the other boxes **ten wrong residues and reports success**, the same shape as the
  positional chain split that cost the NR-V04 covalent panel its entire spend. The box is therefore **not a
  remembered list**: it is re-derived by matching residue **IDENTITIES**, and **exactly one** alignment of 400
  candidates reproduces all ten. One hit is a resolution; several would have been a fit, and a test fails if
  that ever becomes true.
  ⚠ **Priced PROJECTED and excluded from the pinned total**, per §Spending rules 4: the real campaign ran this
  exact funnel, but its cost was never broken out as a ladder line, so there is no completed benchmark leg to
  quote. Price it off the real campaign's ledger before buying it, not off this entry.
  **Gate:** none upstream — it is a control on work already in the paper. **Reading, pre-registered here:** a
  manufactured rate at or above the real campaign's own survival rate means the confound is **not** excluded
  and §2.6/§2.7 keep their current hedges; materially below it means the survival is not a generic funnel
  artifact. **Either outcome is publishable and neither unlocks anything downstream.**
- **`[x]` TIER-0 · NR4A paralogue-UNIQUE reactive-residue map — DONE 2026-07-24 · $0 · GATE PASS/GO.** Full-length
  UniProt (P22736/P43354/Q92570/Q01844) + dual-aligner agreement + matched-model geometry
  (`nr4a_paralogue_unique_residues.py`, 15 unit tests, run on CI because the sandbox proxy blocks UniProt).
  **4 NR4A3-unique cysteines** (2 exposed) ⚠ *out of **20** enumerated — the other 16 are SHARED, and uniqueness here is enumerated **ONE-WAY only**: the reciprocal handles (both paralogues carry C534 where NR4A3 has S565; NR4A1 carries C551) are absent from the JSON*: **C397** — NR4A1 N363 / NR4A2 S363, RSA 0.395, **10.9 Å** from the
  cryptic pocket (exit-vector reach) — plus C420 (18.3 Å, RSA 0.311), C559 (12.8 Å but RSA 0.095, buried in this
  conformer), C166 (outside the LBD). **4 NR4A3-unique lysines** (3 exposed in the LBD): **K572** (RSA 0.879,
  11.5 Å), **K518** (0.413, 13.4 Å), **K592** (0.506, 16.2 Å), K178 (outside). Reciprocal check reproduces the
  NR-V04 Leg-0 exactly (NR4A1 C551 → NR4A3 T579) and completes it: NR4A1 has 5 cysteines NR4A3 lacks. K85/K194
  excluded on aligner disagreement. EWSR1 fusion moiety contributes only 1–2 lysines → **fusion-lysine axis is
  thin, not a design axis**. This is the FIRST gate in the ladder — it costs nothing and it decides what 5a
  optimises. *(Open, cheap: the matched NR4A1/2 MD-ensemble add-on should report the **distribution** of C397
  exposure, not one frame's 0.395 — and could reopen C559.)*
- **`[x]` NR4A differential surface atlas — DONE · $0 · GATE PASS/GO.** Matched Shrake–Rupley SASA + BLOSUM62
  alignment over NR4A{3,1,2} opened models → **46 differential-surface handles** (exposed × divergent ×
  character-changing), 15/15 LBD lysines exposed; per-residue identities reproduce the canonical map 148/148. A
  differential surface exists to steer an E3 against (distinct from the ~70 % pocket hotspot), so the 5a
  orientation-basin search is warranted. *(Optional add-on: matched NR4A1/2 MD ensembles ~$10–40 to test which
  handles survive dynamics.)*
- **`[!]` NR-V04 retrospective — preregistered holdout — ★ HELD 2026-07-25: IT COULD NOT HAVE RETURNED A
  VERDICT UNDER ANY PHYSICS, TWICE OVER** — **~$24 ($5.6–78; repriced from ~$21 onto the 2800-iteration basis)
  · Cum. ~$107.**
  A **$0** pre-spend audit (`nrv04-retrospective-prespend-audit-2026-07-25.md`) found **two independent, silent
  blockers**, each of which would have consumed the whole spend and read post-hoc as a result:
  - **(1) The collector read keys the driver never writes.** `retro_collect` read `d["R1"]`/`d["R2"]`; the
    driver writes **`R1_interface` / `R2_recruitment` / `R3_lys`**. Controlled reproduction through the *real*
    collector: **24 flawless legs → every `e1_plateau_A` None → every leg `technical_failure` → every arm
    underpowered → `tier: INDETERMINATE`.** Corroborated on real artifacts — **19/19 leg JSONs carry
    `R1_interface`, 0/19 carry `R1`**, and two other in-repo consumers read the correct key. **The existing
    tests could not catch it**: they feed the gate `e1_plateau_A` directly, so the driver→collector boundary was
    never crossed. Fixed, with a schema guard that refuses a verdict when legs land, none blow up, and none
    yield an endpoint.
  - **(2) The covalent R2 arm is unbuildable — and it BLOCKS R1 rather than merely costing an arm.** AMENDMENT
    2's finding reproduces on *independent* models: at the preregistered C551, `retro_cov_nr4a1`'s three pinned
    models measure **34.42 / 29.87 / 39.11 Å** against the 8.0 Å limit, so `build_system` **raises**. The raise
    happens *before a leg JSON is written*, so those 6 units never land, **`panel_complete` stays False and §4f
    suppresses the R1 contrast permanently.** The two blockers are **sequential, not alternatives**.
  **Cleared, and verified rather than assumed:** the nm/Å unit error, the positional chain split and the input
  contamination are **NOT** inherited — confirmed on **all 9 models**, including the **6 NR4A2/NR4A3 co-folds no
  prior audit had ever measured** (the earlier allowlist skipped them) which feed **12 of the 18 primary legs**.
  **★ AMENDMENT 3 APPLIED (trimcrae-delegated):** R2 **retired** (authorized panel = **R1 only, 18 legs**); the
  §4d extension window corrected from an unreachable `(0.012, 0.05]` to `(0.05, 0.12]`; the **inert** LOMO
  clause demoted to a reported diagnostic (228,543 configurations reached p ≤ α with correct ordering and
  **zero** then failed LOMO); and an **MDE registered** — measured leg-to-leg σ **0.855 Å**, 80 % power only at
  **1.5–2.0 Å**. Non-rescue: **no result exists to flip**, and defects 1/3/4 all tighten while 2 can only add
  work to already-non-concordant results. **Net, the retrospective can claim LESS than before.**
  ⚠ **And a limitation that is not a bug:** R1's arms are **not matched in ligand placement, with the asymmetry
  running against the hypothesis** — warhead↔target contacts at t=0 are NR4A1 **47** vs NR4A2 **106** / NR4A3
  **73**, i.e. *the spared paralogues start better engaged with their target*, and the designated **pilot leg**
  (`nrv04-descriptive-v4/nr4a2/seed_1`) starts with a **1.05 Å heavy-atom overlap**. A null R1 remains a
  registered outcome, but it licenses *"did not resolve a difference of the size this design can detect"* — **not**
  "selectivity is localised to warhead reactivity", which stands on Leg 0 + Zhang 2018 alone.
  **Price, two different objects wearing one name:** the ~$21 line was **Arm F (alchemical)**, which the prereg
  does not authorise and which is blocked — repriced **~$24 ($5.6–78)**. What a GO would actually spend is
  **Arm E: 18 legs ≈ $7.7** at the measured $0.43/leg.
  *(Original entry retained below for the frozen gate wording.)*
- **`[ ]` NR-V04 retrospective — preregistered holdout** — **~$21 ($4.8–67) · Cum. ~$104.** Full ensembles
  through the pipeline, no tuning, epimer control; report directional concordance only.
  **★ GATE RECONCILED TO THE PREREG, 2026-07-30 (trimcrae go; [Open decisions 12](#open-decisions)) — ARM E
  RUNS, ARM F STAYS BLOCKED.** ⚠ *Superseded, retained: **"Gate: Val B-full + NR-V04 feasibility + Step 1
  fan-out"**, applied to the WHOLE item.* That wording was **this file's, not the prereg's**, and the two had
  disagreed since 2026-07-24: the prereg blocks only **Arm F** (the free-energy arm) on the valB PASS, prices
  **Arm E** (R1, 18 legs — *(count SUPERSEDED by prereg AMENDMENT 4, 2026-07-31: **16 legs** — `nr4a3` co-fold seed 3 excluded by measured input fault)*, ≈$8) inside the standing ≲$50 autonomy threshold, and its **§9 "Dependency honesty"**
  had already argued — before any leg ran — that running Arm E is a *narrowing* rather than a gate jump,
  leaving the judgement explicitly open. **The prereg got there first; this is that judgement being taken**, and
  it is recorded as a dated addition in the prereg itself, amending no criterion. What changed since is only the
  premise: `step1_fanout` **completed** and the feasibility panel was **WITHDRAWN**, so two of the three listed
  gates stopped being pending and became unreachable. **HARD PRECONDITION, met:** the shared driver now persists
  a durable trajectory (`md_analysis_traj.py`) — do not launch 18 legs on a build without it.
  **It no longer gates the causal kill-switch** (lever 4).
  **GO/NO-GO:** at least directionally concordant with the NR4A1-degraded / NR4A2·3-spared outcome → GO to the
  prospective ladder; discordant → the ladder is not justified, publish the honest negative. **Interpret with the
  covalent confound explicit:** NR4A1 Cys551 is unique to NR4A1 (NR4A3 T579), so a concordant result may be
  recovering *target engagement*, not ternary cooperativity — which is why this is a biological holdout and
  SMARCA2/4 is the method calibrator.
  **State: fully built + preregistered + unlaunched.** Because the covalent confound is *measured*, the panel
  **decomposes** — **R1** (primary, all-non-covalent NR4A1/2/3) tests whether the workflow discriminates
  paralogues with the warhead held off; **R2** isolates warhead chemistry; **R3** (epimer) is conditional. **A
  null R1 is a registered, publishable outcome**, not a method failure. Three infrastructure defects (kernel OOM,
  error-swallowing monitoring, the 25-input dispatch cap) are fixed in code and **unproven on hardware**, so the
  next launch is a **pilot, not a fan-out**.
  **Resume here: [nrv04-retrospective-handoff-2026-07-24.md](../modalities/nrv04-retrospective-handoff-2026-07-24.md)**
  (exact commands, cost ledger, traps) · prereg
  [nr4a3-nrv04-retrospective-prereg.md](../modalities/nr4a3-nrv04-retrospective-prereg.md) · its co-folding
  moved off SageMaker onto the Vast lane
  ([provider-deviation-2026-07-24.md](../compute/provider-deviation-2026-07-24.md)).

### RUNG 5 — mechanism-first prospective ladder *(the flagship, gated mid-ladder by the causal kill-switch)*

- **`[x]` 5a · Orientation-basin search, mechanism-first — DONE 2026-07-25, $0 REALIZED · TIER-2 GO (CATEGORICAL)** — **~$0 realized (budget was $0–50; the optional MM-GBSA rescore was NOT run and is recommended against — it refines the axis mechanism-first demoted) ·
  Cum. ~$129.** Broad transform sampling across the **widened ligandable E3 set** (VHL, CRBN, cIAP1/BIRC2, DCAF1,
  DCAF15, DCAF16, KEAP1, FEM1B, RNF114, MDM2 — free at CPU. **★ RECRUITER STAGING + THE MANDATORY ≤2 DOWNSELECT
  ARE DONE, $0 (2026-07-25): CRBN (9CUO) + VHL (9GIO) advance — VHL as a labelled *backfill*, not a co-winner —
  and the full dropped set is logged with reasons**, none of them availability. Engine
  `e3_recruiter_staging.py` → [`e3-recruiter-staging.json`](../modalities/e3-recruiter-staging.json);
  consumer API `load_advanced()`, whose `anchor_xyz` / `exit_direction` / `caveats` fields are the contract the
  basin search consumes. **The remaining 5a work is the orientation-basin search itself.** Two constraints it
  inherits: the E3-breadth widening **confirmed the incumbents rather than displacing them** (structural
  stageability, not availability, is the binding limit — see item (c) above), and the downselect is **blind to
  recruiter-intrinsic pharmacology**, which is a required input to the next gate). **★ Availability answered $0 and it does NOT constrain the choice** (CI run 30125742542): all 8
  widened arms are broadly expressed and record-complete on HPA (`nr4a3_e3_expression.py`, extendable to any
  further candidate), every symbol resolved through HPA's own search with an exact-match guard — same verdict as
  the original VHL/CRBN check. So the downselect must be made on
  **ligandability + interface geometry**, never on availability, and **no recruiter may be dropped with "not
  expressed" as the reason.** Matched 3-paralogue scoring **over the warhead-pose ensemble**; cluster into ~3–8
  basins/ligase; score with the two **categorical** terms (a) and (b) above, then the cheap counterfactual screen
  to nominate marginal wedges.
- **`[~]` 5a-KS · Wedge confirmation — pilot-first KILL-SWITCH + causal RESULT** — **~$23 ($3.1–97) · Cum. ~$152.**
  ★ **FOUR ternary legs — n = 2 SEEDS PER ARM (trimcrae go, 2026-07-30; [Open decisions 11](#open-decisions)).**
  ⚠ *Superseded, retained: **~$12 ($1.6–45) · Cum. ~$141**, which was the TWO-leg configuration — at one seed
  per arm `S` has no replicate SD and cannot report a null, which is its own pre-registered likely outcome.*
  **`[~]`, not `[ ]`: both ternary legs HAVE run and their checkpoints are durable** (NR4A3 `production/800` of
  2000, NR4A1 `warmup/640` of 1600). They are **PARKED, not finished** — see the IN FLIGHT board for why, and
  for the price condition that re-enables them. `[ ]` would say no work exists; it does, and it is banked.
  **PRIMARY: the ligand-side double difference.** Pilot ONE matched pair first:
  `S = ΔΔG_coop(d₀→d | NR4A3) − ΔΔG_coop(d₀→d | NR4A1)`, ternary legs only (lever 2), on the lane Val B
  calibrates. ⚠ **"No discrimination ⇒ STOP" is SUPERSEDED — see the Tier-3 semantics box under §The hard
  kill-switch.** `S` is **non-covalent**, so it tests the **marginal** wedge only and is structurally incapable
  of testing the **categorical** mechanism Tier 2 actually passed on. **`S` ≈ 0 ⇒ the marginal wedge is absent
  and the claim rests on the categorical axis alone; STOP only if the categorical axis has ALSO failed.**
  Discrimination ⇒ extend to NR4A2 and to a second design element.

  **★ THE MATCHED PAIR IS DESIGNED (RUNG 5b, 2026-07-25, $0) — 5a-KS is now buildable.**
  **`crbn|M0` at its term-(a) exemplar**, wedge **3-(3-pyridyl)-L-Ala (*d*) vs
  L-Phe (*d₀*)** at **Thr407** — Leu in NR4A1, Val in NR4A2, so the H-bond **donor is removed in BOTH**
  paralogues. Backbone length, chain strain, E3 clearance and heavy-atom count are stated **once**, in the
  §WHERE WE ARE 5b block above ("The pair stands; the shared-LENGTH reading does not"); the mechanical point
  here is only that the clearance keeps the wedge **off the E3 interface**, so the shared **binary and solvent
  legs still cancel exactly** and only **ternary** legs are needed. ⚠ **The wedge pair and the covalent series
  do NOT share one molecule** — the placement hosts both, but the covalent series sits at 14 backbone atoms and
  the wedge pair at 19. ⚠ *The reason this block **originally** gave — "a single chain carrying both needs 16,
  which the segment grid cannot build (LANE 14 delta L14-7)" — is superseded; the measured blocker is the
  one-pendant chain template, and the §WHERE WE ARE 5b block is its one home.*
  *Differs only in the wedge element:* one atom (C–H→N), identical formal charge, heavy-atom count, rotatable
  bonds and (S) centre.
  **A geometry-only pick would have been wrong**, and the preregistered rule that replaced it is worth keeping:
  geometry alone selected I396 (12.6 Å) — but a pyridyl N against **isoleucine** is desolvation with no
  compensation *in any paralogue*, so `S` would have been ≈0 **by construction**. Rule now: **NR4A3 must present
  a donor and both paralogues must not.**
  **Honest expectation, recorded BEFORE the run:** NR4A1 offers *absence*, not a penalty, so the expected effect
  is an **NR4A3 gain bounded by roughly one partly-buried H-bond (~0.5–1.5 kcal/mol)** — an effect that
  **straddles** the resolvable difference now carried in §MECHANISM-FIRST instead of sitting under it, so **a
  null is PLAUSIBLE and, at an adequate replicate count, INFORMATIVE.** ⚠ *The clause that stood here —
  "against 1.12 resolvable — i.e. A NULL IS LIKELY" — quoted a resolvable figure that has since been measured,
  and is superseded ([Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 53). The pre-registered
  READING of a null is unchanged; only its informativeness moved.* ⚠ **And the replicate count is now the
  binding design question, not the price:** as parked, the lane is **one seed per arm**, at which `S` resolves
  only the TOP of its own expected range — see [§WHAT THE LANDED RESULTS
  CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) 3 and [§Open
  decisions 11](#open-decisions).
  Fallback fully enumerated and RDKit-verified: `vhl|M3` representative, 11 atoms,
  T407, 10.3 Å — **C52H65N9O9S vs C53H66N8O9S** *(per `nr4a3-linker-library-chem.json`; an earlier C₄₇H₅₅N₉O₉S / C₄₈H₅₆N₈O₉S with "66 heavy atoms" disagreed with the artifact and is superseded — the equal-heavy-atom property holds, the formulae were wrong).*
  *Remaining confounds:* modelled rotamer; double conditionality; unmeasured linker-conformer populations. **Evidence grade:** a NO-GO may be taken on
  valB_mini-grade evidence (stopping is the conservative action), but a POSITIVE result stays **exploratory**
  until valB_full passes.

  **CONFIRMATORY second line — the reciprocal PROTEIN-mutation cycle. ENGINE QUALIFIED 2026-07-25; cost
  PROJECTED, not measured on NR4A.** Pilot ONE direction (3→1); loss ⇒ complete the reciprocal cycle
  (3→2 + reciprocal 1/2→3).

  *Engine:* **pmx + GROMACS** (Gapsys & de Groot) — the published, field-standard *free* engine for
  protein-mutation FEP. perses was retired the same day it was tried: its core protein-mutation path builds the
  old→new residue atom map by round-tripping each residue template through an **OpenEye OEMol**
  (`PolymerProposalEngine.generate_oemol_from_pdb_template` → `oechem.oemolistream`), which is commercial and
  licence-gated, with no conditional and no RDKit alternative on that path. Cost of establishing that dead end:
  **~$0.05.** Everything around the engine was engine-agnostic and survived the swap: staging with a
  mutation-site refusal, the SKEMPI-verified references, scoring, the verdict, and the Vast lane. Code:
  [`Dockerfile.pmxfep`](../compute/Dockerfile.pmxfep),
  [`protfep_pmx.py`](../modalities/protfep_pmx.py),
  [`protfep_run.py`](../modalities/protfep_run.py),
  [`protfep_bench.py`](../modalities/protfep_bench.py),
  [`protfep_reduce.py`](../modalities/protfep_reduce.py),
  [`protfep_refcheck.py`](../modalities/protfep_refcheck.py), `gpu-protfep-vast.yml`; plan in
  [protfep-pmx-plan.md](../modalities/protfep-pmx-plan.md). **Most of the ladder is $0** — stage-test,
  refcheck, bake and a build-test that runs the ENTIRE hybrid construction on a CPU runner; a host is rented only
  once a hybrid demonstrably builds.

  *Known-answer benchmark — PASSED* (full set on Vast, equilibrium λ windows + BAR, scored by `protfep_reduce`
  against SKEMPI 2.0-verified references; artifact
  [`protfep-benchmark-result.json`](../modalities/protfep-benchmark-result.json)):

  | benchmark | computed ΔΔG_bind | reference | abs err | within ±1.5 |
  |---|---|---|---|---|
  | barnase–barstar **Y29A** (hot spot) | **+4.424 ± 1.077** (3 complex × 3 apo) | +3.40 | 1.024 | ✔ |
  | barnase–barstar **Y29F** (near-null control) | **−0.370 ± 0.175** (3 complex × 3 apo) | −0.13 | 0.240 | ✔ |

  **Ordering correct** (Y29A ≫ Y29F), which is the test that matters — a wedge is read as a ranking, so a
  magnitude pass with the ordering wrong is a fail. The near-null control did its job: the engine returned
  ≈−0.37 where the experiment sees ≈0, rather than inventing an effect. Both mutations are charge-conserving, so
  engine error is not confounded with the net-charge artifact. `plan_wedge` may now stamp `validated: true`.

  **★ THE MOST DECISION-RELEVANT RESULT IS THE NOISE STRUCTURE, NOT THE AGREEMENT.** At full replication the
  between-setup scatter differs by **6.2×** between the two benchmarks (±1.077 on the +4.4 hot-spot knockout vs
  ±0.175 on the near-null), while *within*-leg MBAR standard errors are 0.05–0.13 kcal/mol in both — an order of
  magnitude smaller. So this is **setup/equilibration variance, NOT insufficient sampling**: running each leg
  longer would not fix it; running more legs would. Two consequences:
  1. **A single leg does not determine a number.** Y29A's mean walked 2.851 → 3.951 → 4.025 → 4.424 as
     replicates landed, and its error against the reference *grew* (0.549 → 1.024). Replicates are mandatory.
  2. **The wedge's own regime is the well-determined one.** The wedge measures a *small* induced-interface
     difference (the best-case resolvable figure lives once, in §MECHANISM-FIRST — this line deliberately does
     not restate it, and the value it **originally** carried is retired there) — exactly where this engine reproduces to ±0.18, not the
     ±1.08 the hot spot suggests. Encouraging for the wedge, and it means **the right validation for 5a-KS is a
     benchmark sized like the wedge**, not a hot-spot knockout. **That benchmark does not exist yet**, and until
     it does the confirmatory line may not claim to resolve a paralogue-scale difference.

  *Price:* **measured 1.058 ± 0.432 GPU-h/leg** over 11 legs (range 0.379–1.8) at a 25,187-particle mean,
  **$0.212/leg** at the $0.20/hr assumed in the reducer → a **PROJECTED** wedge of **~$4.6 (3 replicates)** /
  ~$3.1 (2 replicates). The projection is a **linear particle-count scaling** from 25,187 to the NR4A sizes — an
  assumption, not a measurement, so it may not be quoted as a rate and the confirmatory line stays **excluded
  from the pinned ladder total**. The per-leg GPU-h SD (0.432 on a mean of 1.058) is **host variance, not
  physics** — two hosts rented minutes apart differed ~10× in throughput per particle.

  *Two blockers, both cleared in code before any leg runs*
  (planning layer: [`nr4a3_protein_fep.py`](../modalities/nr4a3_protein_fep.py), whose wedge subtraction
  delegates to `ternary_coop.ddg_coop` so there is **one** definition of the cycle in the repo, not two):
  - **Cross-lane charge mismatch.** `assert_charge_consistency` hard-fails any wedge whose ternary and binary
    legs charge the ligand differently. An un-pinned wedge is not a thermodynamic cycle, so this is a refusal,
    not a warning. Pin NAGL across both legs (the only method that can charge both a small mutation edge and a
    PROTAC-scale assembly) and stamp it into both result JSONs. Cost: $0.
  - **Net-charge-changing mutations, and it bites immediately.** **R412 is one of our own seven selectivity
    handles, and R→A is charge-changing** — exactly what PME cannot do naively (the neutralising background
    plasma shifts the electrostatic free energy by a system-size-dependent amount that does not cancel between
    the differently-sized ternary and binary boxes). `plan_wedge` refuses a charge-changing mutation unless an
    explicit correction strategy is chosen. **Prefer a charge-conserving handle (L406/T410/I484/I531/L534) for
    the FIRST causal test.**

  *Declared physics deviation:* 2 fs with a 1 fs warmup, not the canonical 4 fs+HMR. Softcore regions are where
  the ternary lane NaN'd, the timestep is empirical with no static predictor, and on a new engine's first leg a
  NaN costs the whole rental while 2 fs costs ~2× the iterations of a sub-dollar leg. Escalate only after this
  lane survives a full NR4A-scale leg — and record it; do not assume it transfers.

  *Sequence, cheapest-decisive-first:* smoke (~$0.10) → pilot (both legs of one direction, ~$1–3 — **the abort
  gate**) → full set (~$5–10) only if the pilot sees it.

- **`[x]` 5b · TWO-MECHANISM REACH — DIAGNOSED 2026-07-30, $0, AND THE ANSWER REFUTES THE QUESTION.**
  Added and closed the same day. The item asked whether a finer segment grid could build one chain carrying
  both the covalent electrophile (→C397) and the causal wedge (→T407). **It cannot, and a finer grid was never
  the issue.** Numbers and the refutation live once, in the §WHERE WE ARE 5b block above; the plan-level
  consequences are here:
  1. **The blocker is the chain TEMPLATE, not the grid** — one `pendant` slot, one branch residue. **That is a
     one-line signature, and it means every sweep over segments and lengths was searching a space that
     structurally cannot contain the answer.**
  2. **A two-branch template is constructible at n = 18 with the segments already in the grid**, so the fix
     costs no new chemistry — but it is a **DESIGN change to a preregistered enumeration**, not a defect fix,
     so it does **not** qualify under the amendment standard that covers a statistic shown to lack
     discriminating power. **It needs an explicit decision, and it is not taken here.**
  3. **The pre-registered NO-GO reading half-fires, and the honest report is the half that did.** It said: *if
     no admissible branch exists either, the limit IS geometric and that is the finding.* One exists in
     principle; what does not exist is a template to hold it. **So the paper's statement is neither "a grid
     limit" nor "geometry" — it is that the enumerated architecture carries one mechanism per molecule**, which
     is a real and reportable constraint on the design as enumerated.
  ⚠ **The existing library is untouched and nothing in it is invalidated** — the diagnostic re-enumerates
  nothing, and a test asserts that.
- **`[x]` 5b · THE TWO-BRANCH TEMPLATE — BUILT 2026-07-30, $0 (trimcrae: *"use your judgement"*). ONE molecule
  CAN carry both mechanisms, there is EXACTLY ONE way to do it, and it is not free.**
  [`linker_twobranch.py`](../modalities/linker_twobranch.py) →
  [`nr4a3-linker-twobranch.json`](../modalities/nr4a3-linker-twobranch.json), 10 tests, RDKit-verified
  **16/16**. **The preregistered enumeration is UNTOUCHED and a test asserts it is byte-identical after a full
  run** — this is a SEPARATE artifact and an additive extension, not an amendment. **It unlocks nothing
  downstream** and no gate, verdict or existing construct changes.
  - **★ THE SOLUTION IS A POINT, NOT A REGION — and that is as much the finding as the molecule.** Scanning
    every (SEG1, SEG2, SEG3, warhead) against the windows the committed library actually recorded, **exactly
    one chain** satisfies both at the same length and placement: **n = 18, term-(a) exemplar, a2–a2–a2, the
    5-amide warhead**, electrophile at **k = 13**, wedge at **k = 6**. Change any one segment and one of the
    two windows breaks. A two-mechanism design here has no room to be optimised.
  - **⚠ AND IT COSTS REAL PROPERTY SPACE — reported because it is the honest half.** Against the committed
    single-mechanism library (same chemistry, same handles): **median +10 heavy atoms and +120 Da**, with the
    top of the set at **1248 Da**, *above the entire committed range* (698–1099). That is well into where
    permeability rather than affinity is the binding problem. **So this is a demonstration that the two
    mechanisms CAN be carried on one chain — NOT a claim that the molecule is developable**, and the paper
    must frame it that way.
  - **Claim ceiling, in the artifact:** *constructible and window-admissible against TRANSFERRED windows*. The
    windows come from **single**-branch records; `branch_position_window` is a function of (endpoints, target,
    length, reach) and **not** of branch count, so the transfer is sound — **but no two-branch chain has had
    its own window computed**, and this may never be reported as though one had. No docked pose, no strain, no
    basin-fidelity filtering, no energetic or selectivity quantity of any kind.
  - **Why building it was the right call rather than scope creep:** $0, additive, and the *existing* filters
    and windows decided the outcome rather than my judgement — I put no thumb on the scale. It converts
    *"unknown because inexpressible"* into a measured answer with a stated cost, which is what the deliverable
    (a candidate set with an identified causal mechanism) needs in order to say whether one molecule can carry
    both. **What it does NOT do is make the 5a-KS matched pair two-mechanism** — `S` must isolate a single
    structural element, so the causal test article stays exactly as designed.
- **`[x]` 5b · Inverse linker design — DONE 2026-07-25, $0 REALIZED (1,995 enumerated → 21 retained, RDKit-verified 21/21)** — **~$0–20 (mostly $0 CPU) · Cum. ~$162.** For each confirmed basin, derive
  linker requirements (endpoint distance, exit-vector dihedral, strain, reach), enumerate a virtual library,
  filter by basin fidelity, annotate exact structures + synthetic feasibility → **~12–20 virtual constructs** (the
  reviewer's "24–36" now bounds this virtual set, not a hand-built grid). For basins carrying the covalent handle,
  the library enumerates the **electrophile position on the linker** as a design variable, and **prefers
  reversible-covalent** chemistry.
- **`[ ]` 5b-T · Rebuild the NR4A1/2/3 ternaries by the ASSEMBLY route, from a SMILES-recorded degrader, then
  read them with `V1`** — **$0 · Cum. ~$162 (unchanged).** **Added 2026-08-02.** Serves `R9` → `R10` `R11`;
  runs `V2` (assembly route) then `V1` (descriptor) — **each recovered its own known answer in scope, and
  neither is validated on this system** — and **inherits `R5`, which is unresolved.** ⛔ **This closes the program's largest unpriced gap** — the rebuild was prose only,
  in no rung, no spine row and no decision-value rank, and an item with no rung cannot be scheduled, refused
  or costed.
  **Price, DERIVED not typed — one home:** [`ternary-rebuild-cost.json`](../modalities/ternary-rebuild-cost.json),
  regenerated by [`ternary_rebuild_cost.py`](../modalities/ternary_rebuild_cost.py) and checked by
  `--check` + `tests/test_ternary_rebuild_cost.py`. **It buys 0.0 reference GPU-hours**, so it is $0 at any
  planning rate and **the pinned ladder total does not move**; the rate is read from
  [`vast-ladder-repricing.json`](../modalities/vast-ladder-repricing.json) rather than retyped. The wall-clock
  figure it derives is a **floor**, not an estimate — the per-arm seconds come from a bromodomain+VCB system
  and this one is larger.
  **What runs:** DeepTernary at the frozen commit, patched to CPU at 16 seeds, over **5 arms** — two harness
  positive controls (6HAX VHL, **and 6BN7 CRBN, because this rung's E3 is CRBN and a VHL-only control does
  not cover it**; both are inside the model's data horizon and so control the harness and never
  generalisation) and the three paralogue arms — then `nr4a_ternary_signature.py` over **all 16 models per
  arm**. Inputs, artifacts and the pre-flight snap-mask assertion that stops the empty-mask failure two dead
  runs already paid for: the `spec` block of the cost artifact.
  ⛔ **The degrader's SMILES is recorded this time.** It is taken from
  [`nr4a3-linker-library-chem.json`](../modalities/nr4a3-linker-library-chem.json), which carries a
  `canonical_smiles` and an `inchikey` per construct. The existing ternaries are unusable as evidence for
  exactly this reason: their molecule cannot be recovered from any of the three models, so no replicate can
  ever be matched to them.
  **GO/NO-GO — PRE-REGISTERED, three arms, all three needed. Full criteria and their nulls: the `gate` block
  of the cost artifact.** **(A)** at least one discriminating position whose **aligned residue itself
  differs** in both comparators — same-residue positions are placement artifacts and count for nothing, which
  is what five of the earlier six were. **(B)** that position present in **≥12 of 16** models on the NR4A3 arm
  and **≤4 of 16** on **each** comparator; under a per-model coin-flip null each tail is one-sided binomial
  *p* = 0.0384. Anything between is **INDETERMINATE**, a third outcome and not a pass. **(C)** the assembled
  ternary must **preserve the tether geometry the categorical axis depends on** — a ternary that only
  assembles by lengthening the effective tether past the paralogue-collision knee has traded away the
  property it exists to exploit, and that is **NO-GO, not a caveat**. ⚠ **Arm (C) is registered as AT RISK
  before the rung runs:** no committed construct sits at or below 12 backbone atoms (the shortest is 14), and
  the only CRBN basin in the confirmed set misses the 12-atom gate by construction. A $0 RDKit re-enumeration
  is the named way out; if it returns nothing buildable the rung runs at the shortest committed length and
  **carries the measured collision bracket** instead of claiming the 12-atom figure.
  ✅ **THE NAMED WAY OUT WAS TAKEN, 2026-08-03, AND IT ANSWERS ARM (C) PARTLY IN THIS RUNG'S FAVOUR AND PARTLY
  AGAINST IT** ([`nr4a3-short-linker-probe.json`](../modalities/nr4a3-short-linker-probe.json)). **(i)** The
  premise *"nothing exists at 12"* is false — a construct exists, is named, has a SMILES and an InChIKey, and
  clears the gate under both reach conventions; the library's floor of 14 turned out to be a basin-**breadth
  policy** rather than geometry or chemistry ([§8 Route B](#route-b--a-linker-borne-covalent-handle-at-an-nr4a3-unique-cysteine---blocked-on-r5-nothing-running--serves-r8-r15)).
  ⛔ **(ii) But it is a VHL construct and THIS RUNG'S E3 IS CRBN.** The best CRBN construct at the gate reaches
  C397 **through-space only**; under the corridor convention its floor is **14**, above the gate. So arm (C)
  stays AT RISK for CRBN, and the fallback stands as written — run at the shortest committed length and carry
  the measured bracket. ⛔ **(iii) And before either, the SMILES provenance has to be settled:** this rung
  takes its degrader from `nr4a3-linker-library-chem.json`, which is generated from
  `nr4a3-linker-design.json`, **which no longer reproduces from its own generator** —
  [§10.1 row 25](#101--open-rows-ordered-by-what-unblocks-the-most). That is a $0 decision and it belongs
  *before* the run, not after it.
  **Refusals, not results:** an empty snap mask or an infeasible embed is **REFUSED**, never reported as a
  zero; a failed positive control makes the whole run uninterpretable; fewer than 3 models on any arm and no
  reproducibility statement is made in either direction.
  ⛔ **Scope, up front:** this yields **structural** evidence — *these modelled interface contacts differ
  between paralogues* — and never thermodynamic. It computes no free energy, so it cannot say anything binds
  more tightly, and it does **not** discharge `R12` or the free-energy requirement. `V1` recovered one contact
  in one pair and no more; `V2`'s post-horizon pass is one arm on a VHL/bromodomain system, and nothing at all
  covers a CRBN ternary with a nuclear receptor, which is what this rung assembles; every model here is an
  isolated LBD, so `R13` is untouched.
- **`[ ]` 5c · Explicit ternary-ensemble refinement** — **~$21 ($1.9–85; endpoint MD, 24–~200 legs at ~1.38 ref
  GPU-h each) · Cum. ~$183.** *(The biggest swing item — the leg COUNT, not the rate, dominates its uncertainty.)*
  Replicated ternary + full CRL/E2~Ub MD across target states, linker conformers, and in-basin poses; matched
  NR4A1/2/3; separate accessibility from stability; robust constraint-satisfaction filtering → **~4–8 constructs**
  nondominated under scenario + model uncertainty. Add a constraint: **which lysine the ubiquitin actually
  reaches**, reported per construct as a distribution over unique-vs-conserved sites, not just "a lysine is near".
- **`[ ]` 5d · Local ternary FEP** — **~$21 ($3.1–87; 3–6 ternary comparisons) · Cum. ~$169.** Alchemy **only**
  within a retained basin (both endpoints plausibly bound, modest congeneric change). Refines the matched final
  series → **~6–12** with ≥2 mechanistic wedges, ≥2 linker architectures, VHL/CRBN only where both survive,
  explicit negative controls. **Deliverable** = the prioritized, structure-defined, retrosynthetically annotated
  candidate set with an identified causal selectivity mechanism — degradation experimentally unvalidated.

### RUNG S — the two SCOPE rungs (`R13`, `R14`): claim-ceiling conditions, deliberately OFF the `Cum.` chain

*★ **Added 2026-08-03, closing [§10.1](#101--open-rows-ordered-by-what-unblocks-the-most) rows 9 and 10** — two of the five rows that had **no rung, no gate and no price anywhere in the program.** ⛔ **All four items below are EXCLUDED from the pinned ladder total**, in exactly the way [pricing.md §C](../compute/pricing.md) excludes the 5a-KS confirmatory wedge and the reciprocal mutation cycle: they are **claim-ceiling conditions**, not steps of the gated 5a→5d spine, and **no rung's GO gates them.** So each carries a **Price** and deliberately **no `Cum.`** — folding them into the chain would silently move a total `vast_cost_model.py` derives. Every figure here is **DERIVED, never typed**, and its one home is [`scope-rung-cost.json`](../modalities/scope-rung-cost.json) (`python3 research/modalities/scope_rung_cost.py --check`), priced off the **live** market rate in [`vast-ladder-repricing.json`](../modalities/vast-ladder-repricing.json) so these rungs move with the ladder instead of freezing a rate.*

- **`[ ]` `R13-a` · Fusion-junction SEQUENCE inventory, at the CORRECTED junction** — **$0 (0.0 ref-GPU-h) · needs no nod · CI/CPU.** Serves `R13`. Extend the uniqueness + lysine/cysteine sweep **across the junction** and state explicitly which real residues the modelled LBD construct (373–626) excludes from every geometry claim in the program. ⚠ **Price the CORRECTED object, never the old one:** the exon→residue map was re-derived on 2026-08-03 and NR4A3's first two *transcript* exons are non-coding, so all **7** previously committed junctions deleted the AF1 **and** the first zinc finger of the C4 DBD; the corrected canonical junction is **EWSR1 exon 7 ending at residue 264 :: NR4A3 exon 3 beginning at residue 1** ([`nr4a3-exon-audit.json`](../modalities/nr4a3-exon-audit.json); the guard that makes a repeat loud is `fusion_breakpoints.resume_offset`, which now **raises** on a non-coding exon instead of sliding to a neighbour). **GATE:** a re-derivation that does **not** reproduce `EWSR1(1-264)::NR4A3(1-626)` from exon structure alone is a REFUSAL, not a result. ⛔ It settles **scope, not geometry** — the deliverable is one sentence the paper currently cannot write, plus the confirmation that **C166** is present in the disease protein and absent from every structure here.
- **`[ ]` `R13-b` · Apo co-fold of the two corrected fusion constructs** — **~$0.66 ($0.28–1.67; 5.81 ref-GPU-h, 12 models = 2 constructs × 6 seeds) · 🔒 needs a nod · Vast, baked image.** Serves `R13`. The `seam` and `composite` constructs of [`fusion_cofold.py`](../modalities/fusion_cofold.py), re-cut to the corrected junction. **Basis is MEASURED, not estimated:** the one completed co-fold panel in this repo billed **5.808 ref-GPU-h / $1.0723 over 8 rentals, all on the reference card, for 12 models** ([`selcal-price-ledger.json`](../modalities/selcal-price-ledger.json) → `scope-rung-cost.json` `bases.cofold_per_model`), and that basis is an **upper bound twice over** — its system is *larger* (~570 residues vs 380/486, and the co-fold cost is ~N²), and its hours include an environment build on the billing host that [CLAUDE.md §6](../../CLAUDE.md) has since forbidden. **`$/ns` = `—`, and that is an honest refusal, not a missing field:** a co-fold integrates no dynamics, so there is no ns denominator (`inflight_board.unpriceable_usd_cell`); this rung is gated on its **dollar** ceiling alone and a refusal must say which ceiling it hit. **PRE-REGISTERED GATE, written before the run because a null here is the expected outcome:** `fusion_cofold.py`'s own prior is that the EWSR1 side is a prion-like IDR (mean pLDDT 38.8, 98 % of residues < 50) with **no cross-seam coevolution** for an MSA-based predictor to use — so **absence of an ordered composite interface is a FEASIBILITY READ, not evidence that no pocket can form**, and it may not be reported as a refutation. A GO is: an interface cavity present in **≥4 of 6 seeds** on the `composite` construct that is **absent from both parent AlphaFold models** — anything less is INDETERMINATE, a third outcome.
- **`[ ]` `R14-a` · Complete the anti-target panel, and run the self-control it has never run** — **$0 (0.0 ref-GPU-h) · needs no nod · CI/CPU (smina, the identical 24 Å box / exhaustiveness 8).** Serves `R14`. ⚠ **This is an ASSEMBLY job, not a build:** the 47-receptor sequence screen has run and flagged exactly **NR3C2 (MR)** and **AR**, the docking harness has run at panel scale (SI §S1), **AR is already a panel target**, and `denovo_401` is already staged. What is missing is that **MR/NR3C2 is not in [`antitarget_panel.json`](../modalities/antitarget_panel.json)** (a data row; `antitarget_prep.py` **drops** a target whose ligand/chain cannot be resolved, loudly, so a bad PDB pick fails rather than emits a bad receptor) and that the panel has a **never-run cognate-ligand self-control.** **GATE, and it is ordered deliberately:** the self-control runs **FIRST** — each target's own cognate ligand re-docked through the identical protocol — and **until it passes, no anti-target margin from this panel may be read, including the one already published in SI §S1.** ⭑ That is what makes this the higher-value half: a failure would reach a result the paper already carries.
- **`[ ]` `R14-b` · Matched AR/MR cryptic-pocket ensembles (+ the $0 detector)** — **~$3.41 ($1.10–18.65; 29.87 ref-GPU-h, band 23.2–64.7) · 🔒 needs a nod · ⛔ AND CURRENTLY BLOCKED BY THE RATE LINE — see the gate.** Serves `R14`. The SI's *second* requirement: 2 species × (60 ns well-tempered metadynamics + 3 × 5 ns release), the workflow's own declared recipe, then the harmonized detector — which is **$0 CPU once frames exist**, the same $0 re-read that `paralogue-pocket-contrast.json` already performed on the paralogues. **⚠ Its dominant uncertainty is GPU-HOURS, not $/hr:** the measured host spread on this exact workload is **3.1× (146 → 47 ns/day)** and is **host-CPU-bound**, because PLUMED does per-step host-side work — caught on one instance jumping 24–33 % → 74 % `gpu_util` at the metad→release boundary, same card, minutes apart ([pricing.md §A.1](../compute/pricing.md)). So host CPU must enter selection for this rung. **⛔ REGISTERED GATE 1 — DO NOT LAUNCH:** its derived `$0.022758/ns` is **6.67× the ladder basis and 3.48× the approved buy line**, i.e. a row the standing gate **refuses**. ⚠ **That is NOT a drift finding and must not be quoted as one** — the line's basis is the 84,534-particle *unbiased* RBFE benchmark and this is a *biased* leg, so the two `$/ns` have different denominators. **There is no metadynamics-anchored basis in this repo, and until one exists this rung cannot be graded by the rate line at all.** Surfaced now rather than discovered at launch; it is a decision for trimcrae, not a rule to loosen. **⛔ REGISTERED GATE 2 — a $0 precheck that can refuse the spend on evidence, exactly like [§10.1 row 12](#101--open-rows-ordered-by-what-unblocks-the-most)'s did:** the CV is the Rg of **NR4A3's** ten Pocket-5 lining residues, mapped onto the target by BLOSUM62 at runtime. That ran on the paralogues at overall identity **0.51 / 0.58**; **AR and MR sit at ~0.32**, only marginally above the SI's own confidence floor, and the SI itself warns that *"a distant global alignment can mis-register a two-residue run"*. If the aligner does not map all ten CV residues at a stated confidence, **R14-b is REFUSED and $0 is spent.**
- **`[x]` `R14-c` · The ENERGETIC (FEP) half — RULED OUT OF THIS RUNG, on the claim-ceiling rule** — **$0 (a decision).** The SI asks for *"docking/FEP into their LBDs"*. The FEP half **is `V4`'s instrument** — the selectivity ABFE that has never recovered a known selectivity answer across two pockets — so under [§2.3](#23--the-claim-ceiling-rule-stated-so-it-can-be-checked) a number from it could not raise `R14` above *unvalidated prediction*. Pricing it here would create a **second home** for a decision that already has one: [§10.1 row 2](#101--open-rows-ordered-by-what-unblocks-the-most), `V4`'s missing rung. **It is downstream of row 2, not parallel to it**, and that is why this rung is closed rather than costed.

### OPTIONAL / HELD — only if a specific claim needs them AND a budget nod is given

- **`[ ]` ΔG_open per paralogue** — **~$120–300.** Only to make affinity/selectivity *unconditional*; otherwise
  report conditional on the open state ($0, fully defensible).
- **`[ ]` Conditional ABFE (pose-plausibility)** — **~$80–200.** Raw values, T4L discrepancy separate, no offset,
  does not prove binding. **This hold covers the existing ABFE block's λ-overlap repair too** — it is parked, not
  in flight. Launch only with an explicit nod after everything above.

### RUNG 6 — write & ship (~$0)

- **`[ ]` Fold results into paper** — language discipline; QM/torsion validation at linker junctions;
  physicochemical + retrosynthetic assessment; re-render figures.
- **`[ ]` Final red-team + review-response.**
- **`[ ]` Post + submit** — OUTWARD-FACING, needs trimcrae sign-off.

---

## ★★ WHAT THE LANDED RESULTS CHANGE ABOUT THE REMAINING PLAN

*★ **THE REASONING BEHIND THE ORDERING.** Its item 6, the decision-value ranking, is **folded into [§10](#10--the-roadmap--one-ordered-list)** together with this page's old critical path; §10 holds the union of both plus eight rows that were on neither list. Read this for the *why*; read §10 for the order.*

*Written 2026-07-30 8:21 PM ET, with nothing billing and the fixed scope closed.
Everything above this line records what happened. **This section is the only place that says what it means for
what is still UNBOUGHT**, and it exists because most of what follows is a correction to a load-bearing INPUT of
the plan rather than a new piece of work: with the fixed scope closed and nothing billing, the remaining ladder
was still being steered on three numbers that had never been measured and one requirement that was never
implemented. Per rule 1 nothing here restates a figure that has a home elsewhere — each item points at its
home and carries only the CONSEQUENCE.*

**The one-line reading. The program's blocker is no longer precision and is no longer money — it is that the
flagship quantity `S` has never had a known answer, and, as it was parked, could not have reported its own most
likely result.** ✅ **Both halves of that are now acted on** (2026-07-30, trimcrae go): the lane is re-specified
to **n = 2 seeds per arm**, so a null becomes a *bound* rather than a shrug; and the calibrator question is
split so the free half — *can a null be READ?* — no longer waits behind the paid half
([§Open decisions 11 and 13](#open-decisions)). **Nothing is bought: the four legs stay parked behind the
market gate.** What is left below is the reasoning, and the parts that are still open are marked as such.

### 1 · The axis the plan demoted was demoted on an assumption that has since been measured

§MECHANISM-FIRST is the home for the numbers; the strategic consequence is here, and it is a **re-rank, not a
re-order**:

- **Mechanism-first survives untouched.** A categorical handle needs no margin at all, and the categorical
  screens are $0 — either argument alone is sufficient, and Tier 0/1/2 all passed on that basis.
- **But the marginal axis was written off as a *discovery* tool for a reason that no longer holds**, and the
  §Spend summary paragraph that quoted it is corrected in place. Its problem was never really resolution; the
  measured accuracy failure is a *different* defect with a *different* remedy. **Remedy for a blunt tool: more
  sampling. Remedy for an uncalibrated one: a calibrator.** The plan has been buying neither.
- **⚠ The correction cuts against my own reading as well as for it, and both halves must be carried.** A better
  noise floor does **not** make a 2.0 kcal/mol induced-interface margin *exist* — that is a property of the
  designed molecule, not of the instrument. It only means that **if** one exists, this pipeline can now be
  shown to resolve it.

### 2 · The FAIL was measured on the WORST-cancelling form of the quantity; the flagship uses the BEST-cancelling one

The algebra already lives in [`valb_failure_propagation.error_algebra`](../modalities/valb_failure_propagation.py)
and is **not restated here**. What had not been drawn out of it is the planning consequence: `ΔΔG_coop` — the
quantity that failed at 1.543 kcal/mol — differences two environments **that differ by a whole protein chain**,
while `S` differences **one morph of one atom across two homologous pockets at matched ternary architecture**.
They are opposite ends of the same cancellation spectrum, and the program measured the bad end and then priced
the good end as though the result transferred.

**⚠ THIS IS NOT A LICENCE AND MUST NEVER BE QUOTED AS ONE.** *"Not implicated"* is an **argument**, not a
measurement — the file's own words. A per-endpoint error that differs **between the NR4A3 and NR4A1 pockets**
cancels from neither `S` nor anything else this program runs, and no check we own can see it
(`s_resolvability_from_R_ternary._blind_spot_stated`). The correct conclusion is narrow and it is enough:
**the valB FAIL is not a reason to leave `S` unbought — it is a reason `S` needs its own known answer.**

### 3 · ★ 5a-KS AS PARKED CANNOT REPORT ITS OWN MOST LIKELY RESULT — a DESIGN defect, and only the PRICE one is on the board

[`valb_failure_propagation.s_error_bar_scope`](../modalities/valb_failure_propagation.py) computes it and
is the one home: at **one seed per arm** — which is exactly what the two parked legs are — `S` resolves only the
**top** of its own designed effect range. The pre-registered expectation is that the effect sits **inside** that
range. **So the configuration that is parked buys, in its likely case, a number that cannot answer its own
question — the identical defect as valB_mini at n = 1, on the lane that was supposed to have learned it.**

**★ THE $0 CHECK THAT ITEM OWED IS NOW DONE, AND THE ANSWER IS FAVOURABLE.** `s_error_bar_scope` flagged
*"CHECK BEFORE BUYING: whether the 5a-KS co-fold staging has the same seed→model wrap is UNVERIFIED here and
must be checked, not assumed, or the second seed re-runs the first model and buys no independence."* Checked
against the source rather than assumed:

- The wrap that motivated the warning is **`ternary_pdb_stage.py`'s `starting_model_index = SEED % n_models`,
  and it is gated on `target_acc == "P51532"`** — the SMARCA4 template, i.e. the valB calibrator's homology
  substitution. **It cannot reach a 5a-KS leg**, which stages through `nr4a3_5aks_stage` against a CRBN co-fold.
- 5a-KS is **one co-fold per species BY DESIGN** (`nr4a3_5aks_stage` docstring: both endpoints are staged from
  one pose, deliberately, so the alchemical transformation does not have to absorb a pose difference).
- `nr4a3_ternary_fep` seeds each replica's sampler, so **a second seed is genuinely independent SAMPLING**.

**Consequence, stated in both directions.** A second seed **does** buy a real replicate SD — the blocker is
cost, not machinery. It **does not** buy co-fold-pose independence, by construction, so an `S` replicate SD
measures sampling scatter *within one pose* and the pose stays a stated conditional. That is a limit to declare,
not a reason to stay at n = 1: **an error bar that covers one of two error sources beats no error bar at all**,
and n = 1 covers neither.

**The parked row on the IN FLIGHT board was therefore parked for TWO reasons and listed one.** The price gate is
real and its refusal was correct. But `s_resolvability_from_R_ternary` reads **ADMIT** on the landed
`R_ternary` — the *science* gate says buy — so if the market had opened the lane would have resumed **in the
configuration this item calls under-powered.** ✅ **SETTLED 2026-07-30 (trimcrae go): n = 2 seeds per arm.** The
lane now declares four legs, the ladder is regenerated, the stage-cache seeder covers every declared seed and
both new units are watched — all still `enabled: false` behind the price gate, re-enabling together.
[§Open decisions 11](#open-decisions) carries the reasoning and what was NOT chosen.

### 4 · ✅ FIXED — a REQUIREMENT this file adopted had never been implemented on the driver whose loss created it

RUNG 3 records *"the highest-leverage infrastructure change for the whole ternary program (adopted as a
requirement, 2026-07-25): every MD driver must persist a strided heavy-atom TRAJECTORY"*, because the NR-V04
panel's three data-invalidating defects would each have been correctable for **$0** instead of costing a re-run.
**Measured against the source on 2026-07-30, ten months of that requirement had produced nothing on the one
driver that needed it: `nrv04_covalent_md.py` had no trajectory reporter at all** — it reduces in-loop and
discards positions, which is the exact mechanism `nrv04_result_forensics` recorded as
`trajectory_objects_found: 0`. Every other endpoint-MD lane at least writes one — `nr4a3_md`, `nr4a3_metad`,
`nr4a3_md_release` and `nr4a_paralogue_release` all attach a `DCDReporter` into the job's output directory, and
`nr4a_paralogue_release` documents an explicit strided heavy-atom persist. ⚠ **Stated at what was actually
checked: that is a reporter, not an audited end-to-end persist for all four** — the claim here is only that the
lane which lost everything had no reporter at all.
**And the NR-V04 retrospective SHARES THAT DRIVER**, so the 18-leg holdout would have repeated the
irrecoverability that retired the panel it descends from.

**✅ BUILT AND WIRED 2026-07-30, $0** — [`md_analysis_traj.py`](../modalities/md_analysis_traj.py),
mirrored to S3 on the driver's existing per-checkpoint hook (upload-as-written, per CLAUDE.md's checkpoint
rule) and with its own receipt in every leg's result JSON, so a leg that silently failed to persist coordinates
is visible in the artifact the collector already reads. 11 tests, all runnable in the dev sandbox.
**⚠ IT IS DELIBERATELY NOT A FULL HEAVY-ATOM TRAJECTORY, and the honest version of that is the point:** full
heavy-atom on a ~466k-atom solvated assembly is ~2.8 MB/frame, i.e. hundreds of MB per leg — outside the "tens
of MB against the ~112 MB System XML the driver already uploads" the requirement was costed at, which is
plausibly why it was adopted and never done. What ships instead is the **closure of the atoms every readout in
this lane consumes** — every protein CA, every Cys SG, every Lys NZ, every non-polymer heavy atom — at ~1k
atoms and single-digit MB per leg. **All three historical defects become $0 re-derivations** (a test asserts
exactly that, atom by atom); an analysis nobody anticipated over a dropped sidechain does not, and
`select_analysis_atoms(all_heavy=True)` is there for a leg that can afford the bytes. **The cheap 95 %,
labelled as such in the file's own manifest**, beats a complete record that stays unwritten.

### 5 · ✅ RESOLVED — the NR-V04 retrospective's own gate could no longer be satisfied by anything

Its **Gate** reads *"Val B-full + NR-V04 feasibility + Step 1 fan-out."* The fan-out is **DONE**; the
feasibility panel is **WITHDRAWN**, not merely paused; and valB_full sits behind a module-1 gate that
[§Open decisions 9](#open-decisions) has just **declined to amend, correctly**. Two of the three preconditions
are therefore not pending — they are **unreachable**. An item that is "built, preregistered and idle" behind a
gate that cannot fire is not being held; it is being **abandoned without saying so**, which is the failure mode
this file's own §Current front paragraph was corrected for. **It needed a decision either way**, and it got one:
✅ **2026-07-30 (trimcrae go) — Arm E RUNS, Arm F stays blocked on the valB PASS.** ⚠ **And my framing was wrong
in a way worth keeping: I proposed this as a scope correction I had derived, and the prereg's own §9
"Dependency honesty" had made the same argument on 2026-07-24** and left the judgement open — so no criterion
is amended and none needed to be. [§Open decisions 12](#open-decisions).

### 6 · Ranking what is left by DECISION VALUE PER DOLLAR — not by dollars

*Cheapest-decisive-first is a rule about **decisiveness ÷ cost**, and the ladder has lately been ordered on the
denominator alone. The lane that spent the most this month (~$74, the fan-out) returned a **single-conformer,
single-replicate, one-cycle-open** map that the paper can only report as provisional, while the three items
that could change what the program CONCLUDES cost $0, $0 and low-tens-of-dollars and are unbought. That is not
an argument the fan-out was wrong — it is §2.9 and it is real — it is an argument about **ordering**, and it is
the ordering below.*

| rank | what | $ | why it ranks here |
|---|---|---|---|
| 1 | **Re-anchor the paper's resolvability argument on the measured SD** | **$0** | The paper currently states the *assumed* SD in §2.10/§4/§5 while **reporting the measured one in §2.11** — one fact, two values, in one document. Done in this pass |
| 2 | ~~**Wire the strided-trajectory requirement into `nrv04_covalent_md`**~~ ✅ **DONE 2026-07-30** | **$0** | Item 4. It was a hard precondition on the only built-and-unlaunched GPU item we own, and it is now met |
| 3 | ~~**Settle the `S` replicate count BEFORE the market re-opens**~~ ✅ **DONE — n = 2 per arm** | **$0 to decide** | Item 3. The lane would otherwise have resumed under-powered the moment price allowed |
| 4 | **`S` at n = 2 per arm** — the flagship kill-switch, correctly sized and now CONFIGURED | **~$23** (ladder) | The only unrun test of the program's headline causal claim, and the second seed is what makes its *likely* answer readable. Waiting on the market, not on a decision |
| 5 | **NR-V04 retrospective, Arm E (R1 only, 16 legs)** ✅ **RUNNING** — *was "18 legs", superseded by prereg AMENDMENT 4 (2026-07-31): `nr4a3` co-fold seed 3 excluded by measured input fault (0.181 Å heavy-atom clash), so n = 3/3/2* | **≈$7.7** | A *new axis of evidence* (biological holdout), built and preregistered, with a registered MDE — CLAUDE.md §5's "default YES". The gate is reconciled to the prereg and the durable-trajectory precondition is met |
| 6 | ~~**Segment-grid re-enumeration** (5b)~~ ✅ **DONE 2026-07-30 — and it refuted its own premise** | **$0** | Neither a grid limit nor geometry: the chain template carries **one pendant**. A two-branch template is constructible at n = 18 with existing segments, but that is a DESIGN change to a preregistered enumeration and is not taken here |
| 7 | **Replicates on the open cycle** (3 of 18 fan-out edges) | **~$25** | One purchase, two open caveats: it attributes or dissolves `cycle_3carbonyl`'s violation AND gives the binary lane its first measured replicate SD, which today is transferred from the ternary lane |
| 8 | **The generative arm of the generation-matched null** (control c) — ✅ **$0 prep DONE, launch-ready** | **PROJECTED** | Addresses the confound actually raised (the GENERATIVE step); the arm that ran addresses the SELECTION step and bounds the manufactured rate at 3× the real campaign's own — narrowed, not excluded |
| 9 | **A known-answer calibrator for the `S`-shaped quantity** | **unpriced** | The real gap [Open decision 9](#open-decisions) exposed. It unlocks nothing on its own and must obey decision 9b's binding requirement (reference data and structure on the **same** protein), so it follows 4 rather than leading it |
| — | **More replicates on `ΔΔG_coop` / a rescoped valB edge** | — | **Explicitly NOT on this list.** `R` says the miss is endpoint-state; replicates shrink variance, not bias; [decision 6](#open-decisions) closed it |

*(Ranks 6–8 were added on 2026-07-30 — they are not new discoveries, they are items that had been sitting as
prose in a deliverable table or a §2.9 caveat with no rung, no price and no gate. **A caveat with nowhere to go
is how work gets silently dropped**, which is the same failure this section's item 5 names for the
retrospective. They now have entries in the ordered plan.)*

**★ AND THE PAPER IS CLOSER TO SHIPPABLE THAN THE LADDER IMPLIES.** Ranks 1–3 are **$0**, ranks 4–5 together
are **low tens of dollars**, and the flagship's tail (5c + 5d, priced in their own rung entries — not restated
here) is gated behind a causal result that rank 4 either delivers or honestly bounds. **Nothing on this list is
a multi-hundred-dollar commitment**, and no item above needs the prospective NR4A ternary matrix that
[decision 9](#open-decisions) correctly left locked. ⚠ **The corollary is a stopping condition, and it is worth
stating because "state of the art" can drift into "never finish":** once rank 4 reads out, **every result the
paper's current claims rest on has either landed or been honestly bounded** — what remains after that is the
tail that a *positive* `S` would unlock, and a paper reporting a bounded null does not wait for it.

---

## 11 · Money, authorization and gates

*Navigation, not content. Every figure below has exactly one home and this section states none of them.*

**The four spending rules are immediately below, in [§Spending rules](#spending-rules)** — no
pre-authorization · spend-gated, cheapest-decisive-first · GO/NO-GO after every priced rung · a step whose
engine has no completed benchmark leg is **PROJECTED** and excluded from the pinned total. ⭑ That last rule
is why [§10](#10--the-roadmap--one-ordered-list)'s price column distinguishes *priced* from *PROJECTED* from
*unpriced*, and why an honest **unpriced** beats a plausible figure. ⚠ **Superseded, retained:** this section
used to restate all four rules in full, which was a second copy of a fact with one home — legitimate while
the rules lived in another file, a rule-1 violation the moment the merge put them on this page.

**Where the numbers live** — and per invariant 6 this section holds none of them:

| | one home |
|---|---|
| the pinned ladder total and its derivation | [§Spend summary](#spend-summary), regenerated by `vast_cost_model.py` and CI-checked against [`vast-ladder-repricing.json`](../modalities/vast-ladder-repricing.json) |
| per-rung authorisation and cumulative cost | [§Dependency spine](#dependency-spine) |
| per-item price and gate | [§THE ORDERED PLAN](#the-ordered-plan-spend-gated--read-top-to-bottom-for-whats-next) |
| the cost evidence behind every rate | [pricing.md](../compute/pricing.md) · [bid-strategy.md](../compute/bid-strategy.md) |
| realised spend | [`realised-spend.json`](../modalities/realised-spend.json), summed from each lane's own rental ledger — a **floor**, with an attested block the machine ledgers cannot see |
| the buy line (`$/ns`) | [`inflight_usd_per_ns.APPROVED_USD_PER_NS`](../modalities/inflight_usd_per_ns.py) — **the drift line IS the buy line**; a row that prints `⚠ DRIFT` is a row we do not buy |
| live in-flight state | [`inflight_usd_per_ns.py`](../modalities/inflight_usd_per_ns.py) / `inflight-board-all.md` — ⚠ **not** the [⏱️ IN FLIGHT](#in-flight-superseded) block on this page, which is superseded ([§12](#12--findings-that-belong-to-other-documents) finding 6) |

⚠ **Two ledgers, never summed.** GCP trial credit buys wall clock, not headroom; it is tracked separately from
realised and ladder spend.

⚠ **The dependency spine is a SPEND graph, not this page's claim graph.** Its edges are authorisations; the
edges in [§4](#4--the-dependency-graph) are entailments. They must never be merged — collapsing them loses
either the money or the epistemics.

⚠ **The plan's cumulative chain is non-monotonic and this page does not repair it**: it steps
$109 → $107 → $104 across the three RUNG-4 entries and $162 → $183 → $169 across 5b → 5c → 5d. The CI subset
check verifies that the spine's cumulative values are a *subset* of the plan's; it does **not** check the
plan's own ordering. Recorded in [§12](#12--findings-that-belong-to-other-documents).

---

## Spending rules

*★ **THE ONE HOME** for the four spending rules. Zero history. [§11](#11--money-authorization-and-gates) links here and restates nothing. Rule 4 is why [§10](#10--the-roadmap--one-ordered-list)'s price column distinguishes priced / PROJECTED / **unpriced**.*

1. **No pre-authorization, no pre-staging.** Nothing is ever queued to auto-fire. Every GPU run is presented at
   its gate with (a) the prior step's result, (b) a pinned cost (from realized GPU-h, not a guess), and (c) a wait
   for an explicit trimcrae "go." Only $0 CPU/CI work runs without a nod.
2. **Spend-gated ladder, cheapest-decisive-first.** The cheapest run that could kill the paper comes first; each
   rung's bigger spend unlocks only if the previous, cheaper rung looks promising. Never pay for an expensive
   stage on a hypothesis a cheap stage could have falsified.
3. **GO/NO-GO after every priced rung.** Each rung ends with an explicit test; NO-GO = stop or pivot.
4. **Every step is priced bottom-up per edge** on the Vast-4090 bases below; provenance in
   [pricing.md](../compute/pricing.md). A step whose engine has no completed benchmark leg is carried as
   **PROJECTED and excluded from the pinned total**, never at a fake number.

## GPU economics (full provenance in [pricing.md](../compute/pricing.md))

*★ **LARGELY A POINTER**, deliberately: the throughput table's home is `vast_cost_model.MEASURED_NS_PER_DAY_84K`, the bid rule's is `bid-strategy.md §7`, the per-edge bases' is [pricing.md](../compute/pricing.md). What genuinely lives here is the **six cost levers**, which are ratios and survive any reprice.*

**All production runs go on Vast.** GCP L4 / SageMaker / Modal are not the go-forward basis. **The card is not
the decision — the OFFER is.** Rank live offers by all-in **`$/ns`** (bid + storage ÷ measured throughput) and
take whatever wins; the top 10 routinely contain both 4090s and 3090s. Measured throughput @84,534 particles is
**4090 804.06 / 4080 693.35 / 3090 460.91 ns/day** (4090/3090 = **1.745×**) — table of record
`vast_cost_model.MEASURED_NS_PER_DAY_84K`, re-anchored 2026-07-27 onto a median over N≥3 independent hosts
(pricing.md → Appendix T). The cheapest 3090 floor was **$0.0147/hr** against **$0.1310** for the cheapest 4090
— an **8.8×** price spread that more than covers the throughput gap. VRAM is never the constraint (≥24 GB is
ample). A 3090 does need **1.745×** the wall clock, so a leg with a hard continuity requirement is
proportionally more exposed on it — scaled and flagged per card, not ignored.
*(Superseded, retained: the single-host figures **4090 755.36 / 4080 703.51 / 3090 359.36** and the
**2.10×** ratio derived from them. Appendix T says what retired them.)*

- **★ PLANNING RATE: $0.137 per reference (4090) GPU-hour** — best-10-offer mean on the live board; range
  $0.057 (best offer) to $0.309 (median). Against the **$0.35–0.39/hr `step1_fanout` actually paid**, that is
  **2.6–2.8×**. Best-to-median spread is **5.43×**, so *selection* is the dominant lever — worth several times
  the bid policy.
- **Bid = the market floor plus a staleness tick** (`min_bid × 1.02`, min +$0.0005), **capped at that machine's
  on-demand price**, never at or below the floor. Measured 2026-07-25 by renting one offer at three bid
  multiples: **`charged = min(your bid, the machine's on-demand price)`** — so a premium is paid on *every*
  hour and cannot buy safety from on-demand renters. Retention is bought with **checkpoint frequency**, which is
  free. Every multiplier this repo has used (`×1.1`, `×1.5`, `×1.9`, `×1.25`) is retired; derivation, the
  measured bid ladder, and what retired each one are in
  [bid-strategy.md](../compute/bid-strategy.md). `VAST_BID_FLOOR_MULT` survives only as an unset escape
  hatch for a leg that genuinely cannot be paused.
- **Storage is a real line, not a rounding error** — ~$0.011/hr at the 40 GB the launcher requests, which on the
  *best* offer is 42 % of all-in cost. Ask for the disk the job needs.
- **On a `resources_unavailable` refusal, pick another host — do not wait it out.** Vast is a market of ~23
  independently-priced machines you can see at once, not a pool; the floor is flat day-to-day, so a different
  host today costs what this one will cost tomorrow. `protfep_vast_launch.collect` records and destroys the
  machine and `ResourceSpec.exclude_machine_ids` keeps selection off it — a host that never starts has infinite
  realised $/ns, which the ranking cannot otherwise see.

### Per-edge bases — one extrapolated, one rate-measured, one converted

**None is a completed end-to-end edge on a 4090.** That caveat is the reason every stage cost below is a
bottom-up estimate rather than a total.

| basis | value | how it was obtained |
|---|---|---|
| **RBFE binary edge** (complex+solvent, ~35k atoms) | **~13.7 ref GPU-h ≈ ~$1.9** | Live-diagnosed per-iteration rate on the **real cmpd19/NR4A3** complex — 12.76 / 13.70 / 14.42 s/iter on three independent Vast 4090 hosts (16 samples each) — × the hardcoded 2400-iteration leg. A clean end-to-end ΔG was **not** captured (both spot instances preempted), so this is an extrapolated rate, not a completed-edge measurement |
| **Ternary cooperativity edge** (3 replicas, ~146k particles, 12 windows) | **~$8.8 ($3.2–22)**, 56–72 ref GPU-h | Rate **measured directly on a Vast 4090** (firm leg via `run_ternary_leg.sh`, self-staged 8G1Q, 146,284 particles): warmup clean, production steady at **~14–18 s/iter (median ~16)**. Leg length **confirmed at 2400 iterations** (400 equil + 2000 production at 2.5 ps/iter, `nr4a3_ternary_fep.py:343-344`) — and now *observed*: valB_mini's ternary seed 0 reached **2000/2000** production iterations. 2400 × 16 s ≈ **~10.7 GPU-h/leg** × 2 legs × 3 replicas ≈ **~64 GPU-h/edge** |
| **Endpoint-MD leg** (~466k atoms) | **~$0.19**, ~1.38 ref GPU-h | Backed out of the **completed** 18-leg NR-V04 covalent panel: ~$0.43/leg realized on a 3090 at ~$0.10–0.21/hr ÷ the card ratio *(computed with the then-current **2.102×**, superseded 2026-07-27 — pricing.md Appendix T; the conversion is due a refresh at the next reprice)*. The one basis resting on a completed multi-leg ledger; the 4090 conversion itself is inferred |

**Two live transferability warnings.** (i) The ternary rate was measured on the **SMARCA2/VHL 8G1Q** assembly
and is being used to price **NR4A** ternaries — the *same* move that cost 2.6× on the binary lane when the real
cmpd19/NR4A3 complex turned out to sample at ~13.6 s/iter against TYK2's ~5.2. Expect an NR4A ternary leg to be
heavier, not lighter; time one before treating these rows as firm. (ii) The **L4→4090 card ratio is validated at
~2.06×** (33 → 16 s/iter) — a ratio of rates is count-independent, so that conclusion is solid.

**Provider reality check.** The ladder is *priced* in Vast-4090 dollars, but `valB_mini` is *actually running* on
**GCP L4 on-demand**, a lane pricing.md bills at ~$94/edge. That is a deliberate use of the **expiring GCP free
trial** (~$292 left of $300, window closes **2026-10-10**; Modal's $30/mo is already $27.54 spent and does not
carry over) — free credit beats cheap cash, and it buys ≈3 ternary edges, not the ladder. But it means
**realized spend and ladder spend are two different ledgers**: `credit-status.json` records GCP `spent: 8.0`
from a **manual** source not yet reconciled against the ~8 dispatched L4 legs. Track GCP burn separately, and do
not let "we spent ~$2 so far" imply the L4 lane was free.

### Cost levers adopted 2026-07-24 ([evidence](nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md))

1. **~~4 fs ternary production ≈ 2× cheaper per leg.~~ ⚠ CORRECTED 2026-07-25 — the saving is **1.56×**, not
   2×, and the leg is **2800 iterations**, not 2400. Both verified against `rbfe_spot_driver` source, both pure
   arithmetic on the existing measured rate.**
   - **Why not 2×:** halving the timestep halves the force evaluations only in the phase whose dt *changed*.
     The warmup is pinned at **1 fs either way**. Per replica: 2 fs = 1.0e6 (warmup) + 2.5e6 (production)
     = **3.5e6 steps**; 4 fs = 1.0e6 + 1.25e6 = **2.25e6**. Ratio **0.643×** ⇒ a **1.56×** saving. The old
     "2×" overstated it by ~36 %.
   - **Why 2800, not 2400:** "400 equil + 2000 production at 2.5 ps/iter" assumes the warmup runs at the
     *production* timestep. It does not — `_iters_from_time` derives warmup iterations from the **WARMUP**
     integrator, and the source comment says so outright (*"more iters at a smaller dt"*). At the as-run
     `warmup_timestep_fs=1.0`, 1 ns of equilibration is 1e6 steps ÷ 1250 steps-per-iteration = **800**
     iterations, each costing the **same 1250 force evaluations** as a production iteration. So the as-run 2 fs
     leg is **2800 equal-cost iterations**, and pricing it at 2400 understated **every 2 fs ternary stage by
     ~17 %**.
   - **⚠ The claim "iterations are timestep-independent (2.5 ps/iter)" is FALSE and is retired.** Iterations are
     `steps ÷ steps_per_iteration`, and steps depend on dt; 2.5 ps/iter holds only *at 2 fs*. **Price in STEPS,
     not iterations** — iteration counts are not comparable across protocols.
   - Net effect on the edge: **~$8.8 → ~$10.2 at 2 fs**, and the 4 fs edge is **~$6.6, not ~$4.4**.
   **The as-run lane is 1 fs warmup → 2 fs production**, verified against the live VM, not the doc (GH run
   30123894814 `mode=tail` on VM `gcp-ternary-30112102294`: `[tfep] timestep=2.0 fs`,
   `warmup_dt_override="WARMUP timestep overridden to 1.0 fs"`, `NaN_seen=no`; `gpu-ternary-fep-gcp.yml` defaults
   `timestep_fs: 2.0`, `use_preequil: 0`). The "4 fs" people remember is the runbook §1c *pre-equilibration
   demonstration* — after plain-MD pre-equilibration the calib leg ran warmup 48/48 @1 fs → production 40/40
   @4 fs, zero NaN, ΔG_morph 47.28 ± 0.53, where every prior attempt died at warmup iteration 1 — i.e. 40
   production iterations, not 2000, and it held **only because** pre-equilibration was on. Settling step: RUNG 2b.
2. **The binary and solvent legs cancel EXACTLY in any paralogue comparison — up to 2×.**
   `nr4a3_ternary_fep.py` defines `binary_<e3>` as **E3 machinery + PROTAC with NO target**, and solvent as
   ligand-in-water. Both are **paralogue-independent**, so for any morph
   `ΔΔG_coop(P) − ΔΔG_coop(P′) = ΔG_ternary,P − ΔG_ternary,P′` **exactly.** A 3-paralogue comparison therefore
   needs **3 ternary legs + 1 shared binary + 1 shared solvent — NOT 3 edges** (18 legs vs 12, −33 %; 9 if only
   the selectivity contrast is needed, −50 %). **Never price a paralogue panel as N edges again.** And the
   saving is *larger* than the leg count suggests: the `binary_vhl` leg ran at **~28.6–38.2 s/iter (median ≈33)**
   on L4, the *same* rate as the ternary leg — a shared binary leg is a full-price leg paid for once instead of
   N times.
3. **~~Sequential (anytime-valid) stopping instead of a fixed 3 replicas — ~20–25 %.~~ ⚠ REFUTED BY MEASUREMENT
   2026-07-25 — it saves ~0.8–2.6 % on THIS ladder, and should NOT be wired.** `adaptive_certify.py` /
   `adaptive_allocator.py` are built and unit-tested but were never wired to the ternary ladder, and the
   ~20–25 % was an allocation-design figure that was never checked against this ladder's actual shape. Measured
   as a futility stop (`valb_rescope_design.py`): at σ = 0.5 it stops after **4.87 of 5** replicates (**2.6 %**);
   at σ = 0.7, **4.96 of 5** (**0.8 %**). **Mechanism, not a fitting artifact:** an anytime-valid bound must be
   wide enough to remain valid under *every* stopping time, so at n = 2–4 with σ ≈ 0.7 it is simply never tight
   enough to fire. The saving is real for long horizons; **a 5-replicate ladder is too short to pay for it.**
   Do not carry the 20–25 % in any total.
4. **Free gates lead.** `selectivity_wedge_confirm` depended on `valB_full` + `nrv04_retrospective` (~$43) even
   though its validation need is matched-pair, not cooperativity-cube. Decoupled.
5. **Ligand-side double difference replaces the protein-mutation campaign** as the primary causal test — which
   at the time had no engine at all, and still has no NR4A-scale rate.
6. **E3 breadth is free at search, capped before GPU** (≤2 recruiters, dropped set logged).

*Operational Vast setup — image `triskit23/nr4a3fep:latest` (openfe ≥1.12 + ambertools + lomap/kartograf +
OpenMM pinned to CUDA 12.6), the `probe_offers` / `bench` / `firm` tooling in
[`nrv04_vast_launch.py`](../modalities/nrv04_vast_launch.py), and the bid/ranking code of record in
[`gpu_backend.py`](../modalities/gpu_backend.py) + `vast_cost_model.recommended_bid` — is documented in
[pricing.md §E](../compute/pricing.md); not repeated here. The hourly read-only price sampler is
`.github/workflows/vast-price-sample.yml`.*

---

## Spend summary

*★ **THE SPEND LADDER'S ARITHMETIC.** The pinned total is **DERIVED** (`vast_cost_model.py` → [`vast-ladder-repricing.json`](../modalities/vast-ladder-repricing.json)) and `lint_consistency.check_derivations` fails the build if this file, [pricing.md](../compute/pricing.md) or [bid-strategy.md](../compute/bid-strategy.md) drifts from it. Never hand-carry it.*

**PINNED TOTAL: ~$169 mid-range (~$46–626)**, GO at every gate, priceable stages only.
*(Superseded, retained: **~$158 mid (~$44–578)** — retired 2026-07-30 when RUNG 5a-KS went from **2 ternary legs
to 4** (n = 2 seeds per arm; [Open decisions 11](#open-decisions)). ⚠ **That reprice is the cleanest in this
file's history and it is worth saying why: the market snapshot, the `$/reference-GPU-hour` rate and every other
stage's GPU-hours are BYTE-IDENTICAL across it**, so the entire **+$11 mid** is the second seed per arm and
nothing else — the opposite of the 2026-07-27 reprice, where no price moved and only the yardstick did. And
that earlier one is retained too: **~$185 mid (~$51–614)**, retired 2026-07-27 when the throughput table was
re-anchored; the GPU-hours did not change, the `$/reference-GPU-hour` did. pricing.md Appendix T.)*

**How it is built** — regenerate the alchemical/MD stages with
`python research/modalities/vast_cost_model.py --json-out vast-ladder-repricing.json`
(JSON: [`vast-ladder-repricing.json`](../modalities/vast-ladder-repricing.json)); the tool prices 9 stages
at **$149.63 ($36.58–531.46)** at the committed snapshot's **$0.1143/ref-GPU-h**. The ladder figure adds the
stages the tool does not cover, at the **[low, mid, high] the machine registry uses** — step0 ~$1–2 (mid
**$1.5**), valA_mini ~$0–15 (mid **$0**, its *realized* cost on GCP credit rather than the band's midpoint), the
~$8 measured covalent panel, 5a basin ~$0–50 (mid **$0**, realized), 5b linker ~$0–20 (mid **$10**):
`149.63 + 1.5 + 0 + 8 + 0 + 10 ≈ 169`; low `36.58 + 1 + 0 + 8 + 0 + 0 ≈ 46`; high
`531.46 + 2 + 15 + 8 + 50 + 20 ≈ 626`. [pricing.md §C](../compute/pricing.md) and
[bid-strategy.md §6](../compute/bid-strategy.md) carry the same total — all three must agree, and
[`lint_consistency.py`](lint_consistency.py) recomputes it from
[`pinned-figures.json`](pinned-figures.json) → `derivations.ladder_total` rather than
trusting any of them.

⚠ **TWO THINGS THIS PARAGRAPH GOT WRONG UNTIL 2026-07-30, both found by regenerating rather than reading.**
**(a)** It stated the 5a basin stage at **mid $25** while the machine registry has always used **$0** — so its
own printed arithmetic came out at **`≈ 194`** beside a pinned total of `~$158`, and the sentence that followed
asserted the chain *"ends on the same ~$158"*. A doc contradicting itself inside four lines, which is precisely
what rule 1 exists to catch; the registry was right and the prose was wrong. **(b)** The tool figures quoted
here (**$149.4 at $0.137/ref-GPU-h**) were from an older market snapshot than the committed artifact, which
carried **$138.16 at $0.1143**. ⚠ **Beware a near-collision when reading old copies of this file: the tool total
is NOW $149.63, which is within $0.25 of the stale $149.4 it replaces, and the two have nothing to do with each
other** — the old one was 2 legs at a higher rate, the new one is 4 legs at a lower one.

**Excluded from the total:** (a) the 5a-KS **confirmatory** protein-mutation wedge and its reciprocal cycle —
engine qualified, but the NR4A cost is a particle-count projection, not a measured rate; (b) Optional/HELD
ΔG_open + ABFE (~$200–500 more).

**⚠⚠ THE `$/hr` AXIS IS MEASURED; THE GPU-HOUR AXIS IS NOT.** The reference GPU-hours are the repo's own work
estimates; this multiplies them by a measured rate, it does not re-derive them. **A rate measured on one
molecular system is not a price for another** — the single largest correction to date (~4× on the fan-out) came
from applying a public-TYK2 per-iteration rate to the NR4A3 complex, which is ~2.6× heavier. The ternary base is
*still* a SMARCA2/VHL rate pricing NR4A ternaries. If the GPU-hours are 2.6× low, these costs are 2.6× low no
matter what we bid. Dominant uncertainties, in order: the **ensemble-MD leg count** (5c + retrospective), the
**ternary transferability risk**, then the confirmatory wedge's particle-count projection.

**What survives every reprice.** The six cost levers are **ratios** — 4 fs halving force evaluations, the exact
binary/solvent cancellation, sequential stopping — so they are independent of $/hr and of system heaviness. And
**none of this weakens the mechanism-first case** — but ⚠ **one of the two arguments that used to carry it has
been retired by measurement and must not be re-quoted.** The *precision* argument — *"spending on an axis
needing ~2.0 kcal/mol when the method resolves 1.12 is a bad trade at any price"* — **no longer holds**, because
the resolvable difference was assumed and is now measured (§MECHANISM-FIRST; [Appendix
A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) 53). **Two arguments survive intact and they are
sufficient on their own:** (i) a **categorical** handle needs *no* margin at all, so it is not competing with
the marginal axis for resolution; and (ii) the categorical screens are **$0 CPU** and therefore dominate on
cost at any noise floor. What the correction does change is the marginal axis's **rank**, not its **order** —
it is worth confirming, and §MECHANISM-FIRST says on what condition.

| Rung | GPU work | Step $ (low–high) | Cum. (mid) |
|---|---|---|---|
| 0 · infra + free CPU (DONE) | step0 + emc_e3 + pocket | ~$1–2 | ~$2 |
| 1 · Val A smoke (DONE, realized ~$0 on GCP credit) | 1 public RBFE edge | ~$0–15 | ~$2 |
| 2 · pilot (DONE) + Val B-mini | 1–2 RBFE edges + 1 ternary edge | ~$2.8 + ~$8.8 (range $4–31) | ~$13 |
| **2b · 4 fs adoption + matched re-calibration** | 1 ternary edge @4 fs | **~$4.4** ($1.6–11) | ~$17 |
| 3 · Val B cube (SMARCA2/4 module) + NR-V04 feas. (DONE) | 2–3 ternary edges + CRL-MD; covalent panel | ~$22.5 + ~$8 (range $14–75) | ~$48 |
| 4 · fan-out + atlas + **unique-residue map** (both $0) + NR-V04 retro | ≈19 RBFE edges + NR4A1/2/3 ternary **legs** | **~$36** + ~$21 (range $20–147) | ~$104 |
| 5a · mechanism-first basin search + **KILL-SWITCH** | basin ($0–50, multi-E3, CPU) + ligand-side double difference, **4 ternary legs (n = 2 seeds × 2 arms)** | ~$0–50 + **~$23** ($3.1–97) | ~$152 |
| 5 (if GO) · linker + ensemble refine + local FEP | inverse-linker ($0–20) + ensemble MD (~$18) + within-basin FEP (~$21) | ~$49 (range $5–187) | ~$169 |
| Confirmatory protein-mutation cycle (optional) | 1–3 mutation directions | **~$4.6 PROJECTED** | *(excl.)* |
| Optional ΔG_open / ABFE (HELD) | — | +$200–500 | *(excl.)* |

Notes: the restructuring buys **causal evidence** (matched-pair cycles + ensemble MD + local FEP) over
co-fold-and-score — higher information per dollar, not lower. A non-viable paper still dies for ~$2 at Val A, or
**free** at the Tier-0 unique-residue map and the atlas (both passed). The *expected* cost is lower than the
totals suggest, because the leading gates are now $0.

## Dependency spine

*★ **THE AUTHORISATION GRAPH.** ⚠ **This is a SPEND graph: its edges are authorisations, not entailments.** [§4](#4--the-dependency-graph)'s graph is the claim graph, and the two must never be merged — collapsing them loses either the money or the epistemics. ⚠ Its cumulative notation (`Cum ~$N`) is **deliberately distinct** from the plan's (`Cum. ~$N`) and `lint_consistency.check_subsets` raises an ERROR if the two are unified.*

```
TIER-0 unique_residue_map [x]($0) + atlas [x]($0)  ──[BOTH PASS]──►    ★ leads everything priced
          │        (C397 exit-vector reach; K572/K518/K592 exposed; EWSR1-lysine axis thin)
          │
RUNG0  step0 [x] + emc_e3 [x] + pocket [x]                              (CPU/$0, done; Cum ~$2)
          │
RUNG1  valA_mini [x] ──[GO]──►                                          (cite OpenFE; Cum ~$2)
          │
RUNG2  step1_pilot [x] ∥ valB_mini [~ 2 fs, r0 wrong sign]  ──[GO?]──►  (Cum ~$13)
          │
RUNG2b 4 fs adoption + MATCHED re-calibration (~$4.4) ──[no NaN & ΔΔG consistent?]──►   (Cum ~$17)
          │      └── YES ⇒ every downstream ternary leg ≈2× cheaper
          │      └── NO  ⇒ stay at 2 fs, carry the 2 fs base
          │
RUNG3  valB_full cube (module 3 = SMARCA2-vs-SMARCA4) + nrv04_feasibility [!] ──[GO?]──►   (Cum ~$48)
          │            ([!] = feasibility's GO is WITHDRAWN pending a corrected re-run: its readouts
          │             measured the Elongin C interface, not VHL<->NR4A1. It gates nothing until then.)
          │
RUNG4  step1_fanout ∥ atlas [x]($0) ──► nrv04_retrospective ──[concordant?]──►   (Cum ~$104)
          │      (holdout, NOT the calibrator; read WITH the Cys551 covalent confound)
          │
RUNG5  basin_search($0–50, multi-E3, pose-marginalised, CATEGORICAL terms)        (Cum ~$129)
          │        ──► ★ KILL-SWITCH = ligand-side double difference (~$12)       (Cum ~$141)
          │      └── no discrimination ⇒ STOP: publish honest causal negative
          │      └── discrimination    ⇒ extend + tail
          │      └── CONFIRMATORY 2nd line: the protein-mutation cycle — pmx + GROMACS
          │           (perses retired: OpenEye-gated). Known-answer benchmark PASSED
          │           2026-07-25; NR4A cost PROJECTED (~$4.6), so it is excluded from
          │           the total and still owes a WEDGE-SIZED benchmark before it may
          │           claim to resolve a paralogue-scale difference. It does NOT gate
          │           the ladder — the ligand-side double difference does.
          │
       inverse_linker($0) ──► ternary_ensemble_refine ──► local_ternary_fep         (Cum ~$169)
          │
RUNG6  fold ──► redteam ──► post/submit                                             ($0)

OPTIONAL/HELD (explicit nod only): dg_open_paralogue, abfe_conditional (incl. the λ-repair)
```

## Current front

*★ **SUPERSEDED BY [§10](#10--the-roadmap--one-ordered-list), retained for one statement.** ⚠ This section has **zero** inbound references and names its own homes for everything it says. The one thing it owns is the sharpest statement of the feasibility panel's status — **WITHDRAWN**, not merely "under correction" — which contradicts the ordered plan's `[!]` marker and the schedule JSON, and is recorded as [§12 finding 12](#12--findings-that-belong-to-other-documents).*

Rungs 0–1 are done. The Tier-0 unique-residue map and the differential atlas are done ($0, both PASS). The
NR-V04 covalent feasibility panel is **WITHDRAWN** — not merely "under correction". Its GO was never
produced by the frozen scoring rule, its inputs were contaminated, and no trajectory survives to re-derive from,
so its re-run is **`[HELD]`** pending a prereg amendment. It gates nothing.

**NOTHING IS BILLING.** All three lanes that were running closed on 2026-07-30 — the **Step 1 fan-out** (19
congeneric RBFE edges), the **valB_mini replicates** (4 legs) and the **closure triangle**, whose `R` landed at
5:11 PM ET and was the last owed GPU work in the fixed scope. **Two lanes remain held, deliberately and for
stated reasons**: RUNG **5a-KS** behind the relaunch price gate, and the **restrained binary re-run** behind
the triangle's `R` — which has now landed, so what that leg is waiting on is a *reading*, not a run. Live
state, cost and `$/ns` for every one of them: the [**⏱️ IN FLIGHT**](#in-flight-superseded) block on this page, which is their
one home — ⚠ **and this paragraph must never restate it.** It said *"three lanes are billing"* for a day after
the board said nothing was, which is a rule-1 defect in the one direction that matters, since a stale
"currently spending" line is what an unattended fleet looks like when it is *not* being supervised.

**Built and idle, awaiting a go or a decision:**
- **The NR-V04 retrospective** — built, preregistered, never launched; next launch is a pilot, not a fan-out.
  ⚠ **"Awaiting a go" overstates it, and the correction is the point:** its own gate names two preconditions
  that are **unreachable**, and its driver does not meet a requirement this file adopted. Both are in
  [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) 4–5;
  the decision is [§Open decisions 12](#open-decisions).

**★ WHAT IS ACTUALLY NEXT is not on this page.** This section says what is *idle*; it has never said what to do
first, and while the fixed scope was closing that gap did not matter. It does now — nothing is billing, so the
next thing to happen is a *choice* rather than a result landing. The ranked list, the reasoning and the prices
are in [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) 6,
which is their one home; **this paragraph deliberately does not restate the order.**

**Closed earlier:** the 5a-KS confirmatory protein-mutation benchmark **qualified** (RUNG 5a-KS), moving the
ladder's only unscoped rung from UNPRICED to *projected*. Nothing with a GPU price launches without an explicit
go, and every rental — fan-out, resume or single cold unit — now faces the buy line as well as its rung's
dollar ceiling.

## Open decisions

*★ **THE DECISION REGISTER.** 15 numbered rulings, all closed. ⚠ **Cited by number in 30 files and nothing resolves a decision number** — the numbering is **frozen** and survived this file's merge unchanged. [§10](#10--the-roadmap--one-ordered-list) rows cite these by number.*

1. **`[x]` ADOPTED — method calibrator swapped from NR-V04 to SMARCA2-vs-SMARCA4** (valB_full module 3). NR-V04
   stays the biological holdout; its selectivity is most plausibly covalent target engagement, and SMARCA2/4 is
   already staged in-repo.
2. **`[x]` ADOPTED — the protein-mutation wedge is demoted from primary to confirmatory.** The ligand-side double
   difference is the paper's headline causal evidence and runs on the lane Val B already has an accuracy control
   for. The mutation cycle is kept, not deleted: its benchmark has now passed. ⚠ **The clause that stood here —
   *"so the paper can have two independent causal lines"* — is WITHDRAWN (2026-07-30):** the mutation cycle is
   a **ternary-minus-binary contrast, structurally the quantity that failed**, so it is a second line but not an
   independent one. Algebra and consequences: [Open decisions 10](#open-decisions).
3. **`[x]` DECIDED — adopt 4 fs, but TWO-STAGE**, sequenced after valB_mini's 2 fs result (RUNG 2b).
4. **`[x]` REVERSED — the step1 fan-out was RESUMED on 2026-07-26 and is running.** The hold below is
   **superseded**; it is kept because its reasoning is still the right reasoning and would apply again to any
   *new* edge list.
   *Superseded text, do not cite as current:* **"HOLD the step1 fan-out; do NOT resume the 19-edge tranche"**,
   on a *scientific* reason independent of price — under mechanism-first the fan-out's **selection criterion**
   had changed, the exit vector must now carry a linker toward **C397** (10.9 Å) and orient the E3 so the
   transfer zone covers **K572/K518/K592**, which is not the same as ranking substituents by affinity, so
   resuming the old edge list would spend ~$36 optimising the wrong objective; and nothing was lost by
   re-scoping because **0/19 units had produced a ΔΔG**.
   **What retired it:** the 5a basin search — the $0 step the hold was waiting on — **completed**, and the two
   preconditions it was protecting are now met. The lane also ceased to be a $36 all-or-nothing bet: placement
   is **per unit** and gated on `$/ns`, so it buys only what the market sells inside the buy line and holds the
   rest, and the cycle-closure edges are in the queue rather than stranded in a last wave. The rung entry under
   RUNG 4 carries the live status.
5. **`[x]` CLOSED — raising `GPUS_ALL_REGIONS` is NOT available to us.** trimcrae, 2026-07-26: *"We've tried
   over and over for more quota. They won't give it to a small account like ours."* Repeatedly requested,
   repeatedly refused. **Do not re-file it, and do not plan around a quota that is not coming.** (I raised it as
   an ask the same day, quantified at 1→4; withdrawn — see [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 20.)

   **AND A FASTER GPU WOULD NOT HELP EITHER — because the GCP lane is DOLLAR-bound, not time-bound.** Asked and
   answered 2026-07-26 rather than assumed. From [credit-status.json](../compute/credit-status.json): cap
   **$300**, spent **$8**, so **~$292 remains** against a 2026-10-10 expiry.

   | | value |
   |---|---|
   | one full ternary leg (2800 iters × 56.5 s) | **43.9 L4-h ≈ $31** |
   | credit runway | **~411 L4-h ≈ 17 days continuous ≈ 9.4 full legs** |
   | calendar available | 76 days ≈ 1,824 h of single-GPU wall clock |

   The credit is exhausted after ~17 days of continuous running inside a 76-day window, so **calendar is not
   scarce — money is.** And science-per-dollar is `speed / rate`, which is flat-to-worse on faster cards
   *(non-L4 rates are list-price approximations, not repo-measured)*:

   ⛔ **SUPERSEDED 2026-07-31 — the non-L4 rows of BOTH tables below are WITHDRAWN, do not cite them as
   current; the correction is beneath them and in [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 56.**

   | card | rel. speed | ~$/h | units/$ | leg-equivalents on $292 |
   |---|---|---|---|---|
   | **L4 (current)** | 1.0× | 0.71 | **1.41** | **9.4** |
   | A100 40 GB | ~5.2× | 3.67 | 1.41 | 9.4 |
   | V100 ⛔ *superseded* | ~3.0× | 2.48 | 1.21 | 8.0 |
   | H100 80 GB | ~11× | 11.0 | 1.02 | 6.7 |

   **★ BUT THE CENSUS CHANGED THE ANSWER, AND NO REQUEST IS NEEDED FOR ANY OF IT.** `GPUS_ALL_REGIONS = 1` caps
   the **count**; the **per-type** quotas say which card, and several are **already granted at limit 1** —
   `NVIDIA_V100_GPUS`, `NVIDIA_P100_GPUS`, `NVIDIA_T4_GPUS`, `NVIDIA_P4_GPUS`, `NVIDIA_K80_GPUS` alongside
   `NVIDIA_L4_GPUS` (A100/H100 are the only ones at 0). Nobody had looked, because the quota check only grepped
   `L4|G2|GPU` and printed the rows mid-log. Spec-derived against the ~$292:

   ⛔ **SUPERSEDED 2026-07-31 — WITHDRAWN, do not cite; see beneath the table.**

   | card | quota | ~×L4 | ~$/h | ~$/leg | legs on $292 | science/$ |
   |---|---|---|---|---|---|---|
   | L4 (current) | 1 | 1.00 | 0.71 | 31 | 9.4 | 1.41 |
   | **P100** ⛔ *superseded* | **1** | ~2.4 | 1.46 | **26** | **11.1** | **1.67** |
   | V100 ⛔ *superseded* | 1 | ~3.0 | 2.48 | 36 | 8.0 | 1.21 |
   | T4 ⛔ *superseded* | 1 | ~1.1 | 0.35 | 14 | 20.3 | 3.05 |

   ⛔ **SUPERSEDED BY MEASUREMENT, 2026-07-31 — DO NOT CITE EITHER TABLE ABOVE AS CURRENT.** The reading they
   supported — *"P100 looks better than L4 on BOTH axes, faster and more science per dollar, i.e. **+18 % more
   legs from the same money**"*, and the T4 at **2.2×** the L4's science-per-dollar — is **WITHDRAWN**. It was
   never measured, it was flagged as unmeasured, and the measurement has now refuted the heuristic that
   produced it. Retained above because it is what the plan carried for five days;
   [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 56 has the correction.

   **★★ WHAT THE PROBE MEASURED, AND WHY IT INVERTS THE TABLE.** Built and run 2026-07-31 on free trial credit
   (`gpu-bench-gcp.yml` + [`gcp_card_bench.py`](../modalities/gcp_card_bench.py)); one home for every
   number is [`gcp-card-bench.json`](../modalities/gcp-card-bench.json), and the readable table with its
   full caveats is **[gcp-gpu-facts.md §1c](../compute/gcp-gpu-facts.md)**. Do not copy figures here —
   point at those.

   1. **THE WORKLOAD IS COMPUTE-BOUND, NOT BANDWIDTH-BOUND — and that is the whole ballgame.** The T4 is the
      discriminating card precisely because its two specs point opposite ways (bandwidth 320 vs the L4's 300,
      FP32 8.1 vs 30.3 TFLOPS). Bandwidth predicts **1.07× L4**; FP32 predicts **0.27×**. **Measured: ~0.31×**
      at the ternary system size. So every row generated by the bandwidth heuristic — P100 and V100 included —
      rests on a premise the measurement rejects.
   2. **THE SPEC TABLE ALSO HAD A PRICE ERROR THAT NEEDED NO MEASUREMENT AT ALL.** Its `$/h` column compares
      the L4's **whole-VM** rate (0.71 = a g2-standard-4, which *bundles* the L4) against **bare GPU** rates
      for the others (1.46 / 2.48 / 0.35). A P100 cannot run without a host. Adding the n1-standard-4 it needs
      (**$0.190/h**) to the same table, with its own speed assumptions untouched, already collapses P100's
      advantage from **+18 % to +3 %** and the T4's from **2.16× to 1.44×**. Two independent errors, both in
      the direction that made the alternatives look good.
   3. **THE PRACTICAL ANSWER: STAY ON THE L4.** Combining the two, the T4 delivers **~0.41×** the L4's
      science-per-dollar where the table promised 2.2× — wrong by **~5×**, and in the direction that would have
      sent the next GCP leg to the worst card available. The original framing of this decision — *"a faster GPU
      would not help either, because the GCP lane is DOLLAR-bound"* — **survives, and is now measured rather
      than assumed.**

   ⚠ **WHAT IS STILL NOT MEASURED, stated so nobody over-reads this.** The T4 figure was **REFUSED by the
   probe's own admission gate** (CV 5.6 % against a 5 % ceiling) and is reported as a *ranking*, not a rate —
   a 3.5× discrepancy cannot be manufactured by 5.6 % of block scatter, but the number itself is provisional.
   Capacity also intervened: `NVIDIA_T4_GPUS` on-demand returned **`ZONE_RESOURCE_POOL_EXHAUSTED` in all four
   us-central1 zones**, so the T4 arm had to run on spot ([facts §1d](../compute/gcp-gpu-facts.md)).
   **A granted per-type quota is not capacity** — that is new, and it is the one respect in which "we already
   hold quota for several GPU types" oversold itself.

   **What no longer holds: "buy the probe together with the first GCP leg that is actually queued."** That was
   right while the probe was hypothetical and the answer had no consumer. It is now bought and the answer
   exists, so the sequencing question is closed rather than deferred.

   **What stands regardless: no GPU quota REQUEST is worth filing** — not more count (refused, and wouldn't have
   helped), and not a faster type (we already hold several). ⚠ This also means the quota increase I
   proposed would not have helped **even if Google had granted it**: at 4 GPUs the same $292 is spent 4× faster,
   not turned into 4× the science. That table's central claim was wrong independently of the refusal — see
   [Appendix A](../../STRATEGY.md#appendix-a--superseded-numbers-and-retracted-claims) row 20.

   **THE REAL BUDGET, and the number to plan the rescope against: ~$292 ≈ 9 more full ternary legs on GCP.**
   The lane split still holds and is still not a cost question — GCP free/serial/1-GPU at ~56.5 s/iter, Vast paid/
   parallel at ~16 s/iter (**3.53×**, corrected from the 2.06× in pricing.md, which compared an L4 *warmup* rate
   against a 4090 *production* rate). Every idle GCP-GPU minute is still expiring credit lost, so keeping that one
   GPU fed still matters — it just cannot be fed for more than ~411 hours in total.

6. **`[x]` CLOSED 2026-07-30 — the valB_mini rescope. `R` answered it, and the answer is that no rescope of
   this calibrator's EDGE can help.** *(It was held until the reverse leg read out; that landed 2026-07-28, and
   the closure triangle then produced `R`.)* Every rescope variant was a search for a better **edge** — a bigger
   signal, a cleaner replicate SD, the P-series network. **`R ≈ 0` says the miss is an ENDPOINT-STATE error**,
   which telescopes out of any cycle and is a property of the **model or the reference data**, not of which edge
   sits on top of them. Changing the edge changes neither. The live successor is a **system** question, not an
   edge question — [decision 9](#open-decisions) and its $0 survey of paralogue-selective systems with a solved
   structure on **both** arms. *(Superseded framings retained: the P-series congeneric network, refuted for $0
   on charge/heavy-atom grounds; and the synthetic closure triangle, which was not a rescope in the end but the
   diagnostic that closed this item.)*
7. **`[x]` RESOLVED 2026-07-30 — the admits-zero gate defect. It never touched valB's verdict, and it is now a
   BINDING REQUIREMENT ON THE NEXT CALIBRATOR rather than a retrospective amendment. $0.** The frozen gate
   accepts a method that predicts no cooperativity change (**22 % vs 23 %** — a gate you can pass by predicting
   nothing). Two things settle it. **(a) It is moot for valB_mini**, which failed on **SIGN**, before the
   `|mean − target| ≤ 1.0` band was ever consulted — so no amendment could change that verdict and none is
   sought, which is exactly why this is not the forbidden retune. **(b) It is NOT moot going forward**, because
   any future calibrator reusing this gate design inherits it. **It therefore binds the S-calibrator spec
   ([decision 9](#open-decisions)): no accuracy band wider than the signal being calibrated, and a stated
   null-rejection rate up front.** The 22 %/23 % measurement is the evidence for that requirement; the frozen
   valB gate itself is left **unamended**, on the record, failed on sign.
8. **`[x]` RESOLVED 2026-07-30 — the `UNDERPOWERED` proxy. $0, LOW STAKES, and it is low-stakes because the measurement says
   so.** `binary_departure_prereg` demotes a null closure to `UNDERPOWERED` whenever `sigma_leg > 0.2` — a
   threshold hand-set when `sigma_leg` was unknown to a factor of 15.6, i.e. a proxy chosen because the power
   itself was not computable. **It is computable now, and it VINDICATES the proxy:** bisecting the design's own
   power curve puts a conventional 0.80-power threshold at `sigma_leg ≈ 0.216` against the frozen **0.200** —
   agreement to ~7 %. ⚠ **So amending it would NOT rescue a null `R`**: at the measured upper bound the power
   is ~0.63, which a conventional threshold demotes anyway. **Proposed fix is therefore transparency, not
   correction** — report the computed power *beside* the verdict, keeping the demotion rule, because
   "UNDERPOWERED" currently cannot distinguish power 0.63 from 0.05 and those warrant different responses.
   Evidence: [`valb_failure_propagation.frozen_rule_vs_measured_power`](../modalities/valb_failure_propagation.py).
   **Same standard as item 6 and it is why nothing was changed:** a rule may be amended only if its statistic
   is shown to lack discriminating power, demonstrated independently of whether we like its answer — and here
   the statistic turned out **not** to lack it. Written down **before `R` landed**.
   **★ THE LIVE QUESTION IS NOT THIS RULE — IT IS WHERE `sigma_leg` ACTUALLY SITS.** The crossing (≈0.216) lies
   *inside* the bounded interval [0.045, 0.265], so a null `R` is readable or not depending on the true value,
   and the bound is an UPPER bound. **That is settleable for $0 from the triangle's OWN legs when they land** —
   `valb_failure_propagation.narrow_sigma_leg_from_triangle_legs` applies the n=3-measured replicate-SD/MBAR-SE
   ratio to the triangle's own per-leg MBAR SEs, giving an estimate with no homology-model and no cross-seed
   solvation term. ⚠ The ratio is **transferred, not measured on the triangle** (which has no replicates), so
   this narrows the interval and must never be reported as though the triangle had replicates.
9b. **`[x]` DONE 2026-07-30 — decision 9's $0 survey RAN, and it answered more than it was asked.
   Artifact: [`s-calibrator-survey.json`](../modalities/s-calibrator-survey.json)
   (generator [`s_calibrator_survey.py`](../modalities/s_calibrator_survey.py)); every PDB ID is fetched
   from RCSB, never typed.** Ten candidate paralogue pairs screened on whether a deposited **ternary** exists
   on **both** arms. **2 of 10 are symmetric: SMARCA2/SMARCA4 and IKZF1/IKZF3.** The incumbent therefore
   **survives its own screen** and decision 9 forces no system change. Two pairs would have been traps —
   **BRD4 has 24 ternary structures while BRD2 and BRD3 have zero**, so either BET pairing puts a modelled arm
   opposite a real one, the exact configuration decision 9 exists to avoid.
   **★ THE FINDING THAT MATTERS MOST WAS NOT THE QUESTION ASKED, AND IT IS A CORRECTION.** A first reading of
   this survey said the lane's SMARCA4→SMARCA2 homology substitution "was avoidable". ⚠ **It was not — not for
   this ligand.** 8G1Q's own deposition title is *"Compound 1 … bromodomain of human **SMARCA4** and
   pVHL:ElonginC:ElonginB"*: Wurz **compound 1**, the calibrator's `calib_hi`, was co-crystallised **only** with
   SMARCA4. Every deposited SMARCA2 ternary carries a **different ligand** (8G1P = Compound 11, 6HAX = PROTAC 2,
   6HAY = PROTAC 1, 9HYB = P-series P3). Keeping the ligand whose SPR α values **are** the reference data
   therefore *forced* the substitution.
   **What the choice cost is the real result: the calibrator is built on the LOWEST-RESOLUTION structure in the
   family — 3.73 Å — AND on the wrong paralogue, while SMARCA2 ternaries exist at 2.24–2.84 Å.**
   Ligand-identity and protein-identity are **coupled** here, and the lane resolved that coupling in favour of
   the ligand. **`R` has since localised the valB miss to the model or the reference data — and both candidate
   causes trace to that one coupled choice.** Binding consequence for the S-calibrator spec: **pick a pair
   whose reference data and structure sit on the SAME protein**, rather than buying reference data at the price
   of a modelled arm. *(Not established and not claimed: that a different template would change the
   calibrator's answer. A shared deposition series does not make two entries interchangeable.)*

9. **`[x]` DECIDED 2026-07-30 (trimcrae delegated: *"You make an educated call yourself"*) — the valB_full gate
   is NOT amended, and module 3 is NOT decoupled to unlock it.** The question was whether module 3 (paralogue
   discrimination, SMARCA2-vs-SMARCA4) should be freed from behind the failed cooperativity gate now that `R`
   says the ternary environment is internally clean. **It should not.** Module 1's statistic did not *lack
   discriminating power* — it discriminated perfectly well and returned NO — so the repo's own amendment
   standard ([AMENDMENT 1](../modalities/nr4a3-nrv04-covalent-feasibility-prereg.md#amendment-1--2026-07-25-dated-defect-fix-trimcrae-delegated))
   does not reach it; and `R` supplies no licence either, because `R` is **blind to the endpoint-state class
   that broke valB**. Unlocking the prospective ladder here would be the retune this program forbids, wearing
   a diagnosis as cover. **The prospective NR4A ternary matrix stays unrun and cooperativity claims stay
   exploratory.**
   **★ THE REAL FINDING IS A GAP, NOT A GATE IN THE WAY.** `S` — the flagship kill-switch the whole prospective
   stage turns on — **has never had a known-answer calibrator**, because valB_mini calibrated `ΔΔG_coop`, a
   quantity `S` does not contain (its binary leg cancels algebraically). The failure *exposed* that; it did not
   cause it. Closing it is a **new item**, not a gate amendment, and it unlocks **nothing** beyond whether `S`
   may be read as calibrated rather than exploratory. Reasoning + what must be preregistered first:
   [`valb_failure_propagation.module3_decision`](../modalities/valb_failure_propagation.py).
   ⚠ **The strongest argument against, recorded because it must be preregistered rather than discovered:** an
   S-calibrator on SMARCA2-vs-SMARCA4 runs on the **same system family carrying the suspected error**, and a
   known-answer accuracy test does *not* telescope an endpoint-state error the way a cycle does — which is
   precisely why valB_mini caught it. The arms are also **asymmetric**: 8G1Q is a *SMARCA4* structure and
   SMARCA2 is the homology-substituted arm, so a homology-model error sits on **one arm and does not cancel**.
   A failure would then be ambiguous between *"the S-class quantity does not work"* and *"this benchmark
   inherited the same model defect."* **So the system must be chosen on which arm is REAL, not on what is
   already staged** — and the $0 survey of paralogue-selective systems with a solved structure on *both* arms
   leads, before any spend.
10. **`[x]` RESOLVED 2026-07-30 — the protein-mutation cycle is no longer called an independent second causal line.
   $0.** RUNG 5's CONFIRMATORY cycle is `ΔΔG_neo-interface^m = ΔG_mut^ternary − ΔG_mut^binary` — a
   **ternary-minus-binary contrast, structurally identical to the quantity that failed** (the PRIMARY `S`
   escapes this only because its binary leg cancels *algebraically*; a protein mutation changes the target,
   which is exactly what the two environments differ by). Its known-answer benchmark passed on a
   *protein-mutation* quantity, **not** on a ternary-minus-binary one, so that pass does not cover this
   exposure. Consequence: a concordance between `S` and this cycle is **not two independent lines agreeing**,
   and a discordance would be uninterpretable. Derived in
   [`valb_failure_propagation.error_algebra`](../modalities/valb_failure_propagation.py). *Not
   load-bearing* — the paper's headline causal result is already stated as not hostage to it.
11. **`[x]` DECIDED 2026-07-30 (trimcrae go) — `S` GETS n = 2 SEEDS PER ARM (4 ternary legs).**
    The lane is re-specified and the ladder regenerated: `ternary_vast_launch.MODES['5aks']` declares four
    legs, `vast_cost_model` prices four, the stage-cache seeder now seeds **every declared seed** (it seeded
    only seed 0, and `5aks` sets `stage_required: True`, so a seed-1 leg would have died on a cache MISS on a
    rented host), and both new units are on the watch list rather than launching unwatched. **Nothing is
    bought yet** — all four stay `enabled: false` behind the relaunch price gate and re-enable **together**,
    because a partial re-enable buys a number that still cannot report a null.
    ⚠ *The two parked seed-0 legs are untouched and resume byte-identically from `production/800` and
    `warmup/640`; the seed-1 legs are cold starts.* The question, as it stood:

    **`[~]` HOW MANY SEEDS PER ARM DOES `S` GET? This is trimcrae's, because it is a multi-leg GPU
    spend; everything else about it is settled and free.** ⚠ **It must be settled BEFORE the market re-opens,
    not after**: the relaunch price gate is the only thing currently holding the lane, and `R_ternary` already
    reads **ADMIT** on the science gate — so the next cheap offer resumes 5a-KS in the **n = 1 per arm**
    configuration that
    [§WHAT THE LANDED RESULTS CHANGE](#-what-the-landed-results-change-about-the-remaining-plan) 3
    shows cannot report its own likely answer.
    **RECOMMENDED — n = 2 per arm (4 legs; the 2 parked legs plus 2 more), for roughly double the parked
    ladder figure.** The reasoning is this repo's own litmus test, applied to the *design* instead of the
    sequence: *is there a result the extra pair could return that changes what we do?* **Yes — a readable
    null.** The pre-registered expectation is that the effect sits inside the range `S` can only half-resolve
    at n = 1, so the increment is what converts the **likely** outcome from an uninterpretable non-result into
    a **publishable bounded negative** — the same argument that made valB-mini "the highest-value dollar in
    the plan", now applied to the test valB-mini was supposed to certify. The $0 machinery check is **done**
    and favourable (item 3); the seeds are genuinely independent.
    **The alternatives, stated fairly.** *(a) Finish as parked (n = 1, ~$12 total, ~$1.5 already banked):*
    cheapest, retires the paper's *"the causal test has not been run"*, and is enough **if** `S` comes back
    large. Its failure mode is the likely case. *(b) n = 3 per arm (6 legs):* the repo's stated replicate
    standard, and it brings the resolvable difference down to the figure in §MECHANISM-FIRST — but the second
    seed buys most of the readability and the third is the shallow part of a `1/√n` curve, so it is the
    "deepening past field standard" CLAUDE.md §5 defaults against. *(c) Don't buy:* defensible only if the
    paper is content to ship with its headline causal test unrun, which contradicts the North Star.
    **What I would do, and would not do without a nod:** buy (b)-minus — the 2 parked legs plus 2 more, at
    n = 2 — and read a null as a bound rather than an absence. **Not proposed:** re-running the parked legs
    from scratch (their checkpoints are intact and durable) or extending them (more sampling on one seed buys
    precision that `S` does not lack).
12. **`[x]` DECIDED 2026-07-30 (trimcrae go) — THE NR-V04 RETROSPECTIVE RUNS: ARM E (R1, 18 legs, ≈$8). *(count SUPERSEDED by prereg AMENDMENT 4, 2026-07-31: **16 legs** — `nr4a3` co-fold seed 3 excluded by measured input fault)*.
    Arm F stays blocked on the valB PASS.** ⚠ **AND MY FRAMING OF THIS WAS WRONG IN A WAY WORTH
    CORRECTING: I proposed it as a scope correction I had derived, and the prereg had already made the
    same argument on 2026-07-24.** Its **§9 "Dependency honesty"** states that the gates govern the
    free-energy arm, that Arm E asserts no free energy, and that running Arm E is a *narrowing* rather
    than a gate jump — then names the alternative (hold Arm E until valB passes) and leaves the
    judgement open. So no criterion is amended and no amendment was needed; the decision is recorded as
    a **dated addition** in the prereg, which is what §9 itself asks for. The gate wording that
    conflicted was **this file's**, and it is reconciled in the RUNG 4 entry. What genuinely changed
    since 2026-07-24 is the premise: `step1_fanout` completed and the feasibility panel was WITHDRAWN,
    so two of three gates became **unreachable** rather than pending. **Integrity test, checkable
    rather than rhetorical: the panel has never run, so no result exists that this could have been
    motivated by disliking** — the distinction from [decision 9](#open-decisions), where a real NO
    existed and the gate was correctly left standing. **Precondition met** (durable trajectory).
    The question, as it stood:

    **`[~]` DOES THE NR-V04 RETROSPECTIVE RUN, OR IS IT FORMALLY RETIRED? It cannot stay "idle".**
    Its gate names **valB_full** and the **NR-V04 feasibility panel**; the first is behind a module-1 gate
    [decision 9](#open-decisions) has just declined to amend, and the second is **WITHDRAWN**. Neither is
    coming. Leaving it listed as built-and-awaiting-a-go is the *appearance* of a plan for ~$7.7 of work that
    nothing can authorise.
    **RECOMMENDED — a SCOPE correction to the gate, not an amendment to a rule, and only after the $0
    precondition below.** The argument, and it is deliberately narrow: **valB calibrates the ternary-FEP
    cooperativity lane, and the retrospective's authorised readout (`R1`, Arm E, 18 legs — *(count SUPERSEDED by prereg AMENDMENT 4, 2026-07-31: **16 legs** — `nr4a3` co-fold seed 3 excluded by measured input fault)*) is not in that
    lane** — it is an **endpoint-MD geometric contrast reported in Ångström**, with its own registered MDE
    (leg-to-leg σ 0.855 Å, 80 % power at 1.5–2.0 Å) and its own preregistered *directional-concordance-only*
    claim ceiling. A gate that names a control which does not cover the quantity is a **scope** defect, and it
    reads as one in the direction that matters: this is a *biological holdout*, i.e. exactly the kind of **new
    axis of evidence** CLAUDE.md §5 defaults YES to. ⚠ **The integrity test it must pass, stated because the
    repo forbids the retune this could be mistaken for:** amending a gate after a failing result is forbidden
    — **but there is no result here to rescue.** The retrospective has never run, so no verdict exists that
    this correction could be motivated by disliking. That is the difference between this and
    [decision 9](#open-decisions), where a real NO existed and the gate was correctly left standing.
    **HARD PRECONDITION — ✅ NOW MET, $0.** The shared driver had to persist a durable trajectory first, because
    launching 18 legs on a driver that discards positions repeats, exactly, what made the parent panel
    unrecoverable. Built and wired 2026-07-30 (item 4 above), so **this decision is no longer blocked on
    engineering — only on the call.** **If the decision is no, retire it explicitly** with the reason on the
    record — a named retirement is a result; an indefinite hold is not.
13. **`[x]` SPLIT 2026-07-30 — the "`S` has no calibrator" gap is TWO items, and the free half is now DONE.**
    [Decision 9](#open-decisions) recorded the gap as one thing and left it unsequenced, which is why it never
    acquired a rung. It separates cleanly:
    - **(a) Can a null `S` be READ? — a power/MDE question, $0, and it needs no known answer at all.** It is
      arithmetic on measurements this program already owns, and it is what item 3 above just did. **Done.**
      This is the half that actually gates the 5a-KS spend, and it was never the expensive half.
    - **(b) Can a non-null `S` be called CALIBRATED? — a known-answer question, and it is the paid one.** It
      stays deferred, behind [decision 9b](#open-decisions)'s binding requirement (pick a pair whose reference
      data and structure sit on the **same** protein) and [decision 7](#open-decisions)'s (no accuracy band
      wider than the signal being calibrated). ⚠ **It does not gate item 11**, and conflating the two is what
      made the gap look unaffordable: a *bounded null* needs (a) only, and a bounded null is the
      pre-registered likely outcome.
    **Consequence for the ladder:** `S` may be bought and read as a **bound** now; it may not be reported as
    calibrated until (b) exists. Both statements can be true in the same paper, and saying so is cheaper and
    more honest than waiting for (b) to buy (a)'s answer.

---

## 12 · Findings that belong to other documents

★ **Recorded, not fixed here — and recorded precisely because a caveat with nowhere to go is how work gets
silently dropped.** Each was found while reconciling this page against the paper, the SI, STRATEGY.md and the
merge inventory. **None is a roadmap bug**; each is a real inconsistency in a document this page does not own.

**For the manuscript** (do not read these as roadmap states):

1. ⛔ **The paper's preregistered Tier-0 gate is reported as *"pass on both axes"* on a criterion with a
   demonstrated false negative.** The pass turns on the word **exposed**, adjudicated by `V17`, the same
   `EXPOSED_RSA = 0.25` cutoff that [§7 branch 1](#branch-1--answered-2026-08-02--serves-r8) shows **fails to recover NR4A1 Cys551** — the one NR4A-family
   covalent site with literature support — in **0 of 25** frames. Neither Cys551's exposure failure, nor the
   rank-based replacement, nor `nr4a3-covalent-handle-ensemble.json` appears anywhere in the paper or SI.
   **This is the single most consequential thing this page knows that the manuscript does not.**
2. **The paper's Tier-3 row says the causal matched-pair test is *"priced, **not run**"* / "pending"**
   (`:2765–2772`) while §2.10e reports its result (`S = −0.1297 ± 0.3264`) and `:2670` says it *"retires the
   earlier"* reading. The tier table is stale against the paper's own §2.10e.
3. **The paper contradicts itself on how far the co-folding DockQ failure extends.** §2.12a confines it to
   *"this co-folding pipeline on a **VHL** neosubstrate interface and about nothing else"* (`:2128–2130`),
   while §4 (`:2501–2503`) applies it to structures that are a **CRBN** ternary. A reader arriving via §2.12a
   and one arriving via §4 get opposite answers, and `R10`/`R11` inherit whichever is chosen.
4. **SI `:229` — *"Lead — NR4A3-selective (the validated path)"*** is the strongest residual over-claim in
   either file: it heads the indication table and pairs the R1 term with "validated" in four words, where
   `:2478` says *"**Every paralogue-selectivity statement in this work is therefore an unvalidated
   prediction.**"*

**⚠ FOR THIS PAGE — findings 5–13 were raised against STRATEGY.md and the merge MOVED THEIR SUBJECTS HERE.**
They are unchanged in substance and deliberately not fixed by the merge: it records what is true today, and
several of them are owed-work entries whose count this merge is verified against. **Their old
`STRATEGY.md:NNN` line references are dead** — a section reference is given where one is available, and the
line number is kept only where it names a *paper* line.

5. ⛔ **The gate-failed header is stamped ~7 hours in the future** —
   [`## ❌ GATE FAILED … (2026-08-02 10:42 PM ET)`](#-gate-failed--the-smarca24-sensitivity-control-returns-null-on-an-adequately-powered-design-2026-08-02-1042-pm-et),
   against `selcal-verdict.json`'s `utc: "2026-08-01T02:43:16Z"`-derived truth. **Root cause,
   read from the data rather than guessed: the clock face was converted and the calendar date was not.**
   `02:43 Z → 10:43 PM` is the correct 12-hour conversion, but the date must roll back from 08-02 to 08-01
   and did not (the minute is also off by one). ⛔ **The heading itself is NOT corrected**, because its slug is
   the target of the repo's only non-Appendix-A anchor link (`nr4a-repanel-prereg-DRAFT.md:9`) and changing the
   date changes the slug. A dated correction note has been added **beneath** it instead.
6. ⛔ **The [⏱️ IN FLIGHT](#in-flight-superseded) board is
   3 days stale and structurally cannot see the lanes that have billed since** —
   header `as of 2026-07-30 5:30 PM ET` with *"NOTHING IS BILLING"*. The rows happen to be
   true for Vast (verified three ways at $0), but the board is scoped to Vast + GCP, so **a SageMaker rental
   is invisible to it by construction** — which is precisely how the 3:16 PM ET ABFE dispatch appeared on no
   board at all. A banner has been added pointing at the live renderer; **the board is not re-stamped**,
   because inventing a live state is the failure it already committed.
7. **[§The standing tally](#the-standing-tally-this-closes)'s *"have never been run"* / *"Neither is
   authorized here"* needs splitting.** The
   authorization half stands and is load-bearing. The *"never been run"* half is now imprecise for the
   CREBBP arm: a dispatch fired and was halted with no result. ✅ **The pmx half of this finding is already
   closed** — the arm was authorized, its $0 precheck then ran and returned `STOP_NO_REFERENCE`, and the
   tally now carries that correction with the old line retained. ⚠ **Superseded, retained:** *"pmx is now
   authorized … so `:546` is stale on that arm."* The ABFE arm's half of the finding stands.
8. **[§The SMARCA2/4 gate record](#-gate-failed--the-smarca24-sensitivity-control-returns-null-on-an-adequately-powered-design-2026-08-02-1042-pm-et)
   quotes a DeepTernary median its own artifact no longer holds** — `median 0.438` against
   `selcal-deepternary-poscontrol.json`'s `median_DockQ 0.4143` (recomputed from the 16 poses: 0.4087).
9. ✅ **CLOSED BY THIS MERGE. STRATEGY.md's banner said *"three selectivity results came to be withdrawn"***;
   [§3.3](#33--the-pattern--rewritten-because-the-version-this-page-carried-was-false) shows the count is at
   least **four** and the causal generalization attached to it is refuted. The banner was rewritten out of
   existence when the merge folded the document in, so the claim no longer stands anywhere — verified by
   search. ⚠ The audit record [`map-audit-strategy.md`](map-audit-strategy.md) A18 still quotes it as a live
   line; that file is a dated audit and is not corrected here.
10. ⛔ **`V4` — the highest-leverage unrun item in the program — has no entry in the ordered plan.** Verified
    over the plan's whole span: zero occurrences of CREBBP, SGC-CBP30, 4NR7, 5BT4 or `selectivity-benchmark`.
    It exists only in [§The standing tally](#the-standing-tally-this-closes) and Appendix A 64. **An item with no rung
    cannot be scheduled, refused or costed** — see [§10 row 2](#101--open-rows-ordered-by-what-unblocks-the-most).
11. ⛔ **`selcal_sensitivity_control` (RUNG 4b) has no ordered-plan entry either** — it is a schedule milestone
    with a landed **NULL** verdict and a frozen gate, visible only as its timestamped headline block.
    `work_ledger.scan_plan_items` therefore cannot see it, and neither can a reader reading the plan
    top-to-bottom. ⚠ **Adding it would change the open-item count**, so this merge records it rather than
    doing it.
12. **Six plan markers contradict a later section of this page or the schedule JSON** — `valB_mini` `[~]`
    (scoreboard: FAILED), Rung 2b `[ ]` "needs a go" (scoreboard: PASSED both stages), the step-1 fan-out
    `[~]` "RESUMED and RUNNING" (COMPLETE, lane closed), the NR-V04 retrospective (**two entries for one
    item**, `[!]` and `[ ]`, against RAN/DISCORDANT), 5a-KS `[~]` "PARKED, not finished" (LANDED), and
    `nrv04_feasibility` `[!]` "under correction" ([§Current front](#current-front): **WITHDRAWN**). `work_ledger.py`'s own
    docstring flags this exact hazard as a declared coverage hole. ⚠ **Not fixed here for the same reason as
    11** — every one of them is an owed-work entry, and changing a marker changes the count this merge is
    verified against.
13. **The plan's cumulative chain is non-monotonic** ($109 → $107 → $104; $162 → $183 → $169). The CI subset
    check verifies the spine's values are a subset of the plan's, not the plan's own ordering.

**For the pose pass** (which owns those rows):

14. ⛔ **The pose RMSD was a stale read of its own artifact, and it is invariant 5's failure mode for the
    second time.** This page quoted **3.46 Å** in four places. The artifact's history:
    `blind_apo_fpocket_top_box.rmsd_A` was **3.464** at commit `cc4325b68` and is **3.04** at the current
    `060a6a653`; the **3.489** in the same file is the *oracle-box* arm, a different arm. So the value was read
    once, the artifact was regenerated, and nothing re-read it — exactly what happened to the 76 % thiol
    occlusion figure. The live text now carries **3.04** with the arm named; **which arm the pose claim should
    rest on is the pose pass's call, not this merge's.**

**For the branch-1b pass:**

15. ⛔ **Branch 1b's prose has not been reconciled to its now-committed artifact**, and at least one
    disagreement is readable: the prose names **C534** as the paralogue cysteine that closes C397's window;
    the artifact's widest graded cell records `closed_by: "NR4A1 C505"`. The direction of the finding survives;
    the specific residue, the per-convention cell counts and the window widths do not, until re-read.
    [§10 row 5](#101--open-rows-ordered-by-what-unblocks-the-most).

**For branch hygiene** (CLAUDE.md §7):

16. **Two artifacts this page cites live off `main`.** [`nr4a3-linker-covalent-reach.json`](../modalities/nr4a3-linker-covalent-reach.json)
    was committed only on the working branch (it reaches `main` with this merge), and
    `nr4a-resistance-map.json` exists **only** on `origin/modalities-cache`, with its producer run under a
    soft-fail. **An artifact on the wrong branch is a stale fact that reads as a current one.**
17. ⛔ **The branch-drift rule fired during this very merge, and it changed a roadmap row.** This document was
    drafted on `claude/nr4a1-protac-positive-control-xnszjl`, whose copies of this page and of STRATEGY.md
    were **168 commits behind `origin/main`**. The page itself was byte-identical on both refs, so the drift
    was invisible in the obvious place — but `origin/main`'s STRATEGY.md carried a block the branch did not,
    and it **inverted** a roadmap row: the pmx arm was authorized on the branch and is **closed on evidence**
    on `main`. Ported before publishing, per CLAUDE.md §7's *port-then-switch, never switch-then-discover*.
    ✅ **The two workflow conflicts this finding left open are CLOSED** — `main` and the branch now carry
    byte-identical `.github/workflows/gpu-protfep-vast.yml` and `.github/workflows/nr4a3-linker-covalent-reach.yml`,
    both on `publish_artifacts.sh`, because the physical merge's port took them across. ⚠ **Still divergent,
    and not this pass's to resolve:** `.github/workflows/pose-recovery-check.yml` plus the ABFE-selectivity and
    apo-pose modules, which belong to the lane that is building them.

**For the merge inventory:**

17. **[`map-merge-inventory.md`](map-merge-inventory.md) counts Appendix A at *"76 rows"*.** Read directly, it
    is **69** (ids 1–65 plus 19a–19d, no duplicates). The inventory's own gloss — *"numbered 1–65 with
    19a/19b/19c/19d and a trailing framing row"* — describes 70 objects including the header, not 76. ⚠ The
    inventory is right that this page's old *"~113"* was wrong; its replacement is wrong too.

**For the categorical-axis pass** (found 2026-08-02 while pricing rung `5b-T`; **flagged, not fixed here** —
both are live text this pass does not own):

19. ✅ **CLOSED 2026-08-02 — the pilot pair is now marked superseded at every live use on this page, and
    `pinned-figures.json` carries `paralogue_collision_pilot_5657` so CI finds any copy that was missed.**
    Kept below with its original evidence because the diagnosis is what the registry entry cites.
    ⛔ **The categorical block above still says the matched paralogue MD ensembles are *"in flight"* and marks
    the verdict `VERDICT_NOT_EVALUABLE`. THEY LANDED.**
    [`nr4a-paralogue-dynamics.json`](../modalities/nr4a-paralogue-dynamics.json) carries the finished
    matched NR4A1/2/3 ensembles over **73,867** placements and **three** conformer scopes
    (`static_opened_model`, `unbiased_release`, `metad_biased`), and the verdict is evaluable. This is
    invariant 5's failure mode again — a status that had a committed artifact and was never re-read against
    it — and it matters in the direction that *understates* the program: the block hedges as unevaluable a
    result that is now measured. ⚠ **And re-reading it moves a number the design leans on**: the block's
    superseded *"0 at 12 atoms, 0.081 at 16, 0.258 at 20"* is the **5,657-placement** pre-landing figure,
    whereas the landed unbiased-release ensemble reads **0.00124 / 0.13331 / 0.38254** at those lengths — same
    direction, steeper, and not zero at 12. The keep-it-short consequence survives and gets *stronger*; the
    specific numbers do not, until re-read.
20. ✅ **CLOSED 2026-08-02 — `PARALOGUE_COLLISION_BY_LINKER_ATOMS` is now DERIVED from
    `nr4a-paralogue-dynamics.json` (`_load_collision_profile`), and the pilot pair survives only as
    `PARALOGUE_COLLISION_PILOT_5657_SUPERSEDED`, which nothing reads.** The derived `reach_only` is the widest
    reading across the three scopes, so a bracket built from it cannot understate. **No committed selection
    changed** — the field was always reported and never filtered on, which is precisely why it was safe to
    correct. ⚠ The committed `nr4a3-linker-design.json` still carries brackets written from the pilot table
    and will pick up the corrected ones the next time that lane regenerates; it is **separately stale for an
    unrelated reason** (57 enumerated constructs against the committed 54, a wedge-site change) — recorded in
    [`nr4a3-short-linker-probe.json`](../modalities/nr4a3-short-linker-probe.json) → `flagged_not_fixed`.
    Kept below with its original diagnosis:
    ⛔ **`nr4a3_linker_design.PARALOGUE_COLLISION_BY_LINKER_ATOMS` is a HARD-CODED COPY of that same
    pre-landing measurement**, and its own comment says so — *"The matched paralogue MD ensembles that turn it
    into a distribution were still in flight when this was written."* Every construct in the committed library
    is annotated with a collision bracket read from that copy rather than from the landed artifact. It is a
    reported cost and nothing is filtered on it, so no committed selection changes — but a design decision
    taken against **0.000 at 14 atoms** is being taken against a figure the landed unbiased ensemble puts at
    **0.03169**. ⚠ **Not edited here on purpose:** changing it changes what a preregistered enumeration
    reports per construct, which is that lane's call, not this one's. Rung `5b-T`'s gate therefore reads the
    **artifact** and never the copy.

**For the fusion / neoantigen lane** (found 2026-08-03 by the target-route sweep, **fixed at source, one
consequence still owed** — that consequence is not this page's to discharge):

23. ⛔ **THE REPO HELD TWO INCOMPATIBLE MODELS OF THE FUSION PROTEIN, AND ONE OF THEM WAS AN OFF-BY-TWO.**
    `fusion_cofold.py` resumed NR4A3 at residue 2; `fusion-breakpoint-neoantigens.json`'s 7 in-frame
    junctions resumed it at 318 / 361 / 419. A **$0 CI run** settled it
    ([`nr4a3-exon-audit.json`](../modalities/nr4a3-exon-audit.json)): **NR4A3's first two transcript exons
    are entirely non-coding**, and `fusion_breakpoints.py` indexed a **coding**-exon table with **transcript**
    exon numbers. For EWSR1 that is harmless — its exon 1 *is* coding, so rank ≡ coding index — **which is
    exactly why the error was invisible.** ✅ **Fixed at source**, with a guard that raises on a non-coding
    exon instead of silently sliding to a neighbour, plus an assertion that the resume window still retains
    the DBD.
    - ⛔ **The consequence the neoantigen lane owes:** all 7 committed junctions delete NR4A3's AF1 **and the
      first zinc finger**, so its **26 predicted binders span seams that do not exist**.
      `fusion-breakpoint-neoantigens.json` predates the fix and **must be regenerated before any of it is
      quoted** (regeneration needs MHCflurry in CI and belongs to that lane).
    - ✅ **What it does to this page, and it is favourable in both directions.** The model flagged as an
      *unsourced assumption* turns out to be the exon-correct one, arrived at independently. The ASO lane is
      unaffected and now corroborated — it deliberately refuses the exon mapping and sweeps a window that
      **brackets** the right answer, so what looked like conservatism was load-bearing. And **`R13`'s object
      is now defined at the sequence level**, which strengthens rather than weakens the standing note that
      the modelled LBD construct (373–626) excludes the fourth unique cysteine **C166**: under the *wrong*
      model that concern would have evaporated, because C166 would not have been in the fusion at all.
    - ⚠ **Still not settled:** the audit bounds which junction models are *arithmetically possible*; it does
      not pin the patient-level breakpoint, which needs a primary breakpoint report. `R13` still has no rung,
      no gate and no price ([§10.1 row 9](#101--open-rows-ordered-by-what-unblocks-the-most)) — what changed
      is that it now has a defined object to write them against.

**Closed by this merge** (recorded so it is not re-raised):

18. ✅ **Neither document contained the union of the two orderings.** This page's critical path and
    STRATEGY.md's decision-value ranking shared **zero** items. **Taken in
    [§10](#10--the-roadmap--one-ordered-list)**, which now holds both plus eight rows that were on neither.
21. ✅ **The ternary rebuild had no rung, no gate and no price.** It is **rung `5b-T`** in
    [the ordered plan](#the-ordered-plan-spend-gated--read-top-to-bottom-for-whats-next), priced at **$0**
    (DERIVED — [`ternary-rebuild-cost.json`](../modalities/ternary-rebuild-cost.json)) with a pre-registered
    three-arm GO/NO-GO. [§10 rows 1 and 18](#101--open-rows-ordered-by-what-unblocks-the-most) point at it.
22. ✅ **"What do I do next" needed two documents, and the first attempt at fixing that was a RELABELLING.**
    STRATEGY.md was 3,317 lines against this page's 1,436 while
    [`map-merge-inventory.md`](map-merge-inventory.md) classified **~2,430** of those lines as live plan
    material and only **~430** as genuine history — so ~75 % of the roadmap sat in the file labelled
    "appendices". ⛔ **The justification for leaving it there was that seven CI checks parse STRATEGY.md by
    exact heading string, and that is not a reason** — CLAUDE.md §5 rules that engineering effort is free and
    *"not worth the engineering effort to save X"* is never valid. Every live section is now physically here,
    each under the heading string and slug it always had; every parser was repointed in the same commit
    (`work_ledger.DEFAULT_PLAN_DOC`, `pinned-figures.json`'s `must_appear_in` / `subset_checks.file` /
    `artifact_figures`, and `lint_claims.py`'s 21 provenance strings). **No row number, decision number, price,
    gate or verdict changed.** What remains in STRATEGY.md is Appendix A and Appendix B, because their rows are
    read *as data* by `realised_spend.py` and their heading is a structural clear in
    `lint_consistency.is_cleared`.

---

## 13 · The deliverable's FRAMING — an open question, with a register and no decision

★ **Added 2026-08-03, and deliberately left OPEN.** [§5's operating regime](#5--where-each-requirement-stands)
names a **single deliverable** — [the paper](nr4a3-degrader-paper.md) + its SI — and this page has never
carried the question of *what that paper is about* as a question at all. It is one, it is trimcrae's, and
until 2026-08-03 nothing enumerated the alternatives. Seven framings, graded on six columns (does its central
claim rest on an instrument that has recovered a known answer **in the regime the claim needs** · evidence
committed · needs a bench · softening an existing claim · manuscript re-use · clock):
[`paper-framing-options.md`](paper-framing-options.md), which owns every grade and every figure below.

**Three things this page records, and none of them is a decision.**

1. ⛔ **The current framing is hostage to `R4`, which has no in-silico instrument and never will.** The
   candidate paper's central claim needs *something to bind the opened pocket*
   ([§2.2](#22--requirements-with-no-instrument--the-holes)), and [§10.1 row 20](#101--open-rows-ordered-by-what-unblocks-the-most)
   is the only row on the board that **cannot be bought at all**. Under a permanent no-wet-lab regime that is
   not a scheduling fact, it is a structural one.
2. ★ **Three of the seven framings need NEITHER a validated instrument NOR a bench.** They are writable on
   committed evidence today: **the known-answer audit** (the register of what happens when in-silico
   selectivity pipelines are put to tests with known answers — where **the failures ARE the result**, so no
   instrument has to pass); **the co-folding assembly failure** (components right, assembly wrong, by a
   factor of ten — self-contained, and the only framing with a live clock on it); and **the target-enablement
   dossier**, which can absorb the candidate work as a closing *"what a candidate would require"* section and
   so keeps every result in print. ⚠ **This is a statement about what is WRITABLE, not about what is best.**
3. ⚠ **The uncomfortable observation the register makes, recorded rather than argued:** the current paper's
   own scoreboard has more failed gates than a title promising a selective candidate can carry, and **three
   of the four failures are the three attempts at a positive control for the exact capability the title
   promises**. [§the scoreboard](#-where-we-are--the-scoreboard-in-plain-language) owns those counts; this
   section does not restate them.

⛔ **NOTHING HERE IS DECIDED, AND NOTHING HERE BLOCKS ANYTHING.** The framing choice is not a gate on any row
of [§10.1](#101--open-rows-ordered-by-what-unblocks-the-most): the mechanism, instrument and requirement work
strengthens whichever paper is written, and no row waits on it. ⚠ **It is also not an Open decision** — the
[Open decisions](#open-decisions) numbering is frozen and cited as data by 30 files, and this is not a ruling
that has been taken. It is recorded here so that a question with real consequences stops being invisible,
which is the same reason every other section of this page exists.

---

## Provenance

Artifacts that own the numbers above:
[`nr4a3-covalent-handle-ensemble.json`](../modalities/nr4a3-covalent-handle-ensemble.json) ·
[`nr4a3-linker-covalent-reach.json`](../modalities/nr4a3-linker-covalent-reach.json) ·
[`nr4a-paralogue-unique-residues.json`](../modalities/nr4a-paralogue-unique-residues.json) ·
[`nr4a3-pocket-reharmonize-summary.json`](../modalities/nr4a3-pocket-reharmonize-summary.json) ·
[`apo-pose-recovery.json`](../modalities/apo-pose-recovery.json) ·
[`nr4a-selectivity.json`](../modalities/nr4a-selectivity.json) ·
[`nr4a3-differential-surface-atlas.json`](../modalities/nr4a3-differential-surface-atlas.json) ·
[`selcal-interface-signature.json`](../modalities/selcal-interface-signature.json) ·
[`selcal-deepternary-headtohead.json`](../modalities/selcal-deepternary-headtohead.json) ·
[`selcal-cofold-decompose.json`](../modalities/selcal-cofold-decompose.json) ·
[`selcal-dockq-decoy-scale.json`](../modalities/selcal-dockq-decoy-scale.json) ·
[`selcal-xtal-census.json`](../modalities/selcal-xtal-census.json) ·
[`selcal-verdict.json`](../modalities/selcal-verdict.json) ·
[`nr4a-ternary-signature.json`](../modalities/nr4a-ternary-signature.json) ·
[`nr4a-ternary-ligand-provenance.json`](../modalities/nr4a-ternary-ligand-provenance.json) ·
[`valb-triangle-closure.json`](../modalities/valb-triangle-closure.json) ·
[`nr4a3-5aks-reduction.json`](../modalities/nr4a3-5aks-reduction.json) ·
[`nrv04-retro-verdict.json`](../modalities/nrv04-retro-verdict.json) ·
[`step1-fanout-map.json`](../modalities/step1-fanout-map.json) ·
[`selectivity-benchmark.json`](../modalities/selectivity-benchmark.json) ·
[`nr4a3-metad-crossreplica.json`](../modalities/nr4a3-metad-crossreplica.json).

**And the options registers wired in on 2026-08-03** ([§0.8](#08--the-six-options-registers--what-they-own-and-the-one-thing-they-may-never-do)),
each of which owns its own numbers and is linked rather than restated:
[`selectivity-mechanism-options.json`](../modalities/selectivity-mechanism-options.json) ·
[`instrument-options.json`](../modalities/instrument-options.json) ·
[`target-route-census.json`](../modalities/target-route-census.json) ·
[`nr4a3-short-linker-probe.json`](../modalities/nr4a3-short-linker-probe.json) ·
[`nr4a3-exon-audit.json`](../modalities/nr4a3-exon-audit.json) ·
[`nr4a3-5aks-cofold-prep.json`](../modalities/nr4a3-5aks-cofold-prep.json).

⛔ No claim on this page asserts NR4A3 selectivity, efficacy or clinical readiness; predicted quantities are
labelled as predictions throughout.
