> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check done: the two artifacts agree independently — `gse243553-eno3-overlap.json` records `median_width = 500` for all 32 peaksets, and every one of the ~800 intervals I parsed from the *separately generated* `-supplement.json` byte prefixes is exactly 500 bp wide. Both scripts exited 0, verdict strings are printed by the scripts, and the Git tree is unmodified. Report follows.

---

## Worker

**Worker ID:** W20b · **Lane 20 refill** — named secondary successor to W20: partner-interchangeability of the four NR4A3 fusions at the chromatin level.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). This is a self-report from my own system context, not an observed fact; no environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript.

Literal output of `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I' | sort` at start (the long duplicated `no_proxy` / `JAVA_TOOL_OPTIONS` / `GLOBAL_AGENT_NO_PROXY` / `npm_config_noproxy` lines are retained below in full as printed; nothing model-relevant was removed):

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

`date -u` at start: `Tue Sep  8 02:05:01 UTC 2026`
`date -u` at end: `Tue Sep  8 02:08:48 UTC 2026`

Repository HEAD read: `92abbcb905cacf07f14b238db50d1b98f6590374` (matches the frozen campaign commit). `git status --porcelain` shows one untracked path, `research/autonomy/opus-capacity-campaign-20260908/` — the coordinator's own campaign directory, which was already untracked before I started. **I created and modified nothing under `/home/user/Rare-cancers`, and performed no git write of any kind.** All execution was under `/tmp/claude-0/w20b/`. `df -h /` = 27 GiB available at start and at end (≥10 GiB budget satisfied); nothing was downloaded.

**W20's refutation is preserved unchanged.** Nothing in this report revises, softens or re-opens it: `TAF15` is not elevated in EWSR1-FISH-negative EMC in PRJNA1357027 (δ = −0.83 log2CPM, one-sided exact p = 0.99 over all 495 label splits; pre-specified negative control `FUS` null at p = 0.91), and W20's power caveat travels with it verbatim — *the TempO-Seq `TAF15` probe's position relative to the fusion breakpoint is unverified, so if the probe lies 3′ of the breakpoint the test had no power by construction, and the null is therefore weaker evidence than the alternative outcome would have been.* I did not re-run, re-derive or re-interpret that test.

---

## Question

**Is the chromatin output of the four NR4A3 fusions determined by the shared NR4A3 moiety or by the 5′ partner — i.e. are EMC's non-EWSR1 variants one disease at the chromatin level?**

Why it is open. The repository treats `EWSR1::NR4A3`, `TAF15::NR4A3`, `TCF12::NR4A3` and `TFG::NR4A3` as variants of one disease, and clinical practice does the same. But the repository's own retained evidence points the other way in at least one place: `PUB-FUSION-PARTNER-…-seat-citations-and-instruments.json` records Brenca 2019 verbatim — *"the ability of NR4A3 to recognize the SEMA3C target region was retained by the EWSR1-NR4A3 chimera but was impaired by TAF15-NR4A3"* — a partner-dependent, single-locus ChAP-qPCR result. Whether that generalises to the genome has never been tested here. GSE243553 is an unusually clean substrate because all fusions were expressed in **one HEK293T background**, so partner effects are not confounded with tumour lineage.

W20 designed this test, could not execute it, and named it as its secondary successor.

---

## Prior-work check

**Step 1 — did the data situation change?** Commands run:

```
python3 -c "...json.load('inputs/evidence-4878/EXACT-FILE-MANIFEST.json')..."
```
The capsule declares `source_commit 4878b9b9d1c082cea46e636dad47be419f1fe021`, `source_tree 2ff1a4d0…`, `source_parent 93b75888…`, scope *"Exact47 changed files from committed writer revision. File snapshot only, not the full repository or imported Git history."* All **47** files sit under `research/autonomy/OPERATING_PROTOCOL.md` and `research/autonomy/source-reuse-program-2026-09-08/**` — protocol text, checkpoint history, preflight logs and evidence ZIPs of the source-reuse program. **No peak coordinates, no GSE243553 material, no closure record bearing on this question.** Per the brief, that absence is UNKNOWN about ancestry, not proof of absence.

```
git ls-files | grep -i -E "gse243553|markers|peak|\.bed|bigwig|narrowPeak"
grep -rl -i "GSE243553" --exclude-dir=.git .
```
Four retained GSE243553 JSON artifacts plus `gse243553_eno3_overlap.py`, `peak_rss.py` and a test. No `.bed` file is tracked anywhere in the repository.

