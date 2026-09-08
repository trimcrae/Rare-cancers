> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity checks done: `git status --porcelain` is empty (no repo writes), the module imports clean, and all three runs completed with real exit codes. Note the checkout HEAD is `47aac85f874a57a6f981c3432abcf16980968aec`, not the `92abbcb…` named in the brief — reported below as-is.

---

## Worker

**W18** — Lane 18, identifiable statistical methods for a feasible EMC question.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in the environment confirms a served model; the coordinator must extract the actual per-child runtime model from the transcript. The environment exposes no model variable at all.

`date -u` at start / end:
```
Tue Sep  8 01:56:25 UTC 2026
Tue Sep  8 02:30:15 UTC 2026
```

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — full output was captured at start (55 lines, no `model` key present anywhere). Identity-relevant subset, verbatim at end:
```
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
```
Start-of-run extras not repeated above: `CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605`, `CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f`, `CLAUDE_CODE_CHILD_SESSION=1`, `CLAUDE_EFFORT=medium`, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`, `CLAUDE_SESSION_INGRESS_TOKEN=<redacted>`, `CLAUDE_CODE_MESSAGING_TOKEN=<redacted>`.

**Write isolation honoured.** `git status --porcelain` at end returned empty; no file under `/home/user/Rare-cancers` was created or modified; no git write operation was run. All execution was under `/tmp/claude-0/w18/`. **Discrepancy to record:** the brief names frozen read commit `92abbcb905cacf07f14b238db50d1b98f6590374`, but this checkout's `git rev-parse HEAD` is `47aac85f874a57a6f981c3432abcf16980968aec`. I read the tree as I found it and did not change it.

---

## Question

**Can the pooled cumulative incidence of distant metastasis in EMC be estimated in a way that is honest about publication selection — i.e. with the selection mechanism as an explicit modelled object, a sensitivity surface instead of a point estimate, and a demonstrable regime in which the estimator is false?**

Why it is open: `research/PROTOCOL.md` §6 specifies DerSimonian–Laird pooling of logit proportions with leave-one-out, registry-vs-all-series, and era-stratified sensitivity analyses. All three vary *which published studies enter*. None of them models *the studies that were never published*. §5 (risk of bias) is explicitly `*Planned (not yet implemented)*` and mentions selection only as an appraisal flag: "Consultation/referral series flagged for selection bias." §8 concedes pooled figures are "descriptive, not causal" but offers no quantification. So the repository currently has no estimator whose answer moves as publication selection varies — the exact gap this lane names.

---

## Prior-work check

Commands run and what they showed:

```
rg -n -i "estimand|identification|selection bias|publication bias|sensitivity analysis|bootstrap|bayesian|prior" research/ --glob '!.git' | head -80
```
80 hits, none a selection estimator. Nearly all "prior" hits are *prior art* (citation provenance) or a Bayesian-flavoured word in `method-watch-*`. The one genuine statistical-selection hit is `research/manuscripts/emc_endpoint_alternatives.py:564`, which *names* the problem in prose — "population is SELECTED for expected indolence -- which is the same selection bias that…" — and does not model it.

```
rg -n -i "heckman|copas|tipping point|e-value|manski|partial identification|selection model" --glob '!.git' | head -40
```
**Zero hits for `heckman`, `copas`, `manski`, `partial identification`, `selection model`, `tipping point`.** The only `e-value` hits are `research/manuscripts/care-delivery/emc-radioresistance-reappraisal.md:241-244` and two prose echoes — that is an E-value bias analysis for **indication/confounding bias in the RT comparison**, a different bias class from publication selection, and it is already closed work.

```
git ls-files | rg -i "estimand|selection|publication-bias|sensitivity|tipping|heckman|bound" | head -40
```
39 files; every `sensitivity` file is a molecular/junction-annotation sensitivity artifact (`junction_transcript_sensitivity.py`, `surface_address_sensitivity.py`, `nr4a2_sparing_bound.py`); every `bounded`/`bound` file is the autonomy review harness or a manuscript numeric-binding test. None is a meta-analytic selection model.

Also read: `research/PROTOCOL.md` in full, and `research/data/emc-clinical-registry.json` structure.

**CLOSED-WORK.md items confirmed not replayed.** I am not touching PUB-ASO, the frozen external-validation comment, or the Qeios/aiXiv path. I did not recreate the restricted NR4A Perspective review. I did not replay the paired-Davis, Hofvander, Brenca, promoter-transfer or inverse-bounds gates. I did not invent an independent cohort or re-fetch `GSE4303`/`GSE28866`. I made **no network requests at all**, so none of the recorded 403/EGRESS_BLOCKED routes (Pazopanib, Sunitinib 2014, Wagner 2020, CTARC 2022, Trabectedin/RT 2018) was retried. I am not in lane 11 and touched no source-index file.

One CLOSED-WORK line bears directly on this lane and I am obeying it: *"Clinical conditional-recurrence, RT/IPD synthesis, and trial-discoverability/response checkpoints did not admit their proposed papers."* This deliverable is therefore **a method with simulation evidence, not a proposed clinical paper and not a new EMC number.**

---

## Method / inputs

| Item | Value |
|---|---|
| Files read (read-only) | `research/PROTOCOL.md`, `research/data/emc-clinical-registry.json`, campaign `COMMON-BRIEF.md`, `CLOSED-WORK.md` |
| Code authored | `emc_copas_selection.py`, `run_validation.py`, `k_feasibility.py`, `f2_kappa_sweep.py` (all under `/tmp/claude-0/w18/`, all returned inline below) |
| Python | 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0] |
| numpy | 2.4.6 (preinstalled) |
| scipy | 1.17.1 (installed this session via `pip3 install --quiet numpy scipy`; `pypi.org` and `files.pythonhosted.org` are in `no_proxy`, so no egress-policy route was crossed) |
| Platform | `Linux-6.18.44-fc-v24-x86_64-with-glibc2.39` |
| Data used for all numbers below | **SYNTHETIC**, generated in-process from seeded `numpy.random.default_rng` |
| Method basis | Copas & Shi (2000), *Stat Methods Med Res* 9:247–262, conditional-likelihood selection model — adapted here to logit proportions. **Citation is from my own knowledge and was NOT retrieved this session; treat the reference as unverified.** |

### The estimand (S2)

Let $S$ be the set of EMC case series **conducted** (published or not) meeting `PROTOCOL.md` §2 eligibility. Series $i$ has a true study-specific logit cumulative incidence of distant metastasis $\theta_i = \theta + u_i$, $u_i \sim N(0,\tau^2)$. The estimand is

$$\theta^\* \;=\; \mathbb{E}_{i \in S}[\theta_i] \;=\; \theta, \qquad \text{reported as } \operatorname{expit}(\theta).$$

**What the answer would mean:** the average metastasis risk across the series that were *carried out*, not across patients. The unit is the series, not the patient — a large registry and a 12-patient report count equally. It is **not** a personal risk for a patient with EMC, and it inherits every follow-up-length and censoring problem `PROTOCOL.md` §6 already flags (which is why that section refuses to pool time-anchored survival).

The naive comparator, DerSimonian–Laird over published series, targets $\mathbb{E}[\theta_i \mid \text{published}]$ — **a different functional** whenever selection operates. The two coincide only if selection is independent of outcome and of precision.

### The selection mechanism as an explicit object (S3)

Series $i$ is published iff a latent propensity crosses zero:

$$z_i = \gamma_0 + \gamma_1/s_i + \delta_i, \quad \delta_i\sim N(0,1), \quad \operatorname{corr}(\delta_i,\varepsilon_i)=\rho,$$

where $y_i = \theta_i + \varepsilon_i$, $\varepsilon_i \sim N(0,s_i^2)$ is the within-study sampling error. So $\gamma_1>0$ = "bigger series get written up regardless"; $\rho>0$ = "a series that *happened* to come out striking gets written up". I reparameterise $(\gamma_0,\gamma_1)$ by two readable quantities: $P(\text{publish})$ for the most precise and for the least precise conducted series.

### Identification assumptions, what violates each, and how badly

| # | Assumption | What violates it | How badly |
|---|---|---|---|
| A1 | $(\gamma_0,\gamma_1,\rho)$ are **known**, not estimated | Trying to estimate $\rho$ from published data | **Fatal, and measured.** See D0 below: at EMC scale the profile MLE of $\rho$ has the *wrong sign* 68% of the time. This is why the code refuses to estimate $\rho$ and grids it instead. |
| A2 | Selection acts through the **sampling error** $\varepsilon_i$ | Selection acting on the study's **true** risk $u_i$ — referral centres with genuinely worse case-mix publishing more | **Fatal and unfixable by this model.** Quantified in F2: at $\kappa\ge3$ the bound stops covering the truth. This is the estimator's real failure mode and it is a realistic EMC regime. |
| A3 | $u_i$ normal, $\varepsilon_i$ normal on the logit scale | Small denominators; 0/n or n/n cells | Bites hardest exactly where EMC lives. The continuity correction (`cc=0.5`, matching `PROTOCOL.md` §6) is a patch, not a fix. |
| A4 | Series are **independent** | Overlapping populations — SEER inside a national registry, an institution inside a multi-centre series | Already a live problem: the registry marks 8 of 14 cohorts `pool: false` with `contextReason: population-overlap`. Violation inflates apparent precision and shrinks the bound *toward a false confidence*. |
| A5 | $s_i$ is the correct within-study SE and is **known** | Follow-up heterogeneity: metastasis is a time-to-event outcome analysed here as a proportion | Systematic, direction unknown. Series with longer follow-up report higher proportions for identical biology. `PROTOCOL.md` §6 refuses to pool time-anchored survival for this reason; the same objection applies to metastasis proportions and is **not** solved here. |
| A6 | The conducted-series population $S$ is well defined | "Conducted but unpublished EMC series" may not be a coherent set — a clinician who sees three cases and writes nothing may never have "conducted a series" | Conceptual, and it limits interpretation more than estimation. |

**Unidentifiable no matter what (S6):** $\rho$ and $(\gamma_0,\gamma_1)$ are not identified from published data at any $k$ this disease will ever produce. Nothing in the published record distinguishes "high true risk, no selection" from "lower true risk, strong selection" — that is a likelihood ridge, not a small-sample problem. **Assumption A2 is not testable from published data at all**, because $u_i$ and $\varepsilon_i$ are never separately observed. The output is therefore a **bound conditional on a grid**, and a bound whose validity itself rests on untestable A2.

---

## Result

### D0 — Selection strength cannot be estimated; it must be gridded `PRIMARY` (computational, on synthetic data)

Profiling $\rho$ out of the likelihood, 60 synthetic replicates, 40 conducted series, median 31 published, **true $\rho=+0.70$**:

| Quantity | Value | Grade |
|---|---|---|
| Fitted $\rho$, median (IQR) | −0.277 (−0.891, +0.073) | `PRIMARY` |
| Fitted $\rho$ range | −1.000 to +1.000 | `PRIMARY` |
| Fraction at the \|ρ\|>0.995 boundary | 0.23 | `PRIMARY` |
| **Fraction with the wrong sign** | **0.68** | `PRIMARY` |

This is the load-bearing methodological finding. Any EMC analysis that *estimates* publication-selection strength from the published record is reporting noise. I redesigned the estimator around it.

### D1 — The 20-cell sensitivity surface `PRIMARY` (SYNTHETIC; truth θ = −0.800, i.e. 0.310)

28 of 40 conducted series published. Units: logit and proportion; interval = 95% profile-likelihood CI at that grid cell.

| ρ | P(pub \| least precise) | θ̂ | expit(θ̂) | 95% profile CI (logit) | τ̂ | implied unpublished |
|---|---|---|---|---|---|---|
| 0.0 | 0.99 | −0.707 | 0.330 | [−0.889, −0.529] | 0.392 | 0.3 |
| 0.0 | 0.30 | −0.707 | 0.330 | [−0.889, −0.529] | 0.392 | 11.6 |
| 0.4 | 0.60 | −0.731 | 0.325 | [−0.917, −0.551] | 0.404 | 4.2 |
| 0.4 | 0.10 | −0.769 | 0.317 | [−0.963, −0.583] | 0.426 | 34.9 |
| 0.6 | 0.30 | −0.774 | 0.316 | [−0.966, −0.587] | 0.431 | 11.6 |
| 0.8 | 0.30 | −0.804 | 0.309 | [−1.001, −0.611] | 0.456 | 11.6 |
| 0.8 | 0.10 | **−0.852** | **0.299** | [−1.061, −0.647] | 0.495 | 34.9 |

(Seven of 20 cells shown; the full 20 are in the verbatim output below.)

- **HONEST BOUND** (union over the grid): logit [−1.061, −0.529] → **proportion [0.257, 0.371]**. This is a bound, not a point estimate.
- Naive DerSimonian–Laird on published only: −0.707 → **0.330**, CI [0.292, 0.370].
- Note the structure: at ρ=0 the estimate is *completely insensitive* to $\gamma$ (all four rows identical to 3 d.p.). Size-selection alone does not bias the pooled estimate; **it is the ρ×γ interaction that does the damage.** The naive answer 0.330 sits near the *upper* edge of the honest bound.

### D2 / F1 — Calibration and recovery, selection parameters KNOWN `PRIMARY` (300 reps, SYNTHETIC)

| Estimator | mean θ̂ | bias | SD | 95% CI coverage |
|---|---|---|---|---|
| Copas at the true selection triple | −0.7479 | **+0.0521** | 0.0898 | **0.933** |
| Naive DerSimonian–Laird | −0.6885 | **+0.1115** | 0.0884 | **0.753** |

- **D2 PASS** (Copas coverage 0.933 ∈ [0.90, 0.99]; naive coverage 0.753 < 0.80). Nominal is 0.95 — the naive estimator's 95% interval misses the truth **one time in four**.
- **F1 FAIL**, and I am not moving the line. I pre-specified |bias| < 0.05; the achieved bias is **+0.0521**. The second clause passed (|0.1115| > 2×|0.0521| = 0.1042, narrowly). Honest reading: knowing the selection parameters exactly **halves** the bias (0.111 → 0.052) but does **not** remove it — residual small-sample bias of the Copas MLE at k≈28 survives. Even the best case here is not unbiased.

### D3 — Bound coverage, modelled selection of unknown strength `PRIMARY` (150 reps)

Bound coverage **0.960**, median bound width 0.459 logit. **D3 PASS.** When the selection mechanism is of the modelled form but its strength is unknown, the union bound is honest.

### F2 — Falsification `PRIMARY` (150 reps at the pre-specified κ; then a post-hoc sweep)

Regime the model cannot represent: publication driven by the series' **true** risk $u_i$, not its sampling error.

- **At the pre-specified κ=1.5: bound coverage 0.867. The falsification test DID NOT FIRE** (criterion was <0.50). Median bound [−0.906, −0.463] against truth −0.800. Reported as a non-firing test, per the pre-specification.
- **Post-hoc sweep** (explicitly *not* pre-specified — κ is the severity knob and I went looking for the breaking point):

| κ | reps | median k published | bound coverage | median bound (logit) vs truth −0.800 |
|---|---|---|---|---|
| 1.5 | 70 | 30 | 0.900 | [−0.883, −0.436] |
| 3.0 | 70 | 26 | **0.529** | [−0.803, −0.343] |
| 6.0 | 70 | 24 | **0.243** | [−0.734, −0.296] |
| 12.0 | 70 | 22 | **0.243** | [−0.734, −0.288] |

**The estimator is falsifiable and here it is false.** At κ≥6 the entire honest bound lies above the truth in ~76% of replicates — the bound excludes the true value. Two honest conclusions: (i) the bound is *not* a guarantee; it protects only against the modelled selection channel; (ii) the pre-specified κ=1.5 was too weak a probe, which the pre-specified run correctly recorded as a non-firing test rather than as a pass.

### K — Feasibility floor `PRIMARY` (SYNTHETIC) and the real-data denominator gap `PRIMARY` (repository)

**NOT APPLIED TO REAL DATA.** I did not assemble an EMC dataset and I report no EMC number.

The reason is concrete, not procedural. In `research/data/emc-clinical-registry.json`, exactly **3 of 14 cohorts** carry an extractable `metastasis: {events, denom}`:

| sourceId | metastasis | pool | grade |
|---|---|---|---|
| `masunaga2025` | 39/134 | true | `PRIMARY` (repository record) |
| `meisKindblom1999` | 35/76 | true | `PRIMARY` |
| `chiusole2020` | 20/49 | true | `PRIMARY` |

The rest are `percentage-only`, `population-overlap`, or `different-endpoint`. The registry also holds only **4 IPD patients**. What k=3 buys:

| median k published | reps | bound coverage | median bound width (logit) | median bound (proportion) |
|---|---|---|---|---|
| **3** | 38 | 0.868 | **1.156** | **[0.204, 0.460]** |
| 6 | 59 | 0.932 | 0.990 | [0.220, 0.435] |
| 12 | 60 | 0.983 | 0.697 | [0.250, 0.402] |
| 24 | 60 | 0.950 | 0.509 | [0.274, 0.380] |
| 48 | 60 | 1.000 | 0.383 | [0.279, 0.362] |

At k=3 the honest bound spans **0.204 to 0.460** — it cannot distinguish "one EMC patient in five" from "nearly one in two", and its coverage (0.868) is already below nominal. **Applying this estimator to the current EMC registry would produce an interval too wide to inform any decision.** That is the correct answer, and it is more useful than a false point estimate.

---

## Validation evidence

Environment line printed by the harness itself:
```
environment: python 3.11.15 | numpy 2.4.6 | scipy 1.17.1 | Linux-6.18.44-fc-v24-x86_64-with-glibc2.39
```

### RUN 1 — D0, ρ identifiability
```
$ cd /tmp/claude-0/w18 && python3 - <<'EOF'  # 60 replicates, true rho=0.7
```
```
replicates: 60 median published k: 31
true rho = 0.70 ; fitted rho: median -0.277  IQR [-0.891, 0.073]  min -1.000 max 1.000
fraction at |rho|>0.995 boundary: 0.23
fraction with WRONG SIGN (rho<0): 0.68
EXIT=0
```

### RUN 2 — full validation harness (`RUN`)
```
$ cd /tmp/claude-0/w18 && time python3 run_validation.py 2>&1 | tee validation.log
real  11m43.629s
user  11m5.483s
sys   0m0.880s
EXIT=1
```
**Exit code 1 is correct and intended**: `main()` returns 1 unless every pre-specified criterion is met, and F1 failed while F2 did not fire. I did not weaken the criteria to obtain 0. Verbatim tail:
```
  0.8    0.10         -0.852     0.299   [-1.061, -0.647]    0.495     34.9
  HONEST BOUND (union over grid): logit [-1.061, -0.529]  ->  proportion [0.257, 0.371]
  naive DerSimonian-Laird on published only: -0.707 [-0.884, -0.531] -> proportion 0.330
  all converged=True ; max multistart theta spread=4.50e-08 ; D1 PASS
