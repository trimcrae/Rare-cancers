---
id: DOC-ASO-CITATIONS-PRIORART-2026-08-08
title: "Citations and prior art for the fusion-junction ASO manuscript — what was retrieved, what was refuted, and what is left"
level: L3
kind: memo
status: live
canonical_for: [aso-paper-citation-retrieval, aso-paper-prior-art]
purpose: >
  Close the fusion-junction ASO manuscript's citation gap with retrieved sources rather than
  recollection, run the prior-art search the manuscript never had, and record two findings that
  change what the manuscript may claim.
scope: >
  Covers research/manuscripts/aso/fusion-junction-aso-working-record.md only. Does not touch the degrader paper,
  the partner-stratification paper, the surface-antigen files or the citation-provenance ledger.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-08
last_verified: 2026-08-08
---

# Citations and prior art for the fusion-junction ASO manuscript

**One-line summary.** All eight of the manuscript's `[citation to verify]` items are now closed —
six with retrieved, quoted primary sources, two as evidence-backed absences — and the prior-art
search turns up a **35-year, clinically-tested lineage of junction-directed oligonucleotides against
fusion oncogenes**, which does not sink the paper but does relocate its novelty from the *method* to
the *indication*.

Every identifier in this note was returned by a Europe PMC search executed on a GitHub runner on
2026-08-08 and is quoted from that returned record. Nothing here was typed from memory. The machine
record — queries, run IDs, verbatim abstracts, the known-positive control — is
[`lit-targets-aso-verify.json`](./lit-targets-aso-verify.json), which is also the anchor
[`lint_citations.py`](../lint_citations.py) checks the manuscript against.

**How it was fetched.** `.github/workflows/fetch-literature.yml`, `query` path, dispatched at
`ref=claude/paper-paths-emc-treatment-ad72sg`. Six corpora, published to the `literature-cache`
branch under `literature/<slug>/`. Each query carried `EXT_ID:29370992` as a **known-positive
control** and `expect_pmids=29370992`, because `scripts/fetch-paper.mjs sync` exits 0 whether Europe
PMC returned 400 records or none — a wired-up search that matches nothing is still a green run with
no retrieval behind it. All six runs passed the control. The cost of the control is one irrelevant
record per corpus, declared in the JSON so nobody mistakes it for a citation.

⚠ **The publish step lost seven races before every corpus was through.** `fetch-literature.yml`'s corpus publish does a
bare `git push origin literature-cache` with **no retry**, and several sibling sessions were pushing
to that branch every one to two minutes. Seven of my runs completed a real retrieval — hundreds of
full texts fetched each time — and then died on `! [rejected] (fetch first)`, discarding it. The lane-probe
step in the same file already carries the three-attempt `push / fetch / rebase` loop that fixes this;
the corpus step does not. Each loss cost a re-dispatch. Recorded, not fixed — that file belongs to no
one session and four are running against it right now.

---

## Part 1 — the eight `[citation to verify]` items

### (a) ⛔ Quantitative RNase-H1 tolerance of a single **gap-internal** mismatch — RESOLVED, AND IT REFUTES THE HEURISTIC IT WAS ASKED TO SUPPORT

This is the load-bearing one: §3a-quater's "2 of 5 gapmers predicted off-target-clean" is produced by
scoring every near-match whose mismatch falls inside the DNA gap as **zero predicted-cleavable**, on
a stated-conservative "gap mismatch ⇒ no cleavage" heuristic. The manuscript flags that the
heuristic is unsourced. It is now sourced, and the number is not zero.

> **Østergaard ME, Southwell AL, Kordasiewicz H, Watt AT, Skotte NH, Doty CN, Vaid K, Villanueva EB,
> Swayze EE, Bennett CF, Hayden MR, Seth PP.** *Rational design of antisense oligonucleotides
> targeting single nucleotide polymorphisms for potent and allele selective suppression of mutant
> Huntingtin in the CNS.* 2013. **PMID: 23963702 · PMC3834808 · doi:10.1093/nar/gkt725**
>
> Verbatim: *"ASOs have been previously shown to discriminate single nucleotide changes in targeted
> RNAs with **∼5-fold selectivity**. Based on RNase H enzymology, we enhanced single nucleotide
> discrimination by positional incorporation of chemical modifications within the oligonucleotide to
> limit RNase H cleavage of the non-targeted transcript. The resulting oligonucleotides demonstrate
> **>100-fold discrimination** for a single nucleotide change at an SNP site…"*

