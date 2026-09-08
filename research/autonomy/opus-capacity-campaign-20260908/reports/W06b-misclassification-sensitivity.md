> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git tree; the coordinator is the sole collector.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: at π = 0 my independent reimplementation reproduces the committed numbers exactly (competing shares 45.4 / 29.8 / 23.0 / 23.7, pooled median 23.0, range [12.1, 45.4], and A2 = 4/33 = 12.1% Wilson [4.8, 27.3]) — so the sensitivity machinery is anchored to the real generator, not to a paraphrase of it. Full run exit 0. `git status --porcelain` shows only the coordinator's own untracked campaign directory; I wrote nothing into the tree.

result: EMC pooled estimates are ROBUST to unquantified diagnostic misclassification — the relative-survival convergence conclusion has NO tipping point at any π in [0,1) (structurally: only 4 of 8 pooled shares can move, and the upper-median is floored at 12.1%, inside the cause-split range [10.0, 30.8]), and the cytotoxic response pool moves only in the safe direction (12.1% → 18.2% at π=0.5, intervals never separating); one provenance field change routed.

---

## Worker

- **Worker ID:** W06b — refill for Lane 6 (EMC diagnostic delay, referral pathway, molecular confirmation)
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt. I did not observe the served model and do not assert it as fact; the coordinator should extract the actual runtime model from the transcript. **No environment variable in this container names a model** — the literal `env` output below contains no model identifier, so the self-report has no environmental corroboration.
- **`date -u` at start:** `Tue Sep  8 02:05:13 UTC 2026` (first execution of the analysis). **`date -u` at end:** `Tue Sep  8 02:05:47 UTC 2026`. The reading and analysis phase preceded the first timestamped run; the analysis itself runs in under a second.
- **Write isolation complied with.** All execution under `/tmp/claude-0/W06b/`. `git status --porcelain` at end returns only `?? research/autonomy/opus-capacity-campaign-20260908/` — the coordinator's own untracked directory. `HEAD = 92abbcb905cacf07f14b238db50d1b98f6590374`, the frozen read commit. No git write operation was run.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I' | sort` (proxy/`NO_PROXY`/`JAVA_TOOL_OPTIONS` lines matched only on the substring `anthropic` inside host allowlists and are elided as noise; every Claude/Anthropic-named variable is reproduced):

```
AI_AGENT=claude-code_2-1-263_agent
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDECODE=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_CHILD_SESSION=1
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_CODE_DEBUG=true
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_SYNC_SESSION_REFS=1
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_EFFORT=medium
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_PID=522
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
SESSION_INGRESS_URL=https://api.anthropic.com
```

---

## Question

**How much could unquantified diagnostic misclassification move this repository's committed pooled EMC estimates, and is any existing pooled result fragile to it?**

W06 established the constraint — five series covering 247 of 543 published EMC patients state no molecular-confirmation numerator, and Drilon 2008's Methods establish that its testing was applied *selectively* to morphologically ambiguous cases with the tested fraction never stated. W06 did not quantify the consequence. A named exposure with no magnitude attached is not actionable: it can be used to dismiss any pooled number or to dismiss none, and nothing in the repository says which. This run attaches a magnitude.

It is open because no committed analysis in the repository sweeps a contamination parameter. `emc-relative-survival.json` lists five `limits`, none of which is diagnostic misclassification. `emc-systemic-therapy-pooling.json` carries a `where_the_evidence_is_too_thin` entry about the Drilon row's *response assessment* ("physician-assessed rather than centrally reviewed") but says nothing about its *diagnostic* assessment.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers`:

1. `grep -n -i -E "drilon|meis|kindblom|oliveira|santos|saleh" research/manuscripts/*.py research/manuscripts/*.json` — located every committed analysis touching the five unstated-numerator series. This is how I found that the exposure reaches **further than the three scripts my dispatch named**: `emc_relative_survival.py`, `emc_mortality_decomposition.py` and `emc_host_factor_model.py` all consume Drilon 2008 and Meis-Kindblom 1999.
2. `grep -n -E "18951519|10366145|10955458|30353688|1451062" research/manuscripts/emc_fusion_partner_pooling.py research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` — **no matches**. The fusion-partner pooling is not exposed.
3. A Python dump of every `short`/`label` field in `emc_fusion_partner_pooling.py` (17 sources) — independently confirms (2): its series are Stacchiotti ×4, Jacobs & Lapeire, Davis, Agaram, Huang, Lenz, Paioli, Sjögren 2003, Llombart-Bosch, Klubickova, Brenca, Bangerter, Remiszewski, Suemitsu. None is one of the five.
4. `grep -n -i -E "competing|excess_mortality|cytotoxic|12\.1|23\.0|relative" research/manuscripts/pinned-figures.json` — **no matches**; none of the quantities analysed here is a pinned figure, so nothing I report bears on `pinned-figures.json`.
5. `grep -n "design_tier" research/manuscripts/emc_systemic_therapy_pooling.py` — the eight tier strings, used to size the routed correction against the file's own existing vocabulary.

