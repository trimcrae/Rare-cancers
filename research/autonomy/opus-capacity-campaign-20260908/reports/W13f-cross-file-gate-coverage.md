> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

## Worker

**W13f** — lane 13 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in my environment independently confirms a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 02:48:29 UTC 2026` · `date -u` **end**: `Tue Sep  8 02:57:29 UTC 2026`

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start of run):

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
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<proxy/truststore flags, elided: repeats the no_proxy list>
NO_PROXY=<same list as no_proxy>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same list as no_proxy>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

(Only the four long proxy-list variables are elided, and only where they repeat the `no_proxy` value verbatim. Nothing else is altered.)

**HEAD actually read — start**: `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`. **HEAD at end**: `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8`. Neither is the `92abbcb9…` frozen commit named in `COMMON-BRIEF.md`, and neither is W13e's `7d081218`. I checked the divergence rather than assuming it harmless: `git diff --name-only 3f5fc95d ce743d6a` lists **15 files, all of them under `research/autonomy/opus-capacity-campaign-20260908/`** (coordinator report collection). No file I measured — the registry, any artifact, any generator, any test, `scripts/tier_budget.py`, `scripts/tier-budgets.json` — changed during my run.

`git status --porcelain` was **empty at start and empty at end**. I wrote nothing into the Git tree. All my writes are under `/tmp/claude-0/w13f/`.

## Question

W13e established that nothing reads both `research/data/emc-clinical-registry.json` and `research/modalities/emc-site-curation.json`, so the site pool's divergence from the registry's `pool` flags is unenforced whichever reading the owner picks. My question: **how wide is that hole across the whole tree — how many committed artifacts pool across registry sources with no gate comparing their membership to the `pool` flags, which `pool: false` cohorts actually appear inside pooled figures, and what is the smallest reporting-only check that closes the hole without deciding the reading?**

Open because W13d measured blast radius only over *consumers that read the registry*, and W13e measured only the one artifact W13d found. Neither measured artifacts that pool across registry sources **without opening the registry at all** — which turns out to be where most of the exposure is.

**I did not decide the per-pool-vs-per-source reading, did not author a pooling rule, and did not add, remove or reweight any cohort in any pool or denominator.** No clinical claim is made anywhere below.

## Prior-work check

Commands run and what they showed:

- `git ls-files | grep -E '\.(py|mjs|js|ts)$' | xargs grep -ln -i -E 'pool|wilson|weighted|meta.?analys|aggregate'` — ~300 files, used as the candidate frame rather than as a finding.
- Per-sourceId `git ls-files -z | xargs -0 grep -l "<sourceId>"` for all 12 registry sourceIds — this is a *mention* map, not a read map, and I treated it only as a candidate list. Every enforcement conclusion below comes from reading what code opens.
- `git ls-files | grep -E '\.(py|mjs|js|ts|sh|yml|yaml)$' | xargs grep -ln 'emc-clinical-registry'` → **18 files**, then each inspected for an actual `open()`/`readFileSync`/`read_text` of that path and for any read of the `pool` field.
- Read in full as required: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `systems/POLICY-evidence.md` (§§2.1–2.4, 2.7, 5 in detail), and the W13c/W13d/W13e/W16b reports at `research/autonomy/opus-capacity-campaign-20260908/reports/`. **Note: the dispatch prompt named these as `reports/W13c-…` etc.; that path does not exist. They are under `research/autonomy/opus-capacity-campaign-20260908/reports/`.** W13d's report, which W13e recorded as absent from the filesystem, **is present at this HEAD** and I read it directly rather than via a dispatch summary.

**CLOSED-WORK items confirmed not replayed**: no PUB-EMC-CLASSIFICATION, no Brenca route, no patient/case/specimen identity work, no `GSE4303`/`GSE28866`, no NR4A Perspective, no source fetch of any kind. **No network was used.** I did not re-run W16b's Fréchet computation, W13e's `both_readings.py`, or W13d's validator. I did not re-derive the two site-curation readings — W13e owns that and I neither endorse nor repeat either.

**What is genuinely new here versus W13d/W13e**: W13d found "one artifact, two figures" of exposure by searching *registry consumers*. That frame misses every artifact that pools registry sources from hard-coded transcriptions. Measuring by *published membership* instead of by *registry reads* raises the exposed set from 1 artifact to 4–5, and shows `bishop2019` is **not** the only `pool: false` source inside a pooled figure.

## Method / inputs

| Input | Path | Role |
|---|---|---|
| Registry | `/home/user/Rare-cancers/research/data/emc-clinical-registry.json` | `registry.cohorts` (14 rows), `treatments.systemicEvidence` (10 rows) — the `pool` flags under test |
| Policy | `/home/user/Rare-cancers/systems/POLICY-evidence.md` (386 lines) | §§2.1–2.4, 2.7(d), 5 — read before any pooling statement |
| Gate | `/home/user/Rare-cancers/scripts/validate-registry.mjs` | preflight gate 10 |
| Tier tool | `/home/user/Rare-cancers/scripts/tier_budget.py`, `/home/user/Rare-cancers/scripts/tier-budgets.json` | the counting method for §4 |
| Artifacts under review | all `git ls-files '*.json'` outside `research/autonomy/`, plus their generators and tests | the exposure survey |
| Prior reports | `research/autonomy/opus-capacity-campaign-20260908/reports/W13{,b,c,d,e}-*.md`, `W16b-*.md` | framing, non-duplication |
| My scratch | `/tmp/claude-0/w13f/scan_pooled.py`, `scan2.py`, `check_pool_flag_divergence_is_written_down.py` (170 lines, sha256 `4b17f83641f5b5e27af8313568a11b93e8514602f10f4f6161c4ca0369f79e84`), `tiertest/test_pool_flag_divergence_is_written_down.py` | the only code I authored |

Tools: `python3` = `/usr/local/bin/python3` (system), `git`, `grep`, `awk`. **`pytest` is not installed under the system `python3`** in this container, so no pytest run was attempted and no pytest result is claimed anywhere.

## Result

### R1 — Enforcement: **zero** gates, tests, validators or workflows compare any pooled artifact's membership against the registry's `pool` flags (`PRIMARY`)

18 committed `.py`/`.mjs`/`.js`/`.sh`/`.yml` files *name* the registry path. Reading what each actually opens, and whether it reads the `pool` field:

| File | Opens the registry? | Reads `pool`? | Also opens a pooled artifact? | Cross-file `pool` comparison? |
|---|---|---|---|---|
| `scripts/validate-registry.mjs` | yes (`readFileSync(REGISTRY)`, line 32 — the **only** file it opens) | yes (line 113) | **no** | **no** |
| `research/meta/meta-analysis.mjs` | yes (line 22) | yes (line 32, `filter(c => c.pool !== false)`) | writes its own `results.json` | **no** — obeys the flags by construction |
| `research/modalities/emc_locoregional_eligibility.py` | yes (lines 202–203) | yes (line 158) | **no** — `emc-site-curation.json` appears only as a *string value* at line 62 (`"resolved_by"`), never opened | **no** |
| `research/manuscripts/emc_mortality_decomposition.py` | yes (line 427) | **no** | its own OUT | **no** — registry read is for verbatim provenance strings |
| `research/manuscripts/tests/test_emc_mortality_decomposition.py` | yes (lines 214–215) | **no** | yes, `emc-mortality-decomposition.json` (line 245) | **no** — `verify_provenance` is substring presence |
| `research/manuscripts/submission_citations.py` | yes (line 118/155) | **no** | yes, `emc-fusion-partner-pooling.json` | **no** — compares `citations` coverage |
| `research/modalities/tests/test_emc_ipd_survival.py` | yes (lines 260–261) | **no** (only `curve.get("pool")` on its own readings file) | its own OUT | **no** — asserts citation keys resolve |
| `research/hypotheses/enumerate-drugs.mjs` | yes (line 151) | **no** | — | **no** |
| `scripts/emc_km_admissibility.py`, `scripts/emc_km_figure_fetch.py`, `scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py` | yes | **no** | — | **no** |
| `research/modalities/emc_site_curation.py`, `emc_ipd_survival.py`, `research/manuscripts/emc_systemic_therapy_pooling.py`, `emc_fusion_partner_pooling.py`, `aso_archive_manifest.py`, `scripts/method-watch.mjs`, `research/manuscripts/tests/test_fusion_partner_prose_matches_its_artifact.py` | **NO — registry path appears only inside string literals / docstrings; these open only their own OUT artifact** | n/a | — | **no** |

Only **three** files read the `pool` field at all, and each is either the validator (registry-only) or a generator applying the flags to its *own* output. **No committed code anywhere reads a pooled artifact and the registry's `pool` flags together.** W13e's finding is not local to the site file — it is the general case.

### R2 — Exposed artifacts: **4 hand-verified, 1 boundary case** (`PRIMARY` for membership as committed)

Exposed = a committed artifact publishing a pooled/summed/averaged figure whose declared membership includes a source the registry marks `pool: false`.

| # | Artifact | Figure | `pool: false` members included | Gate comparing to registry flags | Divergence written down? |
|---|---|---|---|---|---|
| 1 | `research/modalities/emc-site-curation.json` | `pooled_extremity_fraction` (`extremity_strict`, `extremity_inclusive`) | `bishop2019` | **none** | **YES** — key `⭐_why_bishop2019_is_pooled_HERE_and_pool_false_in_the_REGISTRY` |
| 2 | `research/modalities/emc-rt-bed-reappraisal.json` | `consistency.fixed_effect_pooled` (inverse-variance over `masunaga2025`, `bishop2019`, `paioli2021`) | `bishop2019` | **none** | **NO** |
| 3 | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` | `analyses.A2_objective_response_cytotoxic_chemotherapy.pool` (0/21 + 4/10 + 0/2) | `drilon2008` | **none** | **NO** |
| 4 | `research/manuscripts/emc-mortality-decomposition.json` | `cross_series.5_year` and `.10_year` (`competing_share_of_deaths_pct_median`, pairing counts, ranges) | 5-yr: `china2016`, `seer270_2022`, `uMich2023`, `drilon2008`, `japan2003`; 10-yr: `bishop2019`, `drilon2008`, `japan2003` | **none** | **NO** |
| 5 | `research/manuscripts/emc-relative-survival.json` | `convergence.relative_survival_competing_share_pct_median` over `relative_survival_series_pooled: 8` | `drilon2008`, `japan2003`, `seer270_2022`, `uMich2023`, `china2016` (only `meisKindblom1999` is `pool: true`) | **none** | **NO** |

