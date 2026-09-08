<!-- collected 2026-09-08T07:35:48Z by campaign coordinator; agent id a07b78237ee438258; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a07b78237ee438258.jsonl;
     OBSERVED child model set: ['claude-opus-5']; single longest assistant turn;
     worker was read-only (no repository writes) -->

Report follows.

## Worker

C1, paper lane, OPUS-CAPACITY-CAMPAIGN-20260908. Model identity is a **SELF-REPORT, NOT INDEPENDENTLY VERIFIED**: I am told I am `claude-opus-5`; I did not observe the served model. No environment variable names a model — literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start and end is in the transcript above (identical both times apart from proxy lists; key lines: `AI_AGENT=claude-code_2-1-263_agent`, `CLAUDE_CODE_VERSION=2.1.42`, `CLAUDE_EFFORT=medium`, `ANTHROPIC_BASE_URL=https://api.anthropic.com`, `CLAUDE_SESSION_INGRESS_TOKEN=<redacted>`, `CLAUDE_CODE_MESSAGING_TOKEN=<redacted>`). **No environment variable contains a model ID**, so the environment supports no model claim at all.

| | start | end |
|---|---|---|
| `date -u` | Tue Sep  8 07:30:01 UTC 2026 | Tue Sep  8 07:33:00 UTC 2026 |
| `git rev-parse HEAD` | `d7988bcf4bd277dbe168f146c946a048175cf13e` | `c27c0870b68755b4136e0faff3aff6e9eae8cf43` |
| `git status --porcelain` | empty | empty |
| `df -h /` | 252G / 18G used / **20G avail** / 47% | identical |

HEAD advanced under me (coordinator commits). Measured: `git diff --name-only d7988bcf c27c0870 | grep -v opus-capacity-campaign-20260908 | wc -l` = **0**, and all five input files re-hash identically at the end HEAD, so nothing I read moved.

## Question

Does the compartment-B upper band in `research/manuscripts/emc-host-factor-model.json` survive changing its competing-share input from the value it currently uses (0.394) to the value the paper adopted, and by how much does each output move?

## Step 1: provenance of the source estimator

**(a) `direct_cause_split` stores no single "21.7 %" value — it stores two strata, and the pooled figure is the paper's, not the artifact's.** In `/home/user/Rare-cancers/research/manuscripts/emc-mortality-decomposition.json`:

| row | n | disease_deaths | other_cause_deaths | total_deaths | stored `competing_share_of_deaths_pct` |
|---|---:|---:|---:|---:|---:|
| `masunaga2025_localized` | 134 | 9 | 4 | 13 | **30.8** |
| `masunaga2025_metastatic` | 29 | 9 | 1 | 10 | **10.0** |
| pooled (computed from stored counts) | 163 | 18 | 5 | 23 | **5/23 = 0.21739130434782608** |

I used the **stored numerators and denominators** (5 and 23), never the rounded display. Result of the disagreement check the contract required: the stored counts give **21.7391 %**; the paper's Table 2 and Appendix A.1 display **21.7 %**. These **agree to rounding — no contradiction**. The real finding is a different one: **the decomposition artifact contains no combined/pooled `direct_cause_split` row at all.** The `163 / 18 / 5 / 21.7 %` line exists only in `research/manuscripts/emc-mortality-mechanisms-paper.md` (line 241); it is a paper-side pooling of two stored strata, and it is **not** a value the model or any other consumer can read from the JSON.

**(b) No committed record shows the within-series estimator was chosen deliberately — the record shows the opposite.**
- `research/manuscripts/emc_host_factor_model.py:244-245` selects it unconditionally: `within = (decomp.get("within_series") or [{}])[0]` then `competing_share = within["competing_share_of_deaths_pct"]/100.0`. There is no branch, no config, no comment, no superseded-and-retained marker.
- The only rationale text is the generator's own emitted string, *"within-series (Meis-Kindblom 1999) — the only pairing measured on the same patients."* `rg "only pairing measured on the same patients"` returns exactly two files: the generator and its own output. It is **self-referential**, and it is **contradicted by the same JSON it reads**: each `direct_cause_split` row carries `estimator = "Direct ratio of two death counts on the same patients."`
- `direct_cause_split` was **already present** in the decomposition at the commit where the model was generated (`git show abc73e0e:…emc-mortality-decomposition.json | grep -c direct_cause_split` → 1; commit `abc73e0e`, 2026-09-04, "RT-HOST-FACTOR: enter the retrieved effect sizes and run the two-compartment model (AUT-220)"). So the better pairing was available and was not taken.
- Paper Appendix A.1 (line 391): *"Competing share, 39.4 per cent superseded by 21.7 per cent"* — an explicit supersession.
- `research/autonomy/research-ledger.json` records the same supersession being applied elsewhere: *"the rationale's superseded 39.4% competing-share figure corrected to the paper's own 21.7%/23.0% (Appendix A.1)"* in `systems/graph/routes.json`, and separately *"THE BRANCH'S OWN SUPERSEDED HEADLINE WAS NOT IMPORTED: IDEAS.md still carried 39.4 % after `4d61197b3` corrected the competing share to 21.7 %"*.
- The 0.394 occurrences in `research/manuscripts/tests/test_emc_host_factor_model.py` are a **fixture value passed into `model_factor`**, not a pinned source choice.

