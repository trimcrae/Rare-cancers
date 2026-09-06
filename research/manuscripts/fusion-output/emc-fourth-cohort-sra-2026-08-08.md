---
id: DOC-EMC-FOURTH-COHORT-SRA-2026-08-08
title: A fourth EMC cohort exists in SRA — PRJNA1357027 / SRP640302 characterised (2026-08-08)
level: L3
kind: manuscript
status: live
canonical_for: []
purpose: Records the SRA-side characterisation of PRJNA1357027 / SRP640302 — a real, public, n = 12
  FFPE EMC tumour cohort with per-sample EWSR1 break-apart FISH status that every GEO-side search in
  this repository was correct to miss. Carries the exact queries, the three transport controls, the
  measured counts, the TempO-Seq panel limitation that gates every use of it, and the two query-shape
  defects found and fixed in the same session.
scope: Archive metadata only. NO expression value is read, measured or implied anywhere in this
  document, and no claim about EMC biology, treatment, efficacy or safety is made. Sample counts are
  BioSamples, not patients-by-chart.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-08
last_verified: 2026-08-08
---

# A fourth EMC cohort exists, it is public, and it is the first one with per-sample fusion status

**2026-08-08 · `PRJNA1357027` / `SRP640302` · verdict `EMC_PUBLIC_CANDIDATE`**

One home for the machine-readable result:
[`emc-sra-study.json`](../../modalities/emc-sra-study.json) (verdict) and
[`emc-sra-study-inputs.json`](../../modalities/emc-sra-study-inputs.json) (every raw payload).
Instrument: [`emc_sra_study.py`](../../modalities/emc_sra_study.py), dispatched as
`emc-expression-datasets.yml mode=sra-study`. **Every number below is read from those artifacts —
none is typed from a run log.**

---

## 1 · The question, and why the repo's existing negatives could not answer it

[`nr4a3-fusion-transcriptional-output.md`](./nr4a3-fusion-transcriptional-output.md) §3.13 records
that **no fourth EMC cohort exists**, and
[`emc-cohort-search.json`](../../modalities/emc-cohort-search.json) reaches the same conclusion from a
search that worked properly — **56 candidates examined, 15 naming EMC in prose, positive control
passing, zero new cohorts, zero ungraded**.

**Both are GEO-side, and both are correct.** That artifact's own `⛔ scope` field states the bound
it cannot cross: *"GEO esearch matches DEPOSITOR PROSE. … A null result bounds what a term search
over GEO can reach; it is NOT a statement that no fourth cohort exists."*

⭐ **So this is not a search that failed and was redone. It is a different archive**, and the two
verdicts stand side by side without contradicting each other.

⭐ **A deposit registered in SRA that never received a GEO series is outside both searches by
construction.** That is exactly what this is.

⚠ **And the repo was already holding half the answer without knowing it.**
[`emc-atr-vulnerability-inputs.json`](../../modalities/emc-atr-vulnerability-inputs.json) →
`part_b.dataset_search.sra.studies[0]` has carried `SRP640302` **with its full title** since the
four-archive search;
[`emc-atr-vulnerability-assessment.md`](../dependency/emc-atr-vulnerability-assessment.md) §3.0a names it as
⭐ real. What nobody had done was **open it**. A title is not a characterisation, and the
assessment's own guess about it — *"these are RAW READS"* — turns out to be right in letter and
misleading in substance (§4 below). **`PRJNA1357027` appears nowhere in this repository before
today**; only the `SRP` side was ever recorded.

---

## 2 · What was asked, in two archives, with three controls

NCBI E-utilities and EBI/ENA were queried independently, from a GitHub Actions runner — the dev
sandbox's egress proxy 403s both on CONNECT (measured this session: `curl` exit 56, *"CONNECT tunnel
failed, response 403"*, on `eutils.ncbi.nlm.nih.gov` **and** `www.ebi.ac.uk`).

