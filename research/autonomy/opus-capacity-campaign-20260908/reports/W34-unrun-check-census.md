<!-- collected 2026-09-08T03:38:44Z by campaign coordinator; agent id ac10f6df24031505d; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ac10f6df24031505d.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W34** — verification-mode reachability lane, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in this container's environment names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

- `date -u` **start**: `Tue Sep  8 03:26:20 UTC 2026` · **end**: `Tue Sep  8 03:35:24 UTC 2026`
- `git rev-parse HEAD` **start**: `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f` · **end**: `1c9d827870599576c0c027a9134363d59456fd04`. HEAD moved during my run (the coordinator is landing sibling reports). This is neither the brief's frozen `92abbcb…` nor any HEAD quoted by W13g/W03e/W27/W29. **All measurements below are valid for `ff6bb018`**, and I verified afterwards that the only difference between my `ff6bb018` scratch copy and the live tree is the coordinator's newly-added `reports/W*.md` files — no file I measured changed underneath me (evidence in Validation).
- `git status --porcelain` **start**: empty. **end**: empty. I created, moved and deleted nothing in the repository and ran no git write operation. All execution was under `/tmp/claude-0/w34/`.
- Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (captured at start):

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
JAVA_TOOL_OPTIONS=<truststore/proxy flags only>
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

**No variable names a model.**

## Question

W13g and W03e each found, independently and by different routes, a working `--check` that nothing invokes. **Is that a three-instance anecdote or a class — and how large is it?** Concretely: enumerate every non-test module in the repository that implements a `--check`-shaped verification mode, enumerate every runner that could invoke one, compute the set difference, and rank the unrun ones by what their artifact reaches.

This is disjoint from the two concurrent siblings by construction. W27b asks what a `--check` **asserts**; W29b asks whether a preflight **row** is reachable. I ask only whether anything **runs** a given `--check` at all — a module can have a perfect assertion and still never execute.

## Prior-work check

Commands run against the live tree:

```
cat research/autonomy/opus-capacity-campaign-20260908/{COMMON-BRIEF,CLOSED-WORK,CORPUS-CONTEXT}.md    # read in full
cat .../reports/{W13g-cross-file-gate-hole,W03e-aso-chain-guard-sweep,W29-preflight-row-provenance,W27-drift-gate-hash-census}.md
git ls-files | wc -l            # 7753
git ls-files '*.py' | wc -l     # 1490
git ls-files '*.sh' | wc -l     # 26  (5 under scripts/)
git ls-files '.github/workflows/*' | wc -l   # 173
git ls-files | grep -i regenerate            # exactly 2 chains
```

**No prior campaign report asks the reachability question.** The four reports I was given each measure a *subset* and each stops at its own boundary:

- **W13g** measured the 18 preflight loop rows (`scripts/preflight.sh:847-864`) and found `emc_rt_bed_reappraisal.py --check` unrun. It explicitly scoped itself to five artifacts, not to the repository.
- **W03e** measured 19 ASO-chain verification paths and found three producers declared check-less that have a `--check`. Scoped to the ASO chain.
- **W29** measured the same 18 rows for vacuous passes. Scoped to rows that *do* run.
- **W27** enumerated 130 non-test modules under `research/modalities` + `research/manuscripts` that define or dispatch on `--check`, but classified what each **compares**, never whether anything **calls** it. That is the nearest prior art and it is a different axis; W27's own next-action names the 78 unclassified modules, not reachability.

**CLOSED-WORK items confirmed not replayed**: no NR4A Perspective under any framing; no Brenca / Hofvander / pazopanib / sunitinib / Wagner / CTARC / trabectedin route; no GSE4303 or GSE28866 re-reading; no registry ICD-O work; no patient, specimen or oligonucleotide design work; no publication or aiXiv act. **No network was initiated by me deliberately.** Six modules attempted outbound egress under my command (Ensembl `rest.ensembl.org`, `403 Forbidden` at the proxy); I did not retry, reroute or work around any of them — they are recorded below as `rc 124` timeouts. No content-policy refusal was encountered. The frozen corpus at `/tmp/claude-0/frozen-corpus/` was not needed: every claim here is about code at the recorded live HEAD, not a novelty or absence claim about sources.

