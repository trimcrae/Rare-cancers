> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

`date -u` end: `Tue Sep  8 02:30:32 UTC 2026`

---

## Worker

**Worker ID:** W20d · **Lane 20 second refill** — generalise W20c's probe-position failure mode across the corpus.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). This is a self-report from my own system context, not an observed fact; no environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at **start**: `Tue Sep  8 02:26:29 UTC 2026`
`date -u` at **end**: `Tue Sep  8 02:30:32 UTC 2026`

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (run at start; the long `no_proxy` / `NO_PROXY` / `JAVA_TOOL_OPTIONS` / `npm_config_noproxy` lines are retained verbatim in the transcript and contain no model information):

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

**Repository HEAD actually read: `b9a0257e6acff53ad22535cf2adf261313e0b250`.** This is neither the frozen campaign commit `92abbcb90…` named in `COMMON-BRIEF.md` nor W20c's `103ff76f…`; the drift is the coordinator's own collection commits of earlier workers' reports (`git status --porcelain` shows 16 further worker reports still untracked plus a modified `WAVE-LOG.md`). **Every non-report file I read is committed at this HEAD.** **No file under `/home/user/Rare-cancers` was created, modified or staged; no git write of any kind was performed.** All execution was under `/tmp/claude-0/w20d/`.

---

## Question

**Does the probe-position failure mode W20c found for the TempO-Seq *TAF15* probe invalidate any *other* verdict in this repository that rests on a targeted-panel probe measurement of a fusion transcript, and what is the general check that would have caught it?**

Open because W20c settled exactly one probe and explicitly left the generalisation to a successor ("take the probe sequences already committed … and search each against TAF15 cDNA 1–570 and against the six committed fusion-partner transcripts' retained 5′ regions"). The question matters beyond bookkeeping: if the same failure mode is latent elsewhere, other nulls are being read as negatives when they had no power.

---

## Prior-work check

Commands actually run and what they showed:

```
rg -n -il "tempo-?seq" --glob '!.git'
   -> 30 files. Of these, exactly 5 are conclusion-bearing about the probe deposit:
      research/manuscripts/fusion-output/{emc-fourth-cohort-sra-2026-08-08.md,
        nr4a3-fusion-transcriptional-output.md,nr4a3-cistrome-search-2026-08-08.md}
      research/manuscripts/dependency/emc-atr-vulnerability-assessment.md
      research/modalities/{emc-fourth-cohort-quant.json,emc_fusion_read_scan.py}
      + the four campaign reports W01/W02/W19/W20*

rg -n -i "panel|targeted rna|nanostring|amplicon|archer|fusionplex|qpcr|rt-pcr|taqman" --glob '!.git' -l
   -> no second targeted-panel expression deposit exists in the corpus; "panel" elsewhere
      means the GSE243553 ATAC peakset panel (W20b/W19c) or a peptide/construct panel.

rg -n -i "probe_start|probe_end|probe_position|breakpoint_relative|transcript_position|
          probe_cdna|retained_region|probe_offset" --glob '!.git'
   -> ZERO hits on any probe record. `cdna_start_0based` exists but only on EXON records
      (emc-construct-inputs.json, emc_fet_construct_designs.py, pgr_parent_engagement.py).

cut -f1 research/modalities/emc-fourth-cohort-gene-counts.tsv | grep -x -E "NR4A3|NR4A1|NR4A2|
      EWSR1|TAF15|TCF12|TFG|FUS|ENO3|PPARG|SEMA3C"
   -> FUS, TAF15 only.
```

**Closed items I confirmed I am not replaying** (`CLOSED-WORK.md`, read in full): Hofvander/EGA — no Hofvander material, no EGA request; **Brenca — not touched** (explicitly excluded by my dispatch as already recovered/DUPLICATE); **PUB-EMC-CLASSIFICATION — not touched** (user-rejected, closed); GSE4303/GSE28866 — not re-read as data, only checked for whether a *partner-gene expression endpoint* exists in the manuscript that reads them (it does not); Davis, promoter transfer, inverse bounds, methylation, the clinical checkpoints — none touched. **No network request of any kind was made.** The 403 CONNECT denials on NCBI/EBI/Ensembl and the GSE243553 `MOESM3_ESM.zip` route were **not probed, not retried and not routed around**; the vendor TempO-Seq probe manifest remains an honest unrecovered source. **I hit no content-policy refusal.**

W20c's proposed successor task ("probe-inventory check that needs no network at all") had **not** been run. I ran it. That is not a duplication — it is the execution of an explicitly handed-over task.

---

## Method / inputs

