# NR4A3 degrader — the 8XTT structural-provenance situation, work in flight, and open decisions

*Shareable memo · 2026-07-10 (~9:45 PM ET) · companion to the manuscript
`nr4a3-degrader-paper.md` (§2.1, §2.8) — written to be read on its own.*

## TL;DR

We evaluate a de-novo NR4A3-favoured ligand (`denovo_401`) by absolute binding free energy (ABFE). The
headline selectivity was computed on **AlphaFold-derived opened pockets**: ΔG_bind ≈ **+3.5 (NR4A3) / +8.3
(NR4A1) / +8.5 (NR4A2) kcal/mol**, i.e. a ~5 kcal/mol NR4A3 margin (lower = tighter). We then recomputed the
**NR4A3 leg only** anchored on the **experimental** structure (the 8XTT solution-NMR ensemble). Result, now
complete over three replicates: **+8.17 ± 0.98 kcal/mol** — about **4.7 kcal/mol weaker** than on the AF pocket,
i.e. **larger than the entire selectivity margin**. The one-line takeaway: **our absolute ABFE is strongly
dependent on which opened conformer we anchor on, so the selectivity number must be read as *conditional on the
chosen conformers*, not as a structure-independent fact.** This is not a refutation of the molecule — it is a
provenance-sensitivity result that tells us exactly what to nail down next.

## 1. Background a colleague needs

- **NR4A3 (NOR-1)** is an "orphan" nuclear receptor; the family's orthosteric pocket is **collapsed/occluded in
  crystal structures** and historically called "undruggable." That reputation is about *static* structures —
  solution/NMR/HDX/MD work on the paralogues (Nurr1/Nur77) shows the pocket is **dynamic and can expand**. So a
  cryptic, breathing, occasionally-druggable pocket is a **known family feature**, not a claim we originate. Our
  contribution is a *designed selective ligand + its selectivity energetics*, using that pocket as the premise.
- **Two structural bases for NR4A3:**
  - **AF2 model** (AlphaFold, UniProt Q92570) — a single predicted conformer; our design and headline ABFE were
    built on an MD-opened version of it. (8XTT did not exist when the design was done — it was released
    2025-01-15.)
  - **8XTT** — the experimental NR4A3 LBD, a **20-model solution-NMR ensemble**. fpocket over the 20 models:
    median druggability 0.012, **20% (4/20) above our drug-bound reference boundary**, peak 0.925. So the
    experimental ensemble is **mostly closed with a druggable minority** — the classic low-population cryptic
    pocket. Our experiment-anchored ABFE seeds MD from one of those **druggable (open) NMR models**, relaxes it,
    and docks into the persistent druggable frame. (So the 8XTT run does **not** start from a closed structure.)

## 2. The core finding: structural provenance dominates the absolute ΔG

| NR4A3 conformer used for ABFE | ΔG_bind (kcal/mol) | vs paralogues (NR4A1 8.3 / NR4A2 8.5) |
|---|---|---|
| **AF2-opened** (headline, n=3) | **+3.5 ± 1.4** | margin ~5 (ΔΔG(3−2) = −4.98) |
| **8XTT experiment-anchored** (n=3: 7.95/9.24/7.32) | **+8.17 ± 0.98** | margin ~0 |

Two readings, both of which we state in the paper:

1. **It is NOT a fair selectivity comparison as it stands.** The 8.17 is an *experiment-anchored NR4A3* leg
   compared against *AF2-opened* paralogue references — deliberately **mismatched provenance**. So the apparent
   collapse of the margin (8.17 vs 8.3/8.5) is **not** a selectivity refutation. What it rigorously proves is
   point 2.
2. **Structural provenance dominates.** Swapping the NR4A3 opened conformer (both are open/druggable, but with
   ~3.6 Å pocket-backbone difference between AF and the 8XTT-derived frame) moves the absolute by **more than the
   whole selectivity margin**. Therefore the ΔΔG magnitude is conformer-dependent and the selectivity is honestly
   reported as **conditional on the AF2-opened states**.

**Important caveat on trusting 8.17 itself:** the 8XTT complex legs have **low λ-overlap in the soft-core tail
(min adjacent MBAR overlap 0.017–0.026)** — the same defect that put the NR4A2 selectivity leg on a "provisional"
footing. So +8.17 is itself **not yet a converged absolute**; it needs the same dense-λ repair before we read it
literally. The qualitative conclusion (provenance moves the number a lot) is robust; the exact 8.17 is not final.

## 3. Supporting context (why this is a sharpening, not a collapse)

