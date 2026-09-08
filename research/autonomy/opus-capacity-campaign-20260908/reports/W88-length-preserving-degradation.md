<!-- collected 2026-09-08T05:16:12Z by campaign coordinator; agent id ad176ce0bdd1bf3e0; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ad176ce0bdd1bf3e0.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W88** — regenerate-then-check escape lane, W58's named successor. OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am Claude Opus 5, exact ID `claude-opus-5`. Nothing in the environment confirms a served model — `env` carries no model variable. The coordinator must extract the actual runtime model from the transcript.

- `date -u` start **`Tue Sep  8 05:03:23 UTC 2026`** · end **`Tue Sep  8 05:13:00 UTC 2026`**.
- `git rev-parse HEAD` (live tree) start **`cf0af448f41bf6142fe0689d68f8da1430ad1b55`** · end **`997bc9e769da6bf606392941d46d20b319beab85`** (HEAD advanced under me; coordinator report collection). The `cp -a` scratch copy was taken moments after the start reading and its embedded `.git` reported HEAD **`9a936582365c8b46cb69e171d9fcd063c6a6add9`**; all measurements pin to the tree **as copied**, at `9a936582`.
- `git status --porcelain` on `/home/user/Rare-cancers`: **0 lines at start, 0 lines at end.** I wrote nothing there and ran no git write operation (only `rev-parse`, `status`). Scratch repo `git status --porcelain` was also **0 lines** at the end of all experiments (before deletion).
- All execution under `/tmp/claude-0/w88/repo`, a **`cp -a` copy including `.git`** (`CP_EXIT=0`, `.git` present), `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w88/pyc`. **Scratch deleted before returning** (`RM_EXIT=0`; `ls` → "No such file or directory"; `/` 19 G free). No network attempted; no `--refresh`/`--fetch` mode run; `scripts/preflight.sh` not run; `research/modalities/atr_hrd_sarcoma_series.py` **never invoked in any mode**. No paid API, no GPU, no publication, no human contacted. No content-policy refusal occurred.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (end; the five long proxy-list variables `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` filtered out of this paste — they repeat the same host list W58 printed verbatim):

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
PWD=/tmp/claude-0/w88/repo
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

## Question

W58 found that the escape discriminator's values are **tried in execution order, not exclusive**: `emc_prmt5_multiplicity` owns a deliberate cross-cache refusal (`emc_prmt5_multiplicity.py:568-575`) but never reached it, because an `IndexError` from a zip-by-index bug fired first. So a one-shape census reports the *first* blocker, not the strongest.

Bounded question: **re-run the three-step test (degrade → run the regeneration mode → re-check) on the five ACCIDENTAL-CRASH modules and the four ESCAPES, using a LENGTH-PRESERVING degradation — replace list *elements* with nulls or zeros rather than emptying the lists — and record for each whether the module then reaches a deliberate guard, crashes again, or escapes.** Report the class under both shapes side by side.

## Prior-work check

- Read in full as directed: `COMMON-BRIEF.md` (784 lines, both pages), `CORPUS-CONTEXT.md` (82), `CLOSED-WORK.md` (70), `reports/W58-escape-test-sixteen-modules.md` (251). W45's report was read targetedly (`grep -n "fet_frame_and_composition|empty.py|Degradation|KeyError"`) for its degradation shape and its `emc_fet_frame_and_composition` row; I take W45's, W58's, W74's and W37c's results **as given** and did **not** redo the emptying census.
- **W25 not read, not referenced.**
- Module and source discovery was by execution, not by trusting the prior reports: `grep -nE '__file__' <module>.py` and `grep -nE '^[A-Z][A-Z0-9_]* *=.*\.json' <module>.py` over all nine modules. This confirmed **all nine resolve every path from `__file__`** (`HERE = os.path.dirname(os.path.abspath(__file__))`) **before any write mode was run**, so a copy under `/tmp` writes only under `/tmp`.
- No repository file records this property; W58's own "PROPOSED (NOT RUN)" block names exactly this test as unrun. This is not a replay.

## Method and inputs

