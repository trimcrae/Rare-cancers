# FP final reviewer — retained source-copy locators, answered from local Git objects

**2026-09-08, parent. ⛔ No new worker, no literature search, no external source fetch, no
denied-route retry. Nothing was fetched to answer this.**

Method: `GIT_NO_LAZY_FETCH=1 git cat-file -s <blob>` on each requested object, so a locally absent
object would report ABSENT rather than silently triggering a fetch. Two blobs were additionally
round-tripped through `git hash-object --stdin` and reproduced their own ids exactly.

## ⭐ ALL TWELVE REQUESTED BLOBS ARE PRESENT IN THIS SESSION'S GIT OBJECTS

| # | path | blob | bytes |
|---|---|---|---|
| 1 | `literature/emc-post-degrader-options/emc_fusion_freq_agaram2014_pmc.txt` (Agaram) | `e8df2912937b7d340bb890aceaec1960268af5ee` | **39,636** |
| 2 | `literature/emc-clinical-sweep-c3-2026-08-07/PMC7563993.txt` | `8f72a7371f12985c56737a46650e0b7e67abcf47` | **26,795** |
| 3 | `literature/emc-clinical-sweep-c3-2026-08-07/PMC7999686.txt` | `b9681a74b63f3a095eee15c61f069deb6c3a8e7c` | **35,817** |
| 4 | `literature/emc-clinical-sweep-c3-2026-08-07/PMC5400622.txt` | `69118d3320f0fd287533cf7d19beb5f43c410718` | **17,532** |
| 5 | `literature/emc-clinical-sweep-c3-2026-08-07/PMC3534218.txt` | `808a46cc757f22d7ede9af1d83955007d62224c9` | **14,869** |
| 6 | `literature/emc-clinical-sweep-c3-2026-08-07/ft_sunitinib2014_ejc.txt` | `0978078ce1871bad92800e9eaf57dec8cebc17ad` | **15,951** |
| 7 | `literature/emc-post-degrader-options/emc_pazopanib_pubmed.txt` | `a88c3661fcc535215f071a3b4fe4c22110dae6c5` | **19,163** |
| 8 | `literature/emc-partner-events/nct02066285_ctgov_v2_full.txt` | `9b1e5fcc8eeae807bd8fa98d37720c891f0f89de` | **16,971** |
| 9 | `emc-partner-events-r2/nct02066285_ctgov_results.txt` | `3c566f782dd0c7c9b984fe27df16ffb7c4aa59fc` | **5,755** |
| 10 | `emc-partner-events-r3/nct02066285_ctgov_v2_history.txt` | `ebd3e4d082630634efcbc408fb74a355da44019d` | **198** |
| 11 | `literature/emc-partner-events/huang2023_epmc_core.txt` (Huang) | `53b86f686d448a284affe5e7d45522f297dffb23` | **12,984** |
| 12 | `emc-partner-events-r2/_manifest.json` | `4b8fde7a8840467b0a37dbf8f2db3690efe704dd` | **3,784** |

**Nothing is absent.** Every object resolves locally without network access, so the reviewer can read
each one directly at the pin above. Retrieval command, read-only:

```
GIT_NO_LAZY_FETCH=1 git cat-file blob <blob-id>
```

The frozen pooling artifact's `literature-cache` pin
`216bd1b5fb25a56b90ef3cc2373e1fe68322708f` is also resolvable in this session (its tree enumerates
72,207 paths). ⚠ Items 2–5 repeat unchanged blobs that also appear under other named slugs; **no
duplicate copies were made** and none is needed — one blob id is one object.

## ⛔ Huang Table 1 — the one thing that is NOT here, stated plainly

Item 12, `emc-partner-events-r2/_manifest.json`, **documents earlier 403 attempts. It is NOT a
delivered Table 1 PDF**, and it must not be read as one. Item 11 is the Europa PMC core text, which
is a different object from a publisher Table 1.

**No previously retained human PDF or human extraction original with a known locator was found for
Huang Table 1.** ⚠ Artifact prose asserting that a human read that table is **not** such an original
and is not offered as one.

⛔ Per the request, **no hunt and no reconstruction of that missing human source was attempted**, and
none should be inferred from this record. It stays a named absence.

## Scope

This is a locator answer only. ⛔ It makes no scientific claim, revalidates nothing, and does not
touch the FP paper — its independent final review is running on immutable `f44b75588`. This request
did not serialize the healthy P-ST and P-AB owners, which continued throughout.
