# The EMC surface-target landscape: a delivery- and immunotherapy-directed antigen map for extraskeletal myxoid chondrosarcoma

> **Role banner (2026-07-03).** **SCAFFOLD / GATED manuscript — not yet a draft to ship.** This is a
> *target-class* paper (surface antigens of EMC), spun out of the fusion-junction ASO paper's delivery
> section (§3c) on the recognition that surface-antigen targeting is a **different thesis and a different
> modality axis** from RNA-level fusion silencing. **It is explicitly gated on obtaining real EMC surface
> data** — the author-held immunophenotype / RNA-seq of the USZ-EMC and NCC-EMC1-C1 lines (preprint-stage
> outreach; ASO paper §4), or a strong public result. Until that lands, the only evidence here is an
> **EMC-*surrogate*** in-silico scan; this file records the thesis, the computation done so far, and exactly
> what the real data unlocks — it does **not** assert an EMC surface-antigen finding. Medical-integrity rule
> as everywhere: nothing is claimed as EMC-specific on surrogate data.

## Why this is a separate paper (not part of the ASO paper)

The fusion-junction ASO paper's thesis is **fusion-exclusivity**: silence the EWSR1::NR4A3 chimera while
sparing wild-type NR4A3, selectivity enforced by base-pairing across the breakpoint. Its dominant gate is
**delivery** — getting a large charged oligo into the tumour-cell cytosol/nucleus.

Surface-antigen targeting is a **different thing on both axes**:
- **Different selectivity model.** A surface antigen is *not* the fusion and sits on some normal cells too, so
  tumour-vs-normal selectivity comes from the antigen's **expression distribution**, not from fusion
  sequence. It is explicitly **not fusion-exclusive** — so it does not belong inside the ASO's
  fusion-exclusivity argument.
- **Different (easier) delivery.** Surface modalities either use antibody-mediated delivery (a solved,
  approved paradigm), act at the surface with no intracellular delivery, or deliver themselves — so they
  **shed the ASO's dominant gate** (see the modality map below).
- **Serves multiple routes, not one.** The same antigen map feeds the ASO's AOC targeting arm **and** the
  B7-H3 ADC / CAR-T, FAP-RLT, PRAME routes already tracked in [`../IDEAS.md`](../IDEAS.md) and
  [`emerging-modalities-scan-emc.md`](./emerging-modalities-scan-emc.md) /
  [`car-t-strategies-emc.md`](./car-t-strategies-emc.md). A standalone antigen-landscape paper is the natural
  home for all of them.

This mirrors the repo's own split of the **NR4A3-degrader** paper out of the EMC roadmap: a *target-centric*
result with applications beyond one indication (see
[`nr4a3-degrader-paper-positioning.md`](./nr4a3-degrader-paper-positioning.md)). Here EMC is the lead
indication of a surface-target program that generalises (broader-indications section below).

## Thesis (what the paper will argue, once the data supports it)

> EMC displays targetable cell-surface antigens that enable **delivery- and immunotherapy-directed
> modalities less gated by the intracellular-delivery problem that limits the fusion-junction ASO** — trading
> the ASO's exquisite fusion-exclusivity for a solved/easier delivery route and a coarser,
> antigen-distribution-based selectivity. We map the EMC surfaceome, rank candidate antigens, and pair each
> with the modality it best enables (AOC / ADC / T-cell engager / CAR / radioligand).

## The modality map — why a surface antigen unlocks a less-delivery-gated axis

