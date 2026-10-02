# Fixed-prediction methylation score transport addendum

Date: 2026-10-02. Source revision: `da49c4e836533253825587f83656675dac4c913b`, trimcrae/Rare-cancers. This is a post hoc descriptive sensitivity, not a preregistered analysis, new model fit or independent diagnostic validation.

## Executed arithmetic

The values below were calculated in JavaScript in memory from the source-pinned JSON results. The accompanying Python reproduction script has not been executed in this worker session.

| Weighting and loss | Raw | Temperature transformed |
|---|---:|---:|
| Profile-weighted NLL, existing | 0.43886850867822524 | 0.4359242413670505 |
| Equal-class NLL, newly calculated | 1.0742871213223848 | 1.8437918075204678 |
| Profile-weighted Brier, existing | 0.11232166666666671 | 0.03751010299478826 |
| Equal-class Brier, newly calculated | 0.2365079526109961 | 0.19326224730468514 |

Equal-class means are the arithmetic mean of the 12 saved class-specific mean losses. All use the existing epsilon 1e-6 predictions. Four classes supply 91/120 profiles; three classes have one profile each. No interval is inferred. Equal-class weighting changes the estimand rather than correcting the original one.

Total transformed NLL is 52.31090896404606. The three discordant profiles contribute 98.45830919609586% of it; the zero-vote DFSP profile contributes 78.72747192263749%. Their losses are 41.18305616714582 (VALIDATION_SAMPLE 262), 7.205009591657335 (405) and 3.1163707323055325 (417). These are direct negative logs of the saved target probabilities. No case was removed from the summaries.

The already-preserved original-score-below-0.9 stratum contains seven fusion-compatible profiles. Its NLL rises 3.2510634604397297 to 7.359025978889228 and Brier rises 0.5520714285714287 to 0.6285940180085888. Five profiles are assigned after transformation, four concordantly. This is an existing stratum, not a newly optimized subset.

## Manuscript-ready addition

Score-transport conclusions also depended on case weighting. In a post hoc sensitivity assigning equal weight to each of the 12 fusion-compatible classes, mean class-specific negative log likelihood increased from 1.0743 to 1.8438, although the corresponding Brier score decreased from 0.2365 to 0.1933. These descriptive summaries used the same fixed predictions and input floor of 10^-6. Four classes supplied 91 of the 120 profiles, and three classes had only one profile each; equal-class weighting therefore addresses a different, highly uncertain target distribution. Improved average Brier score did not imply uniformly improved scores across classes.

## Exact corrections and boundaries

- Replace “added a frozen epsilon” with “floored input votes at a fixed epsilon and normalized them.” `methylation_final_replay.py` uses `np.clip(raw, eps, 1)`, not additive smoothing.
- Replace “without adding discrimination” with “without changing any maximum-score class assignment.” Multiclass temperature scaling preserves within-profile class ordering, not necessarily across-profile class-score ordering. Mathematical illustration only: at T=0.3115089490681155, class-1 values in `[.400,.399,.201]` and `[.390,.305,.305]` change from .400>.390 to .4757839568856305<.5239884338570159. This is not measured data.
- Add “The common grouped-validation panel did not include the EMC class.” Its 658 profiles span 23 of 65 classes; EMCS is absent.
- Supplier and chip bootstrap intervals are conditional on saved predictions, excluding model refitting variability and unmeasured patient clustering. They do not establish a causal technical batch effect.
- Brier and NLL are aggregate proper losses, not calibration-only measurements; improved loss alone does not establish clinical calibration.

## Identity and overlap assessment

The frozen external result records 1,077 unique reference IDAT identifiers, 428 unique validation identifiers, zero exact IDAT overlap, and one shared chip prefix. These establish array identifier separation, not patient independence. The existing chip exclusion removes four validation profiles; the fusion subset drops to 118 while retaining all three discordances. Different arrays or biopsies from one patient remain unresolved.

BioStudies directly confirms that E-MTAB-9875 is the separate 986-profile UCL/RNOH validation deposition, using 450K and EPIC arrays. No cross-accession sample identifier join or patient-disjointness verification was executed. API: https://www.ebi.ac.uk/biostudies/api/v1/studies/E-MTAB-9875 . Study: https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-9875 .

## Focused primary-literature comparison

- Koelsche et al. 2021 is the reused GSE140686 source, not a new external patient cohort: https://www.nature.com/articles/s41467-020-20603-4 .
- Lyskjær et al. already evaluated 986 profiles, including 820 within the classifier's represented diagnoses, and reported variable coverage and class performance. External validation itself is not the present novelty: https://pmc.ncbi.nlm.nih.gov/articles/PMC8185366/ .
- Miettinen et al. 2024 evaluated 619 specimens and used additional workup after unexpected methylation results. Its integrated diagnosis illustrates why incorporation effects and unrepresented entities matter: https://pmc.ncbi.nlm.nih.gov/articles/PMC10842611/ .
- Jäger et al.'s sarcoma v13.1 preprint reports 4,377 reference profiles, expanded hierarchical classes and 1,547 validation profiles. Its different taxonomy and class-level metrics are not a direct benchmark for the present legacy-taxonomy experiment. Training accession GHGAS64406795843199 requires a data-transfer agreement according to its data-sharing statement: https://www.medrxiv.org/content/10.1101/2025.06.30.25330543v1 .
- A 2026 single-center comparison contains 40 samples from 34 patients and demonstrates version-dependent coverage. Sample/patient denominators and classifier version must accompany transport claims: https://link.springer.com/article/10.1007/s00432-026-06494-w .

Citation identity warning: PubMed40630595 links an UpdateIn entry to PMID41349541 / DOI10.1016/j.ccell.2025.11.002. Direct inspection identifies that publication as “Advancing CNS tumor diagnostics...” rather than the sarcoma paper. Do not substitute it as the sarcoma version of record: https://pubmed.ncbi.nlm.nih.gov/41349541/ . A correct sarcoma version-of-record identity was not established here.

The defensible contribution is paired provenance partitions with matched training support and score-scale/case-weighting sensitivity in a frozen taxonomy. This search does not establish a first-in-literature claim. A computational methods report is better supported than new diagnostic-validation claims. A patient-linked, independently adjudicated, taxonomy-reconciled cohort remains the consequential validation gap.

## Source files

All under `research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/` at the frozen revision:

- `methylation-hallmark-fusion-score-transport-final.json`
- `methylation-hallmark-fusion-selected-cases-final.json`
- `methylation-corrected-full-support-actual.json`
- `methylation-processed-external-validation-final.json`

Code inspected: `deep-analysis/methylation_final_replay.py`, `methylation_full_geo.py`, and `methylation_transfer.py` in the same source directory. No fits were rerun.
