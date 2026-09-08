<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:10:00Z UTC
     agent id a95ad46693f742cfb ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a95ad46693f742cfb.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

# W02f — Does the EMC fibro/ECM variance excess (k = 14) concentrate where the endothelial one did not?

## Worker

- **Worker ID:** W02f (lane 2 refill), OPUS-CAPACITY-CAMPAIGN-20260908. W02e's named successor.
- **Lane:** Lane 2 — EMC microenvironment. Exact variance decomposition of the second surviving compartment axis.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I self-report as Claude Opus 5 (`claude-opus-5`), running as Claude Code in the Anthropic Cloud remote environment. **This is a self-report and must not be treated as an observed fact.** No `ANTHROPIC_MODEL` variable exists in the environment (see the literal dump below — it is absent), so the served model is not confirmable from inside the session. The coordinator must extract the runtime model from the transcript.
- **Write isolation:** READ-ONLY on the Git tree, honoured. All execution under `/tmp/claude-0/w02f/`. **Nothing written, moved or deleted anywhere under `/home/user/Rare-cancers`. No git write operation of any kind.** `git status --porcelain` was **empty at start and empty at end** (verbatim: no output both times).
- **`git rev-parse HEAD` actually read — IT MOVED UNDER ME, and I checked:** `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8` at start (02:57:20 UTC), `fc6ed92999c26f52c47668d1c126321a5f51d1b5` at end (03:00:52 UTC). The two intervening commits are the coordinator's tenth and eleventh report batches (`4ec9da1e`, `fc6ed929`), which add only `W07e`, `W10f`, `W01f`, `W05f` report files. **I verified my inputs are unchanged across the move:** `git diff --stat ce743d6a fc6ed929 -- research/modalities/emc-expression-panels.json .../W02d-....md .../W02e-....md .../COMMON-BRIEF.md` returned **empty output, exit 0**. The panel cache's sha256 at end is `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` and its `generated_utc` is `2026-08-29T12:51:32+00:00`, identical to what W02b/W02c/W02d/W02e read. The COMMON-BRIEF names frozen read commit `92abbcb9…`; HEAD has advanced well past it, as W02e also recorded.
- **`date -u` at start:** `Tue Sep  8 02:57:20 UTC 2026`
- **`date -u` at end:** `Tue Sep  8 03:00:52 UTC 2026`
- **Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (captured at start; unchanged at end):**

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

**Is the EMC fibro/ECM score's excess between-specimen variance (SD 0.0798 vs LGFMS 0.0442, W02d R3) a property of the fourteen-gene set or of the six specimens — and does it concentrate more than the endothelial axis did, i.e. is there a real difference between the two axes W02d's pass/fail gate could not see?**

Open because W02d certified two axes as artifact-resistant using a four-part **pass/fail battery**, and W02e then showed that exactly this style of gate says nothing about how the variance is *distributed*: the endothelial decomposition came back DISTRIBUTED with a shape control that returned ORDINARY, so the decomposition had no discriminating power there. If fibro/ECM behaves the same, the two axes are indistinguishable in shape and no decomposition argument can be made about either. If it behaves differently, that difference is new information about the corpus.

**Substrate limit, stated up front and not in a footnote:** the only input is the committed **gene-panel cache of 479 genes** (464 complete-case on this platform), **not an expression matrix**. The expression matrices are not committed and fetching them is denied. Every quantity below is a statement about `array_percentile` values held in that cache. It is not a measure of collagen, matrix density, fibroblast content, stroma, tumour biology, treatment, or any patient.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers` (all read-only, all exit 0):

```
rg -n -i "herfindahl|HHI_gene|HHI_sample" --glob '!.git' -l
rg -n -i "fibro/ECM|fibroECM" --glob '!.git' -l
git ls-files | rg -i "w02f|decompos"
grep -rl -i "herfindahl" /tmp/claude-0/frozen-corpus/extracted/corpus/ | head
```

What they showed:

- `herfindahl|HHI_gene|HHI_sample` returns **exactly one file**: `W02e-endothelial-variance-decomposition.md`. The concentration machinery exists nowhere else in the tree, and **`W02f` returns nothing** — this decomposition has not been run on the fibro/ECM axis.
- `fibro/ECM|fibroECM` returns **only** `W02b`, `W02c`, `W02d`, `W02e` — the four lane-2 reports I was handed. No other file in the tree carries a fibro/ECM compartment score.
- `git ls-files | rg -i "decompos"` hits `emc_mortality_decomposition.*` (registry mortality split into disease vs other-cause deaths — different data, different question), `fep_decompose.py` and `selcal_cofold_decompose.py` (per-residue FEP / cofold attribution). **None is a compartment-score variance decomposition.**
- The frozen corpus grep for `herfindahl` returns **nothing**.

**Conclusion: this is not a replay.** Confirmed against `CLOSED-WORK.md` that I touched none of: the clinical registry, PUB-ASO / Qeios frozen deliverables, the NR4A Perspective refusal, Brenca/Hofvander, the paired-Davis negative, or any egress route. **No network call of any kind was made; no expression matrix was fetched; no closed or denied route was opened or replayed.** I did not re-run W02e's endothelial verdict — the endothelial arm appears only as a loader-reproduction control row and in the k-comparison (declared in advance as A5).

---

## Method / inputs

- **Input (only data source):** `/home/user/Rare-cancers/research/modalities/emc-expression-panels.json`, `generated_utc 2026-08-29T12:51:32+00:00`, sha256 `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9`. Field used: `gene_reads[<symbol>][<platform>].per_sample[].array_percentile`, with `gsm` and `class`.
- **Platform:** GPL6244 (`GSE24369`), single-channel, **464 genes complete-case × 35 samples**, classes `{desmoid_fibromatosis 6, EMC 6, LGFMS 17, fibrosarcoma 6}`. **No cross-platform pooling; GPL3290 was not used at all.**
- **Marker set:** the identical 14 strings W02d used — `COL1A1, COL1A2, COL3A1, COL5A1, DCN, LUM, FAP, THY1, POSTN, FN1, PDGFRA, PDGFRB, ACTA2, COL11A1`. **All 14 complete-case** (asserted in-script). Score = unweighted mean of the 14 `array_percentile` values; SD is between-specimen, `ddof=1`.
- **`FLOOR = 0.0442` — TAKEN FROM W02d R3**, the LGFMS fibro/ECM SD on GPL6244 (that set's largest comparator-arm SD). **I did not re-derive it as the threshold.** The script recomputes the comparator SDs purely as a reproduction check and prints the result; the verdict uses the taken constant regardless. This mirrors W02e, which took `FLOOR = 0.0949` from W02c. The recomputation agreed: **0.0442**.
- **Tools:** Python 3.11.15, numpy 2.4.6, scipy 1.17.1, Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w02f`, no network. Scripts `w02f.py` and `supp.py`, both returned inline below.
- **Order of operations, which is the point of this task:** the complete pre-declaration — decomposition, statistic, the k-scaling diagnostics, all thresholds, and what result would make the excess an artifact — was written into `w02f.py`'s docstring; the file was hashed; and **only then** was it executed. **Pre-run sha256 `12034ef83c063269306c0ff86558bf839e24a80aee1ea9a3d948fbaef9f6ce41` at 02:59:39 UTC; post-run sha256 identical at 02:59:57 UTC.** The script prints every threshold beside its own result.

### The pre-declaration, quoted from the frozen docstring

- **(A) Per-gene, exact:** `Var(s) = Σ_i C_i`, `C_i = (1/k)·Cov(g_i, s)` (ddof=1); share `f_i = C_i/Var(s)`.
- **(B) Per-sample, exact:** `Var(s) = (1/(n−1))·Σ_j (s_j−s̄)²`; leverage `l_j = (s_j−s̄)²/Σ(s−s̄)²`.
- **Statistic:** `HHI_gene = Σf_i²` (even = 1/14 = 0.07143), `HHI_sample = Σl_j²` (even = 1/6 = 0.16667). Top-1 and top-2 cumulative alongside.
- **The k = 14 diagnostics, declared because k differs from W02e's 6** (all three **descriptive; they cannot change the verdict**):
  - **D1 SELF-SHARE.** `f_i^self = Var(g_i)/(k²·Var(s))`; `Σ_i f_i^self` is the fraction of score variance that is pure within-gene variance rather than between-gene covariance. This quantifies W02e's Limitation 5 floor. **Declared PREDICTION: smaller at k = 14.**
  - **D2 k-NORMALISED CONCENTRATION.** Raw `HHI_gene` is not comparable across k because even = 1/k. The comparable form is `R_gene = k·HHI_gene` (even = 1.0 at any k).
  - **D3** The null uses the identical k = 14 construction, so it absorbs whatever floor the construction imposes; the null comparison is like-for-like even though absolute `HHI_gene` is not comparable across k.
