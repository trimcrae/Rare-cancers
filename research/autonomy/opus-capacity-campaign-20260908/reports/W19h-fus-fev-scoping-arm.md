<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:16:10Z UTC
     agent id a5ce1608e8115b8e1 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a5ce1608e8115b8e1.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Report follows. Stop condition met; nothing written into the repository (`git status --porcelain` empty at both ends).

---

## Stop condition (stated up front)

**Set before running:** stop the moment (a) the ARM 1 gate has been evaluated against the published figures, (b) the complete `FUS-FEV × *` and `TMPRSS2-ERG × *` residual rankings exist with the in-class pairs located in them, and (c) the substrate-geometry table for all 32 peaksets exists. **Met.** No p-value was computed for this arm, by design. Returned immediately on meeting it.

---

## Worker

**Worker ID:** W19h · lane 19 refill · OPUS-CAPACITY-CAMPAIGN-20260908 · Anthropic Cloud, Claude Code.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript; do not treat my self-report as observed.

`date -u` at start: `Tue Sep  8 03:05:02 UTC 2026`. At end: `Tue Sep  8 03:07:12 UTC 2026`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (five long proxy-plumbing lines — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy` — matched the grep and are verbatim in the tool log; elided here for length, model-irrelevant):

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

The end-of-run capture was byte-identical apart from the elided proxy lines (I filtered them at the end rather than by hand). No `*MODEL*` variable exists at either end.

**HEAD moved under me**, as the brief anticipates: `4bd79b3bca255451dc5b25aaafa882e0ebed02e8` at start → `98a0833f1ede2cf9cef13790388260567a32e868` at end. **Both my inputs are byte-identical across the move**: `git diff --stat 4bd79b3..98a0833 -- research/modalities/gse243553-eno3-overlap.json research/modalities/gse243553-eno3-overlap-supplement.json` printed **nothing**, exit 0. `git status --porcelain` was **empty at start and empty at end** — I wrote nothing into `/home/user/Rare-cancers`; all four scripts live under `/tmp/claude-0/w19h/`.

Note: neither HEAD equals the `92abbcb…` frozen read commit named in `COMMON-BRIEF.md`; the tree has moved on under concurrent workers. I read the live checkout, not the frozen corpus.

---

## Question

W19g found that the `SAMEFAM-DIFFGENE-DIFF5'` (ETS) class residual of **+0.1226** halves to **+0.0613** when `FUS-FEV` is dropped, and that the three highest residuals in the class are all `EWSR1-* × FUS-FEV`. The open question, which is a **scoping** question and not a significance question:

> **Is that residual an ETS-family property, or a `FUS-FEV` property?**

Operationalised exactly as W19g named it: if `FUS-FEV` is simply a globally high-similarity peakset, then within **its own** panel-wide ranking its in-class partners will not stand out, and the class effect is partly a property of one peakset. This is descriptive and distribution-free. **No p-value is computed for this arm.**

---

## Prior-work check

Commands actually run against the live checkout:

- `rg -n -i "FUS-FEV" --glob '!.git' -l` → 7 files: the two committed GSE243553 JSONs, `research/modalities/gse243553-eno3-overlap-arms.json`, and reports W19c/W19d/W19e/W19f/W19g. No existing per-peakset ranking anywhere.
- `rg -n -i "hub|within-peakset rank|per-peakset ranking|scoping arm" .../reports/W19*.md` → hits only in W19g, lines 167/176 (its dependence census) and lines 433/435, which **name this exact arm as its successor** and rule out a third DBD family, any leave-two-out arm, and any genome-wide route.
- `git ls-files | rg -i "w19|peakset"` → the seven lane-19 report files only.

**Not replaying anything closed.** I did not re-run W19e's or W19f's tests beyond the ARM 1 gate; did not introduce a third family; did not run leave-two-out; did not touch the GSE243553 genome-wide `MOESM3_ESM.zip` (recorded 403 CONNECT policy denial — **not probed, not retried, no alternative host sought**). No network call of any kind was made this run.

---

## Method / inputs

| Input | Path | Field used |
|---|---|---|
| Coordinate prefixes | `research/modalities/gse243553-eno3-overlap-supplement.json` | `contents['SPRINGER::3::zip']['first_bytes']` |
| Peak counts | `research/modalities/gse243553-eno3-overlap.json` | `peakset_inventory[*].n_intervals` |

Deposit **GSE243553**, primary publication doi `10.1038/s41587-024-02347-4`; fusion oncoproteins expressed in one **HEK293T** background; assembly hg38. **These are the authors' own marker calls — this repository called no peak.**

**Tools:** Python 3.11.15, standard library only (`json`, `itertools`, `math`, `statistics`). No third-party package, no network, no GPU, no paid API, **$0 spend**.

**Substrate rebuilt independently** (`/tmp/claude-0/w19h/substrate.py`, re-typed, importing no object from W19c–W19g): 32 real `Supp_Data_1_new/*_markers.bed` prefixes; trailing partial line discarded; `chr1` records only; `W(A,B) = min(last retained chr1 end)`; Jaccard on **exact interval identity** inside `chr1:0–W`; pair non-degenerate iff both sides hold ≥1 interval in the window; density residual `r = J − mean(J in the pair's |Δlog₁₀ n_intervals| quintile)`, quintiles over the 376 full-panel non-degenerate pairs. I added two assertions the earlier substrate did not carry (`len(names)==32`, and every prefix ascending by start).

**Class inherited verbatim, not redefined:** `SAMEFAM-DIFFGENE-DIFF5'`; families sourced only, ETS = {ERG, FLI1, FEV, ETV1, ETV4}, CREB = {ATF1, CREB1}; any other 3′ partner is UNKNOWN and never matches another UNKNOWN. **No third family. No new split tested.**

**The arm itself:** for each focal peakset, rank *all* its panel partners by residual, mark which pairs are in-class, and report the in-class rank positions. Then the two mundane orderings — `|Δlog₁₀ n_intervals|` and window `W` — computed for the same partners so the reader can see whether the ranking is geometry.

---

## Result

### 0. Gate — ARM 1 reproduced digit-for-digit; **no discrepancy** (PRIMARY)

| Quantity | W19h (this rebuild) | Published ARM 1 | Match |
|---|---|---|---|
| Real BED peaksets | 32 | 32 | ✔ |
| All pairs / non-degenerate | 496 / **376** | 496 / 376 | ✔ |
| Density quintile mean J | 0.0387 / 0.0163 / 0.0126 / 0.0110 / 0.0014 (n=75/75/75/75/76) | same | ✔ |
| SHARES-3 | n=10, mean J 0.1715, residual **+0.1513** | n=10, +0.1513 | ✔ |
| SHARES-5 | n=66, mean J 0.0300, residual **+0.0094** | n=66, +0.0094 | ✔ |
| SHARES-NEITHER | n=300, mean J 0.0077, residual −0.0071 | same | ✔ |
| Class `SAMEFAM-DIFFGENE-DIFF5'` | n=8, mean J 0.1556, residual **+0.1226**; all 8 member residuals matched W19g's table exactly | same | ✔ |

Also reproduced as a sanity constant: the mean residual over all 376 pairs is **+0.000000** by construction, so "above/below zero" is literally "above/below the panel average at matched density".

### 1. `FUS-FEV` × all 31 partners, ranked by residual (PRIMARY)

25 of 31 partners give a non-degenerate pair; 6 are degenerate and excluded (`ACTB-GLI1`, `EPC1-PHF1`, `EWSR1-DDIT3`, `MEAF6-PHF1`, `PAX7-FOXO1`, `TPR-NTRK1`).

| Rank | Partner | J | residual r | in class? | ETS 3′? |
|---|---|---|---|---|---|
| **1** | `EWSR1-FLI1` | 0.2973 | **+0.2586** | **yes** | yes |
| **2** | `EWSR1-ETV1` | 0.2571 | **+0.2185** | **yes** | yes |
| **3** | `EWSR1-ETV4` | 0.1892 | **+0.1505** | **yes** | yes |
| 4 | `EWSR1-FEV` | 0.1667 | **+0.1280** | no — **same 3′ gene**, excluded by the class rule | yes |
| **5** | `TMPRSS2-ERG` | 0.1463 | **+0.1077** | **yes** | yes |
| 6 | `EWSR1-PBX1` | 0.0345 | +0.0219 | no | no |
| 7 | `EWSR1-SP3` | 0.0333 | +0.0171 | no | no |
| 8 | `IRF2BP2-CDX1` | 0.0233 | +0.0122 | no | no |
| 9–25 | 17 peaksets | all J = 0.0000 | −0.0014 → −0.0387 | no | no |

**In-class ranks: 1, 2, 3, 5 of 25.** In-class mean residual **+0.1838** (n=4) against a rest-of-panel mean of **−0.0051** (n=21), rest median **−0.0126**, rest maximum **+0.1280** — and that maximum *is* rank 4, `EWSR1-FEV`.

**The single most informative row is rank 4.** The only peakset that separates the four in-class pairs from a clean top-4 block is `EWSR1-FEV`, which is excluded from the class **solely because it shares the 3′ gene `FEV`** — the most 3′-similar peakset in the whole panel. So `FUS-FEV`'s top five partners are **exactly the five other ETS-3′ peaksets in the panel**, in an unbroken block, and rank 6 falls off a cliff: **+0.1077 → +0.0219**, a factor of ~5.

### 2. `TMPRSS2-ERG` × all 31 partners, ranked by residual (PRIMARY)

Same 25 non-degenerate partners, same 6 exclusions.

| Rank | Partner | J | residual r | in class? |
|---|---|---|---|---|
| **1** | `FUS-FEV` | 0.1463 | **+0.1077** | **yes** |
| **2** | `EWSR1-ETV1` | 0.1081 | **+0.0918** | **yes** |
| **3** | `EWSR1-ETV4` | 0.0789 | **+0.0627** | **yes** |
| **4** | `EWSR1-FLI1` | 0.0930 | **+0.0544** | **yes** |
| **5** | `EWSR1-FEV` | 0.0750 | **+0.0363** | **yes** |
| 6 | `EWSR1-SP3` | 0.0312 | +0.0187 | no |
| 7 | `EWSR1-PBX1` | 0.0345 | +0.0182 | no |
| 8 | `IRF2BP2-CDX1` | 0.0233 | +0.0107 | no |
| 9–25 | 17 peaksets | J ≤ 0.0208 | −0.0014 → −0.0387 | no |

**In-class ranks: 1, 2, 3, 4, 5 of 25 — a perfect top-5 block.** In-class mean **+0.0706** (n=5) vs rest-of-panel **−0.0116** (n=20), rest max **+0.0187**. `TMPRSS2-ERG` has five ETS partners and all five are in class, so here the ETS block and the class block coincide exactly.

### 3. The direct answer to the scoping question (PRIMARY)

**The rank positions do not support the "`FUS-FEV` is a globally high-similarity peakset" reading. They support the family reading — for these six peaksets, on this substrate.**

Three lines of evidence, all descriptive:

1. **Both hubs put every ETS partner at the very top of their own ranking, with a large gap below.** `FUS-FEV`: ETS block occupies ranks 1–5, then a 5× drop. `TMPRSS2-ERG`: ETS block occupies ranks 1–5, then a 3× drop. If `FUS-FEV` were indiscriminately similar to everything, its in-class pairs would be scattered through its own ranking. They are not; they are its ceiling.
2. **`FUS-FEV` is *below* panel average against non-ETS peaksets.** Its rest-of-panel mean residual is **−0.0051** against a panel mean of exactly 0.0000. Removing ETS-vs-ETS pairs entirely — which kills the circularity in any "global similarity" statistic computed over all 32 — drops **all six** ETS peaksets to ranks 16, 20, 21, 23, 26 and 31 of 32, every one of them negative: `EWSR1-FEV` −0.0068, `TMPRSS2-ERG` −0.0116, `EWSR1-FLI1` −0.0116, `FUS-FEV` −0.0118, `EWSR1-ETV1` −0.0131, `EWSR1-ETV4` −0.0161. The top of *that* list is the NR4A3/ATF1 group (`TCF12-NR4A3` +0.0081, `EWSR1-NR4A3` +0.0077, `EWSR1-ATF1` +0.0062). **`FUS-FEV`'s apparent global elevation (rank 3 of 32, +0.0251 over all its pairs) is entirely manufactured by its own ETS partners.** Strip them and it is in the bottom third.
3. **It is not an `EWSR1` effect either.** Four of the six ETS peaksets are `EWSR1-*`, and 13 of 32 panel peaksets are `EWSR1-*` — so "these are all EWSR1 fusions" is the obvious rival. It does not hold: in `FUS-FEV`'s ranking, `EWSR1-POU5F1` sits at rank 22 and `EWSR1-CREB1` at rank 25 (last), both at the floor residual −0.0387, while the non-`EWSR1` peakset `TMPRSS2-ERG` sits at rank 5.

**What this does and does not settle.** It settles that W19g's `FUS-FEV`-dominance observation is **not** explained by `FUS-FEV` being globally promiscuous. It does **not** settle that the effect is the ETS family as a category, because the six ETS peaksets are still only six, three of the four `EWSR1-*×FUS-FEV` pairs are FET↔FET 5′ swaps, and the whole line is exploratory on recycled data. The accurate statement is narrower than "the ETS family clusters" and wider than "`FUS-FEV` is a hub": **within this panel, the six ETS-3′ peaksets are each other's top-ranked partners and are unremarkable against everything else.** W19g's summary — "four `EWSR1-*` ETS peaksets resemble `FUS-FEV` strongly and `TMPRSS2-ERG` weakly" — survives, but this arm adds that the *weak* hub `TMPRSS2-ERG` also shows the clean block structure, which the LOPO arm could not see.

### 4. Substrate geometry — all 32 peaksets, the mundane explanation checked first (PRIMARY)

`n_chr1` = retained chr1 intervals; `last_chr1_end` = last retained chr1 end (the peakset's own window ceiling); `median W` / `min W` = window against the other 31.

| Peakset | n_intervals | n_chr1 | last_chr1_end | median W | min W |
|---|---|---|---|---|---|
| `MEAF6-PHF1` | 150 | 17 | 244,354,165 | 36,412,321 | 4,426,293 |
| `HEY1-NCOA2` | 63 | 8 | 240,672,651 | 36,412,321 | 4,426,293 |
| `ACTB-GLI1` | 45 | 7 | 236,155,846 | 36,412,321 | 4,426,293 |
| `EWSR1-DDIT3` | 22 | 5 | 232,600,025 | 36,412,321 | 4,426,293 |
| `FUS-DDIT3` | 151 | 19 | 229,557,880 | 36,412,321 | 4,426,293 |
| `FUS-ATF1` | 251 | 24 | 225,243,066 | 36,412,321 | 4,426,293 |
| `EPC1-PHF1` | 42 | 4 | 219,310,741 | 36,412,321 | 4,426,293 |
| `PAX7-FOXO1` | 208 | 24 | 209,114,028 | 36,412,321 | 4,426,293 |
| `TPR-NTRK1` | 161 | 24 | 208,184,897 | 36,412,321 | 4,426,293 |
| `SS18L1-SSX1` | 85 | 4 | 81,030,715 | 36,412,321 | 4,426,293 |
| `EWSR1-PBX1` | 1,020 | 26 | 78,944,462 | 36,412,321 | 4,426,293 |
| `EWSR1-NFATC2` | 724 | 26 | 76,107,313 | 36,412,321 | 4,426,293 |
| `EWSR1-NR4A3` | 1,119 | 26 | 59,179,217 | 36,412,321 | 4,426,293 |
| `EWSR1-ATF1` | 1,363 | 26 | 57,518,299 | 36,412,321 | 4,426,293 |
| `TCF12-NR4A3` | 1,411 | 26 | 53,717,864 | 36,412,321 | 4,426,293 |
| **`EWSR1-FEV`** | 2,658 | 26 | 38,053,851 | 36,412,321 | 4,426,293 |
| `IRF2BP2-CDX1` | 762 | 27 | 36,412,321 | 36,412,321 | 4,426,293 |
| `TFG-NR4A3` | 2,272 | 26 | 31,958,072 | 31,958,072 | 4,426,293 |
| `FGFR3-TACC3` | 1,892 | 26 | 30,817,034 | 30,817,034 | 4,426,293 |
| **`EWSR1-FLI1`** | 2,676 | 27 | 30,259,296 | 30,259,296 | 4,426,293 |
| `ETV6-NTRK3` | 2,524 | 26 | 27,011,468 | 27,011,468 | 4,426,293 |
| **`TMPRSS2-ERG`** | 2,527 | 26 | 26,744,528 | 26,744,528 | 4,426,293 |
| `ARFGEF2-HNF4A` | 2,895 | 26 | 24,864,887 | 24,864,887 | 4,426,293 |
| **`FUS-FEV`** | **3,728** | **27** | **24,295,259** | **24,295,259** | 4,426,293 |
| `EWSR1-POU5F1` | 5,785 | 26 | 21,419,165 | 21,419,165 | 4,426,293 |
| **`EWSR1-ETV1`** | 5,121 | 27 | 15,833,768 | 15,833,768 | 4,426,293 |
| **`EWSR1-ETV4`** | 5,805 | 27 | 15,761,103 | 15,761,103 | 4,426,293 |
| `EWSR1-CREB1` | 4,663 | 27 | 14,540,695 | 14,540,695 | 4,426,293 |
| `TAF15-NR4A3` | 8,525 | 27 | 11,733,791 | 11,733,791 | 4,426,293 |
| `EWSR1-YY1` | 7,950 | 28 | 10,249,035 | 10,249,035 | 4,426,293 |
| `CCDC6-RET` | 13,692 | 28 | 6,860,877 | 6,860,877 | 4,426,293 |
| `EWSR1-SP3` | 6,730 | 28 | 4,426,293 | 4,426,293 | 4,426,293 |

Bold = the six ETS-3′ peaksets. **`FUS-FEV` is not a substrate outlier on any of these axes.** Its 3,728 intervals put it 9th of 32 by count, mid-pack among the high-count peaksets and well below `CCDC6-RET` (13,692), `TAF15-NR4A3` (8,525), `EWSR1-YY1` (7,950), `EWSR1-SP3` (6,730), `EWSR1-ETV4` (5,805), `EWSR1-POU5F1` (5,785), `EWSR1-ETV1` (5,121) and `EWSR1-CREB1` (4,663). Its 27 retained chr1 intervals are one below the panel maximum of 28 and equal to five other peaksets. Its window ceiling of 24.3 Mb sits in the middle of the distribution, which spans 4.4 Mb to 244 Mb. The six ETS peaksets do not occupy a distinct band of the table: they are spread from 2,527 to 5,805 intervals and from 15.8 Mb to 38.1 Mb of window ceiling, interleaved with non-ETS peaksets throughout.

**The direct test of the two mundane orderings is decisive against them.** For `FUS-FEV`, the partner **nearest** in `|Δlog₁₀ n_intervals|` is `EWSR1-CREB1` (Δ = 0.0972), which ranks **25th of 25** on residual, at the floor; the second nearest, `ARFGEF2-HNF4A` (Δ = 0.1098), ranks **24th**. Meanwhile rank 3, `EWSR1-ETV4`, is only the **9th** nearest by count. For `TMPRSS2-ERG` the pattern is starker: its **closest** partner by interval count is `ETV6-NTRK3` (Δ = 0.0005 — essentially identical counts, 2,524 vs 2,527), and it ranks **25th of 25**, at the floor; `TFG-NR4A3` (Δ = 0.0462, 4th nearest) ranks 24th. Window size fails equally: `EWSR1-SP3` has the **smallest** window against both hubs (4.4 Mb) and ranks only 7th and 6th, while `TFG-NR4A3` and `TCF12-NR4A3` sit in the largest-window band and rank 21st–24th.

So neither interval count nor window geometry orders these rankings. **The mundane explanations are checked and they do not hold.** Note this is not a surprise for interval count specifically — the residual is *constructed* to remove it — but the check confirms the residual is doing its job rather than leaving a monotone remainder, and window geometry was never controlled for at all and is now shown not to matter here.

**PREDICTION rows: none.** No model output, extrapolation or projection appears in this report. **UNKNOWN:** everything genome-wide; the CREB arm (still one candidate, still lost to prefix geometry, not revisited here); wild-type `NR4A3` and reciprocal `NR4A3-EWSR1`, which have no marker BED in the supplement at all — that is a missing file, **not** a tested-and-empty result.

---

## Validation evidence

All **RUN**. Nothing here is `PROPOSED (NOT RUN)`. No network call was made.

**RUN — command 1 (start state).**
```
date -u && git rev-parse HEAD && git status --porcelain && env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'
```
→ `Tue Sep  8 03:05:02 UTC 2026`; HEAD `4bd79b3bca255451dc5b25aaafa882e0ebed02e8`; `git status --porcelain` **empty**; env as quoted above. **Exit 0.**

**RUN — command 2 (substrate rebuild + ARM 1 gate).**
```
cd /tmp/claude-0/w19h && python3 --version && python3 gate.py; echo "EXIT=$?"
```
Environment: Python 3.11.15, stdlib only. **`EXIT=0`.** Verbatim:
```
real BED peaksets: 32
all pairs: 496  non-degenerate: 376
density quintiles: Q1=0.0387(n=75) Q2=0.0163(n=75) Q3=0.0126(n=75) Q4=0.0110(n=75) Q5=0.0014(n=76)
  SHARES-3        n= 10 mean J 0.1715 mean residual +0.1513
  SHARES-5        n= 66 mean J 0.0300 mean residual +0.0094
  SHARES-NEITHER  n=300 mean J 0.0077 mean residual -0.0071
```
All three assertions in `substrate.py` passed silently (name-set equality, `len(names)==32`, every prefix ascending).

**RUN — command 3 (the scoping arm).**
```
cd /tmp/claude-0/w19h && python3 scope.py; echo "EXIT=$?"
```
**`EXIT=0`.** Verbatim key output:
```
=== CLASS (inherited, unchanged): n=8  mean J 0.1556  mean residual +0.1226 ===
   EWSR1-ETV1       x FUS-FEV           J=0.2571  r=+0.2185
   EWSR1-ETV1       x TMPRSS2-ERG       J=0.1081  r=+0.0918
   EWSR1-ETV4       x FUS-FEV           J=0.1892  r=+0.1505
   EWSR1-ETV4       x TMPRSS2-ERG       J=0.0789  r=+0.0627
   EWSR1-FEV        x TMPRSS2-ERG       J=0.0750  r=+0.0363
   EWSR1-FLI1       x FUS-FEV           J=0.2973  r=+0.2586
   EWSR1-FLI1       x TMPRSS2-ERG       J=0.0930  r=+0.0544
   FUS-FEV          x TMPRSS2-ERG       J=0.1463  r=+0.1077

=== FOCAL FUS-FEV : all panel partners ranked by residual (descending) ===
partners with a non-degenerate pair: 25 of 31   degenerate/excluded: 6 ['ACTB-GLI1', 'EPC1-PHF1', 'EWSR1-DDIT3', 'MEAF6-PHF1', 'PAX7-FOXO1', 'TPR-NTRK1']
  rank  1/25  EWSR1-FLI1        J=0.2973  r=+0.2586  << IN-CLASS
  rank  2/25  EWSR1-ETV1        J=0.2571  r=+0.2185  << IN-CLASS
  rank  3/25  EWSR1-ETV4        J=0.1892  r=+0.1505  << IN-CLASS
  rank  4/25  EWSR1-FEV         J=0.1667  r=+0.1280
  rank  5/25  TMPRSS2-ERG       J=0.1463  r=+0.1077  << IN-CLASS
  rank  6/25  EWSR1-PBX1        J=0.0345  r=+0.0219
  rank  7/25  EWSR1-SP3         J=0.0333  r=+0.0171
  rank  8/25  IRF2BP2-CDX1      J=0.0233  r=+0.0122
  IN-CLASS ranks: [1, 2, 3, 5] of 25   (top-4 block? False)
  mean residual in-class +0.1838 (n=4) vs rest-of-panel -0.0051 (n=21); median rest -0.0126; max rest +0.1280

=== FOCAL TMPRSS2-ERG : ... ===
  rank  1/25  FUS-FEV           J=0.1463  r=+0.1077  << IN-CLASS
  rank  2/25  EWSR1-ETV1        J=0.1081  r=+0.0918  << IN-CLASS
  rank  3/25  EWSR1-ETV4        J=0.0789  r=+0.0627  << IN-CLASS
  rank  4/25  EWSR1-FLI1        J=0.0930  r=+0.0544  << IN-CLASS
  rank  5/25  EWSR1-FEV         J=0.0750  r=+0.0363  << IN-CLASS
  IN-CLASS ranks: [1, 2, 3, 4, 5] of 25   (top-5 block? True)
  mean residual in-class +0.0706 (n=5) vs rest-of-panel -0.0116 (n=20); median rest -0.0126; max rest +0.0187
```
(Ranks 9–25 of both rankings and the full 32-row geometry table are verbatim in the tool log and transcribed in the Result section.)

**RUN — command 4 (mundane-explanation checks).**
```
cd /tmp/claude-0/w19h && python3 mundane.py; echo "EXIT=$?"
```
**`EXIT=0`.** Verbatim key output:
```
ETS peaksets in panel (6): ['EWSR1-ETV1', 'EWSR1-ETV4', 'EWSR1-FEV', 'EWSR1-FLI1', 'FUS-FEV', 'TMPRSS2-ERG']
overall mean residual over all 376 non-degenerate pairs: +0.000000
=== per-peakset mean residual, ETS-vs-ETS pairs REMOVED ===
  rank  1  TCF12-NR4A3        mean r +0.0081 over 27 non-ETS-ETS pairs
  ...
  rank 16  EWSR1-FEV          mean r -0.0068 over 22 non-ETS-ETS pairs [ETS]
  rank 20  TMPRSS2-ERG        mean r -0.0116 over 20 non-ETS-ETS pairs [ETS]
  rank 21  EWSR1-FLI1         mean r -0.0116 over 20 non-ETS-ETS pairs [ETS]
  rank 23  FUS-FEV            mean r -0.0118 over 20 non-ETS-ETS pairs [ETS]
  rank 26  EWSR1-ETV1         mean r -0.0131 over 19 non-ETS-ETS pairs [ETS]
  rank 31  EWSR1-ETV4         mean r -0.0161 over 19 non-ETS-ETS pairs [ETS]
-- FUS-FEV (n_int=3728, last_chr1_end=24295259) --
   1 EWSR1-FLI1       +0.2586     0.1440     24295259        4       13  ETS
   ...
  24 ARFGEF2-HNF4A    -0.0387     0.1098     24295259        2        9
  25 EWSR1-CREB1      -0.0387     0.0972     14540695        1        5
-- TMPRSS2-ERG (n_int=2527, last_chr1_end=26744528) --
   1 FUS-FEV          +0.1077     0.1689     24295259        7        9  ETS
   ...
  25 ETV6-NTRK3       -0.0387     0.0005     26744528        1       11
```

**RUN — command 5 (end state + HEAD-move impact).**
```
date -u && git rev-parse HEAD && echo "STATUS:[$(git status --porcelain)]" && git diff --stat 4bd79b3…..HEAD -- research/modalities/gse243553-eno3-overlap.json research/modalities/gse243553-eno3-overlap-supplement.json; echo "INPUTS_DIFF_EXIT=$?"; ls -1 /tmp/claude-0/w19h/
```
→ `Tue Sep  8 03:07:12 UTC 2026`; HEAD **`98a0833f1ede2cf9cef13790388260567a32e868`**; `STATUS:[]` (**empty**); the input diff printed **nothing** with `INPUTS_DIFF_EXIT=0` — both inputs byte-identical across the HEAD move; four `.py` files, all under `/tmp/claude-0/w19h/`. **No repository file created, modified or deleted.**

### Code (returned inline, not written into the tree)

`/tmp/claude-0/w19h/substrate.py`:
```python
"""W19h substrate rebuild - independent re-parse from the two committed JSONs.
Gate: reproduce published ARM 1 (376 non-degenerate; SHARES-3 n=10 r=+0.1513;
SHARES-5 n=66 r=+0.0094). Nothing imported from W19c/d/e/f/g."""
import json, itertools, math, statistics

REPO="/home/user/Rare-cancers"
sup=json.load(open(REPO+"/research/modalities/gse243553-eno3-overlap-supplement.json"))
fb=sup["contents"]["SPRINGER::3::zip"]["first_bytes"]
inv=json.load(open(REPO+"/research/modalities/gse243553-eno3-overlap.json"))["peakset_inventory"]

real={k:v for k,v in inv.items() if "__MACOSX" not in k and "Supp_Data_1_new/" in k and k.endswith(".bed")}

def parse_prefix(s):
    lines=s.split("\n")
    if not s.endswith("\n"): lines=lines[:-1]      # discard trailing partial line
    out=[]
    for ln in lines:
        p=ln.split("\t")
        if len(p)<3 or p[0]!="chr1": continue      # chr1 only
        try: out.append((int(p[1]),int(p[2])))
        except ValueError: continue
    return out

peaks={}; names=[]
for k,s in fb.items():
    if "__MACOSX" in k or not k.endswith("_markers.bed"): continue
    nm=k.split("/")[-1][:-len("_markers.bed")]
    peaks[nm]=parse_prefix(s); names.append(nm)
names.sort()
nint={k.split("/")[-1][:-len("_markers.bed")]:v["n_intervals"] for k,v in real.items()}
assert set(nint)==set(names), "name set mismatch between inventory and prefixes"
assert len(names)==32, len(names)
for nm in names:
    A=peaks[nm]
    assert all(A[i][0]<=A[i+1][0] for i in range(len(A)-1)), "not ascending: "+nm

def jac(a,b):
    A,B=peaks[a],peaks[b]
    if not A or not B: return None
    W=min(A[-1][1],B[-1][1])
    SA={iv for iv in A if iv[1]<=W}; SB={iv for iv in B if iv[1]<=W}
    if not SA or not SB: return None               # non-degenerate iff both hold >=1
    return len(SA&SB)/len(SA|SB)

J={}
for a,b in itertools.combinations(names,2): J[(a,b)]=jac(a,b)
good=[p for p in J if J[p] is not None]

d={p:abs(math.log10(nint[p[0]])-math.log10(nint[p[1]])) for p in good}
order=sorted(good,key=lambda p:d[p]); q=max(1,len(order)//5); bin_of={}
for i,p in enumerate(order): bin_of[p]=min(4,i//q)
bmean={b:statistics.mean([J[p] for p in good if bin_of[p]==b]) for b in range(5)}
R={p:J[p]-bmean[bin_of[p]] for p in good}

def split(nm):
    i=nm.index("-"); return nm[:i],nm[i+1:]
G={n:split(n) for n in names}
```

`/tmp/claude-0/w19h/scope.py` (the arm; `gate.py` and `mundane.py` are in the tool log and are mechanical extensions of the same two blocks):
```python
"""
W19h - SCOPING ARM (descriptive, distribution-free). NO p-VALUE IS COMPUTED HERE.

Question: is the SAMEFAM-DIFFGENE-DIFF5' class residual family signal or FUS-FEV signal?
Method: for each focal peakset, rank ALL its 31 pair residuals across the panel
(degenerate pairs excluded and listed), and report where its in-class pairs fall.
Class inherited VERBATIM from W19e/W19f/W19g; no family added, no new split tested.
"""
exec(open('/tmp/claude-0/w19h/substrate.py').read())
import statistics

FAM={"FLI1":"ETS","ERG":"ETS","FEV":"ETS","ETV1":"ETS","ETV4":"ETS",
     "ATF1":"CREB","CREB1":"CREB"}
def fam(g): return FAM.get(g)
def in_class(a,b):
    a5,a3=G[a]; b5,b3=G[b]
    fa,fb=fam(a3),fam(b3)
    if fa is None or fb is None: return False
    if fa!=fb: return False
    if a3==b3: return False
    if a5==b5: return False
    return True

full=sorted([p for p in good if in_class(*p)])
print("=== CLASS (inherited, unchanged): n=%d  mean J %.4f  mean residual %+.4f ==="
      %(len(full),statistics.mean([J[p] for p in full]),statistics.mean([R[p] for p in full])))
for a,b in full: print("   %-16s x %-16s  J=%.4f  r=%+.4f"%(a,b,J[(a,b)],R[(a,b)]))

def key(a,b): return (a,b) if (a,b) in J else (b,a)

def focal(f):
    print("\n=== FOCAL %s : all panel partners ranked by residual (descending) ==="%f)
    rows=[]; degen=[]
    for o in names:
        if o==f: continue
        k=key(f,o)
        if J[k] is None: degen.append(o); continue
        rows.append((R[k],J[k],o,in_class(*k)))
    rows.sort(reverse=True)
    n=len(rows)
    print("partners with a non-degenerate pair: %d of 31   degenerate/excluded: %d %s"%(n,len(degen),sorted(degen)))
    for i,(r,j,o,ic) in enumerate(rows,1):
        print("  rank %2d/%d  %-16s  J=%.4f  r=%+.4f  %s"%(i,n,o,j,r,"<< IN-CLASS" if ic else ""))
    ic_ranks=[i for i,(r,j,o,ic) in enumerate(rows,1) if ic]
    ic_r=[r for (r,j,o,ic) in rows if ic]
    oth_r=[r for (r,j,o,ic) in rows if not ic]
    print("  IN-CLASS ranks: %s of %d   (top-%d block? %s)"
          %(ic_ranks,n,len(ic_ranks),ic_ranks==list(range(1,len(ic_ranks)+1))))
    print("  mean residual in-class %+.4f (n=%d) vs rest-of-panel %+.4f (n=%d); median rest %+.4f; max rest %+.4f"
          %(statistics.mean(ic_r),len(ic_r),statistics.mean(oth_r),len(oth_r),
            statistics.median(oth_r),max(oth_r)))

focal("FUS-FEV")
focal("TMPRSS2-ERG")
```

---

## Limitations

- **This is a reproducible EXPLORATORY successor on recycled data, and nothing in it is confirmation.** The DBD-family rule was fixed *after* the same residuals had already been viewed, and every arm in the W19d→W19h line — this one included — re-uses the same 32 peaksets. **Nothing is held out.** Do not describe any part of this as prespecified, as independent replication, or as confirmation of W19e/W19f/W19g. It is one more view of one dataset.
- **No p-value, by design, and none may be back-fitted onto these ranks.** Rank positions in a ranking whose ordering statistic was already inspected are not a test. Any "top-5 of 25" figure computed from this table would be a post-hoc probability on the same data and is not offered.
- **Descriptive gaps are not effect sizes.** The 5× drop at rank 6 in `FUS-FEV`'s ranking has no confidence interval here, and none is computable without a null I have deliberately not run.
- **The truncation is severe and is the ceiling on the whole line.** These are ≤600-byte BED prefixes: 4 to 28 retained chr1 intervals per peakset out of 22 to 13,692 genome-wide. The rankings describe the first few megabases of chr1 and nothing else. The genome-wide `MOESM3_ESM.zip` is a **recorded 403 CONNECT policy denial** — not probed, not retried, no alternative host sought.
- **Six ETS peaksets, four of them `EWSR1-*`.** Three of the four `EWSR1-*×FUS-FEV` pairs differ from their partner only by a FET↔FET (EWSR1↔FUS) 5′ swap. I ruled out "EWSR1-ness" as the driver using the ranking itself, but I cannot separate an ETS-family effect from a FET-5′-context effect on six peaksets.
- **The residual controls interval count, not window size, GC, mappability, or peak strength.** I showed window size does not order these rankings, which is weaker than showing it cannot matter.
- **`n_intervals` comes from the inventory JSON and describes the full genome-wide BED, while the Jaccard describes the chr1 prefix.** The density control therefore matches pairs on a genome-wide quantity while measuring a local one. That was true of every arm in this line and is inherited, not introduced here.
- **HEK293T is not EMC.** This is one immortalised cell background with ectopically expressed fusion proteins. **Nothing here transfers to any tumour or any patient**, and no clinical claim of any kind is made or supported. There is no wet lab; nothing here is experimental validation.
- **No claim is made about clinical practice.** W19g checked and found no claim of fusion-partner interchangeability anywhere in this evidence chain, and I did not reintroduce one — it would be unsourced.
- **`EWSR1-FEV`'s position at rank 4 is a fact about the class definition, not a new result.** It is excluded because it shares the 3′ gene; noting that it completes the ETS block is an observation, not a redefinition, and I did not re-run anything with a changed class.
- **UNKNOWN stays UNKNOWN:** the CREB arm, wild-type `NR4A3`, reciprocal `NR4A3-EWSR1`, and everything outside the retained chr1 prefixes. A missing marker BED is a missing file, not a measured zero.

---

## Tool-call and wall-clock count actually used

**9 tool calls** (8 Bash, 1 Grep-equivalent run inside Bash per the auto-mode instruction; no Read/Write/Edit tool used, no network tool used). **Wall clock 03:05:02Z → 03:07:12Z = 2 min 10 s**, well inside the ~40 call / ~40 min target. Spend **$0**: stdlib Python only, no paid API, no GPU, no network.

---

## Next concrete action

**One successor, and it is the last one this substrate can carry honestly.** Every arm since W19d has re-used the same 32 truncated chr1 prefixes, and this arm has now used the ranking structure itself — the most informative remaining view of that substrate. The one thing not yet done that would not be a post-hoc split is a **pre-registered, held-out replication of the block structure on a different chromosome or a different deposit**: fix the ETS family list and the block-structure prediction *in writing before looking*, then evaluate it on peaksets this line has never seen. That requires either the genome-wide GSE243553 BEDs (one recorded 403 away — **must not be re-probed**) or a different fusion-oncoprotein ChIP/CUT&RUN panel entirely, which is a new-source-access question, not an analysis question.

**Therefore, honestly: there is no viable purely-computational successor inside lane 19 on the retained data.** Further re-analysis of these 32 prefixes cannot raise the finding above an exploratory association, and each additional arm increases the multiplicity burden on a dataset that has now been viewed many times. My recommendation to the coordinator is to **close the W19d→W19h line here**, record its conclusion as a single exploratory association with the scoping result attached, and route any continuation to source access rather than to another arm.

**Explicitly not successors:** a third DBD family (post-hoc redefinition after seeing these results); any leave-two-peaksets-out arm (below the n ≥ 4 floor by construction); any p-value attached to the rankings in this report; and any re-probe of the denied genome-wide route.
