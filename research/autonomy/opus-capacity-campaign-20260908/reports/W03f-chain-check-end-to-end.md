<!-- collected 2026-09-08T03:34:17Z by campaign coordinator; agent id aecba09f6b518962b; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-aecba09f6b518962b.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

- **Worker:** W03f, lane 3 refill, OPUS-CAPACITY-CAMPAIGN-20260908. Named successor to W03e.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the runtime model from the child transcript.
- `date -u` **start:** `Tue Sep  8 03:22:30 UTC 2026`. `date -u` **end:** `Tue Sep  8 03:26:57 UTC 2026` (report drafting followed).
- `git rev-parse HEAD` **start:** `302c2b63f7cc3ff16e2690de46e90a644181635f`. **end:** `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f`. **HEAD moved under me.** My scratch copy was taken at, and every measurement below is against, **`302c2b63f7cc3ff16e2690de46e90a644181635f`**.
- `git status --porcelain` **start:** empty (no output). **end:** empty (no output). The live tree is unmodified by me.
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (verbatim):

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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...(same list as no_proxy)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=/root/.ccr/java-truststore.p12 ... (proxy/truststore flags)
NO_PROXY=...(same list as no_proxy)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=...(same list as no_proxy)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

(The identical variable set was present at end; only the redacted token values and the three long proxy lists are elided above, and they were byte-identical between the two captures.)

## Question

`scripts/regenerate_aso_chain.sh` passes an empty check-command for three producers W03e measured as REAL — `aso_per_junction_table.py` (chain `:264`), `offtarget_chance_baseline.py` (`:249`) and `aso_noncoding_acceptor_screened_table.py` (`:265`) — so the chain prints `⚠ NOT VERIFIED -- this producer has no --check mode` about producers that have one.

**Two open sub-questions, both unmeasured before this report:**

1. What does `scripts/regenerate_aso_chain.sh --check` actually do end to end, unmodified? **Nobody had ever run the whole chain.** W03e enumerated and probed the producers individually and explicitly did not run the chain script itself.
2. What does wiring those three check-commands cost and buy — the change in exit code, in the `CANNOT VOUCH FOR` list, in wall time — and does any newly wired guard go red on a pristine tree?

## Prior-work check

Read in full: `research/autonomy/opus-capacity-campaign-20260908/{COMMON-BRIEF,CLOSED-WORK,CORPUS-CONTEXT}.md` and `reports/W03e-aso-chain-guard-sweep.md`. W03b/W03c/W03d were read as summarised inside W03e's own prior-work and Result sections (W03e restates their measured outcomes: W03b exon-2 = ALREADY-KNOWN; W03c mutation score 5/5, baseline 183 passed; W03d 8/8 degradations detected on `aso_per_junction_table --check`).

Commands run for prior work and enumeration:

```
cd /home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908 && ls reports/
sed -n '180,230p;240,330p;400,500p;1,60p' scripts/regenerate_aso_chain.sh
grep -n 'run_step "chance baseline"\|run_step "per-junction table"\|run_step "non-canonical acceptor table"' scripts/regenerate_aso_chain.sh
grep -n 'git_revision\|def build\|--check\b\|def main' research/manuscripts/aso_archive_manifest.py
grep -c -- '--check' <each of the 7 remaining unverified producers>
```

**Confirmed not replayed.** No network retrieval was attempted by me. No Brenca / Hofvander / pazopanib / sunitinib / Wagner / CTARC / trabectedin route; no GSE4303 / GSE28866; no lane-11 source-index work; the restricted NR4A Perspective was not touched under any framing. **I did not open a review round on PUB-ASO, did not edit any manuscript or preregistration, did not design or modify any oligonucleotide sequence, did not run `scripts/preflight.sh`, did not set `PREFLIGHT_FULL`, and performed no git write and no write of any kind inside `/home/user/Rare-cancers`.** I did **not** apply W03e's `submission_citations.py` repair, and I did **not** apply the three-line wiring to the live tree.

## Method and inputs

