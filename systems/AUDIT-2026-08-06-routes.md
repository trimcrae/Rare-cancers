---
id: DOC-AUDIT-ROUTES-2026-08-06
title: Route framing audit — all 40 L2 routes, one ST- family at a time
level: cross-cutting
kind: incident
status: live
purpose: >
  Record what a per-route framing audit found beneath the machine-checkable layer, before more
  science is bought. Every finding here was invisible to `systems_check.py --check`, which was
  green at 0 ERROR throughout.
scope: >
  The 40 `RT-*` routes in `systems/graph/routes.json` and the documents that grade them. Not the
  biology — no finding here re-grades a scientific result; findings are about whether the record
  tells the truth about what is already known.
audience: [maintainers, autonomous research agents, external reviewers]
date: 2026-08-06
last_verified: 2026-08-06
related: [DOC-ARCHITECTURE, DOC-CONVENTIONS, DOC-TAX-BLOCKERS]
---

# Route framing audit — 2026-08-06

> **Why this exists.** trimcrae, 2026-08-06: *"This is an audit to make sure our framing is
> bulletproof before we start doing more science."* One subagent per route, stepped through one
> `ST-` family at a time.

**The baseline that makes this document necessary.** `systems/systems_check.py --check` was
**0 ERROR · 12 WARN · 5 INFO** before the audit started and after every fix landed. The schema layer,
the pointer layer, the link layer and the hierarchy layer all hold. ⛔ **So every finding below is one
a green build cannot see** — the checker validates that a field exists, resolves and is well-formed;
it cannot read the sentence in it and ask whether that sentence is true.

## Method

Eleven checks per route, defined once and given to every auditor identically: grade-pointer truth ·
evidence truth and `strength` honesty · `instruments.support` legality · state honesty · blocker
completeness **and kind** · `distinct_from` · `required_validation` honesty · `readiness`/`timing` ·
the inherited claim ceiling · closure integrity · a repo-wide contradiction sweep.