```
grep -rn -i -E "jaccard|interchange|partner-independen|pairwise.*peakset|one disease" \
  --exclude-dir=.git --include=*.py --include=*.json --include=*.md . | grep -v opus-capacity-campaign
```
All `jaccard` hits are unrelated (`proposal_dedup.py`'s text-shingle deduplication; two gene-set Jaccards inside the ATR/PPARγ ledger rows). **No pairwise comparison between GSE243553 peaksets exists anywhere in the tree.** This question has not been asked here before.

**Step 2 — verifying W20's characterisation myself, with one correction and one material discovery.**

- **W20 was right about `gse243553-eno3-overlap.json`.** Its `peakset_inventory` carries only `n_intervals`, `chroms`, `median_width`, `header`, `n_unparseable_lines` per peakset, plus intervals restricted to four ENO3 NBRE windows. No genome-wide coordinates. Confirmed by direct structural walk.
- **CORRECTION to the dispatch framing, and to a number.** `peakset_inventory` has **128 entries but only 32 are real peaksets**: 64 are `__MACOSX/…/._*` AppleDouble resource forks (220–276 bytes each, not data) and 32 are `Supp_Data_2_new/*.txt`, which are ATAC-seq enrichment tables of a different type, not interval files. So the panel available for comparison is **32 BED peaksets — 4 NR4A3 and 28 others — not ~124.** My dispatch's "~124 other fusions" is wrong, and every denominator below uses 28/32.
- **MATERIAL DISCOVERY — the situation has partly changed.** A **sibling artifact W20 did not examine**, `research/modalities/gse243553-eno3-overlap-supplement.json`, retains under `contents['SPRINGER::3::zip']['first_bytes']` a **≤600-byte verbatim prefix of each `*_markers.bed`** — the first ~26 hg38 chr1 intervals of every one of the 32 peaksets, **including all four NR4A3 fusions**. These are real genome-wide-derived coordinates, not summaries. They are a *truncated prefix*, not the genome, so the correct status is **partially retained**, not "retained". W20's statement was accurate about the file it inspected and incomplete about the deposit as retained here. This makes a genuine **location** test possible, which is a materially stronger instrument than the coarse route my dispatch anticipated.

**Closed items I confirmed I am not replaying** (`CLOSED-WORK.md`, line by line): I use no clinical data, no registry, no methylation, no promoter transfer, no inverse bound, no Hofvander/EGA material, no Brenca case identity (I quote Brenca only as published motivation, and make no claim about its cases), no GSE4303/GSE28866, no invented cohort, no drug or kinase quantity. I did **not** replay the 403-denied route — see below. I hit **no** content-policy refusal in this run.

---

## Method / inputs

**Standing access boundary, recorded and not tested.** The genome-wide `MOESM3_ESM.zip` route is recorded by W20 as a **403 CONNECT policy denial** at the agent proxy. I made **no network request of any kind** in this run — I did not re-probe it, did not route around it, and did not attempt an alternative host. It stands as an honest unrecovered source. The 2.7 GB PRJNA1357027 FASTQ set was likewise not downloaded.

**Inputs — both committed at the frozen commit, both read-only:**

| Input | Path | What I used |
|---|---|---|
| Peakset summaries | `research/modalities/gse243553-eno3-overlap.json` | `peakset_inventory` → `n_intervals`, `median_width` for 32 real BEDs |
| Coordinate prefixes | `research/modalities/gse243553-eno3-overlap-supplement.json` | `contents['SPRINGER::3::zip']['first_bytes']` → ≤600-byte verbatim BED prefix per peakset |
| Provenance | same two files | `_peak_call_provenance`, `genome_build`, `controls` |

Deposit: **GSE243553**, primary publication doi `10.1038/s41587-024-02347-4`, 128 fusion oncoproteins expressed in HEK293T. Assembly **hg38**, established by the deposit's own `!Sample_data_processing: Assembly: hg38` (recorded in `genome_build._how_established`). **The intervals are the authors' own marker calls from the Springer ESM — this repository called no peak** (`_peak_call_provenance`: GEO deposits fragments only, 80.1 GB, no peak call).

**Tools:** Python 3.11.15, standard library only (`json`, `itertools`, `math`, `statistics`, `re`). No third-party package, no network, no GPU, no paid API.

**Design.** Two analyses, both with the rule fixed in the script docstring before execution and the verdict string emitted by the script.

- **Analysis A — coarse shape.** Statistic *D* = mean pairwise absolute difference within a 4-member group, on log₁₀(`n_intervals`), on `median_width`, and on a combined 2-D Euclidean distance after z-standardising both features across the 32 peaksets.
- **Analysis B — location, chr1 prefix.** For each pair, take both retained prefixes, set *W* = min(last retained chr1 interval end of A, of B), and restrict both to `chr1:0–W`. Because the deposited BEDs are coordinate-sorted (verified: all 32 prefixes ascending), **each set is complete inside that window**, so the Jaccard index over `chr1:0–W` is exact for that window. Statistic = mean pairwise Jaccard within the group. Where one side extends past chr1 the boundary is its last chr1 peak, which is conservative.
- **Null for both:** exact enumeration of **all C(32,4) = 35,960** four-member subsets of the 32 peaksets. No Monte-Carlo error, no seed.
- **Groups, all pre-specified with a stated selection rule so none is cherry-picked:**
  - **TEST** — the four shared-3′-moiety fusions: `EWSR1-NR4A3`, `TAF15-NR4A3`, `TCF12-NR4A3`, `TFG-NR4A3`.
  - **POSITIVE ANALOGUE** — the four alphabetically-first non-NR4A3 `EWSR1-*` peaksets, i.e. a group sharing a **5′** partner instead: `EWSR1-ATF1`, `EWSR1-CREB1`, `EWSR1-DDIT3`, `EWSR1-ETV1`.
  - **NEGATIVE CONTROL** — the four alphabetically-first peaksets sharing **neither** partner with each other: `ACTB-GLI1`, `ARFGEF2-HNF4A`, `CCDC6-RET`, `EPC1-PHF1`. Expected null.

**Pre-declared decision rule:**
- **A: COARSELY COHERENT** iff the TEST group's combined *D* is in the **lowest 5%** of the exact null (one-sided p ≤ 0.05).
- **B: LOCATIONALLY COHERENT** iff mean pairwise Jaccard is in the **highest 5%** (one-sided p ≤ 0.05); **UNDECIDED** iff the median within-group comparison window holds < 5 intervals on the smaller side for more than half the pairs.
- **Confound gate for B, declared before it was run:** two peaksets of similar *density* have systematically more opportunity to share exact coordinates in a common window, because Jaccard is penalised by union-size asymmetry. The TEST group is density-similar, so B must be recomputed **conditional on density**: restrict the null to subsets whose *D*(log₁₀ n_intervals) is ≤ the TEST group's. **Survives iff conditional p ≤ 0.05.**

---

## Result

### Analysis A — coarse shape: NOT coherent, and the width feature is degenerate

| Group | Row type | *D* on log₁₀ n_intervals | p (low tail, exact) | *D* combined 2-D | p (low tail, exact) |
|---|---|---|---|---|---|
| **NR4A3 quartet** (TEST) | **PRIMARY** | 0.4754 | **0.1419** | 0.6150 | **0.1419** |
| EWSR1-* quartet (positive analogue) | PRIMARY | 1.2725 | 0.8753 | 1.6460 | 0.8753 |
| No-shared-partner quartet (negative control) | PRIMARY | 1.5580 | 0.9917 | 2.0153 | 0.9917 |
| Exact null, all 35,960 subsets | — | mean 0.8940 | — | mean 1.1563 | — |

**Verdict A, emitted by the script: `NOT COARSELY COHERENT` (p = 0.1419).** The NR4A3 quartet is more count-similar than a typical quartet (0.475 vs null mean 0.894) but **does not clear the pre-declared 5% threshold**. Units: *D* is a dimensionless mean absolute difference in log₁₀ peak count; uncertainty is the exact permutation distribution over all 35,960 four-subsets of these same 32 peaksets, and extends no further.

**An important null finding about the instrument itself. `median_width` is 500 bp for all 32 peaksets — standard deviation exactly 0.** The authors' marker intervals are fixed-width 500 bp windows. **The width feature carries literally zero information**, so the "coarse" analysis my dispatch specified collapses to peak *count* alone, on 32 peaksets. That is a much thinner instrument than the dispatch assumed, and I report it as the reason Analysis A is not the load-bearing result. (`n_intervals` across the 32: min 22, median 1,651, max 13,692.)

### Analysis B — location: coherent, and it survives density matching

Retained substrate: median 26 complete chr1 intervals per peakset (min 4, max 28); every interval exactly 500 bp; all prefixes ascending-sorted.

| Group | Row type | mean pairwise Jaccard | p (high tail, exact, unconditional) | median window depth (smaller side) |
|---|---|---|---|---|
| **NR4A3 quartet** (TEST) | **PRIMARY** | **0.1994** | **0.0013** | 8.0 intervals |
| EWSR1-* quartet (shared 5′ partner) | **PRIMARY** | 0.0952 | 0.0244 | 4.5 intervals |
| No-shared-partner quartet (negative control) | **PRIMARY** | 0.0000 | 1.0000 | 0.0 intervals |
| Exact null, all 35,960 subsets | — | mean 0.0160 | — | — |

Background scale: over all 496 unordered peakset pairs, 376 admit a non-degenerate window; their Jaccard is mean 0.0159, **median 0.0000**, max 0.4118, with only **65/376 pairs sharing any interval at all**. So a shared coordinate is rare in this panel, which is what makes the quartet's 6/6 non-zero pairs notable.

Per-pair detail inside the NR4A3 quartet (**PRIMARY**):

| Pair | Jaccard | window | \|A\| | \|B\| | shared |
|---|---|---|---|---|---|
| EWSR1-NR4A3 · TCF12-NR4A3 | 0.3750 | chr1:0–53,717,864 | 18 | 26 | 12 |
| TAF15-NR4A3 · TFG-NR4A3 | 0.2414 | chr1:0–11,733,791 | 27 | 9 | 7 |
| EWSR1-NR4A3 · TFG-NR4A3 | 0.1786 | chr1:0–31,958,072 | 7 | 26 | 5 |
| TCF12-NR4A3 · TFG-NR4A3 | 0.1515 | chr1:0–31,958,072 | 12 | 26 | 5 |
| TAF15-NR4A3 · TCF12-NR4A3 | 0.1429 | chr1:0–11,733,791 | 27 | 5 | 4 |
| EWSR1-NR4A3 · TAF15-NR4A3 | 0.1071 | chr1:0–11,733,791 | 4 | 27 | 3 |

**Density-matched conditional test (the pre-declared confound gate):** restricting the null to the **5,102** subsets at least as density-matched as the TEST group (*D*(log₁₀ n) ≤ 0.4754) raises the null mean from 0.0160 to 0.0273 — confirming the confound is real and non-trivial — but the TEST group's 0.1994 still sits at **conditional p = 0.0010**. **Verdict, emitted by the script: `SURVIVES density matching`.**

**Verdict B, emitted by the script: `LOCATIONALLY COHERENT` (p = 0.0013 unconditional, p = 0.0010 density-matched, median window depth 8.0 ≥ the pre-declared floor of 5).**

### What this does and does not answer

**ASSOCIATION — the ordering is the interesting part, and it is the correct strength of claim.** Shared-3′-NR4A3 quartet (J = 0.199) > shared-5′-EWSR1 quartet (J = 0.095) > unrelated quartet (J = 0.000, exactly the null expectation). Within one chr1 prefix window, in one cell background, the four NR4A3 fusions land on the **same 500 bp windows** more than four random fusions do, and more than four fusions sharing a 5′ partner do. That is **consistent with** the shared NR4A3 DNA-binding moiety, not the 5′ partner, setting where these fusions go.

**It is not a decision, and the question remains UNDECIDED as posed.** The measured quantity is 0.199 — the four fusions share roughly a fifth of their peaks in the tested window, not most of them. On this evidence the honest reading is **partial convergence**, which is neither "one disease" nor "four diseases", and it is exactly the regime in which the Brenca partner-dependence result (`SEMA3C` recognition impaired by `TAF15-NR4A3`) and a shared-moiety model can both be true. I make no disease-identity claim.

**PREDICTION rows: none.** This report contains no model output, no extrapolation and no projection.

**Also established, independent of the verdicts:**

1. **PRIMARY.** Genome-derived peak *coordinates* for all four NR4A3 fusions **are partially retained in this repository**, in `gse243553-eno3-overlap-supplement.json`. W20 recorded this question as UNDECIDED-because-data-inaccessible on the basis of the summary file alone. That status is now **partially superseded**: the coarse route was not the only one available.
2. **PRIMARY.** The authors' marker intervals are **fixed 500 bp windows**, so `median_width` is a constant across the panel and cannot discriminate anything. Any future analysis planning to use it should not.
3. **PRIMARY.** `peakset_inventory`'s 128 entries are **32 real peaksets** plus 64 AppleDouble forks and 32 non-interval tables. A count of "128 fusions" taken from that field would be wrong by a factor of four.
4. **UNKNOWN, preserved from the source.** The wild-type `NR4A3` and reciprocal `NR4A3-EWSR1` controls have **no marker BED in the supplement at all**, and `controls.⚠_how_to_read_a_missing_file` states the correct reading: *"the fusion arms have interval sets and the two controls have none"*, **not** "the controls were tested here and came back empty". I could not include them, and I assert no zero for them.

---

## Limitations

- **THE CENTRAL LIMITATION — the window is a sliver of one chromosome.** Every location comparison happens inside `chr1:0` to at most 53.7 Mb, and for three of the six pairs inside `chr1:0–11.7 Mb`. That is roughly **0.4% of the genome** at the median. The retained data is a byte-truncated prefix, so the tested region is not a random sample of the genome — it is **the proximal end of chr1, chosen by nothing except sort order**. Whether the quartet's convergence holds genome-wide is **UNKNOWN**. This result raises the prior; it does not settle the question.
- **Window depths are small: 4–27 intervals per side, median 8 on the smaller side.** With that many intervals a single shared or unshared window moves the Jaccard by several points. The exact null protects the p-value against distributional error but not against the fact that the effect rests on 36 shared intervals in total.
- **Similarity in peak count and width is not similarity in peak location.** Analysis A speaks only to shape and it did **not** reach its threshold; the coherence claim rests entirely on Analysis B, which is location. These must not be blurred, and A's near-miss (p = 0.14) must not be reported as support.
- **Different peaksets have different prefix depths, so the window is pair-dependent.** A pair with one dense member gets a narrow window. This is handled exactly rather than approximately — inside each window both sets are complete — but it means the six pairwise Jaccards are **not measured over a common region** and should not be averaged as if they were interchangeable estimates of one quantity. The group statistic is a mean over heterogeneous windows, and its null was computed the same way, which is what makes the comparison fair.
- **The density confound is real.** The unconditional null understates the expected Jaccard for a density-matched group (0.016 vs 0.027). The conditional test is the one to quote.
- **HEK293T is not EMC.** All 128 fusions were expressed in one embryonic-kidney background. That is precisely what makes the panel internally controlled, and precisely why nothing here transfers to chondroid tissue, to a patient tumour, or to disease behaviour. A fusion's accessible chromatin in HEK293T is not its cistrome in EMC.
- **These are the authors' marker calls, not peaks this repository called**, at a threshold and with a differential-accessibility definition I did not set and cannot re-tune. A peakset's size reflects that pipeline as much as the fusion's biology.
- **Group membership drives Analysis A's alternatives, not its null.** With only 32 peaksets, the exact null is over 35,960 subsets but the *panel* is small; a different fusion library could give a different null.
- **Nothing here bears on efficacy, safety, selectivity, therapeutic window, potency, dosing or clinical readiness** of any agent, target or gene, and no such quantity was computed. No reagent was designed. There is no wet lab.
- **W20's transfer limits carry forward unchanged**, including that `EWSR1-` FISH status is not fusion-negative and that its `TAF15` null may have had no power by construction.

---

## Stop condition

**Condition set in advance:** either an executed partner-interchangeability analysis on retained data with a pre-declared rule and stated limits, or a precise statement that even the coarse route is unsupported, naming exactly what is missing.

**MET, by the first branch, and by a stronger route than the dispatch anticipated.** Two analyses ran to exit 0 against rules fixed before execution, with a pre-specified negative control that behaved as a control should (J = 0.0000, p = 1.0000) and a pre-declared confound gate that the result survived. The coarse route was executed and **did not clear** its threshold; the location route was executed — enabled by coordinate prefixes retained in a file W20 had not examined — and **did**, at p = 0.0010 density-matched.

**Still missing, and named exactly:** the genome-wide interval sets, GSE243553 supplementary `MOESM3_ESM.zip`, members `Supp_Data_1_new/{EWSR1,TAF15,TCF12,TFG}-NR4A3_markers.bed` (sizes recorded in the retained `members` list; e.g. `EWSR1-NFATC2_markers.bed` 17,345 B, `TPR-NTRK1_markers.bed` 3,899 B). Behind a **403 CONNECT policy denial** from this container, which I did not test, retry or route around. The wild-type `NR4A3` and reciprocal `NR4A3-EWSR1` controls have **no such file to fetch**.

---

## Validation evidence

**RUN — command 1** (budget gate, before analysis):
```
df -h / | tail -1
```
→ `/dev/vda  252G  12G used  27G avail  30%` — ≥10 GiB satisfied. Re-checked at end: identical. Nothing downloaded.

**RUN — command 2** (`/tmp/claude-0/w20b/partner_interchange.py`, full source in the next section):
```
cd /tmp/claude-0/w20b && df -h / | tail -1 && python3 --version && python3 partner_interchange.py; echo "EXIT=$?"
```
Environment: `Python 3.11.15`, stdlib only. Verbatim output:
```
entries in peakset_inventory : 128
REAL BED peaksets            : 32
excluded __MACOSX forks      : 64
excluded Supp_Data_2 tables  : 32

TEST  (shared 3' NR4A3): ['EWSR1-NR4A3', 'TAF15-NR4A3', 'TCF12-NR4A3', 'TFG-NR4A3']
POS-ANALOGUE (shared 5' EWSR1): ['EWSR1-ATF1', 'EWSR1-CREB1', 'EWSR1-DDIT3', 'EWSR1-ETV1']
NEG-CONTROL (no shared partner): ['ACTB-GLI1', 'ARFGEF2-HNF4A', 'CCDC6-RET', 'EPC1-PHF1']

median_width across 32 peaksets: sd = 0.0000  (values: [500])
n_intervals across 32: min 22  median 1651  max 13692

exact null subsets enumerated: 35960

--- ANALYSIS A : coarse shape (count + width). NOT location. ---
group                D_logN      p_low     D_comb      p_low
NR4A3                0.4754     0.1419     0.6150     0.1419
POS-ANALOGUE         1.2725     0.8753     1.6460     0.8753
NEG-CONTROL          1.5580     0.9917     2.0153     0.9917
null mean D_logN 0.8940 ; null mean D_comb 1.1563

--- ANALYSIS B : chr1-prefix location overlap (exact within window) ---
retained complete chr1 intervals per peakset: min 4 median 26 max 28
distinct interval widths in retained prefixes: [500]
all retained prefixes ascending-sorted: True
  EWSR1-NR4A3    n=26  chr1 span 9885968 - 59179217
  TAF15-NR4A3    n=27  chr1 span 2310329 - 11733791
  TCF12-NR4A3    n=26  chr1 span 9796550 - 53717864
  TFG-NR4A3      n=26  chr1 span 3803820 - 31958072

group              meanJacc     p_high  medWinN(min side)
NR4A3                0.1994     0.0013            8.0
POS-ANALOGUE         0.0952     0.0244            4.5
NEG-CONTROL          0.0000     1.0000            0.0
null mean meanJacc 0.0160 ; n null subsets with Jacc>0: 20110/35960

PRE-SPECIFIED VERDICT A (shape) : NOT COARSELY COHERENT   p=0.1419
PRE-SPECIFIED VERDICT B (location): LOCATIONALLY COHERENT   p=0.0013  medianWindowN=8.0
EXIT=0
```

**RUN — command 3** (`/tmp/claude-0/w20b/density_matched.py`, the pre-declared confound gate):
```
cd /tmp/claude-0/w20b && python3 density_matched.py; echo "EXIT=$?"; date -u
```
Verbatim output:
```
all 496 pairwise Jaccard: mean 0.0159  median 0.0000  max 0.4118  n_nonzero 65/376
observed NR4A3 meanJacc 0.1994   D_logN 0.4754
unconditional null n=35960  p_high=0.0013
density-matched null n=5102 (D_logN<=0.4754)  mean 0.0273  p_high=0.0010
pairwise Jaccard inside NR4A3 quartet:
  EWSR1-NR4A3  TAF15-NR4A3  J=0.1071  window chr1:0-11733791  |A|=4 |B|=27 shared=3
  EWSR1-NR4A3  TCF12-NR4A3  J=0.3750  window chr1:0-53717864  |A|=18 |B|=26 shared=12
  EWSR1-NR4A3  TFG-NR4A3    J=0.1786  window chr1:0-31958072  |A|=7 |B|=26 shared=5
  TAF15-NR4A3  TCF12-NR4A3  J=0.1429  window chr1:0-11733791  |A|=27 |B|=5 shared=4
  TAF15-NR4A3  TFG-NR4A3    J=0.2414  window chr1:0-11733791  |A|=27 |B|=9 shared=7
  TCF12-NR4A3  TFG-NR4A3    J=0.1515  window chr1:0-31958072  |A|=12 |B|=26 shared=5

PRE-SPECIFIED CONDITIONAL VERDICT: SURVIVES density matching  p_cond=0.0010
EXIT=0
Tue Sep  8 02:08:20 UTC 2026
```

**RUN — command 4** (write-isolation and provenance check):
```
cd /home/user/Rare-cancers && git rev-parse HEAD && git status --porcelain | head && df -h / | tail -1 && date -u
```
→ `92abbcb905cacf07f14b238db50d1b98f6590374`; the only porcelain line is `?? research/autonomy/opus-capacity-campaign-20260908/` (the coordinator's pre-existing untracked campaign directory); `27G avail`; `Tue Sep  8 02:08:48 UTC 2026`. Exit 0.

**Sanity check performed before writing this report.** (a) Re-read the lane ask and confirmed both required elements — an executed analysis with a pre-declared rule, and precise statements of what it cannot show. (b) **Cross-file join validation:** `gse243553-eno3-overlap.json` records `median_width = 500` for all 32 peaksets, and every interval I parsed from the *separately generated* `-supplement.json` byte prefixes is exactly 500 bp wide — two independently produced artifacts agreeing, which is a real check that I am reading the same peaksets in both and not mis-joining them. (c) Verified all 32 prefixes are ascending-sorted, which is the precondition that makes the windowed Jaccard exact rather than approximate; the script asserts and prints this. (d) Confirmed both scripts exited 0 and all four verdict strings are printed by the scripts, not typed by me. (e) Confirmed no network call was made in this session and the tree is unmodified.

**PROPOSED (NOT RUN):**
- The genome-wide version of Analysis B over the full `*_markers.bed` files. No code was written for it; the input is 403-denied.
- Any re-run or re-derivation of W20's `TAF15` expression test. Not touched.
- `scripts/preflight.sh` — **not run**, per COMMON-BRIEF §1; my dispatch did not instruct it and I wrote nothing to the tree for it to gate.

---

## Code (returned inline, not written to the tree)

`/tmp/claude-0/w20b/partner_interchange.py`

```python
#!/usr/bin/env python3
"""
W20b - partner-interchangeability of the four NR4A3 fusions in the GSE243553
HEK293T fusion-oncoprotein panel, on RETAINED data only. No network.

INPUTS (read-only, committed at frozen commit 92abbcb9):
  research/modalities/gse243553-eno3-overlap.json
      -> peakset_inventory: per-peakset n_intervals, chroms, median_width
  research/modalities/gse243553-eno3-overlap-supplement.json
      -> contents['SPRINGER::3::zip']['first_bytes']: a <=600-byte PREFIX of each
         markers.bed, i.e. the first ~24 chr1 intervals in ascending order.

TWO ANALYSES.

  A (COARSE, shape only).  Statistic D = mean pairwise |difference| over a group,
     computed on (i) log10(n_intervals) and (ii) median_width, and (iii) a combined
     2-D Euclidean distance after z-standardising both features over the 32 real
     BED peaksets.  Similarity in peak COUNT and WIDTH is NOT similarity in peak
     LOCATION.  This analysis cannot speak to location at all.

  B (LOCATION, chr1 prefix).  For each ordered pair, take the retained complete
     intervals of both, restrict both to [0, W] with W = min(last retained end of
     A, last retained end of B) on chr1.  Inside that window each retained set is
     COMPLETE because the deposited BEDs are coordinate-sorted, so the Jaccard
     index over that window is exact for that window.  Statistic = mean pairwise
     Jaccard within a group.

PRE-DECLARED DECISION RULE (fixed before execution, printed by the script):
  Null = EXACT enumeration of all C(32,4) = 35960 four-member subsets of the 32
  real BED peaksets.
  A: NR4A3 quartet is "COARSELY COHERENT" iff its D is in the LOWEST 5% of the
     exact null (one-sided p <= 0.05) on the combined 2-D statistic.
  B: NR4A3 quartet is "LOCATIONALLY COHERENT" iff its mean pairwise Jaccard is in
     the HIGHEST 5% of the exact null (one-sided p <= 0.05).
  UNDECIDED for B iff the median pairwise comparison window contains < 5 intervals
     in either member of the pair, for more than half the within-group pairs.
  Verdict strings are emitted by the script, not typed by the author.

CONTROL GROUPS, pre-specified, no post-hoc selection:
  POS-ANALOGUE  : four alphabetically-first EWSR1-* peaksets that are NOT NR4A3
                  (shared 5' partner instead of shared 3' moiety).
  NEG-CONTROL   : four alphabetically-first peaksets sharing NEITHER partner with
                  each other.
"""
import json, itertools, math, statistics, re

BASE = "/home/user/Rare-cancers/research/modalities/"
ov  = json.load(open(BASE + "gse243553-eno3-overlap.json"))
sup = json.load(open(BASE + "gse243553-eno3-overlap-supplement.json"))

inv = ov["peakset_inventory"]
# real BED peaksets only: Supp_Data_1_new/*.bed, excluding __MACOSX resource forks
real = {k: v for k, v in inv.items()
        if k.startswith("Supp_Data_1_new/") and k.endswith("_markers.bed")}
names = sorted(real)
short = {k: k.split("/")[1].replace("_markers.bed", "") for k in names}
print("entries in peakset_inventory :", len(inv))
print("REAL BED peaksets            :", len(names))
print("excluded __MACOSX forks      :", sum(1 for k in inv if k.startswith("__MACOSX")))
print("excluded Supp_Data_2 tables  :", sum(1 for k in inv if k.startswith("Supp_Data_2_new/")))
print()

NR4A3 = [k for k in names if k.endswith("NR4A3_markers.bed")]
assert len(NR4A3) == 4, NR4A3
ews = [k for k in names if short[k].startswith("EWSR1-") and "NR4A3" not in k]
POSA = sorted(ews)[:4]
used = set()
NEG = []
for k in names:
    a, b = short[k].split("-", 1)
    if a in used or b in used:
        continue
    NEG.append(k); used |= {a, b}
    if len(NEG) == 4:
        break
print("TEST  (shared 3' NR4A3):", [short[k] for k in NR4A3])
print("POS-ANALOGUE (shared 5' EWSR1):", [short[k] for k in POSA])
print("NEG-CONTROL (no shared partner):", [short[k] for k in NEG])
print()

# ---------------- A : coarse shape ----------------
n_int = {k: real[k]["n_intervals"] for k in names}
med_w = {k: real[k]["median_width"] for k in names}
f1 = {k: math.log10(n_int[k]) for k in names}
f2 = {k: float(med_w[k]) for k in names}
def zs(d):
    v = list(d.values()); m = statistics.mean(v); s = statistics.pstdev(v)
    return {k: (0.0 if s == 0 else (x - m) / s) for k, x in d.items()}, s
z1, s1 = zs(f1); z2, s2 = zs(f2)
print("median_width across 32 peaksets: sd = %.4f  (values: %s)"
      % (s2, sorted(set(med_w.values()))))
print("n_intervals across 32: min %d  median %d  max %d"
      % (min(n_int.values()), int(statistics.median(n_int.values())), max(n_int.values())))
print()

def D_feat(group, f):
    p = list(itertools.combinations(group, 2))
    return statistics.mean(abs(f[a] - f[b]) for a, b in p)
def D_comb(group):
    p = list(itertools.combinations(group, 2))
    return statistics.mean(math.dist((z1[a], z2[a]), (z1[b], z2[b])) for a, b in p)

subsets = list(itertools.combinations(names, 4))
print("exact null subsets enumerated:", len(subsets))

def pctile_low(stat_fn, group):
    obs = stat_fn(group)
    nulls = [stat_fn(s) for s in subsets]
    le = sum(1 for x in nulls if x <= obs)
    return obs, le / len(nulls), statistics.mean(nulls)

print()
print("--- ANALYSIS A : coarse shape (count + width). NOT location. ---")
print("%-16s %10s %10s %10s %10s" % ("group", "D_logN", "p_low", "D_comb", "p_low"))
resA = {}
for lab, g in (("NR4A3", NR4A3), ("POS-ANALOGUE", POSA), ("NEG-CONTROL", NEG)):
    o1, p1, m1 = pctile_low(lambda s: D_feat(s, f1), g)
    o3, p3, m3 = pctile_low(D_comb, g)
    resA[lab] = (o1, p1, o3, p3)
    print("%-16s %10.4f %10.4f %10.4f %10.4f" % (lab, o1, p1, o3, p3))
print("null mean D_logN %.4f ; null mean D_comb %.4f" % (m1, m3))

# ---------------- B : chr1 prefix location ----------------
fb = sup["contents"]["SPRINGER::3::zip"]["first_bytes"]
def parse_prefix(key):
    """Complete BED lines only; drop the final truncated line."""
    txt = fb[key]
    lines = txt.split("\n")
    if not txt.endswith("\n"):
        lines = lines[:-1]           # last line is truncated by the byte cap
    out = []
    for ln in lines:
        p = ln.split("\t")
        if len(p) < 3: continue
        if not re.fullmatch(r"\d+", p[1]) or not re.fullmatch(r"\d+", p[2]): continue
        out.append((p[0], int(p[1]), int(p[2])))
    return out

pre = {}
for k in names:
    iv = parse_prefix(k)
    iv = [x for x in iv if x[0] == "chr1"]     # every prefix is chr1-sorted
    pre[k] = iv
widths = sorted({e - s for k in names for _, s, e in pre[k]})
print()
print("--- ANALYSIS B : chr1-prefix location overlap (exact within window) ---")
print("retained complete chr1 intervals per peakset: min %d median %d max %d"
      % (min(len(v) for v in pre.values()),
         int(statistics.median([len(v) for v in pre.values()])),
         max(len(v) for v in pre.values())))
print("distinct interval widths in retained prefixes:", widths)
sorted_ok = all(all(pre[k][i][1] <= pre[k][i+1][1] for i in range(len(pre[k])-1)) for k in names)
print("all retained prefixes ascending-sorted:", sorted_ok)
for k in NR4A3:
    print("  %-14s n=%2d  chr1 span %d - %d" % (short[k], len(pre[k]), pre[k][0][1], pre[k][-1][2]))

def jac(a, b):
    A, B = pre[a], pre[b]
    if not A or not B: return None, 0, 0
    W = min(A[-1][2], B[-1][2])
    SA = {(s, e) for _, s, e in A if e <= W}
    SB = {(s, e) for _, s, e in B if e <= W}
    if not SA or not SB: return None, len(SA), len(SB)
    return len(SA & SB) / len(SA | SB), len(SA), len(SB)

def meanJ(group):
    vs = [jac(a, b)[0] for a, b in itertools.combinations(group, 2)]
    vs = [v for v in vs if v is not None]
    return statistics.mean(vs) if vs else 0.0

nullJ = [meanJ(s) for s in subsets]
print()
print("%-16s %10s %10s %14s" % ("group", "meanJacc", "p_high", "medWinN(min side)"))
for lab, g in (("NR4A3", NR4A3), ("POS-ANALOGUE", POSA), ("NEG-CONTROL", NEG)):
    o = meanJ(g)
    ge = sum(1 for x in nullJ if x >= o) / len(nullJ)
    wins = [min(jac(a, b)[1], jac(a, b)[2]) for a, b in itertools.combinations(g, 2)]
    print("%-16s %10.4f %10.4f %14.1f" % (lab, o, ge, statistics.median(wins)))
print("null mean meanJacc %.4f ; n null subsets with Jacc>0: %d/%d"
      % (statistics.mean(nullJ), sum(1 for x in nullJ if x > 0), len(nullJ)))
medwin = statistics.median([min(jac(a, b)[1], jac(a, b)[2])
                            for a, b in itertools.combinations(NR4A3, 2)])

# ---------------- verdicts ----------------
print()
_, _, dc, pA = resA["NR4A3"]
vA = "COARSELY COHERENT" if pA <= 0.05 else "NOT COARSELY COHERENT"
oJ = meanJ(NR4A3); pB = sum(1 for x in nullJ if x >= oJ) / len(nullJ)
if medwin < 5:
    vB = "UNDECIDED (comparison window too small)"
else:
    vB = "LOCATIONALLY COHERENT" if pB <= 0.05 else "NOT LOCATIONALLY COHERENT"
print("PRE-SPECIFIED VERDICT A (shape) :", vA, "  p=%.4f" % pA)
print("PRE-SPECIFIED VERDICT B (location):", vB, "  p=%.4f  medianWindowN=%.1f" % (pB, medwin))
```

`/tmp/claude-0/w20b/density_matched.py`

```python
#!/usr/bin/env python3
"""
W20b addendum. CONFOUND: two peaksets of similar density have systematically more
opportunity to share exact 500-bp coordinates inside a common chr1 window than a
dense/sparse pair, because Jaccard is penalised by union-size asymmetry. The NR4A3
quartet IS density-similar (D_logN 0.475 vs null mean 0.894). So the Analysis-B
p-value must be recomputed CONDITIONAL on density similarity.

PRE-DECLARED (fixed before this run): restrict the exact C(32,4) null to those
subsets whose D_logN is <= the NR4A3 quartet's D_logN, i.e. subsets at least as
density-matched as the test group, and recompute the one-sided high-tail p.
Rule: location coherence SURVIVES iff conditional p <= 0.05.
Also reported: a permutation of the SAME question that ignores identity entirely
(mean pairwise Jaccard of all 496 pairs) for scale.
"""
import json, itertools, math, statistics, re
BASE="/home/user/Rare-cancers/research/modalities/"
ov=json.load(open(BASE+"gse243553-eno3-overlap.json"))
sup=json.load(open(BASE+"gse243553-eno3-overlap-supplement.json"))
inv=ov["peakset_inventory"]
real={k:v for k,v in inv.items() if k.startswith("Supp_Data_1_new/") and k.endswith("_markers.bed")}
names=sorted(real); short={k:k.split("/")[1].replace("_markers.bed","") for k in names}
f1={k:math.log10(real[k]["n_intervals"]) for k in names}
NR4A3=[k for k in names if k.endswith("NR4A3_markers.bed")]
fb=sup["contents"]["SPRINGER::3::zip"]["first_bytes"]
def parse(k):
    t=fb[k]; L=t.split("\n")
    if not t.endswith("\n"): L=L[:-1]
    o=[]
    for ln in L:
        p=ln.split("\t")
        if len(p)>=3 and re.fullmatch(r"\d+",p[1]) and re.fullmatch(r"\d+",p[2]) and p[0]=="chr1":
            o.append((int(p[1]),int(p[2])))
    return o
pre={k:parse(k) for k in names}
def jac(a,b):
    A,B=pre[a],pre[b]
    if not A or not B: return None
    W=min(A[-1][1],B[-1][1])
    SA={x for x in A if x[1]<=W}; SB={x for x in B if x[1]<=W}
    if not SA or not SB: return None
    return len(SA&SB)/len(SA|SB)
J={}
for a,b in itertools.combinations(names,2):
    J[(a,b)]=jac(a,b)
def meanJ(g):
    v=[J[(a,b)] if (a,b) in J else J[(b,a)] for a,b in itertools.combinations(sorted(g),2)]
    v=[x for x in v if x is not None]
    return statistics.mean(v) if v else 0.0
def D(g):
    return statistics.mean(abs(f1[a]-f1[b]) for a,b in itertools.combinations(g,2))
subs=list(itertools.combinations(names,4))
obsJ=meanJ(NR4A3); obsD=D(NR4A3)
allp=[x for x in J.values() if x is not None]
print("all 496 pairwise Jaccard: mean %.4f  median %.4f  max %.4f  n_nonzero %d/%d"
      %(statistics.mean(allp),statistics.median(allp),max(allp),
        sum(1 for x in allp if x>0),len(allp)))
print("observed NR4A3 meanJacc %.4f   D_logN %.4f"%(obsJ,obsD))
uncond=[meanJ(s) for s in subs]
p_un=sum(1 for x in uncond if x>=obsJ)/len(uncond)
matched=[s for s in subs if D(s)<=obsD]
mj=[meanJ(s) for s in matched]
p_cond=sum(1 for x in mj if x>=obsJ)/len(mj)
print("unconditional null n=%d  p_high=%.4f"%(len(uncond),p_un))
print("density-matched null n=%d (D_logN<=%.4f)  mean %.4f  p_high=%.4f"
      %(len(matched),obsD,statistics.mean(mj),p_cond))
print("pairwise Jaccard inside NR4A3 quartet:")
for a,b in itertools.combinations(NR4A3,2):
    v=J[(a,b)] if (a,b) in J else J[(b,a)]
    A,B=pre[a],pre[b]; W=min(A[-1][1],B[-1][1])
    SA={x for x in A if x[1]<=W}; SB={x for x in B if x[1]<=W}
    print("  %-12s %-12s J=%.4f  window chr1:0-%d  |A|=%d |B|=%d shared=%d"
          %(short[a],short[b],v,W,len(SA),len(SB),len(SA&SB)))
print()
print("PRE-SPECIFIED CONDITIONAL VERDICT:",
      "SURVIVES density matching" if p_cond<=0.05 else "DOES NOT SURVIVE density matching",
      " p_cond=%.4f"%p_cond)
```

---

## Tool-call and wall-clock count actually used

**Tool calls: 10.** **Wall clock: approximately 4 minutes of execution** (first `date -u` 02:05:01 UTC, final 02:08:48 UTC) plus report composition. Well inside the ~40-call / ~40-minute self-observed target. No compute is left running; nothing is in flight.

---

## Next concrete action

**One successor task for this lane.**

**Fetch the six named `Supp_Data_1_new/*_markers.bed` files via the Actions-runner escape hatch and re-run Analysis B genome-wide, unchanged.** The script above is complete and its only assumption about the input is that BED lines are coordinate-sorted — swapping the 600-byte prefixes for full files requires changing one loader function and nothing else, so the analysis is pre-registered by construction and the genome-wide result cannot be tuned after the fact. This is the single change that converts a 0.4%-of-chr1 association at p = 0.0010 into a decidable answer about whether EMC's four fusion variants are one disease at the chromatin level. Feasibility, honestly: the container cannot fetch them (403 CONNECT at the agent proxy, recorded as a standing boundary and not retried here), the files are small (3.9–17.3 KB each, sizes read from the retained ZIP member list), and the runner has egress. Two caveats must travel with it: the wild-type `NR4A3` and reciprocal `NR4A3-EWSR1` controls **have no file to fetch** and their absence is not a measured zero; and the whole panel is HEK293T, so a genome-wide answer is still an answer about fusion protein behaviour in one heterologous background, not about EMC tissue.

*Secondary, if the above is out of budget:* extend Analysis B to the ~26 non-NR4A3 peaksets pairwise to ask a different retained-data question — does the panel as a whole cluster by 5′ partner, by 3′ partner, or by neither? The retained prefixes support it today, at the same severe window limitation.

result: Lane 20's named successor executed — using coordinate prefixes retained in `gse243553-eno3-overlap-supplement.json` that the prior worker had not found, the four NR4A3 fusions share peak *locations* in the GSE243553 HEK293T panel far more than chance (mean Jaccard 0.199 vs null 0.016; exact one-sided p = 0.0013, p = 0.0010 after a pre-declared density-matched null; shared-5′-EWSR1 control 0.095, unrelated control 0.000), while the coarse count/width route did NOT clear its threshold (p = 0.14, and `median_width` is a constant 500 bp carrying zero information) — the location signal is confined to ≤53.7 Mb of chr1 so the "one disease" question stays UNDECIDED with a raised prior, and W20's TAF15 refutation plus its power caveat are preserved intact.
