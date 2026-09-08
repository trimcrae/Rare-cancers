<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:16:10Z UTC
     agent id a5fa0c40c837b797c ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a5fa0c40c837b797c.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Report follows. I wrote nothing into the repository; `git status --porcelain` is empty at start and end.

---

## Worker

**W16e**, LANE 16 third refill — W16d's named successor: the regeneration-identity census for `research/modalities/`.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am powered by Opus 5, exact model ID `claude-opus-5`. I did not observe the served model and do not assert it as fact; the coordinator must extract the actual per-child runtime model from the transcript. **No environment variable in this container names a served model.**

`date -u` at start: `Tue Sep  8 02:50:12 UTC 2026`
`date -u` at end: `Tue Sep  8 03:08:59 UTC 2026`

`git rev-parse HEAD` **actually read at start: `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`** — this is neither the frozen commit in `COMMON-BRIEF.md` (`92abbcb…`) nor W16c's (`b9a0257…`). The tree kept moving under me while I worked: HEAD was `9ce39b4cac2aa2aa0e79c4f3045a0fd3e765ab52` at 02:56Z and `98a0833f1ede2cf9cef13790388260567a32e868` at 03:08Z. **My `tar` snapshot was taken at `3f5fc95`, so every measurement below is against `3f5fc95` and only that.** The coordinator is committing campaign reports; nothing under `research/modalities/`, `research/data/` or `scripts/` appears in any `git status` I took.

`git status --porcelain` at start: **empty**. At end: **empty**.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (51 lines; unmodified except the sed redaction and four very long proxy-host lists marked elided rather than reprinted):

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
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=...        [elided: proxy/truststore flags, no model identity]
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

---

## Stop condition (stated up front)

Return the moment all four of these are measured: (1) the regeneration identity for `emc_locoregional_eligibility` plus the two named controls, with real exit codes and, if different, the exact fields; (2) the coverage count across every `research/modalities/` generator/artifact pair; (3) the identity actually executed on every uncovered pair, with failures named; (4) the tier cost of adding the missing tests, measured by `tier_budget.py` itself. **All four were measured. Stop condition MET.**

---

## Question

**Does `research/modalities/emc-locoregional-eligibility.json` currently reproduce from its generator, how many of the repository's other modality artifacts are protected by the regeneration identity, which of the unprotected ones actually fail it today, and what would it cost to close the gap?**

Open because W16d established that the two headline pooled figures can be moved with zero tests going red, and identified the neighbouring identity assertion as the existing mechanism — but explicitly left "whether the committed artifact currently reproduces from its generator" UNKNOWN, and nobody has the coverage number.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers` (all read-only):

```
grep -n 'matches_the_generator\|reproduces_from_its_generator' -A12 \
  research/modalities/tests/test_emc_site_curation.py \
  research/modalities/tests/test_emc_surgical_quality.py
grep -n 'OUT\|^def build' research/modalities/emc_locoregional_eligibility.py
grep -n 'OUT\|^def build' research/modalities/emc_site_curation.py research/modalities/emc_surgical_quality.py
```

plus full reads of `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `systems/POLICY-evidence.md` (all 386 lines), `reports/W16b-frechet-followup-adversarial.md`, `reports/W16c-bishop2019-admissibility-package.md`, and `scripts/tier_budget.py`.

**Not replaying W16d.** I ran no perturbation battery and injected no controls into the pooled figures beyond one single-field negative control needed to prove my own diff is not vacuous (restored immediately, in scratch only). **I authored no `pinned-figures.json` entry.** **I did not touch, argue or resolve the `bishop2019` per-pool clause** — it is not mentioned again below except as the thing I am not doing. I retrieved nothing over the network. I did not run `scripts/preflight.sh`.

**Confirming W16c's D12 negative, and extending it:** W16c found no committed test pins 94, 259, 88, 326, 36.3 or 27.0. I confirm that and add the structural reason (§Result 1).

---

## Method / inputs

Everything executed on a `tar --exclude=./.git` copy at `/tmp/claude-0/w16e/`, taken from HEAD `3f5fc95`. Nothing in `/home/user/Rare-cancers` was created, edited or deleted.

