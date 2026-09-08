<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:16:10Z UTC
     agent id a3a0bb609b153379b ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a3a0bb609b153379b.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

All runs complete. Stop condition met.

---

## Worker

**W18b** — Lane 18 refill (successor to W18), OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in the environment confirms a served model; no `model` key exists anywhere in the environment. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start / end:
```
Tue Sep  8 02:38:25 UTC 2026
Tue Sep  8 03:07:10 UTC 2026
```

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — full output captured at start (43 lines); identity-relevant subset, verbatim at end:
```
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_EFFORT=medium
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
```
Start-of-run extras: `CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605`, `CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f`, `CLAUDE_CODE_CHILD_SESSION=1`, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`, `CLAUDE_SESSION_INGRESS_TOKEN=<redacted>`, `CLAUDE_CODE_MESSAGING_TOKEN=<redacted>`.

**HEAD actually read — and it moved during my run.** At start `git rev-parse HEAD` = `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`; at end = `98a0833f1ede2cf9cef13790388260567a32e868`. Neither is the `92abbcb905cacf07f14b238db50d1b98f6590374` named in `COMMON-BRIEF.md`, and neither is the `47aac85f…` W18 recorded. The checkout is being advanced by the coordinator while workers run. I read the tree as I found it.

**Write isolation honoured.** `git status --porcelain` empty at end; no repository file created or modified; no git write operation. All execution under `/tmp/claude-0/w18b/`. I read the live checkout plus the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/` (read-only, not copied, not overlaid).

---

## Question

**Can the selection family be extended with an explicit second channel for selection on the study's true risk, so that W18's A2 violation becomes a gridded sensitivity dimension rather than an unmodelled fatal assumption?**

Open because W18 proved the one-channel Copas estimator *false* in a realistic EMC regime — bound coverage collapsing to 0.243 at κ=6 — and named this extension as its own successor with a pre-specified acceptance criterion it did not itself test.

---

## Prior-work check

```
rg -n -i "copas" --glob '!.git' -l
  -> research/autonomy/opus-capacity-campaign-20260908/reports/W18-publication-selection-estimator.md   (only hit)

rg -n -i "two-channel|second selection channel|selection on true risk" --glob '!.git' -l
  -> W18-publication-selection-estimator.md   (only hit)

git ls-files | rg -i "copas|selection|meta"
  -> no selection-model file; `research/meta/` contains meta-analysis.mjs + results.json (JS, unrelated)

grep -ril "copas" /tmp/claude-0/frozen-corpus/extracted/corpus/
  -> (no output)
```
The frozen corpus contains no Copas-type selection model either, so this is not a rediscovery. Absence in the corpus is UNKNOWN for the wider repository, not proof of absence — but the live tracked tree was searched directly and returns only W18's own report.

**CLOSED-WORK.md items confirmed not replayed.** No PUB-EMC-CLASSIFICATION, no Brenca route, no PUB-ASO, no frozen external-validation comment, no NR4A Perspective under any label. **No network requests at all**, so none of the recorded 403/EGRESS_BLOCKED routes was retried, and — per my dispatch — I did **not** attempt to retrieve Copas & Shi (2000). That citation **remains flagged as unretrieved and unverified**, inherited from W18 unchanged. No case added to any denominator. Not lane 11; no source-index file touched.

One denied action to record honestly: a `python3 -c` read of `research/data/emc-clinical-registry.json` was **blocked by the auto-mode classifier**. I did not route around it. Consequence: W18's registry figures (3 of 14 cohorts with extractable `metastasis {events, denom}`) are **cited as W18's, not independently re-verified by me**. This does not affect any result below, all of which are synthetic.

---

## Method / inputs

| Item | Value |
|---|---|
| Read (read-only) | `…/opus-capacity-campaign-20260908/{COMMON-BRIEF,CLOSED-WORK,CORPUS-CONTEXT}.md`; `reports/W18-publication-selection-estimator.md` (847 lines, in full); frozen corpus grep |
| Reconstructed from W18's report | `emc_copas_selection.py`, `run_validation.py`, `k_feasibility.py`, `f2_kappa_sweep.py` — **verbatim**, sole change `sys.path` `/tmp/claude-0/w18` → `/tmp/claude-0/w18b` |
| Reconstructed from W18's **prose only** | `repro_d0.py` — W18 did **not** return the D0 script inline (unshown heredoc) and gave no seed; best-effort, flagged below |
| Authored new | `emc_copas_two_channel.py`, `run_extension_acceptance.py` |
| Python / numpy / scipy | 3.11.15 / 2.4.6 / 1.17.1 — **identical to W18's** |
| Platform | `Linux-6.18.44-fc-v24-x86_64-with-glibc2.39` |
| Data | **ALL SYNTHETIC**, seeded `numpy.random.default_rng`. `NOT APPLIED TO REAL DATA.` |

### The extension

W18's propensity gains one term:

```
y_i = theta + u_i + eps_i,   u_i ~ N(0, tau^2),  eps_i ~ N(0, s_i^2)
z_i = gamma0 + gamma1/s_i  +  lambda*(u_i/tau)  +  delta_i,   delta_i ~ N(0,1)
corr(delta_i, eps_i) = rho ,   u_i independent of delta_i
```
- channel 1 (`rho`): the series *happened* to come out striking — sampling error. W18's only channel.
- channel 2 (`lambda`): the centre's *real* case-mix is worse and it writes up more often — **true risk**. This is exactly W18's A2 violation, now a parameter.

