# Rescoping the valB calibrator — both designs, priced, with the decision keyed to the reverse leg

**Date:** 2026-07-25 · **Status:** design + recommendation. **No GPU work is proposed for launch here** — every
number below is a $0 CPU derivation, and the spend decision is trimcrae's.
**Artifacts:** [`valb_rescope_design.py`](../modalities/valb_rescope_design.py) ·
[`valb-rescope-design.json`](../modalities/valb-rescope-design.json) ·
[`valb-gate-audit.json`](../modalities/valb-gate-audit.json) (the power arithmetic this rests on).

---

## 1. Why the calibrator is the thing to change

Three measured facts, none of them opinions:

1. **r0 is a converged measurement that misses by 1.478 kcal/mol.** MBAR SE 0.045, ΔG(t) flat to 0.0023,
   overlap connected, 2000/2000 iterations. The miss is **~33× the statistical error**, so it is systematic, and
   replicates shrink variance, not bias.
2. **The gate's accept band is [+0.472, +1.944] kcal/mol** against a +0.944 target — a factor of **4.1**. The
   preregistered ±1.0 accuracy margin is *larger than the signal being calibrated*, so even a PASS would certify
   the cycle only to within a factor of four. (`valb-gate-audit.json → D_acceptance_band`.)
3. **P(PASS) has a ceiling of `P(sample SD ≤ 0.75)`**, which at n = 5 is exactly `P(χ²₄ ≤ 4(0.75/σ)²)` —
   **66.8 % at σ = 0.7** — independent of the target and of how accurate the method is. Analytic and Monte Carlo
   agree to 0.15 %. (`F_power_ceiling`.)

Sweeping the target at the frozen ±1.0 margin makes the shape of the problem explicit:

| target (kcal/mol) | accept band ÷ target | P(PASS) accurate, σ=0.7 | P(PASS) null |
|---|---|---|---|
| 0.5 | 4.00 | 21.9 % | 2.3 % |
| **0.944 (current)** | 2.12 | **52.4 %** | 1.7 % |
| 1.25 | 1.60 | 63.3 % | 0.95 % |
| 1.5 | 1.33 | 66.1 % | 0.45 % |
| **2.0** | 1.00 | **66.8 %** | **0.07 %** |
| 2.53 | 0.79 | 66.8 % | **0.00 %** |
| 2.99 | 0.67 | 66.8 % | **0.00 %** |
| 3.5 | 0.57 | 66.8 % | 0.00 % |

**2.0 kcal/mol is a knee, not a round number.** Below it the accuracy margin binds and both axes are bad; at it
the null is excluded outright and power has reached its ceiling; above it nothing further is bought. STRATEGY
argued "≳2 kcal/mol" by analogy to the degradation window; this derives the same number from the gate itself.

> **The one lever left above 2 kcal/mol is the between-replicate SD.** Any design choice that raises SD is a
> direct loss of power no matter how big the signal. §4 is where that bites.

---

## 2. Design (i) — a multi-edge congeneric network, which finally supplies **cycle closure**

**What is different in kind.** Every check this lane currently has either needs the experimental answer
(accuracy vs α) or measures precision only (replicate SD, MBAR overlap, fwd/rev). **Cycle closure needs
neither.** For a closed path the residual

```
R = ΔΔG_coop(A→B) + ΔΔG_coop(B→C) − ΔΔG_coop(A→C)
```

is **identically zero for an exact method regardless of what the experimental α values are.** A nonzero R is
proof of systematic error with nothing else assumed — the instrument this program has never had (no reverse
legs existed until today, no redundant edge, therefore no closure; reviewer Req 7 already flagged it).

It also produces the **measured resolution floor** STRATEGY says is the honest deliverable: |R| is a
self-contained statement of what the ΔΔG_coop cycle can and cannot resolve, **and it is publishable whether or
not the calibration passes.**

### Edge list (recommended triangle)

Ciulli SMARCA2–VHL P-series, α_TR-FRET from
[`nr4a3-ternary-coop-prereg.json`](../modalities/nr4a3-ternary-coop-prereg.json) (each primary-source verified;
Nat Commun 2025 PMC12480974 Supp. Table 1, SI archived + checksummed):

| edge | from → to | PDBs | target ΔΔG_coop |
|---|---|---|---|
| E1 | P1 (α 93) → P3 (α 5.0) | 9HYN → 9HYB | **+1.732** |
| E2 | P3 (α 5.0) → P5 (α 0.6) | 9HYB → 9HYP | **+1.256** |
| E3 | P1 → P5 **(closes the loop)** | 9HYN → 9HYP | **+2.988** |

