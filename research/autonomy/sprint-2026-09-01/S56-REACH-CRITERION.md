---
id: DOC-SPRINT-S56-REACH-CRITERION
title: "The $0 act the blocker names, taken: a reactivity-weighted criterion whose apparent rescue is refuted by its own null, and a retirement condition nothing can fail"
level: L3
kind: memo
status: live
purpose: "Record the reach enumeration re-run under a reactivity-weighted accessibility criterion, the decoy null that refutes the corridor opening as attrition rather than selection, the filter variant that would have manufactured a route rescue and was refused, and the finding that the blocker's own retirement condition is unfalsifiable with one positive and no confirmed negatives."
scope: "One route, one blocker, one producer. Geometry only — no reactivity, potency, selectivity, developability, efficacy or clinical claim is made or implied. Says nothing about whether C397 is reactive; reach can refute a route and cannot license one. UNMEASURED = 8, enumerated in the memo."
audience: [autonomous research agents, maintainers]
date: 2026-09-02
last_verified: 2026-09-02
---

# S56 · The reactivity-weighted accessibility criterion, and what re-running the reach enumeration under it does

**Seat:** S56, sprint 2026-09-01. **Cost: $0** — CPU, pure stdlib, no network, no rental, no install.
**Charge:** S54 §2 named `RT-COVALENT-PROBE` the one route an audit of 1,200 claims found that becomes
takeable at $0. This memo verifies that premise, builds the criterion the blocker asks for, runs it, and
reports the answer at its true weight.

⛔ **Scope.** Everything below is GEOMETRY plus STRUCTURAL DETERMINANTS read off static models. No thiol
pKa, intrinsic electrophile reactivity, adduct stability, potency, exposure, selectivity beyond a
three-protein comparison set, efficacy, safety, therapeutic window or clinical statement is computed or
implied. Calling a cysteine a "covalent handle" remains a CATEGORICAL sequence/geometry label in this
repository and nothing here changes that.

---

## 1 · THE PREMISE HELD — the two sentences name one action, and the blocker prices it itself

**The route's next action** — `systems/graph/routes.json`, `RT-COVALENT-PROBE.next`:

> `"best_next_action": "Build a reactivity-weighted accessibility criterion and calibrate it against the`
> `known covalent site, then re-run the reach enumeration under it. Report the result as a rank until the`
> `criterion passes."`, `"cost": "$0"`, `"blocked_on": ["BLK-REACH-CATEGORICAL"]`

**The blocker's retiring action** — `systems/graph/blockers.json`, `BLK-REACH-CATEGORICAL`:

> `"retired_by_action": "Re-run the reach enumeration under a criterion that passes its own positive`
> `control, and report the result as a rank rather than a verdict until one exists. $0."`

★ **Not verbatim identical — S54 called them "the same sentence" and they are the same ACTION in two
wordings.** Both name (i) a re-run of the reach enumeration, (ii) under a criterion that passes its
positive control, (iii) with a rank reported until it does. The blocker's own record prices that act at
`$0`, and its `kind` is `scientific_uncertainty` — not a wet lab, not a dataset, not a decision for
trimcrae. **`next.blocked_on` therefore asserts that a $0 act is blocked by the thing that act retires.**
Premise confirmed.

**The instrument control states**, `systems/graph/instruments.json`:

- `INS-MONOVALENT-REACH.known_answer_control.state`: `"passes"` — *"its BIVALENT half must replicate the
  already-committed bivalent artifact cell-for-cell"*. The harness is validated.
- `V17` (`"The exposure criterion EXPOSED_RSA = 0.25"`) `known_answer_control.state`: `"fails"`, on
  *"NR4A1 C551 — the one NR4A-family covalent site with literature support"*, noted
  `"⛔ KNOWN-DEFECTIVE … What survives is a threshold-free RANK"`.

All three states are as S54 reported them. **The premise is verified against the graph, not inherited.**

---

## 2 · ⛔ THE FIRST REAL FINDING, AND IT CHANGES WHAT THE ACTION IS: THE REACH ENUMERATION NEVER CONSUMED A CRITERION

`grep -c "RSA" research/modalities/nr4a3_monovalent_reach.py` returns **0**. The string `expos`,
`accessib` and `reactiv` occur in that file **only inside disclaimers** (lines 45–46, 497, 510 —
*"No thiol pKa, intrinsic electrophile reactivity … or exposure … is computed or implied"*).

