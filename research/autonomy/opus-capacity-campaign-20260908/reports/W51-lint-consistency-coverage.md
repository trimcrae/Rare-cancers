<!-- collected 2026-09-08T04:45:25Z by campaign coordinator; agent id a640add59be361fdc; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a640add59be361fdc.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Done. `/tmp/claude-0/w51/` is deleted.

## Worker

W51, campaign OPUS-CAPACITY-CAMPAIGN-20260908, lane: preflight-gate audit.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; re-run at end was identical):

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
GLOBAL_AGENT_NO_PROXY=<same no_proxy list>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 …
NO_PROXY=<same list>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same list>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**State.** Start `date -u` = `Tue Sep  8 04:40:38 UTC 2026`, HEAD `408b676aec3625a36917755662516232a27a1278`, `git status --porcelain` **empty**. End `date -u` = `Tue Sep  8 04:42:48 UTC 2026`, HEAD `3e286595023949f75eddd09da9aff36ca58c3f00`, `git status --porcelain` **empty**. HEAD advanced by coordinator commits during my run (expected per COMMON-BRIEF §1); I performed no git write.

## Question

`research/manuscripts/lint_consistency.py` is a `scripts/preflight.sh` gate whose name promises "manuscript consistency" linting. What does it actually check, over what file set, and what does its name lead a reader to believe it checks that it does not?

## Prior-work check

- `rg -n -i "lint_consistency" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'` — 30 hits. Two are **genuine prior art on this exact question and I am extending, not replaying, them**:
  - `research/manuscripts/map-audit-manuscript.md:782-787` — records that the program map "**is** in `lint_consistency.py`'s target list (`pinned-figures.json` → `targets`, 12 files) and passes at 0 ERROR", and that "**`lint_consistency` at 0 ERROR does not cover F1, F10 or F18**". That is a coverage-gap finding for *three specific findings in one file*.
  - `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-decline-review-integrity-2026-08-10.md:93-94,343` — records "0 ERROR, 17 targets", that `pinned-figures.json` "registers **zero** pinned figures, derivations or superseded values for [that manuscript]", and that "**the SI is not a target at all**". A file-set gap for one manuscript.
  - Neither enumerates the rule set with line numbers, neither computes the repository-wide manuscript file-set gap, and **neither performs an injection experiment**. Note both cite stale target counts (12 and 17); the registry now declares **29**.
  - `STRATEGY.md:90` (Appendix A row 21) is a measured prior negative I confirm below: "`lint_consistency.py` did not catch either, because both were self-consistent prose".
- `git ls-files | rg -i "lint_"` — 19 files; `research/modalities/tests/test_lint_consistency.py` exists (its own unit tests, not a coverage audit).
- `CLOSED-WORK.md` read in full — nothing here is a closed/owned item. PUB-ASO belongs to the submission owner; I did not edit it (my one PUB-ASO-adjacent observation is read-only file-set arithmetic).
- Campaign sibling reports were excluded from the search per COMMON-BRIEF §3; `reports/W25-*` was not read.

## Method and inputs

- Read `research/manuscripts/lint_consistency.py` (648 lines) **in full**, from the live checkout at HEAD `408b676`.
- Enumerated `research/manuscripts/pinned-figures.json` programmatically (stdlib `json`), and `git ls-files research/manuscripts` for the manuscript denominator.
- `grep -n "glob\|os.walk\|rglob\|listdir" research/manuscripts/lint_consistency.py` → **no matches, exit 1**.
- Mutation experiments in `cp -a /home/user/Rare-cancers /tmp/claude-0/w51/tree` only. Each injection applied with `sed -i`, linter run, then reverted with `git checkout -- <file>` **inside the scratch copy**. Six injections.
- Python 3 (`/usr/local/bin/python3`), stdlib only; no network, no paid API, no GPU. `scripts/preflight.sh` was **not** run.

## Result

### What it actually implements — five rule families, all registry-driven

