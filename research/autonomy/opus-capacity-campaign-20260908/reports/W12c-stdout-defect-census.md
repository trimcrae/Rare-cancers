> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Start `date -u`: `Tue Sep  8 02:30:44 UTC 2026`. End `date -u`: `Tue Sep  8 02:34:58 UTC 2026` (plus report drafting).

---

## Worker

**W12c**, lane 12 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start of run (proxy/no_proxy lines elided only where they are pure host lists; every identity-bearing line is verbatim):

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
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

End-of-run re-read of the identity-bearing subset was **identical**: `AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_CODE_VERSION=2.1.42`, `CLAUDE_EFFORT=medium`, `CLAUDE_CODE_ENTRYPOINT=remote`, `ANTHROPIC_BASE_URL=https://api.anthropic.com`, `CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71`.

**HEAD actually read — and it moved during my run, which I record rather than paper over.**
- Start: `git rev-parse HEAD` → `47aac85f874a57a6f981c3432abcf16980968aec` (**not** the `92abbcb905…` named in COMMON-BRIEF.md; the coordinator has been committing collected reports).
- End: `7d081218f107363573573e6d102e4334567adf77`.
- `git diff --name-only 47aac85..7d08121` → **13 files, all `research/autonomy/opus-capacity-campaign-20260908/reports/W*.md`**, including `W12b-locale-rederivation-proof.md` landing mid-run. Filtered to `\.py$|^scripts/|^systems/|^research/manuscripts/|^research/modalities/` → **0 files**. **No file I scanned changed between the two commits**, so every count below is valid at both.
- `git status --porcelain | wc -l` → `0` at end. I created and modified **nothing** in the tree; all execution was under `/tmp/claude-0/w12c/`. No git write of any kind.

I read the live cloud checkout at `/home/user/Rare-cancers`. I did **not** need the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/` for any claim here: every claim in this report is a measurement over the live tracked tree, not a novelty or absence claim about prior work. The one absence claim I do make (no io-encoding guard exists) is stated as measured-in-this-tree, not repository-wide-forever.

---

## Question

Two parts, both read-only, both about the second defect W12b isolated.

**(1) Is the stdout defect confined to the five modules W12b named?** W12b ran 215 real generator runs over 35 `research/manuscripts` generators and found five that stay broken under a hostile locale even with every file `open()` pinned, because `print()` of a non-ASCII literal goes to a `sys.stdout` `TextIOWrapper` the interpreter built from the process locale before any repository code runs. W12b's sample was **35 modules in one directory**. Nothing had asked how large the site population actually is across `research/manuscripts`, `research/modalities`, `scripts` and `systems`, or how much of it sits inside a gate.

**(2) What exactly does `_generated_utc` cost?** W12b found 8 artifacts that never re-derive byte-identically in any locale, and attributed four of them to an embedded `_generated_utc` wall-clock stamp. It explicitly left "does the repository hash these artifacts for provenance?" to the owner as an open design question. That intersection — stamped **and** hashed — is the part that is a measurable defect rather than a preference, and it had not been quantified.

Both are open. Neither replays anything closed.

---

## Prior-work check

```
$ ls research/autonomy/opus-capacity-campaign-20260908/reports/W12*
W12-windows-portability-defects.md            (461 lines, read in full)
W12b-locale-rederivation-proof.md             (landed mid-run at 7d08121; read)
```

- `W12-windows-portability-defects.md` — read. Its R1–R7 are the **file-I/O** class (`open()` without `encoding=`, `Path.read_text/write_text`, `newline=`, CRLF sha256 divergence). Its AST census (52 / 1221 / 3 / 0 bare text opens by directory) counted **`open()` call sites**, not print sites. It never scanned `print()`. I am not re-reporting R1–R7.
- `W12b-locale-rederivation-proof.md` — read. Confirmed the five STILL-BROKEN rows and the exemplar line each names: `build_submission_parts.py:395` (U+2014), `emc_systems_map_check.py:1364` (U+00B7), `submission_metrics.py:630` (U+2014), `lint_readability.py:359` (U+26A0), `line_citations.py:688` (U+26A0). **All five of those exact file:line pairs appear in my independent inventory**, which is a cross-check on my scanner rather than a rediscovery. W12b's line 471 states the `_generated_utc` question and hands it to the owner unquantified — that is exactly the gap I filled.
- W12b's raw run evidence at `/tmp/claude-0/w12b/` (`check-results.json`, `write-results.json`, `patch-report.json`, `modules.txt`) was reconstructed independently to confirm the 8 never-matching artifacts and the still-broken set before I built on them.

```
$ grep -rn "PYTHONIOENCODING|PYTHONUTF8|stdout.reconfigure|getpreferredencoding" \
      --include=* . | grep -v '^\./\.git'
