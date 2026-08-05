---
id: DOC-CONVENTIONS
title: Conventions — identifiers, states, vocabularies and invariants
level: L0
kind: convention
status: live
canonical_for: [ID namespace, status vocabulary, work-state glyphs, structural invariants, document naming]
purpose: >
  Define every identifier namespace, every controlled vocabulary and every structural invariant used
  across the repository, so that a name always resolves to exactly one thing.
scope: Repository-wide. Binding on prose, JSON, code and generated views alike.
audience: [maintainers, autonomous research agents]
supersedes:
  - research/manuscripts/nr4a3-program-map.md §0 (reading rules, glyphs, ID scheme, invariants)
date: 2026-08-05
last_verified: 2026-08-05
related: [DOC-ARCHITECTURE, DOC-MIGRATION]
---

# Conventions

> **Role:** the one home of every identifier namespace, controlled vocabulary and structural invariant.
> A name that does not resolve here is not a name this repository recognises.

---

## 1 · The identifier namespace

One prefix, one meaning, repository-wide. **No bare number-only identifier is valid** — every id carries its
prefix, always, including inside tables and figure captions where it is tempting to abbreviate.

| prefix | object | level | example |
|---|---|---|---|
| `ST-` | strategy family | L1 | `ST-PROXIMITY` |
| `RT-` | route / therapeutic approach | L2 | `RT-DEGRADER` |
| `PUB-` | publication | L3 | `PUB-DEGRADER-PAPER` |
| `EXP-` | experiment / compute lane | L4 | `EXP-STEP1-FANOUT` |
| `V` | instrument (a method with a known-answer control) | L4 | `V3` |
| `R` | **requirement** — what must be TRUE | cross-cutting | `R7` |
| `C` | **configuration** — a frozen choice a number is conditional on | L5 | `C14` |
| `EV-` | evidence (a citable source) | L5 | `EV-ZAIENNE-2022` |
| `OBJ-` | biological object | L5 | `OBJ-FUS-T1` |
| `ART-` | artifact (a produced file) | L5 | `ART-IDR-CENSUS` |
| `CLM-` | claim (a quoted figure with one home) | L5 | `CLM-IDR-EMC` |
| `BLK-` | blocker | cross-cutting | `BLK-PARALOGUE-DDG` |
| `TECH-` | technology dependency | cross-cutting | `TECH-FE-CRYPTIC-POCKET` |
| `FC-` | forecast | cross-cutting | `FC-FE-CRYPTIC-POCKET` |
| `MS-` | roadmap milestone | cross-cutting | `MS-2027-TERNARY` |
| `TRG-` | literature scan trigger | cross-cutting | `TRG-FEP-CRYPTIC-POCKET` |
| `OC-` / `RC-` | open / resolved conflict | cross-cutting | `OC-2` |
| `DOC-` | registered document | — | `DOC-ARCHITECTURE` |

### 1.1 · ⚠ Two collisions this repository already had — and how they are resolved

Both were documented as live hazards before this architecture existed. Documenting a collision does not fix
it; renaming does. Both renames are mechanical and both old spellings stay searchable via `aliases`.

**`R` meant five different things.** It now means exactly one.

| was written | now written | what it is |
|---|---|---|
| `R1`…`R16` | **`R1`…`R16`** *(unchanged)* | a requirement — what must be TRUE |
| "validation requirement 1–5" | **`VR1`…`VR5`** | the external reviewer's five conditions on what a result may claim |
| "lint rule R1–R5" | **`LR1`…`LR5`** | the manuscript language-discipline rule families |
| "Arm R1 / Arm R2" | **`ARM-1` / `ARM-2`** | the two arms of the NR-V04 retrospective panel |
| `R` (a number) | **`R_closure`** | the cycle-closure statistic |

**`C` meant three different things, and two of them collided outright.** The configuration register runs to
`C24` and the instrument-options register ran to `C16`, so `C10`–`C16` existed in both schemes spelled
identically, with no padding or context to tell them apart. Zero-padding was tried as the tell and it failed
at ten — which is exactly the kind of near-miss convention that reads as working until it silently doesn't.

| was written | now written | what it is |
|---|---|---|
| `C1`…`C24` | **`C1`…`C24`** *(unchanged)* | a configuration item — a frozen choice |
| `C01`…`C16` (zero-padded) | **`IC-1`…`IC-16`** | an instrument-options candidate |
| `C397`, `C420`, `C551` … | **`Cys397`, `Cys420`, `Cys551`** | a cysteine residue |

⛔ **A residue is written `Cys<number>`, never `C<number>`.** The old spelling collides with the
configuration register on every residue below `C25`, and residue numbers are quoted constantly in the
covalent work.

