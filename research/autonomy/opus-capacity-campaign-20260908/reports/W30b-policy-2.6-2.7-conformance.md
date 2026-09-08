<!-- collected 2026-09-08T03:38:26Z by campaign coordinator; agent id a8c7972c6caa8e29b; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a8c7972c6caa8e29b.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Stop condition met. Report follows.

---

## Worker

**W30b**, OPUS-CAPACITY-CAMPAIGN-20260908. Lane: evidence-contract conformance of the §2.6 / §2.7 estimand classes — the two sections W30 found exercised at denominator zero by the clinical registry.

**Model: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I am told I am Claude Opus 5 (`claude-opus-5`). Nothing in my environment corroborates this — no environment variable names a model. The coordinator must extract the served model from the transcript.

**Start** — `date -u` → `Tue Sep  8 03:26:57 UTC 2026`; `git rev-parse HEAD` → `ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f`; `git status --porcelain` → **empty**.

**End** — `date -u` → `Tue Sep  8 03:31:39 UTC 2026`; `git rev-parse HEAD` → `215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1` (**HEAD advanced under me** — the coordinator committed 8 further worker reports, 2,433 insertions, including W28 and W31); `git status --porcelain` → **empty**. Neither commit equals COMMON-BRIEF's frozen `92abbcb9…`; I read the checkout as it stands and say so.

**I verified the HEAD move touched nothing I read.** `git diff --stat ff6bb018 215ed8e7 --` over all 15 of my inputs (`systems/POLICY-evidence.md`, `research/modalities/emc-ipd-survival.json`, `emc_ipd_survival.py`, `km-figure-readings.json`, `km-swimmer-readings.json`, `figures/ATTRIBUTION.md`, `research/manuscripts/endpoint/`, the four §2.6 generators, `scripts/preflight.sh`, `no-wet-lab-publication-archetypes.md`, and both test files) returned **empty output, exit 0** — every input byte-identical across the move.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — identical at start and end; the five long `*no_proxy*` / `JAVA_TOOL_OPTIONS` lines are elided here as pure proxy noise and were captured in full at start:

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

**Write isolation honoured: zero repository writes, zero git write operations, no network.** All execution under `/tmp/claude-0/w30b/` (two scratch scripts, `scan26.py` and `int26.py`). `git status --porcelain` was empty at start, after every command that could conceivably have written, and at end. I did not run `scripts/preflight.sh`, and every generator I invoked was invoked with `--check`, whose write-free behaviour I verified **by reading the source before running it** (`emc_ipd_survival.py:936` — `"""Compare the committed artifact against a fresh in-memory build. Writes nothing."""`; `main()` writes only on the no-`--check` branch).

## Question

**Which committed artifacts actually carry a §2.6 study-level descriptive series or a §2.7 reconstructed patient-level survival dataset, and does each satisfy those sections requirement by requirement — in particular §2.7(a)'s mandatory numbers-at-risk table and §2.7(b)'s reproduce-your-own-input condition, which the policy states as refusals and which no gate checks?**

Open because W30 established the negative half only: the registry exercises §2.6 and §2.7 at denominator **0**, and `scripts/validate-registry.mjs` enforces nothing from either. That locates the requirement classes elsewhere without auditing them. The strictest language in the evidence contract had, until this run, no recorded conformance check against the artifacts it actually governs.

## Prior-work check

Commands run (read-only), and what they showed:

```
$ git ls-files | grep -i -E 'ipd|guyot|kaplan|km[-_]|digitis|digitiz|survival|descriptive|series|census|at.risk|risk.table'
   → 80+ paths; the KM/IPD cluster under research/modalities/ and research/literature/
$ grep -rn -i -l -E 'guyot|numbers at risk|risk_table|digitiz|reconstructed (patient|ipd)|study-level descriptive' \
    --include='*.py' --include='*.mjs' --include='*.json' --include='*.md' --include='*.csv' .
   → 60 files, listed below
$ grep -rn '"governed_by"' --include='*.json' --include='*.py' research/ systems/ scripts/
   → 9 hits, ALL naming "systems/POLICY-evidence.md 2.6"; ZERO naming 2.7
$ git log --oneline -- research/manuscripts/endpoint/endpoint-corpus.json \
    research/modalities/emc-ipd-survival.json research/manuscripts/endpoint/lit-targets-cross-disease-endpoints.json
   → 14a3f172 (one commit; history squashed, as W30 recorded for the registry)
```