**Read that against the heuristic.** A single mismatch inside the catalytic window of an
*unmodified* RNase-H-active gapmer buys about **5-fold**, not abolition. >100-fold exists but is
**engineered** — it requires deliberately placed chemical modifications whose purpose is to suppress
cleavage of the mismatched strand. The manuscript's designs carry no such modification. So
"gap-disrupted ⇒ 0 predicted-cleavable" is not conservative; it is **optimistic by roughly the factor
that matters**, and the oligo with 21 gap-disrupted near-matches is not thereby clean.

Six further retrieved sources agree, from four independent directions:

| source | what it shows |
|---|---|
| **PMID: 28624195 · PMC5363678 · doi:10.1016/j.omtn.2017.02.001** — Østergaard et al., fluorinated gap modifications | *"Certain mismatches, however, allow ASOs to bind at physiological conditions and result in RNA cleavage mediated by RNase H."* Cleavage through a mismatch is the expected case, not the exception. |
| **PMID: 28970564 · PMC5624880 · doi:10.1038/s41598-017-12844-z** — Magner et al., mismatched and bulged nucleotides in gapmer heteroduplexes | *"Among the over 120 gapmers tested, we found two gapmers that caused preferential degradation of the mutant allele APP 692 G and one that led to preferential cleavage of the mutant SNCA 53 A allele, both in vitro and in cells."* Roughly **3 of 120** achieved discrimination that survived into cells. Selectivity is mismatch-type- and position-dependent and mostly absent. |
| **PMID: 38993932 · PMC11238192 · doi:10.1016/j.omtn.2024.102237** — Aguti et al. | *"Initial gapmer ASO design exhibited high efficiency but **poor specificity** for the mutant allele."* A plain gapmer against a single-base difference discriminates badly; 10-fold needed a deliberately introduced extra mismatch. |
| **PMID: 42327837 · PMC13276142 · doi:10.1016/j.omtn.2026.102937** — Anwar et al., ACVR1 R206H | A 2′-O-methyl is placed at **gap position 2** specifically *"to synergize with the wild-type sequence mismatch to restrict RNase H1 cleavage."* The state of the art spends a chemical modification to buy what the manuscript's heuristic assumes for free. |
| **PMID: 7567450 · PMC307218 · doi:10.1093/nar/23.17.3411** — Duroux et al., mutant Ha-*ras* codon 12 | *"Short oligonucleotides (12- or 13mers) centered on the mutation had a very high discriminatory efficiency. **Longer oligonucleotides (16mers) did not discriminate efficiently.**"* ⚠ The manuscript's gapmers are **16-mers**. This is the one retrieved result that speaks directly to its geometry, and it speaks against it. |
| **PMID: 7731809 · PMC306791 · doi:10.1093/nar/23.6.954** — Giles et al. | Single-base discrimination in cells was obtained with chimeric methylphosphonodiester/phosphodiester backbones, *"whereas neither the phosphodiester nor phosphorothioate compounds were as stringent."* Discrimination is a property of the chemistry, not of the mismatch. |

Also retrieved and relevant to the same section: **PMID: 26544037 · PMC4704561 ·
doi:10.1371/journal.pone.0142139** (a second, blocking oligonucleotide against the wild-type allele
buys 1.5–15× — the tandem approach), **PMID: 32092825 · PMC7033438 · doi:10.1016/j.omtn.2020.01.012**
and **PMID: 35085461 · doi:10.1089/nat.2021.0009** (allele-selective gapmer campaigns in practice),
and three on measured gapmer off-target behaviour: **PMID: 29790953 · doi:10.1093/nar/gky397**,
**PMID: 31637814 · doi:10.1111/gtc.12730**, **PMID: 36276652 · doi:10.7150/thno.77830**.

**What is still not sourced.** No retrieved paper reports a tolerance figure for the manuscript's
*specific* geometry — a 6-nt DNA gap flanked by 5-nt LNA wings. The ~5-fold figure is the field's
general value for an unmodified RNase-H-active ASO and must be cited as that.