All inputs committed at HEAD `b9a0257e…`. Nothing downloaded.

| Input | Path | Used for |
|---|---|---|
| Probe/sequence counts | `research/modalities/emc-fourth-cohort-probe-counts.tsv` | all 213,007 distinct 50-nt sequences × 12 runs |
| Gene counts | `research/modalities/emc-fourth-cohort-gene-counts.tsv` | 862 genes × 12 runs, raw reads |
| Provenance + labels | `research/modalities/emc-fourth-cohort-quant.json` | `probe_map`, `per_run.*.ewsr1_break_apart_fish`, units statements |
| Quant source | `research/modalities/emc_fourth_cohort_quant.py` | how probes were *offered* to the matcher (lines 395–460, 583) |
| Transcript models | `research/modalities/emc-construct-inputs.json` | cDNA + per-exon `exon_length_nt` / `cdna_start_0based` for EWSR1, TAF15, FUS, TCF12, TFG, NR4A3 |
| Breakpoints | `research/modalities/nr4a3-fusion-junction-atlas.json` | `donor_symbol` / `donor_exon_end` for every graded junction |
| Existing assay gate | `research/modalities/emc_fusion_read_scan.py` | `assay_is_capable_of_spanning_a_junction()`, lines 177–200 |

**Tools:** Python 3.11.15, stdlib only (`json`, `itertools`, `math`, `statistics`, `collections`, `re`). No third-party package, no network, no GPU, no paid API.

**Decision rules, fixed in the script docstring before execution:** for probe span `[start,end]` (1-based cDNA) and retained-region end `E` (cumulative cDNA end of the donor exon) — `POWER` iff `end ≤ E`; `STRADDLE` iff `start ≤ E < end`; `NO-POWER` iff `start > E`. Statistical recomputation used W20's own pre-specified pipeline (CPM → log2(x+1) → δ = mean(neg) − mean(pos) → complete enumeration of all C(12,4)=495 label splits), re-implemented independently from the committed counts rather than copied.

---

## Result

### 1. Swept inventory — every conclusion in the corpus resting on a targeted-panel probe measurement of a fusion transcript

The corpus contains exactly **one** targeted-panel expression deposit (PRJNA1357027 / SRP640302, TempO-Seq) and **no** second panel/amplicon/qPCR expression deposit. Within it, only **FUS** and **TAF15** of the fusion-relevant genes carry an assigned probe. The complete inventory is therefore five items:

| # | Conclusion | Where | Probe position recorded anywhere? | Recoverable? | Classification |
|---|---|---|---|---|---|
| 1 | *TAF15* is not elevated in EWSR1-FISH-negative EMC (primary endpoint) | W20 §Result | **No** — no positional field exists | Yes | **NO-POWER** — already relabelled UNDECIDED by W20c; **confirmed here independently** |
| 2 | *FUS* negative control behaved as a control should | W20 §Result, item 2 | **No** | Yes | **VERIFIED for its stated function; probe is also 3′** — see §3 |
| 3 | *NR4A3, EWSR1, TCF12, TFG, ENO3, PPARG, SEMA3C, NR4A1, NR4A2* are "absent from this panel" | W20 §Limitations | n/a (an absence claim about the probe→gene map) | Yes | **UNVERIFIED — and materially wrong for at least EWSR1, TCF12, TFG.** See §4 |
| 4 | *VCAN* / *FN1* descriptive rows | W20 §Result | n/a | n/a | **NOT AFFECTED** — ordinary genes, not fusion transcripts; no breakpoint applies |
| 5 | "A processed matrix cannot carry a breakpoint, and neither can a targeted probe assay" — the deposit is refused for fusion calling | `emc_fusion_read_scan.py` §docstring; `nr4a3-fusion-transcriptional-output.md` §Limitation 1 / §1271; `emc-fourth-cohort-sra-2026-08-08.md` | n/a (a refusal, not a measurement) | n/a | **NOT AFFECTED — and correct.** These decline to read the deposit rather than reading a null from it |

**Rows outside the inventory, checked and excluded with reasons.** W20b and W19c (GSE243553 partner-interchange / panel-wide clustering) rest on ATAC-seq peak intervals, not probes — no probe, no breakpoint-relative position, failure mode does not apply. `nr4a3-fusion-transcriptional-output.md` reads GSE4303 (GPL3290) and GSE28866 arrays, which *are* probe-based, but a targeted grep for any 5′-partner gene used as a measured endpoint (`(EWSR1|TAF15|TCF12|TFG)` within 60 characters of `log2|fold|z-score|percentile|delta|rank|median expression`) returned **zero rows**: its endpoints are *NR4A3 target gene sets* — ordinary downstream genes measured on ordinary probes — not the chimeric transcript. `emc-atr-vulnerability-assessment.md` names TempO-Seq only in a candidate-route table, and carries no measurement from it. **No verdict outside W20 is affected.**