## Decision to proceed or stop, with evidence

**Proceed.** Stop condition (ii) — a committed record showing deliberate choice — **did not fire**: the search found supersession language for 39.4 % in the paper and the ledger, a self-referential and factually wrong rationale string in the generator, and no deliberate-retention marker anywhere. The model input is stale, not chosen.

## Method and what was held fixed

All execution in `/tmp/claude-0/c1-scratch/repo` (a `cp -a` of five files), **nothing written to the checkout**, no git operation, no network, no paid API, no GPU, no `scripts/preflight.sh`, `atr_hrd_sarcoma_series.py` never invoked.

1. **Baseline reproduction attempt** — ran the committed generator unmodified. It **refused**, verbatim (exit code **1**):
```
UNANCHORED EVIDENCE -- refusing to model:
  - HF-SMOKING: PMID 42340948 is in no retrieved artifact. Either the search did not return it, or it was written from recollection.
  - HF-CV-RISK: PMID 42068528 is in no retrieved artifact. Either the search did not return it, or it was written from recollection.
  - HF-SARCOPENIA: PMID 41055780 is in no retrieved artifact. Either the search did not return it, or it was written from recollection.
```
This is a **measured negative, reported not routed around**: I did not weaken `check_anchors`. Consequence: **the committed `emc-host-factor-model.json` cannot be regenerated from the committed inputs at this HEAD.** Note also that `emc-host-factor-inputs.json` now names PMID **42340948** for HF-SMOKING while the committed model output carries **41300991** — the inputs have drifted since the output was written. That drift is a second, independent defect and is **out of my scope to repair**.

2. **Consequence check** — because the generator refuses, I applied the generator's own arithmetic, quoted verbatim from `model_factor` (lines ~198-217), to the committed model's own stored values, changing **only** the share:
   - `share_of_all_deaths` = `share` (B) / `1.0 - share` (A)
   - `exposed_patient_share_of_deaths_averted_range` = `[round(share·rrr_lo·t_lo,4), round(share·rrr_hi·t_hi,4)]`
   - `cohort_share_of_deaths_averted_range` = `[round(prev·share·rrr_lo·t_lo,4), round(prev·share·rrr_hi·t_hi,4)]`
   
   **Held fixed:** every prevalence, every relative-risk-reduction range, every transfer multiplier `[0.6, 1.0]`, every status, every PMID, the decomposition itself, and the compartment structure. No re-derivation of the decomposition, no re-retrieval of effect sizes, no added factor, **one variant only** — no sweep. The `factors_not_entered` rows (type-2 diabetes/metformin, hypertension, exercise-as-intervention) require network retrieval outside worker authority and **stay excluded and unfetched — out of reach, not zero**.
   
   The script **asserts** that the committed file reproduces under its own formula at share = 0.394 before computing the variant; all assertions passed (exit 0).

Share: **0.39399999999999996 → 0.21739130434782608**. Ratio new/current **0.551755**; current/new **1.812400**.

## Recomputed outputs beside current values

Every number is a **model output** under a changed input — not a measurement, not a treatment effect.

| factor | comp | status | quantity | current | recomputed | ratio |
|---|---|---|---|---|---|---|
| — | B | — | competing share | 0.3940 | **0.2174** | 0.5518 |
| — | A | — | share of all deaths | 0.6060 | **0.7826** | 1.2914 |
| HF-OBESITY | B | MODELLED | exposed patient share averted | [0.0118, 0.0827] | **[0.0065, 0.0457]** | 0.5525 / 0.5526 |
| HF-OBESITY | B | MODELLED | cohort share averted | [0.0048, 0.0333] | **[0.0026, 0.0184]** | 0.5417 / 0.5526 |
| HF-SMOKING | B | MODELLED | exposed patient share averted | [0.0449, 0.1261] | **[0.0248, 0.0696]** | 0.5523 / 0.5519 |
| HF-SMOKING | B | MODELLED | cohort share averted | [0.0050, 0.0141] | **[0.0028, 0.0078]** | 0.5600 / 0.5532 |
| HF-CV-RISK | B | MODELLED | exposed patient share averted | [0.0118, 0.1143] | **[0.0065, 0.0630]** | 0.5525 / 0.5512 |
| HF-CV-RISK | B | MODELLED | cohort share averted | [0.0055, 0.0535] | **[0.0031, 0.0295]** | 0.5636 / 0.5514 |
| HF-SARCOPENIA | B | ASSOCIATION_ONLY | both ranges | [0.0, 0.0] | **[0.0, 0.0]** | unchanged |
| all four | A | NO_EVIDENCE / ASSOCIATION_ONLY | both ranges | [0.0, 0.0] | **[0.0, 0.0]** | unchanged |