**So the answer to "how wide" is: 5 committed artifacts publish a pooled/averaged figure containing at least one registry `pool: false` source, and 0 of the 5 are checked against the registry's flags by anything. Exactly 1 of the 5 writes its divergence down.**

Artifacts I checked and found **NOT exposed**, with the reason:

- `research/modalities/emc-locoregional-eligibility.json` — its generator reads the flags and records every exclusion verbatim (`"pool: false — population-overlap …"`, 9 rows × 2 outcomes). Correct by construction.
- `research/meta/results.json` (via `meta-analysis.mjs`) — filters on `c.pool !== false` before pooling.
- `research/modalities/emc-ipd-survival.json` — its `pooled` block declares `sources_pooled: ["stacchiotti2013anthracycline"]`, a single non-cohort source; the file emits `⛔_this_is_not_a_pool` elsewhere.
- `research/modalities/emc-prognostic-coefficients.json`, `emc-recurrence-timing.json`, `emc-surgical-quality.json` — each carries `⛔_nothing_is_pooled` / `⛔_nothing_here_is_pooled`.
- `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` — its pools use a different source namespace and its own `pool` field; no registry `pool: false` cohort enters them.

**Boundary case, flagged and not resolved by me**: `analyses.A7_the_pool_that_is_refused.arithmetic_if_taken` in `emc-systemic-therapy-pooling.json` publishes a computed value containing `drilon2008` while the artifact explicitly *refuses* that pool. By the rule as written it is a divergence; by intent it is a refusal on the record. Whether a refused-but-printed pool counts is a rule question, not mine.

