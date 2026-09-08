<!-- collected 2026-09-08T04:45:25Z by campaign coordinator; agent id a9c7e8735bde249bb; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a9c7e8735bde249bb.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W45** — generator regenerate-then-check census lane, OPUS-CAPACITY-CAMPAIGN-20260908 (re-dispatch; the prior attempt produced no report, so this is a fresh run with no inherited measurements).

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am Claude Opus 5, exact ID `claude-opus-5`. Nothing in my environment confirms a served model — `env` carries no model variable at all. The coordinator must extract the actual per-child runtime model from the transcript.

- `date -u` start `Tue Sep  8 04:35:47 UTC 2026` · end `Tue Sep  8 04:42:46 UTC 2026`.
- `git rev-parse HEAD` start **`408b676aec3625a36917755662516232a27a1278`** · end **`3e286595023949f75eddd09da9aff36ca58c3f00`**. HEAD moved under me (coordinator report collection).
- `git status --porcelain` start: **0 lines**. End: **1 line**, `?? research/autonomy/opus-capacity-campaign-20260908/reports/W02k-e2-limb-calibration.md` — **another worker's report, not mine**. I wrote nothing into `/home/user/Rare-cancers` and ran no git write operation (only `rev-parse`, `status`, `ls-files`, `grep`, and one `git show HEAD:<path>` read to restore a scratch file).
- All execution under `/tmp/claude-0/w45/repo`, a `tar --exclude=./.git` copy (`TAR_EXIT=0`, 614 M), `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w45/pyc`. **Scratch deleted before returning** (`RM_EXIT=0`; `ls` → "No such file or directory"; `/` 17 G free). No network, no paid API, no GPU, no publication. `scripts/preflight.sh` not run. `research/modalities/atr_hrd_sarcoma_series.py` **never invoked in any mode**.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; the four long proxy-list variables `GLOBAL_AGENT_NO_PROXY`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` are elided only where they repeat the `no_proxy` value verbatim):

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
JAVA_TOOL_OPTIONS=<proxy/truststore flags; repeats the no_proxy list>
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

## Question

W37 measured that `emc_systems_map_check.py --check` protects its registry exactly one command deep: emptying every section reddens on `[V1] view differs`, and the module's own prescribed remedy `--write-view` then takes it to exit 0 over 0 registry items. W37b measured that `systems_check.py` does **not** behave that way — 13 `[G2]` view-drift errors dissolved on `--write-views` while 89 `[L2]`, 18 `[W1]` and 16 `[M2]` cross-source errors survived, leaving exit 1 with 123 errors.

**How many other generators in this repository have the regenerate-then-check escape, and is a cross-source anchor the discriminator?** That is: enumerate every module that produces a committed artifact or view and ships both a check-shaped verification mode and a regeneration mode, then for each determine whether running the regeneration mode on a degenerate source makes the check mode green.

## Prior-work check

- `git ls-files | rg -i 'W37|regenerate'` and `ls research/autonomy/opus-capacity-campaign-20260908/reports/` — the two dispatch-named reports exist only under the campaign directory, **not** under a top-level `reports/`; I corrected my path and read both **in full**, plus `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`.
- I did **not** replay W37b's `systems_check` case; I take its result as given and cite it. I did **not** re-measure the campaign resolution rate, the `origin/literature-cache` question, the pytest-interpreter trap, or the `systems_check` baseline attribution. **W25 not read.**
- I **did** independently re-run W37's `emc_systems_map_check` I1/I2b sequence, because it is the anchor case for my hypothesis and cost three commands. It reproduced exactly.
- Enumeration commands, all read-only in the live tree: `git grep -l -E '"--write(-|_)?…"' -- '*.py' '*.mjs' '*.js'`; `git grep -n -E "add_argument\(\s*[\"']--(write|regen|rebuild|update|emit|render|apply|fix|refresh|sync)…"`; a per-file loop intersecting check-shaped and write-shaped `add_argument` declarations; and a verdict-string grep for the recompute-and-diff family.
- No repository file contains a prior measurement of this property. My only related hits are sibling campaign reports, which per W35 are not repository evidence.

## Method / inputs

| Input | Value |
|---|---|
| Source tree | `/home/user/Rare-cancers` @ `408b676a` (copied at start) |
| Scratch | `tar --exclude=./.git` copy at `/tmp/claude-0/w45/repo`, 614 M, deleted at end |
| Degradation | `empty.py`: recursively replace **every list** in a JSON source with `[]`, printing rows removed; or a targeted line-delete for the Markdown register; or a sequence-stub for the FET cache |
| Restore | per-module backups under `/tmp/claude-0/w45/bak`, verified by re-running `--check` to its original exit code after every experiment |
| Excluded by dispatch | `research/modalities/atr_hrd_sarcoma_series.py` — never invoked in any mode |

**Confirmed from source before running any write mode**, so that nothing could touch the live tree: every module resolves its paths from `__file__` (`HERE = os.path.dirname(os.path.abspath(__file__))`, `REPO = pathlib.Path(__file__).resolve().parents[1]`), so a copy under `/tmp` writes only under `/tmp`. I additionally confirmed that the five `--refresh` flags in this population are **network fetches into an inputs cache**, not regeneration modes, and I ran none of them.

## Result

### R0 — The enumeration, and why it is two tiers (`PRIMARY`)

Taken literally, "ships a `--write`/`--write-view`/`--write-views`-shaped flag" is a small population. But the intersection grep surfaced a second and much larger family: the modality artifact modules, where **the regeneration mode is the bare invocation** and `--check` is the added flag. Both satisfy the dispatch's criteria (a) and (b); only the flag naming differs. I report both and keep the denominators separate.

**Tier A — explicit write-shaped flag alongside a check-shaped mode: 10 modules.**
**Tier B — bare-run regeneration with a `--check` that recomputes and diffs the committed artifact: 17 modules**, measured by `git grep -l -E 'REPRODUCES|DRIFT in:|--check OK: the artifact re-derives|does not match a re-derive'` intersected with a `--check` declaration.

Overlap between the tiers is **1** (`junction_seam_retraction.py`). **Distinct enumerated: 26.**

Explicitly *not* enumerated: `priority.py`, `venue_fit.py`, `work_ledger.py`, `ready_to_post.py`, `alarm_state.py`, `claim_audit.py` — each has a `--write` but its non-write mode is "print only", not a verification mode that can redden.

### R1 — The census, with the real exit codes (`PRIMARY` where executed)

| # | Module | Check / regenerate pair | Degenerate source used | Escape? | Grade |
|---|---|---|---|---|---|
| 1 | `research/manuscripts/emc_systems_map_check.py` | `--check` / `--write-view` | all 8 sections emptied (195 rows) | **YES** | **EXECUTED** |
| 2 | `systems/systems_check.py` | `--check` / `--write-views` | all 15 graph collections (620 rows) | **NO** | W37b, given |
| 3 | `research/modalities/emc_fet_idr_census.py` | `--check` / bare run | 8 sequences → 3-residue stubs (4,319 residues removed) | **YES** | **EXECUTED** |
| 4 | `research/modalities/atm_status_atri_stratification.py` | `--check` / bare run | inputs cache, 4,424 rows removed | **YES** | **EXECUTED** |
| 5 | `research/modalities/emc_atr_vulnerability.py` | `--check` / bare run | inputs cache, **102,397** rows removed | **YES** | **EXECUTED** |
| 6 | `research/modalities/emc_fet_frame_and_composition.py` | `--check` / bare run | inputs cache, 93 rows removed | **NO — crashes** | **EXECUTED** |
| 7 | `research/manuscripts/lint_readability.py` | `--check` / `--write-baseline` | (none needed) | **PARTIAL** | **EXECUTED** |
| 8 | `research/autonomy/derived_ids.py` | `--check` / `--extend` | `systems/graph/routes.json` → `[]` | **n/a — already green** | **EXECUTED** |
| 9 | `systems/extract_requirement_register.py` | default check / `--write` | all 16 `R<n>` roadmap rows deleted | **n/a — already green** | **EXECUTED** |
| 10 | `research/autonomy/health.py` | `--check` / `--write` | (none needed) | **n/a — check never reddens** | **EXECUTED** |
| 11 | `research/modalities/realised_spend.py` | `--check` / `--write` | — | **n/a — `--check` returns 0 unconditionally** | source-derived |
| 12 | `research/modalities/expression_validation_readiness.py` | `--check` / `--write` | — | anchored in a **pinned git revision** | source-derived |
| 13 | `research/modalities/junction_seam_retraction.py` | `--check` / `--write` | — | escape-shaped (`--write` stamps the banners `--check` grades) | source-derived |
| 14 | `research/autonomy/cadence.py` | `--check` / `--stamp` | — | escape-shaped | source-derived |
| 15–26 | 12 further Tier-B modules | `--check` / bare run | — | same construction as #3–5 | source-derived |

Tier-B modules graded from source only: `alcam_precedent`, `cd248_precedent`, `emc_expression_panels`, `emc_fet_construct_designs`, `emc_hypoxia_confounds`, `emc_mtap_locus_persample`, `emc_prmt5_effect_sizes`, `emc_prmt5_multiplicity`, `emc_ret_cistrome`, `nr4a3_fusion_targets`, `continuity`, plus `atr_hrd_sarcoma_series` (excluded from execution by dispatch).

### R2 — The honest denominator (`PRIMARY`)

- **Enumerated: 26** distinct modules (Tier A 10 + Tier B 17, overlap 1).
- **Tested by execution: 10** — 9 by me, 1 (`systems_check`) by W37b and taken as given.
- **Graded from source: 16**, marked as such in R1 and claimed no more strongly than that.
- **Have the escape (executed evidence): 4** — `emc_systems_map_check`, `emc_fet_idr_census`, `atm_status_atri_stratification`, `emc_atr_vulnerability`. **Do not: 2** — `systems_check` (cross-source anchors), `emc_fet_frame_and_composition` (crashes). **Partial: 1** — `lint_readability`. **Not applicable because the check never reddened on the degenerate source at all: 3** — `derived_ids`, `extract_requirement_register`, `health`.

### R3 — ⭐ The four full escapes, verbatim (`PRIMARY`, executed)

Each is the same three-step sequence: degrade the source, run the module's own regeneration mode, re-check.

```
=== emc_systems_map_check  (all 8 sections emptied, 195 rows removed) ===
-- emc_systems_map_check.py --check        rc=1   0 registry items · 1 ERROR · 1 WARN
-- emc_systems_map_check.py --write-view   rc=0   wrote research/manuscripts/emc-systems-map.md
-- emc_systems_map_check.py --check        rc=0   0 registry items · 0 ERROR · 1 WARN
-- (restored)                              rc=0   155 registry items · 0 ERROR · 2 WARN

