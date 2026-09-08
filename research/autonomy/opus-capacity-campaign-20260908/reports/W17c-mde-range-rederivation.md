> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: re-ran nothing destructive; `git status --porcelain` under `/home/user/Rare-cancers` shows only the coordinator's pre-existing untracked campaign reports and no file of mine; all execution was in `/tmp/claude-0/w17c/`; the pass criterion was written into the script docstring before the script was executed and was not edited afterwards.

---

## Worker

**W17c**, lane 17 (refill) — re-derivation of an uninstrumented headline number in PUB-ATR.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). I did not observe the served model; no environment variable names a model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:11:41 UTC 2026` (first tool call); `date -u` at end: `Tue Sep  8 02:15:08 UTC 2026`.

`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` — model-relevant lines, verbatim (the full output is long and proxy-dominated; identical at start and end):

```
AI_AGENT=claude-code_2-1-263_agent
CLAUDE_CODE_VERSION=2.1.42
CLAUDECODE=1
CLAUDE_EFFORT=medium
CLAUDE_CODE_CHILD_SESSION=1
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
```

**No string matching `model` appears anywhere in the environment.**

**Repository state — one honest correction to the brief.** `git rev-parse HEAD` returns **`103ff76f1d66426420c56a4d49752eb84f5f5c39`**, not the brief's frozen read commit `92abbcb9…`. `git log --oneline -1 92abbcb9` resolves (`account-keyed cross-lane alarm: ATTENTION (CI)`), and `103ff76f` is `Add OPUS-CAPACITY-CAMPAIGN-20260908 manifest and worker reports` — i.e. the coordinator has committed campaign material on top of the frozen commit since W17 ran. The two files I read (`emc-atr-vulnerability.json`, `emc-atr-vulnerability-assessment.md`) are not touched by that commit, but I record the actual HEAD rather than the asserted one. `git status --porcelain` shows only untracked coordinator report files (W02b, W06b, W08b, W16b, W19b, W20b …). **I created and modified nothing under `/home/user/Rare-cancers` and ran no git write operation.**

---

## Question

**Can PUB-ATR's headline minimum-detectable-effect range "0.045–0.186 SD units" be re-derived from committed data along the manuscript's own stated route, and does it reproduce — and under which reading of its concept scope?**

Open because `research/autonomy/hardening-state/PUB-ATR.json` records `last_round: 7`, `converged: false`, and five open P1s, of which `p1s[0]` is exactly this. Quoted **verbatim** (the `summary` field):

> "The minimum-detectable-effect range '0.045-0.186 SD units' (printed twice, in the body and again in section 6.1) is correct but is carried by NO artifact field and produced by NO code, and the recipe as printed is ambiguous between t- and normal critical values, where the normal reading gives a visibly different range."

The manuscript's claim, quoted exactly.

`research/manuscripts/dependency/emc-atr-vulnerability-assessment.md:565–570`:

> "⚠ **Part B's nulls are at n = 10 and n = 6 EMC tumours.** The minimum detectable effect is computed as SE = |Δ|/|*t*| from the committed contrast blocks, at 80 % power and two-sided α 0.05, against the fixed 0.2 elevated cut. On the proliferation-adjusted contrast the verdict rests on — no concept clears 0.2 after adjustment on either series — every DDR concept on both series is powered to see an effect of 0.045–0.186 SD units, comfortably inside the 0.2 cut. So this is not an unqualified demonstration that a DDR signal is absent: effects below roughly 0.1 SD units are not excluded."

and at `:831`:

> "**no proliferation-adjusted DDR concept exceeds the 0.2 elevated cut on either series, with ≥80 % power to have seen one down to 0.045–0.186 SD units** (§3.4)."

So the claimed set is: **DDR concepts × both series, on the proliferation-adjusted contrast**. The range is the min and max of the per-concept MDE over that set.

---

## Prior-work check

- `PUB-ATR.json` `p1s[0]` itself contains a hardening-seat re-derivation with twelve numbers. **My run is therefore a second, independent execution of a computation a seat previously reported in prose**, not a first. I say so plainly rather than claiming novelty: what is new is (i) an *executed* script with a real command, environment and exit code — the seat's numbers live only in a JSON `evidence` string with no code behind them, which is the very defect being reported; (ii) an explicit enumeration and elimination of the scope readings; and (iii) a measurement of how *inert* the scope ambiguity actually is.
- W17's own report (transferred to me) lists this as its `R10` — "Whether the MDE *range endpoints* 0.045–0.186 are the min/max … **UNKNOWN**, not tested here" — and in `PROPOSED (NOT RUN)` as deliberately out of its lane. So it was left standing on purpose, and this is the sanctioned pickup.
- I did not redo W17's df-feasibility identity (confirmed, zero violations, ~9–12 % detection power) and did not touch W17b's point-test upgrade.
- Grep at HEAD, confirming the "no code" half of `p1s[0]` independently:
  - `grep -nE 't_\.975|MDE|minimum_detectable|\.ppf\(' research/modalities/emc_atr_vulnerability.py` → **no output**.
  - `grep -c 'detectable' research/modalities/emc-atr-vulnerability.json` → the only power-adjacent strings in the artifact are `"_status": "underpowered: n_a=…, n_b=…"` markers. **No `minimum_detectable_effect` field exists.**
- **CLOSED-WORK.md items I confirmed I am not replaying:** no ASO/NAT or Qeios work, no tissue-RNA paper, no edit or re-review of frozen comment `7baf2727…`; no rediscovery of `GSE4303`/`GSE28866` as new data (I used only committed derived fields); no invented cohort; no external retrieval; **no review round opened on PUB-ATR**, no edit to the manuscript or to the hardening state.

---

## Method / inputs

| File (read-only) | Role |
|---|---|
| `research/autonomy/hardening-state/PUB-ATR.json` | the P1 target, quoted above |
| `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` `:559–578`, `:820–840` | the claim and its stated derivation |
| `research/modalities/emc-atr-vulnerability.json` | `part_b_emc_tumour_signature.per_platform[*].contrast_*` — the (Δ, t, df) inputs |
| `research/modalities/emc-atr-vulnerability-inputs.json` | `gene_sets.concepts[*].role` — the concept classification |

**Tools:** `python3` 3.11.15, `scipy` 1.17.1 (`scipy.stats.norm`, `scipy.stats.t`), ripgrep/coreutils. No network, no installs, no paid API, no GPU. Execution directory `/tmp/claude-0/w17c/`.

### Step 2 — the concept scope, established from the artifact before computing

**The "DDR concept" half is not ambiguous.** `emc-atr-vulnerability-inputs.json#gene_sets.concepts` tags each concept with a `role`. Exactly six carry `role: "tested"`:

`ATM_signalling_DSB_repair`, `ATR_CHK1_activity`, `replication_stress`, `stalled_fork_response`, `S_phase_E2F`, `DNA_damage_checkpoint`

The other six are `proliferation_control` (`proliferation_MYC`, `proliferation_mitotic`) or `unrelated_control` (`control_myogenesis`, `control_adipogenesis`, `control_oxphos`, `control_generic_DNA_repair`). The artifact's own `ddr_concepts_elevated_raw` = `["ATR_CHK1_activity","S_phase_E2F","DNA_damage_checkpoint"]` — a subset of the six — corroborates that mapping, and matches the manuscript's own three-concept raw sentence at `:572–573`. So "DDR concepts" = the six `tested` concepts, sourced from the artifact, not chosen by me.

**The "both series" half is where the prose is loose**, so I enumerated rather than picked. `part_b` names GSE4303 and GSE24369 as the two series; GSE4303 is spread over **seven** platform files, of which `platforms_with_a_readable_EMC_vs_comparator_contrast` lists only `GSE4303-GPL3290`. Candidate readings, all five computed:

- **S1** verdict platform `GSE4303-GPL3290` + `GSE24369`, 6 DDR, proliferation-adjusted — the literal reading of the sentence.
- **S2** same platforms, **all 12** concepts, adjusted — the reading where "DDR concept" is taken loosely.
- **S3** all 7 GSE4303 platforms + GSE24369, 6 DDR, adjusted — "series" read as every platform in the series.
- **S4** all 11 platforms with `scored_concepts > 0`, 6 DDR, adjusted.
- **S5** S1 but on the **RAW** contrast — the reading that ignores "proliferation-adjusted".

### Step 4 — pass criterion, FIXED BEFORE THE RUN

