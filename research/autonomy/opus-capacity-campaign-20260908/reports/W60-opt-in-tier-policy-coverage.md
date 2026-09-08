<!-- collected 2026-09-08T04:57:32Z by campaign coordinator; agent id a0e68dd1ccf8cfd04; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a0e68dd1ccf8cfd04.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

All work is done and scratch is deleted. Report follows.

## Worker

**W60**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: evidence-contract enforcement — W48's named successor. Successor question: do the opt-in pytest tiers cover the predicates W48 measured as UNENFORCED at commit-gate 10?

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in the environment corroborates it — no variable names a model. The coordinator must extract the served model from the transcript.

Start `date -u`: `Tue Sep  8 04:47:32 UTC 2026`; start HEAD `8a667406e875ae99c7d50347b2e895a177fcb048`; `git status --porcelain` **empty**.
End `date -u`: `Tue Sep  8 04:53:44 UTC 2026`; end HEAD `fcb36d3c651223d90b98c0cb64169bb106e6e060`; `git status --porcelain` **empty**. HEAD moved under me (coordinator collection); every file I measured is a tracked source file outside the campaign directory, and per the brief's measured invariant no commit since `92abbcb` touches anything outside that directory.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start of run, complete):

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
GLOBAL_AGENT_NO_PROXY=(same list as no_proxy)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy/truststore flags only)
NO_PROXY=(same list as no_proxy)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=(same list as no_proxy)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

No variable names a model. (Re-grepped at end: `CLAUDE_EFFORT=medium`, `CLAUDE_CODE_VERSION=2.1.42`, `CLAUDE_CODE_ENTRYPOINT=remote`, runner `release-ba76006550-ext` — unchanged, still no model.)

## Question

W48 measured 13 of 31 decidable POLICY-evidence predicates as UNENFORCED, and explicitly scoped that to "no check reachable by a bare commit-time run of gate 10", leaving **UNKNOWN** whether the opt-in pytest tiers cover them, because it ran none. My bounded question: **for §2.1(3), §2.2, §2.3-across-study, §2.4, §2.6 and §2.7 — locate the covering pytest modules, run them, and determine by construction whether each passing test could actually fail on a violation of the policy predicate it is credited with.**

It is open because every claim in the enforcement chain so far is a source reading: W30c read the source and named the tests; W48 measured the validator but ran no pytest. Nobody had executed the tests or mutated what they guard.

## Prior-work check

```
$ ls research/autonomy/opus-capacity-campaign-20260908/reports/ | grep -iE 'W30c|W48'
   W30c-policy-sections-without-gates.md, W48-policy-enforcement-falsifiability.md   (both read)
$ grep -rn "def <each test name W30c cites>" --include='*.py' . | grep -v opus-capacity
   → all six modules located (table below)
$ grep -rn -iE 'population-overlap|populationKey|contextReason|2\.3' --include='test_*.py' . | grep -v opus-capacity
   → exactly ONE relevant hit repository-wide: test_locoregional_eligibility.py:64, a pool:false
     fixture inside test_pool_false_cohorts_never_enter_the_headline. No test asserts that an
     overlapping cohort must BE marked pool:false.
$ grep -rn -iE "I2|I²|heterogene|inverse.variance|random.effect|cross.population" \
      research/manuscripts/tests/test_endpoint_logic.py research/manuscripts/tests/test_endpoint_producers_check.py
   → 0 hits.
$ grep -rln "def wilson" --include='*.py' --include='*.mjs' . | grep -v opus-capacity
   → 15 files each define their own wilson().
```

I am not replaying: W48's validator mutation sweep (I ran no validator mutation), W30c's static map, W30b's §2.6/§2.7 conformance audit, the registry shape census (W30d), the campaign resolution rate. I read and referenced no `W25-*` file. I did not run `scripts/preflight.sh`, and I never invoked `atr_hrd_sarcoma_series.py`.