**Scratch copy, pinned.** `git rev-parse HEAD` → `302c2b63…`, then
`tar --exclude=./.git --exclude='*/__pycache__' -cf /tmp/claude-0/w03f/tree.tar .`, extracted twice:
`/tmp/claude-0/w03f/base` (pristine, 611 MB, no `.git`) and `/tmp/claude-0/w03f/patched` (611 MB).
Environment for every run below: Linux, CPython **3.11.15** (`/usr/local/bin/python3`), `pytest` as a standalone tool, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w03f/pycache`, working directory the scratch copy, **outside the repository**. No network (agent proxy denies CONNECT with `403 Forbidden`). **These are not preflight results.**

**Baseline (arm A).** `bash scripts/regenerate_aso_chain.sh --check` in `base`, unmodified, end to end; exit code, full stdout, stderr, `$SECONDS` wall time, and an mtime sweep `find base -newer STAMP` taken across the run.

**Wiring (arm B).** Exactly three string replacements in `patched/scripts/regenerate_aso_chain.sh`, verified by `diff` to be the only changes in the file (diff quoted below): each empty third field becomes `"python3 $MOD/<producer>.py --check"`. Nothing else changed; no guard weakened, reordered, removed, or re-thresholded. Then the same end-to-end `--check` run, same instrumentation.

**Write detection.** The scratch copies have no `.git`, so `git status --porcelain` is unavailable there; I used an **mtime sweep** (`touch STAMP; sleep 1; run; find <tree> -newer STAMP`) as instructed, before and after each arm, plus a per-command sweep for the three isolated producers and for `aso_archive_manifest.py --check`. The live tree's `git status --porcelain` was taken at start and end and is empty both times.

## Result

### R1 — The baseline: the chain's own `--check`, unmodified, end to end (PRIMARY)

Against `302c2b63`, in `/tmp/claude-0/w03f/base`:

| Measurement | Value |
|---|---|
| Command | `bash scripts/regenerate_aso_chain.sh --check` |
| **Real exit code** | **1** |
| Wall time | **8 s** |
| Steps reporting `current` | 14 |
| Steps reporting `⚠ NOT VERIFIED` | **11** |
| Steps reporting `UNCHECKABLE HERE` (missing prerequisite) | 1 — prior-art evidence |
| Steps reporting **`STALE`** | **1 — archive manifest** |
| Gates | `OK lint_consistency.py`, `OK lint_citations.py`, `OK lint_style.py` |
| Files modified anywhere in the tree during `--check` | **7, all under `.pytest_cache/` at the tree root; zero under `research/`** |

Final verdict printed:

```
ASO CHAIN: 1 step(s) could not run on this machine:
   · prior-art evidence (--check could not run) — git fetch origin literature-cache:refs/remotes/origin/literature-cache  ($0, seconds)
Each of those is a MISSING PREREQUISITE, not a stale artifact. Nothing above says the
deliverable is current -- it says nobody here could rebuild or verify it.

