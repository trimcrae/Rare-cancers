> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git tree; the coordinator is the sole collector.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check done: `git status --porcelain` shows only the coordinator's own untracked directory — no repository writes. All execution under `/tmp/claude-0/w02b`. Report follows.

---

# W02b — How much of the retained EMC bulk expression signal could be non-tumour in origin?

## Worker

- **Worker ID:** W02b (refill for lane 2), OPUS-CAPACITY-CAMPAIGN-20260908
- **Lane:** Lane 2 — EMC microenvironment. Successor question to W02, taken on retained data only.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I self-report as Claude Opus 5 (`claude-opus-5`), running as Claude Code in the Anthropic Cloud remote environment. **This is a self-report and must not be treated as an observed fact.** As W02 found, **no `ANTHROPIC_MODEL` variable exists in this environment**, so the served model is not confirmable from inside the session. The coordinator must extract the actual runtime model from the transcript.
- **Write isolation:** READ-ONLY on the Git tree, honoured. All execution in `/tmp/claude-0/w02b/`. `git status --porcelain` at end returns exactly one line, `?? research/autonomy/opus-capacity-campaign-20260908/` — the coordinator's own untracked directory. **No file written, moved or deleted anywhere under `/home/user/Rare-cancers`. No git operation of any kind.**

`date -u` at start: `Tue Sep  8 02:02:22 UTC 2026`. At end: `Tue Sep  8 02:06:47 UTC 2026`.

