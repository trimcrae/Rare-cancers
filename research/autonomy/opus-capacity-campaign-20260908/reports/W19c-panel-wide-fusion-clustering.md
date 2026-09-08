> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check done: W20b's six per-pair Jaccards reproduce digit-for-digit, both apparent replication discrepancies traced to a definite cause (one a convention, one my own double-counting counter), all three scripts exited 0, the negative control behaved as a control, and `git status` shows only the coordinator's own untracked report files — I wrote nothing under `/home/user/Rare-cancers`. Report follows.

---

## Worker

**Worker ID:** W19c · **Lane 19 slot, reassigned.** Lane 19's own question is closed on W19b's recommendation; this slot executes W20b's named secondary successor instead.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model; this is a self-report from my own system context, not an observed fact. The coordinator must extract the actual per-child runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I' | sort` at start (proxy-plumbing lines `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `NO_PROXY`, `no_proxy`, `npm_config_noproxy` matched the grep and are verbatim in the tool log; they are elided here for length and contain nothing model-relevant):

```
AI_AGENT=claude-code_2-1-263_agent
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDECODE=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
CLAUDE_AFTER_LAST_COMPACT=true
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
CLAUDE_AUTO_BACKGROUND_TASKS=true
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_CHILD_SESSION=1
CLAUDE_CODE_CONTAINER_ID=container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4
CLAUDE_CODE_DEBUG=true
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
CLAUDE_CODE_GZIP_REQUEST_BODIES=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_MESSAGING_SOCKET=/tmp/cc-socks/522.sock
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST=1
CLAUDE_CODE_PROXY_RESOLVES_HOSTS=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_SYNC_SESSION_REFS=1
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_EFFORT=medium
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_PID=522
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
SESSION_INGRESS_URL=https://api.anthropic.com
```

`date -u` at start: `Tue Sep  8 02:15:15 UTC 2026` · at end: `Tue Sep  8 02:18:00 UTC 2026`.

**Repository state.** `git rev-parse HEAD` read `103ff76f1d66426420c56a4d49752eb84f5f5c39` at start and `b9a0257e6acff53ad22535cf2adf261313e0b250` at end. **Neither is the frozen campaign commit `92abbcb…`** — the coordinator has been committing sibling workers' reports concurrently, and HEAD moved twice during my run. **I did not do this and did not perform any git write of any kind.** `git status --porcelain` showed only untracked paths under `research/autonomy/opus-capacity-campaign-20260908/reports/` (other workers' collected reports), 6 at start, 2 at end. Every file I created lives under `/tmp/claude-0/w19c/`. Nothing was downloaded; `df -h /` = 24 GiB available.

**No network request of any kind was made in this run.** The GSE243553 genome-wide `MOESM3_ESM.zip` route is a recorded 403 CONNECT policy denial; I did not probe it, retry it, route around it, or attempt an alternative host. It stands as an honest unrecovered source. **I hit no content-policy refusal.**

---

## Question

**Does the GSE243553 fusion panel cluster by 5′ partner, by 3′ partner, or by neither?**

W20b tested one pre-specified quartet (the four `*-NR4A3` fusions) against a null over all four-member subsets, and found their peak *locations* converge (mean Jaccard 0.199, exact p = 0.0013; 0.0010 density-matched). That is a statement about one quartet. The panel-wide question is different and strictly more informative: across all 32 peaksets and all 496 pairs, **is location similarity predicted by sharing a 5′ gene, by sharing a 3′ gene, by both, or by neither?** And — the check that decides how W20b's result should be read — **does 3′ sharing still predict location once the NR4A3 quartet is removed?**

It is open because no pairwise comparison between GSE243553 peaksets, of any kind, exists anywhere in this repository. W20b named this as its secondary successor and did not run it.

---

## Prior-work check

Commands run against the tracked corpus (all read-only):

```
git ls-files | rg -i "gse243553|peakset|jaccard"
```
→ 7 paths: `research/manuscripts/fusion-output/gse243553-eno3-overlap-2026-08-08.md`, the four `research/modalities/gse243553-eno3-overlap*.json` artifacts, `research/modalities/gse243553_eno3_overlap.py`, `research/modalities/tests/test_gse243553_eno3_overlap.py`. **No `.bed` file is tracked anywhere.**

```
rg -n -i "jaccard" --glob '!.git' -l | head -20
```
→ 20 files, all NR4A3-degrader / modality documents; W20b already established these are text-shingle dedup and gene-set Jaccards, unrelated to peaksets.

```
rg -n -i "jaccard" --glob '!.git' research/modalities/gse243553* \
   research/manuscripts/fusion-output/gse243553-eno3-overlap-2026-08-08.md
```
→ **no matches.** No Jaccard, pairwise or otherwise, has ever been computed on GSE243553 material in this repository outside W20b's in-response draft.

```
rg -n -i "shares.?5|5-prime|five.?prime|partner.?class|cluster by partner" --glob '!.git' -l
rg -n -i "496 pairs|panel-wide|5.{0,3}vs.{0,3}3" --glob '!.git' -l
```
→ hits are fusion-partner *stratification* and *pooling* documents about clinical/expression partner effects, plus degrader/ASO design text. **None compares peak locations, and none asks the 5′-vs-3′ clustering question.**

**Closed items I confirmed I am not replaying** (`CLOSED-WORK.md`, item by item): no clinical, registry, methylation, promoter-transfer, inverse-bound, Hofvander/EGA, Brenca-case-identity, GSE4303/GSE28866, pazopanib/anthracycline/sunitinib/trabectedin/Wagner/CTARC or SEER material is used; no cohort is invented; lane 11 source-index work is untouched; the restricted NR4A Perspective review is not recreated under any label. I am not replaying W19's Q-NR4A2-COVERAGE — **lane 19's question is closed and I did not reopen it.** I am not re-running W20's `TAF15` refutation, which stands unchanged with its power caveat.

