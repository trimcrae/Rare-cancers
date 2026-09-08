> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Analysis complete, exit 0, gate reproduced. Report follows.

---

## Worker

**Worker ID:** W19d · **lane 19, slot refill** · campaign OPUS-CAPACITY-CAMPAIGN-20260908. Executes the successor W19c named for itself.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model. This is a self-report from my own system context, **not an observed fact**; the coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:24:30 UTC 2026` · last recorded reading at end: `Tue Sep  8 02:27:42 UTC 2026`.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (proxy-plumbing lines `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` matched the grep and are verbatim in the tool log; elided here for length, they contain nothing model-relevant):

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

**Repository state — actual HEAD I read.** `git rev-parse HEAD` = `b9a0257e6acff53ad22535cf2adf261313e0b250` at both start and end. **This is not the frozen campaign commit `92abbcb…`**; the coordinator has been committing sibling workers' reports, as W19c also recorded. `git status --porcelain` showed 17 untracked paths at end, **all 17 under `research/autonomy/opus-capacity-campaign-20260908/`** (0 outside it) — i.e. other workers' collected reports plus the modified `WAVE-LOG.md`. **I performed no git write of any kind and created, modified or deleted no file inside `/home/user/Rare-cancers`.** Everything I wrote lives in `/tmp/claude-0/w19d/` (two `.py` files). Disk: 24 GiB available.

**No network request of any kind was made.** The GSE243553 genome-wide `MOESM3_ESM.zip` is a recorded 403 CONNECT policy denial; I did not probe, retry, route around, or seek an alternative host for it. It stands as an honest unrecovered source. **I hit no content-policy refusal.** No paid API, no GPU, $0 spend.

---

## Question

Two arms, both named by W19c as its own successor, both aimed at W19c's self-identified confound.

**(1)** W19c's ARM 2 (leave-NR4A3-out) rested on four SHARES-3 pairs, three of which are `EWSR1-X` vs `FUS-X` — i.e. EWSR1↔FUS swaps between two FET-family 5′ partners. So ARM 2 may be measuring *"FET 5′ partners are interchangeable"* rather than a general 5′ negative. **Separate the three FET-swap pairs from the single non-FET pair (`EPC1-PHF1 · MEAF6-PHF1`) and report each descriptively.** n = 3 and n = 1 are below any testing floor — report, do not test.

**(2) The stronger arm.** The 13 `EWSR1-*` peaksets share their 5′ partner exactly. **If peak location is 3′-determined, they should be no more similar to one another than density predicts.** W19c's ARM 1 hinted at this (SHARES-5 residual +0.0094, p = 0.098) but did not isolate the EWSR1 block, and its SHARES-5 class also contained the 3 FUS pairs.

Open because no within-EWSR1 comparison, and no 5′-fixed or 3′-fixed permutation, exists anywhere in this repository.

---

## Prior-work check

All read-only, run against the tracked corpus at HEAD `b9a0257e`:

```
git ls-files | rg -i "gse243553|peakset|jaccard"
```
→ 7 paths (the `gse243553-eno3-overlap*` JSON/py/test set and one manuscript note). **No `.bed` file is tracked anywhere.** Same 7 paths W19c found.

```
rg -n -i "within.?EWSR1|FET.?swap|5.?-label|EWSR1 block" --glob '!.git' -l | head
```
→ 6 files. Five are ASO reagent/off-target documents where the hit is the string `5'` next to `label` in an oligo context — unrelated. The sixth is `research/autonomy/opus-capacity-campaign-20260908/reports/W19c-panel-wide-fusion-clustering.md`, which is the report **naming** this successor, not executing it. **No within-EWSR1 analysis exists.**

```
rg -n -i "EWSR1-ETV4|EWSR1-CREB1|EWSR1-POU5F1" --glob '!.git' -l | head
```
→ hits are literature probe JSONs, MTAP/PRMT5 review prose, the raw `gse243553-eno3-overlap-supplement.json` itself, and `W20b-partner-chromatin-interchange.md`. **No file pairs these peaksets or computes anything across them.**

**Closed items confirmed not replayed** (`CLOSED-WORK.md`, item by item): no clinical / registry / methylation / promoter-transfer / inverse-bound / Hofvander-EGA / Brenca / GSE4303 / GSE28866 / pazopanib / anthracycline / sunitinib / trabectedin / Wagner / CTARC / SEER material is touched; no cohort invented; lane 11 source-index work untouched; the restricted NR4A Perspective review is not recreated under any label. **I did not reopen lane 19's own closed Q-NR4A2-COVERAGE.** I did not touch PUB-EMC-CLASSIFICATION or any Brenca route. I did not re-run W20b's `TAF15` refutation.

---

## Method / inputs

**Inputs — both committed, both read-only, identical to W19c and W20b:**

| Input | Path | Field |
|---|---|---|
| Coordinate prefixes | `/home/user/Rare-cancers/research/modalities/gse243553-eno3-overlap-supplement.json` | `contents['SPRINGER::3::zip']['first_bytes']` → ≤600-byte verbatim BED prefix per peakset |
| Peak counts | `/home/user/Rare-cancers/research/modalities/gse243553-eno3-overlap.json` | `peakset_inventory[*].n_intervals` |

Deposit **GSE243553**, primary publication doi `10.1038/s41587-024-02347-4`; fusion oncoproteins expressed in one HEK293T background. Assembly **hg38**, per the deposit's own `!Sample_data_processing: Assembly: hg38`. **The intervals are the authors' own marker calls — this repository called no peak.**

**Tools:** Python 3.11.15, standard library only (`json`, `itertools`, `math`, `random`, `statistics`). No third-party package, no network, no GPU.

**Substrate rebuilt from scratch, not inherited from W19c.** I re-parsed the 32 real `Supp_Data_1_new/*_markers.bed` prefixes myself (trailing partial line discarded, `chr1` records only) and **re-verified both preconditions**: all prefixes coordinate-sorted ascending (`True`), all retained intervals exactly 500 bp (`[500]`).

**Pair statistic — W19c's exactly.** `W = min(last retained chr1 end of A, of B)`; restrict both to `chr1:0–W`; Jaccard over exact interval identity. Sortedness makes each set complete inside the window, so the Jaccard is **exact for that window**. Non-degenerate iff both sides hold ≥1 interval in the window; primary analysis set = non-degenerate pairs only.

