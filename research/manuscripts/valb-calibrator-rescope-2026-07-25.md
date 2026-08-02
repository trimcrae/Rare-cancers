# Rescoping the valB calibrator — both designs, priced, with the decision keyed to the reverse leg

**Date:** 2026-07-25 · **Status:** design + recommendation. **No GPU work is proposed for launch here** — every
number below is a $0 CPU derivation, and the spend decision is trimcrae's.
**Artifacts:** [`valb_rescope_design.py`](../modalities/valb_rescope_design.py) ·
[`valb-rescope-design.json`](../modalities/valb-rescope-design.json) ·
[`valb-gate-audit.json`](../modalities/valb-gate-audit.json) (the power arithmetic this rests on) ·
[`valb_pseries_chem.py`](../modalities/valb_pseries_chem.py) ·
[`valb-pseries-chem.json`](../modalities/valb-pseries-chem.json) (the RCSB mappability check).

> ## ⚠ READ §5a FIRST — THE $0 BLOCKER RAN, AND IT REFUTES §§2–4
>
> Sections 2–4 design the rescope onto the Ciulli SMARCA2–VHL P-series and were written while the ligand
> chemistry was unknown. **It is now known** (GH run 30168578199, RCSB + RDKit MCS in the production mapper's own
> container), and the P-series **cannot carry this calibrator**: 6 of its 10 pairs **change formal charge**, and
> the 4 that do not perturb **58–80 heavy atoms** — against the 2 perturbed atoms of the edge already running.
> **§§2–4 are retained unedited** because their arithmetic is correct and reusable, and because a design refuted
> by its own pre-check is worth showing rather than deleting. **§5a is what actually happened; §8 is the revised
> recommendation and supersedes the one §§2–4 imply.**

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

## 5a. The blocker ran — and the P-series cannot carry this calibrator

Run **30168578199**, $0, on a GitHub runner in `triskit23/ternary-fep` (rdkit + lomap2 + kartograf, i.e. the
production mapper at version parity). All ten pairs, sorted by perturbation:

| edge | heavy A → B | MCS | **perturbed heavy** | charge A → B | verdict |
|---|---|---|---|---|---|
| P1 → P5 | 65 → 71 | 39 | **58** | +1 → +1 | large perturbation |
| P1 → P4 | 65 → 79 | 42 | 60 | +1 → **0** | **CHARGE-CHANGING** |
| P1 → P2 | 65 → 69 | 36 | 62 | +1 → **0** | **CHARGE-CHANGING** |
| P2 → P5 | 69 → 71 | 36 | 68 | 0 → **+1** | **CHARGE-CHANGING** |
| P4 → P5 | 79 → 71 | 39 | 72 | 0 → **+1** | **CHARGE-CHANGING** |
| P1 → P3 | 65 → 79 | 35 | **74** | +1 → +1 | large perturbation |
| P2 → P3 | 69 → 79 | 36 | 76 | 0 → **+1** | **CHARGE-CHANGING** |
| P2 → P4 | 69 → 79 | 36 | 76 | 0 → 0 | large perturbation |
| P3 → P5 | 79 → 71 | 35 | **80** | +1 → +1 | large perturbation |
| P3 → P4 | 79 → 79 | 35 | 88 | +1 → **0** | **CHARGE-CHANGING** |

**Three findings, in order of how much they cost the design.**

1. **The P-series is not a congeneric series in the RBFE sense.** Its MCS is only 35–42 atoms out of 65–79
   heavy, so *half of every molecule* is perturbed. For scale, the edge already running — Wurz cmpd1 → cmpd4 —
   is a **single ring N→CH swap: 2 perturbed heavy atoms**, run over 12 λ-windows. Going to 58 is not a bigger
   version of the same calculation; it is a different regime, needing far more windows (and therefore far more
   than the $9–27 quoted in §2–3) with no assurance of overlap even then. The published α series is a
   *linker/exit-vector design* series — chemically diverse by construction, which is exactly what makes it a
   good SAR paper and a bad alchemical map.
