> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Reproduction exact, all five checks pass, tree unmodified by me. Report follows.

---

## Worker

**W16b**, LANE 16 refill — testing whether W16's endpoint-decoupling bound is an artifact of short follow-up.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am powered by Opus 5, exact model ID `claude-opus-5`. I did not observe the served model and do not assert it as fact; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:06:46 UTC 2026`
`date -u` at end: `Tue Sep  8 02:09:40 UTC 2026`
(Session began ~02:02 UTC; these bracket the execution phase. Reading phase preceded the first `date -u`.)

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — unmodified except that sed redaction, and except that I mark three very long proxy list values as elided rather than reprinting them:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...                    [elided: proxy host list]
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...       [elided]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=... [elided: proxy/truststore flags, no model identity]
NO_PROXY=localhost,127.0.0.1,::1,...                    [elided]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...          [elided]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**No environment variable in this container names a served model.** Identical in this respect to W16's capture.

---

## Question

**Does the direction of the metastasis-minus-recurrence gap depend systematically on follow-up length — and if so, is W16's decoupling finding an artifact of short follow-up rather than a property of EMC?**

It is open because W16's own falsification check F3 found a real hit: Meis-Kindblom 1999, the longest follow-up in the registry (median 108 months), reports recurrence 48.2% against metastasis 46.1% — the opposite sign from the admitted cohorts, and exactly what differential ascertainment over follow-up length would predict. W16 named this as its main open flank and did not test it.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers`:

```
grep -rn -i "ussc2022\|drilon" --include=*.json --include=*.md --include=*.py . | grep -v '^./.git'
grep -rn "35962783\|jso.27062\|Sarcoma Collaborative" -l . | grep -v '^./.git'
grep -rn -i "bishop" research/modalities/emc-site-curation.json
grep -rn "13 patients who developed distant" --include=*.json --include=*.md .
```

