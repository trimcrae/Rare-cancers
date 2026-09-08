<!-- collected 2026-09-08T04:56:03Z by campaign coordinator; agent id af70a5205f87075b5; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-af70a5205f87075b5.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

W66, lane 3 (ASO deposited-chain guard), OPUS-CAPACITY-CAMPAIGN-20260908. Named successor to W03j.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the runtime model from the child transcript.

- `date -u` **start** `Tue Sep  8 04:50:55 UTC 2026`; **end** `Tue Sep  8 04:52:47 UTC 2026` (report drafting followed).
- `git rev-parse HEAD` **start** `56f355f65b7b3e47aeb434ac02edf4cf049f40f3`; **end** `fcb36d3c651223d90b98c0cb64169bb106e6e060`. HEAD moved under me (coordinator collection commits; `COMMON-BRIEF.md` was edited on disk mid-run, notified by the harness). Per the brief's W35b item, campaign commits touch only the campaign directory; **no ASO-lane file is in the campaign directory**, and my only executed measurement ran against `research/` and `scripts/` sources.
- `git status --porcelain` **empty at start and empty at end** (`| wc -l` → `0` at both ends). I wrote nothing in `/home/user/Rare-cancers` and ran no git write operation. Scratch was one file under `/tmp/claude-0/w66/`, deleted before returning (`ls -d` → `No such file or directory`, exit 2). No `cp -a` copy was needed: the measurement is a read-only import, run with `PYTHONDONTWRITEBYTECODE=1` **and** `sys.dont_write_bytecode = True`. Verified afterwards that no `.pyc` newer than my run exists in `research/modalities/__pycache__` (newest member `04:44:07`, i.e. a prior worker's; the directory is `.gitignore:9`-ignored and `git status --porcelain --ignored=no` is 0).

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (the five very long proxy/truststore lines — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are elided as they name no model):

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

W03j's named successor measurement, verbatim in substance: **for every deposited module that `_invoked(_script())` does not cover, what do the SHIPPED `_module_level_paths` and `_names_opened_for_writing` resolve to, and how many of those resolve to an existing, undeposited, non-output artifact?** This decides whether the `:293` `_invoked`-scoping limit — the second, disjoint escape route W03j found but did not characterise — is a one-module curiosity (`aso_taf15_intron2_designs.py`) or a wider hole than the container idiom of route 1.

**Stop condition, set up front, four clauses:** (a) the uncovered set is computed from the shipped `_manifest()`/`_invoked()`/`_script()`, not by eye, with an honest denominator; (b) the shipped `_module_level_paths` and `_names_opened_for_writing` are *imported and called*, not reimplemented, and the guard's own per-module filter chain at `:302-310` is replicated exactly; (c) a per-module table and a total are produced, with each hit checked against existence, deposit status and output status; (d) the live tree is confirmed untouched (`git status --porcelain` empty) and scratch deleted. **All four met.**

## Prior-work check

Read in full before running anything, in this order: `research/autonomy/opus-capacity-campaign-20260908/COMMON-BRIEF.md` (478 lines, including the whole "Known, measured, and NOT worth rediscovering" section and the pytest-interpreter trap), `CORPUS-CONTEXT.md` (82 lines), `CLOSED-WORK.md` (70 lines), `reports/W03j-deposited-chain-guard-blind-spot.md` (220 lines) and `reports/W03i-archive-glob-coverage.md` (299 lines, read across three windows). Then the guard source itself: `sed -n '1,60p;120,340p' research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py`.

Prior-work commands actually run on the tree: `git ls-files -- <the six candidate artifacts>` (all six tracked); `grep -rn --include='*.py' -l "<basename>" research` for each candidate, to find producers/consumers; `grep -n` over the three hit modules' write and read sites.

Not replayed, per the dispatch and the brief: W03j's pytest run (its exit-0/10-passed result is cited, not repeated — **I ran no pytest at all**, so I needed no `cp -a` copy); W03j's AST census of the container idiom; W03i's R0/R1 denominators and glob reconstruction; the campaign 0-of-89 resolution rate; the `systems_check` baseline; the `superseded[]` census; the registry validator. **No `reports/W25-*` was read, listed or referenced.** I heeded the interpreter correction and ran the probe under `/root/.local/share/uv/tools/pytest/bin/python3` (the guard module does `import pytest` at module level), never `python3 -m pytest`.

I did not add, remove or reorder any glob; did not edit the guard or any file; did not re-derive the manifest; did not run `scripts/regenerate_aso_chain.sh` or `scripts/preflight.sh`; did not invoke `atr_hrd_sarcoma_series.py` at all; did not `git fetch`; no network. I authored, proposed and applied **no repair, patch, gate or test**, and weakened, relaxed, reordered, skipped or disabled nothing. No content-policy refusal occurred in this unit.

## Method and inputs

One scratch script, `/tmp/claude-0/w66/probe.py`, which:

1. loads the guard by `importlib.util.spec_from_file_location` from `/home/user/Rare-cancers/research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py` and calls **its own** `_manifest()`, `_script()`, `_invoked()`, `_module_level_paths()`, `_names_opened_for_writing()`, `MANIFEST`, `REPO`. Nothing is reimplemented;
2. builds `deposited = {f["path"] for f in manifest["files"]}` and adds the guard's own `shipped_beside_the_list` manifest exemption (`:298-301`), so my filter is byte-identical to `test_every_input_an_invoked_module_names_is_in_the_archive`;
3. takes `uncovered = {deposited .py that exist on disk} − _invoked(_script())`;
4. for each uncovered module, replicates the guard's per-module body from `:304-310` exactly: skip a name in `_names_opened_for_writing(full)`; compute `cand = os.path.relpath(path, REPO)`; skip if `cand.startswith("..")`, `cand in deposited`, or `not os.path.exists(path)`.

Inputs: the committed manifest `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` (516 rows, loaded via `_manifest()`); `scripts/regenerate_aso_chain.sh` (via `_script()`); the 48 uncovered deposited modules; and, for adjudication of the hits, `research/modalities/junction_sirna.py`, `research/modalities/fusion_neoantigen_invalidation.py`, `research/modalities/aso_taf15_intron2_designs.py`.

Environment: Linux, CPython 3.11.15 at `/root/.local/share/uv/tools/pytest/bin/python3`, `PYTHONDONTWRITEBYTECODE=1`, no network. **Not preflight. No pytest run. No repository module was executed** — only the guard's pure AST/JSON helpers.

## Result

### R0 — The denominator (PRIMARY, EXECUTED)

| Quantity | Value |
|---|---:|
| Manifest `files` rows | 516 |
| Deposited `.py` that exist on disk | **77** |
| Deposited `.py` that do not exist on disk | 0 |
| `len(_invoked(_script()))` | **29** |
| Invoked steps not deposited | **0** (so `test_every_module_the_chain_invokes_is_in_the_archive` has nothing to fire on) |
| **Deposited `.py` NOT covered by `_invoked`** | **48** (77 − 29) |

So the `_invoked` scoping at `:293` looks at **29 of 77 deposited modules — 38%. 48 deposited modules, 62%, are never opened by the guard at all.** That is the size of route 2's aperture, and it is measured, not estimated.

### R1 — Per-module table over the 48 uncovered modules (PRIMARY, EXECUTED)

Columns: `n_resolved` = entries returned by the shipped `_module_level_paths`; `n_output_names` = size of the shipped `_names_opened_for_writing` set; `n_HITS` = entries surviving the guard's exact filter chain (existing, undeposited, non-output, inside the repo). The 14 modules where `_module_level_paths` returns `{}` are omitted from the rows below and counted in the summary.

| Module (uncovered, deposited) | n_resolved | n_output_names | **n_HITS** | Hits (`NAME -> path`) |
|---|---:|---:|---:|---|
| `research/manuscripts/aso_coverage_ladder.py` | 3 | 1 | 0 | — |
| `research/manuscripts/aso_journal_tables.py` | 1 | 1 | 0 | — |
| `research/manuscripts/aso_reagent_coverage.py` | 1 | 1 | 0 | — |
| `research/manuscripts/tcf12_breakpoint_assignment.py` | 1 | 1 | 0 | — |
| `research/manuscripts/tests/test_pdf_text_layer_is_orderable.py` | 1 | 0 | 0 | — |
| `research/modalities/aso_control_oligos.py` | 1 | 1 | 0 | — |
| `research/modalities/aso_delivery_antigen.py` | 5 | 1 | 0 | — |
| `research/modalities/aso_gap_length_tradeoff.py` | 2 | 1 | 0 | — |
| `research/modalities/aso_independent_verification.py` | 6 | 1 | 0 | — |
| `research/modalities/aso_noncoding_acceptor_designs.py` | 2 | 2 | 0 | — |
| `research/modalities/aso_offtarget_tissue_expression.py` | 3 | 2 | 0 | — |
| `research/modalities/aso_parent_gap_pairing.py` | 1 | 1 | 0 | — |
| `research/modalities/aso_premrna_offtarget.py` | 1 | 3 | 0 | — |
| **`research/modalities/aso_taf15_intron2_designs.py`** | 4 | 2 | **2** | `GENOME_SCREEN -> research/modalities/aso-genome-offtarget-taf15intron2.json`; `PREMRNA_SCREEN -> research/modalities/aso-premrna-offtarget-taf15intron2.json` |
| `research/modalities/depmap_sarcoma_dependency.py` | 1 | 1 | 0 | — |
| `research/modalities/emc_atr_vulnerability.py` | 3 | 3 | 0 | — |
| `research/modalities/emc_expression_panels.py` | 2 | 2 | 0 | — |
| `research/modalities/emc_model_junction_evidence.py` | 1 | 1 | 0 | — |
| `research/modalities/fet_ddr_axis_scan.py` | 1 | 1 | 0 | — |
| `research/modalities/fusion_breakpoints.py` | 1 | 1 | 0 | — |
| **`research/modalities/fusion_neoantigen_invalidation.py`** | 5 | 1 | **3** | `BREAKPOINT_ARTIFACT -> research/modalities/fusion-breakpoint-neoantigens.json`; `SINGLE_BREAKPOINT_ARTIFACT -> research/modalities/fusion-neoantigen-predictions.json`; `SEQ_CACHE -> research/modalities/nr4a-sequences-cache.json` |
| `research/modalities/junction_aso.py` | 2 | 1 | 0 | — |
| `research/modalities/junction_breakpoint_scan.py` | 1 | 1 | 0 | — |
| `research/modalities/junction_seam_retraction.py` | 1 | 1 | 0 | — |
| **`research/modalities/junction_sirna.py`** | 1 | 1 | **1** | `OUT -> research/modalities/junction-sirna-designs.json` |
| `research/modalities/tests/test_aso_gap_length_tradeoff.py` | 1 | 0 | 0 | — |
| `research/modalities/tests/test_aso_independent_verification.py` | 1 | 1 | 0 | — |
| `research/modalities/tests/test_aso_offtarget_tissue_expression.py` | 2 | 0 | 0 | — |
| `research/modalities/tests/test_aso_parent_gap_pairing.py` | 1 | 0 | 0 | — |
| `research/modalities/tests/test_aso_parent_null.py` | 1 | 0 | 0 | — |
| `research/modalities/tests/test_aso_per_junction_table.py` | 1 | 0 | 0 | — |
| `research/modalities/tests/test_aso_submission_numbers.py` | 6 | 0 | 0 | — |
| `research/modalities/tests/test_junction_aso_graded.py` | 2 | 0 | 0 | — |
| `research/modalities/tests/test_junction_aso_seam.py` | 2 | 0 | 0 | — |
| *(14 further uncovered modules)* | 0 | — | 0 | resolver returns `{}` |

**Totals: 48 uncovered modules · 34 with ≥1 resolved module-level path · 14 with none · 3 modules with ≥1 hit · 6 (name, module) hit pairs · 6 distinct artifacts.**

### R2 — The six distinct artifacts, adjudicated (PRIMARY, EXECUTED + source)

All six are **tracked** (`git ls-files` returns all six), **present on disk**, and **not in `files[]`**. Three of the six are not what the raw count suggests, so the honest number is smaller than 6:

| Artifact | Named by | Grade | Evidence |
|---|---|---|---|
| `research/modalities/aso-genome-offtarget-taf15intron2.json` | `aso_taf15_intron2_designs.py:316` | **TRUE GAP (input)** | W03j settled it as OPENED at `aso_taf15_intron2_designs.py:404` via the f-string path; grep shows the only `.py` naming it is that module — it is produced nowhere in `research/`, so it is an input to the lane. |
| `research/modalities/aso-premrna-offtarget-taf15intron2.json` | `aso_taf15_intron2_designs.py:317` | **TRUE GAP (input)** | Same loop; and it is *also* one of W03i's four `_PREMRNA_ARTIFACTS` — so this single artifact is hidden **twice over**, by route 1 in a chain-invoked step and by route 2 here. |
| `research/modalities/fusion-breakpoint-neoantigens.json` | `fusion_neoantigen_invalidation.py:51` | **TRUE GAP (input)** | Read at `:103` and `:426` (`json.load(open(BREAKPOINT_ARTIFACT, …))`, unguarded); named by 8+ other modules including its producer `fusion_breakpoints.py`. `fusion_neoantigen_invalidation.py` only re-stamps it under `--write` (`:856,:862`, through the loop variable `path`), so it is an input to this module, not its product. |
| `research/modalities/fusion-neoantigen-predictions.json` | `fusion_neoantigen_invalidation.py:53` | **TRUE GAP (input)** | Read at `:613`; produced by `fusion_neoantigen.py`. Same `--write` re-stamp caveat. |
| `research/modalities/nr4a-sequences-cache.json` | `fusion_neoantigen_invalidation.py:59` | **TRUE GAP (input)** | Read at `:616`, never written by this module; named by 8 other modules. A pure cross-module input. |
| `research/modalities/junction-sirna-designs.json` | `junction_sirna.py:32` | ⚠ **FALSE ALARM — the module's own OUTPUT** | `OUT` at `:32` is a documentary constant; `main()` at `:94-95` builds its **own local** `out` (with an `OUT_SUFFIX` env var) and writes at `:116-117` `with open(out, "w")`. `_names_opened_for_writing` records `out` (the local), not `OUT`, so the shipped output-detector misses it. Grep: the basename appears in **exactly one** `.py`, its producer. Nothing reads it. |

**So the guard-as-written, if it looked at the uncovered 48, would report 6 artifacts — of which 5 are genuine undeposited inputs and 1 would be a false alarm.** That last row is a *third*, previously unnamed limitation, independent of both of W03j's routes: `_names_opened_for_writing` (`:333-336`) only records `open(...)` whose first argument is an `ast.Name` in the *same* module scope, so a producer that writes through a **local** variable while naming the same file in a module-level constant is classed as reading an input it actually creates.

### R3 — Direct answer

**Route 2 is wider than a one-module curiosity, but it is not wider than the container idiom in the sense that matters.**

- **Wider in aperture, decisively.** The `_invoked` scoping hides **48 of 77 deposited modules (62%)**, and the resolver has no blind spot at all on 34 of them — it returns real bindings that the guard simply never asks for.
- **Wider in yield, modestly.** It surfaces **3 modules and 5 genuine undeposited inputs** (plus 1 false alarm), versus route 1's **1 chain-invoked module and 4** (`aso_sequence_manifest.py`'s `_PREMRNA_ARTIFACTS`). The two sets overlap in exactly one artifact, `aso-premrna-offtarget-taf15intron2.json`.
- **Narrower in severity, and this is the part that must travel with the count.** None of the three hit modules is chain-invoked, so **none of these five reads happens when a reader runs `scripts/regenerate_aso_chain.sh`** — the command the Availability statement names. Route 1's four are read by a *chain-invoked* step whose own comment (`aso_sequence_manifest.py:152-155`) declares that a missing artifact must break the build. The `fusion_neoantigen_invalidation.py` reads are unguarded (`json.load(open(...))`, no `try`/`exists` check) so they would raise on a clean download if a reader ran that module; the `aso_taf15_intron2_designs.py` reads are absence-tolerant (`:360`, per W03j). **Route 1 remains the sharper defect; route 2 is the larger unexamined surface.**

