> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

# W10f — For each W10e disagreement, which record is right, and can it be settled without a retrieval?

## Worker

- **W10f**, lane 10 refill, OPUS-CAPACITY-CAMPAIGN-20260908. **Read-only on the Git tree**; nothing written into `/home/user/Rare-cancers` (`git status --porcelain` = 0 lines at start and end). Scratch dir `/tmp/claude-0/w10f/` was created and stayed **empty** — no script file was needed.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a model; the coordinator must extract the served model from the transcript.
- `date -u` **start: `Tue Sep  8 02:50:27 UTC 2026`**; **end: `Tue Sep  8 02:54:40 UTC 2026`**.
- **HEAD actually read: `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`** at start; `4d950cf036294627b7ae67dfb306cc1875d702ac` at end. Neither is COMMON-BRIEF §1's frozen `92abbcb905cacf07f14b238db50d1b98f6590374`; the coordinator is committing to the shared checkout. Every artifact I read has mtime `Sep 4 12:16` / last-touching commit `14a3f172d6b494d872f6d2678c7d0caa7ef26ccc`, so the audited content is stable across the move.
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — the full start-of-run output is in tool call 1; the end-of-run re-run is identical. Four long `no_proxy`/`NO_PROXY`/`npm_config_noproxy`/`GLOBAL_AGENT_NO_PROXY`/`JAVA_TOOL_OPTIONS` lines are elided **in the second printing only** because they carry no identity information; all identity-bearing lines:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
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
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

## Stop condition (set up front)

Set before starting: **(i)** re-derive W10e's disagreement list independently, quoting both sides with `file:line`; **(ii)** classify every disagreement into (a)/(b)/(c)/(d) with counts; **(iii)** settle every class (a) row from committed evidence with working shown, routed not applied; **(iv)** name the minimal query for every class (b) row and execute at most three; **(v)** report the "census says unreachable / record elsewhere says reached" class first and separately. **All five MET.** Returning immediately.

## Question

**For each disagreement W10e found in the repository's literature-reachability record, which record is right — and can that be established without a single new retrieval?**

Open because W10e deliberately stopped at diagnosis: it enumerated the disagreements and explicitly declined to adjudicate any ("*This is an audit of a record, not a re-adjudication*", W10e Limitations). Nobody has asked which side of each disagreement the committed evidence actually supports.

**Headline answer: yes for the ones that matter.** 9 of 13 disagreements are settleable from committed evidence alone, and the single most important one — two sources the reachability record calls **unreachable** were in fact **read in full text at $0 on the same date** — is settled outright by a dated, explicit, self-declared correction already in the tree. **I issued no publisher request and replayed no denied route.** The only network calls I made were three `convert_article_ids` lookups (§4).

## Prior-work check