**Environment:** system `python3` = `3.11.15`, no pytest. `/root/.local/bin/pytest` = **`pytest 9.1.1`, Python 3.11.15** (the uv venv). Both used with `PYTHONDONTWRITEBYTECODE=1`; pytest with `-p no:cacheprovider`.

**Identity harness** (`/tmp/claude-0/w16e/_scratch/one.py`, `identity.py`, `coverage2.py`, `census.py`): loads each generator by file path, loads the committed artifact, obtains the regenerated dict from `build()` where one exists or by setting `mod.OUT` to a temp path and calling `main()` where it does not, and diffs the two structures recursively, reporting the JSON path and both values of every leaf that differs.

---

## Result

### 1 · `emc-locoregional-eligibility.json` DOES reproduce today — but the identity is not expressible as written · PRIMARY

| Module | Artifact | Entry point | Identity holds? | Grade |
|---|---|---|---|---|
| `emc_locoregional_eligibility.py` | `emc-locoregional-eligibility.json` | **`main()` with `OUT` redirected — there is NO `build()`** | **YES, exactly identical, zero differing fields** | PRIMARY |
| `emc_site_curation.py` (control) | `emc-site-curation.json` | `build()` | YES, zero differing fields | PRIMARY |
| `emc_surgical_quality.py` (control) | `emc-surgical-quality.json` | `build()` | YES, zero differing fields | PRIMARY |

Exit code of the three-way run: **0**.

⛔ **The substantive finding is structural, and it is why the assertion is missing rather than merely forgotten.** `emc_locoregional_eligibility.py` has exactly three top-level functions — `wilson()` (line 137), `pool()` (line 148) and `main()` (line 201). **The artifact dict is assembled inside `main()` and written as a side effect at line 255.** There is no pure builder to compare against, so `json.load(open(mod.OUT)) == mod.build()` — the exact line the two neighbours use — **cannot be written for this module at all** without first extracting the dict construction out of `main()`. That is the smallest correct repair, and it is a change to a generator, not just an added test.

**Negative control on my own diff (non-vacuity).** I set `who_ever_metastasises.events` to 95 in the scratch copy and re-ran:
```
IDENTICAL: False
   DIFF $.who_ever_metastasises.events: 95 -> 94
```
then restored the file and re-ran to `IDENTICAL: True`. So the "reproduces" verdict is a measurement, not a harness that always says yes.

**Green baseline, same tree, same binary** (required before any failure is reported as a delta):
```
$ cd /tmp/claude-0/w16e && PYTHONDONTWRITEBYTECODE=1 /root/.local/bin/pytest -p no:cacheprovider -q \
    research/modalities/tests/test_emc_site_curation.py \
    research/modalities/tests/test_emc_surgical_quality.py \
    research/modalities/tests/test_emc_prognostic_coefficients.py \
    research/modalities/tests/test_emc_radiotherapy_contradiction.py \
    research/modalities/tests/test_emc_recurrence_timing.py \
    research/modalities/tests/test_locoregional_eligibility.py
92 passed in 0.65s
PYTEST_EXIT=0
```
**No pytest failure is reported anywhere in this report.** Everything below is a direct structural comparison, not a test-suite failure count.

### 2 · The coverage number nobody had · PRIMARY

Census rule (AST, not grep): a `research/modalities/*.py` with a module-level `OUT = …"<name>.json"` where that artifact exists on disk, and either a top-level `build()` or a top-level `main()` that writes `OUT`.

| Quantity | Count |
|---|---|
| Generator/artifact pairs found | **163** |
| … with a top-level `build()` | 52 |
| … `main()`-only (dict built inside `main()`, as the target artifact is) | 111 |
| Modules with `OUT` naming a `.json` that **does not exist** (excluded) | 9 |
| **Pairs whose regeneration identity IS asserted by a committed test** | **5** |
| **Pairs with NO committed identity assertion** | **158 (96.9%)** |
| Generators owning a `check()` that itself compares `OUT` to a rebuild | 9 (only 5 are exercised by a test) |

**The five that are covered — the complete list:**

