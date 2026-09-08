<!-- collected 2026-09-08T04:56:03Z by campaign coordinator; agent id aee50ca9dfe456ebf; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aee50ca9dfe456ebf.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

## Worker

**W56**, lane: `is_cleared` robustness — the sole live exercise path for the `superseded[]` guards. Campaign OPUS-CAPACITY-CAMPAIGN-20260908, successor to W28d's R.5 finding.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the served model from the transcript.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 04:45:00 UTC 2026` | `Tue Sep  8 04:52:05 UTC 2026` |
| `git rev-parse HEAD` | `fb1a3f8040537234010114053b36ec55b729c65e` | `56f355f65b7b3e47aeb434ac02edf4cf049f40f3` |
| `git status --porcelain` | empty (0 lines) | empty (0 lines) |

HEAD advanced during my run (coordinator collecting reports, as the brief says it does). My `cp -a` snapshot was taken at `fb1a3f80`; the two files I measure — `research/manuscripts/lint_consistency.py` and `research/manuscripts/pinned-figures.json` — are byte-identical between my snapshot and the live tree at `56f355f6` (`diff -rq --exclude=.git` reports no difference on either; the only non-campaign diffs are `__pycache__`/`.pytest_cache`, see the disclosure below).

Literal output of the prescribed `env` command (proxy/`JAVA_TOOL_OPTIONS` lines omitted for length; nothing else removed):

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
No variable names a served model.

⚠ **Write-isolation disclosure, stated because it is a deviation from my instruction, not because anything was tracked.** I ran `pytest research/modalities/tests/test_lint_consistency.py` **in the live tree** (to obtain a real exit code for the tests that pin `_WINDOW_CHARS`). That run wrote Python bytecode caches and updated `.pytest_cache/v/cache/nodeids` under `/home/user/Rare-cancers`. All of those paths are gitignored: `git status --porcelain` returns **0 lines** at start and at end, and no tracked file changed. I did **not** delete them afterwards, because deleting would be a further write and could remove pre-existing caches. Every *mutation* experiment ran in the `cp -a` copy only. No git write operation, no manuscript/graph/view/report edit, no repair, patch, gate or test authored; `scripts/preflight.sh` not run; `atr_hrd_sarcoma_series.py` not invoked; no W25 material read or referenced; no network, paid API or GPU. Scratch `/tmp/claude-0/w56/` deleted (`ls` → `No such file or directory`).

## Question

W28d measured that all 246 live `superseded[]` matches across 58 of 81 entries are cleared by `is_cleared`, making it the guards' only live exercise path, and explicitly declined to test it. **How robust is `is_cleared`?** Specifically: (a) how much slack sits between each live match and its clearing marker, and how much would let an unrelated marker clear a genuinely stale value; (b) can a marker for supersession A clear a match for supersession B; (c) how does it behave at file boundaries, blank lines and headings.

Open because W28d named it as an unopened lane ("I did not test `is_cleared`'s window mechanics, and I did not test whether any firing guard would be *spuriously* cleared").

## Prior-work check

