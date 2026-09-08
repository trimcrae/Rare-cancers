> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

# W08h — Source status of the three remaining missing-value borderline records

## Worker

Worker ID **W08h**, lane 8 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT ONLY, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). I cannot observe the served model; no environment variable in this container names a model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:58:33 UTC 2026`
`date -u` at end: `Tue Sep  8 02:59:54 UTC 2026`

Repository read: `/home/user/Rare-cancers`.
- **`git rev-parse HEAD` at start: `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8`**
- **`git rev-parse HEAD` at end: `4ec9da1e4d335911a92157cf7a402e3990fe5cee`**

The checkout **moved during my run** (as it did for W08d `b9a0257e`, W08e `47aac85f`, W08f `d3e9c4d8`, W08g `3f5fc95d`); none of these is the `92abbcb9` frozen commit named in `COMMON-BRIEF.md`. Nothing I read is affected — the four reports I read are identical in content to what W08g and W08f describe — but the campaign's "frozen read commit" statement is factually stale and the coordinator should know it.

`git status --porcelain` printed **nothing (clean tree) at both start and end**. **No writes of any kind to the Git tree; no git write operations.** The only directory I created is `/tmp/claude-0/w08h/`, which is empty (no execution was needed).

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 -Djavax.net.ssl.trustStorePassword=changeit -Djavax.net.ssl.trustStoreType=PKCS12 -Dhttps.proxyHost=127.0.0.1 -Dhttps.proxyPort=37223 -Dhttp.nonProxyHosts=localhost|127.0.0.1|::1|127.*|0.*|::|169.254.*|api.anthropic.com|api-staging.anthropic.com|api-pr-preview.anthropic.com|mcp-proxy.anthropic.com|mcp-proxy-staging.anthropic.com|registry.npmjs.org|jsr.io|npm.jsr.io|pypi.org|files.pythonhosted.org|index.crates.io|proxy.golang.org|host.docker.internal|10.*|172.16.*|172.17.*|172.18.*|172.19.*|172.20.*|172.21.*|172.22.*|172.23.*|172.24.*|172.25.*|172.26.*|172.27.*|172.28.*|172.29.*|172.30.*|172.31.*|192.168.*|100.64.0.0/10|*.svc.cluster.local|*.svc.cluster.local -Djdk.http.auth.tunneling.disabledSchemes= -Djdk.http.auth.proxying.disabledSchemes=
NO_PROXY=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,127.0.0.0/8,0.0.0.0/8,::,169.254.0.0/16,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,registry.npmjs.org,jsr.io,npm.jsr.io,pypi.org,files.pythonhosted.org,index.crates.io,proxy.golang.org,host.docker.internal,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,.svc.cluster.local,*.svc.cluster.local
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

(Identical at start and end; no model-naming variable is present.)

## Question

For the **three** of W08f's five untestable borderline calls that W08g did **not** close: does a PMC deposit exist, and does the record state an elapsed interval that W08c's Rule A (anchor → **first** distant or regional metastasis) or Rule B (anchor → **first** local recurrence) would admit into the EMC published-case-report interval census?

This is open because W08f classified those calls as untestable for the specific reason that a **numeric value is absent from what W08c recorded** — a fact about the record, not about the rule — and W08d's `convert_article_ids` deposit sweep covered only the eight unadjudicated records, never the borderline-call PMIDs. W08g closed two of the five at source; the other three had not been checked.

## Prior-work check

Commands run (repository `/home/user/Rare-cancers`, HEAD `ce743d6a`):

```
rg -n "3731040" --glob '!.git' | head -20
rg -n "22446404" --glob '!.git' | head -20
rg -n "W08h" --glob '!.git' | head -20
git ls-files | rg -i "W08"
grep -n "9158707" W08c-...md W08b-...md W08-...md
```

What they showed:
- `rg "W08h"` returned **nothing** — no prior W08h output exists; this is not a replay.
- `git ls-files | rg -i "W08"` lists exactly seven lane-8 reports (`W08`, `W08b`–`W08g`). W08g is the most recent and stops after its two PMIDs.
- `rg "3731040"` shows the record already appearing in W08, W08b, W08c, W04b and W08f — always as an **excluded / different-estimand** row, never with a recovered elapsed value, and never with its deposit status checked.
- `rg "22446404"` shows only W08c's exclusion line and W08f's untestable line (the one other hit, in `results/nr4a3-metad-r1/ckpt/HILLS`, is a coincidental digit substring of a float, not a PMID).
- I confirmed I am **not** replaying any `CLOSED-WORK.md` item: no publisher route was attempted; retrieval was PubMed MCP only; none of the closed sources (Pazopanib, Sunitinib 24703573, Trabectedin/RT, Wagner 2020, CTARC 2022, anthracycline `PMC3879193`) was touched; the blocked NR4A Perspective was not approached in any form.

I read, in full, `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `W08c-blinded-third-adjudication.md`, `W08d-unavailable-record-recovery.md`, `W08f-full-adjudication-envelope.md` and `W08g-borderline-pmid-recovery.md`. I did not consult `/tmp/claude-0/frozen-corpus/` — every input I needed is in the live checkout, and the corpus is a selected snapshot whose absences are UNKNOWN either way.

