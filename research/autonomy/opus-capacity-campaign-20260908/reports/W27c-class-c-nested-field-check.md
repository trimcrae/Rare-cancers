<!-- collected 2026-09-08T03:51:46Z by campaign coordinator; agent id ab2d9b95514b685ee; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-ab2d9b95514b685ee.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W27c** · OPUS-CAPACITY-CAMPAIGN-20260908 · tooling audit lane, successor to W27b.

**Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). Nothing in this container's environment names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` **start**: `Tue Sep  8 03:40:28 UTC 2026` · **end**: `Tue Sep  8 03:48:05 UTC 2026` (report drafting after).

`git rev-parse HEAD` **start**: `5ae0fa04ff9516ac8f820381079d644a094f4a77` · **end**: `e5d60db79f9dcbe7a4b2e6b0db1de6e32ccf69e7`. **HEAD moved under me** (the coordinator collecting reports). I checked the exposure rather than assuming it: `git diff --name-only 5ae0fa04..HEAD -- research/modalities research/manuscripts` → **0 files**; and against W27b's own start commit, `git diff --name-only ff6bb018..HEAD -- research/modalities research/manuscripts` → **0 files**. No module or artifact W27b or I measured has changed across either run.

`git status --porcelain` **start**: `0` lines · **end**: `0` lines. I wrote nothing into the Git tree and ran no git write operation. All execution under `/tmp/claude-0/w27c/` with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPYCACHEPREFIX=/tmp/claude-0/w27c/pyc`. **Scratch deleted** (`rm -rf /tmp/claude-0/w27c`; `ls` → "No such file or directory"). I did not run `scripts/preflight.sh`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (the four long proxy variables — `no_proxy`, `NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — are verbatim in the transcript, contain no model information, and are marked below; nothing else is altered):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=<proxy list, no model information>
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
GLOBAL_AGENT_NO_PROXY=<proxy list, no model information>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<truststore + proxy flags, no model information>
NO_PROXY=<proxy list, no model information>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<proxy list, no model information>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

I read the corrected `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md` and `CLOSED-WORK.md` in full, and the stray `EOF_MARKER_REPLACED_BELOW` line in my dispatch is ignored. I did not read, audit or reference any `W25-*` report.

---

## Stop condition (set before any measurement)

**Stop when: (1) a sampling rule over W27b's 90 Class C modules is stated and executed, with the untested remainder named; (2) every sampled module's comparison is read from its own source, at `file:line`, and its `--check` write-safety confirmed in source BEFORE any run; (3) at least four sampled modules are demonstrated by mutating a DEEPLY NESTED leaf of the committed artifact on a scratch copy, with the module's own real `--check` exit code recorded, restored between mutations and the scratch verified restored at the end; (4) the split is reported with an explicit denominator — sampled / source-read only / mutation-demonstrated / Class C surviving; (5) no repair authored, no guard weakened, no Class A or Class B re-audited, and the two refused writing modules plus `emc_sra_study.py` not run.**

**MET.** All five. (3) exceeded — **twelve mutation runs over ten distinct modules**, all with real recorded exit codes. Returning immediately.

---

## Question

W27b's census (90 Class C / 22 B / 11 A / 6 F of 129) rests on an assertion it explicitly limited: *"Class C is asserted at the top level only… I make no claim about a `derive()` that silently drops a nested field inside a compared key."* Class C is 69.8 % of the surface and the entire basis for calling the gap class a minority.

**Question pursued: does W27b's Class C hold at depth — i.e. for how many of the 90 does `--check` fail to notice a mutation to a leaf *below* the top level of the committed artifact?**

---

## Prior-work check

