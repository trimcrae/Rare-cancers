# valB_mini — what the r0 replicate actually says, and why r1/r2 is the wrong next spend

**Date:** 2026-07-25 · **Status:** analysis + recommendation; the strategic call (rescope vs spend) is trimcrae's.
**Governing gate:** `wurz-calib-frozen.json → decision_rule_valB_mini` (reviewer condition 6, 2026-07-19),
implemented as `ternary_fep_reduce.calibration_gate` — the three-tier PASS / BORDERLINE / FAIL rule. The older
zero-exclusion variant (`calibration_decision`) is superseded and is *retired precisely because it could accept
zero*.

---

## 1. The result

From CI run `30148463967` (`mode=reduce`, 2:59 AM ET 2026-07-25), re-confirmed with a full per-leg dump in run
`30155238348`:

| leg | ΔG_morph (kcal/mol) | replicates | reverse leg |
|---|---|---|---|
| `calib_hi_to_lo__binary_vhl` fwd r0 | **48.0046** | 1 | none |
| `calib_hi_to_lo__ternary_vhl` fwd r0 | **47.4701** | 1 | none |
| `calib_hi_to_lo__solvent` fwd r0 | **47.8060** | 1 | none |

**ΔΔG_coop(r0) = ternary − binary = −0.534 kcal/mol.** Preregistered target **+0.944** (α_SPR 12.8 → 2.6, Wurz
2023). So the single available replicate has the **wrong sign** and is **1.478 kcal/mol** from target.

Gate verdict: `INDETERMINATE — need >=2 independent replicates for a cycle SD` (n=1).

Two things that are *not* wrong, and should not be blamed:

- **`protocol_hash_consistency: consistent, 1 distinct hash`** across all three legs. The cycle is not
  contaminated by a protocol/timestep/charge mismatch between the ternary and binary arm. That worry is closed.
- **`"converged": false`** in the per-leg schema record is **not** an MD-convergence finding. It is
  `n_replicas >= 3 and ci <= 1.5 and hysteresis <= 1.0`, and it is False only because n=1. Do not cite it as
  evidence the trajectory is bad.

---

## 2. r1 + r2 cannot produce a PASS. This is arithmetic, not judgement.

Exhaustive scan of every (r1, r2) pair over [−4, +8]² at 0.05 kcal/mol resolution, through the frozen gate, with
r0 = −0.534 held: **17,276 BORDERLINE, 11,885 FAIL, 0 PASS.**

Analytic proof:

```
PASS at n=3 (not yet extended) requires NOT near_boundary, i.e. abs_err <= 0.5 AND cycle SD <= 0.25
abs_err <= 0.5                       =>  mean >= 0.444
one replicate pinned at r0 = -0.534  =>  SD >= (mean - r0)/sqrt(n-1) = (0.444+0.534)/sqrt(2) = 0.692
0.692 > 0.25                         =>  contradiction. No (r1, r2) exists.
```

So the honest description of "run r1 and r2 and hope" is: **spend to convert an INDETERMINATE into a
BORDERLINE-extend-to-5, or into a FAIL.** Neither authorises the NR-V04 retrospective.

### And the n=3 round was never going to be decisive anyway

The same boundary rule requires a first-round PASS to have cycle SD ≤ 0.25 kcal/mol. For a method that is
**perfectly accurate** (true effect exactly +0.944), Monte Carlo over the real gate gives:

