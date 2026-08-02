# The family of paths — synthesis across five independent fan-outs

★ **trimcrae, 2026-08-02: *"fan out about alternative ways we could get to our end goal paper… Use everything
we've learned from our failed tests to help guide what we think would and wouldn't work… I want to make sure
we have a really well considered family of paths and we can start with the ones that are the best
candidates."***

Five agents worked independently on five different axes. This file is the synthesis, not a sixth opinion.
Every number below points at the register that owns it (rule 1):
[mechanisms](../modalities/selectivity-mechanism-options.md) ·
[papers](nr4a3-program-map.md) → [framings](paper-framing-options.md) ·
[targets](target-route-options.md) · [instruments](../modalities/instrument-options.md) ·
[the candidate](../modalities/nr4a3-short-linker-probe.json).

⏳ **ONE INPUT IS STILL OUTSTANDING AND IT CAN REORDER THIS PAGE.** The categorical decoy null (`C02`) is
running. It is the falsifier for the mechanism ranked first below, and the mechanism it would falsify has
**never faced a cross-system null**. `V20` looked equally clean until 38 unrelated drugs went through its
funnel and 22 scored positive. **Nothing here is final until that lands.**

---

## 1 · What the fan-out changed, in one table

| before today | after |
|---|---|
| "the paralogues are ~80 % identical" | **LBD is 59.4 % / 67.3 %** — we already work in the protein's most divergent domain; the 80 % was SMARCA2/4 transplanted |
| selectivity is one requirement | **it is asymmetric** — NR4A1 is a *mandatory* anti-target (the NR4A1+NR4A3 double-KO is the named mouse AML genotype, PMID 17515897 / 29343483); NR4A2 is **unbounded** (pLI 1.0 but no phenotyped KO) |
| 3 candidate mechanisms | **17 enumerated, 9 previously unrecorded**, 2 refuted on committed data |
| "no ≤12-atom construct exists" | **one exists** — the floor of 14 was a *basin-breadth policy*, not geometry |
| the cryptic pocket is NR4A3's edge | **refuted** — fpocket rates NR4A1's opened frame *more* druggable (0.981 vs 0.931) |
| degradation-competence is a live option | **refuted** — paralogues are not lysine-poor (gap +0.0118 against a replicate-SD of 0.0175) |
| ΔΔΔG might inherit `V6`'s validation | **it does not** — but `R6` cancels out of a *relative* quantity, so `R6` blocks the ABFE route and **not** the ΔΔΔG route |

⛔ **The single most useful generalisation, arrived at independently on three axes:** every route that genuinely
reduces the selectivity requirement does so by **leaving the free-energy axis**, not by better pocket
chemistry. The requirement is a *measurement* problem — ~2.0 kcal/mol needed, 0.60 resolvable at best, and the
one ternary attempt returned 1.543 with the **wrong sign**. Mechanisms that terminate in a ΔΔG inherit that;
mechanisms that terminate in a geometry, a sequence fact or a shape constraint do not.

---

## 2 · The family, ranked — what to start with

### Tier 1 — start here

| # | path | why it leads | what it costs | its falsifier |
|---|---|---|---|---|
| **1** | **Categorical covalent at C397, at ≤12 atoms** — the candidate now exists (`RZSRKKSYYBOIEK-ACNWJKEOSA-N`) | only mechanism with a *measured* selectivity number that needs no free-energy instrument | **$0 spent** | ⏳ `C02`, running |
| **2** | **Steric exclusion / negative design** — L406→His, I484→Tyr, L534→Phe | paralogue-only clash **0.923** vs a **0.173** null (5.34×); scores a structure rather than generating one; the only new mechanism with a constructible unconfounded positive control | $0 to extend | its own M4 control: the paralogue **relocates** the ligand (~5.3 Å) rather than refusing it — a pose rule, not a binding claim |
| **3** | **Widen the categorical enumeration** — 35 unique alignment-robust positions, 11 reactive classes; **Y419** (SuFEx) and **M398/M399** (oxaziridine) are new | Route B's single point of failure is a **gap in the enumeration**, not a fact about the protein | $0 | chemistry credibility is a literature label, not a computed quantity |
| **4** | **Write the brief asymmetrically** — hard constraint vs NR4A1, relaxed vs NR4A2 | 5 engageable handles against the mandatory paralogue, 4 against the unbounded one; free, and nobody had | $0 | NR4A2's tolerance is *unbounded*, not *established* — an absent KO is not a safe KO |

