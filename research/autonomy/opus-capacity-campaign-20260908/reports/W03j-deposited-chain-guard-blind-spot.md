<!-- collected 2026-09-08T04:50:34Z by campaign coordinator; agent id ad7f7af3ee8ffee9b; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ad7f7af3ee8ffee9b.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

W03j, lane 3, OPUS-CAPACITY-CAMPAIGN-20260908. Named successor to W03i.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the runtime model from the child transcript.

- `date -u` **start** `Tue Sep  8 04:44:25 UTC 2026`; **end** `Tue Sep  8 04:47:08 UTC 2026` (report drafting followed).
- `git rev-parse HEAD` **start** `fb1a3f8040537234010114053b36ec55b729c65e`; **end** `8a667406e875ae99c7d50347b2e895a177fcb048`. **HEAD moved under me** (coordinator collection commits). `diff -rq --exclude=.git` between the live tree and my `cp -a` copy shows the moved content is *entirely* inside `research/autonomy/opus-capacity-campaign-20260908/` (8 new `reports/*.md`, `COMMON-BRIEF.md` edited) plus my scratch's own `__pycache__`/`.pytest_cache` — **no ASO-lane file differs**, so my measurement at `fb1a3f80` holds at `8a667406`.
- `git status --porcelain` **empty at start and empty at end**. I wrote nothing in `/home/user/Rare-cancers` and ran no git write operation. All execution was under `/tmp/claude-0/w03j/`, deleted before returning (`ls -d` → `No such file or directory`).

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (51 lines; the five very long proxy/truststore lines — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are elided here as they name no model; the end-of-run re-run returned the same 51-line count):

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

## Question

W03i's named successor measurement, verbatim: **is the four-artifact gap in `_PREMRNA_ARTIFACTS` already flagged by a red gate someone is living with, or is it genuinely unwatched?** Answered by running `research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py` on a `cp -a` copy and recording the real exit code. If green, characterise `_module_level_paths`'s blind spot with `file:line` and name the other deposited modules using the same third idiom. Plus: settle W03i's two UNKNOWNs by reading the open sites — are `aso-genome-offtarget-taf15intron2.json` and `junction-aso-offtarget.json` **opened** by an inventoried module, or merely mentioned?

**Stop condition, set up front, four clauses:** (a) the test is run in scratch with `pytest` on PATH and its real exit code and pass/fail counts recorded; (b) if green, the resolver's blind spot is located with `file:line` and empirically demonstrated on `aso_sequence_manifest.py`, and the other deposited third-idiom modules are enumerated by AST rather than by eye; (c) both UNKNOWNs are resolved to OPENED or MENTIONED with the open site cited; (d) live tree verified untouched and scratch deleted. **All four met.**

## Prior-work check

Read in full before doing anything: `COMMON-BRIEF.md` (including "Known, measured, and NOT worth rediscovering"), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, and `reports/W03i-archive-glob-coverage.md` (33.7 KB, read across two `sed` windows). All under `research/autonomy/opus-capacity-campaign-20260908/`.

This unit is a **named successor measurement, explicitly labelled `PROPOSED (NOT RUN)` by W03i**, so there is nothing to re-derive. I did not re-measure W03i's R0/R1 denominators, W03h's perturbation set, W03g's mode invocations, the campaign 0-of-89 resolution rate, the `systems_check` baseline, or the `superseded[]` census. **No `reports/W25-*` was read, listed or referenced.** I heeded the brief's measured correction and used `pytest` on PATH (`/root/.local/bin/pytest`, pytest 9.1.1, interpreter `/root/.local/share/uv/tools/pytest/bin/python3`), never `python3 -m pytest`; when a scratch probe hit `ModuleNotFoundError: No module named 'pytest'` under `/usr/local/bin/python3`, I re-ran it under the uv-tool interpreter rather than concluding anything about installation.

I did not run `scripts/preflight.sh`, did not invoke `atr_hrd_sarcoma_series.py` at all, did not run `scripts/regenerate_aso_chain.sh`, did not re-derive the manifest, did not add/remove/reorder any glob, did not `git fetch`, and authored/proposed/applied **no repair, patch, gate or test**. No test was skipped, deselected or disabled. No network. No content-policy refusal occurred in this unit.

## Method and inputs