Auditors were **read-only** and returned findings with `file:line` evidence; fixes were applied by
the orchestrator after independent re-verification. That split is load-bearing — see
[what nearly went wrong](#what-nearly-went-wrong-in-the-audit-itself).

## Cross-cutting findings

These came from a mechanical sweep over all 40 routes and could not be seen from inside any one route.

### X7 · ✅ FIXED — the whole route portfolio was outside the language-discipline linter

`lint_claims.py` `DEFAULT_TARGETS` was **7 files**. `systems/views/L0-ecosystem.md`, the 9 `L1-st-*.md`
and all **40 `L2-rt-*.md`** were not among them — so every word of framing for every therapeutic route
(`rationale`, `purpose`, `grade.value`, `closure_note`) was unenforced against R1–R5.

This is the third instance of one pattern, and `lint_claims.py`'s own header documents the first two:
`views/plan.md` was added when moving THE ORDERED PLAN silently dropped ~1,580 lines from the linted
set (*"a linter whose scope shrinks while its pass rate improves is the worst possible signal"*), and
`outreach-emails.md` was added because *"the one document written to leave the building was the one
document nothing linted."* **The same migration that moved the plan moved the portfolio, and only the
plan was carried across.**

Fixed by globbing rather than listing — a hand-typed list of 50 paths leaves the next new route
outside the linter by default, which reproduces the failure instead of fixing it. Coverage went
**7 → 57 files, still 0 ERROR**.

### X7b · OPEN — 15 of the 18 documents that OWN a route grade are still unlinted, and cannot be added as-is

Measured: adding them yields **12 ERROR**, and **all 12 are false positives** — `CURE ID` (the
FDA/NCATS registry), the identifier `TRG-ASO-EFFICACY-ACCESSIBILITY`, *"the first-ever approved
degrader"* (vepdegestrant, not our work), a `Keywords:` line, an external *Nature* 2019 paper called a
landmark. Adding them would turn `main` red on twelve non-violations, and the linter's own design
brief says why that is worse than no linter. **The fix is three clearance rules first** (registered
identifiers and proper nouns; sentences about a named external agent or publication; keyword and
citation lines), then the files. Engineering is free; the sequencing is the point.

### X8 · ✅ FIXED — a permanent blocker missing from routes that plainly carry it

`BLK-NOT-FUSION-SELECTIVE` (*"the route also engages the wild-type protein"*, kind
`fundamental_biological_limit` — **permanent, retired by nothing**) was carried by RT-DEGRADER and by
none of the other four ST-PROXIMITY routes whose only handle is the same shared LBD object.

**Three auditors reached this independently, from three different directions, none seeing the others.**
The fourth — RT-ANDGATE's — *declined* it, citing `target-route-options.md:629-632`, which explicitly
scopes RT-EWSR1-PROTEIN's closure so it does not close the AND-gate. That the one route with a
documented exemption was correctly exempted is what makes the convergence evidence rather than four
agents pattern-matching the same prompt.

### X9 · ⛔ OPEN, BLOCKING — the "AF1 → EWSR1-LC swap" premise is contradicted by the repo's own inventory

Four documents state that the fusion *replaces* NR4A3's AF1 (1–260) with EWSR1's low-complexity region
— *"a domain the disease deletes."* The repo's own committed artifacts say otherwise:

| source | statement |
|---|---|
| `objects.json` → `OBJ-FUS-T1` | `EWSR1(1–431) :: 1 junction residue :: **NR4A3(1–626)**` |
| `objects.json` → `OBJ-MODEL-E7E3` | `EWSR1(1–264) :: **NR4A3(1–626)**` |
| `fusion-object-inventory.md` | the fusion *"**additionally contains** NR4A3 residues 1-372"* |
| same, residue table | K37, K72, K85, K136, K178, K194, K249 — all NR4A3 AF1 — **INVARIANT, 9/9** |

`NR4A3(1–626)` is the full coding region. **Nothing is deleted; EWSR1-LC is additive.**
`target-route-options.md:672` contains the collision in one sentence: *"the chimera does retain
NR4A3's own AF1 replaced by EWSR1-LC"* — retained and replaced at once. The roadmap already states the
correct additive form at `:585`, so the repository holds both readings simultaneously.

⛔ **The expensive consequence.** `RT-6MP` is `status: closed`, `closure_kind: definitional` —
**permanent, no revival trigger, filed "never retry"** — and its whole closure is this premise:
*"A ligand whose whole mechanism lives in a domain the disease deletes cannot act on the chimera at
any dose."* 6-MP is the one **approved** drug that activates NR4A3, which the repo itself calls *"the
cheapest imaginable entry."*

⚠ **This audit does not rule that 6-MP works** — reopening the route is a scientific call, not an
audit action. Two things are established without any biology: the repo contradicts itself, and
`definitional` (the most permanent value in the enum) cannot rest on a contradicted premise. Left
open deliberately for trimcrae; it is handled in the ST-REPURPOSING pass, where RT-6MP lives.

### X1 · ✅ PARTLY FIXED — `revisit_trigger` that unblocks nothing the route is blocked by

ARCHITECTURE §5.3: the field exists to make *"let's wait"* a monitored condition. On four routes the
condition could fire in full and the route would still be blocked. RT-GLUE and RT-RIPTAC fixed.
**Still open: RT-VACCINE and RT-TCR-IMMTAC**, which inherit only `BLK-ANTIGEN-COLD` — permanent — while
carrying a `revisit_trigger`. A permanent blocker with a reopening condition beside it is the exact
conflation the blocker taxonomy forbids; both are in the ST-IMMUNO pass. **RT-SYNPROMOTER** (ST-NUCLEIC-ACID) is the fourth.

### X2 · OPEN, MINOR — route→technology `revisit_trigger` edges are one-directional on 8 routes

The route names a `TECH-*`; that technology's `unblocks.routes` omits the route. Nothing enforces
reciprocity, though `[T1]` enforces exactly this shape for technology↔forecast. Consequence:
`fan_out` is computed from `unblocks`, and `fan_out` is what L0's *"highest-leverage things to wait
for"* table ranks by — so the portfolio's watch-list ordering is computed from an incomplete edge set.

### X3 · OPEN, MAJOR — `fails_on` is one field name with two meanings, in neither schema

`relations.json` defines it one way on `distinct_from` (*"which blockers the distinction turns on"*)
and the other way on `sub_forms` (*"what it fails on"*). `route.schema.json` defines **neither field**;
both pass only via `additionalProperties: true`, so the route ids and blocker ids inside them are
validated by nothing. They all resolve today (verified: 0 unresolved, 0 one-directional pairs) — a
latent hole, not a present error.

### X6 · OPEN, MAJOR — CONVENTIONS §4.1 and ARCHITECTURE §6 disagree, and a correct route sits in the gap

CONVENTIONS says `closed` *"carries no `TECH-*`"*; ARCHITECTURE says a **permanently**-closed route may
carry none. `RT-RXR` is exactly the separating case — `closed`, `closure_kind: premise_false` (not
permanent), carrying `TECH-RXR-HETERODIMER-REPORT`, with its own `closure_note` arguing the case. **The
route is right and CONVENTIONS is the defect.** It matters because CONVENTIONS is the table an agent
consults when setting a status, so as written it teaches that a correct row is an error — which is how
a correct row gets "fixed" into a wrong one. **Do not "fix" RT-RXR**; it is the cleanest-reasoned
closure in the registry.

### X10 · ⛔ OPEN, MAJOR — the `support` legality rule has a second door, and it is unguarded

`instruments.support` is legality-checked: an instrument whose known-answer control failed, or that has
none, may not appear there. Across all 40 routes, **0 illegal entries** — the rule works.

But `supporting_evidence[].ref` accepts the **same instrument ids** and is checked by nothing. Measured
across all 40: **9 citations of control-failed or control-free instruments**, eight of them at
`strength: direct`.

| route | instrument | control | strength | verdict |
|---|---|---|---|---|
| RT-METHODS-PAPER | V5, V7, V21 | `fails` ×3 | `direct` | ✅ **legitimate** — this route's thesis IS the failure record; the failures are the result |
| RT-SYNLETH-DEP | INS-DEPMAP-KO | `fails` | `transferred` | ✅ honestly labelled |
| RT-DEGRADER | V13, V14, V15 | `fails`/`none`/`mixed` | `direct` | ⚠ the lead route's whole evidentiary base is three uncontrolled instruments |
| RT-COVALENT-PROBE | V17 | `fails` | `direct` | ✅ fixed — entry removed |
| RT-UBIQ-SELECTIVE | V18 | `none` | `direct` | ⚠ open |

⛔ **The fix is not "delete them"** — RT-METHODS-PAPER *needs* them, and deleting would destroy the one
route whose deliverable is the honest failure record. The defect is that `strength`'s enum
(`direct`/`transferred`/`class_inherited`/`surrogate`) is about **provenance distance**, and has no value
meaning *"this instrument has no valid control."* So a reader sees `direct` and reads "validated", when
the right reading is "measured on this system by an instrument that failed its own positive control" —
a different and much weaker claim. CONVENTIONS §5 invariant 2 states the rule in prose; nothing
implements it on this field.

⚠ Related, found in the same sweep: `route.schema.json` says `supporting_evidence` *"may be empty ONLY
for a route at maturity `concept`, **and the checker enforces that**"*. **Nothing implements it** —
`concept` appears nowhere in `systems_check.py`. **11 routes at `maturity: computed` carry an empty
`supporting_evidence`.** A schema that describes an enforcement that does not exist is the same
two-homes failure `check_document_frontmatter` was written to close, one collection over.

## ST-PROXIMITY — 7 routes, all 7 audited

**Every one returned DEFECTIVE.** Not one was a schema problem.

| route | most severe finding | status |
|---|---|---|
| RT-DEGRADER | `work_state: in_work` with `running_job` naming lanes that do not exist — census `n_instances: 0`, `plan.json` has **zero** `~` items, roadmap says *"NOTHING BILLING on Vast"* | ✅ fixed |
| RT-RIPTAC | `rationale` asserted *"partial selectivity still gives a therapeutic effect"* — a direct breach of the family's third limitation, and textbook selectivity-equals-window reasoning | ✅ fixed |
| RT-ANDGATE | recorded `maturity: concept` (*"no computation"*) against **three tracked model artifacts** and a 404-line manuscript | ✅ fixed |
| RT-UBIQ-SELECTIVE | its closure rests on the X9 premise; `strength: direct` on a control-free instrument | ⚠ partly — X9 open |
| RT-GLUE | `rationale` inverts its own grade owner: removals stated as gains, when the register says *"it removes handles rather than adding them"* | ⚠ partly |
| RT-TCIP | filed `closure_kind: instrument_limit` with **no instruments and nothing failed**; *"retires R9/R10"* is false and is stated in the binding roadmap | ⚠ partly |
| RT-AF3-INTERFACE | carried only the degrader-architecture blocker, though its admissible interfaces include a non-E3 one | ✅ fixed |

### Applied this pass

- `BLK-NOT-FUSION-SELECTIVE` → RT-RIPTAC, RT-GLUE, RT-UBIQ-SELECTIVE (X8); `BLK-R4-BINDS` →
  RT-UBIQ-SELECTIVE; `BLK-NO-WET-LAB` → RT-RIPTAC; `BLK-INDUCED-COMPLEX` → RT-AF3-INTERFACE;
  `BLK-UNSIZED-REQUIREMENT` → RT-TCIP.
- RT-RIPTAC `rationale` and `purpose` rewritten to state the mechanism honestly — on this target the
  bound protein is the LBD the paralogues share, so engagement outside the tumour is cytotoxic by the
  same mechanism, and partial selectivity is a **liability** here rather than a tolerance.
- RT-DEGRADER: `work_state` → `future`, `running_job` deleted, `feasible_today` → `false` on the
  ternary item (the only route of five carrying that blocker kind to claim `true`), V14/V15 disclosed,
  `grade_pointers[0].asserts_grade` → `true`, and `closure_note` scoped so *"every one … is an
  instrument limit"* no longer reads across seven blockers, two of which are not.
- RT-ANDGATE → `complete`/`computed`; RT-TCIP `closure_kind` → `open`; RT-GLUE and RT-RIPTAC
  `revisit_trigger` widened to technologies that actually unblock them.
- `RT-TCIP.closure_kind` also corrected in the **legacy registry mirror**
  (`research/manuscripts/emc-systems-map.json`) — caught by `[L3]`, which is rule 1 working.

### Left open deliberately

X9 and its RT-6MP consequence; the RT-TCIP *"retires R9/R10"* correction, which touches the binding
roadmap and three other documents and so belongs in one deliberate commit; the RT-GLUE `rationale`
inversion, which has propagated to `technologies.json`; and the unverified-citation flag on
`EV-EB-TCIP-2025` (DOI absent from `verify-refs.yml` and from `fact-check-log.md`, while the graph
quotes it verbatim with no `provenance_flag`).

## ST-OCCUPANCY — 3 routes, all 3 audited

**All 3 DEFECTIVE.** The family's own limitation — *"nobody has stated how much paralogue selectivity
this family would need, so 'the requirement is smaller here' is not a claim this repository can make"* —
was breached by all three, each in a different way.

| route | most severe finding | status |
|---|---|---|
| RT-ASYMMETRIC | rested on a premise the repo **retired three days before the route's own `last_verified`** | ✅ fixed |
| RT-MONOVALENT | `BLK-PARALOGUE-DDG` named by its own `sub_forms` and absent from `blockers_inherited` | ✅ fixed |
| RT-COVALENT-PROBE | `BLK-PARALOGUE-DDG` in `blockers_retired`, **unearned** — the one route acting on the very pocket the blocker is about | ✅ fixed |

### RT-ASYMMETRIC — the retired exposure lever

`rationale` and `remaining_unknowns` both said NR4A2 sparing is *"unbounded in both directions"*, so
*"a molecule only has to win decisively against one of them."* `nr4a2-sparing-bound.json` returns
`decision: "BOUNDED"` — MGI complete-penetrance neonatal lethality (PMID 9092472/9608532), and across
51 HPA tissues NR4A2 co-expresses with NR4A3 in **47**, is dominant in **0**, unbuffered in **0**. The
roadmap had already restated the brief in its harder form; the route record was the last live document
still on the retired lever, and its `last_verified: 2026-08-05` **post-dates the 2026-08-03 result**.

Rewritten to the measured form: both constraints molecular, the asymmetry a difference in *kind* (a
combination genotype vs complete developmental loss), and carrying the caveat the source artifact names
`caveat_that_must_travel_with_any_result` — a germline knockout bounds developmental, complete,
lifelong loss, while a degrader is adult, transient and incomplete, so **a KO phenotype sets the
ceiling of concern and never the expected effect of a molecule.** That clause was in the paper and not
in the graph.

### RT-MONOVALENT — the `sub_forms` ruling

The only route of 40 using `sub_forms`, a field **no checker covers** (X3). The open question was
whether a route must carry the union of its sub-forms' blockers. **Ruled (b), a gap** — the decisive
argument being internal: the route already applies the **union** rule to the covalent sub-form's
blocker (`BLK-REACH-CATEGORICAL`, which the memo says has *no bearing* on the non-covalent form) while
applying **intersection** to the non-covalent form's. Two rules at once, and the asymmetry is the whole
defect. Its own grade owner settles it: *"The two sub-forms fail on opposite blockers, so there is no
version that clears both."*

⚠ Consequence beyond one row: the generated view renders `sub_forms` **nowhere**, so the split the memo
calls *"the memo's organizing fact"* is invisible in every generated output — and the board showed the
portfolio's only LBD-directed small-molecule route as escaping the program's central selectivity
blocker.

### A published error in the legacy mirror

`emc-systems-map.json` cited `INS-MONOVALENT-REACH` as `instruments.support` — the exact mis-filing
the graph fixed and pinned a test against — and `emc-systems-map.md` **printed** *"cited as SUPPORT by
RT-MONOVALENT"* under a heading reading *"Citing one as support is a checker failure."* Neither checker
could see it: `[L3]`'s `SHARED_ROUTE_FIELDS` omits `instruments`, and the map's own `I1` reads only
`known_answer_control.state` (`passes`), while the usability that condemns it is computed transitively
through `inherits_limits_from` (V3 inconclusive, V17 fails). Fixed.

### Stale branch-drift warnings, corrected on the same pass

`path-family-synthesis.md` warned in five places that artifacts were `main`-only or branch-only,
including *"the largest result on this page is absent from the branch these registers were written
on."* Re-measured with `git cat-file -e` against both refs: **all five are on both, ten of ten
present.** The drift was real when written and is reconciled now. ⛔ **A drift warning that outlives its
drift is not harmless caution** — it tells the next session that committed artifacts are unsafe to
quote, and it spends the force of a ⛔ on a fixed condition, so the next real one reads as noise.

## ST-FUSION-DIRECT — 3 routes, all 3 audited

All three are `dead`/`closed`, so **check 10 (closure integrity) was the whole audit** — a closed route
is the most expensive record to get wrong, because nothing revisits it.

| route | verdict | most severe finding | status |
|---|---|---|---|
| RT-EWSR1-PROTEIN | **SOUND-WITH-NITS** — the first non-defective route in the audit | `closure_note` broader than what its own grade owner argued | ✅ fixed |
| RT-FET-LC-LIGAND | DEFECTIVE | `definitional` closure with a load-bearing **empirical** step | ⚠ open for trimcrae |
| RT-DBD | DEFECTIVE | permanent closure whose only blocker is **non-permanent** | ✅ fixed |

### X11 · ⚠ OPEN for trimcrae — a permanent closure with an empirical step inside it

`RT-FET-LC-LIGAND` is `closure_kind: definitional` — one of only two PERMANENT kinds, unfalsifiable by
any future capability. Its closure decomposes into two steps and **only the first is definitional**:

- **S1, definitional and airtight:** a ligand defined by the shared FET-LC feature engages wild-type
  EWSR1, because the fusion's EWSR1 portion *is* wild-type EWSR1 sequence — present in all nine
  surviving breakpoint windows, `K144` INVARIANT 9/9.
- **S2, empirical, and it is what actually closes the route:** "binds wild-type EWSR1" does **not** close
  routes here — `BLK-NOT-FUSION-SELECTIVE` is held by 9 routes, three of which are live. What separates
  the closed from the live ones is whether the wild-type protein is *dispensable*, and that is a
  **DepMap surrogate number** (EWSR1 gene effect ≈ −1.2 against NR4A1 0.5 % / NR4A2 0.3 %), on a page
  that labels itself *"Surrogate evidence, not EMC data."* A trade over surrogate numbers is a
  judgement, not a definition.

⛔ **And the registry contradicts "essential ⇒ permanently dead" in principle:** `RT-CARFILZOMIB` is
`status: ready` on a **pan-essential proteasome**, and `RT-RIPTAC` is `parked` rather than closed on a
mechanism that *deliberately* poisons an essential protein.

Applied: the two legs are now separated in `closure_note`, the surrogate is cited as surrogate, and the
open question is stated in the record. **Not applied:** the ruling itself — either drop *"worse"* from
the grade and keep `definitional` honest, or keep it and re-file the closure as non-permanent.
Same shape as X9, and the same reason for leaving it: it is a scientific call.

⭐ **A clean negative result worth keeping.** RT-FET-LC-LIGAND's auditor was asked whether X9's
replaced/additive contradiction touches this closure. It does not, and the reasoning is worth
recording: X9 concerns the **NR4A3** side (is AF1 deleted or retained), while this closure's only
object-level premise concerns the **EWSR1** side (is the LC region present and wild-type). Under *both*
readings of X9 the EWSR1 LC is present and identical to wild-type. ⚠ But the two do collide
operationally: the contradicted X9 sentence lives at `emc-post-degrader-options.md:237`, **the same file
that owns this route's grade** — so whoever repairs X9 will be editing this route's grade-owning
document and must not let the sweep touch its §Route 15 text.

### X12 · ✅ FIXED — a permanent closure resting on a non-permanent blocker

`RT-DBD` is `closure_kind: arithmetic_over_fixed_fact` — never revivable — while its **only** blocker
was `BLK-PARALOGUE-DDG`, kind `requires_better_simulation_accuracy`: Group C, non-permanent, and
retired by `TECH-FE-CRYPTIC-POCKET`, the **highest-fan-out watch item in the portfolio**. A route filed
as never revivable inheriting its sole blocker from a live watch item is the conflation
`taxonomy/blockers.md` forbids, and the family's own limitation says such a route *"must never appear on
a watch list."* Corroboration that it was the wrong blocker: `TECH-FE-CRYPTIC-POCKET.unblocks.routes`
lists six routes and **deliberately omits RT-DBD**. Fixed by adding `BLK-NOT-FUSION-SELECTIVE`
(permanent), so the permanent closure now rests on a permanent blocker.

### X13 · ⛔ OPEN — a live manuscript proposes a route this family declares permanently closed

`research/manuscripts/fusion-coactivator-ppi-paper.md` (`status: live`) proposed drugging the EWS-TAD
and called it **"the fusion-unique EWS-TAD surface"**. That surface is the shared FET low-complexity
region — the exact object `RT-FET-LC-LIGAND` declares permanently closed. Verified: the file mentions
wild-type EWSR1 **zero times** (`grep -icE "wild-type EWSR1|WT EWSR1|endogenous EWSR1"` → 0), so its
entire selectivity argument compares only against wild-type NR4A3 and never considers the endogenous
protein carrying the identical domain.

⛔ **The structural point is worse than the wording.** This route is registered as **no `RT-*` at all** —
so no `distinct_from` edge, no blocker inheritance and no closure register reaches it. **A permanently
closed idea was being actively written up in a live manuscript, and the closure register had no way to
know.** The registry can only discipline what is registered in it.

Corrected in the manuscript with the superseded text retained. **Left open:** whether to register the
PPI route as an `RT-*` (which would give it a closure edge) — a scoping decision. ⚠ What survives the
correction is narrower and genuinely open: the BAF-retargeting mechanism as biology, and the
possibility that an interface *contact* is fusion-emergent even though the *surface* supplying it is
not. Nothing has established that.

## ST-NUCLEIC-ACID — 5 routes, all 5 audited

All 5 DEFECTIVE, and this family produced the audit's most serious single finding.

### X14 · ⛔⛔ BLOCKING — the ChemRxiv-queued ASO panel is built on a seam this repo RETRACTED

`RT-ASO` is Tier 1 rank 2, `next.best_next_action: "Publish"`, and was recorded `work_state: complete` /
`maturity: computed`. Its committed design panel was produced by `junction_aso.py`, which **never adopted
the 2026-08-03 exon off-by-two correction**: line 135 indexed a *coding*-exon offset table with a
*transcript* exon number, silently sliding to a neighbouring exon instead of raising.

**Measured, not inferred** — I re-verified every step from the primary artifacts:

| observation | value |
|---|---|
| committed seam `TTGTCCGTACAG` in the NR4A3 CDS | index **1081** |
| ⇒ NR4A3 resumes at residue | **361** |
| `fusion-neoantigen-retraction.json` grades `nr4_cds_nt: 1081` / `resumes_at_residue: 361` | **`SEAM_NOT_PRODUCED`** |
| corrected `nr4a3_resume_range_across_plausible_breakpoints` | **`[1, 1]`** |

So every design, GC value, cleavage count and the headline gapmer was computed against a chimera missing
**NR4A3 residues 1–360** — AF1 and the first zinc finger — that **no plausible breakpoint produces**.

⭐ **Why nothing caught it, and this is the transferable lesson.** The **EWSR1 side reproduced correctly
throughout**. So the two junction panels agreed with each other, and the paper reads that agreement as
confirmation: *"Both share the NR4A3 exon-3 right-side seam … **as expected**."* **Two artifacts agreeing
is not evidence when one defect produces both.**

⭐ **The sharpest part: the repo already knew how to handle this, and did it — for the other lane.**
`fusion-breakpoint-neoantigens.json` and `fusion-neoantigen-predictions.json` both carry a
`⛔_RETRACTED_SEAMS` banner, and `fusion-neoantigen-retraction.json` reads *"RETRACTED — DO NOT QUOTE ANY
PEPTIDE."* The neoantigen lane's retraction hygiene is exemplary. **The ASO lane runs the same defective
module and got none of it.** So this is not a repo that lacked the discipline; it is a retraction that
reached one consumer of a shared defect and not the other — the same shape as
`lint_claims.py`'s own note that *"a retraction that reaches some of its copies is not a retraction."*

⛔ **And three live documents, the binding roadmap among them, asserted the ASO lane was unaffected.** That
claim was true of `junction_breakpoint_scan.py`, which deliberately refuses the exon→CDS mapping — and
false of the lane, because `junction_aso.py`'s `FUSION_JUNCTION_MODE=real` path does the mapping with the
defective arithmetic. **The audit checked one of the lane's two modules and generalised.**

**Applied:** `junction_aso.py` now uses the repo's own `cut_offset`/`resume_offset` helpers, which *raise*
on a non-coding exon; the six affected artifacts carry a `_RETRACTED_SEAM` banner; `RT-ASO` is
`work_state: future` / `maturity: scoped` with the retraction as `remaining_unknowns[0]`; the three
documents are narrowed with the superseded text retained; and the paper is now in `lint_claims`.
⚠ **NOT regenerated — this is the required next step and it needs a network call to Ensembl, so it must
run in CI (CLAUDE.md §6).** Until it does, no design, GC value, cleavage count or the headline gapmer may
be quoted.

### X15 · ✅ FIXED — a decision the repo deferred to "whoever owns the registry", taken

Three vector-gated routes (RT-CRISPR-CAS13, RT-RIBOZYME, RT-SYNPROMOTER) pointed at
`TR-OLIGO-TUMOUR-DELIVERY` — the **oligonucleotide** trigger, whose own text reads *"Delivery is the ASO
route's one remaining gate."* `BLK-DELIVERY` and `BLK-VECTOR-DELIVERY` are separate blockers precisely
because, as `taxonomy/blockers.md` puts it, *"merging them would let one arriving imply the other had"* —
so an AOC or LNP platform landing would have read as reopening three routes that need a **vector**.

`research/method-watch-triggers.json` had already **found this and deferred it**: *"the two files disagree
about the grain, and whoever owns the registry should decide, not this file."* Nobody decided. Minted
`TR-VECTOR-TUMOUR-DELIVERY`, repointed the three routes, and added the matching watch row to
`method-watch.md` — which the map checker then verified, refusing my first attempt because I claimed a
watch-list entry that did not yet exist.

### Other ST-NUCLEIC-ACID fixes

- **RT-RIBOZYME** — `rationale` claimed *"the cleanest possible coupling of tumour identity to tumour
  death"* on a `maturity: concept` route with zero evidence. Same shape as RT-RIPTAC. Rewritten: the
  coupling is to the junction **sequence**, the vector delivers indiscriminately, and no trans-splicing
  specificity has been computed anywhere here.
- **RT-ASO-ASK** — stated a version of the ask **its own red team refuted** (F7: sparing cannot be shown
  in an EMC line, which may express little wild-type NR4A3). The paper carries the corrected design;
  the graph record was the last document on the refuted form. Rewritten, and `experiment_required` added
  — for an *ask* route, the pointer to the specification is the deliverable.
- **RT-SYNPROMOTER** — X1's fourth instance, plus two missing blockers.
- **RT-CRISPR-CAS13** — a `grade_pointer` at a document that never mentions the route (0 hits for
  `cas13|cas9|nuclease|intron`); *"perfect discrimination"* qualified.

### X16 · ✅ FIXED — `distinct_from` was checked by nothing and rendered nowhere

`grep -c distinct_from systems/systems_check.py` → **0**. Rendered in **0** of 60 views. The field exists
because *"one grade was applied to two routes that fail on OPPOSITE blockers"* — and for the portfolio's
most confusable pairs, the architecture's own outputs could not tell a reader which route owned which
claim. That is why so many `distinct_from` defects in this audit had survived: **nothing surfaced the
field, so nobody read it.**

Now rendered on all 40 route pages (32 have entries). ⭐ **It earned itself immediately:** the first
regeneration turned the build red on a claim-ceiling breach that had been sitting in a
`distinct_from.why` — *"This one **treats EMC** with a CAR against an EMC surface antigen"* — invisible to
`lint_claims` for as long as the field went unrendered. Fixed in the same pass.

Same commit also fixes the verb for closed routes: a `dead`/`closed` route's page said *"Blockers this
route RETIRES"* and *"✓ Already cleared by this route"*, crediting a permanently-dead route with clearing
the program's central blocker. It now reads **"Blockers this route never FACES"**, because a closed route
does not answer a blocker — its architecture never encounters one.

## ST-IMMUNO — 9 routes, all 9 audited

7 DEFECTIVE, 1 SOUND-WITH-NITS (RT-PANNR4A-EXVIVO). This family produced the audit's two **structural**
fixes, both of which turned findings into build failures rather than prose.

### X17 · ✅ FIXED — two new checker rules, which immediately caught 8 defects

The audit kept finding the same two shapes by hand. Both are now enforced:

**`[V4]` — `supporting_evidence[].ref` must resolve.** The `instruments.support` legality rule (`[V2]`)
had a second, unguarded door: `supporting_evidence[].ref` takes the same id space and was resolved by
nothing — it fed only the `cited_by` derivation, which treats an unknown id as an L5 row nobody cites.
**Four refs resolved to nothing**, including `ART-SURFACE-EXPRESSION` (cited by three routes, the home
of the repo's headline surface-antigen negative) and `EV-EMC-CLINICAL` (cited by two, at
`strength: direct`). **A `direct` strength on an id that resolves to nothing cannot be audited by
anyone**, and the build was green throughout.

⚠ Fixing it exposed a second defect underneath: `ART-SURFACE-EXPRESSION` was **one id for two different
artifacts** — the surfaceome selectivity screen (RT-B7H3) and the cancer-testis expression panel
(RT-PRAME-IMMTAC, RT-TCRT-CTA). Split into `ART-SURFACE-EXPRESSION` and `ART-CTA-EXPRESSION`.

**`[T7]` — a `revisit_trigger` must be able to move the route.** A trigger passes if it retires one of
the route's blockers *or* the technology names the route in `unblocks.routes`. The second arm is
deliberate: `TECH-JUNCTION-PMHC` has an empty `unblocks.blockers` **on purpose**, because what lands
there changes whether a *permanent* blocker stays decisive without retiring it — the honest shape, and
the check must not punish it. Caught all four X1 routes plus RT-PANNR4A-EXVIVO and RT-ANDGATE.

⭐ **The X1 resolution came from the routes' own fields, and it was neither option I proposed.** I asked
whether RT-VACCINE and RT-TCR-IMMTAC should drop their trigger or inherit `BLK-NO-EMC-DATA`. The auditor
refused both: dropping it violates CONVENTIONS §4.1/§4.5 (a `parked` route must name a `TECH-*`), and
adding the blocker would invent a data shortfall neither route claims — RT-VACCINE's own
`automation_outlook` says *"the immunogenicity question is not computational."* The right answer was
`TECH-JUNCTION-PMHC`, which **already existed, already named all three routes, and already declined to
claim the blocker**. The technology claimed the routes; the routes never claimed it back.

### X18 · ⛔ The claim ceiling is evaded by paraphrase, not by breach

Three breaches, none of which any `lint_claims` rule could see, because R1–R5 match *phrases*:

| route / file | the words | why it breaches |
|---|---|---|
| RT-ICI-TKI | *"an approved combination … is **the shortest path to a patient that exists**"* | clinical readiness, on real approved drugs, rendered one line above `state: ready` |
| RT-PRAME-IMMTAC | *"the reagent problem is already solved by someone else, and **the only question is whether EMC expresses the antigen**"* | collapses efficacy, safety and window into an expression question — and brenetafusp is **investigational**, not approved |
| `fusion-junction-neoantigen-paper.md` | *"**cannot, in principle, harm any normal cell**"* | a safety claim, and the only novelty test run compares against **two parent proteins**, never the proteome |

⛔ **And the last one exposed a design flaw in the linter itself.** I widened `R2-proteome-wide` to
catch *"absent from normal proteome"* and *"harm any normal cell"* — and the second still passed,
because `\bcannot\b` is a **DISCLAIMER MARKER**. For a safety claim the negation *is* the assertion:
*"cannot harm any normal cell"* is stronger than *"is safe"*, and the disclaimer detector read it as a
scope-out. Meanwhile on the same two files the linter flagged three *hedges* as errors — including the
literal disclaimer *"Ready to publish ≠ likely to cure."* **It was strict where it should have cleared
and blind where it should have fired.** A keyword rule enforces the sentence someone thought of, not
the claim.

### X19 · ⛔ A grade that is factually wrong for half its own route

`RT-B7H3`'s grade read *"not selective (BH q = 1.0)"*. Measured in `emc-surfaceome-scan.json`:

| antigen | `enrichment_vs_rest` | `selectivity_q` | verdict |
|---|---|---|---|
| CD276 (B7-H3) | 0.14 | **1.0** | not selective ✔ grade correct |
| NCAM1 (CD56) | **1.74** | **0.0** | **selective** — grade wrong |

CD56 is the second antigen in the route's own `display_name`. It fails on a **different axis** — the
normal-tissue / immune window (NK cells), with a discontinued CD56 ADC precedent. Collapsing two
antigens into one "not selective" verdict was wrong for half the route.

### X20 · The retraction stopped one hop short, again

`hla-coverage.json` — RT-VACCINE's and RT-TCR-IMMTAC's only artifact — is computed from the retracted
`fusion-breakpoint-neoantigens.json` (`hla_coverage.py:57`) and carried **no banner**, though the
producer did and the roadmap had already written *"`hla-coverage` … inherits the defect without ever
printing a seam."* Bannered. Same shape as X14: a retraction that reaches the producer and not the
consumer.

### X21 · ⚠ OPEN for trimcrae — `ready` is being used for two different things

CONVENTIONS §4.1: `ready` = *"nothing blocks it; not yet started"*; `blocked` = *"at least one open
`BLK-*`"*. Measured across all 40:

| `ready` route | open blockers |
|---|---|
| RT-METHODS-PAPER | none ✔ |
| RT-PANNR4A-EXVIVO | none ✔ |
| RT-ATR-ASSESS | BLK-CLASS-INHERITANCE, BLK-NO-EMC-DATA |
| RT-ASYMMETRIC | BLK-PARALOGUE-DDG, BLK-UNSIZED-REQUIREMENT |
| RT-TRABECTEDIN | BLK-NO-EMC-DATA |
| RT-CARFILZOMIB | BLK-NO-EMC-DATA |

**4 of 6 contradict the vocabulary literally.** Two readings are in play and the register does not
distinguish them: *"ready as a paragraph of a paper"* (true of all four) and *"ready as a thing to
do"* (false — each holds an open blocker). On RT-ICI-TKI that ambiguity was actively dangerous — the
view printed `state: ready` one line under *"TOP NEAR-TERM LEAD"* on a nivolumab+sunitinib route, so
it read as ready-as-a-treatment. That one is fixed (`→ delegated`).

⚠ **Not fixed for the other four, deliberately.** Either the vocabulary gains a value for
"deliverable is finishable, route is not", or four statuses change — and both are decisions about
what the board is *for*, not defects to patch. Flagged rather than swept: a status a reader can
misread as clinical readiness is exactly what this audit exists to surface.

## ST-REPURPOSING — 7 routes, all 7 audited

6 DEFECTIVE, 1 SOUND-WITH-NITS (RT-RXR). This family settled X9.

### X9 · ✅ SETTLED — the fusion RETAINS the AF-1, and the repo knew a day before the closure was written

The crux was whether "NR4A3 exon 3" is compatible with "NR4A3(1–626)". **It is — measured, $0:**

| exon | coding nt | first residue |
|---|---:|---|
| 1 | **0** | — |
| 2 | **0** | — |
| 3 | 951 | **1** |

`utr5_len: 699`; `first_transcript_exon_is_coding: false`; all four self-checks true. **NR4A3
transcript exons 1–2 are entirely non-coding, so "exon 3" IS residue 1.** The exon-level and
residue-level definitions of `OBJ-FUS-T1` were never in conflict. `EWSR1(1–264)::NR4A3(1–626)`
retains AF-1, DBD, hinge and LBD — and does so in **all 9 DBD-retaining breakpoint windows**.
EWSR1-LC is **additive**.

⛔ **The repo had already resolved this on 2026-08-02 — the day BEFORE the closure was written — and
recorded it in the very artifact the closure cites.** `target-route-census.json` →
`fusion_model_disagreement.resolution`: *"NR4A3 exon 3 begins at residue 1 … the chimera retains the
AF1, the DBD, the hinge and the LBD."* The closure cited **check B** of that table (lysine/cysteine
*counts*) instead of **check C** two rows below, which resolved the junction the other way.

