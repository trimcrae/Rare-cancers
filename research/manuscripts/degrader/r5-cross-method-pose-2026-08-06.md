---
id: DOC-R5-CROSS-METHOD-POSE-2026-08-06
title: R5 — the second, independent pose method, reproduced; and which cavity each method chose (2026-08-06)
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: Records the independent reproduction of the scoring-independent second pose method, the root
  cause of the artifact that had gone empty beneath it, and the one question neither existing artifact
  could answer — which of R3's two split cavities each method actually picked.
scope: The `denovo_401`-in-NR4A3 pose only. No claim about binding, affinity, reactivity, selectivity,
  efficacy or safety is made or implied anywhere in this document.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-06
last_verified: 2026-08-06
---
# `R5` — the second pose method, reproduced; and which cavity each method chose

**$0 throughout.** Free CPU in the dev sandbox and free CI. **No GPU, no rental, no Vast, no GCP,
nothing to tear down.** ⛔ No threshold, band, box or criterion was defined, moved or re-tuned here.

**Machine-readable numbers, and their only homes:**
[`pose-second-method.json`](../../modalities/pose-second-method.json) (the cross-method run) and
[`r5-cross-method-cavity-attribution.json`](../../modalities/r5-cross-method-cavity-attribution.json)
(the cavity attribution). Nothing below is a number typed fresh; each points at the artifact that owns it.

---

## 0 · What was asked, and the short answer

The mandate was [`path-family-synthesis.md`](../program/path-family-synthesis.md) §2 Tier-1 row 2: *"Run a SECOND,
INDEPENDENT pose method on the same ligand in the same receptor."* Its falsifier was stated in advance:

> *independent methods disagree as widely as the six existing poses ⇒ "the predicted pose" is not an
> object this program is entitled to, and every pose-conditional row above must be restated as
> marginalised-over-poses.*

⛔ **THE FALSIFIER FIRED.** Two engines that share no scoring term, no search algorithm, no atom typing
and no source code disagree on every one of the six receptors, at a median in-frame RMSD comparable to
this molecule's own measured cost of being turned end-for-end in place. **"The predicted pose" does not
survive as an object.** Every pose-conditional claim must be stated as marginalised over poses.

⭑ **And three things were found on the way that were not part of the mandate**, each of which changes
what the record says rather than what the science says:

1. **The second method had already run — on 2026-08-03 — and its artifact had gone empty underneath the
   roadmap that quotes it.** The roadmap's `R5`, `V22` and §10.1 row 4 cells carry numbers that the
   committed artifact no longer contained, and point at a field (`verdict.what_would_resolve_R5`) that
   was not in it. Root-caused, reproduced, and both the cause and the shape are now closed — §2.
2. **The reproduction is exact.** Re-running from the committed inputs reproduces the 2026-08-03 poses
   **coordinate-identical, pose for pose**, so the roadmap's figures are re-derived rather than recalled.
3. **The "orientation, not location" reading was an assumption, and it is now a measurement.** R3 had
   measured this site **split across two real cavities** whose centroids are 9.853 Å apart — and **both
   lie inside the 12.0 Å sphere both engines search**, so a small centroid separation could not by
   itself establish that two poses are in the same pocket. It is now measured directly, on lining
   contacts — §4.

---

## 1 · What was run, and why it is independent where it counts

