<!-- collected 2026-09-08T04:40:39Z by campaign coordinator; agent id a05fbf7cc4f49de58; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a05fbf7cc4f49de58.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted; report follows.

## Worker

**W30d**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: evidence-contract enforcement — W30c's named successor, a line-by-line audit of `scripts/validate-registry.mjs` against every registry-facing sentence of `systems/POLICY-evidence.md`. (Re-dispatch; the earlier attempt produced no report, and I started fresh with no inherited state.)

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in my environment corroborates it — no variable names a model. The coordinator must extract the served model from the transcript.

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

**Start** — `date -u` → `Tue Sep  8 04:33:20 UTC 2026`; `git rev-parse HEAD` → `408b676aec3625a36917755662516232a27a1278`; `git status --porcelain` → **empty**.
**End** — `date -u` → `Tue Sep  8 04:36:30 UTC 2026`; `git rev-parse HEAD` → `408b676aec3625a36917755662516232a27a1278` (**HEAD did not move this run**); `git status --porcelain` → **empty**.
`git diff --stat 408b676a HEAD -- systems/POLICY-evidence.md scripts/validate-registry.mjs research/data/emc-clinical-registry.json` → empty, exit 0. Every load-bearing input byte-identical at start and end.

**Write isolation honoured: zero repository writes, zero git write operations, no network, no retrieval, no MCP call, no `preflight.sh`.** All mutation work ran against **copies** under `/tmp/claude-0/w30d/probe/`, never the repository; `git status --porcelain` empty at both ends. Scratch deleted (`rm -rf /tmp/claude-0/w30d`; `ls` → "No such file or directory"). **I authored no repair, no patch, no gate and no test, and edited neither file.**

## Question

**Read `scripts/validate-registry.mjs` line by line against every registry-facing sentence of `systems/POLICY-evidence.md`. For each requirement sentence: what implements it, at which `file:line`, and is the check EXACT / WEAKER-THAN-TEXT / STRONGER-THAN-TEXT / NOT-IMPLEMENTED? Are W30c's four the whole list? And for each WEAKER row, does the committed registry currently exploit the weakness (live defect) or not (latent)?**

Open because W30c found its four *incidentally*, while reading the script for an enforcement-map purpose, and explicitly named the systematic pass as its successor. It is the one script that carries the whole contract into the commit loop and it has no test of its own.

## Prior-work check

```
$ find . -path ./.git -prune -o -name '*W30c*' -print
  ./research/autonomy/opus-capacity-campaign-20260908/reports/W30c-policy-sections-without-gates.md
$ grep -rn "validate-registry" --include='test_*.py' --include='*.test.mjs' . | grep -v opus-capacity-campaign
  ./scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py:7   (docstring reference only)
$ grep -c "<field>" systems/POLICY-evidence.md   for 11 validator field names   (see Result §D)
```

Read in full before working: `systems/POLICY-evidence.md` (386 l), `reports/W30c-policy-sections-without-gates.md`, `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`. Note for the coordinator: **the dispatch path `reports/W30c-…` does not exist**; there is no top-level `reports/` directory. The file is under `research/autonomy/opus-capacity-campaign-20260908/reports/`.

**Confirmed not replayed:** W30c's 16-unit enforcement map and its preflight-tier findings (I re-derive none; I extend to sentence level on one script); W30b's §2.6/§2.7 audit; the 0-of-89 backlog verification (not touched); the `origin/literature-cache` question. **W25 not read, not referenced.** Per COMMON-BRIEF I used `pytest` at `/root/.local/bin/pytest`, never `python3 -m pytest` — though in the event I ran no pytest suite, because nothing in this lane needed one and no test of this script exists to run.

**Refinement of W30c's "no test":** the single grep hit above is a **docstring**, not coverage. `scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py` scans hand-authored JSON for duplicate keys and never invokes `validate-registry.mjs` (its `subprocess` calls are `git` and a temp-repo fixture). W30c's claim stands. Its docstring does record a real, measured historical blind spot of the validator (2026-08-27: two `galitskiy2025emcpembrolizumab` records under one object; `JSON.parse` keeps the last, so the validator checked the survivor and never saw the dead twin) — that blind spot is now covered by *that* test, not by the validator.

