<!-- collected 2026-09-08T05:02:59Z by campaign coordinator; agent id af98812f53a3ecd08; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-af98812f53a3ecd08.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

All experiments complete, scratch deleted, live tree verified untouched.

## Worker

**W58** — regenerate-then-check escape lane (W45's named successor), OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am Claude Opus 5, exact ID `claude-opus-5`. Nothing in the environment confirms a served model — `env` carries no model variable. The coordinator must extract the actual runtime model from the transcript.

- `date -u` start **`Tue Sep  8 04:46:56 UTC 2026`** · end **`Tue Sep  8 04:59:08 UTC 2026`**.
- `git rev-parse HEAD` start **`8a667406e875ae99c7d50347b2e895a177fcb048`** · end **`d5034489077eee6a11ccee088bd5bfccf6f7a8e1`** (HEAD advanced under me; coordinator report collection).
- `git status --porcelain` start: **0 lines**. End: **0 lines**. I wrote nothing into `/home/user/Rare-cancers` and ran no git write operation (only `rev-parse`, `status`, `ls-files`, `cat-file -t`, `grep`).
- All execution under `/tmp/claude-0/w58/repo`, a **`cp -a` copy that INCLUDES `.git`** (`CP_EXIT=0`, 983 M), `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w58/pyc`. **Scratch deleted before returning** (`RM_EXIT=0`; `ls` → "No such file or directory"; `/` 19 G free). No network attempted, no `--refresh`/`--fetch` mode of any module run, no paid API, no GPU, no publication. `scripts/preflight.sh` not run. `research/modalities/atr_hrd_sarcoma_series.py` **never invoked in any mode**.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; four long proxy-list variables `GLOBAL_AGENT_NO_PROXY`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` elided only where they repeat the `no_proxy` value verbatim):

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

W45 enumerated 26 modules with both a check-shaped and a regeneration-shaped mode, settled 10 by execution, and graded **16 from source only**. Its named successor: **run the same three-step test (degrade the declared source → run the regeneration mode → re-check) on those 16, and classify each into the three-valued discriminator — blocked by a CROSS-SOURCE ANCHOR, blocked by an IN-SOURCE CONSTANT, blocked by an ACCIDENTAL CRASH, or ESCAPES** — establishing a green baseline first where the module is currently red, in a copy that includes `.git`.

## Prior-work check

- Read in full, as directed: `COMMON-BRIEF.md` (369 lines), `CORPUS-CONTEXT.md` (82), `CLOSED-WORK.md` (70), `reports/W45-regenerate-then-check-census.md` (258). I take W45's and W37c's results **as given** and did not replay any of the 10 modules W45 settled by execution, nor W37b's `systems_check` case, nor the campaign resolution rate, the `origin/literature-cache` question, the pytest-interpreter trap, or the `systems_check` baseline attribution.
- **W25 not read, not referenced.**
- Module discovery was by `find research -name "<module>.py"` over W45's own named list, then flag enumeration by `grep -oE 'add_argument\("--[a-z-]+"'` and source-path enumeration by `grep -nE '^[A-Z_]+ *= *(os\.path\.join|Path)'`. I did not re-derive W45's enumeration; my population is exactly its 16.
- No repository file contains a prior measurement of this property for these modules; W45's R1 marks all 16 `source-derived`, and its "PROPOSED (NOT RUN)" section names this exact test.

## Method and inputs

| Input | Value |
|---|---|
| Source tree | `/home/user/Rare-cancers` @ `8a667406` (copied at start) |
| Scratch | `cp -a` copy at `/tmp/claude-0/w58/repo`, **`.git` included**, 983 M; deleted at end |
| Pristine restore set | `cp -a` of `research/modalities/` (330 M) and `research/autonomy/` (23 M) taken before any experiment |
| Degradation (JSON-source modules) | `empty.py` — recursively replace **every list** with `[]`, printing rows removed (W45's shape, so results are comparable) |
| Degradation (in-source-record modules) | insert a top-level `RECORDS = {}` immediately before `def main(`, so `derive()` reads an empty record set |
| Green baseline where red | run the module's own bare regeneration once, then re-check |
| Restore | full `cp -a` of both pristine directories after every module, then re-run `--check` and require it to equal the step-1 exit code |
| Excluded by dispatch | `research/modalities/atr_hrd_sarcoma_series.py` — never invoked in any mode |

**Path-resolution confirmed from source BEFORE any write mode ran**, for all 15 executed modules: every one resolves paths from `__file__` (`HERE = os.path.dirname(os.path.abspath(__file__))`, `ROOT = Path(__file__).resolve().parents[2]`, etc.), so a copy under `/tmp` writes only under `/tmp`. Verified end-state `git status --porcelain` = 0 lines.

## Result

### R1 — The census. 15 executed, 1 excluded. (`PRIMARY`)

Exit codes are the real codes of the module process (captured before any pipe; a first pass that leaked `tail`'s status was re-run to fix this).

| # | Module | Regen mode | Degradation | 1 base | 3 green | 4 degraded | 5 regen | 6 re-check | **Class** |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `emc_ret_cistrome` | bare | inputs, 1,431,683 rows | 1 | 0 | 1 | 0 | **0** | **ESCAPES** |
| 2 | `emc_mtap_locus_persample` | bare | panels-inputs, 443,104 rows | 1 | 0 | 1 | 0 | **0** | **ESCAPES** |
| 3 | `alcam_precedent` | bare | in-source `RECORDS` → `{}` | 1 | 0 | 1 | 0 | **0** | **ESCAPES** |
| 4 | `cd248_precedent` | bare | in-source `RECORDS` → `{}` | 1 | 0 | 1 | 0 | **0** | **ESCAPES** |
| 5 | `emc_prmt5_effect_sizes` | bare | panels-inputs, 443,104 rows | 1 | 0 | 1 | 1 | **1** | **CROSS-SOURCE ANCHOR** |
| 6 | `emc_hypoxia_confounds` | bare | null-background 494,032 + therapeutic-status 621 rows | 1 | 0 | 1 | 1 | **1** | **CROSS-SOURCE ANCHOR** |
| 7 | `cadence` | `--stamp` | (regen itself is the perturbation) | 0 | — | — | 0 | **3** | **CROSS-SOURCE ANCHOR** (wall clock) |
| 8 | `expression_validation_readiness` | `--write` | (none reached) | 1 | **unreachable** | — | 1 | 1 | **CROSS-SOURCE ANCHOR** (pinned git revision) |
| 9 | `emc_expression_panels` | bare | panels-inputs, 443,104 rows | 0 | 0 | 1 | 1 | **1** | **ACCIDENTAL CRASH** (`IndexError`) |
| 10 | `emc_fet_construct_designs` | bare | construct-inputs, 93 rows | 1 | 0 | 1 | 1 | **1** | **ACCIDENTAL CRASH** (`ValueError`) |
| 11 | `emc_prmt5_multiplicity` | bare | panels-inputs, 443,104 rows | 1 | 0 | 1 | 1 | **1** | **ACCIDENTAL CRASH** (`IndexError`) |
| 12 | `nr4a3_fusion_targets` | bare | fusion-targets-inputs, 353,959 rows | 0 | 0 | 1 | 1 | **1** | **ACCIDENTAL CRASH** (`IndexError`) |
| 13 | `realised_spend` | `--write` | snapshot, 10 rows | 0 | — | **0** | — | — | **N/A — check cannot redden** |
| 14 | `junction_seam_retraction` | `--write` | none available | 0 | — | — | — | — | **N/A — check vacuous at HEAD** |
| 15 | `continuity` | none | — | 1 | — | — | — | — | **N/A — no regeneration mode** |
| 16 | `atr_hrd_sarcoma_series` | — | — | — | — | — | — | — | **EXCLUDED by dispatch, never invoked** |

**Tally over the 15 executed: 4 ESCAPE, 4 CROSS-SOURCE ANCHOR, 4 ACCIDENTAL CRASH, 3 N/A. Zero fell into the IN-SOURCE CONSTANT bucket** — W45's `lint_readability` remains the only measured member of that class.

Combined with W45's 10: **26 enumerated, 25 executed (1 excluded), 8 full escapes, 1 partial (`lint_readability`), 5 anchor-blocked, 5 crash-blocked, 6 N/A.**

### R2 — ⭐ The two escapes with a scientific payload, verbatim (`PRIMARY`, executed)

```
=== emc_ret_cistrome  (emc-ret-cistrome-inputs.json, 1,431,683 rows removed) ===
-- --check (baseline)  rc=1  DRIFT — the derive half is not reproducible
-- (bare regen)        rc=0  "verdict": "MEASURED NR4A OCCUPANCY AT THE RET LOCUS IN 15 OF 64 PUBLIC
                             ChIP-seq EXPERIMENTS (17 of 103 peak sets …)"
-- --check             rc=0  REPRODUCES EXACTLY          <- green baseline established
-- (degrade inputs)          rows_removed 1431683
-- --check             rc=1  DRIFT — the derive half is not reproducible
-- (bare regen)        rc=0  "verdict": null,  "part_2": "NO_PEAK_SET_RETRIEVED"
-- --check             rc=0  REPRODUCES EXACTLY          <- ESCAPES
-- (restored)          rc=1  DRIFT — the derive half is not reproducible

=== emc_mtap_locus_persample  (emc-expression-panels-inputs.json, 443,104 rows removed) ===
-- --check (baseline)  rc=1  DRIFT in: ['_generated_from', 'per_platform']
-- (bare regen)        rc=0
-- --check             rc=0  REPRODUCES                  <- green baseline established
-- (degrade inputs)          rows_removed 443104
-- --check             rc=1  DRIFT in: ['per_platform']
-- (bare regen)        rc=0  within-EMC Spearman rho = -0.3091, exact p = 0.38691
-- --check             rc=0  REPRODUCES                  <- ESCAPES
-- (restored)          rc=1  DRIFT in: ['_generated_from', 'per_platform']
```

`emc_ret_cistrome` is the **honest** shape of the escape: with its inputs cache emptied, the regenerated artifact set `verdict: null` and `part_2: NO_PEAK_SET_RETRIEVED` — the artifact says out loud that it has nothing. The gate still certified it `REPRODUCES EXACTLY` at rc 0, so **the exit code carries no information about whether the artifact has content**; only the artifact text does. This is milder than W45's `emc_atr_vulnerability` case, where a scientific verdict string survived the same treatment.

`emc_mtap_locus_persample` is the opposite and the more concerning of the two: it reads **two** sources — `emc-expression-panels-inputs.json` (degraded) and the committed `emc-expression-panels.json` artifact (not degraded) — so the regenerated file still carried the same numbers (`rho = -0.3091, exact p = 0.38691`) while the `per_platform` block silently emptied and the gate went green.

⛔ **Both re-derivations are arithmetic about nothing.** A verdict, a rho or a p-value re-derived from an emptied cache is **not evidence about NR4A/RET biology, MTAP/CDKN2A status, EMC efficacy, safety, selectivity or clinical readiness, in either direction.** Every source I degraded is populated at HEAD, and every one was restored and re-verified inside the scratch copy before it was deleted. There is no wet lab.

### R3 — ⭐ Two of the four anchors are deliberate, documented, cross-cache refusals (`PRIMARY`, executed)

`emc_prmt5_effect_sizes` does not merely fail — it **refuses**, cleanly, via `raise SystemExit` in `emc_prmt5_multiplicity._merge_caches` (`emc_prmt5_multiplicity.py:568-575`), whose docstring states the intent: *"⛔ THE MERGE IS REFUSED unless the two caches agree on the samples, on their order, on the per-sample background and on every value of every symbol they share."*

```
-- --check   rc=1  REFUSING TO MERGE — the two caches do not carry the same samples
-- (bare)    rc=1  REFUSING TO MERGE — the two caches do not carry the same samples
-- --check   rc=1  REFUSING TO MERGE — the two caches do not carry the same samples
```

`emc_hypoxia_confounds` has the same construction with a different implementation shape — `emc_hypoxia_confounds.py:796` raises an `AssertionError` naming the discrepancy:

```
AssertionError: sample order differs between the two caches for GSE24369:
  ['GSM600928', 'GSM600929', 'GSM600930'] vs []
```

Both are genuine **cross-source anchors**: the reference lives in a second, independently fetched cache that the regeneration mode does not write. The traceback is a presentation difference, not a purpose difference — I classify by whether the guard is a deliberate cross-source comparison (it is, in both) rather than by whether it prints a stack.

⚠ **A shape note that matters for grading `emc_prmt5_multiplicity`.** That module *owns* the deliberate refusal above, yet under my degradation it died first with an `IndexError` inside its background-masking comprehension, before reaching its own guard. It is graded **ACCIDENTAL CRASH for this degradation shape**; a degradation that keeps list lengths intact would likely reach the deliberate anchor instead. The two classes are not exclusive per module — they are ordered.

### R4 — ⭐ The four crashes are one bug, not four (`PRIMARY`, executed)

Three of the four accidental crashes are the **same line shape in three different files**, a zip-by-index over a values list and a per-sample background list of assumed-equal length:

```
emc_expression_panels    return [None if (v[i]    is None or not bg[i]) else …   IndexError: list index out of range
emc_prmt5_multiplicity   out[g] = [None if (v[i]  is None or not bg[i]) else …   IndexError: list index out of range
nr4a3_fusion_targets     return [None if (vals[i] is None or not bg[i]) else …   IndexError: list index out of range
```

The fourth, `emc_fet_construct_designs`, is a different and more deliberate-looking raise — `ValueError: EWSR1: no transcript exon 12` at `emc_fet_construct_designs.py:371` (`raise ValueError(f"{g['symbol']}: no transcript exon {rank}")`) — a structural precondition on the gene model, not an index slip.

**None of these four is an anchor.** Each blocks the escape only for the degradation shape that happens to trip it, exactly as W45 measured for `emc_fet_frame_and_composition`. I authored no repair for any of them.

### R5 — ⛔ W45's `.git` confound is REFUTED for both modules it named — the cause is the SHALLOW checkout (`PRIMARY`, executed)

W45 flagged missing `.git` as a live confound for `expression_validation_readiness` and `fusion_frame_trap`. My copy **includes `.git`**, and both are still red, for reasons unrelated to `.git`'s presence:

* `expression_validation_readiness` — **still rc 1** with `.git` present:
  `subprocess.CalledProcessError: Command '['git', 'show', '8c1f292536b7d725186491b42c19c87c0b6c855c:research/modalities/emc-expression-panels.json']' returned non-zero exit status 128`.
  `git cat-file -t 8c1f2925…` → `fatal: git cat-file: could not get object info`, and `git rev-parse --is-shallow-repository` → **`true`**. The module pins `BASE = "8c1f292536b7d725186491b42c19c87c0b6c855c"` (`:18`); that object is **absent from this shallow checkout**, so the failure is a property of the clone depth, not of `.git`'s existence. `--write` fails at rc 1 with the identical traceback, so **the regeneration mode cannot run at all** — the anchor blocks both modes.
* `fusion_frame_trap` — **still rc 2** with `.git` present: `missing research/modalities/fusion-frame-trap-inputs.json: run --refresh on a runner first`. `git ls-files research/modalities/fusion-frame-trap-inputs.json` returns **0 lines** and the file does not exist. The input is simply not in the repository; this is not a `.git` artefact. (`--refresh` is a network fetch and was **not** run.)

**Correction for the record: the other four modules W45 recorded as red in its `.git`-less copy are red with `.git` present too** — `emc_fet_construct_designs` (`DRIFT in: ['gene_models', 'ensembl_vs_uniprot_sequences']`), `alcam_precedent` and `cd248_precedent` (both `DRIFT in: ['emc_specific_evidence']`), `emc_prmt5_multiplicity` (`DRIFT in: ['per_platform']`). I additionally measured **four reds W45 did not record**: `emc_hypoxia_confounds` (`DIFFERS FROM THE COMMITTED ARTIFACT`), `emc_mtap_locus_persample`, `emc_prmt5_effect_sizes`, `emc_ret_cistrome`, plus `continuity` (rc 1). **Nine of the sixteen are `--check`-red on an untouched copy of the live tree at `8a667406`.** I did not run any of them against the live tree itself, and I authored no repair; this is an observation for the coordinator.

The `alcam_precedent` / `cd248_precedent` red is the already-known `literature-cache` consequence: both drift on `emc_specific_evidence`, whose corpus directory (`literature/alcam-cd166-binder`) comes from the ref COMMON-BRIEF records as never present in this checkout.

### R6 — Three modules where the question does not arise, and why each matters (`PRIMARY`, executed)

* **`realised_spend` — `--check` cannot redden.** `realised_spend.py:437-439`: the `--check` branch prints the drift JSON and `return 0` unconditionally. Measured: after emptying every list in `realised-spend.json` (10 rows), `--check` is still rc 0 and still reports `"drift_usd": 0.0, "action": "in step"` — the drift figure reads scalar fields the list-emptying did not touch. W45's source grade is **confirmed by execution**. Its own remedy string ("run --write, then update the figure … IN THE SAME COMMIT") is advisory text, not a gate.
* **`junction_seam_retraction` — the check is vacuous over the committed corpus.** Baseline: `--check: OK (315 artifact(s); every retracted seam carries its banner)`, rc 0. A scan of `research/modalities/*.json` for the module's own `BANNER_KEY = "⛔_RETRACTED_SEAMS"` (`:67`) returns **0 artifacts**, and every graded row printed `seams=0 retracted=0 banner=False`. There is no committed retracted seam to strip, so **no degradation of a declared source can redden this gate**; reddening it would require me to fabricate a seam into an artifact, which I did not do. The gate is a true universal quantification over an empty set — notable given that this is the module whose own comment says *"A self-test that cannot fail is the defect this repository keeps paying for."* Whether that is a defect or the correct state for a clean corpus is a maintainer's call, not mine.
* **`continuity` — it has no regeneration mode.** Flags are `--check`, `--clauses`, `--leases`, `--me`, `--limit`; `grep -cE 'open\([^)]*["'"'"']w|\.write_text|json\.dump\('` over the file returns **0**. It writes nothing and therefore cannot be a regenerate-then-check module. **W45's Tier-B membership over-counts by at least this one**, consistent with its own caveat that the Tier-B denominator of 17 came from a verdict-string grep rather than a per-module reading.

### R7 — What this refines in W45's discriminator (`PRIMARY`)

1. **The three-valued discriminator survives, and the ordering matters.** Anchor, in-source constant and crash are not exclusive per module — they are *tried in execution order*. `emc_prmt5_multiplicity` owns a deliberate anchor and never reached it. A census that grades one degradation shape per module reports the **first** blocker, not the strongest one.
2. **The escape does not need an external source file at all.** `alcam_precedent` and `cd248_precedent` hold their entire source as an in-module `RECORDS` dict, so the module *is* both the source and the regenerator: emptying `RECORDS` reddened `--check` (`DRIFT in: ['binder_precedent']`, `DRIFT in: ['records']`), the bare run rewrote the artifact from the emptied dict, and `--check` returned `REPRODUCES` at rc 0. This is the **mirror image** of W45's `lint_readability` finding: an in-source constant blocks the escape when the check *compares against* it, and enables the escape when the check merely *re-derives from* it. **Direction decides, exactly as W37c found for the `systems_check` CROSS families.**
3. **A cross-source anchor stays sufficient and stays not necessary** (4 anchors, 4 crashes here), and the anchors that work are the ones somebody wrote on purpose with a message naming the discrepancy — two independently fetched caches (`emc_prmt5_effect_sizes`, `emc_hypoxia_confounds`), a pinned immutable git revision (`expression_validation_readiness`), and the wall clock (`cadence`, whose `--stamp` moves the check from rc 0 to **rc 3**, the only module measured whose regeneration mode makes the check *more* red).

**I authored no repair, no patch, no gate, no floor and no test. No guard was weakened, relaxed, narrowed or reordered. `scripts/preflight.sh` was not run. `atr_hrd_sarcoma_series.py` was never invoked. No `--refresh`/`--fetch` mode was run. No network was attempted, so I have no denial to record. No content-policy refusal occurred.**

## Validation evidence

**RUN.** `date -u`, `git rev-parse HEAD`, `git status --porcelain` at start and end (0 lines both times); `df -h /` at start (19 G), mid (16 G) and end (19 G); `cp -a` scratch copy including `.git` (`CP_EXIT=0`, 983 M, `ls -d …/repo/.git` succeeded); `__file__`-resolution grep over all 16 module files quoted in Method; flag enumeration for all 16; source-path enumeration for the 10 Tier-B modules; a 16-module baseline `--check` sweep with real exit codes; the seven-step driver (`baseline → regen → green-check → degrade → check → regen → re-check → restore → restore-check`) executed for `emc_expression_panels`, `emc_fet_construct_designs`, `emc_mtap_locus_persample`, `emc_prmt5_multiplicity`, `emc_prmt5_effect_sizes`, `emc_hypoxia_confounds`, `emc_ret_cistrome`, `nr4a3_fusion_targets`, with rows-removed counts printed by `empty.py` and per-module restore verified by `--check` returning to its step-1 code in every case; a separate real-exit-code run for `alcam_precedent`, `cd248_precedent` and `cadence` (a first pass whose `echo $?` read `tail`'s status was discarded and re-run — the discarded pass is reported here rather than dropped); `realised_spend` degrade/check/restore; `git cat-file -t 8c1f2925…` and `git rev-parse --is-shallow-repository`; `git ls-files research/modalities/fusion-frame-trap-inputs.json`; the `BANNER_KEY` corpus scan; the `continuity` write-operation count; source reads of `realised_spend.main`, `cadence.main`, `junction_seam_retraction.main`, `expression_validation_readiness.main`, `alcam_precedent.main`, and `emc_prmt5_multiplicity._merge_caches`; scratch deletion verified (`RM_EXIT=0`, `ls` → no such file).

**PROPOSED (NOT RUN):** any run of `atr_hrd_sarcoma_series.py`; any `--refresh`/`--fetch` mode; a length-preserving degradation of `emc_prmt5_multiplicity`, `emc_expression_panels` and `nr4a3_fusion_targets` that would reach their deliberate guards instead of the `IndexError`; the `expression_validation_readiness` escape test in a **full** clone where `8c1f2925…` resolves (**PREDICTION**, from source: the anchor is a git object the module cannot rewrite, so `--write` should not be able to green a degraded `--check` — untested and not claimed as measured); a reddening of `junction_seam_retraction --check`, which would require fabricating a retracted seam.

## Limitations

- **"Escape" means escape against exactly the degradation I ran** — emptying every list in the declared JSON source, or emptying an in-source `RECORDS` dict. R4 and the `emc_prmt5_multiplicity` ordering both show a different shape can give a different class for the same module. This is not a general soundness claim about any module.
- **`emc_mtap_locus_persample`'s escape is against one of its two sources.** I degraded `emc-expression-panels-inputs.json`; the committed `emc-expression-panels.json` it also reads was left intact. Whether it escapes when both are degraded is **UNKNOWN**.
- **Six of the nine baseline-red modules needed a bare regeneration to reach green**, so the green baseline is a *regenerated* artifact, not the committed one. The escape measured is therefore "regenerate-then-check on a self-consistent tree", which is the property W45 asked about, but it is not a statement about the committed artifacts at HEAD.
- **The reds I report are from a copy, not from the live tree.** I ran nothing against `/home/user/Rare-cancers`. Whether these nine are red at HEAD in situ is UNKNOWN, though the copy was byte-identical at copy time.
- **This is a census of gate arithmetic, not of science.** No exit code here says anything about EMC efficacy, safety, selectivity, therapeutic window or clinical readiness, and no re-derivation from a degraded cache is evidence about biology in either direction. There is no wet lab.
- **A gate reporting OK over a degraded source is a measurement gap, not evidence that anything is wrong in the repository today.** Every degraded source is populated at HEAD and every one was restored and re-verified before the scratch was deleted.
- HEAD advanced during the run (`8a667406` → `d5034489`); all measurements pin to the tree as copied at `8a667406`.
- `continuity`'s exclusion rests on a write-operation grep and a flag list, not on a full reading of its 400+ lines.

## Stop condition

Set up front: **return the moment all 16 of W45's source-graded modules are classified — 15 by executed three-step test with real exit codes and a green baseline established wherever the module was red, 1 (`atr_hrd_sarcoma_series`) recorded as excluded and never invoked — the scratch tree is deleted, and `git status --porcelain` on the live tree is confirmed empty.** **MET.** 15 executed, 4 ESCAPE / 4 CROSS-SOURCE ANCHOR / 4 ACCIDENTAL CRASH / 3 N/A, 0 IN-SOURCE CONSTANT; W45's `.git` confound refuted for both named modules; scratch deleted; live tree clean. Returned early.

## Tool-call and wall-clock count actually used

**21 tool calls** (several batching many commands; two run in background). Wall clock **04:46:56Z → 04:59:08Z ≈ 12 minutes**, well inside the ~40-call / ~40-minute target.

## Next concrete action

**One successor, and it is the ordering problem R7 opens.** The census now grades each module on the *first* blocker its declared degradation happens to hit, and `emc_prmt5_multiplicity` proves that can hide a deliberate anchor behind an accidental crash. The bounded successor is: **for the 9 modules classified ACCIDENTAL CRASH across W45 and W58 (`emc_fet_frame_and_composition`, `emc_expression_panels`, `emc_fet_construct_designs`, `emc_prmt5_multiplicity`, `nr4a3_fusion_targets`, and re-testing the 4 escapes under the same shape), re-run the three-step test with a LENGTH-PRESERVING degradation — replace list *elements* with nulls or zeros rather than emptying the lists — and record whether the module then reaches a deliberate guard, or escapes.** That converts "blocked by accident" into "blocked, or escaping, on purpose" for the third of the denominator where the current grade is shape-dependent, and it is one bounded run of the shape already executed 12 times.

**Explicitly not a successor:** any repair, anchor, floor, zero-test or gate change for any module in this census — including the three `IndexError` sites that are visibly one bug in three files, `realised_spend`'s unconditional `return 0`, and `junction_seam_retraction`'s vacuous universal. Which of these should acquire an anchor is a maintainer's decision about what each artifact is for.
