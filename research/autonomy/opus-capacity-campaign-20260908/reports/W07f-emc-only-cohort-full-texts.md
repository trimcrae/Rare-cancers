<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:10:00Z UTC
     agent id a6853f58916346501 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a6853f58916346501.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report below.

---

## Worker

- **Worker ID:** W07f · **Lane 7 refill** — full-text resolution of W07e's fourth failure mode over the four PMC-available EMC-only cohorts.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I report myself as Claude Opus 5 (`claude-opus-5`) under Claude Code 2.1.42 in a remote cloud environment. I did not observe the served model and do not assert it as fact; the coordinator extracts the actual per-child runtime model from the transcript.
- **`date -u` at start:** `Tue Sep  8 03:02:00 UTC 2026` · **at end:** `Tue Sep  8 03:03:21 UTC 2026`
- **`git rev-parse HEAD` at start:** `fc6ed92999c26f52c47668d1c126321a5f51d1b5` — this is the commit every `file:line` reference below was read at. **At end:** `a87275c14897230041fde97c9965c9646474df7a`. HEAD advanced under me mid-run (coordinator integration of other lanes); neither equals the brief's frozen `92abbcb9…`, nor W07e's `3f5fc95d…`. Recorded, not worked around.
- **`git status --porcelain` at start:** empty (no output). **At end:** empty (no output). **Working tree clean at both ends; I wrote nothing into `/home/user/Rare-cancers`.** `/tmp/claude-0/w07f/` was created and is empty — this run needed no scratch execution.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — literal output at start (environment identical at end; the four `no_proxy`/`NO_PROXY`/`npm_config_noproxy`/`JAVA_TOOL_OPTIONS` lines match only through embedded `anthropic.com` hostnames and are reproduced in full per the "literal" instruction):

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

**Do the four PMC-available EMC-only cohorts W07e classified `NO-AE-DATA` at abstract level — Drilon `PMC2779719`, Chiusole `PMC7308468`, Bishop `PMC7771031`, Morioka `PMC4946242` — report adverse events over their EMC-only denominators anywhere at full text (toxicity section, table, safety paragraph, discontinuation count)? If any does, W07e's fourth failure mode is wrong and lane 7's support set grows beyond `{PMID 31331701}`. If none does, the mode is established at full-text level.**

Open because W07e classified all four from abstracts only and said so explicitly (`W07e:258`: *"**Not run** — outside this dispatch's scope. Consequence: §5.4's fourth failure mode is **abstract-level-provisional**, exactly as W07b's rows were before W07c."*). This is the exact successor W07e named at `:299`.

## Prior-work check

Commands run at HEAD `fc6ed929…`:

