> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Both parts complete, stop condition met. Report follows.

---

## Worker

**W14c**, lane 14 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` start: `Tue Sep  8 02:31:01 UTC 2026`. `date -u` end: `Tue Sep  8 02:36:25 UTC 2026`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; **no model field present**):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...,api.anthropic.com,...   [proxy exclusion list, matched on the substring "anthropic"]
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
GLOBAL_AGENT_NO_PROXY=...   [proxy exclusion list]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=...   [proxy exclusion list]
NO_PROXY=...            [proxy exclusion list]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=...   [proxy exclusion list]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```
Environment unchanged at end.

**HEAD actually read — and it MOVED under me, which is a finding in itself.** `git rev-parse HEAD` returned **`47aac85f874a57a6f981c3432abcf16980968aec`** at 02:31:01, and **`7d081218f107363573573e6d102e4334567adf77`** at 02:35:40 and again at 02:36. Neither is the `92abbcb905cacf07f14b238db50d1b98f6590374` named as the frozen read commit in `COMMON-BRIEF.md`; the coordinator is committing collected reports while workers run. My Part-1 scratch copy was taken from the tree at `47aac85f`; my Part-2 measurements were taken at `7d081218`. **The source file `emc_fourth_cohort_quant.py` is byte-identical between the live tree and the frozen `93b` corpus copy** (`diff -q` → no output), so the generator itself did not move across any of these commits.

## Question

Two mechanical questions, both about guards rather than science:

1. **Is `research/modalities/emc_fourth_cohort_quant.py --check` genuinely incapable of failing, and what is the smallest repair that makes it capable of failing without changing any committed value?** Open because W14b classified it statically/behaviourally as the single `FAKE-GUARD` among 512 write-capable scripts but did not corrupt an artifact and watch the guard swallow it, and did not build or execute a repair.
2. **Do the 8 `GUARDED-NOT-ENFORCED` rows actually accept, write nothing and exit 0 against the real Git tree?** Open because W14b measured them in a scratch copy *without `.git`*, a limitation it flagged itself; a guard that behaves differently when `.git` is present (or that writes into the live tree) would be a real finding.

## Prior-work check

Commands run, all read-only:

```
rg -n "_probe_tsv_body" --glob '!.git'                          -> (no output)
rg -n "_probe_tsv_body" /tmp/claude-0/frozen-corpus/extracted/  -> (no output)
diff -q /tmp/claude-0/frozen-corpus/extracted/corpus/research/modalities/emc_fourth_cohort_quant.py \
        research/modalities/emc_fourth_cohort_quant.py          -> (no output; identical)
git ls-files | rg -i "check_is_a_check|guard_that_cannot_fail"
    -> research/manuscripts/tests/test_a_guard_that_cannot_fail_is_not_a_guard.py
grep -rn "emc_fourth_cohort_quant" --include=*.py --include=*.yml --include=*.sh --include=*.md .
```

What they showed: the repair I authored is not present in either the live tree or the frozen corpus (**UNKNOWN, not proven absent**, per `CORPUS-CONTEXT.md` — but the specific file is present in the corpus and identical, so for *this file* the absence is a real read). The repository already owns the concept under `test_a_guard_that_cannot_fail_is_not_a_guard.py`, which is the failure class this defect belongs to. `derive()` has exactly **one** in-module caller (`main`, line 933) and two external test call sites (`Q.derive(cache)` positional, lines 138/156/182 of `research/modalities/tests/test_emc_fourth_cohort_quant.py`), which is why the repair is keyword-only with write-preserving defaults.

Closed items I confirmed I am **not** replaying: I drew **no EMC classification conclusion** from `emc_icdo_contamination.py` — I ran its `--check`, recorded the exit code, and read none of its output as science; **PUB-EMC-CLASSIFICATION stays closed and unreopened**. I touched no Brenca route, no lane-11 source-index file, made no network call, and admitted no new EMC calibration analysis. I did not add a row to `scripts/preflight.sh` and did not run `scripts/preflight.sh`.

## Method / inputs