| Module | Artifact | Test | Form |
|---|---|---|---|
| `emc_site_curation` | `emc-site-curation.json` | `tests/test_emc_site_curation.py` | `json.load(OUT) == mod.build()` |
| `emc_surgical_quality` | `emc-surgical-quality.json` | `tests/test_emc_surgical_quality.py` | `sq.check() == 0` |
| `emc_prognostic_coefficients` | `emc-prognostic-coefficients.json` | `tests/test_emc_prognostic_coefficients.py` | `check() == 0` |
| `emc_radiotherapy_contradiction` | `emc-radiotherapy-contradiction.json` | `tests/test_emc_radiotherapy_contradiction.py` | `check() == 0` |
| `emc_recurrence_timing` | `emc-recurrence-timing.json` | `tests/test_emc_recurrence_timing.py` | `check() == 0` |

⭐ **All five are the EMC clinical-curation cluster.** The mechanism exists, it is applied five times, and it stops exactly at the boundary of that cluster. `emc_locoregional_eligibility` sits inside that cluster by subject and outside it by protection.

Naming all 158 unprotected artifacts inline would be a wall of text; the machine-readable list is at `/tmp/claude-0/w16e/_scratch/coverage2.json` under key `uncovered`, and §3 names every one that actually fails. The 158 split **111 `main()`-only / 47 `build()`**.

### 3 · Executing the identity on all 158 — 45 differ, and only some of that is real · PRIMARY / UNKNOWN

Each of the 158 was run in its own subprocess with a 20 s timeout, `OUT` redirected to a temp file.

| Outcome | n | Grade |
|---|---|---|
| **IDENTICAL** — reproduces exactly | **46** | PRIMARY |
| **DIFFERS** | **45** | see breakdown |
| **NOT-EXECUTABLE** in this sandbox (import/runtime error) | 44 | UNKNOWN |
| Timed out or produced no output at 20 s | 20 | UNKNOWN |
| `SystemExit` on import | 2 | UNKNOWN |
| Harness line unparseable (`vaccine_threshold_calibration`) | 1 | UNKNOWN |

⚠ **The 66 UNKNOWN rows are not passes and not failures.** A module that cannot import here (no network, no GPU, missing optional dependency) has an unmeasured identity, exactly as `CLAUDE.md` §4 requires: a missing measurement is unknown, not zero.

**The 45 DIFFERS, classified honestly — because most of them are not what they look like:**

| Class | n | What it means | Grade |
|---|---|---|---|
| **A · Timestamp-only** | **8** | Every differing leaf is an embedded generation time. The artifact is otherwise byte-identical. **The identity is structurally un-assertable for these without normalizing the timestamp** — this is a design fact, not staleness. `categorical_axis_audit`, `emc_cohort_search`, `emc_data_level_sweep`, `emc_mtap_locus_persample`, `emc_sra_study`, `nr4a3_fusion_targets_confounds`, `nr4a3_fusion_targets_occupancy`, `sufex_second_handle` | PRIMARY |
| **B · Degraded-input suspected** | **25** | Whole top-level sections present in the committed artifact and absent from the regeneration — the signature of a generator that needed a network fetch or an absent cache and wrote a stub instead. **I am NOT calling these non-reproducing.** `alcam_precedent`, `aso_control_oligos`, `cd248_precedent`, `depmap_sarcoma_dependency`, `depmap_target_expression`, `apo_pose_recovery`, `emc_surfaceome_scan`, `fet_ddr_axis_scan`, `gse11185_wt_vs_fusion`, `gse28866_tumour_vs_normal`, `junction_proteome_novelty`, `junction_selfsimilarity`, `linker_twobranch`, `km_digitize`, `junction_transcript_sensitivity`, `nr4a3_structure`, `nr4a_selectivity`, `pose_second_method`, `nr4a3_resistance_map`, `nurr1_allosteric_vs_pocket5`, `ternary_calib_alpha_fetch`, `ternary_calib_epimer_freeze`, `ternary_calib_freeze`, `wurz_calib_freeze`, `nr4a_superfamily_selectivity` | **UNKNOWN** |
| **C · Real content divergence** | **12** | The generator ran to completion and produced materially different values from what is committed. **These are the substantive findings.** | PRIMARY |