With `sigma_i^2 = tau^2+s_i^2`, `v_i = gamma0+gamma1/s_i`, `omega^2 = 1+lambda^2`, `c_i = lambda*tau + rho*s_i`:

```
log f(y_i | z_i>0) = log phi(y_i; theta, sigma_i)
                   + log Phi( [v_i/omega + (c_i/(sigma_i^2*omega))*(y_i-theta)]
                              / sqrt(1 - c_i^2/(sigma_i^2*omega^2)) )
                   - log Phi(v_i/omega)
```
Cauchy–Schwarz gives `|c_i| < sigma_i*omega` whenever `|rho|<1`, so the model is coherent everywhere on the grid. At `lambda=0` it is algebraically W18's likelihood; that identity is asserted **numerically** (test E0).

`lambda` is **not estimated** — for W18's D0 reason. It joins `rho` and `P(publish | least precise)` as a third gridded axis.

**Grid size, stated plainly: 3 (`rho`) × 4 (`lambda`) × 2 (`p_least`) = 24 cells, up from W18's 6.**

The pre-specified acceptance criterion was written into the docstring of both new files **before** the first run and was not moved.

---

## Result

### R1 — Reproduction gate: W18's runs reproduce **exactly**, with one flagged caveat `PRIMARY` (computational, synthetic)

| W18 run | W18 reported | W18b reproduced | Verdict |
|---|---|---|---|
| D1 honest bound (logit) | `[-1.061, -0.529]` → prop `[0.257, 0.371]` | `[-1.061, -0.529]` → `[0.257, 0.371]` | **exact** |
| D1 naive DL | `-0.707 [-0.884,-0.531]`, prop `0.330` | identical | **exact** |
| D1 multistart spread | `4.50e-08` | `4.50e-08` | **exact** |
| D2 Copas bias / coverage | `+0.0521` / `0.933` | `+0.0521` / `0.933` | **exact** |
| D2 naive bias / coverage | `+0.1115` / `0.753` | `+0.1115` / `0.753` | **exact** |
| D3 coverage / width | `0.960` / `0.459` | `0.960` / `0.459` | **exact** |
| F2 @ κ=1.5 coverage | `0.867`, bound `[-0.906,-0.463]` | `0.867`, `[-0.906,-0.463]` | **exact** |
| F2 κ sweep (4 rows) | `0.900 / 0.529 / 0.243 / 0.243` | `0.900 / 0.529 / 0.243 / 0.243` | **exact** |
| k-feasibility (5 rows) | k=3 `[0.204,0.460]` w=1.156 … k=48 w=0.383 | all five rows identical | **exact** |
| Harness exit code | `1` | `1` | **exact** |
| **D0 ρ identifiability** | median `-0.277`, IQR `[-0.891,0.073]`, boundary `0.23`, **wrong-sign `0.68`**, k=31 | median `-0.275`, IQR `[-0.875,0.063]`, boundary `0.25`, **wrong-sign `0.65`**, k=31 | **close, not exact — see below** |

**The D0 caveat is a reporting gap in W18, not a discrepancy in its results.** W18 returned the module and three harness scripts inline but **not** the D0 heredoc, and named no seed for it. I reconstructed D0 from prose (60 reps, 40 conducted, true ρ=0.70, profile MLE of ρ over a 41-point grid, seed 20260908, `n_starts=2`). Every reconstructed statistic lands within sampling noise of W18's, the median published k matches exactly at 31, and the load-bearing conclusion is unchanged: **selection strength carries the wrong sign in roughly two thirds of replicates and cannot be estimated at EMC scale.** I cannot certify D0 as bit-reproducible, and I do not.

Everything W18 returned as code reproduces **digit-for-digit**. No discrepancy found in the eight exactly-reproducible runs.

### R2 — E0, the extension contains W18's model as the λ=0 face `PRIMARY`

Max `|loglik(two-channel, λ=0) − loglik(W18)|` over 36 parameter points = **2.842e-14** (floating-point noise). **E0 PASS.** The extension is a strict generalisation, not a replacement.

### R3 — E1, the A2 failure is repaired `PRIMARY` (SYNTHETIC, truth θ = −0.800)

Identical DGP, seed (`999+60`) and 70 replicates as W18's κ=6 sweep row.

| Estimator | grid cells | bound coverage @ κ=6 | median bound (logit) | median width |
|---|---|---|---|---|
| W18 one-channel | 6 | **0.243** | `[-0.734, -0.296]` | 0.438 |
| **W18b two-channel** | 24 | **0.971** | `[-1.044, -0.296]` | 0.747 |

**E1 PASS** (criterion ≥ 0.90). Coverage goes 0.243 → 0.971. The mechanism is visible and one-sided: the **upper** bound edge is unchanged at −0.296, and the entire repair comes from the λ>0 cells extending the **lower** edge from −0.734 to −1.044. That is the point — the true-risk channel was pushing the truth *below* the one-channel bound, and now the bound reaches it.

### R4 — E2, the cost, and it is too high `PRIMARY` (SYNTHETIC)

