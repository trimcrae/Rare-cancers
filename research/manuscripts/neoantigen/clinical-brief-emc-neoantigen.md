---
id: DOC-CLINICAL-BRIEF-EMC-NEOANTIGEN
title: "Clinical brief: a personalised fusion-neoantigen route to treatment in EMC"
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: See the document body; purpose was not stated separately when frontmatter was backfilled.
scope: Scope not separately declared. Inferred kind `manuscript` from its location under research/manuscripts/.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-05
last_verified: unverified
_backfilled: true
---
# Clinical brief: a personalised fusion-neoantigen route to treatment in EMC

> **EARLIER TREATMENT-TRACK DERIVATIVE — one-page brief drawn from** [`novel-modalities.md`](../modality-census/novel-modalities.md).
> Subsumed by the active manuscript [`emc-treatment-roadmap.md`](../program/emc-treatment-roadmap.md); not the active push.
> Folder map: [`README.md`](../README.md).

**For:** sarcoma medical oncologists / immuno-oncologists and translational teams.
**Ask:** for a patient with advanced extraskeletal myxoid chondrosarcoma (EMC) and no
standard option, consider a personalised fusion-directed neoantigen approach — and tell us
whether the workflow below is feasible at your centre. **This is a research hypothesis and
a collaboration request, not medical advice, and not a validated therapy.**

---

## Why EMC is unusually suited to a neoantigen approach

- EMC is driven in ~90% of cases by a single in-frame fusion — **EWSR1::NR4A3** (or, less
  often, TAF15::NR4A3) — on an otherwise **"quiet" genome** with few recurrent secondary
  mutations [companion meta-analysis & repurposing papers; refs therein].
- That fusion is the one near-clonal driver, but it is a **poor small-molecule target**:
  our structure analysis (AlphaFold + fpocket) finds the NR4A3 ligand-binding domain is
  folded yet has **no druggable pocket** (best cavity druggability 0.495, sub-threshold),
  and the EWSR1 transactivation domain is intrinsically disordered. Conventional inhibitors
  are the wrong tool — which is *why* we turn to the immune system.
- The **fusion junction is a tumour-specific sequence** present in no normal protein. If a
  junction-spanning peptide is presented on the patient's HLA, it is a rational, clonal
  neoantigen for a personalised vaccine or TCR-T — a route that needs no druggable pocket.

## Why now: the platform already exists in humans

Personalised neoantigen therapeutics are in clinical trials and showing activity:
individualised mRNA vaccines + checkpoint blockade (mRNA-4157/V940, KEYNOTE-942 in
melanoma [Lancet 2024, doi:10.1016/S0140-6736(23)02268-7]) and autogene cevumeran in
pancreatic cancer [Nature 2023, doi:10.1038/s41586-023-06063-y]. **For EMC, nothing
chemically new is required — only the EMC-specific epitopes**, which the tool below
generates from the patient's own tumour.

## The workflow (what a centre would actually do)

1. **Sequence the tumour** (RNA-seq / targeted fusion panel) → the exact EWSR1::NR4A3
   breakpoint and the chimeric junction sequence. (Often already done at diagnosis.)
2. **HLA class-I type the patient** (standard).
3. **Generate candidate epitopes** — run `research/modalities/patient_neoepitopes.py` with
   the patient's junction + HLA. It returns a ranked shortlist of junction peptides
   predicted presented on that patient's alleles (MHCflurry-2.0, CD8/class-I), with the
   tumour-specific residues flagged. It covers **both** fusion partners — `--partner EWSR1`
   and `--partner TAF15` (the ~16% TAF15::NR4A3 variant). A companion tool,
   `patient_cd4_epitopes.py`, adds **CD4/class-II "helper" epitopes** (MHCnuggets) — class-II
   help is important for durable vaccine responses. *(Reproducible, open, runs in minutes.)*
4. **Validate before use** — confirm presentation (immunopeptidomics on tumour) and
   autologous **T-cell reactivity** ex vivo. Prediction is a screen, not proof.
5. **Manufacture / deploy** a personalised peptide or mRNA vaccine, or isolate/engineer a
   **TCR-T** against a validated epitope, within an appropriate trial/IRB framework.

## Worked example (from the reproducible pipeline)