⛔ **Class C in full, reported plainly with its diff — a committed artifact that no longer reproduces from its generator:**

| Module → artifact | n differing leaves | The divergence |
|---|---|---|
| `emc_proteostasis_read` → `emc-proteostasis-read.json` (`build()`) | 29 | Numeric drift on the same GSE24369 array: `XBP1.signed_percentile 93.95 → 93.96`, `frac_of_array_at_least_as_extreme_two_sided 0.15598 → 0.15585`, `n_symbols_at_least_as_extreme_two_sided 2915 → 2914`, `CANX.n_symbols… 4041 → 4039` |
| `emc_prmt5_route_controls` → `emc-prmt5-route-controls.json` (`build()`) | 31 | Same input, same direction: `n_symbols_scored 18688 → 18697`, `t_distribution.p50 −0.146 → −0.147`, `p75 1.222 → 1.22` |
| `emc_mtap_locus_persample` (Class A by my rule, but see note) | 41 | Alongside the timestamp, `array_dimness_panel_cache.GSM6009xx.n_genes_read 404 → 464` across five samples |
| `emc_ret_cistrome` → `emc-ret-cistrome.json` | 41 | `REMAP2022_NR4A1.background.panel_source.n_available 1297 → 1306`; `n_panel_resolved_on_this_build 198 → 37` |
| `tcip_citation_gate` → `tcip-citation-gate.json` (`build()`) | 15 | Reads live CI history: `verify_refs_runs.runs[0].run_id 31175823997 → 32577476737` |
| `surfaceome_instrument_limits` | 2 | `limits.L4_cspg4_coverage_gap.in_emc_surface_normal_window: False → True` — a boolean claim flip |
| `emc_fet_construct_designs` | 2 | `gene_models.PGR` and `ensembl_vs_uniprot_sequences.PGR` present in the regeneration, absent from the committed file |
| `nr4a3_fusion_targets` | 2 | A `⚠_…_RETRACTED_2026_08_08` key present in the regeneration, absent from the committed file |
| `valb_triangle_closure` | 1 | `noise_floor.sigma_leg_bounds.SUPERSEDED_2026_07_30` present in the regeneration, absent from committed |
| `coverage_threshold_curve` | 1 | `_provenance: 'MHCflurry re-run at the loose cut (this run)' → 'cached epitope-allele-loose-matrix.json'` — the provenance string itself changes with how it is run |
| `extract_smarca2_ic50` | 4 | `$.error` appears; `pdfs` 4→0, `tables` 2→0 — **this one is Class B in substance (needs PDFs it cannot reach here); I list it for completeness and grade it UNKNOWN** |
| `stage0_vaccine_item_provenance`, `row27_ddddg_precheck_status` | 31, 41 | Large divergences not individually inspected within budget — **UNKNOWN pending inspection** |

⭐ **The pattern worth the owner's attention: `emc_proteostasis_read`, `emc_prmt5_route_controls` and `emc_mtap_locus_persample` all read the same GSE24369 series matrix and all three drift together** (`n_genes_read 404 → 464`, `n_symbols_scored 18688 → 18697`). That is one cause, not three: **the committed local input has changed since those three artifacts were written, and no test noticed.** These are transcriptomic reads, not clinical figures, so nothing pooled or patient-facing moves — but they are exactly the failure mode the identity test exists to catch.

### 4 · Cost of adding the identity everywhere it is missing — measured by `tier_budget.py` itself · PRIMARY

I wrote 158 stub `def test_…_artifact_reproduces_from_its_generator()` functions into **one** file in the scratch copy's `research/modalities/tests/`, ran the repository's own `scripts/tier_budget.py --json`, then deleted the file and re-measured to confirm the tree returned to baseline. **No file was placed in the Git tree and no ceiling was raised anywhere.**

| Tier | Baseline (HEAD `3f5fc95`) | With 158 identity tests | Budget | Verdict |
|---|---|---|---|---|
| commit-loop | 102 files, **1466** functions | **unchanged, 1466** | 1500 | under (34 headroom) |
| **modalities** | 436 files, **7247** functions | **437 files, 7405** | **7500** | **under — 95 functions to spare** |
| paper-guards | 111 files, 966 | unchanged | 1000 | under |

