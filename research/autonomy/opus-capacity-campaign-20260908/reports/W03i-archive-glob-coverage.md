<!-- collected 2026-09-08T04:43:31Z by campaign coordinator; agent id aae4c68a9b2eac1a6; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aae4c68a9b2eac1a6.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

- **Worker:** W03i, lane 3, OPUS-CAPACITY-CAMPAIGN-20260908. Re-dispatch; named successor to W03h.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the runtime model from the child transcript.
- `date -u` **start:** `Tue Sep  8 04:34:29 UTC 2026`; **end:** `Tue Sep  8 04:39:59 UTC 2026` (report drafting followed).
- `git rev-parse HEAD` start **and** end: `408b676aec3625a36917755662516232a27a1278` (HEAD did not move under me). `git status --porcelain` empty at start and end (`porcelain-count=0`). **I wrote nothing in `/home/user/Rare-cancers` and ran no git write operation.** All scratch was under `/tmp/claude-0/w03i/`, deleted before returning (`ls -d` → `No such file or directory`).
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (51 lines; the five very long proxy/truststore lines — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are elided here as they name no model; the end-of-run re-run produced the same 51-line set):

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

**Does the declared glob list in `research/manuscripts/aso_archive_manifest.py` still cover everything the ASO submission actually ships?** W03h measured that the inventory is *(declared glob patterns) ∩ (git-tracked)* and that a **committed** artifact matching no declared glob is silently outside it and goes undetected by `--check-archive` (its P3b). That makes the coverage of the pattern list an unmeasured input to the PUB-ASO owner's `:423` decision. The deliverable is a classified list for adjudication, **not** a patch.

**Stop condition set up front:** stop as soon as (a) the declared pattern list is quoted with `file:line` and the prefixes it reaches are enumerated; (b) honest denominators exist — tracked files per reached prefix, inventory rows, and the size of the set difference — and my reconstruction of the inventory is validated against the committed manifest; (c) every tracked-but-not-inventoried file in the deposit's own directory is classified with committed-text evidence, and the wider reached prefixes are screened for the same class; (d) no repository write occurred and the scratch directory is deleted. **All four met.**

## Prior-work check

Read in full, in this order: `reports/W03h-archive-check-discrimination.md`, `reports/W03g-archive-manifest-check-modes.md`, `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md` — all under `research/autonomy/opus-capacity-campaign-20260908/` (a `reports/` directory at the repo root does not exist; located with `find . -name 'W03h-*'`).

Orientation and evidence commands (all read-only on the live tree):

```
git rev-parse HEAD ; git status --porcelain ; git ls-files
sed -n '890,960p;1255,1300p;790,890p;350,395p;1488,1510p' research/manuscripts/aso_archive_manifest.py
grep -n '_resolve(' research/manuscripts/aso_archive_manifest.py
grep -n '"patterns"' research/manuscripts/aso_archive_manifest.py
grep -n -i -E 'redteam|cover-letter|docx|deposit-state|census|claim-audit|…' research/manuscripts/aso_archive_manifest.py
grep -rn -i -E 'not in the (manifest|archive|deposit)|not deposited|…' --include='*.py' --include='*.md' --include='*.sh' research scripts
sed -n '1,40p;204,220p;270,330p' research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py
sed -n '1,40p' research/manuscripts/aso_deposit_drift.py
grep -n 'aso_sequence_manifest' scripts/regenerate_aso_chain.sh
```

**Not replayed / not done, per the dispatch and the standing constraints.** I did not add, remove or reorder any glob; did not edit `aso_archive_manifest.py` or any other file; did not run `scripts/regenerate_aso_chain.sh`; did not make the `:423` swap; did not `git fetch`; did not run `scripts/preflight.sh`; did not invoke `atr_hrd_sarcoma_series.py` at all. **I did not re-run W03h's perturbation experiment** — its P0–P5 results are cited, not repeated — and I did not re-run W03g's two live mode invocations. No network retrieval of any kind (no Ensembl, no PubMed, no proxy attempt). No Brenca/Hofvander/pazopanib/sunitinib/Wagner/CTARC/trabectedin route; no GSE4303/GSE28866 work; no lane-11 source-index work; the restricted NR4A Perspective was not touched under any framing. **No `reports/W25-*` was read, listed or referenced.** I authored, proposed and applied no repair, patch, gate or test, and weakened no guard.