Identical DGP, seed (`4242+30`) and 60 replicates as W18's k-feasibility k=24 row.

| Estimator | median k_pub | **median bound width (logit)** | bound coverage | median bound (logit) | median bound (proportion) |
|---|---|---|---|---|---|
| W18 one-channel | 24 | **0.509** | 0.950 | `[-0.975, -0.489]` | `[0.274, 0.380]` |
| **W18b two-channel** | 24 | **1.033** | 1.000 | `[-1.511, -0.489]` | `[0.181, 0.380]` |

**E2 FAIL** (criterion ≤ ~0.70 logit; achieved **1.033**, over by 0.333 — a 48% overshoot, not a rounding miss). **I did not move the line.**

Again the arithmetic is one-sided and exact: upper edge unchanged (−0.489), lower edge pushed from −0.975 to −1.511, i.e. −0.536; observed width increase +0.524. **The width cost is entirely the λ>0 cells, the same cells that bought the coverage.** Coverage rises to a perfect 1.000 — which is itself the diagnostic: a bound that never misses at k=24 is over-covering, and on the proportion scale it now spans 0.181–0.380, a factor of 2.1.

### R5 — Overall verdict `PRIMARY`

| Criterion | Threshold | Achieved | Verdict |
|---|---|---|---|
| E0 reduction | < 1e-8 | 2.842e-14 | PASS |
| E1 coverage @ κ=6 | ≥ 0.90 | 0.971 | PASS |
| E2 width @ k=24 | ≤ 0.70 logit | **1.033** | **FAIL** |
| **Overall** | both E1 and E2 | — | **FAIL, exit 1** |

**The honest answer to the lane question is: yes and no, and the "no" is the part that matters.** The A2 violation *can* be turned into a gridded sensitivity dimension — the algebra is clean, the reduction is exact, and it fully repairs the regime where W18's estimator was provably false. But at the sample sizes this disease produces, the repair buys honesty by paying ~0.52 logit of width, and it fails W18's own usefulness threshold. **W18's estimator was wrong; W18b's estimator is right and uninformative.** That is a real result about the estimator, and it is not a solution.

### R6 — Real data `PRIMARY` (repository record, cited from W18, not re-verified by me)

**`NOT APPLIED TO REAL DATA.`** W18 recorded 3 of 14 registry cohorts with extractable `metastasis {events, denom}`, and at k=3 the *one-channel* bound already spans 0.204–0.460 with sub-nominal coverage (0.868). The two-channel bound is **wider** at every k. Applying either to the EMC registry would be the false-confidence failure this lane exists to prevent. I did not do it, and I did not assemble any EMC dataset.

---

## Validation evidence

Environment line printed by both harnesses:
```
environment: python 3.11.15 | numpy 2.4.6 | scipy 1.17.1 | Linux-6.18.44-fc-v24-x86_64-with-glibc2.39
```

### RUN 1 — W18 harness reproduction (`RUN`)
```
$ cd /tmp/claude-0/w18b && python3 run_validation.py > validation.log 2>&1; echo "EXIT=$?"
```
Verbatim tail:
```
  HONEST BOUND (union over grid): logit [-1.061, -0.529]  ->  proportion [0.257, 0.371]
  naive DerSimonian-Laird on published only: -0.707 [-0.884, -0.531] -> proportion 0.330
  all converged=True ; max multistart theta spread=4.50e-08 ; D1 PASS
==============================================================================
D2/F1  CALIBRATION AND RECOVERY, selection parameters KNOWN (300 reps)
  usable replicates: 300 ; elapsed 99.2s
  Copas @ true selection : mean theta -0.7479  bias +0.0521  SD 0.0898  coverage 0.933
  naive DerSimonian-Laird: mean theta -0.6885  bias +0.1115  SD 0.0884  coverage 0.753
  D2 PASS ; F1 FAIL
==============================================================================
D3  BOUND COVERAGE, modelled selection of UNKNOWN strength (150 reps)
  replicates 150 ; elapsed 325.0s ; bound coverage 0.960 ; median bound width 0.459 logit
  D3 PASS
==============================================================================
F2  FALSIFICATION: ... (150 reps, kappa=1.5)
  replicates 150 ; elapsed 338.7s
  bound coverage of the true theta = 0.867   (median bound [-0.906, -0.463] vs truth -0.800)
  F2 DID NOT FIRE: coverage >= 0.50, reported as a non-firing test
==============================================================================
SUMMARY
  D1   PASS
  D2   PASS
  F1   FAIL
  D3   PASS
  F2   NOT FIRED
OVERALL: NOT ALL CRITERIA MET
EXIT=1
```
**Exit 1 is correct and matches W18's exit 1.** F1 fails by the same +0.0521 vs <0.05. I did not relax it.

### RUN 2 — k-feasibility (`RUN`)
```
$ cd /tmp/claude-0/w18b && python3 k_feasibility.py
k_pub  reps  bound coverage  median bound width (logit)  median bound (proportion scale)
  3.0    38          0.868                      1.156   [0.204, 0.460]
  6.0    59          0.932                      0.990   [0.220, 0.435]
 12.0    60          0.983                      0.697   [0.250, 0.402]
 24.0    60          0.950                      0.509   [0.274, 0.380]
 48.0    60          1.000                      0.383   [0.279, 0.362]
EXIT=0
```

