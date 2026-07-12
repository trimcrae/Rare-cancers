# NR4A3 ABFE λ-repair — PREREGISTRATION (technical criteria + promotion rules)

**Committed BEFORE the repaired dense runs complete, per the external reviewer (2026-07-11).** This fixes
the stopping rule, the acceptance criteria, the statistics, the promotion terminology, and the audit claim so
none of them is decided post-hoc on a favorable number. Governs the NR4A2 complex-leg dense (16-window)
λ-overlap repair and its use in any denovo_401 promotion decision.

## 0. Why the repair (context)
The standard 12-window complex-NR4A2 leg has one under-overlapped adjacent λ-pair (min MBAR overlap 0.003),
making the NR4A2 selectivity contrast ΔΔG(NR4A3−NR4A2) = −4.98 ± 0.68 (n=3) **provisional**. The dense
16-window schedule adds 4 windows in the soft-core endpoint region to repair that overlap. (A run bug had
frozen the executed window count at 12 while evaluating u at 16 states; fixed 2026-07-11 — `n_windows()` is
now schedule-aware and `reduce_leg` infers K from data and fails closed on mismatch.)

## 1. Stopping rule — r1 is a TECHNICAL pilot, NOT a favorable-outcome gate
- Run r1 (nearest complete: windows 0–11 done, run 12–15). Then **run r2 and r3 REGARDLESS of r1's numerical
  ΔΔG**, provided r1 is *technically* valid (passes §2).
- **Stop/extend only for a TECHNICAL failure:** disconnected overlap network, invalid/corrupt data,
  irrecoverable instability, or failure of one predefined extension (below).
- A large numerical movement in a *technically healthy* r1 is evidence of **sensitivity**, and is informative,
  but **one replicate cannot establish that the original mean was an "overlap artifact."** All three repaired
  replicates must complete before drawing that conclusion. Continuation is **not** conditioned on r1's number.
- **Predefined extension (the only allowed numerical trigger):** if, after the standard sampling, a
  *problematic* state's effective independent samples fall below the §2 floor, extend sampling for that leg
  once (double the iterations of the offending windows) before declaring technical failure.
- **★ COST OVERRIDE (trimcrae, 2026-07-12) — SUPERSEDES the reviewer's "run r2/r3 regardless of r1's number"
  above for the specific case of an UNFAVORABLE r1.** The reviewer's rule exists to avoid outcome-dependent
  selection bias; trimcrae has knowingly accepted that tradeoff on cost grounds. So: **do NOT auto-fan-out to
  r2/r3.** When a *technically-valid* r1 reduces, look at the repaired ΔΔG(NR4A3−NR4A2): if it **suggests
  401 is NOT NR4A3-selective** (the contrast collapses toward/above zero, i.e. the favourable direction is
  lost), **STOP and SURFACE to trimcrae** (reviewer block + phone ping) rather than spend the ~$10–30 on
  r2/r3 to confirm a likely dead end. Preserve honesty: a non-selective r1 is a **reason to surface for a
  decision, NOT a conclusion** that 401 is dead (one replicate can't settle it — the reviewer's caveat stands;
  trimcrae decides whether the r2/r3 spend is worth it). If r1 is favourable, still surface the result +
  recommendation before the r2/r3 spend (expensive-spend rule) rather than firing automatically.

## 2. Technical acceptance criteria for a dense repaired leg (ALL required)
0. **Sampling completeness (added 2026-07-12; environment-independent HARD gate):** every scheduled window
   must have actually REACHED (≥90% of) the target per-window sample count. Target = `meta.json`'s recorded
   `n_iter` (now written by `run_shard`), else the max window count across the leg (a ragged-leg heuristic).
   A leg with any grossly under-sampled window is **technically INVALID regardless of the MBAR criteria, and
   even when pymbar is absent** — this is a pure check so it fails in any environment. *Why this exists:* a
   SageMaker "Completed" status only means the container exited 0; it does NOT prove every window ran to
   `n_iter`, and a session once briefly treated an under-sampled window-15 (1000 of a 2000 target) as a
   finished run. The under-sampled window passed data-integrity (valid samples) and ESS (≥50) and only tripped
   convergence *incidentally* — so completeness is now an explicit, named, first-class FAIL
   (`abfe_repair_gate.crit_sampling_completeness`), not something inferred from a convergence miss. **Process
   corollary:** a leg is never "done"/"valid" on a job status or an assumed completion — only on the gate
   PASSING against the actual S3 per-window counts.
