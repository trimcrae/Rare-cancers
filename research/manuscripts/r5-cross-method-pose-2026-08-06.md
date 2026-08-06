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
[`pose-second-method.json`](../modalities/pose-second-method.json) (the cross-method run) and
[`r5-cross-method-cavity-attribution.json`](../modalities/r5-cross-method-cavity-attribution.json)
(the cavity attribution). Nothing below is a number typed fresh; each points at the artifact that owns it.

---

## 0 · What was asked, and the short answer

The mandate was [`path-family-synthesis.md`](path-family-synthesis.md) §2 Tier-1 row 2: *"Run a SECOND,
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
and lives in [`pose-second-method.json`](../modalities/pose-second-method.json) →
`shared_configuration_by_arm`; it is not asserted in prose here.

⚠ **What is deliberately NOT independent: the site.** Both engines are pointed at the same centre, and
rDock's search radius is *derived* from the pipeline's own box edge rather than chosen, so the two
searches cover the same volume. That is the point — holding the site fixed is what isolates search and
scoring. It also means this comparison **cannot** answer the site question; that has its own instrument
([`apo-pose-site-in-regime.json`](../modalities/apo-pose-site-in-regime.json)).

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
[`nr4a3-program-map.md`](nr4a3-program-map.md) §5 `R5`, §3.1 `V22` and §10.1 row 4 quote a median of
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

- the version is **pinned** in [`pose-recovery-check.yml`](../../.github/workflows/pose-recovery-check.yml),
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

