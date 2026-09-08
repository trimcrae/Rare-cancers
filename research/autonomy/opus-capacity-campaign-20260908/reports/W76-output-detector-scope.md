<!-- collected 2026-09-08T05:03:52Z by campaign coordinator; agent id aac846dcc7eddb4c5; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aac846dcc7eddb4c5.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

W76, lane 3 (ASO deposited-chain guard), OPUS-CAPACITY-CAMPAIGN-20260908. Named successor to W66.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the runtime model from the child transcript.

- `date -u` **start** `Tue Sep  8 04:56:20 UTC 2026`; **end** `Tue Sep  8 05:00:15 UTC 2026` (report drafting followed).
- `git rev-parse HEAD` **start** `129a4e2a1c39352a7a697c42445bb27fc50f9b0c`; **end** `2121960e980034c4c727c2947e6badd888f2dc27`. HEAD moved under me (coordinator collection commits). Per the brief's W35b item those commits touch only the campaign directory; every input I measured is outside it.
- `git status --porcelain` **empty at start and empty at end** (`| wc -l` → `0`). I wrote nothing in `/home/user/Rare-cancers` and ran no git write operation. Scratch was `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/w76/`, **deleted before returning** — the entire scratchpad directory removed, `ls -d` → `No such file or directory`, exit 2. Run with `PYTHONDONTWRITEBYTECODE=1` **and** `sys.dont_write_bytecode = True`; verified afterwards that `find . -name '*.pyc' -newermt '2026-09-08 04:56'` returns nothing in the tree.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (the five very long proxy/truststore lines — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are elided; they name no model):

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

W66's named successor, verbatim in substance: **for each of the 77 deposited `.py` modules, compare the set `_names_opened_for_writing` returns against the set of module-level constants the file actually writes through a local alias — how many deposited modules would produce a FALSE ALARM (a product mistaken for an input), and how many a FALSE PASS (a genuine input mistaken for an output and skipped by `:305`)?** The false-pass direction is the one that matters: it is the only one of W66's three limitations that could make the guard's *current* green on the 29 chain-invoked modules untrustworthy.

**Stop condition, set up front, four clauses:** (a) both counts computed from the *shipped* `_manifest`/`_invoked`/`_script`/`_module_level_paths`/`_names_opened_for_writing`, imported and called, nothing reimplemented; (b) a per-module table over all 77 with the two counts; (c) the false-pass direction resolved by two independent mechanical checks, not one; (d) tree untouched, no `.pyc`, scratch deleted. **All four met.**

## Prior-work check

Read in full before running anything: `research/autonomy/opus-capacity-campaign-20260908/COMMON-BRIEF.md` (601 lines, including the whole "Known, measured, and NOT worth rediscovering" section and the pytest-interpreter trap), `CORPUS-CONTEXT.md` (82 lines), `CLOSED-WORK.md` (70 lines), `reports/W66-uninvoked-deposited-modules.md` (221 lines) and `reports/W03j-deposited-chain-guard-blind-spot.md` (220 lines). Then the guard source: `sed -n '195,345p' research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py` (`_module_level_paths`, `_names_opened_for_writing`, `test_every_input_an_invoked_module_names_is_in_the_archive`).

Taken as given, not re-measured: W03j's pytest run (exit 0, 10 passed) — **I ran no pytest at all**; W03j's container-idiom AST census; W66's 77/29/48 denominator (I recomputed it as a by-product of calling the same shipped helpers, and it reproduced exactly: `DEPOSITED_PY 77 INVOKED 29`); the campaign 0-of-89 resolution rate; the `systems_check` baseline; the `superseded[]` census. **No `reports/W25-*` was read, listed or referenced.** I heeded the interpreter correction and ran every probe under `/root/.local/share/uv/tools/pytest/bin/python3`, never `python3 -m pytest`.

I did not edit the guard, did not re-derive the manifest, did not run `scripts/preflight.sh` or `scripts/regenerate_aso_chain.sh`, did not run any deposited module, never invoked `research/modalities/atr_hrd_sarcoma_series.py`, did not `git fetch`, used no network. I authored, proposed and applied **no repair, patch, gate or test**, and weakened, relaxed, reordered or skipped nothing. No content-policy refusal occurred in this unit.

