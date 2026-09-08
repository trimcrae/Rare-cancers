<!-- collected 2026-09-08T04:42:44Z by campaign coordinator; agent id aa5ce465f54e92947; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aa5ce465f54e92947.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

# W02k — E2-limb calibration: does the last limb holding up the fibro/ECM `U` fire at its nominal α?

## Worker

- **Worker ID:** W02k (lane 2, re-dispatch after a rate-limited W02k attempt produced no report), OPUS-CAPACITY-CAMPAIGN-20260908. W02j's named successor.
- **Lane:** Lane 2 — EMC microenvironment. Calibration of the `E2` limb of W02i's frozen arm-to-arm rule.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I self-report as Claude Opus 5 (`claude-opus-5`), running as Claude Code in the Anthropic Cloud remote container. **This is a self-report and must not be treated as observed fact.** No served-model environment variable exists (`ANTHROPIC_MODEL` unset; the only Anthropic variable is `ANTHROPIC_BASE_URL`). The coordinator must extract the runtime model from the transcript. Literal output of the required `env` command is pasted below.
- **Write isolation:** READ-ONLY on `/home/user/Rare-cancers`, honoured. All execution under `/tmp/claude-0/w02k/`, **deleted before returning** (`rm -rf`; `ls` exits 2, `No such file or directory`). Nothing written, moved or deleted anywhere under the repository. No git write operation of any kind. `scripts/preflight.sh` not run. No network call, no paid API, no GPU. **W25 not read, not referenced.**

**`date -u` start:** `Tue Sep  8 04:34:14 UTC 2026` — **end:** `Tue Sep  8 04:37:57 UTC 2026`
**`git rev-parse HEAD` start / end:** `408b676aec3625a36917755662516232a27a1278` / `408b676aec3625a36917755662516232a27a1278` — **unchanged.** Verified rather than assumed: `git diff --name-only 408b676a HEAD | wc -l` → **0** (total, not just outside the campaign directory). Nothing I measured changed.
**`git status --porcelain` start / end:** empty / empty (literal `STATUS:[]` both times).
**Panel cache sha256 start / at runtime (in-script) / end:** `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` — **all three identical**, and the in-script check asserts equality against the declared constant.

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

W02i's frozen arm-to-arm rule scores `U (UNUSUAL)` only when **both** limbs fire: `E1` (EMC outside the closed interval of the three comparator arm points) and `E2` (`p_lo ≤ 0.05` against the exhaustive C(17,6)=12376 LGFMS six-specimen subsamples). Lane 2's one surviving claim — fibro/ECM `R_gene` = `U`, EMC 2.0460 — depends on both.

W02j's pre-declared D2 measured that **0.2950 of random 423-universe 14-gene panels fire `E1` BELOW on `R_gene`**, against a declared 0.05 bound. `E1` is a rank-1-of-4 test wearing an interval's clothes. That moved the entire weight of the claim onto `E2`, which **had never been calibrated**.

**The question I pursued, W02j's named successor:** for N random k=14 panels drawn from the same 423-gene non-marker universe, what fraction have `p_lo ≤ 0.05`? It is open because `E2`'s nominal α is 0.05 **by construction only** — that rate is guaranteed only if the six EMC arrays are exchangeable with six LGFMS arrays for this statistic. Nothing in the lane has ever tested that, and any gene-set-independent offset between the EMC arm and LGFMS subsamples would inflate one tail for **every** panel at once.

---

## Prior-work check

| # | command | what it showed |
|---|---|---|
| 1 | `rg -n -i "E2.limb\|limb calibration\|p_lo\|12376\|false.fire" --glob '!.git' --glob '!…campaign…/**'` | Zero relevant hits. Every hit is a substring collision — `keep_lo` in `nr4a3_fep.py`, `PMC12376927` in `lint_citation_types.py`, `PPR/PPR1237662` in the method-watch files, `exp_lof` in `nr4a-safety-genetics.json`. **No E2/`p_lo`/12376 calibration exists in the tracked corpus.** |
| 2 | `rg -n -i "R_gene\|arm-to-arm\|exhaustive.*subsample" --glob '!.git' --glob '!…campaign…/**'` | Zero hits for `R_gene`, `arm-to-arm` or an exhaustive-subsample scheme. All hits are `per_gene` substring collisions in the fusion-output and MTAP/PRMT5 manuscripts and `scratchpad/aut-cov-001/`. **The statistic does not exist outside this campaign.** |
| 3 | `rg -n -i "E2 limb\|p_lo\|12376" /tmp/claude-0/frozen-corpus/extracted/corpus/` | Same picture in the verified frozen corpus (`rc`/`stamp_log`/`PMC12376927`/`PPR1237662` collisions only). Confirms this is not locally-absent-but-known prior art. Corpus read only, never written. |
| 4 | `git ls-files \| rg -i "expression-panel\|w02"` | Ten lane-2 campaign reports, W02j the latest, and it names this successor explicitly. |
| 5 | read `W02j-retired-marker-set-control.md` **in full** (frozen docstring, D2 result, Next-concrete-action) and `W02i-comparator-arm-decomposition.md` **in full** (frozen docstring, R4 verdict table, full inline script) | Loader and the three statistic bodies reused **byte-for-byte**; W02i's fibro/ECM verdict row taken as the control target. |
| 6 | read `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md` in full, including both "Known, measured, and NOT worth rediscovering" sections | Nothing there touches this question. I did not re-measure the 0-of-89 resolution rate, did not touch `origin/literature-cache`, ran no pytest and no preflight, and touched none of: the clinical registry, PUB-ASO/Qeios frozen deliverables, the NR4A Perspective refusal, Brenca, Hofvander, the paired-Davis negative, the rejected registry-classification paper, or any unrecovered pazopanib/anthracycline/sunitinib/trabectedin/Wagner/CTARC source. **No network call. No expression matrix fetched. No denied route probed, replayed or routed around.** GSE24369 rediscovery is not new data and I claim none. |

Per the brief, sibling campaign reports are not repository evidence; W02i and W02j are my *inputs*, not my prior art. This exact test is unrun.

---

## Method and inputs

**SUBSTRATE LIMIT, stated up front and not as a gap to close.** Sole input: the committed panel cache `/home/user/Rare-cancers/research/modalities/emc-expression-panels.json` (`generated_utc 2026-08-29T12:51:32+00:00`, sha256 `123bd05a…f336bd9`, verified at start, in-script, and at end). It is **not an expression matrix**. The GSE24369 series matrix is not committed and fetching it is **DENIED**; no attempt, probe or workaround was made. Field used: `gene_reads[SYM]["GSE24369_series_matrix.txt.gz"].per_sample[].array_percentile` — a **within-array rank**, not an abundance. No other file was read.