2. **Six of ten pairs change formal charge**, in the pattern P1 **+1**, P2 **0**, P3 **+1**, P4 **0**, P5 **+1**.
   A charge-changing alchemical transformation needs finite-size/Ewald corrections and is a different and much
   more expensive calculation. This kills **P1→P4 (+2.53) outright** — the very edge §3 costed at $9.
3. **What survives is narrower than expected, and it is not what §2 recommended.** The charge-consistent **+1
   subset {P1, P3, P5}** does form a closed triangle — so the closure *topology* of §2 is intact — but its
   edges perturb 74 / 80 / 58 heavy atoms. The two-hop route P1→P3→P5 is therefore **worse than the direct
   P1→P5 on both axes at once**: larger perturbations (74 and 80 vs 58) *and* the √2 SD penalty of §4. §2's
   "maximise the smallest hop" selection rule optimised the wrong quantity, because it ranked triangles on
   **experimental Δα** while the binding constraint turned out to be **chemical distance.**

**What did hold — with one caveat and one new number.** The entry titles confirm these are genuine SMARCA2
ternaries, not SMARCA4:

| system | PDB | CCD | title | **resolution** |
|---|---|---|---|---|
| P1 | 9HYN | A1IYO | *CRYSTAL STRUCTURE OF THE SMARCA2-VCB-COMPLEX WITH PROTAC P1* | 2.37 Å |
| P2 | 7Z77 | IFF | *…compound 6 in complex with the bromodomain of human SMARCA2 and pVHL:ElonginC:ElonginB* | **1.97 Å** |
| P3 | 9HYB | A1IYB | *…WITH PROTAC P3* | 2.84 Å |
| P4 | 9HYO | A1IYN | *…WITH PROTAC P4* | **3.74 Å** |
| P5 | 9HYP | A1IYM | *…WITH PROTAC P5* | 2.2 Å |

So §2's *second* argument — that this panel deletes the homology-model term and lets replicates measure sampling
noise alone — is **correct and remains available** to any future design that can reach these structures. It is
the P-series *ligands* that are unusable as an alchemical map, not the P-series *structures*.

Two honest corrections to that argument, both from this run:

- **P4 (9HYO) is 3.74 Å**, essentially 8G1Q's 3.73 Å. Had P1→P4 been chemically viable (it is not — it changes
  charge), it would **not** have bought the resolution improvement §2 claimed for the panel as a whole. The
  claim holds for P1/P2/P3/P5 and not for P4.
- **The automated `mentions_smarca2` flag returned FALSE for all five entries** and the identity above rests on
  the *titles*. Cause: RCSB polymer-entity descriptions carry the UniProt recommended name — SMARCA2 is
  *"Probable global transcription activator SNF2L2"* — so the gene symbol never appears there, and the check
  only searched descriptions for the literal string. A check that returns False on five true positives is worse
  than no check, since it reads as "these are not SMARCA2 structures". Fixed to search titles as well and to
  match SNF2L2/SNF2L4; **re-run before quoting the flag rather than the titles.**

### The conclusion that follows, and it is the important one

**A ≥2 kcal/mol ternary calibrator that is also a small, charge-neutral, mappable perturbation may simply not
exist in the public literature.** Large cooperativity differences are produced by large chemical changes — that
is *why* they are large. The two requirements are in tension by construction, and the P-series is the best
public candidate the repo had identified.

This does not leave the program stuck, because **cycle closure never needed the experimental answer.** See §8.

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

## 8. REVISED RECOMMENDATION — a **synthetic closure triangle on the anchor ligand**

§5a removes both published options. What it does **not** remove is the instrument, and this is the point the
whole document turns on:

