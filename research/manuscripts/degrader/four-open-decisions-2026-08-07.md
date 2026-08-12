---
id: DOC-FOUR-OPEN-DECISIONS-2026-08-07
title: Four open decisions — the C14 criterion, Arm F, the two-branch template, and the term-(a) envelope
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: >
  Make four standing roadmap decisions DECIDABLE by trimcrae — assemble the evidence, state the real
  options with their consequences and costs, recommend one, and stop. It takes none of the four.
scope: >
  §10.1 rows 7, 8, 10 and 28 of the roadmap. It amends nothing, decides nothing, and edits no register;
  every proposed change is routed as JSON.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-07
last_verified: 2026-08-07
---
# Four open decisions — a decision dossier

**$0 throughout.** Free CPU in the dev sandbox + committed artifacts + one unauthenticated public GitHub
API read. No GPU, no rental, no dispatch that bills. Nothing in flight.

⛔ **THIS DOCUMENT TAKES NONE OF THESE DECISIONS.** Each is trimcrae's alone under CLAUDE.md §2 and §3.
Every section states what must be decided, the evidence with each number cited to the committed artifact
that owns it, the real options with their consequences and costs, a recommendation with its reasoning,
what happens if nothing is decided, and the check that would falsify the choice. **Nothing here is
implemented.** Machine-readable edits are routed in
[`four-open-decisions-map-edits.json`](four-open-decisions-map-edits.json); the roadmap, `systems/graph/*`,
`systems/views/*` and `path-family-synthesis.md` are untouched.

⛔ **No number below is typed from memory or from a summary.** Every figure names the artifact and the key
it was read from. Where this document derives a value, the derivation is arithmetic on cited artifact
fields and says so.

