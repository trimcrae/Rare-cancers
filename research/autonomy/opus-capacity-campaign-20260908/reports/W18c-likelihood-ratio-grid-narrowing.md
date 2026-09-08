<!-- collected 2026-09-08T03:43:42Z by campaign coordinator; agent id a2962c1787907f51e; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a2962c1787907f51e.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W18c** — Lane 18 refill (named successor to W18b), OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in the environment confirms a served model — no `model` key exists anywhere in the environment. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start / end:
```
Tue Sep  8 03:17:45 UTC 2026
Tue Sep  8 03:39:23 UTC 2026
```

`git rev-parse HEAD` at start / end — **it moved during my run**, as it did for W18b:
```
start: c81236b90c7905caa2e75a57b332ad33f2c10d02
end:   5ae0fa04ff9516ac8f820381079d644a094f4a77
```
Neither is the `92abbcb9…` named in `COMMON-BRIEF.md`, nor W18b's `d3e9c4d8…`/`98a0833f…`. The coordinator is advancing the checkout while workers run; I read the tree as I found it.

`git status --porcelain` at start and at end: **empty both times** (no output). No repository file created, modified or deleted; no git write operation of any kind. All execution under `/tmp/claude-0/w18c/`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — captured at start and again at end, **identical apart from two proxy lines I elided at the end for length**. Verbatim (end capture, with `no_proxy`/`NO_PROXY`/`JAVA_TOOL_OPTIONS` filtered out as pure proxy noise; they were present and unchanged at both captures):
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

## The principled reason this could fail, stated up front, not as a footnote

W18's D0 found that the fitted selection correlation ρ carried the **wrong sign in roughly two thirds of replicates** at EMC scale — the conditional likelihood cannot distinguish selection strengths at these sample sizes. A likelihood-ratio screen across grid cells needs exactly that discrimination in order to drop anything. So this test was, before it ran, a test of a mechanism W18 had already shown to be weak. **It failed, for exactly that reason, and I measured the reason directly.** The conclusion for this lane is therefore written below as a result, not as a prompt for a fourth variant.

---

## Question

**Can the λ (true-risk) axis of W18b's two-channel selection grid be restricted by EVIDENCE — a pre-specified likelihood-ratio screen that drops poorly-supported grid cells — rather than by choice, so as to recover E2 (median k=24 bound width ≤ 0.70 logit) while holding E1 (κ=6 bound coverage ≥ 0.90)?**

Open because W18b passed E1 (0.243 → 0.971) and failed E2 (1.033 vs ≤ 0.70), and diagnosed both effects as coming entirely from the same λ>0 cells extending the **lower** bound edge while the upper edge stayed put. If those cells could be excluded on evidence when the data do not support them, the coverage repair might survive at a usable width. W18b named this as its own successor and explicitly required the LR margin to be pre-specified before running.

---

## Prior-work check

Exact commands and results:

```
$ rg -n -i "copas" --glob '!.git' -l
research/autonomy/opus-capacity-campaign-20260908/reports/W23-cross-output-synthesis-packet.md
research/autonomy/opus-capacity-campaign-20260908/reports/W18b-two-channel-selection-model.md
research/autonomy/opus-capacity-campaign-20260908/reports/W18-publication-selection-estimator.md

$ rg -n -i "likelihood-ratio screen|likelihood ratio screen|grid cell screen|lambda axis" --glob '!.git' -l
research/autonomy/opus-capacity-campaign-20260908/reports/W18b-two-channel-selection-model.md      (only its own "Next action")

$ git ls-files | rg -i "copas|two_channel|selection_model|lr_screen"
(no output — no such file is tracked)

$ grep -ril "copas" /tmp/claude-0/frozen-corpus/extracted/corpus/
(no output)
```

The only new hit since W18b is `W23-cross-output-synthesis-packet.md`, which cites W18 once and adds no method:

> `- **W18** (Copas-type publication-selection estimator): complete runnable code, but all four executed runs are **synthetic**, and its own key finding is that selection strength is unestimable. Honest, and not a paper.`

That is a synthesis reference, not a competing implementation, so I am not replaying it. Absence in the frozen corpus is **UNKNOWN** for the wider repository, not proof of absence; the live tracked tree was searched directly.

