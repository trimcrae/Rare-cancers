# W3 — recover ONLY the missing bibliographic metadata for PMID 11679947

## Why

U1 established that R1's unknown **U6 was half-resolvable**: Sjögren 2003's fields were already
committed, but **Okamoto 2001 (PMID 11679947) genuinely has no committed journal/volume/pages**. It is
a reference **already cited** in R1's proposal — this adds no new citation.

## ⭐ Check the repository FIRST

`11679947` already appears in
`research/autonomy/opus-capacity-campaign-20260908/reports/W06-diagnostic-delay-molecular-confirmation.md`
and in U1/R1 records. **If an already-retained record supplies journal, year, volume, issue, pages or
DOI, REUSE IT and do not retrieve.** Retrieval is only for what is genuinely missing.

## If retrieval is needed

Use the **existing permitted first-party PubMed capability** (the MCP tools; load schemas with
ToolSearch). **No named denial covers this route** — M1 used it successfully for a different PMID.

1. **Match identity before proposing anything:** the returned **PMID and title and author** must match
   the cited Okamoto record. **If identity does not match, STOP and report that** — do not propose
   fields from a near-miss.
2. Propose only **journal, year, volume, issue, pages, DOI**. ⛔ **No full-text recovery, no clinical
   claim verification, no related-article expansion, no second identifier, no search census.**
3. **On ANY refusal or block: record it verbatim and STOP that branch.** ⛔ No retry, no alternative
   mirror, no paid fallback.

## Deliver, in `/tmp/claude-0/w3-lane/`

The **exact original request and result**, the identity match shown explicitly, and the proposed
fields — or a precise **unresolved** result. State the evidence grade.

## Bounds — binding

Input revision **c365b4e836358274703cef278417193f615629f3**. `claude-opus-5` **medium**, saved first-party subscription — no paid fallback,
overage, credits or GPU. Deadline **2026-09-09T02:37:19Z**.

⛔ **No write to any shared repository path** — everything in your own lane. **No git write**;
read-only git only. ⛔ No manuscript, registry, tier, rule, figure or shared-artifact edit. ⛔ No
unchanged gate rerun, no `scripts/preflight.sh`. ⛔ No broad review, 47-item audit, census, history
reconstruction or publication step.
⛔ **Mark anything you cannot source as UNRESOLVED. Never invent a value to fill a column or a claim.**
There is no wet lab: no EMC efficacy, safety, selectivity or clinical-readiness claim. Invent no fact,
source, patient datum or measurement. If a request of yours is refused by content policy, stop that
branch, record the refusal verbatim, never route around it.
⛔ **DELETE NOTHING.** Retain your inputs' digests, your exact commands and their results. Record
`date -u`, `git rev-parse HEAD`, `git status --porcelain` at start and end; confirm you changed
nothing shared.

Final title, preregistration amendments, manuscript integration and publication remain with the
existing decision process. Stop at a supported finite result, or ~35 tool calls / ~30 minutes.

