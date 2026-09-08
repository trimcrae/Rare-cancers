<!-- collected 2026-09-08T03:34:17Z by campaign coordinator; agent id a56ac4557ef8058c8; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a56ac4557ef8058c8.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

**W35**, campaign OPUS-CAPACITY-CAMPAIGN-20260908. Lane: briefing-file standing-fact audit (COMMON-BRIEF.md, CORPUS-CONTEXT.md, WAVE-LOG.md).

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as `claude-opus-5`. No environment variable in this container names a served model; the coordinator must extract the runtime model from the transcript. Do not treat my self-report as observation.

**Start** `date -u` = `Tue Sep  8 03:26:40 UTC 2026`; **end** `date -u` = `Tue Sep  8 03:30:15 UTC 2026`.
**Start** `git rev-parse HEAD` = `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f`; **end** = `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1`. HEAD moved under me mid-run (one coordinator collection commit; `reports/` grew 145 → 150 files during the run).
**Start** `git status --porcelain` = empty (clean). **End** = empty (clean). I wrote nothing to the repo or the corpus; my only writes are `/tmp/claude-0/w35/{lint.txt,tier.txt}`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (identical at start and end; four long proxy/no-proxy lines elided as noted, all others verbatim):

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
(elided for length only, all four are proxy host lists carrying no model information: `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`.)

## Question

Every worker in this campaign reads COMMON-BRIEF.md, CORPUS-CONTEXT.md and WAVE-LOG.md before doing anything. Nobody has audited them. W21d has just shown that corrective dispatch text works *reactively* — but a false standing fact reached three workers before it was caught. Which standing facts in those three files are still wrong, and how many workers will read each one before it is fixed?

**All commit-pinned claims below are against `ff6bb018` (start HEAD) unless noted; the two counts re-taken at the end are against `215ed8e7`.**

## Prior-work check

- `grep -l -E 'COMMON-BRIEF|CORPUS-CONTEXT|WAVE-LOG' *.md` in `reports/` → 108 reports mention a briefing file. **Read:** W21b, W21c, W21d, W23b in the passages that bear on this. None of them audits the briefing files as objects; they audit *report* content and the corpus differential. W21b is the closest — WAVE-LOG:382–387 records that it "flagged that the incorrect standing fact was propagating through dispatch prompts" — but that is one fact (the corpus root), found from the corpus side, not an enumeration of the briefs.
- Sibling **W33** is auditing CLOSED-WORK.md entry by entry. I did not open CLOSED-WORK.md's entries and make no claim about them; my only statement touching it is that COMMON-BRIEF.md:52 points at it and it exists.
- No prior report establishes what commit `92abbcb…` actually contains. That is the gap I closed.

## Method and inputs

Read-only, no network, no retrieval. Live checkout `/home/user/Rare-cancers`; frozen corpus at the **corrected** root `/tmp/claude-0/frozen-corpus/extracted/corpus/`. Tools: `git cat-file/ls-tree/merge-base/log/rev-list`, `find`, `stat`, `sha256sum`, `sed`, `grep`, `rg 14.1.0`, `python3`, plus two read-only repository scripts (`scripts/tier_budget.py --check`, `research/manuscripts/lint_citations.py`). Scratch under `/tmp/claude-0/w35/` only.

## Result

**Denominator: 34 standing facts enumerated across the three files. 25 CONFIRMED, 4 SUPERSEDED, 3 OVER-SCOPED, 2 UNVERIFIABLE.** The corpus block is clean; the damage is concentrated in the brief's frozen commit and in three under-specified path citations.

### Ranked by exposure — how many workers read it before it is fixed

Exposure basis: COMMON-BRIEF.md and CORPUS-CONTEXT.md are read by **every** worker ("Read this in full before doing anything else. It binds every worker", COMMON-BRIEF.md:3). WAVE-LOG.md is read by workers whose dispatch routes them to it, and by the coordinator on every collection. 150 reports exist and the campaign is still dispatching, so a brief-level defect has unbounded forward exposure and ~127 reports of realised exposure (count of report files containing the string `92abbcb`).

