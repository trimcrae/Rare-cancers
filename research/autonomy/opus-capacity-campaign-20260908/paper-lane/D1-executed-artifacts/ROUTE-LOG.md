# D1 route and retrieval log (all times UTC 2026-09-08)
08:00:14  start: HEAD b913719f548c4009711db0bada8f1d9a035567d9, git status clean-of-writes, df / = 20G avail
~08:01    mcp__PubMed__get_article_metadata pmids=["41300991","42340948"] -> 200, count 2, both resolved
~08:01    mcp__PubMed__get_full_text_article pmc_ids=["PMC12651382","PMC13293439"]
          -> tool result exceeded inline token cap; server saved full JSON to
          /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/tool-results/mcp-PubMed-get_full_text_article-1788854465528.txt
          copied verbatim to ./pubmed-fulltext-raw-response.json (both articles present, full_text non-empty)
NOT RUN:  no WebFetch to pmc.ncbi.nlm.nih.gov / www.ncbi.nlm.nih.gov (S7 EGRESS_BLOCKED routes, not retried)
NOT RUN:  no publisher-site fetch, no paid access, no credentials, no literature census
FAILURES/REFUSALS: exactly one, verbatim, non-scientific (size cap), quoted above. No route refusal,
no egress block, no content-policy refusal encountered in this packet.
