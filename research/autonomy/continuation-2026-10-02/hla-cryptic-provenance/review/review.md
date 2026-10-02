---
id: DOC-CHECKPOINT06-PRIMARY-REVIEW
title: Independent review of one deposited HLA protocol witness
kind: review
status: live
date: 2026-10-02
last_verified: 2026-10-02
audience: [external reviewers]
purpose: Verify bounded result-provenance claims against original saved bytes.
scope: One DN13 skin mzIdentML output and reused primary XML and PRIDE metadata; no scientific reanalysis or readiness review.
---

All independent checks passed. No substantive correction is necessary for the reviewed bounded claims. The exact reviewed file hashes and original XML attributes are in review.json.

Independent stdlib parsing confirms that the original compressed object is 78,546 bytes, SHA1 `6fd0ddf159917003808f1c93843b45520f2324f7`, SHA256 `ebbae14f847dd4a3a554c5b818fa1399fbdc2005a22b46288ab1690b3570e1ed`. Decompression yields 814,334 bytes with SHA256 `9ae13ad300ad6e9805d3deb680b2031e93c5f25a0ba66e9b292ec02a9e15a563`. The compressed SHA1 matches the selected PRIDE checksum; the metadata size equals decompressed length. All twelve manifest entries and the four reused source hashes match.

The minimum `(fileSizeBytes, filename)` among 16 RESULT entries in the cached 100-row response independently selects the stated DN13 skin file. README counting independently gives 3,425 rows: 1 FASTA, 1,471 PEAK, 1,470 RAW, 483 RESULT. This is not selection across all 483 results. The ledger records one successful mzIdentML retrieval; it cannot establish that no unrecorded request occurred elsewhere.

Original XML attributes establish serialized Percolator 3.02, precursor plus/minus 6.0 parts per million, fragment plus/minus 0.01 dalton, and two internal references to `sp_21_04_2020_decoy.fasta`. The saved fragment agrees with the original XML elements. This establishes a filename association with the sole deposited canonical FASTA, not byte-level proof of the executed database. No actual execution setting or general property of all outputs follows. The fragment tolerance is not equated with the paper's 0.02 Da Comet fragment-bin quantity. Percolator training/test FDR and generic Threshold metadata do not establish the final identification filter.

Primary XML directly supports PEAKS Studio X, top ten candidates, six-frame HG38 and three-frame Ensembl 90 translation, stratified 10% FDR and NetMHCpan-4.0. Primary conventional methods report Percolator 3.4 and precursor 5 ppm; cached project protocol reports 3.1.1. None resolves the execution provenance of this one output. Exact historical cryptic inputs and Atlas-specific configuration remain missing; representation of all four provisional sequences remains UNKNOWN, not negative peptide or HLA-presentation evidence. The filename screen and failed supplement retrieval do not prove those inputs are absent elsewhere.

Source audit.py was inspected but not executed, avoiding its overwrite behavior. Only these two new private review files were written. No canonical FASTA scan, peptide scan, network retrieval, UI, checkout, installation, paid computation, publication, or submission-readiness assessment was performed.
