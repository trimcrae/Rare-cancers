> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report below.

---

## Worker

- **Worker ID:** W07e · **Lane 7 refill** — second independent widening axis for lane 7's load-bearing adverse-event-denominator claim.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I report myself as Claude Opus 5 (`claude-opus-5`) under Claude Code 2.1.42 in a remote cloud environment. I did not observe the served model and do not assert it as fact; the coordinator extracts the actual per-child runtime model from the transcript.
- **`date -u` at start:** `Tue Sep  8 02:50:58 UTC 2026` · **at end:** `Tue Sep  8 02:54:14 UTC 2026`
- **`git rev-parse HEAD` at start:** `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` — **this is the commit every `file:line` reference below was read at.** **At end:** `4d950cf036294627b7ae67dfb306cc1875d702ac`. HEAD advanced under me mid-run (coordinator integration of other lanes); neither equals the brief's frozen `92abbcb9…`, nor W07d's `7d08121…`. Recorded, not worked around. My reads are all pinned to `3f5fc95d…`.
- **`git status --porcelain` at start:** empty (no output). **At end:** `0` matching lines. **Working tree clean at both ends; I wrote nothing into `/home/user/Rare-cancers`.** All execution under `/tmp/claude-0/w07e/` (7 scratch files, listed in Validation evidence).

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — literal output at start (identical environment at end; the four `no_proxy`/`NO_PROXY`/`npm_config_noproxy`/`JAVA_TOOL_OPTIONS` lines that match only through embedded `anthropic.com` hostnames are reproduced in full below rather than filtered, per the "literal" instruction):

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

**Does lane 7's load-bearing adverse-event-denominator claim survive a second widening axis that is independent of vocabulary — and what is the claim's true support set?**

Open because W07d established the nine-paper set is unstable under term widening (union 26, not 9) but found zero new graded EMC-specific denominators. A single null on a single axis is weak: the term-widening axis and the original axis share a mechanism (both select on words in a PubMed abstract), so a paper missed for a *non-lexical* reason — never indexed under any of the fourteen terms tried, or indexed but describing its adverse events only in a table — would be invisible to both. A second axis whose membership rule does not read abstract text at all tests exactly that. Separately, no worker has yet stated where in the repository the claim actually lives, or which papers actually supply its support.

---

## Prior-work check

Read in full before anything else, at `3f5fc95d…`: `COMMON-BRIEF.md` (84 lines), `CLOSED-WORK.md` (70), `CORPUS-CONTEXT.md` (63), and `reports/W07-patient-reported-outcomes-denominators.md` (290), `W07b-toxicity-denominator-enumeration.md` (266, §Question–§Validation), `W07c-toxicity-fulltext-resolution.md` (304, §Question–§Validation), `W07d-lane7-vocabulary-stability.md` (340, §Question–§Limitations).

Commands run (read-only, from `/home/user/Rare-cancers`):

1. `grep -rn "EMC-specific denominator\|EMC-specific safety\|EMC-only denominator\|denominator-bearing EMC" --include='*.md' --include='*.json' . | grep -v '^./.git'` — 17 hits, all inside `research/autonomy/opus-capacity-campaign-20260908/reports/`. **The claim exists in the tree only as campaign-report prose.** Exact `file:line` in §Result 5.1.
2. `grep -rln "toxicit\|adverse event\|grade 3" systems/views/ systems/graph/ research/manuscripts/ research/literature/ research/data/ | grep -v opus-capacity` — 30+ files; led to finding (2) in §5.1.
3. `grep -n -i "toxicit\|adverse\|grade 3\|26 patient\|hypertension\|denominator" research/manuscripts/care-delivery/emc-adaptive-scheduling-pazopanib.md` and `sed -n '95,150p'` on the same file.
4. Axis-R construction: `grep -oiE 'pmid[^0-9]{0,6}[0-9]{7,8}'` over `research/data/emc-clinical-registry.json` and `systems/graph/evidence.json`; set arithmetic against W07d's union of 26 via `comm`.

**Reuse declaration, per dispatch:** I did **not** re-run W07d's vocabulary widening. I took its union of 26 PMIDs as a given input, transcribed from W07d §5.1/V2/V3 (`reports/W07d-lane7-vocabulary-stability.md:165` and V2/V3), and used it only as the set to subtract. I re-executed neither Query W nor Q5.

