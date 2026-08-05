---
id: DOC-VALB-CLOSURE-TRIANGLE-PREGATE-2026-07-25
title: The valB closure triangle, pre-gated for $0 — what it can prove, what it costs, and the topology that should replace it
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `manuscript` from its location under research/manuscripts/.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# The valB closure triangle, pre-gated for $0 — what it can prove, what it costs, and the topology that should replace it

**Date:** 2026-07-25 · **Status:** $0 pre-gate + costed recommendation. **No GPU work is proposed for launch
here** — every number below is a CPU/CI derivation and the spend decision is trimcrae's.
> ⛔ **THIS PRE-GATE IS MOOT — THE SPEND IT WAS GATING RAN AND THE LANE CLOSED ON 2026-07-30.**
> A pre-gate answers *"should we buy this?"*. That question was settled by events: **LANE 9/20 closed with
> all four legs landed at 5:11 PM ET on 30 July and `R` computed** —
> [`valb-triangle-reduction.json`](../modalities/valb-triangle-reduction.json), off every host, struck
> through in the roadmap's own lane table. Separately, the triangle was **REFUTED as a diagnostic** for the
> wrong-sign miss (`V5`): it returns a clean `R` whether or not the program's actual problem exists.
> ⚠ Not everything here is dead — the roadmap is explicit that *"the triangle still yields a path-error
> floor and an endpoint-consistency check; the **diagnosis** is what died"*. What is dead is **the decision
> this document exists to inform.**
>
> ⚠ **SO `valb-triangle-chem.json` IS NOT A GAP TO FILL — THE CITATION IS WITHDRAWN.** It would have been
> the production-mapper chemistry check *before* buying the T2/T3 edges. Those edges were bought and run.
> Producing the artifact now would grade a design against a spend that already happened and reported.
>
> ⛔ **AND THE ATTEMPT TO PRODUCE IT ON 2026-08-05 WAS A MISTAKE, RECORDED HERE RATHER THAN QUIETLY
> DROPPED.** Run [31017061570](https://github.com/trimcrae/Rare-cancers/actions/runs/31017061570) spent
> **88.5 min** of CI on the mapper and was cancelled at its 90-minute timeout. It was launched to close a
> baselined broken link **without first checking whether the thing the link gated was still live** — the
> roadmap said, in a struck-through row, that it was not. The one useful by-product is a measurement of
> what this gate would cost if anyone ever needed it again: **~5–29 min per edge**, so hours for 17 edges,
> against the ~40 s per edge its workflow comment had assumed.
>
> ⚠ **The `⚠ DEGENERATE MAP` the run reported on the closing edge is NOT a finding and must not be
> carried forward.** Its own message names the likely cause as the mapper's 300 s MCS budget rather than
> the chemistry, and the edge it concerns has since been run for real. **Nothing in this document may be
> re-graded on it, and it is not a reason to re-run anything.**

**Artifacts:** [`valb_triangle_chem.py`](../modalities/valb_triangle_chem.py) ·
[`valb-triangle-chem.json`](../modalities/valb-triangle-chem.json) (production-mapper chemistry gate, run in
`triskit23/ternary-fep`) · [`valb_triangle_closure.py`](../modalities/valb_triangle_closure.py) ·
[`valb-triangle-closure.json`](../modalities/valb-triangle-closure.json) ·
[`tests/test_valb_triangle_closure.py`](../modalities/tests/test_valb_triangle_closure.py) (18 tests — every
claim below that is arithmetic is asserted there, not merely written here).

**What this gates.** [`valb-calibrator-rescope-2026-07-25.md`](valb-calibrator-rescope-2026-07-25.md) §8
proposes a synthetic closure triangle on the anchor ligand to replace the P-series rescope that its own $0
pre-gate refuted. This is the same treatment applied to the replacement: test the design's claims against real
chemistry and real arithmetic **before** any dollar is spent.

---

## 0. Summary

| the design's claim | verdict | evidence |
|---|---|---|
| The triangle closes as a thermodynamic cycle with T1 = r0 reused | **CONFIRMED** | §1 — identity, unit-tested on random states |
| T2 and T3 are each **≤2-heavy-atom** edges | **REFUTED** for all four named candidates — **T3 is a DOUBLE perturbation** | §2 |
| "the machinery carries over unchanged" | **REFUTED** — the engine has exactly one hard-coded pose mutation | §2 |
| It "attacks both candidate causes" of r0's systematic | **REFUTED** — closure is *provably blind* to every cause branch A names | §3 |
| It is "worth buying under **either** branch" | **NOT SUPPORTED AS STATED** — but there is a real, narrower reason to buy it | §4 |
| The cancellation identity does not apply | **CONFIRMED** | §5 |
| ≈ $5.9 at n=1, ≈ $17.6 at n=3 | **≈ $6.8 and ≈ $27.3** — three corrections, the largest is *not* the iteration basis | §6 |

**Bottom line.** The triangle is **ADMITTED, but not as designed and not as the next purchase.** Its named
topology carries a defect the repo's own perturbation-map invariant forbids; a different topology (§2, the
**aza-scan at the linker ring**) removes that defect at no extra cost and is strictly better on every axis.
Its value proposition should be restated: it is **not** a diagnosis of r0 and **not** an accuracy control, it
is a detector for one specific error class that the reverse leg structurally cannot see (§4). And a **$1.31
solvent-only pre-scout** (§7) should be bought before any ternary leg, because it can falsify the triangle's
machinery for ~19 % of the price.

