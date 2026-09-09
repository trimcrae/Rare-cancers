---
id: DOC-EPITOPE-BENCHMARK-FINDING
title: "EPITOPE-BENCHMARK — how many experimentally validated cancer gene-fusion junction epitopes exist, and can they calibrate a class I presentation threshold?"
level: L4
kind: investigation-finding
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# EPITOPE-BENCHMARK — the published validated set is **fifteen**, and the calibration step is not achievable at the precision it demands

Follow-through lane serving two completed lanes that blocked on the same unmeasured number.
Writes confined to this directory. Nothing committed, pushed, or added to the graph. No preflight.

⛔ **Prediction is not validation.** ⛔ **Presentation is not efficacy.** No clinical claim is made.

## 1 · The question, and why one worker answers both lanes

**PUB-NEOANTIGEN** established that the repository's 988 committed "fusion" epitope records are a
**keyword artifact**: across 44 source antigens, **zero** are cancer gene-fusion junction epitopes;
931 are viral or housekeeping proteins merely *named* "fusion". It concluded that a re-fetch alone
would not fix an inclusion rule that admits the poxvirus entry-fusion complex.

**PUB-VACCINE-PATH** established that the threshold-calibration arm's `n = 0` is a **collector
failure** (90/90 identical client-side PostgREST `400`s, `offset` without `order`), and computed what
a defensible calibration would need: a 95% CI width ≤ 0.20 on sensitivity requires **93** epitopes at
sensitivity 0.5 and **60** at 0.8 — so the preregistered floor of 30 is ~3× short in the informative
regime.

Both lanes then stopped at the same wall: **`query-api.iedb.org` is proxy-refused here**, so neither
could measure how large the validated set actually is. The single question they share is therefore
not "is the collector broken" (answered: yes) and not "is the cache polluted" (answered: yes), but:

> **How many experimentally validated cancer gene-fusion *junction* epitopes does the published
> literature actually report — and is that number large enough to calibrate a class I presentation
> threshold at the sizes PUB-VACCINE-PATH computed?**

That question is answerable **without IEDB**, from the primary literature, over a route verified
working this session: the **PubMed/PMC MCP server**.

## 2 · Paper-level merit

The `emc-vaccine-development-path.md` §6.1 ordering puts threshold calibration **first**, on the
grounds that it is the one step needing neither an EMC specimen nor a proteomics facility. Whether
that step is *achievable at all* is therefore load-bearing for the whole route ordering, and it is
decidable from public literature. §B1's assertion that the validated set is "individual sequences
across a few fusions" is a claim about the size of a measured set that has never been checked against
the measured set. Patient relevance is honest and indirect: a public, off-the-shelf junction-peptide
product rests on junction peptides being real ligands, and an antigen-directed route in a rare cancer
should not be graded on an undefended convention — nor should the convention be defended with a
benchmark that cannot support it.

## 3 · The exact gap this closes, and what it is not

* **Not an IEDB fetch, and not a re-opened denied source.** `query-api.iedb.org` and
  `eutils.ncbi.nlm.nih.gov` were re-probed only to preserve the refusal
  (`CONNECT tunnel failed, response 403`, curl exit **56**, `checks/04-`). Everything substantive
  came through the permitted PubMed MCP route. No refusal was worked around.
* **Not B2.** No new mass spectrometry on EMC tissue; no wet lab.
* **Not a re-run of PUB-VACCINE-PATH's arithmetic on faith** — §5 recomputes it independently.
* **Not the 988-record audit repeated.** PUB-NEOANTIGEN read what the cache *contains*; this lane
  measures what the *literature* contains, which is the number the cache was supposed to approximate.

## 4 · The step taken, and the artifact

A literature census over the PubMed/PMC MCP route: **26 searches** (`checks/01-`), metadata for
**49 PMIDs** and full text for **3 PMC articles** (`checks/02-`), curated into a per-record JSON and
tabulated by script (`checks/03-`, `checks/05-`).

* **`epitope-records.json`** — 40 records, one per reported peptide or peptide group, each carrying
  fusion, sequence, length, HLA restriction, **spans-the-junction** verdict with its reasoning,
  evidence grade, assay, source material, PMID and DOI.