- **Platform:** GPL6244 (`GSE24369`), **464 genes complete-case × 35 samples**, classes `{EMC 6, LGFMS 17, desmoid_fibromatosis 6, fibrosarcoma 6}`, asserted in-script.
- **Statistic:** `R_gene = k·Σf_i²`, `f_i = Cov(g_i,s)/(k·Var(s))`. The `r_gene` / `r_var` / `mean_pair_r` bodies and the complete-case loader are **copied byte-for-byte from W02i's returned script** (as W02j also did). `r_var` and `mean_pair_r` are carried only so the control row reproduces in full; they enter no calibration.
- **Vectorisation and its equivalence proof.** 400 × 12376 = 4.95M evaluations is beyond the scalar function's budget, so I added `r_gene_batch`, the identical algebra broadcast over all 12376 column-subsets. It was **not trusted on assertion**: before any calibration number, the run compares it element-by-element against the verbatim scalar `r_gene` over all 12376 combos, on the fibro/ECM panel and on one random panel, with an abort on failure. Both maxima printed **`0.000e+00`** — bit-identical, not merely within tolerance.
- **Subsampling:** LGFMS enumerated **exhaustively**, all C(17,6)=12376 (asserted) — **seed-free on the LGFMS side**. The only seeded object is the panel draw.
- **Universe:** 464 complete-case genes minus the 41 marker genes present (immune 12 + endothelial 6 + fibroECM 14 + tumour 9) = **423**, asserted `== 423` so it is comparable to W02j's D2. Identical construction to W02j's D2 and W02g.
- **Draw:** N = 400 panels, k = 14, seed 20260908 (numpy `default_rng`) — the same N, k and seed W02j specified.
- **Tools:** Python 3.11.15, numpy 2.4.6, Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w02k`. No scipy, no network, no paid API, no GPU.

### Pre-declaration integrity

The complete pre-declaration is the script's module docstring, **written in full before the first execution**; there was exactly one execution.

| moment | sha256 of `/tmp/claude-0/w02k/w02k.py` |
|---|---|
| **before run** (`sha256sum`) | `c3d9bf7ccdebd0e24e079e8bbddc806d8af090b7d640f6c10902b7ad17643f56` |
| **at runtime** (script hashing itself, first line of output) | `c3d9bf7ccdebd0e24e079e8bbddc806d8af090b7d640f6c10902b7ad17643f56` |
| **at runtime, re-read at end of run** (last lines of output) | `c3d9bf7ccdebd0e24e079e8bbddc806d8af090b7d640f6c10902b7ad17643f56` |
| **after run** (`sha256sum`) | `c3d9bf7ccdebd0e24e079e8bbddc806d8af090b7d640f6c10902b7ad17643f56` |

**All identical. The result is NOT VOID.**

**"Materially" given a number IN ADVANCE, quoted from the docstring:** *"With N = 400 the binomial standard error at p = 0.05 is sqrt(0.05\*0.95/400) = 0.0109. I therefore declare, now, a three-way call on F_E2: **DEAD**: F_E2 >= 0.10 … it cannot be sampling noise at N = 400 … the lane's one surviving claim — the fibro/ECM U — IS WITHDRAWN. I PRE-COMMIT to headlining that outcome as a WITHDRAWAL, not as a nuance, in the same form W02i used to withdraw the endothelial finding. **CALIBRATED**: F_E2 <= 0.075 … E2 is behaving at or near its nominal alpha, the fibro/ECM U retains the one limb it still rests on, and it stands exactly as W02i and W02j left it … Calibrated is NOT strengthened. **INTERMEDIATE**: 0.075 < F_E2 < 0.10. Neither call is earned … I will not move the threshold."*

**My expectation, quoted:** *"I expect DEAD, and I should say why, because if it fires I do not want it read as insight … E2 resamples ONE arm … any systematic offset between the EMC six arrays and LGFMS arrays … shifts EVERY panel's EMC value the same way and inflates one tail for every panel at once. AGAINST my lean … W02j's D1 showed EMC's all-464-gene R_gene (11.2313) sits INSIDE the LGFMS subsample bulk (p_lo 0.29880) … So CALIBRATED is a genuinely live outcome and I will report it, in full, as the surviving-claim outcome, without hedging it into a weakness."*

---

## Result

# Headline: the fibro/ECM `U` is WITHDRAWN.

The `E2` limb fires at **0.2075** for random 14-gene panels containing no fibro/ECM content, against its nominal α of 0.05 and my pre-declared DEAD threshold of 0.10. With W02j's `E1` already measured at 0.2950, **neither limb of W02i's rule carries information about the fibro/ECM gene set.** Lane 2's one surviving claim does not survive. This is a withdrawal, in the same form W02i used to withdraw the endothelial finding — not a nuance, not a caveat, not a narrowing.

### R1 — Control: W02i/W02j reproduced BEFORE any calibration number — `PRIMARY`

| axis | k | `R_gene` | taken | `R_var` | taken | `mean_r` | taken | all match |
|---|---|---|---|---|---|---|---|---|
| fibro/ECM | 14 | 2.0460 | 2.0460 | 3.0441 | 3.0441 | 0.5168 | 0.5168 | **True** |
| endothelial | 6 | 1.1729 | 1.1729 | 1.3934 | 1.3934 | 0.8124 | 0.8124 | **True** |

W02i's `R_gene` verdict rows, recomputed in full, verbatim from the run:

```
fibroECM     reproduced=True | mine EMC 2.0460 LGFMSmed 4.3448 des 5.3457 fib 5.1089 side BELOW  p_lo 0.00008 rank 1 U || W02i EMC 2.0460 LGFMSmed 4.3448 des 5.3457 fib 5.1089 p_lo 0.00008 rank 1 U
endothelial  reproduced=True | mine EMC 1.1729 LGFMSmed 1.2528 des 1.4393 fib 1.1724 side INSIDE p_lo 0.20296 rank 2 N || W02i EMC 1.1729 LGFMSmed 1.2528 des 1.4393 fib 1.1724 p_lo 0.20296 rank 2 N
CONTROL OVERALL LIKE-FOR-LIKE = True
```

Every required control value — the six EMC statistics and the full fibro/ECM verdict row (EMC 2.0460, LGFMSmed 4.3448, desmoid 5.3457, fibrosarcoma 5.1089, `p_lo` 0.00008, rank 1, `U`) — matches at 5e-5. This is like-for-like.

### R2 — Equivalence proof of the accelerated evaluator — `PRIMARY` (a precondition, not a finding)

```
fibroECM panel             : max |scalar - batch| over all 12376 combos = 0.000e+00  (bound 1e-9) -> True
one random 14-gene panel   : max |scalar - batch| over all 12376 combos = 0.000e+00  (bound 1e-9) -> True
EQUIVALENCE HOLDS. The batched evaluation is the same statistic.
```

### R3 — The calibration — `PRIMARY` (a computation actually executed)

Universe 423 genes (asserted), N = 400 panels, k = 14, seed 20260908, LGFMS side exhaustive and seed-free. 400 of 400 panels evaluated, 4.3 s, 0.011 s/panel.

| quantity | pre-declared status | nominal / expected | **observed** |
|---|---|---|---|
| **`F_E2`** — fraction with `p_lo ≤ 0.05` | **PRIMARY** | 0.05 | **0.2075** (83 of 400) |
| `F_MIN` — fraction with `p_lo = 1/12377`, i.e. EMC below **all** 12376 subsamples (the exact event fibro/ECM achieved) | SECONDARY | 8.08e-5 (0.032 panels) | **0.0375** (15 of 400) |
| `F_U` — fraction with `E1`-BELOW **and** `p_lo ≤ 0.05` (the full W02i rule's false-`U` rate) | SECONDARY | ≤ 0.05 | **0.1500** |
| `F_HI` — mirror upper tail, `p_hi ≤ 0.05` | SECONDARY, descriptive | 0.05 | **0.0675** |

`p_lo` distribution over the 400 panels: min 0.00008, p05 0.00040, p25 0.07964, p50 0.38414, p75 0.70750, max 1.00000.

### R4 — The pre-declared call, verbatim from the run — `PRIMARY`

```
DEAD if F_E2 >= 0.100 ; CALIBRATED if F_E2 <= 0.075 ; INTERMEDIATE otherwise.
CALL: DEAD — the E2 limb fires at 0.2075 for panels with no fibro/ECM content, >= 0.10.
      W02i's rule has NO limb carrying information about the fibro/ECM gene set
      (E1 measured at 0.2950 by W02j; E2 measured at 0.2075 here).
      THE FIBRO/ECM U IS WITHDRAWN. This is a WITHDRAWAL, not a nuance.
