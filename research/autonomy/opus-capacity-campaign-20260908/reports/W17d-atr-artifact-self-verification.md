> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

All four scripts ran under `/tmp/claude-0/w17d/`, exit 0; write isolation confirmed clean. Report follows.

---

## Worker

**W17d**, lane 17 (second refill) — successor to W17b, exact point-verification of the ATR artifact's part-B concept slots.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). I did not observe the served model. **No environment variable names a model** — the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:21:03 UTC 2026` (first captured); at end: `Tue Sep  8 02:21:14 UTC 2026`. (Tool work began ~02:14Z; the two `date -u` captures are the literal outputs of the two calls that ran the command.)

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — model-relevant lines, verbatim (full output in the transcript):

```
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_VERSION=2.1.42
CLAUDECODE=1
CLAUDE_EFFORT=medium
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_CHILD_SESSION=1
```

Repository HEAD at read time: **`b9a0257e6acff53ad22535cf2adf261313e0b250`** (W17 read `92abbcb9…`, W17b read `103ff76f…`; the coordinator has committed further collected reports since). `git status --porcelain` shows only `?? …/reports/W01c-emc-deposit-literature-inventory.md` and `?? …/reports/W13b-pooled-cohort-unit-resolution.md`, both **other workers'** collected files. **I created and modified no file under `/home/user/Rare-cancers` and ran no git write operation.** All execution was under `/tmp/claude-0/w17d/`.

---

## Question

**Can `research/modalities/emc-atr-vulnerability.json`'s part-B concept slots be verified at the same point level as W17b verified `emc-expression-panels.json` — or does that artifact fail to persist enough to verify itself?**

Open because W17b reached only 72 of 306 slots and left 234 UNKNOWN, on the stated ground that the ATR artifact carries `scores` / `proliferation_adjusted_scores` arrays but no per-concept `per_sample` rows in the shape the inversion needs. W17b named the successor precisely: determine whether those arrays can be regrouped by class into per-sample vectors, and if not, establish that the artifact cannot self-verify.

**Answer, up front: it CAN self-verify. W17b's conjecture is overturned by execution.** The score arrays are positionally aligned with `sample_annotations_verbatim`, the comparator arms are recoverable uniquely, and all 90 slots that carry a statistic at all pass every gate with zero violations. **No generator repair is needed, so nothing is routed as a proposal** (item 4 of my dispatch does not fire).

---

## Prior-work check