## Method and inputs

- **Requirement source:** `/home/user/Rare-cancers/systems/POLICY-evidence.md` @ `408b676a`, read in full. I extracted every sentence that states a condition on the artifact `research/data/emc-clinical-registry.json`, including the normative comments inside the two JSONC blocks (§1.2's citation record, §3's `evidenceQuestions` record) and §5's checklist. §2.2, §2.6 and §2.7 govern *computations and other artifact classes*, not registry bytes; I record them as out-of-artifact rather than as validator gaps.
- **Implementation source:** `/home/user/Rare-cancers/scripts/validate-registry.mjs`, all 170 lines.
- **Write-freedom confirmed from source before running:** its only `node:fs` import is `readFileSync` (`:19`); `grep -n -E "writeFile|appendFile|mkdir|rmSync|unlink|createWriteStream|execSync|spawn|fetch"` returns **no match**. Output is `console.log/warn/error` and `process.exit` only.
- **Mutation probe:** a copy of the script and the registry under `/tmp/claude-0/w30d/probe/`; each mutation is applied to a **fresh** copy of the committed registry, so mutations do not compound. This turns "I read the source and think X passes" into a measured exit code.
- Tools: `node` (repo default), system `python3` (stdlib only), `git`, `grep`. No third-party packages.

## Result

`node scripts/validate-registry.mjs` on the committed tree: **`OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).`**, **real exit code 0**, tree clean afterwards. So the registry passes today with *zero* warnings — which matters below, because it means every warning-tier requirement is currently satisfied on the merits, not merely tolerated.

Registry shape measured: 25 citations, 14 cohorts (5 pooled / 9 context), 4 patients, 2 `evidenceQuestions` (9 positions), 10 `systemicEvidence`, 6 `emergingTreatments`, 11 `studies`, 12 metric blocks.

### A. The divergence list, per requirement sentence

Legend: **EXACT** = check and text coincide; **WEAKER** = artifact can violate the text and pass; **STRONGER** = the check forbids more than the text says (or has no policy sentence at all); **NOT-IMPL** = no check in this script. "Exploited?" is measured against the committed registry.