- Live checkout `/home/user/Rare-cancers` at HEAD `47aac85f…` (part 1 source) / `7d081218…` (part 2 measurement). Frozen corpus consulted read-only for the file-identity check.
- **All execution for part 1 in `/tmp/claude-0/w14c/`.** I copied 6 files (the generator plus `emc-fourth-cohort-quant.json`, `emc-fourth-cohort-quant-inputs.json`, `emc-fourth-cohort-gene-counts.tsv`, `emc-fourth-cohort-probe-counts.tsv`, `emc-sra-study-inputs.json`) into `/tmp/claude-0/w14c/mod/`; `HERE = os.path.dirname(os.path.abspath(__file__))` makes every path resolve inside the scratch dir, so the live tree was never a target.
- Interpreter: CPython **3.11.15** (`/usr/local/bin/python3`). Test runner: **pytest 9.1.1** at `/root/.local/bin/pytest`.
- Part 2 ran the 8 `--check` invocations **in the live tree** as the task requires, bracketed by a `sha256sum` of all 2,151 files under `research/modalities` plus `git status --porcelain`.

## Result

### Part 1 — the fake guard, mechanism and repair

The defect is worse than "hashes the bytes it just wrote", in two distinct ways. Both are `PRIMARY` (executed).

`main()` calls `out = derive()` **before** the `--check` branch (line 933). Inside `derive()`, line 817 calls `_write_probe_tsv(cache, p2g)` — which **writes `emc-fourth-cohort-probe-counts.tsv`** — and lines 830-831 **write `emc-fourth-cohort-gene-counts.tsv`**. The shas at lines 819 and 832 are taken from those just-written bodies, then compared against the shas recorded in the committed JSON. The comparison is therefore process-internal and self-agreeing.

| # | Leg of the defect | Evidence | Grade |
|---|---|---|---|
| 1 | Corrupting `emc-fourth-cohort-gene-counts.tsv` → `--check` **silently restores it** and prints `no drift`, **exit 0** | run below | PRIMARY |
| 2 | `probe_counts_sha256` **is not even in the drift key list** (line 940-941), so probe-table corruption is both restored *and* uncompared | run below | PRIMARY |
| 3 | The one workflow step that runs `--check` is itself **non-blocking** (`.github/workflows/emc-expression-datasets.yml:1066-1067`: `--check \|\| echo "--check reported drift; non-blocking, but READ IT"`) | source read | PRIMARY |

Leg 3 is a **second-order finding beyond W14b's brief**: even had the guard worked, its only caller discards the exit code. Repairing the guard alone does not make it enforced. I did **not** change that workflow (out of scope, and it is a gate-wiring decision).

**The repair**, proven by execution: hoist the writes out of `derive()`, and compare the **committed bytes on disk** rather than the recomputed body.

| Acceptance test | Expected | Observed | Grade |
|---|---|---|---|
| T1 repaired `--check`, clean tree | exit 0, nothing written | `no drift: …` **exit 0**, all 3 shas unchanged | PRIMARY |
| T2 repaired `--check`, corrupted gene TSV | exit 1, file left corrupt | `DRIFT: ['emc-fourth-cohort-gene-counts.tsv']` **exit 1**, file still corrupt | PRIMARY |
| T3 repaired `--check`, corrupted probe TSV | exit 1, file left corrupt | `DRIFT: ['emc-fourth-cohort-probe-counts.tsv']` **exit 1**, file still corrupt | PRIMARY |
| T4 repaired `--check`, JSON-side drift | exit 1 (regression: old behaviour retained) | `DRIFT: ['n_runs_read']` **exit 1** | PRIMARY |
| T5 write path reproduces committed values | JSON identical apart from the pre-existing timestamp | **identical** — see below | PRIMARY |
| T6 module's own 20 tests | 20 passed | **20 passed**, pytest exit 0 | PRIMARY |
| T7 `--selftest` | exit 0 | `selftest: 0 failure(s)` exit 0 | PRIMARY |

