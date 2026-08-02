# Paper framing options — what else this body of work could publish, graded on the evidence that exists

> **Role: an OPTIONS REGISTER, not a decision and not a plan.** The plan is
> [nr4a3-program-map.md](./nr4a3-program-map.md) and it wins over this file on anything it also covers.
> Nothing here changes a status, a price, a gate or a claim. Every figure quoted below has its **one home**
> in a committed artifact or in the roadmap, is **linked, never re-derived**, and was re-read against that
> home while writing (CLAUDE.md rule 1, invariant 5).
>
> **Why it exists (trimcrae, 2026-08-02):** *"a really well considered family of paths… I want lots of
> options in the queue"* and *"use everything we've learned from our failed tests to help guide what we
> think would and wouldn't work."* The program has **one** deliverable and **one** framing of it. That is a
> single point of failure for a body of work whose most rigorous asset may not be its candidate.
>
> **Language discipline applies to this file too** — the roadmap's
> [Honest scope](./nr4a3-program-map.md#honest-scope-and-language-discipline-apply-everywhere-including-the-manuscript)
> section governs every sentence: never imply proteome-wide selectivity, EMC efficacy, safety, a therapeutic
> window, or clinical readiness. Verified clean against `lint_claims.py` (see [§7](#7--cross-checks-taken-while-writing-this-all-0)).
>
> ⚠ **This file is $0 analysis.** No GPU, no rental, nothing dispatched. It proposes no spend.

---

## 0 · How each framing is graded

Six columns, because the program's own history says a paper fails on any one of them alone.

| # | the question | why it is a column |
|---|---|---|
| **G1** | **Does the central claim rest on an instrument validated in the regime the claim needs?** | This is [invariant 1](./nr4a3-program-map.md#05--six-invariants--structural-not-stylistic), the program's most expensive lesson. [§3.2](./nr4a3-program-map.md#32--the-rv-coverage-matrix--where-the-holes-are) reads out **0 of 16 requirements** standing on one. A framing that needs a validated selectivity instrument is a framing that cannot ship. |
| **G2** | **How much of the evidence is already committed?** | Committed artifact ⇒ writable today. S3-only or branch-only ⇒ a repair first (CLAUDE.md §7). |
| **G3** | **What does it need that only a wet lab can supply?** | The operating regime is *no wet lab, ever, self-funded*. A framing whose headline needs a bench is a framing that never posts. |
| **G4** | **Does it require softening a claim the paper already makes?** | Retracting in public is expensive. Framings that *drop* a claim are cheap; framings that *weaken* one already in print are not — and there is no print yet, which is the whole opportunity. |
| **G5** | **How much of the existing manuscript survives?** | ~3,200 lines of paper + ~940 of SI, red-teamed six rounds. Re-use is the dominant cost term when engineering is free. |
| **G6** | **Is there a clock on it?** | 8XTT released 2025-01-15. Co-folding ternary benchmarks are a hot field. Some of these age; most do not. |

**Ids `P1…P7`** — deliberately not `R*` (requirements), not `V*` (instruments), not `R1–R5` (lint rules).
[§0.6 of the roadmap](./nr4a3-program-map.md#06---five-different-things-in-this-program-are-called-r) lists five
things already called `R`; this file adds none.

---

## 1 · The ranking

| rank | id | framing | G1 · validated instrument? | G2 · evidence committed | G3 · needs a bench? | G4 · softening? | G5 · manuscript survives | G6 · clock |
|---|---|---|---|---|---|---|---|---|
| **1** | **P1** | **The known-answer audit** — what happens when you put in-silico selectivity pipelines to tests with known answers | ✅ **the failures ARE the result** — no instrument needs to pass | **~95 %** | **no** | **none — it removes claims** | **~60–70 %** | none |
| **2** | **P2** | **Where sequence-only co-folding breaks on ternary complexes** — components right, assembly wrong, by a factor of 10 | ✅ the scorer is calibrated two ways and both are committed | **100 %** | **no** | **none** | ~10 % (but the densest 10 %) | ⚠ **yes — hot field** |
| **3** | **P3** | **Target enablement** — the NR4A3 cryptic pocket, its divergence, its unique chemistry, **no candidate** | ⚠ partial — `V14`/`V15` have no known-answer test on this system, `V17` fails its own | **~90 %** (one branch-drift repair) | **no** for the claim as scoped; a bench would strengthen | **none — it drops the candidate** | **~35–40 %** + Lane 13, unpublished | ⚠ **yes — 8XTT is public** |
| **4** | **P4** | **The resolution budget** — why prospective paralogue selectivity is not currently decidable by free energy | ✅ it is arithmetic over measured quantities | **100 %** | **no** | none | ~5 % as text; 100 % as argument | none |
| **5** | **P5** | **Categorical > marginal** — a design principle for close-paralogue degraders, with linker length as the filter | ❌ **the causal test returned its preregistered null** and `V16` has no calibrator | ~85 % for NR4A; **0 %** for the transferability claim | **no**, but the chemistry is untestable in silico | ⚠ **yes** — see G4 note in [§2.5](#25--p5--categorical-beats-marginal-a-close-paralogue-design-principle) | ~20–25 % | none |
| **6** | **P6** | **The candidate paper** (current plan) | ❌ **0 of 16** | ~90 % | ⚠ **yes — `R4`** | n/a (it *is* the claim) | 100 % | none |
| **7** | **P7** | **The benchmark / infrastructure suite** — the test battery, the registers, the discipline | ✅ | 100 % | no | none | little text, most apparatus | none |

**Considered and closed, so they are not re-litigated:** the EMC route portfolio
([emc-treatment-strategy.md](./emc-treatment-strategy.md), [IDEAS.md](../IDEAS.md)) already owns its own
deliverables — the surface-target preprint and the fusion-junction ASO paper — and is **not** a re-framing of
this work; and the **cryptic-pocket druggability atlas**
([cryptic-pocket-atlas-concept.md](./cryptic-pocket-atlas-concept.md)) is explicitly scoped as *the next
program after the preprint posts*, not an alternative to it. Both stay where they are.

---

## 2 · The framings in full

### 2.1 · P1 — the known-answer audit  ★ RECOMMENDED

**Claim.** *Known-answer testing of in-silico paralogue-selectivity pipelines: a full-program audit in which
every instrument was put to a test whose answer was already known, and what the results imply for the
published practice of prospective selectivity prediction.*

The paper's subject is the **instrument register**, not NR4A3. NR4A3 is the worked system.

**Why it is first: it is the only framing whose central claim is *strengthened* by every failure.** Every
other framing on this page has to route around the three failed positive controls. This one is about them.

**What it has, cited to committed artifacts:**

| finding | figure | home |
|---|---|---|
| **The decoy null.** Single-snapshot MM-GBSA `margin > 0` is not a selectivity verdict | **22 of 38** unrelated marketed drugs (**57.9 %**) score a positive NR4A3 margin; **15 of 38 (39 %)** score `confirmed_selective` — caffeine, ibuprofen, lidocaine, phenytoin among them — while the developability-gated de-novo set reaches **2 of 11 (18 %)**, *below its own null* | `DECOY_2026_06_30` in [`selectivity_calibration.py`](../modalities/selectivity_calibration.py); paper §2.6 |
| **…and it replicates at 25× the scale**, which is what makes it a result rather than an anecdote | **97 of 250 (39 %)** at 6,000-compound library scale — the 38-drug false-positive rate reproduced almost exactly | SI §S1 |
| **The noise exceeds the signal it is being asked to resolve** | per-margin **SD ≈ 4–6 kcal/mol**; the best lead `denovo_393` goes **+18.34 → −2.95 ± 3.65** on de-noising, while the negative control stays negative | [next-steps.md](../modalities/nr4a3-degrader-next-steps.md); roadmap [§6a](./nr4a3-program-map.md#6a--dead--conclusively-unworkable-never-retry) |
| **…and single-pass de-noising is not reproducible run-to-run** | AGI-5198 swings **+16.4 vs +6.4** across passes | SI §S1 |
| **⛔ Precision diagnostics are *identically* blind to endpoint-state error — proved, not observed** | the known-answer ternary-cooperativity control returns **−0.599 against a target of +0.944** — the **wrong sign in all three preregistered replicates**, ≈**34×** the statistical uncertainty — *with* converged, structurally stable, forward/reverse-antisymmetric sampling **and a closed cycle**. Under every named error class the closure statistic is identically zero, so the triangle returns a clean `R` whether or not the defect exists | roadmap [§2.11 block](./nr4a3-program-map.md#-the-first-forwardreverse-hysteresis-this-program-has-ever-measured--gate-passed-2026-07-27-214-pm-et); [`valb-triangle-closure.json`](../modalities/valb-triangle-closure.json) `branch_A.verdict: "REFUTED for diagnosis"`, `can_closure_see_that_class: false`; paper §2.11 + SI §S11 |
| **A within-run MBAR SE is not reproducibility** | replicate SD **0.375** against per-leg MBAR SEs of **0.097–0.132** — roughly **3×** | roadmap scoreboard, RUNG 2 · replicates |
| **The absolute free-energy scale misses by more than the margin it is used to compute** | T4-lysozyme L99A·benzene: **+1.90 ± 0.09** against an experimental **−5.2** — under-binding by **≈7.1 kcal/mol** | paper §2.8 (`V7`) |
| **A λ-overlap defect on every leg, disclosed rather than repaired** | solvent leg and all three complex legs each carry ≥1 soft-core-tail window pair below **0.03** | paper §2.8, SI §S7 (`V9`) |
| **An endpoint readout that cannot see a *measured* paralogue difference, on an adequately-powered design** | exact one-sided **p = 0.7468**, mirrored **0.2554**, reference set **462** with a floor of **0.00216** against α = 0.05, **zero** technical failures, statistic **+0.4373 Å** and the direction *opposite* to the source's prediction with all 11 LOMO refits keeping that sign | [`selcal-verdict.json`](../modalities/selcal-verdict.json); paper §2.12a |
| **A biological holdout that could never have served, and the reason is in the test system** | NR-V04 retrospective **DISCORDANT, p = 0.392857**; its selectivity is attributed to a covalent bond at **NR4A1 Cys551**, which NR4A2/NR4A3 lack, so a geometry readout passes for the wrong reason at any *n* | [`nrv04-retro-verdict.json`](../modalities/nrv04-retro-verdict.json), [`nrv04-cys-conservation.json`](../modalities/nrv04-cys-conservation.json); paper §2.12, SI §S12 |
| **A threshold that fails its own positive control** | the `EXPOSED_RSA = 0.25` criterion misses **NR4A1 Cys551** — the one NR4A-family covalent site with literature support — at RSA **0.165** on the opened model and in **0 of 25** metadynamics frames (median **0.064**). What survives is a threshold-free **rank** (C551 is 3/18 family-wide) | [`nr4a3-covalent-handle-ensemble.json`](../modalities/nr4a3-covalent-handle-ensemble.json) (`V17`) |
| **A blind-docking benchmark measures the box, not the docking** | the holo self-dock control failed through the pipeline's own box on **6 of 6 pairs across 3 receptors (17.3–29.3 Å)**, while the same protocol through an fpocket-chosen box reaches **3.04 Å, fnat 0.778, 7 of 9 native contacts**. Verdict **INCONCLUSIVE by its own preregistered rule** | [`apo-pose-recovery.json`](../modalities/apo-pose-recovery.json) (`V3`) |
| **Zero events is not zero rate** | the scrambled-objective control manufactured **0 survivors of 191** against the real campaign's **1 of 191** — which bounds the manufactured rate at **≤0.0157** (rule of three), **3×** the real campaign's own 0.0052, Fisher **p = 0.5**. Narrowed, not excluded | paper §2.7 (`V19`) |
| **A positive control inside the model's training horizon is a harness check, not evidence of generalisation** | 6HAX (2018 deposit, inside a 2023-10-14 horizon) at DockQ **0.618**, stated as memorisation-permitting *by construction*; CRBN + lenalidomide likewise | [`selcal-deepternary-poscontrol.json`](../modalities/selcal-deepternary-poscontrol.json); SI §S2 |
| **A closed cycle in a real production map still opens** | of three cycles in the 18-edge congeneric map, `cycle_3carbonyl` sums to **R = +1.307**, a tolerance violation, so its three edges carry that reservation wherever quoted; and an independent recomputation of one edge disagrees with the pilot by **≈0.78 kcal/mol**, more than either stated uncertainty | [`step1-fanout-map.json`](../modalities/step1-fanout-map.json) `cycle_closure`; paper §2.9 |
| ⛔ **And the strongest meta-finding: a known-answer test is necessary and NOT sufficient** | the program's **largest** retraction fell to a **chain-ordering defect** (Elongin C scored as the target), an **nm/Å unit error** and **contaminated inputs** (14-3-3 ε where Elongin B belongs) — **no known-answer test catches any of those**. The panel persisted **no trajectory**: a read-only census found **72 objects, 19 units, zero trajectory files**, so the defects were *"each correctable in principle and none correctable in practice"* | paper §2.5 banners; roadmap [§3.3](./nr4a3-program-map.md#33--the-pattern--rewritten-because-the-version-this-page-carried-was-false) |

**The message that makes it a paper rather than a lab notebook.** *The prophylactic is two rules, not one:*
**(a)** test every instrument against a known answer before believing it — cheap, and it has never once been
wasted; **(b)** **persist the primary artifact**, because the defects that cost the most were analysis and
input bugs that only a retained trajectory could have let anyone fix. Rule (b) is the one this program was
missing and it is the more expensive of the two. That is a general, actionable, quantified claim about
computational practice, and it is supported by a fully enumerated failure record rather than by exhortation.

**What is still missing.** Genuinely little, and none of it needs a GPU:
1. ⛔ **The MM-GBSA decoy null's primary run output lives in S3, not in a committed JSON.** The roadmap
   already names this as *"the weakest evidence chain in §6a … the only row whose refutation is not readable
   end-to-end from a committed artifact"* ([§6d](./nr4a3-program-map.md#6d--superseded--not-here-and-that-is-deliberate)).
   The 38 margins **are** committed (`DECOY_2026_06_30`) and the arithmetic redoes from them — but for the
   paper whose headline this is, the chain must be end-to-end. **$0 CI.**
2. A single committed census artifact holding all 20 instruments with test / result / scope, so the register
   is a table a reader can check rather than prose. Most rows already have their own artifact; this is a
   collector. **$0.**
3. Honest scoping of the generalisation: this is **n = 1 pipeline**, one target family, one author. The
   claim is *"here is what happened when a full program was audited this way"*, not *"this is what happens"*.

**What only a wet lab could add:** nothing the claim needs. **This is the only framing on the page of which
that is true**, and it is the single most important line in this document given the operating regime.

**Venue / audience.** *J. Chem. Inf. Model.* is the natural home — the $0 subscription route is already
confirmed in writing ([preprint-plan.md](./nr4a3-degrader-preprint-plan.md)) and the audience is exactly the
people running these funnels. ChemRxiv first, as planned. Secondary fits worth checking *before* naming
them anywhere outward-facing (fee models change and the hard constraint is **author pays $0**):
*J. Comput.-Aided Mol. Des.*, and a *LiveCoMS* "Best Practices" article — verify each one's fee route in
writing at submission, per the standing rule.

**Manuscript survival: ~60–70 %, mostly verbatim, reordered.** §2.5 (retraction + the affinity-control
failure), §2.6 (decoy null), §2.7 (multi-snapshot + de-noising), §2.8 (ABFE + T4L + λ-overlap), §2.9 (cycle
violation + edge disagreement), §2.11 (whole), §2.12 (whole), §2.12a (whole, including the DockQ calibration
ladder), §4 caveat 9, §5's preregistered gate tables and deviation log; SI §S1, S7, S8, S10, S11, S12
essentially unchanged. §2.1–§2.4 shrink to a Methods-level description of the system.

**Language discipline: it requires softening nothing, and it *retires* the problem.** Under P1 the phrase
"NR4A3-selective" stops being a claim the paper makes at all and becomes a claim the paper *audits* — which
is precisely the sentence-scoped disclaimed use `lint_claims` R1 already clears. The four substantive R1
warnings in [§6](#6--the-four-substantive-lint-warnings-named) disappear rather than needing a fix.

---

### 2.2 · P2 — where sequence-only co-folding breaks on ternary complexes

**Claim.** *Sequence-only co-folding reproduces the components of a PROTAC ternary complex and not their
assembly — and the failure is localisable, calibrated, and specific to the sequence-only route rather than to
the problem.*

This is the single most **self-contained** publishable unit in the repo. Every objection a referee would
raise has already been answered by running something, and each answer is a committed artifact.

**What it has:**

- **The failure, on both arms, by two independent implementations.** Target↔E3 interface **DockQ 0.023–0.046,
  fnat 0.000** — not one native interface contact — while the internal VHL/EloB/EloC machinery in the *same
  models* scores **0.89–0.97** ([`selcal-cofold-vs-crystal.json`](../modalities/selcal-cofold-vs-crystal.json),
  [`selcal-cofold-dockq.json`](../modalities/selcal-cofold-dockq.json)).
- **Is the scorer sane? — calibrated upward.** DeepTernary on `6HAX_B_A_FWZ` reaches **DockQ 0.618 (CAPRI
  "Medium"), median 0.438 over 16 poses, best iRMSD 1.21 Å** through the identical DockQ 2.1.3 build. ⛔
  Stated as **memorisation-permitting by construction** (2018 deposit, inside the 2023-10-14 horizon)
  ([`selcal-deepternary-poscontrol.json`](../modalities/selcal-deepternary-poscontrol.json)).
- **How wrong is 0.03? — calibrated downward, with a physical ruler.** Holding the E3 fixed and rigidly
  displacing the *true* target chain of 9DTY: **1.000 → 0.948 (0.5 Å) → 0.845 (1 Å) → 0.717 (2 Å) → 0.401
  (4 Å) → 0.240 (8 Å) → 0.085 (16 Å) → 0.026 (32 Å)**. The co-folds sit at the **~32 Å** rung, consistent
  with their independently measured 17.8–21.2 Å interface RMSD — **not a near-miss**
  ([`selcal-dockq-decoy-scale.json`](../modalities/selcal-dockq-decoy-scale.json)).
- **Is the complex reachable at all? — yes, post-horizon.** 9DTY and 9DTX are absent from the disclosed
  4,471-entry exclusion set and deposited after the horizon
  ([`deepternary-leakage-check.json`](../modalities/deepternary-leakage-check.json)); **given both binding
  sites**, the generator reaches **DockQ 0.839 (CAPRI "High"), iRMSD 0.67 Å, fnat 0.83**, best of 16 seeds,
  median 0.442 ([`selcal-deepternary-headtohead.json`](../modalities/selcal-deepternary-headtohead.json)).
  ⛔ A **different and easier question** — the model is told which pocket each end occupies — and it is **one
  arm**: the SMARCA4 arm was refused before prediction (warhead fragment overlap 0.42 against a 0.55 bar), so
  no SMARCA4 number exists. Both facts must travel with the number.
- ★ **The localisation, which is the actual contribution.** Superposing each co-fold on **one protein at a
  time** and measuring the degrader over the native atoms contacting *that* protein (correspondence through
  the reference molecule's atom graph, never by proximity): all 12 models sit within **3.2 Å** of the crystal
  in each protein's own frame — target median **1.83 Å**, E3 median **1.96 Å** — against an assembled
  interface scoring what the true complex scores when displaced **32 Å**. A factor of **10**
  ([`selcal-cofold-decompose.json`](../modalities/selcal-cofold-decompose.json)).
- **⇒ The missing information is the *relative placement of the two proteins*** — exactly what a ternary
  generator is handed when given each end's site. **So a co-folder aimed at ternary complexes must be
  benchmarked on assembly, not on per-chain pocket accuracy.** That is the message, it is actionable, and it
  is aimed at a field currently very active in this exact direction.

**What is still missing.** Nothing the claim needs. Two disclosures are mandatory and already written: the
best-of-16 selection, and the single-arm head-to-head.

**What only a wet lab could add:** nothing. The reference structures are deposited.

**Venue / audience.** *J. Chem. Inf. Model.*, *Bioinformatics*, *Protein Science*, or as a substantial
section of P1. Audience: everyone building or benchmarking co-folding models, which is a much larger
readership than everyone interested in NR4A3.

**⚠ This is the one framing with a real clock (G6).** Ternary co-folding benchmarks are being published now.
The decomposition finding in particular is the kind of result someone else will produce.

**Manuscript survival: ~10 %** — §2.12a's back half, SI §S2's control notes. But it is the densest 10 % in
the document, and none of it is currently the *subject* of anything.

**Language discipline:** clean. It makes no selectivity claim at all.

---

### 2.3 · P3 — target enablement: the NR4A3 cryptic pocket, with no candidate

**Claim.** *A structural and dynamic characterisation of a cryptic pocket on the NR4A3 ligand-binding domain,
its paralogue-divergent lining, and the NR4A3-unique reactive residues around it — presented as a target
dossier, with no binder and no candidate.*

**What it has:**

- **An experimental anchor that is independent of our own machinery.** In the apo NMR ensemble **8XTT**, the
  orthosteric site is matched in **19 of 20** deposited conformers, of which **3** score ≥ D\* = 0.53 — i.e.
  **3/20 across all deposited conformers**, no simulation bias applied
  ([`nr4a3-pocket-reharmonize-summary.json`](../modalities/nr4a3-pocket-reharmonize-summary.json), row
  `8xtt_20conformers`, re-read while writing).
- **Dynamics, reported at the weight the gates actually returned.** Preregistered **Gate 1 failed as
  registered** (F(Rg) monotonic, no separate opened basin) and was **reformulated** to basin-internal
  breathing; **Gate 3A supported** (the seeded geometry persists in 3/3 replicas; ≥ D\* in **0.56/0.40/0.80**,
  pooled **44/75 = 59 %**); **Gate 3B unresolved**, and the single-profile reading of it is ✕ dead
  ([`nr4a3-metad-crossreplica.json`](../modalities/nr4a3-metad-crossreplica.json)). **A dossier can carry all
  three honestly; a candidate paper has to argue past them.**
- **Two orthogonal axes, each with its stated limit.** BioEmu unbiased ensemble, **12.5 % druggable** (`V14`,
  no known-answer test on this system); PocketMiner + four permutation nulls, **p = 0.009 / 0.0001 / 0.036 /
  0.74 / 0.014** — **one of the five does not support it** (`V15`).
- **The divergence, which is the dossier's commercial argument.** Of the **10** Pocket-5 lining residues,
  **7 are paralogue-divergent** (L406, T407, T410, R412, I484, I531, L534) —
  [`nr4a-selectivity.json`](../modalities/nr4a-selectivity.json), `n_residues: 10`, `n_divergent: 7` — against
  **≈57 % identity** LBD-wide (254 aligned, 109 divergent;
  [`nr4a3-differential-surface-atlas.json`](../modalities/nr4a3-differential-surface-atlas.json)). ⚠ And the
  narrowing the paper already carries in three places: against **NR4A2 only 6 of 7 differ** (I531 is Ile in
  both), so of the 5 engageable handles only **4** distinguish NR4A3 from NR4A2.
- **A whole differential surface, gated GO.** **33** exposed, divergent-vs-both, character-changing handles of
  254 aligned residues (137 exposed, 109 divergent) — and the SMARCA2/SMARCA4 selectivity that a real
  clinical-stage degrader exploits rests on **one** such position.
- **The categorical chemistry, as a sequence fact.** **20** NR4A3 cysteines, **4 unique vs both paralogues**
  full-length = **3 in the LBD** (C397, C420, C559) **+ C166 outside the modelled construct**; and **4 unique
  lysines**, of which **K518 / K572 / K592** are exposed at 13.4 / 11.5 / 16.2 Å from the pocket
  ([`nr4a-paralogue-unique-residues.json`](../modalities/nr4a-paralogue-unique-residues.json)). ⚠ The
  construct boundary is load-bearing and is `R13` in miniature: C166 is unavailable to any LBD-anchored design.
- **★ Lane 13, which is in the roadmap and NOT yet in the paper.** Over **300 matched conformers** (100 each
  for NR4A3/NR4A1/NR4A2: 25 metadynamics + 3 × 25 unbiased release) and **73,867 matched placements**, the
  probability that no paralogue cysteine is reachable given the construct reaches an NR4A3-unique one is
  **exactly 1.000 on solvent-exposed cysteines in every scope**. ⚠ Report it as the rare-event statistic it
  is: only **122 of 73,867** placements (**0.17 %**) satisfy the conditioning event, so the defensible claim is
  *zero co-labelling events observed*, not a probability quoted to five figures.
- **A superfamily bound.** All **47** reviewed human NRs screened; the paralogues behave as positive controls
  must (NR4A2 4/10 at overall identity 0.58; NR4A1 3/10 at 0.51) and only **MR (3/10, handles 406/407)** and
  **AR (3/10, handles 407/410)** clear the confidence gate as non-paralogue flags
  ([`nr4a-superfamily-selectivity.json`](../modalities/nr4a-superfamily-selectivity.json)). A **shortlist, not
  a clearance** — stated that way in SI §S3 already.

**What is still missing:**
1. ⚠ **A branch-drift repair before the ortholog-invariance claim can be cited.** *"All ten lining residues
   ortholog-invariant across six species spanning ~300 My"* is one of this framing's best sentences, and its
   owning artifact **`nr4a-resistance-map.json` is not on this branch and not on `main`** — checked while
   writing: it exists only on `origin/modalities-cache`, and its producer runs soft-fail. The **"~300 My"**
   figure is in no artifact at all; it is a literature inference carried in prose. **Port the artifact to
   `main` and source the timescale, or drop the sentence.** ($0; CLAUDE.md §7.)
2. **`R3`, the frame-level submission gate** — the roadmap's *cheapest open item in the program*, **$0-to-cheap**.
3. **The `V17` positive-control failure must appear in the paper.** It currently appears **nowhere** in the
   paper or SI, while the paper reports its preregistered **Tier 0** gate as *"pass on both axes"* on the
   strength of the word **exposed**, adjudicated by that same cutoff. The roadmap flags this as a manuscript
   finding. Under P3 the honest form is the threshold-free **rank** plus the disclosure.
4. Nothing else. `R4` — *does anything bind the cryptic pocket* — is **not** a gap for this framing, because
   P3 does not claim anything does.

**What only a wet lab could add:** a thermal-shift / SPR / NMR fragment screen against the opened site. ★ **It
is not required for the claim as scoped** — and the dossier's most valuable feature is that it **specifies
that experiment as its own falsification**, with a negative as useful as a positive. That is the
publish-to-convince lever, made concrete.
⚠ Scoping word is load-bearing: **NR4A3 is already experimentally ligandable** (a fragment screen, hit rate
<1 %, elaborated to a low-micromolar inverse agonist that shifted NOR-1-regulated gene expression in cells).
What has no ligand is *the cryptic site*. Dropping that word makes the dossier contradict its own §1.

**Venue / audience.** *J. Chem. Inf. Model.*, *Protein Science*, *Proteins*, or *Biochemistry*. Audience:
structural biologists and target-enablement groups — including the SGC, already on the outreach list
([outreach-emails.md](./nr4a3-degrader-outreach-emails.md)). **A dossier is a much more natural thing to hand
a structural lab than a candidate**, which is the whole outreach mechanism.

**⚠ Clock (G6): real.** 8XTT has been public since 2025-01-15 and there is still no published pocket-dynamics
analysis of NR4A3. That is this framing's novelty and anyone can now run metadynamics on the same deposit.

**Manuscript survival: ~35–40 %** — §1, §2.1, §2.2, §2.3, §2.4, the categorical census out of §2.10, SI §S3 —
**plus Lane 13, which is currently unpublished.**

**Language discipline: it requires softening nothing, because it drops the claim.** Every R1 warning in the
paper and SI attaches to a candidate or a design objective. P3 has neither.

---

### 2.4 · P4 — the resolution budget

**Claim.** *Prospective computational paralogue selectivity is not currently decidable by free energy, and
the arithmetic says so before any particular method is blamed.*

**The whole argument in three measured numbers, all with one home in the roadmap's
[MECHANISM-FIRST](./nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged) section:**

| quantity | value | what it is |
|---|---|---|
| **required** | **~2.0 kcal/mol** of true margin (median over 27 potency scenarios, range 1.75–2.25) | what a useful degradation window needs — [`selectivity_margin_model.py`](../modalities/selectivity_margin_model.py) |
| **resolvable** | **0.60 kcal/mol** best case | `minimum_detectable_difference(0.375, 3)` — **derived, never typed**, off the *measured* replicate SD |
| **accurate to** | **1.543 kcal/mol, wrong sign** | the one known-answer test of this exact quantity class |

**⇒ The margin that must be detected is ~3.3× the measured noise floor, and the one calibration attempt on
the relevant quantity class missed by most of the required margin *in the wrong direction*.** The binding
constraint is **accuracy, not precision** — which matters because it means the remedy is a calibrator, not
more sampling, and *"more replicates"* is refuted rather than merely expensive.

**Why this is worth writing down.** The field publishes prospective selectivity predictions constantly and
publishes the resolution budget essentially never. This is a short, sharp, checkable argument
(`tests/test_selectivity_margin_model.py` asserts the derivation) that tells a reader what size of effect
their method has to see before they run it.

**The two caveats that must travel with it, or it over-claims:** the **2.0** is a model over potency
scenarios, not a measurement; and the **0.375** SD was measured on the **SMARCA2/VHL** calibrator and is
*transferred* to NR4A exactly as the program's cost bases are — and it is an **upper** bound on sampling-only
scatter, because it also carries model-swap and independent-solvation variance.

**Recommendation: this is P1's spine, not a separate paper.** As a standalone it is a Perspective built on one
model and one measurement; as the framing argument of P1 it explains *why* every instrument in the register
failed the way it did. Named separately here so it does not get lost inside a table of failures. If it were
to stand alone, the venue is a Perspective/Opinion slot (*Drug Discovery Today*, *Expert Opin. Drug Discov.*)
— **verify the fee route in writing first**, per the hard constraint.

---

### 2.5 · P5 — categorical beats marginal: a close-paralogue design principle

**Claim.** *For close paralogues, selectivity should be sought first in **categorical** differences — a
residue the paralogue does not have — because the **marginal** route requires a margin larger than
free-energy methods can currently resolve; and for a linker-borne categorical handle, **linker length is
itself the selectivity filter**.*

**What it has:**

- **The margin arithmetic of P4**, which is the reason the principle exists.
- **The categorical census** — the sequence facts of P3, which are pose-independent.
- **★ The linker-length filter, at its landed values.** Reach-only paralogue-collision probability over
  **73,867 matched placements across three scopes**: **0.000–0.003 at 12 backbone atoms · 0.054–0.133 at 16 ·
  0.263–0.383 at 20** ([`nr4a-paralogue-dynamics.json`](../modalities/nr4a-paralogue-dynamics.json) →
  `categorical_verdict.by_scope[*].by_linker_atoms`, read while writing). **Every extra linker atom is a
  selectivity cost, not just a synthesis cost.**
- **★★ And the finding that makes the principle defensible rather than circular** — from
  [`categorical-axis-audit.json`](../modalities/categorical-axis-audit.json), in its own words: *"At the
  12-atom design gate the exposure filter carries almost nothing… so the headline gate result does NOT rest
  on the criterion that failed its positive control. The filter becomes load-bearing at 16 atoms and dominant
  at 20."* **At the gate the claim stands on reach alone; at 16–20 atoms it does not.** That is exactly the
  kind of scoped, self-auditing statement a design principle needs.
- **Reciprocal uniqueness — a genuinely new observation.** In **30 of 30** graded cells the *first* cysteine
  to come into reach is a **paralogue** one, not an NR4A3 conserved one. ⚠ **Which** one differs by
  convention and must not be merged: through-space it is **NR4A1 C505** in 24/30, which aligns to NR4A3
  **C536** — so NR4A3 *does* carry a cysteine there and the reciprocal-uniqueness reading does not apply to
  it; under corridor it is **NR4A2 C534** in 23/30, aligning to NR4A3 **S565**, which NR4A3 genuinely lacks.
  **A residue-uniqueness argument built only on "which of my residues do they lack" is incomplete by
  construction** — and that is a transferable methodological point, not an NR4A one.
- **A real negative on E3 breadth**, which strengthens rather than weakens the principle: of 10 recruiters,
  **structural stageability** (not target availability) is the binding constraint — RNF114 has no deposited
  structure, DCAF16's ligand is 34 % buried with its partner removed, DCAF15 has no partner-free liganded
  structure — and the widening **left CRBN + VHL standing** rather than displacing them.

**⛔ What is still missing, and it is the reason this ranks fifth:**

1. **The causal test has run and returned its preregistered null.** **S = −0.1297 ± 0.3264 kcal/mol**, a
   **bound** excluding a marginal wedge of **|S| ≳ 0.65 (2σ)**
   ([`nr4a3-5aks-reduction.json`](../modalities/nr4a3-5aks-reduction.json)). It is *not* a failure — it was
   registered in advance as the likely outcome and explicitly not a stop, and it is structurally incapable of
   testing the *categorical* mechanism because it models no bond in either leg. **But it means the paper
   cannot say a designed element *creates* discrimination**, and `V16` **has no known-answer calibrator**, so
   the null may be read as a bound and may not be reported as calibrated (Open decision 13).
2. **⛔ The transferability claim has NO evidence in this repo.** *"Is that principle transferable beyond
   NR4A?"* — nothing here answers it. The only precedent named (NR-V04 at NR4A1 Cys551) is **inside the
   family**. ★ **The fix is cheap and unbuilt**: a cross-family survey asking how often close human paralogue
   pairs present a unique, solvent-exposed nucleophile or lysine within tether range of a druggable pocket.
   That is sequence + structure mining — **$0 CPU / free CI** — and it is the single addition that converts
   P5 from a case study into a principle. It does not exist on any rung.
3. **The chemistry is untestable here and must be said so, prominently.** No thiol pKa, nucleophilicity,
   adduct stability or promiscuity is modelled anywhere in this program; a covalent handle is an **unresolved
   liability, not an upgrade**, and must be reported alongside the parent warhead chemotype's own **MYC
   de-repression**. Reach is necessary and never sufficient.
4. The chemistry axis is **one residue deep with no geometric fallback** — C420 needs 16 atoms and C559 20,
   both paid from the same budget that must span to the E3, and both reach the gate in **0 of 75** unbiased
   frames.

**G4 — ⚠ this framing DOES require care with a claim the program already makes.** Two places:
- The roadmap's [§Program and thesis](./nr4a3-program-map.md#mechanism-first-is-the-search-order-the-thesis-above-is-unchanged)
  and its Tier-2 gate block still carry the **superseded 2026-07-25 A2 pilot** collision profile — *0 at 12,
  **0.081** at 16, **0.258** at 20*, 5,657 placements, static models only — as the live design consequence,
  while `categorical-axis-audit.json` records the landed matched run (73,867 placements, three scopes) and
  states that **the pilot understates the 16-atom collision by ~1.6×**. One fact, two values. **Reported, not
  edited** — see [§7](#7--cross-checks-taken-while-writing-this-all-0).
- The **"honest cut-off is 14 backbone atoms"** is a reach-only bound from four points on static models and
  was explicitly **declined as a gate** for two stated reasons. A design-principle paper must present it that
  way or it manufactures a rule the data does not carry.

**What only a wet lab could add:** the entire chemical axis — pKa, reactivity, adduct stability, and above
all **electrophile promiscuity**, which needs chemoproteomics. P5 can state the geometric principle and must
explicitly decline the chemical one.

**Venue / audience.** *J. Chem. Inf. Model.* or an *RSC Med. Chem.* / *Chem. Sci.* perspective — audience is
degrader design groups. **With** the cross-family survey it is a principle paper; **without** it, it is an
NR4A case study and should be a section of P3 instead.

**Manuscript survival: ~20–25 %** — §2.10, §2.10e, §4 caveat 8, §5's Tier ladder — plus a large amount of
roadmap material that has never been in the manuscript.

---

### 2.6 · P6 — the candidate paper (the current plan)

**Claim, as currently titled:** *"In silico design of a paralogue-favoured ligand for a cryptic NR4A3 pocket."*

★ **Note what the title already concedes.** It has migrated **twice** down the claim ladder — "degrader" →
"binder"/"ligand" (2026-07-10, the review correctly flagged "degrader" as an overclaim) and "selective" →
"**favoured**". The title is already standing in P3 territory while the SI still carries a heading reading
**"Lead — NR4A3-selective (the validated path)"**. That gap is the clearest single symptom that the framing
and the evidence have come apart.

**Graded honestly against the map:**

- ⛔ **G1: 0 of 16 requirements stand on an instrument validated in the regime the claim needs**
  ([§3.2](./nr4a3-program-map.md#32--the-rv-coverage-matrix--where-the-holes-are)). Five requirements have
  **no instrument at all** (`R3`, `R4`, `R6`, `R13`, `R14`); five more have an instrument that has returned
  **no usable answer** (`R2`, `R5`, `R9`, `R11`, and `R7`'s own control is unrun).
- ⛔ **All three attempts at a positive control for selectivity detection have run and none succeeded**, so
  the paper's own §4 states that **every paralogue-selectivity statement in this work is an unvalidated
  prediction** — carried in the Abstract, §2.12a and §4.
- ⛔ **`R7` is blocked by three things and only one is the instrument**: `V4` (unrun, **not authorized**, and
  on **no rung** — it appears nowhere in the ordered plan); `R6`, the per-paralogue opening penalty **nobody
  has ever computed**, which validation requirement 2 says can *miss or **reverse*** selectivity; and the
  resolution budget of P4, which **a passing `V4` would not fix**.
- ⛔ **`R9`: no NR4A3 ternary has been correctly assembled by anyone**, and the existing one's molecule is
  **unrecoverable** — no `_chem_comp_bond` loop in any of the three models
  ([`nr4a-ternary-ligand-provenance.json`](../modalities/nr4a-ternary-ligand-provenance.json)) — so §2.5's
  ternary result cannot be replicated or extended at any price.
- ⚠ **G3: it needs a bench.** `R4` — *does anything bind the opened cryptic pocket* — has **no in-silico
  instrument, ever**. The candidate framing is the only one on this page whose headline is hostage to that.

**In fairness, what P6 genuinely has** (and it is not nothing): a falsification-controlled funnel with a
preregistered gate ladder and a disclosed deviation log; a candidate that survives multi-snapshot de-noising
and clears a same-tier decoy null **in its design frame**; three-replicate conditional ABFE receptor
contrasts; an 18-edge congeneric ΔΔG map; a chemistry-verified 54-construct virtual library; and — a real
asset — a *published record of its own retractions*.

**★ Two things worth saying plainly.** First: **P6 is not wrong, it is mis-titled.** Every result in it is
honestly reported; what does not hold is the *organising promise* that the paper is about a candidate.
Second: **P6 is not free even after its content is written**, because the gap between what the title promises
and what §4 concedes is exactly the gap a referee attacks, and defending it costs revision rounds that P1/P2/P3
never enter.

**Manuscript survival: 100 %, by construction.**

**Roadmap items P6 would still want**, all already listed and none of them cheap-and-decisive together:
`5b-T` (rebuild the ternaries by the assembly route — **$0 CPU, needs no authorization, and nobody has run
it**), the `R3` audit ($0), the branch-1b reconciliation ($0), the pose re-run with site and docking separated
(cheap CPU), then `V4`, `R6`, the matched 8XTT-anchored paralogue legs, and `R14` — of which **five have no
rung, no gate and no price anywhere**.

---

### 2.7 · P7 — the benchmark / infrastructure suite

**Claim.** *A reusable, preregistered known-answer test battery for in-silico selectivity pipelines, plus the
bookkeeping discipline that makes a negative result durable.*

**What it has:** the 20-instrument register with its scope column; the R×V coverage matrix; the six
invariants; the **claim-ceiling rule** (*a requirement may never be claimed above the validation status of
the instrument that produces it*); the closed-route register — checked while writing: **18 ✕ dead rows
(10 scientific + 8 operational), 10 ⏸ parked, 10 🔒 held**; `lint_claims.py` (R1–R5) and
`lint_consistency.py` running in CI over the manuscript, the SI and the roadmap;
[`pinned-figures.json`](./pinned-figures.json); and the preregistrations with their deviation logs and
numbered amendments.

**What is missing, and it is structural:** **n = 1**. A benchmark is a benchmark when someone other than its
author runs it on something other than its origin system. Converting this into a paper means packaging the
battery as runnable code with worked examples on a second target — free in engineering terms, but genuinely
months of scope, and it is the classic expansion that eats the time meant for the lead program.

**Venue:** a JCIM Application Note or a *LiveCoMS* Best Practices article (**verify the fee route** — the hard
constraint is author pays $0). Realistically the weakest venue fit of the serious options.

**Recommendation: not a paper yet. Ship it as the Data & Software Availability section of P1**, where the
apparatus is evidence rather than product.

---

## 3 · The recommendation

> ### ⭑ Lead with **P1 — the known-answer audit** — and it is not the current framing.

**The evidence for that, stated as the map states it:**

1. **P6's own scoreboard is the argument.** *Seven gates passed, four failed.* Three of the four failures are
   the three attempts to establish a positive control for the exact capability P6's title promises, and the
   paper already concedes the consequence: **every paralogue-selectivity statement is an unvalidated
   prediction.** A paper whose Limitations section retracts its own title is a paper that has already been
   written into a different framing.
2. **P1's central claim needs no instrument to pass.** Under G1 this is decisive, and it is unique to P1, P2
   and P4 on this page. Every other framing has to route around the same three nulls.
3. **P1 needs no bench.** Under the operating regime — one researcher, no wet lab, no race — this is the
   binding constraint, and P6 fails it at `R4` with no in-silico substitute existing.
4. **P1 requires softening nothing.** It *removes* the claim the four substantive lint warnings attach to.
   No retraction, no hedging round, no gap for a referee to attack.
5. **P1 has the widest audience.** A false-positive rate of **22 of 38 (57.9 %)** for a scoring function that
   thousands of papers use as a selectivity filter — replicated at 6,000-compound scale at **39 %** — is a
   general-interest negative. NR4A3 is a rare-cancer target of interest to a few dozen people.
6. **P1 is the cheapest to finish.** ~60–70 % of the manuscript survives largely verbatim; the outstanding
   work is one $0 CI job to bring the decoy null's primary output into a committed artifact, one $0
   instrument-census collector, and a re-ordering pass.
7. **And it is the one the record actually earned.** The failure register here is more complete, more
   quantified and more honestly scoped than most published method papers manage — three known-answer tests
   run to completion and reported at their true weight, a decoy null replicated at two scales, a proof that
   the program's favourite convergence diagnostic is blind to its own defect, a co-folding failure localised
   to a factor of 10 with the scorer calibrated in both directions, and 18 conclusively closed routes with the
   evidence that closed each. **That is the asset. It should be the paper, not the appendix to one.**

**Then P2, then P3** — see [§4](#4--the-split-and-the-order).

**And P6 does not die; it is demoted from a paper to a section.** Its honest form is a *"what a candidate
would require"* discussion inside P3 — the requirement graph, the three blocks on `R7`, and the specified
bench experiment — which converts a weak headline into a strong closing argument and keeps every result in
print.

---

## 4 · The split, and the order

**Three papers, in this order.** The argument for the order is not "best first"; it is dependency and clock.

| | paper | why here | what it needs first |
|---|---|---|---|
| **1st** | **P1** (with **P4** as its framing argument and **P7** as its Data & Software section) | Needs nothing we do not have. Establishes the author's calibration in public, which is what makes 2nd and 3rd credible: a target dossier from a group that has already published *why its own selectivity methods failed* reads very differently from one that has not | the two $0 items in [§2.1](#21--p1--the-known-answer-audit--recommended) |
| **2nd** | **P2** | ⚠ **the only one with a live clock.** Self-contained, fully committed, and it is the result someone else will publish. Arguably it should go *first* on clock grounds — the reason it does not is that it is also a natural, strong section of P1, and splitting it costs P1 its sharpest chapter | nothing |
| **3rd** | **P3** (absorbing **P6** as its closing "what a candidate would require" section, and **P5** as a design-principles section unless the cross-family survey gets built) | Its clock is real but slow. It benefits most from P1 existing, and it is the paper that carries the outreach — a dossier plus a specified decisive experiment is what a structural lab can act on | the `nr4a-resistance-map.json` branch-drift repair; `R3`; and the `V17` disclosure |

⚠ **The one genuine risk of splitting**, and it should be named rather than discovered: **a parallel condensed
draft drifted out of sync and self-contradicted once already**, which is why this program collapsed to a
single deliverable in the first place. Splitting is only safe if each paper has **exactly one home for every
shared number** and the shared numbers are read from committed artifacts, not copied between drafts —
i.e. the same rule that already governs the roadmap, applied across manuscripts. `lint_consistency.py`
already runs over multiple documents and is the mechanism.

**If only one paper is ever written: write P1.**

---

## 5 · What every framing has to fix regardless

Four items, all $0, all independent of which framing wins:

1. **The SI heading `**Lead — NR4A3-selective (the validated path):**`** (SI:229) contradicts the paper's own
   §4 in two words at once — *selective* and *validated*. Under P1/P2/P3 the section it heads may not survive
   at all; under P6 it must change today.
2. **The `V17` positive-control failure has to appear in the manuscript.** The paper reports its Tier 0 gate
   as *"pass on both axes"* on the strength of the word **exposed**, adjudicated by a cutoff that misses the
   one NR4A-family covalent site with literature support in 0 of 25 frames. Currently mentioned nowhere in
   the paper or SI.
3. **`nr4a-resistance-map.json` must reach `main`** before the ortholog-invariance sentence is quoted
   anywhere, and the "~300 My" figure needs a source or must be dropped.
4. **The decoy null's primary output must be a committed artifact**, not an S3 object. It is the single most
   load-bearing negative in the repo under P1 and the weakest evidence chain in §6a under any framing.

---

## 6 · The four substantive lint warnings, named

`lint_claims.py` reports **0 ERROR, 50 WARN** across the paper, the SI and the roadmap. Most are R4-`confirms`
warnings on operational prose. **Four are substantive** — each asserts a selectivity property as a structural
label (a heading, a matrix-cell name, a candidate tag) rather than in a sentence that scopes it, which is why
the sentence-scoped disclaimer logic does not clear them:

| # | where | text | why it is substantive |
|---|---|---|---|
| **1** | `nr4a3-degrader-paper-SI.md:229` | `**Lead — NR4A3-selective (the validated path):**` | ⛔ **the worst.** Asserts *selective* **and** *validated*, against the paper's own "every paralogue-selectivity statement … is an unvalidated prediction" |
| **2** | `nr4a3-degrader-paper.md:594` | `### 2.4 Selectivity handles for an NR4A3-selective (NR4A1/2-sparing) warhead` | a **section heading** asserting the property the paper's controls failed to establish |
| **3** | `nr4a3-degrader-paper.md:614` | "…the *same* opened pocket be tuned **NR4A3-selective** … an NR4A3-selective agent" | asserts tunability as demonstrated; it is a specification |
| **4** | `nr4a3-degrader-paper-SI.md:323` | "NR4A3-selective (engaging the divergent handles; lead `denovo_401`)" | attaches the property to the named candidate |

Borderline, same class, worth a look: SI:257 and SI:272 (matrix-mode labels). Cleanly hedged and correctly
passing as WARN-only: paper:162, paper:959, paper:996, SI:302, SI:596 — each is contrastive or negated.

**Under P1, P2 or P3 all four cease to exist rather than needing a rewrite**, because none of those framings
makes a candidate-selectivity claim. That is a real, if unglamorous, argument for the re-framing.

---

## 7 · Cross-checks taken while writing this (all $0)

Per CLAUDE.md §4 — *a $0 observation is never "watching"*. Each of these was cheap, so each was taken rather
than deferred, and two of them changed a sentence in this file.

| # | check | result |
|---|---|---|
| 1 | Recomputed the decoy null from `DECOY_2026_06_30` rather than quoting it | **22 of 38 positive (57.9 %)**, p95 ≈ **+13.1**, range −8.89…+16.46 — matches the paper |
| 2 | Verified 30 cited artifacts are committed at `HEAD` on this branch | **30 of 30 present** |
| 3 | `nr4a-resistance-map.json` | ⛔ **absent** from `HEAD` **and** from `origin/main`; **present** on `origin/modalities-cache`. The roadmap's caveat is correct and the drift is live |
| 4 | Re-read `nr4a3-pocket-reharmonize-summary.json` row `8xtt_20conformers` | `n_propagated: 20`, `n_detected: 19`, `n_ge_dstar: 3`, `d_star: 0.53` — matches |
| 5 | Counted the closed-route register rather than quoting a remembered count | **18 ✕ (10 science + 8 operations), 10 ⏸, 10 🔒.** ⚠ The framing brief that commissioned this file said *"13 approaches were conclusively closed"* — that figure appears nowhere in the register and is **low**. Corrected here; the register is the home |
| 6 | Read `nr4a-paralogue-dynamics.json` → `categorical_verdict.by_scope[*].by_linker_atoms` directly | reach-only collision **0.000 / 0.00124 / 0.00290 @12**, **0.05444 / 0.13331 / 0.12564 @16**, **0.2633 / 0.38254 / 0.37477 @20**. **⚠ FINDING — reported, not edited: the roadmap still carries the superseded 5,657-placement pilot profile (0 / 0.081 / 0.258) as the live design consequence in at least two places**, while `categorical-axis-audit.json` records the landed 73,867-placement values and states the pilot understates the 16-atom collision by ~1.6×. One fact, two values (rule 1) |
| 7 | Read `EXPOSED` collision by scope | exposed-cysteine collision is **0.0 in the static and unbiased scopes at every length**, but **non-zero in `metad_biased` at 14/16/20** (0.00024 / 0.0017 / 0.00195) — because NR4A2 C534 reaches RSA 0.2578 there, above the cutoff. Any P5 sentence saying "zero at every length" must scope to the unbiased ensemble |
| 8 | Ran `lint_claims.py` and read every warning in the paper and the SI | 0 ERROR, 50 WARN; the four substantive ones are [§6](#6--the-four-substantive-lint-warnings-named) |
| 9 | Ran `lint_claims.py` against **this file** | **0 ERROR, 12 WARN** — stated rather than claimed clean, because the first draft of this row said *"0 WARN"* and running it refuted that. All 12 are benign and were read individually: **3** are the file **quoting the offending strings it is flagging** (lines 414, 575, 608), **6** use *validated* in the roadmap's own instrument vocabulary — *"validated instrument"*, *"validated in the regime the claim needs"* — **1** is *"confirmed in writing"* about a journal fee policy, **1** is *"proof that"* about a mathematical identity (closure is identically zero for an endpoint-state error), and **1** is the word *Establishes* about publishing calibration. **No regulated claim is asserted anywhere in this file.** If it is ever added to `DEFAULT_TARGETS`, expect these 12 and grade them against this row |

### Findings that belong to other documents (⚠ NOT edited here — other agents hold those files)

| # | file | finding |
|---|---|---|
| **A** | [nr4a3-program-map.md](./nr4a3-program-map.md) — §Program and thesis (CATEGORICAL bullet) and the Tier-2 "gate PASSES" block | Both quote the **superseded 2026-07-25 A2 pilot** collision profile (*0 at 12, 0.081 at 16, 0.258 at 20*; 5,657 placements, static models) as the current design consequence. The landed matched run is **0.000–0.003 / 0.054–0.133 / 0.263–0.383** over 73,867 placements and three scopes, and `categorical-axis-audit.json` says the pilot **understates the 16-atom figure by ~1.6×**. Suggested fix: quote the landed values, register the pilot pair as superseded |
| **B** | [nr4a3-degrader-paper.md](./nr4a3-degrader-paper.md) + [SI](./nr4a3-degrader-paper-SI.md) | The `V17` positive-control failure (NR4A1 Cys551, 0 of 25 frames, median RSA 0.064) appears **nowhere**, while §5's Tier 0 gate is reported as *"pass on both axes"* on the word *exposed*. Already logged as a manuscript finding in the roadmap's §12; repeated here because it bears on **three** of the framings above |
| **C** | [nr4a3-degrader-paper-SI.md](./nr4a3-degrader-paper-SI.md):229 | `**Lead — NR4A3-selective (the validated path):**` — see [§6](#6--the-four-substantive-lint-warnings-named) |
| **D** | [nr4a3-degrader-preprint-plan.md](./nr4a3-degrader-preprint-plan.md) | Its "Results status" block is dated **2026-07-01** and predates the three failed positive controls, the causal null, the congeneric map and the 8XTT harmonisation. Its *venue and fee* research is still current and valuable; its *readiness* assessment is not, and a reader could take the checklist as live |
| **E** | new work, on no rung | **The cross-family categorical survey** — how often close human paralogue pairs present a unique, exposed nucleophile or lysine within tether range of a druggable pocket. **$0 CPU / free CI.** It is the one addition that turns P5 from a case study into a principle, and it exists nowhere in the plan |

---

*Written 2026-08-02 on `claude/nr4a1-protac-positive-control-xnszjl`. No file outside this one was modified;
the roadmap, `nr4a3_linker_design.py` and the linker library were read only.*