Written into the script's module docstring before execution, and not edited afterwards:

> A scope reading **REPRODUCES** iff `round(min,3) == 0.045` **and** `round(max,3) == 0.186`, i.e. the endpoints agree at the manuscript's own printed 3-decimal precision. Anything else is **DOES-NOT-REPRODUCE** and is reported as expected-vs-observed.

Because the manuscript names 80 % power and two-sided α 0.05 but **names no distribution**, both readings of the critical-value sum were computed for every scope:

- **NORMAL:** `z_.975 + z_.80 = 1.959964 + 0.841621 = 2.801585` (the constant the dispatch brief itself assumed).
- **STUDENT:** `t_.975(df) + t_.80(df)`, with `df` the Welch df carried in the same contrast block.

---

## Result

**Verdict: the range REPRODUCES EXACTLY under scope S1 with STUDENT-t critical values, and DOES NOT reproduce under the normal reading.**

### R1 — scope sweep `PRIMARY` (arithmetic on committed artifact)

| Scope | n blocks | min (z) | max (z) | min (t) | max (t) | vs 0.045–0.186 |
|---|---|---|---|---|---|---|
| **S1** GPL3290 + GSE24369, 6 DDR, adj | 12 | 0.0414 | 0.1644 | **0.0449** | **0.1856** | **t: REPRODUCES** / z: no |
| S2 same, all 12 concepts, adj | 20 | 0.0414 | 0.3175 | 0.0449 | 0.3435 | neither |
| S3 all 7 GSE4303 platforms + GSE24369, 6 DDR, adj | 12 | 0.0414 | 0.1644 | 0.0449 | 0.1856 | **t: REPRODUCES** / z: no |
| S4 all 11 scored platforms, 6 DDR, adj | 12 | 0.0414 | 0.1644 | 0.0449 | 0.1856 | **t: REPRODUCES** / z: no |
| S5 GPL3290 + GSE24369, 6 DDR, **RAW** | 12 | 0.0427 | 0.2802 | 0.0462 | 0.3261 | neither |

`round(0.0449,3) = 0.045`; `round(0.1856,3) = 0.186`. Criterion met, unmodified.

### R2 — the scope ambiguity is real in the prose but **inert** in the arithmetic `PRIMARY`

S1, S3 and S4 return the **identical 12 rows**. Reason, verified directly: nine of the eleven platforms carry no usable adjusted DDR contrast. `GSE4303-GPL2937 … ATM_signalling_DSB_repair` is `{"_status": "underpowered: n_a=0, n_b=0"}`; `GPL3254` is `{"_status": "underpowered: n_a=0, n_b=4"}`; `GSE28866`'s adjusted block value is `null`. Only `GSE4303-GPL3290` and `GSE24369` carry (Δ, t, df) triples. **So "both series" cannot be misread into a different number** — every platform-scope reading collapses to the same 12 blocks. The only readings that change the answer are the two the manuscript's own words already exclude: S2 (widening past `role: tested`) and S5 (dropping "proliferation-adjusted"). That is a finding in the manuscript's favour and I record it as such.

### R3 — per-block detail, S1 `PRIMARY`

SE = |Δ|/|t| in SD units; MDE in SD units; df is the Welch df carried in the block. n = 10 EMC vs 6 comparator (GSE4303/GPL3290) and 6 EMC vs 36 comparator (GSE24369) — the counts W17 independently confirmed against the df-feasibility identity.

