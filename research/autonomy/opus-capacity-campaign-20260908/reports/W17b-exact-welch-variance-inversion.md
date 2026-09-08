> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check done: three W17 reproductions all exit 0 with matching numbers, my exact test exits 0 on all 872 blocks, `git status --porcelain` shows only two *other* workers' collected reports and nothing of mine, and all execution was under `/tmp/claude-0/w17b/`. HEAD has moved to `103ff76f` since W17's frozen `92abbcb9`; my byte-identical reproduction of W17's Run 1 and Run 2 output is direct evidence `emc-expression-panels.json` is unchanged between them.

---

## Worker

**W17b**, lane 17 (refill) — exact variance-inversion successor to W17.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). I did not observe the served model; the coordinator must extract the actual per-child runtime model from the transcript. **No environment variable names a model.**

`date -u` at start: `Tue Sep  8 02:07:04 UTC 2026`; at end: `Tue Sep  8 02:11:14 UTC 2026`.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — model-relevant lines, verbatim (full output printed in the transcript; identical at start and end):

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
```

Repository HEAD at read time: **`103ff76f1d66426420c56a4d49752eb84f5f5c39`** (W17 read `92abbcb9…`; the coordinator has committed collected reports since). `git status --porcelain` shows only `?? …/reports/W02b-stromal-fraction-bound.md` and `?? …/reports/W06b-misclassification-sensitivity.md`, both other workers' collected files. **I created and modified no file under `/home/user/Rare-cancers` and ran no git write operation.**

---

## Question

**Do the within-group variances implied by each committed `welch_EMC_vs_comparator` block agree with the variances computed directly from that block's own `per_sample[].z_vs_array` rows?**

Open because W17 closed only the *loose* half. W17 checked that the committed `df` lies in the feasible interval `[min(n_a,n_b)−1, n_a+n_b−2]` and honestly measured that this catches a single-sample perturbation in only **~9–12%** of blocks: the interval is wide whenever the comparator arm is large. The committed tuple `(Δ, t, df, n_a, n_b)` **over-determines** the two within-group variances, so the same artifact supports an exact *point* test that W17 explicitly named as its successor. Nothing in the repository performs it.

---

## Prior-work check

Commands run and what they showed:

- `rg -n -i "implied variance|variance inversion|recover.*variance|v_a|welch system" --glob '!.git'` — **no hit is a variance inversion.** All hits are unrelated (`biorxiv_about`, `cov_at`, `surv_at`, a `plan.json` narrative).
- `rg -n -i "variance|sd_a|s2_a|invert" --glob '!.git' -l` (excluding this campaign dir) — 20+ files, all systems/manuscript prose or unrelated scripts; none inverts a Welch block.
- `rg -rn -i "welch|variance" research/autonomy/.../inputs/evidence-4878/ -l` — **zero hits.** The coordinator-verified 47-file capsule (`source_commit 4878b9b9d1c082cea46e636dad47be419f1fe021`, scope: "Exact47 changed files from committed writer revision") is entirely the **source-reuse program** — checkpoint history, terminal runs, preflight logs. No statistical overlap with this lane. I consulted it before claiming novelty; absence from it is UNKNOWN, not proof of absence.
- W17's own `rg` sweep for `satterthwaite` / `welch` / `degrees of freedom` is reproduced in its report and I did not need to repeat it.

**Closed items I confirmed I am not replaying** (`CLOSED-WORK.md`): no ASO/NAT submission, no Qeios history, no tissue-RNA paper, no frozen comment `7baf2727…`, no new review round on any paper, no rediscovery of `GSE4303`/`GSE28866` as new data (I read only already-committed derived fields), no invented cohort, no external retrieval, no denied-route replay. **Honest limit:** novelty evidence is a tree-wide `rg` plus the capsule; no hit is UNKNOWN, not proof.

---

## Method / inputs

**Inputs, read-only:** `research/modalities/emc-expression-panels.json` (13.2 MB, `gene_reads`, 958 gene×platform blocks), `research/modalities/emc-atr-vulnerability.json` (343 KB, part-B). **Tools:** `python3` 3.11.15, stdlib `json`/`math`/`sys` only. No network, no installs, no paid API, no GPU. cwd `/tmp/claude-0/w17b`.

### Derivation — written before coding

With $v_a=s_a^2/n_a$, $v_b=s_b^2/n_b$, $S=v_a+v_b$, $A=n_a-1$, $B=n_b-1$:

1. $t=\Delta/\sqrt S \;\Rightarrow\; S=(\Delta/t)^2$ — fixes the **scale** of the variance pair.
2. $\mathrm{df}=S^2/\big(v_a^2/A+v_b^2/B\big)$. Substituting $f=v_a/S$ cancels the scale:
$$\frac{f^2}{A}+\frac{(1-f)^2}{B}=\frac{1}{\mathrm{df}}$$
which is a **quadratic in $f$** — the *shape*:
$$f^2\Big(\tfrac1A+\tfrac1B\Big)-\tfrac{2f}{B}+\Big(\tfrac1B-\tfrac1{\mathrm{df}}\Big)=0,\qquad
f_\pm=\frac{\tfrac1B\pm\sqrt D}{\tfrac1A+\tfrac1B},\quad D=\frac{1/A+1/B}{\mathrm{df}}-\frac{1}{AB}.$$

$D\ge0 \iff \mathrm{df}\le A+B=n_a+n_b-2$ — **W17's upper feasibility edge falls out of this discriminant**, which is an independent confirmation that the two derivations describe the same object. $g(f)$ is convex with $g(0)=1/B$ (df $=B$), $g(1)=1/A$ (df $=A$), minimum at $f^\ast=A/(A+B)$ giving df $=A+B$ — W17's lower edge $\min(n_a,n_b)-1$ and its maximum, both recovered.

**Branch ambiguity, and how I handle it — not silently.** Both roots lie in $[0,1]$ **iff** $\mathrm{df}\ge\max(A,B)$; exactly one does when $\min(A,B)\le \mathrm{df}<\max(A,B)$. **227 of 872 blocks (26.0%) have two admissible roots.** I therefore do **not** pick a root for the pass/fail decision. The gate is the algebraically equivalent **forward** form — check observed $S$ against $(\Delta/t)^2$ (T1) and observed df against committed df (T2) — which is root-agnostic and exactly equivalent to "the observed $(v_a,v_b)$ satisfies both Welch equations". The inversion is reported *separately*, as an interval, with both roots and which one the data matches. Where I did report a nearest-root variance, the branch choice is stated, and the two blocks where it degenerates are dissected below.

### Tolerance — stated before running, propagated not assumed

The artifact prints `z_vs_array`, `mean_a`, `mean_b`, `delta_a_minus_b` to **4 dp** ($\delta_z=5\times10^{-5}$), `t` to **3 dp** ($\delta_t=5\times10^{-4}$), `df` to **1 dp** ($\delta_{df}=0.05$). Instead of a flat tolerance I propagate these into **intervals** and require intersection:

- rigorous worst case on the sample variance: $\;\delta(s^2)\le\big(2\delta_z\sum_i|z_i-\bar z| + n\delta_z^2\big)/(n-1)$, so $\delta v=\delta(s^2)/n$.
- **T1 (scale):** pass iff $[S_{obs}\pm\delta S_{obs}]$ intersects $\big[\big(\tfrac{|\Delta|-\delta_z}{|t|+\delta_t}\big)^2,\big(\tfrac{|\Delta|+\delta_z}{|t|-\delta_t}\big)^2\big]$.
- **T2 (shape):** pass iff the range of $\mathrm{df}(v_a,v_b)$ over the box $[v_a\pm\delta v_a]\times[v_b\pm\delta v_b]$ intersects $[\mathrm{df}_c\pm0.05]$.
- **T3 (means):** pass iff $|\bar z_{obs}-\text{mean}_c|\le 2\delta_z$.
- Sample variance is **ddof=1** (pre-stated); ddof=0 computed only as a diagnostic on any failure.
- **Ill-conditioning declared in advance:** T1 is *not evaluable* where $|t|\le10\delta_t=0.005$ (the implied scale diverges); the *inversion* is ill-conditioned where $D\to0$ (df at the feasibility ceiling — $df/d(\mathrm{df})\sim D^{-1/2}$) and ambiguous where $\mathrm{df}\ge\max(A,B)$. These are counted and reported; **none is used to excuse a failure.**

No criterion was changed after seeing any result.

---

## Result

| # | Finding | n | Uncertainty | Tier |
|---|---|---|---|---|
| **V0** | **W17 Run 1 reproduced byte-identically** from its committed code: 958 seen / 872 checked / 0 / 0 / 0, min edge distance 0.0000, PASS, exit 0. | 872 | exact | PRIMARY |
| **V0b** | **W17 Run 2 reproduced exactly on all eight numbers** (94/76/94/94/109 would-fail; 23 edge blocks; `[((10,6),18),((6,29),3),((10,5),1),((5,4),1)]`; same four named edge examples) from a reimplementation. | 872 | exact | PRIMARY |
| **V0c** | **W17 Run 3 reproduced on every substantive number** — pooled `n_samples_pooled` 36 = 36, `class_counts` element-wise exact, **0 violations**, same 306 total slots. My reimplementation partitions them **72 checked / 234 skipped** vs W17's **84/222**. | 306 slots | — | PRIMARY |
| **V1** | **T1 (scale): 0 violations / 872.** Observed $v_a+v_b$ from the per-sample rows agrees with $(\Delta/t)^2$ in every evaluable block. 2 blocks ill-conditioned ($\vert t\vert\le0.005$), T1 not evaluable there — UNKNOWN, not passed. | 872 | propagated interval | PRIMARY |
| **V2** | **T2 (shape/df): 0 violations / 872.** Observed df recomputed from the rows agrees with committed df. **Max $\vert \mathrm{df}_{obs}-\mathrm{df}_c\vert = 0.049877$** (NR4A2, GSE4303-GPL3290, n=(10,6), 13.9 vs 13.94988) — *just* inside the 0.05 print half-ulp, exactly what pure rounding predicts. | 872 | ±0.05 (df print precision) | PRIMARY |
| **V3** | **T3 (means): 0 violations / 872.** `mean_a`/`mean_b` reproduce the group means of `z_vs_array` to ≤2×5e-5. | 1744 means | 1e-4 | PRIMARY |
| **V4** | **Inversion, stated honestly as an interval: 872/872 observed $f=v_a/S$ lie inside the f-interval implied by $\mathrm{df}_c\pm0.05$. 0 outside, 0 unresolvable.** | 872 | — | PRIMARY |
| **V5** | **Conditioning of the inversion:** width of the implied f-interval — median **0.0064**, p90 **0.0102**, max **0.0420** (on $f\in[0,1]$). So df's single decimal pins the variance *split* to ~0.6% of the range typically, ~4% at worst. | 872 | — | PRIMARY |
| **V6** | **Branch ambiguity is real: 227/872 blocks (26.0%) admit two roots** ($\mathrm{df}\ge\max(n_a,n_b)-1$); **21/872 have $D<10^{-6}$** (df at the ceiling), where the inversion is ill-conditioned. Both are handled by the root-agnostic forward gate, not by picking. | 872 | — | PRIMARY |
| **V7** | **NEW DETECTION POWER, measured.** Would-fail fractions under one-unit perturbation: `n_EMC−1` **99.9%**, `n_EMC+1` **99.7%**, `n_comp−1` **95.4%**, `n_comp+1` **94.2%**, `df±1` **100.0%/100.0%**, `df−0.1` (1 ulp) **97.4%**, `df+0.1` **95.4%**, `Δ±0.001` **99.5%/99.7%**, `Δ±0.0001` (1 ulp) **19.4%/16.9%**. | 872 | — | PRIMARY |
| **V8** | **The upgrade is quantified:** on the identical perturbations W17 measured, detection rises from **8.7–12.5%** to **94.2–100%** — roughly a **9-fold** improvement, and `df±1` goes from 10.8/12.5% to **100%**. | 872 | — | PRIMARY |
| **V9** | Two blocks where the *nearest-root* variance degenerates (CXCL13 and CD274, GSE4303-GPL3290) are **not** violations — dissected below. | 2 | — | PRIMARY |
| **V10** | Whether the ATR artifact's 306 part-B concept slots also pass the exact test | — | not run (no `per_sample` rows in that artifact) | UNKNOWN |

### Outcome, stated plainly

**CONFIRMED. Zero violations across all 872 blocks on all three exact gates.** The within-group variances implied by each committed Welch block agree with the variances computed directly from that block's own per-sample rows, to the artifact's print precision, in every block. There is no discrepancy to report and **I have not manufactured one.**

This is a materially stronger statement than W17's. W17 established that no *systematic* n/df inconsistency exists, with only ~10% per-block sensitivity. This result establishes that **each individual block's committed $(\Delta, t, \mathrm{df})$ triple is a faithful summary of its own per-sample rows**, at 94–100% sensitivity to a one-unit corruption of any of $n_a$, $n_b$, $\mathrm{df}$, or $\Delta$. The 872 Welch contrasts underwriting `emc-surface-target-landscape.md` and the `n = 10` / `n = 6` sample sizes underwriting `emc-atr-vulnerability-assessment.md:565` are internally coherent end-to-end: rows → variances → $t$, df.

### V2 is the sharpest single number

Max deviation `0.049877` against a `0.05` half-ulp is the strongest evidence in this report. Had the generator used a different variance convention (ddof=0), a different grouping, or a stale row set, the deviation would be *orders* of magnitude larger, not 0.25% under the rounding bound. The test came within 0.000123 of its own limit and did not cross it — this is a tight pass, not a slack one.

### V9 — the two degenerate-root blocks, dissected rather than hidden

My first run reported "max relative $|v_a$ implied $-\,v_a$ observed$|$ = 1.000". That is an artifact of a **bad metric**, not a violation, and I checked it rather than reporting it:

- `CXCL13` / GSE4303-GPL3290, $n=(3,5)$, $\mathrm{df}_c=4.0$, $t=-2.653$, $\Delta=-2.8989$. Roots $f_\pm=\{0.0,\ 0.6667\}$, $D=0.0625$. Observed $f=0.002383$, $S_{obs}=1.1943171$, $S_{imp}=1.1939660$, $\mathrm{df}_{obs}=4.0191$ vs 4.0.
- `CD274` / GSE4303-GPL3290, $n=(5,3)$, $\mathrm{df}_c=4.0$, roots $\{0.3333,\ 1.0\}$. Observed $f=0.996535$, $\mathrm{df}_{obs}=4.0278$ vs 4.0.

In both, $\mathrm{df}_c$ lands exactly on $n_b-1$ (resp. $n_a-1$), whose root is the **boundary** $f=0$ (resp. $1$), i.e. implied $v_a=0$. The true $f=0.0024$ is genuinely tiny (one arm's variance is 400× the other) and **indistinguishable from 0 given df's single decimal**. Relative error against a zero denominator is 1.0 by construction. Both blocks pass T1 and T2 comfortably. This is why V4 reports the inversion as an **interval** rather than a point: the interval form is the honest one, and under it these two blocks are inside, like all 870 others.

### V0c — my one disagreement with W17, stated

W17 reported **84 checked / 222 skipped**; I get **72 / 234** of the same 306. The cause is bookkeeping, not arithmetic: the per-platform blocks carry **no `FET_comparator_classes` list** (only `cross_platform_pooled` does, and it is `[]`), so my reimplementation cannot determine $n_b$ for `contrast_EMC_vs_FET_comparators` / `_NONFET_` per-platform and skips them — 12 slots on GSE24369 that W17 evidently resolved by inheriting a class list. **This is a coverage difference between my reimplementation and W17's script (whose text was described but not included in its report), not a numeric disagreement.** Both runs agree on 306 total slots, on **0 violations**, and on the exact pooled parts-to-whole identity. Mine is the more conservative partition — it checks fewer and marks more UNKNOWN. I flag it because a discrepancy with W17 was named the most important possible finding, and this is the only one: it does not change any verdict.

### On the `Δ ± 1 ulp` row (16.9–19.4%)

I report this rather than quietly omitting it. One ulp of Δ is $10^{-4}$, which is *at* the artifact's representable precision — a perturbation smaller than what the file can express is necessarily near the floor of detectability, and 17–19% is what a correctly-calibrated test should give there. At $\Delta\pm0.001$ — still a change invisible in most prose — detection is **99.5%**. The honest headline is the 94.2–100% band for perturbations the artifact can actually represent.

---

## Validation evidence

### RUN

**Environment for all runs:** container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `python3 --version` → `Python 3.11.15`, cwd `/tmp/claude-0/w17b`, stdlib only, no network. Repository read at HEAD `103ff76f1d66426420c56a4d49752eb84f5f5c39`.

**Run 1** — `cd /tmp/claude-0/w17b && python3 w17_repro_1.py; echo "EXIT=$?"` (W17's own code, verbatim)
```
blocks seen              : 958
blocks with welch+n+df   : 872
(a) df-feasibility viol. : 0
(b) delta-identity viol. : 0
(c) n-vs-per_sample viol.: 0
min distance of a passing df to its nearest feasibility edge: 0.0000
VERDICT: PASS
EXIT=0
```

**Run 2** — `python3 w17_repro_2.py; echo "EXIT=$?"`
```
n_EMC-1  : would-fail 94/872 = 10.8%
n_EMC+1  : would-fail 76/872 = 8.7%
n_comp-1 : would-fail 94/872 = 10.8%
df+1     : would-fail 94/872 = 10.8%
df-1     : would-fail 109/872 = 12.5%
blocks sitting exactly on a feasibility edge: 23
[((10, 6), 18), ((6, 29), 3), ((10, 5), 1), ((5, 4), 1)]
  edge eg: ('AHSA1', 'GSE4303-GPL3290_series_matrix.txt.gz', 10, 6, 14.0)
  edge eg: ('BPNT1', 'GSE4303-GPL3290_series_matrix.txt.gz', 10, 6, 14.0)
  edge eg: ('CALR', 'GSE4303-GPL3290_series_matrix.txt.gz', 10, 6, 14.0)
  edge eg: ('CDK12', 'GSE4303-GPL3290_series_matrix.txt.gz', 10, 6, 14.0)
