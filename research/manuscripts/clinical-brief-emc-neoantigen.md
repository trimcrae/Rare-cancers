# Clinical brief: a personalised fusion-neoantigen route to treatment in EMC

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
   predicted presented on that patient's alleles (MHCflurry-2.0), with the tumour-specific
   residues flagged. *(Reproducible, open, runs in minutes.)*
4. **Validate before use** — confirm presentation (immunopeptidomics on tumour) and
   autologous **T-cell reactivity** ex vivo. Prediction is a screen, not proof.
5. **Manufacture / deploy** a personalised peptide or mRNA vaccine, or isolate/engineer a
   **TCR-T** against a validated epitope, within an appropriate trial/IRB framework.

## Worked example (from the reproducible pipeline)

For the commonly reported **EWSR1 exon 7 :: NR4A3 exon 3** junction (context
`…SQQSSSYGQQ|IVRTDSLKGR…`) and a common HLA set (A\*02:01, A\*11:01, B\*07:02, B\*08:01),
the tool returns **6 presented candidates, 2 strong**:

| epitope | HLA | affinity | pres. %ile | tumour-specific residues |
|---|---|---|---|---|
| `QQIVRTDSL` | B\*08:01 | 97 nM | 0.04 (strong) | 2 EWSR1 + 7 NR4A3 |
| `SSYGQQIVR` | A\*11:01 | 61 nM | 0.08 (strong) | 6 EWSR1 + 3 NR4A3 |

A useful nuance the tool surfaces: `SSYGQQIVR` straddles the seam more evenly (6 + 3) so it
is *more foreign* than the otherwise-strong `QQIVRTDSL` (2 + 7, mostly NR4A3-self) — a
relevant tie-breaker when picking a vaccine/TCR target. **A real patient's run uses their
own breakpoint + their own HLA**, which may give entirely different epitopes.

## Honest caveats (please read)

- **Personalised, not off-the-shelf.** Our breakpoint-resolved analysis found **no single
  pan-EMC junction epitope**; the target must be generated per patient. The presenting
  alleles, however, are among the most common worldwide, so many patients will have ≥1.
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
