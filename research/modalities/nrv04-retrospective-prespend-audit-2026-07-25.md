# NR-V04 retrospective (RUNG 4) — $0 pre-spend audit before any leg is paid for (2026-07-25)

**Question put to this lane.** The sibling covalent feasibility panel was found today to be wrong in **four**
independent ways, and they share a driver with the retrospective, which is built, preregistered and
**unlaunched**. Does the retrospective inherit any of them? Does its own preregistration carry the
zero-discriminating-power defect AMENDMENT 1 found? Is its design still coherent after AMENDMENT 2? And what
does it actually cost on the corrected basis?

**Answer.** It inherits **one of the four, decisively** (the covalent R2 arm cannot be built at all), is
**clean on the other three, verified from the artifacts themselves** — and it carries a **fifth defect nobody
was looking for, which alone would have wasted the entire spend**: the collector reads leg-JSON keys the driver
does not write, so a panel of 24 flawless legs returns **INDETERMINATE**. Two frozen criteria are degenerate in
AMENDMENT 1's exact sense. **Total spend: $0. Nothing was launched.**

| # | finding | evidence |
|---|---|---|
| 1 | **The retrospective could not have returned a verdict.** `retro_collect` reads `d["R1"]`/`d["R2"]`; the driver writes `R1_interface`/`R2_recruitment`/`R3_lys`. Every `e1_plateau_A` → None → every leg `technical_failure` → every arm `underpowered` → **INDETERMINATE** | controlled reproduction: 24 driver-shaped legs through the real `retro_collect` via a stubbed S3 → `tier: INDETERMINATE`; and **19/19 real leg JSONs in the bucket carry `R1_interface`, 0/19 carry `R1`** |
| 2 | **The covalent R2 arm (6 of 24 legs) cannot be built — and while it stays in the frozen panel it BLOCKS the R1 verdict.** At C551 its three models sit at **34.42 / 29.87 / 39.11 Å** against the 8.0 Å A1 limit, so `build_system` raises *before* any leg JSON is written; those 6 units are permanently missing, `panel_complete` is permanently False, and prereg §4f suppresses the contrast forever | `nrv04-retro-prespend-audit.json` → `covalent_arm_admissibility`; plus a reproduction feeding the real collector 18 perfect R1 legs → `panel_complete: false, verdict: null` |
| 3 | **Chain identity is CLEAN on all 9 co-fold models** — including the 6 `nr4a2`/`nr4a3` models that no prior audit had ever measured, and that feed 12 of the 18 primary legs | census `A=254 / E=213 (VHL) / F=118 (**Elongin B**) / G=112 (EloC)`, no contaminant, target chain identified = A, on every model |
| 4 | **The R1 arms are NOT matched in ligand placement, and the mismatch runs against the hypothesis.** Warhead↔target contacts at t=0: NR4A1 **47 mean**, NR4A2 **106**, NR4A3 **73**; warhead↔E3: NR4A1 **33**, paralogues **12–14**. `nr4a2/m1` starts with a **1.05 Å** heavy-atom overlap | audit `warhead.contacts_*`, all 9 models |
| 5 | **The extension rule can never fire in the case it was written for.** On the 84-point lattice every attainable p in its window is ≤ α, i.e. already CONCORDANT; the smallest attainable p above α (0.0595) is outside it | exhaustive enumeration, `nrv04-retro-criteria-audit.json` |
| 6 | **The leave-one-model-out clause is inert** — 228,543 configurations reached p ≤ α with the correct ordering; **zero** then failed LOMO | adversarial search, same file |
| 7 | **The primary test's minimum detectable effect is ~1.5–2.0 Å, unregistered.** Measured leg-to-leg SD **0.855 Å** (6 committed same-model groups). Power at a true 1.0 Å paralogue separation: **43–65 %** | Monte-Carlo through the frozen decision rule; false-positive rate at δ=0 is 0.048, so the test is valid, just blunt |

---

## 1. The defect that would have wasted the whole run

`nrv04_covalent_md.run_leg` writes its readouts as

```python
"n_frames": ..., "R1_interface": r1, "R2_recruitment": r2, "R3_lys": r3
```

`nrv04_vast_launch.retro_collect` mapped them as

```python
"e1_plateau_A": ((d.get("R1") or {}).get("plateau_A")),
"technical_failure": bool(d.get("blew_up")) or ((d.get("R1") or {}).get("plateau_A") is None),
```