```

0.2075 is 4.15× the nominal α and **15.4 binomial SE** above 0.05 at N = 400. It is not sampling noise, and the threshold was fixed before the number existed.

### R5 — What this says, and what it does not

**(a) The withdrawal, stated plainly.** W02i reported *"fibro/ECM `R_gene` → U (UNUSUAL), EMC 2.0460 below all three comparator arms and below all but zero of 12376 exhaustive LGFMS six-specimen subsamples (`p_lo` = 0.00008)."* **That row is now withdrawn as evidence of anything about fibro/ECM genes in EMC.** The two limbs that produce it have measured false-fire rates of 0.2950 (`E1`, W02j) and 0.2075 (`E2`, here) on gene panels containing no marker genes at all, and the joint rule returns `U` for **15% of random panels** (`F_U`). A verdict machine that says UNUSUAL about one panel in seven, drawn at random from a universe with no fibro/ECM content, has not identified anything about the panel it was pointed at. Lane 2's last surviving claim is gone.

**(b) The most damning single number is `F_MIN`, and it is a secondary that only qualifies — it does not carry the call.** The fibro/ECM row's headline was not merely `p_lo ≤ 0.05`; it was the **minimum attainable** value, EMC below *every one* of the 12376 subsamples. Under a correctly calibrated `E2` that event has rate 1/12377 and should appear in **0.032 of 400 panels**. It appeared in **15**. The specific extremity that made the fibro/ECM row look like a discovery is reached by **3.75% of random gene panels** — roughly 460× its nominal rate. The `p_lo` = 0.00008 figure was never a small probability; it was a floor that the EMC arm reaches routinely.

**(c) The failure is directional, which points at the arm rather than the gene sets.** `F_E2` = 0.2075 against `F_HI` = 0.0675: the lower tail over-fires by a factor of ~4, the upper tail is close to nominal. EMC's `R_gene` is systematically low relative to LGFMS six-specimen subsamples **for arbitrary gene panels**. That is a property of the EMC arm's six arrays versus LGFMS arrays under this statistic, and it is gene-set-independent by construction, since the panels were drawn at random from the non-marker universe. **This substrate cannot say why** — batch, array processing run, scan date, tumour cellularity and specimen handling are all confounded with disease class in this deposit and none is separable here. I name them as candidates and claim none.

**(d) My expectation was right, and I flag that as the weaker kind of correctness.** I pre-declared DEAD as my lean, with reasoning about single-arm resampling written down before the run. It fired. But I also pre-declared the argument against my own lean — W02j's D1 showing EMC's all-464-gene `R_gene` sitting comfortably inside the LGFMS bulk at `p_lo` 0.29880 — and that argument was **wrong in a way worth recording**: an arm-level offset visible at 20% of random k=14 panels evidently does not show up as an extreme all-464-gene row, because the k=464 statistic is a different and numerically unstable object (W02j already flagged it). The lesson for the lane is that D1 was not a valid substitute for this calibration, and nobody should have treated it as reassurance.

**(e) What is *not* withdrawn.** W02j's substantive finding stands unchanged: neither retired marker set reproduces the fibro/ECM BELOW-and-outside signature, and W02j's refutation of the global-arm `mean_r` explanation (immune puts EMC last of four; D1 puts EMC third of four) is untouched by this run. So is W02i's endothelial withdrawal. What this run removes is the inferential status of the fibro/ECM `U` — not any measured number. **EMC's fibro/ECM `R_gene` really is 2.0460 and really is below all 12376 LGFMS subsamples. That description is true and remains true. What is withdrawn is the claim that it is unusual.**

**(f) Nothing biological, at any point.** `array_percentile` is a within-array rank; six arrays are not six patients; only three comparator arms exist. Nothing here was ever an EMC efficacy, safety, selectivity or clinical-readiness claim, and the withdrawal of an association does not create one.

---

## Validation evidence

**RUN.**

| # | command | exit | verbatim key output |
|---|---|---|---|
| 1 | `python3 -c "import numpy,sys;print(...)"; uname -srm` | 0 | `numpy 2.4.6 python 3.11.15`; `Linux 6.18.44-fc-v24 x86_64` |
| 2 | `sha256sum research/modalities/emc-expression-panels.json` (start) | 0 | `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` |
| 3 | `sha256sum /tmp/claude-0/w02k/w02k.py` (before run) | 0 | `c3d9bf7ccdebd0e24e079e8bbddc806d8af090b7d640f6c10902b7ad17643f56` |
| 4 | `cd /tmp/claude-0/w02k && time python3 w02k.py > out.txt 2>&1` | **0** (`EXIT=0`) | `real 0m5.203s`; full output reproduced as R1–R4 |
| 5 | `sha256sum /tmp/claude-0/w02k/w02k.py` (after run) | 0 | `c3d9bf7c…7643f56` — **identical to #3 and to both in-script self-hashes** |
| 6 | in-script source hash (start of run and end of run) | — | `123bd05a…f336bd9` both times; `SOURCE sha256 MATCHES DECLARED = True` (an `assert`, so a mismatch would have been a non-zero exit) |
| 7 | `sha256sum research/modalities/emc-expression-panels.json` (end) | 0 | `123bd05a…f336bd9` |
| 8 | in-script assertions | — | `X.shape[0]==464`; arm sizes 6/17/6/6; `len(combos)==12376`; realised k 12/6/14/9 with `dropped=none`; `len(UNIV)==423`; batch/scalar equivalence — all passed (any failure aborts non-zero) |
| 9 | control reproduction check | — | `CONTROL OVERALL LIKE-FOR-LIKE = True` |
| 10 | `git rev-parse HEAD` (start / end) | 0 | `408b676a…` / `408b676a…` — **unchanged** |
| 11 | `git diff --name-only 408b676a HEAD \| wc -l` | 0 | **`0`** — nothing in the tree changed at all during this run |
| 12 | `git status --porcelain` (start / end) | 0 | empty / empty |
| 13 | `rm -rf /tmp/claude-0/w02k && ls -d /tmp/claude-0/w02k` | 2 | `ls: cannot access '/tmp/claude-0/w02k': No such file or directory` — scratch deleted |
| 14 | `df -h /` | 0 | `/dev/vda 252G 18G 20G 48% /` |

**PROPOSED (NOT RUN):** any repair to W02i's rule (a permutation-based `E2`, an EMC-vs-comparator exchangeability test, a panel-wise empirical null); any joint arm-varying and gene-varying null; any GPL3290 cross-check; anything on the GSE24369 series matrix (uncommitted, egress **DENIED**). None executed, none claimed, none proposed as a repair to the repository. `scripts/preflight.sh` not run (brief and dispatch forbid it); no repository test tier invoked, because I changed no repository file. **No content-policy refusal was encountered in this unit.**

**Script, returned inline (not written into the tree).** The complete file whose sha256 is `c3d9bf7ccdebd0e24e079e8bbddc806d8af090b7d640f6c10902b7ad17643f56` was `/tmp/claude-0/w02k/w02k.py`, since deleted. Its module docstring is the frozen pre-declaration.

```python
"""
W02k — OPUS-CAPACITY-CAMPAIGN-20260908, lane 2.  W02j's NAMED SUCCESSOR.

COMPLETE PRE-DECLARATION.  Written in full BEFORE the first execution.  The file is sha256'd
before the run, hashes itself at runtime, and is sha256'd again after.  If any of the three
differ the result is VOID and I will say so.  Exactly one execution is intended.

============================================================================================
QUESTION
============================================================================================
W02i produced lane 2's ONE surviving claim: fibro/ECM R_gene -> U (UNUSUAL), EMC 2.0460 below
all three comparator arm points and below every one of the 12376 exhaustive LGFMS six-specimen
subsamples (p_lo = 0.00008).  The verdict U requires BOTH limbs of W02i's rule:

  E1 RANGE     : EMC lies OUTSIDE the closed interval [min P, max P] of the three comparator
                 point values P = { median(LGFMS 12376 subsamples), desmoid, fibrosarcoma }.
  E2 LGFMS TAIL: p_lo = (#{LGFMS subsample <= EMC} + 1) / (12376 + 1) <= ALPHA = 0.05.

W02j then ran a pre-declared calibration (its D2) of the E1 limb alone and measured that
**0.2950 of random 423-universe 14-gene panels fire E1 BELOW on R_gene**, against a declared
0.05 bound.  E1 is therefore a rank-1-of-4 test wearing an interval's clothes, and W02j's
conclusion — which I take as my starting point rather than re-deriving — is that the ENTIRE
weight of the fibro/ECM U now rests on the E2 limb alone.  E2 HAS NEVER BEEN CALIBRATED.

W02j named exactly one successor and called it the only remaining test on this substrate that
can FALSIFY the surviving claim rather than decorate it:

  RUN THE E2-LIMB CALIBRATION.  For each of N random k=14 panels drawn from the same 423-gene
  non-marker universe, compute EMC's R_gene and the EXHAUSTIVE C(17,6) = 12376 LGFMS
  six-specimen subsample distribution, and record the fraction of panels with p_lo <= 0.05.

Why this can kill the claim and D2 could not.  E2's nominal alpha is 0.05 by construction: if
the six EMC arrays were exchangeable with six LGFMS arrays for the purpose of this statistic,
then for a random gene panel EMC's R_gene would be an ordinary draw from the same distribution
the 12376 subsamples trace out, and p_lo <= 0.05 would occur in about 5% of panels.  If it
occurs far more often, E2 is not measuring anything about the fibro/ECM gene set: it is
measuring a gene-set-INDEPENDENT difference between the EMC arm and LGFMS six-array
subsamples (batch, platform run, tumour cellularity, array processing — none of which this
substrate can distinguish).  With E1 already known to fire at ~30%, an E2 firing far above
0.05 leaves the fibro/ECM U with no limb that carries information about fibro/ECM genes.

============================================================================================
INPUT — SUBSTRATE LIMIT, stated as a limit and not as a gap to close
============================================================================================
Sole input: the committed panel cache
  /home/user/Rare-cancers/research/modalities/emc-expression-panels.json
  expected sha256 123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9
verified at start, AT RUNTIME (in this script), and at end.  This is NOT an expression matrix.
The GSE24369 series matrix is not committed and fetching it is DENIED; no attempt, probe or
workaround is made anywhere in this unit.  No network, no paid API, no GPU, no wet lab, no new
deposit, no other file is read.
Field used: gene_reads[SYM][GSE24369_series_matrix.txt.gz].per_sample[].array_percentile — a
WITHIN-ARRAY RANK, not an abundance.  Six arrays are not six patients.  Only three comparator
arms exist, so ANY rank statistic here is DESCRIPTIVE ONLY.  Anything found is an ASSOCIATION
at most: no mechanism, no efficacy, no safety, no selectivity, no clinical readiness.

============================================================================================
STATISTIC — reused VERBATIM from W02i so this is like-for-like
============================================================================================
For a panel of k genes scored on the n specimens of one arm, s = mean over genes:
  R_gene = k * sum_i f_i^2 ,  f_i = Cov(g_i, s) / (k * Var(s))        (even = 1.0)
The r_gene / r_var / mean_pair_r function bodies below are copied BYTE-FOR-BYTE from W02i's
returned script (as W02j also did), and so is the complete-case loader (464 genes x 35 samples
on GPL6244).  r_var and mean_pair_r are carried only so the CONTROL row can be reproduced in
full; they enter no calibration.

VECTORISATION AND ITS EQUIVALENCE PROOF.  400 panels x 12376 combinations is 4.95M evaluations,
which the scalar r_gene cannot do in the time budget.  I therefore ALSO define r_gene_batch,
which applies the IDENTICAL algebra to all 12376 combinations at once with numpy broadcasting.
It is NOT trusted on assertion: before any calibration number is computed, the run asserts
  max |r_gene_batch(...) - [r_gene(...) for every one of the 12376 combos]| < 1e-9
on the fibro/ECM panel AND on one random universe panel, and PRINTS both maxima.  If either
assertion fails the run aborts non-zero and no calibration number exists.  The scalar verbatim
r_gene remains the definition; r_gene_batch is only an accelerated evaluation of it.

============================================================================================
ARMS AND SUBSAMPLING — identical to W02i / W02j
============================================================================================
  EMC                     n = 6   point value (the arm under test)
  desmoid_fibromatosis    n = 6   point value
  fibrosarcoma            n = 6   point value
  LGFMS                   n = 17  EXHAUSTIVE enumeration of all C(17,6) = 12376 six-specimen
                                  subsamples => SEED-FREE on the LGFMS side, not Monte-Carlo.
                                  Asserted in-script.  Full-arm n=17 is not used at all here.
The only seeded object in this unit is the RANDOM PANEL DRAW.

UNIVERSE (identical construction to W02j's D2, which is W02g's exclusion):
  the 464 complete-case genes MINUS every gene named in the four marker sets (immune 12 +
  endothelial 6 + fibroECM 14 + tumour 9) that is present in the 464.  W02j measured this
  universe at 423 genes; the realised size is asserted == 423 and printed.  If it is not 423
  the run aborts and the calibration is not comparable to W02j's D2.

  N = NPANEL = 400 panels, k = 14 (the fibro/ECM size), seed = 20260908 (numpy default_rng),
  the same N, k and seed W02j used and the cost W02j priced at ~150 s.  Sampling without
  replacement within a panel; panels are independent draws and may repeat genes across panels.

============================================================================================
QUANTITIES COMPUTED — declared here, nothing added later
============================================================================================
For each random panel:
  emc      = r_gene on the 6 EMC arrays
  sub[]    = r_gene on all 12376 LGFMS six-specimen subsamples
  p_lo     = (#{sub <= emc} + 1) / 12377          <- the E2 statistic, LOWER tail
  p_hi     = (#{sub >= emc} + 1) / 12377
  E1 side  = BELOW / INSIDE / ABOVE w.r.t. [min P, max P], P as above

PRIMARY  (the quantity W02j's successor statement names):
  F_E2 = fraction of the N panels with p_lo <= 0.05.

SECONDARY, ALSO PRE-DECLARED (reported alongside; they may QUALIFY the primary reading but
they CANNOT overturn it, and no verdict is taken from them):
  F_MIN  = fraction with p_lo == 1/12377, i.e. EMC below ALL 12376 subsamples — the EXACT event
           the fibro/ECM row achieved (p_lo 0.00008).  Under a correct calibration its rate is
           1/12377 = 8.08e-5, so the expected count in 400 panels is 0.032.
  F_U    = fraction with E1-BELOW AND p_lo <= 0.05 — the full W02i rule's U rate for a random
           panel.  This is the false-U rate of the actual rule that produced the claim.
  F_HI   = fraction with p_hi <= 0.05 — the mirror upper tail.  Descriptive: it says whether
           any E2 miscalibration is DIRECTIONAL (EMC systematically low) or merely a
           heavier-tailed EMC arm in both directions.
Distributional context printed and not tested: percentiles of the N p_lo values.

============================================================================================
DECISION RULE — THRESHOLD FIXED IN ADVANCE, "MATERIALLY" GIVEN A NUMBER BEFORE THE RUN
============================================================================================
W02j's reading, in W02j's own words: "if that fraction materially exceeds 0.05, the fibro/ECM
U is dead ... If the fraction is at or below 0.05, the U is calibrated and the lane has said
everything this substrate can support."

"Materially" must be a number, and it must be fixed before I see one.  With N = 400 the
binomial standard error at p = 0.05 is sqrt(0.05*0.95/400) = 0.0109.  I therefore declare,
now, a three-way call on F_E2:

  DEAD        : F_E2 >= 0.10.  That is >= 2x the nominal alpha and >= 4.6 SE above 0.05 — it
                cannot be sampling noise at N = 400.  READING, PRE-COMMITTED: the E2 limb is
                firing far above its nominal rate for panels with no fibro/ECM content, so
                neither limb of W02i's rule carries information about the fibro/ECM gene set,
                and the lane's one surviving claim — the fibro/ECM U — IS WITHDRAWN.  I
                PRE-COMMIT to headlining that outcome as a WITHDRAWAL, not as a nuance, in the
                same form W02i used to withdraw the endothelial finding.
  CALIBRATED  : F_E2 <= 0.075.  That is within ~2.3 SE of the nominal 0.05.  READING: E2 is
                behaving at or near its nominal alpha, the fibro/ECM U retains the one limb it
                still rests on, and it stands exactly as W02i and W02j left it — a confirmation
                under a frozen rule of a post-hoc W02f observation, resting on a single limb,
                on a rank table, with no biological content.  Calibrated is NOT strengthened.
  INTERMEDIATE: 0.075 < F_E2 < 0.10.  Neither call is earned.  Reported as INTERMEDIATE with
                both halves stated, the U retained but flagged as resting on a limb whose
                measured false-fire rate is above nominal.  I will not move the threshold.

No multiplicity correction is applied and none is needed: there is ONE primary number.
No threshold may be moved and no tail re-chosen after a number is seen.  Anything observed
after the numbers is labelled [POST-HOC] and scores nothing.

============================================================================================
CONTROL ROW REQUIRED BY DISPATCH — reproduce W02i/W02j BEFORE any calibration number
============================================================================================
Step 1, before a single random panel is drawn, reproduces:
  EMC values : R_gene fibroECM 2.0460 / endothelial 1.1729 ; R_var 3.0441 / 1.3934 ;
               mean_r 0.5168 / 0.8124        (W02f/W02g/W02h, via W02i, re-checked by W02j)
  W02i's fibro/ECM R_gene VERDICT ROW: EMC 2.0460, LGFMSmed 4.3448, desmoid 5.3457,
               fibrosarcoma 5.1089, p_lo 0.00008, rank 1, outcome U
  and the endothelial R_gene verdict row: EMC 1.1729, LGFMSmed 1.2528, desmoid 1.4393,
               fibrosarcoma 1.1724, p_lo 0.20296, rank 2, outcome N
Every one is asserted-by-printing with a match flag (tolerance 5e-5).  If the control does not
reproduce, the run is reported NOT LIKE-FOR-LIKE and NO calibration conclusion is drawn.

============================================================================================
MY EXPECTATION, DECLARED IN WRITING IN ADVANCE so neither outcome can be staged as a surprise
============================================================================================
I expect DEAD, and I should say why, because if it fires I do not want it read as insight.
Two reasons, both stated now.  (1) E2 resamples ONE arm.  It asks "is EMC's R_gene extreme
relative to LGFMS specimen sampling", and any systematic offset between the EMC six arrays and
LGFMS arrays — of which there are many candidates on a 2010-era two-platform deposit, none of
them separable here — shifts EVERY panel's EMC value the same way and inflates one tail for
every panel at once.  (2) The observed direction is already suspicious: W02i found EMC top of
four arms on mean_r for BOTH marker sets, and W02j's D1 nonetheless found EMC only third of
four on all-464-gene mean_r, so the EMC arm's rank profile is not globally flat; but nothing
measured so far excludes an arm-level offset in R_gene specifically.
AGAINST my lean, stated so it is a real prediction and not a hedge: W02j's D1 showed EMC's
all-464-gene R_gene (11.2313) sits INSIDE the LGFMS subsample bulk (p_lo 0.29880, side BELOW
but not outside the comparator interval).  If the EMC arm carried a global R_gene deflation
strong enough to make E2 fire at 30%, the all-gene row should have looked more extreme than
that.  So CALIBRATED is a genuinely live outcome and I will report it, in full, as the
surviving-claim outcome, without hedging it into a weakness.
I have no stake in either result.  I will report whichever prints.

============================================================================================
STOP CONDITION
============================================================================================
Stop the moment the control block and the single primary number F_E2 (with its three declared
secondaries) have printed on ONE execution with matching before / at-runtime / after script
sha256 and matching source sha256 at all three moments.  No further statistic is added, no
threshold moved, no tail re-chosen, no post-hoc test run, no second execution.
"""
import hashlib, json, itertools, time
import numpy as np

