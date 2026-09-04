---
id: DOC-FUSION-JUNCTION-ASO-NAT-CANDIDATE-REFERENCES-2026-09-04
title: "References — fusion-junction ASO journal article"
level: L3
kind: manuscript
status: live
canonical_for:
  - the reference list of the fusion-junction ASO journal article
purpose: >
  The numbered reference list spliced into the journal article at its `## References` anchor by
  build_submission_pdf.py. The entries are hand-maintained; two fields within them are not — the
  journal name is written from journal-abbreviations.json by journal_abbreviations.py and the
  author segment from journal-reference-authors.json by journal_reference_authors.py, both read
  out of fetch products. It is held to the manuscript by
  tests/test_journal_references_match_the_prose.py.
scope: >
  Bibliographic records only. No scientific claim is made here, and nothing here asserts efficacy,
  safety, a therapeutic window or clinical readiness.
audience: [external reviewers, collaborators, maintainers]
date: 2026-08-25
last_verified: 2026-08-25
related: [DOC-FUSION-JUNCTION-ASO-JOURNAL]
---

<!-- HAND-MAINTAINED, EXCEPT FOR TWO FIELDS THAT ARE WRITTEN FROM FETCH PRODUCTS. The numbered list
     lives here so build_submission_pdf.py can splice it at the `## References` anchor, as it does
     for the preprint. ⛔ The banner once claimed machine provenance while no generator existed, so
     the file read as machine-derived while being edited by hand and checked by nothing —
     submission_citations.py --check reads the PREPRINT and reports its
     references, which is why a green gate said nothing about the entries below. Two fields have
     since been taken out of hand-maintenance, and ONLY those two: the JOURNAL NAME
     (journal_abbreviations.py --apply, from journal-abbreviations.json) and the AUTHOR SEGMENT
     (journal_reference_authors.py --apply, from journal-reference-authors.json). Both are written
     from fetched records and re-checked with `--check`; everything else in an entry — title, year,
     volume, pages, PMID, doi — is still typed here and checked only by the tests below. (This sentence
     typed "these 21" while the list stood at 23: a count beside a list that grows is the drift
     this repository keeps finding, so the count is gone rather than corrected — the list is its
     own home.) What holds it to the
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

