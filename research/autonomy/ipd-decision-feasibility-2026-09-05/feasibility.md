---
id: DOC-IPD-DECISION-FEASIBILITY-20260905
title: Reconstruction decision stability and targeted information recovery
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Decide whether a distinct reconstruction-uncertainty contribution merits development.
scope: Bounded primary prior-art screen and explicitly synthetic feasibility experiment.
audience: [maintainers, autonomous research agents]
---

**Outcome: one remediable uncertainty; retain a narrowly defined development prospect.** Does an exhaustive or conservatively bounded compatibility-set method provide useful decision certification and reduce additional data requests on realistic, known-IPD benchmarks, beyond competent point reconstructions and a simple distance-from-significance-threshold rule? The present evidence supports testing that question. It does not establish a standalone paper, and it does not defeat the question merely because the realistic benchmark remains to be run.

The generic proposition that reconstruction uncertainty can affect inference is already occupied. The potentially distinct contribution is an auditable certificate of whether a specified secondary study decision is determined by the released information, coupled to a query policy that requests the smallest useful additional risk-set information. This is a methods contribution with broad evidence-synthesis utility and weak EMC specificity. No sparse EMC treatment comparison was attempted.

## Concrete target and interpretation

For a fixed pair of right-censored study arms, the reference target is the **finite-sample ordinary two-sided logrank result computed from the original observed IPD**. Define the reporting decision as `p < 0.05`, fixed before the counterexample search. This is a statistical audit threshold, not a clinical-benefit threshold. The underlying test concerns equality of survival distributions; neither the reference decision nor its reconstruction establishes efficacy. Matching the original decision is distinct from controlling population type-I error.

Given released summaries R, let F(R) contain every compatible event/censor record. Compute the minimum and maximum ordinary logrank p-value over F(R). Report stable rejection, stable non-rejection, or unresolved. An unresolved result can be accompanied by two actual compatible witnesses with different decisions. These extrema are **compatibility bounds, not confidence limits or a posterior distribution**. A proof of completeness or an outer bound is essential: agreement among a few sampled reconstructions cannot certify stability.

The pilot supplies exact KM steps, sample sizes, event totals and five risk-table times, with censor ticks and the original p-value withheld. If that exact decision's p-value is already published, requesting it or using it directly is preferable; [Irvine et al.](https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-020-01092-x) also establish its value as a reconstruction constraint. A future application must concern an unreported secondary comparison or statistic and retain all actually available summaries.

## Actual prior-art challenge