EXIT=0
```

**Run 3** — `python3 w17_repro_3.py; echo "EXIT=$?"`
```
pooled n_samples_pooled  : 36 | sum over GSE4303 platforms: 36
pooled class_counts      : {'unclassified': 9, 'MFH_UPS': 4, 'DFSP': 8, 'EMC': 10, 'GIST': 5}
sum of per-platform      : {'unclassified': 9, 'MFH_UPS': 4, 'DFSP': 8, 'EMC': 10, 'GIST': 5}
contrast blocks checked  : 72 | skipped (no df/n): 234
violations               : 0
VERDICT: PASS
EXIT=0
```

**Run 4 — the exact test** — `python3 welch_variance_inversion.py; echo "EXIT=$?"`
```
blocks seen                        : 958
blocks entering the exact test     : 872
  n-vs-rows mismatches (excluded)  : 0
  skipped, a group has n < 2       : 0
T1 scale   S_obs vs (delta/t)^2    : 0 violation(s)   [2 block(s) ill-conditioned, |t|<=0.005, T1 not evaluable]
T2 shape   df_obs vs committed df  : 0 violation(s)
T3 means   mean_obs vs committed   : 0 violation(s)
max |df_obs - df_committed| over all blocks : 0.049877  ('NR4A2', 'GSE4303-GPL3290_series_matrix.txt.gz', 10, 6, 13.9, 13.94987735339006)
max relative |v_a implied - v_a observed|   : 1.000e+00  ('CXCL13', 'GSE4303-GPL3290_series_matrix.txt.gz', 0.002846084444444443, 0.0)
max relative |v_b implied - v_b observed|   : 1.000e+00  ('CD274', 'GSE4303-GPL3290_series_matrix.txt.gz', 0.0019121744444444463, 0.0)
blocks with TWO admissible inversion roots  : 227 (df >= max(n_a,n_b)-1)
blocks with near-zero discriminant (D<1e-6) : 21 (inversion ill-conditioned)
VERDICT: PASS
EXIT=0
```

**Run 5 — inversion interval + detection power** — `python3 inversion_power.py; echo "EXIT=$?"`
```
blocks in the inversion report              : 872  (unresolvable: 0)
observed f = v_a/S inside the df-implied f-interval : 872/872
  outside : 0
