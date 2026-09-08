# ⚠ DATED CORRECTION to `PST-SOURCE-LOCATORS.md` — the esummary DOES carry sample annotations

**2026-09-08, parent. Correction appended beside the original record, which is preserved unchanged
along with its delivered bytes. ⛔ No new retrieval, no repeated transport, no audit.**

## What I got wrong
`PST-SOURCE-LOCATORS.md` reported, under "⛔ What is ABSENT":

> **Supplementary sample/probe annotation tables for GSE24369 or GSE28866: NO RETAINED COPY.** The two
> candidate GEO records are **series-level summaries**: each contains a single `GSM` occurrence, so
> neither carries a per-sample or per-probe annotation table.

**That characterisation is WITHDRAWN.** Root's late source correction establishes that the retained
`geo_esummary_emc.txt` **compact-JSON line 6 does contain per-sample accessions and titles**,
including **all 42 GSE24369 titles** and relevant GSE28866 metadata.

**Why my method missed it, stated plainly:** I counted occurrences of the literal token `GSM` and read
a count of 1 as evidence of series-level-only content. The file is **compact JSON on very few long
lines**, so per-sample entries live inside one line rather than one per line — a line- and
token-oriented probe was the wrong instrument for that shape, and a low count was not the absence I
took it for.

## What the artifact actually establishes
- Per-sample accessions and titles, including all **42 GSE24369** titles and relevant GSE28866
  metadata.
- Source links: **GSE24369 → PMID 21536545**, **GSE28866 → PMID 22929540**,
  **GSE4303 → PMID 15920699**.

⚠ Those links **do not** establish any article's full text or metadata, and this correction asserts
nothing beyond what the retained bytes carry.

## What is unchanged
- The delivered copy of `geo_esummary_emc.txt` is **byte-identical and already with the reviewer** —
  ⛔ the transport is **not** repeated.
- The **HPA original API response remains genuinely absent**; that half of the original record stands.
- The **unavailable B4 PNAS supplement scope stays closed.**
- The original record's historical assertion is preserved verbatim rather than edited away, so the
  mistake and its correction are both readable.

⭐ The artifact's actual sample-title contents and root's finding govern this batch — not my earlier
characterisation.