---

## Method / inputs

**Inputs — both committed, both read-only:**

| Input | Path | Field used |
|---|---|---|
| Coordinate prefixes | `research/modalities/gse243553-eno3-overlap-supplement.json` | `contents['SPRINGER::3::zip']['first_bytes']` → ≤600-byte verbatim BED prefix per peakset |
| Peak counts | `research/modalities/gse243553-eno3-overlap.json` | `peakset_inventory[*].n_intervals`, `.median_width` |

Deposit **GSE243553**, primary publication doi `10.1038/s41587-024-02347-4`; 128 fusion oncoproteins expressed in one HEK293T background. Assembly **hg38**, established by the deposit's own `!Sample_data_processing: Assembly: hg38`. **The intervals are the authors' own marker calls — this repository called no peak.**

**Tools:** Python 3.11.15, standard library only (`json`, `itertools`, `math`, `random`, `statistics`). No third-party package, no network, no GPU, no paid API.

**Substrate rebuilt from scratch, not inherited.** I re-parsed the prefixes myself, discarding the trailing partial line, keeping only `chr1` records, and I re-checked both preconditions that make the windowed Jaccard exact rather than approximate.

**Pair statistic.** For peaksets A, B: `W = min(last retained chr1 end of A, of B)`; restrict both to `chr1:0–W`; Jaccard over exact interval identity. Because both prefixes are coordinate-sorted, **each set is complete inside that window**, so the Jaccard is exact *for that window*. A pair is **non-degenerate** iff both sides hold ≥1 interval in the window; the primary analysis set is the non-degenerate pairs.

**Pair classes**, from the peakset name split on the first `-`: **SHARES-5** (same 5′, different 3′), **SHARES-3** (same 3′, different 5′), **SHARES-BOTH** (same both), **SHARES-CROSS** (a gene shared but in opposite positions — broken out so it cannot contaminate the neither class), **SHARES-NEITHER**. Declared floor: **a class with fewer than 4 non-degenerate pairs is TOO SMALL TO TEST** and is reported descriptively only.

### Comparison and null, stated before running

Both are fixed in the script's docstring, which is the preregistration; every verdict string below is emitted by the script, not typed by me.

- **Null: permutation over gene labels.** Shuffle which peakset carries which `(5′ gene, 3′ gene)` name, holding fixed the 32 peaksets, their interval data, the full pair set, and — automatically, because the label multiset is permuted as a whole — **every class size**. This destroys only the association between partner identity and peak location, which is exactly the hypothesis under test. **Why this and not something else:** resampling peaksets would change the panel, which is the fixed object of study; and no parametric or i.i.d. test is admissible here because the pair statistics are strongly dependent (each peakset appears in 31 pairs). 50,000 permutations, seed `20260908`, one-sided high, `p = (1 + #{perm ≥ obs}) / (1 + n_perm)`.
- **Density control, carried forward from W20b.** `d(A,B) = |log₁₀ n_intervals(A) − log₁₀ n_intervals(B)|`. Bin the non-degenerate pairs into **quintiles of d**, and define the residual `r(A,B) = J(A,B) − mean(J within that pair's quintile)`. **The primary statistic for each class is the mean residual**; raw mean J is reported alongside. The binning depends only on the peakset pair, never on gene labels, so it is invariant under the null — which is what makes residualising legitimate here rather than circular.
- **Decision rule:** a class **PREDICTS LOCATION** iff its mean-residual p ≤ 0.05.
- **Arms:** ARM 1 full panel (32 peaksets, 496 pairs); **ARM 2 leave-NR4A3-out** (28 peaksets, 378 pairs).
- **Negative control, actually run:** a biologically meaningless label — peakset name's first letter in A–M vs N–Z — pushed through the identical machinery and the identical permutation null.
- **Replication gate, run first:** reproduce W20b's reported numbers from my own rebuild before extending. A discrepancy is the most important finding.

---

## Result

### 0. Substrate rebuild — reproduced

| Quantity | This run | W20b | Row type |
|---|---|---|---|
| `peakset_inventory` entries | 128 | 128 | PRIMARY |
| Real `Supp_Data_1_new/*.bed` peaksets | 32 | 32 | PRIMARY |
| `__MACOSX` AppleDouble forks | 64 | 64 | PRIMARY |
| Real `Supp_Data_2` non-interval tables | 32 | 32 | PRIMARY |
| Peaksets with retained chr1 prefixes | 32 | 32 | PRIMARY |
| All prefixes ascending-sorted | **True** | True | PRIMARY |
| Distinct interval widths in retained data | **{500}** only | 500 bp fixed | PRIMARY |
| `median_width` across 32 peaksets | single value 500, **sd = 0.0** | sd = 0.0 | PRIMARY |
| Retained chr1 intervals per peakset | min 4, median 26, max 28 | min 4, median 26, max 28 | PRIMARY |
| `n_intervals` across 32 | min 22, median 1651, max 13692 | min 22, median 1651, max 13692 | PRIMARY |
| All 496 pairs / non-degenerate | 496 / **376** | 496 / 376 | PRIMARY |
| Non-degenerate pairs sharing ≥1 interval | **65** | 65 | PRIMARY |
| Background over 376: mean / median / max J | **0.0159 / 0.0000 / 0.4118** | 0.0159 / 0.0000 / 0.4118 | PRIMARY |

The sortedness precondition and the fixed-500 bp width are the two facts that make the windowed Jaccard *exact* rather than an estimate; I verified both directly rather than accepting them.

### 1. Replication gate — two apparent discrepancies, both diagnosed to a definite cause; W20b's science stands

The gate printed `DISCREPANCY - INVESTIGATE`. I chased both. **Neither is an error in W20b, and neither changes any conclusion.**

