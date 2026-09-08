<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:29:18Z UTC
     agent id acc0a5f4789027465 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-acc0a5f4789027465.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report below.

---

## Worker

- **Worker ID:** W07h · **Lane 7 refill** — audit of the 14 `ASSUMED`-provenance rows W07g named but did not check.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I report myself as Claude Opus 5 (`claude-opus-5`) under Claude Code 2.1.42 in the Anthropic Cloud remote container. I did not observe the served model and do not assert it as fact; the coordinator extracts the actual per-child runtime model from the transcript.
- **`date -u`** — start: `Tue Sep  8 03:21:23 UTC 2026` · end: `Tue Sep  8 03:24:47 UTC 2026`.
- **`git rev-parse HEAD`** — start: `e2214d4f2145c138da44b11c3d59899a5349abfb` · end: `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f`. **HEAD moved under me and the move is not mine**: `git diff --name-only e2214d4f ff6bb018` lists exactly 8 files, all `research/autonomy/opus-capacity-campaign-20260908/reports/W*.md` (W03e, W06g, W13g, W21d, W26, W27, W29, W30) — other lanes' reports written by the coordinator's collector. I re-read every line I cite at the end HEAD (§V5): all stable. All `file:line` references below are valid at `ff6bb018`. Neither HEAD equals the brief's frozen `92abbcb9…`, nor W07g's `98a0833f…`. Recorded, not worked around.
- **`git status --porcelain`** — start: **empty** (no output). End: **empty**. I wrote nothing into `/home/user/Rare-cancers`. My execution directory `/tmp/claude-0/w07h/` is **empty** (`ls -la` → `.` and `..` only; this audit needed no scratch execution). No git write operation; `scripts/preflight.sh` not run.
- **No network, no retrieval.** Zero PubMed MCP calls, zero WebFetch, zero WebSearch, zero HTTP. Every fact below is from a committed artifact in this checkout. **$0.**

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — literal output at start (identical at end). The `no_proxy` / `NO_PROXY` / `npm_config_noproxy` / `GLOBAL_AGENT_NO_PROXY` / `JAVA_TOOL_OPTIONS` lines match the pattern only through embedded `anthropic.com` hostnames and are reproduced in full per the "literal" instruction:

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

**W07g classified 14 of the 57 lane-7 rows as `ASSUMED` — composition traced to neither a full text nor an abstract — and checked none of them, calling them structurally low-risk on the ground that "a composition error in a mouse study, a cow, a parachordoma or an NSCLC trial cannot move a paper into the EMC-specific bucket" (`W07g:161`). Is that judgement correct? For each of the 14: which committed artifact and field did the classification actually come from, what does that artifact establish and not establish about the record's subject and composition, and can the record be, or contain, an EMC-specific human cohort that a composition error would move into the support set?** Plus: recompute W07g's incidental arithmetic finding about W07e §5.5 independently.

Open because the `ASSUMED` class was *created* by W07g and immediately left unexamined; it is the only provenance tier in lane 7 whose members have never been read against any source, primary or secondary, and W07g itself recorded their status as UNKNOWN rather than zero. The class exists to settle exactly one question — does anything in it matter — and nobody had answered it.

## Prior-work check

Commands run (all read-only, exit 0):

1. `wc -l COMMON-BRIEF.md CLOSED-WORK.md CORPUS-CONTEXT.md reports/W07{b,d,e,f,g}*.md` then `cat` of the three campaign docs; W07g read in full from the persisted tool-result file; W07e §5.2–§5.6 and W07d's tally lines read at `file:line`.
2. `for p in <14 PMIDs>; do grep -rn "$p" systems/graph/*.json | head -5; done` — located every one of the 14 in `systems/graph/evidence.json`, and only there among the graph files (36316541 additionally in `blockers.json:98`, `integrity.json:68`, `routes.json:3341` as commentary, not as a composition record).
3. `for p in <14 PMIDs>; do grep -c "$p" research/data/emc-clinical-registry.json; done` — **0 hits for all 14**.
4. `grep -rn -i "parachordoma"` and `grep -rn -i "\bcow\b|bovine"` across the campaign reports.
5. `grep -rln "15920699"` tree-wide; `grep -n "Subramanian" research/manuscripts/repurposing/pparg-direction-emc.md`; `grep -n "15920699" reports/W05-patient-independence-audit.md reports/W01c-emc-deposit-literature-inventory.md`.
6. `git ls-files | grep -i "literature-cache|early-palliative-care-survival-rct|vte-prophylaxis-ambulatory|bangerter-2023"` → **no output** (see §5.4).

