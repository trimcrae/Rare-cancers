<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:10:00Z UTC
     agent id a15ebe1b499343753 ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a15ebe1b499343753.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

# W01g — What "transcriptome-wide" means in this inventory, and whether the criterion survives being applied consistently

## Worker

- **Worker:** W01g, lane 1 refill (public EMC tumour expression / multiomics resources), OPUS-CAPACITY-CAMPAIGN-20260908.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a model. The coordinator must extract the served model from the transcript.
- **`date -u` start:** `Tue Sep  8 03:01:40 UTC 2026`. **`date -u` end:** `Tue Sep  8 03:05:43 UTC 2026`.
- **HEAD actually read:** `fc6ed92999c26f52c47668d1c126321a5f51d1b5` at start (≠ the brief's frozen `92abbcb9…`; ≠ W01f's `4d950cf0…`). **Every reading below is against `fc6ed929`.** At exit HEAD had moved to `87ba0a859680eb72163c23f95ddad274909f0ad8` — coordinator activity, not mine.
- **`git status --porcelain`:** empty at start, empty at end (exit 0). **Zero writes to the Git tree.** All execution under `/tmp/claude-0/w01g/`. **No network and no retrieval of any kind** — no WebFetch, no WebSearch, no PubMed MCP, no archive or accession query.
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** (exit 0), literal; four long proxy host lists and the JVM flag string are marked elided and name no model:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=<long host list, elided — names no model>
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
GLOBAL_AGENT_NO_PROXY=<long host list, elided>
ANTHROPIC_BASE_URL=https://api.anthropic.com
CLAUDE_CODE_DIAGNOSTICS_FILE=/tmp/claude-code-303934770.diag.log
CLAUDE_ENABLE_STREAM_WATCHDOG=1
CLAUDE_CODE_REMOTE_HERMETIC_MODE=0
CLAUDE_CODE_ENVIRONMENT_RUNNER_VERSION=release-ba76006550-ext
CLAUDE_CODE_DISABLE_BUILTIN_ANTMCP=1
CLAUDE_ADDITIONAL_DIRECTORIES=/mnt/user-data
JAVA_TOOL_OPTIONS=<truststore/proxy flags, elided — names no model>
NO_PROXY=<long host list, elided>
CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1
CLAUDE_CODE_USE_CCR_V2=true
CLAUDE_CODE_SYNC_SESSION_REFS=1
DOCUMENTS_MCP_SCRATCH_ROOT=/mnt/user-data/working/claude-docs
CLAUDE_CODE_TEE_SDK_STDOUT=true
CLAUDE_CODE_ENTRYPOINT=remote
CLAUDE_CODE_VERSION=2.1.42
CLAUDE_CODE_EXECPATH=/opt/claude-code/bin/claude
npm_config_noproxy=<long host list, elided>
CLAUDE_CODE_REMOTE_SEND_KEEPALIVES=true
CLAUDE_CODE_REMOTE=true
CLAUDE_CODE_POST_FOR_SESSION_INGRESS_V2=true
CLAUDE_CODE_ORGANIZATION_UUID=9f10e945-e412-4b71-8a9d-5d6affcd7d4f
CLAUDE_SESSION_INGRESS_TOKEN=<redacted>
CLAUDE_CODE_SYNC_SKILLS=1
CLAUDE_CODE_HOLD_UNANSWERED_PARKED_PERMISSION=1
CLAUDE_CODE_MESSAGING_TOKEN=<redacted>
```

## Question

Pursued exactly as dispatched: **what does "transcriptome-wide" mean in this inventory, and does the criterion survive being applied consistently?** Concretely — put the three stable-core deposits, the contested TempO-Seq row and the excluded PMID 41644428 on one table with the same platform columns from committed evidence; enumerate the candidate definitions the committed record actually uses; and state, for each, which rows it admits and what the stable core becomes.

It is open because W01f named **S-PARITY** and declined to assert it: the criterion that excludes row 11 (a targeted probe panel is not transcriptome-wide) applies on identical probe-set logic to `GSE4303`, a spotted cDNA array. If it does, the only quotable number this lane has — a stable core of 20 specimens — falls to 10. W01e's D2 had already found the criterion applied asymmetrically; neither worker set it.

## Prior-work check

Read in full at `fc6ed929`: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, and the three named reports (`W01c` 347 lines, `W01e` 241, `W01f` 240 — `wc -l` run before reading). Commands run and what they showed:

| command | result |
|---|---|
| `rg -n --glob '!.git' '41644428' .` | 16 hits. The only assay-level statement anywhere in the tree is `W02-…:109` (*"IHC + FISH + NGS, 16 EMC cases"*, graded PRIMARY). `emc-mortality-probe.json:1642` carries bibliographic metadata only (no PMC, `isOpenAccess: N`); `emc-tsc-mtor-findings-2026-08-24.json:635` calls it a *"clinicopathological and molecular series"*. **No committed source establishes its platform.** |
| `rg -n -i --glob '!.git' -e 'GPL3290' -e 'GPL6244' -e 'GPL10999' -e '42,?000.spot'` | 313 KB of hits; the load-bearing ones are pinned with `file:line` in R1 |
| `rg -n -i -e 'not transcriptome-wide' -e 'not whole-transcriptome' -e 'rather than transcriptome'` | the two verbatim criterion statements quoted in R2 (`emc-atr-vulnerability-assessment.md:872`, `emc-fourth-cohort-sra-2026-08-08.md:175`) |
| `ls research/autonomy/ \| grep -c nr4a3-patient-junction` | `0` — confirms the directory is absent from this checkout, as the dispatch states. I did not read the frozen corpus this run; nothing below depends on it. |

**Confirmed not replayed.** No retrieval of any kind was attempted — no accession, no PubMed, no archive, no route. `PRJNA692081` / `SRP301712` are treated throughout as **ALREADY RECOVERED**; I did not touch them, and Brenca's row 8 is held at baseline as **SECONDARY, out of scope**. **No cohort, independence or patient claim is made or implied anywhere: 15 unresolved libraries are not 15 patients, libraries are not specimens, the paper-stated specimen count is 12.** I did not attempt to identify row 12. I did not re-derive W01f's leave-one-out table. PUB-EMC-CLASSIFICATION is not reopened. `GSE4303` / `GSE28866` are `CLOSED-WORK.md` "heavily retained" data — I re-read *committed characterisation artifacts about them*, not the deposits, and claim no new data.

**Novelty statement, plainly:** this run adds **no source and no data**. Genuinely new content is (a) the five-row platform table built from committed measurements rather than from paper prose, (b) the enumeration of five conflicting definitions actually in use with `file:line`, (c) the admission matrix and the core range **0–20**, and (d) one measurement nobody had put next to the criterion: the repository has **measured** gene space for `GSE24369` and `GSE28866` and has **never** measured it for `GSE4303`.

## Method / inputs

All inputs are committed artifacts read at `fc6ed929`; no paper was retrieved.

| input | supplies |
|---|---|
| `research/modalities/emc-atr-vulnerability-inputs.json` (`part_b`) | per-platform `n_samples`, `n_probes`, `value_kind`, `accession_resolution_rate`, `n_geneset_genes_measured` for every GSE4303 platform file, GSE24369, GSE28866 |
| `research/modalities/emc-fourth-cohort-quant.json` | the TempO-Seq deposit's **measured** probe and gene space, the probe gate, and the depositor-claim caveat |
| `research/modalities/emc-gse4303-crosscheck.json` | the first GSE4303 read and its `n_probes_mapped: 0` |
| `research/method-watch.md`, `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md` | the two committed verdicts on GSE4303 usability and on TempO-Seq |
| `research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md` | the panel-vs-transcriptome analysis and the superseded/retained panel-naming note |
| `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md` | Table 2 (the three cohorts) and Table 7's 14,120-gene 3SEQ calibration |
| `reports/W01c…`, `W01e…`, `W01f…`, `W02…` | the inventory rows, D2, S-PARITY, and the only assay statement for PMID 41644428 |

Tool: `python3` 3.11.15 on Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w01g/`, outside the repository. Script `criterion_matrix.py` (returned in full in Validation evidence).