★ **So "re-run the reach enumeration under a criterion" is not re-running an existing parameterisation
with a new constant. The criterion is not currently an input to the enumeration at all.** Every cysteine
of NR4A1, NR4A2 and NR4A3 enters `family_window()` as an equally competent competitor, adjudicated purely
by backbone-atom count (`nr4a3_monovalent_reach.py:206-260`). The action the blocker names requires
BUILDING the coupling, not flipping a flag — which is why nobody had run it and why it stayed $0.

⚠ **This is a correction to how S54 §2 reads, not a refutation of it.** The work is still $0 and still
unblocked; it is larger than "a $0 recalculation once the criterion is defined"
(`RT-COVALENT-PROBE.timing.automation_outlook`) by exactly one integration.

---

## 3 · ⛔⛔ THE TRAP: APPLYING `V17` AS THE COMPETITOR FILTER WOULD HAND THE ROUTE A FREE WIN

The determinants for all 18 family cysteines are already committed in
`research/modalities/nr4a3-thiol-environment.json` (`_generated_utc: 2026-08-28T22:52:44Z`, 18 rows,
`★_part_B_determinants`). Reading `exposed_by_atlas_rule` (`rsa >= 0.25`, i.e. `V17`) off those rows:

| cysteine | RSA | `V17` exposed? | closes corridor cells (committed run) |
|---|---|---|---|
| NR4A3 **C397** (target) | 0.395 | **True** | — |
| NR4A3 C420 | 0.311 | **True** | 0 |
| NR4A1 **C551** (positive control) | 0.165 | False | 6 |
| NR4A1 C465 | 0.138 | False | 0 |
| NR4A2 **C534** | 0.120 | False | 34 (bivalent corridor) |
| NR4A3 C559 | 0.095 | False | 0 |
| NR4A3 C594 | 0.063 | False | 0 |
| NR4A1 C475 | 0.024 | False | 0 |
| NR4A3 C506 | 0.024 | False | 0 |
| NR4A2 C566 | 0.025 | False | 0 |
| NR4A2 **C465** | 0.011 | False | 12 |
| NR4A2 C475 | 0.005 | False | 0 |
| NR4A1 **C505** | 0.000 | False | 12 |
| NR4A1 C534, NR4A1 C566, NR4A2 C505, NR4A3 C496, NR4A3 C536 | 0.000 | False | 0 |

★★ **`V17` admits 2 of 18 cysteines, and both are in NR4A3.** Every cysteine of both paralogues —
including all three corridor closers (`NR4A1 C505`, `NR4A2 C465`, `NR4A1 C551`; committed
`summary.monovalent.corridor.closers_by_count`) — is scored not-exposed. **Filtering competitors by `V17`
would open the family-wide window at C397 in essentially every cell, by declaring the entire paralogue
comparison set unreactive using a cutoff already proven to produce a false negative on the one family
cysteine with literature support.** That is the concrete shape of the harm `V17`'s note warns about, and
it is why the blocker exists rather than why it can be waved away.

⛔ **Recorded here so no later session runs the "obvious" $0 re-run and reports a rescued route.**

---

## 4 · WHAT WOULD MAKE ME REJECT MY OWN CRITERION — WRITTEN BEFORE RUNNING IT

★ **The hard problem, stated plainly: there is exactly ONE positive (NR4A1 C551) and ZERO confirmed
negatives in this comparison set.** With n=1 positive, "passes its own positive control" is satisfiable by
construction — put the admission floor at the control. A criterion tuned until the control clears is not a
criterion, so control recovery ALONE cannot be the test, and the blocker's retiring action as written
would be satisfied by a worthless instrument.

**The criterion (fixed before running, zero parameters fitted to the control).** Score each of the 18
cysteines by the mean of its within-set percentile ranks on determinants whose SIGN was declared in
`nr4a3-thiol-environment.json` on 2026-08-28, before this session, in the field
`higher_value_argues_for_lower_pKa`:

- `rsa` — solvent exposure (higher argues for reactivity)
- `n_hbond_capable_donors_within_4A_of_SG` — thiolate stabilisation (higher)
- `net_formal_charge_within_8A` — electrostatic stabilisation of the thiolate (higher)
- `nearest_cationic_group_A` — declared `higher_value_argues_for_lower_pKa: false`, so nearer is better

**Primary composite `RWA-3`** uses exposure, H-bond donors and net charge — three physically independent
axes. `net_formal_charge_within_8A` and `nearest_cationic_group_A` are the SAME axis, so including both
double-weights electrostatics; `RWA-4` (all four) and `RWA-3S` (`RWA-3` with SG-local burial
`sg_heavy_neighbours_within_6A` substituted for residue `rsa`) are computed as declared sensitivity
variants. Equal weights throughout. **Admission floor = the score of NR4A1 C551**, the weakest site known
to work — a convention, declared as such, NOT a success.