**⛔ The controls are the load-bearing part, because a proxy refusal, a rate-limit and a genuinely
absent record all arrive as "no records".** All three ran through the same code paths as the target.

| control | accession | expect | NCBI bioproject | NCBI sra | ENA runs | passed |
|---|---|---|---|---|---|---|
| `ctrl_real_bioproject` | `PRJNA1273954` | non-zero | 1 | 68 | 135 | ✅ |
| `ctrl_real_sra_study` | `SRP445369` | non-zero | 0 | 4 | 4 | ✅ |
| `ctrl_absent` | `PRJNA9999999` | **zero** | 0 | 0 | 0 | ✅ |

**Transport gate: PASSED.** The negative control is the half usually missing: without it, a matcher
loose enough to return something for everything makes every accession "exist", and no positive
control can detect that.

### Queries and what each returned

| query | returned |
|---|---|
| `esearch db=bioproject term=PRJNA1357027[All Fields]` | **count 1** |
| `esearch db=sra term=PRJNA1357027[All Fields]` | **count 12**, 12 UIDs |
| `esearch db=sra term=SRP640302[All Fields]` | **count 12**, 12 UIDs |
| `esearch db=bioproject term=SRP640302[All Fields]` | count 0 — *expected; an SRP is not a BioProject accession* |
| `esearch db=biosample term=…[All Fields]` (both) | count 0 — **a query shape, not an absence; the linked count below is 12. See §6** |
| `efetch db=sra rettype=full retmode=xml` (both) | **12 `EXPERIMENT_PACKAGE`s**, parsed, not truncated |
| ENA `filereport result=read_run` (both) | **12 rows each** |
| ENA `browser/api/xml` (both) | study title + abstract |
| ENA `filereport result=sample` (both) | **HTTP 400** on run 1 (malformed), **HTTP 200 with zero rows** on run 2 — *root-caused in §6* |
| `elink dbfrom=sra db=biosample` (both, added after run 1) | **12 linked BioSample UIDs each** |

---

## 3 · What it is

**BioProject title, verbatim:** *"Prognostic Biomarkers for Enhanced Risk Stratification in
Extraskeletal Myxoid Chondrosarcoma: A Retrospective Cohort Study"*
**Experiment title, verbatim:** *"Targeted RNA-seq (TempO-Seq) of EMC"*
**Registered** `2025/11/04` · **first public** `2025-11-11`.

⭐ **The 12 runs are 12 distinct biological specimens, not repeat sequencing of fewer — and that was
checked, not assumed.** Run, experiment and BioSample counts are three different numbers, and all
three are 12: `SRR35940646`–`SRR35940657`, 12 distinct experiments, `SRS26982694`–`SRS26982705`,
and **12 distinct submitter aliases** (`Si01, Si02, Si05, Si09, Si10, Si14, Si15, Si16, Si17, Si19,
Si20, Si22`). One run per sample, no replicates, no treated/untreated arms, no cell lines — every
sample is `Isolate = FFPE` human tumour tissue.

⛔ **12 BioSamples is NOT the same claim as 12 patients, and the metadata cannot close the gap.**
Nothing in the record links a specimen to a person, so one patient contributing a primary and a
metastasis under two `Si` numbers would be indistinguishable from two patients. The distinct ages,
sexes and collection dates make a 12-patient series the natural reading, but that is an inference
and it is not written anywhere as a measurement. **Everywhere below, n = 12 means BioSamples.**

**This is the largest EMC expression cohort in the repository.** The manuscript's three arms are
n = 6 (`GSE24369`), n = 10 (`GSE4303`) and n = 4 (`GSE28866`).

### ⭐ The per-sample clinical annotation, which is the actual prize

Every one of the 12 BioSamples carries all sixteen attributes below. Counts are derived from the
returned XML:

