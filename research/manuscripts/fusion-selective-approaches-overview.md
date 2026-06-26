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

| Route | Level | Fusion-exclusivity | Maturity / data in hand | Dominant gate or risk | Next step **without GPU** |
|---|---|---|---|---|---|
| **Junction ASO/siRNA** | RNA | High — by base-pairing | **Med–high**: 5 fusion-specific gapmers computed (GC-rich 75–81%) | **Tumour delivery** (unsolved) | CPU transcriptome-wide off-target screen; expanded tiling; junction-spanning siRNA set |
| **Junction neoantigen** | Immune | **Highest** — peptide absent from the normal proteome | **High**: 7 in-frame junctions, 26 binders, HLA coverage all computed; human platforms exist | Mostly-self → tolerance; ~16% both-arm coverage; cold tumour | Per-patient pipeline already runs; mainly *polish-to-preprint* (cohort recurrence is wet-lab) |
| **AND-gate degrader** | Protein | High — avidity coincidence | **Med**: new CPU avidity model (5.5×→~11× window); reuses the degrader's opened pocket | Arm-2 IDR/condensate ligand unproven; binding ≠ degradation selectivity | Linker/EM design space (CPU); arm-2 chemotype scoping (ternary modelling is deferred GPU) |
| **Condensate disruption** | Protein | High in principle — fusion-emergent | **Low** (earliest-stage) | Selectivity vs the cell's **other** condensates | Sequence-based LLPS-propensity analysis (CPU; needs the EWS sequence fetched) |
| **Coactivator PPI** | Protein | High *only at the fusion surface* | **Low–med** | Target coactivators are **pan-essential** (window forfeited if you bind the partner) | Provenance-tagged interactome table (CPU); AF-multimer interface model is deferred GPU |

## Recommendation

**Pursue two tracks, led by the AND-gate degrader for new in-silico work.**

**Primary (new computational lead): the AND-gate fusion-selective degrader (paper 3).** It is the best
combination of *novel + ownable + advanceable here*: (i) it is a genuinely new idea (coincidence detection
to spare wild-type NR4A3) and is the **direct protein-level answer to "attack the fusion, spare healthy
NR4A3"**; (ii) it **reuses the flagship degrader's assets** (the opened-LBD pocket as arm 1, the
selectivity handles) rather than starting a separate program, so it compounds existing work; (iii) it
already carries a real CPU result (the avidity model: a 5.5× base-case fusion-vs-wild-type window, tunable
to ~11×), and its next steps (linker/effective-molarity design space) are partly CPU-doable now, with the
ternary/condensate-partitioning modelling a well-scoped deferred GPU step. Its honest weakness — arm 2 must
engage a disordered EWS-LC / condensate, an emerging chemistry — is shared with, and informed by, paper 4.

**Parallel (most submission-ready / closest to a patient): the junction neoantigen (paper 2).** It needs
the least additional work to reach a preprint — the breakpoint, epitope, and HLA-coverage analyses are
already computed and committed — and it rides immunotherapy platforms **already in humans**. If the goal is
to *convince a collaborator fastest*, this is the one to ship. The junction ASO (paper 1) is the cleanest
mechanistic fusion-exclusivity and a natural third, gated by the unsolved delivery problem.

**Lower priority for now: condensate (paper 4) and coactivator-PPI (paper 5).** Both are real and honestly
argued, but earliest-stage: condensate pharmacology is an emerging field whose hard problem is selectivity
against *all* cellular condensates, and the PPI route's coactivators are pan-essential. Keep them as the
mechanistic backbone that *informs arm 2 of the AND-gate* rather than standalone first moves.

## The choice is yours — three lenses
- **Most novel + extends the flagship + advanceable in-silico now →** AND-gate degrader (paper 3).
- **Most ready to publish / closest to a patient →** junction neoantigen (paper 2), then junction ASO.
- **Highest-risk frontier (mechanistic upside, least mature) →** condensate (paper 4) or PPI (paper 5).

*Medical-integrity note: every quantitative claim in the five papers is cited, quoted from a committed
output, or flagged; the AND-gate model's Kd/EM inputs are illustrative assumptions (so labelled); no
molecule was synthesized and no GPU/AWS run was performed.*