> **Cycle closure needs no experimental measurement whatsoever.** `R = ΔΔG(A→B) + ΔΔG(B→C) − ΔΔG(A→C)` is zero
> for an exact method *whatever the true α values are*. So the ligands in a closure triangle **do not have to
> have measured cooperativity at all** — they only have to be mappable.

That inverts the constraint that §5a just showed is binding. Instead of hunting the literature for compounds
with a large measured Δα *and* a small chemical distance — a pair of requirements in tension by construction —
build the triangle from **small, deliberately chosen perturbations of the anchor ligand itself**, exactly like
the cmpd1→cmpd4 edge that already converged.

### The design

| edge | perturbation | status |
|---|---|---|
| **T1** | Wurz cmpd1 → cmpd4 (ring N→CH, **2 perturbed heavy atoms**) | **ALREADY RUN — this is r0.** Reused, not re-bought |
| **T2** | cmpd4 → cmpd4′ (a second small, charge-neutral single-site change — see the constraint below) | new |
| **T3** | cmpd1 → cmpd4′ (**closes the loop**) | new |

**⚠ cmpd4′ cannot be another pyridine→benzene swap, and this was checked rather than assumed.**
`wurz_calib_freeze._pyridine_variants` enumerates every aromatic six-membered one-nitrogen ring in cmpd1 and
finds **exactly one** (`n_pyridine_rings_in_cmpd1: 1`, in the frozen record) — the pyridine-4-carbonyl linker,
which is the ring cmpd4 already consumes. The other N-heterocycles are a five-membered thiazole and a
two-nitrogen aminopyridazine, neither of which is a pyridine. So cmpd4′ must come from a *different* transform.
Concrete candidates, all ≤ 2 perturbed heavy atoms and charge-neutral:

- **aminopyridazine ring N → CH** (a second single-element swap, on a different ring — closest in kind to the
  transform already validated);
- **thiazole 4-methyl → H** (one heavy atom);
- **tert-butyl → isopropyl** (one heavy atom);
- **2-hydroxyphenyl → phenyl** (one heavy atom).

**What must NOT be touched:** the *trans*-4-hydroxyproline hydroxyl, which is the VHL anchor. Removing it would
abolish VHL engagement, and a leg whose ligand does not stay bound will not converge — the closure would then be
measuring a dissociation, not a systematic error. (Thermodynamically a closure identity holds for any ligands;
practically it needs three legs that each converge.) `_endpoint_pose` already builds derived analogues from
cmpd1's crystal pose, which is exactly how cmpd4 is handled today, so the machinery carries over unchanged.

`R = ΔΔG_coop(T1) + ΔΔG_coop(T2) − ΔΔG_coop(T3)`, expected **0**.

Why this is better than either published option on every axis that matters:

- **It reuses r0.** The triangle costs **2 new edges**, not 3 — the leg already paid for becomes one side of it.
- **Every perturbation is the size that already converged.** No new convergence risk, no window-count blow-up,
  no charge correction. §5a's failure mode cannot occur.
- **It needs no α, so the literature constraint vanishes.** cmpd4 is *already* a derived compound (the frozen
  record calls it "DERIVED (no separate crystal)"), so a second derived analogue is the same move again, and
  `ternary_calib_epimer_freeze.py` / `wurz_calib_freeze.py` already implement the machinery for deriving and
  validating one.
- **It measures the resolution floor directly.** |R| *is* the number "this workflow resolves ΔΔG_coop
  differences of ≥ X and not below", obtained without assuming any experiment is right.
- **It discriminates the branches of §6 by itself**, so it is worth buying under either.

**Cost:** 2 edges × 2 legs (ternary + binary; the solvent morph cancels in ΔΔG_coop) ≈ **43 ref GPU-h ≈ $5.9**
at n = 1 (range $2.1–15); **~$17.6** at n = 3 (range $6.3–44). *Cheaper than the single-edge design already on
the ladder*, because r0 is reused.

