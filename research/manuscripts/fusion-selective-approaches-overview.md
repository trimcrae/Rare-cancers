# Fusion-exclusive approaches to EWSR1::NR4A3 EMC — overview, comparison, and recommendation

> **Role:** index + decision memo for the five *fusion-unique* manuscripts drafted 2026-06-26. Each
> pursues **true fusion-exclusivity** — acting on something present **only** in the EWSR1::NR4A3 (or
> TAF15::NR4A3) chimera and therefore **sparing wild-type NR4A3** — the selectivity layer the repo's lead
> NR4A3-LBD degrader cannot reach (it binds the LBD that the fusion and wild-type NR4A3 *share*). All work
> here is computation-only / publish-to-convince; **no GPU/AWS run** was performed (one new CPU model was).

## Why "fusion-exclusive" is the prize
A drug can be selective at three increasingly tight levels: tumour-vs-normal (weak) → **NR4A3-selective**
(the degrader: spares NR4A1/2, but the NR4A3 LBD is *identical* in fusion and wild-type, so it still
removes wild-type NR4A3) → **fusion-exclusive** (acts only on the chimera). The third level is the most
targeted and lowest-toxicity option, and — uniquely — it neutralises the **tumour-suppressor liability** of
depleting wild-type NR4A3 systemically (NR4A3 is tumour-suppressive in HCC/breast/lymphoma; combined
NR4A1/NR4A3 loss is leukaemogenic — Mullican 2007; Safe & Karki 2021). You can only be fusion-exclusive by
targeting something the fusion has that **neither parent** does: the mRNA junction, the junction
neopeptide, or the fusion-emergent protein behaviour (the appended EWS low-complexity domain and its
condensate / coactivator activity).

> **LIVE DEFERRED DECISION (2026-07-13):** the active ternary-first **NR4A3-degrader** program (Level 1,
> spares NR4A1/2 but co-degrades WT NR4A3) carries an explicit, deferred choice about whether to escalate to
> **Level 2 (fusion-exclusive)** — decided at its post-NR-V04-validation / pre-design gate. The full input
> checklist (esp. *quantifying* the WT-NR4A3-co-degradation liability, and the arm-2 IDR-ligand gate that
> makes a Level-2 *degrader* buildable-or-not) lives in
> [`nr4a3-degrader-strategy-ternary-first.md` → "DEFERRED DECISION — selectivity TARGET"](./nr4a3-degrader-strategy-ternary-first.md).
> That decision may route Level 2 to the **ASO** (paper 1) rather than the AND-gate degrader (paper 3).

## The five manuscripts
1. **RNA — fusion-junction ASO / siRNA** → [`fusion-junction-aso-paper.md`](./fusion-junction-aso-paper.md)
2. **Immune — fusion-junction neoantigen** (vaccine / TCR-T / soluble-TCR) → [`fusion-junction-neoantigen-paper.md`](./fusion-junction-neoantigen-paper.md)
3. **Protein — AND-gate (coincidence-detection) bivalent degrader** → [`fusion-selective-andgate-degrader-paper.md`](./fusion-selective-andgate-degrader-paper.md)
4. **Protein — condensate / phase-separation disruption** → [`fusion-condensate-disruption-paper.md`](./fusion-condensate-disruption-paper.md)
5. **Protein — fusion↔coactivator PPI blockade** → [`fusion-coactivator-ppi-paper.md`](./fusion-coactivator-ppi-paper.md)

New CPU computation produced for this batch: [`../modalities/andgate_selectivity_model.py`](../modalities/andgate_selectivity_model.py)
→ [`../modalities/fusion-andgate-selectivity-model.json`](../modalities/fusion-andgate-selectivity-model.json)
(the avidity selectivity model behind paper 3).

## Comparison

The right primary axis is **likelihood the biology actually works** — distinct from novelty or readiness.
An earlier version of this memo ranked by novelty/ownability and put the AND-gate first; corrected here
(2026-06-26) to lead with probability-of-success.

