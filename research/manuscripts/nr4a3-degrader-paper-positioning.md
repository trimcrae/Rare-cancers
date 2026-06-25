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

## Indication stack (motivation, ordered for impact — all sourced in `nr4a3-degrader-broader-indications.md`)
1. **Immuno-oncology (headline impact, large market):** NR4A1/2/3 drive CD8⁺ T-cell exhaustion;
   NR4A-deficient CAR-T cells show superior solid-tumour control (Chen et al., *Nature* 2019). A NR4A
   degrader as an immunotherapy/CAR-T adjuvant. *(Motivation, not demonstrated here; likely wants a
   broad/pan-NR4A profile — see selectivity knob.)*
2. **Precision oncology — NR4A3-fusion sarcomas:** EMC (EWSR1/TAF15::NR4A3) and variants — a fusion
   oncoprotein driver with **no targeted therapy**. The cleanest concrete application of a *selective*
   NR4A3 degrader; EMC is the proof-of-concept/lead *example* within this.
3. **NR4A1/NR4A2-driven solid tumours** (pancreatic, lung, breast, colorectal) if cross-reactive.

**The spine is selectivity:** NR4A3-selective for the fusion sarcomas; deliberately broad NR4A for
ex-vivo immuno-oncology — **two indications from one chemical program**, bounded by the **AML/myeloid
tumour-suppressor contraindication** (NR4A1/NR4A3 loss is leukemogenic; Mullican 2007). Stating that
boundary is part of the credibility, and it is *why* selectivity engineering is central.

## What this changed downstream (EXECUTED 2026-06-25)
- **[`nr4a3-degrader-paper.md`](./nr4a3-degrader-paper.md)** created as the lead, target-centric result
  paper (cryptic-pocket druggability, selectivity, degrader design; EMC the lead indication of several).
- **`emc-treatment-roadmap.md`** re-bannered as the EMC-program paper; §4.1/§7 now cite the split-out
  degrader paper for the in-silico degrader results.
- **`README.md`** updated from "exactly ONE manuscript" to the two-paper structure.
- **`CLAUDE.md`** PRIMARY FOCUS updated: lead vehicle = the NR4A3-degrader paper, *serving* (not
  replacing) the EMC goal — per the user's framing that the steering-doc goal still applies and the
  split paper is how we accomplish it. (AGENTS.md not edited; CLAUDE.md is the agent-facing TL;DR.)