Read in full first: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W10e-reachability-record-staleness.md`, `reports/W10d-kawaguchi-hospital-enumeration.md`. W10b's sweep is closed and I opened no new sweep; W10c's overlap adjudication and W10d's hospital enumeration are **reused as inputs, not re-run** — specifically, W10d's finding that Kawaguchi 2003 (PMID 12599237) returns no PMCID is taken as transferred fact and I did **not** re-issue that conversion.

| # | command | what it showed |
|---|---|---|
| 1 | `for id in china2016 meisKindblom1999 … bishop2019; do grep -rln "$id" --exclude-dir=.git --exclude-dir=opus-capacity-campaign-20260908 . ; done` | Per-source file sets. **This is what found the class-5 evidence**: `drilon2008` and `bishop2019` appear in `emc-site-curation.json`, `emc-locoregional-eligibility.json`, `emc-radiotherapy-contradiction.json`, `emc-rt-bed-reappraisal.json` — files W10e never opened. |
| 2 | `grep -n "idIsNotOpenAccess" -r research/ --include=*.json --include=*.py --include=*.md` | 4 hits: the source claim at `emc-ipd-admissibility-2026-08-12.json:156`, plus `no-wet-lab-publication-archetypes.md:527`, `W16b-frechet-followup-adversarial.md:151` and W10e's own report — i.e. **the disputed claim has propagated into two downstream documents**. |
| 3 | `grep -n "read_from\|verification\|provenance" research/modalities/*.json` | The full-text provenance strings quoted in Result §A. |
| 4 | python id-set comparison of census / admissibility / `CANDIDATE_SOURCES` | 16 / 16 / **17** — a coverage gap W10e did not report. |

Closed items I confirm I did **not** touch: Pazopanib, anthracycline, sunitinib 2014, trabectedin/RT 2018, Wagner 2020, CTARC 2022 (all recorded as class (c) below and **left alone**); the NR4A Perspective refusal; PUB-EMC-CLASSIFICATION; Brenca; Hofvander/EGA; lane-11 source-index; `GSE4303`/`GSE28866`. No case was added to any denominator; no source's admissibility verdict was changed.

## Method / inputs

Read-only `python3` (stdlib `json` only), `grep`, `sed` over the live checkout at `3f5fc95d…`:

- `research/literature/emc-km-reachability-census-2026-08-25.json` (739 lines, 16 series, 4 rounds)
- `research/literature/emc-km-admissibility-2026-08-27.json` (804 lines, 16 series)
- `research/literature/emc-km-figure-retrieval-2026-08-25.json` (213 lines, 7 targets)
- `research/literature/emc-ipd-admissibility-2026-08-12.json` (195 lines, 7 papers + `step_1b`)
- **`research/modalities/emc-site-curation.json`, `emc-locoregional-eligibility.json`, `emc-radiotherapy-contradiction.json`, `emc-rt-bed-reappraisal.json`** — the four files that carry the decisive counter-evidence and were outside W10e's scope
- `research/modalities/emc_ipd_survival.py` (`CANDIDATE_SOURCES`), `research/modalities/emc-ipd-survival.json` (generated, `_do_not_hand_edit`)
- `scripts/emc_km_figure_fetch.py` (the retrieval ladder), `scripts/emc_km_reachability_census.py`
- `research/autonomy/opus-capacity-campaign-20260908/CLOSED-WORK.md`
- Tool: PubMed MCP `convert_article_ids` ×3 only.

**Re-derivation status.** Everything in §A–§D below is re-derived by me from the committed files and is **PRIMARY** unless marked. W10e's inventory reproduces exactly (16 sources; census tally `{retrieved 5, unresolved 2, free_to_read_but_not_retrieved 3, closed 6}`; admissibility `{admitted 2, refused_no_risk_row 3, unreachable 11}`; the four `routes: []` sets; the five OA-flag-vs-outcome rows; the `oa.fcgi` 404-for-all-seven). W10d's Kawaguchi PMCID result is **SECONDARY** (transferred, not re-verified by me).

---

## Result

### A. FIRST AND SEPARATE — the census says unreachable, the committed record says it *was* reached

This is the most important class, it has **two members**, and **both are settled from committed evidence with no retrieval.**

#### A1. `drilon2008` (PMID 18951519 / PMC2779719) — census `unresolved`, admissibility `unreachable`; the full text was read at $0

**Side 1 — the reachability record.** `research/literature/emc-km-admissibility-2026-08-27.json`, series `drilon2008`, round `km-figures-round5-2026-08-27`:
> `"verdict": "unreachable"`, `"why": "no free route returned the article today, so its figures have not been LOOKED at: the risk-row question is unasked, not answered no"`, `"route_used": null`

**Side 1b — the stronger form of the same claim.** `research/literature/emc-ipd-admissibility-2026-08-12.json:156`:
> `"finding": "drilon2008 (PMC2779719) and bishop2019 (PMC7771031) both return error code 'idIsNotOpenAccess' from the OA service. Their earlier HTTP 404 on fullTextXML was NOT an endpoint quirk -- these papers are not open access, and no open route will reach them."`

**Side 2 — the committed record of the article having been read.** `research/modalities/emc-site-curation.json:80` (`context_not_pooled` → `drilon2008`):
> `"verified_against": "the PMC full-text record PMC2779719, retrieved through the NCBI PMC full-text API"`

and, on the same object, verbatim sentences transcribed from the paper's Results:
> `"⭐_the_lung_confined_sentence": "This is the ONLY series in the reachable set that separates lung-CONFINED from lung-INVOLVED in its own words: 'The first site of metastasis was the lung in 80% of cases (63% with metastasis confined to the lungs and 17% with metastasis at other sites concurrent with lung disease).'"`

and an internal discrepancy only a full-text reader could see:
> `"⚠_internal_discrepancy": "The abstract says 87 patients and the Results say '86 evaluable patients'; the clinical registry carries 87. Recorded, not resolved."`

**Side 2b — the explicit, dated withdrawal.** `research/modalities/emc-site-curation.json:27`:
> `"⚠_SUPERSEDED_the_other_nine_series": "⛔ WITHDRAWN 2026-08-27. This file previously said: 'not open access. Europe PMC returns no PMC record and isOpenAccess: N for all nine remaining candidate series, so their site tables are unreachable at $0.' TWO of the nine have a PMC full-text record and both were read at $0 on 2026-08-27 — bishop2019 (PMC7771031) and drilon2008 (PMC2779719). The registry already carried both PMCIDs, next to `openAccess: false`. ⛔ THE ROOT CAUSE IS A CONFLATION: `openAccess` is a LICENCE field and it was read as an ACCESS statement."`

#### A2. `bishop2019` (PMID 31436747 / PMC7771031) — same shape, and a **third** record disagrees with both

**Side 1.** `emc-km-admissibility-2026-08-27.json`, series `bishop2019`: `"verdict": "unreachable"`, same `why` string, `"route_used": null`, four routes recorded (500 / 200-1817-html / 200-1816-html / 200-168147-html).

**Side 2.** `research/modalities/emc-radiotherapy-contradiction.json:10-11`:
> `"provenance": "primary",`
> `"read_from": "literature-cache: icdo-9231-size-round5/pmc_page_PMC7771031_emc_combined_modality.txt (PMC full text, HTTP 200)"`

— attached to `"cohort": "41 consecutive patients with localized EMC, MD Anderson, 1990-2016"`, `"median_followup_months": 94`, `"hr": 12.7`, i.e. quantities read out of the article.

**Side 3 (a third, contradicting record).** `research/modalities/emc-rt-bed-reappraisal.json:40-41`:
> `"verification": "API",`
> `"read_from": "Europe PMC core record (abstract) cached at literature-cache literature/emc-physical-modalities-r2/epmc_bishop_emc_rt.txt; the full text is isOpenAccess=N and was NOT retrieved"`

**Side 4.** `research/modalities/emc-locoregional-eligibility.json:20`:
> `"…DONE for THREE series that print a site table — chiusole2020 (n=59), masunaga2025 (n=171) and, added 2026-08-27, bishop2019 (n=41), reached through its PMC full-text record. ⚠ *Superseded, retained: "The other nine candidate series are not open access, so their site tables stay unreachable at $0 — a paywall, not a missing extraction."* That sentence read a LICENCE field as an ACCESS statement."`

#### Which record is right, and why — settled from committed evidence (class (a))

| | verdict |
|---|---|
| **Right** | `emc-site-curation.json:27,80`, `emc-locoregional-eligibility.json:20`, `emc-radiotherapy-contradiction.json:10-11` — **the full text of PMC2779719 and PMC7771031 was obtained at $0 on 2026-08-27.** |
| **Wrong as written** | `emc-ipd-admissibility-2026-08-12.json:156` ("no open route will reach them") — **refuted**. `emc-rt-bed-reappraisal.json:41` ("the full text is isOpenAccess=N and was NOT retrieved") — **the exact conflation `emc-site-curation.json:27` withdraws by name**. |
| **Right but misworded** | `emc-km-admissibility-2026-08-27.json`'s `why` string for both rows. |

**Working, three independent legs, none needing a retrieval:**

1. **An explicit dated correction beats an undated inference.** `emc-site-curation.json:27` is not my inference — it is the repository correcting itself in writing, on 2026-08-27, naming the two PMCIDs, naming the root cause, and marking the superseded sentence `⛔ WITHDRAWN`. `emc-rt-bed-reappraisal.json:41` states the withdrawn proposition verbatim (`isOpenAccess=N` ⇒ not retrieved). Under CLAUDE.md §1 ("do not embed retired instructions beside current ones") the withdrawal governs.
2. **Content that only a reader could produce.** `emc-site-curation.json:80` carries a quoted sentence from drilon2008's Results, a four-way printed site percentage breakdown, and an abstract-vs-Results discrepancy (87 vs "86 evaluable"). An abstract does not contain a Results-section word count discrepancy. This is positive evidence of reading, not an absence argument.
3. **The mechanism explains the apparent contradiction without either side lying.** `scripts/emc_km_figure_fetch.py:285-307` builds its route ladder as `oa_tgz_ftp`, `oa_tgz_https`, `oa_pdf_ftp`, `oa_pdf_https`, `europepmc_pdf_render`, `pmc_direct_pdf`, `pmc_legacy_pdf`, `caller_pdf_url` — **every rung is a PDF/graphics route. The NCBI PMC full-text API / PMC article text page is not on the ladder at all.** So "the figure PDF could not be fetched" and "the article text was read" are both true. The defect is the *wording*: the admissibility file generalises a PDF-route failure into `"no free route returned the article today"`.

**Corrected values, routed to the coordinator, NOT applied by me:**

| record | stands as | corrected to |
|---|---|---|
| `emc-km-admissibility-2026-08-27.json` `why` for `drilon2008`, `bishop2019` | verdict `unreachable` **stands** (the figure graphics genuinely were not obtained, so the risk-row question is genuinely unasked) | the `why` should read *"no free route returned the article **PDF/figure graphics** today"*, plus a cross-reference to `emc-site-curation.json:27`. **The §2.7 verdicts do not change and no curve becomes admissible.** |
| `emc-ipd-admissibility-2026-08-12.json:156` | retained verbatim as a dated record | append a `⛔ SUPERSEDED 2026-08-27` key alongside the file's existing `⭐_CLOSED_2026-08-25` pattern (the file already states `"⚠_this_scan_is_not_edited_otherwise": "…rewriting it would destroy that"`, so **append, never rewrite**) |
| `emc-rt-bed-reappraisal.json:41` | — | the clause *"the full text is isOpenAccess=N and was NOT retrieved"* is **false as of 2026-08-27** and must be struck. Whether its RT numbers are still abstract-sourced is a separate question I did not open. |
| `emc_ipd_survival.py:276,313` (mirrored in generated `emc-ipd-survival.json:87,174`) | `"full_text_reachable": "PMC2779719"` / `"PMC7771031"` | **these two are now correct as they stand** and should be kept — but `emc-ipd-admissibility-2026-08-12.json:157` instructs the opposite (*"They stay on the candidate list with full_text_reachable resolved to False"*). That instruction must be marked superseded, or a later maintainer will "fix" the correct value into a wrong one. |
| downstream propagation | — | `research/manuscripts/no-wet-lab-publication-archetypes.md:527` (*"Two papers are now definitively closed … return `idIsNotOpenAccess`"*) and `reports/W16b-frechet-followup-adversarial.md:151` repeat the refuted claim. **W16b's `drilon2008` REFUSAL is unaffected** — it rests on "percentage-only, no `{events, denom}`", which `emc-site-curation.json:80` independently confirms — but its access sentence is wrong. |

**⛔ What this does NOT change.** Nothing here admits a curve, changes a §2.7 verdict, adds a patient to any denominator, or makes any clinical claim. Both papers remain `figure_checked: false`. It corrects a *bookkeeping* statement about access.

### B. The full disagreement list, re-derived, with classification

**Counts: 13 disagreements — (a) 9 · (b) 3 · (c) 6 · (d) 2.** Rows D8/D9/D10 are each simultaneously (b) for a permitted per-source check and (c) for their denied publisher route; the class counts therefore sum to 20 across 13 rows and are reported per-route, not per-row.

| # | disagreement | side 1 (`file:line`) | side 2 (`file:line`) | class | re-derived? |
|---|---|---|---|---|---|
| **D1** | drilon2008 unreachable vs full text read at $0 | `emc-km-admissibility-2026-08-27.json` `drilon2008.retrieval` + `emc-ipd-admissibility-2026-08-12.json:156` | `emc-site-curation.json:27,80` | **(a)** | PRIMARY, **new — W10e did not have it** |
| **D2** | bishop2019 unreachable vs full text read at $0 | `emc-km-admissibility-2026-08-27.json` `bishop2019.retrieval`; `emc-rt-bed-reappraisal.json:41` | `emc-site-curation.json:27`; `emc-radiotherapy-contradiction.json:10-11`; `emc-locoregional-eligibility.json:20` | **(a)** | PRIMARY, **new** |
| **D3** | "`idIsNotOpenAccess` ⇒ definitively closed" vs `oa.fcgi` returning 404/`error_code: null` for **all seven** targets, including all five successfully retrieved | `emc-ipd-admissibility-2026-08-12.json:156` | `emc-km-figure-retrieval-2026-08-25.json:37,64,91,118,145,173,201` (all `"http": 404`), `:41,68,95,122,149,177,205` (all `"error_code": null`) | **(a)** | PRIMARY (W10e found it; **I add the positive control**, below) |
| **D4** | same file, self-contradiction: "retry before concluding anything" vs "definitively closed" | `emc-ipd-admissibility-2026-08-12.json` `⚠_two_of_seven_were_never_retrieved`: *"this is a statement about THAT ENDPOINT… Retry via a different route before concluding anything about them."* | `:156` *"no open route will reach them"* | **(a)** | PRIMARY, **new** |
| **D5** | `emc_ipd_survival.py` internal: header says `figure_checked: False` rows are the unreachable ones, yet two such rows carry a truthy `full_text_reachable` | `emc_ipd_survival.py:230-231` (*"Rows still reading `figure_checked: False` are the ones whose full text this program cannot reach at $0"*) | `emc_ipd_survival.py:276,313` | **(a)** | PRIMARY, **new** |
| **D6** | stale note: "no free-copy lookup has yet been run against its DOI (2026-08-25)" vs an 08-27 round that ran Unpaywall + OpenAlex + `caller_pdf_url` on that DOI | `emc_ipd_survival.py:277,314` | `emc-km-admissibility-2026-08-27.json` `drilon2008`/`bishop2019` `unpaywall`+`oa_locations`+`openalex_locations` blocks | **(a)** | PRIMARY, **new** |
| **D7** | coverage gap: `CANDIDATE_SOURCES` has **17** sources, census and admissibility have **16**; `immunosarc2emc2025` (n=24) has **no reachability record at all** | `emc_ipd_survival.py:329` | census/admissibility `series` arrays (16 each) | **(a)** | PRIMARY, **new** |
| **D8** | `japan2003` Unpaywall `is_oa: true`/bronze, 1 OA location = the exact Wiley URL that 403s | `emc-km-admissibility-2026-08-27.json` `japan2003.retrieval.oa_locations[0]` | same object, `routes[0].http: 403`, `browser_http: 403` | **(a)** resolved as *no disagreement*; publisher route = **(c)** | PRIMARY (W10d/W10e) |
| **D9** | `huang2023` — identical shape (bronze, 1 location = the modernpathology URL that 403s) | `…huang2023.retrieval.oa_locations[0]` | same object, `routes[0].http: 403` | **(a)** as above; **(b)** for the PMCID check | PRIMARY |
| **D10** | `seer270_2022` — gold `cc-by-nc-nd` (Unpaywall) vs `cc-by-sa` (OpenAlex/DOAJ) for the same article; DOAJ location has no recorded outcome | `…seer270_2022.retrieval.oa_locations` / `openalex_locations` | same object, `routes[0].http: 403` | licence conflict **(d)**; publisher route **(c)** | PRIMARY |
| **D11** | `bishop2019` green OA (sole location = PMC) and a `caller_pdf_url` **HTTP 200 / 168,147 bytes** sitting under verdict `unreachable` | `…bishop2019.retrieval.routes[3]`, `unpaywall.oa_status: "green"` | `…bishop2019.verdict: "unreachable"` | **(d)** — the artifact stores no field distinguishing "served the article" from "served a wall at 200"; the 2026-08-12 `step_1b` record shows an HTTP 200 `text/html` reCAPTCHA interstitial has exactly this shape | PRIMARY |
| **D12** | census assigns `closed` from an Unpaywall `is_oa: false` flag with **zero** HTTP attempts, while refusing to believe the same aggregator's `true` | `scripts/emc_km_reachability_census.py:81-95` | `emc-km-admissibility-2026-08-27.json`: `routes: []` for `meisKindblom1999`, `ussc2022`, `uMich2023`, `china2016`, `stacchiotti2019pazopanib`, `stacchiotti2014sunitinib` | **(a)** — asymmetry is settleable as a *labelling* defect (`closed` ⇒ `not_attempted`); the underlying access status is **(b)/(c)** per source | PRIMARY (W10e) |
| **D13** | `CLOSED-WORK.md` records Sunitinib 2014's "three ordinary institutional 403 routes exhausted", Wagner 2020 and Trabectedin/RT 2018 `EGRESS_BLOCKED`, and the pazopanib EudraCT/erratum — **none** appear in the machine-readable record | `CLOSED-WORK.md` (Unrecovered sources) | `emc-km-admissibility-2026-08-27.json` `stacchiotti2014sunitinib.routes: []`; the other three absent entirely | **(a)** as a bookkeeping repair; **(c)** for every underlying route | PRIMARY (W10e) |

**The positive control I add to D3 (this is what makes D3 class (a) rather than merely suspicious).** `emc-ipd-admissibility-2026-08-12.json` `step_1b_figure_route_probe.routes_tried[3]` records `oa.fcgi` as **`"✅ WORKS -- returns licence and package location"`**, with the concrete example *"For PMC7308468: licence CC BY, package oa_package/c5/67/PMC7308468.tar.gz."* Thirteen days later `emc-km-figure-retrieval-2026-08-25.json:63-69` records `oa.fcgi?id=PMC7308468` → **`"http": 404, "error_code": null, "license": null`** — for the *same PMCID it had previously served successfully*, and for a paper whose PDF was retrieved at HTTP 200 in that very run. **So the endpoint itself degraded between 2026-08-12 and 2026-08-25; the 404s are an endpoint fact, not an article fact.** That is a controlled, retrieval-free demonstration that the `oa.fcgi` signal in the 08-25 record carries zero discriminating power, and it removes the last support from `:156`'s word "definitively."

### C. Class (c) — recorded and left alone, not attempted

Six routes. **I issued no request against any of them and propose none.**

| source | route recorded denied | where |
|---|---|---|
| Pazopanib (`stacchiotti2019pazopanib`, PMID 31331701) | primary full paper + observed exposure window unrecovered; EudraCT `2013-005456-15`; mortality erratum unread | `CLOSED-WORK.md`; census `routes: []` |
| Anthracycline (PMID 24345066 / PMC3879193) | retention limited to median 4 cycles (range 1-8) + one first-cycle toxicity stop | `CLOSED-WORK.md` |
| Sunitinib 2014 (PMID 24703573) | three ordinary institutional 403 routes exhausted; **no 2012 substitution** | `CLOSED-WORK.md` |
| Trabectedin/RT 2018 (DOI 10.4172/clinical-practice.1000433) | historical `EGRESS_BLOCKED` (an old proxy outcome, not a biological refusal) | `CLOSED-WORK.md` |
| Wagner 2020 (PMID 32856598) | methods unresolved, ordinary route historically `EGRESS_BLOCKED` | `CLOSED-WORK.md` |
| CTARC 2022 / `seer270_2022` (PMID 35144048) | latest publisher 403; abstract retained | `CLOSED-WORK.md` **and** `emc-km-admissibility-2026-08-27.json` `seer270_2022.retrieval.routes[0]` — the only source of the 16 whose denial is correctly recorded in both places |

⚠ **One framing note on the anthracycline row, flagged not resolved** (I make no change): `CLOSED-WORK.md` files it under *"Unrecovered / partially retained sources"* while both artifacts record it `retrieved` at HTTP 200 (2,609,773-byte PDF) and **admitted** under §2.7(a). These are compatible — `CLOSED-WORK.md` constrains which *quantities* were extracted, not whether the PDF was obtained — but the heading misleads on scan.

### D. Class (b) — the three permitted queries I ran, and the honest result

Minimal query per row, all of the form `convert_article_ids(ids=["<pmid>"], id_type="pmid")` — *does a PMC deposit exist, i.e. is the D1/D2 mechanism (PMC full-text API) available for this source too?* I chose the three by unblocking value: `huang2023` because its PMCID status is recorded **nowhere** (it is absent from `emc-site-curation.json`'s "other seven" list), and `uMich2023` + `ussc2022` as the two most recent remaining sources (highest prior of an NIH-era deposit), together n=162.

**Not queried, deliberately:** `japan2003` (W10d already did this exact call — reused, not repeated); `meisKindblom1999` (1999, pre-deposit era, lowest yield); `seer270_2022`, `stacchiotti2014sunitinib`, `stacchiotti2019pazopanib` (class (c) — left alone).

**Identifier guard applied: `convert_article_ids` called first; the returned `pmid` was checked against the requested id in every case; all three matched; nothing was discarded and no `get_full_text_article` call was made.**

| source | n | requested | returned (verbatim) | guard | PMCID? |
|---|---|---|---|---|---|
| `huang2023` | 58 | `36948401` | `{"pmid":"36948401","requested-id":"36948401"}` | ✅ match | **absent** |
| `uMich2023` | 44 | `36825763` | `{"pmid":"36825763","requested-id":"36825763"}` | ✅ match | **absent** |
| `ussc2022` | 60 | `35962783` | `{"pmid":"35962783","requested-id":"35962783"}` | ✅ match | **absent** |

**Honest result: all three returned nothing beyond the PMID I supplied.** Per the brief, a zero result is **UNKNOWN, not proof of absence** — it does not establish that these papers have no PMC deposit, only that this route surfaced none today (2026-09-08). What it does establish: **the D1/D2 escape hatch does not extend to them**, so their `unreachable` verdicts are not refuted by the same mechanism. For `uMich2023` and `ussc2022` this **re-confirms** `emc-site-curation.json:29`'s 2026-08-27 measurement 12 days later; for `huang2023` it is a **new** datum filling a gap in that file's enumeration.

### E. Class (d) — not settleable at all

1. **D11 — what bishop2019's `caller_pdf_url` HTTP 200 / 168,147-byte `text/html` body actually was.** The schema stores a bare status code, bytes and content-type, with no field classifying "article" vs "wall". I did not fetch it. **UNKNOWN.** (Note this is *not* the same question as D2: D2 is settled through a different, PMC-text route.)
2. **D10 — which licence `seer270_2022` carries.** Unpaywall says `cc-by-nc-nd`, OpenAlex/DOAJ say `cc-by-sa`, for the same DOI. Settling it needs the publisher or DOAJ record, and CTARC 2022's route is class (c). **UNKNOWN**, and the census's separate note that CC BY-NC-ND blocks committing this one is unaffected either way.

### F. Summary table

| classification | count | rows |
|---|---|---|
| **(a) settleable from committed evidence** | **9** | D1, D2, D3, D4, D5, D6, D7, D12 (labelling), D13 (bookkeeping); D8/D9 resolve as *not actually disagreements* |
| **(b) settleable by a permitted retrieval** | **3** | D9 (`huang2023`), plus `uMich2023`, `ussc2022` under D12 — **all three executed, all three returned nothing** |
| **(c) settleable only by a denied retrieval** | **6** | pazopanib, anthracycline, sunitinib 2014, trabectedin/RT 2018, Wagner 2020, CTARC 2022 — recorded, **not attempted** |
| **(d) not settleable** | **2** | D11, D10 |

## Validation evidence

All **RUN**, all read-only. Nothing `PROPOSED (NOT RUN)`; no test skipped or weakened; no guard changed.

- **Environment:** container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Claude Code 2.1.42, Linux 6.18.44-fc-v24, `python3` (stdlib `json`/`re` only), GNU coreutils/grep/sed. **No `curl`, no `WebFetch`, no `WebSearch`, no publisher request of any kind.** The only egress was three PubMed MCP `convert_article_ids` calls.
- `date -u` start `Tue Sep 8 02:50:27 UTC 2026` / end `Tue Sep 8 02:54:40 UTC 2026`, both exit 0.
- `git rev-parse HEAD` → `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` (start) / `4d950cf036294627b7ae67dfb306cc1875d702ac` (end). `git status --porcelain | wc -l` → **`0`** at both, exit 0. `ls -la /tmp/claude-0/w10f/` → **empty**, exit 0. No git write operation was performed.
- Independent re-derivation of the tallies (`python3`, exit 0):

```
census n 16
adm n 16
py candidates n 17 ['seer270_2022','masunaga2025','meisKindblom1999','drilon2008','ussc2022','chiusole2020','japan2003','uMich2023','bishop2019','china2016','huang2023','stacchiotti2019pazopanib','immunosarc2emc2025','martinbroto2020immunosarc1','stacchiotti2013anthracycline','stacchiotti2014sunitinib','morioka2016trabectedin']
py not in census: ['immunosarc2emc2025']
census not in py: []
census tally {'retrieved': 5, 'unresolved': 2, 'free_to_read_but_not_retrieved': 3, 'closed': 6}
adm by_verdict {'unreachable': 11 ids…, 'refused_no_risk_row': 3 ids…, 'admitted': ['stacchiotti2013anthracycline','morioka2016trabectedin']}
```

- The four `routes: []` sets confirmed verbatim from `emc-km-admissibility-2026-08-27.json` (`meisKindblom1999`, `ussc2022`, `uMich2023`, `china2016`, `stacchiotti2019pazopanib`, `stacchiotti2014sunitinib` — six, each with `"unpaywall": {"is_oa": false, "oa_status": "closed", "n_oa_locations": 0}`), exit 0.
- `grep -n 'oa.fcgi' research/literature/emc-km-figure-retrieval-2026-08-25.json` → seven lookups at lines 36, 63, 90, 117, 144, 172, 200, each followed by `"http": 404` and `"error_code": null, "license": null`, exit 0.
- `grep -n '"full_text_reachable": "PMC2779719"\|"full_text_reachable": "PMC7771031"'` → `emc_ipd_survival.py:276,313` and generated `emc-ipd-survival.json:87,174`, exit 0.
- `grep -n "idIsNotOpenAccess" -r research/` → 4 hits (2 source records + 2 downstream propagations), exit 0.
- Three MCP `convert_article_ids` responses quoted verbatim in §D; all `"status":"ok"`, all `requested-id` == returned `pmid`.
- **Not run:** `scripts/preflight.sh` (dispatch does not authorise it); the census and admissibility generators (running them would write).

## Limitations

- **This is an adjudication of records, not of papers.** No verdict in `emc-km-admissibility-2026-08-27.json` is changed by me, no curve becomes admissible, no case joins any denominator, and `drilon2008`/`bishop2019` remain `figure_checked: false`. All corrections in §A are **routed to the coordinator, not applied.**
- **The A1/A2 settlement rests on the repository's own dated self-correction plus transcribed content, not on my re-fetching anything.** If `emc-site-curation.json:27,80` and `emc-radiotherapy-contradiction.json:11` are themselves wrong about what was read on 2026-08-27, my settlement inherits that error. I judged them credible because they carry article content (a quoted Results sentence, a 4-way percentage split, an 87-vs-86 discrepancy) that an abstract does not contain — but I did not verify by retrieval, and the underlying `literature-cache` files are on a branch the census itself flags as *"a working cache rather than repository state"* and which I did not read.
- **`literature-cache` was not inspected.** Every `read_from` path in §A points into it. Their existence is UNKNOWN to me at this HEAD.
- **Still no per-route timestamp anywhere.** All dating remains round-slug/filename granularity, exactly as W10e recorded. My "2026-08-27" datings inherit that imprecision.
- **The three §D zero results are UNKNOWN, not proof of absence** — of the PMCID, and certainly not of the paper.
- **`emc-site-curation.json`'s "nine remaining candidate series" set is not the census's nine** (it enumerates six PMIDs + a review, and omits `huang2023`, `stacchiotti2014sunitinib`, `stacchiotti2019pazopanib`). I flag this as a possible set-membership inconsistency at **low confidence** and did not chase it; it may simply be a different candidate list (site tables vs KM figures).
- **I did not read the frozen corpus** at `/tmp/claude-0/frozen-corpus/`; a locally-absent prior record of any of this remains UNKNOWN in the sense `CORPUS-CONTEXT.md` warns about.
- **HEAD moved during the run** (`3f5fc95d` → `4d950cf0`); every file I read was last touched at `14a3f172` (2026-09-04) and is unaffected, but a coordinator commit after my reads could in principle alter them.
- **W10d is SECONDARY here** (Kawaguchi's absent PMCID, transferred not re-verified). W10c is reused only as context and I re-ran none of its overlap adjudication.
- **No clinical claim of any kind.** Reachability is a statement about this program's $0 routes on specific dates. None of this bears on any patient, on EMC efficacy, safety, selectivity or clinical readiness.

## Tool-call and wall-clock count actually used

**19 tool calls** — 15 `Bash` (read-only), 1 `ToolSearch`, 3 `mcp__PubMed__convert_article_ids`. No `Read`/`Write`/`Edit`, no git write, no `curl`/`WebFetch`/`WebSearch`. **Wall clock 02:50:27Z → 02:54:40Z = 4 min 13 s.** Well inside the ~40-call / ~40-minute target; returned as soon as the stop condition was met.

## Next concrete action

**One successor, and it is a coordinator-owned write, not research: apply the §A corrections, smallest-first, in this order.** (1) Strike the false clause in `emc-rt-bed-reappraisal.json:41`. (2) Append a `⛔ SUPERSEDED 2026-08-27` key to `emc-ipd-admissibility-2026-08-12.json` beside its existing `⭐_CLOSED_2026-08-25` — **append, never rewrite**, per that file's own `⚠_this_scan_is_not_edited_otherwise`. (3) Reword the `why` string for `drilon2008`/`bishop2019` in `emc-km-admissibility-2026-08-27.json` to scope it to the figure graphics, leaving both verdicts `unreachable`. (4) Correct the two downstream repetitions at `no-wet-lab-publication-archetypes.md:527` and `W16b-…:151`. (5) Add W10e's two proposed schema fields — `attempted: false` and a per-route timestamp — and give `immunosarc2emc2025` a reachability row. All five are writes to `research/literature/`, `research/modalities/` and shared campaign reports, so **they are not mine to make**; W10f is read-only and hands them over as a diagnosis with the smallest correct repair, with the file:line evidence for each above.

**For lane 10's research axis: still no viable successor**, and this strengthens rather than reopens W10d/W10e's conclusion. The one genuinely new access fact — the PMC full-text API reaches two papers the PDF ladder cannot — was **already exploited on 2026-08-27** and is exhausted: my three permitted checks found no further PMC deposit among the remaining candidates. Everything left is either class (c) or a subscription/interlibrary decision that is trimcrae's, exactly as the 2026-08-12 record already says.