## Result

### R1 — The five rows on one table, from committed evidence

Every cell is either a committed measurement (PRIMARY) or explicitly UNKNOWN. **"Fraction of the transcriptome addressed" is not directly recorded for any row**; the last column is the nearest committed proxy, and the proxy differs between rows, which is itself part of the finding.

| # | deposit / study | n EMC | assay & platform | probe/spot count | probe set fixed & pre-selected? | committed gene-space measurement | grade |
|---|---|---:|---|---|---|---|---|
| 2 | `GSE4303` (Subramanian 2005) | 10 | two-colour spotted cDNA clone array, 7 platform files (`GPL2937/2938/3254/3288/3289/3290/3335`), 36 samples total; EMC on `GPL3290` | **43,008** spots on `GPL3290` (`emc-atr-vulnerability-inputs.json:97437`); 41,472–45,312 across the print run | **YES** — a fixed spotted clone set, probes annotated by **EST accession only** (`part_b.series_seeds`) | ⚠ **never measured.** `n_geneset_genes_measured` = **1,207 of the 1,383-gene query set (87.3 %)**; the accession→symbol bridge resolves **0.582** of distinct accessions (`…decline-review-statistics-2026-08-10.md:508–511`); the first read mapped **0 probes** (`emc-gse4303-crosscheck.json`, `n_probes_mapped: 0`). **No committed number states how many genes this array addresses.** | PRIMARY (counts) / **UNKNOWN** (transcriptome fraction) |
| 4 | `GSE24369` (Möller 2011) | 6 | Affymetrix Gene ST, `GPL6244`, single-channel intensity, 42 samples | **28,459** probes (`emc-atr-vulnerability-inputs.json:3546`) | **YES** — a fixed manufactured probe set | **20,324 of 28,459 probes carry a gene symbol = 71.4 %** (`emc-sgk1-lane-assessment.md:246`); `n_geneset_genes_measured` **1,308/1,383 = 94.6 %** | PRIMARY |
| 5 | `GSE28866` (Brunner 2012) | 4 | **3SEQ** (`GPL10999`) — 3′-end library sequencing; value is 3′-end read density per peak; 99 samples | **no probe set** — libraries, not probes (`n_probes: 0` at `…inputs.json:61786` is a matrix-parse reading, not a panel) | **NO** | **14,120 genes** calibrated in the deposit (`nr4a3-fusion-transcriptional-output.md:595`). ⚠ the ATR pipeline read **0** of the 1,383-gene set from this matrix — a mapping failure in that pipeline, **not** a coverage measurement | PRIMARY |
| 11 | `PRJNA1357027` / `SRP640302` (Chaiboonchoe 2026) | 12 | **TempO-Seq**, templated-oligo ligation panel, FFPE, 50 nt single-end, 12 runs / 12 samples | **1,645** probes common to every run (`emc-fourth-cohort-quant.json:276`); 213,007 probe-table rows across runs; ~6,251–10,546 sequences cover 80 % of reads per run | **YES** — a commercial fixed panel | **862 genes** have ≥1 assigned probe (`…quant.json:277`); 906 probes assign to one gene, 77 multi-gene, 662 unassigned. Vendor/depositor name claims *"whole human transcriptome"* (`…quant.json:16`) ≈20,000 genes; **the measured space is 862** | PRIMARY (measurement) / **CONTESTED** (name) |
| — | PMID 41644428 (2026 Chinese two-centre series) | 16 | **UNKNOWN.** The only committed assay statement is *"IHC + FISH + NGS"* (`W02-…:109`, PRIMARY); no PMC, `isOpenAccess: N` (`emc-mortality-probe.json:1642`) | UNKNOWN | UNKNOWN | UNKNOWN | **UNKNOWN** |