**Write-safety confirmation, established from source before running anything (not inherited).** I ran **no mode of `aso_archive_manifest.py` at all** — the question is answerable by reading the committed manifest JSON and reconstructing the glob resolution in my own scratch script, so no invocation was needed. I nonetheless verified W03h's finding independently while reading `build()` and the dispatch: the module's single write site is `:1974-1975`, and both check branches return at `:1963/:1966` (`--check-archive`) and `:1969/:1972` (`--check`), before it. All Python I executed ran with `PYTHONDONTWRITEBYTECODE=1`-equivalent isolation (scratch scripts under `/tmp/claude-0/w03i/`, reading the repo only); `git status --porcelain` is 0 at start and end.

## Method and inputs

**Inputs (live checkout, HEAD `408b676a…`):**
`research/manuscripts/aso_archive_manifest.py`; the committed manifest `research/manuscripts/aso/fusion-junction-aso-archive-manifest.json`; `git ls-files` (7,808 tracked paths); `research/manuscripts/aso/fusion-junction-aso-research-article.md`; `research/manuscripts/aso_deposit_drift.py`; `research/manuscripts/aso_sequence_manifest.py`; `research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py`; `scripts/regenerate_aso_chain.sh`.

**Pattern extraction was done by `ast`, not by eye.** A scratch script parsed the module and read the `PROMISES` literal, returning each row's `id`, its `patterns` list, and the source line span of that list. **28 promise rows, 159 declared patterns.** Nothing was hand-transcribed.

**Inventory reconstruction (the validation step).** A second scratch script re-implemented `_resolve` exactly as written at `aso_archive_manifest.py:927-950` — `glob.glob` per pattern (non-recursive; `*` does not cross `/`), `os.path.isfile`, `SELF_EXCLUDE` (`:890`), the `-graded.json` strip for non-graded rows, and the `rel not in tracked` drop — over the live tree and live `git ls-files`.

**Environment:** Linux, system CPython `python3`, no network (agent proxy denies CONNECT; none attempted). **These are not preflight results.**

## Result

### R0 — The reconstruction is exact, which is what licenses every denominator below (PRIMARY, EXECUTED)

| Quantity | Value |
|---|---|
| Promise rows in `PROMISES` | **28** |
| Declared glob patterns | **159** |
| Tracked files in the repository (`git ls-files`) | **7,808** |
| Patterns ∩ tracked, resolved by my re-implementation | **505** |
| `gaps.import_closure.added` (modules pulled in by Python import, not by any pattern) | **11** |
| Manifest `files` rows (`n_files` field, and `len(files)`, and unique paths) | **516** |
| 505 + 11 | **516** — exact |
| Set difference `inventory − my_glob_resolution` | exactly the 11 import-closure modules |
| Set difference `my_glob_resolution − inventory` | **∅** |

So the inventory is precisely **(159 declared globs ∩ tracked) ∪ (11-module import closure)**, and my model of it is byte-exact against the committed artifact. `inventory_limited_to_tracked_files` is `true` in the manifest, confirming the tracked intersection is live.

### R1 — Honest denominators: what the pattern list reaches, and how much of it it takes (PRIMARY, EXECUTED)

The 159 patterns are non-recursive and reach exactly **11 directories**. Tracked files directly in each (not recursive), against inventory rows in each:

| Reached directory | tracked | in inventory | tracked, NOT inventoried |
|---|---:|---:|---:|
| `research/data` | 2 | 1 | 1 |
| `research/literature` | 76 | 3 | 73 |
| `research/manuscripts` | 94 | 22 | 72 |
| **`research/manuscripts/aso`** | **81** | **45** | **36** |
| `research/manuscripts/figures` | 67 | 21 | 46 |
| `research/manuscripts/fusion-partner` | 7 | 2 | 5 |
| `research/manuscripts/tests` | 115 | 4 | 111 |
| `research/modalities` | 1,590 | 389 | 1,201 |
| `research/modalities/noncoding-acceptor` | 15 | **15** | **0** |
| `research/modalities/tests` | 448 | 13 | 435 |
| `scripts` | 48 | 1 | 47 |
| **total** | **2,543** | **516** | **2,027** |

