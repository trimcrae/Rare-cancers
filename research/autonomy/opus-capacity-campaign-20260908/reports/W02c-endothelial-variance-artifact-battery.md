> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: re-ran the reproduction against W02b's published table (exact match to 3 dp on all four arms), confirmed `git status --porcelain` shows only the coordinator's own untracked report files (I wrote nothing under the repo), all execution under `/tmp/claude-0/w02c/`, both scripts exit 0.

---

# W02c — Is the elevated between-specimen variance of the EMC endothelial score real, or an artifact?

## Worker

- **Worker ID:** W02c (refill for lane 2), OPUS-CAPACITY-CAMPAIGN-20260908
- **Lane:** Lane 2 — EMC microenvironment. Successor question surfaced by W02b's replication addendum.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I self-report as Claude Opus 5 (`claude-opus-5`), running as Claude Code in the Anthropic Cloud remote environment. **This is a self-report and must not be treated as observed fact.** Confirming W02b and W02: `env | grep -c '^ANTHROPIC_MODEL='` returns `0` — **no `ANTHROPIC_MODEL` variable exists**, so the served model is not confirmable from inside the session. The coordinator must extract the runtime model from the transcript.
- **Write isolation:** READ-ONLY on the Git tree, honoured. All execution in `/tmp/claude-0/w02c/`. **No file written, moved or deleted anywhere under `/home/user/Rare-cancers`. No git operation of any kind.** `git status --porcelain` at end shows two untracked files, both the coordinator's own collected reports (`W01c-…md`, `W13b-…md`), neither mine. Tree HEAD read at `b9a0257e6acff53ad22535cf2adf261313e0b250` (the campaign brief names the frozen read commit `92abbcb…`; HEAD has advanced because the coordinator has been committing collected reports — the input file `research/modalities/emc-expression-panels.json` is unchanged in content, `generated_utc 2026-08-29T12:51:32+00:00`).
- **No network used.** W02b established the archives are blanket-denied; I did not re-probe.

`date -u` — **honest note: I did not capture a `date -u` at the literal first tool call**, so I report only what I actually ran: `Tue Sep  8 02:16:57 UTC 2026` (end of supplementary run) and `Tue Sep  8 02:17:12 UTC 2026` (final environment capture). Session start was approximately 02:08 UTC by tool-call ordering; that is an estimate, not a recorded measurement.

Literal output of the required env command (proxy/`no_proxy` lines filtered out as declared noise; secrets redacted by the prescribed `sed`):

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

---

## Question

**Is the elevated between-specimen variance of the EMC endothelial marker score (SD 0.200 across six tumours, four times any comparator arm's within-class spread) a real heterogeneity signal, or an artifact of n, of marker composition, or of a single outlier specimen?**

Open because W02b's replication addendum surfaced the number, explicitly labelled it a PREDICTION, and went no further — it had spent its budget on the ≈22% bound and the estimand-B negative. It matters because EMC is a myxoid, relatively hypovascular tumour and several repository lanes reason about vascular/hypoxia biology; a genuinely heterogeneous vascular compartment is a checkable feature, while an outlier-driven SD is a trap that would propagate into those lanes as a false premise.

---

## Prior-work check

Commands run (from `/home/user/Rare-cancers`):

```
rg -n -i "endothel" --glob '!.git' -l | head -20
rg -n -i "bimodal|heterogene" --glob '!.git' -l | head -20
rg -n "GSM6009(34|3[5-9]|4[0-9])" --glob '!.git' -l | head
```

What they showed: 20+ files mention endothelium, but every hit is either a therapeutic-target discussion (`emc-surface-target-landscape-si.md`, `cd248_precedent.py`, ATU027 delivery evidence) or a literature note — **none computes an endothelial score per EMC specimen or asks about its variance.** The `bimodal|heterogene` hits are all `systems/views/` clinical-register views (RT lanes, competing mortality) plus a scratchpad blind-spot audit; **none concerns array-level compartment variance.** The per-GSM hits (`emc-atr-vulnerability-inputs.json`, `emc-cohort-search.json`, `nr4a3-fusion-targets.json`) carry per-sample values for other questions, not compartment scores.

Two adjacent files I read rather than assumed:
- `research/modalities/emc-hypoxia-confounds.json` — asks whether the EMC **class-mean** hypoxia contrast is a comparator-composition artifact. It works on class contrasts, has no per-GSM records at all, and never touches between-specimen variance. Not a replay.
- `research/modalities/emc-expression-panels.json` `platforms[…].sample_annotations_verbatim` — I checked these for any per-specimen covariate. They carry **only diagnosis, "soft tissue", "tumor biopsy"** for all 42 samples. No grade, site, size, treatment, batch or scan date is recorded. This bounds what step 3 can align against (see Result R6).

Closed items I confirm I am not replaying: I did **not** re-run estimand B (the across-sample variance route to a stromal fraction — closed as a hard negative), did **not** attempt any egress (GEO/archives blanket-denied per W02b), did **not** attempt deconvolution against an external reference basis (recorded blocked), did **not** pool across platforms, and did **not** re-derive or alter the ≈22% bound.

---

## Method / inputs

- **Input file (the only data source):** `/home/user/Rare-cancers/research/modalities/emc-expression-panels.json`, `generated_utc 2026-08-29T12:51:32+00:00`. Field used: `gene_reads[<symbol>][<platform>].per_sample[].array_percentile`, with `gsm` and `class`.
- **Series/platforms:** `GSE24369_series_matrix.txt.gz` (GPL6244, Affymetrix Gene ST, single-channel) and `GSE4303-GPL3290_series_matrix.txt.gz` (two-colour cDNA, log-ratio vs a reference pool). **No cross-platform pooling anywhere.** GPL3290 is used only as a same-question cross-check on a contrast scale and never as an abundance level.
- **Extraction:** I re-derived the matrix myself from the source JSON rather than reusing W02b's `panel_percentiles.json`, so step 1 is an independent reproduction. Complete-case: **464 genes × 35 samples (GPL6244)**; **301 genes × 16 samples (GPL3290)**. (W02b reported 418 readable genes on GPL3290; my 301 is the *complete-case* subset after requiring a value in all 16 samples — the same reduction W02b's `block()` applies inside its analysis. Not a discrepancy, a different reporting point; see Result R1.)
- **Endothelial marker set (unchanged from W02b, so the reproduction is like-for-like):** `PECAM1`, `VWF`, `CDH5`, `KDR`, `FLT1`, `MCAM` — all 6 readable and complete-case on both platforms. `MCAM` carries W02b's ambiguity flag (also pericyte/perivascular).
- **Score definition:** per specimen, the unweighted mean of the marker genes' `array_percentile`. Class SD is the sample SD, `ddof=1`.
- **Tools:** Python 3.11.15, numpy 2.4.6, scipy 1.17.1, Linux 6.18.44-fc-v24 x86_64. Scripts `/tmp/claude-0/w02c/w02c.py` and `/tmp/claude-0/w02c/supp.py`, both reproduced inline below.
- **All four criteria were written into the script before it was run**, and the script prints each criterion above its own result.

