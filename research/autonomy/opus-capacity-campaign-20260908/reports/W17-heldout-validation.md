> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check done: the identity I used is exactly necessary and sufficient (I derived the feasible df set analytically before coding it), both scripts ran to completion with exit 0, and `git status` confirms I created nothing under `/home/user/Rare-cancers` — all execution was in `/tmp/claude-0/w17/`.

---

## Worker

**W17**, lane 17 — validation of an unresolved claim in an active EMC analysis against held-out/orthogonal evidence.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). I did not observe the served model; the coordinator must extract the actual per-child runtime model from the transcript. No environment variable names a model.

`date -u` at start: `Tue Sep  8 01:56:08 UTC 2026`
`date -u` at end: `Tue Sep  8 02:00:07 UTC 2026`

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start; full output was long — the model-relevant lines, verbatim, and the same lines re-printed at end were identical):

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
```

**No string matching `model` appears anywhere in the environment.** Repository HEAD at read time: `92abbcb905cacf07f14b238db50d1b98f6590374` (the campaign's frozen read commit). `git status --porcelain` shows only `?? research/autonomy/opus-capacity-campaign-20260908/`, which is the coordinator's pre-existing untracked campaign directory — **I created and modified no file under `/home/user/Rare-cancers`**, and ran no git write operation.

---

## Question

**Are the group sizes that the active EMC expression analyses report — the `n_EMC` / `n_comparator` that every Welch contrast, every percentile read and the manuscripts' power statement rest on — consistent with the Welch–Satterthwaite degrees of freedom those same analyses independently emit?**

This is open because the two quantities are produced by different code paths and neither is fitted to the other, yet they are jointly constrained by an exact mathematical identity that nothing in the repository checks. The reported `n` is a *count of samples*; the reported `df` is a *function of the two within-group variances and the two n's*. A miscount, a misassigned class label, or a silently dropped sample would change the `n` field without changing the `df` emitted by the test that actually ran — so the identity is a real detector, not a tautology.

The concrete downstream claim this underwrites, with file and line:

> `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md:565`
> "⚠ **Part B's nulls are at n = 10 and n = 6 EMC tumours.** The minimum detectable effect is computed as SE = |Δ|/|*t*| from the committed contrast blocks, at 80 % power and two-sided α 0.05, against the fixed 0.2 elevated cut."

and, repeated as the paper's bounded headline at `:831`:

> "**no proliferation-adjusted DDR concept exceeds the 0.2 elevated cut on either series, with ≥80 % power to have seen one down to 0.045–0.186 SD units**"

Its **stated derivation** is `SE = |Δ|/|t|` from the committed contrast blocks — which never touches the sample sizes at all. So `n = 10` and `n = 6` enter the paper's power sentence as asserted counts with no instrument behind them. That is the unresolved part.

I also carried the same identity to the sibling active artifact `research/modalities/emc-expression-panels.json`, whose per-address claims (e.g. `emc-surface-target-landscape.md:344`, SSTR2 on GPL6244) print `n`, Δ, *t* and df together.

---

## Prior-work check

Commands run and what they showed:

- `rg -n -i "satterthwaite" --glob '!.git'` — 19 hits. The load-bearing one is `research/autonomy/review-seats/PUB-ATR-20d33f3478fa34940552d26ea8ae05cdd7a23ad2-seat-statistics.json:18`, which records a statistics seat doing *"recomputation of every part-B contrast from the per-sample score rows: Welch delta, t, Satterthwaite df and 95% CI, raw and proliferation-adjusted, **on both readable platforms**"*. That is **recomputation from the same primary rows** (verification), and it covered **2 of the 11 scored platform blocks**. It did not test the `df`-versus-`n` feasibility identity, and it did not touch `cross_platform_pooled` or the nine non-verdict platforms. No hit anywhere is on `emc-expression-panels.json`.
- `rg -n -i "welch" --glob '!.git' -l` — 20+ files; all are *uses* of Welch, none is a consistency check of df against group sizes.
- `rg -n -i "degrees of freedom" --glob '!.git'` — hits in the surface-targets peer review compute **p-values from the committed t and df** (`emc-surface-target-landscape-peer-review-2026-08-10.md:73`, "its t is 2.214 at 8.5 degrees of freedom, two-sided p = 0.056"). This *consumes* df as trusted input; it never validates it. That makes the df field load-bearing and unvalidated — which is what my check addresses.
- `rg -n -i "PUB-ATR" --glob '!.git' -l` — located the hardening state and 12+ review-seat records.

**Closed items I confirmed I am not replaying** (from `CLOSED-WORK.md`): I did not touch the ASO/NAT submission, the Qeios history, the tissue-RNA paper, or frozen comment `7baf272705d7a629f6d21d4fc169a7188775a60b`. I opened no new review round on any paper — this is an artifact-level arithmetic identity, not a prose review. I did not rediscover `GSE4303`/`GSE28866` as new data; I used only already-committed derived fields. I invented no cohort and retrieved no external source.

**Honest limit on this check:** my novelty evidence is a tree-wide `rg` for the concept's names. Absence of a hit is UNKNOWN, not proof no one ever did this by hand.

---

## Method / inputs

**Which study I chose, and the evidence it is active and unblocked.**

Two, both live:

1. **PUB-SURFACE-TARGETS** — `research/autonomy/cycle-tasks.json` carries the open bounded contract `surface-address-sample-sensitivity` (`resource: paper:PUB-SURFACE-TARGETS`, `ledger_ids: [AUT-025]`), whose declared `inputs` are exactly `research/modalities/emc-expression-panels.json` and siblings. It is a stated contract with an effort budget and a stop condition, not a frozen deliverable, and it appears nowhere in `CLOSED-WORK.md`.
2. **PUB-ATR** — `research/autonomy/hardening-state/PUB-ATR.json` records `last_round: 7`, `utc: 2026-09-02T21:20:02Z`, **`converged: false`**, and five open P1 findings against `reviewed_commit 51fb2b18…`, one of which (`p1s[0]`) is precisely that the MDE range *"is carried by NO artifact field and produced by NO code."* `cycle-tasks.json` also carries an open contract `fet-non-ewsr1-positive-control` with `resource: paper:PUB-ATR`. Not converged, not closed, not in `CLOSED-WORK.md`. `research/autonomy/goals.json` scopes the single tracked goal to PUB-ASO, which I excluded by lane rule.

**Inputs read (read-only, at HEAD `92abbcb9`):**

| File | Role |
|---|---|
| `research/modalities/emc-expression-panels.json` | 13.2 MB; `gene_reads` = 479 genes × platforms, each with `n_EMC_with_a_value`, `n_comparator_with_a_value`, `per_sample[]`, `welch_EMC_vs_comparator{t,df,mean_a,mean_b,delta_a_minus_b}` |
| `research/modalities/emc-atr-vulnerability.json` | 343 KB; `part_b_emc_tumour_signature.per_platform[*]` (11 platforms) with `class_counts`, four contrast blocks each; plus `cross_platform_pooled` |
| `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` | the claim at `:565` / `:831` |
| `research/manuscripts/surface-targets/emc-surface-target-landscape.md` | the SSTR2 claim at `:344` |

**Tools:** `python3` 3.11.15 (stdlib `json` only), GNU coreutils, ripgrep. No network, no installs, no paid API, no GPU.

**Which kind of orthogonal evidence I used, and why it is orthogonal.**

An **arithmetic identity the claim must satisfy but was not fitted to**, cross-validating **two independently emitted fields**.

Welch's *t*-test with $v_a = s_a^2/n_a$, $v_b = s_b^2/n_b$, $S = v_a + v_b$ has

$$\mathrm{df} \;=\; \frac{S^2}{\dfrac{v_a^2}{n_a-1} + \dfrac{v_b^2}{n_b-1}}$$

Substituting $f = v_a/S \in [0,1]$ removes the scale entirely:

$$\mathrm{df}(f) \;=\; \left[\frac{f^2}{n_a-1} + \frac{(1-f)^2}{n_b-1}\right]^{-1}$$

This is continuous on $[0,1]$, equals $n_b-1$ at $f=0$ and $n_a-1$ at $f=1$, and is maximised at $f^\ast = \frac{n_a-1}{(n_a-1)+(n_b-1)}$ with value $n_a+n_b-2$. Therefore the **exact** feasible set of a Welch df on group sizes $(n_a,n_b)$ is

$$\big[\;\min(n_a,n_b)-1,\;\; n_a+n_b-2\;\big]$$

— necessary *and* sufficient, not a heuristic bound. I derived this before writing the code, which is why the check needs no separate "do the variances come out positive" clause: that clause is equivalent to this interval.

**Why this is orthogonal rather than verification.** The `n_*_with_a_value` fields are counts of surviving samples. The `df` field is a variance-ratio functional emitted by the test. The generator was never asked to make one agree with the other, and no test in the repository ties them. The identity is a *third* object — a theorem — that both must obey. Checking a reported n against the sample list it came from would be verification; checking it against the df of a test that never reported n is not.

---

## Result

| # | Finding | n | Uncertainty | Tier |
|---|---|---|---|---|
| R1 | In `emc-expression-panels.json#gene_reads`, **872 of 958** gene×platform blocks carry `welch{df}` + both n fields. All 872 satisfy the Welch feasibility interval within the artifact's 1-dp print precision. **0 violations.** | 872 blocks | tolerance ±0.05 df (print precision), exact otherwise | PRIMARY (arithmetic on committed artifact) |
| R2 | Same 872 blocks: `delta_a_minus_b == mean_a − mean_b` to ≤2e-4. **0 violations.** | 872 | tolerance 2e-4 = 4-dp print precision | PRIMARY |
| R3 | Same 872 blocks: `n_EMC_with_a_value` and `n_comparator_with_a_value` exactly reproduce the counts of `per_sample` rows with a numeric `z_vs_array`. **0 violations.** | 872 | exact integer equality | PRIMARY |
| R4 | In `emc-atr-vulnerability.json`, **84** part-B contrast concept-blocks across 11 scored platforms + `cross_platform_pooled` satisfy the same feasibility interval. **0 violations.** 222 concept-slots were skipped because the block carries no df or an empty comparator arm (chiefly `contrast_EMC_vs_FET_comparators` on GSE4303, where `FET_comparator_classes` is `[]`). | 84 checked / 222 skipped | ±0.05 df | PRIMARY |
| R5 | `cross_platform_pooled.n_samples_pooled = 36` equals the sum of `n_samples` over the seven GSE4303 platform blocks (3+3+6+3+3+16+2 = 36); `cross_platform_pooled.class_counts = {unclassified 9, MFH_UPS 4, DFSP 8, EMC 10, GIST 5}` equals the element-wise sum of the seven per-platform `class_counts` **exactly**. Parts sum to the whole. | 7 strata | exact | PRIMARY |
| R6 | The manuscript's asserted **n = 10 and n = 6 EMC tumours** (`emc-atr-vulnerability-assessment.md:565`) is corroborated by orthogonal evidence: EMC = 10 in the pooled GSE4303 stratum sum (R5), and n_EMC = 6 on GSE24369 is forced by R1+R3 on that series' blocks. | 2 series | — | PRIMARY |
| R7 | **Discriminating power of the identity, measured, not assumed.** Perturbing one field by ±1 and re-running: `n_EMC−1` → 94/872 (10.8%) would fail; `n_EMC+1` → 76/872 (8.7%); `n_comp−1` → 94/872 (10.8%); `df+1` → 94/872 (10.8%); `df−1` → 109/872 (12.5%). | 872 | — | PRIMARY |
| R8 | 23 blocks sit **exactly on a feasibility edge**, 18 of them at (n_a,n_b) = (10,6) with df = 14.0 = n_a+n_b−2, i.e. the equal-variance maximum. Those are the tightest evidence in the set. | 23 | — | PRIMARY |
| R9 | Worked example, `emc-surface-target-landscape.md:344`: SSTR2 on GSE24369/GPL6244 has n_EMC = 6, n_comp = 29, **df = 5.3**, feasible interval [5, 33]. df sits 0.3 above the floor. Had n_EMC been 7, the floor would be 6 > 5.3 and the block would **fail**. For this block the identity actively pins n_EMC = 6. | 1 | — | PRIMARY |
| R10 | Whether the MDE *range endpoints* 0.045–0.186 are the min/max of 2.802·\|Δ\|/\|t\| over the specified concept set | — | not tested here | UNKNOWN |