**No inventory row lies outside these 11 directories** (0 rows), and no inventory row is untracked (0) — the two consistency checks pass.

**The 2,027 figure is a true denominator but a bad question.** 148 of the 159 patterns are exact filenames; for those, "the directory is reached" says nothing about siblings. Only 11 patterns contain a wildcard, and only one directory (`research/modalities/noncoding-acceptor/*.json`) is swept wholesale — it is 15/15. So the classification below is run over (i) **the deposit's own directory**, `research/manuscripts/aso/` — 81 tracked, 45 inventoried, **36 out** — and (ii) a name-screened pass over the other ten directories.

### R2 — The declared pattern list, quoted with `file:line` (PRIMARY, source)

Resolution machinery — `_tracked_files()` at `aso_archive_manifest.py:904-923`, `_resolve()` at `:927-950`, `SELF_EXCLUDE` at `:890`, the single call site at `:1292` (`resolved = _resolve(row["patterns"])`). All 28 rows, cited by the source-line span of the row's `patterns` list:

| Row `id` | `patterns` at | Patterns (n) |
|---|---|---:|
| `reproduction_command` | `:118-159` | 23 exact paths (chain script, per-junction table, figure/format builders, lints, `submission_packet.py`, …) |
| `noncanonical_acceptor_screens` | `:201-206` | 5 exact + `research/modalities/noncoding-acceptor/*.json` |
| `graded_junction_atlas` | `:219-221` | 3 exact |
| `per_junction_design_panels` | `:229-230` | `research/modalities/junction-aso-designs*.json`, `junction_aso.py` |
| `specificity_screen_blast` | `:245-248` | `junction-aso-offtarget-*n3.json` + 3 exact |
| `specificity_screen_exhaustive` | `:259-260` | `aso-insilico-evaluation*.json`, `aso_insilico.py` |
| `graded_rescores` | `:269` | `junction-aso-offtarget-*-graded.json` |
| `per_design_tables` | `:291-303` | 13 exact |
| `retrieval_records` | `:311-349` | 15 exact + `research/manuscripts/aso/lit-targets-*.json` |
| `correction_record` | `:359-369` | 6 exact (incl. `fusion-junction-aso-paper-redteam.md`, singular) |
| `inputs_that_make_it_offline` | `:394-397` | 4 exact |
| `duplex_thermodynamics` | `:407-409` | 3 exact |
| `premrna_compartment_screen` | `:423-426` | 4 exact (`aso-premrna-offtarget.json`, `aso-premrna-sequences.json`, producer, test) |
| `mature_parent_gap_pairing_screen` | `:441-443` | 3 exact |
| `genome_wide_screen` | `:462-465` | 4 exact |
| `duplex_energy_rescore` | `:497-511` | 2 exact |
| `censoring_test_and_genomic_attempt` | `:536-538` | `junction-aso-offtarget-*-deep500*.json`, `aso-insilico-evaluation-*-deep500*.json`, `aso-premrna-offtarget-genomic.json` |
| `priorart_first_in_kind_evidence` | `:549-550` | 2 exact |
| `test_articles_and_cell_models` | `:578-581` | 4 exact |
| `unrearranged_allele_scan` | `:602-608` | 7 exact |
| `delivery_antigen_negative` | `:626-632` | 7 exact (incl. `aso/aso-delivery-antigen-2026-08-08.md`) |
| `canonical_sequence_record` | `:671-676` | 6 exact |
| `reproduction_guards` | `:691-696` | 5 exact |
| `falsification_power` | `:723` | 1 exact |
| `where_each_number_lives` | `:748-759` | 12 exact |
| `reimplementation_crosscheck` | `:777-779` | 3 exact |
| `deposited_documents` | `:831-833` | `aso/fusion-junction-aso-*article*.pdf`, `aso/fusion-junction-aso-*article*.build-stamp.json` |
| `manuscript_and_figures` | `:866-884` | 4 exact + `figures/aso_*_figure.py`, `figures/aso-*.pdf`, `figures/aso-*.png`, `figures/aso-*.svg` + 4 exact |