## Method and inputs

- Read in full: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `systems/POLICY-evidence.md` (386 lines), `reports/W48-policy-enforcement-falsifiability.md` (289 lines). Read targeted: `reports/W30c-…md` §5.2 enforcement table; the six test modules; the three modules under test; `scripts/preflight.sh` tiering (`:550-552`, `:576-578`, `:939`, `:962`); `scripts/tier-budgets.json` header.
- **Execution substrate:** `cp -a /home/user/Rare-cancers /tmp/claude-0/w60/repo` (983 MB; disk floor respected, 19 GB free). Every pytest run and every mutation happened there. I issued no command with the live repository as the working directory for pytest, and no git write anywhere.
- Runner: `pytest` on PATH = `/root/.local/bin/pytest`, **pytest 9.1.1** (per W29f; `python3 -m pytest` was never used). Generator re-runs used the system `python3`.
- Mutation harness: a 20-line literal-replacement helper (`mut.py`) that asserts its pattern occurs exactly once, plus a pristine snapshot of each mutated file for restoration. **12 mutations + 1 direct API probe + 1 baseline.** Each mutation injects one policy violation, runs the credited test module, records the real exit code, then restores.
- **Every mutation is a synthetic test fixture, never data**, and none was applied to the clinical registry (which I did not touch at all).

## Result

### R-0. Tier reachability — confirmed by reading the gate, not by inference

`scripts/preflight.sh:550-552`: `RUN_TESTS=0`, set to 1 only by `PREFLIGHT_TESTS=1` or `PREFLIGHT_FULL=1`. `:576-578`: `RUN_MODALITIES=0`, set to 1 only by `PREFLIGHT_MODALITIES=1` or `PREFLIGHT_FULL=1`. **All six modules are opt-in.** W48's scoping sentence is therefore correct as written, and everything below is coverage that a bare commit does not run. `PRIMARY`.

### R-1. Baseline — do the credited modules run green today?

`cd /tmp/claude-0/w60/repo && pytest -q <7 modules>` → **`146 passed in 21.69s`, exit 0.** Per module: `PRIMARY`

| Module | Tests | Result |
|---|---|---|
| `research/modalities/tests/test_locoregional_eligibility.py` | 9 | passed, exit 0 |
| `research/modalities/tests/test_emc_radiotherapy_contradiction.py` | 27 | passed, exit 0 |
| `research/modalities/tests/test_emc_recurrence_timing.py` | 13 | passed, exit 0 |
| `research/modalities/tests/test_emc_surgical_quality.py` | 14 | passed, exit 0 |
| `research/modalities/tests/test_emc_ipd_survival.py` | 20 | passed, exit 0 |
| `research/manuscripts/tests/test_endpoint_logic.py` | 46 | passed, exit 0 |
| `research/manuscripts/tests/test_endpoint_producers_check.py` | 17 | passed, exit 0 |

No test was skipped, deselected or disabled at any point. Nothing was repaired.

### R-2. The verdict table — every row decided by an executed mutation

