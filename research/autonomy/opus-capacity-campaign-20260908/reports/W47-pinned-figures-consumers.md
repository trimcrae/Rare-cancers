<!-- collected 2026-09-08T04:45:25Z by campaign coordinator; agent id a4c0947258ab83a66; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a4c0947258ab83a66.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

W47, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: repository-instrument audit (consumers of the pinned-figures registry).

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — I am told I am Claude Opus 5 (`claude-opus-5`). No environment variable names a model; the literal output of the required command is pasted below (start; re-running at end returned the same set).

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...,api.anthropic.com,api-staging.anthropic.com,api-pr-preview.anthropic.com,mcp-proxy.anthropic.com,mcp-proxy-staging.anthropic.com,...
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy/truststore flags)
NO_PROXY=localhost,127.0.0.1,::1,...
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

Start: `date -u` = `Tue Sep 8 04:39:42 UTC 2026`; HEAD `408b676aec3625a36917755662516232a27a1278`; `git status --porcelain` = empty.
End: `date -u` = `Tue Sep 8 04:41:51 UTC 2026`; HEAD `7a1002679e0830fb19bed48660772cdcc91c495d`; `git status --porcelain` = 0 lines. **HEAD advanced under me, but `git diff --name-only 408b676 HEAD | grep -v opus-capacity-campaign-20260908` returns 0 files** — no file I read or measured changed. Scratch `/tmp/claude-0/w47/` created and deleted (`rm -rf`, verified absent from the `/tmp/claude-0/` listing).

## Question

For every entry in `research/manuscripts/pinned-figures.json`, which executable consumer actually reads it, and does any gate compare the pinned value against the live value it pins? Classify each entry ENFORCED / READ-BUT-NOT-COMPARED / UNREAD.

## Prior-work check

- `ls research/autonomy/opus-capacity-campaign-20260908/reports/ | grep -iE 'W28|W47'` → `W28-superseded-marker-audit.md`, `W28b-dead-guard-fixture-check.md`, `W28c-registry-schema-and-pattern-census.md`. **No `W28d` report exists at either HEAD**, so there is no transplant result to take as given; I did not attempt W28d's 40-WOULD-MATCH transplant test and my numbers are not a substitute for it. My one overlap-adjacent measurement (which superseded patterns match anything in the 29 targets) is a *scope* measurement needed to answer "can this gate fail", not a transplant.
- `rg -n 'pinned-figures\.json' -t x` (py/sh/yml/yaml/toml/cfg/ini), and `rg -n 'lint_consistency'`, both with `--glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'` — these enumerated the consumer set below.
- Read `CLOSED-WORK.md`: nothing here replays a closed scientific gate. Read the brief's "Known, measured" section: I did not re-measure the campaign resolution rate, the `literature-cache` ref, or the `systems_check` baseline, and I used `pytest` (not `python3 -m pytest`) per the W29f correction.

## Method and inputs

- Registry: `/home/user/Rare-cancers/research/manuscripts/pinned-figures.json` (153,842 bytes). Enumerated its top level with `python3 -c json.load`.
- `rg` for the file path and for each top-level key across `systems/`, `scripts/`, `research/` with the campaign directory excluded; then read every use site in source.
- Two read-only executions (confirmed no-write by reading `main()` and the test module before running): `python3 research/manuscripts/lint_consistency.py` and `pytest -q` on the two registry-derived test modules. I did **not** run `scripts/preflight.sh` and did not invoke `atr_hrd_sarcoma_series.py` at all.
- Live checkout only. I did not read the frozen corpus; `lint_consistency.py` is not one of the two line-shifted files W38b names.

## Result

**Counts (183 entries): ENFORCED 160 · READ-BUT-NOT-COMPARED 23 · UNREAD 0.**

The 23 are all `superseded` entries whose pattern currently matches no line in any of the 29 targets — the entry is loaded and compiled on every gate run, but no comparison against live text ever takes place and, unlike `subset_checks`, there is no zero-match alarm. They remain enforced *by design* (the gate would fail the moment the retired value reappeared unmarked); they are not enforced *today*.