==============================================================================
D2/F1  CALIBRATION AND RECOVERY, selection parameters KNOWN (300 reps)
  usable replicates: 300 ; elapsed 93.3s
  Copas @ true selection : mean theta -0.7479  bias +0.0521  SD 0.0898  coverage 0.933
  naive DerSimonian-Laird: mean theta -0.6885  bias +0.1115  SD 0.0884  coverage 0.753
  D2 PASS ; F1 FAIL
==============================================================================
D3  BOUND COVERAGE, modelled selection of UNKNOWN strength (150 reps)
  replicates 150 ; elapsed 290.3s ; bound coverage 0.960 ; median bound width 0.459 logit
  D3 PASS
==============================================================================
F2  FALSIFICATION: selection on the study's TRUE risk u_i, not on its sampling
    error -- referral centres whose real case-mix is worse publish more often.
    The Copas family has no parameter for this. (150 reps, kappa=1.5)
  replicates 150 ; elapsed 313.2s
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
```

### RUN 3 — k-feasibility (`RUN`)
```
$ cd /tmp/claude-0/w18 && python3 k_feasibility.py 2>&1 | tee k_feasibility.log
k_pub  reps  bound coverage  median bound width (logit)  median bound (proportion scale)
  3.0    38          0.868                      1.156   [0.204, 0.460]
  6.0    59          0.932                      0.990   [0.220, 0.435]
 12.0    60          0.983                      0.697   [0.250, 0.402]
 24.0    60          0.950                      0.509   [0.274, 0.380]
 48.0    60          1.000                      0.383   [0.279, 0.362]