**Two facts on this table were not previously stated side by side and they matter:**

1. **The deposit whose gene space is best measured is the one the criterion currently excludes.** Row 11 is the only row with a run-level, in-repository probe-and-gene census (862 genes, 1,645 probes). Row 2 — the largest member of the stable core — has **no** committed transcriptome-coverage number at all.
2. **Row 5 is the only one of the five that is not a fixed pre-selected probe set.** 3SEQ builds libraries; the other three array/panel rows all select their targets in advance.

### R2 — The candidate definitions actually in the committed record, quoted

There are **five distinct definitions in use, and they conflict.** Each is quoted with `file:line`.

**D1 — NOMINAL: the assay's own name asserts the scope.**
> `reports/W01c-emc-deposit-literature-inventory.md:125` — row 11's Platform column reads **"TempO-Seq Human Whole Transcriptome 2.0, FFPE"**, and the row is admitted on that basis.
> Its source: `research/modalities/emc-fourth-cohort-quant.json:16` — `"TempO-Seq whole human transcriptome assay using BioSpyder reagents"`.

**D2 — ESTABLISHED, NOT MERELY STATED.**
> `reports/W01c-…:129` — *"PMID 41644428 (16 EMC…) — **NGS stated but not established as whole-transcriptome**, so counting it would inflate the numerator on an assumption"*, and *"PMID 41315062 … whole-transcriptome **not established**"*.