SRC = "/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
SRC_SHA = "123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9"
PLAT = "GSE24369_series_matrix.txt.gz"
ALPHA = 0.05
SEED = 20260908
NPANEL = 400
KPANEL = 14
DEAD_AT = 0.10
CAL_AT = 0.075

MARK = {
 "immune": ["PTPRC","CD2","CD3D","CD3E","CD8A","CD68","CD163","CSF1R","ITGAM","HLA-DRA","MS4A1","GZMB"],
 "endothelial": ["PECAM1","VWF","CDH5","KDR","FLT1","MCAM"],
 "fibroECM": ["COL1A1","COL1A2","COL3A1","COL5A1","DCN","LUM","FAP","THY1","POSTN","FN1","PDGFRA","PDGFRB","ACTA2","COL11A1"],
 "tumour": ["NR4A3","PPARG","RET","INSM1","SYP","CHGA","ENO2","KIT","CD24"],
}
TAKEN_RGENE = {"fibroECM": 2.0460, "endothelial": 1.1729}
TAKEN_RVAR  = {"fibroECM": 3.0441, "endothelial": 1.3934}
TAKEN_MEANR = {"fibroECM": 0.5168, "endothelial": 0.8124}
TAKEN_W02I = {
  "fibroECM":    dict(emc=2.0460, lg=4.3448, des=5.3457, fib=5.1089, p_lo=0.00008, rank=1, out="U"),
  "endothelial": dict(emc=1.1729, lg=1.2528, des=1.4393, fib=1.1724, p_lo=0.20296, rank=2, out="N"),
}