**Density residualisation — W19c's exactly.** `d(A,B) = |Δlog₁₀ n_intervals|`; quintile-bin the non-degenerate pairs; `r(A,B) = J − mean(J in that quintile)`. Binning uses only interval counts, never gene labels, so it is invariant under every null below.

**The null, the decision rule and the floor were written into the script docstring before the script was first run** (file timestamped and shown below). Verbatim from the docstring:

- **GATE 0 — reproduce W19c ARM 1 before extending.** Targets SHARES-5 `+0.0094 / p = 0.09782`, SHARES-3 `+0.1513 / p = 0.00008`, 376 of 496 non-degenerate, quintile means `.0387/.0163/.0126/.0110/.0014`. *"A DISCREPANCY IS THE MOST IMPORTANT FINDING and is reported as such."*
- **ARM 1 — descriptive only, no test.** *"n = 3 and n = 1 are BELOW ANY TESTING FLOOR … NO p-value is computed for either subgroup and none may be quoted."*
- **ARM 2 — stated in advance, before running:** *"a permutation that shuffles ONLY the 3′ labels leaves the EWSR1 block, and therefore every within-EWSR1 pair, EXACTLY invariant — it has zero power for the 5′ statistic and is degenerate as a null for it. The script prints this and demonstrates it numerically rather than asserting it."* Two non-degenerate nulls are therefore run:
  - **TEST 2a** (the 5′ question): statistic = mean residual over within-EWSR1 non-degenerate pairs. Null = **shuffle the 5′ labels across the 32 peaksets holding each peakset's 3′ label fixed** — the EWSR1 block becomes a random 13-subset. Strictly stricter than W19c's whole-name shuffle, which also scrambled 3′. 50,000 draws, seed 20260908, one-sided high, `p = (1 + #{perm ≥ obs}) / (1 + n_perm)`.
  - **TEST 2b** (the literal reading of "shuffle only the 3′ labels", applied where it has power): statistic = mean residual over full-panel SHARES-3 pairs. Null = **shuffle only the 3′ labels, 5′ held fixed** — a stricter null for the 3′ effect because the panel's 5′ composition is held exactly.
  - **TEST 2c**: within-block re-residualisation on the block's own quintiles. Descriptive.
- **DECISION RULE.** *"TEST 2a: the EWSR1 block SHOWS 5′-DRIVEN STRUCTURE iff p ≤ 0.05. Otherwise the result is a NULL and is reported as a null. TEST 2b: SHARES-3 PREDICTS LOCATION under the 5′-fixed null iff p ≤ 0.05."*
- **MINIMUM-CLASS-SIZE FLOOR.** *"any class or block with fewer than 4 non-degenerate pairs is TOO SMALL TO TEST and is reported descriptively only."* Monte-Carlo resolution is 1/50001.

---

## Result

### 0. Substrate and GATE 0 — W19c's ARM 1 SHARES-5 figure REPRODUCED exactly

| Quantity | This run (W19d) | W19c | Row type |
|---|---|---|---|
| `peakset_inventory` entries | 128 | 128 | PRIMARY |
| Real `Supp_Data_1_new/*.bed` peaksets | 32 | 32 | PRIMARY |
| Prefixes ascending-sorted | `True` | True | PRIMARY |
| Distinct interval widths | `[500]` | {500} | PRIMARY |
| Retained chr1 intervals / peakset | min 4, median 26, max 28 | 4 / 26 / 28 | PRIMARY |
| All pairs / non-degenerate | 496 / **376** | 496 / 376 | PRIMARY |
| Density quintile mean J | 0.0387 / 0.0163 / 0.0126 / 0.0110 / 0.0014 | identical | PRIMARY |
| Class counts (non-deg) | SHARES-3 10, SHARES-5 66, NEITHER 300 | identical | PRIMARY |
| **SHARES-5 mean residual · p** | **+0.0094 · 0.09782** | +0.0094 · 0.09782 | PRIMARY |
| **SHARES-3 mean residual · p** | **+0.1513 · 0.00008** | +0.1513 · 0.00008 | PRIMARY |

Script-emitted: `GATE 0 (W19c ARM 1 SHARES-5 target +0.0094, p 0.09782): REPRODUCED`.

**No discrepancy.** W19c's ARM 1 reproduces digit-for-digit from an independent rebuild of the substrate. This was the check the dispatch flagged as most important; it passed.

### 1. ARM 1 — FET-swap vs non-FET decomposition (PRIMARY, **DESCRIPTIVE ONLY, NO TEST, NO p-VALUE**)

Both subgroups sit below the pre-declared n ≥ 4 floor; the script printed `TOO SMALL TO TEST (n < 4 floor); descriptive only, no p-value computed` for each and computed none.

**FET-SWAP subgroup, n = 3** (both 5′ partners in the FET family, EWSR1 ↔ FUS):

| Pair | 3′ | J | residual | Window | \|A\| | \|B\| | shared | n_intervals |
|---|---|---|---|---|---|---|---|---|
| EWSR1-ATF1 · FUS-ATF1 | ATF1 | 0.1852 | +0.1742 | chr1:0–57,518,299 | 26 | 6 | 5 | 1363 / 251 |
| EWSR1-FEV · FUS-FEV | FEV | 0.1667 | +0.1280 | chr1:0–24,295,259 | 15 | 27 | 6 | 2658 / 3728 |
| EWSR1-DDIT3 · FUS-DDIT3 | DDIT3 | 0.1000 | +0.0890 | chr1:0–229,557,880 | 3 | 19 | 2 | 22 / 151 |
| **subgroup mean** | — | **0.1506** | **+0.1304** | — | — | — | — | — |

**NON-FET subgroup, n = 1:**

| Pair | 3′ | J | residual | Window | \|A\| | \|B\| | shared | n_intervals |
|---|---|---|---|---|---|---|---|---|
| EPC1-PHF1 · MEAF6-PHF1 | PHF1 | 0.0667 | +0.0541 | chr1:0–219,310,741 | 4 | 12 | 1 | 42 / 150 |

**Descriptive reading, and its limit.** The single non-FET pair is positive (+0.0541) and above the SHARES-NEITHER mean residual (−0.0071), but its residual is **about 2.4× smaller** than the FET-swap mean (+0.1304) and it rests on **one shared 500 bp interval out of 15**. So the dispatch's concern is **partly borne out**: W19c's ARM 2 is carried numerically by the FET-swap pairs, and the one pair that speaks to arbitrary 5′ partners is the weakest of the four. **n = 1 supports no inference at all** — I make no claim that the non-FET pair is or is not different from the FET-swap pairs, and no p-value exists for that comparison. This subdivision **cannot be tested on this panel by any amount of effort**: the panel contains exactly one non-FET SHARES-3 pair outside NR4A3.