**CLOSED-WORK compliance, item by item.** No denied route was opened, retried or rerouted. **Pazopanib `31331701`** — no retrieval attempted; used strictly at W07b's already-retained abstract strength; no exposure window, no erratum, no full-method-omission claim, EudraCT untouched. **Sunitinib 2014 `24703573`** — appears in axis R; **deliberately not retrieved**, classified UNKNOWN from committed evidence alone; nothing substituted for it, and `23058004` was not re-read. **Anthracycline `24345066`/`PMC3879193`** — in axis R; **not retrieved**; carried at retained strength only (median 4 cycles, range 1–8, one patient stopping after cycle 1; separate non-missing denominator unknown), no rate. **CTARC 2022 `35144048`** — in axis R; **not retrieved**, no publisher route touched, classified UNKNOWN. **Wagner 2020, Trabectedin/RT 2018, Brenca, Hofvander, PUB-EMC-CLASSIFICATION, the NR4A Perspective** — not approached. No content-policy refusal was encountered anywhere in this run. **No case added to any pooled denominator; nothing pooled; no rate computed by me; no denominator derived from any percentage.**

---

## Method / inputs

**Repository inputs** (all read at `3f5fc95d…`): the four lane-7 reports above; `research/data/emc-clinical-registry.json`; `systems/graph/evidence.json`; `research/manuscripts/care-delivery/emc-adaptive-scheduling-pazopanib.md`; `research/manuscripts/care-delivery/emc-absence-claims-refuted.json`.

**The widening axis, declared before enumeration.**

> **Axis R — the repository's own curated EMC clinical-evidence source list.**
> **Inclusion rule:** every PMID that appears, attached to a `pmid` key or the literal token `PMID`, anywhere in the two files the repository designates as its canonical clinical-evidence stores — `research/data/emc-clinical-registry.json` (governed by `systems/POLICY-evidence.md`) and `systems/graph/evidence.json` (`CLAUDE.md` §7: "`systems/graph/*.json` owns model state"). **Additions = Axis R minus W07d's union of 26.**

**Why this is independent of W07d's axis.** Membership in Q5 and in Query W is decided by whether specific English strings occur in a PubMed abstract. Membership in Axis R is decided by whether a *prior human/agent curator of this repository* cited the paper for some EMC endpoint — survival, local control, recurrence, fusion partner, RT, VTE prophylaxis, care delivery, drug class. That rule never inspects abstract wording, never queries PubMed, and was fixed years and many cycles before lane 7 existed. A paper enters Axis R with **no** adverse-event vocabulary anywhere in it, and — the decisive property — a paper can enter Axis R while being invisible to *both* term lists. The two axes share only PubMed's existence as an index, not its text-matching mechanism. Axis R is also **not** the citation graph: I deliberately did not use `find_related_articles`, because PubMed "related articles" is itself computed from term overlap and would have been a disguised third vocabulary axis rather than an independent one.

**Retrieval:** PubMed MCP only, 2026-09-08 ~02:53 UTC. `mcp__PubMed__convert_article_ids` ×1 (14 PMIDs, **run first**, per the identifier guard), then `mcp__PubMed__get_article_metadata` ×2 (7 + 7). **Identifier guard executed:** every one of the 14 returned records carries `requested-id` equal to its returned `pmid`, and each metadata record's `identifiers.pmid` equals a PMID I requested; the returned sets equal the requested sets exactly. **Zero mismatches, nothing discarded.** No full-text call, no PMC call, no web fetch, no non-PubMed route. According to PubMed, all abstracts, titles and quoted sentences below come from those calls; DOI links are given for every article named.

**Classification rubric — W07b's, reproduced unchanged** so rows stay comparable: `EMC-SPECIFIC` (AE statement whose denominator contains only EMC patients, any n) / `MIXED-ARM-ONLY` / `NO-AE-DATA` (including: study contains no EMC patients) / `UNRECOVERED`; sub-flag **graded/counted** vs **narrative**.

---

## Result

### 5.1 The load-bearing claim, as the repository actually asserts it — and it asserts it in four incompatible scopes