```
→ every hit is **inside W12's own report file**. **Zero code, test, gate, workflow or documentation hits.** No io-encoding guard exists in this tree. (Measured absence in the tracked tree — UNKNOWN whether anyone ever knew, not proof nobody did.)

**CLOSED-WORK.md items I confirmed I am not touching:** PUB-EMC-CLASSIFICATION (user-rejected, closed) — untouched; any Brenca route — untouched, no accession or case-identity work performed; lane 11's source-index — untouched, I read none of `research/source-index` and W11b remains sole owner; the retained NR4A Perspective refusal — not approached; all unrecovered sources (Pazopanib, anthracycline, sunitinib, trabectedin, Wagner, CTARC) — irrelevant to a tooling finding and not consulted. **This report makes no scientific or clinical claim of any kind.**

---

## Method / inputs

- Live checkout `/home/user/Rare-cancers`, read-only, HEAD `47aac85f…` → `7d081218…` (no scanned file differs between them).
- Interpreter `Python 3.11.15`, Linux `6.18.44-fc-v24`. Container baseline: `sys.stdout.encoding = utf-8`, `locale.getpreferredencoding(False) = utf-8`, `sys.flags.utf8_mode = 1`, `LANG`/`LC_ALL` unset — which is exactly why the defect is invisible here without a forced locale.
- **Part 1 scanner** (`/tmp/claude-0/w12c/scan_print.py`, written and run outside the tree): `ast.parse` + `ast.walk` over every `.py` under `research/manuscripts`, `research/modalities`, `scripts`, `systems`, excluding `.git`/`__pycache__`/`.venv`/`node_modules`. A site is an `ast.Call` whose func is `Name('print')` or `sys.stdout.write` / `sys.stderr.write`, and whose argument subtree contains at least one `ast.Constant` string holding a codepoint > 127 — including literal segments inside f-strings (`JoinedStr`). Each site records file, line, call kind, the distinct non-ASCII characters, their codepoints and Unicode names, and whether the call also contains dynamic (non-literal) arguments.
- **Classification axes**, both computed from the tree: (a) module named anywhere in `scripts/preflight.sh` (`grep -oE '(research|scripts|systems)/[A-Za-z0-9_/]+\.py' scripts/preflight.sh`); (b) module's source contains a `"--check"` / `'--check'` literal. A third, sharper axis: the 18 explicit `--check` rows of the re-derivation gate at `scripts/preflight.sh:849-866`.
- **cp1252 encodability** computed per character with `str.encode("cp1252")`, because the Windows console codepage — not ASCII — is the realistic hostile target.
- **Part 2**: `git ls-files` → every tracked non-`.py` file → regex `"_generated_utc"\s*:\s*"([^"]+)"` to require a **real embedded stamp value**, not a prose mention. Then sha256 of each stamped artifact's current bytes, and a search of every tracked file for that 64-hex digest appearing verbatim — an exact-digest provenance record, not a co-occurrence heuristic. `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` was additionally parsed as JSON and its 516 `files[]` `{path, sha256}` entries checked against current bytes.
- Hostile-locale reproduction: `LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0`, giving `sys.stdout.encoding = ascii`. `scripts/preflight.sh` was **not run**. No network.

---

## Result

### Part 1 — the stdout defect is NOT confined to five modules

**PRIMARY (measured by AST over the tracked tree).** 1,359 `.py` files parsed, **0 unparsed**.

| Population | sites | files |
|---|---:|---:|
| All `print()` / `sys.std*.write` of a non-ASCII literal | **1,031** | **317** |
| …of which the literal is **not encodable in cp1252** | **323** | — |
| In a module that has `--check` **or** is named in `preflight.sh` | **195** | **75** |
| In one of the **18 `--check` rows of the preflight re-derivation gate** | **52** | **16 of 18** |
| W12b's named still-broken set | 23 | 5 |

The five modules W12b named account for **23 of 1,031 sites (2.2 %)**. **PRIMARY.**

**Character census (site count containing each character), top of distribution — PRIMARY:**

| char | codepoint | name | sites | cp1252 |
|---|---|---|---:|---|
| `—` | U+2014 | EM DASH | 778 | encodable |
| `⛔` | U+26D4 | NO ENTRY | 101 | **NOT** |
| `⚠` | U+26A0 | WARNING SIGN | 77 | **NOT** |
| `Δ` | U+0394 | GREEK CAPITAL DELTA | 49 | **NOT** |
| `→` | U+2192 | RIGHTWARDS ARROW | 35 | **NOT** |
| `…` | U+2026 | HORIZONTAL ELLIPSIS | 25 | encodable |
| `✅` | U+2705 | WHITE HEAVY CHECK MARK | 21 | **NOT** |
| `±` | U+00B1 | PLUS-MINUS SIGN | 21 | encodable |
| `§` | U+00A7 | SECTION SIGN | 13 | encodable |
| `·` | U+00B7 | MIDDLE DOT | 12 | encodable |
| `★` | U+2605 | BLACK STAR | 10 | **NOT** |
| `≈` | U+2248 | ALMOST EQUAL TO | 9 | **NOT** |
| `Å` | U+00C5 | LATIN CAPITAL A WITH RING | 8 | encodable |