| Command | What it showed |
|---|---|
| Read in full: `reports/W27b-class-d-and-e-census.md`, head of `reports/W27-drift-gate-hash-census.md`, corrected `COMMON-BRIEF.md`, `CORPUS-CONTEXT.md`, `CLOSED-WORK.md` | W27b's Result names Class A (11), B (22) and F (6) individually but **does not enumerate the 90 Class C modules**. I therefore took Class C as the *complement* of its 39 named modules within its own 129-module `checkpaths.json` key set — this reproduces **exactly 90**, confirming I am working on W27b's set and not re-deriving its classification. |
| `rg -n -i "mutation test\|mutant\|nested mutation" --glob '!.git' --glob '!research/autonomy/opus-capacity-campaign-20260908/**'` | No repository prior art on mutation-testing `--check` gates. Hits are biological ("NBRE mutant", "permutation test"), not gate testing. |
| `git ls-files \| rg -i "mutat"` | `research/manuscripts/tests/mutate_fusion_partner_guard.py`, `research/manuscripts/tests/mutate_round7_bindings.py`, `research/modalities/pmx_mutation_reference.py`. Two mutation harnesses exist for **specific named guards**; **none covers the `--check` gate surface**, and none of the modules I mutated is their target. My axis is new; the technique is not. |
| Fidelity re-read (below, Validation §1) | W27b's `/tmp/claude-0/w27b/checkpaths.json` is a faithful, line-anchored extraction of the live source: **5,528 quoted lines re-read from the live files at my HEAD, 0 mismatches**. Reading it therefore *is* reading source. |

**CLOSED-WORK items confirmed not replayed**: no NR4A Perspective, no Brenca/Hofvander/Pazopanib/Sunitinib/Wagner/CTARC route, no GSE4303/GSE28866 re-reading, no registry ICD-O work, no source fetch, no patient or specimen work. **No network request was initiated.** I did not read or reference W25. The frozen corpus at `/tmp/claude-0/frozen-corpus/extracted/corpus/` was not needed: every claim is about code and artifacts at the recorded live HEADs. No content-policy refusal was encountered.

**Refusals respected, exactly as instructed**: `emc_fourth_cohort_quant.py` (writes at `:928`) and `nr4a3_linker_library_canonical.py` (unconditional write at `:851-852`) were **NOT RUN**; `emc_sra_study.py --check` was **NOT RUN** (network on a cold cache). All three are Class B/A findings of W27b and I did not touch them.

---

## Method / inputs

**Inputs.** W27b's 90 Class C modules and their committed JSON artifacts, at HEAD `5ae0fa04` / `e5d60db7`.

**Tools.** Python 3.11 stdlib only (`json`, `re`, `os`, `subprocess`, `shutil`), `git`, `grep`, `sed`, `tar`, `diff`, `cmp`. No third-party package, no network, no GPU, no paid API.

### Sampling rule (stated up front, then executed)

I did **not** sample uniformly. Nested gaps are not uniformly distributed; they live in the shape of the comparison expression. So:

1. **Full-population shape triage (n = 90, 100 %).** For every Class C module I read its comparison expression from source and assigned a *shape stratum*. No module was skipped at this level.
2. **Full check-block source read (n = 32, 100 % of the at-risk strata).** Every module in strata T2, T3 and T4 — the strata where an exclusion, a canonicalizer or an asymmetric loop could hide depth — had its complete `--check` block *and* its strip/canonicalize helper read at `file:line`. Four T2 candidates were **reclassified to T1** on that read (my regex had caught build-code, not comparison-code); one T1 module (`emc_cohort_search.py`) was **promoted to T2** by a separate recursive-helper sweep.
3. **Mutation demonstration (n = 10 distinct modules, 12 runs).** Chosen to cover **all four strata**, in both directions: modules predicted to stay green *and* modules predicted to go red, so the harness proves itself rather than only confirming a hypothesis.

**What I did not test.** I did **not** run 80 of the 90. For the 61 T1 (plain whole-object or whole-text equality) modules I read the comparison but mutation-tested only four; their depth-completeness is a **source finding, not a measurement**, resting on the fact that Python `!=` on `dict`/`list` is deep and on four confirming demonstrations. I did not enumerate every artifact's nested key space. I did not test any Class A, B or F module — those are W27b's and are done.

**Write-hazard inspection in source BEFORE running anything — done for every module I ran.**