| § | row | decision | recommendation |
|---|---|---|---|
| [1](#decision-1--the-c14-criterion-choice) | 10 | which crystallographic copy `C14` scores against | **do not move `C14`; rewrite SI §S1 (3)** |
| [2](#decision-2--row-7-classify-arm-f) | 7 | classify Arm F — held, or explicitly retired | **retire explicitly, and schedule the trigger** |
| [3](#decision-3--row-8-the-two-branch-template-design-decision) | 8 | promote the two-branch template, or leave it an exploration | **decline promotion; keep it as a registered exploration** |
| [4](#decision-4--row-28-the-term-a-feasibility-envelope) | 28 | rule on `term_a_feasibility_envelope` | **regenerate at a converged `n_mc` — and the row's premise is wrong** |

---

## DECISION 1 — the `C14` criterion choice

### (a) What must be decided, in one sentence

**Whether the frozen pose-recovery criterion `C14` is amended to name which crystallographic copy of a
cognate ligand a re-docked pose is scored against — or is left alone and the four SI §S1 anti-target
clauses it currently renders unreadable are withdrawn or rewritten instead.**

### (b) The evidence

**The gate, in the rung's own words.**
[`antitarget-selfcontrol.json`](../../modalities/antitarget-selfcontrol.json) → `_gate`: *"The cognate-ligand
self-control runs FIRST. Until it passes, no anti-target margin from this panel may be read, including the
one already published in SI §S1."*

**The criterion.** `→ criterion`: `recovered_rmsd_A` **2.0**, `partial_rmsd_A` **4.0**, secondary `fnat`
**0.5**, `n_null` **200**, `null_power_max` **0.05**. `_read_from`: `apo_pose_recovery` — i.e. `C14` was
**not chosen by this rung**; it is the same line that grades `V3` and `V22`
([roadmap §3b.1 row `C14`](../nr4a3-program-map.md#3b1--the-register)).

**What ran.** `R14-a` (2026-08-03, $0 CI) and then `R14-a2`, the receptor-**preparation** repair
(roadmap §10.1 row 10: GH run `30809217139`, job `r14a`, **7:21–7:46 AM ET**, $0 CPU). Both arms are
committed in the same artifact.

**The result, both arms.** `→ selfcontrol`: `n_targets` **10**, `n_pass` **7**, `panel_readable`
**false**, blocking **CYP3A4, PPARG, PXR**. `→ arms.stripped` — the build that produced SI §S1's published
margins — reads the same: 7 of 10, `panel_readable: false`, same three.

**Per target, `→ repair_delta` (stripped → repaired RMSD, Å):**

| target | stripped | repaired | verdict | cofactor kept | receptor changed | centroid shift | RMSD to *nearest* deposited copy | `a_different_copy_would_pass` |
|---|---|---|---|---|---|---|---|---|
| AR | 0.443 | 0.443 | PASS | — | false | 0.229 | 0.443 | false |
| **CYP3A4** | **8.653** | **12.337** | **FAIL** | **HEM** | **true** | **8.148** | **1.108** | **true** |
| ESR1 | 1.186 | 1.36 | PASS | — | false | 0.321 | 1.36 | false |
| GR | 0.336 | 0.335 | PASS | — | false | 0.227 | 0.335 | false |
| HSA | 0.769 | 0.759 | PASS | — | false | 0.626 | 0.759 | false |
| MR | 0.809 | 0.811 | PASS | — | false | 0.348 | 0.811 | false |
| **PPARG** | **6.962** | **6.894** | **FAIL** | — | false | 4.522 | **6.894** | **false** |
| **PXR** | **6.76** | **6.804** | **FAIL** | — | false | 0.934 | **6.804** | **false** |
| RXRA | 0.663 | 0.638 | PASS | — | false | 0.437 | 0.638 | false |
| VDR | 1.033 | 1.008 | PASS | — | false | 0.508 | 1.008 | false |

**The repair was uniform and it is not tuning** — `→ repair_rule.uniform`: *"one predicate, evaluated
identically for all ten targets — it is not a list of exceptions"*; `→ repair_rule.why_it_is_not_tuning`:
*"it makes the RECEPTOR more complete, not the CRITERION more forgiving, and it is applied to passing
targets too"*. It changed exactly one receptor (`repair_changed_the_receptor` true for CYP3A4 alone) and
**CYP3A4's miss got larger, 8.653 → 12.337 Å**.

**The diagnosis the repair produced.** `→ selfcontrol.targets[CYP3A4]`: `n_cognate_copies_in_file` **8**,
`n_copies_in_chain` **2**, `copy_used` **`KLNA1501`**, `rmsd_to_best_crystal_copy_A` **1.108**,
`best_crystal_copy` **`KLNA1500`**, `a_different_copy_would_pass` **true**. The module states the
consequence itself
([`antitarget_selfcontrol.py`](../../modalities/antitarget_selfcontrol.py) → `criterion_decision_edits`):
*"The pre-registered criterion says 'the crystallographic copy', and for a multi-copy site that phrase has
no referent."* It routed the question to the board rather than acting, and that edit **landed** —
[`systems/views/plan.md`](../../../systems/views/plan.md) line 1339 carries it.

**The four clauses.** `→ selfcontrol.si_s1_statements`, all four `readable: false`, all
`blocked_by: [CYP3A4, PPARG, PXR]`:

| id | clause | why it consumes the failing receptors |
|---|---|---|
| **S1.3a** | *every survivor binds ≥1 off-target more tightly than NR4A3 (gap −0.3 to −5.7 kcal/mol)* | a MAX over the panel: one unreadable receptor can be the max, or can hide it |
| **S1.3b** | *5–8 panel targets within 2 kcal, and PXR + HSA engaged within 2 kcal in every case* | counts targets within a window, so it consumes every target; the named pair additionally |
| **S1.3c** | *`denovo_401` tops out at −9.1 (VDR), 1.7–5 kcal weaker than any repurposed survivor and not a PXR/HSA hit* | a MAX over the panel whose argmax is named, plus a negative claim about two named targets |
| **S1.3d** | *the panel DISCRIMINATES rather than merely saturates* | a claim about the instrument itself, which is exactly what the self-control measures |

⚠ **Two of the four name PXR explicitly, and PXR is one of the three that fail.** So S1.3b and S1.3c
cannot be rescued by any restatement over a readable subset — the receptor they name is the unreadable one.

**The state in print today.** [`nr4a3-degrader-paper-SI.md`](nr4a3-degrader-paper-SI.md) §S1 paragraph (3)
carries the routed conditioning banner (`si_edits_required[0].anchor_status: APPLIED`): *"⛔ **NOT CURRENTLY
READABLE (2026-08-03)** … the margins below may not be quoted until the control passes."* **The banner is in
front of the four clauses; the clauses themselves are unchanged and still read as assertions.**

**⛔ THE SECOND, INDEPENDENT BLOCK — and it survives every option below.**
`→ flagged.margin_refusal.why[1]`: *"the NR4A3 column the published margins subtract is NOT COMMITTED
ANYWHERE IN THIS REPO. `nr4a3-antitarget.json` / `nr4a3-antitarget.jsonl` — the raw (drug × target) dG
matrix `antitarget_dock.py` writes — exist only under the S3 output prefix … Recomputing an NR4A3 dG here
would need the release receptor and box that lane used, and inventing either would fabricate the
denominator of a published figure."* **Verified independently in this session, three ways:**
`git ls-files | grep -i antitarget` returns the candidate lists, the code and this artifact — and no dG
matrix; [`antitarget_dock.py`](../../modalities/antitarget_dock.py) `:29–30` writes both files to the job's
S3 `OUT`; and [`antitarget_panel.json`](../../modalities/antitarget_panel.json) carries a box for the ten
panel receptors and **none for NR4A3**. So `C14` governs whether the panel is *readable*; the missing
denominator governs whether the published *numbers* are re-derivable. **They are different locks and only
one of them is a criterion question.**

### ⭑ The arithmetic that decides this — every reachable `C14` amendment still leaves the panel unreadable

Derived from `repair_delta` by comparison alone, no new measurement:

| candidate `C14` amendment | CYP3A4 | PPARG | PXR | `n_pass` | `panel_readable` |
|---|---|---|---|---|---|
| **as frozen** (2.0 Å, the scored copy) | 12.337 ✗ | 6.894 ✗ | 6.804 ✗ | **7 / 10** | **false** |
| score against the **nearest deposited copy** | 1.108 ✓ | 6.894 ✗ | 6.804 ✗ | **8 / 10** | **false** |
| widen the band to the existing `partial` **4.0 Å** | 12.337 ✗ | 6.894 ✗ | 6.804 ✗ | **7 / 10** | **false** |
| **both** (nearest copy + 4.0 Å) | 1.108 ✓ | 6.894 ✗ | 6.804 ✗ | **8 / 10** | **false** |

**No movement of `C14` that anyone has proposed restores readability.** `a_different_copy_would_pass` is
`true` for CYP3A4 and **`false` for all nine other targets**, so the copy clause is a one-target change by
construction; PPARG and PXR miss by 2.9 Å and 2.8 Å past even the `partial` band. ⇒ **the copy question is
a real defect in the criterion's wording and is worth fixing on its own merits, but it is not a route to
readable margins, and it must not be presented as one.**

⭑ **And `C14` is shared.** Roadmap §3b.4 point 5: *"`C14` COUPLES `R5` AND `R14` … Which is also why it must
**not** be moved: `C14` was frozen before the first run and re-tuning it now would repair a failing panel by
lowering its own bar."* The same line produces `V3`'s INCONCLUSIVE (protocol-ceiling self-dock **2.849 Å**
against 2.0 — misses by **0.849 Å**) and `V22`'s **0 of 6** inside the RECOVERED band, median **6.696 Å**
(roadmap §3.1 rows `V3`, `V22`). **Any band change to rescue the anti-target panel silently moves two pose
readings as well**, and one of them would convert a documented protocol-ceiling miss into a pass.

⚠ **Two further committed observations, recorded because they are real and neither is a criterion question.**
(i) PXR's `ligand_resname_declared` is **`348`** while `cognate_comp_id` is **`SRL`** and
`ligand_resname_matched` is **false** — the panel's declared ligand id does not match what was docked.
(ii) HSA has the same mismatch (`SWF` declared, `RWF` matched, `matched: false`) **and passes at 0.759 Å**,
so the mismatch is not sufficient to cause a failure. (iii) `null.p_within_criterion` is **0.0** on all ten
targets at `n_null` 200, so `C15`'s power condition is met everywhere — no target is INCONCLUSIVE; the three
are genuine failures.

### (c) The options

Each option is graded on the one thing that matters here: **does it constitute tuning a criterion to a
result?** The test used throughout is the program's own
([`antitarget_selfcontrol.py`](../../modalities/antitarget_selfcontrol.py) `:63–64`, `:735`): *may not drop a
failing target · may not re-centre a box · may not lower a band*, plus the provenance test *"amending the
criterion after seeing which amendment passes"*.

---

**⭐ OPTION 1 — RECOMMENDED. Leave `C14` exactly as frozen. Rewrite SI §S1 paragraph (3) so the four
clauses are withdrawn as quantitative claims and the screen is reported as an unquantified negative.**

- **Tuning verdict: ✅ NOT TUNING.** Nothing is amended. The criterion adjudicates and the writing follows it.
- **What changes.** S1.3a, S1.3b, S1.3c and S1.3d stop being assertions. The paragraph keeps: the panel was
  built and run at 6k scale under an identical protocol; ten receptors, seven of which recover their own
  crystallographic ligand within 2.0 Å; and the honest statement that **no margin from it is quotable**,
  for two independent reasons — the self-control fails on three receptors, and the NR4A3 denominator is
  not committed. The existing banner stays and the clauses beneath it are rewritten to match it.
- **What it costs.** **$0** (CI + prose). The scientific cost is real and should not be softened: SI §S1 is
  currently the paper's *"6k-scale, promiscuity-controlled negative result"* and the sentence *"precisely
  why a de-novo design (§2.6) is required"* leans on it. Under this option that argument survives only in
  its qualitative form.
- **Why it is recommended.** It is the only option that is correct **whatever** the other options would
  have shown, because the ΔG-column block is untouched by all of them: even a 10-of-10 pass leaves the
  published margins non-re-derivable. Every other option spends effort to arrive here anyway, with the
  added risk of a criterion amendment on the record.
- ⚠ **Sub-choice inside it, and it is trimcrae's too:** *(1a)* condition in place (today's banner, clauses
  unchanged) — **not recommended**, because a banner in front of four unretracted assertions is read past;
  *(1b)* restate over the seven readable receptors — **not available**: S1.3b and S1.3c name PXR, and
  S1.3a's gap needs the missing NR4A3 column; *(1c)* withdraw the four numeric clauses and keep the screen
  as a described negative — **this is the one that works.**

---

**OPTION 2 — Rule the copy clause prospectively, in writing, then re-run the control unchanged.**

One sentence, fixed before it is applied: *"a pose is scored against the nearest deposited copy of the
cognate ligand within the docked chain"* — or the alternative, *"against a named copy, declared per target
at panel-construction time."*

- **Tuning verdict: ⚠ POST-HOC IN PROVENANCE, uniform in application.** The predicate is uniform and
  recomputed for all ten (and by `a_different_copy_would_pass` it moves only CYP3A4). But it is being
  considered **because we already know which target it rescues**, which is precisely what
  `criterion_decision_edits` warns of: *"the difference … is invisible until you know the answer, and by
  then it is not a pre-registration."* The mitigating fact is genuine — *"the crystallographic copy"* has
  **no referent** for an 8-copy deposit, so this repairs an under-specification rather than relaxing a bar.
- **Consequence.** 8 of 10. `panel_readable` **stays false**. The four clauses stay unreadable. It buys
  nothing for SI §S1 and it puts a criterion amendment on the record.
- **Cost.** **$0** CI.
- **Honest reading:** worth doing as bookkeeping so the criterion is well-defined for the next multi-copy
  deposit — **never as a route to readability**, and it must be written down as a definition repair with
  the explicit note that it changes no verdict.

---

**OPTION 3 — Leave `C14` alone and re-source the three failing receptors under a pre-registered structure-selection rule.**

E.g. *"prefer a deposit with exactly one copy of the cognate in the modelled site, and whose declared
`ligand_resname` matches the deposited comp id"* — applied to all ten, one shot, outcome reported whatever
it is.

- **Tuning verdict: ⚠ POST-HOC IN PROVENANCE, and this is the option with the highest reputational risk.**
  It is *not* dropping a target, *not* re-centring a box and *not* lowering a band — it is the same class as
  `R14-a2`'s preparation repair, which the program accepted as not-tuning. But re-sourcing structures after
  seeing which ones fail reads as **shopping for a panel that passes**, and the only defence is a rule fixed
  in writing first, applied to all ten, with a declared one-attempt limit.
- **Consequence.** Unknown until run; PPARG's 4.522 Å centroid shift and PXR's 0.934 Å shift at 6.8 Å RMSD
  are different failure shapes and neither is obviously a copy or a declaration problem.
- **Cost.** **$0** CI (PDB fetch + re-prep + re-dock; `R14-a` cost $0 on a free runner).
- **Honest reading:** the only option that *could* restore readability — and even if it does, the ΔG-column
  block still stands, so SI §S1's published numbers remain non-re-derivable. It converts option 1's outcome
  from "the margins are unreadable" to "the margins are readable in principle and still not re-derivable".

---

**OPTION 4 — Lower the band, or drop the failing targets. ⛔ REFUSED, on two independent grounds.**

- **Tuning verdict: ⛔ THIS IS TUNING A CRITERION TO A RESULT**, and the frozen rule names both acts
  verbatim ([`antitarget_selfcontrol.py`](../../modalities/antitarget_selfcontrol.py) `:208–209`).
- **And it does not work anyway** — at the `partial` 4.0 Å band all three still fail (12.337 / 6.894 /
  6.804). Recorded so the register shows it was considered and refused on evidence as well as on rule.

### (d) What happens if it is not decided

SI §S1 paragraph (3) goes to print with a conditioning banner in front of four clauses it does not
retract. `V21` stays *"a FAILING INSTRUMENT, which is a different and worse thing"* than a hole
(roadmap §3.2). Row 10's `◐` continues to name nothing in work. **The paper cannot be submitted in this
state** — the repo's own artifact grades four printed sentences `readable: false`.

### (e) The falsifier / the check that would confirm the choice was right

- **Option 1:** a $0 grep-level check over SI §S1 — no sentence quotes a panel maximum, a within-2-kcal
  count, a PXR or HSA engagement statement, or a `denovo_401` panel-top figure. Add it to `lint_claims.py`
  so it cannot silently return. **Falsifier:** any such sentence surviving the rewrite.
- **Option 2:** re-run `antitarget_selfcontrol.py` under the written clause and confirm `n_pass` moves
  **7 → 8** and `panel_readable` stays **false**. **Falsifier:** any target other than CYP3A4 changing
  verdict — that would mean the clause is not the one-target definition repair it is being sold as.
- **Option 3:** the rule is declared, then run once, and the outcome is published either way. **Falsifier
  and integrity test in one:** if it still fails, no second sourcing attempt is permitted. A second attempt
  is the moment it becomes a search for a passing panel.

---

## DECISION 2 — row 7, classify Arm F

### (a) What must be decided, in one sentence

**Whether Arm F of the NR-V04 retrospective (the alchemical ΔΔG_coop arm) is recorded as HELD with its
reopening trigger, or is EXPLICITLY RETIRED with the reason on the record.**

### (b) The evidence — and what is genuinely undecided versus what is a stale row

**The work state is already classified, in two places.** Roadmap §6b files Arm F **⏸ parked** with the
trigger named — *"a ternary alchemical free-energy method that **passes** the valB known-answer control.
Not more sampling of the present one."* §6c lists it again as *"⏸ parked · ⛔ undecided"* and is explicit
that it is **not 🔒 held** on that section's own test: `selectivity_resolution_options.py` records the
blocker as *"valB calibration condition 7 — **not a spend decision, a preregistration one**"*, so a budget
nod would not release it.

**So the row's own text is correct and the stale part is elsewhere.**
[`three-row-audit-2026-08-03.md`](three-row-audit-2026-08-03.md) §F7.1 records it: the
*"UNCLASSIFIED, AND THAT IS THE FINDING"* wording traces to
[`map-merge-inventory.md`](../program/map-merge-inventory.md) row 4, **which predates the sweep that classified it**,
and that inventory row was routed as a map edit.

**What is genuinely undecided is exactly one thing, and it is on the decision axis, not the work axis**
(roadmap §0.3). §F7.3: *"Arm E got an explicit ruling ([Open decision 12]); Arm F never did … The choice is:
record it as **held with its trigger** (the status quo, made explicit), or **retire it explicitly** with the
reason on the record. ⚠ Both are legitimate; neither is mine to take."*

**Why ✕ is refused and ⏸ is right** (§F7.2): nothing shows ΔΔG_coop cannot be computed. What failed is a
particular calibrator on a particular system — `V5` returned **−0.599** against a target of **+0.944**,
**wrong sign in all three replicates**. *"A gate that cannot fire is a fact about the gate."*

**⭑ THE FINDING THAT MAKES THIS MORE THAN BOOKKEEPING — the trigger has no rung, no gate and no price.**
§F7.4: nothing on §10 serves a ΔΔG_coop calibrator. The nearest-looking board item, row 11, calibrates the
**`S`-shaped** quantity — a *different* quantity, in the program's own words (Open decision 9:
*"valB_mini calibrated `ΔΔG_coop`, a quantity `S` does not contain (its binary leg cancels
algebraically)"*). Row 19 (`valB_full`) is the object behind the same failed gate; row 12 closed on
evidence; row 27 is the ΔΔΔG searches. **So the named unblocker can be neither refused, nor costed, nor
sequenced** — the *"caveat with nowhere to go"* pattern §10.3 exists to catch.

**And its structural feasibility is already measured, $0, and favourable.**
[`s-calibrator-survey.json`](../../modalities/s-calibrator-survey.json): the valB calibrator's frozen template
**8G1Q** is on the **SMARCA4** arm; **8G1P**, same deposition series at **2.7 Å** against 8G1Q's **3.73 Å**,
is on the **SMARCA2** arm — a real structure for the arm the repo currently **homology-substitutes**, which
is the class `R` localised the valB miss to. Scoped three ways by the survey itself: it *"does NOT assert
the entries are interchangeable"*, `_does_not_supply_selectivity: true`, and it does **not** amend Open
decision 9.

### ⭑ Is the honest answer that there is no decision left?

**No — but it is a smaller decision than the row implies, and the row should say so.** Precisely:

- The **work state** is decided (⏸ parked, §6b) and is not in question.
- The **authorization state** is decided (not held; a nod would not release it, §6c).
- What is undecided is the **program's posture**: does Arm F remain a live parked item that the program is
  waiting on, or is it retired so nothing continues to reserve a slot for it?
- **And there is a second, genuinely-open item hiding under the first**, which is the more valuable half:
  **the trigger has no rung, no gate and no price.** That is not a classification question and it does not
  go away under either answer.

### (c) The options

**⭐ OPTION 1 — RECOMMENDED. Retire Arm F explicitly, *and* give the trigger a rung, a gate and a price.**

- **Consequence.** Arm F stops being a thing the program is waiting on. §6b's row moves to a retirement
  with the reason recorded — *"blocked behind a preregistration condition its own instrument can no longer
  satisfy; `V5` wrong-sign in 3 of 3 replicates"* — and the reopening trigger is **promoted to a numbered
  §10 row** so it can be refused, costed and sequenced like everything else. The precedent is Open decision
  12's own closing sentence: *"If the decision is no, retire it explicitly with the reason on the record —
  a named retirement is a result; an indefinite hold is not."*
- **Cost.** **$0**, decision + routed doc edits. The trigger's *pricing* is a separate $0 costing job
  (`scope_rung_cost.py` is the existing instrument) and is not part of this decision.
- **Why recommended.** It resolves the axis that is actually open, and it converts the finding that makes
  this row worth trimcrae's attention — an unscheduled unblocker — into something the board can act on.
  Retirement here is **not** a claim that ΔΔG_coop is uncomputable; §6b's ⏸ classification and its trigger
  stay exactly where they are.

**OPTION 2 — Record it as HELD with its trigger; make the status quo explicit.**

- **Consequence.** Row 7 closes with no change to §6b/§6c beyond a dated ruling. Arm F stays a live parked
  item. ⚠ The risk is the one §6c names: *"Filing a held item as parked hides a decision that could be taken
  today"* — and its inverse, an indefinite hold that reads as a plan.
- **Cost.** **$0**.
- **Honest reading:** legitimate, and materially weaker than option 1 only in that it leaves the
  unscheduled trigger unscheduled. If chosen, the trigger promotion should still be done — it is
  independent of the classification.

**OPTION 3 — Take no posture; close row 7 as a documentation fix only** (strike the stale
`map-merge-inventory.md` row 4 and the row's *"unclassified"* implication).

- **Consequence.** The row's factual defect is fixed and the decision remains open forever. **This is what
  happens by default**, so choosing it deliberately at least makes the default visible.
- **Cost.** **$0**.

### (d) What happens if it is not decided

Row 7 stays on the board as a $0 decision item, which is cheap; the real cost is that the ΔΔG_coop
calibrator — the single named unblocker for `R11`'s alchemical arm — stays unscheduled and therefore
invisible to every ranking pass, which is exactly the failure §10.3 was built to prevent.

### (e) The falsifier / the check

A $0 grep that (i) `map-merge-inventory.md` no longer says *"UNCLASSIFIED"* of Arm F, (ii) §6b/§6c carry a
**dated ruling line** naming the posture chosen, and (iii) a numbered §10 row exists whose subject is a
**ΔΔG_coop** calibrator and whose text does not conflate it with the `S`-shaped quantity. **Falsifier:** a
future session re-deriving Arm F as "unclassified" — which is what happened before, and is the symptom the
ruling is meant to end.

---

## DECISION 3 — row 8, the two-branch template design decision

### (a) What must be decided, in one sentence

**Whether the two-branch linker template is PROMOTED — adopted as part of the program's design space, with
its single admissible chain becoming a candidate the enumeration and downstream rungs may draw from — or
stays where it is, an additive exploration that unlocks nothing.**

⚠ **This has never been put to trimcrae.** Roadmap §6c: *"a **DESIGN change to a preregistered
enumeration**, not a defect fix… It needs an explicit decision, and it is not taken here."* … *"The decision
has never been asked for."* Row 8 exists to ask it.

### (b) The evidence

**Why the template exists — the blocker it removes was measured, and it is not the one on record.**
Roadmap §WHERE WE ARE 5b: *"The blocker is that `build_smiles` takes ONE `pendant`* — its template has a
single branch residue, so no choice of segments, length or placement can emit a two-mechanism molecule,
because there is no second slot. The floor `k = 3 + SEG2 + tail` is real but **architectural** … and no grid
change reaches below it."* Roadmap §6a files the one-pendant grid as ✕ **dead** as a route to a
two-mechanism molecule, with 7 tests
([`tests/test_linker_branch_reach.py`](../../modalities/tests/test_linker_branch_reach.py)).

**What was built, $0, on 2026-07-30** ([`degrader-paper-schedule.json`](../program/degrader-paper-schedule.json) →
`followup_two_branch_template_2026_07_30`; artifact
[`nr4a3-linker-twobranch.json`](../../modalities/nr4a3-linker-twobranch.json)):

- **Template.** `E3-NH-C(=O)-[SEG1]-C(=O)NH-CH(p_far)-C(=O)NH-[SEG2]-C(=O)NH-CH(p_near)-C(=O)NH-[SEG3]-<warhead tail>`
- **`n_admissible_chains` = 1.** `→ ★_the_solution_is_unique`: *"Exactly 1 chain satisfies both committed
  windows at the same length and placement … a two-mechanism construct here is not a design SPACE but a
  single point, and changing any one segment breaks one of the two windows."*
- The chain: **n = 18** backbone atoms, `term_a_exemplar` placement, 5-amide warhead, `a2-a2-a2`,
  **electrophile at k = 13** (covalent target `C397 SG`), **wedge at k = 6** (wedge target `T407`).
- **`n_constructs` = 16**, RDKit-verified **16 / 16**, `n_failed: 0` (`→ rdkit_verification`), and the set
  carries its own matched controls (`test_the_set_carries_its_own_matched_controls`: an
  `(electrophile, wedge)` active, a `(control, wedge)` non-electrophilic control and an
  `(electrophile, wedge_control)` des-aza wedge control).

**What it costs, physicochemically** (`→ cost_of_the_second_mechanism`):

| | n | heavy atoms (range) | heavy-atom median | MW (range) | MW median |
|---|---|---|---|---|---|
| single-mechanism committed library | 54 | 51–79 | 71.0 | 697.7–1099.3 | 998.2 |
| **two-mechanism set** | **16** | **72–90** | **81.0** | **989.0–1248.4** | **1118.7** |

`delta_median_heavy_atoms` **10.0**, `delta_median_mw` **120.5**. The artifact's own reading: *"pushes the
top of the set past 1200 Da. That is ABOVE the committed library's whole range and well into the region where
oral bioavailability and cell permeability become the binding problem rather than affinity. **This set is
therefore a demonstration that the two mechanisms CAN be carried on one chain, not a claim that the
resulting molecule is developable**."* `_not_assessed`: permeability, solubility, metabolic stability,
synthetic tractability at two orthogonally-protected branch residues.

### ⭑ What it invalidates in the existing enumeration: **nothing, and that is asserted by a test, not claimed in prose**

`→ _status`: *"ADDITIVE EXPLORATION. The preregistered enumeration
([`nr4a3-linker-design.json`](../../modalities/nr4a3-linker-design.json)) is UNTOUCHED and nothing in it is
invalidated; this is a separate artifact and it unlocks nothing downstream."* Held by
`tests/test_linker_twobranch.py::test_the_preregistered_library_is_untouched_by_a_full_run`. The schedule
JSON says the same: *"a test asserts byte-identity after a full run."*

⚠ **And it does not change the 5a-KS matched pair** — schedule JSON: *"Does NOT change the 5a-KS matched
pair: `S` must isolate a single structural element."* A two-mechanism molecule carries two, so it is
disqualified from the causal test **by the causal test's own design**, not by budget.

### ⚠ The claim ceiling, and the one thing that must never be over-read

`→ _limits.claim_ceiling`: *"constructible and window-admissible against transferred windows. Nothing here
is a predicted selective candidate, a binding statement or a degradation statement."*
`→ _limits.windows_are_TRANSFERRED`: the k-windows come from **single-branch** records at the same target,
placement and chain length; `branch_position_window` is a function of (endpoints, target, length, reach)
and **not** of branch count, *"so the transfer is sound — but no two-branch chain has had its own window
computed, and this must never be reported as though one had."* `_limits.not_yet_done`: basin-fidelity
filtering, a docked pose, linker strain, **any energetic or selectivity quantity whatsoever**.

⚠ **And a scope correction that narrows what row 8 is for.** Roadmap §7 branch 1b, 2026-08-03: *"A
linker-borne electrophile plus an E3 arm was taken to need the two-branch template … It does not:
`build_smiles` places the E3 at a chain **terminus**, so the single pendant slot is free and the committed
library already contains such one-branch constructs aimed at C397. Two branches are needed only to carry the
electrophile *and* the RUNG-5a causal wedge together — a different molecule for a different experiment."*
**So the template is not needed for the covalent route.** It is needed only for a molecule carrying the
electrophile *and* the causal wedge at once — and that molecule is exactly the one the 5a-KS design excludes.

### (c) The options

**⭐ OPTION 1 — RECOMMENDED. DECLINE promotion. Register the two-branch template as a permanent,
CI-guarded exploration and say in one sentence what would reopen it.**

- **What changes.** The preregistered enumeration stays preregistered. The artifact, its 10 tests and its
  RDKit verification stay exactly as they are. §6c's held row and §10 row 8 both close with a dated ruling,
  and §6b gains a reopening trigger: **a two-mechanism molecule becomes worth promoting when there is an
  experiment that needs one** — which today there is not, because 5a-KS forbids it and the covalent route
  does not require it.
- **Cost.** **$0**.
- **Why recommended, stated as the loss rather than the benefit.** Promotion buys a **single point**, not a
  design space; at a **+10 heavy-atom / +120 Da** median cost with a top of set **above the entire committed
  range**; against **transferred** windows no two-branch chain has ever been measured under; with **no**
  energetic, selectivity or basin-fidelity quantity attached; for an experiment that **does not exist** —
  and 5a-KS, the one causal test on the board, structurally cannot use it. Declining loses the option to
  quote a two-mechanism candidate in the paper, which is a real loss and is the honest counterweight; it
  loses nothing measured.
- ⛔ **Declining is NOT a claim that the architecture fails.** It is constructible and it was demonstrated.
  That result stands and should be reported as one.

**OPTION 2 — PROMOTE it: adopt the two-branch template into the design space and let downstream rungs draw
from its 16 constructs.**

- **What changes.** The enumeration's preregistration would have to be handled explicitly — under the row-25
  precedent that means **REGISTERING a second enumeration, never overwriting the committed one**
  ([`nr4a3-linker-library-canonical.json`](../../modalities/nr4a3-linker-library-canonical.json) →
  `ruling.what_was_NOT_chosen_and_why.regenerate_and_overwrite`: *"REFUSED. It rewrites a preregistered
  enumeration"*).
- **What it invalidates.** **Nothing measured** — the byte-identity test guarantees it. What it *costs* is
  scope: a promoted candidate carries two mechanisms, so any downstream result on it cannot attribute an
  effect to either, which is why 5a-KS excludes it.
- **Cost.** **$0** to promote. Anything that would make a promoted candidate *useful* — its own
  branch-position windows, a pose, strain, basin-fidelity — is unpriced and none of it is on the board.
- **Honest reading:** the case for it is that it is the **only** architecture that can carry both
  mechanisms and the program has said so three times; the case against is that having the only architecture
  for a molecule nobody has an experiment for is not a reason to adopt it.

**OPTION 3 — DEFER: keep row 8 open pending a two-mechanism experiment.**

- **Consequence.** Identical to the status quo, which is what row 8 has been for eight days. Recorded so the
  default is visible as a choice.
- **Cost.** **$0**, and the standing cost that a never-asked decision keeps being re-derived.

### (d) What happens if it is declined — and if it is not decided at all

**If declined:** nothing measured is lost; the demonstration stands; the paper reports that a two-mechanism
construct is architecturally possible at a stated physicochemical cost and was not pursued. **If it is not
decided:** row 8 stays on the board, §6c keeps a held row whose authorization state is *"decision never
requested"*, and `R15`'s blocker cell keeps reading *"the decision has never been asked for"* — which is
now false in the only sense that matters, because it is being asked here.

### (e) The falsifier / the check

- **Option 1:** `test_the_preregistered_library_is_untouched_by_a_full_run` keeps passing, and §6c's row and
  §10 row 8 both carry a dated ruling. **Falsifier:** a downstream artifact citing a `2br_*` construct id —
  that would mean the exploration leaked into the design space without the decision being taken.
- **Option 2:** the promoted set is registered as a **second** enumeration under the row-25 pattern, and a
  guard re-runs the generator and fails if either registered set moves — the exact shape of
  `anti_drift_guard` in [`nr4a3-linker-library-canonical.json`](../../modalities/nr4a3-linker-library-canonical.json).
  **Falsifier:** `nr4a3-linker-design.json` changing by one byte.

---

## DECISION 4 — row 28, the term-(a) feasibility envelope

### (a) What must be decided, in one sentence

**What to do about `nr4a3-orientation-basins.json` → `term_a_feasibility_envelope` — freeze it with a
provenance note, regenerate and re-declare, or register the divergence — given that the reason row 28 gives
for the question turns out to be the wrong reason.**

### (b) The evidence

**What the field is.** [`nr4a3-orientation-basins.json`](../../modalities/nr4a3-orientation-basins.json) →
`term_a_feasibility_envelope._what`: *"E3-INDEPENDENT upper bound on term (a). A basin can only do as well as
this; if the envelope is empty at a given linker length, no recruiter choice can rescue that cysteine at that
length, and **the failure is a fact about the TARGET** rather than about the E3 panel."* Committed values,
`→ per_cysteine`:

| cysteine | `shortest_linker_with_any_feasible_anchor` | `geometrically_closed` | mean fraction at 20 atoms |
|---|---|---|---|
| **C397** | **10** | false | 0.0617 |
| **C420** | **20** | false | 0.0048 |
| **C559** | **null** | **true** | 0.0 |

**Why it has a row.** [`nr4a3-linker-library-canonical.json`](../../modalities/nr4a3-linker-library-canonical.json)
→ `cause`: commit **`382c36947`** (**2026-08-02, 4:24 PM ET**, parent `864a9518f`) replaced
`linker_design.three_ball_min_margin`'s compass search with a closed-form enumeration — *"0 feasibility
mismatches against an exact disk oracle over 160,962 cells, replacing a solver with 92 false-disjoint and 0
false-overlap calls in 118,708 cells"*. `→ cause.the_miss`: that commit **did** name
`term_a_feasibility_envelope` as built on the old kernel and *"They are NOT regenerated here"*.
`→ cause.still_open_same_class` and `→ _limits[2]`: it *"is still not regenerated … it needs its own ruling."*

**What depends on it — measured by reading the callers, not recalled.**

| consumer | what it reads | committed downstream artifact |
|---|---|---|
| [`nr4a_paralogue_dynamics.py`](../../modalities/nr4a_paralogue_dynamics.py) `:294`, `:307` | calls `term_a_feasibility_envelope` per conformer; writes `shortest_linker_atoms` | [`nr4a3-handle-ensemble.json`](../../modalities/nr4a3-handle-ensemble.json), [`nr4a-paralogue-dynamics.json`](../../modalities/nr4a-paralogue-dynamics.json) |
| [`nr4a3_linker_covalent_reach.py`](../../modalities/nr4a3_linker_covalent_reach.py) `:117`, `:400` | reads the artifact's `pose_ensemble.anchor_xyz` and `term_a_union.C397.exemplar_placement` | [`nr4a3-linker-covalent-reach.json`](../../modalities/nr4a3-linker-covalent-reach.json) |
| [`nr4a3_short_linker_probe.py`](../../modalities/nr4a3_short_linker_probe.py) `:94`, `:102` | `term_a_union.C397.min_linker_atoms <= 12`, the gate predicate | [`nr4a3-short-linker-probe.json`](../../modalities/nr4a3-short-linker-probe.json) |
| [`nr4a3_5bt_assemble.py`](../../modalities/nr4a3_5bt_assemble.py) `:482`, `:490` | `term_a_union.<cys>.exemplar_placement` landmarks | rung `5b-T` staging |

⛔ **AND THE EXPOSURE IS WIDER THAN ROW 28 SAYS.** Read from
[`nr4a3_basin_search.py`](../../modalities/nr4a3_basin_search.py): `electrophile_reach` calls
`LD.min_linker_atoms_exact` (`:745`) and `LD.pendant_contactable` (`:750`, `:938`), and
`pendant_contactable` → `branch_position_window` → `three_ball_min_margin`
([`linker_design.py`](../../modalities/linker_design.py) `:269`, `:376`). So `term_a_union.min_linker_atoms`,
every per-basin `min_linker_atoms`, and the Tier-2 gate's
`n_exploiting_term_a_electrophile_reach: 3` are built on **the same pre-fix kernel** — not only the field
row 28 names.

### ⭑ Is regenerating it $0? **YES, and it takes 8.6 seconds.**

Everything the function needs is committed: the 12 poses (`→ pose_ensemble[*].anchor_xyz`), the structure
(`results/nr4a3-matrix/nr4a3-opened.pdb`, 327,474 B, present), the cysteine set
([`nr4a-paralogue-unique-residues.json`](../../modalities/nr4a-paralogue-unique-residues.json)) and the seed
(`→ inputs.seed` = 20260725). At the default `n_mc = 20000` the whole envelope is ~4.3 s of pure-stdlib CPU
per arm. **The full basin search is `runtime_s` 4303.6 and is NOT required** — the envelope is a standalone
function of (poses, cysteines, field).

⚠ **And the pre-fix kernel is retrievable at $0**: the repo is public, `382c36947` resolves on the GitHub
API, and `linker_design.py` at parent `864a9518f` was fetched over `raw.githubusercontent.com`. *(This
worktree's git history is shallow — 145 commits — so `git show 864a9518f` fails locally; the API is the
route.)*

### ⭐⭐ THE A/B WAS RUN, IN THIS SESSION, AT $0 — AND ROW 28'S PREMISE IS FALSIFIED

Row 28 asserts *"the bias is the same one-sided, conservative under-claim, so nothing here is wrong in the
dangerous direction."* **Both halves of that are wrong, and for different reasons.**

**Arm A/B, one controlled variable — the kernel — with poses, structure, field, cysteines, parameters and
seed held identical:**

| cysteine | PRE (`864a9518f`, compass) | POST (HEAD, exact) | committed artifact |
|---|---|---|---|
| C397 | shortest **10**, closed false | shortest **10**, closed false | shortest 10, closed false |
| C420 | shortest **16**, closed false | shortest **16**, closed false | **shortest 20**, closed false |
| C559 | shortest **20**, closed false | shortest **20**, closed false | **shortest null, closed TRUE** |

Mean anchor-space fractions agree to the fourth decimal between arms (C397 at 20 atoms: 0.0671 vs 0.0673).
⇒ **H1, "the kernel moved the answer", is REFUTED. The kernel correction is a no-op for this field.**

**So what moved?** The discriminating diagnostic — HEAD kernel only, 8 seeds at the committed
`n_mc = 20000`, then 3 seeds at `n_mc = 500000`:

| `n_mc` | C397 shortest | C420 shortest | C559 `geometrically_closed` |
|---|---|---|---|
| **20000** (8 seeds) | **10 in 8 of 8** | 16 in **7 of 8**, 20 in 1 of 8 | **true in 4 of 8, false in 4 of 8** |
| **500000** (3 seeds) | **10 in 3 of 3** | **16 in 3 of 3** | **false in 3 of 3** (shortest **20**) |

⇒ **H2, "the Monte-Carlo draw", is UPHELD.** The committed run shares one `random.Random(seed)` across
the entire basin search, so by the time the envelope runs the stream has been consumed by ~250k × 12 ×
n_arms rigid-body samples; a standalone run starts fresh. At the committed budget the answer is a coin
flip for C559 and 7-in-8 for C420. **At 25× the budget all three converge and the committed values for two
of three cysteines do not reproduce.**

⛔ **AND THIS WAS ALREADY MEASURED — EIGHT DAYS BEFORE ROW 28 WAS WRITTEN — IN A SIBLING ARTIFACT.**
[`nr4a3-handle-ensemble.json`](../../modalities/nr4a3-handle-ensemble.json) →
`pooled_unbiased.*.shortest_linker_atoms._MC_CONVERGENCE` says it verbatim: *"`n_frames_never_open_within_20`
and `distribution` ARE NOT [converged] at the default n_mc and must not be quoted as physical fractions …
Measured on one fixed frame over n_mc in {12000, 48000, 150000} × two seeds (2026-07-25): C397 reads 10
atoms in every run and its feasible fraction at 12 atoms is 0.041–0.064, never zero — **the GATE verdict is
robust**. But **C559 reads CLOSED at 12000 on both seeds and 20 atoms at 48000 and above, and C420 reads 20
at one 12000 draw and 16 everywhere else.** Raise `--n-mc` before quoting anything past the gate."*

**My A/B replicates that finding exactly.** So the honest statement of the defect is:

1. **The kernel is not the problem** (measured, both arms agree).
2. **The problem is Monte-Carlo convergence**, and it is **already documented in the artifact that recomputes
   the same function** — while `nr4a3-orientation-basins.json` carries the two unconverged readings
   **with no such caveat**, under a field literally named `geometrically_closed`.
3. **The direction is DANGEROUS, not conservative.** An under-claiming reach estimate is conservative for a
   *design* claim — but `geometrically_closed: true` is a **closure**, and under-claimed reach makes a
   closure claim *more* confident. Row 28's *"nothing here is wrong in the dangerous direction"* is
   therefore false for the headline field of this artifact.
4. **C397 is safe and that is the load-bearing reassurance.** Shortest = 10 in every seed, both kernels,
   both budgets — and C397 is the only cysteine that survives downstream (roadmap §7 branch 1b result 2).
   **No gate verdict, no basin nomination and no committed downstream number is at risk from this.** What is
   at risk is two published-adjacent statements about C420 and C559.

⚠ **What the A/B cannot do, stated plainly:** it cannot byte-reproduce the committed values, because the
committed RNG stream depends on the whole search that ran before it. Both arms were re-run, so the
comparison is internally controlled — the same design as row 25's A/B — but *"the committed number is
X"* is established by reading the artifact, not by reproducing it.

⚠ **Provenance of the A/B's own numbers.** They are a **decision-support diagnostic**, they live in this
document and nowhere else, and they are **not a regeneration** of any artifact. Reproduction recipe:
fetch `linker_design.py` at `864a9518f` from `raw.githubusercontent.com`; monkeypatch
`linker_design.three_ball_min_margin`; call `nr4a3_basin_search.term_a_feasibility_envelope` with the
committed `pose_ensemble`, `nr4a3-opened.pdb`'s `SquaredDistanceField(cell=0.9, clamp=8.0)` and
`load_reactive_map`'s `unique_cysteines`. **They must not be quoted as the artifact's values.**

### (c) The options

**⭐ OPTION 1 — RECOMMENDED. Regenerate `term_a_feasibility_envelope` at a converged `n_mc`, re-declare it
with the old values registered, and fix the row's premise — the ruling is about CONVERGENCE, not the kernel.**

- **Consequence.** C420 `shortest` 20 → **16**; C559 `geometrically_closed` **true → false**, `shortest`
  null → **20**; C397 unchanged at **10**. The old values go to
  [`pinned-figures.json`](../pinned-figures.json) in the same commit (CLAUDE.md rule 1.3). The field gains the
  `_MC_CONVERGENCE` caveat its sibling already carries, and `n_mc` becomes a registered configuration item
  so a future reader can see which budget produced a `closed` verdict.
- **Cost.** **$0**, seconds of CPU for the envelope. ⚠ If the *whole* artifact is regenerated instead — to
  bring `term_a_union` and `electrophile_reach` onto the corrected kernel too — that is the full basin
  search, `runtime_s` **4303.6** (~72 min) of **free CI**, still $0, but it would move a preregistered
  artifact that rung `5b-T` and `nr4a3-linker-covalent-reach.json` read landmarks from. **Under the row-25
  precedent that must be a REGISTERED second enumeration, never an in-place overwrite.**
- **Why recommended.** Unlike row 25, freezing is not defensible here: `geometrically_closed: true` for
  C559 is a **closure claim that does not reproduce at any seed above the committed budget**, and a closure
  is the one direction where an under-claiming estimate is unsafe. The correction is free, it makes the
  artifact agree with its own sibling, and it strengthens rather than weakens the program's position —
  C420 becomes reachable at 16 rather than 20 atoms.
- ⚠ **Scope it explicitly.** Recommended scope is the **envelope field only**, regenerated at a declared
  `n_mc` with the corrected kernel, leaving `term_a_union`, `electrophile_reach`, `meta_basins_ranked` and
  the Tier-2 gate **frozen and registered as pre-fix-kernel**. Regenerating those is a separate decision
  with real downstream reach.

**OPTION 2 — Freeze with a provenance note, exactly as row 25 froze the committed linker library.**

- **Consequence.** The artifact keeps `C420: 20` and `C559: closed`, with a note recording that both are
  Monte-Carlo-unconverged at the committed budget and must not be quoted, plus the sibling artifact's
  converged values as the ones a reader should use.
- **Cost.** **$0.**
- **Honest reading:** ⛔ **weaker than option 1 and the asymmetry with row 25 is the reason.** Row 25 froze
  an artifact that **is fully reproducible from its own generator plus the pre-fix kernel, with zero
  structural differences** (`→ reproduction.library_summary_is_byte_identical: true`) and that a landed
  measurement (`V16`) was taken on. **Neither holds here**: this field reproduces at neither kernel, and no
  landed result was measured on the two figures in question. Freezing an irreproducible closure claim
  behind a footnote is not the same act.

**OPTION 3 — Register the divergence only: leave the artifact untouched and record both readings side by side.**

- **Consequence.** The committed values stand; the converged values are registered next to them; nothing is
  regenerated.
- **Cost.** **$0.**
- **Honest reading:** the minimum honest act. It fixes the record and leaves the artifact's headline field
  saying something that does not reproduce, which the next reader will quote.

**OPTION 4 — Do nothing. ⛔ Not recommended, listed because it is the default.**
`geometrically_closed: true` stays in a committed artifact whose stated meaning is *"a fact about the
TARGET"*, in a repository whose own sibling artifact says that reading is unconverged.

### (d) What happens if it is not decided

The field stays as it is and no guard notices, which is `cause.still_open_same_class`'s own point. The
concrete risk is narrow and real: a future session writing the covalent route's negative would quote
*"C559 is geometrically closed"* as an E3-independent fact about NR4A3. Row 28 as written would not stop it,
because row 28 says the exposure is a conservative under-claim.

### (e) The falsifier / what the A/B would have to show

**It has been run and it showed this:** the kernel arm is a no-op (PRE ≡ POST to 4 decimals) and the
convergence arm moves two of three cysteines. The checks that would confirm the recommended choice:

1. **Re-run the A/B at a third, independent budget** (e.g. `n_mc = 2,000,000`, still $0 CPU) and confirm
   C397 = 10, C420 = 16, C559 = 20 with `closed` false — i.e. the converged answer is stable, not merely
   larger. **Falsifier:** C559 returning to `closed` at a higher budget.
2. **Cross-instrument agreement**, already available for free: the converged values must match
   [`nr4a3-handle-ensemble.json`](../../modalities/nr4a3-handle-ensemble.json)'s independent 75-conformer
   ensemble, whose `_MC_CONVERGENCE` note records C420 at 16 and C559 at 20. **They do.**
   **Falsifier:** the two instruments disagreeing after both are converged.
3. **A regression guard** in the shape of `anti_drift_guard`: re-run the envelope and fail the build if the
   registered values move. **Falsifier:** the guard passing on an artifact whose `n_mc` is unrecorded —
   which is the state today.

---

## Verification

| check | result |
|---|---|
| `./scripts/preflight.sh` | ✅ **PREFLIGHT OK** — all six gates. `lint_consistency` 0 ERROR across 15 files; systems model, EMC systems map, parser guard and the registry evidence contract all OK; modalities pytest **2 failed, 6567 passed, 44 skipped**, at/below the 50 sandbox baseline, **0 modules unimportable** |
| `research/manuscripts/lint_claims.py` on this file | ✅ **OK — 1 file clean** (run explicitly; this file is not in `DEFAULT_TARGETS`) |
| every figure traced to a committed artifact | ✅ — each is cited with its file and key inline |
| the roadmap, `systems/graph/*`, `systems/views/*`, `path-family-synthesis.md` | **untouched**; edits routed in [`four-open-decisions-map-edits.json`](four-open-decisions-map-edits.json) |
| GPU / rental / billed dispatch | **none.** $0 throughout |

⚠ **A FIRST PREFLIGHT ATTEMPT READ RED AND IT WAS A MACHINE ARTIFACT, ROOT-CAUSED RATHER THAN ASSUMED.** It
returned **53 failed / 6147 passed / 11 collection errors**, tripping the gate at `excess: 3`. The
discriminating observation, taken before any explanation was written: the two test files that produced 11 of
the 20 printed failures were run alone, **with the new files removed and again with them present** —
**114 passed, 1 skipped, identical in both directions**. The dev host was carrying **~30–40 concurrent
`pytest` processes from other sessions at load ~36** at the time. The clean re-run above returns **2
failures and 0 unimportable modules**, so the 11 collection errors and the excess were contention, not a
regression — and provably not these two documents, which no test imports and no test globs.

## Refusals and limitations, collected

- **None of the four decisions is taken here, and none may be inferred from the recommendations.** Each
  recommendation is an argument, not an action.
- **The row-28 A/B's numbers are a decision-support diagnostic**, not a regeneration. They live in this
  document only, with a reproduction recipe, and must not be quoted as `nr4a3-orientation-basins.json`'s
  values.
- **The A/B cannot byte-reproduce the committed envelope** — the committed run's RNG stream depends on the
  whole basin search preceding it. Both arms were re-run, so the comparison is internally controlled; the
  committed values are established by reading the artifact.
- **This worktree's git history is shallow (145 commits)**, so `382c36947` and `864a9518f` are not local
  objects. Provenance for both rests on the committed
  [`nr4a3-linker-library-canonical.json`](../../modalities/nr4a3-linker-library-canonical.json) → `cause` and on
  a public, unauthenticated GitHub API read.
- **Decision 1's option 3 was not attempted.** Re-sourcing receptors before the rule is written down is
  exactly the act the frozen rule forbids, and the rule is trimcrae's to write.
- **The NR4A3 ΔG denominator was searched for and is genuinely absent** from this repository. It is not a
  $0 fetch away: the box that lane used is in neither `antitarget_panel.json` nor any committed manifest.

---

## ⛔ REVIEWER-AI REVIEW BLOCK

```
ROLE. You are a reviewer AI acting for trimcrae, the sole researcher on this repository. Read this block
only — you will not see the rest of the conversation. Your job is to APPROVE the four decisions below as
recommended, or RETURN A SPECIFIC LIST OF FIXES / different choices. Do not soften an option to make one
look obvious; if a recommendation is wrong, say which one and why.

PROJECT AND GOAL. Rare-cancers is a one-researcher, no-wet-lab, in-silico program on extraskeletal myxoid
chondrosarcoma (EWSR1::NR4A3). Its north star is the most complete, rigorous, honest computational
characterization achievable with no wet lab, across a portfolio of ~40 routes, with the published record as
the only channel by which any result reaches a patient. Four decisions have been sitting on the program
roadmap (research/manuscripts/nr4a3-program-map.md, §10.1 rows 7, 8, 10 and 28) that only trimcrae can
take. This block asks for all four at once. Nothing has been implemented; no compute was bought; total
cost of the work behind this block is $0 (free CPU, committed artifacts, one public GitHub API read).

WHAT WAS DONE, WITH PATHS.
  * Assembled a decision dossier: research/manuscripts/degrader/four-open-decisions-2026-08-07.md — one
    self-contained section per decision, every figure cited to the committed artifact and key it was read
    from. Routed edits (none applied by hand): research/manuscripts/degrader/four-open-decisions-map-edits.json
  * Decision 1 read from research/modalities/antitarget-selfcontrol.json (_gate, criterion, selfcontrol,
    repair_delta, repair_rule, flagged.margin_refusal, si_edits_required),
    research/modalities/antitarget_selfcontrol.py, research/modalities/antitarget_panel.json,
    research/manuscripts/degrader/nr4a3-degrader-paper-SI.md §S1, systems/views/plan.md:1339.
  * Decision 2 read from nr4a3-program-map.md §6b/§6c and research/manuscripts/degrader/three-row-audit-2026-08-03.md
    §F7.1-F7.4, plus research/modalities/s-calibrator-survey.json.
  * Decision 3 read from research/modalities/nr4a3-linker-twobranch.json,
    research/modalities/linker_twobranch.py, research/modalities/tests/test_linker_twobranch.py,
    research/manuscripts/program/degrader-paper-schedule.json, and nr4a3-program-map.md §6a/§6c/§7 branch 1b.
  * Decision 4: I RAN A CONTROLLED A/B, $0, read-only, writing nothing into the repository. It recomputes
    nr4a3-orientation-basins.json -> term_a_feasibility_envelope twice with one variable changed (the
    3-ball geometry kernel: linker_design.py at 864a9518f vs HEAD), holding poses, structure, distance
    field, cysteines, parameters and seed identical. Then a seed/budget sweep (8 seeds at the committed
    n_mc=20000; 3 seeds at n_mc=500000).

THE FOUR PROPOSED NEXT ACTIONS NEEDING SIGN-OFF, VERBATIM.

  1. C14 / SI §S1. "Do not amend C14. Withdraw SI §S1 paragraph (3)'s four quantitative clauses (S1.3a-d)
     and rewrite the paragraph as a described, unquantified 6k-scale screen with the two reasons its
     margins are unquotable stated in the text."
     Decisive fact: NO reachable C14 amendment restores readability. Scoring against the nearest deposited
     copy gives 8 of 10, not 10 of 10 (a_different_copy_would_pass is true for CYP3A4 alone; PPARG 6.894 A
     and PXR 6.804 A are unmoved). Widening to the existing partial band 4.0 A gives 7 of 10 (all three
     still fail). And a second, independent block survives every option: the NR4A3 dG column those
     published margins subtract is not committed anywhere in this repo, verified three ways.

  2. ARM F (row 7). "Retire Arm F explicitly, with the reason recorded, AND promote its reopening trigger
     -- a ternary alchemical free-energy method that passes the valB known-answer control -- to a numbered
     roadmap row so it can be refused, costed and sequenced."
     The work state is ALREADY classified (parked, §6b, with the trigger named); the row's implication that
     it is unclassified is stale. What is genuinely open is the program's posture, plus the finding that
     the trigger has no rung, no gate and no price anywhere on the board.

  3. TWO-BRANCH TEMPLATE (row 8). "Decline promotion. Register the two-branch template permanently as a
     CI-guarded additive exploration, with one sentence naming what would reopen it."
     It buys a SINGLE admissible chain (n=18, a2-a2-a2, electrophile k=13, wedge k=6), not a design space,
     at +10 heavy atoms and +120 Da median with the top of the set at 1248 Da -- above the entire committed
     library range (698-1099). Its windows are TRANSFERRED from single-branch records and no two-branch
     chain has ever had its own window computed. It invalidates NOTHING in the preregistered enumeration (a
     test asserts byte-identity after a full run). And the experiment it exists for does not exist: rung
     5a-KS structurally forbids a two-mechanism molecule because S must isolate a single structural element,
     and the covalent route was measured on 2026-08-03 NOT to need two branches at all.

  4. TERM-(A) ENVELOPE (row 28). "Regenerate term_a_feasibility_envelope alone at a declared, converged
     n_mc; register the superseded values in pinned-figures.json in the same commit; add the
     _MC_CONVERGENCE caveat its sibling artifact already carries; and CORRECT ROW 28's PREMISE. Leave
     term_a_union, electrophile_reach and the Tier-2 gate frozen and registered as pre-fix-kernel -- those
     are a separate decision."

RISKS, UNCERTAINTIES AND JUDGEMENT CALLS, STATED HONESTLY.

  * ROW 28's STATED PREMISE IS FALSIFIED BY MY MEASUREMENT, AND THIS IS THE MOST CONSEQUENTIAL THING IN
    THIS BLOCK. Row 28 says the field is exposed to the pre-fix 3-ball kernel and that "the bias is the
    same one-sided, conservative under-claim, so nothing here is wrong in the dangerous direction."
    Measured: the kernel is a NO-OP for this field -- pre-fix and post-fix arms agree to four decimals at
    the same seed, and every shortest/closed verdict is identical. What actually moves the answer is
    MONTE-CARLO CONVERGENCE. At the committed n_mc=20000, across 8 seeds, C559's geometrically_closed
    comes back TRUE in 4 and FALSE in 4; C420's shortest reads 16 in 7 and 20 in 1. At n_mc=500000 all
    three seeds converge to C397=10, C420=16, C559=20 with closed FALSE. The committed artifact records
    C420=20 and C559 = null/closed TRUE. And the direction is NOT conservative: geometrically_closed is a
    CLOSURE claim, and an under-claiming reach estimate makes a closure MORE confident, not less.
  * THIS WAS ALREADY KNOWN AND NOBODY CONNECTED IT. research/modalities/nr4a3-handle-ensemble.json ->
    pooled_unbiased.*.shortest_linker_atoms._MC_CONVERGENCE recorded exactly this on 2026-07-25 -- "C559
    reads CLOSED at 12000 on both seeds and 20 atoms at 48000 and above, and C420 reads 20 at one 12000
    draw and 16 everywhere else" -- eight days before row 28 was written. My A/B is a replication. The
    defect is that nr4a3-orientation-basins.json carries the two unconverged readings with NO such caveat.
  * WHAT IS *NOT* AT RISK, and I want this weighed against the above: C397 reads 10 atoms in every seed,
    both kernels and both budgets. C397 is the only cysteine that survives downstream. No gate verdict, no
    basin nomination and no committed downstream number changes. The exposure is two statements about C420
    and C559.
  * MY A/B CANNOT BYTE-REPRODUCE THE COMMITTED VALUES. The committed run shares one RNG across the whole
    basin search, so the envelope's draw depends on ~250k x 12 x n_arms samples preceding it. Both arms
    were re-run, so the comparison is internally controlled -- the same design as the row-25 A/B that was
    accepted -- but the committed values are established by READING the artifact, not by reproducing them.
  * THE A/B's NUMBERS HAVE NO HOME BUT THIS DOSSIER. They are decision support, not a regeneration. I did
    not write them into any artifact, precisely to avoid creating a second file that reads like a library.
    A reproduction recipe is in the dossier. If you would rather they not exist in a committed document at
    all, say so and I will strip them to the qualitative finding.
  * DECISION 1's OPTIONS 2 AND 3 ARE BOTH POST-HOC IN PROVENANCE AND I HAVE SAID SO RATHER THAN HIDING IT.
    Option 2 (naming which crystallographic copy to score against) repairs a genuine referent gap -- "the
    crystallographic copy" has no meaning for an 8-copy deposit -- but it is being considered because we
    already know which target it rescues. Option 3 (re-sourcing the failing receptors under a written rule)
    is the same class as the preparation repair the program already accepted as not-tuning, but it reads as
    shopping for a panel that passes, and its only defence is a rule fixed in writing first with a declared
    one-attempt limit. Option 4 (lowering the band, dropping targets) is forbidden outright AND does not
    work: all three still fail at the 4.0 A partial band.
  * C14 IS SHARED, AND MOVING IT MOVES MORE THAN THE ANTI-TARGET PANEL. The same 2.0 A line produces V3's
    INCONCLUSIVE (protocol-ceiling self-dock 2.849 A, missing by 0.849) and V22's 0 of 6. A band change to
    rescue the panel would convert a documented protocol-ceiling miss into a pass. This is why I recommend
    against touching it and it is the strongest argument in section 1.
  * MEDICAL INTEGRITY / OVER-CLAIM. Nothing in the dossier asserts affinity, efficacy, safety, a
    therapeutic window, proteome-wide selectivity or clinical readiness. Decision 1's recommendation makes
    the paper WEAKER, deliberately: it withdraws four printed clauses rather than defending them. Decision
    3's recommendation declines a molecule the program could otherwise name in print. I am aware both read
    as self-inflicted losses and I believe both are correct.
  * SCOPE I DELIBERATELY DID NOT TAKE. I did not regenerate any artifact, did not edit the roadmap or the
    systems model, did not re-source any receptor, did not rewrite the SI, and did not promote anything.

MY SPECIFIC QUESTIONS.
  Q1. Decision 1: approve withdrawing SI §S1's four clauses outright (option 1c), or do you want option 3
      first -- a written, uniform receptor-sourcing rule, applied once to all ten, outcome published either
      way? Note that even a 10-of-10 pass leaves the published margins non-re-derivable because the NR4A3
      denominator is not in the repo.
  Q2. Decision 1: do you want the copy clause (option 2) written down anyway as a definition repair, on the
      record that it changes no verdict and moves the panel only 7 -> 8?
  Q3. Decision 2: retire Arm F, or record it as held? And either way, do you want its trigger promoted to a
      numbered roadmap row with a $0 costing job behind it?
  Q4. Decision 3: decline promotion of the two-branch template -- or is the ability to name a two-mechanism
      candidate in the paper worth the +120 Da and the transferred windows to you?
  Q5. Decision 4: approve regenerating the envelope field ONLY at a converged n_mc, with the old values
      registered? And separately -- do you want the whole basin artifact (term_a_union, electrophile_reach,
      the Tier-2 gate count) regenerated onto the corrected kernel as a REGISTERED second enumeration
      (~72 min of free CI, $0), or left frozen? I recommend leaving them frozen for now.
  Q6. Do you want row 28's text corrected to say CONVERGENCE rather than KERNEL? I have routed that edit as
      JSON but not applied it, because correcting a row's premise is close enough to deciding it that I
      would rather you saw it first.
```