**D1 and D2 are applied in the same table, in opposite directions, to rows of the same evidential standing** — W01e's D2 (`W01e-…:144`). This report adds that **the repository's own artifact refuses D1 explicitly**:
> `emc-fourth-cohort-quant.json:18` — *"The assay description above is the **depositors' own words in their own deposit. It is not an independent measurement**, and the read-structure numbers below are."*
> `emc-fourth-cohort-quant.json:10` — *"**Not a confirmation of any named commercial probe panel or of its gene content.**"*

So D1 is not merely inconsistent with D2; it is applied against a caveat the cited artifact wrote to forbid exactly that use.

**D3 — NO FIXED, PRE-SELECTED TARGET SET (the assay must be open).**
> `research/manuscripts/fusion-output/emc-fourth-cohort-sra-2026-08-08.md:175` — *"TempO-Seq is a **templated-oligo ligation panel**, not whole-transcriptome sequencing."*
> `…:272` — *"It is not a processed expression matrix, **not whole-transcriptome**, not …"*
> `research/manuscripts/dependency/emc-atr-vulnerability-assessment.md:872` — *"whole-transcriptome **targeted TempO-Seq** rather than transcriptome-wide."*

**D4 — MEASURED GENE SPACE (a coverage threshold, checkable against artifacts).** Never stated as a rule, but it is the standard every committed *measurement* was built to serve: 20,324 mapped symbols on `GPL6244`, 14,120 genes in the 3SEQ deposit, 862 genes on the TempO-Seq panel, 0.582 bridge on `GPL3290`. The panel note reasons in exactly these terms:
> `emc-fourth-cohort-sra-2026-08-08.md:179` — *"Which TempO-Seq panel (**S1500+ ≈ 3,000 genes, or a whole-transcriptome variant ≈ 20,000**) is the single most decision-relevant unknown."*

**D5 — MODALITY ONLY: RNA expression, as against DNA or methylation.**
> `reports/W01c-…:129` — *"`GSE140686` (methylation, not expression); `SRP445369` / PMID 39086683 (**whole genome, not transcriptome**)"*.

**A sixth criterion is present and must be kept separate: USABILITY.**
> `research/method-watch.md:465` — *"**outcome: GSE4303 is UNUSABLE** (two-colour cDNA-clone array; log-ratios not absolute expression; probes lack gene symbols → 0 shortlist genes resolved)"* — later partly reversed: `emc-atr-vulnerability-assessment.md` §6.3 records *"the EST bridge for GSE4303 works via the archived UniGene build"*.
> **Usability is not transcriptome-wideness.** A deposit can address the whole transcriptome and be unreadable, or address 862 genes and be perfectly readable. Conflating them would let `GSE4303` fail for the wrong reason and let row 11 pass for the wrong reason. It is excluded from the matrix below and named here so it is not smuggled in.

### R3 — What each definition admits, and what the stable core becomes

Machine output, `criterion_matrix.py`, exit 0, assertions passed. Rows 8 (Brenca, 12) and 12 (unnamed series, 19) are **held at W01e/W01f's baseline** and are out of scope; "floor" and "ceiling" therefore move only through the in-scope rows. Total is 84 except where PMID 41644428 is admitted.