| Module | What I read in source | Ran? |
|---|---|---|
| `emc_fet_idr_census.py` | check block `:670-677` returns; the only write is `:679`, after it | **RAN** |
| `emc_fet_construct_designs.py` | check `:995-1002` returns before the write at `:1004`. **Conditional hazard**: if `INPUTS` is absent, `:988` writes `OUT` and returns 1 — I verified `emc-construct-inputs.json` exists (87,259 bytes) before running, and passed neither `--refresh` nor any flag that reaches `urllib` (`:258`) | **RAN** (INPUTS present, no fetch) |
| `nr4a3_fusion_targets_occupancy.py` | check `:385-395` returns; write at `:396-398`; no `urllib`, no `subprocess` | **RAN** |
| `steric_carrier_audit.py` | check `:883-893` returns; writes at `:894-897` | **RAN** |
| `aso_control_oligos.py` | check `:150-155` returns; write at `:157` | **RAN** |
| `cd248_precedent.py` | check `:441-448` returns; write at `:449`. Uses `git show` (`:302`) — a **read-only** git operation | **RAN** |
| `nr4a3_fusion_targets_robustness.py` | check `:416-426` returns; write at `:427-429` | **RAN** |
| `aso_parent_gap_pairing.py` | check returns before write at `:292` | **RAN** |
| `emc_fourth_cohort_route_readout.py` | check returns before write at `:245` | **RAN** |
| `decoy_null_provenance.py` | check returns before write at `:137` | **RAN** |
| `emc_fourth_cohort_quant.py`, `nr4a3_linker_library_canonical.py`, `emc_sra_study.py` | W27b's findings re-read, not re-derived | **NOT RUN — refusals respected** |

**Scratch copy.** `tar -cf - --exclude=./.git . | (cd /tmp/claude-0/w27c/scratch && tar -xf -)` → **613 MB**, my own, not W27b's. Every `--check` executed with `cwd=/tmp/claude-0/w27c/scratch`, never in `/home/user/Rare-cancers`. Each artifact restored from the live tree **before and after** every mutation.

---

## Result

### R1 — Shape strata over all 90 Class C modules (`PRIMARY`, source)