| Platform | Concept | Δ | t | df | SE | MDE (normal) | MDE (t) |
|---|---|---|---|---|---|---|---|
| GSE4303-GPL3290 | ATM_signalling_DSB_repair | −0.0701 | −1.574 | 12.7 | 0.0445 | 0.1248 | 0.1352 |
| GSE4303-GPL3290 | ATR_CHK1_activity | 0.0622 | 1.060 | 8.6 | 0.0587 | 0.1644 | **0.1856 ← max** |
| GSE4303-GPL3290 | replication_stress | −0.0267 | −0.562 | 12.8 | 0.0475 | 0.1331 | 0.1442 |
| GSE4303-GPL3290 | stalled_fork_response | −0.0384 | −0.769 | 11.4 | 0.0499 | 0.1399 | 0.1531 |
| GSE4303-GPL3290 | S_phase_E2F | 0.1282 | 3.602 | 10.7 | 0.0356 | 0.0997 | 0.1098 |
| GSE4303-GPL3290 | DNA_damage_checkpoint | 0.0735 | 2.378 | 12.7 | 0.0309 | 0.0866 | 0.0939 |
| GSE24369 | ATM_signalling_DSB_repair | −0.0350 | −1.771 | 6.9 | 0.0198 | 0.0554 | 0.0646 |
| GSE24369 | ATR_CHK1_activity | −0.0200 | −0.572 | 8.2 | 0.0350 | 0.0980 | 0.1113 |
| GSE24369 | replication_stress | −0.0309 | −1.323 | 7.1 | 0.0234 | 0.0654 | 0.0760 |
| GSE24369 | stalled_fork_response | −0.0397 | −2.685 | 12.7 | 0.0148 | 0.0414 | **0.0449 ← min** |
| GSE24369 | S_phase_E2F | 0.0131 | 0.356 | 7.7 | 0.0368 | 0.1031 | 0.1182 |
| GSE24369 | DNA_damage_checkpoint | 0.0136 | 0.399 | 8.5 | 0.0341 | 0.0955 | 0.1080 |

All twelve values match `p1s[0]`'s recorded seat re-derivation to the digit (0.1352, 0.1856, 0.1442, 0.1531, 0.1098, 0.0939; 0.0646, 0.1113, 0.0760, 0.0449, 0.1182, 0.1080). Two independent derivations, same numbers — the seat's prose figures are now backed by an executed run.

### R4 — the surviving defect, stated at its true size `PRIMARY`

**The number is right. The recipe as printed is under-specified, and the under-specification is load-bearing.** Taking the manuscript's sentence at face value with the natural default when no distribution is named — the normal critical values, exactly the reading the dispatch brief itself adopted (`MDE = 2.802·|Δ|/|t|`) — a reader gets **0.041–0.164**, not 0.045–0.186.

- **Expected (as printed):** 0.045 – 0.186
- **Observed (normal reading):** 0.0414 – 0.1644
- **Magnitude:** lower endpoint low by 0.0035 SD (−7.8 %); upper endpoint low by 0.0216 SD (−11.6 %). Both are **conservative-sounding but wrong** — the normal reading understates the detectable effect, i.e. it makes the study look better powered than the manuscript actually claims.
- **Smallest correction implied:** the numbers need no change. Insert the distribution into the one sentence that gives the formula, `:566–567`, e.g. "…at 80 % power and two-sided α 0.05, using **t critical values on the Welch df carried in each contrast block (t₍.975₎ + t₍.80₎)**, against the fixed 0.2 elevated cut." That is a ~14-word insertion and nothing else changes. It is `p1s[0]`'s own option (b), which I reached independently; I do not author it, and I make no recommendation between the seat's (a) and (b).
- **The second half of `p1s[0]` — "carried by NO artifact field and produced by NO code" — is confirmed and still stands.** My run instruments the number in `/tmp`, outside the tree; it does not put it in `emc_atr_vulnerability.py` or in the artifact, so `--check` still cannot re-derive it and §7's blanket "`--check` re-derives all of it offline" still does not hold for this figure. Only the *reproducibility* question is closed; the *instrumentation* question is not.

### R5 — `UNKNOWN`

Whether the manuscript's authors in fact intended the t reading, or arrived at 0.045–0.186 by a route other than the one at `:566`, is not determinable from committed material. That the t reading reproduces both endpoints to print precision across 12 blocks is strong circumstantial evidence, but it is inference, not a record.

---

## Validation evidence

### RUN

**Environment:** container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux 6.18.44-fc-v24, `Python 3.11.15`, `scipy 1.17.1`, cwd `/tmp/claude-0/w17c`, no network. Repository read at HEAD `103ff76f1d66426420c56a4d49752eb84f5f5c39` (see the correction under **Worker**).

**Command:** `cd /tmp/claude-0/w17c && python3 mde_rederive.py; echo "EXIT=$?"`

**Verbatim output:**