| attribute | values |
|---|---|
| **`FISH_1`** | **`EWSR1+` 8 · `EWSR1-` 4** |
| `Prognosis` | `B` 6 · `G` 6 |
| `Metastasis` | `Met` 10 · `No_Met` 2 |
| `Cellularity` | `Classical` 9 · `HG-spindle` 2 · `HG-solid-cellular` 1 |
| `Synaptophysin` | `NA` 7 · `Neg` 4 · `Pos` 1 |
| `Sex` | female 7 · male 5 |
| `Age` | 12 values, 37–77 |
| `Etnics` | Asian 8 · Caucasian 4 |
| `Tissue` | Thigh 7 · Chest wall, IA knee, Popliteal, Hand, Buttock 1 each |
| `Time` | 12 values, 0–23 |
| `Collection date` | 1997–2020 |
| `Size (cm)`, `Biomaterial Provider` (`Siriraj Hospital`), `Geographic location` (`Thailand`), `Isolate` (`FFPE` ×12), `BioSampleModel` | present on all 12 |

⭐ **`FISH_1` is per-sample fusion status, and this repository has been explicitly waiting for it.**
[`method-watch-triggers.json`](../../method-watch-triggers.json) `TRG-EMC-EXPRESSION-DATASET`
`_still_watching_for` (a) reads: *"an EMC dataset with per-sample FUSION CONFIRMATION — none of the
three series has one, so … an EMC LABEL is indistinguishable from an EMC FUSION (the H-EMC-SS
lesson)."* **Clause (a) is now satisfiable.**

⚠ **But read `FISH_1` for what it is.** It is a **break-apart FISH call on `EWSR1`**, not a fusion
partner call and not a junction. `EWSR1+` says the locus is rearranged; it does not name `NR4A3` as
the partner, and `EWSR1-` in an EMC-labelled case is consistent with a `TAF15::NR4A3` or
`TCF12::NR4A3` variant — the very ambiguity the trigger describes — not with "not EMC". The
4 `EWSR1-` samples are therefore **informative and unresolved**, and a fusion caller over the reads
is what would resolve them.

⚠ **`Prognosis` `B`/`G` and `Time` are UNEXPLAINED KEYS.** Nothing in the returned metadata defines
them. The reading that they are bad/good outcome and follow-up duration is **inference, not a
measurement**, and must not be written into any result until the depositors' publication defines
them.

---

## 4 · Is the data public, or only the metadata?

**Public and downloadable.** All **12/12 runs carry a populated `fastq_ftp`**, totalling
**2,704,945,123 bytes** (~2.7 GB). `submitted_ftp` is empty on all 12, so the FASTQs are ENA's
converted copies.

Library: `library_strategy RNA-Seq` · `library_selection cDNA` · `library_source TRANSCRIPTOMIC` ·
`library_layout SINGLE` · `ILLUMINA` / `Illumina HiSeq 2500`.
Read counts: **5,419,081–8,734,357 per run**, 81,123,915 total.

⛔ **THE STRUCTURED FIELD AND THE TITLE DISAGREE, AND THE TITLE IS THE ONE THAT CONSTRAINS THE
SCIENCE.** `library_strategy` says `RNA-Seq`; the experiment title says **`Targeted RNA-seq
(TempO-Seq)`**. TempO-Seq is a **templated-oligo ligation panel**, not whole-transcriptome
sequencing. Everything observable agrees with the title rather than the field: single-end reads at
~5–9 M per sample is panel depth, not transcriptome depth, and FFPE input is what the assay is
sold for. **So the usable gene space is the panel's, and the panel identity is not in the
metadata.** Which TempO-Seq panel (S1500+ ≈ 3,000 genes, or a whole-transcriptome variant ≈ 20,000)
is **the single most decision-relevant unknown**, and it is not answerable from the archive record
— it needs the depositors' publication or a read of the FASTQs themselves.

⚠ This is why the assessment's *"these are RAW READS"* was right and misleading at once: raw reads,
yes — but not reads you can quantify into a general expression matrix. A conventional
align-and-quantify pipeline pointed at these files would produce a matrix that is **mostly zeros by
construction**, and nothing in the metadata warns you.