`grep` finds the claim **only** inside campaign reports; no `systems/views/`, `systems/graph/` or manuscript file states it. At `3f5fc95d…` the tree simultaneously contains all four of these:

| # | `file:line` | Scope asserted | Status | Row grade |
|---|---|---|---|---|
| A | `research/autonomy/opus-capacity-campaign-20260908/reports/W07-patient-reported-outcomes-denominators.md:173` | *"EMC treatment toxicity has **never** been reported with an EMC-specific denominator."* — **unrestricted universal** | **FALSE as written**, refuted by W07b; **still standing uncorrected in the tree**, listed under W07's own "Supportable, with the denominator attached" heading | PRIMARY (repository text) |
| A′ | same file `:290` | The same universal, repeated in the report's one-line `result:` summary | Same falsity, same uncorrected status | PRIMARY |
| B | `…/W07-patient-reported-outcomes-denominators.md:154` | *"toxicity reported arm-wide only — no EMC-specific safety denominator exists"* — scoped to **Palmerini/trabectedin PMID 36568164 only** | True, and untouched by everything since | PRIMARY |
| C | `…/W07b-toxicity-denominator-enumeration.md:145` (also `:191`) | *"Graded, denominator-bearing EMC-specific safety data exist in exactly one study — the pazopanib EMC phase 2 trial — and nowhere else **in this set**"* — set = **the nine** | True over the nine | PRIMARY |
| D | `…/W07d-lane7-vocabulary-stability.md:176` | Same sentence, **in this set** = the **union of 26** | True over the 26 | PRIMARY |

**Finding (1) — the divergence is real and it is a defect, not a nuance.** A, C and D are not three phrasings of one claim; A is a universal negative that C and D's own counterexample refutes. `CLAUDE.md` §1 requires "Correct current prose directly" and "Do not embed retired instructions beside current ones." W07:173 and W07:290 are retired prose sitting beside current prose, three successor reports later. W09b independently caught the same thing (`reports/W09b-absence-claim-audit.md:206`) and correctly recorded it as W07b's to route — it has not been routed. **Anything quoting lane 7 by reading W07 alone quotes a false sentence.** The repair is a two-line strike-through in W07, not new research; it is a coordinator/owner action, and I performed no write.

**Finding (2) — the counterexample was already inside the repository before W07 asserted the universal.** `research/manuscripts/care-delivery/emc-adaptive-scheduling-pazopanib.md:143-144` states, in tracked manuscript prose:

> *"There is a real toxicity burden to halve: grade 3 hypertension **9/26 (35 %)**, ALT rise **6/26 (23 %)**, AST rise **5/26 (19 %)** in the EMC trial (`[API]`), over a median PFS measured in years."*

with the cohort defined at `:103` as *"NCT02066285, PMID 31331701 `[API]`: 26 patients entered, 23 met modified-ITT eligibility, 22 evaluable."* That is a graded, counted, EMC-specific adverse-event denominator, committed, attributed, and present in the tree **before** W07 wrote "never". `SECONDARY` for the trial's contents (I did not retrieve `31331701`); `PRIMARY` as a statement about repository state. **The universal negative was refutable from committed evidence without any retrieval at all** — which is the more useful lesson than the refutation itself: W07's prior-work check searched the registry for `quality of life` and `toxic` but not for the claim's own negation.

### 5.2 Axis R enumerated

`|Axis R| = 34`. `|Axis R ∩ union-26| = 3` (`31331701`, `32547189`, `36568164` — the pazopanib trial, apatinib and trabectedin, i.e. exactly the three papers both axes already agreed on). **`|Axis R \ union-26| = 31` additions.** Combined lane-7 coverage is now **57 distinct papers** (26 ∪ 34).

Note the axis behaves as an independence check should: it recovers `27418251` (Morioka trabectedin EMC/MCS sub-analysis) and `24345066` (anthracycline) — both of which lane 7 had been *using* since W07 as rows 11 and 13 — even though **neither is in the union of 26**. Two papers the lane was already quoting were outside the set the lane claimed to quantify over. That alone justifies the axis.

### 5.3 The 31 additions, classified

All classifications abstract-level, rubric unchanged. Article metadata, titles and quoted sentences are **according to PubMed**. `n(EMC)` as stated by the source; unstated is UNKNOWN, never zero.

