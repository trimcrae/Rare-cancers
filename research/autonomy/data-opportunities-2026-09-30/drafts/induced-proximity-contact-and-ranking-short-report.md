# Native structures expose sensitivity to contact definitions and sampling units in induced-proximity design

## Abstract

Protein–protein contact counts can be used to prioritize induced-proximity designs, but their interpretation depends on the geometric representation and the unit being counted. We reanalysed a frozen 22-entry structural census using freshly retrieved coordinates, then evaluated a complete public DeepTernary release without rerunning model inference. All 101 saved chain-pair contact records, each evaluated in two directions, reproduced under the original contact definition. Nevertheless, a fixed floor of 12 contact points failed in at least one direction for 6 of 15 degrader or molecular-glue pairs nested in eight PDB entries. Four entries contained a failing copy; three had every evaluated copy fail. Replacing the side-chain centroid with Cβ increased pair failures to 7 of 15. An all-pair audit recovered omitted zero-contact, ligand-spanned pairs in the single TCIP structure, 9MZA. Pooling two separate recruited p300 copies changed its floor decision. In 22 released PROTAC cases, the mean top-ranked DockQ was 0.429, compared with 0.706 for the best of 40 predictions selected using the native reference. These measurements support explicit reporting of geometric definitions, structural nesting, molecular-body choices and native-reference selection. They do not calibrate pharmacological efficacy or validate an EMC treatment.

## Introduction

Public ternary-complex structures provide experimental coordinates for examining computational design rules. They are particularly useful when a proposed induced-proximity strategy lacks a measured ligand, target-engagement assay or cellular response. Structural measurements can test whether a proposed geometric requirement is satisfied by deposited examples, even when they cannot establish the efficacy of a new molecule.

Two distinctions matter. First, an operational contact point is not necessarily an atom, residue, energetic interaction or productive interface. A residue can contribute more than one query point, and close points can be excluded from a contact count by a separate clash convention. Second, copies within a PDB entry, related entries within a structural cluster and predictions generated for one target are nested observations. Counting them as independent evidence can conceal dependence on a chosen representation or sampling budget.

We therefore asked a bounded question: how stable are the decisions produced by a fixed contact floor when the coordinates, query representation and counting unit are made explicit? We also examined the difference between selecting a predicted pose by its released rank and selecting it with knowledge of the native structure. These are methods questions about existing measurements, rather than claims that a geometric gate predicts degradation, transcriptional activity or therapeutic selectivity.

## Methods

### Frozen census and fresh coordinates

We preserved the repository's original census and producer before analysis. The census contained 22 entries and 101 saved chain-pair records. Each pair has a forward and reverse profile. We retrieved the corresponding current PDB mmCIF files and retained source sizes and SHA256 digests. The original contact definition used Cα and the side-chain heavy-atom centroid as query points, with a Cα-only fallback when a side-chain centroid was unavailable. Distances were measured to the nearest partner heavy atom. Query points below 3 Å were assigned to a hard category, those from 3 to below 3.6 Å to a soft category, and those from 3.6 through 6 Å to contacts.

The census's protein-chain eligibility rule is atom-based: a chain must contain at least 40 ATOM heavy-atom records assigned to its frozen amino-acid residue-name set, and these records must comprise at least half its ATOM heavy-atom records. The set includes the canonical residue names and MSE, SEC, PYL, HSD, HSE and HSP. This is not a requirement for 40 amino-acid residues. Exact coordinate and filtering policies are preserved in the executable source.

We evaluated the fixed contact floors 0, 6, 10, 12, 16, 20 and 24. A pair failed a floor if either directional contact-point count was below that floor. This is a count-only result, not an evaluation of every condition in a complete design pipeline. Sensitivity analyses replaced the centroid with Cβ and counted all query points within 6 Å, including the original hard and soft categories. We separately measured contacting residues using actual heavy atoms at 4.5 and 6 Å.

The primary degrader/glue subset comprised 15 saved pairs nested in eight entries: 5FQD, 5T35, 6BN7, 6BOY, 6H0F, 6HAX, 6SIS and 7Q2J. We reported pair failures, entries with any failing copy and entries with every evaluated copy failing. Leave-one-entry-out fractions describe this finite collection; they are not confidence intervals for a population of active molecules.

### Recovering omitted pairs and defining molecular bodies

We enumerated all eligible protein-chain pairs before removing zero-contact profiles. Ligand spanning required a non-buffer ligand with at least 12 heavy atoms, including at least three atoms within 4.5 Å of each protein chain. This geometric rule does not establish a ligand-mediated causal mechanism. Curated constitutive pairs remained excluded from induced-pair summaries.

For 9MZA, we preserved the distinction between the A/C lysine-acetyltransferase body and the two separate recruited p300 copies, B and D. Body-level counts retained source-chain identities. In this structure, each source chain had at most one target profile with any relevant point or heavy-atom contact within 6 Å, permitting exact union counts without double counting. Deposited assembly metadata was recorded; the reported comparisons use deposited coordinate chains.

### Complete released structural and score controls