**No committed value changes.** With the pre-existing non-deterministic `_generated_utc` field normalised, the committed JSON, the original script's output, and the repaired script's output all hash to `44c81ae7f1fe8c418789ea5433f25adf98f4f739a34a61d1faaed405d8067f84`. Both TSVs come back bit-identical to the committed bytes (`sha256sum -c` → OK). A key-by-key diff of the original-produced vs repaired-produced JSON shows **only** `_generated_utc`, differing by the 13 seconds between the two runs.

`_generated_utc` being a wall-clock stamp inside the artifact is a separate pre-existing property (`UNKNOWN` whether intended); it is not in the drift key list so it does not affect the guard, and the repair leaves it alone.

### Part 2 — the 8 rows, re-measured against the real tree

All 8 ran offline in the live tree at HEAD `7d081218f107363573573e6d102e4334567adf77`. All `PRIMARY`.

| # | Script (`research/modalities/…`) | W14b scratch exit | **W14c real-tree exit** | Divergence | Artifact sha before → after |
|---|---|---|---|---|---|
| 1 | `emc_adaptive_pazopanib.py` | 0 | **0** | none | `b04247bb5a3a90c7` → `b04247bb5a3a90c7` |
| 2 | `emc_icdo_contamination.py` | 0 | **0** | none | `0ad05c75bd2a204a` → `0ad05c75bd2a204a` |
| 3 | `emc_rt_bed_reappraisal.py` | 0 | **0** | none | `578995648425fa60` → `578995648425fa60` |
| 4 | `emc_tissue_read_statistics.py` | 0 | **0** | none | `3213777eefcea5c6` → `3213777eefcea5c6` |
| 5 | `emc_scheduling_medians.py` | 0 | **0** | none | `d9fa663dc0f6038f` → `d9fa663dc0f6038f` |
| 6 | `emc_fourth_cohort_route_readout.py` | 0 | **0** | none | `d4e00635f8a3aee6` → `d4e00635f8a3aee6` |
| 7 | `atr_part_d_proliferation_control.py` | 0 | **0** | none | `c1ea403f38ac2735` → `c1ea403f38ac2735` |
| 8 | `tcf12_offtarget_tissue_expression.py` | 0 | **0** | none | `a5dae96da465f1d1` → `a5dae96da465f1d1` |

**Divergence from W14b's scratch result: none. Zero of eight differ.** W14b's flagged limitation (no `.git` in its scratch copy) turns out not to have mattered for these rows — none of the eight consults Git state.

`git status --porcelain` is **empty** before and after. A full recursive `sha256sum` of `research/modalities` (2,151 files) is **byte-identical before and after excluding `__pycache__`**. The only new files are five untracked `.pyc` bytecode caches (`research/modalities/__pycache__/…cpython-311.pyc`), which are gitignored (`.gitignore:9: __pycache__/`, confirmed by `git check-ignore -v`). I report them rather than omit them: they are a real on-disk side effect of running the checks, they are not tracked content, and I left them in place rather than deleting files in a tree I am read-only on.

Row 2 (`emc_icdo_contamination.py`) was verified **mechanically only**. Its `--check` exits 0 and writes nothing. **No classification conclusion is drawn, PUB-EMC-CLASSIFICATION remains user-rejected and closed, and nothing here reopens it.**

## Validation evidence

Environment for every run: CPython 3.11.15, pytest 9.1.1, Linux, no network.

**RUN — the fake guard reproduced** (`cd /tmp/claude-0/w14c/mod`):

```
$ python3 emc_fourth_cohort_quant.py --check          # clean tree, ORIGINAL script
no drift: the derive half reproduces offline
exit=0

$ # corrupt one integer in the committed gene TSV
BEFORE row2: AARS1	491	987	359	435	683	61	107	888	471	448	446	138
AFTER  row2: AARS1	1000491	987	359	435	683	61	107	888	471	448	446	138
corrupted sha: 2168ab583b9f2a209e7c0cdd674f3595a30651adc8301946fdbfac537cf8eeaa

$ python3 emc_fourth_cohort_quant.py --check          # ORIGINAL script, CORRUPTED TSV
no drift: the derive half reproduces offline
exit=0

$ sha256sum emc-fourth-cohort-gene-counts.tsv
8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc   <- SILENTLY RESTORED
row2 now: AARS1	491	987	359	435	683	61	107	888	471	448	446	138
```