**What was done, and what deliberately was not.** `RT-6MP` moves `definitional` → `premise_false`
with a minted, watched revival trigger. It is **still closed** — reopening is a scientific call, not
an audit action — but the ground has changed, and the new ground is *stronger* than the old one:

⭐ **Direction of effect, which the record never stated.** 6-MP **enhances** NR4A3 activity
(`published-warhead-registry.json`), and the fusion is a transcriptionally active **gain-of-function**
oncoprotein. So 6-MP is a candidate **agonist of the oncoprotein** — a better argument for closing
the route than the one on file. It rests on a prior, not a demonstration (no direct
loss-of-function experiment in any EMC cell line exists), which is exactly why it is `premise_false`
and not `definitional`. *"cannot act on the chimera at any dose"* is deleted everywhere.

⚠ **The genuinely open question the correction creates, now in `remaining_unknowns`:** in the chimera
the AF-1 is **internal** — preceded by EWSR1(1–264) and neighboured by a strong independent
activation domain. Whether an internalised AF-1 stays SRC-2-competent and 6-MP-responsive is
untested.

⛔ **And the taxonomy was teaching the refuted case as canonical.** `integrity.json`'s definition of
`definitional` used *"a ligand whose mechanism lives in a domain the disease deletes"* as its worked
example — i.e. RT-6MP. Replaced; the paralogue-shared-residue example beside it holds.

