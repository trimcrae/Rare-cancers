---
id: DOC-FUSION-JUNCTION-ASO-JOURNAL-REFERENCES
title: "References — fusion-junction ASO journal article"
level: L3
kind: manuscript
status: live
canonical_for:
  - the reference list of the fusion-junction ASO journal article
purpose: >
  The numbered reference list spliced into the journal article at its `## References` anchor by
  build_submission_pdf.py. It is hand-maintained rather than generated, and is held to the
  manuscript by tests/test_journal_references_match_the_prose.py rather than by a generator.
scope: >
  Bibliographic records only. No scientific claim is made here, and nothing here asserts efficacy,
  safety, a therapeutic window or clinical readiness.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-20
last_verified: 2026-08-20
related: [DOC-FUSION-JUNCTION-ASO-JOURNAL]
---

<!-- HAND-MAINTAINED, AND CHECKED RATHER THAN GENERATED. The numbered list lives here so
     build_submission_pdf.py can splice it at the `## References` anchor, as it does for the
     preprint. ⛔ It is NOT generated: this banner previously claimed machine provenance while no
     generator existed, so the file read as machine-derived while being edited by hand and checked
     by nothing — submission_citations.py --check reads the PREPRINT and reports its 53
     references, which is why a green gate said nothing about these 21. What holds it to the
     manuscript is test_journal_references_match_the_prose.py: every superscript in the article
     must resolve to an entry here, every entry must be cited, and each entry must carry the PMID
     its citation names. ⛔ NUMBERED BY ORDER OF FIRST CITATION, CONTIGUOUSLY. It previously inherited the extended
     report's numbering so a shared reference carried the same number in both documents. That was
     invisible in the markdown and WRONG IN THE BUILT PDF: an HTML <ol> renumbers its items from 1
     regardless of the source, so a superscript 8 resolved to the 8th printed entry and about two
     thirds of the citations in the typeset article pointed at a real paper that was the wrong one.
     The guard that should have caught it read these markdown files, where the numbering was
     correct, rather than the artefact, where it was not. -->

# References — fusion-junction ASO journal article

*Numbering follows the extended report, so that a reference cited in both documents carries the same
number in each. Metadata is read from retrieved bibliographic records.*

