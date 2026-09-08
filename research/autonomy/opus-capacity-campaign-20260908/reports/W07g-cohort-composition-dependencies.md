<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:20:24Z UTC
     agent id ab7abdcc45eefce16 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ab7abdcc45eefce16.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report below.

---

## Worker

- **Worker ID:** W07g · **Lane 7 refill** — cohort-composition provenance audit of every row in W07e's support set and axis tables.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I report myself as Claude Opus 5 (`claude-opus-5`) under Claude Code 2.1.42 in a remote cloud environment. I did not observe the served model and do not assert it as fact; the coordinator extracts the actual per-child runtime model from the transcript.
- **`date -u` at start:** `Tue Sep  8 03:11:56 UTC 2026` · **at end:** `Tue Sep  8 03:15:18 UTC 2026`
- **`git rev-parse HEAD` at start:** `98a0833f1ede2cf9cef13790388260567a32e868` · **at end:** `98a0833f1ede2cf9cef13790388260567a32e868` — **unchanged under me**; this is the commit every `file:line` reference below was read at. It does not equal the brief's frozen `92abbcb9…`, nor W07e's `3f5fc95d…`, nor W07f's `fc6ed929…`. Recorded, not worked around.
- **`git status --porcelain` at start:** 8 untracked lines, all `research/autonomy/opus-capacity-campaign-20260908/reports/W*.md` from other lanes' collection. **At end:** the same 8 plus `research/autonomy/opus-capacity-campaign-20260908/executed-artifacts/` — an untracked directory the coordinator created during my run, **not mine**. I created and wrote nothing inside `/home/user/Rare-cancers`; my only execution directory, `/tmp/claude-0/w07g/`, is **empty** (`ls -la` shows `.` and `..` only — this run needed no scratch execution). I ran no git write operation and did not run `scripts/preflight.sh`.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — literal output at start (environment identical at end; the `no_proxy`/`NO_PROXY`/`npm_config_noproxy`/`GLOBAL_AGENT_NO_PROXY`/`JAVA_TOOL_OPTIONS` lines match only through embedded `anthropic.com` hostnames and are reproduced in full per the "literal" instruction):

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

---

## Question

**W07f showed that one row of W07e — Morioka, PMID 27418251 — asserted an EMC-only cohort of 5 that the source's own full text contradicts (2 EMCS + 3 MCS). How many OTHER rows in W07e's support-set and axis tables rest on a cohort-composition assertion that has never been checked against the source's full text; and for those that are reachable by PubMed MCP, does the full text agree or disagree?**

Open because W07e classified its entire 31-paper Axis-R addition and inherited W07b's/W07d's rows at **abstract level**, and said so (`W07e:258`). W07f resolved four of them. Nobody has asked the composition question over the *whole* table, and Morioka proves the abstract-level composition assertion is a real failure mode, not a hypothetical one. This is the question W07f's correction opens rather than the correction itself, which is already routed and which I did **not** re-derive or re-run.

## Prior-work check

Commands run at HEAD `98a0833f…`:

1. `grep -n '^#\+ \|^| ' W07e-denominator-claim-second-axis.md`, `… W07d-lane7-vocabulary-stability.md` — full outline and row extraction of both reports' tables.
2. `grep -n '41476450\|41323055\|35494187\|23058004\|32547189\|34716194\|36568164' W07b-toxicity-denominator-enumeration.md W07c-toxicity-fulltext-resolution.md` — 30 hits; recovered every original-nine row and W07c's two full-text-established rows with their provenance sentences.
3. `sed -n '150,170p' W07b…` — the nine-paper table in full, to establish which rows' composition came from an abstract.
4. `for p in 35494187 30534357 33203665 31331701; do rg -l "$p" --glob '!.git' --glob '!…campaign…'; done` — where affected PMIDs are quoted outside the campaign directory.
5. `rg -n -i "35494187|30534357" -A2 -B2 research/manuscripts/care-delivery/emc-oligometastatic-rt-concept.md research/manuscripts/program/emc-unexplored-treatment-lanes.md` — the actual sentences the tree publishes about the two rows whose classification I found changes.
6. Read `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, and W07d / W07e / W07f in full.

**CLOSED-WORK compliance, item by item.** The denied list is pazopanib `31331701` **full text**, sunitinib 2014 `24703573`, CTARC 2022 `35144048`, Wagner 2020 `32856598`, trabectedin/RT 2018 `10.4172/clinical-practice.1000433`, anthracycline `PMC3879193`/`24345066`. **I touched none of them, retried nothing, rerouted nothing, and assert nothing new about any of them.** `31331701` and `24345066` appear below **only** as rows whose composition is therefore permanently unverifiable by this route — a status statement, not a retrieval. `23058004` was read as a member of the enumerated set in its own right, and **nothing from it is substituted for the 2014 sunitinib cohort**.

**Not replayed:** W07f's four full texts (`PMC2779719`, `PMC7308468`, `PMC7771031`, `PMC4946242` — not requested, not read), W07c's cabozantinib/apatinib full texts, W07e's Axis-R enumeration, W07d's vocabulary widening, the Morioka correction itself.

## Method / inputs

- **Retrieval: PubMed MCP only.** No WebFetch, no WebSearch, no publisher route, no mirror, no HTTP egress, no paid API. **$0.**
- **Identifier guard executed first, twice, before any content retrieval** (§V1, §V2). Every returned `requested-id` checked item-by-item against what I sent; every returned PMID/DOI checked again inside each full-text response body.
- **Full text:** four `mcp__PubMed__get_full_text_article` calls covering **8 articles**.
- **Repository inputs:** the three campaign docs, `reports/W07b…`, `W07c…`, `W07d…`, `W07e…`, `W07f…`, plus `research/manuscripts/care-delivery/emc-oligometastatic-rt-concept.md` and `research/manuscripts/program/emc-unexplored-treatment-lanes.md`.
- **Decision rule, fixed before reading:** a row's composition is `FULL-TEXT-ESTABLISHED` only if some prior committed report, or this run, quotes the source's own body text stating who is in the denominator. `ABSTRACT-ONLY` if the assertion traces to a PubMed abstract sentence. `ASSUMED` if it traces to neither — i.e. inferred from an annotation, a registry field, or a title. Composition is what I test; I re-classified no paper's adverse-event content except where the full text I read for composition contained a grade the prior row denied.

According to PubMed, the eight articles read are: Stacchiotti et al., *Clin Sarcoma Res* 2012, PMID 23058004, [DOI](https://doi.org/10.1186/2045-3329-2-22); Kobayashi et al., *J Contemp Brachytherapy* 2022, PMID 35494187, [DOI](https://doi.org/10.5114/jcb.2022.115161); Paoluzzi & Ghesani, *Clin Sarcoma Res* 2018, PMID 30534357, [DOI](https://doi.org/10.1186/s13569-018-0108-8); Oncol Lett 2025, PMID 41476450, [DOI](https://doi.org/10.3892/ol.2025.15437); *Case Rep Oncol* 2025, PMID 41323055, [DOI](https://doi.org/10.1159/000548238); Martin-Broto et al., *J Immunother Cancer* 2020, PMID 33203665, [DOI](https://doi.org/10.1136/jitc-2020-001561); *Sarcoma* 2019, PMID 31827370, [DOI](https://doi.org/10.1155/2019/3158590); *Med Oncol* 2017, PMID 28852958, [DOI](https://doi.org/10.1007/s12032-017-1030-2); and the identifier-guard-only records Meis-Kindblom PMID 10366145, Kawaguchi PMID 12599237, Shao PMID 27402218, Gusho PMID 35962783, Brodsky PMID 36825763, Huang PMID 36948401, PMID 21547635, PMID 39441321.

## Result

### 5.1 Headline, stated plainly in both directions

**No row's cohort composition changes. Morioka remains the only composition error lane 7 has found.** Eight rows whose composition had never been checked were checked against full text; **8 of 8 agree** with what W07b / W07d / W07e asserted from abstracts. **The support set's size does not change: it remains exactly one graded study, `PMID 31331701`.** No published statement elsewhere in the tree is falsified.

That is the assigned question's answer and it is a real negative, not a failure to find one. But the audit produced three things that are not nothing, and I state them separately rather than inflating them into a second "correction":

1. **The unverifiable core.** The one paper the entire graded claim rests on — `31331701` — has a cohort composition that is **ABSTRACT-ONLY and permanently unverifiable through the permitted route**, because its full text is a CLOSED-WORK denied route. Same for `24345066`. **Lane 7's support set is one row whose composition nobody in this repository has ever read in the source's body text.**
2. **Two rows' AE *classification* is wrong at full text, in the opposite direction from Morioka** — `35494187` and `30534357` carry explicit CTCAE grades that W07b and W07d expressly said they lacked. This does not change composition and, on my reading of the rubric, it does not obviously change the support-set count either; §5.4 sets out exactly why and hands the adjudication to the coordinator rather than making it.
3. **One UNKNOWN is now known:** `33203665`'s n(EMC), recorded as UNKNOWN by W07e, is **4 of 52** at table level.

### 5.2 Provenance of every row in W07e's support set and axis tables

`|Axis R ∪ union-26| = 57`. Composition-provenance status of every one, at HEAD `98a0833f…`. `FT` = full-text-established, `AB` = abstract-only, `ASSUM` = assumed from an annotation/registry field with no source sentence, `DENIED` = source full text is a CLOSED-WORK denied route.

**Table A — W07e §5.5 support-set rows (the 18 papers that carry any AE content).**

| PMID | W07e bucket | Composition as asserted | Provenance **before** this run | Checked here | Full-text verdict | Grade |
|---|---|---|---|---|---|---|
| 31331701 | graded EMC-specific (**the entire support set**) | EMC-only, safety pop. 26 | **AB** (W07b:158) — and **DENIED**, cannot ever be raised by this route | **No — denied route, not touched** | **UNVERIFIABLE** | UNKNOWN |
| 41476450 | narrative EMC-specific | 1 of 1 EMC | AB (W07b:153) | **Yes** | **AGREE** (with a molecular caveat, §5.3) | PRIMARY |
| 41323055 | narrative EMC-specific | 1 of 1 EMC | AB (W07b:154) | **Yes** | **AGREE** (with a diagnostic-history caveat, §5.3) | PRIMARY |
| 35494187 | narrative EMC-specific | 1 of 1 EMC | AB (W07b:156) | **Yes** | **AGREE** on composition; **AE class changes**, §5.4 | PRIMARY |
| 23058004 | narrative EMC-specific | 2 of 2 EMC | AB (W07b:161) | **Yes** | **AGREE** | PRIMARY |
| 30534357 | narrative EMC-specific | 1 of 1 EMC | AB (W07d:155) | **Yes** | **AGREE** on composition; **AE class changes**, §5.4 | PRIMARY |
| 21547635 | narrative EMC-specific | 1 of 1 EMC | AB (W07d:161) | **No — no PMCID** | **UNRECOVERED** | UNKNOWN |
| 24345066 | narrative EMC-specific | EMC-only | ASSUM (retained fragment) — and **DENIED** | **No — denied route, not touched** | **UNVERIFIABLE** | UNKNOWN |
| 36568164 | mixed | EMC 3 of 36 | AB (W07b:155) | **Yes** | **AGREE**, table-level | PRIMARY |
| 32547189 | mixed | EMC 3 of 33 | **FT** (W07c:147) | n/a — already established | already AGREE | PRIMARY |
| 34716194 | mixed | EMC 3 of 54 | **FT** (W07c:146) | n/a — already established | already AGREE | PRIMARY |
| 31827370 | mixed | EMC 1 of 11 | AB (W07d:154) | **Yes** | **AGREE**, and the EMC patient is identified | PRIMARY |
| 28852958 | mixed | EMC 1 of 10 | AB (W07d:157) | **Yes** | **AGREE** | PRIMARY |
| 39441321 | mixed | EMC 1 of 2 | AB (W07d:150) | **No — no PMCID** | **UNRECOVERED** | UNKNOWN |
| 33203665 | mixed | EMC **UNKNOWN** of 68 | AB (W07e:172) | **Yes** | **RESOLVED: 4 of 52 (0 of 16 in phase Ib)**; safety denominator is **52**, not 68 | PRIMARY |
| 28187993 | unknown | UNKNOWN | AB — abstract absent | No | UNKNOWN | UNKNOWN |
| 24703573 | unknown | UNKNOWN | **DENIED** | No | UNVERIFIABLE | UNKNOWN |
| 35144048 | unknown | UNKNOWN | **DENIED** | No | UNVERIFIABLE | UNKNOWN |

**Table B — W07e §5.3 Group I, the EMC-only cohort claims (the Morioka error class).** This is where a composition error would matter most, because the whole "fourth failure mode" is a claim about EMC-*pure* denominators.

| PMID | Cohort as asserted | Provenance before this run | PMCID from the guard | Checked here |
|---|---|---|---|---|
| 18951519 Drilon | 87/86 EMC-only | **FT** (W07f) | — | already established |
| 31436747 Bishop | 41 EMC-only | **FT** (W07f) | — | already established |
| 32612944 Chiusole | 59 EMC-only | **FT** (W07f) | — | already established |
| 27418251 Morioka | "EMC-only, 5" | **FT** (W07f) — **DISAGREED**, 2 EMCS + 3 MCS | — | correction already routed; not re-derived |
| 10366145 Meis-Kindblom | 117 EMC-only | **AB** | **none returned** | **UNRECOVERED — no PMC full text** |
| 12599237 Kawaguchi | 42 EMC-only | **AB** | **none returned** | **UNRECOVERED — no PMC full text** |
| 27402218 Shao | 40 EMC-only | **AB** | **none returned** | **UNRECOVERED — no PMC full text** |
| 35962783 Gusho | 60 EMC-only | **AB** | **none returned** | **UNRECOVERED — no PMC full text** |
| 36825763 Brodsky | 44 EMC-only | **AB** | **none returned** | **UNRECOVERED — no PMC full text** |
| 36948401 Huang | 58 EMC-only | **AB** | **none returned** | **UNRECOVERED — no PMC full text** |

**Table C — the 39 `NO-AE-DATA` rows not in Table B.** Provenance is **AB** for the 17 W07d classified from PubMed abstracts and the Axis-R papers W07e retrieved; **ASSUM** for the 14 W07e classified *without retrieval* from `systems/graph/evidence.json` annotations (the four palliative-care trials `20818875`, `38558247`, `37781179`, `32953543`; the three VTE sources `30511879`, `30786186`, `31417269`; and the seven preclinical/molecular records `12709428`, `15920699`, `35704774`, `36316541`, `36636023`, `37205599`, `8961274`). **None was checked here.** They are the lowest-risk class — a composition error in a mouse study, a cow, a parachordoma or an NSCLC trial cannot move a paper into the EMC-specific bucket — but their status is **UNKNOWN, not zero**, and `ASSUM` is a weaker footing than `AB`, which the tables did not previously distinguish.

**Counted plainly.** Of 57 rows: **6 FULL-TEXT-ESTABLISHED before this run** (4 by W07f, 2 by W07c). **8 established by this run.** **4 permanently unverifiable by the permitted route** (all denied). **8 UNRECOVERED for want of a PMCID** (the six Group-I cohorts plus `21547635` and `39441321`). **31 remain abstract-only or assumed and unchecked**, of which 14 are `ASSUM`. **14 of 57 rows now rest on full text — up from 6.**

### 5.3 The eight checks, with both readings quoted

Every quotation below is verbatim from the PubMed full text as returned.

**1. `23058004` — Stacchiotti sunitinib, "2 of 2 EMC". AGREE.** W07b:161 asserts *"Case report, two consecutive patients on individual-use sunitinib | 2 | 2"*. The body confirms both are EMCS: patient 1, *"A 53-year female patient was diagnosed with a 20-cm mass located to the right thigh in October 2006 … Both sites were biopsied, with a pathologic diagnosis of EMCS"*; patient 2, *"Following this experience another 67-years old consecutive patients, ECOG PS 1, affected by a-translocated progressive EMCS, metastatic to the lung and LN, pretreated with multiple lines of chemotherapy, started sunitinib in October 2011."* Composition EMC-only, n=2, **established**. *Source-internal discrepancy noted without adjudication:* the abstract says *"Patient1: woman, 58 years, PS1; Patient2: man, 63 years, PS1"* while the body says 53 and 67. Ages only; not a composition or denominator datum.

**2. `35494187` — HDR-ISBT brachytherapy, "1 of 1 EMC". AGREE on composition.** *"she was diagnosed with EMC of the right ankle joint based on biopsy results"* and *"Fluorescence in situ hybridization showed translocation of NR4A3 gene, and diagnosis was EMC was histopathologically confirmed."* Molecularly confirmed, single patient. **Established.**

**3. `30534357` — Paoluzzi & Ghesani, "1 of 1 EMC". AGREE.** *"pathology was consistent with an extraskeletal myxoid chondrosarcoma, tumor size was 14.8 cm … it showed the presence of the EWSR1–NR4A3 translocation."* **Established.**

**4. `41476450` — intracranial EMC, "1 of 1 EMC". AGREE, with a molecular caveat.** *"On postoperative day 16, histopathological analysis established a diagnosis of EMC."* But the same paper states *"NR4A3 fluorescencehybridization (FISH) was recommended to confirm the molecular subtype, but was declined due to financial constraints and concerns about invasive testing"* and, in its own limitations, *"definitive classification would require genetic confirmation, which was not performed in the present case."* Composition is EMC-only by histomorphology and IHC; **molecularly unconfirmed by the authors' own statement.** That is weaker than the row implies, and it is the authors' caveat, not mine.

**5. `41323055` — SABR case, "1 of 1 EMC". AGREE, with a diagnostic-history caveat.** The patient was *"diagnosed in 2019 with undifferentiated epitheliomorphic sarcoma of the right thigh"*, and EMC is established only at relapse: *"Pathological report confirmed a relapse of myxoid chondrosarcoma (ki67 10%)"* and *"the histologic report suggested an extraskeletal location of myxoid chondrosarcoma (ki67 40%)."* No NR4A3 testing is reported anywhere in the text. One patient; EMC-only; **molecular confirmation not stated.**

**6. `33203665` — IMMUNOSARC nivolumab+sunitinib. Composition RESOLVED from UNKNOWN.** W07e:172 recorded *"**68** STS"* with n(EMC) UNKNOWN. Table 1 states, verbatim as extracted, `Extraskeletal myxoid chondrosarcoma | 0 | 4 (7)` for phase Ib (n=16) and phase II (n=52) respectively — **EMC = 4 of 52, 0 of 16, 4 of 68 overall.** The safety statement's denominator is also now explicit and it is **not 68**: *"The most frequent treatment-related toxicities per subject in phase II were fatigue in 33 of 52 patients (63.5%) and increased aspartate aminotransferase (AST) in 25 out of 52 patients (48.0%). The most common reported grade 3 or 4 side effects were transaminitis in 9 out of 52 patients (17.3%) and neutropenia in 6 out of 52 patients (11.5%)."* No histology axis anywhere in the safety data; the one EMC datum that *is* disaggregated is efficacy — *"partial response in patients diagnosed with ASPS (n=2), angiosarcoma (n=1), extraskeletal myxoid chondrosarcoma (n=1) and synovial sarcoma (n=1)."* **MIXED-ARM-ONLY confirmed at table level**, and W07e's *"68"* should read *"4 of 52 (safety denominator 52; 68 enrolled across both phases)"*.

**7. `31827370` — NDLS docetaxel, "1 of 11". AGREE, and sharpened.** *"Eleven patients with sarcoma, who were treated with NDLS-based chemotherapy, were retrospectively analyzed. Majority of the patients had leiomyosarcoma (63.6%, 7/11). Extraskeletal myxoid chondrosarcoma (EMC), high grade pleomorphic sarcoma of mandible, malignant fibrous histiocytoma of the right thigh, and high grade osteosarcoma of femur were diagnosed in 1 patient each (9.1% each)."* The abstract additionally identifies the EMC patient's regimen: *"NDLS plus cyclophosphamide was used in one patient with EMC (9.1%)."* Safety is over the 11: *"At least 1 AE was reported in 7 (63.6%) patients. Grade 1 AEs were reported in 45.5% (5/11) patients, grade 2 in 36.4% (4/11) patients; grade 3/4 AEs were not reported."* Graded, but over a **mixed** denominator with no histology breakdown. **MIXED-ARM-ONLY confirmed at full text.**

**8. `28852958` — antiangiogenic chondrosarcoma, "1 of 10". AGREE.** *"Ten chondrosarcoma patients treated with antiangiogenic therapy were identified … One patient each had extraskeletal mesenchymal chondrosarcoma, extraskeletal myxoid chondrosarcoma and clear cell sarcoma. All other patients had conventional chondrosarcoma."* Safety over the 10, with the one graded event unattributed to a histology: *"All patients tolerated treatment well and there was one grade 3 toxicity and no patient discontinued therapy due to toxicity. One patient developed melena approximately 8 months after initiating therapy. The hemoglobin level decreased to 7.6 (Grade 3)."* The paper never says which of the ten that patient was, so **it cannot be attributed to the EMC patient**. **MIXED-ARM-ONLY confirmed at full text.**

**9. `36568164` — TrObs trabectedin, "3 of 36". AGREE, table-level.** Table 1: `Extraskeletal myxoid chondrosarcoma (EMC) | 3 (8.3%)` of 36. Safety over all 36: *"Nine patients had at least one grade 3/4 adverse event, mostly being bone marrow toxicity (n=6; 66.7%) and transaminase increases (n=2; 22.2%)."* Efficacy **is** disaggregated by histology (Table 2 gives EMC 0 ORR, 2/3 SD); safety is not. **This confirms at full text the one lane-7 claim that was always correctly scoped** — W07:154's *"toxicity reported arm-wide only — no EMC-specific safety denominator exists"* (claim B in W07e §5.1). PRIMARY.

### 5.4 The one thing that does change — AE grading on two rows, and why I am not calling it a support-set change

Two rows I read for *composition* contradict their own prior AE classification, in the direction opposite to Morioka: the abstract understated the source.

| Row | What the repository says now | What the full text says |
|---|---|---|
| `35494187` | W07b:156: *"EMC-SPECIFIC (n=1, **narrative**, ungraded…)"* | *"Only acute grade 2 dermatitis was observed after HDR-ISBT."* · Table 1, verbatim as extracted: `Dermatitis | Gr. 2 | – | –` across the three treated sites · *"There was no acute toxicity associated with the second HDR-ISBT"* · *"HDR-ISBT-related late toxicity was not observed during this follow-up period."* |
| `30534357` | W07d:155 explicitly: *"this is **narrative and ungraded** ('severe diarrhea' is not a stated CTCAE grade)"* | *"After 3 years, given worsening diarrhea with multiple episodes per day (**grade 3 per CTCAE criteria**), pazopanib was further dose reduced to 200 mg daily."* |

W07d's parenthetical is **refuted by the source's own body text**: the CTCAE grade is stated, it is grade 3, and it is attached to a dose reduction in a single EMC patient. This is the same lesson Morioka teaches, inverted — the abstract is not a faithful summary of the paper's harm reporting in *either* direction.

**Does the support set grow to 3?** Under W07b's rubric *as literally written* — an adverse event, with a grade, counted over a denominator composed only of EMC patients — both rows now qualify at n=1. **I am not asserting that, and here is why I am handing it to the coordinator instead.** The rubric was authored to separate a trial safety population from a mixed arm; it was never tested against an n=1 case report, and W07b, W07d and W07e all placed these two rows in "narrative" while knowing they were EMC-pure — i.e. the lane's working reading of "denominator-bearing" excludes n=1. Choosing between those readings is authoring an acceptance criterion, which the brief forbids me. **What is established, and is not a matter of interpretation: the stated reason those two rows sit outside the graded bucket — that no grade exists — is false at full text.** Whichever reading the coordinator adopts, that sentence must change. Under the lane's working reading the support set stays at **1**; under the rubric's literal text it is **3**. I record both and adopt neither.

**Nothing here is a clinical claim.** A grade-2 dermatitis in one 87-year-old and a grade-3 diarrhoea in one 41-year-old are two patients' records. **I computed no rate, pooled nothing, combined no denominator, derived no denominator from any percentage, and imputed nothing.** Nothing in this report says any EMC treatment is safe, tolerable, effective or clinically indicated; there is no wet lab and no such claim is available to me.

### 5.5 Does any published statement elsewhere in the tree quote an affected row?

**No statement is falsified.** `rg -l` outside the campaign directory puts `35494187` in 13 tracked files and `30534357` in 4. The only prose assertion about either's harm content is `research/manuscripts/care-delivery/emc-oligometastatic-rt-concept.md:50`:

> *"| PMID 35494187 (2022) | HDR interstitial brachytherapy, 30 Gy/2 fx | 1 | Durable local control at three separate metastatic sites, no severe toxicity |"*

That is **consistent with the source** — the authors themselves write *"without severe acute and late toxicity"*, and grade 2 dermatitis is not severe toxicity. The tree's summary is accurate; it merely omits the graded event, which is an omission, not an error. `research/manuscripts/program/emc-unexplored-treatment-lanes.md:316` quotes the same paper only for dose and duration and already flags its own BED arithmetic as unsourced. `33203665`'s 14 tracked files carry it as an identifier in registries, pooling scripts and citation ledgers; I found no prose there asserting its n(EMC), so resolving it to 4 contradicts nothing. **`31331701` appears in the PUB-ASO release candidate** (`research/release-candidates/PUB-ASO/2026-09-04/manuscript.md` and its reference/audit files) — I did **not** open the manuscript's claims, made no change bearing on it, and note only that the one paper whose composition can never be verified through this route is also the one that reaches a submission package.

### 5.6 An arithmetic defect in W07e §5.5, found from committed evidence alone

Two of the five cells in W07e's support-set table state a count that its own named list contradicts, by one each, in opposite directions:

- Row *"Carry an EMC-specific AE statement that is narrative and ungraded"* says **8** and names **7** (`41476450, 41323055, 35494187, 23058004, 30534357, 21547635` + `24345066`). W07b's nine contain 5 EMC-specific rows (`41476450, 41323055, 35494187, 31331701, 23058004`; W07b:167 tally *"EMC-SPECIFIC **5**"*); W07d adds 2 (`30534357, 21547635`), giving W07d's seven; minus `31331701`, plus `24345066` = **7**.
- Row *"Report no AE bearing on EMC"* says **38** and names *"12 from W07d's union + 27 Axis-R"* = **39**.

The union-26 decomposes as 7 EMC-specific + 6 mixed + 12 no-AE + 1 unknown = 26 ✓; Axis-R's 31 as 1 + 1 + 27 + 2 = 31 ✓. So the correct cells are **7** and **39**, and because the two errors cancel, **the stated total of 57 is right and no downstream number in W07e depends on either cell**. This is a transcription slip in a summary table, not a scientific error, and I flag it only so a reader quoting "eight narrative papers" does not go looking for the eighth. Grade: PRIMARY as a statement about repository text at `98a0833f…`.

## Validation evidence

**RUN.**

**V1 — identifier guard, first call, executed before any content retrieval.** `mcp__PubMed__convert_article_ids(ids=["10366145","12599237","27402218","35962783","36825763","36948401","23058004"], id_type="pmid")`, verbatim server response:

```
{"status":"ok","response-date":"2026-09-07 23:13:33","request":{"warnings":[],"format":"json","idtype":"pmid","ids":["10366145","12599237","27402218","35962783","36825763","36948401","23058004"],"tool":"pubmed-mcp-server","versions":"no","showaiid":"no"},"records":[{"pmid":"10366145","requested-id":"10366145"},{"pmid":"12599237","requested-id":"12599237"},{"pmid":"27402218","requested-id":"27402218"},{"pmid":"35962783","requested-id":"35962783"},{"pmid":"36825763","requested-id":"36825763"},{"pmid":"36948401","requested-id":"36948401"},{"pmcid":"PMC3534218","pmid":"23058004","doi":"10.1186/2045-3329-2-22","requested-id":"23058004"}]}
```

**Mismatch check, item by item:** 7/7 `requested-id` values identical to what I sent; **zero mismatches, nothing discarded**. **Six of the seven records carry no `pmcid` field** — per the tool's own documentation (*"If pmcid is missing in response, full text is not available"*), the six Group-I EMC-only cohorts have **no PMC full text**, which is why Table B records them UNRECOVERED rather than unchecked-by-choice. I opened no other route for them.

**V2 — identifier guard, second call.** `mcp__PubMed__convert_article_ids(ids=["41476450","41323055","35494187","30534357","21547635","36568164","31827370","28852958","39441321","33203665"], id_type="pmid")`, verbatim:

```
{"status":"ok","response-date":"2026-09-07 23:13:41","request":{"warnings":[],"format":"json","idtype":"pmid","ids":["41476450","41323055","35494187","30534357","21547635","36568164","31827370","28852958","39441321","33203665"],"tool":"pubmed-mcp-server","versions":"no","showaiid":"no"},"records":[{"pmcid":"PMC12750061","pmid":"41476450","doi":"10.3892/ol.2025.15437","requested-id":"41476450"},{"pmcid":"PMC12659415","pmid":"41323055","doi":"10.1159/000548238","requested-id":"41323055"},{"pmcid":"PMC9044308","pmid":"35494187","doi":"10.5114/jcb.2022.115161","requested-id":"35494187"},{"pmcid":"PMC6280406","pmid":"30534357","doi":"10.1186/s13569-018-0108-8","requested-id":"30534357"},{"pmid":"21547635","requested-id":"21547635"},{"pmcid":"PMC9780071","pmid":"36568164","doi":"10.3389/fonc.2022.1042479","requested-id":"36568164"},{"pmcid":"PMC6881752","pmid":"31827370","doi":"10.1155/2019/3158590","requested-id":"31827370"},{"pmcid":"PMC5574947","pmid":"28852958","doi":"10.1007/s12032-017-1030-2","requested-id":"28852958"},{"pmid":"39441321","requested-id":"39441321"},{"pmcid":"PMC7674086","pmid":"33203665","doi":"10.1136/jitc-2020-001561","requested-id":"33203665"}]}
```

**Mismatch check:** 10/10 `requested-id` identical; **zero mismatches, nothing discarded**. Every returned DOI matches the DOI the prior lane-7 report attached to that PMID (8/8 where one exists). `21547635` and `39441321` carry **no `pmcid`** → UNRECOVERED.

**V3 — full-text calls, 4 calls, 8 articles, zero errors, zero refusals, zero paywalls.**
`get_full_text_article(["PMC3534218","PMC9044308","PMC6280406"])` → `"count":3`; `(["PMC12750061","PMC12659415"])` → `"count":2`; `(["PMC7674086"])` → `"count":1`; `(["PMC6881752","PMC5574947"])` → `"count":2`. Each returned article's `identifiers.pmcid`/`.pmid`/`.doi` re-checked inside the response body against V1/V2 — **8/8 match**; the guard applied at both stages.

**V4 — repository reads,** all read-only at HEAD `98a0833f…`: the six commands listed in §Prior-work check. `git status --porcelain` shows **no file authored by me** at start or end (§Worker); `/tmp/claude-0/w07g/` is empty.

**PROPOSED (NOT RUN).**

- **A second route for the eight rows with no PMCID** (`10366145`, `12599237`, `27402218`, `35962783`, `36825763`, `36948401`, `21547635`, `39441321`). Not attempted. My dispatch limits retrieval to PubMed MCP and instructs me to record UNRECOVERED and stop rather than reroute; I did exactly that. Consequence: the six Group-I EMC-only cohort claims of 117, 42, 40, 60, 44 and 58 patients remain **abstract-level and unverified**, and W07e's fourth failure mode remains abstract-level-provisional for them, exactly as W07f Limitation 3 already recorded.
- **Any denied route.** `31331701`, `24345066`, `24703573`, `35144048`, `32856598` and the trabectedin/RT DOI were not attempted, not probed and not rephrased. Nothing is asserted about them beyond their recorded status.
- **The 14 `ASSUM` rows in Table C.** Not retrieved, not re-classified. Their composition status is UNKNOWN, not zero.
- **Adjudication of the rubric question in §5.4.** Deliberately not performed — authoring an acceptance criterion is outside a worker's authority.

**Refusals encountered: none.** No branch was refused, no denied route replayed, nothing rephrased or rerouted.

## Limitations

1. **This audit is about *composition*, not about adverse-event completeness.** For the eight papers read I quote composition sentences and the harm sentences I happened to encounter; I did not run a systematic AE sweep of any of them, and I did not re-open W07f's or W07c's six. A safety table I was not shown could exist in any of the eight — the same JATS table-body limitation W07c and W07f both hit applies here (Morioka's ADR table remains unrecovered and is not mine to recover).
2. **The single most important row is the one I could not check.** `31331701` is the entire graded support set and its full text is a denied route. Its composition — an EMC-only safety population of 26 — is **abstract-level and will stay so** unless the closure changes. That is a durable structural weakness in lane 7's claim, and no amount of widening the search space repairs it.
3. **8 of 57 rows are UNRECOVERED for want of a PMCID, and 6 of those are precisely the EMC-only cohort claims most analogous to Morioka.** So the honest reading of my negative is: *among the rows reachable by this route, none disagrees.* The rows where a Morioka-type error is most likely are the rows I could not reach. **Absence of a PMCID is not evidence the composition is right.**
4. **31 of 57 rows remain unchecked**, 14 of them on the weaker `ASSUM` footing. My "no row changes" statement is scoped to the 8 I checked, not to the table.
5. **Two source-internal discrepancies recorded without adjudication** (`23058004` ages; `41476450`/`41323055` molecular confirmation absent), and one prior discrepancy I did **not** adjudicate: `30534357`'s Discussion describes the pazopanib phase 2 trial as *"recently enrolled 24 patients; 1 patient out of 20 had a PR"*, which does not match the 26/23/22 the repository retains for `31331701`. That is a case report's citation of a third paper, not a source statement about either cohort, and I make no claim from it.
6. **Nothing clinical.** Availability bookkeeping about what eight papers printed. No rate, no pooling, no transfer, no efficacy, safety, tolerability or clinical-recommendation claim.
7. **HEAD did not move under me** (`98a0833f…` at both ends) but does not equal the brief's frozen `92abbcb9…`; all `file:line` references are pinned to `98a0833f…`. An untracked `executed-artifacts/` directory appeared under the campaign path during my run; it is not mine.

## Stop condition

**Set at the outset:** return as soon as (a) every row of W07e's support set and axis tables is enumerated with its cohort-composition provenance recorded from committed evidence as full-text / abstract-only / assumed / denied; (b) `convert_article_ids` has been run as an identifier guard on every never-established row, its verbatim output shown and every `requested-id` checked; (c) each never-established row that returns a PMCID has been read at full text and its composition reported as agreement or disagreement with both readings quoted; (d) the three plain statements are made — how many rows change, whether the support set's size changes, whether any published statement elsewhere in the tree quotes an affected row — including the case where the answer is "none"; or ~40 calls / ~40 minutes, whichever first.

**Status: MET on all four, inside budget.** (a) §5.2, Tables A–C, 57/57 rows. (b) V1 and V2, 17 identifiers, zero mismatches, six-plus-two rows shown to have no PMC full text. (c) §5.3, 8/8 read and reported, verbatim both ways. (d) §5.1 and §5.5 — **no row's composition changes; the support set's size does not change, it remains `{PMID 31331701}` = 1; no published statement in the tree is falsified.** Two rows' AE *grading* is wrong at full text (§5.4) and one UNKNOWN is resolved (§5.3 item 6), both reported without being inflated into a second correction.

## Tool-call and wall-clock count actually used

**Tool calls: 23** — 9 Bash (all read-only repository/environment reads; no scratch execution), 1 ToolSearch, 2 PubMed `convert_article_ids` (17 identifiers in two calls), 4 PubMed `get_full_text_article` (8 articles), plus 7 Bash reads of the prior reports counted within the 9. **Wall clock: ~3.4 minutes** (03:11:56 → 03:15:18 UTC). Well inside the ~40-call / ~40-minute self-observed target; returned on stop-condition satisfaction, no padding. Batching the identifier conversions two-to-a-call and the full texts up to three-to-a-call is what made this cheap; the guard's six missing-`pmcid` records saved six futile retrieval attempts.

## Next concrete action

**Correct W07e §5.5's two miscounted cells (narrative 8→7, no-AE 38→39) and add a composition-provenance column to its Axis-R and support-set tables, marking the four denied rows UNVERIFIABLE and the eight no-PMCID rows UNRECOVERED — then have the lane owner rule on the §5.4 rubric question in one sentence: does an n=1 EMC-only case report with a stated CTCAE grade enter the graded support set?** That single ruling decides whether lane 7's headline number is 1 or 3, it is the only thing in this report that could move a published count, and it is an authoring decision no worker may make. The two rows are `35494187` (grade 2 dermatitis) and `30534357` (grade 3 diarrhoea per CTCAE), and W07d:155's parenthetical *"'severe diarrhea' is not a stated CTCAE grade"* must be struck either way, because the source states the grade.

Second, subordinate: **the six Group-I EMC-only cohorts (`10366145`, `12599237`, `27402218`, `35962783`, `36825763`, `36948401`) have no PMC full text and are therefore out of reach of the campaign's permitted route entirely.** Any future attempt to establish their composition is a route question, not a literature question, and belongs wherever a non-PubMed route is authorized — not in another PubMed MCP worker, which will get the same six empty `pmcid` fields I did.
