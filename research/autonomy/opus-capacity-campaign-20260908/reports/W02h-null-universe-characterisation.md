<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:29:18Z UTC
     agent id aa65c8d0599c60e9d ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aa65c8d0599c60e9d.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

# W02h — Is the random-panel concentration a heavy variance tail, or correlation structure?

## Worker

- **Worker ID:** W02h (lane 2 refill), OPUS-CAPACITY-CAMPAIGN-20260908. W02g's named successor, and a test of W02g's own weakest point.
- **Lane:** Lane 2 — EMC microenvironment. Decomposition of the 423-gene random-panel draw universe.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I self-report as Claude Opus 5 (`claude-opus-5`), running as Claude Code in the Anthropic Cloud remote container. **This is a self-report and must not be treated as an observed fact.** `env | grep -c '^ANTHROPIC_MODEL='` returned **0** — no served-model variable exists inside the session, so the model is not confirmable from here. The coordinator must extract the runtime model from the transcript.
- **Write isolation:** READ-ONLY on the Git tree, honoured. All execution under `/tmp/claude-0/w02h/`. **Nothing written, moved or deleted anywhere under `/home/user/Rare-cancers`. No git write operation of any kind.** `scripts/preflight.sh` was not run.

**`date -u` at start:** `Tue Sep  8 03:19:38 UTC 2026`
**`date -u` at end:** `Tue Sep  8 03:23:19 UTC 2026`

**`git rev-parse HEAD` at start:** `84f02dae1809ae050e40254f06310ed849982527`
**`git rev-parse HEAD` at end:** `302c2b63f7cc3ff16e2690de46e90a644181635f` — **HEAD MOVED under me, and I am reporting that plainly rather than as a formality.** I performed no git write operation of any kind; the movement is the campaign coordinator committing collected report files in the shared checkout while I ran. I did not create, edit or commit any of them.

**`git status --porcelain`:** at start, untracked coordinator-written report files under `research/autonomy/opus-capacity-campaign-20260908/reports/` (I captured the listing through `| head -20`, so I state only that all captured lines were `??` report paths, none a path I touched — I am not claiming to have seen the untruncated list). At end, **empty output — the tree is clean**, consistent with the coordinator having committed those files at `302c2b63`.

**Input integrity across the run.** `sha256(research/modalities/emc-expression-panels.json)` = `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` at start, again at end, and again **from inside the analysis script at runtime**. It matches the hash named in my dispatch. The input is unchanged.

**Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (51 lines):**

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

At end the same command produced the same variable set; I recorded it as `md5sum` = `d34e5ad074f671b813c93e14de5df58c` rather than re-pasting. I did not md5 the start output, so I am **not** claiming a byte-identical start/end comparison — only that the same variables were present.

---

## Question

**W02g's DISTINCT verdict says both surviving EMC compartment axes are flatter than random same-size panels of the 423-gene non-marker universe. Is that random-panel concentration driven by a heavy tail of a few high-variance genes — in which case "the marker sets are flat" reduces to "the marker sets happen to exclude that tail" — or does it require the between-gene correlation structure?**

W02g's author named this as the honest weakness of its own result (its Limitation 2): the 423-gene draw universe is a **curated compartment panel**, not a transcriptome, so "flatter than a random panel of this cache" may be much weaker than it sounds. The decomposition had never been run.

**Substrate limit, stated up front and not as a gap to close.** The only input is the committed **479-gene panel cache** (464 complete-case on GPL6244), **not an expression matrix**. The expression matrices are not committed and fetching them is **denied**; I made no attempt, probe or workaround. Every quantity below is a statement about `array_percentile` values — a **within-array rank** — held in that cache. Six arrays are not six patients; arrays and specimens are not patients. Every result is an **ASSOCIATION**, never a mechanism and never clinical. There is no wet lab: no efficacy, safety, selectivity or readiness claim follows.

---

## Prior-work check

| # | command | result |
|---|---|---|
| 1 | `rg -c 'R_gene' --glob '!.git'` (run by W02g at its HEAD, re-confirmed by reading the tree) | `R_gene` machinery exists only in the lane-2 campaign reports `W02f` and `W02g`. No `R_var`, no variance-spread decomposition anywhere. |
| 2 | `grep -n -i -E 'HHI\|R_gene\|f_i\|Cov\|share\|marker set' reports/W02f-fibro-ecm-decomposition.md` | recovered W02f's exact decomposition (`C_i = Cov(g_i,s)/k`, `f_i = C_i/Var(s)`, `R_gene = k·ΣHHI`), which I reuse **unchanged** so the comparison is like-for-like. |
| 3 | `grep -n -E 'MARKER SET' reports/W02d-compartment-variance-battery.md` | recovered the four declared marker sets verbatim (immune 12, fibro/ECM 14, tumour 9) — I did not re-invent them. |
| 4 | `grep -n -E 'PECAM1\|CDH5\|VWF' reports/W02c-endothelial-variance-artifact-battery.md` | recovered the 6 endothelial markers and W02c's per-marker EMC SDs, which my U2 table independently reproduces. |
| 5 | reading of `CLOSED-WORK.md` | I touched none of: the clinical registry, PUB-ASO/Qeios frozen deliverables, the NR4A Perspective refusal, Brenca, Hofvander, the paired-Davis negative, or any of the unrecovered pazopanib/sunitinib/trabectedin/Wagner/CTARC sources. **No network call of any kind. No expression matrix fetched. No denied route replayed or routed around.** |

