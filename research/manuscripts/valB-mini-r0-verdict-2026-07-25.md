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

Replicates detect **random** error only. nr4a3-program-map.md's own line: *"Replicates shrink precision, not accuracy."* A
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

## 6. THE CONVERGENCE RESULT — r0 is a converged measurement, not a broken run

Once wired and repaired (§6b), the analyzer ran on r0's real committed trajectories. **Ternary leg
`calib_hi_to_lo__ternary_vhl`, seed 0** (final run `30157501491`):

| diagnostic | value | threshold | verdict |
|---|---|---|---|
| MBAR ΔG | 47.511 **± 0.045** | — | tiny statistical error |
| production iterations | **2000 / 2000** | — | complete leg (the 7/24 forensic read's 1560 was mid-flight) |
| overlap scalar | 0.135 | ≥ 0.03 | pass |
| min adjacent overlap | **0.109** (pair 4–5) | ≥ 0.03 | **λ-path connected** |
| equilibration fraction | 0.381 (761 of 2000) | ≤ 0.50 | pass |
| N_eff | 676 (g = 1.83) | — | well sampled |
| replicas visiting both ends | 12 / 12 | — | pass |
| replica mixing (subdominant eig.) | **0.8915** | ≤ 0.90 | passes **by 0.0085** — record as marginal |
| ΔG(t) full vs final half | **0.0023** | ≤ 0.5 | pass |
| ΔG(t) q3 vs q4 | **0.1255** | ≤ 0.5 | pass |
| fwd/rev gap @ f = 0.875 | **0.0255** (max 0.179 for f<1) | ≤ 1.0 | pass |
| ligand-only pose RMSD | **unmeasured** | ≤ 4.0 Å | needs ligand indices from the hybrid topology |

`technical_failure: false`, `diagnostics_complete: false` (the one unmeasured flag).

**This is the decisive finding for §7.** The free-energy estimate is converged and structurally sound, and
its statistical error (0.045) is ~33× smaller than its miss (1.478). **Therefore the wrong sign is systematic,
and replicates — which shrink variance, not bias — are the wrong instrument.** Adding r1/r2 to a calculation
whose ΔG(t) is flat to 0.002 kcal/mol cannot move the mean toward +0.944.

One nuance that makes the replicate case *worse*, not better: ternary seed *s* uses the *s % n*-th
independently relaxed SMARCA2 model, so r1/r2 are partly **different structures**. Their spread would conflate
sampling noise with homology-model sensitivity — informative about model uncertainty, but not what a
calibration needs, and it makes the SD ≤ 0.75 requirement harder to satisfy.

### Structural check — measured, and its scare number explained away

The solute proxy (7388 of 141968 atoms = the whole assembly + PROTAC, **not** the ligand) first read
**78.94 Å**, then 14.97 Å after Kabsch superposition, and *set `technical_failure: true`* — which via
`_diagnostics_ok()` would have handed valB_mini a **hard FAIL**. That FAIL was an artefact:

- displacement distribution: **p50 2.50 Å, p90 5.91 Å**, but p99 71.5 Å and max 128 Å against a **126.3 Å**
  box edge, with ~1.3–2.0 % of atoms beyond half a box;
- the arithmetic closes — √(0.02·100² + 0.98·3²) ≈ 14.4 Å reproduces the reported 14.97, so **the entire
  apparent rearrangement was that small wrapped tail**;
- ⇒ **H1 (the ternary assembly genuinely rearranged) is REFUTED; the interface is stable at ~2.5 Å median.**
  This also retires the worry H1 raised: the systematic behind −0.534 does **not** implicate the
  SMARCA4→SMARCA2 starting model destabilising the interface.

**Known-incomplete, recorded rather than papered over:** ~1.3 % of atoms still show large displacements after
minimum-image correction, and **the cause is unknown.** I initially attributed it to the parallelepiped fold
being non-minimal on this truncated-octahedron cell (rows `[126.3,0,0] [0,126.3,0] [63.1,63.1,89.3]`) and
added a 27-neighbour search; **direct test refuted that** — fold-only recovers true displacements with worst
error 0.000 Å over 4000 trials on this exact cell, so the search is a no-op here. Undiscriminated candidates:
an NPT box differing between the two compared frames; iteration 0 being pre-equilibration; or
`read_sampler_states[0]` not being the same continuous replica at both iterations. **Discriminator (free):**
compare adjacent checkpointed frames (1960 vs 2000), where nothing can have moved far. No verdict rides on
this number — `ligand_stable_ok` stays unmeasured and `technical_failure` stays false.

## 6b. What the newly-wired convergence run found (2026-07-25)

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

### The full defect list — every one reported success while measuring nothing

Seven defects in the diagnostic that **gates this programme**, all found on 2026-07-25, all fixed on this branch:

1. **Never wired** to any dispatch path (`MODE=converge` existed in the engine; no workflow could reach it).
2. **Missing `openfe`** in the analysis env — openmmtools deserializes end thermodynamic states via class
   references, and OpenFE's alchemical composable state is one, so the *first* metric raised
   `ModuleNotFoundError`.
3. **`_overlap`'s lazy `mbar` access sat outside any try**, so that one env gap deleted the other six
   diagnostics — despite the module docstring promising each degrades to a status string.
4. **Slice MBAR never converged** — `_block_plateau` and `_forward_reverse` built bare `MBAR` objects on
   sub-slices and both died on pymbar's `\sum_n W_nk = 1` check. Seeded from the analyser's converged `f_k`,
   both now compute. (That error's stock text says *"generally indicates the free energies are not converged"*;
   on the evidence it was a verdict on the solver call, not the physics — openmmtools' own MBAR converged on
   the identical samples.)
5. **The fwd/rev gap was taken at fraction 1.0**, where the forward slice (first 100 %) and reverse slice (last
   100 %) are *the same samples* — so it was identically ~0 and `FWD_REV_GAP_MAX_KCAL` could never fire.
   Confirmed empirically: `gap_at_full_fraction_uninformative: 0.0` exactly.
6. **The checkpoint was never opened** — openmmtools looks for `checkpoint.nc`; this repo's driver writes
   `checkpoint.chk`. So positions were unavailable and the mandated ligand-escape check had **never once
   produced a number**, on this lane or any other sharing this commit store.
7. **A ligand-pose threshold applied to the wrong observable** — first an unaligned whole-system RMSD over
   ~146k atoms (79 Å, dominated by bulk water), then a superposed whole-solute RMSD (15 Å), each compared to
   `LIG_RMSD_MAX_A`. The second produced a **fabricated hard FAIL**.

Two of these were actively producing wrong verdicts: #1–#3 as a silent `diagnostics_ok = True`, and #7 as a
FAIL that would have read as *"the ternary lane is broken."* **This bears on how much weight the lane's
verdicts can carry, and argues for spending the next dollar on *independent* checks — reverse legs, cycle
closure — rather than more replicates through the same machinery.**

### Infrastructure note worth keeping

The analysis env is now the pre-baked `docker.io/triskit23/ternary-fep` image rather than an ad-hoc
`micromamba create`: **4.3 min end-to-end vs ~22 min**, and — the reason that actually matters — it is
*byte-for-byte the env the GPU legs run*, so the analysis uses the same openfe/openmmtools/pymbar that
**produced** the trajectory. An ad-hoc solve in an analysis step is a silent protocol deviation on a frozen
protocol. Codified as a standing rule in CLAUDE.md.

---

## 7. Recommendation

**Do not buy r1 + r2 as a rescue attempt.** It cannot pass, and it is the one instrument blind to the failure
mode most likely in play. In order:

1. **✅ DONE (free) — and it answered the question: −0.534 is a MEASUREMENT, not an artifact.** See §6. The leg
   is converged on every measurable criterion (ΔG(t) flat to 0.0023, fwd/rev 0.0255, overlap connected,
   2000/2000 iterations, MBAR SE 0.045) and structurally stable once periodic wrapping is accounted for. This
   *strengthens* the rest of this list: a converged calculation missing by 1.478 kcal/mol has a **systematic**
   problem, and replicates cannot address bias.
2. **(free)** Record the admits-zero defect (done, §3) and route the gate amendment for approval. Do not apply it
   unilaterally.
3. **(~one replicate's cost, strictly higher information than a replicate)** Run the **reverse** ternary and
   binary legs of r0. |ΔG_fwd + ΔG_rev| tests systematic error directly; a replicate cannot.
4. **(the real decision) Rescope the calibrator to a signal the method can resolve.** Target ≳2 kcal/mol — not an
   arbitrary number: it is the same ~2.0 kcal/mol margin nr4a3-program-map.md says a useful degradation window requires.
   Calibrating at 0.944 demands resolution the programme does not even need. Two routes that keep a congeneric
   map:
   - a **multi-edge path** through the SMARCA2–VHL series (signal adds linearly, noise as √N) — which also
     finally supplies **cycle closure**; or
   - the reviewer's original high-contrast pair (P1 α 93 → P4 α 1.3 ≈ **+2.53**; → P5 α 0.6 ≈ **+2.99**) reached
     via intermediate congeneric hops instead of one 32–47-atom jump.

---

## 8. ADDENDUM (2026-07-25 PM ET) — the last unmeasured diagnostic is now measured, and the solute RMSD is explained

Two items this document left open are closed. Full detail:
[valb-gate-defect-fix-audit-2026-07-25.md](valb-gate-defect-fix-audit-2026-07-25.md) and
[valb-calibrator-rescope-2026-07-25.md](valb-calibrator-rescope-2026-07-25.md).

**§6's `ligand-only pose RMSD: unmeasured` is measured.** Nothing in the committed artifacts is a topology
file, so the ligand was *derived* from the hybrid System serialized inside the `.nc`: bonded connectivity
(bonds + constraints + the softcore `CustomBondForce`) partitions the 141,968 particles into 4 protein chains
of 2343/1925/1433/1329, 44,860 waters, 248 monatomic ions and **exactly one** ligand-sized molecule of **110
atoms** — a fail-closed identification with one candidate, not a ranked guess. Removing the 51 hydrogens (mass
~3 Da; **HMR is on in this lane**, contrary to what a code comment had asserted) gives **59 heavy atoms**, which
is exactly `wurz-calib-frozen.json → validation.heavy_1 = heavy_4 = 59`, an RDKit count made at freeze time from
the frozen SMILES with nothing to do with this trajectory. The molecule found in the `.nc` is the Wurz
compound-1/4 hybrid, confirmed by a number nobody computed for the purpose.

**Receptor-superposed ligand HEAVY-ATOM pose RMSD, all 12 replicas: max 2.765 Å, median 1.644** against the
4.0 Å threshold; adjacent checkpointed frames (1960 vs 2000) well below it. `ligand_stable_ok: true`,
`mandatory_unmeasured: []`, **`diagnostics_complete: true`** — measured, not assumed (final: GH run
30169056960). *Appendix: an earlier run of the same analysis reported 2.813 / 1.941 Å; that was over all 110
atoms, before the hydrogen mass was measured rather than assumed. The heavy-atom figures above are the quantity
the prereg names.*

Both independent corroborations return **CONSISTENT**: the derived heavy-atom count against the frozen record
(59 = 59), and the ligand identified separately in the ~5 k-particle solvent box against the ~142 k-particle
ternary assembly.

**And §6's "known-incomplete, the cause is unknown" residual tail is explained.** The per-chain breakdown
discriminates it. In replica 8, the ligand's pose RMSD against each protein chain in turn is
**[1.53, 1.50, 12.18, 10.58] Å** — the ligand cannot be in two places, so the two *smallest* chains have moved
~10 Å relative to the two largest, after minimum-image correction. Across replicas the pattern is consistent:
the ligand sits within ~1–3 Å of the two large chains and 2–13 Å from the two small ones. **The peripheral
chains reorient; the ligand does not move.** That accounts for the 10.3 Å whole-solute superposed RMSD with no
artifact invoked — a single global rotation cannot fit a four-chain assembly whose chains move relative to each
other, which is what the metric's own caveat said. *(Chain identity is inferred from size and is not verified
here; by residue count the two small chains are consistent with Elongin B and C, the parts of VCB furthest from
the ligand.)* **This is benign for ΔΔG_coop**: the interface the cooperativity measures — VHL·PROTAC·SMARCA2 —
is the one that stays intact.

**Two defects were found in the course of measuring it, and one was newly introduced by the fix itself**: a
fixed 2.5 Da "heavy atom" cutoff that counted every HMR'd hydrogen as heavy, and a solvent-leg ligand check that
flagged a free PROTAC's conformational change against a 4 Å *pose-collapse* threshold and produced
`technical_failure: true` — which via `_diagnostics_ok()` would have handed valB_mini a **hard FAIL**, i.e.
exactly the defect-#7 failure mode, re-committed. Both fixed; the solvent leg's ligand check is now **not
applicable** rather than failed or unmeasured. Separately, `_diagnostics_ok()`'s last "absent report → True"
path — the surviving instance of §6's signature defect — now returns `None` (not verified).

### Strategic note

nr4a3-program-map.md already concluded (2026-07-24, mechanism-first revision) that the marginal/induced-interface axis
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
