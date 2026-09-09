---
id: DOC-EPITOPE-BENCHMARK-VALIDATED-EPITOPE-TABLE
title: "Experimentally validated cancer gene-fusion JUNCTION epitopes reported in the published literature — auditable per-epitope table"
level: L4
kind: evidence-table
status: live
date: 2026-09-09
last_verified: 2026-09-09
---

# Validated cancer gene-fusion **junction** epitope table

Lane EPITOPE-BENCHMARK, campaign OPUS-CAPACITY-CAMPAIGN-20260908. Serves the blocked question shared
by **PUB-NEOANTIGEN** and **PUB-VACCINE-PATH**.

**Source route.** Every row was retrieved this session through the **PubMed / PMC MCP server**
(`search_articles`, `get_article_metadata`, `get_full_text_article`). According to PubMed. Direct
HTTP is proxy-refused (`CONNECT tunnel failed, response 403`, curl exit 56) for both
`eutils.ncbi.nlm.nih.gov` and `query-api.iedb.org` — preserved verbatim in
`checks/04-direct-http-refusal-probe/`. **No IEDB record was consulted; no IEDB claim is made.**

⛔ **Prediction is not validation.** A NetMHC/SYFPEITHI score, a "predicted strong binder", or an
"immunogenic candidate" is **not** an epitope. Rows graded `PREDICTION ONLY` and `BINDING ONLY` are
kept in the table so the exclusion is auditable, and are **counted separately and never added in**.
⛔ **Presentation is not efficacy.** Nothing here is a clinical claim about any patient or tumour.

## How to read the columns

* **Spans the junction?** — `YES` = the peptide crosses the fusion breakpoint; `NO` = it lies wholly
  within one partner protein (or elsewhere) and is retained only as a negative control;
  `STATED` = the source calls it a junction peptide but the retrieved text does not let me verify the
  register. This is the column PUB-NEOANTIGEN's finding turns on.
* **Evidence grade** — `MS elution` (identified in an HLA immunopeptidome by LC-MS/MS),
  `multimer` (tetramer/dextramer enumeration), `T-cell` (ELISpot/ICS/activation/cytotoxicity),
  `BINDING ONLY`, `PREDICTION ONLY`.
* **✓elig** marks the rows that pass the **benchmark-eligible** rule used for the count in §Counts:
  natural (non-heteroclitic) sequence, spans the junction, 8–11 residues, a **named class I
  allotype**, and **at least one** of MS elution / T-cell reactivity / multimer.

## Per-epitope table

