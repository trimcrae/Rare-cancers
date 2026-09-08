<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:23:21Z UTC
     agent id ad738b6935829b6c6 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ad738b6935829b6c6.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

All work done on a scratch copy; live tree untouched. Report below.

---

## Worker

**W13g** — lane 13 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in my environment independently confirms a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 03:12:26 UTC 2026` · `date -u` **end**: `Tue Sep  8 03:18:03 UTC 2026` (report drafted after).

`git rev-parse HEAD` **start**: `98a0833f1ede2cf9cef13790388260567a32e868` · **end**: `c81236b90c7905caa2e75a57b332ad33f2c10d02`. HEAD moved during my run (coordinator collecting sibling reports). I did not assume that harmless: after the move I re-compared all six files I read or mutated against the live tree with `cmp` — all six are **byte-identical** to my scratch baseline, so no input I measured changed underneath me.

`git status --porcelain` **start**: 8 untracked `reports/W*.md` files under `research/autonomy/opus-capacity-campaign-20260908/reports/` (coordinator's, not mine). **end**: **empty**. I created, moved and deleted nothing in the repository and ran no git write operation.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start of run — the four long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy` and `JAVA_TOOL_OPTIONS` are elided at the end only, and only because they repeat the same host list verbatim; nothing else is altered):

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

The end-of-run capture is identical (same call, same output).

## Question

W13f produced a count: 5 exposed artifacts, 6 `pool: false` sources inside pooled figures, 0 enforced. A count is not actionable. My question: **for each of those 11 items, what exactly is the field, which gate reads it, what does that gate assert and not assert, and what is the smallest input change that makes a published value wrong while every one of the 18 preflight `--check` rows still exits 0 — demonstrated, not asserted?**

Open because W13f measured *absence of a cross-file comparison* but never measured *what survives*. "No gate compares them" and "a wrong number ships green" are different claims, and only the second tells an owner what it costs to do nothing. I did not author, land or propose landing any guard, test or gate change.

## Prior-work check

Commands run (all read-only, from `/home/user/Rare-cancers`):

- `grep -n -- '--check' scripts/preflight.sh` → located the 18-row shell loop at lines **847–864** and the only two other `--check` invocations (`systems/systems_check.py`, `research/manuscripts/emc_systems_map_check.py`, lines 609/627). The 18 rows are the loop entries; that is the set my dispatch names.
- `grep -ln <artifact> <each of the 18 scripts>` for all five exposed artifacts, the mortality inputs file and the registry.
- `for n in site_curation rt_bed systemic_therapy_pooling mortality_decomposition relative_survival emc-clinical-registry validate-registry; do grep -c "$n" scripts/preflight.sh; done`.
- `git ls-files | grep -i -E '<artifact>'` per artifact, to find generators and test files.
- `git ls-files -z | xargs -0 grep -ln -E 'emc_rt_bed_reappraisal|emc-rt-bed-reappraisal|emc_relative_survival|emc-relative-survival'`.
- `grep -rl "rt-bed\|rt_bed" --include='test_*.py' .` and the same for relative-survival.

Read in full as required: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, W13f's report in full, and `systems/POLICY-evidence.md` front-matter and §§2–2.5. W13e was read via W13f's transcription of its finding plus the campaign brief; **I did not open W13e's own file** — that is a gap in my prior-work check and I record it rather than imply otherwise. I read `scripts/tier-budgets.json` and `scripts/validate-registry.mjs` directly rather than relying on W13f's quotation of them, and one of those direct reads **corrects W13f's cost framing** (see R5).

**CLOSED-WORK items confirmed not replayed**: no network, no source fetch, no PUB-EMC-CLASSIFICATION, no Brenca/Hofvander/Pazopanib/Sunitinib/Wagner/CTARC route, no `GSE4303`/`GSE28866`, no NR4A Perspective, no patient or specimen identity work. I did not re-run W13f's `check_pool_flag_divergence_is_written_down.py` and make no use of its 30-row output as evidence.

