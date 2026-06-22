# Alternative ways to make CAR-T work for EMC (Phase 3)

**Scope.** Autonomous Phase-3 brainstorm (2026-06-22), explicitly the hard case: can CAR-T be made
to work for EWSR1::NR4A3 EMC? Honest about why it's hard, then concrete alternatives. Tags
**[EMC-specific]/[pan-sarcoma]/[hypothesis]**. Feeds `research/IDEAS.md`.

## The two structural problems (state them plainly)

1. **The driver is nuclear; CARs see only the surface.** EWSR1::NR4A3 is a transcription factor —
   not on the cell surface — so (unlike TCR-T/ImmTAC, which read intracellular antigens *via*
   HLA) a CAR can't target the actual oncoprotein. CAR-T for EMC must target a **surrogate surface
   antigen**, accepting it won't be fusion-specific.
2. **EMC is "cold" and myxoid-stroma-rich.** Low mutational burden + an abundant myxoid/CAF matrix
   = poor T-cell infiltration and an immunosuppressive niche. Even a perfect target faces a
   physical/biochemical wall. Solving the target without solving the microenvironment fails.

So "make CAR-T work" = **(A) pick a surface target** + **(B) crack the cold myxoid stroma** +
**(C) manage on-target/off-tumor toxicity & rarity.**

## A. Surface-target options (ranked)

1. **B7-H3 / CD276 — the lead.** Expressed in 97% of soft-tissue sarcomas (69% high), restricted on
   normal tissue; B7-H3 CAR-T is already in trials. The cheapest unlock is **EMC-specific B7-H3
   IHC** (also opens the ADC/bispecific, see `emerging-modalities-scan-emc.md` §3). [pan-sarcoma]
2. **CD56 / NCAM — the EMC-specific angle.** EMC has a **neuroendocrine-like phenotype**
   (synaptophysin+ ~42%, S100 ~52%, INSM1 variable), and CD56/NCAM is the *surface* NE marker. CD56
   is a validated therapeutic surface target (lorvotuzumab mertansine ADC; CD56 CARs explored in
   SCLC/myeloma). **EMC-specific CD56 IHC is the missing datum** — but the NE phenotype makes a
   CD56⁺ subset plausible. [hypothesis, EMC-grounded]
3. **FAP — target the stroma, not the tumour.** A FAP-CAR attacks the myxoid CAF stroma directly —
   doubling as microenvironment disruption (ties to FAPI-RLT, scan §2). [pan-sarcoma]
4. **GD2 / HER2 / NKG2D-ligands** — generic sarcoma CAR targets; fallbacks if 1–3 fail. [pan-sarcoma]

## B. Cracking the cold myxoid stroma (the "alternative ways")

- **CAR-T + anti-angiogenic TKI.** Leverage EMC's *unusual TKI sensitivity* (its one real clinical
  signal) to normalise vasculature and boost T-cell infiltration — the same cold→hot logic behind
  the Phase-1 TKI+ICI lead, applied to cell therapy. Strong rationale to **combine, not solo**.
- **FAP-CAR (or FAPI-RLT) stromal debulking first**, then an anti-tumour CAR — sequential
  stroma-then-tumour.
- **Armored CARs** secreting IL-12 / IL-15 / IL-18 to self-sustain and resist suppression in a cold
  niche.
- **Local / intratumoral delivery** for accessible soft-tissue lesions (EMC is often a resectable
  extremity mass) — lowers the infiltration barrier and systemic toxicity.

## C. Toxicity & rarity

- **Logic-gated / dual CARs.** B7-H3 and CD56 are on some normal tissues, so use **SynNotch
  priming** (prime on antigen 1, kill on antigen 2) or **tandem/AND-gate** CARs (e.g. B7-H3 ∧ CD56)
  to gain tumour selectivity and cover antigen heterogeneity/escape. Affinity-tuned or **transient
  mRNA CARs** add a safety dial.
- **Allogeneic / off-the-shelf CAR-T.** For an ultra-rare cancer, a bespoke autologous product is
  economically and logistically untenable (same rare-disease argument as the vaccine economics) — an
  **allogeneic platform that amortises across diseases** is the only realistic vehicle for EMC.

## D. The forward-looking, computational unlock (most novel)

Rather than *borrow* a generic surface target, **discover an EMC-enriched one from the fusion's own
program**: EWSR1::NR4A3 drives a specific transcriptional output (it even flips an *axon-guidance*
program that differs between EWSR1- and TAF15-EMC, and transactivates PPARG). A **"surfaceome"
screen** — intersect EMC tumour-vs-normal expression / the published fusion-target genes with
membrane-protein annotations (e.g. the in-silico surfaceome / SURFY) — could nominate a
**tumour-restricted surface CAR target** unique to EMC, instead of a pan-sarcoma compromise.
★ This is the concrete computational next step; its limitation is EMC expression-data scarcity
(no DepMap line; few GEO series), so it would lean on published EMC/fusion-target gene lists +
the NE-marker set rather than a fresh screen.

## Recommendation

- **Near-term, borrowed:** **B7-H3 CAR-T combined with a TKI** (target + TME fix together), gated by
  one cheap EMC B7-H3 IHC. CD56 is the EMC-specific second target worth confirming in parallel.
- **EMC-specific discovery:** the surfaceome screen (D) + armored/logic-gated, allogeneic
  constructs. CAR-T for EMC is a *real but harder* path than the antibody/RLT routes that can use the
  same B7-H3/FAP targets sooner — so among surface-target modalities, **ADC (ifinatamab deruxtecan)
  or FAPI-RLT likely beat CAR-T to an EMC patient**, with CAR-T the higher-ceiling follow-on.

## References (verified this session)
- B7-H3 widely expressed in soft-tissue sarcomas. https://pmc.ncbi.nlm.nih.gov/articles/PMC11523878/
- INSM1 / neuroendocrine immunophenotype of EMC (synaptophysin, S100, INSM1).
  https://www.nature.com/articles/modpathol2017189 ; https://pubmed.ncbi.nlm.nih.gov/36563884/
- B7-H3 CAR-T / immunotherapy target review. https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2021.701006/full
- (FAP / FAPI and EMC PPARG references as in `emerging-modalities-scan-emc.md`.)
