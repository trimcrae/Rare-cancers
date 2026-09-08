<!-- collected 2026-09-08T03:38:26Z by campaign coordinator; agent id a5793e576f86f3f34; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a5793e576f86f3f34.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

# W02i — Is EMC unusual in making these marker sets flat, or is flatness a marker-set property every arm shows?

## Worker

- **Worker ID:** W02i (lane 2 refill), OPUS-CAPACITY-CAMPAIGN-20260908. W02h's named successor.
- **Lane:** Lane 2 — EMC microenvironment. Arm-to-arm comparison of the concentration/correlation decomposition.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I self-report as Claude Opus 5 (`claude-opus-5`), running as Claude Code in the Anthropic Cloud remote container. **This is a self-report and must not be treated as observed fact.** No served-model environment variable exists in the session (`ANTHROPIC_MODEL` is unset; the only Anthropic variable is `ANTHROPIC_BASE_URL`). The coordinator must extract the runtime model from the transcript.
- **Write isolation:** READ-ONLY on the Git tree, honoured. All execution under `/tmp/claude-0/w02i/`, **which was deleted before returning** (`rm -rf`; `ls` confirms `No such file or directory`; free disk went 2.9 GiB→19 GiB across the session, and I deleted nothing but my own directory). **Nothing written, moved or deleted anywhere under `/home/user/Rare-cancers`. No git write operation of any kind.** `scripts/preflight.sh` not run.

**`date -u` start:** `Tue Sep  8 03:30:00 UTC 2026` — **end:** `Tue Sep  8 03:32:52 UTC 2026`
**`git rev-parse HEAD` start:** `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1` — **end:** `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1` (unchanged)
**`git status --porcelain` start:** empty — **end:** empty (literal `STATUS:[]`)
**Panel cache sha256 start / at runtime (in-script) / end:** `123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9` — all three identical.

**`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** (start and end runs were identical; four long proxy/no-proxy lines that merely contain `api.anthropic.com` in a host list are elided in this rendering and named here — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
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
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
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

W02g found both surviving marker sets flatter across their genes (`R_gene`) than size-matched random panels drawn from the same 423-gene universe, scored on the six EMC specimens. W02h showed that flatness is correlation-driven rather than a variance tail — and then named its own remaining soft spot honestly: *"a curated marker set is more internally correlated than a random gene list" is close to a tautology*, so the interesting quantity is not whether the marker sets are flat but **whether EMC is unusual in making them flat.**

**The question I pursued:** recompute `R_gene`, `R_var` and mean pairwise `r` for the *same two marker sets* on the three comparator arms — LGFMS (n=17, subsampled to 6), desmoid fibromatosis (n=6), fibrosarcoma (n=6) — and ask whether EMC's value sits **inside or outside the arm-to-arm spread of the identical statistic**.

It is open because the random-panel null in W02g/W02h varies the *gene set* while holding the *arm* fixed at EMC. It therefore cannot distinguish "EMC does something to this marker set" from "this marker set behaves this way on this platform in every sarcoma arm." Only an arm-varying comparison can, and it has never been run for the decomposition.

---

## Prior-work check

| # | command | what it showed |
|---|---|---|
| 1 | `grep -n -i -E 'HHI_gene\|LGFMS\|desmoid\|fibrosarcoma\|comparator' W02f-fibro-ecm-decomposition.md` | W02f's R4 shape-control table is the **only** place comparator-arm concentration values exist: fibro/ECM `R_gene` LGFMS(n=17) 3.4974, desmoid 5.3457, fibrosarcoma 5.1089, vs EMC 2.0460. W02f itself labels this departure **[POST-HOC]** throughout: *"My pre-declaration had no threshold for it, and I am not inventing one now"*. No `R_var` and no mean-pairwise-`r` for any comparator arm. **No endothelial comparator `R_gene` anywhere.** |
| 2 | `rg -n -i "arm-to-arm\|comparator arm\|subsampl" --glob '!.git' research/autonomy/opus-capacity-campaign-20260908/` | Comparator arms appear as *thresholds* (W02d `FLOOR`), as a *score-SD* shape control (W02f), and as an n-matched LGFMS resample null for `HHI_sample`/`HHI_gene` — never as an **arm-to-arm spread of the concentration/correlation decomposition** for both axes. Confirms this exact test is unrun. |
| 3 | `git ls-files \| rg -i "w02"` | Eight lane-2 reports; W02h is the latest and names this successor. |
| 4 | reading of W02h in full (its Method, its frozen docstring, its R1–R5, its script) | I reuse its loader and its three statistics **verbatim, unchanged**, so the arms are compared like-for-like. |
| 5 | reading of `CLOSED-WORK.md`, `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md` | I touched none of: the clinical registry, PUB-ASO/Qeios frozen deliverables, the NR4A Perspective refusal, Brenca, Hofvander, the paired-Davis negative, or any unrecovered pazopanib/sunitinib/trabectedin/Wagner/CTARC source. **No network call of any kind. No expression matrix fetched. No denied route probed, replayed or routed around.** GSE24369 rediscovery is explicitly not new data and I claim none. |

I am not replaying anything closed. W02f's fibro/ECM comparator observation existed but was descriptive and post-hoc; converting it to a frozen rule with an n-matched LGFMS is new, and the endothelial axis and the `R_var`/`mean_r` limbs are entirely new.

---

## Method and inputs

**SUBSTRATE LIMIT, stated up front and not as a gap to close.** The only input is the committed panel cache `/home/user/Rare-cancers/research/modalities/emc-expression-panels.json` (`generated_utc 2026-08-29T12:51:32+00:00`, sha256 `123bd05a…f336bd9`). It is **not an expression matrix**. The GSE24369 series matrix is not committed and fetching it is **DENIED**; no attempt, probe or workaround was made. Field used: `gene_reads[SYM]["GSE24369_series_matrix.txt.gz"].per_sample[].array_percentile` — a **within-array rank**, not an abundance.

- **Platform:** GPL6244 (`GSE24369`), **464 genes complete-case × 35 samples**, classes `{EMC 6, LGFMS 17, desmoid_fibromatosis 6, fibrosarcoma 6}`, asserted in-script. No cross-platform pooling; GPL3290 not used.
- **Marker sets:** the declared fibro/ECM (k=14) and endothelial (k=6) sets, taken verbatim from W02d/W02c via W02h. Not re-invented.
- **Statistics:** identical algebra to W02f/W02g/W02h — `R_gene = k·Σf_i²` with `f_i = Cov(g_i,s)/(k·Var(s))`; `R_var = k·Σ(v_i/Σv_j)²` (the same algebra with off-diagonal covariances zeroed); `mean_r` = mean of the k(k−1)/2 off-diagonal Pearson correlations. Even = 1.0 for the first two at any k.
- **Subsampling scheme:** EMC, desmoid and fibrosarcoma at n=6 are point values. LGFMS (n=17) is enumerated **exhaustively** — all **C(17,6) = 12376** six-specimen subsamples, asserted in-script. Exhaustive means **seed-free**, not a Monte-Carlo estimate. The full-arm n=17 value is printed for context only and enters no rule, because these statistics are n-dependent.
- **Comparator point set** `P = {median of the 12376 LGFMS subsamples, desmoid, fibrosarcoma}` — three arms, all n=6-comparable.
- **Taken as given, not re-derived:** `R_gene` fibro/ECM 2.0460, endothelial 1.1729 (W02f/W02g); `R_var` 3.0441/1.3934 and `mean_r` 0.5168/0.8124 (W02h). Recomputed exactly once as the single permitted loader-reproduction control row.
- **Tools:** Python 3.11.15, numpy 2.4.6, Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w02i`. No network, no paid API, no GPU, no scipy.

