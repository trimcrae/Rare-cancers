> **Role:** decision record — paper positioning/framing for the degrader work. Supersedes the
> EMC-led framing *for this paper's lead*; see the divergence note at the bottom re: the repo mandate.

# Positioning: lead with the NR4A3 degrader, not EMC

**Decision (2026-06-25, trimcrae).** The degrader paper should be framed as **the computational design
of a selective NR4A3 degrader**, with EMC as *one* motivating disease rather than the headline.
Rationale (user): journals and drug developers don't care about the repo's internal EMC-first mandate;
the paper should lead with what is actually compelling to that audience. "Just because [EMC] is our
goal doesn't mean it's what the paper should lead with — we have to be realistic."

This is well-founded technically: **essentially nothing in the degrader pipeline is EMC-specific.** The
EMC fusion is EWSR1's N-terminus joined to a near-intact NR4A3 (DBD + LBD); the LBD we drug is identical
in the fusion and in wild-type NR4A3. Every component — AF2 LBD model, fpocket Pocket-5, the cryptic-
pocket metadynamics, the calibration, the warhead/E3 design, the selectivity-handle analysis vs
NR4A1/NR4A2 — is **NR4A3-generic**. (The genuinely EMC-fusion-specific routes — junction-ASO,
fusion-neoantigen immunotherapy, the outcomes registry — are *separate* and not part of the degrader
paper.)

## Lead framing
**Title direction:** *"Computational design of a selective NR4A3 degrader: a cryptic-pocket route to a
'ligand-independent' nuclear receptor."*

**Contribution (what we actually demonstrate — keep honest):**
1. The NR4A3 orthosteric pocket, occluded/borderline in static models (fpocket 0.495, below the
   calibrated drug-bound NR band of 0.53–0.68), **opens to a druggable state under metadynamics**
   (opened-frame fpocket 0.751 > D\* 0.53; preliminary, 5 ns) — the first pocket-dynamics evidence for
   NR4A3, precedented by Nurr1 (de Vera 2019) and Nur77 MD work.
2. A selectivity map (7 NR4A3-vs-paralogue handles) enabling a tunable selectivity profile.
3. A degrader/E3 ternary design pipeline primed on that pocket.
*This is an in-silico design + feasibility study; no molecule is synthesized.*

## Scope evolution (2026-06-26, trimcrae): a programmable family-wide selectivity matrix
**Decision.** Run the *same* cryptic-pocket metadynamics on **NR4A1 and NR4A2** (one target-agnostic
pipeline; paralogue CV/LBD mapped to NR4A3 by BLOSUM62 alignment) to build **state-matched opened-pocket
ensembles for all three paralogues**, then dock one library into each → a per-candidate **selectivity
fingerprint** across the family. Rationale (user): "we could make a whole matrix of drug candidates
attacking any combination of NR4A versions… the paper could get even more applications for not much more
work." Two reasons this strengthens the paper rather than just enlarging it:
- **Rigor:** docking opened-NR4A3 vs *static* NR4A1/2 biases toward false selectivity (the paralogue
  pockets are likely cryptic too — de Vera 2019; Nur77 MD). State-matched ensembles remove that confound.
  This is the answer to the reviewer question "how do you know it won't bind the paralogue without MD on it?"
- **Reframe (not just scope):** the paper becomes *"one cryptic-pocket method → programmable NR4A-family
  selectivity,"* turning the divergent-handle map (§2.3) into a *demonstrated, tunable* design axis.