**Discrepancy 1 — mine, not W20b's.** My first counter reported "Supp_Data_2 non-interval tables: 64", against W20b's 32. The counters overlapped: `__MACOSX` contains forks of *both* directories. The disjoint partition is **32 real BED + 32 real `Supp_Data_2` tables + 64 forks (32 + 32) = 128**, exactly W20b's characterisation. **My counter double-counted; W20b is correct.** The load-bearing fact survives intact: *a count of "128 fusions" from `peakset_inventory` is wrong by a factor of four.*

**Discrepancy 2 — a genuine convention difference, isolated exactly.** My default treated a degenerate pair inside a four-subset as J = 0; W20b's group mean **drops** degenerate pairs. Running both conventions side by side on the identical substrate:

| Convention for a degenerate pair inside the group mean | Null mean J | Uncond. p | Density-matched n | Cond. null mean | **Cond. p** |
|---|---|---|---|---|---|
| Counted as J = 0 (my default) | 0.0121 | 0.0001 | 5102 | 0.0270 | **0.0010** |
| **Dropped from the mean (W20b)** | **0.0160** | **0.0013** | **5102** | **0.0273** | **0.0010** |
| **W20b as reported** | **0.0160** | **0.0013** | **5102** | **0.0273** | **0.0010** |

W20b's row reproduces **digit-for-digit** under its own stated convention. The NR4A3 quartet has all 6 pairs non-degenerate, so the observed statistic is 0.1994 either way; `D(log₁₀ n) = 0.4754`, low-tail exact p = **0.1419**, null mean D = **0.8940**, and the 5,102 density-matched subsets all reproduce exactly. All six per-pair Jaccards match W20b's table to four decimals (0.3750, 0.2414, 0.1786, 0.1515, 0.1429, 0.1071, with identical windows and shared counts).

**W20b's convention is the more conservative of the two** (it raises the null mean 0.0121 → 0.0160 and the unconditional p 0.0001 → 0.0013), and the density-matched p — the one W20b said to quote — is **0.0010 under both**. My panel-wide analysis below restricts to non-degenerate pairs, i.e. the same convention. **Verdict: W20b is reproduced. Its numbers, its correction and its verdicts stand unchanged.** The only substantive addition is that its convention should be stated explicitly, because the alternative moves the unconditional p by an order of magnitude.

### 2. Pair-class census (PRIMARY)

Panel structure: 5′ multiplicities are `EWSR1 × 13`, `FUS × 3`, and 16 singletons. 3′ multiplicities >1 are `NR4A3 × 4`, `ATF1 × 2`, `DDIT3 × 2`, `FEV × 2`, `PHF1 × 2`.

| Class | Pairs (all 496) | Pairs (non-degenerate) | Testable at declared floor n ≥ 4? |
|---|---|---|---|
| SHARES-5 | 81 | 66 | yes |
| SHARES-3 | 10 | 10 | yes |
| SHARES-BOTH | **0** | 0 | **no — the class is empty by construction** (peakset names are unique) |
| SHARES-CROSS | **0** | 0 | no — no gene appears on both sides anywhere in this panel |
| SHARES-NEITHER | 405 | 300 | reference class |

**SHARES-BOTH cannot be tested and never could be**: two peaksets sharing both partners would be the same fusion. The dispatch's four-way classification collapses to three real classes in this panel, and I say so rather than testing an empty cell.

### 3. ARM 1 — full panel, 32 peaksets, 376 non-degenerate pairs (PRIMARY)

Density quintile mean J, confirming the confound is real and monotone: **Q1 = 0.0387, Q2 = 0.0163, Q3 = 0.0126, Q4 = 0.0110, Q5 = 0.0014** (n = 75/75/75/75/76). Similar-density pairs share ~28× more of their peaks than the most dissimilar. Residualising against this is not optional.

| Class | n | mean J | median J | **mean residual** | median window depth | perm p (one-sided) | Verdict (script-emitted) |
|---|---|---|---|---|---|---|---|
| **SHARES-3** | 10 | **0.1715** | 0.1591 | **+0.1513** | 6.5 | **0.00008** | **PREDICTS LOCATION** |
| SHARES-5 | 66 | 0.0300 | 0.0000 | +0.0094 | 8.5 | 0.09782 | does NOT predict location |
| SHARES-NEITHER | 300 | 0.0077 | 0.0000 | −0.0071 | 5.0 | — (reference) | — |

Units: Jaccard is dimensionless, over the pair-specific `chr1:0–W` window. Uncertainty is the 50,000-draw gene-label permutation distribution over these same 32 peaksets, and extends no further.

**The panel clusters by 3′ partner, not by 5′ partner.** SHARES-3 sits ~20× the SHARES-NEITHER mean and clears the threshold by three orders of magnitude. SHARES-5 is directionally positive (+0.0094) but **does not clear 0.05** at n = 66 — a class six times larger than SHARES-3, so this is not a power problem in the obvious direction. Note its median J is 0.0000: most pairs sharing a 5′ gene share no peak at all.

### 4. ARM 2 — leave-NR4A3-out, 28 peaksets, 277 non-degenerate pairs (PRIMARY) — the decisive arm

| Class | n | mean J | median J | **mean residual** | median window depth | perm p | Verdict (script-emitted) |
|---|---|---|---|---|---|---|---|
| **SHARES-3** | **4** | **0.1296** | 0.1333 | **+0.1105** | 5.0 | **0.01486** | **PREDICTS LOCATION** |
| SHARES-5 | 56 | 0.0353 | 0.0000 | +0.0124 | 9.0 | 0.08302 | does NOT predict location |
| SHARES-NEITHER | 217 | 0.0106 | 0.0000 | −0.0053 | 5.0 | — | — |

**With every NR4A3 fusion removed, 3′ sharing still predicts location.** The four surviving pairs, each individually far above a panel background whose median is 0.0000:

