# M1 lane INDEX — surfaceome membership-table source recovery (one source)

Source: Bausch-Fluck D et al., "The in silico human surfaceome", PNAS 2018.
PMID 30373828 | PMCID PMC6243280 | DOI 10.1073/pnas.1808790115

## Result in the contract's own terms
(a) metadata only ......... YES  (get_article_metadata)
(b) abstract .............. YES  (get_article_metadata; also inside full-text response)
(c) full text ............. YES  (get_full_text_article, body prose, 46,010 chars)
(d) supplementary file list  NO  — see below
(e) membership table ...... NO

The full-text response ends with the literal text:
  "Supplementary Material\n\nSupplementary File\n\nSupplementary File"
Two supplementary items are ACKNOWLEDGED but carry no filename, no caption, no size,
no media type and no URL. The full_text string contains zero occurrences of "http"
or "ftp". There is no supplementary-file listing field anywhere in the response
(article keys are exactly: identifiers, title, full_text, doi, abstract).
The body prose names only ~11 individual gene/protein symbols in running text; it
contains no gene-level membership list.

## Scope of the negative (bounded — NOT a global absence claim)
For THIS identifier, via THESE tools (convert_article_ids, get_article_metadata,
get_full_text_article, get_copyright_status), the membership table was NOT returned
and supplementary files were NOT enumerated or addressable. Nothing here is a claim
about the table's availability by any other route.

## No block, refusal or error occurred
All four PubMed calls returned successfully. Nothing was refused; nothing was routed around.
get_copyright_status reports license.is_open_access = false, open_access_count = 0,
copyright "Copyright © 2018 the Author(s). Published by PNAS." No paid or credentialed
route was attempted, and none is proposed here.

## Files
CALLS.md                                  exact calls + arguments, in order
R02_convert_article_ids.json              sha256 7edcb61a... 301 B   (transcribed verbatim)
R03a_get_article_metadata.json            sha256 c1f25296... 3260 B  (transcribed; see note field)
R03_get_full_text_article_PMC6243280.json sha256 0d372c10... 50461 B (BYTE-EXACT persisted artifact)
R05_get_copyright_status.json             sha256 2ae2a106... 575 B   (transcribed verbatim)
HASHES.txt                                sha256 of all of the above

## Not done
No overlap asserted or computed. Item 44 is NOT resolved. No repository write, no git write,
no other source, no related-article expansion, no repository census, no preflight, no GPU.