**⛔ The five conditions that make me throw the criterion away, all written before the run:**

- **R1 — non-discrimination.** If the floor set by C551 admits **more than 12 of 18** cysteines, the
  criterion is a rubber stamp and I reject it regardless of what it does downstream.
- **R2 — variant disagreement.** If `RWA-3`, `RWA-4` and `RWA-3S` do not agree on the downstream corridor
  verdict, the criterion is not determined by the data; I report the disagreement and retire nothing.
- **R3 — the suspicious admitted set.** If the admitted set turns out to be *precisely* the complement of
  the corridor closers (`NR4A1 C505`, `NR4A2 C465`, `NR4A1 C551`) and nothing else, I treat that as
  evidence I built the criterion to that end and reject it.
- **R4 — the target is not exempt.** C397's own admission is an OUTCOME, not an assumption. If C397 fails
  its own criterion, the route is refuted on reactivity as well as on geometry and I report that.
- **R5 — a fitted weight.** If any weight, sign or threshold has to be chosen to make C551 clear, the
  criterion is dead and I say so instead of reporting a number.

**⚠ Disclosure of what was NOT blind.** I read the 18-row determinant table (§3) before designing the
composite, so C551's per-determinant ranks (`solvent_exposure` 3, `hbond_donors_to_SG` 9,
`net_positive_charge_8A` 5, `proximity_to_cation` 4, of 18 — `★_internal_control…rank_on_each_determinant`)
were known to me. **Control recovery is therefore NOT a blind test and is not reported as one.** The
genuinely blind quantities, unknown at the moment this section was written, are: (a) how many of 18 the
floor admits, (b) whether C397 clears it, (c) the corridor `n_open` after non-admitted competitors are
dropped, and (d) whether the three variants agree.

---

## 5 · THE INSTRUMENT'S CONTROL PASSES LIVE, NOT ONLY IN THE RECORD

Before changing anything, the module was run on an unmodified checkout into a scratch path
(`nr4a3_monovalent_reach.py --out …/baseline-reach.json`, exit 0):

```
[xcheck] committed_anchor_distances: AGREES
[xcheck] unique_cysteine_partition: AGREES
[xcheck] replicates_the_committed_bivalent_window: AGREES
[xcheck] monovalent_never_exceeds_bivalent: HOLDS
```

★ **The regenerated document is equal to the committed `nr4a3-monovalent-reach.json` in full** — not
merely on the four cross-checked fields, but `a == b` over the whole parsed document. `INS-MONOVALENT-REACH`'s
`known_answer_control.state: "passes"` is therefore a live reading in this session, not an inherited one,
and the harness the re-run rides on is sound.

---

## 6 · THE RE-RUN, AND THE NUMBER THAT LOOKS LIKE A RESCUE

The criterion is wired into `family_window()` at exactly one place — a competitor cysteine the criterion
does not admit is not counted as a competitor (`nr4a3_monovalent_reach.py`, `admissible=` parameter;
`admissible=None` reproduces the unfiltered enumeration and is what every committed number was computed
under, pinned by `test_admissible_none_reproduces_the_unfiltered_enumeration_exactly`).

| variant | determinants | admitted / 18 | target `NR4A3 C397` admitted | monovalent corridor open |
|---|---|---|---|---|
| **`RWA-3`** (primary) | rsa, H-bond donors, net charge 8 Å | **4** | **yes** (2nd of 18) | **16 / 30** |
| `RWA-4` (electrostatics twice) | + nearest cation distance | **2** | **NO** (4th of 18) | 17 / 30 |
| `RWA-3S` (SG-local burial) | SG neighbours, H-bond donors, net charge | **3** | yes (2nd of 18) | 17 / 30 |

**Unfiltered, the same board is 0 / 30** (`summary.monovalent.corridor.n_open`, committed).

`RWA-3` admits `NR4A3 C420`, `NR4A3 C397`, `NR4A1 C465`, `NR4A1 C551`. **R1 does not fire** — 4 of 18 is
highly discriminating, not a rubber stamp. **R3 does not fire** — the admitted set is not the complement
of the closers: it retains the control `NR4A1 C551`, which itself closes 6 of the 30 unfiltered corridor
cells, and drops the other two closers.

