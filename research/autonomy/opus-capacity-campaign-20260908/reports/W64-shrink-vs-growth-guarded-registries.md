<!-- collected 2026-09-08T04:54:43Z by campaign coordinator; agent id a15d7676ea5c0fcd4; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a15d7676ea5c0fcd4.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted; nothing written to the repo.

## Worker

W64, registry-coverage lane. Model: **SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — Claude Opus 5 (`claude-opus-5`). No env var names or asserts a served model; literal output of the required command:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...,api.anthropic.com,...
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ...
NO_PROXY=localhost,127.0.0.1,::1,...
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

State:

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 04:48:35 UTC 2026` | `Tue Sep  8 04:52:17 UTC 2026` |
| `git rev-parse HEAD` | `8a667406e875ae99c7d50347b2e895a177fcb048` | `56f355f65b7b3e47aeb434ac02edf4cf049f40f3` |
| `git status --porcelain` | 0 lines | 0 lines |

HEAD advanced under me (coordinator collection); the brief's measured guarantee is that campaign commits touch only the campaign directory, and my working tree stayed clean at 0 lines throughout. All reads were of the live checkout, never the frozen corpus.

## Question

For every hand-maintained registry / target list / allow-list / budget file in the repository: does an executable check **fail** when a declared entry disappears (SHRINK-GUARDED), when the corpus gains something the registry does not list (GROWTH-GUARDED), both, or neither — and what is each registry's coverage ratio against the population it is meant to cover?

Open because W47 and W51 established the asymmetry for exactly one registry (`pinned-figures.json`) and nobody has asked whether it generalises.

## Prior-work check

Taken as given from the brief, not re-measured: W51's 16/187 `lint_consistency` coverage, W47's 183-entry / 18-consumer `pinned-figures` map, W41's `inputs/` gitignore finding and the `test_every_tests_directory_in_the_repository_is_inside_some_budget` failure under `PREFLIGHT_FULL=1`, W43's key-literal-grep rule (which I used: `^(DEFAULT_TARGETS|TARGETS|...) *= *[\[\(]`, `\[K1\]`, `\bDOC_SKIP\b`, not substring greps).

Commands run for novelty: `grep -rn -E '\b(DOC_SKIP|ID_SKIP|TRANSIENT_DIRS|...)\b' --include='*.py' ...`; `grep -rn -E '^(DEFAULT_TARGETS|TARGETS|SOURCES|REQUIRED)[A-Z_]* *= *[\[\(]' --include='*.py' .`; `git ls-files | grep -E '\.json$' | xargs grep -l -E '"(targets|must_appear_in|allow|budgets|tiers)"'`. No prior shrink/growth matrix exists in the tracked corpus. W25 not read or referenced.

## Method and inputs

Read-only source reading plus three read-only executions on the live tree. Coverage denominators computed with `git ls-files`, `os.walk`, and by importing the linters' own modules so the effective (post-glob) target lists are measured rather than the literal ones. `research/modalities/atr_hrd_sarcoma_series.py` never invoked. `scripts/preflight.sh` never invoked.

## Result

Classification rule used, stated up front: **SHRINK-GUARDED** = some executable check exits non-zero (or a test fails) when a declared entry is removed or its referent vanishes. **GROWTH-GUARDED** = some executable check exits non-zero when the population gains a member the registry does not list. A `warn`/`info` that does not change an exit code is **detected-not-enforced**, and I count it as NOT guarded.

| # | Registry (hand-maintained) | n declared | Shrink guard (file:line) | Growth guard (file:line) | Class | Coverage ratio |
|---|---|---|---|---|---|---|
| R1 | `research/manuscripts/pinned-figures.json` → `targets` | 29 (28 `.md`, 1 `.json`) | `systems/parser_guard.py:126-131` — fails per nonexistent target | **none** | **SHRINK ONLY** | 16/187 tracked `research/manuscripts/**.md` (W51, given); union of all pin-declared paths = 31 |
| R2 | `pinned-figures.json` → `must_appear_in` + `file` union | 14 distinct paths | `systems/parser_guard.py:132-139` | fixed 3-document floor only: `research/manuscripts/tests/test_pinned_figures_every_home.py:95-115` asserts the ASO article, SI and journal article each carry ≥1 pinned home — a hardcoded triple, not corpus-relative | **SHRINK + FIXED-FLOOR** | 14 declared homes; population (documents restating a pinned quantity) not computable |
| R3 | `scripts/tier-budgets.json` → `tiers[].directories` | 5 | **indirect only** — `tier_budget.py:80-81` `count_dir` returns `(0,0,[])` for a missing directory, so a vanished dir counts zero; the collapse would eventually trip `scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py:138-151` (ceiling ≤ 1.6×count+50) | **yes** — `scripts/tests/test_a_tier_budget_is_a_decision_somebody_took.py:118-135` walks the tree and fails on any `tests/` dir in no tier | **BOTH (growth real, shrink indirect)** | **5/7** — 2 uncovered, both the untracked campaign `inputs/source-index/**/tests` dirs (W41, given). Live `tier_budget.py --check` = rc 0 |
| R4 | `research/method-watch-triggers.json` → `triggers` | 39 | `systems/systems_check.py:1263-1265` `[X2]` **errors** when a `TECH-*` names a trigger id absent from the registry; `research/modalities/tests/test_glue_watch_row.py:42` pins 1 of 39 by id. `parser_guard.py:173-187` guards only the file and its `evidence_home` paths, not entries | **yes, same check** — `[X2]` fires in exactly the "graph gained a reference the registry lacks" direction | **BOTH** | **32/32** = 100% of the computable population (TECH `scan_trigger` refs); reverse direction (7 triggers watched by no TECH) is `[X3]`/`[X5]` **warn only**, `:1272-1275` |
| R5 | `systems/graph/artifact-refs.json` → `dispositions` | 4 | none — `[K2]` (`systems_check.py:2001-2015`, `:2110`) errors on malformed or lane-duplicating entries, never on removal | **detected, not enforced** — `[K1]` `systems_check.py:2154,2166` enumerates every cited-and-absent artifact missing from the register, but via `f.warn` | **NEITHER (both directions non-failing)** | **4 declared / 5 in the live cited-and-absent population** — 1 unclassified (`emc-prior-art-fulltext-screen.json`, WARN) + 1 lane-derived (`valb-triangle-chem.json`, INFO). The file's own `_why` claims "It cannot silently grow" — measured: it grows with a WARN |
| R6 | `systems/systems_check.py:1289` `DOC_SKIP` | 5 prefixes | partial — `systems/tests/test_systems_check.py:795` pins `"archive/"` in it | N/A by construction (exclusion list over `os.walk`; new content is covered unless explicitly excluded) | **SHRINK (partial) / GROWTH N-A** | 1 of 5 entries pinned |
| R7 | `systems_check.py:1306` `ID_SKIP` | 4 | partial — `test_systems_check.py:796-798` pins `"archive/"` absent and requires ≥1 archived doc actually scanned | N/A (exclusion list) | **SHRINK (partial) / GROWTH N-A** | 1 of 4 entries pinned |
| R8 | `systems_check.py:1425` `TRANSIENT_DIRS` | 12 (11 distinct; `node_modules` listed twice) | partial — `test_systems_check.py:1992-2002` pins `.claude`, asserts `_walk_md` routes through `_is_transient`, and asserts no yielded path is under `.claude/` | N/A (exclusion list) | **SHRINK (partial) / GROWTH N-A** | 1 of 12 entries pinned |
| R9 | `research/manuscripts/lint_style.py:37` `TARGETS` (the single hand-list of "submission texts") | 13 | `research/manuscripts/tests/test_submission_residue_guard.py:246` — `assert set(style.TARGETS) <= set(corpus)` | **none** | **SHRINK ONLY** | **8/26** of `systems/graph/publications.json` `document.file` entries; 13/187 tracked manuscript `.md`. 18 modelled publication documents are outside it, incl. `degrader/nr4a3-degrader-paper.md`, `neoantigen/fusion-junction-neoantigen-paper.md`, `tcip/tcip-induced-interface-preprint.md`. Note `lint_readability.py:293-298` and `lint_submission_residue.py:200,225` both re-use this one list, so its gap propagates to three gates |
| R10 | `research/manuscripts/lint_claims.py:75` `DEFAULT_TARGETS` | 15 literal → **137 effective** | `systems/parser_guard.py:145-171` — parses the literal block, fails on a nonexistent path, and asserts `PLAN_DOC` is a target | **yes, by construction** — `:248-251` unions `systems/views/L[012]-*.md` by glob and `:285` unions every `publications.json` `document.file`; `[B4]` guarantees the glob cannot resolve empty | **BOTH** | 137 effective targets, 36 under `research/manuscripts/`; auto-covers all 26 modelled publication documents. This is the repository's own worked answer to the W47/W51 shape, and its comment says so: *"coverage must follow the model, not a list someone remembers to extend"* |
| R11 | `research/manuscripts/lint_changed_prose.py:57` `DEFAULT_TARGETS` | 6 (4 `.md`) | none found | none | **NEITHER** | 4/187. ⚠ Also `scripts/preflight.sh:661` runs it as `... \|\| true` — the verdict is discarded, the same `\|\| true` shape W47 found on the ensemble workflow |
| R12 | `research/autonomy/amendment_guard.py` `GOVERNED` | 17 patterns | none — `is_governed` is pure `fnmatch`, no existence check; no test asserts membership | none — population ("every bar in the repository") is not mechanically computable | **NEITHER** | not computable. Its own comments record the class: `preflight.sh`, `affected_tests.py` and `.claude/hooks/**` were each found missing *by a human walking through the hole*, in 2026-09-02 and later |
| R13 | The prose enumeration of preflight gates (docs) vs `scripts/preflight.sh`'s actual gates | 17 gates | **yes** — `systems_check.py:1674,1691-1705` `[P1]` errors when the enumeration lists a gate preflight no longer runs | **yes, same family** — `:1649` errors on a count mismatch, `:1674` on a listed-set mismatch in either direction | **BOTH** | 1:1 by construction. The reference implementation of a bidirectional registry guard |
| R14 | `systems/parser_guard.py:190-197` `check_registry` path list | 6 | itself (`:196-198`) | none | **SHRINK ONLY** | 6 declared; population = graph JSONs present = **6/19** files in `systems/graph/` |
| R15 | `submission-residue-baseline.json` / `readability-baseline.json` / `lint_asymmetry.py:324 BASELINE` | ratchets | stale rows reported (`lint_submission_residue.py:450,463`) but non-failing | **yes, by construction** — findings are discovered by walk/corpus, and a NEW unbaselined finding errors | **GROWTH by construction** | population discovered, not declared — the correct shape |

**Count of registries that are shrink-guarded but not growth-guarded: 4** on the strict reading (R1, R2, R9, R14 — inclusion registries where a growth guard is constructible and absent). **7** if the three exclusion-list constants R6–R8 are counted, but they should not be: an exclusion list is opt-out, so corpus growth is covered by default, which is exactly why they do not exhibit the defect.

Three findings beyond the matrix:

1. **The defect is a property of inclusion registries, not of registries.** Every registry that enumerates *what to check* (R1, R2, R9, R11, R14) is blind to corpus growth; every registry that enumerates *what to skip* (R6–R8) or that derives its set from a model or a walk (R10, R13, R15) is not. The repository has both patterns and has already written down which is correct (`lint_claims.py:241-242`).
2. **The population is computable for R9 and it is not being used.** `publications.json` `document.file` + `level: L3` is exactly the machine-readable definition of "submission text" that `lint_style.TARGETS` is a hand-copy of; `lint_claims` already joins to it. The 8/26 ratio is measured, not estimated.
3. **`artifact-refs.json`'s own `_why` states a growth guarantee its check does not deliver.** *"[K1] enumerates anything that is missing from it. It cannot silently grow."* It does enumerate — at WARN. Measured live: one unclassified member of the population, no exit-code consequence.

## Validation evidence

RUN, live tree, `python3 3.11.x` at `/usr/local/bin/python3`, cwd `/home/user/Rare-cancers`:

* `python3 systems/parser_guard.py` → `parser_guard: 5 dependency groups checked · every registered parser can still find its input`, **rc 0**.
* `python3 scripts/tier_budget.py --check` → `ok commit-loop 1466/1500`, `ok modalities 7247/7500`, `ok paper-guards 966/1000`, **rc 0**.
* `timeout 600 python3 systems/systems_check.py --check | grep '\[K1\]'` → 1 INFO, 1 WARN of the artifact-disposition kind (quoted in R5), plus 7 unrelated link ERRORs all under the untracked campaign `inputs/` and `reports/` (consistent with W41/W31b; not attributed here).
* In-process measurement (import, no mutation): `lint_claims.DEFAULT_TARGETS` = 137 (36 under `research/manuscripts/`); `lint_style.TARGETS` = 13; `publications.json` `document.file` = 26; `|TARGETS ∩ docs|` = 8.
* `git ls-files 'research/manuscripts/**.md' | wc -l` → **187** (independently reproduces W51's denominator).
* `os.walk` replication of the budget test: budgeted dirs 5, found `tests/` dirs 7, missing = the two `inputs/source-index/**` dirs (reproduces W41).
* `python3 -c` over `pinned-figures.json`: `targets` 29, `must_appear_in`+`file` union 14, union of all declared paths 31.

PROPOSED (NOT RUN), and deliberately not authored as code per my instructions: no repair, patch, gate or test was written; no registry gained an entry; no guard was weakened or reordered; no budget widened. No mutation experiment was needed, so no `cp -a` copy was made.

## Limitations

* "Population" is only defined for 8 of 15 rows. For R2, R12 and R15 the population is a human category (a document restating a pinned quantity; a bar; a residue) and no ratio is computable — those rows are **UNKNOWN**, not zero.
* I classified by reading the checks and by three live runs, **not** by mutation. A shrink guard I marked absent could in principle exist in a module I did not open; the census is over the constant/registry space I could enumerate with the key-literal greps above, and I claim completeness only over that space.
* `[K1]`/`[K2]` behaviour was observed against a working tree containing the untracked campaign `inputs/` directory; the K1 counts for tracked content specifically are UNKNOWN at a clean checkout.
* Coverage ratios are measured at HEAD `8a667406`→`56f355f6` and are not stable quantities — the tier-budget 5/7 in particular is an artefact of an untracked directory and will read 5/5 in CI.
* Nothing here is a scientific claim; no patient, efficacy, safety or clinical-readiness content is involved.

## Stop condition

Set up front: *return as soon as every named candidate registry plus every registry found by the key-literal sweep is classified, with a checking file:line for each guard that exists and a coverage ratio wherever the population is computable.* **MET.** No repair proposed, no registry entry added, scratch directory deleted.

## Tool-call and wall-clock count actually used

26 tool calls; ~4 minutes wall clock (04:48:35Z → 04:52:17Z). Under the ~40/~40 target; returning early rather than padding.

## Next concrete action

One successor, for a human or the coordinator to route — **not** performed here: decide whether `lint_style.TARGETS` should keep being a hand-list at all, given that `systems/graph/publications.json` `document.file` (+ `level: L3`) is the same set expressed in the model and `lint_claims.py:285` already joins to it. The measured gap is 18 modelled publication documents outside the list, and because `lint_readability.py:297` and `lint_submission_residue.py:225` both import that one list, closing it would move three gates at once. That is a change to what three gates cost and to what they refuse, so it is a decision, not a cleanup — it needs the same governed-declaration treatment `tier-budgets.json` documents, and it is out of scope for a read-only census worker.