```
scipy 1.17.1
DDR (role=='tested') concepts: ['ATM_signalling_DSB_repair', 'ATR_CHK1_activity', 'replication_stress', 'stalled_fork_response', 'S_phase_E2F', 'DNA_damage_checkpoint']
normal critical sum z_.975+z_.80 = 2.801585

SCOPE                                                          n    min_z    max_z    min_t    max_t  VERDICT(t)/VERDICT(z)
S1 verdict-platform GPL3290 + GSE24369, 6 DDR, PROLIF-ADJ     12   0.0414   0.1644   0.0449   0.1856  t:REPRODUCES / z:does-not
S2 same platforms, ALL 12 concepts, PROLIF-ADJ                20   0.0414   0.3175   0.0449   0.3435  t:does-not / z:does-not
S3 all 7 GSE4303 platforms + GSE24369, 6 DDR, PROLIF-ADJ      12   0.0414   0.1644   0.0449   0.1856  t:REPRODUCES / z:does-not
S4 all 11 scored platforms, 6 DDR, PROLIF-ADJ                 12   0.0414   0.1644   0.0449   0.1856  t:REPRODUCES / z:does-not
S5 verdict-platform GPL3290 + GSE24369, 6 DDR, RAW            12   0.0427   0.2802   0.0462   0.3261  t:does-not / z:does-not

--- per-block detail for S1 (the reading the manuscript's words scope) ---
platform                               concept                        delta        t     df        SE     MDE_z     MDE_t
GSE4303-GPL3290_series_matrix.txt.gz   ATM_signalling_DSB_repair    -0.0701   -1.574   12.7    0.0445    0.1248    0.1352
GSE4303-GPL3290_series_matrix.txt.gz   ATR_CHK1_activity             0.0622    1.060    8.6    0.0587    0.1644    0.1856
GSE4303-GPL3290_series_matrix.txt.gz   replication_stress           -0.0267   -0.562   12.8    0.0475    0.1331    0.1442
GSE4303-GPL3290_series_matrix.txt.gz   stalled_fork_response        -0.0384   -0.769   11.4    0.0499    0.1399    0.1531
GSE4303-GPL3290_series_matrix.txt.gz   S_phase_E2F                   0.1282    3.602   10.7    0.0356    0.0997    0.1098
GSE4303-GPL3290_series_matrix.txt.gz   DNA_damage_checkpoint         0.0735    2.378   12.7    0.0309    0.0866    0.0939
GSE24369_series_matrix.txt.gz          ATM_signalling_DSB_repair    -0.0350   -1.771    6.9    0.0198    0.0554    0.0646
GSE24369_series_matrix.txt.gz          ATR_CHK1_activity            -0.0200   -0.572    8.2    0.0350    0.0980    0.1113
GSE24369_series_matrix.txt.gz          replication_stress           -0.0309   -1.323    7.1    0.0234    0.0654    0.0760
GSE24369_series_matrix.txt.gz          stalled_fork_response        -0.0397   -2.685   12.7    0.0148    0.0414    0.0449
GSE24369_series_matrix.txt.gz          S_phase_E2F                   0.0131    0.356    7.7    0.0368    0.1031    0.1182
GSE24369_series_matrix.txt.gz          DNA_damage_checkpoint         0.0136    0.399    8.5    0.0341    0.0955    0.1080
EXIT=0
```

**Supporting run — why S1/S3/S4 coincide** (`python3 -c …` over the artifact):

```
GSE4303-GPL2937_series_matrix.txt.gz {"_status": "underpowered: n_a=0, n_b=0"}
GSE28866_series_matrix.txt.gz null
GSE4303-GPL3254_series_matrix.txt.gz {"_status": "underpowered: n_a=0, n_b=4"}
```

**Code — `/tmp/claude-0/w17c/mde_rederive.py`** (returned inline; nothing written into the repository):

