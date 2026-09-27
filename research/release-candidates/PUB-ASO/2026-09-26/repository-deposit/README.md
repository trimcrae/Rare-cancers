---
id: ASO-JUNCTION-ARCHIVE-README-20260926
title: Reproducing the documented-junction sequence comparisons
kind: memo
status: live
date: 2026-09-26
last_verified: 2026-09-26
purpose: Identify archive scope and exact offline reproduction instructions.
scope: Named ASO data archive, excluding manuscript and downloaded literature.
audience: [maintainers, external reviewers]
---

This archive contains the attributable reference inputs, junction provenance, design comparisons, source receipts, corrections and analysis code for the September 2026 EMC transcript-provenance investigation. Evidence classes distinguish deposited sequences, reference reconstructions, experimental constructs and hypothetical controls.

Extract the ZIP preserving directory paths. Enter `research/release-candidates/PUB-ASO/2026-09-26/evidence` and run `python analyze.py` with Python 3.11 or later. No extra packages or network are required. All eleven files in `results/` should reproduce with the SHA-256 values recorded in `repository-deposit/zenodo-manifest.json` (relative to the candidate directory).

The manifest uses repository-relative paths and pins the source commit, byte size and SHA-256 for every payload member. Its content digest is SHA-256 over sorted records of `path`, a NUL byte, the hexadecimal file SHA-256 and a newline. The manifest itself is an additional ZIP member; its hash is recorded in the deposit description and upload receipt to avoid a circular self-hash.

`supplementary-methods.md` is the source ledger and detailed methods. Downloaded literature articles, figures, abstracts and supplements are omitted from the public data archive; links and retrieval receipts identify the originals. Those omitted files are not inputs to the offline sequence analysis. The larger journal review supplement retains the local source collection.

The optional negative read-prefix experiment requires a separate 128 MiB download. The read receipts and probe code retain exact retrieval and anchor definitions. The partial, nonrandom, single-mate search does not establish that a fusion is absent. `input-manifest.json` describes the larger original investigation collection, including literature and read prefixes; the archive inventory is `repository-deposit/zenodo-manifest.json`.

Original repository software retains Apache-2.0 licensing; see the root `LICENSE`. Original derived artifacts are CC-BY-4.0. Third-party sequence records retain their source attribution and applicable terms. These are computational sequence comparisons, not evidence of RNA cleavage, selectivity, safety or therapeutic benefit.