1. `rg -n -i "PMC2779719|PMC7771031|PMC7308468|PMC4946242" --glob '!.git'` — 34 hits across the tree. All four PMCIDs are **heavily present as identifiers** (`research/data/emc-clinical-registry.json`, `scripts/emc_km_figure_fetch.py`, `research/manuscripts/emc_systemic_therapy_pooling.py`, `research/modalities/emc_ipd_survival.py`, `research/manuscripts/citation-retraction-sweep.json`). **Zero hits concern adverse-event content.** The repository holds these papers as survival/efficacy/IPD sources; their toxicity structure — the object of this question — is not retained anywhere.
2. Same `rg` over `/tmp/claude-0/frozen-corpus/extracted/corpus` — 17 hits, same character, no AE content. Confirms the gap is not merely a local-checkout absence.
3. Read `CLOSED-WORK.md` in full. **None of the four is a denied route.** The denied list is pazopanib PMID 31331701 full text, sunitinib 2014 (24703573), CTARC 2022 (35144048), Wagner 2020 (32856598), trabectedin/RT 2018 (`10.4172/clinical-practice.1000433`), anthracycline `PMC3879193`/24345066. **I touched none of them, retried nothing, rerouted nothing, and assert nothing about any of them.** In particular the pazopanib trial is quoted below only at the abstract strength W07b already retained.
4. Read `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, and W07b/W07c/W07d/W07e in the relevant sections.

**Not replayed:** W07e's Axis-R enumeration (not re-run — I classify no new papers), W07d's vocabulary widening, W07c's cabozantinib/apatinib rows.

## Method / inputs

- **Retrieval: PubMed MCP only.** No publisher fetch, no HTTP egress, no proxy route, no paid API. $0.
- **Identifier guard, executed first.** `mcp__PubMed__convert_article_ids(ids=["PMC2779719","PMC7308468","PMC7771031","PMC4946242"], id_type="pmcid")` **before any full-text call**, and every returned identifier checked against the request (§Validation V1). Zero mismatches; nothing discarded.
- **Full text:** two `mcp__PubMed__get_full_text_article` calls, batched two articles each.
- **Repository inputs read:** `research/autonomy/opus-capacity-campaign-20260908/{COMMON-BRIEF,CLOSED-WORK,CORPUS-CONTEXT}.md`, `reports/W07b…`, `reports/W07c…`, `reports/W07d…`, `reports/W07e…`, and `research/manuscripts/no-wet-lab-publication-archetypes.md:480–500` (the reachability record named in the dispatch).
- **Decision rule, fixed before reading** (W07b's rubric, unchanged): a row counts as growing the support set only if it reports an adverse event **counted over a denominator composed only of EMC patients**, with a **grade**. A narrative harm mention without a count is `EMC-SPECIFIC, narrative, ungraded`. A count over a denominator containing non-EMC patients is `MIXED-ARM-ONLY`.

According to PubMed, the four articles are: Drilon et al., *Cancer* 2008, PMID 18951519, [DOI](https://doi.org/10.1002/cncr.23978); Chiusole et al., *Front Oncol* 2020, PMID 32612944, [DOI](https://doi.org/10.3389/fonc.2020.00828); Bishop et al., *Am J Clin Oncol* 2019, PMID 31436747, [DOI](https://doi.org/10.1097/COC.0000000000000590); Morioka et al., *BMC Cancer* 2016, PMID 27418251, [DOI](https://doi.org/10.1186/s12885-016-2511-y).

## Result

### 5.1 Headline, stated plainly in both directions

**Three of the four report no adverse events at all over their EMC-only denominators at full text. The fourth does report harm — but its denominator is not EMC-pure, and W07e mis-described it.**

- **The support set does NOT grow.** Not one of the four supplies a graded, counted, EMC-specific adverse-event denominator. Lane 7's graded support set remains **exactly one study, `PMID 31331701`**, unchanged.
- **W07e's fourth failure mode survives for Drilon, Chiusole and Bishop and is now full-text-established for them** — 41 / 59 / 87-patient EMC-pure cohorts, with 33 irradiated, 21 on chemotherapy across 32–39 courses, 20 on first-line and 14 on second-line chemotherapy, and **not one adverse-event count between them**.
- **W07e's fourth failure mode is WRONG about Morioka, and W07e's row for it is factually wrong twice over.** W07e recorded Morioka as an "EMC-only cohort" of 5 with *"no AE sentence."* At full text, (a) the 5 is **2 EMCS + 3 MCS**, a mixed-histology denominator, not EMC-only; and (b) the paper carries **four explicit harm statements plus a referenced adverse-drug-reaction table**. Morioka therefore does not belong in the fourth failure mode at all — it belongs in **W07's original mode 3, denominator destroyed by aggregation**, at n=5. That is a correction to W07e that must be appended, and it slightly *narrows* the fourth mode's scope: ten cohorts becomes nine, one of which (Morioka) was never EMC-pure.

### 5.2 Row by row, with verbatim text

| Paper | EMC-only denominator(s) at full text | Verbatim harm text found | Graded? | Counted over an EMC-only denominator? | Classification | Strength |
|---|---|---|---|---|---|---|
| **Drilon 2008**, PMID 18951519 / `PMC2779719`, [DOI](https://doi.org/10.1002/cncr.23978) | 86 EMC retrieved / 87 in abstract; 73 treated with curative intent; **21 patients, 39 chemotherapy courses administered, 32 evaluable** | The **only** occurrence of the word *toxicity* in the entire full text: *"PFS was examined as the primary endpoint for treatment with data censored for toxicity."* No toxicity section, no safety paragraph, no discontinuation count, no AE table referenced anywhere. Chemotherapy Outcomes reports only response and PFS: *"For all courses of therapy combined, 25% (8 of 32 patients) of patients had a best result of SD lasting ≥6 months…"* | **No** | **No** | **NO-AE-DATA — confirmed at full-text level** | PRIMARY |
| **Bishop 2019**, PMID 31436747 / `PMC7771031`, [DOI](https://doi.org/10.1097/COC.0000000000000590) | **41** consecutive localised EMC; **33 (80%) combined-modality surgery+RT**; 23 preoperative RT at median 50 Gy; 10 postoperative RT at median 60 Gy; 3 chemotherapy | **No toxicity sentence of any kind.** The words *toxicity*, *adverse*, *grade 3*, *CTCAE*, *complication* do not appear. The nearest is a generic discussion aside carrying no denominator and no event: *"Local control should be a primary goal given that multiple interventions have a negative impact on quality of life and can lead to significant morbidity."* | **No** | **No** | **NO-AE-DATA — confirmed at full-text level.** A radiotherapy paper that specifies dose, technique (photon 2D/3D n=22, IMRT n=7, electrons n=3, protons n=1) and 94-month median follow-up, and reports **zero** RT toxicity | PRIMARY |
| **Chiusole 2020**, PMID 32612944 / `PMC7308468`, [DOI](https://doi.org/10.3389/fonc.2020.00828) | **59** EMC; 20 on first-line chemotherapy for metastatic disease; **14 second-line**; 23 radiotherapy; 8 drug holidays | **No toxicity section, no AE table, no grades, no discontinuation count.** Tables 1–4 (whose bodies *are* carried in this extraction) are characteristics, surgical outcome, disease-control rate and univariate Cox — no safety table exists. Critically, the paper makes a **safety claim with no adverse-event data behind it**, twice: *"our study is the first to our knowledge to provide data on drug holiday, with long intervals of chemotherapy-free time for eight patients (mean duration of drug-free interval 22.8 months), suggesting the safety of such practice"* and, in the Conclusion, *"Our data also suggest the safety of including drug holidays in the treatment strategy of metastatic disease."* | **No** | **No** | **NO-AE-DATA — confirmed at full-text level** | PRIMARY |
| **Morioka 2016**, PMID 27418251 / `PMC4946242`, [DOI](https://doi.org/10.1186/s12885-016-2511-y) | **Not EMC-pure.** *"The number of subjects with EMCS and MCS was 2 (2.7 %) and 6 (8.2 %), respectively. Five subjects with EMCS and MCS were allocated to the trabectedin group"* — the treated denominator is **5 = 2 EMCS + 3 MCS** | Four harm statements: (i) *"Cycle interval of 20 days was extended in all of five subjects, and the major reasons for extension were neutropenia and thrombocytopenia."* (ii) *"In one subject (subject No. 1) the dose of trabectedin was reduced to 1.0 mg/m[2] in cycle 3 because of adverse event (creatinine phosphokinase increased)."* (iii) *"No subjects withdrew from the study due to toxicity, and no deaths were assessed as drug-related."* (iv) Table reference, verbatim as extracted: *"Adverse drug reactions in the trabectedin group are shown in Table."* Methods also state the grading rule: *"Dose reduction was allowed in case of grade 3 or 4 adverse events including thrombocytopenia < 25,000/μL, neutropenia < 500/μL with fever and neutropenia < 500/μL persistent for at least 6 days."* | **UNKNOWN** — the ADR table is *referenced* but its **body is not carried by this extraction route**; the narrative events (i)–(iii) carry **no grades**. The Methods grading rule is a protocol rule, not a report of graded events | **No** — the denominators are 5/5 and 1/5 over a **mixed EMCS+MCS** population. Subject No. 2 is identified as EMCS and Subject No. 3 as MCS; **Subject No. 1's histology is UNKNOWN from this route**, so even the single dose-reduction event cannot be attributed to an EMC patient | **MIXED-ARM-ONLY, ungraded at narrative level, table UNRECOVERED** — **not** `NO-AE-DATA`, and **not** EMC-only. **W07e's row is corrected on both counts** | PRIMARY for the narrative; UNKNOWN for the table |

### 5.3 What this buys lane 7 — the sharper claim, with its exact scope

The fourth failure mode is real and now rests on full text rather than abstracts, but its correct statement is narrower and more precise than W07e's:

> **In EMC's own cohort literature, where the denominator is already EMC-pure and nothing needs disaggregating, harm is simply not reported.** Three EMC-only series — 41, 59 and 86/87 patients — that between them irradiated 33 patients to 50–60 Gy, gave 21 patients 39 chemotherapy courses, and put 20 patients on first-line and 14 on second-line chemotherapy, contain **zero adverse-event counts, zero grades, zero discontinuation figures and zero toxicity tables** at full text. Two of the three nonetheless use toxicity as a *methodological device* without ever counting it — Drilon censors PFS "for toxicity" while reporting no toxicity, and Chiusole concludes that drug holidays are *safe* on the strength of a cohort in which no adverse event was recorded.

That last pair is the substantive new content of this run: it is not merely omission, it is **omission alongside use**. A paper that censors on toxicity has toxicity data in hand; a paper that concludes "safety" has made a safety judgement. Neither published a number. This is a different and more specific defect than "the denominator was aggregated away", and it has a different remedy — the data exist in the source institutions.

**This is bookkeeping about what four papers reported. It is not a safety, tolerability or efficacy statement about any treatment, and it supports no clinical inference of any kind.** Nothing here says EMC treatment is well tolerated; absence of reporting is not absence of harm.

### 5.4 Route outcome — the reachability record, as the dispatch required

**All four full texts were retrieved successfully, at $0, through the PubMed MCP `get_full_text_article` route, on 2026-09-08 (server response date `2026-09-07 23:02:26` UTC for the id conversion — the PMC server's clock, quoted as returned).**

This **confirms** the separate campaign finding for `PMC2779719` and `PMC7771031`. The in-repo reachability record at `research/manuscripts/no-wet-lab-publication-archetypes.md:488` states verbatim:

> *"⚠ **Two of seven were never retrieved.** `drilon2008` (PMC2779719) and `bishop2019` (PMC7771031) both returned **HTTP 404** from the Europe PMC full-text endpoint despite having PMCIDs. That is a statement about *that endpoint*, not about those papers, and they need a second route before anything is concluded."*

The record was already correctly scoped — it names the endpoint, not the papers — and `research/manuscripts/endpoint/lit-targets-endpoint-benchmarks.json:5` independently records that the Drilon paper *was* recovered at HTTP 200 from `pmc_html_drilon`. **The ladder in that record has no PMC-text/MCP rung, and this run supplies it: both papers are reachable, in full, through PubMed MCP, at no cost.** This is a **route outcome**, not an article fact. It matches W07c's finding that the MCP path is a distinct route from the recorded HTTP egress block, now confirmed on two further articles.

### 5.5 Two source-internal discrepancies found in passing, reported without adjudication

Both concern Drilon (`PMC2779719`) and both affect numbers lane 7 and the repository currently quote:

1. **87 vs 86 patients.** The abstract says *"87 patients with EMC who were seen at 2 institutions between 1975 and 2008"*; the Methods say *"86 patients of EMC were retrieved from the databases"* and the Results say *"Of the 86 evaluable patients, 57 were men and 29 were women"* (57+29 = 86). W07e's Axis-R row, and the repository, carry **87**. I do not adjudicate which is correct.
2. **39 courses administered vs 32 evaluable.** *"Twenty-one of 86 EMC patients received a combined total of 39 courses of chemotherapy: 2 as neoadjuvant therapy, 3 as adjuvant therapy, 2 for local disease recurrence, and 32 for metastatic disease. Response data were available from 32 of these courses in 21 patients."* The abstract's *"32 evaluable courses"* is therefore the metastatic-setting subset and also, coincidentally, the response-evaluable count. The dispatch's framing ("21 EMC patients received 32 evaluable chemotherapy courses") is accurate to the abstract; the administered total is 39. Neither figure is an adverse-event denominator.

Also noted: Bishop's Discussion cites Drilon as *"no radiologic complete or partial responses in 21 patients receiving chemotherapy; the best responses were stable disease for limited lengths of time with a median time to progression of 5 months"* (Drilon's own figure is 5.2 months), and Chiusole's Discussion misspells it *"Drillon et al."* — both cosmetic, recorded so the coordinator is not surprised by them.

## Validation evidence

**RUN.**

**V1 — identifier guard, executed before any full-text call.** `mcp__PubMed__convert_article_ids(id_type="pmcid")`, verbatim server response:

```
{"status":"ok","response-date":"2026-09-07 23:02:26","request":{"warnings":[],"format":"json","idtype":"pmcid","ids":["PMC2779719","PMC7308468","PMC7771031","PMC4946242"],"tool":"pubmed-mcp-server","versions":"no","showaiid":"no"},"records":[
{"pmcid":"PMC2779719","pmid":"18951519","doi":"10.1002/cncr.23978","requested-id":"PMC2779719"},
{"pmcid":"PMC7308468","pmid":"32612944","doi":"10.3389/fonc.2020.00828","requested-id":"PMC7308468"},
{"pmcid":"PMC7771031","pmid":"31436747","doi":"10.1097/COC.0000000000000590","requested-id":"PMC7771031"},
{"pmcid":"PMC4946242","pmid":"27418251","doi":"10.1186/s12885-016-2511-y","requested-id":"PMC4946242"}]}
```

**Mismatch check, item by item:** each record's `requested-id` is **identical to the PMCID I requested** (4/4). Each returned PMID also matches the PMID W07e attached to that PMCID (18951519 Drilon, 32612944 Chiusole, 31436747 Bishop, 27418251 Morioka) — 4/4. **Zero mismatches; nothing discarded.**

**V2 — full-text calls.** `mcp__PubMed__get_full_text_article(pmc_ids=["PMC2779719","PMC7771031"])` → `"count":2`; `mcp__PubMed__get_full_text_article(pmc_ids=["PMC7308468","PMC4946242"])` → `"count":2`. **4/4 retrieved, zero errors, zero refusals, zero paywalls.** Each returned article's `identifiers.pmcid`, `.pmid` and `.doi` were re-checked against V1 inside the response body and match 4/4 — the mismatch guard applied at both stages.

**V3 — repository reads,** all read-only, at HEAD `fc6ed929…`: the four campaign docs, the four prior lane-7 reports, and `no-wet-lab-publication-archetypes.md:480–500`. `git status --porcelain` empty at start and end (§Worker).

**PROPOSED (NOT RUN).**

- **The Morioka adverse-drug-reaction table body.** The MCP JATS extraction carries Chiusole's Tables 1–4 as inline text but renders Morioka's table references as bare *"shown in Table."* — the same structural limitation W07c hit for the apatinib tables. I did **not** open a second route (Europe PMC, PMC HTML, publisher) to recover it. Consequence: Morioka's AE grades are **UNKNOWN**, and Subject No. 1's histology is **UNKNOWN**. Had I run it, the identifier guard would have applied unchanged.
- **Bishop's and Drilon's tables.** Same limitation, same non-attempt. Both papers' table *references* were stripped to bare text (e.g. Bishop's *"Patient and tumor characteristics are listed in."*), so I cannot exclude a toxicity table by title. See Limitation 1 — this is the one real soft edge in this report.
- **Any denied route.** Not attempted; nothing asserted about any of them.

**Refusals encountered: none.** No branch was refused, no denied route replayed, nothing rephrased or rerouted.

## Limitations

1. **The single real soft edge: this extraction route carries table *bodies* inconsistently.** Chiusole's four tables came through in full, so its negative is strong. Drilon's, Bishop's and Morioka's table references came through stripped of both caption and body. For Drilon and Bishop I can state that **no toxicity table is referenced anywhere in the narrative** — a paper with a safety table normally points at it in Results — but I cannot read a table title I was not given. **Their negatives are therefore full-text-narrative-established, not table-established.** This is exactly the error class the repository's own `no-wet-lab-publication-archetypes.md` names (*"an absent reading is not a reading of absence"*), and I am flagging it rather than papering over it. Morioka's ADR table is explicitly referenced and explicitly unrecovered.
2. **Morioka's grades are UNKNOWN, not zero.** The paper plainly has an ADR table. Nothing here says its events were ungraded — only that this route did not return them. It would still not enter lane 7's graded support set, because its denominator is 5 mixed EMCS+MCS.
3. **Four papers, not a literature.** This resolves the four PMC-available members of W07e's ten. The remaining cohorts (117, 60, 58, 44, 42, 40) were **not** checked at full text and their abstract-level `NO-AE-DATA` status is unchanged and unconfirmed. The fourth failure mode is full-text-established for **three** cohorts and abstract-level-provisional for the rest.
4. **No rate, no pooling, no transfer.** I computed nothing. No count was pooled across papers, no denominator combined, no percentage converted into a denominator (none was even attempted — Chiusole's percentages, e.g. "40.8%", were read alongside their stated n and never inverted).
5. **Nothing clinical.** This is availability bookkeeping about what four papers printed. It estimates no toxicity burden, supports no treatment choice, and says nothing about whether any EMC treatment is safe, tolerable or effective.
6. **HEAD moved under me** (`fc6ed929…` → `a87275c1…`) and neither equals the brief's frozen `92abbcb9…`. All my `file:line` references are pinned to `fc6ed929…`.
7. **`PMID 31331701` is quoted at abstract strength only**, as CLOSED-WORK requires. I did not retrieve it and add nothing to what W07b retained.

## Stop condition

**Set at the outset:** return as soon as (a) all four PMCIDs are confirmed by `convert_article_ids` with every returned identifier checked against the request, (b) each of the four full texts is read and classified for an adverse-event report over its EMC-only denominator, with the verbatim sentence or table caption quoted either way, (c) the outcome is stated plainly in both directions — support set grows, or fourth failure mode established — and (d) the retrieval route outcome for `PMC2779719` and `PMC7771031` is reported against the in-repo reachability record; or ~40 calls / ~40 minutes, whichever first.

**Status: MET, on all four, far inside budget.** (a) V1, 4/4, zero mismatches. (b) §5.2, 4/4 read and classified, verbatim text quoted for every row including the three negatives. (c) §5.1 — **support set does not grow; it remains `{PMID 31331701}`, count 1**; fourth failure mode **established at full text for Drilon, Bishop and Chiusole** and **corrected for Morioka**, which was never EMC-pure. (d) §5.4 — both papers retrieved at $0; the record's endpoint-scoped 404 stands and its ladder gains a working rung.

## Tool-call and wall-clock count actually used

**Tool calls: 13** — 9 Bash (all read-only repository/environment reads; no scratch execution needed), 1 ToolSearch, 1 PubMed `convert_article_ids` (all four PMCIDs in one call), 2 PubMed `get_full_text_article` (two articles each). **Wall clock: ~1.4 minutes** (03:02:00 → 03:03:21 UTC). Well inside the ~40-call / ~40-minute self-observed target; returned on stop-condition satisfaction, no padding. Batching four identifier conversions into one call and four full texts into two calls is again what made this cheap.

## Next concrete action

**Append a focused correction to `W07e-denominator-claim-second-axis.md` §5.4 and its Axis-R row for PMID 27418251 — not a new review round — recording that Morioka is a 2 EMCS + 3 MCS mixed cohort, not an EMC-only cohort of 5, and that it *does* report adverse drug reactions (cycle-interval extension in 5/5 for neutropenia and thrombocytopenia; one dose reduction for raised creatine phosphokinase; no toxicity withdrawals; a referenced but unrecovered ADR table), so it reclassifies from `NO-AE-DATA` to `MIXED-ARM-ONLY` and the fourth failure mode covers nine cohorts, not ten.** This is a coordinator write of two sentences into an existing report, it changes no headline (the support set is unchanged at 1), and it must happen before any of W07e's §5.4 text is quoted onward — because as written it asserts of Morioka something the source contradicts.

Second, subordinate: **the natural scientific successor — full-text checks of the six remaining Group-I cohorts (117, 60, 58, 44, 42, 40) — should be gated on PMC availability first**, and whoever runs it should expect the table-body limitation in §Limitations 1 and plan a second route for any paper whose narrative *references* a safety table. I did not enumerate those six's PMCIDs, so whether they are PMC-available is **UNKNOWN** and should be established with one `convert_article_ids` call before the lane commits to another run.