```python
"""W17c -- re-derivation of PUB-ATR's headline minimum-detectable-effect range
"0.045-0.186 SD units" (emc-atr-vulnerability-assessment.md:565-570 and :831).

STATED DERIVATION (manuscript, :565-567):
    "The minimum detectable effect is computed as SE = |D|/|t| from the committed
     contrast blocks, at 80 % power and two-sided alpha 0.05, against the fixed 0.2
     elevated cut."
So  MDE = (crit_two_sided_0.05 + crit_one_sided_0.20_upper) * SE,  SE = |delta| / |t|.
The manuscript names NO distribution, so BOTH readings are computed:
    NORMAL : z_.975 + z_.80  = 1.959964 + 0.841621 = 2.801585
    STUDENT: t_.975(df) + t_.80(df), df = the Welch df carried in the same block.

PASS CRITERION -- FIXED IN WRITING BEFORE THE SCRIPT WAS RUN, NOT ADJUSTED AFTER:
    A scope reading REPRODUCES iff  round(min,3) == 0.045  AND  round(max,3) == 0.186,
    i.e. the endpoints agree with the manuscript's printed 3-decimal precision.
    Anything else is DOES-NOT-REPRODUCE and is reported as expected-vs-observed.

CONCEPT SCOPE: "DDR concepts" is taken from the artifact, not from prose --
emc-atr-vulnerability-inputs.json#gene_sets.concepts tags exactly six concepts
role == "tested"; the other six are role "proliferation_control" (2) or
"unrelated_control" (4).  Candidate readings of "on both series" are enumerated.
"""
import json
from scipy.stats import norm, t as tdist
import scipy

ART = "/home/user/Rare-cancers/research/modalities/emc-atr-vulnerability.json"
INP = "/home/user/Rare-cancers/research/modalities/emc-atr-vulnerability-inputs.json"

art = json.load(open(ART))
inp = json.load(open(INP))
B = art["part_b_emc_tumour_signature"]
PP = B["per_platform"]

concepts = inp["gene_sets"]["concepts"]
DDR = [k for k, v in concepts.items() if v.get("role") == "tested"]
ALL12 = [k for k in concepts]
print("scipy", scipy.__version__)
print("DDR (role=='tested') concepts:", DDR)

Z = norm.ppf(0.975) + norm.ppf(0.80)
print("normal critical sum z_.975+z_.80 = %.6f" % Z)

ADJ = "contrast_EMC_vs_all_comparator_sarcoma_PROLIFERATION_ADJUSTED"
RAW = "contrast_EMC_vs_all_comparator_sarcoma"

G4303_VERDICT = "GSE4303-GPL3290_series_matrix.txt.gz"
G24369 = "GSE24369_series_matrix.txt.gz"
G4303_ALL = [k for k in PP if k.startswith("GSE4303-")]
SCORED = [k for k, n in B["scored_concepts_per_platform"].items() if n > 0]

def mde(plats, conc, block):
    rows = []
    for p in plats:
        blk = PP[p].get(block, {})
        for c in conc:
            b = blk.get(c)
            if not isinstance(b, dict):
                continue
            dl, tt, df = b.get("delta_a_minus_b"), b.get("t"), b.get("df")
            if dl is None or tt is None or tt == 0:
                continue
            se = abs(dl) / abs(tt)
            m_z = Z * se
            m_t = (tdist.ppf(0.975, df) + tdist.ppf(0.80, df)) * se if df else None
            rows.append((p, c, dl, tt, df, se, m_z, m_t))
    return rows

SCOPES = {
 "S1 verdict-platform GPL3290 + GSE24369, 6 DDR, PROLIF-ADJ": ([G4303_VERDICT, G24369], DDR, ADJ),
 "S2 same platforms, ALL 12 concepts, PROLIF-ADJ":            ([G4303_VERDICT, G24369], ALL12, ADJ),
 "S3 all 7 GSE4303 platforms + GSE24369, 6 DDR, PROLIF-ADJ":  (G4303_ALL + [G24369], DDR, ADJ),
 "S4 all 11 scored platforms, 6 DDR, PROLIF-ADJ":             (SCORED, DDR, ADJ),
 "S5 verdict-platform GPL3290 + GSE24369, 6 DDR, RAW":        ([G4303_VERDICT, G24369], DDR, RAW),
}

EXP_LO, EXP_HI = 0.045, 0.186
print("\n%-58s %5s %8s %8s %8s %8s  %s" % ("SCOPE", "n", "min_z", "max_z", "min_t", "max_t", "VERDICT(t)/VERDICT(z)"))
detail = {}
for name, (plats, conc, block) in SCOPES.items():
    rows = mde(plats, conc, block)
    detail[name] = rows
    if not rows:
        print("%-58s   (no blocks)" % name); continue
    mz = [r[6] for r in rows]; mt = [r[7] for r in rows]
    vt = "REPRODUCES" if (round(min(mt),3)==EXP_LO and round(max(mt),3)==EXP_HI) else "does-not"
    vz = "REPRODUCES" if (round(min(mz),3)==EXP_LO and round(max(mz),3)==EXP_HI) else "does-not"
    print("%-58s %5d %8.4f %8.4f %8.4f %8.4f  t:%s / z:%s" %
          (name, len(rows), min(mz), max(mz), min(mt), max(mt), vt, vz))

print("\n--- per-block detail for S1 (the reading the manuscript's words scope) ---")
print("%-38s %-26s %9s %8s %6s %9s %9s %9s" % ("platform","concept","delta","t","df","SE","MDE_z","MDE_t"))
for p, c, dl, tt, df, se, mz_, mt_ in detail["S1 verdict-platform GPL3290 + GSE24369, 6 DDR, PROLIF-ADJ"]:
    print("%-38s %-26s %9.4f %8.3f %6.1f %9.4f %9.4f %9.4f" % (p[:38], c, dl, tt, df, se, mz_, mt_))
```

