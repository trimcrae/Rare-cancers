# S7 — exact URLs attempted and outcomes

Worker: S7, OPUS-CAPACITY-CAMPAIGN-20260908, paper-lane.
Target: Fice 2022, EMC case series. PMID 35251555 / PMC8891938 / DOI 10.1177/20363613221079754.
Route admitted by contract: WebFetch on the open-access PMC record. One source only.

## Attempt 1
URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC8891938/
Tool: WebFetch
Outcome (verbatim tool error):
{"error_type":"EGRESS_BLOCKED","domain":"pmc.ncbi.nlm.nih.gov","message":"Access to pmc.ncbi.nlm.nih.gov is blocked by the network egress proxy."}

## Attempt 2 (the second permitted URL form for the SAME PMC record)
URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8891938/
Tool: WebFetch
Outcome (verbatim tool error):
{"error_type":"EGRESS_BLOCKED","domain":"www.ncbi.nlm.nih.gov","message":"Access to www.ncbi.nlm.nih.gov is blocked by the network egress proxy."}

## Branch stopped
No third attempt. No mirror, no DOI/publisher route, no cached/proxy route, no authentication,
no denied-route retry, no sibling article, no second candidate. Nothing was extracted.

## Raw fetched content
NONE. Zero bytes of article content were returned by either attempt. The article body,
its figures and its tables were NEVER RENDERED in this branch. This is explicitly
MISSING BYTES, not an empty or negative reading of the source.

## Nature of the block (stated precisely, marked as inference)
OBSERVED: both errors are `EGRESS_BLOCKED` naming the network egress proxy and the NCBI host.
INFERRED (not observed): this is a sandbox network-egress restriction on the NCBI/PMC domains,
not a publisher paywall, not an authentication demand, and not a content-policy refusal.
No claim is made about whether the article is reachable from any other network.