| Pair | 3′ gene | J | Window | \|A\| | \|B\| | shared | n_intervals |
|---|---|---|---|---|---|---|---|
| EWSR1-ATF1 · FUS-ATF1 | ATF1 | 0.1852 | chr1:0–57,518,299 | 26 | 6 | 5 | 1363 / 251 |
| EWSR1-FEV · FUS-FEV | FEV | 0.1667 | chr1:0–24,295,259 | 15 | 27 | 6 | 2658 / 3728 |
| EWSR1-DDIT3 · FUS-DDIT3 | DDIT3 | 0.1000 | chr1:0–229,557,880 | 3 | 19 | 2 | 22 / 151 |
| EPC1-PHF1 · MEAF6-PHF1 | PHF1 | 0.0667 | chr1:0–219,310,741 | 4 | 12 | 1 | 42 / 150 |

Leave-one-pair-out means: **0.1506, 0.1111, 0.1395, 0.1173** — no single pair carries the result.

**Honesty about n = 4.** This class sits *exactly* at my pre-declared floor, not comfortably above it. Four pairs is a thin instrument, and the p-value's precision (0.015) far exceeds the evidence's precision. What raises it above a curiosity is that **all four are positive, all four exceed the class-3 threshold independently, leave-one-out is stable, and three of the four are `EWSR1-X` vs `FUS-X`** — a natural internal replicate, since EWSR1 and FUS are both FET-family 5′ partners. That last point cuts both ways and I state it as a caveat, not a bonus: three of the four non-NR4A3 SHARES-3 pairs differ only by an EWSR1↔FUS swap, so ARM 2 is closer to *"swapping one FET partner for another FET partner barely moves peak location"* than to a general statement about arbitrary 5′ partners. The `EPC1-PHF1 · MEAF6-PHF1` pair is the only one outside that pattern, and it is the weakest of the four (J = 0.0667).

### 5. Negative control — behaved as a control (PRIMARY)