⚠ **Two corrections to my dispatch brief, both measured:**

1. **The commit-loop tier is at 1466/1500, not 1497/1500 — it has 34 functions of headroom, not three.** `tier-budgets.json` maps commit-loop to `scripts/tests`, `research/autonomy/tests`, `systems/tests`.
2. **The commit-loop ceiling is not the binding constraint at all.** These tests belong in `research/modalities/tests/`, which is the **modalities** tier. The full 158 fits under the existing 7500 ceiling with 95 functions left over. **Adding the identity everywhere it is missing requires no ceiling change.**

**But the test-function count is not the whole cost, and reporting it alone would be misleading:**

| Cost component | Measured value |
|---|---|
| Test functions | **158** (fits: 7247 → 7405 / 7500) |
| Generators needing a `build()` extracted out of `main()` first — including the target artifact | **111** |
| Generators where a timestamp must be normalized before the identity can hold | **8 (minimum)** |
| Artifacts that would go **red on day one** because they genuinely no longer reproduce | **≥ 9** (Class C, confirmed subset) |
| Artifacts whose identity cannot be measured in this sandbox at all | **66** |

⛔ **So "add the test everywhere" is not a 158-function edit.** Adding it to the 47 `build()`-shaped pairs is cheap and immediate; the 111 `main()`-only pairs each need a generator refactor first; and ≥9 would fail on arrival and must be investigated (or their artifacts regenerated by their owner) **before** the guard is added, not after — adding a test that is red at commit time is not a guard, it is a broken gate.

⭐ **The cheap, correct first move for this lane's own artifact:** extract the dict construction from `emc_locoregional_eligibility.py::main()` into a `build()`, have `main()` call it, and add **one** test function. Cost: **1** test function (7247 → 7248 / 7500), **0** ceiling changes, and it is **green today** — I measured the identity holds. That closes W16d's gap on the two headline figures with the mechanism the repository already owns, and it is the only Class-A-clean member of the EMC clinical cluster still unprotected.

---

## Validation evidence

**RUN.**

| # | Command (cwd `/tmp/claude-0/w16e` unless noted) | Exit | Key output |
|---|---|---|---|
| 1 | `git rev-parse HEAD; git status --porcelain` (in `/home/user/Rare-cancers`, start) | 0 | `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`; status **empty** |
| 2 | `tar --exclude=./.git -cf - . \| (cd /tmp/claude-0/w16e && tar -xf -)` | 0 | `COPY_OK`, 610M |
| 3 | `PYTHONDONTWRITEBYTECODE=1 python3 _scratch/identity.py` | **0** | all three `IDENTICAL: True` |
| 4 | negative control (events 95) then restore, re-run #3 | 0 | `IDENTICAL: False` / `$.who_ever_metastasises.events: 95 -> 94`; then `IDENTICAL: True` |
| 5 | `PYTHONDONTWRITEBYTECODE=1 /root/.local/bin/pytest -p no:cacheprovider -q <6 files>` | **0** | `92 passed in 0.65s` |
| 6 | `PYTHONDONTWRITEBYTECODE=1 python3 _scratch/census.py` | 0 | 172 rows; 163 with an existing artifact, 9 missing |
| 7 | `PYTHONDONTWRITEBYTECODE=1 python3 _scratch/coverage2.py` | 0 | `generator/artifact pairs: 163 / COVERED: 5 / UNCOVERED: 158` |
| 8 | `xargs -P 8 -n 2 _scratch/runone.sh < _scratch/todo.txt` | **0** | 158 result lines |
| 9 | `PYTHONDONTWRITEBYTECODE=1 python3 scripts/tier_budget.py --json` (baseline, live repo) | **0** | commit-loop 1466/1500, modalities 7247/7500, paper-guards 966/1000 |
| 10 | same, scratch tree with 158 stubs | 0 | modalities **7405**/7500, `over: false`; other tiers unchanged |
| 11 | stubs deleted, re-measured | 0 | modalities back to **7247** |
| 12 | `git rev-parse HEAD; git status --porcelain` (end) | 0 | `98a0833f…`; status **empty** |

