> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).
> This is the scientific owner's commissioned one-slot candidate-merit check. It is advice, not admission.

---

## Worker

**Worker ID:** W25 · candidate-merit check on the GSE243553 partner-binding development prospect · OPUS-CAPACITY-CAMPAIGN-20260908.

**Model evidence — SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I self-report as Claude Opus 5 (`claude-opus-5`). No environment variable in this container names a served model. The coordinator must extract the actual per-child runtime model from the transcript.

`date -u` at start: `Tue Sep  8 02:55:49 UTC 2026`. `date -u` at end: `Tue Sep  8 03:02:25 UTC 2026`.

Literal `env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'` (start run; proxy-plumbing lines `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS` matched the grep and are verbatim in the tool log — elided here, they contain nothing model-relevant):

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

**Repository anchors, actually read.** `git rev-parse HEAD` at start: **`4d950cf036294627b7ae67dfb306cc1875d702ac`**; at end: **`fc6ed92999c26f52c47668d1c126321a5f51d1b5`** (the coordinator committed during my run; my two input JSONs are unchanged between them — they are not in either commit's diff). `git status --porcelain` at start: `M research/autonomy/opus-capacity-campaign-20260908/WAVE-LOG.md` (the coordinator's file, not mine). At end: **empty**. I wrote nothing into `/home/user/Rare-cancers`; all execution was under `/tmp/claude-0/w25/` (two files, `audit.py`, `strat.py`).

---

## Verdict up front

**The prospect fails the merit check on novelty, not on statistics.** Two separate retained repository documents record that the primary publication *already reports the finding these four reports rediscovered*. Separately, the "genome-wide data is behind a 403" premise that W20b, W19c, W19d, W19e and W23 all built on is **false at the repository level**: the full Supplementary Data 1 ZIP and all 32 genome-wide BEDs were retrieved and committed on 2026-09-07 and are tracked at the corpus's base commit. The statistics I audited are, by contrast, sounder than I expected — the effect survived both confound attacks I could construct.

My recommendation is that the owner **decline admission** of this as a paper, and that the coordinator issue focused corrections to five reports.

---

## Question

