# EMC fusion-induced lineage-antigen program

> The atlas's junction-antigen result (claims C016/C021/C022) is honest: both common junctions are
> **modest on MHC-I**; only the EWSR1 junction carries a strong CD4 helper epitope. Per the strategy,
> that is the trigger to pursue **fusion-induced LINEAGE antigens** in parallel. This is the program
> spec. It composes with `research/manuscripts/emc-surface-target-landscape.md` (surface-target
> deep-dive) and the DepMap surrogate reads (`research/modalities/depmap-insilico-findings.md`).
>
> **Governing guard (atlas rule #4):** high tumour RNA is a candidate signal, **never** proof of
> accessible cell-surface protein or of a therapeutic window. Every candidate below is gated on
> EMC-tissue protein + normal-tissue safety before any modality is built.

## Candidate table

| Antigen | EMC evidence (atlas-cited) | Modality fit | Decisive gate before any program |
|---|---|---|---|
| **CHRNA6** | **Top EMC-up marker: AUC 1.00, rank 26/23072 in GSE24369 reprocessing (C018)**; validated diagnostic RNA-ISH marker | surface receptor → ADC / CAR | Cell-surface protein density on EMC tissue; **CNS/neural normal expression is a real safety risk** (nicotinic receptor) |
| **NMB (neuromedin B)** | **AUC 1.00, rank 11/23072 (C018)**; possible NMB–NMBR autocrine loop | secreted ligand + NMBR (GPCR) → not a classic surface-Ag; pathway/autocrine target | Is NMBR expressed/functional in EMC? autocrine dependency test (perturbational, not expression) |
| **B7-H3 / CD276** | DepMap sarcoma **surrogate**: mean 5.73 log2TPM, 99% of lines (C013) | ADC (ifinatamab deruxtecan) / CAR-T / bispecific | Confirm on **EMC tissue** (surrogate, not EMC); density for the chosen modality |
| **PRAME** | DepMap **surrogate**: 53% of lines, **high in myxoid class (7.6)** (C014) | HLA-restricted TCR / ImmTAC (brenetafusp) | CTAs are silenced in cell lines (surrogate = lower bound) → confirm in primary EMC; HLA restriction |
| **RET** (as antigen/surface) | Elevated in EMC (Davis 2017; GSE24369 AUC 0.86, C006) but **non-essential** (C020) | surface RTK — but a marker, not a dependency | Not a dependency (C020); only a surface-target candidate, not a driver |

## Prioritisation (by tractability × EMC-specificity × safety)

1. **B7-H3 (CD276)** — best modality maturity (clinical ADC/CAR exist) and near-universal surrogate
   signal; the cleanest first tissue-confirmation experiment. *Gate: EMC-tissue IHC/proteomics.*
2. **PRAME** — best antigen-directed option for a myxoid-class tumour (ImmTAC/TCR exist); *gate: primary
   EMC expression + HLA.*
3. **CHRNA6** — highest EMC-specificity (near-pathognomonic RNA) but the **hardest safety gate**
   (neural expression) and RNA-ISH performance ≠ surface protein; treat as a discovery lead, not a
   near-term program.
4. **NMB/NMBR** — mechanistically interesting (autocrine) but not a classic surface antigen; route it
   into a perturbational dependency test, not an antigen program.

## Validation ladder (hand-off to a tissue/immuno lab)

1. **EMC-tissue protein confirmation** — IHC / quantitative proteomics for B7-H3, PRAME, CHRNA6
   (surface localisation + % positive tumour cells + density).
2. **Normal-tissue safety map** — vital-tissue expression (esp. CHRNA6/CNS), antigen density vs the
   modality's threshold.
3. **Immunopeptidomics** — is the antigen (or the junction CD4 epitope) naturally presented on EMC HLA?
4. **Functional** — for PRAME: HLA-matched TCR/ImmTAC recognition + cytotoxicity on fusion-positive EMC;
   loss of recognition after HLA/antigen knockout.
5. **Modality build** — only after 1–4: ADC (B7-H3), TCR/ImmTAC (PRAME), or a vaccine pairing the EWSR1
   junction CD4 helper epitope (C022) with a confirmed class-I target.

## Go/no-go
- Advance an antigen only with **EMC-tissue protein** confirmation (not RNA, not surrogate), a
  **selectivity margin over vital normal tissue**, a **density above the modality threshold**, and —
  for antigen-directed T-cell modalities — **evidence of natural presentation or functional recognition**.
- CHRNA6 does **not** pass on RNA-ISH diagnostic performance alone (explicit atlas guard).

## Honest limitations
- B7-H3 / PRAME evidence is **DepMap surrogate** (no EMC line); cell lines silence cancer-testis antigens
  (PRAME = lower bound). CHRNA6/NMB are **RNA** signals from a reprocessed tumour set (n=6 EMC).
- No natural-presentation or surface-protein data exist for EMC for any of these — the program is
  explicitly designed to be handed to a lab with tissue and immunopeptidomics capacity.