The registry's `_README`, `_marker_note` and `_artifact_figures_note` are prose, read by humans and by no executable consumer; they are not entries and are excluded from the 183.

### Entry classification (all `PRIMARY` — direct reading of committed source, plus two runs I performed)

| Section | n | Class | Gate that compares pinned vs live | file:line |
|---|---|---|---|---|
| `derivations` (`ladder_total`) | 1 | ENFORCED | D2 compares `expect_low/mid/high` against live `vast-ladder-repricing.json` ladder rows + declared non-tool stages (tol `tolerance_usd`); D1 checks the tool's own total vs its own rows; D3 requires each `must_appear_in` doc to state that same total | `research/manuscripts/lint_consistency.py:276` (loop), `:293-306` (D1), `:308-322` (D2), `:324-338` (D3) |
| `artifact_figures` | 99 | ENFORCED | Reads live artifact JSON at `artifact`/`key`, applies `scale`, then requires every number on a `context`-matching line in each `must_appear_in` home to be within `tolerance`; a missing artifact, unreadable key, absent context or mismatched digits are each ERROR | `lint_consistency.py:403` (loop), `:416` (`_dig_json` read), `:434-451` (context/mismatch), `:389-397` (flattened arm) |
| `table_completeness` (`bid_strategy_repriced_ladder`) | 1 | ENFORCED | Every ladder key in the live `tool_json` must appear among the table's rows; printed TOTAL must match live `total_plan_usd`; printed rows must sum to printed TOTAL | `lint_consistency.py:481` (loop), `:504-515` (T-missing-row), `:526-532` (T-total-mismatch), `:536-548` (T-rows-do-not-sum) |
| `subset_checks` (`strategy_spine_cum`) | 1 | ENFORCED | Values matched by `subset_pattern` must all appear among `superset_pattern` matches in the same live file; **and zero matches on either side is itself an ERROR** (`X-pattern-found-nothing`) — the only section with an anti-inertness alarm | `lint_consistency.py:565` (loop), `:571-578` (alarm), `:580-586` (contradiction) |
| `superseded` — pattern matches ≥1 line in a target | 58 | ENFORCED | Scans all 29 `targets`; an unmarked occurrence of the retired value is ERROR `S-<id>`; `is_cleared` applies the marker window | `lint_consistency.py:601` (loop), `:607` (`is_cleared`), `:609-613` (finding) |
| `superseded` — pattern matches nothing in any target | 23 | READ-BUT-NOT-COMPARED | Same loop reads and compiles the entry; no live text is ever compared and nothing reports the inertness | same site, `lint_consistency.py:601-613` |

The 23 inert ids: `aso_standard_practice_excludes_parents`, `aso_reagent_coverage_95pct`, `thiol_hg_occlusion_first_gen`, `single_host_new_card_figures_2026_07_27`, `card_a100pcie_and_3090ti_first_pass_medians`, `valb_rung_band_8_78_22_28`, `ternary_lane_valb_cohort3_rates`, `realised_spend_before_orphan_leak`, `realised_spend_before_retro_orphan_leak`, `realised_spend_omitted_the_selcal_lane`, `aso_within_partner_shared_donor_run_three_nt`, `aso_parent_null_half_generic_half_specific`, `aso_thermo_cross_margin_discordance`, `aso_ewsr1_partner_share_wilson_upper_87_8`, `aso_canonical_file_condemned_record_count_250`, `aso_canonical_file_junction_key_count_40`, `vaccine_e7_coverage_stated_without_a_panel`, `vaccine_coverage_wilson_intervals`, `commit_loop_about_75_seconds`, `commit_loop_gate13_39s_55_tests`, `commit_loop_about_nine_minutes`, `commit_loop_gate13_446s_85_to_94_percent`, `commit_loop_citation_provenance_44s`.

### Support lists (configuration, not pinned quantities — both fully consumed)