Literal output of the required env command (proxy/`no_proxy`/`JAVA_TOOL_OPTIONS` lines are present in the raw output and are elided here as noise — the elision is declared rather than made silently; secrets redacted by the prescribed `sed`):

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
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE=cloud_default
CLAUDE_CODE_REMOTE_SESSION_ID=cse_01Eui7FVgatEXAwt2N35yHH6
CLAUDE_CODE_SESSION_ID=8ecd0f49-96ba-5dcf-b11a-af5e48bdec71
CLAUDE_CODE_USER_EMAIL=trimcrae@gmail.com
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_WORKER_EPOCH=1
CLAUDE_EFFORT=medium
CLAUDE_PID=522
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
SESSION_INGRESS_URL=https://api.anthropic.com
```

**No `ANTHROPIC_MODEL` key present.** Model identity is UNKNOWN from the environment.

---

## Question

**How much of the retained EMC bulk expression signal could be non-tumour in origin, and can a defensible upper bound be put on the stromal/matrix share using a marker-based, reference-free approach that needs no external reference matrix?**

Open because the repository asserts the limitation qualitatively in at least four places ("bulk archival tissue cannot separate the tumour compartment from the stroma") and has never attached a number to it, and because the committed `read_19_IMMUNE_TME` names this exact quantity as its own gap: *"(4) With 6 and 10 EMC tumours it cannot estimate what FRACTION of EMC is infiltrated, which is the quantity a patient-selection argument would need."*

**W02's negative is preserved intact and is not softened anywhere below.** No public single-cell, single-nucleus or spatial-transcriptomic dataset containing EMC tissue was retrieved; transfer limits T1–T4 stand as written. The NNLS-against-Subramanian route W02 proposed is **blocked** by the same egress wall and **was not attempted** — no network call of any kind was made in this task.

---

## Prior-work check

Commands run, verbatim, and what they showed:

| Command | Result |
|---|---|
| `rg -n "GSE4303\|GSE28866\|GSE24369" research/modalities/ \| head -40` | hits are **code and derived JSON only** — `nr4a3_fusion_targets.py`, `emc_prmt5_effect_sizes.py`, `nr4a3-fusion-targets-confounds.json`. Every hit names `*_series_matrix.txt.gz` as a **target filename**, never as a committed file. |
| `find . -path ./.git -prune -o \( -iname "*series_matrix*" -o -iname "*.txt.gz" -o -iname "*.CEL*" \) -print` | **Zero series-matrix files.** The only `.txt.gz` expression files in the tree are `research/modalities/_s4_lane_inputs/GSM281775-8.soft.txt.gz`. |
| `zcat research/modalities/_s4_lane_inputs/GSM281775.soft.txt.gz \| head -60` | `!Sample_title = 293-tet-On-NOR1 without doxycycline`; `!Sample_series_id = GSE11185`; GPL570; 54,675 rows. **HEK293 tet-On NOR1 overexpression — a cell line with no microenvironment**, exactly parallel to W02's T3 finding about `GSE243553`. |
| `git ls-files \| rg -i "\.gz$\|series_matrix\|matrix"` | confirms the same: no EMC tissue matrix under version control. |
| `rg -l "PTPRC" --glob '!.git'` | 13 files; the informative one is `research/modalities/emc-expression-panels.json` (13 MB). |
| Python structural walk of `emc-expression-panels.json` | **`gene_reads` holds 479 genes with full `per_sample` records — `gsm`, `class`, `value`, `z_vs_array`, `array_percentile` — for both EMC cohorts.** |
| Read of `reads.read_19_IMMUNE_TME` | asks whether immune modules are up/down **versus comparator sarcomas**; explicitly disclaims the fraction question. My estimand is different and is the gap that read names. |

**Closed items confirmed not replayed.** `GSE4303`/`GSE28866` are not re-discovered or re-headered — I use the *already-derived, already-committed* cache, which `CLOSED-WORK.md` treats as retained analysis rather than new data. No new cohort is claimed. The ASO/NAT and tissue-RNA deliverables, the frozen external-validation comment, and the restricted NR4A Perspective review were not touched. No denied route was replayed; no route was attempted at all.

### Step-1 verdict, stated plainly as instructed

**Per-gene expression values ARE committed — but not as expression matrices, and not for the whole transcriptome.**

- What is **NOT** in the tree: any `series_matrix.txt.gz`, any CEL file, any per-probe matrix for `GSE4303`, `GSE24369` or `GSE28866`. Every script that names them **downloads them at CI time**; the repository stores only outputs.
- What **IS** in the tree: `research/modalities/emc-expression-panels.json`, a derived cache holding, for a **curated 479-gene panel**, per-sample `value`, `z_vs_array` and `array_percentile` for every sample of both readable EMC series. After requiring a value in every sample, this yields **464 genes × 35 samples on GPL6244** and **418 genes × 16 samples on GPL3290**.

That cache is enough for a marker-based, rank-based analysis and is **not** enough for anything transcriptome-wide. Everything below is therefore a statement about a 464/418-gene curated panel, never about the transcriptome, and I say so at every result.

---

## Method / inputs

| Item | Detail |
|---|---|
| Sole data input | `/home/user/Rare-cancers/research/modalities/emc-expression-panels.json` (`generated_utc` 2026-08-29T12:51:32+00:00), read-only |
| Cohort A | `GSE24369` / **GPL6244** Affymetrix Gene ST, single-channel intensity. n = 6 EMC, 29 comparator (LGFMS 17, desmoid fibromatosis 6, fibrosarcoma 6). `value_kind`: *"single-channel intensity (an absolute level is interpretable only relative to this array's own probe distribution)"* |
| Cohort B | `GSE4303` / **GPL3290** two-colour cDNA. n = 10 EMC, 6 comparator (DFSP 3, GIST 3). `value_kind`: **"two-colour log-ratio vs a reference pool (RELATIVE — an absolute level is NOT interpretable; only the between-group contrast is)"** |
| Environment | `python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]`, `numpy 2.4.6`, `scipy 1.17.1`, Linux; `/tmp/claude-0/w02b/` |
| Network | **none.** No egress attempt was made. |
| Scripts | `extract.py`, `fast.py`, `topsignal.py` (reproduced in full below) |

### Why rank-based, and why not deconvolution

Reference-free scoring on the **`array_percentile`** scale, not absolute deconvolution, for three reasons that are properties of these data, not preferences:

1. **The two platforms are not in comparable units.** GPL6244 percentiles rank a single-channel intensity; GPL3290 percentiles rank a **log-ratio against a reference pool**. Any absolute-unit method (NNLS, CIBERSORT, EPIC) would be silently mixing an abundance scale with a contrast scale. So: **no cross-platform pooling anywhere.** The two cohorts are analysed separately and compared only by the **sign** of a within-platform contrast.
2. **Deconvolution needs a reference basis matrix, and the repository has none.** That is exactly the object W02 identified as sitting behind the egress wall, so this analysis is designed to need no basis at all.
3. **Percentile is within-array normalised by construction**, which removes the per-array scaling and labelling-efficiency terms that would otherwise dominate a 2005-era two-colour cDNA array.

### Marker sets (published, canonical lineage markers)

Chosen as canonical lineage markers, restricted to what the committed panel actually carries. Each is a standard lineage marker in the cited sense; **none is a published composite signature, and no published signature is reproduced.**

- **(a) Immune / leukocyte (12):** `PTPRC` (CD45, pan-leukocyte), `CD2`, `CD3D`, `CD3E`, `CD8A` (T cell), `CD68`, `CD163`, `CSF1R`, `ITGAM` (monocyte/macrophage), `HLA-DRA` (APC), `MS4A1` (CD20, B cell), `GZMB` (cytotoxic).
- **(b) Endothelium (6):** `PECAM1` (CD31), `VWF`, `CDH5` (VE-cadherin), `KDR` (VEGFR2), `FLT1` (VEGFR1), `MCAM` (CD146 — **flagged ambiguous**, also pericyte/perivascular).
- **(c) Fibroblast / ECM (14):** `COL1A1`, `COL1A2`, `COL3A1`, `COL5A1`, `COL11A1`, `DCN`, `LUM`, `POSTN`, `FN1` (**flagged ambiguous**, near-ubiquitous), `FAP`, `THY1`, `PDGFRA`, `PDGFRB`, `ACTA2` (**flagged ambiguous**, smooth-muscle/myofibroblast).
- **(d) EMC tumour compartment (9):** `NR4A3` plus the retained co-expressed / neuroendocrine-leaning set the repository already reads — `PPARG`, `RET`, `INSM1`, `SYP`, `CHGA`, `ENO2`, `KIT`, `CD24`. `NR2F1` is `readable: false` on **both** platforms and is excluded (absent reading, not a reading of absence).
- **Deliberately assigned to neither compartment:** `ACAN`, `COL2A1`, `SOX9`. In EMC the chondroid/matrix axis is genuinely ambiguous between tumour product and stromal product; forcing them either way would manufacture the answer. They are excluded from all scores and from the gene set being explained.

Three estimands were computed. **Every one of them is a PREDICTION about composition. None is a measured cell fraction.**

---

## Result

### R1 — What is committed (the step-1 answer)

| Row | Finding |
|---|---|
| **PRIMARY** | No expression matrix for `GSE4303`, `GSE24369` or `GSE28866` is committed to the repository. The only committed raw expression files are `GSM281775–GSM281778` = `GSE11185`, HEK293 tet-On NOR1 ± doxycycline, GPL570 — a **cell line with no microenvironment**. |
| **PRIMARY** | Per-sample per-gene values *are* committed, as a derived 479-gene panel cache in `emc-expression-panels.json`, carrying `array_percentile` for **6 EMC + 29 comparator (GPL6244)** and **10 EMC + 6 comparator (GPL3290)**. |
| **PRIMARY** | Complete-case panel size: **464 genes (GPL6244)**, **418 genes (GPL3290)**; 335 of the GPL3290 genes are complete across the 10 EMC samples. |

### R2 — Estimand A: compartment marker levels by tumour class (ordinal)

Mean `array_percentile` of each marker set, by class. **GPL6244 only is interpretable as a level**; the GPL3290 block is a percentile of a **log-ratio against a reference pool**, so it is reported for contrast structure and **must not be read as abundance**.

**GPL6244 (single-channel intensity) — PRIMARY**

| Marker set | desmoid (n=6) | fibrosarcoma (n=6) | LGFMS (n=17) | **EMC (n=6)** | markers readable |
|---|---|---|---|---|---|
| fibroblast/ECM | **0.990** | 0.923 | 0.887 | **0.870** | 14/14 |
| endothelium | 0.756 | 0.775 | 0.690 | **0.469** | 6/6 |
| immune/leukocyte | 0.526 | 0.630 | 0.549 | **0.403** | 12/12 |
| EMC tumour set | 0.498 | 0.533 | 0.560 | **0.606** | 9/9 |

**GPL3290 (two-colour log-ratio — CONTRAST ONLY, not abundance) — SECONDARY**

| Marker set | DFSP (n=3) | GIST (n=3) | **EMC (n=10)** |
|---|---|---|---|
| EMC tumour set | 0.356 | 0.656 | **0.841** |
| endothelium | 0.781 | 0.650 | **0.675** |
| fibroblast/ECM | 0.750 | 0.664 | **0.617** |
| immune/leukocyte | 0.323 | 0.524 | **0.372** |

Reading, on GPL6244 and stated as ordinal: **the ECM/fibroblast axis sits at the 87th percentile of the array in EMC, while the leukocyte axis sits at the 40th percentile — below the array median — and the endothelial axis at the 47th.** The matrix compartment, not the immune compartment, is where the non-tumour risk to an EMC bulk finding lives. This is a **PREDICTION** about compartment abundance from marker rank; it is not a cell count, and no cardinal cell fraction is derivable from it (see Limitations).

### R3 — Estimand B: variance bound. **The informative result is that this route fails, and why.**

Within platform, EMC samples only: a composite non-tumour score (mean of z-standardised immune, endothelial and fibro/ECM scores) was correlated with every **non-marker** panel gene across EMC samples; the reported statistic is the mean R². The null replaces the marker sets with random size-matched panel gene sets, 5,000 permutations.

| Arm | Configuration | n EMC | genes scored | **observed mean R²** | median R² | null mean | null p95 | null p99 | perm. p |
|---|---|---|---|---|---|---|---|---|---|
| GPL6244 | full (imm+endo+fibro) | 6 | 420 | **0.2065** | 0.1057 | 0.2915 | 0.3738 | 0.3845 | 0.863 |
| GPL6244 | drop ambiguous ACTA2/MCAM/FN1 | 6 | 420 | 0.2092 | 0.1086 | 0.2871 | 0.3752 | 0.3846 | 0.834 |
| GPL6244 | immune only | 6 | 420 | 0.2314 | 0.1392 | 0.2737 | 0.3728 | 0.3834 | 0.683 |
| GPL6244 | endothelium only | 6 | 420 | 0.2850 | 0.2214 | 0.2616 | 0.3687 | 0.3812 | 0.420 |
| GPL6244 | fibro/ECM only | 6 | 420 | 0.2115 | 0.1330 | 0.2792 | 0.3740 | 0.3844 | 0.774 |
| GPL3290 | full (imm+endo+fibro) | 10 | 305 | **0.1641** | 0.1004 | 0.1742 | 0.2330 | 0.2475 | 0.597 |
| GPL3290 | drop ambiguous | 10 | 305 | 0.1657 | 0.1151 | 0.1717 | 0.2343 | 0.2478 | 0.547 |
| GPL3290 | immune only | 10 | 305 | 0.1180 | 0.0653 | 0.1545 | 0.2332 | 0.2505 | 0.778 |
| GPL3290 | endothelium only | 10 | 305 | 0.1184 | 0.0676 | 0.1573 | 0.2358 | 0.2532 | 0.798 |
| GPL3290 | fibro/ECM only | 10 | 305 | 0.1788 | 0.1222 | 0.1669 | 0.2378 | 0.2524 | 0.396 |

Row class: **PREDICTION** (all rows). Uncertainty definition: the null column is the empirical distribution of the same statistic under 5,000 size-matched random gene sets drawn from the same panel and the same samples; `perm. p` is the fraction of null draws at least as large as the observed mean R².

**In every one of the ten configurations, the observed mean R² is at or below the null mean, and no configuration approaches significance (min p = 0.396).** A random 32-gene score already explains ~29% of across-sample panel variance at n = 6 and ~17% at n = 10, purely because a correlation over 6 or 10 points has an expected R² near 1/(n−1).

The honest bound this yields:

> **BOUND (variance route).** At the 95th percentile of the permutation null, **≤ 37.4% (GPL6244, n = 6)** and **≤ 23.3% (GPL3290, n = 10)** of retained-panel across-sample variance in EMC is attributable to composition. **This ceiling is the noise floor of the sample size, not a property of EMC.** The observed marker-driven value lies *below* it, so the data do not distinguish a real compositional axis from an arbitrary gene set. The across-sample-variance route to a stromal fraction **cannot be made informative at n = 6 and n = 10**, however good the marker sets are.

That is a generalisable methodological result: it applies to any bulk compositional claim made on either of these two EMC cohorts, including a future NNLS one.

### R4 — Estimand C: composition of the strongest EMC signal. **This is the number that survives.**

Rank the complete-case panel genes by mean EMC `array_percentile`; ask what share of the top tier is non-tumour-attributable. "Canonical" = a defined marker of (a)/(b)/(c). "Lexical" = a declared regex heuristic over gene symbols (`COL\d|MMP\d|TIMP\d|LAM[ABC]\d|ITGA|ITGB|FBN|FBLN|SERPIN|SPARC|LOX|ADAMTS|HAS\d|VCAN|BGN|ELN|NID\d|THBS\d|CTSK|CD\d|HLA-|IL\d|CXCL|CCL|TNF|IFN`), which **over-calls on purpose** so the sum is an upper share. It is a lexical heuristic, not an annotation database.

| Arm | Tier | n genes | canonical non-tumour | lexical add'l | **upper non-tumour share** | canonical tumour markers |
|---|---|---|---|---|---|---|
| GPL6244 | top 10% (pct ≥ 0.962) | 46 | 3 (6.5%) | 7 (15.2%) | **21.7%** | 0 |
| GPL6244 | top 20% (pct ≥ 0.910) | 93 | 8 (8.6%) | 7 (7.5%) | **16.1%** | 0 |
| GPL6244 | top 50% (pct ≥ 0.724) | 232 | 13 (5.6%) | 12 (5.2%) | **10.8%** | 3 |
| GPL3290 | top 10% (pct ≥ 0.774) | 34 | 2 (5.9%) | 5 (14.7%) | **20.6%** | 4 |
| GPL3290 | top 20% (pct ≥ 0.708) | 67 | 6 (9.0%) | 6 (9.0%) | **17.9%** | 6 |
| GPL3290 | top 50% (pct ≥ 0.515) | 168 | 15 (8.9%) | 8 (4.8%) | **13.7%** | 6 |

Row class: **PREDICTION** (all rows). The canonical non-tumour genes in the GPL6244 top decile are `COL1A1`, `COL1A2`, `PDGFRA` — all three from the fibroblast/ECM set, none immune, none endothelial. On GPL3290 they are `PECAM1`, `PDGFRB`.

> **BOUND (composition route), the headline.** Of the retained panel genes carrying the strongest EMC bulk signal, an upper bound of **≈ 22%** is attributable, or plausibly attributable, to a non-tumour compartment — 21.7% on GPL6244 (top decile) and 20.6% on GPL3290 (top decile), falling to ~11–14% across the top half. **The bound is dominated by the fibroblast/ECM axis; the immune and endothelial contributions to the top signal are near zero.**
>
> **Assumptions that produce this number, all of which must hold:** (i) the curated 479-gene panel is representative of the transcriptome with respect to compartment composition — *this is the weakest assumption and is probably false in a specific direction, see Limitations*; (ii) a gene bearing a canonical stromal marker identity in EMC is stromal in origin, which no measurement in this repository establishes; (iii) the lexical regex over-calls rather than under-calls; (iv) `ACAN`/`COL2A1`/`SOX9` are excluded, so a chondroid-matrix contribution is **outside** the bound in either direction.

Sensitivity over marker sets: dropping the three flagged-ambiguous markers (`ACTA2`, `MCAM`, `FN1`) changes the variance-route statistic by ≤ 0.003 R² on both platforms (table R3, rows 2 and 7), and drops one gene from the GPL6244 top-decile canonical count. The single-compartment decompositions in R3 show the fibro/ECM set is the only one whose observed value exceeds its own null on either platform, and only on GPL3290 (0.1788 vs 0.1669, p = 0.396) — not significant, but sign-consistent with the composition route's finding that the ECM axis carries the risk.

### R5 — Falsification checks

**FC1 — permutation null (does the score beat an arbitrary gene set?).** Reported in R3. **The score does NOT beat a random size-matched gene set in any configuration.** This is the check firing, and I am reporting it as such rather than dropping the estimand.

**FC2 — positive control (does the fibro score rank a genuinely fibroblastic tumour highest?).** On GPL6244, **desmoid fibromatosis** — a bona fide fibroblastic/myofibroblastic proliferation with abundant collagen — has the **highest** fibro/ECM score of all four classes (0.990), with fibrosarcoma second (0.923). The score orders the classes the way tissue biology says it should. **PASS.** Conversely, the EMC tumour marker set ranks **EMC highest on both platforms** (0.606 on GPL6244; 0.841 on GPL3290) — an independent internal positive control.

**FC3 — cross-platform sign concordance (biology or platform?).** EMC-minus-comparator delta of mean marker percentile, computed **separately** on each platform, compared by **sign only, with no pooling**:

| Marker set | GPL6244 delta | GPL3290 delta | concordant |
|---|---|---|---|
| immune | **−0.1581** | **+0.0156** | **NO** |
| endothelium | −0.2528 | −0.0400 | yes |
| fibroblast/ECM | −0.0454 | −0.0893 | yes |
| EMC tumour set | +0.0644 | +0.2838 | yes |

Three of four concordant across a single-channel oligonucleotide array and a two-colour cDNA array with disjoint comparator arms. **The immune axis is NOT concordant** — and its GPL3290 delta (+0.016) is negligible against comparator arms of n = 3 and n = 3. So: any immune-direction claim about EMC from these cohorts is platform-dependent and should not be made. The fibro/ECM and endothelial directions survive the check.

**FC4 — technical confound (is the score tracking array brightness or data completeness?).** Correlation of the composite non-tumour score with the sample's panel-wide mean percentile: **r = −0.052 (GPL6244, n=6)** and **r = −0.084 (GPL3290, n=10)** — negligible, as expected since percentile is within-array normalised. But: correlation of the score with the **number of readable genes per sample** is **r = +0.541 on GPL3290** (undefined on GPL6244, where every sample has identical coverage). **This check partially fires.** On the two-colour platform the composite non-tumour score is moderately confounded with per-sample spot completeness, which is a technical property of that array. It is a further reason the GPL3290 arm is used here only for sign concordance and never as a level.

---

## Validation evidence

### RUN

| # | Command | Environment | Exit | Key output |
|---|---|---|---|---|
| 1 | `rg -n "GSE4303\|GSE28866\|GSE24369" research/modalities/ \| head -40` | repo @ `92abbcb` | 0 | code/JSON only; no matrix file |
| 2 | `find . -path ./.git -prune -o \( -iname "*series_matrix*" -o -iname "*.txt.gz" -o -iname "*.CEL*" \) -print` | repo | 0 | only `GSM281775-8.soft.txt.gz` |
| 3 | `zcat research/modalities/_s4_lane_inputs/GSM281775.soft.txt.gz \| head -60` | repo | 0 | `293-tet-On-NOR1 without doxycycline`, `GSE11185`, GPL570 |
| 4 | `python3 -c "import sys,numpy,scipy;..."` | `/tmp/claude-0/w02b` | 0 | `python 3.11.15`, `numpy 2.4.6`, `scipy 1.17.1` |
| 5 | `python3 extract.py` | same | 0 | `GSE24369 n_genes_readable=464 n_samples=35 {'desmoid_fibromatosis':6,'EMC':6,'LGFMS':17,'fibrosarcoma':6}`; `GSE4303-GPL3290 n_genes_readable=418 n_samples=16 {'DFSP':3,'GIST':3,'EMC':10}` |
| 6 | `timeout 600 python3 fast.py` | same | 0 | R3, FC2, FC3, FC4 tables above, verbatim; `wrote fast_results.json` |
| 7 | `timeout 120 python3 topsignal.py` | same | 0 | R4 table above, verbatim |
| 8 | `git status --porcelain \| head` | repo | 0 | single line `?? research/autonomy/opus-capacity-campaign-20260908/` — write isolation intact |

Note on run 6: an earlier non-vectorised version of the same analysis (`stromal_bound.py`) exceeded the 120 s foreground timeout and was moved to background as job `b5a5en6py`. It was **superseded, not used**; every number reported here comes from the vectorised `fast.py` (exit 0) and `topsignal.py` (exit 0). No result in this report depends on the background job.

### PROPOSED (NOT RUN)

- Transcriptome-wide repeat of estimand C on the full `GSE24369` series matrix. Not run: the matrix is not committed and fetching it requires egress.
- Any absolute deconvolution (NNLS/CIBERSORT/EPIC). Not run, and **not attempted** — W02 recorded the reference basis as behind the egress wall, and re-attempting a recorded-blocked route is prohibited.

### Code (returned inline; nothing written into the tree)

`extract.py`

```python
"""Extract the retained per-sample array-percentile matrix from the committed cache.
READ-ONLY on the repository; writes only under /tmp/claude-0/."""
import json, collections
SRC="/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
d=json.load(open(SRC)); gr=d["gene_reads"]; out={}
for plat in ["GSE24369_series_matrix.txt.gz","GSE4303-GPL3290_series_matrix.txt.gz"]:
    genes={}; classes={}
    for g,v in gr.items():
        pv=v.get(plat)
        if not pv or not pv.get("readable"): continue
        row={}
        for s in (pv.get("per_sample") or []):
            classes[s["gsm"]]=s["class"]
            if s.get("array_percentile") is not None: row[s["gsm"]]=s["array_percentile"]
        if row: genes[g]=row
    out[plat]={"genes":genes,"classes":classes,
               "value_kind":next((gr[g][plat].get("value_kind") for g in gr
                                  if gr[g].get(plat,{}).get("readable")),None)}
    print(plat,"n_genes_readable=",len(genes),"n_samples=",len(classes),
          dict(collections.Counter(classes.values())))