* **`tabulate_epitopes.py` → `validated-epitope-counts.json`** — derives every count below from that
  JSON by an explicit rule, so a reader can re-stratify.
* **`VALIDATED-EPITOPE-TABLE.md`** — the auditable table, rendered from the JSON by `render_table.py`.

### The count

Applying the inclusion rule a class I threshold benchmark actually requires — **natural (not
anchor-modified) sequence · spans the fusion junction · 8–11 residues · a named class I allotype ·
at least one immunological measurement (MS elution, T-cell reactivity, or multimer)**:

> ## **n = 15**, across **nine** distinct fusion oncoproteins.

`SSKALQRPV` (BCR::ABL1 b3a2, A\*02:01) · `RIAECILGM`, `MPIGRIAECIL`, `MPIGRIAEC`, `MPIGRIADA`
(ETV6::RUNX1, A\*02:01 / B\*07:02) · `REEMEVHEL` (CBFB::MYH11, B\*40:01) · `QFIDSSWYL` (MYB::NFIB,
A\*02:01) · `MMYSPICLTQT`, `SLASPLQPT` (MYBL1::NFIB / NFIB::MYB, A\*02:01) · `DKESEEEVS` (DEK::AFF2,
C\*04:01 / C\*12:03) · `EIFDRYGEEV`, `IFDRYGEEV`, `RYGEEVKEF` (DNAJB1::PRKACA, A\*68:02 / C\*04:01 /
A\*24:02) · `GYDQIMPKK`, `PYGYDQIMPK` (SS18::SSX, A\*24:02).

Counted **separately and never added in**: **3** prediction-only records, **7** binding-only records,
**6** negative-control records that do **not** span the junction, **6** measured junction epitopes
whose sequences this route could not recover, and **2** class II / out-of-window records.

**Of the 15, only 6 carry MS-elution evidence** — `RIAECILGM`, `MPIGRIAECIL`, `MPIGRIAEC`,
`MPIGRIADA`, `EIFDRYGEEV`, `IFDRYGEEV` — and **every one of those six was eluted from an engineered
cell line** (JY transduced with an ETV6-RUNX1 minigene; Dox-inducible DNAJB1-PRKACA in HCC lines).
**Zero junction epitopes in this table were identified in the immunopeptidome of a primary patient
tumour.** That is the single most consequential row of the census, because a *presentation*-percentile
threshold is a predictor of exactly the quantity that has never been measured on a real tumour for
this antigen class.

