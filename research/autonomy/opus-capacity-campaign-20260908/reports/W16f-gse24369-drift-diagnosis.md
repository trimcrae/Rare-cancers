<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:29:18Z UTC
     agent id a38a913f62f446f8e ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a38a913f62f446f8e.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

## Worker

**W16f**, LANE 16 fourth refill — W16e's second named successor: diagnose the shared cause behind the three co-drifting Class-C artifacts.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am powered by Opus 5, exact model ID `claude-opus-5`. I did not observe the served model and do not assert it as fact. No environment variable in this container names a served model.

| | start | end |
|---|---|---|
| `date -u` | `Tue Sep  8 03:17:07 UTC 2026` | `Tue Sep  8 03:26:03 UTC 2026` |
| `git rev-parse HEAD` | `c81236b90c7905caa2e75a57b332ad33f2c10d02` | `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f` |
| `git status --porcelain` | **empty** | **empty** |

**The tree moved under me** (`c81236b9` → `ff6bb018`; the coordinator is committing campaign reports). **My `tar --exclude=./.git` snapshot was taken at `c81236b9`, and every measurement below is against `c81236b9` and only that.** Note this is a *different* commit from W16e's `3f5fc95`; all values I report reproduced anyway.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (51 lines; five very long proxy/truststore lines marked elided rather than reprinted — none contains a model identity):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...                    [elided: proxy host list]
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
GLOBAL_AGENT_NO_PROXY=localhost,127.0.0.1,::1,...       [elided]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=-Djavax.net.ssl.trustStore=...        [elided: proxy/truststore flags]
NO_PROXY=localhost,127.0.0.1,::1,...                    [elided]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=localhost,127.0.0.1,::1,...          [elided]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

The end-of-run `env` output was identical (46 lines after filtering the 5 elided long ones; unchanged set).

---

## Stop condition (stated up front)

Return the moment all five are established: (1) the exact committed input file each of the three reads, by code path; (2) whether the drift is attributable to input content, a shared helper, or a filter threshold, with quoted values; (3) the decision evidence that would tell an owner which side is stale, *without deciding it*; (4) W16e's three identity failures reproduced independently with a real exit code; (5) every other consumer of the same input tested, with any further cluster members named and any unmeasured ones labelled unmeasured.

**All five were established. Stop condition MET.**

---

## Question

**What single cause makes `emc_proteostasis_read`, `emc_prmt5_route_controls` and `emc_mtap_locus_persample` fail the regeneration identity together and drift in the same direction — and what evidence would tell the data owner whether the committed artifacts or the committed input is the stale side?**

Open because W16e demonstrated the co-drift and explicitly deferred the cause and the which-side-is-correct question to the data owner, and because W16e's 66 UNKNOWN rows could hide further members of the same cluster.

---

## Prior-work check

Commands actually run in `/home/user/Rare-cancers` (read-only):

```
grep -rn "GSE24369" --include=*.py research/modalities/ scripts/
git ls-files | grep -i "GSE24369"
grep -ln "emc-expression-panels.json" research/modalities/*.py
grep -rn "n_symbols_scored|n_genes_read|signed_percentile" research/modalities/*.py
git log --no-merges -3 --format=... -- research/modalities/emc-expression-panels.json  (and 4 more)
git log --format='%h parents=%p ...' -5 14a3f172
```

plus full reads of `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md` and W16e's report.

**Not replaying W16e.** I did not re-run the 158-pair census, the tier-budget measurement, or the coverage detector. I reproduced only the three failing identities W16e's finding rests on, then went past them. **I authored no `pinned-figures.json` entry, wrote nothing into the tree, ran no git write operation, did not run `scripts/preflight.sh`, and retrieved nothing over the network.** **I did not touch, argue or resolve the `bishop2019` per-pool clause** — it plays no part in anything below. `CLOSED-WORK.md` records `GSE24369`-family data as heavily retained; I read no new source and add no new data, only a defect diagnosis over committed files.

---

## Method / inputs