### Pre-declaration integrity

The complete pre-declaration — statistic, subsampling scheme, thresholds, tail of interest, the explicit statement of what would show EMC is **not** unusual, and my expectation — is the script's module docstring, written **in full before the first execution**.

| moment | sha256 of `/tmp/claude-0/w02i/w02i.py` |
|---|---|
| **before run** (`sha256sum`) | `a66c4490afa06a54cc5c74b8f11c418fca595d88edd766ed0601a585f113c641` |
| **at runtime** (script hashing itself) | `a66c4490afa06a54cc5c74b8f11c418fca595d88edd766ed0601a585f113c641` |
| **after run** (`sha256sum`) | `a66c4490afa06a54cc5c74b8f11c418fca595d88edd766ed0601a585f113c641` |

**All three identical. The result is not void.** The script was not edited after any number was seen, and there was exactly one execution.

**Frozen decision rules, quoted from the docstring:**

- `E1 RANGE` — fires iff EMC lies **outside** the closed interval `[min P, max P]`. Side recorded.
- `E2 LGFMS TAIL` — `p_lo = (#{subsample ≤ EMC}+1)/12377`, `p_hi = (#{subsample ≥ EMC}+1)/12377`. **Tail of interest = LOWER** for all three statistics (W02f/W02g's departure was downward). `E2` fires iff `p_lo ≤ 0.05`. Both tails printed regardless.
- `E3 RANK` — EMC's rank among the four n=6-comparable arm values. *"DECLARED IN ADVANCE AS DESCRIPTIVE ONLY: with four arms the smallest attainable one-sided exact rank p is 1/4 = 0.25, so E3 CAN NEVER reach 0.05 and is never cited as significance."*
- Verdict: **U** iff E1 and E2; **N** iff neither; **P** iff exactly one.

**What would show EMC is NOT unusual, quoted:** *"N on R_gene for BOTH axes is the result that shows EMC is not unusual… W02h's tautology worry is confirmed, and the EMC-specific reading of W02g must be withdrawn — I pre-commit to headlining that outcome if it occurs and to writing it as a withdrawal, not as a nuance. Likewise N on mean_r for both axes is the direct, targeted confirmation of W02h's tautology worry for the correlation limb specifically, and must be reported as such even if R_gene returns U."*

**My expectation, quoted, so neither outcome could be staged as a surprise:** *"fibroECM R_gene: I expect U. This is NOT a prediction from insight — W02f already printed EMC 2.0460 below all three comparator values… If it fires I will say plainly that it was already visible. endothelial R_gene: genuinely open… I lean U but weakly… R_var on both axes: I expect N or P… mean_r on both axes: I expect N. Internal correlation of a curated marker set should be a property of the gene set, present in every arm."*

---

## Result

**Headline: the two axes separate, and one of my three expectations was wrong in a direction my frozen rule could not score.**

### R1 — Loader-reproduction control (the only re-derivation) — `PRIMARY`

| axis | k | `R_gene` | taken | match | `R_var` | taken | match | `mean_r` | taken | match |
|---|---|---|---|---|---|---|---|---|---|---|
| fibro/ECM | 14 | 2.0460 | 2.0460 | **True** | 3.0441 | 3.0441 | **True** | 0.5168 | 0.5168 | **True** |
| endothelial | 6 | 1.1729 | 1.1729 | **True** | 1.3934 | 1.3934 | **True** | 0.8124 | 0.8124 | **True** |

An independently written vectorised `r_gene` reproduces W02f/W02g/W02h to 4 dp on all six values. The loader and algebra are the same object.

### R2 — Arm table, fibro/ECM axis (k=14) — `SECONDARY` (derived composition statistics, not measurements)

| stat | EMC (n=6) | desmoid (n=6) | fibrosarcoma (n=6) | LGFMS full (n=17)\* | LGFMS-sub p05 | p50 | p95 | min | max |
|---|---|---|---|---|---|---|---|---|---|
| `R_gene` | **2.0460** | 5.3457 | 5.1089 | 3.4974 | 2.6821 | 4.3448 | 8.1236 | 2.2406 | 21.8869 |
| `R_var` | 3.0441 | 2.9119 | 7.3676 | 4.9361 | 3.7971 | 5.2770 | 7.9996 | 2.6560 | 10.5576 |
| `mean_r` | **0.5168** | 0.0951 | 0.1519 | 0.2451 | −0.0078 | 0.2104 | 0.3976 | −0.0669 | 0.5367 |

\* n=17, context only, enters no rule. LGFMS-sub columns are the 12376 exhaustive six-specimen subsamples.

### R3 — Arm table, endothelial axis (k=6) — `SECONDARY`

| stat | EMC (n=6) | desmoid | fibrosarcoma | LGFMS full (n=17)\* | LGFMS-sub p05 | p50 | p95 | min | max |
|---|---|---|---|---|---|---|---|---|---|
| `R_gene` | 1.1729 | 1.4393 | 1.1724 | 1.2307 | 1.0635 | 1.2528 | 1.5414 | 1.0075 | 3.0873 |
| `R_var` | 1.3934 | 1.6602 | 1.2153 | 1.2754 | 1.0741 | 1.3113 | 1.6073 | 1.0029 | 2.2513 |
| `mean_r` | **0.8124** | 0.3874 | 0.4378 | 0.5456 | 0.2853 | 0.5319 | 0.7460 | −0.0930 | 0.9061 |

### R4 — Declared verdict table, verbatim from the run — `PRIMARY` (a computation actually executed)

```
axis         stat           EMC  LGFMSmed   desmoid fibrosarc    side     E1      p_lo     E2  rank  outcome
fibroECM     R_gene      2.0460    4.3448    5.3457    5.1089   BELOW   True   0.00008   True     1  U (UNUSUAL)
fibroECM     R_var       3.0441    5.2770    2.9119    7.3676  INSIDE  False   0.00097   True     2  P (PARTIAL)
fibroECM     mean_r      0.5168    0.2104    0.0951    0.1519   ABOVE   True   0.99956  False     4  P (PARTIAL)
endothelial  R_gene      1.1729    1.2528    1.4393    1.1724  INSIDE  False   0.20296  False     2  N (NOT UNUSUAL)
endothelial  R_var       1.3934    1.3113    1.6602    1.2153  INSIDE  False   0.69363  False     3  N (NOT UNUSUAL)
endothelial  mean_r      0.8124    0.5319    0.3874    0.4378   ABOVE   True   0.98861  False     4  P (PARTIAL)
```

### R5 — What this says, limb by limb

**(a) The endothelial axis returns N on `R_gene` — the pre-declared "EMC is NOT unusual" outcome — and I headline it as the withdrawal I pre-committed to.** EMC's endothelial `R_gene` 1.1729 sits *between* fibrosarcoma (1.1724) and the LGFMS six-specimen median (1.2528), rank 2 of 4, `p_lo = 0.203`. It also returns N on `R_var`. **W02g's endothelial finding — "flatter across its six genes than a random six-gene panel" — is therefore NOT an EMC-specific property.** Every arm on this platform makes the endothelial marker set roughly this flat. For the endothelial axis, W02h's tautology worry is **confirmed**: the flatness belongs to the marker set, not to EMC, and the EMC-specific reading of W02g's endothelial result must be withdrawn. This is the single most important line in this report and it is a negative.

**(b) The fibro/ECM axis returns U on `R_gene`, and it was already visible.** EMC 2.0460 sits below all three comparator point values (`P = [4.3448, 5.3457]`), rank 1 of 4, and below **all but one** of the 12376 exhaustive LGFMS six-specimen subsamples (`p_lo = 0.00008`; subsample min 2.2406 is still above EMC, so the count is 0 and the +1 estimator gives 1/12377). As I declared in advance, **this is a confirmation under a frozen rule of something W02f had already printed post-hoc, not a discovery.** Its value is that the rule was frozen, the LGFMS arm is now n-matched, and the count is exhaustive rather than a 20,000-draw resample.

**(c) `R_var` splits the way I expected and adds nothing.** fibro/ECM `R_var` is P — inside the comparator range (desmoid 2.9119 is lower) but below the LGFMS subsample bulk. Endothelial is N. Consistent with W02h's finding that the variance limb did not carry the effect (`p_var` 0.332). No `U` anywhere on `R_var`; the variance limb does not separate EMC from other arms on either axis.

**(d) My mean-pairwise-`r` expectation was WRONG, and wrong in a direction my frozen rule scores as P, not U.** I expected N — internal correlation as a gene-set property present in every arm. Instead **EMC has the highest `mean_r` of all four arms on BOTH axes**, by a wide margin: fibro/ECM 0.5168 vs 0.0951 / 0.1519 / 0.2104 (rank 4/4, `E1` fires ABOVE), endothelial 0.8124 vs 0.3874 / 0.4378 / 0.5319 (rank 4/4, ABOVE). **My declared tail of interest was LOWER, so `E2` cannot fire and the verdict is P for both.** The upper-tail figures — `p_hi = 0.00052` (fibro/ECM) and `p_hi = 0.01147` (endothelial) against the exhaustive LGFMS subsamples — are printed by the script but are **`[POST-HOC]` with respect to the direction, and I do not claim significance from them.** I wrote the rule for the wrong tail and I am reporting that rather than re-scoring it.

**(e) `[POST-HOC]`, offered as description and explicitly not as a mechanism:** a high, *evenly shared* internal correlation drives `f_i` toward equality and therefore drives `R_gene` **down**. So (b) and (d) are the same phenomenon seen twice on the fibro/ECM axis. But (a) shows the endothelial axis carries the same elevated `mean_r` **without** an unusual `R_gene`, so elevated internal correlation is **not sufficient** to produce an unusual `R_gene`. This is a description of two statistics of one 464×35 rank matrix. It is not a biological claim.

**Net effect on the lane:** of the two axes W02d/W02g carried forward, **one (endothelial) is now shown not to be EMC-specific on the concentration statistic**, and **one (fibro/ECM) survives arm-to-arm under a frozen rule**. The lane's surviving claim is narrower than it was before this run.

---

## Validation evidence

**RUN.**

| # | command | exit | verbatim key output |
|---|---|---|---|
| 1 | `python3 -c "import numpy,sys;print('numpy',numpy.__version__,'python',sys.version.split()[0])"` | 0 | `numpy 2.4.6 python 3.11.15` |
| 2 | `sha256sum /tmp/claude-0/w02i/w02i.py` (before run) | 0 | `a66c4490afa06a54cc5c74b8f11c418fca595d88edd766ed0601a585f113c641` |
| 3 | `cd /tmp/claude-0/w02i && time python3 w02i.py > out.txt 2>&1` | **0** (`EXIT=0`) | `real 0m3.532s`; full output reproduced as R1–R4 |
| 4 | `sha256sum /tmp/claude-0/w02i/w02i.py` (after run) | 0 | `a66c4490…113c641` — **identical to #2**, and identical to the script's runtime self-hash |
| 5 | `sha256sum research/modalities/emc-expression-panels.json` (start, in-script, end) | 0 | `123bd05a…f336bd9` all three times |
| 6 | `git rev-parse HEAD` (start / end) | 0 | `215ed8e7…` / `215ed8e7…` — **unchanged** |
| 7 | `git status --porcelain` (start / end) | 0 | empty / empty |
| 8 | in-script assertions | — | `X.shape[0] == 464`; arm sizes 6/17/6/6; `len(combos) == 12376` — all passed (a failure would have been a non-zero exit) |
| 9 | `rm -rf /tmp/claude-0/w02i && ls -d /tmp/claude-0/w02i` | 2 (ls no-such-file) | `ls: cannot access '/tmp/claude-0/w02i': No such file or directory` — scratch deleted as required |
| 10 | `df -h /` | 0 | `/dev/vda 252G 19G 19G 51% /` |

**PROPOSED (NOT RUN):** a two-tailed or upper-tail-declared `mean_r` rule; any arm-varying *and* gene-varying joint null; any GPL3290 cross-check (comparator arms there are n=3 and cross-platform pooling is forbidden); anything on the GSE24369 series matrix (uncommitted, egress **denied**). None executed, none claimed. `scripts/preflight.sh` not run (dispatch forbids it); no repository test tier invoked, because I changed no repository file.

**Script, returned inline (not written into the tree).** The complete file whose sha256 is `a66c4490afa06a54cc5c74b8f11c418fca595d88edd766ed0601a585f113c641` is `/tmp/claude-0/w02i/w02i.py` (since deleted). Its module docstring is the frozen pre-declaration quoted in Method above; here it is in full, with the body:

```python
"""
W02i  — OPUS-CAPACITY-CAMPAIGN-20260908, lane 2 refill.  W02h's named successor.

COMPLETE PRE-DECLARATION.  Written in full BEFORE the first execution.  The file is sha256'd
before the run, hashes itself at runtime, and is sha256'd again after.  If any of the three
differ the result is VOID.

--------------------------------------------------------------------------------------------
QUESTION
--------------------------------------------------------------------------------------------
W02g found the two surviving marker sets (fibro/ECM k=14, endothelial k=6) are FLATTER across
their genes than size-matched random panels drawn from the same 423-gene universe, scored on the
same six EMC specimens.  W02h showed that flatness is correlation-driven, not a variance tail.
W02h then named its own remaining soft spot: "a curated marker set is more internally correlated
than a random gene list" is close to a TAUTOLOGY.  The interesting quantity is therefore NOT
whether the marker sets are flat, but whether EMC is unusual IN MAKING THEM FLAT.

So: recompute the SAME three statistics for the SAME two marker sets on the three comparator arms
and ask whether EMC's value sits INSIDE or OUTSIDE the arm-to-arm spread of the identical
statistic.

W02f reported (descriptively, post-hoc, fibro/ECM only) comparator R_gene 3.4974 / 5.3457 / 5.1089
all ABOVE EMC's 2.0460.  That observation is the reason this test is worth running and is also the
reason a "U" outcome on fibro/ECM R_gene is a CONFIRMATION UNDER A FROZEN RULE, not a discovery.
The correlation-vs-variance decomposition (R_var, mean pairwise r) has NEVER been run on the
comparator arms at all; for the endothelial axis NO comparator R_gene exists in the corpus either.

--------------------------------------------------------------------------------------------
INPUT — SUBSTRATE LIMIT, stated as a limit and not as a gap to close
--------------------------------------------------------------------------------------------
Sole input: the committed panel cache
  /home/user/Rare-cancers/research/modalities/emc-expression-panels.json
  sha256 123bd05a9f9f5d08a362df3bd51cdbb72c241b49712123aaf5c5ea914f336bd9
This is NOT an expression matrix.  The GSE24369 series matrix is not committed and fetching it is
DENIED; no attempt, probe or workaround is made.  No network, no paid API, no GPU, no wet lab.
Field used: gene_reads[SYM][GSE24369_series_matrix.txt.gz].per_sample[].array_percentile — a
WITHIN-ARRAY RANK, not an abundance.  Six arrays are not six patients.  Any result here is an
ASSOCIATION, never a mechanism and never clinical.

--------------------------------------------------------------------------------------------
STATISTICS (identical algebra to W02f / W02g / W02h, reused unchanged so this is like-for-like)
--------------------------------------------------------------------------------------------
For a marker set of k genes scored on the n specimens of one arm, s = mean over genes:
  R_gene = k * sum_i f_i^2 ,  f_i = Cov(g_i, s) / (k * Var(s))        (even = 1.0)
  R_var  = k * sum_i (v_i / sum_j v_j)^2 ,  v_i = Var(g_i)            (even = 1.0)
           i.e. R_gene with every off-diagonal covariance set to zero = the "variance-only" limb
  mean_r = mean of the k(k-1)/2 off-diagonal Pearson correlations among the k genes

--------------------------------------------------------------------------------------------
ARMS AND SUBSAMPLING SCHEME
--------------------------------------------------------------------------------------------
  EMC                     n = 6   point value (the arm under test)
  desmoid_fibromatosis    n = 6   point value
  fibrosarcoma            n = 6   point value
  LGFMS                   n = 17  EXHAUSTIVE enumeration of all C(17,6) = 12376 six-specimen
                                  subsamples.  Exhaustive, therefore SEED-FREE and not a
                                  Monte-Carlo estimate.  The full-arm n=17 value is printed for
                                  context ONLY and takes no part in any threshold, because these
                                  statistics are n-dependent and the comparison must be n-matched.
The n-matched LGFMS POINT VALUE used in every rule below is the MEDIAN of its 12376 subsamples.

Comparator point set  P = { median(LGFMS subsamples), desmoid, fibrosarcoma }  (three arms, all
n=6-comparable).  This is the entire available arm-to-arm spread.  There are only three
comparator arms in existence on this platform; that is a hard power ceiling, declared here.

--------------------------------------------------------------------------------------------
DECISION RULES, TAIL OF INTEREST, THRESHOLDS — frozen
--------------------------------------------------------------------------------------------
For EACH axis (fibroECM, endothelial) and EACH statistic (R_gene, R_var, mean_r):

  E1 RANGE      : fires iff EMC's value lies OUTSIDE the closed interval [min P, max P].
                  The printed output records which side.
  E2 LGFMS TAIL : lower-tail p_lo = (#{LGFMS subsample <= EMC} + 1) / (12376 + 1);
                  upper-tail p_hi = (#{LGFMS subsample >= EMC} + 1) / (12376 + 1).
                  TAIL OF INTEREST = LOWER for R_gene and R_var (W02f/W02g's departure was
                  downward: EMC flatter/less concentrated), and LOWER for mean_r as well
                  (a flatter R_gene with lower internal correlation is the coherent alternative).
                  Both tails are printed regardless.  E2 fires iff p_lo <= ALPHA = 0.05.
  E3 RANK       : EMC's rank among the four n=6-comparable arm point values.
                  DECLARED IN ADVANCE AS DESCRIPTIVE ONLY: with four arms the smallest attainable
                  one-sided exact rank p is 1/4 = 0.25, so E3 CAN NEVER reach 0.05 and is never
                  cited as significance.

  VERDICT   U (UNUSUAL)     iff E1 AND E2 both fire.
            N (NOT UNUSUAL) iff NEITHER fires  -> EMC's value is swallowed by the arm-to-arm
                              spread of the identical statistic.
            P (PARTIAL)     iff exactly one fires.

--------------------------------------------------------------------------------------------
EXPLICITLY: WHAT RESULT WOULD SHOW EMC IS *NOT* UNUSUAL
--------------------------------------------------------------------------------------------
N on R_gene for BOTH axes is the result that shows EMC is not unusual.  If EMC's R_gene sits
inside [min P, max P] and inside the LGFMS six-specimen subsample bulk, then "these marker sets
are flatter than random gene panels" is a property of the MARKER SETS and the PLATFORM that every
sarcoma arm on this array shows, W02h's tautology worry is confirmed, and the EMC-specific
reading of W02g must be withdrawn — I pre-commit to headlining that outcome if it occurs and to
writing it as a withdrawal, not as a nuance.
Likewise N on mean_r for both axes is the direct, targeted confirmation of W02h's tautology worry
for the correlation limb specifically, and must be reported as such even if R_gene returns U.
A mixed picture (U on R_gene, N on mean_r) is to be reported as BOTH facts, with neither
suppressed and neither promoted to a mechanism.

--------------------------------------------------------------------------------------------
MY EXPECTATION, DECLARED IN WRITING IN ADVANCE so neither outcome can be staged as a surprise
--------------------------------------------------------------------------------------------
- fibroECM R_gene: I expect U.  This is NOT a prediction from insight — W02f already printed
  EMC 2.0460 below all three comparator values, and I am simply re-testing it under a frozen
  rule with an n-matched LGFMS.  If it fires I will say plainly that it was already visible.
- endothelial R_gene: genuinely open; no comparator value exists anywhere.  I lean U but weakly,
  because W02h showed the endothelial markers are individually HIGH-variance in EMC (median SD
  percentile 95.6), and high single-gene variance pushes R_var, hence R_gene, UP, not down.
- R_var on both axes: I expect N or P.  W02h found the variance limb did NOT carry the fibro/ECM
  effect (p_var 0.332), so I do not expect the variance limb to separate EMC from other arms.
- mean_r on both axes: I expect N.  Internal correlation of a curated marker set should be a
  property of the gene set, present in every arm.  If mean_r returns N while R_gene returns U,
  the honest reading is that EMC differs in HOW the shared correlation is distributed across
  genes, not in HOW MUCH correlation the marker set carries — and that is a weaker claim than
  W02g's phrasing suggests.

--------------------------------------------------------------------------------------------
TAKEN AS GIVEN, NOT RE-DERIVED (per dispatch)
--------------------------------------------------------------------------------------------
W02f/W02g EMC R_gene: fibroECM 2.0460, endothelial 1.1729.  Recomputed EXACTLY ONCE as the single
permitted loader-reproduction control row.  W02h's R_var / mean_r EMC values (fibroECM R_var
3.0441, mean_r 0.5168; endothelial R_var 1.3934, mean_r 0.8124) are likewise taken; they are
printed alongside the arm table as a second consistency check but are not re-litigated.

--------------------------------------------------------------------------------------------
STOP CONDITION
--------------------------------------------------------------------------------------------
Stop the moment the 2 x 3 verdict table is printed with a matching before/at-runtime/after script
sha256 and a matching source sha256.  No further statistic is added, no threshold is moved, no
post-hoc test is run.  Any observation made after seeing the numbers is labelled [POST-HOC].
"""
import hashlib, json, itertools
import numpy as np

SRC = "/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
PLAT = "GSE24369_series_matrix.txt.gz"
ALPHA = 0.05

MARK = {
 "immune": ["PTPRC","CD2","CD3D","CD3E","CD8A","CD68","CD163","CSF1R","ITGAM","HLA-DRA","MS4A1","GZMB"],
 "endothelial": ["PECAM1","VWF","CDH5","KDR","FLT1","MCAM"],
 "fibroECM": ["COL1A1","COL1A2","COL3A1","COL5A1","DCN","LUM","FAP","THY1","POSTN","FN1","PDGFRA","PDGFRB","ACTA2","COL11A1"],
 "tumour": ["NR4A3","PPARG","RET","INSM1","SYP","CHGA","ENO2","KIT","CD24"],
}
TAKEN_RGENE = {"fibroECM": 2.0460, "endothelial": 1.1729}          # W02f / W02g
TAKEN_RVAR  = {"fibroECM": 3.0441, "endothelial": 1.3934}          # W02h
TAKEN_MEANR = {"fibroECM": 0.5168, "endothelial": 0.8124}          # W02h

print("SELF sha256 (as read at runtime) =", hashlib.sha256(open(__file__,'rb').read()).hexdigest())
print("SOURCE sha256 =", hashlib.sha256(open(SRC,'rb').read()).hexdigest())
d = json.load(open(SRC))
print("SOURCE generated_utc =", d.get("generated_utc"))

# ---- loader: complete-case genes on GPL6244 (identical to W02h's) ----
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
idx = {g:i for i,g in enumerate(names)}
ARMS = {c: np.array([i for i,k in enumerate(klass) if k == c]) for c in sorted(set(klass))}
assert len(ARMS["EMC"]) == 6 and len(ARMS["LGFMS"]) == 17
assert len(ARMS["desmoid_fibromatosis"]) == 6 and len(ARMS["fibrosarcoma"]) == 6

# ---- statistics (same algebra as W02f/W02g/W02h) ----
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

STATS = [("R_gene", r_gene), ("R_var", r_var), ("mean_r", mean_pair_r)]

# ---- CONTROL ROW (the only re-derivation) ----
print("\n=== LOADER-REPRODUCTION CONTROL (single row; W02f/W02g/W02h values otherwise TAKEN) ===")
for ax in ["fibroECM","endothelial"]:
    M = X[[idx[g] for g in MARK[ax]]][:, ARMS["EMC"]]
    rc, rv, mr = r_gene(M), r_var(M), mean_pair_r(M)
    print("%-12s k=%2d : R_gene %.4f vs TAKEN %.4f match=%s | R_var %.4f vs %.4f match=%s | mean_r %.4f vs %.4f match=%s"
          % (ax, M.shape[0], rc, TAKEN_RGENE[ax], abs(rc-TAKEN_RGENE[ax])<5e-5,
             rv, TAKEN_RVAR[ax], abs(rv-TAKEN_RVAR[ax])<5e-5,
             mr, TAKEN_MEANR[ax], abs(mr-TAKEN_MEANR[ax])<5e-5))

# ---- arm-to-arm table ----
combos = list(itertools.combinations(range(17), 6))
print("\nLGFMS exhaustive six-specimen subsamples enumerated: %d (expected C(17,6)=12376)" % len(combos))
assert len(combos) == 12376

verdict = {}
for ax in ["fibroECM","endothelial"]:
    G = X[[idx[g] for g in MARK[ax]]]
    k = G.shape[0]
    print("\n================ AXIS %s (k=%d) ================" % (ax, k))
    L = G[:, ARMS["LGFMS"]]
    sub = {nm: [] for nm,_ in STATS}
    for c in combos:
        Mc = L[:, list(c)]
        for nm, fn in STATS:
            val = fn(Mc)
            sub[nm].append(np.nan if val is None else val)
    sub = {nm: np.asarray(v, float) for nm, v in sub.items()}

    print("%-8s %10s %10s %10s %10s | %10s %10s %10s %10s %10s" %
          ("stat","EMC(n=6)","desmoid","fibrosarc","LGFMSfull*","LG p05","LG p50","LG p95","LG min","LG max"))
    rowvals = {}
    for nm, fn in STATS:
        emc = fn(G[:, ARMS["EMC"]])
        des = fn(G[:, ARMS["desmoid_fibromatosis"]])
        fib = fn(G[:, ARMS["fibrosarcoma"]])
        lgf = fn(L)                        # n=17, CONTEXT ONLY
        a = sub[nm][~np.isnan(sub[nm])]
        rowvals[nm] = (emc, des, fib, lgf, a)
        print("%-8s %10.4f %10.4f %10.4f %10.4f | %10.4f %10.4f %10.4f %10.4f %10.4f" %
              (nm, emc, des, fib, lgf, np.percentile(a,5), np.percentile(a,50),
               np.percentile(a,95), a.min(), a.max()))
    print("* LGFMSfull is n=17 and is CONTEXT ONLY; it enters no rule. The n-matched LGFMS point")
    print("  value used in E1/E3 is the median of the 12376 six-specimen subsamples.")

    for nm, _ in STATS:
        emc, des, fib, lgf, a = rowvals[nm]
        lg_pt = float(np.median(a))
        P = [lg_pt, des, fib]
        lo, hi = min(P), max(P)
        e1 = not (lo <= emc <= hi)
        side = "BELOW" if emc < lo else ("ABOVE" if emc > hi else "INSIDE")
        n = len(a)
        p_lo = (int((a <= emc).sum()) + 1) / (n + 1)
        p_hi = (int((a >= emc).sum()) + 1) / (n + 1)
        e2 = p_lo <= ALPHA
        allpts = sorted([("EMC",emc),("LGFMSmed",lg_pt),("desmoid",des),("fibrosarcoma",fib)], key=lambda t:t[1])
        rank = [t[0] for t in allpts].index("EMC") + 1
        out = "U (UNUSUAL)" if (e1 and e2) else ("N (NOT UNUSUAL)" if (not e1 and not e2) else "P (PARTIAL)")
        verdict[(ax,nm)] = (emc, lg_pt, des, fib, lo, hi, side, e1, p_lo, p_hi, e2, rank, out)
        print("  %-7s EMC=%9.4f | P=[%.4f, %.4f] -> %s ; E1=%s | LGFMS-subsample p_lo=%.5f p_hi=%.5f -> E2=%s"
              " | E3 rank %d/4 (%s) [DESCRIPTIVE ONLY] -> %s"
              % (nm, emc, lo, hi, side, e1, p_lo, p_hi, e2, rank,
                 " < ".join("%s %.3f" % t for t in allpts), out))

print("\n=== DECLARED VERDICT TABLE (2 axes x 3 statistics) ===")
print("%-12s %-8s %9s %9s %9s %9s %7s %6s %9s %6s %5s  %s" %
      ("axis","stat","EMC","LGFMSmed","desmoid","fibrosarc","side","E1","p_lo","E2","rank","outcome"))
for (ax,nm),(emc,lg,des,fib,lo,hi,side,e1,plo,phi,e2,rank,out) in verdict.items():
    print("%-12s %-8s %9.4f %9.4f %9.4f %9.4f %7s %6s %9.5f %6s %5d  %s" %
          (ax,nm,emc,lg,des,fib,side,e1,plo,e2,rank,out))
print("""
U => EMC's value lies outside the arm-to-arm spread AND outside the LGFMS six-specimen bulk.
N => EMC is NOT unusual on that statistic: the arm-to-arm spread swallows it, and the property
     belongs to the marker set / platform rather than to EMC.  N on R_gene for BOTH axes
     withdraws the EMC-specific reading of W02g.  N on mean_r confirms W02h's tautology worry
     for the correlation limb.
P => exactly one limb; report both halves, promote neither.
ONLY THREE COMPARATOR ARMS EXIST on this platform; E3 can never reach 0.05 and is descriptive.
No biological, mechanistic or clinical claim follows from any outcome.  array_percentile is a
within-array rank; six arrays are not six patients; this is an ASSOCIATION at most.""")
```

---

## Limitations

1. **SUBSTRATE LIMIT, restated as a limit.** The only input is a committed panel cache of 464 genes' `array_percentile` values on GPL6244. It is not an expression matrix; the matrix is not committed and fetching it is denied. Everything here is a statistic of a rank table.
2. **`array_percentile` is a within-array rank.** Correlations and variances computed on ranks are not correlations of abundance. No absolute expression statement is possible.
3. **Six arrays are not six patients.** EMC n=6, desmoid n=6, fibrosarcoma n=6. Nothing here is a patient-level or clinical statement, and no mechanism follows. Association at most.
4. **Only three comparator arms exist on this platform, and they are hard-coded by the deposit.** The arm-to-arm "spread" is three numbers. `E3` was declared descriptive precisely because a four-arm rank can never reach α = 0.05. `E2`'s apparent precision (12376 exhaustive draws) comes from resampling **one** arm; it measures within-LGFMS specimen sampling, **not** between-disease variability, and must not be read as if there were 12376 arms.
5. **The comparator arms are other sarcomas, several fibroblastic** (LGFMS, desmoid, fibrosarcoma). "Outside the comparator spread" means "unlike these three fibroblastic sarcoma arms" — never "abnormal" and never "high" or "low" in any absolute sense. W02b already flagged this for the lane.
6. **I declared the wrong tail for `mean_r`.** The departure is upward on both axes and my rule scores only the lower tail, so both `mean_r` rows are `P` and the upper-tail p-values are `[POST-HOC]` in direction. I did not re-score them and I claim no significance from them.
7. **The fibro/ECM `U` is a confirmation, not a discovery.** W02f had already printed the same direction descriptively. Its added value is a frozen rule, an n-matched LGFMS arm, and an exhaustive rather than resampled count.
8. **`R_gene`, `R_var` and `mean_r` are n-dependent**, which is why the n=17 LGFMS full-arm column is context only. It is also why a comparison against arms of a different size could not have been made honestly.
9. **No multiplicity correction.** Six rows (2 axes × 3 statistics) were tested at α = 0.05 with no adjustment; that was declared in advance and not corrected afterwards, but it means the two nominally-significant `E2` firings on the fibro/ECM axis should be read with that in mind.
10. **W02c's separate caution stands:** the fibrosarcoma endothelial score correlates with panel brightness at r = +0.845, so the fibrosarcoma arm is a weak comparator on the endothelial axis specifically — and it is precisely the arm that brackets EMC from below in the endothelial `R_gene` row. The endothelial `N` does not depend on it (the LGFMS subsample `p_lo = 0.203` alone gives `E2 = False`), but the `E1` bracket does.
11. **No repository file changed, so no repository test tier applies.** No preflight, no gate, no publication path touched.

---

## Stop condition

**Declared in the frozen docstring before the run:** *"Stop the moment the 2 x 3 verdict table is printed with a matching before/at-runtime/after script sha256 and a matching source sha256. No further statistic is added, no threshold is moved, no post-hoc test is run."*

**MET.** The 2×3 verdict table printed on the single execution (exit 0); all three script hashes are `a66c4490…113c641`; all three source hashes are `123bd05a…f336bd9`. No statistic was added, no threshold moved, no post-hoc test run — the two direction-post-hoc observations are labelled `[POST-HOC]` and scored as `P`, not re-scored. Returning immediately.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 8** (target ~40).
- **Wall clock: ~3 minutes**, `date -u` 03:30:00Z → 03:32:52Z (target ~40 minutes). Script runtime 3.5 s.
- Under target on both because the question was sharply specified, W02h's loader and algebra were reusable verbatim, and the LGFMS enumeration is exhaustive rather than iterative. I did not pad.

---

## Next concrete action

**One successor, and I judge it the last one this substrate supports:** run the identical six-row arm-to-arm rule on the **two marker sets W02d retired** — immune (k=12) and tumour (k=9) — as a *specificity control on the rule itself*. If the retired sets also return `U` on fibro/ECM-like rows, the `U` is a property of the rule or the EMC arm's global rank structure rather than of the fibro/ECM gene set, and the lane's one surviving claim weakens further; if they return `N`, the fibro/ECM `U` gains the discriminant validity it currently lacks. It is cheap (same loader, same 12376 combinations, ~4 s), it can be fully pre-declared, and — critically — it is the only remaining test I can name that could *falsify* the lane's surviving claim rather than decorate it.

**After that, my honest assessment is that lane 2 is out of questions on this substrate.** Every further variant (more arms, transcriptome-wide universes, abundance rather than rank, any single-cell or spatial deconvolution — the lane's original subject) requires the uncommitted expression matrix or new deposits, and that route is denied. The remaining lane-2 statements are associations on a 464-gene rank table across four small sarcoma arms, and after this run one of the two axes has already been shown not to be EMC-specific.
