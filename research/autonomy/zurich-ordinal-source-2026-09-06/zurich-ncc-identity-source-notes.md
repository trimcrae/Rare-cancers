---
id: DOC-ZURICH-NCC-IDENTITY-SOURCES-20260906
title: Primary chemical identity sources for the Zurich NCC crosswalk
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Preserve nominal identity evidence and exclusions for complete catalogue matching.
scope: Chemical labels and formulations only; no assay compatibility or response comparison.
audience: [maintainers, autonomous research agents]
---

# Frozen source-only identity crosswalk, 2026-09-06

The JSON/CSV contains all 40 Figure 5 labels, 20 single nominal matches, six multi-form candidates, one hydrate ambiguity, one solvate ambiguity, one unresolved spelling with two candidates, and 11 labels with no catalogue candidate (including unresolved WE-822). There are 36 candidate catalogue rows. These are chemical-label matches, not evidence of compatible assays. No NCC response data were consulted for this mapping; the same agent previously recovered those files, so this is not a claim of personal blinding.

## Primary source inputs

- Zurich article and Figure 5 legend: https://link.springer.com/article/10.1007/s13577-022-00818-x ; figure image recovered from https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/supplementaryFiles . See existing ordinal freeze for source digests, methods/legend mismatch and transcription ambiguity. All labels are preserved, including Abmaciclib and WE-822. No numeric outcomes were imputed.
- NCC catalogue only, Supplementary Table 2, sheet `drug list`, columns A:C (Cat#, CAS#, Name): https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs13577-025-01250-7/MediaObjects/13577_2025_1250_MOESM4_ESM.xlsx . JSON candidates record exact Excel row locators. The generator never opens MOESM5, MOESM6, or derived response CSVs.

## Primary chemical disambiguation evidence

- Abemaciclib S5716 / CAS1231929-97-7: https://www.selleck.co.jp/products/abemaciclib-cdk4-6-inhibitor.html . Abemaciclib mesylate S7158 / CAS1231930-82-7: https://www.selleck.co.jp/products/abemaciclib-ly2835219-mesylate-cdk4-6-inhibitor.html (publisher tool page lines181–191 identifies product, catalogue ID and CAS). This corrects interpretation of NCC's unsuffixed S7158 name, but DOES NOT establish the Zurich spelling correction.
- Supplier FAQ distinguishes S1068 crizotinib (R enantiomer) from S7505 (S)-crizotinib: https://www.selleckchem.com/products/s-crizotinib.html . Exclude S7505 from crizotinib candidates; retain S1068 and S5190 hydrochloride, since Zurich has no salt or catalogue ID.
- Pemetrexed disodium S1135 / CAS150399-23-8: https://www.selleckchem.com/products/Pemetrexed-disodium.html . Manufacturer SDS distinguishes disodium 2.5 hydrate / CAS357166-30-4 from disodium: https://www.fishersci.at/store/msds?countryCode=AT&language=en&partNumber=15365058 . Zurich specifies hydrate but no hydration number. Do not treat the two CAS as exact matches or substitute free pemetrexed.
- Trametinib DMSO solvate S4484 / CAS1187431-43-1: supplier SDS https://www.selleck.fr/msds/MSDS_S4484.pdf . Zurich has no solvate qualifier; retain as conditional candidate only.
- Irinotecan and SN-38 are distinct parent/active metabolite, not interchangeable compounds: FDA label https://www.accessdata.fda.gov/drugsatfda_docs/label/2022/020571Orig1s053lbl.pdf . Thus SN-38 remains absent even if irinotecan is in NCC catalogue.
- HDM201 = siremadlin / NVP-HDM201: manufacturer https://www.caymanchem.com/product/38516/siremadlin . None in NCC catalogue.
- Derazantinib = ARQ087: manufacturer catalogue https://file.selleckchem.com/publicity/Selleck-Inhibitor-Catalog-Low-Resolution-EN.pdf . Neither name in NCC catalogue.
- Adavosertib = MK1775 / AZD1775: manufacturer https://www.selleckchem.com/datasheet/adavosertib-mk-1775-wee1-inhibitor-S152510-DataSheet.html . None in NCC catalogue.
- Ipatasertib = GDC0068: NCI https://discover.nci.nih.gov/drugs/cellminercdb/ipatasertib_cellminercdb.html . Neither in NCC catalogue.
- Selpercatinib = LOXO292: NCI https://www.cancer.gov/publications/dictionaries/cancer-drug/def/selpercatinib . Neither in NCC catalogue; pralsetinib is not a name match.
- Berzosertib = VE-822 / VX970 / M6620: manufacturer https://www.selleck.co.uk/products/berzosertib-ve-822-atr-inhibitor.html . This supports candidate aliases only, NOT resolution of printed WE-822. All candidate names absent from NCC catalogue.
- AZD5153 manufacturer product sheet: https://cdn.caymanchem.com/cdn/insert/20864.pdf ; PU-H71 manufacturer COA: https://cdn.caymanchem.com/cdn/downloadCofa/Cayman-CofA-11450-0461734.pdf . No matching NCC names.

The six generic labels with multiple catalogue forms (ceritinib, dabrafenib, crizotinib, enasidenib, sorafenib, cabozantinib) retain both named/CAS candidates directly supported by MOESM4. No response-based choice, averaging of forms, or broad target annotation has been made. Explicit Zurich hydrochloride, phosphate, tartrate, sulfate and tosylate labels exclude differently specified NCC forms as recorded row by row.

## Rule for any later comparison

Freeze this mapping before joining outcomes. The initial nominal set is exactly the 20 `strict_nominal_include=true` rows. The remaining candidate forms require source clarification or an explicitly frozen sensitivity rule, never picking the better-performing salt. Assay compatibility and the Zurich Methods AUC versus Figure 5 viability-percent legend discrepancy still require resolution before biological concordance claims. No correlation or other comparison statistic has been run here. Stop numeric interpretation if that discrepancy cannot be resolved; identity and ordinal source recovery remain useful standalone provenance assets.
