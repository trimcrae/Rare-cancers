---
id: DOC-METHYLATION-PRIMARY-IDENTITY-AUDIT-20261002
title: Primary specimen identity and cross-accession array audit for methylation score transport
kind: memo
status: live
level: cross-cutting
purpose: Resolve what primary sources state about patient independence and measure available array-identifier overlap before interpreting score transport.
scope: >
  Bounded primary metadata retrieval and executed identity joins for the Koelsche
  reference/validation workbooks and E-MTAB-9875 SDRF. No methylation matrices,
  raw IDAT arrays, model fitting or fixed-prediction loss calculation were run.
  Identifiers support array-level linkage; independent patient linkage remains limited.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

# New finding and required wording correction

The current manuscript omits a relevant primary-source statement. Koelsche et al.'s Methods explicitly says: “All samples of the reference and validation set are from individual/different patients.” This is an author-reported independence assertion, not merely an inference from array identifiers. The primary reference and validation workbooks lack a shared patient-key column with which we could independently verify the assertion. The manuscript should report both facts, rather than leave readers with the impression that the source supplied no patient-independence information.

The audited workbooks contain 1,077 reference and 428 validation profile IDs, respectively, with one distinct IDAT identifier per profile and zero exact IDAT overlap. This reproduces the existing within-study array-separation result; it is not a new classifier calculation.

The new cross-accession comparison matched these primary workbook identifiers against the separate Lyskjær validation deposition, E-MTAB-9875. Its 1,972 SDRF assay rows resolve to 986 array identities, each with one red and one green channel file. They carry 986 distinct accession-local `Characteristics[individual]` labels, with no label linked to multiple arrays. None of these 986 array identifiers occurs in either Koelsche list. Thus the crosswalk finds **zero identical-array reuse** between E-MTAB-9875 and the original 1,505 profiles. It does not exclude re-arrayed material or other specimens from a common patient under different identifiers.

| Identity comparison | Left profiles/arrays | Right profiles/arrays | Exact shared IDAT identifiers |
| --- | ---: | ---: | ---: |
| Koelsche reference vs validation, existing separation reproduced | 1,077 | 428 | 0 |
| Koelsche reference vs E-MTAB-9875, new cross-accession audit | 1,077 | 986 | 0 |
| Koelsche validation vs E-MTAB-9875, new cross-accession audit | 428 | 986 | 0 |

`profile-array-crosswalk.tsv` contains the full 2,491-row metadata crosswalk. `cross-accession-array-overlap.tsv` is header-only because no exact cross-accession matches were found; successful retrieval and complete expected row counts distinguish this negative result from an access failure. `identity-results.json` preserves the counts and actual available field names. Sample labels such as `REFERENCE_SAMPLE` and `Case_` are accession-local labels and were not treated as patient identifiers shared across sources. IDAT normalization removed only the red/green channel filename suffix when reading the SDRF, preserving chip and array-position identity.

# Interpretation for the methylation manuscript

The source authors report distinct patients between their reference and validation sets. We have not discovered evidence contradicting that statement. The independent audit verifies separation at the array-identifier level, including the separate E-MTAB cohort, but public source fields do not enable a patient-key audit across all cohorts. A classifier's reuse of an original measured validation set remains a secondary reanalysis, even when those validation patients are author-reported to differ from training patients.

E-MTAB-9875 is a concrete separately deposited measured cohort whose array identifiers do not overlap this reanalysis. It therefore remains a candidate for a future separately specified transport analysis. This checkpoint does not evaluate its predictions, reconcile all diagnostic taxonomies, establish blinded reference diagnoses or newly prove patient independence. The Lyskjær paper reports 986 deposited profiles but three quality-control failures before its 983-profile analysis; metadata crosswalk counts must not be substituted for an analyzed-performance denominator. Its original integrated diagnostic review and classifier version also remain relevant to any subsequent question.