| Rule | Entry point | What it checks | Registry entries now declared |
|---|---|---|---|
| **D** derivations | `check_derivations` `lint_consistency.py:270` | D1 `:293` tool JSON's own total vs its own ladder rows; D2 `:308` registry `expect_*` vs tool + declared non-tool stages; D3 `:325` the `$mid ($low–high)` string must appear verbatim in each `must_appear_in` doc | **1** (`ladder_total`, 3 docs) |
| **A** artifact figures | `check_artifact_figures` `:400`, flattened path `_check_flattened` `:373` | a doc line (or flattened window) matching a declared regex `context` must contain a number within `tolerance` of `artifact:key` | **99** |
| **T** table completeness | `check_table_completeness` `:216` (`_section_lines` `:465`) | every priced stage has a table row `:504`; `**TOTAL**` row matches the tool `:527`; printed bolded rows sum to printed total `:541` | **1** (`bid-strategy.md` `## 6. REPRICED LADDER`) |
| **X** subset | `check_subsets` `:556` | `subset_pattern` matches must be a subset of `superset_pattern` matches, in **one file**; both patterns must match something `:571` | **1** (`strategy_spine_cum`, `systems/views/plan.md`) |
| **S** superseded | `check_superseded` `:590`, clearing logic `is_cleared` `:177` | a declared retired-value regex may appear only if cleared by a proximity marker (`_WINDOW_BACK=2`/`_WINDOW_FWD=1` lines **and** `_WINDOW_CHARS=200` chars, `:112`), a negator (`_locally_negated` `:151`), or an *about-supersession* enclosing heading (`_HEADING_CLEAR_PHRASES` `:165`) | **81** patterns × **29** targets |

Plus five "the check itself is broken" guards, which are the module's real strength: `D-tool-json-missing` `:274`, `D-target-missing` `:334`, `A-artifact-missing` `:404`/`A-key-missing` `:414`/`A-target-missing` `:430`, `T-file-missing` `:220`/`T-section-missing` `:225`/`T-no-total-row` `:530`, `X-pattern-found-nothing` `:571`, `S-target-missing` `:595`.

### The file set — enumerated, never discovered

**There is no glob and no directory walk** (grep above, exit 1). Every file read is a literal path string in `pinned-figures.json`. Three disjoint sets:

- **S scans 29 files** (`targets`), including 4 `.claude/skills/*/SKILL.md`, `CLAUDE.md`, `CLAUDE-history.md`, `STRATEGY.md`, 4 `research/compute/*.md`, `systems/views/plan.md`, one `.json`, and **14 `.md` files under `research/manuscripts/`**.
- **A/D/T/X read only their own `must_appear_in`/`file` lists**, which add 2 prose files the S rule never scans: `research/manuscripts/aso/fusion-junction-aso-cover-letter.md` and `research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md` (plus `research/modalities/vast-ladder-repricing.json` as an input).
- **Union across all five rules: 31 paths, of which 16 are `research/manuscripts/*.md`.**

**Manuscript files OUTSIDE the set: 171 of 187 tracked `research/manuscripts/**/*.md` (91.4%).** They include entire programs with no rule at all — `research/manuscripts/tcip/` (3 files), `research/manuscripts/surface-targets/` (11), `research/manuscripts/repurposing/`, `research/manuscripts/fusion-output/`, all `*-redteam-*`, `*-review-response-*`, `*-cover-letter*` and `*-si*` documents except the three named above, `SUBMISSION-PACKET.md`, `README.md`, and — as the mtap-prmt5 integrity note already recorded — `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md` is a target while its SI is not. (Full 171-item list was produced in scratch; the categories above are the substance. `research/manuscripts/aso/fusion-junction-aso-{journal-article,research-article,supplementary-information}.md` **are** inside the set — the PUB-ASO core is covered; its 10+ redteam rounds, journal-references and journal-tables files are not.)

### The injection experiment

Baseline in the scratch copy: `lint_consistency: 0 ERROR across 29 target file(s)`, **exit 0**.