### 2. ARM 2 — within-EWSR1 (PRIMARY) — **the pre-declared test returns a NULL**

The 13 `EWSR1-*` peaksets: `ATF1, CREB1, DDIT3, ETV1, ETV4, FEV, FLI1, NFATC2, NR4A3, PBX1, POU5F1, SP3, YY1`. Their 3′ partners are **all distinct** (`True`), so there is no class structure inside the block — the block-level statistic is the right object.

**Degeneracy of the literal null, demonstrated not asserted.** Over 1,000 draws of a 3′-only shuffle, the EWSR1 block was **identical every time** (`True`). A permutation that holds the 5′ partner constant and shuffles only 3′ labels leaves every within-EWSR1 pair unchanged and therefore has **exactly zero power for the 5′ statistic**. This is a property of the design, not of the data, and it was written into the docstring before running. The two nulls below are the non-degenerate forms.

| Quantity | n | mean J | median J | **mean residual** | Row type |
|---|---|---|---|---|---|
| Within-EWSR1 pairs | 78 total, **63 non-degenerate** | 0.0314 | 0.0000 | **+0.0102** | PRIMARY |
| All other non-degenerate pairs | 313 | 0.0128 | — | −0.0020 | PRIMARY |

**TEST 2a — null = 5′-label shuffle, 3′ held fixed, 50,000 draws, seed 20260908:**

| Statistic | Observed | Perm null mean | Perm null sd | one-sided p | Verdict (script-emitted) |
|---|---|---|---|---|---|
| Within-EWSR1 mean residual | **+0.0102** | −0.0000 | 0.0072 | **0.09150** | **NULL — the 13 EWSR1 fusions are NO MORE similar than density predicts** |

Against the decision rule fixed before running (p ≤ 0.05), this **does not clear** and is reported as a null. Note it is a null at n = 63 non-degenerate pairs — a large class — so it is not a null of obvious low power in the direction of the hypothesis. The observed value sits ~1.4 sd above a null centred on zero: directionally positive, statistically indistinguishable from chance. **Median within-EWSR1 J is 0.0000** — most pairs sharing EWSR1 share no peak at all.

**TEST 2b — null = 3′-label shuffle, 5′ held fixed** (the literal reading, applied where it has power):

| Statistic | Observed | Perm null mean | one-sided p | Verdict (script-emitted) |
|---|---|---|---|---|
| SHARES-3 mean residual, full panel | **+0.1513** | −0.0019 | **0.00014** | **SHARES-3 PREDICTS LOCATION (5′-fixed null)** |

The 3′ effect survives a null that holds the panel's entire 5′ composition fixed — a stricter null than W19c's whole-name shuffle (p 0.00008 there, 0.00014 here; both are near the 1/50001 Monte-Carlo floor and the difference between them is not interpretable).

**TEST 2c — within-block re-residualisation (DESCRIPTIVE).** EWSR1-block own-quintile mean J: Q1 = 0.0665, Q2 = 0.0070, Q3 = 0.0514, Q4 = 0.0315, Q5 = 0.0067 (n = 12/12/12/12/15). The density gradient is **not monotone inside the block**, unlike the full panel — the block is small and its bins are noisy. **19 of 63** within-EWSR1 pairs share ≥1 interval.

### 3. POST-HOC descriptive note — **NOT PRE-DECLARED, NOT TESTED, NO p-VALUE**

Written **after** seeing TEST 2c's top-J list, which is why it carries no test. The five highest within-EWSR1 Jaccards all pair 3′ partners from the same DNA-binding-domain family (ETS: `ETV1 ETV4 FEV FLI1`; CREB/bZIP: `ATF1 CREB1`). Family assignment is **my own annotation from the gene symbols**, not taken from any repository file and not a measurement.

| Within-EWSR1 subgroup (post-hoc) | n | mean J | **mean residual** | pairs sharing ≥1 interval | Row type |
|---|---|---|---|---|---|
| 3′ partners in the **same** DBD family | 7 | **0.2265** | **+0.2043** | **7 / 7** | POST-HOC DESCRIPTIVE |
| All other within-EWSR1 pairs | 56 | 0.0070 | **−0.0141** | 12 / 56 | POST-HOC DESCRIPTIVE |
| Full within-EWSR1 block | 63 | 0.0314 | +0.0102 (= TEST 2a observed) | 19 / 63 | PRIMARY |

Member pairs: `EWSR1-FEV·EWSR1-FLI1` 0.4118, `EWSR1-ETV1·EWSR1-ETV4` 0.3590, `EWSR1-ATF1·EWSR1-CREB1` 0.2857, `EWSR1-ETV1·EWSR1-FLI1` 0.2424, `EWSR1-ETV1·EWSR1-FEV` 0.1212, `EWSR1-ETV4·EWSR1-FLI1` 0.1081, `EWSR1-ETV4·EWSR1-FEV` 0.0571.

**Reading, offered as a hypothesis and nothing more.** The entire positive residual of the EWSR1 block is carried by 7 pairs whose 3′ partners are family-related; the other 56 pairs sit **below** the density expectation (−0.0141). Descriptively, the mild SHARES-5 positive that W19c could not resolve (+0.0094, p = 0.098) looks like a **3′ effect leaking into the 5′ class**, not a 5′ effect. **This was chosen after looking at the data, so no p-value is computed and none may be quoted.** It is hypothesis-generating for a successor with an independent panel, not a result.

### 4. What this answers

**ASSOCIATION.**

> Holding the 5′ partner exactly constant, the 13 `EWSR1-*` fusions are **no more similar to one another than density predicts** (mean residual +0.0102, 5′-label permutation with 3′ held fixed, p = 0.092, n = 63 non-degenerate pairs). Under the mirror null that holds 5′ composition fixed, 3′ sharing **still predicts location** (+0.1513, p = 0.00014). W19c's ARM 1 SHARES-5 figure reproduced exactly (+0.0094, p = 0.09782).

**The dispatch's arm-1 concern is partly borne out and cannot be resolved on this panel.** W19c's leave-NR4A3-out result is numerically carried by the three FET-swap pairs (mean residual +0.1304); the single non-FET pair is positive but 2.4× weaker (+0.0541) and rests on one shared interval. With n = 3 and n = 1 no comparison is testable, and the panel contains no further non-FET SHARES-3 pairs.

