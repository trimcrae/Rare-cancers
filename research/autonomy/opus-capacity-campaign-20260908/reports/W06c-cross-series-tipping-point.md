> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check done: π=0 reproduces every committed `cross_series` field exactly (58.6, 6 coherent / 6 impossible, the 6-pair impossible list, plus the whole 10-year block), the closed form matches the grid at all 8 checkpoints on unrounded shares, and `git status --porcelain` is empty — I wrote nothing into the tree. Unlike W06b's pools, this one **does** have a tipping point.

result: `cross_series` is NOT robust — under disease-specific-side contamination the 5-year median's smallest coherent pairing flips to impossible at **π = 0.130**, which simultaneously breaches the file's own "most pairings are impossible, do not quote this horizon" rule (6/12 → 7/12), below the 0.17–0.22 scale W06b called generous; the all-cause side moves the safe way (more coherent, not fewer) and symmetric contamination at the extremal bound leaves the file exactly invariant.

---

## Worker

- **Worker ID:** W06c — refill for Lane 6, successor to W06b.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`) per my system prompt. I did not observe the served model. **No environment variable in this container names a model** — the `env` output below contains no model identifier, so the self-report has no environmental corroboration. The coordinator should extract the actual runtime model from the transcript.
- `date -u` at start: `Tue Sep  8 02:11:47 UTC 2026`; at end: `Tue Sep  8 02:16:06 UTC 2026`.
- Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`, exit 0. Proxy allowlist lines (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`) matched only on the substring `anthropic` inside host lists and are elided as noise; every Claude/Anthropic-named variable is reproduced:

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

## Question

**Does `research/manuscripts/emc-mortality-decomposition.json` → `cross_series` have a misclassification tipping point, and at what π?** Concretely: (a) at what contamination fraction π does an additional pairing flip from coherent to impossible, and (b) at what π does the reported competing-share median leave the range the file itself treats as coherent?

It is open because W06b explicitly named this as the one exposure it left un-swept, and refused to sweep it without first verifying it could replicate the generator's pairing and exclusion logic. No committed analysis in the repository sweeps a contamination parameter through `cross_series`.

## Prior-work check

I did not re-run broad novelty greps; W06b performed them for this exposure two hours earlier and its own report (line 290) records `cross_series` as **"Not run"**, with the reason (`its estimator pairs across populations and its exclusion logic would need reading first`). W06b's line 330 names this task as its single successor and states the acceptance bar I adopted verbatim: reproduce 58.6 and the 6/6 split at π = 0 or stop. Reads performed:

- `research/autonomy/opus-capacity-campaign-20260908/COMMON-BRIEF.md` — full.
- `.../CLOSED-WORK.md` — full. Nothing in it touches `emc-mortality-decomposition.json`, `cross_series`, or a contamination sweep. This is not a replay of the rejected registry-ICD-O paper, the closed clinical checkpoints, or any refused branch.
- `.../reports/W06b-misclassification-sensitivity.md` — full (49 KB).
- `research/manuscripts/emc_mortality_decomposition.py` (512 lines), `emc-mortality-decomposition-inputs.json`, `emc-mortality-decomposition.json`.

**W06b's findings are preserved intact and are not revisited here.** Nothing below alters the relative-survival competing-share result (no tipping point at any π, median floored at 12.1%) or the cytotoxic-response-pool result (moves only in the safe direction). Those concern `emc-relative-survival.json` and `emc-systemic-therapy-pooling.json`; this run touches neither.

## Method / inputs

**Files (frozen read commit `92abbcb905cacf07f14b238db50d1b98f6590374`, all read-only):**

| File | Role |
|---|---|
| `/home/user/Rare-cancers/research/manuscripts/emc_mortality_decomposition.py` | the generator whose `pct()`, `decompose()`, `cross_series()` I reimplemented |
| `/home/user/Rare-cancers/research/manuscripts/emc-mortality-decomposition-inputs.json` | the swept inputs (9 series + `pooled_reference`) |
| `/home/user/Rare-cancers/research/manuscripts/emc-mortality-decomposition.json` | the committed output, used **only** as the replication target |
| `/home/user/Rare-cancers/research/data/emc-clinical-registry.json` | for the generator's own `verify_provenance` check |

**Tooling.** Python 3.11.15, stdlib only (`json`, `math`, `pathlib`, `platform`, `sys`). No numpy, no network, no writes to the repository. Executed under `/tmp/claude-0/W06c/`.

**Replication requirement I imposed on myself.** My reimplementation had to reproduce every committed `cross_series` field — both horizons, both survival ranges, the source orderings, all four pairing counts, both share ranges, both medians, the ceiling ranges, **and the exact ordered list of impossible pairings** — before any swept value was allowed to mean anything. It does. I reimplemented rather than imported the generator on purpose: importing would have made the replication check circular.

**Contamination model (identical algebra to W06b, applied to a different estimator).**

> S_obs = (1−π)·S_emc + π·S_c ⟹ S_emc = (S_obs − π·S_c)/(1−π)

S_c is swept over four settings: S_obs + 0.05, +0.10, +0.15, and **S_c = 1.00, the extremal bound** (no contaminant dies), capped at 1.0 since a survival probability cannot exceed 1. Corrected rows are then passed through the generator's own unmodified exclusion rules (`coherent` iff `m_comp ≥ 0`; `undefined` iff `m_all = 0`) and its own median convention (`shares[len(shares)//2]`, the upper median).

**Feasibility bound, stated because it limits where the sweep means anything.** Under S_c = 1.00 the mixture requires π ≤ S_obs. Measured: 5-year min all-cause S_obs = 0.710 (`china2016`), min DSS S_obs = 0.758 (`masunaga2025_metastatic`); 10-year min all-cause 0.650, min DSS 0.850. Every tipping point reported below lies inside the feasible region. Beyond it a corrected survival goes non-positive and the row leaves the enumeration — a bookkeeping artifact, not a coherence result, and I flag it rather than quote it.

**Four exposure models, because `cross_series` has two independently contaminable sides.** This is the whole point of the estimator and the reason it needed its own analysis:

| Model | All-cause side corrected | Disease-specific side corrected |
|---|---|---|
| **A** | `meisKindblom1999`, `drilon2008` (W06b's two named series) | none |
| **B** | all six all-cause sources | none |
| **C** | none | all four disease-specific sources |
| **D** | all six | all four (same π, same S_c rule) |

**Models B, C and D are bounding constructions, not claims that any named cohort is contaminated.** Model A is the only one whose exposed set corresponds to a stated rationale in the repository (W06b's morphology-assembled-series argument), and even that assigns no rate.

## Signed direction, stated before computing, with its falsifier

I derived these three signs analytically before running anything:

1. **All-cause side corrected (models A, B).** Contamination raises a series' observed all-cause survival, so removing contaminants **lowers** S_all and **raises** m_all. Since `share = 1 − m_dis/m_all` with m_dis fixed, the share must move **UP**; and since a pairing is impossible iff m_dis > m_all, raising m_all must make impossible pairings **rarer**, never commoner. *So the all-cause asymmetry W06b flagged a priori runs in the SAFE direction — it cannot manufacture the flip-to-impossible it predicted.* Confirmed by the run.
2. **Disease-specific side corrected (model C).** Contaminants cannot die of EMC and the less-lethal ones (myxoid liposarcoma, low-grade fibromyxoid sarcoma) inflate an observed DSS curve, so removing them **lowers** S_dss and **raises** m_dis. The share must move **DOWN** and impossible pairings must become **commoner**. *This, not the all-cause side, is where a real tipping point can live.* Confirmed by the run.
3. **Both sides corrected at the extremal bound (model D).** With S_c = 1.00, (1 − S′) = (1 − S_obs)/(1 − π) on both sides, so the (1−π) factors cancel in `m_comp/m_all` and **every share and every coherence verdict is exactly invariant**. Confirmed by the run: all 11 π rows in the model-D extremal table are bit-identical to π = 0.

**Falsifier, stated in advance:** any swept cell moving a share against its model's predicted sign, or any model-D extremal row differing from π = 0 inside the feasible region, would indicate an algebra error in my reimplementation and would invalidate every tipping point below. **No cell violated its sign, and no feasible model-D extremal row moved.**

## Result

### 1. Replication at π = 0 — `PASS` (`PRIMARY`, arithmetic on committed inputs)

All 24 scalar/list fields plus both exact impossible-pairing lists matched. Verbatim excerpt:

```
  OK   5_year   pairings_total           mine=12 committed=12
  OK   5_year   pairings_coherent        mine=6  committed=6
  OK   5_year   pairings_impossible      mine=6  committed=6
  OK   5_year   pairings_undefined       mine=0  committed=0
  OK   5_year   competing_share_of_deaths_pct_range   mine=[13.0, 70.0] committed=[13.0, 70.0]
  OK   5_year   competing_share_of_deaths_pct_median  mine=58.6 committed=58.6
  OK   5_year   excluded_pairings.impossible (exact list)  n=6
        coherent shares sorted: [13.0, 16.6, 51.7, 58.6, 63.8, 70.0]
  OK   10_year  competing_share_of_deaths_pct_median  mine=57.1 committed=57.1
        coherent shares sorted: [50.0, 50.0, 57.1, 57.1]
  REPLICATION AT pi=0: PASS
```

58.6 is the **upper** median (`shares[3]`) of six sorted shares — the same non-conventional convention W06b had to replicate rather than assume. The generator's `verify_provenance` rule also passes: every `registry_verbatim` string is still present in the clinical registry.

### 2. The tipping points — the deliverable (`PRIMARY` arithmetic; **π and S_c are SWEPT PARAMETERS, NOT MEASUREMENTS**)

S_c = 1.00 extremal bound, π grid resolution 0.0005. "Quotability" is **the file's own rule**, quoted verbatim from `excluded_pairings.how_to_read_them`: *"A horizon where most pairings are impossible should not be quoted at all."*

| Model | Horizon | π: an additional pairing flips to **impossible** | π: >half impossible → **file's own do-not-quote rule breached** | π: median first enters direct-cause-split range [10.0, 30.8] |
|---|---|---|---|---|
| A | 5-year | **NEVER** in [0,1) | **NEVER** | NEVER |
| A | 10-year | **NEVER** | **NEVER** | NEVER |
| B | 5-year | **NEVER** (a pairing flips *back to coherent* at π = 0.0085) | **NEVER** | NEVER |
| B | 10-year | **NEVER** (flips back to coherent at π = 0.200) | **NEVER** | NEVER |
| **C** | **5-year** | **π = 0.130** | **π = 0.130** | **π = 0.476** (median 30.8) |
| **C** | **10-year** | **π = 0.500** | **π = 0.500** | **π = 0.381** (median 30.8) |
| D | 5-year | **NEVER** inside the feasible region (exactly invariant) | **NEVER** | π = 0.82, outside feasibility |
| D | 10-year | **NEVER** (exactly invariant) | **NEVER** | NEVER |

**The two numbers asked for, for the headline 5-year median of 58.6:** an additional pairing flips to impossible at **π = 0.130**, and that same π breaches the file's own quotability rule. The median leaves toward the independent cause-split comparator at **π = 0.476**.

### 3. Why the 5-year flip and the quotability breach coincide — and why that matters

The committed 5-year block sits at **6 impossible out of 12 — exactly the 50% boundary**. The file's rule fires on *most* pairings being impossible, so **one single flip** (6→7 of 12) carries it from "quotable" to "should not be quoted at all". `cross_series` at 5 years has **zero margin** against its own quotability rule at π = 0. This is a structural property of the committed file, visible without any sweep, and it is why this quantity is fragile where W06b's pools were not.

### 4. Closed form (`PRIMARY`, derived and then verified against the grid)

With S_c = 1.00 the correction is multiplicative on mortality: (1 − S′) = (1 − S_obs)/(1 − π). Writing *s* for a pairing's committed competing share as a fraction:

- **Model C:** `s′ = (s − π)/(1 − π)`, coherent iff `s ≥ π`.
- **Model B:** `s′ = π + (1 − π)s`; an impossible pairing (s < 0) becomes coherent at `π = −s/(1 − s)`.
- **Model D:** `s′ = s` exactly; coherence unchanged.

Model C therefore has an exact and checkable rule:

> **A coherent pairing flips to impossible exactly when π exceeds its own competing share.**

The 5-year flip thresholds are the committed shares themselves: 0.130, 0.166, 0.517, 0.586, 0.638, 0.700. The smallest is 13.0% (`meisKindblom1999` × `masunaga2025_localized`), giving π = 0.130 — the grid's first breaching point 0.1305 is exactly one 0.0005 step above it. The 10-year thresholds are 0.500, 0.500, 0.571, 0.571; grid breach 0.5005. **The grid and the closed form agree exactly.**

### 5. Where π = 0.130 sits against the only scale in the repository (`SECONDARY`, and it is a scale not a rate)

W06b anchored the *scale* of π — explicitly not a value — on the only in-repository quantities that bracket anything: Antonescu 1998 detected the fusion in 7/9 tested (2 negative, 0.22) and Okamoto 2001 in 15/18 (3 negative, 0.17), both of which W06b correctly labelled **assay-scope negatives, not misclassifications**. On that scale, π = 0.130 is **below** the range W06b called generous, and π = 0.476 sits just under its 0.50 sweep ceiling. **This is a statement about where the threshold falls on a scale, not a claim that contamination reaches it in any cohort.** Nothing here says any named series contains a misclassified tumour.

### 6. Milder contaminant-survival settings

The three milder S_c settings move things less at every π, as expected, but the 5-year model-C breach still occurs inside the swept grid at every one of them: S_c = S_obs+0.05 breaches between π = 0.20 and 0.25; +0.10 and +0.15 both breach by π = 0.15. **The tipping point is not an artifact of the extremal bound** — the extremal bound only makes it earliest and cleanest.

### 7. What this corrects in W06b's a-priori reasoning

W06b's hypothesis was that *"contamination inflates the all-cause term while leaving the disease-specific term untouched"* would produce the flip. It named the right file and the right mechanism-shape, and I tested it rather than assuming it. **The all-cause asymmetry runs the other way**: models A and B produce *fewer* impossible pairings and a *higher* median, never a flip to impossible at any π. The tipping point is real but it lives on the **disease-specific** side (model C), which W06b's framing had treated as the fixed term. W06b offered this as a hypothesis to test, so this is the test returning a signed answer, not a defect in that report.

## Validation evidence

**RUN.** Environment: Linux-6.18.44-fc-v24-x86_64-with-glibc2.39, Python 3.11.15, stdlib only, no network, executed under `/tmp/claude-0/W06c/`.

```
$ cd /tmp/claude-0/W06c && python3 cross_series_misclassification.py > out.txt 2>&1; echo "EXIT=$?"
EXIT=0
$ wc -l out.txt
386 out.txt
```

First run exited 1 with `IndexError: list index out of range` at extreme π, where every corrected survival on one side goes non-positive and the horizon empties. I added an explicit degenerate-horizon guard and re-ran to exit 0 rather than leave the crash unreported. The crash was in my own harness, not in the generator, and it affected no reported tipping point (all lie well inside the feasible region).

```
$ python3 cf.py; echo "EXIT=$?"      # closed form applied to UNROUNDED committed shares
  5y unrounded coherent shares: [0.13, 0.165517, 0.516667, 0.585714, 0.6375, 0.7]
       pi=0.13 closed form on unrounded s: [0.0, 4.1, 44.4, 52.4, 58.3, 65.5]
       pi=0.40 closed form on unrounded s: [19.4, 31.0, 39.6, 50.0]
EXIT=0
```

These match the swept grid at all 8 checkpoints. The `MISMATCH` lines in section 4 of `out.txt` are ≤ 0.1 pp and are double-rounding — the in-script closed-form check applied the transform to the already-rounded committed share. **I am reporting the mismatch rather than silently suppressing it**; the `cf.py` re-run on unrounded shares is the resolution.

Repository untouched: `git status --porcelain` in `/home/user/Rare-cancers` returns empty. No git write operation of any kind was performed. No `scripts/preflight.sh` run (dispatch did not ask for one).

**Verbatim key output (model C, S_c = 1.00 extremal, both horizons):**

```
      pi |  5y med       5y range  coh/imp  quotable? |  10y med      10y range  coh/imp  quotable?
    0.00 |    58.6    [13.0,70.0]      6/6        yes |     57.1    [50.0,57.1]      4/2        yes
    0.05 |    56.4     [8.4,68.4]      6/6        yes |     54.9    [47.4,54.9]      4/2        yes
    0.10 |    54.0     [3.3,66.7]      6/6        yes |     52.4    [44.4,52.4]      4/2        yes
    0.13 |    52.4     [0.0,65.5]      6/6        yes |     50.7    [42.5,50.7]      4/2        yes
    0.15 |    51.3     [1.8,64.7]      5/7         NO |     49.6    [41.2,49.6]      4/2        yes
    0.20 |    54.7    [39.6,62.5]      4/8         NO |     46.4    [37.5,46.4]      4/2        yes
    0.30 |    48.2    [31.0,57.1]      4/8         NO |     38.8    [28.6,38.8]      4/2        yes
    0.50 |    27.5     [3.3,40.0]      4/8         NO |     14.3     [0.0,14.3]      4/2        yes
```

**PROPOSED (NOT RUN).** A `limits` entry in `emc-mortality-decomposition.json` recording that the 5-year block sits at exactly the 50% impossible boundary. I did not author it: the file is not mine, it is generated (`_do_not_hand_edit` convention applies to this family), and the change belongs in the generator with a re-run. Routing note below. **No π value, contamination rate, or magnitude claim should enter any committed file** — π is a swept parameter.

## Limitations

- **No clinical claim of any kind.** Nothing here bears on EMC efficacy, safety, selectivity, prognosis, or the management of any patient. This is arithmetic on published summary percentages.
- **π is a swept parameter and is labelled so on every row.** It is not a measurement, not an estimate, and not a claim about any cohort. Nothing here says `meisKindblom1999`, `drilon2008`, `masunaga2025_localized`, `bishop2019` or any other series contains a misclassified tumour. It says what would follow *if* they did, at each of a range of assumed fractions.
- **A sensitivity range is never a point estimate.** The swept medians (52.4, 48.2, 27.5 …) are conditional on π, S_c *and* the exposure model, and must never be quoted as revised values of the competing share. The committed value remains 58.6 at π = 0.
- **No exclusion rule was weakened.** `coherent` / `impossible` / `undefined` are the generator's own predicates, transcribed unmodified. No pairing was rescued, retained past its rule, or reclassified.
- **Models B, C, D are bounding constructions.** Assigning contamination to `masunaga2025` (a Japanese national registry) or to any other specific cohort would be a claim about that cohort's diagnostic practice, which I do not make and could not support from anything retrieved in this run.
- **The contaminant model is a two-component mixture with one survival parameter per horizon and per side.** Real contamination would be heterogeneous. S_c = 1.00 bounds any mixture whose components all survive at least as well as EMC; it does **not** bound a contaminant that does worse.
- **The tipping point is a property of the file as committed at `92abbcb9`.** It depends on the current pairing set, the upper-median convention, and the 6/12 boundary position. Adding or removing one series moves all of it.
- **The `cross_series` estimator's own stated limits stand unchanged and are prior to everything here** — it pairs across populations by construction, `background_mortality_check` already reports ratio 1.77 observed-to-expected, and the file's `how_to_read_them` already warns that a heavily-impossible horizon is not quotable. This sweep does not rehabilitate the estimator; it quantifies how little margin one of its outputs has.
- **W06b's results are untouched and remain the finding for their own files.** No retrieval was attempted; none was needed.

## Stop condition

**Set by the dispatch:** an executed sweep with an exact π = 0 replication, and a tipping-point result (or a proven absence) for the cross-series median.

**MET.**
- Replication: `PASS`, exact on all 24 committed fields plus both ordered impossible-pairing lists, including 58.6 and the 6-coherent/6-impossible split.
- Executed: exit 0, real numeric output, Python 3.11.15, stdlib only, `/tmp/claude-0/W06c/`, no writes to the tree.
- Tipping point: **found, not absent.** 5-year — an additional pairing flips to impossible at **π = 0.130**, which is the same π at which the file's own do-not-quote rule is breached; the median enters the independent cause-split range at **π = 0.476**. 10-year — **π = 0.500** and **π = 0.381** respectively. Proven absence on the all-cause side (models A and B: never, at any π) and exact invariance under symmetric extremal contamination (model D).

## Tool-call and wall-clock count actually used

**11 tool calls; wall clock 02:11:47Z → 02:16:06Z ≈ 4.5 minutes.** Well inside the ~40-call / ~40-minute target. Returning now that the stop condition is met, without padding.

## Next concrete action

**One successor, and it is a defect diagnosis rather than another sweep.** `cross_series["5_year"]` sits at exactly 6 impossible of 12 — the boundary of the file's own `"A horizon where most pairings are impossible should not be quoted at all"` rule — while the file simultaneously publishes that horizon's median (58.6) and range without noting the zero margin. The successor is to determine whether `emc_mortality_decomposition.py` should **compute and emit that margin as a field** (e.g. `impossible_fraction` and a boolean `quotable_by_own_rule`), so the rule is enforced by the generator rather than left to a reader's arithmetic. That is a bounded change to one generator with an exact acceptance test (the regenerated JSON gains two fields per horizon and changes no existing number), and it needs no retrieval. It belongs to whoever owns `emc_mortality_decomposition.py`; I am read-only and did not author it.

**Routing note for the coordinator:** the observation in section 3 is a finding about a committed generated file, not an edit request from me. `emc-mortality-decomposition.json` carries the generated-output convention, so any change must be made in the script and the generator re-run — never hand-edited into the JSON.

**Explicitly not recommended:** sweeping a fifth exposure model, or extending this to `within_series` (a single pairing, already covered by W06b's structural argument for the same two series), or attempting Meis-Kindblom 1999 full text — W06b already established that narrowing π would not change any pooled conclusion, and that reasoning holds here too: it would tell us where π sits relative to 0.130, but the threshold itself is already exact.

---

## Code (returned inline; run under `/tmp/claude-0/W06c/`, nothing written to the repository)

`cross_series_misclassification.py`:

```python
#!/usr/bin/env python3
"""W06c -- misclassification sensitivity for emc-mortality-decomposition.json -> cross_series.

Successor to W06b. READ-ONLY on the repository: this script reads three committed JSON
files and writes nothing.

WHAT pi IS. pi is a SWEPT PARAMETER, NOT A MEASUREMENT. It is the fraction of a
diagnostic series that is not truly EMC. No source in this repository states pi for any
cohort. Nothing printed below is an estimate of contamination in any named cohort.

CONTAMINATION MODEL (identical algebra to W06b, applied to a different estimator):
    S_obs = (1-pi)*S_emc + pi*S_c     =>     S_emc = (S_obs - pi*S_c) / (1 - pi)
S_c, the contaminant survival at the horizon, is capped at 1.0. S_c = 1.00 is the
EXTREMAL BOUND: no contaminant dies. A conclusion that survives S_c = 1.00 at every pi
survives any contaminant survival distribution whose components all survive at least as
well as true EMC. Feasibility under S_c = 1.00 requires pi <= S_obs.

THE ASYMMETRY UNDER TEST. cross_series pairs an all-cause figure from one population
against a disease-specific figure from ANOTHER, so the two sides can be contaminated
independently. Four exposure models are swept:
  A  all-cause side, only the two series W06b named (meisKindblom1999, drilon2008)
  B  all-cause side, EVERY all-cause source            (max asymmetry, DSS untouched)
  C  disease-specific side only                        (max asymmetry, all-cause fixed)
  D  both sides, same pi and same S_c rule             (symmetric)
Models B/C/D are BOUNDING CONSTRUCTIONS, not claims that any cohort is contaminated.
"""
from __future__ import annotations
import json, math, pathlib, platform, sys

ROOT = pathlib.Path("/home/user/Rare-cancers")
INPUTS = ROOT / "research/manuscripts/emc-mortality-decomposition-inputs.json"
COMMITTED = ROOT / "research/manuscripts/emc-mortality-decomposition.json"
REGISTRY = ROOT / "research/data/emc-clinical-registry.json"

W06B_EXPOSED = {"meisKindblom1999", "drilon2008"}
PI_GRID = [0.00, 0.01, 0.05, 0.10, 0.13, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
SC_SETTINGS = [("S_c = S_obs + 0.05", 0.05), ("S_c = S_obs + 0.10", 0.10),
               ("S_c = S_obs + 0.15", 0.15), ("S_c = 1.00 (EXTREMAL BOUND)", None)]

# --------------------------------------------------------------------------
# Independent reimplementation of the generator's pairing + exclusion logic.
# Transcribed from research/manuscripts/emc_mortality_decomposition.py, functions
# pct(), decompose(), cross_series(). Reimplemented, not imported, on purpose:
# importing would make the replication check circular.
# --------------------------------------------------------------------------
def pct(x): return round(100.0 * x, 1)

def decompose(s_all, s_dss):
    m_all = 1.0 - s_all
    m_dis = 1.0 - s_dss
    m_comp = m_all - m_dis
    return {
        "all_cause_mortality_pct": pct(m_all),
        "disease_mortality_pct": pct(m_dis),
        "competing_mortality_pct": pct(m_comp),
        "competing_share_of_deaths_pct": pct(m_comp / m_all) if m_all > 0 else None,
        "antitumour_ceiling_pct_points": pct(m_dis),
        "coherent": m_comp >= 0,
    }

def collect(spec):
    all_cause, disease = {}, {}
    for s in spec["series"]:
        for h, v in (s.get("overall_survival") or {}).items():
            all_cause.setdefault(float(h), []).append((s["key"], v))
        for h, v in (s.get("disease_specific_survival") or {}).items():
            disease.setdefault(float(h), []).append((s["key"], v))
    pooled = spec.get("pooled_reference") or {}
    if pooled.get("value") is not None:
        disease.setdefault(10.0, []).append(("registry_pooled", pooled["value"]))
    return all_cause, disease

def correct(s_obs, pi, sc_delta):
    """S_emc = (S_obs - pi*S_c)/(1-pi), with S_c capped at 1.0."""
    if pi <= 0.0:
        return s_obs
    sc = 1.0 if sc_delta is None else min(1.0, s_obs + sc_delta)
    if pi >= 1.0:
        return None
    v = (s_obs - pi * sc) / (1.0 - pi)
    return v if v > 0.0 else None   # a non-positive corrected survival is not usable

def cross_series(spec, pi=0.0, sc_delta=None, ac_exposed=frozenset(), ds_exposed=frozenset()):
    all_cause, disease = collect(spec)
    out = {}
    for h in sorted(set(all_cause) & set(disease)):
        ac_rows, ds_rows = [], []
        for k, v in all_cause[h]:
            v2 = correct(v, pi, sc_delta) if k in ac_exposed else v
            if v2 is not None: ac_rows.append((k, v2))
        for k, v in disease[h]:
            v2 = correct(v, pi, sc_delta) if k in ds_exposed else v
            if v2 is not None: ds_rows.append((k, v2))
        if not ac_rows or not ds_rows:
            # Degenerate: every corrected survival on one side went non-positive, i.e. pi
            # is past the mixture's feasibility bound. Reported, never quoted as a result.
            out[f"{h:g}_year"] = {
                "degenerate": True, "pairings_total": 0, "pairings_coherent": 0,
                "pairings_impossible": 0, "pairings_undefined": 0,
                "competing_share_of_deaths_pct_range": None,
                "competing_share_of_deaths_pct_median": None,
                "antitumour_ceiling_pct_points_range": None,
                "all_cause_sources": [k for k, _ in ac_rows],
                "disease_specific_sources": [k for k, _ in ds_rows],
                "impossible_pairs": [], "coherent_shares": [],
            }
            continue
        coherent, impossible, undefined = [], [], []
        for ac_key, ac_v in sorted(ac_rows, key=lambda kv: kv[1]):
            for ds_key, ds_v in sorted(ds_rows, key=lambda kv: kv[1]):
                d = decompose(ac_v, ds_v)
                d.update({"all_cause_source": ac_key, "all_cause_survival_pct": pct(ac_v),
                          "disease_specific_source": ds_key,
                          "disease_specific_survival_pct": pct(ds_v)})
                if not d["coherent"]:                            impossible.append(d)
                elif d["competing_share_of_deaths_pct"] is None: undefined.append(d)
                else:                                            coherent.append(d)
        shares = sorted(x["competing_share_of_deaths_pct"] for x in coherent)
        ceilings = sorted(x["antitumour_ceiling_pct_points"] for x in coherent)
        ac_vals = sorted(v for _, v in ac_rows); ds_vals = sorted(v for _, v in ds_rows)
        out[f"{h:g}_year"] = {
            "all_cause_survival_pct_range": [pct(ac_vals[0]), pct(ac_vals[-1])],
            "all_cause_sources": [k for k, _ in sorted(ac_rows, key=lambda kv: kv[1])],
            "disease_specific_survival_pct_range": [pct(ds_vals[0]), pct(ds_vals[-1])],
            "disease_specific_sources": [k for k, _ in sorted(ds_rows, key=lambda kv: kv[1])],
            "pairings_total": len(coherent) + len(impossible) + len(undefined),
            "pairings_coherent": len(coherent),
            "pairings_impossible": len(impossible),
            "pairings_undefined": len(undefined),
            "competing_share_of_deaths_pct_range": [shares[0], shares[-1]] if shares else None,
            "competing_share_of_deaths_pct_median": shares[len(shares) // 2] if shares else None,
            "antitumour_ceiling_pct_points_range": [ceilings[0], ceilings[-1]] if ceilings else None,
            "impossible_pairs": [(d["all_cause_source"], d["disease_specific_source"]) for d in impossible],
            "coherent_shares": shares,
        }
    return out


def hr(t=""): print("\n" + "=" * 78); print(t); print("=" * 78)

def main():
    spec = json.loads(INPUTS.read_text())
    committed = json.loads(COMMITTED.read_text())["cross_series"]

    print(f"python {platform.python_version()} on {platform.platform()}")
    print(f"inputs    : {INPUTS}")
    print(f"committed : {COMMITTED}")

    # ---------------- 0. provenance: the verbatim strings still exist -------------
    blob = json.dumps(json.loads(REGISTRY.read_text()), ensure_ascii=False)
    prov = [s["key"] for s in spec["series"]
            if s.get("registry_verbatim") and s["registry_verbatim"] not in blob]
    pv = (spec.get("pooled_reference") or {}).get("registry_verbatim")
    if pv and pv not in blob: prov.append("pooled_reference")
    hr("0. PROVENANCE CHECK (the generator's own verify_provenance rule)")
    print("  registry_verbatim strings missing from the clinical registry:",
          prov if prov else "NONE -- all present")

    # ---------------- 1. exact replication at pi = 0 -----------------------------
    hr("1. REPLICATION AT pi = 0 -- REFUSE TO PROCEED IF THIS FAILS")
    mine = cross_series(spec, pi=0.0)
    ok = True
    keys = ["all_cause_survival_pct_range", "all_cause_sources",
            "disease_specific_survival_pct_range", "disease_specific_sources",
            "pairings_total", "pairings_coherent", "pairings_impossible",
            "pairings_undefined", "competing_share_of_deaths_pct_range",
            "competing_share_of_deaths_pct_median", "antitumour_ceiling_pct_points_range"]
    for h in sorted(committed):
        for k in keys:
            a, b = mine[h][k], committed[h][k]
            same = (a == b); ok &= same
            print(f"  {'OK ' if same else 'FAIL'}  {h:8s} {k:42s} mine={a!r} committed={b!r}")
        cimp = [(d["all_cause_source"], d["disease_specific_source"])
                for d in committed[h]["excluded_pairings"]["impossible"]]
        same = mine[h]["impossible_pairs"] == cimp; ok &= same
        print(f"  {'OK ' if same else 'FAIL'}  {h:8s} "
              f"{'excluded_pairings.impossible (exact list)':42s} n={len(cimp)}")
        print(f"        coherent shares sorted: {mine[h]['coherent_shares']}")
    print(f"\n  REPLICATION AT pi=0: {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  Refusing to sweep. The failure is the deliverable."); sys.exit(2)

    ALL_AC = set(mine["5_year"]["all_cause_sources"]) | set(mine["10_year"]["all_cause_sources"])
    ALL_DS = (set(mine["5_year"]["disease_specific_sources"])
              | set(mine["10_year"]["disease_specific_sources"]))
    MODELS = [
        ("A  all-cause side, W06b's two named series only", W06B_EXPOSED & ALL_AC, frozenset()),
        ("B  all-cause side, ALL sources (max asymmetry, DSS fixed)", ALL_AC, frozenset()),
        ("C  disease-specific side only (max asymmetry, all-cause fixed)", frozenset(), ALL_DS),
        ("D  both sides, same pi and same S_c rule (symmetric)", ALL_AC, ALL_DS),
    ]

    # ---------------- 2. the sweep ------------------------------------------------
    for label, acx, dsx in MODELS:
        hr(f"2. SWEEP -- exposure model {label}")
        print(f"   all-cause exposed : {sorted(acx) if acx else '(none)'}")
        print(f"   disease-spec exposed: {sorted(dsx) if dsx else '(none)'}")
        for sc_label, sc in SC_SETTINGS:
            print(f"\n   -- contaminant survival assumption: {sc_label}  "
                  f"[pi and S_c are SWEPT PARAMETERS, NOT MEASUREMENTS]")
            print(f"   {'pi':>5} | {'5y med':>7} {'5y range':>14} {'coh/imp':>8} {'quotable?':>10}"
                  f" | {'10y med':>8} {'10y range':>14} {'coh/imp':>8} {'quotable?':>10}")
            for pi in PI_GRID:
                r = cross_series(spec, pi, sc, acx, dsx)
                cells = []
                for h in ("5_year", "10_year"):
                    x = r[h]
                    med = x["competing_share_of_deaths_pct_median"]
                    rng = x["competing_share_of_deaths_pct_range"]
                    # The file's OWN quotability rule, verbatim from
                    # excluded_pairings.how_to_read_them: "A horizon where most pairings
                    # are impossible should not be quoted at all."
                    q = ("n/a" if x["pairings_total"] == 0 else
                         "NO" if x["pairings_impossible"] * 2 > x["pairings_total"] else "yes")
                    cells.append((f"{med:.1f}" if med is not None else "n/a",
                                  f"[{rng[0]:.1f},{rng[1]:.1f}]" if rng else "n/a",
                                  f"{x['pairings_coherent']}/{x['pairings_impossible']}", q))
                a, b = cells
                print(f"   {pi:>5.2f} | {a[0]:>7} {a[1]:>14} {a[2]:>8} {a[3]:>10}"
                      f" | {b[0]:>8} {b[1]:>14} {b[2]:>8} {b[3]:>10}")

    # ---------------- 3. tipping points ------------------------------------------
    hr("3. TIPPING POINTS -- fine grid, S_c = 1.00 extremal bound, resolution 0.0005")
    CAUSE_SPLIT = (10.0, 30.8)   # direct_cause_split competing shares: the independent comparator
    print(f"   independent comparator = direct_cause_split competing shares "
          f"[{CAUSE_SPLIT[0]}, {CAUSE_SPLIT[1]}] (masunaga2025 metastatic / localised)")
    grid = [i / 2000 for i in range(0, 2000)]
    for label, acx, dsx in MODELS:
        print(f"\n   model {label}")
        for h in ("5_year", "10_year"):
            base = cross_series(spec, 0.0)[h]
            n_imp0, n_tot = base["pairings_impossible"], base["pairings_total"]
            med0 = base["competing_share_of_deaths_pct_median"]
            first_flip = first_unflip = first_notquotable = first_in_range = None
            for pi in grid:
                x = cross_series(spec, pi, None, acx, dsx)[h]
                if first_flip is None and x["pairings_impossible"] > n_imp0: first_flip = pi
                if first_unflip is None and x["pairings_impossible"] < n_imp0: first_unflip = pi
                if first_notquotable is None and x["pairings_impossible"] * 2 > n_tot:
                    first_notquotable = pi
                m = x["competing_share_of_deaths_pct_median"]
                if first_in_range is None and m is not None and CAUSE_SPLIT[0] <= m <= CAUSE_SPLIT[1]:
                    first_in_range = (pi, m)
            print(f"     {h}: committed median {med0}, {n_imp0}/{n_tot} impossible at pi=0")
            print(f"        pi at which an ADDITIONAL pairing flips to impossible : "
                  f"{first_flip if first_flip is not None else 'NEVER in [0,1)'}")
            print(f"        pi at which a pairing flips BACK to coherent          : "
                  f"{first_unflip if first_unflip is not None else 'NEVER in [0,1)'}")
            print(f"        pi at which >half the pairings are impossible          : "
                  f"{first_notquotable if first_notquotable is not None else 'NEVER in [0,1)'}"
                  f"   <- the file's own 'do not quote this horizon' rule")
            print(f"        pi at which the median first enters [10.0, 30.8]       : "
                  f"{first_in_range if first_in_range is not None else 'NEVER in [0,1)'}")

    # ---------------- 4. closed forms --------------------------------------------
    hr("4. CLOSED FORM (S_c = 1.00 on the exposed side) -- checked against the grid")
    print("""   With S_c = 1.00 the correction acts multiplicatively on the mortality:
       1 - S' = (1 - S_obs) / (1 - pi)
   Writing s for a pairing's committed competing share as a FRACTION:
       model C (DSS side corrected) : s' = (s - pi) / (1 - pi);  coherent iff s >= pi
       model B (all-cause corrected): s' = pi + (1 - pi) s;      an impossible pairing
                                       (s < 0) becomes coherent at pi = -s/(1-s)
       model D (both corrected)     : s' = s EXACTLY, and coherence is unchanged --
                                       the (1-pi) factors cancel between numerator and
                                       denominator, so symmetric contamination at the
                                       extremal bound leaves cross_series invariant.
   Model C therefore has an exact and memorable tipping rule:
       A COHERENT PAIRING FLIPS TO IMPOSSIBLE EXACTLY WHEN pi EXCEEDS ITS OWN
       COMPETING SHARE.
   NOTE: applying the transform to the ROUNDED committed shares reproduces the grid to
   within 0.1 pp (double rounding). cf.py re-derives it from unrounded shares and the
   agreement is then exact.""")
    for h in ("5_year", "10_year"):
        b = cross_series(spec, 0.0)[h]
        print(f"\n   {h} committed coherent shares: {b['coherent_shares']}")
        print(f"     -> model C flip thresholds (= the shares themselves, /100): "
              f"{[round(s/100, 4) for s in b['coherent_shares']]}")
        for pi in (0.05, 0.13, 0.20, 0.40):
            x = cross_series(spec, pi, None, frozenset(), ALL_DS)[h]
            pred = sorted(round(100*((s/100 - pi)/(1-pi)), 1)
                          for s in b["coherent_shares"] if s/100 >= pi)
            print(f"     pi={pi:.2f}  closed form {pred}  grid {x['coherent_shares']}  "
                  f"{'MATCH' if pred == x['coherent_shares'] else 'within-rounding'}")

    hr("pi IS A SWEPT PARAMETER, NOT A MEASUREMENT. No row above estimates contamination "
       "in any\nnamed cohort. A sensitivity range is never a point estimate. No exclusion "
       "rule was\nweakened: coherent/impossible/undefined are the generator's own, "
       "unmodified.")

main()
```

`cf.py` (the unrounded closed-form and feasibility check):

```python
import json, pathlib
ROOT = pathlib.Path("/home/user/Rare-cancers")
spec = json.loads((ROOT / "research/manuscripts/emc-mortality-decomposition-inputs.json").read_text())
def pct(x): return round(100.0 * x, 1)
ac, ds = {}, {}
for s in spec["series"]:
    for h, v in (s.get("overall_survival") or {}).items():          ac.setdefault(float(h), []).append((s["key"], v))
    for h, v in (s.get("disease_specific_survival") or {}).items(): ds.setdefault(float(h), []).append((s["key"], v))
ds.setdefault(10.0, []).append(("registry_pooled", spec["pooled_reference"]["value"]))
print("FEASIBILITY under S_c=1.00 (mixture needs pi <= S_obs):")
for h in (5.0, 10.0):
    print(f"  {h:g}y  min all-cause S_obs={min(v for _, v in ac[h]):.3f}  "
          f"min DSS S_obs={min(v for _, v in ds[h]):.3f}")
print("\nCLOSED FORM from UNROUNDED shares, model C, S_c=1.00:")
for h in (5.0, 10.0):
    raw = []
    for k, a in ac[h]:
        for k2, d in ds[h]:
            m_all, m_dis = 1 - a, 1 - d
            if m_all > 0 and m_all - m_dis >= 0:
                raw.append(((m_all - m_dis) / m_all, k, k2))
    raw.sort()
    print(f"  {h:g}y unrounded coherent shares: {[round(s, 6) for s, _, _ in raw]}")
    print(f"       rounded (= committed)      : {[pct(s) for s, _, _ in raw]}")
    for pi in (0.05, 0.13, 0.20, 0.40):
        print(f"       pi={pi:.2f} closed form on unrounded s: "
              f"{sorted(pct((s - pi) / (1 - pi)) for s, _, _ in raw if s >= pi)}")
```
