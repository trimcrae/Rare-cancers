<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:16:10Z UTC
     agent id af360f1db7a8e48eb ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-af360f1db7a8e48eb.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

# W02g — Is the EMC fibro/ECM flatness a property of the marker set, or of the cache?

## Worker

- **Worker ID:** W02g (lane 2 refill), OPUS-CAPACITY-CAMPAIGN-20260908. W02f's named successor.
- **Lane:** Lane 2 — EMC microenvironment. Gene-set-matched null on `HHI_gene` for both surviving compartment axes.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I self-report as Claude Opus 5 (`claude-opus-5`), running as Claude Code in the Anthropic Cloud remote container. **This is a self-report and must not be treated as an observed fact.** `env | grep -c '^ANTHROPIC_MODEL='` returned **0** — no such variable exists, so the served model is not confirmable from inside the session. The coordinator must extract the runtime model from the transcript.
- **Write isolation:** READ-ONLY on the Git tree, honoured. All execution under `/tmp/claude-0/w02g/`. **Nothing written, moved or deleted anywhere under `/home/user/Rare-cancers`. No git write operation of any kind.** `scripts/preflight.sh` was not run.

**`date -u` at start:** `Tue Sep  8 03:10:36 UTC 2026`
**`date -u` at end:** `Tue Sep  8 03:12:58 UTC 2026`

**`git rev-parse HEAD` at start:** `98a0833f1ede2cf9cef13790388260567a32e868`
**`git rev-parse HEAD` at end:** `98a0833f1ede2cf9cef13790388260567a32e868` — **unchanged; HEAD did not move under me.**

**`git status --porcelain` at start and at end — byte-identical, eight `??` lines, every one a coordinator-written report file, none a path I touched:**

```
?? research/autonomy/opus-capacity-campaign-20260908/reports/W01g-transcriptome-wide-criterion.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W02f-fibro-ecm-decomposition.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W04e-delay-attribution-route.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W06f-coherent-share-readout.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W07f-emc-only-cohort-full-texts.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W09f-publications-false-absence-audit.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W12e-subprocess-env-residual.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W20g-published-denominator-consistency.md
```

**Input integrity across the run.** `sha256(research/modalities/emc-expression-panels.json)` = `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` at start, again at end, and again **from inside the analysis script at runtime**. It matches the hash named in my dispatch. The input is unchanged.

**Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** (identical at start and end; 51 lines both times):

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

**W02f's null varied specimens with the gene set fixed. Does the EMC fibro/ECM axis's low `R_gene` survive a null that varies the gene set with the specimens fixed?**

W02f resampled six LGFMS specimens and scored them on the **same fourteen fibro/ECM genes**, finding EMC's `R_gene = 2.0460` below the null's 5th percentile (lower-tail p = 0.00000, labelled POST-HOC there). That construction cannot separate two explanations:

- **H-arm** — the EMC arm is unusually flat *across these fourteen genes*;
- **H-set** — *any* fourteen genes of this cache are flat when scored on *these six EMC specimens*.

The complementary null — random same-size panels from the cache, scored on the fixed six EMC specimens — had never been run on a concentration statistic. It is open, and W02f named it as its own successor precisely because running it inside W02f would have let a post-hoc observation borrow a pre-declaration's credibility.

**Substrate limit, stated up front and not as a gap to close:** the only input is the committed **479-gene panel cache** (464 complete-case on GPL6244), **not an expression matrix**. The expression matrices are not committed and fetching them is **denied**. Every quantity below is a statement about `array_percentile` values held in that cache. It is not a measure of collagen, matrix, fibroblasts, vessels, stroma, tumour biology, treatment, or any patient. Arrays and specimens are not patients.

---

## Prior-work check

