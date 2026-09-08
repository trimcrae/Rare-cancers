<!-- collected 2026-09-08T04:49:12Z by campaign coordinator; agent id ad3079de420c670a3; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ad3079de420c670a3.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W34c** — verification-mode remediation-advice lane, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

- `date -u` **start** `Tue Sep  8 04:39:14 UTC 2026` · **end** `Tue Sep  8 04:45:50 UTC 2026`
- `git rev-parse HEAD` **start** `408b676aec3625a36917755662516232a27a1278` · **end** `fb1a3f8040537234010114053b36ec55b729c65e`. HEAD moved under me (coordinator landing sibling reports). Verified nothing I measured changed: `diff -rq --exclude=.git --exclude=__pycache__ /home/user/Rare-cancers /tmp/claude-0/w34c/tree`, filtering the campaign directory, returned **one** line only — `.pytest_cache/v/cache/nodeids` (git-ignored, not tracked, not written by me; I ran no pytest). Zero differences under `research/`, `systems/`, `scripts/`.
- `git status --porcelain` **start**: clean except untracked campaign reports. **end**: same, with sibling reports added by the coordinator; **no entry outside `research/autonomy/opus-capacity-campaign-20260908/reports/`**. I ran no git write operation and wrote nothing into the repository. All execution under `/tmp/claude-0/w34c/`, **deleted at end** (`rm -rf /tmp/claude-0/w34c`, confirmed absent).
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start):

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
GLOBAL_AGENT_NO_PROXY=<same no_proxy list>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<truststore/proxy flags only>
NO_PROXY=<same list>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same list>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**No variable names a model.** `date -u` end: `Tue Sep  8 04:45:50 UTC 2026`.

## Question

W34b found that `aso_control_oligos.py --check` prints `re-run without --check`, and that obeying it would revert a documented 2026-08-30 scientific correction held in the committed artifact but absent from the generator. **Is that self-defeating-remediation-advice pattern unique to that module?** Census every module whose check/gate failure message tells the operator to run a command; for each, determine by source reading what that command does to the tracked tree; classify SAFE / LOSSY / UNKNOWN.

## Prior-work check

Read in full first, as dispatched: `COMMON-BRIEF.md` (including "Known, measured, and NOT worth rediscovering"), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W34-unrun-check-census.md`, `reports/W34b-six-red-unrun-checks.md`.

Census commands (live tree):
```
rg -n --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**' -i \
   -e 're-?run (without|with|:| )' -e 'run `?(python3?|scripts/|make |\./)' -e 'to (re)?generate' \
   -e 'regenerate (with|by|via)' -e 'fix(ed)? (it )?(by|with)' --type py --type sh
git grep -n -i -E 'without --check|rerun without|with --write|Regenerate with|Re-?run `|run `python3|redraw it|run \./scripts/' -- '*.py' '*.sh'
```

**No prior campaign report asks this question.** Adjacent siblings checked and confirmed different axes: **W34** = which `--check` modes nothing runs (reachability); **W34b** = why six of those are red (diagnosis); **W27** = what a `--check` compares (assertion scope); **W45** (`W45-regenerate-then-check-census.md`, landed during my run) = whether running the *regeneration* mode on a degenerate source makes the check green (an escape-hatch axis, not a value-destruction axis); **W31e** = self-contradicting message text inside `systems_check.py`. Mine is the only one asking whether the *published remedy* destroys a committed value.

CLOSED-WORK confirmed not replayed: no NR4A Perspective under any framing, no Brenca/Hofvander/pazopanib/sunitinib/Wagner/CTARC/trabectedin route, no GSE4303/GSE28866 re-read, no registry ICD-O work, no publication or aiXiv act, no patient or reagent design work. **W25 was not read or referenced.** No content-policy refusal occurred. Two modules attempted outbound Ensembl egress under my command and got `403 Forbidden` at the proxy; I did not retry, reroute or work around them.

## Method and inputs