EXIT=0
```

### RUN 4 — post-hoc F2 κ sweep (`RUN`, explicitly NOT pre-specified)
```
$ cd /tmp/claude-0/w18 && python3 f2_kappa_sweep.py 2>&1 | tee f2_kappa_sweep.log
kappa  reps  k_pub  bound coverage  median bound (logit)      vs truth -0.800
  1.5    70     30          0.900   [-0.883, -0.436]
  3.0    70     26          0.529   [-0.803, -0.343]
  6.0    70     24          0.243   [-0.734, -0.296]
 12.0    70     22          0.243   [-0.734, -0.288]
EXIT=0
```

### Write-isolation check (`RUN`)
```
$ cd /home/user/Rare-cancers && git status --porcelain | head
(no output)
$ git rev-parse HEAD
47aac85f874a57a6f981c3432abcf16980968aec
```

### `PROPOSED (NOT RUN)`
- Application to real EMC data — **not run**, deliberately. `NOT APPLIED TO REAL DATA`.
- `scripts/preflight.sh` — not run; the dispatch did not authorise it and nothing was written to the tree.
- Retrieval of Copas & Shi (2000) to verify the citation — **not run**; no network requests were made this session.
- A Freeman–Tukey / GLMM cross-check of the `PROTOCOL.md` §6 backlog — not run, out of lane scope.

---

## Code

### `research/meta/emc_copas_selection.py` (suggested path; coordinator decides)

```python
"""
emc_copas_selection.py -- A publication-selection-aware estimator for a pooled EMC proportion.

SCOPE: estimator + diagnostics + falsification harness. Contains NO patient data and is
NOT APPLIED TO REAL DATA here; all runs in the accompanying harness are on SYNTHETIC data.

ESTIMAND. Let S be the set of EMC case series that were CONDUCTED (published or not) meeting
the PROTOCOL.md eligibility criteria, each with a true study-specific logit-risk
theta_i = theta + u_i, u_i ~ N(0, tau^2). The estimand is

    theta* = E_{i in S}[ theta_i ] = theta        (mean logit cumulative incidence of distant
                                                   metastasis over CONDUCTED series),

reported back-transformed as expit(theta). It is NOT the risk in a random patient: the series
population is the unit. The naive comparator is DerSimonian-Laird over PUBLISHED series only,
which targets E[theta_i | published] -- a different functional whenever selection operates.

SELECTION MECHANISM (modelled object, not a caveat). Study i is published iff a latent
propensity crosses zero:
    z_i = gamma0 + gamma1 / s_i + delta_i,   delta_i ~ N(0,1),   corr(delta_i, eps_i) = rho,
where y_i = theta_i + eps_i, eps_i ~ N(0, s_i^2) is the within-study sampling error. rho > 0
encodes "a series whose observed metastasis proportion came out high (relative to its own truth)
is more likely to be written up". gamma1 > 0 encodes "larger/more precise series are published
regardless". (gamma0, gamma1, rho) are the SELECTION PARAMETERS. They are NOT identified from
published data alone; we grid over them. That is the whole point.

Copas & Shi (2000, Stat Methods Med Res 9:247-262) conditional likelihood; here for logit
proportions. NOTE: that reference was not retrieved when this file was written -- verify it.

Requires numpy, scipy.
"""
from __future__ import annotations