Read in full: `COMMON-BRIEF.md` (including the whole "Known, measured, and NOT worth rediscovering" section — I take the 39/13/29 split and the 246/58 measurement as given and did **not** re-derive them, though my instrumentation independently reproduced 246/58 as a by-product), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W28d-transplant-test-40-would-match.md`, `CLAUDE.md`.

Commands run:
- `grep -n "_WINDOW_CHARS\|def is_cleared\|def _read_lines\|def check_superseded\|MARKER\|marker" research/manuscripts/lint_consistency.py`
- `git ls-files | grep -i test_lint_consistency` → **`research/modalities/tests/test_lint_consistency.py`** (note: it is under `research/modalities/`, not `research/manuscripts/tests/`, where the linter's own comment "`tests/test_lint_consistency.py`" would lead you)
- `grep -n "def test_" <that file>` → 27 tests; 12 are about clearing/window/heading/marker/distance.
- `grep -n -i -E "setext|finditer|second occurrence|twice" <that file>` → **zero hits** (no test covers either of my two defect findings).

`CLOSED-WORK.md` closes nothing in this lane. Per the brief, sibling reports are not repository evidence: W28d's R.5 is the *premise* I was dispatched on, and I re-instrumented it rather than importing its numbers.

## Method and inputs

Inputs, all from the live checkout snapshot at `fb1a3f80`:
- `research/manuscripts/lint_consistency.py` (`_WINDOW_BACK/_WINDOW_FWD/_WINDOW_CHARS` at `:81-125`, `_locally_negated` at `:159-163`, `_enclosing_heading` at `:165-171`, `_HEADING_CLEAR_PHRASES` at `:165-175`, `is_cleared` at `:177-227`, `check_superseded` at `:591-612`).
- `research/manuscripts/pinned-figures.json` — 81 `superseded[]` entries, 29 `targets[]`, 35 `supersession_markers`.
- `research/modalities/tests/test_lint_consistency.py` — 27 tests.

Tools: `python3` 3.11 stdlib (`importlib`, `json`, `re`, `collections`), `pytest` 9.1.1 (via `pytest`, not `python3 -m pytest`, per the brief), `git`, `diff`. Five scratch scripts (`analyze.py`, `slack.py`, `slack2.py`, `cross.py`, `spur.py`) plus inline heredocs, all under `/tmp/claude-0/w56/`, all deleted.

Method: load the real module by path against the `cp -a` copy at `/tmp/claude-0/w56/repo`, enumerate live matches exactly as `check_superseded` does, then (i) attribute each clearance to its path, (ii) measure slack by **binary-search perturbation** rather than analytically — insert *k* spaces immediately before the match and *k* immediately after it, which pushes every preceding marker and every following marker *k* characters away simultaneously, and find the largest *k* that still clears, and (iii) run the **real unmodified linter** end-to-end on the copy after each text injection, restoring from a pristine byte-copy between runs.

## Result

### R.1 — The exact predicate `PRIMARY`

`is_cleared(lines, idx, markers, line=None, start=None)` returns `True` iff **any** of three disjuncts holds, short-circuited in this order:

1. **NEGATOR** — `line is not None and start is not None` and `line[max(0, start-28):start].lower()` contains any of `("not ", "never ", "no longer ", "rather than ", "instead of ", "isn't ", "≠")`. Same-line lookback only, 28 characters.
2. **PROXIMITY** — with `lo = max(0, idx-2)`, `hi = min(len(lines), idx+2)`:
   - `window` = `lines[lo:hi]`, with every line that `.startswith("#")` replaced by an equal-length run of spaces **except** the line at `idx` itself (length-preserving, so offsets do not shift);
   - `blob = "\n".join(window)`;
   - `offset = sum(len(l)+1 for l in lines[lo:idx]) + (start or 0)`;
   - `near = blob[max(0, offset-200) : offset+200].lower()`;
   - `True` if **any** marker string, lowercased, is a **bare substring** of `near`.
3. **HEADING ABOUTNESS** — `heading` = the nearest line at or above `idx` starting with `#` (search unbounded, to line 0); `True` if it contains any of the 7 `_HEADING_CLEAR_PHRASES`.

Three properties of that predicate matter for everything below:
- **`markers` is the whole global vocabulary and no entry identity is passed at all.** The signature is literally `(lines, idx, markers, line=None, start=None)` — verified with `inspect.signature`. `check_superseded` calls it identically for every entry.
- **Marker matching is bare, case-insensitive substring with no word boundary.** `'retir'` matches "retirement"; `'once '` matches "once more"; `'carried'`, `'believed'`, `'replac'`, `'previously'`, `'historical'`, `'at the time'`, `'was $'` are ordinary English.
- **Containment, not distance.** The whole marker string must fit inside the 400-char slice, so a marker of length *L* preceding the match clears only if its **start** is within 200 chars, i.e. its **end** within `200 − L`.