- **Thresholds (`FLOOR = 0.0442`):** **T1 SAMPLE-DRIVEN** fires iff top-1 leverage ≥ 0.50 **and** that specimen's LOO SD ≤ 0.0442. **T2 GENE-DRIVEN** fires iff top-1 gene share ≥ 0.50 **and** its 13-gene SD ≤ 0.0442. **T3 DISTRIBUTED** iff neither fires. **T4** both fire → jointly degenerate.
  - **Honest note written into the docstring before the run:** at k = 14 a single gene reaching a 0.50 share is far harder than at k = 6, so **T2 is a weaker test here and a non-firing T2 at k = 14 carries less information than at k = 6**. A secondary declared diagnostic **T2b** (top-1 share ≥ 3/k = 0.21429 **and** 13-gene SD ≤ FLOOR) is reported either way and **does not override T3**.
- **What would make the excess an artifact:** **A1** = T1 fires; **A2** = T2 fires; **A3 SHAPE CONTROL** = if `HHI_sample` lies inside the n-matched null (upper-tail p > 0.05) **and** `HHI_gene` lies within the two n = 6 comparator arms' range, the shape is ORDINARY, the decomposition has no power to discriminate shape, and it must not be cited as support for W02d; **A4 CONCENTRATED-SHAPE** = `HHI_sample` above the null's 95th percentile — declared in advance as *the single most valuable available outcome*, because endothelium's did not, so A4 firing would be a real difference between the two surviving axes; **A5** = the endothelial arm is recomputed only as a control row, no endothelial verdict re-issued.
- **Null:** 20,000 six-specimen subsamples of the **real** 17-specimen LGFMS arm, same seed (`20260908`) and same B as W02e.

---

## Result

### R1 — The committed values every number below is derived from

EMC fibro/ECM `array_percentile`, GPL6244, printed in full (14 genes × 6 specimens = 84 committed numbers). **Row class: PRIMARY** — read verbatim from the committed cache.

| gene | GSM600934 | GSM600935 | GSM600936 | GSM600937 | GSM600938 | GSM600939 |
|---|---|---|---|---|---|---|
| COL1A1 | 0.9786 | 0.9848 | 0.9748 | 0.9994 | 0.9994 | 0.9824 |
| COL1A2 | 0.9742 | 0.9793 | 0.9720 | 0.9993 | 0.9993 | 0.9849 |
| COL3A1 | 0.9612 | 0.8995 | 0.9481 | 0.9983 | 0.9950 | 0.9623 |
| COL5A1 | 0.8068 | 0.9163 | 0.6582 | 0.9483 | 0.9616 | 0.7570 |
| DCN | 0.8697 | 0.7989 | 0.5749 | 0.9935 | 0.9943 | 0.9587 |
| LUM | 0.4208 | 0.2279 | 0.2920 | 0.9333 | 0.8675 | 0.6195 |
| FAP | 0.9712 | 0.8324 | 0.6083 | 0.9863 | 0.9701 | 0.9058 |
| THY1 | 0.7004 | 0.9883 | 0.9928 | 0.9551 | 0.9653 | 0.9689 |
| POSTN | 0.9214 | 0.9470 | 0.7782 | 0.9966 | 0.9963 | 0.9569 |
| FN1 | 0.9169 | 0.9576 | 0.9094 | 0.9716 | 0.9721 | 0.9067 |
| PDGFRA | 0.9823 | 0.9935 | 0.9089 | 0.9889 | 0.9943 | 0.9635 |
| PDGFRB | 0.7791 | 0.7074 | 0.7032 | 0.9112 | 0.9365 | 0.8739 |
| ACTA2 | 0.9243 | 0.9756 | 0.9889 | 0.9832 | 0.9490 | 0.9423 |
| COL11A1 | 0.4312 | 0.3801 | 0.3639 | 0.8607 | 0.8104 | 0.4937 |
| **SCORE** | **0.8313** | **0.8278** | **0.7624** | **0.9661** | **0.9579** | **0.8769** |

`Var(score) = 0.006376`, `SD = 0.0798`, n = 6 — reproducing W02d R1's `0.0798` exactly with an independently written loader, and reproducing the LGFMS comparator SD as `0.0442` exactly. **Row class: PREDICTION** (a score is a derived composition statement, not a measurement).

### R2 — Per-gene contribution to the EMC fibro/ECM score variance (exact, k = 14, ranked)

All rows **PREDICTION**. Units: `array_percentile²` for `C_i`; shares dimensionless.

| rank | gene | `C_i = Cov(g_i,s)/k` | share `f_i` | cumulative | self-share `f_i^self` | 13-gene SD without it |
|---|---|---|---|---|---|---|
| 1 | **LUM** | 0.001594 | **0.2500** | 0.2500 | 0.0702 | **0.0649** |
| 2 | COL11A1 | 0.001202 | 0.1886 | 0.4386 | 0.0392 | 0.0700 |
| 3 | DCN | 0.000831 | 0.1304 | 0.5690 | 0.0209 | 0.0750 |
| 4 | FAP | 0.000658 | 0.1031 | 0.6721 | 0.0167 | 0.0774 |
| 5 | PDGFRB | 0.000547 | 0.0858 | 0.7579 | 0.0084 | 0.0787 |
| 6 | COL5A1 | 0.000545 | 0.0855 | 0.8434 | 0.0117 | 0.0788 |
| 7 | POSTN | 0.000405 | 0.0635 | 0.9069 | 0.0053 | 0.0806 |
| 8 | COL3A1 | 0.000151 | 0.0237 | 0.9306 | 0.0010 | 0.0840 |
| 9 | FN1 | 0.000130 | 0.0203 | 0.9510 | 0.0008 | 0.0843 |
| 10 | PDGFRA | 0.000129 | 0.0202 | 0.9711 | 0.0009 | 0.0843 |
| 11 | THY1 | 0.000078 | 0.0122 | 0.9834 | 0.0102 | 0.0854 |
| 12 | COL1A2 | 0.000067 | 0.0105 | 0.9939 | 0.0001 | 0.0851 |
| 13 | COL1A1 | 0.000057 | 0.0089 | 1.0028 | 0.0001 | 0.0852 |
| 14 | **ACTA2** | **−0.000018** | **−0.0028** | 1.0000 | 0.0005 | 0.0863 |

Identity check: `ΣC_i = 0.006376` against `Var = 0.006376`, residual `8.67e-19` — exact, not approximate.

**`HHI_gene = 0.1461`** (even = 0.07143); **top-1 share 0.2500, top-2 cumulative 0.4386**; **`R_gene = k·HHI = 2.0460`**.

Two things the exact decomposition shows that W02d's leave-one-marker-out gate could not:

- **`LUM` carries exactly a quarter of the axis's score variance** — a fourteen-gene mean in which one gene holds 25.0% and the top two hold 43.9%. W02d independently identified `LUM` as the largest single contributor by a different route (its LOMO minimum, 0.0649); the exact share puts a number on it.
- **`ACTA2`'s contribution is negative (−0.28%).** It is a net *diluter*: removing it *raises* the SD to 0.0863, the largest of the fourteen. A pass/fail LOMO gate records this only as "still passes"; the signed decomposition says the fourteen markers are not all pulling the same way.

### R3 — Per-sample leverage on the EMC fibro/ECM score variance (exact, ranked)

All rows **PREDICTION**.

| rank | GSM | score | deviation | leverage `l_j` | cumulative | SD without it |
|---|---|---|---|---|---|---|
| 1 | GSM600936 | 0.7624 | −0.1080 | **0.3659** | 0.3659 | **0.0669** |
| 2 | GSM600937 | 0.9661 | +0.0957 | 0.2874 | 0.6533 | 0.0723 |
| 3 | GSM600938 | 0.9579 | +0.0875 | 0.2404 | 0.8937 | 0.0753 |
| 4 | GSM600935 | 0.8278 | −0.0426 | 0.0570 | 0.9507 | 0.0862 |
| 5 | GSM600934 | 0.8313 | −0.0391 | 0.0480 | 0.9987 | 0.0867 |
| 6 | GSM600939 | 0.8769 | +0.0065 | 0.0013 | 1.0000 | 0.0892 |

`Σl_j = 1.000000` exactly. **`HHI_sample = 0.2798`**, top-1 leverage **0.3659**, top-2 cumulative 0.6533.

`GSM600936` is again the top-leverage specimen, as on the endothelial axis — but **with the opposite sign**: it is the *lowest* fibro/ECM scorer (−0.1080) and was the *highest* endothelial scorer (+0.3120). It carries 36.6% here versus 48.6% there. The fibro/ECM axis's leverage is more evenly spread across three specimens (`GSM600936`, `GSM600937`, `GSM600938` together hold 89.4%) than the endothelial axis's was.

### R4 — Shape control: the identical k = 14 decomposition on the comparator arms

All rows **PREDICTION**.