### PROPOSED (NOT RUN)

- Emitting `minimum_detectable_effect_at_80pc_power` per concept per series from `emc_atr_vulnerability.py` into `part_b`, so `--check` re-derives it (`p1s[0]` option (a)). **Not run and deliberately not authored** — write isolation forbids it, and the choice between (a) and (b) is the PUB-ATR owner's.
- Applying the 14-word critical-value insertion at `:566–567` (option (b)). **Not applied** — routed, not executed.
- No network, no paid API, no GPU, no external retrieval was attempted. **No content-policy refusal was encountered in this lane.**

---

## Routed statement to the PUB-ATR owner

> `PUB-ATR.json` `p1s[0]` — the MDE range **0.045–0.186 SD units** at `emc-atr-vulnerability-assessment.md:565–570` and `:831` — has now been re-derived by an executed script from committed artifact fields, against a pass criterion fixed before the run.
>
> 1. **The number reproduces exactly**, to the manuscript's own printed 3-decimal precision, under one and only one reading: the six `role: "tested"` DDR concepts of `emc-atr-vulnerability-inputs.json`, on the proliferation-adjusted contrast, across `GSE4303-GPL3290` and `GSE24369`, with **Student-t critical values on the Welch df carried in each block** — `MDE = (t₍.975₎(df) + t₍.80₎(df))·|Δ|/|t|`. Observed 0.0449 – 0.1856 over 12 blocks. That is the scope reading that closes the reproducibility half of the finding.
> 2. **The platform-scope ambiguity is inert.** Widening "both series" from the verdict platform to all seven GSE4303 platforms, or to all eleven scored platforms, returns the identical 12 blocks, because the other nine carry `_status: "underpowered: n_a=0, …"` or `null`. No reader can arrive at a different number by mis-scoping the series.
> 3. **The distribution ambiguity is not inert, and it is the live defect.** A reader taking the sentence at face value — it names 80 % power and two-sided α 0.05 and no distribution — uses normal critical values (2.801585) and gets **0.0414 – 0.1644**. Expected vs observed: lower endpoint −0.0035 SD (−7.8 %), upper −0.0216 SD (−11.6 %), both in the direction that overstates the study's power. The smallest correction is a ~14-word insertion at `:566–567` naming the t convention; the printed endpoints do not change.
> 4. **The instrumentation half of `p1s[0]` still stands.** My script ran in `/tmp/claude-0/w17c/`, outside the tree. `grep -nE 't_\.975|MDE|minimum_detectable|\.ppf\(' research/modalities/emc_atr_vulnerability.py` returns nothing at HEAD, and the artifact carries no MDE field, so `--check` still cannot re-derive this figure and §7's blanket claim still does not hold for it. Whether to close that by emitting the field (option a) or by the prose exception note (option b) is yours; I have authored neither, opened no review round, and edited neither the manuscript nor the hardening state.

---

## Limitations