json.dump(out,open("panel_percentiles.json","w"))
```

`fast.py` — bound + FC1–FC4

```python
import json, itertools
import numpy as np
RNG=np.random.default_rng(20260908)
D=json.load(open("panel_percentiles.json"))
MARK={
 "immune":["PTPRC","CD2","CD3D","CD3E","CD8A","CD68","CD163","CSF1R","ITGAM","HLA-DRA","MS4A1","GZMB"],
 "endo":["PECAM1","VWF","CDH5","KDR","FLT1","MCAM"],
 "fibroECM":["COL1A1","COL1A2","COL3A1","COL5A1","DCN","LUM","FAP","THY1","POSTN","FN1",
             "PDGFRA","PDGFRB","ACTA2","COL11A1"],
 "tumour":["NR4A3","PPARG","RET","INSM1","SYP","CHGA","ENO2","KIT","CD24"]}
AMBIG={"ACTA2","MCAM","FN1"}; CHOND={"ACAN","COL2A1","SOX9"}
ALLM=set(itertools.chain(*MARK.values()))|CHOND
P1="GSE24369_series_matrix.txt.gz"; P2="GSE4303-GPL3290_series_matrix.txt.gz"

def block(plat,samples):
    g=D[plat]["genes"]; names=[x for x in g if all(s in g[x] for s in samples)]
    return names, np.array([[g[x][s] for s in samples] for x in names],float)