width of the f-interval (conditioning of the inversion):
  median 0.0064 | p90 0.0102 | max 0.0420
  (f in [0,1]; a width near 1 means df's 1 dp barely constrains the variance split)

unperturbed: gate passes 872/872
  n_EMC -1                : would-fail 871/872 = 99.9%
  n_EMC +1                : would-fail 869/872 = 99.7%
  n_comp -1               : would-fail 832/872 = 95.4%
  n_comp +1               : would-fail 821/872 = 94.2%
  df -1                   : would-fail 872/872 = 100.0%
  df +1                   : would-fail 872/872 = 100.0%
  df -0.1 (1 ulp)         : would-fail 849/872 = 97.4%
  df +0.1 (1 ulp)         : would-fail 832/872 = 95.4%
  delta -0.0001 (1 ulp)   : would-fail 169/872 = 19.4%
  delta +0.0001 (1 ulp)   : would-fail 147/872 = 16.9%
  delta -0.001            : would-fail 868/872 = 99.5%
  delta +0.001            : would-fail 869/872 = 99.7%
EXIT=0
```
*(The first execution of Run 5 reported `851/872 inside, 0 outside` with 21 unresolvable — those 21 are the feasibility-ceiling blocks where $\mathrm{df}_c+0.05$ exceeds $n_a+n_b-2$ and the root formula returns nothing. Clamping the upper end to the ceiling $A+B$ resolves all 21. This is a **fix to my reporting of an interval endpoint, not a loosening of a criterion**: `outside` was 0 both before and after, and the T1/T2/T3 gate in Run 4 was untouched.)*

**Run 6 — write-isolation check** — `git status --porcelain && git rev-parse HEAD`
```
?? research/autonomy/opus-capacity-campaign-20260908/reports/W02b-stromal-fraction-bound.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W06b-misclassification-sensitivity.md
103ff76f1d66426420c56a4d49752eb84f5f5c39
```
Both untracked files are other workers' coordinator-collected reports. Nothing of mine.

**Code — `/tmp/claude-0/w17b/welch_variance_inversion.py`** (returned inline; nothing written into the repository):

```python
"""W17b: EXACT variance-inversion check of emc-expression-panels.json.

Do the within-group variances IMPLIED by each committed Welch block agree with the
variances computed directly from that block's own per-sample rows?

DERIVATION (written before coding).
  v_a = s_a^2/n_a, v_b = s_b^2/n_b, S = v_a+v_b, A = n_a-1, B = n_b-1.
  (i)  t = Delta/sqrt(S)                      =>  S = (Delta/t)^2
  (ii) df = S^2/(v_a^2/A + v_b^2/B).  With f = v_a/S this is scale-free:
           f^2/A + (1-f)^2/B = 1/df
       i.e.  f^2 (1/A+1/B) - 2f/B + (1/B - 1/df) = 0, a QUADRATIC in f, with
           f_pm = [1/B +- sqrt(D)] / (1/A+1/B),   D = (1/A+1/B)/df - 1/(A*B).
       D >= 0  <=>  df <= A+B = n_a+n_b-2   (W17's upper feasibility edge falls out).
       g(f) is convex with g(0)=1/B (df=B), g(1)=1/A (df=A), minimum at f*=A/(A+B)
       giving df=A+B.  Hence BOTH roots lie in [0,1] iff df >= max(A,B); exactly ONE
       does when min(A,B) <= df < max(A,B).  The branch ambiguity is REAL and is NOT
       silently resolved here: the pass/fail test below is the algebraically equivalent
       FORWARD form (T1 on S, T2 on df), which is root-agnostic, and the inversion is
       reported separately with both roots and which one the data matches.

TOLERANCE (stated before running; propagated from the artifact's print precision,
not assumed):  z_vs_array / mean_a / mean_b / delta to 4 dp -> dz = 5e-5
               t to 3 dp -> dt = 5e-4 ;  df to 1 dp -> ddf = 0.05
  d(s^2) <= (2*dz*sum|z_i - zbar| + n*dz^2)/(n-1)   [rigorous worst case]
  T1 passes iff [S_obs +- dS_obs] intersects [S_imp_lo, S_imp_hi]
  T2 passes iff [df_obs over the v-box corners] intersects [df_c +- 0.05]
  T3 passes iff |mean_obs - mean_c| <= 2*dz
Sample variance is ddof=1 (pre-stated). ddof=0 is computed only as a diagnostic.
"""
import json, math, sys

PATH = "/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
DZ, DT, DDF = 5e-5, 5e-4, 0.05
ILL_T_FACTOR = 10.0          # |t| <= 10*DT  => T1 vacuous (ill-conditioned)

def var(xs, ddof=1):
    n = len(xs); m = sum(xs)/n
    return sum((x-m)**2 for x in xs)/(n-ddof), m

def dvar(xs):
    n = len(xs); m = sum(xs)/n
    return (2*DZ*sum(abs(x-m) for x in xs) + n*DZ*DZ)/(n-1)

def df_of(va, vb, A, B):
    S = va+vb
    return S*S/(va*va/A + vb*vb/B)

def roots_f(A, B, df):
    P = 1.0/A + 1.0/B
    D = P/df - 1.0/(A*B)
    if D < 0: return None, D
    r = math.sqrt(D)
    return sorted(((1.0/B - r)/P, (1.0/B + r)/P)), D

d = json.load(open(PATH))
gr = d["gene_reads"]

seen = checked = 0
f_t1 = []; f_t2 = []; f_t3 = []; f_n = []
ill_t = 0; two_root = 0; near_edge = 0; skipped_small = 0
worst_va = (0.0, None); worst_vb = (0.0, None); worst_df = (0.0, None)
ddof0_would_pass = 0

for gene, plats in gr.items():
    for plat, b in plats.items():
        if not isinstance(b, dict): continue
        seen += 1
        w = b.get("welch_EMC_vs_comparator")
        if not isinstance(w, dict): continue
        na, nb = b.get("n_EMC_with_a_value"), b.get("n_comparator_with_a_value")
        df_c, t_c = w.get("df"), w.get("t")
        dl_c, ma_c, mb_c = w.get("delta_a_minus_b"), w.get("mean_a"), w.get("mean_b")
        ps = b.get("per_sample")
        if None in (na, nb, df_c, t_c, dl_c) or not isinstance(ps, list): continue
        za = [r["z_vs_array"] for r in ps
              if r.get("class") == "EMC" and isinstance(r.get("z_vs_array"), (int, float))]
        zb = [r["z_vs_array"] for r in ps
              if r.get("class") != "EMC" and isinstance(r.get("z_vs_array"), (int, float))]
        if (len(za), len(zb)) != (na, nb):
            f_n.append((gene, plat, na, nb, len(za), len(zb))); continue
        if na < 2 or nb < 2: skipped_small += 1; continue
        checked += 1
        A, B = na-1, nb-1

        s2a, mza = var(za); s2b, mzb = var(zb)
        va, vb = s2a/na, s2b/nb
        dva, dvb = dvar(za)/na, dvar(zb)/nb
        S_obs = va + vb; dS = dva + dvb

        # ---- T1: scale ----
        at = abs(t_c); ad = abs(dl_c)
        if at <= ILL_T_FACTOR*DT:
            ill_t += 1; t1_ok = None; S_lo = S_hi = float('nan')
        else:
            S_hi = ((ad+DZ)/(at-DT))**2
            S_lo = (max(ad-DZ, 0.0)/(at+DT))**2
            t1_ok = not (S_obs+dS < S_lo or S_obs-dS > S_hi)
            if not t1_ok:
                gap = S_lo-(S_obs+dS) if S_obs+dS < S_lo else (S_obs-dS)-S_hi
                f_t1.append((gene, plat, na, nb, t_c, dl_c, S_obs, dS, S_lo, S_hi, gap))

        # ---- T2: shape (df) ----
        corners = [df_of(va+sa*dva, vb+sb*dvb, A, B) for sa in (-1, 1) for sb in (-1, 1)]
        dfl, dfh = min(corners), max(corners)
        t2_ok = not (dfh < df_c-DDF or dfl > df_c+DDF)
        if not t2_ok:
            gap = (df_c-DDF)-dfh if dfh < df_c-DDF else dfl-(df_c+DDF)
            f_t2.append((gene, plat, na, nb, df_c, df_of(va, vb, A, B), dfl, dfh, gap))
            s2a0, _ = var(za, 0); s2b0, _ = var(zb, 0)
            if abs(df_of(s2a0/na, s2b0/nb, A, B) - df_c) <= DDF: ddof0_would_pass += 1
        e = abs(df_of(va, vb, A, B) - df_c)
        if e > worst_df[0]: worst_df = (e, (gene, plat, na, nb, df_c, df_of(va, vb, A, B)))

        # ---- T3: means ----
        if ma_c is not None and abs(mza-ma_c) > 2*DZ: f_t3.append((gene, plat, 'a', mza, ma_c))
        if mb_c is not None and abs(mzb-mb_c) > 2*DZ: f_t3.append((gene, plat, 'b', mzb, mb_c))

        # ---- inversion: implied v_a, v_b vs observed (reported, not the gate) ----
        rr, D = roots_f(A, B, df_c)
        if rr is not None:
            adm = [f for f in rr if -1e-9 <= f <= 1+1e-9]
            if len(adm) == 2 and abs(adm[0]-adm[1]) > 1e-9: two_root += 1
            if D < 1e-6: near_edge += 1
            if t1_ok and adm:
                S_i = (dl_c/t_c)**2
                f_obs = va/S_obs
                fbest = min(adm, key=lambda f: abs(f-f_obs))
                via, vib = fbest*S_i, (1-fbest)*S_i
                ra = abs(via-va)/va if va > 0 else 0.0
                rb = abs(vib-vb)/vb if vb > 0 else 0.0
                if ra > worst_va[0]: worst_va = (ra, (gene, plat, va, via))
                if rb > worst_vb[0]: worst_vb = (rb, (gene, plat, vb, vib))

print(f"blocks seen                        : {seen}")
print(f"blocks entering the exact test     : {checked}")
print(f"  n-vs-rows mismatches (excluded)  : {len(f_n)}")
print(f"  skipped, a group has n < 2       : {skipped_small}")
print(f"T1 scale   S_obs vs (delta/t)^2    : {len(f_t1)} violation(s)"
      f"   [{ill_t} block(s) ill-conditioned, |t|<={ILL_T_FACTOR*DT}, T1 not evaluable]")
print(f"T2 shape   df_obs vs committed df  : {len(f_t2)} violation(s)")
print(f"T3 means   mean_obs vs committed   : {len(f_t3)} violation(s)")
if f_t2: print(f"  of the T2 violations, ddof=0 would have passed: {ddof0_would_pass}")
for nm, v in (("T1", f_t1), ("T2", f_t2), ("T3", f_t3), ("N", f_n)):
    for row in v[:25]: print(f"  VIOL-{nm}", row)
    if len(v) > 25: print(f"  ... and {len(v)-25} more VIOL-{nm}")
print(f"max |df_obs - df_committed| over all blocks : {worst_df[0]:.6f}  {worst_df[1]}")
print(f"max relative |v_a implied - v_a observed|   : {worst_va[0]:.3e}  {worst_va[1]}")
print(f"max relative |v_b implied - v_b observed|   : {worst_vb[0]:.3e}  {worst_vb[1]}")
print(f"blocks with TWO admissible inversion roots  : {two_root} (df >= max(n_a,n_b)-1)")
print(f"blocks with near-zero discriminant (D<1e-6) : {near_edge} (inversion ill-conditioned)")
fail = bool(f_t1 or f_t2 or f_t3 or f_n)
print("VERDICT:", "FAIL" if fail else "PASS")
sys.exit(1 if fail else 0)
```

**Code — `/tmp/claude-0/w17b/inversion_power.py`** (final version, as run in Run 5):

```python
"""W17b part 2: (i) report the inversion as an INTERVAL (the honest form, given df has
1 dp), (ii) measure the detection power of the exact test under one-unit perturbations.

(i) The df equation determines f = v_a/S only to the precision df carries. The set of f
    consistent with df in [df_c-0.05, df_c+0.05] is a union of at most two intervals
    (one per branch). We report whether the OBSERVED f lies in it, and how wide the
    implied v_a interval is -- that width IS the conditioning of the inversion.

(ii) Power: perturb the committed n_EMC, n_comparator, df, delta by one unit and count
     blocks whose combined gate (T1 and T2) then fails. The n-vs-rows precondition is
     DISABLED for this measurement, otherwise an n perturbation would be caught trivially
     by W17's exact row-count test (test C) rather than by the inversion under study.
"""
import json, math, sys
PATH = "/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
DZ, DT, DDF = 5e-5, 5e-4, 0.05
ILL = 10.0*DT

def var(xs):
    n=len(xs); m=sum(xs)/n; return sum((x-m)**2 for x in xs)/(n-1), m
def dvar(xs):
    n=len(xs); m=sum(xs)/n
    return (2*DZ*sum(abs(x-m) for x in xs) + n*DZ*DZ)/(n-1)
def df_of(va,vb,A,B):
    S=va+vb; return S*S/(va*va/A+vb*vb/B)
def froots(A,B,df):
    P=1/A+1/B; D=P/df-1/(A*B)
    if D<0: return None
    r=math.sqrt(D); return sorted(((1/B-r)/P,(1/B+r)/P))

blocks=[]
d=json.load(open(PATH))
for g,plats in d["gene_reads"].items():
    for p,b in plats.items():
        if not isinstance(b,dict): continue
        w=b.get("welch_EMC_vs_comparator")
        if not isinstance(w,dict): continue
        na,nb=b.get("n_EMC_with_a_value"),b.get("n_comparator_with_a_value")
        ps=b.get("per_sample")
        if None in (na,nb,w.get("df"),w.get("t"),w.get("delta_a_minus_b")) or not isinstance(ps,list):
            continue
        num=lambda r: isinstance(r.get("z_vs_array"),(int,float))
        za=[r["z_vs_array"] for r in ps if r.get("class")=="EMC" and num(r)]
        zb=[r["z_vs_array"] for r in ps if r.get("class")!="EMC" and num(r)]
        if len(za)<2 or len(zb)<2: continue
        s2a,_=var(za); s2b,_=var(zb)
        blocks.append((g,p,na,nb,w["df"],w["t"],w["delta_a_minus_b"],
                       s2a,s2b,dvar(za),dvar(zb)))
N=len(blocks)

def gate(bk, na=None, nb=None, df=None, dl=None):
    g,p,NA,NB,DF,T,DL,s2a,s2b,d2a,d2b = bk
    na = NA if na is None else na; nb = NB if nb is None else nb
    df = DF if df is None else df;  dl = DL if dl is None else dl
    if na<2 or nb<2: return False
    A,B=na-1,nb-1
    va,vb=s2a/na,s2b/nb; dva,dvb=d2a/na,d2b/nb
    S=va+vb; dS=dva+dvb
    at=abs(T); ad=abs(dl)
    if at>ILL:
        S_hi=((ad+DZ)/(at-DT))**2; S_lo=(max(ad-DZ,0.0)/(at+DT))**2
        if S+dS<S_lo or S-dS>S_hi: return False
    corners=[df_of(va+sa*dva,vb+sb*dvb,A,B) for sa in(-1,1) for sb in(-1,1)]
    if max(corners)<df-DDF or min(corners)>df+DDF: return False
    return True

# --- (i) inversion as an interval -----------------------------------------
inside=0; outside=[]; widths=[]; unres=0
for bk in blocks:
    g,p,na,nb,df,t,dl,s2a,s2b,_,_=bk
    A,B=na-1,nb-1
    va,vb=s2a/na,s2b/nb; f_obs=va/(va+vb)
    segs=[]
    for lo,hi in ((max(df-DDF,1e-9),min(df+DDF,float(A+B))),):
        rl=froots(A,B,hi); rh=froots(A,B,lo)      # larger df -> roots closer together
        if rl is None or rh is None: continue
        segs=[(rh[0],rl[0]),(rl[1],rh[1])]
    if not segs: unres+=1; continue
    segs=[(max(a,0.0),min(b,1.0)) for a,b in segs if b>=0.0 and a<=1.0]
    ok=any(a-1e-9<=f_obs<=b+1e-9 for a,b in segs)
    inside+= ok
    if not ok: outside.append((g,p,na,nb,df,f_obs,segs))
    w=min(b-a for a,b in segs if a-1e-9<=f_obs<=b+1e-9) if ok else float('nan')
    if ok: widths.append(w)
widths.sort()
print(f"blocks in the inversion report              : {len(blocks)}  (unresolvable: {unres})")
print(f"observed f = v_a/S inside the df-implied f-interval : {inside}/{len(blocks)}")
print(f"  outside : {len(outside)}")
for o in outside[:10]: print("   OUT", o)
print(f"width of the f-interval (conditioning of the inversion):")
print(f"  median {widths[len(widths)//2]:.4f} | p90 {widths[int(.9*len(widths))]:.4f} | max {widths[-1]:.4f}")
print(f"  (f in [0,1]; a width near 1 means df's 1 dp barely constrains the variance split)")

# --- (ii) detection power --------------------------------------------------
base_ok=sum(1 for bk in blocks if gate(bk))
print(f"\nunperturbed: gate passes {base_ok}/{N}")
tests=[("n_EMC -1",  dict(na=-1)), ("n_EMC +1",  dict(na=+1)),
       ("n_comp -1", dict(nb=-1)), ("n_comp +1", dict(nb=+1)),
       ("df -1",     dict(df=-1.0)), ("df +1",   dict(df=+1.0)),
       ("df -0.1 (1 ulp)", dict(df=-0.1)), ("df +0.1 (1 ulp)", dict(df=+0.1)),
       ("delta -0.0001 (1 ulp)", dict(dl=-1e-4)), ("delta +0.0001 (1 ulp)", dict(dl=+1e-4)),
       ("delta -0.001", dict(dl=-1e-3)), ("delta +0.001", dict(dl=+1e-3))]
for label,kw in tests:
    bad=0
    for bk in blocks:
        a=dict(na=bk[2]+kw.get('na',0), nb=bk[3]+kw.get('nb',0),
               df=bk[4]+kw.get('df',0.0), dl=bk[6]+kw.get('dl',0.0))
        if not gate(bk,**a): bad+=1
    print(f"  {label:24s}: would-fail {bad}/{N} = {100*bad/N:.1f}%")
```

`w17_repro_1.py` is W17's committed code verbatim; `w17_repro_2.py` and `w17_repro_3.py` are my reimplementations from W17's described method and are in the transcript's tool calls.

### PROPOSED (NOT RUN)

- Promoting `welch_variance_inversion.py` into `research/modalities/tests/` as a behavioural test. **Not run and deliberately not authored into the tree** — write isolation forbids it, and adding a test tier is not mine to decide.
- Extending the exact test to `emc-atr-vulnerability.json`'s 306 part-B slots (V10). **Not run:** that artifact carries `scores` / `proliferation_adjusted_scores` but no per-concept `per_sample` rows in the shape the inversion needs; whether the score arrays can be regrouped to reconstruct them is unverified.
- No paid API, no GPU, no network, no external source attempted. **No content-policy refusal was encountered in this lane.**

---

## Limitations

1. **This validates bookkeeping, not biology.** Agreement between committed statistics and their own per-sample rows says nothing about whether samples are correctly classified as EMC, whether probes map to the right genes, whether the two-colour GSE4303 reference-channel collinearity biases the contrast, or whether any address is therapeutically relevant. There is no wet lab. **Nothing here establishes EMC efficacy, safety, selectivity, therapeutic window, or clinical readiness. No clinical claim is made.**
2. **A closed loop is not a correct loop.** The test proves the committed $(\Delta,t,\mathrm{df})$ are a faithful reduction of the committed `per_sample` rows. If those rows are themselves wrong — mis-parsed from the series matrix, mis-normalised, mis-labelled — every gate here still passes. This check cannot see upstream of the artifact.
3. **Below print precision is invisible.** df carries 1 dp, $t$ 3 dp, $z$/means 4 dp. A defect smaller than that is undetectable in principle, which is exactly why the `Δ ± 1 ulp` row sits at 17–19% rather than ~100%.
4. **2 blocks are ill-conditioned for T1** ($|t|\le0.005$): the implied scale $(\Delta/t)^2$ diverges and T1 is *not evaluable*. Those two are UNKNOWN on T1, not passed. They still pass T2 and T3.
5. **The inversion proper is ambiguous or unstable on a substantial minority:** 227/872 have two admissible roots, 21/872 sit at the discriminant floor. The pass/fail gate is root-agnostic and unaffected, but any *point* estimate of $v_a$ from the inversion alone is not trustworthy on those blocks — which is why V4/V5 report intervals.
6. **V0c is an unreconciled coverage difference with W17** (72/234 vs 84/222 of 306 ATR slots). Verdicts agree; the partition does not. Mine is the conservative side.
7. **V10 is UNKNOWN**, not passed: the ATR artifact's part-B slots got the loose test only.
8. **Novelty evidence is a tree-wide `rg` plus the evidence-4878 capsule.** No hit is UNKNOWN, not proof of absence.
9. **Denominator gap inherited from W17:** `n_comparator` pools heterogeneous sarcoma histologies differing between series; no arithmetic identity can address comparator-mixture transfer.
10. **The MDE range itself remains uninstrumented.** `PUB-ATR.json p1s[0]` — that "0.045–0.186 SD units" is carried by no artifact field and produced by no code — is untouched by this work. I strengthened the *n* half of the power sentence, not the effect-size half.

---

## Stop condition

**Set:** an executed exact variance-inversion check across all blocks, with a tolerance stated before running, a measured detection power, and an honest verdict.

**MET.** The derivation was written before the code; the branch ambiguity was identified analytically and handled by a root-agnostic forward gate rather than a silent choice; the tolerance was propagated from the artifact's actual print precision as intervals and fixed before any run; six runs executed, all exit 0; **all 872 blocks pass all three gates with zero violations**, max df deviation 0.049877 against a 0.05 rounding bound; detection power measured at **94.2–100%** against W17's 8.7–12.5%. No criterion was weakened after seeing results. **No violation exists to report, and I did not manufacture one.**

---

## Tool-call and wall-clock count actually used

**14 tool calls** (target ~40). **Wall clock 02:07:04Z → 02:11:14Z ≈ 4 minutes of tool time**, roughly 12 minutes including derivation and drafting (target ~40 minutes). Returned as soon as the stop condition was met; no padding.

---

## Next concrete action

**One successor, specific:** the same exact test cannot currently reach `emc-atr-vulnerability.json`, whose 306 part-B concept slots have only the loose interval treatment and where **234 of 306 are UNKNOWN** under my conservative partition. The successor is to determine whether that artifact's `scores` / `proliferation_adjusted_scores` arrays can be regrouped by `class_counts` into the per-sample vectors the inversion needs — and if they can, run T1/T2/T3 over all 306 slots, which would extend point-level verification to the concept blocks that actually carry PUB-ATR's headline. If they cannot, the honest finding is that the ATR artifact does not persist enough to verify itself, and the smallest correct repair is to have its generator emit per-sample rows as `emc-expression-panels.json` already does. Either outcome is a durable result. Read-only under `/tmp`, returning a table.

A secondary, smaller item: reconcile the V0c partition difference by recovering W17's `atr_df_identity.py` from its transcript and diffing the $n_b$ imputation rule for FET/NONFET contrasts.

result: Converted W17's loose Welch df-interval test into an exact variance-inversion point test and ran it over all 872 committed Welch blocks in `emc-expression-panels.json` — derivation written before coding (the quadratic's discriminant independently reproduces W17's feasibility edges), branch ambiguity handled by a root-agnostic forward gate rather than a silent root choice, tolerance propagated as intervals from the artifact's own print precision, W17's three headline runs reproduced first (Runs 1 and 2 byte-identical; Run 3 agrees on 306 slots and 0 violations but partitions 72/234 vs 84/222, an unreconciled coverage difference I report rather than smooth over) — **zero violations on all three gates across all 872 blocks, max df deviation 0.049877 against a 0.05 rounding bound, and detection power measured at 94.2–100% versus W17's 8.7–12.5%; CONFIRMED**, six runs all exit 0, nothing written to the repository.