`_WINDOW_CHARS` history, from the source comments: introduced 2026-07-31 at **400** after a real false clear in `degrader-paper-schedule.json` (one enormous line; an unrelated `"Superseded framing:"` cleared three stale panel counts); narrowed **400 → 200 on 2026-08-05** after a sweep found the margin was doing the clearing (`degrader-paper-schedule.json:72`'s `~$194` cleared by the word "retiring" 130 chars away, about a *caveat*). Retained line: `# Superseded, retained: _WINDOW_CHARS = 400`. Rejected alternatives, both measured at the time: "marker's clause must contain a digit" (+29 new flags, nearly all correct retractions) and "enclosing sentence" (+118).

### R.2 — Clearance-path attribution over the 246 `PRIMARY`

| effective path (short-circuit order) | n / 246 | distinct entries |
|---|---|---|
| NEGATOR | 9 | — |
| PROXIMITY marker | 220 | — |
| HEADING aboutness | 17 | — |

Blast radius of a regression, measured by disabling each path and recounting:

| mutation | uncleared matches | distinct `superseded[]` entries un-covered |
|---|---|---|
| baseline (real `is_cleared`) | **0** | 0 |
| `is_cleared` returns `False` always | **246** | **58** |
| proximity path removed (`markers=[]`) | 193 | 53 |
| heading path removed (`_HEADING_CLEAR_PHRASES=()`) | 17 | 15 |
| negator path removed (`_NEGATORS=()`) | 2 | 2 |

W28d's concentration warning is confirmed numerically: **a total `is_cleared` regression turns 58 entries and 246 committed occurrences into ERRORs at once**, and the proximity path alone carries 193/246.

### R.3 — Slack distribution over the 246 `PRIMARY`

Ground truth by perturbation (largest *k* such that inserting *k* spaces on **both** sides of the match still clears; unbounded probed to 3000):

| | n |
|---|---|
| **unbounded** (heading path — no character bound exists) | **44** |
| **finite** (proximity or negator path) | **202** |

Finite slack, in characters (n = 202, unit = characters of drift between figure and disclaimer before clearance is lost; no sampling uncertainty — this is an exhaustive census, not an estimate):

| min | p10 | p25 | median | p75 | p90 | max |
|---|---|---|---|---|---|---|
| **7** | 88 | 129 | **160** | 178 | 187 | 192 |

| slack band | n |
|---|---|
| 1–9 | 1 |
| 10–24 | 3 |
| 25–49 | 4 |
| 50–99 | 17 |
| 100–149 | 60 |
| 150–199 | 117 |

**The eight most fragile live sites** (an ordinary edit that pushes the figure this many characters from its disclaimer turns the build red — a false *alarm*, the safe direction):

| slack (chars) | entry | site |
|---|---|---|
| 7 | `card_ratio_4090_over_3090_2_10` | `research/compute/bid-strategy.md:213` |
| 13 | `nrv04_retro_panel_18_of_18` | `research/modalities/nr4a3-nrv04-retrospective-prereg.md:184` |
| 19 | `triangle_n3_176` | `systems/views/plan.md:283` |
| 24 | `triangle_n1_59` | `systems/views/plan.md:283` |
| 29 | `fanout_91_101` | `research/compute/pricing.md:328` |
| 34 | `two_mechanism_grid_limit` | `research/manuscripts/program/degrader-paper-schedule.json:630` |
| 35 | `card_rtx3090_359_36` | `research/compute/bid-strategy.md:213` |
| 35 | `tier2_term_a_seven_basins` | `research/manuscripts/nr4a3-program-map.md:3409` |

Redundancy (how many distinct marker occurrences sit inside the ±200 window of each proximity-cleared match): **96 of 220 rest on exactly one marker occurrence** (single point of failure); 75 have 2, 33 have 3, 16 have 4+. Of the 220, **124 would still clear if the nearest marker vanished** (a second marker is also in range); **96 would not**.

Which marker token does the clearing (nearest, n=220): `supersed` 98, `retir` 24, `withdraw` 18, `carried` 12, then a long tail — `once ` 5, `stale` 5, `was ~` 5, `retained for the record` 5, `do not quote` 5, and 18 tokens with ≤4 each.

**The distance at which an unrelated marker starts clearing is 200 characters flat** — that is the predicate, not an emergent property. The interesting number is how much margin the repository's own regression test leaves against it: `test_a_marker_about_a_different_subject_does_not_clear_a_figure` carries the real 2026-08-05 false clear, and I computed its exact geometry — marker `retiring` starts at index 36, the match `$128` at 249, so the window's left edge is at 49 and the marker misses containment by **13 characters**. **Widening `_WINDOW_CHARS` from 200 to 213 would re-admit the measured historical false clear while leaving that regression test green.** I did not change `_WINDOW_CHARS`; this is an analytic property of the committed test, computed, not applied.

### R.4 — (b) Yes: a marker for supersession A clears a match for supersession B, by construction and in the tree `PRIMARY`

Structurally: `is_cleared` receives no entry identity, so it cannot distinguish "this disclaimer is about *this* figure". Every marker is global.

Measured in committed text: **109 of the 246 live matches share their ±200 window with at least one *different* `superseded[]` entry's value** — i.e. in 109 cases one marker demonstrably covers two or more distinct retired quantities. The largest clusters: `STRATEGY.md:67` (6 ladder totals under one disclaimer), `STRATEGY.md:68` and `degrader-paper-schedule.json:41` (5 card figures each), `degrader-paper-schedule.json:87` (5), `bid-strategy.md:213` and `pricing.md:246` (4 each).

Demonstrated end-to-end with the **real unmodified linter** on the copy (all restore-to-pristine between runs; the injected text is `~$390 mid-range`, entry `ladder_total_390`, whose current value is `~$185`):

| experiment | injected text | linter result |
|---|---|---|
| **negative control** — no marker in range | `The gated ladder total is ~$390 mid-range.` | **1 ERROR, exit 1** ✅ caught |
| **cross-entry marker**, ~60 chars away, about the *card rule* | `The RTX 4090 selection rule was superseded on 2026-08-05; the gated ladder total is ~$390 mid-range.` | **0 ERROR, exit 0** ⛔ spuriously cleared |
| **generic English word only** (`carried`), ~40 chars away | `The schedule carried nine legs; the gated ladder total is ~$390 mid-range.` | **0 ERROR, exit 0** ⛔ spuriously cleared |

**Count of live matches that would be spuriously cleared by an unrelated marker.** "Unrelated" cannot be decided mechanically, so I report the defensible operationalisation: split the 35 markers into 17 **explicit** supersession terms (`supersed`, `withdraw`, `retir`, `retract`, `revok`, `do not cite/quote`, `must not be cited/quoted`, `not a go-forward`, `retained for the record`, `what retired it`, `that stood here`, `is not the ladder`, `does not stand`, `no longer current`, `pre-harmonized`) and 18 **ordinary-English** terms (`no longer`, `previously`, `used to`, `originally`, `the original`, `was ~`, `was $`, `stale`, `prior text`, `at the time`, `believed`, `replac`, `appendix a`, `historical`, `carried`, `once `, `the earlier`, `the intermediate`), then recount with only the explicit set honoured:

| | n / 246 |
|---|---|
| an explicit supersession term is in range — clearance does not depend on a generic word | **221** |
| **clearance rests ONLY on a generic English word** — an unrelated use of that word in prose would clear a genuinely stale value identically | **25** |

The 25, by site: `CLAUDE-history.md:97` ×3 (`ladder_total_128/194/169`); `research/compute/pricing.md` ×9 (`:386` ×2, `:387`, `:328` ×2, `:476`, `:298`, `:568`, `:340`, `:74`); `research/manuscripts/program/degrader-paper-schedule.json` ×4 (`:183` ×2, `:254`, `:284`); `research/compute/bid-strategy.md` ×2 (`:320`, `:23`); `research/manuscripts/degrader/nr4a3-degrader-paper.md` ×2 (`:197`, `:3292`); `research/manuscripts/nr4a3-program-map.md` ×2 (`:2517`, `:3409`); `research/modalities/nr4a3-degrader-next-steps.md:1022`; `research/modalities/nr4a3-nrv04-retrospective-prereg.md:271`.

These 25 are **not** claimed to be currently false clears — I did not read all 25 in context and cannot assert their disclaimers are unrelated. The claim is exactly this: **25 of 246 live clearances would survive replacing their disclaimer with an unrelated sentence containing the same ordinary word**, so for those 25 the linter's assurance is only as strong as the word.

### R.5 — (c) Boundary behaviour: five cases correct, one misbehaves `PRIMARY`

All run through the real unmodified linter on the copy, restore-to-pristine between runs.

| case | construction | result | verdict |
|---|---|---|---|
| **start of file, no marker** | stale value as line 1 | 1 ERROR at `:1`, exit 1 | ✅ correct, no crash (`lo=max(0,idx-2)` clamps) |
| **start of file, marker on line 2** | stale line 1, marker line 2 | 0 ERROR, exit 0 | ✅ correct (`_WINDOW_FWD=1`) |
| **end of file, no marker** | stale value as final line, no trailing newline | 1 ERROR, exit 1 | ✅ correct, no crash (`hi=min(len(lines),…)` clamps) |
| **end of file, marker on preceding line** | marker then stale final line | 0 ERROR, exit 0 | ✅ correct |
| **match on an ATX heading line carrying its own marker** | `## the ladder was ~$390 mid, superseded` | 0 ERROR, exit 0 | ✅ correct — the match's own line is deliberately never blanked |
| **ATX heading control** | `## The ladder totals here are superseded` + blank + stale value | **1 ERROR, exit 1** | ✅ correct — heading blanked from the proximity blob, and the words are not in `_HEADING_CLEAR_PHRASES` |
| ⛔ **setext heading, identical words** | `The ladder totals here are superseded` / `------` / stale value | **0 ERROR, exit 0** | ⛔ **misbehaves** |

⛔ **The setext-heading asymmetry is the one boundary defect I found.** `## The ladder totals here are superseded` does **not** clear a figure two lines below (correct — that is the whole point of the 2026-08-05 blanking, pinned by `test_a_marker_word_in_a_nearby_heading_does_not_clear_by_proximity`). Writing the *same words* as a markdown **setext** heading (underlined with `---` or `===`) **does** clear it, because the blanking test is `l.startswith("#")` and `_enclosing_heading` likewise only recognises `#`. Both the guard and its narrowing are invisible to setext headings. `grep -i -E "setext" research/modalities/tests/test_lint_consistency.py` returns **zero hits**. I did not author a repair.

**Blank lines are not a boundary at all.** A marker two lines back, separated from the figure by a **blank line** — i.e. in a different paragraph — clears it: `That estimate was superseded.` / blank / `The gated ladder total is ~$390 mid-range.` → **0 ERROR, exit 0**. The window is line- and character-scoped only; paragraph structure is never consulted. Given the code's own "PROXIMITY IS NOT ABOUTNESS" note this is a design consequence, not a surprise, but it is undocumented and untested.

### R.6 — A live coverage hole *outside* `is_cleared`, found while instrumenting it `PRIMARY`

`check_superseded` uses `rx.search(ln)` — **the first match per line per entry only** — and never calls `finditer`. Over the 29 targets:

| | n |
|---|---|
| lines-with-a-match (what `check_superseded` actually tests) | **246** |
| total occurrences on those lines | **323** |
| **occurrences the linter never examines** (2nd and later on a line) | **77** |
| of those, occurrences that `is_cleared` returns **False** for at their own offset | **4** |

By file, never-examined occurrences: `STRATEGY.md` 28, `research/compute/pricing.md` 11, `degrader-paper-schedule.json` 11, `nr4a3-program-map.md` 8, `nr4a3-degrader-paper.md` 4, `systems/views/plan.md` 4.

The four uncleared-but-unexamined occurrences: `pricing.md:246` — `ternary_edge_3_6` (`~$3–6`), `ternary_edge_4_7` (`~$4–7`), `ternary_edge_10_16` (`~$10–16`); and `degrader-paper-schedule.json:292` — `bid_multiple` (`x1.9`).

**Demonstrated, not inferred.** In the copy I masked only the *first* `~$3–6` on `pricing.md:246` (2 occurrences on that line; first at column 1065) so the second became the first, and re-ran the real linter:

```
research/compute/pricing.md:246: ERROR [S-ternary_edge_3_6] superseded value '~$3–6' stated without marking it superseded
lint_consistency: 1 ERROR across 29 target file(s)
EXIT=1
```

So these are genuinely uncleared registered superseded values on committed target lines, invisible today solely because of first-match-only iteration. `grep -i finditer` over the test file returns zero hits. This is a defect in `check_superseded`, **not** in `is_cleared` — it is exactly the long-line file class (`degrader-paper-schedule.json`, and a 1000+ character `pricing.md` table row) that motivated `_WINDOW_CHARS` in the first place. **I did not repair it and did not propose code.** Whether any of the four is materially stale prose or a within-a-correction restatement is **UNKNOWN** — I did not adjudicate the text.

## Validation evidence

All `RUN`. Environment: `python3` 3.11 (`/usr/local/bin/python3`), `pytest` 9.1.1 via `pytest`, Linux container, no network. Mutations exclusively in `/tmp/claude-0/w56/repo` (a `cp -a` of the live tree at `fb1a3f80`), restored from pristine byte-copies between experiments; scratch deleted at end.

**RUN 1 — path attribution, `analyze.py`, exit 0:**
```
total live matches: 246
uncleared: 0
effective: {'PROX': 220, 'HEAD': 17, 'NEG': 9}
```

**RUN 2 — bidirectional slack by binary-search perturbation, `slack2.py`, exit 0:**
```
n=246 finite=202 unbounded=44
 unbounded breakdown: heading-path 44, negator-path 0, other 0
finite slack chars: min 7 p10 88 p25 129 median 160 p75 178 p90 187 max 192
```

**RUN 3 — regression blast radius, exit 0** (tuple = uncleared matches, distinct entry ids):
```
baseline (real is_cleared)            : (0, 0)
is_cleared always False (total regress): (246, 58)
proximity path disabled (markers=[])   : (193, 53)
heading path disabled                  : (17, 15)
negator path disabled                  : (2, 2)
```

**RUN 4 — generic-marker dependence and window sharing, `spur.py`, exit 0:**
```
{'EXPLICIT-suffices': 221, 'GENERIC-ONLY': 25}
matches sharing their +-200 window with >=1 DIFFERENT superseded entry's value: 109 of 246
```

**RUN 5 — injection / boundary experiments through the real linter** (verbatim, abbreviated to result lines; each preceded by a restore):
```
### E1c NEGATIVE CONTROL  -> research/compute/gcp-gpu-facts.md:520: ERROR [S-ladder_total_390] ... EXIT=1
### E1  CROSS-ENTRY marker -> lint_consistency: 0 ERROR across 29 target file(s)  EXIT=0
### E1b generic 'carried'  -> lint_consistency: 0 ERROR across 29 target file(s)  EXIT=0
### E5  BLANK-LINE         -> lint_consistency: 0 ERROR across 29 target file(s)  EXIT=0
### E6  SETEXT HEADING     -> lint_consistency: 0 ERROR across 29 target file(s)  EXIT=0
### E7  ATX HEADING CTRL   -> research/compute/gcp-gpu-facts.md:522: ERROR [S-ladder_total_390] ... EXIT=1
### E3a start-of-file, no marker  -> ...gcp-gpu-facts.md:1: ERROR ... EXIT=1
### E3b start-of-file, marker L2  -> 0 ERROR  EXIT=0
### E4a end-of-file, no marker    -> ...gcp-gpu-facts.md:519: ERROR ... EXIT=1
### E4b end-of-file, marker prev  -> 0 ERROR  EXIT=0
### E8  match on own ATX heading  -> 0 ERROR  EXIT=0
### restored baseline             -> lint_consistency: 0 ERROR across 29 target file(s)  EXIT=0
```

**RUN 6 — first-match-only demonstration, real linter, copy:**
```
first occurrence at col 1065 total occurrences: 2
research/compute/pricing.md:246: ERROR [S-ternary_edge_3_6] superseded value '~$3–6' stated without marking it superseded
lint_consistency: 1 ERROR across 29 target file(s)
EXIT=1
```

**RUN 7 — the pinning tests, live tree, unmodified:**
```
$ pytest research/modalities/tests/test_lint_consistency.py -q
...........................                                              [100%]
27 passed in 2.13s
EXIT=0
```

**RUN 8 — pinned-test margin computation, exit 0:**
```
marker 'retiring' start 36 end 44  match '$128' start 249
gap between marker END and match START = 205
window slice for containment: match_offset-200 = 49  marker starts at 36 -> contained? False
margin before this pinned test would silently pass (chars): 13
```

**RUN 9 — isolation verification:** `git status --porcelain` → 0 lines at start (`fb1a3f80`) and end (`56f355f6`). `diff -rq --exclude=.git /home/user/Rare-cancers /tmp/claude-0/w56/repo` → 14 non-campaign differences, **all** `__pycache__`/`.pytest_cache` (from RUN 7; see the disclosure in `## Worker`); zero source differences. `rm -rf /tmp/claude-0/w56` → `ls` returns `No such file or directory`.

**`PROPOSED (NOT RUN)`** — everything in "Next concrete action". No repair, patch, gate, test, guard change, `_WINDOW_CHARS` change, registry edit or `targets[]` change was authored, proposed as code, or applied. `scripts/preflight.sh` and `PREFLIGHT_FULL` not run.

## Limitations

- **"Unrelated marker" is not mechanically decidable, and I did not decide it.** The 25 generic-only clearances are a count of *linguistic dependence*, not 25 confirmed false clears. Establishing that any of them is a live false clear requires reading each disclaimer in context, which I did not do. The number is a lower bound on nothing and an upper bound on nothing; it is exactly the size of the class whose assurance rests on an ordinary word.
- **Slack is measured for one perturbation shape** — symmetric character insertion at the match. Real edits reflow lines, and a reflow that crosses the `_WINDOW_BACK=2` / `_WINDOW_FWD=1` **line** boundary breaks clearance regardless of character distance. My numbers do not cover line-count perturbations.
- **The 44 heading-path clearances have no character bound at all** and I report them as unbounded, not as safe. `_enclosing_heading` scans to line 0 with no limit, so a `## … superseded numbers …` heading clears every registered occurrence beneath it for the rest of the file or until the next `#`. I did not measure how far below their headings those 44 sit.
- **The four never-examined uncleared occurrences (R.6) are a defect in coverage, not an adjudication of the prose.** Whether each is genuinely stale text or a legitimate restatement inside a correction is UNKNOWN.
- **The setext finding is a behaviour measurement, not a claim that any committed file uses setext headings this way.** I did not census setext usage across the 29 targets.
- Every number here is from the 29 declared `targets[]` at `fb1a3f80`. Files outside `targets[]` were not scanned. I did not read the frozen corpus.
- **Nothing here is a scientific or clinical claim.** This concerns a lint registry. There is no wet lab; no EMC efficacy, safety, selectivity or clinical-readiness claim is made or implied.
- I did not re-derive W28d's 39/13/29 split or its 246/58 count as independent findings; the brief records them as settled and I took them as given (my instrumentation reproduced 246/58 incidentally, which is corroboration, not a re-measurement).

## Stop condition

Set up front: **stop when (i) the exact predicate is stated from source with its `_WINDOW_CHARS` history, (ii) a slack distribution over all 246 live matches is measured by real perturbation rather than analytically, (iii) the cross-entry question is answered by an end-to-end run of the unmodified linter with a negative control, (iv) a spurious-clearance count over the 246 is stated with its operational definition, and (v) file-start, file-end, blank-line and heading boundaries each carry a real linter exit code — with the live tree verified untouched and scratch deleted.**

**MET.** (i) R.1. (ii) R.3, n=246, 202 finite / 44 unbounded, perturbation-derived. (iii) R.4, three linter runs including the negative control. (iv) R.4, 25 of 246, definition given. (v) R.5, seven cases with exit codes; one misbehaviour found (setext). Isolation verified in RUN 9. Two findings arrived inside the same work and are reported without expansion: the 13-character margin on the pinned regression test (R.3) and the 77 unexamined / 4 uncleared occurrences (R.6). Stopped there.

## Tool-call and wall-clock count actually used

**19 tool calls** (18 `Bash`, 0 `Read`/`Edit`/`Write`), against a ~40 target. **Wall clock 04:45:00Z → 04:52:05Z = 7 min 05 s**, against a ~40 min target. Under both. Early return is the success case per the brief.

## Next concrete action

**One bounded, owner-facing item, requiring no repository write from this campaign and no code from me:** route to the owner of `research/manuscripts/lint_consistency.py` the two measured coverage facts, with their evidence, as a *decision* rather than a patch —

1. **`check_superseded` examines only the first match per line per entry** (`rx.search`, `:604`). 77 registered occurrences on committed target lines are never examined; **4 of them are uncleared at their own offset** (`pricing.md:246` ×3, `degrader-paper-schedule.json:292` ×1), demonstrated by masking the first occurrence and watching the real linter go red. This is the same long-line file class that motivated `_WINDOW_CHARS`, and no test covers it.
2. **The heading-blanking narrowing of 2026-08-05 does not see setext headings.** Identical words as `## …` do not clear (correct, and pinned); as an underlined heading they do clear. Both `is_cleared`'s blanking and `_enclosing_heading` test only `startswith("#")`.

Three things that should travel with that routing but are **not** part of it:

1. **`_WINDOW_CHARS` has 13 characters of margin against its own regression test.** The pinned 2026-08-05 false clear misses the window by 13, so a widening to 213 re-admits the historical bug with the suite still green. If anyone ever proposes widening the bound, that is the number to quote — and the test's docstring's "~130" is the gap, not the distance.
2. **96 of 220 proximity clearances rest on a single marker occurrence, and 25 of 246 rest on an ordinary English word.** Any future edit to `supersession_markers` should be evaluated against those two numbers, not against the marker list's length.
3. **A total `is_cleared` regression un-covers 58 entries / 246 occurrences at once; the proximity limb alone carries 193.** That is the confirmed concentration W28d warned about, now quantified per-limb.

**Successor for this lane:** the nearest genuinely open question is the one W28d named and I did not touch — whether the ~23 `superseded[]` entries with **no** live match in any target are silent because their value is truly gone or because the guard cannot reach it. My R.6 slightly enlarges its denominator (the tree exercises 323 occurrences, not 246), which should be folded in before that question is run.