| Input | Value |
|---|---|
| Source tree | `/home/user/Rare-cancers`, copied at start; scratch `.git` HEAD `9a936582` |
| Scratch | `cp -a` copy at `/tmp/claude-0/w88/repo`, **`.git` included**; deleted at end |
| Pristine restore set | `cp -a` of `research/modalities/` (330 M) taken before any experiment; **full directory restored after every module**, then `--check` re-run and required to equal the step-1 exit code |
| Degradation LP-NUM | every `int`/`float` leaf (not `bool`) → `0`; **every list keeps its length, every dict keeps its keys**, strings untouched |
| Degradation LP-ALL | every scalar leaf (`str`/`int`/`float`/`bool`) → `null`; containers, lengths and keys preserved |
| In-source variant | for `alcam_precedent` / `cd248_precedent`, a module-level walker over `RECORDS` inserted immediately before the `if __name__` guard, applying the same rule in place |
| Green baseline | where step-1 `--check` was red, the module's own bare regeneration was run once and `--check` re-run; all six red modules reached rc 0 before degradation |
| Excluded by dispatch | `research/modalities/atr_hrd_sarcoma_series.py` — never invoked |

The seven-step driver per module: `1 baseline --check → 2 bare regen → 3 --check (green baseline) → 4 degrade → 5 --check → 6 bare regen → 7 --check → 8 full restore → 9 --check == step 1`. Exit codes are the module process's own (`rc=$?` on the command, not on a pipe).

**A measured methodological correction, recorded because it changes the result.** My first LP shape nulled only *scalar elements of lists*. On `emc-construct-inputs.json` that degraded **0 leaves** — its lists hold dicts, so the shape was a silent no-op and the module trivially "escaped". That run is reported here rather than dropped. The two shapes above replace it, and the difference between LP-NUM and LP-ALL turns out to matter (see R2).

## Result

### R1 — Class under both shapes, side by side (`PRIMARY`, executed)

W58/W45 column = the emptying shape (taken as given). W88 column = my length-preserving shape. `rc` triples are (step 5 degraded-check, step 6 regen, step 7 re-check).

| Module | Degraded source | Emptying shape (W45/W58) | LP shape used | LP rc 5/6/7 | **Class under LP** |
|---|---|---|---|---|---|
| `emc_prmt5_multiplicity` | `emc-expression-panels-inputs.json` | ACCIDENTAL CRASH (`IndexError`) | LP-NUM (420,072 in-list + 21,653 outside zeroed) | 1/1/1 | ⭐ **DELIBERATE GUARD REACHED** — `REFUSING TO MERGE — the two caches disagree on the per-sample background` |
| `emc_fet_frame_and_composition` | `emc-construct-inputs.json` | ACCIDENTAL CRASH (`KeyError: 6`) | LP-NUM (641 + 28) | 1/1/1 | **CRASH again** — same `raise KeyError(rank)` at `:112` via `:116` |
| `emc_fet_frame_and_composition` | same | — | LP-ALL (827 + 127) | 1/1/1 | **CRASH, different site** — `TypeError: '<' not supported between 'NoneType' and 'int'` at `:133` |
| `emc_fet_construct_designs` | `emc-construct-inputs.json` | ACCIDENTAL CRASH (`ValueError`) | LP-NUM (641 + 28) | 1/1/1 | **CRASH again — same site**, `:371` `raise ValueError(f"{g['symbol']}: no transcript exon {rank}")` → `ValueError: EWSR1: no transcript exon 12` |
| `emc_fet_construct_designs` | same | — | LP-ALL (827 + 127) | 1/1/1 | **CRASH, earlier site** — `TypeError: object of type 'NoneType' has no len()` at `:859` |
| `emc_expression_panels` | `emc-expression-panels-inputs.json` | ACCIDENTAL CRASH (`IndexError`, masking comprehension) | LP-NUM (420,072 + 21,653) | 1/1/1 | **CRASH again, different site** — `IndexError` at `:1935` `a = [z[i] for i in emc if z[i] is not None]` |
| `nr4a3_fusion_targets` | `nr4a3-fusion-targets-inputs.json` | ACCIDENTAL CRASH (`IndexError`, masking comprehension) | LP-NUM (339,234 + 2,050) | 1/1/1 | **CRASH again, different site** — `TypeError: 'NoneType' object is not subscriptable` at `:1075` in `_global_offset` |
| `emc_ret_cistrome` | `emc-ret-cistrome-inputs.json` | ESCAPES | LP-NUM (3,622,503 + 2,267) | 1/0/0 | **ESCAPES again** (and see R3) |
| `emc_mtap_locus_persample` | `emc-expression-panels-inputs.json` | ESCAPES | LP-NUM (420,072 + 21,653) | 1/0/0 | **ESCAPES again** |
| `alcam_precedent` | in-module `RECORDS` | ESCAPES | LP-NUM | 0/0/0 | **VACUOUS — 0 leaves degraded**; `RECORDS` holds no numbers |
| `alcam_precedent` | in-module `RECORDS` | ESCAPES | LP-ALL (59 leaves nulled) | 1/0/0 | **ESCAPES again** (`DRIFT in: ['binder_precedent']` → regen → `REPRODUCES`) |
| `cd248_precedent` | in-module `RECORDS` | ESCAPES | LP-NUM | 0/0/0 | **VACUOUS — 0 leaves degraded** |
| `cd248_precedent` | in-module `RECORDS` | ESCAPES | LP-ALL (113 leaves nulled) | 1/0/0 | **ESCAPES again** (`DRIFT in: ['records']` → regen → `REPRODUCES`) |