**The module already names this shape as its own known failure mode**, twice, in the same row: `:829-830` — *"A hand-kept list is what produced both this hole and the 2026-08-19 one recorded above; the fix for a list that goes stale is not a longer list"* — and `:874-876` — *"This row names literal paths, so the paper split that created the journal article could not add it — the row's own warning above, firing a second time."*

### R3 — The headline: a deposited chain step's inputs are committed and outside the pattern list (PRIMARY, source-derived)

`scripts/regenerate_aso_chain.sh:318` invokes `aso_sequence_manifest.py` as the "canonical sequences" chain step; the module is inventoried. It declares, at `aso_sequence_manifest.py:142-147`:

```
_PREMRNA_ARTIFACTS = ("aso-premrna-offtarget.json", "aso-premrna-offtarget-genomic.json",
                      "aso-premrna-offtarget-18mer-5-8-5.json",
                      "aso-premrna-offtarget-20mer-5-10-5.json",
                      "aso-premrna-offtarget-ewsr1intron2.json",
                      "aso-premrna-offtarget-taf15intron2.json",
                      "aso-premrna-offtarget-noncoding-acceptor.json")
```

and opens **every one of them unconditionally**, with the absence of a `try/except` stated as deliberate at `:152-155`: *"A missing artifact must break the build loudly: it means the pre-mRNA screen is not in the deposit."*

Measured against the committed manifest:

| `_PREMRNA_ARTIFACTS` member | in inventory? | matched by |
|---|---|---|
| `research/modalities/aso-premrna-offtarget.json` | **IN** | `:423` |
| `research/modalities/aso-premrna-offtarget-genomic.json` | **IN** | `:536-538` |
| `research/modalities/aso-premrna-offtarget-noncoding-acceptor.json` | **IN** | `:201-206` |
| `research/modalities/aso-premrna-offtarget-18mer-5-8-5.json` | **OUT** | — |
| `research/modalities/aso-premrna-offtarget-20mer-5-10-5.json` | **OUT** | — |
| `research/modalities/aso-premrna-offtarget-ewsr1intron2.json` | **OUT** | — |
| `research/modalities/aso-premrna-offtarget-taf15intron2.json` | **OUT** | — |

**All four are tracked and present on disk.** This is exactly the failure the repository has already paid for once — `test_the_deposited_chain_can_run_from_the_deposit.py:1-27` records the round-23 incident (`aso_offtarget_duplex_energy.py` and its output absent from a *published* 484-path archive) and its assert message at `:320-329` names the remedy: *"Add the inputs to a `patterns` list in research/manuscripts/aso_archive_manifest.py and re-derive the manifest."*

**W03h's "no check in the repository would say so" needs one correction and survives it.** That guard exists and is the intended check — but it resolves inputs via `_module_level_paths()` (`:204-213`), documented as evaluating *"the two idioms this lane actually uses"* — `os.path.dirname(os.path.abspath(__file__))` and `os.path.join(...)` over already-known names — and returning `{constant name: absolute path}`. `_PREMRNA_ARTIFACTS` is a module-level **tuple of bare basenames** joined at call time inside `_load(*parts)` (`aso_sequence_manifest.py:75-78`), which binds no name to a path. **Source reading, NOT EXECUTED:** the guard therefore appears blind to this third idiom. I did **not** run it — pytest writes `.pytest_cache/` into the repository root, which my write isolation forbids — so whether it currently passes or fails is **UNKNOWN and is the single most valuable next measurement**.

Two further tracked-but-not-inventoried artifacts are named inside inventoried modules by the same shape: `research/modalities/aso-genome-offtarget-taf15intron2.json` (named in `aso_taf15_intron2_designs.py`, inventoried at `:602-608`) and `research/modalities/junction-aso-offtarget.json` (named in `junction_aso_offtarget.py`, `junction_seam_retraction.py` and `aso_screen_sets.py`, all inventoried). I did not trace whether those two are *opened* or merely *mentioned*; grade **UNKNOWN**, needing the same open-site check I performed for the premrna four.