---

## Result

### R1 — Reproduction of W02b's per-class endothelial statistics (independent re-derivation)

| Arm (GPL6244) | mean | SD | n | W02b's published value | agree? | class |
|---|---|---|---|---|---|---|
| EMC | 0.469 | **0.2001** | 6 | 0.469 (0.200, 6) | **exact to 3 dp** | PREDICTION |
| LGFMS | 0.690 | 0.0949 | 17 | 0.690 (0.095, 17) | **exact to 3 dp** | PREDICTION |
| desmoid fibromatosis | 0.756 | 0.0558 | 6 | 0.756 (0.056, 6) | **exact to 3 dp** | PREDICTION |
| fibrosarcoma | 0.775 | 0.0532 | 6 | 0.775 (0.053, 6) | **exact to 3 dp** | PREDICTION |

**No discrepancy.** Complete-case gene counts also reproduce W02b exactly on GPL6244 (464 genes × 35 samples, class counts `{desmoid 6, EMC 6, LGFMS 17, fibrosarcoma 6}`). The only reporting difference is GPL3290, where I quote the complete-case count (301) and W02b quoted the readable count (418) — both are correct statements about different sets.

The six EMC specimen scores (PREDICTION, `array_percentile` units, GPL6244):

| GSM | endothelial score |
|---|---|
| GSM600934 | 0.5186 |
| GSM600935 | 0.2990 |
| GSM600936 | **0.7806** |
| GSM600937 | 0.3089 |
| GSM600938 | 0.3012 |
| GSM600939 | 0.6032 |

### R2 — Test (a): is one specimen driving it?

> **Criterion, declared before running:** if the *minimum* leave-one-out SD falls to ≤ 0.095 (the largest comparator-arm SD on this platform, LGFMS at n=17), the SD is outlier-driven.

| specimen dropped | resulting SD |
|---|---|
| GSM600934 | 0.2221 |
| GSM600935 | 0.2036 |
| GSM600936 | **0.1444** (the minimum) |
| GSM600937 | 0.2059 |
| GSM600938 | 0.2041 |
| GSM600939 | 0.2112 |

LOO SD range **[0.1444, 0.2221]**. The minimum, 0.1444, is **1.52× the largest comparator SD** and does not approach the criterion. Outlier-insensitive spreads tell the same story (PREDICTION, all rows):

| arm | MAD | IQR | range |
|---|---|---|---|
| **EMC** | **0.1136** | **0.2789** | **0.4816** |
| LGFMS (n=17) | 0.0713 | 0.1149 | 0.3578 |
| desmoid | 0.0310 | 0.0477 | 0.1604 |
| fibrosarcoma | 0.0303 | 0.0626 | 0.1380 |

The EMC MAD — which by construction cannot be moved by one extreme point — is 1.6× LGFMS and 3.7× the two n=6 arms. A further check: the ratio min-LOO-SD / SD is **0.722** in EMC, against a median of **0.727** in 5,000 six-specimen subsamples of the homogeneous LGFMS arm. That is the *expected* leave-one-out sensitivity of a homogeneous n=6 sample; EMC shows **no outlier signature at all**.

**VERDICT (a): survives. Not driven by one specimen.**

### R3 — Test (b): is it a small-n sampling artifact?

> **Criterion, declared before running:** if P(sample SD at n=6 ≥ 0.2001 | σ = the best-powered comparator arm, LGFMS n=17) > 0.05, small-n alone explains it.

| reference σ | route | P(SD₆ ≥ 0.2001) | class |
|---|---|---|---|
| LGFMS σ = 0.0949 (n=17, the only well-powered arm) | χ²₅ tail | **0.00047** | PREDICTION |
| desmoid σ = 0.0558 (n=6) | χ²₅ tail | < 1e-5 | PREDICTION |
| fibrosarcoma σ = 0.0532 (n=6) | χ²₅ tail | < 1e-5 | PREDICTION |
| LGFMS empirical, 20,000 draws of 6 from the 17 real specimens | non-parametric | **0.00000** (max SD observed in 20,000 draws = 0.1511, p99 = 0.1402) | PREDICTION |

Formal variance tests (PREDICTION): Levene/Brown-Forsythe, EMC vs pooled comparators, **W = 10.84, p = 0.0024**; Bartlett across four classes **T = 11.88, p = 0.0078**; F-test EMC vs LGFMS **F = 4.45 (df 5,16), p = 0.0198**.

The non-parametric route is the decisive one: resampling six specimens from the seventeen real LGFMS tumours **never once in 20,000 draws** reached 0.200. n=6 is a weak sample size, but it is not weak enough to manufacture this SD from comparator-like spread.

**VERDICT (b): survives. Not a small-n artifact.**

### R4 — Test (c): is it marker composition?

> **Criterion, declared before running:** if the elevated SD depends on any one marker — i.e. some leave-one-marker-out SD falls to ≤ 0.095 — it is composition-driven.

Per-marker EMC SD (PREDICTION): `PECAM1` 0.207, `VWF` 0.229, `CDH5` 0.139, `KDR` 0.303, `FLT1` 0.302, `MCAM` 0.093. **Five of six single markers individually exceed the whole comparator range**; only the flagged-ambiguous `MCAM` sits inside it.

| marker dropped | 5-marker EMC SD |
|---|---|
| PECAM1 | 0.2029 |
| VWF | 0.1950 |
| CDH5 | 0.2128 |
| KDR | 0.1841 |
| FLT1 | 0.1801 |
| **MCAM** (ambiguous) | **0.2284 — SD *increases*** |

Every leave-one-marker-out SD is ≥ 0.180. **W02b's flagged ambiguity runs the wrong way for the artifact hypothesis:** `MCAM` is the *least* variable member and is *diluting* the signal; removing it strengthens the effect (0.200 → 0.228). A conservative core-3 endothelial-junction set (`PECAM1`, `VWF`, `CDH5` — no receptor tyrosine kinases, no pericyte-ambiguous marker) still gives SD **0.1857**.

Coherence check — within-EMC Pearson correlation among the six markers (n=6):

|  | PECAM1 | VWF | CDH5 | KDR | FLT1 | MCAM |
|---|---|---|---|---|---|---|
| PECAM1 | 1.000 | 0.874 | 0.893 | 0.751 | 0.916 | 0.686 |
| VWF | 0.874 | 1.000 | 0.957 | 0.943 | 0.993 | 0.619 |
| CDH5 | 0.893 | 0.957 | 1.000 | 0.958 | 0.971 | 0.607 |
| KDR | 0.751 | 0.943 | 0.958 | 1.000 | 0.931 | 0.468 |
| FLT1 | 0.916 | 0.993 | 0.971 | 0.931 | 1.000 | 0.617 |
| MCAM | 0.686 | 0.619 | 0.607 | 0.468 | 0.617 | 1.000 |