Long tail (each ≤ 5 sites): `× − ⭐ ≤ λ ⚖ ✗ ❌ – ° ↔ γ ⏳ ⏱ ✓ ÷ ─ └ ⇒ ≥ α σ ∈ ↩ ⏸ ⭑ ⓘ ↻`.

**31 distinct characters are cp1252-unencodable:** `Δ α γ λ σ → ↔ ↩ ↻ ⇒ ∈ − ≈ ≤ ≥ ⏱ ⏳ ⏸ ⓘ ─ └ ★ ⚖ ⚠ ⛔ ✅ ✓ ✗ ❌ ⭐ ⭑`. These are the ones that fail on a **modern Windows cp1252 console**; the encodable ones (`— … § · ± Å ° × ÷`) survive cp1252 and fail only on a stricter ASCII / cp437 / cp850 console. **This distinction is the practical severity axis and W12b's sample did not have enough sites to expose it.**

**The 18 preflight `--check` gate rows (`scripts/preflight.sh:849-866`) — PRIMARY, full inventory with file:line:**

| gate row module | sites | cp1252-unenc | lines |
|---|---:|---:|---|
| `research/manuscripts/submission_tables.py` | 3 | **2** | 3174 `⛔`, 3184 `⛔`, 3190 `…` |
| `research/manuscripts/claim_coverage.py` | 1 | 0 | 847 `—` |
| `research/manuscripts/submission_citations.py` | 6 | **4** | 378 `—`, 391 `⛔`, 393 `—⚠`, 401 `⛔`, 476 `⛔`, 478 `—` |
| `research/manuscripts/submission_metrics.py` | 3 | **2** | 607 `⛔`, 617 `—⛔`, 630 `—` |
| `research/manuscripts/aso_sequence_manifest.py` | 2 | **1** | 1177 `…⛔`, 1188 `—` |
| `research/manuscripts/aso_journal_tables.py` | 2 | 0 | 345 `—`, 349 `—` |
| `research/modalities/aso_offtarget_duplex_energy.py` | 2 | 0 | 351 `—`, 366 `—` |
| `research/manuscripts/submission_packet.py` | 2 | 0 | 555 `—`, 558 `—` |
| `research/manuscripts/vaccine_path_tables.py` | 1 | 0 | 239 `—` |
| `research/manuscripts/aso_archive_manifest.py` | 5 | **3** | 1964 `—`, 1970 `—`, 2000 `⛔`, 2003 `⛔`, 2008 `—⛔` |
| `research/manuscripts/aso_deposit_drift.py` | 1 | **1** | 149 `—⚠` |
| `research/modalities/emc_condensate_report.py` | 1 | 0 | 339 `—` |
| `research/modalities/atr_hrd_sarcoma_series.py` | 10 | 0 | 1349, 1397, 1412, 1419, 1424, 1428, 1446, 1468, 1479, 1481 (all `—`) |
| `research/modalities/single_slot_identity.py` | 3 | **1** | 415 `—`, 422 `—`, 425 `⛔` |
| `research/modalities/instrument_census.py` | **0** | 0 | — |
| `scripts/trigger_scan.py` | 5 | **1** | 452 `—` (`sys.stderr.write`), 834 `—`, 914 `—`, 919 `—`, 1083 `⚠` |
| `scripts/citation_debt.py` | **0** | 0 | — |
| `scripts/news_match.py` | 5 | 0 | 280, 318, 388, 420, 423 (all `—`) |

**16 of the 18 gates carry at least one non-ASCII print site; 52 sites; 15 cp1252-unencodable.** Only `instrument_census.py` and `citation_debt.py` are clean. **PRIMARY.**

**Other preflight-reachable or `--check`-bearing modules with sites (the remaining 143 of the 195), file:line:**

`research/manuscripts/aso_coverage_ladder.py` 1910 `★`, 1915 `⛔`, 1923 `—⛔`, 1933 `—⚠`, 1943 `§—⛔`, 1948 `—` · `aso_priorart_evidence.py` 132 `⛔` · `build_aixiv_metadata.py` 130 `—` · `build_submission_parts.py` 395/442/463 `—` · `emc_systems_map_check.py` 1364 `·` · `figures/aso_figure_provenance.py` 156 `—` · `figures/emc_fusion_frame_figure.py` 279 `—` · `journal_abbreviations.py` 160 `—` · `journal_reference_authors.py` 354 `—` · `line_citations.py` 552 `—⛔`, 558 `⚠`, 567/573 `—`, 688 `—⚠`, 691/694/697/700/702 `—`, 723 `—⛔`, 741 `·` · `lint_changed_prose.py` 270 `⚠`, 272 `⛔` · `lint_citations.py` 429/438/453/491/538 `—` · `lint_readability.py` 355 `—`, 359 `—⚠`, 383 `⛔`, 387 `⚠✅` · `lint_style.py` 494 `—` · `lint_submission_residue.py` 429/455/460/469/482 `—` · `tcf12_breakpoint_assignment.py` 368 `⭐` · `tests/test_the_manifest_hashes_were_taken_against_a_committed_tree.py` 131 `—⚠` · `venue_fee_screen.py` 250 `…`

