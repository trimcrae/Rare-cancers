---
id: DOC-ATLAS-FOCUSED-FINAL-REVIEW-20260906
title: Focused verification of final tissue RNA preprint artifacts
kind: memo
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Preserve independent verification of the batched repairs and actual outgoing package.
scope: Exact final artifacts at 7b673f6c; original scientific review reused for unchanged science.
audience: [maintainers, external reviewers]
---

Coordinator filing metadata precedes the unchanged independent report body. Original bytes are in `report.md.original.txt` and the accompanying complete output ZIP.

Focused final artifact verification

**Verdict: supported. No new submission blocker.** The original scientific verdict carries forward to the exact final local article/SI PDF and code/data archive bound below. This was a focused check of changed artifacts and their dependencies, not another whole-paper review or a repeat of the science.

The original independent report and findings remain unchanged. The same continuing review seat is `/root/atlas_blind_ultra`, dispatched as `gpt-6-astra` with `ultra` reasoning effort. Independent serving-model/effort telemetry remains unexposed; these identifiers are recorded as dispatch provenance. The final rendered source checkpoint is `8bb8c9d2945f2ae68a60455ebd0eef4ee2fb0e0b`; the artifact candidate commit is `7b673f6c73f11e754b463374501d80bfe6cb95c6`.

I compared all 151 original frozen paths against the final root. Exactly six differ: main Markdown, canonical plotting adapter, figure-provenance JSON, article build stamp, and the two component PDFs. The other 145 are byte-identical. The main Markdown diff changes only frontmatter `level: cross-cutting` to `level: L3`; scientific prose and SI Markdown are unchanged. The plotting diff adds only a PDF/PNG/SVG suffix filter to its provenance collection.

M1 is verified fixed. The stale self-entry was removed, its prior record is preserved byte-for-byte, all six actual figure-file hashes match the original review, and the original generation metadata remains unchanged. The current repaired adapter hash is separately bound below; the historical generating-adapter hash correctly remains historical. E1 has an explicit optional-deferred disposition. It was not a condition of the scientific supported verdict and remains nonblocking.

I extracted and compared every final PDF page against the reviewed components. All 11 page texts are exactly unchanged except the source-revision label. The outgoing PDF is the exact seven-page article followed by the four-page SI. Rendering all 11 outgoing pages at the same 1,200-pixel scale produced nine pixel-identical pages. The only differences on pages 1 and 8 are the source-revision labels; I visually inspected those two final pages. Both build stamps match their actual current dependencies.

The refreshed ZIP is 95,349,965 bytes with 148 unique members. All 147 inventoried member hashes and sizes match; archive CRC checks pass. Of the packaged files present in the original review, 139 are unchanged and exactly three carry the expected canonical presentation updates (main Markdown, plotting adapter, and figure provenance). The five effect/sensitivity tables, normal-context Table S4, frozen protocols, analysis kernels, outputs, and historical draft remain unchanged. I verified all 76 replay-lock entries, eight scientific authorization hashes, six adapter code-freeze entries, and 11 original core source members. This establishes dependency continuity with the already verified replay; I did not rerun the scientific kernels. The PRAME factual extract matches its original reviewed workbook cells and supplies the exact original retrieval URL and SHA256; the original publisher HTML/workbook are intentionally not redistributed in this ZIP.

The proposed title and abstract match the final main Markdown exactly. The ZIP and its README describe a local unpublished supplement for separate delivery. I have not verified an aiXiv ZIP attachment route, upload, public hosting, or deposit DOI, and this report makes no such availability claim. Funding and competing-interest metadata remain unknown; no additional inferred venue gate is imposed. The coordinator reports that the full repository preflight was deliberately interrupted after fast-stage repository-maintenance failures. Generated inventory and filing repairs are outside this focused review and leave the bound deliverables unchanged. No full-gate pass is certified here.

Exact artifact bindings

| Artifact | SHA256 |
|---|---|
| Main Markdown | `455260bd45a60817571253d954fc42d6275e3ee53631b20f23d7f6fcbd1816d1` |
| SI Markdown | `81b5ace2d11e3c5ddf1e4a49becdce7d86ea9b5819f41a1415d5a923dd5d1844` |
| Article component PDF (7 pages) | `69a3786e7652e274239d90fc18d30306bfccf954610f75a79891c117b0c4bc99` |
| SI component PDF (4 pages) | `e46566f4eb87b894cbbb40ddce1812c01151dcc9ce30c0aca3a643b18cf4e9da` |
| Article build stamp | `f2211a38981eef20a269997faf01a882878e0f82a5d5fb5a4a326acf67d7a0aa` |
| SI build stamp | `da4bd6687913433cc95aa4899d3c1f0da1914d41b84535830aa69cfaf9d8947b` |
| Repaired canonical plotting adapter | `d40179cf0ca4b3fc4b8ede3885a0532ddfdca5cf72cb93e0630c99a279d27274` |
| Corrected figure provenance | `91953fcfc34aa0ae47b123a45fe6b29501ea2b056fbd6cc8d7c6447bb372e8c3` |
| Combined outgoing PDF (11 pages) | `2b39580313d504bca3790b9c8da16e06e16e8e2a2708fb554903c3a6fad059fc` |
| Final code/data ZIP | `56e089a6b39b9d5d5140a4185987778803359ab1154d26beb882d6e6197f3ea6` |
| Proposed submission metadata | `87721750b0c7eeab04b0c7934c59719921ad90195fc70bb81fa30f88c5a2d79d` |

The full absolute/relative paths, sizes, six individual figure hashes, preserved historical-provenance hash, build/append receipts, and parent review hashes are retained in `findings.json` and `verification.json`. The final root ZIP is byte-identical to the packageworker's `emc-tissue-rna-code-data-supplement-8bb8c9d.zip`.

A final integrity check confirmed that all 151 original frozen inputs remain unchanged, all 151 checked final-root paths stayed stable during this verification, and every bound final artifact retained its recorded hash. No root file was edited. The focused verification is complete; no process from this focused check remains running, and no upload/publication action was taken.