Mean off-diagonal r **within EMC = 0.812**, against **0.546 (LGFMS)**, **0.387 (desmoid)**, **0.438 (fibrosarcoma)**. The six markers move together across the EMC specimens far more tightly than they do within any comparator arm — which is the signature of one coherent underlying axis, not of one rogue probe.

Size-matched null: 5,000 random 6-gene panels drawn from the 423 non-marker complete-case panel genes give EMC SD mean 0.0357, p95 0.0717, and **P(random 6-gene SD ≥ 0.2001) = 0.0000**. The endothelial score's spread is **2.8× the 95th percentile** of what an arbitrary 6-gene panel produces on the same six specimens.

**VERDICT (c): survives. Not marker composition; the ambiguous marker works against the effect.**

### R5 — Test (d): is it a per-specimen technical effect?

> **Criterion, declared before running:** if |r| ≥ 0.8 between the EMC endothelial score and a per-specimen technical covariate (panel-wide mean percentile; readable-gene count), the spread is technical.

| covariate | statistic | class |
|---|---|---|
| panel-wide mean percentile, EMC n=6 | Pearson **r = −0.388, p = 0.447**; Spearman ρ = −0.257, p = 0.623 | PREDICTION |
| readable-gene count, EMC n=6 | **UNDEFINED** — coverage is identical (464 genes) in *every one* of the 35 GPL6244 samples | PRIMARY (structural fact of the file) |
| panel-wide mean percentile, all 35 samples | r = +0.427, p = 0.0105 | PREDICTION |

Neither criterion fires. The EMC specimens' panel-wide mean percentiles span only 0.646–0.694 (SD 0.017) — an order of magnitude less spread than the endothelial score — so there is no per-specimen brightness axis of sufficient size to produce it, as expected since `array_percentile` is within-array normalised by construction. The weak positive association across all 35 samples (r = +0.427) points the **opposite** way from the within-EMC association (r = −0.388) and therefore cannot generate it.

**Reported rather than dropped:** W02b's GPL3290 spot-completeness confound (r = +0.541) has no GPL6244 analogue at all, because GPL6244 coverage is uniform. Separately, my falsification battery found `fibrosarcoma`'s endothelial score is itself strongly correlated with panel-wide mean percentile (**r = +0.845**, n=6) — a caution about that comparator arm, not about EMC.

**VERDICT (d): survives. Not a per-specimen technical effect.**

### R6 — Step 3: shape of the spread, and what it aligns with

Sorted EMC endothelial scores: **0.2990, 0.3012, 0.3089 | 0.5186, 0.6032, 0.7806**. There is a visually striking 0.210 gap between the third and fourth specimen — 43.5% of the total range — suggesting a 3-vs-3 split into a "low-vascular" cluster (GSM600935, 600937, 600938) and a "higher-vascular" cluster (GSM600934, 600939, 600936).

**I tested that impression and it does not hold up.** Under a single normal at n=6, the max-gap/range statistic reaches 0.435 or more **47.4%** of the time (20,000 simulations). The comparator arms produce the same appearance without any bimodality claim: desmoid 0.476, fibrosarcoma 0.435, LGFMS 0.218.

> **Bimodal vs continuous is UNDECIDABLE at n=6.** The data show a large, real spread; they do not show its shape. Nothing here supports describing EMC's vascular compartment as bimodal or as having two subtypes.

Alignment scan against everything else recorded per specimen in the committed data (GPL6244 EMC, n=6):

| endothelial score vs | Pearson r | raw p | Bonferroni ×6 | class |
|---|---|---|---|---|
| `NR4A3` percentile | +0.859 | 0.028 | 0.168 — **does not survive** | PREDICTION |
| immune marker score | +0.749 | 0.087 | 0.522 — does not survive | PREDICTION |
| fibro/ECM marker score | −0.719 | 0.107 | 0.642 — does not survive | PREDICTION |
| EMC tumour marker score | +0.404 | 0.427 | 1.000 | PREDICTION |
| panel-wide mean percentile | −0.388 | 0.447 | 1.000 | PREDICTION |
| GSM order (batch proxy) | −0.011 | 0.983 | 1.000 | PREDICTION |
| composite hypoxia/VEGF-axis score (9 genes) | −0.007 | 0.989 | 1.000 | PREDICTION |

**Nothing recorded in the committed data explains the split.** The `NR4A3` association is the only one below 0.05 raw and it does not survive correcting for the six tests I ran; at n=6 it rests on very few points and I decline to call it a finding. What the pattern is *not*: it is not tumour purity (endothelial and tumour-marker scores move **together**, not oppositely), it is not batch (GSM order r = −0.011), and it is not brightness.

`sample_annotations_verbatim` records only diagnosis and "soft tissue / tumor biopsy" for every specimen — **no grade, site, size, treatment, batch or scan date is committed**, so patient-level or specimen-level alignment is **UNKNOWN, not absent**.

Hypoxia link (directly relevant to the lanes that motivated this task): nine hypoxia/VEGF-axis genes are complete-case in the panel. All sit at very high EMC percentiles with tiny between-specimen spread — `LDHA` 0.994 (SD 0.006), `PGK1` 0.988 (SD 0.010), `HIF1A` 0.982 (SD 0.012), `EPAS1` 0.958 (SD 0.020), `VEGFA` 0.926 (SD 0.056), `SLC2A1` 0.898 (SD 0.070), `ADM` 0.911 (SD 0.100), `CA9` 0.732 (SD 0.103). The composite correlates with the endothelial score at **r = −0.007, p = 0.989**. **So: the hypoxia axis is uniformly high and uniformly flat across all six EMC specimens while the endothelial axis varies four-fold more than any comparator. The variable vascular reading and the invariant hypoxia reading are decoupled in these data.** A lane that assumes low vessel markers track high hypoxia markers per specimen should not assume that here.

### R7 — Specificity, honestly bounded

| marker set | EMC SD | LGFMS SD | EMC/LGFMS | F-test p (df 5,16) | markers |
|---|---|---|---|---|---|
| endothelium | **0.2001** | 0.0949 | 2.11× | 0.0198 | 6/6 |
| EMC tumour | 0.0532 | 0.0239 | 2.23× | 0.0124 | 9/9 |
| fibro/ECM | 0.0798 | 0.0442 | 1.81× | 0.0638 | 14/14 |
| immune | 0.0638 | 0.0640 | 1.00× | 0.9076 | 12/12 |

All rows PREDICTION. **This is a real qualification and I am not burying it:** EMC shows elevated between-specimen variance relative to LGFMS on the tumour and fibro/ECM axes too, at a similar *ratio*. The endothelial score is not uniquely elevated as a ratio. What it is, decisively, is the largest in **absolute** magnitude — 2.5× the next-largest arm-level SD, and 2.8× the p95 of a size-matched random 6-gene panel on the same specimens. The immune axis, notably, shows **no** excess variance at all (1.00×), which is consistent with W02b's finding that the immune compartment contributes near-nothing to the EMC bulk signal.