1. **Schedule identity, not just dimensions:** exactly 16 source windows; each sample's u is a 16-vector; the
   per-window (λ_elec, λ_sterics) values AND their ordering match `LAMBDA_*_DENSE` exactly. (Not merely
   "u has 16 entries.")
2. **Data integrity:** all reduced potentials finite; correct T/β and kcal·mol⁻¹ units; samples unique after
   restart/checkpoint dedup (dedup-by-iteration); exact (target, replicate, leg) identity on every file.
3. **Connected overlap network:** the MBAR overlap graph is connected end-to-end. Min adjacent overlap ≥ 0.03
   is a **heuristic warning threshold, not sufficient proof**; additionally **no** adjacent pair may sit near
   0.003 and **no** pair may be effectively disconnected (the repair must have removed the 0.003 bottleneck).
4. **Effective sample size:** ≥ **50** effective independent samples per state after equilibration/
   decorrelation; if a problematic state is below, trigger the single §1 extension.
5. **Convergence:** |ΔG(full trajectory) − ΔG(second half)| ≤ **1.0 kcal/mol**, and consistent within the
   estimated uncertainty; cumulative ΔG(n) must **visibly plateau**, not merely end at a favorable value.
6. **Independent reduction:** for ≥1 repaired replicate, a **separately written** MBAR input-assembly +
   reduction reproduces ΔG to within tolerance (guards the reduction path itself, not just the data).

A leg failing any of 0–3, 5, or 6 is a **technical failure**. A leg failing 4 triggers the one extension,
then re-evaluates. (A leg failing 0 — incomplete sampling — is not a *scientific* failure of the method; it
means the run simply has not finished. Complete the sampling and re-gate before drawing any conclusion.)

## 3. Statistics — report small-n honestly; NO Gaussian "sigma"
With n=3 independent replicates, use **t-statistics on the standard error (2 dof)**, not "σ". Report the raw
replicates, mean, SD, and the small-n 95% t-interval. (For the *standard* run: NR4A1 t=4.06, 95% t-interval
[−9.80, +0.28] — unanimous in direction but **not resolved from zero**; NR4A2 t=12.68, 95% t-interval
[−6.67, −3.29] — **resolved**.) Never translate these into σ.

## 4. Promotion — TWO-TIER (what the repair can and cannot buy)
**Tier that the repair CAN unlock:** `benchmark → computational warhead candidate / priority synthesis
candidate`, permitted ONLY if ALL hold:
- all three repaired NR4A2 replicates pass §2;
- **mean repaired ΔΔG(NR4A3−NR4A2) ≤ −3.0 kcal/mol**;
- the **95% t-interval lies entirely below zero**;
- **no** repaired replicate weaker than **−1.5 kcal/mol**;
- **≥1 predefined sensitivity analysis** (an alternative plausible NR4A3 receptor state OR an independently
  generated pose) **retains the selectivity direction**.