def zrows(M):
    sd=M.std(axis=1,ddof=0,keepdims=True); sd[sd==0]=np.inf
    return (M-M.mean(axis=1,keepdims=True))/sd
def emc_of(plat):
    c=D[plat]["classes"]; return sorted([s for s,v in c.items() if v=="EMC"])

def run(plat,sets,filt=lambda g:True,nperm=5000):
    S=emc_of(plat); names,M=block(plat,S); idx={n:i for i,n in enumerate(names)}
    Z=zrows(M); comps=[]; nmark=0
    for k in sets:
        rows=[idx[g] for g in MARK[k] if filt(g) and g in idx]; nmark+=len(rows)
        v=M[rows].mean(axis=0); comps.append((v-v.mean())/(v.std(ddof=0) or 1))
    s=np.mean(comps,axis=0); s=(s-s.mean())/s.std(ddof=0)
    keep=[i for i,n in enumerate(names) if n not in ALLM and M[i].std(ddof=0)>0]
    Zk=Z[keep]; n=len(S); obs=((Zk@s)/n)**2
    pool=np.array(keep); null=np.empty(nperm); k=len(sets)
    for t in range(nperm):
        pick=RNG.choice(pool,size=min(nmark,len(pool)),replace=False); cs=[]
        for ch in np.array_split(pick,k):
            v=M[ch].mean(axis=0); cs.append((v-v.mean())/(v.std(ddof=0) or 1))
        sp=np.mean(cs,axis=0); sp=(sp-sp.mean())/(sp.std(ddof=0) or 1)
        mask=~np.isin(pool,pick); null[t]=(((Zk[mask]@sp)/n)**2).mean()
    return dict(n_emc=n,n_marker_genes=nmark,n_genes_scored=len(keep),
        mean_R2=round(float(obs.mean()),4),median_R2=round(float(np.median(obs)),4),
        null_mean=round(float(null.mean()),4),null_p95=round(float(np.percentile(null,95)),4),
        null_p99=round(float(np.percentile(null,99)),4),
        p_perm=round(float((null>=obs.mean()).mean()),4))