- Live checkout `/home/user/Rare-cancers` at `408b676a` → `fb1a3f80`; an isolated scratch copy at `/tmp/claude-0/w34c/tree` (`tar`, `--exclude=./.git --exclude='*/__pycache__'`, 613 MB) for all bulk execution. Python 3.11.15 (`/usr/local/bin/python3`), stdlib only. No GPU, no paid API, no deliberate network.
- **Step 1 — census.** `git grep` over tracked `*.py`/`*.sh` for imperative-command strings, excluding `tests/`, `test_*`, and the campaign directory: **77 hits**. I then hand-separated *emitted gate-failure messages* from (a) in-artifact "DO NOT EDIT / regenerate with" banners, (b) docstrings, (c) design comments. That leaves **~48 real advice-bearing failure messages in 46 modules**, of which **38 are `--check`-shaped artifact gates** and **~10 are `--write`/`--extend`/`--write-view`/`--write-baseline`/preflight advice**.
- **Step 2 — write-site proof BEFORE running.** For each of the 38 I printed the message line ±9 lines together with every write site in the file (`open(...,"w"|"a")`, `json.dump`, `.write_text`, `savefig`, `os.replace`, `shutil.copy`) and read them. **Every one has the same shape**: the `--check` branch `print`s then `return`s (or `raise SystemExit`s) strictly before the write. Examples read verbatim: `aso_control_oligos.py:150-158`, `aso_coverage_ladder.py:1885-1894`, `aso_archive_manifest.py:1956-1975`, `emc_fusion_frame_figure.py:273-287`, `aso_deposit_drift.py:146-155`, `offtarget_chance_baseline.py:704-718` (which documents in-source that until 2026-08-13 `--check` *did* fall through to the write path). Same proof done for the `--write` family: the write is inside `if write:` / `if "--write" in argv` (`extract_requirement_register.py:105`, `submission_citations.py:406-458`, `claim_coverage.py:861`, `lint_readability.py:343`, `emc_systems_map_check.py:1333`).
- **Step 3 — execution.** All 38 `--check` modes run in the **scratch copy** (`timeout 120`, 6-way parallel). The four that came back red were re-run in the live tree only after their non-writing check path was proven. `research/modalities/atr_hrd_sarcoma_series.py` was **never invoked**. `scripts/preflight.sh` was **not** run.
- **Step 4 — value at risk.** For each red, an in-process leaf-diff (import module, call its own `build()`, recursive leaf comparison against the committed file) plus a `difflib` text diff. No advised writing command was run.

## Result

### R1 — The population (PRIMARY)

| | n |
|---|---|
| Tracked non-test `.py`/`.sh` lines matching command-advice patterns | 77 |
| …that are emitted **gate-failure** messages (not banners/docstrings/comments) | **≈48 in 46 modules** |
| …of the `--check` artifact-gate family, executed by me | **38** |
| …**green today** (message cannot fire; advised command reproduces committed state) | **31** |
| …**red today** (message fires) | **4** |
| …**UNKNOWN** (offline egress block confounds the result) | **3** |

### R2 — The four that fire today, classified (PRIMARY)