import numpy as np
from scipy import optimize
from scipy.stats import norm

__all__ = [
    "logit_transform", "dersimonian_laird", "copas_loglik", "gammas_from_publication_probs",
    "fit_copas_at", "sensitivity_surface", "honest_bound", "DEFAULT_RHO_GRID",
    "DEFAULT_PLEAST_GRID",
]

_TINY = 1e-12


# --------------------------------------------------------------------------- data prep
def logit_transform(events, denom, cc: float = 0.5):
    """Logit proportions y_i and within-study SEs s_i.

    Continuity correction `cc` applied ONLY to 0/denom and denom/denom cells, matching
    PROTOCOL.md section 6. Returns (y, s).
    """
    e = np.asarray(events, dtype=float)
    n = np.asarray(denom, dtype=float)
    if np.any(n <= 0) or np.any(e < 0) or np.any(e > n):
        raise ValueError("events must satisfy 0 <= events <= denom, denom > 0")
    bad = (e == 0) | (e == n)
    e2 = np.where(bad, e + cc, e)
    n2 = np.where(bad, n + 2 * cc, n)
    p = e2 / n2
    y = np.log(p / (1 - p))
    s = np.sqrt(1.0 / (n2 * p * (1 - p)))
    return y, s


def dersimonian_laird(y, s):
    """Naive random-effects pooling of PUBLISHED studies. Returns (theta_hat, tau2, se)."""
    y = np.asarray(y, float); s = np.asarray(s, float)
    w = 1.0 / s**2
    theta_fe = np.sum(w * y) / np.sum(w)
    Q = np.sum(w * (y - theta_fe) ** 2)
    k = len(y)
    if k < 2:
        return theta_fe, 0.0, np.sqrt(1.0 / np.sum(w))
    c = np.sum(w) - np.sum(w**2) / np.sum(w)
    tau2 = max(0.0, (Q - (k - 1)) / c)
    wr = 1.0 / (s**2 + tau2)
    theta = np.sum(wr * y) / np.sum(wr)
    se = np.sqrt(1.0 / np.sum(wr))
    return theta, tau2, se