### R3 — Every `pool: false` cohort with a `contextReason`, and where each nevertheless appears in a pooled figure (`PRIMARY`)

All nine `pool: false` cohort rows carry a `contextReason` (there is no `pool: false` row without one), plus one `treatments.systemicEvidence` row.

| Registry row | `sourceId` | `n` | `contextReason` (verbatim) | In a pooled figure at? |
|---|---|---|---|---|
| `cohorts[5]` | `bishop2019` | 41 | `population-overlap (US single institution; likely within SEER / US Sarcoma Collaborative)` | **emc-site-curation** (justified), **emc-rt-bed-reappraisal**, **emc-mortality-decomposition** (10-yr) |
| `cohorts[6]` | `remiszewski2025` | 156 | `population-overlap; percentage-only` | none found |
| `cohorts[7]` | `remiszewski2025` | 31 | `percentage-only` | none found |
| `cohorts[8]` | `remiszewski2025` | 26 | `different-endpoint` | none found |
| `cohorts[9]` | `seer270_2022` | 270 | `population-overlap; percentage-only` | **emc-mortality-decomposition** (5-yr), **emc-relative-survival** |
| `cohorts[10]` | `drilon2008` | 87 | `percentage-only` | **emc-systemic-therapy-pooling** (A2), **emc-mortality-decomposition** (5-yr + 10-yr), **emc-relative-survival** |
| `cohorts[11]` | `uMich2023` | 44 | `population-overlap` | **emc-mortality-decomposition** (5-yr), **emc-relative-survival** |
| `cohorts[12]` | `japan2003` | 42 | `different-endpoint` | **emc-mortality-decomposition** (5-yr + 10-yr), **emc-relative-survival** |
| `cohorts[13]` | `china2016` | 40 | `percentage-only` | **emc-mortality-decomposition** (5-yr), **emc-relative-survival** |
| `treatments.systemicEvidence[7]` | `palmerini2022trobsultrarare` | 3 | `population-overlap` | none found |