self_sha = hashlib.sha256(open(__file__, 'rb').read()).hexdigest()
src_sha = hashlib.sha256(open(SRC, 'rb').read()).hexdigest()
print("SELF sha256 (as read at runtime) =", self_sha)
print("SOURCE sha256 (at runtime)       =", src_sha)
print("SOURCE sha256 MATCHES DECLARED   =", src_sha == SRC_SHA)
assert src_sha == SRC_SHA, "source file changed under me"
d = json.load(open(SRC))
print("SOURCE generated_utc =", d.get("generated_utc"))

# ---- loader: complete-case genes on GPL6244 (copied unchanged from W02i) ----
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
X = np.asarray(rows, float)
assert X.shape[0] == 464, X.shape
cnt = {c: klass.count(c) for c in sorted(set(klass))}
print("PLATFORM %s | complete-case %d genes x %d samples | %s" % (PLAT, X.shape[0], X.shape[1], cnt))
idx = {g: i for i, g in enumerate(names)}
ARMS = {c: np.array([i for i, k in enumerate(klass) if k == c]) for c in sorted(set(klass))}
assert len(ARMS["EMC"]) == 6 and len(ARMS["LGFMS"]) == 17
assert len(ARMS["desmoid_fibromatosis"]) == 6 and len(ARMS["fibrosarcoma"]) == 6