**Reproduced, not inferred.** The driver's key list was read out of its own source by AST (so nothing is
transcribed), 24 driver-shaped leg JSONs were served to the *real* `retro_collect` through a stubbed S3, and
the frozen gate was applied to what came out:

```
legs:  e1_plateau_A=None ... technical_failure=True   (all 24)
verdict: {"tier": "INDETERMINATE",
          "technical_failures": {retro_noncov_nr4a1: 6, ...nr4a2: 6, ...nr4a3: 6, retro_cov_nr4a1: 6},
          "underpowered_arms": [all four]}
```

**Independently corroborated on real artifacts:** of the 19 leg JSONs in the bucket, **19 carry
`R1_interface` and 0 carry `R1`**. Two other consumers in-repo (`nrv04_result_forensics.py`,
`nrv04_cofold_audit.py`) read `R1_interface` and produce real numbers from those same objects.

**Why it survived.** `tests/test_nrv04_retro.py` feeds the gate `e1_plateau_A` directly; nothing crossed the
driver→collector boundary. And the failure mode is *silent* — post-hoc it reads as "every leg technically
failed", i.e. as physics.

**Fixed here** (implementation, not a preregistered criterion): the mapping reads the driver's keys (legacy
short names retained as a fallback), `e4_lys_min_A` is carried through so prereg §3's "E2–E4 reported
alongside E1 in every result" is actually true of the artifact, and a **schema guard** now refuses to emit a
verdict when legs landed, none blew up, and yet none produced an endpoint —
`tests/test_nrv04_retro_collect_contract.py`, 5 tests, with the old rule pinned as the bug.

## 2. Which of the four sibling defects are inherited

| sibling defect | inherited? | evidence, from the artifact that would run |
|---|---|---|
| **(1) wrong cysteine / A1 at C566 not C551** | **YES — and it is now fatal to the R2 arm.** `retro_cov_nr4a1` declares `COV_RESNUM=551`; `_frozen_cys_by_construct` resolves construct residue 207 and `build_system` **raises** above 8.0 Å. Its three models measure **34.42 / 29.87 / 39.11 Å** at C551 | `nrv04-retro-prespend-audit.json` → `covalent_arm_admissibility`: `n_models_passing_A1: 0 / 3` |
| **(2) R3 in nm under an Å label** | **NO** — the shared driver converts at the boundary (`_lys_A`/`_proxy_A`, `* 10.0`) before `lys_presentation`, with the incident recorded inline | `nrv04_covalent_md.py` run_leg, lines 783–793 |
| **(3) positional chain split** | **NO** — the assembler writes `chains.json`, the driver reads it *before* the build and passes `target_chain` to both `build_system` and `_topology_indices`; a smoke leg on real hardware committed `target=['A'] e3=['E','F','G'] explicit=True` | driver lines 663–689; handoff §2 |
| **(4) contaminated inputs (14-3-3 ε for Elongin B)** | **NO — verified on all 9 models, not on the prefix name.** The retrospective's prefix is hard-coded in `nrv04_retro_panel.COFOLD_PREFIX` and is **not** overridable by the workflow's `cofold_prefix` input, so the mechanism that contaminated the sibling (a workflow default overriding a clean fallback) cannot fire here | census `A=254 / E=213 VHL / F=**118** Elongin B / G=112 EloC`, `contaminant: []`, on every one of the 9 |

Two things worth keeping: the 6 `nr4a2`/`nr4a3` models had **never** been chain-audited (the A1 audit skips
them — they are not in its covalent-panel system allowlist) even though they are the inputs to 12 of the 18
primary legs; and each pinned model prefix resolves to **exactly one** `*_model_0.cif`, which is the invariant
the leg pipeline itself enforces on pain of exit 3.

**The R2 failure is not confined to R2.** `build_system` raises *before* a leg JSON is written, so those 6
units never land; `retro_collect` builds `expected` from `retro.enumerate_units()` (stages R1 **and** R2), and
prereg §4f forbids a contrast on an incomplete panel. Fed 18 flawless R1 legs and no R2 legs, the real
collector returns:

```
R1 legs landed: 18 of 24 enumerated units
missing: nrv04retro-retro_cov_nr4a1-m{1,2,3}-r{0,1}
panel_complete: False | verdict: None
```

So the two blockers are **sequential**: fix the collector and you still get no verdict, because R2 can never
complete the panel. Retiring R2 (proposed AMENDMENT 3, defect 1) is what makes the R1 result reachable at all.

