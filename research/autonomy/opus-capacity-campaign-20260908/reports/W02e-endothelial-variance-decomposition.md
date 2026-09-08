> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

# W02e — Is the EMC endothelial variance excess a property of the gene set or of the six samples?

## Worker

- **Worker ID:** W02e (lane 2 refill), OPUS-CAPACITY-CAMPAIGN-20260908.
- **Lane:** Lane 2 — EMC microenvironment. Decomposition of the W02c finding.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I self-report as Claude Opus 5 (`claude-opus-5`), running as Claude Code in the Anthropic Cloud remote environment. **This is a self-report and must not be treated as observed fact.** No `ANTHROPIC_MODEL` variable exists in the environment (see the literal env dump below — it is absent), so the served model is not confirmable from inside the session. The coordinator must extract the runtime model from the transcript.
- **Write isolation:** READ-ONLY on the Git tree, honoured. All execution under `/tmp/claude-0/w02e/`. **Nothing written, moved or deleted anywhere under `/home/user/Rare-cancers`. No git operation of any kind.** `git status --porcelain` was **empty at start and empty at end**.
- **`git rev-parse HEAD` actually read:** `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` at start **and** at end. The COMMON-BRIEF names the frozen read commit `92abbcb905cacf07f14b238db50d1b98f6590374`; the checkout's HEAD has advanced past it (the coordinator has been committing collected reports). The input file `research/modalities/emc-expression-panels.json` carries `generated_utc 2026-08-29T12:51:32+00:00`, unchanged from what W02b/W02c/W02d read.
- **`date -u` at start:** `Tue Sep  8 02:49:21 UTC 2026`
- **`date -u` at end:** `Tue Sep  8 02:52:05 UTC 2026`
- **Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; the end-of-run environment is unchanged):**

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
GLOBAL_AGENT_NO_PROXY=<same list as no_proxy>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 -Djavax.net.ssl.trustStorePassword=changeit -Djavax.net.ssl.trustStoreType=PKCS12 -Dhttps.proxyHost=127.0.0.1 -Dhttps.proxyPort=37223 -Dhttp.nonProxyHosts=<long list> -Djdk.http.auth.tunneling.disabledSchemes= -Djdk.http.auth.proxying.disabledSchemes=
NO_PROXY=<same list as no_proxy>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same list as no_proxy>
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

**Is the excess between-specimen variance of the EMC endothelial score (SD 0.2001 vs a 0.053–0.095 comparator band, W02c) a property of the six-gene endothelial set, or a property of the six EMC samples — and does either concentrate enough to make the excess an artifact?**

Open because W02c and W02d both name the same weakness in their own results: the finding rests on a six-tumour arm inside a 479-gene panel cache. W02c ran leave-one-specimen-out and leave-one-marker-out as *pass/fail gates* against a floor, but never decomposed the variance itself — so it can say "no single drop kills it" without being able to say *how the variance is distributed* across genes and across samples, or whether that distribution is unusual. W02d then showed the gate is discriminating (the tumour-marker axis failed on exactly this route), which makes the distributional question load-bearing rather than cosmetic.