**CLOSED-WORK.md items confirmed not replayed.** No PUB-ASO, no PUB-EMC-CLASSIFICATION, no Brenca/Hofvander/Davis route, no frozen external-validation comment, no NR4A Perspective under any label or framing. **No network requests at all**, so none of the recorded 403/`EGRESS_BLOCKED` routes was retried. Per dispatch I did **not** attempt to retrieve Copas & Shi (2000); that citation **stays flagged as unretrieved and unverified**, inherited from W18 unchanged. Not lane 11; no source-index file touched. No case added to any denominator. **No content-policy refusal was encountered in this run.** (W18b recorded one auto-mode classifier denial on a registry read; I did not attempt that read, so it did not recur and was not routed around.)

---

## Method and inputs

| Item | Value |
|---|---|
| Read (read-only) | `…/opus-capacity-campaign-20260908/{COMMON-BRIEF,CLOSED-WORK,CORPUS-CONTEXT}.md`; `reports/W18-publication-selection-estimator.md`; `reports/W18b-two-channel-selection-model.md` (664 lines, in full); frozen corpus grep |
| Taken as given from W18b | `emc_copas_two_channel.py` — extracted **verbatim** from W18b's report (lines 312–505), sole change the `sys.path` string `/tmp/claude-0/w18b` → `/tmp/claude-0/w18c` |
| Taken as given from W18 | `emc_copas_selection.py` — extracted **verbatim** from W18's report (lines 314–578) |
| Authored new | `run_lr_screen_acceptance.py` (the screen + acceptance harness), `lambda_d0.py` (a λ-identifiability diagnostic, no criterion attached) |
| Python / numpy / scipy | 3.11.15 / 2.4.6 / 1.17.1 — **identical to W18 and W18b** |
| Platform | `Linux-6.18.44-fc-v24-x86_64-with-glibc2.39`, 4 cores, load average 4–8 (other campaign workers concurrent) |
| Data | **ALL SYNTHETIC**, seeded `numpy.random.default_rng`. **NOT APPLIED TO REAL DATA.** |

### Pre-specification, and the hash evidence that it was not moved

The likelihood-ratio margin, the direction of interest, the inherited thresholds and the "may fail" reasoning were written into the module docstring of `run_lr_screen_acceptance.py` **before the first execution of that file**, and the file was hashed before and after.

```
sha256 BEFORE first run:  a88725206c3804d4766844c24e76afc0c23762f1ec375ce8f1d1ea7e6b308bfe
sha256 AFTER  all runs :  a88725206c3804d4766844c24e76afc0c23762f1ec375ce8f1d1ea7e6b308bfe
                          -- IDENTICAL. The result stands.
sha256 lambda_d0.py, before and after: 41a14d2afd8a54c365923da4ee0c81d8e37824ea15435f825a0088547552465b (identical)
```

**Inherited thresholds, NOT moved in either direction:** E1 coverage ≥ 0.90; E2 median k=24 bound width ≤ 0.70 logit. I did not author them and did not touch them.

**The screen, pre-specified.** A grid cell `g` with maximised conditional log-likelihood `L(g)` is retained iff `L(g) ≥ max_h L(h) − Δ`.

- **PRIMARY: `Δ₃ = ½·χ²₀.₉₅(3) = 3.9074`** — df = 3 because three selection quantities are gridded and profiled over (ρ, λ, and `p_least`, which fixes γ₀,γ₁). This is the standard profile-likelihood 95% region for the gridded selection parameters.
- Pre-specified sensitivity, reported but **not** deciding pass/fail: `Δ₂ = 2.9957` (df=2), `Δ₁ = 1.9207` (df=1), and `Δ_∞` = union over all 24 cells = W18b's estimator.
- Monotonicity noted before running: a smaller Δ drops more cells and narrows the bound, so it can only help E2 and only hurt E1. The three margins are a pre-specified monotone tradeoff curve. **No fourth margin was added after seeing results.**

**Direction of interest, pre-specified:** the **lower** bound edge (θ more negative — a larger true adverse-outcome proportion). W18b showed the λ axis moves only that edge; the lower edge is reported separately at every margin.