---

## 1. The cycle closes, and r0 enters unaltered

Sign convention is `ternary_coop.ddg_coop`, already verified there against synthetic K_D pairs:

```
ddG_coop(A→B) = ddG_alch,ternary(A→B) − ddG_alch,binary(A→B) = dG_coop(B) − dG_coop(A)
```

so `ddG_coop` is the **difference of a state function** and every oriented cycle telescopes to exactly zero —
with no reference to any measured α. With

| edge | orientation | coefficient | status |
|---|---|---|---|
| T1 | cmpd1 → cmpd4 | **+1** | **already run — this is r0, ΔΔG_coop = −0.534** |
| T2 | cmpd4 → cmpd4′ | +1 | new |
| T3 | cmpd1 → cmpd4′ | **−1** | new, closes the loop |

`R = ΔΔG_coop(T1) + ΔΔG_coop(T2) − ΔΔG_coop(T3) ≡ 0`. r0 measured cmpd1 → cmpd4 **forward**, which is the
orientation the triangle needs at coefficient +1, so r0 is genuinely reused rather than re-bought and no sign
flip is involved. Verified on 500 random state assignments.

### 1a. R decomposes, and reporting R alone is strictly weaker — a free improvement

Because `ΔΔG_coop = ΔG_ternary − ΔG_binary`,

```
R  =  [ΔG_t(T1) + ΔG_t(T2) − ΔG_t(T3)]  −  [ΔG_b(T1) + ΔG_b(T2) − ΔG_b(T3)]  =  R_ternary − R_binary
```

and **each of `R_ternary` and `R_binary` is itself a closed cycle in its own environment, separately zero for
an exact method.** Therefore **`R ≈ 0` does not imply the cycle is consistent**: two large closures can cancel.
Both come from the *same six legs at zero extra cost*, so there is no reason to report only `R`. If solvent
legs are run, `R_solvent` is a third independent closure. **Recommendation: report `R_ternary` and `R_binary`
separately, always.**

### 1b. A constraint the design does not state, and without it R is not a closure residual