| arm | n | SD | `HHI_gene` | `R_gene = k·HHI` | top-1 gene | `HHI_sample` | top-1 sample | min LOO SD |
|---|---|---|---|---|---|---|---|---|
| **EMC** | 6 | **0.0798** | **0.1461** | **2.0460** | 0.2500 | **0.2798** | 0.3659 | 0.0669 |
| LGFMS | 17 | 0.0442 | 0.2498 | 3.4974 | 0.3880 | 0.1291\* | 0.2302\* | 0.0396 |
| desmoid fibromatosis | 6 | 0.0012 | 0.3818 | 5.3457 | 0.4594 | **0.5062** | **0.6166** | 0.0007 |
| fibrosarcoma | 6 | 0.0277 | 0.3649 | 5.1089 | 0.5673 | **0.5173** | **0.6368** | 0.0151 |

\* `HHI_sample` is mechanically n-dependent (even = 1/n), so the LGFMS row is **not** directly comparable and enters only through the n-matched null.

n-matched null, 20,000 draws of six specimens from the seventeen **real** LGFMS tumours, identical k = 14 construction:

| statistic | null mean | p50 | p95 | max | EMC observed | upper-tail p |
|---|---|---|---|---|---|---|
| `HHI_sample` | 0.3316 | 0.3145 | **0.4877** | 0.6618 | **0.2798** | **0.7115** |
| `HHI_gene` | 0.3341 | 0.3104 | 0.5839 | 1.5633 | **0.1461** | **1.0000** |
| SD (context only, not a declared rule) | — | 0.0433 | 0.0586 | 0.0682 | **0.0798** | **0.00000** |

The SD row independently reproduces W02d's route (b): the EMC fibro/ECM SD was never once reached in 20,000 real six-specimen LGFMS resamples.

### R5 — The k = 14 vs k = 6 question (D1/D2), with the endothelial arm as control

All rows **PREDICTION**.

| EMC axis | k | SD | `HHI_gene` | even = 1/k | `R_gene = k·HHI` | Σ self-share |
|---|---|---|---|---|---|---|
| fibro/ECM | 14 | 0.0798 | 0.1461 | 0.07143 | **2.0460** | **0.1861** |
| endothelial (control) | 6 | 0.2001 | 0.1955 | 0.16667 | **1.1729** | **0.2126** |

The control row reproduces W02e's endothelial values exactly (SD 0.2001, `HHI_gene` 0.1955, `HHI_sample` 0.3011), confirming the loader.

**Does `HHI_gene` behave differently at the larger k? Yes, and the direction is the opposite of what the raw number suggests.**

- **Raw `HHI_gene` falls** (0.1461 vs 0.1955), but that is almost entirely the mechanical shift in the even value (1/14 vs 1/6). **After k-normalisation the fibro/ECM axis is the more concentrated of the two: `R_gene` 2.05× even, against endothelium's 1.17× even — roughly 1.7× as concentrated.**
- **D1's declared prediction held, but weakly.** The self-covariance floor W02e flagged in its Limitation 5 accounts for **18.6%** of the fibro/ECM score variance at k = 14 against **21.3%** at k = 6 — smaller, as predicted, but only by about an eighth, nowhere near the ~4× weakening the `1/k²` self term would imply if gene variances were comparable. **So the honest answer is that the self-covariance floor was never the dominant term at either k, and it does not explain the concentration difference between the two axes.** W02e's Limitation 5 is a real property of the construction but a small one; I am recording that it turned out to matter less than it was flagged as possibly mattering.

### R6 — Verdict against the frozen thresholds

| rule | limb (i) | limb (ii) | outcome |
|---|---|---|---|
| **T1 SAMPLE-DRIVEN** | top-1 leverage 0.3659 ≥ 0.50? **No** | LOO SD 0.0669 ≤ 0.0442? **No** | **does not fire** |
| **T2 GENE-DRIVEN** | top-1 gene share 0.2500 ≥ 0.50? **No** | 13-gene SD 0.0649 ≤ 0.0442? **No** | **does not fire** |
| **T2b** (secondary, descriptive) | 0.2500 ≥ 3/k = 0.21429? **Yes** | 0.0649 ≤ 0.0442? **No** | **does not fire** |
| **T3 DISTRIBUTED** | — | — | **YES** |
| **T4 jointly degenerate** | — | — | No |
| **A3 shape control** | `HHI_sample` p = 0.7115 > 0.05 → inside null ✔ | `HHI_gene` 0.1461 ∈ [0.3649, 0.3818]? **No** | **NOT fully ordinary** |
| **A4 CONCENTRATED-SHAPE** | `HHI_sample` 0.2798 > null p95 0.4877? | — | **does not fire** |

> **VERDICT. Against thresholds frozen and hashed before the run, the EMC fibro/ECM variance excess is neither gene-driven nor sample-driven: T3 DISTRIBUTED**, the same verdict the endothelial axis received. No gene contributes more than 25.0% of the arm's score variance, no specimen more than 36.6% of its sum of squares, and neither the largest gene nor the largest specimen can be removed to bring the SD near the 0.0442 floor (`LUM` removed → 0.0649 = 1.47×; `GSM600936` removed → 0.0669 = 1.51×).
>
> **The most valuable outcome the task named — A4 firing where endothelium's did not — DID NOT HAPPEN, and I am reporting that as the primary negative.** `HHI_sample` 0.2798 sits at upper-tail p = 0.7115, *below* the n-matched null median (0.3145) and far below its p95 (0.4877), just as endothelium's 0.3011 sat at p = 0.6794 below its p95 of 0.5396. **On the sample side the two surviving axes agree: both are unremarkable, and both are if anything flatter than the comparators.** There is no sample-side distinction for W02d's gate to have missed. I had a real chance to report a difference here and the data did not give one.
>
> **The axes do differ, but on the gene side, and A3's gene limb caught it in a direction my frozen rule was not written to score.** `HHI_gene` 0.1461 falls **outside** the n = 6 comparator range [0.3649, 0.3818] — **below it, not above.** The declared A3 conjunction therefore returns "not fully ordinary", and A4, which only tests the upper tail of `HHI_sample`, cannot speak to it. **The EMC fibro/ECM axis is far more evenly spread across its fourteen genes than any comparator arm is across the same fourteen genes** (LGFMS 0.2498, desmoid 0.3818, fibrosarcoma 0.3649). This is a lower-tail departure. **My pre-declaration had no threshold for it, and I am not inventing one now**; the descriptive lower-tail figure is in R7 and is labelled post-hoc throughout.
>
> **The cross-axis comparison that does survive**, using the k-normalised form declared in advance: relative to its own even value, the fibro/ECM axis's gene-side concentration is **2.05×** against endothelium's **1.17×**. Both statements are true at once — fibro/ECM is more concentrated across genes *than endothelium is*, and less concentrated across genes *than its own comparator arms are*. They are not in tension because they use different baselines, and neither is a mechanism.
>
> **This does not overturn W02d and it does not strengthen it.** As in W02e, it removes one specific way the W02d fibro/ECM result could have been wrong — a hidden concentration in one gene or one specimen — and adds no independent support. The n = 6, single-platform, panel-cache limits W02c/W02d/W02e all name are untouched.

### R7 — Post-hoc supplement (labelled, not pre-declared, verdict unchanged)

`supp.py` exists only because the frozen A3 test had an upper tail and the observed departure was in the lower direction. **These are observations made after seeing the result.** All rows **PREDICTION**, all **POST-HOC**.

| quantity | value | note |
|---|---|---|
| `HHI_gene` lower-tail p (null ≤ EMC) | **0.00000** | 0 of 20,000 LGFMS six-specimen subsamples were as flat across the fourteen genes **[POST-HOC]** |
| null `HHI_gene` p05 / p50 | 0.1910 / 0.3104 | EMC 0.1461 lies below the null's 5th percentile **[POST-HOC]** |
| null `R_gene` p05 / p50 / p95 | 2.6744 / 4.3460 / 8.1751 | EMC `R_gene` 2.0460 below p05 **[POST-HOC]** |
| `HHI_sample` lower-tail p | 0.28855 | ordinary in both tails **[POST-HOC]** |
| worst-case drop-2 SD (min over all 15 deletions of two of six) | **0.0471** | 1.07× the 0.0442 floor; **not** ≤ floor |
| drop the two highest-leverage specimens (`GSM600936` + `GSM600937`) | 0.0606 | 1.37× floor |
| full sorted drop-2 SD vector | 0.0471, 0.0606, 0.0644, 0.0651, 0.0665, 0.0766, 0.0818, 0.0820, 0.0824, 0.0854, 0.0856, 0.0858, 0.0946, 0.0995, 0.1001 | — |

**The drop-2 margin is materially tighter than endothelium's.** Under adversarial deletion of a third of the arm, fibro/ECM survives at 1.07× the floor where endothelium survived at 1.14×. Neither falls below, but fibro/ECM is the nearer of the two to the line. That is a real, if modest, difference in robustness between the two surviving axes.

