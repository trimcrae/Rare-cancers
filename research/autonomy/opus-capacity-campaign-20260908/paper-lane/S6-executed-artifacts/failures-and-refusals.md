# S6 — failures, refusals and blocked dependencies (verbatim outcomes)

No content-policy refusal occurred. No tool returned an error. Nothing was routed around.

## 1. The route cannot deliver either half of a figure–truth pair
`mcp__PubMed__get_full_text_article` returns narrative text only. Observed on all three
retrievals (PMC4946242, PMC8891938, PMC6194639): table contents, figure images and even the
table/figure NUMBERS are stripped, so inline citations render as bare `()` or as
`"presented in Table."`. The per-patient rows and the survival curves — the two halves being
catalogued — live exactly in the stripped material.

**Exact dependency to resolve this:** one rendering of the PMC HTML (or PDF) tables and figures
for a named candidate. S6 had no admitted route to that and did not attempt one.

## 2. PubMed cannot search the class at all
`sarcoma AND swimmer plot AND (...)` → **0 records**, while the campaign holds a retained
sarcoma swimmer plot (PMC7674086). PubMed indexes title/abstract/MeSH, not figure captions or
table contents. The property being enumerated is therefore invisible to the search instrument;
candidates can only be screened one article at a time.

## 3. Two queries failed as queries
- `... AND open access[filter]` → 0 records **with no term expansion in the translation** — the
  query appears to have been voided rather than filtered. This is a FAILED QUERY. It is not
  evidence about the class.
- The quoted-phrase query (`"clinical course of each patient"` etc.) was auto-mapped by PubMed
  into generic `patients[MeSH]` and returned 737 unrelated records. Not screened; no inference
  drawn from it.

## 4. Excluded sources encountered and dropped
PMID **32856598 (Wagner)** appeared inside the result list of query 3. It is on the
`CLOSED-WORK.md` denied list. It was **not** retrieved, not converted, not screened, and no
substitute route was sought. No other denied or held item surfaced. GSE4303, GSE28866,
PMID 22592656, W25/GSE243553, the primary-article/Results/novelty continuations and the NR4A
Perspective were not touched in any form.

## 5. Not run
See `queries.json -> not_run`. Fifteen PMC-available candidates were identified but not
full-text screened, and no table or figure was inspected for any candidate.