| ID | Fusion | Junction peptide | Len | HLA restriction | **Spans the junction?** | Evidence grade | Assay / material | Source (PMID · DOI) |
|---|---|---|---|---|---|---|---|---|
| E01 **✓elig** | BCR::ABL1 (b3a2) | `SSKALQRPV` | 9 | HLA-A*02:01 | **YES** — BCR b3 ...ATGFKQSSK \| ABL a2 ALQRPVASD; peptide SSK\|ALQRPV crosses it | T-cell | HLA-A2.1 binding; primary CTL induced in vitro from PBL of healthy donors and CML patients; CTL lysed HLA-matched BCR-ABL+ leukaemic cells (implies natural processing); high CTL frequency in 5/21 CML patients · *human PBL + patient leukaemic cells* | PMID 9593785 · [DOI](https://doi.org/10.1172/JCI488) |
| E02 | BCR::ABL1 (b3a2) | `NOT RETRIEVED (HLA-A3/-A11/-B8 junction peptide(s) of prior authors)` | — | HLA-A3 / -A11 / -B8 | **YES** — described as junction peptides; exact sequences not captured in this session | T-cell | same study: elicited primary CTL that recognised HLA-matched BCR-ABL+ leukaemic cells · *human PBL* | PMID 9593785 · [DOI](https://doi.org/10.1172/JCI488) |
| E03 | BCR::ABL1 (b2a2 + b3a2) | `14 junction peptides tested; 6 bound (sequences NOT RETRIEVED)` | — | HLA-A3/A11, -B8, -B44 (moderate) | **YES** — NEGATIVE CONTROL for the field: only 6/14 junction peptides bound at all, and CTL lines were raised only against NON-junction p210 peptides | BINDING ONLY | binding to 8 class I allotypes; no junction-peptide CTL reported · *synthetic peptide / cell lines* | PMID 9295046 · [DOI](https://doi.org/10.1002/eji.1830270834) |
| E04 | ABL::BCR and BCR::ABL1 (reciprocal) | `panel, sequences NOT RETRIEVED` | — | HLA-A1/-A2/-A3/-A11/-B7/-B27/-B35 | **YES** — class I stabilisation only | BINDING ONLY | HLA class I stabilisation · *synthetic peptide* | PMID 10720136 · [DOI](https://doi.org/10.1038/sj.leu.2401703) |
| E05 | BCR::ABL1 alternative splice, out-of-frame ABL | `OOF-derived, sequences NOT RETRIEVED` | — | HLA-A2, HLA-A3 | **NO** — EXCLUDED from junction count: peptides arise from the out-of-frame C-terminal ABL reading frame, not from the fusion junction itself | T-cell | OOF-specific CD8 T cells in 4/4 patients; 1 case cytotoxic against autologous primary CML cells · *CML patient PBMC* | PMID 17545610 · [DOI](https://doi.org/10.1158/0008-5472.CAN-06-3737) |
| E06 | BCR::ABL1 (b3a2) | `b3a2 junction peptide, sequence NOT RETRIEVED` | — | HLA-DRB1*09:01 (class II) | **YES** — class II - outside a class I threshold benchmark | T-cell | CD4 Th1 clone established; TCR-stimulation-dependent DC licensing · *human CD4 clone* | PMID 27181332 · [DOI](https://doi.org/10.1038/cmi.2016.7) |
| E07 | BCR::ABL1 (b3a2 / b2a2) | `vaccine peptide mixture, sequences NOT RETRIEVED` | — | predominantly class II (CD4) | **YES** — GIMEMA CML0206/SI0207 phase II, n=109; CD4 peptide-specific response in 80% | T-cell | in vivo peptide vaccination; peptide-specific CD4 T-cell responses · *CML patients* | PMID 40333294 · [DOI](https://doi.org/10.3390/vaccines13040419) |
| E08 | DEK::NUP214 (DEK-CAN) | `DEK-CAN fusion peptide, sequence NOT RETRIEVED` | — | class II (CD4, HLA-restricted) | **YES** — class II CD4 CTL clone HO-1 | T-cell | peptide-specific, HLA-restricted cytotoxicity by a CD4+ CTL clone · *healthy-donor PBL clone* | PMID 9920842 |
| E09 **✓elig** | ETV6::RUNX1 (TEL-AML1) | `RIAECILGM` | 9 | HLA-A*02:01 | **YES** — ETV6-RUNX1 E5_3 fusion-region nonamer | MS elution + T-cell | 1998: HLA-A2.1 binding + primary CTL from healthy donors that lysed HLA-A2.1 tumour cells endogenously expressing the fusion; CTL cloned from one patient's marrow. 2025: detected by targeted FAIMS-PRM immunopeptidomics of ETV6-RUNX1\|E5_3-transduced JY cells with a stable-isotope synthetic standard (reduction/alkylation required for detection) · *human PBL / patient marrow (1998); ENGINEERED JY minigene-transduced line (2025)* | PMID 9664088; 41567246 · [DOI](https://doi.org/10.1172/JCI3126) |
| E10 **✓elig** | ETV6::RUNX1 (E5_3) | `MPIGRIAECIL` | 11 | HLA-B*07:02 (also bound B*08:01, B*35:01, B*53:01) | **YES** — same fusion region, longer register | MS elution | in vitro proteasome digestion of the fusion precursor + LC-MS/MS; in vitro HLA binding assay; detected in JY+ETV6-RUNX1\|E5_3 immunopeptidome · *ENGINEERED JY minigene-transduced line* | PMID 41567246 · [DOI](https://doi.org/10.1016/j.isci.2025.114512) |
| E11 **✓elig** | ETV6::RUNX1 (E5_3) | `MPIGRIAEC` | 9 | HLA-B*07:02 | **YES** — N-terminal register of E10 | MS elution | detected by targeted PRM in the JY+ETV6-RUNX1\|E5_3 immunopeptidome · *ENGINEERED JY minigene-transduced line* | PMID 41567246 · [DOI](https://doi.org/10.1016/j.isci.2025.114512) |
| E12 **✓elig** | ETV6::RUNX1 (E5_4) | `MPIGRIADA` | 9 | HLA-B*07:02 | **YES** — alternative ETV6-RUNX1 breakpoint version | MS elution | targeted MS detection across replicates with near-zero control background; no synthetic standard available (proteasome-digest material used) · *ENGINEERED JY minigene-transduced line* | PMID 41567246 · [DOI](https://doi.org/10.1016/j.isci.2025.114512) |
| E13 **✓elig** | CBFB::MYH11 | `REEMEVHEL` | 9 | HLA-B*40:01 (also bound B*44:02 in vitro) | **YES** — nonamer from the prevalent CBFB-MYH11 fusion protein | multimer + T-cell | immunogenic in HLA-B*40:01+ donors; high-avidity CD8 clones killed CBFB-MYH11+ B*40:01+ AML cell lines AND PRIMARY human AML in vitro; controlled AML in a patient-derived murine xenograft in vivo; TCRs transduced into CD8 T cells conferred antileukaemic activity. Authors conclude the neoantigen is naturally presented on AML blasts · *healthy-donor T cells; primary human AML blasts; PDX* | PMID 32831296 · [DOI](https://doi.org/10.1172/JCI137723) |
| E14 **✓elig** | MYB::NFIB (ACC_M9 Fusion 2) | `QFIDSSWYL` | 9 | HLA-A*02:01 | **YES** — length-specific: the 8-mer FIDSSWYL and the 10-mer LQFIDSSWYL did NOT stimulate, so reactivity tracks the exact junction register | multimer + T-cell | T2 stabilisation; IFN-g by patient T cells against DCs expressing the cloned fusion (endogenous processing); PD-1/CD40L/CD137 induction; QFIDSSWYL-dextramer+ CD8 expansion over 21 d · *ACC patient T cells + autologous PBMC/DC* | PMID 31011208 · [DOI](https://doi.org/10.1038/s41591-019-0434-2) |
| E15 **✓elig** | MYBL1::NFIB (ACC panel) | `MMYSPICLTQT` | 11 | HLA-A*02:01 | **YES** — partner assignment per Extended Data Fig. 4 grouping; per-peptide gene attribution partly redacted in the retrieved text | T-cell | T2 stabilisation; healthy-donor HD2 and HD3 T-cell IFN-g; DCs expressing the cloned fusion stimulated peptide-specific HD2 T cells while MYB-N-terminus DCs did not (endogenous processing) · *HEALTHY-DONOR T cells (no autologous patient material available)* | PMID 31011208 · [DOI](https://doi.org/10.1038/s41591-019-0434-2) |
| E16 **✓elig** | NFIB::MYB (reciprocal, ACC panel) | `SLASPLQPT` | 9 | HLA-A*02:01 | **YES** — as E15 | T-cell | T2 stabilisation; healthy-donor HD2 T-cell IFN-g; endogenous processing from the cloned fusion in DCs · *HEALTHY-DONOR T cells* | PMID 31011208 · [DOI](https://doi.org/10.1038/s41591-019-0434-2) |
| E17 | NFIB::MYB / MYB::NFIB (ACC panel) | `SLASPLQSWYL` | 11 | HLA-A*02:01 | **YES** — BINDING ONLY - bound HLA-A*02:01 but no T-cell reactivity is reported for it | BINDING ONLY | T2 stabilisation only · *T2 cells* | PMID 31011208 · [DOI](https://doi.org/10.1038/s41591-019-0434-2) |
| E18 **✓elig** | DEK::AFF2 | `DKESEEEVS` | 9 | HLA-C*04:01 and HLA-C*12:03 | **YES** — stated as the fusion-derived nonamer; an internal figure caption renders it 'DEKSEEEVS', a discrepancy that a re-check of the source figure should resolve | T-cell | stabilised C*04:01 and C*12:03 on transfected T2; IFN-g and CD137 on autologous patient CD8; response abolished by anti-MHC class I; SCC-9 cells transduced with DEK-AFF2 (vs DEK-N-terminus) triggered IFN-g and target-cell caspase-3 (endogenous processing); reactive TCR CDR3 clonotypes tracked in patient blood during tumour regression · *exceptional-responder HNSCC patient (MSK-HN1) T cells* | PMID 31011208 · [DOI](https://doi.org/10.1038/s41591-019-0434-2) |
| E19 **✓elig** | DNAJB1::PRKACA | `EIFDRYGEEV` | 10 | HLA-A*68:02 | **YES** — the junction supplies the C-terminal anchor: the wild-type counterpart EIFDRYGEEG ends in glycine and is predicted not to bind any allotype | MS elution + multimer + T-cell | eluted from the HLA class I immunopeptidome of DNAJB1-PRKACA-induced SMMC-7721/HepG2, spectrum validated against a synthetic peptide; aAPC priming gave tetramer+ polyfunctional CD8 T cells (IFN-g/TNF/CD107a) · *ENGINEERED Dox-inducible HCC lines; healthy-volunteer CD8* | PMID 36302754 · [DOI](https://doi.org/10.1038/s41467-022-33746-3) |
| E20 **✓elig** | DNAJB1::PRKACA | `IFDRYGEEV` | 9 | HLA-C*04:01 | **YES** — as E19; wild-type IFDRYGEEG does not bind | MS elution | eluted from the same engineered HCC immunopeptidomes, spectrum validated against a synthetic peptide; no separate T-cell priming reported · *ENGINEERED Dox-inducible HCC lines* | PMID 36302754 · [DOI](https://doi.org/10.1038/s41467-022-33746-3) |
| E21 **✓elig** | DNAJB1::PRKACA | `RYGEEVKEF` | 9 | HLA-A*24:02 | **YES** — 5 residues from DNAJB1 exon 1 + 4 from PRKACA exon 2 | multimer + T-cell | refolded HLA-A*24:02 monomer, aAPC priming to up to 15.7% tetramer+ CD8 (median 4.1%); polyfunctional; specific lysis up to 82.4%. NATURAL PROCESSING NOT VALIDATED - the authors state it was not detected by MS in the transduced lines · *healthy-volunteer CD8* | PMID 36302754 · [DOI](https://doi.org/10.1038/s41467-022-33746-3) |
| E22 | DNAJB1::PRKACA | `EEVKEFLAKA` | 10 | class I vaccine peptide | **YES** — NEGATIVE: included in the personalised vaccine; no T-cell response against it was observed in the vaccinated patient, and no MS evidence | PREDICTION ONLY | none positive · *FL-HCC01 patient* | PMID 36302754 · [DOI](https://doi.org/10.1038/s41467-022-33746-3) |
| E23 | DNAJB1::PRKACA | `EVKEFLAKAKEDFLKK` | 16 | HLA-DRB1*13:02 (class II) | **YES** — class II - outside a class I benchmark | MS elution | eluted from moDC class II immunopeptidome after loading with lysate of DNAJB1-PRKACA-expressing HLE; spectrum validated with an isotope-labelled synthetic peptide · *ENGINEERED HLE lysate -> healthy-volunteer moDC* | PMID 36302754 · [DOI](https://doi.org/10.1038/s41467-022-33746-3) |
| E24 | DNAJB1::PRKACA | `KREIFDRYGEEVKEFLAKAKED` | 22 | class II, binding core RYGEEVKEF (best NetMHCIIpan rank 0.74 on DPA1*01:03-DPB1*05:01) | **YES** — class II long peptide - outside a class I benchmark | MS elution + T-cell | identified with 12 shorter length variants by MS from peptide-LOADED moDCs; de novo priming of multifunctional CD4 T cells; in the vaccinated FL-HCC patient, IFN-g ELISpot rose from 1 to 872 spots and persisted at 770 spots 18 months on · *healthy volunteers; one vaccinated FL-HCC patient* | PMID 36302754 · [DOI](https://doi.org/10.1038/s41467-022-33746-3) |
| E25 **✓elig** | SS18::SSX (SYT-SSX) | `GYDQIMPKK` | 9 | HLA-A*24:02 | **YES** — SS393, the natural 'B peptide' spanning the SYT-SSX breakpoint | multimer + T-cell | HLA-A24/peptide tetramer detection of CTL precursors in synovial sarcoma patients; CTL induced from patient PBL lysed HLA-A24+ SYT-SSX+ synovial sarcoma cells in a class I-restricted manner · *synovial sarcoma patient PBL + patient-derived tumour lines* | PMID 12133991; 15240740; 12445740 · [DOI](https://doi.org/10.4049/jimmunol.169.3.1611) |
| E26 **✓elig** | SS18::SSX (SYT-SSX) | `PYGYDQIMPK` | 10 | HLA-A24 | **YES** — SS391; CTL were induced with an SS391+SS393 mixture, so its individual contribution is not separable | T-cell | as E25 (peptide mixture) · *synovial sarcoma patient PBL* | PMID 12133991 · [DOI](https://doi.org/10.4049/jimmunol.169.3.1611) |
| E27 | SS18::SSX (SYT-SSX) - ANCHOR-MODIFIED | `K9I heteroclitic variant of GYDQIMPKK (position-9 K->I)` | 9 | HLA-A*24:02 | **YES** — NOT A NATURAL SEQUENCE - an engineered anchor substitute; excluded from any count of naturally occurring junction epitopes | multimer + T-cell | enhanced A24 affinity; CTL inducible from 12/15 patients vs 7/15 with the native B peptide; cross-reactive tetramer staining · *synovial sarcoma patient PBL* | PMID 15240740 · [DOI](https://doi.org/10.4049/jimmunol.173.2.1436) |
| E28 | SS18::SSX (SSX region, NOT the junction) | `AWTHRLRER / AWTHRLRERK` | 9 | HLA-A24 | **NO** — NEGATIVE CONTROL: lies wholly within the SSX partner; illustrates why a source-protein filter over-counts | BINDING ONLY | designed on the A24 motif; tested alongside the junction peptides · *synthetic* | PMID 12133991 · [DOI](https://doi.org/10.4049/jimmunol.169.3.1611) |
| E29 | SS18::SSX | `2 breakpoint peptides, sequences NOT RETRIEVED (10-aa minimal epitope defined)` | 10 | HLA-B7 | **YES** — full text not in PMC; sequences not recoverable through this route | T-cell | specific HLA-B7 binding; CTL induced from normal-donor lymphocytes with autologous peptide-pulsed DC lysed human synovial sarcoma cells endogenously expressing the full-length fusion · *healthy-donor lymphocytes + human SS tumour cells* | PMID 11559563 |
| E30 | SS18::SSX | `1 breakpoint peptide, sequence NOT RETRIEVED` | — | HLA-B27 | **YES** — binding only | BINDING ONLY | specific HLA-B27 binding · *synthetic* | PMID 11559563 |
| E31 | EWSR1::ATF1 (clear cell sarcoma) | `1 breakpoint peptide, sequence NOT RETRIEVED` | — | HLA-B27 | **YES** — binding only; no T-cell data reported for the CCS peptide | BINDING ONLY | specific HLA-B27 binding · *synthetic* | PMID 11559563 |
| E32 | EWSR1::WT1 (DSRCT) | `1 breakpoint peptide, sequence NOT RETRIEVED (9-aa optimal epitope defined)` | 9 | HLA-A3 | **YES** — binding only; no T-cell data reported for the DSRCT peptide | BINDING ONLY | specific HLA-A3 binding · *synthetic* | PMID 11559563 |
| E33 | PML::RARA | `SGAGEAAIETQS` | 12 | NOT STATED (both CD8+ and CD4+ effectors involved) | **STATED** — described as a 12-mer PML-RARalpha (A) peptide; class I restriction never defined, length outside the 8-11mer class I window | T-cell | peptide-pulsed DC primed autologous PBL with significantly higher cytotoxicity against PEPTIDE-PULSED autologous macrophages (p<0.001); no killing of leukaemic cells shown · *normal-donor DC/PBL* | PMID 10746975 |
| E34 | TMPRSS2::ERG (type VI) | `'several high-affinity epitopes' within one chimeric amino-acid sequence; sequences NOT RETRIEVED` | — | HLA-A*02:01 | **YES** — chimeric amino-acid sequence spanning the breakpoint of the two fused gene products | T-cell | bound HLA-A*02:01 and were recognised by CD8 T cells after in vitro peptide-specific T-cell expansion; no demonstration of natural processing on tumour · *in vitro expanded human CD8* | PMID 28954787 · [DOI](https://doi.org/10.1158/1078-0432.CCR-17-0618) |
| E35 | ERG (not the junction) | `ERG295 and 2 other ERG-derived peptides` | — | HLA-A*02:01 | **NO** — NEGATIVE CONTROL: derived from ERG itself, not from the TMPRSS2::ERG breakpoint | multimer + T-cell | T2 stabilisation; immunogenic in HLA-A*02:01 transgenic mice; tetramer · *transgenic mice* | PMID 24149465 · [DOI](https://doi.org/10.1007/s00262-013-1482-y) |
| E36 | NPM1::ALK / ALK+ ALCL | `ALKa, ALKb` | — | HLA-A*02:01 | **NO** — NEGATIVE CONTROL: ALK-derived, not junction-derived | T-cell | IFN-g ELISpot in 7/7 A2+ ALK+ ALCL patients; CTL lines lysed ALK+ ALCL lines · *ALCL patient PBMC* | PMID 16114011 · [DOI](https://doi.org/10.1002/ijc.21410) |
| E37 | NUP98::NSD1 (E11_7) | `LGAGFGTAV` | 9 | HLA-C*03:04 | **YES** — PREDICTION ONLY, and flagged as the single GF-NEO in that screen with a high predicted cross-reactivity risk | PREDICTION ONLY | none · *in silico* | PMID 41567246 · [DOI](https://doi.org/10.1016/j.isci.2025.114512) |
| E38 | EWSR1::FLI1 / EWSR1::ERG / EWSR1::FEV / EWSR1::WT1 | `breakpoint peptide motifs (e.g. EWSR1 exon 7 SQQSSSYGQQ- fused to FLI1 NPSYDSVRRG / ERG NLPYEPPRRS / FEV NPVGDGLFKD / WT1 SEKPYQCDFK)` | — | none | **YES** — PREDICTION/CANDIDATE ONLY - a clinical-genomics breakpoint catalogue explicitly framed as identifying POTENTIAL immunogenic peptides; no immunological measurement | PREDICTION ONLY | none · *in silico over 182 EWS-fusion clinical samples* | PMID 36900411 · [DOI](https://doi.org/10.3390/cancers15051623) |
| E39 | BRD4::NUTM1 (NUT carcinoma) | `PRAME peptides SLLQHLIGL, RLDQLLRHV, YLHARLREL` | 9 | HLA-A*02:01 | **NO** — NEGATIVE CONTROL: targeted MS detected these in 4/4 NUT carcinoma samples, but they derive from PRAME, a cancer/testis antigen UPREGULATED by the fusion - not from the fusion junction. A source-protein or 'fusion-associated' rule admits these; a junction rule does not | MS elution + T-cell | targeted MS >0.01 fM; PRAME-TCR bispecific and TCR-T cytotoxicity · *NUT carcinoma cell lines/PDX/patient samples* | PMID 41644270 · [DOI](https://doi.org/10.1136/jitc-2025-013539) |
| E40 | BCR::ABL1 E255V (kinase-domain point mutation) | `ABL-E255V peptide` | — | HLA-A2 | **NO** — NEGATIVE CONTROL: a TKI-resistance point mutation inside ABL, not a fusion junction | T-cell | CD8 responses in HLA-A2 transgenic mice; TCRs isolated; naturally processed and presented · *transgenic mice / human CD8 TCR-transduced* | PMID 39931057 · [DOI](https://doi.org/10.3389/fimmu.2025.1518691) |

## Counts (derived by `tabulate_epitopes.py` → `validated-epitope-counts.json`)

| Stratum | n | Record IDs |
|---|---|---|
| All records catalogued | 40 | E01–E40 |
| Spans the junction (`YES`) | 33 | — |
| Does **not** span the junction (negative controls) | 6 | E05, E28, E35, E36, E39, E40 |
| PREDICTION ONLY — **excluded from every epitope count** | 3 | E22, E37, E38 |
| BINDING ONLY — **excluded from every epitope count** | 7 | E03, E04, E17, E28, E30, E31, E32 |
| Any immunological measurement (MS / T-cell / multimer) | 30 | — |
| …and spans the junction | 24 | — |
| …and a natural (non-anchor-modified) sequence | 23 | — |
| …but sequence **not retrievable** through this route | 6 | E02, E06, E07, E08, E29, E34 |
| …class II or outside the 8–11mer class I window | 2 | E23, E24 |
| **BENCHMARK-ELIGIBLE class I junction epitopes** | **15** | E01, E09–E16, E18–E21, E25, E26 |
| …of which have **MS-elution** evidence | **6** | E09, E10, E11, E12, E19, E20 |

**Distinct fusion oncoproteins represented in the 15: nine.** BCR::ABL1, CBFB::MYH11, DEK::AFF2,
DNAJB1::PRKACA, ETV6::RUNX1, MYB::NFIB, MYBL1::NFIB, NFIB::MYB, SS18::SSX.

**Per-allele depth of the 15** — the number available to calibrate any *allele-specific* cut:

| HLA | n | peptides |
|---|---|---|
| HLA-A\*02:01 | 5 | SSKALQRPV, RIAECILGM, QFIDSSWYL, MMYSPICLTQT, SLASPLQPT |
| HLA-B\*07:02 | 3 | MPIGRIAECIL, MPIGRIAEC, MPIGRIADA |
| HLA-A\*24:02 | 2 | RYGEEVKEF, GYDQIMPKK |
| HLA-C\*04:01 | 2 | DKESEEEVS, IFDRYGEEV |
| HLA-A\*68:02 | 1 | EIFDRYGEEV |
| HLA-B\*40:01 | 1 | REEMEVHEL |
| HLA-C\*12:03 | 1 | DKESEEEVS |

## Quantitative observations that bear directly on the inclusion rule

| # | Observation | Value | Source |
|---|---|---|---|
| Q1 | Within one fusion protein, only a minority of its MS-identified ligands actually **span** the junction | DNAJB1-PRKACA: **2 of 20** class I ligands span (10%); **1 of 13** class II peptides span (7.7%) | PMID 36302754 · [DOI](https://doi.org/10.1038/s41467-022-33746-3) |
| Q2 | A junction can **create** the HLA anchor, so a junction epitope need not have a wild-type analogue | WT counterparts EIFDRYGEE**G** / IFDRYGEE**G** end in glycine and are predicted not to bind any allotype | PMID 36302754 · [DOI](https://doi.org/10.1038/s41467-022-33746-3) |
| Q3 | Junction reactivity can be specific to a **single length register** | 9-mer `QFIDSSWYL` stimulated; 8-mer `FIDSSWYL` and 10-mer `LQFIDSSWYL` did not | PMID 31011208 · [DOI](https://doi.org/10.1038/s41591-019-0434-2) |
| Q4 | The one recent MS success used **engineered overexpression**, and earlier attempts had failed | "early efforts to demonstrate neoantigen presentation of the recurrent GF ETV6-RUNX1 were unsuccessful"; the 2025 validation is in JY cells transduced with an ETV6-RUNX1 minigene | PMID 41567246 · [DOI](https://doi.org/10.1016/j.isci.2025.114512) |
| Q5 | Junction peptides of the best-studied fusion bind class I **poorly** | Of 162 p210 peptides screened, only **6 of 14** junction peptides bound any of 8 allotypes, and only moderately; 48 **non**-junction peptides bound intermediate/strong, and CTL lines arose only against non-junction peptides | PMID 9295046 · [DOI](https://doi.org/10.1002/eji.1830270834) |
| Q6 | A clinical vaccine against a validated junction epitope produced no robust response | SYT-SSX breakpoint phase II (n=21): DTH negative in all patients; independent evaluation — "No robust evidence of immune response to the target epitope was detected." | PMID 22726592 · [DOI](https://doi.org/10.1111/j.1349-7006.2012.02370.x); PMID 23252384 · [DOI](https://doi.org/10.1586/erv.12.122) |
| Q7 | Class I junction vaccination can fail while the class II response succeeds | Vaccinated FL-HCC patient mounted **no CD8** response to any of the three class I peptides; the durable response was CD4 | PMID 36302754 · [DOI](https://doi.org/10.1038/s41467-022-33746-3) |

## Known incompleteness of this table — stated, not glossed

1. **`EWSR1::FLI1` has no validated junction epitope in this table.** PUB-VACCINE-PATH reports the
   lane manuscript naming "four *EWSR1*::*FLI1* peptides". Nine PubMed queries aimed at it returned
   either nothing or purely computational work (PMID 36900411 is a breakpoint-motif catalogue that
   explicitly produces *candidates*). **I could not confirm an experimental validation through this
   route.** That is an unresolved discrepancy with the manuscript's §B1, not a refutation of it — the
   citation may be to a source PubMed's automatic term mapping did not surface for my queries.
2. **Six measured junction epitopes have unrecoverable sequences** (E02, E06, E07, E08, E29, E34).
   Worley 2001 is not in PMC; the BCR-ABL HLA-A3/-A11/-B8 peptides and the TMPRSS2::ERG type-VI
   epitopes are named but not spelled out in the retrieved records. Adding all of them would move the
   class I count from 15 to at most ~20 — it does not change any conclusion below.
3. **PMC full text strips some gene symbols**, so per-peptide partner attribution for the three
   adenoid-cystic peptides (E15, E16, E17) is stated as the source group, not asserted per gene.
4. **Recall is bounded by NCBI automatic term mapping.** 26 queries were issued; 12 returned zero
   because the mapper conjoins every token with `AND`. Recall was rebuilt with short queries and
   reference-chaining, but a systematic review with hand-curated MeSH would find more. The count
   below is therefore a **lower bound** — which is the safe direction for the conclusion it supports.
5. **No IEDB.** The 988-record cache PUB-NEOANTIGEN audited was not re-queried and IEDB is
   unreachable here. Nothing in this table is offered as a statement about IEDB's contents.