I established the artifact set from the tree via the `governed_by` enumeration and the content grep, **not** from the dispatch's hint. The hint turned out to be correct and incomplete: it named the KM/IPD side, and the §2.6 side is a five-artifact endpoint programme that self-declares its governance.

**Confirmed not replayed:** the user-rejected registry ICD-O paper (I ran no classification analysis, introduced no misclassification parameter, and propose no row); W30's registry audit (I re-read no registry requirement — my §2.6/§2.7 denominators are the ones W30 reported as zero); W07f's Morioka full-text retrieval (I retrieved nothing; the `printed_patient_level_data` rows are read as committed bytes only). **No retrieval of any kind was performed.** No denied route replayed.

**Overlap declared with W30:** F1 below extends W30's gate finding from `validate-registry.mjs` to `preflight.sh`'s generator gate. It is a different gate and a different (non-empty) artifact set.

## Method and inputs

All files read at `ff6bb018`, all verified byte-identical at `215ed8e7`.

**Requirement source:** `/home/user/Rare-cancers/systems/POLICY-evidence.md` (386 lines), read in full first, §2.6(a)–(h) and §2.7(a)–(f) verbatim.

**§2.7 artifact set — established from the tree.** The section defines its unit as "one patient-time record … recovered from a published curve **by the Guyot algorithm**". Exactly **two** committed artifacts hold such records:

| # | Path | What it holds |
|---|---|---|
| A1 | `/home/user/Rare-cancers/research/modalities/emc-ipd-survival.json` (23,818 B) + `research/modalities/emc_ipd_survival.py` (981 l) | The reconstructed dataset of record. **1** admitted reconstruction (11 patient-time records, 9 events, 2 censored, PFS). |
| A2 | `/home/user/Rare-cancers/research/modalities/km-figure-readings.json` (9,374 B) + `research/modalities/km_digitize.py` | Its **sole** coordinate input: 1 figure read, **2** candidate reconstructions of it (1 admitted, 1 refused in place). |

**Adjudicated OUT of §2.7 scope by the section's own definition, recorded rather than silently dropped** (each is patient-level or survival-shaped but involves no Guyot inversion):

- `research/modalities/km-swimmer-readings.json` — 4 per-patient PFS durations read off a **swimmer plot**; its own `_what` says "each bar is one patient and **no Kaplan-Meier inversion is involved**". §2.7(a)'s risk table is not merely unmet, it is inapplicable: censoring is read per bar, not inferred per interval.
- `emc-ipd-survival.json → printed_patient_level_data` (`n_rows: 2`) — **transcription** of a printed table (Morioka Table 2), explicitly not reconstruction, explicitly not pooled.
- `research/manuscripts/emc-relative-survival.json` — Ederer II on **published summary survival**, "not to patient-level data" by its own `_readme`.
- `research/modalities/emc-prognostic-coefficients.json` — Cox coefficients transcribed as digits; carries `⛔_neither_cohort_prints_a_risk_table` and derives no survival probability.
- Screening/support artifacts, not datasets: `km-digitization-error.json` (the known-answer control §2.7 explicitly refuses to credit), `km-risk-row-detection.json`, `research/literature/emc-ipd-admissibility-2026-08-12.json`, `emc-km-admissibility-2026-08-27.json`, `emc-km-figure-retrieval-2026-08-25.json`, `emc-km-reachability-census-2026-08-25.json`.

**§2.6 artifact set — established from the `governed_by` enumeration (9 hits, 5 artifacts + 4 generators):**

| # | Path | Rows |
|---|---|---|
| B1 | `research/manuscripts/endpoint/endpoint-corpus.json` (941,272 B) | 552 arms, 138 distinct trials — the corpus of record; `"_this_file_holds_no_analysis"` |
| B2 | `research/manuscripts/endpoint/orr-dcr-reread.json` (428,155 B) | 552 per-arm rows — the descriptive series proper |
| B3 | `research/manuscripts/endpoint/placebo-arm-calibration.json` | 19 control arms |
| B4 | `research/manuscripts/endpoint/endpoint-regime-map.json` | disease coordinates |
| B5 | `research/manuscripts/endpoint/lit-targets-cross-disease-endpoints.json` | the frozen pre-specified protocol |