### X22 · ⛔ A false clinical claim in a generated candidate ranking

`build-candidates.mjs` (and therefore `candidates.json`) asserted *"Venetoclax sensitivity was
identified and **validated** … **across two** patient-derived EMC ex vivo models"*, carrying
`evidenceTier: T1-preclinical-or-analog`, `rank: 8`. The primary text says the opposite — I read it
from the literature cache: *"**no response to venetoclax as a monotherapy** in the validation."* What
is supported is **combination-only** activity. Corrected in the generator (editing the JSON alone
would be overwritten) and regenerated.

### X23 · Two routes filed as blocked on things that were already free or already done

- **RT-CARFILZOMIB** carried **five** fields demanding a primary citation — `remaining_unknowns`,
  `required_validation`, `readiness.missing`, `why_not_higher`, `best_next_action` — for a lookup
  **completed on 2026-08-05** (`integrity.json` OC-4 resolved; PMID 36316541). The route's own
  `last_verified` is that same date. It was directing the next session to redo finished work.
  ✅ The repoint to `EV-BANGERTER-2023` was verified correct against the primary text, and
  `strength: direct` **survives for carfilzomib** — high sensitivity was validated in *both* models.
  The scope caveat that was missing is now carried: the 40-drug discovery panel ran on USZ20-EMC1
  **alone**, and venetoclax enters only through combination additivity.