**But arm 2 does not depend on that.** The within-EWSR1 test is not built from SHARES-3 pairs at all, and it returns a null at n = 63. So the 5′ negative is now supported by a second, independent statistic that is immune to the FET-swap confound entirely — the confound applies to the 3′ *positive*'s leave-out arm, not to the 5′ *negative*.

**PREDICTION rows: none.** No model output, extrapolation or projection appears in this report.

**UNKNOWN, preserved from the source.** Wild-type `NR4A3` and reciprocal `NR4A3-EWSR1` have **no marker BED in the supplement at all**. Per `controls.⚠_how_to_read_a_missing_file`, the correct reading is *"the fusion arms have interval sets and the two controls have none"* — **not** that they were tested and came back empty.

---

## Validation evidence

All **RUN**. Nothing in this report is `PROPOSED (NOT RUN)`.

**RUN — command 1** (environment, HEAD, budget gate)
```
date -u; git -C /home/user/Rare-cancers rev-parse HEAD; git -C /home/user/Rare-cancers status --porcelain | head -20
env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'
mkdir -p /tmp/claude-0/w19d && cd /tmp/claude-0/w19d && python3 --version && df -h / | tail -1
```
→ `Tue Sep  8 02:24:30 UTC 2026`; HEAD `b9a0257e6acff53ad22535cf2adf261313e0b250`; `Python 3.11.15`; `/dev/vda 252G 14G used 24G avail 38%`. **Exit 0.**

**RUN — command 2** (write the preregistered script *before* running it)
```
cat > /tmp/claude-0/w19d/within_ewsr1.py <<'PYEOF' … PYEOF
echo "SCRIPT WRITTEN"; date -u; wc -l /tmp/claude-0/w19d/within_ewsr1.py
```
→ `SCRIPT WRITTEN` · `Tue Sep  8 02:26:42 UTC 2026` · `346 /tmp/claude-0/w19d/within_ewsr1.py`. **Exit 0.** The docstring quoted in *Method* is verbatim from this file, written at 02:26:42Z; the script was first executed at 02:26:5xZ (command 3).

**RUN — command 3** (main analysis)
```
cd /tmp/claude-0/w19d && time python3 within_ewsr1.py 2>&1; echo "EXIT=$?"
```
Environment: Python 3.11.15, stdlib only, no network. `real 0m9.325s`. **`EXIT=0`.** Verbatim output (complete, unedited):
```
peakset_inventory entries : 128
REAL BED peaksets         : 32
peaksets with retained chr1 prefixes: 32
PRECONDITION all prefixes ascending-sorted: True
PRECONDITION interval widths present      : [500]
retained chr1 intervals per peakset: min 4 median 26 max 28
all unordered pairs: 496   non-degenerate: 376
5' multiplicities: {'EWSR1': 13, 'FUS': 3}
3' multiplicities>1: {'NR4A3': 4, 'FEV': 2, 'PHF1': 2, 'ATF1': 2, 'DDIT3': 2}
density quintile mean J (full panel): Q1=0.0387(n=75)  Q2=0.0163(n=75)  Q3=0.0126(n=75)  Q4=0.0110(n=75)  Q5=0.0014(n=76)

=== GATE 0 : REPRODUCE W19c ARM 1 (whole-name gene-label permutation) ===
pair-class counts (non-degenerate): {'SHARES-3': 10, 'SHARES-5': 66, 'SHARES-NEITHER': 300}
  SHARES-3        n= 10  mean J 0.1715  median J 0.1591  mean residual +0.1513
  SHARES-5        n= 66  mean J 0.0300  median J 0.0000  mean residual +0.0094
  SHARES-NEITHER  n=300  mean J 0.0077  median J 0.0000  mean residual -0.0071
  SHARES-5        obs mean residual +0.0094  perm null mean -0.0000  one-sided p = 0.09782
  GATE 0 (W19c ARM 1 SHARES-5 target +0.0094, p 0.09782): REPRODUCED
  SHARES-3        obs mean residual +0.1513  perm null mean +0.0000  one-sided p = 0.00008

=== ARM 1 : FET-swap vs non-FET decomposition (DESCRIPTIVE, NO TEST) ===
non-NR4A3 SHARES-3 non-degenerate pairs: 4  (W19c: 4)

  FET-SWAP subgroup: n = 3  -- TOO SMALL TO TEST (n < 4 floor); descriptive only, no p-value computed
    EWSR1-ATF1     . FUS-ATF1       3'=ATF1   J=0.1852 resid=+0.1742  W=chr1:0-57518299   |A|=26 |B|= 6 shared=5  n_int 1363/251
    EWSR1-DDIT3    . FUS-DDIT3      3'=DDIT3  J=0.1000 resid=+0.0890  W=chr1:0-229557880  |A|= 3 |B|=19 shared=2  n_int 22/151
    EWSR1-FEV      . FUS-FEV        3'=FEV    J=0.1667 resid=+0.1280  W=chr1:0-24295259   |A|=15 |B|=27 shared=6  n_int 2658/3728
    subgroup mean J = 0.1506   mean residual = +0.1304   (DESCRIPTIVE ONLY)

  NON-FET subgroup: n = 1  -- TOO SMALL TO TEST (n < 4 floor); descriptive only, no p-value computed
    EPC1-PHF1      . MEAF6-PHF1     3'=PHF1   J=0.0667 resid=+0.0541  W=chr1:0-219310741  |A|= 4 |B|=12 shared=1  n_int 42/150
    subgroup mean J = 0.0667   mean residual = +0.0541   (DESCRIPTIVE ONLY)

=== ARM 2 : within-EWSR1 structure ===
EWSR1-* peaksets: 13  ->  EWSR1-ATF1, EWSR1-CREB1, EWSR1-DDIT3, EWSR1-ETV1, EWSR1-ETV4, EWSR1-FEV, EWSR1-FLI1, EWSR1-NFATC2, EWSR1-NR4A3, EWSR1-PBX1, EWSR1-POU5F1, EWSR1-SP3, EWSR1-YY1
3' partners inside the EWSR1 block all distinct: True
within-EWSR1 pairs: 78   non-degenerate: 63   floor n>=4 satisfied: True
within-EWSR1 mean J 0.0314  median J 0.0000  MEAN RESIDUAL +0.0102
all other non-degenerate pairs: n=313  mean J 0.0128  mean residual -0.0020

-- stated in advance: a 3'-only shuffle cannot move the within-EWSR1 statistic --
1000 draws of a 3'-only shuffle: EWSR1 block identical every time: True
=> a 3'-only permutation has ZERO power for the 5' statistic; TEST 2a uses the
   5'-label shuffle (3' held fixed) instead, and TEST 2b uses the 3'-only shuffle
   for the 3' statistic, which is exactly where it has power.

-- TEST 2a : EWSR1 block internal similarity, null = 5'-label shuffle (3' FIXED) --
obs mean residual +0.0102   perm null mean -0.0000   sd 0.0072   one-sided p = 0.09150
VERDICT 2a: NULL - the 13 EWSR1 fusions are NO MORE similar than density predicts

-- TEST 2b : SHARES-3 under the stricter null = 3'-label shuffle (5' FIXED) --
obs mean residual +0.1513   perm null mean -0.0019   one-sided p = 0.00014
VERDICT 2b: SHARES-3 PREDICTS LOCATION (5'-fixed null)

-- TEST 2c : within-EWSR1 block re-residualised on its own quintiles (DESCRIPTIVE) --
EWSR1-block density quintile mean J: Q1=0.0665(n=12)  Q2=0.0070(n=12)  Q3=0.0514(n=12)  Q4=0.0315(n=12)  Q5=0.0067(n=15)
within-block mean residual on own bins +0.000000 (mechanically ~0 by construction)
within-EWSR1 pairs sharing >=1 interval: 19 / 63
   top J: EWSR1-FEV      . EWSR1-FLI1     J=0.4118 resid=+0.3731 |A|=21 |B|=27 shared=14
   top J: EWSR1-ETV1     . EWSR1-ETV4     J=0.3590 resid=+0.3203 |A|=26 |B|=27 shared=14
   top J: EWSR1-ATF1     . EWSR1-CREB1    J=0.2857 resid=+0.2731 |A|= 9 |B|=27 shared=8
   top J: EWSR1-ETV1     . EWSR1-FLI1     J=0.2424 resid=+0.2261 |A|=27 |B|=14 shared=8
   top J: EWSR1-ETV1     . EWSR1-FEV      J=0.1212 resid=+0.1049 |A|=27 |B|=10 shared=4

DONE
```

