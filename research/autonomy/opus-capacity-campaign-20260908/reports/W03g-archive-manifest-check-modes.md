<!-- collected 2026-09-08T03:43:42Z by campaign coordinator; agent id a414ed22859713d43; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a414ed22859713d43.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

- **Worker:** W03g, lane 3, OPUS-CAPACITY-CAMPAIGN-20260908. Named successor to W03f.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the runtime model from the child transcript.
- `date -u` **start:** `Tue Sep  8 03:37:49 UTC 2026`. **end:** `Tue Sep  8 03:39:56 UTC 2026` (report drafting followed).
- `git rev-parse HEAD` **start:** `1c9d827870599576c0c027a9134363d59456fd04`. **end:** `5ae0fa04ff9516ac8f820381079d644a094f4a77`. **HEAD moved under me** (as the corrected brief anticipates — no pin). All live-tree measurements below were taken between those two commits; the module and chain files I read were not touched by either (`git status --porcelain` empty at start and end).
- `git status --porcelain` start: empty. End: empty. **I wrote nothing in `/home/user/Rare-cancers` and ran no git write operation.** All execution was under `/tmp/claude-0/w03g/`, which I deleted before returning (`ls -d /tmp/claude-0/w03g` → `No such file or directory`).
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (verbatim, with five very long proxy/truststore lines — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — elided as noted; 51 lines total at start and 51 at end, byte-identical set):

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

Would `scripts/regenerate_aso_chain.sh --check` reach its own `CANNOT VOUCH FOR` summary line (`:481-484`) if its archive-manifest step called `aso_archive_manifest.py --check-archive` instead of `--check`? And, precisely, what does each of the two modes assert?

Open because W03f measured the summary block unreachable behind the `fail` exit at `:466`, identified `--check-archive` from the module's own source as the revision-independent alternative, but could measure neither mode without confound: its scratch copy had no `.git`, so both modes went red for `.git`-absence reasons and the live-tree outcome was explicitly graded PREDICTION (NOT RUN).

## Prior-work check

