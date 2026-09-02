---
id: DOC-SPRINT-S54-ROUTE-CLAIMS-AUDIT
title: "S54-ROUTE-CLAIMS-AUDIT — 1,200 route claims checked against the trunk; 24 are refuted, one route becomes takeable at $0, and the field that grades evidence carries ten refutations under the label `direct`"
level: L3
kind: memo
status: live
date: 2026-09-02
audience: [autonomous research agents, maintainers]
purpose: >
  The systematic version of what S41 and S43 found by accident: enumerate every field in
  systems/graph/routes.json that asserts something about the world or about this repository, and check
  each one against a committed artifact rather than against the prose beside it. Produces a proposed,
  unapplied patch. Edits no graph file.
scope: >
  All 77 routes in systems/graph/routes.json at HEAD b4cf28c6be8f464fc25e0cee06f6be50eb181138, plus the
  driver's two uncommitted working-tree edits to systems/graph/{blockers,routes}.json read at
  2026-09-02T09:37Z. Fifteen assertive field classes, 1,200 individual claims. Adjudicates records;
  measures nothing new; changes no grade.
last_verified: 2026-09-02
---

# S54 — every route claim, checked against the artifact that would settle it

**Item:** `AUT-PD-104` (`research/autonomy/research-ledger.json`, `state: queued`, `cost_class: free`,
score 131.9). **Started / finished (UTC):** 2026-09-02T08:52Z / 2026-09-02T09:50Z.
**Owned paths:** this file and
[`S54-proposed-route-claim-fixes.json`](./S54-proposed-route-claim-fixes.json). Nothing else was written,
and **no git write command was run** — `git cat-file`, `git show`, `git diff`, `git ls-tree`,
`git rev-parse`, `git log` only.

**Baseline.** `git rev-parse HEAD` = `b4cf28c6be8f464fc25e0cee06f6be50eb181138`. Mid-audit the driver
edited two graph files in the working tree; both were re-read before anything here was written, and
`git diff -U0` shows the whole of the change: one line of `blockers.json`
(`BLK-NO-EMC-DATA.retired_by_action`, narrowed from *"an ex-vivo panel … none of which exists"* to a
*fetchable or deposited* dataset) and one line of `routes.json` (`RT-SGK1`'s
`supporting_evidence[].what_it_supports` for `ART-NDRG1-PANEL-ATTRIBUTION`, rewritten to a withdrawal).
**Every finding below was re-verified against the post-edit tree; none moved.**

---

## ⛔ 0 · THE INSTRUMENT WAS TESTED IN BOTH DIRECTIONS BEFORE ANY VERDICT WAS TAKEN

Existence at the trunk is decided by `git cat-file -e HEAD:<path>` **on its return code**, never by
`git rev-parse`. Both halves were exercised first, on paths whose answer was known in advance:

```
rc=0    CLAUDE.md                                              (known present)
rc=0    systems/graph/routes.json                              (known present)
rc=0    research/modalities/emc-expression-panels.json         (known present)
rc=128  research/manuscripts/emc-supportive-effect-transfer.json  (known absent — S43's finding)
rc=128  research/NOPE-does-not-exist.json                      (fabricated to force a negative)
```

⛔ **And the trap the prompt names is real and was reproduced here.** On the same absent path,
`git rev-parse HEAD:research/manuscripts/emc-supportive-effect-transfer.json` prints
`HEAD:research/manuscripts/emc-supportive-effect-transfer.json` **to stdout** and the fatal to stderr —
so a `|| echo MISSING` fallback never fires and a naive capture records the unresolved path *as if it
were a hash*. Nothing in this memo uses `rev-parse` for existence.

**Applied at scale:** 63 distinct file paths are named inside route records; **all 63 exist at HEAD**.
31 artifact ids are cited by routes; **all 31 resolve in `artifacts.json`, all 31 paths exist, and none
is a stub** (smallest cited artifact is well over the 1 kB placeholder size that
`artifact_stub_guard.py` exists to catch). 29 distinct `grade.owner.file` documents; **all 29 exist**.
21 blocker ids in `blockers.json`; **every blocker id referenced anywhere in `routes.json` resolves —
zero dangling**.

