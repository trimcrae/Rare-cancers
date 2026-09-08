# M1 — exact tool calls, in order

Worker: M1 (subagent, claude-opus-5). Lane: /tmp/claude-0/m1-lane/
Start: date -u = "Tue Sep  8 10:42:29 UTC 2026"; git rev-parse HEAD = 29e2516bda8c40192c066250eebf095ab5629108
git status --porcelain at start: (empty)

C01 ToolSearch  {"query":"select:mcp__PubMed__get_article_metadata,mcp__PubMed__get_full_text_article,mcp__PubMed__convert_article_ids,mcp__PubMed__get_copyright_status","max_results":5}
    -> schemas loaded for the four PubMed tools. Not a source observation.

C02 mcp__PubMed__convert_article_ids  {"ids":["30373828"],"id_type":"pmid"}
    -> R02_convert_article_ids.json   CLASS: identifier resolution (precursor to (a))

C03 mcp__PubMed__get_article_metadata {"pmids":["30373828"]}
    -> R03a_get_article_metadata.json CLASS: (a) metadata + (b) abstract

C04 mcp__PubMed__get_full_text_article {"pmc_ids":["PMC6243280"]}
    -> R03_get_full_text_article_PMC6243280.json  CLASS: (c) full text (body prose only)
       NOT (d): no supplementary file list, no filenames, no URLs.
       NOT (e): no membership table.

C05 mcp__PubMed__get_copyright_status {"pmids":["30373828"]}
    -> R05_get_copyright_status.json  CLASS: licensing metadata

Tools NOT called (deliberately, per contract scope):
  mcp__PubMed__find_related_articles  — related-article expansion is out of scope
  mcp__PubMed__search_articles, mcp__PubMed__lookup_article_by_citation — second-identifier expansion
  WebFetch / WebSearch — not the admitted first-party route for this contract
No publisher site, no alternative host, no credentials, no payment, no download attempt of any kind.

Blocks / refusals / errors encountered: NONE. Every call returned status ok.