ASO CHAIN: something is stale or failed -- see above.
```

### R2 — The `CANNOT VOUCH FOR` list is **never printed** on this tree (PRIMARY — this is the headline)

The dispatch asked for "its full CANNOT VOUCH FOR list". **That block does not execute.** `scripts/regenerate_aso_chain.sh:464-467` exits 1 on `fail != 0`, and the `CANNOT VOUCH FOR` summary lives at `:480-484`, *after* it. Because the archive-manifest step is `STALE`, `fail=1`, and the chain exits at `:466` — so a reader who runs `--check` sees eleven scattered `⚠ NOT VERIFIED` lines interleaved through 27 steps but **never** sees the consolidated list, and never sees the sentence "until then a green `--check` is a partial answer."

I recovered the list mechanically from the per-step lines (`awk '/^== /{lbl=$0} /NOT VERIFIED/{print lbl}'`). The eleven, in chain order:

| # | Step label (baseline `--check`) | Producer has a working `--check`? |
|---|---|---|
| 1 | locus collapse | no (`junction_aso_locus_collapse.py`, 0 hits for `--check`) |
| 2 | **chance baseline** | **YES** (`offtarget_chance_baseline.py:709`) |
| 3 | **per-junction table** | **YES** (`aso_per_junction_table.py:404,408`) |
| 4 | **non-canonical acceptor table** | **YES** (`aso_noncoding_acceptor_screened_table.py:491,495`) |
| 5 | figure · junction space | no (0 hits) |
| 6 | figure · gap-length tradeoff | no (0 hits) |
| 7 | figure · multipartner seam | no (0 hits) |
| 8 | figure · chance baseline | no (0 hits) |
| 9 | figure submission formats | no (0 hits) |
| 10 | **submission packet** | **YES — NEW FINDING, see R5** |
| 11 | anonymized upload · journal format | not separately probed (`build_submission_pdf.py --paper aso-journal --anonymized`, `:374`) |

### R3 — After wiring the three: exit code, list, and cost (PRIMARY)

The whole diff (`diff base/scripts/regenerate_aso_chain.sh patched/scripts/regenerate_aso_chain.sh`), verbatim and complete:

```
249c249
< run_step "chance baseline"     "python3 $MOD/offtarget_chance_baseline.py"           ""
---
> run_step "chance baseline"     "python3 $MOD/offtarget_chance_baseline.py"           "python3 $MOD/offtarget_chance_baseline.py --check"
264,265c264,265
< run_step "per-junction table"  "python3 $MOD/aso_per_junction_table.py"              ""
< run_step "non-canonical acceptor table" "python3 $MOD/aso_noncoding_acceptor_screened_table.py" ""
---
> run_step "per-junction table"  "python3 $MOD/aso_per_junction_table.py"              "python3 $MOD/aso_per_junction_table.py --check"
> run_step "non-canonical acceptor table" "python3 $MOD/aso_noncoding_acceptor_screened_table.py" "python3 $MOD/aso_noncoding_acceptor_screened_table.py --check"
```

| Measurement | Baseline (arm A) | Wired (arm B) | Δ |
|---|---|---|---|
| Chain exit code | **1** | **1** | unchanged |
| Wall time | 8 s | **122 s** | **+114 s** |
| `⚠ NOT VERIFIED` steps | **11** | **8** | **−3** |
| Newly wired steps' verdicts | n/a | `chance baseline → current`, `per-junction table → current`, `non-canonical acceptor table → current` | **all three green** |
| Files modified under `research/` during `--check` | 0 | 0 | — |

**No newly wired guard goes red on the pristine tree.** All three report `current` at `302c2b63`. This is the answer to the dispatch's "if one does, that is the most important thing you can report": **none did.**

The chain still exits 1, for the same pre-existing reason (archive manifest `STALE`), so the `CANNOT VOUCH FOR` summary is still unreachable in arm B as well. **The wiring shrinks the per-step blind spots from 11 to 8; it does not change the chain's verdict, and it cannot, while the manifest step is red.**

**Cost attribution, isolated per producer** (`base`, one at a time, `$SECONDS`, write sweep after each):

| Producer `--check` | exit | wall | wrote anything |
|---|---|---|---|
| `research/modalities/offtarget_chance_baseline.py` | 0 | **0 s** | no |
| `research/modalities/aso_per_junction_table.py` | 0 | **0 s** | no |
| `research/modalities/aso_noncoding_acceptor_screened_table.py` | 0 | **113 s** | no |

So **113 of the 114 added seconds are one producer**, and they are the Ensembl-retry path W03e's R6 recorded: the agent proxy denies the CONNECT with `403 Forbidden`, the module retries four times per gene symbol and then falls back to the committed cache and says so. **That is correct behaviour and a runtime cost, not a defect.** I recorded the denial and did not retry it or reroute it. Two of the three wirings are free; the third makes an 8-second chain check into a two-minute one **offline**. On a network-reachable machine that cost should be far smaller, but I have not measured that and it is UNKNOWN here.

### R4 — Why the chain is red, and what my scratch copy can and cannot say about it (PRIMARY + PREDICTION)

`python3 research/manuscripts/aso_archive_manifest.py --check` in `base` → **exit 1**, `STALE: manifest would change — re-run without --check`, and the mtime sweep shows it **wrote nothing**. I then diffed the committed manifest against a fresh `build()` field by field:

| Drifting field | old (committed) | new (rebuilt in my copy) | Cause |
|---|---|---|---|
| `git_revision` | `1a2d667d77405070d794b1383961bacf3ad2951f` | `None` | no `.git` in the scratch copy |
| `git_tree_is_clean_apart_from_this_manifest` | `True` | `None` | no `.git` |
| `inventory_limited_to_tracked_files` | `True` | `False` | no `git ls-files` |
| `n_files` | 516 | 505 | 11 `.py` files dropped from the import closure |
| `gaps.import_closure.n_added` | 11 | 0 | same |
| `total_bytes` / `total_mib` / `archive_content_digest` | — | — | downstream of the above |

**Every drifting field traces to the missing `.git`.** So my measured `STALE` is **confounded** and I do **not** claim the archive manifest is genuinely stale on the live tree.

**But the chain is red on the live tree anyway, and this is source-grounded rather than measured.** `aso_archive_manifest.py:1538` stamps `"git_revision": _git("rev-parse", "HEAD")` and `--check` compares the full serialised artifact byte for byte (`:1969`). The module's own comment at `:1542-1544` states: "`git_revision` MOVES ON EVERY COMMIT, INCLUDING COMMITS THAT TOUCH NO ARCHIVED FILE, so `--check` goes red after any commit and must NOT be wired into preflight as a gate". The committed manifest records `1a2d667d…`; live HEAD at my start was `302c2b63…` and at my end `ff6bb018…`. `git merge-base --is-ancestor 1a2d667d… HEAD` → **true**, `git rev-list --count 1a2d667d…..HEAD` → **259**. So the manifest's revision is **259 commits behind HEAD**, and the chain's `--check` step for it must go `STALE` on the live tree for that documented reason.

**Consequence, and it is the practical finding of this report: `scripts/regenerate_aso_chain.sh --check` cannot return 0 on any tree whose HEAD has moved past the manifest's recorded revision — i.e. on essentially every tree — and while it is red, its own `CANNOT VOUCH FOR` summary is dead code.** Grade: the mechanism is PRIMARY (read from source, plus the two git reads above); the specific prediction "the live tree's chain `--check` exits 1 with `archive manifest STALE`" is **PREDICTION (NOT RUN)** — I did not execute anything in the live tree.

`--check-archive`, the module's stable inventory-only question, also returned 1 in my copy (`STALE: the archive inventory would change`), but for the same `.git`-absence reason (the 11 dropped `.py` files), so the **inventory** status at `302c2b63` is **UNKNOWN** from my measurement.

### R5 — New finding W03e did not have: a **fourth** mis-declared producer (PRIMARY)

`research/manuscripts/submission_packet.py` has a real `--check` at **`:553`**, added 2026-08-22 (its own comment: "`--check` ADDED 2026-08-22 (round 15 seat 5). This was the ONE deposit generator without…"). The chain wires it with an empty check-command at `:293` and therefore prints `⚠ NOT VERIFIED -- this producer has no --check mode` about it, in **both** arms.

Measured in `base`:

```
$ python3 research/manuscripts/submission_packet.py --check
submission packet reproduces from submission-metrics.json and the filesystem
PACKET_CHECK_EXIT=0
SECONDS=0
--- writes ---            (mtime sweep: empty)
```

**Green, sub-second, writes nothing.** It is a fourth free wiring the PUB-ASO owner should price alongside the three. I did **not** wire it, and its degradation sensitivity is **UNKNOWN** — I did not run a degraded-input probe on it, so "REAL" in W03e's sense is not established for it; all I measured is a green baseline and zero writes.

The other seven unverified producers were checked by `grep -c -- '--check'`: `junction_aso_locus_collapse.py`, `aso_junction_space_figure.py`, `aso_gap_length_figure.py`, `aso_multipartner_seam_figure.py`, `aso_chance_baseline_figure.py`, `svg_to_submission_formats.py` — **0 hits each**. For those six the chain's statement is factually correct. The eleventh row (anonymized upload) shares `build_submission_pdf.py` with three rows that *are* checked; I did not investigate it.

### R6 — `--check` writes nothing under `research/` in either arm, but it is not write-free (PRIMARY)

| Arm | Files newer than the stamp | Under `research/`? |
|---|---|---|
| A (baseline) | **7**: `.pytest_cache/` and its `CACHEDIR.TAG`, `README.md`, `.gitignore`, `v/`, `v/cache/`, `v/cache/nodeids` | **0** |
| B (wired) | **1**: the tree root directory itself (mtime bump only) | **0** |

The `.pytest_cache` writes come from the docx step, whose check-command is `pytest research/manuscripts/tests/test_the_word_manuscript_is_current_and_whole.py -q` (`:420-422`) — pytest's own cache, at the repository root, gitignored. Worth naming because the chain's `--check` is documented as "change nothing" (`:41`); it changes nothing that matters, but it is not literally a no-write operation.

### R7 — An environment defect of mine, reported rather than hidden (PRIMARY)

In arm B the step `Word manuscript · submission format` reported **`STALE`** where arm A reported `current`. **This is an artifact of my own scratch environment, not of the wiring change.** Mid-run the container filesystem hit `ENOSPC` (a tool call failed with "the temp filesystem … is full (0MB free)"; two 611 MB copies plus a 600 MB tar). That is also why arm B's sweep shows no `.pytest_cache` — pytest could not write it. I freed the tar (`df` went from ~0 to 4.3 GB free) and re-ran that exact step alone on the **patched** copy:

```
$ cd /tmp/claude-0/w03f/patched && pytest research/manuscripts/tests/test_the_word_manuscript_is_current_and_whole.py -q
.......                                                                  [100%]
7 passed in 0.03s
DOCX_CHECK_EXIT=0
```

So the wired chain's true unverified/stale profile is arm B's, **with the docx step green**: 8 unverified, 1 uncheckable (prior-art), 1 stale (archive manifest, confounded as in R4), exit 1. I did not re-run the full arm B after freeing disk, so the *composed* arm-B run with a green docx step is **PROPOSED (NOT RUN)**; the step itself is measured green.

## Validation evidence

**RUN.** All in `/tmp/claude-0/w03f/`, CPython 3.11.15, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/tmp/claude-0/w03f/pycache`, no network, outside the repository. Not preflight.