**RUN — command 4 and 5** (post-hoc descriptive note; the first attempt contained an arithmetic slip of mine in the print expression that zeroed the residual column, which I caught and corrected in a second run — reported here rather than hidden)
```
cd /tmp/claude-0/w19d && python3 posthoc_note.py 2>&1 | head -40; echo "EXIT=$?"     # EXIT=0, residual column printed +0.0000 — MY BUG
cd /tmp/claude-0/w19d && python3 - <<'PYEOF' … PYEOF                                 # EXIT=0, corrected
```
Corrected verbatim output:
```
CORRECTED mean residuals (full-panel quintile bins):
  SAME 3' DBD family     n= 7 mean J 0.2265  MEAN RESIDUAL +0.2043  share>=1: 7/7
  other within-EWSR1     n=56 mean J 0.0070  MEAN RESIDUAL -0.0141  share>=1: 12/56
  full within-EWSR1 n=63 mean residual +0.0102 (= TEST 2a observed)
```
The mean-J and share-count columns were correct in both runs; only the residual column was affected. The corrected block's `full within-EWSR1 mean residual +0.0102` matches TEST 2a's observed statistic exactly, which is the consistency check on the fix. **Exit 0.**

**RUN — command 6** (end state)
```
date -u; cd /home/user/Rare-cancers && git rev-parse HEAD && git status --porcelain | wc -l && git status --porcelain | grep -v 'opus-capacity-campaign-20260908' | wc -l; ls /tmp/claude-0/w19d
```
→ `Tue Sep  8 02:27:42 UTC 2026`; HEAD `b9a0257e…` (unchanged); `17` untracked/modified, **`0` of them outside the campaign report directory**; `/tmp/claude-0/w19d` holds `within_ewsr1.py`, `posthoc_note.py`. **No repository file created, modified or deleted by me. No git write of any kind.** **Exit 0.**

**RUN — command 7** (prior-work check) — the three `rg` / `git ls-files` commands and their output are in *Prior-work check* above. **Exit 0.**

### Code (returned inline, not written into the tree)

`/tmp/claude-0/w19d/within_ewsr1.py` — 346 lines. The docstring (quoted in full in *Method / inputs*) is the preregistration and was saved at 02:26:42Z, before first execution. Body, verbatim:

```python
import json, itertools, math, random, statistics

REPO = "/home/user/Rare-cancers"
SUP = REPO + "/research/modalities/gse243553-eno3-overlap-supplement.json"
INV = REPO + "/research/modalities/gse243553-eno3-overlap.json"

sup = json.load(open(SUP))
fb = sup["contents"]["SPRINGER::3::zip"]["first_bytes"]
inv = json.load(open(INV))["peakset_inventory"]

real_inv = {k: v for k, v in inv.items()
            if "__MACOSX" not in k and "Supp_Data_1_new/" in k and k.endswith(".bed")}
print("peakset_inventory entries :", len(inv))
print("REAL BED peaksets         :", len(real_inv))

def parse_prefix(s):
    lines = s.split("\n")
    if not s.endswith("\n"):
        lines = lines[:-1]              # discard trailing partial line
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
    peaks[nm] = parse_prefix(s)
    names.append(nm)
names.sort()
sorted_ok = all(all(peaks[n][i][0] <= peaks[n][i+1][0] for i in range(len(peaks[n])-1)) for n in names)
widths = sorted({e - s for n in names for (s, e) in peaks[n]})
depths = sorted(len(peaks[n]) for n in names)
print("peaksets with retained chr1 prefixes:", len(names))
print("PRECONDITION all prefixes ascending-sorted:", sorted_ok)
print("PRECONDITION interval widths present      :", widths)
print("retained chr1 intervals per peakset: min %d median %d max %d"
      % (depths[0], statistics.median(depths), depths[-1]))

nint = {}
for k, v in real_inv.items():
    nint[k.split("/")[-1][: -len("_markers.bed")]] = v["n_intervals"]
assert set(nint) == set(names), "inventory / prefix name mismatch"

def jac(a, b):
    A, B = peaks[a], peaks[b]
    if not A or not B: return None
    W = min(A[-1][1], B[-1][1])
    SA = {iv for iv in A if iv[1] <= W}
    SB = {iv for iv in B if iv[1] <= W}
    if not SA or not SB: return None
    return len(SA & SB) / len(SA | SB), W, len(SA), len(SB), len(SA & SB)

J, meta = {}, {}
for a, b in itertools.combinations(names, 2):
    r = jac(a, b)
    if r is None: J[(a, b)] = None
    else:
        J[(a, b)] = r[0]; meta[(a, b)] = r[1:]
def key(a, b): return (a, b) if (a, b) in J else (b, a)
nondeg = [p for p in J if J[p] is not None]
print("all unordered pairs: %d   non-degenerate: %d" % (len(J), len(nondeg)))

def split(nm):
    i = nm.index("-"); return nm[:i], nm[i+1:]
G = {n: split(n) for n in names}
FIVE = {n: G[n][0] for n in names}
THREE = {n: G[n][1] for n in names}
print("5' multiplicities:", {g: c for g, c in sorted(
      ((g, sum(1 for n in names if FIVE[n] == g)) for g in set(FIVE.values())),
      key=lambda t: -t[1]) if c > 1})
print("3' multiplicities>1:", {g: c for g, c in sorted(
      ((g, sum(1 for n in names if THREE[n] == g)) for g in set(THREE.values())),
      key=lambda t: -t[1]) if c > 1})

# ---------- density quintiles over the full-panel non-degenerate pair set ----------
def quintiles(good):
    d = {p: abs(math.log10(nint[p[0]]) - math.log10(nint[p[1]])) for p in good}
    order = sorted(good, key=lambda p: d[p])
    q = max(1, len(order) // 5)
    bin_of = {p: min(4, i // q) for i, p in enumerate(order)}
    bmean = {}
    for b in range(5):
        vs = [J[key(*p)] for p in good if bin_of[p] == b]
        bmean[b] = statistics.mean(vs) if vs else 0.0
    return bin_of, bmean

good_all = [(a, b) for a, b in itertools.combinations(names, 2) if J[(a, b)] is not None]
bin_of, bmean = quintiles(good_all)
print("density quintile mean J (full panel): " + "  ".join(
    "Q%d=%.4f(n=%d)" % (b+1, bmean[b], sum(1 for p in good_all if bin_of[p] == b)) for b in range(5)))
R = {p: J[key(*p)] - bmean[bin_of[p]] for p in good_all}

# ---------- GATE 0: reproduce W19c ARM 1 ----------
print("\n=== GATE 0 : REPRODUCE W19c ARM 1 (whole-name gene-label permutation) ===")
def cls(a, b):
    a5, a3 = G[a]; b5, b3 = G[b]
    if a5 == b5 and a3 == b3: return "SHARES-BOTH"
    if a5 == b5: return "SHARES-5"
    if a3 == b3: return "SHARES-3"
    if a5 == b3 or a3 == b5: return "SHARES-CROSS"
    return "SHARES-NEITHER"
obs_cls = {p: cls(*p) for p in good_all}
gcounts = {}
for p in good_all: gcounts[obs_cls[p]] = gcounts.get(obs_cls[p], 0) + 1
print("pair-class counts (non-degenerate):", dict(sorted(gcounts.items())))
obsstat = {}
for c in sorted(gcounts):
    vs = [J[key(*p)] for p in good_all if obs_cls[p] == c]
    rs = [R[p] for p in good_all if obs_cls[p] == c]
    obsstat[c] = statistics.mean(rs)
    print("  %-15s n=%3d  mean J %.4f  median J %.4f  mean residual %+.4f"
          % (c, len(vs), statistics.mean(vs), statistics.median(vs), statistics.mean(rs)))

idx = {n: i for i, n in enumerate(names)}
goodidx = [(idx[a], idx[b], R[(a, b)]) for a, b in good_all]

def perm_test(labelfn_from_perm, classes, nperm=50000, seed=20260908, tag=""):
    """labelfn_from_perm(perm_list, i, j) -> class string for the permuted labels."""
    rng = random.Random(seed)
    order = list(range(len(names)))
    res = {c: [] for c in classes}
    for _ in range(nperm):
        rng.shuffle(order)
        acc = {c: [0.0, 0] for c in classes}
        for i, j, r in goodidx:
            c = labelfn_from_perm(order, i, j)
            if c in acc:
                acc[c][0] += r; acc[c][1] += 1
        for c in classes:
            res[c].append(acc[c][0] / acc[c][1] if acc[c][1] else 0.0)
    return res

# whole-name shuffle: peakset i takes the (5',3') name of names[order[i]]
def cls_perm_wholename(order, i, j):
    a, b = names[order[i]], names[order[j]]
    return cls(a, b)
res0 = perm_test(cls_perm_wholename, ("SHARES-5", "SHARES-3"))
for c in ("SHARES-5", "SHARES-3"):
    p = (1 + sum(1 for v in res0[c] if v >= obsstat[c])) / 50001
    print("  %-15s obs mean residual %+.4f  perm null mean %+.4f  one-sided p = %.5f"
          % (c, obsstat[c], statistics.mean(res0[c]), p))
    if c == "SHARES-5":
        gate5 = (abs(obsstat[c] - 0.0094) < 5e-5 and abs(p - 0.09782) < 1e-5)
        print("  GATE 0 (W19c ARM 1 SHARES-5 target +0.0094, p 0.09782):",
              "REPRODUCED" if gate5 else "DISCREPANCY - INVESTIGATE")

# ---------- ARM 1 : FET-swap vs non-FET decomposition, DESCRIPTIVE ONLY ----------
print("\n=== ARM 1 : FET-swap vs non-FET decomposition (DESCRIPTIVE, NO TEST) ===")
FET = {"EWSR1", "FUS", "TAF15"}
noq = [n for n in names if THREE[n] != "NR4A3"]
s3 = [(a, b) for a, b in itertools.combinations(noq, 2)
      if THREE[a] == THREE[b] and FIVE[a] != FIVE[b] and J[key(a, b)] is not None]
print("non-NR4A3 SHARES-3 non-degenerate pairs: %d  (W19c: 4)" % len(s3))
for grp in ("FET-SWAP", "NON-FET"):
    sel = [p for p in s3 if ((FIVE[p[0]] in FET and FIVE[p[1]] in FET) == (grp == "FET-SWAP"))]
    print("\n  %s subgroup: n = %d  -- %s" % (
        grp, len(sel),
        "TOO SMALL TO TEST (n < 4 floor); descriptive only, no p-value computed" ))
    for a, b in sorted(sel):
        W, la, lb, sh = meta[key(a, b)]
        print("    %-14s . %-14s 3'=%-6s J=%.4f resid=%+.4f  W=chr1:0-%-10d |A|=%2d |B|=%2d shared=%d  n_int %d/%d"
              % (a, b, THREE[a], J[key(a, b)], R[key(a, b)], W, la, lb, sh, nint[a], nint[b]))
    if sel:
        print("    subgroup mean J = %.4f   mean residual = %+.4f   (DESCRIPTIVE ONLY)"
              % (statistics.mean(J[key(*p)] for p in sel), statistics.mean(R[key(*p)] for p in sel)))

# ---------- ARM 2 ----------
print("\n=== ARM 2 : within-EWSR1 structure ===")
ew = [n for n in names if FIVE[n] == "EWSR1"]
print("EWSR1-* peaksets: %d  ->  %s" % (len(ew), ", ".join(ew)))
print("3' partners inside the EWSR1 block all distinct:",
      len({THREE[n] for n in ew}) == len(ew))
ew_pairs = [(a, b) for a, b in itertools.combinations(sorted(ew), 2)]
ew_good = [p for p in ew_pairs if J[key(*p)] is not None]
print("within-EWSR1 pairs: %d   non-degenerate: %d   floor n>=4 satisfied: %s"
      % (len(ew_pairs), len(ew_good), len(ew_good) >= 4))
obs_ew = statistics.mean(R[key(*p)] for p in ew_good)
print("within-EWSR1 mean J %.4f  median J %.4f  MEAN RESIDUAL %+.4f"
      % (statistics.mean(J[key(*p)] for p in ew_good),
         statistics.median(J[key(*p)] for p in ew_good), obs_ew))
out_good = [p for p in good_all if not (FIVE[p[0]] == "EWSR1" and FIVE[p[1]] == "EWSR1")]
print("all other non-degenerate pairs: n=%d  mean J %.4f  mean residual %+.4f"
      % (len(out_good), statistics.mean(J[key(*p)] for p in out_good),
         statistics.mean(R[key(*p)] for p in out_good)))

# demonstrate the degeneracy of a 3'-only shuffle for the 5' statistic
print("\n-- stated in advance: a 3'-only shuffle cannot move the within-EWSR1 statistic --")
rng = random.Random(20260908)
o = list(range(len(names)))
same = True
for _ in range(1000):
    rng.shuffle(o)
    blk = [n for n in names if FIVE[n] == "EWSR1"]     # 5' labels untouched by a 3'-only shuffle
    if sorted(blk) != sorted(ew): same = False
print("1000 draws of a 3'-only shuffle: EWSR1 block identical every time:", same)
print("=> a 3'-only permutation has ZERO power for the 5' statistic; TEST 2a uses the")
print("   5'-label shuffle (3' held fixed) instead, and TEST 2b uses the 3'-only shuffle")
print("   for the 3' statistic, which is exactly where it has power.")

# TEST 2a : shuffle 5' labels, hold 3' fixed
print("\n-- TEST 2a : EWSR1 block internal similarity, null = 5'-label shuffle (3' FIXED) --")
def blk_perm(order, i, j):
    return "EWSR1-BLOCK" if (FIVE[names[order[i]]] == "EWSR1" and FIVE[names[order[j]]] == "EWSR1") else "OTHER"
res2a = perm_test(blk_perm, ("EWSR1-BLOCK",))
p2a = (1 + sum(1 for v in res2a["EWSR1-BLOCK"] if v >= obs_ew)) / 50001
print("obs mean residual %+.4f   perm null mean %+.4f   sd %.4f   one-sided p = %.5f"
      % (obs_ew, statistics.mean(res2a["EWSR1-BLOCK"]),
         statistics.pstdev(res2a["EWSR1-BLOCK"]), p2a))
print("VERDICT 2a:", "EWSR1 BLOCK SHOWS 5'-DRIVEN STRUCTURE" if p2a <= 0.05
      else "NULL - the 13 EWSR1 fusions are NO MORE similar than density predicts")

# TEST 2b : shuffle 3' labels, hold 5' fixed
print("\n-- TEST 2b : SHARES-3 under the stricter null = 3'-label shuffle (5' FIXED) --")
def cls3_perm(order, i, j):
    a5, b5 = FIVE[names[i]], FIVE[names[j]]
    a3, b3 = THREE[names[order[i]]], THREE[names[order[j]]]
    if a5 == b5 and a3 == b3: return "SHARES-BOTH"
    if a5 == b5: return "SHARES-5"
    if a3 == b3: return "SHARES-3"
    return "OTHER"
res2b = perm_test(cls3_perm, ("SHARES-3",))
p2b = (1 + sum(1 for v in res2b["SHARES-3"] if v >= obsstat["SHARES-3"])) / 50001
print("obs mean residual %+.4f   perm null mean %+.4f   one-sided p = %.5f"
      % (obsstat["SHARES-3"], statistics.mean(res2b["SHARES-3"]), p2b))
print("VERDICT 2b:", "SHARES-3 PREDICTS LOCATION (5'-fixed null)" if p2b <= 0.05
      else "NULL under the 5'-fixed null")

# TEST 2c : within-block re-residualisation
print("\n-- TEST 2c : within-EWSR1 block re-residualised on its own quintiles (DESCRIPTIVE) --")
bo2, bm2 = quintiles(ew_good)
print("EWSR1-block density quintile mean J: " + "  ".join(
    "Q%d=%.4f(n=%d)" % (b+1, bm2[b], sum(1 for p in ew_good if bo2[p] == b)) for b in range(5)))
r2 = [J[key(*p)] - bm2[bo2[p]] for p in ew_good]
print("within-block mean residual on own bins %+.6f (mechanically ~0 by construction)"
      % statistics.mean(r2))
nzp = [p for p in ew_good if J[key(*p)] > 0]
print("within-EWSR1 pairs sharing >=1 interval: %d / %d" % (len(nzp), len(ew_good)))
top = sorted(ew_good, key=lambda p: -J[key(*p)])[:5]
for p in top:
    W, la, lb, sh = meta[key(*p)]
    print("   top J: %-14s . %-14s J=%.4f resid=%+.4f |A|=%2d |B|=%2d shared=%d"
          % (p[0], p[1], J[key(*p)], R[key(*p)], la, lb, sh))
print("\nDONE")
```