**Outcome, stated plainly: the claim is CONFIRMED. No discrepancy was found.** The pre-stated criterion was met on both artifacts, with zero violations out of 872 + 84 checked blocks and an exact parts-to-whole match on the pooled stratum. The sample sizes underwriting `emc-atr-vulnerability-assessment.md:565`'s power sentence and `emc-expression-panels.json`'s 872 per-address contrasts are consistent with degrees of freedom that were never fitted to them.

I will not inflate this. R7 is the honest calibration: this identity is a **loose** constraint when the comparator arm is large — with n_comp = 29, the interval [5, 33] tolerates a lot — so a single-sample miscount is caught in roughly **9–12%** of blocks, not all of them. What the PASS establishes is that **no systematic** n/df inconsistency exists (a systematic one would have lit up the 23 edge-sitting blocks and the small-n GSE4303 platforms immediately), and that on the specific tight blocks — R8's eighteen (10,6) blocks at the exact equal-variance maximum, and R9's SSTR2 — the reported n is pinned. It does not certify every individual count.

---

## Validation evidence

### RUN

**Environment for all runs:** container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `python3 --version` → `Python 3.11.15`, cwd `/tmp/claude-0/w17`, stdlib only, no network. Repository read at HEAD `92abbcb905cacf07f14b238db50d1b98f6590374`.