| Implied rule (from the name "manuscript consistency lint") | Implemented? | Caught in experiment? | Evidence |
|---|---|---|---|
| A **claim contradicting a pinned value**, at a location the registry declares | **YES** (rule A) | **CAUGHT** | E3a: `$84.49`→`$84.99` at `nr4a3-program-map.md:664` → `ERROR [A-figure-mismatch] realised_spend_ledgered: this line quotes [84.99] but research/modalities/realised-spend.json:realised_usd_ledgered is $84.49`, **exit 1** |
| A **superseded value restated unmarked**, in a declared target | **YES** (rule S) | **CAUGHT** | E4: inserted `The whole gated ladder prices out at $128 mid-range.` → `ERROR [S-ladder_total_128] superseded value '$128' stated without marking it superseded`, **exit 1** |
| The **same quantity stated at two different values** — the failure the docstring at `:7-8` names as the reason the file exists | **NO** (no rule compares two in-document statements of one quantity) | **NOT CAUGHT** | E1: same target file asserting "screened **412** candidate compounds in stage 1" and, 2 lines later, "stage 1 screened **907** candidate compounds" → `0 ERROR`, **exit 0** |
| A **stale cross-reference** (dead anchor, dead file link) | **NO** (no link, anchor or heading resolution anywhere in the module) | **NOT CAUGHT** | E2: `[the dependency graph](#4--the-dependency-graph-THAT-NO-LONGER-EXISTS)` + `[the SI](…/nr4a3-degrader-paper-SI-DELETED.md)` → `0 ERROR`, **exit 0** |
| A **claim contradicting a pinned value** stated *anywhere else* than the declared `context` | **NO** | **NOT CAUGHT** | E3b: `Cumulative realised spend for the program stands at $12.00 to date.` inserted in the same file that carries the pinned $84.49/$133.38 → `0 ERROR`, **exit 0** |
| The two **caught** defect kinds, in a manuscript outside the registry file set | n/a — rule exists, file does not | **NOT CAUGHT** | E5: the *byte-identical* E3a and E4 injections appended to `research/manuscripts/tcip/tcip-induced-interface-preprint.md` → `0 ERROR`, **exit 0** |

E1 independently reproduces the repository's own recorded finding at `STRATEGY.md:90`: "`lint_consistency.py` did not catch either, because both were self-consistent prose".

## The coverage gap, stated precisely

`lint_consistency.py` is not a manuscript consistency linter. It is a **numeric-registry conformance checker**: it verifies that 102 hand-registered assertions (1 derivation + 99 artifact figures + 1 table + 1 subset) still hold at 33 declared file locations, and that 81 hand-registered retired values do not reappear unmarked across 29 declared files. It does not read a manuscript for consistency; it reads a manuscript **for the strings the registry told it to look for**. The module's own docstring is honest about this — its title is "Cross-document *numeric-consistency* linter for the research plan and its companion docs", and `pinned-figures.json`'s `_README` calls registration "part of making a correction". The name on the preflight step is what over-promises.

Three independent gaps, each measured:

1. **Rule gap.** Two of the three inconsistency classes the name implies are unimplemented. There is no cross-statement equality check (one quantity, two prose values, no registry entry — E1) and no reference resolution at all (E2). Rule X is the closest thing to a general consistency rule and it is instantiated **once**, over one file, on hand-written regexes.
2. **Locus gap.** Even where a value *is* pinned, coverage is one regex-matched location, not the document. The same file may contradict the same pinned artifact in prose and pass (E3b). The registry's own `_artifact_figures_note` and `_check_flattened:373` warn about the weaker sub-case (a non-capturing pattern vouched for by a coincidental neighbour); E3b is the stronger case — text the pattern never reaches.
3. **File-set gap, the largest.** 171 of 187 tracked manuscript `.md` files (91.4%) are outside every rule. E5 shows this is not a soft gap: injections the linter provably catches in a target file are invisible one directory over. Adding a manuscript to the repository adds **zero** linting; it must be typed into `pinned-figures.json` first.

A consequence worth flagging without proposing a repair: **`lint_consistency: 0 ERROR across 29 target file(s)` is a true statement that reads as a stronger one.** The printed denominator is the S-rule target count (`main:640`), not the rule-weighted coverage, and it is quoted as an audit result in at least four repository documents. `systems/parser_guard.py:119-139` already guards the registry against *shrinking* (it fails if a declared target path vanishes); nothing observes whether the registry has *grown* with the corpus.

## Validation evidence

All **RUN**. Environment: this container, `/usr/local/bin/python3`, no network, stdlib only.

