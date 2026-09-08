<!-- collected 2026-09-08T04:49:12Z by campaign coordinator; agent id a2fc1a2e4ce995e4e; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a2fc1a2e4ce995e4e.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted; report follows.

## Worker

**W53**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: evidence-contract enforcement — W30d's named successor, applied to `research/meta/meta-analysis.mjs` (the manuscript's actual pooler) rather than to the registry validator.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in the environment corroborates it — no variable names a model. The coordinator must extract the served model from the transcript.

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

**Start** — `date -u` → `Tue Sep  8 04:41:55 UTC 2026`; `git rev-parse HEAD` → `7a1002679e0830fb19bed48660772cdcc91c495d`; `git status --porcelain` → **empty**.
**End** — `date -u` → `Tue Sep  8 04:44:42 UTC 2026`; `git rev-parse HEAD` → `fb1a3f8040537234010114053b36ec55b729c65e` (**HEAD advanced under me twice**, coordinator collecting reports — an intermediate read at `3e286595` showed one untracked coordinator report `W02k-e2-limb-calibration.md`, not mine); `git status --porcelain` → **empty** at end.

**Read integrity across the HEAD move:** `git diff --stat 7a100267 3e286595 -- research/meta research/data systems/POLICY-evidence.md` → **empty output, exit 0**. End-state hashes of the two load-bearing inputs are byte-identical to what I read: `research/meta/results.json` = `e696abacff88a407bc696d6b6966e2efefe6c08af5fc8ae6b974da42146c8acd`, `research/data/emc-clinical-registry.json` = `6f3b31b352c29592a4657d64aff872a93cf65f280837096008e59ab82e502bdd`.

**Write isolation honoured.** Zero repository writes, zero git write operations, no network, no MCP call, no retrieval, no `preflight.sh`, no generator run in the live tree. `meta-analysis.mjs` was executed **only** inside `/tmp/claude-0/w53/scratch/repo/` (a `cp -a` of `research/meta` and `research/data` into a mirrored tree, which is what the module's `root = <dir>/../..` resolution needs). `git status --porcelain` in the live tree immediately after the first scratch run printed only the coordinator's own untracked file and is empty now. **Scratch deleted** — `rm -rf /tmp/claude-0/w53`; `ls /tmp/claude-0/w53` → `No such file or directory`. **I authored no repair, no patch, no gate and no test, and edited no file in the repository.**

## Question

Audit `research/meta/meta-analysis.mjs` **per requirement sentence** against `systems/POLICY-evidence.md` §2.1(3) (outcome ≠ inclusion criterion), §2.2 (pooling / Wilson arithmetic) and §2.4 (time-anchored survival never merged): what implements each sentence, at which `file:line`, and is it EXACT / WEAKER-THAN-TEXT / STRONGER-THAN-TEXT / NOT-IMPLEMENTED. Then verify the arithmetic independently in Python from the committed registry and compare to what the module produces.

Open because W30c measured that **no gate, test or workflow runs this module**, and W30d's systematic pass covered the *validator*, explicitly recording §2.2 as "out-of-artifact (correctly not this script's job)". Nobody has audited the pooler itself, and nobody has recomputed its published numbers from an independent implementation.

## Prior-work check

```
$ grep -rn -i -E "wilson|1\.959|crude|denominator-weighted|fiveYear|dssText|otherCauseDeath|integer|contextReason|populationKey|stratum|criteria" research/meta/meta-analysis.mjs
36:    if (k === "metastasis" && (c.criteria || {}).stage === "distant") continue; // baseline, not outcome
   (single hit — no "wilson", no "crude", no time-anchored field name anywhere in the module)

$ grep -rln "meta/results.json\|meta-analysis.mjs" --include='*.py' --include='*.mjs' --include='*.sh' --include='*.yml' . | grep -v opus-capacity-campaign
   research/modalities/emc_locoregional_eligibility.py
   research/modalities/emc_rt_bed_reappraisal.py
   research/manuscripts/emc_fusion_partner_pooling.py
   research/meta/meta-analysis.mjs
   scripts/validate-registry.mjs
```

Read in full before working: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `systems/POLICY-evidence.md` (386 l), `reports/W30c-policy-sections-without-gates.md`, `reports/W30d-validator-vs-policy-divergence.md`, and the module itself (105 l).

