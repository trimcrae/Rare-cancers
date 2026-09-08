<!-- collected 2026-09-08T05:00:19Z by campaign coordinator; agent id a4e62a6813ccebc61; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a4e62a6813ccebc61.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

W72, OPUS-CAPACITY-CAMPAIGN-20260908 — checker-invocation census lane. Read-only on `/home/user/Rare-cancers`; all execution under `/tmp/claude-0/w72/`, now deleted.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt. Nothing in the environment confirms a served model; the environment names only a CLI version.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start of run, full; no key names the model):

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
JAVA_TOOL_OPTIONS=<proxy/truststore flags>
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

**Start:** `date -u` = `Tue Sep  8 04:53:31 UTC 2026`; `git rev-parse HEAD` = `fcb36d3c651223d90b98c0cb64169bb106e6e060`; `git status --porcelain` = empty.
**End:** `date -u` = `Tue Sep  8 04:57:05 UTC 2026`; `git rev-parse HEAD` = `129a4e2a1c39352a7a697c42445bb27fc50f9b0c`; `git status --porcelain` = empty (I wrote nothing; HEAD advanced because the coordinator committed collected reports).

## Question

Which of the repository's executable checkers/linters/validators are invoked by **anything** — `scripts/preflight.sh`, `scripts/fast_checks.py`, `.github/workflows/*.yml`, or a pytest module — and which are complete but wired to nothing? Open because three workers (W09j, W30c, W34) hit the same shape from different directions without anyone measuring the denominator.

## Prior-work check