| definition | admits, of the five | **stable core** | floor | ceiling | inventory total |
|---|---|---:|---:|---:|---:|
| D1 nominal (assay name asserts it) | 4303, 24369, 28866, row 11 | **20** | 44 | 63 | 84 |
| D2a established-by-evidence, UNKNOWN excluded | 24369, 28866 | **10** | 22 | 41 | 84 |
| D2b established-by-evidence, UNKNOWN retained | 4303, 24369, 28866 | **20** | 32 | 51 | 84 |
| D3 no fixed pre-selected probe set | 28866 only | **4** | 16 | 35 | 84 |
| D3′ full-length transcript coverage | none | **0** | 12 | 31 | 84 |
| D4a measured gene space ≥10k, GSE4303 counts | 4303, 24369, 28866 | **20** | 32 | 51 | 84 |
| D4b measured gene space ≥10k, GSE4303 UNKNOWN | 24369, 28866 | **10** | 22 | 41 | 84 |
| D5 modality only (RNA expression, any target space) | all five | **20** | 44 | 63 | **100** |

**Stable-core range across the definitions actually in the record: 0 – 20 specimens.** The quoted band's floor ranges **12 – 44** and its ceiling **31 – 63**, from the assay criterion alone — before any of W01f's other nine decisions fires.

### R4 — Which definitions are self-consistent, and which admit a row on grounds they deny another

This is a checkable property, and it is the part that does not require the lane owner's judgement.

**Self-consistent (one rule, applied in both directions):**

- **D2** — evidence must establish the scope. Applied consistently it excludes row 11 (measured 862 genes against a claimed ~20,000) **and** PMID 41644428 (platform UNKNOWN) **and** puts `GSE4303` in the UNKNOWN column, because no committed source states what fraction of the transcriptome 43,008 EST-annotated spots address. **D2 is the definition W01f's S-PARITY predicted, and the evidence confirms the prediction: under D2a the core is 10, not 20.** The escape is D2b — treat UNKNOWN as retained-pending rather than excluded — but that is a *different* rule from the one applied to PMID 41644428, whose platform is equally UNKNOWN. **D2a and D2b cannot both be right; D2b applied to `GSE4303` and D2a applied to 41644428 is the same asymmetry one level down.**
- **D3** — no fixed pre-selected target set. Brutally consistent: it excludes both arrays and the panel and leaves 4 specimens. It denies nothing to one row that it grants another. Its cost is that it discards the two deposits this repository has actually analysed most.
- **D4** — a measured coverage threshold. Consistent and, uniquely, **checkable for four of the five rows from committed numbers today**. Its one gap is `GSE4303`, and the gap is a missing measurement, not a judgement: nobody has counted the genes that array addresses. D4a vs D4b turns on whether the 87.3 % coverage of a 1,383-gene query set is accepted as evidence of transcriptome-scale coverage — it is a *relative* proxy against `GSE24369`'s 94.6 %, not an absolute coverage measurement, so accepting it is a choice.
- **D5** — modality only. Fully consistent, and it does not discriminate targeted from untargeted at all. It admits everything RNA, which raises the inventory total to **100** if PMID 41644428's NGS turns out to be RNA (UNKNOWN), and leaves the core at 20.

**Not self-consistent:**

- **D1 (nominal).** It admits row 11 on a vendor product name while D2 excludes PMID 41644428 for a stated-but-unestablished assay — the same evidential footing, opposite outcomes, in the same table. It additionally contradicts the artifact it draws the name from (`quant.json:10,18`), which states in terms that the name is not a measurement and is not a confirmation of panel gene content. **This is the one combination in current use, and it is the only one on the list that fails a consistency test rather than a preference test.**
- **The current inventory as it stands = D1 for row 11 + D2 for PMID 41644428 + neither applied to `GSE4303`.** Row 2 has simply never been tested by any of the five definitions; it is in the core by default, not by criterion.

**One sentence that can be stated and applied in both directions.** Not a recommendation — the criterion is the lane owner's to set — but of the definitions in the record, only these are single sentences that decide all five rows the same way twice:

- **D3:** *"A deposit is transcriptome-wide only if its assay measures RNA without a fixed, pre-selected target set."* → core 4.
- **D4:** *"A deposit is transcriptome-wide only if a committed measurement shows it addresses at least N genes; where no such measurement exists the row is UNKNOWN, not admitted."* → core 10 today, 20 if `GSE4303`'s gene space is ever counted, and it names the exact missing measurement.
- **D5:** *"A deposit is in scope if it measures RNA expression in EMC tumour tissue, whatever its target space; target breadth is reported as a column, not used as a gate."* → core 20, total 84–100, and the word "transcriptome-wide" disappears from the headline, which is what makes it consistent.

D4 is the only one whose gap is closable by a measurement rather than by a ruling, and the measurement is cheap. D5 is the only one that does not shrink anything, at the price of retiring the phrase.

## Validation evidence

**RUN.** Environment: Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]; Linux 6.18.44-fc-v24 x86_64; cwd `/tmp/claude-0/w01g`, outside the repository. **No network in any command.**

| # | command | exit | key output |
|---|---|---|---|
| 1 | `date -u`; `env \| grep -i -E 'claude\|anthropic\|model' \| sed …`; `git -C /home/user/Rare-cancers rev-parse HEAD`; `git … status --porcelain` | 0 | start `03:01:40 UTC`; HEAD `fc6ed929…`; status **empty** |
| 2 | `wc -l` on the 7 required inputs | 0 | 84 / 70 / 63 / 387 / 347 / 241 / 240 |
| 3 | `cat COMMON-BRIEF.md CLOSED-WORK.md CORPUS-CONTEXT.md` | 0 | read in full |
| 4 | `cat reports/W01f-obtainable-band-stability.md` | 0 | R1–R5 incl. S-PARITY |
| 5–6 | `grep -n -i -E "transcriptome\|TempO\|probe\|platform\|41644428…"` over W01c, W01e | 0 | rows 2/4/5/11, the exclusion sentence at `:129`, D2 at `:144` |
| 7–8 | `rg -n -i` for `GPL3290\|GPL6244\|GPL10999`, and for `transcriptome-wide\|targeted panel\|TempO` | 0 | 313 KB / 44.6 KB of hits, persisted; load-bearing lines pinned |
| 9 | `sed -n '455,480p' research/method-watch.md`; `sed -n '860,885p' …emc-atr-vulnerability-assessment.md` | 0 | *"outcome: GSE4303 is UNUSABLE"*; *"whole-transcriptome targeted TempO-Seq rather than transcriptome-wide"* (`:872`) |
| 10 | `python3 -c` over `emc-atr-vulnerability-inputs.json` `part_b.platforms` | 0 | all 11 platform blocks: `GPL3290` 16 samples / 43,008 probes / two-colour log-ratio; `GPL6244` 42 / 28,459 / single-channel; `GPL10999` 99 / 0 |
| 11 | `python3 -c` over `emc-fourth-cohort-quant.json` | 0 | `n_probes_common_to_every_read_run: 1645`; `n_genes_with_at_least_one_assigned_probe: 862`; `n_probes_offered 1645`, `assigned_to_one_gene 906`, `unassigned 662`; the two caveat strings at `:10` and `:18` |
| 12 | `rg -n '41644428' .`; `python3 -c` over `emc-mortality-probe.json` and `emc-tsc-mtor-findings-2026-08-24.json` | 0 | 16 hits; **no platform statement anywhere**; `isOpenAccess: N`, `pmcid: null` |
| 13 | `sed -n '185,200p;590,600p' nr4a3-fusion-transcriptional-output.md` | 0 | Table 2 (three cohorts); *"all 14,120 genes in the same deposit"* (`:595`) |
| 14 | `python3 -c` over `part_b` non-platform keys | 0 | `n_geneset_genes_wanted: 1383`; `series_seeds` GSE4303 *"probes annotated by EST accession only"*; `_prior_attempt` *"mapped 0 probes to symbols"* |
| 15 | `cd /tmp/claude-0/w01g && python3 criterion_matrix.py; echo "EXIT=$?"` | **0** | the R3 table verbatim; **`stable-core range across candidate definitions: 0 - 20`**; **`ASSERTIONS PASSED`** |
| 16 | coverage arithmetic; `date -u`; `rev-parse HEAD`; `status --porcelain`; `ls research/autonomy/ \| grep -c nr4a3-patient-junction` | 0 | 94.6 % / 87.3 % / 0.0 %; 71.4 %; end `03:05:43 UTC`; HEAD moved to `87ba0a85…` (coordinator); status **empty — no tree writes by me**; junction directory count **0** |

