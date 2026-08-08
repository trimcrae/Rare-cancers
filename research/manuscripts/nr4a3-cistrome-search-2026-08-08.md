---
id: DOC-NR4A3-CISTROME-SEARCH
title: The NR4A3-fusion cistrome search, 2026-08-08 — a measured absence, re-run wide, and overturned
level: L3
kind: memo
status: live
canonical_for: [nr4a3_fusion_chromatin_retrieval_search]
purpose: >
  Settle, reproducibly, whether any genome-wide chromatin or binding experiment has been performed with
  an NR4A3 fusion. PUB-FUSION-OUTPUT rests on the answer being "none retrieved"; this note re-runs the
  search across the primary sequence archives rather than the literature alone and records what came back.
scope: >
  Retrieval only. Nothing here re-analyses a dataset, and nothing here is an efficacy, selectivity,
  safety, therapeutic-window or clinical-readiness statement about any agent, target or gene.
audience: [maintainers, autonomous research agents]
date: 2026-08-08
last_verified: 2026-08-08
---

# The NR4A3-fusion cistrome search, 2026-08-08

**Corpus:** [`lit-targets-nr4a3-cistrome.json`](./lit-targets-nr4a3-cistrome.json) — 179 API endpoints,
every query string preserved verbatim, re-runnable in one dispatch.
**Payloads:** branch `literature-cache`, `literature/nr4a3-cistrome-search{,-r2a,-r2b,-r3,-r4,-r5,-r6}/`.
**Run window:** first dispatch 1:54 PM ET, last round completed 2:26 PM ET, Saturday 2026-08-08. **Cost: $0** (GitHub Actions, no GPU).

---

## 1 · The result, first

**A genome-wide chromatin experiment performed with an NR4A3 fusion exists, is public, and is
downloadable without a login: [GEO **GSE243553**].** It is the deposit behind Frenkel *et al.*,
*Nature Biotechnology* 2025 (PubMed identifier 39048711, PMC13105821) — **PROD-ATAC**, a pooled
single-cell ATAC screen of more than 100 oncofusions expressed in HEK293T. Its library contains
**four NR4A3 fusions — EWSR1-NR4A3, TAF15-NR4A3, TCF12-NR4A3 and TFG-NR4A3** — together with two
controls that are exactly the ones this manuscript's argument needs: **full-length wild-type NR4A3**,
and the **reciprocal NR4A3-EWSR1**.

⛔ **This does not deliver a fusion cistrome, and the distinction is the whole point.** ATAC measures
**accessibility**, not occupancy; the cells are HEK293T, not EMC; the protein is ectopically expressed,
not endogenous. So the two claims in
[PUB-FUSION-OUTPUT](./nr4a3-fusion-transcriptional-output.md) come apart:

| claim as written | status after this search |
|---|---|
| "no **genome-wide chromatin experiment** performed with an NR4A3 fusion was retrieved" (§3.11, §6, cover letter) | **OVERTURNED.** GSE243553 is one, for four different NR4A3 fusions. |
| "no EWSR1::NR4A3 **cistrome** has been retrieved" (§3.11) — an occupancy map | **STANDS**, and is now much better bounded (§4 below). |
| "'up in EMC' and 'driven by the fusion' cannot be told apart" (§6) | **WEAKENED, not closed.** A fusion-versus-wild-type-NR4A3 contrast now exists genome-wide, in the wrong cell type and in the accessibility channel. |

**Figures reported by that paper**, quoted from its own text (PMC13105821) and *not* re-derived here:
TAF15-NR4A3 increased accessibility at **≈8,600 peaks**, within which "the NR4A family motif was highly
enriched"; **EWSR1-NR4A3** gave **1,235 differentially accessible peaks across 112 nuclei**; the direct
TAF15-NR4A3 vs EWSR1-NR4A3 comparison gave "only a few hundred altered peaks out of the 8,600";
**full-length wild-type NR4A3 changed 0 peaks**; and the reciprocal **NR4A3-EWSR1 gave 0 peaks over 503
nuclei**. The authors state plainly that gain-of-function "has not been shown for … TAF15-NR4A3,
TFG-NR4A3, EWSR1-NR4A3, or TCF12-NR4A3 **all of which are shown here**."

---

## 2 · Why the previous search could not see it

Not a retrieval failure of effort — a failure of **vocabulary**, and it is worth recording because the
same shape will recur.

1. **The prior repository census was ANTIGEN-centric.**
   [`emc-ret-cistrome.json`](../modalities/emc-ret-cistrome.json) streamed all 845,824 ChIP-Atlas
   experiments — but filtered on antigen ∈ {NR4A1, NR4A2, NR4A3}. A pooled ATAC screen has no antigen,
   so no antigen filter can reach it.
2. **Its method vocabulary was ChIP-seq-only.** Its six GEO queries used `"chip seq" OR "chip-seq" OR
   chipseq`. ATAC-seq, CUT&RUN, CUT&Tag, DNase-seq, ChIP-exo and HiChIP were never asked for.