## Method / inputs

**Identification of the three (from W08f's own report, not reconstructed).** W08f names its five untestable calls explicitly and identically in two places:

> line 152: "**Not testable: 5 of the 12** (calls 5, 6, 9, 10, 11) — in every one of those five the *value* is missing, not merely the admissibility…"
> line 450: "**5 of the 12 borderline calls were not testable** (calls 5, 6, 9, 10, 11)…"

W08g closed **call 6** (PMID 21547635) and **call 10** (PMID 38111543). The remaining three are therefore **calls 5, 9 and 11**, whose identities W08f's own table gives:

| W08f call | Record as W08f states it |
|---|---|
| 5 | PMID **3731040**, metastases *preceding* the primary by 10 y and 2 y |
| 9 | PMID **22446404** canine EMC, excluded as non-human |
| 11 | **"Non-EMC histologies excluded on sight (9 PMIDs)"** — a *group*, not a single record |

**Call 11 is not one PMID.** W08f carried it forward as a single "call" but it covers nine records, enumerated by W08c line 167: 42294281, 16918143 (synovial sarcoma), 25671361 (clear cell sarcoma), 11504379 (parachordoma), 12743501 (myoepithelioma), 8472444 (parosteal chondrosarcoma), 38961422 (primary pulmonary myxoid sarcoma), 38039617 (SMARCB1/INI1-deficient paratesticular neoplasm), and *the mesenchymal-chondrosarcoma patients within* 9158707. I treated all nine, so the third "call" is fully covered rather than partly.

**Retrieval — PubMed MCP only, under W10c's identifier guard.** `convert_article_ids` was called **first** on every PMID before any content call, and every returned `requested-id` was compared to what I sent. Tools used: `mcp__PubMed__convert_article_ids`, `mcp__PubMed__get_article_metadata`. No `get_full_text_article` call was made, because **no PMC deposit exists for either single-record call**, and for the call-11 group the exclusion is categorical (see Result). No publisher route, no web fetch, no proxy request of any kind.

Attribution: **according to PubMed**, via the PubMed MCP server. DOIs are linked inline below.

## Result

### Identifier guard — outcome

Every `requested-id` in both `convert_article_ids` responses matched the PMID I sent, and every PMID echoed in the two metadata responses matched. **Zero mismatches; nothing discarded.**

### Per-record findings

| # | PMID | PMC deposit? | Value found? | Verbatim admitting/excluding sentence | Anchor | Classification | Grade |
|---|---|---|---|---|---|---|---|
| Call 5 | **3731040** ([DOI](https://doi.org/10.1002/1097-0142(19860901)58:5%3C1144::aid-cncr2820580528%3E3.0.co;2-l)) | **NO** — `convert_article_ids` returned `{"pmid":"3731040","requested-id":"3731040"}` with **no `pmcid` field** | **NO** (no Rule-A/B-admissible value) | **Excluding:** *"The patients presented with metastasis to the lung, 10 years and 2 years, respectively, prior to discovery of the primary neoplasms in the soft tissues of the lower extremities."* | **None usable — the interval runs backwards.** The stated 10 y and 2 y are measured *from lung metastasis forward to* discovery of the primary, so no primary-anchored value exists | **still UNKNOWN** (and a categorical Rule A exclusion: metastasis preceded the primary) | PRIMARY (abstract retrieved this run) |
| Call 9 | **22446404** ([DOI](https://doi.org/10.1292/jvms.11-0555)) | **NO** — `{"pmid":"22446404","requested-id":"22446404"}`, **no `pmcid`** | **NO** — the record contains **no elapsed interval of any kind**; the disease course is described only at necropsy | **Excluding:** *"Extraskeletal myxoid chondrosarcoma was found in a five-month-old male Irish setter dog."* (metastasis described as *"At necropsy… metastatic small masses were observed in multiple organs"* — no timing) | **None stated.** No diagnosis or surgery date, no metastasis date | **still UNKNOWN** (and a categorical exclusion: non-human) | PRIMARY (abstract retrieved this run) |
| Call 11 | **group of 9** (below) | **2 of 9 have deposits, 7 do not** | **NO new value admissible** | see per-record note below | n/a | **still UNKNOWN as a source question; categorically inadmissible as a census question** | PRIMARY (metadata retrieved this run) |

### Call 11 — the nine records individually

| PMID | PMC deposit? | Histology per its own abstract (retrieved this run) |
|---|---|---|
| 42294281 | **YES — PMC13259740** ([DOI](https://doi.org/10.3389/fonc.2026.1846272)) | Synovial sarcoma. **Excluding:** *"Comprehensive genomic profiling identified an SS18-SSX1 fusion gene, and the diagnosis of synovial sarcoma was confirmed…"* — it enters the frame only because it *mimicked* EMC (*"raising suspicion for extraskeletal myxoid chondrosarcoma"*) |
| 16918143 | **NO** | Myxoid monophasic synovial sarcoma |
| 25671361 | **NO** | Small-cell (Ewing-like) clear cell sarcoma, EWSR1-ATF1 |
| 11504379 | **NO** ([DOI](https://doi.org/10.1177/030089160108700318)) | Parachordoma |
| 12743501 | **NO** | Soft-tissue myoepithelioma |
| 8472444 | **NO** | Parosteal (juxtacortical) chondrosarcoma |
| 38961422 | **YES — PMC11223313** ([DOI](https://doi.org/10.1186/s12890-024-03085-8)) | Primary pulmonary myxoid sarcoma, EWSR1-CREB1. **Excluding:** *"The definitive pathological diagnosis established PPMS."* |
| 38039617 | **NO** ([DOI](https://doi.org/10.1016/j.anndiagpath.2023.152242)) | SMARCB1/INI1-deficient paratesticular neoplasm; *"Both cases lacked EWSR1 rearrangements by FISH"* |
| 9158707 | **NO** ([DOI](https://doi.org/10.1016/s0046-8177(97)90081-2)) | Mixed series; only the **mesenchymal**-chondrosarcoma patients are the call-11 exclusion — see below |

**Two records in this group do have PMC deposits, so their full text is retrievable — but retrieving it cannot change the classification.** W08c excluded all nine on **histology**, which is categorical: any interval printed in a synovial-sarcoma or PPMS case report is not an EMC interval, so no Rule A or Rule B admission is possible whatever the full text says. Fetching those two deposits would have produced numbers that must then be discarded, which is exactly the imputation risk the dispatch forbids. I therefore stopped at the deposit determination and record the histology sentence as the excluding sentence. **Note that 42294281's abstract does state a lung metastasis and a local recurrence** — this is precisely the trap: it is an SS18-SSX1 synovial sarcoma, and entering its intervals would corrupt the census.

**One correction worth recording about call 11, in W08c's favour.** PMID 9158707's abstract also contains an *EMC* sentence with an anchored interval: *"The patient with myxoid chondrosarcoma of the posterior mediastinum developed bilateral pulmonary metastases 10 months after surgery and has been lost to follow-up since."* This is **not** a newly recovered value — W08c already admitted it as **row A1 = 10 months, anchor "primary surgery"**, and it is the leading `10` in the baseline Column A. W08c's call-11 wording (*"the mesenchymal-chondrosarcoma patients within 9158707"*) is exact: only the mesenchymal patients were excluded, and the myxoid patient was admitted. I verified this against W08c line 126, W08b lines 186/206 and W08-disease-course line 197. **No double-count and no new event.**

### Census

**No value was recovered from any of the three. The census is therefore unchanged, and I ran no recomputation** — the dispatch conditions recomputation on a recovered value, and there is none. The baseline stands exactly as W08f/W08e left it:

| Column | Set (months) | n | Status |
|---|---|---|---|
| A (anchor → first distant/regional metastasis) | `[10, 16, 24, 26, 34, 48, 60, 74, 108]` | 9 | **BASELINE — unchanged by W08h** |
| B (anchor → first local recurrence) | `[16, 29, 36, 42, 168]` | 5 | **BASELINE — unchanged by W08h** |

Every figure above and in W08c/W08d/W08e/W08f is a **count of published case-report events**. There is **no denominator**: not a rate, risk, incidence, hazard or probability. Nothing here states or implies a surveillance interval, an imaging schedule, a follow-up recommendation, or any clinical advice.

**With W08g, the missing-value question for all five of W08f's untestable calls is now closed at source: 0 of 5 yielded an admissible value.**

## Validation evidence

**RUN.** Environment: Claude Code 2.1.42, remote cloud container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux.

1. `date -u`, `env | grep …`, `git rev-parse HEAD`, `git status --porcelain` — exit 0. Start `ce743d6a`, end `4ec9da1e`, `git status --porcelain` empty at both ends. Quoted above.
2. `mcp__PubMed__convert_article_ids(ids=["3731040","22446404"], id_type="pmid")` — verbatim response:
   `{"status":"ok","response-date":"2026-09-07 22:59:11",…"records":[{"pmid":"3731040","requested-id":"3731040"},{"pmid":"22446404","requested-id":"22446404"}]}`
   **Guard: both `requested-id`s match; no `pmcid` key on either record → no PMC deposit for either.**
3. `mcp__PubMed__convert_article_ids` on the nine call-11 PMIDs — `"status":"ok"`, all nine `requested-id`s match; `pmcid` present only for `42294281` (`PMC13259740`) and `38961422` (`PMC11223313`).
4. `mcp__PubMed__get_article_metadata(pmids=["3731040","22446404"])` — `"count":2`, PMIDs match; abstracts quoted verbatim above.
5. `mcp__PubMed__get_article_metadata` on the nine — `"count":9`, all PMIDs match; histology sentences quoted verbatim above.
6. `grep -n "9158707" …` — exit 0; output quoted above, confirming A1 = 10 months already in the baseline.

**PROPOSED (NOT RUN).** `get_full_text_article(["PMC13259740"])` and `get_full_text_article(["PMC11223313"])` — deliberately not run; see Result for why retrieving them could not produce an admissible value and would only create imputation risk.

No content-policy refusal occurred. No 403, no paywall, no denied route replayed.

## Limitations

- **Absence of a PMC deposit is not absence of the paper.** PMIDs 3731040 (Cancer, 1986) and 22446404 (J Vet Med Sci, 2012) exist as full articles; only their PMC availability is negative. Whether their **full text** states an interval the abstract omits is **UNKNOWN**, not zero — for 3731040 that is largely moot, since the direction of the reported intervals is a categorical Rule A exclusion regardless.
- I read **abstracts**, not full texts, for calls 5 and 9. That is the only route PubMed MCP offers without a deposit. An abstract-level negative is a weaker negative than a full-text negative, and I state it as such.
- For the call-11 group I determined deposit status and histology but did **not** read the two available full texts. That is a deliberate scope choice, not a completed full-text negative; a later worker wanting full-text confirmation of the histology exclusion could run those two fetches.
- **W08f's "call 11" is a group of nine, not a record.** Anyone reading W08f's "5 untestable calls" as "5 records" will miscount: the five calls span **thirteen** PMIDs.
- The whole frame remains a **denominatorless count of published case reports**, subject to publication and reporting selection of unknown magnitude and direction. It supports no rate, no risk, and no clinical recommendation, and I make none.
- The `92abbcb9` commit named as frozen in `COMMON-BRIEF.md` is not what any recent lane-8 worker actually read; my reads are anchored to `ce743d6a` / `4ec9da1e`.

## Stop condition

**Set up front:** stop as soon as, for each of the three remaining untestable calls identified *from W08f's own report*, I have (a) applied the identifier guard, (b) determined PMC deposit status, and (c) determined whether an admissible Rule A / Rule B value exists — recomputing the census only if a value is actually recovered.

**MET.** All three calls resolved (call 11 across all nine of its PMIDs). Deposit status determined for all eleven distinct PMIDs. **Zero admissible values recovered**, so no recomputation was owed and none was performed; the baseline is reported unchanged and was never replaced. No value was imputed for any record, no other W08c call was re-adjudicated, and no W08f envelope was re-run.

## Tool-call and wall-clock count actually used

**11 tool calls** (5 Bash, 1 ToolSearch, 2 `convert_article_ids`, 2 `get_article_metadata`, 1 Bash end-state — of which 2 were issued in parallel batches), against a ~40-call target.
**Wall clock: 1 minute 21 seconds** (`02:58:33Z` → `02:59:54Z`), against a ~40-minute target. Returned immediately on meeting the stop condition; no padding.

## Next concrete action

**No further source-recovery successor exists in this lane.** With W08g and W08h, all five of W08f's untestable calls are closed at source and none yielded a value; W08f had already closed the rule-sensitivity axis to the limit of what W08c recorded. Every remaining lane-8 question needs information that no permitted route supplies.

The one small, finite, genuinely useful successor is **editorial, not scientific**: ask the coordinator to append a **focused correction** (per `CORPUS-CONTEXT.md` §4, not a new review round) to W08f recording (i) that its "call 11" is a **nine-PMID group**, so "5 untestable calls" spans **13 PMIDs**, and (ii) that all five are now closed at source with **0 of 5** yielding a value — citing W08g for 21547635 / 38111543 and this report for 3731040 / 22446404 / the nine. That prevents the next reader from mistaking W08f's envelope bounds as resting on five unexamined records when they now rest on five examined and exhausted ones.

If a successor with a *different* permitted route is ever dispatched, the only two unopened doors I can name are the full texts of `PMC13259740` and `PMC11223313` — and I record honestly that opening them cannot change any census value, only confirm a histology exclusion.
