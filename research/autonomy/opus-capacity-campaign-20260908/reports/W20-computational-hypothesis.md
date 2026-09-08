> Collected by the campaign coordinator from this worker's in-response draft.
> Workers are read-only on the Git working tree; the coordinator is the sole collector.
> Per-child runtime model evidence, from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check passed: my independent parse of the SRA XML recovered exactly 8 `EWSR1+` / 4 `EWSR1-`, matching the count recorded in the repository's own cohort memo — so the label join is correct. Both scripts exited 0, and the decision rule was fixed in the script docstring before execution. Report follows.

---

## Worker

**Worker ID:** W20 · **Lane 20** — distinct computational EMC hypothesis with public data and a decisive test / stop condition.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). This is a self-report from my own system context, not an observed fact; no environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` at start (abridged here only by removing the long duplicated `no_proxy`/`JAVA_TOOL_OPTIONS` lines, which contain no model information; everything model-relevant is retained verbatim):

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

`date -u` at start: `Tue Sep  8 01:56:52 UTC 2026`
`date -u` at end: `Tue Sep  8 02:01:11 UTC 2026` (final `date -u` at report composition; the last executed command block printed this)

Repository HEAD read: `92abbcb905cacf07f14b238db50d1b98f6590374` (matches the frozen campaign commit). **No file under `/home/user/Rare-cancers` was created or modified; no git write of any kind was performed.** All execution was under `/tmp/claude-0/w20/`.

---

## Question

**Does EWSR1 break-apart FISH status stratify the transcriptome *within* a single EMC cohort in the way the fusion-partner model predicts — specifically, is the 5′ partner gene *TAF15* elevated in EWSR1-FISH-negative EMC?**

Why it is open, and why it matters. The repository's own manuscript `nr4a3-fusion-transcriptional-output.md` states its binding limitation explicitly in the abstract: *"Until a fusion cistrome in EMC chromatin exists, 'elevated in EMC' and 'driven by the fusion' are inseparable."* Every EMC expression contrast retained here is **EMC versus a comparator arm** (GSE4303 10-vs-6, GSE28866 tumour-vs-normal), and in that shape disease identity and fusion status are perfectly collinear — nothing in such a design can attribute anything to the fusion rather than to the disease.

A **within-EMC, fusion-status-stratified** contrast breaks that collinearity for the first time, because both arms are EMC. The repository has been explicitly waiting for exactly this: `method-watch-triggers.json` `TRG-EMC-EXPRESSION-DATASET` `_still_watching_for` clause (a) asks for *"an EMC dataset with per-sample FUSION CONFIRMATION"*, and the cohort memo records that **"Clause (a) is now satisfiable"** — but no expression value has ever been read against those labels. The cohort memo is scoped *"Archive metadata only. NO expression value is read, measured or implied anywhere in this document"*, and the quantification module `emc-fourth-cohort-quant.json` deliberately emitted **no** differential-expression result at all.

The specific, falsifiable form I tested: in a gene fusion, the 5′ partner is transcribed from the rearranged allele under **its own** promoter, so a probe lying 5′ of the breakpoint reports endogenous transcript **plus** fusion transcript. EWSR1-break-apart-negative EMC is enriched for the commonest non-EWSR1 variant, `TAF15::NR4A3`. Therefore *TAF15* should read **higher** in EWSR1-FISH-negative EMC than in EWSR1-FISH-positive EMC.

---

## Prior-work check

Commands actually run and what they showed.

```
rg -n -i "hypothes|NR4A3|fusion|target gene|signature|transcription|chondro|myxoid" \
   research/hypotheses/ research/manuscripts/ --glob '!.git' -l | head -60
rg -n -i "hypothes|NR4A3|fusion" research/hypotheses/ research/manuscripts/ --glob '!.git' | wc -l
   -> 13745 matching lines across ~60 files
git ls-files | rg -i "gse|sra|counts|tpm|matrix|\.tsv|\.csv" | head -60
rg -n -l "emc-fourth-cohort-gene-counts|fourth-cohort-gene-counts" --glob '!.git'
   -> research/autonomy/research-ledger.json
      research/modalities/expression-validation-readiness.json
      research/modalities/emc-fourth-cohort-quant.json
      research/modalities/emc_fourth_cohort_quant.py
      research/modalities/emc_fourth_cohort_route_readout.py
