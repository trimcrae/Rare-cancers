> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

## Worker

**W16d**, lane 16 refill, OPUS-CAPACITY-CAMPAIGN-20260908 — executed verification of W16c's finding **D12**.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** My system context states I am powered by Opus 5, exact model ID `claude-opus-5`. I did not observe the served model. No environment variable in this container names a served model; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:39:43 UTC 2026`
`date -u` at end: `Tue Sep  8 02:44:08 UTC 2026`

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (unmodified except the sed redaction; five very long proxy/JVM host-list lines — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` — marked elided rather than reprinted):

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=...                                            [elided: proxy host list]
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
GLOBAL_AGENT_NO_PROXY=...                               [elided: proxy host list]
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=...                                   [elided: JVM proxy/truststore flags]
NO_PROXY=...                                            [elided: proxy host list]
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=...                                  [elided: proxy host list]
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**HEAD actually read: `d3e9c4d87626b78ce41c1a8cbdb5b5584a7502b4`.** ⚠ This is **not** the frozen read commit `92abbcb905cacf07f14b238db50d1b98f6590374` named in `COMMON-BRIEF.md` §1 — the checkout has moved on (the coordinator has been committing wave reports). I read the live checkout at `d3e9c4d`, not the frozen corpus, for every executed result below; I record the discrepancy rather than papering over it. The one artifact my whole result turns on is byte-identical in both my scratch copy and the live tree: `emc-locoregional-eligibility.json` sha256 `ecd0c8c050012d535f2d43c09ed12dafa7e2a4c9ac830e279679ad900fdc3a36`.

**Git working tree: untouched by me.** `git status --porcelain` at end shows only the coordinator's own wave-log edit and other workers' report files (`W03d`, `W07d`, `W09d`, `W10e`, `W11d`, `W12c`, `W13e`, `W14c`, `W15e`). None of those paths is mine, I wrote none of them, and I ran no git write operation of any kind. All execution happened under `/tmp/claude-0/w16d/`.

---

## Question

**Is W16c's finding D12 true when executed — do the repository's own tests actually leave `94/259 = 36.3%` and `88/326 = 27.0%` unprotected — and what is the smallest pin that would close it?**

It is open because W16c reached D12 by **reading every assertion** in `research/modalities/tests/test_locoregional_eligibility.py` and labelled the conclusion explicitly as *"a static reading of the assertions, not an executed test result"*, listing it as its own Limitation 4: *"It should be confirmed by running the suite before being relied on."* A static reading of a test file is a hypothesis about what the file does. This task converts it into a measurement, and is deliberately independent of the `bishop2019` clause itself.

---

## Prior-work check

| Command | What it showed |
|---|---|
| `grep -rn "94/259\|88/326" --include=*.md --include=*.json --include=*.py .` | 19 hits. **Every hit outside `research/manuscripts/aso/fusion-junction-aso-working-record.md:1318` is a campaign report** (W13b, W16b, W16c). No tracked non-report file carries `88/326`. |
| `grep -rln "emc-locoregional-eligibility" --include=*.py .` | **Two files only** — `emc_site_curation.py` and the generator `emc_locoregional_eligibility.py`. **No test anywhere reads the artifact file.** |
| `grep -rln "locoregional" --include=*.py research scripts systems` | 10 files; the only two tests are `test_locoregional_eligibility.py` and `test_emc_surgical_quality.py`. |
| `grep -rn "emc-locoregional-eligibility" research/manuscripts/ systems/` | the working record, `systems/graph/{artifacts,routes}.json`, four generated `systems/views/` files. **Not in any deposit/archive manifest** — confirmed separately by `grep -rn "emc-locoregional\|emc_locoregional" research/manuscripts/aso_archive_manifest.py` returning nothing. |
| `grep -rn "27\.0%" --include=*.md . \| grep -v opus-capacity-campaign` | **empty.** |
| `ls .../reports/ \| grep -E 'W17e\|W16'` | W16, W16b, W16c, W17e present and read. |

**Closed items I confirmed I am not replaying.** I did not resolve or argue the `bishop2019` clause (W16c's package, owner's decision; `W13e-per-pool-overlap-readings.md` also landed on it this wave and I did not read into or duplicate it). I attempted no retrieval of `ussc2022`, SEER, or any source — `CLOSED-WORK.md` records `ussc2022` methods as unrecovered and I did not replay a denied route. I did not touch PUB-EMC-CLASSIFICATION or any Brenca route. I did not recompute, correct or endorse either pooled figure; both are transcribed exactly as committed. I read `systems/POLICY-evidence.md` (header, §1, and the §2 material the artifact's `_method` block cites) before writing anything about pooling.

**One prior-work correction, found by grep, that matters for the deliverable.** W16c states that *both* headline figures are "quoted in the ASO working record". **Only one is.** `36.3% (94/259, Wilson 95% CI 30.7–42.3%)` appears at `research/manuscripts/aso/fusion-junction-aso-working-record.md:1318`. `27.0%` / `88/326` appears in **no tracked prose document at all** outside campaign reports. This does not weaken D12 — it strengthens it, and it changes what the smallest pin can be for each figure (see Result R4).

---

## Method / inputs

| Input | Role |
|---|---|
| `/home/user/Rare-cancers` @ `d3e9c4d8` | the live checkout; read-only |
| `research/modalities/emc-locoregional-eligibility.json` | the committed artifact holding the two figures |
| `research/modalities/emc_locoregional_eligibility.py` | its generator (`wilson`, `pool`, `QUANTITIES`) |
| `research/modalities/tests/test_locoregional_eligibility.py` | the suite W16c read statically; 9 tests |
| `research/manuscripts/lint_consistency.py` (`check_artifact_figures`, `_dig_json`, `_nums`) | the repository's own gate, **imported**, not re-implemented |
| `research/manuscripts/pinned-figures.json` | 99 existing `artifact_figures` entries; candidate host |
| `research/manuscripts/aso/fusion-junction-aso-working-record.md:1318` | the one prose home of `36.3%` |
| `systems/POLICY-evidence.md` | read before any pooling statement |
| `/tmp/claude-0/w16d/{base,armP,armC1,armC2,armQ,armR}` | six `.git`-free scratch trees |

**Execution environment.** `pytest 9.1.1` at `/root/.local/bin/pytest` — a uv tool in its own venv. `python3 -c "import pytest"` → `ModuleNotFoundError: No module named 'pytest'`; the system interpreter has none. This is the same situation two other workers documented, and the same `pytest` binary the branch `scripts/preflight.sh` once recorded producing 36 phantom failures. ⛔ **Nothing below is a preflight result.** I did not run `scripts/preflight.sh`. Every failure I report is a **delta against a green baseline measured in the same tree with the same binary in the same invocation style**, which is what makes the phantom-failure history non-fatal here: a phantom would appear in the baseline too and cancel.

All runs used `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`, so no `__pycache__` or `.pytest_cache` was created anywhere, including in scratch.

**Scratch construction, as instructed.** `tar --exclude=./.git -cf /tmp/claude-0/w16d/tree.tar .` then extracted to `base`. `find /tmp/claude-0/w16d/base -maxdepth 3 -name '.git' -print` → **empty** (the four hits in a looser `-name '.git*'` glob were `.gitattributes`, `.github`, `.gitignore`, `.githooks`, none of which is a repository). The artifact sha256 matches the live tree byte-for-byte.

**Guard set.** Five test files — the eligibility suite plus every test that plausibly guards this artifact family: `test_locoregional_eligibility.py`, `test_emc_site_curation.py`, `test_emc_surgical_quality.py`, `test_lint_consistency.py`, `test_emc_care_delivery_evidence.py`. **72 tests.** Choosing a wider set than the one file makes the negative result harder to reach, not easier.

**Arms.**

| Arm | Perturbation | Expectation |
|---|---|---|
| `base` | none | green |
| `armP` | **the perturbation under test** — in `emc-locoregional-eligibility.json`, metastasis `94/259/36.3/30.7/42.3` → `77/241/32.0/26.4/38.0`; recurrence `88/326/27.0/22.5/32.1` → `70/300/23.3/18.9/28.4` | D12 predicts still green |
| `armC1` | **control that must be detected** — silently degrade `wilson()` to the normal approximation (drop the `d` denominator and the continuity term). This is the exact failure mode the suite's own docstring says it exists to catch | must go red |
| `armC2` | **second control that must be detected** — blank `what_would_supply_it` on a negative quantity in `QUANTITIES` | must go red |
| `armQ` | negative control for the *pin*: prose moved, artifact untouched | pin must fire |
| `armR` | disclosed-weakness probe: artifact `percent` 36.3 → **30.7**, a value already printed on the prose line | see limitation L3 |

---

## Result

### R1 — D12 is **TRUE**, and now measured, not read `PRIMARY (negative)`

| Arm | Result | Exit code | Verdict |
|---|---|---|---|
| `base` (72 tests) | `72 passed in 2.39s` | **0** | green baseline established |
| **`armP`** — both headline figures moved in the committed artifact | **`72 passed in 2.40s`** | **0** | ⛔ **NOTHING GOES RED. Zero delta from baseline.** |
| `armC1` — Wilson degraded | `5 failed, 67 passed` | **1** | ✅ control detected |
| `armC2` — negative quantity loses its escape route | `1 failed, 71 passed` | **1** | ✅ control detected |
| `armP`, eligibility file alone (9 tests) | `9 passed in 0.14s` | **0** | ⛔ undetected there too |

**W16c's static reading is confirmed by execution.** The two pooled figures can be moved by 4.3 and 3.7 percentage points, with both numerators, both denominators and all four Wilson bounds rewritten, and the repository's own eligibility, site-curation, surgical-quality, lint-consistency and care-delivery tests all pass with exit code 0. The controls prove the harness was capable of going red in the same invocation: it went red twice, for two structurally different injuries, in the same trees with the same binary. **The abort condition (control not detected) did not trigger.**

### R2 — *why* it is unprotected, which the static reading could not see `PRIMARY`

`test_locoregional_eligibility.py` never opens `emc-locoregional-eligibility.json`. Its 9 tests exercise `pool()`, `wilson()` and `QUANTITIES` against **synthetic fixtures** — `(5, 50)`, `(40, 50)`, `denom == 100`, `denom == 29`, `denom == 0`, and three closed-form Wilson pairs. Confirmed structurally: `grep -rln "emc-locoregional-eligibility" --include=*.py .` returns **only the generator and `emc_site_curation.py`** — **no test file at all**. The artifact is a write-only output as far as the test tier is concerned.

### R3 — the asymmetry the controls exposed, which is the real diagnosis `PRIMARY`

`armC1` did not only redden the Wilson unit test. It also reddened:

- `test_emc_site_curation.py::test_the_committed_artifact_matches_the_generator`
- `test_emc_surgical_quality.py::test_the_artifact_reproduces_from_its_generator`

**The repository already owns exactly the right mechanism** — a two-line test asserting `json.load(open(mod.OUT)) == mod.build()` — and applies it to `emc-site-curation.json` and to the surgical-quality artifact. It is **not** applied to `emc-locoregional-eligibility.json`. D12 is therefore not a missing idea; it is one missing application of a pattern already committed twice next door. (Those two neighbours reddened in `armC1` only because they *share the generator module* whose `wilson` I broke — which is itself evidence that they are live regeneration gates and this artifact has none.)

### R4 — the smallest pin, and it is **two different pins for the two figures** `PRIMARY`

| Figure | Prose home in the tracked tree | Can `artifact_figures` host it? |
|---|---|---|
| **`36.3%` / `94/259`** metastasis | ✅ `fusion-junction-aso-working-record.md:1318` | **YES** — delivered below, verified clean and negatively controlled |
| **`27.0%` / `88/326`** recurrence | ⛔ **NONE.** `grep -rn "88/326"` excluding campaign reports → **empty**; `grep -rn "27\.0%" --include=*.md` excluding campaign reports → **empty** | **NO.** `check_artifact_figures` needs a `must_appear_in` prose target and there is nothing to point at. Its smallest pin is the R3 regeneration test, not a figure pin. |

⚠ This is the correction to W16c's framing: only one of the two figures is quoted in the ASO working record, so only one is addressable by the mechanism W17e used.

**W17e's two `_dig_json` blockers do NOT bite here.** I checked by execution, not by reading. All five keys are plain dotted paths with no dots-inside-key-names and no list indices:

```
DIG who_ever_metastasises.percent -> 36.3
DIG who_ever_metastasises.events -> 94
DIG who_ever_metastasises.denom -> 259
DIG who_ever_metastasises.ci95_lo_percent -> 30.7
DIG who_ever_metastasises.ci95_hi_percent -> 42.3
```

(The artifact *does* contain dotted and emoji-prefixed keys elsewhere — `per_cohort_percent."Localised at diagnosis, surgically treated"`, `⛔_what_the_registry_cannot_answer.*` — and those would hit W17e's F1 exactly. The five fields the pin needs sit outside that trap. No bracket support is required and no tooling change is requested.)

One more mechanism note: the working record is **not** in `pinned-figures.json`'s `targets` list, but `check_artifact_figures` reads `must_appear_in` paths directly via `_read_lines` and never consults `targets`. Verified by the clean run below — no `A-target-missing` finding.

### R5 — the deliverable: candidate `artifact_figures` entries, routed as data `PRIMARY`

**Five entries, all verified clean by the repository's own `check_artifact_figures` against the current tree at `d3e9c4d8` (0 findings), and all five shown to redden in both drift directions.** ⛔ **This is data routed to the PUB-ASO / manuscript owner. I did not author it into `pinned-figures.json` or any other file, and I make no recommendation about whether to adopt it.**

```json
{
  "artifact_figures": [
    {
      "id": "emc_locoregional_metastasis_pct",
      "description": "The pooled during-follow-up distant-metastasis proportion the ASO working record quotes is a reading of emc-locoregional-eligibility.json, never a typed number. Added because no test bound it: an executed differential (W16d) moved 94/259/36.3 in the artifact and the whole eligibility/site-curation/surgical-quality/lint guard set stayed green at exit 0.",
      "artifact": "research/modalities/emc-locoregional-eligibility.json",
      "key": "who_ever_metastasises.percent",
      "format": "{:.1f}%",
      "tolerance": 0.05,
      "context": "re-derived here: \\*\\*[\\d.]+%\\*\\* \\(\\d+/\\d+, Wilson 95% CI",
      "must_appear_in": ["research/manuscripts/aso/fusion-junction-aso-working-record.md"],
      "regenerate": "python3 research/modalities/emc_locoregional_eligibility.py --write, then update the quoted figure IN THE SAME COMMIT"
    },
    {
      "id": "emc_locoregional_metastasis_events",
      "description": "Numerator of the same pooled proportion, pinned so the fraction cannot drift away from the percent.",
      "artifact": "research/modalities/emc-locoregional-eligibility.json",
      "key": "who_ever_metastasises.events",
      "format": "{:.0f}",
      "tolerance": 0.05,
      "context": "re-derived here: \\*\\*[\\d.]+%\\*\\* \\(\\d+/\\d+, Wilson 95% CI",
      "must_appear_in": ["research/manuscripts/aso/fusion-junction-aso-working-record.md"],
      "regenerate": "python3 research/modalities/emc_locoregional_eligibility.py --write"
    },
    {
      "id": "emc_locoregional_metastasis_denom",
      "description": "Denominator of the same pooled proportion.",
      "artifact": "research/modalities/emc-locoregional-eligibility.json",
      "key": "who_ever_metastasises.denom",
      "format": "{:.0f}",
      "tolerance": 0.05,
      "context": "re-derived here: \\*\\*[\\d.]+%\\*\\* \\(\\d+/\\d+, Wilson 95% CI",
      "must_appear_in": ["research/manuscripts/aso/fusion-junction-aso-working-record.md"],
      "regenerate": "python3 research/modalities/emc_locoregional_eligibility.py --write"
    },
    {
      "id": "emc_locoregional_metastasis_ci_lo",
      "description": "Wilson 95% lower bound quoted on the same line.",
      "artifact": "research/modalities/emc-locoregional-eligibility.json",
      "key": "who_ever_metastasises.ci95_lo_percent",
      "format": "{:.1f}%",
      "tolerance": 0.05,
      "context": "re-derived here: \\*\\*[\\d.]+%\\*\\* \\(\\d+/\\d+, Wilson 95% CI",
      "must_appear_in": ["research/manuscripts/aso/fusion-junction-aso-working-record.md"],
      "regenerate": "python3 research/modalities/emc_locoregional_eligibility.py --write"
    },
    {
      "id": "emc_locoregional_metastasis_ci_hi",
      "description": "Wilson 95% upper bound quoted on the same line.",
      "artifact": "research/modalities/emc-locoregional-eligibility.json",
      "key": "who_ever_metastasises.ci95_hi_percent",
      "format": "{:.1f}%",
      "tolerance": 0.05,
      "context": "re-derived here: \\*\\*[\\d.]+%\\*\\* \\(\\d+/\\d+, Wilson 95% CI",
      "must_appear_in": ["research/manuscripts/aso/fusion-junction-aso-working-record.md"],
      "regenerate": "python3 research/modalities/emc_locoregional_eligibility.py --write"
    }
  ]
}
```

The `context` regex is deliberately anchored on the sentence shape rather than on the digits, so the entries survive a legitimate regeneration and fire only on drift. It is scoped by `must_appear_in` to the working record, which also keeps it clear of the unrelated literal `36.3` in `emc-fusion-partner-stratification.md` (a "36.3-point gap" between two survival percentages — nothing to do with this pool).

**The second, non-figure pin — `PROPOSED (NOT RUN)`.** For the recurrence figure, and for the artifact as a whole, the smallest correct repair is the R3 pattern already committed twice in this same test directory: `assert json.load(open(mod.OUT)) == mod.build()`, in `test_locoregional_eligibility.py`, mirroring `test_emc_site_curation.py::test_the_committed_artifact_matches_the_generator`. ⛔ **I did not author it.** It is a new test file assertion, which is a tooling-owner change and outside a read-only lane; and I did not execute it, so I make no claim about whether the artifact currently reproduces from its generator at `d3e9c4d8` — **that is UNKNOWN and is the obvious successor measurement.**

---

## Validation evidence

**RUN 1 — green baseline.** Environment: `/tmp/claude-0/w16d/base` (tar copy, no `.git`), `pytest 9.1.1` at `/root/.local/bin/pytest`, `PYTHONDONTWRITEBYTECODE=1`.
Command: `pytest research/modalities/tests/test_locoregional_eligibility.py -p no:cacheprovider -q`
```
.........                                                                [100%]
9 passed in 0.14s
```
**EXIT=0**

**RUN 2 — four-arm differential, 72 tests each.** Command (identical `$SET` in every arm):
`pytest research/modalities/tests/test_locoregional_eligibility.py research/modalities/tests/test_emc_site_curation.py research/modalities/tests/test_emc_surgical_quality.py research/modalities/tests/test_lint_consistency.py research/modalities/tests/test_emc_care_delivery_evidence.py -p no:cacheprovider -q`

```
===== ARM base =====
EXIT=0
72 passed in 2.39s
===== ARM armP =====
EXIT=0
72 passed in 2.40s
===== ARM armC1 =====
EXIT=1
FAILED research/modalities/tests/test_emc_site_curation.py::test_the_committed_artifact_matches_the_generator
FAILED research/modalities/tests/test_emc_surgical_quality.py::test_the_artifact_reproduces_from_its_generator
5 failed, 67 passed in 2.37s
===== ARM armC2 =====
EXIT=1
FAILED research/modalities/tests/test_locoregional_eligibility.py::test_every_quantity_the_endpoint_names_is_classified_and_the_negatives_say_what_would_supply_them
1 failed, 71 passed in 2.45s
```
Fuller `armC1` summary from the same run: it also reddened `test_locoregional_eligibility.py::test_wilson_matches_known_values_including_the_boundaries[1-2-0.0945-0.9055]` (and its two sibling parametrisations).

⚠ **Honesty note on exit codes.** My first pass at RUN 2 captured `$?` after a shell assignment and printed a misleading `EXIT=0` for every arm. I noticed, re-ran with the exit code taken directly from `pytest`, and the numbers above are from that corrected run. The corrected codes are what changed the `armC1`/`armC2` rows from `0` to `1`; the pass/fail counts were correct both times.

**RUN 3 — the perturbation, shown.** `armP` build output:
```
BEFORE met 94 259 36.3 30.7 42.3
BEFORE rec 88 326 27.0 22.5 32.1
AFTER  met 77 241 32.0
AFTER  rec 70 300 23.3
--- P differs from base? ---
DIFFERENT
```

**RUN 4 — pin candidate verified clean against the live tree.** Environment: system `python3`, `sys.path` prepended with `research/manuscripts`, importing the repository's own `lint_consistency`. Read-only; nothing written into the repository.
Command: `python3 /tmp/claude-0/w16d/pin/verify.py /home/user/Rare-cancers`
```
DIG who_ever_metastasises.percent -> 36.3
DIG who_ever_metastasises.events -> 94
DIG who_ever_metastasises.denom -> 259
DIG who_ever_metastasises.ci95_lo_percent -> 30.7
DIG who_ever_metastasises.ci95_hi_percent -> 42.3
REPO = /home/user/Rare-cancers
findings: 0
```
**EXIT=0**

**RUN 5 — negative control A: artifact drifts, prose does not (`armP`).**
```
REPO = /tmp/claude-0/w16d/armP
findings: 5
   1318 emc_locoregional_metastasis_pct: this line quotes [36.3, 94.0, 259.0, 95.0, 30.7, 42.3] but ...:who_ever_metastasises.pe...
   1318 emc_locoregional_metastasis_events: ...
   1318 emc_locoregional_metastasis_denom: ...
   1318 emc_locoregional_metastasis_ci_lo: ...
   1318 emc_locoregional_metastasis_ci_hi: ...
```
All five `A-figure-mismatch`, all at the right line.

**RUN 6 — negative control B: prose drifts, artifact does not (`armQ`).** Prose edited in scratch to `**41.9%** (109/260, Wilson 95% CI 36.0–48.0%)`.
```
REPO = /tmp/claude-0/w16d/armQ
findings: 5
   1318 emc_locoregional_metastasis_pct: this line quotes [41.9, 109.0, 260.0, 95.0, 36.0, 48.0] but ...
   ... (all five)
```
The pin fires in **both** directions. It is a gate, not a decoration.

**RUN 7 — disclosed-weakness probe (`armR`), reported against my own deliverable.** Artifact `percent` moved 36.3 → **30.7**, a value already printed on the prose line.
```
REPO = /tmp/claude-0/w16d/armR
findings: 0
```
See limitation L3. I report this rather than omit it.

**PROPOSED (NOT RUN).**
- The regeneration test for `emc-locoregional-eligibility.json` (R5, second pin) — not authored, not executed. Whether the committed artifact currently reproduces from its generator is **UNKNOWN**.
- `scripts/preflight.sh`, in any form, full or normal — not run; my dispatch forbids it.
- The effect of adopting the five candidate entries on any *other* `pinned-figures.json` consumer (`claim_audit.py`, `claim_coverage.py`, `aso_archive_manifest.py`) — **not run**. I verified against `check_artifact_figures` only.
- Any retrieval, any network call, any source fetch — **not attempted**.
- Any resolution, endorsement or re-argument of the `bishop2019` clause — **not attempted**, by instruction.

---

## Limitations

- **L1. Not preflight.** These are targeted `pytest` invocations with a uv-venv `pytest 9.1.1` that the branch preflight has previously been recorded as mishandling (36 phantom failures). The differential design neutralises that for the *delta* — a phantom would appear in `base` too — but it does not license any statement about what preflight would report. **A green `armP` here is not a green preflight.**
- **L2. Bounded guard set.** I ran 72 tests across 5 files, chosen by grep for anything plausibly guarding this artifact. I did **not** run the full suite. A guard elsewhere in the repository that I did not select could in principle catch this perturbation; I searched for one by filename and by content reference and found none, but **absence over a bounded search is weaker than absence over the whole suite.**
- **L3. The pin's granularity is coarser than it looks, and RUN 7 measures it.** `check_artifact_figures` calls `_nums()` on the whole matched line and accepts if **any** number on it is within tolerance. So the five entries collectively pin the line's *number set*, not each number to its position. A drift that moves one field **onto a value already printed on that line** (36.3 → 30.7) passes: `armR` produced **0 findings**. This is a property of the repository's existing mechanism, not of my entries, and it is the honest ceiling on what this pin buys. It still catches every drift shape my `armP`/`armQ` controls exercised, and it is strictly better than the nothing that guards the figure today.
- **L4. Only one of the two figures is closable this way.** `27.0%` / `88/326` has no prose home and therefore no `artifact_figures` pin. Its gap remains open after this work, with a named repair (R3/R5) that I did not author or run.
- **L5. Scope of D12 as now confirmed.** I demonstrated that a **hand edit of the committed artifact** goes undetected. I did **not** demonstrate the wider claim that "a change to the `bishop2019` flag would move them silently" — that would require running the guard set against a mutated registry, which I did not do, and which is W16c's territory in any case.
- **L6. I did not verify the artifact against its generator or its registry.** Whether `94/259` and `88/326` are *correct* is out of scope and untouched. I transcribed them as committed and moved them only inside `/tmp`.
- **L7. HEAD drift.** I read `d3e9c4d8`, not the brief's frozen `92abbcb9`. My one load-bearing artifact is byte-identical between my scratch copy and the live tree, but I cannot assert my results hold at `92abbcb9` and I did not check.
- **L8. No clinical claim whatsoever.** This is tooling, not science. The two pooled figures are **crude during-follow-up proportions over mixed and differing follow-up with censoring ignored** — the artifact's own `_method.endpoint_kind` says so explicitly, and `POLICY-evidence` §2 is what makes that binding. They are not survival estimates. Nothing here concerns efficacy, safety, selectivity, therapeutic window, surveillance intervals, margins, radiotherapy, prognosis, or clinical readiness. **No case entered any denominator; no patient data was created, moved, or inferred.** Every perturbation existed only inside `/tmp/claude-0/w16d/` and none of it touched a number anyone will ever read as a fact. The artifact's own `_limits` — one series dominating both denominators, a consultation series selected toward difficult tumours, recurrence being an endpoint mixture, crude proportions systematically understating lifetime rates — apply unchanged and are in no way softened by anything here.
- **L9. W16c's and W16b's findings are preserved intact.** I confirmed one of W16c's findings and corrected one detail of its framing (R4). I did not revisit, re-review, or relabel anything else in either report.

---

## Stop condition

Set by dispatch: *the test suite executed with a real exit code; the gap demonstrated by a perturbation that goes undetected alongside a control that is detected; and a routed pin candidate verified clean and negatively controlled.*

**MET, all three.**

1. **Executed with real exit codes** — 72 tests, four arms, `EXIT=0 / 0 / 1 / 1`, plus a 9-test single-file run at `EXIT=0`.
2. **Gap demonstrated by construction** — `armP` moves `94/259/36.3` and `88/326/27.0` in the committed artifact and **nothing goes red** (`72 passed`, exit 0), while **two** independent controls are detected (`armC1` 5 failed exit 1; `armC2` 1 failed exit 1). The abort condition did not trigger. **W16c's D12 is confirmed as an executed result, no longer a static reading.**
3. **Pin routed** — five `artifact_figures` entries delivered as data, **0 findings** against the live tree by the repository's own `check_artifact_figures`, and **5 findings** in each of two opposite negative controls. W17e's `_dig_json` blockers were checked by execution and **do not bite**. A self-reported granularity weakness (RUN 7) is disclosed rather than hidden.

The `bishop2019` clause was not resolved, argued, or touched. No file in the Git working tree was edited. No budget row was added. `scripts/preflight.sh` was not run. No network call was made.

---

## Tool-call and wall-clock count actually used

**19 tool calls. 4 minutes 25 seconds wall clock** (`02:39:43Z` → `02:44:08Z`). Well inside the ~40-call / ~40-minute target; I returned on the stop condition rather than padding.

---

## Next concrete action

**Run the regeneration identity check for `emc-locoregional-eligibility.json` — the R3/R5 pin — and report whether the committed artifact actually reproduces from its generator today.** Concretely: in a fresh `/tmp` tar copy, execute `json.load(open(emc_locoregional_eligibility.OUT)) == emc_locoregional_eligibility.build()` with the same `pytest 9.1.1` differential design, against the same green baseline, and record the real exit code. This is the one measurement that would close the recurrence figure's gap (which no `artifact_figures` pin can reach, R4), it is the pattern already committed twice in the same test directory (`test_emc_site_curation.py`, `test_emc_surgical_quality.py`), it needs no new source and no network, and its answer is currently **UNKNOWN** — my controls showed those two neighbours are live regeneration gates, which makes it a live question whether this artifact would pass one. It stays inside lane 16, stays read-only on the tree, and remains independent of the `bishop2019` decision.