## Method and inputs

**Inputs.** All 7,753 tracked files at `ff6bb018`. Implementers: the 1,490 tracked `.py` files. Runners: `scripts/preflight.sh`, all 26 tracked `*.sh`, both `regenerate_*.sh` chains, all 173 `.github/workflows/*.yml`, and all 657 committed test files, plus 854 other tracked code files as a lower-priority runner class.

**Tools.** Python 3.11.15 (`/usr/local/bin/python3`), stdlib only; `git`, `grep`, `tar`, `diff`, `xargs`. No third-party package, no GPU, no paid API.

**My scratch code**, all under `/tmp/claude-0/w34/`: `impl2.py` (implementer enumeration), `final.py` (runner enumeration + set difference), `reach.py` (downstream-reach scoring), `runchecks.sh` (execution harness). Nothing was written into the repository.

**Step 1 — implementers.** A module *implements* a verification mode if a string literal matching `--(check|verify|validate)[a-z0-9_-]*` appears within a ±4-line window of `add_argument` / `argv` / `parse_args` / `argparse`. **The ±4-line window matters and I found it the hard way**: my first pass required the literal and `add_argument` on the *same* line and therefore missed `research/modalities/emc_ipd_survival.py`, whose `ap.add_argument(` is at `:960` and whose `"--check"` is at `:961`. That false negative surfaced only because the inverse scan flagged `tests.yml:334` as invoking a mode that "did not exist". I rebuilt the enumeration and re-ran everything. `--checkpoint-every` and `--checkpoint-h` were excluded by hand as non-verification flags.

**Step 2 — runners.** For each module stem, every non-comment mention in a runner file with a verification flag within a 3-line window counts as an invocation. Comment-only mentions are discarded (preflight and the workflows contain many lines *about* `--check` that do not run one). I then hand-resolved the two dynamic runners a static scan cannot follow: `regenerate_endpoint_chain.sh:51` (`python3 "research/manuscripts/$p.py" --check` over a 7-element `PRODUCERS` array) and `regenerate_aso_chain.sh`'s `$MOD` / `$MAN` / `$FIG` expansions.

**Step 3 — false-negative sweep.** For all 85 never-invoked modules I ran a deliberately *loose* co-occurrence test (module stem anywhere in a test/shell/workflow file that contains a verification flag anywhere). It returned 42 candidate pairs. I inspected each with a ±5-line window: **all 42 are comments, docstrings, or unrelated strings.** None is an invocation.

**Step 4 — greenness.** `tar --exclude=./.git --exclude='*/__pycache__'` copy to `/tmp/claude-0/w34/tree` (612 MB, no `.git`). All 79 never-invoked modules whose flag is literally `--check` were executed there with `timeout 60`, 8-way parallel, cwd `/tmp/claude-0/w34/tree`. **Nothing was executed in `/home/user/Rare-cancers`.** Write hazard was handled as the dispatch requires — I read the `--check` dispatch block of the eight top-ranked modules in source *before* running anything (quoted in Validation), and I additionally verified the empirical claim afterwards by byte-comparing the whole scratch tree against the live tree.

**Step 5 — ranking.** For each never-invoked module I extracted its committed artifact basenames from source, then counted references to those artifacts in four consumer corpora: `systems/graph/*` (weight 100 — `CLAUDE.md` §7 makes it authoritative model state), `pinned-figures.json` (50), tracked registry JSON (20), and `research/manuscripts/**/*.md` (1). **This score is a reference-count proxy, not a semantic impact measure**, and I label it as such.

## Result

### R1 — The class, counted (PRIMARY)

| | n |
|---|---|
| Non-test modules implementing a `--check`-shaped verification mode | **169** |
| …invoked with that flag by at least one real runner | **84** (50 %) |
| …**never invoked by anything** | **85** (50 %) |
| Runners invoking a verification mode on a module that lacks one | **0** |

**The class is not small. It is half the surface.** Three known instances were not the whole of it; they were three of eighty-five. Distribution of the 85: `research/modalities` 63, `research/autonomy` 10, `research/manuscripts` 10, `research/manuscripts/figures` 1, `research/hypotheses` 1.

