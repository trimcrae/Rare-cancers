---
id: DOC-FUSION-SOURCE-RECOVERY-20260905
title: Targeted recovery resolves two reporting gaps and one source classification
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Identify the new design-level evidence and the precise benchmark it can support.
scope: Named-source recovery checkpoint; no manuscript or validation model.
audience: [maintainers, autonomous research agents]
---

The recovered evidence supports a small, explicitly partial siRNA case benchmark, while the proposed transferable fusion-knockdown-and-both-parent-sparing benchmark remains unresolved. This checkpoint adds no qualifying family and no verified ASO design. It does not establish that the research direction is irreparable. The strongest named ASO source, Kashyap's thesis, still cannot be inspected.

The [Varley 2014 XLS](https://doi.org/10.1007/s10549-014-3019-2) is now fully parsed, including its embedded figure. Its two sheets contain sample fusion-read counts and normal-breast fusion expression, not intervention-specific parent effects. The prior supplement uncertainty can therefore be narrowed: it does not fill either missing parent outcome. Visual inspection of main Fig4b assigns approximate remaining fusion expression of 0.44 to siRNA1 and 0.49 to siRNA2; conservative image-reading ranges and original JPEG are preserved. Both are active, so their small difference is not a useful positive-versus-failure validation set. The source's table header `CTSD-IFITM1` is retained verbatim.

The [Clerc 2026 supplement](https://doi.org/10.1007/s00018-026-06254-6) supplies a 19-base junction-siRNA core matching Varley siRNA1, with dTdT residues printed. Fig1G, visually inspected on PDF page3, shows loss of the fusion-sized band alongside reduced canonical CTSD under helicase depletion. No IFITM10 response is supplied. This resolves a sequence-to-nonselective-outcome link, but not a full duplex chemistry specification, junction-specific dose, replicate estimate or quantitative parent-sparing triple. The two reports involve the same chimera, different experimental contexts and incompletely matched reagent chemistry. They cannot be counted as independent target families or a direct replication of selectivity. The helicase-perturbation qPCR panels must not be reassigned to junction-siRNA treatment.

[Ohba 2004](https://doi.org/10.1002/cncr.20468) is now inspectable as publisher text through the web tool, although direct original-byte retrieval still returns403. Its experimental siRNAs target the ABL body; fusion-junction sequences appear as prior-work comparators. Therefore its weak and nonselective designs cannot repair the junction-design negative panel. Exact Figure1A experimental sequences remain visually uninspected. The distinction between fusion in K562 and ABL in Jurkat also prevents treating its results as a same-cell parent-sparing comparison.

[Kashyap's Oxford thesis](https://doi.org/10.5287/ora-avzqyvz9q), Chapter3 Figure3.4/printed page113, remains an access/provenance gap. The exact saved PDF URL and landing page fail with403; targeted DOI/title searches return the same repository item. Indexed descriptions are not promoted to verified designs. Full sequences, matched MLL/AF4 assays, dose, replicates and unsuccessful designs remain uninspected, rather than established absent. A lawful accessible copy would still be worth examining because it could enable an ASO within-family chemistry comparison.

The useful partial estimand is narrowly stated: **among disclosed synthetic siRNA designs in a given study, does a prespecified design score order measured fusion suppression, and, separately, does it flag loss of an actually measured parent?** Retain two separate outcome tables and report their design coverage. Missing parents remain unknown. The Clerc observation can challenge a categorical claim that junction targeting guarantees CTSD sparing; it cannot estimate the probability of sparing both parents. Varley's two active designs alone cannot validate ranking accuracy. Previously recovered larger screens and negative designs should be reused if a subsequent bounded analysis tests this estimand; no broad inventory needs repeating.

Before such analysis, freeze exact sequence/chemistry strata, assay and context-specific outcomes, numerical uncertainty, simple sequence baselines and the evaluation split. Report within-study results and selection bias; keep family-level holdouts distinct from cell-line or dose splits. A useful negative finding would be that apparent ordering vanishes under extraction uncertainty or that available parent outcomes are too selected to assess discrimination. This is achievable methodological work, with contribution/novelty still unresolved. It is not authorization to silently drop parent sparing from the original transferable claim or to market siRNA observations as ASO validation.

The deliverable is this recovery checkpoint. Source bytes, derived cells, visual inspection files, retrieval failures and checks are preserved locally. Coordinator integration and normal preflight remain outstanding; no commit, manuscript, registry, publication, outreach, runner or nested agent was used. No clinical efficacy, safety or therapeutic window is established.