Does the GSE243553 partner-binding line (W20b → W19c → W19d → W19e, ranked #1 by W23) have (a) substantive novelty beyond `doi:10.1038/s41587-024-02347-4` and beyond every retained GSE243553 analysis, and (b) statistical validity on its own terms, sufficient to admit it as a paper?

---

## Prior-work check — searched scope stated explicitly

**Root: `/tmp/claude-0/frozen-corpus/extracted/corpus/` (the corrected path), 5,996 files, verified by `find … -type f | wc -l` → `5996`.** Every corpus command below was rooted there. I additionally read the live checkout at `/home/user/Rare-cancers` and the metadata map at `/tmp/claude-0/frozen-corpus/extracted/metadata/tracked-file-map.txt`.

| Command (root abbreviated `$C`) | Hits |
|---|---|
| `grep -rl -i "GSE243553" $C` | **39 files** |
| `grep -rl -F "s41587-024-02347-4" $C` | **19 files** |
| `grep -rl -i "jaccard" $C` | 86 files (all unrelated: text-shingle dedup, gene-set Jaccards, docking/pocket work) |
| `grep -rl -i "peakset" $C` | 12 files |
| `grep -rl -i "markers.bed\|MOESM3_ESM" $C` | 13 files |
| `grep -rn -i "family clustering\|context-invariant" $C` | **2 files — the decisive hits** |
| `grep -i "gse243553" …/metadata/tracked-file-map.txt` | 7 tracked paths |
| `grep -c "nr4a3-program-source-2026-09-07" …/tracked-file-map.txt` | **60 tracked paths** |
| `git ls-files \| grep -i "nr4a3-program-source\|bed-members\|peaks.tsv\|paper.html"` (live tree) | **0** |

The prior workers' `git ls-files` searches were run **only against the live cloud checkout**, where `research/autonomy/nr4a3-program-source-2026-09-07/` does not exist. That directory is present in the frozen corpus and in the base-`93b` tracked map. This is the same false-absence shape the dispatch warned about, arrived at by a different route: searching the right tool at the wrong root.

Closed items confirmed not replayed: I made **no network request of any kind**. I did not probe, retry or seek another host for `MOESM3_ESM.zip` (recorded 403 CONNECT policy denial). No NR4A Perspective work, no therapeutic design, no frozen-paper edit, no clinical/registry/methylation/Brenca/Hofvander/GSE4303/GSE28866 material, no publication act, no external message. I hit no content-policy refusal.

---

## Method / inputs

| Input | Exact path | What I used |
|---|---|---|
| Coordinate prefixes | `/home/user/Rare-cancers/research/modalities/gse243553-eno3-overlap-supplement.json` | `contents['SPRINGER::3::zip']['first_bytes']` → ≤600-byte verbatim BED prefix per peakset |
| Peak counts | `/home/user/Rare-cancers/research/modalities/gse243553-eno3-overlap.json` | `peakset_inventory[*].n_intervals` (a **dict** of 128 keys, not a list — W19c/W19d/W19e's field access differs; same content) |
| Prior adjudication | `$C/research/autonomy/next-paper-2026-09-07/selection.md` L56–60 | verbatim quotation |
| Prior source packet | `$C/research/autonomy/nr4a3-program-source-2026-09-07/README.md` L53; `outputs/bed-members.tsv`; `source-manifest.jsonl`; `artifact-manifest.json` | verbatim quotation, per-BED hashes and counts, retrieval URLs and byte sizes |
| Tracked-file map, base `93b75888…` | `/tmp/claude-0/frozen-corpus/extracted/metadata/tracked-file-map.txt` | `git ls-tree -r -l` style rows: mode, blob sha, byte size, path |

Tools: Python 3.11.15, standard library only (`json`, `itertools`, `math`, `random`, `statistics`). No third-party package, no network, no GPU, no paid API, no spend.

---

## Result

### 1. The primary publication's full text is NOT supplied in the corpus — the exact missing source, named

**PRIMARY.** The publication is Frenkel M, Corban JE, Hujoel MLA, Morris Z, Raman S. *"Large-scale discovery of chromatin dysregulation induced by oncofusions and other protein-coding variants."* Nat Biotechnol 43(6):996–1010, 2025. PMID `39048711`, PMCID `PMC13105821`, DOI `10.1038/s41587-024-02347-4`. Source for these fields: `$C/research/manuscripts/fusion-output/lit-frenkel-2025-record.json`, which itself states it is *"NOT a verification of the paper's contents"*.

**The full text is not under `corpus/`.** `find $C -name "paper*.htm*" -o -name "*PMC13105821*"` → **zero hits**. The exact missing sources, by tracked path and byte size from the base-`93b` map:

- **`research/autonomy/nr4a3-program-source-2026-09-07/sources/paper.html` — 301,282 bytes** — described in the packet's own README as *"the complete accepted manuscript at https://pmc.ncbi.nlm.nih.gov/articles/PMC13105821/"*. **Tracked at `93b75888…`; absent from `corpus/`; absent from the live checkout.**
- **`…/sources/paper-nature.html` — 429,599 bytes** — described as *"publisher landing/abstract/reference content, not a complete article."*

What I have instead is **SECONDARY**: prose summaries of the paper's Methods and Results written by the 2026-09-07 source worker, which I quote below and do not treat as the paper's text. I did **not** treat metadata, the abstract, or `lit-frenkel-2025-record.json` as full text.

### 2. Novelty after subtraction — the finding is NIL for the headline claim

**PRIMARY, verbatim, from a tracked repository document dated 2026-09-07** — `$C/research/autonomy/next-paper-2026-09-07/selection.md` L56–58:

> *"Frenkel and colleagues already report **fusion-family clustering and context-invariant chromatin effects** in [PROD-ATAC](https://doi.org/10.1038/s41587-024-02347-4). Those ideas, generic gene-set scoring and mapping peaks to genes are not claimed as new methods."*

And the stop rule the same document sets for this exact line (L110–112):

> *"**Stop this proposed experiment if** … **primary prior art already reports the proposed contribution.**"*

**PRIMARY, verbatim, independently** — `$C/research/autonomy/nr4a3-program-source-2026-09-07/README.md` L53:

> *"The primary PROD-ATAC paper already reports **context-invariant chromatin effects, family clustering**, native-control comparisons and NR4A3 fusion gain-of-function chromatin behavior. **None is proposed as novelty here.**"*

Subtracting these from the four reports:

| Report headline | Already reported by the publication? |
|---|---|
| W19e: *same 3′ DBD **family** predicts peak location* (p < 2.1e-5) | **Yes** — "fusion-family clustering", stated twice in retained documents |
| W19c/W19d: *5′ partner does **not** predict location; the panel is 5′-context-insensitive* | **Yes** — "context-invariant chromatin effects" |
| W20b: *the four `*-NR4A3` fusions converge* (p = 0.0010 density-matched) | **Yes**, as the special case — "NR4A3 fusion gain-of-function chromatin behavior" plus family clustering |
| W20b/W19c: `median_width` is a constant 500 bp; `peakset_inventory`'s 128 entries are 32 real BEDs + 64 AppleDouble forks + 32 non-interval tables | **No** — genuinely new, and correct. This is a **data-hygiene correction**, not a scientific finding |

**What remains after subtraction is: (i) the 128→32 counting correction, (ii) the fixed-500 bp degeneracy of `median_width`, (iii) the demonstration that the chr1-prefix substrate reproduces a published qualitative result.** None of those is a paper. Item (iii) is a positive control on a truncated substrate, which is a useful internal check and not a contribution.

I record honestly what I did **not** establish: I could not read the paper's own text, so I cannot state *how* the publication reports family clustering, at what resolution, or whether it distinguishes 5′ from 3′ determination as sharply as W19c/W19d do. There may be a residual sliver of novelty in the *specific* 5′-vs-3′ decomposition. But the burden here runs the other way — the repository's own 2026-09-07 adjudication already ruled these ideas out as new, and I have no evidence to overturn it. **UNKNOWN cannot be converted into novelty.**

### 3. The "403-blocked genome-wide data" premise is false at the repository level

**PRIMARY.** From the base-`93b` tracked-file map, these are tracked blobs with real sizes:

```
   788065  research/autonomy/nr4a3-program-source-2026-09-07/sources/markers.zip
  3041469  research/autonomy/nr4a3-program-source-2026-09-07/outputs/peaks.tsv
  4579392  research/autonomy/nr4a3-program-source-2026-09-07/outputs/peak-gene-links.tsv
  2709678  research/autonomy/nr4a3-program-source-2026-09-07/outputs/program-membership.tsv
 11042624  research/autonomy/nr4a3-program-source-2026-09-07/outputs/tss.tsv
   301282  research/autonomy/nr4a3-program-source-2026-09-07/sources/paper.html
```

Corroborated by two files that **are** in the corpus:

- `source-manifest.jsonl` records a successful retrieval of `https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-024-02347-4/MediaObjects/41587_2…` at **788,065 bytes**, sha256 prefix `1d72675b0c58d59f`.
- `outputs/bed-members.tsv` (4,298 B, in the corpus, 33 lines = header + **32 members**) gives **per-member zip path, byte size, sha256, raw/unique/duplicate peak counts** for every one of the 32 genome-wide BEDs. Its counts match the panel exactly — e.g. `CCDC6-RET … 13692`, `TFG-NR4A3 … 2272`, `TPR-NTRK1 … 161` (the last is the `3,899 B` member W20b cited from the ZIP's member list as unreachable).

So the ZIP W20b/W19c/W19d/W19e/W23 all recorded as unrecoverable **was already fetched, hashed, unpacked and committed on 2026-09-07.** The 403 CONNECT denial from *this container* is real and I did not test it; it is not evidence that the repository lacks the data. Those files are absent from `corpus/` (the selected snapshot) and absent from this cloud checkout — that is a **snapshot-selection and branch-lineage gap, not an access gap.**

**Consequence.** W23's Rank 3 "Exact candidate-specific missing input: GSE243553 supplementary `MOESM3_ESM.zip`" is wrong as stated, as is W19e's closing "Progress beyond it requires the genome-wide peak sets, and that route is a recorded 403." The genome-wide peak sets exist in the repository. Only their delivery to a working checkout is missing.

### 4. Statistics audit of W19c and W20b — I attacked it and it held

I rebuilt the substrate from the two JSONs independently and reproduced every deterministic quantity: 32 peaksets, all prefixes ascending, all widths `[500]`, retained intervals min 4 / median 26 / max 28, **376 of 496** pairs non-degenerate, quintile mean J `0.0382 / 0.0167 / 0.0121 / 0.0110 / 0.0014`, SHARES-3 mean residual **+0.1515, p = 0.00008**, SAMEFAM-DIFFGENE **+0.1608, p = 0.00002**. (W19c reports the quintile means as `0.0387/0.0163/0.0126/0.0110/0.0014`; the ≤0.0005 differences are quintile tie-breaking at the bin boundaries, not a substantive difference.)

**(a) What is the experimental unit?** The **peakset (n = 32)**, not the pair (n = 376). PRIMARY, measured:

| Class | n pairs | distinct peaksets | max pairs from one peakset |
|---|---|---|---|
| SHARES-3 | 10 | 12 | 3 |
| SHARES-5 | 66 | **15** | **11** |
| SAMEFAM-DIFFGENE (W19e primary) | 15 | **8** | **5** |
| all | 376 | 32 | 31 |

The dependence is severe and exactly as the dispatch suspected: W19e's 15 "observations" come from 8 objects, one of which (`EWSR1-ETV1`) enters 5 of them. Nothing resembling n = 15 independent observations exists.

**(b) Is the whole-name permutation a valid null for a pair statistic on the same 32 peaksets? — Yes, and this is the part I expected to break and could not.** The permutation relabels the 32 peaksets and **recomputes the entire dependent class statistic** from the same fixed pair topology on each draw. Pair-to-pair dependence is therefore *inside* both the observed statistic and every null draw. Under the sharp null "gene labels are exchangeable across peaksets", this is an exact randomization test and its type-I error is correct **despite** the dependence. The dependence in (a) is real, but it damages *precision and generalization*, not *validity*: the correct reading is that a p of 2e-5 rests on 8 underlying objects, so the effect size is far less certain than the p-value's magnitude suggests. W19c's own stated rationale for choosing this null over resampling peaksets is sound and I confirm it. W19e's §3 self-correction — that NULL A and NULL B′ are the same null for a 3′-defined class — is also correct.

**(c) Does the density-quintile residual do what it claims? — Partly. It controls the confound it names and misses a larger one, which nevertheless does not overturn the result.** The residual removes only the quintile mean of J against `|Δlog₁₀ n_intervals|`. The stronger mechanical driver of a windowed Jaccard is the **window depth `min(|A|,|B|)`**, which is uncontrolled and badly imbalanced:

| Class | n | median min-depth | mean J | mean residual (density only) | mean residual (density × depth) |
|---|---|---|---|---|---|
| SHARES-3 | 10 | 6.5 | 0.1715 | +0.1515 | +0.1467 |
| SHARES-5 | 66 | 8.5 | 0.0300 | +0.0095 | +0.0097 |
| NEITHER | 300 | 5.0 | 0.0077 | −0.0071 | −0.0070 |
| **SAMEFAM-DIFFGENE** | 15 | **17.0** | 0.1887 | **+0.1608** | **+0.1459** |
| all | 376 | 5.5 | 0.0159 | +0.0000 | — |

Across the whole panel J rises ~8.7× with depth (mean J by min-depth bin 0–4/5–9/10–14/15–19/20+: `0.0050, 0.0145, 0.0199, 0.0286, 0.0435`, n = 153/88/54/43/38). W19e's primary class sits at median depth **17 against a panel median of 5.5** — a serious uncontrolled imbalance that no report names. I added a 5×5 density×depth cell residual: the effect drops only 0.1608 → 0.1459 and the permutation p is unchanged at the Monte-Carlo floor (0.00002).

I also checked the residual's own assumption, within-quintile density imbalance: SAMEFAM-DIFFGENE's within-quintile mean `|Δlog n|` is `0.0934 / 0.3184 / 0.5342` against quintile means `0.1028 / 0.3065 / 0.5212` — near-perfectly matched, no smuggled residual imbalance.

**(d) A stricter null I built, which the prior reports did not run.** W19e's 8 class peaksets are a density clique (`n_intervals` 1363–5805, all above the panel median 1652; panel quartiles 173 / 1652 / 4429). If same-family genes simply produce similar peak counts, the whole-name shuffle would be too permissive. I therefore permuted labels **only within `n_intervals` quartiles** (4 strata of 8), 50,000 draws, seed 20260908:

| Class | statistic | observed | stratified p |
|---|---|---|---|
| SHARES-3 | density residual | +0.1515 | **0.00002** |
| SAMEFAM-DIFFGENE | density residual | +0.1608 | **0.00002** |
| SHARES-5 | density residual | +0.0095 | 0.06790 |

Holding each peakset's density stratum fixed **strengthens** the 3′ effect rather than dissolving it, and leaves the 5′ negative a negative.

**Conclusion of the audit: I found one real defect (uncontrolled window depth, materially imbalanced in W19e's primary class) and it does not overturn the result. The pair-dependence is severe but does not invalidate the permutation. The statistics are not why this prospect fails.**

### 5. Can chr1-prefix sampling answer a useful narrow question at all?

**It can, and does — but the only question it can answer is one the publication already answered.** The substrate is honest and internally exact: the prefixes are coordinate-sorted, so each pair's set is complete inside `chr1:0–W` and the Jaccard is exact for that window. What it cannot support is any *quantitative* claim — the median window is ~15.8 Mb of a ~3.1 Gb genome (≈0.4%), depths are 4–28 intervals, windows are pair-dependent and therefore not commensurable, and the byte truncation makes the retained interval count roughly constant (~26) irrespective of true peak count, so window extent is an artifact of density rather than biology.

So: **it can qualitatively re-detect a strong, already-published clustering signal. It cannot measure it, cannot generalize it, and cannot support a paper.** That answer is now moot in the practical sense, because §3 shows the full 32 genome-wide BEDs are retained and the truncation is unnecessary.

### 6. Corrections owed on the DBD-family line

- **W19e is a reproducible EXPLORATORY successor, not independent confirmation, and not held-out validation.** The family rule was fixed after W19d's post-hoc §3 observation on **the same 32 peaksets, the same 376 pairs, the same substrate**. W19e's own discipline is genuinely good — a sourced table written before any Jaccard, DDIT3 correctly left UNKNOWN rather than inherited, an enforced n ≥ 4 floor, its "both nulls" rule self-corrected — and it should be credited. But procedural prespecification on **recycled data** does not create independence. 7 of W19e's 15 primary pairs are numerically W19d's post-hoc 7 (its mean +0.2043 reproduces exactly), i.e. the confirming set contains the discovering set. **Any wording implying prespecified confirmation or validation must be corrected to "reproducible exploratory successor on the same data."** The title `W19e-dbd-family-prespecified-test.md` should not stand unqualified.
- **The claim that clinical practice assumes partner interchangeability is UNSOURCED.** W20b's Question section asserts *"The repository treats … as variants of one disease, and clinical practice does the same"*; W23 repeats it as *"which the repository and clinical practice both currently assume."* I searched the corpus for it: `grep -rn -i "interchangeab"` and `grep -rn -i "one disease\|regardless of partner\|partner.independen"` over all 5,996 files returned **no source stating this about clinical practice**. Every `interchangeab` hit is a repository document asserting that two things are *not* interchangeable (assays, reagents, inhibitors, vocabularies). **The claim must be dropped or anchored to an actual guideline or reference. It must not be repeated.**
- **W19e's ETS/CREB assignments are honest but thin.** 8 of 25 3′ genes sourced, 17 UNKNOWN; 14 of 15 primary pairs are ETS, so this is in practice a test of one family, and the family boundaries come from sarcoma-pathology prose rather than a DBD taxonomy. W19e states all three limits itself.

---

## Validation evidence

All **RUN**. Nothing here is `PROPOSED (NOT RUN)`. Environment for every run: container `container_0166QEHnXrRA8nCR59c9UG4k--claude_code_remote--71b0d4`, Linux, `cwd=/tmp/claude-0/w25`, Python `3.11.15`, stdlib only, **no network**, no GPU, no spend.

**RUN 1 — anchors.** `date -u`, the `env` grep, `git rev-parse HEAD`, `git status --porcelain`, `mkdir -p /tmp/claude-0/w25`. Output quoted in §Worker. **Exit 0.**

**RUN 2 — corpus scope.** `find /tmp/claude-0/frozen-corpus/extracted/corpus/ -type f | wc -l` → `5996`. **Exit 0.**

**RUN 3–6 — corpus greps.** Commands and hit counts tabulated in §Prior-work check. **Exit 0.**

**RUN 7 — the two decisive quotations.** `grep -rn -i "family clustering\|context-invariant" $C` → exactly 2 files, verbatim text quoted in Result §2. **Exit 0.**

**RUN 8 — the retained genome-wide data.** `wc -l`/`head`/`tail` on `outputs/bed-members.tsv` (33 lines, 32 members with sha256 and peak counts); `source-manifest.jsonl` parsed to (url, bytes, sha256) triples; `grep "nr4a3-program-source-2026-09-07" …/tracked-file-map.txt` → 60 tracked paths with sizes. Output quoted in Result §3. **Exit 0.**

**RUN 9 — live-tree absence.** `ls -d research/autonomy/nr4a3-program-source-2026-09-07` → `No such file or directory`; `git ls-files | grep …` → empty; `find $C -name "paper*.htm*"` → empty. **Exit 0 / 2 (ls).**

**RUN 10 — main audit.** `cd /tmp/claude-0/w25 && python3 --version && time python3 audit.py; echo "EXIT=$?"` → `real 1m4.809s`, **`EXIT=0`**. (First invocation exited 1 on an `AttributeError` — `peakset_inventory` is a dict, not a list; the fix touched only that loop. Both runs are in the tool log.) Verbatim output quoted in Result §4.

**RUN 11 — stratified null.** `time python3 strat.py; echo "EXIT=$?"` → `real 0m35.059s`, **`EXIT=0`**. Verbatim:
```
SHARES-3           stat=res   obs=+0.1515 stratified p=0.00002
SAMEFAM-DIFFGENE   stat=res   obs=+0.1608 stratified p=0.00002
SHARES-5           stat=res   obs=+0.0095 stratified p=0.06790
```
(An intermediate invocation exited 1 on a `KeyError: 'res2'` from an `exec`-truncated prelude; the fix restricted the loop to the one defined statistic.)

**RUN 12 — end state.** `date -u`; `git rev-parse HEAD` → `fc6ed929…`; `git status --porcelain` → **empty**; `ls -la /tmp/claude-0/w25/` → two `.py` files. **No repository file was created, modified or deleted by me. No git write of any kind.**

### Code (returned inline, not written into the tree)

`/tmp/claude-0/w25/audit.py` (6,104 B) rebuilds the substrate from the two committed JSONs; computes the windowed Jaccard, the density quintiles and residual, the class census, the per-class dependence counts, the window-depth tables, the density×depth cell residual, and the whole-name permutation under both residual definitions. `/tmp/claude-0/w25/strat.py` (2,650 B) reuses that prelude via `exec`, reports within-quintile density imbalance and per-class peakset densities, and runs the density-quartile-stratified permutation. Both are stdlib-only and deterministic given `seed=20260908`. The coordinator can request the full bodies; I have kept them out of this report because the analysis they perform is one whose admission I am recommending against.

---

## Limitations

- **I could not read the primary publication.** `sources/paper.html` (301,282 B, PMC13105821) is tracked at `93b75888…` and absent from both the corpus and this checkout. My novelty subtraction rests on two **SECONDARY** repository statements about what the paper reports, not on the paper's text. If the owner disagrees with my reading, reading that one file settles it.
- **A tracked-file-map row proves a blob existed at `93b75888…` with that size; it does not prove I can obtain the bytes here, and I did not obtain them.** Per `CORPUS-CONTEXT.md`, files listed there but absent from `corpus/` remain UNKNOWN as to local availability. What I claim is retention in the repository, not availability in this container.
- **My statistical audit inherits every substrate limit unchanged and without softening**: the window is ~0.4% of the genome at the median; depths are 4–28 intervals; windows are pair-dependent and not commensurable; these are the authors' own marker calls at a threshold this repository did not set and did not re-call.
- **My stratified null is one more label-permutation, not an independent panel.** It cannot repair the fact that 15 pairs come from 8 objects. No amount of reanalysis of this file can.
- **I did not test the 403 route and did not route around it.** It stands as a recorded denial.
- **HEK293T is not EMC.** Nothing in this report transfers to chondroid tissue, to any tumour, to any patient, or to disease behaviour. No efficacy, safety, selectivity, therapeutic-window, potency, dosing or clinical-readiness statement is made or implied about any agent, target or gene. There is no wet lab.
- I checked five reports; I did not re-audit W20b's Analysis A, W19d's ARM 1 subgroup arithmetic, or any report outside this lane.

---

## Stop condition

**Set:** return either the exact next executable computation with a meaningful stop condition, or the named evidence missing for a defensible decision — with an honest "novelty fails" or "identifiability fails" being complete.

**MET, by the novelty branch, with the missing evidence named exactly.** Novelty fails: the publication already reports family clustering and context-invariant chromatin effects, per two retained repository documents, one of which is the repository's own 2026-09-07 paper-selection memo carrying a stop rule that fires on precisely this condition. Identifiability does *not* fail — the statistics survived both confound attacks — which makes the novelty failure the sole and sufficient ground.

---

## Tool-call and wall-clock count actually used

**14 tool calls.** Wall clock `02:55:49Z → 03:02:25Z` = **6 min 36 s**, plus this report. Well inside the ~40-call / ~40-minute target. Compute: ~100 s CPU across three Python runs. No GPU, no paid API, no spend, no network.

---

## Next concrete action

**Recommendation to the owner: decline admission of the GSE243553 partner-binding line as a paper.** Not because the analysis is bad — it is careful, self-correcting work whose central statistical claim survived my best attempts to break it — but because what it establishes is already published, and the repository had already decided in writing on 2026-09-07 that these ideas are not claimed as new.

**The exact next executable computation, if the owner wants the line kept alive.** It is a *verification* step, not another analysis, and it has a hard stop condition:

> Deliver `research/autonomy/nr4a3-program-source-2026-09-07/` into a readable checkout — specifically `sources/paper.html` (301,282 B), `sources/markers.zip` (788,065 B) and `outputs/peaks.tsv` (3,041,469 B). Then, **before any new computation**, read the paper's Results section on cross-fusion clustering and answer one question: *does the publication already report that peak location is determined by the 3′ moiety and not the 5′ partner, at family resolution?*
>
> **Stop condition — binding.** If yes, the line is closed and the four reports are retained as an internal reproduction of published work on a truncated substrate, plus two real data-hygiene corrections. If no, and only then, the identical W19c/W19d/W19e machinery is re-run on the **genome-wide** 32 BEDs, where the ~0.4%-of-genome window, the 4–28-interval depths, the pair-dependent windows and the whole window-depth confound all disappear at once — and the pair-dependence problem (15 pairs from 8 peaksets) remains and must then be addressed by a cluster-aware statistic, not by a larger p-value.

That step costs one file delivery and one careful read. It is the only thing that can change the disposition, and it is cheaper than any further analysis of the prefix file.

**Corrections the coordinator should append** (focused notes, not new review rounds): to **W20b and W23**, that the "clinical practice assumes partner interchangeability" claim is unsourced and must be dropped; to **W20b, W19c, W19d, W19e and W23**, that the genome-wide BEDs and the paper full text are retained in the repository at base `93b75888…` and the "403 blocks the only route" framing is a false absence produced by searching the live checkout only; to **W19e**, that it is a reproducible exploratory successor on recycled data, not a prespecified confirmation or held-out validation, and that its primary class carries an uncontrolled window-depth imbalance (median min-depth 17.0 vs panel 5.5) which I measured and which does not overturn its result.