**Confirmed not replayed.** W30d's 34-row validator audit and its registry shape census — taken as given per the brief, not re-derived, and `validate-registry.mjs` not re-audited. W30c's 16-unit enforcement map — I cite its "no gate runs the pooler" finding rather than re-measuring it. The 0-of-89 backlog — untouched. **W25 not read, not referenced.** W30c did recompute the pooler's *study-level (events, denom) inputs* and matched 9/9 rows; I extend past that to the **estimates, intervals, weights, heterogeneity statistics, leave-one-out ranges and sensitivity subsets**, which no worker has recomputed.

## Method and inputs

- **Requirement source:** `systems/POLICY-evidence.md` @ `7a100267` (identical at `fb1a3f80`), lines 121–130 (the two-methods callout), 132–146 (§2.1), 148–162 (§2.2), 178–186 (§2.4).
- **Implementation source:** `research/meta/meta-analysis.mjs`, all 105 lines.
- **Data source:** `research/data/emc-clinical-registry.json` — 14 cohorts, 5 `pool:true`, grouped by `sourceId` into **4 studies**.
- **Write-behaviour read from source before running:** the module's only `node:fs` write is `writeFileSync` at `:101`, targeting `results.json` in its own directory. It therefore **cannot** be run write-free, which is why every execution was in the scratch copy.
- **Independent implementation:** `/tmp/claude-0/w53/scratch/recompute.py`, Python 3 stdlib only (`math`), written from the policy text and the algorithm description, not by transliterating the JS — it re-derives study grouping, the logit transform with 0.5 continuity correction, DerSimonian–Laird τ²/I²/Q, random-effects weights, leave-one-out, the three sensitivity subsets, **and** the §2.2 crude denominator-weighted pool with Wilson score intervals (which the module does not compute).
- **Mutation probes:** five, each applied to a **fresh** copy of the committed registry inside the scratch tree (no compounding), then the committed file restored and re-hashed.
- Tools: `node` (repo default), system `python3`, `git`, `grep`, `sha256sum`. No third-party packages, no network.

## Result

### A. Divergence table — per requirement sentence

Legend as W30d's: **EXACT** = code and text coincide; **WEAKER** = the artifact can violate the text and still be pooled; **STRONGER** = the code does more than the text says (or contradicts a text disclaimer); **NOT-IMPL** = no implementation in this module. "Exploited?" is measured against the committed registry.