Selection rule: **maximise the smallest hop**, because the weakest hop decides how much of the closure residual
is signal rather than noise. P1→P3→P5 wins (min hop 1.256); the runner-up is P1→P2→P5 (1.850 / 1.139, min
1.139). If the P1→P5 direct edge turns out unmappable, the same triangle can close through P4 instead
(P1→P3→P4 + direct P1→P4, min hop 0.798, direct +2.53).

### A second, larger advantage that has nothing to do with the signal

**The P-series has five solved SMARCA2–VHL ternary structures.** The current valB edge does not: 8G1Q is a
3.73 Å **SMARCA4** structure with the BD sequence substituted to SMARCA2 and relaxed — recorded as a valB_mini
limitation, and the reason ternary seed *s* uses the *s%n*-th independently relaxed model, so **replicate spread
today conflates sampling noise with homology-model sensitivity.** Moving to the P-series:

- deletes the homology-model term from the systematic budget entirely; and
- makes replicates measure **sampling noise alone** — which, per §1, is the *only* remaining lever on power once
  the target clears 2 kcal/mol.

These compound. It is not "a bigger signal"; it is a bigger signal **and** a cleaner SD **and** one fewer
candidate cause for the 1.478 kcal/mol systematic.

### Cost (Vast RTX 4090, $0.137 per reference GPU-hour)

Basis: `vast_cost_model.LADDER_REFERENCE_GPU_H["valB_mini (1 ternary edge, 3 replicas)"] = 56–72` ref GPU-h,
i.e. **~10.7 ref GPU-h per leg** (2400 iterations × ~16 s/iter measured on a Vast 4090).

| variant | legs (ternary / binary / solvent) | ref GPU-h | **cost (mid)** | range |
|---|---|---|---|---|
| **i-scout, n = 1** — closure only, no replicate SD | 3 / 3 / 3 | 65.7 | **$9.0** | $3.2–22 |
| **i-full, n = 3** — closure + replicate SD | 9 / 9 / 9 | 196.5 | **$26.9** | $9.7–67 |
| i-extended, n = 5 | 15 / 15 / 15 | 327 | $44.9 | $16–112 |

**On the cancellation identity, applied honestly.** STRATEGY's identity — *"the binary and solvent legs are
paralogue-independent, so a panel is N ternary legs + 1 shared binary + 1 shared solvent, not N edges"* — is
about **one ligand pair against several targets**. It does **not** apply inside a congeneric network on a single
target, where every edge is a different alchemical transformation and needs its own binary leg. Claiming the
sharing here would underprice these designs by ~2×, so it is not claimed. What the identity *does* buy is
forward-looking: the binary legs are target-independent, so if any of these edges is later replicated against a
second known-answer system (VHL–BRD4), **its binary legs transfer unchanged.**

**i-scout at ~$9 is the recommended first purchase**: one replicate of each of three edges buys the closure
residual — the reference-free systematic detector — for the price of the *existing* single-edge design, and it
is abortable before the replicate spend.

---

## 3. Design (ii) — the high-contrast pair, direct or hopped

| route | hops | target | legs | **cost n=3** |
|---|---|---|---|---|
| P1 → P4 **direct** | 1 | +2.530 | 9 | **$9.0** |
| P1 → P5 **direct** | 1 | +2.988 | 9 | **$9.0** |
| P1 → P2 → P4 hopped | 2 | +2.530 | 18 | $17.9 |
| P1 → P3 → P4 hopped | 2 | +2.530 | 18 | $17.9 |
| P1 → P2 → P5 hopped | 2 | +2.988 | 18 | $17.9 |
| P1 → P3 → P5 hopped | 2 | +2.988 | 18 | $17.9 |

The direct route is the cheapest design on the table and its entire risk is chemical: a 93 → 0.6 cooperativity
span is a large linker/exit-vector change, and **an edge LOMAP/Kartograf cannot map does not converge at any
price.**

---

## 4. The finding that reorders the options: **hops can be a net loss**

Signal adds **linearly** across hops; replicate SD adds in **quadrature**. Since §1 shows the gate is
SD-limited above 2 kcal/mol, a 2-hop route to +2.53 is evaluated at an effective SD of `√2 × σ_hop`:

| design | target | per-edge SD | effective SD | **P(PASS) accurate** | P(PASS) null |
|---|---|---|---|---|---|
| current valB (1 hop) | 0.944 | 0.7 | 0.70 | 52.2 % | 1.8 % |
| **P1→P4 direct (1 hop)** | 2.530 | 0.7 | 0.70 | **66.5 %** | **0.0 %** |
| **P1→P5 direct (1 hop)** | 2.988 | 0.7 | 0.70 | **66.5 %** | **0.0 %** |
| P1→P3→P5 hopped (2 hops) | 2.988 | 0.7 | 0.99 | **30.8 %** | 0.0 % |
| P1→P2→P4 hopped (2 hops) | 2.530 | 0.7 | 0.99 | **30.8 %** | 0.01 % |
| P1→P3→P5 hopped (2 hops) | 2.988 | 0.5 | 0.71 | 65.5 % | 0.0 % |
| P1→P3→P5 hopped (2 hops) | 2.988 | 0.3 | 0.42 | 98.6 % | 0.0 % |

**Read the 4th row against the 1st.** A 2-hop route to a **3× larger signal** has a pass probability of 30.8 %
— *lower than the current 0.944 kcal/mol edge's 52.2 %* — at equal per-edge noise. Hops are justified by
**unmappability**, never by the bigger endpoint separation. They pay only if each hop converges better than the
direct edge would: at 2 hops, per-hop SD must fall below **~0.71×** the direct edge's to break even.

Design (i)'s triangle is subject to the same arithmetic for its *derived* path sum, but it does not depend on
it: **the closure residual R is computed from the three edges directly and is informative at any SD**, because
its expected value is zero by construction rather than by hypothesis.

---

## 5. The blocker, and it is $0 to clear

**Nothing above is executable until the P-series ligand chemistry is in hand:** are the pairs congeneric and
mappable, and is net charge conserved across each edge? An unmappable edge does not converge, and a
charge-changing edge needs a different and much more expensive treatment. Until this returns, every edge above
is a **candidate**, and `ligand_ccd` is `null` for all five systems in the prereg.