| # | Command | Real exit | Key output |
|---|---|---|---|
| V1 | `bash scripts/regenerate_aso_chain.sh --check` in `base` (unmodified, `302c2b63`) | **1** | `ASO CHAIN: something is stale or failed`; 11 `NOT VERIFIED`, 1 `UNCHECKABLE HERE`, 1 `STALE`; `WALL_SECONDS=8`; `NEWER_COUNT=8` (7 files, all `.pytest_cache`) |
| V2 | `bash scripts/regenerate_aso_chain.sh --check` in `patched` (3-line diff above) | **1** | 8 `NOT VERIFIED`; the three wired steps all `current`; `WALL_SECONDS=122`; `NEWER_COUNT=1` (root dir only) |
| V3 | `python3 research/manuscripts/aso_archive_manifest.py --check` in `base` | **1** | `STALE: manifest would change — re-run without --check`; write sweep empty |
| V4 | `python3 research/manuscripts/aso_archive_manifest.py --check-archive` in `base` | **1** | `STALE: the archive inventory would change — re-run without --check` |
| V5 | field-by-field diff of committed manifest vs fresh `build()` (inline `python3` heredoc importing the module) | 0 | the six drifting fields in R4, all `.git`-derived |
| V6 | `python3 research/modalities/offtarget_chance_baseline.py --check` | **0** | 0 s, wrote nothing |
| V7 | `python3 research/modalities/aso_per_junction_table.py --check` | **0** | 0 s, wrote nothing |
| V8 | `python3 research/modalities/aso_noncoding_acceptor_screened_table.py --check` | **0** | **113 s**, wrote nothing (Ensembl `403 Forbidden` retries, then committed-cache fallback) |
| V9 | `python3 research/manuscripts/submission_packet.py --check` | **0** | `submission packet reproduces from submission-metrics.json and the filesystem`; 0 s; wrote nothing |
| V10 | `pytest research/manuscripts/tests/test_the_word_manuscript_is_current_and_whole.py -q` in `patched` | **0** | `7 passed in 0.03s` |
| V11 | `git rev-parse HEAD` / `git merge-base --is-ancestor 1a2d667d… HEAD` / `git rev-list --count 1a2d667d…..HEAD` (live tree, **reads only**) | 0 / 0 / 0 | `ff6bb018…` / ancestor **yes** / **259** |
| V12 | `git status --porcelain` in the live tree, start and end | 0 | empty both times |