## Method and inputs

Scratch scripts under `/tmp/claude-0/.../scratchpad/w76/` (deleted). Each loads the guard by `importlib.util.spec_from_file_location` and calls **its own** `_manifest()`, `_script()`, `_invoked()`, `_module_level_paths()`, `_names_opened_for_writing()`, `REPO`, `MANIFEST`. Nothing shipped is reimplemented.

Per module, over the 77 deposited existing `.py`:

- `P = _module_level_paths(full)` (name → absolute path), `W = _names_opened_for_writing(full)`.
- An **independent local path evaluator** determines, for every `open(..., mode)` call that passes the helper's *own* call filter (write mode `w`/`a`/`x`, literal mode string), what absolute path is actually written. It extends the guard's `ev` with the shapes the helper cannot see: function-local assignment chains resolved in source order, `JoinedStr` f-strings, `str + str`, `os.environ.get(k, "default")` → the default (the clean-run value), and `for`-loop targets — including tuple destructuring — over a literal tuple/list of constants. This is how `junction_sirna.py`'s `out = os.path.join(dirname(__file__), f"junction-sirna-designs{suffix}.json")` and `fusion_neoantigen_invalidation.py:839-840`'s `for path, b, target in ((BREAKPOINT_ARTIFACT, …), (SINGLE_BREAKPOINT_ARTIFACT, …))` are both resolved.
- **FALSE ALARM** ≔ `name ∈ P`, `name ∉ W`, and `normpath(P[name])` is in the set of paths the module actually writes. Then the guard's exact filter chain from `:304-310` (`cand.startswith("..")` / `cand in deposited ∪ shipped_beside_the_list` / `os.path.exists`) is applied to see which survive to the `missing` dict.
- **FALSE PASS** ≔ `name ∈ W ∩ P` (so `:305` skips it) but `normpath(P[name])` is **not** in the set of paths the module writes — i.e. the helper attributed a write to a constant the module never writes, and a genuine input is skipped.
- A second, independent false-pass check, not relying on my evaluator: enumerate every write-`open` site whose first argument is an `ast.Name` that is **locally bound** in an enclosing function scope *and* collides with a name in `P`. That is the shadowing mechanism by which a false pass could arise at all.

Inputs: `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` (516 rows, loaded via `_manifest()`), `scripts/regenerate_aso_chain.sh` (via `_script()`), and the 77 deposited `.py` files. Environment: Linux, CPython 3.11.15 at `/root/.local/share/uv/tools/pytest/bin/python3`, `PYTHONDONTWRITEBYTECODE=1`, no network.

## Result

### R0 — Denominator (PRIMARY, EXECUTED)

| Quantity | Value |
|---|---:|
| Deposited `.py` existing on disk | **77** |
| `len(_invoked(_script()))` | **29** |
| Σ `|_module_level_paths|` over the 77 | **97** names |
| Σ `|_names_opened_for_writing|` over the 77 | **76** names |
| `W ∩ P` pairs — the entire population a FALSE PASS could come from | **35** |

### R1 — FALSE ALARM: 3 modules of 77 (2 surviving the guard's filter) — PRIMARY, EXECUTED

| Module | invoked | Constant | Path | Survives `:306-310`? |
|---|---|---|---|---|
| `research/modalities/junction_sirna.py` | no | `OUT` | `research/modalities/junction-sirna-designs.json` | **yes** |
| `research/modalities/fusion_neoantigen_invalidation.py` | no | `BREAKPOINT_ARTIFACT` | `research/modalities/fusion-breakpoint-neoantigens.json` | **yes** |
| `research/modalities/fusion_neoantigen_invalidation.py` | no | `SINGLE_BREAKPOINT_ARTIFACT` | `research/modalities/fusion-neoantigen-predictions.json` | **yes** |
| `research/modalities/junction_aso.py` | no | `OUT` | `research/modalities/junction-aso-designs.json` | no — already `in deposited` |

**Mechanical count: 3 of 77 modules produce ≥1 false-alarm signal; 2 of 77 produce one that survives the guard's own filter chain; 0 of them are chain-invoked.**

