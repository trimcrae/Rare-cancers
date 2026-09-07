---
id: DOC-TRIAL-REFERENCE-REPAIR-20260905
title: A frozen diagnosis and cohort reference pack for trial discoverability
kind: memo
status: live
date: 2026-09-05
last_verified: 2026-09-05
purpose: Deliver independently checkable labels and the next specific sampling repair before ranking.
scope: Saved ClinicalTrials.gov corpus, three diagnoses, metadata sample and separate challenge anchors.
audience: [maintainers, autonomous research agents]
---

The round delivers 49 unique diagnosis–trial judgments covering 37 distinct trials: 33 metadata-sampled current pairs and 18 separately frozen challenge pairs, with two overlaps retained in both set memberships. All selected cases have a judgment, including unresolved cases. These are single-reader labels with exact source pointers, not an independently verified gold standard or patient eligibility decisions. No rankings were run.

The selection and protocol were frozen before criteria inspection. `freeze-receipt.json` records their hashes at 17:41:35 UTC. The algorithm orders NCT IDs by SHA256 of `20260905|diagnosis|stratum|NCT ID` and selects the first four, or all records if fewer. Strong ordinary retrieval includes all five saved condition/ordinary/eligibility/unquoted query variants. Molecular-only and parent-only are disjoint within diagnosis. The sole SS molecular-only current record is preserved without replacing its three absent sample slots. Each challenge anchor was crossed with all three diagnoses before reading criteria. Anchor knowledge and the original diagnosis/fusion definitions were disclosed; no previous `evidence.json`, `curate.py`, or pilot verdict was read.

| Diagnosis | Stratum | Frame pairs | Sample pairs | Single-reader diagnosis-scope labels |
|---|---|---:|---:|---|
| EMC | Ordinary | 48 | 4 | 3 exclusions; 1 insufficient |
| EMC | Molecular-only | 10 | 4 | 1 fusion-class compatible; 2 exclusions; 1 insufficient |
| EMC | Parent-only | 1021 | 4 | 2 broad compatible; 2 exclusions |
| DSRCT | Ordinary | 29 | 4 | 3 explicit compatible; 1 exclusion |
| DSRCT | Molecular-only | 10 | 4 | 1 broad compatible; 2 exclusions; 1 insufficient |
| DSRCT | Parent-only | 1009 | 4 | 1 broad compatible; 3 exclusions |
| SS | Ordinary | 51 | 4 | 4 explicit compatible |
| SS | Molecular-only | 1 | 1 | 1 broad compatible with unresolved additional biomarker |
| SS | Parent-only | 992 | 4 | 3 broad compatible; 1 exclusion |

Counts are descriptive label counts in this fixed sample, not precision estimates. A broad compatibility label records the tumor/histology scope; it does not establish required biomarkers, a currently open compatible cohort, or suitability for an individual. The snapshot definition of current is recruiting, not-yet-recruiting, or enrolling-by-invitation. Several records are not yet recruiting or have old status-verification months. The reference retains those fields. NCT05071209 is active-not-recruiting and appears only as a challenge anchor; it cannot support a current-trial availability claim. Challenge and probability-style metadata sampling are never pooled as a prevalence denominator.

The labels contain useful positive and control distinctions. EMC ordinary retrieval sampled an explicit EMC exclusion and three unrelated indications, including an EMC acronym referring to a medical center. DSRCT and SS ordinary samples contain named positive cohorts. Parent-only samples include broad sarcoma, surgical imaging, surveillance/management and biomarker-conditioned solid-tumor scopes, alongside closed carcinoma/AML lists and explicit sarcoma exclusions. Registered interventional status alone does not mean a systemic antitumor treatment trial; `oncology_task_domain` preserves that distinction.

The challenge cases expose the specific semantics the next benchmark needs to test:

- NCT05918640 supports FET-class EMC compatibility in phase 1 for matching variants, while phase 2 is Ewing-only. DSRCT has an explicit conditional enrollment hold until a non-DSRCT safety threshold is met; its release is unknown. Score that hold as unresolved, not as a permanent negative or a confirmed open positive.
- NCT05071209 explicitly names EWS-WT1 in an EWS-fusion route, supports only matching EWS-containing EMC variants through that class, and offers a separate additional-DDR-alteration route. Its historical availability remains separate.
- NCT06571734 has a translocation-associated STS cohort, explicitly exemplified by SS, with **greater than two** prior antineoplastic lines. EMC/DSRCT are class-level candidates, requiring pathology/protocol acceptance. Bone metastasis does not convert an STS diagnosis into the separate bone-sarcoma cohort.
- NCT05135975 includes DSRCT and other STS in maintenance stratum A at BR2 or later, but its saved criteria explicitly defer additional exclusions to a protocol not reviewed here. All three labels are provisional and excluded from binary scoring pending that protocol review.
- NCT05687136 lists SS18 **mutation** among biomarker options and requires PI approval; the saved wording does not explicitly establish SS18::SSX fusion acceptance. All three diagnoses have only conditional broad-tumor scope. Biomarker list logic and assay/variant acceptance remain unresolved.
- NCT06094101 restricts screening to rhabdomyosarcoma, Ewing and SS. Generic fusion-positive language cannot expand that list to EMC or DSRCT. SS still requires successful individualized vaccine manufacture and the specified remission/local-control state.

The full saved inclusion/exclusion text, descriptions and arm/cohort text were read for all 37 records; the packet preserves them. This is not a claim to have read complete external protocols. Other concrete uncertainties include Ewing-like classification for EMC in NCT07188532, DSRCT site/histology scope in NCT06526897, part-specific KRAS requirements in NCT07030959, PRAME threshold versus HLA requirements in NCT07686367, and whether a B7-H3-defined CNS cohort accepts SS in NCT07698899. Broad criteria need not be scored as unconditional positives. Exact supporting excerpts and full-module pointers are in `reference.json`; recorded constraints are concise summaries and do not replace complete criteria.

This is enough for an independently checked, bounded case benchmark of diagnosis/cohort scope. It is too sparse for a strong ranking-benefit or review-burden estimate over the whole parent frame. In particular, the four EMC ordinary cases contain no positive oncology scope, and SS has only one molecular-only current case whose fusion interpretation is unresolved. Those are sampling and label-resolution issues, not evidence that the paper prospect is defeated.

The precise next repair is to enumerate the **149 current ordinary-or-molecular diagnosis pairs** in the frozen metadata: 58 EMC, 39 DSRCT and 52 SS. Twenty-one were judged in the metadata sample. Four additional pairs already have challenge judgments (DSRCT:NCT05135975, DSRCT:NCT05918640, SS:NCT06094101, SS:NCT06571734), leaving **124 unjudged pairs** after reuse; two reused DSRCT anchor judgments still require missing-exclusion/hold resolution. Preserve all 33 original sample memberships. If workload across parent retrieval is the endpoint, prospectively freeze up to 40 parent-only pairs per diagnosis using the existing hash order (the current four plus the next 36), or enumerate a separately justified bounded parent subframe. Do not choose replacements by label or rank. Freeze the expansion contract before further eligibility reads. Increasing sample size does not repair missing full protocols or ambiguous biomarkers; resolve or retain those separately.

The next fresh ranking worker should use competent matched-information ordinary/hierarchy baselines and molecular augmentation only after coordinator verification and endpoint freeze. Separate named/defining-fusion scope, broader class scope, broad tumor scope with additional requirements, direct restrictions and unresolved gates. A tiny fixed-case comparison may be reported as such; global recall and full-corpus precision are unavailable because unjudged records remain unjudged. Training or tuning on these labels would require a separate evaluation set. No baseline ordering, scores or ranking performance is contained in this round.

Validation rebuilt all 6182 corpus metadata records from 112 compressed registry pages across 24 query manifests, confirming IDs, memberships, types, statuses, page counts, compressed hashes and decoded hashes. The reference assembler resolved source pointers, checked 95 exact excerpts with character offsets, matched review-packet records against raw records, verified all selection/protocol hashes and accounted for every selected pair. These are reproducibility checks; separate scientific verification remains the coordinator's task. Normal preflight is reserved for integration.

From the repository root, with the supplied Python runtime, run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 research/autonomy/trial-reference-repair-2026-09-05/freeze.py
& 'C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 research/autonomy/trial-reference-repair-2026-09-05/verify_frame.py --check
& 'C:/Users/mcrae/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 research/autonomy/trial-reference-repair-2026-09-05/build_reference.py --check
```

`author_labels.py` reproduces the authored judgments; `prepare_packet.py` reproduces the raw review packet from allowed sources. Run-record and manifests record timing and final hashes. No background process, nested worker, paid API, GPU job, manuscript edit, clinical registry edit, commit or publication was initiated.