---

## 5 · Publication, GEO cross-link, and whether the repo already had it

Searched across every payload returned for the two target accessions:

| looked for | found in target payloads |
|---|---|
| a `pubmed` field | **none** |
| a `PMID` | **none** |
| a `DOI` | **none** |
| a GEO `GSE`/`GSM` accession | **none** |

⚠ The 69 GEO accessions present in the inputs cache belong to **`ctrl_real_bioproject`'s** payloads
(`PRJNA1273954` → `GSE299349`), not to the target. That was checked per-fetch rather than over the
whole file, because a repo-wide grep would have attributed the control's links to the target.

**So: no linked publication, and no GEO mirror.** Registered 2025-11-04, public 2025-11-11 — a
deposit ahead of its paper. **This is also why every GEO-side search in this repository was correct
and still missed it.**

**Already in the repo?** `SRP640302` — yes, as a title in one study list, never opened.
`PRJNA1357027` — **no, nowhere, before today.**

---

## 6 · Two readings that were wrong in the way this instrument exists to prevent

Both were produced by run `31276593535`, caught, root-caused from the servers' own responses, and
fixed in the same session (run `31276785752` re-fetches with the corrections).

1. **NCBI `biosample` esearch returned `count: 0` for both accessions** — while the SRA XML for the
   same deposit carried **twelve fully populated BioSample attribute sets**. A term search over
   `biosample` does not index a project accession. **The zero was a query shape, not an absence.**
   ✅ **Fixed and confirmed:** asking by relationship instead of by string (`elink dbfrom=sra
   db=biosample`) returns **`biosample_linked_uids: 12`** for both accessions in run `31276785752`,
   against the term search's unchanged `0`. The term-search zero now carries a note saying what it
   is, so the two can never again be read as agreeing.
2. **ENA's `sample` endpoint answered HTTP 400 for both accessions**, and said why in its own body:
   *"Accession(s) PRJNA1357027 not valid for search requests on sample data."* That endpoint takes
   sample accessions, not a project accession, and a 400 and a deposit with no samples produce the
   same row count. **The request is now well-formed** — sample accessions are harvested from the run
   report and asked for by name — and a skipped query records `not_attempted` rather than being
   absent, because a missing key reads as zero.
   ⚠ **But the fix did not produce sample rows, and that is stated rather than smoothed over.**
   Run `31276785752`: **HTTP 200, header row, zero data rows** — for accessions ENA's *own* run
   report had just emitted (`sample_accession SAMN53073761`, `secondary_sample_accession
   SRS26982700`, both passed). So two endpoints of the same archive disagree about whether these
   samples exist. **This is now an ENA-side gap rather than a malformed request of ours, which is
   the whole difference between the two readings** — and the cause is not established here, so it is
   not guessed at. The sample level is fully available from NCBI's XML either way (204 attribute
   values across 12 samples, both runs).

⭐ **Neither defect changed the verdict, and that is precisely why they were worth chasing.** NCBI's
XML supplied the sample level that ENA's call would have duplicated — the dual-archive design doing
its job. **A gap covered by redundancy is invisible until the redundancy is gone.**

**Both runs agree on every reported number.** Run `31276593535` (**29 payloads**) and run
`31276785752` (**31** — the two added `elink` calls) return the same verdict, the same 12/12/12, the
same attribute counts and the same 2,704,945,123 bytes. **Run 2 has zero non-`read` fetches**;
run 1 had the two ENA 400s. The committed verdict re-derives from the committed payloads —
`emc_sra_study.py --check` passed in CI, and
`test_the_committed_artifact_if_present_re_derives_from_its_own_cached_payloads` now runs against
the real artifact instead of skipping.