### Tier 2 — strong, but gated on something

| # | path | gate |
|---|---|---|
| 5 | **Ligand-side ΔΔΔG as a named instrument** (`C01`) | needs a paralogue-scale known-answer benchmark; two $0 searches decide whether one is buildable |
| 6 | **Ternary rung `5b-T`** (`V2`→`V1`, both validated) | ⛔ its E3 is **CRBN**, and CRBN reaches C397 at 12 only *through-space* — **14 under corridor**. Its library also no longer reproduces from its own code (57 vs 54 constructs) |
| 7 | **`barnase_barstar_W35F`** — the only probe of the ~1 kcal/mol regime | priced (~$1.3), staged, **authorized**; licenses nothing about paralogues directly |
| 8 | **Covalent inhibitor rather than degrader** at C397 | retires the whole ternary/ubiquitin stack; loses the degradation mechanism |

### Tier 3 — real, but they change what the paper is

| # | path | note |
|---|---|---|
| 9 | **Junction ASO / junction neoantigen** | genuinely removes the paralogue requirement; ⚠ the neoantigen lane owes a correction — its 26 binders span seams that do not exist |
| 10 | **TCIP** | retires `R9`/`R10`/`R12`; keeps `R4`/`R5`/`R7` |
| 11 | **Downstream / dependency target** | removes the requirement by leaving the target |

### ✕ Closed by this fan-out — do not re-propose

**Degradation-competence via lysine availability** (paralogues are not lysine-poor) · **pocket-opening
selectivity** (NR4A1's opened frame is *more* druggable) · **relocating to the DBD** (92.8 % / 98.6 % identical
— strictly worse) · **fusion-selective ubiquitination** (the 17.1 Å transfer zone is LBD-local) · **E3 choice
as a lever** (graded D — restaging alone swings enrichment 16.60 → 6.07) · **molecular glue** (same ΔΔG, fewer
axes, no prospective precedent).

---

## 3 · The paper question, which is separate from the mechanism question

The framing sweep's recommendation is **not** the paper we have been writing. Its argument is that the current
paper's own scoreboard refutes its title: 7 gates passed, 4 failed, and **three of the four failures are the
three attempts at a positive control for the exact capability the title promises**.

Three framings need no instrument to pass and no bench — which matters absolutely under a permanent no-wet-lab
regime, because the candidate framing is hostage to `R4` (*does anything bind the opened pocket*), which has
**no in-silico instrument and never will**:

1. **The known-answer audit** — the register as the subject. Its headline generalises: **22 of 38 (57.9 %)**
   unrelated marketed drugs score a positive MM-GBSA selectivity margin, replicated at 39 % on 6,000
   compounds. Its deepest result is a *proof*: the cooperativity calibrator missed by 1.543 kcal/mol with the
   wrong sign in 3/3 replicates **while converged, stable, forward/reverse-antisymmetric and cycle-closed**.
2. **The co-folding assembly failure** — components at DockQ 0.89–0.97, their assembly at 0.023–0.046. A
   factor of ten, self-contained, and the only framing with a live clock.
3. **The target-enablement dossier** — absorbing the candidate paper as its closing *"what a candidate would
   require"* section, which keeps every result in print.

⚠ **These are not exclusive with Tier 1.** The mechanism work strengthens whichever paper is written; the
framing decision is trimcrae's and does not block any Tier-1 item.

---

## 4 · What I would start, tomorrow, in order

1. **Read `C02`'s answer first.** It is the falsifier for path 1 and it is free. Acting before it lands would
   repeat the `V20` mistake at a larger scale.
2. **Path 2 (steric exclusion) regardless of `C02`** — it is independent of the covalent axis, so it survives
   a bad `C02` and compounds a good one.
3. **Path 4 (asymmetric brief)** — $0, changes the design target, and no result can invalidate it.
4. **Fix `5b-T`'s two defects before running it** — the CRBN corridor conflict and the non-reproducing library.
   Both are provenance, both are $0, and both would otherwise be discovered *after* the spend.

⛔ **Nothing in this file licenses a selectivity, efficacy, safety or clinical claim.** The candidate is a
target-engagement geometry result. No binding affinity has been measured or computed for it, no ternary has
been assembled with it, and the pocket it targets has never been shown to bind anything at all.