**`bishop2019` is NOT the only one — it is one of six.** `drilon2008`, `seer270_2022`, `uMich2023`, `japan2003` and `china2016` each appear in at least one pooled or averaged committed figure. Only `remiszewski2025` (all three rows) and `palmerini2022trobsultrarare` appear in none.

`n` is transcribed exactly as committed; **no unit determination is made or implied** — W13c owns that question. **Nothing in this table says any of these inclusions is wrong.** Four of the five `contextReason`s driving them are `percentage-only` or `different-endpoint`, which are *fitness-for-a-given-estimand* reasons, not double-counting reasons; whether they should travel to a different estimand in a different file is precisely the owner's call and I do not make it.

### R4 — The check, and what it actually flags: it flags **29 of 30**, with **1 OK**, exit 1 (`PRIMARY`)

The complete source is in Validation evidence below and at `/tmp/claude-0/w13f/check_pool_flag_divergence_is_written_down.py`. Its rule, in one line: *where a committed artifact publishes an aggregate figure whose own declared member list includes a source the registry marks `pool: false`, the artifact must carry an explicit written justification naming that source together with the flag it departs from.*

By construction it does not decide the reading, does not touch any pool or denominator, does not judge whether a justification is *good* (accepting text is not endorsing it), and never infers membership from prose — membership comes only from a list the artifact itself publishes.

**Actual run, exit code 1**, full row set:

| verdict | artifact | node | member |
|---|---|---|---|
| FLAG | `research/literature/emc-km-admissibility-2026-08-27.json` | `$` | `bishop2019`, `china2016`, `drilon2008`, `japan2003`, `seer270_2022`, `uMich2023` (6 rows) |
| FLAG | `research/manuscripts/emc-mortality-decomposition-inputs.json` | `$` | `bishop2019`, `china2016`, `drilon2008`, `japan2003`, `seer270_2022`, `uMich2023` (6 rows) |
| FLAG | `research/manuscripts/emc-mortality-decomposition.json` | `$.cross_series.10_year` | `bishop2019`, `drilon2008`, `japan2003` |
| FLAG | `research/manuscripts/emc-mortality-decomposition.json` | `$.cross_series.5_year` | `china2016`, `drilon2008`, `japan2003`, `seer270_2022`, `uMich2023` |
| FLAG | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` | `$.analyses.A2_objective_response_cytotoxic_chemotherapy.pool` | `drilon2008` |
| FLAG | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` | `$.analyses.A7_the_pool_that_is_refused.arithmetic_if_taken` | `drilon2008` |
| FLAG | `research/modalities/emc-ipd-survival.json` | `$` | `bishop2019`, `china2016`, `drilon2008`, `japan2003`, `seer270_2022`, `uMich2023` (6 rows) |
| FLAG | `research/modalities/emc-rt-bed-reappraisal.json` | `$.consistency` | `bishop2019` |
| **OK** | `research/modalities/emc-site-curation.json` | `$` | `bishop2019` |