The fix is a **$0 CI job**: fetch the bound-ligand chemistry for 9HYN / 7Z77 / 9HYB / 9HYO / 9HYP from RCSB on a
GitHub runner (the dev sandbox's egress proxy blocks RCSB), then run RDKit MCS + LOMAP mapping inside the
pre-baked `triskit23/ternary-fep` image — which already carries **rdkit + lomap2 + kartograf**, i.e. the same
mapper the production edge would use, at version parity. It also confirms, rather than assumes, that these are
genuinely SMARCA2 (not SMARCA4) ternaries. **This should run before any rescope spend is authorised**, and it
costs nothing.

---

## 6. The decision tree, keyed to the reverse leg now in flight

The preregistered antisymmetry check `|ΔG_fwd + ΔG_rev|` is `null` on all three legs and is being measured right
now by a sibling session. **It changes which design is correct, so both branches are specified in advance.**

### Branch A — `|ΔG_fwd + ΔG_rev| ≲ 0.3 kcal/mol` (no hysteresis)

The alchemical path is internally consistent and λ-sampling is adequate. The 1.478 systematic is therefore
**not** a path artefact; it lives in the **model** (SMARCA4→SMARCA2 homology substitution, NAGL charges, force
field, protonation) or in the **reference data** (α_SPR is an *apparent* cooperativity, not a Kd-derived
thermodynamic one).

→ **RESCOPE, and design (i) is strictly dominant**, because it attacks both candidate causes at once: the
P-series removes the homology-model term outright, and the closure residual tests the remaining systematic
*without requiring the reference data to be right.*

### Branch B — `|ΔG_fwd + ΔG_rev| ≳ 1.0 kcal/mol` (real hysteresis)

A slow degree of freedom orthogonal to λ — an interface substate replica exchange does not traverse — despite
every MBAR diagnostic reading clean. **One diagnostic already leans this way: replica mixing 0.8915 against a
0.90 ceiling, recorded as MARGINAL.**

→ **DO NOT RESCOPE YET.** A larger target measured through a hysteretic path is still wrong; buying a new
calibrator would buy a better-looking wrong number. **The design must change first, and it can be tested on the
edge already paid for** — more λ-windows across the 0.109 bottleneck at pair 4–5, a softer softcore schedule,
longer pre-equilibration, or interface-aware enhanced sampling. Only once the antisymmetry is small does the
rescope become the right spend.

### True under both branches

**The closure network is worth buying either way**, because the closure residual is the instrument that tells
branch A from branch B *for any future edge* without paying for a reverse leg every time. Under branch B it is
bought after the protocol fix rather than before it.

---

## 7. Anytime-valid sequential stopping — evaluated, and it **does not pay here**

`adaptive_certify.py` and `adaptive_allocator.py` are built and unit-tested but not wired into the ternary
ladder. The proposal was to use `anytime_upper_bound` as a **futility stop**: if the anytime-valid upper bound
on ΔΔG_coop is already below `target − 1.0`, the accuracy criterion is unreachable and the remaining replicates
are wasted money. It stays honest under repeated looks and data-dependent stopping, which a fixed-n gate peeked
at repeatedly does not; and it can only ever *reduce* spend, never convert a non-PASS into a PASS, so it needs
no amendment to the frozen rule.

**Measured, it saves 0.8–2.6 %, not the ~20–25 % the allocation design quotes:**

| scenario | replicate SD | mean replicates bought | futility fired | **saving** |
|---|---|---|---|---|
| r0 is representative (μ = −0.534) | 0.5 | 4.87 of 5 | 16.7 % | **2.6 %** |
| r0 is representative | 0.7 | 4.96 of 5 | 5.7 % | **0.8 %** |
| null (μ = 0) | 0.5 / 0.7 | 5.00 | 0.1 % | **0.0 %** |
| method exactly right | 0.5 / 0.7 | 5.00 | 0.0 % | **0.0 %** |

**Why:** an anytime-valid bound must be wide enough to survive *every* stopping time, so at n = 2–4 with σ ≈
0.5–0.7 it almost never crosses the futility bar before n = 5 arrives anyway. **Sequential methods need a long
horizon and a 5-replicate ladder does not have one.** The ~20–25 % figure in
`nr4a3-adaptive-allocation-design.md` is for the *prospective* campaign — many candidates × many rungs, where
futility kills prune survivors before the expensive rungs — and it does not transfer.

**Recommendation: do NOT wire it into the valB replicate ladder.** It is engineering effort (free) spent for a
~1 % compute saving on a lane whose problem is bias, not budget. Keep it for the prospective matrix, where the
horizon is long enough for it to earn its keep.

---

## 8. Recommendation

1. **Now, $0 — run the RCSB ligand-chemistry fetch** (§5). It gates everything and costs nothing. Nothing below
   should be authorised before it returns.
2. **When the reverse leg lands, read the branch (§6).** Branch B → fix the protocol on the edge already paid
   for; do not buy a new calibrator. Branch A → proceed.
3. **Under branch A, buy design (i) i-scout: three edges × one replicate, ~$9 (range $3.2–22).** It costs what
   the *existing* single-edge design costs and returns something that design structurally cannot: a
   reference-free systematic-error detector, and the measured resolution floor. It is abortable before the
   replicate spend.
4. **Only then decide on replicates (~$27 for n = 3).** If the closure residual is small, the systematic is in
   the model or reference data and replicates are worth buying; if it is large, replicates are again the wrong
   instrument and the money goes to the protocol.
5. **Do not buy the hopped routes of design (ii)** unless the RCSB fetch shows the direct edges are unmappable
   — §4 shows they *lower* the pass probability at equal per-edge noise.
6. **Do not wire sequential stopping into this ladder** (§7).

**The deliverable to aim at is the measured resolution floor, not a PASS.** A rigorous statement that "this
workflow resolves induced-interface ΔΔG_coop differences of ≥ X kcal/mol and not below" is honest-limits
reporting of exactly the kind the North Star calls for, it is what the paper needs in order to say what the
ternary numbers can support, and — unlike a PASS — **the closure network produces it whether the calibration
succeeds or fails.**

---

## 9. Honest-scope notes that must travel with any result from this

- **Val B is the NAGL lane's known-answer accuracy control.** OpenFE's published ~1.7 kcal/mol RBFE accuracy was
  measured on **am1bcc** and does **not** transfer to the ternary lane. No ternary number in this program may
  cite it.
- **The P-series α values are α_TR-FRET** (an *apparent* cooperativity, an IC50 ratio) while the current valB
  target is **α_SPR**. Each *edge* is same-assay, which is what a relative calibration requires — but a P-series
  result must never be reported as continuous with the Wurz number.
- **Replicate spread on the current edge is not pure sampling noise**, because ternary seed *s* uses the
  *s%n*-th relaxed SMARCA2 model. Any SD quoted from the existing lane conflates sampling with homology-model
  sensitivity. The P-series designs do not have this defect.