⚠ **One discrepancy inside the deposit itself, reported and not resolved:** on one sample the
submitter's `sample_alias` is **`Si22`** while its `library_name` is **`Si21`**. Both are the
depositors' own strings. It is recorded verbatim in the artifact; it does not change any count
(aliases and BioSample accessions are both 12-distinct), and it is not this repository's to fix.

---

## 7 · Verdict

> **`EMC_PUBLIC_CANDIDATE` — a fourth EMC cohort exists. It is `PRJNA1357027` / `SRP640302`,
> n = 12 FFPE EMC tumours, public and downloadable since 2025-11-11, carrying per-sample
> `EWSR1` break-apart FISH status, site, size, morphology and outcome-adjacent annotation. It is
> larger than any of the three cohorts the manuscript reads. It is TempO-Seq targeted panel data,
> so its gene space is the panel's and the panel is not named in the structured metadata; there is
> no GEO mirror.**
>
> ⚠ **SUPERSEDED CLAUSE, RETAINED: "there is no linked publication".** There is, and it was already
> published when this note was written. See §10.

⛔ **What this is NOT.** It is not a processed expression matrix, not whole-transcriptome, not
fusion-partner-resolved, and not yet read. Nothing in this note is an expression measurement. The
n = 12 counts **BioSamples**, which is the closest thing the metadata supports to a biological n.

### What §3.13 should say — **for the coordinator to integrate; this agent did not edit that file**

> §3.13's negative was **GEO-side**, and it stands as such. It does **not** cover SRA-only deposits,
> and one exists: `PRJNA1357027` / `SRP640302`, 12 FFPE EMC tumours, public since 2025-11-11, with
> per-sample `EWSR1` break-apart FISH status — characterised in
> [`emc-fourth-cohort-sra-2026-08-08.md`](./emc-fourth-cohort-sra-2026-08-08.md), artifact
> [`emc-sra-study.json`](../../modalities/emc-sra-study.json). It is TempO-Seq targeted-panel data, so
> it is **not** a drop-in fourth arm for a whole-transcriptome contrast, and Limitation 1's "three
> cohorts of 4, 6 and 10" is unchanged **for the analyses the manuscript actually runs**. What
> changes is that "no fourth EMC cohort exists" is no longer sayable without the GEO-side
> qualifier.

---

## 8 · What characterising it would take, in order, all $0

1. **Name the panel.** Download one run (~225 MB of the 2.7 GB) and read the raw sequences: the
   number of DISTINCT sequences and their length distribution is a direct measurement of how many
   probes the panel has, whatever the assay is called. ⚠ That is the *test to run*, not a claim
   about TempO-Seq's read structure — this note asserts nothing about the assay's internals.
   Cheaper still: wait for the depositors' publication, which does not exist yet (§5).
   **Everything below is gated on this** — the panel's gene list determines which of the reads
   below are even askable. One CI run, no GPU.
   ⚠ **SUPERSEDED 2026-08-24, RETAINED.** The depositors' publication existed on the day this
   line was written and it names the assay as **whole-transcriptome** targeted RNA sequencing —
   which is this note's own ≈20,000-gene variant, not S1500+. The download is no longer the
   cheapest way to name the panel, and it is still the only way to *verify* the name against the
   reads, which nothing here has done. §10.
2. **Quantify against the panel.** Once named, TempO-Seq quantification is probe-count matching,
   not spliced alignment — cheap, CPU-only, and it does **not** need the alignment pipeline
   §3.0a's table assumed.
3. **The fusion-partner call the FISH cannot make.** Targeted panel reads may or may not span the
   `NR4A3` junction; whether they do is answerable from the panel definition in step 1. If they do,
   the 4 `EWSR1-` samples become the most informative rows in the repository.
4. **`Prognosis`/`Time` stay unused until defined by the depositors' publication** — §3's warning.

---

## 9 · Which of `BLK-NO-EMC-DATA`'s routes this touches