**30 divergence rows: 1 written down, 29 not.** So the answer to "flags nothing or flags everything" is: **it flags almost everything, and the single row it passes is exactly the file W13e studied** — the one artifact in the repository that argued its divergence in writing is the one artifact the check clears.

**I am reporting this check's own errors rather than tuning them away** (tuning a guard until rows disappear is the failure mode `CLAUDE.md` §6 forbids):

- **False positives — 3 artifacts, 13 of the 29 flags.** `emc-km-admissibility-2026-08-27.json` (`$`), `emc-mortality-decomposition-inputs.json` (`$`) and `emc-ipd-survival.json` (`$`) each pair a root-level *work list* of candidate series with a root-level count key (`totals`, `curves_pooled`, `pooled_reference`). Those counts are censuses of curves/series, not pooled clinical estimates, and `emc-ipd-survival`'s real pooled block declares a single non-cohort source. The heuristic cannot tell a source *census* from a source *pool* at the document root.
- **False negative — 1 artifact.** `research/manuscripts/emc-relative-survival.json` is genuinely exposed (R2 row 5) and the check **misses it**: its `convergence` node publishes the median but declares its membership one level up, in the root `series` list, so no single node carries both.
- **Unresolved by rule, not by me**: the `A7_the_pool_that_is_refused` row (see R2 boundary case).

Net, against my hand-verified R2 set: the check catches 4 of the 5 real exposures, clears the 1 that is documented, and adds 13 spurious rows across 3 files. **A version of this that is safe to place would need its aggregate/member discovery replaced by an explicit committed manifest of pooled figures** — that is a design decision with a maintenance cost, and it belongs to whoever owns the tier, not to me.

### R5 — Tier and cost, by `tier_budget.py`'s own counting method (`PRIMARY`)

**Tier: `commit-loop`.** `scripts/tier-budgets.json` defines it as `["scripts/tests", "research/autonomy/tests", "systems/tests"]` — the pure-logic suites over committed repository data. The nearest existing neighbour is already there: `scripts/tests/test_no_hand_authored_json_has_a_duplicate_key.py`, a structural guard over this same registry file. It is not `paper-guards` (its subject is not a manuscript) and not `modalities` (its subject is not a science route).

**Cost: 2 test functions**, measured by re-using `tier_budget.py`'s own AST method (module-body `def test_*`, plus its `_shadowed` check) against a proposed module written to `/tmp/claude-0/w13f/tiertest/`: `test_every_pool_flag_divergence_is_written_down` (invokes the check, asserts exit 0) and `test_the_check_can_actually_fail` (the repository's "a guard that cannot fail is not a guard" convention). AST count **2**, shadowed **0**. A minimum-viable placement is **1**; 2 is the count that honours the negative-control convention.

**Headroom, stated both ways and not acted on**: this cloud checkout measures `commit-loop` at **1466/1500 across 102 files** (`python3 scripts/tier_budget.py`, exit 0). The owner's writer-side measurement is **1497/1500 across 105 files**. As the dispatch states, that gap is an expected source-base difference and **not** a `count_dir` malfunction — I make no claim about `count_dir`. 2 functions fit under either number (1468/1500 here; 1499/1500 there). **I did not raise any ceiling, did not place any file, and did not edit `tier-budgets.json`.**

## Validation evidence

**RUN** — all commands from `/home/user/Rare-cancers`, `python3` = `/usr/local/bin/python3` (system), no network, read-only on the tree.