1. Labelle Y, J Zucman, G Stenman, LG Kindblom, J Knight, C Turc-Carel, B Dockhorn-Dworniczak, N Mandahl, C Desmaze, et al. (1995). Oncogenic conversion of a novel orphan nuclear receptor by chromosome translocation. Hum Mol Genet 4:2219–2226. PMID: 8634690. doi:10.1093/hmg/4.12.2219
2. Paioli A, S Stacchiotti, D Campanacci, E Palmerini, AM Frezza, A Longhi, S Radaelli, DM Donati, G Beltrami, et al. (2021). Extraskeletal Myxoid Chondrosarcoma with Molecularly Confirmed Diagnosis: A Multicenter Retrospective Study Within the Italian Sarcoma Group. Ann Surg Oncol 28:1142–1150. PMID: 32572850. doi:10.1245/s10434-020-08737-7
3. Chen X, X He, R Peng, M Chen and H Zhang. (2026). A series of extraskeletal myxoid chondrosarcomas with rare morphological and molecular variations. Histopathology 89:181–188. PMID: 41755350. doi:10.1111/his.70131
4. Remiszewski P, S Falkowski, A Szumera-Ciećkiewicz, MJ Spałek, P Rutkowski and AM Czarnecka. (2025). From pathogenesis to the patient's bedside: a comprehensive review of extraskeletal myxoid chondrosarcoma. J Cancer Res Clin Oncol 151:283. PMID: 41055792. doi:10.1007/s00432-025-06316-5
5. Stacchiotti S, GP Dagrada, R Sanfilippo, T Negri, I Vittimberga, S Ferrari, F Grosso, G Apice, M Tricomi, et al. (2013). Anthracycline-based chemotherapy in extraskeletal myxoid chondrosarcoma: a retrospective study. Clin Sarcoma Res 3:16. PMID: 24345066. doi:10.1186/2045-3329-3-16
6. Stacchiotti S, S Ferrari, A Redondo, N Hindi, E Palmerini, MA Vaz Salgado, AM Frezza, PG Casali, A Gutierrez, et al. (2019). Pazopanib for treatment of advanced extraskeletal myxoid chondrosarcoma: a multicentre, single-arm, phase 2 trial. Lancet Oncol 20:1252–1262. PMID: 31331701. doi:10.1016/S1470-2045(19)30319-5
7. Skórski T, C Szczylik, L Malaguarnera and B Calabretta. (1991). Gene-targeted specific inhibition of chronic myeloid leukemia cell growth by BCR-ABL antisense oligodeoxynucleotides. Folia Histochem Cytobiol 29:85–89. PMID: 1794439.
8. Toretsky JA, Y Connell, L Neckers and NK Bhat. (1997). Inhibition of EWS-FLI-1 fusion protein with antisense oligodeoxynucleotides. J Neurooncol 31:9–16. PMID: 9049825. doi:10.1023/a:1005716926800
9. Parker Kerrigan BC, D Ledbetter, M Kronowitz, L Phillips, J Gumin, A Hossain, J Yang, M Mendt, S Singh, et al. (2020). RNAi technology targeting the FGFR3-TACC3 fusion breakpoint: an opportunity for precision medicine. Neurooncol Adv 2:vdaa132. PMID: 33241214. doi:10.1093/noajnl/vdaa132
10. Ward SV, T Sternsdorf and NB Woods. (2011). Targeting expression of the leukemogenic PML-RARα fusion protein by lentiviral vector-mediated small interfering RNA results in leukemic cell differentiation and apoptosis. Hum Gene Ther 22:1593–1598. PMID: 21846246. doi:10.1089/hum.2011.079
11. Shao L, I Tekedereli, J Wang, E Yuca, S Tsang, A Sood, G Lopez-Berestein, B Ozpolat and M Ittmann. (2012). Highly specific targeting of the TMPRSS2/ERG fusion gene using liposomal nanovectors. Clin Cancer Res 18:6648–6657. PMID: 23052253. doi:10.1158/1078-0432.ccr-12-2715
12. Neumayer C, D Ng, D Requena, CS Jiang, A Qureshi, R Vaughan, TP Prakash, A Revenko and SM Simon. (2024). GalNAc-conjugated siRNA targeting the DNAJB1-PRKACA fusion junction in fibrolamellar hepatocellular carcinoma. Mol Ther 32:140–151. PMID: 37980543. doi:10.1016/j.ymthe.2023.11.012
13. Kauppinen S, B Vester and J Wengel. (2005). Locked nucleic acid (LNA): High affinity targeting of RNA for diagnostics and therapeutics. Drug Discov Today Technol 2:287–290. PMID: 24981949. doi:10.1016/j.ddtec.2005.08.012
14. Andersson P, SA Burel, H Estrella, J Foy, PH Hagedorn, TA Harper Jr, SP Henry, JC Hoflack, EM Holgersen, et al. (2025). Assessing Hybridization-Dependent Off-Target Risk for Therapeutic Oligonucleotides: Updated Industry Recommendations. Nucleic Acid Ther 35:16–33. PMID: 39912803. doi:10.1089/nat.2024.0072
15. Dyer SC, O Austine-Orimoloye, AG Azov, M Barba, I Barnes, VP Barrera-Enriquez, A Becker, R Bennett, M Beracochea, et al. (2025). Ensembl 2025. Nucleic Acids Res 53:D948–D957. PMID: 39656687. doi:10.1093/nar/gkae1071
16. Sugimoto N, S Nakano, M Katoh, A Matsumura, H Nakamuta, T Ohmichi, M Yoneyama and M Sasaki. (1995). Thermodynamic parameters to predict stability of RNA/DNA hybrid duplexes. Biochemistry 34:11211–11216. PMID: 7545436. doi:10.1021/bi00035a029
17. Panagopoulos I, F Mertens, M Isaksson, HA Domanski, O Brosjö, S Heim, B Bjerkehagen, R Sciot, P Dal Cin, et al. (2002). Molecular genetic characterization of the EWS/CHN and RBP56/CHN fusion genes in extraskeletal myxoid chondrosarcoma. Genes Chromosomes Cancer 35:340–352. PMID: 12378528. doi:10.1002/gcc.10127
18. Huang SC, JC Lee, YC Hsu, JW Tsai, YC Kao, TH Hsieh, YM Chang, KC Chang, PS Wu, et al. (2023). Extraskeletal Myxoid Chondrosarcomas: The Uncommon Clinicopathologic Manifestations and Significance of TAF15::NR4A3 Fusion. Mod Pathol 36:100161. PMID: 36948401. doi:10.1016/j.modpat.2023.100161
19. Urbini M, V Indio, A Astolfi, G Tarantino, SL Renne, S Pilotti, AP Dei Tos, R Maestro, P Collini, et al. (2018). Identification of an Actionable Mutation of KIT in a Case of Extraskeletal Myxoid Chondrosarcoma. Int J Mol Sci 19:E1855. PMID: 29937513. doi:10.3390/ijms19071855
20. Wilbur HC, DR Robinson, YM Wu, C Kumar-Sinha, AM Chinnaiyan and R Chugh. (2022). Identification of Novel PGR-NR4A3 Fusion in Extraskeletal Myxoid Chondrosarcoma and Resultant Patient Benefit From Tamoxifen Therapy. JCO Precis Oncol 6:e2200039. PMID: 36103645. doi:10.1200/po.22.00039
21. Brenca M, S Stacchiotti, K Fassetta, M Sbaraglia, M Janjusevic, D Racanelli, M Polano, S Rossi, S Brich, et al. (2019). NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. J Pathol 249:90–101. PMID: 31020999. doi:10.1002/path.5284
22. Bangerter JL, KJ Harnisch, Y Chen, C Hagedorn, L Planas-Paz and C Pauli. (2023). Establishment, characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models. Hum Cell 36:446–455. PMID: 36316541. doi:10.1007/s13577-022-00818-x
23. Li Y, JT Nguyen, M Ammanamanchi, Z Zhou, EF Harbut, JL Mondaza-Hernandez, CA Meyer, DS Moura, J Martin-Broto, HN Hayenga and L Bleris. (2023). Reduction of Tumor Growth with RNA-Targeting Treatment of the NAB2-STAT6 Fusion Transcript in Solitary Fibrous Tumor Models. Cancers (Basel) 15:3127. PMID: 37370737. doi:10.3390/cancers15123127
24. Lee MS, S An, JY Song, M Sung, K Jung, ES Chang, J Choi, DY Oh, YK Jeon, et al. (2023). Cancer-Specific Sequences in the Diagnosis and Treatment of NUT Carcinoma. Cancer Res Treat 55:452–467. PMID: 36265509. doi:10.4143/crt.2022.910