| Route | Level | Fusion-exclusivity | **Likely to work (biology)** | Maturity / data | Dominant gate | Next step **w/o GPU** |
|---|---|---|---|---|---|---|
| **Junction ASO/siRNA** | RNA | High — by base-pairing | **HIGH — proven knockdown modality + strong fusion-addiction prior; the risk is *delivery*, not whether the biology works** | Med–high: 5 gapmers computed | **Tumour delivery** (engineering, not biology) | Transcriptome-wide off-target screen (needs internet → GitHub); siRNA set |
| **Junction neoantigen** | Immune | **Highest** — absent from normal proteome | **MODERATE — platform proven in humans, but self-adjacent junction (tolerance) + cold tumour + ~16% both-arm coverage cast real *efficacy* doubt** | High: breakpoints + coverage computed | Immunogenicity (tolerance, cold tumour) | Polish to preprint; per-patient pipeline already runs |
| **AND-gate degrader** | Protein | High — avidity coincidence | **LOW near-term — requires *unsolved* chemistry (a ligand for the disordered EWS-LC/condensate, arm 2); modest 5–11× window; binding ≠ degradation** | Med: new CPU avidity model | Arm-2 IDR ligand does not exist yet | Linker/EM design space; arm-2 scoping |
| **Condensate disruption** | Protein | High in principle | **LOW — emerging field; selectivity vs the cell's *other* condensates unsolved** | Low (earliest-stage) | Which-condensate selectivity | LLPS-propensity seq analysis (needs EWS seq → GitHub) |
| **Coactivator PPI** | Protein | High *only at the fusion surface* | **LOW — target coactivators are pan-essential; PPIs hard to drug** | Low–med | Pan-essential partners | Provenance-tagged interactome table |

## Recommendation (re-ranked by likelihood of working)

**Lead with the junction ASO/siRNA (paper 1) — it is the route most likely to work on the biology.**
Transcript knockdown of an addicted fusion is the most *de-risked mechanism* of the five: RNase-H gapmers
and siRNA are an established, approved drug class, and EMC's fusion-addiction prior is strong (the Ewing
FLI1 analogy: −0.93 gene effect, 74% dependent). Crucially, its one big uncertainty — **solid-tumour
delivery** — is an *engineering* problem with active solutions (antibody–oligonucleotide conjugates,
tumour-receptor-targeted nanoparticles), not a question of whether knocking the fusion down impairs the
cell. That is a categorically more tractable risk than "does an unproven modality work at all." It is also
genuinely fusion-exclusive (spares wild-type NR4A3 by sequence) — the property you asked for.

**Second: the junction neoantigen (paper 2)** — most platform-ready (clinical neoantigen-vaccine platforms
already in humans) and the cleanest selectivity, but its *efficacy* is more doubtful than the ASO's
(mostly-self junction → central tolerance; cold tumour; partial HLA coverage). Ready to publish ≠ likely to
cure.

**De-prioritised for a "likely to work" goal: the AND-gate degrader (paper 3).** It is the most novel and
the best selectivity *concept*, and the right long-horizon protein-level answer — but it depends on an
**unsolved** chemistry (a small molecule that selectively engages the disordered EWS-LC/condensate as arm
2), so its near-term probability of yielding a working drug is the *lowest* of the practical routes. Keep it
as the high-ceiling, lower-odds bet, informed by the condensate work (paper 4). **Condensate (4) and PPI
(5)** remain frontier/backbone, not first moves.

## Computed CPU evidence (2026-06-26) — and how it updates the ranking
Real CPU results now back the comparison (no GPU/AWS):
- **AND-gate avidity + linker-physics models** — fusion-vs-WT binding window 5.5×→~11×, *robust* across the
  synthesizable linker range (EM grounded in ideal-chain physics). The selectivity concept holds; the
  unsolved arm-2 chemistry remains the gate.
- **LLPS sequence-features (condensate route) — clean positive.** EWS/TAF15 LC domains show the prion/LLPS
  signature (SYGQ 0.56/0.68, aromatic ~0.14, low charge, low entropy ~3.2) that folded controls and — the
  key control — NR4A3's own disordered AF1 region do **not**. First-party support that the condensate
  capacity is genuinely fusion-emergent. (Still a sequence proxy, not a measured phase diagram.)