1. Tier measurement:

```
$ python3 scripts/tier_budget.py
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
EXIT=0
```

2. The check, run against the current tree:

```
$ python3 /tmp/claude-0/w13f/check_pool_flag_divergence_is_written_down.py /home/user/Rare-cancers
registry sources with pool:false + contextReason (8): bishop2019, china2016, drilon2008, japan2003, palmerini2022trobsultrarare, remiszewski2025, seer270_2022, uMich2023
declared cross-source aggregates including one of them: 30
...
30 divergence rows: 1 written down, 29 NOT written down.
EXIT=1
```

3. Proposed test module counted by `tier_budget.py`'s own AST logic (module loaded from `scripts/tier_budget.py`, `_shadowed` invoked directly):

```
AST test functions in the proposed module: 2
shadowed: []
EXIT=0
```

4. Tree untouched: `git status --porcelain` empty at start and at end; `git diff --name-only 3f5fc95d ce743d6a` → 15 files, all under `research/autonomy/opus-capacity-campaign-20260908/`.

5. The check's complete source (170 lines, sha256 `4b17f83641f5b5e27af8313568a11b93e8514602f10f4f6161c4ca0369f79e84`), returned inline as required:

```python
#!/usr/bin/env python3
"""REPORTING-ONLY cross-file check.

Rule (one line): where a committed artifact publishes an aggregate figure whose OWN
declared member list includes a source the clinical registry marks `pool: false`, the
artifact must carry an explicit written justification naming that source together with
the flag it is departing from.

What this check does NOT do, by construction:
  * It does not decide whether pool membership is per-pool or per-source.
  * It does not add, remove, reweight or recompute any cohort, pool or denominator.
  * It does not judge whether a justification is GOOD. Accepting text is not endorsing it.
  * It never infers membership from prose: membership comes only from a list the artifact
    itself publishes as its members.

Exit 0 = no unwritten divergence.  Exit 1 = at least one.  Exit 2 = could not run.
"""
import json, os, re, subprocess, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
REGISTRY = os.path.join(ROOT, "research", "data", "emc-clinical-registry.json")

# A node is an AGGREGATE if it publishes a combined value ...
AGG_VALUE = re.compile(r'^(pool\w*|pool|events|denom|denominator|proportion\w*|percent\w*'
                       r'|weighted\w*|fixed_effect\w*|random_effect\w*|\w*_median|\w*_mean'
                       r'|\w*_total|totals?|\w*_sum|\w*_pooled|\w*_range)$', re.I)
# ... and it declares WHO is in it with one of these keys, as a list/dict of names.
MEMBER_KEY = re.compile(r'^(members?|included_sources?|sources?_pooled|pooled_sources?'
                        r'|cohorts?|series|studies|per_cohort|per_series|per_source'
                        r'|\w*_sources)$', re.I)

FLAG = re.compile(r'pool\W{0,4}false', re.I)


def load_registry():
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    pool_false, all_ids = {}, set()
    for c in reg.get("registry", {}).get("cohorts", []):
        all_ids.add(c["sourceId"])
        if c.get("pool") is False and c.get("contextReason"):
            pool_false.setdefault(c["sourceId"], set()).add(c["contextReason"])
    for c in reg.get("treatments", {}).get("systemicEvidence", []):
        all_ids.add(c["sourceId"])
        if c.get("pool") is False and c.get("contextReason"):
            pool_false.setdefault(c["sourceId"], set()).add(c["contextReason"])
    return pool_false, all_ids


def local_key_map(doc):
    """key -> sourceId, from any row the artifact itself labels with both."""
    m = {}
    def walk(n):
        if isinstance(n, dict):
            sid = n.get("sourceId") or n.get("source_id")
            if isinstance(sid, str):
                for kk in ("key", "id", "cohort_id", "series", "label", "name"):
                    if isinstance(n.get(kk), str):
                        m[n[kk]] = sid
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(doc)
    return m


def declared_members(node, ids, kmap):
    """Names the node itself lists as its members, resolved to registry sourceIds."""
    out = set()
    for k, v in node.items():
        if not MEMBER_KEY.match(str(k)):
            continue
        names = []
        if isinstance(v, list):
            for e in v:
                if isinstance(e, str):
                    names.append(e)
                elif isinstance(e, dict):
                    for kk in ("sourceId", "source_id", "key", "series", "id"):
                        if isinstance(e.get(kk), str):
                            names.append(e[kk]); break
        elif isinstance(v, dict):
            names.extend([n for n in v.keys() if isinstance(n, str)])
        for n in names:
            r = n if n in ids else kmap.get(n)
            if r is None:                      # tolerate stratum suffixes: masunaga2025_localized
                r = next((s for s in ids if n.split("_")[0] == s or n == s), None)
            if r in ids:
                out.add(r)
    return out


def _numeric_bearing(v):
    """The aggregate key must hold an actual computed value, not a table of records."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return True
    if isinstance(v, dict):
        return any(_numeric_bearing(x) for x in v.values())
    if isinstance(v, list):
        return any(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
    return False


def justified(blob, sid, window=400):
    """The artifact names this source within `window` chars of the flag it departs from."""
    for m in FLAG.finditer(blob):
        if sid in blob[max(0, m.start() - window): m.end() + window]:
            return True
    return False


def main():
    if not os.path.exists(REGISTRY):
        print("BLOCKED: no registry at", REGISTRY); return 2
    pool_false, ids = load_registry()
    files = [p for p in subprocess.run(["git", "-C", ROOT, "ls-files", "*.json"],
                                       capture_output=True, text=True).stdout.split()
             if not p.startswith("research/autonomy/")
             and p != "research/data/emc-clinical-registry.json"]
    rows = []
    for rel in files:
        try:
            doc = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
        except Exception:
            continue
        blob = json.dumps(doc, ensure_ascii=False)
        if not any(s in blob for s in ids):
            continue
        kmap = local_key_map(doc)
        # Collect every node that is an aggregate WITH its own declared member list.
        # Only the DEEPEST such nodes are reported: an outer container that merely
        # encloses them is not itself the figure.
        cands = []
        def walk(n, p):
            if isinstance(n, dict):
                has_val = any(AGG_VALUE.match(str(k)) and _numeric_bearing(n[k]) for k in n)
                has_mem = any(MEMBER_KEY.match(str(k)) for k in n)
                if has_val and has_mem:
                    cands.append((p, declared_members(n, ids, kmap)))
                for k, v in n.items():
                    walk(v, p + "." + str(k))
            elif isinstance(n, list):
                for i, v in enumerate(n):
                    walk(v, "%s[%d]" % (p, i))
        walk(doc, "$")
        inner = [c[0] for c in cands if len(c[1]) >= 2]
        for p, mem in cands:
            if any(q != p and q.startswith(p) for q in inner):
                continue                      # an enclosing container, not the figure
            if len(mem) < 2:
                continue
            for sid in sorted(mem & set(pool_false)):
                rows.append((rel, p, sid, "; ".join(sorted(pool_false[sid])),
                             justified(blob, sid)))
    rows = sorted(set(rows))
    bad = [r for r in rows if not r[4]]
    print("registry sources with pool:false + contextReason (%d): %s"
          % (len(pool_false), ", ".join(sorted(pool_false))))
    print("declared cross-source aggregates including one of them: %d\n" % len(rows))
    for rel, p, sid, reasons, ok in rows:
        print("%-4s %s\n       node %s\n       declares member %s -- registry pool:false (%s)"
              % ("OK" if ok else "FLAG", rel, p, sid, reasons))
    print("\n%d divergence rows: %d written down, %d NOT written down."
          % (len(rows), len(rows) - len(bad), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
```

