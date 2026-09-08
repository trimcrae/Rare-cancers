<!-- collected 2026-09-08T05:02:59Z by campaign coordinator; agent id a383be8606e09f224; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a383be8606e09f224.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

## Worker

**W78**, lane: `is_cleared` / `check_superseded` reach census — successor to W56's two unmeasured defects. Campaign OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the served model from the transcript.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 04:56:59 UTC 2026` | `Tue Sep  8 04:59:45 UTC 2026` |
| `git rev-parse HEAD` | `129a4e2a1c39352a7a697c42445bb27fc50f9b0c` | `2121960e980034c4c727c2947e6badd888f2dc27` |
| `git status --porcelain` | empty (0 lines) | empty (0 lines) |

HEAD advanced during my run (coordinator collecting reports, as the brief says it does). Nothing outside the campaign directory changed; the two files I measure (`research/manuscripts/lint_consistency.py`, `research/manuscripts/pinned-figures.json`) were read from the live checkout.

Literal output of the prescribed `env` command (51 lines; proxy/`JAVA_TOOL_OPTIONS`/`no_proxy` lines are long and are reproduced verbatim below except where noted):

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
GLOBAL_AGENT_NO_PROXY=<same host list as no_proxy>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... -Djdk.http.auth.proxying.disabledSchemes=
NO_PROXY=<same host list as no_proxy>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<same host list as no_proxy>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

No variable in that set names a served model.

## Question

W56 found two defects in `research/manuscripts/lint_consistency.py` and measured neither's reach. Two censuses, no repair:

**(a)** How many setext headings exist in the 29 `targets[]`, and how many live `superseded[]` matches sit under one — i.e. how many of the 246 live clearances, or of the currently-uncleared population, would change verdict had `is_cleared`'s heading-blanking and `_enclosing_heading` recognised setext headings?

**(b)** Characterise the 77 occurrences `check_superseded:604`'s `rx.search` never examines — per file and per entry — and for the 4 uncleared ones, read the surrounding prose and adjudicate whether each is materially stale text or a restatement inside a correction. W56 explicitly left that UNKNOWN.

Both are open because W56 states so in its own Limitations: *"The setext finding is a behaviour measurement, not a claim that any committed file uses setext headings this way. I did not census setext usage across the 29 targets"*, and *"Whether any of the four is materially stale prose or a within-a-correction restatement is UNKNOWN — I did not adjudicate the text."*

## Prior-work check

Read in full first, as instructed: `COMMON-BRIEF.md` (all 601 lines, including the whole "Known, measured, and NOT worth rediscovering" section), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W56-is-cleared-window-mechanics.md`, `reports/W28d-transplant-test-40-would-match.md`. I took as given and did **not** re-derive: the `is_cleared` predicate, the 246/58 count, the 39/13/29 split, and W56's slack distribution. (My instrumentation reproduced 246 examined / 58 entries and the 323/77/4 split as a by-product of building a verified replica; that is corroboration, not a re-measurement.)

Commands run against the tracked corpus, excluding the campaign directory:

- `grep -n -i "setext\|finditer" research/manuscripts/lint_consistency.py research/modalities/tests/test_lint_consistency.py` — the source and its test file contain neither term (consistent with W56's zero-hit greps). No prior art in the tree.
- Source read directly: `lint_consistency.py:159-227` (`_locally_negated`, `_enclosing_heading`, `_HEADING_CLEAR_PHRASES`, `is_cleared`) and `:591-612` (`check_superseded`). `l.startswith("#")` appears at `:169` (`_enclosing_heading`) and `:207` (the blanking comprehension) — exactly the two sites W56 names.
- W25 is HELD: I read, referenced and cited no `reports/W25-*` file.

Closed items I confirmed I am not replaying: the 39/13/29 transplant set (W28d, closed), the resolution-rate backlog (W36/W36b, closed), lane 2 (closed). Nothing in `CLOSED-WORK.md` covers linter mechanics.

## Method and inputs

All measurement is **read-only against the live checkout**. Scripts were written to and run from `/tmp/claude-0/w78/` (now deleted); nothing in the repository was written, edited or copied over. `PYTHONDONTWRITEBYTECODE=1` and `sys.dont_write_bytecode = True` were both set, so no `__pycache__` was created in `research/manuscripts/` — this is the deviation W56 recorded and I avoided it. `git status --porcelain` is empty at start and end.

Inputs:
- `/home/user/Rare-cancers/research/manuscripts/lint_consistency.py` — imported unmodified as a module; `L.is_cleared`, `L._locally_negated`, `L._WINDOW_BACK/_FWD/_CHARS`, `L._HEADING_CLEAR_PHRASES` used as shipped.
- `/home/user/Rare-cancers/research/manuscripts/pinned-figures.json` — `targets[]` (29 paths: 28 `.md`, 1 `.json`), `superseded[]` (81 entries), `supersession_markers` (34 markers).
- Python 3 (`/usr/local/bin/python3`).

Instrument: for every `(target, entry)` pair I ran `re.finditer` (not `search`) over every line, giving all 323 occurrences. For each occurrence I evaluated three verdicts: the **live** `L.is_cleared`, a **replica** of `is_cleared` that also reports which of the three disjuncts fired, and a **setext-aware variant** identical to the replica except that a setext heading's text line *and* its underline line are treated as headings for both the length-preserving blanking and the `_enclosing_heading` upward scan. The replica reproduced live `is_cleared` on **all 323 occurrences with 0 mismatches**, which is what licenses using the variant's diff as the counterfactual.

Setext enumeration, two definitions:
- **Naive** (the dispatch's literal definition): a non-blank text line followed by a line matching `^(=+|-+)\s*$` of length ≥3, not inside a ```` ``` ````/`~~~` fence.
- **Strict**: the naive definition additionally excluding the YAML frontmatter block (lines from a line-1 `---` to its closing `---`).