- I read `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `reports/W17-heldout-validation.md` (targeted) and `reports/W17b-exact-welch-variance-inversion.md` **in full** before writing any code.
- `find . -name '*W17*'` → exactly two lane-17 reports (`W17-heldout-validation.md`, `W17b-exact-welch-variance-inversion.md`). No third.
- W17b's own tree-wide novelty sweep (`rg -n -i "implied variance|variance inversion|recover.*variance|v_a|welch system"`, plus the evidence-4878 capsule) covers the inversion machinery I reuse; I did not repeat it, and I reuse rather than re-derive W17b's derivation, tolerance propagation and root-agnostic forward gate as my dispatch instructs. **The regrouping question itself is new** — no artifact or script in the tree groups the ATR score arrays.
- **Closed items confirmed not replayed:** no ASO/NAT submission, no Qeios history, no tissue-RNA paper, no frozen comment `7baf2727…`, **no review round opened on PUB-ATR**, no frozen deliverable touched, no `GSE4303`/`GSE28866` rediscovery as new data (I read only already-committed derived fields), no invented cohort, no external retrieval, no denied-route replay. **W17c is separately on the PUB-ATR MDE range (`p1s[0]`); I did not touch it** — the MDE range is untouched by this work.

---

## Method / inputs

**Input, read-only:** `research/modalities/emc-atr-vulnerability.json` (342,797 bytes, mtime 2026-09-04 12:16), part B. **Tools:** `python3` → `Python 3.11.15`, stdlib `json`/`math`/`itertools`/`random` only. No network, no installs, no paid API, no GPU. cwd `/tmp/claude-0/w17d`.

### 1. What the artifact actually persists — read, not assumed

Each `part_b_emc_tumour_signature.per_platform[<matrix file>]` block carries these 17 keys:

```
_status, series, platform, value_kind, n_samples, n_probes_mapped_to_symbols,
probe_mapping_diagnostic, class_counts, sample_annotations_verbatim,
n_geneset_genes_matched, scores, proliferation_adjusted_scores,
contrast_EMC_vs_all_comparator_sarcoma,
contrast_EMC_vs_all_comparator_sarcoma_PROLIFERATION_ADJUSTED,
contrast_EMC_vs_FET_comparators, contrast_EMC_vs_NONFET_comparators, _sign
```

The three fields that matter, quoted from `GSE4303-GPL3290_series_matrix.txt.gz`:

- `n_samples: 16`
- `sample_annotations_verbatim`: a **list of 16 dicts**, each `{'gsm': …, 'class': …, 'annotation': …}` — e.g. `{'gsm': 'GSM89883', 'class': 'DFSP', …}`, `{'gsm': 'GSM98495', 'class': 'EMC', …}`.
- `scores[concept]`: a **bare list of 16 floats**, printed to 4 dp — e.g. `scores['ATR_CHK1_activity'] = [-0.678, -0.5805, -0.6841, -0.9074, -0.8682, -0.6872, -0.679, -0.4257, -0.5568, -0.5409, -0.6487, -0.3416, -0.5152, -0.5977, -0.2081, -0.3775]`.
- `proliferation_adjusted_scores[concept]`: likewise, 16 floats, 4 dp.

**W17b's factual description is correct** — there is no `per_sample` object, and the score lists carry **no labels of their own**. This is exactly the hazard my dispatch named: an ordered array whose class labels live in a separate structure. `class_counts` alone (`{"DFSP": 3, "EMC": 10, "GIST": 3}`) is a multiset and cannot order anything; the orderable information is `sample_annotations_verbatim`.

Verified across all 11 platforms: `len(scores[c]) == len(proliferation_adjusted_scores[c]) == len(sample_annotations_verbatim) == n_samples == sum(class_counts.values())` **for every platform and every concept**, with no exception. Four platforms (`GSE28866`, `GSE43632`, `GSE80126`) carry `scores: {}` — no probes mapped — and consequently carry no statistic either.

### 2. The join is tested, not assumed

The hypothesis under test: `scores[c][i]` is the score of the sample described by `sample_annotations_verbatim[i]`. **I did not join on this assumption.** Stage 1 of `atr_point_verify.py` does an exhaustive recovery:

> For each platform × contrast family, search **all 2^k−1 non-empty subsets** of the non-EMC classes present. A subset is ADMITTED only if, under the positional join, it reproduces the committed `mean_b` of **every concept in that family simultaneously** to `|mean_obs − mean_c| ≤ 2·δz`. `mean_a` is likewise required to match for every concept under group `EMC`. Zero admitted subsets ⇒ the slot is UNKNOWN (join unestablished); more than one ⇒ AMBIGUOUS, reported, not silently picked.

Requiring 6–12 concepts to match at once against a 4-dp target makes coincidental admission implausible, and uniqueness is checked rather than hoped for.

### 3. The point gate — W17b's, unchanged

Reused verbatim in structure from W17b's report: with `v_a=s_a²/n_a`, `v_b=s_b²/n_b`, `S=v_a+v_b`, `A=n_a−1`, `B=n_b−1`,

- **T1 (scale):** `t = Δ/√S ⇒ S = (Δ/t)²`
- **T2 (shape):** `df = S²/(v_a²/A + v_b²/B)`; with `f=v_a/S` this is the scale-free quadratic `f²/A + (1−f)²/B = 1/df`, discriminant `D = (1/A+1/B)/df − 1/(AB) ≥ 0 ⟺ df ≤ A+B`. **Both roots lie in [0,1] iff df ≥ max(A,B)** — the branch ambiguity is real, and as in W17b it is **not silently resolved**: the gate is the algebraically equivalent **root-agnostic forward form**, and the inversion is reported separately.
- **T3 (means):** `|mean_obs − mean_c| ≤ 2·δz`.
- **T0 (identity, added here):** `|(mean_a − mean_b) − delta_a_minus_b| ≤ 3·δz`.

### 4. Tolerance — stated before running, propagated from the artifact's own print precision

`scores` / `proliferation_adjusted_scores` / `mean_a` / `mean_b` / `delta_a_minus_b` at **4 dp** ⇒ `δz = 5e-5`; `t` at **3 dp** ⇒ `δt = 5e-4`; `df` at **1 dp** ⇒ `δdf = 0.05`. Rigorous worst case on the sample variance, `d(s²) ≤ (2·δz·Σ|z_i−z̄| + n·δz²)/(n−1)`, `δv = d(s²)/n`. T1 passes iff `[S_obs ± δS]` intersects `[((|Δ|−δz)/(|t|+δt))², ((|Δ|+δz)/(|t|−δt))²]`; T2 passes iff the range of `df` over the four corners of `[v_a±δv_a]×[v_b±δv_b]` intersects `[df_c ± 0.05]`. **Declared in advance:** T1 is *not evaluable* where `|t| ≤ 10·δt = 0.005` (the implied scale diverges) — such slots are **UNKNOWN, not passed**. Sample variance is **ddof=1** (pre-stated); ddof=0 computed only as a diagnostic on a failure. **No criterion was changed after seeing any result**, and none was weakened.

---

## Result

| # | Finding | n | Uncertainty | Tier |
|---|---|---|---|---|
| **A0** | **The artifact enumerates 408 concept slots**, of which **306 are non-null** (matching W17/W17b's "306") and **90 carry both `t` and `df`**. The other **216 carry only a `_status` string** (`"underpowered: n_a=0, n_b=0"` ×92, `n_a=0,n_b=2` ×56, `n_a=0,n_b=4` ×28, `n_a=0,n_b=3` ×28, `n_a=10,n_b=0` ×12) — **no statistic exists in them to verify.** | 408 / 306 / 90 / 216 | exact counts | PRIMARY |
| **A1** | **The positional join is establishable, not assumed.** `len(scores[c]) == len(sample_annotations_verbatim) == n_samples == sum(class_counts)` for every platform and concept, with zero exceptions. | 11 platforms × 12 concepts | exact | PRIMARY |
| **A2** | **Comparator-arm recovery is UNIQUE for all 10 contrast families.** Exactly one class subset is admitted in each; **0 families with no admissible subset, 0 ambiguous.** Max `|mean_a` error`|` ≤ 5.00e-05 and max `|mean_b` error`|` ≤ 5.00e-05 everywhere — i.e. at the 4-dp half-ulp, not merely inside a loose band. | 10 families | ≤ 2·δz = 1e-4 | PRIMARY |
| **A3** | **The recovered arms are corroborated by an independent artifact field.** Pooled recovery returns `['DFSP','GIST','MFH_UPS']`, which equals the committed `cross_platform_pooled.comparator_classes_used` **exactly** — a field the recovery never read. GSE24369 recovery returns FET=`['LGFMS']` (n_b=17) and NONFET=`['desmoid_fibromatosis','fibrosarcoma']` (n_b=12), a partition consistent with LGFMS being the one FET-fusion entity among them. | 2 independent checks | exact set equality | PRIMARY |
| **A4** | **Pooling is validated, not assumed.** Concatenating the 7 GSE4303 platforms reproduces `class_counts` **element-wise exactly** (`{DFSP:8, EMC:10, GIST:5, MFH_UPS:4, unclassified:9}`) and `n_samples_pooled = 36 = 36`. | 36 samples | exact | PRIMARY |
| **A5** | **T0 (delta identity): 0 violations / 90.** | 90 | ≤3·δz | PRIMARY |
| **A6** | **T1 (scale): 0 violations / 90.** 1 slot ill-conditioned (`GSE24369 / all_comparator_sarcoma / replication_stress`, `t=−0.001`, `Δ=−0.0001`) — T1 **not evaluable** there, UNKNOWN not passed; it passes T0/T2/T3. | 90 | propagated interval | PRIMARY |
| **A7** | **T2 (shape/df): 0 violations / 90. Max `\|df_obs − df_c\| = 0.049986`** (`GSE24369 / NONFET / replication_stress`, n=(6,12), committed 12.3 vs observed 12.250014) — inside the 0.05 print half-ulp by **1.4e-5**. | 90 | ±0.05 (df print precision) | PRIMARY |
| **A8** | **T3 (means): 0 violations / 90.** Reported but **not counted as independent** — it is Stage-1 recovery evidence re-used. The independent gates are T1 and T2, which use variance information the recovery never touched. | 180 means | ≤2·δz | PRIMARY |
| **A9** | **A wrong join cannot pass silently — measured, which was the named risk.** Labels rotated by 1, 2 or 3 positions, and the canonical adjacent-boundary swap (off-by-one): **Stage 1 recovers 0/10 families** and **Stage 2 fails 90/90 slots (100%)** in every case. 200 seeded random label shuffles fail **89–90/90 (98.9–100%)**. | 4 systematic + 200 random | — | PRIMARY |
| **A10** | **Detection power under statistic perturbation** (W17b's protocol, same units): `n_a±1` **100%/100%**, `n_b±1` **98.9%/98.9%**, `df±1` **100%/100%**, `df−0.1` (1 ulp) **94.4%**, `df+0.1` **85.6%**, `Δ±0.001` **98.9%/97.8%**, `Δ±0.0001` (1 ulp) **31.1%/37.8%**. | 90 | — | PRIMARY |
| **A11** | **Inversion conditioning:** 54/90 slots admit two roots (`df ≥ max(n_a,n_b)−1`); **0 slots at the discriminant floor** (`D<1e-6`). Handled by the root-agnostic forward gate, not by picking a root. | 90 | — | PRIMARY |
| **A12** | **The partition verdict: neither 72/234 nor 84/222 is correct; the artifact's own testable count is 90.** Both prior numbers are reconstructed exactly (see below). | 90 vs 84 vs 72 | exact | PRIMARY |
| **A13** | **The loose test could not have caught the mis-imputation.** On all 6 GSE24369 NONFET slots, the W17 feasibility interval PASSES under both the true `n_b=12` (`[5,16]`) and the plausible wrong `n_b=29` (`[5,33]`). The point test distinguishes them. | 6 slots | exact | PRIMARY |
| **A14** | Whether the *upstream* scores are correctly computed from the series matrices | — | not testable from this artifact | UNKNOWN |

### Outcome, stated plainly

**The ATR artifact IS point-verifiable, and it passes. Zero violations on T0/T1/T2/T3 across all 90 slots that carry a statistic.** W17b's named alternative — *"the ATR artifact does not persist enough to verify itself"* — **is false, and I am reporting that with the same willingness I would have reported the reverse.** The artifact persists exactly what the inversion needs; it persists it in a *different shape* (a positional array plus a separate ordered annotation list, instead of joined per-concept rows), and W17b's conservative reading of that shape was the only thing standing between the two artifacts. **No generator change is proposed, because none is warranted.**

The remaining 216 slots are not a persistence gap: each carries an explicit `_status` recording an empty or single-member arm (`n_a=0` or `n_b=0`), so **no statistic was ever computed there to verify.** That is the generator behaving correctly, not failing to persist.

### A7 is the sharpest single number

`0.049986` against a `0.05` half-ulp — inside by 1.4e-5, i.e. the test came within **0.03%** of its own limit and did not cross it. As in W17b, a wrong variance convention (ddof=0), a wrong grouping or a stale array would miss by orders of magnitude, not by 1.4e-5. This is a tight pass, not a slack one — and it is tight for a mechanical reason: it is what pure 1-dp rounding predicts and nothing else.

### The partition, settled from the artifact itself (item 5)

The artifact enumerates **408** slots across 4 contrast families × 11 platforms + pooled. **102 are JSON `null`; 306 are non-null** — this is the "306" both W17 and W17b report, and **both are right about it.** Of those 306, **exactly 90 carry both `t` and `df`**, distributed as:

```
per_platform  all_comparator_sarcoma                        24
per_platform  all_comparator_sarcoma_PROLIFERATION_ADJUSTED 20
per_platform  NONFET_comparators                            12
per_platform  FET_comparators                                6
pooled        all_comparator_sarcoma                        12
pooled        all_comparator_sarcoma_PROLIFERATION_ADJUSTED 10
pooled        NONFET_comparators                             6
```

Both prior partitions are then reproduced **exactly** by the `n_b` imputation rule each applied:

- `90 − FET(6) = **84**` → **W17's 84 / 222.** W17 could resolve `n_b` for the per-platform NONFET arms (by some inheritance rule) but not for FET.
- `90 − FET(6) − NONFET(12) = **72**` → **W17b's 72 / 234.** W17b declined to impute `n_b` for either FET or NONFET on the per-platform blocks, since only `cross_platform_pooled` carries `FET_comparator_classes` (and it is `[]`).

**Verdict: neither partition is correct, and the disagreement was never about arithmetic — it was that both workers tried to *impute* `n_b` from a class list the per-platform blocks do not carry, instead of *recovering* the arm from the score arrays, which the blocks do carry.** The correct partition is **90 testable / 216 carrying no statistic**, out of 306 non-null slots (408 enumerated). W17b's is the more conservative of the two and its self-description as such is accurate; **W17's 84 is the closer number but for a reason that does not survive scrutiny** — A13 shows the loose feasibility interval passes on the NONFET slots under both the true `n_b=12` and a wrong `n_b=29`, so W17's inclusion of those 12 slots was not validated by its own test. Both reported **0 violations**, and that verdict stands unchanged under the corrected partition.

---

## Validation evidence

### RUN

**Environment for all runs:** container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `python3 --version` → `Python 3.11.15`, cwd `/tmp/claude-0/w17d`, stdlib only, no network. Repository read at HEAD `b9a0257e6acff53ad22535cf2adf261313e0b250`.

**Run 1 — slot inventory** — `cd /tmp/claude-0/w17d && python3 inventory.py; echo "EXIT=$?"`
```
TOTAL concept slots: 408
slots with _status  : 216
slots with t and df : 90