**Not replayed, not probed, not rephrased:** `31331701` full text, `24703573`, `35144048`, `32856598`, `24345066`, and the trabectedin/RT DOI `10.4172/clinical-practice.1000433`. None of the six is among the 14 and none is touched here; I make no new statement about any of them. W07f's four full texts, W07c's two, and W07g's eight were not re-read or re-derived. **I authored and adjudicated no acceptance criterion**: the §5.4 rubric question W07g raised (does an n=1 EMC-only case report with a stated CTCAE grade enter the graded support set?) remains open, I refuse it too, and **no classification below depends on which way it goes** — none of the 14 carries an adverse-event statement of any kind in any committed artifact, so the rubric never engages.

## Method and inputs

- **Inputs, all committed at `ff6bb018`:** `systems/graph/evidence.json` (the sole source of all 14 classifications), `research/data/emc-clinical-registry.json` (negative control), `systems/graph/{blockers,integrity,routes}.json`, `research/manuscripts/repurposing/pparg-direction-emc.md`, and the campaign reports W07b / W07d / W07e / W07f / W07g, `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`. Frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/` consulted once for a directory listing.
- **Tools:** Bash (`grep`, `awk`, `sed`, `git show`, `git diff`, `ls`, `find`) only. No MCP tool of any kind.
- **Decision rule, fixed before reading.** For each record I ask three separate questions and keep the answers separate: **(i) Source** — which artifact and field did W07e's classification come from, quoted verbatim? **(ii) Establishes / does not establish** — what does that field state about the record's subject and study population, and what does it leave silent? **(iii) Structural capability** — could this record be, or contain, *an EMC-specific human cohort* (a set of human EMC patients over which an adverse-event statement could be made)? "Could contain an EMC patient somewhere in a mixed population" is answered separately from "could supply an EMC-specific denominator", because they are different questions and conflating them is how the class got its blanket clearance in the first place. Silence is UNKNOWN, never zero.
- **Nothing pooled, no rate, no denominator derived from a percentage, nothing imputed, no clinical claim.**

## Result

### 5.1 Headline, both directions

**W07g's operational conclusion is correct; its stated ground is wrong in three specific ways, and one of the fourteen is not what the class says it is.**

- **Correct:** on all evidence committed to this tree, **none of the 14 can move the graded support set**, which stays `{31331701}` under the lane's working reading. Not one of the 14 carries an adverse-event statement of any kind in any committed field. The class is genuinely low-consequence.
- **Wrong, 1 — the illustrative examples are not members.** Two of W07g's four exemplars are not in the 14 at all. The **cow** is `15980139` and the **parachordoma** is `21922364`, both W07d rows classified from PubMed abstracts (`W07d:165`, `W07d:160`) — i.e. `ABSTRACT-ONLY`, a *different* provenance tier. Half the sentence justifying the `ASSUMED` class describes non-members.
- **Wrong, 2 — "structurally incapable" is false for at least one member.** `15920699` (Subramanian 2005) **is an EMC-specific human cohort of 10 patients** by committed evidence, recorded as such in three independent places in this tree. It is not a mouse, a cow or an NSCLC trial.
- **Wrong, 3 — "zero EMC patients" is unestablished for two members.** `30511879` (AVERT) and `30786186` (CASSINI) are **mixed-tumour-type ambulatory-cancer trials**, not NSCLC; no committed artifact states their histology composition. W07e:177's parenthetical *"(zero EMC patients)"* is an assumption for those two, not a fact. The *classification* (`NO-AE-DATA for EMC`) survives anyway, because a mixed-cancer trial with no histology axis cannot supply an EMC-specific denominator whatever its composition — but the reason on the record is not the reason that holds.

**Counts, stated plainly.** Of the 14: **13 are structurally incapable** of being or containing an EMC-specific human cohort that could enter the support set. **1 is not** — `15920699`, an EMC-specific human cohort of 10, whose adverse-event content is **UNKNOWN, not zero** (never retrieved, abstract-only elsewhere in the tree, and no committed field mentions treatment or toxicity). Within the 13, one further row (`36316541`, Bangerter) is **human EMC patient-derived material** — two patient-derived cell models — rather than a non-EMC model; it cannot yield a patient adverse-event denominator because nothing was administered to a human, but describing it as a mouse-study-class record is wrong.

### 5.2 Provenance of every one of the 14, with the field quoted

**All 14 trace to exactly one file, `systems/graph/evidence.json`, and to one of two prose fields in it — `citation` or `what_it_supports`.** None traces to a registry row (`grep -c` on `research/data/emc-clinical-registry.json` → **0** for all 14) and none to a title alone. This sharpens W07g's "an annotation, a registry field, or a title" to: **an annotation, and only an annotation.** Note the structural fact underneath: `evidence.json` records carry `id`, `canonical`, `citation`, `what_it_supports`, `aliases`, `misattributed_as`, `provenance_flag`, `cited_in` — **there is no cohort-composition field in the schema at all**. Composition was read out of prose written to record what a *route* rests on, not who was in a study.

Column key: **CAPABLE?** = could this be, or contain, an EMC-specific human cohort that an adverse-event statement could attach to? All rows `PRIMARY` as statements about repository text at `ff6bb018`; the underlying study content is `SECONDARY` (an annotation's report of a source) except where noted.

| # | PMID | evidence.json id | Field the classification came from | What it **establishes** | What it does **not** establish | CAPABLE? |
|---|---|---|---|---|---|---|
| 1 | 20818875 | EV-TEMEL-2010 | `what_it_supports` (`:595`): *"Newly diagnosed metastatic NSCLC (n=151), randomized to early palliative care integrated with standard oncologic care vs standard care alone."* | Disease is metastatic NSCLC; n=151; a randomised trial | Nothing about sarcoma; the record has no histology axis | **No** — NSCLC excludes EMC |
| 2 | 38558247 | EV-PACO-2024 | `what_it_supports` (`:616`): *"Advanced NSCLC (n=146), EPC vs standard oncologic care (SOC), primary endpoint overall survival."* | Advanced NSCLC; n=146 | Same | **No** |
| 3 | 37781179 | EV-CHEN-2023-CEPC | `what_it_supports` (`:637`): *"NSCLC (n=140), combined early palliative care (CEPC…) vs standard care (SC), primary endpoint overall survival."* | NSCLC; n=140 | Same | **No** |
| 4 | 32953543 | EV-KOCHOVSKA-2020 | `citation` (`:657`): *"…Earlier multidisciplinary palliative care intervention for people with lung cancer: **a systematic review and meta-analysis**…"*; `what_it_supports` (`:658`): *"…one in a mixed advanced-cancer population comparing EARLY (30-60 days) vs DELAYED (3 months) palliative care referral"* | A **secondary synthesis** in lung cancer, whose evidence base includes **one mixed advanced-cancer study** | That it is an NSCLC *trial* — it is **neither a trial nor NSCLC-restricted**, so W07e:177's *"all NSCLC"* misdescribes this row; and it does not state the mixed study's histology composition | **No** — a lung-cancer synthesis; the one mixed study is not EMC-specific and no EMC arm is named |
| 5 | 30511879 | EV-CARRIER-2019 | `what_it_supports` (`:534`): *"The AVERT trial (**ambulatory cancer**, Khorana score ≥2, apixaban vs placebo, n=563 modified ITT)…"* | A **mixed-tumour-type** ambulatory-cancer VTE-prophylaxis RCT; n=563 mITT; event rates and major bleeding | **Tumour-type composition is not stated.** "Zero EMC patients" is **not** established — that is W07e's assumption | **No** — no histology axis; cannot yield an EMC-specific denominator whatever the composition |
| 6 | 30786186 | EV-KHORANA-2019 | `what_it_supports` (`:554`): *"The CASSINI trial (**ambulatory cancer**, Khorana score ≥2, rivaroxaban vs placebo, n=841 randomized)…"* | Mixed-cancer RCT; n=841 | Same — histology composition unstated | **No**, same reason |
| 7 | 31417269 | EV-SONG-2019 | `citation` (`:574`): *"…**Direct oral anticoagulants for treatment and prevention of venous thromboembolism in cancer patients.**…"*; `what_it_supports` (`:575`) describes it summarising AVERT and CASSINI | A **review**, i.e. secondary literature with **no primary cohort of its own** | Any cohort it could contribute | **No** — a review has no denominator |
| 8 | 12709428 | EV-WANSA-2003 | `what_it_supports` (`:125`): *"NOR-1's AF-1 is delimited to residues 1–112 and SRC-2 modulates AF-1 but not the LBD…"* | Molecular/biochemical domain mapping | **No study population is stated anywhere in the record** — "no patients" is an inference from the described content, defensible but not a quoted fact | **No** — protein-domain biochemistry |
| 9 | **15920699** | EV-SUBRAMANIAN-2005 | `what_it_supports` (`:405`): *"**The independent EMC cohort (10 EMCs)** showing PPARG over-expression relative to other sarcomas — one of the two concordant abundance cohorts."* | **An EMC-specific human tumour cohort, n=10.** Corroborated at `research/manuscripts/repurposing/pparg-direction-emc.md:132` (*"10 EMCs vs 26 other sarcomas, 42,000-spot cDNA microarrays"*, *"abstract retrieved; not open access"*) and `reports/W05-patient-independence-audit.md:135` (GSE4303, *"10 EMC arrays"*, *"one of 'three independent EMC cohorts'"*, count tier A, PRIMARY) | Any treatment, exposure or adverse-event content. Its AE content has **never been checked**; the abstract was retrieved for PPARG, not for harms | **YES** — it is an EMC-specific human cohort. Its exclusion from the support set rests on an unchecked assumption, not on structure |
| 10 | 35704774 | EV-ZAIENNE-2022 | `what_it_supports` (`:10`): *"LBD-borne functional modulation of NOR-1/NR4A3; the **Gal4-NOR-1-LBD reporter construct** (which is itself AF-1-less); the absent paralogue counter-screen…"* | A cell-based reporter/medicinal-chemistry study | No population stated; "no patients" is inference | **No** — reporter-assay chemistry |
| 11 | 36316541 | EV-BANGERTER-2023 | `citation` (`:377`): *"…ex-vivo drug sensitivity in **patient-derived EMC models USZ20-EMC1 and USZ22-EMC2**"*; `what_it_supports` (`:378`): *"the 40-drug panel (17 chemotherapies + 23 targeted agents) was screened on USZ20-EMC1 ALONE…"* | **Ex vivo** drug sensitivity in **two EMC-patient-derived models**; drugs applied to cells, not to people | No human administration, no clinical exposure, no patient outcome | **No** — human-derived but not a human cohort; nothing was given to a patient, so no AE denominator exists. **But it is EMC and patient-derived**, so the "mouse/cow" framing misdescribes it |
| 12 | 36636023 | EV-HIGUCHI-2023 | `what_it_supports` (`:427`): *"…it uses **H-EMC-SS** (OBJ-LINE-HEMCSS), **identity disputed** — the curated record does not support its EMC identity. ⚠ Whether the **MOUSE** experiment used that line is **UNREAD** — not open access, full text not retrieved."* | A cell-line + mouse functional experiment; the line's EMC identity is **disputed in this repository's own record** | Whether the mouse work used that line — the record says **UNREAD** | **No** — mouse/cell-line, no patients |
| 13 | 37205599 | EV-FET-ATR-2023 | `citation` (`:146`): *"FET fusion oncoproteins impair ATM activation at double-strand breaks through their shared N-terminal IDR, leaving the ATR axis load-bearing."* (`canonical.doi` `:144` = `10.1101/2023.04.30.538578`, a preprint DOI) | Molecular DNA-damage-response mechanism | No population stated; no model system named in the record | **No** — molecular mechanism |
| 14 | 8961274 | EV-ZETTERSTROM-1996 | `what_it_supports` (`:104`): *"NR4A3/NOR-1 does not heterodimerise with RXR, unlike NR4A1 and NR4A2 — the verbatim basis on which the RXR-heterodimer route is closed."* | Receptor-dimerisation biochemistry | No population stated | **No** — biochemistry |

**Tally: CAPABLE = 1 (`15920699`) · NOT CAPABLE = 13.** Sub-note within the 13: 1 human-patient-derived-ex-vivo (`36316541`), 1 mouse/disputed-line (`36636023`), 4 pure molecular (`12709428`, `35704774`, `37205599`, `8961274`), 3 NSCLC RCTs (`20818875`, `38558247`, `37781179`), 1 lung-cancer meta-analysis (`32953543`), 2 mixed-cancer VTE RCTs (`30511879`, `30786186`), 1 review (`31417269`).

### 5.3 Is W07g's low-risk judgement correct?

**Yes as to consequence, no as to reasoning.** Restated precisely, and separating the two questions W07g's sentence merged:

1. **Can any of the 14 supply an EMC-specific adverse-event denominator on committed evidence?** **No — 14 of 14.** No committed field for any of the 14 contains an adverse-event, toxicity, harm, grade or discontinuation statement. This is what makes the class low-risk, and it holds for `15920699` too.
2. **Is any of the 14 structurally incapable of being an EMC-specific human cohort?** **13 of 14, not 14 of 14.** `15920699` is one — 10 human EMC tumours, corroborated in three places. Its non-membership in the support set follows from the absence of any AE content in what has been read of it, which is an **unchecked** state (UNKNOWN), not from its structure.

The practical difference is small but real and it is the difference the `ASSUMED` tier was created to expose: for 13 rows a future worker can stop, because no retrieval could change the answer; for `15920699` a future worker cannot, because a retrieval could in principle find a treatment/toxicity sentence in a 2005 expression-profiling paper on 10 EMC patients. I assign that **low prior and no probability estimate** — an archival microarray profiling study is an unlikely place for a harm denominator — and I record it as **UNKNOWN, not zero**, which is exactly the standard W07g applied and exactly the standard its blanket wording then undercut.

### 5.4 One further provenance observation, recorded because it bears on the tier's name

Five of the 14 carry a `provenance_flag` asserting the full text was read and cached: `38558247` (`:619`, *"Open access; full text read directly"*, `literature/early-palliative-care-survival-rct/PMC11449095.txt`), `37781179` (`:640`), `32953543` (`:661`), `31417269` (`:578`, `literature/vte-prophylaxis-ambulatory-cancer-survival/PMC6593743.txt`), and `36316541` (`:384`, `literature/bangerter-2023-emc-exvivo/PMC9813045.txt`). **None of those cache files is in this checkout**: `git ls-files | grep -i "literature-cache|early-palliative-care-survival-rct|vte-prophylaxis-ambulatory|bangerter-2023"` returns **no output**, and the frozen corpus's `research/literature/` listing contains no matching directory either. Two more (`20818875:598`, `30511879:537`, `30786186:557`) state abstract-only retrieval by design.

**What this means and does not mean.** It does **not** mean the retrievals did not happen — the flags name workflow run IDs (`33821316750`, `33823172816`) and a publication target outside this tree, and absence from this checkout is **UNKNOWN, not proof of absence** (`CORPUS-CONTEXT.md`, `snapshot-provenance.json`). It does mean that **`ASSUMED` is the right tier name for all 14 as read from this tree**: the composition statements are annotations, and the material that would upgrade five of them to full-text-established is not here to be checked. That is a route fact, not a literature fact.

### 5.5 Independent recomputation of W07e §5.5 — W07g's arithmetic finding is **CONFIRMED**

Recomputed from the named lists, not from W07g's assertion. Inputs, quoted at `ff6bb018`:

- `W07d:170` — *"**Tally over the full 26-paper union** (W07b's nine, unchanged by me, plus these 17): `EMC-SPECIFIC` **7** (graded/counted **1**, narrative **6**) · `MIXED-ARM-ONLY` **6** · `NO-AE-DATA` **12** · `UNRECOVERED` **1**."* → 7+6+12+1 = **26** ✓.
- `W07e:188` — *"**Tally over the 31 Axis-R additions:** `EMC-SPECIFIC` **1** … · `MIXED-ARM-ONLY` **1** · `NO-AE-DATA` **27** · `UNKNOWN/unrecovered` **2**."* → 1+1+27+2 = **31** ✓.
- `W07e:203` — narrative-and-ungraded cell says **8**, and names *"41476450, 41323055, 35494187, 23058004, 30534357, 21547635 (W07d's seven, minus 31331701) + 24345066 (Axis R, retained strength)"*.
- `W07e:205` — no-AE cell says **38**, and names *"12 from W07d's union + 27 Axis-R"*.

| Cell | Stated | Recomputed from the named lists | Verdict |
|---|---|---|---|
| Graded, counted, EMC-specific | 1 | union 1 (`31331701`) + Axis-R 0 = **1** | ✓ |
| Narrative, ungraded, EMC-specific | **8** | union 7 − 1 graded = 6 named PMIDs (`41476450, 41323055, 35494187, 23058004, 30534357, 21547635`) + Axis-R 1 (`24345066`) = **7** | ✗ **overstated by 1** |
| Mixed denominator | 7 | union 6 + Axis-R 1 (`33203665`) = **7** | ✓ |
| No AE bearing on EMC | **38** | union 12 + Axis-R 27 = **39** | ✗ **understated by 1** |
| UNKNOWN / unrecovered | 3 | union 1 (`28187993`) + Axis-R 2 (`24703573`, `35144048`) = **3** | ✓ |
| **Total** | **57** | 1 + 7 + 7 + 39 + 3 = **57** | ✓ **correct** |

**Confirmed exactly as W07g reported: narrative 8 → 7, no-AE 38 → 39, the two errors cancel, and the total 57 is right.** Both stated and corrected column sums equal 57 (1+8+7+38+3 = 57; 1+7+7+39+3 = 57), so no downstream figure in W07e depends on either cell. Independent cross-check: the two cells' correction is forced by W07d:170 and W07e:188 alone, without touching W07g. Grade: **PRIMARY** as a statement about repository text at `ff6bb018`.

Consistency check on the 27 that carries the 14: Axis-R `NO-AE-DATA` 27 = Group I 10 (`W07e:154-163`) + Group II's 2 no-AE-for-EMC (`15739208`, `40941020`, `W07e:171,173`) + Group III's 1 retrieved (`42660639`, `W07e:176`) + Group III's **14** unretrieved (`W07e:177-178`) = **27** ✓. **The 14 audited here are exactly the 14 in that decomposition** — 4 palliative + 3 VTE + 7 preclinical/molecular.

### 5.6 No clinical claim

Nothing here bears on the safety, tolerability, efficacy, prognosis, therapeutic window or clinical readiness of any agent, procedure or care model — palliative care, apixaban, rivaroxaban, carfilzomib, doxorubicin, venetoclax, a PPARγ agonist or inhibitor, or anything else — for any patient. There is no wet lab. This is bookkeeping about what fields in one JSON file state. **I pooled nothing, computed no rate, derived no denominator from any percentage, imputed nothing, and substituted no cohort n.** The survival and event-rate figures quoted above appear only as verbatim evidence of what a record's *population* field says, and I make no transfer of any of them to EMC — `EV-TEMEL-2010:595` states that transfer question itself: *"any application to EMC is a TRANSFER, not a direct finding."*

## Validation evidence

**RUN.** All commands read-only, in `/home/user/Rare-cancers`, exit 0 unless noted. No network of any kind.

- **V1 — start state.** `date -u` → `Tue Sep  8 03:21:23 UTC 2026`; `git rev-parse HEAD` → `e2214d4f2145c138da44b11c3d59899a5349abfb`; `git status --porcelain | head -50` → **no output**; `env | grep …` output pasted verbatim in §Worker.
- **V2 — the 14 located, and the registry negative control.** `for p in 20818875 38558247 37781179 32953543 30511879 30786186 31417269 12709428 15920699 35704774 36316541 36636023 37205599 8961274; do grep -rn "$p" systems/graph/*.json | head -5; done` → every PMID found in `systems/graph/evidence.json`; and `grep -c "$p" research/data/emc-clinical-registry.json` → verbatim, all fourteen lines:
  ```
  20818875 registry_hits=0
  38558247 registry_hits=0
  37781179 registry_hits=0
  32953543 registry_hits=0
  30511879 registry_hits=0
  30786186 registry_hits=0
  31417269 registry_hits=0
  12709428 registry_hits=0
  15920699 registry_hits=0
  35704774 registry_hits=0
  36316541 registry_hits=0
  36636023 registry_hits=0
  37205599 registry_hits=0
  8961274 registry_hits=0
  ```
  **Zero registry provenance for all 14** — the classification source is `evidence.json` alone.
- **V3 — field extraction.** `awk 'NR>=a && NR<=b {printf "%d: %s\n", NR, $0}' systems/graph/evidence.json` over line ranges 1–22, 95–170, 360–440, 520–675. Every quotation in §5.2 is verbatim from that output at the stated line.
- **V4 — the exemplar check.** `grep -rn -i "parachordoma"` → `W07d:160` (`21922364`, *"presacral **parachordoma** case report"*, *"**0 — EMC appears only in a differential-diagnosis list**"*) and `W07d:186,195,336`; `grep -rn -i "\bcow\b|bovine"` → `W07d:165` (`15980139`, *"Vet Rec — 'Extraskeletal myxoid chondrosarcoma in a cow.'"*, *"**0 human patients (bovine)**"*). **Neither PMID appears in W07g's 14-member list at `W07g:161`.**
- **V5 — end state and stability of every cited line.** `date -u` → `Tue Sep  8 03:24:47 UTC 2026`; `git rev-parse HEAD` → `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f`; `git status --porcelain` → **no output**; `ls -la /tmp/claude-0/w07h/` → `.` and `..` only. `git diff --name-only e2214d4f ff6bb018` → 8 files, all other lanes' `reports/W*.md`. `git show ff6bb018:systems/graph/evidence.json | awk 'NR==401||NR==405||NR==427||NR==534||NR==657||NR==658'` reproduced the same text I cite; `git show ff6bb018:…/W07e-….md | awk 'NR==203||NR==205'` reproduced the **8** and **38** cells verbatim. **All `file:line` references valid at the end HEAD.**

**PROPOSED (NOT RUN).**
- **Retrieval of `15920699`'s full text or abstract to settle its AE content.** Not attempted — my dispatch forbids network and retrieval, and W07g already ran the PubMed route for lane 7. Consequence: the one CAPABLE row of the 14 stays **UNKNOWN**.
- **Any denied route.** `31331701`, `24703573`, `35144048`, `32856598`, `24345066` and the trabectedin/RT DOI were not attempted, probed, rephrased or rerouted. Nothing new is asserted about any of them.
- **Locating the five cached full texts named in `provenance_flag` fields.** They are not in this checkout (§5.4); finding them is a branch/store question, not a literature question, and I did not pursue it.
- **Adjudication of W07g's §5.4 rubric question.** Deliberately not performed. It is an acceptance criterion and no worker may author it. Nothing in this report presupposes either answer.

**Refusals encountered: none.** No branch refused, no denied route replayed, nothing rephrased or rerouted.

## Limitations

1. **This is an audit of annotations, not of sources.** Every "establishes" in §5.2 means *this repository's `evidence.json` field says so*. I read none of the 14 papers. Where a field's content is itself wrong, my audit inherits the error — and for five of the 14 the material that would check it is not in this tree (§5.4).
2. **"Structurally incapable" is a judgement about study *type* from a one-sentence description.** For four rows (`12709428`, `35704774`, `37205599`, `8961274`) the record states **no population at all**; I classify them as patient-free from the molecular content described. That is an inference, clearly labelled, not a quotation.
3. **The two mixed-cancer VTE trials could in principle have enrolled an EMC patient.** I state that this is **UNKNOWN**, and that it does not matter for the support set because neither trial has a histology axis. Anyone wanting to say "no EMC patient was in AVERT or CASSINI" must retrieve those trials; the repository does not support that sentence today.
4. **`15920699`'s AE content is UNKNOWN, and I did not estimate how likely a harm sentence is.** Low prior, no number, no probability claim.
5. **The arithmetic recomputation is about repository text, not about the world.** It confirms two transcription cells; it does not revalidate the classifications those cells count, and it changes no downstream number.
6. **HEAD moved under me** (`e2214d4f` → `ff6bb018`, other lanes' report collection). I verified every cited line at the end HEAD; I did not re-verify lines I read but do not cite.
7. **Nothing clinical.** No efficacy, safety, tolerability, prognosis or clinical-recommendation claim is made or is available to me.

## Stop condition

**Set at the outset:** return as soon as (a) each of the 14 `ASSUMED` rows has its classifying artifact **and field** identified and quoted verbatim with `file:line`, with what it does and does not establish stated separately; (b) each of the 14 is answered CAPABLE / NOT CAPABLE against the question "could this be, or contain, an EMC-specific human cohort a composition error would move into the support set", with the count reported both ways; (c) W07e §5.5's five cells are recomputed independently from the named lists in W07d and W07e and the recomputation is reported as confirming or correcting W07g; or ~40 tool calls / ~40 minutes, whichever comes first.

**Status: MET on all three, well inside budget.** (a) §5.2, 14/14, all from `systems/graph/evidence.json` and no other artifact (V2). (b) §5.2–§5.3 — **13 NOT CAPABLE, 1 CAPABLE (`15920699`)**; W07g's low-risk conclusion holds, its stated ground does not, in three named ways. (c) §5.5 — **CONFIRMED independently**: narrative 8 → 7, no-AE 38 → 39, errors cancel, total 57 correct.

## Tool-call and wall-clock count actually used

**Tool calls: 17**, all Bash, all read-only, **zero MCP / network calls, $0**. **Wall clock: ~3.5 minutes** (03:21:23 → 03:24:47 UTC), plus report drafting. Far inside the ~40-call / ~40-minute target; returned on stop-condition satisfaction, no padding. What made it cheap: the `for p in …; do grep` loop resolved all 14 provenances in one call, and the registry negative control in a second.

## Next concrete action

**Amend `W07g:161` and `W07e:177-178` together in one edit, since they are the same defect at two removes.** Specifically: (i) strike the cow and parachordoma from W07g's `ASSUMED`-class illustration — they are `15980139` and `21922364`, W07d `ABSTRACT-ONLY` rows, not members; (ii) replace W07g's blanket *"structurally incapable"* with **13 of 14 structurally incapable, 1 CAPABLE (`15920699`, an EMC-specific human cohort of 10, AE content UNKNOWN and unchecked)**; (iii) strike *"(zero EMC patients)"* from W07e:177 for `30511879` and `30786186` and replace it with *"mixed-tumour-type ambulatory-cancer trials; histology composition not stated in any committed artifact; no EMC-specific denominator recoverable"*; (iv) correct W07e:177's *"all NSCLC"* — `32953543` is a lung-cancer **systematic review and meta-analysis**, not an NSCLC trial; (v) note that `36316541` is EMC **patient-derived** ex-vivo material, not a non-EMC model; and (vi) record that all 14 trace to `systems/graph/evidence.json` prose alone — **zero registry provenance** — and that the file's schema has no composition field, which is why the tier exists. Apply W07g's already-identified §5.5 cell corrections (8→7, 38→39, total 57 unchanged) in the same edit. This is a documentation repair by the coordinator or lane owner; **it moves no count and needs no rubric ruling**, and it should not be bundled with the still-open §5.4 acceptance-criterion question, which remains for the lane owner alone.

**Explicitly not successors:** (a) any retrieval of `15920699` by a worker without a network grant — it is the only one of the 14 where a retrieval could matter, and it belongs wherever retrieval is authorised, scoped to one question (does the paper report any treatment or adverse event over its 10 EMC patients?); (b) re-checking the other 13 — no retrieval can change their answer, and doing so would spend calls to confirm a structural fact; (c) locating the five absent literature-cache files, which is a route/branch question, not a lane-7 question; (d) any attempt on the six CLOSED-WORK denied routes, none of which is in this class.