**What it is NOT, stated plainly:** a closure triangle measures **internal consistency and systematic path
error**. It is **not** an accuracy control — it cannot tell you the cycle gets the right answer, only that it
gets a *self-consistent* one. **The known-answer accuracy requirement therefore remains OPEN**, and §5a is the
honest reason why: the public literature may not contain a ternary edge that is simultaneously large-signal and
mappable. That is a finding to report in the paper, not a gap to paper over.

### Ordered actions

1. **✅ done, $0** — the RCSB mappability check (§5a). It refuted §§2–4 before a dollar was spent, which is what
   a $0 pre-gate is for.
2. **$0, next** — derive and validate 1–2 candidate cmpd4′ analogues through the existing freeze machinery, and
   confirm with the same RCSB/RDKit path that each is ≤ ~4 perturbed heavy atoms and charge-neutral against
   **both** cmpd1 and cmpd4. Only then is the triangle a plan rather than a sketch.
3. **$0, worth doing regardless** — fetch the Wurz 2023 SI α table. If that paper's own series contains a
   *congeneric* pair with a larger Δα than 12.8→2.6, it is the one known-answer option §5a did not test, and it
   would come with a matching crystal structure. Cheap, and it is the only remaining route to a real accuracy
   control.
4. **When the reverse leg lands, read the branch (§6).** Branch B → fix the protocol on the edge already paid
   for. Branch A → buy the triangle.
5. **Under branch A, buy the closure triangle at n = 1 first (~$5.9).** Abortable before any replicate spend,
   and it returns the resolution floor on its own.
6. **Do not** buy the P-series edges (§5a), the hopped routes (§4), or sequential stopping on this ladder (§7).

**The deliverable to aim at is the measured resolution floor, not a PASS.** A rigorous statement that "this
workflow resolves induced-interface ΔΔG_coop differences of ≥ X kcal/mol and not below" is honest-limits
reporting of exactly the kind the North Star calls for, it is what the paper needs in order to say what the
ternary numbers can support, and — unlike a PASS — **the closure triangle produces it whether the calibration
succeeds or fails.** After §5a it is also the *only* one of the two that the available chemistry can deliver.

---

## 8a. Exact `nr4a3-program-map.md` deltas (this lane does not edit that file)

**(1) RUNG 2 → Validation B-mini → "Recommended next steps (spend order)", item 4.** Replace the current text —
*"rescope the calibrator to a ≳2 kcal/mol signal … via a multi-edge congeneric path … or the high-contrast
P1→P4/P5 pair (+2.53 / +2.99) reached through intermediate hops"* — with:

> **(4) THE REAL DECISION — rescope, but NOT onto the P-series. Both published options are dead, checked for $0
> before a dollar was spent (GH run 30168578199, RCSB + RDKit MCS in the production mapper's own container;
> [valb-pseries-chem.json](research/modalities/valb-pseries-chem.json)).** 6 of the 10 Ciulli P-series pairs
> **change formal charge** (P1 +1, P2 0, P3 +1, P4 0, P5 +1) — which kills **P1→P4 (+2.53)** outright — and the
> 4 that do not perturb **58–80 heavy atoms** against the **2** of the edge already running (MCS 35–42 of 65–79
> heavy: half of every molecule). It is a linker/exit-vector *design* series, chemically diverse by
> construction: a good SAR paper and a bad alchemical map. **General conclusion: a ≥2 kcal/mol ternary
> calibrator that is ALSO small, charge-neutral and mappable may not exist in the public literature — large
> cooperativity differences are produced by large chemical changes, so the two requirements fight each other.**
> **What replaces it: a SYNTHETIC CLOSURE TRIANGLE on the anchor ligand**, because closure needs no experimental
> measurement at all (`R = ΔΔG(A→B)+ΔΔG(B→C)−ΔΔG(A→C)` is zero for an exact method whatever the true α values
> are). T1 = cmpd1→cmpd4 **is r0, reused not re-bought**; T2 = cmpd4→cmpd4′ and T3 = cmpd1→cmpd4′ are new, each
> a ≤2-heavy-atom charge-neutral change. **2 new edges ≈ $5.9 at n=1 ($2.1–15), ≈$17.6 at n=3** — cheaper than
> the single-edge design already on the ladder. ⚠ cmpd4′ cannot be a second pyridine→benzene swap
> (`n_pyridine_rings_in_cmpd1: 1`); candidates are the aminopyridazine N→CH, thiazole 4-methyl→H,
> *tert*-butyl→isopropyl, 2-hydroxyphenyl→phenyl — never the *trans*-4-hydroxyproline OH, which is the VHL
> anchor. **Honest limit: closure measures internal consistency and systematic path error, NOT accuracy. The
> known-answer accuracy requirement stays OPEN.** Design:
> [valb-calibrator-rescope-2026-07-25.md](research/manuscripts/valb-calibrator-rescope-2026-07-25.md).