**Tally over the nine modules under a length-preserving shape: 1 reaches a deliberate guard, 4 crash again, 4 escape again.** Green baseline was established first for all six modules whose step-1 `--check` was red (`emc_fet_construct_designs`, `emc_prmt5_multiplicity`, `emc_mtap_locus_persample`, `emc_ret_cistrome`, `alcam_precedent`, `cd248_precedent` — each reached `REPRODUCES` at rc 0 before degradation). `emc_fet_frame_and_composition`, `emc_expression_panels` and `nr4a3_fusion_targets` were rc 0 at step 1 already. **All nine restores matched their step-1 exit code exactly** (`RESTORE_MATCH: base=N now=N`, nine of nine).

### R2 — ⭐ W58's ordering hypothesis is CONFIRMED by execution, for exactly one module (`PRIMARY`)

```
=== emc_prmt5_multiplicity, LENGTH-PRESERVING numeric (420,072 in-list leaves zeroed) ===
-- 1 --check (baseline)   rc=1  DRIFT in: ['per_platform']
-- 2 (bare regen)         rc=0  PRMT5 t=6.674 adjusted p=0.2473 …
-- 3 --check              rc=0  REPRODUCES                    <- green baseline
-- 5 --check degraded     rc=1  REFUSING TO MERGE — the two caches disagree on the per-sample background
-- 6 (bare regen)         rc=1  REFUSING TO MERGE — the two caches disagree on the per-sample background
-- 7 --check              rc=1  REFUSING TO MERGE — the two caches disagree on the per-sample background
-- 9 --check restored     rc=1  DRIFT in: ['per_platform']    <- matches step 1
```

Under W58's emptying shape this module died with an `IndexError` in its background-masking comprehension. Under a length-preserving shape it reaches its own deliberate cross-cache refusal at `emc_prmt5_multiplicity.py:568-575` — the guard whose docstring states *"⛔ THE MERGE IS REFUSED unless the two caches agree on the samples, on their order, on the per-sample background and on every value of every symbol they share"* — and the message names the discrepancy precisely (the per-sample background, not the sample set). **So its true class is CROSS-SOURCE ANCHOR, and the ACCIDENTAL-CRASH grade was an artefact of the degradation shape.** W58's warning was correct and is now measured, not predicted.

**⚠ The ordering problem does not stop at two shapes — it recurses.** Within the length-preserving family, LP-ALL is *more* destructive than LP-NUM and reaches a *different, earlier* blocker in three of three modules where both were run:

- `emc_prmt5_multiplicity` under LP-ALL never reaches its own guard either — it dies at `AttributeError: 'NoneType' object has no attribute 'lower'` in an **imported** module, `emc_atr_vulnerability.py:1612` `_classify_sample`, because nulling strings destroys the annotation text a shared helper parses.
- `emc_fet_frame_and_composition`: LP-NUM → `KeyError` at `:112`; LP-ALL → `TypeError` at `:133`.
- `emc_fet_construct_designs`: LP-NUM → the `:371` `ValueError`; LP-ALL → a bare `TypeError` at `:859`.

The generalisation: **a census over degradation shapes reports the blocker nearest the entry point of the shape it used, in every direction.** "Blocked by an anchor" is a statement about a (module, shape) pair, never about a module. Only the exhaustive claim is safe: a module that escapes under a shape is *unprotected against that shape*; a module that crashes under a shape is *ungraded*, not protected.

### R3 — ⛔ The strongest single measurement: a length-preserving degradation makes `emc_ret_cistrome` publish a *stronger* verdict, not an emptier one (`PRIMARY`, executed)

```
=== emc_ret_cistrome, LENGTH-PRESERVING numeric (3,622,503 in-list leaves zeroed) ===
-- 1 --check (baseline)   rc=1  DRIFT — the derive half is not reproducible
-- 2 (bare regen)         rc=0  "verdict": "MEASURED NR4A OCCUPANCY AT THE RET LOCUS IN 15 OF 64
                                 PUBLIC ChIP-seq EXPERIMENTS (17 of 103 peak sets …)"
-- 3 --check              rc=0  REPRODUCES EXACTLY            <- green baseline
-- 5 --check degraded     rc=1  DRIFT — the derive half is not reproducible
-- 6 (bare regen)         rc=0  "verdict": "MEASURED NR4A OCCUPANCY AT THE RET LOCUS IN 64 OF 64
                                 PUBLIC ChIP-seq EXPERIMENTS (102 of 103 peak sets …)"
-- 7 --check              rc=0  REPRODUCES EXACTLY            <- ESCAPES
-- 9 --check restored     rc=1  DRIFT — the derive half is not reproducible   <- matches step 1
```

Under W58's emptying shape this module degraded *honestly*: the regenerated artifact said `verdict: null, part_2: NO_PEAK_SET_RETRIEVED`. Under a length-preserving shape the same module regenerates a **confident, maximal-sounding verdict string** — 64 of 64 experiments, 102 of 103 peak sets — and the gate certifies it `REPRODUCES EXACTLY` at rc 0. The arithmetic reason is visible in the shape: zeroing the numeric coordinates collapses every peak interval onto the locus, so every peak set "overlaps".

⛔ **This number is arithmetic about nothing.** `64 of 64` is **not** evidence about NR4A occupancy at the RET locus, about NR4A/RET biology, or about EMC efficacy, safety, selectivity or clinical readiness, **in either direction** — and neither is the committed `15 of 64`, which I neither verified nor challenged. The `emc-ret-cistrome-inputs.json` cache is populated at HEAD; it was restored in full and `--check` was re-run to its baseline code before scratch deletion. The finding here is about the **gate**: `REPRODUCES EXACTLY` at rc 0 carries no information about whether the artifact's content is real, and W58's "the artifact says out loud that it has nothing" mitigation is **shape-dependent and does not survive a length-preserving degradation**. There is no wet lab.

The same caution applies to `emc_mtap_locus_persample`, which escaped again and again re-printed `within-EMC Spearman rho = -0.3091, exact p = 0.38691` — unchanged because, as W58 measured, its second source (the committed `emc-expression-panels.json` artifact) was not degraded. **I restate neither that rho nor that p-value as a finding.**

### R4 — The three-file zip-by-index bug was in fact bypassed; the crash simply moved (`PRIMARY`, executed)

W58 predicted a length-preserving shape "should get past" the shared `IndexError`. Measured, per file:

| File | Emptying-shape crash site | LP-NUM crash site | Bypassed? |
|---|---|---|---|
| `emc_prmt5_multiplicity` | masking comprehension `bg[i]` | none — reaches `:568-575` refusal | **yes** |
| `emc_expression_panels` | masking comprehension `bg[i]` | `:1935` `a = [z[i] for i in emc …]`, `IndexError` | **yes** (new, downstream site) |
| `nr4a3_fusion_targets` | masking comprehension `bg[i]` | `:1075` `abs(w['delta_a_minus_b'])`, `TypeError` | **yes** (new, downstream site) |

So the shared bug is genuinely one bug in three files and a length-preserving input clears it in all three; two of the three then hit a *second*, independent fragility further down the same pipeline. `emc_expression_panels:1935` is a second index-length assumption of the same kind (an index list `emc` used against a derived list `z`), not the same line. **I authored no repair, no patch, no gate, no test and no anchor for any of these, and I did not fix the shared index bug.** Which of these should acquire a guard is a maintainer's decision.

`emc_fet_construct_designs` is the one row where the LP shape lands on the *same* site as the emptying shape: `:371` raises `ValueError(f"{g['symbol']}: no transcript exon {rank}")`. That is a raise with a message naming the discrepancy, and it is a deliberate structural precondition on the gene model — but it is an **in-source precondition, not a cross-source comparison**, so I do not promote it to CROSS-SOURCE ANCHOR. It sits between the two classes and the census should say so rather than pick.

### R5 — The in-source `RECORDS` escape is content-type-dependent (`PRIMARY`, executed)

`alcam_precedent` and `cd248_precedent` hold their entire source as an in-module `RECORDS` dict. Measured: **that dict contains zero numeric leaves in both modules** — LP-NUM degraded 0 leaves and the whole three-step test was vacuous (rc 0/0/0 throughout, `--check` never reddened). Under LP-ALL (59 and 113 scalar leaves nulled) both reddened correctly (`DRIFT in: ['binder_precedent']`, `DRIFT in: ['records']`), the bare run rewrote the artifact from the nulled dict, and `--check` returned `REPRODUCES` at rc 0. **Both escape again**, confirming W58 under a second shape. The practical note for any future census: **a numeric-only degradation is a silent no-op against a prose-only source, and a vacuous "escape" is indistinguishable from a real one by exit code alone** — it must be caught by the degrader's own leaf count, which is why I printed one on every run.

## Validation evidence

**RUN.** All commands executed inside `/tmp/claude-0/w88/repo`, exit codes captured directly from the module process.

- `date -u`, `git rev-parse HEAD`, `git status --porcelain` on the live tree at start and end (0 lines both times); `df -h /` at start (16 G free), mid and end (19 G free).
- `cp -a /home/user/Rare-cancers /tmp/claude-0/w88/repo` → `CP_EXIT=0`, `.git` present (`ls -d …/repo/.git` succeeded), scratch `git status --porcelain` = 0 lines after all experiments.
- `cp -a` pristine snapshot of `research/modalities` (330 M) before any experiment; **full `rm -rf` + `cp -a` restore after every one of the 13 module runs**, each followed by a `--check` that matched the step-1 exit code (`RESTORE_MATCH` printed 13/13 matching).
- `grep -nE '__file__'` and `grep -nE '^[A-Z][A-Z0-9_]* *=.*\.json'` over all nine modules **before any write mode ran**; every one anchors on `os.path.dirname(os.path.abspath(__file__))`.
- The seven-step driver executed for: `emc_fet_frame_and_composition` (LP-ALL and LP-NUM), `emc_fet_construct_designs` (LP-ALL and LP-NUM), `emc_prmt5_multiplicity` (LP-ALL and LP-NUM), `emc_expression_panels` (LP-NUM), `nr4a3_fusion_targets` (LP-NUM), `emc_mtap_locus_persample` (LP-NUM), `emc_ret_cistrome` (LP-NUM), `alcam_precedent` (LP-NUM and LP-ALL), `cd248_precedent` (LP-NUM and LP-ALL) — 13 runs, with per-run degraded-leaf counts printed, verbatim tracebacks and verdict lines quoted above.
- The discarded first shape (null only scalar *elements of lists*) is reported in Method rather than dropped: it degraded 0 leaves of `emc-construct-inputs.json` and produced a false "escape" for `emc_fet_frame_and_composition`.
- Scratch deletion verified: `rm -rf /tmp/claude-0/w88` → `RM_EXIT=0`; `ls` → `No such file or directory`.

