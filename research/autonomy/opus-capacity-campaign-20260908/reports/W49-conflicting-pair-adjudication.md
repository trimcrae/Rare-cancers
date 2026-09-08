<!-- collected 2026-09-08T04:49:12Z by campaign coordinator; agent id ac3b313c1682f9460; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ac3b313c1682f9460.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Scratch deleted; HEAD drift touched only campaign-directory files. Report follows.

## Worker

**W49**, conflict-adjudication lane, OPUS-CAPACITY-CAMPAIGN-20260908. Read-only. I landed, applied, patched and repaired nothing; I authored no code, no gate, no test.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. I did not observe the served model. No environment variable names a model. Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (identical at start; the five long proxy-exclusion variables that match only on the substring `anthropic` — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy` — are elided as marked; everything else verbatim):

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

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep 8 04:40:10 UTC 2026` | `Tue Sep 8 04:44:06 UTC 2026` |
| `git rev-parse HEAD` | `408b676aec3625a36917755662516232a27a1278` | `fb1a3f8040537234010114053b36ec55b729c65e` |
| `git status --porcelain` | clean (0 lines) | clean (0 lines) |

**HEAD moved under me, and I verified it did not disturb any measurement.** `git diff --name-only 408b676a fb1a3f80` → **9 files, all inside `research/autonomy/opus-capacity-campaign-20260908/`**; the same diff filtered with `grep -v opus-capacity-campaign-20260908` → **0 files**. Every value I measured is in `scripts/`, `systems/graph/`, `systems/views/` or `research/modalities/`, none of which changed. I re-ran `tier_budget.py --check` and the two greps at the end HEAD and got byte-identical results (see Validation).

---

## Question

**For each of the 20 conflicting pairs indexed by W36 (16) and W36c (4), what does the repository tree actually show, and which side is right?** Open because both index reports state explicitly that they do not adjudicate: W36 is an "advisory index only … adjudicated no ruling"; W36c "did not re-verify any of W36's U01–U102" and inherits every `CONFLICTS with U*n*` claim from W36's transcription. No worker has measured whether the conflicts are real.

---

## Prior-work check

Read in full: `COMMON-BRIEF.md` (146 lines, both corrections present), `CORPUS-CONTEXT.md` (82), `CLOSED-WORK.md` (70), and the three index reports (`W36` 366 lines, `W36b` 298, `W36c` 303). Conflict tables at `W36:239-253` and `W36c:231-241`.

Confirmed I am **not replaying**: the 0-of-89 resolution rate (closed, `COMMON-BRIEF.md` "Known, measured"); the `origin/literature-cache` non-incident (W40 — I touched it only to confirm `submission_citations.py:304` still ignores its return code, which W29b routed and I did not re-derive); the pytest-interpreter trap (W29f — I ran no pytest); W36b's backlog verification. I read no `W25-*` report. I ran no `preflight.sh` and never invoked `atr_hrd_sarcoma_series.py`. Before running `scripts/tier_budget.py --check` I read `main()` at `scripts/tier_budget.py:130-160` and confirmed it only `print`s and returns an exit code — **no `open(...,"w")`, no `json.dump` to a file, no write of any kind**.

Source-index items (pairs 13–14) touch **lane 11's exclusive ownership** (`CLOSED-WORK.md`). I adjudicated the *reports' claims against the tree* and authored nothing; I did not open the source-index bundle or re-review its 9 static findings.

---

## Method and inputs

Live checkout `/home/user/Rare-cancers` only (not the frozen corpus — every citation here is a `:NN` written from the live tree, which `CORPUS-CONTEXT.md`'s W38b correction says must be resolved live). Files measured: `scripts/preflight.sh`, `scripts/tier_budget.py`, `scripts/tier-budgets.json`, `research/modalities/emc_fourth_cohort_quant.py`, `research/modalities/emc_tissue_read_statistics.py`, `research/manuscripts/submission_citations.py`, `systems/graph/publications.json`, `systems/views/*.md`, `research/modalities/tests/`. Reports read for verbatim claims: W09d, W09e, W11b, W11d, W12b, W12c, W12d, W13g, W14c, W14d, W14e, W14f, W17f, W17h, W17i, W23, W24b, W24c, W24d, W27, W29, W29b, W30b, W34, W34b. All execution in `/tmp/claude-0/w49/` (deleted).

---

## Result

### Measurement 0 — the pair count is 19, not 20 `PRIMARY`

W36's own table at `:241-251` sums to **15** pairs (2 + 3 + 2 + 5 + 2 + 1), not the 16 its summary row at `:239` states. W36c added 4 to the stated 16 to reach 20. Adjudicating the table as written gives **19 enumerable pairs**. The 16th W36 pair is not enumerated anywhere in W36 and I could not recover it. `UNKNOWN` — it may be a summing error or an omitted row.

### Measurement 1 — tier facts that decide six of the pairs `PRIMARY`

```
$ python3 scripts/tier_budget.py --check
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
EXIT=0
```

`scripts/tier-budgets.json` defines: `commit-loop` = `['scripts/tests', 'research/autonomy/tests', 'systems/tests']`; `modalities` = `['research/modalities/tests']`; `paper-guards` = `['research/manuscripts/tests']`.

**`research/modalities/tests/` is the `modalities` tier and is NOT `commit-loop`.** W27's hold is textually and only about `commit-loop` (`W27:352`: *"placing any new test in `commit-loop` before Option 1 is done"*), and W27's own Option-3 row (`W27:246`) says a modalities placement *"would go to **`modalities`** (7247/7500, headroom **253**) … Affordable in the right tier."*

**W27's stated headroom no longer matches the tree.** W27 argues from *"1497/1500 measured on the real writer … the three remaining slots"*. At this HEAD `commit-loop` is **1466/1500 — headroom 34, not 3**. That is an 11-fold difference in the quantity W27's hold rests on.

---

### The 19 pairs, adjudicated

**Target: `research/modalities/emc_fourth_cohort_quant.py`**

| # | Pair | A's claim (verbatim, sourced) | B's claim (verbatim, sourced) | What the tree shows | Verdict |
|---|---|---|---|---|---|
| 1 | **R07 × R08** | W14c's R07 rewrites `_write_probe_tsv` into `_probe_tsv_body_impl` (`W14c:271` diff opens `@@ -567,7 +567,7 @@`) | W14d's R08 adds a `write=` kwarg and off-disk sha (`W14d:208-232`, hunks `@@ -570`, `@@ -589,593`, `@@ -817`, `@@ -830,831`) | Every contested line is exactly where W24b says. `emc_fourth_cohort_quant.py:817` = `body = _write_probe_tsv(cache, p2g)`; `:830-831` = the gene-TSV write; `:933-943` = the `--check` branch; `:570` = `def _write_probe_tsv`. Drift tuple at `:933-935` contains `gene_counts_sha256` and **not** `probe_counts_sha256` (which exists only at `:819`), so D3 drift is undetected today. **Neither patch is present.** | **UNRESOLVABLE-WITHOUT-A-DECISION-THE-OWNER-MUST-MAKE.** W24b's mechanism is verified against the live file: both rewrite `:933-943`; R08's context at `:817` ceases to exist once R07 lands; their trigger condition is identical. Whichever lands second cannot apply. This is a genuine forced design choice, not a sequencing artefact. |
| 2 | **C3 × R07** | W20g's C3 touches `:586` only | R07 rewrites `:586-593` as a block move | `:584-594` is one `lines.append(...)` construction block; `:586` is `g = (gene_of or {}).get(pr) or "unassigned"` inside it — a single expression R07 relocates but does not alter | **BOTH-PARTIALLY-CORRECT-ON-DIFFERENT-SCOPES.** W24b:241-247 is right that this is textual/ordering, not semantic: *"C3 conflicts textually with R07's hunk and not with R08's."* Resolvable by ordering (C3 after R07/R08); no owner design decision needed beyond pair 1. |
| 18 | **W24d × W24c** | W24c:27-28: *"`git apply --check` and `git apply` both exit 0, no fuzz, no rejection, no hunk offset"* | W24d:119-120: verbatim R07 gives `error: patch fragment without header at line 1: @@ -567,7 +567,7 @@`, `EXIT=128` | **Independently reproduced by inspection**: `W14c:270-272` shows the fence opening directly on `@@ -567,7 +567,7 @@` with **no `--- a/` / `+++ b/` header**. `git apply` cannot consume that. Separately, `grep -n "@@" W14d` returns abbreviated non-standard headers (`@@ -570 (def _write_probe_tsv)`, `@@ -589,593`) — R08 is not machine-applicable at all. | **B-CORRECT (W24d).** W24c's statement is true of a *headed* form and false of the published bytes. W24d's own framing is the honest one: *"a packaging defect in the report, not in the repair."* |

**Target: `scripts/preflight.sh` (locale)** — measured: `grep -c "PYTHONUTF8" scripts/preflight.sh` → **0**; `grep -c "PYTHONIOENCODING"` → **0**. Nothing landed.

I measured the CPython semantics the three-way turns on, rather than adjudicating from report text (Python 3.11.15, `LC_ALL=C LANG=C`, `-X utf8=0` to defeat PEP 540 auto-coercion):

| config | `sys.stdout.encoding` | `open()` of a UTF-8 file | `print()` of `— ⚠` |
|---|---|---|---|
| `PYTHONUTF8=0` (baseline) | `ascii` | **UnicodeDecodeError** | **UnicodeEncodeError** |
| `PYTHONUTF8=0 PYTHONIOENCODING=utf-8` | `utf-8` | **UnicodeDecodeError** | OK |
| UTF-8 mode on (`utf8mode=1`) | `utf-8` | OK | OK |

| # | Pair | Verdict |
|---|---|---|
| 3 | **W12b × W12c** | **B-CORRECT (W12c), on the gate scope.** W12b's five-module `sys.stdout.reconfigure` fix is measured by W12c to leave *"1,008 of 1,031 sites, and 14 of the 16 affected preflight gate rows, unrepaired"*, and W12b's own table (`W12b:154-158`) shows three of its five modules `STILL BROKEN` on the write path after its own patch. W12c does not contradict W12b — it states W12b's fix is *"correct and insufficient."* |
| 4 | **W12b × W12d** | **B-CORRECT (W12d).** Same reason, stronger: `PYTHONUTF8=1` is the only candidate my table shows repairing **both** the stdio side and the `open()` side. |
| 5 | **W12c × W12d** | **BOTH-PARTIALLY-CORRECT-ON-DIFFERENT-SCOPES, with W12d dominant on the gate.** `PYTHONIOENCODING=utf-8` repairs `print()` only and leaves `open()` broken — measured above — so on the 18-row gate `PYTHONUTF8=1` strictly dominates it. **W12d's stated objection does not land on W12c's actual proposal**: W12d's `⛔` warns against `PYTHONIOENCODING=...:replace` converting *"a crash into a mangled green"*; W12c proposed the **strict** `PYTHONIOENCODING=utf-8` with no error handler, and attached the same `errors="replace"` objection to its own second candidate. W12c's *source* form is genuinely out of W12d's reach — it is the only one covering direct invocation outside preflight. **W12c itself says: *"The two are complementary, not alternatives. Owner's call; I am not making it."*** The residual is one owner choice about scope (gate-only vs. direct-invocation-too), not a factual dispute. |

**Target: `research/modalities/tests/` (W17 cluster)** — measured: `ls research/modalities/tests/ | grep -E "committed_welch|committed_statistical"` → **no matches, exit 1**. None of the three modules exists. Headroom 253.

| # | Pair | Verdict |
|---|---|---|
| 6 | **W17i × W17f** | **BOTH-PARTIALLY-CORRECT-ON-DIFFERENT-SCOPES.** W17i (`next action`) says *"Land nothing new; consolidate … three separate files asserting the same four tests with three different input-error propagations"* and asks for one merged module at ≤20 test functions. W17f asks to land `test_committed_welch_blocks_invert_to_their_own_rows.py` verbatim (8 functions, `7247 → 7255`). **This is not a budget conflict** — 253 functions of modalities headroom absorb all three several times over — so W17i's argument stands or falls entirely on *duplication*, which is a design judgement, not an arithmetic one. W17f's module is delivered and self-reports a real pytest run; W17i's merged module does not exist. |
| 7 | **W17i × W17h** | **Same verdict, same reasoning.** W17h's `test_committed_welch_blocks_in_the_uncovered_artifacts.py` (`W17h:188`) is likewise absent and likewise affordable. |

**Target: gate-row additions vs W27's hold** — the decisive fact is Measurement 1.

| # | Pair | Verdict |
|---|---|---|
| 8 | **W27 × W17f** | **NOT A CONFLICT — A-and-B are about different tiers. Verdict: BOTH-CORRECT-ON-DIFFERENT-SCOPES.** W27's hold names `commit-loop`; `research/modalities/tests/` is `modalities` by `scripts/tier-budgets.json`. W27's own `:246` prices a modalities placement as *"affordable in the right tier."* W36's pairing is a scope error. |
| 9 | **W27 × W17h** | **Same. BOTH-CORRECT-ON-DIFFERENT-SCOPES** — scope error in the index. |
| 10 | **W27 × W17i** | **Same. BOTH-CORRECT-ON-DIFFERENT-SCOPES** — scope error in the index. |
| 11 | **W27 × W14e (U31)** | **NOT A CONFLICT. BOTH-CORRECT-ON-DIFFERENT-SCOPES.** U31 adds `--check` rows to the shell loop at `scripts/preflight.sh:847-864`, which consumes **zero** test functions in any tier; W27's hold is a test-function budget argument. |
| 12 | **W27 × W13g (U28)** | **NOT A CONFLICT. BOTH-CORRECT-ON-DIFFERENT-SCOPES**, and W13g says so itself: `W13g:262` — *"It costs **0 test functions against every tier ceiling**"*, adding a 19th entry *"to the loop at `scripts/preflight.sh:847–864`"*. Verified: the loop at `:847-864` currently carries exactly **18 rows**, and `grep -c` for W13g's module → **0**. |

**Target: source-index placement**

| # | Pair | Verdict |
|---|---|---|
| 13 | **W11d × W11b** | **NOT A CONFLICT; the arithmetic agrees exactly. BOTH-PARTIALLY-CORRECT-ON-DIFFERENT-SCOPES.** W11b proposes `scripts/tests/test_source_reuse_index.py` (18 functions) and predicts *"1484"*; W11d's answer (`W11d:205`) is *"there is no cheaper tier. `scripts/tests` is already the cheapest correct home"* and its `next action` names *"W11b as sole code owner … place the 18-function pair plus D6 and D4 only … 1466 → 1488/1500."* Both are consistent with my measured **1466** base (1466+18=1484; 1466+22=1488). They agree on the path and disagree only about D1/D2/D3/D5, which W11b listed as an open successor needing *"its own test-budget decision"* and W11d closes as *"no viable home"*. **Residual = one owner decision**, which W11d correctly routes: *"a declared ceiling amendment put to trimcrae with this measurement attached, not a routing manoeuvre by a worker."* |
| 14 | **W11d × W23** | **NOT A CONFLICT; UNRESOLVABLE-WITHOUT-A-DECISION-THE-OWNER-MUST-MAKE only on the missing input.** W23 disclaims the role (`W23:95`: *"I am **not** a second source-index repair owner — W11b is sole owner and I authored no code for it"*) and names its own gap (`W23:169`): *"Exact missing input: the freshly measured writer-base … commit-loop count."* W11d supplied a cloud-base count; my measurement is the cloud base too (1466). **The writer-base count remains UNKNOWN** and is the only thing W23 asked for. |

**Target: `systems/graph/publications.json` C5**

| # | Pair | Verdict |
|---|---|---|
| 15 | **W09d × W09e** | **NOT A CONTRADICTION — B supersedes A on the same scope. Verdict: B-CORRECT (W09e).** W09e states plainly (`W09e:93`): *"W09d's numbers are reproduced independently below and **agree**."* W09d measured the clause and declined the wording; W09e produced the correction diff and settled it. Tree: `grep -c "treatment setting is reported by no reachable series"` → `systems/graph/publications.json:1` plus **5** generated views (`L2-rt-metastasectomy`, `L2-rt-risk-model`, `L2-rt-surgical-quality`, `L2-rt-surveillance`, `L3-publications`). That is exactly W09d's *"5 view lines from 1 source field"* and consistent with W09e's field-level 6-vs-clause-level-5 refinement. The C5 wording is still in the tree unchanged. W36's "status disagreement" label reads a *timeline* as a *contradiction*. |

**The four late pairs (W36c)**

| # | Pair | Verdict |
|---|---|---|
| 17 | **W14f × W14e (U31)** | **B-CORRECT (W14f), and it is A's own precondition being executed, not a contradiction.** W14e's `next action` says *"the nine … and only those nine"* — but the **same paragraph** says: *"The successor should verify each row's guard **can fail** — drift the artifact, watch the exit code go to 1 — *before* adding the row, since a guard added without that check is the exact defect this lane has now spent four workers characterising."* W14f is that successor and returns 7 of 9. **I verified the discriminating fact in the tree**: `research/modalities/emc_tissue_read_statistics.py:425-428` is `if "--check" in argv: print(...); return 0` — an unconditional `return 0` that compares nothing and **cannot fail**. Wiring it, as W14e's "only those nine" would, adds precisely the fake guard W14e's own report was written about. All nine are absent from `preflight.sh` (`grep` → rc=1, no match). |
| 19 | **W29b × W29 (U34)** | **B-CORRECT (W29b), on measurement.** W29 asked whether a *committed floor* is right for rows 16/17/18; W29b measured the reachable states as `triggers: []`, `rows: []`, `items: []` and concludes a **zero-test** is *"the honest scope"*, with a floor being *"a separate, larger change"*. W29b also refutes W29's row-3 classification, and **I verified that in the tree**: `research/manuscripts/submission_citations.py:304-306` runs `git ls-tree … origin/literature-cache` and then iterates `r.stdout.splitlines()` with **no reference to `r.returncode` anywhere** — the silent degrade. W29b's *"the 5-of-18 figure should be restated as 4 of 18 wherever the campaign has propagated it"* is therefore well-founded. This is a correction, not a two-sided dispute. |
| 20 | **W30b × W34** | **BOTH-PARTIALLY-CORRECT-ON-DIFFERENT-SCOPES — the module sets are disjoint, measured.** W34b's seven reds are `emc_mtap_prmt5_figures`, `emc_mtap_locus_persample`, `emc_prmt5_multiplicity`, `alcam_precedent`, `emc_fusion_frame_figure`, `aso_control_oligos`, `cd248_precedent` (`W34b:116-122`). W30b's six are `emc_ipd_survival`, `km_digitize`, `endpoint_corpus`, `orr_dcr_reread`, `placebo_arm_calibration`, `endpoint_regime_map`. **Intersection: empty.** W34 itself confirms W30b's five implement `--check` (`W34:195`: *"All seven `PRODUCERS` … implement `--check`"*). None of W30b's six is in `preflight.sh` (`grep -c` → **0**). **The residual is a real policy question the owner must answer**: does *"diagnose first, wire second"* bind rows that are measured green on arrival, or only rows that would turn the gate red? W34's stated reason (`W34b:249`) is red-specific — *"Beyond the six that would turn the gate red, ranks 4 and 7 would additionally make the commit gate depend on a `literature-cache` branch fetch"* — which does not reach W30b's set. **UNRESOLVABLE-WITHOUT-A-DECISION-THE-OWNER-MUST-MAKE** on the general gate policy; **W30b is correct on the facts of its own six.** |

### Summary of verdicts

| Verdict | Pairs | Count |
|---|---|---|
| **Not a conflict at all — index scope/timeline error** | 8, 9, 10, 11, 12 (tier scope), 13 (agrees), 15 (timeline) | **7** |
| **B-CORRECT (successor supersedes)** | 4, 17, 18, 19 | **4** |
| **B-CORRECT on the decisive scope** | 3 | **1** |
| **BOTH-PARTIALLY-CORRECT-ON-DIFFERENT-SCOPES** | 2, 5, 6, 7, 20 | **5** |
| **UNRESOLVABLE-WITHOUT-A-DECISION-THE-OWNER-MUST-MAKE** | 1 (R07/R08), 14 (missing writer-base count), and the *policy* residual of 20 | **2 + 1 residual** |
| **A-CORRECT** | — | **0** |

**The headline for the owner: of 19 enumerable pairs, only one — R07 vs R08 — is a genuine forced either/or requiring a design ruling.** Seven are index scope errors that dissolve on a single tier-membership fact; five reduce to an ordering or a stated complementarity; four are a successor correcting a predecessor, three of which the predecessor's own text authorises. The contested surface is roughly a fifth the size the index reports.

---

## Validation evidence

All `RUN` in `/home/user/Rare-cancers` (read-only) or `/tmp/claude-0/w49/`. Environment: Linux 6.18.44-fc-v24, Python 3.11.15, `git version` via checkout. No network, no paid API, no GPU, no pytest, no `preflight.sh`, no `atr_hrd_sarcoma_series.py`.

| # | Command | Exit | Key output |
|---|---|---|---|
| V1 | `date -u; git rev-parse HEAD; git status --porcelain \| head -30` (start) | 0 | `Tue Sep 8 04:40:10 UTC 2026`; `408b676a…`; clean |
| V2 | `grep -c "PYTHONUTF8" scripts/preflight.sh; grep -c "PYTHONIOENCODING" scripts/preflight.sh` | 1,1 (grep no-match) | `0`; `0` |
| V3 | `ls research/modalities/tests/ \| grep -E "committed_welch\|committed_statistical"` | 1 | no match |
| V4 | `sed -n '931,945p' research/modalities/emc_fourth_cohort_quant.py` | 0 | drift tuple = `("probe_gate","n_runs_read","n_probes_common_to_every_read_run","n_genes_with_at_least_one_assigned_probe","gene_counts_sha256")` — no `probe_counts_sha256` |
| V5 | `grep -n "probe_counts_sha256" research/modalities/emc_fourth_cohort_quant.py` | 0 | one hit, `:819` only |
| V6 | `sed -n '815,819p'`, `'828,833p'`, `'568,572p'` same file | 0 | `:817` = `body = _write_probe_tsv(cache, p2g)`; `:830-831` gene write; `:570` = `def _write_probe_tsv` — W24b's anchors all correct |
| V7 | `sed -n '269,276p' W14c-fake-guard-repair-proof.md` | 0 | fence opens on `@@ -567,7 +567,7 @@`; **no file header** — W24d reproduced |
| V8 | `grep -n "@@" W14d-fourth-cohort-guard-repair.md` | 0 | `@@ -570 (def _write_probe_tsv)`, `@@ -589,593`, `@@ -830,831` — abbreviated, not applicable |
| V9 | `for cfg in "PYTHONUTF8=0" "PYTHONUTF8=0 PYTHONIOENCODING=utf-8"; do env LC_ALL=C LANG=C $cfg python3 -X utf8=0 probe.py; done` | 0 | `ascii / OPEN_FAIL UnicodeDecodeError / PRINT_FAIL UnicodeEncodeError`, then `utf-8 / OPEN_FAIL UnicodeDecodeError / PRINT_OK` |
| V10 | `env LC_ALL=C LANG=C python3 probe.py` (UTF-8 mode on) | 0 | `utf8mode= 1 / OPEN_OK 12 / PRINT_OK` |
| V11 | `grep -n "def main" -A30 scripts/tier_budget.py` (**read before run**) | 0 | only `print`/`return`; no file write |
| V12 | `python3 scripts/tier_budget.py --check` | **0** | `commit-loop 1466/1500 · modalities 7247/7500 · paper-guards 966/1000` |
| V13 | `python3 -c "import json; …"` on `scripts/tier-budgets.json` | 0 | `commit-loop ['scripts/tests','research/autonomy/tests','systems/tests']`; `modalities ['research/modalities/tests']` |
| V14 | `grep -n -B4 -A8 "Not recommended" W27-drift-gate-hash-census.md` | 0 | `:352` — *"placing any new test in `commit-loop`"*; `:246` — modalities *"headroom 253 … Affordable in the right tier"* |
| V15 | `grep -n "<nine module names>" scripts/preflight.sh` | 1 | no match — none of W14e/W14f's nine wired |
| V16 | `sed -n '840,875p' scripts/preflight.sh` | 0 | generator loop, **18 rows**, first = `submission_tables.py`, last = `news_match.py` |
| V17 | `sed -n '420,430p' research/modalities/emc_tissue_read_statistics.py` | 0 | `if "--check" in argv: print(...); return 0` — unconditional |
| V18 | `grep -c "emc_ipd_survival\|km_digitize\|endpoint_corpus\|orr_dcr_reread\|placebo_arm_calibration\|endpoint_regime_map" scripts/preflight.sh` | 1 | `0` |
| V19 | `grep -nE "^\| *(rank )?[0-9]" W34b-six-red-unrun-checks.md` | 0 | seven red modules, none in W30b's set |
| V20 | `sed -n '300,310p' research/manuscripts/submission_citations.py` | 0 | `r = subprocess.run([...])` then `for path in [ln for ln in r.stdout.splitlines() …]` — `r.returncode` never read |
| V21 | `sed -n '119p' systems/graph/publications.json`; `grep -c "treatment setting is reported by no reachable series" …` | 0 | 1 source + 5 generated views = 6 |
| V22 | end: `date -u; git rev-parse HEAD; git status --porcelain \| wc -l; python3 scripts/tier_budget.py --check; grep -c …` | 0 | `04:44:06Z`; `fb1a3f80…`; `0`; **identical** tier numbers; `0`; `1` |
| V23 | `git diff --name-only 408b676a fb1a3f80 \| grep -v opus-capacity-campaign \| wc -l` and unfiltered `wc -l` | 0 | **`0`** and `9` — HEAD drift touched only campaign files |
| V24 | `rm -rf /tmp/claude-0/w49; ls /tmp/claude-0/ \| grep -c w49` | 1 | `0` — scratch gone |

`PROPOSED (NOT RUN)`: I did **not** execute any of W30b's six generators, so W30b's *"all five exit 0 … green on arrival"* remains **SECONDARY** in this report — I verified set-disjointness and absence from the gate, not greenness. I did **not** run pytest on W17f's or W17h's delivered modules. I did **not** apply R07, R08 or C3 in any form, headed or verbatim, in any directory.

---

## Limitations

- **Adjudication of *design* preference is out of reach of measurement.** Pairs 1, 5 (residual), 6, 7 and 20 (policy) end in a judgement about what the repository *should* do. I priced them; I did not decide them, and no measurement can.
- **W36's 16th pair is unrecoverable.** Its table enumerates 15. Whether one row was dropped or the summary miscounted is **UNKNOWN**; the campaign total is 19 enumerable, not 20.
- **W27's `1497/1500` is not reproducible here and I did not diagnose the gap.** W27 attributes its number to *"the real writer"*, which may be a different machine, a different HEAD, or a different counting basis. I report only that the tree at `fb1a3f80` measures 1466 by the repository's own instrument. The 31-function difference is a real discrepancy I have not explained.
- **W23's missing input stays missing.** The writer-base commit-loop count is not obtainable from this container.
- **Report claims I did not re-execute** are marked SECONDARY inline (W30b's greenness, W12b's and W12c's site counts, W17f's pytest run, W24b's recomputed hashes, W34b's stamp comparisons). Where I contradict or confirm a report, the tree measurement is PRIMARY and quoted.
- **No scientific claim of any kind.** Everything here concerns gate wiring, tier arithmetic, patch packaging and view generation. Nothing establishes anything about EMC, NR4A3, ASOs, any degrader, any therapeutic, or any patient. No efficacy, safety, selectivity, therapeutic-window or clinical-readiness claim is made or implied. There is no wet lab.
- **No content-policy refusal occurred in this run.** Nothing to record.

---

## Stop condition

**Set up front:** return the moment every conflicting pair in W36's and W36c's tables carries (a) both claims quoted verbatim with report and line, (b) a tree measurement with file:line or command output where the conflict turns on a value in the tree, and (c) one of the four verdicts — at roughly 40 tool calls / 40 minutes, without landing, applying, patching or proposing any repair, and with scratch deleted and HEAD drift verified.

**MET.** 19 enumerable pairs adjudicated (the 20th is a counting discrepancy, reported as such); 24 validation rows; 11 tree measurements, of which 4 are independently decisive (tier membership, `commit-loop` headroom, the header-less R07 diff, the unconditional `return 0` at `emc_tissue_read_statistics.py:425`); scratch deleted; HEAD drift measured and shown to touch nothing I read. Returning immediately.

---

## Tool-call and wall-clock count actually used

**24 tool calls** (all `Bash`), wall clock **04:40:10Z → 04:44:06Z ≈ 4 minutes** of measured tool time plus report drafting. Well inside both targets. 0 network calls, 0 writes to the repository, 0 git write operations, 0 pytest invocations, 0 `preflight.sh` runs.

---

## Next concrete action

**One task, for the owner, and it is the only pair on this list that cannot be dissolved by a fact: rule on R07 vs R08 for `research/modalities/emc_fourth_cohort_quant.py`.** Everything the ruling needs is now assembled and verified against the live file — W24b's cost table, W24d's executed twelve-cell drift matrix, and the measurement that both patches are unlanded and that `:933-935` still omits `probe_counts_sha256`. **W24d's packaging finding must travel with the ruling**: whichever is chosen, the diff as published in its report is not machine-applicable — R07 needs two header lines, R08 needs full reconstruction — so "land the report's bytes" is not an available instruction for either.

**A second item, smaller and separable, for whoever maintains the index:** seven of the nineteen pairs are index scope errors, not disagreements, and five of those seven turn on one line of `scripts/tier-budgets.json`. Correcting W36's conflict table in place — rather than re-indexing — would remove them from the owner's queue at zero cost. That is coordinator work, not a research question, and I have not done it.