### RUN 3 — F2 κ sweep (`RUN`)
```
$ cd /tmp/claude-0/w18b && python3 f2_kappa_sweep.py
kappa  reps  k_pub  bound coverage  median bound (logit)      vs truth -0.800
  1.5    70     30          0.900   [-0.883, -0.436]
  3.0    70     26          0.529   [-0.803, -0.343]
  6.0    70     24          0.243   [-0.734, -0.296]
 12.0    70     22          0.243   [-0.734, -0.288]
EXIT=0
```

### RUN 4 — D0 reconstruction (`RUN`, reconstructed from prose, not W18's script)
```
$ cd /tmp/claude-0/w18b && python3 repro_d0.py
replicates: 60 median published k: 31
true rho = 0.70 ; fitted rho: median -0.275  IQR [-0.875, 0.063]  min -0.999 max 0.999
fraction at |rho|>0.995 boundary: 0.25
fraction with WRONG SIGN (rho<0): 0.65
EXIT=0
```

### RUN 5 — two-channel acceptance test (`RUN`)
```
$ cd /tmp/claude-0/w18b && python3 run_extension_acceptance.py > extension.log 2>&1; echo "EXIT=$?"
```
```
grid: rho (0.0, 0.4, 0.8) x lambda (0.0, 1.5, 3.0, 6.0) x p_least (0.99, 0.3)  ->  24 cells (W18 bound grid: 6 cells)
==============================================================================
E0  REDUCTION: two-channel loglik at lambda=0 vs W18 copas_loglik
  max abs difference over 36 parameter points = 2.842e-14 ; E0 PASS
==============================================================================
E1  BOUND COVERAGE in the kappa=6 TRUE-RISK regime (70 reps, seed 999+60)
    W18 one-channel result at this exact setting: coverage 0.243
  replicates 70 ; median k_pub 24 ; elapsed 668.1s
  bound coverage = 0.971  (median bound [-1.044, -0.296] vs truth -0.800 ; median width 0.747 logit)
  E1 PASS   (criterion: coverage >= 0.90)
==============================================================================
E2  BOUND WIDTH at k_published ~ 24 (60 reps, seed 4242+30, modelled selection)
    W18 one-channel result at this exact setting: median width 0.509 logit
  replicates 60 ; median k_pub 24 ; elapsed 621.2s
  median bound width = 1.033 logit ; bound coverage 1.000 ; median bound [-1.511, -0.489]
  on the proportion scale the median bound is [0.181, 0.380]
  E2 FAIL   (criterion: median width <= 0.70 logit)
==============================================================================
SUMMARY
  E0  PASS
  E1  PASS
  E2  FAIL
OVERALL: NOT ALL CRITERIA MET -- criteria were NOT relaxed
EXIT=1
```

### Write-isolation check (`RUN`)
```
$ git status --porcelain | head
(no output)
$ git rev-parse HEAD
98a0833f1ede2cf9cef13790388260567a32e868      # start of run: d3e9c4d876...
```

### `PROPOSED (NOT RUN)`
- Application to real EMC data — deliberately not run. `NOT APPLIED TO REAL DATA`.
- Retrieval of Copas & Shi (2000) — **not run, by dispatch instruction.** Citation stays flagged unverified.
- `scripts/preflight.sh` — not run; dispatch did not authorise it and nothing was written to the tree.
- A λ-grid narrowing study (see Next action) — **not run**.
- Registry re-verification of the 3-of-14 cohort count — **blocked by the auto-mode classifier**, not routed around.

---

## Code

Returned inline. Path suggestions only; the coordinator decides placement. `emc_copas_selection.py`, `run_validation.py`, `k_feasibility.py`, `f2_kappa_sweep.py` are **W18's, unchanged apart from the `sys.path` line** — they are already in W18's report and I do not repeat them here. The two new files follow.

### `research/meta/emc_copas_two_channel.py` (suggested path)