| Key | n | Consumers | file:line |
|---|---|---|---|
| `targets` | 29 | (a) scope of the superseded scan; (b) `parser_guard` fails if any target path is gone; (c) `systems_check` `_pinned_targets()` feeds `[D8]` archive-dependency and **raises** rather than returning empty; (d) the every-home test asserts the SI is a target | `lint_consistency.py:596`, `:642`; `systems/parser_guard.py:122-130`; `systems/systems_check.py:1360,1368-1381,1846-1847`; `research/manuscripts/tests/test_pinned_figures_every_home.py:118` |
| `supersession_markers` | 35 | (a) `is_cleared`; (b) `publish_bar` clause-count guard reads the marker list from here rather than restating it; (c) a policy test forbids any marker that would clear a reprice-style assertion | `lint_consistency.py:595`; `research/autonomy/tests/test_the_clause_count_is_never_typed.py:57,93-95`; `research/modalities/tests/test_lint_consistency.py:340-345` |

### Full consumer inventory, with what each actually does

| Consumer | file:line | Reads | Comparison? |
|---|---|---|---|
| `lint_consistency.py` (the gate) | `research/manuscripts/lint_consistency.py:79` (`REGISTRY`), `:616-620` (`lint()`) | all 5 entry sections + `targets` + `supersession_markers` | **Yes** — all five checks; exit 1 on any ERROR |
| `scripts/preflight.sh` | `:585-591` | runs the gate | Yes (sets `rc=1`) |
| `.github/workflows/tests.yml` | `:136` | runs the gate | Yes (CI job fails) |
| `.github/workflows/nr4a3-linker-covalent-reach.yml` | `:99` | runs the gate | Yes |
| `.github/workflows/nr4a3-covalent-handle-ensemble.yml` | `:88` | runs the gate with `|| true` | **No — result discarded** |
| `scripts/fast_checks.py` | `:73` | runs the gate as member 1 of six | Yes |
| `scripts/blast_radius.py` | `:235` | runs the gate | Yes |
| `scripts/regenerate_aso_chain.sh` | `:429` | runs the gate in the chain's check loop | Yes |
| `systems/parser_guard.py` | `:119-140` | `targets`, and `must_appear_in`/`file` across `derivations`/`artifact_figures`/`table_completeness`/`subset_checks` | Path-existence only — fails if the registry is missing, a target is gone, or a pinned figure's home path does not exist. Not a value comparison |
| `systems/systems_check.py` | `:1360,1368-1381,1846-1847` | `targets` (`.md` only) | Not a value comparison; `[D8]` refuses to archive a pinned target, and `_pinned_targets()` raises rather than fail open |
| `tests/test_pinned_figures_every_home.py` | `:53-55` (`load_registry`), `:88-93` (per-entry), `:104-121`, plus corrupt/delete/italicise/wrap arms | every `artifact_figures` entry, parameterised | **Yes**, per entry, and each entry must also *prove it can fail* under mechanical corruption |
| `tests/test_pin_remediations_name_the_generator_that_writes_the_artifact.py` | `:30,39-41,55-68` | `artifact_figures[].regenerate` | Asserts the named script exists and actually names the artifact the pin reads. Not a value comparison |
| `research/modalities/tests/test_lint_consistency.py` | `:342-345`, `:351-357` | `supersession_markers`; every `superseded[].pattern` | Per-entry policy assertion (pattern not a bare number; no self-clearing marker). Not a value comparison |
| `research/autonomy/tests/test_the_clause_count_is_never_typed.py` | `:57,93-95` | `supersession_markers` | Uses them to clear/flag clause-count claims elsewhere |
| `research/modalities/tests/test_throughput_provenance.py` | `:161-166` | `superseded[].id` set | Asserts three specific retired card ids are registered. Registration check, not value comparison |
| `research/manuscripts/claim_coverage.py` | `:47,495-505` | `artifact_figures[].context` + `must_appear_in` | Harvests pin patterns for the coverage census. No comparison |
| `research/manuscripts/claim_audit.py` | `:89,487-503` | `artifact_figures` entries targeting one manuscript | Builds evidence handles. No comparison |
| `research/manuscripts/claim_ablation_cache.py` | `:104-108` | the file as a whole | Hashes it as a `pin:` witness input, so re-pinning invalidates cached verdicts. No comparison |

Live gate state at HEAD `408b676` / `7a10026`: `lint_consistency: 0 ERROR across 29 target file(s)`, exit 0.