- **RT-PPARG-DOWNSTREAM** was filed behind a **2029** expression-data forecast, when its own grade
  owner says *"it is a literature question, not a compute question. **$0 test** … in CI."* Added as
  `feasible_today: true`; `wait` → `pursue_now`.

### X24 · The same artifact, permanent on one route and revivable on another

`RT-HDAC-BET` was `definitional` on `depmap-sarcoma-dependency.json` (BET/CDK pan-essential, no
selectivity window) — a **sarcoma-wide transfer prior, not EMC data**. `RT-SYNLETH-DEP` rests on the
**same artifact and the same sentence** and is `premise_false` with two triggers. One artifact cannot
be a permanent definitional fact on one route and a revivable measured premise on another. Re-filed.

Its grade also claimed *"not an EMC result"* — false: the repo holds a **fact-checked** EMC ex-vivo
result for the class (Iwata 2025, 221-drug screen in a patient-derived EMC line, hits including
panobinostat and romidepsin). Re-scoped to *"not a fusion-SELECTIVITY result"*, with the
non-selective-activity question named as explicitly **not** closed.

### RT-TRABECTEDIN — a monotherapy route citing a combination case

`strength: direct` for *"a reported EMC response"*. The registry records **disease control**: n=5,
**secondary** provenance, median PFS ~12.5 months, *"mostly stable disease"*, **no ORR field**, and
its own intro says cytotoxic chemotherapy *"mainly stabilises disease"*. The single "impressive
response" in the literature is a **radiotherapy + trabectedin** case — cited by a route whose alias
is `trabectedin monotherapy`. Same shape as the Bangerter over-read: a combination result read as a
monotherapy result. → `transferred`, confidence `low`, RT confound stated.