| | first method (`V3`, the pipeline's own) | second method (`V22`) |
|---|---|---|
| engine | **smina** (an AutoDock Vina fork), via `nr4a3_warhead.dock_into` | **rDock** — `rbcavity` + `rbdock`, stock three-stage protocol |
| search | iterated-local-search Monte Carlo + BFGS, inside an axis-aligned box | genetic algorithm → Monte Carlo → Simplex, restrained to a mapped **cavity** |
| scoring | the Vina empirical function — gauss1/gauss2/repulsion/hydrophobic + non-directional H-bond | piecewise vdW + **directional** polar over annotated donor/acceptor/ionic types + aromatic + weighted-SASA desolvation |
| atom typing | Vina's X-Score-derived typing | Sybyl types + Gasteiger charges, assigned by Open Babel |

**They share no source code, no scoring term, no search algorithm and no atom typing.** What they
deliberately do share is the receptor coordinates, the ligand, the evaluation frame and the grading
criterion — because a comparison that did not share those would be comparing two different questions.
⛔ **Sharing a THRESHOLD is comparability; sharing a MEASUREMENT CHAIN is pseudo-independence.** The
per-arm declaration of which `C*` configuration items are shared is computed from each arm's definition
and lives in [`pose-second-method.json`](../../modalities/pose-second-method.json) →
`shared_configuration_by_arm`; it is not asserted in prose here.

⚠ **What is deliberately NOT independent: the site.** Both engines are pointed at the same centre, and
rDock's search radius is *derived* from the pipeline's own box edge rather than chosen, so the two
searches cover the same volume. That is the point — holding the site fixed is what isolates search and
scoring. It also means this comparison **cannot** answer the site question; that has its own instrument
([`apo-pose-site-in-regime.json`](../../modalities/apo-pose-site-in-regime.json)).

⚠ **What is shared and cannot be removed: the receptor conformer.** Both methods place a ligand into a
fixed receptor, so an error carried by the receptor survives both. Agreement would not have proven
correctness, and disagreement does not prove either engine wrong.

**The ligand handed to rDock is a fresh ETKDGv3 conformer built from the census SMILES — never the smina
pose.** Seeding the second method inside the answer it is checking would bias the comparison toward
agreement.

---

## 2 · ⛔ The artifact beneath `R5` had gone empty — root cause, with the evidence

**The observation.** `pose-second-method.json` on this branch read `outcome: UNRUN`,
`cross_method_evidence: "STILL NONE"`, `part_a_n_systems: 0`, and had no
`verdict.what_would_resolve_R5` — while
[`nr4a3-program-map.md`](../nr4a3-program-map.md) §5 `R5`, §3.1 `V22` and §10.1 row 4 quote a median of
6.696 Å over six systems and link to that exact field. Meanwhile six rDock pose files sat committed
beside it under `_pose_second_method_poses/`, holding **50 real rDock poses each**, with full
`SCORE.INTER.*` blocks — output no failed run can produce.

**Competing hypotheses.** (a) the poses are stale leftovers and no second-method run ever succeeded;
(b) a run succeeded and a later run overwrote its artifact.

**The discriminating observation.** The poses' own `Rbt.Executable` records **rbdock v25.07-alpha**; the
artifact's `tooling.rdock_version` records **2013.1**, with `RBT_ROOT: null` and
`_provenance.github_run_id: 30826469202`. Different builds ⇒ different runs ⇒ **(b)**.

**The cause, measured rather than inferred.** Installing both packages side by side:

| conda spec | resolves to | ships its protocol at | `rdock_tools()` finds it? |
|---|---|---|---|
| `rdock` (unpinned) | `2013.1` | `share/rdock-2013.1-1/data/scripts/dock.prm` | ⛔ **no** — the probe is `share/rDock` |
| `rdock=24.04` | `24.04.204_legacy` (binary self-reports v25.07-alpha) | `share/rDock/data/scripts/dock.prm` | ✅ yes |

So `RBT_ROOT` resolved to `None`, `_stage_dock_prm` found no protocol file, Part A returned UNRUN with
zero systems — **and the workflow reported `success`.** ⛔ **AND AN UNRUN HALF WAS THEN WRITTEN OVER A
MEASURED ONE.** The module already had a guard for a half that was *absent* (`MODE=panel` builds a doc
with no `part_a`); it had none for a half that was *present and empty*. **A guard keyed on absence
cannot see a failure that arrives fully populated** — the same shape CLAUDE.md §4(b) records, in a new
costume.

**Both halves closed:**

- the version is **pinned** in [`pose-recovery-check.yml`](../../../.github/workflows/pose-recovery-check.yml),
  and the job now **fails at install time** if `share/rDock/data/scripts/dock.prm` is not there, rather
  than 20 minutes later as a silent UNRUN. ⚠ The pin is deliberately not paired with a widened
  `share/rdock*` probe: the two packages ship **different stock protocols**, and silently docking under
  whichever one the solver supplied is worse than an honest refusal.
- `pose_second_method._carry_forward` now **refuses to let an unrun half overwrite a measured one**, and
  records the failed attempt in place under `_superseded_attempt` — because a re-run that quietly
  reverted to the old numbers with no trace would be its own fail-quiet defect. Held by
  `tests/test_pose_second_method.py::test_an_unrun_half_does_not_overwrite_a_measured_half`, with a
  companion test asserting the guard has **not** become a freeze.

⚠ **The measurement of "measured" deliberately ignores `_status`.** An UNRUN half is a fully populated
dict carrying every declaration, criterion and note; a status string is exactly the thing a default can
fill in. What is counted is a **row with a number in it**.

---

## 3 · The reproduction, and the cross-method result

**Reproduced exactly.** Re-running the module from the committed inputs against the pinned engine, at
the module's own fixed seed, reproduces the 2026-08-03 pose files **coordinate-identical across all 50
poses** on the first system checked (scores and coordinates both). The roadmap's `V22` figures are
therefore re-derived, not recalled.

⚠ **One process defect surfaced and is worth stating plainly:** the 2026-08-03 run that produced those
poses ran in a **dev-sandbox scratch prefix**, not in CI — its `Rbt.Parameter_File` records a scratchpad
path. The CI lane for this instrument had, at that point, never succeeded. That is why the numbers lived
only in the roadmap's prose.


**The result, in each receptor's own frame — no superposition, nothing to fudge.** All six systems, all
numbers from [`pose-second-method.json`](../../modalities/pose-second-method.json) → `part_a`:

| receptor | receptor provenance | inter-method RMSD (Å) | `C14` band | centroid separation (Å) | internal conformer RMSD (Å) |
|---|---|---|---|---|---|
| `dock/metad-opened/v2` | metadynamics-opened AF2 | **3.147** | PARTIAL | 1.685 | 1.422 |
| `dock/metad-opened/v2-statematch` | metadynamics-opened AF2 | **6.501** | NOT RECOVERED | 1.370 | 2.128 |
| `dock/8XTT-model2` | experimental apo NMR | **9.816** | NOT RECOVERED | 7.500 | 1.628 |
| `dock/8XTT-model8` | experimental apo NMR | **6.787** | NOT RECOVERED | 1.116 | 1.355 |
| `dock/8XTT-model20` | experimental apo NMR | **7.231** | NOT RECOVERED | 2.457 | 1.367 |
| `dock/8XTT-model6` | experimental apo NMR | **6.605** | NOT RECOVERED | 6.416 | 0.898 |
| **spread (n = 6)** | | **3.147 – 9.816, median 6.696** | **0 RECOVERED · 1 PARTIAL · 5 NOT RECOVERED** | median 2.071 | median 1.394 |

⭑ **Read those against the scales that make an RMSD interpretable**, all measured on this molecule and
recomputed at run time rather than quoted:

- the molecule is **10.4 Å** long;
- turning it **end-for-end in place** costs **6.84 Å**;
- a **uniformly random reorientation** in place averages **5.11 Å** (n = 200).

⛔ **The median inter-method disagreement, 6.696 Å, is ~98 % of the end-for-end flip and 1.31× the random
reorientation.** Not one of the six pairs reaches `C14`'s 2.0 Å RECOVERED line; five of six do not reach
the 4.0 Å PARTIAL line either.

**The conformer is not the explanation.** Median internal-conformer RMSD is **1.394 Å** against a
6.696 Å in-frame RMSD — both engines find a similar molecular shape and put it in differently.

**And the second method does not converge across receptor conformers either.** Measured with the same
Pocket-5 Cα superposition and the same symmetry-corrected kernel the first method's spread uses:
**0 of 15 pairs** inside 2.0 Å, **0 of 15** inside 4.0 Å, range **4.453 – 12.845 Å**, median **7.385 Å**
(`part_a.within_second_method_spread`). ⇒ **the non-convergence is a property of the SYSTEM, not of one
scoring function** — which is precisely the attribution
[`pose-convergence-401.json`](../../modalities/pose-convergence-401.json) said it could not make.

---

## 4 · ⭑ Which cavity did each method actually choose?

This is the question neither existing artifact could answer, and it is the one R3 made unavoidable.

**Why it had to be asked.** `pose-second-method.json` reads its own result as *"same location, different
orientation"* — the median centroid separation, 2.071 Å, is small beside a 6.696 Å RMSD. **That reading
presumes one pocket.** [`r3-site-choice-audit.json`](../../modalities/r3-site-choice-audit.json) measured
**two**: the prespecified site is split across two accepted cavities sharing 4 residues, pairwise
Jaccard **0.21**, centroids **9.853 Å** apart — *further than the frozen gate's own 8.0 Å ceiling*.
Pocket 1 is the helix-3 face; pocket 2 is the helix-11/12 face. **Both lie inside the 12.0 Å sphere both
engines search** (their centroids sit 3.478 Å and 7.562 Å from the reference centroid), so neither
engine was ever asked to choose, and a ~2 Å centroid shift cannot by itself establish a shared pocket.

**How it is measured.** On **discriminating lining contacts only** — residues that line exactly one
cavity. The 4 residues lining both are dropped, because counting them would let the overlap between the
two cavities decide which cavity a pose is in. The contact cutoff and kernel are the pipeline's own
(`pose_convergence_401.contact_a` / `.contacts`), and the cavity definitions are read out of the R3
audit rather than typed. A tie, or no discriminating contact, is **AMBIGUOUS and is never broken**.

| receptor | first method (smina) | second method (rDock) | same cavity? |
|---|---|---|---|
| `dock/metad-opened/v2` | **AMBIGUOUS** (4 – 4) | pocket 1 (margin 1) | not gradeable |
| `dock/metad-opened/v2-statematch` | pocket **2** (margin 3) | pocket **2** (margin 1) | ✅ yes |
| `dock/8XTT-model2` | pocket **2** (margin 4) | pocket **1** (margin 1) | ⛔ **no** |
| `dock/8XTT-model8` | pocket **2** (margin 4) | pocket **2** (margin 2) | ✅ yes |
| `dock/8XTT-model20` | pocket **2** (margin 3) | pocket **2** (margin 6) | ✅ yes |
| `dock/8XTT-model6` | pocket **2** (margin 1) | pocket **2** (margin 1) | ✅ yes |

**Two readings, and the second is the bigger one.**

1. **The orientation reading mostly survives, but not universally: 4 of 5 gradeable systems are in the
   same cavity, 1 is not.** The one that is not — `8XTT-model2` — is also the pair with the largest RMSD
   (9.816 Å) and the largest centroid separation (7.500 Å), so it is internally consistent rather than
   anomalous. ⚠ **The cavity call is therefore receptor-conformer dependent**, and a blanket
   "orientation, not location" across the census overstates it.
2. ⭑ **THE POSE THIS PROGRAM HOLDS IS NOT IN THE CAVITY THE FROZEN SITE RULE SCORED.** The first method
   puts `denovo_401` in **pocket 2 on 5 of 6 receptors** (the sixth is a 4–4 tie); the frozen
   `pocket_tracking.match_pocket` ordering selected **pocket 1** as the site. The R3 audit records that
   pocket 1 scores druggability **0.259** and returns `GATE_A_FAIL_BELOW_DSTAR`, while pocket 2 scores
   **0.667** and would return `GATE_A_PASS`. ⛔ **These are two different questions being answered about
   two different cavities, and nothing until now put them side by side.**

⚠ **Honest limits on this section, stated at full strength.** The margins are thin — six of the eleven
calls rest on a margin of 1 or 2 discriminating contacts — and a contact count is a coarse instrument.
A cavity call is a **geometry** statement: it makes no pose correct, and **nothing here says anything
binds either cavity**; `R4` is untouched and still needs a bench. And this measures which cavity the
poses *are in*, never which cavity is *the site* — that is `C2`'s frozen rule, which this work does not
touch, re-tune, or ask to be re-tuned.

---

## 5 · So: is *"the predicted pose"* an object this program is entitled to?

⛔ **NO. `R5` is DEAD as a source of a singular pose, and it is now dead for a measured reason.**

The pre-registered falsifier asked whether independent methods disagree *as widely as the six existing
poses*. They do:

| | median pairwise RMSD | pairs within 2.0 Å |
|---|---|---|
| first method, across six receptor conformers | 7.006 Å ([`pose-convergence-401.json`](../../modalities/pose-convergence-401.json)) | 1 of 15 |
| second method, across the same six | 7.385 Å | 0 of 15 |
| **between the two methods, in the same frame** | **6.696 Å** | **0 of 6** |

Three independent ways of asking, one answer. **⇒ Every pose-conditional claim must be stated as
marginalised over poses, never as "the predicted pose."**

⛔ **AND THE SYMMETRIC HONESTY, WHICH MATTERS AS MUCH:** this does **not** show the pose is wrong, that
either engine failed, or that nothing occupies this site. Both methods are handed the same receptor
conformer and could share its error; a convergent answer would have shown only convergence. What has
been removed is the *entitlement to singularity*, not any measured quantity.

**What `R5` is now blocked on** is listed with costs in
[`pose-second-method.json`](../../modalities/pose-second-method.json) → `verdict.what_would_resolve_R5`.
⚠ The cheapest item is **$0 and is a SOURCING question, not a compute one**: a known answer *in regime*
with a real apo→holo rearrangement. The panel's own numbers say why it is not answered yet —
**0 gradeable pairs** today, against **4** systems whose site does rearrange (site Cα RMSD median
3.011 Å, max 6.460 Å).

---

## 6 · What was NOT done, and what it would cost

**The optional GPU half of the mandate — a co-fold — was not authorized and was not run.** It is worth
stating what it would and would not add, because the evidence to judge that already exists at $0:

- A co-fold is genuinely a **third axis**: it predicts the complex rather than placing a ligand into a
  fixed receptor, so it fails differently from *both* docking searches and does not inherit the shared
  receptor conformer.
- ⛔ **But this program already ran one, and it reports itself as being in its unreliable regime on this
  exact system.** [`nr4a3-binary-cofold-result.json`](../../modalities/nr4a3-binary-cofold-result.json)
  records NR4A3 `protein_ligand_pair_iptm` **0.233** against a CRBN+lenalidomide control at **0.778**,
  with a confident protein fold (`protein_chain_ptm` 0.909) and an unconfident ligand placement. Its own
  honest interpretation names the reason: no ligand-bound NR4A structures exist in the training data.
- ⚠ **And its coordinates were never committed**, which is why
  [`pose-convergence-401.json`](../../modalities/pose-convergence-401.json) lists it under `known_absent`
  and could not include it. **The $0 half of that item is recovering coordinates from the run that
  already happened, if any survive** — that is worth doing before any new spend.

⇒ **Read: a fresh GPU co-fold would most likely return a third non-attributable placement at low
confidence, which changes no verdict.** The decision-relevant spend is the **$0 sourcing** item above,
not a co-fold.

---

## 7 · Roadmap edits — DESCRIBED, NEVER APPLIED

Three edits are required and **none was applied.** They are generated, with each `current_text` read out
of the live map at run time, in
[`r5-cross-method-cavity-attribution.json`](../../modalities/r5-cross-method-cavity-attribution.json) →
`map_edits_required`; all three anchors resolve uniquely (`status: ALL APPLICABLE`). They target §5 row
`R5`, §10.1 row 4 and §3.1 row `V22`. ⛔ `nr4a3-program-map.md` is trimcrae's; a session that rewrites
the plan to match its own result is the outcome-selection defect this repo keeps guarding against.

⚠ **`pose-convergence-401.json` is a landed record and was NOT edited**, so its
`cross_method_evidence: NONE` still reads as written. That statement was true of the census it measured
and is now superseded by this work; it is corrected by pointing at it, not by rewriting it.
The same applies to [`path-family-synthesis.md`](../program/path-family-synthesis.md) §2 row 2, whose mandate this
document discharges.

---

## 8 · How much weight the median can carry — stated plainly

**n = 6, and every one of the six is a real measurement.** The median is **6.696 Å** over six systems,
and its stability is not a matter of opinion here: **the whole distribution reproduces the 2026-08-03
run figure for figure** — same range (3.147 – 9.816 Å), same median, same centroid median (2.071 Å),
same internal-conformer median (1.394 Å), same bands (0 / 1 / 5). ⚠ *Superseded, retained: an interim
median of **4.824 Å** over **2** systems, reported mid-run. That was not a smaller sample of the same
thing — it was a run in which `biopython` was absent, so all four 8XTT receptors returned the named
refusal `8XTT alignment failed: ModuleNotFoundError` before any docking. **An absent reading is not a
reading of absence**; the two metadynamics systems that did run are the two most similar receptors in
the census, and reading their median as the census median would have understated the disagreement by
1.9 Å.*

⛔ **But the number that bounds what any of this licenses is a different one: the known-answer panel has
`n_gradeable: 0`.** Twelve apo→holo pairs were attempted and **none** produced a gradeable result — two
excluded by the panel's own pre-registered rule `R2b`, ten with no ceiling computed at all, because the
panel arm needs a structure fetch this pass did not have. ⇒ **Neither engine has been graded against a
crystallographic answer in this regime.** So the honest reading of 6.696 Å is:

- ✅ it supports **"the two methods disagree, and the pose is not method-independent"** — that is a
  statement about the two methods, and six systems measured three ways all say it;
- ⛔ it does **not** support **"and here is which one is right"**, and no amount of extra receptor
  conformers would make it, because the missing thing is a **known answer**, not more samples.

⚠ **And the panel's own numbers say why that gap is not merely bookkeeping.** Four of the six systems
whose site rearrangement could be measured show a **large** apo→holo rearrangement (site Cα RMSD median
**3.011 Å**, max **6.460 Å**). A panel of near-rigid re-docks could not answer whether either engine
survives induced fit even if it were gradeable — which is exactly why
`verdict.what_would_resolve_R5`'s cheapest item is a **sourcing** question at **$0**, not a compute one.

⚠ **One provenance defect found in the same pass and closed.** `_carry_forward` stamped a carried half
with the *previous run's* provenance — correct on the first carry, wrong on every one after, because the
previous run may itself have been a carrier. Two single-mode re-runs were enough to make a half produced
in CI read as `where: local reproduction`. An already-carried half now keeps its **original** producer
and counts the hops (`n_carries`, `last_carried_by`); held by
`tests/test_pose_second_method.py::test_a_twice_carried_half_still_names_the_run_that_measured_it`.
⚠ **The `part_b` block in the current artifact was carried twice before that fix**, so its
`_carried_forward.produced_by` names the carrying run rather than the producing one. It is left as it
stands rather than hand-edited — an artifact repaired by hand is an artifact whose provenance is a
claim — and the next `MODE=panel` run will replace it with a measured half.