Absolute SDs are not comparable *across* marker sets of different sizes (averaging 14 genes damps variance more than averaging 6), so the within-set EMC/LGFMS ratio is the fair comparison and the size-matched random-panel null is the fair absolute reference. Both are reported.

### R8 — Falsification check (executed, not proposed)

The identical four-part battery applied to each comparator arm, which should *not* show the effect:

| arm | n | SD | LOO range | leave-1-marker range | max-gap/range | r vs panel-mean | P(SD ≥ 0.2001 given this arm's σ, n=6) |
|---|---|---|---|---|---|---|---|
| LGFMS | 17 | 0.0949 | [0.0794, 0.0980] | [0.0835, 0.1129] | 0.218 | +0.401 | 0.00047 |
| desmoid | 6 | 0.0558 | [0.0339, 0.0624] | [0.0470, 0.0671] | 0.476 | +0.191 | < 1e-5 |
| fibrosarcoma | 6 | 0.0532 | [0.0347, 0.0592] | [0.0470, 0.0604] | 0.435 | +0.845 | < 1e-5 |

**The falsification check passes.** No comparator arm approaches the EMC spread on any of the four routes, including the two arms at the *same* n=6. The battery is not a machine that returns "heterogeneous" for any small arm you feed it.

### R9 — GPL3290 cross-check (contrast scale only; no pooling, no abundance reading)

EMC n=10: mean 0.676, SD 0.086; DFSP n=3 SD 0.027; GIST n=3 SD 0.116. EMC LOO SD range [0.0671, 0.0915], max-gap/range 0.357. **This arm neither confirms nor refutes the GPL6244 finding, and I do not claim it does.** Its comparator arms are n=3 (too small to estimate a reference σ), its values are percentiles of a **log-ratio against a reference pool** rather than abundances, and W02b's spot-completeness confound (r = +0.54) applies to it. It is reported for completeness, not as evidence.

---

## Verdict

> **The elevated between-specimen variance of the EMC endothelial score on GPL6244 is NOT explained by any of the four artifact routes tested.** It is not driven by one specimen (min leave-one-out SD 0.144, still 1.5× the largest comparator SD; leave-one-out sensitivity exactly matches a homogeneous n=6 sample). It is not a small-n artifact (never reached in 20,000 six-specimen resamples of the real LGFMS arm; Levene p = 0.0024). It is not marker composition (every leave-one-marker-out SD ≥ 0.180; the flagged-ambiguous `MCAM` *dilutes* rather than drives it; the six markers co-vary within EMC at mean r = 0.812, more tightly than in any comparator arm; P < 0.0002 against size-matched random 6-gene panels). It is not a per-specimen technical effect (coverage identical in all 35 samples; |r| = 0.39 against panel brightness, far below the 0.80 criterion).
>
> **Therefore, as a PREDICTION about compartment composition and never as a measured vessel density: the endothelial marker signal genuinely varies more between individual EMC tumours than between individual tumours of any comparator class on this array — roughly four-fold more than the tightest comparator arms and twice the best-powered one. W02b's caution stands and is now supported: a single-specimen EMC vascular reading must not be generalised.**
>
> **Two limits on that verdict, stated as firmly as the verdict itself.** First, **the shape of the spread is UNDECIDABLE at n = 6** — the apparent 3-vs-3 split is not distinguishable from a single continuous distribution (p = 0.474), and EMC must not be described as having two vascular subtypes. Second, **the excess variance is not unique to the endothelial axis as a ratio** — the tumour-marker and fibro/ECM axes show comparable EMC/LGFMS variance ratios; endothelium is distinguished by being much the largest in absolute magnitude, while the immune axis shows no excess at all.

---

## Validation evidence

**RUN.** Environment for both: Linux 6.18.44-fc-v24 x86_64, Python 3.11.15, numpy 2.4.6, scipy 1.17.1, cwd `/tmp/claude-0/w02c`, no network.

| # | command | exit code | key verbatim output |
|---|---|---|---|
| 1 | `python3 -c "import numpy,scipy,sys;print(...)"` | 0 | `numpy 2.4.6 scipy 1.17.1 python 3.11.15` |
| 2 | `cd /tmp/claude-0/w02c && python3 w02c.py 2>&1 \| tee out.txt` | **0** | see below |
| 3 | `cd /tmp/claude-0/w02c && python3 supp.py 2>&1 \| tee supp.txt` | **0** | see below |
| 4 | `env \| grep -c '^ANTHROPIC_MODEL='` | 1 (grep no-match) | `0` |
| 5 | `git status --porcelain` | 0 | two `??` lines, both coordinator report files; **no line references any path I touched** |
| 6 | `git rev-parse HEAD` | 0 | `b9a0257e6acff53ad22535cf2adf261313e0b250` |

Verbatim key output of run 2 (`out.txt`, abridged to the load-bearing lines; the full file is at `/tmp/claude-0/w02c/out.txt`):

```
GPL6244 genes_readable=464 samples=35 {'desmoid_fibromatosis': 6, 'EMC': 6, 'LGFMS': 17, 'fibrosarcoma': 6}
complete-case GPL6244: 464 genes x 35 samples ; GPL3290: 301 x 16
 GPL6244 endothelium (markers used: PECAM1,VWF,CDH5,KDR,FLT1,MCAM)
   EMC                    mean=0.469 sd=0.200 n=6
   LGFMS                  mean=0.690 sd=0.095 n=17
   desmoid_fibromatosis   mean=0.756 sd=0.056 n=6
   fibrosarcoma           mean=0.775 sd=0.053 n=6
 EMC SD (ddof=1) = 0.2001 ; ddof=0 = 0.1827
 LOO SD range = [0.1444, 0.2221]
 VERDICT(a): survives - no single specimen explains it
   chi2 tail vs sigma=LGFMS (0.0949, n=17): P(SD_6>=0.2001)=0.00047
   LGFMS subsample-of-6 SD: mean=0.0915 p95=0.1307 p99=0.1402 max=0.1511 ; P(>=obs)=0.00000
   Levene (Brown-Forsythe, median) EMC vs pooled comparators: W=10.841 p=0.00237
   F-test EMC vs LGFMS: F=4.449 p=0.019777
   drop MCAM    SD=0.2284 mean=0.4395
 core-3 (PECAM1,VWF,CDH5) EMC SD=0.1857 mean=0.4357
 mean off-diagonal within-EMC r = 0.812
   P(random 6-gene SD_EMC >= observed endothelial SD) = 0.0000
   readable-gene count per sample, EMC: [464,464,464,464,464,464] (distinct=1 across all 35: [464])
   EMC endo vs panel-wide mean percentile: pearson r=-0.388 p=0.447
   P(max-gap/range >= observed | 6 draws from a single normal) = 0.4736
  LGFMS n=6 subsamples: median min-LOO-SD / SD = 0.727 (EMC value = 0.722)
```

Verbatim key output of run 3 (`supp.txt`):

```
   endo         0.2001   0.0949   0.0558   0.0532      2.11x  p=0.0198  (6/6 markers)
   tumour       0.0532   0.0239   0.0176   0.0328      2.23x  p=0.0124  (9/9 markers)
   immune       0.0638   0.0640   0.0319   0.0922      1.00x  p=0.9076  (12/12 markers)
   composite hypoxia/VEGF-axis score: EMC mean=0.874 sd=0.034 ; r(endo, hypoxia | EMC)=-0.007 p=0.989
   NR4A3       raw p=0.028  Bonferroni x6 = 0.168  does NOT survive
```

**PROPOSED (NOT RUN)** — declared, not claimed:
- Repeating this battery on the full `GSE24369` series matrix rather than the 464-gene panel cache. Not run: the matrix is not committed and fetching it requires egress, which is blanket-denied.
- Any independent EMC cohort. Not run and not available; **arrays or specimens do not imply new patients**.
- A dip test (Hartigan) on the six EMC values. Not run because `scipy` carries no implementation and n=6 is below any dip test's usable range; the max-gap permutation above is the honest substitute and it returns "undecidable".

### Code (returned inline; nothing written into the tree)

`/tmp/claude-0/w02c/w02c.py`

```python
"""W02c - is the elevated between-specimen SD of the EMC endothelial score real?
READ-ONLY on the repository. Executes only under /tmp/claude-0/w02c/."""
import json, itertools, collections
import numpy as np
from scipy import stats

SRC="/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
P1="GSE24369_series_matrix.txt.gz"; P2="GSE4303-GPL3290_series_matrix.txt.gz"
ENDO=["PECAM1","VWF","CDH5","KDR","FLT1","MCAM"]
IMM=["PTPRC","CD2","CD3D","CD3E","CD8A","CD68","CD163","CSF1R","ITGAM","HLA-DRA","MS4A1","GZMB"]
FIB=["COL1A1","COL1A2","COL3A1","COL5A1","DCN","LUM","FAP","THY1","POSTN","FN1",
     "PDGFRA","PDGFRB","ACTA2","COL11A1"]
TUM=["NR4A3","PPARG","RET","INSM1","SYP","CHGA","ENO2","KIT","CD24"]
RNG=np.random.default_rng(20260908)

d=json.load(open(SRC)); gr=d["gene_reads"]
def load(plat):
    genes={}; classes={}
    for g,v in gr.items():
        pv=v.get(plat)
        if not pv or not pv.get("readable"): continue
        row={}
        for s in (pv.get("per_sample") or []):
            classes[s["gsm"]]=s["class"]
            if s.get("array_percentile") is not None: row[s["gsm"]]=s["array_percentile"]
        if row: genes[g]=row
    return genes,classes
G1,C1=load(P1); G2,C2=load(P2)
print("GPL6244 genes_readable=%d samples=%d %s"%(len(G1),len(C1),dict(collections.Counter(C1.values()))))
print("GPL3290 genes_readable=%d samples=%d %s"%(len(G2),len(C2),dict(collections.Counter(C2.values()))))

def complete(G,C):
    S=sorted(C); names=[g for g in G if all(s in G[g] for s in S)]
    return S,names,{g:np.array([G[g][s] for s in S]) for g in names}
S1,N1,M1=complete(G1,C1); S2,N2,M2=complete(G2,C2)
print("complete-case GPL6244: %d genes x %d samples ; GPL3290: %d x %d"%(len(N1),len(S1),len(N2),len(S2)))
print("endo markers complete-case GPL6244:",[g for g in ENDO if g in M1],"GPL3290:",[g for g in ENDO if g in M2])

def score(M,markers,S):
    ok=[g for g in markers if g in M]
    return np.mean([M[g] for g in ok],axis=0), ok
def byclass(M,C,S,markers):
    v,ok=score(M,markers,S); out={}
    for cl in sorted(set(C.values())):
        idx=[i for i,s in enumerate(S) if C[s]==cl]
        out[cl]=(v[idx].mean(), v[idx].std(ddof=1), len(idx), v[idx])
    return out,v,ok

print("\n=== STEP 1: reproduce per-class endothelial statistics ===")
for lbl,M,C,S in [("GPL6244",M1,C1,S1),("GPL3290",M2,C2,S2)]:
    bc,v,ok=byclass(M,C,S,ENDO)
    print(" %s endothelium (markers used: %s)"%(lbl,",".join(ok)))
    for cl,(m,sd,n,_) in bc.items():
        print("   %-22s mean=%.3f sd=%.3f n=%d"%(cl,m,sd,n))
E_bc,E_v,_=byclass(M1,C1,S1,ENDO)
emc_idx=[i for i,s in enumerate(S1) if C1[s]=="EMC"]
emc_gsm=[S1[i] for i in emc_idx]; emc_endo=E_v[emc_idx]
print("\n EMC per-specimen endothelial score (GPL6244):")
for s,x in zip(emc_gsm,emc_endo): print("   %s %.4f"%(s,x))
SD_OBS=emc_endo.std(ddof=1); print(" EMC SD (ddof=1) = %.4f ; ddof=0 = %.4f"%(SD_OBS,emc_endo.std(ddof=0)))

print("\n=== TEST (a): outlier / leave-one-out ===")
print(" criterion declared BEFORE running: if the minimum leave-one-out SD falls to <=0.095")
print(" (the largest comparator-arm SD on this platform, LGFMS n=17), the SD is outlier-driven.")
loo=[]
for i in range(len(emc_endo)):
    r=np.delete(emc_endo,i); loo.append((emc_gsm[i],r.std(ddof=1)))
for g,s in loo: print("   drop %s -> SD=%.4f"%(g,s))
lo=min(s for _,s in loo); hi=max(s for _,s in loo)
print(" LOO SD range = [%.4f, %.4f]"%(lo,hi))
print(" robust spread: MAD=%.4f IQR=%.4f range=%.4f"%(
    stats.median_abs_deviation(emc_endo), np.subtract(*np.percentile(emc_endo,[75,25])),
    emc_endo.max()-emc_endo.min()))
for cl,(m,sd,n,vals) in E_bc.items():
    print("   %-22s MAD=%.4f IQR=%.4f range=%.4f"%(cl,stats.median_abs_deviation(vals),
          np.subtract(*np.percentile(vals,[75,25])), vals.max()-vals.min()))
print(" VERDICT(a): %s"%("OUTLIER-DRIVEN (min LOO SD <= 0.095)" if lo<=0.095 else "survives - no single specimen explains it"))

print("\n=== TEST (b): small-n sampling artifact ===")
print(" criterion declared BEFORE running: if P(sample SD at n=6 >= observed | sigma = the")
print(" best-powered comparator arm, LGFMS n=17) > 0.05, small-n alone explains it.")
lg=E_bc["LGFMS"][3]; sig_lg=lg.std(ddof=1)
for cl,(m,sd,n,vals) in E_bc.items():
    if cl=="EMC": continue
    p=stats.chi2.sf(5*(SD_OBS/sd)**2,5)
    print("   chi2 tail vs sigma=%s (%.4f, n=%d): P(SD_6>=%.4f)=%.5f"%(cl,sd,n,SD_OBS,p))
draws=np.array([np.random.default_rng(1000+t).choice(lg,6,replace=False).std(ddof=1) for t in range(20000)])
print("   LGFMS subsample-of-6 SD: mean=%.4f p95=%.4f p99=%.4f max=%.4f ; P(>=obs)=%.5f"%(
    draws.mean(),np.percentile(draws,95),np.percentile(draws,99),draws.max(),(draws>=SD_OBS).mean()))
allcmp=np.concatenate([E_bc[c][3] for c in E_bc if c!="EMC"])
print("   Levene (Brown-Forsythe, median) EMC vs pooled comparators: W=%.3f p=%.5f"%
      stats.levene(emc_endo,allcmp,center='median'))
print("   Bartlett across 4 classes: T=%.3f p=%.6f"%stats.bartlett(*[E_bc[c][3] for c in E_bc]))
print("   F-test EMC vs LGFMS: F=%.3f p=%.6f"%((SD_OBS**2/sig_lg**2),
      2*min(stats.f.sf(SD_OBS**2/sig_lg**2,5,16),stats.f.cdf(SD_OBS**2/sig_lg**2,5,16))))

print("\n=== TEST (c): marker composition ===")
print(" criterion declared BEFORE running: if the elevated SD depends on any one marker -")
print(" i.e. some leave-one-marker-out SD falls to <=0.095 - it is composition-driven.")
print(" per-marker EMC SD and class means:")
for g in ENDO:
    if g not in M1: print("   %s absent"%g); continue
    vals=M1[g]
    row=" ".join("%s=%.3f(sd %.3f)"%(cl,vals[[i for i,s in enumerate(S1) if C1[s]==cl]].mean(),
                 vals[[i for i,s in enumerate(S1) if C1[s]==cl]].std(ddof=1)) for cl in sorted(set(C1.values())))
    print("   %-7s %s"%(g,row))
print(" leave-one-marker-out EMC endothelial SD:")
for g in ENDO:
    sub=[x for x in ENDO if x!=g]
    v,_=score(M1,sub,S1); print("   drop %-7s SD=%.4f mean=%.4f"%(g,v[emc_idx].std(ddof=1),v[emc_idx].mean()))
v,_=score(M1,[x for x in ENDO if x!="MCAM"],S1)
print(" 5-marker (MCAM dropped) EMC SD=%.4f ; comparator SDs: %s"%(v[emc_idx].std(ddof=1),
   {cl:round(v[[i for i,s in enumerate(S1) if C1[s]==cl]].std(ddof=1),4) for cl in sorted(set(C1.values()))}))
sub3=["PECAM1","VWF","CDH5"]
v3,_=score(M1,sub3,S1); print(" core-3 (PECAM1,VWF,CDH5) EMC SD=%.4f mean=%.4f"%(v3[emc_idx].std(ddof=1),v3[emc_idx].mean()))
print(" within-EMC correlation among endothelial markers (n=6, Pearson):")
present=[g for g in ENDO if g in M1]
Mx=np.array([M1[g][emc_idx] for g in present])
Cm=np.corrcoef(Mx)
print("    "+" ".join("%7s"%g for g in present))
for i,g in enumerate(present): print("   %-7s "%g+" ".join("%7.3f"%x for x in Cm[i]))
print(" mean off-diagonal within-EMC r = %.3f"%(Cm[np.triu_indices(len(present),1)].mean()))
for cl in sorted(set(C1.values())):
    if cl=="EMC": continue
    ix=[i for i,s in enumerate(S1) if C1[s]==cl]
    Cc=np.corrcoef(np.array([M1[g][ix] for g in present]))
    print("   mean off-diagonal r in %-22s = %.3f (n=%d)"%(cl,Cc[np.triu_indices(len(present),1)].mean(),len(ix)))
pool=[g for g in N1 if g not in set(ENDO+IMM+FIB+TUM)]
def rnd_sd(idx,nrep=5000,k=6):
    out=np.empty(nrep)
    for t in range(nrep):
        pick=RNG.choice(len(pool),k,replace=False)
        v=np.mean([M1[pool[i]] for i in pick],axis=0); out[t]=v[idx].std(ddof=1)
    return out
r_emc=rnd_sd(emc_idx); lgidx=[i for i,s in enumerate(S1) if C1[s]=="LGFMS"]
r_lg=rnd_sd(lgidx)
print(" random 6-gene panels (n=%d genes eligible): SD in EMC mean=%.4f p95=%.4f ; in LGFMS mean=%.4f p95=%.4f"%(
   len(pool),r_emc.mean(),np.percentile(r_emc,95),r_lg.mean(),np.percentile(r_lg,95)))
print("   P(random 6-gene SD_EMC >= observed endothelial SD) = %.4f"%((r_emc>=SD_OBS).mean()))

print("\n=== TEST (d): per-specimen technical effect ===")
print(" criterion declared BEFORE running: if |r| >= 0.8 between the EMC endothelial score and")
print(" a per-specimen technical covariate (panel-wide mean percentile; readable-gene count),")
print(" the spread is technical.")
panelmean=np.array([np.mean([M1[g][i] for g in N1]) for i in range(len(S1))])
readable=np.array([sum(1 for g in G1 if S1[i] in G1[g]) for i in range(len(S1))])
print("   readable-gene count per sample, EMC: %s (distinct=%d across all 35: %s)"%(
   readable[emc_idx].tolist(),len(set(readable.tolist())),sorted(set(readable.tolist()))))
r1=stats.pearsonr(emc_endo,panelmean[emc_idx]); r2=stats.spearmanr(emc_endo,panelmean[emc_idx])
print("   EMC endo vs panel-wide mean percentile: pearson r=%.3f p=%.3f ; spearman rho=%.3f p=%.3f"%(r1[0],r1[1],r2[0],r2[1]))
print("   EMC panel-wide mean percentile values: %s (sd=%.4f)"%(np.round(panelmean[emc_idx],4).tolist(),panelmean[emc_idx].std(ddof=1)))
if len(set(readable[emc_idx].tolist()))>1:
    r3=stats.pearsonr(emc_endo,readable[emc_idx].astype(float)); print("   EMC endo vs readable-gene count: r=%.3f p=%.3f"%r3)
else:
    print("   EMC endo vs readable-gene count: UNDEFINED - coverage identical in every EMC sample")
ra=stats.pearsonr(E_v,panelmean); print("   all 35 samples: endo vs panel-wide mean percentile r=%.3f p=%.4f"%ra)

print("\n=== STEP 3: shape of the EMC spread and what it aligns with ===")
srt=np.sort(emc_endo); gaps=np.diff(srt)
print("   sorted EMC endo: %s"%np.round(srt,4).tolist())
print("   gaps: %s ; largest gap=%.4f at position %d ; gap/range=%.3f"%(np.round(gaps,4).tolist(),
      gaps.max(),int(gaps.argmax())+1,gaps.max()/(srt[-1]-srt[0])))
def maxgap(x):
    s=np.sort(x); g=np.diff(s); return g.max()/(s[-1]-s[0])
sim=np.array([maxgap(np.random.default_rng(5000+t).normal(size=6)) for t in range(20000)])
print("   P(max-gap/range >= observed | 6 draws from a single normal) = %.4f"%((sim>=maxgap(emc_endo)).mean()))
oth={}
for nm,mk in [("immune",IMM),("fibroECM",FIB),("tumour",TUM)]:
    v,_=score(M1,mk,S1); oth[nm]=v[emc_idx]
oth["panel_mean"]=panelmean[emc_idx]
oth["NR4A3"]=M1["NR4A3"][emc_idx] if "NR4A3" in M1 else None
oth["gsm_order"]=np.arange(6,dtype=float)
print("   per-specimen table (GPL6244 EMC):")
hdr=["gsm","endo"]+[k for k in oth if oth[k] is not None]
print("   "+" ".join("%12s"%h for h in hdr))
for i in range(6):
    print("   "+" ".join(["%12s"%emc_gsm[i],"%12.4f"%emc_endo[i]]+
          ["%12.4f"%oth[k][i] for k in oth if oth[k] is not None]))
for k in oth:
    if oth[k] is None: continue
    rr=stats.pearsonr(emc_endo,oth[k]); ss=stats.spearmanr(emc_endo,oth[k])
    print("   endo vs %-12s pearson r=%+.3f p=%.3f  spearman rho=%+.3f p=%.3f"%(k,rr[0],rr[1],ss[0],ss[1]))

print("\n=== FALSIFICATION: same battery on comparator arms ===")
for cl in ["LGFMS","desmoid_fibromatosis","fibrosarcoma"]:
    ix=[i for i,s in enumerate(S1) if C1[s]==cl]; vals=E_v[ix]; sd=vals.std(ddof=1)
    l=[np.delete(vals,i).std(ddof=1) for i in range(len(vals))]
    lom=[]
    for g in ENDO:
        vv,_=score(M1,[x for x in ENDO if x!=g],S1); lom.append(vv[ix].std(ddof=1))
    print("  %-22s n=%2d SD=%.4f LOO[%.4f,%.4f] leave-1-marker[%.4f,%.4f] maxgap/range=%.3f r_vs_panelmean=%+.3f"%(
       cl,len(ix),sd,min(l),max(l),min(lom),max(lom),maxgap(vals),stats.pearsonr(vals,panelmean[ix])[0]))
    print("      P(SD>=EMC's %.4f | this arm's sigma, n=6, chi2) = %.5f"%(SD_OBS,stats.chi2.sf(5*(SD_OBS/sd)**2,5)))
frac=[]
for t in range(5000):
    v=np.random.default_rng(9000+t).choice(lg,6,replace=False)
    frac.append(min(np.delete(v,i).std(ddof=1) for i in range(6))/v.std(ddof=1))
print("  LGFMS n=6 subsamples: median min-LOO-SD / SD = %.3f (EMC value = %.3f)"%(np.median(frac),lo/SD_OBS))

print("\n=== GPL3290 cross-check (contrast scale, NOT abundance; no pooling) ===")
bc2,v2,ok2=byclass(M2,C2,S2,ENDO)
for cl,(m,sd,n,vals) in bc2.items(): print("   %-8s mean=%.3f sd=%.3f n=%d"%(cl,m,sd,n))
e2=bc2["EMC"][3]; print("   EMC(n=10) sorted: %s"%np.round(np.sort(e2),4).tolist())
print("   EMC LOO SD range=[%.4f,%.4f] maxgap/range=%.3f"%(
   min(np.delete(e2,i).std(ddof=1) for i in range(len(e2))),
   max(np.delete(e2,i).std(ddof=1) for i in range(len(e2))), maxgap(e2)))
```

`/tmp/claude-0/w02c/supp.py`

```python
import json,collections
import numpy as np
from scipy import stats
SRC="/home/user/Rare-cancers/research/modalities/emc-expression-panels.json"
P1="GSE24369_series_matrix.txt.gz"
d=json.load(open(SRC)); gr=d["gene_reads"]
genes={};classes={}
for g,v in gr.items():
    pv=v.get(P1)
    if not pv or not pv.get("readable"): continue
    row={}
    for s in (pv.get("per_sample") or []):
        classes[s["gsm"]]=s["class"]
        if s.get("array_percentile") is not None: row[s["gsm"]]=s["array_percentile"]
    if row: genes[g]=row
S=sorted(classes); names=[g for g in genes if all(x in genes[g] for x in S)]
M={g:np.array([genes[g][s] for s in S]) for g in names}
idx={cl:[i for i,s in enumerate(S) if classes[s]==cl] for cl in sorted(set(classes.values()))}
SETS={"immune":["PTPRC","CD2","CD3D","CD3E","CD8A","CD68","CD163","CSF1R","ITGAM","HLA-DRA","MS4A1","GZMB"],
 "endo":["PECAM1","VWF","CDH5","KDR","FLT1","MCAM"],
 "fibroECM":["COL1A1","COL1A2","COL3A1","COL5A1","DCN","LUM","FAP","THY1","POSTN","FN1","PDGFRA","PDGFRB","ACTA2","COL11A1"],
 "tumour":["NR4A3","PPARG","RET","INSM1","SYP","CHGA","ENO2","KIT","CD24"]}
print("A) is the excess between-specimen SD specific to endothelium? (GPL6244, SD across specimens)")
print("   %-10s %8s %8s %8s %8s  EMC/LGFMS  F-test p (EMC n=6 vs LGFMS n=17)"%("set","EMC","LGFMS","desmoid","fibrosar"))
for nm,mk in SETS.items():
    ok=[g for g in mk if g in M]; v=np.mean([M[g] for g in ok],axis=0)
    sds={cl:v[idx[cl]].std(ddof=1) for cl in idx}
    F=sds["EMC"]**2/sds["LGFMS"]**2
    p=2*min(stats.f.sf(F,5,16),stats.f.cdf(F,5,16))
    print("   %-10s %8.4f %8.4f %8.4f %8.4f  %8.2fx  p=%.4f  (%d/%d markers)"%(
      nm,sds["EMC"],sds["LGFMS"],sds["desmoid_fibromatosis"],sds["fibrosarcoma"],
      sds["EMC"]/sds["LGFMS"],p,len(ok),len(mk)))
print("\nB) hypoxia / VEGF-axis markers present in the committed panel, per EMC specimen")
HYP=["VEGFA","VEGFB","VEGFC","CA9","SLC2A1","HIF1A","EPAS1","LDHA","PGK1","ADM","ANGPT1","ANGPT2","TEK","NOS3","ESM1","HEY1","DLL4","NRP1","PDGFB","FLT4"]
have=[g for g in HYP if g in M]; print("   present:",have,"| absent from complete-case panel:",[g for g in HYP if g not in M])
endo=np.mean([M[g] for g in SETS["endo"]],axis=0)
e=idx["EMC"]
for g in have:
    r=stats.pearsonr(endo[e],M[g][e]); print("   %-7s EMC mean=%.3f sd=%.3f ; r(endo,gene | EMC n=6)=%+.3f p=%.3f"%(g,M[g][e].mean(),M[g][e].std(ddof=1),r[0],r[1]))
if have:
    hv=np.mean([M[g] for g in have],axis=0); r=stats.pearsonr(endo[e],hv[e])
    print("   composite hypoxia/VEGF-axis score: EMC mean=%.3f sd=%.3f ; r(endo, hypoxia | EMC)=%+.3f p=%.3f"%(hv[e].mean(),hv[e].std(ddof=1),r[0],r[1]))
print("\nC) multiplicity on the step-3 alignment scan (6 correlations tested)")
for nm,p in [("immune",0.087),("fibroECM",0.107),("tumour",0.427),("panel_mean",0.447),("NR4A3",0.028),("gsm_order",0.983)]:
    print("   %-11s raw p=%.3f  Bonferroni x6 = %.3f  %s"%(nm,p,min(1,p*6),"survives" if p*6<0.05 else "does NOT survive"))
```

---

## Limitations

1. **This is a PREDICTION about composition. It is not a vessel count and never becomes one.** Nothing here measures microvessel density, vessel calibre, perfusion or any vascular parameter. A transcript-level marker score in bulk archival tissue is a hypothesis about what cells are present, and CD31/VWF/CDH5 signal can arise from causes other than more vessels. **A compartment-resolved or histological measurement remains the only thing that would settle it.**
2. **No clinical claim of any kind.** Nothing here bears on efficacy, safety, selectivity, therapeutic window, prognosis, patient selection, or clinical readiness for any agent or target. Six archival tumours on one array do not support an anti-angiogenic or any other treatment inference.
3. **n = 6.** Every EMC statement rests on six specimens on one platform. The variance excess is robust; the *shape* of the distribution is not resolvable, and I say so explicitly rather than reading the visible gap as bimodality.
4. **No cross-platform pooling.** GPL3290 percentiles rank a log-ratio against a reference pool, not an abundance; that arm's comparators are n=3. It is reported as neither confirming nor refuting.
5. **Marker attribution is assumed, not measured** — W02b's limitation carries over unchanged. That a `PECAM1` reading in an EMC sample originates in endothelium rather than in tumour cells is precisely what bulk data cannot establish.
6. **The panel is 464 genes, not a transcriptome.** Every statement is about a curated panel's marker sets. The random-6-gene null draws from the same 423-gene panel pool and inherits its selection.
7. **Specimen covariates are UNKNOWN, not absent.** The committed annotations carry only diagnosis and "tumor biopsy". Grade, site, size, prior treatment, fusion partner, batch and scan date are not committed, so the alignment scan in R6 cannot rule out that the split tracks an uncommitted clinical or technical variable. I did not fetch them (egress denied) and I did not guess.
8. **Multiplicity.** The R6 alignment scan tested six correlations at n=6; **none survives Bonferroni**, including the `NR4A3` association. I report it because concealing a scan is worse than reporting a corrected null, not because it is a finding.
9. **The variance excess is not endothelium-specific as a ratio** (R7). Reported prominently, not in a footnote.
10. **W02's transfer limits, W02b's ≈22% non-tumour bound, and W02b's estimand-B negative are preserved intact and unmodified.** Nothing in this report revises, weakens or extends any of them. In particular, this result is fully consistent with the estimand-B negative: that negative concerns whether a marker score beats a *random gene set* at explaining panel-wide across-sample variance (it does not, p ≥ 0.396), which is a different question from whether the endothelial score's own between-specimen SD exceeds what comparator arms and size-matched random panels produce (it does, p < 0.001).

---

## Stop condition

**Set:** an executed four-part artifact battery with pre-declared criteria and a verdict on whether the EMC vascular heterogeneity is real, outlier-driven, or undecidable at n=6.

**MET.** All four tests were executed with criteria written into the script before it ran; a falsification battery was executed on all three comparator arms and passed; the verdict is delivered in two parts — the **variance excess is real and survives all four artifact explanations**, while the **shape of that variance (bimodal vs continuous) is undecidable at n = 6**.

---

## Tool-call and wall-clock count actually used

**11 tool calls** (target ~40). **Wall clock approximately 10 minutes** by tool-call ordering, ending `Tue Sep  8 02:17:12 UTC 2026` (target ~40 minutes). No network calls; no repository writes; no git operations.

---

## Next concrete action

**One successor for this lane:** re-run this exact four-part battery on the **full `GSE24369` series matrix** rather than the 464-gene panel cache, using a broader published endothelial marker set, to test whether the variance excess survives outside the curated panel. That is the single check that would most strengthen or break the finding, and it is **not a worker task** — it needs the series matrix committed (a write) plus a CI fetch, i.e. the same named successor W02b already identified. Until then this finding is bounded to the committed panel.

A second, honestly weaker option **inside** worker scope: apply the same battery to the other compartment scores on GPL6244, since R7 shows the tumour and fibro/ECM axes also carry elevated EMC variance and neither has been checked for outlier or composition artifacts. That is a real question but a smaller one, and it would need its own pre-declared criteria.

result: The EMC endothelial-score variance excess (SD 0.200 across six tumours vs 0.053–0.095 in comparator arms, GPL6244) is REAL — it survives all four pre-declared artifact tests (leave-one-out min SD 0.144, still 1.5x the largest comparator SD; never reached in 20,000 six-specimen resamples of the real LGFMS arm, Levene p=0.0024; every leave-one-marker-out SD >=0.180 with the ambiguous MCAM *diluting* not driving it, P<0.0002 vs size-matched random panels; no technical covariate, |r|=0.39 vs the 0.80 criterion) and a falsification battery on all three comparator arms shows the effect in none of them — but its SHAPE is undecidable at n=6 (apparent 3-vs-3 split, max-gap p=0.474), nothing committed per specimen explains the split after multiplicity correction, and the hypoxia axis is uniformly high and flat (r=-0.007 with the endothelial score), so W02b's caution stands: a single-specimen EMC vascular reading must not be generalised.