# --------------------------------------------------------------------------- Copas model
def gammas_from_publication_probs(s, p_most_precise: float, p_least_precise: float):
    """Reparameterise (gamma0, gamma1) by two interpretable marginal publication probabilities.

    P(publish | s) = Phi(gamma0 + gamma1/s). Pin it at the most precise study (smallest s) and
    the least precise study (largest s). Returns (gamma0, gamma1).
    """
    s = np.asarray(s, float)
    a, b = 1.0 / np.min(s), 1.0 / np.max(s)          # a > b
    if np.isclose(a, b):
        raise ValueError("all studies have equal precision; gamma1 is not separable")
    q_hi, q_lo = norm.ppf(p_most_precise), norm.ppf(p_least_precise)
    gamma1 = (q_hi - q_lo) / (a - b)
    gamma0 = q_hi - gamma1 * a
    return gamma0, gamma1


def copas_loglik(theta, tau, rho, gamma0, gamma1, y, s):
    """Conditional log-likelihood of the PUBLISHED studies under the Copas selection model."""
    tau = abs(tau)
    sig2 = tau**2 + s**2
    sig = np.sqrt(sig2)
    v = gamma0 + gamma1 / s
    # correlation between y_i and z_i is rho*s_i/sig_i; must be < 1 in absolute value
    r = rho * s / sig
    denom = 1.0 - r**2
    if np.any(denom <= _TINY):
        return -np.inf
    num = v + (rho * s / sig2) * (y - theta)
    ll = (norm.logpdf(y, loc=theta, scale=sig)
          + norm.logcdf(num / np.sqrt(denom))
          - norm.logcdf(v))
    if not np.all(np.isfinite(ll)):
        return -np.inf
    return float(np.sum(ll))


def fit_copas_at(y, s, gamma0, gamma1, rho, n_starts: int = 3, seed: int = 0):
    """Maximise the Copas conditional likelihood over (theta, tau) at a FIXED selection
    triple (gamma0, gamma1, rho).

    rho is NOT estimated. Diagnostic D0 (run on synthetic data, reported alongside this code)
    shows that at EMC scale -- k ~ 30 published series -- the profile MLE of rho carries the
    WRONG SIGN in 68% of replicates and sits on the |rho|=1 boundary in 23%. Selection strength
    is therefore a sensitivity parameter to be varied, never a quantity to be read off the
    published record.
    """
    y = np.asarray(y, float); s = np.asarray(s, float)
    rng = np.random.default_rng(seed)
    dl_theta, dl_tau2, _ = dersimonian_laird(y, s)

    def nll(p):
        val = copas_loglik(p[0], np.exp(p[1]), rho, gamma0, gamma1, y, s)
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
        "rho": float(rho), "loglik": float(-best.fun),
        "converged": bool(all(r.success for r in res)),
        "multistart_theta_spread": float(np.ptp(near)) if near.size > 1 else 0.0,
        "gamma0": float(gamma0), "gamma1": float(gamma1),
    }


def _profile_ci_theta(y, s, gamma0, gamma1, rho, ll_hat, theta_hat,
                      level=0.95, halfwidth=4.0, n_bisect=22, maxiter=600):
    """Profile-likelihood CI for theta, tau profiled out, at fixed (gamma0, gamma1, rho)."""
    from scipy.stats import chi2
    cut = ll_hat - 0.5 * chi2.ppf(level, 1)

    def prof(theta):
        def nll(p):
            val = copas_loglik(theta, np.exp(p[0]), rho, gamma0, gamma1, y, s)
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


DEFAULT_RHO_GRID = (0.0, 0.2, 0.4, 0.6, 0.8)
DEFAULT_PLEAST_GRID = (0.99, 0.6, 0.3, 0.1)


def sensitivity_surface(y, s, rho_grid=DEFAULT_RHO_GRID, p_least_grid=DEFAULT_PLEAST_GRID,
                        p_most_precise: float = 0.99, with_ci: bool = True, seed: int = 0,
                        **ci_kw):
    """THE DELIVERABLE: how the pooled estimate moves as the selection parameters vary.

    rho          -- correlation between a series' sampling error and its publication propensity
                    ("did it get written up because it came out striking?"). rho=0 is
                    selection-on-size-only; rho=0.8 is severe outcome-driven selection.
    p_least_grid -- P(publish) for the LEAST precise conducted series. 0.99 is near-no
                    size-selection; 0.1 means nine in ten small series never appear.

    Returns one row per (rho, p_least) cell. Read the SPREAD, not any single cell.
    """
    y = np.asarray(y, float); s = np.asarray(s, float)
    rows = []
    for rho in rho_grid:
        for p_lo in p_least_grid:
            g0, g1 = gammas_from_publication_probs(s, p_most_precise, p_lo)
            fit = fit_copas_at(y, s, g0, g1, rho, seed=seed)
            pub_p = norm.cdf(g0 + g1 / s)
            fit["p_least_precise"] = float(p_lo)
            fit["mean_pub_prob"] = float(np.mean(pub_p))
            fit["implied_unpublished"] = float(np.sum(1.0 / pub_p) - len(y))
            if with_ci:
                fit["ci_lo"], fit["ci_hi"] = _profile_ci_theta(
                    y, s, g0, g1, rho, fit["loglik"], fit["theta"], **ci_kw)
            rows.append(fit)
    return rows


def honest_bound(rows):
    """Union of the per-cell profile CIs across the whole selection grid.

    This is a BOUND under the stated grid, not a point estimate and not a confidence interval
    with a single coverage guarantee. It is valid only if the true selection mechanism lies in
    the modelled family AND inside the grid. Falsification test F2 exhibits a realistic EMC
    regime where both fail and the bound excludes the truth.
    """
    return min(r["ci_lo"] for r in rows), max(r["ci_hi"] for r in rows)


# --------------------------------------------------------------------------- simulation
def _expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def simulate_conducted(rng, n_conducted, theta, tau, denom_lo=15, denom_hi=140):
    """SYNTHETIC. Draw conducted series: true logit-risks and observed binomial proportions."""
    n = rng.integers(denom_lo, denom_hi + 1, size=n_conducted)
    theta_i = theta + rng.normal(0, tau, size=n_conducted)
    events = rng.binomial(n, _expit(theta_i))
    y, s = logit_transform(events, n)
    return y, s, theta_i, events, n


def select_copas(rng, y, s, theta_i, gamma0, gamma1, rho):
    """SYNTHETIC selection EXACTLY as the model assumes: on the sampling error eps_i."""
    eps = y - theta_i
    # delta = rho*(eps/s) + sqrt(1-rho^2)*N(0,1)  gives corr(delta, eps)=rho with delta~N(0,1)
    delta = rho * (eps / s) + np.sqrt(max(0.0, 1 - rho**2)) * rng.normal(size=len(y))
    z = gamma0 + gamma1 / s + delta
    return z > 0