rg -n -i "break-apart|breakapart|FISH" \
   research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md
```

`research/hypotheses/` is small (292K, 12 files) and I read `METHODOLOGY.md` and `txgnn-emc-findings.md` in full.

**Hypotheses already tested in this repository, with outcomes:**

| Prior hypothesis | Outcome | Where |
|---|---|---|
| TxGNN graph-foundation-model ranking corroborates EMC mechanism leads | **REFUTED / non-corroboratory** — pazopanib 19.3 pct, sunitinib 19.8, imatinib 25.2 of 7,957 | `txgnn-emc-findings.md` |
| EMC's PrimeKG **sparsity** explains that divergence | **REFUTED by pre-specified stress test** — chondrosarcoma 17.7, STS 17.4 median pct, same implausible top hits | `txgnn-relatives-comparison.json` |
| A pooled NR4A3 direct-target set is elevated in EMC | **DOES NOT CLEAR** its size-matched null (39% and 88% of threshold) | `nr4a3-fusion-transcriptional-output.md` |
| *SEMA3C* is a fusion-driven EMC target | survives nothing; **reverses sign** with comparator | ibid. |
| *PPARG* strongest reading | **circular** (scored on the cohort that first published it) | ibid. |
| *ENO3* | survives all robustness, but was the **pre-designated positive control**, not independent | ibid. |
| Wild-type NOR1 and EWS/NOR1 drive the same program | **partial non-reproduction** — Spearman 0.2322, overlap 8%/13% of each set | `gse11185-wt-vs-fusion.md` |
| A class-A gene carries unusual occupancy in NR4A peak catalogues | **negative** — none does, across 110 peak sets | `nr4a3-fusion-transcriptional-output.md` |
| A fourth EMC cohort exists | **found** (PRJNA1357027), but **no expression value ever read** | `emc-fourth-cohort-sra-2026-08-08.md` |

**Closed items I confirmed I am not replaying** (`CLOSED-WORK.md`, checked line by line):

- **Paired Davis validation (negative)** — that is drug–kinase affinity profiling. My test contains no drug, no kinase, and no affinity quantity.
- **Promoter transfer (failed)** — I transfer nothing between promoters, species or platforms. Both arms of my contrast are the same 12 specimens on one platform in one batch.
- **Inverse bounds (2/36 failed)** — I compute no bound; I compute one difference in means with an exact permutation distribution.
- **Methylation (deprioritized)** — no methylation datum is used.
- **Hofvander (one TAF15 case, EGA controlled-access)** — I use **no** Hofvander material and made **no** EGA request. The word "TAF15" is common to both, and I want to be precise about the difference: Hofvander is a **single case with controlled-access raw data**; my *TAF15* reading is a **transcript count in an unrelated, fully public, already-retained 12-tumour deposit**. No inference passes between them, and I make no claim about Hofvander's case.
- **Brenca (case identities unresolved)** — not used.
- **"Do not invent independent cohorts"** — I invented nothing. PRJNA1357027 / SRP640302 is a public deposit already discovered, characterised, quantified and committed to this repository by prior work. I added **zero** specimens and **zero** patients, and I treat the 12 runs as BioSamples, not as patients-by-chart.
- **GSE4303 / GSE28866 "rediscovery is not new data"** — I used **neither**. This is a different deposit entirely.
- **Registry ICD-O paper; clinical conditional-recurrence / RT-IPD / trial-discoverability checkpoints** — no clinical question is asked here.
- **The restricted NR4A Perspective refusal** — not touched, not recreated, not relabelled. I hit **no** content-policy refusal in this run.

**What is structurally different about this evidence route.** Every closed route above either (i) moved a quantity across a boundary it could not cross (promoter transfer, inverse bounds, cross-platform target transfer), (ii) depended on a source behind access control (Hofvander/EGA, the 403 publishers), or (iii) compared **EMC against something that is not EMC**, which cannot separate disease from fusion. This route does none of those. It is a **within-cohort, within-platform, within-batch contrast between two groups of EMC tumours split by a per-specimen molecular label that was deposited with the specimens** — the one design shape the repository's own watch-trigger has been waiting for, and the first time any expression value in that deposit has been read against any label.

---

## Method / inputs

**Data (all already committed to the repository at the frozen commit; nothing was downloaded):**

| Input | Path / accession | Content used |
|---|---|---|
| Count matrix | `research/modalities/emc-fourth-cohort-gene-counts.tsv` | 862 genes × 12 runs, **raw reads per gene** (not normalised, not length-corrected) |
| Per-sample labels | `research/modalities/emc-sra-study-inputs.json` | raw SRA `efetch` XML; `<TAG>FISH_1</TAG>` per `EXPERIMENT_PACKAGE`, joined on `RUN accession` |
| Provenance | `research/modalities/emc-fourth-cohort-quant.json` | units statement, probe-map state, `why_no_differential_expression` |
| Cohort characterisation | `research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md` | FISH_1 = `EWSR1+` 8 · `EWSR1-` 4 (used as an independent check on my parse) |

Deposit: **BioProject `PRJNA1357027` / SRA study `SRP640302`** — n = 12 FFPE EMC tumours, Siriraj Hospital (Thailand), collection years 1997–2020, **Targeted RNA-seq (TempO-Seq panel)**, Illumina HiSeq 2500, single-end, 5.4–8.7 M reads/run.

**Tools:** Python 3.11.15, standard library only (`json`, `re`, `itertools`, `math`, `statistics`). No third-party package, no network, no GPU, no paid API. `df -h /` before starting: **28 GiB available** (budget ≥10 GiB satisfied); **nothing was downloaded**, so no disk was consumed beyond two small scripts.

**Analysis, fully pre-specified in the script docstring before execution:**

1. Join FISH_1 to count columns on SRR accession.
2. CPM-normalise each column by its panel library size; take log2(CPM + 1).
3. Per-gene statistic δ = mean(log2CPM, EWSR1-negative) − mean(log2CPM, EWSR1-positive).
4. **Exact permutation inference**: complete enumeration of all C(12,4) = **495** label assignments. No asymptotic approximation, no Monte-Carlo resampling error, no seed dependence.
5. **Calibration**: percentile rank of *TAF15*'s δ among all 862 panel genes — the repository's own empirical-null instrument applied within-panel.
6. **Negative control**: *FUS* (FET-family paralog of EWSR1/TAF15, essentially never the EMC 5′ partner) — expected null.

**Decision rule, fixed before the run and applied verbatim afterwards:**

- **SUPPORTED** if δ(TAF15) > 0 **and** one-sided exact p ≤ 0.05 **and** *TAF15* in the top 5% of panel genes.
- **REFUTED** if δ(TAF15) ≤ 0, **or** one-sided exact p > 0.05.
- **UNDECIDED** if *TAF15* median raw count < 10 across the 12 runs, or the label mapping fails.

Note the rule is falsifiable in both directions and was not adjustable after seeing output — the verdict string is printed by the script itself.

---

## Result

**The hypothesis is REFUTED.** *TAF15* is not elevated in EWSR1-FISH-negative EMC; it is **lower**.

| Gene | Row type | median raw reads (n=12) | δ = neg − pos, log2CPM | exact p (1-sided, δ>0) | exact p (2-sided) | panel percentile (of 862) |
|---|---|---|---|---|---|---|
| **TAF15** (primary endpoint) | **PRIMARY** | 1041.5 | **−0.8347** | **0.9899** | 0.0182 | 9.05 |
| *FUS* (pre-specified negative control) | **PRIMARY** | 1023.0 | +0.0789 | 0.4808 | 0.9131 | 62.06 |
| *VCAN* | SECONDARY (descriptive) | 3223.0 | −1.0618 | 0.9778 | 0.0303 | 4.52 |
| *FN1* | SECONDARY (descriptive) | 1707.5 | −1.1137 | 0.7879 | 0.4283 | 3.94 |

Units: δ is a difference of arm means in log2(counts-per-million + 1), i.e. an approximate log2 fold change. n = 4 EWSR1-negative vs 8 EWSR1-positive. **Uncertainty is defined as the exact permutation distribution over all 495 possible 4/8 label assignments of these same 12 specimens** — not a parametric interval, and it does not extend beyond this deposit.

Group assignment recovered by my parse: `EWSR1-` = SRR35940648, SRR35940654, SRR35940656, SRR35940657; the remaining eight `EWSR1+`. **This 8/4 split independently reproduces the FISH_1 counts recorded in the repository's cohort memo**, which is a genuine check that the label join is correct rather than an assumption.

Per-specimen *TAF15* values (**PRIMARY**), log2CPM — EWSR1-negative: 10.68, 9.46, 10.91, 10.45; EWSR1-positive: 11.76, 11.58, 11.37, 11.25, 10.71, 10.51, 11.39, 11.12. The groups overlap; the separation is a shift, not a clean split.

**Robustness / global-shift control (RUN, `robust.py`).** A CPM-normalised panel of 862 genes can carry a global arm shift, which would manufacture a spurious per-gene difference. Measured: panel-wide δ mean **−0.0971**, median **−0.0835**, SD **0.5781**, with **490/862 genes negative**. So there *is* a mild global negative shift in the EWSR1-negative arm, and *TAF15* sits at **z = −1.276** against the panel — i.e. moderately, not dramatically, more negative than the typical gene. This is why I report the panel percentile (9.05) alongside the p-value: the raw two-sided p overstates how exceptional *TAF15* is relative to its own platform.

**On the opposite-direction signal, stated carefully.** *TAF15*'s two-sided exact p = 0.0182 on a **single pre-specified gene** is a legitimate test, and it points the *opposite* way to the hypothesis. I am **not** converting that into a new claim. It is one gene, n = 4 vs 8, in FFPE material spanning 23 collection years, with a mild global arm shift already documented above and no way to separate specimen degradation from biology in this metadata. Classify it as **ASSOCIATION, hypothesis-generating, not validated** — the correct status of a post-hoc direction reversal, and precisely the kind of reading the parent quantification module declined to make for this cohort.

**PREDICTION rows: none.** This report contains no prediction, no model output, and no extrapolation.

**Two things this result does establish, independent of the refutation:**

1. **PRIMARY.** The first expression reading of PRJNA1357027 against its per-sample FISH labels — the design shape `TRG-EMC-EXPRESSION-DATASET` clause (a) has been waiting for — is now performed, and it is negative for the partner-allele-readthrough prediction.
2. **PRIMARY.** *FUS*, the pre-specified negative control, behaved as a control should (δ = +0.079, two-sided p = 0.913, 62nd percentile). The instrument is not manufacturing differences everywhere, which is what makes the *TAF15* null interpretable rather than merely uninformative.

---

## Validation evidence

**RUN — command 1** (feasibility/budget gate, before any analysis):
```
df -h /
```
→ `/dev/vda  252G  9.3G used  28G avail  25%` — exit 0. ≥10 GiB budget satisfied; no download was performed at any point.

**RUN — command 2** (egress probe, 8 hosts):
```
for u in https://ftp.ncbi.nlm.nih.gov/ https://www.ebi.ac.uk/gxa/ https://ftp.ebi.ac.uk/pub/databases/ \
         https://depmap.org/ https://cbioportal.org/ https://api.gdc.cancer.gov/status \
         https://www.proteinatlas.org/ https://rest.uniprot.org/ ; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 -L "$u"); echo "$code  $u"; done