`criterion_matrix.py`, in full (it does arithmetic only; every input is a transcribed committed reading, cited in R1):

```python
"""W01g - what does 'transcriptome-wide' admit? No network. Inputs are committed-record
readings transcribed in the report; this script only does the arithmetic."""
N = {"GSE4303": 10, "GSE24369": 6, "GSE28866": 4, "PRJNA1357027": 12, "PMID41644428": 16}
BRENCA = 12          # row 8, held at baseline (SECONDARY, not in scope)
ROW12  = 19          # ceiling adder, held at baseline (UNKNOWN identity)
TOTAL_BASE = 84

CORE3 = ["GSE4303", "GSE24369", "GSE28866"]

# admit-sets per candidate definition, over the five in-scope rows
DEFS = {
 "D1 nominal (assay name asserts it)":            ["GSE4303","GSE24369","GSE28866","PRJNA1357027"],
 "D2a established-by-evidence, UNKNOWN excluded": ["GSE24369","GSE28866"],
 "D2b established-by-evidence, UNKNOWN retained": ["GSE4303","GSE24369","GSE28866"],
 "D3 no fixed pre-selected probe set":            ["GSE28866"],
 "D3' full-length transcript coverage":           [],
 "D4a measured gene space >=10k, GSE4303 counts": ["GSE4303","GSE24369","GSE28866"],
 "D4b measured gene space >=10k, GSE4303 UNKNOWN":["GSE24369","GSE28866"],
 "D5 modality only (RNA expression, any target space)":
                                                  ["GSE4303","GSE24369","GSE28866","PRJNA1357027","PMID41644428"],
}
print(f"{'definition':52s} {'core':>5s} {'floor':>6s} {'ceil':>5s} {'total':>7s}")
cores=[]
for name, admit in DEFS.items():
    core  = sum(N[r] for r in CORE3 if r in admit)
    floor = core + BRENCA + (N["PRJNA1357027"] if "PRJNA1357027" in admit else 0)
    ceil  = floor + ROW12
    tot   = TOTAL_BASE + (N["PMID41644428"] if "PMID41644428" in admit else 0)
    cores.append(core)
    print(f"{name:52s} {core:5d} {floor:6d} {ceil:5d} {tot:7d}")
print()
print("stable-core range across candidate definitions:", min(cores), "-", max(cores))
assert max(cores) == 20 and min(cores) == 0
assert sum(N[r] for r in CORE3) == 20
print("ASSERTIONS PASSED")
```

**PROPOSED (NOT RUN):**
- **Count the genes `GSE4303` addresses** — read `GPL3290`'s platform record and resolve its EST accessions against a gene build. **Not run:** requires an archive query and a symbol bridge, both network acts this dispatch forbids. This is the single measurement that moves D4 from core 10 to a determinate answer.
- **Establish PMID 41644428's platform.** **Not run:** no PMC, `isOpenAccess: N`, and any route is a retrieval.
- **Verify the TempO-Seq panel identity against the reads.** **Not run** — and note `emc-fourth-cohort-sra-2026-08-08.md:301` already records that verifying the vendor name against the reads is *"the only way to verify"* and that **nothing here has done it**.

**No test suite and no `scripts/preflight.sh`.** This run changes no code, manuscript or shared state, and the dispatch does not call for them. Nothing here is a skipped check reported as a pass.

## Limitations

