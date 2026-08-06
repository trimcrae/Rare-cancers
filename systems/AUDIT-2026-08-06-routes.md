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

## What nearly went wrong in the audit itself

Recorded because the next audit will hit the same traps.

1. **I nearly filed 25 false defects.** Reading `fails_on` with its `sub_forms` meaning made 25
   `distinct_from` entries look like contradictions of the named route's own blockers. Under the
   correct definition, zero are. **A field name reused across two fields is a trap for exactly the
   kind of mechanical sweep an audit runs.**
2. **A `distinct_from` completeness matrix is not a finding.** The schema says *"objects this one is
   routinely confused with"* — not exhaustive. Most routes are undistinguished from most siblings by
   design.
3. **My first `revisit_trigger` sweep used a field that does not exist** (`technologies.retires`; the
   real one is `unblocks.blockers`) and reported 29 false positives before I checked. Re-run
   correctly, it found 4 real ones.
4. **A "required" field can be satisfied by an empty array.** The closed routes carry
   `revisit_trigger: []` — schema-valid and honest. Truthiness and presence are different questions.

The common shape: **every one was a mechanical result that looked like a finding until it was checked
against the definition.** The rule that caught all four is CLAUDE.md §4 — get the evidence before
writing the sentence.