Note also the three `fusion_neoantigen_*`/`nr4a-sequences-cache` artifacts are *not* ASO-lane files. They surface because the deposit carries `fusion_neoantigen_invalidation.py` and `junction_sirna.py` as payload; whether such neoantigen-lane inputs belong in an ASO deposit at all is a scope question for the owner, not a defect I can grade.

## Validation evidence

**RUN.** Live checkout `/home/user/Rare-cancers`, HEAD `56f355f6…` → `fcb36d3c…`. CPython 3.11.15 at `/root/.local/share/uv/tools/pytest/bin/python3`, `PYTHONDONTWRITEBYTECODE=1`, `sys.dont_write_bytecode = True`, no network. **Not preflight. No pytest invocation.**

| # | Command | Real exit | Key verbatim output |
|---|---|---|---|
| V0 | `date -u; git rev-parse HEAD; git status --porcelain` (start) | 0 | `Tue Sep 8 04:50:55 UTC 2026`; `56f355f65b7b3e47aeb434ac02edf4cf049f40f3`; empty |
| V1 | `sed -n '1,60p;120,340p' …/test_the_deposited_chain_can_run_from_the_deposit.py` | 0 | `_DATA_SUFFIXES`, `_module_level_paths` docstring, `ev()` `return None`, `:302-310` filter chain, `shipped_beside_the_list` |
| **V2** | `PYTHONDONTWRITEBYTECODE=1 /root/.local/share/uv/tools/pytest/bin/python3 /tmp/claude-0/w66/probe.py` | **0** | `REPO const in guard: /home/user/Rare-cancers`; `n_files: 516 invoked: 29`; `deposited .py existing: 77 deposited .py missing on disk: 0 []`; `deposited .py NOT in _invoked: 48`; `invoked-but-not-deposited (context): []`; `modules with zero resolved module-level paths: 14`; `modules with >=1 HIT: 3`; `TOTAL HIT (name,module) pairs: 6`; `TOTAL DISTINCT undeposited existing non-output artifacts: 6` — full per-module table transcribed verbatim into R1 |
| V3 | `grep -n -E '^(OUT\|BREAKPOINT_ARTIFACT\|…)\b\|write_text\|json\.dump\|open\(\|dump\(' <3 modules>` | 0 | `junction_sirna.py:32 OUT = os.path.join(...)`, `:116 with open(out, "w") as fh`; `fusion_neoantigen_invalidation.py:103,:426,:613,:616 json.load(open(...))`, `:856,:862 with open(path, "w"…)`; `aso_taf15_intron2_designs.py:316,317`, `:404 d = json.load(open(path, …))` |
| V4 | `sed -n '110,120p' junction_sirna.py; grep -n 'def main\|out =\|OUT' junction_sirna.py` | 0 | `82: def main():` … `95:    out = os.path.join(os.path.dirname(__file__), f"junction-sirna-designs{suffix}.json")` — the local, not `OUT` |
| V5 | `grep -rn --include='*.py' -l "<basename>" research` ×5 | 0 | `junction-sirna-designs.json` → 1 file (`junction_sirna.py`); `aso-genome-offtarget-taf15intron2.json` → 1 (`aso_taf15_intron2_designs.py`); `fusion-breakpoint-neoantigens.json` → 8+; `fusion-neoantigen-predictions.json` → 4; `nr4a-sequences-cache.json` → 8+ |
| V6 | `git ls-files -- <the six artifacts>` | 0 | all six listed (all tracked) |
| V7 | `sed -n '99,106p;423,429p;610,619p' fusion_neoantigen_invalidation.py` | 0 | `art = artifact or json.load(open(BREAKPOINT_ARTIFACT, …))`; `art = json.load(open(SINGLE_BREAKPOINT_ARTIFACT, …))`; `seqs = json.load(open(SEQ_CACHE, …))` — no `try`, no `exists` guard |
| V8 | `git status --porcelain \| wc -l`; `find … -name '__pycache__' -newermt '2026-09-08 04:45'`; `ls -la --time-style=full-iso research/modalities/__pycache__`; `git check-ignore -v` | 0 | `0`; directory mtime `04:50:53` but **newest member `04:44:07`** (a prior worker's) — no `.pyc` from my run; `.gitignore:9:__pycache__/`; `git status --porcelain --ignored=no` → `0` |
| V9 | `rm -rf /tmp/claude-0/w66; ls -d /tmp/claude-0/w66; date -u; git rev-parse HEAD; git status --porcelain` (end) | 2 (ls) | `No such file or directory`; `Tue Sep 8 04:52:47 UTC 2026`; `fcb36d3c651223d90b98c0cb64169bb106e6e060`; empty |

**PROPOSED (NOT RUN):** widening `:293` from `_invoked(_script())` to the deposited `.py` set; teaching `ev()` the container node kinds; teaching `_names_opened_for_writing` about locals aliasing a module-level constant; adding any artifact to a `patterns` list; re-deriving the manifest; `scripts/regenerate_aso_chain.sh`; `scripts/preflight.sh`; `PREFLIGHT_FULL=1`; running the guard's pytest (W03j already did — exit 0, 10 passed — and I cite that rather than repeating it). **No content-policy refusal occurred in this unit.**

## Limitations

- **This is a simulation of what the guard *would* report, not a test run.** I called the shipped helpers and replicated the shipped filter chain, but the guard's assertion body was never executed over this set. The guard is green as W03j measured it; nothing here changes that.
- **My grades on the six are readings, not executions.** I read the open sites and the write sites; I did not run any of the three modules, did not unpack the archive, and did not run the chain against a clean download. TRUE GAP means "committed, undeposited, and read by name in committed code"; FALSE ALARM means "the module produces it, and the shipped output-detector misses that".
- **The measurement inherits every blind spot of the two helpers it calls.** It is a lower bound in three directions at once: route 1's container idiom is still invisible here (a hit hidden inside a tuple in an uncovered module is not counted); paths built by comprehension, f-string or without a `_DATA_SUFFIXES` extension are invisible; and function-body opens are invisible. **6 is a floor, not a census.**
- The 48/77 aperture is a statement about `.py` files in `files[]`. I did not examine deposited non-`.py` payload, and I did not audit the 14 zero-resolution modules for anything.
- Three of the five true gaps are neoantigen-lane, not ASO-lane, files. Whether they are in-scope for this deposit at all is the owner's judgement; I graded only their relationship to the guard.
- HEAD moved under me and `COMMON-BRIEF.md` changed on disk mid-run. I did not re-read the brief after the change beyond the harness diff; per W35b the movement is campaign-directory-only, and my inputs are all outside it.
- Measured at one working tree, one machine, one manifest. Nothing here is a statement about CI or about the published Zenodo archive's actual contents.
- **Nothing in this report is evidence about any oligonucleotide's efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab. A manifest's contents are a statement about file freshness and nothing else.**

## Stop condition

Set up front, four clauses under **Question**. **Met, all four.** (a) R0 — 77 deposited existing `.py`, 29 invoked, **48 uncovered**, all computed from the shipped `_manifest()`/`_invoked()`/`_script()`. (b) V2 — the guard module was imported and its real `_module_level_paths` and `_names_opened_for_writing` called; the `:302-310` filter chain including `shipped_beside_the_list` was replicated exactly; nothing was reimplemented. (c) R1 — per-module table for all 48 (34 rows with resolved paths, 14 with none), totals **3 modules / 6 hit pairs / 6 distinct artifacts**, and R2 adjudicates each of the six to **5 TRUE GAP + 1 FALSE ALARM**. (d) V8/V9 — `git status --porcelain` empty at start and end, no bytecode written into the tree, scratch deleted and confirmed absent. Returning now.

## Tool-call and wall-clock count actually used

**19 tool calls** (all `Bash`; no `Read`, no `Skill`, no network, no background task, no subagent, no `cp -a` copy). Two calls were paired-parallel in the first block. **Wall clock 04:50:55Z → 04:52:47Z ≈ 1.9 minutes of execution**, plus reading (~5 min) and report drafting. Well inside the ~40 calls / ~40 minutes target.

## Next concrete action

**For the PUB-ASO owner — the decision has not changed, and it should not be enlarged by this result.** W03i/W03j's four `aso-premrna-offtarget-*.json` remain the only artifacts read by a *chain-invoked, unconditionally-opening* deposited step, and they remain the owner's call on `aso_archive_manifest.py:423-426`. Route 2's five add scope questions, not urgency: none of them is executed by the Availability statement's command. **I have deliberately authored no patch, and none should be authored by a worker** — it changes what a published deposit contains.

**The most useful successor measurement in this lane** is now narrow and mechanical, and it is *not* another sweep of the same helpers. Route 1 and route 2 have both been characterised on `_DATA_SUFFIXES`-terminated module-level string constants; **the unmeasured surface is now the third limitation this unit found — `_names_opened_for_writing`'s scope.** Concretely: for each of the 77 deposited modules, compare the set of names that helper returns against the set of module-level constants whose value is written anywhere in the file *through a local alias* (`out = OUT`-shaped, or a loop variable over a tuple of constants as at `fusion_neoantigen_invalidation.py:840`), and count how many deposited modules would produce a false alarm and how many would produce a false *pass* (a genuine input mistaken for an output). `junction_sirna.py` gives one of the first kind already. That measurement decides whether the guard's output-detector is a per-module quirk or a systematic mis-classifier — and unlike this unit's question, its answer could change whether the guard's *current* green is trustworthy on the 29 modules it does look at. It needs a read-only import, no scratch copy, and about ten minutes.
