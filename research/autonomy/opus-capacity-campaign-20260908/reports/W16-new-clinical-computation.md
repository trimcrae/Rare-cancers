> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, extracted by the coordinator from the child transcript:
> `"model":"claude-opus-5"` (OBSERVED, not self-report).

---

Sanity check done: HEAD is still the frozen commit `92abbcb9`, `git status --porcelain` shows only the pre-existing campaign directory (I created no file in the tree), the script exited 0, the exact-CI bisection re-derivation matched scipy to the reported digit on every row, my Fréchet counts agreed with the repository's independent frequency-scale implementation on 5/5 cases, and I re-did the key arithmetic by hand (39−16=23; 23/134=17.2%; 23/39=59.0%).

result: EMC registry data yields a distribution-free bound never previously computed here — at least 59% of patients who develop distant metastasis do so with no documented local recurrence (Masunaga n=134), and at least 77% of metastatic patients are not disease-dead at the study horizon — with a run negative control that correctly returns a null bound in the reverse direction.

---

## Worker

**W16**, LANE 16 — a new clinically important, nontrivial computation supportable by retained public data.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`) per my system context. I do not assert this as observed fact; the coordinator must extract the actual served model from the transcript.

`date -u` at start: `Tue Sep  8 01:58:26 UTC 2026`
`date -u` at end: `Tue Sep  8 01:59:43 UTC 2026`
(Session began ~01:52 UTC; the two `date -u` calls bracket the execution phase.)

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (unmodified except that sed redaction):

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
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
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
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
JAVA_TOOL_OPTIONS=<proxy/truststore flags, no model identity>
npm_config_noproxy=<same list as no_proxy>
NO_PROXY=<same list as no_proxy>
```

**No environment variable in this container names a served model.** `CLAUDE_EFFORT=medium` and `CLAUDE_CODE_VERSION=2.1.42` are the only behaviourally relevant values present.

---

## Question

**Published EMC series report local recurrence, distant metastasis and disease-specific death as separate marginal counts on the same patients, and essentially never print the cross-tabulation. How many EMC patients develop distant metastasis *without* a documented local recurrence — and how many are alive without disease-specific death after metastasis?**

Why it is open, and why it matters clinically:

- The joint distribution is unpublished, so the quantity looks unavailable. It is not unavailable — it is **partially identified**. Given two marginals on the **same denominator**, the Fréchet–Hoeffding inequalities pin every cell of the unobserved 2×2 to an interval **under any dependence whatever**, including perfect nesting. The lower bound is *attained*, so it cannot be tightened without new data, and it requires no independence assumption.
- Clinically it bears on the central endpoint problem this lane names. If most metastases are preceded by a local failure, local-control endpoints (margin status, local recurrence, RT effect) carry information about distant failure. If most are not, they cannot, and a local-control endpoint is not a surrogate for the event that kills patients in this disease.
- The second axis quantifies the lane's premise directly: the disease's "long survival with metastatic disease" is normally asserted narratively. Here it becomes a bounded number from retained counts.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers`:

```
rg -n -i "endpoint|discordance|relative survival|competing risk|disease.specific" research/ --glob '!.git' -l | head -40
git ls-files | rg -i "endpoint|discord|survival|competing" | head -60
rg -n -i "frechet|fréchet|hoeffding|joint distribution bound|without local recurrence|metastasis without|recurrence-free.*metastasis.*same patients" --glob '!.git' | head -30
rg -n -i "b_min|discordant cell|2x2|two-by-two" research/ --glob '!.git' | head -20
```

plus direct reads of `research/manuscripts/endpoint/emc-endpoint-discordance.json`, `research/manuscripts/emc-relative-survival.json`, `research/manuscripts/emc-mortality-decomposition.json`, `research/modalities/emc-ipd-survival.json`, the headers of `emc_endpoint_alternatives.py` and `emc_ipd_survival.py`, and `research/data/emc-clinical-registry.json`.

**What is already established (I am not re-running any of it):**

| Existing work | What it settled |
|---|---|
| `emc-endpoint-discordance.json` (D1) | ORR vs DCR on the *identical* 47 advanced patients: 12.8% vs 89.4%, 76.6 pp apart. This is a **response**-endpoint discordance, in the advanced/trial setting. |
| `emc_endpoint_alternatives.py` / `.json` | Design-side: the 6-month PFS null's provenance, operating characteristics, patient cost, natural-history gap. About *nulls and designs*, not event co-occurrence. |
| `emc-relative-survival.json` | Ederer II excess mortality on published summary survival; competing share of deaths. |
| `emc-mortality-decomposition.json` | Disease-specific vs other-cause **death** counts on the same patients (Masunaga localised: 9 vs 4). A cause-of-death split, not a recurrence/metastasis relation. |
| `emc_ipd_survival.py` | Guyot reconstruction instrument built; **only one curve admitted** (`stacchiotti2013_pfs_anthracycline`, n=11). The largest series (SEER n=270) is 403-blocked. So the time-to-event route is effectively closed at present. |
| `coverage_uncertainty.py` | Fréchet bounds **exist in this repository** — applied to **HLA allele coverage** in the neoantigen paper. Never applied to a clinical endpoint. |

**Confirmed not replayed** from `CLOSED-WORK.md`: no clinical conditional-recurrence checkpoint re-proposal, no RT/IPD synthesis, no trial-discoverability work, no new cohort invented, no Pazopanib/anthracycline/sunitinib/CTARC/Wagner route retried, no SEER-parameter calibration of EMC, no re-fetch of GSE4303/GSE28866, no restricted-review recreation. Every input below is already committed in the tree; **I retrieved nothing over the network.**

**Novelty statement:** the co-occurrence of *local recurrence, distant metastasis and disease death within the same patients* is nowhere bounded or estimated in this tree. That is the gap this computation fills.

---

## Method / inputs

**Input file (read-only, committed):** `/home/user/Rare-cancers/research/data/emc-clinical-registry.json`, object `registry.cohorts`, at frozen commit `92abbcb905cacf07f14b238db50d1b98f6590374`.

**Primary sources behind the admitted rows** (registry citation block, both open access, both marked `provenance: primary`):
- `masunaga2025` — Masunaga T, Tsukamoto S, Nagano A, et al. *The role of radiotherapy and chemotherapy in extraskeletal myxoid chondrosarcoma.* J Orthop Surg Res 2025. DOI `10.1186/s13018-025-06245-6`, PMCID `PMC12398172`. Japanese National Bone & Soft Tissue Tumour Registry, 2002–2022.
- `chiusole2020` — Chiusole B, Le Cesne A, Rastrelli M, et al. Front Oncol 2020;10:828. DOI `10.3389/fonc.2020.00828`, PMID `32612944`, PMCID `PMC7308468`.
- (reported but **refused** for the bound) `meisKindblom1999` — Am J Surg Pathol 1999. PMID `10366145`.

**Admissibility rule, applied by the program and not by me:** a cohort enters only if `pool == true`, `provenance == "primary"`, **and both endpoints carry the identical denominator**. A cohort whose two endpoints have different denominators is **refused, never reconciled** — different denominators mean a different patient set and the joint bound is undefined. 12 of 14 cohorts were refused; the refusal list is printed in the output.

**Estimands, per cohort, at that cohort's own follow-up horizon:**
- `D = p_A − p_B` — risk difference on the same patients. **Exactly identified** by the marginals.
- `b = #(A and not B)` — **partially identified**; Fréchet bounds `b ∈ [A − min(A,B), A − max(0, A+B−n)]`.
- `b/A` — share of patients with event A who never had event B; bounded below.

**Uncertainty, three distinct kinds, kept apart:**
1. **Wilson score 95%** on each marginal proportion (ordinary binomial sampling).
2. **Conservative paired Wald 95% CI on D.** Because `b − c = A − B` is fixed by the marginals, the point estimate is exact and only the variance is unidentified: `Var = [(b+c) − (A−B)²/n]/n²`, and `b+c` is evaluated at its **maximum admissible value** (overlap minimal), giving the widest interval over every joint consistent with the data. Declared as a Wald approximation, not an exact interval.
3. **Exact one-sided 95% Clopper–Pearson lower confidence limit** on `b_min/n`. Valid and conservative: the CP lower limit is monotone increasing in the count, and true `b ≥ b_min`, so the limit computed from `b_min` is never above the one the true count would give.

**Environment:** Python `3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]`, scipy `1.17.1`, numpy `2.4.6`, statsmodels absent. Script written to and run from `/tmp/claude-0/w16/` — **outside the repository**.

---

## Result

### A · Distant metastasis vs local recurrence (same patients, same denominator)

| Row | Cohort (source) | n | med. FU (mo) | Metastasis | Local recurrence | Risk diff (95% CI, conservative) | Fréchet: met **without** LR (count) | ≥ % of cohort | CP95 lower limit | **≥ % of metastatic pts** | Grade |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | Masunaga 2025, localised surgical | 134 | 38 | 39 (29.1%; Wilson 22.1–37.3) | 16 (11.9%; Wilson 7.5–18.5) | **+17.2 pp (6.7 to 27.6)** | **[23, 39]** | 17.2% | 12.0% | **59.0%** | PRIMARY |
| A2 | Chiusole 2020, curative-intent | 49 | not reported | 20 (40.8%; Wilson 28.2–54.8) | 14 (28.6%; Wilson 17.8–42.4) | +12.2 pp (−10.8 to 35.3) | **[6, 20]** | 12.2% | 5.5% | **30.0%** | PRIMARY |