| # | Message `file:line` | Advised command | Write site | Committed value at risk | Class |
|---|---|---|---|---|---|
| 1 | `research/modalities/aso_control_oligos.py:153` — `aso-control-oligos.json is stale; re-run without --check` | `python3 research/modalities/aso_control_oligos.py` | `:157-158` `open(OUT,"w").write(new)` | `_not_a_claim_of_inertness` would revert from **"a control … CLEARS the same specificity screen"** back to **"FAILS the specificity screen"**, and the `_superseded_…` record of the change would be deleted. Provenance **is** recorded in the tree, inside the artifact's own text: *"⛔ THIS FIELD SAID 'FAILS' UNTIL 2026-08-30 AND WAS THE DIRECT INVERSE OF `_what` IN THE SAME OBJECT … Found by round 22's arithmetic seat."* 36 of 38 leaves (sequences, seed `20260824`, draw counts, duplex measurements) are already byte-equal. | **LOSSY — destroys a dated, recorded correction** |
| 2 | `research/manuscripts/build_aixiv_metadata.py:130` — `… is STALE — rerun without --check` (fires for `--paper fusion-output`; `--paper vaccine-path` is green) | `python3 research/manuscripts/build_aixiv_metadata.py --paper fusion-output` | `:134-135` `open(out,"w").write(rendered)` | `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-aixiv-metadata.json` → key `abstract` (2075 → 2200 chars). The committed metadata reads **"In three cohorts on three platforms that aggregate reaches 39% and 88% of its null threshold"**; the manuscript-derived text reads **"On the two readable array platforms that pooled set reaches 39% and 88%"**, and adds the four-gene-floor sentence. No provenance record protects the committed string. | **LOSSY by definition, but the direction is corrective** — the module builds the abstract *from the manuscript* (`:2` "so the two cannot disagree"); the committed copy is behind, and it is the **wider** of the two claims. Reported, not repaired. |
| 3 | `research/manuscripts/aso_archive_manifest.py:1970` — `STALE: manifest would change — re-run without --check` | `python3 research/manuscripts/aso_archive_manifest.py` | `:1974-1975` | Leaf diff: **exactly 1 of N leaves differs** — `.git_revision`, committed `1a2d667d…`, fresh `fb1a3f80…` (the current HEAD). The same module's `--check --check-archive` mode returns **"manifest inventory is current (repository-state fields not compared)", rc 0**. | **SAFE** — the only overwritten value is a repository-state stamp the module itself classifies as not-compared; no scientific value at risk. |
| 4 | `research/manuscripts/figures/emc_fusion_frame_figure.py:279` — `STALE — an artifact changed since the figure was drawn; redraw it` | `python3 research/manuscripts/figures/emc_fusion_frame_figure.py` | `:287` (`png`/`pdf`) and the provenance stamp at `:79-81` | `emc-fusion-frame-fig1.png/.pdf` and their provenance record. The figure is **not** in `pinned-figures.json` (grep for `fusion-frame`/`emc-fusion` returns only `fusion-partner` rows). | **LOSSY by definition, direction correct** — the module's own docstring at `:73` states the rule: *"a number changed in an artifact and not redrawn is a stale figure, and the fix is to redraw it, never to re-stamp."* W34b independently diagnosed this as an upstream Ensembl re-fetch cascading into an undrawn figure. |

### R3 — The three UNKNOWNs (UNKNOWN)

| Module · message | Why UNKNOWN |
|---|---|
| `research/modalities/aso_noncoding_acceptor_designs.py:1181` | `--check` calls the Ensembl REST lookup unconditionally; three retries returned `<urlopen error Tunnel connection failed: 403 Forbidden>` and the run exited 1. The red is confounded with blocked egress; I did not retry or reroute. |
| `research/modalities/pgr_parent_engagement.py:230` | Same shape, same 403, rc 1. |
| `research/modalities/hla_coverage.py:426` (`⛔ regenerate with python3 …hla_coverage.py`) | Exits **0** offline, but its own message says the AFND frequency figures are *not* checked without the fetch, so the green is partial. What a regeneration would do to the AFND numbers is not determinable offline. |

`research/manuscripts/aso_deposit_drift.py:150` is a **false red of my scratch copy**: rc 1 without `.git`, **rc 0 and silent in the live tree**. Recorded so nobody re-measures it. `research/modalities/aso_taf15_intron2_designs.py:983` also hit the Ensembl 403 but fell back and exited **0**.

### R4 — The 31 green `--check` gates (PRIMARY, class SAFE)

Message cannot fire today; on the current tree the advised command reproduces the committed bytes. Verbatim exit-0 outputs recorded in Validation for: `aso_coverage_ladder`, `aso_journal_tables`, `aso_reagent_coverage`, `aso_sequence_manifest` (782 sequences), `submission_packet`, `submission_metrics`, `submission_tables`, `tcf12_breakpoint_assignment`, `aso_figure_provenance`, `svg_to_print_formats`, `aso_gap_length_tradeoff`, `aso_independent_verification`, `aso_offtarget_duplex_energy`, `aso_offtarget_tissue_expression`, `aso_parent_gap_pairing`, `aso_parent_null`, `aso_taf15_intron2_designs`, `emc_cohort_search`, `emc_prognostic_coefficients`, `emc_radiotherapy_contradiction`, `emc_recurrence_timing`, `emc_surgical_quality`, `junction_aso_thermo`, `ndrg1_panel_attribution`, `nr4a3_fusion_targets_confounds`, `nr4a3_fusion_targets_occupancy`, `nr4a3_fusion_targets_robustness`, `offtarget_chance_baseline`, `pgr_tissue_expression`, `tcf12_offtarget_tissue_expression`, `build_aixiv_metadata --paper vaccine-path`.