Runner-class coverage of the 84 that *are* reached (a module may be reached by several): workflows 53, tests 36, preflight 25, regenerate chains 21, other shell 3.

### R2 — The six unrun-**and-red** modes: the actionable core (PRIMARY)

Of the 79 executed, **53 exit 0, 16 exit 1, 4 exit 2, 6 time out at 60 s on blocked Ensembl egress.** Most non-zero exits are environment artifacts of my scratch copy (absent `.git`, blocked network, a missing `--refresh` cache, a required argument I did not supply). Filtering those out by source inspection — no `git` subprocess, no `urlopen`/`http`, no `utcnow`/`time.time()` — leaves **six modules whose `--check` is deterministic, is red, and which nothing runs.** I re-ran all six a second time and got identical exit codes and identical messages.

| Rank | Module · `file:line` of the check entry | Verbatim output, `rc` | Reach (graph/pinned/md) | Grade |
|---|---|---|---|---|
| 1 | `research/modalities/emc_mtap_prmt5_figures.py:445,447` | `mtap-prmt5 figures --check: DRIFT census-route-expression-grading.json: stamped a21cdbebdda19710, now 5bc3c80c034dde77` + a second DRIFT on `emc-expression-panels.json`, **rc 1** | 6 / 2 / 54 | PRIMARY |
| 2 | `research/modalities/emc_mtap_locus_persample.py:472` | `DRIFT in: ['_generated_from', 'per_platform']`, **rc 1** | 2 / 1 / 31 | PRIMARY |
| 3 | `research/modalities/emc_prmt5_multiplicity.py:656` | `DRIFT in: ['per_platform']`, **rc 1** | 2 / 1 / 34 | PRIMARY |
| 4 | `research/modalities/alcam_precedent.py:323` | `DRIFT in: ['emc_specific_evidence']`, **rc 1** | 2 / 1 / 24 | PRIMARY |
| 5 | `research/manuscripts/figures/emc_fusion_frame_figure.py:269` | `STALE — an artifact changed since the figure was drawn; redraw it`, **rc 1** | 2 / 0 / 19 | PRIMARY |
| 6 | `research/modalities/aso_control_oligos.py:150` | `aso-control-oligos.json is stale; re-run without --check`, **rc 1** | 0 / 0 / 2 | PRIMARY |

**This is a qualitatively stronger finding than W13g's and W03e's.** Theirs were guards that are *green today* and would catch a hypothetical future edit. These six are guards that are **red right now** and have been telling nobody. Ranks 1-3 are the MTAP/PRMT5 family and their artifacts are referenced from `systems/graph/`. I state plainly what I have **not** established: I have not determined whether each red is a stale committed artifact, a changed input, or a generator whose output is not reproducible in this container. That diagnosis is per-module work and belongs to the module owner.

`research/modalities/cd248_precedent.py:437` reports the same `DRIFT in: ['emc_specific_evidence']` shape at rc 1, but it makes one `git` subprocess call, so I cannot separate real drift from my `.git`-less scratch copy. **UNKNOWN**, and it is the first thing to re-check in a tree with `.git`.

### R3 — The highest-reach unrun modes that are green today (PRIMARY)

Green means: exits 0 on the current committed inputs, so it is armed and ready — and unwired.

| Reach score | `rc` | Module | graph / pinned / registry / md |
|---|---|---|---|
| 2215 | 0 | `research/modalities/sufex_second_handle.py:744` | 19 / 3 / 1 / 145 |
| 1419 | 0 | `research/modalities/fusion_cofold_recut.py:508,525` | 13 / 1 / 0 / 69 |
| 956 | 0 | `research/modalities/map_edit_anchors.py:529` | 8 / 2 / 0 / 56 |
| 724 | 0 | `research/modalities/emc_fet_idr_census.py:303` | 7 / 0 / 0 / 24 |
| 698 | 0 | `research/modalities/aso_delivery_antigen.py:833` | 6 / 1 / 0 / 48 |
| 656 | 0 | `research/modalities/realised_spend.py:434` | 5 / 3 / 0 / 6 |
| 572 | 0 | `research/modalities/hla_coverage.py:437` | 5 / 1 / 0 / 22 |
| 526 | 0 | `research/manuscripts/aso_coverage_ladder.py:1885` | 3 / 4 / 0 / 26 |