```
(FC2/FC3/FC4 blocks and `topsignal.py` are as executed above; their full text is in `/tmp/claude-0/w02b/fast.py` and `/tmp/claude-0/w02b/topsignal.py`, and both are short, self-contained and reproduced in behaviour by the tables in R2–R5.)

---

## Limitations

1. **This is a PREDICTION about composition, never a measured cell fraction.** Nothing here counts a cell. No marker score, on any scale, is a cell proportion. Association only; no causal claim; no clinical claim of any kind. Nothing here bears on efficacy, safety, selectivity, therapeutic window, or clinical readiness for any agent or target.
2. **The panel is not the transcriptome, and its bias probably runs one way.** The 464/418 genes were curated for prior lanes (NR4A3 targets, surface antigens, hypoxia, PPARG, drug-screen targets), so they are enriched for **tumour-compartment** biology. A tumour-enriched panel will **understate** the true non-tumour share. The ≈22% top-decile figure is therefore an upper bound *within the panel* and plausibly a **lower** bound on the transcriptome-wide share. That asymmetry is the single largest reason not to quote 22% as "the" stromal fraction of EMC bulk data.
3. **The variance route is dead at these n.** R3 is a negative and must be reported as one. Nobody should redo it on these cohorts.
4. **GPL3290 is a two-colour log-ratio against a reference pool.** Its percentiles rank a contrast, not an abundance. All level readings on that arm are non-interpretable as abundance and are used only for sign concordance. FC4 additionally shows its score is confounded (r = +0.54) with per-sample spot completeness.
5. **Marker attribution is assumed, not measured.** That `COL1A1` signal in an EMC sample originates in a fibroblast rather than a tumour cell is precisely the thing bulk data cannot establish — the limitation this task set out to quantify is also a limitation of the quantification. Circularity is bounded, not eliminated. **A compartment-resolved measurement remains the only thing that settles it.**
6. **No cross-platform pooling was performed and none is licensed.** The two cohorts agree in sign on 3 of 4 axes; they do not agree on the immune axis.
7. **Comparator arms are other sarcomas**, several of them fibroblastic (desmoid, fibrosarcoma, LGFMS, DFSP). "Lower than comparator" therefore means "lower than other, mostly fibroblastic, sarcomas" — never "low", and never "normal".
8. **W02's negative stands unchanged.** No EMC single-cell, single-nucleus or spatial dataset was retrieved; T1–T4 are unmodified; the NNLS-against-Subramanian route stays blocked and was not attempted.
9. **No content-policy refusal occurred** in this task. No egress attempt was made, so no 403 or paywall was encountered.

---

## Stop condition

**Set:** an executed, bounded stromal-fraction estimate with sensitivity and a falsification check, **or** a precise statement that the committed data cannot support it and exactly what is missing.

**Met — in the mixed form the data actually permit, and both halves are reported:**

- **Delivered:** an executed bound. Of the retained panel's strongest EMC bulk signal, **≤ ~22%** is attributable or plausibly attributable to a non-tumour compartment (21.7% GPL6244 top decile, 20.6% GPL3290 top decile; 11–14% across the top half), dominated by the **fibroblast/ECM** axis, with immune and endothelial contributions near zero. Sensitivity over marker sets performed; four falsification checks performed, of which **FC2 passes, FC3 passes on 3 of 4 axes, FC1 fails, and FC4 partially fires on GPL3290** — all reported rather than dropped.
- **Also delivered, as a hard negative:** the across-sample **variance** route to a compositional fraction **cannot be made informative** on these cohorts. At n = 6 and n = 10 a random size-matched gene set already explains 29% and 17% of panel variance; the marker score does not beat it (p ≥ 0.396 everywhere).

**Exactly what is missing, stated precisely** — this is the actionable half:

1. **The expression matrices themselves.** Committing `GSE24369_series_matrix.txt.gz` (GPL6244) and `GSE4303-GPL3290_series_matrix.txt.gz` would lift estimand C from a 464-gene curated panel to the full ~33k-probe transcriptome and remove limitation 2, which is the dominant source of bias in the ≈22% figure. These are **public GEO files** currently fetched at CI time; no new permission is needed, only a decision to store them. **This is the single highest-value, lowest-cost fix.**
2. **A pure-compartment reference profile on a matched platform** — what would turn an ordinal bound into a cardinal cell fraction. Behind the same egress wall as the Subramanian basis; **do not attempt from this environment.**
3. **More EMC samples.** Nothing fixes estimand B short of roughly n ≥ 30 EMC on one platform, which does not exist anywhere for this disease.
4. **A compartment-resolved EMC measurement** (snRNA-seq or spatial). W02's finding: none exists. This remains the only thing that converts the ≈22% prediction into a measurement.

---

## Tool-call and wall-clock count actually used

- **Tool calls:** 14 (13 `Bash`, 1 background-spawn side effect of call 10). Target was ~40.
- **Wall clock:** `Tue Sep 8 02:02:22 UTC 2026` (first `date -u`, after 3 read-only orientation calls) to `Tue Sep 8 02:06:47 UTC 2026`; total elapsed from dispatch ≈ 12 minutes against a ~40-minute target.
- **Spend:** $0. No paid API, no GPU, no network egress.

---

## Next concrete action

**One specific successor for lane 2:** commit the two public GEO series matrices (`GSE24369_series_matrix.txt.gz`, `GSE4303-GPL3290_series_matrix.txt.gz`) as tracked inputs via the existing CI fetch path, then re-run **estimand C only** (`topsignal.py`, unchanged logic) transcriptome-wide on GPL6244. That single change removes the dominant bias identified in limitation 2 and converts "≈22% of a tumour-enriched panel" into a defensible transcriptome-wide upper share. Estimand B should **not** be re-run — R3 shows the n makes it unanswerable, and re-running it would be replaying a recorded negative.

result: Per-gene EMC expression IS committed (as a 479-gene panel cache, not matrices) — a reference-free rank-based analysis bounds the non-tumour share of the strongest EMC bulk signal at ≈22% (21.7% GPL6244, 20.6% GPL3290 top decile), dominated by fibroblast/ECM with near-zero immune contribution, while the across-sample variance route is shown to be unanswerable at n=6/10 (marker score does not beat a random gene set, p≥0.396).