**Run 1** — `cd /tmp/claude-0/w17 && python3 --version && time python3 welch_df_identity.py; echo "EXIT=$?"`

```
Python 3.11.15
blocks seen              : 958
blocks with welch+n+df   : 872
(a) df-feasibility viol. : 0
(b) delta-identity viol. : 0
(c) n-vs-per_sample viol.: 0
min distance of a passing df to its nearest feasibility edge: 0.0000
VERDICT: PASS

real	0m0.128s
user	0m0.096s
sys	0m0.032s
EXIT=0
```

**Run 2** — `python3 power.py; echo "EXIT=$?"`

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

**Run 3** — `python3 atr_df_identity.py; echo "EXIT=$?"`

```
pooled n_samples_pooled  : 36 | sum over GSE4303 platforms: 36
pooled class_counts      : {'unclassified': 9, 'MFH_UPS': 4, 'DFSP': 8, 'EMC': 10, 'GIST': 5}
sum of per-platform      : {'unclassified': 9, 'MFH_UPS': 4, 'DFSP': 8, 'EMC': 10, 'GIST': 5}
contrast blocks checked  : 84 | skipped (no df/n): 222
violations               : 0
VERDICT: PASS
EXIT=0
```

**Note on Run 1's `min distance … : 0.0000`:** that is R8, not a failure — 23 blocks sit exactly *on* an edge, which the closed interval admits. Run 2 was written specifically to confirm that reading rather than leave the 0.0000 ambiguous.

