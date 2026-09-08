<!-- collected 2026-09-08T03:38:26Z by campaign coordinator; agent id aa00660e2628c4bba; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aa00660e2628c4bba.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W27b** · OPUS-CAPACITY-CAMPAIGN-20260908 · tooling audit lane, named successor to W27.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in this container's environment names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 03:25:31 UTC 2026` · **end**: `Tue Sep  8 03:33:00 UTC 2026` (report drafting after).

`git rev-parse HEAD` **start**: `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f` · **end**: `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1`. **HEAD moved under me** (the coordinator collecting eight other workers' reports). I checked the exposure rather than assuming it: `git diff --name-only ff6bb01..215ed8e -- research/modalities research/manuscripts` returns **0 files**. No module or artifact I measured changed during this run.

`git status --porcelain` **start**: `0` lines. **end**: `0` lines. I wrote nothing into the Git tree and ran no git write operation. All execution under `/tmp/claude-0/w27b/` with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPYCACHEPREFIX=/tmp/claude-0/w27b/pyc`. I did not run `scripts/preflight.sh`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (the four long proxy variables — `no_proxy`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are verbatim in the transcript, contain no model information, and are marked below; nothing else is altered):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=<proxy list, no model information>
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
GLOBAL_AGENT_NO_PROXY=<proxy list, no model information>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<truststore + proxy flags, no model information>
NO_PROXY=<proxy list, no model information>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<proxy list, no model information>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

---

## Stop condition (set before any measurement)

**Stop when: (1) every module under `research/modalities` and `research/manuscripts` that declares or dispatches on `--check` carries a class assigned from its own source, with W27's Class D and Class E emptied; (2) every newly found Class A or Class B module has its published set and compared set given with `file:line`, in both directions, for every case where I actually enumerated the artifact's keys, and is marked UNKNOWN where I did not; (3) at least two newly found gaps are demonstrated by mutating the committed artifact on the scratch copy and recording the module's own real `--check` exit code, restoring between demonstrations and verifying the scratch restored at the end; (4) the completed totals are stated so W27's lower bound of 10 becomes an actual number; (5) no repair is authored, no ceiling proposed, no guard weakened.**

**MET.** All five. (3) exceeded — three demonstrations, all real exit 0. Returning immediately.

---

## Question

W27 classified 52 of ~130 `--check` modules and left **78 unresolved**: 22 Class D (`return check()` — delegation it did not follow) and 56 Class E (its regex extractor did not resolve them). W27's Class A+B count of 10 was therefore an explicit **lower bound**, and the owner cannot choose between Option 1 (repair in place, 0 test functions) and Option 2 (static meta-guard, 2 of 3 remaining `commit-loop` slots) because Option 2's allowlist cannot be written until D and E are resolved.

**Question pursued: for every module that declares or dispatches on `--check`, what does that `--check` actually compare against the module's own committed artifact — and what is the completed total of modules whose gate is narrower than "the whole document"?**

---

## Prior-work check

| Command / read | What it showed |
|---|---|
| Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, `reports/W20g-published-denominator-consistency.md`, `reports/W27-drift-gate-hash-census.md` | W27 is my direct predecessor and named this task. I do **not** re-derive its Class A/B findings from scratch; I reuse them, and I **correct two** of them below where source disagrees. W20g's `662/77/211,362` denominator work is not replayed. |
| `grep -n -m3 -A6 "^## Question" reports/W14e-fake-guard-triage.md` (appeared in the tree during my run) | W14e/W14b measure a **different axis**: `--check` paths that *write*, and their *reachability*. My census measures what `--check` *compares*. Overlap is one module name. **My `nr4a3_linker_library_canonical.py` write finding is offered as confirmation on their axis, not as novelty** — a self-writing `--check` is exactly the class W14b enumerated. |
| `git ls-files` + AST walk of every `.py` under `research/modalities`, `research/manuscripts` | 139 files mention `--check`; **129** declare it via `add_argument("--check")` or dispatch on `"--check" in sys.argv` / `args.check`. W27 reported 130; the ±1 is a boundary-rule difference I cannot reconcile without W27's list, which its report does not publish. **I report my own enumeration and its rule.** |

**CLOSED-WORK items confirmed not replayed**: no NR4A Perspective, no Brenca/Hofvander/Pazopanib/Sunitinib/Wagner/CTARC route, no GSE4303/GSE28866 re-reading, no registry ICD-O work, no source fetch, no patient or specimen work. **No network request was initiated by me.** No module I ran attempted egress (I deliberately avoided `emc_sra_study.py --check`, which imports `urllib.request` and would fetch if its cache were cold — that outcome is **UNKNOWN**, not tested). No content-policy refusal was encountered. The frozen corpus at `/tmp/claude-0/frozen-corpus/` was not needed: every claim is about code at the recorded live HEADs, anchored to `file:line`.

---

## Method / inputs

**Inputs.** All 129 modules under `research/modalities` and `research/manuscripts` (non-test `.py`) that declare or dispatch on `--check`, plus their committed JSON artifacts.

**Tools.** Python 3.11 stdlib only (`ast`, `json`, `re`, `os`, `subprocess`, `shutil`), `git`, `grep`, `tar`, `diff`, `cmp`. No third-party package, no network, no GPU, no paid API.

**Extraction (this is where I differ from W27, and it is why D and E emptied).** W27's extractor matched idioms textually. Mine is AST-based, in `/tmp/claude-0/w27b/`:
- `scan.py` → the 139/129 enumeration.
- `resolve.py` / `resolve2.py` → for each module, locate every `ast.If` whose test mentions the check flag; take the **positive branch** for `if args.check:` and the **remainder of the enclosing function** for the inverted `if not args.check: return` guard; then follow local function calls transitively (depth ≤ 8) so `return check()` resolves to the `check()` body. This is what emptied Class D.
- `dump.py` → per module, print every line inside the check span matching `==`, `!=`, `assert`, `drift`, `mismatch`, `differ`, `sha256`, `return 1`, `sys.exit(1)`, `raise`. **I read all 129 of these extracts.** For the 22 delegating modules and every ambiguous residual I additionally read the `check()` body itself with `deleg.py` and, for 19 modules, read the full source range with `sed`.

**Classification rule, stated so it can be checked.** For each module, what does `--check` compare **against the module's own committed artifact**?
- **C** — the whole committed document, against a fresh derivation (an explicitly named volatile field such as `_generated_utc` may be stripped).
- **B** — a proper subset of it.
- **A** — nothing of it: the check never opens the committed artifact, or opens it only to print it back.
- **F** — not a publish-vs-gate comparison at all: unit self-tests over functions, or a linter over prose. For the owner's purposes F behaves like A (the committed artifact is ungated) but the repair is different, so I keep it separate rather than inflating A.

**Write-hazard inspection in source BEFORE running anything — required by the dispatch, done for every module I ran.**

| Module | What I read in source | Ran? |
|---|---|---|
| `realised_spend.py` | `--check` branch is `:437-439`: `print(json.dumps(drift(doc))); return 0`. The only `open(...,"w")` is `:441`, inside the `--write` branch, after the check returns. `drift()`/`summary()` read only. | **RAN** (scratch) |
| `ternary_rebuild_cost.py` | `--check` branch `:472-482` returns; the only write is `:484`, after it. `derive()` reads committed CI records. | **RAN** (scratch) |
| `nr4a3_fusion_targets.py` | with `--check` (no `--fetch`) the `INPUTS` write at `:2047-2048` is inside the `if a.fetch:` branch (`:2046`); the `OUT` write at `:2073` is after the check block returns at `:2066-2071`. | **RAN** (scratch) |
| **`emc_fourth_cohort_quant.py`** | `:928` calls `derive()` unconditionally, which writes both TSVs. **W27's refusal confirmed.** | **NOT RUN — `PROPOSED (NOT RUN)`** |
| **`nr4a3_linker_library_canonical.py`** | **A SECOND WRITING `--check`, not previously named in this campaign's gate census.** `main()` writes `args.out` unconditionally at `:851-852` (`json.dump(doc, fh, ...)`); the `--check` branch is at `:873-876`, *after* the write, and the run prints `"[canon] wrote %s"` even under `--check`. | **NOT RUN — refused by the same rule that protected `emc_fourth_cohort_quant.py`** |
| `emc_sra_study.py` | check body `:907-921` compares and returns before any write, **but** the module imports `urllib.request` and fetches when its cache is cold (`:162-179`). Running it risks egress I was told not to initiate. | **NOT RUN — deliberate; its class is a source finding** |
| all other Class A/B modules | not run; their classes are source findings only | not run |

**Scratch copy.** `tar -cf - --exclude=./.git . | (cd /tmp/claude-0/w27b/scratch && tar -xf -)` → **612 MB**. Every `--check` executed with `cwd=/tmp/claude-0/w27b/scratch`, never in `/home/user/Rare-cancers`. Each artifact restored from the live tree before and after each mutation.

---

## Result

### R1 — The completed 129-module census (`PRIMARY`)

| Class | n | Share | What `--check` compares against the committed artifact |
|---|---|---|---|
| **C — the whole document** | **90** | 69.8 % | `cur != new`, `json.load(OUT) != out`, or every top-level key; volatile stamp may be stripped. Published set = gated set at top level. |
| **B — a proper subset** | **22** | 17.1 % | A hand-listed key subset, a provenance stamp, or an internal self-consistency relation. |
| **A — nothing of it** | **11** | 8.5 % | Never opens the committed artifact, or opens it only to print it back. |
| **F — not a publish/gate comparison** | **6** | 4.7 % | Unit self-tests over functions, or a prose linter. The committed artifact is ungated, but the repair is different from A. |
| **D (W27) — unresolved delegation** | **0** | — | **emptied** |
| **E (W27) — unresolved by extractor** | **0** | — | **emptied** |

**The number the owner asked for. W27's lower bound of 10 becomes 33** on W27's own definition (A + B = 11 + 22), or **39 of 129 (30.2 %)** if Class F is counted, since F's committed artifacts are equally ungated. **Ninety modules — 69.8 % — are complete at the top level and need nothing.** W27's central reading survives contact with the other 78: the whole-document idiom is the dominant one, and the gap class is a minority. It is **3.3× larger** than W27 could see.

**Two corrections to W27, from source.**
1. W27 listed six Class A modules; five re-confirm. `nat_scope_census.py:349-371` and `venue_fee_screen.py:323-339` do contain a `return 1` (`:355`, `:328`) — but only for a **missing file**. No content of either artifact is compared. Class A stands; the "returns 0 unconditionally" wording does not.
2. W27's Class B entries `gse11185_wt_vs_fusion.py` and `nurr1_allosteric_vs_pocket5.py` **do** exit non-zero on their narrow comparison: `gse11185_wt_vs_fusion.py:920` and `nurr1_allosteric_vs_pocket5.py:769` are both `return 0 if same else 1`. They are genuinely Class B (a real gate over 2 keys and 1 key respectively), not gates that cannot fail. W27 did not claim otherwise; I record it because my own first automated pass mis-flagged them and I do not want that error propagating.

### R2 — Class A, completed: 11 modules whose `--check` gates nothing of their committed artifact (`PRIMARY`)

Five newly found; six from W27, re-confirmed in source.

| # | Module and gate `file:line` | What the check does | Status |
|---|---|---|---|
| 1 | `research/modalities/nr4a3_acceptor_numbering.py:147-155` | opens its own output, prints four fields, `return 0` | W27, re-confirmed |
| 2 | `research/manuscripts/venue_fee_screen.py:326-332` | opens the artifact, prints every verdict, `return 0` (`:328` `return 1` = file missing only) | W27, re-confirmed |
| 3 | `research/manuscripts/nat_scope_census.py:353-361` | opens the artifact, prints counts, `return 0` (`:355` = file missing only) | W27, re-confirmed |
| 4 | `research/modalities/gse243553_eno3_overlap.py:1678-1686` | opens `RECON_OUT`, prints four keys, `return 0` | W27, re-confirmed |
| 5 | `research/modalities/emc_prior_art_fulltext_screen.py:127-128` | recomputes, prints `out["counts"]`, `return 0`; never opens the committed artifact | W27, re-confirmed |
| 6 | `research/modalities/emc_tissue_read_statistics.py:426-428` | recomputes, prints one summary line, `return 0`; never opens the committed artifact | W27, re-confirmed |
| **7** | **`research/modalities/realised_spend.py:437-439`** | `print(json.dumps(drift(doc), indent=1)); return 0` — it computes a drift report **and returns 0 whatever it says**. A `--check` whose entire output is a drift report it then ignores. | **NEW — demonstrated, D1** |
| **8** | **`research/modalities/ternary_rebuild_cost.py:472-482`** | re-derives and checks the **derived** doc's internal sums (`ok = rec["sums"] and doc["derived_cost"]["reference_gpu_h"] == 0.0`); never opens `ternary-rebuild-cost.json` | **NEW — demonstrated, D2** |
| **9** | **`research/modalities/fusion_cofold_recut.py:525-526`** | `return 0 if ok else 1` where `ok` comes from `build_all()` at `:517`; the committed `fusion-cofold-constructs.json` is never read | **NEW** |
| **10** | **`research/modalities/km_risk_row_detect.py:869-871`** | `--check` = "synthetic controls only" (`:866` help text); runs `run_control()` and returns on its verdict; `km-risk-row-detection.json` is never read | **NEW** |
| **11** | **`research/modalities/nr4a3_linker_library_canonical.py:873-876`** | refuses only on `n_DEAD_anchors`; the committed artifact is never compared — **and `:851-852` writes it before the check branch is reached** | **NEW — and NOT RUN, it writes** |

Modules 8-11 are a shape W27's six did not include and which its Class A wording would have missed: they *can* fail, so they do not look inert, but what they gate is a freshly derived object or a synthetic control — **never the file in Git**.

### R3 — Class A: published set vs compared set, both sides, both directions (`PRIMARY`)

For the five new Class A modules I enumerated the committed artifact's top-level keys and their line numbers. The compared set is ∅ in every case, so **the gated-but-not-published direction is trivially empty** for all five — no key is compared that the artifact lacks, because no key is compared.

| Module (gate `file:line`) | Committed artifact | Published set — every top-level key, `file:line` | Compared set |
|---|---|---|---|
| `realised_spend.py:437-439` | `research/modalities/realised-spend.json` | **17 of 17 ungated**: `_what`:2, `_generated_by`:3, `_as_of_utc`:4, `_as_of_et`:5, `realised_usd_ledgered`:6, `realised_usd_ledgered_meaning`:7, `lanes`:8, `unreadable_lanes`:37, `attested_unledgered_usd`:38, `attested_unledgered_meaning`:39, `attested_unledgered`:40, `realised_usd_best_estimate`:82, `realised_usd_best_estimate_meaning`:83, `free_credit_separate_ledger`:84, `free_credit_note`:104, `mirrors_deliberately_not_summed`:105, `ladder_total_is_elsewhere`:117 | **∅** |
| `ternary_rebuild_cost.py:472-482` | `research/modalities/ternary-rebuild-cost.json` | **14 of 14 ungated**: `_what`:2, `_status`:3, `serves`:4, `spec`:24, `gate`:98, `scope`:136, `measured_basis`:156, `unit_seconds`:199, `basis_reconciliation`:205, `units`:213, `derived_wall_clock`:228, `derived_cost`:235, `unpriced`:257, `_provenance`:261 | **∅** |
| `fusion_cofold_recut.py:525-526` | `research/modalities/fusion-cofold-constructs.json` (path at `fusion_cofold_recut.py:63`) | **17 of 17 ungated**: `_title`:2, `_owner`:3, `_cost`:4, `_serves`:5, `_scope`:6, `⛔_PRE_REGISTERED_GATE_FOR_THE_RUN_THIS_PREPARES`:7, `why_a_recut_was_owed`:8, `⛔_the_cut_is_not_single_valued`:9, `seed_plan`:10, `ews_seam_len`:23, `dollar_ceiling`:24, `launch_path_check`:40, `gate`:93, `objects`:470, `yaml_written`:574, `map_edits_required`:580, `refusals`:614 | **∅** |
| `km_risk_row_detect.py:869-871` | `research/modalities/km-risk-row-detection.json` (path at `km_risk_row_detect.py:82`) | **10 of 10 ungated**: `_generated_by`:2, `_what`:3, `_not_medical_advice`:4, `⛔_this_is_an_admissibility_reading_not_a_digitization`:5, `method`:6, `⛔_the_figures_are_not_committed`:23, `inputs`:24, `control`:30, `sources`:109, `_totals`:1822 | **∅** |
| `nr4a3_linker_library_canonical.py:873-876` | `nr4a3-linker-library-canonical` output at `args.out` | key/line enumeration **NOT PERFORMED** — I refused to run or resolve this module's output path further once I found the unconditional write at `:851-852`. **UNKNOWN**, not zero. | **∅** |

### R4 — Class B, completed: 22 modules that compare a proper subset (`PRIMARY`)

W27's four, plus 18 newly resolved. The four **fully quantified** new ones (published keys with `file:line`, both directions) are first.

**B5 · `research/modalities/emc_sra_study.py` — gate at `:913-915`** (NEW)
- Compared (3), `emc_sra_study.py:913`: `verdict`, `resolved`, `transport_gate_passed`.
- **Published-but-not-gated: 8 of 11 top-level keys**, with `research/modalities/emc-sra-study.json:line`: `_generated_utc`:2, `_inputs_generated_utc`:3, `_question`:4, `target_bioproject`:5, `target_sra_study`:6, `transport_controls`:7, **`targets`:46**, `pairing_check`:882.
- **Gated-but-not-published: none** — all 3 compared keys exist in the artifact.

**B6 · `research/modalities/nr4a3_fusion_targets.py` — gate at `:2064-2065`** (NEW)
- Compared (3), `nr4a3_fusion_targets.py:2064`: `controls`, `set_scores`, `circularity_reading`.
- **Published-but-not-gated: 15 of 18 top-level keys**, with `research/modalities/nr4a3-fusion-targets.json:line`: `_framing`:2, `_language_discipline`:3, `_limits`:4, `_the_rule_that_governs_every_row`:13, `_the_second_rule`:14, `_what`:15, `_what_this_cannot_conclude`:16, **`evidence_table`:281**, **`gene_reads`:715**, `generated_utc`:33006, `platforms`:33007, `pparg_arms`:33167, **`reads`:34458**, `series_records`:34720, `set_definitions`:34814.
- **Gated-but-not-published: none.**
- The ungated set is the bulk of a 34,000-line artifact — every read, every per-gene score row — while the gate covers three summary blocks. Demonstrated as **D3**.

**B7 · `research/modalities/fusion_frame_trap.py` — gate at `:992-1003`** (NEW)
- Compared: 8 named top-level keys (`fusion_frame_trap.py:992-993`: `counts`, `counts_by_fusion`, `both_conditions_hold`, `indeterminate`, `n_fusions_in_catalogue`, `n_junctions_graded`, `architecture_survey`, `exposure_sweep`), plus the **order** of `fusions` by `id::junction` (`:999`) and each fusion's `verdict` (`:1002`).
- **Published-but-not-gated: every field of every `fusions[]` row other than `id`, `junction` and `verdict`.** Artifact top-level key/line enumeration **NOT PERFORMED** — `OUT` (`fusion_frame_trap.py:88`) does not resolve to a file I located (`research/modalities/fusion-frame-trap.json` is absent; only `fusion-frame-trap-breakpoints.json` and `-inputs.json` exist). The subset structure is `PRIMARY` from source; the artifact-side line numbers are **UNKNOWN**, and I will not invent them.

**B8 · `research/modalities/emc_mtap_prmt5_figures.py` — gate at `:430-437`** (NEW)
- Compared: the `sources` map of `mtap-prmt5-figure-provenance.json` (path at `:46`) against `_fingerprint()`. That is a check on the figures' **inputs**.
- **Published-but-not-gated: the figure files themselves.** A redrawn or corrupted figure whose inputs are unchanged is not drift here.

**The remaining 14 Class B modules**, resolved from source. For these I read the comparison and quote it; I did **not** enumerate each artifact's key lines, so their published-side line numbers are honestly **UNKNOWN** rather than asserted.

| Module and gate `file:line` | Compared | Published-but-not-gated |
|---|---|---|
| `research/modalities/emc_fourth_cohort_quant.py:940-942` | 5 keys | 22 of 27 (W20g/W27, quantified there) |
| `research/modalities/aso_delivery_antigen.py:838-840` | `per_antigen`, `headline` | 16 of 18 (W27) |
| `research/modalities/gse11185_wt_vs_fusion.py:917-920` | 2 `verdict` subkeys | 11 of 12 top-level (W27) |
| `research/modalities/nurr1_allosteric_vs_pocket5.py:766-769` | `verdict.answer` | 17 of 18 (W27) |
| `research/modalities/nr4a3_fusion_targets_figures.py:504-512` | stamped source fingerprints | the figures themselves |
| `research/manuscripts/figures/aso_figure_provenance.py:160-171` | `sources` map only | the figures themselves |
| `research/manuscripts/figures/emc_fusion_frame_figure.py:278-280` | `have != stamp()` — the stamp only | the figure |
| `research/manuscripts/figures/svg_to_print_formats.py:449-455` | per-stem `source_pdf_sha256` only | the PDF/PNG deliverables' own bytes |
| `research/modalities/pgr_transcript_fetch.py:96-111` | symbol presence + 4 recorded `self_checks` booleans **read out of the artifact itself** | every sequence the artifact publishes (cDNA, CDS, protein, exons) |
| `research/modalities/hgnc_index.py:182-201` | 3 internal count relations of its own file | the `genes` and `alias_to_symbol` content those counts summarise |
| `research/modalities/hla_coverage.py:396-429` | stated-vs-listed allele counts within its own file | the rest of the coverage artifact |
| `research/modalities/fusion_junction_census.py:730-746` | `summary` vs `_summarise(rows)` — self-consistency, no fresh derivation | the `rows` themselves, against any source |
| `research/modalities/km_digitize.py:1653-1670` | control summary + a `_summary()` of readings, with `ipd` explicitly excluded at `:1666` | the per-figure IPD it publishes |
| `research/modalities/aso_genome_offtarget.py:1500-1509` | `oligo_len`, `max_mismatches`, `gap_region_1based`, `windows_scanned` | the hit tables |
| `research/manuscripts/journal_abbreviations.py:202` | one rendered field per reference | the rest of the reference list |
| `research/manuscripts/journal_reference_authors.py:400` | the rendered author string per reference | the rest |
| `research/modalities/single_slot_identity.py:294-342` | declared identity per slot | the slot's content |
| `research/manuscripts/build_submission_parts.py:392-400` → `_verify` | block presence + line spacing in the built `.docx` | the text content of every block |

**Class F, for completeness (6):** `research/modalities/antitarget_selfcontrol.py:1083-1133`, `research/modalities/fusion_object_inventory.py:774-830`, `research/modalities/map_edit_anchors.py:460-525` (three `check()` bodies that are pure `assert`-based unit tests over functions, plus fixtures), `research/manuscripts/line_citations.py:676-763` and `research/manuscripts/lint_readability.py:307-389` (prose linters), `research/modalities/junction_seam_retraction.py:485-557` (grades a directory sweep; note `:523`, `return 0 if not args.check else 0`, is 0 on both arms). These gate real things; none of them gates a committed artifact against a fresh derivation.

### R5 — Demonstrations: three mutations, three real exit 0 (`PRIMARY`, RUN)

Environment for every run: Linux 6.18.44-fc-v24 x86_64, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, `python3` = system Python 3.11, `cwd=/tmp/claude-0/w27b/scratch`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w27b/pyc`, no network initiated. Exit codes are `subprocess.CompletedProcess.returncode` **of the module itself**, not of a pipeline. Each artifact restored from the live tree before and after each mutation.

```
--- D1 realised_spend (Class A: --check compares nothing, prints drift(), return 0)
  BASELINE exit=0  }
  mutation: realised_usd_ledgered -> 999999.99
  MUTATED  exit=0  }
  VERDICT: STAYS GREEN — gap confirmed
  restored: True

--- D2 ternary_rebuild_cost (Class A2: --check re-derives, never opens the committed artifact)
  BASELINE exit=0  cost : 0.0 reference GPU-h -> $0.00 (plan rate 0.1143)
  mutation: derived_cost.reference_gpu_h -> 424242.0
  MUTATED  exit=0  cost : 0.0 reference GPU-h -> $0.00 (plan rate 0.1143)
  VERDICT: STAYS GREEN — gap confirmed
  restored: True

--- D3 nr4a3_fusion_targets (Class B: gates 3 of 18 top-level keys)
  BASELINE exit=0  offline re-derive matches the artifact
  mutation: evidence_table (whole block) -> 'W27b-MUTATED'
  MUTATED  exit=0  offline re-derive matches the artifact
  VERDICT: STAYS GREEN — gap confirmed
  restored: True
```

**D1** is the sharpest of the three: `realised-spend.json` is the repository's own spend ledger, and a `--check` that prints a drift report and returns 0 regardless is a gate that has already computed the answer and then discards it. **D3** is the one with the most content behind it: the mutated `evidence_table` block is one of fifteen ungated top-level keys in a 34,000-line artifact, and the module's own `--check` answers *"offline re-derive matches the artifact"* over it. **D2** shows the Class-A2 shape W27's taxonomy had no slot for — a check that genuinely can fail, on an object that is not the committed file.

---

## Validation evidence

**RUN.**

1. **Enumeration** — `python3 /tmp/claude-0/w27b/scan.py`, cwd `/home/user/Rare-cancers`, **exit 0**: `139 modules with '--check'`; 129 after the declare/dispatch filter (`resolve2.py`, **exit 0**: `modules 129`).
2. **Extraction** — `resolve.py` → `resolved 129 / total lines 8292`, **exit 0**. `dump.py 0 45`, `dump.py 45 90`, `dump.py 90 130`, `deleg.py 0 20`, `deleg.py 20 39` — all **exit 0**; their output is the per-module `file:line` evidence quoted throughout R2-R4. I read all of it.
3. **Artifact key enumeration** — inline `python3` heredoc over the six artifacts, **exit 0**; the key/line lists in R3 and B5/B6 are its verbatim output, including its `GATED-BUT-NOT-PUBLISHED` check, which reported none for `emc-sra-study.json` and `nr4a3-fusion-targets.json`.
4. **Scratch copy** — `tar -cf - --exclude=./.git . | (cd /tmp/claude-0/w27b/scratch && tar -xf -)`, **exit 0**, `du -sh` = **612M**.
5. **The three demonstrations** — `python3 /tmp/claude-0/w27b/demo.py`, **exit 0**; output quoted verbatim in R5.
6. **Scratch restored, verified at the end.** `cmp -s` against the live tree for all three mutated artifacts → **`IDENTICAL_TO_LIVE`** for `realised-spend.json`, `ternary-rebuild-cost.json`, `nr4a3-fusion-targets.json`. `diff -rq --exclude=.git /home/user/Rare-cancers /tmp/claude-0/w27b/scratch` reports **no content differences** — its only output is eight `Only in /home/user/Rare-cancers/.../reports:` lines, which are other workers' report files the coordinator wrote into the live tree *after* my tar. In-run `restored: True` was also asserted per demonstration by comparing the restored scratch file to the live JSON object.
7. **Live tree untouched.** `git status --porcelain | wc -l` → **0** at start and at end. `git diff --name-only ff6bb01..215ed8e -- research/modalities research/manuscripts` → **0 files**. No git write operation, no `scripts/preflight.sh`.

**PROPOSED (NOT RUN), explicitly:**
- `research/modalities/emc_fourth_cohort_quant.py --check` — refused; `derive()` at `:928` writes two TSVs. Outcome **UNKNOWN**.
- `research/modalities/nr4a3_linker_library_canonical.py --check` — refused; `:851-852` writes `args.out` unconditionally, before the check branch at `:873`. Outcome **UNKNOWN**. Its Class A status is a source finding.
- `research/modalities/emc_sra_study.py --check` — not run; the module fetches over the network when its cache is cold. Its Class B status is a source finding.
- Every other Class A/B/F module — not run.
- Any repair, either option, and any test. **No fix authored, no `--check` edited, no guard weakened, no ceiling raised or proposed, no pytest run of any kind.**

---

## Limitations

- **The 129 vs W27's 130.** My enumeration rule is published above and is reproducible; W27's list is not in its report, so the one-module difference is **unresolved**. Anyone reconciling them should compare `/tmp/claude-0/w27b/modlist.json` against W27's scan.
- **Class C is asserted at the top level only.** A module comparing every top-level key is complete at that level. I make **no** claim about a `derive()` that silently drops a nested field inside a compared key.
- **Class B line evidence is asymmetric by design.** Four new B modules are fully quantified on both sides; for the other 14 I quote the gate `file:line` but did **not** enumerate the artifact's keys and lines. Those published-side counts are **UNKNOWN**, not zero.
- **`fusion_frame_trap.py`'s artifact was not located.** Its subset structure is `PRIMARY`; its published key count is **UNKNOWN**.
- **Class F is my construct, not W27's.** Reasonable owners could fold F into A (raising the "gates nothing about the committed artifact" total to 17) or treat F as out of scope entirely. I kept both totals visible rather than choosing one.
- **Three demonstrations, not eleven.** D1-D3 cover Class A (no comparison), Class A2 (comparison of a derived object) and Class B. The remaining 30 gaps rest on source reading, exactly as W27's `emc_fourth_cohort_quant.py` case does.
- **Nothing here says any committed value *is* wrong.** Every artifact I mutated was restored and verified restored. D1-D3 show only that a wrong value *would not be caught*.
- **No clinical claim.** This is an audit of exit codes. No efficacy, safety, selectivity or readiness statement; no wet lab; no patient data; no new source.
- **Model identity is SELF-REPORT, not independently verified.** HEAD moved under me; I verified no file I measured changed rather than assuming it.

---

## Stop condition

Stated before measurement, five parts, quoted above. **MET in full.** Classes D and E are empty; every one of the 129 modules carries a class assigned from its own source. Both directions are given for every case where I enumerated the artifact, and marked UNKNOWN where I did not. Three demonstrations exceed the required two, with real module exit codes, restored between runs and verified restored at the end. The total is stated. Nothing was written into the Git tree, no repair was authored, no ceiling was raised or proposed, no guard was weakened.

---

## Tool-call and wall-clock count actually used

**31 tool calls** (all `Bash`), **7 minutes 29 seconds** wall clock (`03:25:31Z` → `03:33:00Z`), plus report drafting. Inside the ~40-call / ~40-minute target; I returned on meeting the stop condition.

---

## Next concrete action

**One successor, and it is now unblocked in exactly the way the dispatch anticipated: the owner can choose.** The input W27 said was missing is delivered — **33 modules (A+B), or 39 counting Class F, out of 129**, each named with its gate `file:line`.

The single next action is **for the owner, not for another audit worker: take Option 1 on the 11 Class A modules first.** It costs **0 test functions**, touches no tier budget, and each edit adopts the whole-document idiom **90 sibling modules already use** — the largest, cheapest reduction available, and it eliminates the shape D1/D2 demonstrate (a gate whose output is a function of the file it is meant to be checking). Sequence it by what a wrong value reaches, and start with `realised_spend.py:437-439` (the spend ledger; it already computes the drift it discards) and `nr4a3_fusion_targets.py:2064-2065` (15 of 18 keys, 34,000 lines). Expect first honest runs to go red; per `CLAUDE.md` §6 the response is to fix the drift, never to re-narrow the guard.

**Two things the owner should know before pricing Option 2.** Its allowlist is now writable — the 33 are enumerated — but it would have to allowlist **39** entries, not 10, which is a third of every `--check` module in the repository; a meta-guard with an exemption list that long is close to the failure W27 already flagged. And the allowlist would have to carry **two modules whose `--check` writes** — `emc_fourth_cohort_quant.py:928` and the newly found `nr4a3_linker_library_canonical.py:851-852` — which a static guard cannot exercise at all. I do not recommend either option; I have not authored either; and I propose no ceiling change.

**A separate, smaller handoff, offered to W14e's lane rather than claimed as mine:** `nr4a3_linker_library_canonical.py:851-852` is a `--check` that writes its own output before evaluating the check, and it prints `"[canon] wrote ..."` while doing so. That belongs on W14b/W14e's self-writing-`--check` axis, not on this census's.