A hardening that already works: `_frozen_cys_by_construct` verifies the residue is a Cys bearing an Sγ and
raises otherwise, so a covalent paralogue leg — forbidden by prereg §2b — would **fail closed** on NR4A3
(construct 207 is not a cysteine) rather than silently adducting something else.

## 3. Degenerate frozen criteria (AMENDMENT 1's own test, applied before any leg runs)

The standard AMENDMENT 1 set: *a rule may be amended only if its statistic is shown to lack discriminating
power, demonstrated independently of whether we liked the answer.* Applied to `nrv04_retro_gate.py`:

**(a) The primary statistic is a rank statistic, and that bounds what the test can ever see.** With 3 vs 6 and
pooled total S, `d = mean(A) − mean(B) = a/2 − S/6` is strictly increasing in `a = sum(A)`, so the exact
permutation p-value is exactly `rank(sum of the NR4A1 trio) / 84`. Verified on 4,000 random configurations,
zero mismatches. **Consequence:** a 0.2 Å effect and a 20 Å effect that produce the same ordering produce the
same p. This is not a defect — it is what an exact rank test *is* — but it is why (c) below matters.

**(b) The extension rule (§4d) is unreachable in its stated case — DEGENERATE.** It fires on
`p ∈ (0.012, 0.05]`. The attainable p-values are `k/84`, so the window contains exactly
**{0.0238, 0.0357, 0.0476}** — and **all three are ≤ α**, hence already CONCORDANT. The smallest attainable p
strictly above α is **0.0595**, outside the window. So the rule as frozen fires *only* on results the same run
already grades CONCORDANT, and **never** on the case its own text names ("the ordering is right but n = 3
models cannot resolve it", which requires p > α). It is a criterion that cannot do the job it was written for.

**(c) The LOMO clause is inert — DEGENERATE.** Adversarial search over 400,000 configurations, deliberately
including the ones where NR4A1 is *not* simply the three smallest values (p ≤ 4/84 admits {v1,v2,v4},
{v1,v3,v4}, …): **228,543 reached p ≤ α with the correct ordering and NR4A1 below both paralogues; zero then
failed LOMO.** So the CONCORDANT tier's four conditions are effectively three, and the WEAKLY_CONCORDANT
branch reading *"correct ordering and p ≤ alpha, but the sign fails leave-one-model-out"* is unreachable code.

**(d) No minimum detectable effect is registered, which is what §5c's "informative null" actually depends on.**
Measured pooled within-system leg SD, from 6 groups of committed feasibility legs (same system, same co-fold
model, velocity seeds only): **σ = 0.855 Å**, across an observed E1 range of 1.005–5.047 Å. Monte-Carlo through
the frozen decision rule:

| true NR4A1-vs-paralogue separation | power (σ = 0.605 Å, optimistic) | power (σ = 0.855 Å) |
|---|---|---|
| 0.0 Å | 0.048 | 0.048 |
| 0.5 Å | 0.27 | 0.18 |
| 1.0 Å | 0.65 | 0.43 |
| **1.5 Å** | **0.92** | 0.70 |
| **2.0 Å** | 0.99 | **0.89** |

The false-positive rate at δ = 0 is 0.048 — the test is **valid**, not anticonservative. But its **MDE at 80 %
power is 1.5–2.0 Å**, and the realistic figure is the *right-hand* column or worse: the σ = 0.605 column
assumes co-fold-model-to-model structural variance is **zero**, while distinct co-fold seeds of the same system
differ by 3–8 Å CA-RMSD. Requiring a ≥ 1.5–2.0 Å between-paralogue mean separation is asking for a difference
comparable to half the entire observed dynamic range of the endpoint.

**Not degenerate:** E1 itself varies (measured 1.005–5.047 Å); E2's 4.0 Å threshold is met by some legs and not
others; E3's *continuous* `mean_contacts` varies (1620–3861) and the retrospective correctly does **not** gate
on the derived binary `recruited`, which is the statistic AMENDMENT 1 retired. One cosmetic asymmetry: the
reverse-direction check only appends text to `reason` — a significant *reverse* result and a merely wrong-signed
one are both graded DISCORDANT.

## 4. Is the design still coherent after AMENDMENT 2?

**R2 is gone, and with it the composite outcome §5c registers as the expected one.** AMENDMENT 2 retired the
sibling panel's covalent legs on evidence that no predictor seats celastrol near C551 — 7/7 clean models, 4
seeds, 3 prefixes, 2 providers, plus a steered co-fold that honoured a 6 Å restraint and still failed on 3
seeds. That evidence transfers verbatim: the retrospective's own three NR4A1 models measure 29.9–39.1 Å at
C551. So:

- prereg §0's table — R2 *"quantifies how much of the NR-V04 result is warhead chemistry"* — has nothing to
  quantify it with;
- prereg §5c's registered expected result is *"a **null R1 with a strong R2 covalency effect**"*. With R2
  unbuildable, that composite is **unattainable**. A null R1 would stand alone, and the localisation of NR-V04's
  selectivity to warhead reactivity would rest **entirely** on Leg 0 (sequence: NR4A1 Cys551 unique; NR4A2 Tyr,
  NR4A3 Thr579) and Zhang 2018 — which is honest and sufficient, but it is **not** what the prereg registers.

**R1's own construct validity is weaker than the prereg assumes.** §2a/§2c ground protocol-matching in "one
co-fold prefix, one code path". That matches the *procedure*; it does not match the *structures*, which are
independent Boltz diffusion outputs. Measured at t = 0 on the exact models that would run:

| arm | warhead↔target contacts (4.5 Å) | warhead↔E3 contacts | min warhead–target distance |
|---|---|---|---|
| NR4A1 (degraded) | 35 / 67 / 40 — mean **47** | 41 / 29 / 30 — mean **33** | 2.85 / 2.67 / 2.71 Å |
| NR4A2 (spared) | 185 / 72 / 61 — mean **106** | 0 / 41 / 0 — mean **14** | **1.05** / 2.43 / 2.74 Å |
| NR4A3 (spared) | 58 / 87 / 74 — mean **73** | 14 / 19 / 3 — mean **12** | 2.76 / 3.07 / 2.78 Å |

The **spared** paralogues begin with the warhead **more** engaged with their target and **less** draped over the
E3 than the degraded one does — i.e. the starting-structure asymmetry runs *against* the registered direction
(NR4A1 predicted more stable). And `nr4a2/m1` — which is the designated **pilot leg** — starts with a **1.05 Å**
heavy-atom overlap, well inside a covalent bond length; minimization must resolve a hard clash there, and that
relaxation will dominate its early interface RMSD.

**Is a null R1 still a registered, publishable outcome?** As an *outcome*, yes — and it should stay registered.
As an *inference*, no, not as §5c words it, on two independent counts: the composite it names cannot occur
(R2), and a null is the modal result for any true separation below ~1.5 Å regardless of the biology (§3d). A
null licenses *"the workflow did not resolve a paralogue difference of the size this design can detect"*, not
*"selectivity is localised to warhead reactivity"*.

## 5. Corrected price

Two different objects are both called "the NR-V04 retrospective", and they are priced in different ledgers.

**(a) The ~$21 line is the ALCHEMICAL arm (Arm F) — which the prereg does not authorise.** Schedule id
`nrv04_retrospective` prices *"3 ternary LEGS + 1 shared binary + 1 shared solvent"* — the exact cancellation
identity — at 84–216 reference-4090 GPU-h × $0.1372 = ~$21. That is the **2400-iteration** basis. On the as-run
**2800** (warmup iterations derive from the WARMUP integrator at 1 fs → 800, not 400 — `rbfe_spot_driver`
`_iters_from_time`, ×1.1667), it is **98–252 ref GPU-h → $24.01 plan, $5.59–$77.97**, already regenerated in
`vast-ladder-repricing.json`. **The schedule JSON and `pricing.md` still carry the stale ~$21 ($4.8–$67).**
This figure is the **2 fs base**; `pricing.md` §B is explicit that the 4 fs conversion (×0.643, not ×0.5) is not
taken until the recalibration edge runs. Arm F remains **BLOCKED** by calibration addendum condition 7.

**(b) What a GO on RUNG 4 would actually spend is Arm E endpoint MD**, priced from the measured 15-leg ledger at
**$0.43/leg**:

| | legs | measured-realized basis | current best-10-offer policy (1.38 ref GPU-h/leg × $0.1372) |
|---|---|---|---|
| as frozen (R1 + R2) | 24 | **~$10.3** | ~$4.6 |
| **as runnable today** (R2 unbuildable) | **18** | **~$7.7** | ~$3.4 |
| R3 epimer (conditional, §5d) | 18 + 6 co-folds | ~$7.7 + ~$1 | — |

The two bases differ because the $0.43 was realised on 3090 rentals at $0.10–0.21/hr, while the policy rate
prices a top-10-ranked 4090 offer; the prereg's own "~$0.19 converted to a reference 4090 GPU-hour" is the same
reconciliation. **Plan on the measured-realized number.**

## 6. Recommendation — **HOLD**, and the hold is cheap to clear

Do **not** launch. Nothing is pending and $0 has been spent. Three things gate it, in order:

1. **Ship the collector fix** (done here) and prove it on the pilot's own collect before the fan-out. Without
   it the 18–24 legs buy an INDETERMINATE.
2. **A dated prereg amendment** covering the R2 arm, the extension rule, the LOMO clause and the MDE
   (proposed in §7, **not applied** — amending a preregistration is trimcrae's).
3. **A $0 decision on R1's starting structures.** The t = 0 asymmetry in §4 is measured, not hypothetical, and
   it is decision-relevant: either register it as a stated limitation, or add a cheap pre-registered
   admissibility criterion on ligand placement (the analogue of A1 for the non-covalent arms) and regenerate
   the models that fail it. Either is free; simulating past it is not.

## 7. Proposed AMENDMENT 3 — exact text, **not applied**

> ### AMENDMENT 3 — 2026-07-25 (dated defect-fix; proposed, pending trimcrae)
>
> **Authority.** §7's freeze and nr4a3-program-map.md's requirement that amending a preregistered rule be an explicit,
> dated, reviewer-approved defect-fix. The frozen text above is left **unedited**.
>
> **Standard applied (AMENDMENT 1's):** a rule may be amended only if its statistic is shown to lack
> discriminating power, demonstrated independently of whether we liked the answer it gave. All four findings
> below were measured **before any retrospective leg ran**, so no result exists to have liked or disliked.
>
> **Defect 1 — the R2 arm is unbuildable on every available input.** `retro_cov_nr4a1` declares the C6→Cys551
> adduct. Measured at the preregistered site on the exact pinned models
> (`nrv04-descriptive-v4/nr4a1/seed_{1,2,3}`): **34.42 / 29.87 / 39.11 Å**, against A1's 8.0 Å limit, so
> `nrv04_covalent_md.build_system` raises. This is the same finding as covalent-panel AMENDMENT 2, on
> independent models: no predictor in this pipeline — unconstrained, re-seeded, E3-free or steered — seats
> celastrol against C551. It is also **blocking**: the raise happens before a leg JSON is written, so the 6
> units never land, `panel_complete` stays False and §4f suppresses the R1 contrast permanently — leaving R2
> in the panel does not merely cost an arm, it costs the primary result. **Ruling: R2 is RETIRED**, and with
> it §5c's registered composite outcome. The
> covalent confound is documented from **Leg 0** (sequence) and **Zhang 2018** (literature), never from a
> simulation this program ran. The authorized panel becomes **R1 only, 18 legs**.
>
> **Defect 2 — the §4d extension rule cannot fire in its stated case.** Attainable p-values are k/84. The
> window (0.012, 0.05] contains exactly {0.0238, 0.0357, 0.0476}, all ≤ α and therefore already CONCORDANT;
> the smallest attainable p above α is 0.0595, outside the window. **Ruling: the window becomes
> `(0.05, 0.12]`** — the right-sign-but-unresolvable band the rule's own text describes, i.e. p ∈ {5…10}/84 —
> and it remains triggerable by the p-value alone and unavailable to a wrong-sign result.
>
> **Defect 3 — the LOMO clause is inert.** 228,543 configurations reached p ≤ α with the correct ordering;
> zero failed LOMO. **Ruling: LOMO is retained as a REPORTED robustness diagnostic and removed from the
> CONCORDANT tier's conjunction**, which it cannot affect. The WEAKLY_CONCORDANT branch predicated on it is
> struck as unreachable.
>
> **Defect 4 — no minimum detectable effect was registered, and §5c depends on one.** Measured leg-to-leg
> σ = 0.855 Å; MDE at 80 % power = **1.5 Å (optimistic, σ_model = 0) to 2.0 Å**. **Ruling: the MDE is
> registered**, and §5b/§5c are narrowed: a null R1 licenses *"the workflow did not resolve a paralogue
> difference of the magnitude this design can detect (≥ ~1.5–2.0 Å in interface-RMSD plateau at n = 3
> models/arm)"* and **may not** be reported as localising NR-V04's selectivity to warhead reactivity. That
> localisation stands on Leg 0 and Zhang 2018 and is stated as such.
>
> **Does this amendment rescue a failing result? NO — stated as the integrity test.**
> 1. **No result exists.** Not one retrospective leg has run; there is no outcome for any of this to flip.
>    Every criterion changed here was assessed by enumeration or against the *sibling* panel's noise.
> 2. **None of the four can convert a fail into a pass.** Defect 1 **removes** an arm (strictly less evidence,
>    strictly less spend). Defect 2 alters only whether *more data is generated* — `extension_triggered` is a
>    separate field that `nrv04_retro_gate.verdict` never reads when assigning a tier; the corrected window
>    fires on p > α, which is precisely the region that is **not** CONCORDANT, so it can only add work to
>    ambiguous results, never promote one. Defect 3 removes a condition that has been shown incapable of ever
>    being false when the others hold — the CONCORDANT set is **unchanged** by construction. Defect 4
>    **restricts** what a null may claim.
> 3. **The primary contrast, its direction, its α, its endpoint, its threshold and its unit of independence
>    are all untouched.**
>
> **Honest statement of what this LOOSENS and what it TIGHTENS.** Defect 2 is a **loosening in form** — it
> makes an extension reachable where it previously was not — but it buys no claim: an extension only ever adds
> models and re-runs the same frozen test at larger n. Defects 1, 3 and 4 all **tighten**: one arm is deleted,
> one tier condition is demoted to a diagnostic (removing a clause that could never bite is neutral to the
> verdict and honest about the tier's real content), and the null's licensed claim is narrowed. Net: the
> retrospective can claim **less** after this amendment than before it.

## 8. Exact deltas requested elsewhere (**not applied** — these files are owned upstream)

**`nr4a3-nrv04-retrospective-prereg.md`** — append AMENDMENT 3 verbatim from §7. Additionally, in the same
amendment or a note beside §2a/§2c: record that "one co-fold prefix + one code path" matches the *procedure*
but not the *structures*, with the measured t = 0 asymmetry from §4 (NR4A1 warhead↔target mean 47 contacts vs
NR4A2 106 / NR4A3 73; NR4A1 warhead↔E3 33 vs 12–14) stated as a limitation of R1 — or, if a criterion is
preferred over a caveat, a pre-registered non-covalent placement-admissibility rule and regeneration of the
models that fail it. Flag `nrv04-descriptive-v4/nr4a2/seed_1`'s **1.05 Å** warhead–target overlap explicitly:
it is the designated pilot.

**`research/manuscripts/degrader-paper-schedule.json`** → `nrv04_retrospective.cost_est_usd`: replace
**~$21 ($4.8–$67), 84–216 ref GPU-h** with **~$24 ($5.6–$78), 98–252 ref GPU-h** — the as-run 2800-iteration
basis, regenerated by `vast_cost_model.py` into `vast-ladder-repricing.json`, which already carries $24.01.
Add that this prices **Arm F**, which the prereg does not authorise, and that the authorized **Arm E** is
**~$7.7 for the 18 runnable legs** on the measured $0.43/leg ledger.

**`research/compute/pricing.md`** line 183 (`nrv04_retrospective` row): same substitution, same reason; the row
already says "PROJECTED on the ternary component" and should say which arm that is.

**`nr4a3-program-map.md`** RUNG 4: record that the retrospective is **HELD pending AMENDMENT 3 + the collector fix**,
that its covalent R2 arm is retired for the same reason AMENDMENT 2 retired the sibling's covalent legs, and
that the "two bugs found here propagate to the unlaunched NR-V04 retrospective" note (line ~1289) now has a
**third and a fourth**: the covalent site was resolved by proximity rather than identified (fixed upstream), and
the retrospective's collector read leg-JSON keys the driver does not write (fixed here).

## Provenance / honesty

- Every distance, census and contact count is measured on a real co-fold artifact in the bucket by the same
  kernels the assembler and driver use; the E1 values are read off real committed leg JSONs. Nothing is
  fabricated or estimated.
- The power figures are Monte-Carlo through the **frozen** decision rule against a **measured** SD; they are a
  property of the design, not a prediction of any result.
- **$0 spent. No GPU leg, no instance, no co-fold was launched by this lane.**
- Any NR-V04 statement remains **directional concordance** only, with the covalent confound explicit: NR4A1
  Cys551 is unique to NR4A1 (NR4A3 has Thr579), so a concordant result may reflect **target engagement** rather
  than ternary cooperativity — which is exactly why NR-V04 is a **biological holdout, not the method
  calibrator**. No efficacy, affinity, safety, therapeutic-window or clinical claim is made or implied, and
  nothing here says "recovered degradation".
