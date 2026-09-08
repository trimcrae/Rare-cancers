# B4 — Bausch-Fluck 2018 surfaceome membership supplement: source checkpoint

# OUTCOME: DENIED

The one genuinely untried route — the PNAS publisher supplement page for
`10.1073/pnas.1808790115` — was attempted **once** and was **denied at the egress proxy with
`HTTP/1.1 403 Forbidden` on the CONNECT tunnel**. Zero bytes were transferred. No supplement file
was retrieved, so **no comparison against the retained UniProt-derived set was performed**
(Step 3 never became eligible).

⛔ This is **not** a claim that the supplement was recovered, and **not** a claim that item 44 is
resolved. It is a measurement of what one named route returned to this sandbox at one time.

Written 2026-09-08, `date -u` 19:22Z. Session `session_01Eui7FVgatEXAwt2N35yHH6`.
No manuscript, artifact, producer, commit, push, test suite, preflight or figure build was touched.

## Source identity — verified before anything was attributed

| field | value |
|---|---|
| citation | Bausch-Fluck D, Goldmann U, Muller S, van Oostrum M, Muller M, Schubert OT, Wollscheid B. *The in silico human surfaceome.* PNAS 2018 |
| PMID | 30373828 |
| PMCID | PMC6243280 |
| DOI | 10.1073/pnas.1808790115 |

Identity was checked against the retained artifact
`M1-executed-artifacts/R03a_get_article_metadata.json` and the citation record in
`research/literature/remaining-reference-metadata-2026-08-09.json`, not assumed from the
proposal's locators.

## Step 1 — look before fetching (done once)

### 1a · Is a matching membership table already available in this repository? **No.**

Searched, and stating what each search does and does not establish:

- **Filename search** across the whole tree (`-iname "*surf*"`, excluding `.git`) returns 60+ hits,
  all of them this repository's own EMC surface work — `research/modalities/emc-surfaceome-scan.json`,
  `surfaceome-instrument-limits.json`, `nr4a3-differential-surface-atlas.json`,
  `emc_surface_figure.py`, the `surface-targets` manuscript set, and campaign lane artifacts.
  I opened the three data JSONs: they are **this repository's own derived artifacts** (a DepMap
  surrogate-line scan, an instrument-limits record, and a SASA/alignment atlas). **None declares
  Bausch-Fluck as a source and none contains a published surfaceome membership list.**
- **Content search** for `SURFY`, `1808790115`, `30373828`, `PMC6243280` and
  `in silico human surfaceome` hits only **citation records, campaign lane prose, and the M1
  retrieval artifacts** — never a gene-level membership table.
- **Format search** for `*.xlsx *.xls *.csv *.tsv *.zip *supp* *sd0*` across the tree returns only
  this campaign's own curation TSVs, LEAF outputs and evidence zips. **No publisher supplement file
  of any kind is present.**
- The **retained source index** (`inputs/source-index/`, and `inputs/source-index-cloud-inputs.zip`)
  is the `source_reuse_index.py` tooling package plus its execution/comparison evidence. It is a
  **code-reuse index, not a bibliographic asset store**, and holds no supplement.

⚠ Bounded, as required: these searches establish that **no matching membership table was found under
any label I searched**. Combined with the format search returning no supplement-shaped file at all,
this is a strong negative — but it remains a statement about searches actually run, not a proof of
global absence.

### 1b · Is the exact route already recorded as tried or denied? **The PubMed/PMC route is, and is exhausted.**

`CONTRACT-M1-surfaceome-membership-source-recovery.md`, `M1-executed-artifacts/INDEX.md` and the
2026-09-08 10:45 UTC append to `BLOCKER-surface-targets-item44-surfaceome-overlap.md` record that
worker M1 already ran the first-party PubMed/PMC tools against this exact identifier:

- Four calls (`convert_article_ids`, `get_article_metadata`, `get_full_text_article`,
  `get_copyright_status`) **all returned ok — no block, no refusal, no error**.
- Returned: identifier resolution, metadata, abstract, and full text (46,010 characters).
- **Not** returned: any supplementary-file listing, and **no membership table**. The body ends at
  `"Supplementary Material\n\nSupplementary File\n\nSupplementary File"` — two items acknowledged
  with no filename, caption, size, media type or URL — and the full text contains zero `http` and
  zero `ftp` occurrences.
- `get_copyright_status` returned `license.is_open_access: false`, `open_access_count: 0`,
  `Copyright (c) 2018 the Author(s). Published by PNAS.` **A PMCID is not proof of open access.**

So the PubMed/PMC route is not *denied*; it is **measured and exhausted** — it exposes prose but not
supplementary assets. Re-running it is pointless and I did not re-run it. I did not touch, modify or
duplicate any M1 file; M1's evidence directory remains intact.

## Step 2 — the one untried route, attempted once

Legitimate primary publisher route for the supplement:
`https://www.pnas.org/doi/suppl/10.1073/pnas.1808790115`

Result, `date -u` **2026-09-08T19:22:18Z**:

```
* Establish HTTP proxy tunnel to www.pnas.org:443
> CONNECT www.pnas.org:443 HTTP/1.1
< HTTP/1.1 403 Forbidden
< Connection: close
* CONNECT tunnel failed, response 403
curl: (56) CONNECT tunnel failed, response 403
```

`__HTTP=000  TYPE=  BYTES=0`. **Nothing was transferred**, so there are no original bytes, no source
schema and no table to preserve — only the denial itself, retained with its checksum at
`B4-surfaceome-source-artifacts/PNAS-publisher-route-denial.txt`
(sha256 `78cfe0d7856b96ec4726d536e21651845f72b721e5eafcfe2fab878b803f1d61`).

This denial is consistent with the independently recorded condition in
`research/literature/browser-fetch.json`: publisher pages "return 403 (publisher bot protection) or
429 ... to plain HTTP from both the dev sandbox and CI".

**I stopped here.** Per the brief, a denial is not permission to try a succession of routes. I did
**not** attempt a mirror, a CI/Actions runner, a headless-browser fetch, a search-engine copy, an
alternate host, a guessed `suppl_file` URL, or any credentialed, paid or paywall-bypassing access.
I did not disable TLS verification and did not unset `HTTPS_PROXY`.

## Step 3 — not eligible

Step 3 is conditional on Step 2 delivering an actual file. It did not. **No identifier mapping, no
duplicate or unmapped counts, and no set-membership comparison were produced**, and none should be
attributed to this task. Nothing here bears on target efficacy, on cell-surface expression in EMC, or
on the publication's classifier.

## What this changes

**Nothing, pending root.** The manuscript's existing statement — that the resource exists and was not
used, because this repository's surfaceome is built from UniProt annotation — remains accurate and
untouched. Item 44 stays open. Its reopening condition is unchanged: the membership table committed
here as gene-level data, obtained through a route that actually exposes supplementary assets and is
separately authorised. **No such route is proposed or implied by this record.**

## Retention

`B4-surfaceome-source-artifacts/` holds the denial transcript and `SHA256SUMS.txt`. Under CLAUDE.md
section 8 this directory stays intact until a directory-specific local receipt verifies it. Nothing
was deleted.