| true replicate SD | P(PASS) at n=3 | P(BORDERLINE) |
|---|---|---|
| 0.3 | 50 % | 50 % |
| 0.4 | 31 % | 69 % |
| 0.5 | 20 % | 80 % |
| 0.7 *(the repo's own assumed SD)* | 9 % | 90 % |
| 1.0 | 4 % | 91 % |

The first round is **BORDERLINE-by-construction** at any realistic noise level. r0's wrong sign did not create
that; it only removed the residual 9 %.

---

## 3. Going to n=5 buys little, and the gate cannot tell signal from nothing

Conditioning on r0 and drawing r1…r4, through the real gate (40 000 trials each):

| scenario | n=3 (+r1,r2) | n=5 (+r1…r4, extended) |
|---|---|---|
| method exactly right, SD 0.4 | BORD 99 %, FAIL 1 % | **PASS 53 %**, BORD 46 % |
| method exactly right, SD 0.7 | BORD 91 %, FAIL 9 % | **PASS 23 %**, BORD 48 %, FAIL 28 % |
| method right, SD 1.0 | BORD 83 %, FAIL 17 % | **PASS 11 %**, FAIL 61 % |
| **no real signal (μ = 0), SD 0.7** | BORD 29 %, FAIL 71 % | **PASS 22 %**, FAIL 67 % |
| r0 is representative (μ = −0.534) | BORD 5 %, FAIL 95 % | PASS 2 %, FAIL 98 % |

**Read the 4th row against the 2nd.** A method with *zero* cooperativity signal passes at n=5 about as often
(22 %) as a method that is *exactly right* (23 %).

The cause is a defect in the frozen accuracy criterion: `|mean − 0.944| ≤ 1.0` **admits mean = 0.0** (error
0.944 < 1.0). Verified directly against the gate:

```
five replicates all at +0.05 (i.e. no signal)  -> mean +0.050  sd 0.000  err 0.894  -> PASS
five replicates scattered around zero          -> mean +0.060  sd 0.096  err 0.884  -> PASS
```

**A gate you can pass by predicting nothing is not a validation.** So even a PASS on the current design would not
have earned what it was supposed to earn — the right to trust the ΔΔG_coop cycle on NR4A.

> ⚠ **Do not quietly retune this.** The rule is preregistered, and tightening it *after* seeing a failing result
> is exactly what preregistration exists to prevent. Any change must be explicit, dated, justified as a
> **defect-fix** (the criterion admits the null hypothesis it was meant to exclude — a logical flaw present at
> freeze time, independent of r0), and — because this gate blocks the flagship — reviewer-approved. It is
> recorded here, not applied.

---

## 4. Why the design is fragile: the answer is 1.1 % of the numbers being subtracted

The reduction's own condition-8 audit: `cancellation_ratio = 0.01113`, `max_leg_magnitude = 48.0046`. All three
legs land within 0.54 kcal/mol of each other around ~47.8 — the N→CH morph free energy is almost entirely an
environment-independent common mode, and the *entire* physical signal is a ~0.5 kcal/mol residue on top of it.
Resolving the +0.944 target means determining a **~2 % differential** between two ~48 kcal/mol alchemical free
energies computed by MBAR over 12 λ-windows in a 146 k-atom **homology-built** assembly (8G1Q is a 3.73 Å
SMARCA4 structure with the BD sequence substituted to SMARCA2 and relaxed — already recorded as a valB_mini
limitation).

The audit's note is correct that a large common mode is fine **"if binary + ternary cancel reproducibly."** That
conditional is the whole question, and n = 1 cannot answer it.

---

## 5. Two of the three independent error detectors were never run — and one could not have run

Replicates detect **random** error only. STRATEGY.md's own line: *"Replicates shrink precision, not accuracy."* A
**wrong sign, 1.478 kcal/mol from target** is far more consistent with a systematic problem than with a 2σ
unlucky draw. The instruments for systematic error:

1. **Forward/reverse antisymmetry — NEVER RUN.** `antisymmetry_fwd_plus_rev_kcal: null` on all three legs; only
   `fwd` legs exist. |ΔG_fwd + ΔG_rev| detects insufficient sampling and hysteresis **without needing the
   experimental answer**, and costs the same as one replicate.
2. **Convergence diagnostics on the committed trajectory — COULD NOT HAVE RUN.** The reviewer's required change
   #1 was *built* (`ternary_fep_convergence.py`, engine `MODE=converge`) and then never *wired*: this workflow
   had no `converge` mode, and the reduce step calls the reducer module directly rather than the engine's
   `main()`, so no dispatch path reached it. And `_diagnostics_ok()` returns **True when the report is absent** —
   so the gate's "all convergence diagnostics pass" requirement has been satisfied by never measuring it.
   Wired 2026-07-25 (this branch); on first execution it surfaced two further blockers that would have stopped it
   regardless (see §6).
3. **Cycle closure — absent by design.** A single edge with no redundant path has no internal consistency check.
   Reviewer Req 7 already noted a redundant edge is required before any relative-edge calibration network.

---

## 6. What the newly-wired convergence run found (2026-07-25)

- The committed `simulation.nc` for the r0 legs **does exist** — the first "no production commits" report was my
  wrong path guess (the commit prefix is keyed by (dt, clig, warmup, salt); discovery is now layout-agnostic).
- On first real execution the analyzer crashed: **`ModuleNotFoundError: No module named 'openfe'`**, from
  `_overlap → analyzer.mbar → read_end_thermodynamic_states → utils.deserialize → import_module('openfe…')`.
  openmmtools stores end thermodynamic states as serialized class references and OpenFE's alchemical composable
  state is one of them, so an openmmtools-only environment **cannot analyse an OpenFE trajectory at all**.
- And `_overlap`'s lazy `mbar` access sat **outside any try**, so that one env gap deleted the other six
  diagnostics — despite the module docstring promising each degrades to a status string.

Both fixed on `claude/max-effort-3hgq45`. Net: **required change #1 has been non-functional since it was built** —
unwired, missing a dependency, and fatal on its first metric — and its silence read as `diagnostics_ok = True`.

---

## 7. Recommendation

**Do not buy r1 + r2 as a rescue attempt.** It cannot pass, and it is the one instrument blind to the failure
mode most likely in play. In order:

1. **(free, in flight)** Finish the convergence analysis of r0's three legs. Overlap connectivity, dG(t) plateau,
   replica mixing, N_eff and structural drift decide whether −0.534 is a *measurement* or an *artifact*. Nothing
   else should be bought before this reads out.
2. **(free)** Record the admits-zero defect (done, §3) and route the gate amendment for approval. Do not apply it
   unilaterally.
3. **(~one replicate's cost, strictly higher information than a replicate)** Run the **reverse** ternary and
   binary legs of r0. |ΔG_fwd + ΔG_rev| tests systematic error directly; a replicate cannot.
4. **(the real decision) Rescope the calibrator to a signal the method can resolve.** Target ≳2 kcal/mol — not an
   arbitrary number: it is the same ~2.0 kcal/mol margin STRATEGY.md says a useful degradation window requires.
   Calibrating at 0.944 demands resolution the programme does not even need. Two routes that keep a congeneric
   map:
   - a **multi-edge path** through the SMARCA2–VHL series (signal adds linearly, noise as √N) — which also
     finally supplies **cycle closure**; or
   - the reviewer's original high-contrast pair (P1 α 93 → P4 α 1.3 ≈ **+2.53**; → P5 α 0.6 ≈ **+2.99**) reached
     via intermediate congeneric hops instead of one 32–47-atom jump.

### Strategic note

STRATEGY.md already concluded (2026-07-24, mechanism-first revision) that the marginal/induced-interface axis
*"is a confirmation tool operating near its limit, not a discovery tool"* — best-case resolvable difference
1.12 kcal/mol against a ~2.0 kcal/mol requirement. **valB_mini is a test of exactly that near-limit axis, at a
0.944 kcal/mol signal.** The programme's own revision moved the load-bearing selectivity claim to the
*categorical* mechanisms (paralogue-unique C397, K572/K518/K592). So forcing a PASS here optimises a gate the
strategy has already demoted.

The constructive reframe: a rigorous, honest **measured resolution floor** for the ΔΔG_coop cycle — "this
workflow resolves induced-interface differences of ≥X kcal/mol and not below" — is itself a publishable result,
is exactly the honest-limits reporting the North Star calls for, and is what the paper needs in order to state
what the ternary numbers can and cannot support. That is a better deliverable than a 23 %-odds PASS on a
benchmark that a null method passes 22 % of the time.