plus full reads of `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `reports/W16-new-clinical-computation.md`, the head of `reports/W08-disease-course-surveillance-question.md`, `research/data/emc-clinical-registry.json` (all 14 cohorts dumped), `research/modalities/emc-locoregional-eligibility.json` (in full), and the relevant blocks of `research/literature/emc-km-admissibility-2026-08-27.json` and `emc-km-reachability-census-2026-08-25.json`.

**Not duplicating W08.** W08 built a patient-level census of *time to first metastasis* from 84 PubMed case reports (n=10 exact intervals, median 30 months). That is a different data object (case literature, no denominator, interval-valued) from mine (cohort marginal counts from the committed registry, denominator-anchored, no timing). No overlap in inputs, estimand or conclusion.

**Not replaying `CLOSED-WORK.md`.** No conditional-recurrence checkpoint re-proposal, no RT/IPD synthesis, no KM reconstruction, no invented cohort, no re-approach to any recorded-denied route (Drilon, USSC, SEER-270, CTARC, Wagner, pazopanib, sunitinib). **I retrieved nothing over the network at all** — every input is already on disk.

---

## Method / inputs

**Inputs (read-only, committed at frozen HEAD `92abbcb905cacf07f14b238db50d1b98f6590374`):**

- `research/data/emc-clinical-registry.json` → `registry.cohorts` (14 cohorts)
- `research/modalities/emc-locoregional-eligibility.json` — the repository's own committed admissibility adjudications, quoted rather than re-derived
- `research/modalities/emc-site-curation.json` — source of the Bishop 2019 distant-metastasis count
- `research/literature/emc-km-admissibility-2026-08-27.json`, `emc-km-reachability-census-2026-08-25.json` — access verdicts for `ussc2022` and `drilon2008`
- `research/modalities/coverage_uncertainty.py` — imported as the independent cross-implementation for F4

**Environment:** Python `3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]`, scipy `1.17.1`, numpy `2.4.6`, statsmodels **absent** (`ModuleNotFoundError: No module named 'statsmodels'`). Identical to W16's environment. Script written to and run from `/tmp/claude-0/w16b/` — **outside the repository**.

**W16's admissibility rule, transcribed and applied UNCHANGED:** a cohort enters only if `pool == true` **and** `provenance == "primary"` **and** both endpoints carry the identical denominator. I did not relax any clause, and I reconciled no mismatched denominator.

---

## Result

### 1 · Reproduction of W16 — exact, no discrepancy

I re-implemented the Fréchet–Hoeffding bound, Wilson intervals, the conservative paired Wald RD interval and the exact one-sided Clopper–Pearson lower limit independently, then compared all eight numeric fields of each of W16's three headline rows.

```
"1_reproduction_vs_W16": {
 "n_headline_rows_checked": 3,
 "n_admitted_rows_i_produced": 3,
 "discrepancies": [],
 "REPRODUCED_EXACTLY": true
}
```

| Row | Cohort | n | Met | LR / death | RD (95% conservative) | Fréchet count | ≥ % cohort | CP95 lower | ≥ % of metastatic pts | Grade |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | Masunaga 2025 localised | 134 | 39 (29.1) | LR 16 (11.9) | +17.2 (6.7, 27.6) | **[23, 39]** | 17.2% | 12.0% | **59.0%** | PRIMARY |
| A2 | Chiusole 2020 | 49 | 20 (40.8) | LR 14 (28.6) | +12.2 (−10.8, 35.3) | **[6, 20]** | 12.2% | 5.5% | **30.0%** | PRIMARY |
| B1 | Masunaga 2025 localised | 134 | 39 (29.1) | death 9 (6.7) | +22.4 (13.0, 31.8) | **[30, 39]** | 22.4% | 16.6% | **76.9%** | PRIMARY |

**No discrepancy found.** The refusal count also reproduces: 25 refused (cohort, endpoint-pair) combinations, 3 admitted rows across 2 distinct cohorts — W16's "12 of 14 cohorts refused" is the same fact counted per cohort.

### 2 · Widening the admitted set — **REFUSED. The admitted set stays at 2 cohorts.**

| Cohort | Verdict | Why, from committed evidence | Grade |
|---|---|---|---|
| `ussc2022` (n=60) | **REFUSED** | Registry gives locoregional recurrence 18/60 only. `emc-locoregional-eligibility.json` states verbatim under the metastasis pool's exclusions: `"US Sarcoma Collaborative database": "no explicit integer metastasis counts"`. The note's "any relapse 41.6%" is a *composite* (local OR distant) and **41.6% is not attainable as x/60 for any integer x** (24/60 = 40.0%, 25/60 = 41.7%), so it is a Kaplan–Meier-type or otherwise non-crude figure, not a count on this denominator. Full text unreachable: `emc-km-admissibility-2026-08-27.json` verdict `unreachable`, Unpaywall `oa_status: "closed"`, 0 OA locations. | PRIMARY |
| `drilon2008` (n=87) | **REFUSED** | Carries **no** `{events, denom}` block for either endpoint. `emc-locoregional-eligibility.json` lists it under *both* pools' exclusions as `"pool: false — percentage-only"`. A percentage with no printed numerator is not a count, and reconstructing one is reconciliation, which the rule forbids. Also `pool == false`. Full text `PMC2779719` returns HTTP 500 / `idIsNotOpenAccess`. | PRIMARY |
| `uMich2023` (n=44) | **REFUSED** | "59% developed metastasis" is percentage-only (0.59 × 44 = 25.96, not an integer); no recurrence count. `pool == false` (population overlap). | PRIMARY |
| `meisKindblom1999` | **REFUSED** | Denominators differ across all three endpoints: recurrence 40/83, metastasis 35/76, disease death 18/99. W16 refused it; so do I. | PRIMARY |
| `seer270_2022`, `remiszewski2025` ×3, `japan2003`, `china2016`, Masunaga metastatic-at-dx | **REFUSED** | Secondary provenance, percentage-only, `pool == false`, no recurrence capture, or (Masunaga metastatic stratum) metastasis is the inclusion criterion rather than an outcome. | PRIMARY |
| **`bishop2019` (n=41)** | **DENOMINATORS MATCH — still refused, on one clause only** | See below. | PRIMARY |

**The one genuine widening candidate is `bishop2019`, and W16 did not name it.** Both endpoints are committed on the identical denominator n=41: local relapse **5/41** (registry cohort note, "41 consecutive localized EMC; 5/41 (12%) local relapse") and distant metastasis **13/41** (`emc-locoregional-eligibility.json`, transcribed 2026-08-27 from the `PMC7771031` full text: *"bishop2019 partitions the 13 patients who developed distant metastases during follow-up as 12 lung and 1 bone, which exhausts that cohort"*; `emc-site-curation.json` independently records *"the registry cohort and the paper's site breakdown are both over n=41, the whole series"*). Provenance is `primary`. Median follow-up **94 months**.

It fails **exactly one** clause: `pool == false`, with `contextReason: population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)`. **I did not relax the rule, so bishop2019 is NOT admitted.** I note without acting on it that the repository's own `emc-site-curation.json` argues *"Pool membership is decided per pool, not once per source"* and does pool bishop2019 for site — and that W16's bound never pools, so the double-counting hazard the flag guards against does not arise here. **Changing the acceptance criterion is not mine to do**; I flag it as the one substantive question for whoever owns that rule.

Its bound, computed as a labelled **SENSITIVITY row outside the admitted set** (`SECONDARY`):

| Cohort | n | med FU | Met | LR | RD (95% cons.) | Fréchet count | ≥ % cohort | CP95 lower | ≥ % of metastatic pts |
|---|---|---|---|---|---|---|---|---|---|
| bishop2019 (**NOT ADMITTED**) | 41 | **94 mo** | 13 (31.7) | 5 (12.2) | +19.5 (0.1, 38.9) | **[8, 13]** | 19.5% | 10.1% | **61.5%** |

### 3 · The follow-up hypothesis — **NOT SUPPORTED, and its one specific prediction is contradicted**

**Pre-specified before looking** (encoded as constants in the script). Disclosure of the honest order of events: I had already read the Bishop counts while doing the section-2 admissibility scan, so this is a pre-specification of the *criterion*, not a blind one. I state it that way rather than pretending otherwise.

- **Would SUPPORT:** the signed gap decreases monotonically with median follow-up across every cohort reporting both endpoints, and is ≤ 0 in every cohort beyond ~90 months.
- **Would REFUTE:** at least one cohort beyond ~90 months shows a gap of the same sign and comparable magnitude to the short-follow-up cohorts.
- **Would be UNDECIDABLE:** fewer than ~5 cohorts carry both a signed gap and a median follow-up, or the gaps are mutually indistinguishable given sampling error.

**Signed gap (metastasis% − recurrence%) against median follow-up. Direction only — no bound is taken from an inadmissible row.**

| Median FU (mo) | Cohort | n | Met % | Rec % | **Gap (pp)** | Denominators match? | Admitted? | Grade |
|---|---|---|---|---|---|---|---|---|
| 38 | Masunaga 2025 localised | 134 | 29.1 | 11.9 | **+17.2** | yes | **yes** | PRIMARY |
| **94** | **Bishop 2019 localised** | 41 | 31.7 | 12.2 | **+19.5** | **yes** | no (`pool == false`) | SECONDARY |
| 108 | Meis-Kindblom 1999 | 117 | 46.1 (35/76) | 48.2 (40/83) | **−2.1** | **no** (76 vs 83) | no | SECONDARY |
| **not reported** | Chiusole 2020 | 49 | 40.8 | 28.6 | +12.2 | yes | **yes** | PRIMARY / FU **UNKNOWN** |

**Verdict, three parts:**

1. **The specific prediction of the ascertainment explanation is contradicted.** The hypothesis says the gap should shrink and cross zero as follow-up lengthens. `monotone_decreasing_in_followup: false`. The **second-longest-follow-up cohort in the set, at 94 months, has the *largest positive* gap of all four (+19.5 pp)** — and it is the only long-follow-up cohort whose two endpoints sit on the *same* denominator. `cohorts_beyond_90mo_with_a_POSITIVE_gap: ["bishop2019"]`. Under the ascertainment story this row should not exist.

2. **The one reversal is a mismatched-denominator artefact at least as plausibly as a follow-up artefact.** Meis-Kindblom's endpoints are measured on *different patient subsets* (76 vs 83 vs 99) — that is, its recurrence and metastasis statuses were ascertainable in different numbers of patients, which is a differential-ascertainment mechanism operating at the level of *reporting completeness*, not follow-up duration. It is also a consultation series selected toward diagnostically difficult tumours. Follow-up length is confounded with both.

3. **The reversal itself cannot be distinguished from zero.** Unpaired normal approximation (deliberately the *looser* of the available options, since the subsets overlap unequally and no paired variance is available): gap **−2.1 pp, SE 7.9 pp, 95% CI −17.7 to +13.4 pp**. It **covers zero**. It does **not** cover Masunaga's +17.2 — so there *is* genuine between-cohort heterogeneity in the gap, which is a point *for* F3, not against it.

**Honest limit on this verdict.** Three cohorts carry both a signed gap and a median follow-up. **No line was fitted, no correlation coefficient computed, no trend statistic reported** — three points cannot support one, and doing so would be exactly the error this task warned against. So: the ascertainment explanation's *specific directional prediction* is contradicted by a real cohort, and the reversal that motivated it is statistically indistinguishable from zero and has a competing explanation. That is **not** a demonstration that follow-up length is irrelevant. **The sample of cohorts cannot decide the general question, and I am not claiming it does.**

### 4 · The adversarial worst case — **W16's argument is correct about direction but its bound does NOT survive unconditionally**

Construction, exactly as specified: let *k* additional local recurrences exist beyond Masunaga's data cut, and place **every one** of them in a patient who has already metastasised. This is the maximally hostile placement — it removes one from the bound one-for-one.

Bound = 39 − (16 + k), on n = 134.

| k (extra late LRs) | implied true lifetime LR % | bound (count) | ≥ % of metastatic pts | CP95 lower, % of cohort |
|---|---|---|---|---|
| 0 (observed) | 11.9 | 23 | 59.0 | 12.0 |
| 5 | 15.7 | 18 | 46.2 | 8.9 |
| 10 | 19.4 | 13 | 33.3 | 5.8 |
| 15 | 23.1 | 8 | 20.5 | 3.0 |
| 20 | 26.9 | 3 | 7.7 | 0.6 |
| 22 | 28.4 | 1 | 2.6 | 0.0 |
| **23** | **29.1** | **0** | **0.0** | **0.0** |

**Breakpoint: k = 23, implied true lifetime local-recurrence rate 29.1%.** The bound survives the adversarial construction **if and only if** the cohort's true lifetime local-recurrence count stays strictly below its observed metastasis count — i.e. a lifetime local-recurrence rate **below 29.1%** in this cohort.

Committed anchors placed either side of that breakpoint (each `SECONDARY` — these are other cohorts' rates imported as assumptions, not measurements of Masunaga):

| Assumed lifetime LR rate for Masunaga | Source | implied k | bound | ≥ % of metastatic pts | **Survives?** |
|---|---|---|---|---|---|
| 11.9% | Masunaga observed @ 38 mo | 0 | 23 | 59.0 | yes |
| 12.2% | bishop2019 @ **94 mo** | 0 | 23 | 59.0 | yes |
| 27.0% | registry pooled crude (88/326) | 20 | 3 | 7.7 | yes, barely |
| 28.6% | chiusole2020 | 22 | 1 | 2.6 | yes, barely |
| 30.0% | ussc2022 locoregional | 24 | 0 | 0.0 | **NO** |
| 48.2% | meisKindblom1999 @ 108 mo | 49 | 0 | 0.0 | **NO** |

**Plain verdict.** W16's limitation 3 is **correct about the direction** of the bias — under-ascertainment of local recurrence does push the observed bound upward — but W16 did not quantify the slack, and the slack is finite and not large: **23 events, 17.2 percentage points.** Under the maximally adversarial construction the bound is destroyed by any true lifetime local-recurrence rate at or above 29.1%, and two committed EMC series report local-recurrence rates at or above that (`ussc2022` 30.0%, `meisKindblom1999` 48.2%). So the honest statement is:

- **A1 stands unconditionally as a statement at Masunaga's own 38-month horizon.** Nothing in this section touches that; the bound is arithmetic on observed counts.
- **A1 does NOT stand as a lifetime statement.** Extrapolated to indefinite follow-up under the adversarial placement, it collapses at a local-recurrence rate that the published EMC literature does reach. That is a real vulnerability, and it is the one W16's limitation 3 pointed at without measuring.

**One decomposition that cuts the other way, and it matters.** The adversarial construction requires local recurrence to be **differentially** under-ascertained. If ascertainment is merely *incomplete* — both endpoints under-counted by the same relative factor r — the bound **scales up and the fraction is invariant**:

| r | metastasis | local recurrence | bound | ≥ % of metastatic pts |
|---|---|---|---|---|
| 1.00 | 39 | 16 | 23 | 59.0 |
| 1.25 | 49 | 20 | 29 | 59.2 |
| 1.50 | 58 | 24 | 34 | 58.6 |
| 2.00 | 78 | 32 | 46 | 59.0 |

So the threat to A1 is specifically *differential* ascertainment, not short follow-up per se — and the Bishop row in section 3 is the closest thing the committed record holds to a direct test of that, since at 94 months it shows a local-recurrence rate of 12.2%, essentially identical to Masunaga's 11.9% at 38 months, with the metastasis rate likewise barely moved (31.7% vs 29.1%). **One cohort is not a demonstration.** I state it as the direction the available evidence points, not as a result.

---

## Validation evidence

**RUN.** One command, real exit code:

```
cd /tmp/claude-0/w16b && python3 w16b_followup_direction_and_adversarial.py > out.json; echo "EXIT=$?"
EXIT=0
```
`out.json` = 29538 bytes. Environment: Python 3.11.15, scipy 1.17.1, numpy 2.4.6, statsmodels absent.

**Two failures during development, reported rather than hidden:** (i) first run exited **1** — `TypeError: %i format: a real number is required, not list`, caused by a literal `95%` inside a string I was `%`-formatting; fixed by string concatenation. (ii) My no-scipy Clopper–Pearson bisection was **inverted** (it bisected toward `lo` when `P(X≥k)` is *increasing* in p, returning 100.0 on every row). It was not in the field set compared against W16, so it did not contaminate the reproduction — but a broken check is worse than no check, so I fixed the direction and re-ran. Post-fix it matches scipy on all three rows.

### Falsification checks — five, all RUN

**F1 · Reverse-direction negative control (W16's primary falsifier, re-run by me).** Verbatim:
```
"rows": [
 {"cohort":"Localised at diagnosis, surgically treated","min_recurrence_without_metastasis_pct_of_cohort":0.0,"informative":false},
 {"cohort":"European two-institution series (Chiusole)","min_recurrence_without_metastasis_pct_of_cohort":0.0,"informative":false}],