`BLK-NO-EMC-DATA` is inherited by **19 routes** (`blockers_inherited` in
[`systems/graph/routes.json`](../../../systems/graph/routes.json) — measured, not counted by hand) and
named in `required_validation` by the same 19. **This lead does not retire the blocker**, whose
statement is about *functional-genomics* data — one DepMap line, no CRISPR. A tumour expression
panel is not a dependency screen.

**What it does move** is every route whose ask is *expression in EMC tumour tissue with per-sample
annotation*, and it moves them only as far as step 1 above allows — a route needing a gene outside
the panel gains nothing. On the evidence in hand the strongest candidates are the surface-antigen
and stratification routes (`RT-SSTR2`, `RT-B7H3`, `RT-CART-SURFACE`, `RT-PARTNER-STRAT`,
`RT-FUSION-OUTPUT`, `RT-ENDPOINT-CHOICE`), because they ask for a named gene's level in tumour
tissue and now have a cohort with fusion status and outcome-adjacent labels attached.

⚠ **That list is a reading of the routes' asks, not a graph edit**, and it is deliberately not
written into `systems/graph/` as a per-route claim: which routes actually benefit is **not knowable
until the panel is named**, and recording a benefit the panel may not support would be exactly the
"populated field is not a measured one" failure. The graph records **the lead and what would retire
the blocker**, and nothing more.

---

## 10 · Update 2026-08-24 — the deposit's publication exists, has existed all along, and the field this note searched for was the wrong one

**The finding.** `PRJNA1357027` / `SRP640302` is the data behind
**Chaiboonchoe A, Chanthercrob J, Sakamula R, et al. "Prognostic biomarkers for enhanced risk
stratification in extraskeletal myxoid chondrosarcoma: a retrospective cohort study." PeerJ 2026;
doi 10.7717/peerj.21497; PMID 42465974**, first published **2026-07-13** — twenty-six days before
§5 of this note concluded there was no linked publication.

**The evidence, all of it already inside the payloads §5 searched.**

| what matches | archive record | publication |
|---|---|---|
| study title | `STUDY_TITLE` = *"Prognostic Biomarkers for Enhanced Risk Stratification in Extraskeletal Myxoid Chondrosarcoma: A Retrospective Cohort Study"* (§3) | the paper's title, word for word |
| depositor | `Submitter contact_name="amphun chaiboonchoe"`, `center_name="Mahidol University"` | first author `Chaiboonchoe A` |
| specimen source | `Biomaterial Provider = Siriraj Hospital`, `Geographic location = Thailand` | Siriraj Hospital, Mahidol University |
| n and material | 12 BioSamples, every one `Isolate = FFPE` | "12 molecularly confirmed EMC cases", archival FFPE |
| assay | `Targeted RNA-seq (TempO-Seq) of EMC` | "whole-transcriptome targeted RNA sequencing (TempO-Seq)" |
| prognosis split | `Prognosis` `B` 6 · `G` 6 | good-prognosis n = 6 (OS > 8 y) versus poor-prognosis n = 6 (OS < 8 y) |

⛔ **The defect is not that the search was shallow. It is that it asked for identifiers and read
their absence as the absence of a publication.** §5's table looked for a `pubmed` field, a `PMID`,
a `DOI` and a GEO accession, found none of the four, and concluded correctly that none of the four
was present — then the verdict turned that into *"there is no linked publication"*. The title was in
the same payload and the depositor's name was in the same payload, and either one resolves the
question in a single query. **An absent reading is not a reading of absence** (CLAUDE.md §4), and
this is that rule failing on the field the rule is usually quoted about.

### 10.1 · What it unblocks: the panel is named

§4 called the panel identity **"the single most decision-relevant unknown"**, and §8 gated every
downstream read on naming it. The paper's own Methods sentence names it: **whole-transcriptome**
TempO-Seq, which is this note's ≈20,000-gene variant rather than S1500+ ≈ 3,000.