**Where I differ from W13f**: two of its five "exposed, unenforced" artifacts turn out to be **defended against hand edits** by checks W13f did not look for (R2, A1 and A3). W13f's claim was about the *pool-flag* axis and remains correct on that axis; its report is nonetheless read as "5 unenforced artifacts", and that reading is wrong. I show which two, and with what.

## Method / inputs

Scratch copy per dispatch: `tar --exclude=./.git -cf - . | (cd /tmp/claude-0/w13g && tar -xf -)` → 611 MB. **Every mutation and every `--check`, `node` and `pytest` invocation below ran with cwd `/tmp/claude-0/w13g`.** Nothing ran against `/home/user/Rare-cancers` except read-only `grep`/`sed`/`cat`/`git rev-parse`/`git status`. I did not run `scripts/preflight.sh`.

| Input | Path | Role |
|---|---|---|
| The 18 rows | `scripts/preflight.sh` lines 847–864 | the gate set under test |
| My runner | `/tmp/claude-0/w13g/run18.sh` (transcribed verbatim from those lines) | runs all 18, prints each real exit code |
| Registry | `research/data/emc-clinical-registry.json` | `registry.cohorts[*].{sourceId,n,pool,contextReason}` |
| Registry gate | `scripts/validate-registry.mjs` | preflight gate 10 — **not** one of the 18 |
| Policy | `systems/POLICY-evidence.md` §§2.1–2.5 | what `pool: false` means |
| Tier ceilings | `scripts/tier-budgets.json`, `scripts/tier_budget.py` | costing, read directly |
| Artifacts | the five in R2, plus `research/manuscripts/emc-mortality-decomposition-inputs.json` | the fields under test |

Tools: `python3` = `/usr/local/bin/python3`; `node`; `pytest 9.1.1` at `/root/.local/bin/pytest` (a uv tool — `python3 -c "import pytest"` **fails**, which is why W13f reported no pytest; the binary on `PATH` works and I used it). No network. No paid API. No GPU.

## Result

### R1 — Baseline: 16 of the 18 rows are green on the scratch copy; 2 are red for a `.git` reason, before any mutation (`PRIMARY`)

```
0   research/manuscripts/submission_tables.py --check
0   research/manuscripts/claim_coverage.py --check
0   research/manuscripts/submission_citations.py --check
0   research/manuscripts/submission_metrics.py --check
0   research/manuscripts/aso_sequence_manifest.py --check
0   research/manuscripts/aso_journal_tables.py --check
0   research/modalities/aso_offtarget_duplex_energy.py --check
0   research/manuscripts/submission_packet.py --check
0   research/manuscripts/vaccine_path_tables.py --check
1   research/manuscripts/aso_archive_manifest.py --check-archive
1   research/manuscripts/aso_deposit_drift.py --check
0   research/modalities/emc_condensate_report.py --check
0   research/modalities/atr_hrd_sarcoma_series.py --check
0   research/modalities/single_slot_identity.py --check
0   research/modalities/instrument_census.py --check
0   scripts/trigger_scan.py --check
0   scripts/citation_debt.py --check
0   scripts/news_match.py --check
```

**I am reporting this rather than working around it.** The two red rows print `STALE: the archive inventory would change` and `the declared deposit drift is not the measured one` — they enumerate the deposit from Git-tracked state, and my dispatch mandates a scratch copy made with `tar --exclude=./.git`, so they cannot be green here. I therefore **cannot** demonstrate "all 18 exit 0"; I demonstrate the strictly weaker and fully honest claim: **every mutation below leaves all 18 exit codes byte-identical to this baseline — the 16 green rows stay green and the 2 environmentally-red rows stay red with the same message.** No mutation is hiding behind a row that was already red. Whether those two are green on the writer's real tree is **UNKNOWN** to me and I did not run them there.

### R2 — The five exposed artifacts, field by field (`PRIMARY`)