The strongest single row is `REEMEVHEL` (CBFB::MYH11, HLA-B\*40:01): high-avidity CD8 clones killed
CBFB-MYH11⁺ B\*40:01⁺ AML lines **and primary human AML**, controlled AML in a patient-derived
xenograft, and the TCRs transferred activity — the authors conclude the neoantigen is naturally
presented on AML blasts (PMID 32831296, [DOI](https://doi.org/10.1172/JCI137723)).

## 5 · Direct answer to both lanes' blocked question

### (a) Is the validated set large enough to calibrate the class I threshold? **No — by ~6×.**

`tabulate_epitopes.py` recomputes PUB-VACCINE-PATH's Wilson requirement independently and
**reproduces it exactly at three of four points** (93 at sensitivity 0.5, 78 at 0.7, 60 at 0.8); at
sensitivity 0.9 it returns **37** where that lane reported 34 — a small discrepancy in the
degenerate tail worth one line of reconciliation, and immaterial to the verdict.

| true sensitivity | n required (CI width ≤ 0.20) | n available | shortfall |
|---|---|---|---|
| 0.5 | 93 | **15** | 78 |
| 0.7 | 78 | **15** | 63 |
| 0.8 | 60 | **15** | 45 |
| 0.9 | 37 | **15** | 22 |
| *preregistered floor* | *30* | **15** | *15* |

At n = 15 the achievable 95% CI width on a sensitivity of 0.5 is **0.4515** — more than twice the
declared 0.20. **The entire published, experimentally validated set falls short of the run's own
preregistered floor of 30, before any width criterion is applied at all.** Restricted to the
MS-eluted subset that a presentation threshold is genuinely about, n = **6**.

Per-allele the position is worse still: **A\*02:01 n=5, B\*07:02 n=3, A\*24:02 n=2, C\*04:01 n=2,
and A\*68:02, B\*40:01, C\*12:03 n=1 each.** An allele-specific cut cannot be calibrated at any
allele, and the pooled cut is confounded by nine fusions across seven allotypes.

**Consequence for §6.1's ordering.** PUB-VACCINE-PATH showed step 1 was *unmeasured*; this shows it
is **unachievable at the precision the preregistration demands**, and that the shortfall is not a
collector defect but a property of the literature. A successful IEDB re-fetch — even a perfect one
with the stable-paging patch applied — cannot close a 78-epitope gap that does not exist in the
published record to be fetched. The honest move is therefore **not** "fix the collector and re-run to
get the number"; it is to **retire the calibration as a gate** and report §2.3's coverage curve as
the only defensible statement, exactly as that lane's own §6 step 2 anticipated.

### (b) Does a properly-scoped inclusion rule recover anything the keyword rule missed? **Yes — and the amount it recovers is the finding.**

An explicit cancer-fusion oncoprotein list plus an assay-method filter recovers **15** class I
junction epitopes (≈20 if the six sequence-unresolved ones were chased down offline). PUB-NEOANTIGEN
found **0** in the 988 keyword records across 44 source antigens, and **none** of the nine fusions
above appears among those 44. So the keyword rule missed the entire real set — but the real set is
**fifteen peptides**, not a corpus. **Both lanes' readings are correct and they compose:** the 988 is
a keyword artifact *and* the properly-scoped number is single- to low-double-digit. Quoting 988 as a
count of validated fusion-junction epitopes overstates it by roughly **65-fold**.

The census also supplies the quantitative reason a **source-protein** filter cannot substitute for a
**junction** filter, which is exactly the defect in the committed rule: in the one study that
enumerates both, **2 of 20** MS-identified class I ligands from the DNAJB1-PRKACA fusion protein
actually span the junction (10%), and **1 of 13** class II peptides (PMID 36302754,
[DOI](https://doi.org/10.1038/s41467-022-33746-3)). A rule keyed on the source antigen therefore
over-counts junction epitopes by about an order of magnitude even when the antigen is a *genuine*
cancer fusion — a distinct error from the keyword artifact, and one a corrected fetch would still
make unless it filters on the register.

### (c) A caution the count carries, in the direction that matters

The literature also records that this antigen class **binds class I poorly and vaccinates badly**:
only 6 of 14 p210 BCR-ABL junction peptides bound any of eight allotypes and CTL lines arose only
against **non**-junction peptides (PMID 9295046); the SYT-SSX breakpoint phase II saw DTH negative in
all 21 patients with "no robust evidence of immune response to the target epitope" (PMIDs 22726592,
23252384); and the vaccinated FL-HCC patient mounted **no CD8 response** to any of the three class I
junction peptides (PMID 36302754). A benchmark assembled from the 15 would therefore also be
**selected for success** — every entry is a published positive — so any sensitivity estimated on it is
an **upper bound**, compounding the circularity PUB-VACCINE-PATH already flagged (MHCflurry is trained
on IEDB). This makes the n = 15 shortfall an *optimistic* reading of the calibration's feasibility.

## 6 · Artifact · validation · provenance · limitations · stop condition

* **Artifact.** `VALIDATED-EPITOPE-TABLE.md`, `epitope-records.json` (40 records),
  `validated-epitope-counts.json`, `tabulate_epitopes.py`, `render_table.py`, `checks/` (5 attempts).
* **Validation / baseline.** (i) The sufficiency arithmetic is an **independent recomputation** that
  reproduces PUB-VACCINE-PATH's 93 / 78 / 60 exactly and differs only at sensitivity 0.9 (37 vs 34) —
  a genuine cross-check, and the discrepancy is reported rather than smoothed. (ii) The table carries
  **six negative-control rows** that do *not* span the junction (out-of-frame BCR-ABL peptides, the
  SSX-region peptides, ERG295, ALKa/ALKb, the BRD4::NUTM1-driven PRAME ligands, the ABL E255V
  mutation neoepitope), so the spans-the-junction column is demonstrably discriminating and not a
  column of "yes". (iii) Prediction-only and binding-only rows are retained **in** the table and
  excluded **from** the counts by an explicit rule in code, so the exclusion is re-runnable.
  (iv) Q1 is a within-study control from the source itself, not my inference.
* **Provenance.** PubMed/PMC MCP server, 2026-09-09. Every row carries a PMID and, where one exists,
  a DOI. Full text was read for PMC6558662, PMC9613889, PMC12818165. Cost $0. No GPU, no paid API.
* **Limitations.** ⛔ No efficacy, safety, presentation or clinical-readiness claim; a threshold
  benchmark calibrates a predictor. (i) Recall is bounded by NCBI automatic term mapping — 12 of 26
  queries returned zero because the mapper `AND`s every token — so **n = 15 is a lower bound**, which
  is the safe direction for a shortfall conclusion but means a hand-curated systematic review would
  find more. (ii) Six measured junction epitopes have sequences this route cannot recover; including
  all of them raises the count to at most ~20 and changes no conclusion. (iii) `EWSR1::FLI1` — named
  in the lane manuscript's §B1 as contributing four peptides — returned **no** experimentally
  validated junction epitope through nine queries; that is an unresolved discrepancy with §B1, not a
  refutation of it. (iv) PMC full text strips some gene symbols, so per-peptide partner attribution
  for three adenoid-cystic peptides is given at the source-group level. (v) The table is a census of
  *published positives* and is selected for success (§5c). (vi) Nothing here says anything about
  IEDB's contents; IEDB was never reached.
* **Stop condition.** Reached. The number both lanes needed is measured, its sufficiency is decided
  against the criterion that was already preregistered, and the answer does not depend on the
  unreachable source. The next move is a paper-owner decision, not another computation.

## 7 · Proposed, UNAPPLIED — no shared file was edited

Neither the lane manuscripts nor `systems/graph/*.json` were touched. Two sentences are offered for
the paper owner's judgement, each of which must travel with §6's limitations:

1. For `emc-vaccine-development-path.md` §6.1 — *"A literature census of experimentally validated
   cancer gene-fusion junction epitopes returns 15 class I epitopes across nine fusion oncoproteins,
   of which six carry mass-spectrometric elution evidence and all six of those were eluted from
   engineered cell lines rather than a patient tumour; against the preregistered criterion of a 95%
   CI width ≤ 0.20, which needs 93 epitopes at sensitivity 0.5 and 60 at 0.8, the available set falls
   short of even the n ≥ 30 floor, so the acceptance threshold cannot be defended by calibration and
   the coverage curve of §2.3 remains the only supportable report."*
2. For the neoantigen manuscript, to accompany PUB-NEOANTIGEN's existing proposed sentence — *"A
   correctly scoped search of the published literature recovers 15 validated class I fusion-junction
   epitopes that the source-antigen name pattern missed entirely; within a single genuine fusion
   oncoprotein, only 2 of 20 mass-spectrometrically identified class I ligands span the junction, so
   filtering on the source protein rather than the register over-counts by roughly tenfold."*

Whether either belongs in a manuscript is the paper owner's call.

## 8 · Next credible independent work (not done here, not authorised here)

1. **Retire, do not repair, the calibration gate.** Applying PUB-VACCINE-PATH's stable-paging patch
   and re-running the collector is still worth doing for a *measured* count in place of `WITHHELD` —
   but it should be framed as recording the shortfall, not as obtaining a calibration. No fetch can
   supply 78 epitopes the literature does not contain.
2. **Resolve the `EWSR1::FLI1` discrepancy** in §B1 by checking the manuscript's own citation
   directly, since PubMed term mapping did not surface it here.
3. **Recover the six unresolved sequences** — Worley 2001 (no PMC), the BCR-ABL HLA-A3/-A11/-B8
   junction peptides, the TMPRSS2::ERG type-VI epitopes — from the publishers' PDFs on the CI runner.
   This is completeness work; it cannot change the verdict.
4. **If a benchmark is ever wanted at all**, prefer a **paired** design (McNemar on the same epitopes
   under two cuts), which needs fewer epitopes than the independent-binomial table assumes — though
   on n = 15 across seven allotypes even that is unlikely to separate 0.5 from 0.2.
