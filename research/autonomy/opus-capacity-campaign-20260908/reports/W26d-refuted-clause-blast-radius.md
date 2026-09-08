<!-- collected 2026-09-08T04:40:39Z by campaign coordinator; agent id af03ac3878b74b270; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-af03ac3878b74b270.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

## Worker

- **Worker:** W26d, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: successor to W26c — blast-radius measurement of W26c's 14 movable clauses in `systems/graph/*.json`.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model — `AI_AGENT=claude-code_2-1-263_agent` and `CLAUDE_CODE_VERSION=2.1.42` are harness versions. The coordinator must extract the runtime model from the transcript.
- **Re-dispatch note:** a previous W26d attempt was killed mid-run by a session rate limit and produced no report. This run started fresh; no state was inherited from it.
- **Write isolation honoured.** Nothing written, moved or deleted under `/home/user/Rare-cancers`; no git write operation; `--write-views` never run against the live tree; `scripts/preflight.sh` not run; no repair, patch, gate or test authored; no clause re-graded. All execution under `/tmp/claude-0/w26d/` and `/tmp/claude-0/w26dx/`, **both deleted before returning**.
- No network, no retrieval, no paid API, no GPU, no human contact, no publication. No clinical, efficacy, safety, selectivity or readiness claim; there is no wet lab.

`date -u` — start `Tue Sep  8 04:34:56 UTC 2026`, end `Tue Sep  8 04:37:32 UTC 2026`.
`git rev-parse HEAD` — start `408b676aec3625a36917755662516232a27a1278`, end `408b676aec3625a36917755662516232a27a1278` (HEAD did **not** move under me).
`git status --porcelain` — **0 lines at start, 0 lines at end.**

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (literal, long proxy lists elided as `…` and marked):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=…  [elided, proxy list]
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
GLOBAL_AGENT_NO_PROXY=…  [elided, proxy list]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=…  [elided, truststore + proxy flags]
NO_PROXY=…  [elided, proxy list]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=…  [elided, proxy list]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

---

## Question

**What does each of W26c's 14 movable clauses cost to land — how many committed view files and view lines does its source field reach — and which of them reach no view at all, and so cannot be caught by the view-drift guard?**

Open because W26c produced 14 verdict changes with restatements but explicitly filed blast radius as `PROPOSED (NOT RUN)`: *"W26b's radii cover only its own 16 fields and do not transfer to mine."* The lander therefore had 14 corrections with no cost, no reach, and no way to know which are gate-checkable.

---

## Prior-work check

Read in full before touching anything: `COMMON-BRIEF.md` (including the 03:36Z HEAD correction and the "Known, measured, and NOT worth rediscovering" section — the `systems_check` campaign-footprint baseline attribution and the two line-shifted files, `systems/systems_check.py` and `systems/views/L3-publications.md`), `CORPUS-CONTEXT.md`, `CLOSED-WORK.md`, `reports/W26c-unverifiable-clauses-against-corpus.md`, `reports/W26b-remaining-graph-files-sweep.md` (R.7 sentinel method, both controls, the clip table), and `systems/POLICY-evidence.md` before touching `systems/`.