**Group I — EMC-only cohorts and series (10 papers, all retrieved).** Every one has a clean, EMC-pure, often large denominator. **None reports any adverse event at abstract level.**

| PMID | Yr | Cohort | AE content | Class | Grade |
|---|---|---|---|---|---|
| 10366145 | 1999 | Meis-Kindblom, **117** EMC, follow-up in 99 (median 9 yr) | No AE statement; morphology, recurrence, metastasis, survival only | NO-AE-DATA | PRIMARY |
| 12599237 | 2003 | Kawaguchi, **42** EMC Japan, 8 hospitals | No AE statement; "treatments, outcomes, prognostic factors" — no toxicity term | NO-AE-DATA | PRIMARY |
| 18951519 | 2008 | Drilon, **87** EMC, 2 centres; **21 patients received 32 evaluable chemotherapy courses** | Response, time-to-progression, PFS estimates only. **No toxicity, no discontinuation, no AE** — despite an EMC-pure chemotherapy denominator of 21 | NO-AE-DATA | PRIMARY |
| 27402218 | 2016 | Shao, **40** EMC China | Clinicopathologic/radiologic/FISH; no AE | NO-AE-DATA | PRIMARY |
| 27418251 | 2016 | Morioka, trabectedin phase 2 sub-analysis, **5** EMCS+MCS subjects | PFS, PFR, response, OS only; **no AE sentence** — confirms W07 row 13 ("no toxicity attributable to the EMC pair") from the source | NO-AE-DATA | PRIMARY |
| 31436747 | 2019 | Bishop, **41** consecutive localised EMC, 33 combined-modality RT+surgery | Local control, DMFS, DSS, OS; **no toxicity of any grade**, in a radiotherapy paper | NO-AE-DATA | PRIMARY |
| 32612944 | 2020 | Chiusole, **59** EMC, 2 institutions; 20 treated with chemo for metastatic disease, 14 second-line, **8 given a drug holiday** | Response and disease-control rates only. A drug holiday is not an AE statement. No toxicity | NO-AE-DATA | PRIMARY |
| 35962783 | 2022 | Gusho, **60** EMC, US Sarcoma Collaborative | OS/RFS, prognostic factors; no AE | NO-AE-DATA | PRIMARY |
| 36825763 | 2023 | Brodsky, **44** EMC, Michigan | OS/DFS/MFS/PFS; no AE | NO-AE-DATA | PRIMARY |
| 36948401 | 2023 | Huang, **58** EMC confirmed by FISH | Fusion partners, IHC, survival; no AE | NO-AE-DATA | PRIMARY |

