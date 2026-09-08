<!-- collected 2026-09-08T04:54:43Z by campaign coordinator; agent id ade8f4d707dae2fe4; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ade8f4d707dae2fe4.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

W59, campaign OPUS-CAPACITY-CAMPAIGN-20260908, lane: preflight-gate audit (W51's named successor).

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED** — I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at **start**:

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
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 … (proxy/truststore flags)
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

At **end** the same command's output was identical (re-checked keys: `AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_EFFORT=medium`, `ANTHROPIC_BASE_URL=https://api.anthropic.com`, `CLAUDE_CODE_VERSION=2.1.42`).

**State.** Start `date -u` = `Tue Sep  8 04:47:15 UTC 2026`, HEAD `8a667406e875ae99c7d50347b2e895a177fcb048`, `git status --porcelain` **empty**. End `date -u` = `Tue Sep  8 04:51:51 UTC 2026`, HEAD `56f355f65b7b3e47aeb434ac02edf4cf049f40f3`, `git status --porcelain` **empty (0 lines)**. HEAD advanced by coordinator commits during the run (expected, COMMON-BRIEF §1); I ran no git write operation.

## Question

Does `lint_consistency.py`'s enumerate-don't-discover pattern (W51: 16 of 187 tracked `research/manuscripts/**/*.md`, no glob, no walk) hold for the other manuscript-facing `scripts/preflight.sh` gates — `lint_claims.py`, `lint_citations.py`, `lint_style.py`, `lint_submission_residue.py`, and any other manuscript gate in that script? For each: source read for discovery calls, actual file set computed, coverage against the same 187-file denominator, and — where a linter discovers — an injection into an *unlisted* manuscript to verify the discovery is real.

## Prior-work check

- W51's report read in full; its result is taken as given and **not re-derived** (COMMON-BRIEF "Known, measured" §, `lint_consistency.py` bullet). COMMON-BRIEF, CORPUS-CONTEXT.md, CLOSED-WORK.md read in full.
- `grep -n 'glob\|os.walk\|rglob\|listdir\|ls-files\|iterdir\|scandir'` run over all eight lint modules (evidence below) — this is the primary discovery measurement, not a novelty search.
- COMMON-BRIEF already records one adjacent fact I confirm rather than replay: *"`lint_citations.py:187` and `emc_systems_map_check.py:351` use `git ls-files --cached --others --exclude-standard`"* (W41). W41 used that to argue those gates cannot see `inputs/`; **nobody had computed what it means for manuscript coverage**, which is this run's contribution.
- `reports/W25-*` not read, not referenced. PUB-ASO files were read and (in the scratch copy only) never modified.

## Method and inputs

- Live checkout `/home/user/Rare-cancers` at HEAD `8a66740` → `56f355f`. Denominator: `git ls-files 'research/manuscripts/*' | grep '\.md$'` = **187**, identical to W51's.
- Preflight gate inventory: `grep -n 'lint_\|\.py\b' scripts/preflight.sh`. Manuscript-facing, exit-coded gates: `lint_consistency` (`:586`), `emc_systems_map_check --check` (`:627`), `lint_claims` (`:650`), `lint_citations` (`:684`, which also runs `lint_citation_types.py`), `lint_style` (`:700`), `lint_submission_residue` (`:1437`). Advisory (verdict discarded): `lint_changed_prose` (`:661`, `|| true`), `lint_readability --report` (`:713`, `|| true`).
- File sets computed by **importing each module and reading its own target expression** (`lint_claims.DEFAULT_TARGETS`, `lint_style.TARGETS`, `lint_submission_residue.targets()`, `lint_citations._tracked()` + `PROSE_SUFFIXES`), not by re-implementing them.
- All injections in `cp -a /home/user/Rare-cancers /tmp/claude-0/w59/tree` **only**; each reverted by restoring a pre-injection copy, with `git status --porcelain` inside the scratch tree confirming a clean revert each time.
- `/usr/local/bin/python3` (3.11), stdlib only. No network, no paid API, no GPU. `scripts/preflight.sh` **not run**. `atr_hrd_sarcoma_series.py` never invoked.

## Result

### Discovery mechanism, read from source

`grep -n 'glob\|os.walk\|rglob\|listdir\|ls-files\|iterdir\|scandir'`:

| Module | Hits | Mechanism |
|---|---|---|
| `lint_claims.py` | `:65 import glob`, `:250 glob.glob(.../systems/views/L[012]-*.md)` | **hybrid** — hand-list + views glob + `publications.json` `document.file` |
| `lint_citations.py` | `:187 git ls-files --cached --others --exclude-standard` | **whole-repository discovery** |
| `lint_style.py` | **none** | pure hand-list `TARGETS` (`:37`) |
| `lint_submission_residue.py` | **none** | derived from four committed declarations (`targets()` `:190-255`) |
| `lint_readability.py` | none | imports `lint_style.TARGETS` (`:297-298`) |
| `lint_changed_prose.py` | none | git-diff-scoped (`:114`, `main` `:224`) |
| `lint_citation_types.py` | none | runs inside `lint_citations`' scan |
| `lint_asymmetry.py` | `:675 os.walk` | not a preflight gate |
| `emc_systems_map_check.py` | `:351 git ls-files --cached --others --exclude-standard` | whole-repository discovery |

### Coverage against the 187-file denominator — all rows PRIMARY (measured this run except where marked)

| Gate | Preflight status | Actual file set | `research/manuscripts/**/*.md` covered | % of 187 |
|---|---|---|---|---|
| `lint_citations.py` (+`lint_citation_types`) | exit-coded `:684` | 7,824 tracked+untracked paths → **789 `.md` scanned** | **187** | **100%** |
| `emc_systems_map_check.py --check` | exit-coded `:627` | same `ls-files` discovery | whole tree (not per-manuscript prose linting) | n/a |
| `lint_claims.py` | exit-coded `:650` | **137 targets** (36 manuscripts + 1 `research/modalities` + 100 `systems/views`) | **36** | **19.3%** |
| `lint_submission_residue.py` | exit-coded `:1437` | **34 outgoing documents** | **34** | **18.2%** |
| `lint_consistency.py` | exit-coded `:586` | 31 paths (W51, given) | **16** | **8.6%** |
| `lint_style.py` | exit-coded `:700` | **13 `TARGETS`** (prints "15 file(s)": +2 non-manuscript figure sources) | **13** | **7.0%** |
| `lint_readability.py` | advisory `\|\| true` | `lint_style.TARGETS` | 13 | 7.0% |
| `lint_changed_prose.py` | advisory `\|\| true` | whatever the diff touches | unbounded but **verdict discarded** | n/a |

**Union of the five registry/list-driven manuscript gates** (`lint_claims` ∪ `lint_style` ∪ `lint_submission_residue` ∪ `lint_consistency`) over the denominator: **41 of 187 (21.9%). 146 manuscripts (78.1%) are in none of them** — including `README.md`, `SUBMISSION-PACKET.md`, every `*-redteam-round*`, `fusion-junction-aso-cover-letter.md`, `fusion-junction-aso-guard-coverage-audit.md`, `aso-delivery-evidence-2026-08.md`.

### The verdict W51 framed — the binary does not hold; the honest answer is a third one

**Neither branch of W51's dichotomy is correct as stated.** The four are not all registry-driven, so this is **not** a blanket systemic blind spot; but `lint_consistency.py`'s 16/187 is **not an isolated registry design** either — three of the other five prose gates are the same shape, two of them *lower* than 16 (`lint_style` 13, `lint_readability` 13) and two comparable (`lint_claims` 36, `lint_submission_residue` 34).

The correct statement is a **split by defect class, not by gate**:

* **Fabricated/unanchored citation identifiers are checked over 100% of manuscripts**, with an exit code, by discovery (`lint_citations._tracked()`). Adding a manuscript adds citation linting automatically. Verified by injection below.
* **Every other manuscript defect class the commit gate checks — over-claiming (R1–R5), style register, unverified-output residue, numeric-registry conformance, readability — is scoped to a hand-list or a declaration registry, covering 21.9% of manuscripts at most.** Adding a manuscript adds *none* of them; it must be typed into `pinned-figures.json`, `lint_style.TARGETS`, `lint_claims.DEFAULT_TARGETS`, or pointed at by a `publications.json` endpoint / `build_submission_pdf.PAPERS` / `submission-metrics.json` row.

Two mitigations worth recording with that, both read from source:
* `lint_claims` and `lint_submission_residue` are **model-driven, not hand-typed**: `lint_claims._publication_documents()` (`:266-283`) and `lint_submission_residue.targets()` (`:190-255`) derive from `publications.json`, `lint_style.TARGETS`, `build_submission_pdf.PAPERS` and `submission-metrics.json`, and residue's docstring states the property explicitly ("a paper cannot join the outgoing set without joining this gate in the same commit"). Their gap is that a manuscript that is *not* an endpoint or a submission text is outside by design — which is a defensible scope for a submission gate, unlike a hand-list.
* `lint_claims.py:249-252` contains the repository's own written statement of the principle W51 is pointing at: *"⚠ GLOBBED, NOT LISTED. A hand-typed list of 50 paths would leave the next new route outside the linter by default, which is this failure mode reproduced rather than fixed: coverage must follow the model, not a list someone remembers to extend."* That principle was applied to `systems/views/` and to publication endpoints and **was not applied to the manuscript corpus**, to `lint_style.TARGETS`, or to `pinned-figures.json`.

### Injection experiments — all in `/tmp/claude-0/w59/tree`, all reverted

Scratch baselines: `lint_claims` `0 ERROR, 178 WARN across 137 file(s)` exit **0**; `lint_style` `0 ERROR across 15 file(s)` exit **0**; `lint_submission_residue` `34 outgoing document(s), 5 finding(s), 5 baselined, 0 new` exit **0**; `lint_citations` exit **1** at baseline (pre-existing red, caused by campaign-report content and 12 PubMed type disagreements — so its result is read by *identifier name*, not by exit code alone).

Unlisted manuscript used throughout: `research/manuscripts/aso/aso-delivery-evidence-2026-08.md` (in **no** gate's set except `lint_citations`).

| # | Injection | Gate | Outcome | Verbatim key output |
|---|---|---|---|---|
| I1 | fabricated `PMID 41999901` + `doi:10.9999/w59.fake.00001` into the **unlisted** manuscript | `lint_citations` | **CAUGHT**, exit 1 | `::error::UNANCHORED DOI 10.9999/w59.fake.00001 — appears only in prose (research/manuscripts/aso/aso-delivery-evidence-2026-08.md) and is not in the citation-provenance ledger` and the matching `UNANCHORED PMID 41999901` line; sweep count rose 1485→1487 |
| I1 | same injection | `lint_claims` / `lint_style` / `lint_submission_residue` | **NOT CAUGHT**, exit 0 each; counts unmoved (137 / 15 / 34 files) | no mention of the file in any output |
| I2 (positive control) | `"…is safe and effective in patients with extraskeletal myxoid chondrosarcoma and cures the disease"` into two **covered** files | `lint_claims` | **CAUGHT**, exit 1 | `repurposing-hypotheses.md:650: ERROR [R2-safe] 'is safe'`, `:651: ERROR [R2-treats-cures] 'cures'`, same pair in `tcip-induced-interface-preprint.md:295-296`; `4 ERROR, 178 WARN across 137 file(s)` |
| I3 (paired) | byte-identical banned-phrase line inserted after the first `##` heading of a **covered** (`endpoint/response-endpoint-indolent-tumours.md`) and the **unlisted** file | `lint_style` | **CAUGHT in the covered file only**, exit 1 | `5 ERROR across 15 file(s)`; five `[banned-phrase]` errors all at `response-endpoint-indolent-tumours.md:65` (`'that is the point'`, `'deliberately'`, `'It is worth noting'`, `'worth noting'`, `'to be clear'`); the unlisted file is not in the output at all |
| I4 (paired) | byte-identical `As an AI language model, I hope this helps.` appended to the same covered and unlisted files | `lint_submission_residue` | **CAUGHT in the covered file only**, exit 1 | `::error::…response-endpoint-indolent-tumours.md:738 UNVERIFIED-OUTPUT RESIDUE (ai-self-reference) — 'As an AI' is the assistant naming itself…` plus a `(handover)` error; `34 outgoing document(s), 7 finding(s), 5 baselined, 2 new` |

I2/I3/I4 are the controls that make the negatives load-bearing: the identical text is caught inside the set and invisible one directory over, so "not caught" is a **file-set** result, not a weak injection. (A methodological note found in passing: an appended-at-EOF `lint_style` injection produced **0 ERROR** even in a covered file — the appended text landed in a region the body scanner skips. Injections into `lint_style` must go into the body, after a `##` heading.)

## Validation evidence

All rows above are **RUN**. Environment: this container, `/usr/local/bin/python3` (3.11), no network, stdlib only, all execution inside `/tmp/claude-0/w59/tree` for injections and inside the live checkout for read-only enumeration.

- `grep -n 'glob\|os.walk\|rglob\|listdir\|ls-files\|iterdir\|scandir' lint_style.py` → no output, exit 1. Same for `lint_submission_residue.py`, `lint_changed_prose.py`, `lint_citation_types.py`.
- Enumeration run: `python3 -c` importing `lint_claims`, `lint_style`, `lint_submission_residue`, `lint_citations` → `lint_claims total targets: 137 … under research/manuscripts: 36`; `lint_citations tracked+others: 7824 prose-scanned: 789 → manuscripts covered: 187 / 187`; `lint_style TARGETS: 13`; `residue targets: 34`; `union of 4 registry-driven gates over manuscripts: 41`, `uncovered: 146`.
- Every injection was reverted from a pre-injection copy and confirmed by `git status --porcelain` inside the scratch tree printing nothing before the next run.
- **Write isolation:** `git -C /home/user/Rare-cancers status --porcelain` **empty at start and end (0 lines)**. `diff -rq --exclude=.git /home/user/Rare-cancers /tmp/claude-0/w59/tree` showed differences only in (a) `research/autonomy/opus-capacity-campaign-20260908/` — `COMMON-BRIEF.md` differing and eight coordinator reports (`W03j`, `W34c`, `W44`, `W49`, `W52`–`W55`) present only in the live tree, i.e. the live tree **gaining** content after my copy — and (b) untracked `__pycache__` / `.pytest_cache` entries. **Honest deviation to record:** my read-only enumeration imported the linter modules with cwd inside the live checkout, so CPython wrote `.pyc` bytecode into pre-existing, `.gitignore`d `__pycache__` directories there (`gitignore:9`, `git check-ignore -v research/manuscripts/__pycache__` confirms). No tracked file was created, modified or deleted; `git status --porcelain` stayed empty; no git write operation was run.
- Scratch deleted: `rm -rf /tmp/claude-0/w59` executed; `ls /tmp/claude-0/` no longer lists `w59`.
- **PROPOSED (NOT RUN), deliberately:** `scripts/preflight.sh` (dispatch forbids); `research/modalities/atr_hrd_sarcoma_series.py` (never invoked in any form); the modules' own unit-test suites; any repair, patch, gate or test — none authored, none proposed as code.

## Limitations

- Coverage is measured over `git ls-files 'research/manuscripts/*' | grep '\.md$'` = 187, W51's denominator exactly. Manuscript-like prose elsewhere (`research/modalities/*.md`, `systems/views/`, `archive/`) is outside it; `lint_claims` covers 100 `systems/views/*.md` and 1 `research/modalities` file that this denominator does not count, so its 19.3% understates its total surface while correctly stating its manuscript surface.
- The injections are representative, not exhaustive. "Not caught" is proven for the specific texts injected; for `lint_style` and `lint_submission_residue` it is additionally entailed by the source (a file not in `TARGETS`/`targets()` is never opened). A differently-worded injection could coincidentally trip an unrelated rule.
- `lint_citations`' 100% is coverage of **one defect class** (identifier anchoring/provenance) and says nothing about whether the cited paper says what the prose claims. It also exits 1 at baseline on this branch, largely from campaign-report content — a gate that is already red is a weaker signal in practice than one that is green.
- I did not evaluate whether any absent rule *should* exist, and authored no repair. Each registry-scoped gate carries in-source rationale for its scoping (notably `lint_style`'s "a memo, a plan or a findings note must not be added here" and `lint_submission_residue.targets()`' four-declaration design); a wider linter is not self-evidently better and I make no such recommendation.
- Static + injection audit of six modules at two HEADs. Nothing here bears on any manuscript's scientific correctness, and nothing computational here bears on EMC efficacy, safety, selectivity or clinical readiness. No content-policy refusal occurred.

## Stop condition

**Set up front:** stop once (a) each of the four named linters plus every other manuscript-facing preflight gate has its discovery mechanism read from source with `file:line`, (b) each one's actual manuscript file set is computed against the 187-file denominator, and (c) at least one paired injection (covered vs unlisted, byte-identical text) has been run per gate whose file set is in question — or at ~40 tool calls / ~40 minutes.

**MET**, early, on all three conditions: five paired or controlled injections across four gates, all four coverage figures computed, verdict resolved.

## Tool-call and wall-clock count actually used

**36 tool calls** (target ~40). **Wall clock ~4 minutes 36 seconds**, `04:47:15Z` → `04:51:51Z` (target ~40 min). Returning early rather than padding.

## Next concrete action

One successor, in this lane, for whoever owns gate semantics — **and it is a scoping decision, not a code task**: the measured split is that *citation identifiers* are gated over 187/187 manuscripts by discovery while *claim strength, style register, submission residue and numeric conformance* are gated over 41/187 (21.9%) by enumeration. The open question a successor can settle read-only is **which of the 146 uncovered manuscripts are actually outward-facing** — i.e. cross the 146 against `publications.json` states, `submission-metrics.json` rows and the deposited/archive manifests to separate "internal working record, correctly outside a submission gate" from "a document that can leave the building and is linted only for citation identifiers". That converts a coverage percentage into a named, human-decidable list, and it is the only form in which this finding can be acted on without someone choosing to widen a file set — which no worker should do. I am **not** proposing a repair and authored none.