★ **So on its face the blocker's $0 re-run reopens a window that the committed geometry says is shut, and
the two cysteines whose removal does it — `NR4A1 C505` (RSA 0.000, `RWA-3` 0.412) and `NR4A2 C465`
(RSA 0.011, `RWA-3` 0.480) — are the two most deeply buried closers on the board.** That is the result a
seat under pressure to produce a live route reports. It is wrong, and §7 is why.

---

## 7 · ⛔⛔ THE OBSERVATION THAT DISCRIMINATES: THE WINDOW REOPENS FROM ATTRITION, NOT FROM SELECTION

Filtering competitors can open a window for two reasons that produce the identical number: because the
cysteines removed were the ones that mattered (**selection**), or because 17 competitors became 3
(**attrition**). §4's conditions do not separate them, so a size-matched decoy null was built —
`rwa_decoy_null()` — which holds the SIZE of the admitted competitor set fixed and redraws its MEMBERS
from every family cysteine.

⚠ **Declared honestly: this null was NOT pre-registered.** It was designed after seeing the 0 → 16 flip,
because CLAUDE.md §4 requires the observation that discriminates rather than an explanation. It is
reported as a post-hoc diagnostic and it is now a permanent guard in the module (`R6`), so no later run can
report a reopened window without it.

**Result — exhaustive over all C(17,3) = 680 three-competitor subsets, 30 monovalent corridor cells:**

| | n_open |
|---|---|
| unfiltered (17 competitors) | **0** |
| `RWA-3` criterion (3 competitors) | **16** |
| size-matched null, **median** | **20** |
| size-matched null, min / max | 0 / 30 |
| fraction of random same-size subsets opening ≥ 16 cells | **65.0 %** (442 / 680) |

★★ **The criterion's board is BELOW the median of its own size-matched null.** A randomly chosen trio of
competitors opens more cells than the reactivity-weighted trio does, two times in three. The reactivity
ranking contributed nothing: the window came from discarding 14 of 17 competitors, and any 14 would have
done as well or better.

⛔ **And it is not a quirk of the primary composite — all three variants fail the same way**
(`reactivity_weighted_rerun.boards.*.decoy_null_monovalent_corridor`, exhaustive):

| variant | competitors retained | observed open | null median | fraction of same-size subsets ≥ observed | `R6` |
|---|---|---|---|---|---|
| `RWA-3` | 3 | 16 | 20.0 | 0.650 | **fires** |
| `RWA-3S` | 2 | 17 | 22.0 | 0.750 | **fires** |
| `RWA-4` | 1 | 17 | 22.0 | 0.750 | **fires** |

**The attrition curve makes the mechanism explicit** (median open cells over subsets of each size, 400
sampled where exhaustive enumeration is too large, seed 20260902):

| competitors retained | 0 | 1 | 2 | **3** | 4 | 6 | 8 | 9 | 12 | 17 |
|---|---|---|---|---|---|---|---|---|---|---|
| median open cells (of 30) | 30 | 30 | 22 | **20** | 15.5 | 12 | 7 | 0 | 0 | **0** |

⛔ **`n_open` is a smooth monotone function of how many competitors you keep.** Any filter that discards
enough of them reopens the window, so "the window opens under criterion X" carries no information about X
unless X beats its size-matched null. **`RWA-3` does not.** `R6` fires.

---

## 8 · WHAT THE FOUR PRE-REGISTERED CONDITIONS DID, VERBATIM

| condition | fired? | the number |
|---|---|---|
| **R1** non-discrimination (> 12 of 18 admitted) | **no** | 4 of 18 |
| **R2** variant disagreement | **YES** | `RWA-4` excludes the target; `RWA-3` and `RWA-3S` admit it |
| **R3** the suspicious admitted set | **no** | the control `NR4A1 C551` is retained and closes 6 cells |
| **R4** the target fails its own criterion | **YES under `RWA-4`** | `C397` 0.669 vs floor 0.699 |
| **R5** a fitted weight | **no** | equal weights, signs read from the 2026-08-28 artifact |
| **R6** attrition not selection *(added post-hoc, §7)* | **YES, on all three variants** | 16 observed vs 20.0 null median (`RWA-3`); 17 vs 22.0 (`RWA-3S`, `RWA-4`) |