**Closed items I confirmed I am not replaying.** I opened **no retrieval route of any kind** — no PubMed call, no WebFetch, no network. In particular I did not attempt Meis-Kindblom 1999 full text (W06's proposed successor, recorded as paywalled and egress-blocked), nor Oliveira 2000, Saleh 1992, Wagner 2020, CTARC 2022, Sunitinib 2014, the Pazopanib primary or Trabectedin/RT 2018. This run is pure computation on committed inputs. **No content-policy refusal occurred.** I did not re-derive W06's denominator table; I consumed its conclusion as transferred prior work.

---

## Method / inputs

**Inputs, all committed at `92abbcb9`, all read-only:**

| File | What I took from it |
|---|---|
| `research/manuscripts/emc-relative-survival.json` | 8 pooled series-horizons with `observed_all_cause_survival`, `expected_background_survival`, `competing_share_of_deaths_pct`; the `convergence` block |
| `research/manuscripts/emc_relative_survival.py` | the exact estimator and the exact pooling rules I had to replicate (lines 94–110, 178–186) |
| `research/manuscripts/emc-mortality-decomposition.json` | `direct_cause_split` — the independent comparator, shares `[30.8, 10.0]` |
| `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` | analyses A1–A7, per-cohort counts, Wilson intervals |
| `research/manuscripts/emc_systemic_therapy_pooling.py` | the `drilon_chemotherapy` cohort dict, line 596 ff., including its `design_tier` at line 599 |
| `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` | negative check — none of the five PMIDs appears |

**Tooling.** Python 3.11.15, stdlib only (`json`, `math`, `os`, `sys`, `platform`). No numpy, no scipy, nothing to pin beyond the interpreter. No network.

**Replication requirement I imposed on myself.** My reimplementation of the relative-survival estimator and of the Wilson interval had to reproduce every committed number **exactly** at π = 0 before any swept value was allowed to mean anything. It does (see Validation).

### The model

Let **π** be the fraction of a morphology-assembled series that is not truly EMC. **π is a swept parameter, not a measurement.** No source in this repository states it for any series, and nothing below may be quoted as an estimate of contamination in any cohort.

**Sweep range and why it is defensible without inventing a rate.** π is swept 0.00–0.50, with extension to 0.90 in the therapy pool. The scale is anchored — *not* the value — by the only in-repository quantities that bracket anything: the two series that tested a morphology-assembled cohort and reported failures. Antonescu 1998 detected the fusion in 7 of 9 tested (2 negative, 0.22) and Okamoto 2001 in 15 of 18 (3 negative, 0.17). **Those are assay-scope negatives, not misclassifications** — `aso_coverage_ladder.py` already argues that Okamoto's type-panel RT-PCR on paraffin cannot report a junction it has no primer for. They therefore justify sweeping *to* 0.50 as generous, and justify nothing else.

**Signed direction, stated before computing.** The realistic contaminants of a myxoid-morphology EMC diagnosis are myxoid liposarcoma and low-grade fibromyxoid sarcoma. Both are less lethal than metastatic EMC, and for the chemotherapy question at least as chemo-responsive. Therefore:

- **Survival pools.** Contamination raises a series' observed all-cause survival. With the expected-survival denominator fixed, competing mortality = S_obs·(1/S_exp − 1) is *increasing* in S_obs while all-cause mortality is *decreasing* in it, so the competing **share** of deaths is biased **upward** by contamination. Removing contaminants must move every affected share **down**. *Predicted before running; confirmed by the run.*
- **Cytotoxic response pool.** Drilon's row is 0 responses in 21. **Zero observed events forces zero contaminant events**, so removing contaminants removes denominator only, and the pooled proportion must move **up** with π. *Predicted before running; confirmed by the run.* This is the one place where the analysis needs no assumption at all about the contaminants' behaviour — the zero numerator does the work.

**Survival correction.** S_obs = (1−π)·S_emc + π·S_c ⟹ S_emc = (S_obs − π·S_c)/(1−π). S_c, the contaminant survival at the horizon, is swept over four settings: S_obs + 0.05, + 0.10, + 0.15, and **S_c = 1.00, an extremal bound** (no contaminant dies) which maximises the distortion. A conclusion that survives S_c = 1.00 at every π survives any contaminant survival distribution whatsoever, so the extremal row is the one that carries the argument. Corrected rows are then passed through the generator's own exclusion rules (drop RS > 1; drop RS ≥ 0.99 as numerically unstable) and its own median convention (`sorted[len//2]`, the upper median of 8).

---

## Result

### Which committed analyses actually pool over the five affected series

| Committed pooled quantity | Draws on one of the five? | The affected row's provenance field, quoted | Grade |
|---|---|---|---|
| `emc-relative-survival.json` → `convergence.relative_survival_competing_share_pct_median` = **23.0** (range [12.1, 45.4], 8 series-horizons) | **YES — 4 of the 8 pooled rows.** `meisKindblom1999` @5y and @10y; `drilon2008` @5y and @10y | Series carry no design/provenance field at all in `emc-mortality-decomposition-inputs.json`; only `"registry_path"` and `"label"` (`"Two-referral-center long-term series (Drilon)"`) | **PRIMARY (arithmetic on committed inputs)** |
| `emc-systemic-therapy-pooling.json` → `A2_objective_response_cytotoxic_chemotherapy` = **4/33 = 12.1%, Wilson95 [4.8, 27.3]** | **YES — 1 of 3 rows, 63.6% of the denominator.** `drilon_chemotherapy` | `"design_tier": "retrospective two-referral-centre series, PHYSICIAN-ASSESSED response"` — **records the response-assessment exposure and not the diagnostic one** | **PRIMARY** |
| `emc-systemic-therapy-pooling.json` → `A7_the_pool_that_is_refused` = 17/91 = 18.7% | YES, but `"status": "context only - do not quote"` — the file already refuses it for a different reason (Italian-series overlap). Not a reported conclusion; excluded from the sensitivity | `drilon_chemotherapy`, as above | **UNKNOWN (not a claim)** |
| `emc-mortality-decomposition.json` → `cross_series` 5-year and 10-year bands | YES — `drilon2008` and `meisKindblom1999` are named `all_cause_sources`. Not analysed here; see Limitations | inputs carry `label` and `registry_path` only | **UNKNOWN (out of scope this run)** |
| `A1_objective_response_prospective` = 6/47 = 12.8% [6.0, 25.2] | **NO.** Rows: `pazopanib_phase2`, `sunitinib_nivolumab_immunosarc2`, `trabectedin_emc_subset` | `"prospective trial, central molecular confirmation"` / `"prospective trial, central pathology; CONFERENCE ABSTRACT ONLY"` / `"randomised phase 2 trial arm, CENTRAL RADIOLOGY REVIEW"` | **PRIMARY (unexposed)** |
| `A3_objective_response_vegfr_directed` = 13/58 = 22.4% [13.6, 34.7] | **NO.** Adds `sunitinib_italian_named_use`, `apatinib_emc_subset` | `"retrospective consecutive series, named-patient use"` / `"retrospective two-centre study of ALL chondrosarcoma subtypes"` | **PRIMARY (unexposed)** |
| `A4_disease_control` = 42/47 = 89.4% [77.4, 95.4] | **NO** — same three rows as A1 | as A1 | **PRIMARY (unexposed)** |
| `emc-fusion-partner-pooling.json` (all pooled partner frequencies) | **NO.** Grep for all five PMIDs returns nothing; its 17 sources are independently enumerated and contain none of them | n/a | **PRIMARY (unexposed)** |

Two things worth naming. First, **`emc_fusion_partner_pooling.py` is entirely unexposed** — a clean negative that narrows the problem by one of the three scripts my dispatch named. Second, the exposure is **worse in the survival pool than in the therapy pool**: half its rows are affected, versus one of three, and unlike the therapy pool it carries no provenance field on which the exposure could even be recorded.

### Sensitivity 1 — relative-survival competing-share pool

Every cell is the recomputed pooled median (%) over the 8 series-horizons, after correcting only the 4 affected rows. `PRIMARY` arithmetic on `PRIMARY` committed inputs; **π and S_c are swept parameters, not measurements.**

**Extremal bound, S_c = 1.00 (no contaminant dies — the maximum possible distortion):**

| π | MK@5y | MK@10y | Dri@5y | Dri@10y | pooled median | pooled range | inside cause-split [10.0, 30.8]? |
|---|---|---|---|---|---|---|---|
| 0.00 | 45.4 | 29.8 | 23.0 | 23.7 | **23.0** | [12.1, 45.4] | **YES** |
| 0.05 | 42.9 | 27.7 | 21.6 | 21.9 | **21.6** | [12.1, 42.9] | **YES** |
| 0.10 | 40.3 | 25.6 | 20.2 | 20.1 | **20.1** | [12.1, 40.3] | **YES** |
| 0.15 | 37.8 | 23.4 | 18.8 | 18.3 | **18.8** | [12.1, 37.8] | **YES** |
| 0.20 | 35.3 | 21.3 | 17.4 | 16.4 | **17.4** | [12.1, 35.3] | **YES** |
| 0.25 | 32.8 | 19.2 | 16.0 | 14.6 | **16.0** | [12.1, 32.8] | **YES** |
| 0.30 | 30.3 | 17.0 | 14.6 | 12.8 | **16.0** | [12.1, 30.3] | **YES** |
| 0.40 | 25.2 | 12.8 | 11.8 | 9.1 | **12.8** | [9.1, 25.2] | **YES** |
| 0.50 | 20.2 | 8.5 | 9.0 | 5.5 | **12.4** | [5.5, 20.2] | **YES** |

The three milder contaminant-survival settings (S_c = S_obs + 0.05 / +0.10 / +0.15) move the median less at every π; their full tables are in the verbatim output below. At the mildest setting the median only falls from 23.0 to 19.0 across the whole sweep.

### Sensitivity 2 — cytotoxic objective-response pool (A2)

Drilon contributes 0 events, so its corrected row is 0/round(21(1−π)) **exactly**, with no assumption about contaminant chemosensitivity required.

| π | Drilon n | pooled k/n | % | Wilson95 | Drilon share of denominator | exceeds A3's 22.4%? |
|---|---|---|---|---|---|---|
| 0.00 | 21 | 4/33 | **12.1** | [4.8, 27.3] | 63.6% | no |
| 0.10 | 19 | 4/31 | 12.9 | [5.1, 28.9] | 61.3% | no |
| 0.20 | 17 | 4/29 | 13.8 | [5.5, 30.6] | 58.6% | no |
| 0.30 | 15 | 4/27 | 14.8 | [5.9, 32.5] | 55.6% | no |
| 0.40 | 13 | 4/25 | 16.0 | [6.4, 34.7] | 52.0% | no |
| 0.50 | 10 | 4/22 | 18.2 | [7.3, 38.5] | 45.5% | no |
| 0.60 | 8 | 4/20 | 20.0 | [8.1, 41.6] | 40.0% | no |
| 0.72 | 6 | 4/18 | 22.2 | [9.0, 45.2] | 33.3% | no |
| 0.75 | 5 | 4/17 | 23.5 | [9.6, 47.3] | 29.4% | **yes** |
| 0.90 | 2 | 4/14 | 28.6 | [11.7, 54.6] | 14.3% | yes |

### The tipping-point calculation — the single most useful number, and it is an absence

**Survival pool: NO TIPPING POINT EXISTS, for any π in [0, 1) and any contaminant survival distribution.** This is structural, not empirical, and the argument is short enough to check by hand:

- The pooled quantity is the **upper median of 8** values, `sorted[4]` — the 5th smallest.
- Only **4** of the 8 are affected. The 4 unaffected shares are fixed at `[12.1, 12.4, 16.0, 19.0]` (`china2016`@7y, `china2016`@5y, `seer270_2022`@5y, `uMich2023`@5y).
- Correction can only move affected shares **down** (the signed direction, proven above).
- So in the limiting case where all 4 affected shares are driven to 0, the sorted vector is `[0, 0, 0, 0, 12.1, 12.4, 16.0, 19.0]` and `sorted[4] = 12.1`.
- **The pooled median is therefore floored at 12.1%**, which lies inside the independent cause-split range `[10.0, 30.8]`. The convergence conclusion cannot be broken by contamination at any π.

**Cytotoxic pool: three tipping points, none of which reverses a conclusion.**

| # | The statement that would change | π at which it changes | Consequence |
|---|---|---|---|
| (a) | The file's own caveat *"Drilon's 21 patients are two thirds of this pooled denominator"* | **π = 0.4286** (share falls to 50%) | The caveat weakens; the estimate does not break. Solving 21(1−π)/(33−21π) = 0.5 |
| (b) | A2's point estimate rises past A3's committed 22.4% | **π = 0.7211** | Solving 4/(33−21π) = 0.224. Would reverse the *ordering* of two point estimates whose intervals already overlap heavily — it would not create a finding, it would remove a non-finding |
| (c) | A2's Wilson interval separates from A1's or A3's | **never** — swept at 0.005 resolution over π ∈ [0, 0.995], no separation at any point | No interval separation exists to lose |
| (d) | A2's sign | **n/a** — a proportion in [0,1] has no sign. Its lower Wilson bound is 4.8% at π = 0 and rises monotonically | The conclusion "objective response to cytotoxic chemotherapy is uncommon but non-zero" is *strengthened*, never reversed |

**The answer is reassuring, and I am reporting it as such.** Every committed pooled estimate that draws on the five unstated-numerator series is robust across the whole plausible π range, and in the two cases that matter the robustness is structural rather than lucky:

- The relative-survival convergence — the methodological spine of the mortality-mechanisms paper — cannot be broken by contamination *at any contamination level*, because the median is a rank statistic and the exposure touches a minority of ranks. That is a stronger statement than "the sensitivity analysis was reassuring at the values we tried."
- The cytotoxic response pool's exposure runs **in the safe direction**. Contamination makes the true EMC-only response rate look *lower* than it is, so the committed 12.1% is a **conservative upper reading**, and the program's claim that objective response is rare in EMC is if anything understated by the contamination it was worried about.

The honest counterweight: the *existence* of the exposure remains unquantified and unrecorded, and the repository currently has no field in which a reader could see that it was considered. That is what the routed correction below fixes.

---

## Routed provenance correction (I did not edit the file)

**Target:** `research/manuscripts/emc_systemic_therapy_pooling.py`, **line 599**, inside the `drilon_chemotherapy` cohort dict.

**Current value:**
```python
"design_tier": "retrospective two-referral-centre series, PHYSICIAN-ASSESSED response",
```

**Smallest correct change — one field, one appended clause:**
```python
"design_tier": ("retrospective two-referral-centre series, PHYSICIAN-ASSESSED response, "
                "SELECTIVE molecular confirmation with unstated denominator"),
```

**Why this exact wording and no more.** The file's own tier vocabulary already distinguishes confirmation regimes: line 370 `"prospective trial, central molecular confirmation"`, line 556 `"retrospective series, central pathology review + molecular confirmation"`. The Drilon tier is the only exposed row and is currently silent on confirmation, so a reader comparing it against line 556 cannot see that the difference exists. The added clause is licensed verbatim by Drilon 2008's Methods (PMC2779719): *"In situations in which a clear diagnosis was not established on pathology, confirmation was made by reverse-transcriptase polymerase chain reaction (RT-PCR) or fluorescence in situ hybridization (FISH) analysis for the translocation t(9;22)."* — selective, denominator never stated.

**Owner and routing.** This file is not mine and I am read-only. It belongs to whoever owns `emc_systemic_therapy_pooling.py`; the coordinator should route it there. `_do_not_hand_edit` on the output JSON means the change must be made **in the script and the generator re-run**, not in `endpoint/emc-systemic-therapy-pooling.json`. **It changes no number** — `design_tier` enters no computation — so the regenerated JSON should differ in exactly this one string, which is a clean acceptance test for whoever applies it. I deliberately did **not** propose adding a π value, a contamination estimate, or a new limits entry asserting a magnitude: π is a swept parameter and must not enter a committed file as a quantity.

**A second, larger gap I am reporting but not proposing a fix for** (it is a design change, not a field change, and needs its owner's judgement): `emc-mortality-decomposition-inputs.json` carries **no design or confirmation field at all** on its series — only `key`, `label`, `n` and `registry_path`. The `meisKindblom1999` and `drilon2008` entries there feed four of the eight rows of the relative-survival pool with nothing recording that both are morphology-assembled with no stated confirmation numerator. That is the more consequential omission of the two, and it is out of my scope to design.

---

## Validation evidence

**RUN.**

- Working directory: `/tmp/claude-0/W06b` (outside the repository)
- Script: `/tmp/claude-0/W06b/emc_misclassification_sensitivity.py`, authored by me, returned inline below
- Command: `date -u && python3 -VV && python3 emc_misclassification_sensitivity.py; echo "EXIT=$?"; date -u`
- Environment: `Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]`; `Linux-6.18.44-fc-v24-x86_64-with-glibc2.39`; **third-party packages imported: NONE** (stdlib `json`, `math`, `os`, `sys`, `platform` only); no network
- **Exit code: `EXIT=0`.** Post-fix re-run: `FULL_RUN_EXIT=0`
- Timestamps: `Tue Sep  8 02:05:13 UTC 2026` → `Tue Sep  8 02:05:47 UTC 2026`
- Repository state after: `git status --porcelain` → `?? research/autonomy/opus-capacity-campaign-20260908/` only; `HEAD` unchanged at `92abbcb905cacf07f14b238db50d1b98f6590374`

**Independent sanity checks I performed on the result, not merely that it ran:**

1. **Exact replication at π = 0.** My reimplementation of the Ederer-II-convention estimator reproduces the committed `emc-relative-survival.json` values to the last printed digit: competing shares 45.4 / 29.8 / 23.0 / 23.7 for MK@5y, MK@10y, Dri@5y, Dri@10y; pooled median **23.0**; pooled range **[12.1, 45.4]**; pool size **8**. My Wilson implementation reproduces the committed A2 interval **[4.8, 27.3]** on 4/33 exactly. Neither number was copied into the sensitivity path — both are recomputed from `observed_all_cause_survival` and `expected_background_survival`, and from the integer counts.
2. **The median convention was replicated, not assumed.** I read `emc_relative_survival.py` lines 178–186 and found `shares[len(shares) // 2]` — the *upper* median, which returns 23.0 rather than the conventional 21.0 for these 8 values. Assuming the conventional median would have made the committed number irreproducible and every downstream tipping point wrong.
3. **The generator's exclusion rules were replicated, not assumed.** `japan2003`@10y (share 93.7, RS = 0.9925) is excluded by the RS ≥ 0.99 instability rule. **A bug I caught and fixed:** my first tipping-point printout listed 93.7 among the "unaffected" shares, giving a 9-element limiting vector. The limiting median was 12.1 either way, so the conclusion was unaffected — but the intermediate was wrong and I corrected it and re-ran rather than leave it. The corrected line reads `[12.1, 12.4, 16.0, 19.0]`, 8 elements in the limiting vector, limiting median 12.1.
4. **Monotonicity matches the pre-stated sign in every one of the 36 survival cells and every one of the 13 therapy cells.** Shares fall with π; A2 rises with π. Had any cell moved the other way it would have indicated an algebra error, since both directions are provable in closed form.
5. **The tipping-point absence is checkable by hand** and does not depend on the sweep: 4 unaffected shares, upper median of 8, floor 12.1, comparator range [10.0, 30.8].
6. **Negative check executed inside the script rather than asserted:** the fusion-partner pooling output is opened and searched for all five PMIDs at runtime; the run prints `-> NONE  (file present: True)`.

**Verbatim key output** (the four survival tables and the therapy table are transcribed in Result; the two verdict blocks as printed):

```
TIPPING-POINT ANALYSIS, survival pool
  8 series-horizons; median convention = sorted[4] (upper median).
  Unaffected shares, fixed at their committed values: [12.1, 12.4, 16.0, 19.0]
  Contamination correction moves the 4 affected shares DOWNWARD only.
  In the limit where all 4 affected shares fall below every unaffected share,
  the median becomes sorted[4] = the 1st of the 4 unaffected values in rank 5
    limiting sorted shares = [0.0, 0.0, 0.0, 0.0, 12.1, 12.4, 16.0, 19.0] -> limiting median = 12.1
  Cause-split comparator range = [10.0, 30.8]
  LIMITING MEDIAN 12.1 vs range: inside = True
  => No value of pi in [0,1) can push the pooled median outside the
     cause-split range, because the median is bounded below by the 5th
     smallest share and at most 4 shares can move. NO TIPPING POINT EXISTS.

TIPPING-POINT ANALYSIS, cytotoxic pool
  (a) The file's stated caveat 'Drilon's 21 patients are two thirds of this
      pooled denominator' stops being true at pi where the share falls to 50%:
      21(1-pi)/(33-21pi) = 0.5  ->  pi = 0.4286
  (b) A2's point estimate rises past A3's committed 22.4% at
      4/(33-21pi) = 0.224  ->  pi = 0.7211
  (c) Wilson-interval separation of A2 from A1 or A3 over pi in [0, 0.995]:
      NONE -- the intervals overlap at every pi
  (d) A2 is a proportion bounded in [0,1]; it has no sign to change. Its
      committed lower Wilson bound 4.8% excludes 0 at pi=0
      and rises monotonically with pi, so the conclusion 'objective response
      to cytotoxic chemotherapy is uncommon but non-zero' is preserved and
      STRENGTHENED, never reversed, by any amount of contamination.

pi IS A SWEPT PARAMETER, NOT A MEASUREMENT. No row above estimates contamination in any cohort.
```

**PROPOSED (NOT RUN).**
- Unit tests pinning `wilson()` against published reference intervals and `rs_row()` against a worked Ederer II example. I verified by exact replication of committed values, which is a stronger check for this purpose, but I wrote no test file and do not claim the numerics are unit-tested.
- Extension of the sensitivity to `emc-mortality-decomposition.json` `cross_series` (whose 5-year band names `drilon2008` and `meisKindblom1999` among six `all_cause_sources`, and whose 12 pairings already include 6 declared impossible). Not run — its estimator pairs across populations and its exclusion logic would need reading first; I did not want to sweep a parameter through machinery I had not verified I could replicate at π = 0.
- Re-running `emc_systemic_therapy_pooling.py` after the routed `design_tier` change, to confirm the regenerated JSON differs in exactly one string. Not run — the file is not mine and running its generator would write into the tree.
- Any retrieval that would reduce π's ignorance (Meis-Kindblom 1999, Oliveira 2000, Saleh 1992 full texts). No route attempted.

---

## Limitations

- **π is a swept parameter and is labelled so everywhere. It is not a measurement, not an estimate, and not a claim about any cohort.** Nothing in this report says that Drilon 2008 or Meis-Kindblom 1999 contains any misclassified tumour. It says what would follow *if* they did, at each of a range of assumed fractions.
- **A sensitivity range is not a point estimate.** The corrected medians in the tables are conditional on π and S_c and must never be quoted as revised values of the competing share.
- **This is a robustness result, not a validation.** Showing that a pooled estimate cannot be moved by one specific bias says nothing about the other biases the source files already document — the Ederer II synthetic-cohort approximation, a single US life table applied to Japanese, Swedish, Chinese and Italian cohorts across five decades, publication bias, and the possible non-independence of the two Italian series. Those remain exactly as stated.
- **The structural argument depends on the current composition of the pool.** The survival pool's immunity comes from 4 unaffected rows out of 8 and an upper-median convention. If a future revision drops an unaffected series, adds another morphology-only one, or changes the median convention, the floor moves and the tipping point must be recomputed. The result is a property of `emc-relative-survival.json` as committed at `92abbcb9`, not a permanent property of the method.
- **The contaminant model is a two-component mixture with a single survival parameter per horizon.** Real contamination would be heterogeneous across contaminant type, grade and stage. The extremal S_c = 1.00 row is the defence against this: it bounds any mixture whose components all survive at least as well as EMC. It does **not** bound a contaminant that does *worse* than metastatic EMC, which I judge unrealistic for myxoid liposarcoma and low-grade fibromyxoid sarcoma but have not established from a retrieved source in this run.
- **I did not analyse `emc-mortality-decomposition.json` `cross_series`,** which is exposed and un-swept. That is a real gap in coverage of the exposure, named rather than hidden, and it is the successor task below.
- **Saleh 1992, Oliveira 2000 and Santos 2018 turned out to feed no committed pooled quantity I could find.** Of the five unstated-numerator series, only Drilon 2008 and Meis-Kindblom 1999 reach a pooled estimate. That narrows the problem usefully but rests on a grep over `research/manuscripts/`; a series reaching a pool through the clinical registry under a different label would not have been caught.
- **No clinical claim of any kind follows from this report.** It contains no efficacy, safety, selectivity or readiness statement, no new patient data, and no wet-lab result. Every number is arithmetic on values already committed to this repository.
- **The diagnostic-delay and referral-pathway halves of Lane 6 remain untouched,** as they were after W06.

---

## Stop condition

**Set by the dispatch:** an executed misclassification sensitivity analysis with a tipping-point result per affected pooled quantity, and a routed provenance correction.

**MET.**

- Executed: exit 0, real numeric output, Python 3.11.15, stdlib only, run under `/tmp/claude-0/W06b`, anchored by exact replication of every committed value at π = 0.
- Tipping point per affected pooled quantity: **relative-survival competing-share median — no tipping point exists at any π, proven structurally** (median floored at 12.1%, comparator range [10.0, 30.8]); **cytotoxic response pool — three thresholds computed (π = 0.4286 dominance caveat, π = 0.7211 point-estimate ordering, no interval separation at any π), none reversing a conclusion.** Two further pooled families (A1/A3/A4, fusion-partner) shown to be unexposed; A7 excluded as already non-quotable; `cross_series` named as exposed and not swept.
- Routed provenance correction: `emc_systemic_therapy_pooling.py` line 599, one field, exact replacement string given, file not edited, ownership and acceptance test stated.

---

## Tool-call and wall-clock count actually used

**Tool calls: 13** (3 context reads, 3 prior-work/provenance greps, 4 committed-output inspections, 1 script write-and-run, 1 bug-fix re-run, 1 environment/verification call). **Wall clock: roughly 20 minutes.** Both inside the ~40/~40 target. No retrieval, no network, no spend.

---

## Next concrete action

**One successor, and it is the only remaining un-swept exposure.** Extend this sensitivity to `emc-mortality-decomposition.json` → `cross_series`, whose 5-year band names `drilon2008` and `meisKindblom1999` among six `all_cause_sources` and reports `competing_share_of_deaths_pct_median = 58.6` over 12 pairings of which 6 are already declared impossible. That quantity is more fragile *a priori* than the two analysed here, for a reason visible without running anything: it pairs all-cause survival from one population against disease-specific survival from another, so contamination inflates the all-cause term while leaving the disease-specific term alone — and the file's own `excluded_pairings` machinery shows that pairings flip to "impossible" at a threshold, which is exactly the shape of a real tipping point. The work is the same shape as this run: replicate `emc_mortality_decomposition.py`'s pairing and exclusion logic at π = 0 first, refuse to proceed unless it reproduces 58.6 and the 6/6 coherent/impossible split exactly, then sweep. It needs no retrieval and no new access.

Explicitly **not** recommended as a successor: another attempt at Meis-Kindblom 1999 full text. W06 already routed that correctly and it is paywalled and egress-blocked here; and this run has now shown that the answer would not change any pooled conclusion, only narrow π. That reorders the lane's priorities — the retrieval is no longer the decisive next step it looked like when W06 proposed it.

---

### Code, for the coordinator to write to disk

`research/autonomy/opus-capacity-campaign-20260908/code/W06b/emc_misclassification_sensitivity.py` (suggested path; the file as run lives at `/tmp/claude-0/W06b/emc_misclassification_sensitivity.py`):

```python
#!/usr/bin/env python3
"""Misclassification sensitivity for EMC pooled estimates (worker W06b).

WHAT pi IS. pi is a SWEPT PARAMETER, NOT A MEASUREMENT. It is the fraction of a
morphology-assembled series that is not truly extraskeletal myxoid chondrosarcoma.
No source in this repository states it for any series. Nothing below may be quoted as
an estimate of contamination in any cohort.

WHY THESE SERIES. W06 established that five series in the EMC literature state no
molecular-confirmation numerator at all: Saleh 1992, Meis-Kindblom 1999, Oliveira 2000,
Drilon 2008 and Santos 2018. Drilon 2008's Methods (PMC2779719) state that molecular
confirmation was made only "in situations in which a clear diagnosis was not established
on pathology" -- selective testing, tested fraction never stated.

SIGNED DIRECTION, STATED BEFORE COMPUTING.
  Realistic contaminants of a myxoid-morphology EMC diagnosis are myxoid liposarcoma and
  low-grade fibromyxoid sarcoma. Both are less lethal than metastatic EMC and, for the
  chemotherapy question, at least as chemo-responsive.
  (a) SURVIVAL POOLS: contamination raises a series' observed all-cause survival. With a
      fixed expected-survival denominator, competing mortality = S_obs*(1/S_exp - 1) is
      INCREASING in S_obs and all-cause mortality is decreasing in it, so the competing
      SHARE of deaths is biased UPWARD by contamination. Removing contaminants must move
      every affected competing share DOWN. Predicted before running.
  (b) CYTOTOXIC RESPONSE POOL: Drilon's row is 0 responses in 21. Zero observed events
      forces zero contaminant events, so removing contaminants can only shrink the
      denominator. The pooled cytotoxic response proportion must move UP with pi.
      Predicted before running.

Inputs are read from the committed repository files; nothing is written to the repository.
"""
from __future__ import annotations
import json, math, os, sys, platform

REPO = "/home/user/Rare-cancers"
RS_JSON   = os.path.join(REPO, "research/manuscripts/emc-relative-survival.json")
SYS_JSON  = os.path.join(REPO, "research/manuscripts/endpoint/emc-systemic-therapy-pooling.json")
DEC_JSON  = os.path.join(REPO, "research/manuscripts/emc-mortality-decomposition.json")

# The five unstated-numerator series, keyed as the repository keys them.
AFFECTED_SERIES = {"drilon2008", "meisKindblom1999"}      # present in the survival pool
AFFECTED_COHORTS = {"drilon_chemotherapy"}                 # present in the therapy pools

PI_GRID = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]


def wilson(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (None, None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * p, 100 * max(0.0, c - h), 100 * min(1.0, c + h))


# ---------------------------------------------------------------- Part 1: survival pool
def rs_row(observed: float, expected: float):
    r = observed / expected
    allc = 1 - observed
    excess = 1 - r
    comp = allc - excess
    return {"rs": r, "excess_pct": 100 * excess, "allcause_pct": 100 * allc,
            "competing_pct": 100 * comp,
            "share_pct": (100 * comp / allc) if observed < 1 else None}


def pool_shares(rows):
    """Replicates emc_relative_survival.py exactly: exclude RS>1 and RS>=0.99,
    sort the remaining shares, median = sorted[len//2] (upper median)."""
    ok, exc = [], []
    for r in rows:
        if r["share"] is None:
            continue
        if r["rs"] > 1.0:
            exc.append((r["key"], "RS>1")); continue
        if r["rs"] >= 0.99:
            exc.append((r["key"], "RS>=0.99 unstable")); continue
        ok.append(r)
    shares = sorted(x["share"] for x in ok)
    med = shares[len(shares) // 2] if shares else None
    return shares, med, len(ok), exc


def survival_sensitivity(rsdoc):
    committed = []
    for s in rsdoc["series"]:
        if s.get("status") != "OK" or s.get("competing_share_of_deaths_pct") is None:
            continue
        committed.append({
            "key": f"{s['series']}@{s['horizon_years']:.0f}y",
            "series": s["series"],
            "horizon": s["horizon_years"],
            "S_obs": s["observed_all_cause_survival"],
            "S_exp": s["expected_background_survival"],
            "rs": s["relative_survival"],
            "share": s["competing_share_of_deaths_pct"],
            "affected": s["series"] in AFFECTED_SERIES,
        })
    base_shares, base_med, base_n, base_exc = pool_shares(committed)
    cause_split = [d["competing_share_of_deaths_pct"]
                   for d in json.load(open(DEC_JSON))["direct_cause_split"]]
    lo_cs, hi_cs = min(cause_split), max(cause_split)

    print("=" * 78)
    print("PART 1 -- relative-survival competing-share pool (emc-relative-survival.json)")
    print("=" * 78)
    print(f"committed pool: n={base_n} series-horizons, range "
          f"[{base_shares[0]}, {base_shares[-1]}], median {base_med}")
    print(f"  affected rows (unstated molecular-confirmation numerator): "
          f"{[r['key'] for r in committed if r['affected']]}")
    print(f"  cause-split comparator (independent): {cause_split}  -> range "
          f"[{lo_cs}, {hi_cs}]")
    print(f"  convergence conclusion as committed: median {base_med} lies INSIDE "
          f"[{lo_cs}, {hi_cs}] -> {lo_cs <= base_med <= hi_cs}")
    print()

    results = {}
    for label, sc_mode in (("Sc = S_obs + 0.05", 0.05), ("Sc = S_obs + 0.10", 0.10),
                           ("Sc = S_obs + 0.15", 0.15), ("Sc = 1.00 (EXTREMAL BOUND)", None)):
        print(f"-- contaminant survival assumption: {label}")
        print(f"{'pi':>6} {'MK@5y':>8} {'MK@10y':>8} {'Dri@5y':>8} {'Dri@10y':>8} "
              f"{'median':>8} {'range':>16} {'inside cause-split?':>20}")
        rows_out = []
        for pi in PI_GRID:
            cur, infeasible = [], False
            for r in committed:
                if not r["affected"] or pi == 0.0:
                    cur.append(dict(r)); continue
                sc = 1.0 if sc_mode is None else min(1.0, r["S_obs"] + sc_mode)
                num = r["S_obs"] - pi * sc
                if num <= 0 or pi >= 1.0:
                    infeasible = True
                    cur.append(dict(r, rs=0.0, share=0.0)); continue
                s_emc = num / (1 - pi)
                v = rs_row(s_emc, r["S_exp"])
                cur.append(dict(r, rs=v["rs"], share=round(v["share_pct"], 1)))
            sh, med, n_ok, _ = pool_shares(cur)
            byk = {x["key"]: x["share"] for x in cur}
            inside = (lo_cs <= med <= hi_cs) if med is not None else None
            print(f"{pi:>6.2f} {byk['meisKindblom1999@5y']:>8.1f} "
                  f"{byk['meisKindblom1999@10y']:>8.1f} {byk['drilon2008@5y']:>8.1f} "
                  f"{byk['drilon2008@10y']:>8.1f} {med:>8.1f} "
                  f"{f'[{sh[0]:.1f}, {sh[-1]:.1f}]':>16} {str(inside):>20}"
                  + ("   INFEASIBLE(S_emc<=0)" if infeasible else ""))
            rows_out.append((pi, med, inside))
        results[label] = rows_out
        print()
    return base_med, (lo_cs, hi_cs), results, committed


def survival_tipping(committed, lo_cs, hi_cs):
    """Analytic tipping point: the pooled median is the upper median of 8 sorted shares,
    i.e. sorted[4] -- the 5th smallest. Correction only lowers the 4 affected shares."""
    # Only rows that SURVIVE the generator's exclusion rules are in the pool. japan2003@10y
    # is excluded there (RS>=0.99) and must be excluded here too.
    pooled_rows, _, _, _ = pool_shares(committed)
    kept = [r for r in committed if r["share"] in pooled_rows]
    unaffected = sorted(r["share"] for r in kept if not r["affected"])
    n_tot = len(pooled_rows)
    print("TIPPING-POINT ANALYSIS, survival pool")
    print(f"  8 series-horizons; median convention = sorted[{n_tot//2}] (upper median).")
    print(f"  Unaffected shares, fixed at their committed values: {unaffected}")
    print(f"  Contamination correction moves the 4 affected shares DOWNWARD only.")
    print(f"  In the limit where all 4 affected shares fall below every unaffected share,")
    print(f"  the median becomes sorted[4] = the 1st of the 4 unaffected values in rank 5")
    limit_shares = sorted([0.0, 0.0, 0.0, 0.0] + unaffected)
    print(f"    limiting sorted shares = {limit_shares} -> limiting median = "
          f"{limit_shares[n_tot//2]}")
    print(f"  Cause-split comparator range = [{lo_cs}, {hi_cs}]")
    lim = limit_shares[n_tot // 2]
    print(f"  LIMITING MEDIAN {lim} vs range: inside = {lo_cs <= lim <= hi_cs}")
    print("  => No value of pi in [0,1) can push the pooled median outside the")
    print("     cause-split range, because the median is bounded below by the 5th")
    print("     smallest share and at most 4 shares can move. NO TIPPING POINT EXISTS.")
    print()


# ------------------------------------------------------- Part 2: cytotoxic response pool
def therapy_sensitivity(sysdoc):
    a2 = sysdoc["analyses"]["A2_objective_response_cytotoxic_chemotherapy"]["pool"]
    a1 = sysdoc["analyses"]["A1_objective_response_prospective"]["pool"]
    a3 = sysdoc["analyses"]["A3_objective_response_vegfr_directed"]["pool"]
    per = a2["per_cohort"]
    print("=" * 78)
    print("PART 2 -- cytotoxic objective-response pool A2 "
          "(endpoint/emc-systemic-therapy-pooling.json)")
    print("=" * 78)
    print(f"committed A2: {a2['events']}/{a2['denom']} = {a2['proportion_pct']}% "
          f"Wilson95 {a2['wilson95_pct']}")
    print(f"  per cohort: " + ", ".join(
        f"{k} {v['events']}/{v['denom']}" for k, v in per.items()))
    print(f"  affected row: drilon_chemotherapy, design_tier = "
          f"{next(c['design_tier'] for c in sysdoc['cohorts'] if c['key']=='drilon_chemotherapy')!r}")
    print(f"  comparators as committed: A1 {a1['proportion_pct']}% {a1['wilson95_pct']}, "
          f"A3 {a3['proportion_pct']}% {a3['wilson95_pct']}")
    print()
    print("  KEY EXACT FACT: Drilon reports 0 responses in 21. Zero observed events forces")
    print("  zero contaminant events, so no assumption about contaminant chemosensitivity")
    print("  is needed -- removing contaminants removes denominator only.")
    print()
    other_e = a2["events"] - per["drilon_chemotherapy"]["events"]
    other_n = a2["denom"] - per["drilon_chemotherapy"]["denom"]
    n_dri = per["drilon_chemotherapy"]["denom"]
    print(f"{'pi':>6} {'Drilon n':>9} {'pooled k/n':>12} {'pct':>7} {'Wilson95':>18} "
          f"{'Drilon share':>13} {'> A3 22.4%?':>12}")
    for pi in PI_GRID + [0.60, 0.72, 0.75, 0.90]:
        nd = int(round(n_dri * (1 - pi)))
        k, n = other_e + 0, other_n + nd
        p, lo, hi = wilson(k, n)
        share = 100 * nd / n if n else 0.0
        print(f"{pi:>6.2f} {nd:>9d} {f'{k}/{n}':>12} {p:>7.1f} "
              f"{f'[{lo:.1f}, {hi:.1f}]':>18} {share:>12.1f}% {str(p>22.4):>12}")
    print()
    print("TIPPING-POINT ANALYSIS, cytotoxic pool")
    # (a) dominance statement: "Drilon's 21 patients are two thirds of this denominator"
    #     21(1-pi) / (33 - 21pi) = 0.5
    pi_dom = (21 - 0.5 * 33) / (21 - 0.5 * 21)
    print(f"  (a) The file's stated caveat 'Drilon's 21 patients are two thirds of this")
    print(f"      pooled denominator' stops being true at pi where the share falls to 50%:")
    print(f"      21(1-pi)/(33-21pi) = 0.5  ->  pi = {pi_dom:.4f}")
    # (b) A2 point estimate exceeding A3
    pi_a3 = (33 - other_e / (a3["proportion_pct"] / 100)) / 21
    print(f"  (b) A2's point estimate rises past A3's committed 22.4% at")
    print(f"      4/(33-21pi) = 0.224  ->  pi = {pi_a3:.4f}")
    # (c) interval separation from A1 and A3
    sep = []
    for pi in [i / 200 for i in range(0, 199)]:
        nd = int(round(n_dri * (1 - pi)))
        p, lo, hi = wilson(other_e, other_n + nd)
        if lo > a1["wilson95_pct"][1] or hi < a1["wilson95_pct"][0]:
            sep.append(("A1", pi))
        if lo > a3["wilson95_pct"][1] or hi < a3["wilson95_pct"][0]:
            sep.append(("A3", pi))
    print(f"  (c) Wilson-interval separation of A2 from A1 or A3 over pi in [0, 0.995]:")
    print(f"      {'NONE -- the intervals overlap at every pi' if not sep else sep[:5]}")
    print(f"  (d) A2 is a proportion bounded in [0,1]; it has no sign to change. Its")
    print(f"      committed lower Wilson bound {a2['wilson95_pct'][0]}% excludes 0 at pi=0")
    print(f"      and rises monotonically with pi, so the conclusion 'objective response")
    print(f"      to cytotoxic chemotherapy is uncommon but non-zero' is preserved and")
    print(f"      STRENGTHENED, never reversed, by any amount of contamination.")
    print()


def main():
    print(f"python: {sys.version}")
    print(f"platform: {platform.platform()}")
    print(f"third-party packages imported: NONE (stdlib json/math/os/sys/platform only)")
    print(f"repo read root: {REPO}")
    print()
    rsdoc = json.load(open(RS_JSON))
    sysdoc = json.load(open(SYS_JSON))
    base_med, (lo_cs, hi_cs), _, committed = survival_sensitivity(rsdoc)
    survival_tipping(committed, lo_cs, hi_cs)
    therapy_sensitivity(sysdoc)
    print("=" * 78)
    print("PART 3 -- pooled quantities checked and found NOT to draw on any of the five")
    print("=" * 78)
    fp = os.path.join(REPO, "research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json")
    txt = open(fp).read() if os.path.exists(fp) else ""
    hits = [p for p in ("18951519", "10366145", "10955458", "30353688", "1451062")
            if p in txt]
    print(f"  emc_fusion_partner_pooling.py output: PMIDs of the five unstated-numerator")
    print(f"  series found in it -> {hits or 'NONE'}  (file present: {bool(txt)})")
    print("  A1 (prospective ORR), A3 (VEGFR ORR), A4 (disease control) contain no")
    print("  affected cohort: their rows are pazopanib_phase2, sunitinib_nivolumab_")
    print("  immunosarc2, trabectedin_emc_subset, sunitinib_italian_named_use,")
    print("  apatinib_emc_subset, anthracycline_italian_rcn -- none is one of the five.")
    print()
    print("pi IS A SWEPT PARAMETER, NOT A MEASUREMENT. No row above estimates "
          "contamination in any cohort.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