| # | § | Policy sentence (quoted) | Implementation (`meta-analysis.mjs:line`) | Class | Exploited? |
|---|---|---|---|---|---|
| M1 | 2.1 lead-in | "A cohort is summed into the headline only if **all** hold" | `:32 data.registry.cohorts.filter((c) => c.pool !== false)` — admission is delegated wholly to one boolean, and the test is **not** `c.pool === true` | **WEAKER** | **No** — 14/14 cohorts carry an explicit `pool`. Probe **P3** (a `pool:false` context cohort with its `pool` key *deleted* and counts added) → the cohort **enters the pool**: recurrence k=4→5, 27.8%→27.2%, and the "older/undated" sensitivity arm k=2→3. A cohort added with no `pool` field is pooled by default. Latent. |
| M2 | 2.1(1) | "**Confirmed EMC** (molecular/histological), matching the page." | none — `criteria` is read only for the one `stage` test at `:36` | **NOT-IMPL** | n/a (undecidable from the file) |
| M3 | 2.1(2) | "**Explicit integer counts** are reported: `{events, denom}`." | `:38 if (mm && mm.denom)` — presence-of-denominator only; no type test, no integer test, no `events ≤ denom` test | **WEAKER** | **No** — 0 of 12 metric blocks non-integer (W30d, taken as given). Probe **P4** (`events: 3.5` on the largest cohort) → **runs clean, exit 0**, recurrence 27.8%→**22.0%**, registry-only arm 11.9%→**2.6%**. The validator's `typeof === "number"` (W30d R12) is the only upstream barrier and it also admits `3.5`, so the two weaknesses compose: a back-derived fractional count reaches the published pooled estimate through both. |
| M4 | 2.1(2) | "We **never derive counts from a published percentage** for pooling." | none | **NOT-IMPL** | **No** — all `*Pct`/`*Text`-only cohorts are `pool:false` by authorship |
| **M5** | **2.1(3)** | **"The outcome is a true outcome, not the inclusion criterion — e.g. a 'metastatic at diagnosis' cohort does not contribute to the metastasis rate (its metastasis count is structurally 100%)."** | **`:36 if (k === "metastasis" && (c.criteria \|\| {}).stage === "distant") continue;`** | **WEAKER** | **No.** The guard **does fire**: probe **P1** gives cohort[1] (`criteria.stage:"distant"`) an explicit `metastasis: {29,29}` and the metastasis pool is **unchanged** (37.9%, k=3) — the exact case W30d measured the *validator* would admit (its M11). But the guard is **one string literal against one field for one metric, with no vocabulary check**: probe **P2** respells the same cohort's `criteria.stage` as `"metastatic"` and the structurally-100% row **enters the pool** — metastasis **37.9% → 42.7%**, CI 27.5–49.6% → 37.1–48.5%, **I² 69% → 0%**, τ² 0.122 → 0.000. Heterogeneity collapses to zero precisely *because* the admitted row is definitionally 100%. Registry vocabulary today is `{localized, distant}` only, so this is **latent**. Symmetrically, no analogous guard exists for `recurrence` or `diseaseDeath` — a cohort selected on recurrent disease would contribute to the recurrence rate unchecked. |
| M6 | 2.1(4) | "**Non-overlapping population** (see 2.3)." | none in this module; `populationKey`/`stratum` are never read. Grouping by `sourceId` at `:33` merges a study's strata so a registry counts once, which is §2.3's *within-study* intent but is not a check | **NOT-IMPL** (partially satisfied structurally) | **No** |
| M7 | 2.2 | "**Pooled proportion** p̂ = (Σ eventsᵢ)/(Σ denomᵢ). This is a denominator-weighted ('fixed-effect'-style) crude pool." | **not this method.** `:50-59 dl()` is inverse-variance **random-effects** on logits with τ² added to each variance | **NOT-IMPL — by explicit carve-out** (policy `:121-130` names DL in this file as the manuscript's method and binds only §2.1 and §2.3 to both) | n/a. Quantified below: the two methods give materially different headlines. |
| M8 | 2.2 | "Disclose when one study dominates (currently a single national registry does)." | `:59 weights`, `:65`, `:85` — per-study `weight` is emitted into `results.json`; **no dominance statement is produced**, and DL's τ²-inflated weights are far flatter than the crude denominator weights the sentence is about | **WEAKER** | **No** (weights are published; the *disclosure* is left to the manuscript, which this module does not check) |
| **M9** | **2.2** | **"**95% confidence interval**: the **Wilson score interval** on (Σevents, Σdenom)."** | **none.** `grep -i wilson` on the module → **0 hits**. Per-study intervals at `:48` are logit-Wald (`expit(y ± 1.96√v)`); the pooled interval at `:59` is logit-Wald on the DL mean | **NOT-IMPL** (carved out with M7, but the *substituted* interval is neither Wilson nor on (Σe, Σd)) | n/a — quantified in §B |
| M10 | 2.2 | "Wilson is used because it behaves well at small n and near 0%/100%" | the module's substitute for that role is the **0.5 continuity correction** at `:46`, applied only when `e===0` or `e===n` | **WEAKER-THAN-TEXT in kind** (a different, cruder small-n device) | **No** — no 0% or 100% cell in the pooled set today, so `:46` never fires |
| M11 | 2.2 | "the per-cohort rates are shown side-by-side and the breakdown reports their **range**" | `:85` emits per-study `p` and `ci` (side-by-side: satisfied). **The range is never computed**; `looRange` `:68-73` is a *leave-one-out pooled* range, a different quantity | **WEAKER** | **No** — a consumer can compute the range from the emitted rows |
| **M12** | **2.2** | **"(We do not compute I²; the honest signal is 'look how much the studies disagree.')"** | **`:56` computes I², `:59` publishes it, `:86` prints it.** The module also computes τ² (`:55`) and Q (`:53`) | **STRONGER-THAN-TEXT — a direct contradiction of the policy's own parenthetical** | **YES — live.** `results.json` carries `I2 = 90.37 / 69.12 / 61.55` for the three metrics. Not a data defect: the §2 callout says the manuscript uses DL, and I² is conventional for DL. But §2.2's sentence is unqualified and the callout does not except it, so the contract as written says "we do not compute I²" while the committed artifact publishes three of them. This is the one row where policy text and shipped artifact disagree **today**, not latently. |
| M13 | 2.4 | "**Event-rate metrics** (local recurrence, distant metastasis, disease-specific death)" | `:30 const METRICS = ["recurrence", "metastasis", "diseaseDeath"]` — a whitelist matching the three named endpoints element-for-element | **EXACT** (on the selection clause) | — |
| M14 | 2.4 | "…are pooled as **crude during-follow-up proportions** — labelled 'crude, mixed follow-up'" | pooled by DL random effects, not crude proportions (M7); and the string "crude" appears **nowhere** in the module or in `results.json`'s keys | **NOT-IMPL** (labelling clause) | **UNKNOWN in effect** — whether the manuscript applies the label is outside this module and outside my scope |
| **M15** | **2.4** | **"**Time-anchored survival** (5-yr, 10-yr DSS/OS) is **never merged** into one number — denominators represent different follow-up."** | **implemented by omission**: the `:30` whitelist excludes `fiveYearDSS` and `dssText`, and `:35-39` iterates only `METRICS`, so a time-anchored field is unreachable. No refusal, no error — it is simply never read | **EXACT in effect, but a whitelist rather than a guard** | **No.** Probe **P5** adds `fiveYearDSS: 88.0` to a third pooled cohort → **every output byte-identical**. The prohibition holds today and holds against data changes; it would not survive a code change that added a key to `:30`, and nothing would fail if one did. |
| M16 | 2.4 | "Each cohort's time-anchored figure is shown **per row** in the breakdown instead." | **none.** `:85` emits `label, e, n, p, ci, weight, period` — `fiveYearDSS`/`dssText` are not passed through | **NOT-IMPL** | **No** — 2 `fiveYearDSS` and 8 `dssText` values exist in the registry and reach no row of `results.json` |

**Summary of the three sections asked about.** §2.1(3): **one WEAKER implementation** (M5) that works on the committed data and is bypassable by a synonym. §2.2: **the section is not implemented here at all** (M7, M9, M10) — partly by the policy's own carve-out — with one WEAKER row (M8, M11) and **one live contradiction** (M12, I²). §2.4: the load-bearing prohibition is **effectively EXACT** (M15, probe-confirmed) while both of its companion clauses — the "crude, mixed follow-up" label (M14) and the per-row display (M16) — are **NOT-IMPLEMENTED**.

### B. Arithmetic verification — independent recomputation

`node research/meta/meta-analysis.mjs` inside the scratch copy regenerated `results.json` **byte-identical to the committed file** (`diff` → no output; both sha256 `e696abac…`). So the committed artifact is currently reproducible from the committed registry — a fact nothing in the repository checks.

Independent Python recomputation, all rows **PRIMARY** (computed by me from committed bytes):

| Metric | k | Σevents/Σdenom | **Module (DL logit)** p̂ (95% CI) | **Python (DL logit)** p̂ (95% CI) | I² / τ² module vs python | **§2.2-as-written**: crude pool + **Wilson** |
|---|---|---|---|---|---|---|
| recurrence | 4 | 88/326 | 27.84466% (14.2109–47.3407%) | 27.84466% (14.2109–47.3407%) | 90.366224 / 0.670524 — **identical both** | **26.99% (95% CI 22.46–32.06%)** |
| metastasis | 3 | 94/259 | 37.90353% (27.4802–49.5777%) | 37.90353% (27.4802–49.5777%) | 69.121472 / 0.121785 — **identical both** | **36.29% (95% CI 30.68–42.31%)** |
| diseaseDeath | 2 | 36/262 | 14.18634% (8.5453–22.6298%) | 14.18634% (8.5453–22.6298%) | 61.553963 / 0.104351 — **identical both** | **13.74% (95% CI 10.09–18.44%)** |

Also recomputed and matched: **Q** (31.140439 / 6.476993 / 2.601048), all **9 per-study random-effects weights**, all **9 per-study rates and logit CIs**, both **leave-one-out ranges** (recurrence 22.03–35.87%, metastasis 33.68–44.02%), and all **three sensitivity subsets** (modern k=2 19.367%, 7.215–42.590%; older/undated k=2 38.612%, 21.610–58.934%; registry-only 11.940%, 7.445–18.604%).

```
MAX ABSOLUTE DIVERGENCE across all compared quantities: 1.4210854715202004e-14
```

**Arithmetic verdict: AGREES.** Every quantity the module publishes matches an independent implementation to **1.4×10⁻¹⁴ absolute** — IEEE-754 double roundoff, ~13 orders of magnitude below the module's own 1-decimal-place reporting (`pc1`, `:27`). No divergence at stated precision, and none at any precision the module reports. The study-level inputs I derived independently (masunaga 16/134, 39/134, 18/163; meis 40/83, 35/76, 18/99; ussc 18/60; chiusole 14/49, 20/49) reproduce W30c's 9/9 input match on a later HEAD.

**What the §2.2 column means.** Had §2.2's own arithmetic been applied to the same admitted set, the headline recurrence figure would be **27.0% (22.5–32.1%)** rather than **27.8% (14.2–47.3%)** — the point estimates differ by under a percentage point, but the **interval is 3.3× wider** under DL because τ²=0.67 carries the between-study disagreement that a crude Wilson interval on (88, 326) discards. That is the §2 callout's "different assumptions about between-study heterogeneity" made numerical, and it is the reason the callout says quoting one where the other is meant is a real error. Per-study, the module's logit-Wald intervals sit within **+0.09 to +0.37 percentage points** of the Wilson intervals in width — a negligible difference at these n, so **§2.2's non-implementation costs nothing at the study level and everything at the pooled level.**

**No clinical claim is made or restated here.** These are pooled descriptive proportions from published retrospective series, hypothesis-generating by the contract's own §2 wording; nothing above says any treatment works, is safe, or is ready for a patient. There is no wet lab.

## Validation evidence

**RUN.** Environment: `/home/user/Rare-cancers`, HEAD `7a100267` → `3e286595` → `fb1a3f80` (load-bearing inputs byte-identical throughout, verified by `git diff --stat` and by end-state sha256). `node` (repo default), system `python3` (stdlib only), `git`, `grep`. All execution under `/tmp/claude-0/w53/scratch/` on a `cp -a` copy; deleted.

Scratch construction and identity of the copy:
```
$ cp -a /home/user/Rare-cancers/research/meta  $S/repo/research/meta
$ cp -a /home/user/Rare-cancers/research/data  $S/repo/research/data
$ sha256sum $S/repo/research/meta/results.json /home/user/Rare-cancers/research/meta/results.json
e696abacff88a407bc696d6b6966e2efefe6c08af5fc8ae6b974da42146c8acd  (both)
```

The real run, in scratch only:
```
$ cd $S/repo && node research/meta/meta-analysis.mjs
EMC outcomes meta-analysis (random-effects, logit, DL)

recurrence: pooled 27.8% (95% CI 14.2-47.3%), I²=90%, τ²=0.671, k=4
   leave-one-out pooled range: 22-35.9%
metastasis: pooled 37.9% (95% CI 27.5-49.6%), I²=69%, τ²=0.122, k=3
   leave-one-out pooled range: 33.7-44%
diseaseDeath: pooled 14.2% (95% CI 8.5-22.6%), I²=62%, τ²=0.104, k=2
recurrence (modern, dx mid>=2005, k=2): 19.4% (7.2-42.6%)
recurrence (older/undated, k=2): 38.6% (21.6-58.9%)
recurrence (registry-only): 11.9% (7.4-18.6%)
Results: research/meta/results.json
REAL_EXIT=0

$ diff <committed results.json> research/meta/results.json
IDENTICAL

$ cd /home/user/Rare-cancers && git status --porcelain
?? research/autonomy/opus-capacity-campaign-20260908/reports/W02k-e2-limb-calibration.md   # coordinator's, not mine
```

Mutation probes (verbatim deltas from the P0 baseline reproduced above; each on a fresh registry copy, committed file restored and re-hashed afterwards — `6f3b31b3…` matches):
```
P1  metastatic-at-dx cohort given metastasis {29,29}     → metastasis 37.9% k=3   UNCHANGED  (guard fires)
P2  ...same, criteria.stage respelled "metastatic"       → metastasis 42.7% (37.1-48.5%), I²=0%, τ²=0.000   (guard bypassed)
P3  a pool:false cohort with the `pool` key deleted      → recurrence k=5, 27.2% (15.7-42.9%)               (default-include)
P4  events: 3.5 on cohort[0].recurrence                  → recurrence 22.0% (8.7-45.4%); registry-only 2.6% (0.9-7.2%)
P5  fiveYearDSS added to a third pooled cohort           → every output byte-identical                      (§2.4 holds)
```

End-state hashes and scratch deletion:
```
$ sha256sum research/meta/results.json research/data/emc-clinical-registry.json
e696abacff88a407bc696d6b6966e2efefe6c08af5fc8ae6b974da42146c8acd  research/meta/results.json
6f3b31b352c29592a4657d64aff872a93cf65f280837096008e59ab82e502bdd  research/data/emc-clinical-registry.json
$ git status --porcelain      (empty)
$ rm -rf /tmp/claude-0/w53 && ls /tmp/claude-0/w53
ls: cannot access '/tmp/claude-0/w53': No such file or directory
```

**PROPOSED (NOT RUN).** I ran no pytest suite: nothing in this lane has a suite over `meta-analysis.mjs` (W30c measured zero test modules naming it), and I did not run the opt-in modality tests that cover §2.1(3) at the *policy* level — `research/manuscripts/tests/test_endpoint_logic.py` and the named inclusion-criterion test — because they test other producers, not this module. I assert no pass or fail for any of them. I did not run `scripts/preflight.sh` or `research/modalities/atr_hrd_sarcoma_series.py` in any form.

## Limitations

1. **My Python is an independent implementation of the same specification, not an independent specification.** Agreement to 1.4e-14 proves the JS contains no arithmetic or transcription error relative to textbook DerSimonian–Laird on logits; it cannot prove DL-on-logits is the right estimator for these data, and it explicitly does **not** validate §2.2's method, which the module does not implement.
2. **Every WEAKER row is latent, and latency is a property of today's registry, not of the code.** M1, M3 and M5 are one authoring mistake away from live, and none of them is caught downstream: no gate runs this module (W30c), so a wrong number here would enter the manuscript silently and reproducibly.
3. **I did not audit §2.1(1), §2.1(4)/§2.3 or §2.5–§2.7 against this module** beyond noting the absent implementations; the dispatch scoped me to §2.1(3), §2.2 and §2.4.
4. **The M12 finding is a documentation conflict, not a computation error.** Whether "we do not compute I²" was meant to bind only the crude method is the owner's call; I record that the sentence as written is unqualified and the callout does not except it.
5. **n is small.** 4 studies, 9 study-metric rows, 326 patient-denominators at the largest. A clean arithmetic audit at k=2–4 is a clean audit at k=2–4, and DL's τ² is itself poorly estimated at k=2 (the `diseaseDeath` pool).
6. **No clinical inference.** Nothing here supports any statement about efficacy, safety, selectivity or prognosis, and §2.5's limitations (publication bias, short and mixed follow-up, no censoring, no risk adjustment) apply in full to every number I quoted.
7. **Reproducibility ≠ currency.** I verified `results.json` regenerates from today's registry; I cannot establish it was regenerated after any particular registry edit (W30c's squashed-history limitation stands).