- **This is an audit of committed artifacts, not of the platforms themselves.** I did not read a single GEO platform record, vendor manifest or paper. Every platform fact is a repository measurement or a repository transcription, and where the repository is wrong I am wrong identically.
- **The "fraction of the transcriptome addressed" column is UNKNOWN for every row**, and saying otherwise would be the exact error this report is about. What exists is four heterogeneous proxies — mapped-symbol fraction (`GSE24369`), deposit-calibrated gene count (`GSE28866`), assigned-probe gene count (`PRJNA1357027`), and a 1,383-gene query-set coverage (`GSE4303`) — measured by different pipelines against different denominators. **They are not directly comparable, and the D4 threshold is therefore approximate.**
- **`GSE28866`'s 0/1,383 in the ATR artifact is a mapping failure, not a coverage measurement**, and I have not treated it as one. Its 14,120-gene figure comes from a different pipeline in the fusion-output manuscript.
- **`GSE4303`'s 87.3 % is relative, not absolute.** It says this array covers 87 % of what a 1,383-gene query set asked for; it does not say the array addresses 87 % of the transcriptome.
- **The definition set is not exhaustive.** I enumerated what the committed record uses or clearly implies. A definition nobody has written down would add rows to R3 and could widen the 0–20 range further.
- **Rows 8 and 12 are held fixed and are not analysed.** Row 8 (Brenca) is SECONDARY and out of scope by dispatch; **no cohort, independence or patient claim is built on it, and the specimen count stays at the paper-stated 12**. Row 12's identity remains UNKNOWN and I made no attempt on it. Note for the owner, flagged not asserted: **D2 applied consistently would also put row 8's platform in the UNKNOWN column**, since no committed source in this checkout establishes it — that would move the floor further than any figure in R3.
- **Specimens, not patients. Arrays are not patients. Runs are not patients. Libraries are not specimens.** Nothing here is a cohort and no patient-level deduplication exists.
- **Transcriptome-wideness is not usability and not quality.** A criterion that admits a deposit says nothing about whether its matrix is readable, comparable, or fit for any particular question.
- **No clinical claim.** This is a data-scope audit. Nothing here bears on EMC efficacy, safety, selectivity, prognosis or clinical readiness, and no computational result could.

## Stop condition

**Set up front:** all five rows on one table with the same platform columns from committed evidence; every candidate definition in the record quoted with `file:line`; an admission matrix giving the stable core under each; and an explicit, checkable statement of which definitions are self-consistent — **without** picking a winner, identifying row 12, re-deriving W01f's table, or reopening PUB-EMC-CLASSIFICATION. Return the moment those four exist.

**MET.** (1) Five-row table built, with `n_probes`, fixed-probe-set status and the nearest committed gene-space measurement per row, and **UNKNOWN written where it belongs** (R1). (2) **Five definitions** quoted with `file:line`, plus a sixth (usability) explicitly quarantined; **they conflict, and the conflict is the finding** (R2). (3) Matrix computed and assertion-checked: **stable core ranges 0 – 20**, floor 12 – 44, ceiling 31 – 63 from the assay criterion alone (R3). (4) Consistency adjudicated: **D2, D3, D4, D5 are self-consistent; D1 is not, and D1-plus-D2 is what the inventory currently runs** — with three one-sentence criteria that apply in both directions (R4). **No winner picked.** Returning immediately; no padding.

## Tool-call and wall-clock count actually used

**16 tool calls** (all Bash; zero MCP, zero WebSearch, zero WebFetch, zero network, zero retrieval) against the ~40 target. **Wall clock 4 min 03 s** (`03:01:40` → `03:05:43` UTC) against the ~40-minute target.

## Next concrete action

**One ruling by the lane owner, then one cheap measurement — in that order.**

The ruling: pick one of D2 / D3 / D4 / D5 and write it as a single sentence into whatever file owns the inventory, then apply it to all five rows in one pass. The consequence is priced in R3 and ranges from a core of 4 to a core of 20; **D1 is not available, because it fails the consistency test rather than a preference test**, and because the artifact it cites forbids its own use as a measurement. If the ruling is D5, the phrase "transcriptome-wide" should leave the headline entirely and target breadth should become a reported column — that is the only version of the inventory in which row 11's 862 measured genes and `GSE4303`'s 43,008 unmeasured spots can sit in the same table honestly.

The measurement, and it is the one worth buying: **count the genes `GSE4303` addresses.** Read the `GPL3290` platform record and resolve its EST accessions against a gene build. It is a single archive query on the GitHub Actions escape hatch (~15 min, $0, no GPU), it shares a runner job with the row-12 query W01e and W01f both queued, and it is the **only** action that converts the largest member of the stable core from a default inclusion into a criterion-tested one. Under D4 it decides between a core of 10 and a core of 20 — the exact 10 specimens S-PARITY threatens — and it does so with a number rather than a ruling.