So the honest headline is close to the "welcome answer" the dispatch allowed: **the probe-position failure mode invalidates no verdict beyond the one W20c already relabelled.** What the sweep *did* turn up is a different, adjacent defect in the same report (item 3), which is a matcher/filter artefact rather than a probe-position artefact.

### 2. Probe positions computed for every recoverable case (PRIMARY, computed)

Only one probe is assigned to each of TAF15 and FUS in the whole 213,007-row table.

| Gene | Probe (50 nt) | cDNA span, 1-based | Occurrences | Retained region for the reported EMC breakpoint | Verdict |
|---|---|---|---|---|---|
| **TAF15** | `CTTCTGTCTCCTCCATAGCCTCCTCGATCTCCTCCATAACCTCCTCGATC` (antisense) | **1617–1666** (exon 15 of 16) | 1 (unique) | exon 6 ends at cDNA **570** | **NO-POWER, +1,047 nt 3′** |
| **FUS** | `CCGATTAAAGTCTGCCCGGCGAGTAGCAAATGAGACCTTGATAGGATTTC` (antisense) | **1158–1207** | 1 (unique) | exon 6 ends at cDNA **840** | **NO-POWER, +318 nt 3′** |

The TAF15 row **independently reproduces W20c to the nucleotide** by a script written without reference to W20c's code, and extends it: the probe is NO-POWER against *every* TAF15 donor exon 1–14 (offsets +1,524 down to +354 nt) and only "POWER" against exons 15–16, which are not reported breakpoints and lie downstream of the probe anyway.

The FUS row is **new**. It is reported in §3.

### 3. W20's *FUS* control — independently re-verified, with one correction

**(a) The numbers are confirmed.** I recomputed W20's entire statistic from the committed counts with an independent implementation. Verbatim (RUN, exit 0):

```
TAF15    medRaw=  1041.5 delta=-0.8347 p1=0.9899 p2=0.0182 panelPct=9.11
FUS      medRaw=  1023.0 delta=+0.0789 p1=0.4808 p2=0.9131 panelPct=62.12
VCAN     medRaw=  3223.0 delta=-1.0618 p1=0.9778 p2=0.0303 panelPct=4.58
FN1      medRaw=  1707.5 delta=-1.1137 p1=0.7879 p2=0.4283 panelPct=4.00
panel-wide delta mean=-0.0971 median=-0.0835 sd=0.5784 n_neg=490/862
TAF15 z vs panel: -1.275     FUS   z vs panel: +0.304
```

δ, both p-values, medians, the panel-wide shift and the z all reproduce W20 exactly. The four panel percentiles differ by a constant **+0.06** (9.11 vs 9.05, 62.12 vs 62.06, 4.58 vs 4.52, 4.00 vs 3.94) — I used a midpoint rank `(i+0.5)/n`, W20 evidently used `i/n`. That is a reporting convention, not a discrepancy in the statistic, and I record it rather than presenting a false exact match. The 8/4 FISH split also reproduces (`EWSR1-` = SRR35940648, 654, 656, 657).

**(b) The correction: the FUS probe lies 3′ of the FUS exon-6 breakpoint too, by 318 nt.** W20c wrote that the FUS control "stands unchanged"; verified independently, that is **true for the control's stated function and incomplete as a statement about the control's position**. Precisely:

- **CONFIRMED.** W20's stated use of *FUS* was as a **specificity control** — "the instrument is not manufacturing differences everywhere". That function depends only on the pipeline, normalisation and permutation machinery, not on where the probe sits. It holds: δ = +0.079, two-sided exact p = 0.9131, 62nd percentile, z = +0.30 against the panel. **The control passes and W20's use of it is sound.**
- **CORRECTED / ADDED.** *FUS* could **never** have served as a demonstration that this assay is *capable* of detecting partner-side fusion readthrough, because its probe is in the same position class as TAF15's — 3′ of the retained portion. Nothing in W20 claims it was; but W20c's blanket "stands unchanged" would license that reading, and it should not. **A negative control that shares the primary endpoint's blind spot is not a positive control and must not be quoted as evidence the instrument had power.**
- **A second-order consequence, stated and not inflated.** Because both probes are 3′, the TAF15-vs-FUS contrast is **position-matched**: the difference between δ(TAF15) = −0.83 and δ(FUS) = +0.08 is *not* explained by probe placement. Under W20c's post-hoc reasoning (a 3′ probe should read *less* when one allele is diverted into a chimera stopping at exon 6), FUS behaving null is **coherent** — FUS::NR4A3 is not an EMC fusion, so no allele is diverted. **This is a consistency observation, not a finding.** It is post-hoc, n = 4 vs 8, in FFPE material spanning 23 collection years, against a documented mild global arm shift, in a negative arm of unknown composition. **ASSOCIATION, hypothesis-generating, not validated.** It is neither a positive result nor an upgrade of any null.