### B · Distant metastasis vs disease-specific death (same patients, same denominator)

| Row | Cohort | n | med. FU (mo) | Metastasis | Disease death | Risk diff (95% CI, conservative) | Fréchet: met **without** disease death | ≥ % of cohort | CP95 lower limit | **≥ % of metastatic pts** | Grade |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | Masunaga 2025, localised surgical | 134 | 38 | 39 (29.1%) | 9 (6.7%; Wilson 3.6–12.3) | **+22.4 pp (13.0 to 31.8)** | **[30, 39]** | 22.4% | 16.6% | **76.9%** | PRIMARY |

### What these numbers say

**A1 is the substantive finding.** In the largest admissible EMC cohort, **no joint distribution whatsoever** — not perfect nesting, not any correlation — can place fewer than **23 of 39 metastatic patients (59.0%)** outside the set of patients with a documented local recurrence. The exact 95% one-sided lower confidence limit for that fraction of the whole cohort is **12.0%**. In EMC, local failure and distant failure are substantially **decoupled events**: the majority of metastases in this cohort occurred in patients whose primary site was never recorded as having recurred. This is a property of the endpoints as measured, established without any assumption about their dependence.

**A2 replicates the direction independently** (≥30% of metastatic patients, CP95 lower limit 5.5% of the cohort) — but note honestly that A2's **risk-difference CI crosses zero** (−10.8 to 35.3). The count bound and the risk difference are different claims: the bound is arithmetic on the observed cohort, and the CP limit is its sampling statement; the RD CI is a separate, weaker question that n=49 cannot answer. A2 corroborates A1; it does not independently establish it.

**B1 quantifies the lane's premise.** At a median 38 months, **at least 30 of 39 metastatic patients (76.9%)** had not died of EMC. That is the "long survival with metastatic disease" fact stated as a bound from counts rather than as narrative — and it is a direct, source-traceable reason why a mortality endpoint discriminates poorly at trial-length horizons in this disease. It is *not* a prognosis and *not* a survival estimate: it is a statement about the study's own horizon.

**Rows deliberately not produced:** UNKNOWN for the upper half of every bound (the joint is genuinely unidentified above `b_min`), UNKNOWN for the *ordering in time* of the two events (the registry holds no sequence data — see Limitations), and UNKNOWN for all 12 refused cohorts.

---

## Validation evidence

**RUN.** One command, exit code preserved:

```
cd /tmp/claude-0/w16 && python3 emc_endpoint_cooccurrence_bounds.py > out.json; echo "EXIT=$?"
EXIT=0
```

Environment as above (Python 3.11.15, scipy 1.17.1, numpy 2.4.6).

### Falsification checks — all four RUN

**F1 · Reverse-direction negative control (the primary falsifier).** The same machinery, same cohorts, run to bound *local recurrence without metastasis*. If the positive bound were an artifact of the arithmetic rather than of the data, it would come out positive in both directions. Verbatim:

```
"rows": [
 {"cohort": "Localised at diagnosis, surgically treated",
  "min_recurrence_without_metastasis_pct_of_cohort": 0.0, "informative": false},
 {"cohort": "European two-institution series (Chiusole)",
  "min_recurrence_without_metastasis_pct_of_cohort": 0.0, "informative": false}]
```

**PASSES.** The bound vanishes in the direction the data does not support. The method is capable of returning null and does return null.

**F2 · Counterfactual flip, run.** The bound is strictly positive **iff** reported metastasis exceeds reported local recurrence in the same patients. Re-running with recurrence set to the observed metastasis count returns `0.0` for both cohorts. So the flip condition is explicit and testable: had Masunaga reported ≥39 local recurrences instead of 16 (or Chiusole ≥20 instead of 14), this result would be null.

**F3 · A real cohort where the direction reverses, reported not hidden.** Meis-Kindblom 1999, the **longest** follow-up in the registry (median 108 months): recurrence **48.2% (40/83)** vs metastasis **46.1% (35/76)** — recurrence marginally *higher*. Its denominators differ, so it is inadmissible for the bound and the program refused it, but its direction is the opposite of A1/A2. This is exactly what differential ascertainment over follow-up length predicts, and it is a genuine constraint on how far A1 generalises. Reported as a hit against the finding, not as support for it.

**F4 · Cross-implementation check, run.** My count-scale `frechet_intersection` was checked against this repository's **independent** frequency-scale implementation `research/modalities/coverage_uncertainty.py::intersection_bounds` on 5 cases including the degenerate `(1,1,1)` and the forced-overlap `(5,5,6)` → `[4,5]`. `"all_agree": true`.

