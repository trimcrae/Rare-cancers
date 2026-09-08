# P-ST reviewer — existing-byte locators for GEO and HPA sources

**2026-09-08, parent-only. ⛔ No publisher, registry or API request; no source acquisition, mirror,
B4 retry, new worker or planner.** All reads used `GIT_NO_LAZY_FETCH=1`, so a locally absent object
would have failed loudly rather than triggering a fetch. GSE28866 source closure is respected — only
already-retained bytes are reported.

⚠ Root's earlier metadata-only filename listing found no literal filename matches. **This search went
further and queried BODY identifiers** across the literature tree, which is why it finds records that
a filename scan could not.

## 1 · What EXISTS, with exact pins

**GEO series-level metadata (esummary), enumerating both accessions.**
- path `literature/ct-reverify-c3b-2026-08-07/geo_esummary_emc.txt`
- blob `64621bda29a49a155b08d00c5e407a59a53c9481`, **30,740 B**, at commit `216bd1b5…`
- byte-identical duplicate at `literature/emc-clinical-sweep-c3-2026-08-07/geo_esummary_emc.txt`
  (same blob — one object, no second copy made)
- It enumerates **GSE24369, GSE28866, GSE4303, GSE43632, GSE80126**.
- A copy is delivered beside this record with its sha256.

**Documents whose body cites an accession** — offered as citing records, ⛔ **NOT asserted to be the
originating publications**, which this evidence does not establish:
- `literature/ct-reverify-c3b-2026-08-07/PMC4053743.txt`, blob `efc39df2f139b7a263ba23b0290d67735eeb0a53`,
  52,208 B — cites `[GEO:GSE28866]` for predicted transcripts in a figure/additional file. Duplicated
  under six further slugs, same blob.
- `literature/aso-priorart-junction/PMC10959353.txt`, blob `c51cd8a9c6bf41653cedf33a5d39044cdbabe52b`,
  56,220 B — matches `GSE24369` on a whole-file search.
- `literature/nr4a3-cistrome-search-r2a/r2_sum_gds_03_disease_any.txt`, blob
  `9db85556c71aa5a428babf131a151f8df7c771e2`, 40,224 B — a GEO DataSets summary listing.

## 2 · ⛔ What is ABSENT — precisely scoped, not an invitation

**Supplementary sample/probe annotation tables for GSE24369 or GSE28866: NO RETAINED COPY.** The two
candidate GEO records are **series-level summaries**: each contains a single `GSM` occurrence, so
neither carries a per-sample or per-probe annotation table. Nothing else in the tree matches.

**The original HPA API response underlying `research/modalities/emc-surface-normal-window.json`: NO
RETAINED COPY.** Searched by filename (`proteinatlas`, `hpa`) and by body identifiers
(`proteinatlas.org/api`, `RNA tissue specificity`, `rna_tissue_specificity`). The only body matches
are three unrelated PMC full texts that mention the Human Protein Atlas in prose. ⚠ As root already
noted, the normal-window artifact's own source metadata merely **names** HPA RNA
tissue/blood-cell/subcellular specificity — that naming **is not an original API response**, and this
search found no payload of that shape anywhere.

⛔ These absences are a **precisely scoped limitation of what was retained**, established over the
refs actually inspected (`216bd1b5`, `HEAD`, `origin/main`). They are **not** a source-retrieval
invitation, and no fetch, mirror or B4 retry was attempted or is proposed.

## 3 · Not duplicated
The reviewer already holds the frozen reduced inputs, the full sample annotations, the accession
cache, the source readers and both PNGs. ⛔ None of those was re-copied. The FP batch-2 transport is
closed and was not repeated.