### ⭐ RT-RXR — SOUND, and its auditor did the $0 check nobody had

`TECH-RXR-HETERODIMER-REPORT` asserted *"The published negative stands unchanged"* — an assertion
with **no reading behind it**, while a 2025 primary paper on that exact question sat unreferenced in
`lit-targets-emc-post-degrader.json`. Read: Yu et al., now eLife 106861 — it studies **Nurr1–RXRα and
Nur77–RXRγ only**, i.e. the two paralogues that *do* heterodimerise. **The negative stands, and it is
now a reading rather than an assumption.** The closure's `premise_false` filing is correct and was
not touched.

## ST-RADIOLIGAND — 2 routes · ST-DISSEMINATION — 1 route

### X25 · ⛔ A fabricated figure — and my own prompt was carrying it

`emc-treatment-strategy.md:297` asserted *"B7-H3/CD276 **and FAP** are not class-selective, **BH q = 1.0**."*
**FAP's measured value is `selectivity_q = 0.1555`** (`emc-surfaceome-scan.json`; enrichment 0.02,
`selectivity_significant: false`). The source it paraphrases reads *"not for B7-H3/CD276 (BH q = 1.0),
EGFR or FAP"* — **the parenthetical is scoped to CD276 and was distributed across three genes in
transit.** That is a fabricated statistic under the golden rule, and it sat in a file CLAUDE.md §5
names as required reading.