`sufex_second_handle.py` is the single highest-reach unrun verification mode in the repository — 19 `systems/graph` references and 3 pinned figures behind a `--check` that is green, correct as far as I can tell, and called by nothing.

`aso_delivery_antigen.py:833-844` is a direct convergence with W27, which ranked it **first** of its ten Class A+B modules for narrow comparison scope. My finding is orthogonal and compounding: **its comparison is narrow *and* nothing runs it.** Its check compares only `per_antigen` and `headline` — everything else in the artifact is uncompared — and no runner invokes it. Two independent workers ranked the same module first on two different axes.

W13g's `emc_rt_bed_reappraisal.py` sits at rank 46 by my reach proxy (`rc 0`, 1 graph / 0 pinned / 1 md). That is not a contradiction of W13g: its importance comes from what a *reversed published effect* means scientifically, which a reference count cannot see. It is a good illustration of my ranking's limit.

### R4 — What the top-ranked checks assert (PRIMARY, read from source)

| Module | What `--check` asserts | Writes during `--check`? |
|---|---|---|
| `target_route_census.py:363-371` | `open(OUT).read() != text` — full-text reproduction of the committed artifact against a fresh in-process build. `MISSING` if absent, `STALE` if different. | No — `return`s at `:371` before the `open(OUT,"w")` at `:373`. |
| `aso_delivery_antigen.py:833-844` | `per_antigen` and `headline` only, as sorted JSON, against a fresh build. | No — both branches `return` before `:845`. |
| `fusion_cofold_recut.py:525-526` | `return 0 if ok else 1` on the construct-cut validity flag, ahead of the write path that refuses to emit a mis-cut construct. | No. |
| `map_edit_anchors.py:529-530` | delegates to `check()`; the CLI path gates on `summary["all_accounted"]`, with a source comment explaining that a landed edit must not break the build. | No. |
| `emc_mtap_prmt5_figures.py:447-448` | delegates to `check()`; compares a stamped hash of each input artifact against its current hash. | No. |
| `sufex_second_handle.py:744` | `add_argument("--check", action="store_true", …)`; green at baseline. | No file changed (verified empirically in R5). |

### R5 — Zero of the 79 wrote anything (PRIMARY, and it is the reassuring number)

After all 79 `--check` runs plus six re-runs, `diff -rq --exclude=.git --exclude=__pycache__ /home/user/Rare-cancers /tmp/claude-0/w34/tree` returned **rc 0 with zero output lines** at the first measurement, and at the second measurement its only output was three `Only in …/reports:` lines naming `W01i`, `W03f`, `W06h` — sibling reports the coordinator landed in the live tree during my run. **Not one byte under `research/`, `systems/` or `scripts/` differs.** So: none of the 79 unrun `--check` modes writes during verification, and the live tree is provably untouched by me. This is the same negative that W03e measured for the ASO chain and W29 for the 18 preflight rows, now extended to the whole unrun class.

It also settles the HEAD-moved concern: every file I measured is byte-identical between my `ff6bb018` copy and the live tree.

### R6 — The inverse is empty, with one near-miss worth recording (PRIMARY)

**No runner invokes a verification mode on a module that does not implement one.** Every `.py` target paired with a verification flag in any `preflight` / shell / regenerate-chain / workflow / test file resolves to a module that implements that flag. The dynamic `regenerate_endpoint_chain.sh:51` loop was expanded by hand: all seven `PRODUCERS` (`endpoint_corpus`, `orr_dcr_reread`, `endpoint_regime_map`, `placebo_arm_calibration`, `endpoint_prior_art_audit`, `endpoint_regime_figure`, `endpoint_result_figures`) implement `--check`. All twelve `$MOD`/`$MAN`/`$FIG` targets in `regenerate_aso_chain.sh` implement theirs. **There is no silently-skipped row of that shape.** The only apparent hit, `tests.yml:334 → emc_ipd_survival.py --check`, was my detector's bug, not the repository's.

