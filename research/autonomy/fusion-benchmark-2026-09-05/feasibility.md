---
id: DOC-FUSION-BENCHMARK-FEASIBILITY-2026-09-05
title: External fusion-junction oligonucleotide benchmark feasibility
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Record a bounded primary-source data gate and retain recoverable evidence and failures.
audience: [maintainers, autonomous research agents]
scope: Public design-level fusion and both-parent outcomes; no model, manuscript, or clinical inference.
---

The transferable benchmark is **not supported under the current contract**. Three siRNA target families have some measured both-parent evidence: BCR-ABL1, KMT2A-AFF1 (MLL-AF4), and FGFR3-TACC3. They do not provide three families with multiple designs and informative negative outcomes measured on the same fusion/both-parent basis. In particular, FGFR3-TACC3 has parent follow-up only for one selected junction design; the BCR-ABL1 failed screening designs were not reported. MLL-AF4 supplies the strongest small paired positive/negative subset, with an important wrong-breakpoint/model distinction. Counting cell lines, doses, or breakpoint variants as new families would not fix the deficit.

This is a negative feasibility result, not a claim that public evidence is nonexistent. [evidence.json](evidence.json) preserves 63 design/condition inventory rows, including nulls and explicit missingness, from 16 source records. Four rows have exact numeric fusion/BCR/ABL triples, covering two selected sequences in one family. No figure values were digitized. ASO, synthetic siRNA, shRNA, and expressed structured antisense remain separate.

## Recoverable siRNA evidence