- **Not replayed:** W26b's own 16 sentinels are not re-run except one deliberate overlap (`TECH-RECONSTRUCTED-IPD.not_scannable_because`) used as an **instrument-identity check** — my number must reproduce W26b's or my radii are not comparable to its. It does (see R.4). W26c's 14 grades are **not** re-graded; I take them as given and measure only cost. `reports/W25-*` — **not read, not referenced**. `publications.json` / `routes.json` — not touched.
- **Campaign reports are not repository evidence.** W26b's and W26c's reports supplied my *field list* only; every number below comes from a run I performed.
- Not re-measured (per the brief's "not worth rediscovering"): the campaign resolution rate, the `origin/literature-cache` question, the `pytest` interpreter trap, the `--check` ERROR baseline. My guard-reachability claim rests on my own sentinel measurement, not on any `--check` count.
- **The two line-shifted files are irrelevant to this unit**: I cite no `systems_check.py:NN` line and no `L3-publications.md` line. All line numbers I report were read from the **live checkout's** view snapshot I took myself, not from the corpus.

---

## Method / inputs

| input | role |
|---|---|
| `/home/user/Rare-cancers` @ `408b676a` (start = end) | tree under test, **read-only throughout** |
| `/tmp/claude-0/w26d/repo` | scratch copy, `tar --exclude=./.git --exclude=./results` (429 MB); every mutation happened here |
| `/tmp/claude-0/w26d/views-committed` | committed `systems/views/` snapshot, **111 files**, taken before any generator run |
| `systems/systems_check.py --write-views` | the generator actually run, on the scratch copy only |
| the 19 files in `systems/graph/` | restored pristine from the live tree before **and** after every case |
| `/tmp/claude-0/w26dx/harness.py`, `run.py` | the two scripts I wrote and ran |

Python 3.11 stdlib, Linux, no network. **Method is W26b's R.7 verbatim**: per case — restore all 19 graph files pristine from `/home/user/Rare-cancers`; substitute `ZZSENTINELZZ` for the whole field; re-serialize (`json.dump`, `indent=2, ensure_ascii=False`); regenerate; walk all 111 written view files **including `registers/`**; count sentinel occurrences and unified-diff ±lines against the pre-run snapshot; restore pristine; regenerate; **assert `RESTORE_NOOP` = zero changed view files AND `gen_exit=0`**. Both controls ran **first**.

**Field list — W26c's 14 clauses map to 13 distinct fields**, because its clauses #7 and #8 are the two halves of the *same* field, `ST-REPURPOSING.limitations[1]`. I sentinel whole fields, so that pair is one sentinel and shares one radius. To that I added a 14th sentinel, `TECH-RECONSTRUCTED-IPD.not_scannable_because` — the second field carrying W26c's R.5 finding, and W26b's overlap case.

---

## Result

### R.1 — Measured blast radius of W26c's 14 clauses `PRIMARY`

Ranked by reach. `gen_exit=0` and `RESTORE_NOOP=True` on **all 14**; terminal `ALL_RESTORED_OK`. "Committed lines consumed" = lines removed from the committed snapshot; "written" = lines the sentinel run produced.

| rank | W26c # | record · field | W26c grade | files touched | committed lines consumed | written | sentinel occ. | exit |
|---:|---|---|---|---:|---:|---:|---:|---|
| 1 | 7+8 | `strategies` `ST-REPURPOSING.limitations[1]` | FALSE ×2 | **12** | 12 | 12 | 12 | 0 |
| 2= | 10 | `strategies` `ST-MICROENV.limitations[2]` | FALSE | **5** | 5 | 5 | 5 | 0 |
| 2= | 11 | `strategies` `ST-LOCOREGIONAL.limitations[0]` | FALSE | **5** | 5 | 5 | 5 | 0 |
| 4 | 9 | `strategies` `ST-RADIOLIGAND.limitations[0]` | FALSE | **3** | 3 | 3 | 3 | 0 |
| 5= | 12 | `forecasts` `FC-RECONSTRUCTED-IPD.scenarios.conservative.rationale` | OVER-SCOPED | **1** | 1 | 1 | 1 | 0 |
| 5= | 13 | `technologies` `TECH-RECONSTRUCTED-IPD.evidence[1]` | OVER-SCOPED | **1** | 1 | 1 | 1 | 0 |
| 5= | 14 | `forecasts` `FC-FE-CRYPTIC-POCKET.scenarios.optimistic.rationale` | OVER-SCOPED | **1** | 1 | 1 | 1 | 0 |
| — | (R.5 partner) | `technologies` `TECH-RECONSTRUCTED-IPD.not_scannable_because` | (W26b OVER-SCOPED) | **1** | **3** | 1 | 1 | 0 |
| 8= | 1 | `modalities` `MOD-ARGININE-DEPRIVATION.requires[0]` | FALSE | **0** | 0 | 0 | 0 | 0 |
| 8= | 2 | `modalities` `MOD-PRMT5-MAT2A.requires[0]` | FALSE | **0** | 0 | 0 | 0 | 0 |
| 8= | 3 | `modalities` `MOD-PRMT5-MAT2A.rationale` | FALSE | **0** | 0 | 0 | 0 | 0 |
| 8= | 4 | `modalities` `MOD-MCL1-BCLXL.rationale` | FALSE | **0** | 0 | 0 | 0 | 0 |
| 8= | 5 | `modalities` `MOD-RET.rationale` | FALSE | **0** | 0 | 0 | 0 | 0 |
| 8= | 6 | `modalities` `MOD-TF-LBD-OCCUPANCY.rationale` | FALSE | **0** | 0 | 0 | 0 | 0 |

Per-file destinations, with committed line numbers read from the snapshot (`L1-*`/`L2-*` are at repo root of `systems/views/`):

- `ST-REPURPOSING.limitations[1]` → `L1-st-repurposing.md:30`, `L2-rt-6mp.md:103`, `L2-rt-alk-hit.md:125`, `L2-rt-carfilzomib.md:122`, `L2-rt-hdac-bet.md:100`, `L2-rt-hormone-partner.md:114`, `L2-rt-partner-strat.md:133`, `L2-rt-pparg-downstream.md:128`, `L2-rt-ret.md:123`, `L2-rt-rxr.md:86`, `L2-rt-trabectedin-pparg.md:137`, `L2-rt-trabectedin.md:129`
- `ST-MICROENV.limitations[2]` → `L1-st-microenv.md:31`, `L2-rt-hypoxia-prodrug.md:113`, `L2-rt-immunocytokine.md:118`, `L2-rt-matrix-address.md:120`, `L2-rt-matrix-synthesis.md:112`
- `ST-LOCOREGIONAL.limitations[0]` → `L1-st-locoregional.md:29`, `L2-rt-limb-perfusion.md:107`, `L2-rt-lung-directed.md:106`, `L2-rt-mdt-lung.md:99`, `L2-rt-rt-intensify.md:109`
- `ST-RADIOLIGAND.limitations[0]` → `L1-st-radioligand.md:29`, `L2-rt-fap-rlt.md:137`, `L2-rt-sstr2.md:142`
- `FC-FE-CRYPTIC-POCKET…optimistic.rationale` → `registers/technologies.md:117`; `TECH-RECONSTRUCTED-IPD.evidence[1]` → `registers/technologies.md:169`; `FC-RECONSTRUCTED-IPD…conservative.rationale` → `registers/technologies.md:178`; `TECH-RECONSTRUCTED-IPD.not_scannable_because` → `registers/technologies.md:188`

**Total for a complete landing of all 14 clauses: 13 source fields → 29 committed view lines across 23 view files.** ⚠ Every W26c restatement is *longer* than what it replaces, so lines below each edit renumber; the lander must regenerate and re-diff rather than reuse these numbers.

### R.2 — ⭐ Which of the 14 render at all, and which are invisible to the drift guard `PRIMARY`

**Six of W26c's 14 clauses have a blast radius of exactly ZERO — and all six are FALSE clauses**, the class most worth correcting.

| reach class | n / 14 clauses | which |
|---|---:|---|
| renders into views (gate-checkable) | **8** | the 4 `strategies.json` clauses (counting #7 and #8 separately), the 3 `forecasts`/`technologies` register clauses, plus the R.5 partner field |
| **renders nowhere — invisible to `--check`** | **6** | all six `modalities.json` clauses: #1 `MOD-ARGININE-DEPRIVATION.requires[0]`, #2 `MOD-PRMT5-MAT2A.requires[0]`, #3 `MOD-PRMT5-MAT2A.rationale`, #4 `MOD-MCL1-BCLXL.rationale`, #5 `MOD-RET.rationale`, #6 `MOD-TF-LBD-OCCUPANCY.rationale` |

⚠ **Consequence, and it is the same one W26b named, now measured on a different field set.** `systems_check.py --check` re-renders the views and compares; prose that reaches no view is prose no re-render can check. **Six FALSE clauses — including all eight of W26c's refutations that rest on `census-route-expression-grading.json` in `modalities.json` — are outside the reach of the whole view-diff mechanism. They need a human reviewer, not a gate.** No gate change is proposed here; I am reporting a reach measurement.

**Why the zero is structural, not accidental** (measured, so the lander does not have to re-derive it): all five sentinelled `modalities` records carry a `route` — `MOD-RET` → `RT-RET`, `MOD-PRMT5-MAT2A` → `RT-MTAP-PRMT5`, `MOD-ARGININE-DEPRIVATION` → `RT-ARGININE`, `MOD-MCL1-BCLXL` → `RT-APOPTOSIS-DEP`, `MOD-TF-LBD-OCCUPANCY` → `RT-MONOVALENT` — and the census renderer's `rationale` row is gated on the row *not* having a route (W26b's R.7 clip table records the same gating for `MOD-RET` and `MOD-MCL1-BCLXL`). Separately, `grep -n '"requires"' systems/systems_check.py` returns **no hits at all**: the `requires` array is never read by the generator, so clauses #1 and #2 are dead to the view layer by field name, independent of any route gating. **This is not the 150-character clip.** The clip cannot fire on a field that is never rendered; my six zeros are non-rendering, not truncation.

### R.3 — ⛔ W26c's "5–8 view pages per `strategies.json` `limitations[n]`" is REFUTED by measurement `PRIMARY`

W26c's Next-concrete-action says `ST-RADIOLIGAND.limitations[0]` and `ST-REPURPOSING.limitations[1]` should land first *because* a `strategies.json` `limitations[n]` fans out to 5–8 view pages. That range was W26b's, measured on two **different** fields (`ST-PROXIMITY` = 8, `ST-OCCUPANCY` = 5), and W26c inherited it rather than measuring. Measured on W26c's own four fields, the range is **3 to 12**, and both of its named clauses fall outside 5–8:

| field | W26c inherited | **W26d measured** | verdict on the inherited figure |
|---|---:|---:|---|
| `ST-REPURPOSING.limitations[1]` | 5–8 | **12** | ⛔ **understated by 50–140%** — this is the widest field in W26c's whole set, wider than W26b's widest (`ST-PROXIMITY`, 8) |
| `ST-RADIOLIGAND.limitations[0]` | 5–8 | **3** | ⛔ **overstated** — the *narrowest* rendering field in W26c's set |
| `ST-MICROENV.limitations[2]` | (not named) | 5 | inside the range |
| `ST-LOCOREGIONAL.limitations[0]` | (not named) | 5 | inside the range |

⭐ **The generalisation "a `strategies.json` `limitations[n]` costs 5–8 pages" does not hold; fan-out tracks the size of the route family the strategy owns, not the file.** `ST-REPURPOSING` owns 11 `L2-rt-*` route pages, `ST-RADIOLIGAND` owns 2.

**Effect on the priority W26c gave the lander:** the *ordering* it proposed is wrong on its own criterion, but the *pairing* survives for a different reason. On reach alone, `ST-REPURPOSING.limitations[1]` (12 pages) outranks `ST-RADIOLIGAND.limitations[0]` (3) by 4×, and `ST-MICROENV` and `ST-LOCOREGIONAL` (5 each) also outrank `ST-RADIOLIGAND`. `ST-RADIOLIGAND` is the **narrowest** of the four, not a co-equal widest. What is *not* refuted is W26c's structural point: all four `strategies.json` clauses do reprint verbatim on every route page in their family, so a false absence there is re-presented as if independently confirmed on each — measured at **12, 5, 5 and 3 pages** rather than 5–8. ⚠ Reach is a cost/exposure measure only; it is not a scientific ranking, and it does not touch W26c's grades, which I did not re-open.

### R.4 — The R.5 stale-watcher field, and an instrument-identity check `PRIMARY`

W26c's R.5 finding — `TECH-RECONSTRUCTED-IPD` says `curves_supplied` *"is 0 today"* while `emc-ipd-survival.json` says `1` — sits in **two** fields, and both were measured:

| field carrying R.5 | files touched | committed lines consumed | written | note |
|---|---:|---:|---:|---|
| `evidence[1]` (the *"computes over an empty CURVES table"* sentence) | 1 — `registers/technologies.md:169` | 1 | 1 | renders in full on one line |
| `not_scannable_because` (the *"which is 0 today"* sentence) | 1 — `registers/technologies.md:188` | **3** | 1 | field is 962 chars and **wraps across three committed lines** |

⭐ **The whole R.5 defect costs 2 fields → 4 committed lines in 1 file.** That is the smallest reach of any multi-clause item in this set — and it is exactly the profile that makes a stale watcher dangerous. A number that is wrong reaches one register page; the artifact it contradicts (`research/modalities/emc-ipd-survival.json`) is **not** an input to the view layer at all, so **no regeneration and no `--check` can ever compare the two.** The guard would confirm that `registers/technologies.md` faithfully reprints a stale `0`. W26c is right that this needs a reader rather than a gate, and the measurement is the reason: **the drift guard's fixed point is "the view matches the graph", never "the graph matches the artifact it cites."** I am reporting this; I propose no gate, test or repair.

⚙ **Instrument-identity check.** `not_scannable_because` is the one field W26b also sentinelled. W26b: 1 file, `registers/technologies.md:188`, **3 committed lines consumed for 1 written**, occ 1. W26d: identical on every number and the same line. **The instrument reproduces, so my radii are comparable to W26b's on the same scale** — which is what makes the R.3 comparison against W26b's 5–8 legitimate rather than a units mismatch.

### R.5 — Sentinel radius vs clause-level radius `PRIMARY`

W26b warned that in `modalities.json` sentinel radius ≠ clause-level radius, because the 150-char clip can cut an offending clause out of a line the sentinel still touches. **In W26c's set that divergence does not arise**, and I measured rather than assumed it: a verbatim search of the full field value across all 111 committed views returns exactly the sentinel count for **every** field with a nonzero radius (12, 5, 5, 3, 1, 1, 1). No clip, no truncation, one full-value render per page.

The single exception is `not_scannable_because`, where the full value matches **0** lines while its first 70 characters match 1 — because the value wraps across three lines. That is a line-wrap artefact, not a clip.

**So for the lander: across all of W26c's 14 clauses, sentinel radius = clause-level radius exactly.** The six `modalities.json` zeros are zero at *both* levels — the field never renders, so no clause inside it can. A clause-level fix in those six touches zero view lines.

---

## Validation evidence

Environment for every run: scratch copy at `/tmp/claude-0/w26d/repo`, produced by `tar --exclude=./.git --exclude=./results -cf - . | tar -xf - -C …` from `/home/user/Rare-cancers` (429 MB; `results/` excluded for disk, exactly as W26b did — Control 1 below is byte-clean, which is the justification). Committed views snapshotted to `/tmp/claude-0/w26d/views-committed` (**111 files**) before any generator run. Linux, Python 3.11 stdlib, no network. `df` showed 20 GiB free; no `ENOSPC`.

### `RUN` — Control 1: regeneration with no edit is a no-op (run FIRST, before any sentinel)
```
CONTROL1_GEN_EXIT=0 | systems_check: wrote 111 view(s) to systems/views/
CONTROL1 changed_view_files=0 +0/-0 sentinel_occ=0
changed: []
```

### `RUN` — Control 2: re-serializing the JSON alone changes no view
This is the control that makes every radius above *attributable to the text* and not to the serializer. All four files I would later sentinel were `json.load`-ed and re-dumped with `indent=2, ensure_ascii=False`, no content change, then regenerated:
```
CONTROL2_RESERIALIZE files=['modalities.json', 'strategies.json', 'forecasts.json', 'technologies.json']
  gen_exit=0 stdout='systems_check: wrote 111 view(s) to systems/views/'
  changed_view_files=0 +0/-0 sentinel_occ=0
CONTROL2_RESTORE gen_exit=0 changed_view_files=0 (expect 0)
```

### `RUN` — Field-path resolution (before any mutation)
All 14 field paths resolved in the live graph; each printed `OK <file> <record> <spec> len=<n>` with the leading text of the value. `MOD-TF-LBD-OCCUPANCY` has **no** `requires` key (I sentinelled its `rationale`, which is what W26c graded). No `MISSING RECORD` / `MISSING FIELD` lines.

### `RUN` — Fourteen whole-field sentinels
Every case: `gen_exit=0`, stdout `systems_check: wrote 111 view(s) to systems/views/`, followed by `RESTORE_NOOP=True (gen_exit=0 changed=0)`. Terminal line **`ALL_RESTORED_OK`**. Representative cases, verbatim:
```
=== strategies ST-REPURPOSING.limitations.1
   gen_exit=0 stdout='systems_check: wrote 111 view(s) to systems/views/' field_len=157
   files_touched=12  committed_lines_consumed=12  written_lines=12  sentinel_occ=12
   RESTORE_NOOP=True (gen_exit=0 changed=0)
=== strategies ST-RADIOLIGAND.limitations.0
   files_touched=3  committed_lines_consumed=3  written_lines=3  sentinel_occ=3
=== modalities MOD-RET.rationale
   gen_exit=0 ... field_len=693
   files_touched=0  committed_lines_consumed=0  written_lines=0  sentinel_occ=0
=== technologies TECH-RECONSTRUCTED-IPD.not_scannable_because
   files_touched=1  committed_lines_consumed=3  written_lines=1  sentinel_occ=1
     - registers/technologies.md  -3/+1 occ=1
ALL_RESTORED_OK
```

### `RUN` — Clause-level verbatim render check (the clip question)
Full-value and head-70 searches across all 111 committed views:
```
modalities  MOD-ARGININE-DEPRIVATION requires.0    head70_hits=0 full_hits=0
modalities  MOD-PRMT5-MAT2A          requires.0    head70_hits=0 full_hits=0
modalities  MOD-PRMT5-MAT2A          rationale     head70_hits=0 full_hits=0
modalities  MOD-MCL1-BCLXL           rationale     head70_hits=0 full_hits=0
modalities  MOD-RET                  rationale     head70_hits=0 full_hits=0
modalities  MOD-TF-LBD-OCCUPANCY     rationale     head70_hits=0 full_hits=0
strategies  ST-REPURPOSING           limitations.1 head70_hits=12 full_hits=12
strategies  ST-RADIOLIGAND           limitations.0 head70_hits=3  full_hits=3
strategies  ST-MICROENV              limitations.2 head70_hits=5  full_hits=5
strategies  ST-LOCOREGIONAL          limitations.0 head70_hits=5  full_hits=5
forecasts   FC-RECONSTRUCTED-IPD     …conservative head70_hits=1  full_hits=1
technologies TECH-RECONSTRUCTED-IPD  evidence.1    head70_hits=1  full_hits=1
forecasts   FC-FE-CRYPTIC-POCKET     …optimistic   head70_hits=1  full_hits=1
technologies TECH-RECONSTRUCTED-IPD  not_scannable_because head70_hits=1 full_hits=0
```

### `RUN` — Why the six zeros are structural
```
$ grep -n '"requires"' systems/systems_check.py     # no output — requires is never read by the generator
MOD-RET                  route='RT-RET'
MOD-PRMT5-MAT2A          route='RT-MTAP-PRMT5'
MOD-ARGININE-DEPRIVATION route='RT-ARGININE'
MOD-MCL1-BCLXL           route='RT-APOPTOSIS-DEP'
MOD-TF-LBD-OCCUPANCY     route='RT-MONOVALENT'   (no 'requires' key)
```

### `RUN` — Write isolation and cleanup
```
$ git status --porcelain | wc -l          # 0 at start, 0 at end
$ git rev-parse HEAD                      # 408b676a at start AND end (HEAD did not move)
$ diff -rq systems/views /tmp/claude-0/w26d/views-committed   # VIEWS_UNCHANGED_SINCE_SNAPSHOT
$ cmp systems/graph/{modalities,strategies,forecasts,technologies}.json  <scratch copies>
modalities IDENTICAL  strategies IDENTICAL  forecasts IDENTICAL  technologies IDENTICAL
$ rm -rf /tmp/claude-0/w26d /tmp/claude-0/w26dx && ls -d /tmp/claude-0/w26d /tmp/claude-0/w26dx
ls: cannot access '/tmp/claude-0/w26d': No such file or directory
ls: cannot access '/tmp/claude-0/w26dx': No such file or directory
```

### `PROPOSED (NOT RUN)`
- Landing any of W26c's 14 restatements. **Nothing applied**, per dispatch and the brief.
- Any gate, test, guard or repair for the six zero-radius clauses or the stale-watcher defect. **Not authored, not proposed as code.** I report the reach; the disposition is not mine.
- `systems/systems_check.py --check` in any form, and `scripts/preflight.sh`. Not run.
- Radii for W26c's 16 still-UNVERIFIABLE clauses. Out of scope for this unit.

---

## Limitations

- **These radii are valid for HEAD `408b676a` only**, and go stale the moment any of these fields, the route families, or the generator changes. HEAD did not move during my run, which is why start and end match.
- **A sentinel measures the *field's* reach, not the restatement's diff size.** Every W26c restatement is longer than what it replaces, so the actual landed diff will differ in line content and will renumber every line below each edit. The lander must regenerate and re-diff; my line numbers are for locating, not for patching.
- **Reach is exposure, not importance.** A 12-page clause is not more wrong than a 0-page one — the six zero-radius clauses are all graded FALSE, the strongest grade in the set. Ranking by reach answers "what does it cost and can a gate see it", nothing more.
- **"Invisible to the view-drift guard" is a claim about `--check`'s re-render mechanism as I measured it via `--write-views`, not a claim that no check anywhere covers these fields.** I did not run `--check`, and I did not audit `systems/tests/` for an independent assertion over `modalities.json`. Whether some other check reads these fields is **UNKNOWN**, not zero.
- **`results/` was excluded from the scratch copy** (as W26b did). Both controls came back byte-clean, so nothing under `results/` participates in view generation — but I did not prove that independently of the controls.
- **The R.3 refutation is of an inherited generalisation, not of W26c's grades.** W26c's 11 FALSE / 3 OVER-SCOPED verdicts are untouched here; I measured cost only, and nothing above bears on whether any clause is true.
- **I did not verify W26c's evidence.** Whether `census-route-expression-grading.json` refutes what W26c says it refutes is W26c's finding, carried forward unverified by me.
- **No clinical claim.** Nothing here concerns EMC efficacy, safety, selectivity or clinical readiness; every number is a count of lines in generated Markdown. There is no wet lab.

---

## Stop condition

**Set up front:** return the moment (a) both W26b controls have run clean *before* any sentinel, (b) every one of W26c's 14 clauses has a measured radius from a run with `gen_exit=0` and an asserted `RESTORE_NOOP`, (c) the zero-radius set is identified and the reason for the zero is measured rather than assumed, and (d) W26c's inherited "5–8 pages" claim is confirmed or refuted by my own measurement — or at ~40 tool calls / ~40 minutes, whichever came first.

**MET, well inside budget, on all four legs.** Both controls byte-clean and run first; 14/14 sentinels at `gen_exit=0` with `RESTORE_NOOP=True` and terminal `ALL_RESTORED_OK`; 6 zero-radius clauses identified with the route-gating and never-read-`requires` mechanism measured; the 5–8 claim refuted in both directions (12 and 3). Live tree byte-identical at start and end; scratch deleted.

---

## Tool-call and wall-clock count actually used

**14 tool calls** (target ~40). **Wall clock 2 min 36 s by the UTC clock** — `date -u` start `04:34:56Z`, end `04:37:32Z` (target ~40 min); real elapsed session time including model latency was longer, and I report the clock bracket rather than an estimate. The saving is W26b's and W26c's: W26b's R.7 supplied the harness design and both controls, W26c supplied the field list, so no instrument-building or clause-enumeration phase was needed. I record that so the coordinator does not read the speed as reduced scope.

---

## Next concrete action

**Re-order W26c's landing queue by measured reach, and land `strategies.json` `ST-REPURPOSING.limitations[1]` first — 12 view pages, the widest field measured anywhere in the W26b/W26c/W26d set, wider than W26b's own headline `ST-PROXIMITY` at 8.** It is one field carrying *two* of W26c's FALSE clauses (its #7 and #8), so a single edit retires two refuted absences at once, and its false claim — that a direction of effect *"has never been read in EMC tissue"* — is currently reprinted verbatim on eleven `L2-rt-*` route pages where a reader will take each as an independent confirmation. It is fully gate-checkable: sentinel radius = clause-level radius, one full-value render per page, no clip.

**Two things the lander must be told, both measured here:**
1. **`ST-RADIOLIGAND.limitations[0]` is the narrowest of the four `strategies.json` clauses (3 pages), not a co-equal widest.** Its case for landing early is scientific — W26c's restatement replaces an unmeasured gap with a measured null — not one of reach. State it that way rather than on the refuted 5–8 figure.
2. **Six of the fourteen — every `modalities.json` clause, all graded FALSE — reach no view and cannot be caught by re-rendering.** They need a named human reviewer at land time. No gate is proposed for them here, and none should be invented to make them look covered.

An honest successor for this lane exists but is narrow: **measure the radius of W26c's 16 still-UNVERIFIABLE clauses**, so that if any is later moved the cost is already known. It is the same harness with a different field list and would cost well under the budget. If the coordinator judges that premature — measuring the cost of corrections nobody can yet justify — then there is no further blast-radius work in this lane, and the remaining question (does any `systems/tests/` assertion cover the six unrendered `modalities.json` fields?) belongs to whoever owns `systems/tests/`, not here.