**0 of the 18 rows names any of the five artifacts.** `grep -ln` across all 18 scripts returns nothing for `emc-site-curation.json`, `emc-rt-bed-reappraisal.json`, `emc-systemic-therapy-pooling.json`, `emc-mortality-decomposition.json`, `emc-relative-survival.json` or `emc-mortality-decomposition-inputs.json`. Two of the 18 name the *registry*: `submission_citations.py` and `aso_archive_manifest.py` (see R3). **`scripts/preflight.sh` contains zero occurrences of `site_curation`, `rt_bed`, `systemic_therapy_pooling`, `mortality_decomposition`, `relative_survival` or `emc-clinical-registry`** — measured by `grep -c`, all six returned `0`.

| # | Artifact · exact field | Members incl. `pool:false` | Rows of the 18 that read it | Generator `--check`? | Test file? | What *is* asserted | What is **not** asserted | Smallest input change that ships a wrong value green |
|---|---|---|---|---|---|---|---|---|
| A1 | `research/modalities/emc-site-curation.json` → `.pooled_extremity_fraction.extremity_strict.{events=194,denom=271,percent=71.6,ci95_lo=65.9,ci95_hi=76.6}` and `.extremity_inclusive.{229,271,84.5,79.7,88.3}` | `bishop2019` (`.series[2].source_id`) | **0** | **yes** (`emc_site_curation.py`, 2 occurrences) — but preflight runs it **0** times | **yes**, `research/modalities/tests/test_emc_site_curation.py`, 9 tests incl. `test_the_committed_artifact_matches_the_generator` and `test_context_rows_are_never_pooled_into_any_fraction` | the artifact reproduces from its generator; each series' site table sums to its own n; the two extremity definitions differ | **any relation to the registry.** `bishop2019 n=41` here is an independent transcription from the paper | **DEMONSTRATED (Demo 1)** — change `registry.cohorts[5].n` 41→82. The artifact's own key `⚠_these_denominators_DIFFER_from_the_registry_cohorts_AND_BOTH_ARE_RIGHT.bishop2019` = *"the registry cohort and the paper's site breakdown are both over n=41"* becomes **false**, and the pooled `denom=271` no longer reconciles with the registry |
| A2 | `research/modalities/emc-rt-bed-reappraisal.json` → `.consistency.fixed_effect_pooled.{log_effect=-1.4108, point=0.24396, ci95=[0.0818,0.7278], se_log=0.5577, z=-2.5296, p_two_sided=0.01142}` | `bishop2019` (`.consistency.studies[1].source_id`) | **0** | **yes** — and **nothing in the repository runs it** | **NONE** — `grep -rl "rt-bed\|rt_bed" --include='test_*.py'` returns nothing | *nothing runs*, so nothing is asserted at commit time | everything | **DEMONSTRATED (Demo 2)** — flip the sign of `fixed_effect_pooled.log_effect` and set `point` to `4.0991`. The published direction reverses (RT protective → RT harmful) with every study's `log_effect`, `se_log` and `weight_fraction` untouched |
| A3 | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` → `.analyses.A2_objective_response_cytotoxic_chemotherapy.pool` | `drilon2008` | **0** | **yes** (6 occurrences) — preflight runs it **0** times | **yes**, `research/manuscripts/tests/test_emc_systemic_therapy_pooling_check.py`, 7 tests named `test_the_committed_artifact_currently_reproduces`, `test_check_refuses_a_hand_edited_pooled_proportion`, `…_confidence_bound`, `…_integer_count`, `…_the_do_not_hand_edit_promise_itself` | by their names, hand edits to the pooled proportion, its CI and its counts are refused; I ran the file and all 7 pass at baseline | any relation to the registry's `pool` flag for `drilon2008` | **not a value hole.** A value edit is caught (see R4 caveat). The live hole is flag-side: **DEMONSTRATED (Demo 5)** — the registry's justification for excluding `drilon2008` can be deleted outright with every gate green |
| A4 | `research/manuscripts/emc-mortality-decomposition.json` → `.cross_series.5_year.competing_share_of_deaths_pct_median = 58.6` (and `.10_year… = 57.1`, `pairings_total/coherent/impossible/undefined`) | 5-yr: `china2016`, `seer270_2022`, `uMich2023`, `drilon2008`, `japan2003`; 10-yr: `bishop2019`, `drilon2008`, `japan2003` | **0** | **NO** — `grep -c -- '--check' emc_mortality_decomposition.py` = **0** | **yes**, 19 tests — but **none is a reproduction test**; they exercise the decomposition *functions* and two provenance/sanity properties of the artifact | the decomposition maths; that the committed headline is not negative or impossible; that quoted registry strings still exist as substrings | that the committed `cross_series` medians are what the generator produces | **DEMONSTRATED (Demo 4)** — change the 5-year median 58.6 → 31.4 (in-band, so the impossible-value guard is untouched). **19/19 tests pass** |
| A5 | `research/manuscripts/emc-relative-survival.json` → `.convergence.relative_survival_competing_share_pct_median = 23.0` (with `_range=[12.1,45.4]`, `_series_pooled=8`) | `drilon2008`, `japan2003`, `seer270_2022`, `uMich2023`, `china2016` (only `meisKindblom1999` is `pool:true`) | **0** | **NO** — 0 occurrences of `--check`, no `argparse` at all | **NONE** | nothing | everything | **DEMONSTRATED (Demo 3)** — change the median 23.0 → 61.0 |

**Correction to W13f, stated plainly**: two of the five (A1, A3) *are* defended against a hand edit of the published number, by `test_the_committed_artifact_matches_the_generator` and `test_the_committed_artifact_currently_reproduces` respectively. W13f's claim was specifically that no gate compares them **to the registry's `pool` flags**, and that claim survives intact for all five. But the five are not equally exposed, and an owner triaging from the count alone would mis-spend. The real ordering is: **A2 and A5 have no value guard of any kind** (A5 has not even a generator `--check` to run), **A4 has 19 tests and none of them regenerates**, and **A1/A3 are value-safe and flag-blind only**.

**Second correction, and the most actionable single fact in this report**: `research/modalities/emc_rt_bed_reappraisal.py` **already has a working `--check`** — its docstring at line 54 says `python3 research/modalities/emc_rt_bed_reappraisal.py --check    # fail if the artifact drifted` — and **nothing in the commit loop runs it**. This is verbatim the incident pattern `scripts/preflight.sh` documents against itself three times in its own comments (lines 736, 761–765, 779, 789: *"a `--check` that already existed and that nothing in the commit loop ran"*, *"NOTHING RAN IT: `--check` appears nowhere in this script"*). It is the same defect, on a fourth file, uncaught.