⭐ **The instructive part: the error had already escaped into tooling, and into this audit.**
`lint_claims.py`'s own header recorded *"the repo's own computed selectivity screen recording BH q = 1.0
for **both**"* — so the linter's documentation carried the same transcription error it was written to
catch. **I inherited it from there into the audit prompt**, told the subagent q = 1.0 held for FAP, and
the subagent opened the artifact and corrected me. Both sites fixed. **A linter's documentation is read
as fact.**

⚠ And the inference does not transfer to FAP at all: the screen is DepMap tumour-cell **monoculture
with no CAF compartment**, so it cannot see the stroma a FAP route targets. Applying a stroma-blind
instrument to a stromal target and concluding the target is unselective is an absent reading treated as
a reading of absence.

### Other ST-RADIOLIGAND fixes

- **RT-FAP-RLT** carried `BLK-NOT-FUSION-SELECTIVE`, whose registered meaning is *"engages the wild-type
  protein (NR4A3 LBD, or EWSR1's low-complexity half)"* — **a FAP ligand engages neither.** Its sibling
  RT-SSTR2, structurally identical, filed the same blocker as *retired*. Both cannot be right; moved to
  retired to match. `BLK-NO-WET-LAB` was missing on a route whose validation is a clinical readout.
- **RT-SSTR2** presented `confidence: unknown` as though nothing were known, when its normal-tissue
  window is already computed as `ENHANCED_BROAD`. Crossfire does not make a broadly-expressed normal
  antigen safer — it widens the irradiated field. Now stated.

### ⭐ RT-METHODS-PAPER — the 40th route, and the only one with genuinely zero blockers

Verified rather than assumed: computing the union of `blockers_inherited` + every
`required_validation[].blocked_by` across all 40 routes, **this is the only route whose union is
empty.** The zero is a real property, not an omission.

Its citation of V5/V7/V21 — three instruments whose controls **failed** — at `strength: direct` is
**legitimate**, and legibly so: each `what_it_supports` states the *failure* as its proposition. Do not
"fix" these.

Two things did stop it being writable as-is, both now fixed:
- **The instrument list contradicted its own thesis.** A paper claiming a *complete* record listed 9 of
  22 instruments on no stated rule, and **omitted the passes** — including `V1`, whose known-answer
  pass beside its "not yet" on our own system is exactly the honest half. `support` now carries
  V1/V6/V8/V10; `disclosed_failing` 9 → 16.
- **"Nothing blocks it. Write it."** appeared in three places unqualified, while the binding roadmap
  reserves the *framing* choice (P1 vs P6) to trimcrae. The record's own `why_not_higher` already had
  the qualifier — *"no **scientific** blocker"* — and the other three had dropped it.

One real $0 prerequisite is now recorded where it printed "—": the MM-GBSA decoy null's primary run
output lives in S3, not in a committed JSON, and it is the **headline evidence of the recommended
framing**.

## ST-DEPENDENCY — 3 routes

### X26 · ⛔ An instrument cited for a scan it never ran

`RT-SYNLETH-DEP`'s only `supporting_evidence` cited `INS-DEPMAP-KO` — *"DepMap CRISPR-knockout
dependency scan of **the ATR axis**"*. Its module's gene panel is ATR/ATM/DDR/CONTEXT and contains
**no BRD9, no BICRA, no ncBAF gene at all** (verified: 1 incidental hit in the whole file). The
route's BRD9 result lives in a different artifact entirely. **Two scans, two panels, one cited for the
other's result** — and `strength: transferred` was honest, so the label gave no warning.

⛔ **Worse, that artifact had no `ART-*` id at all** — so X24's ruling (that the same artifact is filed
`premise_false` on RT-SYNLETH-DEP and could not be `definitional` on RT-HDAC-BET) rested on a **prose
assertion about a file the graph could not name.** Registered as `ART-DEPMAP-SARCOMA-DEP`; the closure
is now checkable rather than asserted.