| Primary source | Actual evidence and decisive limitation |
|---|---|
| [Scherr 2003](https://doi.org/10.1182/blood-2002-06-1685), Table 1, p. 1568 | K562, 24 h: b3a2_1 has fusion/BCR/ABL values 24.8/98.0/95.0%; b3a2_3 has 32.4/99.5/109%. These are normalized transcript/GAPDH percentages, not percent knockdown. SDs and n=4 independent experiments are preserved in JSON. Two primary CD34+ samples have numeric triples; four PBMNC samples explicitly have parents **not done**. The initial four-design screen selected two; unsuccessful designs/data are not shown. Table 2 retains failure to significantly suppress CML colony formation, a different endpoint. |
| [Thomas 2005](https://doi.org/10.1182/blood-2005-03-1283), Fig. 1A/D/E | Fourteen MLL-AF4 designs were screened at 500 nM, 24 h. Separate fusion/MLL/AF4 qPCR appears for selected siMA6 in SEM and siMARS in RS4;11, with wrong-breakpoint siMA6 as a negative in RS4;11. siMA3 also suppressed AF4, but those data are explicitly not shown; siMA13 was nearly inactive. Parent outcomes are selectively reported, and most scan sequences were not transcribed. Figure-only values remain null. |
| [Parker Kerrigan 2020](https://doi.org/10.1093/noajnl/vdaa132), Figs. 2-3; supplementary Figs. 5-6 | Ten target strings and fusion-protein screening blots are public. Only selected #5 proceeds to 25/100/250 pmol, 48 h parent testing. WT FGFR3 is assayed in a separate WT-FGFR3 expression line; WT TACC3 is measured by protein blot. This is not a same-cell endogenous transcript triple or a negative-design parent panel. Full duplex chemistry is not disclosed. |
| [Lee 2023](https://doi.org/10.4143/crt.2022.910), S1-S3 tables, S5-S6 figures | All 15 BRD4-NUTM1 and 16 SS18-SSX1 duplex sequences are recoverable, with 3-prime dTdT overhangs, 50 nM and 72 h assays. Visually inspected S5 plots fusion and WT BRD4 only; S6 plots fusion and WT SS18 only. S3 lists a WT NUTM1 primer but that is not an outcome. No WT SSX1 primer appears there. B4N #6 failure, #12/#15 BRD4 effects, and SS #12 transcript/protein discordance are retained. |
| [Gavrilov 2015](https://doi.org/10.1073/pnas.1517039112), Figs. 2-5, S1-S3, Methods | Public sequences compare unmodified, terminal-asymmetry, and wobble duplexes. BCR fusion qPCR/protein and ectopic V5-TMPRSS2-ERG protein results do not measure both parents. Endogenous ERG/fusion band ambiguity is explicitly acknowledged. RNA, protein, viability, dose saturation, and vehicle toxicity disagree in informative ways; these are not interchangeable labels. This is siRNA prior art, not an ASO dataset. |
| [Varley 2014](https://doi.org/10.1007/s10549-014-3019-2), Fig. 4 and siRNA Methods | Two ON-TARGETplus CTSD-IFITM10 sequences; MCF7, 3 pmol/well, 48 h qPCR. Text reports 42-51% transcript remaining across both designs; exact design assignments were not transcribed. Both designs were active. Neither parent outcome is identified in the main article. The XLS supplement was identified but not parsed, so this is a main-text limitation rather than an exhaustive absence claim. |
| [Ohba 2004](https://doi.org/10.1002/cncr.20468), abstract | Three constructs include weak and nonselective BCR-ABL/c-ABL outcomes. Direct full text returned 403. Exact sequences, figures, and BCR-parent outcomes remain uninspected, not presumed absent. |

The Scherr and Thomas primary texts were inspected through author-posted article transcriptions on ResearchGate after publisher access failed. Exact alternate URLs and page/figure pointers are in JSON. These are original reports, not review summaries. The coordinator independently checked the decisive Scherr table and Thomas reporting limitations.

## ASO evidence and counterexamples

[ASP210, 2024](https://doi.org/10.1152/ajpcell.00188.2024) discloses one linked 34mer PS-DNA design with PEG12, Cyanine5 and biotin, alongside fusion qPCR. The inspected assays do not provide WT BCR/ABL effects or a failed-design panel. HL60 viability cannot establish either parent effect. [Stocks and Rabbitts 2000](https://doi.org/10.1093/embo-reports/kvd003), Fig. 4, measures both endogenous parents after expression of masked antisense RNA, but this is a U6-vector/ectopic-fusion system, not a synthetic gapmer stratum.

The [Toretsky 1997](https://doi.org/10.1023/a:1005716926800) abstract reports an RNase-H-dependent cell-free screen followed by selected ODN testing and fusion/EWS protein measurements; FLI1 and full sequences remain uninspected. [Maksimenko 2003](https://doi.org/10.1196/annals.1281.017) supplies an abstract-level lead for two EWS-FLI1 AON chemistries, not verified paired-parent rows.

Negative primary abstracts were deliberately retained: [PMID 7579358](https://pubmed.ncbi.nlm.nih.gov/7579358/) reports a terminal-sequence-dependent nonantisense growth effect; [PMID 7808004](https://pubmed.ncbi.nlm.nih.gov/7808004/) reports nonspecific inhibition across breakpoint contexts; [Käbisch 1994](https://doi.org/10.1159/000204219) reports colony inhibition without reducing the BCR-ABL-positive colony fraction. Their full sequences and molecular outcome tables were not inspected. A targeted [2026 CTSD-IFITM10 passage](https://doi.org/10.1007/s00018-026-06254-6), Fig. 1F-G, additionally reports canonical CTSD reduction by a junction siRNA; its supplement and IFITM10 response remain uninspected.

The strongest unresolved ASO lead is [Kashyap's Oxford DPhil thesis](https://doi.org/10.5287/ora-avzqyvz9q), Chapter 3, Fig. 3.4/p. 113. Indexed primary excerpts describe PS, 16mer LNA and 20mer MOE candidates with fusion/MLL/AF4 RT-qPCR. The PDF returned 403; sequence maps, doses, replicates, raw values and assay specificity were not verified. No thesis row is counted as validated. Even confirmation would add one ASO family, not justify pooling with siRNA or establish the three-family gate.

## Methods, stop, and next decision

This was one lead-driven search, not a systematic review. Named leads were followed through original methods, supplements and cited BCR/MLL studies; separate ASO queries deliberately sought failures. JSON records the principal exact queries, retrieval routes, inspection depth, chemistry limits and missing fields. Lee supplementary PDFs were extracted in memory with pypdf and S5/S6 rendered with PDFium. FGFR3-TACC3 Figures 2/3 were visually inspected. No measurements were invented or inferred from uniqueness, viability, primer availability, or a shared antibody signal.

Stop benchmark development here. The next decisive question is whether a newly accessible source can supply **multiple chemically specified designs, including ineffective/nonselective designs, with matched fusion and both-parent measurements in an additional qualifying family**, while resolving the selected-only coverage in existing families. Merely digitizing existing bars cannot create missing parent measurements. The Oxford thesis is a precise retrieval lead, not authorization for an expanded paper.

Execution used one fresh task at medium effort, without nested agents, runners, installs, paid APIs, GPU work or outreach. Actual model/effort (`gpt-6-astra`, `medium`) was confirmed by the coordinator from local turn metadata. The actual base is `0be885c02d7ae889828052c5090c74c0926249bf` (the contract records its preceding base). Final elapsed time and checks are in JSON. Only the permitted evidence directory was written; no commits, publication, registry/manuscript/graph edits, or shared queue changes occurred. No research process remains running after this bounded task completes. This feasibility result establishes no clinical efficacy, safety, or therapeutic window.