**Code — `/tmp/claude-0/w17/welch_df_identity.py`** (returned inline; nothing was written into the repository):

```python
"""W17 orthogonal identity check on research/modalities/emc-expression-panels.json.

Welch-Satterthwaite df is  df = S^2 / (va^2/(na-1) + vb^2/(nb-1)),  S = va+vb.
With f = va/S in [0,1],  df = 1/(f^2/(na-1) + (1-f)^2/(nb-1)).
That function is continuous, equals nb-1 at f=0, na-1 at f=1, and is maximised at
f* = (na-1)/((na-1)+(nb-1)) with value na+nb-2.  So the EXACT feasible set for a
Welch df on group sizes (na, nb) is  [min(na,nb)-1,  na+nb-2].
The df and the two n fields are emitted independently and neither is fitted to the other.
"""
import json, sys

PATH = "/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
TOL_DF = 0.05      # artifact prints df to 1 decimal
TOL_DELTA = 2e-4   # mean_a/mean_b printed to 4 decimals

d = json.load(open(PATH))
gr = d["gene_reads"]

n_blocks = n_checked = 0
viol_df = []; viol_delta = []; viol_n = []
df_slack = []

for gene, plats in gr.items():
    for plat, b in plats.items():
        if not isinstance(b, dict):
            continue
        n_blocks += 1
        w = b.get("welch_EMC_vs_comparator")
        if not isinstance(w, dict):
            continue
        df = w.get("df")
        na = b.get("n_EMC_with_a_value")
        nb = b.get("n_comparator_with_a_value")
        if df is None or na is None or nb is None:
            continue
        n_checked += 1
        # (a) df feasibility -- necessary AND sufficient, see module docstring
        lo = min(na, nb) - 1
        hi = na + nb - 2
        if not (lo - TOL_DF <= df <= hi + TOL_DF):
            viol_df.append((gene, plat, na, nb, df, lo, hi))
        else:
            df_slack.append(min(df - lo, hi - df))
        # (b) delta identity
        ma, mb, dl = w.get("mean_a"), w.get("mean_b"), w.get("delta_a_minus_b")
        if None not in (ma, mb, dl) and abs(dl - (ma - mb)) > TOL_DELTA:
            viol_delta.append((gene, plat, ma, mb, dl, dl - (ma - mb)))
        # (c) n reconstruction from per_sample
        ps = b.get("per_sample")
        if isinstance(ps, list) and ps:
            ea = sum(1 for r in ps if r.get("class") == "EMC"
                     and isinstance(r.get("z_vs_array"), (int, float)))
            eb = sum(1 for r in ps if r.get("class") != "EMC"
                     and isinstance(r.get("z_vs_array"), (int, float)))
            if (ea, eb) != (na, nb):
                viol_n.append((gene, plat, na, nb, ea, eb))

print(f"blocks seen              : {n_blocks}")
print(f"blocks with welch+n+df   : {n_checked}")
print(f"(a) df-feasibility viol. : {len(viol_df)}")
print(f"(b) delta-identity viol. : {len(viol_delta)}")
print(f"(c) n-vs-per_sample viol.: {len(viol_n)}")
for name, v in (("A", viol_df), ("B", viol_delta), ("C", viol_n)):
    for row in v[:25]:
        print(f"  VIOL-{name}", row)
    if len(v) > 25:
        print(f"  ... and {len(v)-25} more VIOL-{name}")
if df_slack:
    print(f"min distance of a passing df to its nearest feasibility edge: {min(df_slack):.4f}")
fail = bool(viol_df or viol_delta or viol_n)
print("VERDICT:", "FAIL" if fail else "PASS")
sys.exit(1 if fail else 0)
```