**Additional checks run:** the exact Clopper–Pearson limits were re-derived independently by pure-`math.comb` bisection on the binomial tail with no scipy — `cp95_lower_limit_crosscheck_bisection` matches `cp95_lower_limit_on_that_pct` on every row (12.0, 5.5, 16.6). Key arithmetic verified by hand: 39−16=23, 23/134=17.2%, 23/39=59.0%; 20−14=6, 6/49=12.2%, 6/20=30.0%; 39−9=30, 30/134=22.4%, 30/39=76.9%.

**Write isolation verified:** `git rev-parse HEAD` = `92abbcb905cacf07f14b238db50d1b98f6590374` (unchanged); `git status --porcelain` shows only `?? research/autonomy/opus-capacity-campaign-20260908/`, the coordinator's pre-existing campaign directory, which I did not create or modify. No git write command was issued.

**PROPOSED (NOT RUN):** integration into the repository's test tiers; regeneration of any committed artifact; any figure. None attempted — write isolation forbids it.

---

## Limitations

1. **The bound is a floor, never an estimate.** True `b` lies anywhere in `[23, 39]` (A1). Nothing here identifies where. Reporting the midpoint would be invention.
2. **No temporal ordering.** The registry holds event *occurrence*, not event *sequence*. "Metastasis without documented local recurrence" is a statement about the follow-up window, not a claim that metastasis came first. A patient could recur after the data cut.
3. **Ascertainment, not biology, may drive the direction.** Local recurrence requires surveillance of the primary site; metastasis is often what brings a patient back. F3 shows the direction reversing in the longest-follow-up series. A shorter horizon plausibly under-counts local recurrence relative to metastasis, which biases A1's bound **upward** — this runs *in favour of* the finding, so it is the limitation that matters most.
4. **Median follow-up 38 months (A1) is far shorter than EMC's natural history.** Both endpoints are censored, and not equally. This is a reading at the study's horizon, not a lifetime statement.
5. **A2 is corroborative only.** Its risk-difference CI includes zero and its follow-up is unreported.
6. **Two cohorts, both localised/curative-intent, one Japanese registry and one European two-institution series.** No pooling was attempted — the populations are not exchangeable and the repository's own policy forbids merging time-anchored data. n=134 and n=49 stand separately.
7. **Selection effects are inherited whole.** Registry and referral-institution series are not population samples.
8. **The Wald interval on D is asymptotic.** At n=49 that approximation is weak; the exact CP limits are the interval to trust.
9. **What this cannot claim:** no clinical recommendation; no statement about surveillance intervals, imaging schedules, margins, radiotherapy or any treatment; no efficacy, safety, selectivity or therapeutic-window claim; no prognosis for any patient; no surrogate-endpoint *validation* (showing two endpoints are decoupled is not validating either one). No new patients were created — 183 patient-records across two published cohorts, counted once.
10. **No EMC calibration from generic SEER parameters** was performed, and none of the closed/blocked sources was re-approached.

---

## Stop condition

**Set:** one executed computation with real numeric output, stated uncertainty, a *run* falsification check, and stated limits — or an evidence-backed statement that the retained data cannot support one.

**MET.** One computation executed at exit code 0 against committed primary data, producing bounded numeric results with three distinct kinds of uncertainty, four falsification checks all actually run (one of which, F3, returns a genuine hit against the finding's generality and is reported as such), and an explicit limits section. The answer is **not** null: A1 is informative and its floor is attained.

---

## Tool-call and wall-clock count actually used

**13 tool calls** (all `Bash`; no network retrieval, no subagents, no writes to the repository). **Wall clock ≈ 9 minutes** (~01:52 → 02:01 UTC). Both inside the ~40 min / ~40 call target.

---

## Next concrete action

**One successor, and it is a data-retrieval task rather than a method task:** obtain the **cross-tabulation** for the Masunaga 2025 localised cohort — the 2×2 of local recurrence against distant metastasis, and the sequence of events. The full text is open access at `PMC12398172` (CC-BY-NC-ND-4.0) and is already recorded in the registry as `verified: true`, so a full-text read of its results tables and supplementary material would either (a) print the joint directly, collapsing `[23, 39]` to a point, or (b) confirm it is unpublished, in which case the bound is the best available answer and should be written up as such. That read requires an egress route to PMC, which `CLOSED-WORK.md` records as historically blocked — so the honest framing is that the successor is **route-limited, not method-limited**, and the `ci-escape-hatches` Actions runner is the named route to try, once, by whoever owns that lane.

A second, lower-value successor within this lane: apply the same bound to `recurrence` vs `metastasis` in the `ussc2022` (n=60) and `drilon2008` (n=87) series if their second endpoint can be extracted onto a matching denominator — that would raise the admitted cohort count from 2 to 4 and let the direction be tested against follow-up length, which F3 identifies as the finding's main open flank.