### R3 — The six `pool: false` sources, and what the only registry-aware gate asserts (`PRIMARY`)

All six live at `research/data/emc-clinical-registry.json` → `registry.cohorts[i].{sourceId, n, pool, contextReason}`:

| i | `sourceId` | `n` | `contextReason` | Read by any of the 18? | Read by any gate at all? |
|---|---|---|---|---|---|
| 5 | `bishop2019` | 41 | `population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)` | **no** | `validate-registry.mjs` only |
| 9 | `seer270_2022` | 270 | `population-overlap; percentage-only` | **no** | same |
| 10 | `drilon2008` | 87 | `percentage-only` | **no** | same |
| 11 | `uMich2023` | 44 | `population-overlap` | **no** | same |
| 12 | `japan2003` | 42 | `different-endpoint` | **no** | same |
| 13 | `china2016` | 40 | `percentage-only` | **no** | same |

(The other four `pool:false` rows — `remiszewski2025` ×3 at i=6,7,8 and `treatments.systemicEvidence[7] palmerini2022trobsultrarare` — appear in no pooled figure, per W13f R3, which I did not re-derive.)

**Which of the 18 touch the registry, and how.** Two name the path and **neither reads `registry.cohorts`**:

- `research/manuscripts/submission_citations.py` line 118 reads it as `CURATED = [(…"emc-clinical-registry.json", **"registry.citations"**), …]` — the *bibliographic* subtree, keyed by PMID. It never opens `registry.cohorts` and never touches `pool`.
- `research/manuscripts/aso_archive_manifest.py` line 320 lists the path as a **deposit membership pattern** under `retrieval_records`. It asserts the file is in the archive, not what is in it.

**So the entire enforcement surface for `pool` is `scripts/validate-registry.mjs`, which is preflight gate 10 and is not one of the 18 rows.** It reads `pool` in exactly two places:

- line 88 — `if (c.pool === false && !c.contextReason) warns.push(…)`
- line 113 — `if (c.pool !== false && c.populationKey) { … warns.push("shares populationKey+stratum … risk of double-counting in the pool") }`

**Both are `warns`, not `errors`.** The script exits non-zero only at line 163–166, `if (errors.length)`. Its success line (170) prints the warning count and exits 0. Therefore:

- **What the gate asserts about a `pool:false` row**: nothing that can fail a build. It asserts `events <= denom`, that disease and other-cause deaths share a denominator and do not exceed n, and that citations resolve — all real, none `pool`-specific.
- **What it does not assert**: that a `pool:false` row carries a reason at all (warn only); that any artifact outside this one file honours the flag; that `n` agrees with any downstream transcription of it; that a cohort's exclusion reason is still true.

### R4 — Five mutations actually run; five times the gates stayed green (`PRIMARY`)

Two were required. I ran five because each isolates a different hole, and three of them cost one call each.

| Demo | Mutation (scratch only) | 18 rows | Other gates run | Verdict |
|---|---|---|---|---|
| **1** | `registry.cohorts[5].n` (`bishop2019`) 41 → 82 | **identical to baseline** (16×0, 2×1) | `node scripts/validate-registry.mjs` → **0**; `emc_site_curation.py --check` → **0**; `pytest` over the three artifact test files → **35 passed** | registry and the published site pool now disagree about the same cohort's size, with a committed sentence asserting they agree. Nothing notices. |
| **2** | `emc-rt-bed-reappraisal.json` `fixed_effect_pooled.log_effect` −1.4108 → +1.4108, `point` 0.24396 → 4.0991 | **identical to baseline** | `validate-registry.mjs` → **0**; **`emc_rt_bed_reappraisal.py --check` → exit 1**, `DRIFT: …emc-rt-bed-reappraisal.json differs from a fresh build of …emc_rt_bed_reappraisal.py` | the published RT effect is reversed in direction. The guard that catches it **exists and is never run.** |
| **3** | `emc-relative-survival.json` `.convergence.relative_survival_competing_share_pct_median` 23.0 → 61.0 | **identical to baseline** | no `--check` exists (0 occurrences); no test file exists | nothing in the repository can detect it. |
| **4** | `emc-mortality-decomposition.json` `.cross_series.5_year.competing_share_of_deaths_pct_median` 58.6 → 31.4 | **identical to baseline** | `pytest research/manuscripts/tests/test_emc_mortality_decomposition.py` → **19 passed in 0.03s**; `submission_metrics.py --check` → **0**; `claim_coverage.py --check` → **0** | a headline median moves by 27 points past 19 dedicated tests. |
| **5** | delete `contextReason` from `cohorts[10]` (`drilon2008`) and `cohorts[12]` (`japan2003`) | **identical to baseline** | `validate-registry.mjs` prints two `WARN … is context (pool:false) but gives no contextReason` and **exits 0** | the stated reason for excluding a cohort from every pool can be deleted with the build green. |

**Restoration, verified**: after every demo the mutated file was restored from a byte copy and re-verified. Final check, all six files, `cmp` against the live tree at HEAD `c81236b9`:

```
IDENTICAL research/data/emc-clinical-registry.json
IDENTICAL research/modalities/emc-site-curation.json
IDENTICAL research/modalities/emc-rt-bed-reappraisal.json
IDENTICAL research/manuscripts/endpoint/emc-systemic-therapy-pooling.json
IDENTICAL research/manuscripts/emc-mortality-decomposition.json
IDENTICAL research/manuscripts/emc-relative-survival.json
```

**Caveat I am recording rather than smoothing**: for A3 I ran `test_emc_systemic_therapy_pooling_check.py` and observed 7 passes at baseline (inside the 35), and I read its test *names*. **I did not read its body and did not run a mutation against it.** My statement that A3 is defended against hand edits is an inference from names plus a passing baseline, not a demonstrated refusal. Label it `SECONDARY`. The same caveat applies to A1's `test_the_committed_artifact_matches_the_generator` — though there I did run `emc_site_curation.py --check` under a registry mutation and saw exit 0, which shows only that the *registry* is outside its scope, not that a value edit would fail.