| Stratum | n | Comparison shape | Depth behaviour |
|---|---|---|---|
| **T1 — whole-object / whole-text equality** | **61** | `cur != new`, `committed == fresh`, `json.load(fh) != doc`, `open(OUT).read() != text` | **Deep by construction.** Python `!=` on dict/list recurses. |
| **T2 — whole-object equality minus a named field** | **20** | `_strip_volatile`, `_canon`, `.pop("_generated")`, `{k:v … if k != "generated_utc"}` | Deep **except** the named field. **16 strip a top-level stamp only** (permitted by W27b's own Class C definition); **4 reach below the top level — see R2**. |
| **T3 — one-directional top-level key loop** | **7** | `drift = [k for k in res if old.get(k) != res[k]]` | **Deep within every key of the derivation**, but an artifact key *absent from the derivation* is never examined; 2 of the 7 additionally skip a named key outright. |
| **T4 — bidirectional key loop** | **2** | as T3 plus `drift += [k for k in old if k not in res]` | **Complete**, both directions, deep. |
| | **90** | | |

### R2 — The six modules where Class C does not hold at the top level as stated (`PRIMARY`)

| # | Module and `file:line` | What is ungated, and at what depth | Kind |
|---|---|---|---|
| 1 | `research/modalities/emc_fet_idr_census.py:675` | `drift = [k for k in result if k != "_limits" and …]` — the **entire `_limits` subtree, at every depth**, is excluded. `_limits` is a prose limitations block, **not** a volatile stamp. | **Really Class B** — demonstrated, D7 |
| 2 | `research/modalities/emc_fet_construct_designs.py:1000` | Identical idiom, identical `_limits` exclusion. | **Really Class B** — D1 (confounded, see below) |
| 3 | `research/modalities/nr4a3_fusion_targets_occupancy.py:371-376` | `_strip` is **recursive**: `{k: _strip(v) for k, v in o.items() if k != "generated_utc"}` — a `generated_utc` key at *any* nesting depth is dropped from both sides. | Nested exclusion, **volatile stamp** — demonstrated, D12 |
| 4 | `research/modalities/nr4a3_fusion_targets_confounds.py:728-733` | Byte-identical recursive `_strip_volatile` on `generated_utc`. | Nested exclusion, volatile stamp — source only |
| 5 | `research/modalities/emc_cohort_search.py:552-556` | Recursive `_strip` on `("generated_utc", "_generated_utc")`. Found by a dedicated recursive-helper sweep after my first regex missed it (`k not in (…)` rather than `k != "…"`). | Nested exclusion, volatile stamp — source only |
| 6 | `research/modalities/steric_carrier_audit.py:874-876` | `out.get("_generated", {}).pop("date", None)` — a **depth-2** leaf inside a compared top-level key. Carries a 10-line written rationale at `:862-873` explaining exactly why. | Nested exclusion, volatile stamp — demonstrated, D2 |

Plus a **separate, non-nested** caveat on all **7 T3** modules: the loop iterates the *derivation's* keys, so a top-level key present in the committed artifact but absent from the fresh derivation is never compared. That is a top-level asymmetry, inside W27b's stated scope, and it qualifies its "compares every top-level key" wording for those 7 — but 2 of the 7 (`emc_prmt5_effect_sizes.py:572`, `emc_mtap_locus_persample.py:482` are the T4 pair that closes it; the other 5 do not).

### R3 — The mutation demonstrations: 12 runs, 10 modules, real exit codes (`PRIMARY`, RUN)

Environment: Linux 6.18.44-fc-v24 x86_64, container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, system `python3` 3.11, `cwd=/tmp/claude-0/w27c/scratch`, `PYTHONDONTWRITEBYTECODE=1`, no network. Exit codes are `subprocess.CompletedProcess.returncode` **of the module itself**. "Leaf" = a scalar chosen by a deepest-first walk of the committed artifact.

**Decisive demonstrations — green baseline, so the mutated exit code means something (9 runs, 7 modules):**

```
D7  emc_fet_idr_census.py            T3, leaf _limits[0]                          depth 2
      BASELINE exit=0  REPRODUCES
      MUTATED  exit=0  REPRODUCES
      VERDICT: STAYS GREEN — nested gap CONFIRMED      restored=True

D8  emc_fet_idr_census.py            SAME MODULE control, leaf inside a COMPARED key
      path ['positive_controls', 'EWSR1::FLI1 (Ewing, type 1 …)', 'types', 0,
            'retained_segment_composition', 'span', 0]                            depth 7
      BASELINE exit=0  REPRODUCES
      MUTATED  exit=1  DRIFT in: ['positive_controls']
      VERDICT: GOES RED — gate catches it at depth 7   restored=True

D2  steric_carrier_audit.py          T2, leaf _generated.date                     depth 2
      BASELINE exit=0  ✅ reproduces (… committed stamp 2026-08-06 …)
      MUTATED  exit=0  ✅ reproduces (… committed stamp 1999-01-01 …)
      VERDICT: STAYS GREEN — nested gap CONFIRMED      restored=True

D12 nr4a3_fusion_targets_occupancy.py  T2 recursive _strip; INSERTED a nested
      per_peakset['REMAP2022_NR4A1'].generated_utc = 'W27c-NESTED-INJECTED-2099-…'
      BASELINE exit=0  occupancy --check: OK
      MUTATED  exit=0  occupancy --check: OK
      VERDICT: STAYS GREEN — recursive-strip nested gap CONFIRMED   restored=True

D3  nr4a3_fusion_targets_occupancy.py  SAME MODULE control, ordinary deep leaf
      path ['per_peakset','REMAP2022_NR4A1','genes','ENO3','empirical_p_vs_panel'] depth 5
      BASELINE exit=0 OK   MUTATED exit=1 DRIFT      GOES RED       restored=True

D6  nr4a3_fusion_targets_robustness.py  T2 top-level strip only
      path ['rows',0,'jackknife_leave_one_emc_out','per_fit',0,'delta']            depth 6
      BASELINE exit=0   MUTATED exit=1 ⛔ MISMATCH   GOES RED       restored=True

D9  aso_parent_gap_pairing.py        T1
      path ['corpus','by_gap_specificity_margin','3','n_designs']                  depth 4
      BASELINE exit=0   MUTATED exit=1 stale         GOES RED       restored=True

D10 emc_fourth_cohort_route_readout.py  T1
      path ['per_route','RT-SSTR2','per_gene','SSTR2','readable_in_array_series',0] depth 6
      BASELINE exit=0   MUTATED exit=1 ⛔ stale       GOES RED       restored=True

D11 decoy_null_provenance.py         T1
      path ['arms',0,'verdict_census','confirmed_selective']                       depth 4
      BASELINE exit=0   MUTATED exit=1 DRIFTED       GOES RED       restored=True
```

**Confounded demonstrations — the baseline was already red in the scratch, so the exit code cannot separate (3 runs, 3 modules). Reported, not hidden:**

```
D1  emc_fet_construct_designs.py   BASELINE exit=1  DRIFT in: ['gene_models','ensembl_vs_uniprot_sequences']
                                   MUTATED  exit=1  DRIFT in: ['gene_models','ensembl_vs_uniprot_sequences']
    leaf _limits[0]. Exit code UNINFORMATIVE. Weaker but real signal: the module's own drift
    list is IDENTICAL before and after, so the _limits mutation is invisible to it. Its
    `_limits` gap rests on source (:1000), which is byte-identical to emc_fet_idr_census:675
    where D7 IS decisive.

D4  aso_control_oligos.py          BASELINE exit=1 (already stale in the scratch)  UNINFORMATIVE
D5  cd248_precedent.py             BASELINE exit=1  DRIFT in: ['emc_specific_evidence']
                                   MUTATED  exit=1  DRIFT in: ['records','emc_specific_evidence']
    Partially informative: the drift list GAINED 'records', so the gate did notice the
    depth-4 mutation. Recorded as a weak RED, not a clean one.
```

**Three Class C modules did not reproduce in a clean scratch checkout at all** (`emc_fet_construct_designs.py`, `aso_control_oligos.py`, `cd248_precedent.py` — baseline exit 1). That is an incidental observation on a sample of ten, **not** a measured repository-wide rate, and I make no claim about its cause.

### R4 — The split, with its denominator (`PRIMARY`)

| Quantity | n | of 90 |
|---|---|---|
| Class C modules in W27b's census | **90** | 100 % |
| **Sampled** — comparison expression read from source and assigned a shape | **90** | **100 %** |
| Of those, **full check block + helper read** at `file:line` (the at-risk strata T2/T3/T4) | **32** | 35.6 % |
| **Source-read only**, no mutation run | **80** | 88.9 % |
| **Demonstrated by mutation** (distinct modules) | **10** | 11.1 % |
| — of which the demonstration is **decisive** (green baseline) | **7** | 7.8 % |
| — of which **confounded** (baseline already red) | **3** | 3.3 % |
| **Class C modules that survive as stated** | **88** | **97.8 %** |
| **Class C modules that are really Class B** (a content key excluded outright) | **2** | 2.2 % |
| Class C modules with a **nested exclusion below the top level** | **4** | 4.4 % |
| Class C modules with a **one-directional top-level loop** (caveat, not reclassification) | **7** | 7.8 % |

**W27b's headline changes by two modules and survives.** Its A+B total of 33 becomes **35 of 129 (27.1 %)**; counting Class F, 39 becomes **41 of 129 (31.8 %)**. Class C falls from 90 to **88 (68.2 %)**. The whole-document idiom remains dominant and the gap class remains a minority.

**The failure mode W27b named was not found.** It feared *"a `derive()` that silently drops a nested field inside a compared key."* I found **zero** instances. Every one of the six exclusions in R2 is **explicit in the comparison expression itself**, one line from the `!=`, and three of them carry a written rationale in the source. Four of the six exclude a **generation timestamp**; two exclude a **hand-written prose limitations block**. **None excludes a measured scientific value.** The nested gap that exists is narrow, named, and — for the four timestamp cases — deliberate.

---

## Validation evidence

**RUN.**

1. **W27b's extraction re-verified against live source.** Inline `python3` heredoc re-reading every line W27b quoted, from the live file at my HEAD: `lines re-read from live source: 5528  mismatches: 0`, **exit 0**. This is what licenses treating `checkpaths.json` as source.
2. **Class C set reconstructed and cross-checked.** `/tmp/claude-0/w27c/classc.py` over `checkpaths.json` (129 keys) minus W27b's 39 named A/B/F modules → `total 129 ClassC 90`, **exit 0**, `named 39 missing from modlist: []`. Reproduces W27b's 90 exactly.
3. **Shape triage over all 90.** `shapes.py` → 610 lines of comparison-line extracts, **exit 0**; I read all of it. `strata2.py` → `Counter({'T1_whole': 58, 'T2_whole_minus_named': 23, 'T3_keyloop_onedir': 7, 'T4_keyloop_bidir': 2}) sum 90`, **exit 0** — then corrected by hand-read to **61 / 20 / 7 / 2** (4 T2 false positives demoted, 1 T1 promoted).
4. **T2/T3/T4 full check-block read.** `t2.txt` (358 lines) and an equivalent T3/T4 dump, **exit 0** each; both read in full.
5. **Recursive-helper sweep.** Inline `python3` heredoc over all 90 resolved check paths → `RECURSIVE: nr4a3_fusion_targets_occupancy.py _strip`, `RECURSIVE: emc_cohort_search.py _strip`, `RECURSIVE: nr4a3_fusion_targets_confounds.py _strip_volatile`, `NESTED-POP: steric_carrier_audit.py .get("_generated", {}).pop(`. **exit 0.** This is what caught `emc_cohort_search.py`.
6. **Scratch copy.** `tar … | (cd /tmp/claude-0/w27c/scratch && tar -xf -)`, **exit 0**, `du -sh` = **613M**.
7. **Baseline sweep** on five write-safe candidates, `cwd=scratch`: `emc_fet_idr_census.py exit=0`, `aso_parent_gap_pairing.py exit=0`, `emc_fourth_cohort_route_readout.py exit=0`, `junction_aso_thermo.py exit=0`, `decoy_null_provenance.py exit=0`.
8. **The twelve demonstrations.** `demo.py`, `demo2.py`, `demo3.py`, each **exit 0**; output quoted verbatim in R3.
9. **Scratch restored, verified at the end.** `cmp -s` against the live tree for **all ten** mutated artifacts → `IDENTICAL_TO_LIVE` ×10. `diff -rq research /tmp/claude-0/w27c/scratch/research` reports **no content differences** — its only output is three `Only in …/reports:` lines (`W16h`, `W31c`, `W37`), other workers' reports the coordinator wrote into the live tree *after* my tar. In-run `restored=True` was additionally asserted per demonstration.
10. **Live tree untouched.** `git status --porcelain | wc -l` → **0** at start and end. `git diff --name-only 5ae0fa04..HEAD -- research/modalities research/manuscripts` → **0 files**. No git write operation. `scripts/preflight.sh` not run.
11. **Scratch deleted.** `rm -rf /tmp/claude-0/w27c`; `ls -d /tmp/claude-0/w27c` → "No such file or directory".

**PROPOSED (NOT RUN), explicitly:**
- `emc_fourth_cohort_quant.py --check`, `nr4a3_linker_library_canonical.py --check` — **refused**, both write. W27b's refusals respected unchanged.
- `emc_sra_study.py --check` — not run; fetches on a cold cache.
- The other 80 Class C modules — not run; their depth behaviour is a **source finding**.
- Any repair, allowlist, meta-guard or test. **No fix authored, no `--check` edited, no guard weakened or reordered, no ceiling proposed, no pytest run.**

---

## Limitations

- **80 of 90 rest on source reading, not measurement.** In particular the 61 T1 modules are asserted deep-complete because `!=` on Python containers recurses and because four of them demonstrated it; the other 57 are **UNKNOWN by measurement**, though their comparison expressions leave no room I can see.
- **Three of ten demonstrations were confounded by a red baseline**, including the one I most wanted (`emc_fet_construct_designs.py`). Its `_limits` finding is carried by the byte-identical sibling `emc_fet_idr_census.py:675`, where D7 is decisive, plus its own unchanged drift list. That is inference across two modules, not a direct measurement of the first.
- **"Three of ten did not reproduce in a clean scratch" is not a rate.** Ten is not a sample from which to estimate the repository. I did not investigate the cause and make no claim about it.
- **I did not enumerate any artifact's full nested key space.** A gap that exists only for a nested key I did not happen to walk to would be missed. The deepest-first walk picks *one* leaf per module.
- **The `_limits` reclassification is a judgment call on W27b's own rule.** Its Class C definition permits stripping "an explicitly named volatile field". `_limits` is named and explicit but is *not* volatile — it is content — so I count those two as B. An owner who reads the rule as "any explicitly named field" would keep Class C at 90. I state the basis so the choice is checkable rather than buried.
- **Class C's own boundary is inherited, not re-derived.** I took W27b's 129-module enumeration and its 39 named A/B/F modules as given, per dispatch. Its unresolved 129-vs-W27's-130 discrepancy is untouched and remains open.
- **Nothing here says any committed value *is* wrong.** Every artifact mutated was restored and verified byte-identical to the live tree. The demonstrations show only that a wrong value in those specific positions *would not be caught*.
- **No clinical claim.** This is an audit of exit codes. No EMC efficacy, safety, selectivity or clinical-readiness statement; no wet lab; no patient data; no new source.
- **Model identity is SELF-REPORT, not independently verified.** HEAD moved under me; I verified no file I measured changed rather than assuming it.

---

## Stop condition

Stated before measurement, five parts, quoted above. **MET in full.** A sampling rule is stated and executed at 100 % coverage for shape and 35.6 % for full check-block reading, with the untested 80 named. Every sampled comparison was read from source at `file:line`, and write-safety was confirmed in source before each of the ten modules I ran. Twelve mutation runs over ten modules exceed the required four, with real recorded exit codes, restored between mutations and the scratch verified restored and then deleted. The split is reported with its denominator. No repair was authored, no guard weakened, no Class A or B re-audited, and all three named modules were left unrun.

---

## Tool-call and wall-clock count actually used

**34 tool calls** (all `Bash`), **7 minutes 37 seconds** wall clock (`03:40:28Z` → `03:48:05Z`), plus report drafting. Inside the ~40-call / ~40-minute target; I returned on meeting the stop condition.

---

## Next concrete action

**No further audit is warranted in this lane, and that is the finding.** W27's Class D/E were the open question; W27b closed them; I stress-tested the one assertion W27b flagged and it held at 97.8 %. A third census pass would be the "repeatedly rewrite a correct paper" failure `CLAUDE.md` §5 names. The lane's remaining uncertainty — 57 T1 modules unmutated — would cost a full run to convert source certainty into measured certainty about an idiom that has now gone red on four of four deep mutations.

**The single next action is the owner's, and my result sharpens W27b's recommendation rather than replacing it.** W27b advised Option 1 on the 11 Class A modules. **Add exactly two names to that list**: `research/modalities/emc_fet_idr_census.py:675` and `research/modalities/emc_fet_construct_designs.py:1000`, whose `k != "_limits"` excludes a prose content block, not a stamp — the cheapest correct change is deleting five characters from a list comprehension in each, and both sit next to 88 siblings that already gate the whole document. Do **not** touch the four timestamp exclusions: they are deliberate, documented, and `steric_carrier_audit.py:862-873` argues in its own source why a check that cries wolf about a timestamp is worse than no check. That argument is right, and this repository should not un-learn it to make a census table tidier.

**One thing the owner should know before pricing Option 2.** Its allowlist grows from 39 to **41**, and the two additions are *inside* what a top-level static analysis would score as complete — a meta-guard reading only the comparison's shape would pass `emc_fet_idr_census.py` and miss `_limits`. The gap Option 2 is meant to close is partly invisible to Option 2. I do not recommend either option, have authored neither, and propose no ceiling change.