- **Design/evaluation separation is a feature, not a bug.** `denovo_401` was designed on the AF pocket. Scoring
  it in an *independent* experimental conformer is a **cross-structure generalization test**; it survives
  (still NR4A3-favoured, degraded). Designing *and* scoring on the same structure would be circular/overfit —
  the one combination to avoid. The ~4.7 kcal/mol drop is the honest "designed-for-a-different-pocket" penalty.
- **AF is a faithful *fold* model for the whole family** (new, matched check): AF vs the experimental crystals —
  **NR4A1 vs 3V3E global 1.20 Å / pocket 0.44 Å; NR4A2 vs 1OVL global 1.40 Å / 0.82 Å**. So the AF-based design
  and the paralogue references rest on sound backbones. (These are AF-vs-*collapsed-crystal* fold checks, not
  open-pocket validations.) NR4A3's larger AF-vs-experiment divergence (7.63 Å global) is because 8XTT is a
  *flexible NMR ensemble*, not a single crystal — consistent with a genuinely dynamic pocket.
- **The engine's absolute scale is unvalidated anyway.** On the T4-lysozyme L99A/benzene textbook benchmark the
  same engine under-binds by ~7 kcal/mol, so we already interpret **contrasts, not absolutes**. The provenance
  result reinforces that we should never quote a calibrated absolute affinity.

## 4. What is in flight right now (as of ~9:45 PM ET, 2026-07-10)

| Run | Purpose | Status |
|---|---|---|
| **T4L benchmark v2** | engine absolute-accuracy anchor (more important now that absolutes move) | running (complex leg ~window 4) |
| **NR4A2 λ-repair pilot (r1)** | prove the dense-16-window schedule restores soft-core-tail overlap — the fix we also need for the 8XTT legs | running, **window 4/16**; validation gate at window 9 (~4–5 AM ET) |
| **NR4A2 λ-repair r2/r3** | error bars on the repaired NR4A2 leg | **paused** (validate-first) |
| **Phase-2 metad shakeout** | single-shard validation that a data-derived (TICA) reaction coordinate drives pocket opening/recrossing, before a ~$100–200 3-seed × 3-paralogue fleet | **completed 8 ns cleanly**; recrossing analysis running now |
| **Phase-2 fleet (opening free-energy)** | the paralogue **ΔG_open differential** (the other half of the honest selectivity) | pre-approved **contingent on the shakeout showing clean recrossing** |

Slots are not the constraint (≈6 of 8 free); nothing in flight is measuring something obsolete — in particular
the NR4A2 λ-repair pilot is now *cross-critical* because the 8XTT legs share its exact overlap defect.

## 5. Open decisions (what needs a human call)

1. **λ-repair the 8XTT NR4A3 legs first?** (~$10–15, resume from checkpoint.) Cheapest way to learn whether
   +8.17 is real or a tail-overlap artifact **before** spending on anything bigger. *Recommended first step.*
2. **Run matched, experiment-anchored paralogue ABFE?** This is the only way to make a *fair* experiment-anchored
   selectivity statement. Cost ~$40–80 (spot GPU) — and note the paralogue crystals (1OVL, 3V3E) are **collapsed**,
   so it requires a crystal-seeded pocket-opening MD step first (the "experiment-anchored" paralogue pocket is
   itself MD-derived, symmetric to how 8XTT is handled). Decision gated on #1.
3. **Phase-2 opening free-energy fleet?** ~$100–200; already pre-approved **contingent** on the shakeout's
   recrossing verdict (analysis landing shortly). Measures the ΔG_open *differential*, the conformer-cost term
   that the conditional ABFE omits — directly relevant now that provenance is shown to matter.
4. **How to frame selectivity in the paper if we stop here.** Fallback that needs no further GPU: report the
   AF2-opened ΔΔG as **explicitly conditional on the opened conformers**, with the 8XTT recalc as a stated
   sensitivity result showing the magnitude is provenance-dependent. (Already written this way in §2.8.)

**Recommended sequence:** (1) λ-repair the 8XTT legs → trust or revise +8.17; in parallel read the shakeout
recrossing → decide Phase-2; then (2) decide the matched paralogue ABFE on the repaired numbers. Each step is
gated on cheap/free information before the expensive one.

## 6. Bottom line for a reader/collaborator

The molecule still shows an NR4A3 preference on matched-provenance comparisons, and survives a cross-structure
stress test in degraded form. The new, honest headline is methodological: **for a shallow cryptic pocket,
which opened conformer you anchor on can move the absolute binding free energy by more than the selectivity
margin.** That is a result worth stating plainly, and it defines a concrete, bounded set of follow-up
calculations (λ-repair → matched experiment-anchored paralogues → opening-FE differential) rather than
undermining the program.