---

## 2 · Work state — the five glyphs

**A state is WORK STATUS, not evidence quality.** A claim can rest on excellent evidence and still be
blocked; a dead end can be very well established. These answer *"what should I do about this?"* and every
object carries exactly one.

| state | glyph | means | what to do |
|---|---|---|---|
| complete | `✓` | ran, returned, result recorded in a committed artifact | cite it; do not re-run it |
| in work | `◐` | dispatched or building right now | wait; do not start a second copy |
| future work | `○` | not started; nothing blocks it except sequence | this is where new effort goes |
| parked | `⏸` | failed with today's tools; a better tool could change the answer | name the `TECH-*` that reopens it |
| dead end | `✕` | conclusively proven unworkable | never retry |

⛔ **`✕` means conclusively proven unworkable, not "we tried and it didn't work."** The test is one question:
*is there any future development that would make us retry this?* If yes, it is `⏸`, not `✕`. A `✕` requires
positive evidence of impossibility — a structural confound no sample size fixes, arithmetic that cannot reach
the criterion, a premise shown false, or an artifact that can never be regenerated. Conflating the two is
expensive in both directions: it buries live options and it invites re-running things that cannot work.

⛔ **`◐` is the most expensive glyph to get wrong.** It instructs every reader *"do not start a second copy"*,
so a `◐` on something nobody has started is an instruction not to do the work. It has been wrong seven times
here. **A `◐` must name the running job**, and whether anything is actually running is a free observation any
reader can take before believing one.

⚠ **`✓` never means the claim is true** — it means the work item finished. An instrument whose known-answer
test completed cleanly and returned a clear negative is `✓` on work and `⏸` on the avenue.

---

## 3 · Three orthogonal axes

One glyph cannot answer four questions. Every time it was made to, it produced a wrong instruction — always
the same shape: an item that was **not authorised** got recorded as **low value**, because the only column
available to record "not now" was the one that grades importance.

| axis | question | values | owned by |
|---|---|---|---|
| **work state** | what should I do about this? | `✓ ◐ ○ ⏸ ✕` | the committed artifact |
| **authorization** | am I allowed to spend on it? | `—` free · `🔒` needs a decision | the person holding the budget |
| **sufficiency** | would it finish the job? | the claim ceiling | the instrument underneath it |

All three can be true at once. A route may be the highest-leverage item on the board (`sufficiency`), not
started (`work state`), and unauthorised (`authorization`) — and it must still read as high-leverage.

---

## 4 · Controlled vocabularies

Closed enums. The checker rejects any value outside them. Before this, roughly nineteen distinct status
strings were in use across the corpus, three of them in a single file.

### 4.1 · `status` — a route, strategy or publication

| value | means |
|---|---|
| `active` | being worked on now |
| `ready` | nothing blocks it; not yet started |
| `blocked` | at least one open `BLK-*` |
| `parked` | failed with today's tools; has a named `TECH-*` to reopen it |
| `closed` | conclusively unworkable; carries no `TECH-*` |
| `delegated` | someone else's to answer |
| `superseded` | replaced by another object, which is named |

### 4.2 · `maturity` — how far an approach has actually got

| value | means |
|---|---|
| `concept` | an idea with a rationale and no computation |
| `scoped` | question stated, protocol designed, cost known |
| `computed` | the in-silico work has run and returned |
| `validated_in_silico` | the instrument that produced it has passed a known-answer control |
| `externally_corroborated` | an independent method or published measurement agrees |
| `experimentally_testable` | a concrete bench experiment is specified and costed |

⚠ `computed` and `validated_in_silico` are deliberately separate. A result exists as soon as a pipeline
returns; it may support a claim only once the instrument underneath it has recovered a known answer. Most of
this program sits at `computed`, and saying so plainly is the point.

### 4.3 · `confidence` — in the object's own central assertion

`high` · `moderate` · `low` · `unknown`. **`unknown` is a legitimate value and is not a placeholder** — it
means nobody has assessed it, which is different from having assessed it as low.

### 4.4 · `readiness.attainable_today`

`internal_note` → `reproducible_workflow` → `preprint` → `chemrxiv` → `journal_submission` →
`experimental_proposal`. Ordered, but **not a ladder** — `experimental_proposal` is not "better than"
`journal_submission`; they are different outputs, and a route can be ready for one and not the other.

### 4.5 · `timing.recommendation`

`pursue_now` · `wait` · `monitor` · `closed`. Anything other than `pursue_now` requires a `revisit_trigger`
naming a `TECH-*`, so that "later" is a monitored condition rather than a feeling.