**(2) Same bullet — replace the "Still unmeasured: the ligand-only pose RMSD … `diagnostics_complete: false`
says so"** sentence with:

> **✅ MEASURED (GH runs 30167976061 → 30168343299): `diagnostics_complete: TRUE` on the ternary leg.** The
> ligand was *derived* from the hybrid System in the `.nc` (no topology file is committed): one 110-atom
> component against chains of 2343/1925/1433/1329, 44,860 waters and 248 ions — a fail-closed identification
> with exactly one candidate. **HMR is on in this lane** (H at ~3 Da), so 110 − 51 H = **59 heavy**, which is
> exactly `wurz-calib-frozen.json → validation.heavy_1 = heavy_4 = 59` — **CONSISTENT**, as is the ligand
> identified independently in the solvent box vs the ternary assembly. **Receptor-superposed ligand heavy-atom
> pose RMSD over all 12 replicas: max 2.765 Å, median 1.644** (threshold 4.0; final run 30169056960).
> The 10.3 Å whole-solute RMSD is now **explained, not excused**: per-chain, the ligand sits ~1–3 Å from
> the two large chains and 2–13 Å from the two small ones, so the *peripheral chains reorient by ~10 Å while the
> ligand does not move* — benign for ΔΔG_coop, whose interface is the one that stays intact.

**(3) Add to the same bullet, after the seven-defects sentence** (the count is now higher and two were
self-inflicted, which is the point):

> **★ THREE MORE DEFECTS, 2026-07-25 PM — and two were introduced by the repair itself.** (8) a fixed 2.5 Da
> "heavy atom" cutoff that counted every **HMR'd hydrogen as heavy** (the hydrogen mass is now *measured* per
> system from the molecular graph, correct at any HMR factor); (9) a solvent-leg ligand check that judged a free
> PROTAC's conformational change against a 4 Å **pose-collapse** threshold and returned `technical_failure:
> true` — which via `_diagnostics_ok()` would have handed valB_mini a **hard FAIL**, i.e. defect #7's exact
> failure mode re-committed eight hours later (now **not applicable**, a third state distinct from failed and
> unmeasured); (10) `_diagnostics_ok()`'s surviving **"absent report → True"** path, the last instance of this
> lane's signature defect, now `None` (not verified). A Kabsch convention error was also caught *by its own
> regression test* before shipping. **The rate at which this lane produces measure-nothing defects is itself a
> finding**, and it is the argument for spending on **independent** instruments — reverse legs, cycle closure —
> rather than more replicates through the same machinery.

**(4) The in-flight board's LANE 5 row** can be marked complete: `diagnostics_complete` closed honestly, the
gate defect independently audited (already-applied; ratification block ready to route), both rescope options
designed *and one of them refuted by its own $0 pre-gate*, with a replacement design and the rev-leg-keyed
decision tree in place.

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