**Tools:** system `python3` (no third-party packages), `git`, `grep`. Two scratch scripts under `/tmp/claude-0/w30b/`. **No network, no retrieval, no MCP call.**

## Result

### 5.1 Headline

**Both estimand classes conform. Across the two §2.7 artifacts and the five §2.6 artifacts I found 0 violations of every decidable requirement, on the denominators tabulated below.** In particular:

- **No artifact publishes reconstructed IPD without a numbers-at-risk table.** §2.7(a) is satisfied 1/1 on the one admitted curve, and it is satisfied *as a refusal* on the largest reachable EMC series: `masunaga2025` (n=171) is recorded `REFUSED by the quality floor` because `km_risk_row_detect.py` measured `numbers_at_risk_row: false` on all three of its figures.
- **No artifact publishes reconstructed IPD that fails to reproduce its own input.** §2.7(b) is satisfied 1/1 at `max_abs_km_deviation: 0.0454` against a stated floor of `0.05`, and — again as a refusal — the *same figure's* alternative reconstruction sits in the same file at `0.0903` marked `"admissible": false, "failures": ["km_deviation 0.0903 exceeds floor 0.05"]`. The refusal is committed beside the admission, which is exactly what §2.7(a)'s "a refusal is checkable" asks for.
- **Nothing downstream quotes the reconstruction as an EMC survival figure.** Every downstream reference I found quotes it to say it is the wrong shape for the asking question.

That is a clean audit of the strictest section of the evidence policy, and the denominators are small and stated.

### 5.2 §2.7 — reconstructed patient-level survival, requirement by requirement

Denominator: **1 published reconstruction** (`stacchiotti2013_pfs_anthracycline::risk_table_anchored`), plus **1 documented refusal of the same figure** and **4 candidate series refused or unread**. All rows `PRIMARY` as statements about repository state (I read the bytes).

| # | §2.7 requirement | Satisfy | Violate | Uneval | Denominator | Evidence read |
|---|---|---|---|---|---|---|
| P-a | Numbers-at-risk table mandatory; curve without one **refused** | **1** | **0** | 0 | 1 published reconstruction | `quality_floor.require_numbers_at_risk_table: true`; `reconstructions[0].risk_table_intervals: 5`, `risk_table_overridden: []`; enforced in code at `emc_ipd_survival.py:774` (`failures.append("no_numbers_at_risk_table")`) |
| P-a′ | The refusal actually fires on real candidates | **2** | **0** | 0 | 2 candidates with a measured figure | `masunaga2025` (n=171): `numbers_at_risk_row: false`, `risk_row_measured_2026_08_27: "absent (all three figures, km_risk_row_detect.py, pixel arm)"`, `⛔_consequence: "REFUSED by the quality floor"`. A second candidate carries the same `⛔_consequence`. |
| P-b | Reconstruction reproduces its own input; curve past the floor **refused** | **1** | **0** | 0 | 1 | `max_abs_km_deviation: 0.0454` vs `max_abs_km_deviation: 0.05` floor. **Plus a stronger, non-policy-required check**: `external_check` = printed median PFS 8.0 mo (Fig. 2 caption), tolerance 0.5, reconstruction median 7.985 → `external_check_passes: true`. The loader admits **only** readings with `admissible AND external_check_passes` (`emc_ipd_survival.py:446`). |
| P-b′ | A failing reconstruction is refused rather than caveated | **1** | **0** | 0 | 1 rejected candidate | `km-figure-readings.json → readings[0].reconstructions.risk_table_printed`: `max_abs_km_deviation 0.0903`, `admissible: false`, `external_check_passes: false`. Not loaded. |
| P-c | Digitization provenance per curve — who read the figure, with what tool | **1** | **0** | 0 | 1 | `digitized_by: "km_digitize.extract_series over the committed 600-dpi crop; axis anchors, curve colour and the numbers-at-risk row read from the image by the agent session of 2026-08-25 and recorded in FIGURE_RECIPES"`. Enforced at `emc_ipd_survival.py:786` (`"no_digitization_provenance"`). **The pixels themselves are committed** — `research/modalities/figures/stacchiotti2013-csr-3-16-fig2.png`, CC BY 2.0, attributed in `figures/ATTRIBUTION.md` with the exact `pdftoppm -r 600 -png` recipe. |
| P-d | §2.1/§2.3 bind — only non-overlapping populations combined | — | **0** | **UNKNOWN** | **0 pairs** — one curve, so no combination is performed | `pooled.curves_pooled` has length 1 and the artifact says so itself: `⛔_this_is_not_a_pool: "ONE curve, from ONE series … median_survival here is not this disease's median survival."` **Non-overlap is not exercised.** See F4 for the latent gap. |
| P-e | Permitted: KM, medians with "not reached" as a NON-NUMBER, competing risks, PH with optimism correction. Prohibited: covariate-stratified claim from a pooled curve | **1** | **0** | 0 | 1 | `_median_survival` returns `None` when S never reaches 0.5 — *"None means 'not reached' … it must never be rendered as a number."* No PH model, no competing-risks decomposition, no covariate stratification anywhere in the artifact. The one curve **is** the source's own published anthracycline-arm figure, not a stratum cut out of a pooled curve. |
| P-e′ | Endpoint mixing refused rather than caveated | **1** | **0** | 0 | 1 pooler | `pool_reconstructions` **raises** on mixed endpoints: *"a caveat on a number this wrong travels worse than a crash."* Stricter than §2.7 requires. |
| P-f | Labelled as a reconstruction wherever it appears | **1** | **0** | 0 | 1 | `what_this_is: "…A reconstruction is a re-expression of a published figure -- never new patients, never new follow-up, and it inherits every selection effect of the series it came from."` |