★ **R2 and R4 are the same fact seen twice, and the fact is small and fatal.** The ONLY difference between
`RWA-3` and `RWA-4` is whether the electrostatic axis is counted once or twice —
`net_formal_charge_within_8A` and `nearest_cationic_group_A` measure the same thing. `C397` is strong on
accessibility (rank 1 of 18) and H-bond donation (rank 1 of 18) and weak on electrostatics (rank 14 and 12
of 18); `NR4A1 C551` is the reverse (ranks 3, 9, 5, 4). **So whether the route's own target clears a bar
set by the family's one known covalent site is decided entirely by a weighting choice — and with one
positive and no confirmed negatives, nothing in the data constrains that weight.**

⛔ **That is the finding, and it is a statement about calibration, not about C397.** Nothing here says the
cysteine is or is not engageable. It says this comparison set cannot tell.

---

## 9 · ⛔ WHY "PASSES ITS OWN POSITIVE CONTROL" IS A BAR NO CRITERION CAN FAIL

`BLK-REACH-CATEGORICAL.retired_by_action` asks for *"a criterion that passes its own positive control"*.
With exactly one positive (`NR4A1 C551`) and zero confirmed negatives, the admission floor can always be
placed at the control's own score — which is what `rwa_admitted()` does, deliberately and with the fact
stated in its docstring. `test_control_recovery_is_by_construction_for_ANY_scores_so_it_is_not_evidence`
pins it: for **any** score vector whatsoever, the control is admitted.

★★ **A condition that cannot be failed cannot be cleared into evidence.** The blocker's retiring action,
as written, is satisfied by a criterion of no value — and the $0 work it asks for has now been done and
demonstrates exactly that. **The blocker should therefore NOT be retired; it should be restated so its
retirement names something falsifiable**, which requires an external reactivity dataset carrying at least
one confirmed *unreactive* cysteine. That is a networked read, not a local one, and is $0 at CI.

**But `RT-COVALENT-PROBE.next.blocked_on` is still wrong and is now wrong for a second reason.** It
asserted a $0 act was gated by the blocker that act retires; the act has since been taken. Both proposals,
with the two others this seat's evidence supports, are in
[`S56-proposed-reach-criterion.json`](./S56-proposed-reach-criterion.json). ⛔ **This seat did not edit
`systems/graph/*.json`.**

---

## 10 · ⛔ THE TRAP RECORDED FOR THE NEXT SESSION

The obvious way to satisfy `retired_by_action` is to filter the enumeration by the exposure criterion the
repository already has. **Do not.** `V17` (`EXPOSED_RSA = 0.25`) admits **2 of 18** family cysteines and
both are in NR4A3 (§3). Every cysteine of both paralogues — including all three corridor closers — is
scored not-exposed, so the filtered board would open almost everywhere, and the whole of that result would
be produced by a cutoff with a demonstrated false negative on the one family cysteine with literature
support. Proposal `P4` writes this consequence into `V17`'s own record, where it was missing.

---

## 11 · WHAT REMAINS UNMEASURED — **8**

1. **Thiol pKa.** Not computed. No predictor is installed in this sandbox and `C12`'s own register entry
   holds the known-answer set at `candidate_unverified`.
2. **Intrinsic electrophile reactivity.** Not computed anywhere in this repository.
3. **Adduct stability.** Not computed.
4. **Any competitor outside three proteins.** The comparison set is NR4A1, NR4A2, NR4A3 — 18 cysteines.
   Nothing here is proteome-wide and nothing here is a selectivity claim.
5. **A confirmed unreactive cysteine.** Zero negatives. This is the missing quantity that makes the whole
   calibration unfalsifiable, and it is the one an external dataset would supply.
6. **The literature anchor at first hand.** `NR4A1 C551`'s covalent precedent is taken from this
   repository's own records (`V17.known_answer_control.description`, and the determinant artifact's
   `★_internal_control…`). No primary source was re-read in this session.
7. **Determinant dynamics.** One static opened conformer per protein. The paralogue metadynamics ensembles
   carry reach geometry but no determinants, so the criterion could not be re-scored across them.
8. **The site question.** `V3` returned INCONCLUSIVE on site selection and every anchor still comes from
   that pose. Inherited whole and not narrowed here.

---

## 12 · THE ONE-SENTENCE ANSWER

★ **This is a NEGATIVE with a working instrument, not an instrument that cannot answer:** the $0 act
`BLK-REACH-CATEGORICAL` names has been performed on a harness whose control passes live, the apparent
rescue it produces (0 → 16 of 30 corridor cells) is refuted by a size-matched null in which a random
competitor trio does better two times in three, and the reason the act cannot succeed is structural — one
positive and no negatives make "passes its own positive control" a bar nothing can fail. **`RT-COVALENT-PROBE`
gains no support and loses none; what it loses is a $0 next action that was never going to work.**