key-shapes:
   216 ('_status',)
   102 ('<None>',)
   90 ('delta_a_minus_b', 'df', 'mean_a', 'mean_b', 't')

_status values:
   92 x underpowered: n_a=0, n_b=0
   56 x underpowered: n_a=0, n_b=2
   28 x underpowered: n_a=0, n_b=4
   28 x underpowered: n_a=0, n_b=3
   12 x underpowered: n_a=10, n_b=0
EXIT=0
```

**Run 2 — the point gate** — `python3 atr_point_verify.py; echo "EXIT=$?"`
```
POOLED class_counts recomputed from concatenated GSE4303 annotations: {"DFSP": 8, "EMC": 10, "GIST": 5, "MFH_UPS": 4, "unclassified": 9}
POOLED class_counts committed                                      : {"DFSP": 8, "EMC": 10, "GIST": 5, "MFH_UPS": 4, "unclassified": 9}
POOLED n_samples_pooled committed: 36 | recomputed: 36

STAGE 1 - positional join + comparator-group recovery
GSE24369_series_matrix.txt.gz    all_comparator_sarcoma      concepts=12 n_a= 6 max|mean_a err|=5.00e-05
      -> ADMITTED n_b=29 max|mean_b err|=4.48e-05  classes=['LGFMS', 'desmoid_fibromatosis', 'fibrosarcoma']
GSE24369_series_matrix.txt.gz    all_comparator_sarcoma_PRO  concepts=10 n_a= 6 max|mean_a err|=5.00e-05
      -> ADMITTED n_b=29 max|mean_b err|=3.79e-05  classes=['LGFMS', 'desmoid_fibromatosis', 'fibrosarcoma']
GSE24369_series_matrix.txt.gz    FET_comparators             concepts= 6 n_a= 6 max|mean_a err|=5.00e-05
      -> ADMITTED n_b=17 max|mean_b err|=4.71e-05  classes=['LGFMS']
GSE24369_series_matrix.txt.gz    NONFET_comparators          concepts= 6 n_a= 6 max|mean_a err|=5.00e-05
      -> ADMITTED n_b=12 max|mean_b err|=5.00e-05  classes=['desmoid_fibromatosis', 'fibrosarcoma']
GSE4303-GPL3290_...              all_comparator_sarcoma      concepts=12 n_a=10 max|mean_a err|=4.00e-05
      -> ADMITTED n_b= 6 max|mean_b err|=5.00e-05  classes=['DFSP', 'GIST']
GSE4303-GPL3290_...              all_comparator_sarcoma_PRO  concepts=10 n_a=10 max|mean_a err|=5.00e-05
      -> ADMITTED n_b= 6 max|mean_b err|=5.00e-05  classes=['DFSP', 'GIST']
GSE4303-GPL3290_...              NONFET_comparators          concepts= 6 n_a=10 max|mean_a err|=4.00e-05
      -> ADMITTED n_b= 6 max|mean_b err|=3.33e-05  classes=['DFSP', 'GIST']
cross_platform_pooled            all_comparator_sarcoma      concepts=12 n_a=10 max|mean_a err|=4.00e-05
      -> ADMITTED n_b=17 max|mean_b err|=4.71e-05  classes=['DFSP', 'GIST', 'MFH_UPS']
cross_platform_pooled            all_comparator_sarcoma_PRO  concepts=10 n_a=10 max|mean_a err|=5.00e-05
      -> ADMITTED n_b=17 max|mean_b err|=4.71e-05  classes=['DFSP', 'GIST', 'MFH_UPS']
cross_platform_pooled            NONFET_comparators          concepts= 6 n_a=10 max|mean_a err|=4.00e-05
      -> ADMITTED n_b=17 max|mean_b err|=4.71e-05  classes=['DFSP', 'GIST', 'MFH_UPS']

STAGE 2 - T0/T1/T2/T3 point gate
concept slots enumerated (incl. null)      : 408
  non-null slots                           : 306
  slots carrying BOTH t and df (testable)  : 90
  slots actually point-tested              : 90
  UNKNOWN (group unrecoverable / n<2)      : 0
  AMBIGUOUS (>1 admissible group)          : 0