**PROPOSED (NOT RUN)**: the two-function test module in `/tmp/claude-0/w13f/tiertest/` was written and AST-counted, but **never executed** — `pytest` is not importable under the system `python3` in this container, so it is **BLOCKED, not a pass**. No pytest result is claimed. The file was not placed in the tree.

## Limitations

- **The check is a heuristic over JSON shape, and it has measured errors in both directions** (R4): 13 false-positive flags across 3 files, 1 false negative (`emc-relative-survival.json`), 1 row whose status is a rule question. It is evidence about the size of the hole, **not** a check that is ready to be placed. Placing it as-is would put 29 flags into a gate, 13 of which are wrong.
- **"Pooled figure" has no committed definition, and I did not supply one.** I counted sums, crude proportions, inverse-variance combinations and cross-source medians as aggregates. Whether a cross-series *median of pairings* (`emc-mortality-decomposition`, `emc-relative-survival`) is "pooling" in the §2.2 sense is a rule question I raise and do not answer.
- **The `pool` flag is attached to a registry *row*, not to a *source*.** My R2/R3 matching is by `sourceId`, which is the only machine-readable link available; a source can carry `pool: true` on one row and `pool: false` on another (`masunaga2025` is `pool: true` twice; `remiszewski2025` is `pool: false` three times with three different reasons). The row-vs-source granularity is itself part of the reading question the owner owns, and my per-source matching is a measurement convention, not a ruling.
- **Four of the six implicated `contextReason`s are `percentage-only` or `different-endpoint`, not `population-overlap`.** Those are estimand-fitness reasons. Nothing here says that including such a source in a *different* estimand is an error; the finding is only that the divergence is unrecorded and unchecked.
- **`justified()` accepts any text pairing the sourceId with a `pool…false` token within 400 characters.** It measures that a divergence was *written down*, never that the writing is correct or sufficient. The single OK row is not an endorsement of the site file's argument, and W13e's §4 finding — that its counterpart set is UNKNOWN from committed fields — stands untouched.
- **W13d's ruling still governs**: `POLICY-evidence` §2.3/§5 require a `pool: false` row to carry a `contextReason` and nothing more. Nothing in this report is a policy violation by any artifact or any author. Everything here is a **PROPOSED** new requirement.
- No clinical claim, no efficacy/safety/selectivity claim, no patient data, no new source. No network. The frozen corpus at `/tmp/claude-0/frozen-corpus/` was not consulted this run — every absence claim above is scoped to the tracked tree at the HEADs recorded, and absence there is not repository-wide absence.