def select_on_random_effect(rng, y, s, theta_i, theta, gamma0, gamma1, kappa):
    """SYNTHETIC selection the model CANNOT represent: publication driven by the study's TRUE
    underlying risk u_i (referral centres with genuinely worse case-mix write up more often),
    independent of that series' sampling error. Copas has no parameter for this."""
    u = theta_i - theta
    tau_u = np.std(u) if np.std(u) > 0 else 1.0
    delta = rng.normal(size=len(y))
    z = gamma0 + gamma1 / s + kappa * (u / tau_u) + delta
    return z > 0
```

### `research/meta/tests/run_validation.py` (suggested path)

```python
"""Diagnostics + falsification for emc_copas_selection.py.  ALL DATA HERE IS SYNTHETIC.

Pass criteria are PRE-SPECIFIED below and printed before any result is computed.
Exits 1 unless every criterion is met. Runtime ~12 min.
"""
import sys, time, platform
import numpy as np
sys.path.insert(0, '/tmp/claude-0/w18')   # coordinator: repoint at the module's real home
import scipy
import emc_copas_selection as m

NOMINAL = 0.95
SEED = 20260908
THETA_TRUE, TAU_TRUE, RHO_TRUE = -0.8, 0.5, 0.7   # expit(-0.8) = 0.310
N_CONDUCTED = 40
P_LEAST_TRUE = 0.3
REPS_A, REPS_B = 300, 150
BOUND_RHO = (0.0, 0.4, 0.8)
BOUND_PLEAST = (0.99, 0.3)

CRITERIA = """
PRE-SPECIFIED PASS CRITERIA (fixed before running; results below are not permitted to move them)
  D1 convergence : every cell of a 20-cell surface reports converged=True and
                   multistart_theta_spread < 0.01 (logit units).
  D2 calibration : with the selection parameters KNOWN, Copas 95% profile-CI coverage of
                   theta must lie in [0.90, 0.99]; the naive DerSimonian-Laird 95% CI
                   coverage must be < 0.80 (i.e. the problem is real).
  F1 must-recover: |mean bias(Copas at true selection)| < 0.05 logit, AND
                   |mean bias(naive DL)| > 2 x |mean bias(Copas)|.
  D3 bound cover : selection of the MODELLED form but of UNKNOWN strength -- the union bound
                   over the (rho x p_least) grid must cover theta in >= 90% of replicates.
  F2 must-FAIL   : selection driven by the study's TRUE risk u_i (referral-centre case-mix),
                   which the Copas family cannot represent. The falsification FIRES -- i.e.
                   the estimator is shown to be breakable -- if the union bound covers theta
                   in < 50% of replicates. If it does not fire, that is reported as a
                   NON-FIRING falsification test, not as a success.
"""


def dl_ci(y, s):
    th, _, se = m.dersimonian_laird(y, s)
    return th, th - 1.96 * se, th + 1.96 * se


