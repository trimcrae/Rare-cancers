> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check done: my gap measurement reproduces W15's 908/0/214/1 exactly; the extended ingester exits 0 on real committed inputs; 19/19 new tests pass at exit 0 and W15's original 17/17 still pass unchanged; the 5-mutation run fails at exit 1 catching all five; `git status` shows no modified tracked file (only the coordinator's own untracked reports).

---

## Worker

**W15b**, Lane 15 (refill) — data-ingestion / normalisation / evidence-retention.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my own system context. This is not an observed fact; the coordinator must extract the served model from the transcript. No environment variable names a model.

`date -u` at start: `Tue Sep  8 02:04:07 UTC 2026` (first tool call). At end: `Tue Sep  8 02:13:08 UTC 2026`.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (verbatim; the three long proxy host-list lines `no_proxy`/`NO_PROXY`/`GLOBAL_AGENT_NO_PROXY` and `JAVA_TOOL_OPTIONS` elided as marked — they contain no model):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=... (host list only)
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_DEBUG=true
CLAUDE_PID=522
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_EFFORT=medium
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDECODE=1
SESSION_INGRESS_URL=https://api.anthropic.com
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
GLOBAL_AGENT_NO_PROXY=... (host list only)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=... (proxy/truststore only)
NO_PROXY=... (host list only)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
```

**⚠ The read commit is no longer `92abbcb`.** At my start `HEAD=103ff76f1d66426420c56a4d49752eb84f5f5c39` — the coordinator has been committing this campaign's reports throughout my run. I verified this does not contaminate the measurement:

```
$ git merge-base --is-ancestor 92abbcb905cacf07f14b238db50d1b98f6590374 HEAD && echo IS-ANCESTOR
IS-ANCESTOR
$ git diff --name-only 92abbcb905cacf07f14b238db50d1b98f6590374 HEAD | grep -vc 'opus-capacity-campaign-20260908'
0
```

**Zero files outside the campaign directory changed.** Every scientific artifact I read is byte-identical to `92abbcb`. No repository file was created or modified by me; all execution under `/tmp/claude-0/w15b/`.

## Question

**Does a second `FT_QUOTE`-tier retained fact exist anywhere in this repository — i.e. is the retention gap W15 measured a tooling gap or a genuine evidence gap?**

Open because W15 measured exactly **one** full-text-quote-tier record and correctly refused to guess which way the binary falls. If a wider adapter surfaces more, the evidence was read and committed and only the reader was missing (tooling, cheap). If it does not, no tooling helps (evidence, expensive). Nothing between those two answers was assumed.

## Prior-work check

```
$ git ls-files | rg -i "fulltext|full-text|sweep|corpus|quote|extract"
   (36 paths — full list in Method below)
$ rg -n "^## |^### " research/autonomy/.../reports/W13-provenance-identity-contract.md
```

W13 built `scripts/validate_identity_contract.py` + `systems/schema/identity-provenance.schema.json`, which asks *whether a committed count's unit (patient / tumour / specimen) is declared* and exits 1 on 41 violations. That is a **validator over units of counting**; mine is an **ingester over retained quotations**. No overlap in input, output, or failure mode, and I did not touch W13's files.

I performed **zero network retrieval** — no probe, no fetch, no route replay changed or unchanged. Pazopanib, Sunitinib 2014, Trabectedin/RT 2018, Wagner 2020 and CTARC 2022 are read only as committed records. I am not touching lane 11's source-index, the frozen external-validation comment, the registry, or `systems/graph/`. **No content-policy refusal occurred in this lane.**

## Method / inputs

Read-only. Python `3.11.15` (`[GCC 13.3.0]`), Linux, standard library only, no network. Scratch: `/tmp/claude-0/w15b/`.

**Step 1 — independent reproduction.** `/tmp/claude-0/w15b/measure_gap.py`, written from scratch, importing `research/manuscripts/lint_citations.py` as a library for `PATTERNS`/`extract()`/`TRAILING` so the measurement uses the repository's own definition of an identifier.

**Step 2 — inventory, by structure not by filename.** The `git ls-files | rg` filename sweep returned 36 paths. **Filenames proved actively misleading, so I did not trust them:**

| Path | What its name implies | What it actually contains | Row |
|---|---|---|---|
| `research/literature/emc-clinical-sweep-fulltext.json` | retrieved full texts | **7,775 bytes of bare URLs.** 19 flat `key: url` strings (`.../PMC12504171/fullTextXML`, publisher landing pages). **No retrieved text whatsoever.** | PRIMARY |
| `research/literature/emc-prior-art-fulltext-screen-2026-08-10.json` | full-text corpus | term-hit **counts** over 237 full texts held on the `origin/literature-cache` branch (not in this tree); `counts`, `hits` — no quoted sentence | PRIMARY |
| `research/modalities/atr-hrd-sarcoma-series.json` | has a `fulltext` field | the field's value is `"CANNOT_DETERMINE — no open-access full text was retrievable"` — a **negative** marker | PRIMARY |
| `research/literature/emc-mortality-probe.json` | has `fulltext`/`sentences` | `caps.fulltext = "400"` is a **retrieval cap parameter**, not text | PRIMARY |

**W15's named successor target contains no full text.** Had I written the fifth adapter it proposed and stopped there, I would have measured `FT_QUOTE = 1` and reported "evidence gap" — the wrong answer, from the right-sounding file.

So I scanned **all 4,518 tracked `.json` files** structurally for quote-like keys (`quote`, `quotes`, `verbatim`, `corpus_quotes`, `quoted`, `excerpt`, `passage`, `text`, `sentence`, `body`, …). 1 file failed to parse (`research/modalities/e3-provenance-correction.json`, malformed JSON at line 22 — pre-existing, reported as UNKNOWN, not repaired). Result: **774 quote-like strings ≥25 chars across 80 files**, of which 170 sit on a node carrying a bound PMID/PMCID/DOI.

**Step 3 — the tier rule, which is the whole scientific content of this deliverable.** A row reaches `FT_QUOTE` **only** when the committed artifact itself declares full text was the read surface — either (a) the file says so in its own header, and that sentence is quoted verbatim in the code beside the field it licenses and asserted still present at load time, or (b) the individual record names a retrieved full-text artifact (a `*fulltext*.txt` path in the literature cache, or a Europe PMC `fullTextXML` URL). Everything else with a quote and an identifier lands at `ABSTRACT`. **No tier is upgraded by inference** — not from a sentence reading like Results prose, not from open access, not from a PMCID existing.

## Result

### R1 — Reproduction of W15's gap measurement: exact match

```
$ cd /tmp/claude-0/w15b && python3 measure_gap.py /home/user/Rare-cancers
kind    prose_md  any_tracked_json  ledger_rows  prose_only(no json)  prose_not_in_ledger
PMID         362              2210           75                    0                  287
DOI          368              4854          112                    0                  256
PMCID        178              3944           27                    0                  151
TOTAL        908             11008          214                    0
distinct ids in ledger (all kinds): 237; ledger rows: 237
tracked .json files carrying both a "denominator" and a "quote" field: 1 -> ['research/modalities/emc-care-delivery-evidence.json']
EXIT=0
```

| Quantity | W15 | W15b | Row |
|---|---|---|---|
| Distinct PMID/DOI/PMCID in `research/**/*.md` | 908 | **908** | PRIMARY |
| Prose identifiers absent from every tracked JSON | 0 | **0** | PRIMARY (negative) |
| Ledger rows of the three kinds | 214 | **214** | PRIMARY |
| Tracked `.json` pairing a `quote` with a `denominator` | 1 | **1** | PRIMARY |

All four reproduce. One wording correction, not a discrepancy: the ledger has **237 rows and 237 distinct ids**; 214 is the count restricted to PMID/DOI/PMCID (the other 23 are NCT/GEO/arXiv). W15's "214 distinct ids / 237 rows" reads as if 23 rows were duplicates; they are other kinds.

### R2 — A real discrepancy, in the campaign's own reports

My `measure_gap.py` ran while the campaign directory was still untracked. The coordinator committed 29 campaign reports mid-session, and those reports are now **tracked prose under `research/`**. Re-measuring with them in scope:

```
A. excl. campaign: prose_md_total=908   prose_only(no tracked json)=0    PMID=362/0  DOI=368/0  PMCID=178/0
B. incl. campaign: prose_md_total=1026  prose_only(no tracked json)=71   PMID=397/31 DOI=433/38 PMCID=196/2
```

| Finding | Value | Row |
|---|---|---|
| Identifiers the 29 campaign reports add to tracked prose | **118** | PRIMARY |
| Of those, identifiers anchored by **no** tracked `.json` | **71** | PRIMARY |

**This is a live gate consequence and the coordinator should see it before the next preflight.** `lint_citations.py` fails on any prose identifier that is neither anchored in a tracked JSON nor already in the ledger, and it is explicit that "what is NOT baselined is anything new." Workers were read-only by design, so we cited identifiers whose fetch products we were forbidden to commit — the write-isolation rule and the citation-anchor gate are in direct tension, and committing the reports realised it. I am **not** claiming these 71 are fabricated; they are identifiers real workers quoted whose fetch products never landed. UNKNOWN, not invalid. The repair is the coordinator's call (commit the fetch products, or ledger the identifiers deliberately — `--baseline` refuses to re-run, so it must be deliberate), and it is outside my write isolation.

### R3 — The binary, answered

```
$ cd /tmp/claude-0/w15b && python3 retained_facts_fulltext.py --root /home/user/Rare-cancers \
    --fetch-file research/literature/arxiv-aso-route.json \
    --fetch-file research/literature/venue-fee-pages-2026-08-24.json
{
 "n_records": 444,
 "n_distinct_sources": 372,
 "by_provenance_tier": {"FT_QUOTE": 70, "ABSTRACT": 104, "METADATA": 33, "UNCORROBORATED": 237},
 "by_denominator_status": {"STATED": 12, "UNKNOWN": 162, "NOT_APPLICABLE": 270},
 "by_access_status": {"FULL_TEXT": 87, "ABSTRACT_ONLY": 104, "METADATA_ONLY": 237,
                      "UNRECOVERED_403": 5, "UNRECOVERED_OTHER": 11},
 "n_with_computable_rate": 8,
 "n_ft_quote_distinct_sources": 35,
 "ft_quote_files": [
  "research/literature/fet-fusion-trial-eligibility-2026-08-07.json",
  "research/manuscripts/aso/lit-targets-aso-breakpoint-census.json",
  "research/manuscripts/aso/lit-targets-aso-round7-precedents.json",
  "research/manuscripts/emc-terminal-events-classified.json",
  "research/manuscripts/emc-terminal-events.json",
  "research/modalities/emc-care-delivery-evidence.json"
 ]
}
EXIT=0
```

**A second `FT_QUOTE`-tier record exists. So do sixty-eight more.**

| `FT_QUOTE` measure | Count | Row |
|---|---|---|
| Rows emitted | **70** | PRIMARY |
| Distinct (source identifier, quoted text) pairs | **48** | PRIMARY |
| Distinct source identifiers | **35** | PRIMARY |
| Committed files supplying them | **6** | PRIMARY |
| W15's baseline, reproduced unchanged by running W15's module alone | **1** | PRIMARY |

The 70 → 48 shrinkage is honest duplication, not inflation: `emc-terminal-events.json` and its hand-labelled companion `emc-terminal-events-classified.json` carry the same 18 individual events and 3 aggregate splits. Both are ingested because they are separately committed artifacts; deduplication is a query concern, and I report the deduplicated number beside the raw one rather than picking whichever is more flattering.

Per file: `emc-terminal-events-classified.json` 27, `emc-terminal-events.json` 22, `lit-targets-aso-breakpoint-census.json` 16, `lit-targets-aso-round7-precedents.json` 3, `emc-care-delivery-evidence.json` 1 (W15's original), `fet-fusion-trial-eligibility-2026-08-07.json` 1.

**What licensed each tier, checkably:**

| File | Licence | Kind | Row |
|---|---|---|---|
| `emc-terminal-events.json` | own `corpus` block: `"full_texts_retrieved": 328`, `"death_sentences_retrieved": 577` | file-level declaration | PRIMARY |
| `emc-terminal-events-classified.json` | own `_readme`: "open-access EMC literature that the terminal-event probe retrieved" | file-level declaration | PRIMARY |
| `lit-targets-aso-breakpoint-census.json` | own `_what`: "retrieved as open-access full text, with the verbatim sentence behind each junction" | file-level declaration | PRIMARY |
| `lit-targets-aso-round7-precedents.json` | per-record `source: origin/literature-cache:literature/aso-round7-ref39-fulltext/pmc_PMC10787139_galnac_fulltext.txt` | record-level marker | PRIMARY |
| `fet-fusion-trial-eligibility-2026-08-07.json` | per-record `url: .../PMC7563993/fullTextXML` | record-level marker | PRIMARY |
| `emc-care-delivery-evidence.json` | `corpus_quotes[]` (W15's adapter, unchanged) | file-level | PRIMARY |

Distinct `FT_QUOTE` source identifiers: `9060841, 11156374, 12826747, 18521326, 21941486, 22567356, 22569967, 23115670, 23213584, 24345066, 25177237, 26125202, 27418251, 28638563, 29937513, 29977924, 31020999, 32612944, 32963861, 32967265, 35251555, 35488288, 35494187, 35665108, 35775709, 35910216, 36097623, 36103645, 36326382, 36614077, 36636521, 40885991, 41755350, 41799218, PMC10787139`.

Deliberately **not** promoted, and each is a case the tests pin: `fet-fusion-chaperone-clientship-2026-08-27.json` (10 verbatim strings, but its own header says they were read "from PubMed … through the NCBI MCP tools" and one record labels itself "in the abstract's framing" → all 10 stay `ABSTRACT`); `atr-hrd-sarcoma-series.json` (`fulltext: "CANNOT_DETERMINE"` → not a marker); every record whose only full-text evidence would have been an open-access PMCID.

Also excluded, and this matters: the ~200 `quote` fields in `research/autonomy/review-seats/*.json` quote **this repository's own manuscripts**, not sources. None carries an identifier, so none produces a row; a test pins that on a real committed seat file. Counting them would have inflated the answer by a factor of four with zero literature content.

### R4 — Verdict

**The retention gap is a TOOLING gap, not an evidence gap** — decisively, and by a wide margin. This repository has read and committed the verbatim text of at least **35 distinct sources**, spanning exon-resolved fusion breakpoints, patient-level terminal events, and a registry's cause-of-death strata. W15's `FT_QUOTE = 1` measured its own adapter coverage, not the corpus. Three committed files, all named without the word "fulltext", each hold more full-text-quote evidence than the file W15 nominated — which holds none.

The corrected shape of the gap: of 908 prose identifiers, **7** had a machine-readable retained fact under W15's adapters; **≈174** do under these (70 `FT_QUOTE` + 104 `ABSTRACT`), i.e. roughly **19%** rather than 0.8%. The remaining ~730 still have nothing to ingest, and that residue is a real evidence gap — but it is four-fifths of the problem, not all of it, and the first fifth was already paid for.

## Validation evidence

**RUN.** Environment: Python 3.11.15, Linux, no network, cwd `/tmp/claude-0/w15b`, repository read-only.

1. **Gap reproduction** — `python3 measure_gap.py /home/user/Rare-cancers` → output in R1, **EXIT=0**.
2. **W15's module alone, re-run to confirm the baseline** — `python3 retained_facts.py --root /home/user/Rare-cancers` → `{"FT_QUOTE": 1, "ABSTRACT": 6, "METADATA": 0, "UNCORROBORATED": 237}`, **EXIT=0**. Reproduces W15's `FT_QUOTE = 1` exactly.
3. **Extended ingester on real committed inputs** — command and full output in R3, **EXIT=0**.
4. **New test suite** —
```
$ RARE_CANCERS_ROOT=/home/user/Rare-cancers python3 -m unittest test_retained_facts_fulltext -v
...
Ran 19 tests in 0.135s
OK
EXIT=0
```
5. **W15's original suite, unmodified, still green against the shared module** —
```
$ RARE_CANCERS_ROOT=/home/user/Rare-cancers python3 -m unittest test_retained_facts
Ran 17 tests in 0.006s
OK
EXIT=0
```
6. **Mutation check — proof the new tests are not vacuous.** Copied to `/tmp/claude-0/w15b/mut/`, five defects injected, each asserted present before the run:
   - **M1** every quote treated as full text (`ft = True`)
   - **M2** a negative `"CANNOT_DETERMINE — no open-access full text"` field read as a full-text marker
   - **M3** an unbound quote becomes a fact under a placeholder identifier
   - **M4** a denominator regexed straight out of the quoted sentence
   - **M5** a stale file-level declaration keeps its tier instead of raising
```
$ RARE_CANCERS_ROOT=/home/user/Rare-cancers python3 -m unittest test_retained_facts_fulltext
FAIL: test_a_quote_with_no_declaration_is_ABSTRACT_not_FT_QUOTE  -- 'FT_QUOTE' != 'ABSTRACT'
FAIL: test_a_pmcid_alone_does_not_license_full_text              -- 'FT_QUOTE' != 'ABSTRACT'
FAIL: test_a_field_saying_full_text_was_NOT_obtained_is_not_a_marker
FAIL: test_an_unbound_quote_yields_no_row
FAIL: test_review_seat_quotes_are_not_literature_facts
FAIL: test_a_number_inside_the_quoted_sentence_is_not_a_denominator
FAIL: test_a_missing_declaration_raises_rather_than_keeping_the_tier
Ran 19 tests in 0.078s
FAILED (failures=7)
EXIT=1
```
   All five mutations caught (M1→2 tests, M2→1, M3→2, M4→1, M5→1). The mutated copy is discarded; the clean modules are returned below.
7. **Tree untouched** — `git status --porcelain` shows no modified tracked file; the only entries are the coordinator's own untracked campaign reports.

**PROPOSED (NOT RUN).** `scripts/preflight.sh` (the brief forbids running it). Deduplicating `emc-terminal-events.json` against its classified companion. `systems/schema/retained-fact.schema.json`.

## Limitations

- **The tier rule is a declaration reader, not a verifier.** `FT_QUOTE` here means *a committed artifact states full text was the read surface*. It does not verify the retrieval happened, and it cannot: the retrieved texts for the census and terminal-event corpora live on the `origin/literature-cache` branch, not in this tree. If an artifact's header overstates its own retrieval, this module inherits that overstatement. It is one strictly weaker claim than "we hold the text", stated as such.
- **The 6 declarations are hand-listed.** They are quoted verbatim in the code and asserted present at load time (M5 proves the assertion fires), so a reader can check every one — but a seventh artifact declaring full text in different words is invisible until someone adds it. `FT_QUOTE = 70` is therefore a **lower bound**, and the verdict "tooling gap" only strengthens if it rises.
- **70 rows contain 48 distinct (source, quote) pairs.** Two committed artifacts describe the same 21 events. Both numbers are reported; neither is the "real" one without a stated dedup policy.
- **`QUOTE_SOURCES` is 39 hand-listed files**, chosen from the structural scan of all 4,518 tracked JSON. It is not corpus-wide. Files omitted are ones whose quotes are unbound and would yield no rows.
- **One tracked file could not be parsed** — `research/modalities/e3-provenance-correction.json`, malformed JSON. Its contents are **UNKNOWN**, not zero. I did not repair it (read-only).
- **Numbers inside quoted sentences are not parsed**, following W15. The only lift is a bare `n=<int>` from a `stratum`/`design`/`cohort` field whose declared job is to state the stratum size. `test_a_number_inside_the_quoted_sentence_is_not_a_denominator` pins this against M4.
- **The 12 `STATED` denominators are small and source-specific** (2, 3, 13, 16, 29, 128, 439, …) and license nothing beyond their own row. `n_with_computable_rate = 8`, of which 3 are the same registry stratum counted twice across duplicate artifacts, and the source's own `note` — carried into `notes` — says those strata overlap and must not be pooled. Nothing here pools anything; there is no pooling operation in the module.
- **This establishes nothing clinical.** It is a data-structure measurement. It cannot bear on EMC efficacy, safety, selectivity or readiness, creates no cohort, no patient and no denominator that a committed artifact did not already state, and every row is a re-expression of committed text.
- **The R2 finding is a process observation about this campaign**, made from a commit range, not a scientific result. I did not verify any of the 71 identifiers.

## Code

Proposed path `research/manuscripts/retained_facts_fulltext.py` (**the coordinator writes it; I did not**). It **imports** W15's `retained_facts` rather than editing it — an extension is structurally incapable of relaxing an invariant it does not own, which is why every row here still passes through W15's `__post_init__` unchanged.

```python
#!/usr/bin/env python3
"""W15b — the FULL-TEXT-QUOTE adapters for `retained_facts`.

⭐ WHY THIS IS A SEPARATE MODULE AND NOT AN EDIT. W15's `RetainedFact` owns three invariants
(an unknown denominator stays UNKNOWN and never becomes 0; a failed fetch stays a first-class
row; tier FT_QUOTE requires the quoted text). This module IMPORTS that class and constructs it,
so it is structurally incapable of relaxing any of them -- every row here goes through W15's
`__post_init__` unchanged. An edit to the original could have loosened a check by accident; an
extension cannot.

⭐ THE QUESTION THIS EXISTS TO ANSWER, AND IT IS A MEASUREMENT, NOT A FEATURE. W15 measured that
the tracked corpus held exactly ONE `FT_QUOTE`-tier record and named the successor question:
does a second one exist anywhere? If yes, the retention gap is a TOOLING gap -- the evidence was
read and is committed, and only the reader was missing. If no, it is an EVIDENCE gap and no
tooling closes it. The adapters below are the instrument for that one binary.

⛔ WHAT DECIDES THE TIER, AND IT IS NEVER MY JUDGEMENT. A record reaches FT_QUOTE only when the
committed artifact ITSELF declares that full text was the surface that was read -- either

  (a) the file states it in its own prose header, and that statement is quoted verbatim in
      `FULL_TEXT_DECLARATIONS` below beside the field it licenses, so a reader can check the
      claim against the file without trusting me; or
  (b) the individual record names a retrieved full-text artifact (a `*fulltext*.txt` path in the
      literature cache, or a Europe PMC `fullTextXML` URL).

Everything else with a quote and a bound identifier lands at ABSTRACT. ⛔ NO TIER IS UPGRADED BY
INFERENCE -- not from a sentence "looking like Results prose", not from a paper being open
access, not from a PMCID existing. Guessing the read surface is exactly how a repository comes
to believe it read a paper it only saw the abstract of.

⛔ NOTHING IS RETRIEVED AND NOTHING IS PARSED OUT OF PROSE. Like W15, this reads committed
artifacts and re-expresses them. The ONLY number lifted from a sentence is a bare unambiguous
`n=<int>` in a field whose declared job is to state the stratum size; every other number stays
inside the quoted text where the source put it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Iterable, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retained_facts as rf  # noqa: E402  -- W15's module; the invariants live there

# --------------------------------------------------------------------------------------
# (a) File-level full-text declarations. KEY = repository-relative path. VALUE = the verbatim
# substring of that file's own header which states that full text was read. The loader ASSERTS
# the substring is actually present; if an artifact's header is reworded, this raises rather
# than silently keeping a tier the file no longer claims.
# --------------------------------------------------------------------------------------
FULL_TEXT_DECLARATIONS = {
    "research/manuscripts/aso/lit-targets-aso-breakpoint-census.json":
        "retrieved as open-access full text, with the verbatim sentence behind each junction",
    # emc-terminal-events.json states the retrieval size in its own `corpus` block:
    # "full_texts_retrieved": 328. Its classification file is the hand-labelled companion.
    "research/manuscripts/emc-terminal-events.json": "full_texts_retrieved",
    "research/manuscripts/emc-terminal-events-classified.json":
        "open-access EMC literature that the terminal-event probe retrieved",
}

#: (b) Record-level markers. A value naming one of these is a retrieved full-text artifact.
_FT_SOURCE = re.compile(r"fulltext|full_text|fullTextXML", re.I)

TERMINAL_CLASSIFIED = "research/manuscripts/emc-terminal-events-classified.json"
TERMINAL_EVENTS = "research/manuscripts/emc-terminal-events.json"
BREAKPOINT_CENSUS = "research/manuscripts/aso/lit-targets-aso-breakpoint-census.json"
ROUND7 = "research/manuscripts/aso/lit-targets-aso-round7-precedents.json"
TCF12 = "research/literature/tcf12-nr4a3-breakpoint-primary-sources.json"
CHAPERONE = "research/literature/fet-fusion-chaperone-clientship-2026-08-27.json"

#: Quote-bearing keys actually observed in the tracked corpus (scan of all 4518 tracked .json).
QUOTE_KEYS = ("verbatim", "verbatim_second", "quote", "quotes", "quoted", "excerpt", "passage")
#: Identifier keys actually observed beside them.
ID_KEYS = ("pmid", "pmcid", "doi")

#: ⛔ A quote is only a RETAINED LITERATURE FACT if it is bound to a source identifier. The
#: repository's review-seat files carry 200+ `quote` fields that quote OUR OWN manuscript back at
#: us; none has a PMID, and none may become a literature row. This threshold is what excludes
#: them, and `test_review_seat_quotes_are_not_literature_facts` pins that.
MIN_QUOTE_CHARS = 20


def _load(root: str, rel: str) -> Any:
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return json.load(fh)


def declares_full_text(root: str, rel: str) -> bool:
    """True iff `rel` is listed above AND its file still literally contains the declaration.

    ⛔ RAISES on a listed file whose declaration has gone. A tier that outlives the sentence
    licensing it is the failure this whole module is trying not to commit."""
    decl = FULL_TEXT_DECLARATIONS.get(rel)
    if decl is None:
        return False
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        if decl not in fh.read():
            raise rf.RetentionError(
                f"{rel} no longer contains its full-text declaration {decl!r}; "
                "the FT_QUOTE tier it licensed is no longer claimed by the artifact")
    return True


def _bare_n(text: Optional[str]) -> Optional[float]:
    """A bare unambiguous `n=<int>`, or None. Same rule W15 applied to `design`.

    ⛔ Only this one form. Nothing else is lifted out of a sentence."""
    m = re.search(r"\bn\s*=\s*(\d+)\b", text or "")
    return float(m.group(1)) if m else None


def _first_id(node: dict) -> Optional[tuple[str, str]]:
    for k in ID_KEYS:
        for cand in (k, k.upper()):
            v = node.get(cand)
            if v not in (None, ""):
                ident = rf._norm_id(v)
                if ident:
                    return ident, rf._kind_of(ident)
    return None


def _record_names_full_text(node: dict) -> bool:
    for k in ("source", "url", "read_via", "fulltext", "full_text", "source_file"):
        v = node.get(k)
        if isinstance(v, str) and _FT_SOURCE.search(v):
            # ⛔ A field that says full text was NOT obtained is not a full-text marker.
            if re.search(r"CANNOT_DETERMINE|not retriev|no open-access|unavailable", v, re.I):
                return False
            return True
    return False


def from_quoted_records(doc: Any, rel: str, file_declares_full_text: bool) -> list[rf.RetainedFact]:
    """Every node in `doc` that carries a quote AND a bound source identifier.

    Generic on purpose: the corpus has no single quote schema (`verbatim`, `quote`, `quotes`,
    `verbatim_second`), so a per-file adapter would have to be rewritten for each and would miss
    the next one. This walks the real shapes instead of assuming one.

    ⛔ A node WITHOUT a bound PMID/PMCID/DOI yields NO ROW. That is not a silent drop: an
    unbound quote is not a fact about a source, it is a sentence, and the corpus is full of
    sentences that quote this repository's own manuscripts back at it.
    """
    out: list[rf.RetainedFact] = []
    seen: set[str] = set()

    def emit(node: dict, quote: str, path: str, subject_hint: str) -> None:
        ident_kind = _first_id(node)
        if ident_kind is None:
            return
        ident, kind = ident_kind
        ft = file_declares_full_text or _record_names_full_text(node)
        tier = "FT_QUOTE" if ft else "ABSTRACT"
        access = "FULL_TEXT" if ft else "ABSTRACT_ONLY"
        # A stratum/design field is the only place a denominator is allowed to come from.
        den = _bare_n(node.get("stratum") or node.get("design") or node.get("cohort"))
        num = node.get("emc_deaths")
        num = float(num) if isinstance(num, (int, float)) else None
        rid = f"QUOTE-{os.path.basename(rel)}:{path}"
        if rid in seen:
            return
        seen.add(rid)
        out.append(rf.RetainedFact(
            record_id=rid,
            source_id=ident, source_id_kind=kind,
            subject=str(node.get("label") or node.get("category") or node.get("series")
                        or node.get("kind") or subject_hint),
            claim=quote.strip(),
            quote=quote.strip(),
            numerator=num,
            denominator=den,
            denominator_status="STATED" if den is not None else "UNKNOWN",
            denominator_means=node.get("stratum") or node.get("design") or node.get("cohort"),
            access_status=access,
            retrieval_date=None,   # ⛔ never today's date as a stand-in
            provenance_tier=tier,
            ingested_from=rel,
            notes=node.get("note") or node.get("role") or node.get("what_it_establishes"),
        ))

    def walk(node: Any, path: str, subject_hint: str) -> None:
        if isinstance(node, dict):
            hint = str(node.get("_what") or subject_hint)
            for k, v in node.items():
                if k in QUOTE_KEYS:
                    if isinstance(v, str) and len(v.strip()) >= MIN_QUOTE_CHARS:
                        emit(node, v, f"{path}/{k}", hint)
                    elif isinstance(v, list):
                        for i, s in enumerate(v):
                            if isinstance(s, str) and len(s.strip()) >= MIN_QUOTE_CHARS:
                                emit(node, s, f"{path}/{k}[{i}]", hint)
                            elif isinstance(s, dict):
                                walk(s, f"{path}/{k}[{i}]", hint)
                else:
                    walk(v, f"{path}/{k}", hint)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]", subject_hint)

    walk(doc, "", os.path.basename(rel))
    return out


#: The tracked artifacts scanned for quoted literature facts. Chosen by a structural scan of all
#: 4518 tracked .json files for a quote-like key, NOT by filename -- see the report. Files whose
#: quotes are unbound (review seats, venue-fit, policy pages) are absent because they yield no
#: rows, and passing them changes nothing.
QUOTE_SOURCES = (
    TERMINAL_CLASSIFIED, TERMINAL_EVENTS, BREAKPOINT_CENSUS, ROUND7, TCF12, CHAPERONE,
    "research/literature/live-lane-answers-2026-08-09.json",
    "research/literature/ndrg1-kinase-attribution-2026-08-28.json",
    "research/literature/fet-fusion-trial-eligibility-2026-08-07.json",
    "research/manuscripts/aso/fusion-junction-aso-coverage-ladder.json",
    "research/manuscripts/aso/fusion-junction-aso-reagent-coverage.json",
    "research/manuscripts/aso/tcf12-breakpoint-assignment.json",
    "research/manuscripts/emc-host-factor-inputs.json",
    "research/manuscripts/endpoint/emc-systemic-therapy-pooling.json",
    "research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json",
    "research/manuscripts/care-delivery/emc-absence-claims-refuted.json",
    "research/modalities/emc-rt-bed-reappraisal.json",
    "research/modalities/emc-icdo-contamination.json",
    "research/modalities/cd248-precedent.json",
    "research/modalities/hemcss-label-priorart.json",
    "research/modalities/emc-ret-activation-bar.json",
    "research/modalities/emc-ret-target-scan.json",
    "research/modalities/nr4a3-fusion-targets.json",
    "research/modalities/geo-gse28866-brunner-series.json",
    "research/modalities/atr-hrd-sarcoma-series.json",
    "research/modalities/nurr1-allosteric-vs-pocket5.json",
    "research/modalities/nr2f1-dormancy-lane.json",
    "research/modalities/hormone-partner-lane.json",
    "research/modalities/hspa8-promoter-hormone-grade.json",
    "research/modalities/emc-fet-idr-census.json",
    "research/modalities/emc-fet-construct-designs.json",
    "research/modalities/fusion-frame-trap-breakpoints.json",
    "research/literature/shared-vs-individualized-neoantigen-sources-2026-08-24.json",
    "research/literature/prmt5-ewing-expression-panel-composition-2026-08-10.json",
    "research/literature/no-wet-lab-archetypes-2026-08-12.json",
    "research/manuscripts/endpoint/emc-endpoint-alternatives.json",
    "research/manuscripts/endpoint/placebo-arm-calibration.json",
    "research/manuscripts/endpoint/placebo-arm-detail-inputs.json",
    "research/manuscripts/aso/lit-targets-aso-gap-length.json",
    "research/modalities/surfaceome-instrument-limits.json",
)


def ingest_quotes(root: str = rf.ROOT, sources: Iterable[str] = QUOTE_SOURCES) -> list[rf.RetainedFact]:
    out: list[rf.RetainedFact] = []
    for rel in sources:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            # ⛔ UNKNOWN, not zero. A named artifact that is absent is reported, never skipped.
            print(f"WARNING: declared quote source absent, no rows produced: {rel}",
                  file=sys.stderr)
            continue
        out.extend(from_quoted_records(_load(root, rel), rel, declares_full_text(root, rel)))
    return out


def ingest_all(root: str = rf.ROOT, extra_fetch_files: Iterable[str] = ()) -> list[rf.RetainedFact]:
    """W15's four adapters plus the quote adapters. Same row type throughout."""
    return rf.ingest(root, extra_fetch_files) + ingest_quotes(root)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=rf.ROOT)
    ap.add_argument("--fetch-file", action="append", default=[])
    ap.add_argument("--subject")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--ft-only", action="store_true", help="emit only FT_QUOTE-tier rows")
    a = ap.parse_args(argv)
    facts = ingest_all(a.root, a.fetch_file)
    if a.ft_only:
        facts = [f for f in facts if f.provenance_tier == "FT_QUOTE"]
    if a.subject:
        facts = rf.by_subject(facts, a.subject)
    if a.json:
        json.dump([f.to_json() for f in facts], sys.stdout, indent=1)
        print()
    else:
        summary = rf.summarise(facts)
        summary["n_ft_quote_distinct_sources"] = len(
            {f.source_id for f in facts if f.provenance_tier == "FT_QUOTE"})
        summary["ft_quote_files"] = sorted(
            {f.ingested_from for f in facts if f.provenance_tier == "FT_QUOTE"})
        json.dump(summary, sys.stdout, indent=1)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Proposed path `research/manuscripts/tests/test_retained_facts_fulltext.py`:

```python
#!/usr/bin/env python3
"""Behaviour tests for the full-text-quote adapters.

Each test names a way this module could OVERSTATE what the repository has read, and fails if it
does. The failure mode being defended against is one-directional and specific: a quote silently
promoted to FT_QUOTE when nothing committed says full text was the surface that was read.
"""
import os
import unittest

import retained_facts as rf
import retained_facts_fulltext as ext

ROOT = os.environ.get("RARE_CANCERS_ROOT", "/home/user/Rare-cancers")


class TierIsNeverUpgradedByInference(unittest.TestCase):
    """The single most dangerous defect available to this module."""

    NODE = {"pmid": "12345678", "verbatim": "A sentence long enough to count as a quotation here."}

    def test_a_quote_with_no_declaration_is_ABSTRACT_not_FT_QUOTE(self):
        got = ext.from_quoted_records(self.NODE, "x.json", file_declares_full_text=False)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0].provenance_tier, "ABSTRACT")
        self.assertEqual(got[0].access_status, "ABSTRACT_ONLY")

    def test_a_file_level_declaration_licenses_FT_QUOTE(self):
        got = ext.from_quoted_records(self.NODE, "x.json", file_declares_full_text=True)
        self.assertEqual(got[0].provenance_tier, "FT_QUOTE")
        self.assertEqual(got[0].access_status, "FULL_TEXT")

    def test_a_record_naming_a_retrieved_full_text_file_licenses_FT_QUOTE(self):
        node = dict(self.NODE, source="origin/literature-cache:literature/x/pmc_PMC1_fulltext.txt")
        got = ext.from_quoted_records(node, "x.json", file_declares_full_text=False)
        self.assertEqual(got[0].provenance_tier, "FT_QUOTE")

    def test_a_field_saying_full_text_was_NOT_obtained_is_not_a_marker(self):
        """`atr-hrd-sarcoma-series.json` carries
        `fulltext: "CANNOT_DETERMINE — no open-access full text was retrievable"`.
        Matching the word `fulltext` there would invert the record's meaning."""
        node = dict(self.NODE,
                    fulltext="CANNOT_DETERMINE — no open-access full text was retrievable; "
                             "only the search record above was read")
        got = ext.from_quoted_records(node, "x.json", file_declares_full_text=False)
        self.assertEqual(got[0].provenance_tier, "ABSTRACT",
                         "a negative full-text field must not read as a full-text marker")

    def test_a_pmcid_alone_does_not_license_full_text(self):
        node = {"pmid": "1", "pmcid": "PMC7563993", "verbatim": "Open access is not a read surface."}
        got = ext.from_quoted_records(node, "x.json", file_declares_full_text=False)
        self.assertEqual(got[0].provenance_tier, "ABSTRACT")


class OnlyBoundQuotesBecomeFacts(unittest.TestCase):
    def test_an_unbound_quote_yields_no_row(self):
        got = ext.from_quoted_records(
            {"quote": "A sentence with no source identifier anywhere near it."},
            "x.json", file_declares_full_text=True)
        self.assertEqual(got, [], "a quote with no bound identifier is a sentence, not a fact")

    def test_a_trivially_short_quote_yields_no_row(self):
        got = ext.from_quoted_records({"pmid": "1", "quote": "yes"}, "x.json", False)
        self.assertEqual(got, [])

    def test_review_seat_quotes_are_not_literature_facts(self):
        """Review-seat files quote THIS repository's own manuscripts. None carries a PMID, and
        none may become a row asserting a source said something."""
        rel = ("research/autonomy/review-seats/"
               "PUB-FUSION-PARTNER-475ad7d0c3bd0b587bce6591c3826a8c37c77d09-seat-statistics.json")
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            self.skipTest(f"{rel} absent")
        got = ext.from_quoted_records(ext._load(ROOT, rel), rel, file_declares_full_text=False)
        self.assertEqual(got, [])


class DeclarationsMustStillBeInTheFile(unittest.TestCase):
    def test_a_missing_declaration_raises_rather_than_keeping_the_tier(self):
        rel = "research/manuscripts/emc-terminal-events.json"
        saved = ext.FULL_TEXT_DECLARATIONS[rel]
        ext.FULL_TEXT_DECLARATIONS[rel] = "a sentence this artifact does not contain"
        try:
            with self.assertRaises(rf.RetentionError):
                ext.declares_full_text(ROOT, rel)
        finally:
            ext.FULL_TEXT_DECLARATIONS[rel] = saved

    def test_every_declared_file_really_declares_it(self):
        for rel in ext.FULL_TEXT_DECLARATIONS:
            if os.path.exists(os.path.join(ROOT, rel)):
                self.assertTrue(ext.declares_full_text(ROOT, rel), rel)

    def test_an_undeclared_file_is_not_full_text(self):
        self.assertFalse(ext.declares_full_text(ROOT, "research/literature/arxiv-aso-route.json"))


class DenominatorsAreLiftedFromNowhereButAStratumField(unittest.TestCase):
    def test_a_number_inside_the_quoted_sentence_is_not_a_denominator(self):
        node = {"pmid": "1", "quote": "Among the 16 patients who received chemotherapy, one died."}
        got = ext.from_quoted_records(node, "x.json", False)
        self.assertIsNone(got[0].denominator)
        self.assertEqual(got[0].denominator_status, "UNKNOWN")
        self.assertIsNone(got[0].rate, "an unknown denominator must not yield a rate")

    def test_a_bare_n_in_the_stratum_field_is_lifted(self):
        node = {"pmid": "1", "quote": "Eight of them died from tumours in this stratum.",
                "stratum": "no (neo)adjuvant chemotherapy, n=128", "emc_deaths": 8}
        got = ext.from_quoted_records(node, "x.json", False)
        self.assertEqual(got[0].denominator, 128.0)
        self.assertEqual(got[0].denominator_status, "STATED")
        self.assertAlmostEqual(got[0].rate, 8 / 128)


class AgainstTheRealTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.isdir(ROOT):
            raise unittest.SkipTest(f"repository not present at {ROOT}")
        cls.facts = ext.ingest_all(ROOT)
        cls.ft = [f for f in cls.facts if f.provenance_tier == "FT_QUOTE"]

    def test_more_than_one_full_text_quote_exists(self):
        """THE MEASUREMENT. W15 found exactly one. If this ever returns to 1, the retention gap
        is an evidence gap and the correct response is to say so, not to loosen a tier."""
        self.assertGreater(len(self.ft), 1)

    def test_every_full_text_row_carries_the_text_it_rests_on(self):
        for f in self.ft:
            self.assertTrue((f.quote or "").strip(), f.record_id)

    def test_no_ingested_row_hides_a_number_under_an_unknown_denominator(self):
        for f in self.facts:
            if f.denominator is not None:
                self.assertEqual(f.denominator_status, "STATED", f.record_id)
            if f.denominator_status != "STATED":
                self.assertIsNone(f.rate, f.record_id)

    def test_the_w15_care_delivery_quote_is_still_among_them(self):
        self.assertIn("research/modalities/emc-care-delivery-evidence.json",
                      {f.ingested_from for f in self.ft})

    def test_w15s_own_rows_are_unchanged_by_the_extension(self):
        base = rf.ingest(ROOT)
        self.assertEqual(base, self.facts[:len(base)],
                         "the extension must not alter a single row W15 produced")

    def test_failed_fetches_remain_first_class(self):
        facts = ext.ingest_all(ROOT, ["research/literature/venue-fee-pages-2026-08-24.json"])
        self.assertTrue(any(f.access_status.startswith("UNRECOVERED") for f in facts))


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

## Stop condition

**Set:** an executed extended ingester with the `FT_QUOTE` count established across the tracked corpus, a non-vacuous test run, and an explicit tooling-vs-evidence verdict.

**MET.** W15's gap measurement independently reproduced at 908 / 0 / 214 / 1. Extended ingester run on real committed inputs at **EXIT=0**, yielding **70 `FT_QUOTE` rows / 48 distinct (source, quote) pairs / 35 distinct sources across 6 files**, against W15's baseline of 1 which I also reproduced. 19 new tests at **EXIT=0**, W15's 17 still at **EXIT=0**, and a five-defect mutation run at **EXIT=1** catching all five. Verdict stated: **tooling gap**.

## Tool-call and wall-clock count actually used

**26 tool calls** (target ~40). Wall clock `02:04:07Z → 02:13:08Z` ≈ **9 minutes** (target ~40). No padding; returning on the stop condition.

## Next concrete action

**Two, ranked; the first is not mine to do and should not wait for the second.**

1. **Coordinator, before the next `preflight.sh`:** the 29 now-tracked campaign reports put **71 identifiers into `research/**/*.md` prose that no tracked `.json` anchors**, which is exactly what `lint_citations.py` is built to fail on and what its docstring calls "an ERROR the moment it is written". This is a foreseeable collision between this campaign's read-only write-isolation rule and the repository's citation-anchor gate, not a fabrication. Decide deliberately whether to commit the workers' fetch products or to ledger the identifiers; `--baseline` refuses to re-run, so there is no accidental path.

2. **Lane 15 successor:** with the tooling verdict settled, the open question is no longer *does retained evidence exist* but *is what we retained internally consistent*. Six committed artifacts now yield 48 distinct source-bound full-text quotations, and at least one source (`27418251`) is quoted by more than one of them. Run the ingester's own rows against each other and ask: **does any single source identifier carry two committed quotations that state incompatible numbers?** That is a finite, network-free contradiction check over 48 rows, it needs no new adapter, and unlike the count it can only be answered by actually reading what we already hold.

result: A second FT_QUOTE-tier retained fact does exist — 70 of them (48 distinct source-quote pairs, 35 distinct sources, 6 committed files) versus W15's baseline of 1 which I reproduced exactly, so the EMC repository's retention gap is a TOOLING gap not an evidence gap; W15's nominated target `emc-clinical-sweep-fulltext.json` was found to contain only bare URLs and no text, and I separately measured that the campaign's own 29 now-tracked reports introduce 71 prose identifiers that no tracked JSON anchors, which will fail `lint_citations.py` at the next preflight.