⭐ **And registering it corrected the bound.** The family limitation read *"one EMC model in public
dependency data … bounded by a sample size of one."* The artifact's own note says EMC **has no DepMap
line**, and the prior was computed over **91 sarcoma lines, none of them EMC**. The honest bound is not
n = 1 — it is **no EMC observation at all**, which is stronger. The "one EMC model" phrasing is also the exact description `OBJ-LINE-HEMCSS.may_not_ground` forbids:
that model is **ACH-001519 / H-EMC-SS**, whose **identity is disputed** on the curated record (Cellosaurus
CVCL_1238, *"does not harbor a gene fusion involving EWSR1"*) — so it is named here only to record that it
grounds nothing.

### X27 · ⚠ OPEN for trimcrae — the two wet-lab asks spend the same relationship

`RT-ATR-PANEL` and `RT-ASO-ASK` both address **the same two groups** (USZ Zurich, NCC Japan), both
`pursue_now`, both `$0`. `BLK-NO-WET-LAB` is `requires_external_collaboration` — **the scarce input is
a relationship, not money** — and the repo says so outright: *"the cell-line repositories exclude
individuals by published policy rather than by price."* **Two $0 asks to one relationship are not
independent: a declined first ask prices the second.** `$0 · $0` is arithmetic over the wrong resource.

Eleven routes sit behind `TR-EMC-MODEL-ACCESS`, and ready-to-send outreach exists for a third set.
**No ordering existed anywhere.** Now recorded on both routes; the ordering itself is an
outward-facing call and is trimcrae's.

Also: `RT-ATR-ASSESS` had not absorbed **its own graded result** — tier **WEAK**, all three positive
predicates false, 1 of 4 mechanism tests passing, and the ATM-signalling predictor at ρ = −0.090, the
**wrong sign** — while carrying `confidence: moderate` and a `Tier 1 DELIVERABLE` grade. And
`RT-ATR-PANEL` claimed *"a costed design"* when no cost exists anywhere in its prereg.

## The audit in one table

| family | routes | SOUND | DEFECTIVE |
|---|---:|---:|---:|
| ST-PROXIMITY | 7 | 0 | 7 |
| ST-OCCUPANCY | 3 | 0 | 3 |
| ST-FUSION-DIRECT | 3 | 1 | 2 |
| ST-NUCLEIC-ACID | 5 | 0 | 5 |
| ST-IMMUNO | 9 | 1 | 8 |
| ST-REPURPOSING | 7 | 1 | 6 |
| ST-DEPENDENCY | 3 | 0 | 3 |
| ST-RADIOLIGAND | 2 | 1 | 1 |
| ST-DISSEMINATION | 1 | 1 | 0 |
| **total** | **40** | **5** | **35** |

`systems_check --check`: **0 ERROR before, 0 ERROR after.** None of the 35 was a schema defect.

### What the checker gained

Three rules now fail the build on shapes this audit had to find by hand — `[V4]`
(`supporting_evidence[].ref` must resolve), `[T7]` (a `revisit_trigger` must be able to move the
route), and `closure_note`/`rationale` added to `SHARED_ROUTE_FIELDS` so a closure argument cannot
diverge silently between the graph and its mirror. Plus `distinct_from` is rendered for the first
time, and `R2-proteome-wide` now catches *"absent from normal proteome"*.

### What is left open for trimcrae, deliberately

1. **RT-6MP** — reopen, or keep it closed on direction-of-effect? The premise it was closed on is
   refuted; the new ground is stronger but rests on a prior. (X9)
2. **RT-FET-LC-LIGAND** — drop *"worse"* from the grade and keep `definitional` honest, or keep it and
   re-file as non-permanent? (X11)
3. **`ready`** — one vocabulary value doing two jobs on 4 routes. (X21)
4. **The outreach ordering** — which ask spends the one relationship first. (X27)
5. **The ASO regeneration** — needs Ensembl, so it must run in CI, and nothing may be quoted from that
   panel until it does. (X14)

## What nearly went wrong in the audit itself

Recorded because the next audit will hit the same traps.

1. **I nearly filed 25 false defects.** Reading `fails_on` with its `sub_forms` meaning made 25
   `distinct_from` entries look like contradictions of the named route's own blockers. Under the
   correct definition, zero are. **A field name reused across two fields is a trap for exactly the
   kind of mechanical sweep an audit runs.**
2. **A `distinct_from` completeness matrix is not a finding.** The schema says *"objects this one is
   routinely confused with"* — not exhaustive. Most routes are undistinguished from most siblings by
   design.
3. **A third module looked like it carried the same off-by-two, and does not.** `patient_neoepitopes.py`
   has the identical `offsets[n_exon - 2]` pattern — but its CLI declares those flags as **coding**-exon
   ranks, for which the arithmetic is right. What IS wrong is narrower and easy to miss: its own worked
   example passes `--nr4a3-exon 3`, the repo's *transcript*-exon name for the canonical fusion, into a
   coding-exon parameter. **A correct function with a wrong worked example fails no test and lints
   clean.** Documented in place rather than "fixed".
4. **My first `revisit_trigger` sweep used a field that does not exist** (`technologies.retires`; the
   real one is `unblocks.blockers`) and reported 29 false positives before I checked. Re-run
   correctly, it found 4 real ones.
5. **A "required" field can be satisfied by an empty array.** The closed routes carry
   `revisit_trigger: []` — schema-valid and honest. Truthiness and presence are different questions.

The common shape: **every one was a mechanical result that looked like a finding until it was checked
against the definition.** The rule that caught all four is CLAUDE.md §4 — get the evidence before
writing the sentence.
