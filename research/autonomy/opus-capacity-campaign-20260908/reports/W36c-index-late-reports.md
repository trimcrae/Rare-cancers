<!-- collected 2026-09-08T04:32:14Z by campaign coordinator; agent id ab05a0ed8e751a322; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ab05a0ed8e751a322.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report below.

---

## Worker

**W36c**, second successor to W36 — routing-index extension over the reports added after `215ed8e7`. Advisory index only: I performed, adjudicated, sequenced and decided **nothing**.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. I did not observe the served model; no environment variable in this container names a model. The coordinator must extract the actual per-child runtime model from the transcript.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (full output, secrets redacted by the sed):

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
GLOBAL_AGENT_NO_PROXY=... (same host list)
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=... (proxy/truststore only)
NO_PROXY=... (same host list)
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=... (same host list)
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep 8 03:46:54 UTC 2026` | `Tue Sep 8 03:51:50 UTC 2026` |
| `git rev-parse HEAD` | `606d79f96526b651f3b825190d721f6b302c032e` | `cfc5f3dcbfccf4e05e8316be16f55d129826eb3a` |
| `git status --porcelain` | *(empty — clean)* | *(empty — clean)* |
| files in `reports/` | 175 → 178 (raced during the first two calls) | **187** |

I wrote nothing into `/home/user/Rare-cancers`, ran no git write operation, made no network call. Scratch `/tmp/claude-0/w36c/` created and **deleted** (`ls` confirms absent).

---

## Question

**How many routed-but-unlanded items did the reports arriving after `215ed8e7` actually add to W36's index, and did they create new conflicts?** W36 pinned to 150 reports and estimated the late arrivals carry "roughly four to seven further routed items and at least one new conflict" — an estimate over the **seven** reports it could see the names of. The measured late set is much larger, so the estimate's denominator was wrong.

---

## Prior-work check

Read **in full**: `COMMON-BRIEF.md` (111 lines, both corrections present), `CORPUS-CONTEXT.md` (73), `CLOSED-WORK.md` (70), `SAFETY-EVENTS.md` (35), and `reports/W36-routed-repair-index.md` (366 lines — counting rule at `:85`, class legend at `:93`, Tiers 1–5 at `:98/:122/:145/:188/:207`, conflict table at `:239-253`, growth conclusion at `:275-291`, successor note at `:366`).

I extracted W36's full U01–U102 anchor/target list mechanically (`awk -F'|' '/^\| U[0-9]/'`) **only to compute conflicts against it** — I did not re-verify any U-row. W36b owns that.

Closed items I confirm I am not replaying: the NR4A Perspective content-policy refusal (not read, not relabelled, not indexed as an open route); **W25 and every W25 continuation — not read, not referenced, not routed out of**; the user-rejected registry ICD-O paper; methylation; the clinical checkpoints; paired Davis; promoter transfer; Brenca; Hofvander/EGA; GSE4303/GSE28866; every denied retrieval route. Zero network calls; no paid API; no GPU. I did not run `scripts/preflight.sh`. Every module I executed I first read in source to confirm its check path writes nothing.

---

## Method and inputs

**Pinned set, determined by git, not by guessing** (`D=research/autonomy/opus-capacity-campaign-20260908/reports`):

```
git diff --name-only --diff-filter=A 215ed8e7 HEAD -- $D     # HEAD = e5d60db7
```

→ **28 files added**, 0 deleted, **1 modified** (`W14e-fake-guard-triage.md`). `git ls-tree -r --name-only 215ed8e7 -- $D | wc -l` = **150** (W36's number confirmed); at `e5d60db7` = **178**.

The 28 added, minus `W36-routed-repair-index.md` itself, give my **pinned set of 27 reports to index** (~8,200 lines):

`W01i, W02i, W03f, W03g, W06h, W06i, W09h, W14f, W16g, W16h, W18c, W24d, W26b, W27b, W28b, W29b, W29c, W29d, W30b, W31b, W31c, W33, W34, W35, W35b, W37, W38`

**Arrived after my pin and are UNINDEXED by me** (9, added between `e5d60db7` and `cfc5f3dc` during this run): `W03h, W26c, W27c, W28c, W29e, W29f, W30c, W34b, W39`. Several of these names indicate they answer items I list below (`W29f` = the pytest-availability question in my V-row for W29c; `W34b` = W34's six reds; `W39` = a cross-report contradiction census). They are **UNKNOWN to this index**.

Extraction, per W36's own method:
1. Marker-density census over the 27 (same 10-alternative grep W36 used) → ranking.
2. `awk '/^#+ .*[Nn]ext concrete action/{p=1;next} p&&/^#+ /{exit} p'` over all 27 → the residual each report hands on (read in full).
3. Path × routing co-occurrence grep for `report:line` anchors.
4. Tree verification on 13 checks (below).

**Counting rule — W36's, unchanged:** one distinct (proposed change **or** identified-and-refused decision **or** named measurement request) × (one target). Same change to same target across two reports = one item, two anchors.

---

## Result

### A. New routed items, folded into W36's tiers

`Ver`: **V** = I checked it against the tree this run; **T** = transcribed from the report (SECONDARY, not a test result). Classes are W36's: `DEF` / `DIS` / `DEC` / `MEA`.

#### Tier 1 — `systems/graph/` or an active manuscript

| # | Report:line | What it is | Target | Owner as stated | Blocked on | Rel. to W36 | Class | Ver |
|---|---|---|---|---|---|---|---|---|
| V01 | `W26b:169`, next action | `ST-PROXIMITY.limitations[0]` is FALSE, is labelled a load-bearing scoping error by `requirements.json:113`, and renders into **8 view files** — widest measured blast radius in the late set | `systems/graph/strategies.json:21` | graph owner | nothing | **COMPLEMENTS** U05 (`systems/graph/*.json`); new file, no overlap | DEF | **V** — `sed -n '19,22p'` still reads *"has no known ligand of any kind"* verbatim |
| V02 | `W26b` R.3/R.4, next action | Two FALSE/stale clauses that render into **zero** view lines, so `--check` stays green either way — *"they need a reviewer, not a gate"* | `systems/graph/modalities.json` | graph owner | a reviewer | complements V01; new target | DIS | T |
| V03 | `W06h:371`, `W06i:318` | Narrow the refuted independence sentence at `:80`, `:162` (2nd clause), `:256` (1st clause) | `research/manuscripts/emc-mortality-mechanisms-paper.md` | paper owner | nothing | new target | DIS | **V** — `:80` still reads *"the two methods share no input"* |
| V04 | `W06h:371`, `W06i:318` | Same narrowing | `research/IDEAS.md:166` | paper owner | nothing | new target | DIS | **V** — line matches |
| V05 | `W06i:318` | Same narrowing in the generator's `reading` string (**W06i corrects W06h's site to `:229`**) | `research/manuscripts/emc_relative_survival.py` | paper owner | nothing | new target | DIS | T |
| V06 | `W06i:318` | Two more sites W06h missed, then `--write-views` repairs all seven generated views in one pass | `systems/graph/publications.json:573`, `:579` | paper + graph owner | nothing | **COMPLEMENTS** U02/U02a/U03/U04 — same file, different fields; sequencing note, not a conflict | DIS | **V** — both lines carry the wording |
| V07 | `W06i` next action | Audit every other `PUB-*` `what_it_would_claim` for content superseded by later measurement — no drift check compares that field against the artifact it describes | `systems/graph/publications.json` | lane 6 successor | nothing | complements U02–U04 | DEF | T |
| V08 | `W31c:209`, second item | The `[D5]` load-bearing document carries `last_verified: unverified` and needs a human to read and stamp it honestly; the checker forbids clearing by bulk date | `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` | a human reader | judgement | **COMPLEMENTS with ordering** U13/U14 — same file; the stamp should follow their corrections, not precede them | DEC | T |
| V09 | `W31c:209` | Decide whether `modalities.parent` is a rule to instantiate or an entry to retire — a register of edges naming an edge **0 of 217** rows carry | `systems/graph/relations.json:404-411` | relations.json maintainer | one edit, either way | new target | DEC | **V** — `grep -c '"parent"' systems/graph/modalities.json` → **0** |
| V10 | `W14f:153-180` | `row4_pose_map_edits.py`'s 8 standing failures are a scientific question about the manuscript's text, belonging to the manuscript owner, not to a gate-wiring task | `research/manuscripts/nr4a3-program-map.md` | manuscript owner | scientific judgement | new target; downstream of the V13 conflict | DEC | **V** — reproduced, see Validation |

#### Tier 2 — protected shared state and the commit gate

| # | Report:line | What it is | Target | Owner | Blocked on | Rel. to W36 | Class | Ver |
|---|---|---|---|---|---|---|---|---|
| V11 | `W30b:297` | Add six §2.6/§2.7 generators to the *"generated deposit artifacts reproduce from their generators"* gate; five ran exit 0 in <1 s each, so *"green on arrival"* | `scripts/preflight.sh` | preflight owner | nothing (author says so) | **⛔ CONFLICTS with V12** | DEF | **V** — none of the six appears in `preflight.sh` |
| V12 | `W34:282`, "explicitly not recommended" | *"Explicitly not recommended as the next action: wiring any of the 85 into a runner … six of these would turn the gate red on the next commit. Diagnose first, wire second."* | `scripts/preflight.sh` (policy) | gate owner | the six diagnoses | **⛔ CONFLICTS with V11**; tension (not a formal pair) with U31/U32/U62/U67, which all propose commit-loop additions | DEC | T |
| V13 | `W14f` next action, `:153-180` | Wire **only seven** proven-failable rows; hold `emc_tissue_read_statistics` and `row4_pose_map_edits` back with the reason attached | `scripts/preflight.sh` | gate owner | the two held rows | **⛔ CONFLICTS with U31** (`W14e:390`: *"the nine … and only those nine"*) | DEF+DEC | **V** — see Validation V8 |
| V14 | `W14f` next action, `:135` | Smallest correct repair to `:425`: read `OUT`, compare to the computed `out`, return 1 on mismatch — the idiom the seven passing rows use — then re-run drift/truncate/delete | `research/modalities/emc_tissue_read_statistics.py:425` | module owner | nothing | new target; prerequisite to V13 | DEF | **V** (source read: `--check` returns before `open(OUT,"w")`) |
| V15 | `W29b:305` | Rows 16/17/18 get a **zero-test**, not a committed floor (47→3); the floor is a separate, larger change and must be argued on `lit_consensus_probe.py`'s calibration principle, not `single_slot_identity.py` | `scripts/preflight.sh` | gate owner | the choice | **⛔ CONFLICTS with U34** — W29b explicitly says *"correct W29's Next-action line before it is acted on"* | DEF+DEC | T |
| V16 | `W29c:294` | `:881-893` captures each row's stdout then discards it on success, so the denominators rows 16/17/18 compute never reach a reader; explicitly independent of the floor debate | `scripts/preflight.sh:881-893` | gate owner | nothing | new target; **complements** V15 | DEF | **V** — `gen_out` is unused on the `OK` branch |
| V17 | `W09h` next action, R.5 | Decide whether `--write-views` should run `check_schemas` before it writes. Measured: delete `outcome_potential_why` from all 33 records → `--write-views` exit 0 and 111 byte-identical views; plain run → exit 1 and 33 `[S3]` | `systems/systems_check.py` | graph owner | the tradeoff (regeneration would start failing on a tree with unrelated `[D4]`) | **COMPLEMENTS** U11/U12 — same file, different defect | DEC | T |
| V18 | `W29d` next action, `:157` | Disposition of `lint_changed_prose.py:114` — a preflight row (`preflight.sh:661`) that prints `OK` and exits 0 on a rev-range git exited 128 on; the repository's only dropped-qualifier instrument | `research/manuscripts/lint_changed_prose.py:114` | module owner | (i) below | DEF | **V** — `_git()` returns only `.stdout`; no `returncode` inspected |
| V19 | `W29d` next action (i) | Determine whether any tracked workflow or documented invocation passes a rev-range to it — *"I did not check `.github/workflows/`, so that is UNKNOWN"* | `.github/workflows/` | lane-29 successor | nothing | new | MEA | T |
| V20 | `W03g:236`, item 2 | Fetch `origin/literature-cache` on the machine that runs the chain, or the run still exits **3** at `:474` with the summary unprinted | chain host env | PUB-ASO owner | must land with V22 | complements U35/U36 | DEF | T |
| V21 | `W29b:305`, item 2 | `_literature_cache()` ignores `rc=128`; smallest repair is to inspect `r.returncode` and announce the degrade, per `tests.yml:174-177` | `research/manuscripts/submission_citations.py:303-306` | gate owner | nothing | **COMPLEMENTS** U36 — same file, different defect | DEF | **V** — `subprocess.run(...)`, `.stdout` consumed, rc discarded |

#### Tier 3 — generators, artifacts and tests

| # | Report:line | What it is | Target | Owner | Blocked on | Rel. to W36 | Class | Ver |
|---|---|---|---|---|---|---|---|---|
| V22 | `W03f:310`, `W03g:236` | Call `aso_archive_manifest.py --check-archive` for the check-command (keeping `--check` as the human pre-deposit step). Measured effect: step goes `current`, `fail` 1→0; cost: the chain stops asserting `git_revision` freshness. **"not made; it is the PUB-ASO owner's decision"** | `scripts/regenerate_aso_chain.sh:423` | PUB-ASO owner | the tradeoff | new target | DEC | **V** — `:423` still passes `--check` |
| V23 | `W03g:236` | Bounded scratch experiment before adopting V22: perturb one inventoried file, run `--check-archive`, expect exit 1 — *"does the swap keep the guard that matters or quietly disarm it?"* Not run | scratch experiment | lane-3 successor | nothing | new; gates V22 | MEA | T (**`W03h`, arrived after my pin, appears to answer this**) |
| V24 | `W03f:76`, `W34:282,:206` | The `CANNOT VOUCH FOR` list is wrong for **four** rows, not three: `:249, :264, :265, :297` — `submission_packet.py` joins W03e's three and its `--check` is already a preflight loop row. Zero test-function cost | `scripts/regenerate_aso_chain.sh:249,264,265,297` | ASO-chain owner | nothing | **EXTENDS U35** (which named only `:265` and W03e's three); the `:297` string is a genuinely new target line | DEF | **V** — all four still pass `""` as check-command |
| V25 | `W27b:132,175,189`, handoff | A **second writing `--check`**, not previously named in the gate census: `main()` writes `args.out` unconditionally at `:851-852` and prints `[canon] wrote …` before the check at `:873-876` refuses only on `n_DEAD_anchors` | `research/modalities/nr4a3_linker_library_canonical.py:851-852` | offered to W14e's lane | nothing | **COMPLEMENTS** the U31/W14e self-writing-`--check` axis and U37's `emc_fourth_cohort_quant.py:928` | DEF | **V** — `open(args.out,"w")` at `:851` precedes `if args.check…` at `:873` |
| V26 | `W27b` next action | Option 1 on the **11 Class A modules** first — 0 test functions, no tier budget, the idiom **90 siblings** already use; start `realised_spend.py:437-439`, then `nr4a3_fusion_targets.py:2064-2065` | 11 named modules | *"the owner, not another audit worker"* | nothing | **EXTENDS U67/U68** — delivers the census input U68 was blocked on and grows the target set 10 → 33 (39 with Class F). Not a duplicate item; same change-shape, new targets | DEF | T |
| V27 | `W16h:289` (a) | Whether the `BASE` pin should point at a reachable mainline commit — all six pinned blobs are byte-identical to the tree today, so the change converts a silent-staleness surface into a live one | `research/modalities/expression_validation_readiness.py:18` | module owner | which-side-is-stale decision | **COMPLEMENTS** U51 (same drift cluster); W16h endorses W16f's *"a guard red at commit time is a broken gate"* | DEC | **V** — `git cat-file -e 8c1f2925…` → **exit 1** (object absent) |
| V28 | `W16h:289` (b), `:144` | Whether `preflight` should restore the bundle so the check is runnable, *"or whether a check that cannot run is worse than no check"* — recoverable offline via the `restore_command` in `source-history.json` | `scripts/preflight.sh` + that module | module owner | (a) | new | DEC | T |
| V29 | `W16g:251` | Diagnose whether `BASE` names a commit that ever existed; with `--check` runnable the cluster count becomes *exactly* 7 or 8 | same module | module owner | — | **RESOLVED inside the late set by W16h** (answer: unmerged, unpushed local branch tip; recoverable; passes once recovered) | MEA | **V** (object absent, consistent with both) |
| V30 | `W30b:299` | Make `pool_reconstructions` raise on an overlapping population the way it already raises on a mixed endpoint (F4) | reconstruction instrument | *"whoever owns the reconstruction instrument"* | nothing | new | DEF | T |
| V31 | `W30b:299` | One-line cross-reference to `systems/POLICY-evidence.md` §2.7(a) in `no-wet-lab-publication-archetypes.md` §6.1, so its correct method statement cannot be read as licence | `no-wet-lab-publication-archetypes.md` §6.1 | policy owner | nothing | new | DIS | T |
| V32 | `W28b` next action | Add `retired_by` to `realised_spend_omitted_the_selcal_lane` and `current`+`retired_by` to `aso_thermo_cross_margin_discordance` — or move the latter to `artifact_figures[]` — then re-run `lint_consistency.py`. Closes a **confirmed unhandled `KeyError` crash reproduced live against the real linter**, 2 of 81 entries, no manuscript judgement | `research/manuscripts/pinned-figures.json` | pinned-figures owner | the add-vs-move choice | **COMPLEMENTS** U15/U16/U17 (same file, different clauses — a fourth edit in that pass) and U18 (`lint_consistency.py` is its verifier) | DEF+DEC | **V** — `superseded[]` entry 1 has keys `[current,id,pattern]`, entry 2 `[artifact,id,note,pattern]`; **neither has `retired_by`** |
| V33 | `W28b` R.1 #2/#3/#4 | The `best estimate is **$…**` construction fails in **three separate guards** — *"the single highest-yield pattern repair"* | same file (patterns) | pinned-figures owner | judgement | complements V32 | DEF | T |
| V34 | `W28b` R.1 #4 | `$126.17` is currently **both a current and a retired figure inside the same registry** | same file | pinned-figures owner | judgement | complements V32 | DIS | T |
| V35 | `W18c` next action | If W18/W18b/W18c code is integrated, commit W18's D0 script and seed — *"the single artifact three workers could not reproduce bit-for-bit"* | lane-18 code | integrator | integration decision | new; **W18c otherwise CLOSES U101's open question** (the bound's width is irreducible from the data at EMC n) — a net reduction, not an addition | DEF | T |
| V36 | `W37` next action, I2b | Run the I2b experiment against `systems_check.py` — empty the fifteen `systems/graph/` collections, `--write-views`, then `--check` — in a scratch copy whose baseline is first established rc=0 | `systems/systems_check.py` | lane-37 | a `.git`-bearing copy | complements V17 | MEA | T |
| V37 | `W37:294` | `systems_check --check` rc=1 with **179 errors** in a scratch copy, sampled as broken relative links inside the campaign's own `inputs/`. *"I did not run it live and it is UNKNOWN."* | `systems/systems_check.py` + campaign `inputs/` | systems_check owner | a live run | **COMPLEMENTS** V38 and the brief's *"Known, measured"* note (which already states the 9 `inputs/` errors are real findings) | DEF | T — **and expressly UNKNOWN live** |
| V38 | `W29c` next action 1 | Run exactly three named tests against three degenerate states and record exit codes — `test_glue_watch_row.py` and `test_trigger_board_filter.py` against `triggers: []`, `test_the_deposit_the_papers_cite_is_current.py` against the UNKNOWN deposit-drift block. *"No worker has been able to run `pytest`, so every 'a test compensates' claim in W29/W29b/W29c is a source reading."* | `research/…/tests/` | gate owner | pytest availability | new | MEA | T (**`W29f`, arrived after my pin, is titled "pytest-availability-contradiction"**) |

#### Tier 4 — corrections whose only reader is the campaign's own artifacts

| # | Report:line | What it is | Target | Owner | Rel. to W36 | Class | Ver |
|---|---|---|---|---|---|---|---|
| V39 | `W24d` next action | Row 139(b) must stop crediting R08 with the D3 *capability* (both patches have it, executed on both); row 137's *"two drift legs D1/D2"* for R07 becomes *"all three drift classes, executed by W24d"* | `reports/W24-repair-routing-index.md` | coordinator | **⛔ CONFLICTS with U38** — U38 is built on W24c's record, which W24d measured false in the verbatim form | DIS | T |
| V40 | `W24d:112-150` | New row the index does not carry: **R07's diff is not machine-applicable without a two-line file header, and R08's is not machine-applicable at all**; the applier must expect to reconstruct the patch rather than pipe it into `git apply`, and R08 needs its rebuild diffed against W14d's intent before landing. *"That packaging fact, not capability, is now the sharpest practical difference."* Plus: **no further read-only worker should be sent at this file** — four have converged | same, and U37's decision | coordinator / owner | sharpens U37 with a new axis | DIS | T |
| V41 | `W33` next action | One coordinator write applying **nine restatements** to `CLOSED-WORK.md`, C12/C14/C19 first: C12/C20 tell every worker two input directories are "pending" when they have been readable since ~02:30Z; **C14 has already propagated "denied" onto a verified primary in at least five reports**; C19 restores a dropped ban on sparse-input repository-wide absence claims. No retrieval, no network, no reopening | `CLOSED-WORK.md` | coordinator | **COMPLEMENTS** U76/U77 — W33 says it should ship in the same pass, and that this document is upstream of them | DIS | T |
| V42 | `W38` next action | Annotate 14 flagged citations with a tree qualifier (10 corpus-only, 1 line-count mismatch, 2 unresolvable path forms) **plus** the 4 SILENT-DIVERGENCE citations with the opposite qualifier. File, line, path and direction for all 18 already tabulated | campaign reports + `WAVE-LOG.md` | coordinator | **COMPLEMENTS** U75/U76/U77 — same annotation pass | DIS | T |
| V43 | `W18c` next action | Record in the campaign synthesis the closed three-step negative result and mark lane 18 closed with the code preserved | `W23-cross-output-synthesis-packet.md` | coordinator | new | DIS | T |
| V44 | `W29b` next action | Restate the *"5 of 18"* vacuous-pass figure as **4 of 18** wherever the campaign has propagated it — row 3 is refuted by execution | campaign artifacts | coordinator | complements V15 | DIS | T |
| V45 | `W31b` next action | Choose one of three honest exits for the report-frontmatter policy and **record the decision**: (a) collector emits real frontmatter (count falls to 22), (b) declare the directory machinery and write the policy down (a `DOC_SKIP` question that would also stop checking `inputs/`), or (c) accept it as campaign noise **and state that in `COMMON-BRIEF.md`**. Explicitly refuses to recommend an exclusion | campaign policy | coordinator | **partially landed** — the brief's *"Known, measured"* section now carries exit (c)'s measurement | DEC | **V** — brief carries it |
| V46 | `W35` next action | Coordinator edits `COMMON-BRIEF.md:7-8` and inserts one line into `CORPUS-CONTEXT.md` after line 15 | brief + corpus context | coordinator | **LANDED** | DIS | **V** — both texts present |
| V47 | `W35` next action | Ranks 2, 4, 5, 6 — single-line annotations that can follow in the same commit but do not gate dispatch | same | coordinator | open residual of V46 | DIS | T |
| V48 | `W35b` next action | Append the *reason* the stale pin was harmless, so nobody assumes it stays harmless | `COMMON-BRIEF.md` §1 | coordinator | **LANDED** | DIS | **V** — verbatim, including *"39 pin-anchored reports lose it silently"* |

#### Tier 5 — measurement and retrieval requests

| # | Report:line | What it is | Owner | Blocker | Rel. to W36 | Class |
|---|---|---|---|---|---|---|
| V49 | `W34` next action | Diagnose the six reds in rank order — `emc_mtap_prmt5_figures.py --check` in a `.git`-bearing tree, per DRIFT line, then `emc_mtap_locus_persample.py` and `emc_prmt5_multiplicity.py` (same `per_platform` key, plausibly one cause / three symptoms), plus `cd248_precedent.py` alongside `alcam_precedent.py`. *"Expect the honest answer to be that an artifact needs regenerating; the fix is the drift, never the guard."* | module owners | a `.git` tree | new; gates V12 | MEA |
| V50 | `W03f` next action | Run `bash scripts/regenerate_aso_chain.sh --check` once in a real `.git` checkout to confirm R4's prediction (`archive manifest STALE`, exit 1) | PUB-ASO owner | a `.git` checkout | gates V22/V24 | MEA |
| V51 | `W01i` next action | Read two **local frozen-corpus** articles (`brenca-article.xml`, `urbini-article.xml`) for rows 8/7 — library-prep and platform sentences — *"not retrieval"*; holding row 8 at 12 specimens, no patient or library-to-specimen inference, and **no article text can supply the measured gene space D4 demands** | lane 1 | nothing (offline) | **COMPLEMENTS** U85 | MEA |
| V52 | `W01i` next action | *"This campaign should buy nothing further: 78 of the 90-specimen spread is closed by choosing a definition, not by spending retrieval budget, and that choice is the lane owner's to make."* Rows 1,3,6,7,9,10,12 have **zero** marginal value once row 8 is done | lane owner | the definition choice | new; a **refusal to spend**, i.e. a reduction of U89–U100's pressure | DEC |
| V53 | `W02i` next action | Run the identical six-row arm-to-arm rule on the **two marker sets W02d retired** (immune k=12, tumour k=9) as a specificity control on the rule itself — *"the only remaining test I can name that could falsify the lane's surviving claim rather than decorate it."* ~4 s, same loader, fully pre-declarable | lane 2 | nothing | **COMPLEMENTS** U91; W02i then declares lane 2 out of questions on this substrate | MEA |

---

### B. The measured answers to W36's estimate

| Quantity | W36's estimate (over the 7 report names it had) | **Measured (over the 27 that actually arrived)** |
|---|---|---|
| Late reports | 7 | **27** (+1 modified) |
| Further routed items | "roughly four to seven" | **53** |
| New conflicts | "at least one" | **4 new conflicting pairs**, plus 1 correction-pair |

**W36's estimate was directionally right and an order of magnitude low, and the reason is the denominator, not the rate.** Its own per-report rate at `215ed8e7` was 102 items / 149 indexed reports ≈ **0.68 items per report**. My measured rate over the late set is 53 / 27 ≈ **1.96 items per report** — nearly 3× higher. The late cohort is denser because it is disproportionately made of *successor* reports (`W03f/g`, `W06h/i`, `W16g/h`, `W24d`, `W27b`, `W29b/c/d`, `W31b/c`, `W34`, `W35/b`) whose whole unit was to price or narrow an already-routed decision — and pricing a decision produces a routed item, not a landed one.

**Totals, folding into W36's:**

| | W36 @ `215ed8e7` | + late set | **combined** |
|---|---|---|---|
| Routed items | 102 | +53 | **155** |
| …of which landed/resolved | (W17d's refusal) | **3** (V46, V48 landed; V29 answered by W16h) | |
| **Net open** | 102 | +50 | **~152** |
| Conflicting pairs | 16 | **+4** | **20** |
| Distinct targets | 51 | +~20 new files/paths | ~71 |
| Class split (late set) | — | DEF 17 · DIS 15 · DEC 11 · MEA 10 | |

**The 4 new conflicting pairs:**

| Pair | Target | The disagreement, in the reports' own words |
|---|---|---|
| **W14f × W14e (U31)** | `scripts/preflight.sh` | *"Wire the nine … and only those nine"* (`W14e:390`) vs *"Wire only the seven proven-failable rows … do not add `emc_tissue_read_statistics` or `row4_pose_map_edits` yet"*. **Grounded in measurement I reproduced independently.** |
| **W24d × W24c (U38)** | `emc_fourth_cohort_quant.py` / `W24-repair-routing-index.md` | W24c's transcribed *"`git apply --check` and `git apply` both exit 0, no fuzz, no rejection, no hunk offset"* is **true of the headed form and false of the verbatim form** — verbatim R07 gives `error: patch fragment without header at line 1`, `EXIT=128`. |
| **W29b × W29 (U34)** | `scripts/preflight.sh` | *"Rows 16, 17, 18 get a zero-test, not a floor … a committed floor (47 → 3) is a separate, larger change and should be argued separately"* — W29b explicitly directs that W29's Next-action line be corrected before it is acted on. |
| **W30b × W34** | `scripts/preflight.sh` (policy) | *"Add the six §2.6/§2.7 generators … the rows are green on arrival and cost is negligible"* vs *"Explicitly not recommended as the next action: wiring any of the 85 into a runner … six of these would turn the gate red on the next commit. Diagnose first, wire second."* The two module sets are disjoint, so this may be reconcilable — but as written they state opposing gate policy and must not both be acted on unread. |

**One correction-pair, flagged but not counted as a conflict:** **W06i corrects W06h.** W06h routes 5 edit sites including two *generated* files (`systems/views/L2-rt-competing-mortality.md:80`, `emc-relative-survival.json:210`); W06i measures **seven source sites** and adds `publications.json:573`/`:579`, which W06h missed entirely. A lander acting on W06h alone would edit a generated file directly and leave two graph fields stale. This is a refinement in the same direction, not a contradiction — but it is load-bearing.

**Three genuine reductions in the late set** (the input W36 asked for to sharpen its growth-versus-resolution finding, which I am not re-deriving): W35 and W35b's brief corrections **landed** (verified in the live brief); W16h **answered** W16g's diagnosis (`BASE` = an unmerged, unpushed local branch tip, recoverable offline, and it passes once recovered), converting a measurement request into two owner decisions; and W18c **closed** the question behind U101 by measuring that the bound's width is irreducible at EMC sample sizes, refusing a fourth variant. Against 50 net additions, that is 3.

**One index-maintenance fact for W36b:** `W14e-fake-guard-triage.md` was **modified** after `215ed8e7` — a collector-header rewrite only (3 insertions, 5 deletions, all inside the leading HTML comment), no body change. It shifted every line number in that file by **−2**. W36's U31 anchor `W14e:392` now lands on `---`; the sentence it cites is at **`W14e:390`**. No other indexed report was modified.

---

## Validation evidence

All `RUN` unless marked. Environment: `/home/user/Rare-cancers`, branch `claude/confident-bardeen-ji76cd`, HEAD `606d79f9` → `e5d60db7` → `cfc5f3dc` (moved 3× under me), `python3` as installed, no network. Every module below was **read in source first** to confirm its check path writes nothing; `git status --porcelain` was empty before and after.

| # | Command | Exit | What it establishes | Row |
|---|---|---|---|---|
| V-a | `git diff --name-only --diff-filter=A 215ed8e7 HEAD -- reports/` | 0 | the 28-file pinned set; identical when re-run at `e5d60db7` | Method |
| V-b | `git ls-tree -r --name-only 215ed8e7 -- reports/ \| wc -l` → `150` | 0 | W36's pin confirmed exactly | Method |
| V-c | `git diff --name-only --diff-filter=D 215ed8e7 HEAD` → empty | 0 | nothing deleted; the set is purely additive | Method |
| V-d | `grep -c '"parent"' systems/graph/modalities.json` → **0** | 1 | `modalities.parent` is declared by `relations.json:404-411` and carried by 0 of 217 rows | V09 |
| V-e | `sed -n '19,22p' systems/graph/strategies.json` | 0 | `ST-PROXIMITY.limitations[0]` is present verbatim and unlanded | V01 |
| V-f | `git cat-file -e 8c1f292536b7d725186491b42c19c87c0b6c855c` | **1** | the pinned `BASE` object is **absent from this clone** — W16g's premise and W16h's answer are both consistent with it | V27/V29 |
| V-g | `json.load` on `pinned-figures.json`, key sets of the two `superseded[]` entries → `[current,id,pattern]` and `[artifact,id,note,pattern]` | 0 | **neither carries `retired_by`**; W28b's change is unlanded | V32 |
| V-h | `sed -n '80p' emc-mortality-mechanisms-paper.md`; `grep -n 'shar\(e\|ing\) no input' … publications.json` | 0 | `:80` and `publications.json:573,:579` still carry the refuted wording | V03/V06 |
| V-i | `sed -n '112,116p' research/manuscripts/lint_changed_prose.py` | 0 | `_git()` returns only `.stdout`; no `returncode` inspected | V18 |
| V-j | `sed -n '249p;264p;265p;297p;423p' scripts/regenerate_aso_chain.sh` | 0 | all four rows pass `""` as check-command; `:423` still passes `--check` | V22/V24 |
| V-k | source read `nr4a3_linker_library_canonical.py:845-880` | 0 | `open(args.out,"w")` at `:851` executes before `if args.check…` at `:873`; `print("[canon] wrote %s")` at `:871` | V25 |
| V-l | source read `submission_citations.py:300-308`; `preflight.sh:881-893`; `grep -n endpoint_corpus\|orr_dcr_reread\|placebo_arm_calibration\|endpoint_regime_map\|emc_ipd_survival\|km_digitize scripts/preflight.sh` → **no output** | 0 / 1 | rc discarded; `gen_out` unused on the `OK` branch; **none of W30b's six generators is wired** | V21/V16/V11 |
| **V-m** | **`python3 research/manuscripts/row4_pose_map_edits.py --verify`** — source read first (`verify()` at `:371` opens files read-mode, shells `git show`, prints, returns; `main():393` raises `SystemExit(verify())` **before** `open(OUT,"w")` at `:409`) | **1** | **REPRODUCED at HEAD `e5d60db7`:** `FAIL P1–P4 × {origin/main, WORKTREE}`, `OK P5–P7 × 2`, `7 edits × 2 refs — 8 failure(s)`. `git status --porcelain` empty after. **W14f's Finding 2 is PRIMARY and independently confirmed: the row is red at baseline on the live tree.** | V13/V10 |
| V-n | `grep -c` on `COMMON-BRIEF.md` / `CORPUS-CONTEXT.md` for W35's and W35b's replacement texts → 2 and 1 | 0 | V46 and V48 have **landed** | V46/V48 |

`PROPOSED (NOT RUN)` — everything in Tier 5, V23, V36, V38, V49, V50, plus every row marked `T`. **A worker report is not a test result**: all `T` rows are SECONDARY.

---

## Limitations

- **My totals depend on W36's counting rule**, which I applied deliberately unchanged so the two indexes add. A per-hunk or per-report rule gives a different number. Where one change spans several files (V03–V06) I counted one item per target file, as W36 did for U15/U16/U17.
- **38 of my 53 rows are `T` (transcribed, SECONDARY).** I verified 13 checks covering ~15 rows. The rest are the reports' own words, not measurements I made.
- **The report directory grew from 178 to 187 while I worked.** Nine reports (`W03h, W26c, W27c, W28c, W29e, W29f, W30c, W34b, W39`) arrived after my pin `e5d60db7` and are **UNKNOWN to this index**. Their titles suggest at least three answer items I list as open (V23, V38, V49) and that `W39` is itself a contradiction census — so my "4 new conflicts" is a floor over my pinned set, not over the live directory.
- **I did not re-verify any of W36's U01–U102**, so every "CONFLICTS with U*n*" claim inherits W36's transcription of that row. The `W14e:392` → `:390` anchor drift I found is one demonstrated instance of that inheritance being imperfect. W36b owns that verification.
- **I did not adjudicate anything.** The W30b × W34 pair in particular may be reconcilable on inspection (disjoint module sets); I recorded the disagreement as the reports state it and stopped.
- No claim here touches EMC efficacy, safety, selectivity, therapeutic window or clinical readiness. Nothing here is a scientific result; it is an inventory of routing.
- One reading is expressly UNKNOWN and I left it so: W37's 179 `systems_check` errors were measured in a **scratch copy without `.git`** and W37 says it did not run live. Per the brief, that baseline is dominated by this campaign's own footprint and changes between any two sessions.

---

## Stop condition

**Set up front:** return the moment (a) the set of reports added after `215ed8e7` is determined by `git diff`/`git log` and stated, (b) every routed-but-unlanded item in that set is enumerated under W36's counting rule with report:line, target, owner, blocker, class and its CONFLICTS/COMPLEMENTS relation to an existing U-row, (c) the item count and new-conflict count are reported as measurements against W36's estimate, (d) a handful of rows are tree-verified and the rest honestly marked `T`, and (e) the scratch directory is deleted — at roughly 40 tool calls / 40 minutes, without performing, adjudicating, sequencing or deciding any item.

**MET.** 27 reports indexed, 53 items (V01–V53), 4 new conflicting pairs plus 1 correction-pair, 13 verification checks including one full independent reproduction, 3 reductions identified, scratch deleted, tree clean.

---

## Tool-call and wall-clock count actually used

**23 tool calls**, `03:46:54Z → 03:51:50Z` = **4 min 56 s**. Well inside the ~40/~40 target; returning immediately rather than padding.

---

## Next concrete action

**One successor, and it is the same unit again on a set that is now known:** index the **nine reports that arrived after `e5d60db7`** — `W03h, W26c, W27c, W28c, W29e, W29f, W30c, W34b, W39` — under the same counting rule, and fold them into Tiers 1–5 as V54+. Three of them plausibly *close* items I opened (`W03h` → V23's `--check-archive` discrimination experiment; `W29f` → V38's pytest availability; `W34b` → V49's six reds), so this successor is the first in the chain with a real chance of recording **net reduction**, and `W39` should be read first because a cross-report contradiction census may already name conflicts I derived independently. It needs no retrieval, no network and no authority.

**A second, smaller item for the coordinator, not a worker:** the collector's header rewrite on `W14e-fake-guard-triage.md` silently shifted that file's line numbers by −2 and invalidated `W36:U31`'s anchor. If the collector rewrites headers on already-collected reports as a matter of course, **every `report:line` anchor in W24's, W36's and this index degrades silently.** Freezing the header at collection time, or recording the header line-count in the index, is a bookkeeping decision worth one minute of the coordinator's attention — I am not proposing the change.