```python
"""
emc_copas_two_channel.py -- W18b. TWO-CHANNEL publication-selection model.

============================== PRE-SPECIFIED ACCEPTANCE CRITERION ==============================
Set by W18 in `research/autonomy/opus-capacity-campaign-20260908/reports/
W18-publication-selection-estimator.md`, section "Next concrete action", and written here BEFORE
any run of this module. It is NOT permitted to move:

  E1  The extended estimator must restore honest-bound coverage of the true theta to >= 0.90
      in the kappa=6 regime (selection driven by the study's TRUE risk u_i) where W18's
      one-channel estimator collapses to 0.243.
  E2  ... WITHOUT inflating the k=24 published-series bound width beyond about 0.7 logit.
      (W18's one-channel grid gave median bound width 0.509 logit at median k_pub=24.)

A bound that is honest because it is uselessly wide is not a solution. The k=24 median bound
width is reported unconditionally, pass or fail.
================================================================================================

ALL DATA SYNTHETIC. NOT APPLIED TO REAL DATA.

MODEL. Extends W18's Copas-type propensity with an explicit SECOND CHANNEL for selection on the
study's own true risk -- the A2 violation that W18 proved fatal:

    y_i     = theta + u_i + eps_i,    u_i ~ N(0, tau^2),  eps_i ~ N(0, s_i^2)
    z_i     = gamma0 + gamma1/s_i  +  lambda * (u_i / tau)  +  delta_i,     delta_i ~ N(0,1)
    corr(delta_i, eps_i) = rho ,   u_i _||_ delta_i

  channel 1 (rho)    : "the series happened to come out striking"      -- sampling error
  channel 2 (lambda) : "the centre's real case-mix is worse and it writes up more often"
                       -- TRUE risk. lambda = 0 recovers W18's model exactly.

JOINT LAW (both channels active). Writing sigma_i^2 = tau^2 + s_i^2, v_i = gamma0 + gamma1/s_i:
    Var(y_i)    = sigma_i^2
    Var(z_i)    = 1 + lambda^2                      =: omega^2
    Cov(y_i,z_i)= lambda*tau + rho*s_i              =: c_i
By Cauchy-Schwarz |c_i| < sigma_i*omega whenever |rho| < 1, so the model is always coherent.
Standardising z' = z/omega, the conditional log-likelihood of the PUBLISHED studies is

    log f(y_i | z_i > 0) = log phi(y_i; theta, sigma_i)
                         + log Phi( [ v_i/omega + (c_i/(sigma_i^2 * omega))*(y_i - theta) ]
                                    / sqrt(1 - c_i^2/(sigma_i^2 * omega^2)) )
                         - log Phi( v_i / omega )

At lambda = 0 this is algebraically identical to W18's `copas_loglik` (omega=1, c_i = rho*s_i);
that identity is asserted numerically by `assert_reduces_to_w18` below.

IDENTIFIABILITY. lambda is NOT estimated, for exactly the reason W18's D0 gives for rho: at EMC
scale the published record cannot identify selection strength. lambda joins rho and
P(publish | least precise) as a THIRD GRIDDED SENSITIVITY DIMENSION. The A2 violation therefore
becomes a stated grid axis rather than an unmodelled fatal assumption. The cost is arithmetic:
the bound grid goes from 3 x 2 = 6 cells to 3 x 4 x 2 = 24 cells, and the bound can only widen.

Note: `gammas_from_publication_probs` is reused UNCHANGED from W18, so the p_least label refers
to the marginal publication probability of the least precise series WHEN lambda = 0. At
lambda > 0 the realised marginal is Phi(v/omega), which is pulled toward 0.5.

Requires numpy, scipy. scipy is NOT a pinned repository dependency (see W18 limitation 9).
"""
from __future__ import annotations

import numpy as np
from scipy import optimize
from scipy.stats import norm, chi2

import emc_copas_selection as w18
from emc_copas_selection import (  # reused UNCHANGED
    logit_transform, dersimonian_laird, gammas_from_publication_probs,
    simulate_conducted, select_copas, select_on_random_effect, _expit,
)

_TINY = 1e-12

DEFAULT_RHO_GRID = (0.0, 0.4, 0.8)
DEFAULT_LAMBDA_GRID = (0.0, 1.5, 3.0, 6.0)
DEFAULT_PLEAST_GRID = (0.99, 0.3)


def two_channel_loglik(theta, tau, rho, lam, gamma0, gamma1, y, s):
    """Conditional log-likelihood of the PUBLISHED studies under the two-channel model."""
    tau = abs(tau)
    sig2 = tau ** 2 + s ** 2
    sig = np.sqrt(sig2)
    v = gamma0 + gamma1 / s
    omega = np.sqrt(1.0 + lam ** 2)
    c = lam * tau + rho * s
    r2 = c ** 2 / (sig2 * omega ** 2)
    denom = 1.0 - r2
    if np.any(denom <= _TINY):
        return -np.inf
    num = v / omega + (c / (sig2 * omega)) * (y - theta)
    ll = (norm.logpdf(y, loc=theta, scale=sig)
          + norm.logcdf(num / np.sqrt(denom))
          - norm.logcdf(v / omega))
    if not np.all(np.isfinite(ll)):
        return -np.inf
    return float(np.sum(ll))


def fit_two_channel_at(y, s, gamma0, gamma1, rho, lam, n_starts: int = 3, seed: int = 0):
    """Maximise over (theta, tau) at a FIXED selection quadruple (gamma0, gamma1, rho, lambda)."""
    y = np.asarray(y, float); s = np.asarray(s, float)
    rng = np.random.default_rng(seed)
    dl_theta, dl_tau2, _ = dersimonian_laird(y, s)

    def nll(p):
        val = two_channel_loglik(p[0], np.exp(p[1]), rho, lam, gamma0, gamma1, y, s)
        return -val if np.isfinite(val) else 1e10

    starts = [np.array([dl_theta, np.log(max(np.sqrt(dl_tau2), 0.05))])]
    for _ in range(n_starts - 1):
        starts.append(np.array([dl_theta + rng.normal(0, 0.4),
                                rng.uniform(np.log(0.02), np.log(1.0))]))
    best, res = None, []
    for x0 in starts:
        r = optimize.minimize(nll, x0, method="Nelder-Mead",
                              options={"xatol": 1e-7, "fatol": 1e-9, "maxiter": 1500})
        res.append(r)
        if best is None or r.fun < best.fun:
            best = r
    near = np.array([r.x[0] for r in res if r.fun < best.fun + 1.0])
    return {
        "theta": float(best.x[0]), "tau": float(np.exp(best.x[1])),
        "rho": float(rho), "lam": float(lam), "loglik": float(-best.fun),
        "converged": bool(all(r.success for r in res)),
        "multistart_theta_spread": float(np.ptp(near)) if near.size > 1 else 0.0,
        "gamma0": float(gamma0), "gamma1": float(gamma1),
    }


def _profile_ci_theta2(y, s, gamma0, gamma1, rho, lam, ll_hat, theta_hat,
                       level=0.95, halfwidth=4.0, n_bisect=22, maxiter=600):
    """Profile-likelihood CI for theta, tau profiled out, at fixed selection quadruple.
    Same bisection schedule as W18's `_profile_ci_theta`."""
    cut = ll_hat - 0.5 * chi2.ppf(level, 1)

    def prof(theta):
        def nll(p):
            val = two_channel_loglik(theta, np.exp(p[0]), rho, lam, gamma0, gamma1, y, s)
            return -val if np.isfinite(val) else 1e10
        r = optimize.minimize(nll, np.array([np.log(0.2)]), method="Nelder-Mead",
                              options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": maxiter})
        return -r.fun

    out = []
    for sign in (-1, +1):
        lo, hi = theta_hat, theta_hat + sign * halfwidth
        if prof(hi) - cut > 0:
            out.append(hi); continue
        for _ in range(n_bisect):
            mid = 0.5 * (lo + hi)
            if prof(mid) - cut > 0:
                lo = mid
            else:
                hi = mid
        out.append(0.5 * (lo + hi))
    return float(out[0]), float(out[1])


def sensitivity_surface2(y, s, rho_grid=DEFAULT_RHO_GRID, lam_grid=DEFAULT_LAMBDA_GRID,
                         p_least_grid=DEFAULT_PLEAST_GRID, p_most_precise: float = 0.99,
                         with_ci: bool = True, seed: int = 0, **ci_kw):
    """Three-dimensional sensitivity surface: rho x lambda x P(publish | least precise)."""
    y = np.asarray(y, float); s = np.asarray(s, float)
    rows = []
    for rho in rho_grid:
        for lam in lam_grid:
            for p_lo in p_least_grid:
                g0, g1 = gammas_from_publication_probs(s, p_most_precise, p_lo)
                fit = fit_two_channel_at(y, s, g0, g1, rho, lam, seed=seed)
                fit["p_least_precise"] = float(p_lo)
                if with_ci:
                    fit["ci_lo"], fit["ci_hi"] = _profile_ci_theta2(
                        y, s, g0, g1, rho, lam, fit["loglik"], fit["theta"], **ci_kw)
                rows.append(fit)
    return rows


def honest_bound(rows):
    return min(r["ci_lo"] for r in rows), max(r["ci_hi"] for r in rows)


def assert_reduces_to_w18(seed=1):
    """NUMERICAL PROOF that lambda=0 reproduces W18's one-channel likelihood exactly."""
    rng = np.random.default_rng(seed)
    y, s, ti, ev, nn = simulate_conducted(rng, 25, -0.8, 0.5)
    g0, g1 = gammas_from_publication_probs(s, 0.99, 0.3)
    worst = 0.0
    for rho in (0.0, 0.3, 0.7, 0.9):
        for theta in (-1.2, -0.8, -0.3):
            for tau in (0.1, 0.5, 0.9):
                a = w18.copas_loglik(theta, tau, rho, g0, g1, y, s)
                b = two_channel_loglik(theta, tau, rho, 0.0, g0, g1, y, s)
                worst = max(worst, abs(a - b))
    return worst
```