**PROPOSED (NOT RUN).**
- The three-line wiring applied to the live tree — deliberately **not** done; it belongs to the PUB-ASO owner.
- W03e's `submission_citations.py` repair — deliberately **not** applied.
- A full arm-B chain re-run on a disk with headroom (R7).
- Any degraded-input probe of `submission_packet.py --check` — its discrimination is UNKNOWN.
- Executing `regenerate_aso_chain.sh --check` in the live tree to confirm R4's prediction empirically.
- Any network retrieval; the proxy `403` was recorded, not retried or rerouted.

## Limitations

- **Every measurement is against `302c2b63f7cc3ff16e2690de46e90a644181635f`**, on a copy with **no `.git`**. HEAD moved to `ff6bb018…` during my run; nothing here is a statement about `ff6bb018`.
- The absent `.git` **confounds the one red step**. The archive-manifest `STALE` I measured is fully explained by `.git` absence (R4); my claim that the live tree is also red rests on source reading plus two git reads, not on an executed live run. It is a PREDICTION.
- `--check-archive` is likewise confounded, so the archive **inventory** status is UNKNOWN.
- Arm B ran under `ENOSPC` (R7), which corrupted exactly one step's verdict; I identified it and re-measured that step, but I did not re-run the composed arm B.
- `+114 s` is an **offline** cost dominated by proxy-denied Ensembl retries. The on-network cost of `aso_noncoding_acceptor_screened_table.py --check` is UNKNOWN.
- "All three wired guards green" says the artifacts are current at `302c2b63`; it says nothing new about whether those guards **discriminate** — that is W03d's and W03e's measurement, reused, not re-run here.
- Nothing in this report is evidence about any oligonucleotide's efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab. A regeneration chain going green is a statement about file freshness and nothing else.