### R5 — What a minimal enforcement must assert, and what it actually costs (`PRIMARY` for the ceilings, `PROPOSED (NOT RUN)` for every design)

I wrote no enforcement and propose landing none. What follows is the price list.

**Measured ceilings**, `python3 scripts/tier_budget.py` run at `/tmp/claude-0/w13g`, **exit 0**:

```
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
```

**The single most important costing fact, and it corrects the premise handed to me.** I read `scripts/tier-budgets.json` directly. `commit-loop` covers exactly `["scripts/tests", "research/autonomy/tests", "systems/tests"]`. **None of the five artifacts lives in those directories.** Their natural test homes are `research/modalities/tests` (A1, A2 → **modalities**, 7247/7500, **253 slots**) and `research/manuscripts/tests` (A3, A4, A5 → **paper-guards**, 966/1000, **34 slots**). The 1497/1500 writer-side figure binds **only** a guard placed in `scripts/tests` — and `tier-budgets.json` itself says of `paper-guards`: *"This is the tier to spend on."* It also records that commit-loop tests are now **opt-in (`PREFLIGHT_TESTS=1`) and out of the default loop**. So the honest answer to "can this be afforded" is: **for four of the five holes the commit-loop ceiling is not the constraint, and invoking it would be the wrong argument.** I am not raising any ceiling and not recommending one be raised.

**The cheaper fact: three of the five holes cost zero test functions.** The 18 rows are entries in a shell `for` loop in `scripts/preflight.sh`. `tier_budget.py` counts `def test_*` functions in three directories; a loop entry is neither. Adding a row is **0 against every ceiling**, at a cost of one subprocess per commit.

| Hole | Minimal enforcement must assert | Cost | Constraint that actually binds |
|---|---|---|---|
| **A2** `emc-rt-bed-reappraisal` | *nothing new* — run the `--check` that is already written and already correct (Demo 2: it exits 1 on the mutation). One 19th row in the 847–864 loop. | **0 test functions**, one `python3` subprocess | none. This is the repository's own documented lesson applied to a fourth file. |
| **A5** `emc-relative-survival` | that the committed artifact reproduces from `emc_relative_survival.py`. Requires *writing* a `--check` (the generator has no `argparse`), then one loop row. | **0 test functions**; one generator `main()` change (owner's call) | generator-authoring effort, not budget |
| **A4** `emc-mortality-decomposition` | same shape: a `--check` on a generator that has none, then one loop row. Its 19 tests already cover the maths; what is missing is *this artifact is that generator's output*. | **0 test functions** | same |
| **A1/A3** flag-side, and the general case | that where an artifact publishes an aggregate whose declared members include a registry `pool:false` source, the artifact names that source and the flag it departs from. `emc-site-curation.json` already does this and is the worked example. | **1–2 functions** if a test, **0** if a `--check` row | if placed in `research/manuscripts/tests` → paper-guards, 34 slots free. If in `scripts/tests` → commit-loop, **3 slots** on the writer, which is the wrong tier for a manuscript-subject guard by `tier-budgets.json`'s own rule |
| **The registry side** | that `pool:false` without `contextReason` is an **error**, not a `warn` (Demo 5). One-word change at `validate-registry.mjs` line 88: `warns.push` → `errors.push`. | **0 test functions**; gate 10 already runs | ⚠ **would this turn the tree red today?** Unknown — the live registry has a `contextReason` on every `pool:false` row, so it should not, but I did not run it and do not assert it. Owner must verify before touching it. |

**Cross-file assertion, stated so an owner can accept or reject it without me**: *given a committed artifact publishing an aggregate figure, and given that artifact's own declared member list, every member the registry marks `pool: false` must be named in a written justification inside that artifact together with the flag it departs from.* This asserts **disclosure, not membership** — it decides nothing about whether the inclusion is right, which is the owner's per-pool-vs-per-source reading and not mine. Its hard part is not the rule but *finding the aggregates*: W13f's heuristic version produced 13 false positives across 3 files and missed A5 entirely. A version fit to place needs an explicit committed manifest of `(artifact, node, member field)`, which is maintenance, and which cannot be designed before the reading is settled.

**One policy question I am raising and not answering**: `POLICY-evidence.md` §2.4 says *"Time-anchored survival (5-yr, 10-yr DSS/OS) is never merged into one number — denominators represent different follow-up."* A4 publishes `cross_series.5_year` and `.10_year` medians and A5 publishes a median over 8 series at fixed horizons. These are medians of a derived *competing share*, not merged survival, so §2.4 may simply not reach them. **Whether it does is a policy reading, it belongs to the policy owner, and I make no finding.**

## Limitations

- **I could not demonstrate "all 18 exit 0."** Two rows are red at baseline on the mandated `.git`-less scratch copy. I demonstrated the weaker claim (all 18 exit codes unchanged, 16 green rows stay green). Their behaviour on the writer's real tree is UNKNOWN.
- **A3's defence is inferred from test names plus a passing baseline**, not from a demonstrated refusal. So is A1's. Marked `SECONDARY` in R4.
- Mutations were reversible edits to a scratch copy; they show what a *gate* fails to detect. They say nothing about whether the committed values are correct — **every committed value I touched was restored and verified byte-identical, and I found no evidence that any of them is wrong.**
- I did not read W13e's own report, only W13f's transcription of it.
- I did not re-derive W13f's membership map (R3's "appears in a pooled figure" column) — that is W13f's `PRIMARY`, carried forward as `SECONDARY` here. My own `PRIMARY` covers fields, gate readership, assertions and the five mutations.
- Every enforcement in R5 is `PROPOSED (NOT RUN)`. I wrote no guard, changed no gate, edited no ceiling, and touched no live file.
- **No clinical claim.** The reversed RT effect in Demo 2 is a deliberately falsified number in a throwaway copy; it is not a finding about radiotherapy. There is no wet lab and nothing here bears on efficacy, safety or clinical readiness.