## Stop condition

Set up front: **stop when (a) every committed artifact publishing a cross-source aggregate over registry sourceIds has been enumerated and its enforcement status determined by reading what code opens, (b) every `pool: false` cohort with a `contextReason` has been checked for membership in a pooled figure, (c) a reporting-only cross-file check has been drafted and run with a real exit code and its actual flagged rows recorded, and (d) the tier and test-function cost have been measured with `tier_budget.py`'s own method.**

**MET**, with one part qualified: (a)–(d) are all done and measured. (c) is met in the sense the task specified — the check exists, ran, and its exact rows and exit code (1) are reported — but the check is **not placement-ready**, and I report its own false positives and false negative rather than tuning them away. Nothing was written into the Git tree; no ceiling was raised; no file was placed; the reading was not decided.

## Tool-call and wall-clock count actually used

**41 tool calls** (all `Bash`), **~9 minutes** wall clock (`02:48:29Z` → `02:57:29Z`). Under the ~40-call / ~40-minute target on time, one call over on calls.

## Next concrete action

**For the registry/policy owner, one decision with a concrete package attached**: the finding that generalises W13e is that the divergence is unrecorded in **4 of 5** exposed artifacts and unchecked in **5 of 5**, and that **six** `pool: false` sources — not one — sit inside committed pooled figures. The smallest step that does not pre-empt the reading is to require the *disclosure*, not the membership: each of the four unjustified artifacts gains one key naming the source and the flag it departs from, exactly as `emc-site-curation.json` already does. That is four prose additions by four artifact owners and changes no number.

**For this lane, the concrete successor**: replace the check's heuristic aggregate discovery with an explicit committed manifest of pooled figures — `(artifact path, node path, member field)` — so the guard has no false positives and no silent false negatives, and so a *new* pooled artifact that is absent from the manifest fails a completeness test rather than passing unnoticed. That is the version worth costing against the `commit-loop` ceiling; the version I ran is not. It should be built only after the owner says whether a cross-series median counts as pooling and whether the flag is a property of a row or of a source, because the manifest's shape depends on both answers.