Prose adjudication for the 4 uncleared occurrences was done by reading the raw character ranges of the two enormous single lines involved (`pricing.md:246` is 3,677 chars; `degrader-paper-schedule.json:292` is 2,661 chars), plus surrounding lines.

## Result

### (a) Setext census — the defect is real in behaviour and has **zero reach** in this corpus

| row | value | grade |
|---|---|---|
| Targets scanned | 29 (28 `.md`, 1 `.json`) | PRIMARY |
| **Genuine setext headings in the 29 targets (strict definition)** | **0** | PRIMARY |
| Naive-definition candidates | 28 | PRIMARY |
| …of which are the **closing `---` of a YAML frontmatter block** | **28 of 28 (100%)** | PRIMARY |
| `=`-underline candidates anywhere in the 29 targets | 0 | PRIMARY |
| Live `superseded[]` matches whose `_enclosing_heading` would have differed under setext-awareness | **0** | PRIMARY |
| **Verdict flips among the 246 live clearances** | **0** | PRIMARY |
| **Verdict flips among the currently-uncleared population (the 4)** | **0** | PRIMARY |
| Verdict flips across all 323 occurrences | **0** | PRIMARY |

The 28 naive hits are all of one shape — a frontmatter key line (`_backfilled: true`, `last_verified: 2026-08-05`, `related: [...]`, `description: …`) immediately followed by the frontmatter's closing `---`. Exactly one per file, in 28 of 29 targets; the 29th is the `.json`, which has no frontmatter. Examples verbatim:

```
CLAUDE.md:13        text='_backfilled: true'          underline='---'
STRATEGY.md:20      text='last_verified: 2026-08-05'  underline='---'
systems/views/plan.md:12  text='last_verified: 2026-08-05'  underline='---'
```

The 0-flip result is measured under the **naive** definition, which is the stronger test: even when all 28 frontmatter closers are *granted* setext status — blanked out of every proximity window and allowed to serve as an enclosing heading — no occurrence changes verdict. The mechanism is distance: the closest any of the 323 occurrences comes to a naive-setext line is **5 lines**, against a window of `_WINDOW_BACK=2` / `_WINDOW_FWD=1`, so none of the 28 lies in any proximity blob; and every one sits near the top of its file above every occurrence's nearest `#`, so the `_enclosing_heading` scan hits a `#` first (and in any case none of the 28 contains a `_HEADING_CLEAR_PHRASES` string). Under the strict definition the count is 0 and the flip count is trivially 0.

**Conclusion for (a):** W56's setext finding is a genuine and reproducible *behavioural* defect in `is_cleared` — I confirm the two `startswith("#")` sites at `:169` and `:207` — but its **current blast radius over the committed corpus is exactly zero occurrences**. It is a latent hazard against future prose, not a live false clear. That is a strictly weaker claim than W56's demonstration implies if read without this census, and it is the honest one.

### (b) The 77 never-examined occurrences

Reproduced exactly: **323 total occurrences, 246 examined (first per line per entry), 77 never examined, 4 of the 77 uncleared at their own offset.**

**Per file (n=77):**