### 4. The one materially wrong conclusion the sweep found (item 3) — an *absence* claim, not a null

W20's Limitations state that *EWSR1*, *TCF12*, *TFG* (among others) are **"absent from this panel"**. The committed data contradict that for at least three of them. Searching all 213,007 distinct sequences against the committed partner cDNAs (RUN, exit 0):

| Gene | Sequence found | cDNA span | `assigned_gene` in the table | Counts across 12 runs | Position vs reported EMC breakpoint |
|---|---|---|---|---|---|
| **EWSR1** | `GCTTGTTTCCATCCTGCGGTCTTGTAGGTGCAGTGGCTGCTGGCTGCTGC` | **453–502** | `unassigned` | 337, 521, 423, 459, 807, 0, 0, 735, 791, 999, 281, 183 (median 459) | **POWER** vs donor exons 7–13 (offsets −409 to −1,033 nt) |
| **TCF12** | `CCTTCATGGGCTCCTAATCGACTGTCATTCAAGTGATCACTGTAATGAGG` | 523–572 | `unassigned` | median 243, present in 10/12 | no exon-resolved TCF12 breakpoint exists in the literature (repository's own statement), so no verdict is computable |
| **TCF12** | `CTCACACATCATAAGCAACAACTTCTGTTTAGCTGATTAACACTGAAATG` | 4128–4177 | `unassigned` | median 499 | as above |
| **TFG** | `GGTGTAGAGGAGCCTCCTTATCGATAACCAGGTCCAGGTTGGGTATAGCC` | 1442–1491 | `unassigned` | median 360 | **NO-POWER** vs donor exons 4/5/6 (+756/+591/+450 nt) |

**Mechanism, fully diagnosed from the committed source.** `emc_fourth_cohort_quant.py:583` builds the probe set as the sequences present in **every** read run (`n_probes_common_to_every_read_run = 1645`). Only those 1,645 were offered to the cDNA matcher (`n_probes_offered: 1645` = 906 unique + 77 multi-gene + 662 unassigned). The EWSR1 sequence reads 0 in the two smallest-library runs (SRR35940651, SRR35940652; libraries 164,967 and 140,423), so it was **never offered**, and the TSV's `unassigned` label conflates *"offered and unmatched"* (662) with *"never offered"* (~211,439). The module's own units statement already warns about both halves — *"a zero in the probe table … is not a measurement of zero reads"* and *"a gene with no assigned probe is ABSENT FROM THIS TABLE, which is a statement about the panel and the matcher, never about the tumour."* W20's Limitations attributed the absence to **the panel**; the committed evidence attributes it to **an intersection-across-runs filter interacting with a lossy-counting persistence cap**.

**This is classified UNVERIFIED→corrected, not "refuted".** I have not established that this sequence *is* the vendor's EWSR1 probe — the vendor manifest is behind the recorded egress denial and I did not probe it. What is established: a 50-nt sequence with an **exact, unique** match inside EWSR1 cDNA carries real counts in 10 of 12 runs, and it lies **inside the retained 5′ portion** of every EMC-reported EWSR1 breakpoint. So the statement "the fusion-transcript question cannot be asked of this cohort at all" is **not supported**; for EWSR1::NR4A3 it appears to be askable with a probe that has power. **I did not test it.** Running an endpoint on a sequence I discovered mid-run, with no pre-specified rule, is exactly the post-hoc inflation this dispatch forbids. It is routed as the successor task.

### 5. The general precondition, as a checkable rule

**RULE (probe-power precondition).** *Before a probe-based null is read as evidence of absence of a fusion transcript, the probe's target interval must lie wholly within the retained portion of that fusion transcript.* Formally, for probe span `[p_start, p_end]` in the donor transcript's cDNA coordinates and breakpoint at cumulative cDNA position `E`:

```
power(probe, junction) = POWER     if p_end   <= E          # 5' partner: retained
                       = STRADDLE  if p_start <= E < p_end   # partial, quantify before use
                       = NO-POWER  if p_start >  E           # null carries NO information
if power == NO-POWER  ->  the endpoint's verdict is UNDECIDED, never REFUTED
if position is not recorded and not recoverable -> UNVERIFIED, never REFUTED
```
(For a 3′ acceptor such as NR4A3 the inequality reverses: the retained portion is everything downstream of the acceptor exon start.)

**What committed field would have to exist for this to be machine-checkable.** Two, and only two, joined by gene symbol:

1. **On each probe record:** a transcript-coordinate span — `probe_transcript_id`, `probe_cdna_start`, `probe_cdna_end`, `probe_strand`. The natural home is `emc-fourth-cohort-quant.json` → `probe_map.probe_to_gene`, which today stores only `{probe_sequence: gene_symbol}`.
2. **On each junction record:** the donor-side cumulative cDNA cut position. `nr4a3-fusion-junction-atlas.json` records `donor_exon_end` (an exon *ordinal*) and `donor_coding_nt_through_cut`, but **no cDNA cut coordinate** — the ordinal must be resolved against a transcript model in a *different* file before any comparison is possible, which is precisely why the check was never made.

**Does any such field exist today? No.** `rg` for `probe_start|probe_end|probe_position|breakpoint_relative|transcript_position|probe_cdna|retained_region|probe_offset` across the tracked tree returns **zero hits on any probe record**. `cdna_start_0based` exists, but only on *exon* records in `emc-construct-inputs.json`, `emc_fet_construct_designs.py` and `pgr_parent_engagement.py`. The join W20c and I performed by hand is therefore not reproducible by any committed script.

**What *does* exist, and why it did not catch this.** `research/modalities/emc_fusion_read_scan.py:177` already implements a sibling gate, `assay_is_capable_of_spanning_a_junction()`, which refuses to scan a deposit whose metadata names a targeted probe assay — with exactly the right reasoning in its docstring (*"a zero from scanning it would carry no information"*). **That gate is one level too coarse.** It answers "can a *read* cross from one gene into another?" — a property of the assay. It does not answer "does this *probe* lie inside the retained half?" — a property of the probe. A TempO-Seq deposit correctly fails the read-spanning gate for fusion *calling* while still being perfectly usable for a partner-side *expression* endpoint — provided the probe is 5′. W20 was doing the second thing, and no gate covered it. **The general check is the same idea applied one level down, and the repository has already accepted the idea; it has only not implemented it at probe resolution.**

**PREDICTION rows: none.** This report contains no model output and no extrapolation.

### 6. Label routing — exact current text and exact proposed text

I have relabelled nothing. Four routings, for the coordinator / the report owners to accept or reject.

**R1 — W20 §Result, primary verdict.** *(Already routed by W20c; restated only so the coordinator has one list. Independently confirmed here.)*
- Current: `**The hypothesis is REFUTED.** *TAF15* is not elevated in EWSR1-FISH-negative EMC; it is **lower**.`
- Proposed: `**The hypothesis is UNDECIDED — the test had no power by construction.** The TempO-Seq *TAF15* probe lies 1,047 nt 3′ of the exon-6 breakpoint (cDNA 1617–1666, exon 15), so the chimeric transcript contains none of its target and the fusion allele could not have contributed to the measurement. The computed values below stand exactly as reported; only the inferential label changes. (W20c, confirmed independently by W20d.)`

**R2 — W20 §Limitations, panel-membership claim.**
- Current: `**Targeted 862-gene panel.** *NR4A3*, *EWSR1*, *TCF12*, *TFG*, *ENO3*, *PPARG*, *SEMA3C*, *NR4A1* and *NR4A2* are **absent from this panel**, so the direct fusion-target question and the fusion-transcript question itself cannot be asked of this cohort at all. A gene absent from the table is a statement about the panel, never about the tumour.`
- Proposed: `**Targeted 862-gene panel.** *NR4A3*, *EWSR1*, *TCF12*, *TFG*, *ENO3*, *PPARG*, *SEMA3C*, *NR4A1* and *NR4A2* carry **no probe assigned in `emc-fourth-cohort-gene-counts.tsv`**. ⚠ That is a statement about the panel **and the matcher**, never about the tumour, and for at least *EWSR1*, *TCF12* and *TFG* it is the matcher: the probe→gene map was offered only the 1,645 sequences present in **every** run (`n_probes_common_to_every_read_run`), and sequences with an exact unique match inside *EWSR1* (cDNA 453–502, counts in 10/12 runs), *TCF12* (two) and *TFG* cDNA read 0 in the smallest-library runs and were never offered. The *EWSR1* sequence lies **5′** of every EMC-reported *EWSR1* breakpoint, i.e. inside the retained portion. So "the fusion-transcript question cannot be asked of this cohort at all" is **withdrawn as unsupported**; it is UNVERIFIED whether that sequence is the vendor's *EWSR1* probe, and the question is open pending a pre-specified test. (W20d.)`

**R3 — W20 §Result, item 2 (the FUS control).**
- Current: `**PRIMARY.** *FUS*, the pre-specified negative control, behaved as a control should (δ = +0.079, two-sided p = 0.913, 62nd percentile). The instrument is not manufacturing differences everywhere, which is what makes the *TAF15* null interpretable rather than merely uninformative.`
- Proposed: `**PRIMARY.** *FUS*, the pre-specified negative control, behaved as a control should (δ = +0.079, two-sided p = 0.913, 62nd percentile; independently recomputed by W20d). The instrument is not manufacturing differences everywhere. ⚠ *FUS*'s probe also lies 3′ of the FUS exon-6 breakpoint (cDNA 1158–1207, +318 nt), so it is a **specificity** control only: it shares the primary endpoint's blind spot and is **not** evidence that the assay could have detected partner-side readthrough. Its one useful additional property is that it makes the *TAF15*-vs-*FUS* contrast position-matched. (W20d.)`

**R4 — W20c §Next concrete action, a factual correction to the successor spec.**
- Current: `take the **1,645 probe sequences already committed** in `emc-fourth-cohort-probe-counts.tsv` — including the **662 currently `unassigned`**`
- Proposed: `take the **213,007 distinct sequences committed** in `emc-fourth-cohort-probe-counts.tsv` — of which **212,101 are labelled `unassigned`**, a label that conflates the 662 that were offered to the matcher and did not match with the ~211,439 that were **never offered** (only the 1,645 sequences present in every run were). (W20d; task executed — see W20d §Result 4.)`

**No negative finding is removed by any of these.** R1 and R3 weaken claims; R2 withdraws an over-broad *absence* claim and replaces it with a narrower, better-evidenced one plus an explicit UNVERIFIED; R4 corrects a count. Nothing is upgraded to a positive.

---

## Validation evidence

**Environment for every RUN below:** `Python 3.11.15`, stdlib only; container HEAD `b9a0257e6acff53ad22535cf2adf261313e0b250`; **no network request of any kind was made**; all execution under `/tmp/claude-0/w20d/`.

**RUN — command 1** (start stamp / env / HEAD / write-isolation):
```
date -u; env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'
cd /home/user/Rare-cancers && git rev-parse HEAD && git status --porcelain | head -20
```
→ exit 0. `Tue Sep  8 02:26:29 UTC 2026`; HEAD `b9a0257e…`; the only dirty paths are the coordinator's `WAVE-LOG.md` and 16 untracked worker reports. **No path authored by me appears anywhere in the tree.**

**RUN — command 2** (independent recomputation + probe placement): `/tmp/claude-0/w20d/w20d.py`
```
cd /tmp/claude-0/w20d && python3 --version && python3 w20d.py; echo "EXIT=$?"
```
Verbatim key output (abridged only by eliding the 14 additional TAF15 exon rows and 14 FUS exon rows, all reproduced in §2):
```
runs: 12 EWSR1-: 4 ['SRR35940648', 'SRR35940654', 'SRR35940656', 'SRR35940657'] EWSR1+: 8
library sizes: [375572, 1174158, 907268, 588992, 1066043, 164967, 140423, 292897, 994241, 1356848, 406135, 307583]
permutations enumerated: 495
TAF15    medRaw=  1041.5 delta=-0.8347 p1=0.9899 p2=0.0182 panelPct=9.11
FUS      medRaw=  1023.0 delta=+0.0789 p1=0.4808 p2=0.9131 panelPct=62.12
VCAN     medRaw=  3223.0 delta=-1.0618 p1=0.9778 p2=0.0303 panelPct=4.58
FN1      medRaw=  1707.5 delta=-1.1137 p1=0.7879 p2=0.4283 panelPct=4.00
panel-wide delta mean=-0.0971 median=-0.0835 sd=0.5784 n_neg=490/862
TAF15 z vs panel: -1.275
FUS   z vs panel: 0.304
FUS raw neg: [1749, 2764, 830, 231]  pos: [783, 2463, 1182, 2057, 170, 61, 864, 2649]

probe rows: 213007 distinct seqs: 213007
probes assigned to fusion genes: {'TAF15': 1, 'FUS': 1, 'EWSR1': 0, 'TCF12': 0, 'TFG': 0, 'NR4A3': 0}
top assigned_gene values: [('unassigned', 212101), ('ENSG00000283738.3', 5), ('FAM156A', 3), ...]

--- TAF15: cDNA 2162 nt, 16 exons
  probe CTTCTGTCTCCTCCATAGCCTCCTCGATCTCCTCCATAACCTCCTCGATC -> antisense(rc) cDNA 1617..1666  occurrences=1
     vs exon-6 end (cDNA 570): NO-POWER  offset=+1047 nt
     vs exon-14 end (cDNA 1263): NO-POWER  offset=+354 nt
--- FUS: cDNA 1824 nt, 15 exons
  probe CCGATTAAAGTCTGCCCGGCGAGTAGCAAATGAGACCTTGATAGGATTTC -> antisense(rc) cDNA 1158..1207  occurrences=1
     vs exon-6 end (cDNA 840): NO-POWER  offset=+318 nt
     vs exon-10 end (cDNA 1142): NO-POWER  offset=+16 nt
     vs exon-11 end (cDNA 1244): POWER  offset=-86 nt

--- sweep: any of the 213007 distinct probe sequences inside a retained 5' region? ---
  TAF15: retained 5' region = cDNA 1..2162; probes landing inside: 1
  FUS:   retained 5' region = cDNA 1..1824; probes landing inside: 2
  EWSR1: retained 5' region = cDNA 1..2400; probes landing inside: 1
  TCF12: retained 5' region = cDNA 1..6114; probes landing inside: 2
  TFG:   retained 5' region = cDNA 1..1907; probes landing inside: 1
EXIT=0
```

**RUN — command 3** (characterising the unassigned partner-matching sequences): `/tmp/claude-0/w20d/w20d2.py` — `EXIT=0`
```
rows= 213007 unassigned= 212101 assigned= 906 distinct genes= 862
EWSR1: GCTTGTTTCCATCC...GCTGCTGC antisense cDNA 453..502 assigned_gene='unassigned'
       counts=[337, 521, 423, 459, 807, 0, 0, 735, 791, 999, 281, 183] median=459
    vs EWSR1 exon-7 end 862: POWER offset=-409      vs exon-13 end 1486: POWER offset=-1033
TFG:   ...cDNA 1442..1491 assigned_gene='unassigned' median=360
    vs TFG exon-6 end 992: NO-POWER offset=+450
FUS:   ...cDNA 1157..1206 assigned_gene='unassigned' counts=[0,0,32,0,0,0,0,0,0,0,0,0] median=0
```

**RUN — command 4** (mechanism, from the committed source):
```
grep -n "offered\|n_probes\|probes *=" research/modalities/emc_fourth_cohort_quant.py
sed -n '395,460p' research/modalities/emc_fourth_cohort_quant.py
```
→ exit 0. `583: probes = sorted(set().union(*[set(runs[a]["counts"]) for a in accs]))`; `447: "n_probes_offered": len(probes)`; artifact field `n_probes_common_to_every_read_run = 1645`.

**RUN — command 5** (missing-field sweep): the `rg` for eight candidate probe-position field names, quoted in §Prior-work check → **zero hits on any probe record**, exit 0.

**PROPOSED (NOT RUN):**
- **Any test of the candidate EWSR1 probe as an endpoint.** Deliberately not run — no pre-specified rule existed before I found the sequence, and running it post-hoc would be the exact inflation this dispatch forbids. Routed as successor.
- **Confirmation against the vendor's TempO-Seq probe manifest** — behind the recorded egress denial. **Not attempted; no archive route probed or routed around.**
- **A `probe_position_gate()` implementation.** I did not author code into the tree; the rule is specified in §5 in a form a lane owner can implement. `emc_fourth_cohort_quant.py` and `emc_fusion_read_scan.py` are not mine to change.
- **`scripts/preflight.sh`** — not run, per COMMON-BRIEF §1; my dispatch did not instruct it and I wrote nothing to the tree for it to gate.
- **No reagent of any kind was designed, proposed or scored.**

---

## Limitations

- **The sweep's denominator is the tracked corpus at one HEAD.** A conclusion phrased without any of my search terms could have been missed. What I can state firmly is narrower and checkable: the corpus contains **one** targeted-panel expression deposit, and within it **two** fusion-partner genes carry an assigned probe. Both are placed above.
- **Every position is computed against the repository's own transcript models** (`ENST00000605844` TAF15, the committed FUS/EWSR1/TCF12/TFG records), not against a vendor manifest. A probe designed on a different isoform's numbering would land at the same *sequence*, which is what I matched, but isoform choice is not independently verified.
- **The EWSR1/TCF12/TFG sequences are candidate probes, not confirmed probes.** An exact unique cDNA match with real counts in most runs is consistent with a probe and is not proof of one. **UNVERIFIED is the correct word and I use it.**
- **"No power" is a construction argument, not a measurement of zero.** It states the chimeric mRNA contains none of the probe's target. It does not exclude a reciprocal `NR4A3::TAF15` or `NR4A3::FUS` transcript, which nothing here measures.
- **TCF12 has no verdict** because no exon-resolved TCF12::NR4A3 breakpoint exists anywhere in the literature (the repository's own statement). That is UNKNOWN, not NO-POWER.
- **My panel percentiles use a different rank convention from W20's** (+0.06 offset, §3a). Neither is wrong; the difference is recorded rather than smoothed over.
- **No clinical claim.** A probe measurement in a targeted panel of 12 FFPE tumour BioSamples establishes nothing about EMC efficacy, safety, selectivity, therapeutic window, potency, dosing or clinical readiness, and no such quantity was computed. There is no wet lab. Runs are not samples and samples are not people.

---

## Stop condition

**Set in advance:** a swept inventory of probe-based conclusions with a per-item VERIFIED / UNVERIFIED / NO-POWER classification, the general precondition stated as a checkable rule with its missing field named, and W20's *FUS* control independently confirmed or corrected.

**MET, all three parts.**
1. **Inventory:** five items, §1 — one NO-POWER (already relabelled), one VERIFIED-with-qualification, one UNVERIFIED-and-corrected, two NOT AFFECTED; plus explicit exclusions for W20b/W19c (peak intervals, not probes) and the array manuscript (no partner-gene endpoint). **No verdict outside W20 is affected by the probe-position failure mode.**
2. **Rule:** stated formally in §5. The missing field is a **probe-level transcript coordinate** (`probe_transcript_id` / `probe_cdna_start` / `probe_cdna_end` / `probe_strand`) on `probe_map.probe_to_gene`, joined to a **donor-side cDNA cut coordinate** on each junction record (the atlas stores only the exon *ordinal*). **Neither exists today** — `rg` over eight candidate names returns zero hits on any probe record. A coarser sibling gate does exist (`assay_is_capable_of_spanning_a_junction()`), and it is one resolution level too high to have caught this.
3. **FUS control:** numbers independently reproduced exactly; **CONFIRMED** as a specificity control; **CORRECTED** in that its probe is also 3′ (+318 nt), so it is not and never was evidence of assay power against partner readthrough.

Four label changes are routed with exact current and proposed text (§6). **I relabelled nothing myself.** No null was upgraded to a negative; no null was inflated into a positive; every negative finding I touched is preserved.

---

## Tool-call and wall-clock count actually used

**Tool calls: 19.** **Wall clock: 4 min 03 s of tool execution** (`date -u` start `02:26:29`, end `02:30:32`), plus report composition — measured, not estimated. Both inside the ~40-call / ~40-minute self-observed target. No compute is in flight; nothing was left running.

---

## Next concrete action

**One successor for this lane: pre-specify and run the EWSR1-probe endpoint that W20's test should have used.** The sequence `GCTTGTTTCCATCCTGCGGTCTTGTAGGTGCAGTGGCTGCTGGCTGCTGC` sits at EWSR1 cDNA 453–502, i.e. **inside the retained 5′ half of every EMC-reported EWSR1 breakpoint (exons 7–13)**, and carries real counts in 10 of 12 runs. It is the only sequence in the whole deposit with power against the partner-readthrough hypothesis. The successor must, **in this order and with the rule fixed in the script docstring before any count is read**: (i) confirm the sequence's uniqueness across the human cDNA set the matcher already used, or state plainly that the check could not be made offline; (ii) declare the direction — the fusion-partner model predicts EWSR1 reads **higher** in the EWSR1-FISH-**positive** arm, which is the opposite arm from W20's TAF15 test and therefore a genuinely independent prediction; (iii) run the identical exact-permutation machinery over all 495 splits with the panel percentile as calibration; (iv) treat the two runs where it reads 0 as `below persistence cap`, per the module's own `⛔ a_zero_in_the_probe_table` caveat, **not** as zeros. Bounded, offline, stdlib-only, no new access. Either outcome is publishable inside this repository's standards, and a null from it would be the first probe-based EMC fusion null in the corpus that actually had power.

*Secondary, and a better use of a tooling lane than of a science lane:* implement `probe_power_gate()` from §5 as a real committed check, which requires first adding the two missing coordinate fields. That converts the rule from a thing four workers rediscovered by hand into a thing a script refuses.
