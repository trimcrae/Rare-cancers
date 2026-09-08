> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Index below.

---

## Worker

**W24**, cross-cutting routing index (repairs / decisions / named missing inputs / contradictions), OPUS-CAPACITY-CAMPAIGN-20260908. Advisory index only — **no integration, merge, apply, publication or outreach authority**; the scientific owner retains all of it and does all ranking.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) from my own system context. I did not observe the served model, and no environment variable in this container names a model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start: `Tue Sep  8 02:53:54 UTC 2026`** · `date -u` **end: `Tue Sep  8 02:58:14 UTC 2026`**

`git rev-parse HEAD` **at start: `4d950cf036294627b7ae67dfb306cc1875d702ac`** · **at end: `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8`**. `git status --porcelain` → **empty at start and empty at end** (zero lines both times). All my execution was under `/tmp/claude-0/w24/`; that directory is **empty** (I needed no scratch files — every command was a read or a `git`/`grep`/`python3 -c` read). **Zero files created or modified under `/home/user/Rare-cancers`.** No git write operation, no network.

⚠ **HEAD moved twice under me during this run** — `4d950cf0` → `9ce39b4c` (eighth batch: +W09e, W12d, W15f, W19f, W21b, WAVE-LOG update) → `ce743d6a` (ninth batch: +W02e, W06e). The `reports/` directory went **92 → 97 → 99 files** while I worked. My index covers the **92 at `4d950cf0`**, plus five of the seven added mid-run, sampled. **W02e and W06e are not indexed at all.**

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — literal at end of run, sorted; five long proxy host-list variables (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy`) were present in the raw output and are filtered here only for length:

```
AI_AGENT=claude-code_2-1-263_agent
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDECODE=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_CHILD_SESSION=1
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_CODE_DEBUG=true
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_SYNC_SESSION_REFS=1
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_EFFORT=medium
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_PID=522
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
SESSION_INGRESS_URL=https://api.anthropic.com
```

---

## Question

The campaign has scattered proposed repairs, owner-routed decisions, named missing inputs and cross-report disagreements across 92+ report bodies, in a form nobody can act on. **What is the complete routing index of those four classes, ordered by target file, with each row carrying the evidence class the originating report actually earned — and which targets have two different reports proposing two different repairs?**

Open because no report indexes the campaign's *actionable residue*; W23 ranked six items by scientific importance and explicitly excluded routing, and W21/W21b audited novelty claims, not repairs or decisions.

---

## Prior-work check

Commands run and what they showed:

- `cat COMMON-BRIEF.md CLOSED-WORK.md CORPUS-CONTEXT.md` — read **in full**.
- `grep -n '^#\{1,4\} \|^| ' reports/W23-cross-output-synthesis-packet.md` then `sed -n '152,260p'` — W23's Result and W11b disposition §1 read; W23 ranks by scientific importance and states "not ranked, and why". **No routing index exists in it.** I do **not** duplicate its ranking below.
- `grep -n '^#\|^\*\*\|^| W' WAVE-LOG.md` + `sed -n '141,200p;203,260p'` — the ~02:45Z / ~02:47Z / ~02:52Z / ~02:58Z coordinator entries, which **supersede** two W23 lines (see Contradictions C4 and the W11b row).
- `for f in *.md; do … grep -c …` marker census over all 92 reports (missing-input / negative-control / exit-code / `PROPOSED (NOT RUN)` / owner-routing / blocked-route / diff-marker counts) — the table that drove every targeted read below.
- `grep -n -i -E '^#{2,4} .*(repair|patch|fix|defect|proposed change)' *.md` → 44 repair-bearing section headings.
- `grep -o -E '(research|scripts|systems)/[A-Za-z0-9_./-]+\.(py|json|md|…)' *.md | sort | uniq -c` → target-file frequency.

**Closed items I confirm I am not replaying, reopening or relabelling:** the NR4A Perspective content-policy refusal (not recreated, not rerouted, not relabelled, not indexed as an open route); the rejected registry ICD-O paper; methylation; the clinical conditional-recurrence / RT-IPD / trial-discoverability checkpoints; Brenca `PRJNA692081`/`SRP301712` (**DUPLICATE**, classification fixed and not mine to revisit); paired Davis; promoter transfer; GSE4303 / GSE28866 re-reads. I probed **no** blocked route: I made **zero** network calls this session.

**Reports read in full:** none of the 92 end to end. **Read in substantial part (named sections, ≥40 lines each):** W23, W14, W14c, W14d, W06d, W12, W12b, W12c, W12d, W13, W13b, W13c, W15c, W09c, W17c, W17e, W17g, W11c, W03, W08b, W10c, W21, W21b, WAVE-LOG.md. **Sampled (Question + Stop-condition sections only):** W09e, W15f, W19f. **Sampled by grep line only, never opened:** the remaining ~65 reports. **Not touched at all:** W02e, W06e.

---

## Method / inputs

- Live cloud checkout `/home/user/Rare-cancers` at the three HEADs above. I did **not** read the frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/` this run — every corpus statement below is transcribed from W21/W21b/WAVE-LOG and marked SECONDARY.
- Tools: `git`, `grep`, `sed`, `awk`, `find`, `wc`, `python3` 3.11 stdlib (`json`) for reading committed JSON. No network, no MCP, no paid API, no GPU.

---

## Result

### 0 · One index-wide fact I established by execution, which makes every line number below usable

**DEMONSTRATED-BY-W24 (exit 0).** Reports pin **four different read bases** — `92abbcb9` (101 mentions), `d3e9c4d8` (35), `3f5fc95d` (10), and `103ff76f` (W17c alone) — and none is the current HEAD. I therefore checked whether the drift matters:

```
$ git diff --name-only 92abbcb905cacf07f14b238db50d1b98f6590374 HEAD | grep -v 'opus-capacity-campaign-20260908'
(no output)
```

**Every commit from `92abbcb9` to `ce743d6a` touches only files inside the campaign directory.** Per-file confirmation via `git rev-parse <base>:<path>` vs `HEAD:<path>`: `emc_mortality_decomposition.py`, `emc_relative_survival.py`, `emc_terminal_events.py`, `emc_fourth_cohort_quant.py`, `scripts/preflight.sh`, `scripts/tier_budget.py`, `systems/POLICY-evidence.md` are **all byte-identical across the whole span**. **Consequence: every `file:line` anchor in this index is still valid at HEAD, and diffs cut against different bases still apply to the same bytes.**

### 1 · Repairs proposed to committed files — ordered by target file

Evidence-class legend, applied per row: **DBE** = DEMONSTRATED-BY-EXECUTION (the report itself quotes command + environment + real exit code); **DBW24** = I executed the check myself this session; **PNR** = `PROPOSED (NOT RUN)`; **ROD** = READ-ONLY-DIAGNOSIS (a defect described, no repair authored). *A worker report is not a test result; rows without an exit code carry no execution evidence.*

"Gate-reachable" answers **would anything in the tree catch the defect this repair fixes** — measured by me at HEAD with `grep -c <module> scripts/preflight.sh`, `grep -rl <module> .github/workflows | wc -l`, `grep -rl <module> --include='test_*.py' research scripts systems | wc -l`.

| # | Target file (repo path) | Anchor / lines | Proposing report | Body returned inline? | Negative control executed? | Real exit codes in report | Gate-reachable at HEAD (my measurement) | Class |
|---|---|---|---|---|---|---|---|---|
| R01 | `research/data/emc-clinical-registry.json` → `cohorts[0..4]` (+ 3 Meis-Kindblom `denomNote`) | `W13b:239-275` | W13b | **Yes** — full deterministic patch script, order-preserving, asserts every `n`/`sourceId` it keys off | Report has RUN2 byte-calibrated mirror + RUN4 "the patch does not damage anything"; **I did not read its exit codes** | 9 exit-code markers present in file; **not read by me** | `validate-registry.mjs` **is** in preflight (2 hits) — but `nUnit` is a *new* field no validator knows, so **NO**, nothing catches its absence | ROD + report-claimed DBE, unverified by me |
| R02 | same file → `cohorts[5..13]` | `W13c:318-348` | W13c | **Yes** — same shape, same `put()` helper | as above; 10 exit markers | not read by me | as R01 | as R01 |
| — | **Ordering, stated by W13c itself:** "*It **extends** W13b's patch and does not modify or replace it — apply W13b's first, then this.*" **Not a conflict.** Both are `ROUTED, NOT APPLIED`; the registry is protected state under `systems/POLICY-evidence.md` and `CLAUDE.md` §7. | | | | | | | |
| R03 | `research/manuscripts/emc_mortality_decomposition.py` `@@ -218`, `@@ -269`, `@@ -282` | `W06d:133-180` | W06d | **Yes** — unified diff, adds `IMPOSSIBLE_FRACTION_QUOTABLE_MAX` + `quotability()` readout | **Not stated as run**; boundary behaviour exercised directly (7 input/output pairs) | 9 exit markers; W06d states preflight/pytest **blocked by missing `pytest`** in its environment | preflight **0**, workflows **0**, tests **1** → **effectively NO** | PNR for the gate; boundary probe DBE |
| R04 | same file (**second, different repair**) — `--check` guard | `W14:144-232` | W14 | **Yes** — diff plus `_emit()` helper body | **YES, real** — `9 failed` (`PYTEST_EXIT=1`) before patch, `9 passed` after; artifact corruption → `--check` exit **0** pre-repair | quoted: `PATCH_EXIT=0`, before `1`, after `0` | as R03 | **DBE** |
| ⚠ | **FLAG — two reports edit one file.** W06d (quotability readout) and W14 (`--check` guard) both modify `emc_mortality_decomposition.py`. They are *not* the same change and do not obviously conflict textually, but **the owner must sequence them and re-cut the second diff after the first lands.** Neither author knew of the other. | | | | | | | |
| R05 | `research/manuscripts/emc_relative_survival.py` | `W14:130-232` | W14 | Yes (same 3-file diff) | **YES** (same before/after suite) | `0` pre-repair on corrupted artifact; suite `1` → `0` | preflight **0**, workflows **0**, tests **0** → **NO** | **DBE** |
| R06 | `research/manuscripts/emc_terminal_events.py` | `W14:130-232` | W14 | Yes | **YES** (same suite) | as R05 | as R05 → **NO** | **DBE** |
| — | W14's own residual, its words: adding these three as rows in `scripts/preflight.sh`'s `--check` gate list, and running the gate, is **`PROPOSED (NOT RUN)`**. "*The three fixed scripts are now* eligible *for it; I did not make them members.*" | | | | | | | |
| R07 | `research/modalities/emc_fourth_cohort_quant.py` — `@@ -567`, `-586`, `-736`, `-814`, `-827`, `-930` (6 hunks) | `W14c:266-360` | W14c | **Yes** — unified diff; splits `_write_probe_tsv` into `_probe_tsv_body_impl` / `_probe_tsv_body` / writer | Report shows a pre/post modality-tree byte diff (`NONE`); two drift legs D1/D2 | 28 exit markers | preflight **0**; **1 workflow** (`.github/workflows/emc-expression-datasets.yml:1065-1066`, **explicitly non-blocking**: `\|\| echo "--check reported drift; non-blocking"`); tests **1** → **NO** | report-claimed DBE |
| R08 | **same file, a DIFFERENT repair** — 4 edits, 92 diff lines: a `write=` switch on `_write_probe_tsv`/`derive`, and hashing committed bytes **off disk before `derive()` runs** | `W14d:115-232` | W14d | **Yes** — hunks plus the complete repaired `--check` body | **YES, three drift classes, one file at a time** — T2 `exit 1` file left `2168ab58…`; T3 `exit 1` left `f273b0c0…`; T4 `exit 1` left `e7b31a6e…`; T1 clean `exit 0`, nothing written; T5 no-regression `exit 1`; T6 both TSVs bit-identical; T7 `20 passed` exit 0; T8 `selftest: 0 failure(s)` exit 0 | 23 exit markers, all eight T-rows carry one | as R07 → **NO** | **DBE, and the strongest negative control in the campaign** |
| ⛔ | **FLAG — TWO DIFFERENT REPAIRS FOR ONE TARGET. The owner must apply exactly one of R07 or R08, not both.** They are alternatives, not layers. Discriminating facts, all from the reports themselves: (a) W14d is **smaller** — "*one file, four edits … smaller than W14c's (no function split, one keyword parameter instead of two, no `bodies` dict)*"; (b) W14d finds a **third sub-defect W14c did not** — D3, a probe-*count* drift that byte comparison can never see because `load_inputs()` rehydrates counts from the probe TSV itself (`:552-566`), fixed only by adding `probe_counts_sha256` to the drift key tuple at `:940-941`; (c) W14d **independently reproduces W14c's D1/D2 including the same intermediate shas**, so W14c's diagnosis is confirmed even if its patch is not the one applied. W14c was cut against `92abbcb9`, W14d against `3f5fc95d` — **§0 shows the file is byte-identical between them**, so this is a genuine choice, not a base artifact. | | | | | | | |
| R09 | `research/manuscripts/endpoint_regime_map.py` (`:264-267`, `:544`, `:554`) and `research/manuscripts/placebo_arm_calibration.py` (`:202-216`) | `W12:270-300` | W12 | **Yes** — code blocks, not a `git apply`-able diff | No | 12 exit markers, 3 `PROPOSED (NOT RUN)` | preflight **0**; workflows **1** each; tests **4** each | **PNR — W12 labels these "PROPOSED (NOT RUN), do not apply without the owner"** |
| R10 | the same encoding class across **35** `research/manuscripts` generators | `W12b:150-330` | W12b | Yes — an AST-guided patcher, run in `/tmp` | Partial: the "STILL BROKEN" arm is itself the control | 23 exit markers, 4 `PROPOSED (NOT RUN)` | as R09 | **DBE, partial** — fixes **11 of 35**, of which **10 proven byte-identical to the committed sha256** (named: `endpoint-regime-map.json` `f542b99d…`, `fusion-junction-aso-submission-tables.md` `cd7f516c…`) |
| R11 | `scripts/preflight.sh` (~line 103) — `export PYTHONIOENCODING=utf-8` | `W12c:319-341` | W12c | Yes — one line, with its comment | No | 10 exit markers | this **is** the gate | **PNR — W12c: "Owner's call; I am not making it."** |
| R12 | `scripts/preflight.sh` line ~94 — **`export PYTHONUTF8=1`** (a *different* one-line repair to the same target) | `W12d:217-268` | W12d | Yes — the diff hunk including its ⛔ comment | **YES** — six candidate shapes scored; the corruption arm demonstrated, not asserted: `PYTHONIOENCODING=ascii:replace` makes `atr_hrd_sarcoma_series.py --check` return **rc=0 with mangled output** | 5/5 encode sites reproduced under `env -i … LC_ALL=C LANG=C PYTHONUTF8=0 python3 -X utf8=0`; **18/18 gate rows rc=0 with all 18 combined-output sha256 identical to baseline** | this **is** the gate | **DBE — and it settles R11 on evidence:** candidate A (`PYTHONIOENCODING`) leaves **5 of 18 rows red** under a C locale because it fixes only the write side; A2 fixes 16 print rows **and** 5 decode rows |
| ⛔ | **FLAG — three reports, one target, three shapes.** `scripts/preflight.sh` stdout/locale repair: W12b (five-module source form) ⊂ W12c (A, one env line) vs W12d (A2, a different env line). **W12c's own census refutes W12b's scope** (5 modules cover 23 of 1,031 sites, 2 of 16 affected gate rows). **W12d's execution refutes W12c's choice of variable.** Apply **one**. W12d's own honest residual: "*there is no single change that fixes all 1,031 sites*" — environment is per-process, with an **UNKNOWN upper bound of 173** re-parented subprocesses. | | | | | | | |
| R13 | `scripts/source_reuse_index.py` (1056 lines) + `scripts/tests/test_source_reuse_index.py` (477 lines) | `W11b:208-1263`, `:1271-1747` | W11b | **Yes — complete final file bodies, both** | **YES — owner-measured, and it is the campaign's cleanest control:** final pair **18 passed, exit 0**; **negative control**, same tests against the *unchanged original* helper, **7 failed / 11 passed, exit 1** (`WAVE-LOG.md` ~02:47Z, recorded as the **scientific owner's own terminal run**, not a worker claim, not the coordinator's) | W23 V7/V8/V9/V10 all exit 0 — sha256 `b3288598…` / `49208917…` independently recomputed and **matched**; py_compile 0/0; 18 test methods counted statically | **Neither file exists at HEAD** — `ls` exit 2, confirmed by me. So: **nothing catches anything; there is no defect in the tree to catch.** | **DBE (standalone)** |
| ⛔ | **TWO FLAGS on R13.** (1) **Path divergence, DBW24:** the delivered input bundle lives at `research/autonomy/opus-capacity-campaign-20260908/inputs/source-index/**research/tools/**source_reuse_index.py` (+ `research/tools/tests/`), while W11b/W11c/W23 all name **`scripts/`** as the intended destination. `research/tools/` **does not exist** in the live tree. The owner must fix the destination before any placement. (2) **Its "missing input" is now supplied, and the answer is negative:** `WAVE-LOG.md` ~02:45Z records the owner's measured writer-4878 baseline `scripts/tier_budget.py --check`, **exit 0**, commit-loop **1497/1500 across 105 files**. **1497 + 18 = 1515 > 1500.** Integration eligibility is **NEGATIVE**, and the three ways to make it fit are all explicitly refused (raise the ceiling / hide tests from accounting / invent a 30-case gate). **This supersedes W23 Rank 1's "exact missing input" line.** | | | | | | | |
| R14 | `systems/graph/artifacts.json` — notes on `ART-RT-CONTRADICTION` and `ART-CARE-DELIVERY-EVIDENCE` (2 of 56 notes) | `W09c:265-300` | W09c | Yes — replacement note text, plus a standalone acceptance test | **YES — RED/GREEN, the load-bearing evidence:** acceptance test at HEAD → `2 failure(s)`, **EXIT=1**; on the scratch fixture → `0 failure(s)`, **EXIT=0**; T4 shows all **54 unrelated notes hash-identical**, no node added or removed | quoted, exit 1 and exit 0 | `systems_check` is heavily gated (preflight **10**, workflows **2**, tests **7**) | **DBE** |
| R15 | `systems/graph/publications.json:119` — the C5 clause of `PUB-CARE-DELIVERY.why_not_written` | `W09e` Result/Stop | W09e | Yes — full correction diff | Regeneration proof: exactly **5 lines in 5 files** change; **106 of 111 views byte-identical by md5**; exactly 6 files differ tree-wide | regeneration exit **0** | as R14 | **DBE** (sampled: I read W09e's Question + Stop only) |
| — | Both R14 and R15 target **`systems/graph/`, which `CLAUDE.md` §7 names as owning model state** and `systems/views/` as generated. Neither may be applied by a worker. W09d measured the blast radius of one clause but **explicitly declined the wording**; W09e supplies it. | | | | | | | |
| R16 | `research/manuscripts/pinned-figures.json` — 11 candidate `artifact_figures` entries | `W17e:R5 ff.` | W17e | **Yes** — keyed JSON block | **YES** — all 11 verified clean by the repository's own `check_artifact_figures`, **and all 11 shown to redden when the artifact moves** | 7 exit markers | the pin registry is the gate; the entries do not exist yet, so **currently NO** | **DBE** |
| R17 | same file — **one further entry**, a second pin on the same key with `"scale": -1.0` | `W17g:~240` | W17g | Described, **not authored** ("only the pin registry entry, which is part of the routed repair below and which I have **not authored**") | n/a | 3 exit markers | as R16 | **ROD / PNR** |
| — | R16 + R17 are **complementary, same file, two reports** — the owner should land them as one edit. Not a conflict. | | | | | | | |
| R18 | PUB-ATR manuscript prose, **line 761** (`0.41× that standard error`) | `W17g:249-262` | W17g | No — "*a routing note, not a patch*"; two defensible forms given (`0.37×` at n=565, or the range `0.37–0.38×`) | n/a | arithmetic re-derived from the committed artifact | frozen-paper adjacent | **ROD**, arithmetic verified in-report |
| R19 | PUB-ATR manuscript prose, **`:566-567`** (the MDE formula sentence) | `W17c:155-175` | W17c | A ~14-word insertion naming the t critical values on the Welch df | n/a | 3 exit markers | as R18 | **ROD** |
| — | R18/R19 hit **different lines of the same frozen-paper-adjacent document**. **W17g states the ordering constraint explicitly:** the artifact half "(b) implemented honestly will emit `0.37×`/`0.042`, so it will *fail* against the current prose. **(a) must land first or with it.**" | | | | | | | |
| R20 | `research/modalities/emc_atr_vulnerability.py` + `emc-atr-vulnerability.json` — instrument `0.1968` / `0.0155` / `0.41×` and the per-row minimum `n` | `W17e:405`, `W17g:257` | W17e, W17g | No | n/a | — | preflight **0**, workflows **2**, tests **4**; the figures are **prose-only**, so `--check` **cannot re-derive them** — **NO** | **ROD — both say "the owner's call"** |
| R21 | `lint_consistency._dig_json` — bracket/escape support so `per_platform["…txt.gz"]` keys become addressable | `W17e:188,404` | W17e | No — a `KeyError` reproduction is quoted | n/a | reproduction quoted | this is gate machinery | **ROD.** Without it, 27196 and 20629 **have no dot-safe path** and cannot be pinned at all |
| R22 | lane-15 module — add invariant **I6** (`denominator_status=="STATED"` ⇒ `denominator_means` ∈ 5-value unit enum) | `W15c:198-225`, consequences in `W15d` | W15c | Described as "one line in lane 15's module" | Measured both ways against the real committed registry: base **34 CONSTRUCTED / 17 lossless / 13 REFUSED** → with I6 **17 / 0 / 30** | 5 exit markers (W15c), 15 (W15d) | — | **DBE for the measurement.** Its finding: *under a schema requiring a unit, the clinical registry currently supports **zero** fully-typed quantitative records* |
| R23 | `research/manuscripts/endpoint/emc-systemic-therapy-pooling.json` — 2 items | `W05e:255,342` | W05e | Described | n/a | 1 exit marker | — | **ROD — "routed, not applied"** |
| R24 | registry **schema** — add a `periodBasis` field (`diagnosis` \| `registration` \| …) | `W05d:180` | W05d | Described | 7 negative-control mentions in-report | 4 exit markers | — | **ROD.** W05d is explicit that the correct answer is **an addition, not a relaxation** |
| R25 | `research/data/aso-per-junction-table.json` — **all 38 junctions fix the 3′ acceptor at `NR4A3_e3`** | `W03:114-130` | W03 | **No repair authored** | n/a | 1 exit marker | — | **ROD.** Two published sources contradict it as a universal (Urbini 2018 `exon7/exon2`; Panagopoulos 2002 "*12 breakpoints in intron 2 and only two in intron 1*", i.e. 2/14). A published breakpoint class is **structurally unrepresentable** in the enumeration. W03 states plainly this "*is not reagent design and implies nothing about any molecule*". W03b closed the acceptor-coverage question as ALREADY-KNOWN. |
| R26 | **tool defect, not a repo file** — `mcp__PubMed__get_full_text_article` **silently accepts a PMID as a PMCID and returns a different paper** | `W10c:60-64` | W10c | n/a | Reproduced: passing `pmc_ids:["11493979"]` returned `PMC11493979 / PMID 39433838`, a neuroscience TMS paper, ~15 KB, **no error, no warning** | — | nothing catches it | **DBE. Routed to the coordinator/tooling owner. Any worker passing a PMID here gets confident full text of the wrong article.** |

**Gate-reachability summary, DBW24.** I read `scripts/preflight.sh:845-864` — the 18-row `--check` loop — and enumerated it. **Not one repair target above is a member.** The 18 are: `submission_tables`, `claim_coverage`, `submission_citations`, `submission_metrics`, `aso_sequence_manifest`, `aso_journal_tables`, `aso_offtarget_duplex_energy`, `submission_packet`, `vaccine_path_tables`, `aso_archive_manifest` (`--check-archive`), `aso_deposit_drift`, `emc_condensate_report`, `atr_hrd_sarcoma_series`, `single_slot_identity`, `instrument_census`, `trigger_scan`, `citation_debt`, `news_match`. **Every guard repair in this index fixes a guard that no blocking gate runs.** Repairing them is necessary but, on its own, **enforces nothing** — W14d's phrasing, independently confirmed by me at HEAD.

### 2 · Questions explicitly routed to an owner rather than decided

| # | Question as the report puts it | Owner class | Anchor | Evidence already assembled | What is specifically missing |
|---|---|---|---|---|---|
| D01 | Which of R07/R08 is the repair for `emc_fourth_cohort_quant.py`; and separately, **should the non-blocking workflow row be made blocking?** | tooling | `W14d:173` | Both repairs, both with drift tables; W14d's 8-row acceptance suite | A decision. W14d: "*wiring it is a coordinator decision I did not take.*" |
| D02 | `PYTHONIOENCODING` vs `PYTHONUTF8` vs per-entry-point `reconfigure`; and `errors=` strict vs replace | tooling | `W12c:341`, `W12d:217` | 1,031-site census; 6 scored shapes; 18/18 gate sweep with sha256 | Only the choice. W12d recommends A2 and states its residual (≤173 subprocesses, **UNKNOWN**) |
| D03 | Should `_generated_utc` stay in the eight timestamped artifacts? | tooling / provenance | `W12b:471`, `W12c` Finding C | The 5 manifest-hashed stamped paths; the `--check-archive` precedent at `scripts/preflight.sh:748-758` | A design decision. **W12c proposes no removal** and refuses to pre-empt it |
| D04 | Which of the 35 `research/manuscripts` generators does the owner want patched? | tooling | W23 Rank 4 | 11 fixed, 10 byte-proven | Scope only — **no missing measurement** |
| D05 | Do the registry `nUnit` patches land, and in which order? | registry / policy | `W13b:241`, `W13c:322` | Two complete patch scripts, every value source-quoted | Registry-owner authority under `systems/POLICY-evidence.md` |
| D06 | `evidenceQuestions[]` — the ≥2-opposing-positions rule is **validator-enforced** at `validate-registry.mjs:124`, but the committed registry has **no `evidenceQuestions` at all** | registry / policy | `W13` (post-A12 note) | Keys enumerated: `['intro','dataStatus','dataStatusBanner','fields','patients','cohorts','citations']` | **UNKNOWN as to intent.** A live rule with an absent subject |
| D07 | Are A5/A6 policy breaches or unguarded invariants? | registry / policy | `W13d:168` | W13d's reframing | W13d's own answer: they are properties **the policy does not currently require** — the owner decides whether it should |
| D08 | Provenance defensibility of the file that already used the disputed row | registry / policy | `W13e:219` | Admissibility settled (**no**); provenance separate | "**UNKNOWN, owner's call**" |
| D09 | The two ENTANGLED denominator records | registry / policy | `W15e:348` | V1–V7 enumerated with sha1 and occurrence counts | A single scoped routing to the two artifact owners |
| D10 | V5/V7 name the grandparent (171), V6 the parent (142) — reword or leave? | manuscript / registry | `W15f:163,250` | **Resolved as one series at two nested scopes** | "*a wording judgement for the owner, not a defect*". Constraint: any V5 edit must move `emc_radiotherapy_contradiction.py:273-275` **and** the artifact in one commit |
| D11 | Is a 0.6/1.7 pp move worth re-stamping a minted DOI? | manuscript / publication | `W16c:285` | Cost **costed, not weighed** | A judgement |
| D12 | The `bishop2019` clause | manuscript | `W16c`, `W16d:96`, `W13e` | Three reports landed on it | Owner's decision; W16d explicitly did not argue it |
| D13 | PUB-ATR prose: which of W17g's two forms for line 761 | manuscript (PUB-ATR) | `W17g:255` | Both forms with their `n` | The choice, and it must precede D14 |
| D14 | Instrument the four PUB-ATR quantities into generator + artifact? | manuscript (PUB-ATR) | `W17e:405`, `W17g:257` | The exact fields named | "*the same class of repair as `p1s[0]`'s and is the owner's call*" |
| D15 | Bracket support in `_dig_json`, **or** a flat mirror field in the artifact? | tooling **and** manuscript | `W17e:404` | The `KeyError` reproduction; 2 of 4 keys already worked around via dot-safe twins | Two owners must agree; 27196 / 20629 unpinnable either way today |
| D16 | Promote `welch_df_identity.py` / `welch_variance_inversion.py` / `atr_point_verify.py` into `research/modalities/tests/`? | tooling | `W17:273`, `W17b:513`, `W17d:737` | Three working scripts | Write authority + tier budget. W17f asks separately for **8** functions of `modalities` headroom (7247→7255) — **a different tier, does not compete with R13** |
| D17 | Does an Actions-runner fetch of the Kawaguchi PDF count as a genuinely new route? | coordinator / policy | `W10d:197` | The prior denials | "*a coordinator decision rather than a worker task*". **Do not treat this as authorization** |
| D18 | Ceiling amendment for R13, or drop it | tooling / owner | `WAVE-LOG.md` ~02:45Z | The measured 1497/1500 and the 1515 projection | **A declared ceiling amendment with the measurement attached is the only remaining path, and it is the scientific owner's decision.** Three shortcuts explicitly refused |
| D19 | W11c's D7 (supersession designation) and D8 (title candidates) are **real divergences that should probably not be closed** | tooling | `W11c` §3 | 8/8 divergences confirmed by executed probes | D7 would make the tool decide which retained status supersedes which; D8 is an **internal contradiction in the review itself** (praises exact-match, then faults it for it). D3 is unsatisfiable as worded |
| D20 | `emc-mortality-decomposition-inputs.json` design gap | manuscript | `W06b:230` | Reported, deliberately no fix proposed | "*a design change, not a field change, and needs its owner's judgement*" |

### 3 · Named missing inputs — **blocked** / **pending** / **nonexistent**

**BLOCKED — a recorded access denial. Never to be probed, retried unchanged, or rerouted.** I made zero network calls; every entry is transcribed.

| Input | Denial recorded | Anchor |
|---|---|---|
| GSE243553 `MOESM3_ESM.zip` → `Supp_Data_1_new/*_markers.bed` (genome-wide intervals, 32 peaksets) | **403 CONNECT policy denial** from this container; W20b did not test, retry or route around it, nor did W23 | `W20b`, `W19d`, `W23` Rank 3 |
| Brenca 2019 sequencing accession | **14 distinct routes**, `curl: (56) CONNECT tunnel failed, response 403` / `EGRESS_BLOCKED` across Europe PMC (2 hosts, 2 transports), Crossref, PMC, and a 12-host reachability probe | `W01b:98-111,183` |
| `eutils.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`, `europepmc.org`, `api.crossref.org`, `pmc.ncbi.nlm.nih.gov`, `www.nature.com`, `www.mdpi.com`, `mitelmandatabase.isb-cgc.org`, `api.gdc.cancer.gov`, `cancerimagingarchive.net` (×3), `zenodo.org`, `arxiv.org` | 403 CONNECT / `EGRESS_BLOCKED`, verbatim JSON retained | `W01:161`, `W02:201-202`, `W03:74-75`, `W04:113-119,185-197` |
| ArrayExpress/BioStudies, EGA, dbGaP, cBioPortal, GDC archive-side sweep | "**UNKNOWN — not searchable from here**"; W01 states the negative is **route-bounded and NOT a statement that no such resource exists** | `W01:136,142` |
| Sunitinib 2014 (`PMID 24703573`), Wagner 2020, CTARC 2022, Pazopanib primary, Trabectedin/RT 2018, Hofvander (EGA controlled-access) | standing closures, three institutional 403 routes exhausted on Sunitinib | `CLOSED-WORK.md` |
| The restricted NR4A Perspective review | **content-policy refusal**, closed without probes | `CLOSED-WORK.md` — **retained, never routed around, not reopened here** |
| Panagopoulos / Urbini full tables | `EGRESS_BLOCKED`, unread; W03b states **nothing depends on them** | `W03b:179` |
| Full text of 9 (W04c) and 16 (W04b) case reports | would need paywalled routes the brief forbids | `W04b:244`, `W04c:279` |

**PENDING — exists, not yet supplied here.**

| Input | State | Anchor |
|---|---|---|
| `research/autonomy/nr4a3-patient-junction-source-2026-09-07/` + `retrieval.json` | **Absent from the live checkout at every HEAD this campaign has read; PRESENT in the frozen corpus as 13 corpus-only files** (`README.md`, `brenca-origin-gate.csv`, `recover.py`, `retrieval.json`, `sources/*`). SECONDARY — I did not read the corpus | `W21b:R0,N1,N3`; `WAVE-LOG.md` ~02:58Z |
| Fresh writer-base `scripts/tier_budget.py` commit-loop count | **NO LONGER MISSING.** Owner-measured, exit 0: **1497/1500 across 105 files.** Answer: **integration NEGATIVE (1515 > 1500)** | `WAVE-LOG.md` ~02:45Z — **supersedes W23 Rank 1** |
| `research/autonomy/clinical-methods-checkpoints-2026-09-07` | not in this checkout (`ls` exit 2). W08 correctly called it **UNKNOWN, not proof of absence**; W21 C3 records it as an UNKNOWN correctly resolved | `W08:133`, `W21:144` |
| `atlas-primary-matrix-availability.json` | named "(pending input)" | `CLOSED-WORK.md` |
| A Windows host | none available — **every Windows-specific exception string in W12 is a PREDICTION**; only the mechanisms are reproduced on Linux | `W12` Limitations |
| `pytest` in the W06d lane environment | absent — blocks W06d's own gate run; "*The generator's owner must run it*" | `W06d:302` |
| Executor packet paths and hashes for the owner's R13 terminal run | "*will follow when supplied — **this log must not invent them***" | `WAVE-LOG.md` ~02:47Z |
| The frozen corpus itself, for **me** | I did not read `/tmp/claude-0/frozen-corpus/extracted/corpus/` this run | this report |

**NONEXISTENT — the thing named does not exist, and that is the finding.**

| Input | Anchor |
|---|---|
| IMMUNOSARC II EMC cohort full paper — **not yet indexed** | `W05e:303` |
| Any `denominator_unit`, or **any key matching `/unit/i` at any depth**, in the four scanned committed files | `W15e:176`, `W15d`; corroborated `W21b:N9` |
| `evidenceQuestions[]` in the committed registry — the enforcing rule is live, its subject absent | `W13` |
| Any tracked `.bed` file anywhere in the tree | `W20b` (via `W23` Rank 3) |
| A dot-safe artifact path for the probe counts 27196 / 20629 | `W17e:188` |
| A second `source_id` that would make W15f's option (B) true | `W15f:160` |
| `research/tools/` in the live tree (R13's apparent intended home) | **DBW24** — `find` shows it only inside `inputs/source-index/` |
| `scripts/source_reuse_index.py`, `scripts/tests/test_source_reuse_index.py` | **DBW24** — `ls` exit 2 |

### 4 · Contradictions — both sides, with anchors. **I adjudicate only where committed data settles it arithmetically.**

| # | Side A | Side B | My disposition |
|---|---|---|---|
| C1 | `W08`: "*3 frame articles have no abstract available (PMIDs 12672100, 16337717, 21753718)*" | `W08b:330`: literal-string screen finds **5** — adds `28467750` and `36097623`; "*The honest statement is **5/84 abstracts unretrieved, UNKNOWN, not zero***" | **NOT ADJUDICABLE on committed data.** DBW24: the 84-article frame is a **live PubMed query**, W08b's files are in scratch, and no committed JSON carries the 84-article frame (the only `Abstract not available` hits are `citation-retraction-notices.json` and `-sweep.json`, 1 occurrence). W08b **executed** the screen; W08 did not. Both sides recorded; the owner decides. |
| C2 | `W12b`: the five-module `sys.stdout.reconfigure` shape | `W12c:323`: it "*is correct and insufficient*" — leaves 1,008 of 1,031 sites and 14 of 16 affected gate rows unrepaired | **Not adjudicated — but C3 settles the practical question.** W12c's census is a measurement; W12b never claimed whole-class coverage. |
| C3 | `W12c` Finding A: `PYTHONIOENCODING=utf-8` | `W12d:219`: recommends `PYTHONUTF8=1` instead — "*A leaves 5 of 18 gate rows red under a C locale, because it fixes only the write side*" | **W12d carries execution evidence and W12c does not on this point** (18/18 rc=0 with identical output sha256 vs 13/18). Recorded as an evidence asymmetry, not adjudicated by me. |
| C4 | `W23:223`: `nr4a3-patient-junction-source-2026-09-07/` "*is **not** in the 5,996-file frozen corpus*" | `W21b:R0,N1`: **present as 13 corpus-only files**, with `grep` counts (`→ 13`, `→ 13`, `ls … → no output, exit 1`) | **W21b carries the command evidence and W23 does not.** `WAVE-LOG.md` ~02:58Z records the coordinator's own correction: the path was `…/extracted/corpus/`, not `…/extracted/`. The **checkout half of W23's statement stands**; the corpus half does not. SECONDARY — I read neither. |
| C5 | `W01e:148`: "*The only EGA accession anywhere in the tree is `EGAS00001002795`*" | `W21b:N2`: **six** distinct EGAS accessions — four in the **live tree**, two corpus-only | **CONTRADICTED per W21b.** Not verified by me. |
| C6 | `W13c:139,387`: Giner 2022 "*identified here for the first time*" | `W21b:N4`: the full citation is in the **live tree at two paths** — a **live-tree** contradiction, not a corpus one | **CONTRADICTED per W21b.** Novelty claim only; the unit work is unaffected. |
| C7 | `W01:59,136,234,242`: "*Zero `E-MTAB-`, zero `EGAS`, zero `phs` accessions anywhere in the tree*" | `W21:142` C1: **CONTRADICTED** by the corpus | per W21. |
| C8 | `W12:432`: "*The Windows path-separator failure logs are not in the tree*" | `W21:143` C2: **CONTRADICTED** by the corpus | per W21. Note W23 Rank 4 already treats W12's premise as honestly self-corrected. |
| C9 | `W13:92`: "*No committed file anywhere carries `n_patients`, `n_specimens`, or a `namespace` declaration*" | `W21:145` C4: **CONTRADICTED, but by the live tree, not the corpus** | per W21. |
| C10 | `W13e:90,333`: "*`W13d-*.md` **DOES NOT EXIST** at this HEAD*" (`cat` exit 1; filesystem-wide `find` negative) | `W13d-population-overlap-validator.md` is present in `reports/` now | **Resolved by time, not by error.** W13e's record was accurate when made; every W13d finding it relied on is flagged in-report as a transfer limit. **The owner should re-check W13e's framing against the now-present W13d.** |
| C11 | `W10c` R1: registry `masunaga2025` **n = 171** | `W13b:246` / `W23`: `C[0]["n"] == 134` | **ADJUDICATED BY ME — both are right; there is no contradiction.** DBW24, reading the committed `research/data/emc-clinical-registry.json`: `citations.masunaga2025.n = 171` at **line 652** (registered series) and `registry.cohorts[0].n = 134` at **line 371** (localized analytic), with `cohorts[1].n = 29` (metastatic at diagnosis). Arithmetic on committed integers: **134 + 8 (non-surgical, excluded) = 142 localized**, and **142 + 29 = 171 registered**. W15f establishes exactly this nesting independently from the source's own Table 1 headers. **This is C-11 as an instance of D06/R01: the registry commits two `n` in two sections with no machine-readable unit or scope field to tell them apart** — precisely W13's contract gap. |
| C12 | Four different pinned read bases across the corpus: `92abbcb9` (101 mentions), `d3e9c4d8` (35), `3f5fc95d` (10), `103ff76f` (W17c alone) | — | **ADJUDICATED BY ME as harmless for this index.** DBW24: `git diff --name-only 92abbcb9 HEAD` outside the campaign directory returns **nothing**. All anchors remain valid. |
| C13 | `W19c` §3: SHARES-3 **post-hoc**, p = 0.00008, "PREDICTS LOCATION" | `W19e` pre-declared same-family (n=15, p at the 50,000-draw floor); `W19f` ran the pre-declared falsification `SAMEFAM-DIFFGENE-DIFF5′` (n=8, **p = 0.00084 — did not falsify**) | **NOT A CONTRADICTION — a sequence, and I do not adjudicate it.** These are three stages of one pre-registration chain, each stating its own confounds (W19e: 14/15 ETS, 7/15 share EWSR1). **No clinical claim; no mechanism; ASSOCIATION only.** Left entirely to the scientific owner, and deliberately not re-ranked against W23. |

---

## Validation evidence

All `RUN` by me unless marked. Environment: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `python3` 3.11 stdlib only, cwd `/home/user/Rare-cancers`, **no network**, no paid API, no GPU.

| # | Command | Exit | Key verbatim output |
|---|---|---|---|
| V1 | `date -u` (start) | 0 | `Tue Sep  8 02:53:54 UTC 2026` |
| V2 | `git rev-parse HEAD` (start) | 0 | `4d950cf036294627b7ae67dfb306cc1875d702ac` |
| V3 | `git status --porcelain` (start) | 0 | *(empty)* |
| V4 | per-report marker census over 92 reports (`grep -c` ×8 each) | 0 | the census table (drove all targeted reads) |
| V5 | `git diff --name-only 92abbcb905…374 HEAD \| grep -v opus-capacity-campaign-20260908` | 1 (no match) | **no output — nothing outside the campaign dir changed** |
| V6 | `git rev-parse <base>:<path>` vs `HEAD:<path>` ×7 | 0 | `UNCHANGED` for all seven repair targets |
| V7 | `ls`/`wc -l` on 9 target paths | mixed | `scripts/source_reuse_index.py` and `scripts/tests/test_source_reuse_index.py` **ABSENT**; `emc_fourth_cohort_quant.py` 958 lines; `scripts/preflight.sh` 1648 |
| V8 | `python3 -c "import json; …"` over `research/data/emc-clinical-registry.json` | 0 | 14 cohorts; `0 masunaga2025 n= 134`, `1 masunaga2025 n= 29`, … `9 seer270_2022 n= 270` |
| V9 | `sed -n '640,665p'` same file | 0 | `"n": 171,` under `citations.masunaga2025`, `"design": "retrospective national registry cohort"` |
| V10 | gate-reachability sweep — `grep -c <mod> scripts/preflight.sh`; `grep -rl <mod> .github/workflows \| wc -l`; `grep -rl <mod> --include='test_*.py' …` ×13 | 0 | `emc_fourth_cohort_quant preflight=0 workflows=1 tests=1`; `emc_relative_survival preflight=0 workflows=0 tests=0`; `systems_check preflight=10` |
| V11 | `sed -n '845,866p' scripts/preflight.sh` | 0 | the 18-row `--check` loop, enumerated in §1 — **no repair target is a member** |
| V12 | `find …/inputs -maxdepth 5 -type f` | 0 | `…/inputs/source-index/research/tools/source_reuse_index.py` — **`research/tools/`, not `scripts/`** |
| V13 | `grep -o -h -E '\b(92abbcb90\|3f5fc95d\|d3e9c4d8\|…)…' *.md \| sort \| uniq -c` | 0 | `101 92abbcb9`, `35 d3e9c4d8`, `10 3f5fc95d`, `8 93b75888`, `1 ad34f06b` |
| V14 | `ls reports \| wc -l` at three HEADs | 0 | `92` → `97` → `99` |
| V15 | `git log --oneline 4d950cf..HEAD`, then `9ce39b4c..HEAD` | 0 | `9ce39b4c Campaign: eighth batch…`; `ce743d6a Campaign: ninth batch — W02e…, W06e…` |
| V16 | `date -u`; `git rev-parse HEAD`; `git status --porcelain`; `ls -la /tmp/claude-0/w24/` (end) | 0 | `Tue Sep  8 02:58:14 UTC 2026`; `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8`; *(empty)*; scratch dir **empty** |

**`PROPOSED (NOT RUN)` by me:** applying, testing or gating **any** repair in §1; running `scripts/preflight.sh`; running any pytest; reading the frozen corpus; opening any of the ~65 reports I only grepped; reading W02e or W06e.

---

## Limitations

- **This index is a map of claims, not a verification of them.** With the exceptions explicitly marked **DBW24** (§0, V5–V12, C11, C12), every exit code, negative control and measurement quoted here is **transcribed from a report body I did not re-execute**. A worker report is not a test result. Where I list exit-code counts (`23 exit markers`) that is a count of markers in the file, **not** a validation of them.
- **I did not read 65 of the 92 reports.** Any repair, decision, missing input or contradiction living only in a section my greps did not match is **absent from this index, and its absence is UNKNOWN, not evidence it does not exist.** The greps keyed on `repair|patch|fix|defect`, `owner`, `403|EGRESS_BLOCKED`, `missing input`, diff markers and repo file paths — a report phrasing any of these differently is invisible to me.
- **The corpus moved under me.** 7 reports were added during the run; 5 sampled, 2 not read. The index is a snapshot, already stale.
- **I did not read the frozen corpus.** Every corpus-based verdict (C4, C5, C7, C8, and the PENDING junction-source row) is **SECONDARY**, transcribed from W21/W21b/WAVE-LOG.
- **W13b/W13c/W15c/W16d exit codes were not read by me** — I read their patch bodies and section headings only. Those rows carry the reports' claims, tagged as such.
- **No clinical claim of any kind is made or implied here.** This index covers tooling, guards, provenance contracts and evidence routing. Nothing in it bears on EMC efficacy, safety, selectivity, therapeutic window or clinical readiness, and no computational result in the campaign could establish any of those. C13 is left explicitly unadjudicated for that reason.
- **I ranked nothing.** Row order is by target file. The one place I adjudicate (C11, C12) is arithmetic and byte-identity on committed data, shown in full.
- **Blocked routes are recorded, never probed.** I made zero network calls. Listing a blocked input is not a suggestion to retry it, and D17 is a coordinator question, not an authorization.

---

## Stop condition

**Set up front:** return the moment all four requested classes are indexed with per-row evidence class and `file:line` anchors, every two-reports-one-target case is flagged, and start/end provenance is recorded — at roughly 40 tool calls / 40 minutes, without padding.

**MET.** Four classes indexed: **26 repair rows** across 21 distinct targets, **20 routed decisions**, **~30 named missing inputs** split blocked / pending / nonexistent, **13 contradiction rows**. **Three two-reports-one-target flags** raised (`emc_fourth_cohort_quant.py` R07/R08 — a true either/or; `scripts/preflight.sh` R11/R12 plus W12b — three shapes; `emc_mortality_decomposition.py` R03/R04 — a sequencing requirement), plus two complementary-not-conflicting pairs called out as such (R01/R02, R16/R17). Two contradictions adjudicated on committed data with the arithmetic shown; the rest left to the owner. One superseded W23 line corrected from the wave log (R13 / D18). Returning immediately.

---

## Tool-call and wall-clock count actually used

**41 tool calls** (all `Bash`; every one a read, `grep`, `git` read-only command, or `python3 -c` read). **Wall clock 4 min 20 s** (`02:53:54Z` → `02:58:14Z`). Well inside the ~40-call / ~40-minute target; I stopped on the condition, not the budget.

---

## Next concrete action

**One successor, bounded, inside this lane and needing no missing input: index the ~65 reports this run only grepped.** Specifically — for each report not opened above, extract its `## Result` verdict line, its `## Stop condition` outcome (MET / NOT MET / BLOCKED), and its `## Next concrete action`, and fold them into §1–§4 as additional rows. My marker census (V4) already names the 30 reports most likely to carry unindexed material: the ones with ≥5 exit-code markers or ≥1 owner-routing hit that I did not open (`W03c`, `W03d`, `W05b`, `W05c`, `W07`, `W07c`, `W07d`, `W08`, `W08c`–`W08g`, `W09d`, `W11`, `W11d`, `W13d`, `W13e`, `W15`, `W15b`, `W15d`, `W16d`, `W17`, `W17b`, `W17d`, `W17f`, `W18`, `W19b`, `W20d`–`W20f`, `W22`). That is a mechanical completion of an index whose shape is now fixed, and it would close the honest gap named first under Limitations.

A second, smaller successor if the owner wants it separated: **re-check W13e's framing against the now-present `W13d-population-overlap-validator.md`** (C10) — W13e built on a report it could not read, said so, and that transfer limit is now removable.