★ **That is the first result and it is a negative one: the mechanical half of this defect class is
clean.** Nothing in the graph points at a file that is not there. **Every finding below is therefore a
claim refuted by the CONTENT of a file that IS there** — which is the harder half and the one no gate
reads.

---

## 1 · What was enumerated — 1,200 claims across fifteen field classes

A field is in scope if it asserts something a committed artifact could contradict. Descriptive fields
(`display_name`, `purpose`, `rationale`, `remaining_unknowns`, `distinct_from`, `aliases`, `objects`,
`closure_note`) are out.

| field class | claims | how it was checked |
|---|---|---|
| `required_validation[*].feasible_today` | 148 | against the S32/S41 adjudication, the `✅ DONE` marker scan, and `emc-expression-panels.json` |
| `required_validation[*].blocked_by` | 145 | id resolution; route-vs-entry consistency; each blocker's own `retired_by_action` |
| `supporting_evidence[*].strength` | 81 | against each cited artifact's own grading field — **§4, and it is the largest finding** |
| `grade` (value + `owner.file`) | 77 | pointer resolution only — **see the UNMEASURED row in §5** |
| `state.status` | 77 | against `blockers_inherited`, `required_validation`, and each blocker's record |
| `blockers_inherited` | 77 | id resolution; set-difference against entry-level `blocked_by` |
| `blockers_retired` | 77 | id resolution; overlap with `blockers_inherited` |
| `readiness.attainable_today` | 77 | against `grade.owner.file` existence |
| `next.best_next_action` | 77 | absence-assertion scan, conditional-trigger scan, named-path resolution |
| `next.cost` | 77 | against the compute/fetch content of the action it prices |
| `timing.recommendation` | 77 | against whether the route's own revisit trigger has fired |
| `timing.rationale` | 77 | absence-assertion scan |
| `readiness.missing` | 69 route-level fields (97 individual entries) | against `emc-expression-panels.json`, `selectivity-requirement-sizing.md`, and named paths |
| `timing.revisit_trigger` | 49 | against `technologies.json` `current_state` and against the artifact that would have fired it |
| `next.blocked_on` | 15 | against `next.cost`, `next.best_next_action`, and the named blocker's `retired_by_action` |
| **total** | **1,200** | |