`research/modalities/aso_delivery_antigen.py` 843 `—⛔` · `aso_gap_length_tradeoff.py` 891 `—`, 893 `·Δ` · `aso_genome_offtarget.py` 860/941/1435/1517/1656 `—` · `aso_noncoding_acceptor_designs.py` 568/807 `⚠` · `aso_noncoding_acceptor_screened_table.py` 500 `—` · `aso_per_junction_table.py` 413 `—` · `aso_taf15_intron2_designs.py` 207 `⚠` · `categorical_axis_audit.py` 1180 `—` · `emc_atr_vulnerability.py` 3174/3199/3214 `—` · `emc_expression_panels.py` 2878/2894 `—` · `emc_fet_frame_and_composition.py` 506 `—` · `emc_fourth_cohort_route_readout.py` 237/241 `—⛔`, 243 `—` · `emc_model_junction_evidence.py` 479 `—`, 488 `⭐` · `emc_mtap_prmt5_figures.py` 438 `—` · `emc_ret_cistrome.py` 2549/2594/2650/2657/2668/2699/2740/2749/2789 `⛔`, 2762 `⏱`, 2765/2995 `—⛔`, 3027 `—` · `emc_ret_target_scan.py` 1405/1407 `—` · `emc_sra_study.py` 878/920 `—`, 917 `⚠` · `fusion_cofold_recut.py` 528 `—` · `fusion_frame_trap.py` 970/1007 `—` · `fusion_junction_census.py` 677/733 `—⛔`, 695/740/743 `⛔`, 745 `✅` · `gse243553_eno3_overlap.py` 1655 `—` · `hgnc_index.py` 196 `⛔`, 198 `✅` · `hla_coverage.py` 426 `⛔`, 430 `⚠` · `junction_aso_thermo.py` 307 `—`, 453 `°Δ`, 457 `Δ` · `ndrg1_panel_attribution.py` 599 `—⛔`, 604 `⛔` · `nr4a3_fusion_targets_robustness.py` 345/424 `⛔` · `nr4a3_linker_library_canonical.py` 867 `—⛔`, 869 `⚠`, 874 `—` · `pgr_tissue_expression.py` 200 `—` · `pgr_transcript_fetch.py` 108/124 `—` · `realised_spend.py` 444 `—` · `scope_rung_cost.py` 315 `⛔`, 317 `✅`, 326 `—` · `steric_carrier_audit.py` 887/903 `⛔`, 890 `—✅` · `steric_design_rule.py` 367/384 `⛔`, 369 `✅` · `sufex_second_handle.py` 751 `⛔`, 758 `—⛔`, 760 `✅` · `tcf12_offtarget_tissue_expression.py` 265 `—`

`scripts/affected_tests.py` 382 `—⚠` · `scripts/fast_checks.py` 144 `—`, 155 `⚠` · `scripts/record_selector_validation.py` 26 `…` · `scripts/tier_budget.py` 144/151/161 `—`

`systems/parser_guard.py` 213 `·`, 221 `—` · `systems/systems_check.py` 4585 `·`

The remaining **836 sites in 242 files** are in modules with neither `--check` nor a preflight mention — overwhelmingly `research/modalities` GPU/fleet operations tooling (`nrv04_vast_launch.py` 55, `selcal_vast_launch.py` 50, `ternary_vast_launch.py` 34, `congeneric_fanout_vast.py` 33, `nr4a3_rbfe.py` 22, `scripts/aixiv_review.py` 20 …). Full machine-readable inventory at `/tmp/claude-0/w12c/print-sites.json` (1,031 records, each with file, line, kind, chars, codepoints, Unicode names). **PRIMARY.**

**Lower-bound caveat — stated as plainly as W12b stated its own.** This census is a **LOWER BOUND**, for four separate reasons, none of which I can eliminate statically:
1. Only **literal** non-ASCII is counted. `print(f"{label}")` where `label` is a module constant containing `⛔` is invisible to this scan; so is `print(TEMPLATE.format(...))`, `print("".join(parts))`, and any string built from `chr()`/`\N{}` escapes at runtime. Given how much of this tree formats status lines from constants, I expect this to be the largest missed class.
2. `print` reached through an alias, `functools.partial`, a logging shim, or `builtins.print` is not matched — only the bare `Name('print')` and `sys.stdout/stderr.write`.
3. `sys.stdout.writelines`, `traceback.print_exc()`, `argparse` help/usage text, and exception messages that reach stderr through the interpreter's own top-level handler are all uncounted, and all can carry non-ASCII from a docstring or a default.
4. `research/autonomy` and `.github/workflows` were out of scope per the dispatch, so anything there is uncounted.
Counting `print` sites is also **not** the same as counting *executions*: a site inside a rarely taken error branch costs nothing until that branch fires. **A site count is an upper bound on nothing and a lower bound on exposure.**