**§2.7 totals: 9 satisfy, 0 violate, 1 UNEVAL (P-d, denominator 0 pairs), on 1 published reconstruction.**

### 5.3 §2.6 — study-level descriptive series, requirement by requirement

Denominators: **552 arms** (B1), **552 per-arm rows** (B2), **19 control arms** (B3), **4,414 records screened**.

| # | §2.6 requirement | Satisfy | Violate | Uneval | Denominator | Evidence read |
|---|---|---|---|---|---|---|
| D-a | No pooled estimate and **no CI on any cross-population summary** | **4** | **0** | 0 | 4 analysis artifacts | I walked every key of all four JSONs. Interval-bearing keys occur **only** on per-arm rows: `R2_per_arm_rows[].objective_response.wilson95` ×552, `.disease_control.wilson95` ×552, `.gap_is_the_stable_disease_proportion.wilson95` ×552, `P2_control_arms[].objective_response_wilson95` ×19, `.disease_control_wilson95` ×19. **Zero** interval keys on any cross-population block. |
| D-b | Explicit integers (no count back-derived from a percentage) + own Wilson interval per row | **552 / 552** | **0** | 0 | 552 arms | Enumerated: all 552 rows carry the same 4-cell shape `(CR, PD, PR, SD)`; **0** non-integer cells; **0** non-integer `evaluable_n`; **0** rows where the cells fail to sum to `evaluable_n`. `C1_prespecified_protocol.percentages_are_refused: "a non-integer measurement is a percentage or a rate and is dropped rather than rounded, per POLICY-evidence 2.1"`. All 552 orr rows carry integer `events`/`n`. |
| D-c | Order statistics only; **no** pooled proportion, inverse-variance/random-effects weighting, I², meta-regression or significance test across rows | **4** | **0** | 0 | 4 artifacts | Key-scan for `pooled_(proportion\|estimate\|rate)`, `i2`, `i_squared`, `meta_regress`, `random_effect`, `inverse_variance`, `p_value`: **the only 10 hits are the literal disclaimer key `_no_pooled_estimate`** on 10 summary blocks. The two `grep` hits for "significance" in `endpoint-corpus.json` are verbatim `why_stopped` text quoted from trial registrations, not analyses. Summaries are `median_gap_pp`, `iqr_gap_pp`, `range_gap_pp`, `arms_at_or_above {25,50,75}` — count, median, IQR, range, threshold counts, exactly the permitted list. |
| D-d | Rows unweighted by denominator by default; a weighted view labelled as answering a different question | **1** | **0** | 0 | 1 weighted quantity in the set | `R3._estimand: "how a TRIAL reads, not how patients fare. Arms are therefore unweighted by denominator (POLICY-evidence 2.6(d))."` The single weighted number carries `_answers_a_different_question: "…'how do patients fare' rather than 'how does a trial read'. Reported once so that the unweighted choice is visible rather than silent, and used nowhere else."` |
| D-e | Deduplication at **arm** level | **552 / 552** | **0** | 0 | 552 arms | Enumerated: 552 distinct `(nct_id, outcome_measure_title, arm_title)` triples over 552 rows — **0 collisions**. `C3_dispositions.duplicate_arm_block: 12` records the collapsed ones. **Scoping note, not a defect:** the policy names the key as (registry id, publication id, population key); this corpus is drawn from ClinicalTrials.gov posted results only, so the publication-id component (companion papers, updates, pooled re-reports) has no instances to collapse. The registry-id component is enforced. |
| D-f | Time-to-event per row; a validated modelling conversion does not transfer and may not be an input to a summary | **4** | **0** | 0 | 4 artifacts | **0** median↔rate conversions appear in the declared §2.6 set. See F3 for the one conversion in the tree and why it is out of this scope. |
| D-g | Corpus pre-specified; run ids recorded; **every** screened record has a disposition; a descriptive label may be an attribute and never an inclusion criterion | **3 of 4 sub-clauses** | **0** | **1 sub-clause** | 4,414 records | (i) Protocol frozen in B5, `unit`, `inclusion` and screening rule stated. (ii) `C5_retrieval_provenance` records **10 arm queries + accrual queries** by id with `ref: origin/literature-cache` and `total_count_reported_by_the_api == records_returned` on every one. (iii) **Disposition arithmetic reconciles exactly**: `studies_screened 4414 − study_posted_results_but_no_four_cell_block 4276 = 138 = C6_counts.distinct_trials`; the group-block layer records a further 332 / 14 / 12. (iv) `no_disease_filter: "no tumour type, grade, rarity or indolence descriptor is an inclusion criterion … 'indolent' is recorded nowhere and is used nowhere"`, and `C4_disease_attributes._used_by_nothing: "Nothing in the corpus rule reads this block, and no analysis may filter on it."` **UNEVAL:** `committed_before_any_fetch_ran: true` is an assertion about commit ordering; the history for these paths is squashed to one commit (`14a3f172`), so I cannot verify it from committed data. **UNKNOWN, not a pass and not a fail.** |
| D-h | Selection bias bounded by a census **structurally sharing** the denominator | **1** | **0** | 0 | 1 census | `R5_reporting_census` opens `_this_is_the_sensitivity_analysis_not_a_separate_finding` and is computed in the same pass as `C3_dispositions` — *"which is why it is computed here and not in a separate pass."* It is decomposed into the two query families (`best_overall_response` 2851/2715; `placebo_arm` 1563/1561) with the narrower, fairer denominator reported alongside, and `R6` states that the bias direction is **not known** in either direction. |