**What is new here.** W02c ran a size-matched random-panel null on **SD**; W02g ran one on **`R_gene`**. Neither decomposed the null into variance spread versus correlation structure, and no `R_var`-style diagonal-only surrogate exists anywhere in the corpus. I re-derived nothing from W02f or W02g except the single mandated loader-reproduction control row.

---

## Method and inputs

- **Input (sole data source):** `/home/user/Rare-cancers/research/modalities/emc-expression-panels.json`, `generated_utc 2026-08-29T12:51:32+00:00`, sha256 `123bd05a…f336bd9` (hashed inside the script at runtime). Field used: `gene_reads[<symbol>]["GSE24369_series_matrix.txt.gz"].per_sample[].array_percentile`, with `gsm` and `class`.
- **Platform:** GPL6244 (`GSE24369`). **464 genes complete-case × 35 samples**, classes `{EMC 6, LGFMS 17, desmoid_fibromatosis 6, fibrosarcoma 6}`. **No cross-platform pooling; GPL3290 was not used at all.** Asserted in-script (`assert X.shape[0] == 464`).
- **Specimens:** the **six EMC specimens only**, held fixed for every draw, exactly as in W02g.
- **Universe:** 464 complete-case genes minus all 41 declared marker genes → **423**, asserted in-script; matches W02c's and W02g's independently stated 423.
- **Draw:** uniform **without replacement within a panel**, panels independent, `B = 20000` per family, `k ∈ {14, 6}`, `numpy.random.default_rng(20260908)` consumed in the fixed order k=14 then k=6. Permutation companion uses a separate generator, seed `20260909`. **I do not claim my panels are the same panels W02g drew** — only the same seed and the same declared procedure.
- **The decomposition (exact algebra, pre-declared):** with `Var(s) = (1/k²)ΣᵢΣⱼCov(gᵢ,gⱼ)` and `f_i = Cov(gᵢ,s)/(k·Var(s))`, setting every **off-diagonal covariance to zero** collapses the same algebra to `f_i^var = vᵢ/Σvⱼ`, so
  - **`R_var(G) = k·Σ(vᵢ/Σvⱼ)²` is exactly limb (a)** — the concentration a panel would show if its genes were mutually uncorrelated, i.e. the spread of single-gene variances and nothing else;
  - **`R_gene − R_var` is limb (b)** — the between-gene correlation structure;
  - **`R_perm`** (one gene-wise independent permutation of each gene's six values, recomputing `R_gene`) is a Monte-Carlo companion to `R_var` that preserves each marginal variance exactly while destroying correlation, and unlike the analytic `R_var` it retains the finite-`n = 6` sampling noise.
- **Taken as given, not re-derived:** `OBS_FIB R_gene = 2.0460` (p = 0.01475), `OBS_ENDO R_gene = 1.1729` (p = 0.00205). Recomputed **once**, as a control row only.
- **Tools:** Python 3.11.15, numpy 2.4.6, Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w02h`, **no network**, no paid API, no GPU, no scipy (Spearman ρ computed as Pearson on ranks).

### Pre-declaration integrity

The complete pre-declaration — the decomposition, the statistics, the thresholds, the direction of interest, and **explicitly what result would weaken W02g's verdict** — is the script's module docstring, written in full **before execution**.

| moment | sha256 of `/tmp/claude-0/w02h/w02h.py` |
|---|---|
| **before run** (`sha256sum`) | `56142f60cc2ee7a4ac4a4096b37123979ef9f1a62303b82a2f451ba8af0fd622` |
| **at runtime** (script hashing itself) | `56142f60cc2ee7a4ac4a4096b37123979ef9f1a62303b82a2f451ba8af0fd622` |
| **after run** (`sha256sum`) | `56142f60cc2ee7a4ac4a4096b37123979ef9f1a62303b82a2f451ba8af0fd622` |

**All three identical. The result is not void.** The script was not edited after seeing any number.

**Pre-declared statistics and thresholds, quoted from the frozen docstring:**

- `S1` = Spearman ρ(`R_gene`, `R_var`) over the B random panels at each k.
- `S2` = `median(R_var)/median(R_gene)` over the B random panels.
- `S3` = `p_var`, the lower-tail p of the axis's own `R_var` against the random panels' `R_var`, estimator `(#{null ≤ obs}+1)/(B_valid+1)`, α = 0.05 — **the same estimator, tail and α as W02g, deliberately.**

**Pre-declared outcomes, quoted:**

- **T (TAIL-DRIVEN)** — fires iff **T-i** (`ρ ≥ 0.70` **and** `ratio ≥ 0.60`) **and T-ii** (`p_var ≤ 0.05`). *"**T IS THE RESULT THAT WEAKENS W02g.** … 'Flatter than a random panel' would then be substantially re-describable as 'its genes' variances are unusually equal / it avoids the high-variance tail', and W02g's DISTINCT verdict must be DOWNGRADED and reported as the weaker claim it would then be. I pre-commit to headlining T if it fires."*
- **C (CORRELATION-DEPENDENT)** — neither limb. *"W02g's D is not reducible to the variance tail."*
- **M (MIXED)** — exactly one limb. *"Reported per limb, explicitly, as a PARTIAL weakening. M … is NOT to be written up as a clean vindication of W02g."*

**Pre-declared expectation, quoted, so neither result could be staged as a surprise:** *"I expect T-i to FIRE (rho high, ratio high) because with n = 6 a panel's concentration is plausibly dominated by whichever one or two of its genes varies most … I am LESS sure about T-ii, and I expect the two axes to SPLIT on it: the endothelial markers are known from W02c to be individually HIGH-variance … so endothelium plausibly does NOT sit in the low-variance part of the universe and may return M rather than T."*

---

## Result

### R1 — Loader-reproduction control (the only re-derivation)

| axis | k | recomputed `R_gene` | taken from W02f/W02g | match |
|---|---|---|---|---|
| fibro/ECM | 14 | **2.0460** | 2.0460 | **True** |
| endothelial | 6 | **1.1729** | 1.1729 | **True** |

An independently written loader reproduces both values to four decimals. Row class **PREDICTION**; the *agreement* is a **PRIMARY** fact about two computations over the same committed file.

### R2 — U1: the 423-gene universe's own between-EMC-specimen SD distribution

All rows **PREDICTION**. Units: `array_percentile` (dimensionless rank, 0–1); SD is between the six EMC specimens, `ddof = 1`; n = 423 genes.

| quantity | value |
|---|---|
| SD mean | 0.0646 |
| SD min / p05 / p25 / **p50** / p75 / p95 / max | 0.0008 / 0.0067 / 0.0236 / **0.0418** / 0.0839 / 0.2043 / 0.3063 |
| SD skewness / variance skewness | **1.711** / **3.051** |
| top-1 gene's share of total universe variance | 2.77 % |
| top-5 / top-10 / top-20 / top-42 (10 %) share | 12.52 % / **22.40 %** / 38.21 % / 59.80 % |
| universe-wide k-normalised variance concentration `R_var(all 423)` | **4.6897** (even = 1.0) |
| ten highest-SD genes | NT5E 0.3063, PMAIP1 0.3016, HAS2 0.2873, CD36 0.2840, SLC7A2 0.2765, CHGB 0.2757, MET 0.2611, PAPSS2 0.2551, PCK1 0.2529, TOP2A 0.2487 |

**The universe does have a right-skewed variance tail** (skewness 1.71 on SD, 3.05 on variance; p95/p50 SD ratio 4.9×). But it is a **broad** tail, not a few dominant genes: no single gene holds even 3 % of total variance, and it takes 42 genes — a tenth of the universe — to reach 60 %.

### R3 — U2: where the marker genes sit inside that SD distribution

Percentile rank of each marker's own EMC SD among the 423 universe SDs. All rows **PREDICTION**.

| axis | per-gene SD and percentile rank |
|---|---|
| fibro/ECM (k=14) | COL1A1 0.0105 (9.2) · COL1A2 0.0121 (10.6) · COL3A1 0.0360 (43.3) · COL5A1 0.1211 (85.6) · DCN 0.1616 (90.8) · **LUM 0.2963 (99.5)** · FAP 0.1446 (87.9) · THY1 0.1126 (84.2) · POSTN 0.0811 (73.0) · FN1 0.0313 (37.4) · PDGFRA 0.0329 (39.2) · PDGFRB 0.1027 (82.3) · ACTA2 0.0258 (28.1) · **COL11A1 0.2213 (95.5)** |
| | **median percentile rank 77.7 ; 8/14 above universe p50 ; 2/14 above universe p95** |
| endothelial (k=6) | PECAM1 0.2073 (95.0) · VWF 0.2288 (96.2) · CDH5 0.1392 (87.2) · **KDR 0.3029 (99.8)** · **FLT1 0.3024 (99.8)** · MCAM 0.0928 (78.3) |
| | **median percentile rank 95.6 ; 6/6 above universe p50 ; 4/6 above universe p95** |

**This is the direct answer to the reduction the task asked about, and it goes the opposite way.** Neither marker set excludes the high-variance tail. Both are **enriched** in it: the fibro/ECM set's median gene sits at the 78th percentile of universe SD and the endothelial set's at the **96th**, with `KDR` and `FLT1` at the 99.8th. The endothelial markers are the six highest-variance-per-gene set of the two, and they are the axis W02g scored as *flattest*. (These per-gene EMC SDs independently reproduce W02c's reported values — PECAM1 0.207, KDR 0.303, FLT1 0.302, MCAM 0.093 — from a separately written loader.)

### R4 — N1/N2: decomposition of the random-panel `R_gene` distribution

`B = 20,000` per family, 20,000 valid, 0 degenerate. All rows **PREDICTION**. `R_gene`, `R_var`, `R_perm` are dimensionless (even = 1.0 at any k). Uncertainty is Monte-Carlo over 20,000 independent gene-set draws with the six specimens held fixed.

**fibro/ECM-matched, k = 14**

| distribution | mean | p05 | p50 | p95 | max |
|---|---|---|---|---|---|
| `R_gene` (full) | 5.7309 | 2.4021 | 4.5310 | 12.5667 | **238.5029** |
| `R_var` (variances only, off-diagonals zeroed) | 3.7998 | 2.0825 | 3.5249 | 6.4932 | **11.8613** |
| `R_perm` (gene-wise permuted, correlation destroyed) | 6.8650 | 2.6884 | 5.3617 | 15.2807 | 154.8688 |

**endothelial-matched, k = 6**

| distribution | mean | p05 | p50 | p95 | max |
|---|---|---|---|---|---|
| `R_gene` (full) | 3.6429 | 1.5875 | 2.9943 | 7.5887 | **114.0340** |
| `R_var` (variances only) | 2.7548 | 1.4734 | 2.5448 | 4.7462 | **5.8959** |
| `R_perm` (permuted) | 3.7509 | 1.6033 | 3.1128 | 7.7252 | 78.2872 |

### R5 — Declared verdict table

| axis | k | `S1` ρ(R_gene,R_var) | ≥0.70? | `S2` ratio | ≥0.60? | **T-i** | marker `R_var` | count(null ≤ obs) | **`S3` p_var** | ≤0.05? = **T-ii** | **outcome** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fibro/ECM | 14 | **0.3659** | No | 0.7779 | Yes | **False** | 3.0441 | 6637/20000 | **0.33188** | **False** | **C (CORRELATION-DEPENDENT)** |
| endothelial | 6 | **0.5317** | No | 0.8499 | Yes | **False** | 1.3934 | 612/20000 | **0.03065** | **True** | **M (MIXED)** |

Mean pairwise Pearson r across the six EMC specimens, as declared descriptive context: fibro/ECM **0.5168**, endothelial **0.8124**, against random-panel medians of **0.0192** (k=14) and **0.0037** (k=6). For both axes `count(null mean-r ≤ observed) = 20000/20000`, so the pre-declared lower-tail p = 1.00000; the implied upper-tail exceedance is ≤ 1/20001 ≈ 5.0×10⁻⁵, which is **POST-HOC arithmetic** offered as context and is not a pre-declared test.

---

## Verdict

> **The decision-relevant answer is NO on both axes, and it is a clean negative for the reduction the task was built to detect. The pre-declared TAIL-DRIVEN outcome T did not fire for either axis.**
>
> **Limb T-i failed on both axes, and it failed on ρ, not on level.** The variance-spread-only surrogate `R_var` reproduces most of the *level* of the random-panel concentration (median ratio 0.78 at k=14, 0.85 at k=6, both above the 0.60 threshold) but it reproduces the *ordering* poorly (Spearman ρ = 0.37 and 0.53, both far below the 0.70 threshold). The decisive detail is in the maxima: random `R_gene` reaches **238.5** at k=14 and **114.0** at k=6, while `R_var` — which is the exact concentration those same panels would show with every off-diagonal covariance zeroed — **cannot exceed 11.86 and 5.90**. The right tail of the random-panel concentration, the part that puts the median random panel more than twice as high as either marker set, is **not** something a heavy tail of high-variance genes can produce. It requires between-gene correlation. Two panels with identical single-gene variances differ in `R_gene` by more than an order of magnitude depending on how their genes co-vary.
>
> **Limb T-ii failed on fibro/ECM (`p_var` = 0.332 — entirely ordinary) and fired on endothelium (`p_var` = 0.031), so the axes split, as I predicted in writing they might.** But the endothelial firing does **not** mean what the reduction hypothesis needs it to mean, and this is the point that must not be glossed. `R_var` is low for the endothelial set because its six genes' variances are unusually **equal to each other** — not because they are small. All six sit above the universe median SD and four sit above its 95th percentile (`KDR` and `FLT1` at the 99.8th). The endothelial set does not avoid the high-variance tail; **it is almost entirely inside it.** "The marker set happens to exclude the tail" is factually wrong for endothelium and wrong for fibro/ECM too (median gene at the 78th percentile, `LUM` at the 99.5th, `COL11A1` at the 95.5th).
>
> **So W02g's DISTINCT verdict is not reducible to a variance-tail artefact, and I am stating the positive form of that plainly.** The marker sets' flatness tracks their **coherence**, not their variance profile: mean pairwise r of 0.52 (fibro/ECM) and 0.81 (endothelial) against random-panel medians of 0.02 and 0.004, with every one of 20,000 random panels at or below the observed value on both axes. A random panel of this cache is a set of high-variance genes that do **not** move together, and one or two of them dominate; a marker set is a set of high-variance genes that **do** move together, and none dominates.
>
> **My pre-declared expectation was wrong on its main limb, and I am reporting that rather than burying it.** I predicted in writing that T-i would fire — that with n = 6 the concentration would be dominated by whichever one or two genes varied most. It did not fire on either axis. I was right about the split on T-ii and right that endothelium's markers are individually high-variance, but wrong about the mechanism driving the null.
>
> **What this does NOT establish.** It does not turn W02f's post-hoc lower-tail observation into a pre-registered finding; that label stands. It does not extend to a transcriptome-wide universe — W02g's Limitation 2 is **narrowed, not removed**: I have shown the concentration is correlation-driven *within this curated cache*, and what a transcriptome-wide draw universe would do remains **UNKNOWN** and untestable on the committed substrate. And it licenses **no** biological, mechanistic or clinical claim whatsoever. That a set of co-varying percentile ranks is more coherent than a random set of percentile ranks is a statement about a 464-gene cache and six arrays. It is not a statement about vessels, matrix, fibroblasts, stroma, treatment, or any patient.
>
> **The ordinary reason this could read as more than it is, retained.** "A curated marker set is more internally correlated than a random gene list" is close to a tautology — it is what curation means. The honest reading of this run, and of W02g's, is therefore that both are best treated as a **positive control on the marker sets** and only secondarily as evidence about EMC. What this run adds is that the control passes for a *specific and checkable* reason (correlation structure), and that the most natural deflationary explanation (a variance tail) is measurably not the reason.

---

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24 x86_64, Python 3.11.15, numpy 2.4.6, cwd `/tmp/claude-0/w02h`, **no network**, no paid API, no GPU.

| # | command | exit code | key verbatim output |
|---|---|---|---|
| 1 | `python3 -c "import numpy,sys;print('numpy',numpy.__version__,'python',sys.version.split()[0])"` | 0 | `numpy 2.4.6 python 3.11.15` |
| 2 | `sha256sum /tmp/claude-0/w02h/w02h.py` (before run) | 0 | `56142f60cc2ee7a4ac4a4096b37123979ef9f1a62303b82a2f451ba8af0fd622` |
| 3 | `cd /tmp/claude-0/w02h && python3 w02h.py > out.txt 2>&1` | **0** (`EXIT=0`) | full output reproduced in R2–R5 above and quoted below |
| 4 | `sha256sum /tmp/claude-0/w02h/w02h.py` (after run) | 0 | `56142f60…0fd622` — **identical to #2** |
| 5 | `git rev-parse HEAD` (start / end) | 0 | `84f02dae…` / `302c2b63…` — **moved; coordinator commit, not mine** |
| 6 | `git status --porcelain` (start / end) | 0 | start: `??` coordinator report paths (captured via `head -20`); end: **empty** |
| 7 | `env \| grep -c '^ANTHROPIC_MODEL='` | 1 (grep no-match) | `0` — no served-model variable exists |
| 8 | `sha256sum research/modalities/emc-expression-panels.json` (start, end, in-script) | 0 | `123bd05a…f336bd9` all three times |
| 9 | `df -h` | 2 | `/dev/vda 252G 35G 2.9G 93% /` — recorded because tool call #3 of the session failed once with an ENOSPC on the harness task temp filesystem; I did **not** delete any other worker's scratch, and re-ran under `/tmp/claude-0/w02h/` successfully |

**Verbatim key output of run #3** (the full run is reproduced as R2–R5; the verdict block quoted literally):

```
=== DECLARED VERDICT TABLE ===
axis           k      rho    ratio     R_var     p_var    meanr  p_meanr  outcome
fibroECM      14   0.3659   0.7779    3.0441   0.33188   0.5168  1.00000  C (CORRELATION-DEPENDENT)
endothelial    6   0.5317   0.8499    1.3934   0.03065   0.8124  1.00000  M (MIXED)
```

```
-- fibroECM-matched, k=14, 20000 valid of 20000 --
   R_gene (full)                                        mean=  5.7309 p05= 2.4021 p50= 4.5310 p95= 12.5667 max= 238.5029
   R_var  (variances only, off-diagonals zeroed)        mean=  3.7998 p05= 2.0825 p50= 3.5249 p95=  6.4932 max=  11.8613
   R_perm (gene-wise permuted, correlation destroyed)   mean=  6.8650 p05= 2.6884 p50= 5.3617 p95= 15.2807 max= 154.8688
   PRE-DECLARED OUTCOME: T-i=False  T-ii=False  ->  C (CORRELATION-DEPENDENT)
-- endothelial-matched, k=6, 20000 valid of 20000 --
   R_gene (full)                                        mean=  3.6429 p05= 1.5875 p50= 2.9943 p95=  7.5887 max= 114.0340
   R_var  (variances only, off-diagonals zeroed)        mean=  2.7548 p05= 1.4734 p50= 2.5448 p95=  4.7462 max=   5.8959
   R_perm (gene-wise permuted, correlation destroyed)   mean=  3.7509 p05= 1.6033 p50= 3.1128 p95=  7.7252 max=  78.2872
   PRE-DECLARED OUTCOME: T-i=False  T-ii=True  ->  M (MIXED)
```

Note that my independently drawn k=14 and k=6 `R_gene` null distributions match W02g's reported values to four decimals at every quantile (mean 5.7309/3.6429, p05 2.4021/1.5875, p50 4.5310/2.9943, p95 12.5667/7.5887, max 238.5029/114.0340) — an unplanned but real cross-check that the same seed and declared procedure reproduce that worker's null exactly.

**PROPOSED (NOT RUN):** a transcriptome-wide draw universe; a `R_var`-conditioned or correlation-conditioned null; any multiplicity-corrected or two-tailed variant; any analysis on the `GSE24369` series matrix. None was executed and none is claimed; the last requires an uncommitted matrix and **denied** egress. `scripts/preflight.sh` was **not run** (dispatch forbids it); no repository test tier was invoked, because I changed no repository file.

**Script, returned inline (not written into the tree).** The complete file whose sha256 is `56142f60cc2ee7a4ac4a4096b37123979ef9f1a62303b82a2f451ba8af0fd622` is `/tmp/claude-0/w02h/w02h.py`. Its module docstring is the frozen pre-declaration quoted in the Method section above, verbatim, and its body is:

```python
import hashlib, json, sys
import numpy as np

SRC = "/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
PLAT = "GSE24369_series_matrix.txt.gz"
B = 20000
ALPHA = 0.05
RHO_T, RATIO_T = 0.70, 0.60

MARK = {
 "immune": ["PTPRC","CD2","CD3D","CD3E","CD8A","CD68","CD163","CSF1R","ITGAM","HLA-DRA","MS4A1","GZMB"],
 "endothelial": ["PECAM1","VWF","CDH5","KDR","FLT1","MCAM"],
 "fibroECM": ["COL1A1","COL1A2","COL3A1","COL5A1","DCN","LUM","FAP","THY1","POSTN","FN1","PDGFRA","PDGFRB","ACTA2","COL11A1"],
 "tumour": ["NR4A3","PPARG","RET","INSM1","SYP","CHGA","ENO2","KIT","CD24"],
}
TAKEN = {"fibroECM": 2.0460, "endothelial": 1.1729}   # from W02f/W02g, NOT re-derived

print("SELF sha256 (as read at runtime) =", hashlib.sha256(open(__file__,'rb').read()).hexdigest())
print("SOURCE sha256 =", hashlib.sha256(open(SRC,'rb').read()).hexdigest())
d = json.load(open(SRC))
print("SOURCE generated_utc =", d.get("generated_utc"))

# ---- loader: complete-case genes on GPL6244 ----
gr = d["gene_reads"]
gsms, klass, rows, names = None, None, [], []
for g in sorted(gr):
    p = gr[g].get(PLAT)
    if not p or not p.get("per_sample"): continue
    ps = p["per_sample"]
    if any(r.get("array_percentile") is None for r in ps): continue
    ids = [r["gsm"] for r in ps]
    if gsms is None:
        gsms = ids; klass = [r["class"] for r in ps]
    if ids != gsms: continue
    names.append(g); rows.append([r["array_percentile"] for r in ps])
X = np.asarray(rows, float)                      # genes x samples
assert X.shape[0] == 464, X.shape
cnt = {c: klass.count(c) for c in sorted(set(klass))}
print("PLATFORM %s | complete-case %d genes x %d samples | %s" % (PLAT, X.shape[0], X.shape[1], cnt))
emc = np.array([i for i,c in enumerate(klass) if c == "EMC"])
assert len(emc) == 6
E = X[:, emc]                                    # 464 x 6
idx = {g:i for i,g in enumerate(names)}

declared = sorted(set(sum(MARK.values(), [])) & set(names))
uni = [g for g in names if g not in set(declared)]
print("declared markers excluded: %d (immune %d, endo %d, fibroECM %d, tumour %d)"
      % (len(declared), *[sum(1 for g in MARK[k] if g in idx) for k in ["immune","endothelial","fibroECM","tumour"]]))
print("null universe size = %d  (expected 464 - 41 = 423)" % len(uni))
assert len(uni) == 423
U = np.array([idx[g] for g in uni])

# ---- statistics ----
def r_gene(M):
    k = M.shape[0]
    s = M.mean(0)
    vs = s.var(ddof=1)
    if vs <= 0: return None
    C = np.array([np.cov(M[i], s, ddof=1)[0,1] for i in range(k)]) / k
    f = C / vs
    return k * float((f**2).sum())

def r_var(M):
    k = M.shape[0]
    v = M.var(1, ddof=1)
    t = v.sum()
    if t <= 0: return None
    return k * float(((v/t)**2).sum())

def mean_pair_r(M):
    k = M.shape[0]
    sd = M.std(1, ddof=1)
    if np.any(sd <= 0): return None
    R = np.corrcoef(M)
    iu = np.triu_indices(k, 1)
    return float(R[iu].mean())

def lowp(null, obs):
    null = np.asarray(null)
    return (int((null <= obs).sum()) + 1) / (len(null) + 1)

def q(a):
    a = np.asarray(a)
    return dict(mean=a.mean(), min=a.min(), p05=np.percentile(a,5), p25=np.percentile(a,25),
                p50=np.percentile(a,50), p75=np.percentile(a,75), p95=np.percentile(a,95), max=a.max())

# ---- CONTROL ROW (only re-derivation) ----
print("\n=== LOADER-REPRODUCTION CONTROL (single row; everything else TAKEN from W02f/W02g) ===")
for ax in ["fibroECM","endothelial"]:
    M = E[[idx[g] for g in MARK[ax]], :]
    rc = r_gene(M)
    print("%-12s k=%2d : recomputed R_gene = %.4f   TAKEN = %.4f   match=%s"
          % (ax, M.shape[0], rc, TAKEN[ax], abs(rc-TAKEN[ax]) < 5e-5))

# ---- U1: the universe itself ----
EU = E[U, :]
sd_u = EU.std(1, ddof=1)
v_u = EU.var(1, ddof=1)
o = np.argsort(v_u)[::-1]
tot = v_u.sum()
print("\n=== U1  BETWEEN-EMC-SPECIMEN SD OF THE 423 NON-MARKER GENES (n=6, ddof=1) ===")
s = q(sd_u)
print("SD  mean=%.4f min=%.4f p05=%.4f p25=%.4f p50=%.4f p75=%.4f p95=%.4f max=%.4f"
      % (s['mean'],s['min'],s['p05'],s['p25'],s['p50'],s['p75'],s['p95'],s['max']))
m3 = float((((sd_u-sd_u.mean())/sd_u.std())**3).mean())
print("SD skewness = %.4f ; variance skewness = %.4f"
      % (m3, float((((v_u-v_u.mean())/v_u.std())**3).mean())))
for n in (1,5,10,20,42):
    print("top-%-3d genes hold %6.2f%% of the universe's total variance" % (n, 100*v_u[o[:n]].sum()/tot))
print("universe-wide k-normalised variance concentration R_var(all 423) = %.4f (even = 1.0)" % (423*((v_u/tot)**2).sum()))
print("top-10 highest-SD universe genes:", ", ".join("%s %.4f" % (uni[i], sd_u[i]) for i in o[:10]))

# ---- U2: where do the marker genes sit in that SD distribution? ----
print("\n=== U2  PERCENTILE RANK OF EACH MARKER GENE'S EMC SD WITHIN THE 423-GENE UNIVERSE ===")
for ax in ["fibroECM","endothelial"]:
    pr = []
    for g in MARK[ax]:
        sg = float(E[idx[g]].std(ddof=1))
        pr.append((g, sg, 100.0*float((sd_u < sg).mean())))
    print("-- %s (k=%d): " % (ax, len(pr)) + "; ".join("%s SD=%.4f pct=%.1f" % t for t in pr))
    pcts = np.array([t[2] for t in pr])
    print("   median percentile rank = %.1f ; n above universe p50 = %d/%d ; n above universe p95 = %d/%d"
          % (np.median(pcts), int((pcts>50).sum()), len(pcts), int((pcts>95).sum()), len(pcts)))

# ---- N1/N2: random panels, decomposed ----
rng = np.random.default_rng(20260908)
rngp = np.random.default_rng(20260909)
print("\n=== N1/N2  RANDOM-PANEL DECOMPOSITION (B=%d, without replacement, seed 20260908) ===" % B)
verdict = {}
for ax, k in (("fibroECM",14), ("endothelial",6)):
    RG, RV, RP, MR = [], [], [], []
    for _ in range(B):
        M = EU[rng.choice(len(U), size=k, replace=False), :]
        a, b = r_gene(M), r_var(M)
        if a is None or b is None: continue
        Mp = np.array([rngp.permutation(row) for row in M])
        c = r_gene(Mp)
        mr = mean_pair_r(M)
        RG.append(a); RV.append(b); RP.append(c if c is not None else np.nan); MR.append(mr if mr is not None else np.nan)
    RG, RV = np.array(RG), np.array(RV)
    RP = np.array(RP, float); MR = np.array(MR, float)
    def rank(a):
        o2 = np.argsort(a, kind="mergesort"); r = np.empty(len(a)); r[o2] = np.arange(len(a)); return r
    rho = float(np.corrcoef(rank(RG), rank(RV))[0,1])
    ratio = float(np.median(RV)/np.median(RG))
    Mk = E[[idx[g] for g in MARK[ax]], :]
    obs_rv, obs_mr = r_var(Mk), mean_pair_r(Mk)
    p_var = lowp(RV, obs_rv)
    p_mr = lowp(MR[~np.isnan(MR)], obs_mr)
    ti = (rho >= RHO_T) and (ratio >= RATIO_T)
    tii = (p_var <= ALPHA)
    out = "T (TAIL-DRIVEN)" if (ti and tii) else ("C (CORRELATION-DEPENDENT)" if (not ti and not tii) else "M (MIXED)")
    verdict[ax] = (k, rho, ratio, obs_rv, p_var, obs_mr, p_mr, ti, tii, out)
    a1, a2, a3 = q(RG), q(RV), q(RP[~np.isnan(RP)])
    print("\n-- %s-matched, k=%d, %d valid of %d --" % (ax, k, len(RG), B))
    for nm, s2 in (("R_gene (full)", a1), ("R_var  (variances only, off-diagonals zeroed)", a2), ("R_perm (gene-wise permuted, correlation destroyed)", a3)):
        print("   %-52s mean=%8.4f p05=%7.4f p50=%7.4f p95=%8.4f max=%9.4f"
              % (nm, s2['mean'], s2['p05'], s2['p50'], s2['p95'], s2['max']))
    print("   S1 Spearman rho(R_gene, R_var) = %.4f   (threshold >= %.2f -> %s)" % (rho, RHO_T, rho>=RHO_T))
    print("   S2 median(R_var)/median(R_gene) = %.4f  (threshold >= %.2f -> %s)" % (ratio, RATIO_T, ratio>=RATIO_T))
    print("   marker-set R_var = %.4f ; count(null R_var <= obs) = %d/%d ; S3 lower-tail p_var = %.5f (alpha %.2f -> %s)"
          % (obs_rv, int((RV<=obs_rv).sum()), len(RV), p_var, ALPHA, p_var<=ALPHA))
    print("   marker-set mean pairwise r = %.4f ; random-panel mean pairwise r p50 = %.4f ; UPPER context lower-tail p = %.5f"
          % (obs_mr, np.nanmedian(MR), p_mr))
    print("   TAKEN from W02g: observed R_gene = %.4f, lower-tail p = %s" % (TAKEN[ax], {"fibroECM":"0.01475","endothelial":"0.00205"}[ax]))
    print("   PRE-DECLARED OUTCOME: T-i=%s  T-ii=%s  ->  %s" % (ti, tii, out))

print("\n=== DECLARED VERDICT TABLE ===")
print("%-12s %3s %8s %8s %9s %9s %8s %8s  %s" % ("axis","k","rho","ratio","R_var","p_var","meanr","p_meanr","outcome"))
for ax,(k,rho,ratio,orv,pv,omr,pmr,ti,tii,out) in verdict.items():
    print("%-12s %3d %8.4f %8.4f %9.4f %9.5f %8.4f %8.5f  %s" % (ax,k,rho,ratio,orv,pv,omr,pmr,out))
print("""
T => W02g's DISTINCT verdict is MATERIALLY WEAKENED for that axis: 'flatter than a
     random panel' is substantially re-describable as 'excludes the high-variance tail'.
C => W02g's DISTINCT is NOT reducible to the variance tail for that axis.
M => partial; report each limb separately and do NOT read it as vindication.
No biological, mechanistic or clinical claim follows from any outcome.""")
```

---

## Limitations

1. **Substrate.** The 479-gene panel cache (464 complete-case here) is the only admissible input. The expression matrices are **not committed** and fetching them is **denied**. This is a substrate limit, not a scheduling gap, and it bounds every number above. Everything lives inside 464 genes × 6 EMC arrays.
2. **W02g's Limitation 2 is narrowed, not removed.** I characterised the *curated* 423-gene universe and showed the concentration in it is correlation-driven. What a **transcriptome-wide** draw universe would do is **UNKNOWN** and is not testable on the committed substrate. Do not read this as "the transcriptome-wide null was checked".
3. **n = 6.** Every variance, covariance, correlation and percentile rank rests on six arrays. Pairwise correlations at n = 6 have four degrees of freedom and are individually very noisy; the mean-pairwise-r figures are stable only as set-level averages over many pairs, and the `R_perm` companion exists precisely because the analytic `R_var` drops that sampling noise. Six arrays are not six patients and support no cohort statement.
4. **Not a measurement.** `array_percentile` is a within-array rank. A percentile-score composition statistic is an **ASSOCIATION**, never a mechanism. Nothing here measures collagen, matrix density, fibroblast content, microvessel density, perfusion, stroma, or treatment response. **No efficacy, safety, selectivity, therapeutic-window or readiness claim follows.** There is no wet lab.
5. **Marker attribution is assumed, not measured** — W02b's and W02c's limitation carries over unchanged. That a `COL1A1` or `PECAM1` reading in an EMC sample originates in the named compartment rather than in tumour cells is exactly what bulk data cannot establish.
6. **`R_var` is an idealisation.** It is the exact algebraic consequence of zeroing off-diagonal covariances, not a resample. Its bounded maximum (11.86 at k=14, 5.90 at k=6) is a mathematical property of a k-simplex, not an empirical ceiling, and the T-i argument leans on that bound; the `R_perm` companion is the empirical check, and it agrees in direction while sitting *above* `R_gene` in level.
7. **The mean-pairwise-r p-values are POST-HOC as upper-tail statements.** I pre-declared only a lower-tail p there as descriptive context; the "≤ 5.0×10⁻⁵ upper-tail exceedance" arithmetic is post-hoc and must not be promoted to a test.
8. **Multiplicity.** Two axes, no pre-declared correction, exactly as in W02g. The endothelial `p_var` = 0.031 would not survive a Bonferroni α/2 = 0.025; that arithmetic is **POST-HOC** and is a caution, not a corrected result.
9. **This does not retro-fit W02f or W02g.** W02f's lower-tail `HHI_gene` finding remains **POST-HOC** in W02f, and W02g's DISTINCT remains a claim about *this cache*. Nothing here launders either label.
10. **What was left alone.** `HHI_sample`, the SD/floor comparisons, W02d's four-route gate, W02e's endothelial verdict and W02f's sample-side negative were not re-run and are not re-issued.
11. **HEAD moved under me.** All my results were computed against files whose content I hashed (the cache hash is identical at start, runtime and end), but the checkout's HEAD advanced from `84f02dae` to `302c2b63` during the run. I performed no git write; the movement is the coordinator's.

---

## Stop condition

**Declared up front, in the frozen docstring:** *return the moment U1, U2, N1 and N2 have run to a real exit code, the pre-run / runtime / post-run sha256 of the script have been compared, and the pre-declared outcome (T, C or M) has been read off for both axes.*

**Status: MET.** All four blocks ran in a single invocation, exit code **0**; the three hashes of `w02h.py` are identical, so the result is not void; both axes read off against the pre-declared thresholds — fibro/ECM **C (CORRELATION-DEPENDENT)**, endothelial **M (MIXED)**, and **T did not fire on either axis**. I returned immediately, without extending into a transcriptome-wide universe, a correlation-conditioned null, or any further statistic.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 13** (target ~40). One of them (a structure probe) failed with an ENOSPC on the harness task temp filesystem and was re-run successfully under `/tmp/claude-0/w02h/`; both are counted.
- **Wall clock: 3 minutes 41 seconds** — `date -u` start `Tue Sep 8 03:19:38 UTC 2026`, end `Tue Sep 8 03:23:19 UTC 2026` (target ~40 minutes).
- Well inside both budgets because the stop condition was met on the first run and I did not pad.

---

## Next concrete action

**One successor, and it is the last question this substrate can answer about the null.** The remaining soft spot in the W02g/W02h pair is that "coherent marker sets are more correlated than random gene lists" is close to a tautology, so the interesting quantity is not *whether* the marker sets are flat but *whether EMC is unusual in making them flat*. That is testable here and has not been run: recompute `R_gene`, `R_var` and mean pairwise r for the **same two marker sets** on the **three comparator arms** (LGFMS n=17 subsampled to 6, desmoid n=6, fibrosarcoma n=6), and ask whether EMC's `R_gene` sits inside or outside the arm-to-arm spread of the identical statistic. W02f reported comparator `HHI_gene` values (LGFMS 0.2498, desmoid 0.3818, fibrosarcoma 0.3649) that are all *above* EMC's 0.1461 on the fibro/ECM axis, which suggests EMC may in fact be distinguishable from its own comparators on this statistic — but that comparison was descriptive and post-hoc there, and the correlation-versus-variance decomposition has never been run on the comparator arms at all. It needs no egress, no new data, and one pre-declared script.

**What must not be done next:** any variant requiring the `GSE24369` series matrix or a transcriptome-wide gene universe. Both need the uncommitted expression matrix and egress that is **denied**; naming either as a successor would be proposing a route already known to be closed.