**No clinical claim.** Every quantity is a **PREDICTION about the composition of a committed gene-panel cache**, and a percentile-score result is an **ASSOCIATION** — never a mechanism, never clinical. Nothing here bears on EMC stroma, matrix biology, fibroblast content, treatment, or any patient. There is no wet lab.

---

## Validation evidence

**RUN.** Environment for all rows: Linux 6.18.44-fc-v24 x86_64, Python 3.11.15, numpy 2.4.6, scipy 1.17.1, cwd `/tmp/claude-0/w02f`, no network.

| # | command | exit | key verbatim output |
|---|---|---|---|
| 1 | `date -u` (start) | 0 | `Tue Sep  8 02:57:20 UTC 2026` |
| 2 | `git rev-parse HEAD` (start) | 0 | `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8` |
| 3 | `git status --porcelain` (start) | 0 | **empty output** |
| 4 | `python3 -c "import numpy,scipy,sys;print(...)"` | 0 | `numpy 2.4.6 scipy 1.17.1 python 3.11.15` |
| 5 | `sha256sum /tmp/claude-0/w02f/w02f.py` **before the run**, 02:59:39 UTC | 0 | `12034ef83c063269306c0ff86558bf839e24a80aee1ea9a3d948fbaef9f6ce41` |
| 6 | `cd /tmp/claude-0/w02f && python3 w02f.py 2>&1 \| tee out.txt` | **0** (`EXIT=0` via `PIPESTATUS`) | full output below |
| 7 | `sha256sum w02f.py` **after the run**, 02:59:57 UTC | 0 | `12034ef83c063269306c0ff86558bf839e24a80aee1ea9a3d948fbaef9f6ce41` — **identical to #5** |
| 8 | `sha256sum supp.py` | 0 | `2b33093c18dce64eef0979946c40e424a5aaa64f1912bc653345fc348e8db82f` |
| 9 | `cd /tmp/claude-0/w02f && python3 supp.py 2>&1 \| tee supp.txt` | **0** | full output below |
| 10 | `git rev-parse HEAD` (end) | 0 | `fc6ed92999c26f52c47668d1c126321a5f51d1b5` — **moved**, see #11 |
| 11 | `git diff --stat ce743d6a fc6ed929 -- research/modalities/emc-expression-panels.json .../W02d-….md .../W02e-….md .../COMMON-BRIEF.md` | 0 | **empty output — none of my inputs changed across the HEAD move** |
| 12 | `sha256sum research/modalities/emc-expression-panels.json` (end) | 0 | `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` |
| 13 | `git status --porcelain` (end) | 0 | **empty output** |
| 14 | `date -u` (end) | 0 | `Tue Sep  8 03:00:52 UTC 2026` |

**The hash identity in rows 5 and 7 is the pre-declaration guarantee: the file carrying the decomposition, the statistic, the thresholds and the artifact rules was byte-identical before and after execution, so nothing was written or adjusted after a result was seen. The hashes do not differ, so the result is not void.** `/tmp/claude-0/w02f/` contains exactly four files: `w02f.py`, `supp.py`, `out.txt`, `supp.txt`.

Verbatim output of run #6 (`out.txt`, complete):

```
SOURCE generated_utc = 2026-08-29T12:51:32+00:00
PLATFORM GSE24369_series_matrix.txt.gz | complete-case 464 genes x 35 samples | {'desmoid_fibromatosis': 6, 'EMC': 6, 'LGFMS': 17, 'fibrosarcoma': 6}
fibro/ECM markers complete-case: 14/14 -> ['COL1A1', 'COL1A2', 'COL3A1', 'COL5A1', 'DCN', 'LUM', 'FAP', 'THY1', 'POSTN', 'FN1', 'PDGFRA', 'PDGFRB', 'ACTA2', 'COL11A1']

=== COMMITTED VALUES: EMC fibro/ECM array_percentile matrix (GPL6244), 14 x 6 ===
gene         GSM600934   GSM600935   GSM600936   GSM600937   GSM600938   GSM600939
COL1A1          0.9786      0.9848      0.9748      0.9994      0.9994      0.9824
COL1A2          0.9742      0.9793      0.9720      0.9993      0.9993      0.9849
COL3A1          0.9612      0.8995      0.9481      0.9983      0.9950      0.9623
COL5A1          0.8068      0.9163      0.6582      0.9483      0.9616      0.7570
DCN             0.8697      0.7989      0.5749      0.9935      0.9943      0.9587
LUM             0.4208      0.2279      0.2920      0.9333      0.8675      0.6195
FAP             0.9712      0.8324      0.6083      0.9863      0.9701      0.9058
THY1            0.7004      0.9883      0.9928      0.9551      0.9653      0.9689
POSTN           0.9214      0.9470      0.7782      0.9966      0.9963      0.9569
FN1             0.9169      0.9576      0.9094      0.9716      0.9721      0.9067
PDGFRA          0.9823      0.9935      0.9089      0.9889      0.9943      0.9635
PDGFRB          0.7791      0.7074      0.7032      0.9112      0.9365      0.8739
ACTA2           0.9243      0.9756      0.9889      0.9832      0.9490      0.9423
COL11A1         0.4312      0.3801      0.3639      0.8607      0.8104      0.4937
SCORE           0.8313      0.8278      0.7624      0.9661      0.9579      0.8769

=== FLOOR PROVENANCE ===
FLOOR used for every threshold = 0.0442, TAKEN FROM W02d R3 (LGFMS fibro/ECM SD).
reproduction check only (does NOT set the threshold): recomputed LGFMS fibro/ECM SD = 0.0442
recomputed EMC fibro/ECM SD = 0.0798 (W02d R1 reported 0.0798)

=== (A) PER-GENE CONTRIBUTION TO THE EMC fibro/ECM SCORE VARIANCE (exact, k=14) ===
Var(score) = 0.006376   SD = 0.0798   n=6 k=14
gene           C_i=Cov/k  share f_i        cum   self f^s 13-gene SD w/o it
LUM             0.001594     0.2500     0.2500     0.0702            0.0649
COL11A1         0.001202     0.1886     0.4386     0.0392            0.0700
DCN             0.000831     0.1304     0.5690     0.0209            0.0750
FAP             0.000658     0.1031     0.6721     0.0167            0.0774
PDGFRB          0.000547     0.0858     0.7579     0.0084            0.0787
COL5A1          0.000545     0.0855     0.8434     0.0117            0.0788
POSTN           0.000405     0.0635     0.9069     0.0053            0.0806
COL3A1          0.000151     0.0237     0.9306     0.0010            0.0840
FN1             0.000130     0.0203     0.9510     0.0008            0.0843
PDGFRA          0.000129     0.0202     0.9711     0.0009            0.0843
THY1            0.000078     0.0122     0.9834     0.0102            0.0854
COL1A2          0.000067     0.0105     0.9939     0.0001            0.0851
COL1A1          0.000057     0.0089     1.0028     0.0001            0.0852
ACTA2          -0.000018    -0.0028     1.0000     0.0005            0.0863
sum of C_i = 0.006376  (equals Var = 0.006376 ; residual 8.67e-19)
HHI_gene = 0.1461  (even = 0.07143)   top1 = 0.2500   top2 cum = 0.4386   R_gene = k*HHI = 2.0460

=== (B) PER-SAMPLE LEVERAGE ON THE EMC fibro/ECM SCORE VARIANCE (exact) ===
GSM               score          dev   leverage        cum    SD w/o it
GSM600936        0.7624      -0.1080     0.3659     0.3659       0.0669
GSM600937        0.9661       0.0957     0.2874     0.6533       0.0723
GSM600938        0.9579       0.0875     0.2404     0.8937       0.0753
GSM600935        0.8278      -0.0426     0.0570     0.9507       0.0862
GSM600934        0.8313      -0.0391     0.0480     0.9987       0.0867
GSM600939        0.8769       0.0065     0.0013     1.0000       0.0892
sum of leverages = 1.000000
HHI_sample = 0.2798  (even = 0.16667)   top1 = 0.3659   top2 cum = 0.6533

=== (C) SHAPE CONTROL: same k=14 decomposition on the comparator arms ===
arm                         n       SD   HHI_gene     R_gene  top1_gen   HHI_samp  top1_samp   min_LOO_SD
EMC                         6   0.0798     0.1461     2.0460    0.2500     0.2798     0.3659       0.0669
LGFMS                      17   0.0442     0.2498     3.4974    0.3880     0.1291     0.2302       0.0396
desmoid_fibromatosis        6   0.0012     0.3818     5.3457    0.4594     0.5062     0.6166       0.0007
fibrosarcoma                6   0.0277     0.3649     5.1089    0.5673     0.5173     0.6368       0.0151
note: HHI_sample is mechanically n-dependent (even = 1/n); LGFMS (n=17) enters only via the
n=6 subsample null below.  HHI_gene is k-dependent (even = 1/k); R_gene = k*HHI is the
k-comparable form (even = 1.0 at any k).

=== (D1/D2) k=14 vs k=6: SELF-COVARIANCE FLOOR AND k-NORMALISED CONCENTRATION ===
axis (EMC)       k       SD   HHI_gene   even 1/k R_gene=k*HHI sum self-share
fibro/ECM       14   0.0798     0.1461    0.07143       2.0460         0.1861
endothelial      6   0.2001     0.1955    0.16667       1.1729         0.2126
CONTROL (W02e reproduction): endothelial EMC SD 0.2001 / HHI_gene 0.1955 / HHI_sample 0.3011
sum self-share = fraction of the arm's score variance that is pure within-gene variance
rather than between-gene covariance; declared PREDICTION was that it is smaller at k=14.

=== (E) n-MATCHED NULL: 20000 six-specimen subsamples of the REAL 17-specimen LGFMS arm ===
HHI_sample null: mean=0.3316 p50=0.3145 p95=0.4877 max=0.6618 | EMC=0.2798 | upper-tail p=0.7115
HHI_gene   null: mean=0.3341 p50=0.3104 p95=0.5839 max=1.5633 | EMC=0.1461 | upper-tail p=1.0000
(context, not a declared rule) SD null: p50=0.0433 p95=0.0586 max=0.0682 | EMC SD=0.0798 | p=0.00000

=== (F) VERDICT AGAINST THE PRE-DECLARED THRESHOLDS ===
T1 SAMPLE-DRIVEN : top1 leverage 0.3659 >= 0.50 ? False | its LOO SD 0.0669 <= 0.0442 ? False -> does not fire
T2 GENE-DRIVEN   : top1 gene share 0.2500 >= 0.50 ? False | its 13-gene SD 0.0649 <= 0.0442 ? False -> does not fire
T2b (SECONDARY, descriptive, does NOT change the verdict): top1 share 0.2500 >= 3/k=0.21429 ? True | 13-gene SD <= FLOOR ? False -> does not fire
T3 DISTRIBUTED   : YES - neither T1 nor T2 fires
T4 jointly degenerate: False
A3 SHAPE CONTROL : HHI_sample inside n-matched null (p=0.7115 > 0.05)? True ; HHI_gene inside n=6 comparator range [0.3649, 0.3818]? False -> shape NOT fully ordinary
A4 CONCENTRATED-SHAPE : HHI_sample 0.2798 above null p95 0.4877 ? False
CROSS-AXIS COMPARISON (the point of this run): endothelium A4 was False (W02e: HHI_sample
0.3011, p=0.6794, null p95=0.5396). fibro/ECM A4 = False -> axes AGREE on the sample-side

DONE
```