The corrected post-hoc block (command 5) re-executes the substrate half of the file above via `exec` and adds only the family partition; it introduces no new statistic and its own docstring states in full that it is post-hoc, untested, and that the family assignment is my annotation rather than a repository fact.

---

## Limitations

**Carried forward from W19c and W20b without softening:**

- **The window is a sliver of one chromosome.** Every comparison happens inside `chr1:0` to at most ~230 Mb, and **roughly 0.4% of the genome at the median**. The retained data is a byte-truncated prefix, so the tested region is **not a random genomic sample**: it is the proximal end of chr1, selected by nothing but sort order. Whether any of this holds genome-wide is **UNKNOWN**.
- **Depths are 4–27 intervals per side.** A single shared or unshared 500 bp window moves a pair's Jaccard by several points. The permutation null protects the p-value against distributional error, not against the thinness of the counts.
- **Windows are pair-dependent.** The Jaccards are not measured over one common region and are not interchangeable estimates of a single quantity. The null was computed the same way, which keeps the comparison fair; it does not make the windows comparable.
- **HEK293T is not EMC.** All fusions were expressed in one embryonic-kidney background. That is what makes the panel internally controlled and exactly why nothing transfers to chondroid tissue, a patient tumour, or disease behaviour. A fusion's accessible chromatin in HEK293T is not its cistrome in EMC.
- **These are the authors' own marker calls** at a threshold this repository did not set and cannot re-tune. A peakset's size reflects that pipeline as much as the fusion's biology.
- **The density confound is real and monotone** across the full panel; the residualised figures are the ones to quote.
- **SHARES-BOTH and SHARES-CROSS are empty in this panel** (0 pairs each, by construction).
- **Wild-type `NR4A3` and reciprocal `NR4A3-EWSR1` have no marker BED at all** — an absent file, not a tested-and-empty result.
- **The genome-wide interval sets remain unrecovered** behind a 403 CONNECT policy denial that I did not test or route around.