---

**RANK 1 — SUPERSEDED, every worker, realised in ~127 reports.**
COMMON-BRIEF.md:7–8:
> "Repository: `/home/user/Rare-cancers`. Frozen read commit:
>   `92abbcb905cacf07f14b238db50d1b98f6590374` (this checkout's HEAD)."

`92abbcb` is a real, reachable commit (`git cat-file -t` → `commit`, `2026-09-08 01:23:53 +0000`, "account-keyed cross-lane alarm: ATTENTION (CI)") and is an ancestor of HEAD. It was **not** HEAD for most of this campaign: at start it was 23 commits behind (`git rev-list --count 92abbcb..HEAD` = 23), and HEAD advanced again during my own run. Every one of the ten distinct HEADs reports actually recorded (`98a0833f`, `3f5fc95d`, `b9a0257e`, `47aac85f`, `d3e9c4d8`, `7d081218`, `c81236b9`, `fc6ed929`, `103ff76f`, `ce743d6a`) is a **descendant** of `92abbcb`, none equals it.

**What a worker who took the brief literally would have done, and this is the sharp part:** at `92abbcb` the campaign directory **does not exist**. `git ls-tree -r --name-only 92abbcb -- research/autonomy/opus-capacity-campaign-20260908` returns **0 files**; the same command at HEAD returns 156. `git diff --stat 92abbcb HEAD` on the four briefing files shows all four as pure additions (+70/+84/+63/+451). So a worker who checked out or read "the frozen read commit" would find **no COMMON-BRIEF.md, no CORPUS-CONTEXT.md, no CLOSED-WORK.md and no reports** — and COMMON-BRIEF.md:52's own instruction ("read `CLOSED-WORK.md` in this directory") is unsatisfiable at the commit the same file pins. The brief is self-referentially impossible at its own pin. Nobody hit this because everyone read the working tree instead, which is the right thing to have done and the opposite of what the text says.

*Smallest correct restatement:* "Repository: `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`. **HEAD advances during this campaign as the coordinator collects reports — record the HEAD you actually read.** `92abbcb905cacf07f14b238db50d1b98f6590374` is the campaign's start commit, not a frozen pin, and the campaign directory does not exist at it: read the working tree."

---

**RANK 2 — OVER-SCOPED, every worker, realised.**
COMMON-BRIEF.md:50–52:
> "Search the actual tracked corpus first, e.g.
> `rg -n -i "<term>" --glob '!.git' | head -50`"

This glob excludes `.git` and nothing else, so the campaign's own unreviewed report directory is inside the search space that the brief calls "the actual tracked corpus." Demonstrated: `rg -n -i "interchangeab" --glob '!.git' -l` returns 12 files under `reports/` **and `WAVE-LOG.md` itself** alongside the genuine tracked sources. A worker's mandatory prior-work check can therefore be satisfied — or a novelty claim refuted — by a sibling's uncollected draft. This is the same failure family as the propagated false standing fact: campaign text being read as repository evidence. Note it interacts with WAVE-LOG:438–440, where W25 refutes an unsourced claim using exactly a "corpus search found no source" argument.

*Smallest correct restatement:* append `--glob '!research/autonomy/opus-capacity-campaign-20260908/**'` to the example, and add: "campaign reports are not repository evidence; if your only hit is a sibling's report, that is not prior art and not a refutation."

---

**RANK 3 — OVER-SCOPED (silent on the root), every worker, still live.**
CORPUS-CONTEXT.md:8–15 draws the tree correctly:
```
/tmp/claude-0/frozen-corpus/extracted/
    README.md
    corpus/          <- 5,996 selected source files …
```
but **CORPUS-CONTEXT.md never states that the repository-relative root is `…/extracted/corpus/`.** The correction exists only at WAVE-LOG.md:336–337, in a file not every worker reads. The document that all workers read for corpus guidance still names `…/extracted/` as the address (line 9) and then says at line 54 "Before any novelty, absence or identifier claim … check this corpus" — which is the exact instruction that produced the wrong-root absence claim. The fix landed in the log, not in the file that seeds it. This is the single highest-value edit available.

*Smallest correct restatement:* insert after line 15 — "**Repository-relative paths live under `/tmp/claude-0/frozen-corpus/extracted/corpus/`, NOT under `…/extracted/`.** Searching the outer directory finds nothing and looks like absence. A path that resolves under `corpus/` is present; a path that does not is UNKNOWN, never absent."

---

**RANK 4 — OVER-SCOPED, three separate citations, coordinator + any worker following them.**
Three WAVE-LOG citations name a repository-relative path and a line number without saying the file is **corpus-only** or **corpus-divergent**. Each reproduces the shape that already caused harm.

- WAVE-LOG:87 — "`portfolio-2026-09-05/recommendation.md:70`". **Read.** In the corpus that file is 80 lines and line 70 is verbatim `| User-rejected paper: remain closed | PUB-EMC-CLASSIFICATION |` — the citation is exactly right *there*. In the **live checkout** the same path is **39 lines**, has no line 70, and `grep -n 'PUB-EMC-CLASSIFICATION'` returns nothing. A worker resolving the citation in the live tree finds a shorter file and could conclude the closure is unrecorded. The two copies genuinely differ (`diff -q` reports "differ"). *Restatement:* "`portfolio-2026-09-05/recommendation.md:70` **in the frozen corpus** (`…/extracted/corpus/…`); the live checkout's copy of this path is 39 lines and does not carry the row."
- WAVE-LOG:397 — "`research/autonomy/next-paper-2026-09-07/selection.md` L56–58". **Read.** Quote CONFIRMED verbatim at those lines in the corpus. Path **does not exist** in the live checkout. *Restatement:* add "(corpus-only; absent from this checkout)".
- WAVE-LOG:403 — "`research/autonomy/nr4a3-program-source-2026-09-07/README.md` L53". **Read.** Quote CONFIRMED verbatim as the opening of line 53 in the corpus. Path **does not exist** in the live checkout. *Restatement:* same annotation.

---

**RANK 5 — SUPERSEDED, coordinator-facing.**
WAVE-LOG.md:12: `| — | cumulative dispatches | 48 workers dispatched across all waves |`. Stale: `reports/` held **145** files at `ff6bb018` and **150** at `215ed8e7`, across **31** distinct base worker numbers and 150 distinct worker IDs. The row carries `—` for its timestamp, so it cannot even be read as "as of". *Restatement:* give it a UTC stamp, or replace with the recomputable "report files collected: N as of <HEAD>".

**RANK 6 — SUPERSEDED, low exposure.** CORPUS-CONTEXT.md:21 pins the supporting ref at `codex/opus-cloud-inputs-20260908 @ ad34f06b…`. WAVE-LOG:270–272 records that ref fetched forward to `ba8b66ea…` with `ad34f06b` as its parent. Both objects exist here. Harmless because the corpus ZIP hash is independently pinned, but the two files disagree. *Restatement:* "`ad34f06b…` was the ref at corpus-verification time; it has since advanced to `ba8b66ea…` (see WAVE-LOG ~02:52Z)."

**RANK 7 — CONFIRMED-as-written but materially weaker than it reads.** CORPUS-CONTEXT.md:6 — "it is **read-only** (`chmod -R a-w`)". The mode is real (`dr-xr-xr-x`, `-r--r--r--` throughout). But `id -u` = **0**: every worker runs as root, and root bypasses mode bits. `test -w` on the corpus root returns **writable**. The corpus is protected by worker discipline and by my write-isolation instruction, not by the filesystem. *Restatement:* "read-only by mode (`chmod -R a-w`); workers run as **root**, so this is a guard-rail, not an enforcement — do not write to it."

**RANK 8 — UNVERIFIABLE (honestly so, in both cases).**
- CORPUS-CONTEXT.md:32 / README / provenance: snapshot base `93b75888e31976195145e2404373b2d7a512f6d1`. `git cat-file -t` → **"could not get object info"**. The object is not in this repository, so no worker can check out or diff the base. This is *consistent with* the file's own lines 37–40 ("NOT a `93b` Git checkout"), so it is correctly labelled — I record it so no worker wastes a call trying.
- WAVE-LOG.md:147–154 (writer-4878 tier baseline: commit-loop 1497/1500 in 105 files, modalities 7249, paper-guards 973) — owner-measured on a different tree, unreachable from here. Correctly attributed in the log. The arithmetic built on it checks out: 1497+18 = **1515**, exceeds 1500 by **15** (WAVE-LOG:156, 251–253); 1466+18 = **1484** (WAVE-LOG:157); 7247+8 = **7255** (WAVE-LOG:193).

---

### CONFIRMED — recomputed or read, not assumed (25)

| # | Item (file:line) | Check | Class |
|---|---|---|---|
| 1 | CORPUS-CONTEXT:11 — 5,996 files under `corpus/` | `find … -type f \| wc -l` = **5996** | CONFIRMED |
| 2 | CORPUS-CONTEXT:26 — members 6,002 = 1 README + 5,996 + 5 metadata | 6002 total; metadata = **5** | CONFIRMED |
| 3 | CORPUS-CONTEXT:30 — uncompressed bytes under `corpus/` 236,150,544 | `awk` sum = **236150544** | CONFIRMED |
| 4 | CORPUS-CONTEXT:29 — symlink members 0 | `find -type l` = **0** | CONFIRMED |
| 5 | CORPUS-CONTEXT:13–14 — the five metadata filenames | all five present, names exact | CONFIRMED |
| 6 | CORPUS-CONTEXT:11 — corpus covers AGENTS.md, CLAUDE.md, README.md, research/, scripts/, systems/ | `ls corpus/` = exactly those six | CONFIRMED |
| 7–12 | CORPUS-CONTEXT:37–46 — six quoted `snapshot-provenance.json` strings (`identity`, `is_complete_repository`, `contains_git_history`, `is_git_commit_materialization`, `absent_files`, `no_new_source_material`/`no_source_fetch`/`no_scientific_acceptance`) | **read** the JSON; all verbatim | CONFIRMED |
| 13 | CORPUS-CONTEXT:44–45 — tracked-file-map "lists more than what is present" | **10,566** lines vs 5,996 selected | CONFIRMED |
| 14 | COMMON-BRIEF:22 — `scripts/preflight.sh` | exists, executable | CONFIRMED |
| 15 | COMMON-BRIEF:51 — `rg` available | ripgrep 14.1.0 | CONFIRMED |
| 16 | COMMON-BRIEF:52 — `CLOSED-WORK.md` in this directory | present at HEAD (70 lines) | CONFIRMED (fails only at the pinned commit — Rank 1) |
| 17 | COMMON-BRIEF:16 — scratch writable under `/tmp/claude-0/` | wrote two files there | CONFIRMED |
| 18 | WAVE-LOG:352–354 — junction dir holds **13** files, named | `find` = **13**, names match one-for-one | CONFIRMED |
| 19 | WAVE-LOG:345–347 — three files' bytes **7,227 / 3,870 / 2,599** and sha256s | `stat`+`sha256sum`: **all six match exactly** | CONFIRMED |
| 20 | WAVE-LOG:366–367 — dir "absent from this cloud checkout, present in the frozen corpus" | absent in worktree **and** `git log --all` finds no commit touching it; present in corpus | CONFIRMED |
| 21 | WAVE-LOG:418–419 — `markers.zip` 788,065 B, `peaks.tsv` 3,041,469 B, `paper.html` 301,282 B | grep of tracked-file-map: **all three exact** | CONFIRMED |
| 22 | WAVE-LOG:421 — "60 tracked paths in all" | `grep -c` = **60** | CONFIRMED |
| 23 | WAVE-LOG:420–421 — `bed-members.tsv` covers all **32** BEDs | 33 lines = header + **32** | CONFIRMED |
| 24 | WAVE-LOG:63–65 — `lint_citations.py` **exit 1** | re-ran at `ff6bb018`: **LINT_EXIT=1** | CONFIRMED |
| 25 | WAVE-LOG:67–69 — every `::error::UNANCHORED` names a campaign report file | **221** UNANCHORED lines, **221/221** under `…/opus-capacity-campaign-20260908/reports/`, zero elsewhere | CONFIRMED |
| 26 | WAVE-LOG:160–161, 193 — commit-loop **1466/1500 across 102 files** on this checkout | `tier_budget.py --check`, exit 0: `ok commit-loop 1466/1500 test function(s) in 102 file(s)` | CONFIRMED, independently reproduced |
| 27 | WAVE-LOG:193 — W17f's modalities base 7247 | same run: `ok modalities 7247/7500` | CONFIRMED |
| 28 | WAVE-LOG:88 — `icdo-9231-restriction-audit.json:48` retains unquantified residual and loss of genuine bone-primary EMC | **read** line 48 = `"the_bound_the_ledger_line_drops"`, states both residuals "unquantified" and the loss of primary EMC of bone; live copy byte-identical to corpus copy | CONFIRMED |

**Notable positive:** the entire corpus-verification block of CORPUS-CONTEXT.md (counts, byte totals, symlinks, provenance quotes, the map-is-larger caveat) is accurate on every item I could recompute — **13 of 13**. The `~02:58Z` root correction in WAVE-LOG is accurate to the byte on all six hash/size anchors. The two defects W21d measured as no longer recurring are not recurring in the briefing files either. The problem is not that the briefs are sloppy; it is that the *one* line workers use to address the repository (the frozen commit) is wrong, and the *one* correction that mattered was written into the log instead of into the file every worker reads.

## Validation evidence

All **RUN**, all read-only, `cwd=/home/user/Rare-cancers` unless noted, exit codes as shown.

```
git cat-file -t 92abbcb905cacf07f14b238db50d1b98f6590374        → commit
git merge-base --is-ancestor 92abbcb… HEAD                      → IS_ANCESTOR_OF_HEAD=yes
git rev-list --count 92abbcb…..HEAD                             → 23
git ls-tree -r --name-only 92abbcb -- research/autonomy/opus-capacity-campaign-20260908 | wc -l   → 0
git ls-tree -r --name-only HEAD    -- research/autonomy/opus-capacity-campaign-20260908 | wc -l   → 156
git cat-file -t 93b75888e31976195145e2404373b2d7a512f6d1        → fatal: could not get object info
find /tmp/claude-0/frozen-corpus/extracted/corpus -type f | wc -l            → 5996
find /tmp/claude-0/frozen-corpus/extracted -type f | wc -l                   → 6002
find … /corpus -type f -printf '%s\n' | awk '{s+=$1} END{print s}'           → 236150544
find /tmp/claude-0/frozen-corpus/extracted -type l | wc -l                   → 0
wc -l …/metadata/tracked-file-map.txt                                        → 10566
id -u                                                                        → 0
test -w …/extracted/corpus                                                   → WRITABLE   (root bypasses dr-xr-xr-x)
find …/corpus/research/autonomy/nr4a3-patient-junction-source-2026-09-07 -type f | wc -l  → 13
sha256sum README.md retrieval.json brenca-correction-pubmed.json →
  55dc009f52373fa28faf9aa22037db552f9625aee7646f3d3d8957794e1750c2   (7227 B)
  a5216ca7edcf00694cf58625f85cf991f77d3b85aea1a19902aef998aefee273   (3870 B)
  c83fbdbf5adb54721a59088f5db824d099960bc56d05b191019e74ea9a343172   (2599 B)
grep -c 'nr4a3-program-source-2026-09-07/' metadata/tracked-file-map.txt      → 60
wc -l recommendation.md   live → 39      corpus → 80
timeout 300 python3 scripts/tier_budget.py --check   → TIER_EXIT=0
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
timeout 420 python3 research/manuscripts/lint_citations.py > /tmp/claude-0/w35/lint.txt 2>&1
   LINT_EXIT=1 ; 642 lines ; 221 ::error::UNANCHORED ; 221 under …/reports/ ; 0 elsewhere
```

**PROPOSED (NOT RUN):** whole-ZIP sha256 `b474cd2f…`, the six part hashes, the 6,001/6,001 per-file provenance sweep, and `ZipFile.testzip()` (CORPUS-CONTEXT:22–31) — the ZIP parts are not in my execution area and re-verifying 236 MB was outside my budget. I verified the *extracted* counts, sizes and three member hashes instead, all of which agree.

## False-positive discipline — read versus counted

**Read in full before promoting:** COMMON-BRIEF.md (84 lines), CORPUS-CONTEXT.md (63), WAVE-LOG.md (451); `metadata/snapshot-provenance.json`; `extracted/README.md`; `corpus/…/next-paper-2026-09-07/selection.md` L54–60; `corpus/…/nr4a3-program-source-2026-09-07/README.md` L53; `corpus/…/portfolio-2026-09-05/recommendation.md` L68–72; `…/icdo-9231-restriction-audit.json` L44–52; the 13-file `find` listing.

**Counted only, never promoted to a claim about content:** the 108 report files matching a briefing-file name; the ~127 files containing `92abbcb`; the 221 UNANCHORED lines (I read the pattern of their paths via `grep -c` on two complementary filters — 221 in / 0 out — but did not read the 221 lines individually); the 10,566 tracked-map lines; the 5,996 / 6,002 file counts; the ten distinct recorded HEADs (I checked ancestry, I did not read the reports that recorded them).

**Not treated as evidence:** I did not treat any absence as a repository-wide absence. Every absence I report is stated as "absent from *this checkout*" or "absent from the corpus snapshot", tested at the **corrected** root `…/extracted/corpus/`, never at `…/extracted/`.

## Limitations

- HEAD moved from `ff6bb018` to `215ed8e7` during the run; two counts (`reports/` file count, and the final `git status`) are against the later commit and I say so at each. The `lint_citations` and `tier_budget` runs are against `ff6bb018`.
- I audited three files. CLOSED-WORK.md is W33's; the 150 reports are not in scope and I make no claim about their content.
- I could not verify the writer-4878 baseline, the owner's terminal runs, the ZIP-level hashes, or anything at snapshot base `93b`, which is not an object here. Those stay UNVERIFIABLE-from-here and are correctly labelled in the log already.
- Exposure ranking is a reasoned ordering from "which file does a worker必 read", plus the realised `92abbcb` count. It is not a measurement of future dispatches.
- No cohort, independence or patient claim is made or implied. Nothing here touches the Brenca closure: PRJNA692081 / SRP301712 remain already recovered and DUPLICATE. I approached no denied route and did not touch the blocked NR4A Perspective. No clinical claim; there is no wet lab.

## Stop condition

**Set up front:** stop when every standing fact in the three files is enumerated and classified, or at ~40 tool calls / ~40 minutes. **MET** — 34 facts enumerated and classified in 11 tool calls and 3m35s; returning immediately rather than padding.

## Tool-call and wall-clock count actually used

**11 tool calls** (all Bash, all read-only outside `/tmp/claude-0/w35/`). **Wall clock 3 minutes 35 seconds** (03:26:40Z → 03:30:15Z). Well inside both targets.

## Next concrete action

**Coordinator edits COMMON-BRIEF.md:7–8 and inserts one line into CORPUS-CONTEXT.md after line 15 — before the next dispatch.** Those two edits close Rank 1 and Rank 3, the only two findings that reach *every* future worker, and both have their replacement text written out above ready to paste. Ranks 2, 4, 5 and 6 are single-line annotations that can follow in the same commit but do not gate dispatch. Do not re-pin a new "frozen" commit: HEAD demonstrably advances during the campaign, so the honest instruction is "record the HEAD you read", which is what every worker was already doing correctly in spite of the brief.