⚠ **`running_job` was in the ask and does not exist in `routes.json`** — `grep -c running_job
systems/graph/routes.json` returns **0**. The one occurrence in `systems/graph/` is
`strategies.json`, where it is prose (*"the degrader program's open compute lanes — see the ordered
plan"*) pointing at the roadmap rather than naming a job id. **There is no stale-job claim to find
because there is no job field.** Recorded so the next audit does not re-search for it.

---

## ⭐⭐ 2 · THE ONE ROUTE THAT BECOMES MORE TAKEABLE: `RT-COVALENT-PROBE`, AND IT COSTS $0

**Put first because CLAUDE.md §0 says a route wrongly marked blocked is live work nobody is doing.**

`RT-COVALENT-PROBE` holds all five of these at once, at HEAD:

- `next.blocked_on`: `["BLK-REACH-CATEGORICAL"]`
- `next.cost`: `"$0"`
- `next.best_next_action`: *"Build a reactivity-weighted accessibility criterion and calibrate it against
  the known covalent site, then re-run the reach enumeration under it. Report the result as a rank until
  the criterion passes."*
- `required_validation[0]`: `{"what": "An exposure or reactivity criterion that recovers the known
  covalent site", "instrument": "V17", "feasible_today": true, "blocked_by": ["BLK-REACH-CATEGORICAL"]}`
- `timing`: `recommendation: pursue_now`, `automation_outlook: "Fully automatable — it is a $0
  recalculation once the criterion is defined."`

⛔ **And `BLK-REACH-CATEGORICAL`'s entire `retired_by_action` in `systems/graph/blockers.json` is:**

> *"Re-run the reach enumeration under a criterion that passes its own positive control, and report the
> result as a rank rather than a verdict until one exists. **$0.**"*

★ **The blocker's retiring action and the route's next action are the same sentence, and the blocker
prices it at zero itself.** `next.blocked_on` therefore says *this $0 act is blocked by the thing the
act retires* — a claim refuted by the record it names. The blocker is `kind: scientific_uncertainty`;
it is not a wet lab, not a person, not a dataset and not a decision for trimcrae.

**What taking it would cost, exactly.**

- **Real dollars: $0.** The enumeration module is `research/modalities/nr4a3_monovalent_reach.py`, whose
  own docstring line 3 reads *"($0, CPU/CI only, pure stdlib.)"* — no GPU, no rental, no network, no
  dependency install. The companion `INS-MONOVALENT-REACH` record in `instruments.json` carries
  `known_answer_control.state: "passes"` (its bivalent half replicates the committed artifact
  cell-for-cell), so the harness that would run the re-run is already validated.
- **The only genuinely new work** is defining a reactivity-weighted accessibility criterion and
  calibrating it against **NR4A1 C551** — which `instruments.json` already names as `V17`'s positive
  control, currently `known_answer_control.state: "fails"` with the note *"⛔ KNOWN-DEFECTIVE. Fails its
  own positive control; anything adjudicated by this cutoff inherits a demonstrated false negative."*
  That is agent time, which CLAUDE.md §5 prices at zero.
- **What it would buy.** `BLK-REACH-CATEGORICAL` is inherited by **two** routes (`RT-COVALENT-PROBE`,
  `RT-MONOVALENT`), and `V17` sits in the `instruments.disclosed_failing` list of both. Retiring it is
  the only $0 path in this audit that moves an instrument out of a failing known-answer state.
- ⛔ **What it would NOT buy, stated so nobody reads this as a promotion.** The route's other four
  blockers are untouched: `BLK-NO-WET-LAB`, `BLK-NOT-FUSION-SELECTIVE`, `BLK-PARALOGUE-DDG`,
  `BLK-R4-BINDS`. `required_validation[1]` (*"Chemical synthesis and a binding assay"*) stays
  `feasible_today: false` on `BLK-NO-WET-LAB`. The route-level `state.status: "blocked"` is therefore
  **correct and this memo does not propose changing it** — what is wrong is `next.blocked_on`, the field
  that says the *next action* is gated. No grade moves, no claim about C397, selectivity, efficacy or a
  therapeutic window is made or implied here.

⚠ **Second-ranked, and it creates no new work:** `RT-CARFILZOMIB.next.blocked_on` — already found by S41
(Finding 4) and independently re-verified here. Its `$0` class-level literature query is not gated by
`BLK-NO-EMC-DATA`; the referenced file
`research/literature/carfilzomib-class-clinical-2026-08-28.json` exists at HEAD. **Everything else in
this audit is a record correction: the work behind it is already done.**

---

## ⛔ 3 · THE PATCH A COMMITTED MANUSCRIPT ALREADY WROTE, AND THE GRAPH TOOK HALF OF

`research/manuscripts/degrader/selectivity-requirement-sizing.md` (committed, dated 2026-08-07, exists at
HEAD) is the specification `BLK-UNSIZED-REQUIREMENT` asked for. **Its §6 contains the graph patch,
verbatim, as pasteable JSON blocks (a)–(f).** Checking each against the graph:

| block | prescribes | applied? |
|---|---|---|
| (a) restate `BLK-UNSIZED-REQUIREMENT` | new `name`, `kind: requires_wet_lab`, `kind_history` | ✅ applied |
| (b) add `BLK-TCIP-INTERFACE-FLOOR` | a new blocker | ✅ applied |
| (c) `RT-TCIP.blockers_inherited` + two `remaining_unknowns` | | ✅ applied |
| (d) `RT-MONOVALENT` — `remaining_unknowns[1]` | | ✅ applied |
| (d) `RT-MONOVALENT` — `readiness.missing` replacement | *"the occupancy-to-output transfer functions … (MISSING-1, MISSING-2)"* | ✅ applied |
| **(d) `RT-MONOVALENT` — the `required_validation` row** | the ✅ DONE replacement, `blocked_by: []` | ⛔ **NOT applied** |
| **(d)'s flag on `next.best_next_action` and `timing.rationale`** | *"They should move on — the specification is written"* | ⛔ **NOT acted on** |
| (e) `RT-ASYMMETRIC.remaining_unknowns` append | | ✅ applied |

★ **Five of six blocks landed and the sixth did not, in the same route object where four of the five
did.** This is the one-of-a-pair defect class the `paper-hardening` skill already records, arriving in
the graph instead of in prose.

**What the graph still says, and what refutes it:**

- `RT-MONOVALENT.next.best_next_action` = *"Write down the selectivity requirement this route would have
  to meet, with its basis. It is $0 and it is what makes every later grade of this route meaningful."*
  ⛔ **REFUTED.** It was written down on 2026-08-07. The document's own §0 header: *"`BLK-UNSIZED-
  REQUIREMENT` is held by three routes — `RT-MONOVALENT`, `RT-TCIP` and `RT-ASYMMETRIC` … **This file is
  that statement.**"*
- `RT-MONOVALENT.timing.rationale` = *"…**nobody has stated** how much selectivity this route would need,
  and until someone does, the route cannot be shown to meet or miss it."*
  ⛔ **REFUTED twice over** — by that document, and by the blocker's own current `name` in
  `blockers.json`: *"The selectivity requirement **is now STATED for all three routes**, and three of its
  inputs are unmeasured dose-responses that only a bench produces."*
- `RT-MONOVALENT.required_validation[1].blocked_by` = `["BLK-UNSIZED-REQUIREMENT"]` on the entry *"A
  stated selectivity requirement this route would have to meet"*.
  ⛔ **REFUTED.** The sizing document §6(d) supplies the exact replacement, ending `"blocked_by": []`.

⚠ **`state.last_verified` on this route is `2026-08-06` — one day before the document that refutes it.**
The route has not been re-read since the artifact that answers it was committed, 26 days ago.

⛔ **What this does NOT do.** Writing a specification down is not evidence that the route is more
feasible — the sizing document's own §0 item 1 says exactly that, and nothing here contradicts it. The
thresholds remain forms with a range (0.50–3.49 kcal/mol, **not bounded above**), the transfer functions
`MISSING-1`/`MISSING-2` are unmeasured, and `BLK-UNSIZED-REQUIREMENT` stays on the route as a
`requires_wet_lab` blocker. **The correction removes a false to-do, not a barrier.**

---

## ⛔⛔ 4 · THE LARGEST FINDING: `strength: direct` ON TEN PIECES OF EVIDENCE THAT ARGUE AGAINST THEIR OWN ROUTE

The driver flagged `RT-SGK1`/`ART-NDRG1-PANEL-ATTRIBUTION` as the first case anyone had hit and asked
how many of the ~60 `strength: direct` entries are, on their own text, refutations or non-findings.
**Answer: ten, across nine routes. The first case is not the only case.**

`supporting_evidence` carries 81 entries: **`direct` 60, `class_inherited` 8, `surrogate` 7,
`transferred` 6.** `systems/schema/route.schema.json:62` admits only those four, with
`additionalProperties: false` on the entry — **so there is no value that means "this evidence argues
against the route"**, and the four available all read as support to any machine reader.

⭐ **THE DISCRIMINATOR IS NOT THE PROSE — IT IS THE ARTIFACT'S OWN GRADING FIELD, AND THAT IS THE
METHODOLOGICAL RESULT HERE.** A language scan of `what_it_supports` found 14 of the 60 and **missed
three of the ten** (`RT-ARGININE`, `RT-MDM2`, `RT-EZH2`), whose entry text is phrased as a neutral
measurement. `research/modalities/census-route-expression-grading.json` grades 16 routes and carries,
per route, a `direction_the_route_needed` and a `route_action`. Cross-referencing that field against the
graph's `strength` is mechanical and catches all of them:

| route | artifact | the artifact's own `route_action` / text | `strength` |
|---|---|---|---|
| `RT-ARGININE` | `ART-CENSUS-ROUTE-GRADING` | *"down-grade: the premise as stated is not supported"* | `direct` ⛔ |
| `RT-MDM2` | `ART-CENSUS-ROUTE-GRADING` | *"down-grade; the selection argument was the whole route and it is not supported"* | `direct` ⛔ |
| `RT-EZH2` | `ART-CENSUS-ROUTE-GRADING` | *"down-grade"* | `direct` ⛔ |
| `RT-POLQ` | `ART-CENSUS-ROUTE-GRADING` | *"down-grade, but record the alt-EJ elevation rather than burying it"* — needed *"alt-EJ up WITH HR down"*; artifact: *"the combination the class needs … is not present"* | `direct` ⛔ |
| `RT-MATRIX-SYNTHESIS` | `ART-CENSUS-ROUTE-GRADING` | *"re-scope: the premise must be restated in a form this reading does not already contradict"* | `direct` ⛔ |
| `RT-ALK-HIT` | `ART-CENSUS-ROUTE-GRADING` | *"demote and fold into the kinase paper as a corrected reading of a lead"* | `direct` ⛔ |
| `RT-SGK1` | `ART-CENSUS-ROUTE-GRADING` | *"keep at concept; the corroboration this route was registered for did not arrive"* | `direct` ⛔ |
| `RT-SGK1` | `ART-NDRG1-PANEL-ATTRIBUTION` | *"⛔⛔ REFUTED AS A DIRECTIONAL FINDING, 2026-09-02"* — the case already filed | `direct` ⛔ |
| `RT-PRAME-IMMTAC` | `ART-EMC-EXPRESSION-PANELS` | entry's own words: *"it points **against this route** rather than for it"* | `direct` ⛔ |
| `RT-TRABECTEDIN` | `ART-EMC-CLINICAL-REGISTRY` | n=2 EMC subjects, `orrEvents 0`, both stable disease; the arm-wide ~12.5-month median PFS **withdrawn** as an EMC figure | `direct` ⛔ |

**Verified from the artifacts, not the graph prose.** `research/modalities/emc-expression-panels.json →
gene_reads.PRAME` on `GSE24369`/`GPL6244`: `readable: true`, probe `8074856`, `n_EMC_with_a_value: 6`,
`n_comparator_with_a_value: 29`, EMC `mean_z −0.468` against comparator `mean_z −0.464`,
`mean_array_percentile 0.3026` — which is the *"delta = −0.004 … at the 30th array percentile"* the entry
claims, reproduced from the file. `census-route-expression-grading.json → routes.RT-MATRIX-SYNTHESIS`
carries `direction_the_route_needed: "CS biosynthetic and sulfation machinery HIGH in EMC"` beside the
`route_action` above.

★ **The three the language scan missed are the reason this matters.** *"ASS1 is not low in EMC tumour
tissue on either readable array platform, so the selecting feature for arginine deprivation is absent at
transcript level"* is a complete, careful, correct sentence — and it is a **refutation filed as
support**. A machine reader counting `direct` evidence per route reads `RT-ARGININE`, `RT-MDM2` and
`RT-EZH2` as each having one piece of direct evidence FOR them.

⛔ **What is NOT proposed.** Four of the four schema values would be a lie for these ten, and the schema
fix has a blast radius this seat does not own. The patch file therefore proposes **no `strength` edit**;
it proposes the same carrier the driver used on `RT-SGK1` — an explicit *"read this text, not that
field"* clause in `what_it_supports` — plus a ledger row for the schema. ⚠ **That is a mitigation and not
a fix: the field still reads green.**

⚠ **Six further `direct` entries are mixed rather than refuting** and are left alone: `RT-TRABECTEDIN-
PPARG` and `RT-PPARG-DOWNSTREAM` on `ART-EMC-EXPRESSION-PANELS` (a real positive with a stated
adipogenic ceiling), both `RT-FUSION-OUTPUT` entries, `RT-CHAPERONE`, `RT-DIAGNOSTIC-PATHWAY`. And one
is **correct usage of a negative**: `RT-RXR`/`EV-ZETTERSTROM-1996` — a published primary negative is
`direct` support for a route that IS a closure.

---

## ⛔ 5 · THE TRIGGER THAT ALREADY FIRED — FIVE ROUTES WAITING ON DATA THEY HAVE READ

`research/modalities/emc-expression-panels.json` (`ART-EMC-EXPRESSION-PANELS`, committed,
`generated_utc: "2026-08-29T12:51:32+00:00"`) holds **20 reads** over **two EMC tumour series** —
`GSE24369` on `GPL6244` (`_status: "read"`, 42 samples, 28 459 probes, 6 EMC vs 29 comparator sarcomas)
and `GSE4303-GPL3290` (10 vs 6) — with a `reads.control` arm that reads NR4A3 and ENO3 as must-be-up and
MKI67 as must-be-flat before any panel is scored, and `gene_reads` over **479 symbols**.

Five routes carry `timing.revisit_trigger: ["TECH-EMC-EXPRESSION-DATA"]` and a next action or a
`readiness.missing` phrased as though that read has not happened:

| route | the claim | what refutes it |
|---|---|---|
| `RT-TCRT-CTA` | `readiness.missing: ["a real EMC expression series"]`; `next`: *"Keep registered for automatic re-grade when EMC expression data lands."* | ⛔ **REFUTED.** Two series, both `_status: "read"`, with a passing control. `last_verified: 2026-08-05` |
| `RT-FAP-RLT` | `readiness.missing: ["any measurement in EMC"]`; same next action | ⛔ **REFUTED.** `gene_reads.FAP` → `readable: true`, probe `8056257` on `GPL6244`, `n_EMC_with_a_value: 6`. ⚠ The route's imaging and dosimetry halves are genuinely open — it is the word **"any"** that is refuted |
| `RT-CART-SURFACE` | `next`: *"The antigen search re-runs automatically when EMC expression data lands."* | ⛔ **REFUTED.** `reads.read_8_SURFACE_ANTIGEN` ran, with a `cross_platform_board` and a `the_route_named_addresses` block. ⚠ `readiness.missing: ["a selective surface antigen"]` **HOLDS** — the artifact's own `⛔_what_no_reading_here_can_establish` refuses surface localisation, density, tumour-vs-stroma and normal-tissue restriction |
| `RT-TRABECTEDIN-PPARG` | `next`: *"Hold the ask until the PPARγ direction can be stated. Re-grade automatically when EMC expression data lands."*; `next.blocked_on: ["BLK-NO-EMC-DATA"]` | ⛔ **REFUTED by its own `required_validation[0]`**: *"✅ THE READ WAS TAKEN 2026-08-24 … AND IT DOES NOT ESTABLISH A DIRECTION."* The named trigger fired and the answer was negative |
| `RT-PPARG-DOWNSTREAM` | `next`: *"What remains is a PPARγ activity readout in EMC, which is blocked by BLK-NO-EMC-DATA"*; `next.blocked_on: ["BLK-NO-EMC-DATA"]` | ⛔ **REFUTED by its own `required_validation[1]`** (*"✅ TAKEN 2026-08-24"*) and its own `readiness.missing[0]` (*"the target-gene activity readout itself is **DONE**"*), both naming `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-SI.md §S4` — **which exists at HEAD, at line 179: `## S4 · The PPARγ receptor-activity reading, and its adipogenic ceiling`**. And `required_validation[2]` names the true residual as a study-design limit on `BLK-NO-WET-LAB`, *"so a further bulk expression cohort does not lift it"* |

★ **The shape is identical in all five and it is worth naming: a route was updated in one field and not
in its neighbour.** `RT-PPARG-DOWNSTREAM` is the sharpest — three fields carry the 2026-08-24 read
correctly and `next` still says the read is what's missing, in the same object, with
`last_verified: 2026-08-28`.

**STALE, not refuted — `TECH-EMC-EXPRESSION-DATA` itself.** Its `current_state` is `"early_signals"` and
its sole `evidence` line reads *"The weekly scan fired on this trigger with new hits in its most recent
run; **none has yet been graded as a usable deposit**."* Two series were graded usable and read.
⛔ **This memo grades that STALE and refuses REFUTED**, because the technology's `name` specifies *"a
fetchable public EMC RNA-seq or proteomics deposit"* and what landed is decade-old microarray — a
different modality, and the honest reading is that the *capability* its `why_it_matters` describes
("per-antigen expression confirmation on real EMC tissue") arrived by a route its `name` does not cover.
**20 routes carry this technology as a revisit trigger**, and its `pending_signals[0]`
(`PMC13039535`, `seen_on: "2026-08-08"`) still reads `graded: false` — ungraded for 25 days.
⚠ `technologies.json` is outside this audit's population; recorded as adjacent, with a ledger row.

---

## 6 · Findings that are internal to the graph — checked, small, and included for completeness

- **Seven routes have `blockers_inherited: []` while one of their own `required_validation` entries
  carries a `blocked_by`**: `RT-PANNR4A-EXVIVO`, `RT-RXR`, `RT-ENDPOINT-CHOICE`, `RT-FUSION-OUTPUT`,
  `RT-MDT-LUNG`, `RT-SCHEDULING`, `RT-DIAGNOSTIC-PATHWAY`. S41 found `RT-ENDPOINT-CHOICE`; the
  mechanical population is seven. **Widening it: 27 routes carry an entry-level `blocked_by` that is
  absent from `blockers_inherited`** — overwhelmingly `BLK-NO-WET-LAB` (24 of 27). Whether route-level
  inheritance is *meant* to be the union of its entries is a graph-semantics question this seat does not
  own; it is raised, not patched.
- **Zero contradictions of the obvious kinds:** no blocker appears in both `blockers_inherited` and
  `blockers_retired` on any route; no route has `status: blocked` with no blocker anywhere; no dangling
  blocker id.
- **`next.cost` is `"$0"` on 77 of 77 routes** (76 exactly, one with the rider *"$0 to ask; the run
  itself points at the pricing home"*). Each was checked against the action it prices and each holds —
  every action is write, publish, ask, hold, or a CI/literature fetch. ⚠ **But a field with one value
  across the entire population discriminates nothing**, and a reader scanning for a cheap route learns
  nothing from it. Noted as a design observation, not a defect.
- **`BLK-NO-FIELD-ATTENTION-MEASUREMENT` is referenced by no route** — and that is deliberate and
  documented: its own record says *"It does not hold any ROUTE, and `systems_check` [B3] will say so —
  that is honest rather than mis-scoped. It holds the PAPER."* **HOLDS.** ⭐ Worth a reader's eye
  anyway: its `retired_by_action` opens *"FREE AND TAKEABLE TODAY"* and names a $0 term census over 554
  committed records, and because no route carries it, **nothing in the route ranker will ever surface
  it.**
- **`RT-VACCINE-COMBINATION` is the only route with no `grade_pointers` key.** Schema-optional; noted.
- **Three `required_validation` entries omit `blocked_by` entirely** (`RT-TRABECTEDIN-PPARG[0]`,
  `RT-PPARG-DOWNSTREAM[1]`, `RT-PRAME-IMMTAC[0]`) where the other 145 carry it. All three are
  already-answered requirements, so the omission is benign in effect — but it is an unenforced optional
  key doing load-bearing work.

---

## 7 · Verdict counts

| verdict | claims | |
|---|---|---|
| **REFUTED** | **24** | 14 route-field claims (§2 §3 §5) + 10 `supporting_evidence[].strength` (§4) |
| **STALE** | **5** | the five `timing.revisit_trigger: TECH-EMC-EXPRESSION-DATA` claims on routes whose own records say the read was taken |
| **UNVERIFIABLE** | **82** | 53 `next.best_next_action` naming no artifact, date, id or ✅ marker (of 58 such; 5 are refuted above) + 29 non-empty `blockers_retired` asserting a per-route retirement of a blocker that is live globally, with no evidence pointer on the assertion |
| **HOLDS** | **1,012** | |
| **UNMEASURED** | **77** | **named, not zero — see below** |
| **total** | **1,200** | |

⛔ **THE UNMEASURED ROW IS `grade.value`, ALL 77, AND IT IS NAMED RATHER THAN CLAIMED CLEAN.** What was
measured is the pointer: all 77 `grade.owner` blocks name a file, all 29 distinct files exist at HEAD,
zero absent. What was **not** measured is whether each grade's prose still matches the current text of
the document that owns it — several grades run to 2,000 characters of argument over a dozen figures, and
re-deriving one is a per-route read of a manuscript section, not a mechanical check. **Closing this row
is a separate seat**, and the honest state of it today is UNMEASURED rather than HOLDS.

⚠ **One further honest limit.** `readiness.attainable_today` (77 claims: 59 `internal_note`, 8
`preprint`, 5 `experimental_proposal`, 3 `journal_submission`, 1 `chemrxiv`, 1
`reproducible_workflow`) is counted under HOLDS on the strength of its owner document existing. Whether
a route marked `preprint` is *actually* at preprint quality is a judgement, not an artifact check, and
was not attempted.

---

## 8 · Ranked by whether they make a route MORE takeable

1. ⭐⭐ **`RT-COVALENT-PROBE`** — the only finding that makes unrun work available. **$0, CPU/stdlib
   only, no GPU, no fetch, no person, no decision for trimcrae.** §2 has the cost breakdown.
2. **`RT-CARFILZOMIB`** — $0 literature query, already found by S41 and re-verified here; no new work
   created by this memo.
3. **Everything else is a record correction.** `RT-MONOVALENT`, the five expression-trigger routes and
   the ten `strength` entries all describe work that is already done or evidence that already exists.
   Correcting them changes what the next session believes, not what it can run. ⛔ **And that is the
   point of the class: the cost of these is paid by whoever reads the graph next, which is why
   AUT-PD-104 was filed after the same defect propagated into a manuscript.**

---

## What I changed

- `research/autonomy/sprint-2026-09-01/S54-ROUTE-CLAIMS-AUDIT.md` — this file.
- `research/autonomy/sprint-2026-09-01/S54-proposed-route-claim-fixes.json` — a **proposed, unapplied**
  patch with a per-route justification. ⛔ Written as instructions. `systems/graph/*.json` was NOT
  edited: a graph edit is what makes the ranker start offering a route, and another seat was editing
  `blockers.json` during this audit.

## What I did not touch

`systems/graph/*.json` · `systems/views/` (generated) · `research/manuscripts/` ·
`research/autonomy/research-ledger.json` · every other path in the repository. No git write command was
run.

## Ledger rows the driver should write

| what | kind | state | serves |
|---|---|---|---|
| **`RT-COVALENT-PROBE.next.blocked_on` names a blocker whose own `retired_by_action` is that route's own next action, priced `$0` by the blocker.** Clear the field and build the reactivity-weighted accessibility criterion against NR4A1 C551. $0, CPU only. **The only takeable route this audit produced.** | `experiment` | `queued` | `RT-COVALENT-PROBE` |
| **`systems/schema/route.schema.json:62` has no `strength` value meaning "this evidence argues against the route", and ten of 60 `direct` entries are refutations or non-findings.** Nine routes, listed in S54 §4. The schema fix has a blast radius; the mitigation is an explicit "read this text, not that field" clause per entry. | `process_defect` | `queued` | — |
| **Apply `S54-proposed-route-claim-fixes.json`** — 24 refuted claims across 11 routes, no grade change, requires a `systems/views` regeneration. | `process_defect` | `queued` | — |
| **`selectivity-requirement-sizing.md` §6 carries a six-block graph patch; five blocks were applied on 2026-08-07 and the sixth was not.** A manuscript that writes its own graph patch has no mechanism that checks the patch landed. Worth a guard, not only a fix. | `process_defect` | `queued` | `RT-MONOVALENT` |
| **`TECH-EMC-EXPRESSION-DATA.current_state` is `early_signals` with evidence *"none has yet been graded as a usable deposit"*, while `emc-expression-panels.json` holds 20 reads over two graded EMC series.** 20 routes carry it as a revisit trigger; `pending_signals[0]` has read `graded: false` for 25 days. Re-grade the technology row. $0. | `process_defect` | `queued` | — |
| **27 routes carry an entry-level `blocked_by` absent from route-level `blockers_inherited`** (24 of them `BLK-NO-WET-LAB`); seven of those have `blockers_inherited: []` outright. Decide the graph semantics, then guard it. | `process_defect` | `queued` | — |

## Gates

None run — this seat wrote two new files under `research/autonomy/sprint-2026-09-01/` and touched no
manuscript, SI, citation, `systems/` path or generated artifact. `./scripts/preflight.sh` is the
driver's to run before the commit that lands them.