T0 delta identity        : 0 violation(s)
T1 scale  S vs (D/t)^2   : 0 violation(s)   [1 ill-conditioned |t|<=0.005, not evaluable]
T2 shape  df_obs vs df_c : 0 violation(s)
T3 means (Stage-1 reuse) : 0 violation(s)
max |df_obs - df_committed| : 0.049986  ('GSE24369_series_matrix.txt.gz', 'contrast_EMC_vs_NONFET_comparators', 'replication_stress', 6, 12, 12.3, 12.250014188613829)
max relative |S_obs - (delta/t)^2| / S_obs : 2.221e-02  ('GSE24369...', 'contrast_EMC_vs_FET_comparators', 'ATM_signalling_DSB_repair', 0.0002245812200115339, 0.00022956841138659323)
slots with TWO admissible inversion roots  : 54
slots with near-zero discriminant (D<1e-6) : 0
VERDICT: PASS
EXIT=0
```

**Run 3 — join discrimination and power** — `python3 atr_power.py; echo "EXIT=$?"`
```
recovered families: 10 | testable slots: 90

unperturbed baseline:
  identity (correct join)            STAGE-1 families still recovering 10/10 | STAGE-2 slots failing T1&T2: 0/90 = 0.0%

JOIN perturbations:
  labels rotated by 1                STAGE-1 families still recovering 0/10 | STAGE-2 slots failing T1&T2: 90/90 = 100.0%
  labels rotated by 2                STAGE-1 families still recovering 0/10 | STAGE-2 slots failing T1&T2: 90/90 = 100.0%
  labels rotated by 3                STAGE-1 families still recovering 0/10 | STAGE-2 slots failing T1&T2: 90/90 = 100.0%
  adjacent-boundary swap (off-by-one) STAGE-1 families still recovering 0/10 | STAGE-2 slots failing T1&T2: 90/90 = 100.0%
  random label shuffle (200 draws)   STAGE-2 slots failing T1&T2: min 89/90 = 98.9%, max 90/90 = 100.0%

STATISTIC perturbations (W17b protocol):
  n_a -1                  : would-fail 90/90 = 100.0%
  n_a +1                  : would-fail 90/90 = 100.0%
  n_b -1                  : would-fail 89/90 = 98.9%
  n_b +1                  : would-fail 89/90 = 98.9%
  df -1                   : would-fail 90/90 = 100.0%
  df +1                   : would-fail 90/90 = 100.0%
  df -0.1 (1 ulp)         : would-fail 85/90 = 94.4%
  df +0.1 (1 ulp)         : would-fail 77/90 = 85.6%
  delta -0.001            : would-fail 89/90 = 98.9%
  delta +0.001            : would-fail 88/90 = 97.8%
  delta -0.0001 (1 ulp)   : would-fail 28/90 = 31.1%
  delta +0.0001 (1 ulp)   : would-fail 34/90 = 37.8%
EXIT=0
```

**Run 4 — the partition and the loose-test comparison** — `python3 partition.py; echo "EXIT=$?"`
```
enumerated slots (incl. JSON null) : 408
non-null slots  ('306')            : 306
slots with BOTH t and df           : 90
   per_platform FET_comparators                              6
   per_platform NONFET_comparators                           12
   per_platform all_comparator_sarcoma                       24
   per_platform all_comparator_sarcoma_PROLIFERATION_ADJUSTED 20
   pooled       NONFET_comparators                           6
   pooled       all_comparator_sarcoma                       12
   pooled       all_comparator_sarcoma_PROLIFERATION_ADJUSTED 10

per-platform FET slots with t/df    : 6
per-platform NONFET slots with t/df : 12
90 - FET(6)                       = 84   <- W17 reported 84 checked / 222 skipped
90 - FET(6) - NONFET(12)            = 72   <- W17b reported 72 checked / 234 skipped