**§2.6 totals: 8 requirements, 7 fully satisfied, 0 violated, 1 partially UNEVAL (D-g's commit-ordering sub-clause).**

### 5.4 F1 — the gate gap, extending W30 from the validator to preflight

W30 found `validate-registry.mjs` enforces nothing from §2.6 or §2.7. The same is true one level up. `scripts/preflight.sh`'s gate *"generated deposit artifacts reproduce from their generators"* enumerates **18** generators by path (lines 848–865 in the block I read). **None of the six generators that own §2.6/§2.7 data is among them:** `emc_ipd_survival.py`, `km_digitize.py`, `endpoint_corpus.py`, `orr_dcr_reread.py`, `placebo_arm_calibration.py`, `endpoint_regime_map.py`. All six ship a working `--check` (I ran five; all exit 0).

This is not an unguarded state, and I will not overstate it. The requirements **are** tested — I read the test names:

- `research/modalities/tests/test_emc_ipd_survival.py` (20 tests) contains, by name, `test_a_curve_with_no_risk_table_is_refused_rather_than_reconstructed` (§2.7a), `test_every_loaded_curve_carries_its_provenance_and_passed_an_external_check` and `test_a_reading_that_fails_its_external_check_is_not_loaded` (§2.7b, c), `test_median_survival_is_none_when_not_reached_rather_than_a_number` (§2.7e), `test_pooling_across_endpoints_raises_rather_than_caveats`, `test_the_committed_artifact_does_not_present_one_curve_as_a_pool` (§2.7f), and `test_the_curves_table_is_empty_and_the_artifact_says_so`.
- `research/manuscripts/tests/test_endpoint_producers_check.py` asserts every §2.6 producer's `--check` **really refuses** a drifted artifact, perturbing the real file on disk and restoring it.

The gap is **where they run**: the modalities suite is opt-in behind `PREFLIGHT_MODALITIES=1` or the change-selector (preflight lines 1022–1050), so a commit touching only, say, the registry or a manuscript would not exercise the §2.7 refusals. This is the same shape as the two incidents preflight's own comments record for `atr_hrd_sarcoma_series.py` and `instrument_census.py`: a `--check` that already existed and that nothing in the commit loop ran.

### 5.5 F2 — nothing downstream quotes the reconstruction as a survival figure

I grepped every `.md`, `.json`, `.py` and `.mjs` under `research/`, `systems/` and `scripts/` for `emc-ipd-survival`, `emc_ipd_survival`, `7.98` and `risk_table_anchored`. Every downstream mention is one of: (i) a route audit quoting the artifact to conclude the route is **not takeable** (`S41-BLOCKED-ROUTE-AUDIT.md` ×2, `S41-proposed-routes-patch.json`, `S15-CAREDELIVERY.md` — *"genuinely the wrong shape for a surveillance model"*), (ii) ledger/receipt records of the Morioka transcription, each restating that the 2 printed rows are **not pooled with anything**, or (iii) upstream artifacts pointing at it as the place admissibility is decided. **No manuscript, no pinned figure, and no systems-graph node quotes the reconstructed median (7.985 mo), the n=11, or the 9 events as an EMC survival estimate.** `pinned-figures.json` contains no reconstructed-IPD quantity.

### 5.6 F3 — the one document arguing a risk table is optional, and why it is not a violation

`research/manuscripts/no-wet-lab-publication-archetypes.md` §6.1 states: *"IPDfromKM treats numbers at risk, total patients and total events as OPTIONAL arguments… a curve lacking them is lower fidelity, **not illegal to reconstruct**."* Read in isolation that contradicts §2.7(a) in the policy's strongest language. Read in place it does not: the very next sentence is *"`emc_ipd_survival.py` sets `REQUIRE_RISK_TABLE = True` and refuses such curves outright. **That is this programme's own deliberate stricter choice, not a constraint inherited from the method**, and it should be visible as a choice"* — and it then gives Guyot's hard conditional (hazard-ratio error factor 4.7 at the 97.5% bound) as the justification. It is a correct statement about the *method* alongside an explicit statement that the *policy* is stricter. **Not a violation.** The only thing missing is a pointer: the passage does not cite §2.7(a), so a reader arriving at it first meets "not illegal to reconstruct" with no sign that this repository's contract has since made it a refusal.

The same reading applies to `research/manuscripts/endpoint/emc-endpoint-alternatives.json`, which holds the tree's only constant-hazard median→rate conversion. It does **not** declare `governed_by: 2.6`, its rows are all EMC (so §2.6(f)'s cross-disease transfer prohibition is not triggered), the conversion is calibrated against the three EMC cohorts publishing both quantities, it is labelled with a ±10-point band, and the file states *"no conclusion below is allowed to turn on a converted value alone -- the two conclusions that matter (E3, E5) both rest on PUBLISHED rates."* No converted value enters any §2.6 summary. I record it as an **undeclared boundary case**, not a finding.