**Tier that is NOT permitted from this evidence:** `denovo_401 → "NR4A3-selective degrader lead."** Reasons:
binary warhead selectivity ≠ degrader selectivity; the adopted strategy makes **ternary** behavior the central
selectivity variable; 401 must still enter the degrader matrix and survive the same ternary/linker/geometry/
anti-target assessment as the chemotype-anchored candidates; without experimental engagement, **"priority
synthesis candidate"** is the defensible ceiling.

## 5. Both anti-targets for an UNQUALIFIED selectivity claim
NR4A2 is the primary gate (harder paralogue), but NR4A1 cannot be ignored. Until NR4A1's uncertainty interval
is entirely below zero, 401 may be described ONLY as an **"NR4A2-sparing computational candidate; NR4A1
selectivity provisional."** An unqualified "selective vs NR4A1 AND NR4A2" statement requires NR4A1 independent
replicates until its 95% t-interval is entirely below zero. (Current NR4A1 is encouraging enough to justify
further work, not enough for the unqualified claim.)

## 6. Absolute ΔG is positive → a blocker for BINDING/LEAD claims, not for a relative result
The positive absolute ΔG_binds (+2.6…+9.5 kcal/mol) do **not** prohibit reporting protocol-matched ΔΔG, but
they **do** prohibit any statement that 401 is predicted to bind favorably or is an affinity-qualified lead.
Language: replace **"offset-cancelling"** with **"a protocol-matched relative comparison expected to reduce
some common-mode errors."** An unknown offset is **not** guaranteed to cancel across paralogues (target-specific
restraint terms, receptor-state/bound-state definitions, protonation, and pose errors can remain; ABFE is
especially sensitive to bound-state/restraint/symmetry/standard-state treatment). A stronger (binding/affinity)
claim requires EITHER experimental engagement from a collaborator OR a calibrated computational control
(measured binder/nonbinder or affinity standards + an independently checked thermodynamic-cycle sign +
correction audit) — and even the latter supports only "computational lead candidate," not an established lead.

## 7. Audit claim — narrowed + strengthened
Supportable statement: **"We found no evidence that the published ABFE table used the inconsistent dense legs;
the fixed reducer exactly reproduces the table from structurally consistent standard-schedule data."** It does
**not** prove "no published value could have been corrupted." To strengthen toward that, add: an immutable
manifest mapping every paper value → S3 object version IDs + SHA-256; commit SHA, container/env digest,
force-field/param versions, full config, seed, λ schedule, checkpoint ancestry; verification the S3 inventory
is exhaustive and objects were not overwritten without versioning; **semantic** checks (λ identity/order,
source-window assignment, target identity, endpoints, sample duplication, schedule metadata — not just
window_count == u_length); an independently implemented reduction of one standard + one dense replicate; and a
direct test that the **production dispatcher** (not only helper functions) launches all schedule-defined windows.

## 8. Cross-tag reduction guard
Dense-complex + standard-solvent reduction is valid ONLY if an automated compatibility check confirms identical:
ligand topology + parameters; solvent-leg object hashes; temperature + thermodynamic endpoints; standard-state
+ restraint conventions; replicate mapping + correction terms. Additionally compute ΔΔG(NR4A3−NR4A2) **directly
from the complex-leg difference + any non-cancelling corrections** and confirm it agrees algebraically with
subtracting the two per-receptor ABFEs.

---
**Decision (reviewer, 2026-07-11):** complete r1 as a technical smoke; then complete r2/r3 whenever r1 is
technically valid; use the result to decide whether 401 enters the degrader matrix as a *computational warhead
candidate*. Do **not** promote it to "lead" from selectivity-only ABFE; do **not** claim broad NR4A3 paralogue
selectivity while NR4A1 remains statistically unresolved.

## 9. OUTCOME of r1 + amendment rules (recorded 2026-07-12)
**r1 result — TECHNICAL FAILURE (accepted; not to be rescued).** The dense-16-window complex-NR4A2 pilot (tag
`nr4a3-abfe-nr4a2rep-r1`) was carried to completion (all 16 windows at 2000 iters, after correcting an
endpoint window-15 that had stalled at 1000 while a job reported `Completed`) and re-gated. It **passed**
completeness (§2.0), schedule identity (§2.1), data integrity (§2.2), connected overlap (§2.3; min adjacent
0.085), ESS (§2.4; all states ≥ 50) and the plateau sub-check, but **FAILED the temporal-stability criterion
(§2.5): |ΔG(full) − ΔG(second half)| = 1.147 kcal/mol > the pre-registered 1.0 limit** (ΔG_full 21.85,
ΔG_second-half 20.71; completing window 15 improved it 1.36 → 1.147). Per §2 this is a **technical failure**.
**Reviewer decision (2026-07-12): accept the failure; do NOT run a rescue extension.** Rationale: the §1
sanctioned extension is **ESS-triggered only** and expressly excludes convergence-triggered extensions; a
convergence-triggered extension here is **outcome-contingent optional sampling** (even as a single look), which
the pre-registration forbids. Closeness to the threshold does not change the gate outcome.

**Binding constraints going forward (do not violate):**
1. r1 is recorded as a **technical-gate failure** on §2.5; the r2/r3 error-bar replicates are **NOT** unlocked.
2. **No additional sampling may retroactively pass r1.** A later 4000-iteration result must not (a) change r1
   FAIL→PASS, (b) unlock r2/r3 under this pre-registration, (c) be described as "the pre-registered pilot
   result", or (d) support a confirmatory selectivity claim.
3. **Do not relax or reinterpret the gate:** no plateau-only acceptance, no rounding 1.147 → 1.0, no
   "negligible excess". The conjunctive §2.5 (half-difference AND plateau) requirement stands; the passing
   plateau and the 1.36 → 1.147 improvement are diagnostics, not offsets.
4. **Biological reading stays narrow:** this does NOT show `denovo_401` lacks NR4A2 selectivity — it shows this
   NR4A2 ABFE leg, under the pre-registered protocol, was not technically stable enough to yield a gated
   selectivity estimate. The full/half ΔG are QC diagnostics only.
5. **No headline ΔΔG** is computed or promoted from this failed leg (the cross-tag reduce was NOT run).
6. **Preserved provenance:** the previously-incomplete state, the completed 2000-iteration state, job/trajectory
   provenance, target `n_iter` in `meta.json`, gate output (`run_id` 29190987163) and software commit hashes.
   Commit `3f6e3c9` (sampling-completeness guard + `meta.json` `n_iter`) was a **procedural-integrity
   improvement that did NOT alter the convergence threshold.**

**Optional exploratory extension (only if separately declared).** A 4000-iteration run may be conducted ONLY as
a **separately declared exploratory method diagnostic**, not a continuation under this gate. Before launch, a
timestamped amendment must specify: exactly 4000 total iterations for every window; **no** examination or
decisions at intermediate iteration counts; unchanged estimator, equilibration treatment, inclusion rules,
overlap calculation, convergence formula, plateau definition and software version; whether trajectories are
appended or restarted; that **r1 remains FAILED regardless of the exploratory outcome**; and that a favourable
result may only motivate a **newly pre-registered** ABFE protocol or fresh pilot, subject to the cost override.
Doubling to 4000 is a clean operational choice justified by simplicity + diagnostic value — **not** a
prospective power/convergence calculation — and the same 1.0 threshold alone does not make it non-p-hacked,
because the decision to extend was triggered by the observed failure.

**Integrity-clean reporting language (use this phrasing):** *"The repaired NR4A2 complex ABFE pilot was
complete and passed the pre-specified schedule, data-integrity, overlap, ESS and plateau checks, but it did not
satisfy the pre-registered temporal-stability criterion: the full-versus-second-half difference was 1.147
kcal/mol against a 1.0 kcal/mol limit. The pilot was therefore classified as a technical failure, and no gated
NR4A2 selectivity ΔΔG was reported. This finding concerns the reliability of this ABFE protocol for the NR4A2
leg and does not establish that denovo_401 is nonselective."* Prefer this to "did not converge," which can
sound like an absolute physical conclusion rather than failure of a particular finite-sampling diagnostic.