Commands run against the live checkout at HEAD `98a0833f…`, and against the verified frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/` (base `93b75888…`):

| # | command | result |
|---|---|---|
| 1 | `rg -c 'R_gene' --glob '!.git'` | **exactly one file**: `research/autonomy/opus-capacity-campaign-20260908/reports/W02f-fibro-ecm-decomposition.md` (21 hits). Nowhere else in the tree. |
| 2 | `rg -l 'gene-set-matched\|gene-set matched' --glob '!.git'` | **exactly one file**: the same W02f report — i.e. only the place where this test is *named as not run*. |
| 3 | `grep -rl 'R_gene' /tmp/claude-0/frozen-corpus/extracted/corpus/` | **no output.** The `R_gene` / k-normalised-concentration machinery is absent from the 5,996-file frozen snapshot of base `93b`. |
| 4 | `git ls-files \| rg -i 'w02g\|gene-set-match'` | no output — no tracked file for this work. |
| 5 | `grep -n -i 'random' …/W02c-endothelial-variance-artifact-battery.md` | W02c **did** run a size-matched random-panel null — but on **SD**, not on concentration: *"5,000 random 6-gene panels drawn from the 423 non-marker complete-case panel genes give EMC SD mean 0.0357, p95 0.0717, and P(random 6-gene SD ≥ 0.2001) = 0.0000."* |

**What this establishes.** The random-panel *draw universe* is prior art (W02c's 423 genes; my independently derived universe is also 423, which is a consistency check, not a new fact). The random-panel null **on `HHI_gene`/`R_gene` is new**: no concentration statistic has ever been compared against a gene-set-matched null anywhere in this corpus. I am not replaying W02c's SD null and I make no SD claim.

**Not a replay of anything closed.** Checked against `CLOSED-WORK.md`: I touched none of the clinical registry, PUB-ASO/Qeios frozen deliverables, the NR4A Perspective refusal, Brenca, Hofvander, the paired-Davis negative, the pazopanib/sunitinib/trabectedin/Wagner/CTARC unrecovered sources, or any egress route. **No network call of any kind was made. No expression matrix was fetched. No denied route was replayed or rerouted around.** I did not re-derive W02f's or W02e's verdicts; W02f's two observed values enter as taken constants, with a single loader-reproduction control row.

---

## Method and inputs

- **Input (sole data source):** `/home/user/Rare-cancers/research/modalities/emc-expression-panels.json`, `generated_utc 2026-08-29T12:51:32+00:00`, sha256 `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` (hashed inside the script at runtime). Field used: `gene_reads[<symbol>][<platform>].per_sample[].array_percentile`, with `gsm` and `class`.
- **Platform:** GPL6244 (`GSE24369`), single-channel. **464 genes complete-case × 35 samples**, classes `{desmoid_fibromatosis 6, EMC 6, LGFMS 17, fibrosarcoma 6}`. **No cross-platform pooling; GPL3290 was not used at all.** The script asserts `len(names) == 464` and aborts otherwise, so a changed cache cannot silently redefine the null.
- **Specimens:** the **six EMC specimens only**, held fixed for every draw. This is the whole point of the design.
- **Null universe:** 464 complete-case genes minus **all four declared marker sets** — immune (12), endothelial (6), fibro/ECM (14), tumour (9) = 41 genes → **423**. Asserted in-script; matches W02c's independently stated 423.
- **Draw:** uniform **without replacement within a panel**, panels independent, `B = 20000` per family, `k ∈ {14, 6}`, `numpy.random.default_rng(20260908)` consumed in the fixed order k=14 then k=6.
- **Statistic:** `R_gene = k · HHI_gene = k · Σ f_i²`, with `f_i = Cov(g_i, score)/(k · Var(score))` — W02f's exact decomposition, unchanged. Even = 1.0 at any k; larger = more concentrated in fewer genes.
- **Tail and threshold, both pre-declared:** **lower** tail; `p_lower = (#{null ≤ observed} + 1)/(B_valid + 1)`; **α = 0.05**.
- **Observed values TAKEN FROM W02f, not re-derived:** `OBS_FIB = 2.0460` (k=14), `OBS_ENDO = 1.1729` (k=6). Recomputed **once**, as a control row only; the verdict uses the taken constants regardless.
- **Tools:** Python 3.11.15, numpy 2.4.6, Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w02g`, no network. No scipy needed.

### Pre-declaration integrity (the procedure this successor was required to follow)

The complete pre-declaration — draw procedure, universe, B, seed, statistic, tail, exact threshold, the two scored outcomes, **and what result would make the fibro/ECM flatness unremarkable** — is the script's module docstring, written in full before execution. The file was hashed before running, hashed itself at runtime, and hashed again after:

| moment | sha256 of `/tmp/claude-0/w02g/w02g.py` |
|---|---|
| **before run** (`sha256sum`) | `72b3592e3639ba890fa5aecb9ef777cb3ebbe9ce91a6951abca073adcf6501c6` |
| **at runtime** (script hashing itself) | `72b3592e3639ba890fa5aecb9ef777cb3ebbe9ce91a6951abca073adcf6501c6` |
| **after run** (`sha256sum`) | `72b3592e3639ba890fa5aecb9ef777cb3ebbe9ce91a6951abca073adcf6501c6` |

**All three identical. The result is not void.** The script was not edited after seeing any number.

**Declared outcomes, quoted from the frozen docstring:**

- **U (UNREMARKABLE)** — `p_lower > 0.05`: *"THIS IS THE OUTCOME THAT WOULD MAKE THE FIBRO/ECM FLATNESS UNREMARKABLE. It would mean W02f's lower-tail finding is a property of scoring k genes of THIS CACHE on THESE SIX SPECIMENS, not a property of the fibro/ECM marker set… It would be a SECOND NEGATIVE for this lane and is to be reported as such, plainly and without padding."*
- **D (DISTINCT)** — `p_lower ≤ 0.05`: the marker set is flatter than random same-size panels on the same six specimens; H-set disfavoured.

**Declared expectation, quoted from the frozen docstring, so that a null could not be written up as a surprise:** *"I expect U for at least one axis and consider U for BOTH the single most likely outcome… this cache is a curated compartment panel, so a random draw from it is not a random draw from the transcriptome… Random panels drawn from a cache already enriched for these compartments may well be FLATTER STILL than the fibro/ECM set. If that happens the honest report is a second negative, and I am committing to that write-up now, in advance."*

---

## Result

### R1 — Loader-reproduction control (the only re-derivation; PRIMARY reproduction of a PREDICTION)

| axis | k | recomputed `R_gene` | taken from W02f | match |
|---|---|---|---|---|
| fibro/ECM | 14 | **2.0460** | 2.0460 | **True** |
| endothelial | 6 | **1.1729** | 1.1729 | **True** |

An independently written loader reproduces both of W02f's values to four decimals. Row class: **PREDICTION** (a composition statistic, not a measurement); the *agreement* is a **PRIMARY** fact about two computations over the same committed file.

### R2 — Gene-set-matched null, fibro/ECM-matched (k = 14, B = 20,000, 20,000 valid, 0 degenerate)

| quantity | value |
|---|---|
| null `R_gene` mean | 5.7309 |
| min / p01 / **p05** / p25 | 1.3842 / 1.9702 / **2.4021** / 3.3692 |
| **p50** / p75 / p95 / p99 / max | **4.5310** / 6.4496 / 12.5667 / 23.4024 / 238.5029 |
| observed (taken) | **2.0460** |
| count(null ≤ observed) | **294 / 20,000** |
| **lower-tail p** | **0.01475** |
| pre-declared outcome | **D (DISTINCT)** |

All rows **PREDICTION**. Units: `R_gene` is dimensionless (even = 1.0). Uncertainty is Monte-Carlo over 20,000 independent gene-set draws with the six specimens held fixed; the `+1/+1` p-estimator is the pre-declared one.

### R3 — Gene-set-matched null, endothelial-matched (k = 6, B = 20,000, 20,000 valid, 0 degenerate)

| quantity | value |
|---|---|
| null `R_gene` mean | 3.6429 |
| min / p01 / **p05** / p25 | 1.0464 / 1.3081 / **1.5875** / 2.2215 |
| **p50** / p75 / p95 / p99 / max | **2.9943** / 4.2542 / 7.5887 / 12.4847 / 114.0340 |
| observed (taken) | **1.1729** |
| count(null ≤ observed) | **40 / 20,000** |
| **lower-tail p** | **0.00205** |
| pre-declared outcome | **D (DISTINCT)** |

All rows **PREDICTION**.

### R4 — Declared verdict table

| axis | k | observed | null p05 | null p50 | null p95 | `p_lower` | outcome (pre-declared) |
|---|---|---|---|---|---|---|---|
| fibro/ECM | 14 | 2.0460 | 2.4021 | 4.5310 | 12.5667 | **0.01475** | **D (DISTINCT)** |
| endothelial | 6 | 1.1729 | 1.5875 | 2.9943 | 7.5887 | **0.00205** | **D (DISTINCT)** |

---

## Verdict

> **The gene-set-matched null does not make the fibro/ECM flatness unremarkable. Both surviving EMC compartment axes are flatter across their own genes than random same-size panels drawn from the same cache and scored on the same six EMC specimens** — fibro/ECM at lower-tail p = 0.01475 (294 of 20,000 random 14-gene panels were as flat or flatter), endothelial at p = 0.00205 (40 of 20,000). Both fire the pre-declared **D** outcome at the pre-declared α = 0.05.
>
> **H-set is disfavoured on both axes.** "Any fourteen genes of this cache are this flat on these six specimens" is not what the cache does: the median random 14-gene panel reaches `R_gene` 4.53, more than twice the fibro/ECM value, and the median random 6-gene panel reaches 2.99, more than twice the endothelial value. The evenness of variance contribution across the declared markers is a property of **those gene sets**, not an artefact of the substrate or of k.
>
> **My pre-declared expectation was wrong, and I am reporting that as the headline of this run rather than as a footnote.** I predicted, in writing and before execution, that random panels drawn from a compartment-curated cache would very likely be *flatter still* (outcome U on both axes) and I pre-committed to writing that up as a second negative. The data went the other way on both axes. The reasoning behind the expectation — that the cache is curated and therefore internally co-regulated — is not supported here: the random panels are strongly *right-skewed toward concentration* (means 5.73 and 3.64 against medians 4.53 and 2.99, maxima 238.5 and 114.0), which is what one expects when an arbitrary panel is dominated by whichever one or two of its genes happens to vary most across six arrays. A coherent marker set is the thing that avoids that domination.
>
> **What this does NOT establish, stated as firmly as the verdict.** It does not turn W02f's post-hoc lower-tail observation into a pre-registered finding — that observation remains post-hoc, and this test is a *separate*, independently pre-declared question about a *different* null. It does not revive W02f's A4: `HHI_sample` is untouched here and the sample-side negative on both axes stands exactly as W02f reported it. And it licenses **no** biological, mechanistic or clinical claim whatsoever: this is one composition statistic of a percentile cache compared against a permutation of that same cache, across 464 genes and six arrays.

**Two ordinary reasons this could read as significant without being interesting, both retained.** (i) The two axes are not independent tests of one hypothesis and I apply no multiplicity correction, because none was pre-declared — at α = 0.05 with two axes, the fibro/ECM p = 0.01475 would survive a Bonferroni α/2 = 0.025 and the endothelial p = 0.00205 comfortably so, but that arithmetic is **POST-HOC** and is offered as a caution, not as a corrected result. (ii) "Flatter than a random panel" is close to a definition of a coherent marker set; the finding is best read as a **positive control on the marker sets** — they behave like coherent axes rather than like arbitrary gene lists — and only secondarily as evidence about EMC.

---

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24 x86_64, Python 3.11.15, numpy 2.4.6, cwd `/tmp/claude-0/w02g`, **no network**, no paid API, no GPU.

| # | command | exit code | key verbatim output |
|---|---|---|---|
| 1 | `python3 -c "import numpy,sys;print('numpy',numpy.__version__,'python',sys.version.split()[0])"` | 0 | `numpy 2.4.6 python 3.11.15` |
| 2 | `sha256sum /tmp/claude-0/w02g/w02g.py` (before run) | 0 | `72b3592e3639ba890fa5aecb9ef777cb3ebbe9ce91a6951abca073adcf6501c6` |
| 3 | `cd /tmp/claude-0/w02g && python3 w02g.py 2>&1 \| tee out.txt` | **0** (`EXIT=0` via `${PIPESTATUS[0]}`) | full output below |
| 4 | `sha256sum /tmp/claude-0/w02g/w02g.py` (after run) | 0 | `72b3592e3639ba890fa5aecb9ef777cb3ebbe9ce91a6951abca073adcf6501c6` — **identical to #2** |
| 5 | `git rev-parse HEAD` (start and end) | 0 | `98a0833f1ede2cf9cef13790388260567a32e868` both times |
| 6 | `git status --porcelain` (start and end) | 0 | identical 8 `??` lines, all coordinator report files, **none a path I touched** |
| 7 | `env \| grep -c '^ANTHROPIC_MODEL='` | 1 (grep no-match) | `0` — no served-model variable exists |
| 8 | `sha256sum research/modalities/emc-expression-panels.json` (start, end, and in-script) | 0 | `123bd05a…f336bd9` all three times |

**Verbatim output of run #3, in full:**

```
SELF sha256 (as read at runtime) = 72b3592e3639ba890fa5aecb9ef777cb3ebbe9ce91a6951abca073adcf6501c6
SOURCE sha256 = 123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9
SOURCE generated_utc = 2026-08-29T12:51:32+00:00
PLATFORM GSE24369_series_matrix.txt.gz | complete-case 464 genes x 35 samples | {'desmoid_fibromatosis': 6, 'EMC': 6, 'LGFMS': 17, 'fibrosarcoma': 6}
declared markers excluded: 41 (immune 12, endo 6, fibroECM 14, tumour 9)
null universe size = 423  (expected 464 - 41 = 423)

=== LOADER-REPRODUCTION CONTROL (single row; verdict uses the TAKEN constants) ===
fibro/ECM  k=14 : recomputed R_gene = 2.0460   TAKEN FROM W02f = 2.0460   match=True
endothelial k=6 : recomputed R_gene = 1.1729   TAKEN FROM W02f = 1.1729   match=True

=== GENE-SET-MATCHED NULL, fibro/ECM-matched : k=14, B=20000, 20000 valid, 0 degenerate ===
null R_gene  mean=5.7309  min=1.3842  p01=1.9702 p05=2.4021 p25=3.3692 p50=4.5310 p75=6.4496 p95=12.5667 p99=23.4024  max=238.5029
OBSERVED (taken from W02f) R_gene = 2.0460
count(null <= obs) = 294 / 20000
LOWER-tail p = 0.01475   alpha = 0.05   -> outcome D (DISTINCT)

=== GENE-SET-MATCHED NULL, endothelial-matched : k=6, B=20000, 20000 valid, 0 degenerate ===
null R_gene  mean=3.6429  min=1.0464  p01=1.3081 p05=1.5875 p25=2.2215 p50=2.9943 p75=4.2542 p95=7.5887 p99=12.4847  max=114.0340
OBSERVED (taken from W02f) R_gene = 1.1729
count(null <= obs) = 40 / 20000
LOWER-tail p = 0.00205   alpha = 0.05   -> outcome D (DISTINCT)

=== DECLARED VERDICT TABLE ===
axis             k   observed   null p05   null p50   null p95   p_lower outcome
fibro/ECM       14     2.0460     2.4021     4.5310    12.5667   0.01475 D (DISTINCT)
endothelial      6     1.1729     1.5875     2.9943     7.5887   0.00205 D (DISTINCT)

H-set = 'any k genes of this cache are this flat on these six EMC specimens'.
U on an axis => H-set is NOT excluded for that axis; W02f's gene-side lower-tail departure
               must not be attributed to that marker set.
D on an axis => the marker set is flatter than random same-size panels; H-set disfavoured.

No biological, mechanistic or clinical claim follows from either outcome.
```

**PROPOSED (NOT RUN):** the same gene-set-matched null against the full `GSE24369` series matrix rather than the 464-gene panel cache; a null drawn from a transcriptome-wide universe rather than a compartment-curated one; any multiplicity-corrected or two-tailed variant. None of these was executed and none is claimed. `scripts/preflight.sh` was **not run** (dispatch forbids it); no repository test tier was invoked, because I changed no repository file.

**Script, returned inline (not written into the tree).** The complete file whose sha256 is `72b3592e…6501c6` is `/tmp/claude-0/w02g/w02g.py`; its module docstring is the frozen pre-declaration quoted in the Method section, and its body is the ~90 lines of loader + `r_gene()` + two `run()` calls whose output is reproduced verbatim above. The loader, the universe construction, the three asserts (464 genes, 6 EMC specimens, 423-gene universe), the seed `20260908`, `B = 20000` and the `+1/+1` lower-tail estimator are all as described; the decomposition `r_gene(G)` is byte-for-byte the share computation W02f used, reduced to the single statistic this test needs.

---

## Limitations

1. **Substrate.** The 479-gene panel cache (464 complete-case here) is the only admissible input. The expression matrices are **not committed** and fetching them is **denied**. This is a substrate limit, not a scheduling gap, and it bounds every number above. Both the observed values and the entire null live inside 464 genes × 6 arrays.
2. **The null universe is curated, not transcriptome-wide.** 423 genes of a compartment panel are not a random sample of the transcriptome. A "random panel" here is a random panel *of this cache*. Whether the same verdict would hold against a transcriptome-wide universe is **UNKNOWN** and cannot be tested here.
3. **n = 6.** Six EMC specimens fix the whole design. Every share, every `R_gene`, and every null draw rests on six arrays. Six arrays are not six patients and support no cohort statement.
4. **Not a measurement.** `array_percentile` is a within-array rank. A percentile-score composition statistic is an **ASSOCIATION**, never a mechanism. Nothing here measures collagen, matrix density, fibroblast content, microvessel density, perfusion, stroma, or treatment response. **No clinical efficacy, safety, selectivity, therapeutic-window or readiness claim follows.** There is no wet lab.
5. **Marker attribution is assumed, not measured** — W02b's and W02c's limitation carries over unchanged. That a `COL1A1` or `PECAM1` reading in an EMC sample originates in the named compartment rather than in tumour cells is exactly what bulk data cannot establish.
6. **Multiplicity.** Two axes, no pre-declared correction. The post-hoc Bonferroni note in the Verdict is labelled post-hoc and must not be promoted.
7. **This does not retro-fit W02f.** W02f's lower-tail `HHI_gene` finding remains **POST-HOC** in W02f. This is a separate pre-declared test of a different null and does not launder that label.
8. **What was left alone.** `HHI_sample`, the SD/floor comparisons, W02d's gate, and W02e's endothelial verdict were not re-run and are not re-issued. W02f's sample-side negative (A4 did not fire on either axis) stands unaltered.
9. **No successor may treat "D on both axes" as a discriminating result *between* the two axes.** The two lower-tail p-values are not a comparison; nothing here says fibro/ECM and endothelium differ from each other.

---

## Stop condition

**Declared up front:** *return the moment both gene-set-matched nulls (k = 14 and k = 6) have run to a real exit code, the pre-run and post-run sha256 of the pre-declared script have been compared, and the pre-declared outcome (U or D) has been read off for both axes.*

**Status: MET.** Both nulls ran in a single invocation, exit code **0**; the three hashes of `w02g.py` are identical, so the result is not void; both axes read **D (DISTINCT)** against the pre-declared α = 0.05. I returned immediately, without extending into the transcriptome-wide universe, the multiplicity variants, or any further statistic.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 9** (target ~40).
- **Wall clock: 2 minutes 22 seconds** — `date -u` start `Tue Sep 8 03:10:36 UTC 2026`, end `Tue Sep 8 03:12:58 UTC 2026` (target ~40 minutes).
- Well inside both budgets because the stop condition was met on the first run and I did not pad.

---

## Next concrete action

**One successor, and it is a scoping test rather than another null.** The honest weakness of this result is Limitation 2: the 423-gene universe is a *curated compartment panel*, so "flatter than a random panel of this cache" may be a much weaker statement than "flatter than a random panel of the transcriptome". The single most informative next step that is **executable on the committed substrate** is to characterise the universe itself — for each of the 423 non-marker genes, compute its between-EMC-specimen SD, and report how the random-panel `R_gene` distribution decomposes into (a) the spread of single-gene variances in the universe and (b) the between-gene correlation structure. If the random panels' concentration is driven almost entirely by a heavy tail of a few high-variance genes, then "the marker sets are flat" reduces to "the marker sets happen to exclude that tail", which is a far weaker claim than D suggests, and it must be stated. That test needs no egress, no new data, and one pre-declared script.

**What must not be done next:** re-running this null against the full `GSE24369` series matrix. That requires the uncommitted expression matrix and egress that is **denied**; naming it as a successor would be proposing a route I already know is closed.