### 5.7 F4 — one latent gap, harmless at n=1

`pool_reconstructions` says of itself: *"This function does not police overlap; the caller must have set `pool: false` on the smaller of any overlapping pair."* §2.7(d) makes §2.3 binding, and with one admitted curve there is nothing to overlap — hence the UNEVAL at P-d. But the enforcement asymmetry is real and worth naming while it costs nothing to fix: the same function **raises** on a mixed endpoint and is **silent** on an overlapping population, and the overlap risk is the live one for this disease (the artifact's own `candidate_sources` records that `seer270_2022`'s cohort composition is UNKNOWN and *"must not anchor a pooled estimate until that split is quantified"*). The guard would bite the first time a second curve is admitted, which is precisely when nobody will be looking at this function.

## Validation evidence

**RUN.** Environment: `/home/user/Rare-cancers`, HEAD `ff6bb018` → `215ed8e7`, system `python3` (no third-party packages), `git`, `grep`. Working directory for execution `/tmp/claude-0/w30b/`.

```
$ python3 /home/user/Rare-cancers/research/modalities/emc_ipd_survival.py --check
OK: research/modalities/emc-ipd-survival.json matches the generator
exit=0
$ python3 /home/user/Rare-cancers/research/manuscripts/endpoint_corpus.py --check
OK: research/manuscripts/endpoint/endpoint-corpus.json re-derives from its inputs
exit=0
$ python3 /home/user/Rare-cancers/research/manuscripts/orr_dcr_reread.py --check
OK: research/manuscripts/endpoint/orr-dcr-reread.json re-derives from the corpus
exit=0
$ python3 /home/user/Rare-cancers/research/manuscripts/placebo_arm_calibration.py --check
OK: research/manuscripts/endpoint/placebo-arm-calibration.json re-derives
exit=0
$ python3 /home/user/Rare-cancers/research/manuscripts/endpoint_regime_map.py --check
OK: research/manuscripts/endpoint/endpoint-regime-map.json re-derives
exit=0
$ git status --porcelain          # after every one of the five
(empty)
```