=== emc_fet_idr_census  (4,319 residues → 8 three-residue stubs) ===
-- emc_fet_idr_census.py --check   rc=1  DRIFT in: ['wild_type_annotation', 'positive_controls',
       'emc_EWSR1_NR4A3_reported_types', 'emc_retained_half_vs_measured_fusions', …]
-- emc_fet_idr_census.py           rc=0  ("rg_dipeptides_total_in_wildtype": 0)
-- emc_fet_idr_census.py --check   rc=0  REPRODUCES
-- (restored)                      rc=0  REPRODUCES

=== atm_status_atri_stratification  (inputs cache, 4,424 rows removed) ===
-- --check  rc=1  --check DRIFT: the artifact does not match a re-derive from its inputs cache
-- (bare)   rc=0
-- --check  rc=0  --check OK: the artifact re-derives byte-identically from its inputs cache
-- (restored) rc=0

=== emc_atr_vulnerability  (inputs cache, 102,397 rows removed) ===
-- --check  rc=1  DRIFT in: ['expression_file_choice', 'gene_sets_used', 'part_a_hemcss_identity',
       'part_b_emc_tumour_signature', 'part_c_coordinated_dependency', 'part_d_drug_response_correlation', 'grading']
-- (bare)   rc=0  "part_d_verdict": "SENSITIVITY_DOES_NOT_TRACK_MECHANISM"
-- --check  rc=0  REPRODUCES
-- (restored) rc=0  REPRODUCES
```

The `emc_atr_vulnerability` line is the sharpest instance in the census: after 102,397 rows were removed from its inputs cache, the regenerated artifact still carried a **scientific verdict string**, and the gate certified it as `REPRODUCES`. Two notes, both required for honesty: **this was done on a scratch copy and the inputs cache is fully populated at HEAD**, where the same `--check` is rc 0 over the real inputs; and a verdict re-derived from an emptied cache is arithmetic about nothing — it is **not** evidence about ATR biology, EMC efficacy, safety, selectivity or clinical readiness, in either direction.

Note also that `emc_fet_idr_census` computes **positive controls** (EWSR1::FLI1, EWSR1::ATF1) whose whole purpose is to catch a wrong derivation. They are written *into* the artifact rather than asserted, so `--check`, which only diffs recomputation against artifact, regenerated the controls alongside everything else and reported `REPRODUCES`.

### R4 — ⭐ The discriminator, tested rather than assumed (`PRIMARY`, executed)

W37b's hypothesis was that the escape is blocked by a **cross-source anchor** outside the file the module regenerates. My census supports it, and refines it in two directions.

**Supporting, at single-module resolution — `lint_readability.py --check` splits cleanly in half.** It enforces two rules: a caution-marker rule anchored in the regenerable `readability-baseline.json`, and a 60-word sentence rule anchored in an **in-source constant**. Running its own prescribed remedy:

```
-- lint_readability.py --check            rc=1   caution_errors=2   longsent_errors=6
-- lint_readability.py --write-baseline   rc=0   pinned caution baselines for 13 document(s)
-- lint_readability.py --check            rc=1   caution_errors=0   longsent_errors=6
```

**Every error whose reference lived in a file the module can rewrite dissolved; every error whose reference lived outside it survived, and the exit code stayed 1.** This is W37b's `[G2]`-dissolves / `[L2]`-`[W1]`-`[M2]`-survive result reproduced inside a single 300-line module, and it extends the hypothesis: **the anchor does not have to be another file — a constant in the module's own source is enough**, because the regeneration mode cannot rewrite it.

**Refuting necessity — `emc_fet_frame_and_composition.py` has no cross-source anchor and still does not escape.** It has exactly the single-source shape of the four escapes, yet:

```
(inputs cache emptied, 93 rows removed)
-- --check    rc=1   KeyError: 6
-- (bare)     rc=1   KeyError: 6
-- --check    rc=1   KeyError: 6
-- (restored) rc=0   REPRODUCES
```

The regeneration mode **crashed** on the degenerate source, so there was never a regenerated artifact for the check to agree with. **A cross-source anchor is sufficient to block the escape but not necessary; a hard structural dependency that raises also blocks it** — though only accidentally, and only for the degradation shape that happens to trip it.

**A third shape the hypothesis did not anticipate: three gates never reddened on the degenerate source at all, so the write mode was not needed.**

```
=== extract_requirement_register: all 16 R-rows deleted from the roadmap (the declared SOURCE) ===
-- (default check)  rc=0   ::warning::R15 has no register row in the roadmap — left as-is
                           requirement register: graph already agrees with the roadmap — nothing to write