**PROPOSED (NOT RUN).** The `build()` extraction for `emc_locoregional_eligibility.py` and its one test function. I authored no such diff and placed no file. I did not run `scripts/preflight.sh` or `validate-registry.mjs`.

---

## Limitations

- **The tree moved under me.** HEAD went `3f5fc95` → `9ce39b4` → `98a0833` during this run. My snapshot is `3f5fc95`; every count and identity verdict is pinned to that commit and could differ at a later one.
- **66 of 163 pairs have an UNMEASURED identity here** (44 not executable, 20 timed out at 20 s, 1 unparseable, 1 `SystemExit`). Sandbox inability is not evidence of non-reproduction, and a 20 s timeout will have caught genuinely slow-but-correct generators. The true failure count is **≥ 9 and unbounded above by this run.**
- **Class B (25 pairs) is deliberately not called a failure.** Distinguishing "the artifact is stale" from "the generator degraded because its input is unreachable in this container" needs each module read individually, which I did not do.
- **My census rule is mechanical.** Generators whose output path is computed rather than written as a literal `"…json"` string, or that live outside `research/modalities/`, are not in the 163. The 9 `ARTIFACT-MISSING` rows were excluded without inspection.
- **The coverage detector is AST-based but not exhaustive.** It recognizes `alias.build()` compared against `json.load`, and `alias.check() == 0` where that module's `check()` provably references both `build()` and `OUT`. A test asserting the identity in some third form would be missed and counted as uncovered.
- **`tier_budget.py` counts test *functions*, not collected tests**, as its own docstring states; a parametrized identity test would cost 1 here and more to pytest.
- **No clinical claim.** The pooled figures involved are crude during-follow-up proportions with censoring ignored (`POLICY-evidence` §2.4), not survival estimates, and nothing here bears on efficacy, safety or any patient's prognosis. **Nothing in this report resolves, argues or touches the `bishop2019` per-pool clause.**
- Class C names artifacts that no longer reproduce; **it does not establish which side is correct** — the committed artifact may be right and the input wrong, or the reverse. That is the owner's call.

---

## Stop condition

Stated up front; **MET**. All four sub-questions were measured by execution, with a green pytest baseline in the same tree with the same binary, a non-vacuity control on the diff, and controls run alongside the target so a target failure could be told from an environment failure. Returning now.

---

## Tool-call and wall-clock count actually used

**28 tool calls** (26 Bash, 1 ToolSearch, 1 Monitor-schema fetch). **Wall clock 02:50:12Z → 03:08:59Z = 18 min 47 s.** Both inside the ~40/~40 target. One self-inflicted cost worth recording: my first batch runner was serial with a 75 s per-module timeout and had to be killed after ~11 minutes; re-running it as `xargs -P 8` with a 20 s timeout finished all 158 in under a minute.

---

## Next concrete action

**One task, finite, in this lane:** extract the artifact-dict construction from `research/modalities/emc_locoregional_eligibility.py::main()` into a top-level `build()` that `main()` then calls and writes, and add exactly one test function to `research/modalities/tests/test_locoregional_eligibility.py`:

```python
def test_the_committed_artifact_matches_the_generator():
    assert os.path.exists(mod.OUT)
    with open(mod.OUT, encoding="utf-8") as fh:
        assert json.load(fh) == mod.build()
```

This is measured-green today, costs **1** test function (modalities 7247 → 7248 / 7500), requires **no** ceiling change, closes the exact gap W16d demonstrated on `94/259` and `88/326`, and uses the mechanism the repository already applies five times next door. It must be done by a worker with write authority; I have none and wrote nothing.

**Second, separable and for the registry/artifact owner, not for this lane:** investigate the shared-cause Class C cluster — `emc_proteostasis_read`, `emc_prmt5_route_controls` and `emc_mtap_locus_persample` all drift together on the GSE24369 input (`n_genes_read 404 → 464`). One of the committed artifact set and the committed input set is stale; deciding which is a data-ownership call, not a testing one.