## Stop condition

Set up front: **stop as soon as (a) the unmodified chain `--check` has a recorded real exit code, unverified list and wall time, (b) the wired chain `--check` has the same three, and (c) each newly wired guard's colour on the pristine tree is recorded — red or green — with no adjustment attempted.**

**Met.** (a) V1, (b) V2, (c) V2 + V6–V8: all three green, none adjusted. Two findings outside the stop condition arrived for free and are reported (R2: the summary block is unreachable; R5: a fourth mis-declared producer). Returning now.

## Tool-call and wall-clock count actually used

**22 tool calls** (2 of them background `Bash` launches; 1 `ToolSearch` whose loaded tool I then did **not** need to call; 1 hook refusal for a `&`-detached command, immediately corrected to `run_in_background`; 1 call lost to `ENOSPC` and re-run). **Wall clock 03:22:30Z → 03:26:57Z ≈ 4.5 minutes of execution**, plus report drafting. Both well inside the ~40/~40 target; W03e's 2.4× overrun was not repeated, and **no `until [ -f … ]; do sleep N; done` poller was issued at any point** — both long runs were tracked by the tool's own completion notification.

## Next concrete action

**For the PUB-ASO owner, one bounded task:** the wiring decision is now priced — three one-string edits, +114 s offline (113 s of it one producer's proxy-denied Ensembl retries), 11 → 8 blind steps, zero new red, zero writes — but it **buys nothing a reader can see until the archive-manifest step stops forcing exit 1**, because the `CANNOT VOUCH FOR` summary at `:480-484` is unreachable behind the `fail` exit at `:466`. So the successor task is: **run `bash scripts/regenerate_aso_chain.sh --check` once in a real `.git` checkout to confirm R4's prediction (`archive manifest STALE`, exit 1), and decide whether the chain should call `aso_archive_manifest.py --check-archive` — the module's own stable, revision-independent question, which its source at `:1855-1857` says exists for exactly this purpose — instead of `--check`, whose author documented it as going red after every commit.** That is the change that would let the chain reach its own summary line; the three (now four, with `submission_packet.py`) wirings should be priced as a package with it, not before it. **I did not make that change and it is not mine to make.**