| Modality | Needs intracellular delivery? | Gate that replaces "delivery" | Existing agents to borrow |
|---|---|---|---|
| **T-cell engager / bispecific** (antigen × CD3) | **No** — kills at the surface via recruited T cells | Cold TME (EMC's immunosuppressive myxoid stroma); antigen coverage | many approved TCEs |
| **CAR-T / CAR-NK** | **No** — living cells home and kill | Solid-tumour infiltration + cold TME + antigen escape | B7-H3 CAR-T (repo route) |
| **Radioligand therapy** (¹⁷⁷Lu/²²⁵Ac) | **No** — payload is radiation; **crossfire** kills unbound neighbours | Antigen expression; radiobiology; tumour-vs-normal window | FAP-RLT (repo route); theranostic |
| **ADC** (antibody + cytotoxic) | Some — needs internalisation, but a **solved, approved** paradigm; diffusible payload | Antigen internalisation + tumour-vs-normal window | B7-H3 ADC (ifinatamab deruxtecan) |
| **AOC** (antibody–oligo conjugate) | Yes — but antibody-targeted, not naked | The ASO's arm; same antigen | — |

**Radioligand therapy is the sharpest contrast to the ASO:** the ASO must functionally engage *every*
tumour cell's RNA (one escapee regrows the tumour), whereas an α/β emitter kills cells it never bound
(crossfire ~mm), so **heterogeneous delivery is tolerable** — it converts "hit every cell" into "hit enough
cells near every cell."

## Computation done so far (EMC-*surrogate* — not yet EMC)

**Unbiased surfaceome scan** ([`../modalities/emc_surfaceome_scan.py`](../modalities/emc_surfaceome_scan.py)
→ `emc-surfaceome-scan.json`). Whole human surfaceome (UniProt plasma-membrane + TM/GPI, 2,820 genes;
self-validated) ranked by expression across the **EMC-surrogate translocation-sarcoma DepMap class** (n=76;
EMC has no DepMap line). Result:
- **B7-H3 (CD276) is broad but NON-selective** (98% of class expressed; enrichment vs other cancer lineages
  only +0.14) — reprioritising the antigen the field defaults to.
- **More selective candidates rank above it:** **CDH11 (+3.18), FGFR1 (+1.99, highest in the one myxoid
  line), GPC2 (+1.49), PTK7 (+1.24), MCAM/CD146 (+1.09), EPHB4 (+1.0)** — several with existing ADC/CAR/TCE
  programs.

**Real-EMC-tumour cross-check — attempted, and the public path is exhausted**
([`../modalities/emc_gse4303_crosscheck.py`](../modalities/emc_gse4303_crosscheck.py) →
`emc-gse4303-crosscheck.json`). We tried to validate the shortlist against the only public real-EMC
transcriptome, GSE4303. Honest outcome: **GSE4303 is unusable for a surface-antigen expression ranking.** It
is a 7-platform, **two-colour cDNA-*clone* array** series (GPL2937/…; 3 EMC samples/platform) whose values are
**log-ratios vs a reference pool** (63% negative — *relative*, not absolute expression) and whose probes are
**clone/spot IDs without gene symbols** (0 of the shortlist genes were resolvable). The platform gate did its
job — it flagged the two-colour data rather than forcing a meaningless ranking. **Upshot:** the public-data
route to real-EMC surface expression is exhausted; the author-held **USZ/NCC line** data (immunophenotype /
RNA-seq) is the genuine unlock, and this paper's gate.

**Honest bounds (the reason this is still a scaffold):** surrogate sarcoma lines, not EMC; the myxoid subset
is a single DepMap line; "enrichment" is vs other **cancer** lineages, **not normal tissue** (the
toxicity-relevant tumour-vs-normal window — GTEx/HPA — is not yet applied); cell-line/tumour **mRNA** is a
proxy for surface **protein**. These are exactly the gaps the real EMC data closes.

## The gate — what turns this scaffold into a paper

1. **Real EMC surface data** (the decisive input): the USZ-EMC / NCC-EMC1-C1 line **immunophenotype and/or
   RNA-seq**, currently *"available on request"* (USZ) or paywalled (NCC) — the preprint-stage outreach ask
   (ASO paper §4). This replaces the surrogate ranking with an EMC-specific one.
2. **Tumour-vs-normal window** on the shortlist (GTEx/HPA normal-tissue expression) — the load-bearing
   safety filter for every surface modality, computable in-silico once the shortlist is fixed.
3. **Lead antigen × modality selection** — pair the winning antigen with the modality its biology best fits
   (internalising → ADC/AOC; non-internalising but accessible → TCE/CAR/RLT).

## Positioning vs the two priority papers

- **Degrader paper** — intracellular, target-*selective* (NR4A3 LBD), not fusion-selective.
- **ASO paper** — intracellular (RNA), **fusion-exclusive**, delivery-gated.
- **This paper** — **surface**, immuno/delivery axis, **less delivery-gated**, not fusion-exclusive.

The three are complementary shots on the same driver biology from three compartments (protein / RNA /
surface). This paper is the surface/immuno axis and the antigen-discovery engine feeding the delivery arms
of the other routes.

## Broader indications (per the IDEAS cross-cutting strategy)

Surface antigens that surface for EMC (B7-H3, GPC2, PTK7, FGFR1, MCAM, CDH11) are **pan-sarcoma / pan-cancer
targets** with active ADC/CAR/TCE/RLT programs — so EMC is the *entry* indication of a broader surface-target
opportunity, the market-widening logic that the IDEAS board argues is needed to get a rare-cancer result
actually developed.

## Next steps
- **Send the outreach ask** (ASO §4) for USZ/NCC line surface data → re-run `emc_surfaceome_scan.py` on real
  EMC expression.
- **Add the GTEx/HPA normal-tissue window** filter on the shortlist.
- **Fold in the GSE4303 cross-check** result.
- When (1)+(2) land, promote this scaffold to a real draft and register it in the priority tiering.

---
*Provenance: this scaffold consolidates the surfaceome scan (`emc_surfaceome_scan.py`), the EMC-line data
probe (`emc_line_data_probe.py`), and the GSE4303 cross-check (`emc_gse4303_crosscheck.py`) — all committed
CPU outputs on `modalities-cache` — plus the surface-modality discussion in `emerging-modalities-scan-emc.md`
and `car-t-strategies-emc.md`. No EMC-specific surface claim is made on surrogate data.*