⚠ **Adjudication correction to the mechanical count, and it matters.** Only `junction_sirna.py` is a *pure* false alarm in W66's sense — `OUT` is the module's sole product, nothing else in the tree reads it (W66's V5: one `.py` names the basename), so the guard would report a product as a missing input. The two `fusion_neoantigen_invalidation.py` constants are **read-modify-write**: they are unconditionally `json.load`ed at `:103` and `:426` and only re-stamped under `--write` at `:857,:862`. W66 graded them TRUE GAP (input), and that grade is right: an artifact that is read before it is written is a genuine input regardless of whether the module also rewrites it. So the honest reading is **1 pure false alarm (`junction_sirna.py`), plus 2 signals on artifacts that are legitimately inputs as well as products**. The mechanical rule "written through a local alias ⇒ product" is itself imprecise in exactly this case; I report both numbers rather than choosing.

### R2 — FALSE PASS: **0 of 77** — PRIMARY, EXECUTED, two independent checks

| Check | Result |
|---|---|
| Names in `W ∩ P` (35 pairs) whose resolved path the module never actually writes | **0** |
| Write-`open` sites whose recorded `ast.Name` is **locally bound** and collides with a name in `P` | **0** |

Every one of the 35 `W ∩ P` names is written to its own resolved path by a *module-scope* `Name` passed directly to `open(..., "w")`. There is no shadowing anywhere in the 77: no deposited module has a function-local variable whose name coincides with a resolved module-level path constant at a write site. The false-pass mechanism has **no instance in this corpus**.

Spot-checked by grep because the names looked like inputs — all confirmed genuine writes at module scope: `aso_offtarget_tissue_expression.py:813 open(INPUTS,"w")`, `emc_expression_panels.py:2891 json.dump(inp, open(INPUTS,"w"))`, `emc_atr_vulnerability.py:1047 open(_ACC_CACHE_PATH,"w")` and `:3182,:3217 open(INPUTS,"w")`, `aso_premrna_offtarget.py:518 open(CACHE,"w")`.

### R3 — How much of the green on the 29 rests on `:305` at all (PRIMARY, EXECUTED)

Over the 29 chain-invoked deposited modules, the number of candidates that exist, are undeposited, are inside the repo, and are suppressed **solely** by `if name in outputs: continue` is **3**:

| Module | Constant | Path |
|---|---|---|
| `research/manuscripts/claim_coverage.py` | `ARTIFACT` | `research/manuscripts/claim-coverage.json` |
| `research/manuscripts/figures/svg_to_print_formats.py` | `MANIFEST` | `research/manuscripts/figures/submission/print-formats-manifest.json` |
| `research/manuscripts/lint_citations.py` | `LEDGER` | `research/manuscripts/citation-provenance-ledger.json` |

All three are direct module-scope writes, so all three suppressions are correct. Two of the three are the ones the helper's own docstring names (`svg_to_print_formats.py`, `lint_citations.py --baseline`); `claim_coverage.py` is a fourth case the docstring does not mention, and `aso_archive_manifest.py` — which the docstring does name — is suppressed one step earlier by `shipped_beside_the_list`, not by `:305`. That is a small documentation drift, not a defect.

### R4 — Direct answer to the load-bearing question

**The guard's current green on the 29 chain-invoked modules is NOT weakened by any false pass, because there is no false pass to find.** `_names_opened_for_writing`'s scope limitation is **directional in this corpus**: it can only ever *under*-populate the outputs set (it misses writes made through a local variable), and an under-populated outputs set makes the guard **stricter**, never laxer. The lax direction — a genuine input landing in `outputs` and being skipped at `:305` — requires a local name to shadow a resolved module-level path constant at a write site, and that happens **zero times across all 77 deposited modules**. The entire suppression surface on the 29 is 3 candidates, and all 3 are real products.

So W66's third limitation is a **false-alarm-only** defect: it can make the guard red on something it should not (which is loud and self-correcting), and it cannot make the guard silently green. It is a per-module quirk in effect (1 pure instance, 3 signals, all in non-chain-invoked modules), not a systematic mis-classifier. The trustworthiness of the 10/10 exit-0 W03j measured is untouched by this axis; W03j's two escape routes (the container idiom at `:218-233,:240`, and the `_invoked` scoping at `:293`) remain the only measured ways this guard passes without looking.

## Validation evidence

**RUN.** Live checkout `/home/user/Rare-cancers`, HEAD `129a4e2a…` → `2121960e…`. CPython 3.11.15 at `/root/.local/share/uv/tools/pytest/bin/python3`, `PYTHONDONTWRITEBYTECODE=1`, `sys.dont_write_bytecode = True`, no network. **Not preflight. No pytest invocation. No deposited module executed.**

| # | Command | Real exit | Key verbatim output |
|---|---|---|---|
| V0 | `date -u; git rev-parse HEAD; git status --porcelain` (start) | 0 | `Tue Sep  8 04:56:20 UTC 2026`; `129a4e2a1c39352a7a697c42445bb27fc50f9b0c`; empty |
| V1 | `sed -n '195,345p' …/test_the_deposited_chain_can_run_from_the_deposit.py` | 0 | `_DATA_SUFFIXES`; `ev()` … `return None`; `_names_opened_for_writing` … `if isinstance(node.args[0], ast.Name): written.add(node.args[0].id)`; the `:304-310` filter chain |
| V2 | `probe.py` (literal `out = OUT` / loop-over-tuple-of-Names only) | 0 | `DEPOSITED_PY 77 INVOKED 29`; `modules with >=1 false-alarm candidate: 0` — **the narrow shape in the dispatch finds nothing**, because `junction_sirna` reconstructs the path rather than aliasing the constant |
| V3 | `sed -n '25,35p;88,120p' junction_sirna.py; sed -n '835,865p' fusion_neoantigen_invalidation.py` | 0 | `:32 OUT = os.path.join(...)`; `:94 suffix = os.environ.get("OUT_SUFFIX","")`; `:95 out = os.path.join(..., f"junction-sirna-designs{suffix}.json")`; `:116 with open(out,"w")`; `:839-840 for path, b, target in ((BREAKPOINT_ARTIFACT, banner, art), (SINGLE_BREAKPOINT_ARTIFACT, banner2, art2)):`; `:857,:862 with open(path,"w"…)` |
| **V4** | `PYTHONDONTWRITEBYTECODE=1 …/pytest/bin/python3 probe2.py` (broadened evaluator) | **0** | `denominator: deposited .py = 77  invoked = 29`; the three false-alarm modules verbatim as R1; `=== FALSE PASS … ===` **empty**; `modules with >=1 false alarm (any): 3`; `modules whose false alarm survives the guard filter chain: 2`; `of those, chain-invoked: 0`; `modules with >=1 false pass: 0  chain-invoked: 0`; full 68-row per-module table (`nP`/`nW`/`FA`/`FA_hit`/`FP`) transcribed into R5 below |
| **V5** | `… probe4.py` (independent shadowing check) | **0** | `sum |P| over 77 = 97  sum |W| over 77 = 76`; `W-and-P overlap pairs …: 35` (all 35 listed); `write-open sites where the Name is LOCALLY bound and collides with a resolved module const: 0` |
| V6 | `grep -n '^INPUTS\|^CACHE\|^_ACC_CACHE_PATH' …; grep -n 'open(INPUTS\|open(CACHE\|open(_ACC_CACHE_PATH' research/modalities/*.py` | 0 | `aso_offtarget_tissue_expression.py:813 with open(INPUTS,"w"…)`; `emc_atr_vulnerability.py:1047 with open(_ACC_CACHE_PATH,"w"…)`, `:3182 json.dump(inp, open(INPUTS,"w"))`; `aso_premrna_offtarget.py:518 with open(CACHE,"w")` — all module-scope writes |
| **V7** | `… probe5.py` (what `:305` actually suppresses on the 29) | **0** | `candidates … SKIPPED solely by the `name in outputs` test at :305 … : 3` — `claim_coverage.py ARTIFACT`, `svg_to_print_formats.py MANIFEST`, `lint_citations.py LEDGER` |
| V8 | `find . -name '*.pyc' -newermt '2026-09-08 04:56'`; `git status --porcelain \| wc -l` | 0 | no output (no bytecode written into the tree); `0` |
| V9 | `rm -rf …/scratchpad; ls -d …/scratchpad; date -u; git rev-parse HEAD; git status --porcelain` (end) | 2 (ls) | `No such file or directory`; `Tue Sep  8 05:00:15 UTC 2026`; `2121960e980034c4c727c2947e6badd888f2dc27`; empty |

**PROPOSED (NOT RUN):** any change to `_names_opened_for_writing`, `_module_level_paths`, `_invoked`'s scope, or any `patterns` list; re-deriving the manifest; running the guard's pytest (W03j already did — exit 0, 10 passed — cited, not repeated); `scripts/regenerate_aso_chain.sh`; `scripts/preflight.sh`; `PREFLIGHT_FULL=1`; executing any deposited module. **No content-policy refusal occurred in this unit.**

### R5 — Per-module table (PRIMARY, EXECUTED)

All 77 deposited `.py` were analysed. The 9 with `nP = 0` **and** `nW = 0` cannot produce either error and are omitted as rows (they are counted in the 77): `FA` = false-alarm constants, `FA_hit` = those surviving `:306-310`, `FP` = false passes.

| Module | invoked | nP | nW | FA | FA_hit | FP |
|---|---|---:|---:|---:|---:|---:|
| `research/manuscripts/aso_archive_manifest.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/aso_coverage_ladder.py` | no | 3 | 1 | 0 | 0 | 0 |
| `research/manuscripts/aso_journal_tables.py` | no | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/aso_priorart_evidence.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/aso_reagent_coverage.py` | no | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/aso_sequence_manifest.py` | yes | 2 | 2 | 0 | 0 | 0 |
| `research/manuscripts/build_submission_docx.py` | yes | 0 | 1 | 0 | 0 | 0 |
| `research/manuscripts/build_submission_parts.py` | yes | 0 | 1 | 0 | 0 | 0 |
| `research/manuscripts/build_submission_pdf.py` | yes | 0 | 2 | 0 | 0 | 0 |
| `research/manuscripts/citation_scan_cache.py` | no | 0 | 1 | 0 | 0 | 0 |
| `research/manuscripts/claim_coverage.py` | yes | 2 | 1 | 0 | 0 | 0 |
| `research/manuscripts/figures/aso_chance_baseline_figure.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/figures/aso_figure_provenance.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/figures/aso_gap_length_figure.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/figures/aso_junction_space_figure.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/figures/aso_multipartner_seam_figure.py` | yes | 2 | 1 | 0 | 0 | 0 |
| `research/manuscripts/figures/svg_to_print_formats.py` | yes | 1 | 2 | 0 | 0 | 0 |
| `research/manuscripts/figures/svg_to_submission_formats.py` | yes | 0 | 2 | 0 | 0 | 0 |
| `research/manuscripts/lint_citations.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/lint_consistency.py` | yes | 1 | 0 | 0 | 0 | 0 |
| `research/manuscripts/submission_citations.py` | yes | 3 | 4 | 0 | 0 | 0 |
| `research/manuscripts/submission_metrics.py` | yes | 0 | 1 | 0 | 0 | 0 |
| `research/manuscripts/submission_packet.py` | yes | 0 | 1 | 0 | 0 | 0 |
| `research/manuscripts/submission_tables.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/tcf12_breakpoint_assignment.py` | no | 1 | 1 | 0 | 0 | 0 |
| `research/manuscripts/tests/test_pdf_text_layer_is_orderable.py` | no | 1 | 0 | 0 | 0 | 0 |
| `research/modalities/aso_control_oligos.py` | no | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/aso_delivery_antigen.py` | no | 5 | 1 | 0 | 0 | 0 |
| `research/modalities/aso_gap_length_tradeoff.py` | no | 2 | 1 | 0 | 0 | 0 |
| `research/modalities/aso_genome_offtarget.py` | no | 0 | 3 | 0 | 0 | 0 |
| `research/modalities/aso_independent_verification.py` | no | 6 | 1 | 0 | 0 | 0 |
| `research/modalities/aso_insilico.py` | no | 0 | 1 | 0 | 0 | 0 |
| `research/modalities/aso_noncoding_acceptor_designs.py` | no | 2 | 2 | 0 | 0 | 0 |
| `research/modalities/aso_noncoding_acceptor_screened_table.py` | yes | 6 | 1 | 0 | 0 | 0 |
| `research/modalities/aso_offtarget_duplex_energy.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/aso_offtarget_tissue_expression.py` | no | 3 | 2 | 0 | 0 | 0 |
| `research/modalities/aso_parent_gap_pairing.py` | no | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/aso_parent_null.py` | no | 0 | 1 | 0 | 0 | 0 |
| `research/modalities/aso_per_junction_table.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/aso_premrna_offtarget.py` | no | 1 | 3 | 0 | 0 | 0 |
| `research/modalities/aso_taf15_intron2_designs.py` | no | 4 | 2 | 0 | 0 | 0 |
| `research/modalities/depmap_sarcoma_dependency.py` | no | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/emc_atr_vulnerability.py` | no | 3 | 3 | 0 | 0 | 0 |
| `research/modalities/emc_expression_panels.py` | no | 2 | 2 | 0 | 0 | 0 |
| `research/modalities/emc_model_junction_evidence.py` | no | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/fet_ddr_axis_scan.py` | no | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/fusion_breakpoints.py` | no | 1 | 1 | 0 | 0 | 0 |
| **`research/modalities/fusion_neoantigen_invalidation.py`** | no | 5 | 1 | **2** | **2** | 0 |
| **`research/modalities/junction_aso.py`** | no | 2 | 1 | **1** | 0 | 0 |
| `research/modalities/junction_aso_locus_collapse.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/junction_aso_offtarget.py` | yes | 0 | 2 | 0 | 0 | 0 |
| `research/modalities/junction_aso_thermo.py` | yes | 0 | 1 | 0 | 0 | 0 |
| `research/modalities/junction_breakpoint_scan.py` | no | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/junction_seam_retraction.py` | no | 1 | 1 | 0 | 0 | 0 |
| **`research/modalities/junction_sirna.py`** | no | 1 | 1 | **1** | **1** | 0 |
| `research/modalities/nr4a3_fusion_atlas.py` | no | 0 | 1 | 0 | 0 | 0 |
| `research/modalities/offtarget_chance_baseline.py` | yes | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/tests/test_aso_gap_length_tradeoff.py` | no | 1 | 0 | 0 | 0 | 0 |
| `research/modalities/tests/test_aso_genome_offtarget.py` | no | 0 | 2 | 0 | 0 | 0 |
| `research/modalities/tests/test_aso_independent_verification.py` | no | 1 | 1 | 0 | 0 | 0 |
| `research/modalities/tests/test_aso_offtarget_tissue_expression.py` | no | 2 | 0 | 0 | 0 | 0 |
| `research/modalities/tests/test_aso_parent_gap_pairing.py` | no | 1 | 0 | 0 | 0 | 0 |
| `research/modalities/tests/test_aso_parent_null.py` | no | 1 | 0 | 0 | 0 | 0 |
| `research/modalities/tests/test_aso_per_junction_table.py` | no | 1 | 0 | 0 | 0 | 0 |
| `research/modalities/tests/test_aso_submission_numbers.py` | no | 6 | 0 | 0 | 0 | 0 |
| `research/modalities/tests/test_junction_aso_graded.py` | no | 2 | 0 | 0 | 0 | 0 |
| `research/modalities/tests/test_junction_aso_seam.py` | no | 2 | 0 | 0 | 0 | 0 |
| *(9 further deposited modules, `nP = 0` and `nW = 0`)* | — | 0 | 0 | 0 | 0 | 0 |

**Totals over 77: FALSE ALARM 3 modules (2 surviving the filter, 0 chain-invoked); FALSE PASS 0 modules (0 chain-invoked).**

## Limitations

- **This is a simulation of what the guard *would* report on a widened scope, not a test run.** I called the shipped helpers and replicated the shipped filter chain; the guard's assertion body was never executed over this set. The guard is green as W03j measured it and nothing here changes that.
- **My write-path evaluator is mine, not shipped.** The false-alarm and false-pass verdicts depend on it. It is a lower bound on writes in both directions: a path built by comprehension, by a function call it cannot fold, by a non-default `OUT_SUFFIX` env value, or reached through a helper function's parameter is invisible to it. The independent shadowing check (V5, 0 sites) does **not** depend on it and is the stronger support for FP = 0.
- **`os.environ.get(k, default)` was resolved to its default.** With `OUT_SUFFIX` set, `junction_sirna.py` writes a *different* file and the false alarm on `OUT` would become correct. The clean-run value is the one that matters for a reader of the deposit, so the default is the right choice, but it is a choice.
- **The false-alarm rule is imprecise for read-modify-write artifacts**, as R1's adjudication note says: `fusion_neoantigen_invalidation.py`'s two are written *and* read unconditionally, so calling them false alarms would contradict W66's TRUE-GAP grade, which I believe is the right one. I report the mechanical count and the adjudicated count separately rather than collapsing them.
- **FP = 0 is a statement about the 77 deposited `.py` at this HEAD**, not a proof that the mechanism cannot occur. A future module that binds a function-local variable named `OUT` and writes it would create one silently, and no test in the tree would notice.
- This measures only `_names_opened_for_writing`'s scope. Route 1 (the container idiom) and route 2 (`_invoked` scoping) are untouched and remain as W03j and W66 measured them.
- HEAD moved under me. Per W35b that movement is campaign-directory-only; all my inputs are outside it.
- Measured at one working tree, one machine, against the committed manifest. Nothing here is a statement about CI or about the published Zenodo archive's actual contents.
- **Nothing in this report is evidence about any oligonucleotide's efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab. A manifest's contents are a statement about file freshness and nothing else.**

## Stop condition

Set up front, four clauses under **Question**. **Met, all four.** (a) V4/V5/V7 — every denominator and every helper output comes from the imported shipped module (`77`/`29` reproduced exactly); nothing shipped was reimplemented. (b) R5 — per-module table over all 77, with `nP`, `nW`, `FA`, `FA_hit`, `FP`. (c) R2 — false pass resolved to **0** by two independent checks, one of which (the shadowing enumeration, V5) does not use my evaluator at all; R3 quantifies the entire `:305` suppression surface on the 29 at 3 candidates, all correct. (d) V8/V9 — `git status --porcelain` empty at start and end, no `.pyc` written into the tree, entire scratch directory deleted and confirmed absent. Returning now.

## Tool-call and wall-clock count actually used

**14 tool calls** (2 `Read`, 12 `Bash`; the first block was two parallel calls). No `Skill`, no network, no background task, no subagent, no `cp -a` copy, no pytest run. **Wall clock 04:56:20Z → 05:00:15Z ≈ 3.9 minutes**, plus report drafting. Well inside the ~40 calls / ~40 minutes target.

## Next concrete action

**For the PUB-ASO owner: this result *narrows* the decision rather than enlarging it, and it should close the `_names_opened_for_writing` thread.** The output-detector's scope limitation is measured to be false-alarm-only in this corpus — it can make the guard shout, it cannot make it stay quiet — so the guard's 10/10 exit-0 stands as evidence for the 29 modules it inspects. The owner's single open call remains what W03i/W03j framed: whether the four `aso-premrna-offtarget-{18mer-5-8-5,20mer-5-10-5,ewsr1intron2,taf15intron2}.json` join the deposit (`aso_archive_manifest.py:423-426`). **I have deliberately authored no patch, and none should be authored by a worker** — it changes what a published deposit contains.

**The most useful successor measurement in this lane is now outside this file, and I say so plainly rather than inventing a fourth sweep of the same helpers.** All three of the guard's own limitations are characterised: container idiom (W03j), `_invoked` scoping (W66), output-detector scope (this unit, benign). The remaining unmeasured question is not about the guard's AST at all — it is whether the *published archive* actually contains what `files[]` says, which requires unpacking the deposited ZIP and comparing member digests against the manifest. That is a real, bounded, mechanical measurement, it needs no network if the archive exists locally, and it is the only step that would turn "the manifest is internally consistent" into "a reader who downloads the deposit can run the chain". If no local archive exists, the honest answer is **UNKNOWN**, and this lane has no viable successor without one.