**Substrate limit, stated up front rather than in a footnote:** the only input is a committed **gene-panel cache of 479 genes** (464 complete-case on this platform), not an expression matrix. Every quantity below is a statement about `array_percentile` values held in that cache. It is not a vessel count, not a measure of tumour biology, and not a clinical finding.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers` (all read-only):

```
rg -n -i "leverage|herfindahl|HHI|variance decomposition|per-gene contribution" --glob '!.git' -l | head -20
rg -n -i "leave-two-out|drop-2|top-1 share" --glob '!.git' -l | head
git ls-files | rg -i "decomp|leverage|variance" | head
grep -rl -i "herfindahl\|sample leverage" /tmp/claude-0/frozen-corpus/extracted/corpus/ | head
```

What they showed:

- The first `rg` returns 20 files, but **every hit is the word "leverage" in a strategic/planning sense** (`systems/graph/*.json`, `systems/views/*`, `systems/taxonomy/*`, `README.md`, `research/IDEAS.md`, `research/manuscripts/nr4a3-program-map.md`). **No hit is a statistical variance decomposition.** `herfindahl` and `HHI` return nothing.
- The second `rg` returns **nothing** — no leave-two-out or share-concentration analysis exists in the tree.
- `git ls-files` "decomp/leverage/variance" hits, each opened or headed rather than assumed: `research/manuscripts/emc_mortality_decomposition.py` / `.json` decompose **mortality after diagnosis into disease vs other-cause deaths** (clinical registry, different question, different data); `research/modalities/fep_decompose.py` is **per-residue FEP selectivity attribution**; `research/autonomy/tests/test_the_leverage_cap_is_load_bearing.py` and `S49-BLOCKER-LEVERAGE.md` are autonomy-process files; `W17b-exact-welch-variance-inversion.md` inverts committed Welch tuples for within-group variances, a different artifact and a different question. The only real neighbours are `W02c` and `W02d` themselves.
- The frozen corpus grep returns **nothing** for `herfindahl` or `sample leverage`.

**Conclusion: no exact per-gene / per-sample variance decomposition of any compartment score exists in the tree or in the frozen corpus. This is not a replay.** Confirmed against `CLOSED-WORK.md` that I touched none of: the clinical registry, PUB-ASO/Qeios frozen deliverables, the NR4A Perspective refusal, Brenca/Hofvander, the estimand-B negative, or any egress route. **No network call of any kind was made; no expression matrix was fetched; no closed route was opened.**

---

## Method / inputs

- **Input (only data source):** `/home/user/Rare-cancers/research/modalities/emc-expression-panels.json`, `generated_utc 2026-08-29T12:51:32+00:00`, 13,253,561 bytes, 479 genes. Field used: `gene_reads[<symbol>]["GSE24369_series_matrix.txt.gz"].per_sample[].array_percentile`, with `gsm` and `class`.
- **Platform:** GPL6244 (`GSE24369`), single-channel, 464 genes complete-case × 35 samples, classes `{desmoid 6, EMC 6, LGFMS 17, fibrosarcoma 6}`. **No cross-platform pooling; GPL3290 was not used at all in this report.**
- **Marker set:** unchanged from W02b/W02c — `PECAM1, VWF, CDH5, KDR, FLT1, MCAM`, all six complete-case. Score = unweighted mean of the six `array_percentile` values. SD is between-specimen, `ddof=1`.
- **Loader:** written independently in `w02e.py`; it reproduces W02c's per-specimen EMC scores and all four arm SDs exactly (see R1).
- **Tools:** Python 3.11.15, numpy 2.4.6, Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w02e`, no network. Scripts `w02e.py` and `supp.py`, both returned inline below.
- **Order of operations, which is the point of this task:** the complete pre-declaration (decomposition, statistic, thresholds, artifact rule) was written into `w02e.py`'s docstring, the file was hashed, and **only then** was it executed. Pre-run hash `a39c1a11e176084dec531bbca0211434eb1a17f8bebb244cce0013c332aae691` at `02:51:10 UTC`; post-run hash **identical** at `02:51:19 UTC` (verbatim output in Validation evidence). The script prints each threshold beside its own result.

### The pre-declaration, quoted from the frozen docstring

**Decomposition (both exact, both summing to the target by construction):**

- **(A) Per-gene.** `Var(s) = Σ_i C_i` where `C_i = (1/k)·Cov(g_i, s)`, ddof=1. Gene share `f_i = C_i / Var(s)`.
- **(B) Per-sample.** `Var(s) = (1/(n−1))·Σ_j (s_j − s̄)²`. Sample leverage `l_j = (s_j − s̄)² / Σ(s − s̄)²`.

**Statistic:** Herfindahl-Hirschman concentration index of each share vector — `HHI_gene = Σf_i²`, `HHI_sample = Σl_j²`. Perfectly even at k=n=6 is `1/6 = 0.16667`; maximum is 1. Top-1 and top-2 cumulative shares reported alongside.

**Thresholds (`FLOOR = 0.0949`, the largest comparator-arm SD, the same ceiling W02c used):**

| rule | fires when | meaning |
|---|---|---|
| **T1 SAMPLE-DRIVEN** | top-1 sample leverage ≥ 0.50 **AND** that specimen's leave-one-out SD ≤ 0.0949 | one specimen carries it; **W02c substantially weakened, report plainly** |
| **T2 GENE-DRIVEN** | top-1 gene share ≥ 0.50 **AND** that gene's leave-one-out 5-gene SD ≤ 0.0949 | one gene carries it; artifact of panel composition |
| **T3 DISTRIBUTED** | neither T1 nor T2 fires | property of the set acting across the samples |
| **T4** | T1 and T2 both fire | jointly degenerate; not a defensible signal |

**What would make it an artifact:** A1 = T1 fires; A2 = T2 fires; **A3 SHAPE CONTROL** = if EMC's `HHI_sample` lies inside an n-matched null (20,000 six-specimen subsamples of the real 17-specimen LGFMS arm, upper-tail p > 0.05) **and** EMC's `HHI_gene` lies within the range spanned by the two n=6 comparator arms, then **the concentration *shape* is ordinary and only the magnitude differs — and that must be said explicitly**; A4 = the converse.

---

## Result

### R1 — The committed values every number below is derived from

EMC endothelial `array_percentile`, GPL6244, printed in full (6 genes × 6 specimens = 36 committed numbers). **Row class: PRIMARY** — these are values read verbatim from the committed cache, not derived.

| gene | GSM600934 | GSM600935 | GSM600936 | GSM600937 | GSM600938 | GSM600939 |
|---|---|---|---|---|---|---|
| PECAM1 | 0.2593 | 0.1151 | 0.7041 | 0.2148 | 0.2240 | 0.3617 |
| VWF | 0.6473 | 0.3451 | 0.8703 | 0.3333 | 0.3153 | 0.6458 |
| CDH5 | 0.4802 | 0.3472 | 0.6685 | 0.3413 | 0.3723 | 0.5973 |
| KDR | 0.6794 | 0.2383 | 0.8271 | 0.2025 | 0.2726 | 0.8335 |
| FLT1 | 0.4884 | 0.1375 | 0.8672 | 0.1108 | 0.1498 | 0.5349 |
| MCAM | 0.5568 | 0.6108 | 0.7464 | 0.6507 | 0.4732 | 0.6461 |
| **SCORE** | **0.5186** | **0.2990** | **0.7806** | **0.3089** | **0.3012** | **0.6032** |

`Var(score) = 0.040051`, `SD = 0.2001`, n = 6 — reproducing W02c's per-specimen table exactly to 4 dp with an independent loader. **Row class: PREDICTION** (the score is a derived composition statement, not a measurement).

### R2 — Per-gene contribution to the EMC arm's score variance (exact, ranked)

All rows **PREDICTION**. Units: `array_percentile²` for `C_i`; `f_i` dimensionless.

| rank | gene | `C_i = Cov(g_i,s)/k` | share `f_i` | cumulative | 5-gene SD without it |
|---|---|---|---|---|---|
| 1 | FLT1 | 0.010031 | 0.2505 | 0.2505 | 0.1801 |
| 2 | KDR | 0.009529 | 0.2379 | 0.4884 | 0.1841 |
| 3 | VWF | 0.007545 | 0.1884 | 0.6768 | 0.1950 |
| 4 | PECAM1 | 0.006335 | 0.1582 | 0.8349 | 0.2029 |
| 5 | CDH5 | 0.004577 | 0.1143 | 0.9492 | 0.2128 |
| 6 | MCAM | 0.002034 | 0.0508 | 1.0000 | 0.2284 |

Identity check: `ΣC_i = 0.040051` against `Var = 0.040051`, residual `6.94e-18` — the decomposition is exact, not approximate.

**`HHI_gene = 0.1955`** against a perfectly even 0.16667. **Top-1 share 0.2505; top-2 cumulative 0.4884.** No gene approaches the 0.50 pre-declared threshold. `MCAM`, the marker W02b flagged as pericyte-ambiguous, contributes the *least* (5.1%) — consistent with W02c's independent finding by a different route.

### R3 — Per-sample leverage on the EMC arm's score variance (exact, ranked)

All rows **PREDICTION**.

| rank | GSM | score | deviation | leverage `l_j` | cumulative | SD without it |
|---|---|---|---|---|---|---|
| 1 | **GSM600936** | 0.7806 | +0.3120 | **0.4862** | 0.4862 | **0.1444** |
| 2 | GSM600935 | 0.2990 | −0.1696 | 0.1436 | 0.6298 | 0.2036 |
| 3 | GSM600938 | 0.3012 | −0.1674 | 0.1399 | 0.7697 | 0.2041 |
| 4 | GSM600937 | 0.3089 | −0.1597 | 0.1273 | 0.8970 | 0.2059 |
| 5 | GSM600939 | 0.6032 | +0.1346 | 0.0905 | 0.9875 | 0.2112 |
| 6 | GSM600934 | 0.5186 | +0.0500 | 0.0125 | 1.0000 | 0.2221 |

`Σl_j = 1.000000` exactly. **`HHI_sample = 0.3011`** against a perfectly even 0.16667. **Top-1 leverage 0.4862 — GSM600936 alone accounts for 48.6% of the arm's total sum of squares.**

**This is the closest call in the report and I am not smoothing it.** 0.4862 sits 1.4 percentage points below the pre-declared 0.50, and I am not adjusting the threshold to make it clear. But the rule is a *conjunction*: dropping GSM600936 leaves SD 0.1444, which is **1.52× the 0.0949 floor**, so limb (ii) fails decisively even had limb (i) fired. Half the variance living in one of six specimens is exactly what "n = 6" means arithmetically; it is not by itself evidence of an outlier.

### R4 — Shape control: the identical decomposition on the comparator arms

All rows **PREDICTION**.

| arm | n | SD | `HHI_gene` | top-1 gene | `HHI_sample` | top-1 sample | min LOO SD |
|---|---|---|---|---|---|---|---|
| **EMC** | 6 | **0.2001** | **0.1955** | 0.2505 | **0.3011** | 0.4862 | 0.1444 |
| LGFMS | 17 | 0.0949 | 0.2051 | 0.2739 | 0.1655* | 0.3235* | 0.0794 |
| desmoid fibromatosis | 6 | 0.0558 | 0.2399 | 0.3080 | **0.4313** | **0.5866** | 0.0339 |
| fibrosarcoma | 6 | 0.0532 | 0.1954 | 0.2661 | **0.3586** | **0.5501** | 0.0347 |

\* `HHI_sample` is mechanically n-dependent (even value = 1/n), so the LGFMS row is **not** directly comparable and is used only through the n-matched null in R5.

n-matched null, 20,000 draws of six specimens from the seventeen **real** LGFMS tumours:

| statistic | null mean | p50 | p95 | max | EMC observed | upper-tail p |
|---|---|---|---|---|---|---|
| `HHI_sample` | 0.3613 | 0.3410 | 0.5396 | 0.6946 | **0.3011** | **0.6794** |
| `HHI_gene` | 0.2125 | 0.2089 | 0.2571 | 0.5145 | **0.1955** | **0.7922** |

**The shape control fires, and its result runs against the interesting reading, so I lead with it.** EMC's concentration structure is not merely ordinary — on both axes it is **less concentrated than the comparators**. `HHI_sample` 0.3011 sits *below* the n-matched LGFMS median (0.3410) and below both n=6 comparator arms (desmoid 0.4313, fibrosarcoma 0.3586). Desmoid's top specimen carries 58.7% of its arm's sum of squares and fibrosarcoma's carries 55.0% — **both exceed the 0.50 threshold that EMC does not reach.** `HHI_gene` 0.1955 is likewise the lowest of the four arms and below the null median.

**So the answer to the framing question "is the *shape* special?" is a clear no, and per the pre-declared A3 I must state it explicitly: the concentration structure of the EMC endothelial spread is not distinguishable from — and is if anything flatter than — what the comparator arms show. Only the magnitude differs.** A decomposition-shape argument cannot be used to support the W02c finding. It also cannot be used against it, because the comparators fail the same shape test more severely.

### R5 — The explicit "one or two samples" test (descriptive supplement, no new threshold)

| arm | n | SD | top-1 leverage | top-2 cumulative | worst-case drop-2 SD | ≤ FLOOR? |
|---|---|---|---|---|---|---|
| **EMC** | 6 | 0.2001 | 0.4862 | 0.6298 | **0.1079** | **False** |
| desmoid | 6 | 0.0558 | 0.5866 | 0.8568 | 0.0258 | True |
| fibrosarcoma | 6 | 0.0532 | 0.5501 | 0.7247 | 0.0269 | True |

"Worst-case drop-2" is the **minimum** SD over all 15 ways of deleting two of the six specimens — a deliberately hostile test, not a pre-declared gate. EMC's full sorted drop-2 SD vector: `[0.1079, 0.1502, 0.1517, 0.1524, 0.1545, 0.1959, 0.1991, 0.2000, 0.2259, 0.2265, 0.2284, 0.2348, 0.2354, 0.2375, 0.2388]`. Deleting the two highest-leverage specimens (GSM600936 + GSM600935) gives 0.1517.

**Even under adversarial deletion of a third of the arm, the EMC endothelial SD stays at 0.1079 — 1.14× the top of the comparator band, and above every comparator arm's undeleted SD.** The two n=6 comparator arms both fall below the floor under the same deletion. All rows **PREDICTION**.

### R6 — Verdict against the pre-declared thresholds

| rule | limb (i) | limb (ii) | outcome |
|---|---|---|---|
| **T1 SAMPLE-DRIVEN** | top-1 leverage 0.4862 ≥ 0.50? **No** | LOO SD 0.1444 ≤ 0.0949? **No** | **does not fire** |
| **T2 GENE-DRIVEN** | top-1 gene share 0.2505 ≥ 0.50? **No** | 5-gene SD 0.1801 ≤ 0.0949? **No** | **does not fire** |
| **T3 DISTRIBUTED** | — | — | **YES** |
| **T4 jointly degenerate** | — | — | No |
| **A3 shape control** | `HHI_sample` p = 0.6794 > 0.05 → inside null | `HHI_gene` 0.1955 ∈ [0.1954, 0.2399] → inside | **SHAPE ORDINARY** |
| **A4** | `HHI_sample` 0.3011 > null p95 0.5396? | — | **No** |

> **VERDICT.** Against the thresholds frozen before the run: **the excess is neither gene-driven nor sample-driven. It is DISTRIBUTED (T3)** — no single endothelial gene contributes more than 25.1% of the arm's score variance, no single specimen more than 48.6% of its sum of squares, and neither the largest gene nor the largest specimen can be removed to bring the SD near the comparator band. Deleting the two most influential specimens still leaves it above the band.
>
> **I was prepared to report "this is one or two samples" and the pre-declared rule did not permit it.** The nearest thing to that finding is real and stated plainly: **GSM600936 alone carries 48.6% of the arm's variance**, one and a half points short of the threshold, and a reader who prefers a 0.45 threshold to my 0.50 should know the leave-one-out SD is 0.1444 either way — still 1.52× the floor.
>
> **The finding that genuinely qualifies W02c is the shape control (R4), and it is a negative.** EMC's concentration structure is *ordinary and in fact flatter* than the comparator arms'. **The excess variance is a matter of magnitude only; its shape carries no information.** Any future argument of the form "the EMC spread is distributed across specimens in a distinctive way" is refuted by this table.
>
> **This does not overturn W02c, and it does not strengthen it either.** It removes one specific way the W02c result could have been wrong (a hidden concentration in one gene or one sample) and adds no new support. The n = 6, single-array, panel-cache limit that both W02c and W02d name is untouched by anything here.

**No clinical claim.** Every quantity is a **PREDICTION about the composition of a committed gene-panel cache**, never a measurement of vessels, vasculature, perfusion, or any patient-level property. Nothing here supports a statement about EMC vasculature, about treatment, or about any patient. There is no wet lab.

---

## Validation evidence

**RUN.** Environment for all rows: Linux 6.18.44-fc-v24 x86_64, Python 3.11.15, numpy 2.4.6, scipy 1.17.1, cwd `/tmp/claude-0/w02e`, no network.

| # | command | exit code | key verbatim output |
|---|---|---|---|
| 1 | `date -u` (start) | 0 | `Tue Sep  8 02:49:21 UTC 2026` |
| 2 | `git rev-parse HEAD` (start) | 0 | `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` |
| 3 | `git status --porcelain` (start) | 0 | **empty output** |
| 4 | `python3 -c "import numpy,scipy,sys;print(...)"` | 0 | `numpy 2.4.6 scipy 1.17.1 python 3.11.15` |
| 5 | `sha256sum w02e.py` **before the run**, 02:51:10 UTC | 0 | `a39c1a11e176084dec531bbca0211434eb1a17f8bebb244cce0013c332aae691  w02e.py` |
| 6 | `cd /tmp/claude-0/w02e && python3 w02e.py 2>&1 \| tee out.txt` | **0** (`EXIT=0` via `PIPESTATUS`) | full output below |
| 7 | `sha256sum w02e.py` **after the run**, 02:51:19 UTC | 0 | `a39c1a11e176084dec531bbca0211434eb1a17f8bebb244cce0013c332aae691  w02e.py` — **identical to #5** |
| 8 | `sha256sum supp.py` | 0 | `5a366eb3594c94b91ed0308a25da2ab646fb6832b6ddd9cd27b9ff116522a3c0` |
| 9 | `cd /tmp/claude-0/w02e && python3 supp.py 2>&1 \| tee supp.txt` | **0** | full output below |
| 10 | `git status --porcelain` (end) | 0 | **empty output** |
| 11 | `git rev-parse HEAD` (end) | 0 | `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` — unchanged |
| 12 | `date -u` (end) | 0 | `Tue Sep  8 02:52:05 UTC 2026` |

**The hash identity in rows 5 and 7 is the pre-declaration guarantee: the file carrying the thresholds was byte-identical before and after execution, so no threshold was written or altered after seeing a result.** `/tmp/claude-0/w02e/` contains exactly four files: `w02e.py`, `supp.py`, `out.txt`, `supp.txt`.

Verbatim output of run #6 (`out.txt`, complete):

```
PLATFORM GSE24369_series_matrix.txt.gz | complete-case 464 genes x 35 samples | {'desmoid_fibromatosis': 6, 'EMC': 6, 'LGFMS': 17, 'fibrosarcoma': 6}
endothelial markers complete-case: ['PECAM1', 'VWF', 'CDH5', 'KDR', 'FLT1', 'MCAM']

=== COMMITTED VALUES: EMC endothelial array_percentile matrix (GPL6244) ===
gene         GSM600934   GSM600935   GSM600936   GSM600937   GSM600938   GSM600939
PECAM1          0.2593      0.1151      0.7041      0.2148      0.2240      0.3617
VWF             0.6473      0.3451      0.8703      0.3333      0.3153      0.6458
CDH5            0.4802      0.3472      0.6685      0.3413      0.3723      0.5973
KDR             0.6794      0.2383      0.8271      0.2025      0.2726      0.8335
FLT1            0.4884      0.1375      0.8672      0.1108      0.1498      0.5349
MCAM            0.5568      0.6108      0.7464      0.6507      0.4732      0.6461
SCORE           0.5186      0.2990      0.7806      0.3089      0.3012      0.6032

=== (A) PER-GENE CONTRIBUTION TO THE EMC ARM'S SCORE VARIANCE (exact decomposition) ===
Var(score) = 0.040051   SD = 0.2001   n=6 k=6
gene          C_i=Cov/k  share f_i        cum 5-gene SD w/o it
FLT1           0.010031     0.2505     0.2505           0.1801
KDR            0.009529     0.2379     0.4884           0.1841
VWF            0.007545     0.1884     0.6768           0.1950
PECAM1         0.006335     0.1582     0.8349           0.2029
CDH5           0.004577     0.1143     0.9492           0.2128
MCAM           0.002034     0.0508     1.0000           0.2284
sum of C_i = 0.040051  (equals Var = 0.040051 ; residual 6.94e-18)
HHI_gene = 0.1955  (even = 0.16667)   top1 share = 0.2505   top2 cum = 0.4884

=== (B) PER-SAMPLE LEVERAGE ON THE EMC ARM'S SCORE VARIANCE (exact decomposition) ===
GSM               score          dev   leverage        cum    SD w/o it
GSM600936        0.7806       0.3120     0.4862     0.4862       0.1444
GSM600935        0.2990      -0.1696     0.1436     0.6298       0.2036
GSM600938        0.3012      -0.1674     0.1399     0.7697       0.2041
GSM600937        0.3089      -0.1597     0.1273     0.8970       0.2059
GSM600939        0.6032       0.1346     0.0905     0.9875       0.2112
GSM600934        0.5186       0.0500     0.0125     1.0000       0.2221
sum of leverages = 1.000000
HHI_sample = 0.3011  (even = 0.16667)   top1 share = 0.4862   top2 cum = 0.6298

=== (C) SHAPE CONTROL: same decomposition on the comparator arms ===
arm                         n       SD   HHI_gene  top1_gene   HHI_samp  top1_samp   min_LOO_SD
EMC                         6   0.2001     0.1955     0.2505     0.3011     0.4862       0.1444
LGFMS                      17   0.0949     0.2051     0.2739     0.1655     0.3235       0.0794
desmoid_fibromatosis        6   0.0558     0.2399     0.3080     0.4313     0.5866       0.0339
fibrosarcoma                6   0.0532     0.1954     0.2661     0.3586     0.5501       0.0347
note: HHI_sample is mechanically n-dependent (even value = 1/n), so LGFMS (n=17) is NOT
comparable directly and is used only via the n=6 subsample null below.

=== (D) n-MATCHED NULL: HHI_sample of 6-specimen subsamples of the real LGFMS arm ===
LGFMS n=6 subsample HHI_sample: mean=0.3613 p50=0.3410 p95=0.5396 max=0.6946 | EMC=0.3011 | upper-tail p=0.6794
LGFMS n=6 subsample HHI_gene  : mean=0.2125 p50=0.2089 p95=0.2571 max=0.5145 | EMC=0.1955 | upper-tail p=0.7922

=== (E) VERDICT AGAINST THE PRE-DECLARED THRESHOLDS ===
T1 SAMPLE-DRIVEN : top1 leverage 0.4862 >= 0.50 ? False | its LOO SD 0.1444 <= 0.0949 ? False -> does not fire
T2 GENE-DRIVEN   : top1 gene share 0.2505 >= 0.50 ? False | its 5-gene SD 0.1801 <= 0.0949 ? False -> does not fire
T3 DISTRIBUTED   : YES - neither T1 nor T2 fires
T4 jointly degenerate: False
A3 SHAPE CONTROL : HHI_sample inside n-matched LGFMS null (p=0.6794 > 0.05)? True ; HHI_gene inside n=6 comparator range [0.1954, 0.2399]? True -> shape ORDINARY
A4 HHI_sample above LGFMS n-matched p95 (0.5396)? False

DONE
```

Verbatim output of run #9 (`supp.txt`, complete):

```
arm                         n       SD   top1_lev   top2_cum drop-2 SD(min) drop-2 <= FLOOR?
EMC                         6   0.2001     0.4862     0.6298         0.1079          False
desmoid_fibromatosis        6   0.0558     0.5866     0.8568         0.0258           True
fibrosarcoma                6   0.0532     0.5501     0.7247         0.0269           True

EMC drop-the-two-highest-leverage (GSM600936 + GSM600935) SD = 0.1517
EMC all pairwise drop-2 SDs, sorted: [0.1079 0.1502 0.1517 0.1524 0.1545 0.1959 0.1991 0.2    0.2259 0.2265
 0.2284 0.2348 0.2354 0.2375 0.2388]
```

**PROPOSED (NOT RUN)** — declared, not claimed:

- The same decomposition against the full `GSE24369` series matrix rather than the 464-gene panel cache. **Not run:** the matrix is not committed and fetching it requires egress, which is blanket-denied. This is the substrate limit, not a scheduling gap.
- A bootstrap confidence interval on `HHI_sample` itself. **Not run:** at n = 6 a bootstrap resamples the same six values and would report the arm's own arithmetic back as if it were sampling uncertainty. The n-matched LGFMS subsample null in R4 is the honest substitute and it was run.
- The same decomposition on the fibro/ECM axis that W02d found survives its battery. **Not run:** out of this task's declared scope; named as the successor below.

### Code, returned inline (nothing written into the tree)

`/tmp/claude-0/w02e/w02e.py` — sha256 `a39c1a11e176084dec531bbca0211434eb1a17f8bebb244cce0013c332aae691`, unchanged across the run:

```python
"""W02e - is the EMC endothelial score's excess between-specimen variance a property of the
GENE SET or of the SIX SAMPLES?  READ-ONLY on the repository; executes only under /tmp/claude-0/w02e/.

=========================  PRE-DECLARATION (frozen before any computation)  =========================
Written 2026-09-08 before the script was executed. sha256 of this file is recorded before the run
and re-checked after the run; the two must match.

SUBSTRATE LIMIT: the only input is a committed 479-GENE PANEL CACHE
(research/modalities/emc-expression-panels.json), not an expression matrix. Every number below is a
statement about that cache's array_percentile values. Nothing here is a vessel measurement, a
tumour-biology claim, or a clinical finding.

--- The decomposition ---
The arm score is s_j = (1/k) * sum_i g_ij over k marker genes and n specimens.
(A) EXACT GENE DECOMPOSITION.  Var(s) = sum_i C_i  with  C_i = (1/k) * Cov(g_i, s)  (ddof=1).
    This is exact and the C_i sum to Var(s) by construction. Gene share  f_i = C_i / Var(s).
(B) EXACT SAMPLE DECOMPOSITION.  Var(s) = (1/(n-1)) * sum_j (s_j - sbar)^2. Sample leverage share
    l_j = (s_j - sbar)^2 / sum_j (s_j - sbar)^2. The l_j sum to 1 by construction.
    Reported alongside the leave-one-out SD, SD_-j, and the ratio SD_-j / SD.

--- The statistic ---
Concentration is measured by the Herfindahl-Hirschman index of the shares:
    HHI_gene   = sum_i f_i^2     (k=6 -> perfectly even = 1/6 = 0.16667, maximum = 1)
    HHI_sample = sum_j l_j^2     (n=6 -> perfectly even = 1/6 = 0.16667, maximum = 1)
Also reported: top-1 share, and top-2 cumulative share, for each decomposition.

--- The thresholds (declared now, not adjusted later) ---
FLOOR = 0.0949, the largest comparator-arm endothelial SD on GPL6244 (LGFMS, n=17), the same
comparator ceiling W02c used. The comparator band is 0.053-0.095.

T1 SAMPLE-DRIVEN if BOTH:
      (i) top-1 sample leverage share l_(1) >= 0.50, AND
      (ii) the corresponding leave-one-out SD_-j <= FLOOR (0.0949).
   -> The excess is a property of one specimen. This substantially weakens W02c and must be
      reported plainly as such.
T2 GENE-DRIVEN if BOTH:
      (i) top-1 gene contribution share f_(1) >= 0.50, AND
      (ii) the leave-that-gene-out 5-gene EMC SD <= FLOOR (0.0949).
   -> The excess is a property of one member of the gene set, not of the endothelial axis.
T3 DISTRIBUTED (the excess is a property of the SET acting coherently across the SAMPLES) if
   NEITHER T1 NOR T2 fires, i.e. no single gene and no single specimen carries it past the floor.
T4 If T1 and T2 both fire, the finding is reported as jointly degenerate and treated as NOT a
   defensible signal.

--- What would make the excess an ARTIFACT rather than a signal ---
A1 T1 fires (one specimen carries it) -> artifact of the six samples. W02c's verdict is weakened.
A2 T2 fires (one gene carries it) -> artifact of panel composition.
A3 SHAPE CONTROL. The same decomposition is run on the comparator arms (LGFMS n=17, desmoid n=6,
   fibrosarcoma n=6). Because HHI_sample depends on n, LGFMS is compared ONLY through 20000
   n=6 subsamples of its 17 real specimens (an n-matched null). If EMC's HHI_sample lies INSIDE
   that null (empirical two-sided position, i.e. its upper-tail p > 0.05) AND EMC's HHI_gene lies
   within the range spanned by the two n=6 comparator arms, then EMC's concentration STRUCTURE is
   not special: the SHAPE of the spread is ordinary and only its MAGNITUDE differs. That must be
   stated explicitly, because a battery that shows the same shape everywhere is not diagnostic of
   shape.
A4 CONVERSELY, if EMC's HHI_sample sits ABOVE the n-matched LGFMS null's 95th percentile, the
   concentration is unusual and T1's threshold decides whether that concentration is enough to
   overturn the finding.

--- Committed values every number is derived from ---
The six EMC per-specimen, per-gene array_percentile values (6 genes x 6 specimens = 36 numbers)
are printed in full so every derived quantity can be recomputed by hand.
=====================================================================================================
"""
import json, collections
import numpy as np

SRC = "/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
PLAT = "GSE24369_series_matrix.txt.gz"          # GPL6244 single-channel; no cross-platform pooling
ENDO = ["PECAM1", "VWF", "CDH5", "KDR", "FLT1", "MCAM"]
FLOOR = 0.0949
RNG = np.random.default_rng(20260908)

d = json.load(open(SRC))
gr = d["gene_reads"]
genes, classes = {}, {}
for g, v in gr.items():
    pv = v.get(PLAT)
    if not pv or not pv.get("readable"):
        continue
    row = {}
    for s in (pv.get("per_sample") or []):
        classes[s["gsm"]] = s["class"]
        if s.get("array_percentile") is not None:
            row[s["gsm"]] = s["array_percentile"]
    if row:
        genes[g] = row
S = sorted(classes)
names = [g for g in genes if all(x in genes[g] for x in S)]
M = {g: np.array([genes[g][x] for x in S]) for g in names}
print("PLATFORM %s | complete-case %d genes x %d samples | %s"
      % (PLAT, len(names), len(S), dict(collections.Counter(classes.values()))))
print("endothelial markers complete-case:", [g for g in ENDO if g in M])
assert all(g in M for g in ENDO)

ARMS = ["EMC", "LGFMS", "desmoid_fibromatosis", "fibrosarcoma"]
idx = {a: [i for i, x in enumerate(S) if classes[x] == a] for a in ARMS}
gsm = {a: [S[i] for i in idx[a]] for a in ARMS}


def score(ii, marks=ENDO):
    return np.mean([M[g][ii] for g in marks], axis=0)


# ---------- committed values, printed in full ----------
print("\n=== COMMITTED VALUES: EMC endothelial array_percentile matrix (GPL6244) ===")
hdr = "gene      " + "".join("%12s" % s for s in gsm["EMC"])
print(hdr)
for g in ENDO:
    print("%-10s" % g + "".join("%12.4f" % M[g][i] for i in idx["EMC"]))
print("%-10s" % "SCORE" + "".join("%12.4f" % v for v in score(idx["EMC"])))


def decompose(ii, marks=ENDO):
    k = len(marks)
    G = np.array([M[g][ii] for g in marks])          # k x n
    s = G.mean(axis=0)
    n = len(s)
    var = s.var(ddof=1)
    # gene contributions C_i = (1/k) Cov(g_i, s)
    C = np.array([np.cov(G[i], s, ddof=1)[0, 1] / k for i in range(k)])
    f = C / var
    # sample leverages
    ss = (s - s.mean()) ** 2
    l = ss / ss.sum()
    loo_sd = np.array([np.delete(s, j).std(ddof=1) for j in range(n)])
    lomo_sd = np.array([np.mean([M[g][ii] for g in marks if g != marks[i]], axis=0).std(ddof=1)
                        for i in range(k)])
    return dict(s=s, var=var, sd=np.sqrt(var), C=C, f=f, l=l, loo_sd=loo_sd, lomo_sd=lomo_sd,
                hhi_g=float((f ** 2).sum()), hhi_s=float((l ** 2).sum()), n=n, k=k)


R = {a: decompose(idx[a]) for a in ARMS}

print("\n=== (A) PER-GENE CONTRIBUTION TO THE EMC ARM'S SCORE VARIANCE (exact decomposition) ===")
e = R["EMC"]
print("Var(score) = %.6f   SD = %.4f   n=%d k=%d" % (e["var"], e["sd"], e["n"], e["k"]))
print("%-8s %14s %10s %10s %16s" % ("gene", "C_i=Cov/k", "share f_i", "cum", "5-gene SD w/o it"))
order = np.argsort(-e["f"])
cum = 0.0
for i in order:
    cum += e["f"][i]
    print("%-8s %14.6f %10.4f %10.4f %16.4f"
          % (ENDO[i], e["C"][i], e["f"][i], cum, e["lomo_sd"][i]))
print("sum of C_i = %.6f  (equals Var = %.6f ; residual %.2e)"
      % (e["C"].sum(), e["var"], abs(e["C"].sum() - e["var"])))
print("HHI_gene = %.4f  (even = %.5f)   top1 share = %.4f   top2 cum = %.4f"
      % (e["hhi_g"], 1 / e["k"], e["f"][order[0]], e["f"][order[0]] + e["f"][order[1]]))

print("\n=== (B) PER-SAMPLE LEVERAGE ON THE EMC ARM'S SCORE VARIANCE (exact decomposition) ===")
print("%-12s %10s %12s %10s %10s %12s" % ("GSM", "score", "dev", "leverage", "cum", "SD w/o it"))
o2 = np.argsort(-e["l"])
cum = 0.0
for j in o2:
    cum += e["l"][j]
    print("%-12s %10.4f %12.4f %10.4f %10.4f %12.4f"
          % (gsm["EMC"][j], e["s"][j], e["s"][j] - e["s"].mean(), e["l"][j], cum, e["loo_sd"][j]))
print("sum of leverages = %.6f" % e["l"].sum())
print("HHI_sample = %.4f  (even = %.5f)   top1 share = %.4f   top2 cum = %.4f"
      % (e["hhi_s"], 1 / e["n"], e["l"][o2[0]], e["l"][o2[0]] + e["l"][o2[1]]))

print("\n=== (C) SHAPE CONTROL: same decomposition on the comparator arms ===")
print("%-24s %4s %8s %10s %10s %10s %10s %12s"
      % ("arm", "n", "SD", "HHI_gene", "top1_gene", "HHI_samp", "top1_samp", "min_LOO_SD"))
for a in ARMS:
    r = R[a]
    print("%-24s %4d %8.4f %10.4f %10.4f %10.4f %10.4f %12.4f"
          % (a, r["n"], r["sd"], r["hhi_g"], r["f"].max(), r["hhi_s"], r["l"].max(),
             r["loo_sd"].min()))
print("note: HHI_sample is mechanically n-dependent (even value = 1/n), so LGFMS (n=17) is NOT")
print("comparable directly and is used only via the n=6 subsample null below.")

print("\n=== (D) n-MATCHED NULL: HHI_sample of 6-specimen subsamples of the real LGFMS arm ===")
L = R["LGFMS"]["s"]
B = 20000
hs = np.empty(B)
hg = np.empty(B)
Lg = np.array([M[g][idx["LGFMS"]] for g in ENDO])
for b in range(B):
    pick = RNG.choice(len(L), 6, replace=False)
    ssb = (L[pick] - L[pick].mean()) ** 2
    hs[b] = ((ssb / ssb.sum()) ** 2).sum()
    Gb = Lg[:, pick]
    sb = Gb.mean(axis=0)
    vb = sb.var(ddof=1)
    Cb = np.array([np.cov(Gb[i], sb, ddof=1)[0, 1] / 6 for i in range(6)])
    hg[b] = ((Cb / vb) ** 2).sum()
p_s = float((hs >= e["hhi_s"]).mean())
p_g = float((hg >= e["hhi_g"]).mean())
print("LGFMS n=6 subsample HHI_sample: mean=%.4f p50=%.4f p95=%.4f max=%.4f | EMC=%.4f | upper-tail p=%.4f"
      % (hs.mean(), np.median(hs), np.percentile(hs, 95), hs.max(), e["hhi_s"], p_s))
print("LGFMS n=6 subsample HHI_gene  : mean=%.4f p50=%.4f p95=%.4f max=%.4f | EMC=%.4f | upper-tail p=%.4f"
      % (hg.mean(), np.median(hg), np.percentile(hg, 95), hg.max(), e["hhi_g"], p_g))

print("\n=== (E) VERDICT AGAINST THE PRE-DECLARED THRESHOLDS ===")
t1_i = e["l"].max() >= 0.50
t1_ii = e["loo_sd"][int(np.argmax(e["l"]))] <= FLOOR
T1 = t1_i and t1_ii
t2_i = e["f"].max() >= 0.50
t2_ii = e["lomo_sd"][int(np.argmax(e["f"]))] <= FLOOR
T2 = t2_i and t2_ii
print("T1 SAMPLE-DRIVEN : top1 leverage %.4f >= 0.50 ? %s | its LOO SD %.4f <= %.4f ? %s -> %s"
      % (e["l"].max(), t1_i, e["loo_sd"][int(np.argmax(e["l"]))], FLOOR, t1_ii, "FIRES" if T1 else "does not fire"))
print("T2 GENE-DRIVEN   : top1 gene share %.4f >= 0.50 ? %s | its 5-gene SD %.4f <= %.4f ? %s -> %s"
      % (e["f"].max(), t2_i, e["lomo_sd"][int(np.argmax(e["f"]))], FLOOR, t2_ii, "FIRES" if T2 else "does not fire"))
print("T3 DISTRIBUTED   : %s" % ("YES - neither T1 nor T2 fires" if not (T1 or T2) else "no"))
print("T4 jointly degenerate: %s" % (T1 and T2))
a3_s = p_s > 0.05
lo, hi = sorted([R["desmoid_fibromatosis"]["hhi_g"], R["fibrosarcoma"]["hhi_g"]])
a3_g = lo <= e["hhi_g"] <= hi
print("A3 SHAPE CONTROL : HHI_sample inside n-matched LGFMS null (p=%.4f > 0.05)? %s ; "
      "HHI_gene inside n=6 comparator range [%.4f, %.4f]? %s -> shape %s"
      % (p_s, a3_s, lo, hi, a3_g, "ORDINARY" if (a3_s and a3_g) else "see report"))
print("A4 HHI_sample above LGFMS n-matched p95 (%.4f)? %s" % (np.percentile(hs, 95), e["hhi_s"] > np.percentile(hs, 95)))
print("\nDONE")
```

`/tmp/claude-0/w02e/supp.py` — sha256 `5a366eb3594c94b91ed0308a25da2ab646fb6832b6ddd9cd27b9ff116522a3c0`:

```python
"""W02e supplement - DESCRIPTIVE ONLY. No new threshold is declared here; the verdict rule stays
exactly T1/T2/T3/A3 as frozen in w02e.py. This only answers the explicit 'is this one or TWO
samples?' framing by reporting top-2 cumulative leverage and the drop-the-two-highest-leverage SD
for EMC and for the two n=6 comparator arms, on the same committed panel-cache values."""
import json, collections, itertools
import numpy as np
SRC="/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
PLAT="GSE24369_series_matrix.txt.gz"; ENDO=["PECAM1","VWF","CDH5","KDR","FLT1","MCAM"]; FLOOR=0.0949
d=json.load(open(SRC)); gr=d["gene_reads"]; genes={}; classes={}
for g,v in gr.items():
    pv=v.get(PLAT)
    if not pv or not pv.get("readable"): continue
    row={}
    for s in (pv.get("per_sample") or []):
        classes[s["gsm"]]=s["class"]
        if s.get("array_percentile") is not None: row[s["gsm"]]=s["array_percentile"]
    if row: genes[g]=row
S=sorted(classes); names=[g for g in genes if all(x in genes[g] for x in S)]
M={g:np.array([genes[g][x] for x in S]) for g in names}
print("%-24s %4s %8s %10s %10s %14s %14s"%("arm","n","SD","top1_lev","top2_cum","drop-2 SD(min)","drop-2 <= FLOOR?"))
for a in ["EMC","desmoid_fibromatosis","fibrosarcoma"]:
    ii=[i for i,x in enumerate(S) if classes[x]==a]
    s=np.mean([M[g][ii] for g in ENDO],axis=0); ss=(s-s.mean())**2; l=ss/ss.sum()
    o=np.argsort(-l); d2=min(np.delete(s,list(c)).std(ddof=1) for c in itertools.combinations(range(len(s)),2))
    print("%-24s %4d %8.4f %10.4f %10.4f %14.4f %14s"%(a,len(s),s.std(ddof=1),l[o[0]],l[o[0]]+l[o[1]],d2,d2<=FLOOR))
ii=[i for i,x in enumerate(S) if classes[x]=="EMC"]; g6=[S[i] for i in ii]
s=np.mean([M[g][ii] for g in ENDO],axis=0)
print("\nEMC drop-the-two-highest-leverage (GSM600936 + GSM600935) SD = %.4f"
      %(np.delete(s,[list(g6).index("GSM600936"),list(g6).index("GSM600935")]).std(ddof=1)))
print("EMC all pairwise drop-2 SDs, sorted: %s"%np.round(sorted(np.delete(s,list(c)).std(ddof=1)
      for c in itertools.combinations(range(6),2)),4))
```

---

## Limitations

1. **The substrate is a gene-panel cache, not an expression matrix.** `research/modalities/emc-expression-panels.json` holds 479 selected genes; 464 are complete-case on GPL6244. Every "variance", "contribution" and "leverage" here is a property of *those cached percentile values*. This bounds the work far more than n does: a decomposition of six curated endothelial genes cannot speak to the endothelial transcriptional programme, and the panel's gene selection is itself a prior choice this report did not make and cannot audit.
2. **n = 6 is the arithmetic, not a background assumption.** With six specimens, one specimen carrying ~49% of the sum of squares is unremarkable — the *even* value is 17% and the comparator arms sit at 55–59%. Interpreting any leverage number here as unusual requires the n-matched null, which is why one was run.
3. **The T1 threshold is a judgement I made in advance, not a law.** 0.50 is a defensible line (a majority of the variance) but it is a line. Top-1 leverage came in at 0.4862. A reader preferring 0.45 would see limb (i) fire; limb (ii) would still fail at 0.1444 vs 0.0949, so the verdict does not turn on it — but the closeness is a real property of the data and I have not hidden it.
4. **The shape control returns a null and that null has teeth.** Because EMC's concentration structure is indistinguishable from (indeed flatter than) the comparators', **this decomposition has no power to discriminate shape** and should not be cited as independent support for W02c. It rules out one failure mode; it does not corroborate.
5. **`HHI_gene` is not fully independent of the score.** Because `C_i = Cov(g_i, s)/k` and `s` contains `g_i`, each gene's contribution includes its own variance term. The decomposition is exact and the shares sum to 1, but the floor on any share is not zero, so `HHI_gene` cannot fall to 1/k in the presence of uncorrelated genes as cleanly as an independent-component index would. The n-matched LGFMS null in R4 is computed with the identical construction, so the comparison is like-for-like; the absolute value is not.
6. **One platform, one series, no replication.** GPL6244 / `GSE24369` only. GPL3290 was deliberately not used (different measurement scale, n=3 comparator arms, and a known spot-completeness confound). No independent EMC cohort exists here, and **arrays or specimens do not imply new patients**.
7. **No covariate can be excluded.** `sample_annotations_verbatim` records only diagnosis and "soft tissue / tumor biopsy" for all 42 samples (W02c, verified). Grade, site, size, treatment, batch and scan date are **UNKNOWN, not absent**, so no per-specimen explanation for GSM600936's position can be tested or ruled out.
8. **No mechanism, no clinic.** A percentile-score association is an **ASSOCIATION**, never a mechanism and never a clinical finding. Nothing here bears on EMC vasculature in life, on angiogenesis, on treatment selection, or on any patient. **There is no wet lab**, and no computational result in this report can establish efficacy, safety, selectivity or clinical readiness.

---

## Stop condition

**Declared before starting:** return the moment (a) the pre-declared rule is frozen and hashed, (b) both decompositions are computed on the EMC arm with the committed values shown, (c) the same decomposition is run on the comparator arms as a control, and (d) the verdict is stated against the frozen threshold — whichever way it falls — with the post-run hash shown unchanged.

**MET.** All four conditions satisfied: hash `a39c1a11…` identical before (02:51:10 UTC) and after (02:51:19 UTC) the run; both decompositions exact (gene residual `6.94e-18`, leverages summing to `1.000000`); comparator control run on all three arms plus a 20,000-draw n-matched null; verdict **T3 DISTRIBUTED** with the shape control returning **ORDINARY**, reported including the parts that cut against the finding. Returned immediately; nothing padded.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 10** (all `Bash`; no other tool, no network call, no subagent).
- **Wall clock: ~3 minutes** — `Tue Sep  8 02:49:21 UTC 2026` to `Tue Sep  8 02:52:05 UTC 2026`. Well inside the ~40-call / ~40-minute target.
- `git status --porcelain` empty at start and at end; `git rev-parse HEAD` = `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` at both.

---

## Next concrete action

**Run this same frozen decomposition on the fibro/ECM axis (k=14), the one other compartment that survived W02d's full battery.** It is the highest-value successor because W02d's verdict for that axis rests on the same pass/fail-gate logic this report just showed is uninformative about shape, and because k=14 vs k=6 lets the `HHI_gene` construction be checked at a different gene count — where the self-covariance floor noted in Limitation 5 is four times weaker. Concretely: reuse `w02e.py` unchanged except for the marker list and `FLOOR = 0.0442` (the LGFMS fibro/ECM SD from W02d R3), declare and hash before running, and report whether the fibro/ECM excess is likewise distributed or whether it concentrates. A **useful secondary outcome would be a negative**: if fibro/ECM's `HHI_sample` *does* exceed the n-matched null's p95 while endothelium's does not, that is a real difference between the two surviving axes that W02d's gate could not see.

A second, weaker option I am recording rather than recommending: re-run the decomposition treating GSM600936 as a declared held-out specimen and asking whether the remaining five still show excess variance against a five-specimen-matched null. It is weaker because at n=5 the null is very wide and the answer is likely "undecidable" — the same wall W02c hit on the bimodality question.