| Primary work | What it already establishes; remaining distinction |
|---|---|
| [Guyot 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3313891/), [Hoyle–Henley 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3198983/), [Wei–Royston 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5796634/) | Reconstruction, downstream model fitting and reconstruction accuracy are established. These are baselines, not a new contribution. |
| [IPDfromKM 2021](https://link.springer.com/article/10.1186/s12874-021-01308-8) | Its variability appendix compares logrank conclusions and bootstrap HR intervals with original data. Merely measuring decision flips is insufficient novelty. |
| [Titman 2026](https://onlinelibrary.wiley.com/doi/10.1002/sim.70474) | QP/MIQP exploits auxiliary constraints; benchmarks include HR, RMST difference and proportionality-test statistics. Changing an optimizer or testing downstream accuracy alone is insufficient. |
| [Rogula 2022](https://pubmed.ncbi.nlm.nih.gov/35128059/) | Censor ticks can replace uniform-censor assumptions. A fair benchmark must compare the same available information. |
| [RESOLVE-IPD](https://arxiv.org/html/2511.01785v1), [KoMbine](https://arxiv.org/html/2509.15371v1), [Boucher et al. PSI 2025](https://www.psiweb.org/docs/default-source/psi-conference-2025/abstracts-2025/cys07-abstract-157.pdf?sfvrsn=db1fafdb_2) | Respectively address subgroup-label ensembles, patient-assignment uncertainty, and simulation-based reconstruction uncertainty. General uncertainty propagation is already occupied. The first two are preprints; the last was inspected as a conference abstract. |
| [CCTG RMST validation](https://pubmed.ncbi.nlm.nih.gov/35779942/), [Kim 2025](https://pubmed.ncbi.nlm.nih.gov/40919413/), [KM-PoPiGo developer benchmark](https://kmpopigo.github.io/doc/datasets/index.html) | Real-data validation and broad benchmarks already exist. Reuse available benchmark material rather than manufacture another generic accuracy dataset. |

In the inspected methods, none supplied the particular combination of a complete study-specific decision bound and a minimax additional-information query. That is a bounded search finding, not proof of priority. The strongest collision is Titman's constraint formulation; an extension that simply reproduces its comparisons would not justify a paper. [Source records](sources/prior-art.json) preserve access levels, locators and limitations.

## Reproduced synthetic result

The standalone [pilot](pilot.py) generates 20 records per arm: A has 16 events and four censorings; B has 20 events. Times are arbitrary units. This is a deliberately constructed observed-data compression experiment, not a clinical trial simulation with a validated censoring mechanism. Seed 20260905 searches at most 1,000 cases and stops at the first decision ambiguity. All 32 attempted case summaries are retained; the selected case is zero-based 31. This selected example cannot estimate the frequency of ambiguity.

Because each exact curve has as many positive drops as its reported event count, every drop must contain one event. The exact drop ratios therefore identify the own-arm event risk sets. These, together with the risk table, identify censor counts in the intervening intervals. Only the order of those censorings relative to the other arm's events remains unknown. Partitioning at the pooled event times enumerates every relevant censor-order class, including event/censor tie behavior through the equivalent just-after-event class. This completeness argument applies to this restricted exact-summary setting, not rounded figures in general.

| Calculation from identical released summaries | Result |
|---|---:|
| Compatible censor-order classes | 10 |
| Minimum–maximum logrank p | 0.0437281–0.0509152 |
| Original observed-IPD p | 0.0509152 |
| Midpoint-censor reconstruction p | 0.0454414 |
| Largest RMST difference across compatible A reconstructions | 0 arbitrary time units |

The comparator is a transparent midpoint placement using **exact interval counts inferred from the same summaries**. It is an idealized perfect-fit point reconstruction, not an execution or a port of IPDfromKM or CIFresolve. Both witness curves and risk tables match exactly; the comparator nevertheless changes the reference reporting decision. RMST remains invariant because it is a curve functional: not every downstream quantity inherits censor-order uncertainty. This negative control is part of the result.

A query selected using only feasible summaries asks for A's number at risk at B's event time 11.0609546922. The policy minimizes worst-case remaining ambiguous classes, then worst p-range width, then time. Either possible answer resolves the decision: risk 5 leaves two classes with p 0.0502763–0.0509152; risk 6 leaves eight with p 0.0437281–0.0489494. The true answer is 5. Thus the query is not chosen after seeing the hidden answer. It requests one count; it does not recover the patients.

## Exact repair experiment

Build and evaluate a decision-certificate/query benchmark on known original IPD with realistically rounded/rendered releases. Start by checking the files and licenses at the [KM-PoPiGo-linked Zenodo record](https://zenodo.org/records/18320575); that endpoint returned HTTP 429 here, so its contents were not downloaded or independently verified. A fully synthetic known-IPD benchmark remains attainable without that access. Retain the current example as a development test, never a held-out success.

Freeze release transformations and test targets before evaluation: event-time/probability resolution, risk-table density, censor-mark availability and reported summaries. Include tied events and both-arm censoring. Extend enumeration to rigorously bound the full compatible set; an incomplete search returns unresolved, never stable. Compare version-pinned IPDfromKM, CIFresolve, the exact-count midpoint control, and a rule that abstains near the reconstructed p threshold. Match auxiliary information. If original p is supplied, evaluate a different prespecified secondary target rather than discarding that constraint.

Measure erroneous stability declarations against hidden observed IPD, fraction certified, bound containment, computation cost, and additional counts required to resolve ambiguity. Compare query selection with equally spaced added risk counts. Use separate development and held-out cases, report all failures and stratify by original distance from 0.05. The decisive question is useful certification or information savings **beyond simply abstaining for borderline p-values**. A threshold-crossing counterexample alone is mathematically unsurprising and not a paper. If the valid bounds are nearly always unresolved or the simple baseline is equally useful, stop the standalone route and retain the benchmark/tool result. Missing realistic validation is currently remediable; it is not an established scientific no-go.

## Validation and scope

[Independent code checks](verify_pilot.py) compare every selected class and the original/midpoint records with SciPy logrank. Maximum p discrepancy is 1.04e-16. A separate global brute-force traversal tests 123,410 four-censor multisets and recovers the same ten risk signatures and extrema. Reproduction is byte-identical. [Validation receipt](validation.json) states exact runtime versions and scope. No independent scientific review or publication readiness is claimed.

All changes are confined to this round's directory. The original contract is preserved; no shared state, manuscript, registry, preregistration, commit or publication was changed. Normal repository preflight and integration belong to the coordinator. No runner, nested worker, paid service or GPU job was launched. The bounded investigation ends at this checkpoint; no further process remains running.