3. **The manuscript's literature screen asked the right question of the wrong field.** PMID 39048711
   *is* inside the retrieved corpus — this search re-found it in `epmc_01_fusion_x_methods` — but its
   **title and abstract say only ">100 oncofusions"**. The string `NR4A3` appears **26 times in the full
   text and zero times in the abstract**. A title/abstract screen for "applies a chromatin method to an
   NR4A3 chimera" cannot return it.
4. **GEO's own metadata repeats the problem.** GSE243553 carries
   `Series_type = Genome binding/occupancy profiling by high throughput sequencing` — the exact DataSet
   Type this search queried — and **`NR4A3` appears 0 times across all 24 of its sample records.** The
   fusion identities live in the per-cell barcode association files, not in the metadata. Measured:
   `gds_09_nr4a3_datasettype_genomebinding` returns 16 series and GSE243553 is not among them, because
   nothing NR4A3-shaped is indexed on it.

⭐ **The generalisable lesson:** for a pooled screen, the perturbation identity is data, not metadata.
No keyword query against any archive's index can find your gene inside one. The only routes in are the
paper's full text and the screen's own supplementary tables.

---

## 3 · What GSE243553 is, precisely

| field | value |
|---|---|
| accession | **GSE243553**, public 2024-07-24, last updated 2024-10-23 |
| title | Large-scale discovery of chromatin dysregulation induced by oncofusions and other protein-coding variants |
| primary publication | PubMed identifier 39048711 (*Nat Biotechnol* 2025); preprint doi `10.1101/2023.09.20.555752`, CC-BY-NC-ND |
| contributors | Frenkel M, Hujoel MLA, Morris Z, Raman S (University of Wisconsin–Madison) |
| assay | Spear-ATAC (10x droplet single-cell ATAC) on a pooled variant library, one perturbation per cell |
| cells | **HEK293T** — the authors' term is "disease-agnostic biosensor cell line" |
| scale | ~120,000 nuclei across 12 samples; the 12 are technical replicates of one library, not conditions |
| samples | GSM7790859–GSM7790882 (12 fragment files + 12 barcode→variant association files) |
| files | `*_fullfusion_fragments-N.tsv.gz` and `*_SampleN_merged_associations.csv.gz`, GEO FTP, no login |
| library | 116 unique sequences: >100 oncofusions, single domains, wild-type counterparts, empty vector |
| NR4A3 arms | EWSR1-NR4A3, TAF15-NR4A3, TCF12-NR4A3, TFG-NR4A3 |
| NR4A3 controls | full-length wild-type NR4A3; reciprocal NR4A3-EWSR1. (NR4A3-TAF15 failed synthesis) |
| code | `github.com/mfrenkel16/OncofusionPRODATAC` — 9 R files, including `ChipAtlas.R`, `GGAA_analysis.R`, `FF_ArchR.R`, `Motif.R` |

**What it can and cannot settle for this manuscript.**

- ✅ It is the first genome-wide chromatin readout that separates **an NR4A3 fusion** from
  **wild-type NR4A3**, with a null control (the reciprocal) that returned zero.
- ✅ Its NR4A-motif enrichment is a direct, independent cross-check on §3.10's NBRE scan — a sequence
  argument and a chromatin argument that were previously unable to meet.
- ⛔ It is **HEK293T**, so it reports what the fusion can do to a naive genome, not what it does in EMC
  chromatin. §3.2's finding that native NR4A3 fails to activate the promoter the fusion activates is
  reinforced by "wild-type NR4A3 changed 0 peaks", but neither is an EMC measurement.
- ⛔ It is **accessibility**, not binding. A peak opening near a gene is not the fusion sitting on it.
- ⛔ It is **sparse per arm**: 112 nuclei for EWSR1-NR4A3. That is the authors' own headline about
  sensitivity, not a hidden weakness, but it bounds any per-gene read hard.
- ⚠ **Nothing in it has been verified by this repository.** Every number in §1 is quoted from the paper.
  The barcode→variant association files have not been opened. **That is the next step and it is $0**
  (§7).

---

## 4 · The negative that survives, now properly bounded

Everything below is a **measured count from a named query on 2026-08-08**, not an assertion.

**No chromatin experiment of any kind has been deposited on EMC material.**