**PROPOSED (NOT RUN):** any run of `atr_hrd_sarcoma_series.py`; any `--refresh`/`--fetch` mode; LP-ALL for `emc_expression_panels`, `nr4a3_fusion_targets`, `emc_ret_cistrome` and `emc_mtap_locus_persample`; a shape that degrades **both** of `emc_mtap_locus_persample`'s sources; a shape targeted per-module at the specific field a module's own guard compares (which is what would settle the remaining four crash rows); any repair, patch, gate, floor or test — none authored, none proposed as code.

## Limitations

- **Every class here is a statement about a (module, shape) pair.** R2 measures the failure mode directly: the same module gives three different answers under three shapes. Four rows remain **ungraded, not protected** — `emc_fet_frame_and_composition`, `emc_fet_construct_designs`, `emc_expression_panels`, `nr4a3_fusion_targets` crash before any comparison, so whether they own a deliberate guard is **UNKNOWN**.
- The four escapes are escapes **against the shapes I ran**, not a general soundness claim; and the two in-source escapes rest on LP-ALL only, because LP-NUM was vacuous for them.
- **This is a census of gate arithmetic, not of science.** No exit code, verdict string, rho or p-value re-derived from a degraded cache is evidence about NR4A/RET biology, MTAP/CDKN2A status, EMC efficacy, safety, selectivity, therapeutic window or clinical readiness, in either direction. There is no wet lab, and no clinical claim is made here.
- **A gate reporting OK over a degraded source is a measurement gap, not evidence that anything is wrong in the repository today.** Every source I degraded is populated at HEAD; all were restored and re-verified inside the scratch copy before it was deleted.
- All reds and greens are from a `cp -a` copy at scratch HEAD `9a936582`; I ran nothing against the live tree. Whether these codes hold in situ is UNKNOWN, though the copy was byte-identical at copy time. Live HEAD advanced `cf0af448` → `997bc9e7` during the run.
- Crash-site line numbers are from the scratch copy's files and were read from live tracebacks, not from a source citation.

## Stop condition

Set up front: **return the moment all nine modules are classified under a length-preserving degradation by executed three-step test with real exit codes, a green baseline established wherever the module was red, every degraded directory fully restored and its `--check` re-verified to the step-1 code, the scratch tree deleted, and the live `git status --porcelain` confirmed empty.** **MET.** 9 modules, 13 runs, 1 deliberate guard reached / 4 crash again / 4 escape again; 13/13 restores matched; scratch deleted; live tree clean at start and end. Returned early.

## Tool-call and wall-clock count actually used

**17 tool calls** (2 Read, 15 Bash, several batching many commands; 1 run in background). Wall clock **05:03:23Z → 05:13:00Z ≈ 10 minutes**, well inside the ~40-call / ~40-minute target.

## Next concrete action

**One successor, and it is the shape-dependence R2 exposes rather than more shapes.** Shape-by-shape probing cannot terminate — each new shape lands on whatever blocker is nearest its entry point, and after two families the four crash rows are still ungraded. The bounded successor that *can* terminate is **static, per-module, and reads the guard rather than trying to trip it: for the four still-ungraded modules, enumerate every `raise`/`SystemExit`/`assert` in the module and in the modules it imports, and classify each by whether its condition dereferences a source the regeneration mode does not write** (the property that makes `emc_prmt5_multiplicity:568-575` and `emc_hypoxia_confounds:796` real anchors, and `emc_fet_construct_designs:371` an in-source precondition). That yields a per-module *inventory* of candidate anchors and their source-dependence, which a targeted degradation can then confirm one at a time — replacing an unbounded search over shapes with a finite read of the guards. **Explicitly not a successor:** any repair, anchor, floor, zero-test or gate change — including the three `IndexError`/`TypeError` sites and `emc_expression_panels:1935`'s second index-length assumption. Whether an artifact regenerated from a degraded cache should be refusable is a maintainer's decision about what each artifact is for.