Second leg, the probe table (its sha is not in the drift key list at all):

```
$ # set row 2's assigned_gene column to BOGUS_GENE_XYZ
corrupted probe sha: f273b0c07e13f30e37c136ee4a526463d84e2cde6c4328ed427af4c3f16d6f1d
$ python3 emc_fourth_cohort_quant.py --check          # ORIGINAL script
no drift: the derive half reproduces offline
exit=0
$ sha256sum -c baseline.sha
emc-fourth-cohort-probe-counts.tsv: OK                <- SILENTLY RESTORED
```

**RUN — the repaired guard** (same directory, patch applied):

```
$ python3 emc_fourth_cohort_quant.py --check          # T1 clean
no drift: the derive half reproduces offline
exit=0
emc-fourth-cohort-gene-counts.tsv: OK
emc-fourth-cohort-probe-counts.tsv: OK
emc-fourth-cohort-quant.json: OK

$ python3 emc_fourth_cohort_quant.py --check          # T2 corrupted gene TSV
DRIFT: ['emc-fourth-cohort-gene-counts.tsv']
exit=1
2168ab583b9f2a209e7c0cdd674f3595a30651adc8301946fdbfac537cf8eeaa   <- NOT restored
row2 still corrupt: AARS1	1000491	987	359	435	683	61	107	888	471	448	446	138

$ python3 emc_fourth_cohort_quant.py --check          # T3 corrupted probe TSV
DRIFT: ['emc-fourth-cohort-probe-counts.tsv']
exit=1
f273b0c07e13f30e37c136ee4a526463d84e2cde6c4328ed427af4c3f16d6f1d   <- NOT restored

$ python3 emc_fourth_cohort_quant.py --check          # T4 JSON-side drift
DRIFT: ['n_runs_read']
exit=1

$ python3 emc_fourth_cohort_quant.py                  # T5 write path
exit=0
$ sha256sum -c baseline.sha
emc-fourth-cohort-gene-counts.tsv: OK
emc-fourth-cohort-probe-counts.tsv: OK
$ # _generated_utc normalised, then hashed:
committed      : 44c81ae7f1fe8c418789ea5433f25adf98f4f739a34a61d1faaed405d8067f84
orig write path: 44c81ae7f1fe8c418789ea5433f25adf98f4f739a34a61d1faaed405d8067f84
repaired path  : 44c81ae7f1fe8c418789ea5433f25adf98f4f739a34a61d1faaed405d8067f84

$ /root/.local/bin/pytest tests/test_emc_fourth_cohort_quant.py -q     # T6
....................                                                     [100%]
20 passed in 0.11s
pytest exit=0

$ python3 emc_fourth_cohort_quant.py --selftest       # T7
selftest: 0 failure(s)
exit=0
```

One correction I made mid-run, recorded honestly: my first T5 deleted both TSVs before the write path, which produced a **false failure** — the probe TSV *is* the input checkpoint (`load_inputs()` rehydrates per-run counts from it, since the JSON cache stores runs with `counts` stripped), so deleting it removes the counts. Re-run from a pristine copy without deleting, T5 passes. The failure was my test setup, not the repair.

**RUN — part 2, the 8 rows in the live tree** (`cd /home/user/Rare-cancers`, HEAD `7d081218…`):

```
research/modalities/emc_adaptive_pazopanib.py          emc_adaptive_pazopanib: artifact matches                      EXIT=0
research/modalities/emc_icdo_contamination.py          OK: …/emc-icdo-contamination.json matches the generator       EXIT=0
research/modalities/emc_rt_bed_reappraisal.py          emc_rt_bed_reappraisal: artifact matches                      EXIT=0
research/modalities/emc_tissue_read_statistics.py      emc_tissue_read_statistics: verified, 100 board genes, …      EXIT=0
research/modalities/emc_scheduling_medians.py          emc_scheduling_medians: artifact matches                      EXIT=0
research/modalities/emc_fourth_cohort_route_readout.py OK — the committed readout reproduces from its inputs         EXIT=0
research/modalities/atr_part_d_proliferation_control.py OK: atr-part-d-proliferation-control.json reproduces …       EXIT=0
research/modalities/tcf12_offtarget_tissue_expression.py TCF12 off-target tissue-expression artifact is current      EXIT=0

$ git status --porcelain     # before AND after
[empty]
$ diff <(grep -v __pycache__ pre.modalities.sha) <(grep -v __pycache__ post.modalities.sha)
NONE — every tracked/non-bytecode file under research/modalities is byte-identical
$ git check-ignore -v research/modalities/__pycache__
.gitignore:9:__pycache__/	research/modalities/__pycache__
```