## Stop condition

**Set up front:** produce (a) a per-sentence divergence table for §2.1(3), §2.2 and §2.4 with `file:line` and a class for every sentence, probe-confirming each WEAKER/EXACT claim by execution in scratch rather than by reading, and (b) an independent Python recomputation of every published estimate, interval, weight, heterogeneity statistic, LOO range and sensitivity subset with a stated max-divergence number — then return without repairing anything.

**MET.** 16 requirement rows classified (1 EXACT, 1 EXACT-by-omission, 5 WEAKER, 1 STRONGER/contradictory, 8 NOT-IMPLEMENTED), five mutation probes executed, and 30+ published quantities recomputed with max divergence **1.42e-14**. Arithmetic verdict: **AGREES to stated precision** (and to machine precision). One live policy-vs-artifact contradiction found (M12, I²); everything else latent. No repair authored.

## Tool-call and wall-clock count actually used

**20 tool calls** (all Bash; the first two issued in parallel), of which 2 were the mandated start/end state records. **0** network calls, **0** retrieval calls, **0** MCP calls, **0** repository writes, **0** git write operations, **0** live-tree executions of the pooler. Wall clock **04:41:55Z → 04:44:42Z ≈ 2.8 minutes** of measured tool time plus report drafting. Well inside the ~40/~40 target; returning rather than padding.

## Next concrete action

**One successor for this lane:** determine which of the two pooled headlines — the DL random-effects figure this module writes, or §2.2's crude Wilson figure — the **manuscript actually prints**, and whether `research/manuscripts/pinned-figures.json` pins a value from one method while citing the other's section. My grep for the literal strings `27.8`, `37.9`, `14.2%`, `90.4`, `69.1` in `pinned-figures.json` and `research/manuscripts/*.md` returned **no hits**, which is UNKNOWN (the numbers may be formatted differently or live in a subdirectory I did not walk), not absence. The §2 callout names quoting one method where the other is meant as "a real error", and I have now measured that the two methods differ by **3.3× in interval width** on the recurrence headline — so the question has a concrete consequence and is answerable by reading committed bytes, with no science, no network and no writes. It should be one worker, scoped to *locating and comparing the printed figure*, and explicitly **not** authorized to change the manuscript, the module or the policy.

I propose this; **I have written nothing into the repository, authored no repair, proposed no patch, added no gate row and changed no guard.** W30c's and W30d's open proposals stand unaddressed by me.