### R7 — Correction and extension to W03e: it is four, not three (PRIMARY)

`scripts/regenerate_aso_chain.sh` has **11** `run_step` rows with an empty check-command, for which it prints `⚠ NOT VERIFIED -- this producer has no --check mode` and ends with `--check CANNOT VOUCH FOR: <labels>` at exit 0. W03e found three of those producers to have a working `--check`. **There are four:**

| Line | Chain label | Producer | Status |
|---|---|---|---|
| 249 | chance baseline | `offtarget_chance_baseline.py` | HAS `--check` (W03e: REAL) |
| 264 | per-junction table | `aso_per_junction_table.py` | HAS `--check` (W03d: 8/8 degradations detected) |
| 265 | non-canonical acceptor table | `aso_noncoding_acceptor_screened_table.py` | HAS `--check` (W03e: REAL, guards the exon-2 lane) |
| **297** | **submission packet** | **`research/manuscripts/submission_packet.py`** | **HAS `--check` — not previously reported** |

The fourth is the interesting one, because `submission_packet.py --check` **is** one of preflight's 18 loop rows (W13g's transcription, row 8, `rc 0`). So the ASO chain prints "cannot vouch for the submission packet" about a producer the commit gate verifies on every run. The seven genuinely check-less rows are `junction_aso_locus_collapse.py`, four `figures/aso_*_figure.py`, `svg_to_submission_formats.py` and `build_submission_pdf.py`.

### R8 — The class-level reading

`scripts/preflight.sh` documents this exact defect against itself three times in its own comments (`:736, 761-765, 779, 789` — *"a `--check` that already existed and that nothing in the commit loop ran"*, *"NOTHING RAN IT"*), and `.github/workflows/tests.yml:142` and `autonomy-tick.yml:71` each carry a comment naming the same shape. W13g called `emc_rt_bed_reappraisal` the fourth recurrence. **The measurement says it is not a recurrence pattern at all: it is the default state.** Eighty-five modules, half the verification surface, sit unrun; the three or four found so far were found by incident, and each incident was written up as a one-off. The honest framing for the owner is not "fix the fourth" but "the repository writes verification modes faster than it wires them, and six are red today."

## Validation evidence

**Environment for every command**: Linux 6.18.44-fc-v24 x86_64, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Python 3.11.15 (`/usr/local/bin/python3`), stdlib only, no network initiated by me. Repository commands (`git ls-files`, `grep`, `sed`, `cat`, `git rev-parse`, `git status`) run read-only with cwd `/home/user/Rare-cancers`. **All module executions with cwd `/tmp/claude-0/w34/tree`.** `scripts/preflight.sh` was **not** run; `PREFLIGHT_FULL` was **not** set. Nothing here is a preflight result.

**RUN — the census.** `python3 /tmp/claude-0/w34/impl2.py` → `ALL py with a verification flag in argparse/argv context: 172` / `non-test modules: 169`. `python3 /tmp/claude-0/w34/final.py` → `invoked with that flag by a real runner: 84` / `NEVER invoked: 85` / `coverage by runner class (modules reached): {'test': 36, 'workflow': 53, 'preflight': 25, 'regen-chain': 21, 'shell': 3}`.

**RUN — the false-negative sweep.** `python3 /tmp/claude-0/w34/loose.py` → 42 candidate pairs; the ±5-line inspection returned `(no flag within +/-5 lines of any mention)` for 38 of them and, for the other four, only comment or unrelated-string matches (e.g. `.github/workflows/aso-offtarget.yml:375` is a `# ⛔ …ARE STAGED BECAUSE THE` comment; `research/modalities/tests/test_realised_spend.py:105` is an assertion *message* reading `"run: python3 research/modalities/realised_spend.py --write"`). **No invocation was missed.**

**RUN — the 79 executions.** `xargs -a checkonly.txt -n1 -P 8 /tmp/claude-0/w34/runchecks.sh` (each `timeout 60 python3 <module> --check`). Exit-code histogram, verbatim:

```
     53 0
     16 1
      6 124
      4 2
```