### R5 — The non-`--check` advice family (PRIMARY, all SAFE today)

Every one of these is a *write-gated* remedy whose gate is green right now, so the message does not fire: `claim_coverage.py:795` (`--write`) → rc 0 "reproduces from the live census (28 documents)"; `derived_ids.py:171` (`--extend`) → rc 0 "83 route→id bindings, frozen and agreeing"; `ledger_schema.py:617,620` (`priority.py --write`) — library, header-vs-rows recomputation; `submission_citations.py:479` (`--write`) → rc 0 "citation numbering is current"; `lint_readability.py:380` (`--write-baseline`) → rc 0; `systems/extract_requirement_register.py:108` (`--write`, writes `systems/graph/*.json`) → rc 0 "graph already agrees with the roadmap — nothing to write"; `emc_systems_map_check.py:1349,1353` (`--write-view`) → rc 0, 155 items, 0 ERROR, 2 WARN; `lint_consistency.py:302` (`vast_cost_model.py`) → rc 0, 0 ERROR across 29 files. `push_guard.py:118,128,165` advises `./scripts/preflight.sh`, which is a gate, not a generator.

**One structural near-miss worth the owner's attention, not a repair:** `lint_readability.py:380` is the only *other* message in the repository that advises re-pinning a committed value **after** the check detected that a hedge or limitation was lost. It is guarded by intent (*"⛔ Do not delete a clause to get under the line, and do not raise the ceiling … if it left on purpose, re-pin with `--write-baseline` IN THE SAME COMMIT"*), so it is not self-defeating — but it is the same *shape* as `aso_control_oligos.py`, with the safeguard that `aso_control_oligos.py` lacks.

### R6 — Answer to the question

**The pattern is not unique, but the *destructive* instance is.** Of ~48 advice-bearing gate messages, 4 fire today; of those, exactly **one** — `aso_control_oligos.py:153` — advises a command that would overwrite a committed value the tree explicitly records as a dated scientific correction. Two more (`build_aixiv_metadata` fusion-output, `emc_fusion_frame_figure`) would overwrite committed bytes, but in both the committed side is the stale side and the module's own design documents the regeneration as the correct fix. One (`aso_archive_manifest`) touches only a `git_revision` stamp. The distinguishing property is **not** the message wording, which is near-identical boilerplate across ~30 modules; it is whether a hand-applied correction was ever carried back into the generator. `aso_control_oligos.py` is the only module in this census where it was not.

## Validation evidence

**Environment for every command**: Linux 6.18.44-fc-v24 x86_64, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Python 3.11.15, stdlib only. `scripts/preflight.sh` **not** run; `PREFLIGHT_FULL` **not** set; `atr_hrd_sarcoma_series.py` **never invoked**; no advised writing command was executed.

