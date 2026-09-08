> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Start `date -u`: `Tue Sep  8 02:49:05 UTC 2026`. End `date -u`: `Tue Sep  8 02:58:29 UTC 2026`. HEAD at read time `3f5fc95d806765b8fddf4fbe1dc288c85869fa2d`, HEAD at end `ce743d6ac63c6645ea65121c7a2157b54b0a2ad8` (coordinator commits during my run; the two artifacts I gated were read once each at the start of their run). `git status --porcelain` was **empty at start and empty at end** — I wrote nothing into the tree. All execution under `/tmp/claude-0/w17h/`.

---

## Worker

**W17h**, lane 17 refill, OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). I did not observe the served model; no environment variable names a model. The coordinator must extract the actual per-child runtime model from the transcript.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — model-relevant lines, verbatim, identical at start and end (full output printed in the transcript):

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
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
```

Note: the COMMON-BRIEF names a frozen read commit `92abbcb9…`; this checkout was already at `3f5fc95d…` when I started and at `ce743d6a…` when I finished. I recorded both rather than asserting the brief's value.

---

## Question

**How much of the repository's committed inferential statistics is self-verifiable against its own rows, how much of that is currently unverified, and is the campaign's shared premise — that zero of it is gate-reachable — actually true?**

Open because W17b, W17d and W17f each verified one artifact by hand and each closed with the same *asserted* claim: no repository gate reaches any of it. None of them measured the denominator (how many committed statistical blocks exist), and none of them tested the "zero gates" claim against the whole test corpus — they searched only for the two artifact names they were working on.

---

## Prior-work check

Commands run against the live checkout (`/home/user/Rare-cancers`), plus the three prior reports read in full:

- `git grep -c '"welch_EMC_vs_comparator"' -- research/` → `emc-expression-panels.json:1001`, **`nr4a3-fusion-targets.json:145`**, plus generator/test/report hits. **The second artifact with the identical schema was never named by W17b, W17d or W17f.**
- `git grep -o -h -i -E '"[a-z_0-9]*(t_stat|statistic|_df|df_|welch|mannwhitney|chi2|fisher|dof|degrees)[a-z_0-9]*"' -- 'research/*.json' | sort | uniq -c` → surfaced seven further Welch families never mentioned in this campaign: `welch_raw_ln_ic50`, `welch_line_median_corrected`, `welch_FETsarcoma_vs_matched`, `welch_FETall_vs_OLD_comparator`, `welch_re_derived_here`, `welch_committed`, `welch_joint_z`.
- `git grep -n -E 'statistics\.(p|)variance|statistics\.stdev|sum\(\(.*-.*\)\*\*2|welch|satterthwaite|degrees_of_freedom' -- research/modalities/tests/ research/manuscripts/tests/ scripts/tests/ research/autonomy/tests/ systems/tests/` → **14 hits, and one of them falsifies the campaign's premise** (see Result R3). W17f ran the equivalent search restricted to two artifact names and therefore could not have seen it.
- `CLOSED-WORK.md` read in full. I am not replaying: any ASO/NAT or Qeios item, the frozen comment `7baf2727…`, the blocked NR4A Perspective, the user-rejected registry paper, lane 11's source-index (W11b sole owner), or any denied external route. I opened **no** review round on any paper, edited **no** manuscript or hardening-state file, ran **no** network call, and did **not** run `scripts/preflight.sh`.
- I re-ran W17b's own script only where I needed its algebra (I read `/tmp/claude-0/w17b/welch_variance_inversion.py` and preserved its derivation and tolerance discipline); I did **not** re-run its 872-block census, per the dispatch.

Honest limit on novelty: `rg`/`git grep` over the live tree only. I did not consult the frozen corpus this run; absence there would in any case be UNKNOWN, not proof.

---

## Method / inputs

**Inputs, read-only, live checkout:**
`research/modalities/nr4a3-fusion-targets.json`, `emc-mtap-locus-persample.json`, `emc-expression-panels.json`, `emc-expression-panels-inputs.json`, `aso-delivery-antigen.json`, `aso_delivery_antigen.py`, `research/modalities/tests/test_aso_delivery_antigen.py`, `scripts/tier_budget.py`, plus all 1,525 tracked `research/**/*.json` for the census. Prior work: `reports/W17b-…`, `W17d-…`, `W17f-…` and `/tmp/claude-0/w17b/welch_variance_inversion.py`.

**Tools:** system `python3` 3.11.15 (stdlib `json`/`math`/`re`/`ast`/`collections` only, no pytest) and the uv tool venv `/root/.local/share/uv/tools/pytest/bin/python` with pytest 9.1.1 for the module run. No network, no installs, no paid API, no GPU. Execution root `/tmp/claude-0/w17h/`, with read-only symlinks at `/tmp/claude-0/w17h/research/modalities/` so the shipping `__file__`-relative path resolution is exercised verbatim. Nothing was copied into or out of the repository.

**Census definition, stated before running.** A dict node counts as a *statistical block* if it carries a numeric test statistic (`t`, `u`, `z`, `observed_t`, `statistic`, …) together with either a numeric `df`/`dof` (**strict**) or any numeric `n*` (**loose**). Row-carrying is measured separately as the presence of a non-empty `per_sample` / `values` / `scores` / `rows` list. Classification into *self-verifiable* / *external-input* / *not verifiable* is then a structural fact about the file, not a judgement.

**Gate form, unchanged from W17b and deliberately so.** T1 (scale): observed `v_a+v_b` against `(Δ/t)²`. T2 (df): observed Welch–Satterthwaite df against committed df, over the interval box induced by the row-precision error. T3 (means): committed `mean_a`/`mean_b` against observed group means. Sample variance `ddof=1` (pre-stated; `ddof=0` only as a failure diagnostic). Rigorous worst-case variance error `d(s²) ≤ (2·dz·Σ|zᵢ−z̄| + n·dz²)/(n−1)`.

**Tolerances propagated, not chosen.** For each artifact I measured the printed precision of each field *from the artifact's own serialised text* (max decimals observed across all literals of that field inside that welch family) and used its half-ulp:

| artifact | family | `t` | `df` | `delta` | `mean` | rows |
|---|---|---|---|---|---|---|
| `nr4a3-fusion-targets.json` | `welch_EMC_vs_comparator` | 3 dp → 5e-4 | 1 dp → 0.05 | 4 dp → 5e-5 | 4 dp → 5e-5 | `z_vs_array` 4 dp → 5e-5 |
| `emc-mtap-locus-persample.json` | `welch_re_derived_here` | **4 dp → 5e-5** | 1 dp → 0.05 | 4 dp → 5e-5 | 4 dp → 5e-5 | 4 dp → 5e-5 |

I first implemented tolerance from each *literal's own* decimals and it mis-fired: `t = -3.0` (a 3-dp value that happens to be round) got a half-ulp of 0.5, which made `|t| ≤ 10·dt` and wrongly declared one block ill-conditioned. **Field-level printed precision is the correct propagation and per-literal repr is not**; I record the wrong version because it changed a reported number (1 spurious UNKNOWN → 0).

**No root is ever picked.** The df inversion `f = v_a/S` is a quadratic with discriminant `D = (1/A+1/B)/df − 1/(A·B)`; both roots are admissible whenever `df ≥ max(n_a,n_b)−1`. Every pass/fail decision uses only the root-agnostic forward form; ambiguity is *counted*, never resolved.

---

## Result

### R1 — Census: what exists, and what could ever be checked against its own rows

Repository-wide over all 1,525 tracked `research/**/*.json` (`census2.py`, exit 0):

- **2,607 strict statistical blocks** (statistic + df) in **11 files**.
- **11,534 loose statistical blocks** (statistic + df or n) in 18 files.

Per artifact (blocks ≥ 3; `strict` = statistic + df):

| Artifact | strict | loose | row lists in file | Verifiability class | Tier |
|---|---|---|---|---|---|
| `emc-expression-panels.json` | 1556 | 5855 | 889 | **872 welch blocks SELF-VERIFIABLE** (own `per_sample`); the other ~684 t+df blocks are panel/read-level scores (`reads/read_8_SURFACE_ANTIGEN` 226, `read_7_RET` 38, `panels/*` …) whose per-block rows are **not** carried → external-input or in-file reconstruction, **UNKNOWN, not gated here** | PRIMARY |
| `emc-expression-panels-inputs.json` | 0 | 4299 | 4319 | `genome_wide_null` t + rank, **no df**; the reference distribution is over all array symbols, not carried → **verifiable only with an external input**: the class-assignment rule in `emc_expression_panels.py` *and* the full series matrix. `samples[]` carries `annotation_verbatim` but **no `class` field** | PRIMARY |
| `emc-tissue-read-statistics.json` | 354 | 354 | **0** | t + df + `n_emc`/`n_comparator`, **no rows at all in file** → external input: the GEO series matrices | PRIMARY |
| `emc-hypoxia-confounds.json` | 245 | 269 | 0 | same → external input | PRIMARY |
| `emc-atr-vulnerability.json` | 105 | 225 | 3 | **90 slots self-verifiable by in-file reconstruction** (W17d/W17f: exhaustive unique recovery of the comparator subset); rest external | SECONDARY (W17d/W17f) |
| **`nr4a3-fusion-targets.json`** | **173** | 173 | 146 | **142 `gene_reads` welch blocks SELF-VERIFIABLE** (own `per_sample.z_vs_array`) + **7 `controls.checks` blocks self-verifiable by in-file cross-block join** (PLAGL1/ENO3/SGK1/NR4A3 are all present in `gene_reads`); **22 `set_scores` + 2 `platforms` blocks carry no per-sample score rows** → reconstruction candidate via `set_definitions` + the aggregation rule, **not gated here, UNKNOWN** | PRIMARY |
| `atm-status-atri-stratification.json` | 0 | 63 | 0 | Mann–Whitney `u`,`z` + `n_null`/`n_intact`, **no per-line rows** → external input: the DepMap/PRISM per-cell-line values | PRIMARY |
| `census-route-expression-grading.json` | 56 | 56 | 0 | external input | PRIMARY |
| `nr4a3-fusion-targets-confounds.json` | 53 | 53 | 0 | external input | PRIMARY |
| `emc-prmt5-multiplicity.json` | 0 | 38 | 0 | permutation-null t, no df, no rows → external | PRIMARY |
| `emc-prmt5-route-controls.json` | 0 | 31 | 0 | external | PRIMARY |
| `emc-proteostasis-read.json` | 0 | 28 | 0 | external | PRIMARY |
| `aso-delivery-antigen.json` | 21 | 21 | 0 | rows live in `emc-expression-panels.json` → **verifiable only with an external input (that artifact)** — and this is the one path that *is* gated, see R3 | PRIMARY |
| `fet-ddr-axis-scan.json` | 20 | 20 | 0 | `welch_raw_ln_ic50` / `welch_line_median_corrected` on drug-response lines → external input: DepMap/PRISM per-line IC50s | PRIMARY |
| `emc-ret-target-scan.json` | 19 | 19 | 0 | external input | PRIMARY |
| `emc-prmt5-effect-sizes.json` | 0 | 16 | 0 | external input | PRIMARY |
| **`emc-mtap-locus-persample.json`** | **5** | 5 | 5 | **SELF-VERIFIABLE** (`welch_re_derived_here` + own `per_sample`) | PRIMARY |
| `atr-part-d-proliferation-control.json` | 0 | 5 | 0 | correlation t + n, no rows → external | PRIMARY |

**Headline coverage arithmetic (strict blocks, statistic + df):**

| | blocks | share of 2,607 | Tier |
|---|---|---|---|
| Self-verifiable, rows carried per block | **1,026** (872 panels + 142 nr4a3 gene_reads + 7 nr4a3 controls + 5 mtap) | 39.4 % | PRIMARY |
| Self-verifiable only by in-file reconstruction (join/subset recovery) | 90 ATR part-B slots verified by W17d/W17f; **~684 panels + 24 nr4a3 candidates NOT assessed** | UNKNOWN | UNKNOWN |
| Verifiable only with an external input (GEO series matrices, DepMap/PRISM, a class-assignment rule) | ~800 (`emc-tissue-read-statistics` 354, `emc-hypoxia-confounds` 245, `census-route-expression-grading` 56, `nr4a3-…-confounds` 53, `aso` 21, `fet-ddr` 20, `emc-ret` 19, plus the loose families) | — | PRIMARY |
| Not verifiable at all from committed material | none identified — every block I examined has *some* named recovery path | — | PRIMARY |

### R2 — Gate applied to the two self-verifiable artifacts nobody had covered

`pytest` run, **8 passed in 0.05 s, exit 0**, and a standalone census run, exit 0:

| Artifact | blocks gated | T1 scale | T2 df | T3 means | n-vs-rows | UNKNOWN (\|t\|≤10·dt) | worst \|df_obs−df_c\| vs half-ulp | two distinct roots | Tier |
|---|---|---|---|---|---|---|---|---|---|
| `nr4a3-fusion-targets.json` `gene_reads` | **142** | **0** | **0** | **0** | **0** | **0** | **0.049662 / 0.05 = 0.9932** (COX5A, GSE24369, n=(6,29), df 7.2 vs 7.150338) | **36 / 142 = 25.4 %** (+4 with `D<1e-6`, degenerate not ambiguous) | PRIMARY |
| `nr4a3-fusion-targets.json` `controls.checks` (cross-block join) | **7** | **0** | **0** | n/a | **0** | **0** | 0.049312 (ENO3, GSE4303-GPL3290) | **0** | PRIMARY |
| `emc-mtap-locus-persample.json` `welch_re_derived_here` | **5** | **0** | **0** | **0** | **0** | **0** | **0.049492 / 0.05 = 0.9898** (CDKN2B, GSE24369, df 8.4 vs 8.350508) | **2 / 5** | PRIMARY |
| **Total new** | **154** | **0** | **0** | **0** | **0** | **0** | — | **38** | PRIMARY |

**Outcome: 154 additional committed Welch blocks verified, 0 violations, 0 slots excluded as ill-conditioned.** Combined with W17b/W17d/W17f's 962, **1,116 committed statistical blocks are now point-verified against their own rows and 0 violations have been found anywhere.**

The two worst df deviations (0.9932 and 0.9898 of the print half-ulp) are the sharpest numbers here: both land just inside the rounding bound, which is what a faithful `ddof=1` Welch computed on exactly these rows must produce and what a different variance convention or a stale row set could not.

**Root ambiguity is real in the new artifacts.** 36/142 nr4a3 blocks and 2/5 mtap blocks admit **two distinct** admissible roots; 4 further nr4a3 blocks sit at `D < 1e-6` (a degenerate double root, ill-conditioned rather than ambiguous — I initially counted these as ambiguous and the module's own guard test caught the error at `assert 40 == 36`, which is why the distinctness condition is now explicit in the code). No root was picked anywhere.

**A row basis was recovered, not assumed.** `emc-mtap-locus-persample.json` nowhere states which per-sample field its Welch was computed on. I gated **both** candidates: `z_vs_array` is clean on all three tests; `array_percentile` fails **5/5 T1, 4/5 T2 and 10/10 T3** with a worst df deviation of **108.6 half-ulps**. The recovery is therefore unique and evidenced, and the module asserts `admissible == ["z_vs_array"]` so that zero candidates reads UNKNOWN and two reads AMBIGUOUS rather than either being silently resolved. As a bonus consistency check, all 5 `welch_committed` values agree with their `welch_re_derived_here` counterparts within the 3-dp half-ulp.

One block that looked like an n-vs-rows violation — `gene_reads/PLAGL1/GSE4303-GPL3290`, `n_EMC_with_a_value = 8` against 10 rows with `class == "EMC"` — is **not** one: two of those rows carry `value: null, z_vs_array: null` (samples GSM98496, GSM98499 had no value for the probe). I dissected it rather than reporting it.

### R3 — The campaign's shared premise is FALSE, and this is the most important finding here

W17b, W17d and W17f each state that no repository gate reaches any committed Welch verification. **One does.**

`research/modalities/tests/test_aso_delivery_antigen.py::test_the_committed_welch_statistics_still_agree_with_the_committed_per_sample_values` asserts `res["controls"]["artifact_self_consistency_recomputed_welch_t"]["n_disagreements"] == 0`, and its `res` fixture is `M.derive()` — it **re-runs the generator**, which at `aso_delivery_antigen.py:366–387` re-derives the Welch `t` from `emc-expression-panels.json`'s committed `per_sample[].z_vs_array` for every antigen it scores. This is a genuine, gate-reachable, artifact-against-its-own-rows check, and it is not a self-attested field being read back.

Its **measured** scope, however, is narrow:

| Property | ASO gate (existing) | W17b/W17f/W17h gate | Tier |
|---|---|---|---|
| Panel blocks reached | **21 of 872 = 2.4 %** (12 antigens × 2 platforms, readable) | 872 | PRIMARY |
| Statistic checked | `t` only | `t` (via T1 on `v_a+v_b`), **df**, means, n-vs-rows | PRIMARY |
| Tolerance | flat **0.02**, chosen | half-ulp of the field's own printed precision (**5e-4** on t) — **40× tighter** | PRIMARY |
| Ill-conditioning | not declared | `\|t\| ≤ 10·dt` ⇒ UNKNOWN, capped | PRIMARY |
| Other 2,586 strict blocks repo-wide | not reached | — | PRIMARY |

I also checked whether the ASO gate is *vacuous* because it defines the comparator arm differently (it excludes `class == "unclassified"`, where the panels artifact's `n_comparator_with_a_value` does not): for these 21 blocks there are **no `unclassified` rows at all**, the two arm definitions coincide, and the worst recomputed-vs-committed `t` deviation is **0.00049**, inside the 3-dp half-ulp. So the gate is real but narrow — not vacuous, and not a substitute.

**Corrected answer to the campaign's question: gate-reachable coverage of committed statistical blocks today is 21 / 2,607 = 0.81 %, not 0 %.** The corollary the three prior reports were reaching for still stands, sharpened: **99.2 % of the repository's committed inferential statistics is not reachable by any gate**, and the one gate that exists checks a single statistic at a tolerance 40× looser than the artifact's own precision.

### R4 — Cost of covering the rest, by `tier_budget.py`'s own AST method

`python3 scripts/tier_budget.py` — independent reproduction of W17f's figures, exit 0:

```
   ok    commit-loop             1466/1500  test function(s) in 102 file(s)
   ok    modalities              7247/7500  test function(s) in 436 file(s)
   ok    paper-guards             966/1000  test function(s) in 111 file(s)
```

`tier_budget`'s AST counter applied to my module: **8 test functions, 0 shadowed**.

| | test functions | modalities tier | Tier |
|---|---|---|---|
| today | — | 7247 / 7500 (headroom 253) | PRIMARY |
| + W17f's module (872 + 90 blocks) | +8 | 7255 / 7500 | SECONDARY (W17f) |
| + this module (154 blocks) | **+8** | **7263 / 7500** | PRIMARY (count measured; the tier effect is arithmetic) |
| combined single module, all 1,116 self-verifiable blocks | **16** | 7263 / 7500, **6.3 % of the tier's headroom** | PRIMARY / PREDICTION |

**Sixteen test functions would cover every block in this repository that is self-verifiable against rows it already carries** — 1,116 of them, 42.8 % of the 2,607 strict statistical blocks, at 0.05–0.26 s of runtime. The remaining ~1,490 strict blocks cannot be closed by any module: they need an external input (a GEO series matrix, DepMap/PRISM per-line values, or a class-assignment rule), and no test-count budget buys that.

### The module, returned inline (authored nowhere in the tree)

Placement, if the coordinator lands it: `research/modalities/tests/test_committed_welch_blocks_in_the_uncovered_artifacts.py`. It is read-only, stdlib-only, imports no generator, and takes 0.05 s.

```python
"""W17h — read-only forward-form Welch gate for the two SELF-VERIFIABLE artifacts that
W17b/W17d/W17f do not cover:

  * `nr4a3-fusion-targets.json` — 142 `gene_reads[gene][platform].welch_EMC_vs_comparator`
    blocks plus 7 `controls.checks[*].per_platform[*]` blocks, each checkable against
    `gene_reads[...].per_sample[].z_vs_array` carried in the SAME file.
  * `emc-mtap-locus-persample.json` — 5 `welch_re_derived_here` blocks with their own
    `per_sample` rows.

Form is W17b's, unchanged and deliberately so:
  T1 (scale)  observed v_a+v_b  vs  (delta/t)^2
  T2 (df)     observed Welch–Satterthwaite df  vs  committed df
  T3 (means)  committed mean_a / mean_b  vs  observed group means

⛔ NO ROOT IS EVER PICKED. Inverting df for the variance SPLIT is a quadratic whose
discriminant is D = (1/A+1/B)/df − 1/(A·B); BOTH roots are admissible whenever
df ≥ max(n_a,n_b)−1. The gate is the algebraically equivalent forward form, which is
root-agnostic. `test_the_root_ambiguity_is_real_and_stays_measured` MEASURES the
ambiguity so that a later "simplification" into an inversion cannot happen quietly.

Tolerances are the artifact's OWN printed precision, measured from its serialised text
(max decimals per field within each welch family), never a flat epsilon chosen here.
Sample variance is ddof=1. |t| ≤ 10·dt ⇒ T1 NOT EVALUABLE ⇒ UNKNOWN, never a pass, and
the count of such slots is capped so the exclusion cannot silently grow.
"""
import json
import math
import os
import re

import pytest

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NR4A3 = os.path.join(MOD, "nr4a3-fusion-targets.json")
MTAP = os.path.join(MOD, "emc-mtap-locus-persample.json")

DZ = 5e-5  # per-sample z / array_percentile are printed to 4 dp in both artifacts


def _field_dp(path, family, field):
    """Printed precision of `field` inside `family` blocks, MEASURED from the file."""
    txt = open(path, encoding="utf-8").read()
    dp = []
    for blk in re.findall(r'"%s"\s*:\s*\{[^}]*\}' % re.escape(family), txt):
        m = re.search(r'"%s"\s*:\s*(-?\d+(?:\.(\d+))?)' % re.escape(field), blk)
        if m:
            dp.append(len(m.group(2)) if m.group(2) else 0)
    assert dp, (path, family, field)
    return max(dp)


def _var(xs, ddof=1):
    n = len(xs)
    m = sum(xs) / n
    return sum((x - m) ** 2 for x in xs) / (n - ddof), m


def _dvar(xs):
    n = len(xs)
    m = sum(xs) / n
    return (2 * DZ * sum(abs(x - m) for x in xs) + n * DZ * DZ) / (n - 1)


def _df_of(va, vb, A, B):
    S = va + vb
    return S * S / (va * va / A + vb * vb / B)


def _gate(za, zb, t_c, dl_c, df_c, dt, ddl, ddf):
    """Return (t1, t2, df_dev, two_roots) with t1 None when NOT EVALUABLE."""
    na, nb = len(za), len(zb)
    A, B = na - 1, nb - 1
    s2a, _ = _var(za)
    s2b, _ = _var(zb)
    va, vb = s2a / na, s2b / nb
    dva, dvb = _dvar(za) / na, _dvar(zb) / nb
    S_obs, dS = va + vb, dva + dvb
    at, ad = abs(t_c), abs(dl_c)
    if at <= 10 * dt:
        t1 = None
    else:
        S_hi = ((ad + ddl) / (at - dt)) ** 2
        S_lo = (max(ad - ddl, 0.0) / (at + dt)) ** 2
        t1 = not (S_obs + dS < S_lo or S_obs - dS > S_hi)
    corners = [_df_of(va + sa * dva, vb + sb * dvb, A, B) for sa in (-1, 1) for sb in (-1, 1)]
    t2 = not (max(corners) < df_c - ddf or min(corners) > df_c + ddf)
    P = 1.0 / A + 1.0 / B
    D = P / df_c - 1.0 / (A * B)
    two = False
    if D >= 0:
        r = math.sqrt(D)
        f1, f2 = (1 / B - r) / P, (1 / B + r) / P
        # DISTINCT admissible roots only: a degenerate double root (D -> 0, df at the
        # feasibility ceiling) is ill-conditioned, not ambiguous, and is counted apart.
        two = all(-1e-9 <= f <= 1 + 1e-9 for f in (f1, f2)) and abs(f1 - f2) > 1e-9
    return t1, t2, abs(_df_of(va, vb, A, B) - df_c), two


@pytest.fixture(scope="module")
def nr():
    return json.load(open(NR4A3, encoding="utf-8"))


@pytest.fixture(scope="module")
def mt():
    return json.load(open(MTAP, encoding="utf-8"))


def _nr_blocks(d):
    for gene, plats in d["gene_reads"].items():
        for plat, b in plats.items():
            w = b.get("welch_EMC_vs_comparator") if isinstance(b, dict) else None
            if not isinstance(w, dict) or not isinstance(b.get("per_sample"), list):
                continue
            za = [r["z_vs_array"] for r in b["per_sample"]
                  if r.get("class") == "EMC" and isinstance(r.get("z_vs_array"), (int, float))]
            zb = [r["z_vs_array"] for r in b["per_sample"]
                  if r.get("class") != "EMC" and isinstance(r.get("z_vs_array"), (int, float))]
            yield gene, plat, b, w, za, zb


def test_every_nr4a3_gene_read_carries_the_rows_its_own_n_claims(nr):
    bad = [(g, p, b["n_EMC_with_a_value"], b["n_comparator_with_a_value"], len(za), len(zb))
           for g, p, b, w, za, zb in _nr_blocks(nr)
           if (b["n_EMC_with_a_value"], b["n_comparator_with_a_value"]) != (len(za), len(zb))]
    assert bad == []


def test_nr4a3_gene_read_welch_blocks_agree_with_their_own_per_sample_rows(nr):
    dt = 0.5 * 10 ** -_field_dp(NR4A3, "welch_EMC_vs_comparator", "t")
    ddl = 0.5 * 10 ** -_field_dp(NR4A3, "welch_EMC_vs_comparator", "delta_a_minus_b")
    ddf = 0.5 * 10 ** -_field_dp(NR4A3, "welch_EMC_vs_comparator", "df")
    dme = 0.5 * 10 ** -_field_dp(NR4A3, "welch_EMC_vs_comparator", "mean_a")
    t1_bad, t2_bad, t3_bad, unknown, n = [], [], [], [], 0
    for g, p, b, w, za, zb in _nr_blocks(nr):
        if min(len(za), len(zb)) < 2:
            continue
        n += 1
        t1, t2, dev, _ = _gate(za, zb, w["t"], w["delta_a_minus_b"], w["df"], dt, ddl, ddf)
        if t1 is None:
            unknown.append((g, p))
        elif not t1:
            t1_bad.append((g, p))
        if not t2:
            t2_bad.append((g, p, w["df"], dev))
        if abs(sum(za) / len(za) - w["mean_a"]) > 2 * dme:
            t3_bad.append((g, p, "mean_a"))
        if abs(sum(zb) / len(zb) - w["mean_b"]) > 2 * dme:
            t3_bad.append((g, p, "mean_b"))
    assert n == 142
    assert (t1_bad, t2_bad, t3_bad) == ([], [], [])
    assert len(unknown) <= 2, unknown  # NOT passes: |t| <= 10*dt, T1 not evaluable


def test_nr4a3_control_blocks_agree_with_the_gene_read_rows_they_cite(nr):
    dt, ddl, ddf = 5e-4, 5e-5, 0.05
    gr = nr["gene_reads"]
    seen, bad = 0, []
    for name, ck in nr["controls"]["checks"].items():
        gene = name.split("_")[-1]
        for plat, b in (ck.get("per_platform") or {}).items():
            if not (isinstance(b.get("t"), (int, float)) and isinstance(b.get("df"), (int, float))):
                continue
            rec = (gr.get(gene) or {}).get(plat)
            assert rec and isinstance(rec.get("per_sample"), list), (gene, plat)
            za = [r["z_vs_array"] for r in rec["per_sample"]
                  if r.get("class") == "EMC" and isinstance(r.get("z_vs_array"), (int, float))]
            zb = [r["z_vs_array"] for r in rec["per_sample"]
                  if r.get("class") != "EMC" and isinstance(r.get("z_vs_array"), (int, float))]
            assert (len(za), len(zb)) == (b["n_EMC_with_a_value"], b["n_comparator_with_a_value"])
            seen += 1
            t1, t2, dev, _ = _gate(za, zb, b["t"], b["delta"], b["df"], dt, ddl, ddf)
            if t1 is False or not t2:
                bad.append((name, plat, t1, t2, dev))
    assert seen == 7
    assert bad == []


def test_the_mtap_row_basis_is_recovered_uniquely_and_not_assumed(mt):
    """The artifact does not declare WHICH per-sample field its Welch was computed on.
    Exactly one of the two candidate fields may reproduce every committed mean."""
    dme = 0.5 * 10 ** -_field_dp(MTAP, "welch_re_derived_here", "mean_EMC")
    admissible = []
    for field in ("z_vs_array", "array_percentile"):
        ok = True
        for pv in mt["per_platform"].values():
            for b in pv["locus_genes"].values():
                w = b.get("welch_re_derived_here")
                if not isinstance(w, dict):
                    continue
                xa = [r[field] for r in b["per_sample"] if r.get("class") == "EMC"]
                xb = [r[field] for r in b["per_sample"] if r.get("class") != "EMC"]
                ok &= abs(sum(xa) / len(xa) - w["mean_EMC"]) <= 2 * dme
                ok &= abs(sum(xb) / len(xb) - w["mean_comparator"]) <= 2 * dme
        if ok:
            admissible.append(field)
    assert admissible == ["z_vs_array"]  # unique: 0 would be UNKNOWN, 2 would be AMBIGUOUS


def test_mtap_welch_blocks_agree_with_their_own_per_sample_rows(mt):
    dt = 0.5 * 10 ** -_field_dp(MTAP, "welch_re_derived_here", "t")
    ddl = 0.5 * 10 ** -_field_dp(MTAP, "welch_re_derived_here", "delta_EMC_minus_comparator")
    ddf = 0.5 * 10 ** -_field_dp(MTAP, "welch_re_derived_here", "df")
    n, bad, unknown = 0, [], []
    for plat, pv in mt["per_platform"].items():
        for gene, b in pv["locus_genes"].items():
            w = b.get("welch_re_derived_here")
            if not isinstance(w, dict):
                continue
            za = [r["z_vs_array"] for r in b["per_sample"] if r.get("class") == "EMC"]
            zb = [r["z_vs_array"] for r in b["per_sample"] if r.get("class") != "EMC"]
            assert (len(za), len(zb)) == (pv["n_EMC"], pv["n_comparator"]), (plat, gene)
            n += 1
            t1, t2, dev, _ = _gate(za, zb, w["t"], w["delta_EMC_minus_comparator"], w["df"],
                                   dt, ddl, ddf)
            if t1 is None:
                unknown.append((plat, gene))
            elif not t1 or not t2:
                bad.append((plat, gene, t1, t2, dev))
    assert n == 5
    assert bad == []
    assert len(unknown) <= 1, unknown


def test_the_mtap_committed_and_re_derived_welch_agree_with_each_other(mt):
    bad = []
    for plat, pv in mt["per_platform"].items():
        for gene, b in pv["locus_genes"].items():
            c, r = b.get("welch_committed"), b.get("welch_re_derived_here")
            if not (isinstance(c, dict) and isinstance(r, dict)):
                continue
            if abs(c["t"] - r["t"]) > 0.5e-3 or abs(c["delta_a_minus_b"]
                                                    - r["delta_EMC_minus_comparator"]) > 1e-9:
                bad.append((plat, gene, c, r))
    assert bad == []


def test_the_root_ambiguity_is_real_and_stays_measured(nr, mt):
    """Guards the ⛔ above: if this ever reads 0, the forward form is no longer needed and
    somebody may be tempted to 'simplify' the gate into a root-picking inversion."""
    two = sum(1 for g, p, b, w, za, zb in _nr_blocks(nr)
              if min(len(za), len(zb)) >= 2
              and _gate(za, zb, w["t"], w["delta_a_minus_b"], w["df"], 5e-4, 5e-5, 0.05)[3])
    assert two == 36
    two_mt = 0
    for pv in mt["per_platform"].values():
        for b in pv["locus_genes"].values():
            w = b.get("welch_re_derived_here")
            if not isinstance(w, dict):
                continue
            za = [r["z_vs_array"] for r in b["per_sample"] if r.get("class") == "EMC"]
            zb = [r["z_vs_array"] for r in b["per_sample"] if r.get("class") != "EMC"]
            two_mt += _gate(za, zb, w["t"], w["delta_EMC_minus_comparator"], w["df"],
                            5e-5, 5e-5, 0.05)[3]
    assert two_mt == 2


def test_the_gate_is_not_vacuous(nr):
    """A perturbation the artifact can represent must turn the gate red."""
    dt, ddl, ddf = 5e-4, 5e-5, 0.05
    caught_delta = caught_df = total = 0
    for g, p, b, w, za, zb in _nr_blocks(nr):
        if min(len(za), len(zb)) < 2:
            continue
        total += 1
        t1, _, _, _ = _gate(za, zb, w["t"], w["delta_a_minus_b"] + 0.001, w["df"], dt, ddl, ddf)
        caught_delta += (t1 is False)
        _, t2, _, _ = _gate(za, zb, w["t"], w["delta_a_minus_b"], w["df"] + 1.0, dt, ddl, ddf)
        caught_df += (not t2)
    assert total == 142
    assert caught_delta / total >= 0.90
    assert caught_df == total
```

---

## Validation evidence

### RUN

**Environment for every run:** container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, cwd `/tmp/claude-0/w17h`, no network, no installs.

**Run 1 — the pytest module** (uv tool venv, since the system `python3` has no pytest)

```
$ cd /tmp/claude-0/w17h && /root/.local/share/uv/tools/pytest/bin/python -m pytest \
    research/modalities/tests/test_committed_welch_blocks_in_the_uncovered_artifacts.py -q
........                                                                 [100%]
8 passed in 0.05s
EXIT=0
```

Its **previous** run is preserved rather than hidden: `1 failed, 7 passed in 0.07s`, `EXIT=1`, `test_the_root_ambiguity_is_real_and_stays_measured … assert 40 == 36`. The module's own guard caught my conflation of a degenerate double root with a genuinely ambiguous pair; the fix is the `abs(f1 - f2) > 1e-9` condition now in the code, not a relaxed assertion.

**Run 2 — standalone census gate** (`python3 gate2` under `python3` 3.11.15), exit 0, verbatim key output:

```
nr4a3 welch field precision (dp): {'t': 3, 'df': 1, 'delta_a_minus_b': 4, 'mean_a': 4, 'mean_b': 4}
mtap  welch field precision (dp): {'t': 4, 'df': 1, 'delta_EMC_minus_comparator': 4, ...}
--- A  nr4a3-fusion-targets.json (field-precision tolerances)
  blocks entering the exact gate    : 142
  n-vs-rows mismatch (excluded)     : 0 []
  T1 scale  violations              : 0
  T2 df     violations              : 0
  T3 means  violations              : 0
  UNKNOWN (|t|<=10*dt, T1 not eval) : 0 []
  TWO admissible inversion roots    : 36  (ambiguity is real here)
  near-zero discriminant D<1e-6     : 4
  worst |df_obs-df_c|/half-ulp      : 0.9932  (COX5A, GSE24369, df 7.2, dev 0.049662, ulp 0.05)
--- B  emc-mtap-locus-persample.json  basis=z_vs_array
  blocks entering the exact gate    : 5 | T1 0 | T2 0 | T3 0 | UNKNOWN 0 | two-root 2
  worst |df_obs-df_c|/half-ulp      : 0.9898  (CDKN2B, df 8.4, dev 0.049492)
--- B  emc-mtap-locus-persample.json  basis=array_percentile
  T1 5 violations | T2 4 violations | T3 10 violations | worst dev/ulp 108.5748
committed-vs-rederived disagreements: 0
```

**Run 3 — nr4a3 control cross-block join**, exit 0: 6 blocks gated PASS/PASS with df deviations 0.0135–0.0495, `violations: 0`; the 7th (PLAGL1/GSE4303-GPL3290) was excluded by that ad-hoc script's coarser null filter and is gated cleanly by the module (`assert seen == 7` passes).

**Run 4 — repository-wide census** (`census2.py`), exit 0: `TOTAL strict t+df : 2607`, `TOTAL t+(df or n) : 11534`, `files with >=1 strict block: 11`; per-file table reproduced in R1.

**Run 5 — ASO gate coverage**, exit 0: `per_antigen antigens: 12`, `panel blocks actually reached by the ASO gate: 21`, `as a fraction of the 872 W17b blocks: 2.4%`; arm-definition check `blocks where ASO arm != all-non-EMC arm: 0`, `worst |t_ASO_recomputed - t_committed|: 0.00049 (CD248, GPL6244)`.

**Run 6 — tier budget**, `python3 scripts/tier_budget.py`, exit 0: `commit-loop 1466/1500`, `modalities 7247/7500`, `paper-guards 966/1000`. AST count of my module via `tier_budget._shadowed` and its own walk: `test functions = 8`, `shadowed = []`.

### PROPOSED (NOT RUN)

- Gating the ~684 panel-level and 24 nr4a3 `set_scores`/`platforms` t+df blocks by in-file reconstruction (W17d-style unique-subset recovery from `signature_sets` / `set_definitions` + the aggregation rule). I did not attempt it and make no claim about whether the recovery is unique.
- `scripts/preflight.sh` (dispatch forbids it) and any `PREFLIGHT_FULL` run.
- Landing the module in the tree and re-running `tier_budget.py --check`. **The 7263/7500 figure is arithmetic, not an observation.**

---

## Limitations

1. **A closed verification loop is not a correct one.** These 154 new blocks are faithful summaries *of their own rows*. A mis-parsed series matrix, a wrong probe→symbol map or a mis-assigned `class` label would leave every arm self-consistent and every test green. Nothing here is a clinical, efficacy, safety or selectivity claim; there is no wet lab and no new data.
2. **The census is a structural heuristic, not a semantic one.** "Statistic + df" counts a dict node; some of the 2,607 are the *same* contrast serialised at two levels (e.g. nr4a3's control blocks restate a `gene_reads` block), so the strict total is an upper bound on distinct inferences. I did not de-duplicate, and I say so rather than quoting the number as a count of independent tests.
3. **JSON only.** The census covers `research/**/*.json`. Statistics embedded in Markdown manuscripts, in `systems/`, or in `.py` literals are not counted; their coverage is **UNKNOWN**.
4. **The "verifiable only with an external input" class is named, not tested.** I did not fetch or open any GEO series matrix or DepMap file, so I cannot say those ~800 blocks *would* verify — only that a named input exists for each.
5. **The 684 panel-level and 24 nr4a3 aggregate blocks are UNKNOWN**, not "not verifiable": I did not attempt the reconstruction that would decide it.
6. **The ASO gate finding depends on `M.derive()` actually recomputing at test time.** I read the fixture and the generator source and confirmed the loop, but I did **not** execute `test_aso_delivery_antigen.py` (it would import and run a generator, which is outside a read-only remit). Its status is PRIMARY-by-source-reading, and one degree weaker than a run.
7. **A per-literal tolerance would have been wrong.** My first implementation produced one spurious UNKNOWN. Field-level printed precision is a *lower bound* on the true serialisation format; if a generator ever printed a field with fewer decimals than its format allows, my tolerance would be tighter than the rounding actually applied.
8. **HEAD moved under me** (`3f5fc95d` → `ce743d6a`) because the coordinator was committing collected reports. I did not re-read the two artifacts after the move; a change to them mid-run would not have been detected.
9. **Novelty evidence is `rg`/`git grep` over the live tree only.** Absence is UNKNOWN, not proof.
10. **W11c and W17f are measuring the same tier.** My 7247/7500 agrees with W17f's; I did not coordinate, and a discrepancy with anyone else is a finding, not something to reconcile away.

---

## Stop condition

**Set up front:** (i) a repository-wide census of statistical blocks with a per-artifact verifiability class; (ii) the forward-form gate actually executed with a real exit code on every self-verifiable artifact not already covered, with ill-conditioned slots reported as UNKNOWN and the worst df deviation stated against its print half-ulp; (iii) the gate-reachability claim tested rather than assumed; (iv) the covering-module cost measured by `tier_budget.py`'s own AST method.

**MET, all four.** (i) 2,607 strict blocks over 11 files, classified. (ii) `8 passed in 0.05s`, exit 0 — **154 new blocks, 0 violations, 0 ill-conditioned, worst df deviation 0.9932 half-ulps**; the mtap row basis recovered uniquely with the rejected alternative failing at 108.6 half-ulps. (iii) **The premise was false**: one gate exists, reaching 21/2,607 = 0.81 %; measured, not assumed. (iv) 8 test functions, 0 shadowed; 16 for a combined module; modalities 7247 → 7263/7500.

**No ceiling raised, no budget file changed, no test added to any tier, no manuscript or hardening-state file touched, no review round opened, `preflight.sh` not run, nothing written into the working tree** (`git status --porcelain` empty at start and end).

---

## Tool-call and wall-clock count actually used

**44 tool calls.** Wall clock **02:49:05Z → 02:58:29Z = 9 min 24 s.** Both inside the ~40/~40 target; I returned as soon as the stop condition was met.

---

## Next concrete action

**One task, for whoever owns integration:** land W17f's module *and* this one together at `research/modalities/tests/`, then run `python3 scripts/tier_budget.py --check` and confirm `modalities 7263/7500`, exit 0. That single commit takes gate-reachable coverage of committed statistics from **21 blocks (0.81 %) to 1,137 blocks (43.6 %)** and turns both reports' arithmetic into an observation.

Two follow-ups, explicitly **not** bundled: (a) tighten `aso_delivery_antigen.py`'s existing self-consistency control from a flat `0.02` on `t` to the artifact's own half-ulp and add the df check — it is the one place in the repository where a real gate is 40× looser than the data it reads, and it is a two-line generator change with a pinned-figure blast radius somebody must price; (b) decide the ~684 panel-level and 24 nr4a3 aggregate blocks by attempting the W17d-style unique-subset recovery — that is the only remaining path to raise coverage without an external input, and it is a genuinely open question, not arithmetic.