"PASSES": true
```
**PASSES.** The bound vanishes in the direction the data does not support.

**F2 · The adversarial machinery must reduce to the observed bound at k = 0.** `bound_at_k0: 23`, `expected: 23`, `PASSES: true`. Guards against the adversarial code silently re-deriving a different quantity.

**F3 · Meis-Kindblom reversal — PRESERVED VERBATIM, NOT SOFTENED.** W16's F3 text is carried into my output character-for-character. My addition does not weaken it: the reversal's 95% interval `[-17.7, 13.4]` pp covers zero **but does not cover Masunaga's +17.2**, so the gap is genuinely heterogeneous between cohorts and F3 is if anything *strengthened* as a constraint on generality. What F3 does not establish — and what section 3 tests and fails to support — is that follow-up *length* is the reason.

**F4 · Cross-implementation against the repository's own independent frequency-scale code.** Imported `research/modalities/coverage_uncertainty.py::intersection_bounds` and checked my count-scale `frechet_intersection` on 5 cases including the degenerate `(1,1,1)`, the forced-overlap `(5,5,6) → [4,5]`, and all three live cohorts. `"all_agree": true`.

**F5 · Exact CP limits re-derived with pure `math.comb` bisection, no scipy.** All three rows match: 12.0 / 12.0, 16.6 / 16.6, 5.5 / 5.5. `"all_match": true`.

**Hand arithmetic re-done independently:** 13 − 5 = 8; 8/41 = 19.5%; 8/13 = 61.5%. 39 − 16 = 23; breakpoint LR = 39; 39/134 = 29.1%. −2.1 ± 1.96 × 7.9 = [−17.6, 13.4] (script prints −17.7, a rounding difference in the last digit of the SE, not a discrepancy in the conclusion).

**Write isolation verified.** `git rev-parse HEAD` = `92abbcb905cacf07f14b238db50d1b98f6590374`, **unchanged**. `git status --porcelain` shows only the coordinator's campaign directory (its files moved from `??` to staged `A` between my first and last check — **the coordinator staged them; I issued no git command of any kind**). No file authored by me appears anywhere in the tree. All execution in `/tmp/claude-0/w16b/`.

**PROPOSED (NOT RUN):** any change to W16's admissibility rule regarding `pool == false`; any integration into repository test tiers; any figure; any full-text retrieval of `ussc2022` or `drilon2008`. None attempted.

---

## Limitations

**W16's ten limitations are preserved intact and none is softened.** In particular limitation 1 (the bound is a floor, never an estimate), limitation 2 (no temporal ordering), limitation 3 (ascertainment may drive the direction) and limitation 6 (no pooling; the populations are not exchangeable) all continue to apply unchanged to rows A1, A2 and B1. Additionally:

1. **W16's limitation 3 is now quantified and partly qualified, not removed.** Its claim that under-ascertainment biases the bound upward is correct in direction; section 4 shows the slack is 23 events and that the bound does not survive an adversarial lifetime local-recurrence rate ≥ 29.1%. A1 remains a horizon statement, not a lifetime statement.
2. **The follow-up verdict rests on three follow-up-paired cohorts.** It contradicts one specific prediction of the ascertainment explanation; it does not establish the negation of that explanation, and I fitted nothing.
3. **The decisive long-follow-up row (bishop2019) is NOT admitted** and carries n = 41 with a conservative RD interval whose lower bound is +0.1 pp — barely off zero. It is one single-institution series in which 10-year local control was 100% with surgery + radiotherapy, so its low local-recurrence rate is plausibly a *treatment* effect rather than a natural-history one. That cuts against reading it as a clean test of ascertainment.
4. **Chiusole 2020 reports no median follow-up**, so the one other admitted cohort contributes nothing to the follow-up comparison. UNKNOWN, not zero.
5. **The committed anchors in section 4 are other cohorts' rates imported as assumptions about Masunaga.** They are not measurements of Masunaga's lifetime rate, which is unmeasured and unmeasurable from committed data.
6. **The Bishop metastasis count (13/41) is a committed transcription**, made 2026-08-27 from `PMC7771031` by earlier work in this repository. I did not re-read the primary text — no network retrieval was performed — so it inherits that transcription's correctness.
7. **No pooling across non-exchangeable cohorts was performed anywhere.** The registry's own 27.0% pooled recurrence figure appears only as a labelled assumption in the section-4 anchor table, never as an estimate of anything.
8. **What this cannot claim:** no clinical recommendation; no statement about surveillance intervals, imaging schedules, margins, radiotherapy or any treatment; no prognosis for any patient; no efficacy, safety, selectivity or therapeutic-window claim; no surrogate-endpoint validation. No bound is reported as a point estimate. No new patients were created — the same 183 admitted patient-records as W16, plus 41 Bishop and 117 Meis-Kindblom records used for direction only.
9. **`ussc2022` and `drilon2008` remain route-limited, not method-limited.** Both are `oa_status: "closed"`. I replayed no denied route.

---

## Stop condition

**Set:** an executed reproduction, a widened or explicitly-refused admitted set, an honest verdict on the follow-up-length hypothesis, and the adversarial worst-case bound.

**MET, all four.** (i) Reproduction executed at exit 0, exact on all eight numeric fields of all three headline rows, no discrepancy. (ii) Admitted set **explicitly refused** at 2 cohorts, with a per-cohort reason from committed evidence for all 14, including the previously unnamed `bishop2019`, which matches on denominators and fails on `pool == true` alone. (iii) Follow-up hypothesis **not supported** — its specific prediction is contradicted by a 94-month cohort with the largest positive gap in the set, the one reversal is indistinguishable from zero, and the sample of cohorts honestly cannot decide the general question. (iv) Adversarial bound computed: breakpoint k = 23, lifetime local-recurrence rate 29.1%; the bound survives at the study horizon and **does not survive unconditionally** as a lifetime claim.

---

## Tool-call and wall-clock count actually used

**15 tool calls** (all `Bash`; no network retrieval, no subagents, no writes to the repository, no git write command). **Wall clock ≈ 13 minutes** (~02:02 → 02:15 UTC). Both inside the ~40 min / ~40 call target.

---

## Next concrete action

**One successor, and it is a rule-ownership decision rather than new computation:** put the `bishop2019` case to whoever owns W16's admissibility rule. Its two endpoints sit on the identical denominator n=41 from primary committed evidence, its median follow-up of 94 months is the longest available on matching denominators, and it fails only the `pool == true` clause — a clause that exists to prevent double-counting *within a pool*, whereas this bound pools nothing and evaluates each cohort separately. The repository's own `emc-site-curation.json` already articulates the principle ("Pool membership is decided per pool, not once per source") and applies it to this same source. If that clause is judged inapplicable to a non-pooling estimand, the admitted set goes from 2 cohorts to 3, the longest matching-denominator follow-up enters the admitted evidence, and the follow-up-length flank moves from "contradicted by a sensitivity row" to "contradicted by an admitted row". **I could not make that call — authoring or relaxing my own acceptance criterion is forbidden — so it is handed over, not done.**

result: W16's Fréchet bound reproduced exactly (exit 0, zero discrepancies across all 3 headline rows); admitted set explicitly refused at 2 cohorts with committed per-cohort reasons, uncovering bishop2019 (13/41 metastasis vs 5/41 recurrence, median FU 94 mo) as the sole widening candidate blocked only by `pool == false`; the follow-up-length explanation for F3 is NOT supported — the 94-month cohort carries the largest positive gap (+19.5 pp) and Meis-Kindblom's reversal is −2.1 pp (95% CI −17.7 to +13.4, covers zero) — and the adversarial worst case gives a hard breakpoint of k=23 missed late local recurrences (29.1% lifetime rate), so W16's A1 stands unconditionally at its 38-month horizon but collapses as a lifetime claim at local-recurrence rates two committed EMC series actually report.