| question | query | result |
|---|---|---|
| GEO: an EMC disease term AND any chromatin method | `gds_04_disease_x_methods` | **0** |
| SRA: an EMC disease term, any library | `sra_01_disease_any` | 46 runs — **every one** RNA-Seq, WXS, WGS, Targeted-Capture or CAGE. **Zero chromatin strategies.** |
| SRA: chondrosarcoma AND `"atac seq"[Strategy]` | `sra_09` | **0** |
| BioSample: EMC disease term AND ChIP/ATAC/chromatin/CUT | `r4_biosample_disease_x_chromatin` | **0** |
| ArrayExpress: `"EWSR1::NR4A3"` | `r2_biostudies_all_fusion_cistrome` | **0** |
| ENA: study title `*chondrosarcoma*` (the single-word form — see §6) | `r2_ena_study_chondrosarcoma` | **64 studies. 4 are EMC** — PRJNA94685 (the 2005 array), PRJNA974549/PRJNA974550 (metastatic WGS), PRJNA1357027 (TempO-Seq) — **none chromatin.** The only chromatin-titled chondrosarcoma studies are PRJNA686877 and PRJNA802858 (HEY1-NCOA2) and PRJNA393452 (Gli1/Gli2). |
| PubMed: NR4A3 AND CUT&RUN/CUT&Tag | `r2_pubmed_03` | **0** |
| GEO / SRA: fusion names as strings | `gds_05`=6, `sra_03`=**0**, `r2_sra_04 EWSR1 AND NR4A3`=**0** | the 6 GEO records are **GSE11185/GDS3481**, the HEK293 tet-on EWS/NOR1 **expression array**, plus GSE118725 |

**No NR4A3-fusion ChIP has been performed under any label.** ChIP-Atlas's complete antigen index
(`antigenList.tab`, 7,567 antigen×genome rows, 10 genomes) was read and every FET-partner antigen
resolved to its cell line through ENA:

| antigen | ChIP-Atlas experiments (hg19/hg38) | cell lines, resolved |
|---|---|---|
| **NR4A3** | 6 | CD1c+ dendritic cells — **all six**, one study |
| **EWSR1** | 13 | HEK293, RWPE1, VCaP, K562, **JN-DSRCT-1 (EWSR1::WT1)**, **SU-CCS-1 and DTC1 (EWSR1::ATF1)** |
| **TAF15** | 13 | HepG2, U2OS, K562, HONE-1, HEK293 |
| TCF12 / FUS | 27 / 9 | — |
| HSPA8 | **absent as an antigen in every genome** | — |

**Not one is EMC, and not one is an NR4A3 fusion.** No epitope-tag antigen class exists in ChIP-Atlas
other than GFP, so a tagged-fusion ChIP hiding under `FLAG`/`HA` is excluded too.

⛔ **The one EMC-labelled cell line was interrogated by name, and its identity is disputed — both
facts belong in the record.** `gds_14_emc_cell_lines` asked GEO for `"H-EMC-SS" OR "HEMC SS" OR
"H EMC SS" OR MUG-Chor1` and got **53 records, of which exactly 3 name the line** (GSM1669877,
GSM959004, GSM827448) — **all three expression samples inside multi-line panels, none chromatin**;
the Europe PMC companion query `r2_epmc_emc_cellline_chromatin` returned 6 papers, none reporting a
chromatin assay on it. ⚠ **That zero is the weaker of two reasons this line could not have settled
the question.** H-EMC-SS / ACH-001519 / CVCL_1238 is registered here as `identity_disputed`
(`OBJ-LINE-HEMCSS`); the curated record holds that it does **not** carry an EWSR1 fusion
([`emc-surface-target-landscape.md`](./emc-surface-target-landscape.md) → Amendment 1). So a chromatin
dataset keyed to that line would have been *a chromatin dataset on a line whose fusion status the
curated record contradicts* — **not** an NR4A3-fusion chromatin experiment. The line is named here only
as a search term; no reading anywhere in this note or its corpus is taken off that model, and the use
is classified `unaffected` in
[`emc-systems-map.json`](./emc-systems-map.json) → `OBJ-LINE-HEMCSS.read_by` —
**interrogated as a search term only; returned no chromatin dataset**. The mention is deliberately
retained rather than deleted: a negative that hides which models it interrogated cannot be re-run.

⚠ **The bound this negative actually has, stated rather than glossed.** The searches above are
**metadata searches**, and §2 is the proof that metadata can hide the answer: GSE243553 was invisible
to every NR4A3-keyed query in this sweep and was found only through a paper's full text. Two specific
residues follow. **(a)** `gds_11_sarcoma_datasettype_genomebinding` returned **688** sarcoma series
with a genome-binding DataSet Type and they were **not** screened one by one; what excludes an EMC
deposit from them is that an EMC deposit would have to carry an EMC disease term, and the query that
asks exactly that (`gds_04`) returned 0. **(b)** A deposit carrying *neither* an EMC term *nor* NR4A3
in its metadata is precisely the GSE243553 case, and no index query can reach one. So the defensible
claim is **"nothing has been deposited on EMC material under any label an archive indexes"** — not
"no such data exists anywhere", which no search of this kind can establish.

⭐ **The sharpest form of the negative is comparative, and it is new.** The field has done this
experiment for the *sibling* fusions and not for this one:

- **EWSR1::WT1** — ChIP-seq in JN-DSRCT-1 (3 experiments).
- **EWSR1::ATF1** — ChIP-seq in SU-CCS-1 and DTC1 (4 experiments).
- **FUS::DDIT3 and EWSR1::FLI1** — ATAC-seq, **GSE235218** (PubMed identifier 40988026).
- **HEY1::NCOA2 mesenchymal chondrosarcoma** — ChIP-seq **twice**, mouse **GSE163585** and human
  **GSE196000**.