| # | Policy predicate | Covering test (file:line) | Green today? | Catches the violation? | Verdict |
|---|---|---|---|---|---|
| M1 | **§2.1(3)** outcome ≠ inclusion criterion | `test_locoregional_eligibility.py:30` | yes (9/9) | **yes** — guard replaced by `if False:` → `1 failed, 8 passed`, **exit 1** | **COVERED-AND-FALSIFIABLE** |
| M2 | **§2.2** Wilson score interval (not normal approx) | `test_locoregional_eligibility.py:89` (3 closed-form params) | yes | **yes** — `wilson()` degraded to normal approximation → `3 failed, 6 passed`, **exit 1**; also `test_emc_surgical_quality.py` reproduce-check **exit 1** | **COVERED-AND-FALSIFIABLE** (one implementation only — see R-3) |
| M3 | **§2.2** *denominator-weighted* pool | none found | — | **no** — pooled p̂ silently replaced by the unweighted mean of per-cohort rates → `23 passed`, **exit 0** | **GENUINELY-UNENFORCED-ANYWHERE** |
| M4 | **§2.3 across-study** overlapping series → `pool:false` + `contextReason` | none exists | — | **no** — two cohorts sharing `populationKey="jpreg"`, both `pool:true`, were summed to **38/211** with `cohorts_excluded={}`; `pool()` contains no overlap logic and no test asserts one | **GENUINELY-UNENFORCED-ANYWHERE** |
| M5/M6 | **§2.4** time-anchored survival never merged | `test_emc_recurrence_timing.py:146` (`test_nothing_is_pooled`), `test_emc_surgical_quality.py:145` | yes | **no** — a merged 5-yr DSS field (`five_year_dss_merged_across_cohorts`, `merged_from:[masunaga2025, chiusole2020]`) injected into the generator: **M5** (artifact stale) → exit 1 *from the reproduce-check only*; **M6** (same violation, artifact properly regenerated) → **`13 passed`, exit 0** | **COVERED-VACUOUSLY** |
| M7 | §2.4-adjacent: cross-anchor comparison refused | `test_emc_recurrence_timing.py:59` | yes | **yes** — `_check_no_cross_anchor_comparison()` forced to return `[]` → `1 failed`, **exit 1** | **COVERED-AND-FALSIFIABLE** (not one of W48's 13; reported for completeness) |
| M10 | **§2.6(h)** census shares the corpus denominator | `test_endpoint_logic.py:274` | yes | **yes** — `distinct_ncts_with_a_four_cell_block += 3` → `1 failed, 45 passed`, **exit 1** | **COVERED-AND-FALSIFIABLE** |
| M12 | **§2.6(g)** strata were not pre-specified | `test_endpoint_logic.py:484` | yes | **yes** — a `stratum` string added to the frozen protocol → `1 failed, 45 passed`, **exit 1** | **COVERED-AND-FALSIFIABLE** |
| M11 | **§2.6(c)** no cross-population pool, no I², no inverse-variance weighting | none found | — | **no** — `{"pooledProportion":0.317,"ci95":[…],"I2":0.71,"weighting":"inverse-variance","pooled_across":["ovarian","sarcoma","melanoma"]}` injected into `endpoint-corpus.json` → `test_endpoint_logic.py` **46 passed, exit 0**. `test_endpoint_producers_check.py` failed, but *only* as drift: `FAIL: … does not re-derive. Differing keys: ['C9_cross_disease_pooled_response']` | **COVERED-VACUOUSLY** (drift-only; no assertion inspects for pooling, I² or weighting) |
| M8 | **§2.7** risk table mandatory | `test_emc_ipd_survival.py:129` | yes | **yes** — both the `raise ValueError` and the `no_numbers_at_risk_table` quality failure removed → `1 failed, 19 passed`, **exit 1** | **COVERED-AND-FALSIFIABLE** |
| M9 | **§2.7** digitization provenance required | `test_emc_ipd_survival.py:142` | yes | **yes** — `no_digitization_provenance` failure removed → `1 failed, 19 passed`, **exit 1** | **COVERED-AND-FALSIFIABLE** |
| — | **§2.7** labelled as a reconstruction | none found (grep only, **NOT PROBED by mutation**) | — | UNKNOWN | **UNKNOWN** |
| — | §2.2 heterogeneity reported as a range | **NOT PROBED** | — | — | **UNKNOWN** |
| — | §2.1(2) integer-ness (W48's E-VAC row) | **NOT PROBED** (outside my dispatched list) | — | — | **UNKNOWN** |

**Summary against W48's 13 UNENFORCED predicates.** Of the six areas dispatched: **7 predicates are COVERED-AND-FALSIFIABLE in an opt-in tier** (§2.1(3), §2.2-Wilson, §2.6(g), §2.6(h), §2.7-risk-table, §2.7-provenance, plus the §2.4 anchor guard), **2 are COVERED-VACUOUSLY** (§2.4 "never merged", §2.6(c)), **2 are GENUINELY-UNENFORCED-ANYWHERE** (§2.2 denominator-weighting, §2.3 across-study), and **3 are UNKNOWN** (not probed). W48's UNENFORCED-at-gate-10 label survives for all of them *at the commit gate*; it is **downgraded to "covered in an opt-in tier"** for the seven falsifiable rows.

### R-3. The scope limit that travels with the Wilson row — measured

`test_wilson_matches_known_values_including_the_boundaries` is a real closed-form control and it does bite. But **15 files define their own `wilson()`**: `paralogue_pocket_asymmetric_read.py`, `hla_coverage.py`, `aso_parent_null.py`, `nr4a_paralogue_dynamics.py`, `hormone_partner_map.py`, `emc_locoregional_eligibility.py`, `nr4a3_tcip_reach.py`, `emc_endpoint_alternatives.py`, `emc_fusion_partner_pooling.py`, `emc_systemic_therapy_pooling.py`, `placebo_arm_calibration.py`, `orr_dcr_reread.py`, `emc_endpoint_discordance.py`, `aso_reagent_coverage.py`, `emc_mortality_decomposition.py`. The closed-form test guards **one** of them; `test_emc_surgical_quality.py:157` (`test_the_wilson_helper_is_the_repositorys_one_wilson`, an identity assertion `sq.wilson is loco.wilson`) binds **one more module** to that guarded implementation. The other thirteen are unexercised by this control. This is W30c's "one-fact-many-places" line, now with the denominator measured. `PRIMARY`.

### R-4. NEW FINDING — the reproduce-check is drift detection, and M5/M6 measures exactly how far it goes

The same §2.4 violation produced **exit 1** when the artifact was stale and **exit 0** when the artifact was regenerated from the mutated generator. The only thing that fired in M5 was `test_the_artifact_reproduces_from_its_generator` (`test_emc_recurrence_timing.py:28` → `check()` at `emc_recurrence_timing.py:333-341`), which compares `json.load(OUT)` to `build()`. It cannot distinguish a policy violation from any other edit, and a violator who changes the generator and reruns it passes. This is a direct, executed instance of W45's "regenerate-then-check escape" class, and it is the reason M11's `producers_check` failure does **not** upgrade §2.6(c) to covered.

The content-level assertion that is supposed to carry §2.4 — `test_nothing_is_pooled` — checks only `"⛔_nothing_is_pooled" in doc` and that the serialized blob contains neither the literal string `"pooled_median"` nor `"combined_median"`. A merged time-anchored survival figure under any other key name passes. `PRIMARY`.

⚠ Method note on M6, recorded because it nearly produced a wrong verdict: my first regeneration attempt ran the module as a script, which executes `main()` at import-time **before** the appended mutation is defined, so the artifact was rewritten unmutated and the test still failed — which would have read as "caught". The honest result required regenerating through `m.main([])` after import (`REGEN_RC=0`, injected key confirmed present in the artifact by grep) — only then did the suite go green.

## Validation evidence

**RUN.** Environment: live repo `/home/user/Rare-cancers` read-only, HEAD `8a667406` → `fcb36d3c`; all execution in `/tmp/claude-0/w60/repo` (a `cp -a` copy, since deleted); `pytest 9.1.1` at `/root/.local/bin/pytest`; system `python3` for generators and the mutation helper. No network, no paid API, no GPU, no preflight, no validator run.

Baseline:
```
$ cd /tmp/claude-0/w60/repo && pytest -q <7 modules>
146 passed in 21.69s
EXIT=0
```

Mutation sweep, verbatim tails:
```
M1  2.1(3) guard removed                      → 1 failed, 8 passed   PYTEST_EXIT=1
M2  2.2 Wilson->normal approx (loco)          → 3 failed, 6 passed   PYTEST_EXIT=1
M2  2.2 Wilson->normal approx (surg. quality) → 1 failed, 13 passed  PYTEST_EXIT=1
M3  2.2 unweighted mean replaces weighted pool→ 23 passed            PYTEST_EXIT=0
M4  2.3 across-study probe: POOLED events/denom = 38 / 211  excluded= {}
M5  2.4 merged 5-yr DSS, artifact stale       → 1 failed, 12 passed  PYTEST_EXIT=1
      ERROR: emc-recurrence-timing.json does not reproduce from its generator
M6  2.4 merged 5-yr DSS, artifact regenerated → 13 passed            PYTEST_EXIT=0
M7  2.4 cross-anchor guard defanged           → 1 failed, 12 passed  PYTEST_EXIT=1
M8  2.7 risk table no longer mandatory        → 1 failed, 19 passed  PYTEST_EXIT=1
M9  2.7 digitization provenance not required  → 1 failed, 19 passed  PYTEST_EXIT=1
M10 2.6(h) census denominator broken          → 1 failed, 45 passed  PYTEST_EXIT=1
M11 2.6(c) pool+I2+inverse-variance injected  → 46 passed            PYTEST_EXIT=0
M11b same injection vs producers_check        → 1 failed, 16 passed  PYTEST_EXIT=1
      FAIL: research/manuscripts/endpoint/endpoint-corpus.json does not re-derive.
            Differing keys: ['C9_cross_disease_pooled_response']
M12 2.6(g) frozen protocol mentions strata    → 1 failed, 45 passed  PYTEST_EXIT=1
```

Tier gating, verbatim:
```
scripts/preflight.sh:550  RUN_TESTS=0
                    :551  [ "${PREFLIGHT_TESTS:-0}" = "1" ] && RUN_TESTS=1
                    :552  [ "${PREFLIGHT_FULL:-0}" = "1" ] && RUN_TESTS=1
                    :576  RUN_MODALITIES=0
                    :577  [ "${PREFLIGHT_MODALITIES:-0}" = "1" ] && RUN_MODALITIES=1
                    :578  [ "${PREFLIGHT_FULL:-0}" = "1" ] && RUN_MODALITIES=1
```

Write isolation:
```
$ git status --porcelain    # start: empty;  end: empty
$ diff -rq --exclude=.git /home/user/Rare-cancers /tmp/claude-0/w60/repo
   → differences are ONLY: coordinator-added campaign reports (W03j, W09j, W34c, W44, W49, W52–W55),
     the edited COMMON-BRIEF.md, and __pycache__/.pytest_cache entries. No tracked source file differs.
$ rm -rf /tmp/claude-0/w60 && ls /tmp/claude-0/    # w60 no longer listed — SCRATCH_DELETED
```

⚠ One honest caveat on isolation: the live tree's `.pytest_cache/v/cache/nodeids` and one `research/manuscripts/__pycache__/*.pyc` differ from my copy in a direction implying the live tree was touched *after* my `cp -a`. I issued no pytest command with the live tree as cwd and no git write; the live tree also carries a `.pyc` my copy lacks, which points at a **concurrent worker**, not at me. `git status --porcelain` is empty at both ends. I state this rather than assert an isolation I cannot fully prove.

**PROPOSED (NOT RUN).** The M6-equivalent for `endpoint_corpus` (mutate the producer, regenerate `endpoint-corpus.json`, re-run `producers_check`) — I did not execute it, so §2.6(c)'s COVERED-VACUOUSLY verdict rests on the *absence of any content assertion* (grep: 0 hits for I²/inverse-variance/cross-population in either endpoint test module) plus the M5/M6 demonstration of the escape on a different producer, not on an executed escape for this one. Also not run: mutations for §2.7 "labelled as a reconstruction", §2.2 heterogeneity-as-range, §2.1(2) integer-ness.

## Limitations

- **A caught mutation proves the test fails on *that* construction**, not that it would catch every violation of the predicate. M1, M8, M9 in particular are single-point mutations of a single branch.
- **"GENUINELY-UNENFORCED-ANYWHERE" is scoped** to gate 10 (W48, not re-measured) plus the seven modules W30c credits with coverage plus the repository-wide `test_*.py` greps quoted above. A check living somewhere I did not grep would be UNKNOWN, not absent.
- My 31-predicate mapping inherits W48's decomposition; I did not re-derive it, and I probed 12 of its rows, not all 31.
- **All coverage found is opt-in.** W41 additionally measured that `PREFLIGHT_FULL=1` — the only tier that runs both suites — currently fails a tier-budget test on this branch for reasons unrelated to any of this. So the tier carrying seven falsifiable guards is not currently green end-to-end on this branch, which I did not attempt to verify (I ran no preflight).
- Everything here is about **repository tooling**. Nothing is a clinical claim: no statement about any treatment's efficacy, safety, selectivity or therapeutic window, no patient-level inference, and no registry count or pooled rate restated as a clinical claim. The injected fixtures (a fabricated merged DSS, a fabricated cross-disease pooled proportion, a duplicated overlapping cohort) are **synthetic test fixtures, never data**, and every one was reverted; the live registry was never opened for writing.
- The M3 and M4 findings are **latent**: they bound what the tests could catch, not evidence that anything committed is mis-pooled. W30d measured the live registry as conforming.
- I authored no repair, patch, gate or test; weakened, relaxed or reordered no guard; skipped, deselected and disabled nothing.

## Stop condition

**Set up front:** return as soon as every dispatched predicate (§2.1(3), §2.2, §2.3-across-study, §2.4, §2.6, §2.7) has a covering-test location, a real baseline exit code, and a real mutation exit code deciding COVERED-AND-FALSIFIABLE / COVERED-VACUOUSLY / GENUINELY-UNENFORCED-ANYWHERE — with the live tree verified untouched and scratch deleted.

**Met.** 12 mutations + 1 API probe + 1 baseline executed; all six dispatched areas decided (three further predicates explicitly returned as UNKNOWN rather than guessed); live tree clean; scratch deleted.

## Tool-call and wall-clock count actually used

**33 tool calls** (all Bash), **~6.2 minutes** wall clock (`04:47:32Z` → `04:53:44Z`), plus report drafting. Well inside the ~40/~40 target; returning early rather than padding.

## Next concrete action

**One successor, bounded and executable:** settle §2.6(c) the way M5/M6 settled §2.4 — mutate `research/manuscripts/endpoint_corpus.py` itself to emit a cross-population pooled proportion with I² and inverse-variance weighting, regenerate `endpoint-corpus.json` through the producer's own write path, and re-run `test_endpoint_logic.py` + `test_endpoint_producers_check.py` on a `cp -a` copy. If it goes green, §2.6(c) moves from COVERED-VACUOUSLY-by-inference to COVERED-VACUOUSLY-by-execution and the row becomes a hard finding; if the producer needs the network it is honestly BLOCKED and should be recorded as such. The same run can cheaply add the three UNKNOWN rows (§2.7 "labelled as a reconstruction", §2.2 heterogeneity-as-range, §2.1(2) integer-ness at the pytest tier, which W48 measured as vacuous at the validator).

A second, for whoever owns `research/modalities/emc_locoregional_eligibility.py` — **not me, I am read-only and authored nothing**: `pool()` sums cohorts sharing a `populationKey` without comment (measured: 38/211, no exclusion), and no test anywhere asserts the §2.3 across-study rule. That is a routing note, not a patch; the diff is the owner's to write, and the honest test for it duplicates a `populationKey` across two `pool:true` cohorts.