> ⛔⛔ **THE JUNCTION SEQUENCE THIS EXAMPLE USES IS WRONG, AND EVERY PEPTIDE BELOW IS
> WITHDRAWN (2026-08-07).** The seam `…SQQSSSYGQQ|IVRTDSLKGR…` resumes NR4A3 at residue 361,
> which no corrected breakpoint produces. `fusion_breakpoints.py` was rebuilt on the
> **transcript** model: a fusion transcript retains the acceptor exon whole, so NR4A3 exon 3
> contributes 2 nt of 5′UTR that compose with EWSR1's 1 leftover nt into a codon belonging to
> **neither parent**, and NR4A3 then resumes at **Met1**. The corrected seam is
> `…SQQSSSYGQQ-N-MPCVQAQYSP…`, and at e7::e3 the strong candidates are **`NMPCVQAQY`**
> (B\*15:01, 73 nM, %ile 0.37) and **`QQNMPCVQAQY`** (B\*15:01, 109 nM, %ile 0.50) — both on
> the *same* allele. ⚠ *Superseded, retained: `QQIVRTDSL`/B\*08:01 (97 nM, 0.04),
> `SSYGQQIVR`/A\*11:01 (61 nM, 0.08), the "6 + 3 straddles more evenly" tie-breaker, and the
> TAF15 pair `SVVRTDSLK`/A\*11:01 (37 nM) and `QSVVRTDSL`/B\*08:01 (124 nM).* The **TAF15**
> panel has NOT been regenerated — `patient_neoepitopes.py` still builds its chimera through
> the CDS/protein instrument and carries the same defect — so its peptides stay withdrawn
> rather than being replaced. Corrected panel:
> [`fusion-breakpoint-neoantigens.json`](../../modalities/fusion-breakpoint-neoantigens.json);
> narrative: [`fusion-junction-neoantigen-paper.md`](./fusion-junction-neoantigen-paper.md) §2.
> The *structural* claim this example exists to make — that a TAF15-fusion patient is not
> served by an EWSR1 construct — is about exon identity, not peptides, and is untouched.

⚠ *The example below is retained verbatim as the superseded record; do not quote it.*

For the commonly reported **EWSR1 exon 7 :: NR4A3 exon 3** junction (context
`…SQQSSSYGQQ|IVRTDSLKGR…`) and a common HLA set (A\*02:01, A\*11:01, B\*07:02, B\*08:01),
the tool returns **6 presented candidates, 2 strong**:

| epitope | HLA | affinity | pres. %ile | tumour-specific residues |
|---|---|---|---|---|
| `QQIVRTDSL` | B\*08:01 | 97 nM | 0.04 (strong) | 2 EWSR1 + 7 NR4A3 |
| `SSYGQQIVR` | A\*11:01 | 61 nM | 0.08 (strong) | 6 EWSR1 + 3 NR4A3 |

A useful nuance the tool surfaces: `SSYGQQIVR` straddles the seam more evenly (6 + 3) so it
is *more foreign* than the otherwise-strong `QQIVRTDSL` (2 + 7, mostly NR4A3-self) — a
relevant tie-breaker when picking a vaccine/TCR target.

The **TAF15::NR4A3 variant** (~16%) yields its *own* strong candidates — for TAF15 exon 4
:: NR4A3 e3 (`…GYSSYGQSQS|VVRTDSLKGR…`): 6 presented / 3 strong, e.g. `SVVRTDSLK`/A\*11:01
(37 nM) and `QSVVRTDSL`/B\*08:01 (124 nM) — different from the EWSR1 epitopes, reinforcing
that targets are patient-specific.

**CD4 help is available too.** The class-II companion (EWSR1 e7::e3 vs DRB1\*15:01/03:01/
07:01) predicts 9 junction-spanning helper epitopes, 4 strong — e.g. `SQYSQQSSSYGQQIV`/
DRB1\*07:01 (14.5 nM) and `QIVRTDSLKGRRGRL`/DRB1\*03:01 (52 nM) — so a vaccine could pair
CD8 targets with the CD4 help that drives durable responses. **A real patient's run uses
their own breakpoint, class-I and class-II HLA**, which may give entirely different epitopes.

## Honest caveats (please read)

- **Personalised, not off-the-shelf.** Our breakpoint-resolved analysis found **no single
  pan-EMC junction epitope**; the target must be generated per patient. ⛔ *This conclusion
  survives the 2026-08-07 seam correction and is strengthened by it — in the regenerated
  panel every strong binder is breakpoint-specific and three of five junctions have none at
  all.* ⚠ *Superseded, retained: "The presenting alleles, however, are among the most common
  worldwide, so many patients will have ≥1." The corrected allele set is A\*01:01 / B\*07:02 /
  B\*15:01 and reaches **27%** of patients pooled (was 58%); the public e7::e3 junction is
  presented on **B\*15:01 alone** and reaches **8.5%** (was 30%). That sentence is no longer
  supportable as written.*
- **Junction peptides are largely self-sequence** (often one or two foreign residues at the
  seam); central tolerance may blunt responses. This must be tested, not assumed.
- **Predicted MHC binding ≠ immunogenicity.** Steps 4 is non-negotiable.
- This is **not a clinical recommendation**; it is a reproducible hypothesis and a request
  for expert feasibility input and collaboration.

## What we provide / what we need

- **Provided (open, reproducible):** the epitope-shortlisting tool and the full
  computational analysis (`research/modalities/`), with a documented self-correcting
  verification trail.
- **Needed:** a sarcoma immuno-oncology team to assess feasibility, a route to validation
  (immunopeptidomics + T-cell assays), and — ideally — an existing personalised-vaccine or
  TCR-T platform/trial that an EMC patient could access.

*Contact: see repository. No patient data here; nothing in this brief has been tested in a
person.*