### The two honest weak points this audit found (reported, not repaired — I authored no patch)

1. **`superseded` has no anti-inertness alarm.** `subset_checks` explicitly errors when its patterns match nothing ("a check that matches nothing silently passes forever", `lint_consistency.py:571-578`); the superseded arm, which holds 81 of the 183 entries, has no equivalent, and 23 of them currently match nothing. Whether each of the 23 is *correctly* inert (the retired value was genuinely removed everywhere) or *silently* inert (the pattern drifted off the text) is **UNKNOWN from this audit** — distinguishing them is exactly the transplant test W28d was dispatched for, and I did not do it.
2. **`nr4a3-covalent-handle-ensemble.yml:88` runs the gate under `|| true`**, so that one workflow reads the registry and discards the verdict. The other two workflows and preflight do not.

## Validation evidence

RUN, all in `/home/user/Rare-cancers`, container Linux 6.18.44, `python3` = `/usr/local/bin/python3`, `pytest` = `/root/.local/bin/pytest` (uv tool venv, per W29f):

```
$ python3 research/manuscripts/lint_consistency.py | tail -5
lint_consistency: 0 ERROR across 29 target file(s)
EXIT=0

$ pytest -q research/manuscripts/tests/test_pinned_figures_every_home.py \
        research/manuscripts/tests/test_pin_remediations_name_the_generator_that_writes_the_artifact.py
294 passed in 1.75s
EXIT=0
```

Entry census and superseded-scope measurement, run as a heredoc `python3` script reading only the registry and the 29 target files (no writes):

```
targets 29 missing: []
superseded total 81 pattern matches somewhere: 58 matches nowhere: 23
artifact_figures 99 artifact missing: []
homes 11 missing homes []
```

PROPOSED (NOT RUN): nothing. I authored no test, patch or gate.

## Limitations

- "Can fail" for the 58 matching superseded entries is inferred from source plus the match measurement, not from a corruption transplant; I did not perturb any file. W28d's transplant, when it lands, is the stronger instrument and may reclassify individual rows.
- The scope measurement is line-oriented and uses the same `re.search` per line as the gate, but does **not** apply `is_cleared`; a pattern that matches only cleared lines is counted as "matches somewhere". So 58 is an upper bound on entries currently doing live work, and 23 is a lower bound on inert ones.
- "Matches nothing" is measured against the 29 `targets` only. Several of the 23 may match text in files outside the target set — that is the registry's intended scoping, not necessarily a defect.
- Single HEAD pair; the registry is 153 KB and I enumerated it structurally rather than reading every entry's prose, so per-entry semantic correctness is not assessed.
- This is an instrument audit. It makes no scientific, EMC efficacy, safety, selectivity or clinical-readiness claim, and says nothing about whether any pinned *number* is scientifically right — only about whether an executable consumer checks it.
- No content-policy refusal occurred.

## Stop condition

Set up front: **stop once every top-level section of the registry has its consumer set enumerated from source, each consumer's use site read, and every entry classified — or at ~40 tool calls / ~40 minutes.** MET, early: all 183 entries classified, all 18 consumers read at their use sites, two confirming runs executed.

## Tool-call and wall-clock count actually used

15 tool calls (13 Bash batches, several carrying two independent commands). Wall clock 04:39:42Z → 04:41:51Z ≈ 2 minutes of measured elapsed repository time within a single turn. Well inside the ~40/~40 target.

## Next concrete action

One specific successor for this lane: **add a `superseded`-arm inertness report to `lint_consistency.py` modelled on the existing `X-pattern-found-nothing` alarm — but as a WARN-level census line, not an ERROR, and only after W28d's transplant separates correctly-inert from silently-drifted entries.** Turning the 23 straight to ERROR would redden the gate on entries that are inert for the right reason, which is the ignored-linter failure the registry's own `_README` warns about. Owner: whoever owns `lint_consistency.py`; I did not author it. Second, smaller item, routable now: the `|| true` on `.github/workflows/nr4a3-covalent-handle-ensemble.yml:88` makes that workflow's registry read decorative — worth a one-line decision from that workflow's owner on whether it is deliberate.