### `research/meta/tests/run_extension_acceptance.py` (suggested path)

```python
"""
W18b acceptance test for the TWO-CHANNEL selection model. ALL DATA SYNTHETIC.
NOT APPLIED TO REAL DATA.

============================== PRE-SPECIFIED ACCEPTANCE CRITERION ==============================
Copied verbatim from W18's "Next concrete action". Written here BEFORE running. NOT movable:

  E1  bound coverage >= 0.90 in the kappa=6 regime (W18 one-channel: 0.243)
  E2  median k=24 bound width <= 0.70 logit          (W18 one-channel: 0.509)

  PASS requires BOTH. The k=24 width is reported whatever happens.
  E0 (mechanical) : the two-channel log-likelihood at lambda=0 must equal W18's to < 1e-8.

Protocols are matched to W18's originals so the numbers are directly comparable:
  E1 uses the exact DGP, seed (999+60) and 70 replicates of W18's `f2_kappa_sweep.py` at kappa=6.
  E2 uses the exact DGP, seed (4242+30) and 60 replicates of W18's `k_feasibility.py` at
     k_conducted=30 (which W18 reports as median k_published = 24).
================================================================================================
"""
import sys, time, platform
import numpy as np
sys.path.insert(0, '/tmp/claude-0/w18b')   # coordinator: repoint at the module's real home
import scipy
import emc_copas_selection as w18
import emc_copas_two_channel as tc

TH, TAU = -0.8, 0.5
RHO_G, LAM_G, PL_G = tc.DEFAULT_RHO_GRID, tc.DEFAULT_LAMBDA_GRID, tc.DEFAULT_PLEAST_GRID
NCELL = len(RHO_G) * len(LAM_G) * len(PL_G)
W18_RHO_G, W18_PL_G = (0.0, 0.4, 0.8), (0.99, 0.3)
ex = lambda x: 1.0 / (1.0 + np.exp(-x))


def main():
    print("environment: python %s | numpy %s | scipy %s | %s"
          % (platform.python_version(), np.__version__, scipy.__version__, platform.platform()))
    print(__doc__)
    print("grid: rho %s x lambda %s x p_least %s  ->  %d cells (W18 bound grid: %d cells)"
          % (RHO_G, LAM_G, PL_G, NCELL, len(W18_RHO_G) * len(W18_PL_G)))
    v = {}

    print("=" * 78)
    print("E0  REDUCTION: two-channel loglik at lambda=0 vs W18 copas_loglik")
    worst = tc.assert_reduces_to_w18()
    v["E0"] = worst < 1e-8
    print("  max abs difference over 36 parameter points = %.3e ; E0 %s"
          % (worst, "PASS" if v["E0"] else "FAIL"))

    print("=" * 78)
    print("E1  BOUND COVERAGE in the kappa=6 TRUE-RISK regime (70 reps, seed 999+60)")
    print("    W18 one-channel result at this exact setting: coverage 0.243")
    rng = np.random.default_rng(999 + 60)
    hit, los, his, kp, wid = [], [], [], [], []
    t0 = time.time()
    for rep in range(70):
        y, s, ti, e, n = w18.simulate_conducted(rng, 40, TH, TAU)
        g0, g1 = w18.gammas_from_publication_probs(s, 0.99, 0.6)
        sel = w18.select_on_random_effect(rng, y, s, ti, TH, g0, g1, kappa=6.0)
        if sel.sum() < 8:
            continue
        rows = tc.sensitivity_surface2(y[sel], s[sel], seed=rep)
        lo, hi = tc.honest_bound(rows)
        hit.append(lo <= TH <= hi); los.append(lo); his.append(hi)
        wid.append(hi - lo); kp.append(int(sel.sum()))
    e1 = float(np.mean(hit))
    print("  replicates %d ; median k_pub %d ; elapsed %.1fs" % (len(hit), int(np.median(kp)), time.time() - t0))
    print("  bound coverage = %.3f  (median bound [%.3f, %.3f] vs truth %.3f ; median width %.3f logit)"
          % (e1, np.median(los), np.median(his), TH, np.median(wid)))
    v["E1"] = e1 >= 0.90
    print("  E1 %s   (criterion: coverage >= 0.90)" % ("PASS" if v["E1"] else "FAIL"))

    print("=" * 78)
    print("E2  BOUND WIDTH at k_published ~ 24 (60 reps, seed 4242+30, modelled selection)")
    print("    W18 one-channel result at this exact setting: median width 0.509 logit")
    rng = np.random.default_rng(4242 + 30)
    hit2, w2, lo2, hi2, kp2 = [], [], [], [], []
    t0 = time.time()
    for rep in range(60):
        y, s, ti, e, n = w18.simulate_conducted(rng, 30, TH, TAU)
        g0, g1 = w18.gammas_from_publication_probs(s, 0.99, 0.3)
        sel = w18.select_copas(rng, y, s, ti, g0, g1, 0.7)
        if sel.sum() < 3:
            continue
        rows = tc.sensitivity_surface2(y[sel], s[sel], seed=rep)
        lo, hi = tc.honest_bound(rows)
        hit2.append(lo <= TH <= hi); w2.append(hi - lo); lo2.append(lo); hi2.append(hi)
        kp2.append(int(sel.sum()))
    mw = float(np.median(w2))
    print("  replicates %d ; median k_pub %d ; elapsed %.1fs" % (len(hit2), int(np.median(kp2)), time.time() - t0))
    print("  median bound width = %.3f logit ; bound coverage %.3f ; median bound [%.3f, %.3f]"
          % (mw, np.mean(hit2), np.median(lo2), np.median(hi2)))
    print("  on the proportion scale the median bound is [%.3f, %.3f]"
          % (ex(np.median(lo2)), ex(np.median(hi2))))
    v["E2"] = mw <= 0.70
    print("  E2 %s   (criterion: median width <= 0.70 logit)" % ("PASS" if v["E2"] else "FAIL"))

    print("=" * 78); print("SUMMARY")
    for k in ("E0", "E1", "E2"):
        print("  %-3s %s" % (k, "PASS" if v[k] else "FAIL"))
    ok = all(v.values())
    print("OVERALL: %s" % ("ALL PRE-SPECIFIED CRITERIA MET" if ok
                           else "NOT ALL CRITERIA MET -- criteria were NOT relaxed"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

`repro_d0.py` (the reconstruction, so the caveat is checkable) is at `/tmp/claude-0/w18b/repro_d0.py`; it is 40 lines and is the only script here not derived from code W18 published.

---

## Limitations

1. **`NOT APPLIED TO REAL DATA.`** Every number is synthetic. No EMC quantity is estimated. No case added to any denominator.
2. **The extension FAILS its pre-specified acceptance criterion** on E2 (1.033 vs ≤0.70 logit). It is not accepted. I did not move the line, in either direction, and the criterion was written into both new files' docstrings before the first run.
3. **W18's own F1 failure persists**, reproduced exactly at +0.0521 vs <0.05. The extension does not address it and does not claim to.
4. **λ is gridded, not identified.** Everything W18 said about ρ's unidentifiability applies to λ with equal force and is untested here — I ran no D0-analogue for λ. Its non-identifiability is asserted by argument, not measured. `UNKNOWN`.
5. **Grid dependence, now worse.** The bound is a union over a grid I chose (λ ≤ 6). A wider λ grid gives a wider bound, without limit. The grid is an assumption, stated, not derived — and with three axes the arbitrariness compounds.
6. **The λ=6 grid endpoint was chosen to contain W18's κ=6 falsification DGP.** That makes E1 a fair test of *whether the extension can represent the channel*, but it is not a test of performance when the truth lies outside the grid. A κ=12 truth against a λ≤6 grid was not run. `UNKNOWN`.
7. **A third channel is not excluded.** Nothing here shows the two-channel family is complete. It repairs the one violation W18 exhibited; another unmodelled channel would break it the same way, and the same F2-style probe would be needed to find it.
8. **Assumptions A3–A6 are untouched** — normality on the logit scale at small denominators, independence (the registry marks 8 of 14 cohorts `pool:false` for population overlap), known within-study SE, follow-up heterogeneity in a time-to-event outcome analysed as a proportion, and the coherence of "conducted but unpublished EMC series". The extension addresses A1/A2 only.
9. **D0 is not bit-reproducible** because W18 did not return its script or seed. Reconstructed statistics agree to within sampling noise and the conclusion is unchanged, but I cannot certify it. This is a **reporting gap in W18** worth fixing if any of this is integrated.
10. **The Copas & Shi (2000) citation remains unretrieved and unverified**, per dispatch. My derivation is self-contained algebra and does not depend on it, but the attribution does.
11. **scipy is not a pinned repository dependency** — installed this session. If this integrates, it must be declared and pinned. The new module adds no dependency beyond W18's.
12. **A registry read was blocked** by the auto-mode classifier and not routed around; W18's 3-of-14 cohort figure is cited, not re-verified by me.
13. **Transfer limit.** This is a statistical method with simulation validation. **It establishes something about the estimator and about nothing else** — no EMC biology, no treatment effect, no association, no clinical efficacy, safety, selectivity or readiness. It is not a proposed clinical paper.

---

## Stop condition

**Set by dispatch:** W18's four runs reproduced or a discrepancy diagnosed; the two-channel extension implemented and run against the κ=6 regime with the pre-specified criterion; a definite pass/fail with real exit codes and the k=24 bound width reported.

**MET.** All four W18 runs reproduced — eight exactly (digit-for-digit, including the harness's exit 1) and D0 to within sampling noise with the reason diagnosed (W18 did not publish that script). The two-channel extension is implemented, proven to contain W18's model exactly at λ=0 (2.842e-14), and run against the κ=6 regime. **Definite verdict: FAIL** — E0 PASS, E1 PASS (0.971 ≥ 0.90), **E2 FAIL (1.033 > 0.70)**, harness exit code **1**. The k=24 median bound width is **1.033 logit**, up from W18's 0.509. Criteria were not relaxed.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 31** (28 Bash, 1 ToolSearch, 2 blocked before execution — a `&`-detach hook block and one classifier denial). Target ~40 — under.
- **Wall clock: 02:38:25Z → 03:07:10Z ≈ 29 minutes.** Target ~40 — under. The three concurrent simulation jobs dominated (validation 12.6 min; acceptance test 21.5 min across E1+E2).
- No network requests, no paid API, no GPU, no repository writes, no git operations, no external contact, no publication. **No content-policy refusal was encountered.** One classifier permission denial, recorded verbatim in Prior-work check, not routed around.

---

## Next concrete action

**One successor task, inside this lane — and it is a narrowing task, not another extension.** E1 and E2 are driven by the *same* λ>0 cells: the coverage repair and the width blowout are both entirely in the lower bound edge (−0.734→−1.044 at κ=6; −0.975→−1.511 at k=24; upper edge unmoved in both). So the question is whether the λ axis can be **restricted by evidence rather than by choice**. Concretely: test whether a likelihood-ratio screen across λ cells — dropping cells whose maximised conditional log-likelihood falls more than a pre-specified margin below the best cell, rather than unioning all 24 — recovers E2 (median k=24 width ≤ 0.70 logit) while holding E1 (κ=6 coverage ≥ 0.90). Pre-specify the LR margin before running; both thresholds already exist and must not move. This is bounded, needs no data, and reuses the harness unchanged.

**Honest caveat on that successor:** it may well fail, and for a principled reason — W18's D0 result implies the likelihood cannot distinguish selection strengths at EMC scale, which is exactly what such a screen would need it to do. If it fails, the correct conclusion for this lane is that **the A2 channel can be modelled but not bounded usefully at EMC sample sizes**, and that conclusion should be written down rather than attacked with a fourth variant.

**What I would not do next:** apply either estimator to the registry. The two-channel bound is wider than the one-channel bound at every k, and the one-channel bound at k=3 already spans 0.204–0.460.