`/tmp/claude-0/w17/atr_df_identity.py` and `/tmp/claude-0/w17/power.py` are the two scripts quoted in Runs 2 and 3; their full text is in the transcript's tool calls and can be regenerated verbatim from there if the coordinator wants them committed.

### PROPOSED (NOT RUN)

- Promoting `welch_df_identity.py` into `research/modalities/tests/` as a behavioural test over both artifacts. **Not run, and deliberately not authored into the tree** — write isolation forbids it, and adding a test tier is not mine to decide.
- Re-deriving the MDE endpoints 0.045 and 0.186 as min/max of $(z_{0.975}+z_{0.80})\cdot|\Delta|/|t|$ over the proliferation-adjusted DDR concepts on both series (R10). Not run: this is re-derivation along the claim's *own* stated route, so it is verification and out of this lane's scope.
- No paid API, no GPU, no network retrieval, no external source was attempted. **No content-policy refusal was encountered in this lane.**

---

## Limitations

1. **A PASS is not proof of correctness.** R7 measures the check's real sensitivity: a single-sample miscount is detected in only ~9–12% of blocks. The interval $[\min(n_a,n_b)-1,\ n_a+n_b-2]$ is wide when the comparator arm is large. This result excludes a *systematic* n/df inconsistency; it does not certify every individual count.
2. **222 of 306 ATR concept-slots were not checked**, because those blocks carry no df or an empty comparator arm (`FET_comparator_classes: []` on the GSE4303 platforms). Unchecked is UNKNOWN, not passed.
3. **Rounding.** The artifact prints df to 1 dp and means to 4 dp. I used ±0.05 and 2e-4 tolerances matched to that precision. A defect smaller than print precision is invisible to this check.
4. **This validates bookkeeping, not biology.** Consistent n and df say nothing about whether the samples are correctly classified as EMC, whether the probes map to the right genes, whether the two-colour GSE4303 reference-channel collinearity flagged at `emc-atr-vulnerability-assessment.md:559–563` biases the contrast, or whether any address is therapeutically relevant. There is no wet lab. Nothing here establishes EMC efficacy, safety, selectivity or clinical readiness.
5. **The MDE range itself is still uninstrumented.** My result strengthens the *n* half of the power sentence. `PUB-ATR.json p1s[0]` — that "0.045–0.186 SD units" is carried by no artifact field and produced by no code — remains open and untouched by this work.
6. **Novelty evidence is a tree-wide `rg`.** No hit means UNKNOWN, not that no one has ever done this by hand.
7. **Denominator gap:** `n_comparator` pools heterogeneous sarcoma histologies that differ between the two series; the identity is blind to that and cannot address comparator-mixture transfer.