Executed on a `tar --exclude=./.git` scratch copy at `/tmp/claude-0/w16f/tree/`, taken from HEAD `c81236b9`. Nothing under `/home/user/Rare-cancers` was created, edited or deleted. Read-only inspection (`grep`, `git log`, `python3 -c` over committed JSON) was done in the live checkout.

**Environment:** system `python3` = 3.11.15, stdlib only. All runs with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPYCACHEPREFIX=/tmp/claude-0/w16f/pyc`. No network was used; no series matrix was fetched.

Files read (all committed, all under `research/modalities/`):
`emc_proteostasis_read.py`, `emc_prmt5_route_controls.py`, `emc_mtap_locus_persample.py`, `emc_expression_panels.py`, `emc_hypoxia_confounds.py`, `emc-expression-panels.json`, `emc-expression-panels-inputs.json`, `emc-proteostasis-read.json`, `emc-prmt5-route-controls.json`, `emc-mtap-locus-persample.json`, `emc-hypoxia-confounds.json`, `emc-prmt5-effect-sizes.json`, plus the 22-module consumer set.

---

## Result

### 1 · The premise correction: there is no GSE24369 series matrix in this repository · PRIMARY

W16e wrote that the three modules "all read the same GSE24369 series matrix." **They do not.** `GSE24369_series_matrix.txt.gz` is a **dictionary key**, not a path.

```
$ git ls-files | grep -i GSE24369      → (no output)
$ find . -name "GSE24369*" -not -path "./.git/*"   → (no output)
```

The string is never opened. In `emc_prmt5_route_controls.py` it is a bare literal (`P6244 = "GSE24369_series_matrix.txt.gz"`, line 52) used only to index into a JSON object. **This matters for the diagnosis: no external or raw input changed, because there is no raw input in the tree to change.**

### 2 · The single shared committed input, by code path · PRIMARY

All three read the **same one committed artifact**: `research/modalities/emc-expression-panels.json`.

| Module | Line | Binding |
|---|---|---|
| `emc_proteostasis_read.py` | 49 | `PANEL = os.path.join(HERE, "emc-expression-panels.json")` |
| `emc_prmt5_route_controls.py` | 51 | `PANEL = os.path.join(HERE, "emc-expression-panels.json")` |
| `emc_mtap_locus_persample.py` | 69 | `PANELS = os.path.join(HERE, "emc-expression-panels.json")` |

(`emc_mtap_locus_persample` additionally reads `emc-expression-panels-inputs.json` and `emc-hypoxia-null-background.json`; `emc_proteostasis_read` additionally reads `depmap-sarcoma-dependency.json`. The panel is the only input common to all three.)

### 3 · Input content, not helper, not threshold — with the values · PRIMARY

**The two named drifting fields are not computed by any of the three generators. They are computed once in `emc_expression_panels.py` and copied through.**

- `emc_expression_panels.py:1591` — `"signed_percentile": round(100.0 * bisect_left(ts_sorted, t) / n, 2)`
- `emc_expression_panels.py:1602` — `"n_symbols_scored": n`
- `emc_prmt5_route_controls.py:290` — `"n_symbols_scored": gw.get("n_symbols_scored")` ← **a pure pass-through of the input's value.**

Grepping all of `research/modalities/*.py`, `n_symbols_scored` appears in exactly two files (the producer and this one consumer) and `signed_percentile` in exactly one (the producer). **No consumer recomputes them; no filter threshold and no shared helper is on the path.**

Reading the committed values directly settles it:

| Field (GSE24369 arm) | Committed **input** `emc-expression-panels.json` | Committed **artifacts** | Grade |
|---|---|---|---|
| `…genome_wide_null.n_symbols_scored` | **18697** | `emc-prmt5-route-controls.json` → **18688** | PRIMARY |
| `…placed_wanted_genes.XBP1.signed_percentile` | **93.96** | `emc-proteostasis-read.json` → **93.95** | PRIMARY |
| genes in `gene_reads` | **479** | — | PRIMARY |
| genes `readable` on GSE24369 | **464** | `emc-mtap-locus-persample.json` `n_genes_read` → **404** (all 6 EMC + all 29 comparator samples) | PRIMARY |

`n_genes_read` is not a stored value either — `emc_mtap_locus_persample.py::_dimness` (lines 171-193) counts, per sample, the panel genes that are `readable` and carry a non-null `array_percentile`. I re-executed that loop against the committed panel: **it returns 464 for all 35 samples** (`distinct values: [464], n_gsm: 35`). The committed artifact stores 404.

⭐ **The single cause: the shared committed input `emc-expression-panels.json` gained roughly 60 readable genes on the GPL6244 arm since the three artifacts were written. Every drifting field is a count over, or a rank within, that gene set — so one more gene entering the panel moves the denominator, which moves every percentile and every "n at least as extreme" by one or two units. That is one input change, propagating through three pass-through consumers.** It is **not** a change to any of the three generators, **not** a shared helper, and **not** a filter threshold.

Direction is consistent with growth: the array-wide denominator went **up** (18688 → 18697), so a fixed t-statistic's rank fraction moved **up** (93.95 → 93.96) and the panel-cache count went **up** (404 → 464). The GPL3290 arm moves **down** by one (`n_symbols_scored` 14404 → 14403), which is a small opposite-direction change on the other platform — **W16e described the cluster as drifting on one input in one direction; the GSE4303 arm is a second, smaller, opposite-signed drift in the same shared file, which W16e did not report.**

### 4 · What would tell the owner which side is stale — the evidence, not the decision · PRIMARY

I am **not** deciding this. The strongest single piece of evidence already exists inside the artifacts, self-documented:

| Committed file | Embedded provenance stamp | Grade |
|---|---|---|
| `emc-expression-panels.json` | `generated_utc = 2026-08-29T12:51:32+00:00` | PRIMARY |
| `emc-expression-panels-inputs.json` | `_generated_utc = 2026-08-29T12:51:32+00:00` | PRIMARY |
| `emc-mtap-locus-persample.json` | `_generated_from = **2026-08-09T18:41:04+00:00**` | PRIMARY |
| `emc-hypoxia-confounds.json` | `_source_inputs_generated_utc = **2026-08-07T14:10:07+00:00**` | PRIMARY |

`emc_mtap_locus_persample.py:299` writes `"_generated_from": panels.get("generated_utc")`. **So the committed artifact states, in its own text, that it was built from a panel stamped 2026-08-09, while the panel now committed beside it is stamped 2026-08-29 — a 20-day gap.** `emc-proteostasis-read.json` and `emc-prmt5-route-controls.json` carry **no** provenance stamp at all, which is itself a finding: they cannot say what they were built from.

**The decision evidence an owner should weigh, laid out neutrally:**

1. **The self-declared stamp gap above.** It establishes ordering (the artifacts encode an older panel) but *not* correctness — a panel could have been regenerated wrongly on 2026-08-29 and the older artifacts still be the right numbers.
2. **Whether the 2026-08-29 panel itself reproduces from `emc_expression_panels.py`.** This is the decisive test and **I could not run it: the GEO series matrices it parses are not in the tree, and I am under a no-network instruction. UNKNOWN.** If the panel does not reproduce from its own generator, the input is the stale/suspect side; if it does, the downstream artifacts are.
3. **Which ~60 genes entered the panel between the two stamps, and under what authorization.** `emc_prmt5_route_controls.py`'s own docstring records that genes were deliberately added to `emc_expression_panels.PANELS` on **2026-08-09** for controls 2-4, and states that until a `mode=panels` fetch runs the panel does not carry them. That is a *documented intent to grow the panel*, which favours the input being the newer, intended state — but it is prose, not a measurement.
4. **`git` history gives nothing.** `14a3f172` is the repository's **root commit** (`git log --format='%h parents=%p'` → `parents=` empty); every file above has exactly one commit. **There is no version history to date either side.** This is a real gap in the decision evidence and the owner should know it before treating "the input is newer" as proven by anything other than the embedded stamps.
5. **Downstream blast radius.** See §5 — six artifacts, not three, move with this input.

### 5 · The cluster is at least SIX, not three — three further members found · PRIMARY

22 modules under `research/modalities/` read `emc-expression-panels.json`. I ran the identity on all of them. Six of these expose the repository's own `--check` mode (re-derive and diff against the committed artifact); I used it, and quote its real exit codes.

| Module | Verdict | Exit | What differs | Grade |
|---|---|---|---|---|
| `emc_proteostasis_read` | **DIFFERS** (29 leaves) | 1 | percentiles / n-at-least-as-extreme | PRIMARY |
| `emc_prmt5_route_controls` | **DIFFERS** (31 leaves) | 1 | `n_symbols_scored` 18688→18697 + placements | PRIMARY |
| `emc_mtap_locus_persample` | **DIFFERS** (**200** leaves) | 1 | `_generated_from` + `n_genes_read` 404→464 ×35 samples | PRIMARY |
| **`emc_hypoxia_confounds`** | **DIFFERS** | **1** | `_source_inputs_generated_utc`, `platforms`, `cross_platform` | **PRIMARY — new** |
| **`emc_prmt5_effect_sizes`** | **DIFFERS** | **1** | `cache_sizes`, `family_composition_sensitivity`, `per_platform` | **PRIMARY — new** |
| **`emc_prmt5_multiplicity`** | **DIFFERS** | **1** | `per_platform` | **PRIMARY — new** |
| `nr4a3_fusion_targets` | REPRODUCES | **0** | — (`offline re-derive matches the artifact`) | PRIMARY |
| `census_route_expression_grading` | IDENTICAL | 0 | — | PRIMARY |
| `emc_dkk1_lineage_controls` | IDENTICAL | 0 | — | PRIMARY |
| `emc_fourth_cohort_route_readout` | IDENTICAL | 0 | — | PRIMARY |
| `ndrg1_panel_attribution` | IDENTICAL | 0 | — | PRIMARY |
| `alcam_precedent` | DIFFERS, exit 1 — **but NOT this cluster** | 1 | `emc_specific_evidence._status: 'READ' → 'UNREAD'`; the whole block vanishes because `origin/literature-cache` is unreachable here. This is W16e's Class B (degraded input), not panel drift. | UNKNOWN |
| `cd248_precedent` | same as above | 1 | same `READ → UNREAD` signature | UNKNOWN |

⚠ **Identity UNMEASURED — not passing, not failing** (these are exactly W16e's UNKNOWN rows, and I could not clear them either):

- **`emc_surface_normal_window`** — still running when my 120 s harness timeout killed it (`rc=143`). **Unmeasured.** This is the one I would look at next: it is a panel consumer with a real artifact and no result either way.
- **`aso_delivery_antigen`**, **`emc_tissue_read_statistics`** — `main()` takes a required `argv`; my harness could not drive them and I did not construct arguments. **Unmeasured.**
- **`atr_hrd_sarcoma_series`**, **`emc_mtap_prmt5_figures`**, **`expression_validation_readiness`**, **`single_slot_identity`**, **`surface_address_sensitivity`** — no module-level `OUT` naming a `.json` (figure/report modules). Not identity-testable in this form. **Unmeasured.**

⛔ **Say this plainly: none of the eight modules above is reported as passing. Their identity was not measured. A missing measurement is unknown, not zero.**

### 6 · Where I disagree with W16e, with both numbers · PRIMARY

| Item | W16e | W16f (this run) | Note |
|---|---|---|---|
| `emc_mtap_locus_persample` differing leaves | **41**, classified **Class A (timestamp-only)** | **200**, and the timestamp is **not** a run clock | Both stated. The `_generated_from` field is a *propagated input provenance stamp*, not a generation time; classifying it as a timestamp masked 199 real leaves. Different snapshot commits (`3f5fc95` vs `c81236b9`) could contribute, but the class error does not depend on the commit. |
| The shared input | "the same GSE24369 series matrix" | `emc-expression-panels.json`; **no series matrix exists in the tree** | See §1. |
| Cluster size | 3 | **≥ 6** | See §5. |
| Drift direction | one direction on one input | GPL6244 up, **GPL3290 down by 1** | See §3. |

`n_symbols_scored` 18688→18697, XBP1 `signed_percentile` 93.95→93.96 and `n_genes_read` 404→464 **all reproduced exactly** as W16e reported. W16e's core finding stands; the framing of its cause did not.

**No clinical, efficacy, safety, selectivity or prognosis claim is made or implied here.** Every number above is an internal consistency measurement over committed files. A transcriptomic percentile is an **ASSOCIATION**, never a mechanism, and none of these values changes what any of them can support.

---

## Validation evidence

**RUN.** All in the scratch copy at `/tmp/claude-0/w16f/tree` unless noted, with `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/claude-0/w16f/pyc`.

| # | Command | Exit | Key output |
|---|---|---|---|
| 1 | `date -u; git rev-parse HEAD; git status --porcelain` (live repo, start) | 0 | `03:17:07Z`; `c81236b9…`; status **empty** |
| 2 | `tar --exclude=./.git -cf - . \| (cd /tmp/claude-0/w16f/tree && tar -xf -)` | 0 | `COPY_OK`, 612M |
| 3 | `git ls-files \| grep -i GSE24369` ; `find . -name "GSE24369*"` | 1 / 0 | **no output** — no series matrix in the tree |
| 4 | `git log --format='%h parents=%p …' -5 14a3f172` | 0 | `14a3f172 parents=` — **root commit** |
| 5 | `python3 _s/id.py` (independent 3-module identity) | **1** | `emc_proteostasis_read IDENTICAL=False n=29`; `emc_prmt5_route_controls IDENTICAL=False n=31`; `emc_mtap_locus_persample IDENTICAL=False n=200`; incl. `n_symbols_scored: 18688 -> 18697`, `n_genes_read: 404 -> 464`, `_generated_from: '2026-08-09T18:41:04+00:00' -> '2026-08-29T12:51:32+00:00'` |
| 6 | `python3` over committed `emc-expression-panels.json` | 0 | `n_symbols_scored = 18697`; `XBP1.signed_percentile = 93.96`; `gene_reads = 479`; readable GSE24369 = **464**; recomputed `n_genes_read` per gsm = **[464]**, 35 samples |
| 7 | `python3` over the three committed artifacts | 0 | `18688`, `93.95`, `404` ×109 occurrences |
| 8 | provenance-stamp scan over all `research/modalities/*.json` | 0 | panel `2026-08-29T12:51:32+00:00`; mtap `_generated_from 2026-08-09T18:41:04+00:00`; hypoxia `_source_inputs_generated_utc 2026-08-07T14:10:07+00:00`; proteostasis & prmt5-route-controls **no stamp** |
| 9 | `xargs -P 6 timeout 40 python3 _s/one.py` over the 18 other panel consumers | 0 (pipe) | 4 IDENTICAL, 6 argparse `SystemExit 2`, 2 `main(argv)`, 5 `NO-OUT`, 1 slow |
| 10 | `python3 <m>.py --check` for the 6 argparse-gated consumers | **1,1,1,1,1,0** | `emc_hypoxia_confounds` **1** `DIFFERS FROM THE COMMITTED ARTIFACT`; `emc_prmt5_effect_sizes` **1** `DRIFT in: ['cache_sizes','family_composition_sensitivity','per_platform']`; `emc_prmt5_multiplicity` **1** `DRIFT in: ['per_platform']`; `alcam_precedent` **1**; `cd248_precedent` **1**; `nr4a3_fusion_targets` **0** `offline re-derive matches the artifact` |
| 11 | alcam/cd248 `emc_specific_evidence` leaf diff | 0 | `._status: 'READ' -> 'UNREAD'` — literature cache, not the panel |
| 12 | `timeout 120 python3 _s/one.py ndrg1_panel_attribution / emc_surface_normal_window` | 0 / **143** | `ndrg1_panel_attribution IDENTICAL build 0`; `emc_surface_normal_window` **killed, unmeasured** |
| 13 | `date -u; git rev-parse HEAD; git status --porcelain` (live repo, end) | 0 | `03:26:03Z`; `ff6bb018…`; status **empty** |

**PROPOSED (NOT RUN).** Regenerating `emc-expression-panels.json` from `emc_expression_panels.py` to test decision-evidence item 2 — **not run: the GEO series matrices are absent from the tree and network use is prohibited by my dispatch.** Result **UNKNOWN**. I regenerated no committed artifact, landed no fix, and wrote no file into the repository. I did not run `scripts/preflight.sh` and did not touch any test or guard.

---

## Limitations

- **The tree moved under me** (`c81236b9` → `ff6bb018`). Every measurement is pinned to the `c81236b9` snapshot and could differ at a later commit.
- **The decisive test is unrun.** Whether `emc-expression-panels.json` itself reproduces from `emc_expression_panels.py` is **UNKNOWN** here and cannot be answered without the series matrices or network. Without it, "the input is newer" rests on embedded stamps and prose intent, not on a verified regeneration.
- **`git` history is unusable as evidence** — one root commit, no per-file history for any file involved.
- **Eight panel consumers have an unmeasured identity** (§5). The cluster is **≥ 6 and unbounded above by this run**. One (`emc_surface_normal_window`) failed only on my own 120 s harness timeout; a slow-but-correct generator would look identical to that.
- **I did not audit the other 141 non-panel generators** in W16e's census. Whether an analogous shared-committed-input cluster exists elsewhere is UNKNOWN.
- **My leaf-diff harness compares JSON leaves after a full recursive walk**, so a reordered list registers as many differing leaves; the 200-leaf count for `emc_mtap_locus_persample` is a leaf count, not 200 independent quantities (35 samples × several fields dominates it).
- **No clinical claim of any kind.** Nothing here bears on efficacy, safety, selectivity, therapeutic window, prognosis or clinical readiness for any agent or patient. There is no wet lab. Nothing here resolves, argues or touches the `bishop2019` per-pool clause.
- **I did not decide which side is stale.** That is the data owner's call and I have deliberately left it open.

---

## Stop condition

Stated up front; **MET**. All five sub-questions were established by execution or by direct reading of committed files, with real exit codes, W16e's failures reproduced independently on a fresh snapshot before being relied on, disagreements reported with both numbers, and every unmeasured module named as unmeasured rather than passing. Returning now.

---

## Tool-call and wall-clock count actually used

**19 tool calls** (all Bash; one of them backgrounded on timeout and collected). **Wall clock 03:17:07Z → 03:26:03Z = 8 min 56 s.** Both well inside the ~40/~40 target.

---

## Next concrete action

**One task, finite, and it belongs to the data owner of `research/modalities/emc-expression-panels.json`, not to this lane:** run `emc_expression_panels.py` in an environment that has the GEO series matrices (the repository's standing CI/Actions escape hatch is the route, per `CLOSED-WORK.md`'s $0-fetch precedent and the module's own `mode=panels` fetch), and compare the result to the committed 2026-08-29 panel. That single measurement resolves decision-evidence item 2 and therefore the whole which-side-is-stale question: if the panel reproduces, the six downstream artifacts are stale and their owner regenerates them; if it does not, the panel is the suspect side and no downstream regeneration should happen until it is settled. **Whichever way it falls, `emc-proteostasis-read.json` and `emc-prmt5-route-controls.json` should gain a `_generated_from` stamp copied from the panel's `generated_utc`, as `emc_mtap_locus_persample.py:299` already does — that one line is what made this diagnosis possible at all, and its absence is why two of the six artifacts cannot say what they were built from.**

**Explicitly not the next action:** adding a regeneration-identity test to any of these six. Six of them are red today; adding a guard that is red at commit time is a broken gate, not a guard. The identity test goes in *after* the owner's decision, not before.