| file | never-examined |
|---|---|
| `STRATEGY.md` | 28 |
| `research/compute/pricing.md` | 11 |
| `research/manuscripts/program/degrader-paper-schedule.json` | 11 |
| `research/manuscripts/nr4a3-program-map.md` | 8 |
| `research/manuscripts/degrader/nr4a3-degrader-paper.md` | 4 |
| `systems/views/plan.md` | 4 |
| `research/compute/bid-strategy.md` | 3 |
| `research/modalities/nr4a3-nrv04-retrospective-prereg.md` | 3 |
| `research/compute/gcp-gpu-facts.md` | 2 |
| `research/manuscripts/degrader/nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md` | 2 |
| `research/manuscripts/degrader/nr4a3-degrader-paper-SI.md` | 1 |

11 of the 29 targets carry at least one; 18 carry none. (This agrees with W56's per-file line for the six files it listed and adds the five it did not.) All PRIMARY.

**Per entry (n=77, 27 distinct `superseded[]` ids of 81):**

| entry id | n | | entry id | n |
|---|---|---|---|---|
| `covalent_panel_arms` | 9 | | `ladder_total_390` | 3 |
| `paralogue_collision_pilot_5657` | 8 | | `ladder_total_467` | 3 |
| `rbfe_edge_tyk2_rate` | 5 | | `endpoint_leg_0_26` | 3 |
| `ladder_total_185` | 5 | | `two_mechanism_grid_limit` | 3 |
| `valb_miss_magnitude_and_ratio` | 5 | | `ladder_total_128` | 2 |
| `ladder_total_158_two_leg_5aks` | 5 | | `tier2_term_a_seven_basins` | 2 |
| `bid_multiple` | 4 | | `gcp_spec_card_table_p100` | 2 |
| `scoreboard_realised_0_74` | 4 | | `gcp_spec_card_table_t4` | 2 |
| | | | `nrv04_retro_panel_18_of_18` | 2 |

plus nine ids with 1 each: `ternary_edge_65_110`, `fanout_91_101`, `s1f_shakeout_offer_quote_1p41x`, `genmatched_null_degenerate_statistics`, `marginal_axis_resolvable_1p12_assumed_sd`, `bid_strategy_tool_total_166`, `ternary_edge_3_6`, `ternary_edge_4_7`, `ternary_edge_10_16`, `fanout_12_26`. (27 ids listed; 9+8+5+5+5+5+4+4+3+3+3+3+2+2+2+2+2 = 67, plus 10 singletons = 77.) All PRIMARY.

**Would-be verdict if the linter examined them** (evaluated at each occurrence's own offset with the unmodified `is_cleared`):

| would-be path | n / 77 |
|---|---|
| PROXIMITY (a marker within ±200 chars of that offset) | 61 |
| HEADING (enclosing section is about superseded values) | 9 |
| NEGATOR (contrastive "not X" within 28 chars) | 3 |
| **NONE — would be flagged ERROR** | **4** |

So **73 of 77 (94.8%) would clear anyway**; the first-match-only defect hides 4. Line hotspots: `STRATEGY.md:67` (6), `degrader-paper-schedule.json:292` (4), `STRATEGY.md:70` (3), `pricing.md:246` (3). 66 distinct `(file, line, entry)` triples carry an extra occurrence; the maximum extras on a single triple is 2.

### (b) Prose adjudication of the 4 — my judgement, stated as mine

W56 left this UNKNOWN. I read each in its raw character context. **All four are, in my reading, restatements inside an explicit correction, not materially stale text.** I quote each and say why. These are judgements of English prose about compute-cost bookkeeping; nothing here is a scientific, clinical or EMC claim.

**1–2. `research/compute/pricing.md:246`, cols 2743 and 2753 — `ternary_edge_3_6` (`~$3–6`), `ternary_edge_4_7` (`~$4–7`).** Verbatim (chars ~2600–2790 of a 3,677-char table row):

> "**The ~920-iteration figure that both prior estimates used as 'a full leg' is ~38 % of one**, which is why ~$3–6 and ~$4–7 are each ~2.6× low."

**NOT materially stale (my judgement).** The sentence exists solely to retract those two figures and states the retraction quantitatively in the same clause that names them. It is the textbook shape the linter's own `_locally_negated` docstring calls "the CORRECT way to write a correction". It fails only because none of the 34 markers appears within ±200 chars: the list contains `prior text`, not bare `prior`, and "is ~2.6× low" is not in the vocabulary.

**3. `research/compute/pricing.md:246`, col 2941 — `ternary_edge_10_16` (`~$10–16`).** Verbatim:

> "edge = binary+ternary × 3 replicas = 6 legs ≈ **~64 GPU-h** ≈ **~$8.8** at the $0.137/ref-GPU-h policy *(the ~$10–16 this arithmetic first gave assumed ~$0.15–0.25/hr)*."

**NOT materially stale (my judgement).** The parenthetical is a retraction of the old figure, and it stands immediately beside the registry's own `current` value (`~$8.8 ($3.2–22) per ternary edge`) — the live number is stated 60 characters before the retired one. "first gave" is not a marker string.

**4. `research/manuscripts/program/degrader-paper-schedule.json:292`, col 2534 — `bid_multiple` (`x1.9`).** Verbatim:

> "…3090+x1.9 merely got THIS panel done cheaply on the hosts it landed."

**NOT materially stale (my judgement)**, and this is the weakest of the four. It is a past-tense narrative about a completed run, not a go-forward prescription, and the *same JSON string value* already carries an explicit bracketed retraction of the same quantity 864 characters earlier at col 1670:

> "bid min_bid x1.5->x1.9 [both SUPERSEDED: the bid rule is now the market floor plus a staleness tic…"

That first occurrence is the one the linter examines, and it clears correctly. The second is outside `_WINDOW_CHARS=200` of the first — which is exactly the long-single-line file class that `_WINDOW_CHARS` was introduced for in the first place. My reservation: unlike the three `pricing.md` cases, this occurrence carries no retraction of its own, so a reader arriving mid-string sees `x1.9` presented without qualification. I grade it not-stale on the strength of the same-value bracket, not on the sentence alone.

**The consequential finding for whoever owns this defect:** all 4 hidden occurrences are correctly-written corrections. So `check_superseded`'s first-match-only iteration is currently suppressing **4 would-be false positives, not 4 stale values**. Changing `rx.search` to `rx.finditer` would, at this HEAD and with `_WINDOW_CHARS=200` unchanged, turn `0 ERROR across 29 target file(s)` red on four occurrences that a human reading the prose would call correct. That reframes the defect: it is a *coverage* gap whose current contents happen to be clean, and repairing it in isolation makes the gate worse before it makes it better. I did not author, propose or apply any repair, and I did not change `_WINDOW_CHARS`.

## Validation evidence

All **RUN**. Environment: `/home/user/Rare-cancers`, Python 3 at `/usr/local/bin/python3`, `PYTHONDONTWRITEBYTECODE=1`, `sys.dont_write_bytecode=True`, scripts under `/tmp/claude-0/w78/` (deleted at end). No pytest was run at all, so no `.pytest_cache` was created.

**RUN 1 — baseline, unmodified linter on the live tree:**
```
$ PYTHONDONTWRITEBYTECODE=1 python3 research/manuscripts/lint_consistency.py
lint_consistency: 0 ERROR across 29 target file(s)
EXIT=0
```

**RUN 2 — replica fidelity and headline counts** (`/tmp/claude-0/w78/census.py`, exit 0):
```
n targets: 29
replica mismatches vs live is_cleared: 0
total occurrences (finditer): 323
examined (first per line per entry): 246
never examined: 77
examined & cleared: 246
examined & uncleared: 0
never-examined & would-be-uncleared: 4
```

**RUN 3 — setext census, naive definition** (same script):
```
=== SETEXT HEADINGS ===
total setext headings across 29 targets: 28
     1  .claude/skills/ci-escape-hatches/SKILL.md
     ... (one per file, 28 files) ...
     1  systems/views/plan.md

verdict flips under setext-awareness (all occurrences): 0
  of which examined by the linter today: 0
```

**RUN 4 — the 28 candidates inspected**, all 28 shown to be frontmatter closers (excerpt):
```
CLAUDE.md:13 char='-'
   text: '_backfilled: true'
   ulin: '---'
   prev: 'last_verified: 2026-09-04'
```

**RUN 5 — strict (frontmatter-aware) enumeration**, exit 0:
```
targets by extension: Counter({'.md': 28, '.json': 1})
GENUINE setext headings (frontmatter-excluded, fence-excluded): 0
'=' underline candidates total: 0
```

**RUN 6 — proximity check**, exit 0:
```
closest any of the 323 occurrences comes to a naive-setext line (|line delta|): (5, 'research/manuscripts/degrader/nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md', 13, 18)
window half-height in lines: back=2 fwd=1
```

**RUN 7 — 77-occurrence census** (per-file, per-entry and path tables reproduced in Result above), exit 0.

**RUN 8 — prose reads** of `pricing.md:246` chars 2400–3100 and 0–400, and `degrader-paper-schedule.json:292` chars 2204–2804 plus both `x1.9` occurrence contexts. Quoted verbatim above.

**RUN 9 — isolation:**
```
$ git status --porcelain       # start: empty
$ git status --porcelain       # end:   empty
$ rm -rf /tmp/claude-0/w78 && ls /tmp/claude-0/   # w78 absent
```
No git write operation of any kind was run; `scripts/preflight.sh` was not run; `atr_hrd_sarcoma_series.py` was not invoked.

**PROPOSED (NOT RUN):** none. I deliberately did not run a `finditer` variant of `check_superseded` through the real linter, because building one is authoring the repair I was told not to author. The 4-occurrence claim rests on my replica's 0/323 agreement with live `is_cleared`, plus W56's already-published end-to-end masking demonstration for `pricing.md:246`'s `~$3–6`.

## Limitations

- **The 0-flip setext result is corpus-specific and expires on the next edit.** It says nothing about whether setext headings *should* be recognised; it says that at HEAD `129a4e2a`/`2121960e` no target file contains one, so the defect currently costs nothing. Writing one setext heading containing a marker word into any of the 29 targets would make it live immediately, with no test to catch it (`grep -i setext` over `research/modalities/tests/test_lint_consistency.py` is still zero hits).
- **The naive/strict definition split is a real ambiguity I resolved by judgement.** A CommonMark parser would also reject the 28 frontmatter closers (a `---` inside frontmatter is not a setext underline), so I am confident the strict count of 0 is right — but I did not run a CommonMark parser, and my fence tracking is a simple toggle that does not handle indented fences or differing fence lengths. Files with unbalanced fences could in principle hide a candidate. I judge this low-risk given the naive superset also yields 0 flips.
- **My setext-aware variant is one of several defensible ones.** I treated both the text line and the underline line as headings. A variant blanking only the text line, or one also excluding setext headings from `_HEADING_CLEAR_PHRASES` matching, could in principle differ — but with 0 in-window candidates the choice cannot matter here.
- **The four adjudications are my reading of English prose, not a measurement.** I state them as my judgement and quote the text so a reader can disagree. The `degrader-paper-schedule.json:292` case is the one I would flag for a human: it is clean only because a bracketed retraction 864 characters away in the same JSON string covers it.
- **"Would clear if examined" for the other 73 is computed, not observed.** I evaluated `is_cleared` at each occurrence's own offset; I did not run a modified linter to watch it. The replica's exact agreement on all 323 occurrences is the warrant.
- I did not census the whole tree for setext headings — only the 29 `targets[]`, which is what `lint_consistency` reads (W51: no glob, no walk). 146 of 187 manuscripts are outside every prose gate; nothing here changes that.
- Nothing in this report is a scientific, EMC-efficacy, safety, selectivity or clinical-readiness claim. A lint registry is not a scientific claim. No retired value is restated here as current.

## Stop condition

Set up front: **stop when (i) setext headings in all 29 targets are enumerated under an explicit definition, with the ambiguous cases inspected and classified; (ii) the count of the 246 live clearances and of the uncleared population whose verdict would change under setext-awareness is produced by a counterfactual whose baseline arm reproduces live `is_cleared` exactly; (iii) the 77 never-examined occurrences are tabulated per file and per entry with their would-be clearance path; (iv) each of the 4 uncleared is quoted in context and adjudicated with the judgement attributed to me; and (v) the live tree is verified untouched and scratch deleted.**

**MET.** (i) 28 naive candidates, all 28 inspected and classified as frontmatter closers; 0 strict. (ii) 0 flips, replica 0/323 mismatches. (iii) 11 files, 27 entry ids, 61/9/3/4 path split. (iv) all four quoted and adjudicated. (v) RUN 9. I did not repair anything, did not touch `_WINDOW_CHARS`, and did not edit the linter or registry. Stopped here rather than extending to the ~23 unmatched entries — that is W56's named successor and a different question.

## Tool-call and wall-clock count actually used

**14 tool calls** (all Bash; no Read/Write/Edit/Grep tool used, per the auto-mode instruction). **Wall clock: ~3 minutes** (`04:56:59Z` → `04:59:45Z`). Both well inside the ~40/~40 target; returning early rather than padding.

## Next concrete action

For this lane, the single highest-value next task is **not** the `finditer` repair, and this census is the reason. It is: **decide, with the manuscript owner, whether the four `pricing.md:246` / `degrader-paper-schedule.json:292` corrections should be rewritten to carry a marker inside their own ±200-char window** — e.g. so that the retraction clause uses one of the 34 registered markers rather than "prior estimates"/"first gave"/an 864-char-distant bracket. If that prose change lands first, `rx.search → rx.finditer` becomes a pure coverage win that keeps the gate green; if it does not, the repair turns a green gate red on four correctly-written sentences and will be reverted within a day — precisely the failure mode `_WINDOW_CHARS`'s own comment block warns about twice. The setext defect needs no action beyond a note that its reach is currently zero.
