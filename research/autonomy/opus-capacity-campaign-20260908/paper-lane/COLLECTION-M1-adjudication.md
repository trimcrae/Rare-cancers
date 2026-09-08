# M1 — collection and adjudication against `CONTRACT-M1-surfaceome-membership-source-recovery.md`

Collected 2026-09-08 10:46-10:52 UTC. **Result: a clean, bounded NEGATIVE — an early stop, which the
contract records in advance as a successful outcome.** No re-run, no second identifier, no census.

## Child identity — from the transcript, full lifetime

| item | measured |
|---|---|
| child | `a5956710c3213c7aa` |
| original JSONL | `M1-executed-artifacts/ORIGINAL-CHILD-TRANSCRIPT-a5956710c3213c7aa.jsonl`, **123,367 B**, `cmp`-identical |
| model strings | **`claude-opus-5` only, 0 others** |
| tool pairs | **15** |
| **full lifetime** | **10:42:24.532Z -> 10:45:18.532Z** (~2 m 54 s) of a ~25 min bound |

## What was asked and what came back

Four first-party PubMed MCP calls, all returning **status ok — no block, no refusal, no error, so
nothing was routed around**:

| call | classified |
|---|---|
| `convert_article_ids` | identifier resolution: PMC6243280 / 30373828 / 10.1073/pnas.1808790115 |
| `get_article_metadata` | **(a) metadata + (b) abstract** |
| `get_full_text_article` | **(c) full text** — 46,010 characters of body prose |
| `get_copyright_status` | licensing metadata |

**Not (d) a supplementary-file listing. Not (e) the membership table.**

## Parent verification — I checked the artifact myself

Re-reading `R03_get_full_text_article_PMC6243280.json` independently:

- **50,461 B**, sha256 `0d372c107062479110b804f67e29e620...` — matches the child's report.
- Longest string is **46,010 characters**, the full text.
- **`http` occurrences: 0. `ftp` occurrences: 0.** No link to any supplementary asset.
- The body ends exactly at `'Supplementary Material\n\nSupplementary File\n\nSupplementary File'` —
  two supplementary items **acknowledged but unnamed**: no filename, caption, size, media type or URL.

So the tool exposes the article's prose but **not its supplementary assets**, and the membership table
lives in those assets.

## ⚠ One retention distinction the child itself flagged, and it matters

- `R03_get_full_text_article_PMC6243280.json` is the **byte-exact persisted artifact** from the tool.
- `R03a_get_article_metadata.json` is a **verbatim transcription, NOT original bytes** — the child says
  so in an embedded `_M1_transcription_note` recording its two omissions (per-author affiliation
  arrays, the boilerplate legal notice). **A transcription is not the original response**, and it is
  labelled as such rather than presented as retained bytes. This is the same distinction the campaign
  drew for D2 earlier.

## ⭐ A correction to my own blocker record

In `BLOCKER-surface-targets-item44-surfaceome-overlap.md` I wrote: *"PMC6243280 exists, so the article
is open access"*. **That was an inference from the presence of a PMCID, and it is contradicted by the
measurement.** `get_copyright_status` returned:

```
license.is_open_access: false
open_access_count: 0
copyright.statement: "Copyright (c) 2018 the Author(s). Published by PNAS."
```

**A PMCID is not proof of open access.** The inference is withdrawn.

## Acceptance, adjudicated

1. **First-party tools only — MET.** No paid access, credential, publisher site, alternative host or
   download. Nothing was refused, so nothing was routed around.
2. **Classified precisely — MET**, as the table above.
3. **No overclaim — MET.** The child asserted no overlap, computed nothing, and did **not** treat
   item 44 as resolved.
4. **Provenance retained — MET**, with the transcription honestly distinguished from the byte-exact
   artifact.
5. **Early stop — MET, and correct.** It stopped at ~3 minutes of 25 rather than expanding the search.
6. **Nothing written to the repository — MET.** `git status` empty at its end; no git write.

## The finding, worded so it cannot be overread

**For PMID 30373828 / PMC6243280, via these four PubMed MCP tools, the response carried no
supplementary-file listing and no membership table.** That is a statement about **what this tested
route returned for this identifier**. It is **not** a claim that the table is unavailable in general,
nor by any other route, nor that no membership data exists anywhere.

## Item 44: what changed, and what the reopening condition now is

**Before:** the route had never been tested, so there was no observed access failure.
**Now:** the route **has** been tested and returns prose but not supplements — a measured, bounded
result rather than an assumption.

**Reopening condition, refined:** item 44 reopens when the membership table is committed here as
gene-level data, obtained through a route that actually exposes **supplementary assets** — which the
PubMed full-text tool demonstrably does not. Nothing about that route is worth retrying for this
identifier; a different, separately authorised route would be required, and **none is proposed or
implied here**. The article is additionally recorded as **not open access**, which bears on what any
such route could legitimately do.

**Item 44 remains open and unresolved.** No manuscript wording changes: the paper's existing statement
that the resource exists and was not used, with the reason, remains accurate.

## Retention

`/tmp/claude-0/m1-lane/` **intact, nothing deleted**, pending an exact-directory receipt. In-repo copy
`M1-executed-artifacts/` with a self-exclusive manifest.