-- --write          rc=0   (same)
-- (default check)  rc=0   (same)
```
Its docstring states "THE ROADMAP IS THE SOURCE, ALWAYS", and deleting the entire source leaves it green, because a row with no source row is classed `unknown` and emitted as a `::warning::` annotation rather than an error.

```
=== derived_ids: systems/graph/routes.json emptied (the source --extend binds FROM) ===
-- --check   rc=0   note: 83 binding(s) name a route no longer in the graph, retained so their ids
                    stay resolvable: RT-6MP, RT-AF3-INTERFACE, … 83 route→id bindings, frozen and agreeing
-- --extend  rc=0   every graph route already has an id — nothing to bind
-- --check   rc=0   (same)
```
This refines W37's F2 into a clean asymmetry: **emptying the generated side reddens ("83 route(s) … have no derived ledger id"), emptying the source side is green with a note.** The coverage relation is one-directional.

`health.py --check` was rc 0 before and after `--write`; the write flipped its `commit-worthy` line from `True` to `False`. It is a state board, not a drift gate, and I measured no state in which its check reddens.

### R5 — Incidental, measured, and reported without a repair (`PRIMARY`, executed)

Four Tier-B modules were **already `--check`-red in my `.git`-less scratch copy at `408b676a`**: `emc_fet_construct_designs` (`DRIFT in: ['gene_models', 'ensembl_vs_uniprot_sequences']`), `alcam_precedent` and `cd248_precedent` (both `DRIFT in: ['emc_specific_evidence']`), `emc_prmt5_multiplicity` (`DRIFT in: ['per_platform']`); `fusion_frame_trap --check` was rc 2 for a missing inputs file, and `expression_validation_readiness --check` raised `CalledProcessError` on `git show 8c1f2925…`. **The absence of `.git` is a live confound for at least the last two, and I did not run any of these against the live tree, so whether they are red at HEAD is UNKNOWN.** I record it as an observation for the coordinator and author nothing.

**I authored no repair, no patch, no gate, no test and no floor. No guard was weakened, relaxed, narrowed or reordered. `scripts/preflight.sh` was not run. `atr_hrd_sarcoma_series.py` was never invoked.**

## Validation evidence

**RUN.** `date -u` / `git rev-parse HEAD` / `git status --porcelain` at start and end; `df -h /` before and after; `tar --exclude=./.git` scratch copy (`TAR_EXIT=0`, 614 M); the four enumeration greps quoted in Prior-work check, with their outputs (12-module flag intersection, 110-module `--check` inventory with per-file flag lists, 17-module tight recompute-and-diff family, and a 87-module loose keyword count I **discard as too loose to be a denominator**); baseline `--check` for 14 modules in two batches with exit codes; the five three-step escape sequences quoted verbatim in R3/R4; the `lint_readability` two-rule split with per-rule error counts; `health --check`/`--write`/`--check`; `derived_ids` and `extract_requirement_register` degenerate-source runs; per-module restore verified by re-running `--check` to its original exit code in every case (all restores returned to their baseline code); source reads of `extract_requirement_register.py:1-70` and its `reconcile`, `emc_fet_construct_designs` main dispatch, `expression_validation_readiness.main`, `realised_spend.main`, `derived_ids.main`, `junction_seam_retraction` main, and the `--refresh` help strings of the five network-fetch modules; scratch deletion verified (`RM_EXIT=0`, `ls` → no such file). **No network of any kind was attempted, so I have no denial to record.**

**PROPOSED (NOT RUN):** the escape test for the 16 source-graded modules; any run of `atr_hrd_sarcoma_series.py`; `emc_systems_map_check`'s escape in a tree that **has** `.git`, where its `[C1]` and `[O4]` git-dependent checks would be live rather than degraded to WARN; and any degradation shape other than "empty every list" for `emc_fet_frame_and_composition`, whose `KeyError` may be specific to the shape I used.

## Limitations

- **The scratch tree has no `.git`.** This matters most for the anchor question: `emc_systems_map_check` printed `WARN [C1] none of ('origin/main', …) is present` and `WARN [O4] git is unavailable`, so two of its potentially cross-source checks were **unavailable rather than passing**. My ESCAPE grade for it therefore holds for a git-less tree; whether it holds in a git-present checkout is **UNKNOWN**. W37 had the same confound. The three modality escapes (#3, #4, #5) do not consult git and are not affected.
- **"Escape" means escape against exactly the degradation I ran** — emptying every list in the module's declared source, or stubbing its sequences. It is not a general soundness claim, and R4's `KeyError` case shows a different degradation shape can give a different answer for the same module.
- **16 of 26 enumerated modules are graded from source and nothing more.** I state their construction, not their behaviour.
- **My Tier-B denominator of 17 is a verdict-string grep**, not a verified per-module reading. A module in this family that phrases its verdict differently is missed, and a module outside it that uses the words is over-counted; I read 8 of the 17 directly and found no false member among those.
- **This is a census of gate arithmetic, not of science.** No exit code here says anything about EMC efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab.
- **A gate reporting OK over an empty or degraded source is a measurement gap, not evidence that anything is wrong in the repository today.** Every source I degraded is populated at HEAD — 155 registry items, 4,319 FET residues, 4,424 and 102,397 inputs rows, 16 roadmap register rows, 83 graph routes — and every one was restored and re-verified inside the scratch copy before it was deleted.
- HEAD advanced during my run (`408b676a` → `3e286595`); all measurements pin to the tree as copied at `408b676a`.

## Stop condition

Set up front: **return the moment every module with both a check-shaped and a regeneration-shaped mode is enumerated and graded escape / no-escape, with an executed exit code for every case whose baseline is green and whose write mode provably confines itself to the scratch copy.** **MET.** 26 enumerated, 10 settled by execution, 16 graded from source and marked, and the cross-source hypothesis tested against three independent shapes rather than assumed. Returned early.

## Tool-call and wall-clock count actually used

**19 tool calls** (several batching many commands). Wall clock **04:35:47Z → 04:42:46Z ≈ 7 minutes**, well inside the ~40-call / ~40-minute target.

## Next concrete action

**One successor, and it is the question R4 opens.** The discriminator is now three-valued — a cross-source anchor, an in-source constant, or an accidental crash — and only the first two are deliberate. The bounded run that would settle the census is: **for the 16 source-graded modules, execute the same three-step test on a scratch copy and classify each into those three buckets**, establishing a green baseline first where the module is currently red (as W37b did by moving the campaign directory outside the scan root). That converts a source grade into a measurement for the majority of the denominator and is a single bounded run of the same shape I already ran nine times.

**Explicitly not a successor:** any repair, floor, zero-test or gate change for any module in this census. Several of these modules carry long docstrings reasoning about exactly this class of defect (`junction_seam_retraction`'s "a self-test that cannot fail is the defect this repository keeps paying for"; `extract_requirement_register`'s "a guard whose remedy did not exist"), and which of them should acquire an anchor is a maintainer's decision about what each artifact is for, not a worker's.