Read in full: `COMMON-BRIEF.md` (510 lines), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`. Taken as given and **not re-derived**: W45's 26-module regenerate/check census, W44's 18-row preflight vacuous-pass census, W47's `|| true` finding at `nr4a3-covalent-handle-ensemble.yml:88`, W09j's `lint_asymmetry` observation, W30c's `meta-analysis.mjs` observation, W53's arithmetic verification of the pooler, W51/W30d/W48 on `lint_consistency`/`validate-registry`.

Commands run to build the population (not to re-derive prior findings):
- `git ls-files | grep -E '(^|/)(lint_[^/]*|[^/]*_check[^/]*|check_[^/]*|validate[-_][^/]*|[^/]*_validator[^/]*|[^/]*_lint[^/]*)\.(py|mjs|js|sh)$'` → 24 files, 23 after dropping `research/modalities/rbfe_spot_checkpoint_test.py`.
- A Python scan of every tracked `.py/.mjs/.js/.sh` outside `tests/` for a literal `"--check"`/`'--check'`/`--check-only` → 157 files. Union population = **175**.
- `git ls-files '*.mjs' '*.js'`, `git ls-files '*guard*.py'` to add verification executables the name/flag patterns miss.

W25 not read or referenced. I did not run `scripts/preflight.sh`, did not run any `--refresh` mode, and did not invoke `atr_hrd_sarcoma_series.py` at all.

## Method and inputs

1. Built the 175-file population above.
2. Grepped every basename against the four invocation surfaces: `scripts/preflight.sh`, `scripts/fast_checks.py`, all 175 `.github/workflows/*.yml`, and every tracked pytest-shaped file (`**/tests/*.py`, `test_*.py`, `conftest.py`).
3. **Classified each hit rather than counting it** — a raw grep over this repository is badly misleading, because its comments and test docstrings name tools constantly. Each hit line was typed as `EXEC` (a `python3|node|pytest|bash` invocation), `IMPORT`, `STRING` (a quoted filename in code), or `MENTION` (prose/comment), and comment-only lines were dropped.
4. Hand-adjudicated every candidate that came back with no `EXEC`/`IMPORT`/`STRING` hit, plus the whole 23-file name-shaped set.
5. Read each unwired checker's source for write surfaces (`open(...,'w'/'a')`, `write_text`, `writeFileSync`, `shutil`, `mkdir`) before executing it. The four pure checkers were run in place (zero write surfaces, confirmed by source). `meta-analysis.mjs` **does** write (`:101 writeFileSync(... "results.json")`) and was run only in a `cp -a` scratch copy under `/tmp/claude-0/w72/scratch/`.

⚠ **Methodological warning for anyone reusing this**: my first-pass grep, and the obvious one, produces false positives in both directions. Four examples I caught: (a) `scripts/fast_checks.py:100,103,105,108` name `validate-registry.mjs`, `validate-research.mjs`, `lint_optional_input_guards.py` and `lint_derived_thresholds.py` inside an **`EXCLUDED` tuple** — a list of things fast_checks deliberately does *not* run, which greps identically to a run; (b) `scripts/preflight.sh:7` names `lint_consistency.py` in a header comment, not the gate (the gate is `:586`); (c) `test_figure_render_is_not_truncated.py:12` and `test_ckpt_cadence_is_new_legs_only.py:5` name their subject in a docstring only; (d) in the other direction, a `grep -v "/<basename>:"` filter to exclude a file's self-hits **also silently deletes `tests/test_<basename>:` lines**, which briefly made `abfe_xtag_guard.py` look callerless when it is imported at `research/modalities/tests/test_abfe_xtag_guard.py:21`. Raw hit counts are not evidence here.

## Result

### Table A — the 23 name-shaped dedicated checkers (PRIMARY, all rows adjudicated by hand)

| Checker | Invoked by (file:line) | Currently passes? |
|---|---|---|
| `research/autonomy/contract_check.py` | `scripts/preflight.sh:1484` (`--check`) | not run (invoked; out of scope) |
| `research/manuscripts/emc_systems_map_check.py` | `scripts/preflight.sh:627`; `scripts/fast_checks.py:84`; `.github/workflows/tests.yml:182`; `research/manuscripts/tests/test_emc_systems_map_check.py` | not run |
| `research/manuscripts/fet_notice_sync_check.py` | **NOTHING** | **RUN: exit 0** |
| `research/manuscripts/figures/check_figure_specs.py` | **NOTHING** (`test_figure_render_is_not_truncated.py:12` is a docstring mention) | **RUN: exit 1 — `ModuleNotFoundError: No module named 'PIL'`.** Not a content defect; not runnable in this container |
| `research/manuscripts/lint_asymmetry.py` | **NOTHING** on the tree (`research/manuscripts/tests/test_lint_asymmetry.py` calls `la.check()` on `tmp_path` corpora only — its own docstring `:8` says so) | **RUN: exit 0** |
| `research/manuscripts/lint_changed_prose.py` | `scripts/preflight.sh:661` — but `\|\| true`, verdict discarded (advisory by design, per the comment above it) | not run |
| `research/manuscripts/lint_citation_types.py` | `scripts/preflight.sh:664`; `.github/workflows/tests.yml:144`; `research/manuscripts/tests/test_citation_type_guard.py` | not run |
| `research/manuscripts/lint_citations.py` | `scripts/preflight.sh:684`; `.github/workflows/tests.yml:149`; pytest | not run |
| `research/manuscripts/lint_claims.py` | `scripts/preflight.sh:650`; `scripts/fast_checks.py:36`; `.github/workflows/nr4a3-covalent-handle-ensemble.yml:87`; pytest | not run |
| `research/manuscripts/lint_consistency.py` | `scripts/preflight.sh:586`; `scripts/fast_checks.py:73`; `tests.yml:136`; `nr4a3-linker-covalent-reach.yml:99`; `nr4a3-covalent-handle-ensemble.yml:88` (`\|\| true`) | not run (W28d/W51 measured exit 0) |
| `research/manuscripts/lint_readability.py` | `scripts/preflight.sh:713` — `--report`, piped, `\|\| true`; advisory by explicit design | not run |
| `research/manuscripts/lint_style.py` | `scripts/preflight.sh:700`; `.github/workflows/tests.yml:151`; pytest | not run |
| `research/manuscripts/lint_submission_residue.py` | `scripts/preflight.sh:1437`; `.github/workflows/tests.yml:162`; pytest | not run |
| `research/modalities/linker_chem_check.py` | `.github/workflows/fusion-cpu-extras.yml:730` (`\|\| true`), `:736`, `:742` | not run (needs chem deps) |
| `research/modalities/lint_derived_thresholds.py` | `.github/workflows/tests.yml:351`; `research/modalities/tests/test_lint_derived_thresholds.py:241`. **Not** fast_checks — `:108` is its `EXCLUDED` entry | not run |
| `research/modalities/lint_optional_input_guards.py` | `.github/workflows/pose-recovery-check.yml:249`; `research/modalities/tests/test_lint_optional_input_guards.py:370`. **Not** fast_checks — `:105` is its `EXCLUDED` entry | not run |
| `research/modalities/nrv04_prespend_check.py` | `.github/workflows/fusion-cpu-extras.yml:1583` | not run (needs S3 creds) |
| `research/modalities/rbfe_spot_checkpoint.py` | `research/modalities/tests/test_ckpt_cadence_is_new_legs_only.py:25-26` (IMPORT) | not run (runtime lib, not a content checker) |
| `research/modalities/valb_frame_transfer_check.py` | `.github/workflows/selcal-cofold-validate.yml:197` | not run (needs job artifacts) |
| `scripts/fast_checks.py` | is itself a surface; `research/manuscripts/tests/test_line_citations.py:537` | not run |
| `scripts/validate-registry.mjs` | `scripts/preflight.sh:723`. **Not** fast_checks — `:100` is its `EXCLUDED` entry | not run (W30d measured exit 0 at `408b676a`) |
| `scripts/validate-research.mjs` | **NOTHING.** Its only appearance across all four surfaces is `scripts/fast_checks.py:103`, inside `EXCLUDED` — i.e. a documented decision *not* to run it | **RUN: exit 0**, `OK - 14 candidate(s) valid. 1 warning(s)`, one WARN (`candidates[0] "imatinib-kit-subset" is T3`) |
| `systems/systems_check.py` | `scripts/preflight.sh:609`; `scripts/fast_checks.py:88`; `.github/workflows/method-watch-triggers.yml:136`; pytest | not run (red for campaign-footprint reasons, W31b/W41 — given) |

### Table B — verification executables outside the name pattern

| Checker | Invoked by (file:line) | Currently passes? |
|---|---|---|
| `research/meta/meta-analysis.mjs` | **NOTHING** (confirms W30c: zero hits in preflight, fast_checks, all 175 workflows, all pytest files; `test_systems_check.py:1818` is an unrelated title string) | **RUN in `cp -a` scratch: exit 0**, `results.json` sha256 `e696abac…` unchanged — byte-identical regeneration (independently confirms W53) |
| `systems/parser_guard.py` | `scripts/preflight.sh:716`; `scripts/fast_checks.py:92`; `.github/workflows/tests.yml:268` | not run |
| `scripts/tier_budget.py` | `scripts/preflight.sh:1507` (`--check`); `scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py:170` | not run |
| `scripts/citation_debt.py` | `scripts/preflight.sh:863` (via the piped gate-spec helper, `--check`) | not run (W44 row 17 — exposed-vacuous, given) |
| `research/manuscripts/claim_coverage.py` | `scripts/preflight.sh:848`; `.github/workflows/tests.yml:243` | not run |
| `research/autonomy/amendment_guard.py` | `.github/workflows/autonomy-tick.yml:105` (`--check-log`); pytest | not run |
| `research/autonomy/push_guard.py` / `prepush_ledger_guard.py` | **Not by the four surfaces** — by the git hook `.githooks/pre-push`, and `core.hooksPath` **is** set to `.githooks` in this checkout (measured). A fifth, real gate | not run (would require a push) |
| `research/modalities/abfe_xtag_guard.py` | `research/modalities/tests/test_abfe_xtag_guard.py:21` (IMPORT) | not run |
| `research/modalities/vast_idle_guard.py` | imported by 6 modalities modules + `research/modalities/tests/test_vast_idle_guard.py` | not run (live-instance guard) |
| `research/modalities/artifact_stub_guard.py`, `gcp_launch_guard.py`, `stuck_run_guard.py` | workflows (`depmap-dependency.yml:213`, `gpu-ternary-fep-gcp.yml:1472`, `lane-staleness-watch.yml:317` — the last under `\|\| true`) | not run |

### The count

**Dedicated-checker denominator (Tables A+B, 33 distinct executables): 5 are invoked by nothing — 15.2%.**

The five: `research/manuscripts/lint_asymmetry.py`, `research/manuscripts/fet_notice_sync_check.py`, `research/manuscripts/figures/check_figure_specs.py`, `scripts/validate-research.mjs`, `research/meta/meta-analysis.mjs`. **Three of these are new** (only `lint_asymmetry` and `meta-analysis.mjs` were already known, from W09j and W30c).

**Four of the five run clean today** (exit 0), so the repository maintains four working, currently-green checkers that nothing ever consults. The fifth, `check_figure_specs.py`, exits 1 in this container solely for a missing `PIL` — **UNKNOWN**, not a content defect, and no surface installs Pillow for it because no surface runs it.

Two sharper observations:
- **`validate-research.mjs` is not merely unwired, it is documented-out.** `scripts/fast_checks.py:103` lists it under `EXCLUDED` with the reason `"(a) -- Node. Validates research/hypotheses/candidates.json against METHODOLOGY.md"`. The three siblings in that same `EXCLUDED` block are all covered elsewhere and the comments say where — `validate-registry.mjs` "IS covered: preflight gate 5 runs it", the two `lint_*` modules run in `tests.yml`/`pose-recovery-check.yml`. `validate-research.mjs` alone is excluded from fast_checks *and* covered nowhere else. The exclusion reads as a routing decision; the routing never happened.
- **`lint_asymmetry.py` is invoked-but-never-aimed.** It has a full 774-line implementation and a passing test suite, but `test_lint_asymmetry.py:8` states outright that "EVERY CORPUS IS A `tmp_path` TREE, NEVER THE WORKING TREE". The only thing that has ever pointed it at the manuscripts is a hand-run recorded in `research/autonomy/sprint-2026-09-01/S45-ELIGIBILITY-MAP-GAPS-CLOSED.md:141` — and my run reproduces that line's output exactly, a year-old hand result still true and still unautomated.

**Broader `--check`-population denominator: of the 175 files declaring a `--check`-shaped flag, 42 (24.0%) have zero mention of any kind on any of the four surfaces.** ⚠ That 42 is a *weaker* number and should not be quoted as "42 unwired checkers": most are generator/analysis modules whose `--check` is the reproducibility arm of a producer (W45's class), not standalone checkers. The 42, for the record: `goal_progress`, `posting_register`, `stalled_holder`, `aso_priorart_evidence`, `fet_notice_sync_check`, `emc_fusion_frame_figure`, `lint_asymmetry`, `alcam_precedent`, `aso_control_oligos`, `aso_delivery_antigen`, `aso_per_junction_table`, `atr_part_d_proliferation_control`, `cd248_precedent`, `emc_adaptive_pazopanib`, `emc_fet_frame_and_composition`, `emc_fourth_cohort_route_readout`, `emc_icdo_contamination`, `emc_model_junction_evidence`, `emc_mtap_locus_persample`, `emc_prior_art_fulltext_screen`, `emc_prmt5_effect_sizes`, `emc_prmt5_multiplicity`, `emc_prognostic_coefficients`, `emc_radiotherapy_contradiction`, `emc_recurrence_timing`, `emc_rt_bed_reappraisal`, `emc_scheduling_medians`, `emc_surgical_quality`, `emc_tissue_read_statistics`, `expression_validation_readiness`, `fus_ddit3_prefix_comparison`, `fusion_cofold_recut`, `gse11185_wt_vs_fusion`, `hgnc_index`, `nr4a3_fusion_targets_robustness`, `nr4a3_short_linker_probe`, `nurr1_allosteric_vs_pocket5`, `pgr_parent_engagement`, `scope_rung_cost`, `steric_design_rule`, `target_route_census`, `tcf12_offtarget_tissue_expression`. I did not run these (W45 already characterised the class, and several are the write-mode hazards the brief warns about).

Surface distribution over all 175 (PRIMARY, mention-level, unadjudicated): 42 nothing, 40 pytest-only, 34 pytest+workflows, 18 workflows-only, 16 preflight+pytest+workflows, 8 preflight+pytest, 6 preflight-only, 5 all-four, 6 other combinations.

## Validation evidence

Environment: `/home/user/Rare-cancers`, Linux, `python3` = `/usr/local/bin/python3`, `node` present. All RUN.

```
$ python3 research/manuscripts/lint_asymmetry.py
⚠ KNOWN OPEN  research/manuscripts/degrader/nr4a3-degrader-broader-indications.md:35  (baselined 2026-09-01)
⚠ KNOWN OPEN  research/manuscripts/degrader/nr4a3-degrader-broader-indications.md:44  (baselined 2026-09-01)
lint_asymmetry: 0 new symmetric restatements of the paralogue requirement (2 known open, 1 accepted)
EXIT=0

$ python3 research/manuscripts/fet_notice_sync_check.py
fet_notice_sync_check: OK - section 4 and the reviewer block agree (720 words)
EXIT=0

$ python3 research/manuscripts/figures/check_figure_specs.py
Traceback (most recent call last):
  File ".../check_figure_specs.py", line 26, in <module>
    from PIL import Image
ModuleNotFoundError: No module named 'PIL'
EXIT=1

$ node scripts/validate-research.mjs
WARN  candidates[0] "imatinib-kit-subset" is T3 — eligible to graduate into the clinical registry's emergingTreatments (needs clinician review)
OK - 14 candidate(s) valid. 1 warning(s) (unverified claims to resolve before publication).
EXIT=0

$ cd /tmp/claude-0/w72/scratch && node research/meta/meta-analysis.mjs     # cp -a copy, NOT the tree
diseaseDeath: pooled 14.2% (95% CI 8.5-22.6%), I²=62%, τ²=0.104, k=2
recurrence (modern, dx mid>=2005, k=2): 19.4% (7.2-42.6%)
recurrence (older/undated, k=2): 38.6% (21.6-58.9%)
recurrence (registry-only): 11.9% (7.4-18.6%)
Results: research/meta/results.json
EXIT=0
sha256 before = e696abacff88a407bc696d6b6966e2efefe6c08af5fc8ae6b974da42146c8acd
sha256 after  = e696abacff88a407bc696d6b6966e2efefe6c08af5fc8ae6b974da42146c8acd   # IDENTICAL
```

Write-surface pre-check before running the four in-place: `grep -nE "open\([^)]*['\"][wa]|write_text|writeFileSync|\.write\(|os\.remove|shutil\.(copy|move|rmtree)|mkdir|subprocess"` returned **zero matches** in all four (`lint_asymmetry.py`, 774 lines, only `argparse`; `fet_notice_sync_check.py`, 85 lines; `check_figure_specs.py`, 61 lines; `validate-research.mjs`, 80 lines). `git status --porcelain` empty before and after every run.

`core.hooksPath` = `.githooks`; `.githooks/pre-push` exists, is executable (2162 bytes), and names both `prepush_ledger_guard.py` and `push_guard.py`. SOURCE-DERIVED, not an observed hook firing — I ran no push.

PROPOSED (NOT RUN): running the 42 broader-population modules; installing Pillow to obtain a real verdict from `check_figure_specs.py`; any wiring change. **Nothing was wired, repaired, or proposed as code.**

## Limitations

- **Scope of "invoked" is the four named surfaces plus, where I found it, the git hook.** A checker could also be reached by `make`, a shell alias, a skill, a `SessionStart` hook, or a human habit; I did not enumerate those. `.claude/hooks/` holds five turn-end scripts I did not audit for checker invocation.
- **"Passes" means exit 0 on this container at this working tree.** It is not a statement about CI, where dependency sets differ (`check_figure_specs.py` is the live proof: exit 1 here for `PIL` alone).
- **Table B is a curated set, not an exhaustive one.** I selected verification-purpose executables the name/flag patterns miss; a different curator would draw the 33 boundary differently, which moves the 15.2%. The 175/42 pair is reproducible from a stated rule and is the number to quote if a mechanical denominator is wanted — with the caveat above that most of the 42 are producers, not checkers.
- **W63's question is disjoint from mine and both are needed.** A checker can be invoked *and* suppressed: `lint_changed_prose` (`preflight.sh:661`), `lint_readability` (`:713`), `lint_consistency` in `nr4a3-covalent-handle-ensemble.yml:88`, `linker_chem_check` at `fusion-cpu-extras.yml:730`, and `stuck_run_guard` at `lane-staleness-watch.yml:317` all run under `|| true`. Two of those five (`lint_changed_prose`, `lint_readability`) are advisory by explicit, reasoned design and should not be counted as defects; I make no claim about the other three — that is W63's lane.
- HEAD advanced from `fcb36d3c` to `129a4e2a` during the run. Per the brief's measured guarantee, coordinator commits touch only the campaign directory, so no measurement above is affected; I did not re-verify that guarantee.
- No network, no paid API, no GPU, no GitHub API call, no Actions run. No content-policy refusal occurred.

## Stop condition

Set up front: *return as soon as every dedicated checker has an adjudicated invoked/NOTHING verdict and every unwired one has a recorded exit code from a read-confirmed non-writing mode (or a scratch copy).* **MET.** 33 dedicated checkers adjudicated, 5 unwired, all 5 executed with real exit codes recorded.

## Tool-call and wall-clock count actually used

**16 tool calls; ~4 minutes wall clock** (04:53:31Z → 04:57:05Z). Well inside the ~40/~40 target. Scratch directory `/tmp/claude-0/w72/` deleted; `ls /tmp/claude-0/` confirms it is gone.

## Next concrete action

One successor, for the owner and not for a worker: **decide `scripts/validate-research.mjs`'s home.** It is the only entry in `fast_checks.py`'s `EXCLUDED` block whose exclusion comment does not name a covering surface, its three siblings all do, and it exits 0 today with one long-standing WARN — so a decision is cheap and carries no failure risk. The natural comparison is `validate-registry.mjs`, which sits at preflight gate 5 for exactly the reason its `EXCLUDED` comment gives. ⚠ That decision must be taken by the gate's owner, not by a census worker: `scripts/preflight.sh:684`'s own comment block records that gate ordinals are derived from its `== … ==` headings by `systems_check.check_preflight_gate_list` and hard-coded in four other documents, so adding a heading renumbers every gate below it and turns `[P1]` red. Wiring is not a mechanical edit here, and I made none.