### R4 — Classification of all 36 tracked, non-inventoried files in `research/manuscripts/aso/` (PRIMARY)

Denominator: **81 tracked in that directory, 45 inventoried, 36 out.**

**DELIBERATE EXCLUSION — 3 files, documented in committed text**

| File | Documented where |
|---|---|
| `fusion-junction-aso-archive-manifest.json` | `aso_archive_manifest.py:888-890` (`SELF_EXCLUDE`, *"The manifest never lists itself… named here so a reader can see the omission is a decision"*) + the manifest's own `self_entry` block (`travels_with_the_deposit: true`, `in_the_files_list_below: false`, with the fixed-point argument spelled out). |
| `fusion-junction-aso-cover-letter.md` | `aso_archive_manifest.py:845-859`: *"⛔⛔ THE COVER LETTER CAME OUT OF THE DEPOSIT ON 2026-08-30, AND IT SHOULD NEVER HAVE BEEN IN IT"*, quoting the user in session, and recording three incidents caused by depositing it. Note it is still named by the inventoried `submission_packet.py` — worth the owner's eye, but the exclusion itself is unambiguous. |
| `fusion-junction-aso-preprint-checklist.md` | `aso_deposit_drift.py:22-25`: *"**the preprint checklist is NOT in the manifest** — verified against the committed file list, 515 paths, and the checklist is not one of them. Nor is this module."* Recorded as a relied-upon property (the drift count's non-self-reference depends on it) rather than as a rationale — a weaker form of "documented why", but committed and deliberate. **Note the stated denominator there is 515; it is 516 today** — the deposit has grown by one path since that comment was written. |

**PATTERN GAP — 7 files that look like they belong and match no declared glob**

| File(s) | Why it looks like it belongs |
|---|---|
| `fusion-junction-aso-journal-article-manuscript.docx`, `-title-page.docx`, `-figure-legends.docx` | **Their own build stamps are deposited and they are not.** `fusion-junction-aso-journal-article-manuscript.docx.build-stamp.json` and the other two stamps match `fusion-junction-aso-*article*.build-stamp.json` (`:832-833`) and are inventory rows; the `.docx` match `*article*` but not `.pdf`, so they fall out. The extension census confirms it: `payload_file_types.by_extension` has `.pdf` (8) and **no `.docx` at all**. The inventoried guard `research/manuscripts/tests/test_the_word_manuscript_is_current_and_whole.py:30` names the manuscript `.docx` as `DOCX` — a deposited test whose subject is absent, which is the very defect the module warns of at `:874-878` in the other direction. **Counter-argument for the owner:** the row's `promise` at `:816-817` speaks only of *"The PDFs in the archive…"*, so a reading in which the `.docx` are journal-submission artifacts rather than archive payload is defensible. The asymmetry — stamp in, stamped file out — is what needs a decision either way. |
| `aso-delivery-evidence-2026-08.json` + `.md`, `atu027-systemic-sirna-solid-tumour-evidence.json` + `.md` | The `delivery_antigen_negative` row (`:626-632`) deposits `research/manuscripts/aso/aso-delivery-antigen-2026-08-08.md`, a dated delivery-evidence memo of exactly this family, by exact path. These four are the same shape, same directory, same lane, and match nothing. Both `.md` files cross-reference each other. |

**UNKNOWN — 26 files, not determinable from committed text**

Governance / process records (17): the 11 numbered red-team rounds `fusion-junction-aso-paper-redteam-round{2,3,4,5,6,7,8,9,10,11-absent,12}.md` (10 present: 2–10 and 12), plus `fusion-junction-aso-submission-plan.md`, `fusion-junction-aso-deposit-stopping-rule.md`, `fusion-junction-aso-guard-coverage-audit.md`, `nat-revision-checklist-2026-08-25.md`, `review-backlog-2026-08-19.md`, `fusion-junction-aso-claim-audit-manifest.json`, `fusion-junction-aso-claim-audit-verdicts.json`.
**Why UNKNOWN rather than DELIBERATE:** the `correction_record` row (`:352-369`) quotes the paper's promise *"The complete correction record, including every superseded value, is released with the archive"* and deposits `fusion-junction-aso-working-record.md` + `fusion-junction-aso-paper-redteam.md` (the 2026-08-05 review of the working record, which narrates the withdrawal) + `pinned-figures.json`. The numbered rounds' own front matter (e.g. round 7, round 12) describes them as adversarial reviews of the *submission*, not as records of superseded values — a good argument that they are correctly out — but **no committed text states that**, so the class is not determinable, only arguable.

Venue / citation / census inputs (7): `journal-abbreviations.json`, `journal-reference-authors.json`, `venue-fee-screen.json`, `nat-scope-census.json`, `gcc-scope-census.json`, `aso-design-only-census.json`, `hybrid-intron-map-edits.json`. Their producers (`venue_fee_screen.py`, `nat_scope_census.py`) are themselves not inventoried; none is named by any of the 77 inventoried `.py` files. Nothing in committed text says they are excluded.

Two with a specific hook (2): `deposit-state.json` — named inside the inventoried `aso_archive_manifest.py` at `:1498-1503` as *"where what-is-reserved lives"*; leaving it out avoids a record of the deposit inside the deposit, but no committed text says that is the reason. `hybrid-intron-aso-target.md` — cited in prose by the inventoried `aso_premrna_offtarget.py:17` (*"`hybrid-intron-aso-target.md` states it plainly for the same database families"*); a citation, not an open.

### R5 — Screen of the other ten reached directories (PRIMARY, EXECUTED)

Restricting the 2,027 to files whose **basename contains "aso"** gives **51** tracked, non-inventoried candidates: 25 in `research/manuscripts/aso/` (already in R4) and **26 elsewhere**. Of those 26, ten are named inside an inventoried module — the R3 set (4 premrna variants, `aso-genome-offtarget-taf15intron2.json`, `junction-aso-offtarget.json`) plus five inventoried-module *tests* that are not themselves deposited (`test_aso_coverage_ladder.py`, `test_aso_deposition_doi_is_one_fact.py`, `test_aso_figure_chain_is_complete.py`, `test_aso_figure_text_fits.py`, `test_aso_sequence_manifest_joins.py`, `test_aso_insilico_scan_equivalence.py`, `test_junction_aso_thermo.py`). The remaining sixteen — including `research/modalities/aso-parent-gap-pairing-{18mer-5-8-5,20mer-5-10-5}.json` and `junction-aso-thermo-{18mer-5-8-5,20mer-5-10-5}.json`, geometry-variant siblings of exact-path patterns at `:407-409` and `:441-443` — are named by no inventoried module and by none of the three manuscripts. **All 26 are UNKNOWN pending the owner's judgement, except the six of R3, which are PATTERN GAP candidates on the strength of being read by deposited code.** The `-graded.json` re-scores W03h flagged as UNGRADED-on-purpose are a separate, already-declared class: 53 of them are enumerated in the manifest's `gaps.screen_coverage.gap_resolved_screens_with_no_committed_graded_rescore`, and none is a tracked file at all.

### R6 — Direct answer

**No. The declared glob list does not cover everything the ASO submission ships, and the shortfall is not hypothetical.** At minimum four committed artifacts that a deposited chain step opens unconditionally are outside the inventory (R3). W03h's P3b class is therefore **already real**, not merely possible. Everything else in the 36 splits 3 documented-deliberate / 7 gap-shaped / 26 undeterminable.

## Validation evidence

**RUN.** Live checkout `/home/user/Rare-cancers` at HEAD `408b676aec3625a36917755662516232a27a1278`, system CPython, scratch scripts under `/tmp/claude-0/w03i/`, no network. **Not preflight. No module of the repository was executed** — only `git ls-files`, `grep`/`sed`, and my own scratch scripts reading committed files.

| # | Command | Real exit | Key verbatim output |
|---|---|---|---|
| V0 | `date -u; git rev-parse HEAD; git status --porcelain` (start) | 0 | `Tue Sep 8 04:34:29 UTC 2026`; `408b676a…`; empty |
| V1 | scratch `extract.py` — `ast` parse of `PROMISES` | 0 | `rows: 28` / `patterns: 159` |
| V2 | `git ls-files > tracked.txt` | 0 | 7,808 paths |
| V3 | scratch `diff.py` — per-directory tracked vs inventory | 0 | `manifest n_files field: 516 len(files): 516 unique: 516`; `tracked total: 7808`; `total tracked in reached dirs: 2543`; `inventory rows outside reached dirs: 0`; `total tracked-not-inventoried in reached dirs: 2027` |
| V4 | scratch — 36 non-inventoried files under `research/manuscripts/aso/` with sizes | 0 | `81 tracked; 45 inventoried; 36 not` |
| V5 | scratch — re-implementation of `_resolve` over the 159 patterns | 0 | `glob-resolved (tracked): 505`; `inventory: 516`; `inv - glob:` = the 11 `import_closure` modules; `glob - inv: []` |
| V6 | scratch — the 7 `_PREMRNA_ARTIFACTS` against the inventory | 0 | 3 `IN`, 4 `OUT` (verbatim table in R3) |
| V7 | scratch — 36 aso/ files scanned against the 77 inventoried `.py` | 0 | `inventoried .py files scanned: 77`; hits for `deposit-state.json`, the manifest itself, `cover-letter.md`, `…-manuscript.docx`, `hybrid-intron-aso-target.md` |
| V8 | scratch — same scan for the 26 non-`aso/` name-screened candidates | 0 | 10 `HIT`, 16 `--` (verbatim list in R5) |
| V9 | `grep -rn -i -E 'not in the (manifest\|archive\|deposit)\|not deposited\|…'` over `research scripts` | 0 | surfaced `aso_deposit_drift.py`, `aso_archive_manifest.py:845`, `test_the_deposited_chain_can_run_from_the_deposit.py:320,387` |
| V10 | `grep -n 'aso_sequence_manifest' scripts/regenerate_aso_chain.sh` | 0 | `318: run_step "canonical sequences" "python3 $MAN/aso_sequence_manifest.py" …` |
| V11 | `date -u; git rev-parse HEAD; git status --porcelain \| wc -l` (end) | 0 | `Tue Sep 8 04:39:59 UTC 2026`; `408b676a…`; `porcelain-count=0` |
| V12 | `rm -rf /tmp/claude-0/w03i; ls -d /tmp/claude-0/w03i` | 2 (ls) | `ls: cannot access '/tmp/claude-0/w03i': No such file or directory` |

**PROPOSED (NOT RUN).** Running `pytest research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py` — **deliberately not run**: pytest writes `.pytest_cache/` into the repository root, which write isolation forbids; it would need a `cp -a` scratch tree. Any edit to a `patterns` list, or to `_module_level_paths`. The `:423` swap. `scripts/regenerate_aso_chain.sh`. `git fetch`. `scripts/preflight.sh`. Any patch, gate or test. **No content-policy refusal occurred in this unit.**

## Limitations

- **The classification is an inspection, not an adjudication, and it says so.** DELIBERATE EXCLUSION means committed text documents the omission; it does not mean the omission is right. PATTERN GAP means the artifact is committed, deposit-shaped, and matches nothing; for the three `.docx` I have quoted the committed sentence that argues the other way. **UNKNOWN is 26 of 36** — the largest class — and it is honest: absence of a documented rationale is not evidence that no rationale exists.
- **R3's central claim is source-derived, not executed.** I read that `aso_sequence_manifest.py` opens all seven `_PREMRNA_ARTIFACTS` with no `try/except` and that four are outside the inventory; I did **not** unpack the archive and run the chain step against it. The failure mode is inferred from the code path, and the module's own comment states the intended consequence.
- **Whether the existing guard already catches it is UNKNOWN.** My reading of `_module_level_paths` (`:204-213`) says a module-level tuple of bare basenames is a third idiom it does not evaluate, but I did not run the test, so I cannot say whether it is currently green or red. That is a one-command measurement on a scratch copy and it decides whether R3 is an unguarded gap or a known-failing gate.
- **The 2,027 denominator is real but should not be quoted as a gap size.** 148 of 159 patterns are exact filenames, so most of those 2,027 files were never in scope. The classifiable set is the 36 in the deposit's own directory plus the name-screened 26.
- The name screen ("basename contains `aso`") is a **heuristic**, and it will miss a deposit-relevant artifact named without that string — `deposit-state.json` and the three censuses are exactly that shape inside `aso/`, and their analogues elsewhere would not have been found. **Not a complete enumeration of the wider directories.**
- One incidental measurement worth an owner's eye and nothing more: `aso_deposit_drift.py` records the deposit as **515 paths**; it is **516** today. A comment stating a count that has since moved is not itself a defect, and I did not investigate which path arrived.
- Measured at one HEAD (`408b676a…`), on one machine. Nothing here is a statement about any other commit, about CI, or about the published Zenodo archive's actual contents — only about the committed manifest and the working tree.
- **Nothing here is evidence about any oligonucleotide's efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab. A manifest's contents are a statement about file freshness and nothing else.**

## Stop condition

Set up front, four clauses (a)–(d) under **Question**. **Met, all four.** (a) R2 — 28 rows, 159 patterns, each with its `patterns` line span, plus the resolution machinery at `:890/:904-923/:927-950/:1292`. (b) R0 and R1 — 7,808 tracked, 2,543 in reached directories, 516 inventory rows, 2,027 difference, and my re-implementation reproduces the inventory exactly (505 + 11 = 516, symmetric difference ∅), which is the validation that licenses the rest. (c) R4 classifies all 36 in `research/manuscripts/aso/` (3 / 7 / 26) with `file:line` evidence, and R5 screens the other ten directories. (d) No repository write, `porcelain-count=0` at start and end, HEAD unmoved, scratch deleted and confirmed absent. Returning now.

## Tool-call and wall-clock count actually used

**16 tool calls** (all `Bash`; no `Read`, no `Skill`, no network, no background task, no poller). One early `ls /home/user/Rare-cancers/reports/` failed — that directory does not exist — and was resolved with `find`. **Wall clock 04:34:29Z → 04:39:59Z ≈ 5.5 minutes of execution**, plus report drafting. Well inside the ~40 calls / ~40 minutes target.

## Next concrete action

**For the PUB-ASO owner, one decision and one measurement, in that order.**

The decision is now concrete rather than hypothetical: **four committed artifacts that the deposited "canonical sequences" chain step opens unconditionally are not in the archive** — `aso-premrna-offtarget-{18mer-5-8-5,20mer-5-10-5,ewsr1intron2,taf15intron2}.json` — and the repository's own guard for this class already spells out the remedy in its assert message (*"Add the inputs to a `patterns` list … and re-derive the manifest"*, `test_the_deposited_chain_can_run_from_the_deposit.py:326-329`). **I have deliberately not made that edit**; it changes what a published deposit contains, and it is the owner's call. Two secondary items travel with it: whether the three `.docx` belong in an archive that already carries their build stamps, and whether the four `aso-delivery-evidence`/`atu027` files belong beside the `aso-delivery-antigen-2026-08-08.md` the same row already deposits.

**The single most useful successor measurement in this lane** is one command on a scratch copy: `cp -a` the tree to `/tmp`, then run `pytest research/manuscripts/tests/test_the_deposited_chain_can_run_from_the_deposit.py` there and record the real exit code. If it is **red**, the gap in R3 is already flagged by a gate someone has been living with, and the finding is a triage item. If it is **green**, the guard has a third resolver idiom it cannot see (`_PREMRNA_ARTIFACTS` — a module-level tuple of bare basenames consumed through `_load(*parts)`), and the gap is genuinely unwatched — which is the stronger version of W03h's P3b and the thing that most changes what `--check-archive` is worth in the chain. I did not run it because pytest writes `.pytest_cache/` into the repository root and my write isolation forbids it; on a scratch copy it costs about a minute and no repository byte.