**Protocol, matched to W18b so numbers are directly comparable.** E1: the exact DGP, seed (`999+60`) and 70 replicates of W18's `f2_kappa_sweep.py` at κ=6. E2: the exact DGP, seed (`4242+30`) and 60 replicates of W18's `k_feasibility.py` at `k_conducted=30`. Profile CIs are computed only for cells surviving the widest margin Δ₃ (cells outside it cannot enter any reported bound) — this is a pure speed optimisation with no effect on any reported bound. The all-24 union was **not recomputed**; W18b's values at these identical seeds are cited.

**Budget sizing, as asked.** I kept W18b's full replicate counts (70 / 60) rather than reducing them, because screening lets me skip profile CIs for excluded cells, which made the run *faster* than W18b's despite identical protocols (1018 s vs W18b's 1289 s). A 4+4-replicate pilot (81 s) established the per-replicate cost before committing. Everything is single-process CPU; no GPU, no paid API, no network.

---

## Result

### R0 — Inherited code reproduces `PRIMARY` (computational, synthetic)

W18b's E0 reduction check, re-run from the verbatim-extracted modules: max |loglik(two-channel, λ=0) − loglik(W18)| over 36 parameter points = **2.842170943040401e-14**, digit-for-digit W18b's `2.842e-14`. Median `k_pub` came out **24** in E1 and **24** in E2, matching W18b's E1 (24) and E2 (24) exactly. The inherited stack is intact; I took W18b's code and numbers as given.

### R1 — The screen HOLDS E1 `PRIMARY` (SYNTHETIC, 70 reps, truth θ = −0.800)

κ=6 true-risk regime, seed 999+60, median `k_pub` = 24, elapsed 564.9 s.

| Estimator / margin | cells kept (median) | bound coverage | median lower edge | median upper edge | median width (logit) |
|---|---|---|---|---|---|
| W18 one-channel (cited) | 6 of 6 | 0.243 | −0.734 | −0.296 | 0.438 |
| W18b all-24 union (cited) | 24 of 24 | 0.971 | −1.044 | −0.296 | 0.747 |
| **W18c Δ₃ (PRIMARY)** | **24.0 / 24** | **0.971** | −1.044 | −0.296 | 0.741 |
| W18c Δ₂ (sensitivity) | 23.0 / 24 | 0.971 | −1.044 | −0.296 | 0.737 |
| W18c Δ₁ (sensitivity) | 21.0 / 24 | 0.971 | −1.037 | −0.296 | 0.726 |

**E1 PASS** at the primary margin, coverage **0.971** — identical to W18b to three decimals. λ values retained across replicates: **{0.0, 1.5, 3.0, 6.0}** at every margin, i.e. the screen never eliminated a λ level.

### R2 — The screen does NOT recover E2 `PRIMARY` (SYNTHETIC, 60 reps)

`k_conducted=30` → median `k_pub` = 24, seed 4242+30, elapsed 453.0 s.

| Estimator / margin | cells kept (median) | median lower edge | median upper edge | **median bound width (logit)** | coverage |
|---|---|---|---|---|---|
| W18 one-channel (cited) | 6 of 6 | −0.975 | −0.489 | **0.509** | 0.950 |
| W18b all-24 union (cited) | 24 of 24 | −1.511 | −0.489 | **1.033** | 1.000 |
| **W18c Δ₃ (PRIMARY)** | **23.0 / 24** | −1.475 | −0.489 | **0.997** | 1.000 |
| W18c Δ₂ (sensitivity) | 22.0 / 24 | −1.455 | −0.489 | 0.974 | 1.000 |
| W18c Δ₁ (sensitivity) | 18.5 / 24 | −1.389 | −0.491 | 0.922 | 1.000 |

**Median k=24 bound width, reported UNCONDITIONALLY as required: 0.997 logit.** On the proportion scale the median primary bound is **[0.186, 0.380]** — still a factor of 2.0.

**E2 FAIL** (0.997 vs ≤ 0.70; over by 0.297, a 42% overshoot). **I did not move the line.**

The screen recovered **0.036 logit of the 0.333-logit deficit — about 11%**. Even the most aggressive pre-specified margin Δ₁, which drops nearly a quarter of the cells, reaches only 0.922 and is still 0.222 over. The upper edge is again immovable (−0.489 at every margin), confirming W18b's one-sided diagnosis exactly.

### R3 — Overall verdict `PRIMARY`

| Criterion | Inherited threshold | W18 | W18b | **W18c (Δ₃ PRIMARY)** | Verdict |
|---|---|---|---|---|---|
| E1 coverage @ κ=6 | ≥ 0.90 | 0.243 | 0.971 | **0.971** | **PASS** |
| E2 width @ k=24 | ≤ 0.70 logit | 0.509 | 1.033 | **0.997** | **FAIL** |
| Overall | both | — | FAIL | **FAIL, exit 1** | — |

### R4 — WHY it failed, measured directly `PRIMARY` (SYNTHETIC, 40 reps, diagnostic only — no criterion attached)

A D0-analogue for λ, run on the E1 DGP where the **true λ is 6.0** (grid top):

| Quantity | Value |
|---|---|
| argmax cell has λ = 0.0 (no true-risk channel at all) | 7/40 = **0.175** |
| argmax cell has λ = 1.5 | 8/40 = 0.200 |
| argmax cell has λ = 3.0 | 14/40 = 0.350 |
| argmax cell has λ = 6.0 — **the true value** | 11/40 = **0.275** |
| Total log-likelihood span across all 24 cells | median **3.313**, IQR [1.889, 5.018], min 1.113, max 7.722 |

Two numbers settle it.

1. **The likelihood picks the true λ cell 27.5% of the time**, against 25% for picking uniformly at random from the four λ levels. There is essentially no discrimination — and in 17.5% of replicates the best-supported cell says the true-risk channel is *absent* when it is in fact at the grid maximum. This is W18's D0 result, reproduced on the λ axis.
2. **The median total log-likelihood span across all 24 cells is 3.313, which is smaller than the primary margin Δ₃ = 3.9074.** In more than half of replicates the *entire grid* fits inside the retention region, so the primary screen **cannot exclude a single cell**. That is the arithmetic of R1's "24.0/24 cells kept".

The screen is not badly tuned; there is nothing for it to act on.

### R5 — Real data `PRIMARY` (repository record, cited from W18 via W18b, not re-verified by me)

**NOT APPLIED TO REAL DATA.** W18 recorded 3 of 14 registry cohorts with extractable `metastasis {events, denom}`, and at k=3 the *one-channel* bound already spans 0.204–0.460. Every bound reported here is **wider than the one-channel bound at every margin and every k**. Applying any of these three estimators to the EMC clinical registry would be the false-confidence failure this lane exists to prevent. I did not do it, did not read the registry, and assembled no EMC dataset. No case was added to any denominator.

### R6 — The lane's result, stated as W18b's dispatch requires

**The A2 (true-risk) selection channel can be MODELLED but not BOUNDED USEFULLY at EMC sample sizes.**

The three-worker arc is now closed and consistent. W18 built a one-channel Copas estimator and proved it *false* in a realistic regime (coverage 0.243). W18b showed the missing channel can be written down exactly — the algebra is clean, the λ=0 reduction is exact to 2.8e-14, and the repair is complete (coverage 0.971) — but costs 0.52 logit of width and fails usability. W18c has now shown that the width cannot be bought back from the data: at k≈24 the published record does not contain enough information to say which selection regime it came from, so an evidence-based restriction of the λ axis retains 23 of 24 cells and recovers 11% of the deficit. **W18's estimator was wrong; W18b's is right and uninformative; and W18c shows the uninformativeness is a property of the sample size, not of the grid.** That is a real, durable negative result about the estimator, and it should be recorded rather than attacked with a fourth variant.

---

## Validation evidence

Environment line printed by both harnesses:
```
environment: python 3.11.15 | numpy 2.4.6 | scipy 1.17.1 | Linux-6.18.44-fc-v24-x86_64-with-glibc2.39
```

### RUN 1 — E0 reduction re-check on the extracted modules (`RUN`)
```
$ cd /tmp/claude-0/w18c && python3 -c "
import sys; sys.path.insert(0,'/tmp/claude-0/w18c')
import emc_copas_two_channel as tc
print('import ok', tc.assert_reduces_to_w18())"
import ok 2.842170943040401e-14
```
Matches W18b's reported `2.842e-14`.

### RUN 2 — pilot, 4+4 replicates, for timing before committing the budget (`RUN`)
```
$ cd /tmp/claude-0/w18c && timeout 900 python3 run_lr_screen_acceptance.py 4 4
  E1: replicates 4 ; median k_pub 26 ; elapsed 34.7s ; DELTA_3 coverage 1.000 width 0.773 ; 24.0/24 cells kept
  E2: replicates 4 ; median k_pub 21 ; elapsed 46.0s ; DELTA_3 coverage 1.000 width 0.997 ; 22.0/24 cells kept
EXIT=1
```

### RUN 3 — the acceptance run, full protocol, 70 + 60 replicates (`RUN`)
```
$ cd /tmp/claude-0/w18c && python3 run_lr_screen_acceptance.py 70 60 > screen.log 2>&1; echo "EXIT=$?" >> screen.log
```
Verbatim from `screen.log`:
```
margins: DELTA_1=1.9207  DELTA_2=2.9957  DELTA_3(PRIMARY)=3.9074  (log-lik units)
replicates: E1=70 E2=60
==============================================================================
E1  BOUND COVERAGE, kappa=6 TRUE-RISK regime (seed 999+60)
    W18 one-channel 0.243 ; W18b all-24 union 0.971 (cited, not recomputed)
  replicates 70 ; median k_pub 24 ; elapsed 564.9s
  DELTA_1            coverage 0.971 | median width 0.726 logit | median bound [-1.037, -0.296] | median cells kept 21.0/24 | lambda values ever kept [0.0, 1.5, 3.0, 6.0]
  DELTA_2            coverage 0.971 | median width 0.737 logit | median bound [-1.044, -0.296] | median cells kept 23.0/24 | lambda values ever kept [0.0, 1.5, 3.0, 6.0]
  DELTA_3(PRIMARY)   coverage 0.971 | median width 0.741 logit | median bound [-1.044, -0.296] | median cells kept 24.0/24 | lambda values ever kept [0.0, 1.5, 3.0, 6.0]
  E1 PASS   (INHERITED criterion: coverage >= 0.90 ; achieved 0.971)
==============================================================================
E2  BOUND WIDTH at k_published ~ 24 (seed 4242+30, modelled selection)
    W18 one-channel 0.509 ; W18b all-24 union 1.033 (cited, not recomputed)
  replicates 60 ; median k_pub 24 ; elapsed 453.0s
  DELTA_1            coverage 1.000 | median width 0.922 logit | median bound [-1.389, -0.491] | median cells kept 18.5/24 | lambda values ever kept [0.0, 1.5, 3.0, 6.0]
  DELTA_2            coverage 1.000 | median width 0.974 logit | median bound [-1.455, -0.489] | median cells kept 22.0/24 | lambda values ever kept [0.0, 1.5, 3.0, 6.0]
  DELTA_3(PRIMARY)   coverage 1.000 | median width 0.997 logit | median bound [-1.475, -0.489] | median cells kept 23.0/24 | lambda values ever kept [0.0, 1.5, 3.0, 6.0]
  median k=24 bound width (UNCONDITIONAL REPORT) = 0.997 logit
  on the proportion scale the median bound is [0.186, 0.380]
  E2 FAIL   (INHERITED criterion: median width <= 0.70 logit ; achieved 0.997)
==============================================================================
SUMMARY (PRIMARY margin DELTA_3 = 3.9074)
  E1  PASS  coverage 0.971  (W18 0.243 -> W18b 0.971 -> W18c 0.971)
  E2  FAIL  width    0.997  (W18 0.509 -> W18b 1.033 -> W18c 0.997)
OVERALL: NOT ALL CRITERIA MET -- criteria were NOT relaxed
EXIT=1
```
**Exit code 1 is the real, correct exit code.** Nothing was relaxed.

### RUN 4 — λ-identifiability diagnostic (`RUN`, no acceptance criterion attached)
```
$ cd /tmp/claude-0/w18c && timeout 900 python3 lambda_d0.py
replicates 40 ; median k_pub 24 ; TRUE lambda = 6.0 (grid top)
  argmax-cell lambda == 0.0  :  7/40  (0.175)
  argmax-cell lambda == 1.5  :  8/40  (0.200)
  argmax-cell lambda == 3.0  : 14/40  (0.350)
  argmax-cell lambda == 6.0  : 11/40  (0.275)
fraction picking the TRUE lambda=6.0 cell : 0.275
fraction picking lambda=0 (no true-risk channel at all) : 0.175
total log-lik span across all 24 cells: median 3.313  IQR [1.889, 5.018]  min 1.113 max 7.722
PRE-SPECIFIED margins for reference: DELTA_1=1.9207 DELTA_2=2.9957 DELTA_3=3.9074
EXIT=0
```

### Pre-specification hash evidence (`RUN`)
```
$ sha256sum /tmp/claude-0/w18c/run_lr_screen_acceptance.py     # BEFORE any run of it
a88725206c3804d4766844c24e76afc0c23762f1ec375ce8f1d1ea7e6b308bfe

$ sha256sum run_lr_screen_acceptance.py lambda_d0.py            # AFTER all runs
a88725206c3804d4766844c24e76afc0c23762f1ec375ce8f1d1ea7e6b308bfe  run_lr_screen_acceptance.py
41a14d2afd8a54c365923da4ee0c81d8e37824ea15435f825a0088547552465b  lambda_d0.py
```
The acceptance script's hash is **unchanged**, so the docstring's pre-specified margin, thresholds and direction of interest are exactly what was in place before the first run. The result is not void.

### Write-isolation check (`RUN`)
```
$ git status --porcelain          # at start AND at end
(no output, both times)
$ git rev-parse HEAD
c81236b90c7905caa2e75a57b332ad33f2c10d02   # start
5ae0fa04ff9516ac8f820381079d644a094f4a77   # end (coordinator advanced the checkout)
```

### `PROPOSED (NOT RUN)`
- **Application to real EMC data — deliberately not run.** `NOT APPLIED TO REAL DATA.`
- **Retrieval of Copas & Shi (2000) — not run, by dispatch instruction.** Stays flagged unretrieved and unverified.
- `scripts/preflight.sh` — **not run**; dispatch forbade it and nothing was written to the tree.
- A registry read of any kind — not attempted.
- Recomputation of W18b's all-24-cell union at these seeds — not run; W18b's 0.971 / 1.033 are cited, and my Δ₃ row is the direct comparator.
- A λ-grid extended past 6, or a κ=12 truth against a λ≤6 grid — not run. `UNKNOWN`, inherited from W18b limitation 6.
- A fourth screening variant (data-adaptive Δ, BIC/AIC weighting, cell-averaged rather than union bound) — **deliberately not run**; see Next action.

---

## Limitations

1. **NOT APPLIED TO REAL DATA.** Every number above is synthetic. No EMC quantity is estimated, no case added to any denominator, no registry file read.
2. **The screen FAILS its inherited acceptance criterion** on E2 (0.997 vs ≤ 0.70 logit). It is not accepted. I did not move the line in either direction, and the hash evidence shows the criterion was fixed before the first run.
3. **The screen recovered only ~11% of the E2 deficit.** That is a small, real improvement over W18b (1.033 → 0.997), not a repair. Reporting it as progress would be misleading.
4. **The λ diagnostic is a diagnostic, not a proof of non-identifiability.** It measures argmax accuracy and log-likelihood span at *one* DGP (κ=6, 40 conducted, 24 published) with 40 replicates. It does not establish that λ is unidentifiable in general, only that at this scale the likelihood surface across the grid is flatter than the pre-specified retention margin. `UNKNOWN` outside this setting.
5. **The margins are χ²-calibrated but their nominal coverage is not verified here.** Δ₃ is the textbook profile-likelihood region for three parameters; whether that asymptotic calibration holds at k≈24 with two of the three parameters fixed on a coarse grid was not tested. A miscalibrated margin would change how many cells are kept — but note the failure direction: even Δ₁, far stricter than any calibration argument would justify, still misses E2 by 0.222.
6. **Coverage at E2 is 1.000 at every margin**, which is itself a diagnostic of over-covering, exactly as W18b noted. A bound that never misses in 60 replicates is not calibrated at 95%.
7. **W18's own F1 failure persists** (+0.0521 bias vs <0.05) and is untouched here. W18b reproduced it exactly; I did not re-run the D1/D2/D3 harness, since W18b already reproduced all eight of W18's exactly-reproducible runs digit-for-digit and I took that as given per dispatch.
8. **Grid dependence remains, and the screen does not remove it.** The bound is still a union over a grid I inherited (λ ≤ 6, ρ ≤ 0.8). A wider grid gives a wider bound without limit; the screen was the candidate fix for that and it did not work.
9. **A third selection channel is not excluded.** Nothing here shows the two-channel family is complete.
10. **Assumptions A3–A6 are untouched** — normality on the logit scale at small denominators, independence (the registry marks 8 of 14 cohorts `pool:false` for population overlap), known within-study SE, follow-up heterogeneity in a time-to-event outcome analysed as a proportion, and the coherence of "conducted but unpublished EMC series".
11. **D0 remains not bit-reproducible** (W18 published neither its script nor its seed); W18b reconstructed it from prose. My R4 is a *λ*-analogue I wrote fresh, not a reproduction of W18's D0, and should not be read as certifying it.
12. **The Copas & Shi (2000) citation remains unretrieved and unverified.** The algebra is self-contained; the attribution is not verified.
13. **scipy is not a pinned repository dependency.** If any of this is integrated it must be declared and pinned. My script adds no dependency beyond W18's.
14. **Concurrent load.** The container ran at load average 4–8 on 4 cores (other campaign workers). This affects wall-clock timings only; results are seeded and deterministic given the code.
15. **Transfer limit — the important one.** This is a statistical method validated by simulation. **It establishes something about the estimator and about nothing else** — no EMC biology, no treatment effect, no association, no efficacy, safety, selectivity or clinical readiness. There is no wet lab. It is not a proposed clinical paper.

---

## Stop condition

**Set up front, before the first run:** return the moment both inherited criteria have been evaluated under the pre-specified primary margin with a real exit code, the k=24 median bound width has been reported unconditionally, and the before/after hashes of the acceptance script have been shown.

**MET.** Both criteria evaluated at Δ₃ = 3.9074 on the full W18b protocol (70 + 60 replicates, identical DGPs and seeds): **E1 PASS at 0.971, E2 FAIL at 0.997 logit, harness exit code 1.** The k=24 median bound width is **0.997 logit** (0.186–0.380 on the proportion scale), reported unconditionally. Script sha256 identical before and after (`a887252…8bfe`). Criteria were not relaxed. I stopped here and did not start a fourth variant.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 17** (14 Bash, 1 ToolSearch, 1 Monitor, 1 background Bash launch). Target ~40 — **well under**.
- **Wall clock: 03:17:45Z → 03:39:23Z ≈ 22 minutes.** Target ~40 — **under**. The acceptance run dominated (1018 s = 17.0 min for E1+E2); the λ diagnostic added ~40 s. Screening made the run *faster* than W18b's 1289 s at identical replicate counts, because excluded cells skip their profile-CI bisection.
- No network requests, no paid API, no GPU spend, no repository writes, no git operations, no external contact, no publication, no `preflight.sh`. **No content-policy refusal and no permission denial was encountered.**

---

## Next concrete action

**No viable successor in this lane, and that is the finding — not a scheduling gap.**

W18b's dispatch pre-committed to this, and I am honouring it: the screen failed for the principled reason stated before it ran, so the correct action is to **write the conclusion down and close lane 18**, not to try a fourth variant. R4 measures why any such variant would fail: the median log-likelihood span across the whole 24-cell grid (3.313) is smaller than the primary retention margin (3.907), and the best-supported λ cell is the true one only 27.5% of the time against 25% for chance. Data-adaptive margins, information-criterion weighting, or an averaged rather than union bound would all be re-parameterisations of a likelihood surface that is flat at this sample size. They would change the number without changing what is known.

**The one concrete action I recommend to the coordinator** is a documentation action, not a modelling one: record in the campaign's synthesis (`W23-cross-output-synthesis-packet.md` already carries the one-line W18 entry) the closed three-step negative result — *the A2 true-risk selection channel can be modelled exactly but not bounded usefully at EMC sample sizes; W18's one-channel bound is false in that regime, W18b's two-channel bound is honest but 2× too wide, and W18c shows the width is irreducible from the data* — and mark lane 18 closed with the code preserved. If W18/W18b/W18c code is integrated, fix W18's reporting gap by committing its D0 script and seed, since that is the single artifact three workers could not reproduce bit-for-bit.

**What must not be done next, explicitly.** Do not apply any of the three estimators to the EMC clinical registry. The one-channel bound at k=3 already spans 0.204–0.460; every bound reported here is wider at every k and every margin; and the registry has 3 extractable cohorts, not 24. Applying any of them would manufacture exactly the false confidence this lane exists to prevent.