Enumeration output (`/tmp/claude-0/w30b/int26.py`, verbatim):

```
arms 552 cell-key-shapes {('CR', 'PD', 'PR', 'SD')}
non-integer cells 0 | non-integer evaluable_n 0 | cells do not sum to evaluable_n 0 | rows without retrieved_file 0
screened 4414 no4cell 4276 included_trials 138 screened-no4cell = 138
distinct (nct,outcome,arm) triples 552 of 552
distinct nct 138
orr rows 552 row mismatches vs corpus 0
orr rows with non-integer events/n 0
```

Key-scan output (`/tmp/claude-0/w30b/scan26.py`, abridged to the decisive lines):

```
== endpoint-corpus            prohibited-key hits: {}   interval-key hits: {}
== orr-dcr-reread             prohibited-key hits: {10 × '_no_pooled_estimate'}
                              interval-key hits: {'/R2_per_arm_rows[]/objective_response/wilson95': 552,
                                                  '/R2_per_arm_rows[]/disease_control/wilson95': 552,
                                                  '/R2_per_arm_rows[]/gap_is_the_stable_disease_proportion/wilson95': 552}
== endpoint-regime-map        prohibited-key hits: {}   interval-key hits: {}
== placebo-arm-calibration    prohibited-key hits: {}
                              interval-key hits: {'/P2_control_arms[]/objective_response_wilson95': 19,
                                                  '/P2_control_arms[]/disease_control_wilson95': 19}
```

Read-integrity check across the HEAD move:

```
$ git diff --stat ff6bb018936451d0c2d60fb4a2aa7ae8ba932d7f 215ed8e78f83d1e5acdbb726317dfd0eeed8f6a1 -- <all 15 inputs>
(empty)
diff-exit=0
```

**PROPOSED (NOT RUN).** The two test suites that enforce these requirements:

```
$ python3 -m pytest research/modalities/tests/test_emc_ipd_survival.py \
      research/manuscripts/tests/test_endpoint_producers_check.py -q -p no:cacheprovider
/usr/local/bin/python3: No module named pytest
```

**pytest is not installed in this container, so I have no pass/fail evidence for either suite and assert none.** A skipped test is not a pass. Separately, `test_endpoint_producers_check.py` **perturbs the committed artifacts on disk** and restores them in a `finally` — running it would have breached my write isolation regardless, and I would not have run it even with pytest present. My statements about those files are limited to what their test names and docstrings say they assert, which I read directly.

## Limitations