Ternary seed *s* selects the *s % n*-th independently relaxed SMARCA2 model. **If T1, T2 and T3 run at
different seeds they are computed on different Hamiltonians**, the three edges no longer share endpoint states,
the telescoping fails, and |R| becomes a measure of homology-model sensitivity rather than of method
consistency. r0 is seed 0, so **T2 and T3 must be seed 0.** (Side benefit: a same-seed triangle removes the
homology-model term from R's noise — see §3a.)

---

## 2. The chemistry gate — T3 is a double perturbation, and a better topology exists

Run in `docker.io/triskit23/ternary-fep` (rdkit + openfe + lomap2 + kartograf), i.e. the **production mapper at
version parity**: `nr4a3_rbfe._mapping(prefer_element_change=True)` → `LomapAtomMapper(time=20, threed=False)`,
the function `protocol_signature` names as `lomap_prefer_element_change`. rdFMCS settings are copied from
`valb_pseries_chem.py` so perturbed-atom counts are directly comparable to the **58–80** that refuted the
P-series and the **2** of the edge already running. The harness first **re-derives cmpd4 from cmpd1** and
checks it against `wurz-calib-frozen.json`, failing closed if it cannot.

*(Per-candidate numbers: `valb-triangle-chem.json`. The structural findings below are properties of the
molecule and the topology, and hold independently of those numbers.)*

### 2a. The structural defect: the closing edge carries both transforms

cmpd1's frozen SMILES resolves into: a *trans*-4-hydroxyproline (the **VHL anchor — off-limits**), a
tert-leucine *tert*-butyl, a 4-methylthiazole cap, the **pyridine-4-carbonyl linker** (the ring T1 already
consumes), a piperazine, an aminopyridazine (the warhead's acetyl-lysine mimic) and a 2-hydroxyphenyl.

All four candidates the design names — aminopyridazine N→CH, thiazole 4-Me→H, *t*Bu→*i*Pr, phenol OH→H — sit at
a site **different from the linker**. With three vertices and two different single-site transforms X (site 1)
and Y (site 2), the closing edge cmpd1 → cmpd4′ necessarily carries **both**:

```
perturbed(T3)  =  perturbed(T1)  +  perturbed(T2)          (the sites are independent, so it is exactly additive)
```

So **T3 is a double mutation** — and the repo's own perturbation-map design forbids exactly that, *specifically
for closing edges*. `rbfe_map.py` states the rule twice: *"NO cross-class double-mutation edges (two
simultaneous changes break common-mode)"*, and — directly on point — on the cycle-closure edges themselves,
*"Each closing edge is itself a SINGLE-site change (not a double mutation)."* `validate_map()` asserts
`single_site` on every edge. The design's claim that "T2/T3 are new ≤2-heavy-atom, charge-neutral edges" is
therefore **wrong for T3 in every named case**, as is "every perturbation is the size that already converged."

The magnitude is mild — 3–4 perturbed heavy atoms, not 58 — so this is a **design defect, not a killer**. But
it is avoidable for free.

### 2b. The alchemical class matters more than the atom count

Three of the four named candidates are **deletions** (methyl→H, *t*Bu→*i*Pr, phenol→phenyl). A deletion creates
a **heavy dummy atom that must be decoupled through the softcore region** — whereas the N→CH edge that already
converged maps 1:1 with **zero heavy dummies**. This is not a cosmetic distinction on this lane:
`ternary-rbfe-runbook.md` §1b/§1c root-causes the warmup NaNs to *"the softcore alchemical (dis)appearing
region in a large, rough homology-built assembly"*, and records that there is **no static predictor** of it.
Buying a deletion edge here means re-entering the exact failure mode that cost this lane multiple dead runs.
**Counting "perturbed heavy atoms" alone treats a 1-atom deletion and a 1-atom element swap as equivalent. They
are not.**

### 2c. "The machinery carries over unchanged" is not true

`nr4a3_ternary_fep._endpoint_pose` always builds from cmpd1's crystal pose and has **exactly one**
element-change mutation path, `_pyridine_to_benzene_pose`, which requires the molecule to have exactly one
pyridine and produces the benzene analogue. For any cmpd4′ it produces cmpd4, the canonical-SMILES check fails,
and the function raises `SystemExit("refusing a wrong-molecule leg")`. **The engine cannot build any cmpd4′
endpoint today.** Engineering is free, so this is not a blocker — but the required new code differs sharply by
class: an element change needs a one-line generalisation (`SetAtomicNum` on another ring atom; N and C have
near-identical radii, which is *why* the crystal pose transfers), while a deletion needs an entirely new
atom-removal-and-H-placement path that the engine does not have. On a lane that produced **ten** measure-nothing
defects in one day, a new fail-closed surface is a real cost.

### 2d. ★ The replacement topology: an **aza-scan at the linker ring**

Put all three vertices at the **same site**. The linker ring already offers three states by moving one nitrogen:

| edge | transform | mutating atoms | heavy dummies | site |
|---|---|---|---|---|
| **T1** | cmpd1 → cmpd4 — remove the ring N | 1 | **0** | linker ring |
| **T2** | cmpd4 → cmpd4″ — add a ring N at a free CH | 1 | **0** | linker ring |
| **T3** | cmpd1 → cmpd4″ — **move** the ring N | 2 | **0** | linker ring |

Every edge is **single-site, charge-neutral, and a pure element change with zero heavy dummy atoms**, so:

- **T3 stops being a double perturbation** — the invariant violation in §2a disappears;
- **no edge grows the softcore region** — §2b's NaN risk disappears;
- **nothing outside the linker is touched** — not the hydroxyproline VHL anchor, not the thiazole cap, not the
  tert-leucine, not the aminopyridazine acetyl-lysine mimic, not the phenol. Every one of the four named
  candidates lands on a recognition element; the linker is the one region carrying none. *(This matters
  practically, not just aesthetically: a leg whose ligand does not stay bound does not converge, and the
  closure would then be measuring a dissociation rather than a systematic error.)*
- **the pose construction is the transform the engine already implements**, generalised by one line.

The new nitrogen may only occupy a ring carbon **bearing a hydrogen** — putting it at a substituted position
would make a quaternary aromatic N⁺ and change the formal charge, which is the failure mode that killed 6 of
the 10 P-series pairs. That is enforced in code, not assumed. Route A (apply to cmpd4) and route B (a
single-edit N move on cmpd1) are **independent constructions of the same endpoint** and must agree, which is
what proves the three edges share endpoints.

---

## 3. What a closure residual can and cannot diagnose — the decisive result

**Two lines.** Write the computed edge value as `ΔΔG_calc(A→B) = ΔΔG_true(A→B) + e(A→B)`. Around a closed cycle
the true terms telescope to zero, so `R = Σ_cycle e`. If the error is a **per-endpoint bias**,
`e(A→B) = ε(B) − ε(A)` for some state function ε, then `Σ_cycle e` telescopes to zero as well. **Hence R
measures only the NON-CONSERVATIVE (path-dependent) part of the error.** Demonstrated numerically over 2000
random draws: max |R| = **3.6 × 10⁻¹⁵** with state-function error alone; adding a per-edge path error makes it
non-zero. Unit-tested twice, once independently of the module's own loop.

| error class | is it a state function? | seen by closure? |
|---|---|---|
| force-field error at the ternary interface | yes (per endpoint) | **NO** |
| the SMARCA4→SMARCA2 homology substitution | yes (same Hamiltonian for every endpoint) | **NO** |
| NAGL partial-charge error | yes (per molecule) | **NO** |
| protonation / tautomer assignment | yes | **NO** |
| reference data (α_SPR is an *apparent* cooperativity) | not in the calculation at all | **NO** |
| insufficient λ sampling / hysteresis / poor overlap | no — path-dependent, edge-specific | **YES** |
| endpoint-state inconsistency across independently staged edges | no | **YES** |
| mutually inconsistent atom maps between edges | no | **YES** |

> **The r0 convergence analysis concluded the systematic lives "in the model or the reference data."
> Every one of those is in the top half of this table. A closure triangle is mathematically blind to all of
> them.** The design's claim that it "attacks both candidate causes at once" is refuted — not by judgement, by
> the telescoping identity.
>
> The design's own honest limit ("closure measures internal consistency, not accuracy — the known-answer
> requirement stays OPEN") is **correct and must travel with any result**. This section is the sharper version
> of it: closure is not merely *not an accuracy control*, it is **specifically blind to the error classes this
> lane's live hypothesis names**.

### 3a. How big must |R| be to mean anything?

R is a ±1 combination of **six** leg free energies, so `SD(R) = √6 · σ_leg = √3 · σ_edge` (analytic and Monte
Carlo agree to <1 %). The problem: **σ_leg for this lane is known only to within a factor of ~15.**

| σ_leg | SD(R) | null 95th %ile of \|R\| | power at n=1 to detect a **1.478** path error |
|---|---|---|---|
| **0.045** (r0 ternary MBAR SE — a *lower* bound; blind to slow modes) | 0.110 | 0.215 | **100 %** |
| 0.2 | 0.490 | 0.957 | 86 % |
| 0.5 | 1.225 | 2.420 | 22 % |
| **0.7** (the repo's assumed replicate SD — an *upper* bound here) | 1.715 | 3.349 | **14 %** |

Two readings, both load-bearing:

1. **The instrument's own power is unknown by a factor of ~7** over the plausible σ range, and 0.7 is a genuine
   over-estimate for a *same-seed* triangle (it includes the homology-model swap §1b removes) while 0.045 is a
   genuine under-estimate. Nothing in this lane has measured the quantity in between.
2. **The asymmetry is what makes the n=1 scout worth buying anyway.** A **small |R| is strong evidence** — it
   bounds the path error *and* the noise simultaneously, since both would have to be small. A **large |R| at
   n=1 is ambiguous** — one draw cannot separate a systematic from an unlucky sample. So the n=1 scout can
   **admit** the cycle but cannot **convict** it. That is still a useful gate, and it is the honest way to
   describe what ~$7 buys.

---

## 4. The decision tree, and a test of "worth buying under either branch"

The design asserts the triangle is worth buying under either branch of the reverse-leg result. Tested against
§3 rather than inherited:

### Branch A — |ΔG_fwd + ΔG_rev| ≲ 0.3 (no hysteresis)

The path is internally consistent, so the systematic lives in the **model** or the **reference data**. §3 shows
closure is **provably blind to every one of those classes**. Under branch A the triangle's expected residual is
~0 *whether or not the programme's actual problem exists*, so it cannot discriminate "the method is right" from
"the model is wrong". → **REFUTED for diagnosis.** It still yields a path-error resolution floor and an
endpoint-consistency check — publishable methods results, but not what branch A needs.

### Branch B — |ΔG_fwd + ΔG_rev| ≳ 1.0 (real hysteresis)

Path error *is* the class closure measures. But (i) the reverse leg has **already** established that it exists,
on the edge already paid for, for 2 legs; and (ii) the design's own branch-B instruction is *"fix the protocol
first"* — and a triangle bought **before** the fix measures the **old** protocol and must be re-bought after.
→ **REDUNDANT, THEN STALE.**

*(Replica mixing **0.8915** against the 0.90 ceiling, recorded MARGINAL, already leans toward branch B — which
is the branch under which buying now is worst.)*

### The claim is NOT SUPPORTED AS STATED. But there is a real reason to buy, and it is a different one.

**The forward/reverse pair now running IS a closed cycle** — 1 → 4 → 1, residual |ΔG_fwd + ΔG_rev|, which is
precisely the preregistered antisymmetry check. So the programme's first cycle-closure instrument is **already
arriving at zero marginal cash cost**, and "no cycle closure exists" is a historical statement, not a current
one. What does a 3-cycle add? Simulated over 4000 draws:

| error class | 2-cycle (fwd + rev) detects | 3-cycle (triangle) detects |
|---|---|---|
| state-function (per-endpoint bias) | **0.00** | **0.00** |
| **symmetric** path bias (estimate lags whichever endpoint the leg started from) | **1.00** | 1.00 |
| **antisymmetric per-edge** bias (`fwd = true + δ`, `rev = −true − δ`, δ differing per edge) | **0.00** | **1.00** |

**The triangle's exclusive territory is the third row**, and that is the class a *reversible-but-wrong* λ
schedule produces — invisible to a forward/reverse pair by construction, because a 2-cycle reuses its own two
endpoints. That is the honest case for the triangle. It is narrower than the design's case, it is specific, and
it is testable.

**Cost per edge, for completeness:** the reverse leg closes a 2-cycle on 1 edge for 2 new legs (2.0 legs/edge);
the triangle closes a 3-cycle on 3 edges for 4 new legs (1.33 legs/edge). The triangle is cheaper *per edge* —
but only if all three edges were wanted anyway. To diagnose one edge, the reverse leg is cheaper outright.

### 4a. Is there a better use of the same four legs? — the comparison the ADMIT actually rests on

A design should win a comparison, not win by being the only proposal. All three options below cost the **same
4 new ternary+binary legs ≈ $6.83**:

| option | edges covered | sees symmetric path bias | sees **antisymmetric per-edge** bias | tests cross-edge endpoint consistency |
|---|---|---|---|---|
| **the closure triangle** (T2 + T3, forward only) | **3** | ✅ | **✅ (uniquely)** | **✅** |
| forward **and** reverse of one new edge (T2 fwd + rev) | 1 | ✅ | ❌ (a 2-cycle is blind by construction) | ❌ |
| two more **replicates** of T1 (r1 + r2) | 1 | ❌ (random error only) | ❌ | ❌ |

**The triangle wins**: it is the only option covering more than one edge, the only one that can see an
antisymmetric per-edge bias, and the only one testing cross-edge endpoint consistency. *(The replicate option is
the one the r0 verdict already argued against on independent grounds — r0's miss is 33× its own MBAR SE, so it
is systematic, and seed *s* swaps the homology model so the SD would conflate sampling with model sensitivity.)*
**This is the substantive reason to ADMIT the triangle** — and it is neither the reason the design gives, nor a
claim about r0's systematic.

Winning a 4-leg comparison is not the same as being the next thing to buy: §7's $1.31 pre-scout costs ~19 % of
these four legs and can falsify the machinery first, and the reverse-leg branch decides whether any of it should
be bought yet at all.

---

## 5. Leg accounting — the cancellation identity does **not** apply, and one thing *does* cancel

STRATEGY's identity: *a paralogue panel is N ternary legs + 1 shared binary + 1 shared solvent, not N edges*,
because `binary_<e3>` (E3 machinery + PROTAC, no target) and `solvent` (ligand in water) are both
paralogue-independent.

**Tested, not assumed. It does not apply here.** The identity shares legs across **targets** at a fixed ligand
pair; the triangle varies the **ligand pair** at a fixed target. A binary leg is an alchemical morph of the
ligand *inside VCB*, so it is a function of the pair — three pairs, three binary legs, **zero shared legs**.
Claiming it here would underprice the triangle by ~2×. *(This confirms the rescope doc's own §2 reasoning.)*

**What does cancel:** the **solvent leg cancels exactly** inside `ΔΔG_coop = ternary − binary`, so a triangle
whose deliverable is R needs **2 legs per edge, not 3**. ⚠ But the pattern `nr4a3_ternary_fep.expand_pilot_legs()` implements is *one shared solvent leg per
distinct morph*, added unconditionally — so registering T2/T3 as morphs would buy 2 solvent legs the closure does
not need — **$1.31** of avoidable spend, unless they are bought deliberately for the reason in §7.

**Forward-looking:** binary legs *are* target-independent, so if a triangle edge is later replicated against a
second known-answer system (VHL–BRD4), its binary legs transfer unchanged.

---

## 6. The corrected price — three corrections, and the largest is not the iteration basis

**Priced in STEPS, because iteration counts are not comparable across protocols.** A 1 fs warmup iteration and a
2 fs production iteration each cost the same **1250 force evaluations**, which is exactly why the leg is 2800
iterations and not 2400:

```
warmup     1.0 ns @ 1 fs  = 1.00e6 steps  =  800 iterations
production 5.0 ns @ 2 fs  = 2.50e6 steps  = 2000 iterations
                            ---------         ----
leg                         3.50e6 steps      2800 iterations
```

At the measured **~16 s/iteration** on a Vast RTX 4090 (146,284-particle assembly) → **12.44 reference GPU-h per
ternary leg**, against 10.67 on the withdrawn 2400 basis. At the repo's planning rate **$0.1372 / ref GPU-h**
(range $0.057 best offer – $0.3094 median):

| variant | legs | ref GPU-h | **plan $** | range $ |
|---|---|---|---|---|
| **solvent-only pre-scout** (§7) | 2 solvent | 9.6 | **$1.31** | $0.55–2.96 |
| **n = 1 scout, R only** (2 new edges × ternary+binary; r0 reused) | 4 | 49.8 | **$6.83** | $2.84–15.40 |
| n = 1 as the pipeline pattern would run it (+2 solvent) | 6 | 59.3 | $8.14 | $3.38–18.36 |
| n = 3 *as the design prices it* — **incomplete** | 12 | 149.3 | $20.49 | $8.51–46.20 |
| **n = 3 HONEST** (all three edges at n=3 ⇒ 12 new legs **+ T1's r1, r2**) | **16** | 199.1 | **$27.32** | $11.35–61.60 |

**The three corrections, in increasing size:**

**(a) The iteration basis: +16.7 %.** The design's ~$5.9 was computed on 2400 iterations. Corrected: **$6.83**.
This is arithmetic on the existing rate, not a new measurement.

**(b) Solvent legs: +$1.12 if run by default.** Not needed for R, but the pipeline adds them. Priced separately
so the choice is explicit rather than accidental.

**(c) ★ T1's replicates do not exist: the n=3 triangle is 16 legs, not 12 — +33 %, the largest correction.**
An n=3 closure needs three replicates of **all three** edges (seeds 0, 1, 2 on each — §1b), and **T1 has only
r0**. So the n=3 design silently re-includes buying **r1 and r2 of the edge already run** — precisely the spend
[`valB-mini-r0-verdict-2026-07-25.md`](valB-mini-r0-verdict-2026-07-25.md) §7 argued against, on the grounds
that replicates shrink variance and the miss is systematic. **n = 3 is $27.3, not $17.6.**

**Every figure above is a CEILING.** The ~16 s/iter rate was measured on the **146,284-particle ternary**
assembly and is applied to the binary leg too. But `binary_<e3>` is E3 machinery + PROTAC with **no target**, so
it lacks the SMARCA2 bromodomain — ~1,900 of the 7,388 solute atoms, by the convergence analysis's own chain
census — and its solvated box is correspondingly smaller. The true cost is lower by an amount **nobody has
measured**, and this document does not invent one. Erring high is the right direction for a spend gate.

**If RUNG 2b adopts 4 fs**, every figure scales by the **step** ratio **0.643 — not 0.5** (the warmup is pinned
at 1 fs either way, so only the production half halves; a "2× cheaper" claim overstates by ~36 %). The n=1
scout would be **$4.39**. That decision is RUNG 2b's and is not assumed here — **quote the 2 fs price.**

---

## 7. ★ Buy the SOLVENT closure first — $1.31, and it can falsify the triangle before any ternary leg

A new recommendation, and it is the repo's own pilot-one-leg-first rule applied to the triangle itself.

`R_solvent = ΔG_solv(T1) + ΔG_solv(T2) − ΔG_solv(T3)` is a **full closure test of the alchemical machinery** —
atom-map consistency between edges, endpoint chemical identity, λ-schedule adequacy, charge-model consistency —
in a ~5 k-particle box instead of a ~142 k-particle assembly. **T1's solvent leg already ran** (r0: ΔG_morph =
47.8060), so it costs **2 new solvent legs ≈ $1.31**, about **19 %** of the full n=1 scout.

It **cannot** see protein-sampling path error, interface substates, or anything about cooperativity — and that
is the point: it isolates the *machinery* from the *physics*. **If the machinery closure fails, no ternary leg
should be bought**, and finding that out costs a fraction of one ternary leg. It also directly targets the bug
class this lane has actually produced: the reverse leg's `base_smiles` defect built an endpoint against the
wrong bond-order template — a chemical-identity error that shows up in solvent.

⚠ **Honest caveat on the number, and a self-caught instance of the very error this document corrects.**
The only solvent-leg figure the repo has is the binary NR4A3 RBFE lane's **~4.1 ref GPU-h** (pricing.md §B) —
and that is stated on the **binary lane's 2400-iteration leg**. Carrying it across as a *total* would import a
2400-basis number into a 2800-basis calculation, which is exactly the mistake being corrected in §6. It is
therefore converted to a **rate** first (4.1 h / 2400 iters = **6.15 s/iter**) and re-multiplied by the ternary
lane's 2800 iterations → **4.78 ref GPU-h per leg**. Still an **estimate, not a ternary-lane measurement**, and
the two lanes' solvent boxes differ (a 59-heavy-atom PROTAC vs a ~20-heavy-atom warhead). It is *not* 1/28 of a
ternary leg despite the particle ratio, because a solvent leg runs the same 12 λ-windows for the same number of
iterations and is latency-bound rather than throughput-bound at that size.

---

## 8. Recommendation, in spend order

1. **$0, done** — this pre-gate. It admitted the triangle but corrected its topology, its price, and its stated
   purpose.
2. **$0, next** — implement the **aza-scan** transform and the one-line generalisation of
   `_pyridine_to_benzene_pose`, and add a route-A/route-B endpoint-agreement assertion to the 5-part pre-spend
   gate. Free engineering; no dollar is committed by doing it.
3. **Read the reverse leg** (result ~2026-07-26 AM ET). Branch B ⇒ **fix the protocol on the edge already paid
   for**; do not buy the triangle, it would go stale on the fix. Branch A ⇒ continue to (4), but with the
   purpose restated per §4: it is not a diagnosis of r0.
4. **~$1.31 — the solvent-only closure pre-scout (§7).** Abortable, and it can falsify the triangle's machinery
   for ~19 % of the scout price.
5. **~$6.83 — the n = 1 closure scout**, only if (4) closes. Report `R_ternary` and `R_binary` **separately**
   (§1a), all edges at **seed 0** (§1b).
6. **Do NOT buy n = 3 at $27.3** without a separate decision: it drags in T1's r1/r2, the spend the r0 verdict
   argued against, and §3a shows the replicate SD it would measure is not the quantity the closure needs.

**The deliverable to aim at remains the measured resolution floor**, and §3 sharpens what may honestly be
claimed for it: *"this workflow's ΔΔG_coop cycle is internally self-consistent to within X kcal/mol of
**path** error"* — **not** "resolves differences of ≥ X", which would imply an accuracy statement the
instrument cannot support.

---

## 9. Honest-scope notes that must travel with any result from this

- **Val B is the NAGL lane's known-answer control.** OpenFE's published ~1.7 kcal/mol RBFE accuracy was measured
  on **am1bcc** and does **not** transfer to the ternary lane. No ternary number in this program may cite it.
- **The known-answer accuracy requirement stays OPEN.** Closure measures internal consistency, and §3 shows it
  is specifically blind to the model and reference-data error classes. Nothing in this document narrows that
  gap; the rescope doc's §5a conclusion — that a ≥2 kcal/mol calibrator which is simultaneously small,
  charge-neutral and mappable may not exist in the public literature — still stands as the reason.
- **Replicate spread on this lane is not pure sampling noise**: ternary seed *s* uses the *s % n*-th relaxed
  SMARCA2 model, so any SD quoted from it conflates sampling with homology-model sensitivity. §1b's same-seed
  requirement removes that term from R specifically, but not from the lane's other numbers.
- **No number in this document is a measurement of a new physical quantity.** The rate (~16 s/iter), the leg
  length (3.5e6 steps), the $/ref-GPU-h ($0.1372) and the solvent-leg estimate (4.1 ref GPU-h) are all carried
  from the repo's existing basis; this document reprices and re-derives, it does not re-measure.