### 4.6 · Document `status`

`live` · `generated` · `historical` · `superseded` · `immutable`.

⛔ **`immutable` is reserved for preregistrations.** A preregistration's entire value is that it was written
before the result. It is never rewritten, never consolidated and never tidied; amendments are appended as
dated blocks. The checker fails on any edit to the body of an `immutable` document.

---

## 5 · Structural invariants

Each is enforced by [`systems_check.py`](systems_check.py) and each exists because it was violated.

1. **One fact, one home.** Every number, status and grade has exactly one owning file; everything else that
   shows it is generated or points at it. A total is derived, never typed.
2. **A claim can never be stronger than the instrument underneath it.** An instrument that has not recovered
   a known answer cannot support a claim, however good its output looks. An instrument whose control failed,
   and one that has no control at all, are different facts — and neither is support.
3. **A generated view may not be hand-edited.** The checker re-renders every view and fails on any
   difference.
4. **Every pointer resolves.** A reference to a file, section anchor or artifact field that does not exist
   fails the build.
5. **A correction goes in an appendix; the live text carries only the current value.** Never silently drop a
   superseded number — but never leave the "was X, then Y, both wrong, now Z" narrative in the live text
   either, because the old values stay quotable.
6. **A blocker carries exactly one kind, and a non-permanent blocker names at least one technology that
   would retire it.** Otherwise the register cannot say what to watch for.
7. **A forecast declares its basis.** `evidence_based`, `extrapolated` or `speculative` — required, because
   an unlabelled forecast is indistinguishable from a measurement.
8. **A guard fails red.** A check that cannot run must exit non-zero. A guard that fails open leaves no
   trace, and a silent guard is worse than no guard because it is trusted.

---

## 6 · Document conventions

**Frontmatter is required on every Markdown file.** Filesystem dates carry no information in this repository
— the history is a squashed import and every file reports the same date — so freshness is declared, not
computed.

```yaml
---
id: DOC-<SLUG>
title: <one line>
level: L0|L1|L2|L3|L4|L5|—
kind: architecture|convention|policy|manuscript|prereg|memo|register|runbook|generated|historical
status: live|generated|historical|superseded|immutable
canonical_for: [<concepts this file owns; empty if it owns none>]
purpose: <what question this document answers>
scope: <what it covers, and what it deliberately does not>
audience: [<who reads it>]
supersedes: [<paths or DOC- ids>]
superseded_by: <path or DOC- id, if any>
date: <authored>
last_verified: <when someone last checked it is still true>
related: [<DOC- ids>]
---
```

`canonical_for` is the load-bearing field: it is how a reader finds the owner of a fact, and how the checker
detects two documents claiming the same concept.

### 6.1 · File naming

- Generated views: `systems/views/**` — always carry `status: generated` and a do-not-edit banner.
- Durable references: descriptive, undated names (`pricing.md`, `gcp-gpu-facts.md`).
- Preregistrations: `*-prereg.md`, `status: immutable`.
- ⛔ **A date in a filename means the document is a one-off record of a moment**, and a one-off belongs in
  `archive/` once its findings have been folded into a durable home. Roughly twenty-six such files existed
  with a date in the name, and about eighteen more without one — so the date is a *hint*, and `kind` +
  `status` in the frontmatter are what actually decide.

### 6.2 · Terminology

| use | not |
|---|---|
| route | approach, avenue, path, strategy *(when a specific `RT-*` is meant)* |
| strategy family | track, area, theme, category |
| instrument | method, tool, pipeline *(when a specific `V*` is meant)* |
| blocker | gate, obstacle, barrier, limitation |
| technology dependency | unlock, trigger, capability *(when a specific `TECH-*` is meant)* |
| known-answer control | positive control, benchmark, sanity check |
| claim ceiling | caveat, limitation, disclaimer |

Ordinary English is fine in prose. The rule binds where an identifier is being referenced: name the object,
then gloss it, rather than using a synonym that the reader has to resolve.

---

## 7 · Language discipline

Claim-language rules (`LR1`–`LR5`) are enforced by `lint_claims.py` over the manuscripts and the model's
generated views. They are stated in full in [`POLICY-language.md`](POLICY-language.md). In summary: never
imply proteome-wide selectivity, EMC efficacy, safety, a therapeutic window or clinical readiness; no
computational result *proves*, *confirms* or *establishes* anything; a projected number is never described as
*measured*; and novelty is right-sized — incremental, not landmark.

These are not stylistic. Selectivity results in this program have had to be withdrawn, and the linter exists
because prose discipline is exactly what failed here.