- **ASO off-target screen + siRNA — an important caveat to the #1 pick.** At the *canonical modelled
  breakpoint*, the junction is GC-rich **and** low-complexity, so all 5 gapmers have many gap-spanning
  near-complementary hits to **real genes** (OTOG, SPTBN2, …), and the GC-tolerant siRNA route does **not**
  escape it (min GC 73.7%). The problem is *this junction sequence*, not the modality — and real patients
  carry ≥7 distinct breakpoints. **This makes ASO/siRNA feasibility breakpoint-conditional**: the mechanism
  is still the most de-risked, but a favorable breakpoint must be selected. The per-breakpoint feasibility
  scan (running) tests whether favorable breakpoints exist.

**Update (per-breakpoint scan + degradation model, just computed):**
- **ASO specificity is achievable at a favorable breakpoint — demonstrated in-silico.** The breakpoint scan
  (390 modelled) finds **243 (62%) favorable** by GC/complexity triage; the *canonical* is an unlucky
  GC-rich one. The full BLAST screen on a favorable breakpoint (200/8), **resolved to gap-mismatch position**
  (RNase-H can't cleave a near-match whose mismatch falls in the DNA gap), shows **2 of 5 gapmers are
  predicted genuinely clean — zero true cleavage risks** (the residual 14/16 hits are gap-disrupted). So the
  workflow breakpoint-triage → per-oligo BLAST → gap-mismatch resolution **yields clean candidates**;
  specificity is achievable, not merely improvable. Caveats: predicted (not wet-lab-confirmed), modelled
  breakpoint, and **delivery remains the separate unsolved gate**. ASO stays #1 on mechanism *and* now has
  demonstrated in-silico specificity feasibility.
- **AND-gate degradation window is *narrower* than its binding window.** A cooperative ternary model shows
  the 5.5–11× binding window erodes to ~1× at saturating dose (hook effect) and shrinks with cooperativity;
  it survives (~6.8×) only at sub-saturating dose. Another reason the AND-gate stays a lower-odds bet.

**Net:** the ranking holds and is sharpened — the ASO route stays #1 on mechanism, with **demonstrated
in-silico specificity feasibility** (clean gapmers found at a favorable breakpoint), leaving **delivery as
its single remaining unsolved gate**; the condensate premise is data-supported (still early on
druggability); and the AND-gate's selectivity is real but modest and dose-fragile in degradation.

## Three lenses (pick by what you weight)
- **Most likely to work (biology) →** junction ASO/siRNA, then junction neoantigen.
- **Most ready to publish *now* →** junction neoantigen.
- **Most novel / best selectivity, highest ceiling, lowest near-term odds →** AND-gate degrader.

## Publishing decision (2026-06-26, trimcrae)
**The two papers to publish FIRST are the NR4A3-degrader paper and the fusion-junction ASO paper** (the
standout of this set — most-likely-to-work, with a complete in-silico arc ending in predicted-clean gapmers;
delivery is its one gate). Of the five fusion-unique routes here, **only the ASO is promoted to a standalone
priority paper.** The other four (neoantigen, AND-gate degrader, condensate, PPI) are **not** separate papers
yet — they become the **comparative design space inside the fusion-exclusivity *framework* paper** (this
overview, grown into a perspective/methods piece: *"target-selective ≠ fusion-selective — the computable
design space for sparing the wild-type protein"*), which is **next-tier**, after the degrader + ASO. So the
sequence is: **degrader + ASO (first) → fusion-exclusivity framework + EMC-program roadmap (next) →**
individual route papers only if/when their gating step matures (AND-gate arm-2 chemistry; condensate
druggability; PPI interactome). Recorded in `emc-treatment-strategy.md` Q1, `CLAUDE.md`, and
`research/manuscripts/README.md`.

*Medical-integrity note: every quantitative claim in the five papers is cited, quoted from a committed
output, or flagged; the AND-gate model's Kd/EM inputs are illustrative assumptions (so labelled); no
molecule was synthesized and no GPU/AWS run was performed.*