# ---- statistics: bodies copied unchanged from W02i (as W02j also did) ----
def r_gene(M):
    k, n = M.shape
    s = M.mean(0)
    vs = s.var(ddof=1)
    if vs <= 0: return None
    Mc = M - M.mean(1, keepdims=True)
    sc = s - s.mean()
    C = (Mc * sc).sum(1) / (n - 1) / k
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

# ---- accelerated evaluation of the SAME algebra over many column-subsets at once ----
# A[k, m, n] : k genes, m subsamples, n specimens each.  Returns (m,) of r_gene values.
def r_gene_batch(A):
    k, m, n = A.shape
    s = A.mean(0)                                  # (m, n)
    vs = s.var(1, ddof=1)                          # (m,)
    Ac = A - A.mean(2, keepdims=True)
    sc = s - s.mean(1, keepdims=True)              # (m, n)
    C = (Ac * sc[None, :, :]).sum(2) / (n - 1) / k # (k, m)
    f = C / vs[None, :]
    out = k * (f**2).sum(0)
    out[vs <= 0] = np.nan
    return out

combos = list(itertools.combinations(range(17), 6))
assert len(combos) == 12376
CIDX = np.asarray(combos, dtype=np.intp)           # (12376, 6)
print("\nLGFMS exhaustive six-specimen subsamples enumerated: %d (expected C(17,6)=12376)" % len(combos))
XL = X[:, ARMS["LGFMS"]]                           # (464, 17)
XE = X[:, ARMS["EMC"]]
XD = X[:, ARMS["desmoid_fibromatosis"]]
XF = X[:, ARMS["fibrosarcoma"]]

REAL = {}
for ax, gl in MARK.items():
    have = [g for g in gl if g in idx]
    miss = [g for g in gl if g not in idx]
    REAL[ax] = have
    print("SET %-12s declared k=%2d realised k=%2d  dropped=%s" % (ax, len(gl), len(have), miss if miss else "none"))

# ============ STEP 0: EQUIVALENCE PROOF for r_gene_batch (before any calibration number) ============
print("\n############ STEP 0 — r_gene_batch equivalence against the VERBATIM scalar r_gene ############")
rng0 = np.random.default_rng(SEED)
eq_ok = True
for lab, sel in [("fibroECM panel", np.array([idx[g] for g in REAL["fibroECM"]])),
                 ("one random 14-gene panel", rng0.choice(np.arange(464), size=14, replace=False))]:
    L = XL[sel]
    scal = np.array([r_gene(L[:, list(c)]) for c in combos], float)
    batch = r_gene_batch(L[:, CIDX])
    mx = float(np.nanmax(np.abs(scal - batch)))
    print("%-26s : max |scalar - batch| over all 12376 combos = %.3e  (bound 1e-9) -> %s"
          % (lab, mx, mx < 1e-9))
    eq_ok = eq_ok and (mx < 1e-9)
assert eq_ok, "r_gene_batch is NOT equivalent to the verbatim scalar r_gene; run aborted."
print("EQUIVALENCE HOLDS. The batched evaluation is the same statistic.")

# ============ STEP 1: CONTROL — reproduce W02i/W02j before any calibration number ============
print("\n############ STEP 1 — CONTROL: reproduce W02i/W02j (BEFORE any calibration number) ############")
ok = True
for ax in ["fibroECM", "endothelial"]:
    sel = [idx[g] for g in REAL[ax]]
    M = X[sel][:, ARMS["EMC"]]
    rc, rv, mr = r_gene(M), r_var(M), mean_pair_r(M)
    m1 = abs(rc-TAKEN_RGENE[ax]) < 5e-5; m2 = abs(rv-TAKEN_RVAR[ax]) < 5e-5; m3 = abs(mr-TAKEN_MEANR[ax]) < 5e-5
    ok = ok and m1 and m2 and m3
    print("%-12s k=%2d : R_gene %.4f vs TAKEN %.4f match=%s | R_var %.4f vs %.4f match=%s | mean_r %.4f vs %.4f match=%s"
          % (ax, M.shape[0], rc, TAKEN_RGENE[ax], m1, rv, TAKEN_RVAR[ax], m2, mr, TAKEN_MEANR[ax], m3))