Read in full: `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, and `reports/W03f-chain-check-end-to-end.md`. I am the successor W03f named; I did not replay its measurements, I resolved the one it could not.

Commands run for orientation and source reading (all read-only):

```
git rev-parse HEAD ; git status --porcelain
grep -n -- 'check_archive|check-archive|"--check"|--check\b|add_argument' research/manuscripts/aso_archive_manifest.py
sed -n '1830,1900p;1900,2000p;1530,1600p;945,975p' research/manuscripts/aso_archive_manifest.py
grep -n '_REPO_STATE_FIELDS' research/manuscripts/aso_archive_manifest.py
grep -n "open(.*[\"']w|\.write\(|os\.remove|shutil\.|mkdir|subprocess\.|urllib|requests" research/manuscripts/aso_archive_manifest.py
grep -n '_git\(' research/manuscripts/aso_archive_manifest.py
grep -n 'archive_manifest|archive manifest|_blocked_only|blocked=|fail=|unverified=|UNCHECKABLE|skipped=|prior-art' scripts/regenerate_aso_chain.sh
sed -n '140,235p;319,322p;425,500p' scripts/regenerate_aso_chain.sh
```

**Confirmed not replayed.** No network retrieval of any kind was attempted — in particular I did not repeat W03f's 113 s of proxy-denied Ensembl retries (I did not run `aso_noncoding_acceptor_screened_table.py` at all), and I attempted no `git fetch`. No Brenca/Hofvander/pazopanib/sunitinib/Wagner/CTARC/trabectedin route; no GSE4303/GSE28866; no lane-11 source-index work; the restricted NR4A Perspective was not touched under any framing. **No `reports/W25-*` was read, listed, or referenced.** I did not open a PUB-ASO review round, did not edit any manuscript, module, script or preregistration, did not author or apply a patch, did not run `scripts/preflight.sh`, and made no oligonucleotide claim.

## Method and inputs

**Files read (live checkout, `/home/user/Rare-cancers`, HEAD `1c9d8278…`→`5ae0fa04…`):**
`research/manuscripts/aso_archive_manifest.py` (2000+ lines; regions quoted below), `scripts/regenerate_aso_chain.sh` (486 lines).

**Read-only verification performed BEFORE running either mode**, as instructed:

- The module contains exactly **one** file-write site, `aso_archive_manifest.py:1974-1975` (`with open(OUT, "w", …) as fh: fh.write(text)`). It sits after both check branches return (`:1963` returns for `--check-archive`, `:1968-1972` for `--check`), so neither mode can reach it. `grep` for `open(...,"w")`, `.write(`, `os.remove`, `shutil.`, `mkdir` found no other write site.
- The only subprocess is `_git()` at `:952-958`, and every call site is a **read**: `ls-files -z` (`:921`), `status --porcelain` (`:986`), `rev-parse HEAD` (`:1538`), `rev-parse --git-dir` (`:1749`), `for-each-ref` (`:1751`, `:1762`), `cat-file -e` (`:1755`), `rev-parse --is-shallow-repository` (`:1757`).
- **No network**: no `urllib`, `requests`, `http` or socket use anywhere in the module.
- I ran both modes with `PYTHONDONTWRITEBYTECODE=1` so the interpreter could not leave `__pycache__` in the tree, and took `git status --porcelain` immediately before and after.

**Execution environment:** Linux, `python3` (system CPython), working directory `/home/user/Rare-cancers`, no network (agent proxy denies CONNECT). Chain-tail simulations run under `/bin/sh` in `/tmp/claude-0/w03g/`, outside the repository. **These are not preflight results.**

## Result

### R1 — What the two modes assert, precisely (PRIMARY, source-quoted)

Both modes share a dispatch flag at `aso_archive_manifest.py:1932`:

```
checking = "--check" in argv or "--check-archive" in argv
```

**Common inputs and common preconditions (`:1932-1956`).** Both read the committed artifact `OUT` (`research/manuscripts/aso/fusion-junction-aso-archive-manifest.json`) into `old_text`; if it is absent they print `STALE: no manifest on disk` and **return 1** (`:1950-1952`). Both then run `_dirty_tree_refusal(old_text)` and **return 1** on a refusal (`:1953-1956`) — the header at `:1938-1941` states this provenance gate "runs before `build()`" and "gates both modes" deliberately. Both then call `build()` (`:1957`), which re-derives the full inventory: `git ls-files` (`:921`), a SHA-256 per archived file, and the repository-state fields.

**`--check-archive` — the predicate (`:1958-1966`):**

```
if "--check-archive" in argv:
    old = json.loads(old_text)
    if _archive_only(old) != _archive_only(art):
        print("STALE: the archive inventory would change — re-run without --check", …); return 1
    print("manifest inventory is current (repository-state fields not compared)"); return 0
```

Predicate: *the committed manifest, with the repository-state fields dropped, equals a freshly built manifest with the same fields dropped.* `_archive_only` is defined at `:1859-1860` and drops exactly `_REPO_STATE_FIELDS = ("git_revision", "git_tree_is_clean_apart_from_this_manifest")` (`:1674`). Exit **0** = inventory current, **1** = inventory would change (or a shared precondition failed).

**`--check` — the predicate (`:1967-1972`):**

```
if old_text != text:
    print("STALE: manifest would change — re-run without --check", …); return 1
print("manifest is current"); return 0
```

Predicate: *the committed manifest's bytes equal the freshly serialised artifact's bytes* — a whole-file byte comparison, `git_revision` and `git_tree_is_clean_apart_from_this_manifest` **included**. Exit **0** = byte-identical, **1** = any difference.

**Why one is revision-dependent and the other is not — the module says so in its own words.** `:1538` stamps `"git_revision": _git("rev-parse", "HEAD")`, and the comment at `:1542-1548` reads:

> `git_revision` MOVES ON EVERY COMMIT, INCLUDING COMMITS THAT TOUCH NO ARCHIVED FILE, so `--check` goes red after any commit and must NOT be wired into preflight as a gate: it would cry wolf on every push and be switched off, which is how a real staleness would then be missed. It is a PRE-DEPOSIT check (step 2), run deliberately by a human at the moment the hashes have to be true.

`_archive_only`'s docstring (`:1845-1857`) records that this was not theoretical — `--check` *was* wired into preflight and failed on the first commit after (2026-08-17) — and states the separation:

> `--check-archive` asks "does the FILE LIST still describe the tree?" — stable across commits, safe in preflight, and it is the question that catches a real staleness.
> `--check` keeps asking the strict question, including the revision, and stays the PRE-DEPOSIT check a human runs at the moment the hashes have to be true.

So: `--check` is revision-dependent because `git_revision` is one of the compared bytes and HEAD advances on every commit; `--check-archive` is revision-independent because `_archive_only` removes that field (and the clean-tree flag) from **both** sides of the comparison before diffing.

(For completeness, two further modes exist and are *not* what the chain's step calls: `--check-revision-published` at `:1909`, which reads the file on disk and never builds, and `--is-inventoried` at `:1888`.)

### R2 — Both modes run live, read-only, with real exit codes (PRIMARY, EXECUTED)

Live checkout, between HEAD `1c9d8278…` and `5ae0fa04…`:

| # | Command | Real exit | Verbatim output |
|---|---|---|---|
| A | `PYTHONDONTWRITEBYTECODE=1 python3 research/manuscripts/aso_archive_manifest.py --check` | **1** | `STALE: manifest would change — re-run without --check` (stderr) |
| B | `PYTHONDONTWRITEBYTECODE=1 python3 research/manuscripts/aso_archive_manifest.py --check-archive` | **0** | `manifest inventory is current (repository-state fields not compared)` (stdout) |

`git status --porcelain` was empty immediately before A and immediately after B — **neither run modified the tree.**

**W03f's R4 prediction is CONFIRMED, and its confound is now removed.** W03f predicted `archive manifest STALE`, exit 1, on a real `.git` checkout, grading it PREDICTION (NOT RUN); run A reproduces exactly that message and exit code with `.git` present, so the staleness is the documented revision drift, not `.git` absence. **And W03f's UNKNOWN on the inventory is now resolved to a positive result:** run B says the archive **inventory is current** at this HEAD. The manifest is stale only in the sense its own author documented as unactionable — the repository moved around a stationary archive.

### R3 — The concrete question: no, the swap alone does not reach the summary line (PRIMARY, executed on the chain's own tail; the per-step inputs measured live)

The chain's step is `scripts/regenerate_aso_chain.sh:423`:

```
run_step "archive manifest"    "python3 $MAN/aso_archive_manifest.py" "python3 $MAN/aso_archive_manifest.py --check"
```

Its tail decides in this order (`:449-486`):

| Line | Condition | Outcome |
|---|---|---|
| `:449-450` | `_blocked_only=1` iff `fail = 0` **and** `blocked` non-empty | — |
| `:464-467` | `fail != 0` | print `something is stale or failed`, **exit 1** |
| `:468-474` | `_blocked_only = 1` | print `INCOMPLETE (missing prerequisites)`, **exit 3** |
| `:475-480` | `ONLY` non-empty | `SCOPED`, **exit 0** |
| `:481-484` | `CHECK=1` and `unverified` non-empty | **the `CANNOT VOUCH FOR` summary**, exit 0 |

Swapping `--check`→`--check-archive` moves the archive-manifest step from `STALE` (`fail=1`, `:205`) to `current` (`:194`) — R2 run B measures exactly that verdict. But `blocked` is **not** empty on this machine. The prior-art-evidence step (`:319-320`) carries the prerequisite probe `git rev-parse --verify -q refs/remotes/origin/literature-cache`, and I measured live:

```
$ git rev-parse --verify -q refs/remotes/origin/literature-cache ; echo $?
1
$ python3 research/manuscripts/aso_priorart_evidence.py --check ; echo $?
REFUSED: origin/literature-cache does not carry ['literature/aso-priorart-fusiononco/_index.json',
'literature/aso-priorart-junction/_index.json']. Fetch it first: git fetch origin
literature-cache:refs/remotes/origin/literature-cache
2
```

Check fails, probe fails ⇒ `run_step` takes the `UNCHECKABLE HERE` branch at `:198-204` and appends to `blocked`. So with the manifest green, `fail=0` and `blocked` non-empty ⇒ `_blocked_only=1` ⇒ **exit 3 at `:474`, before `:481`.**

I demonstrated this by running the chain's own tail verbatim (`sed -n '449,486p'` of the real script) under `/bin/sh` in scratch, with the state variables set to the values I measured live:

| Simulation | `fail` | `blocked` | Exit | Last line printed |
|---|---|---|---|---|
| S1 — swap made, prior-art blocked (**the actual live state**) | 0 | prior-art | **3** | `ASO CHAIN: no staleness found, but the run was INCOMPLETE (missing prerequisites).` |
| S2 — swap made **and** `literature-cache` fetched | 0 | empty | **0** | `ASO CHAIN: every checkable producer is current, but --check CANNOT VOUCH FOR: …` + `Give each of those a --check mode; until then a green --check is a partial answer.` |

**Answer: NO — not by itself.** The swap is necessary but not sufficient. It removes the `:466` blocker and hands the chain to a *second* one at `:474`. Two conditions must hold together for the summary line to print on this machine:

1. the archive-manifest step stops setting `fail=1` (the `--check-archive` swap does this — measured, R2 B), **and**
2. `refs/remotes/origin/literature-cache` is fetched, so the prior-art step is checkable rather than blocked (a `git fetch`, i.e. a git write plus network — **I did not do it**, and the chain itself prices it at `$0, seconds`).

Grade: the two per-step inputs are **PRIMARY/EXECUTED** on the live tree; the tail control flow is **EXECUTED** on the script's own verbatim lines in scratch; the composed statement "a full swapped chain run would exit 3" is **source-derived, not executed end to end** — I did not run `regenerate_aso_chain.sh` itself (see Limitations).

### R4 — One residual `fail` source checked, and it is clean (PRIMARY, EXECUTED)

The chain's graded-artifact guard at `:148-157` sets `fail=1` when the on-disk and tracked counts of `junction-aso-offtarget-*-graded.json` disagree. It uses `git ls-files`, so W03f's `.git`-less copy could not exercise it in either arm. Measured live with the guard's own two commands: `tracked=39`, `ondisk=39` ⇒ equal ⇒ **guard does not fire**. This removes one candidate for a hidden second `fail` source.

## Validation evidence

**RUN.** Live checkout `/home/user/Rare-cancers` (HEAD `1c9d8278…`→`5ae0fa04…`) for V1-V5; `/bin/sh` in `/tmp/claude-0/w03g/` for V6-V7. `PYTHONDONTWRITEBYTECODE=1` on every Python invocation. No network. **Not preflight.**

| # | Command | Real exit | Key verbatim output |
|---|---|---|---|
| V1 | `git status --porcelain` (before A) | 0 | empty |
| V2 | `python3 research/manuscripts/aso_archive_manifest.py --check` | **1** | `STALE: manifest would change — re-run without --check` |
| V3 | `python3 research/manuscripts/aso_archive_manifest.py --check-archive` | **0** | `manifest inventory is current (repository-state fields not compared)` |
| V4 | `git status --porcelain` (after B) | 0 | empty — **no write by either mode** |
| V5a | `git rev-parse --verify -q refs/remotes/origin/literature-cache` | **1** | (no output) |
| V5b | `python3 research/manuscripts/aso_priorart_evidence.py --check` | **2** | `REFUSED: origin/literature-cache does not carry [...]. Fetch it first: git fetch origin literature-cache:refs/remotes/origin/literature-cache` |
| V5c | graded-artifact guard's own two commands (`git ls-files … \| grep -c -- '-graded.json'`; `ls … \| wc -l`) | 0 | `tracked=39 ondisk=39` |
| V6 | `sh t2.sh` — chain lines `449-486` verbatim, `fail=0`, `blocked=prior-art` | **3** | `ASO CHAIN: no staleness found, but the run was INCOMPLETE (missing prerequisites).` |
| V7 | `sh tail_nofetch.sh` — same lines, `fail=0`, `blocked=""` | **0** | `ASO CHAIN: every checkable producer is current, but --check CANNOT VOUCH FOR: …` |

Read-only pre-verification of both modes (required before V2/V3): single write site `:1974-1975` unreachable from either check branch; all seven `_git()` call sites are read subcommands; no networking imports. This was established by reading the source, before executing anything.

**PROPOSED (NOT RUN).**
- Executing `bash scripts/regenerate_aso_chain.sh --check` in the live tree — **deliberately not run**: W03f measured that it writes 7 files under `.pytest_cache/` at the repository root, which my write isolation forbids.
- The `--check`→`--check-archive` edit at `scripts/regenerate_aso_chain.sh:423` — **not made**; it is the PUB-ASO owner's decision.
- `git fetch origin literature-cache:refs/remotes/origin/literature-cache` — a git write and a network act; not attempted.
- W03f's three-producer wiring, and `submission_packet.py`'s fourth — not applied.
- Any degradation probe of `--check-archive` (does it actually go red when an archived file's bytes change?) — **not run**; see Limitations.

**No content-policy refusal occurred in this unit.** The one refusal encountered was `aso_priorart_evidence.py`'s own `REFUSED:` line, quoted verbatim above; it is a missing local git ref, not a policy refusal, and I did not route around it.

## Limitations

- I did not run the chain end to end. The composed claim in R3 is assembled from three separately executed pieces (the manifest step's new verdict, the prior-art step's blocked status, the tail's verbatim control flow) plus the reading of `run_step` at `:183-233`. It is **source-derived with executed components**, not a single executed chain run, exactly as the dispatch allows. If some step other than the two I examined sets `fail=1` on the live tree, the swap would not even reach the exit-3 branch. W03f measured only the archive manifest as `STALE` in its (`.git`-less) baseline and I closed the one guard its copy could not exercise (R4), but the three lint gates at `:429-431` and the remaining ~25 check-commands are **UNMEASURED by me on the live tree**.
- **HEAD moved during my run** (`1c9d8278…`→`5ae0fa04…`). V2/V3 were taken as a pair within seconds; a commit landing between them could in principle have changed `--check`'s answer, though not `--check-archive`'s — that is the whole point of the separation. Nothing here is a statement about any other commit.
- `--check-archive` exit 0 means only that the *inventory and hashes* still describe the tree. It is silent about `git_revision`, which remains stale by design; a deposit still needs the pre-deposit `--check` the module documents at `:1543-1548` and `:1592`. **Swapping the chain's step would therefore weaken what the chain asserts about the manifest**, from "byte-identical to a fresh build" to "the file list and hashes still match". That tradeoff is the substance of the decision and belongs to the PUB-ASO owner; the module's author argues at `:1845-1857` that it is the right one for an automated gate, but I am pricing the change, not endorsing it.
- I did **not** verify that `--check-archive` discriminates — i.e. that it goes red when an archived file genuinely changes. Its sensitivity is **UNKNOWN** from my measurement; a green result on an undegraded tree is not evidence of detection power.
- Nothing here is evidence about any oligonucleotide's efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab. A regeneration chain's exit code is a statement about file freshness and nothing else.

## Stop condition

Set up front: **stop as soon as (a) both modes' predicates, inputs and exit codes are stated with `file:line` quotes, (b) both modes have been verified read-only from source and then run live with real exit codes recorded, and (c) the reachability question has a yes/no answer with its blocking step named and graded.**

**Met.** (a) R1; (b) R2 with the pre-run write audit in Method; (c) R3 — **no**, blocked at `:474` by the prior-art evidence step's missing `origin/literature-cache` ref, demonstrated by running the chain's own tail lines under both states. W03f's R4 prediction confirmed and its `--check-archive` UNKNOWN resolved (R2). Scratch deleted. Returning now.

## Tool-call and wall-clock count actually used

**14 tool calls** (13 `Bash`, 1 `Read`; one `Bash` failed with a shell syntax error from a truncated `sed` range and was immediately re-run with the correct range). **Wall clock 03:37:49Z → 03:39:56Z ≈ 2.1 minutes of execution**, plus report drafting. Well inside the ~40/~40 target. No network call, no poller, no background task.

## Next concrete action

**For the PUB-ASO owner, one bounded decision now fully priced.** Making `scripts/regenerate_aso_chain.sh --check` reach its own `CANNOT VOUCH FOR` summary needs **two** changes, not one, and they must land together or the first buys nothing visible:

1. `:423` — call `aso_archive_manifest.py --check-archive` for the check-command (keeping `--check` as the human pre-deposit step the module documents). Measured effect: that step goes `current`, `fail` 1→0. Cost: the chain stops asserting `git_revision` freshness.
2. Fetch `origin/literature-cache` on the machine that runs the chain (the chain itself prints the exact command and prices it `$0, seconds`), or the run still exits **3** at `:474` with the summary unprinted.

With both, the chain exits **0** and finally prints the list of producers it cannot vouch for — at which point W03f's three wirings, plus `submission_packet.py`'s fourth, become the visible next item on that list rather than an invisible one. **The one thing worth measuring before adopting (1)** is the question I could not close: does `--check-archive` actually go red when an archived file's bytes change? A single bounded scratch experiment — copy the tree, perturb one inventoried file, run `--check-archive`, expect exit 1 — would settle whether the swap keeps the guard that matters or quietly disarms it. I did not run it; my unit was the reachability question, and it is answered.
