---
id: DOC-TEMPO-NORMAL-ALLOCATION-20260906
title: Recover a specific public FFPE TempO-Seq normal reference before judging atlas comparability
kind: memo
status: live
purpose: Test the concrete missing normal-assay dependency for the highest-ranked atlas using a newly identified public dataset.
scope: GSE119630 human specimens, primary methods, count matrices and assay/sample provenance; no tumor-normal effect estimates or manuscript.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

Atlas remains highest-ranked. Lack of a selected next experiment did not establish an overall
impasse. A targeted TempO-Seq normal-tissue search identifies an unexamined public source:
GSE119630 (Trejo2019, PMID30794557, PMC6386473). The GEO series directly lists matched normal
colon specimens from five patients with biological/technical replicate identifiers, downloadable
GSE119630_ColonCancerReplicatesMaster.csv.gz and GSE119630_HumanGeneCountsMaster.csv.gz.
The series also contains animal tissues and cancer/cell-line/archived specimens, which must not
be called normal human tissue based on short titles. Prior scoped repository search found no
GSE119630 source packet or completed normal-TempO comparator evaluation. The earlier impasse
memo is therefore not an established overall blocker and is superseded for allocation.

Question: Do this specific dataset's human normal sample provenance, probe/assay identity,
controls and raw counts permit a defensible calibration or normal-expression comparison with
the newly recovered twelve-column EMC TempO-Seq data? Same assay family is insufficient by
itself: probe version, attenuators, target sequence/aggregation, fixation/staining and gene-specific
study effects require explicit evidence. Ordinary library-size normalization cannot prove batch
comparability, and symbol overlap alone does not identify identical measurement. Cell lines and
animal tissues cannot substitute for normal human organs. Patient versus biological/technical
replication must remain distinct. Adjacent-normal surgical tissue is not a healthy-donor census.

One isolated worker retrieves original public GEO series/sample metadata, the two named HUMAN
count matrices, and the directly linked primary methods/supplements needed for assay/sample
identity. Do not download mouse/rat matrices or raw FASTQs. Recover patient-level normal/tumor
and replicate mapping and any shared technical reference/negative controls. Preserve primary
bytes, source URLs/times/hashes, exact matrix shape/identifiers and processing/probe metadata.
First inspect structural data and provenance only. Do not compute target-level differential
expression, target ordering, deconvolution, prognostic models, pooling or tumor/normal folds.
A fixed12target exact-symbol/probe-presence inventory may identify coverage, but do not tune a
panel or choose genes by observed expression. The existing panel is in the PeerJ source packet.

Compare documented measurement requirements to the existing PeerJ methods/processed export;
state what is identified, what remains study-confounded and whether a concrete calibrated
experiment is justified. Return no-go if essential mapping/calibration is absent, but do not
mistake a single missing field for proof no future comparison is possible. No broad literature
inventory or repeat Cattaruzza/Benassi access attempt. No paid access, contact, CAPTCHA workaround,
publication or manuscript. Public normal data are already a real source, not assumed equivalent.

Own research/autonomy/tempo-normal-source-2026-09-06/ in the isolated worktree based on
6ca5e76b559914510e28c0c6ad4bfb7ad1a3c544. Resource paper:PUB-SURFACE-TARGETS:tempo-normal-source.
One25minute source/provenance checkpoint, original bytes and meaningful format/identifier/hash
checks, actual requested medium effort and available runtime/timing evidence. Coordinator
independently verifies source before any new expression analysis. Normal/full release gates and
independent ultra requirement remain unchanged. Goal stays active with overall blocked count0.