DOIs: [10.1097/00000478-199906000-00002](https://doi.org/10.1097/00000478-199906000-00002), [10.1002/cncr.11162](https://doi.org/10.1002/cncr.11162), [10.1002/cncr.23978](https://doi.org/10.1002/cncr.23978), [10.1016/j.anndiagpath.2016.04.004](https://doi.org/10.1016/j.anndiagpath.2016.04.004), [10.1186/s12885-016-2511-y](https://doi.org/10.1186/s12885-016-2511-y), [10.1097/COC.0000000000000590](https://doi.org/10.1097/COC.0000000000000590), [10.3389/fonc.2020.00828](https://doi.org/10.3389/fonc.2020.00828), [10.1002/jso.27062](https://doi.org/10.1002/jso.27062), [10.1097/COC.0000000000000988](https://doi.org/10.1097/COC.0000000000000988), [10.1016/j.modpat.2023.100161](https://doi.org/10.1016/j.modpat.2023.100161).

**Group II — mixed-arm trials, EMC count not stated in the abstract (3, retrieved).**

| PMID | Study | AE sentence (verbatim) | Class | Grade |
|---|---|---|---|---|
| 15739208 | Maki 2005, bortezomib phase 2, recurrent/metastatic sarcoma, arm B 21 evaluable — [DOI](https://doi.org/10.1002/cncr.20968) | *"Painful neuropathy, myalgias, and asthenia were the most significant observed toxicities."* Over the whole enrolment; EMC not named | NO-AE-DATA for EMC (n(EMC) UNKNOWN, not zero) | UNKNOWN |
| 33203665 | Martin-Broto 2020, nivolumab+sunitinib phase Ib/II, **68** STS — [DOI](https://doi.org/10.1136/jitc-2020-001561) | *"The most common grade 3-4 adverse events included transaminitis (17.3%) and neutropenia (11.5%)."* Percentages only, whole cohort; no histology axis | MIXED-ARM-ONLY (counted-as-percentages; **no count and no EMC denominator recoverable — and none may be derived from these percentages**) | PRIMARY |
| 40941020 | Boklan 2025, carfilzomib+cyclophosphamide/etoposide phase 1, **38** paediatric — [DOI](https://doi.org/10.3390/cancers17172924) | DLTs enumerated per stratum (*"thrombocytopenia, pericarditis, and posterior reversible encephalopathy syndrome"*); EMC not named in the abstract | NO-AE-DATA for EMC (n(EMC) UNKNOWN) | UNKNOWN |

**Group III — non-treatment / non-EMC-patient records (1 retrieved, 14 from committed evidence).**
- Retrieved: `42660639` Li & Gong 2026, ALK IHC across 119 FET-rearranged tumours incl. *"extraskeletal myxoid chondrosarcoma exhibited a high overexpression rate (50%, 2/4)"* — [DOI](https://doi.org/10.1136/jcp-2026-210760). Immunohistochemistry on archival tissue; no treatment, no AE. **NO-AE-DATA**, PRIMARY.
- Non-EMC by committed evidence, **not retrieved**: the four class-level palliative-care trials `20818875` (Temel, NSCLC), `38558247` (PACO), `37781179` (Chen), `32953543` (Kochovska) — all NSCLC, per `systems/graph/evidence.json` and W07's own prior-work section; and the three VTE-prophylaxis sources `30511879` (Carrier), `30786186` (Khorana), `31417269` (Song), cited for `RT-VTE-PROPHYLAXIS`. **NO-AE-DATA for EMC** (zero EMC patients). SECONDARY.
- Preclinical / molecular, **not retrieved**, classified from `evidence.json`'s own annotations: `12709428` (Wansa, NOR-1 AF-1 mapping), `15920699` (Subramanian, expression profiling), `35704774` (Zaienne, druggability), `36316541` (Bangerter), `36636023` (Higuchi), `37205599` (FET-ATR preprint), `8961274` (Zetterström). **NO-AE-DATA** (no patients). SECONDARY.

**Group IV — CLOSED-WORK members of Axis R, classified from retained evidence only, no retrieval (3).**

| PMID | Retained status | Class | Grade |
|---|---|---|---|
| 24345066 anthracycline | EMC-only cohort; one patient stopped after cycle 1 for toxicity; separate non-missing denominator **unknown**; median 4 cycles (range 1–8). No rate | **EMC-SPECIFIC, narrative, ungraded** — already lane-7 row 11, **not new** | UNKNOWN (denominator) |
| 24703573 sunitinib 2014 | Unrecovered, metadata only, three institutional 403 routes exhausted | **UNKNOWN** | UNKNOWN |
| 35144048 CTARC 2022 | Abstract retained, methods unrecovered, publisher 403 | **UNKNOWN** | UNKNOWN |

**Tally over the 31 Axis-R additions:** `EMC-SPECIFIC` **1** (graded/counted **0**, narrative **1**, and that one already in lane 7 since W07) · `MIXED-ARM-ONLY` **1** · `NO-AE-DATA` **27** · `UNKNOWN/unrecovered` **2**.

### 5.4 Count of new qualifying denominators: **ZERO**

**Plainly: the second, independent widening axis produced zero new graded, EMC-specific adverse-event denominators.** Not one of the 31 additions supplies one. This is a second null on an axis that shares no selection mechanism with the first, and it is the outcome the dispatch expected. The claim survives.

**What the second axis adds beyond "survives" — a new failure mode.** W07 §5.3 named three modes, of which mode 3 was "denominator destroyed by aggregation": EMC toxicity vanishing inside mixed-sarcoma arms. Axis R shows that mode is **not** the main one. Ten EMC-only cohorts — 117, 87, 60, 59, 58, 44, 42, 41, 40 and 5 patients — have denominators that are already perfectly EMC-pure, with nothing to disaggregate, and they report **no adverse events at all**. Drilon states 21 EMC patients received 32 evaluable chemotherapy courses and reports response and progression for them without a single toxicity sentence; Bishop reports 33 EMC patients treated with radiotherapy and no toxicity of any grade; Chiusole reports 20 EMC patients on chemotherapy, 14 on second line, and no toxicity. **Fourth failure mode, `PRIMARY` at abstract level: in the EMC-only literature the adverse-event denominator is not aggregated away — it is simply never reported.** That is a different defect with a different remedy, and it is the substantive new content of this run.

### 5.5 The claim's true support set

Over the **57** distinct papers lane 7 has now examined across both axes:

| | Papers | Which |
|---|---|---|
| Carry a **graded, counted, EMC-specific** AE denominator | **1** | **PMID 31331701** — Stacchiotti pazopanib EMC-only phase 2, safety population 26 (23 centrally molecularly confirmed), authors' own grade 3 counts: hypertension 9/26, ALT 6, AST 5; no grade 4, no deaths. [DOI](https://doi.org/10.1016/S1470-2045(19)30319-5). Abstract strength only, per CLOSED-WORK |
| Carry an EMC-specific AE statement that is **narrative and ungraded** | **8** | 41476450, 41323055, 35494187, 23058004, 30534357, 21547635 (W07d's seven, minus 31331701) + 24345066 (Axis R, retained strength) |
| Report AEs only over a **mixed** denominator | **7** | 36568164, 32547189, 34716194, 31827370, 28852958, 39441321 (W07d's six) + 33203665 (Axis R) |
| Report **no** AE bearing on EMC | **38** | 12 from W07d's union + 27 Axis-R (with one Axis-R paper double-counted nowhere; see arithmetic note) |
| **UNKNOWN / unrecovered** | **3** | 28187993 (abstract absent), 24703573, 35144048 |

*Arithmetic note:* 1 + 8 + 7 + 38 + 3 = 57. The union-26 and Axis-R-31 tallies are disjoint by construction (`comm -23`).

> **Finding (3) — the true support set is a single paper.** The graded half of lane 7's load-bearing claim rests on **exactly one study, PMID 31331701**, and on **one denominator, 26** — itself only 23-confirmed. It does not rest on nine papers, on 26, or on 57. Those numbers describe the **search space over which the exception was shown to be unique**, not the evidence base. The nine-paper set the lane has been quoting is a *sampling frame*, and quoting it as if it were support overstates the evidentiary base by roughly ninefold.

That distinction is what makes the two nulls valuable. A single-paper support set would normally be fragile; what two independent widenings buy is the demonstration that its **uniqueness** is robust — 57 papers, two orthogonal selection rules, one exception, found by both. The claim is simultaneously **thinly supported and well-tested**, and lane 7 must say both.

### 5.6 No clinical claim

Nothing here bears on the safety, tolerability, therapeutic window, efficacy or clinical readiness of pazopanib, trabectedin, apatinib, cabozantinib, sunitinib, bortezomib, nivolumab, carfilzomib, any anthracycline, radiotherapy or any other agent or procedure, for any patient. This is bookkeeping about what papers reported. **I computed no rate, derived no denominator from any percentage, imputed nothing, substituted no cohort n, added no case to any pooled denominator, and pooled nothing with anything.**

---

## Validation evidence

### RUN

**V1.** Start: `date -u` → `Tue Sep  8 02:50:58 UTC 2026`; `git rev-parse HEAD` → `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`; `git status --porcelain` → no output. Exit 0.

**V2.** Claim-location grep (exit 0), 17 hits, all under `…/opus-capacity-campaign-20260908/reports/`. Key verbatim lines quoted in §5.1 table with their `file:line`. **No hit outside campaign reports.**

**V3.** Pre-existing counterexample, `sed -n '95,150p' research/manuscripts/care-delivery/emc-adaptive-scheduling-pazopanib.md` (exit 0), verbatim at `:143-144`:
```
Anchor: adaptive abiraterone held 10 of 11 patients in stable oscillation at **47 % of standard
cumulative dose** (PMID 29180633, `[secondary]`). There is a real toxicity burden to halve: grade 3
hypertension **9/26 (35 %)**, ALT rise **6/26 (23 %)**, AST rise **5/26 (19 %)** in the EMC trial
(`[API]`), over a median PFS measured in years.
```

**V4.** Axis-R extraction, verbatim (exit 0):
```
$ grep -oiE 'pmid[^0-9]{0,6}[0-9]{7,8}' research/data/emc-clinical-registry.json systems/graph/evidence.json | grep -oE '[0-9]{7,8}' | sort -u | wc -l
34
```
The 34: `10366145 12599237 12709428 15739208 15920699 18951519 20818875 24345066 24703573 27402218 27418251 30511879 30786186 31331701 31417269 31436747 32547189 32612944 32953543 33203665 35144048 35704774 35962783 36316541 36568164 36636023 36825763 36948401 37205599 37781179 38558247 40941020 42660639 8961274`. A stricter `"pmid":` key-only extraction gave 33, differing by exactly one (`32547189`, present in the registry as prose rather than a `pmid` key); the looser 34-set was used, so no candidate was dropped.

**V5.** Set arithmetic, verbatim (exit 0):
```
$ comm -12 axisR2.txt u26.s   -> 31331701 32547189 36568164        (|∩| = 3)
$ comm -23 axisR2.txt u26.s | wc -l -> 31                          (|Axis R \ union26| = 31)
```
`u26.s` is W07d's union of 26, transcribed from its report, `sort -u`, `wc -l` → 26.

**V6.** Identifier guard, `mcp__PubMed__convert_article_ids` on 14 PMIDs. Server `"status":"ok"`, 14 records, **each carrying `"requested-id"` identical to its `"pmid"`**. Verbatim sample: `{"pmcid":"PMC2779719","pmid":"18951519","doi":"10.1002/cncr.23978","requested-id":"18951519"}`. **Zero mismatches; nothing discarded.**

**V7.** `mcp__PubMed__get_article_metadata` ×2, `"count":7` and `"count":7` — **14 of 14 resolved, zero UNRECOVERED**. Every sentence quoted in §5.3 is a verbatim substring of an abstract returned by those two calls. Each returned `identifiers.pmid` equals a requested PMID; the returned set equals the requested set exactly.

**V8.** End: `date -u` → `Tue Sep  8 02:54:14 UTC 2026`; `git rev-parse HEAD` → `4d950cf036294627b7ae67dfb306cc1875d702ac` (**advanced mid-run, recorded, not acted on**); `git status --porcelain | grep -c .` → `0`. Scratch (`/tmp/claude-0/w07e/`): `axisR.txt`, `axisR2.txt`, `axisR_new.txt`, `emc-clinical-registry.json.raw`, `evidence.json.raw`, `u26.s`, `union26.txt`. **Working tree clean; zero repository writes.**

### PROPOSED (NOT RUN)

- **Full-text check of the Group-I EMC-only cohorts for a toxicity section absent from the abstract** — `PMC2779719` (Drilon, 21 patients / 32 chemo courses), `PMC7308468` (Chiusole, 20 on chemo), `PMC7771031` (Bishop, 33 RT+surgery), `PMC4946242` (Morioka). **Not run** — outside this dispatch's scope. Consequence: §5.4's fourth failure mode is **abstract-level-provisional**, exactly as W07b's rows were before W07c. Had I run it, `convert_article_ids` would have confirmed each PMCID first and every returned identifier been checked against the request.
- **n(EMC) recovery for `15739208`, `33203665`, `40941020`** from full text, which would move them between NO-AE-DATA and MIXED-ARM-ONLY. Not run.
- **A third axis** (e.g. the EMC ClinicalTrials.gov registration set, or reference lists of the ten Group-I cohorts). Not run.
- **Any pazopanib `31331701`, sunitinib `24703573`, CTARC `35144048` or anthracycline `24345066` retrieval.** Deliberately not attempted — CLOSED-WORK routes, untested by me.
- `scripts/preflight.sh` — not run; not authorised by this dispatch and no code was authored.

### Content-policy refusals

**None encountered.** No branch was refused, no denied route replayed, nothing rephrased, rerouted or relabelled.

---

## Limitations

1. **Abstract-level only.** Every Axis-R classification rests on the PubMed abstract. A histology- or toxicity-specific table inside any of the 14 retrieved full texts would change its row. **Zero is what these abstracts report, not what these papers contain** — UNKNOWN, not proof of absence. This is the single largest soft edge and it is the next action.
2. **Axis R is bounded by two files.** PMIDs cited elsewhere in the tree (other `research/literature/*.json` probes, manuscripts, `routes.json`) are outside it. The axis is *independent*, not *exhaustive*; a third store could add members. I chose two canonical stores rather than the whole tree to keep the inclusion rule stateable in one sentence and reproducible.
3. **Three Axis-R members were classified without retrieval** (`24703573`, `35144048`, `24345066`) because CLOSED-WORK forbids the routes. Their AE content is UNKNOWN at any strength beyond what is retained; two are marked UNKNOWN precisely so they cannot be silently counted as nulls. If either turned out to carry a graded EMC-specific denominator, the support set would grow — that possibility is live and unresolved.
4. **Fifteen of the 31 were classified from committed repository annotations rather than fresh retrieval** (the NSCLC palliative trials, VTE sources, molecular papers). Those rows are `SECONDARY` and carry the repository's provenance, not mine.
5. **The support-set count of 1 depends on W07b's reading of `31331701`'s abstract, which I did not re-verify** and am not permitted to. It is `SECONDARY` to me throughout.
6. **`n(EMC)` is UNKNOWN for three mixed trials**, so I cannot say whether those studies contain EMC patients at all; UNKNOWN is not zero in either direction.
7. **HEAD moved during the run.** All `file:line` references are pinned to `3f5fc95d…`; a later commit could shift line numbers, though the campaign reports are append-only in practice.
8. **This establishes nothing clinical**, and the count of qualifying denominators is a statement about publication practice, never about whether any treatment is tolerable, safe or advisable.

---

## Stop condition

**Set at the outset:** return as soon as (a) the load-bearing claim is located with `file:line` and any scope divergence recorded, (b) an axis independent of vocabulary is declared and enumerated, (c) each addition is classified for a graded EMC-specific AE denominator with the count stated, and (d) the true support set is named with its count — or as soon as ~40 calls / ~40 minutes is reached, whichever first.

**Status: MET, on all four, well inside budget.** (a) §5.1 — four divergent assertions, one of them false and uncorrected, plus a pre-existing in-tree counterexample. (b) §Method + §5.2 — Axis R declared before enumeration, 31 additions. (c) §5.3–5.4 — all 31 classified; **new qualifying graded EMC-specific denominators = 0**. (d) §5.5 — support set = `{PMID 31331701}`, count **1**, against a 57-paper search space.

---

## Tool-call and wall-clock count actually used

**Tool calls: 13** (9 Bash, 1 ToolSearch, 1 `convert_article_ids`, 2 `get_article_metadata`). **Wall clock: ~3.3 minutes** (02:50:58 → 02:54:14 UTC). Far inside the ~40-call / ~40-minute self-observed target; returned on stop-condition satisfaction rather than padding.

---

## Next concrete action

**Full-text check of the four Group-I EMC-only cohorts with PMC availability — `PMC2779719` (Drilon, 87 EMC / 21 on chemotherapy / 32 courses), `PMC7308468` (Chiusole, 59 EMC / 20 on chemotherapy / 8 drug holidays), `PMC7771031` (Bishop, 41 EMC / 33 combined-modality RT) and `PMC4946242` (Morioka, 5 EMCS+MCS) — for a toxicity section or table absent from the abstract.** This is the exact successor W07c was to W07b, applied to the new axis, and it is decisive in both directions: if any of the four reports graded events over its EMC-only denominator, the support set grows from 1 and §5.4's fourth failure mode is wrong; if none does, the mode is established at full-text level and lane 7 gains a sharper claim than it has — that EMC's *own* cohort literature, with denominators already pure, omits harm entirely. Four articles, all PMC-available, binary per row, one `convert_article_ids` call plus one `get_full_text_article` call, no denied route touched.

**Also flagged for the coordinator, not for research:** `W07-patient-reported-outcomes-denominators.md:173` and `:290` still assert a refuted universal. That is a two-line strike-through by the report's owner, not new work, and it should not wait on another lane-7 dispatch.
