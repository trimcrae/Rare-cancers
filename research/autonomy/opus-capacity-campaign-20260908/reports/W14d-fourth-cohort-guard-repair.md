> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Stop condition met. Report follows.

---

## Worker

**W14d**, lane 14 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` start: `Tue Sep  8 02:45:49 UTC 2026`. `date -u` end: `Tue Sep  8 02:48:51 UTC 2026`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; **no model field present**; long proxy exclusion lists elided as marked, everything else verbatim):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=localhost,127.0.0.1,::1,...,api.anthropic.com,...   [proxy exclusion list; matched on "anthropic"]
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

**HEAD actually read: `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`** at start and unchanged at end (`git rev-parse HEAD` both times). This is neither the `92abbcb…` named as the frozen read commit in `COMMON-BRIEF.md` nor either of the commits W14c saw (`47aac85f`, `7d081218`) — the coordinator is still committing collected reports while workers run. `git status --porcelain` was **empty (0 lines) at start and empty at end**. Nothing was written into `/home/user/Rare-cancers`; all execution was in `/tmp/claude-0/w14d/`.

## Question

**What is the smallest correct repair to `research/modalities/emc_fourth_cohort_quant.py --check`, and does it actually discriminate?**

**First, the honest disposition: this question is largely already answered, by W14c, on this exact file.** My dispatch prompt said "W14c proved a repair by execution for a *related* guard". That is wrong. `W14c-fake-guard-repair-proof.md:81` states W14c's question 1 as *this file*, and `:268-379` contains a full unified diff for `research/modalities/emc_fourth_cohort_quant.py` proven by seven executed acceptance tests (T1–T7). I did not discover this defect and I am not claiming it as new.

What remained genuinely open, and what I therefore pursued:
1. **Independent replication.** W14c's proof is single-worker. A repair nobody else has reproduced is one worker's word.
2. **Is W14c's repair actually the *smallest* correct one?** W14c's diff splits `_write_probe_tsv` into three functions and adds two keyword parameters to `derive`, and W14c itself flagged a collapsed form as `PROPOSED (NOT RUN)`. Whether a strictly smaller repair passes the same acceptance set was untested.
3. **A third drift class W14c did not test.** W14c drifted the gene TSV's integers and the probe TSV's *label* column. It did not drift the probe TSV's *counts* — which matters because `load_inputs()` rehydrates the counts **from that same TSV**, so the file is simultaneously an artifact and an input, and byte comparison alone cannot see that drift.
4. Task items 3 and 4 (JSON path soundness verified rather than assumed; preflight row impact enumerated by name).

## Prior-work check

```
grep -n -i "fourth_cohort\|emc_fourth" research/autonomy/opus-capacity-campaign-20260908/reports/*.md
grep -rn "fourth_cohort_quant" --include=*.py --include=*.yml --include=*.sh .   # excluding .git
grep -n "fourth_cohort" scripts/preflight.sh
ls research/modalities/tests/ | grep -i fourth
```

What they showed:
- `W14b-guard-coverage-sweep.md:120,126,232,519` — this file is the single true FAKE-GUARD of 512 write-capable scripts; W14b diagnosed but did not repair it.
- `W14c-fake-guard-repair-proof.md:81,268-379` — **W14c already authored and executed a repair to this same file.** I read it in full before writing mine, and I say plainly that my repair is a smaller variant of the same idea, not an independent discovery.
- `W23-cross-output-synthesis-packet.md:183,411` — names this repair as the next executable action and asserts "the JSON path is already sound". I verified that by execution rather than assuming it (below).
- **The repair is still not in the tree.** The live `emc_fourth_cohort_quant.py` at `3f5fc95d…` sha256 `c5180c11a57463337d023fda58fb5516833d1eb4e4787095e15c35af5eb5965f` still contains the unguarded writes at lines 590-593 and 830-831 and `out = derive()` at line 933. W14c's diff has **not** been applied.

Closed items I confirmed I am not replaying: no EMC scientific conclusion of any kind, no ICD-O/classification reading, no Brenca/Hofvander/Davis route, no lane-11 source-index file, no network call, no other generator repaired (W14b's 64 other FAKE-GUARD rows untouched), no `scripts/preflight.sh` row added, `scripts/preflight.sh` **not run**.

## Method / inputs

- Live checkout `/home/user/Rare-cancers` at HEAD `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`, read-only. I did not read the frozen corpus this run; W14c already established this file is byte-identical between the live tree and the `93b` corpus copy, and my own sha of the live file matches the artifact shas W14c reported.
- **All execution in `/tmp/claude-0/w14d/`.** Six files copied out of `research/modalities/`: the generator plus `emc-fourth-cohort-quant.json`, `emc-fourth-cohort-quant-inputs.json`, `emc-fourth-cohort-gene-counts.tsv`, `emc-fourth-cohort-probe-counts.tsv`, `emc-sra-study-inputs.json`; plus `tests/test_emc_fourth_cohort_quant.py`. `HERE = os.path.dirname(os.path.abspath(__file__))` (line 64) makes every path resolve inside the scratch copy, so no run could target the tree.
- Interpreter CPython **3.11.15** (`/usr/local/bin/python3`); test runner **pytest** at `/root/.local/bin/pytest`. Linux, no network, no paid API, no GPU.
- Baseline shas of the six copied files recorded before anything ran (`/tmp/claude-0/w14d/baseline.sha`).

## Result

### 1. The defect, reproduced by execution (`PRIMARY`)

The mechanism, quoted with `file:line` from the committed file at `3f5fc95d…`:

- `research/modalities/emc_fourth_cohort_quant.py:933` — `    out = derive()` runs **before** the `--check` branch at `:934`.
- `:817` — `        body = _write_probe_tsv(cache, p2g)` inside `derive()`, which at `:590-593` does `tmp = PROBE_TSV + ".tmp"` / `fh.write(body)` / `os.replace(tmp, PROBE_TSV)` — **this line rewrites the committed `emc-fourth-cohort-probe-counts.tsv`**.
- `:830-831` — `        with open(GENE_TSV, "w", encoding="utf-8") as fh:` / `            fh.write(body)` — **this line rewrites the committed `emc-fourth-cohort-gene-counts.tsv`**.
- `:819` and `:832` then hash those just-written bodies into `out["probe_counts_sha256"]` / `out["gene_counts_sha256"]`, and `:940-942` compares `out` against the committed JSON. The comparison is process-internal and self-agreeing.
- `:940-941` — the drift key tuple contains `gene_counts_sha256` but **not** `probe_counts_sha256`, so the probe table's hash was not compared at all.

| # | Drift injected (one file at a time, from the committed bytes) | Original `--check` exit | File after `--check` | Grade |
|---|---|---|---|---|
| D1 | gene TSV, row 2 integer `491` → `1000491` (sha `2168ab58…`) | **0**, prints `no drift` | **silently restored** to `8aa3064a…` | PRIMARY |
| D2 | probe TSV, row 2 `assigned_gene` → `BOGUS_GENE_XYZ` (sha `f273b0c0…`) | **0**, prints `no drift` | **silently restored** to `c689e0fd…` | PRIMARY |
| D3 | probe TSV, row 2 first count `0` → `1000000` (sha `e7b31a6e…`) | **0**, prints `no drift` | left corrupt (`e7b31a6e…`) | PRIMARY |

D1 and D2 replicate W14c's two legs exactly, including the same intermediate shas — an independent confirmation.

**D3 is new and is a distinct sub-defect.** The count drift is *not* restored, because `load_inputs()` rehydrates per-run counts **from the probe TSV itself** (`:552-566`), so `derive()` regenerates a body that reproduces the drift bit-for-bit. A byte-only comparison can therefore never see it. It is invisible to the original guard for a second reason too: `probe_counts_sha256` was absent from the drift key list. This is why adding that one key is load-bearing, not cosmetic.

### 2. The smallest correct repair, and whether it discriminates (`PRIMARY`)

My repair is **one file, four edits, 92 diff lines including context** — smaller than W14c's (no function split, one keyword parameter instead of two, no `bodies` dict). It adds a `write` switch to `_write_probe_tsv` and `derive`, and in `--check` hashes the **committed bytes off disk before `derive()` is called at all**, comparing them against the shas `derive(write=False)` computes in memory.

| Acceptance test | Expected | Observed | Grade |
|---|---|---|---|
| T1 clean committed inputs | exit 0, nothing written | `no drift: the derive half reproduces offline`, **exit 0**; all three artifact shas unchanged | PRIMARY |
| T2 D1 gene-TSV drift | exit ≠ 0, corruption left in place | `DRIFT: ['emc-fourth-cohort-gene-counts.tsv']` **exit 1**, file still `2168ab58…` | PRIMARY |
| T3 D2 probe-label drift | exit ≠ 0, corruption left in place | `DRIFT: ['emc-fourth-cohort-probe-counts.tsv']` **exit 1**, file still `f273b0c0…` | PRIMARY |
| T4 D3 probe-count drift | exit ≠ 0, corruption left in place | `DRIFT: ['probe_counts_sha256']` **exit 1**, file still `e7b31a6e…` | PRIMARY |
| T5 JSON-side drift (`n_runs_read` 12 → 19) | exit ≠ 0 (no regression) | `DRIFT: ['n_runs_read']` **exit 1** | PRIMARY |
| T6 write path (no `--check`) | committed artifacts reproduced | exit 0; **both TSVs bit-identical** to committed (`8aa3064a…`, `c689e0fd…`); JSON differs in **exactly one key**, `_generated_utc` | PRIMARY |
| T7 module's own test file | all pass | **20 passed**, pytest exit 0 | PRIMARY |
| T8 `--selftest` | exit 0 | `selftest: 0 failure(s)`, exit 0 | PRIMARY |

**The negative control is satisfied on all three drift classes, one file at a time, and in every case the corruption is left on disk rather than repaired.** Note T4 is caught by the *JSON key* path, not the byte path — exactly as the D3 mechanism predicts.

### 3. Is the JSON comparison path already sound? **Yes — verified, not assumed** (`PRIMARY`)

W23 asserts it; I executed it. `derive()` never writes `ART` (`emc-fourth-cohort-quant.json`); `ART` is written only at `:947-951`, after the `--check` branch has returned. So `:938-939` reads genuinely committed JSON. Executed on the **unrepaired** script with `n_runs_read` drifted 12 → 19: `DRIFT: ['n_runs_read']`, **exit 1**, JSON left drifted. Same on the repaired script. The JSON half was always a real check; only the two `.tsv` halves were fake. My repair leaves the JSON path's semantics untouched and only adds `probe_counts_sha256` to its key tuple.

### 4. Does the repair change any committed artifact byte? **No** (`PRIMARY`)

`sha256sum -c` against the pre-run baseline over all six copied files: the only mismatch is `emc_fourth_cohort_quant.py` itself (the repair). All five artifacts byte-identical. In the tree: `git status --porcelain` empty at start and end; the tree was never a write target.

### 5. Preflight impact: **none. Zero of the 18 rows** (`PRIMARY`)

`grep -n "fourth_cohort" scripts/preflight.sh` → **no match**. The 18 `--check` rows are the loop body at `scripts/preflight.sh:847-864` (18 lines, confirmed by `wc -l`):

`submission_tables.py` · `claim_coverage.py` · `submission_citations.py` · `submission_metrics.py` · `aso_sequence_manifest.py` · `aso_journal_tables.py` · `aso_offtarget_duplex_energy.py` · `submission_packet.py` · `vaccine_path_tables.py` · `aso_archive_manifest.py` (`--check-archive`, not `--check`) · `aso_deposit_drift.py` · `emc_condensate_report.py` · `atr_hrd_sarcoma_series.py` · `single_slot_identity.py` · `instrument_census.py` · `scripts/trigger_scan.py` · `scripts/citation_debt.py` · `scripts/news_match.py`.

**`emc_fourth_cohort_quant.py` is not among them and is not referenced anywhere else in `scripts/preflight.sh`.** The repair is a single file that no preflight row imports or invokes, so it cannot change any of the 18 outcomes. Its only caller anywhere is `.github/workflows/emc-expression-datasets.yml:1065-1066`, which is **non-blocking** — verbatim:

```yaml
          python research/modalities/emc_fourth_cohort_quant.py --check \
            || echo "--check reported drift; non-blocking, but READ IT"
```

So repairing the guard does not by itself enforce it. That is W14c's leg-3 finding, independently confirmed at this HEAD, and wiring it is a coordinator decision I did not take.

### The complete repaired `--check` function body, inline

This is the whole of `main()`'s check branch as executed (replacing committed `:933-943`), plus the two enabling edits it depends on. **Not written into the tree.**

```python
    if args.check:
        if not os.path.exists(ART):
            print("--check: no committed artifact to compare against")
            return 1
        # ⛔ hash what is COMMITTED, before anything is regenerated.
        on_disk = {key: (hashlib.sha256(open(path, "rb").read()).hexdigest()
                         if os.path.exists(path) else None)
                   for key, path in (("gene_counts_sha256", GENE_TSV),
                                     ("probe_counts_sha256", PROBE_TSV))}
        with open(ART, encoding="utf-8") as fh:
            old = json.load(fh)
        out = derive(write=False)
        drift = [k for k in ("probe_gate", "n_runs_read", "n_probes_common_to_every_read_run",
                             "n_genes_with_at_least_one_assigned_probe",
                             "gene_counts_sha256", "probe_counts_sha256")
                 if old.get(k) != out.get(k)]
        drift += [os.path.basename(path) for key, path in (("gene_counts_sha256", GENE_TSV),
                                                           ("probe_counts_sha256", PROBE_TSV))
                  if key in out and on_disk[key] != out[key]]
        print("DRIFT:" if drift else "no drift:", drift or "the derive half reproduces offline")
        return 1 if drift else 0

    out = derive()
```

The three supporting edits, exactly as executed (committed line numbers):

```diff
@@ -570 (def _write_probe_tsv)
-def _write_probe_tsv(cache: dict, gene_of=None) -> str:
+def _write_probe_tsv(cache: dict, gene_of=None, *, write: bool = True) -> str:
@@ -589,593
     body = "\n".join(lines) + "\n"
-    tmp = PROBE_TSV + ".tmp"
-    with open(tmp, "w", encoding="utf-8") as fh:
-        fh.write(body)
-    os.replace(tmp, PROBE_TSV)
+    if write:   # ⛔ write=False computes the body only: --check must never write.
+        tmp = PROBE_TSV + ".tmp"
+        with open(tmp, "w", encoding="utf-8") as fh:
+            fh.write(body)
+        os.replace(tmp, PROBE_TSV)
     return body
@@ -739 (def derive)
-def derive(cache: dict | None = None) -> dict:
+def derive(cache: dict | None = None, *, write: bool = True) -> dict:
+    """`write=False` derives the artifact WITHOUT touching either committed .tsv, so that
+    `--check` can compare the bytes already on disk instead of bytes it has just written.
+    A checker that regenerates first can only ever agree with itself (CLAUDE.md §6)."""
@@ -817
-        body = _write_probe_tsv(cache, p2g)
+        body = _write_probe_tsv(cache, p2g, write=write)
@@ -830,831
-        with open(GENE_TSV, "w", encoding="utf-8") as fh:
-            fh.write(body)
+        if write:
+            with open(GENE_TSV, "w", encoding="utf-8") as fh:
+                fh.write(body)
```

`write` is keyword-only with a write-preserving default, so the three existing positional `Q.derive(cache)` call sites (`research/modalities/tests/test_emc_fourth_cohort_quant.py:138,156,182`) are unaffected — confirmed by T7 (20 passed). `_write_probe_tsv` keeps its name and its two positional parameters, so `save_inputs()` and `phase_probe` are unaffected.

**Relation to W14c's diff:** both are correct and both pass the same acceptance set. Mine is smaller (no `_probe_tsv_body`/`_probe_tsv_body_impl` split, no `bodies` out-parameter) because comparing on-disk **sha256** against `out["*_sha256"]`, which `derive()` already computes, makes carrying the 18 MB body out of `derive()` unnecessary. Either is applicable; the integrator should apply **one**, not both.

## Validation evidence

Environment for every run: CPython 3.11.15, pytest at `/root/.local/bin/pytest`, Linux, no network, working directories under `/tmp/claude-0/w14d/`.

**RUN — defect reproduced, original script:**
```
===== ORIGINAL SCRIPT / drift=gene_int on emc-fourth-cohort-gene-counts.tsv =====
drifted gene_int row2 head: AARS1	1000491	987	359	435	683	61	107	888	471	448	446	138
sha after drift : 2168ab583b9f2a209e7c0cdd674f3595a30651adc8301946fdbfac537cf8eeaa
no drift: the derive half reproduces offline
EXIT=0
sha after --check: 8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc
===== ORIGINAL SCRIPT / drift=probe_label on emc-fourth-cohort-probe-counts.tsv =====
sha after drift : f273b0c07e13f30e37c136ee4a526463d84e2cde6c4328ed427af4c3f16d6f1d
no drift: the derive half reproduces offline
EXIT=0
sha after --check: c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc
===== ORIGINAL SCRIPT / drift=probe_count on emc-fourth-cohort-probe-counts.tsv =====
sha after drift : e7b31a6ec554fa39db1d6d82643e52c7da9e424431a414fcff02956d7173487b
no drift: the derive half reproduces offline
EXIT=0
sha after --check: e7b31a6ec554fa39db1d6d82643e52c7da9e424431a414fcff02956d7173487b
```

**RUN — repaired guard, clean and three negative controls:**
```
===== T1 repaired, CLEAN =====
no drift: the derive half reproduces offline
EXIT=0
8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc  emc-fourth-cohort-gene-counts.tsv
c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc  emc-fourth-cohort-probe-counts.tsv
1769b3f0ee01f1a640dabc6c4f36ce86630ff62f87249400e070a4638fcf5165  emc-fourth-cohort-quant.json
===== REPAIRED / drift=gene_int =====
DRIFT: ['emc-fourth-cohort-gene-counts.tsv']
EXIT=1
sha after --check: 2168ab58…  NOT RESTORED (good)
===== REPAIRED / drift=probe_label =====
DRIFT: ['emc-fourth-cohort-probe-counts.tsv']
EXIT=1
sha after --check: f273b0c0…  NOT RESTORED (good)
===== REPAIRED / drift=probe_count =====
DRIFT: ['probe_counts_sha256']
EXIT=1
sha after --check: e7b31a6e…  NOT RESTORED (good)
```

**RUN — JSON path, both scripts:**
```
n_runs_read committed: 12   (drifted to 19)
=== JSON-drift, script=orig ===  DRIFT: ['n_runs_read']  EXIT=1
=== JSON-drift, script=mod  ===  DRIFT: ['n_runs_read']  EXIT=1
```

**RUN — write path (T6) and module tests (T7/T8):**
```
WRITE_EXIT=0
8aa3064a97a496a8fa09ef4ae8e472a612318e49ea91d0daac915a3b8fa180cc  emc-fourth-cohort-gene-counts.tsv
c689e0fd4f5c8cda0f132cd8ce42f039f691bf94cb8d81d3f622886e2bdd26fc  emc-fourth-cohort-probe-counts.tsv
keys differing from committed JSON: ['_generated_utc']
   _generated_utc committed= '2026-09-02T17:42:53Z' regen= '2026-09-08T02:48:41Z'
normalised sha equal: True

$ /root/.local/bin/pytest tests/test_emc_fourth_cohort_quant.py -q
....................                                                     [100%]
20 passed in 0.24s
PYTEST_EXIT=0

$ python3 emc_fourth_cohort_quant.py --selftest
selftest: 0 failure(s)
EXIT=0

$ sha256sum -c baseline.sha        # six copied files
emc_fourth_cohort_quant.py: FAILED       <- the repair itself; all five artifacts OK
```

**RUN — tree state:** `git rev-parse HEAD` → `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d` (start and end); `git status --porcelain` → **empty, 0 lines, start and end**. Unlike W14c's part 2, I ran nothing inside `research/modalities`, so I created no `__pycache__` bytecode there.

**PROPOSED (NOT RUN):**
- The pytest acceptance case W14c drafted (`test_check_cannot_repair_the_drift_it_must_report`). My T1–T4 are its assertions executed as shell commands; I did not author it as a pytest module. A fourth assertion should be added for the D3 count-drift class.
- `scripts/preflight.sh` — **not run**, per the dispatch.
- The network phases (`--phase probe|quant|map`) — not exercised; the repair does not touch them.

## Limitations

- **Tooling only. No scientific finding, no EMC conclusion, no clinical claim of any kind.** A guard that can fail says nothing about whether the fourth-cohort counts are correct, whether the probe panel is adequate (see W20d/W20e on the intersection filter), or about any patient.
- **This is a replication and a minimisation of W14c's work, not a new discovery.** W14b diagnosed the defect; W14c authored the first proven repair. My additions are: independent reproduction at a different HEAD, a strictly smaller repair, a third drift class (D3), executed verification of the JSON path, and the named preflight-row enumeration.
- **Residual hole, inherent and not closed by any repair of this shape:** `emc-fourth-cohort-probe-counts.tsv` is both an artifact and the input checkpoint `load_inputs()` rehydrates from. A drift in its *counts* is reproduced exactly by `derive()`, so it is caught only because the committed **JSON's** recorded `probe_counts_sha256` disagrees. If someone drifted the probe TSV *and* regenerated the JSON, both would agree and the guard would pass. Reproduce-from-inputs checking cannot detect a consistent edit to its own input; only a Git-content or signature check could. I did not build one.
- Proven against three corruption modes plus one JSON-key drift, one file at a time. Not proven against arbitrary corruptions, and not proven under concurrent writers.
- Run in a **7-file scratch copy**, not a full checkout. Only the code paths those files reach were exercised.
- `_generated_utc` makes the JSON not bit-reproducible. I normalised it to prove value-equality and did not change it — a pre-existing property, `UNKNOWN` whether intended.
- I did not verify W14c's diff *and* mine against each other by running W14c's version; I read it and authored a smaller variant. **Both should not be applied.**
- Model identity is **SELF-REPORT, NOT INDEPENDENTLY VERIFIED**.

## Stop condition

Set up front: *the defect reproduced by execution on at least one drifted copy of each committed TSV with the rewriting line quoted at `file:line`; a repair executed to exit 0 clean and non-zero on each drift one at a time with the corruption left in place; the JSON path's soundness settled by execution; and the preflight rows enumerated by name.*

**MET, in full.** Defect reproduced on both TSVs (three drift classes, all exit 0, two silently restored). Repair executed: exit 0 clean, exit 1 on each of three drifts individually, corruption left on disk every time, 20/20 module tests pass, `--selftest` passes, both TSVs reproduced bit-identical by the write path, JSON identical apart from the pre-existing timestamp. JSON path confirmed sound by execution on both the original and repaired scripts. Zero of the 18 preflight `--check` rows touched. Nothing written to the tree; `git status --porcelain` empty at start and end.

## Tool-call and wall-clock count actually used

**14 tool calls** (all `Bash`; no network, no subagents, no paid API, no GPU spend, no skills). **Wall clock 02:45:49Z → 02:48:51Z = 3 minutes 2 seconds**, well inside the ~40-call / ~40-minute target.

## Next concrete action

**Have the coordinator pick exactly one of the two proven diffs — W14c's (`W14c-fake-guard-repair-proof.md:268-379`) or the smaller one above — and route it to a writer to apply to `research/modalities/emc_fourth_cohort_quant.py`, together with a new case in `research/modalities/tests/test_emc_fourth_cohort_quant.py` carrying all four drift assertions (gene integer, probe label, probe count, JSON key), then run the normal `scripts/preflight.sh` once on the settled tree.** Two workers have now independently proven this repair cannot change a committed byte; the only thing standing between the diff and the tree is a writer with authority, and every additional read-only worker sent at this file will re-derive the same answer. The separate and still-open decision is whether `.github/workflows/emc-expression-datasets.yml:1065-1066` should stop swallowing the exit code — that turns a decorative step into a gate that can go red, which is a policy call, not a repair. I recommend the application unconditionally and flag the enforcement wiring for a decision.