**Consequence for the manuscript (not applied here — outside this task's file scope).** §3a-quater's
"2 of 5 clean" and the abstract's specificity framing rest on a heuristic that the primary literature
now quantifies at ~5-fold. The honest restatement is *"a gap-internal mismatch is expected to reduce
cleavage roughly five-fold, not abolish it, so these counts are a ranking rather than a clean/dirty
call."* That is a real weakening and it should be made before the paper goes anywhere.

### (b) ✅ Rank-order of recurrent EMC exon junctions — RESOLVED, with numbers, from the primary literature

The manuscript states this item has *"no in-repo support at all"* since the exon-index retraction. It
now has out-of-repo support, and it is exactly the rank order the paper assumed.

> **Panagopoulos I, Mertens F, Isaksson M, Domanski HA, Brosjö O, Heim S, Bjerkehagen B, Sciot R,
> Dal Cin P, Fletcher JA, Fletcher CD, Mandahl N.** *Molecular genetic characterization of the
> EWS/CHN and RBP56/CHN fusion genes in extraskeletal myxoid chondrosarcoma.* 2002.
> **PMID: 12378528 · doi:10.1002/gcc.10127**
>
> Verbatim: *"…18 EMCs were studied both cytogenetically and at the molecular level… Fifteen cases
> had an EWS/CHN fusion transcript and three had an RBP56/CHN transcript. **The most frequent
> EWS/CHN transcript (type 1; 10 tumors), involved fusion of EWS exon 12 with CHN exon 3, and the
> second most common (type 5; two cases) was fusion of EWS exon 13 with CHN exon 3.** In all tumors
> with RBP56/CHN fusion, exon 6 of RBP56 was fused to exon 3 of CHN. … In CHN, 12 breakpoints were
> found in intron 2 and only two in intron 1. In EWS, the breaks occurred in introns 7 (one break),
> 12 (eight breaks), and 13 (one break), and in RBP56 in intron 6."*

(`CHN` = `TEC` = `NR4A3`; `RBP56` = `TAF2N` = `TAF15`.)

Independent corroboration, retrieved in the same sweep:

- **PMID: 11679947 · doi:10.1053/hupa.2001.28226** — Okamoto et al., 18 EMCs: *"EWS-CHN type 1 in 11
  cases, EWS-CHN type 2 in 1, and TAF2N-CHN in 3."*
- **PMID: 8634690 · doi:10.1093/hmg/4.12.2219** — Labelle et al. 1995, the discovery paper: *"This
  fusion transcript was detected in six of eight EMC studied, and **three different junction types**
  between the two genes were found. In all junction types, the putative translation product contained
  the amino-terminal transactivation domain of EWS linked to **the entire TEC protein**."*
- **PMID: 9060841 · PMC1857890** — Brody et al. 1997, an independent EWS/CHN series.
- Variant 5′ partners: **PMID: 10537274** (TAF2N exon 6 → *"the entire coding region of TEC"*),
  **PMID: 11156374** (TCF12 → *"the entire TEC protein"*), **PMID: 12598313 · PMC1868116 ·
  doi:10.1016/s0002-9440(10)63875-8** (EWS-TEC 5, TAF2N-TEC 4, TCF12-TEC 1 of 10),
  **PMID: 34124809 · doi:10.1002/gcc.22976** (SMARCA2 exon 3 → NR4A3 exon 3),
  **PMID: 41315062 · doi:10.1007/s00428-025-04352-7** (an EMC driven by HSPA8::**NR4A2**, not NR4A3).

⭐ **This independently vindicates the 2026-08-06 exon-index retraction, and it is worth stating
plainly.** Panagopoulos maps 12 of 14 genomic breaks to **CHN intron 2**, and Labelle, Sjögren ×2 all
describe the product as containing the **entire** TEC/NR4A3 protein. NR4A3 therefore resumes at
residue 1, which is `fusion-object-inventory.json`'s corrected
`nr4a3_resume_range_across_plausible_breakpoints` of **[1, 1]** — and is flatly incompatible with the
retracted panels' residue 361. The primary literature says the same thing the corrected index says.
The defect was real, the correction is right, and it is now checkable from outside the repository.

### (c) ⛔ B7-H3 (CD276) in EMC — CLOSED AS AN EVIDENCE-BACKED ABSENCE

754-record EMC corpus whose query **named** `B7-H3` and `CD276` as OR terms: **zero** records with
either in title or abstract. Full-text grep over the 449 open-access bodies finds four mentioning
B7-H3/CD276; the two that also contain "extraskeletal myxoid" are a pediatric precision-oncology
review (PMC10196192) and a congress abstract book (PMC9379246), and in neither is the B7-H3 text
about EMC. **No EMC-specific B7-H3 study exists that this query can see.** Quote the query, never the
bare zero. This is concordant with §3c, which already calls B7-H3 an extrapolation.

### (d) ◐ EMC line papers — identifiers RESOLVED; the data question answered for one, PAYWALLED for the other

- **Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, Pauli C.** *Establishment,
  characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma
  (EMC) cell models.* 2023. **PMID: 36316541 · PMC9813045 · doi:10.1007/s13577-022-00818-x** — open
  access, full text retrieved. Verbatim: *"The cells were molecularly characterized using **DNA
  sequencing and methylation profiling**."* The full text contains **zero** occurrences of
  `immunohisto`, no RNA-seq, and no GEO/SRA accession. It also records that the sole
  earlier EMC line, established in 1992, has no available molecular profile and no functional testing
  (that line is named in the paper but omitted here: its identity is flagged DISPUTED in this repository's cell-line model). The models are named
  **USZ20-EMC1** (EWSR1-NR4A3) and **USZ22-EMC2** (TAF15-NR4A3). ⇒ **No immunophenotype, no deposited
  transcriptome.** The §3c "decisive upgrade" is not sitting behind a request for this paper; it does
  not exist in it.
- **Iwata S, Noguchi R, Osaki J, Adachi Y, Shiota Y, Osaki S, Nishino S, Yoshida A, Ohtori S, Kawai
  A, Kondo T.** *Establishment and characterization of NCC-EMC1-C1: a novel patient-derived cell line
  of extraskeletal myxoid chondrosarcoma.* 2025. **PMID: 40580361 · doi:10.1007/s13577-025-01250-7**
  — **NOT open access. PAYWALLED, named as such.** Abstract only: drug screening of 221 agents
  (brigatinib, panobinostat, romidepsin); no immunophenotype, no accession. The item stays open **for
  this paper by name**, which is a better state than an unattributed `[citation to verify]`.

### (e) ⛔ EMC-specific surface expression of the surfaceome shortlist (CDH11, FGFR1, GPC2, PTK7, MCAM/CD146) — NOT A MISSING CITATION, A MISSING STUDY

Same corpus, and the query named CDH11, GPC2, PTK7, MCAM and CD146. No EMC record reports surface
expression of any of them in EMC. There is no citation to supply. The shortlist stays surrogate-derived,
which is what §3c already says.

### (f) ✅ Non-EWSR1/FET recurrent-fusion cancers as platform extensions — RESOLVED, and far better than "per indication [citation to verify]"

The prior-art search returns junction-directed oligonucleotide work in, at minimum: **CML
(BCR-ABL)**, **APL (PML-RARα)**, **AML t(8;21) (AML1-MTG8 / RUNX1::RUNX1T1)**, **prostate
(TMPRSS2/ERG)**, **glioblastoma and bladder (FGFR3-TACC3)**, **NUT carcinoma (BRD4-NUTM1)**,
**fibrolamellar HCC (DNAJB1::PRKACA)**, **Ewing sarcoma (EWS-FLI1)**, **alveolar rhabdomyosarcoma
(PAX3-FOXO1)** and **synovial sarcoma (SS18-SSX1)**. Identifiers in Part 2.

### (g)/(h) The two "verified" entries that carried no identifier and no use

`Fpocket` and `AlphaFold DB` are marked in the manuscript as *"not used in this analysis"*. Both now
have identifiers (below) so that a reader can check them, but a reference used by nothing should be
cut from an RNA-level paper, not decorated.

### The nine "verified" entries — every one now carries a retrieved identifier

| manuscript entry | retrieved identifier | note |
|---|---|---|
| Sjögren H, *EWSR1/NR4A3 fusion in EMC* (EMC-defining fusion) | ⚠ **misattributed** — see below | |
| — the EMC-defining fusion | **PMID: 8634690 · doi:10.1093/hmg/4.12.2219** (Labelle Y, Zucman J, Stenman G, Kindblom LG, *et al.*, 1995) | Stenman is a co-author; **Sjögren is not**. The Sjögren papers are the *variant-partner* papers below. |
| — Sjögren, variant partners | **PMID: 10537274** (TAF2N::TEC, 1999) · **PMID: 11156374** (TCF12::TEC, 2000) · **PMID: 12598313 · PMC1868116** (2003) | |
| Panagopoulos I, *fusion variants and partners* | **PMID: 12378528 · doi:10.1002/gcc.10127** | also the source for item (b) |
| Crooke ST *et al.*, *Antisense technology: an overview and prospectus* | **PMID: 33762737 · doi:10.1038/s41573-021-00162-z** | DOI in the manuscript was correct; PMID added |
| Bangerter, USZ-EMC | **PMID: 36316541 · PMC9813045 · doi:10.1007/s13577-022-00818-x** | |
| Iwata S, NCC-EMC | **PMID: 40580361 · doi:10.1007/s13577-025-01250-7** | paywalled |
| Mullican SE *et al.*, Nr4a3/Nr4a1 → AML | **PMID: 17515897 · doi:10.1038/nm1579** | true title is *"Abrogation of **nuclear receptors** Nr4a3 and Nr4a1 leads to **development of** acute myeloid leukemia"* |
| Safe S, Karki K | **PMID: 33106376 · PMC7864866 · doi:10.1158/1541-7786.mcr-20-0707** | |
| Le Guilloux V, Schmidtke P, Tufféry P, *Fpocket* | **PMID: 19486540 · PMC2700099 · doi:10.1186/1471-2105-10-168** | unused by this paper |
| Varadi M *et al.*, *AlphaFold Protein Structure Database* | **PMID: 34791371 · PMC8728224 · doi:10.1093/nar/gkab1061** | unused by this paper |

⚠ **The one correction the retrieval forced.** The manuscript's first reference credits Sjögren with
the EMC-defining fusion. The discovery paper is **Labelle et al. 1995**; Sjögren's EMC papers
(1999/2000/2003) report the *variant* 5′ partners. Both groups are Stenman's, which is very likely how
the two got merged. This is a mis-citation of the kind an identifier-free reference list cannot
surface — the entry had no PMID, so nothing could check it.

---

## Part 2 — prior art: junction-directed oligonucleotides against fusion oncogenes

Two corpora, 5,385 rows (5,153 unique records), filtered to those whose title or abstract carries **both** an
oligonucleotide modality **and** a junction/breakpoint targeting term. This is the section the
manuscript does not have, and it is the section a reviewer will open first.

### The lineage is 35 years old, continuous, and has reached the clinic

**1990s — the idea and the mechanism, already stated.**

- **PMID: 1794439** — Skórski T, Szczylik C, Malaguarnera L, Calabretta B, 1991. *"The 18-mer
  antisense directed against the specific BCR/ABL mRNA breakpoint region diminished the colony
  formation by CML-CP and CML-BC cells, but not by NBMC. Scrambled oligomer did not affect
  significantly the growth of leukemic and normal cells."* — a junction-directed antisense oligo,
  with a scrambled control and demonstrated sparing of normal cells. That is the manuscript's §4
  experiment, run in 1991.
- **PMID: 9049825 · doi:10.1023/a:1005716926800** — Toretsky JA, Connell Y, Neckers L, Bhat NK,
  1997. **The closest mechanistic precedent found.** *"We have evaluated a series of antisense ODN
  directed toward the **breakpoint region**… **Exogenously added RNase H was found to be required
  for translation inhibition.**"* Antisense at a *sarcoma* fusion breakpoint, discriminating by
  base-pairing, cleaving by RNase H — every element of this manuscript's mechanism, 29 years earlier.
- **PMID: 7566963** (Ouchida 1995), **PMID: 9005992 · PMC507791 · doi:10.1172/jci119152** (Tanaka
  1997) — EWS-fusion antisense abolishes Ewing tumorigenicity *in vitro* and *in vivo*.
- Catalytic-nucleic-acid route: **PMID: 7987829** (a hammerhead ribozyme *"which discriminates in
  vitro between PML/RARα … and PML and RARα, the transcripts from the nonrearranged alleles"*),
  **PMID: 8127665 · PMC523580 · doi:10.1093/nar/22.3.301**, **PMID: 9150886**, and **PMID: 9224607 ·
  PMC146844 · doi:10.1093/nar/25.15.3074** — the last of which is a warning the manuscript should
  read: *"Several hammerhead ribozymes with relatively long junction-recognition sequences have
  **poor substrate-specificity**."* Long junction-spanning arms do not buy selectivity.

**2000s — the rationale written down as a general principle.**

- **PMID: 16083345 · doi:10.1517/14728222.9.4.825** — Maksimenko & Malvy, 2005. *"the **junction
  point at the mRNA level offers a target for short therapeutic nucleic acids that is present only in
  the cancer cells and not in the normal tissues** of a patient. Several teams have, therefore,
  investigated the activity of antisense oligonucleotides and siRNAs targeted against the junction
  point."* This is the manuscript's central rationale, in a review, 21 years ago.
- **PMID: 14620508 · doi:10.1023/a:1026122914852** — *"Oligonucleotides targeted against a **junction
  oncogene** are made efficient by nanotechnologies"*, 2003 — junction ASO plus a delivery vehicle,
  which is also the manuscript's §3c shape.

**2010s–2020s — junction siRNA with parental sparing demonstrated, repeatedly, and delivery solved.**

- **PMID: 33241214 · PMC7680176 · doi:10.1093/noajnl/vdaa132** — 10 siRNAs tiled across the
  FGFR3-TACC3 breakpoint; *"7/10 iF3T3 depleted F3-T3, and **importantly, did not affect levels of
  wild-type (WT) FGFR3 or TACC3**."* The manuscript's specificity endpoint, demonstrated at a bench.
- **PMID: 36265509 · PMC10101799 · doi:10.4143/crt.2022.910** — siRNAs against the BRD4-NUTM1
  junction: *"specific inhibitory effects on the B4N fusion transcript and fusion protein **without
  affecting the endogenous expression of the parent genes**."*
- **PMID: 36302174 · PMC9811160 · doi:10.1158/1078-0432.ccr-22-1851** — *"We screened short hairpin
  RNAs (shRNA) **tiled over the fusion junction**"* for DNAJB1-PRKACA, in two PDX models.
- **PMID: 37980543 · PMC10787139 · doi:10.1016/j.ymthe.2023.11.012** — **the closest program-level
  precedent.** GalNAc-conjugated siRNA against the DNAJB1::PRKACA **fusion junction** in fibrolamellar
  HCC: *"mRNA degrading modalities such as **antisense oligonucleotides or small interfering RNAs
  provide an opportunity to specifically target the fusion junction**… Knockdown of DNAJB1::PRKACA
  results in durable growth inhibition of FLC PDX in vivo with no detectable toxicities."* A rare,
  fusion-driven cancer; junction-exclusive design; **and the delivery problem solved by a receptor
  conjugate** — which is precisely the axis the manuscript names as unsolved for EMC.
- Sarcoma specifically: **PMID: 20648560 · doi:10.1002/ijc.25564** (*"siRNA … targeting the
  **breakpoint** of EWS/Fli-1"*, xenograft tumour-growth inhibition reported in that model — a result in Ewing sarcoma, not in EMC, and no efficacy is claimed here for EMC); **PMID: 27261335 ·
  doi:10.1016/j.jconrel.2016.05.063** (RGD-targeted nanoparticles carrying siRNA *"directed against
  the **breakpoint** of P3F"*, PAX3-FOXO1, alveolar rhabdomyosarcoma); **PMID: 20198325 ·
  doi:10.3892/ijo_00000559** and **PMID: 23716114 · PMC3916608** (SS18-SSX1 in synovial sarcoma,
  systemic nanoparticle delivery *in vivo*).
- Prostate: **PMID: 23052253 · PMC3525716** and **PMID: 31614005 · PMC6925833** (TMPRSS2/ERG
  junctional isoforms, liposomal nanovectors). Leukaemia: **PMID: 21846246 · PMC3237690**
  (PML-RARα breakpoint), **PMID: 31104089 · PMC7116733** (BCR-ABL LNP), **PMID: 40991849 ·
  PMC12824707 · doi:10.1182/blood.2025028988** (RUNX1::RUNX1T1 siRNA-LNP in **primary** AML cells,
  2025). Review, 2026: **PMID: 42110475 · PMC13156592 · doi:10.1016/j.omton.2026.201213**.

**Clinical stage.** **PMID: 27166877 · PMC5023384 · doi:10.1038/mt.2016.93** — *"Bi-shRNA EWS/FLI1 …
targets the identical **type 1 translocation junction region** of the EWS/FLI1 transcribed mRNA…
Target protein and RNA knockdown of 85–92% was demonstrated… Type 1 Ewing's sarcoma xenograft
modeling confirmed dose related safety and tumor response… These results provide the justification to
**initiate clinical testing**."* Follow-through in patients: **PMID: 36780200 · PMC10150239**.

### The design methodology also exists

- **PMID: 26627251 · PMC4672813 · doi:10.1073/pnas.1517039112** — *"Canonical siRNA design algorithms
  have become remarkably effective… but in some cases (**e.g., a fusion junction site**) region choice
  is restricted. In these instances, alternative approaches are necessary."* Exactly the problem the
  manuscript's §3a-ter breakpoint scan addresses, named and attacked in 2015 for BCR-ABL and
  TMPRSS2-ERG.
- **PMID: 31728968 · doi:10.1007/978-1-4939-9904-0_11** — a protocols chapter: *"sequence homology
  restricts the targeting region to the chimeric junction and **can result in off-target effects on
  the parental genes**. In this chapter, we provide guidelines and procedures for RNAi design of
  chimeric RNAs… and **necessary controls** to accompany each set of experiments."* The manuscript's
  §4 control design is a solved, published protocol.

### What was NOT found — and the accounting that makes that auditable

**No junction-directed oligonucleotide against EWSR1::NR4A3, or against any NR4A3 fusion.** The two
corpora are 5,385 rows / **5,153 unique records** (232 papers matched both queries), and both queries
carried NR4A3 / EWS-NR4A3 / EWS-CHN terms. A bare "we found nothing" is not checkable, so here is the
per-fusion accounting behind it — a record counts under a fusion if its title or abstract names it, and
the two narrowing columns additionally require an oligonucleotide term and a junction/breakpoint term:

| fusion | records naming it | + oligo modality | + junction/breakpoint |
|---|---:|---:|---:|
| **EWSR1::NR4A3 (EMC)** | **4** | **0** | **0** |
| BCR::ABL1 (CML) | 409 | 170 | 108 |
| EWSR1::FLI1 (Ewing) | 182 | 55 | 37 |
| PAX3::FOXO1 (ARMS) | 64 | 9 | 4 |
| RUNX1::RUNX1T1 (AML) | 51 | 12 | 8 |
| SS18::SSX (synovial) | 50 | 6 | 2 |
| PML::RARA (APL) | 30 | 8 | 5 |
| TMPRSS2::ERG (prostate) | 30 | 8 | 5 |
| EWSR1::WT1 (DSRCT) | 24 | 4 | 2 |
| FGFR3::TACC3 (GBM) | 9 | 3 | 2 |
| DNAJB1::PRKACA (FLC) | 6 | 5 | 3 |
| BRD4::NUTM1 (NUT ca.) | 4 | 2 | 2 |

The four EWSR1::NR4A3 rows are three distinct papers and **not one is an oligonucleotide study**:
PMID: 40762284 (NR4A3/EWSR1 in bladder cancer), PMID: 29937513 (a *KIT* mutation in an EMC case report)
and PMID: 25097177 (a myelofibrosis miRNA analysis). An independent full-text grep across the
open-access bodies of the junction corpus agrees — two NR4A3 papers, neither an oligonucleotide study.
⚠ **The method is title/abstract-only, so every number above is a LOWER bound** — which is the right
direction for this particular claim, because a lower-bound method cannot manufacture a zero it did not
observe. Against 108 junction+oligo records for BCR::ABL1, EMC is not a thin search result; it is an
untouched indication.
**Also not found: any gapmer** — as opposed to siRNA/shRNA/ribozyme/unmodified ODN — **directed at a
fusion junction in a modern LNA/cEt architecture.** The 1990s work is unmodified or
phosphorothioate ODN; the 2010s–2020s work is overwhelmingly RNAi. That gap is real but it is a
**chemistry** gap, and per Part 1(a) it is a gap the field has partly avoided on purpose, because a
gapmer's discrimination at a single-base scale is poor without engineered gap modifications.

---

## Verdict on PUB-ASO's novelty claim

**It survives, but only in the narrower form the manuscript is already half-committed to, and the
paper must state the prior art itself rather than let a reviewer find it.**

What is **not** novel, and would be indefensible to imply:

1. **Targeting a fusion breakpoint junction with an oligonucleotide.** 1991, and continuously since.
2. **The fusion-exclusivity rationale** — "the junction sequence exists in no normal transcript, so
   base-pairing buys tumour-exclusivity." Written as a general principle in a 2005 review
   (PMID: 16083345).
3. **RNase-H-mediated cleavage at a sarcoma fusion breakpoint.** PMID: 9049825, 1997.
4. **Demonstrating parental sparing.** Done for FGFR3-TACC3, BRD4-NUTM1, PML-RARα, TMPRSS2-ERG.
5. **The decisive §4 experiment** (junction oligo vs scrambled control, with parental sparing) is a
   published protocol (PMID: 31728968) that has been executed in at least six fusion cancers.
6. **"The platform generalises to any recurrent-fusion cancer with a defined breakpoint."** True, and
   already generalised — by other people, in ten indications, one of them in the clinic.

What **is** novel and defensible:

1. **EMC / EWSR1::NR4A3 has never been attempted.** No junction-directed oligonucleotide against any
   NR4A3 fusion appears in 5,385 records. Genuinely first — an **indication-level** first.
2. **The degrader-vs-ASO argument is EMC-specific and is the paper's real contribution.** No prior
   junction-oligo paper had to argue against a competing modality that is *sequence-identical* to
   wild-type; that argument only exists because NR4A3's LBD is retained intact in the fusion and
   NR4A3 is itself a tumour suppressor (PMID: 17515897, PMID: 33106376). This is not a
   junction-oligo insight and it is not available in Ewing or FLC.
3. **The breakpoint-favorability scan as a *selection* step** (§3a-ter/§3a-quater) — sweeping
   candidate breakpoints on GC/complexity/off-target and reporting that favorability is
   breakpoint-conditional. The nearest prior work (PMID: 26627251) optimises an siRNA *outside* a
   fixed junction; it does not triage across junctions. Modest, but real, and it is a methods
   contribution rather than a claim about EMC.
4. **The honest negative that the reference junction is intrinsically bad** (75–81 % GC,
   low-complexity, poor predicted specificity) is a publishable result on its own and nobody has
   reported it.

What this costs the paper, stated plainly:

- **A prior-art / related-work section is mandatory**, and it must appear before §2, not in a
  limitations paragraph. A design paper whose design has 35 years of precedent, submitted without
  citing that precedent, gets desk-rejected — and reasonably so.
- **The framing must move from "we propose junction-directed oligos" to "we apply an established
  modality to EMC for the first time, and report where EMC's junction sequence makes it hard."** That
  is a smaller claim and a much more defensible one.
- **§3c gains an argument it currently lacks.** DNAJB1::PRKACA (PMID: 37980543) shows a
  receptor-conjugated junction siRNA working in a rare fusion cancer — evidence that the delivery gate
  is passable in principle, with the honest caveat that GalNAc/ASGPR is a liver-specific handle EMC
  does not have. That is a stronger §3c than the current one and it comes from the prior art.
- **§3a-quater must be re-scored or re-worded** per Part 1(a). This is the one place where prior art
  and the citation audit collide: the paper's specificity headline rests on a heuristic the literature
  quantifies at ~5-fold.

---

## Part 3 — noted for the record, not fixed here

### ⛔ §3a-quinquies is a RETRACTED section still sitting in the manuscript body

Lines 562–690 of `fusion-junction-aso-working-record.md` are a fully retracted section retained inline, under
a banner, in the body of a document whose front matter says `status: live`. It is superseded by
§3a-sexies. Keeping a withdrawn section in the running text — rather than in an appendix — means
every quotable sequence, GC value and off-target count in it stays quotable, which is precisely what
[CLAUDE.md §1 rule 1.2](../../../CLAUDE.md) says corrections must not do: *"never leave the 'was X, then
Y, both wrong, now Z' narrative in the live text."*

### ⚠ AND THE RETRACTION'S OWN ABSENCE CLAIM IS FALSE — 13 of the 14 "never existed" artifacts ARE on `origin/modalities-cache`

This is a correction to the task I was given as well as to the manuscript. The manuscript's
Reproducibility section states:

> *"The `e9n3`, `e10n3` and `e13n3` variants and **every** exon-mode siRNA file are absent from
> `origin/main`, from `origin/modalities-cache` and from every commit reachable in this clone."*

**Measured 2026-08-08, `git cat-file -e <ref>:<path>` against a freshly fetched clone:**

| file | `origin/main` | `origin/modalities-cache` |
|---|---|---|
| `junction-aso-designs-e9n3.json` | absent | **absent** |
| `junction-aso-designs-{e10,e13}n3.json` | absent | **PRESENT** |
| `junction-aso-offtarget-{e9,e10,e13}n3.json` | absent | **PRESENT** |
| `aso-insilico-evaluation-{e9,e10,e13}n3.json` | absent | **PRESENT** |
| `junction-sirna-designs-{e7,e9,e10,e12,e13}n3.json` | absent | **PRESENT** |

**13 of the 14** files the manuscript calls absent are at the tip of `origin/modalities-cache`. Only
`junction-aso-designs-e9n3.json` is genuinely absent everywhere. Thirteen of them were added in one
commit — **`30eb56842`, 2026-07-03 01:05:15 UTC, `github-actions[bot]`, "ASO real/reference junction
screens: design + gap-resolved BLAST + uncapped eval + siRNA", 13 files, 3,400 insertions** — which is
reachable from `origin/modalities-cache` and from nothing else.

Three consequences, in increasing order of seriousness:

1. **The `main`-only half of the claim is correct** and the `modalities-cache` half is not. This is
   the branch-drift bug of [CLAUDE.md §7](../../../CLAUDE.md) exactly: an artifact whose only home is a
   non-default branch reads as non-existent from `main`.
2. **The withdrawal's *independent* ground collapses.** The manuscript withdraws those claims *"as
   unverifiable, **independently of** the seam defect."* They are verifiable — the files are there. The
   seam-defect retraction still stands entirely on its own and nothing measured is restored by this;
   what falls is only the second, additional reason.
3. ⛔ **The worse half: those 13 files carry the defective seam and NO retraction banner.** Reading
   `origin/modalities-cache:research/modalities/junction-sirna-designs-e12n3.json` returns
   `"junction_context_mRNA": "AATGGTTTGATG|TTGTCCGTACAG"` and `"assumption": false` — the retracted
   `TTGTCCGTACAG` seam, asserted as real, with `"n_passing_all_filters": 3`. The six `e7n3`/`e12n3`
   files on `main` were regenerated at the corrected seam on 2026-08-06; **their cache-branch
   siblings were not touched.** So the repository's most confidently-worded retracted numbers are
   sitting unbannered on a branch, and the manuscript tells a reader they do not exist. A
   mislabelled record is worse than a missing one, and here the label is on the wrong side.

**Not fixed here** — regenerating or bannering `modalities-cache` is outside this task's file scope,
and the branch is written by a workflow. But it should be fixed before anything is submitted, and the
manuscript's absence sentence should be corrected in the same pass.