def rgene_row(sel):
    sel = np.asarray(sel)
    emc = r_gene(X[sel][:, ARMS["EMC"]])
    des = r_gene(X[sel][:, ARMS["desmoid_fibromatosis"]])
    fib = r_gene(X[sel][:, ARMS["fibrosarcoma"]])
    a = r_gene_batch(XL[sel][:, CIDX])
    a = a[~np.isnan(a)]
    lg_pt = float(np.median(a))
    P = [lg_pt, des, fib]; lo, hi = min(P), max(P)
    side = "BELOW" if emc < lo else ("ABOVE" if emc > hi else "INSIDE")
    e1 = side != "INSIDE"
    n = len(a)
    p_lo = (int((a <= emc).sum()) + 1) / (n + 1)
    p_hi = (int((a >= emc).sum()) + 1) / (n + 1)
    e2 = p_lo <= ALPHA
    pts = sorted([("EMC", emc), ("LGFMSmed", lg_pt), ("desmoid", des), ("fibrosarcoma", fib)], key=lambda t: t[1])
    rank = [t[0] for t in pts].index("EMC") + 1
    out = "U" if (e1 and e2) else ("N" if (not e1 and not e2) else "P")
    return dict(emc=emc, lg=lg_pt, des=des, fib=fib, side=side, e1=e1, p_lo=p_lo, p_hi=p_hi,
                e2=e2, rank=rank, out=out, nsub=n)

print("\n--- CONTROL: W02i's R_gene verdict rows, recomputed ---")
for ax in ["fibroECM", "endothelial"]:
    r = rgene_row([idx[g] for g in REAL[ax]])
    t = TAKEN_W02I[ax]
    chk = (abs(r["emc"]-t["emc"]) < 5e-5 and abs(r["lg"]-t["lg"]) < 5e-5 and abs(r["des"]-t["des"]) < 5e-5
           and abs(r["fib"]-t["fib"]) < 5e-5 and abs(r["p_lo"]-t["p_lo"]) < 5e-5
           and r["rank"] == t["rank"] and r["out"] == t["out"])
    ok = ok and chk
    print("%-12s reproduced=%s | mine EMC %.4f LGFMSmed %.4f des %.4f fib %.4f side %s p_lo %.5f rank %d %s"
          " || W02i EMC %.4f LGFMSmed %.4f des %.4f fib %.4f p_lo %.5f rank %d %s"
          % (ax, chk, r["emc"], r["lg"], r["des"], r["fib"], r["side"], r["p_lo"], r["rank"], r["out"],
             t["emc"], t["lg"], t["des"], t["fib"], t["p_lo"], t["rank"], t["out"]))
print("CONTROL OVERALL LIKE-FOR-LIKE =", ok)
if not ok:
    print("!! CONTROL FAILED: NOT like-for-like with W02i/W02j; no calibration conclusion may be drawn.")

# ============ STEP 2: THE E2-LIMB CALIBRATION ============
excluded = set(g for gl in MARK.values() for g in gl if g in idx)
UNIV = [g for g in names if g not in excluded]
print("\n############ STEP 2 — E2-LIMB CALIBRATION ############")
print("Universe = %d complete-case genes minus %d marker genes present = %d genes (W02g/W02j exclusion)."
      % (X.shape[0], len(excluded), len(UNIV)))
assert len(UNIV) == 423, "universe is not 423 genes; not comparable to W02j's D2"
print("N=%d panels, k=%d, seed=%d, LGFMS side EXHAUSTIVE (12376, seed-free)." % (NPANEL, KPANEL, SEED))
uidx = np.array([idx[g] for g in UNIV], dtype=np.intp)
rng = np.random.default_rng(SEED)
t0 = time.time()
plo = np.empty(NPANEL); phi = np.empty(NPANEL); belw = np.zeros(NPANEL, bool); used = 0
for i in range(NPANEL):
    sel = rng.choice(uidx, size=KPANEL, replace=False)
    emc = r_gene(X[sel][:, ARMS["EMC"]])
    des = r_gene(X[sel][:, ARMS["desmoid_fibromatosis"]])
    fib = r_gene(X[sel][:, ARMS["fibrosarcoma"]])
    a = r_gene_batch(XL[sel][:, CIDX]); a = a[~np.isnan(a)]
    if emc is None or des is None or fib is None or len(a) == 0:
        plo[i] = np.nan; phi[i] = np.nan; continue
    n = len(a)
    plo[i] = (int((a <= emc).sum()) + 1) / (n + 1)
    phi[i] = (int((a >= emc).sum()) + 1) / (n + 1)
    lo = min(float(np.median(a)), des, fib)
    belw[i] = emc < lo
    used += 1
el = time.time() - t0
good = ~np.isnan(plo)
print("panels evaluated = %d of %d (%.1f s, %.3f s/panel)" % (used, NPANEL, el, el/NPANEL))

F_E2 = float((plo[good] <= ALPHA).mean())
PMIN = 1.0 / (len(combos) + 1)
F_MIN = float((plo[good] <= PMIN + 1e-12).mean())
F_U = float(((plo[good] <= ALPHA) & belw[good]).mean())
F_HI = float((phi[good] <= ALPHA).mean())

print("\n=== PRIMARY (pre-declared) ===")
print("F_E2 = fraction of random k=14 panels with p_lo <= %.2f  ==>  %.4f  (%d of %d)"
      % (ALPHA, F_E2, int((plo[good] <= ALPHA).sum()), int(good.sum())))
print("\n=== SECONDARY (pre-declared; qualify only, never overturn) ===")
print("F_MIN (p_lo == 1/12377, the exact event fibro/ECM achieved) = %.4f (%d of %d); "
      "expected under nominal calibration = %.4f (%.3f panels)"
      % (F_MIN, int((plo[good] <= PMIN+1e-12).sum()), int(good.sum()), PMIN, PMIN*good.sum()))
print("F_U   (E1-BELOW AND p_lo<=0.05 : the full W02i rule's false-U rate) = %.4f" % F_U)
print("F_HI  (mirror upper tail p_hi<=0.05)                                = %.4f" % F_HI)
print("p_lo distribution over panels: min %.5f  p05 %.5f  p25 %.5f  p50 %.5f  p75 %.5f  max %.5f"
      % (np.nanmin(plo), np.nanpercentile(plo, 5), np.nanpercentile(plo, 25), np.nanpercentile(plo, 50),
         np.nanpercentile(plo, 75), np.nanmax(plo)))

print("\n=== PRE-DECLARED THREE-WAY CALL ON F_E2 (thresholds fixed before the run) ===")
print("DEAD if F_E2 >= %.3f ; CALIBRATED if F_E2 <= %.3f ; INTERMEDIATE otherwise." % (DEAD_AT, CAL_AT))
if F_E2 >= DEAD_AT:
    print("CALL: DEAD — the E2 limb fires at %.4f for panels with no fibro/ECM content, >= %.2f."
          % (F_E2, DEAD_AT))
    print("      W02i's rule has NO limb carrying information about the fibro/ECM gene set")
    print("      (E1 measured at 0.2950 by W02j; E2 measured at %.4f here)." % F_E2)
    print("      THE FIBRO/ECM U IS WITHDRAWN. This is a WITHDRAWAL, not a nuance.")