Ratios deviate from 0.5518 only by fourth-decimal rounding in the generator's `round(...,4)`.

## Does each stated conclusion change, and why

1. **"Compartment B is ~40 % of deaths, compartment A ~60 %" (module docstring lines 14-19, and `_readme`).** **CHANGES.** Under the adopted estimator it is **~22 % / ~78 %**. The prose figures are the direct restatement of the changed input.
2. **`competing_share_source`: "within-series (Meis-Kindblom 1999) — the only pairing measured on the same patients."** **CHANGES, and it is false as written today.** `direct_cause_split`'s own `estimator` field says its rows are a direct ratio of two death counts **on the same patients**; the Meis-Kindblom pairing additionally carries a stored `estimator_mismatch` (survival-curve reading vs crude proportion) that the direct ratio does not have.
3. **`the_honest_ceiling` — "a host-factor intervention can only ever touch the share of deaths that are not EMC deaths."** **Survives qualitatively, shrinks quantitatively by 1.81×.** The structural statement is independent of the share's value; the ceiling it bounds is 0.55× what the file currently implies.
4. **The whole-model qualitative conclusion — every compartment-A entry is zero, no efficacy is claimed, an association is never an intervention effect.** **DOES NOT CHANGE.** Compartment A is pinned to `relative_risk_reduction_range = [0.0, 0.0]` regardless of its share; 0.0 × anything is 0.0. Raising A's share from 0.606 to 0.7826 moves **no** A output.
5. **`why_two_compartments` (never report one blended number).** **DOES NOT CHANGE** — a structural argument, not a numeric one.
6. **HF-CV-RISK's `endpoint_caveat` ("read the modelled band as an upper-bound shape, not an estimate").** **DOES NOT CHANGE, and now applies to a smaller band.**
7. **The `limits` block** (prevalences imported, share-averted is not life expectancy, model cannot detect its own biases). **DOES NOT CHANGE.**

**Direct answer to the question:** the upper band **survives in the sense that it stays non-zero, keeps its sign and keeps every qualitative statement attached to it — it does not collapse.** It **does not survive as a number**: every modelled compartment-B band contracts by a factor of **1.8124** (largest single figure: HF-CV-RISK exposed-patient upper bound 0.1143 → **0.0630**).

## Durable artifacts written and verified

`/tmp/claude-0/c1-retained/` — created outside the checkout, **not deleted**, parent alone collects. `sha256sum -c SHA256SUMS.txt` printed **OK for all 8 files** (verification run and printed before any cleanup; **no scratch was deleted**, `/tmp/claude-0/c1-scratch/` also remains).

```
7581bee8654a741beedece7bf4a69cb670019601cd2519092b25eab2638e759e  INPUT-HASHES.txt
6f337696ccb5f904b6bdec95cf7e5bfb8eb7a164eb6017a3e9bbdca68ded1267  baseline-rerun-emc-host-factor-model.json
6f337696ccb5f904b6bdec95cf7e5bfb8eb7a164eb6017a3e9bbdca68ded1267  committed-emc-host-factor-model.json
47aac7b8f9a3138820ad80f7b6c9448797e085629a9d5ca117cadd1d45e97ed9  generator-baseline-stderr.txt
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  generator-baseline-stdout.txt   (0 bytes — the run refused, stdout is legitimately empty)
f265d0095bfa28c6379b78b6dfbab6e402032da538e6957cf41df226dbc15eaa  recompute-stdout.txt
c9831fa6d7e722e0dd6011eb1e2c7b44007243bb48b00708ae68ce9b1933083d  recompute_competing_share.py
1b0f913d43e2ab52a539e8530a14c76b28c9e41c2355461275feae5c07e73ea0  recomputed-output.json
```

