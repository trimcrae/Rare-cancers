# NR4A1/2/3 RE-PANEL — PREREGISTRATION · ⚠ **DRAFT, NOT FROZEN** · ⛔ **RETIRED UNRUN 2026-08-02**

> ## ⛔⛔ RETIRED UNRUN — 2026-08-02. STEP 2 RETURNED **NULL**, AND THIS DOCUMENT'S OWN FREEZE CONDITION 1
> ## REQUIRED `tier: PASS`. IT IS RETIRED, NOT AMENDED, EXACTLY AS §7 SAID IT WOULD BE.
>
> The sensitivity control was scored on its complete panel and returned **NULL** on an adequately-powered
> design — exact one-sided *p* = 0.7468, reference set 462, floor 0.00216, zero technical failures
> ([`selcal-verdict.json`](./selcal-verdict.json); [roadmap gate
> record](../manuscripts/nr4a3-program-map.md#-gate-failed--the-smarca24-sensitivity-control-returns-null-on-an-adequately-powered-design-2026-08-02-1042-pm-et)).
> **Step 3 is therefore not bought: it would be money spent to reproduce a failure.**
>
> ⚠ **THE DOCUMENT IS KEPT, NOT DELETED**, and that is the point of having written it early. It is the
> record that the step-3 design was fixed *before* the verdict that killed it, so nobody later has to take
> on trust that the design was not tuned to a result. Its §4c power analysis — the finding that this shape
> was powered **≤ 0.16** against the separations already measured, and that those figures are UPPER BOUNDS
> because LOMO is not modelled — **stands on its own** and pointed at the same conclusion the tier reached
> independently. **Nothing here may be run, quoted as in force, or revived without a new step 2.**
>
> ---
>
> ## ⛔ ORIGINAL STATUS (superseded, retained): **NOT FROZEN. NOT IN FORCE. NOTHING MAY BE RUN AGAINST IT.**
>
> This document is **step 3** of [`selectivity-resolution-options.md`](./selectivity-resolution-options.md)
> §3, and step 3 **runs only if step 2 (the sensitivity control) returns PASS**. Step 2 has not returned.
>
> It is written **before** that verdict on purpose. A preregistration drafted *after* seeing the result it is
> gated on cannot be shown not to have been tuned to it; one drafted before can. Everything below that does
> **not** depend on step 2's numbers is therefore fixed now, and every field that **does** is left explicitly
> unfilled, named, and pointed at its derivation — never guessed.
>
> **It becomes frozen only when ALL of these are true**, and the freeze is a separate, dated commit:
> 1. `selcal-verdict.json` carries `tier: PASS` (any other tier and this document is **retired unrun**, not
>    amended — see §7);
> 2. every `⬜ TO BE FILLED` field below is filled **from a derivation, not a judgement**;
> 3. §6's one open decision is answered by trimcrae;
> 4. the STATUS block above is replaced by a freeze stamp, and the filename loses `-DRAFT`.
>
> `tests/test_nr4a_repanel_prereg_draft.py` fails if this file is read as frozen while it still says DRAFT,
> and fails if a `⬜ TO BE FILLED` marker is deleted without a value replacing it.

---

## 1 · What this panel asks, and what it cannot ask

**Question.** Does the ensemble endpoint-MD readout discriminate NR4A1 / NR4A2 / NR4A3 for the NR-V04
non-covalent chemotype, on a design whose power and reference sets were fixed before the data?

**⛔ What it cannot ask, and this is not a formality.** The NR-V04 system is **covalency-confounded**:
feasibility Leg 0 measured the reactive **Cys551 as unique to NR4A1** (Tyr in NR4A2, Thr in NR4A3, no cysteine
within ±5), so warhead chemistry alone is *sufficient* to explain the reported selectivity. This panel
therefore tests **the non-covalent arm's geometry only**, and a positive result is **directional concordance
with a reference, not an attribution to ternary geometry**. That limit is a property of the system and no `n`
removes it — which is precisely why the sensitivity control had to be run on a *different* pair
(SMARCA2/SMARCA4) before this document could exist at all.

**This is NOT an extension of the NR-V04 retrospective prereg.** Its §4d may not be invoked on a wrong-sign
result, and the retrospective returned tier DISCORDANT. This is a **new preregistration**, and the distinction
is the whole reason the options paper wrote step 3 as one.

---

## 2 · Design — fixed now

| item | value | where it is DERIVED (never typed here) |
|---|---|---|
| arms | NR4A1, NR4A2, NR4A3 | `selectivity_resolution_options.NR4A_REPANEL_SHAPE` |
| co-fold models per arm | see shape | `NR4A_REPANEL_SHAPE` |
| replicas per model | see shape | `NR4A_REPANEL_SHAPE` |
| total legs · plan $ · range | see sequence | `selectivity_resolution_options.recommended_sequence()` step 3 |

⚠ **No leg count and no dollar figure appears in this document** (CLAUDE.md §1). They have one home, they are
derived from the throughput table and the planning rate, and a copy here would go stale silently and then be
quoted in a paper.

**Unit of independence: the co-fold MODEL.** Per-leg values are collapsed to model means before any test, so
velocity replicas cannot inflate the reference set. Identical to NR-V04 prereg §4a and to the sensitivity
control, and it is why options B1/B2 (more replicates) were refused: replicates do not move a reference set.

---

## 3 · Primary endpoint: **E1, unchanged**

The primary is the **interface-RMSD plateau (E1)**, exactly as registered for the NR-V04 retrospective and the
sensitivity control.

⛔ **The endpoint is NOT re-chosen here, and that is a decision rather than an omission.** Step 1 discharged
the preregistered obligation to report E2/E3/E4 ([`nrv04-retro-secondaries.json`](./nrv04-retro-secondaries.json))
and **promoted none of them** — its own `_role` records that none is "a verdict, a tier condition or a
substitute primary." Two of the three carry disqualifying caveats measured *before* this panel: **E3** is a
KNOWN WEAK DISCRIMINATOR (co-fold seeds contact in all arms) and **E4** is DESCRIPTIVE ONLY, NEVER A GATE.

Selecting whichever endpoint separated best on the landed panel and then testing on new models would be
**endpoint-shopping** — the retune this program forbids. Keeping E1 costs nothing and is the only choice that
requires no justification from the data being replaced.

**E2/E3/E4 are reported alongside E1 in every result of this panel, including when they disagree with it**
(inherited obligation, NR-V04 prereg §3). Reporting them is required; **gating** on them is forbidden.

---

## 4 · The test — fixed now

- **Statistic:** model-level arm means, primary contrast and the three pairwise contrasts, each stated with
  its direction **before** the data.
- **Test:** exact one-sided permutation over all label assignments of the model means, observed arrangement
  included — `nrv04_retro_gate.exact_permutation_p`, **imported, never re-implemented**.
- **α = 0.05**, one-sided, the same α as both prior panels. A panel judged at a looser α than the control that
  licensed it is not licensed by it.
- **Sign must survive leave-one-model-out** (`nrv04_retro_gate.leave_one_model_out`), as in both prior panels.
- **⬜ TO BE FILLED — direction of each pairwise contrast.** Must be stated from the *reference literature*
  before the freeze, not from any landed NR4A leg. A contrast whose predicted direction is set after seeing
  data is not preregistered.

### 4a · Admissibility, by PROPORTION not by copied integer

⚠ **Do not copy `MAX_FAILED_LEGS_PER_ARM` from either prior panel.** `nrv04_retro_gate` uses **1** for arms of
6 legs; `selcal_panel` deliberately uses **2** for arms of 12, and records that copying the absolute number
across "would silently make this panel's failure tolerance half as generous… a stricter rule arrived at by
accident." What is held constant is **the proportion and the consequence**, not the integer.

- **⬜ TO BE FILLED — technical-failure allowance per arm**, derived as that same proportion of this panel's
  arm size, with the arithmetic shown.
- **⬜ TO BE FILLED — minimum conforming models per arm**, derived so the reference set can still reach α
  after any measured input-fault exclusion (the sensitivity control's rule: enough arrangements that the
  attainable floor stays below α). Co-fold supply risk is real and measured — **1 of 8 models was already
  excluded on an input fault** on a prior panel.

### 4b · Power — DERIVED, and it is the most important section in this document

**σ = 1.0278 Å**, the **model-level** SD, from its one home
[`selectivity-resolution-options.json → which_sigma`](./selectivity-resolution-options.json), derived by
`selectivity_resolution_options.py` from the landed panel's own model means. ⚠ Three σ are in play and
quoting the wrong one is ~3× out; the model-level one is what the test competes against, because prereg §4a
makes the co-fold model the unit of independence.

**Exact power at the shape `NR4A_REPANEL_SHAPE` declares**, from `power_primary` / `power_pairwise`
(permutation Monte-Carlo, n_sims = 2000, so ±~0.01):

| true δ (Å) | primary (3-arm) | pairwise NR4A1-vs-NR4A3 |
|---:|---:|---:|
| 0.50 | 0.230 | 0.198 |
| 0.75 | 0.410 | 0.310 |
| 1.00 | 0.590 | 0.463 |
| 1.25 | 0.757 | 0.615 |
| 1.50 | 0.887 | 0.757 |
| 2.00 | 0.983 | 0.933 |

⚠ **The normal approximation says this shape reaches 80 % power at δ = 1.50 Å. The exact rule delivers
0.757 on the pairwise contrast.** That gap is the measured optimism the prior panel already recorded
(0.64 / 0.67 / 0.72 / 0.74 at n = 3/4/5/6 where the approximation claimed 0.80), reproduced here at this
design. **No power claim in this document may be sourced from the approximation.**

⚠⚠ **EVERY FIGURE ABOVE IS AN UPPER BOUND, AND THE REASON IS IN THE FUNCTION'S OWN DOCSTRING.**
`power_primary` replicates the frozen conjunction — statistic negative, the primary arm below **both**
paralogue means, and p ≤ α — but **it does not apply leave-one-model-out**, because LOMO was outside that
conjunction on the panel it was written for. **§4 of this document REQUIRES LOMO survival.** Adding a
further condition can only lower the probability of passing all of them, so the true power of the criterion
registered here is **at or below** each number in these tables. That direction is stated rather than
estimated: quantifying it would need a LOMO-aware simulator, and an unmeasured correction is not a number.

*(The arithmetic does not depend on which arm is designated primary — the arms are equal-sized, so the
figures hold whichever paralogue the reference literature puts in the numerator. Which one that is remains
⬜ below, and it is a direction to be stated, not a power question.)*

### 4c · ⛔ WHAT THIS DESIGN CANNOT DETECT — and it is the observed effect

Against the separations the landed NR-V04 panel actually showed:

| observed contrast | δ (Å) | exact power at this shape |
|---|---:|---:|
| pairwise NR4A1-vs-NR4A3 | 0.4124 | **0.159** |
| primary | 0.2825 | **0.130** |

**So if the true effect is the size this program has already measured, this design returns a null roughly
five times out of six.** That is not a detail to report afterwards — it decides what a null from step 3 is
allowed to mean, and it must be fixed here, before the run:

> **The null hypothesis this design can reject is "δ ≳ 1.5 Å", not "δ > 0".** A null result licenses
> *"no paralogue separation of ~1.5 Å or larger was detected"* and **nothing weaker**. It does **not**
> license "no separation", "the paralogues are equivalent", or any statement about the ~0.4 Å effect the
> retrospective saw — against which this design is powered at ~0.16 and is therefore uninformative.

⚠ **This is a live design question, not a caveat.** Three responses exist and the choice must be made before
the freeze; it is recorded here so it is made deliberately rather than by inheriting a shape:

1. **Run as shaped, with the restricted null above.** Cheap, honest, and answers only "is there a LARGE
   effect". Recommended, because §1d's argument stands: resolution on an endpoint whose claim ceiling is
   directional concordance is *"a precise number nobody can interpret"*.
2. **Re-shape to a powered design.** `selectivity-resolution-options.md` §1d derives ~77 models/arm for the
   pairwise contrast at 0.4124 Å. Its own §1d argues against buying this, on three grounds that have not
   changed — the system is covalency-confounded, the power calculation is post-hoc on observed effects, and
   the endpoint has no established quantitative link to degradation.
3. **Do not run step 3.** Report the predictions as unvalidated (§4 of the options paper). This becomes the
   right call if the sensitivity control does not PASS, and is *already* defensible if option 1's restricted
   null is judged not worth the spend.

---

## 5 · No interim analysis

The verdict is emitted only when the panel is complete or an arm is definitively short. Peeking at a partial
panel and stopping on a favourable p is the defect NR-V04 prereg §4f exists to prevent, and the sensitivity
control's `PASS_CRITERION["no_interim_analysis"]` restates it. The scorer must **suppress the tier** while
`panel_complete` is false — reporting the evidence but withholding the label — exactly as `selcal` does.

---

## 6 · ⚠ THE ONE OPEN DECISION — re-use of the 16 landed NR-V04 legs

The options paper is explicit: *"any re-use of the 16 landed legs must be declared inside it, in advance."*
This is the declaration, and it is the one place this draft asks rather than decides.

**Draft position: DO NOT re-use them.** Reasoning, so the alternative can be chosen against it rather than by
default:

1. They were produced at a **different design** (model-level n = 3/3/2 after AMENDMENT 4). Pooling them with a
   6-models-per-arm panel makes the reference set heterogeneous in a way the permutation test does not model.
2. They are the data of a panel that returned **DISCORDANT**. Importing them into a fresh test is the shape of
   analysing until something is significant, even when each individual step is defensible.
3. The legs are **cheap** — the retrospective's realised mean was well under the planning rate — so re-use
   buys very little and costs the cleanliness of the whole exercise.

**Against (recorded because it is the real argument):** discarding 16 conforming legs to re-run equivalent
ones is a waste of compute the program is otherwise careful about, and the models are not obviously worse.

⛔ **This must be answered before the freeze.** If the answer is "re-use them", the declaration must name
exactly which legs, at which design, and how the heterogeneity is handled — and that clause must be written
here **before** any new leg runs.

---

## 7 · What each outcome licenses — written before the run

- **A detection, in the predicted direction, surviving LOMO** licenses: *"on the non-covalent arm of this
  chemotype, the ensemble endpoint readout separated NR4A paralogues in the direction the reference
  predicts."* It licenses **nothing** about degradation, efficacy, a therapeutic window, or clinical
  readiness, and — per §1 — **it does not attribute the separation to ternary geometry**, because the system
  is covalency-confounded.
- **A null** is a real negative at a design whose power was fixed in advance, and is reported as one.
- **A wrong-sign result** is a failure reported **with the sign stated**.
- **INDETERMINATE** means nothing was measured. It is not a null and must not be reported as one.

**If step 2 does not PASS, this document is retired UNRUN.** It is not amended, not weakened, and not
re-scoped onto a different pair — the honest outcome is the sentence already written at
[`selectivity-resolution-options.md`](./selectivity-resolution-options.md) §4, and it was written in advance
precisely so it could not later be re-narrated as a method failure.

---

## 8 · Supervision is a precondition, not an afterthought

The NR-V04 lane's own ledger records **`leaked_usd` = $25.83 against $1.57 of compute** — on that lane the
dominant cost was *unattended rental*, not GPU-hours, and **no design choice in this document touches it**.
Before this panel is bought, its lane must re-place bare units and re-arm its own watch without an agent
awake, as the sensitivity control now does. A panel that is cheap to compute and expensive to supervise has
not been costed.