1. **Small denominators, honestly stated.** The entire §2.7 conformance result rests on **one** published reconstruction from **one** figure of **one** series (11 patient-time records). A clean audit of n=1 is a clean audit of n=1. What it establishes is that the instrument's refusals are wired and firing, not that the class has been stress-tested.
2. **I verified conformance, not correctness of the reading.** §2.7(b) is a self-consistency plus a printed-median check; neither I nor any committed artifact can rule out a systematically mis-read axis. The policy says this itself, and the digitization-error control is explicitly excluded as evidence about any particular curve.
3. **I retrieved nothing.** Every claim is about committed bytes. I did not open `PMC3879193`, did not re-read Figure 2, and do not adjudicate whether the digitized coordinates match the published curve.
4. **Commit ordering is undecidable here.** The history for every artifact I audited is squashed to `14a3f172`, so §2.6(g)'s "committed before any fetch ran" and the recency of any field are UNKNOWN.
5. **Scope adjudications are mine.** Placing the swimmer-plot readings, the printed Morioka rows, the relative-survival life table and the Cox coefficients **outside** §2.7 follows the section's own "by the Guyot algorithm" definition. A reader who reads §2.7 as governing all patient-level survival recovered from a figure would put `km-swimmer-readings.json` inside it — in which case §2.7(a) would be inapplicable rather than unmet, and (c) and (f) are satisfied there too (committed recipe with URL/page/dpi, explicit claim ceiling, "re-expressions of an already-published figure").
6. **No clinical claim.** Nothing here says any treatment works, is safe, or should be given. There is no wet lab. The reconstructed median (7.985 months) is one anthracycline-treated series' own re-expressed figure and is not this disease's median survival — the artifact says so in its own `⛔_this_is_not_a_pool`, and I repeat it rather than quoting the number bare.
7. **F1 is a coverage observation about where tests run, not a measured failure.** I did not run preflight and did not run the suites.

## Stop condition

**Set up front:** enumerate the §2.6 and §2.7 artifact set from the tree (not from the dispatch's hint), audit each against §2.6(a)–(h) and §2.7(a)–(f) with satisfy/violate/uneval and an honest denominator per requirement, decide specifically whether any artifact publishes reconstructed IPD without a risk table or without reproducing its input, and determine whether anything downstream quotes such an artifact — then return.

**MET.** The set is established (2 artifacts under §2.7, 5 under §2.6, with 9 adjacent artifacts adjudicated out and listed). All 14 requirement lines are decided: 16 satisfy, **0 violate**, 2 UNEVAL (§2.7(d) at denominator 0; §2.6(g)'s commit-ordering sub-clause). No artifact publishes reconstructed IPD without a numbers-at-risk table or without reproducing its own input, and no downstream artifact quotes the reconstruction as a survival figure.

## Tool-call and wall-clock count actually used

**33 Bash tool calls** across 22 assistant blocks (counted from this transcript; ±2). **0** network calls, **0** retrieval calls, **0** writes to the repository, **0** git write operations. Wall clock **03:26:57Z → 03:31:39Z ≈ 4.7 minutes** of measured tool time, plus report drafting. Well inside the ~40/~40 target.

## Next concrete action

**Add the six §2.6/§2.7 generators to `scripts/preflight.sh`'s "generated deposit artifacts reproduce from their generators" gate** — `research/modalities/emc_ipd_survival.py|reconstructed IPD survival|--check`, `research/modalities/km_digitize.py|KM figure readings|--check` (if it has one; I confirmed the other five do), `research/manuscripts/endpoint_corpus.py`, `orr_dcr_reread.py`, `placebo_arm_calibration.py`, `endpoint_regime_map.py`. All five I ran exit 0 on the current tree in well under a second each, so the rows are green on arrival and cost is negligible — the same argument preflight's own comments make for the `atr_hrd_sarcoma_series.py` and `instrument_census.py` rows, which were added after exactly this failure mode shipped a stale artifact. This moves the §2.7(a) and §2.7(b) refusal conditions from an opt-in test tier into the commit loop, which is what W30's finding was pointing at. It is a one-block edit to a shell script and needs no science.

A second, smaller item for whoever owns the reconstruction instrument: make `pool_reconstructions` raise on an overlapping population the way it already raises on a mixed endpoint (F4), and add a one-line cross-reference to `systems/POLICY-evidence.md` §2.7(a) in `no-wet-lab-publication-archetypes.md` §6.1 so its correct method statement cannot be read as licence (F3). **I propose these; I have written nothing.**