```
→ `000` for all eight. Confirmed at the proxy:
```
curl -sS --max-time 25 "$HTTPS_PROXY/__agentproxy/status"
```
→ `"recentRelayFailures": [{"kind":"connect_rejected","detail":"gateway answered 403 to CONNECT (policy denial or upstream failure)","host":"rest.ensembl.org:443"}, ...]`

**This is an organization egress-policy denial. Per `/root/.ccr/README.md` I did not retry it, did not route around it, and did not weaken TLS.** It is recorded here as an honest access boundary, and it is the reason the test had to run on retained data.

**RUN — command 3** (the decisive test): `/tmp/claude-0/w20/taf15_test.py`
```
cd /tmp/claude-0/w20 && python3 --version && python3 taf15_test.py; echo "EXIT=$?"
```
Environment: `Python 3.11.15`, stdlib only. Verbatim key output:
```
label mapping: n = 12
EWSR1- idx [2, 8, 10, 11]  EWSR1+ idx [0, 1, 3, 4, 5, 6, 7, 9]
library sizes (panel reads): [375572, 1174158, 907268, 588992, 1066043, 164967,
                              140423, 292897, 994241, 1356848, 406135, 307583]
exact permutations enumerated: 495

gene        medRaw    delta    p1sided    p2sided  panelPct
TAF15       1041.5  -0.8347     0.9899     0.0182      9.05
FUS         1023.0   0.0789     0.4808     0.9131     62.06
VCAN        3223.0  -1.0618     0.9778     0.0303      4.52
FN1         1707.5  -1.1137     0.7879     0.4283      3.94