### The routed repair package — exact file, lines and text

**File: `research/modalities/emc_fourth_cohort_quant.py`** (single file; no other file changes). Applied and executed in `/tmp/claude-0/w14c/mod/`; **NOT applied to the tree**. Unified diff against the committed file (line numbers are the committed file's):

```diff
@@ -567,7 +567,7 @@
     return out
 
 
-def _write_probe_tsv(cache: dict, gene_of=None) -> str:
+def _probe_tsv_body_impl(cache: dict, gene_of=None) -> str:
     """THE CHECKPOINT ITSELF, and the raw deliverable. One row per probe, one column per run.
 
     ⛔ WHY THE COUNTS LIVE HERE AND NOT IN THE JSON CACHE. A JSON object keyed by 50-nt sequences,
@@ -586,7 +586,25 @@
         g = (gene_of or {}).get(pr) or "unassigned"
         lines.append(pr + "\t" + g + "\t" +
                      "\t".join(str(runs[a]["counts"].get(pr, 0)) for a in accs))
-    body = "\n".join(lines) + "\n"
+    return "\n".join(lines) + "\n"
+
+
+def _probe_tsv_body(cache: dict, gene_of=None) -> str:
+    """The probe table's exact bytes, COMPUTED AND RETURNED WITHOUT WRITING ANYTHING.
+
+    ⛔ WHY THIS IS SEPARATE FROM THE WRITE. `--check` must compare the COMMITTED table
+    against what the inputs imply. A checker that writes first and hashes second can only
+    ever agree with itself: it silently repairs the drift it was asked to detect. Keep this
+    function write-free.
+    """
+    return _probe_tsv_body_impl(cache, gene_of)
+
+
+def _write_probe_tsv(cache: dict, gene_of=None) -> str:
+    """Persist the probe table atomically. The ONLY writer of `PROBE_TSV`."""
+    body = _probe_tsv_body(cache, gene_of)
+    if not body:
+        return ""
     tmp = PROBE_TSV + ".tmp"
     with open(tmp, "w", encoding="utf-8") as fh:
         fh.write(body)
@@ -736,7 +754,12 @@
 # ------------------------------------------------------------------ derive
 
 
-def derive(cache: dict | None = None) -> dict:
+def derive(cache: dict | None = None, *, write: bool = True,
+           bodies: dict | None = None) -> dict:
+    """`write=False` computes the two TSV bodies without touching disk; `bodies`, when a
+    dict is passed, receives {path: exact body} so `--check` can compare against what is
+    COMMITTED rather than against what it just wrote (CLAUDE.md §6: never change a guard just
+    to hide an error -- and never let a guard repair the drift it is supposed to report)."""
     cache = cache if cache is not None else load_inputs()
     runs = cache.get("runs", {})
     read_runs = {k: v for k, v in runs.items() if v.get("counts")}
@@ -814,7 +837,9 @@
     }
     accs = sorted(read_runs)
     if read_runs:
-        body = _write_probe_tsv(cache, p2g)
+        body = _write_probe_tsv(cache, p2g) if write else _probe_tsv_body(cache, p2g)
+        if bodies is not None:
+            bodies[PROBE_TSV] = body
         out["probe_counts_written_to"] = os.path.basename(PROBE_TSV)
         out["probe_counts_sha256"] = hashlib.sha256(body.encode()).hexdigest()
         out["probe_counts_n_rows"] = len(body.strip().split("\n")) - 1
@@ -827,8 +852,11 @@
         for g in sorted(gene_counts):
             lines.append(g + "\t" + "\t".join(str(gene_counts[g].get(a, 0)) for a in accs))
         body = "\n".join(lines) + "\n"
-        with open(GENE_TSV, "w", encoding="utf-8") as fh:
-            fh.write(body)
+        if write:
+            with open(GENE_TSV, "w", encoding="utf-8") as fh:
+                fh.write(body)
+        if bodies is not None:
+            bodies[GENE_TSV] = body
         out["gene_counts_sha256"] = hashlib.sha256(body.encode()).hexdigest()
         out["gene_counts_n_rows"] = len(gene_counts)
         out["⛔ gene_counts_units"] = (
@@ -930,19 +958,28 @@
         print(json.dumps(phase_map(budget_s=args.budget_s), indent=1))
         return 0
 
-    out = derive()
     if args.check:
+        bodies: dict = {}
+        out = derive(write=False, bodies=bodies)
         if not os.path.exists(ART):
             print("--check: no committed artifact to compare against")
             return 1
         with open(ART, encoding="utf-8") as fh:
             old = json.load(fh)
         drift = [k for k in ("probe_gate", "n_runs_read", "n_probes_common_to_every_read_run",
-                             "n_genes_with_at_least_one_assigned_probe", "gene_counts_sha256")
+                             "n_genes_with_at_least_one_assigned_probe",
+                             "gene_counts_sha256", "probe_counts_sha256")
                  if old.get(k) != out.get(k)]
+        # ⛔ the COMMITTED bytes, not the bytes we just computed: the JSON can only ever
+        # agree with a body derived in the same process, so compare the tables themselves.
+        for path, body in sorted(bodies.items()):
+            on_disk = open(path, "rb").read() if os.path.exists(path) else None
+            if on_disk != body.encode():
+                drift.append(os.path.basename(path))
         print("DRIFT:" if drift else "no drift:", drift or "the derive half reproduces offline")
         return 1 if drift else 0
 
+    out = derive()
     tmp = ART + ".tmp"
     with open(tmp, "w", encoding="utf-8") as fh:
         json.dump(out, fh, indent=1)
```

Design notes for the integrator: `write`/`bodies` are **keyword-only with write-preserving defaults**, so the three existing positional `Q.derive(cache)` call sites in `research/modalities/tests/test_emc_fourth_cohort_quant.py` are unaffected — verified by T6 (20 passed). `_write_probe_tsv` keeps its name and signature, so `save_inputs()` (line 620) and `phase_probe` are unaffected.

**`PROPOSED (NOT RUN)` — one cosmetic simplification available:** `_probe_tsv_body_impl` + the one-line `_probe_tsv_body` wrapper can collapse into a single `_probe_tsv_body` (rename the impl, delete the wrapper). I kept the wrapper because that is the exact form I executed all seven acceptance tests against; the collapsed form is equivalent but **has not been run**, so the integrator should either apply the diff above verbatim or re-run T1-T7 after collapsing.

**`PROPOSED (NOT RUN)` — acceptance test for the integrator**, mirroring `test_a_guard_that_cannot_fail_is_not_a_guard.py`. I did not add it to the tree and did not run it as a pytest module (its three assertions are exactly T1/T2/T5, which I *did* run as shell commands and quote above):

```python
def test_check_cannot_repair_the_drift_it_must_report(tmp_path, monkeypatch):
    """⛔ --check must COMPARE, never write. Corrupt a committed TSV: the guard must exit 1
    and leave the corruption on disk, not restore it and print 'no drift'."""
    # copy the 6 committed inputs into tmp_path, monkeypatch Q.HERE-derived paths, then:
    assert Q.main(["--check"]) == 0                      # clean tree passes
    before = open(Q.GENE_TSV, "rb").read()
    corrupt(Q.GENE_TSV)                                  # bump one integer
    corrupted = open(Q.GENE_TSV, "rb").read()
    assert Q.main(["--check"]) == 1                      # the guard can FAIL
    assert open(Q.GENE_TSV, "rb").read() == corrupted    # and did NOT silently restore it
    assert Q.main([]) == 0 and open(Q.GENE_TSV, "rb").read() == before   # write path unchanged
```

**Explicitly NOT done, per the constraints:** no row added to `scripts/preflight.sh`; `scripts/preflight.sh` not run; nothing applied to the Git working tree; the non-blocking `|| echo` at `.github/workflows/emc-expression-datasets.yml:1066` left exactly as it stands.

## Limitations

- **Tooling only. No scientific conclusion, no EMC conclusion change, no clinical claim.** A generator reproducing its artifact says the arithmetic is stable; it says nothing about whether the artifact is correct, whether its inputs are sound, or whether any of it bears on patient care. `emc_icdo_contamination.py` exiting 0 is a statement about bytes, not about ICD-O classification.
- The tree **moved under me** (`47aac85f` → `7d081218`), so parts 1 and 2 were measured at different commits. The specific generator is byte-identical to the frozen `93b` corpus copy, but I cannot assert that nothing else relevant changed between those two commits.
- Part 1 ran in a **6-file scratch copy**, not a full checkout. That is the correct isolation for a corruption experiment, but it means only the code paths those 6 files reach were exercised — the network phases (`--phase probe/quant/map`) were never run and are untested by me.
- The repair is proven against **two corruption modes** (an integer in the gene table, a gene label in the probe table) plus one JSON-key drift. It is not proven against every possible corruption; in particular a corruption that changes an *input* in a way the derive step reproduces exactly would still pass, which is inherent to reproduce-from-inputs checking and not a defect of the repair.
- Repairing the guard does **not** enforce it: its only caller discards the exit code, and no preflight row references it. Whether to wire it is a decision I was told not to make.
- `_generated_utc` makes the JSON not bit-reproducible. I normalised it to prove value-equality; I did not investigate or change it.
- Running the 8 checks in the live tree created 5 untracked `.pyc` files. Gitignored, no tracked content touched, left in place.
- Model identity is **SELF-REPORT, NOT INDEPENDENTLY VERIFIED**; no environment variable names a served model.

## Stop condition

Set: *the fake guard reproduced, and its repair proven by execution to fail on corruption and pass when clean; the 8 rows re-verified against the real tree with per-row exit codes and any divergence from W14b named.*

**MET.** The fake guard was reproduced in two independent legs (gene table silently restored + `no drift` + exit 0; probe table silently restored, its sha not even compared). The repair was authored, applied in `/tmp`, and executed: exit **1** on each of two corruptions with the corruption **left in place**, exit **0** clean, exit **1** still on JSON drift, all 20 module tests passing, `--selftest` passing, and every committed value reproduced identically once the pre-existing timestamp is normalised. All 8 `GUARDED-NOT-ENFORCED` rows re-verified against the real tree: **8/8 exit 0, 8/8 wrote nothing to tracked content, 0/8 diverge from W14b's scratch result** — so W14b's flagged `.git`-absence limitation did not affect any of them. Nothing was applied to the tree; `git status --porcelain` is empty.

## Tool-call and wall-clock count actually used

**33 tool calls** (all `Bash`; no network, no subagents, no paid API, no GPU). **Wall clock 02:31:01Z → 02:36:25Z = 5 minutes 24 seconds**, well inside the ~40-minute / ~40-call target.

## Next concrete action

**Route the proven diff above to a writer to apply to `research/modalities/emc_fourth_cohort_quant.py`, together with the acceptance test as a new case in `research/modalities/tests/test_emc_fourth_cohort_quant.py`, and — separately and only if the coordinator decides enforcement is wanted — change `.github/workflows/emc-expression-datasets.yml:1066-1067` from `--check || echo "…non-blocking…"` to a blocking `--check`.** These are two decisions, not one: the first is a strict repair that cannot change any committed value (proven), the second turns a currently-decorative workflow step into a gate that can now actually go red, and that is a policy call for the coordinator. I recommend the first unconditionally and flag the second for a decision. The eight `GUARDED-NOT-ENFORCED` rows are now confirmed green against the real tree and are ready for gate wiring whenever someone owns that; I did not wire them because the brief forbade touching `scripts/preflight.sh`.