Meaningless label (name's first letter A–M vs N–Z), identical machinery and null:

| Pseudo-class | n | mean J | mean residual | perm p | Verdict |
|---|---|---|---|---|---|
| AM-BUCKET | 242 | 0.0190 | +0.0031 | **0.10300** | **does NOT predict location** |
| complement | 134 | 0.0104 | −0.0055 | — | — |

The control is mildly positive in the raw mean and **does not reach significance** — which is the correct behaviour, and it also shows the machinery does not manufacture significance from a large class with a slight imbalance.

### 6. What this answers

**ASSOCIATION, and the ordering is the finding.**

> Across the whole GSE243553 panel, location similarity is predicted by **sharing a 3′ partner** (p = 0.00008) and **not** by sharing a 5′ partner (p = 0.098). The 3′ effect **survives deleting every NR4A3 fusion** (p = 0.015, n = 4).

This **generalises W20b's single-quartet result into a panel-level property** rather than leaving it as a fact about NR4A3: W20b's alternative reading — "this is specific to NR4A3" — is **not** what the data show, though the leave-out arm rests on four pairs and three of those are FET↔FET swaps. Mechanistically it is consistent with the 3′ moiety carrying the DNA-binding function that decides *where* a fusion goes, while the 5′ moiety (in this panel, overwhelmingly a FET-family activation domain) decides something else. **That is a hypothesis this result is consistent with, not a mechanism this result establishes.**

**PREDICTION rows: none.** No model output, extrapolation or projection appears in this report.

**Additional PRIMARY findings:**
1. **SHARES-BOTH and SHARES-CROSS are empty classes in this panel** — 0 pairs each, by construction. The dispatch's four-way split is a three-way split here.
2. **The density confound is monotone across the full panel**, not just near the NR4A3 quartet: 0.0387 → 0.0014 across quintiles of `|Δlog₁₀ n|`. Any future GSE243553 pairwise work that skips this control will overstate its effect.
3. **W20b's degenerate-pair convention is load-bearing for its unconditional p** (0.0013 vs 0.0001) and irrelevant to its density-matched p (0.0010 both ways). The density-matched figure is the robust one, as W20b said.

**UNKNOWN, preserved from the source.** Wild-type `NR4A3` and reciprocal `NR4A3-EWSR1` have **no marker BED in the supplement at all**. Per `controls.⚠_how_to_read_a_missing_file`, the correct reading is *"the fusion arms have interval sets and the two controls have none"* — **not** that they were tested and came back empty. I could not include them and assert no zero for them.

---

## Validation evidence

All **RUN**. Nothing in this report is `PROPOSED (NOT RUN)`.

**RUN — command 1** (environment and budget gate)
```
date -u; env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I' | sort
cd /home/user/Rare-cancers && git rev-parse HEAD && git status --porcelain | head
python3 --version; df -h / | tail -1
```
→ `Python 3.11.15`; `/dev/vda 252G 14G used 24G avail 36%` (≥10 GiB satisfied); HEAD `103ff76f…`; only untracked coordinator report paths. **Exit 0.**

**RUN — command 2** (main analysis; full source below)
```
cd /tmp/claude-0/w19c && python3 --version && time python3 partner_class_clustering.py; echo "EXIT=$?"
```
Environment: Python 3.11.15, stdlib only, no network. Wall clock `real 0m9.155s`. **`EXIT=0`.** Verbatim output is quoted in full across §0–§5 above; the key script-emitted verdict lines are:
```
REPLICATION VERDICT: DISCREPANCY - INVESTIGATE
  SHARES-5        obs mean residual +0.0094   perm null mean -0.0000   one-sided p = 0.09782   -> does NOT predict location
  SHARES-3        obs mean residual +0.1513   perm null mean +0.0000   one-sided p = 0.00008   -> PREDICTS LOCATION
  SHARES-5        obs mean residual +0.0124   perm null mean -0.0000   one-sided p = 0.08302   -> does NOT predict location
  SHARES-3        obs mean residual +0.1105   perm null mean +0.0003   one-sided p = 0.01486   -> PREDICTS LOCATION
  AM-BUCKET       obs mean residual +0.0031   perm null mean -0.0000   one-sided p = 0.10300   -> does NOT predict location
```

**RUN — command 3** (discrepancy diagnosis)
```
cd /tmp/claude-0/w19c && python3 discrepancy.py; echo "EXIT=$?"
```
**`EXIT=0`.** Verbatim output quoted in §1.

**RUN — command 4** (per-pair detail and ARM-2 leave-one-out)
```
cd /tmp/claude-0/w19c && python3 detail.py; echo "EXIT=$?"
```
**`EXIT=0`.** Verbatim output quoted in §2 and §4.

**RUN — command 5** (end-state check)
```
date -u; cd /home/user/Rare-cancers && git status --porcelain | wc -l && git rev-parse HEAD && ls /tmp/claude-0/w19c
```
→ `2` untracked coordinator paths; HEAD `b9a0257e…`; three `.py` files, all under `/tmp/claude-0/w19c/`. **No repository file was created, modified or deleted by me. No git write of any kind.**

### Code (returned inline, not written into the tree)

`/tmp/claude-0/w19c/partner_class_clustering.py` — the docstring is the preregistration and was written before execution:

```python
"""
W19c - GSE243553 panel-wide 5' vs 3' partner clustering.

PRE-DECLARED BEFORE EXECUTION (this docstring is the preregistration; the
verdict strings below are emitted by the script, not written by hand).

SUBSTRATE
  32 real *_markers.bed peaksets from
  research/modalities/gse243553-eno3-overlap-supplement.json
  contents['SPRINGER::3::zip']['first_bytes'] (<=600-byte verbatim BED prefix,
  hg38, authors' own marker calls).  Peak counts from
  research/modalities/gse243553-eno3-overlap.json peakset_inventory.
  Preconditions checked and printed: (a) all prefixes coordinate-sorted
  ascending, (b) all retained intervals exactly 500 bp, (c) trailing partial
  line discarded, (d) only chr1 intervals retained.

PAIR STATISTIC
  For peaksets A,B: W = min(last retained chr1 end of A, of B).  Restrict both
  to chr1:0-W.  Because both prefixes are sorted, each set is COMPLETE inside
  that window, so Jaccard over chr1:0-W is exact for that window.
  A pair is NON-DEGENERATE iff both sides hold >=1 interval in the window.
  Primary analysis set = non-degenerate pairs only.

PAIR CLASSES (from the peakset name split on the first '-': 5' gene, 3' gene)
  SHARES-5   same 5' gene, different 3' gene
  SHARES-3   same 3' gene, different 5' gene
  SHARES-BOTH  same 5' and same 3' gene
  SHARES-CROSS a gene shared but in opposite positions (reported separately so
               it does not contaminate SHARES-NEITHER)
  SHARES-NEITHER  no gene in common
  A class with fewer than 4 non-degenerate pairs is declared TOO SMALL TO TEST
  and is reported descriptively only.

DENSITY CONTROL (W20b showed peak-count similarity inflates Jaccard)
  d(A,B) = |log10 n_intervals(A) - log10 n_intervals(B)|.
  Over the non-degenerate pair set, bin pairs into QUINTILES of d and define
  residual r(A,B) = J(A,B) - mean(J within that pair's quintile).
  PRIMARY statistic for each class = mean residual r.  Raw mean J reported too.
  The binning depends only on the peakset pair, never on gene labels, so it is
  invariant under the null below.

NULL (chosen and stated before running)
  Permutation over GENE LABELS: shuffle which peakset carries which
  (5' gene, 3' gene) name, keeping the 32 peaksets, their interval data, the
  full pair set and every class size exactly as observed.  This destroys only
  the association between partner identity and peak location, which is the
  hypothesis under test.  It is preferred over resampling peaksets (which would
  change the panel) and over a parametric test (pair statistics are strongly
  dependent - every peakset appears in 31 pairs - so no i.i.d. test is valid).
  50,000 permutations, seed 20260908, one-sided (high).  Monte-Carlo p reported
  as (1 + #{perm >= obs}) / (1 + n_perm).

DECISION RULE
  A class PREDICTS LOCATION iff its mean residual p <= 0.05.

ARMS
  ARM 1  full panel, 32 peaksets, 496 pairs.
  ARM 2  leave-NR4A3-out: drop the 4 *-NR4A3 peaksets, 28 peaksets, 378 pairs.
         Separates "3' sharing predicts location in general" from "the NR4A3
         quartet is doing all the work".

NEGATIVE CONTROL (actually run)
  A biologically meaningless label: peakset name's first letter in A-M vs N-Z.
  Pairs sharing a bucket are the pseudo-class.  Tested with the identical
  machinery and the identical permutation null.  Expected: not significant.

REPLICATION GATE
  Before any of the above, reproduce W20b's reported numbers from scratch:
  32 real peaksets / 64 AppleDouble / 32 non-interval tables; median_width
  constant 500; NR4A3-quartet mean Jaccard 0.1994, exact p 0.0013 over all
  C(32,4)=35960 subsets, density-matched p 0.0010; Analysis A D=0.4754 p=0.1419.
  Any discrepancy is reported as the most important finding.
"""
import json, itertools, math, random, statistics, sys

REPO = "/home/user/Rare-cancers"
SUP = REPO + "/research/modalities/gse243553-eno3-overlap-supplement.json"
INV = REPO + "/research/modalities/gse243553-eno3-overlap.json"

# ---------- substrate ----------
sup = json.load(open(SUP))
fb = sup["contents"]["SPRINGER::3::zip"]["first_bytes"]
inv = json.load(open(INV))["peakset_inventory"]

n_macosx = sum(1 for k in inv if "__MACOSX" in k)
n_sd2 = sum(1 for k in inv if "Supp_Data_2" in k)
real_inv = {k: v for k, v in inv.items()
            if "__MACOSX" not in k and "Supp_Data_1_new/" in k and k.endswith(".bed")}
print("peakset_inventory entries        :", len(inv))
print("  __MACOSX AppleDouble forks     :", n_macosx)
print("  Supp_Data_2 non-interval tables:", n_sd2)
print("  REAL BED peaksets              :", len(real_inv))

widths = sorted({v["median_width"] for v in real_inv.values()})
print("median_width distinct values across real peaksets:", widths,
      " sd =", round(statistics.pstdev([v["median_width"] for v in real_inv.values()]), 4))

def parse_prefix(s):
    lines = s.split("\n")
    if not s.endswith("\n"):
        lines = lines[:-1]          # discard trailing partial line
    out = []
    for ln in lines:
        p = ln.split("\t")
        if len(p) < 3 or p[0] != "chr1":
            continue
        try:
            out.append((int(p[1]), int(p[2])))
        except ValueError:
            continue
    return out

peaks, names = {}, []
for k, s in fb.items():
    if "__MACOSX" in k or not k.endswith("_markers.bed"):
        continue
    nm = k.split("/")[-1][: -len("_markers.bed")]
    iv = parse_prefix(s)
    peaks[nm] = iv
    names.append(nm)
names.sort()
print("peaksets with retained chr1 prefixes:", len(names))

sorted_ok = all(all(peaks[n][i][0] <= peaks[n][i+1][0] for i in range(len(peaks[n])-1)) for n in names)
w500 = {e - s for n in names for (s, e) in peaks[n]}
depths = sorted(len(peaks[n]) for n in names)
print("PRECONDITION all prefixes ascending-sorted:", sorted_ok)
print("PRECONDITION interval widths present      :", sorted(w500))
print("retained chr1 intervals per peakset: min %d median %d max %d" %
      (depths[0], statistics.median(depths), depths[-1]))

nint = {}
for k, v in real_inv.items():
    nm = k.split("/")[-1][: -len("_markers.bed")]
    nint[nm] = v["n_intervals"]
vals = sorted(nint[n] for n in names)
print("n_intervals across 32: min %d median %d max %d" % (vals[0], statistics.median(vals), vals[-1]))
assert set(nint) == set(names), "inventory / prefix name mismatch"

# ---------- pair statistic ----------
def jac(a, b):
    A, B = peaks[a], peaks[b]
    if not A or not B:
        return None
    W = min(A[-1][1], B[-1][1])
    SA = {iv for iv in A if iv[1] <= W}
    SB = {iv for iv in B if iv[1] <= W}
    if not SA or not SB:
        return None
    return len(SA & SB) / len(SA | SB), W, len(SA), len(SB), len(SA & SB)

J, meta = {}, {}
for a, b in itertools.combinations(names, 2):
    r = jac(a, b)
    if r is None:
        J[(a, b)] = None
    else:
        J[(a, b)] = r[0]; meta[(a, b)] = r[1:]
tot = len(J); nondeg = [p for p in J if J[p] is not None]
print("all unordered pairs: %d   non-degenerate window: %d   degenerate: %d"
      % (tot, len(nondeg), tot - len(nondeg)))
nz = [p for p in nondeg if J[p] > 0]
print("non-degenerate pairs sharing >=1 interval: %d   mean J %.4f  median J %.4f  max J %.4f"
      % (len(nz), statistics.mean(J[p] for p in nondeg),
         statistics.median(J[p] for p in nondeg), max(J[p] for p in nondeg)))

# ---------- REPLICATION GATE: W20b ----------
print("\n=== REPLICATION GATE (W20b) ===")
QUART = ["EWSR1-NR4A3", "TAF15-NR4A3", "TCF12-NR4A3", "TFG-NR4A3"]
def key(a, b): return (a, b) if (a, b) in J else (b, a)
def grpJ(g):
    vs = [J[key(a, b)] or 0.0 for a, b in itertools.combinations(g, 2)]
    return statistics.mean(vs)
def grpD(g):
    vs = [abs(math.log10(nint[a]) - math.log10(nint[b])) for a, b in itertools.combinations(g, 2)]
    return statistics.mean(vs)
obsJ, obsD = grpJ(QUART), grpD(QUART)
allsub = list(itertools.combinations(names, 4))
nullJ = [grpJ(g) for g in allsub]; nullD = [grpD(g) for g in allsub]
pJ = sum(1 for v in nullJ if v >= obsJ) / len(allsub)
pD = sum(1 for v in nullD if v <= obsD) / len(allsub)
cond = [nullJ[i] for i in range(len(allsub)) if nullD[i] <= obsD]
pJc = sum(1 for v in cond if v >= obsJ) / len(cond)
print("subsets enumerated C(32,4)      : %d" % len(allsub))
print("NR4A3 quartet mean Jaccard      : %.4f   (W20b 0.1994)" % obsJ)
print("  exact one-sided p, high tail  : %.4f   (W20b 0.0013)" % pJ)
print("  null mean Jaccard             : %.4f   (W20b 0.0160)" % statistics.mean(nullJ))
print("  density-matched subsets       : %d      (W20b 5102)" % len(cond))
print("  density-matched null mean     : %.4f   (W20b 0.0273)" % statistics.mean(cond))
print("  density-matched p             : %.4f   (W20b 0.0010)" % pJc)
print("NR4A3 quartet D(log10 n)        : %.4f   (W20b 0.4754)" % obsD)
print("  exact one-sided p, low tail   : %.4f   (W20b 0.1419)" % pD)
print("  null mean D                   : %.4f   (W20b 0.8940)" % statistics.mean(nullD))
ok = (abs(obsJ-0.1994)<5e-4 and abs(pJ-0.0013)<1e-4 and abs(pJc-0.0010)<1e-4
      and abs(obsD-0.4754)<5e-4 and abs(pD-0.1419)<1e-4 and len(cond)==5102)
print("REPLICATION VERDICT:", "REPRODUCED" if ok else "DISCREPANCY - INVESTIGATE")

# ---------- classification ----------
def split(nm):
    i = nm.index("-"); return nm[:i], nm[i+1:]
G = {n: split(n) for n in names}
def cls(a, b):
    a5, a3 = G[a]; b5, b3 = G[b]
    if a5 == b5 and a3 == b3: return "SHARES-BOTH"
    if a5 == b5: return "SHARES-5"
    if a3 == b3: return "SHARES-3"
    if a5 == b3 or a3 == b5: return "SHARES-CROSS"
    return "SHARES-NEITHER"

# ---------- test machinery ----------
def analyse(sub, tag, labelfn=cls, classes=("SHARES-5", "SHARES-3"), nperm=50000, seed=20260908):
    print("\n=== %s ===" % tag)
    sub = sorted(sub); idx = {n: i for i, n in enumerate(sub)}
    pairs = [(a, b) for a, b in itertools.combinations(sub, 2)]
    good = [(a, b) for a, b in pairs if J[key(a, b)] is not None]
    print("peaksets %d   pairs %d   non-degenerate %d" % (len(sub), len(pairs), len(good)))
    d = {p: abs(math.log10(nint[p[0]]) - math.log10(nint[p[1]])) for p in good}
    order = sorted(good, key=lambda p: d[p])
    q = max(1, len(order)//5); bin_of = {}
    for i, p in enumerate(order): bin_of[p] = min(4, i//q)
    bmean = {}
    for bnum in range(5):
        vs = [J[key(*p)] for p in good if bin_of[p] == bnum]
        bmean[bnum] = statistics.mean(vs) if vs else 0.0
    print("density quintile mean J (by |dlog10 n|): " +
          "  ".join("Q%d=%.4f(n=%d)" % (b+1, bmean[b], sum(1 for p in good if bin_of[p]==b)) for b in range(5)))
    R = {p: J[key(*p)] - bmean[bin_of[p]] for p in good}
    # observed
    obs_cls = {p: labelfn(*p) for p in good}
    counts = {}
    for p in pairs:
        c = labelfn(*p); counts[c] = counts.get(c, 0) + 1
    print("pair-class counts (all pairs)      :", dict(sorted(counts.items())))
    gcounts = {}
    for p in good:
        gcounts[obs_cls[p]] = gcounts.get(obs_cls[p], 0) + 1
    print("pair-class counts (non-degenerate) :", dict(sorted(gcounts.items())))
    for c in sorted(gcounts):
        vs = [J[key(*p)] for p in good if obs_cls[p] == c]
        rs = [R[p] for p in good if obs_cls[p] == c]
        dp = [min(meta[key(*p)][1], meta[key(*p)][2]) for p in good if obs_cls[p] == c]
        print("  %-15s n=%3d  mean J %.4f  median J %.4f  mean residual %+.4f  median window depth %.1f"
              % (c, len(vs), statistics.mean(vs), statistics.median(vs), statistics.mean(rs),
                 statistics.median(dp)))
    # permutation
    rng = random.Random(seed)
    labels = list(sub)
    res = {c: [] for c in classes}
    obsstat = {}
    for c in classes:
        vs = [R[p] for p in good if obs_cls[p] == c]
        obsstat[c] = statistics.mean(vs) if vs else None
    goodidx = [(idx[a], idx[b], R[(a, b)]) for a, b in good]
    for _ in range(nperm):
        rng.shuffle(labels)
        acc = {c: [0.0, 0] for c in classes}
        for i, j, r in goodidx:
            c = labelfn(labels[i], labels[j])
            if c in acc:
                acc[c][0] += r; acc[c][1] += 1
        for c in classes:
            res[c].append(acc[c][0] / acc[c][1] if acc[c][1] else 0.0)
    out = {}
    for c in classes:
        n = gcounts.get(c, 0)
        if n < 4:
            print("  %-15s TOO SMALL TO TEST (n=%d non-degenerate pairs < 4) - descriptive only" % (c, n))
            out[c] = None; continue
        p = (1 + sum(1 for v in res[c] if v >= obsstat[c])) / (1 + nperm)
        verdict = "PREDICTS LOCATION" if p <= 0.05 else "does NOT predict location"
        print("  %-15s obs mean residual %+.4f   perm null mean %+.4f   one-sided p = %.5f   -> %s"
              % (c, obsstat[c], statistics.mean(res[c]), p, verdict))
        out[c] = p
    return out

# ARM 1
a1 = analyse(names, "ARM 1 - FULL PANEL (32 peaksets)")
# ARM 2
noq = [n for n in names if not n.endswith("-NR4A3")]
a2 = analyse(noq, "ARM 2 - LEAVE-NR4A3-OUT (28 peaksets)")
# negative control
def ctrl(a, b):
    return "AM-BUCKET" if (a[0] <= "M") == (b[0] <= "M") else "SHARES-NEITHER"
a3 = analyse(names, "NEGATIVE CONTROL - alphabetical bucket (meaningless label)",
             labelfn=ctrl, classes=("AM-BUCKET",))
print("\nDONE")
```

`discrepancy.py` and `detail.py` are short diagnostic scripts whose full verbatim output is quoted in §1, §2 and §4; both re-parse the same two JSON inputs with the identical `parse`/`jac` functions shown above and add no new statistic beyond the two conventions table, the class census and the leave-one-out means.

---

## Limitations

**Carried forward from W20b without softening:**

- **The window is a sliver of one chromosome.** Every comparison happens inside `chr1:0` to at most ~53.7 Mb for the NR4A3 pairs — roughly **0.4% of the genome at the median**. The retained data is a byte-truncated prefix, so the tested region is not a random genomic sample: it is **the proximal end of chr1, selected by nothing but sort order**. Whether the 3′-clustering property holds genome-wide is **UNKNOWN**. This raises a prior; it does not settle anything.
- **Depths are 4–27 intervals per side** (median window depth 5–9 by class). A single shared or unshared 500 bp window moves a pair's Jaccard by several points. The permutation null protects the p-value against distributional error, not against the thinness of the underlying counts.
- **Windows are pair-dependent.** The Jaccards are not measured over one common region, so they are not interchangeable estimates of a single quantity. The class means are means over heterogeneous windows — and the null was computed the same way, which is what keeps the comparison fair, not what makes the windows comparable.
- **HEK293T is not EMC.** All fusions were expressed in one embryonic-kidney background. That is exactly what makes the panel internally controlled and exactly why nothing here transfers to chondroid tissue, a patient tumour, or disease behaviour. A fusion's accessible chromatin in HEK293T is not its cistrome in EMC.
- **These are the authors' marker calls at a threshold this repository did not set** and cannot re-tune. A peakset's size reflects that pipeline as much as the fusion's biology.
- **The density confound is real and monotone** and the residualised figures are the ones to quote.

**New to this arm:**

- **ARM 2 rests on four pairs**, exactly at my declared floor. It is a real test with a real p-value and it is a thin one. Do not quote 0.015 as if it carried the precision of the ARM-1 figure.
- **Three of ARM 2's four pairs are `EWSR1-X` vs `FUS-X`.** The honest reading is closer to *"swapping one FET 5′ partner for another barely moves peak location"* than to a general claim about arbitrary 5′ partners. Only `EPC1-PHF1 · MEAF6-PHF1` sits outside that pattern, and it is the weakest pair.
- **The 5′ negative is a negative in this panel, not in general.** SHARES-5 is 81 pairs of which 78 are `EWSR1-*`, so "5′ sharing" is almost synonymous with "both are EWSR1 fusions". A panel with a different 5′ composition could give a different answer.
- **SHARES-BOTH is empty and untestable** — the dispatch's four-way classification cannot be completed on this panel by any amount of effort.
- **Monte-Carlo, not exact.** ARM 1's `p = 0.00008` is `1/50001`-limited; it means "smaller than the resolution of 50,000 draws", not a precise value.
- **Nothing here bears on efficacy, safety, selectivity, therapeutic window, potency, dosing or clinical readiness** of any agent, target or gene; no such quantity was computed. No reagent was designed. There is no wet lab. **An association in a heterologous cell line is not a statement about EMC tissue or about disease identity**, and I make no disease-identity claim.
- **The genome-wide interval sets remain unrecovered** behind a 403 CONNECT policy denial that I did not test or route around: GSE243553 supplementary `MOESM3_ESM.zip`, `Supp_Data_1_new/*_markers.bed`.

---

## Stop condition

**Set in advance:** an executed panel-wide 5′-vs-3′ clustering test with a pre-declared null, a density control, and a leave-NR4A3-out arm — reporting a null result with equal willingness.

**MET.** All three ran to exit 0 against a rule fixed before execution. The density control is in the primary statistic, not bolted on. The negative control was actually run and was correctly non-significant (p = 0.103). The leave-out arm was run and reported with its n = 4 stated plainly rather than buried. **One of the two hypotheses returned a null and is reported as a null**: 5′ sharing does not predict location, in either arm (p = 0.098, 0.083). And the replication gate produced its own finding — W20b reproduces exactly, with its degenerate-pair convention identified as the thing that moves its unconditional p by an order of magnitude.

---

## Tool-call and wall-clock count actually used

**11 tool calls. Wall clock 02:15:15Z → 02:18:00Z ≈ 3 minutes** (well inside the ~40 min / ~40 call target). Three scripts written and run under `/tmp/claude-0/w19c/`; zero repository writes; zero network requests; $0 spend.

---

## Next concrete action

**One successor, runnable today on retained data:** the ARM-2 confound is that three of its four pairs are EWSR1↔FUS swaps, so what looks like "3′ predicts, 5′ does not" may partly be "FET 5′ partners are interchangeable". That is separable with the data already in hand: **test whether `EWSR1-X` vs `FUS-X` pairs (n = 3) differ from the `EPC1-PHF1 · MEAF6-PHF1` non-FET pair, and — the stronger arm — test the 13 `EWSR1-*` peaksets for 5′-driven structure using a within-EWSR1 permutation** that holds the 5′ partner constant and shuffles only the 3′ labels. If peak location is 3′-determined, the 13 EWSR1 fusions should be *no more* similar to each other than density predicts; ARM 1 already hints at this (SHARES-5 residual +0.0094, p = 0.098) but did not isolate it. Same substrate, same machinery, no new access required.

**Not a successor:** anything needing the genome-wide BEDs. That is one 403 away and must not be re-probed.

result: GSE243553 clusters by 3′ partner, not 5′ — across all 32 peaksets and 376 non-degenerate pairs, sharing a 3′ gene predicts peak location (density-residualised mean +0.1513, gene-label permutation p = 0.00008) while sharing a 5′ gene does not (+0.0094, p = 0.098), and the 3′ effect survives deleting every NR4A3 fusion (p = 0.015, n = 4, leave-one-out stable), so W20b's quartet result generalises rather than being NR4A3-specific — with a run negative control correctly null (p = 0.103) and W20b's numbers reproduced exactly once its degenerate-pair convention is made explicit (that convention moves its unconditional p from 0.0013 to 0.0001; its density-matched 0.0010 is unchanged).