Verbatim output of run #9 (`supp.txt`, complete):

```
POST-HOC, NOT PRE-DECLARED. Direction of the fibro/ECM HHI_gene departure:
  EMC HHI_gene = 0.1461 ; null p05=0.1910 p50=0.3104 ; LOWER-tail p(null <= EMC) = 0.00000  [POST-HOC]
  EMC R_gene=k*HHI = 2.0460 ; null R_gene p05=2.6744 p50=4.3460 p95=8.1751  [POST-HOC]
  EMC HHI_sample = 0.2798 ; LOWER-tail p(null <= EMC) = 0.28855  [POST-HOC]

Worst-case drop-2 (min SD over all 15 deletions of two of six) = 0.0471 ; <= FLOOR 0.0442 ? False
all pairwise drop-2 SDs sorted: [0.0471 0.0606 0.0644 0.0651 0.0665 0.0766 0.0818 0.082  0.0824 0.0854
 0.0856 0.0858 0.0946 0.0995 0.1001]
drop the two highest-leverage specimens (GSM600936 + GSM600937) SD = 0.0606
```

**PROPOSED (NOT RUN)** — declared, not claimed:

- The same decomposition against the full `GSE24369` series matrix rather than the 464-gene panel cache. **Not run:** the matrix is not committed and fetching it requires egress, which is denied. This is the substrate limit, not a scheduling gap.
- A **gene-set-matched** null (random 14-gene panels drawn from the 464-gene cache, scored on the six EMC specimens, to ask whether the low `HHI_gene` is a property of the fibro/ECM gene set or of the EMC arm). **Not run:** it would be a new test constructed after seeing the lower-tail result, so running it inside this report would let a post-hoc observation borrow the pre-declaration's credibility. Named as the successor below, to be frozen and hashed on its own terms.
- Any correlation between the fibro/ECM and endothelial axes within EMC (W02d's own named successor). **Not run:** out of this task's declared scope, and it is a coupling question rather than an artifact route.

### Code, returned inline (nothing written into the tree)

`/tmp/claude-0/w02f/w02f.py` — sha256 `12034ef83c063269306c0ff86558bf839e24a80aee1ea9a3d948fbaef9f6ce41`, unchanged across the run:

```python
"""W02f - is the EMC fibro/ECM score's excess between-specimen variance a property of the
GENE SET (k=14) or of the SIX SAMPLES?  READ-ONLY on the repository; executes only under
/tmp/claude-0/w02f/.  This is W02e's named successor, run with W02e's machinery unchanged
except for the marker list, the floor, and the k-scaling diagnostics added because k=14.

=========================  PRE-DECLARATION (frozen before any computation)  =========================
Written 2026-09-08 before the script was executed. sha256 of this file is recorded before the run
and re-checked after the run; the two must match. If they differ the result is VOID.

SUBSTRATE LIMIT, stated up front and not in a footnote: the only input is a committed
479-GENE PANEL CACHE (research/modalities/emc-expression-panels.json), NOT an expression matrix.
The expression matrices are not committed and fetching them is denied. Every number below is a
statement about that cache's array_percentile values. Nothing here is a measure of collagen,
matrix density, fibroblast content, stroma, tumour biology, treatment or any patient.

--- Inputs, taken not re-derived ---
Marker set: fibro/ECM, k=14, the identical 14 strings W02d used -
  COL1A1 COL1A2 COL3A1 COL5A1 DCN LUM FAP THY1 POSTN FN1 PDGFRA PDGFRB ACTA2 COL11A1
FLOOR = 0.0442.  THIS IS TAKEN FROM W02d R3 (the LGFMS fibro/ECM SD on GPL6244, the largest
comparator-arm SD for this marker set).  IT IS NOT RE-DERIVED HERE AS THE THRESHOLD; the script
recomputes the comparator SDs only as a reproduction check and PRINTS whether the recomputed
LGFMS value equals the taken 0.0442, but the verdict uses the taken constant either way.
This mirrors W02e, which took FLOOR = 0.0949 for endothelium from W02c.

--- The decomposition (identical construction to W02e) ---
Arm score s_j = (1/k) * sum_i g_ij over k marker genes and n specimens.
(A) EXACT GENE DECOMPOSITION.  Var(s) = sum_i C_i  with  C_i = (1/k) * Cov(g_i, s)  (ddof=1).
    Exact by construction; gene share f_i = C_i / Var(s); sum_i f_i = 1.
(B) EXACT SAMPLE DECOMPOSITION.  Var(s) = (1/(n-1)) * sum_j (s_j - sbar)^2; sample leverage
    l_j = (s_j - sbar)^2 / sum_j (s_j - sbar)^2; sum_j l_j = 1.
    Reported with the leave-one-out SD_-j.

--- The statistic ---
HHI_gene   = sum_i f_i^2   (k=14 -> perfectly even = 1/14 = 0.07143, maximum = 1)
HHI_sample = sum_j l_j^2   (n=6  -> perfectly even = 1/6  = 0.16667, maximum = 1)
Top-1 and top-2 cumulative shares are reported for each.

--- k=14 vs k=6: the specific question this run adds to W02e ---
W02e Limitation 5 flagged that C_i contains gene i's OWN variance (self-covariance), so f_i has a
non-zero floor and HHI_gene cannot fall to 1/k as cleanly as an independent index would. That self
term is Var(g_i)/k^2 out of Var(s), so its relative weight scales as 1/k and is ~2.3x weaker at
k=14 than at k=6 (and the self term's share of C_i's own k-fold sum is 1/k, i.e. 4x smaller in the
sense that k^2 grows 5.4x while the cross-term count grows 13/5 = 2.6x). Three diagnostics,
declared now:
  D1 SELF-SHARE.  f_i^self = Var(g_i) / (k^2 * Var(s)); report sum_i f_i^self, the fraction of the
     arm's score variance that is pure self-variance rather than between-gene covariance. Report it
     for fibro/ECM (k=14) AND for endothelium (k=6) as a control. PREDICTION: it is smaller at k=14.
  D2 k-NORMALISED CONCENTRATION.  Because even HHI_gene = 1/k, raw HHI_gene is NOT comparable
     between k=6 and k=14. The comparable quantity is R_gene = k * HHI_gene (even = 1.0 for any k).
     Report R_gene for both axes and for every arm.
  D3 The n-matched null is computed with the IDENTICAL k=14 construction, so the null absorbs
     whatever floor the construction imposes; the null comparison is therefore like-for-like even
     though the absolute HHI_gene is not comparable across k.
D1-D3 are DESCRIPTIVE. They do not enter the verdict rules below and cannot change them.

--- The thresholds (declared now, not adjusted later; identical rule shapes to W02e) ---
T1 SAMPLE-DRIVEN if BOTH:
      (i) top-1 sample leverage l_(1) >= 0.50, AND
      (ii) that specimen's leave-one-out SD_-j <= FLOOR (0.0442).
   -> The excess is a property of one specimen. W02d's fibro/ECM verdict is substantially
      weakened and that must be reported plainly.
T2 GENE-DRIVEN if BOTH:
      (i) top-1 gene share f_(1) >= 0.50, AND
      (ii) the leave-that-gene-out 13-gene EMC SD <= FLOOR (0.0442).
   -> The excess is a property of one member of the gene set.
   HONEST NOTE DECLARED IN ADVANCE: at k=14 a single gene reaching a 0.50 share is far harder than
   at k=6, so T2 is a WEAKER test here than it was in W02e, and a non-firing T2 at k=14 carries
   less information than a non-firing T2 at k=6. To avoid claiming more than T2 supports, a
   SECONDARY DECLARED DIAGNOSTIC is added (descriptive, NOT part of the verdict):
   T2b top-1 gene share >= 3x the even share (3/14 = 0.21429) AND its 13-gene SD <= FLOOR.
   T2b is reported whether it fires or not; it does not override T3.
T3 DISTRIBUTED if NEITHER T1 NOR T2 fires.
T4 If T1 and T2 both fire -> jointly degenerate, NOT a defensible signal.

--- What would make the excess an ARTIFACT rather than a signal ---
A1 T1 fires -> artifact of the six samples; W02d's fibro/ECM verdict weakened.
A2 T2 fires -> artifact of panel composition.
A3 SHAPE CONTROL. The same decomposition is run on the comparator arms (LGFMS n=17, desmoid n=6,
   fibrosarcoma n=6). Because HHI_sample depends on n, LGFMS enters ONLY through 20000 six-specimen
   subsamples of its 17 REAL specimens (an n-matched null), same seed and same B as W02e.
   If EMC's HHI_sample lies INSIDE that null (upper-tail p > 0.05) AND EMC's HHI_gene lies within
   the range spanned by the two n=6 comparator arms, the concentration SHAPE is ORDINARY: only the
   magnitude differs, and this decomposition then has NO power to discriminate shape and must not
   be cited as support for W02d.
A4 CONVERSELY, if EMC's HHI_sample sits ABOVE the n-matched null's 95th percentile, the sample-side
   concentration is UNUSUAL. Endothelium's did NOT (W02e: HHI_sample 0.3011, p = 0.6794, null
   p95 = 0.5396). So A4 firing here would be a REAL DIFFERENCE BETWEEN THE TWO SURVIVING AXES that
   W02d's pass/fail gate could not see, and is the single most valuable outcome available.
   It would be reported as CONCENTRATED-SHAPE, and would qualify W02d's fibro/ECM verdict, NOT
   confirm it.
A5 The endothelial arm is recomputed here ONLY as a control row (to confirm the loader reproduces
   W02e's 0.2001 / 0.1955 / 0.3011) and for the D1/D2 k-comparison. No endothelial verdict is
   re-issued and none of W02e's conclusions is revisited.

--- Committed values every number is derived from ---
The EMC fibro/ECM per-specimen, per-gene array_percentile values (14 genes x 6 specimens = 84
numbers) are printed in full so every derived quantity can be recomputed by hand.
=====================================================================================================
"""
import json, collections
import numpy as np

SRC = "/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
PLAT = "GSE24369_series_matrix.txt.gz"          # GPL6244 single-channel; no cross-platform pooling
FIB = ["COL1A1", "COL1A2", "COL3A1", "COL5A1", "DCN", "LUM", "FAP", "THY1",
       "POSTN", "FN1", "PDGFRA", "PDGFRB", "ACTA2", "COL11A1"]
ENDO = ["PECAM1", "VWF", "CDH5", "KDR", "FLT1", "MCAM"]      # control row only
FLOOR = 0.0442                                  # TAKEN FROM W02d R3, not re-derived
FLOOR_ENDO = 0.0949                             # W02e's, quoted for the control row only
RNG = np.random.default_rng(20260908)           # same seed as W02e
B = 20000                                       # same B as W02e

d = json.load(open(SRC))
print("SOURCE generated_utc = %s" % d.get("generated_utc"))
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
print("fibro/ECM markers complete-case: %d/%d -> %s" % (sum(g in M for g in FIB), len(FIB),
                                                        [g for g in FIB if g in M]))
assert all(g in M for g in FIB), "a declared fibro/ECM marker is not complete-case"
assert all(g in M for g in ENDO)

ARMS = ["EMC", "LGFMS", "desmoid_fibromatosis", "fibrosarcoma"]
idx = {a: [i for i, x in enumerate(S) if classes[x] == a] for a in ARMS}
gsm = {a: [S[i] for i in idx[a]] for a in ARMS}


def decompose(ii, marks):
    k = len(marks)
    G = np.array([M[g][ii] for g in marks])          # k x n
    s = G.mean(axis=0)
    n = len(s)
    var = s.var(ddof=1)
    C = np.array([np.cov(G[i], s, ddof=1)[0, 1] / k for i in range(k)])
    f = C / var
    fself = np.array([G[i].var(ddof=1) / (k * k * var) for i in range(k)])
    ss = (s - s.mean()) ** 2
    l = ss / ss.sum()
    loo_sd = np.array([np.delete(s, j).std(ddof=1) for j in range(n)])
    lomo_sd = np.array([np.mean([M[g][ii] for g in marks if g != marks[i]], axis=0).std(ddof=1)
                        for i in range(k)])
    return dict(s=s, var=var, sd=float(np.sqrt(var)), C=C, f=f, fself=fself, l=l,
                loo_sd=loo_sd, lomo_sd=lomo_sd, n=n, k=k,
                hhi_g=float((f ** 2).sum()), hhi_s=float((l ** 2).sum()))


# ---------- committed values, printed in full ----------
print("\n=== COMMITTED VALUES: EMC fibro/ECM array_percentile matrix (GPL6244), 14 x 6 ===")
print("gene      " + "".join("%12s" % s for s in gsm["EMC"]))
for g in FIB:
    print("%-10s" % g + "".join("%12.4f" % M[g][i] for i in idx["EMC"]))
print("%-10s" % "SCORE" + "".join("%12.4f" % v for v in
                                  np.mean([M[g][idx["EMC"]] for g in FIB], axis=0)))

R = {a: decompose(idx[a], FIB) for a in ARMS}
RE = {a: decompose(idx[a], ENDO) for a in ARMS}
e = R["EMC"]

print("\n=== FLOOR PROVENANCE ===")
print("FLOOR used for every threshold = %.4f, TAKEN FROM W02d R3 (LGFMS fibro/ECM SD)." % FLOOR)
print("reproduction check only (does NOT set the threshold): recomputed LGFMS fibro/ECM SD = %.4f"
      % R["LGFMS"]["sd"])
print("recomputed EMC fibro/ECM SD = %.4f (W02d R1 reported 0.0798)" % e["sd"])

print("\n=== (A) PER-GENE CONTRIBUTION TO THE EMC fibro/ECM SCORE VARIANCE (exact, k=14) ===")
print("Var(score) = %.6f   SD = %.4f   n=%d k=%d" % (e["var"], e["sd"], e["n"], e["k"]))
print("%-9s %14s %10s %10s %10s %17s" % ("gene", "C_i=Cov/k", "share f_i", "cum",
                                         "self f^s", "13-gene SD w/o it"))
order = np.argsort(-e["f"]); cum = 0.0
for i in order:
    cum += e["f"][i]
    print("%-9s %14.6f %10.4f %10.4f %10.4f %17.4f"
          % (FIB[i], e["C"][i], e["f"][i], cum, e["fself"][i], e["lomo_sd"][i]))
print("sum of C_i = %.6f  (equals Var = %.6f ; residual %.2e)"
      % (e["C"].sum(), e["var"], abs(e["C"].sum() - e["var"])))
print("HHI_gene = %.4f  (even = %.5f)   top1 = %.4f   top2 cum = %.4f   R_gene = k*HHI = %.4f"
      % (e["hhi_g"], 1 / e["k"], e["f"][order[0]], e["f"][order[0]] + e["f"][order[1]],
         e["k"] * e["hhi_g"]))

print("\n=== (B) PER-SAMPLE LEVERAGE ON THE EMC fibro/ECM SCORE VARIANCE (exact) ===")
print("%-12s %10s %12s %10s %10s %12s" % ("GSM", "score", "dev", "leverage", "cum", "SD w/o it"))
o2 = np.argsort(-e["l"]); cum = 0.0
for j in o2:
    cum += e["l"][j]
    print("%-12s %10.4f %12.4f %10.4f %10.4f %12.4f"
          % (gsm["EMC"][j], e["s"][j], e["s"][j] - e["s"].mean(), e["l"][j], cum, e["loo_sd"][j]))
print("sum of leverages = %.6f" % e["l"].sum())
print("HHI_sample = %.4f  (even = %.5f)   top1 = %.4f   top2 cum = %.4f"
      % (e["hhi_s"], 1 / e["n"], e["l"][o2[0]], e["l"][o2[0]] + e["l"][o2[1]]))

print("\n=== (C) SHAPE CONTROL: same k=14 decomposition on the comparator arms ===")
print("%-24s %4s %8s %10s %10s %9s %10s %10s %12s"
      % ("arm", "n", "SD", "HHI_gene", "R_gene", "top1_gen", "HHI_samp", "top1_samp", "min_LOO_SD"))
for a in ARMS:
    r = R[a]
    print("%-24s %4d %8.4f %10.4f %10.4f %9.4f %10.4f %10.4f %12.4f"
          % (a, r["n"], r["sd"], r["hhi_g"], r["k"] * r["hhi_g"], r["f"].max(), r["hhi_s"],
             r["l"].max(), r["loo_sd"].min()))
print("note: HHI_sample is mechanically n-dependent (even = 1/n); LGFMS (n=17) enters only via the")
print("n=6 subsample null below.  HHI_gene is k-dependent (even = 1/k); R_gene = k*HHI is the")
print("k-comparable form (even = 1.0 at any k).")

print("\n=== (D1/D2) k=14 vs k=6: SELF-COVARIANCE FLOOR AND k-NORMALISED CONCENTRATION ===")
print("%-14s %3s %8s %10s %10s %12s %14s"
      % ("axis (EMC)", "k", "SD", "HHI_gene", "even 1/k", "R_gene=k*HHI", "sum self-share"))
print("%-14s %3d %8.4f %10.4f %10.5f %12.4f %14.4f"
      % ("fibro/ECM", e["k"], e["sd"], e["hhi_g"], 1 / e["k"], e["k"] * e["hhi_g"],
         e["fself"].sum()))
ee = RE["EMC"]
print("%-14s %3d %8.4f %10.4f %10.5f %12.4f %14.4f"
      % ("endothelial", ee["k"], ee["sd"], ee["hhi_g"], 1 / ee["k"], ee["k"] * ee["hhi_g"],
         ee["fself"].sum()))
print("CONTROL (W02e reproduction): endothelial EMC SD %.4f / HHI_gene %.4f / HHI_sample %.4f"
      % (ee["sd"], ee["hhi_g"], ee["hhi_s"]))
print("sum self-share = fraction of the arm's score variance that is pure within-gene variance")
print("rather than between-gene covariance; declared PREDICTION was that it is smaller at k=14.")

print("\n=== (E) n-MATCHED NULL: 20000 six-specimen subsamples of the REAL 17-specimen LGFMS arm ===")
L = R["LGFMS"]["s"]
Lg = np.array([M[g][idx["LGFMS"]] for g in FIB])
k = len(FIB)
hs = np.empty(B); hg = np.empty(B); sdn = np.empty(B)
for b in range(B):
    pick = RNG.choice(len(L), 6, replace=False)
    ssb = (L[pick] - L[pick].mean()) ** 2
    hs[b] = ((ssb / ssb.sum()) ** 2).sum()
    Gb = Lg[:, pick]
    sb = Gb.mean(axis=0)
    vb = sb.var(ddof=1)
    sdn[b] = np.sqrt(vb)
    Cb = np.array([np.cov(Gb[i], sb, ddof=1)[0, 1] / k for i in range(k)])
    hg[b] = ((Cb / vb) ** 2).sum()
p_s = float((hs >= e["hhi_s"]).mean())
p_g = float((hg >= e["hhi_g"]).mean())
p95s = float(np.percentile(hs, 95))
print("HHI_sample null: mean=%.4f p50=%.4f p95=%.4f max=%.4f | EMC=%.4f | upper-tail p=%.4f"
      % (hs.mean(), np.median(hs), p95s, hs.max(), e["hhi_s"], p_s))
print("HHI_gene   null: mean=%.4f p50=%.4f p95=%.4f max=%.4f | EMC=%.4f | upper-tail p=%.4f"
      % (hg.mean(), np.median(hg), np.percentile(hg, 95), hg.max(), e["hhi_g"], p_g))
print("(context, not a declared rule) SD null: p50=%.4f p95=%.4f max=%.4f | EMC SD=%.4f | p=%.5f"
      % (np.median(sdn), np.percentile(sdn, 95), sdn.max(), e["sd"], float((sdn >= e["sd"]).mean())))

print("\n=== (F) VERDICT AGAINST THE PRE-DECLARED THRESHOLDS ===")
t1_i = bool(e["l"].max() >= 0.50)
t1_ii = bool(e["loo_sd"][int(np.argmax(e["l"]))] <= FLOOR)
T1 = t1_i and t1_ii
t2_i = bool(e["f"].max() >= 0.50)
t2_ii = bool(e["lomo_sd"][int(np.argmax(e["f"]))] <= FLOOR)
T2 = t2_i and t2_ii
t2b_i = bool(e["f"].max() >= 3.0 / e["k"])
T2b = t2b_i and t2_ii
print("T1 SAMPLE-DRIVEN : top1 leverage %.4f >= 0.50 ? %s | its LOO SD %.4f <= %.4f ? %s -> %s"
      % (e["l"].max(), t1_i, e["loo_sd"][int(np.argmax(e["l"]))], FLOOR, t1_ii,
         "FIRES" if T1 else "does not fire"))
print("T2 GENE-DRIVEN   : top1 gene share %.4f >= 0.50 ? %s | its 13-gene SD %.4f <= %.4f ? %s -> %s"
      % (e["f"].max(), t2_i, e["lomo_sd"][int(np.argmax(e["f"]))], FLOOR, t2_ii,
         "FIRES" if T2 else "does not fire"))
print("T2b (SECONDARY, descriptive, does NOT change the verdict): top1 share %.4f >= 3/k=%.5f ? %s"
      " | 13-gene SD <= FLOOR ? %s -> %s"
      % (e["f"].max(), 3.0 / e["k"], t2b_i, t2_ii, "FIRES" if T2b else "does not fire"))
print("T3 DISTRIBUTED   : %s" % ("YES - neither T1 nor T2 fires" if not (T1 or T2) else "no"))
print("T4 jointly degenerate: %s" % (T1 and T2))
a3_s = p_s > 0.05
lo, hi = sorted([R["desmoid_fibromatosis"]["hhi_g"], R["fibrosarcoma"]["hhi_g"]])
a3_g = bool(lo <= e["hhi_g"] <= hi)
A4 = bool(e["hhi_s"] > p95s)
print("A3 SHAPE CONTROL : HHI_sample inside n-matched null (p=%.4f > 0.05)? %s ; HHI_gene inside"
      " n=6 comparator range [%.4f, %.4f]? %s -> shape %s"
      % (p_s, a3_s, lo, hi, a3_g, "ORDINARY" if (a3_s and a3_g) else "NOT fully ordinary"))
print("A4 CONCENTRATED-SHAPE : HHI_sample %.4f above null p95 %.4f ? %s"
      % (e["hhi_s"], p95s, A4))
print("CROSS-AXIS COMPARISON (the point of this run): endothelium A4 was False (W02e: HHI_sample")
print("0.3011, p=0.6794, null p95=0.5396). fibro/ECM A4 = %s -> axes %s on the sample-side"
      % (A4, "DIFFER" if A4 else "AGREE"))
print("\nDONE")
```

`/tmp/claude-0/w02f/supp.py` — sha256 `2b33093c18dce64eef0979946c40e424a5aaa64f1912bc653345fc348e8db82f`:

```python
"""W02f supplement - DESCRIPTIVE, POST-HOC, NOT PRE-DECLARED. No verdict rule is created or
changed here; w02f.py's frozen T1/T2/T3/T4/A3/A4 stand exactly as they ran. This exists only
because the frozen A3 test had an UPPER tail and the observed fibro/ECM HHI_gene departed in the
LOWER (flatter) direction, which the frozen rule could not quantify. The lower-tail p below is
therefore an OBSERVATION MADE AFTER SEEING THE RESULT and is labelled as such everywhere it is
used. It is not evidence for or against W02d; it is a description of the departure's direction.
Also reports the k-normalised R_gene = k*HHI_gene null and the worst-case drop-2 SD, for
comparability with W02e's supplement."""
import json, collections, itertools
import numpy as np
SRC="/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
PLAT="GSE24369_series_matrix.txt.gz"
FIB=["COL1A1","COL1A2","COL3A1","COL5A1","DCN","LUM","FAP","THY1","POSTN","FN1","PDGFRA","PDGFRB","ACTA2","COL11A1"]
FLOOR=0.0442; RNG=np.random.default_rng(20260908); B=20000; k=14
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
ii=[i for i,x in enumerate(S) if classes[x]=="EMC"]; g6=[S[i] for i in ii]
li=[i for i,x in enumerate(S) if classes[x]=="LGFMS"]
G=np.array([M[g][ii] for g in FIB]); s=G.mean(axis=0); var=s.var(ddof=1)
C=np.array([np.cov(G[i],s,ddof=1)[0,1]/k for i in range(k)]); f=C/var
hhi_g=float((f**2).sum()); ss=(s-s.mean())**2; l=ss/ss.sum(); hhi_s=float((l**2).sum())
L=np.array([M[g][li] for g in FIB]); Ls=L.mean(axis=0)
hg=np.empty(B); hs=np.empty(B)
for b in range(B):
    p=RNG.choice(len(li),6,replace=False); Gb=L[:,p]; sb=Gb.mean(axis=0); vb=sb.var(ddof=1)
    Cb=np.array([np.cov(Gb[i],sb,ddof=1)[0,1]/k for i in range(k)]); hg[b]=((Cb/vb)**2).sum()
    sq=(sb-sb.mean())**2; hs[b]=((sq/sq.sum())**2).sum()
print("POST-HOC, NOT PRE-DECLARED. Direction of the fibro/ECM HHI_gene departure:")
print("  EMC HHI_gene = %.4f ; null p05=%.4f p50=%.4f ; LOWER-tail p(null <= EMC) = %.5f  [POST-HOC]"
      %(hhi_g,np.percentile(hg,5),np.median(hg),float((hg<=hhi_g).mean())))
print("  EMC R_gene=k*HHI = %.4f ; null R_gene p05=%.4f p50=%.4f p95=%.4f  [POST-HOC]"
      %(k*hhi_g,k*np.percentile(hg,5),k*np.median(hg),k*np.percentile(hg,95)))
print("  EMC HHI_sample = %.4f ; LOWER-tail p(null <= EMC) = %.5f  [POST-HOC]"
      %(hhi_s,float((hs<=hhi_s).mean())))
d2=sorted(np.delete(s,list(c)).std(ddof=1) for c in itertools.combinations(range(6),2))
print("\nWorst-case drop-2 (min SD over all 15 deletions of two of six) = %.4f ; <= FLOOR %.4f ? %s"
      %(d2[0],FLOOR,d2[0]<=FLOOR))
print("all pairwise drop-2 SDs sorted:",np.round(d2,4))
o=np.argsort(-l)
print("drop the two highest-leverage specimens (%s + %s) SD = %.4f"
      %(g6[o[0]],g6[o[1]],np.delete(s,[o[0],o[1]]).std(ddof=1)))
```

---

## Limitations

1. **The substrate is a committed gene-panel cache, not an expression matrix.** `research/modalities/emc-expression-panels.json` holds 479 selected genes; 464 are complete-case on GPL6244. Every "variance", "contribution" and "leverage" here is a property of *those cached percentile values*. A decomposition of fourteen curated matrix genes cannot speak to an ECM transcriptional programme, and the panel's gene selection is a prior choice this report did not make and cannot audit. **The matrices are not committed and fetching them is denied; this is a substrate limit, not a scheduling gap.**
2. **The headline outcome is a negative on the question the task most wanted answered.** A4 did not fire; the two surviving axes are indistinguishable on the sample side. I had the machinery and the pre-declared threshold to report a difference and the data did not produce one.
3. **The gene-side departure is real but was caught in a direction my frozen rule could not score.** A3's gene limb tests membership of a range; the observed value fell *below* it. Everything quantifying that departure (R7) is explicitly **post-hoc**, and none of it may be treated as a pre-registered finding. A lower-tail p of 0.00000 obtained after seeing the direction is not the same evidential object as a pre-declared upper-tail test.
4. **The n-matched null varies specimens while holding the gene set fixed.** It therefore cannot separate "the EMC arm is flat across these fourteen genes" from "these fourteen genes are flat in this cache". A gene-set-matched (random-panel) null would separate them and is the named successor; it was deliberately **not** run here.
5. **`R_gene = k·HHI` is my declared normalisation, not a canonical statistic.** It is the right first-order correction for the mechanical `1/k` even value, but it does not make two different marker sets equivalent objects. "fibro/ECM is 1.7× as concentrated as endothelium" is a statement about these two specific gene sets on this cache.
6. **T2 is a weaker test at k = 14 than at k = 6**, as declared before the run. A non-firing T2 at k = 14 excludes less than the same non-firing did in W02e. T2b was added for exactly this reason and is descriptive only.
7. **n = 6 is the arithmetic, not a background assumption.** The even leverage value is 16.7% and the two n = 6 comparator arms sit at 61.7% and 63.7%. No leverage number here is interpretable without the n-matched null, which is why one was run.
8. **The self-covariance floor (W02e Limitation 5) turned out to be modest at both k**, 18.6% at k = 14 and 21.3% at k = 6. The direction I predicted held; the magnitude of the weakening did not approach the `1/k` scaling. `HHI_gene`'s absolute value remains non-comparable across k, and only the identically-constructed null (D3) makes any comparison legitimate.
9. **One platform, one series, no replication.** GPL6244 / `GSE24369` only; GPL3290 deliberately not used. No independent EMC cohort exists here, and **arrays or specimens do not imply new patients**.
10. **No covariate can be excluded.** As W02c verified, `sample_annotations_verbatim` records only diagnosis and "soft tissue / tumor biopsy". Grade, site, size, treatment, batch and scan date are **UNKNOWN, not absent**, so no per-specimen explanation for `GSM600936`'s or `GSM600937`'s position can be tested or ruled out.
11. **No mechanism, no clinic.** A percentile-score result is an **ASSOCIATION**, never a mechanism and never clinical. Nothing here bears on EMC stroma, matrix deposition, fibroblast biology, treatment selection, prognosis, or any patient. **There is no wet lab**, and no computational result in this report can establish efficacy, safety, selectivity or clinical readiness. It also cannot claim the fibro/ECM heterogeneity is biological rather than a further untested artifact route.

---

## Stop condition

**Declared before starting:** return the moment (a) the full pre-declaration is frozen in the script docstring and hashed, (b) both exact decompositions are computed on the EMC fibro/ECM arm with the 84 committed values shown, (c) the same decomposition is run on the comparator arms plus the n-matched null, (d) the `HHI_gene`-at-larger-k question is answered, and (e) the verdict is stated against the frozen thresholds — whichever way it falls — with the post-run hash shown unchanged.

**MET.** Hash `12034ef8…` identical before (02:59:39 UTC) and after (02:59:57 UTC) the run, so the result is not void. Both decompositions exact (gene residual `8.67e-19`; leverages summing to `1.000000`). Comparator control on all three arms plus a 20,000-draw n-matched null at the identical k = 14. The k-question answered with the endothelial arm as control. Verdict **T3 DISTRIBUTED**, **A4 did not fire**, and the one departure that did occur is reported in the direction it actually took, with its quantification labelled post-hoc. Returned immediately; nothing padded.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 11** (all `Bash`; no other tool, no network call, no subagent, no skill).
- **Wall clock: ~3.5 minutes** — `Tue Sep  8 02:57:20 UTC 2026` to `Tue Sep  8 03:00:52 UTC 2026`. Well inside the ~40-call / ~40-minute target.
- `git status --porcelain` **empty at start and at end**. `git rev-parse HEAD` **moved** from `ce743d6a` to `fc6ed929` under me (coordinator batches 10 and 11); my four inputs were verified byte-identical across the move.

---

## Next concrete action

**Run a gene-set-matched null on `HHI_gene` for both surviving axes: draw random 14-gene and random 6-gene panels from the 464-gene complete-case cache (excluding all four declared marker sets), score them on the six EMC specimens, and compare `R_gene = k·HHI_gene` against the observed 2.0460 (fibro/ECM) and 1.1729 (endothelium).** This is the one test that separates the two explanations the present null cannot: the LGFMS subsample null varies *specimens* with the gene set fixed, so it cannot tell whether the fibro/ECM axis's unusual gene-side flatness (0 of 20,000 subsamples as flat, **post-hoc**) is a property of the EMC arm or a property of those fourteen genes in this cache. A random-panel null varies *genes* with the specimens fixed and answers it directly. It must be frozen and hashed on its own terms — with the threshold and the direction of interest declared **before** running, precisely because this successor exists in response to a post-hoc observation and would otherwise inherit credibility it has not earned. **Declared expectation, stated up front so a null is not written as a surprise:** random panels drawn from a cache already enriched for these compartments may well be flatter still, in which case the fibro/ECM flatness is unremarkable and the honest report is a second negative.

A weaker option I record rather than recommend: W02d's own named successor, the endothelial-vs-fibro/ECM score correlation within the six EMC specimens. W02d already predicted n = 6 will leave it undecidable, and the leverage tables here support that — `GSM600936` is the top-leverage specimen on both axes but with opposite sign, which is suggestive and, at n = 6, not testable.
