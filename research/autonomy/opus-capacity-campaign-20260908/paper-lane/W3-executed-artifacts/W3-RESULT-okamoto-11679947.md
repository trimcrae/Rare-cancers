# W3 — bibliographic metadata for PMID 11679947 (Okamoto 2001)

Worker W3. Start: 2026-09-08T11:56:09Z, HEAD f5a16b5bd571df8ae56964e40f3248eccddb9276,
`git status --porcelain` EMPTY at start.

## Result in one line

RESOLVED FROM THE REPOSITORY. **No retrieval was needed and none was performed.** All six requested
fields are already committed in tracked repository files. U1's finding that "no committed record
carries its journal, volume or pages" is **incorrect** — it missed
`research/manuscripts/aso/fusion-junction-aso-references.json`.

## What the repository already held (quoted, with file and line)

`research/manuscripts/aso/fusion-junction-aso-references.json:539-552` (entry n=37):

```
      "n": 37,
      "pmid": "11679947",
      "authors": "Okamoto S, Hisaoka M, Ishida T, Imamura T, Kanda H, Shimajiri S, Hashimoto H.",
      "title": "Extraskeletal myxoid chondrosarcoma: a clinicopathologic, immunohistochemical, and molecular analysis of 18 cases.",
      "journal": "Human pathology",
      "year": 2001,
      "volume": "32",
      "issue": "10",
      "pages": "1116-1124",
      "doi": "10.1053/hupa.2001.28226",
      "_corpus": "panagopoulos-2002-citing-papers"
```

Independent corroborating committed records (same fields, different files):

- `research/manuscripts/aso/fusion-junction-aso-references.md:64` — "37. Okamoto S, Hisaoka M, Ishida T,
  Imamura T, Kanda H, Shimajiri S, Hashimoto H. Extraskeletal myxoid chondrosarcoma: a
  clinicopathologic, immunohistochemical, and molecular analysis of 18 cases. Human pathology.
  2001;32(10):1116-1124. PMID: 11679947. doi:10.1053/hupa.2001.28226"
- `research/manuscripts/aso/fusion-junction-aso-supplementary-information.md:210` — same journal,
  year, volume, issue, pages and PMID.
- `research/autonomy/opus-capacity-campaign-20260908/reports/W06-diagnostic-delay-molecular-confirmation.md:107`
  — "Okamoto 2001 [DOI](https://doi.org/10.1053/hupa.2001.28226)" (retrieved from PubMed in W06's
  own `get_article_metadata` call on a list including 11679947, line 104), i.e. the DOI is
  independently retained from a prior permitted retrieval.
- `research/manuscripts/aso/fusion-junction-aso-coverage-ladder.json:1903-1904` — "pmid":
  "11679947", "who": "Okamoto 2001, Hum Pathol — 18 EMCs, RT-PCR on paraffin-embedded tissue"
  (journal abbreviation and year, consistent).

All of these are tracked files; `fusion-junction-aso-references.json` last changed at commit
14a3f172d6b494d872f6d2678c7d0caa7ef26ccc and is clean in the working tree.

## Identity match, shown explicitly

| Field | R1's cited record (`R1-executed-artifacts/PROPOSED-emc-atr-collaborator-package.md:578`, ref 9) | Retained record (`fusion-junction-aso-references.json:541-543`) | Match |
|---|---|---|---|
| PMID | 11679947 | 11679947 | YES |
| Title | "Extraskeletal myxoid chondrosarcoma: a clinicopathologic, immunohistochemical, and molecular analysis of 18 cases." | identical string | YES |
| First author + list | "Okamoto S, Hisaoka M, Ishida T, Imamura T, Kanda H, Shimajiri S, Hashimoto H." | identical string | YES |

Content check (not required, noted because it is free): R1's ref 9 states "fusion transcripts detected
in 15 of 18 cases … type 1 in 11, type 2 in 1 and TAF2N-CHN in 3", which matches the retained
abstract verbatim quoted at `fusion-junction-aso-coverage-ladder.json:1905`. Same paper.

## Proposed fields (for R1 ref 9 only)

| Field | Value |
|---|---|
| journal | Human pathology (Hum Pathol) |
| year | 2001 |
| volume | 32 |
| issue | 10 |
| pages | 1116-1124 |
| DOI | 10.1053/hupa.2001.28226 |

Formatted: Okamoto S, Hisaoka M, Ishida T, Imamura T, Kanda H, Shimajiri S, Hashimoto H.
Extraskeletal myxoid chondrosarcoma: a clinicopathologic, immunohistochemical, and molecular analysis
of 18 cases. *Hum Pathol* 2001;32(10):1116-1124. PMID 11679947. doi 10.1053/hupa.2001.28226.

Consequence for R1: the "[PROPOSED — UNRESOLVED U6 …]" marker on reference 9 can be removed, exactly
as U1 directed for reference 10 (Sjögren). U6 is now **fully** resolvable, not half.

## Evidence grade

**Read, not inferred, and not retrieved in this lane.** I read the six fields verbatim in a committed
tracked repository file and confirmed them against three further independent committed records. I did
not open PubMed, a DOI, or any network route in this lane; the DOI's own retrieval provenance is W06's
prior permitted PubMed `get_article_metadata` call, recorded at that report's line 104/107. I have not
verified the article's content beyond the identity fields above, and I make no clinical, efficacy,
safety, selectivity or readiness claim.

## Refusals or blocks

None. No tool refused anything in this lane; no PubMed request was issued.

## What I did NOT do

No retrieval, no PubMed MCP call, no ToolSearch schema load, no WebFetch/WebSearch. No full text, no
clinical-claim verification, no related-article expansion, no second identifier, no search census. No
edit to any shared repository path, no git write, no manuscript/registry/artifact edit, no gate rerun,
no preflight, no GPU, no paid API. I deleted nothing.

## End state

End: 2026-09-08T11:57:12Z. HEAD at end **869879a609f78bc5737f5f0bc4f59b00c877640c** ("paper-lane: W1
to W3 executing on three review-identified dependencies"), i.e. main advanced under me from
f5a16b5bd571df8ae56964e40f3248eccddb9276 by the coordinator, not by me: **I performed no git write and
no shared-path write.** `git status --porcelain` EMPTY at start and EMPTY at end. Lines 539-552 of
`research/manuscripts/aso/fusion-junction-aso-references.json` re-read at the new HEAD and unchanged.