**Answer to (1): NO.** The stdout defect is not confined to five modules. It is a tree-wide property of this repository's console idiom — em dashes in prose lines, `⛔`/`⚠`/`✅`/`★` as severity markers — and it lands in **16 of the 18 preflight `--check` gate rows**.

### Part 2 — what `_generated_utc` costs

**PRIMARY.** `git ls-files`, non-`.py`, regex-matched on a real `"_generated_utc": "<value>"` pair: **38 tracked artifacts carry an embedded wall-clock stamp.** (66 tracked non-`.py` files contain the *string* `_generated_utc`; 28 of those are prose, workflow YAML, or report text and are excluded.)

**The intersection that is the actual defect: 9 of 38 (23.7 %) stamped artifacts have their current sha256 recorded verbatim in at least one tracked file.**

| stamped artifact | stamp value | hashing site(s) recording its current sha256 | gate-enforced? |
|---|---|---|---|
| `research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json` | `2026-08-28T00:14:14Z` | `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` | **YES** — 2 preflight rows |
| `research/modalities/aso-offtarget-tissue-expression.json` | `2026-08-15T13:58:56.716810+00:00` | same manifest | **YES** |
| `research/modalities/aso-offtarget-tissue-expression-inputs.json` | `2026-08-15T13:58:56.716810+00:00` | same manifest | **YES** |
| `research/modalities/noncoding-acceptor/pgr-offtarget-locus-expression.json` | `2026-08-15T15:13:57.395404+00:00` | same manifest | **YES** |
| `research/modalities/noncoding-acceptor/pgr-offtarget-locus-expression-inputs.json` | `2026-08-15T15:13:57.395404+00:00` | same manifest | **YES** |
| `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` | `2026-08-09T00:35:00Z` | `research/modalities/emc-scheduling-medians.json` | no (`emc_scheduling_medians.py --check` exists, not a preflight row) |
| `research/modalities/emc-expression-panels-inputs.json` | `2026-08-29T12:51:32+00:00` | 12 files: `research/modalities/expression-validation-readiness.json`, `research/modalities/surface-address-sensitivity.json`, 8 under `research/autonomy/cycle-outcomes/2026090{5T032612Z-df96afc413,5T084620Z-b7637a0999,5T111908Z-083a73575a}/`, 2 under `research/autonomy/follow-through-2026-09-05/` | no |
| `research/modalities/emc-fourth-cohort-quant.json` | `2026-09-02T17:42:53Z` | `research/modalities/expression-validation-readiness.json` + 3 `cycle-outcomes/20260905T111908Z-083a73575a/` files | no |
| `research/modalities/emc-fourth-cohort-quant-inputs.json` | `2026-09-02T17:42:52Z` | same 4 | no |

The **29 stamped artifacts with no recorded digest anywhere** — `health.json`, `S21-UNSCORED-proposals.json`, `S43-proposed-graph-additions.json`, the two 2026-08-10 `research/literature/` JSONs, `emc-endpoint-alternatives.json`, `emc-endpoint-discordance.json`, `alarm-state.json`, `cys-chemoproteomics-precheck.json`, `emc-cohort-search-inputs.json`, `emc-data-level-sweep{,-inputs}.json`, `emc-fusion-read-scan{,-inputs,-deposits}.json`, `emc-hypoxia-null-background.json`, `emc-hypoxia-therapeutic-status.json`, `emc-ret-cistrome-inputs.json`, `emc-sra-study{,-inputs}.json`, `nr4a3-fusion-targets-inputs.json`, `nr4a3-nuccore-sweep{,-inputs}.json`, `nr4a3-thiol-environment.json`, `panagopoulos-elink-probe.json`, `pgr-tissue-expression-inputs.json`, `step1-fanout-progress.json`, `tcf12-offtarget-tissue-expression-inputs.json`, `work-ledger.json` — carry the stamp at **no provenance cost**, because nothing hashes them. For those the stamp is free and the design question is purely the owner's taste. **PRIMARY.** (Two of them, `emc-endpoint-alternatives.json` and `emc-endpoint-discordance.json`, are in W12b's never-re-deriving eight — so they cost a false `--check` failure but **not** a broken provenance record.)

**The sharpest instance, quantified.** `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json` records `{path, sha256}` for **516** tracked paths; all 5 stamped entries currently **match** their recorded digest (verified by recomputing sha256 of current bytes — `ad449441…`, `1768a0d3…`, `323d8a22…`, `d7dddb96…`, `06fe6f02…`). That manifest is consumed by **two** rows of the preflight re-derivation gate:

```
scripts/preflight.sh:856   research/manuscripts/aso_archive_manifest.py|archive manifest|--check-archive
scripts/preflight.sh:857   research/manuscripts/aso_deposit_drift.py|declared deposit drift|--check
```

and `aso_deposit_drift.py:76,96` reads exactly `{f["path"]: f["sha256"] for f in …["files"]}` and diffs it against the manifest at an earlier git revision.

**So the cost, stated exactly:** for those **5 of 516 deposited paths (0.97 %)**, `sha256` no longer answers "did the science change?" — it answers "was this file regenerated?". Re-running the generator with **no input and no code change** rewrites `_generated_utc`, changes the file's sha256, makes the archive manifest stale, and turns both preflight rows red; `aso_deposit_drift.py` then prints a "paths changed" count that includes a path whose content is identical. Conversely a stale stamp cannot distinguish "unchanged" from "not regenerated". This is the same class the gate block's own comment at `scripts/preflight.sh:748-758` already names for `git_revision` — where the repository's chosen remedy was a narrower comparison mode (`--check-archive`), **not** removal of the field. **PRIMARY.**

**Relation to W12b's eight.** Of W12b's 8 never-re-deriving artifacts, **4** are `_generated_utc`-stamped: `emc-endpoint-alternatives.json`, `emc-endpoint-discordance.json`, `emc-systemic-therapy-pooling.json`, `emc-fusion-partner-pooling.json` — all four with equal produced/committed byte counts (96,266 / 18,248 / 79,198 / 113,032), which is consistent with a fixed-width ISO stamp being the only differing field, as W12b's quoted diff shows. The other 4 are a **different** stamp mechanism and I flag that rather than fold it in: `fusion-junction-aso-archive-manifest.json` and `fusion-junction-aso-preprint-checklist.md` differ by 5,778 B and 1,732 B under W12b's own recorded `.git`-less-scratch blocker (verdict N/A, not a stamp finding); the two `.docx` (`…figure-legends.docx`, `…title-page.docx`) are equal-size and carry ZIP member mtimes, which is a third stamp mechanism entirely. `_generated_utc` explains **4 of 8**, not 8 of 8. **PRIMARY / one row UNKNOWN as W12b left it.**

---

## Validation evidence

Environment for every RUN below: Python 3.11.15, Linux 6.18.44-fc-v24, cwd `/home/user/Rare-cancers` (read-only) or `/tmp/claude-0/w12c/`, no network.

**V1 — RUN. HEAD at start and end, tree untouched (exit 0).**
```
$ git rev-parse HEAD                     # start
47aac85f874a57a6f981c3432abcf16980968aec
$ git rev-parse HEAD                     # end
7d081218f107363573573e6d102e4334567adf77
$ git status --porcelain | wc -l
0
$ git diff --name-only 47aac85..7d08121 | grep -E '\.py$|^scripts/|^systems/|^research/manuscripts/|^research/modalities/' | wc -l
0
```

**V2 — RUN. AST census (exit 0).**
```
$ python3 /tmp/claude-0/w12c/scan_print.py
files_scanned 1359 unparsed 0 sites 1031
```

**V3 — RUN. The mechanism, reproduced under an ASCII stdout (exit 0).**
```
$ LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0 /tmp/claude-0/w12c/pr.py
enc ascii ANSI_X3.4-1968
PRINT FAILED U+2014 EM DASH: UnicodeEncodeError: 'ascii' codec can't encode character '\u2014' in position 3: ordinal not in range(128)
PRINT FAILED U+26D4 NO ENTRY: UnicodeEncodeError: 'ascii' codec can't encode character '\u26d4' in position 3: ordinal not in range(128)
PRINT FAILED U+00B7 MIDDLE DOT: UnicodeEncodeError: 'ascii' codec can't encode character '\xb7' in position 3: ordinal not in range(128)
```
Note the interpreter's own `-c` handler failed on the same input before I moved the probe to a file — `Unable to decode the command from the command line: UnicodeEncodeError: 'utf-8' codec can't encode characters in position 113-115: surrogates not allowed`, exit 1 — which is the same defect one layer up.

**V4 — RUN. Both candidate remedies confirmed to work (exit 0 each).**
```
$ LC_ALL=C LANG=C PYTHONUTF8=1 python3 /tmp/claude-0/w12c/pr.py
enc utf-8 utf-8
ok — U+2014 EM DASH / ok ⛔ U+26D4 NO ENTRY / ok · U+00B7 MIDDLE DOT
$ LC_ALL=C LANG=C PYTHONUTF8=0 PYTHONIOENCODING=utf-8 python3 -X utf8=0 /tmp/claude-0/w12c/pr.py
enc utf-8 ANSI_X3.4-1968
ok — U+2014 EM DASH / ok ⛔ U+26D4 NO ENTRY / ok · U+00B7 MIDDLE DOT
```
`PYTHONIOENCODING=utf-8` fixes stdout while leaving `getpreferredencoding` hostile — i.e. it repairs this defect **without** masking W12's file-I/O defect. That property matters for the routing below.

**V5 — RUN. Guard absence (exit 0, hits confined to W12's report).**
```
$ grep -rn "PYTHONIOENCODING\|PYTHONUTF8\|stdout.reconfigure\|getpreferredencoding" --include=* . | grep -v '^\./\.git' | head
./research/autonomy/opus-capacity-campaign-20260908/reports/W12-windows-portability-defects.md:123 …
(all 10 hits are inside that one report file)
```

**V6 — RUN. Stamped-artifact enumeration (exit 0).** `tracked non-.py files with a real embedded _generated_utc VALUE: 38`, list quoted in Result.

**V7 — RUN. Exact-digest provenance intersection (exit 0).**
```
covered: 9 of 38
```
Full per-artifact output quoted in Result.

**V8 — RUN. ASO archive manifest verification (exit 0).**
```
manifest n_files: 516 entries: 516
STAMPED artifacts hashed by the ASO archive manifest: 5
  … match=True  (×5)