n genes in panel: 862

PRE-SPECIFIED VERDICT: REFUTED
EXIT=0
```

**RUN — command 4** (global-shift robustness): `/tmp/claude-0/w20/robust.py` — `EXIT=0`
```
panel-wide delta: mean -0.0971  median -0.0835  sd 0.5781
n genes delta<0: 490 / 862
TAF15 delta -0.8347  z vs panel -1.276
TAF15 raw counts  neg: [1489, 701, 783, 429]
TAF15 raw counts  pos: [1298, 3585, 1563, 2603, 276, 204, 785, 3028]
libsize neg: [907268, 994241, 406135, 307583]
libsize pos: [375572, 1174158, 588992, 1066043, 164967, 140423, 292897, 1356848]
```

**Sanity check performed before writing this report:** (a) re-read the lane ask and confirmed a decisive test with a pre-declared refutation criterion was executed and a verdict recorded; (b) confirmed my independently parsed 8/4 FISH split reproduces the count recorded in `emc-fourth-cohort-sra-2026-08-08.md`; (c) confirmed both scripts exited 0 and the verdict string is emitted by the script, not typed by me; (d) confirmed `git status` was never invoked to write and no repository path was opened for writing.

**PROPOSED (NOT RUN):**
- The genome-wide GSE243553 test I designed first and abandoned (below) — no code was written or executed for it.
- Any fusion-caller over the PRJNA1357027 FASTQs to resolve the 4 EWSR1-negative cases' actual partner. **Not run** (2.7 GB download; egress denied; and it is a separate piece of work).
- `scripts/preflight.sh` — **not run**, per COMMON-BRIEF §1; my dispatch did not instruct it and I wrote nothing to the tree for it to gate.

**A route I checked and abandoned, reported because the negative is useful to the next worker.** My first hypothesis was that the four NR4A3 fusions in GSE243553 (`EWSR1-NR4A3`, `TAF15-NR4A3`, `TCF12-NR4A3`, `TFG-NR4A3`, plus wild-type and reciprocal controls, all in one HEK293T background across 128 fusion oncoproteins) would show partner-independent chromatin output — a genuine test of the "all NR4A3 fusions are one disease" assumption. **It is not executable here.** `gse243553-eno3-overlap.json` retains only (i) per-peakset *summary* (`n_intervals`, `chroms`, `median_width`) and (ii) intervals restricted to the four ENO3 NBRE windows. **No genome-wide peak coordinates are retained**, and the source ZIP (`MOESM3_ESM.zip`, member `Supp_Data_1_new/*_markers.bed`) is behind the 403 egress denial above. This is UNDECIDED-because-data-inaccessible, and I name the exact missing artifact in "Next concrete action".

---

## Limitations

- **This is a refutation of one specific prediction, not of the fusion-partner model.** The prediction depends on an unverified premise I could not check: that the TempO-Seq *TAF15* probe lies **5′ of the fusion breakpoint**. If it lies 3′, the fusion allele contributes nothing to the probe and the test had **no power by construction**. The probe-to-transcript map in `emc-fourth-cohort-quant.json` assigns probes to genes by verbatim cDNA matching; it records no breakpoint-relative position. **The null is therefore weaker evidence than the alternative outcome would have been**, and I state that asymmetry rather than banking the null as a strong negative.
- **`EWSR1-` is not `fusion-negative`.** It is a break-apart call on the *EWSR1* locus only. An EWSR1-negative EMC-labelled case is consistent with `TAF15::NR4A3`, `TCF12::NR4A3`, `TFG::NR4A3`, or a false-negative FISH — the cohort memo says exactly this. So the negative arm is a **mixture of unknown composition**, which dilutes any TAF15-specific effect toward the null. With n = 4, one non-TAF15 case is 25% of the arm.
- **n = 4 vs 8.** The exact permutation distribution has 495 points, so the smallest attainable one-sided p is 1/495 ≈ 0.002; power against realistic effects is low. A null here does not exclude a modest true effect.
- **FFPE, 1997–2020, one batch, no adjustable covariate.** The parent module declined a 6-vs-6 differential-expression list for precisely these reasons. I did not overturn that judgement — I asked a **single pre-specified question** with exact inference and panel calibration, which is a different statistical object from a ranked genome-wide list. The degradation confound still applies to the direction of the observed shift and is unresolvable from the deposited metadata.
- **Targeted 862-gene panel.** *NR4A3*, *EWSR1*, *TCF12*, *TFG*, *ENO3*, *PPARG*, *SEMA3C*, *NR4A1* and *NR4A2* are **absent from this panel**, so the direct fusion-target question and the fusion-transcript question itself cannot be asked of this cohort at all. A gene absent from the table is a statement about the panel, never about the tumour.
- **Counts are raw and lossy-floored** per the source module's own units statement; CPM normalisation is mine and is a per-column library-size correction only.
- **What this cannot claim.** Nothing here bears on efficacy, safety, selectivity, therapeutic window, potency, dosing or clinical readiness of any agent, target or gene, and no such quantity was computed. No reagent of any kind was designed. Runs are not samples and samples are not people: n = 12 is BioSamples, not patients-by-chart. The *TAF15* and *VCAN* directions are **associations within one deposit**, not validated findings and not transferable to any other cohort.
- **Provenance honesty.** The `Prognosis` B/G key remains undefined by the deposit; I did not use it, and this report asserts no outcome meaning for it.

---

## Stop condition

**Condition set in advance:** a decisive test executed with a pre-declared refutation criterion and a verdict recorded — or an evidence-backed statement that no accessible public data can decide the hypothesis, naming the one dataset that would.

**MET, by the first branch.** The test ran (exit 0), against a decision rule fixed before execution, and returned **REFUTED** for the primary hypothesis, with a pre-specified negative control behaving correctly.

The secondary branch also produced an evidence-backed inaccessibility statement for the abandoned chromatin route: **the one dataset that would decide it is GSE243553 supplementary `MOESM3_ESM.zip`, members `Supp_Data_1_new/{EWSR1,TAF15,TCF12,TFG}-NR4A3_markers.bed` plus the `NR4A3` full-length and `NR4A3-EWSR1` reciprocal controls** — genome-wide interval coordinates, currently retained only as summary counts, and behind a 403 CONNECT denial from this container.

---

## Tool-call and wall-clock count actually used

**Tool calls: 21.** **Wall clock: approximately 12 minutes** (first `date -u` 01:56:52 UTC; final command block 02:01:11 UTC, plus report composition). Both well inside the ~40-call / ~40-minute self-observed target. No compute was left running; nothing is in flight.

---

## Next concrete action

**One successor task for this lane, in priority order — the first is the one I would hand over:**

**Resolve the fusion partner in the four EWSR1-FISH-negative PRJNA1357027 specimens by running a fusion caller over their public FASTQs**, and re-run exactly this pre-specified test with `TAF15::NR4A3`-confirmed cases as the positive arm instead of `EWSR1-` as a proxy. This converts a mixture-diluted proxy label into the real one, and it is the single change that would make either outcome of my test interpretable. Feasibility, stated honestly: the FASTQs are public and complete (12/12 runs carry populated `fastq_ftp`, 2,704,945,123 bytes ≈ 2.7 GB), but **this container cannot fetch them** (403 CONNECT), so it needs the Actions-runner escape hatch and a worker with a write path. It also needs a caveat carried forward: TempO-Seq is a targeted ligation panel, so whether the reads even span a fusion junction is **unknown** and must be checked before the caller is trusted — the cohort memo already flags this as "the fusion-partner call the FISH cannot make."

*Secondary, if the above is judged out of budget:* retrieve the GSE243553 `MOESM3_ESM.zip` peak BEDs named in the Stop condition and run the partner-interchangeability chromatin test I specified but could not execute — is the chromatin output of the four NR4A3 fusions determined by the shared NR4A3 moiety or by the 5′ partner? That question bears directly on whether EMC's non-EWSR1 variants are one disease, and the internally-controlled 128-fusion HEK293T panel is an unusually clean substrate for it.

result: Lane 20 executed a pre-specified, exactly-permuted within-EMC test on the retained PRJNA1357027 cohort (n=12, per-sample EWSR1 FISH) — the first expression reading of that deposit against its fusion labels — and the "TAF15 elevated in EWSR1-FISH-negative EMC" hypothesis is REFUTED (δ = −0.83 log2CPM, one-sided exact p = 0.99 over all 495 label splits; negative control FUS null at p = 0.91); the alternative GSE243553 chromatin route is UNDECIDED because genome-wide peak coordinates are not retained and egress is 403-denied.