**RUN — batch of 38 `--check` modes**, cwd `/tmp/claude-0/w34c/tree`, `timeout 120 python3 <mod> --check`, `xargs -P 6`. Verbatim reds:
```
1  research/manuscripts/aso_archive_manifest.py   STALE: manifest would change — re-run without --check
1  research/manuscripts/aso_deposit_drift.py      the declared deposit drift is not the measured one … rerun it without --check
1  research/manuscripts/figures/emc_fusion_frame_figure.py   STALE — an artifact changed since the figure was drawn; redraw it
1  research/modalities/aso_control_oligos.py      aso-control-oligos.json is stale; re-run without --check
2  research/manuscripts/build_aixiv_metadata.py   error: the following arguments are required: --paper
1  research/modalities/aso_noncoding_acceptor_designs.py  <urlopen error Tunnel connection failed: 403 Forbidden>
1  research/modalities/pgr_parent_engagement.py           <urlopen error Tunnel connection failed: 403 Forbidden>
```
**RUN — live-tree re-run of the reds** (each check path proven non-writing first), cwd `/home/user/Rare-cancers`:
```
aso_archive_manifest.py --check                  → STALE: manifest would change — re-run without --check
aso_archive_manifest.py --check --check-archive  → manifest inventory is current (repository-state fields not compared)
aso_deposit_drift.py --check                     → (no output; green in the live tree)
figures/emc_fusion_frame_figure.py --check       → STALE — an artifact changed since the figure was drawn; redraw it
aso_control_oligos.py --check                    → aso-control-oligos.json is stale; re-run without --check
build_aixiv_metadata.py --paper fusion-output --check → …-aixiv-metadata.json is STALE — rerun without --check
build_aixiv_metadata.py --paper vaccine-path --check  → emc-vaccine-path-aixiv-metadata.json: up to date
```
**RUN — leaf diff, archive manifest** (`/tmp/claude-0/w34c/diff2.py`, import + `build()` + recursive leaf compare, no write): `archive_manifest differing leaves: 1` / `COMMITTED .git_revision = '1a2d667d77405070d794b1383961bacf3ad2951f'` / `FRESH = 'fb1a3f8040537234010114053b36ec55b729c65e'`.

**RUN — text diff, aiXiv metadata** (`/tmp/claude-0/w34c/diff3.py`, `difflib`, no write): single differing key `abstract`, committed 2075 chars vs fresh 2200; opcodes quoted in R2 row 2.

**RUN — non-writing proof, negative control**: `diff -rq --exclude=.git --exclude=__pycache__` live vs scratch after all 45+ executions → the only non-campaign line is `.pytest_cache/v/cache/nodeids` (git-ignored). `git status --porcelain` shows no modification anywhere in the tree.

**PROPOSED (NOT RUN)**: re-running `aso_noncoding_acceptor_designs.py --check`, `pgr_parent_engagement.py --check` and the AFND half of `hla_coverage.py` on a networked Actions runner to resolve the three UNKNOWNs. Every advised writing command in R2 remains NOT RUN by design.

## Limitations

- **Class SAFE is a statement about this tree at `408b676a`/`fb1a3f80`, not a property of the module.** A green `--check` means the advised command reproduces the committed bytes *today*; the same message becomes LOSSY the moment anyone hand-edits the artifact without carrying the edit into the generator. That is exactly how `aso_control_oligos.py` got here, and 30 modules share its message boilerplate with no structural protection.
- The census is string-pattern based over tracked `*.py`/`*.sh`. A failure message that advises a command in wording my patterns miss is UNKNOWN, not absent. Workflow YAML `run:` advice and Markdown remedies were out of scope.
- Three modules are UNKNOWN purely because of the 403 at the egress proxy. Absence of a measurement is not a green.
- **Nothing here is a scientific result.** A stale artifact says nothing about EMC biology, efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab. R2 row 1 concerns the *wording of a caveat about control oligos*, not any property of a reagent.
- I authored no repair, patch, gate or test, and weakened, relaxed or reordered no guard.

## Stop condition

Set up front: **stop once every advice-bearing check/gate failure message in the tracked non-test corpus is enumerated, each has been classified by source reading plus (where safely executable) a non-writing run, and every LOSSY case has message line, advised command, write site and value at risk.** **MET.** 48 messages enumerated, 38 executed, 4 fire, all 4 characterised at leaf level, 3 honestly UNKNOWN.

## Tool-call and wall-clock count actually used

**22 tool calls; 6 min 36 s wall clock** (04:39:14Z → 04:45:50Z). Target was ~40 and ~40 min; returning early.

## Next concrete action

**One finite task, and it is a routing, not a repair:** the coordinator should attach this census as the *generality answer* to W34b's existing owner referral for `research/modalities/aso_control_oligos.py`, with the measured framing that the destructive-advice instance is **1 of ~48**, so the correct fix is a two-string generator edit by the ASO owner and **not** a repository-wide message rewrite. Secondary, to a different owner: `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-aixiv-metadata.json` currently publishes a **wider** claim ("three cohorts on three platforms") than its own manuscript ("the two readable array platforms"), and that file is aiXiv-facing metadata — a manuscript-owner decision, not a tooling one, and no publication act should follow from this report.