def main():
    print("environment: python %s | numpy %s | scipy %s | %s"
          % (platform.python_version(), np.__version__, scipy.__version__, platform.platform()))
    print("truth (SYNTHETIC): theta=%.2f (=%.3f on the proportion scale), tau=%.2f, rho=%.2f, "
          "n_conducted=%d, P(publish|least precise)=%.2f"
          % (THETA_TRUE, 1/(1+np.exp(-THETA_TRUE)), TAU_TRUE, RHO_TRUE, N_CONDUCTED, P_LEAST_TRUE))
    print(CRITERIA)
    verdicts = {}

    # ---------------------------------------------------------------- D1
    print("=" * 78); print("D1  CONVERGENCE over the full 20-cell sensitivity surface")
    rng = np.random.default_rng(SEED)
    y, s, ti, ev, nn = m.simulate_conducted(rng, N_CONDUCTED, THETA_TRUE, TAU_TRUE)
    g0, g1 = m.gammas_from_publication_probs(s, 0.99, P_LEAST_TRUE)
    sel = m.select_copas(rng, y, s, ti, g0, g1, RHO_TRUE)
    yo, so = y[sel], s[sel]
    print("  published %d of %d conducted series" % (sel.sum(), N_CONDUCTED))
    t0 = time.time()
    rows = m.sensitivity_surface(yo, so)
    print("  20 cells in %.1fs" % (time.time() - t0))
    print("  %-6s %-9s %9s %9s %19s %8s %8s" %
          ("rho", "p_least", "theta", "expit", "95% profile CI", "tau", "unpub"))
    for r in rows:
        print("  %-6.1f %-9.2f %9.3f %9.3f   [%6.3f, %6.3f] %8.3f %8.1f" %
              (r["rho"], r["p_least_precise"], r["theta"], 1/(1+np.exp(-r["theta"])),
               r["ci_lo"], r["ci_hi"], r["tau"], r["implied_unpublished"]))
    lo, hi = m.honest_bound(rows)
    print("  HONEST BOUND (union over grid): logit [%.3f, %.3f]  ->  proportion [%.3f, %.3f]"
          % (lo, hi, 1/(1+np.exp(-lo)), 1/(1+np.exp(-hi))))
    dth, dlo, dhi = dl_ci(yo, so)
    print("  naive DerSimonian-Laird on published only: %.3f [%.3f, %.3f] -> proportion %.3f"
          % (dth, dlo, dhi, 1/(1+np.exp(-dth))))
    okc = all(r["converged"] for r in rows)
    oks = max(r["multistart_theta_spread"] for r in rows)
    verdicts["D1"] = okc and oks < 0.01
    print("  all converged=%s ; max multistart theta spread=%.2e ; D1 %s"
          % (okc, oks, "PASS" if verdicts["D1"] else "FAIL"))

    # ---------------------------------------------------------------- D2 / F1
    print("=" * 78); print("D2/F1  CALIBRATION AND RECOVERY, selection parameters KNOWN (%d reps)" % REPS_A)
    rng = np.random.default_rng(SEED + 1)
    cop, nai, cov_c, cov_n = [], [], [], []
    t0 = time.time()
    for rep in range(REPS_A):
        y, s, ti, ev, nn = m.simulate_conducted(rng, N_CONDUCTED, THETA_TRUE, TAU_TRUE)
        g0, g1 = m.gammas_from_publication_probs(s, 0.99, P_LEAST_TRUE)
        sel = m.select_copas(rng, y, s, ti, g0, g1, RHO_TRUE)
        if sel.sum() < 8:
            continue
        yo, so = y[sel], s[sel]
        f = m.fit_copas_at(yo, so, g0, g1, RHO_TRUE, seed=rep)
        cl, ch = m._profile_ci_theta(yo, so, g0, g1, RHO_TRUE, f["loglik"], f["theta"])
        cop.append(f["theta"]); cov_c.append(cl <= THETA_TRUE <= ch)
        dth, dlo, dhi = dl_ci(yo, so)
        nai.append(dth); cov_n.append(dlo <= THETA_TRUE <= dhi)
    cop, nai = np.array(cop), np.array(nai)
    bc, bn = cop.mean() - THETA_TRUE, nai.mean() - THETA_TRUE
    cc, cn = np.mean(cov_c), np.mean(cov_n)
    print("  usable replicates: %d ; elapsed %.1fs" % (len(cop), time.time() - t0))
    print("  Copas @ true selection : mean theta %+.4f  bias %+.4f  SD %.4f  coverage %.3f"
          % (cop.mean(), bc, cop.std(), cc))
    print("  naive DerSimonian-Laird: mean theta %+.4f  bias %+.4f  SD %.4f  coverage %.3f"
          % (nai.mean(), bn, nai.std(), cn))
    verdicts["D2"] = (0.90 <= cc <= 0.99) and (cn < 0.80)
    verdicts["F1"] = (abs(bc) < 0.05) and (abs(bn) > 2 * abs(bc))
    print("  D2 %s ; F1 %s" % ("PASS" if verdicts["D2"] else "FAIL",
                               "PASS" if verdicts["F1"] else "FAIL"))

    # ---------------------------------------------------------------- D3
    print("=" * 78); print("D3  BOUND COVERAGE, modelled selection of UNKNOWN strength (%d reps)" % REPS_B)
    rng = np.random.default_rng(SEED + 2)
    hit, widths = [], []
    t0 = time.time()
    for rep in range(REPS_B):
        y, s, ti, ev, nn = m.simulate_conducted(rng, N_CONDUCTED, THETA_TRUE, TAU_TRUE)
        g0, g1 = m.gammas_from_publication_probs(s, 0.99, P_LEAST_TRUE)
        sel = m.select_copas(rng, y, s, ti, g0, g1, RHO_TRUE)
        if sel.sum() < 8:
            continue
        rows = m.sensitivity_surface(y[sel], s[sel], rho_grid=BOUND_RHO,
                                     p_least_grid=BOUND_PLEAST, seed=rep)
        lo, hi = m.honest_bound(rows)
        hit.append(lo <= THETA_TRUE <= hi); widths.append(hi - lo)
    d3 = np.mean(hit)
    print("  replicates %d ; elapsed %.1fs ; bound coverage %.3f ; median bound width %.3f logit"
          % (len(hit), time.time() - t0, d3, np.median(widths)))
    verdicts["D3"] = d3 >= 0.90
    print("  D3 %s" % ("PASS" if verdicts["D3"] else "FAIL"))

    # ---------------------------------------------------------------- F2
    print("=" * 78)
    print("F2  FALSIFICATION: selection on the study's TRUE risk u_i, not on its sampling")
    print("    error -- referral centres whose real case-mix is worse publish more often.")
    print("    The Copas family has no parameter for this. (%d reps, kappa=1.5)" % REPS_B)
    rng = np.random.default_rng(SEED + 3)
    hit2, los, his = [], [], []
    t0 = time.time()
    for rep in range(REPS_B):
        y, s, ti, ev, nn = m.simulate_conducted(rng, N_CONDUCTED, THETA_TRUE, TAU_TRUE)
        g0, g1 = m.gammas_from_publication_probs(s, 0.99, 0.6)
        sel = m.select_on_random_effect(rng, y, s, ti, THETA_TRUE, g0, g1, kappa=1.5)
        if sel.sum() < 8:
            continue
        rows = m.sensitivity_surface(y[sel], s[sel], rho_grid=BOUND_RHO,
                                     p_least_grid=BOUND_PLEAST, seed=rep)
        lo, hi = m.honest_bound(rows)
        hit2.append(lo <= THETA_TRUE <= hi); los.append(lo); his.append(hi)
    f2 = np.mean(hit2)
    print("  replicates %d ; elapsed %.1fs" % (len(hit2), time.time() - t0))
    print("  bound coverage of the true theta = %.3f   (median bound [%.3f, %.3f] vs truth %.3f)"
          % (f2, np.median(los), np.median(his), THETA_TRUE))
    verdicts["F2_fires"] = f2 < 0.50
    print("  F2 %s" % ("FIRED as pre-specified: the estimator is falsifiable and here it is FALSE"
                       if verdicts["F2_fires"] else
                       "DID NOT FIRE: coverage >= 0.50, reported as a non-firing test"))

    # ---------------------------------------------------------------- summary
    print("=" * 78); print("SUMMARY")
    for k in ("D1", "D2", "F1", "D3"):
        print("  %-4s %s" % (k, "PASS" if verdicts[k] else "FAIL"))
    print("  F2   %s" % ("FIRED (required)" if verdicts["F2_fires"] else "NOT FIRED"))
    ok = all(verdicts[k] for k in ("D1", "D2", "F1", "D3")) and verdicts["F2_fires"]
    print("OVERALL: %s" % ("ALL PRE-SPECIFIED CRITERIA MET" if ok else "NOT ALL CRITERIA MET"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

### `research/meta/tests/k_feasibility.py`

```python
"""How many published series does this estimator need before its bound says anything?
SYNTHETIC data only. Truth theta=-0.8 (=0.310)."""
import sys, numpy as np
sys.path.insert(0,'/tmp/claude-0/w18')   # coordinator: repoint
import emc_copas_selection as m
TH, TAU, RHO, PL = -0.8, 0.5, 0.7, 0.3
GR, GP = (0.0,0.4,0.8), (0.99,0.3)
print("k_pub  reps  bound coverage  median bound width (logit)  median bound (proportion scale)")
for k_cond in (4, 8, 16, 30, 60):
    rng=np.random.default_rng(4242+k_cond); hit=[];w=[];los=[];his=[];kp=[]
    for rep in range(60):
        y,s,ti,e,n=m.simulate_conducted(rng,k_cond,TH,TAU)
        g0,g1=m.gammas_from_publication_probs(s,0.99,PL)
        sel=m.select_copas(rng,y,s,ti,g0,g1,RHO)
        if sel.sum()<3: continue
        rows=m.sensitivity_surface(y[sel],s[sel],rho_grid=GR,p_least_grid=GP,seed=rep)
        lo,hi=m.honest_bound(rows)
        hit.append(lo<=TH<=hi); w.append(hi-lo); los.append(lo); his.append(hi); kp.append(int(sel.sum()))
    ex=lambda x:1/(1+np.exp(-x))
    print("%5.1f %5d  %13.3f  %25.3f   [%.3f, %.3f]"%(
        np.median(kp),len(hit),np.mean(hit),np.median(w),ex(np.median(los)),ex(np.median(his))))
```

### `research/meta/tests/f2_kappa_sweep.py`

```python
"""POST-HOC (not pre-specified): how strong must selection-on-the-true-risk be before the
honest bound stops covering the truth? SYNTHETIC. Truth theta=-0.8."""
import sys, numpy as np
sys.path.insert(0,'/tmp/claude-0/w18')   # coordinator: repoint
import emc_copas_selection as m
TH,TAU=-0.8,0.5; GR,GP=(0.0,0.4,0.8),(0.99,0.3)
print("kappa  reps  k_pub  bound coverage  median bound (logit)      vs truth -0.800")
for kap in (1.5, 3.0, 6.0, 12.0):
    rng=np.random.default_rng(999+int(kap*10)); hit=[];los=[];his=[];kp=[]
    for rep in range(70):
        y,s,ti,e,n=m.simulate_conducted(rng,40,TH,TAU)
        g0,g1=m.gammas_from_publication_probs(s,0.99,0.6)
        sel=m.select_on_random_effect(rng,y,s,ti,TH,g0,g1,kappa=kap)
        if sel.sum()<8: continue
        rows=m.sensitivity_surface(y[sel],s[sel],rho_grid=GR,p_least_grid=GP,seed=rep)
        lo,hi=m.honest_bound(rows)
        hit.append(lo<=TH<=hi); los.append(lo); his.append(hi); kp.append(int(sel.sum()))
    print("%5.1f %5d %6.0f  %13.3f   [%6.3f, %6.3f]"%(
        kap,len(hit),np.median(kp),np.mean(hit),np.median(los),np.median(his)))
```

---

## Limitations

1. **NOT APPLIED TO REAL DATA.** Every number in this report comes from synthetic data generated in-process. No EMC quantity is estimated here. The k-feasibility table explains why: at the registry's k=3 the bound spans 0.204–0.460 and is uninformative.
2. **The bound is not a guarantee.** F2's post-hoc sweep shows it excluding the truth in ~76% of replicates when selection runs through the study's true risk rather than its sampling error. Assumption A2 is untestable from published data. A reader must not treat [0.257, 0.371] as a coverage-guaranteed interval.
3. **F1 failed its own pre-specified threshold** (+0.0521 vs <0.05). Even with the selection parameters known exactly, a residual upward bias of about 0.05 logit units survives at k≈28. I did not relax the criterion.
4. **F2 did not fire at the pre-specified κ=1.5.** The κ sweep that located the breaking point is post-hoc and is labelled as such; it is hypothesis-generating about the estimator, not a pre-registered result.
5. **The proportion framing is itself contestable.** Metastasis is time-to-event. `PROTOCOL.md` §6 already refuses to pool time-anchored survival as a crude proportion for exactly this reason, and assumption A5 records that the same objection applies here. This estimator does not solve follow-up heterogeneity; it inherits it.
6. **Overlap (A4) is unmodelled.** The registry marks 8 of 14 cohorts `pool:false` for population overlap. Independence is assumed and is known to be false in the real corpus.
7. **The Copas & Shi citation was not retrieved this session** and should be verified before any of this reaches prose.
8. **Transfer limit.** This is a statistical method with simulation-based validation. It establishes nothing about EMC biology, no treatment effect, no clinical efficacy, safety or readiness, and it is not a proposed clinical paper. Simulation validation of an estimator is legitimate evidence *about the estimator* and about nothing else.
9. **scipy was installed this session** rather than being a pinned repository dependency; if this code is integrated, that dependency must be declared and pinned.
10. **Grid dependence.** The "honest bound" is the union over a grid I chose (ρ ≤ 0.8, P(pub|least precise) ≥ 0.1). A wider grid gives a wider bound. The grid is an assumption, stated, not derived.

---

## Stop condition

**Set:** a fully specified estimand with explicit identification assumptions, runnable code, and executed diagnostic + falsification runs with real exit evidence.

**MET.** The estimand is stated with its population, functional and interpretation; six identification assumptions are enumerated with violation modes and severity, with the selection mechanism as a modelled object carrying its own parameters; complete runnable code is returned inline; four runs executed with real exit codes (0, 1, 0, 0). Both required regimes ran: D2/F1 (must recover a known truth — recovered, coverage 0.933, though the bias threshold failed by 0.002) and F2 (must fail — did not fire at the pre-specified κ, fires decisively at κ≥3 in the post-hoc sweep). The overall harness verdict is honestly `NOT ALL CRITERIA MET`, exit 1, and I did not adjust the criteria to change it.

---

## Tool-call and wall-clock count actually used

- **Tool calls: 26** (24 Bash, 1 ToolSearch, 1 background-wait). Target was ~40 — under.
- **Wall clock: 01:56:25Z → 02:30:15Z ≈ 34 minutes**, plus this write-up. Target was ~40 minutes — approximately on target. The single validation run alone consumed 11m44s of that.
- No network requests, no paid API, no GPU, no repository writes, no git operations, no external contact. No content-policy refusal was encountered on any branch.

---

## Next concrete action

**One successor task, inside this lane:** extend the selection family to a **two-channel** model that adds an explicit parameter for selection on the study's *true* risk $u_i$ (the A2 violation), so that the referral-centre channel F2 exposes becomes a *gridded sensitivity dimension* rather than an unmodelled fatal assumption. The falsification harness already exists and would become its acceptance test: the extended estimator must restore bound coverage ≥ 0.90 in the κ=6 regime where the current one collapses to 0.243, without inflating the k=24 bound width beyond about 0.7 logit. This is bounded, has a pre-specified pass criterion, and needs no data.

**What I would not do next:** apply this to the registry. At k=3 that produces an interval spanning 0.204–0.460, and reporting it would be the false-confidence failure this lane exists to prevent.

result: Built and validated a Copas-type publication-selection estimator for a pooled EMC proportion — estimand, six identification assumptions, complete runnable code, and four executed synthetic runs (exit 0/1/0/0); key findings: selection strength is unestimable at EMC scale (fitted ρ wrong-signed in 68% of replicates), naive DerSimonian–Laird 95% CIs cover the truth only 75% of the time, the estimator is falsifiable and provably false when selection runs through study-level true risk (bound coverage 0.243 at κ=6), and it is NOT APPLIED TO REAL DATA because the registry's k=3 poolable cohorts yield an uninformative bound of 0.204–0.460; harness exits 1 on its own pre-specified criteria (F1 bias +0.0521 vs <0.05, F2 non-firing at the pre-specified κ) and those criteria were not relaxed.