| # | § | Policy sentence (quoted) | Implementing check | Class | Exploited? |
|---|---|---|---|---|---|
| R1 | 1.1 | "Each cancer file carries a `registry.citations` map keyed by a short id" | `:51 const citations = reg.citations || {}` — absence silently defaults to empty | **WEAKER** | **No** (25 citations present). Probe **M9** (citations deleted) exits **1** only because *cohort/patient* `sourceId`s then dangle; a registry with no citations and no rows would pass. |
| R2 | 1.1 | "Every patient row … references a citation with `sourceId`" | `:71-72` presence (ERROR) + `:73-74 !hasCite(p.sourceId)` (ERROR) | **EXACT** | — |
| R3 | 1.1 | "…and every cohort references a citation with `sourceId`" | `:85 if (!hasCite(c.sourceId))` (ERROR) | **EXACT** | — |
| R4 | 1.2 | "**Hard requirements** (validator-enforced): at least one **resolvable identifier** (`pmid`, `pmcid`, or `doi`), a `title`, a `year`, and a `url`." | `:55` title, `:56` year, `:57` `!pmid && !pmcid && !doi`, `:58` url — all ERROR; empty strings are falsy so also caught | **EXACT** | — (measured id coverage: 9 pmid+doi, 7 all three, 4 pmcid only, 3 pmcid+doi, 2 doi only) |
| R5 | 1.2 | "Record the `license`" | `:59 warns.push(\`${cw} has no license recorded\`)` | **WEAKER** (imperative → advisory) | **No** — 25/25 carry `license`. Probe **M6** (all licenses stripped) → 25 WARNs, **exit 0**. |
| R6 | 1.2 | "never reproduce more than it permits" | none | **NOT-IMPL** | n/a (not decidable from the file) |
| R7 | 1.3 | "`sourceId` is **the document you actually read the number in**" | none | **NOT-IMPL** | n/a (undecidable from data) |
| R8 | 1.3 | "If that document is a review/secondary source, set `provenance: \"secondary\"` and record `primaryRef`" | `:86-87` cohorts, `:134` positions, `:150` systemicEvidence — all ERROR | **WEAKER — NEW, not in W30c's four** | **No.** The check is `provenance === "secondary"`; **`provenance` has no enumerated vocabulary anywhere in the script**, so any other spelling skips the `primaryRef` requirement entirely. Probes **M5** (`"secondry"`, primaryRef removed) and **M5b** (`"review"`, primaryRef removed) both **exit 0, 0 warnings**. Measured vocabulary in the registry is clean: cohorts `{primary:11, secondary:3}`, positions `{primary:5, secondary:4}`, systemicEvidence `{primary:9, secondary:1}` — no third value anywhere. Latent. |
| R9 | 1.3 | "**Do not invent an identifier** (PMID/DOI) for a primary you have not actually fetched" | none | **NOT-IMPL** | n/a |
| R10 | 1.3 / 1.2 | "`verified: true` is set **only** when the link was opened and confirmed to support the exact claim. Auto-fetched but unread → `verified: false`." | none — no line reads `verified` | **NOT-IMPL** | Probe **M8** (a citation flipped to `verified:false`) → **exit 0, 0 warnings**: the field is inert in both directions. 25/25 assert `true`; **UNKNOWN**, as W30c also concluded. |
| R11 | 2.1(1) | "**Confirmed EMC** (molecular/histological), matching the page." | none (the `criteria` field is never read; 13 of 14 cohorts carry it) | **NOT-IMPL** | n/a |
| R12 | 2.1(2) | "**Explicit integer counts** are reported: `{events, denom}`." | `:98 typeof m.events !== "number" \|\| typeof m.denom !== "number"` | **WEAKER** (W30c #1, **confirmed by execution**) | **No.** Probe **M1** (`events: 3.5`) → **exit 0, 0 warnings**. Measured: 0 of 12 metric blocks non-integer; every count cell an `int`. *Sub-case closed:* `NaN` is `typeof "number"` but is **not representable in strict JSON** — probe **M1b** dies at `JSON.parse` (`:33-38`, exit 1), so the NaN route is blocked by the parser, not by the check. |
| R13 | 2.1(2) | "We **never derive counts from a published percentage** for pooling (rounding invents data)." | none — no line relates a `*Pct` field to an `{events,denom}` block, nor forbids a pooled cohort from carrying only a percentage | **NOT-IMPL** | **No.** Measured: all 5 `*Pct`/`*Text`-only cohorts (indices 5, 7, 10, 11) are `pool:false`; all 5 pooled cohorts carry explicit `{events,denom}` and no `*Pct`. Clean by authorship, not by gate. |
| R14 | 2.1(3) | "The outcome is a **true outcome, not the inclusion criterion** — e.g. a 'metastatic at diagnosis' cohort does **not** contribute to the *metastasis* rate" | none in this script (W30c located it in `research/meta/meta-analysis.mjs:36`, which no gate runs) | **NOT-IMPL** | **No** — but this is the closest to live. Cohort[1] *is* `"metastatic-at-dx"`, `pool:true`; it carries `diseaseDeath` and `otherCauseDeath` and **no metastasis block**, so it does not contribute. Probe **M11** (giving it `metastasis: {29,29}`) → **exit 0, 0 warnings**: the validator would admit the exact structurally-100% case §2.1(3) names by example. |
| R15 | 2.1 | "Everything else … is shown as **context** (`pool: false`)" with `contextReason` (§5 checklist: "set `pool:false` + `contextReason`") | `:88 if (c.pool === false && !c.contextReason) warns.push(...)` | **WEAKER** | **No** — 9/9 context cohorts carry a reason (`population-overlap` ×4, `percentage-only` ×3, `different-endpoint` ×2). Probe **M7** → 1 WARN, **exit 0**. |
| R16 | 2.3 | "**Within a study:** use **mutually exclusive strata** only… the validator flags two pooled cohorts that share both [`populationKey` and `stratum`]" | `:113-117`, `warns.push` | **WEAKER** (W30c #3) | **No** — 0 collisions today. |
| R17 | 2.3 | *same clause — the mechanism itself* | `:115 if (poolKeys[key]) …; else poolKeys[key] = i;` | **WEAKER — NEW, a defect W30c did not find** | **No, but the guard is absent, not merely advisory, for one specific cohort.** `poolKeys[key]` stores the **array index**, and **index `0` is falsy in JS**, so a collision whose first member is `cohorts[0]` is never reported *and* the `else` branch then overwrites the entry. Measured by probe: duplicating cohort[**0**] → `OK … 0 warning(s)`, **exit 0**; duplicating cohort[**1**], [2], [3] or [4] → the WARN fires correctly. `node -e` control: `Boolean({x:0}["x"]) === false`. Cohort[0] is `masunaga2025-jpreg::localized-surgical`, `n=134` — the **largest pooled cohort in the registry** and the one the manuscript's denominator weighting leans on hardest. |
| R18 | 2.3 | "**Never pool a whole-cohort row *and* its sub-strata.**" | `:114 const key = \`${c.populationKey}::${c.stratum \|\| ""}\`` | **WEAKER — NEW, not in W30c's four** | **No.** The key includes `stratum`, so a whole-cohort row (`stratum` absent → key `pk::`) and its sub-stratum (key `pk::localized`) are **different keys and never collide** — the guard cannot detect the pattern this sentence prohibits by name. Probe **M3b** (whole-cohort row appended alongside its own stratum, same `populationKey`) → **exit 0, 0 warnings**. Measured: the one multi-row `populationKey`, `masunaga2025-jpreg`, holds two *disjoint* strata (`localized-surgical`, `metastatic-at-dx`) and no whole-cohort row. Latent. |
| R19 | 2.3 | "**Across studies:** … the **smaller/overlapping** cohort is marked `pool: false` with `contextReason: \"population-overlap\"`" | none — no cross-study overlap detection; `populationKey` is only compared within itself, and 0 context cohorts even carry one | **NOT-IMPL** | **No** (4 context cohorts name `population-overlap` by authorship) |
| R20 | 2.4 | "**Time-anchored survival** (5-yr, 10-yr DSS/OS) is **never merged** into one number" | none — `fiveYearDSS` (2 cohorts) and `dssText` (8) get **no shape check and no consumer** | **NOT-IMPL** | **No** — vacuously, as W30c found: nothing in the tree merges them |
| R21 | 3 | "Contested clinical questions live in `evidenceQuestions[]`" + `question` required | `:124` iteration, `:126` `!q.question` (ERROR) | **EXACT** | — |
| R22 | 3 | consensus vocabulary `consensus-for \| consensus-against \| contested \| limited-evidence \| emerging` (JSONC comment) | `:122` `CONSENSUS`, `:127` ERROR | **EXACT** (set matches the comment element-for-element) | — |
| R23 | 3 | stance vocabulary `supports \| against \| mixed \| null` (JSONC comment) | `:123` `STANCES`, `:131` ERROR | **EXACT** | — |
| R24 | 3 | "Every position carries a real `sourceId`" | `:133 !hasCite(p.sourceId)` (ERROR) | **EXACT** for what is checkable ("real" beyond resolution is R7) | — |
| R25 | 3 | "A question marked `contested` must show **≥2 positions taking opposing stances** (validator-enforced) — you may not label something contested and then list one side." | `:139-140 if (!(stances.has("supports") && stances.has("against")) && !stances.has("mixed"))` | **WEAKER** (W30c #2, **confirmed by execution**) | **No.** Probe **M2** (the contested question reduced to a *single* `mixed` position) → **exit 0, 0 warnings** — literally "label something contested and then list one side". Measured: `rt-localized-emc` carries **5** positions, 2 `supports` + 3 `against`, satisfying the text. The parenthetical over-describes the check by one position. |
| R26 | 3 | "Always name the **mechanism of conflict**" (the `caveat` field) | none | **NOT-IMPL** | **No** — 9/9 positions carry `caveat`. Probe **M10** (all caveats + `bottomLine` stripped) → **exit 0, 0 warnings**. |
| R27 | 3 | "The `bottomLine` … must state what remains unproven" | none | **NOT-IMPL** | **No** — 2/2 present (see M10) |
| R28 | 3 | `"summary": "…plain-language synthesis that states the uncertainty…"` (JSONC) | none | **NOT-IMPL** | **No** — 2/2 present |
| R29 | 3 | "**Never** resolve a genuine controversy with a fabricated consensus" / "Link to the pool" | none | **NOT-IMPL** | n/a (as W30c's F4: `evidenceQuestions` has exactly two references tree-wide, both in this script) |
| R30 | 4.1 | "Every cohort/citation records `studyPeriod: [firstDxYear, lastDxYear]`" — **cohort side** | `:90-91` presence on pooled cohorts, `warns.push`, suppressible by `studyPeriodUnknown` | **WEAKER** (W30c #4) | **No.** Probe **M4** (cohort[0]'s `studyPeriod` removed, no `studyPeriodUnknown`) → 1 WARN, **exit 0**. Measured: 4 of 5 pooled cohorts carry a period; the 5th (Meis-Kindblom) carries `studyPeriodUnknown: true`, the policy's own "mark it absent" path. **Non-pooled cohorts are not checked for presence at all** (5 of 9 lack a period; 3 carry `studyPeriodUnknown`, 2 carry neither). |
| R31 | 4.1 | same sentence — **citation side** | `:119` runs `checkPeriod` over citations but `checkPeriod` `:64` returns immediately when `sp === undefined`; there is **no presence check and no `studyPeriodUnknown` path for citations** | **NOT-IMPL — NEW, not in W30c's four** | **No, by construction** — 13 of 25 citations carry no `studyPeriod` and none is marked absent. §4.1's next sentence ("mark it absent") makes this permissible content, so it is not a registry violation; what is missing is any *affirmative marking* on the citation side, so silence-because-unstated and silence-because-forgotten are indistinguishable. |
| R32 | 4.1 | shape: `[startYear, endYear]`, "the years patients were **diagnosed/treated**" | `:65-67` — array, length 2, both `Number.isInteger`, `start<=end<=CUR+1`, ERROR | **EXACT / mildly STRONGER** (`<= CUR+1` has no policy sentence; it is sound). Note the **integer test the policy asked for in §2.1(2) exists here and only here**. | Probe **M12** (`[-5000, 1200]`) → exit 0: no lower bound, but the policy states none either. |
| R33 | 4.1 | "**Record it only from what the source states; never infer or fabricate it**" | none | **NOT-IMPL** | n/a (undecidable from data) |
| R34 | 5 | "`node scripts/validate-registry.mjs` passes" | the script itself | **EXACT** | passes, exit 0 |

**Out-of-artifact (correctly not this script's job):** §2.2 (Wilson/pooling arithmetic), §2.5 (user-facing limitations — retired surface), §2.6 (a)–(h) and §2.7 (a)–(f) (other artifact classes), §4.2, both §4.3s (display/generalization — retired surface). I do **not** count these as validator gaps.

### B. Are W30c's four the whole list? — **No.**

W30c's four are all confirmed by execution (R12, R25, R16, R30). The systematic pass adds **five more**, of which one is a code defect rather than a policy-vs-check gap:

1. **R17 — the falsy-zero bug at `:115`.** The double-counting guard is silently inoperative for any collision whose first member is `cohorts[0]`. This is the strongest finding of the run: §2.3 is the policy's self-declared "cardinal sin", the guard was already only a warning (R16), and for the registry's largest pooled cohort it is **not even that**. Measured, not inferred: dup-of-[0] → `OK … 0 warning(s)`; dup-of-[1..4] → WARN.
2. **R18 — the guard's key cannot express the pattern §2.3 names.** "Never pool a whole-cohort row *and* its sub-strata" is precisely the case where `stratum` differs, so the `populationKey::stratum` key never collides.
3. **R8 — `provenance` has no vocabulary check**, so the secondary⇒`primaryRef` rule at three call sites is skippable by a typo.
4. **R31 — `studyPeriod` presence is unchecked on citations**, where §4.1's "every cohort/citation" also applies.
5. **R13 / R14 — the two §2.1 clauses with no check at all in this script**: the percentage-back-derivation ban and the outcome-≠-inclusion-criterion rule. W30c classified §2.1(2) as "gate weaker than text" as a whole; separating the sentences shows the integer clause is *weakly* checked while the back-derivation clause is *not checked at all*, and R14's absence is demonstrable (probe M11).

Also worth the owner's attention as a **soft** row: **R5** (`license`) and **R15** (`contextReason`) are the same error-vs-warning shape as W30c's R16/R30, bringing the warning-tier count to four.

### C. Live vs latent — the summary the owner asked for

**Every WEAKER and NOT-IMPL row above is LATENT. Zero are live.** The committed registry satisfies the *policy text* on every sentence that is decidable from the file, not merely the weaker gate — including all four of W30c's and all five of mine. Measured supports: 0 of 12 metric blocks non-integer; 0 `populationKey`+`stratum` collisions and 0 whole-row/stratum pairs; 3 provenance vocabularies clean at `{primary, secondary}` with 0 third values across cohorts, positions and systemicEvidence; 25/25 licenses; 9/9 `contextReason`; 9/9 `caveat`; 2/2 `bottomLine` and `summary`; 5/5 pooled cohorts with a period or an explicit `studyPeriodUnknown`; the one contested question at 5 opposing positions; all percentage-only series `pool:false`; and the metastatic-at-dx cohort carrying no metastasis block. The validator's own run reports **0 warnings**, so nothing is even being tolerated at the advisory tier.

The distinction that matters for triage: R17 is latent *today* but is a **defect in the mechanism** rather than a deliberate strictness choice, and it degrades silently — a future duplicate of cohort[0] would produce no output at all, whereas a duplicate of any other cohort produces a visible WARN. The other eight are consistent, intentional-looking choices about strictness that the owner may have made on purpose.

### D. One structural observation, offered as context not as a finding

Nine of the validator's checks enforce field names that **appear zero times in `POLICY-evidence.md`**: `dataStatus` / `SAMPLE_SYNTHETIC` / `dataStatusBanner` (`:43-49`), `vitalStatus` and the patient field list (`:71-72`), the patient `stage` vocabulary (`:75-76`, warn), cohort numeric `n` (`:84`), `otherCauseDeath` and the disjointness pair (`:96-110`), `systemicEvidence` (`:146-151`), `emergingTreatments` (`:152-155`), `studies` (`:157-160`), `studyPeriodUnknown` (`:90`). These are **STRONGER-THAN-TEXT**: real invariants the script defends that the policy never wrote down. The `otherCauseDeath` pair is documented in the script's own comment (`:92-95`, added 2026-08-09) with a clear rationale and is not reflected in the policy at all. So the two documents diverge in *both* directions — the policy claims two enforcements it does not fully have, and the script defends nine invariants the policy never claims. Both halves are the owner's to reconcile.

## Validation evidence

**RUN.** Environment: `/home/user/Rare-cancers` @ HEAD `408b676aec3625a36917755662516232a27a1278` (unchanged start→end), `node` (repo default), system `python3` (stdlib only, no third-party packages), `git`, `grep`. All mutation execution under `/tmp/claude-0/w30d/probe/` on copies; the repository was read-only throughout.

Write-freedom of the script, confirmed **before** running it:
```
$ grep -n -E "writeFile|appendFile|mkdir|rmSync|unlink|createWriteStream|execSync|spawn|fetch|require\(|import " scripts/validate-registry.mjs
19:import { readFileSync } from "node:fs";
20:import { fileURLToPath } from "node:url";
21:import { dirname, join } from "node:path";
```

The real run on the committed tree:
```
$ node scripts/validate-registry.mjs
OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).
REAL_EXIT=0
$ git status --porcelain
(empty)
```

Mutation probe — each mutation applied to a **fresh** copy of the committed registry (verbatim):
```
=== BASELINE (unmodified copy) ===
OK - EMC clinical registry valid: 25 citation(s), 14 cohort(s). 0 warning(s).   exit=0
M1    exit=0  OK - ... 0 warning(s).                       # events: 3.5           -> R12
M1b   exit=1  ERROR ... cannot read or parse - Unexpected token 'N' ...           # NaN -> parser
M2    exit=0  OK - ... 0 warning(s).                       # contested, 1 "mixed"  -> R25
M3    exit=0  OK - ... 15 cohort(s). 0 warning(s).         # exact dup of [0]      -> R17
M3b   exit=0  OK - ... 15 cohort(s). 0 warning(s).         # whole row + stratum   -> R18
M4    exit=0  WARN ... is pooled but has no studyPeriod                            -> R30
M5    exit=0  OK - ... 0 warning(s).                       # provenance "secondry" -> R8
M5b   exit=0  OK - ... 0 warning(s).                       # provenance "review"   -> R8
M6    exit=0  WARN ... has no license recorded  (x25)                              -> R5
M7    exit=0  WARN ... is context (pool:false) but gives no contextReason          -> R15
M8    exit=0  OK - ... 0 warning(s).                       # verified: false       -> R10
M9    exit=1  ERROR ... sourceId "gunasekaran2026" has no registry.citations entry -> R1
M10   exit=0  OK - ... 0 warning(s).                       # caveats+bottomLine    -> R26/27
M11   exit=0  OK - ... 0 warning(s).                       # metastatic-at-dx: 29/29 -> R14
M12   exit=0  OK - ... 0 warning(s).                       # studyPeriod [-5000,1200] -> R32
```

R17 isolated, duplicating each pooled cohort in turn (verbatim):
```
  dup-of-cohort[0]: OK - EMC clinical registry valid: 25 citation(s), 15 cohort(s). 0 warning(s).
  dup-of-cohort[1]: WARN ... registry.cohorts[14] "DUP-of-1" shares populationKey+stratum with cohort[1]
  dup-of-cohort[2]: WARN ... shares populationKey+stratum with cohort[2]
  dup-of-cohort[3]: WARN ... shares populationKey+stratum with cohort[3]
  dup-of-cohort[4]: WARN ... shares populationKey+stratum with cohort[4]
$ node -e 'const k={};k["x"]=0;console.log(Boolean(k["x"]))'
false
```

Registry enumeration (stdin heredoc, key lines verbatim):
```
citations: 25   cohorts: 14   patients: 4   evidenceQuestions: 2
systemicEvidence: 10   emergingTreatments: 6   studies: 11
dataStatus: partial-curated | banner present: True
non-integer count cells: []
provenance (cohorts):   Counter({'primary': 11, 'secondary': 3})
provenance (positions): Counter({'primary': 5,  'secondary': 4})
provenance (systemic):  Counter({'primary': 9,  'secondary': 1})
pooled popKey groups: masunaga2025-jpreg -> [(0,'localized-surgical'), (1,'metastatic-at-dx')];
                      meisKindblom1999 -> [(2,None)]; ussc2022 -> [(3,None)]; chiusole2020 -> [(4,None)]
populationKey on pool:false cohorts: []
citations lacking studyPeriod: 13 of 25
studies missing url: 0  missing title: 0   emerging missing url: 0
patients stage: Counter({'localized': 3, 'distant': 1})
```

**PROPOSED (NOT RUN).** None. I ran no pytest suite (no test of this script exists), no generator, no `preflight.sh`, `research/meta/meta-analysis.mjs` (it writes `results.json`), or any network call. I authored no repair and assert no test result anywhere.

## Limitations

1. **This audits one script against one policy file.** A requirement could be enforced elsewhere — W30c already showed §2.1(3) lives in `meta-analysis.mjs` and several sections have opt-in pytest coverage. "NOT-IMPL" in my table means **not implemented in `validate-registry.mjs`**, which for the commit loop is what matters, but it is not a claim of tree-wide absence.
2. **Sentence extraction involves judgement.** I counted normative JSONC comments as requirements and excluded illustrative fields (`short`, `authors`, `journal`, `design`, `n`, `population`, `accessed`) that §1.2 shows but does not list among its "hard requirements". A different reasonable reading would add rows; it would not remove the nine divergences, each of which is anchored to a quoted sentence and a measured exit code.
3. **Latency is a snapshot at one commit.** "Latent, not live" describes `408b676a`. It is a property of the current registry, not a guarantee about the next edit — which is exactly why R17 matters.
4. **The mutation probe proves what passes, not what a maintainer would do.** M5/M5b/M11 construct data no careful curator would write; they establish the gate's boundary, not a likelihood.
5. **Small denominators.** 14 cohorts, 25 citations, 2 evidence questions, 12 metric blocks. A clean audit at n=14 is a clean audit at n=14.
6. **R7, R9, R10, R33 are undecidable from the repository.** They record acts performed outside it (a link opened, a source read). I retrieved nothing, so `verified: true` on 25 citations remains **UNKNOWN** — not a pass and not a fail, as W30c also concluded.
7. **No clinical claim whatsoever.** Everything here concerns JSON conformance to a repository policy. Nothing in this report says that radiotherapy, chemotherapy, or any agent works, is safe, is selective, or should be given to anyone; no count in the registry is restated as a clinical claim. There is no wet lab.

## Stop condition

**Set up front:** produce a per-sentence divergence list covering every registry-facing sentence of `POLICY-evidence.md` against all 170 lines of `validate-registry.mjs`, each row carrying a quoted policy sentence, a `file:line` (or a recorded absence), a classification, and — for every WEAKER row — a measured live/latent determination against the committed registry; settle whether W30c's four are exhaustive; then return without authoring any repair.

**MET.** 34 rows produced. W30c's four are confirmed by execution and are **not** exhaustive: five further divergences, including one code defect (`:115` falsy-zero) that disables the §2.3 guard entirely for the registry's largest pooled cohort. All nine WEAKER/NOT-IMPL rows are **latent — zero live**. The validator's real exit code on the committed tree is **0** with 0 warnings. Returning now rather than padding.

## Tool-call and wall-clock count actually used

**10 tool calls**, all Bash, of which 2 were the mandated start/end state records. **0** network calls, **0** retrieval calls, **0** repository writes, **0** git write operations, **0** generator invocations, **0** pytest runs. Wall clock **04:33:20Z → 04:36:30Z ≈ 3.2 minutes** of measured tool time plus report drafting. Well inside the ~40 call / ~40 minute target.

## Next concrete action

**Route R17 to the owner as a one-line, single-decision defect, separately from the other eight.** The eight policy-vs-check divergences are genuine owner choices between tightening a check and softening a parenthetical, and they can wait for a considered pass. R17 is different in kind: `:115` uses a stored array index as a truthiness test, so the §2.3 double-counting guard — the policy's "cardinal sin" — is silently inoperative for `cohorts[0]` and its `else` branch then discards the entry. It is measured (dup-of-[0] → 0 warnings; dup-of-[1..4] → WARN), it is not a matter of policy interpretation, and no reading of §2.3 wants it. **I have written nothing and propose no diff**; the smallest correct repair is a one-token decision that belongs to the owner, and the fact that the script has no test of its own is why a mutation probe was needed to find it at all.

A viable successor for this lane, if the owner wants one: the same per-sentence, mutation-probed treatment of `research/meta/meta-analysis.mjs` against §2.1(3), §2.2 and §2.4 — the manuscript's actual pooler, which W30c measured is run by **no gate, no test and no workflow**, and which consumes exactly the fields R12, R14 and R17 leave unguarded.