⚠ **That is the depositors' description, not a measurement.** It comes from the same authors who
wrote the deposit, so it is one source, not two, and it does not say which catalogue build or how
many probes passed QC. §8's step 1 — count the distinct probe sequences in one downloaded run —
remains the only *independent* check, and it is now a verification rather than a discovery. What
changes for planning is the prior: a read that needs a gene outside a 3,000-gene panel is no longer
likely to be unaskable.

### 10.2 · What it adds that this note did not anticipate: EMC immune profiling

The paper reports, in EMC tumour tissue: computational immune-infiltration estimates with **higher
B-cell infiltration in the low-risk group (P = 0.005)**, and proof-of-concept **multiplex
immunofluorescence on two specimens** describing a spatially localised immunosuppressive
microenvironment in the high-risk specimen — increased exhausted **CD3⁺CD8⁺PD1⁺** T cells
(P = 6.4 × 10⁻⁵) and **FOXP3⁺** regulatory T cells (P = 0.006). The authors state that all
multiplex-immunofluorescence comparisons are within-specimen region-of-interest analyses, that the
cohort is small, that their prognostic model overfits, and that the findings are exploratory and
hypothesis-generating. Their own conclusion on this axis is that immune microenvironment
heterogeneity in EMC warrants further investigation.

⭐ **This is the class of observation `emc-vaccine-development-path.md` §B8 says does not exist for
this disease** — that entry's proposition is that EMC's characterisation as cold and as excluded is
inferred from mutational burden, histology and sarcoma-wide experience "rather than from published
EMC-specific immune profiling", and its *what would clear it* is infiltrate quantification on a
series of EMC specimens. A twelve-specimen series with two-specimen spatial validation is not that
series, and it does not clear B8. It does mean B8's proposition is no longer literally true, and
the direction of the exploratory finding is that lymphocytes are **present and exhausted or
suppressed** rather than absent — which distinguishes B7 (excluded) from B6 (cold) in the direction
this note cannot itself adjudicate.

⛔ **Nothing in §10.2 is read from data.** Every figure is quoted from the paper's abstract as
retrieved from Europe PMC; the full text returned HTTP 403 to the runner and has not been read
here, so the infiltration method, the external validation cohorts and the per-sample values are
unexamined. No efficacy, treatment or clinical claim follows from any of it.

### 10.3 · What this does not change

The verdict grade, the counts, the annotation table, the transport controls and the GEO-side
negatives all stand exactly as measured. `BLK-NO-EMC-DATA` is **still not retired** for the reason
§9 gives — its statement is about functional-genomics data, and a tumour expression panel is not a
dependency screen, whoever published it.


## 11 · Update 2026-09-06 — processed supplementary matrix recovered

The public full-text JATS and named Data S1 workbook have now been recovered through Europe PMC.
The [verified source packet](../../autonomy/peerj21497-source-2026-09-06/decision.md) preserves the
original workbook, archive, source-cell inventories and independent coordinator checks. Data S1
is a 9,500-feature by 12-sample processed export labelled log2CPM, not the raw 22-case probe
matrix. Seven prespecified atlas symbols have rows. Five are absent for unresolved reasons;
missing rows are not zero expression. Six feature identifiers are numeric, and the difference
from the article's stated 9,909 genes is unresolved. No external MI-ONCOSEQ matrix, probe map,
normalization factors, known batch-correction state or same-assay normal arm is supplied.

This supersedes lack of an available processed matrix, not the original raw-read probe-design
gate or functional-genomics limitations. The primary Methods reports twelve patients after
exclusions; that is stronger evidence than merely counting BioSamples. Column-to-patient and
aliquot links remain unavailable in this workbook. Conditional on twelve distinct represented
patients and an at-most-six-patient discovery cohort, at least six patients must be new to
discovery; their identities and separation from every other cohort do not follow. No new
expression contrast, calibrated detection criterion, target validation or manuscript result
is established. The source packet's coordinator verification records the exact scope.