Input hashes with source paths (`INPUT-HASHES.txt`, re-verified identical against the live tree at the end HEAD):
```
25a5095a9e965193cddbcce56d9d8bf55d856e185258f49795b3e94328b77bc5  research/manuscripts/emc-host-factor-inputs.json
6f337696ccb5f904b6bdec95cf7e5bfb8eb7a164eb6017a3e9bbdca68ded1267  research/manuscripts/emc-host-factor-model.json
fe47c13b575c0dc0ebf1f0013c28cbc86045eff2673b87f86d5a18443107df6b  research/manuscripts/emc-mortality-decomposition.json
3d66e026eaac3a4f65a1204c64b3b356ae88f54c93b6b36254b7b54bec57baa5  research/manuscripts/emc_host_factor_model.py
dff1c49c7459eb323355e3a55967d6fd4d93b61279aa8554c29229ce0c45fea1  research/literature/emc-host-factor-probe.json
```
No missing bytes; nothing reconstructed. Disk 20 GiB free throughout (≥10 GiB floor honoured).

## What this does and does not support

The quantity is a **cohort death fraction** — the share of deaths in a retrospective series attributed to causes other than the tumour. It is **not population mortality risk, not a causal treatment effect, and not a bound on any antitumour argument.** This recomputation is arithmetic over a committed model's inputs. It **establishes no clinical benefit** — no efficacy, no safety, no selectivity, no therapeutic window, no clinical readiness, in EMC or anywhere. The corrected band is a **model output, not a treatment effect and not a patient-facing quantity**. There is no wet lab. Nothing here is advice for any individual, and no one should act on any figure in this report.

## Validation evidence

**RUN.** `python3` (system interpreter), cwd `/tmp/claude-0/c1-scratch/repo`.
- `python3 research/manuscripts/emc_host_factor_model.py` → **exit 1**, stderr quoted verbatim above (three unanchored PMIDs), stdout empty, output file untouched (`diff -q` against the committed copy: identical).
- `python3 /tmp/claude-0/c1-retained/recompute_competing_share.py …` → **exit 0**. Self-consistency assertions that the committed model reproduces under its own formula at share 0.394: **all passed** for 8 factor-compartments.
- `sha256sum -c SHA256SUMS.txt` → **8/8 OK**.
- Provenance searches actually run: `grep -n -i -E "competing|within_series|direct_cause|0\.394|…" emc_host_factor_model.py`; `rg -n -i "only pairing measured on the same patients" -l` (2 hits, both self-referential); `git show abc73e0e:research/manuscripts/emc-mortality-decomposition.json | grep -c direct_cause_split` → **1**; `grep -n -o -E ".{300}(39\.4|within-series).{400}" research/autonomy/research-ledger.json`.

**PROPOSED (NOT RUN):** re-running the generator end-to-end under the corrected share — **impossible at this HEAD**, blocked by the anchor refusal above. `scripts/preflight.sh`, `research/manuscripts/tests/test_emc_host_factor_model.py`, and every repository write **NOT RUN by prohibition**.

## Limitations

- The recomputed bands inherit **every** limitation of the current model unchanged: all four prevalences are imported from US general-population sources because no EMC series records a host factor (`BLK-NO-EMC-DATA`); a share of deaths averted is **not** a gain in life expectancy; the model cannot detect the biases in its own inputs.
- The adopted 5/23 estimator rests on **5 other-cause deaths** and a median follow-up of ~3.2 years. The decomposition's own text records that short follow-up **flatters** the competing share, and that censoring other-cause deaths makes the competing share an **under**-estimate — two biases running in opposite directions, neither corrected here.
- Pooling the two strata is the **paper's** operation, not the artifact's; the strata differ sharply (30.8 % vs 10.0 %) and a pooled share conceals that stage dependence.
- The generator's refusal means the committed model output is **not currently reproducible**; my figures reproduce its arithmetic, not its full generation path.
- `factors_not_entered` (diabetes/metformin, hypertension, exercise-as-intervention) are **out of reach without network retrieval outside worker authority** — unknown, not zero.
- I made **no** repository change. Every correction implied here — the generator's estimator selection, its false `competing_share_source` sentence, the missing pooled `direct_cause_split` row, and the HF-SMOKING PMID drift — is an **owner act**.

## Stop condition

Set: acceptance on recomputed figures with ratios and a per-conclusion survives/does-not statement, **or** a documented deliberate-estimator finding; else ~40 tool calls / ~40 minutes. **Met by acceptance** (Step 2 completed). Stop (ii) checked and did **not** fire. Stop (iii) did not fire — the recomputation needed no input the model excludes. No content-policy refusal occurred. One tool refusal did occur and is reported, not routed around: the generator's own anchor check, exit 1.

## Tool-call and wall-clock count actually used

**16 tool calls** (2 of them parallel-batched), **3 minutes** wall clock (07:30:01 → 07:33:00 UTC), both well inside the ~40/~40 budget.