We acquired the complete DeepTernary v1.0.1 output ZIP, verified its publisher SHA256 and retained its members. The frozen PROTAC list contains 22 cases from 14 PDB entries and seven author-defined clusters. Native coordinates were evaluated using the same fixed geometric definitions. Six PDB entries overlap the original eight-entry degrader/glue subset, so these collections are not independent replications. An additional released native case, 7PI4_A_D_7QB, was evaluated separately because it lies outside the frozen 22-case score list.

Released PROTAC and molecular-glue score tables were parsed in full. Because score rows lack case identifiers, joins to case and cluster labels assume the verified author list order. We retained that assumption rather than claiming an independently identified mapping. PROTAC summaries compare the released top-ranked prediction with the best DockQ among 40 predictions, using the native reference. The molecular-glue table uses one prediction per case under a different, bound-task setup. Their results are not a matched performance comparison. Equal-entry and equal-cluster averages were reported alongside case-weighted means.

Finally, we reanalysed 32 previously completed poses from two known-pocket systems. Ordinary medians average the two middle observations. Exact finite-subset calculations describe the expected native-reference maximum among saved subsets; they do not estimate success for future seeds or provide a deployable ranking rule.

## Results

### Contact decisions changed with the representation and denominator

The fresh-coordinate replay reproduced the saved contact counts for all 101 chain-pair records. This agreement concerns the original contact counts; it does not assert identical reproduction of every hard or soft category. All coordinate retrievals and calculations completed without a recorded pair-level error.

In the original degrader/glue subset, the numbers of pairs failing at least one directional count were 0, 1, 1, 6, 7, 9 and 15 at floors 0, 6, 10, 12, 16, 20 and 24, respectively. At the floor of 12, the pair-weighted fraction was 6/15 (40.0%), the fraction of entries with any failing copy was 4/8 (50.0%), and the fraction with every evaluated copy failing was 3/8 (37.5%). These denominators answer different questions.

| Fixed contact-point floor | Failing original degrader/glue pairs | Total pairs |
|---:|---:|---:|
| 0 | 0 | 15 |
| 6 | 1 | 15 |
| 10 | 1 | 15 |
| 12 | 6 | 15 |
| 16 | 7 | 15 |
| 20 | 9 | 15 |
| 24 | 15 | 15 |

Replacing side-chain centroids with Cβ increased floor-12 failures to 7/15; four of eight entries then had every copy fail. Including the original hard and soft query points in the within-6-Å count reduced failures to 2/15. Thus both the query location and the rule that separates contacts from closer points affected the result. In the original representation, leave-one-entry-out pair fractions ranged from 30.8% to 54.5%. This range reflects structural nesting within the observed collection.

The released PROTAC native-coordinate collection yielded 13/22 floor-12 failures, with any-copy failures in 9/14 entries and every-copy failures in 7/14. Six of seven author clusters contained a failing case, whereas only two had every case fail. Removing one author cluster at a time gave case-weighted fractions of 55.56–65.0%. Because six PDB entries overlap the first collection, this is an extension of the control set rather than an independent replication. The additional 7PI4 control had 13 and 16 directional contact points and passed floor 12, but failed floors 16, 20 and 24. It remains outside the 22-case denominator.

### A zero-contact selection rule concealed a molecular-body ambiguity

The all-pair audit evaluated 220 eligible protein-chain pairs before zero-contact selection. In 9MZA it recovered ligand-spanned A–B and C–D pairs omitted from the saved nonzero census. Their minimum protein heavy-atom separations were 7.14 and 7.70 Å, and both had zero proxy contacts. A–D and B–C had directional contact counts of 6 and 7. All four induced-eligible pairs failed floor 12. The constitutive A–C pair was excluded from that induced summary.

Treating A/C as one body and either p300 copy individually preserved counts of 6/7 and therefore the failure. For A/C versus B, the actual heavy-atom contacting-residue counts were 4/2 at 4.5 Å and 5/5 at 6 Å. The corresponding counts versus D were 4/3 and 5/6. These are residue counts, distinct from proxy-point counts.

Pooling B and D changed the proxy counts to 12/14 and made the count-only floor pass. However, B and D are separate p300 copies with a minimum heavy-atom separation of 25.35 Å. Pooling them changes the counted molecular body; it does not demonstrate that either recruited copy independently satisfies the floor. The census contains one TCIP entry, 9MZA. Its broader induced-transcriptional category contains six entries and should not be described as six TCIP examples.

### Native-reference pose selection changed the apparent benchmark performance

Across the 22 released PROTAC cases, mean top-ranked DockQ was 0.4287, whereas the mean best-of-40 DockQ was 0.7062: a mean difference of 0.2775. At DockQ cutoffs 0.23, 0.49 and 0.80, top-ranked counts were 17, 9 and 1, compared with native-reference best-of-40 counts of 22, 19 and 7. Allowing the first two ranked predictions recovered an acceptable DockQ in 21 cases; the remaining case's first acceptable prediction had rank 37. The equal-PDB and equal-author-cluster top-ranked means were 0.3755 and 0.3745, respectively.