## Stop condition

Set before starting: **stop when (a) all five exposed artifacts and all six `pool:false` sources have an exact field, a gate-readership determination made by reading what each gate opens, and a named minimal input change; (b) at least two of those changes are demonstrated by real mutation with real exit codes showing the gates green; (c) the enforcement cost is priced against the measured tier ceilings; and (d) the scratch copy is verified restored and the live tree verified untouched.**

**MET.** (a) 11/11 mapped. (b) five demonstrated, not two. (c) priced, with a correction to the premise — the commit-loop ceiling binds only one of the five candidate placements. (d) `cmp` clean on all six files, `git status --porcelain` empty at end. Returning now.

## Tool-call and wall-clock count actually used

**34 tool calls** (33 `Bash`, 1 `Bash` for briefs), **~6 minutes** of tool wall clock (`03:12:26Z` → `03:18:03Z`) plus drafting. Well under the ~40-call / ~40-minute target.

## Next concrete action

**For the preflight owner, one line and no budget argument required**: add `"research/modalities/emc_rt_bed_reappraisal.py|RT BED reappraisal|--check"` as a 19th entry to the loop at `scripts/preflight.sh:847–864`. The `--check` is already written, already correct, and Demo 2 shows it exits 1 on a reversed published effect that all 18 current rows pass. It costs **0 test functions against every tier ceiling**. This is the fourth recurrence of the exact defect that script's own comments document three times; the first three were found by incident, this one by measurement, and it is still unfixed. **I have not made this change** — it is a gate change and belongs to its owner.

**Second, and sequenced after it**: A5 (`emc-relative-survival.json`) has no `--check`, no test and a published median that Demo 3 moved from 23.0 to 61.0 with nothing objecting. Giving `emc_relative_survival.py` the same `--check` its sibling generators have, then a 20th loop row, closes it for 0 test functions. A4 is the same shape. Only after those three does the cross-file `pool`-flag guard become the binding question — and that one should not be built until the owner answers whether the flag is a property of a registry row or of a source, because the manifest it needs has a different shape under each answer.