elif F_E2 <= CAL_AT:
    print("CALL: CALIBRATED — F_E2 = %.4f <= %.3f, at or near the nominal alpha." % (F_E2, CAL_AT))
    print("      The fibro/ECM U retains its one remaining limb and stands as W02i/W02j left it:")
    print("      a frozen-rule confirmation of a post-hoc observation, on a single limb, on a rank")
    print("      table, with no biological content. CALIBRATED IS NOT STRENGTHENED.")
else:
    print("CALL: INTERMEDIATE — F_E2 = %.4f is between %.3f and %.3f; neither call is earned."
          % (F_E2, CAL_AT, DEAD_AT))
    print("      The U is retained but flagged: its one remaining limb fires above nominal.")

print("""
============================================================================================
No biological, mechanistic or clinical claim follows from any outcome above.  array_percentile
is a within-array rank; six arrays are not six patients; only three comparator arms exist and a
four-arm rank can never reach alpha=0.05, so every rank statistic here is DESCRIPTIVE ONLY.
There is no wet lab.  No EMC efficacy, safety, selectivity or clinical-readiness claim is made
or implied.  This is an ASSOCIATION at most.
============================================================================================""")
print("SELF sha256 re-read at end of run =", hashlib.sha256(open(__file__, 'rb').read()).hexdigest())
print("SOURCE sha256 re-read at end of run =", hashlib.sha256(open(SRC, 'rb').read()).hexdigest())
```

---

## Limitations

1. **SUBSTRATE LIMIT, restated as a limit.** The only input is a committed panel cache of 464 genes' `array_percentile` values on GPL6244. It is not an expression matrix; the matrix is not committed and fetching it is denied. Everything here is a statistic of a rank table.
2. **`array_percentile` is a within-array rank.** No absolute expression statement is possible, in either direction.
3. **Six arrays are not six patients.** Nothing here is patient-level or clinical, and no mechanism follows — including the withdrawal. **Association at most.** No EMC efficacy, safety, selectivity or clinical-readiness claim is made or implied.
4. **This calibration diagnoses the rule, not the biology.** It shows `E2` fires far above its nominal α for arbitrary gene panels. It does **not** show that EMC's fibro/ECM markers behave like other panels — that question is not answerable once the test used to ask it is known to be miscalibrated. **The right statement is "not evidence", not "shown to be nothing".**
5. **The cause of the miscalibration is UNKNOWN.** An arm-level offset between the EMC six arrays and LGFMS arrays under `R_gene` is what the numbers require; batch, scan date, array processing, tumour cellularity and specimen handling are all confounded with disease class in this deposit and none is separable on this substrate. I name them as candidates and claim none.
6. **N = 400 carries Monte-Carlo error of roughly ±0.020 on `F_E2`** at the observed value. That is an order of magnitude smaller than the gap between 0.2075 and the 0.10 threshold, so the call is not sensitive to it. `F_MIN` at 15/400 has a wide relative interval and is a **secondary** that qualifies rather than decides.
7. **The panel draw is seeded (20260908) and matches W02j's D2 seed**, so the two calibrations are not independent draws of the universe; they are, however, calibrations of *different limbs* and the shared seed makes them comparable rather than redundant.
8. **`F_HI` = 0.0675 is descriptive.** I declared it in advance as a directionality check only; it is close enough to nominal that I make no claim from it beyond "the failure is one-sided".
9. **Only three comparator arms exist**, fixed by the deposit, all other sarcomas and several fibroblastic. `E1` and `E3` are four-arm rank tests that can never reach α = 0.05; W02c's caution that the fibrosarcoma arm is a weak comparator stands.
10. **No repository file changed**, so no repository test tier applies. No preflight, no gate, no publication path, no graph or view touched. HEAD did not move; I verified rather than assumed.
11. **I authored no repair and propose none.** Whether W02i's `U` row is annotated anywhere outside this campaign directory is not something I checked or acted on; the greps in the prior-work check found no trace of `R_gene` in the tracked corpus, so the withdrawal has no known downstream consumer to correct — but "no known consumer" is UNKNOWN, not zero.

---

## Stop condition

**Declared in the frozen docstring before the run:** *"Stop the moment the control block and the single primary number F_E2 (with its three declared secondaries) have printed on ONE execution with matching before / at-runtime / after script sha256 and matching source sha256 at all three moments. No further statistic is added, no threshold moved, no tail re-chosen, no post-hoc test run, no second execution."*

**MET.** Control block, equivalence proof, `F_E2` and all three secondaries printed on the single execution (exit 0, 5.2 s). All four script hashes are `c3d9bf7c…7643f56`; all three source hashes are `123bd05a…f336bd9`. No statistic was added, no threshold moved, no tail re-chosen after seeing a number, no second run. Scratch deleted; returning immediately.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 12** (target ~40).
- **Wall clock: 3 min 43 s** of execution, `date -u` 04:34:14Z → 04:37:57Z (target ~40 min), plus report composition. Script runtime 5.2 s — far under W02j's ~150 s estimate, because vectorising `r_gene` across the 12376 combinations turned 4.95M scalar calls into 400 broadcast passes at 0.011 s/panel.
- Under target because W02i's loader and statistics were reusable verbatim and the question was a single pre-specified number. I did not pad.

---

## Next concrete action

**No viable successor in this lane, and W02j's judgment is confirmed rather than merely accepted.**

W02j wrote: *"After that test, and only after it, I agree lane 2 is finished on this substrate."* The test has been run and it killed the claim it was aimed at. **I say plainly that this supports W02j's assessment: lane 2 is finished on this substrate.**

The reason is structural, not a shortage of ideas. Lane 2 now has two withdrawn findings (endothelial, W02i; fibro/ECM, this run), one measured specificity failure of the `mean_r` limb (W02j's tumour row), and a rule whose two limbs have measured false-fire rates of 0.2950 and 0.2075. **The correct next question is not another statistic on this table — it is whether the EMC arm's six arrays are exchangeable with the comparator arrays at all, and that question cannot be asked from a 464-gene within-array-rank cache.** It needs the per-array covariates (scan date, batch, processing) or the full expression matrix, and both live in the uncommitted GSE24369 series matrix, whose retrieval is **DENIED**. Every other variant W02i and W02j enumerated — more arms, transcriptome-wide universes, abundance instead of rank, single-cell or spatial deconvolution — requires the same denied route or a new deposit.

The one thing a future worker could usefully do costs nothing scientific and is **not** a lane-2 research question: if the fibro/ECM `U` has been carried into any manuscript, view or graph node outside this campaign directory, that text needs the withdrawal applied. My greps found no occurrence of `R_gene` anywhere in the tracked corpus or the frozen corpus, so **as far as I could measure there is nothing to correct** — but I am read-only, I did not audit exhaustively, and absence of a grep hit is UNKNOWN, not proof of absence. That is a coordinator disposition, not a lane-2 investigation.