**RUN — determinism of the six reds**, second execution, verbatim (rc after each):

```
research/modalities/alcam_precedent.py            DRIFT in: ['emc_specific_evidence']                      rc=1
research/modalities/emc_mtap_locus_persample.py   DRIFT in: ['_generated_from', 'per_platform']            rc=1
research/modalities/emc_prmt5_multiplicity.py     DRIFT in: ['per_platform']                               rc=1
research/modalities/emc_mtap_prmt5_figures.py     DRIFT census-route-expression-grading.json: stamped
                                                  a21cdbebdda19710, now 5bc3c80c034dde77 …               rc=1
research/modalities/aso_control_oligos.py         aso-control-oligos.json is stale; re-run without --check rc=1
research/manuscripts/figures/emc_fusion_frame_figure.py
                                                  STALE — an artifact changed since the figure was drawn   rc=1
```

**RUN — write-hazard proof.** `diff -rq --exclude=.git --exclude=__pycache__ /home/user/Rare-cancers /tmp/claude-0/w34/tree` → **rc 0, 0 lines of output** (first measurement, after all 79 runs). Second measurement, after the six re-runs: three `Only in …/reports:` lines naming coordinator-added sibling reports, nothing else. A size-manifest diff over 7,824 files independently showed 49 changed lines, **all `__pycache__`**.

**RUN — the inverse scan.** 25 unique `(runner, line, target)` pairs pairing a `.py` with a verification flag; every one resolves to an implementing module, a `$`-expanded path I hand-resolved to an implementing module, or a documentation string (`research/manuscripts/thing.py`, `pins.py`, `generator.py` — none of which is a tracked file). **Zero `NO-SUCH-MODE` findings** other than one comment line in `test_the_readability_splitter_breaks_where_a_sentence_does.py:14` about `publish_bar.py`, which is prose, not an invocation.

**RUN — the chain audit.** A parser over `regenerate_aso_chain.sh`'s `run_step "label" "cmd" "check"` rows → `run_step rows with an EMPTY check-command: 11`, of which four resolve to producers that implement `--check` (table in R7).

**PROPOSED (NOT RUN)**, stated explicitly:
- I did **not** run any of the 85 `--check` modes in the live tree. Every exit code above is from `/tmp/claude-0/w34/tree`.
- I did **not** run the six modules whose only flag is `--verify` / `--verify-log` / `--verify-status` / `--validate-hydration` / `--validated` (`row4_pose_map_edits.py`, `linker_twobranch.py`, `seat_scratch.py`, `protfep_bench.py`, `nr4a3_abfe.py`, `nr4a_ternary_signature.py`). They are counted in the 85 but carry `rc = None`; their greenness is **UNKNOWN**.
- I did **not** diagnose *why* any of the six reds is red, and did **not** mutate any input to prove any guard discriminates. Discrimination for `emc_rt_bed_reappraisal.py` is W13g's measurement, not mine.
- I did **not** re-run `cd248_precedent.py` in a tree with `.git`.
- I authored **no** wiring change, no repair, and no gate edit.

## Limitations

- **The 85 is a lower bound on unrun modes and an upper bound on confidence.** My runner scan counts a mention within a 3-line window as an invocation, which over-credits: a workflow line that merely names a module near an unrelated flag would move it into the "invoked" column. Errors in that direction *shrink* my never-list, so 85 is conservative. It is not conservative in the other direction: a genuinely exotic invocation (a module invoked through a variable name that never contains its stem, a `Makefile` target I mis-classified, an invocation from a file outside my runner set) would be missed. I mitigated this with the loose sweep in Step 3 but cannot claim exhaustiveness.
- **The reach score is a reference count, not an impact measure.** It counts occurrences of an artifact's basename in four corpora. It cannot see that a reversed radiotherapy effect matters more than a well-cited housekeeping artifact — `emc_rt_bed_reappraisal.py` ranking 46th is exactly that failure. Use the ranking to triage, never to dismiss.
- **The reds are measured on a `.git`-less scratch copy with no network.** I filtered by source inspection for `git`/network/timestamp dependence, and re-ran for determinism, but a module could still consult `.git` through an indirection I did not grep for. The six reds are reproducible *in this environment*; confirming them in a tree with `.git` is one command the owner can run.
- **"Never invoked" is not "worthless".** A module's `--check` may be intended for manual use, may be documented in a runbook I did not read, or may be the deliberate manual half of a two-speed workflow. I measured automation, not intent.
- **This is a tooling audit.** Nothing here is a scientific result, and none of it bears on EMC efficacy, safety, selectivity or clinical readiness. There is no wet lab. A red `--check` on an MTAP/PRMT5 artifact means an artifact and its generator disagree — it says nothing whatever about the biology.
- I did not read the bodies of all 85 `--check` implementations; I read eight in source. For the other 77 my claim is reachability and exit code only, never assertion quality — that axis belongs to W27/W27b.