all match: 5 / 5
fraction of manifest entries that carry a wall-clock stamp: 5 / 516
```

**V9 — RUN. Preflight gate-row extraction (exit 0).** `scripts/preflight.sh:849-866` read verbatim; 18 rows transcribed into the table above.

**PROPOSED (NOT RUN):**
- I applied **no repair**, ran **no generator**, and ran **no `--check`**. All Part 1 evidence is static AST plus an isolated three-line locale probe; the claim "these gates would fail on a cp1252 console" is a **PREDICTION**, since I have no Windows host. Only the *mechanism* (a non-ASCII literal cannot reach a non-UTF-8 stdout) is reproduced.
- `scripts/preflight.sh` was **not** run, per dispatch.
- I did **not** verify that each listed print site is actually on the `--check` code path of its module. Site-in-module is measured; site-on-check-path is not. For the five W12b modules that question is already answered empirically by W12b's 215 runs; for the other 70 it is **UNKNOWN**.
- I did **not** regenerate any artifact, so I did not independently confirm that removing/freezing `_generated_utc` would make the 4 endpoint artifacts re-derive. That is W12b's measurement, not mine.

---

## Routing — findings only, no repair applied

**All of the following is PROPOSED (NOT RUN) and requires write authority this lane does not have.** I have not applied, staged, or tested any of it. Per the constraints I have **not** weakened or reordered any `--check` comparison and I propose **no** removal of any timestamp from any artifact.

**Finding A — the stdout repair must be process-wide, not five-module.** W12b's proposed `sys.stdout/sys.stderr.reconfigure(encoding="utf-8")` in five entry points is correct and insufficient: it leaves 1,008 of 1,031 sites, and 14 of the 16 affected preflight gate rows, unrepaired. Two candidate shapes, both verified working in V4, both for the owner to choose between:

- *Environment form, one line, covers every gate row at once.* In `scripts/preflight.sh`, beside the existing `PYTHONPYCACHEPREFIX` export (currently `scripts/preflight.sh:~103`):
  ```bash
  # Every gate below prints non-ASCII status markers (— ⛔ ⚠ ✅ …) that a locale-encoded
  # stdout cannot hold. Measured 2026-09-08: 52 such sites across 16 of the 18 --check rows.
  # This does NOT mask the file-I/O defect: getpreferredencoding() is left alone deliberately.
  export PYTHONIOENCODING=utf-8
  ```
  Tradeoff, stated: it repairs only runs that go through preflight. A direct `python3 research/manuscripts/submission_metrics.py --check` on a Windows console still fails.
- *Source form, per entry point, covers direct invocation too.* At the top of each `if __name__ == "__main__":` block:
  ```python
  for _s in (sys.stdout, sys.stderr):
      if hasattr(_s, "reconfigure"):
          _s.reconfigure(encoding="utf-8", errors="replace")
  ```
  Tradeoff: 75+ edit sites, and `errors="replace"` silently mangles output rather than failing — which this repository's own gate-design comments would likely object to; `errors="strict"` keeps the failure loud but then only fixes the encodable subset. This is a real design choice, not a mechanical one.

The two are complementary, not alternatives. **Owner's call; I am not making it.**

**Finding B — W12b's proposed locale guard should assert on stdout as well as on `open()`.** As W12b already noted at its line 421, the guard W12 drafted would have passed all five STILL-BROKEN modules. My census says the guard's blast radius if written against `open()` alone is 1,031 uncovered sites. Any new guard is itself a `--check`-shaped addition and belongs to the writer who owns the repair, not to me.

**Finding C — `_generated_utc` × provenance hashing.** The five manifest-hashed, stamped paths are the only ones where a gate is affected. **I propose no removal.** The repository has already solved this exact shape once, for `git_revision`, by adding a *narrower comparison mode* rather than deleting the field (`--check-archive`, documented at `scripts/preflight.sh:748-758`). If the owner wants the same treatment here, the smallest shape consistent with that precedent is a manifest-side note recording *which* entries carry a wall-clock stamp, so a reader knows a digest change on those five paths is not necessarily a content change. **Deciding whether the stamps stay is the owner's design decision and I have not pre-empted it.**

---

## Limitations

- **The site inventory is a LOWER BOUND**, for the four reasons enumerated in Result: literal-only detection (f-string interpolation of a non-ASCII constant is invisible), no alias/partial/shim resolution, no `writelines`/`traceback`/argparse-help coverage, and `research/autonomy` + `.github/workflows` out of scope. I expect the true site count to exceed 1,031, and I cannot bound by how much.
- **A site count is not an execution count.** Many `⛔` sites sit in error branches that never fire on a green run. I did not attempt reachability analysis, and I did not verify that any listed site lies on its module's `--check` path. That is measured only for W12b's five.
- **No Windows host.** Every per-codepage outcome is a PREDICTION. The reproduction is on Linux under a forced ASCII locale, which is strictly more hostile than cp1252 — so my `cp1252-unencodable` column is the honest severity axis, and the `cp1252-ok` sites are *not* demonstrated to fail on a modern Windows console.
- **`errors=` behaviour untested at scale.** V4 shows `PYTHONIOENCODING=utf-8` works on a three-line probe. I did not run it against any real generator, so I cannot claim it leaves the 22 artifacts W12b hashed unchanged.
- **The provenance intersection is exact-digest, which cuts both ways.** A file whose recorded digest is already *stale* (recorded before a regeneration) would not match my search and would be counted as "not hashed anywhere". So 9-of-38 is the count of artifacts with a *currently valid* recorded digest; artifacts with a *broken* recorded digest are undercounted, and 9 is therefore itself a lower bound on the affected set.
- **HEAD moved mid-run** (`47aac85` → `7d08121`). I verified no scanned file differs between them, but the campaign's declared frozen commit `92abbcb905…` was already not this checkout's HEAD when I started.
- **This is a reproducibility and tooling finding only.** No EMC scientific conclusion is changed, questioned or supported by it. No clinical claim is made. No patient data, accession, citation or measurement was created or consulted. Nothing here bears on efficacy, safety, selectivity or clinical readiness.

---

## Stop condition

**Set:** (a) a complete non-ASCII-print site inventory with file:line and a stated lower-bound caveat, and (b) a quantified `_generated_utc` × provenance-hashing intersection naming the affected artifacts and the hashing sites.

**MET.** (a) 1,031 sites across 317 files, 0 unparsed of 1,359 scanned, classified by character (44 distinct, 31 cp1252-unencodable), by cp1252 encodability (323 unencodable sites), by `--check` presence and by preflight reachability; full file:line given for all 195 sites in the 75 gate-relevant modules, machine-readable full set at `/tmp/claude-0/w12c/print-sites.json`; lower-bound caveat stated with its four specific causes. **The answer to (1) is NO — 16 of the 18 preflight `--check` gate rows are affected, not 5 modules.** (b) 38 stamped artifacts enumerated; **9** have a currently valid sha256 recorded in a tracked file; **5** of those are inside the 516-entry ASO archive manifest that two preflight rows consume (`scripts/preflight.sh:856,857`), giving the quantified cost **5 of 516 deposited paths (0.97 %)** on which sha256 answers "was this regenerated?" rather than "did the content change?"; all hashing sites named. No repair applied; no `--check` comparison weakened or reordered; no timestamp removed.

---

## Tool-call and wall-clock count actually used

**20 tool calls** (all Bash; no Read/Edit/Write against the repository, no network, no subagents). **Wall clock: 02:30:44Z → 02:34:58Z for all measurement = 4 min 14 s**, plus report drafting — comfortably inside the ~40 min / ~40 call target.

---

## Next concrete action

**One successor for this lane:** *Determine, for each of the 52 non-ASCII print sites inside the 18 preflight `--check` gate rows, whether the site is actually on the `--check` code path* — by running each gate's `--check` under `LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0` in a scratch copy and recording which of the 16 affected gates actually raise, versus which merely contain a site in an untaken branch. That converts my static 16-of-18 upper bound into a measured count, and it is the one number the writer applying the repair needs to size it: if only 4 of 16 fire, the environment-form one-liner is enough; if 14 fire, the source form is unavoidable. It is read-only, needs no write authority, and reuses W12b's existing three-config harness at `/tmp/claude-0/w12b/run_checks.py` unchanged.

The repair itself is **not** a successor for this lane: it needs write authority and a proper writer worktree, exactly as W12b concluded, and Finding A above shows its scope is now larger than W12b's five modules.