The consequential missing evidence is a shared deidentified patient/specimen crosswalk, or equivalent author-verified cross-study linkage, to independently test different-array or repeated-specimen reuse across studies. The original workbooks supply specimen manifestation/location and array labels but no common patient key. E-MTAB's individual labels solve within-accession naming, not cross-accession identity. No probabilistic patient matching was attempted from age, anatomical site or diagnosis; those attributes cannot establish identity and would invite false joins.

## Exact replacement for the manuscript identity paragraph

> The original study reports that all reference and validation samples came from different patients. We independently confirmed that the primary workbooks contain 1,077 unique reference and 428 unique validation IDAT identifiers with no exact overlap; the public workbooks do not provide a shared patient key for an independent patient-level linkage audit. Excluding the previously identified shared physical-chip prefix retained 118 fusion-compatible profiles and the same three class discordances. In a separate metadata-only audit, all 986 array identifiers in the E-MTAB-9875 validation deposition were distinct from both original lists. This establishes array-level separation, not the absence of different-array specimens from a shared patient across studies. Taxonomy and diagnostic adjudication must also be reconciled before using a separate cohort for score transport.

The retained 118-profile/chip-exclusion statement above is existing frozen evidence, not recomputed at this checkpoint. The new audit does not repeat the 120-profile loss calculation or alter its inclusion rules. Update the earlier addendum's identity assessment consistently so the source's explicit patient statement is not lost.

# Sources, reproducibility and access

- [Koelsche primary article](https://doi.org/10.1038/s41467-020-20603-4); [primary XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7819999/fullTextXML). The patient statement is in Methods, immediately before the discussion of pathological examination and validation-study recruitment.
- [Reference workbook, Supplementary Data 1](https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-020-20603-4/MediaObjects/41467_2020_20603_MOESM4_ESM.xlsx): SHA256 `85a148285ef1812d6ca8d68c839a2d64f73cebb6f8ebfa95844e3d85b5c03bb9`, matching the frozen analysis input.
- [Validation workbook, Supplementary Data 3](https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-020-20603-4/MediaObjects/41467_2020_20603_MOESM6_ESM.xlsx): SHA256 `605dd1ba7af9845e53f5db51c11b8d7e36b0076ade3dd5ba97edccbdf32ceb36`, also matching the frozen input.
- [Lyskjær primary XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8185366/fullTextXML); [E-MTAB-9875 SDRF](https://www.ebi.ac.uk/biostudies/files/E-MTAB-9875/E-MTAB-9875.sdrf.txt): SHA256 `c6ffc854493f95d3b1c70bc18e0862abf269ea889e7ca2db153d435c80adc216`, 816,169 bytes. The SDRF is metadata, not array measurements.
- `audit_identity.py` captures sources with a 2 MB cap per metadata request and records response identities. `compare_metadata.py` checks fixed hashes, verifies channel pairing and expected row counts, and reproduces the crosswalk. Python's standard library and existing openpyxl were used; no package installation was needed.

The browser-facing NCBI GEO page and PMC page returned reCAPTCHA responses through the web retrieval tool; a separate Nature find call returned an internal error. These are access failures, not negative evidence about source availability. Primary Europe PMC XML, publisher workbooks and BioStudies SDRF were successfully retrieved. A preliminary console Unicode-encoding failure affected printing only and was resolved by running Python in UTF-8 mode; it was not interpreted as missing source data. No browser automation or UI was used.

# Portfolio identity

This methylation correspondence is not identified as the submitted Cancer Genetics letter. The coordinator independently confirmed the submitted item as the CSPG4 Letter, CG-D-26-00971, resubmitted September 25, scientific candidate `744170c2f327aa76c3aed0a9d36fe2fa7fc0c985`. That submission identification is coordinator-provided evidence, not a fresh submission-system check by this worker. The inspected repository also contains an older CSPG4 Cancer Genetics preparation package explicitly marked as preparation without submission; it cannot override the later submission record. No contact or submission action was taken.