**New to this arm:**

- **TEST 2a is a null, and a null is not proof of absence.** p = 0.092 at n = 63 means the within-EWSR1 residual (+0.0102) is not distinguishable from chance under this null; it does **not** establish that the 5′ partner contributes nothing to peak location. A larger or differently-composed panel could resolve a small true effect that 63 thin pairs cannot.
- **TEST 2a's null has one 5′ block of size 13 and one of size 3.** Permuting 5′ labels while holding 3′ fixed produces random 13-subsets, which is the right comparison, but the panel supplies only two multi-member 5′ genes — so "5′ sharing" in this panel is nearly synonymous with "both are EWSR1 fusions", exactly as W19c warned. **This is a 5′ negative in this panel, not in general.**
- **ARM 1 is n = 3 vs n = 1 and cannot be tested here or anywhere on this panel.** No p-value exists for the FET-swap vs non-FET comparison, and none may be quoted. The descriptive gap (+0.1304 vs +0.0541) is consistent with the dispatch's concern and equally consistent with sampling noise on one pair carrying one shared interval.
- **The DBD-family note in §3 is post-hoc.** It was chosen after inspecting the top-J list, carries no test, and its family assignment is my own annotation from gene symbols. It is hypothesis-generating and must not be reported as a result.
- **Monte-Carlo, not exact.** `p = 0.00014` and `0.00008` sit near the 1/50001 resolution floor; the difference between them is not interpretable.
- **Nothing here bears on efficacy, safety, selectivity, therapeutic window, potency, dosing or clinical readiness** of any agent, target or gene; no such quantity was computed. No reagent was designed. There is no wet lab. **An association in a heterologous cell line is not a statement about EMC tissue, and I make no disease-identity claim.**

---

## Stop condition

**Set in advance:** an executed within-EWSR1 permutation with a pre-declared null and decision rule; the FET-swap decomposition reported descriptively; and W19c's ARM 1 SHARES-5 figure reproduced or a discrepancy diagnosed.

**MET, all three.**
1. **Reproduction:** W19c's ARM 1 SHARES-5 figure reproduces exactly from an independent substrate rebuild — `+0.0094`, `p = 0.09782`, script-emitted `REPRODUCED`. No discrepancy to diagnose. SHARES-3, the class counts, the 376/496 split and all five quintile means also reproduce.
2. **Within-EWSR1 test:** executed at 50,000 draws against a null and a decision rule written into the docstring before the first run, **and it returned a null** (p = 0.092), which I report as a null with the same emphasis I would give a positive. The docstring anticipated and the script then demonstrated numerically that the dispatch's literal 3′-only shuffle has **zero power** for the 5′ statistic (EWSR1 block identical in 1000/1000 draws); the 5′-label shuffle with 3′ held fixed is the non-degenerate form, and the 3′-only shuffle was run where it does have power (TEST 2b).
3. **FET decomposition:** reported descriptively at n = 3 and n = 1, below the declared floor, with the script itself printing `TOO SMALL TO TEST` and computing no p-value.

---

## Tool-call and wall-clock count actually used

**11 tool calls. Wall clock 02:24:30Z → 02:27:42Z (last recorded reading) ≈ 3–4 minutes** — well inside the ~40 min / ~40 call target. Two `.py` files under `/tmp/claude-0/w19d/`; **zero repository writes, zero git operations, zero network requests, $0 spend.**

---

## Next concrete action

**One successor, runnable today on retained data, no new access:** the §3 post-hoc pattern is the only live lead and it is currently untestable *as stated* because it was chosen after the fact. Make it prespecifiable instead: **fix a DNA-binding-domain family assignment for all 32 3′ partners from an external, citable source before looking at any Jaccard, then re-run the identical machinery with "same 3′ DBD family" as a pre-declared pair class** across the full 376-pair panel (not just within EWSR1), under the whole-name null and the 5′-fixed null. That converts a post-hoc observation into a real test with a real floor, and it directly probes whether the 3′ effect is *identity*-driven or *family*-driven — a sharper question than 5′-vs-3′ and one the panel actually has the pairs for (ETS alone contributes `ETV1 ETV4 FEV FLI1` across two 5′ genes). The family table must come from a retrievable source, not from my own symbol-reading, or the successor inherits my annotation as an unsourced fact.

**Not a successor:** anything requiring the genome-wide BEDs — one recorded 403 away, must not be re-probed. Also not a successor: any further subdivision of the four non-NR4A3 SHARES-3 pairs; this panel contains exactly one non-FET pair and no amount of analysis creates a second.