LOOSE feasibility test (W17's) on GSE24369 NONFET, true n_b=12 vs the
plausible mis-imputation n_b = n_comparator = 29 (all comparator sarcoma):
   ATM_signalling_DSB_repair    df= 15.8 TRUE   n_b=12 feasible[5,16] -> PASS
   ATM_signalling_DSB_repair    df= 15.8 WRONG  n_b=29 feasible[5,33] -> PASS
   ATR_CHK1_activity            df= 14.3 TRUE   n_b=12 feasible[5,16] -> PASS
   ATR_CHK1_activity            df= 14.3 WRONG  n_b=29 feasible[5,33] -> PASS
   replication_stress           df= 12.3 TRUE   n_b=12 feasible[5,16] -> PASS
   replication_stress           df= 12.3 WRONG  n_b=29 feasible[5,33] -> PASS
   stalled_fork_response        df= 15.5 TRUE   n_b=12 feasible[5,16] -> PASS
   stalled_fork_response        df= 15.5 WRONG  n_b=29 feasible[5,33] -> PASS
   S_phase_E2F                  df= 13.6 TRUE   n_b=12 feasible[5,16] -> PASS
   S_phase_E2F                  df= 13.6 WRONG  n_b=29 feasible[5,33] -> PASS
   DNA_damage_checkpoint        df= 13.4 TRUE   n_b=12 feasible[5,16] -> PASS
   DNA_damage_checkpoint        df= 13.4 WRONG  n_b=29 feasible[5,33] -> PASS
EXIT=0
```

**Run 5 — write-isolation check** — `git status --porcelain && git rev-parse HEAD`
```
?? research/autonomy/opus-capacity-campaign-20260908/reports/W01c-emc-deposit-literature-inventory.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W13b-pooled-cohort-unit-resolution.md
b9a0257e6acff53ad22535cf2adf261313e0b250
```
Both untracked files are other workers' coordinator-collected reports. Nothing of mine. `ls -la /tmp/claude-0/w17d` shows my five scripts and nothing else.

**Code — `/tmp/claude-0/w17d/atr_point_verify.py`** (returned inline; nothing written into the repository):

```python
"""W17d: EXACT variance-inversion point test of emc-atr-vulnerability.json part B.

QUESTION. W17b's exact test reached emc-expression-panels.json because each Welch block
carries its own `per_sample[].z_vs_array` rows.  The ATR artifact carries no such rows.
It DOES carry, per platform:
    scores[concept]                        -> list of floats, len == n_samples
    proliferation_adjusted_scores[concept] -> list of floats, len == n_samples
    sample_annotations_verbatim            -> list of dicts, len == n_samples, each with 'class'
The hypothesis under test is that these two lists are POSITIONALLY ALIGNED, i.e. that
scores[c][i] is the score of the sample described by sample_annotations_verbatim[i].
That hypothesis is NOT assumed.  It is tested, and the group definitions (which classes
form the comparator / FET / NONFET arms) are RECOVERED by exhaustive search and required
to be UNIQUE, before any variance is computed.

STAGE 1 - JOIN + GROUP RECOVERY (means only).
  For each platform and each contrast family, search all 2^k-1 non-empty subsets of the
  non-EMC classes present.  A subset is ADMITTED only if, under the positional join, it
  reproduces the committed mean_b of EVERY concept in that family simultaneously to
  |mean_obs - mean_c| <= 2*dz.  mean_a is likewise required to match for every concept
  under group EMC.  If zero subsets are admitted the slot is UNKNOWN (join unestablished);
  if more than one is admitted the slot is AMBIGUOUS and is reported, not silently picked.

STAGE 2 - THE POINT GATE (variance; independent of Stage 1's evidence).
  Identical to W17b:  v_a=s_a^2/n_a, v_b=s_b^2/n_b, S=v_a+v_b, A=n_a-1, B=n_b-1.
    (i)  t = Delta/sqrt(S)                 => S = (Delta/t)^2                  [T1 scale]
    (ii) df = S^2/(v_a^2/A + v_b^2/B)                                          [T2 shape]
  With f=v_a/S, (ii) is f^2/A+(1-f)^2/B = 1/df, a quadratic whose discriminant
  D=(1/A+1/B)/df - 1/(A*B) is >=0 iff df <= A+B, reproducing the feasibility ceiling.
  Both roots lie in [0,1] iff df >= max(A,B): the branch ambiguity is REAL and is NOT
  silently resolved.  The gate is the root-agnostic FORWARD form (T1 on S, T2 on df);
  the inversion is reported separately as an interval, exactly as in W17b.

TOLERANCE - stated before running, propagated from the artifact's own print precision.
  scores / proliferation_adjusted_scores / mean_a / mean_b / delta : 4 dp -> dz  = 5e-5
  t  : 3 dp -> dt  = 5e-4        df : 1 dp -> ddf = 0.05
  d(s^2) <= (2*dz*sum|z_i - zbar| + n*dz^2)/(n-1)   [rigorous worst case];  dv = d(s^2)/n
  T0 identity : |(mean_a - mean_b) - delta_a_minus_b| <= 3*dz
  T1 scale    : [S_obs +- dS] intersects [((|D|-dz)/(|t|+dt))^2, ((|D|+dz)/(|t|-dt))^2]
                NOT EVALUABLE (UNKNOWN, not passed) where |t| <= 10*dt = 0.005
  T2 shape    : df range over the 4 corners of [v_a+-dv_a]x[v_b+-dv_b] intersects df_c+-0.05
  T3 means    : |mean_obs - mean_c| <= 2*dz     (on recovered slots this is Stage-1
                evidence re-used, so it is reported but NOT counted as independent)
  Sample variance is ddof=1 (pre-stated).  ddof=0 computed only as a diagnostic on failure.
No criterion is changed after seeing any result.
"""
import json, math, sys, itertools

P = "/home/user/Rare-cancers/research/modalities/emc-atr-vulnerability.json"
DZ, DT, DDF = 5e-5, 5e-4, 0.05
ILL = 10.0*DT

d = json.load(open(P)); B = d['part_b_emc_tumour_signature']
FAMS = ['contrast_EMC_vs_all_comparator_sarcoma',
        'contrast_EMC_vs_all_comparator_sarcoma_PROLIFERATION_ADJUSTED',
        'contrast_EMC_vs_FET_comparators',
        'contrast_EMC_vs_NONFET_comparators']
ADJ = {'contrast_EMC_vs_all_comparator_sarcoma_PROLIFERATION_ADJUSTED'}

def var(xs, ddof=1):
    n=len(xs); m=sum(xs)/n
    return sum((x-m)**2 for x in xs)/(n-ddof), m
def dvar(xs):
    n=len(xs); m=sum(xs)/n
    return (2*DZ*sum(abs(x-m) for x in xs) + n*DZ*DZ)/(n-1)
def df_of(va,vb,A,Bb):
    S=va+vb; return S*S/(va*va/A + vb*vb/Bb)
def froots(A,Bb,df):
    Pp=1.0/A+1.0/Bb; D=Pp/df-1.0/(A*Bb)
    if D<0: return None,D
    r=math.sqrt(D); return sorted(((1.0/Bb-r)/Pp,(1.0/Bb+r)/Pp)),D

# ---------------- assemble the score panels -------------------------------
# a "panel" = (name, list of class labels, {concept: [scores]}, {concept: [padj]})
panels={}
for name,b in B['per_platform'].items():
    lbl=[r['class'] for r in b['sample_annotations_verbatim']]
    assert len(lbl)==b['n_samples']
    panels[name]=(lbl,b.get('scores') or {}, b.get('proliferation_adjusted_scores') or {})
# pooled = concatenation of the GSE4303 platforms (scope stated in the artifact:
# "platforms of GSE4303 only - never across series").  Concatenation order does not
# affect any group mean or variance; the class_counts identity is verified below.
g4=[n for n,b in B['per_platform'].items() if b.get('series')=='GSE4303']
g4.sort()
plbl=[]; psc={}; ppa={}
concepts=set()
for n in g4: concepts |= set(panels[n][1].keys())
for n in g4:
    lbl,sc,pa=panels[n]; plbl+=lbl
    for c in concepts:
        psc.setdefault(c,[]).extend(sc.get(c,[None]*len(lbl)))
        ppa.setdefault(c,[]).extend(pa.get(c,[None]*len(lbl)))
panels['cross_platform_pooled']=(plbl,psc,ppa)
POOLCC={}
for c in plbl: POOLCC[c]=POOLCC.get(c,0)+1
print("POOLED class_counts recomputed from concatenated GSE4303 annotations:",
      json.dumps(POOLCC,sort_keys=True))
print("POOLED class_counts committed                                      :",
      json.dumps(B['cross_platform_pooled']['class_counts'],sort_keys=True))
print("POOLED n_samples_pooled committed:",B['cross_platform_pooled']['n_samples_pooled'],
      "| recomputed:",len(plbl))
print("GSE4303 platforms concatenated:",g4)
print()

def blocks():
    for n,b in B['per_platform'].items(): yield n,b
    yield 'cross_platform_pooled',B['cross_platform_pooled']

# ---------------- STAGE 1: join + group recovery --------------------------
recovered={}   # (panel, family) -> list of admitted (subset, n_b, max err)
stage1=[]
for name,b in blocks():
    lbl,sc,pa = panels[name]
    nonemc=sorted(set(lbl)-{'EMC'})
    for fam in FAMS:
        fb=b.get(fam) or {}
        live={c:s for c,s in fb.items() if isinstance(s,dict) and 't' in s and 'df' in s}
        if not live: continue
        src = pa if fam in ADJ else sc
        # mean_a check (group EMC), all concepts
        ia=[i for i,l in enumerate(lbl) if l=='EMC']
        amax=0.0; aok=True
        for c,s in live.items():
            v=src.get(c)
            if not v or any(v[i] is None for i in ia): aok=False; break
            m=sum(v[i] for i in ia)/len(ia)
            amax=max(amax,abs(m-s['mean_a']))
        if not aok or amax>2*DZ:
            recovered[(name,fam)]=('MEAN_A_FAIL',amax if aok else None); continue
        adm=[]
        for k in range(1,len(nonemc)+1):
            for sub in itertools.combinations(nonemc,k):
                ib=[i for i,l in enumerate(lbl) if l in sub]
                if len(ib)<2: continue
                ok=True; mx=0.0
                for c,s in live.items():
                    v=src.get(c)
                    if not v or any(v[i] is None for i in ib): ok=False; break
                    m=sum(v[i] for i in ib)/len(ib)
                    e=abs(m-s['mean_b'])
                    if e>2*DZ: ok=False; break
                    mx=max(mx,e)
                if ok: adm.append((sub,len(ib),mx))
        recovered[(name,fam)]=adm
        stage1.append((name,fam,len(live),len(ia),amax,adm))

print("="*100)
print("STAGE 1 - positional join + comparator-group recovery")
print("="*100)
for name,fam,nlive,na,amax,adm in stage1:
    tag=fam.replace('contrast_EMC_vs_','')
    print(f"{name[:38]:40s} {tag[:34]:36s} concepts={nlive:2d} n_a={na:2d} max|mean_a err|={amax:.2e}")
    if not adm: print("      -> NO admissible comparator subset  => JOIN/GROUP UNESTABLISHED")
    for sub,nb,mx in adm:
        print(f"      -> ADMITTED n_b={nb:2d} max|mean_b err|={mx:.2e}  classes={list(sub)}")
    if len(adm)>1: print("      -> AMBIGUOUS: more than one subset reproduces every mean_b")
print()

# ---------------- STAGE 2: the point gate ---------------------------------
print("="*100)
print("STAGE 2 - T0/T1/T2/T3 point gate")
print("="*100)
tot=nonnull=live_tot=0
checked=0; unknown=[]; ambiguous=[]
vT0=[];vT1=[];vT2=[];vT3=[]
ill=0; tworoot=0; nearD=0; worst_df=(0.0,None); worst_S=(0.0,None)
fin=[]; ddof0_pass=0
for name,b in blocks():
    lbl,sc,pa=panels[name]
    for fam in FAMS:
        fb=b.get(fam) or {}
        for c,s in fb.items():
            tot+=1
            if not isinstance(s,dict): continue
            nonnull+=1
            if 't' not in s or 'df' not in s: continue
            live_tot+=1
            rec=recovered.get((name,fam))
            if not isinstance(rec,list) or len(rec)==0:
                unknown.append((name,fam,c,'no admissible group')); continue
            if len(rec)>1:
                ambiguous.append((name,fam,c,[r[0] for r in rec])); continue
            sub,nb,_=rec[0]
            src = pa if fam in ADJ else sc
            v=src.get(c)
            za=[v[i] for i,l in enumerate(lbl) if l=='EMC']
            zb=[v[i] for i,l in enumerate(lbl) if l in sub]
            na=len(za)
            if na<2 or nb<2: unknown.append((name,fam,c,'n<2')); continue
            checked+=1
            A,Bb=na-1,nb-1
            s2a,ma=var(za); s2b,mb=var(zb)
            va,vb=s2a/na,s2b/nb
            dva,dvb=dvar(za)/na,dvar(zb)/nb
            S=va+vb; dS=dva+dvb
            t_c,df_c,dl_c=s['t'],s['df'],s['delta_a_minus_b']
            # T0
            if abs((s['mean_a']-s['mean_b'])-dl_c)>3*DZ:
                vT0.append((name,fam,c,s['mean_a']-s['mean_b'],dl_c))
            # T1
            at,ad=abs(t_c),abs(dl_c)
            if at<=ILL:
                ill+=1; t1ok=None
            else:
                Shi=((ad+DZ)/(at-DT))**2; Slo=(max(ad-DZ,0.0)/(at+DT))**2
                t1ok = not (S+dS<Slo or S-dS>Shi)
                if not t1ok:
                    gap = Slo-(S+dS) if S+dS<Slo else (S-dS)-Shi
                    vT1.append((name,fam,c,na,nb,t_c,dl_c,S,dS,Slo,Shi,gap))
                rel=abs(S-(dl_c/t_c)**2)/S
                if rel>worst_S[0]: worst_S=(rel,(name,fam,c,S,(dl_c/t_c)**2))
            # T2
            corners=[df_of(va+sa*dva,vb+sb*dvb,A,Bb) for sa in(-1,1) for sb in(-1,1)]
            lo,hi=min(corners),max(corners)
            t2ok = not (hi<df_c-DDF or lo>df_c+DDF)
            dfo=df_of(va,vb,A,Bb)
            if not t2ok:
                gap=(df_c-DDF)-hi if hi<df_c-DDF else lo-(df_c+DDF)
                vT2.append((name,fam,c,na,nb,df_c,dfo,lo,hi,gap))
                s2a0,_=var(za,0); s2b0,_=var(zb,0)
                if abs(df_of(s2a0/na,s2b0/nb,A,Bb)-df_c)<=DDF: ddof0_pass+=1
            e=abs(dfo-df_c)
            if e>worst_df[0]: worst_df=(e,(name,fam,c,na,nb,df_c,dfo))
            # T3
            if abs(ma-s['mean_a'])>2*DZ: vT3.append((name,fam,c,'a',ma,s['mean_a']))
            if abs(mb-s['mean_b'])>2*DZ: vT3.append((name,fam,c,'b',mb,s['mean_b']))
            # inversion diagnostics
            rr,D=froots(A,Bb,df_c)
            if rr is not None:
                admr=[f for f in rr if -1e-9<=f<=1+1e-9]
                if len(admr)==2 and abs(admr[0]-admr[1])>1e-9: tworoot+=1
                if D<1e-6: nearD+=1
            fin.append((name,fam,c,na,nb,va/S,df_c,dfo))

print(f"concept slots enumerated (incl. null)      : {tot}")
print(f"  non-null slots                           : {nonnull}")
print(f"  slots carrying BOTH t and df (testable)  : {live_tot}")
print(f"  slots actually point-tested              : {checked}")
print(f"  UNKNOWN (group unrecoverable / n<2)      : {len(unknown)}")
print(f"  AMBIGUOUS (>1 admissible group)          : {len(ambiguous)}")
for u in unknown[:20]: print("    UNKNOWN",u)
for a in ambiguous[:20]: print("    AMBIG  ",a)
print(f"T0 delta identity        : {len(vT0)} violation(s)")
print(f"T1 scale  S vs (D/t)^2   : {len(vT1)} violation(s)   [{ill} ill-conditioned |t|<={ILL}, not evaluable]")
print(f"T2 shape  df_obs vs df_c : {len(vT2)} violation(s)")
print(f"T3 means (Stage-1 reuse) : {len(vT3)} violation(s)")
if vT2: print(f"  of the T2 violations, ddof=0 would have passed: {ddof0_pass}")
for nm,vv in (("T0",vT0),("T1",vT1),("T2",vT2),("T3",vT3)):
    for r in vv[:30]: print(f"  VIOL-{nm}",r)
print(f"max |df_obs - df_committed| : {worst_df[0]:.6f}  {worst_df[1]}")
print(f"max relative |S_obs - (delta/t)^2| / S_obs : {worst_S[0]:.3e}  {worst_S[1]}")
print(f"slots with TWO admissible inversion roots  : {tworoot}")
print(f"slots with near-zero discriminant (D<1e-6) : {nearD}")
fail=bool(vT0 or vT1 or vT2 or vT3)
print("VERDICT:", "FAIL" if fail else "PASS")
sys.exit(1 if fail else 0)
```

**Code — `/tmp/claude-0/w17d/atr_power.py`** (as run in Run 3):

```python
"""W17d part 2 - how detectable is a WRONG join, and what is the point test's power?

The risk named in this lane: score arrays are ordered but class labels are carried
separately, so an off-by-one or a mis-ordered join could silently produce a wrong
variance that still passes a self-consistency check.  This measures that directly.

PERTURBATIONS OF THE JOIN (labels moved relative to the score arrays):
  rot k    : class-label vector rotated by k positions
  swapbnd  : the two samples astride each class boundary exchanged (a canonical off-by-one)
  shuffle  : labels randomly permuted (seeded), 200 draws, worst case reported
For each we report (i) STAGE-1 survival: how many of the 10 contrast families still admit
any comparator subset reproducing every committed mean, and (ii) STAGE-2 failure: of the
90 slots, how many fail the combined T1&T2 variance gate with the recovered subset forced.

PERTURBATIONS OF THE COMMITTED STATISTICS (W17b's power protocol, same units):
  n_a+-1, n_b+-1, df+-1, df+-0.1 (1 ulp), delta+-0.001, delta+-0.0001 (1 ulp)
Tolerances are exactly those of atr_point_verify.py and are NOT changed here.
"""
import json, math, random, itertools
P="/home/user/Rare-cancers/research/modalities/emc-atr-vulnerability.json"
DZ,DT,DDF=5e-5,5e-4,0.05; ILL=10.0*DT
d=json.load(open(P)); B=d['part_b_emc_tumour_signature']
FAMS=['contrast_EMC_vs_all_comparator_sarcoma',
      'contrast_EMC_vs_all_comparator_sarcoma_PROLIFERATION_ADJUSTED',
      'contrast_EMC_vs_FET_comparators','contrast_EMC_vs_NONFET_comparators']
ADJ={'contrast_EMC_vs_all_comparator_sarcoma_PROLIFERATION_ADJUSTED'}
def var(xs):
    n=len(xs); m=sum(xs)/n; return sum((x-m)**2 for x in xs)/(n-1), m
def dvar(xs):
    n=len(xs); m=sum(xs)/n; return (2*DZ*sum(abs(x-m) for x in xs)+n*DZ*DZ)/(n-1)
def df_of(va,vb,A,Bb):
    S=va+vb; return S*S/(va*va/A+vb*vb/Bb)

panels={}
for name,b in B['per_platform'].items():
    panels[name]=([r['class'] for r in b['sample_annotations_verbatim']],
                  b.get('scores') or {}, b.get('proliferation_adjusted_scores') or {})
g4=sorted(n for n,b in B['per_platform'].items() if b.get('series')=='GSE4303')
concepts=set().union(*[set(panels[n][1]) for n in g4])
plbl=[];psc={};ppa={}
for n in g4:
    lbl,sc,pa=panels[n]; plbl+=lbl
    for c in concepts:
        psc.setdefault(c,[]).extend(sc.get(c,[None]*len(lbl)))
        ppa.setdefault(c,[]).extend(pa.get(c,[None]*len(lbl)))
panels['cross_platform_pooled']=(plbl,psc,ppa)
def blocks():
    for n,b in B['per_platform'].items(): yield n,b
    yield 'cross_platform_pooled',B['cross_platform_pooled']

# recovered subsets from Stage 1 (re-derived here, unperturbed)
REC={}
for name,b in blocks():
    lbl,sc,pa=panels[name]; nonemc=sorted(set(lbl)-{'EMC'})
    for fam in FAMS:
        live={c:s for c,s in (b.get(fam) or {}).items() if isinstance(s,dict) and 't' in s}
        if not live: continue
        src=pa if fam in ADJ else sc
        for k in range(1,len(nonemc)+1):
            for sub in itertools.combinations(nonemc,k):
                ib=[i for i,l in enumerate(lbl) if l in sub]
                if len(ib)<2: continue
                if all(abs(sum(src[c][i] for i in ib)/len(ib)-s['mean_b'])<=2*DZ
                       for c,s in live.items()):
                    REC[(name,fam)]=sub
SLOTS=[]
for name,b in blocks():
    lbl,sc,pa=panels[name]
    for fam in FAMS:
        for c,s in (b.get(fam) or {}).items():
            if isinstance(s,dict) and 't' in s and 'df' in s and (name,fam) in REC:
                SLOTS.append((name,fam,c,s,REC[(name,fam)]))
print("recovered families:",len(REC),"| testable slots:",len(SLOTS))

def gate(za,zb,t_c,df_c,dl_c,na=None,nb=None):
    na=len(za) if na is None else na; nb=len(zb) if nb is None else nb
    if na<2 or nb<2 or len(za)<2 or len(zb)<2: return False
    A,Bb=na-1,nb-1
    s2a,_=var(za); s2b,_=var(zb)
    va,vb=s2a/na,s2b/nb; dva,dvb=dvar(za)/na,dvar(zb)/nb
    S=va+vb; dS=dva+dvb
    at,ad=abs(t_c),abs(dl_c)
    if at>ILL:
        Shi=((ad+DZ)/(at-DT))**2; Slo=(max(ad-DZ,0.0)/(at+DT))**2
        if S+dS<Slo or S-dS>Shi: return False
    cor=[df_of(va+sa*dva,vb+sb*dvb,A,Bb) for sa in(-1,1) for sb in(-1,1)]
    if max(cor)<df_c-DDF or min(cor)>df_c+DDF: return False
    return True

def groups(lbl,src,c,sub):
    za=[src[c][i] for i,l in enumerate(lbl) if l=='EMC']
    zb=[src[c][i] for i,l in enumerate(lbl) if l in sub]
    return za,zb

def run(lblmap,label):
    s1=0; fail=0
    for (name,fam) in REC:
        lbl,sc,pa=panels[name]; L=lblmap(name,lbl)
        src=pa if fam in ADJ else sc
        live={c:s for c,s in (B['per_platform'].get(name) or B['cross_platform_pooled'])[fam].items()
              if isinstance(s,dict) and 't' in s}
        nonemc=sorted(set(L)-{'EMC'}); found=False
        for k in range(1,len(nonemc)+1):
            for sub in itertools.combinations(nonemc,k):
                ib=[i for i,l in enumerate(L) if l in sub]
                if len(ib)<2: continue
                if all(abs(sum(src[c][i] for i in ib)/len(ib)-s['mean_b'])<=2*DZ
                       for c,s in live.items()): found=True; break
            if found: break
        s1+=found
    for name,fam,c,s,sub in SLOTS:
        lbl,sc,pa=panels[name]; L=lblmap(name,lbl)
        src=pa if fam in ADJ else sc
        za,zb=groups(L,src,c,sub)
        if not gate(za,zb,s['t'],s['df'],s['delta_a_minus_b']): fail+=1
    print(f"  {label:34s} STAGE-1 families still recovering {s1}/{len(REC)}"
          f" | STAGE-2 slots failing T1&T2: {fail}/{len(SLOTS)} = {100*fail/len(SLOTS):.1f}%")
    return fail

print("\nunperturbed baseline:")
run(lambda n,l:l,"identity (correct join)")
print("\nJOIN perturbations:")
for k in (1,2,3):
    run(lambda n,l,k=k: l[k:]+l[:k], f"labels rotated by {k}")
def swapbnd(n,l):
    l=list(l)
    for i in range(len(l)-1):
        if l[i]!=l[i+1] and i+1<len(l): l[i],l[i+1]=l[i+1],l[i]
    return l
run(swapbnd,"adjacent-boundary swap (off-by-one)")
rnd=random.Random(20260908); worst=10**9; best=-1
for _ in range(200):
    seed=rnd.random()
    def sh(n,l,seed=seed):
        r=random.Random(hash((n,seed))&0xffffffff); l=list(l); r.shuffle(l); return l
    f=0
    for name,fam,c,s,sub in SLOTS:
        lbl,sc,pa=panels[name]; L=sh(name,lbl)
        src=pa if fam in ADJ else sc
        za,zb=groups(L,src,c,sub)
        if not gate(za,zb,s['t'],s['df'],s['delta_a_minus_b']): f+=1
    worst=min(worst,f); best=max(best,f)
print(f"  {'random label shuffle (200 draws)':34s} STAGE-2 slots failing T1&T2:"
      f" min {worst}/{len(SLOTS)} = {100*worst/len(SLOTS):.1f}%, max {best}/{len(SLOTS)} = {100*best/len(SLOTS):.1f}%")

print("\nSTATISTIC perturbations (W17b protocol):")
tests=[("n_a -1",dict(dna=-1)),("n_a +1",dict(dna=1)),("n_b -1",dict(dnb=-1)),("n_b +1",dict(dnb=1)),
       ("df -1",dict(ddf=-1.0)),("df +1",dict(ddf=1.0)),
       ("df -0.1 (1 ulp)",dict(ddf=-0.1)),("df +0.1 (1 ulp)",dict(ddf=0.1)),
       ("delta -0.001",dict(ddl=-1e-3)),("delta +0.001",dict(ddl=1e-3)),
       ("delta -0.0001 (1 ulp)",dict(ddl=-1e-4)),("delta +0.0001 (1 ulp)",dict(ddl=1e-4))]
for lab,kw in tests:
    bad=0
    for name,fam,c,s,sub in SLOTS:
        lbl,sc,pa=panels[name]; src=pa if fam in ADJ else sc
        za,zb=groups(lbl,src,c,sub)
        if not gate(za,zb,s['t'],s['df']+kw.get('ddf',0.0),s['delta_a_minus_b']+kw.get('ddl',0.0),
                    na=len(za)+kw.get('dna',0), nb=len(zb)+kw.get('dnb',0)): bad+=1
    print(f"  {lab:24s}: would-fail {bad}/{len(SLOTS)} = {100*bad/len(SLOTS):.1f}%")
```

`inventory.py`, `recon.py` and `partition.py` are the three short diagnostic scripts quoted in Runs 1 and 4; their full text is in this transcript's tool calls.

### PROPOSED (NOT RUN)

- **No generator repair is proposed.** Item 4 of my dispatch is conditional on regrouping failing; it did not fail, so there is nothing to route. Had it failed, the routed proposal would have been to have the part-B generator emit per-concept `per_sample` rows; **that repair is not warranted and I am not proposing it.**
- Promoting `atr_point_verify.py` into `research/modalities/tests/` alongside W17b's `welch_variance_inversion.py`. **Not run, and deliberately not authored into the tree** — write isolation forbids it, and adding a test tier is a coordinator/owner decision, not mine.
- No paid API, no GPU, no network, no external source attempted. **No content-policy refusal was encountered in this lane.**

---

## Limitations

1. **This is bookkeeping, not biology.** Nothing here bears on EMC efficacy, safety, selectivity, therapeutic window or clinical readiness, and no clinical claim is made. There is no wet lab. The artifact's own verdict (`GENERIC_ONLY`, `signature_specific_to_DDR: False`) is untouched by this work and is not endorsed or contested by it.
2. **A closed loop is not a correct loop.** This proves the committed `(t, df, mean_a, mean_b, Δ)` are a faithful reduction of the committed score arrays. If the score arrays are themselves wrong — mis-parsed from the series matrix, mis-normalised, or the samples mis-classified — every gate still passes. This cannot see upstream of the artifact (A14, UNKNOWN).
3. **T3 is not independent evidence on these slots.** It is Stage-1 recovery evidence re-used, and I have labelled it as such throughout. The independent gates are T1 and T2, which consume variance information the recovery never read.
4. **The positional-join hypothesis is established empirically, not documented.** The artifact contains no field asserting the alignment. My evidence is: exact length agreement everywhere; unique simultaneous 4-dp mean reproduction across 6–12 concepts per family; exact set agreement with the independent `comparator_classes_used` field; exact `class_counts` reproduction on pooling; and 100% rejection of every perturbed join. That is strong, but it is inference from consistency, not a persisted contract — **a future generator change could break the alignment silently for a reader that assumes it.** This is the one genuine (and small) documentation weakness I found, and it is not a computational defect.
5. **1 of 90 slots is ill-conditioned for T1** (`|t| = 0.001 ≤ 0.005`): the implied scale `(Δ/t)²` diverges and T1 is **not evaluable**. That slot is UNKNOWN on T1, not passed. It passes T0/T2/T3.
6. **216 of 306 non-null slots carry no statistic**, so they are not verifiable and are not claimed as verified. That is correct generator behaviour on empty arms, not a gap — but it does mean the point test covers 90 slots, not 306, and any statement about "306 slots verified" would be false.
7. **Below print precision is invisible.** Scores and means carry 4 dp, `t` 3 dp, `df` 1 dp; the `Δ ± 1 ulp` row at 31–38% is exactly what a correctly calibrated test gives at its own floor.
8. **54/90 slots admit two inversion roots.** The pass/fail gate is root-agnostic and unaffected, but any *point* estimate of `v_a` from the inversion alone is untrustworthy there.
9. **The pooled panel is a reconstruction.** The artifact does not persist pooled score arrays; I concatenate the 7 GSE4303 platforms. The concatenation is validated by the exact `class_counts` and `n_samples_pooled` identities and by the mean recovery, and group means/variances are order-invariant — but it is a reconstruction, not a persisted object.
10. **Denominator gap inherited from W17/W17b:** the comparator arms pool heterogeneous sarcoma histologies; no arithmetic identity addresses comparator-mixture transfer.
11. **The MDE range remains uninstrumented** and untouched here — `PUB-ATR.json p1s[0]` is W17c's, and I did not go near it.

---

## Stop condition

**Set:** an executed determination of whether the ATR artifact is point-verifiable — either the full slot-level gate result or a rigorous demonstration that it cannot self-verify plus the smallest routed generator repair — and a verdict on the 72/234-vs-84/222 partition.

**MET.** The artifact's structure was read rather than assumed from W17b's description; the positional join and the comparator arms were **recovered by exhaustive search and required to be unique**, not joined on an assumption; the tolerance was propagated from the artifact's own print precision and fixed before any run; the branch ambiguity was handled by W17b's root-agnostic forward gate rather than silently resolved; **four runs executed, all exit 0**; **all 90 slots that carry a statistic pass T0/T1/T2/T3 with zero violations**, max df deviation 0.049986 against a 0.05 rounding bound; and the off-by-one hazard the dispatch named was measured directly — **every perturbed join is rejected, 100%, at both stages.** The partition is settled from the artifact: **90 testable, 216 statistic-free, of 306 non-null (408 enumerated)**; both prior counts are reproduced exactly by their respective `n_b` imputation rules and **both are wrong**, W17b conservatively and W17 by a route its own loose test could not have validated. No criterion was weakened after seeing results. **No violation exists to report, and I did not manufacture one; equally, W17b's negative conjecture was disproved and I report that plainly rather than preserving it.**

---

## Tool-call and wall-clock count actually used

**11 tool calls** (target ~40). **Wall clock ≈ 02:14Z → 02:21Z, roughly 7 minutes of tool time**, ~15 minutes including reading the three briefs and drafting (target ~40 minutes). Returned as soon as the stop condition was met; no padding.

---

## Next concrete action

**One successor, specific:** the two artifacts are now both point-verified internally, and the remaining lane-17 gap is that **neither test is reachable by the repository's own gates** — both `welch_variance_inversion.py` (W17b) and `atr_point_verify.py` (this report) exist only in campaign report bodies, so a future generator change that broke either identity would not be caught. The successor is to prepare a single combined read-only test module covering both artifacts (872 Welch blocks + 90 ATR slots, same tolerances, same root-agnostic gate), legitimately integrated with the repository's **existing** test tiers rather than a new one, and route it to the coordinator/artifact owner as a proposal with its exit-code evidence — **not** to author it into the tree from a worker lane. A smaller companion item: propose that the part-B generator persist an explicit alignment contract (e.g. a `_scores_are_positionally_aligned_with_sample_annotations_verbatim: true` note, or the `gsm` list beside `scores`), which costs nothing and removes Limitation 4 — the one real, if minor, weakness this lane found.

result: The ATR artifact CAN self-verify — W17b's negative conjecture is overturned by execution: `scores`/`proliferation_adjusted_scores` are positionally aligned with `sample_annotations_verbatim`, the comparator arms recover uniquely for all 10 contrast families (corroborated by exact set agreement with the artifact's independent `comparator_classes_used` field and exact pooled `class_counts` reproduction), and **all 90 part-B slots that carry a statistic pass the T0/T1/T2/T3 point gate with zero violations**, max df deviation 0.049986 against a 0.05 rounding bound; the named off-by-one hazard is measured and rejected 100% of the time (rotations, boundary swap, 200 shuffles); **no generator repair is warranted so none is routed**; and the 72/234-vs-84/222 partition is settled against the artifact — **neither is correct, the true split is 90 testable / 216 statistic-free of 306 non-null (408 enumerated)**, both prior counts reproduced exactly by their `n_b` imputation rules, with W17's extra 12 slots shown to be ones its own loose test could not have validated; four runs all exit 0, nothing written to the repository.