1. **This is bookkeeping arithmetic, not biology.** Reproducing an MDE range says nothing about whether EMC has a DDR phenotype, whether the concepts are the right gene sets, whether the GSE4303 two-colour reference-channel collinearity flagged at `:559–563` biases the underlying Δ, or whether any of it is therapeutically relevant. There is no wet lab. **No clinical claim, and nothing here establishes efficacy, safety, selectivity or clinical readiness.**
2. **A reproduction is not a validation of the inputs.** I took (Δ, t, df) as committed. If the contrast blocks were wrong, my MDEs would be wrong in exactly the same way and would still "reproduce". W17's orthogonal df-feasibility check bounds that risk for the n fields but, by its own measurement, detects a single-sample miscount in only ~9–12 % of blocks.
3. **The pass criterion is a 3-decimal round.** A defect below print precision is invisible to it. I chose the criterion to match the manuscript's own printing and did not tune it.
4. **Intent is UNKNOWN** (R5). I show the t reading reproduces; I cannot show it was the route taken.
5. **`round()` uses banker's rounding**, immaterial here (0.0449 and 0.1856 are not half-way cases).
6. **HEAD differs from the brief's frozen commit** (`103ff76f` vs `92abbcb9`). The two scientific files I read are untouched by the intervening commit, but the reader should know the run was not literally at the frozen pin.
7. **The four other open P1s in `PUB-ATR.json` are untouched**, including `p1s[1]` (no `artifact_figures` binding for this document) and `p1s[2]` (the Section 3.1 itemisation summing to 22 against a correct total of 27). `converged: false` remains correct.

---

## Stop condition

**Set:** an executed re-derivation of the 0.045–0.186 range with a criterion stated before the result, and an explicit reproduce / does-not-reproduce verdict scoped to the reading that produced it.

**MET.** Criterion fixed in the script docstring before execution and not adjusted. One run, exit 0. **Verdict: REPRODUCES**, exactly, under scope S1 with Student-t critical values on the carried Welch df (0.0449–0.1856 → 0.045–0.186); **DOES NOT REPRODUCE** under the normal-critical-value reading the manuscript's wording invites (0.0414–0.1644, endpoints low by 7.8 % and 11.6 %). I neither manufactured a defect nor softened the one that is there: the number is correct, the recipe as printed is not sufficient to regenerate it, and the number remains carried by no artifact field and produced by no committed code.

---

## Tool-call and wall-clock count actually used

**10 tool calls** (target ~40). **Wall clock 02:11:41Z → 02:15:08Z ≈ 3.5 minutes of tool time**, ~12 minutes including reading and drafting (target ~40). Returned as soon as the stop condition was met; no padding.

---

## Next concrete action

**One successor, specific and inside this lane:** `p1s[0]`'s sibling `p1s[1]` — the absence of any `artifact_figures` entry for `emc-atr-vulnerability-assessment.md` in `research/manuscripts/pinned-figures.json` — is now the highest-value open item, and the same technique applies. Build a read-only extractor under `/tmp` that walks the manuscript's ~200 machine-derived printed numbers, resolves each to a candidate JSON path in `emc-atr-vulnerability.json`, and reports (i) matches, (ii) mismatches, and (iii) printed numbers with no resolvable artifact home — the last category being where the next `p1s[0]`-shaped finding lives. It needs no new data and no writes, and it produces exactly the keyed `artifact_figures` candidate list `p1s[1]`'s `fix` asks for, for the PUB-ATR owner to accept or reject. I would **not** attempt `p1s[2]` (the 22-vs-27 itemisation) in this lane: its repair is prose, and prose is the owner's.

result: PUB-ATR's headline MDE range "0.045–0.186 SD units" REPRODUCES exactly (0.0449–0.1856, 12 blocks, exit 0) from committed artifact fields under one scope reading — the six `role: "tested"` DDR concepts, proliferation-adjusted, on GSE4303-GPL3290 + GSE24369, using **Student-t** critical values on the carried Welch df; the normal-critical-value reading the manuscript's wording invites gives 0.041–0.164 instead (endpoints low by 7.8 % and 11.6 %), so the number is right but the printed recipe is insufficient to regenerate it — smallest correction is a ~14-word insertion naming the t convention at `:566–567`, routed to the PUB-ATR owner; the platform-scope ambiguity is inert (nine of eleven platforms carry no usable block), the "no artifact field, no code" half of `p1s[0]` still stands, and nothing was written to the repository.