The 94-case molecular-glue table used one prediction per case, so its top-ranked and oracle values were identical. Mean DockQ was 0.2493, and 33 cases met the 0.23 cutoff. Equal weighting of 44 author clusters gave a mean of 0.2087 and an acceptable fraction of 30.38%, compared with the case-weighted 35.11%. This comparison exposes a weighting choice, not a matched contrast with the PROTAC task.

[Released embedded configurations](../deep-analysis/results/DeepTernary-released-validation-test-config-final.json) point both test and validation to the same PROTAC22 list and, separately, the same molecular-glue test_all list. These are released benchmark/validation summaries rather than a demonstrated blind test. Thirteen molecular-glue rows disagreed between the released legacy hit field and the DockQ cutoff. Distinct metric definitions can produce such disagreements. The pinned current prediction source additionally passes RMSD arguments in an order opposite its classifier signature, and its classifier logic is not equivalent to canonical CAPRI criteria. The historical executable producing the released tables is unresolved; we did not repair historical hit labels or attribute all disagreements to current source code.

The two saved 16-pose systems had ordinary DockQ medians of 0.4087 and 0.4228, compared with upper-middle order statistics of 0.4143 and 0.4421. For the second system, expected native-reference maxima among uniformly chosen saved subsets of 1, 2, 4, 8 and 16 poses were 0.4318, 0.6086, 0.7488, 0.8175 and 0.8388. These finite calculations demonstrate selection-budget dependence. They do not estimate future-seed success, affinity or a usable prediction-ranking procedure.

## Discussion

A fixed contact floor produced different decisions when we changed the query representation, included closer query points, aggregated structural copies or selected poses using their native reference. The contribution is an executable audit of these choices using deposited measurements and complete released score tables. It does not establish that the tested floor is intrinsically wrong, identify an optimal replacement, or show that a rejected design is pharmacologically inactive.

The original census and released structural controls are enriched for deposited complexes. They do not form a prospective activity-labelled cohort. A separately completed PROTAC source audit recovered active and inactive entries, missing quantitative endpoints and incompletely reported controls, but those assay labels could not be matched to the structural collection. Missing measurements cannot be treated as zero activity. Consequently, these analyses provide no sensitivity, specificity or efficacy calibration for the geometric gate.

The strongest transferable recommendation is to report the exact coordinate representation, directional rule, molecular-body definition, structural nesting and selection budget alongside a geometric decision. An interface floor may help organize candidates while requiring independent measurements of binding, ternary-complex formation, functional response and selectivity. For proposed EMC interventions, the present results supply methods controls rather than measured target engagement or therapeutic benefit.

## Data and reproducibility

The frozen producer is [nr4a3_induced_interface_census.py](../../../modalities/nr4a3_induced_interface_census.py), Git blob 31ec026e05aa336c4e7d4f1f03440306c35aadf2. The frozen census blob is b184a9d23198d7c56a6a69a87d60a2042ba5b67a. DeepTernary source is pinned to 827821dccca31a5918bd0355e2d6bf70c072b6dd; its complete 151,480,895-byte output ZIP has SHA256 1eb43229480459730f7993f3c22ac42e9a1a5aee60d747088eb35aac4f3d18c3. The complete release contained native coordinates and score tables but no released prediction poses for new coordinate-based rescoring.

Executable scripts, source receipts and durable JSON results accompany the report: [fresh coordinates](../deep-analysis/results/structure-coordinate-actual.json), [all-pair audit](../deep-analysis/results/structure-all-pairs-actual.json), [complete released scores](../deep-analysis/results/released-ternary-complete-score-analysis.json), [body and saved poses](../deep-analysis/results/structure-body-and-saved-pose-analysis.json), and [additional native control](../deep-analysis/results/extra-released-native-structural-control.json).

Successful executions were run 36866309548/job 110382565725 (fresh census), 36880462046/job 110430876033 (all-pair audit), 36882102233/job 110436284388 (complete release/native geometry), and [36900530648](https://github.com/trimcrae/Rare-cancers/actions/runs/36900530648)/job 110498362126 (score/body/saved-pose/extra-native replay). Failures in other jobs of a shared workflow do not change these successful job receipts.

## References

1. Xue F, Zhang M, Li S, et al. SE(3)-Equivariant Ternary Complex Prediction towards Target Protein Degradation. Nature Communications. 2025;16:5514. [doi:10.1038/s41467-025-61272-5](https://doi.org/10.1038/s41467-025-61272-5).
2. Basu S, Wallner B. DockQ: A Quality Measure for Protein–Protein Docking Models. PLoS ONE. 2016;11:e0161879. [doi:10.1371/journal.pone.0161879](https://doi.org/10.1371/journal.pone.0161879).
3. Nix et al. A Bivalent Molecular Glue Linking Lysine Acetyltransferases to Oncogene-induced Cell Death. bioRxiv. 2025. [doi:10.1101/2025.03.14.643404](https://doi.org/10.1101/2025.03.14.643404).