1. Labelle Y, Zucman J, Stenman G, Kindblom LG, Knight J, Turc-Carel C, et al. Oncogenic conversion of a novel orphan nuclear receptor by chromosome translocation. Human molecular genetics. 1995;4(12):2219-2226. PMID: 8634690. doi:10.1093/hmg/4.12.2219
2. Paioli A, Stacchiotti S, Campanacci D, Palmerini E, Frezza AM, Longhi A, et al. Extraskeletal Myxoid Chondrosarcoma with Molecularly Confirmed Diagnosis: A Multicenter Retrospective Study Within the Italian Sarcoma Group. Ann Surg Oncol. 2021;28(2):1142-1150. PMID: 32572850. doi:10.1245/s10434-020-08737-7
3. Stacchiotti S, Dagrada GP, Sanfilippo R, Negri T, Vittimberga I, Ferrari S, et al. Anthracycline-based chemotherapy in extraskeletal myxoid chondrosarcoma: a retrospective study. Clinical Sarcoma Research. 2013;3(1):16. PMID: 24345066. doi:10.1186/2045-3329-3-16
4. Stacchiotti S, Ferrari S, Redondo A, Hindi N, Palmerini E, Vaz Salgado MA, et al. Pazopanib for treatment of advanced extraskeletal myxoid chondrosarcoma: a multicentre, single-arm, phase 2 trial. The Lancet Oncology. 2019;20(9):1252-1262. PMID: 31331701. doi:10.1016/S1470-2045(19)30319-5
5. Skórski T, Szczylik C, Malaguarnera L, Calabretta B. Gene-targeted specific inhibition of chronic myeloid leukemia cell growth by BCR-ABL antisense oligodeoxynucleotides. Folia histochemica et cytobiologica. 1991;29(3):85-89. PMID: 1794439.
6. Toretsky JA, Connell Y, Neckers L, Bhat NK. Inhibition of EWS-FLI-1 fusion protein with antisense oligodeoxynucleotides. Journal of neuro-oncology. 1997;31(1-2):9-16. PMID: 9049825. doi:10.1023/a:1005716926800
7. Parker Kerrigan BC, Ledbetter D, Kronowitz M, Phillips L, Gumin J, Hossain A, et al. RNAi technology targeting the FGFR3-TACC3 fusion breakpoint: an opportunity for precision medicine. Neuro-oncology advances. 2020;2(1):vdaa132. PMID: 33241214. doi:10.1093/noajnl/vdaa132
8. Ward SV, Sternsdorf T, Woods NB. Targeting expression of the leukemogenic PML-RARα fusion protein by lentiviral vector-mediated small interfering RNA results in leukemic cell differentiation and apoptosis. Human gene therapy. 2011;22(12):1593-1598. PMID: 21846246. doi:10.1089/hum.2011.079
9. Shao L, Tekedereli I, Wang J, Yuca E, Tsang S, Sood A, et al. Highly specific targeting of the TMPRSS2/ERG fusion gene using liposomal nanovectors. Clinical cancer research. 2012;18(24):6648-6657. PMID: 23052253. doi:10.1158/1078-0432.ccr-12-2715
10. Neumayer C, Ng D, Requena D, Jiang CS, Qureshi A, Vaughan R, et al. GalNAc-conjugated siRNA targeting the DNAJB1-PRKACA fusion junction in fibrolamellar hepatocellular carcinoma. Molecular therapy. 2024;32(1):140-151. PMID: 37980543. doi:10.1016/j.ymthe.2023.11.012
11. Panagopoulos I, Mertens F, Isaksson M, Domanski HA, Brosjö O, Heim S, et al. Molecular genetic characterization of the EWS/CHN and RBP56/CHN fusion genes in extraskeletal myxoid chondrosarcoma. Genes, chromosomes & cancer. 2002;35(4):340-352. PMID: 12378528. doi:10.1002/gcc.10127
12. Huang SC, Lee JC, Hsu YC, Tsai JW, Kao YC, Hsieh TH, et al. Extraskeletal Myxoid Chondrosarcomas: The Uncommon Clinicopathologic Manifestations and Significance of TAF15::NR4A3 Fusion. Modern pathology. 2023;36(7):100161. PMID: 36948401. doi:10.1016/j.modpat.2023.100161
13. Brenca M, Stacchiotti S, Fassetta K, Sbaraglia M, Janjusevic M, Racanelli D, et al. NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. J Pathol. 2019;249(1):90-101. PMID: 31020999. doi:10.1002/path.5284
14. Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, Pauli C. Establishment, characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models. Human cell. 2023;36(1):446-455. PMID: 36316541. doi:10.1007/s13577-022-00818-x
15. Remiszewski P, Falkowski S, Szumera-Ciećkiewicz A, Spałek MJ, Rutkowski P, Czarnecka AM. From pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid chondrosarcoma. Journal of cancer research and clinical oncology. 2025;151(11):283. PMID: 41055792. doi:10.1007/s00432-025-06316-5
16. Li Y, Nguyen JT, Ammanamanchi M, Zhou Z, Harbut EF, Mondaza-Hernandez JL, et al. Reduction of Tumor Growth with RNA-Targeting Treatment of the NAB2-STAT6 Fusion Transcript in Solitary Fibrous Tumor Models. Cancers. 2023;15(12):3127. PMID: 37370737. doi:10.3390/cancers15123127
17. Lee MS, An S, Song JY, Sung M, Jung K, Chang ES, et al. Cancer-Specific Sequences in the Diagnosis and Treatment of NUT Carcinoma. Cancer research and treatment. 2023;55(2):452-467. PMID: 36265509. doi:10.4143/crt.2022.910
18. Freire PR, Conneely OM. NR4A1 and NR4A3 restrict HSC proliferation via reciprocal regulation of C/EBPα and inflammatory signaling. Blood. 2018;131(10):1081-1093. PMID: 29343483. doi:10.1182/blood-2017-07-795757
19. Beard JA, Tenga A, Chen T. The interplay of NR4A receptors and the oncogene-tumor suppressor networks in cancer. Cellular signalling. 2015;27(2):257-266. PMID: 25446259. doi:10.1016/j.cellsig.2014.11.009
20. Dyer SC, Austine-Orimoloye O, Azov AG, et al. Ensembl 2025. Nucleic acids research. 2025;53(D1):D948-D957. PMID: 39656687. doi:10.1093/nar/gkae1071
21. Kauppinen S, Vester B, Wengel J. Locked nucleic acid (LNA): High affinity targeting of RNA for diagnostics and therapeutics. Drug discovery today. Technologies. 2005;2(3):287-290. PMID: 24981949. doi:10.1016/j.ddtec.2005.08.012