**Honest bound (keeps the prior decision's safety logic):** the *binder* matrix is cheap, but the
*application* matrix is gated by degradation **direction** (degrading neuroprotective Nurr1/NR4A2 in PD is
wrong-direction) and bounded by the **NR4A1+NR4A3 = AML anti-target** (Mullican 2007). So pan-NR4A is a
deliberate *second design mode* (ex-vivo/transient immuno), not blanket new indications — the "Contingency
only" framing below is upgraded to "second design mode," but its safety bound is unchanged. Docking remains
triage; quantitative selectivity needs MM-GBSA/FEP on the state-matched ensembles. Executed: paper §2.4/§3/§5
rewritten; `gpu-metad-aws.yml` parameterized; NR4A1 (run 28256669839) + NR4A2 (run 28256671172) metad launched.

## Indication stack (CORRECTED 2026-06-25 — the EMC drug must be NR4A3-selective, so lead with
## indications that want NR4A3 down AND NR4A1/2 spared; sourced in `nr4a3-degrader-broader-indications.md`)
**Lead (NR4A3-selective — the same molecule):**
1. **EMC** (EWSR1/TAF15::NR4A3 fusion) — clean single-driver proof-of-concept.
2. **Acinic cell carcinoma of the salivary glands** — NR4A3 *over-expression* via enhancer hijacking
   (Haller, *Nat Commun* 2019); NR4A3 is the driver; a selective degrader applies directly and AciCC is
   **more common than EMC** — the key second indication.
3. **Other NR4A3-rearranged sarcomas** (EMC fusion-variant spectrum).

**Contingency only (NOT motivation):** immuno-oncology / T-cell exhaustion needs **pan-NR4A** degradation
(triple-knockout; Chen *Nature* 2019) — the *opposite* selectivity to EMC; relevant only if the agent
proves non-selective. (Earlier drafts wrongly headlined this for a *selective* drug — corrected.)

**Contraindication:** NR4A1/NR4A3 are myeloid tumour suppressors (loss → AML; Mullican 2007); NR4A3 also
tumour-suppressive in HCC/breast/lymphoma. Bounds the set and mandates NR4A1-sparing selectivity.

## What this changed downstream (EXECUTED 2026-06-25)
- **[`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)** created as the lead, target-centric result
  paper (cryptic-pocket druggability, selectivity, degrader design; EMC the lead indication of several).
- **`emc-treatment-roadmap.md`** re-bannered as the EMC-program paper; §4.1/§7 now cite the split-out
  degrader paper for the in-silico degrader results.
- **`README.md`** updated from "exactly ONE manuscript" to the two-paper structure.
- **`CLAUDE.md`** PRIMARY FOCUS updated: lead vehicle = the NR4A3-degrader paper, *serving* (not
  replacing) the EMC goal — per the user's framing that the steering-doc goal still applies and the
  split paper is how we accomplish it. (AGENTS.md not edited; CLAUDE.md is the agent-facing TL;DR.)

## Update (2026-06-26, trimcrae): the ASO joins the degrader as the second priority paper
The degrader remains the lead, but it is **NR4A3-selective, not fusion-selective** (the LBD it drugs is
identical in the fusion and wild-type NR4A3). The **fusion-junction ASO paper**
([`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md)) is now the **co-priority second paper**:
it covers the *next* selectivity tier — sparing wild-type NR4A3 by silencing the chimeric transcript — and
is the most-likely-to-work fusion-exclusive route (complete in-silico arc; delivery the one gate). The two
pair naturally: degrader spares the paralogues, ASO spares wild-type NR4A3. Full sequencing + the
fusion-exclusivity framework (the 5-route design space, next-tier) are in `emc-treatment-strategy.md` Q1 and
[`fusion-selective-approaches-overview.md`](./fusion-selective-approaches-overview.md).

## Update (2026-06-27, trimcrae): keep the degrader STANDALONE — do not fold the other findings into it
A novelty stress-test of the portfolio (degrader vs. ASO-solo, the ASO specificity *method*, and the
fusion-exclusivity *framework*) reached a clear split:
- **The degrader is the only piece currently on a path to a results-paper publication.** Its novelty is
  *target/structure-level* — first pocket-dynamics + druggability-feasibility analysis of NR4A3 (no
  experimental structure, "undruggable" reputation), the family-wide state-matched selectivity matrix, and
  the calibration that corrects the misread "Nurr1 ~0.8 druggable" (non-orthosteric cavity). It clears the
  "what's new?" bar. **Caveat:** publishability is gated on *finishing the in-silico tests* (the unbiased
  release run that decides whether the breathing-open geometry is populated vs. bias-induced strain; the
  NR4A1/NR4A2 ensembles; warhead/ternary) — i.e. gated on completion, not on novelty.
- **The ASO-solo, the ASO method, and the framework are confirmed-but-NOT-novel** — each reframes a known
  principle (fusion-exclusivity spares wild-type; junction ASOs; standard off-target screening + one
  uncalibrated gap-mismatch heuristic; a design-space survey of mostly not-yet-working routes).

**Decision: the degrader ships standalone (target-centric), and we do NOT make it the anchor of a combined
"EMC + all our findings" paper.** Two reasons, beyond the existing "nothing in the pipeline is
EMC-specific" argument:
1. **All of the degrader's novelty is NR4A3-generic, and that is where its value/market lives** (AciCC —
   bigger than EMC; NR4A-rearranged sarcomas; ex-vivo pan-NR4A immuno). An EMC frame hides the novel result
   from the audience that values it and shrinks the apparent market to the smallest indication.
2. **Novelty-contamination:** reviewers grade a multi-contribution paper by its weakest load-bearing claim.
   Co-mingling the novel degrader result with the confirmed-but-not-novel ASO/framework material lets their
   "what's new?" liability rub off on the one results paper that clears the bar. A tight paper doing *one*
   novel thing well beats a sprawling program paper doing one novel thing and three reframings. (The ASO is
   also *EMC-fusion-specific*, so it doesn't even belong in an NR4A3-*generic* degrader paper.)

The non-novel-but-mission-relevant EMC work keeps its home in the **EMC-program paper**
([`emc-treatment-roadmap.md`](./emc-treatment-roadmap.md)) — a program/perspective piece whose contribution
is the framework + falsifiable kill-criteria, where "not novel per-route" is not a fatal objection — which
*cites* the degrader as its §4.1 route. This confirms, rather than changes, the existing two-paper split;
recorded here so the standalone-vs-merge question is not re-opened.