`cp -a /home/user/Rare-cancers /tmp/claude-0/w03j/tree` (983 MB; free space checked first — 19 GB available on `/`, above the 10 GiB floor). Every execution ran with cwd inside that copy.

Inputs read: `research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py`; `research/manuscripts/aso_sequence_manifest.py`; `research/modalities/aso_taf15_intron2_designs.py`; `research/modalities/junction_seam_retraction.py`; `research/modalities/aso_screen_sets.py`; `research/modalities/junction_aso_offtarget.py`; `research/manuscripts/aso_priorart_evidence.py`; `research/manuscripts/aso_reagent_coverage.py`; the committed manifest `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` (loaded through the guard's own `_manifest()`).

Two scratch probes imported the guard module itself and called its real helpers (`_manifest`, `_invoked`, `_script`, `_module_level_paths`, `_names_opened_for_writing`, `_DATA_SUFFIXES`) — so the resolver's behaviour is measured from the shipped code, not re-implemented. A third scratch script AST-scanned every deposited `.py` for module-level `Tuple`/`List`/`Set`/`Dict` assignments containing string constants ending in a `_DATA_SUFFIXES` extension.

Environment: Linux, pytest 9.1.1 on CPython 3.11.15 (`/root/.local/share/uv/tools/pytest/bin/python3`), plugins `xdist-3.8.0`, no network.

## Result

### R1 — The gate is GREEN. The gap is genuinely unwatched. (PRIMARY, EXECUTED)

```
$ cd /tmp/claude-0/w03j/tree && pytest research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py -v
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/claude-0/w03j/tree
plugins: xdist-3.8.0
collected 10 items
... 10 PASSED ...
======================== 10 passed, 2 warnings in 0.29s ========================
REAL_EXIT=0
```

**Real exit code 0. 10 collected, 10 passed, 0 failed, 0 skipped, 0 errors, 0 xfail, 2 warnings** (both `DeprecationWarning: invalid escape sequence '\s'` from `test_every_input_an_invoked_module_names_is_in_the_archive`). Every one of the ten node ids passed, including the two the gap would have to fire through: `test_every_input_an_invoked_module_names_is_in_the_archive` and `test_the_deposited_chain_does_not_read_an_undeposited_artifact`.

**So: not a red gate someone is living with. W03i's R3 is the stronger case — an unwatched gap.** This is the stronger version of W03h's P3b, and it means `--check-archive` plus this guard, run together, both report a complete archive while four committed inputs of a deposited chain step are outside it.

### R2 — The blind spot, located and demonstrated (PRIMARY, EXECUTED + source)

The resolver is `_module_level_paths` at `research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py:204-247`. Its evaluator `ev(node)` is defined at `:218` and handles exactly three node kinds — `ast.Constant` holding a `str` (`:219`), `ast.Name` looked up in `env` (`:221`), and `ast.Call` restricted to `join` / `dirname` / `abspath` / `realpath` (`:223-232`) — then **`return None` at `:233` for everything else**. `ast.Tuple`, `ast.List`, `ast.Set` and `ast.Dict` all fall to that `return None`. The collection loop at `:235-241` then keeps a binding only `if isinstance(value, str)` (`:240`).

**Consequence, stated exactly: a module-level constant whose value is a *container* of path strings is invisible to the resolver, no matter what the container holds.** It is not that bare basenames are unresolvable — `:243-252` explicitly resolves a bare filename against `home` and against any constant naming a real directory (the docstring at `:211-213` says so, and `test_the_input_reader_actually_resolves_this_lanes_two_idioms` proves it on `aso_noncoding_acceptor_screened_table.py`). The failure is one level earlier: **the tuple never becomes seven string bindings in `env`, so those basenames are never candidates for resolution at all.** The `_load(*parts)` join at `aso_sequence_manifest.py:75-78` happens at call time inside a function body, which `:235`'s `for node in tree.body` does not walk.

Measured directly, calling the shipped helper on the shipped module:

```
module_level_paths(aso_sequence_manifest.py) = {
 "OUT_CSV":   "research/manuscripts/aso/fusion-junction-aso-sequences.csv",
 "OUT_FASTA": "research/manuscripts/aso/fusion-junction-aso-sequences.fasta"
}
PREMRNA seen: []
```

Both names the resolver *does* find are **outputs** (they are in `_names_opened_for_writing`, so `:311` skips them). **The guard therefore extracts zero inputs from `aso_sequence_manifest.py` and contributes nothing at all for that step — it passes vacuously on the one module W03i's finding is about**, even though `aso_sequence_manifest.py` **is** in `_invoked(_script())` (measured `True`; 29 invoked steps) and **is** deposited.

**A second, independent reason the gap escapes, not previously named.** `test_every_input_an_invoked_module_names_is_in_the_archive` (`:293`) iterates `_invoked(_script())` only — deposited-but-not-chain-invoked modules are never opened. That matters concretely (see R3): `aso_taf15_intron2_designs.py` is deposited, its `GENOME_SCREEN`/`PREMRNA_SCREEN` **are** resolved by `_module_level_paths` (second idiom, so no blind spot), both point at existing undeposited files, and neither is an output — the guard would flag them if it looked, and it does not, purely because `invoked_by_chain: False`. So the third idiom is one of at least two disjoint escape routes.

The sibling test `test_the_deposited_chain_does_not_read_an_undeposited_artifact` (`:257-289`) *does* use a text regex (`r'"([\w-]+\.json)"'`) that would match a bare basename inside a tuple — but it is scoped to deposited files with `"/tests/"` in the path (`:270-271`). `aso_sequence_manifest.py` is not a test, and its own test `test_aso_sequence_manifest_joins.py` is **not deposited** (measured `False`), so that regex never sees these seven names either.

### R3 — Other deposited modules using the same third idiom (PRIMARY, EXECUTED, AST census)

AST scan of every `.py` in the manifest's `files[]` for a module-level container assignment holding path-suffixed string constants — **11 hits across 8 modules**:

| Module : line | Constant | n | Chain-invoked? | Verdict |
|---|---|---:|---|---|
| `research/manuscripts/aso_sequence_manifest.py:142` | `_PREMRNA_ARTIFACTS` | 7 | **yes** | **LIVE GAP — 7 invisible, 4 of them not in the archive** (`aso-premrna-offtarget-{18mer-5-8-5,20mer-5-10-5,ewsr1intron2,taf15intron2}.json`) |
| `research/manuscripts/aso_priorart_evidence.py:46` | `CORPORA` (dict) | 2 | **yes** | invisible, but **not a gap**: `_read` at `:57` reads them via `git show origin/literature-cache:<path>`, not from the working tree — the brief's W40 item covers that ref. No working-tree file to be missing. |
| `research/manuscripts/build_submission_pdf.py:2261` | `STAMP_SOURCES` | 1 | yes | invisible; the file it names **is** in the archive. Latent only. |
| `research/manuscripts/lint_citations.py:72` | `ANCHOR_SUFFIXES` | 2 | yes | **false positive of my screen** — `(".json", ".jsonl")` are extensions, not paths. |
| `research/modalities/fusion_neoantigen_invalidation.py:176,177` | `_SCAN_EXTS`, `_EXCLUDE` | 2, 1 | no | same false-positive shape (extension lists). |
| `research/modalities/junction_seam_retraction.py:88` | `_OWN_GLOBS` | 3 | no | **a fourth idiom** — module-level tuple of *glob patterns*, expanded at `:90` into `ARTIFACT_GLOBS` and consumed by `glob.glob` at `:431`, `json.load` at `:434-435`. Invisible to the resolver twice over (container, and a pattern rather than a path). Contains `junction-aso-offtarget.json` — see R4. |
| `research/modalities/aso_reagent_coverage.py:46,57` | `PARTNER_COHORT`, `BREAKPOINT_COHORT` | 1, 1 | no | **false positive** — dicts of literature metadata whose `source` value happens to be a repo path string; no open. |
| `research/modalities/depmap_sarcoma_dependency.py:104` | `WANT_FILES` | 2 | no | invisible; not chain-invoked, not assessed further. |
| `research/modalities/emc_atr_vulnerability.py:209` | `EXPRESSION_FILE_PREFERENCE` | 2 | no | invisible; not chain-invoked, not assessed further. |

**Answer to "which other deposited modules use the same third idiom": eight, of which two are chain-invoked with real paths (`aso_sequence_manifest.py`, `aso_priorart_evidence.py`) and one more is chain-invoked with an already-deposited path (`build_submission_pdf.py`). `aso_sequence_manifest.py` is the only one where the idiom currently hides an undeposited artifact from a chain-invoked step.** I did not audit the four non-chain-invoked modules for undeposited targets — out of scope and not needed for the stop condition.

### R4 — W03i's two UNKNOWNs, settled (PRIMARY, source, open sites read)

Both are **tracked and present on disk, and both are `deposited: False`** (measured against the manifest's `files[]`).

**`research/modalities/aso-genome-offtarget-taf15intron2.json` — OPENED, not merely mentioned.**
Opened by `research/modalities/aso_taf15_intron2_designs.py` (deposited: **True**; chain-invoked: **False**) inside `screen_readout(slug="taf15intron2")` at `:338`. The loop header at `:357-359` builds the path as an **f-string**, `os.path.join(HERE, f"aso-genome-offtarget-{slug}.json")`, and the open is `d = json.load(open(path, encoding="utf-8"))` at `:404`. The module-level constants `GENOME_SCREEN` (`:316`) and `PREMRNA_SCREEN` (`:317`) name the same two files in the second idiom but are **never referenced anywhere else in the module** (`grep` returns only their definitions) — they are documentary aliases; the live open goes through the f-string. Its sibling `aso-premrna-offtarget-taf15intron2.json` (`:317`, and one of W03i's four) is opened by the same loop.
**Materially different from the premrna four in one respect:** this open is *guarded* — `if not os.path.exists(path)` at `:360` records the screen as `"NOT RUN — no artifact on disk. ABSENT, NOT CLEAN."` So absence here degrades loudly-in-the-artifact rather than raising, which is the opposite of `_premrna_condemned`'s deliberate no-`try/except` at `aso_sequence_manifest.py:148-155`.

**`research/modalities/junction-aso-offtarget.json` — OPENED, not merely mentioned, but only via glob and only by a non-chain-invoked module.** The four sites split cleanly:
- `junction_aso_offtarget.py:26` — docstring line `Output: junction-aso-offtarget.json`. This module *produces* it. **MENTION** (and correctly so).
- `aso_screen_sets.py:266` — a comment explaining why the loader family pattern excludes it. **MENTION.**
- `junction_seam_retraction.py:89` — the bare basename inside `_OWN_GLOBS`, folded into `ARTIFACT_GLOBS` at `:90`, expanded by `glob.glob` at `:431` and `json.load`ed at `:434-435`. **OPENED**, by a module that is deposited (**True**) but not chain-invoked (**False**). The comment at `:84-87` states the entry is deliberate and that dropping it would narrow the sweep from 315 files to 314. The open is inside `try: … except (OSError, ValueError)` (`:433-440`), which grades the file `UNGRADEABLE` rather than raising — again tolerant, unlike the premrna four.
- `research/manuscripts/tests/test_the_journal_articles_word_quantities_are_derived.py:63` binds `ALIGNMENT` and `:294` does `json.load(open(_required(ALIGNMENT, "the RefSeq alignment screen")))` — a genuine **OPEN**, but that test is **not deposited** (measured `False`), so it is outside both guards' scope and outside the archive.

**Summary of the two:** both are genuinely opened by deposited code, so W03i's PATTERN-GAP suspicion is upheld in kind — but neither is opened by a *chain-invoked* module, and both opens are absence-tolerant. **The four premrna artifacts remain the sharpest case**, because they are the only ones opened unconditionally, by a chain-invoked deposited step, with the module's own comment declaring that a missing artifact must break the build.

### R5 — Direct answer

**Genuinely unwatched. Exit 0, 10/10 passed.** The guard's resolver cannot see a module-level container of path strings (`:218-233`, `:240`), so the seven `_PREMRNA_ARTIFACTS` names produce zero input candidates for the one chain step this is about; and a second, disjoint scoping limit (`_invoked` only, `:293`) hides the deposited-but-not-invoked `aso_taf15_intron2_designs.py`, whose two undeposited screens the resolver *does* resolve. Nothing else in the repository covers the gap: the sibling regex guard is scoped to deposited `/tests/` files, and the relevant test is not deposited.

## Validation evidence

**RUN.** All inside `/tmp/claude-0/w03j/tree`, a `cp -a` of the live checkout at HEAD `fb1a3f80`. pytest 9.1.1 on CPython 3.11.15 (`/root/.local/share/uv/tools/pytest/bin/python3`), plugins `xdist-3.8.0`, no network. **Not preflight.**

| # | Command | Real exit | Key verbatim output |
|---|---|---|---|
| V0 | `date -u; git rev-parse HEAD; git status --porcelain` (live, start) | 0 | `Tue Sep 8 04:44:25 UTC 2026`; `fb1a3f80…`; empty |
| V1 | `df -h /tmp`; `du -sh /home/user/Rare-cancers` | 0 | `19G` free; `983M` |
| V2 | `cp -a /home/user/Rare-cancers /tmp/claude-0/w03j/tree`; `which pytest`; `pytest --version` | 0 | `/root/.local/bin/pytest`; `pytest 9.1.1` |
| **V3** | `cd /tmp/claude-0/w03j/tree && pytest research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py -v` | **0** | `collected 10 items`; ten `PASSED`; `10 passed, 2 warnings in 0.29s`; `REAL_EXIT=0` |
| V4 | scratch `probe.py` under `/usr/local/bin/python3` | 1 | `ModuleNotFoundError: No module named 'pytest'` — the brief's known trap; re-run under the uv-tool interpreter |
| V5 | scratch `probe.py` under `/root/.local/share/uv/tools/pytest/bin/python3` | 0 | `invoked steps: 29`; `aso_sequence_manifest invoked: True`; `module_level_paths(...) = {OUT_CSV, OUT_FASTA}`; `PREMRNA seen: []` |
| V6 | scratch `idiom.py` — AST census of deposited `.py` | 0 | section A 4 rows (verbatim in R3, incl. `_PREMRNA_ARTIFACTS n=7 invisible_to_resolver=7 of_those_NOT_in_archive=4`); section B 11 rows |
| V7 | scratch `two.py` — deposited/invoked status + resolver output for `aso_taf15_intron2_designs.py` | 0 | `taf15_designs deposited: True invoked_by_chain: False`; `junction_seam_retraction deposited: True invoked_by_chain: False`; both JSONs `deposited: False exists: True`; `module_level_paths keys: ['GENOME_SCREEN','PANEL_ATLAS','PREMRNA_CACHE','PREMRNA_SCREEN']`; `names_opened_for_writing: ['out_atlas','out_designs']` |
| V8 | `grep -n`/`sed -n` over the six open sites (read-only, live tree) | 0 | `:404 d = json.load(open(path, …))`; `:431 glob.glob(...)` / `:434-435 json.load`; `:294 json.load(open(_required(ALIGNMENT, …)))`; `:26 Output: junction-aso-offtarget.json` |
| V9 | deposited-status of the two tests | 0 | `test_the_journal_articles_word_quantities_are_derived.py deposited: False`; `test_one_geometry_screen_loading.py deposited: False` |
| V10 | `git status --porcelain` (live); `diff -rq --exclude=.git` live vs scratch | 0; 1 | live status empty; diff lists **only** campaign-directory files (8 new `reports/*`, `COMMON-BRIEF.md`) and scratch-only `__pycache__`/`.pytest_cache` — **no ASO-lane file differs** |
| V11 | `rm -rf /tmp/claude-0/w03j; ls -d /tmp/claude-0/w03j`; `date -u`; `git rev-parse HEAD`; `git status --porcelain` (end) | 2 (ls) | `No such file or directory`; `Tue Sep 8 04:47:08 UTC 2026`; `8a667406…`; empty |

**PROPOSED (NOT RUN):** any change to `_module_level_paths`, to `_invoked`'s scope, or to any `patterns` list; re-deriving the manifest; `scripts/regenerate_aso_chain.sh`; `scripts/preflight.sh`; `PREFLIGHT_FULL=1`; unpacking the published archive and running the chain against it. **No content-policy refusal occurred in this unit.**

## Limitations

- **Green means "this guard does not fire", not "no guard anywhere fires".** I established non-coverage for the two guards in this file plus the deposited-test regex scope; I did not run the full test suite, so a fire from some other file is UNKNOWN — though the mechanism (a container the resolver never unpacks) makes it unlikely and W03i's `grep` over `research`/`scripts` surfaced no other claimant.
- **The four premrna artifacts' consequence is still source-derived, not executed.** I read the unconditional `_load` and the deliberate absence of `try/except`; I did not unpack the archive and run the step against it. W03i's limitation stands unchanged here.
- **My third-idiom census has known false positives** (`ANCHOR_SUFFIXES`, `_SCAN_EXTS`, `_EXCLUDE` are extension lists; `PARTNER_COHORT`/`BREAKPOINT_COHORT` are literature metadata). I classified each by reading it; the *screen* is mechanical, the *verdicts* are mine. It is also incomplete in the other direction: it looks only for module-level containers of suffix-matching string constants, so a container built by comprehension, an f-string list, or paths without a `_DATA_SUFFIXES` extension would be missed.
- I did not audit the four non-chain-invoked third-idiom modules (`depmap_sarcoma_dependency.py`, `emc_atr_vulnerability.py`, `fusion_neoantigen_invalidation.py`, `junction_seam_retraction.py`) for further undeposited targets.
- HEAD moved under me (`fb1a3f80` → `8a667406`). I verified by `diff -rq` that the movement is confined to the campaign directory, but that is a working-tree comparison, not a `git diff` over the two commits.
- Measured at one HEAD, on one machine, against the committed manifest and working tree. Nothing here is a statement about CI or about the published Zenodo archive's actual contents.
- **Nothing in this report is evidence about any oligonucleotide's efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab. A manifest's contents are a statement about file freshness and nothing else.**

## Stop condition

Set up front, four clauses under **Question**. **Met, all four.** (a) V3 — real exit 0, 10 collected / 10 passed / 0 failed / 0 skipped, run with `pytest` on PATH in the scratch copy. (b) R2 — blind spot at `test_the_deposited_chain_can_run_from_the_deposit.py:218-233` and `:240`, demonstrated by calling the shipped `_module_level_paths` on the shipped module (`PREMRNA seen: []`, only two output names found); R3 — eight deposited modules enumerated by AST. (c) R4 — both UNKNOWNs resolved to **OPENED**, with `aso_taf15_intron2_designs.py:357-359,404` and `junction_seam_retraction.py:89,90,431,434-435` cited, and the mention-only sites separated out. (d) V10/V11 — live `git status --porcelain` empty at start and end, no ASO-lane file differs, scratch deleted and confirmed absent. Returning now.

## Tool-call and wall-clock count actually used

**13 tool calls** (all `Bash`; no `Read`, no `Skill`, no network, no background task, no subagent). Two calls were paired-parallel. One probe failed with the expected wrong-interpreter `ModuleNotFoundError` and was re-run correctly. **Wall clock 04:44:25Z → 04:47:08Z ≈ 2.7 minutes of execution**, plus report drafting. Well inside the ~40 calls / ~40 minutes target.

## Next concrete action

**For the PUB-ASO owner: the decision W03i framed is now unblocked, and it is exactly one decision, not two.**

The measurement removes the branch. The gap is not a known-failing gate — it is invisible to the repository's own instrument, which passes 10/10 while four committed inputs of a deposited, unconditionally-opening chain step sit outside the archive. The guard's own header comment (`:~185-200`) records that this class has now been missed **three** times, each time one level further in; this is the fourth, and its shape is new: not a verb (`python3 -m pytest` vs `pytest`), not a shell variable (`FIG=$MAN/figures`), not a module-vs-artifact level, but **a container the AST resolver never unpacks**.

The single next action is the owner's call on `aso_archive_manifest.py`'s `premrna_compartment_screen` row (`:423-426`) — whether the four `aso-premrna-offtarget-{18mer-5-8-5,20mer-5-10-5,ewsr1intron2,taf15intron2}.json` join the deposit — which is what the guard's own assert message prescribes (`:326-329`). **I have deliberately authored no patch, and none should be authored by a worker**: it changes what a published deposit contains.

**The most useful successor measurement in this lane** is now a different and smaller question than W03i's was, because R2 found *two* disjoint escape routes and only characterised the reach of one. Concretely: take the 11 deposited modules that `_invoked(_script())` does **not** cover but that the manifest ships, run the shipped `_module_level_paths` and `_names_opened_for_writing` over each, and count how many resolve to an existing, undeposited, non-output artifact. `aso_taf15_intron2_designs.py` already gives two (`GENOME_SCREEN`, `PREMRNA_SCREEN`) with **no resolver blind spot at all** — the guard simply never looks at that module. That measurement is mechanical, needs no scratch copy beyond a read-only import, and it decides whether the `_invoked`-scoping limit is a one-module curiosity or a wider hole than the container idiom is.