- `python3 research/manuscripts/lint_consistency.py` in the untouched `cp -a` copy → `lint_consistency: 0 ERROR across 29 target file(s)`, **exit 0**.
- Six injections, each applied then reverted in the scratch copy; verbatim key output and exit codes are in the table above. Exit codes observed: E3a **1**, E4 **1**, E1/E2/E3b/E5 **0**.
- `grep -n "glob\|os.walk\|rglob\|listdir" research/manuscripts/lint_consistency.py` → no output, **exit 1**.
- **Write isolation confirmed:** `diff -rq --exclude=.git /home/user/Rare-cancers /tmp/claude-0/w51/tree` reported exactly two differences, **both inside `research/autonomy/opus-capacity-campaign-20260908/`** (`COMMON-BRIEF.md` differs; `reports/W41-campaign-inputs-gate-footprint.md` present only in the live tree). Those are the coordinator's commits between HEAD `408b676` (when I copied) and `3e28659` (end), i.e. the direction of the difference is the live tree gaining content, not losing it. `git -C /home/user/Rare-cancers status --porcelain` was **empty at start and at end**. No file under `/home/user/Rare-cancers` was written, no git write operation was run.
- Scratch deleted: `rm -rf /tmp/claude-0/w51` executed and confirmed absent from `ls /tmp/claude-0/`.
- **PROPOSED (NOT RUN), and deliberately not run:** `scripts/preflight.sh` (dispatch forbade it); `research/modalities/atr_hrd_sarcoma_series.py` (never invoked, in any form); `research/modalities/tests/test_lint_consistency.py` (would have added the module's own unit-test verdict, but is not needed for a coverage question and would have cost calls against my stop condition).

## Limitations

- The injections are **representative, not exhaustive**. "Not caught" is proven for the six specific texts I injected; a differently-worded stale cross-reference is still not caught (no code path exists), but a differently-worded numeric contradiction could coincidentally trip an unrelated S pattern. E1/E2/E3b/E5 establish that the *rule families are absent or file-scoped*, which I argue from source reading as well as from the runs.
- The 171-file "outside" count uses `git ls-files research/manuscripts` + `.md`. Manuscript content living elsewhere (`research/modalities/*.md`, `systems/views/`, `archive/`) is not in that denominator; two `research/modalities` files *are* S targets. The 91.4% figure is therefore specific to `research/manuscripts/**/*.md`.
- I did not evaluate whether the absent rules *should* exist, and per dispatch I authored no repair, patch, gate or test. Rules D/A/T/X/S each carry long in-source rationale (notably `_WINDOW_CHARS` at `:86-112`) recording false-clear incidents that a broader rule would reintroduce; a "wider linter" is not self-evidently better and I make no such recommendation.
- This is a static + injection audit of one module at one HEAD. It says nothing about the scientific correctness of any manuscript, and nothing computational here bears on EMC efficacy, safety, selectivity or clinical readiness.
- No content-policy refusal occurred in this run.

## Stop condition

**Set up front:** stop once (a) every rule is enumerated with `file:line`, (b) the exact file set is computed and the outside-set manuscript list produced, and (c) one injection of each name-implied inconsistency kind has been run and its catch/no-catch recorded — or at ~40 tool calls / ~40 minutes, whichever came first.

**MET**, early, on all three conditions.

## Tool-call and wall-clock count actually used

**12 tool calls** (target ~40). **Wall clock ~2 minutes 10 seconds**, `04:40:38Z` → `04:42:48Z` (target ~40 min). Returning early rather than padding.

## Next concrete action

One successor task, in this lane, for whoever owns gate semantics: **measure whether the same enumerate-don't-discover pattern holds for the other four preflight manuscript linters** — `lint_claims.py`, `lint_citations.py`, `lint_style.py`, `lint_submission_residue.py` — by computing each one's actual file set the same way (source read for glob/walk, plus its registry if it has one) against the 187-file manuscript denominator. If those four *do* glob, then `lint_consistency.py`'s 16/187 is an isolated registry design and the honest fix is a name change; if they are all registry-driven, the repository has a systemic 91% manuscript blind spot in its commit gate and that is a single finding worth one owner. This is a bounded read-only measurement, roughly the size of this run. I am **not** proposing a repair to `lint_consistency.py` and did not author one.