---

## Stop condition

**Set:** one claim in an active, unblocked EMC analysis validated against genuinely orthogonal evidence, with an executed check and a criterion stated before the result.

**MET.** The criterion (a/b/c above) was fixed in writing before either script ran and was not adjusted afterwards. Three runs executed, all exit 0. The claim — the group sizes underwriting `emc-atr-vulnerability-assessment.md:565` and the 872 Welch contrasts in `emc-expression-panels.json` — is **confirmed** against a Welch–Satterthwaite feasibility identity and a stratum-sums-to-marginal identity, neither of which was an input to it. Zero violations in 872 + 84 blocks; exact parts-to-whole on the pooled stratum. No discrepancy to report, and I have not manufactured one.

---

## Tool-call and wall-clock count actually used

**23 tool calls** (target ~40). **Wall clock 01:56:08Z → 02:00:07Z ≈ 4 minutes of tool time**, roughly 10 minutes including reasoning and drafting (target ~40 minutes). Returned as soon as the stop condition was met; no padding.

---

## Next concrete action

**One successor, specific:** extend the identity to the field it does *not* yet cover — reconstruct each `welch_EMC_vs_comparator` block's implied within-group variances $v_a, v_b$ by solving the two-equation Welch system from the committed $(\Delta, t, \mathrm{df}, n_a, n_b)$, then compare them against the variances computed directly from the `per_sample[].z_vs_array` rows in the same block. That closes the loop: it converts today's *loose* interval test into an *exact* point test, raising detection from ~10% of blocks to essentially 100%, and it needs no new data — `emc-expression-panels.json` already carries the per-sample rows for all 872 blocks. It would be a read-only script under `/tmp` returning a table, for the coordinator to decide whether it belongs in `research/modalities/tests/`.

result: Validated the group sizes underwriting PUB-ATR's power claim (`emc-atr-vulnerability-assessment.md:565`, "n = 10 and n = 6 EMC tumours") and 872 Welch contrasts in the active PUB-SURFACE-TARGETS artifact against an orthogonal Welch–Satterthwaite df-feasibility identity plus a stratum-sums-to-marginal check — pre-stated criterion, 3 runs all exit 0, 872+84 blocks and the pooled GSE4303 stratum all consistent, zero violations; CONFIRMED, with measured detection power of only ~9–12% per single-sample perturbation honestly reported, and no file written to the repository.