- Chondrosarcoma generally — Gli1/Gli2 ChIP-seq **GSE100936**; IDH-mutant **GSE270026**; IL-1 ATAC
  **GSE144303**.
- **EMC / any NR4A3 fusion, in native chromatin — nothing.**

So the honest sentence is not "nobody has looked". It is: **the experiment is routine in this exact
tumour family, has been done for at least five sibling fusions, and has never been done on EMC
material.**

---

## 5 · Two other things this search turned up

**(a) A previously unretrieved NR4A3 occupancy dataset: GSE254076.** "Effect of depletion of NR4A3 on
vascular calcification [**CUT&Tag_NR4A3**]", mouse vascular smooth muscle cells, public 2024-05-14;
sibling GSE254075 (H3K18la CUT&Tag), SuperSeries GSE254078. It is **wild-type mouse Nr4a3, not a
fusion, and not EMC** — but it is a genuine genome-wide NR4A3 occupancy dataset absent from
[§3.11's Table 9](./nr4a3-fusion-transcriptional-output.md) and from the 110 peak sets in
[`emc-ret-cistrome.json`](../modalities/emc-ret-cistrome.json). It was missed for reason 2 above: GEO
types it `Other`, and it is CUT&Tag, so neither the DataSet-Type filter nor a ChIP-seq keyword reaches
it. Adding it would extend the occupancy axis by one experiment in a new tissue.

**(b) A candidate fourth EMC expression cohort — RNA, not chromatin.** BioProject **PRJNA1357027** /
SRA study **SRP640302**, "Prognostic Biomarkers for Enhanced Risk Stratification in Extraskeletal
Myxoid Chondrosarcoma: A Retrospective…", **12 targeted RNA-seq (TempO-Seq) runs of EMC**. §3.13 of
PUB-FUSION-OUTPUT records that no fourth EMC cohort exists; that section's search was GEO-side, and
this deposit is registered in BioProject/SRA. It is **outside this note's scope and unverified** —
sample count, tumour-versus-normal design and data release status were not checked — but it is a live
lead for whoever owns §3.13. (Separately, GSE299349 carries EMC-labelled samples and SRA still reports
it as scheduled-release.)

---

## 6 · Retrieval integrity — what failed, and what that does and does not mean

179 fetches were issued across six rounds; **177 reached a server and 121 returned HTTP 200**. Failures are listed rather than folded into
the counts, because an absent reading is not a reading of absence.

| failure | count | disposition |
|---|---|---|
| NCBI **HTTP 429** (rate limit) | 25 | **All re-run in a later round until they answered.** No NCBI query is reported as zero on the strength of a 429. `gds_20_nr4a3_knockdown_chromatin` was retried in R6 and returned **108**; `gap_02` is moot because `db=gap` does not exist (row below). |
| ENCODE **HTTP 502** | 21 | **NOT RETRIEVED, not empty.** Sixteen distinct ENCODE URLs across five rounds and six URL shapes (`/search/`, `/report/`, `/summary/`, `/targets/`, with and without `frame=object`, `limit=all` and `limit=25`) — including a trivial `target.label=CTCF&limit=5` control — all returned `502 Bad Gateway`. ⚠ The gap is bounded rather than open: ENCODE deposits are mirrored into GEO and ingested by ChIP-Atlas, both of which were searched completely, and ChIP-Atlas's NR4A1/EWSR1/TAF15 experiment lists visibly contain ENCODE experiments (K562, HepG2). |
| Zenodo **HTTP 400** | 7 | Cause identified from the response body: `"Page size cannot be greater than 25"` unauthenticated. Re-run at `size=25` in R3 and answered. |
| Europe PMC `fullTextXML` **404** | 2 | PMC13105821 is `isOpenAccess: N`, so the XML endpoint is closed. Routed around: the PMC HTML rendering was fetched instead (133 KB) and is where §1's quotations come from. |
| `chip-atlas cellTypeList.tab` **404** | 1 | That file does not exist; `antigenList.tab` does and was read (7,567 rows). |
| bioRxiv full text **HTTP 429** | 1 | Routed around: the same content was read from the PMC HTML rendering. |
| ReMap `api/v1` ×2, CistromeDB `api/inspector` ×2 | 4 | ReMap **times out with no response at all** — those two are the only fetches of the 179 that produced no file, which is why 177 reached a server. CistromeDB returns HTTP **200 with the body `Request denied!`**, so it is counted among the 121 two-hundreds and is nonetheless a non-answer; it is listed here rather than in the counts for that reason. ⚠ Both are **reprocessing catalogues downstream of SRA/GEO**, which were searched directly, so neither can hold a deposit the primary archives lack. |
| `esearch db=gap` | 1 | `ERROR: Invalid db name specified: gap`. dbGaP is not queryable through esearch; it is reachable through BioProject, which was searched. |

**Known-positive controls, all green** — a zero from these archives is a real zero:
`ctrl_ncbi_gds_gse4303` = 44, `ctrl_ncbi_pubmed_subramanian` = 1 (PubMed identifier 15920699),
`ctrl_ncbi_sra_ctcf_chip` = 16,740, `ctrl_biostudies_arrayexpress_ctcf` = 397,
`ctrl_epmc_subramanian_pmid` = 1, `r2_ctrl_ncbi_bioproject_ewing` = 468.
⚠ **One control did NOT pass, and chasing it changed which ENA reading §4 is allowed to use.**
`ctrl_ena_ewing_sarcoma` (`study_title="*Ewing sarcoma*"`) returned **0**, which cannot be true — so
the three ENA *multi-word* title queries (`*Ewing sarcoma*`, `*myxoid chondrosarcoma*`,
`*chordoid sarcoma*`, all **0**) are **discarded as transport artifacts, not read as absences.** The
discriminating observation was free and was taken: the *single-word* form
`r2_ena_study_chondrosarcoma` (`study_title="*chondrosarcoma*"`) returned **64 studies**, so ENA's
wildcard title index works and it is the space that breaks it. §4 therefore quotes only the
single-word query, whose result is interpretable and which independently corroborates the negative
from a fourth archive. ENA also carried the *positive* direction throughout, resolving 32 ChIP-Atlas
accessions to their cell lines.

---

## 7 · What PUB-FUSION-OUTPUT should now write

**Replace the absence claim.** The sentence "no genome-wide chromatin experiment performed with an
NR4A3 fusion was retrieved in 2,276 documents across five corpora" is **false as of 2026-08-08** and
must not survive into a submission. The claim that replaces it, and which this search supports:

> A genome-wide chromatin experiment has been performed with an NR4A3 fusion, and it is not a cistrome.
> Frenkel *et al.* expressed EWSR1-NR4A3, TAF15-NR4A3, TCF12-NR4A3 and TFG-NR4A3 in HEK293T inside a
> pooled 116-member variant library and read chromatin accessibility by single-cell ATAC (GSE243553);
> they report ≈8,600 peaks opened by TAF15-NR4A3, enriched for the NR4A-family motif, against zero for
> full-length wild-type NR4A3 and zero for the reciprocal NR4A3-EWSR1. What is still missing for this
> paper's question is narrower and can now be stated exactly: **no experiment has measured where an
> NR4A3 fusion binds — or what chromatin does — in EMC material.** Across GEO, SRA, BioProject,
> BioSample, ArrayExpress/BioStudies and ChIP-Atlas, searched on 2026-08-08 by the queries in
> `lit-targets-nr4a3-cistrome.json`, an EMC disease term returns zero deposits with any chromatin
> library strategy, and ChIP-Atlas's complete antigen index carries NR4A3 in only one cell type
> (CD1c+ dendritic cells) and EWSR1 in seven, none of them EMC — while the same catalogues hold
> chromatin maps for EWSR1::WT1, EWSR1::ATF1, EWSR1::FLI1, FUS::DDIT3 and HEY1::NCOA2. This is a
> statement about what has been deposited under a label an archive indexes, not about what exists:
> the experiment reported above was itself invisible to every gene-keyed query and was reached only
> through a paper's full text.

**Three consequential edits follow.**

1. **§6's conclusion is now too strong and too weak at once.** "Until a fusion cistrome is in hand,
   'up in EMC' and 'driven by the fusion' cannot be told apart" — a fusion-versus-wild-type contrast
   now exists genome-wide. It is in the wrong cell type and the wrong channel, which the sentence should
   say, rather than asserting that nothing exists.
2. **§3.10 gains a cross-check it did not have.** The paper's own report that NR4A3-fusion-opened peaks
   are enriched for the NR4A-family motif is an independent, chromatin-side test of the NBRE argument,
   from a different instrument.
3. **§4.3's discriminating experiment survives and sharpens.** It is no longer "a fusion cistrome" in
   the abstract; it is *occupancy of an NR4A3 fusion in EMC chromatin* — and §4 above shows the field
   routinely performs exactly that experiment for neighbouring fusions.

**The $0 next step, named and not taken here.** GSE243553's twelve
`GSM77908xx_SampleN_merged_associations.csv.gz` files map each cell barcode to its variant. Downloading
them (GEO FTP, no login), confirming the four NR4A3 arms and their nuclei counts from the data rather
than from the paper's prose, and intersecting the accessibility calls with the class-A genes *ENO3*,
*PPARG* and *SEMA3C* would convert every quoted figure in §1 into a measured one — and would be the
first time any instrument in this repository has read an NR4A3 **fusion** rather than a surrogate.
⚠ Two guards on that read before anyone starts: the arms are sparse (112 nuclei for EWSR1-NR4A3), and
HEK293T accessibility is not EMC occupancy — the same background-panel calibration §3.11 applies to the
NR4A peak sets applies here, or the result will be the uncalibrated reading §1.3 exists to refuse.

---

## Appendix — every target, its round, its HTTP status and its count

Rounds: **R1** the 78-target sweep · **R2A** resolve IDs to records · **R2B** re-run R1's failures ·
**R3** resolve remainder and chase leads · **R4** test PMID 39048711 · **R5** characterise GSE243553 ·
**R6** final retries. `—` = not retrieved (see §6). Query strings: one home,
[`lit-targets-nr4a3-cistrome.json`](./lit-targets-nr4a3-cistrome.json), keyed by the same names.

| target | round | HTTP | count |
|---|---|---|---|
| `bioproject_01_disease_any` | R1 | 200 | 6 |
| `bioproject_02_nr4a3_x_methods` | R1 | 429 | — |
| `bioproject_03_fusion_names` | R1 | 429 | — |
| `biosample_01_disease_any` | R1 | 429 | — |
| `biosample_02_fusion_names` | R1 | 200 | 0 |
| `biostudies_ae_01_nr4a3` | R1 | 200 | 13 |
| `biostudies_ae_02_disease` | R1 | 200 | 104 |
| `biostudies_ae_03_ewsr1_nr4a3` | R1 | 200 | 25 |
| `biostudies_ae_04_chondrosarcoma_chip` | R1 | 200 | 14275 |
| `biostudies_all_01_fusion` | R1 | 200 | 41713 |
| `biostudies_all_02_disease_chromatin` | R1 | 200 | 43643 |
| `chipatlas_antigen_list` | R1 | 200 | None |
| `chipatlas_celltype_list` | R1 | 404 | — |
| `cistromedb_ewsr1` | R1 | 200 | None |
| `cistromedb_nr4a3` | R1 | 200 | None |
| `ctrl_biostudies_arrayexpress_ctcf` | R1 | 200 | 397 |
| `ctrl_ena_ewing_sarcoma` | R1 | 200 | 0 |
| `ctrl_encode_ctcf` | R1 | 502 | — |
| `ctrl_epmc_subramanian_pmid` | R1 | 200 | 1 |
| `ctrl_ncbi_bioproject_ewing` | R1 | 429 | — |
| `ctrl_ncbi_gds_gse4303` | R1 | 200 | 44 |
| `ctrl_ncbi_pubmed_subramanian` | R1 | 200 | 1 |
| `ctrl_ncbi_sra_ctcf_chip` | R1 | 200 | 16740 |
| `ctrl_zenodo_haller_nr4a3_deposit` | R1 | 400 | — |
| `ena_01_study_title_myxoid_chondrosarcoma` | R1 | 200 | 0 |
| `ena_02_study_title_nr4a3` | R1 | 200 | 40 |
| `ena_03_study_title_chordoid_sarcoma` | R1 | 200 | 0 |
| `encode_01_searchterm_nr4a3` | R1 | 502 | — |
| `encode_02_target_nr4a3` | R1 | 502 | — |
| `encode_03_target_ewsr1` | R1 | 502 | — |
| `encode_04_target_taf15` | R1 | 502 | — |
| `encode_05_searchterm_chondrosarcoma` | R1 | 502 | — |
| `encode_06_biosample_chondrosarcoma` | R1 | 502 | — |
| `encode_07_searchterm_sarcoma_experiments` | R1 | 502 | — |
| `epmc_01_fusion_x_methods` | R1 | 200 | 33 |
| `epmc_02_disease_x_methods` | R1 | 200 | 21 |
| `epmc_03_nr4a3_cistrome_anycontext` | R1 | 200 | 161 |
| `epmc_04_fusion_names_only` | R1 | 200 | 213 |
| `epmc_05_emc_open_chromatin` | R1 | 200 | 104 |
| `gap_01_disease_any` | R1 | 200 | ERROR:Invalid db name specified: gap |
| `gap_02_nr4a3` | R1 | 429 | — |
| `gds_01_nr4a3_any` | R1 | 200 | 309 |
| `gds_02_nr4a3_x_methods` | R1 | 200 | 35 |
| `gds_03_disease_any` | R1 | 200 | 20 |
| `gds_04_disease_x_methods` | R1 | 429 | — |
| `gds_05_fusion_names` | R1 | 429 | — |
| `gds_06_ewsr1_and_nr4a3` | R1 | 429 | — |
| `gds_07_taf15_and_nr4a3` | R1 | 429 | — |
| `gds_08_other_partners_and_nr4a3` | R1 | 429 | — |
| `gds_09_nr4a3_datasettype_genomebinding` | R1 | 200 | 16 |
| `gds_10_chondrosarcoma_datasettype_genomebinding` | R1 | 200 | 11 |
| `gds_11_sarcoma_datasettype_genomebinding` | R1 | 200 | 688 |
| `gds_12_nr4a3_and_sarcoma` | R1 | 429 | — |
| `gds_13_nr4a3_epitope_tagged` | R1 | 200 | 23 |
| `gds_14_emc_cell_lines` | R1 | 429 | — |
| `gds_15_nor1_tec_x_methods` | R1 | 200 | 116 |
| `gds_16_ewsr1_x_methods` | R1 | 429 | — |
| `gds_17_taf15_x_methods` | R1 | 429 | — |
| `gds_18_fet_fusion_cistromes` | R1 | 200 | 139 |
| `gds_19_chondrosarcoma_any` | R1 | 429 | — |
| `gds_20_nr4a3_knockdown_chromatin` | R1 | 429 | — |
| `pubmed_01_fusion_x_methods` | R1 | 429 | — |
| `pubmed_02_disease_x_methods` | R1 | 200 | 11 |
| `pubmed_03_nr4a3_cutrun_cuttag` | R1 | 429 | — |
| `sra_01_disease_any` | R1 | 200 | 46 |
| `sra_02_nr4a3_x_methods` | R1 | 200 | 145 |
| `sra_03_fusion_names` | R1 | 429 | — |
| `sra_04_ewsr1_and_nr4a3` | R1 | 429 | — |
| `sra_05_chondrosarcoma_chip_or_atac` | R1 | 200 | 109 |
| `sra_06_nr4a3_strategy_chipseq` | R1 | 200 | 24 |
| `sra_07_nr4a3_strategy_atacseq` | R1 | 429 | — |
| `sra_08_chondrosarcoma_strategy_chipseq` | R1 | 200 | 36 |
| `sra_09_chondrosarcoma_strategy_atacseq` | R1 | 200 | 0 |
| `zenodo_01_nr4a3_chip` | R1 | 400 | — |
| `zenodo_02_myxoid_chondrosarcoma` | R1 | 400 | — |
| `zenodo_03_ewsr1_nr4a3` | R1 | 400 | — |
| `r2_ena_chipatlas_EWSR1_experiments` | R2A | 200 | 13 |
| `r2_ena_chipatlas_NR4A3_experiments` | R2A | 200 | 10 |
| `r2_ena_chipatlas_TAF15_experiments` | R2A | 200 | 17 |
| `r2_encode_biosample_chondrosarcoma` | R2A | 502 | — |
| `r2_encode_searchterm_chondrosarcoma` | R2A | 502 | — |
| `r2_encode_target_ewsr1` | R2A | 502 | — |
| `r2_encode_target_nr4a3` | R2A | 502 | — |
| `r2_encode_target_taf15` | R2A | 502 | — |
| `r2_epmc_oncofusion_chromatin` | R2A | 200 | 1 |
| `r2_sum_bioproject_01_disease` | R2A | 200 | 6 |
| `r2_sum_gds_02_nr4a3_x_methods` | R2A | 200 | 35 |
| `r2_sum_gds_03_disease_any` | R2A | 200 | 20 |
| `r2_sum_gds_09_nr4a3_genomebinding` | R2A | 200 | 16 |
| `r2_sum_gds_10_chondrosarcoma_genomebinding` | R2A | 200 | 11 |
| `r2_sum_gds_13_nr4a3_epitope_tagged` | R2A | 200 | 23 |
| `r2_sum_sra_01_disease_any` | R2A | 200 | 46 |
| `r2_sum_sra_06_nr4a3_chipseq` | R2A | 200 | 24 |
| `r2_sum_sra_08_chondrosarcoma_chipseq` | R2A | 200 | 36 |
| `r2_zenodo_chondrosarcoma` | R2A | 400 | — |
| `r2_zenodo_nr4a3` | R2A | 400 | — |
| `r2_bioproject_02_nr4a3_x_methods` | R2B | 429 | — |
| `r2_bioproject_03_fusion_names` | R2B | 429 | — |
| `r2_biosample_01_disease_any` | R2B | 429 | — |
| `r2_biostudies_ae_atac` | R2B | 200 | 268 |
| `r2_biostudies_ae_emc` | R2B | 200 | 104 |
| `r2_biostudies_all_fusion_cistrome` | R2B | 200 | 0 |
| `r2_ctrl_ncbi_bioproject_ewing` | R2B | 200 | 468 |
| `r2_ena_study_chondrosarcoma` | R2B | 200 | 64 |
| `r2_encode_ctcf_control` | R2B | 502 | — |
| `r2_encode_searchterm_nr4a3` | R2B | 502 | — |
| `r2_epmc_emc_atac` | R2B | 200 | 5 |
| `r2_epmc_emc_cellline_chromatin` | R2B | 200 | 6 |
| `r2_epmc_emc_transcriptome_deposit` | R2B | 200 | 223 |
| `r2_gds_04_disease_x_methods` | R2B | 200 | 0 |
| `r2_gds_05_fusion_names` | R2B | 200 | 6 |
| `r2_gds_06_ewsr1_and_nr4a3` | R2B | 200 | 0 |
| `r2_gds_07_taf15_and_nr4a3` | R2B | 200 | 0 |
| `r2_gds_08_other_partners_and_nr4a3` | R2B | 200 | 1 |
| `r2_gds_12_nr4a3_and_sarcoma` | R2B | 200 | 13 |
| `r2_gds_14_emc_cell_lines` | R2B | 200 | 53 |
| `r2_gds_16_ewsr1_x_methods` | R2B | 200 | 126 |
| `r2_gds_17_taf15_x_methods` | R2B | 200 | 66 |
| `r2_gds_19_chondrosarcoma_any` | R2B | 200 | 872 |
| `r2_pubmed_01_fusion_x_methods` | R2B | 200 | 4 |
| `r2_pubmed_03_nr4a3_cutrun_cuttag` | R2B | 200 | 0 |
| `r2_sra_03_fusion_names` | R2B | 200 | 0 |
| `r2_sra_04_ewsr1_and_nr4a3` | R2B | 200 | 0 |
| `r2_sra_07_nr4a3_strategy_atacseq` | R2B | 200 | 55 |
| `r2_zenodo_ewsr1` | R2B | 400 | — |
| `r3_bioproject_02_nr4a3_x_methods` | R3 | 200 | 13 |
| `r3_bioproject_03_fusion_names` | R3 | 200 | 3 |
| `r3_biosample_01_disease_any` | R3 | 200 | 33 |
| `r3_biostudies_ae_cuttag` | R3 | 200 | 3983 |
| `r3_encode_v1_min` | R3 | 502 | — |
| `r3_encode_v2_target_page` | R3 | 502 | — |
| `r3_encode_v3_report` | R3 | 502 | — |
| `r3_epmc_39048711_core` | R3 | 200 | 1 |
| `r3_epmc_39048711_fulltext` | R3 | 404 | — |
| `r3_epmc_oncofusion_nr4a3_check` | R3 | 200 | 0 |
| `r3_geo_GSE254075_cuttag_h3k18la` | R3 | 200 | None |
| `r3_geo_GSE254076_cuttag_nr4a3` | R3 | 200 | None |
| `r3_geo_GSE254078_parent` | R3 | 200 | None |
| `r3_sum_gds_05_fusion_names` | R3 | 200 | 6 |
| `r3_sum_gds_12_nr4a3_and_sarcoma` | R3 | 200 | 13 |
| `r3_sum_gds_14_emc_cell_lines` | R3 | 200 | 53 |
| `r3_sum_gds_16_ewsr1_methods` | R3 | 200 | 88 |
| `r3_sum_gds_17_taf15_methods` | R3 | 200 | 28 |
| `r3_sum_sra_07_nr4a3_atac` | R3 | 200 | 55 |
| `r3_zenodo_chondrosarcoma` | R3 | 200 | 80 |
| `r3_zenodo_ewsr1_nr4a3` | R3 | 200 | 1 |
| `r3_zenodo_nr4a3` | R3 | 200 | 6 |
| `r4_biosample_disease_x_chromatin` | R4 | 200 | 0 |
| `r4_biostudies_prodatac` | R4 | 200 | 1 |
| `r4_encode_v4_report` | R4 | 502 | — |
| `r4_encode_v5_matrix` | R4 | 502 | — |
| `r4_epmc_fulltext_fusion_x_chromatin` | R4 | 200 | 3 |
| `r4_epmc_preprints_fusion_chromatin` | R4 | 200 | 0 |
| `r4_epmc_prodatac_all_versions` | R4 | 200 | 4 |
| `r4_epmc_prodatac_fulltext_xml` | R4 | 404 | — |
| `r4_epmc_prodatac_mentions_chondrosarcoma` | R4 | 200 | 0 |
| `r4_epmc_prodatac_mentions_ewsfli1` | R4 | 200 | 1 |
| `r4_epmc_prodatac_mentions_ewsr1` | R4 | 200 | 1 |
| `r4_epmc_prodatac_mentions_nr4a3` | R4 | 200 | 1 |
| `r4_gds_prodatac_deposit` | R4 | 200 | 9 |
| `r4_geo_GSE235218` | R4 | 200 | None |
| `r4_pmc_prodatac_html` | R4 | 200 | None |
| `r4_sum_bioproject_106887` | R4 | 200 | 1 |
| `r5_biorxiv_prodatac_details` | R5 | 200 | None |
| `r5_biorxiv_prodatac_fulltext` | R5 | 429 | — |
| `r5_epmc_preprint_PPR728373` | R5 | 200 | 1 |
| `r5_epmc_prodatac_cites_emc` | R5 | 200 | 1 |
| `r5_gds_gsm_naming_nr4a3_fusion` | R5 | 200 | 27 |
| `r5_geo_GSE243553_gsm_list` | R5 | 200 | None |
| `r5_geo_GSE243553_self` | R5 | 200 | None |
| `r5_github_prodatac_repo` | R5 | 200 | 9 |
| `r5_sra_gse243553` | R5 | 200 | 0 |
| `r5_sum_gds_prodatac_neighbours` | R5 | 200 | 9 |
| `r6_encode_v6_summary` | R6 | 502 | — |
| `r6_gds_18_fet_fusion_titles` | R6 | 200 | 10 |
| `r6_gds_20_nr4a3_knockdown_chromatin` | R6 | 200 | 108 |
| `r6_geo_GSE243553_suppl_list` | R6 | 200 | None |