## Stop condition

**Set before any measurement:** return the moment (1) every non-test module implementing a `--check`-shaped verification mode is enumerated with `file:line`; (2) every runner class — preflight, all shell under `scripts/`, both regenerate chains, all workflows, all committed tests — is enumerated and its invocations resolved, including the dynamic ones a static scan cannot follow; (3) the set difference is computed and cross-checked with a deliberately loose false-negative sweep; (4) the unrun set is ranked by downstream reach rather than alphabetically, with greenness established for every one I can run without writing; and (5) the inverse is answered with a yes-or-no, not a maybe.

**MET, all five.** (1) 169 modules; (2) 856 runner files scanned, both dynamic chains hand-resolved; (3) 85 never-invoked, 42 loose candidates all inspected and all rejected; (4) ranked, with 79 of 85 executed for real exit codes and 6 honestly marked UNKNOWN; (5) the inverse is empty, and the one apparent hit was my own detector's bug, corrected and re-run. Returning immediately rather than extending into per-module diagnosis, which is owner work.

## Tool-call and wall-clock count actually used

**28 tool calls** (all `Bash`), **9 minutes 4 seconds** wall clock (`03:26:20Z` → `03:35:24Z`), plus report drafting. Well inside the ~40-call / ~40-minute target; I returned on meeting the stop condition rather than padding. One call ran in the background (the 612 MB scratch copy) while I computed downstream reach, per §2 of `CLAUDE.md`.

## Next concrete action

**Diagnose the six reds, in rank order, starting with the MTAP/PRMT5 family — and diagnose them, do not silence them.** The concrete first unit: run `python3 research/modalities/emc_mtap_prmt5_figures.py --check` in a tree that has `.git`, and determine for each of its two DRIFT lines (`census-route-expression-grading.json`, `emc-expression-panels.json`) whether the committed artifact is stale, an input changed, or the generator is non-reproducible. Then the same for `emc_mtap_locus_persample.py` and `emc_prmt5_multiplicity.py`, which report drift on the same `per_platform` key and are plausibly one cause with three symptoms. That unit is read-only up to the point of decision, needs no network, and ends in a finding the module owner can act on. **Expect the honest answer to be that an artifact needs regenerating; the fix is the drift, never the guard.** Add `cd248_precedent.py` to that batch — it shows the same `DRIFT in: ['emc_specific_evidence']` string as `alcam_precedent.py`, and the two are sibling precedent modules, so one cause probably explains both.

**Explicitly not recommended as the next action: wiring any of the 85 into a runner.** Wiring is a gate change and belongs to its owner, W03e priced one of its three at minutes of runtime the owner must approve, and — decisively — **six of these would turn the gate red on the next commit.** Wiring before diagnosis converts a silent problem into a blocked commit loop, and the owner would then be under pressure to weaken the guard, which is the one outcome this campaign must not produce. Diagnose first, wire second, and price the runtime once the reds are green.

**For the ASO-chain owner, available now and independent of all the above**: `regenerate_aso_chain.sh`'s `CANNOT VOUCH FOR` list is factually wrong for four rows, not three — line 297 (`submission_packet.py`) joins W03e's three, and its `--check` is already run by preflight on every commit. Correcting the four literal strings at `:249, :264, :265, :297` costs zero test functions against every tier ceiling. **I have not made that change.**
