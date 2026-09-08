> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

All stop-condition items are met. Report follows.

---

## Worker

**W17f**, lane 17 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). I did not observe the served model, and **no environment variable names a model**. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:31:52 UTC 2026`. `date -u` at end: `Tue Sep  8 02:36:33 UTC 2026`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (run at start; the model-relevant lines, verbatim — the full output is in the transcript and contains no model name):

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
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDECODE=1
SESSION_INGRESS_URL=https://api.anthropic.com
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

**Actual HEAD read.** `git rev-parse HEAD` at start: **`47aac85f874a57a6f981c3432abcf16980968aec`**. At end: **`7d081218f107363573573e6d102e4334567adf77`** — the coordinator committed collected reports during my run. The brief names `92abbcb9…` as the frozen read commit; I record what I actually read. My numeric results are byte-identical to W17b's (read at `103ff76f`) and W17d's, which is direct evidence both artifacts are unchanged across all four commits.

**Write isolation.** `git status --porcelain` at end shows one line, `M research/autonomy/opus-capacity-campaign-20260908/WAVE-LOG.md` — the coordinator's file, not mine. I created and modified nothing under `/home/user/Rare-cancers` and ran no git write operation. All execution was under `/tmp/claude-0/w17f/`.

---

## Question

**Can W17b's 872-block Welch variance inversion and W17d's 90-slot ATR part-B point verification be combined into one read-only test module that an existing repository test tier could host — and what would that tier pay?**

Open because both prior workers independently reached zero violations and both closed with the same finding: **neither test is reachable by any repository gate.** They exist only in campaign report bodies. A generator change that broke either identity would be caught by nobody. Verifying an artifact once by hand and verifying it on every run are different guarantees, and only the second survives the campaign.

---

## Prior-work check

Commands run against the live checkout and the frozen corpus:

- `rg -n "welch_EMC_vs_comparator" research/modalities/tests/ scripts/tests/ research/autonomy/tests/ systems/tests/ research/manuscripts/tests/` — **6 hits, none is this test.** `test_emc_expression_panels.py:219` asserts the block is `None` below the minimum n; `:491` checks the *sign* convention; `test_surface_address_sensitivity.py` constructs synthetic blocks; `test_emc_prmt5_route_controls.py:45` reads `t` as a route input. **No tier recomputes a variance from `per_sample[].z_vs_array`.**
- `rg -ni "satterthwaite|variance.*invert|invert.*variance" <all five tests dirs>` — 3 hits, all unrelated (`test_hysteresis_survives_the_early_returns.py` on a calibration CI, `test_ternary_coop_sign.py` on a ΔΔG number).
- `rg -l "emc-expression-panels|emc-atr-vulnerability" <tests dirs>` — the two natural host files exist (`research/modalities/tests/test_emc_expression_panels.py`, 39 test functions; `test_emc_atr_vulnerability.py`, 32) but both are **generator-behaviour** suites (framing, grading, determinism, monkeypatched selection), not artifact point verification.
- Frozen corpus `/tmp/claude-0/frozen-corpus/extracted/corpus/research/modalities/tests/` (449 files): `rg -ln "welch_EMC_vs_comparator"` returns the **same three files**, no additional gate. Absence there is UNKNOWN, not proof, per `CORPUS-CONTEXT.md` — but it is consistent with the live tree.
- `CLOSED-WORK.md` read in full. I am not replaying: PUB-EMC-CLASSIFICATION (user-rejected), any Brenca route, lane 11's source-index (W11b sole owner), any ASO/NAT or Qeios item, the frozen comment `7baf2727…`, the blocked NR4A Perspective, or any denied external route. I opened **no** review round on PUB-ATR, edited **no** manuscript or hardening-state file, touched **nothing** of W17c's MDE range, and ran **no** network call and **not** `scripts/preflight.sh`.

**W17d's report is not in `reports/`** — `find` for `*W17d*` over the tree and the corpus returns nothing; only `W17-heldout-validation.md`, `W17b-…`, `W17c-…` are collected. I therefore reconstructed W17d's half from its executable scratch artifact `/tmp/claude-0/w17d/atr_point_verify.py`, whose docstring states its derivation, tolerances and stage design in full, and which I re-executed to confirm it still produces W17d's numbers. **This is stronger evidence than the prose report would have been, but it means I could not cross-check my reading against W17d's own narrative Limitation list; Limitation 4 is as described to me in the dispatch, which I did not independently confirm.**

---

## Method / inputs

**Inputs, read-only:**
- `/home/user/Rare-cancers/research/modalities/emc-expression-panels.json` (13.2 MB; `gene_reads`, 958 gene×platform blocks, 872 carrying a Welch triple plus their own `per_sample` rows)
- `/home/user/Rare-cancers/research/modalities/emc-atr-vulnerability.json` (342,797 bytes; `part_b_emc_tumour_signature`)
- `/home/user/Rare-cancers/scripts/tier_budget.py`, `scripts/tier-budgets.json`
- `/home/user/Rare-cancers/research/modalities/emc_atr_vulnerability.py` (lines 2062–2091, the part-B emit site — read for the alignment-contract costing only)
- Prior work: `reports/W17b-exact-welch-variance-inversion.md`; `/tmp/claude-0/w17b/welch_variance_inversion.py`; `/tmp/claude-0/w17d/atr_point_verify.py`

**Tools:** `python3` 3.11.15 (system) and `/root/.local/share/uv/tools/pytest/bin/python` 3.11.15 with `pytest` 9.1.1, `pluggy` 1.6.0, `xdist` 3.8.0. Stdlib `json`/`math`/`itertools`/`ast`/`os` only. No network, no installs, no paid API, no GPU.

**Execution root:** `/tmp/claude-0/w17f/`. To exercise the shipping `__file__`-relative root resolution verbatim rather than a `/tmp`-special-cased variant, I created the mirror path `/tmp/claude-0/w17f/research/modalities/tests/` and placed **read-only symlinks** to the two artifacts at `/tmp/claude-0/w17f/research/modalities/`. Nothing was copied and nothing was written into the repository.

**What I preserved exactly, and did not re-derive.** Tolerances are propagated from each artifact's own print precision, not chosen: `dz = 5e-5` (4 dp on scores/z/means/delta), `dt = 5e-4` (3 dp on t), `ddf = 0.05` (1 dp on df); the rigorous worst-case variance error `d(s²) ≤ (2·dz·Σ|zᵢ−z̄| + n·dz²)/(n−1)`; `ddof=1`, with `ddof=0` computed **only** as a diagnostic on failure; and the ill-conditioning declaration `|t| ≤ 10·dt = 0.005 ⇒ T1 NOT EVALUABLE (UNKNOWN, never a pass)`.

**W17b's root-agnostic forward gate is preserved and is not silently resolved.** The inversion `f = v_a/S` solves a quadratic with discriminant `D = (1/A+1/B)/df − 1/(A·B)`; both roots are admissible whenever `df ≥ max(A,B)`. The module never picks a root. It gates on the algebraically equivalent forward form — observed `S` against `(Δ/t)²` (T1) and observed `df` against committed `df` (T2) — and adds a dedicated test that **measures** the ambiguity and fails if it ever collapses, precisely so a later "simplification" into an inversion cannot happen quietly.

**W17d's Stage-1 join recovery is preserved as a gating test, not an assumption.** The artifact nowhere states that `scores[c][i]` belongs to `sample_annotations_verbatim[i]`. The module recovers the comparator group by exhaustive search over all non-empty subsets of the non-EMC classes, admits a subset only if it reproduces *every* committed `mean_b` in the family simultaneously to `2·dz`, and **requires the winner to be unique** — zero admissible subsets is UNKNOWN, more than one is AMBIGUOUS, and either fails the test rather than picking.

---

## Result

### R1 — the combined module runs clean, and its numbers match both prior reports exactly

| Artifact | Blocks/slots gated | T0 δ | T1 scale | T2 df | T3 mean | Not evaluable | worst \|df_obs − df_c\| | Tier |
|---|---|---|---|---|---|---|---|---|
| `emc-expression-panels.json` | **872** | n/a | **0** | **0** | **0** | 2 (\|t\|≤0.005) | **0.049877** vs half-ulp 0.05 | PRIMARY |
| `emc-atr-vulnerability.json` part B | **90** (0 unresolved, 0 ambiguous) | **0** | **0** | **0** | reused from Stage 1 | 1 (\|t\|≤0.005) | **0.049986** vs half-ulp 0.05 | PRIMARY |
| **Total violations** | **962** | — | — | — | — | — | **0** | PRIMARY |

**Zero violations reproduced.** Every reported number is identical to the prior work: W17b's 872 / 0 / 0 / 0 / 2-ill-conditioned / 0.049877, and W17d's 90 / 0 / 0 / 0 / 0 / 1-ill-conditioned / 0.049986. **There is therefore no violation to classify as regression versus transcription error** — the reconstruction is faithful, and the "which is it" question does not arise. Had a violation appeared, the identical match on every other statistic would have localised it to my reconstruction; it did not appear.

Both worst-case df deviations sit *just* inside the print half-ulp (0.049877 and 0.049986 against 0.05) — 0.000123 and 0.000014 of margin. That is what pure 1-dp rounding predicts and nothing else does: a changed variance convention, grouping, or stale row set would miss by orders of magnitude, not by 0.03 %. **These are tight passes, not slack ones**, and they are the single sharpest evidence in this report.

### R2 — the module is not vacuous (measured, not asserted)

| Mutation applied in memory | Gate goes red | Tier |
|---|---|---|
| `delta + 0.001` **or** `df + 1` on a panel block | **872 / 872 blocks (100.0 %)** | PRIMARY |

I ran this because a test that passes on everything is indistinguishable from a test that checks nothing. It is a *lower* bound on sensitivity (a disjunction over two perturbations), consistent with W17b's per-perturbation 94–100 % band; I did not re-measure W17b's full power table, which stands as reported.

### R3 — tier arithmetic, measured

`python3 scripts/tier_budget.py` on the live tree, run by me:

| Tier | Directories | Measured | Budget | Headroom | After +8 | Fits? | Tier |
|---|---|---|---|---|---|---|---|
| commit-loop | `scripts/tests`, `research/autonomy/tests`, `systems/tests` | **1466** in 102 files | 1500 | **34** | 1474 | **yes** | PRIMARY |
| modalities | `research/modalities/tests` | **7247** in 436 files | 7500 | **253** | 7255 | **yes** | PRIMARY |
| paper-guards | `research/manuscripts/tests` | **966** in 111 files | 1000 | **34** | 974 | **yes** | PRIMARY |

`scripts/tier_budget.py --check` exits **0** today; no tier is over and none reports a shadowed name.

**Module cost, counted by the repository's own AST method** (`ast.walk`, names starting `test_`, plus `tier_budget._shadowed`): **8 test functions, 0 shadowed**, in 1 file. Runtime **0.26 s** for the 8 tests (0.43 s wall including interpreter start), on 13.5 MB of JSON.

**Feasibility statement, explicit.** **Yes — the `modalities` tier can carry it, and it is the correct host.** Its directory is `research/modalities/tests/`, the two artifacts are `research/modalities/*.json`, and 8 functions consume **3.2 % of its 253-function headroom**, leaving 245. The other two tiers would also *fit* arithmetically (34 headroom each, 8 needed), but both would be wrong homes and each would spend **24 % of its remaining headroom** on a test whose subject is a modality artifact: `commit-loop` is explicitly documented as "none of it is about a manuscript" and its directories do not contain these artifacts, and `paper-guards` is for the papers' own guards. **No budget file was changed, no ceiling was raised, and no test was added to any tier.** I measured the commit-loop tier at 1466/1500 independently; **W11c is measuring the same tier separately and I did not coordinate an answer with them** — if our figures differ, that difference is itself the finding.

The honest counter-argument, stated: `tier-budgets.json` says the modalities suite has **0 failures across eight committed `PREFLIGHT_FULL` logs** while costing 72 % of each run, and its ceiling is "deliberately close to the current count" because "this suite has already grown past the point where anyone reads its total". Adding to it is exactly the accretion the budget file exists to make somebody decide. My case for spending 8 of the 253 anyway: this is a **new surface, not a fourth guard on a covered one** — no tier recomputes a variance from committed rows — it costs 0.26 s, and the two artifacts it guards underwrite `emc-surface-target-landscape.md` and `emc-atr-vulnerability-assessment.md`. **That is a case for a decision-maker, not a decision I am entitled to take**, and I have not taken it.

### R4 — the alignment-contract proposal, costed

W17d's Limitation 4: the part-B positional join is *recovered*, not *declared*. I read the generator emit site to cost it.

**What I found that changes the framing:** `research/modalities/emc_atr_vulnerability.py:2086-2090` **already computes the joined per-sample record** — `pooled_rows.append({"gsm": s["gsm"], …, "scores": {c: scores[c][i] for c in scores}, "adj": {…}})`, iterating `for i, s in enumerate(samples)`. The alignment is therefore a fact **the generator already relies on**; it simply is not persisted into `part_b…per_platform`.

| Option | Change | Artifact cost | Test cost | Does it remove Limitation 4? | Tier |
|---|---|---|---|---|---|
| **(a)** declarative field, e.g. `"_scores_alignment": "scores[c][i] and proliferation_adjusted_scores[c][i] are the sample at sample_annotations_verbatim[i]"` | ~4 lines in one dict literal at `emc_atr_vulnerability.py:2073` | ~**1 KB** (one string × 11 platforms), **+0.3 %** on 342,797 bytes | **+1** test function (→ 9; modalities → 7256/7500) asserting the field exists **and** that the exhaustive-unique recovery agrees with it | **Only when paired with the module.** A string alone is an assertion that can drift from the code; it removes the *ambiguity of interpretation*, not the *risk of misalignment*. | PREDICTION |
| **(b)** persist the per-sample rows the generator already builds | ~3 lines (add `pooled_rows`-shaped list to `per_platform[mf]`) | **+74,454 bytes, +21.7 %** — measured, not estimated | +1 test function; the join becomes row-by-row, Stage-1 search becomes redundant | **Yes, outright** — the join is then *carried*, exactly as in `emc-expression-panels.json` | PREDICTION |

**Recommendation: (a), and only because the module makes it checkable.** (b) is the scientifically cleaner shape and would let the ATR half of the module drop its exhaustive search entirely, but it duplicates data already present in `scores`/`proliferation_adjusted_scores` at a 21.7 % size cost, and every consumer of the existing lists would still need them. (a) costs ~0.3 % and one test function, and the test that verifies it is already written.

**Routing — and the honest limit on it.** Both options require **writing the generator and regenerating a committed artifact**, which is outside my read-only mandate and outside this campaign's write isolation. Regeneration touches `research/modalities/emc-atr-vulnerability.json`, which is referenced by `research/manuscripts/pinned-figures.json` (1 match) and by ~20 other files including `systems/graph/artifacts.json`, `systems/graph/publications.json`, three `systems/views/` files, `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` and `research/manuscripts/claim-coverage.json`. **I did not verify whether a byte change to the artifact perturbs any pinned quantity or any `systems/views/` regeneration** — that check is part of the cost and I have not paid it. **Route: to the coordinator, for assignment to the owner of the ATR modality generator, as a single bounded change (a) + 1 test function, conditional on that pinned-figure and views-regeneration check coming back clean.** I am not the owner and have not opened it.

---

## Validation evidence

### RUN

**Environment for every run below:** container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, cwd `/tmp/claude-0/w17f`, stdlib only, no network. System `python3` is 3.11.15 **without pytest**; the repository's `uv` tool venv at `/root/.local/share/uv/tools/pytest/bin/python` is 3.11.15 **with** pytest 9.1.1 — this is the documented split described in `scripts/preflight.sh` and I used the tool venv for everything that imports pytest.

**Run 1 — W17b's original module re-executed unchanged**
`cd /tmp/claude-0/w17b && time python3 welch_variance_inversion.py; echo "EXIT=$?"`
```
real	0m0.115s
EXIT=0
max |df_obs - df_committed| over all blocks : 0.049877  ('NR4A2', 'GSE4303-GPL3290_series_matrix.txt.gz', 10, 6, 13.9, 13.94987735339006)
max relative |v_a implied - v_a observed|   : 1.000e+00  ('CXCL13', 'GSE4303-GPL3290_series_matrix.txt.gz', 0.002846084444444443, 0.0)
max relative |v_b implied - v_b observed|   : 1.000e+00  ('CD274', 'GSE4303-GPL3290_series_matrix.txt.gz', 0.0019121744444444463, 0.0)
blocks with TWO admissible inversion roots  : 227 (df >= max(n_a,n_b)-1)
blocks with near-zero discriminant (D<1e-6) : 21 (inversion ill-conditioned)
VERDICT: PASS
```

**Run 2 — W17d's original module re-executed unchanged**
`cd /tmp/claude-0/w17d && time python3 atr_point_verify.py; echo "EXIT=$?"`
```
real	0m0.025s
EXIT=0
concept slots enumerated (incl. null)      : 408
  non-null slots                           : 306
  slots carrying BOTH t and df (testable)  : 90
  slots actually point-tested              : 90
T0 delta identity        : 0 violation(s)
T1 scale  S vs (D/t)^2   : 0 violation(s)   [1 ill-conditioned |t|<=0.005, not evaluable]
T2 shape  df_obs vs df_c : 0 violation(s)
T3 means (Stage-1 reuse) : 0 violation(s)
max |df_obs - df_committed| : 0.049986  ('GSE24369_series_matrix.txt.gz', 'contrast_EMC_vs_NONFET_comparators', 'replication_stress', 6, 12, 12.3, 12.250014188613829)
max relative |S_obs - (delta/t)^2| / S_obs : 2.221e-02  ('GSE24369_series_matrix.txt.gz', 'contrast_EMC_vs_FET_comparators', 'ATM_signalling_DSB_repair', 0.0002245812200115339, 0.00022956841138659323)
slots with TWO admissible inversion roots  : 54
slots with near-zero discriminant (D<1e-6) : 0
VERDICT: PASS
```

**Run 3 — the combined module, under pytest**
`cd /tmp/claude-0/w17f && time /root/.local/share/uv/tools/pytest/bin/python -m pytest research/modalities/tests/test_committed_welch_blocks_invert_to_their_own_rows.py -v -p no:cacheprovider; echo "EXIT=$?"`
```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /root/.local/share/uv/tools/pytest/bin/python
rootdir: /tmp/claude-0/w17f
plugins: xdist-3.8.0
collecting ... collected 8 items

...::test_every_panel_welch_block_matches_the_scale_implied_by_its_own_rows PASSED [ 12%]
...::test_every_panel_welch_df_matches_the_variances_from_its_own_rows PASSED [ 25%]
...::test_every_panel_welch_mean_matches_its_own_rows PASSED [ 37%]
...::test_the_atr_positional_join_recovers_exactly_one_comparator_group PASSED [ 50%]
...::test_every_atr_slot_delta_equals_its_own_two_committed_means PASSED [ 62%]
...::test_every_atr_slot_matches_the_scale_implied_by_the_joined_scores PASSED [ 75%]
...::test_every_atr_slot_df_matches_the_variances_from_the_joined_scores PASSED [ 87%]
...::test_the_gate_is_root_agnostic_because_the_branch_ambiguity_is_real PASSED [100%]

============================== 8 passed in 0.26s ===============================

real	0m0.432s
EXIT=0
```

**Run 4 — per-artifact violation census, using the module's own functions**
`cd /tmp/claude-0/w17f && time /root/.local/share/uv/tools/pytest/bin/python census.py; echo "EXIT=$?"`
```
ARTIFACT A  emc-expression-panels.json
  blocks entering the gate            : 872
  T1 scale violations                 : 0   [2 not evaluable, |t|<=0.005]
  T2 df violations                    : 0
  T3 mean violations                  : 0
  worst |df_obs - df_committed|       : 0.049877  (print half-ulp 0.05)
ARTIFACT B  emc-atr-vulnerability.json (part B)
  slots uniquely joined + gated       : 90   (unresolved: 0, ambiguous families: 0)
  T0 delta-identity violations        : 0
  T1 scale violations                 : 0   [1 not evaluable]
  T2 df violations                    : 0
  worst |df_obs - df_committed|       : 0.049986  (print half-ulp 0.05)
TOTAL VIOLATIONS ACROSS BOTH ARTIFACTS : 0

real	0m0.251s
EXIT=0
```

**Run 5 — non-vacuity mutation**
`cd /tmp/claude-0/w17f && /root/.local/share/uv/tools/pytest/bin/python mutate.py; echo "EXIT=$?"`
```
ARTIFACT A mutation  delta+0.001 OR df+1  -> gate goes red on 872/872 blocks (100.0%)
EXIT=0
```

**Run 6 — tier budget, measured, unmodified**
`cd /home/user/Rare-cancers && python3 scripts/tier_budget.py --check; echo "TIER_CHECK_EXIT=$?"`
```
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
TIER_CHECK_EXIT=0
```
and the headroom arithmetic from `--json`:
```
commit-loop    measured= 1466 budget= 1500 headroom=  34  after +8 ->  1474  fits=True
modalities     measured= 7247 budget= 7500 headroom= 253  after +8 ->  7255  fits=True
paper-guards   measured=  966 budget= 1000 headroom=  34  after +8 ->   974  fits=True
```

**Run 7 — module cost by the repository's own AST method**
```
AST test functions (tier_budget.count_dir method): 8
shadowed: []
```

**Run 8 — artifact-size cost of alignment-contract option (b)**, from the committed artifact:
```
artifact bytes: 342797
 ... 11 platforms ...
total added bytes (option b): 74454
```

**Run 9 — write isolation**
`git status --porcelain && git rev-parse HEAD && date -u`
```
 M research/autonomy/opus-capacity-campaign-20260908/WAVE-LOG.md
7d081218f107363573573e6d102e4334567adf77
Tue Sep  8 02:36:33 UTC 2026
```
The one modified file is the coordinator's wave log. Nothing of mine.

### PROPOSED (NOT RUN)

- **Placing this module at `research/modalities/tests/test_committed_welch_blocks_invert_to_their_own_rows.py`.** I did not create it in the tree. Its tier effect is computed above (modalities 7247 → 7255 / 7500) but **not observed**, because observing it would require the write I am forbidden.
- **A `PREFLIGHT_FULL` or `scripts/preflight.sh` run.** Explicitly excluded by my dispatch; not run. The 0.26 s figure is the module in isolation, **not** a measurement of the modalities tier's total runtime, and I make no claim about the latter.
- **Alignment-contract options (a) and (b).** Neither generator edit was written or executed. The +1 KB / +74,454-byte figures are computed from the committed artifact; the *downstream* effect of regenerating it on `pinned-figures.json` and `systems/views/` is **unchecked**.

### The module, returned inline (authored nowhere in the tree)

`/tmp/claude-0/w17f/research/modalities/tests/test_committed_welch_blocks_invert_to_their_own_rows.py`:

```python
"""A committed Welch triple must be recoverable from the rows it claims to summarise.

⛔⛔ WHAT THIS EXISTS FOR. Two campaign workers point-verified two artifacts by hand and both
reported the same hole: NEITHER TEST IS REACHABLE BY ANY REPOSITORY GATE. W17b inverted the 872
`welch_EMC_vs_comparator` blocks in `emc-expression-panels.json` against their own
`per_sample[].z_vs_array` rows; W17d recovered the positional join in `emc-atr-vulnerability.json`
part B by exhaustive unique search and point-verified all 90 statistic-bearing slots. Both runs
were clean. Both lived only in a report body, so a generator change that broke either identity
would be caught by nobody. This module is those two verifications, merged, so a tier owns them.

★ THE IDENTITY. A committed block prints (delta, t, df, n_a, n_b). With v_a = s_a^2/n_a,
v_b = s_b^2/n_b, S = v_a+v_b, A = n_a-1, B = n_b-1:

    (i)  t  = delta / sqrt(S)                      =>  S = (delta/t)^2          [T1, scale]
    (ii) df = S^2 / (v_a^2/A + v_b^2/B)                                         [T2, shape]

That OVER-DETERMINES the variance pair, which is what makes a point test possible at all. With
f = v_a/S, (ii) is scale-free: f^2/A + (1-f)^2/B = 1/df, a quadratic whose discriminant
D = (1/A+1/B)/df - 1/(A*B) is >= 0 exactly when df <= A+B — the feasibility ceiling an earlier
gate checked on its own falls out of this algebra as a corollary.

⛔ THE BRANCH AMBIGUITY IS REAL AND IS NOT RESOLVED HERE. Both roots of that quadratic lie in
[0,1] whenever df >= max(A,B): 227 of 872 panel blocks and 54 of 90 ATR slots are two-root.
Picking a root to make an assertion simpler would be inventing a fact the artifact does not carry.
So the gate is the algebraically equivalent FORWARD form — check the OBSERVED S against
(delta/t)^2 and the OBSERVED df against the committed df — which is root-agnostic and is exactly
"the observed (v_a, v_b) satisfies both Welch equations". `test_the_gate_is_root_agnostic` guards
that this stays true if someone later edits the file.

⚠ TOLERANCES ARE PROPAGATED FROM THE ARTIFACTS' OWN PRINT PRECISION, NOT CHOSEN. Scores, z-values,
means and delta print to 4 dp (dz = 5e-5); t to 3 dp (dt = 5e-4); df to 1 dp (ddf = 0.05). The
worst-case error on a sample variance is bounded rigorously by
d(s^2) <= (2*dz*sum|z_i - zbar| + n*dz^2)/(n-1), and each test asks whether the observed INTERVAL
intersects the committed one. A flat epsilon here would be a number somebody picked; this is not.
⛔ A slot with |t| <= 10*dt = 0.005 makes the implied scale diverge: T1 is NOT EVALUABLE there and
is recorded UNKNOWN, never counted as a pass. Sample variance is ddof=1. ddof=0 is computed only
as a diagnostic on a failure, to say WHICH convention drifted.

★ SCOPE. This is bookkeeping, not biology. It says a committed summary is a faithful summary of
its own rows. It says nothing whatever about EMC efficacy, safety, selectivity or clinical
readiness, and a closed verification loop is not a correct one.
"""

from __future__ import annotations

import itertools
import json
import math
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PANELS = os.path.join(ROOT, "research", "modalities", "emc-expression-panels.json")
ATR = os.path.join(ROOT, "research", "modalities", "emc-atr-vulnerability.json")

DZ, DT, DDF = 5e-5, 5e-4, 0.05
ILL = 10.0 * DT  # |t| at or below this makes (delta/t)^2 meaningless — UNKNOWN, not passed

FAMS = (
    "contrast_EMC_vs_all_comparator_sarcoma",
    "contrast_EMC_vs_all_comparator_sarcoma_PROLIFERATION_ADJUSTED",
    "contrast_EMC_vs_FET_comparators",
    "contrast_EMC_vs_NONFET_comparators",
)
ADJ = {"contrast_EMC_vs_all_comparator_sarcoma_PROLIFERATION_ADJUSTED"}


# ---------------------------------------------------------------- shared algebra

def _var(xs, ddof=1):
    n = len(xs)
    m = sum(xs) / n
    return sum((x - m) ** 2 for x in xs) / (n - ddof), m


def _dvar(xs):
    """Rigorous worst-case error on s^2 given every x is printed to within DZ."""
    n = len(xs)
    m = sum(xs) / n
    return (2 * DZ * sum(abs(x - m) for x in xs) + n * DZ * DZ) / (n - 1)


def _df_of(va, vb, A, B):
    S = va + vb
    return S * S / (va * va / A + vb * vb / B)


def _froots(A, B, df):
    P = 1.0 / A + 1.0 / B
    D = P / df - 1.0 / (A * B)
    if D < 0:
        return None, D
    r = math.sqrt(D)
    return sorted(((1.0 / B - r) / P, (1.0 / B + r) / P)), D


def _t1(za, zb, t_c, dl_c):
    """(verdict, detail). verdict is True, False, or None == not evaluable."""
    na, nb = len(za), len(zb)
    s2a, _ = _var(za)
    s2b, _ = _var(zb)
    va, vb = s2a / na, s2b / nb
    S = va + vb
    dS = _dvar(za) / na + _dvar(zb) / nb
    at, ad = abs(t_c), abs(dl_c)
    if at <= ILL:
        return None, ("|t| <= %g, implied scale diverges" % ILL)
    hi = ((ad + DZ) / (at - DT)) ** 2
    lo = (max(ad - DZ, 0.0) / (at + DT)) ** 2
    ok = not (S + dS < lo or S - dS > hi)
    return ok, (S, dS, lo, hi, (dl_c / t_c) ** 2)


def _t2(za, zb, df_c):
    na, nb = len(za), len(zb)
    A, B = na - 1, nb - 1
    s2a, _ = _var(za)
    s2b, _ = _var(zb)
    va, vb = s2a / na, s2b / nb
    dva, dvb = _dvar(za) / na, _dvar(zb) / nb
    corners = [_df_of(va + sa * dva, vb + sb * dvb, A, B) for sa in (-1, 1) for sb in (-1, 1)]
    lo, hi = min(corners), max(corners)
    ok = not (hi < df_c - DDF or lo > df_c + DDF)
    detail = (_df_of(va, vb, A, B), lo, hi)
    if not ok:  # diagnostic only, on failure: did the generator switch to ddof=0?
        s2a0, _ = _var(za, 0)
        s2b0, _ = _var(zb, 0)
        detail = detail + ("ddof=0 would give df=%.4f" % _df_of(s2a0 / na, s2b0 / nb, A, B),)
    return ok, detail


# ---------------------------------------------------------------- artifact A: panels

@pytest.fixture(scope="module")
def panel_blocks():
    """Every expression-panel block that carries a Welch triple AND its own rows.

    ⛔ A block whose per_sample row count disagrees with its committed n is NOT skipped — it is
    surfaced as a mismatch, because that is precisely the corruption this module is for.
    """
    with open(PANELS, encoding="utf-8") as fh:
        doc = json.load(fh)
    out, bad_n = [], []
    for gene, plats in doc["gene_reads"].items():
        for plat, b in plats.items():
            if not isinstance(b, dict):
                continue
            w = b.get("welch_EMC_vs_comparator")
            ps = b.get("per_sample")
            na, nb = b.get("n_EMC_with_a_value"), b.get("n_comparator_with_a_value")
            if not isinstance(w, dict) or not isinstance(ps, list):
                continue
            if None in (na, nb, w.get("df"), w.get("t"), w.get("delta_a_minus_b")):
                continue
            za = [r["z_vs_array"] for r in ps
                  if r.get("class") == "EMC" and isinstance(r.get("z_vs_array"), (int, float))]
            zb = [r["z_vs_array"] for r in ps
                  if r.get("class") != "EMC" and isinstance(r.get("z_vs_array"), (int, float))]
            if (len(za), len(zb)) != (na, nb):
                bad_n.append((gene, plat, na, nb, len(za), len(zb)))
                continue
            if na < 2 or nb < 2:
                continue
            out.append((gene, plat, za, zb, w))
    assert not bad_n, "per_sample row counts disagree with the committed n: %r" % (bad_n[:10],)
    assert len(out) > 800, "the panel artifact stopped carrying its Welch blocks: %d" % len(out)
    return out


def test_every_panel_welch_block_matches_the_scale_implied_by_its_own_rows(panel_blocks):
    bad, unevaluable = [], 0
    for gene, plat, za, zb, w in panel_blocks:
        ok, detail = _t1(za, zb, w["t"], w["delta_a_minus_b"])
        if ok is None:
            unevaluable += 1
        elif not ok:
            bad.append((gene, plat, len(za), len(zb), w["t"], w["delta_a_minus_b"], detail))
    assert not bad, "v_a+v_b from the rows does not equal (delta/t)^2 in %d block(s): %r" % (
        len(bad), bad[:5])
    assert unevaluable <= 5, "too many blocks have |t| <= %g to evaluate: %d" % (ILL, unevaluable)


def test_every_panel_welch_df_matches_the_variances_from_its_own_rows(panel_blocks):
    bad, worst = [], (0.0, None)
    for gene, plat, za, zb, w in panel_blocks:
        ok, detail = _t2(za, zb, w["df"])
        if not ok:
            bad.append((gene, plat, len(za), len(zb), w["df"], detail))
        e = abs(detail[0] - w["df"])
        if e > worst[0]:
            worst = (e, (gene, plat, w["df"], detail[0]))
    assert not bad, "recomputed Satterthwaite df disagrees with the committed df in %d block(s): %r" % (
        len(bad), bad[:5])
    # ⚠ The committed df prints to 1 dp, so no deviation can legitimately exceed the half-ulp.
    assert worst[0] <= DDF, "worst df deviation %.6f exceeds the print half-ulp at %r" % worst


def test_every_panel_welch_mean_matches_its_own_rows(panel_blocks):
    bad = []
    for gene, plat, za, zb, w in panel_blocks:
        for arm, xs in (("mean_a", za), ("mean_b", zb)):
            c = w.get(arm)
            if c is None:
                continue
            m = sum(xs) / len(xs)
            if abs(m - c) > 2 * DZ:
                bad.append((gene, plat, arm, m, c))
    assert not bad, "committed arm mean is not the mean of its own rows in %d case(s): %r" % (
        len(bad), bad[:5])


# ---------------------------------------------------------------- artifact B: ATR part B

@pytest.fixture(scope="module")
def atr_panels():
    """Score panels plus the pooled concatenation, and the committed part-B blocks.

    ⛔⛔ THE JOIN IS A HYPOTHESIS, NOT AN ASSUMPTION. This artifact carries no per-sample rows. It
    carries `scores[concept]` (len == n_samples) and `sample_annotations_verbatim` (len ==
    n_samples) and NOTHING that states they are positionally aligned. This fixture only assembles;
    `test_the_atr_positional_join_recovers_exactly_one_comparator_group` is where the alignment is
    EARNED, by requiring a unique class subset that reproduces every committed mean.
    """
    with open(ATR, encoding="utf-8") as fh:
        doc = json.load(fh)
    B = doc["part_b_emc_tumour_signature"]
    panels = {}
    for name, b in B["per_platform"].items():
        lbl = [r["class"] for r in b["sample_annotations_verbatim"]]
        assert len(lbl) == b["n_samples"], "%s: annotations do not match n_samples" % name
        panels[name] = (lbl, b.get("scores") or {}, b.get("proliferation_adjusted_scores") or {})
    # The pooled block is the concatenation of the GSE4303 platforms — the artifact's own stated
    # scope is "platforms of GSE4303 only, never across series". Order does not affect any group
    # mean or variance; the class_counts identity below is what pins the membership.
    g4 = sorted(n for n, b in B["per_platform"].items() if b.get("series") == "GSE4303")
    concepts = set()
    for n in g4:
        concepts |= set(panels[n][1].keys())
    plbl, psc, ppa = [], {}, {}
    for n in g4:
        lbl, sc, pa = panels[n]
        plbl += lbl
        for c in concepts:
            psc.setdefault(c, []).extend(sc.get(c, [None] * len(lbl)))
            ppa.setdefault(c, []).extend(pa.get(c, [None] * len(lbl)))
    counts = {}
    for c in plbl:
        counts[c] = counts.get(c, 0) + 1
    assert counts == B["cross_platform_pooled"]["class_counts"], (
        "pooled class_counts is not the sum of the platforms it pools: %r vs %r"
        % (counts, B["cross_platform_pooled"]["class_counts"]))
    assert len(plbl) == B["cross_platform_pooled"]["n_samples_pooled"]
    panels["cross_platform_pooled"] = (plbl, psc, ppa)
    blocks = list(B["per_platform"].items()) + [("cross_platform_pooled", B["cross_platform_pooled"])]
    return panels, blocks


def _recover(panels, blocks):
    """(panel, family) -> list of admissible (class subset, n_b). Exhaustive; never picks."""
    rec = {}
    for name, b in blocks:
        lbl, sc, pa = panels[name]
        nonemc = sorted(set(lbl) - {"EMC"})
        ia = [i for i, l in enumerate(lbl) if l == "EMC"]
        for fam in FAMS:
            live = {c: s for c, s in (b.get(fam) or {}).items()
                    if isinstance(s, dict) and "t" in s and "df" in s}
            if not live:
                continue
            src = pa if fam in ADJ else sc
            amax, aok = 0.0, True
            for c, s in live.items():
                v = src.get(c)
                if not v or any(v[i] is None for i in ia):
                    aok = False
                    break
                amax = max(amax, abs(sum(v[i] for i in ia) / len(ia) - s["mean_a"]))
            if not aok or amax > 2 * DZ:
                rec[(name, fam)] = ("MEAN_A_FAIL", amax if aok else None)
                continue
            adm = []
            for k in range(1, len(nonemc) + 1):
                for sub in itertools.combinations(nonemc, k):
                    ib = [i for i, l in enumerate(lbl) if l in sub]
                    if len(ib) < 2:
                        continue
                    ok = True
                    for c, s in live.items():
                        v = src.get(c)
                        if not v or any(v[i] is None for i in ib) \
                                or abs(sum(v[i] for i in ib) / len(ib) - s["mean_b"]) > 2 * DZ:
                            ok = False
                            break
                    if ok:
                        adm.append((sub, len(ib)))
            rec[(name, fam)] = adm
    return rec


def _atr_slots(panels, blocks):
    """Every part-B slot whose comparator group was UNIQUELY recovered, with its two arms."""
    rec = _recover(panels, blocks)
    out, unresolved = [], []
    for name, b in blocks:
        lbl, sc, pa = panels[name]
        for fam in FAMS:
            for c, s in (b.get(fam) or {}).items():
                if not isinstance(s, dict) or "t" not in s or "df" not in s:
                    continue
                r = rec.get((name, fam))
                if not isinstance(r, list) or len(r) != 1:
                    unresolved.append((name, fam, c, r))
                    continue
                sub, nb = r[0]
                v = (pa if fam in ADJ else sc).get(c)
                za = [v[i] for i, l in enumerate(lbl) if l == "EMC"]
                zb = [v[i] for i, l in enumerate(lbl) if l in sub]
                if len(za) < 2 or nb < 2:
                    unresolved.append((name, fam, c, "n<2"))
                    continue
                out.append((name, fam, c, za, zb, s))
    return out, unresolved


@pytest.fixture(scope="module")
def atr_slots(atr_panels):
    slots, _ = _atr_slots(*atr_panels)
    return slots


def test_the_atr_positional_join_recovers_exactly_one_comparator_group(atr_panels):
    """⛔ If this ever goes AMBIGUOUS or UNKNOWN, the three tests below are testing nothing.

    The artifact does not declare that `scores` is aligned with `sample_annotations_verbatim`.
    This recovers the alignment by exhaustive search over every non-empty subset of the non-EMC
    classes and requires the winner to be UNIQUE — reproducing every committed mean_b in the
    family simultaneously. Zero admissible subsets means the join is unestablished; more than one
    means the artifact cannot distinguish them and NOTHING may be pointed at either.
    """
    panels, blocks = atr_panels
    slots, unresolved = _atr_slots(panels, blocks)
    assert not unresolved, "%d part-B slot(s) have no uniquely recovered comparator group: %r" % (
        len(unresolved), unresolved[:5])
    assert len(slots) >= 90, "part B stopped carrying its statistic-bearing slots: %d" % len(slots)


def test_every_atr_slot_delta_equals_its_own_two_committed_means(atr_panels):
    _, blocks = atr_panels
    bad = []
    for name, b in blocks:
        for fam in FAMS:
            for c, s in (b.get(fam) or {}).items():
                if not isinstance(s, dict) or "t" not in s or "df" not in s:
                    continue
                if abs((s["mean_a"] - s["mean_b"]) - s["delta_a_minus_b"]) > 3 * DZ:
                    bad.append((name, fam, c, s["mean_a"] - s["mean_b"], s["delta_a_minus_b"]))
    assert not bad, "delta_a_minus_b is not mean_a - mean_b in %d slot(s): %r" % (len(bad), bad[:5])


def test_every_atr_slot_matches_the_scale_implied_by_the_joined_scores(atr_slots):
    bad, unevaluable = [], 0
    for name, fam, c, za, zb, s in atr_slots:
        ok, detail = _t1(za, zb, s["t"], s["delta_a_minus_b"])
        if ok is None:
            unevaluable += 1
        elif not ok:
            bad.append((name, fam, c, len(za), len(zb), s["t"], detail))
    assert not bad, "v_a+v_b from the joined scores does not equal (delta/t)^2 in %d slot(s): %r" % (
        len(bad), bad[:5])
    assert unevaluable <= 2, "too many slots have |t| <= %g to evaluate: %d" % (ILL, unevaluable)


def test_every_atr_slot_df_matches_the_variances_from_the_joined_scores(atr_slots):
    bad, worst = [], (0.0, None)
    for name, fam, c, za, zb, s in atr_slots:
        ok, detail = _t2(za, zb, s["df"])
        if not ok:
            bad.append((name, fam, c, len(za), len(zb), s["df"], detail))
        e = abs(detail[0] - s["df"])
        if e > worst[0]:
            worst = (e, (name, fam, c, s["df"], detail[0]))
    assert not bad, "recomputed df disagrees with the committed df in %d slot(s): %r" % (
        len(bad), bad[:5])
    assert worst[0] <= DDF, "worst df deviation %.6f exceeds the print half-ulp at %r" % worst


# ---------------------------------------------------------------- the invariant that keeps it honest

def test_the_gate_is_root_agnostic_because_the_branch_ambiguity_is_real(panel_blocks, atr_slots):
    """⛔⛔ THE ONE THING A LATER EDIT MUST NOT DO IS PICK A ROOT.

    Inverting df to a variance SPLIT gives a quadratic with two roots, and both are admissible
    whenever df >= max(n_a,n_b)-1. This measures how often that happens — if it were rare, someone
    would eventually 'simplify' the tests above into an inversion, and would be silently choosing
    one of two variance pairs the artifact does not distinguish. It is not rare. The forward form
    the tests above use is the only form the data supports.
    """
    two_root = degenerate = 0
    for _, _, za, zb, w in panel_blocks:
        rr, D = _froots(len(za) - 1, len(zb) - 1, w["df"])
        if rr is None:
            continue
        adm = [f for f in rr if -1e-9 <= f <= 1 + 1e-9]
        if len(adm) == 2 and abs(adm[0] - adm[1]) > 1e-9:
            two_root += 1
        if D < 1e-6:
            degenerate += 1
    atr_two_root = 0
    for _, _, _, za, zb, s in atr_slots:
        rr, _ = _froots(len(za) - 1, len(zb) - 1, s["df"])
        if rr is None:
            continue
        adm = [f for f in rr if -1e-9 <= f <= 1 + 1e-9]
        if len(adm) == 2 and abs(adm[0] - adm[1]) > 1e-9:
            atr_two_root += 1
    assert two_root > 100, (
        "panel branch ambiguity collapsed to %d blocks — re-derive before trusting any inversion"
        % two_root)
    assert atr_two_root > 20, "ATR branch ambiguity collapsed to %d slots" % atr_two_root
    # Degenerate discriminants sit exactly on the feasibility ceiling df == n_a+n_b-2. They are
    # legal, and they are the blocks where an inversion would be worst conditioned.
    assert degenerate < len(panel_blocks) // 10
```

---

## Limitations

1. **A closed verification loop is not a correct one.** This module proves each committed summary is a faithful summary of *its own rows*. It cannot detect a fault upstream of those rows — a mis-parsed series matrix, a wrong probe→symbol mapping, a mis-assigned `class` label. Every arm would be self-consistent and every test would pass.
2. **Bookkeeping, not biology.** Nothing here bears on EMC efficacy, safety, selectivity, therapeutic window or clinical readiness. There is no wet lab and no new data; I read only already-committed derived fields.
3. **The tier figures are counts, not seconds.** `tier_budget.py` documents this itself: it counts test *functions*, not collected tests and not runtime. My 0.26 s is this module alone on this box; I did not measure the modalities tier's total runtime, and I did not run `preflight.sh`.
4. **I did not place the module in the tree, so its tier effect is arithmetic, not observation.** 7247 + 8 = 7255 is a computation; nobody has seen `tier_budget.py` report it.
5. **The ATR positional join remains recovered, not declared.** My Stage-1 test *is* the recovery, so the module depends on the same evidence W17d used. If a future artifact revision made two class subsets reproduce every mean, the test would go AMBIGUOUS and fail — correctly — but the alignment would still be unknown. That is exactly the gap the routed proposal addresses, and it is not closed by this module.
6. **Ill-conditioned slots are UNKNOWN, not passed.** 2 panel blocks and 1 ATR slot have |t| ≤ 0.005 and are excluded from T1. The module caps how many may be so excluded (5 and 2) so the exclusion cannot silently grow, but those three are genuinely unverified on the scale identity.
7. **W17d's own report was unavailable to me.** I reconstructed from its executable scratch script, which is more verifiable but means I could not check my summary against W17d's own narrative. My statement of its Limitation 4 comes from the dispatch prompt, not from W17d.
8. **Novelty is `rg` over the live tree plus the frozen corpus.** Per `CORPUS-CONTEXT.md`, absence there is UNKNOWN, not proof of repository-wide absence.
9. **The commit-loop figure is mine alone.** W11c is measuring the same tier; I did not coordinate, and a discrepancy between us is a finding, not an error to reconcile away.
10. **Option (b)'s +21.7 % is a measured size cost only.** I did not check whether regenerating `emc-atr-vulnerability.json` perturbs `pinned-figures.json` or any `systems/views/` output — an unpaid part of the cost of either option.

---

## Stop condition

**Set:** (i) the combined module executed with a real exit code and per-artifact violation counts; (ii) a measured tier-budget figure with an explicit feasibility statement; (iii) the alignment-contract proposal costed and routed.

**MET, all three.**
(i) `8 passed in 0.26s`, **exit 0**; census exit 0 with **872 blocks / 0 violations** on `emc-expression-panels.json` and **90 slots / 0 violations** on `emc-atr-vulnerability.json` part B, **0 total** — numerically identical to both prior reports, so no violation required classification as regression versus transcription error.
(ii) `tier_budget.py` run by me: commit-loop **1466/1500**, modalities **7247/7500**, paper-guards **966/1000**, `--check` exit 0; module costs **8 test functions, 0 shadowed** by the repository's own AST method; **the modalities tier can carry it** (7255/7500, 3.2 % of its headroom) and is the correct host.
(iii) Option (a) costed at ~4 generator lines, +~1 KB (+0.3 %), +1 test function, and routed to the coordinator for the ATR generator's owner, conditional on a pinned-figure and views-regeneration check; option (b) costed at **+74,454 bytes (+21.7 %)**, measured, and not recommended.

**No budget file changed, no ceiling raised, no test added to any tier, nothing authored into the working tree.**

---

## Tool-call and wall-clock count actually used

**19 tool calls.** Wall clock **02:31:52Z → 02:36:33Z = 4 min 41 s**. Both well inside the ~40/~40 target; I returned as soon as the stop condition was met and did not pad.

---

## Next concrete action

**One task, for whoever owns integration:** land `test_committed_welch_blocks_invert_to_their_own_rows.py` verbatim at `research/modalities/tests/`, then run `python3 scripts/tier_budget.py --check` and confirm it reports `modalities 7255/7500` and exit 0 — turning this report's arithmetic into an observation. That single commit is what actually closes the gap both W17b and W17d named; until it happens, these two verifications remain unreachable by any gate and this report is one more of the report bodies the finding is about.

The alignment contract is a **separate, later** task and should not be bundled: it edits a generator and regenerates a consumed artifact, and its pinned-figure blast radius is unmeasured.
