> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

# W01e — What makes 32 of 84 EMC expression specimens obtainable, and is the classification reproducible from committed data?

## Worker

- **Worker:** W01e, lane 1 refill (public EMC tumour expression / multiomics resources).
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a model; the coordinator must extract the served model from the transcript.
- **`date -u` start:** `Tue Sep  8 02:27:55 UTC 2026`. **End:** `Tue Sep  8 02:32:20 UTC 2026`.
- **HEAD actually read:** `b9a0257e6acff53ad22535cf2adf261313e0b250` at start (≠ the brief's frozen `92abbcb9…`, ≠ W01d's `b9a0257e` end state); at exit HEAD had moved again to `47aac85f874a57a6f981c3432abcf16980968aec` (coordinator activity, not mine). **All committed-data readings in this report are against `b9a0257e`.**
- **Write isolation honoured.** `git status --porcelain` filtered of the campaign directory returned empty (grep exit 1). Execution and both scratch files under `/tmp/claude-0/w01e/`. Nothing downloaded; **no network used at all** — not even PubMed MCP, because the question is answerable from committed data.
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** (exit 0), literal, long proxy host lists marked:

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

Pursued exactly as dispatched: **what makes 32 of W01c's 84 EMC expression specimens "obtainable without correspondence" and the other 52 not, and is that classification reproducible from committed data alone?** Per-study re-derivation of deposit status and specimen count against W01c's table, disagreements named, Brenca's row corrected or confirmed, and the single highest-leverage classification decision identified.

It is open because W01c's band was built in-session from PubMed full texts and never checked against this repository's own committed GEO/SRA artifacts, and because the owner's Brenca closure post-dates W01c and W01d.

## Prior-work check

Commands run and what they showed:

- `git ls-files | grep -i -E 'junction-source|brenca'` → **one file only**: `research/autonomy/opus-capacity-campaign-20260908/reports/W01b-brenca-accession-recovery.md`.
- `rg -n -i --glob '!.git' -e 'PRJNA692081' -e 'SRP301712' -e 'path\.5737' -e '34216030' -e 'PMC8451045' .` → the accessions and the correction DOI appear **only** in `research/autonomy/opus-capacity-campaign-20260908/WAVE-LOG.md:82-84` (the coordinator's transcription of the owner closure). PMID `34216030` appears in two modality artifacts as a bare identifier. **`research/autonomy/nr4a3-patient-junction-source-2026-09-07/` does not exist at this HEAD** (`ls research/autonomy` confirms).
- Per closure #2 I **do not** treat that local absence as source novelty. I attempted **no** recovery of PRJNA692081/SRP301712 and replayed **none** of W01b's fourteen routes. Any statement here about the Brenca deposit is transcribed from the owner closure and graded SECONDARY.
- Read in full: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `reports/W01c-…`, `reports/W01d-…`, the structural parts of `reports/W01b-…`.
- Confirmed not replayed: Brenca case identities (CLOSED-unresolved), Urbini Table 1 via mdpi.com (blocked), PUB-EMC-CLASSIFICATION (user-rejected), Hofvander/EGA, paired Davis validation.

## Method / inputs

Committed artifacts and prose read at `b9a0257e`:

| input | what it supplied |
|---|---|
| `research/modalities/emc-cohort-search-inputs.json` | the GEO census: 56 records (21 GSE series with `series_samples` sample-level reads), each series' `n_samples` and full GSM title/summary list. Query provenance `_found_by: "extraskeletal myxoid chondrosarcoma"[All Fields]` |
| `research/modalities/emc-sra-study.json` | `PRJNA1357027` / `SRP640302`: `runs.n_runs 12`, `n_distinct_samples 12`, `assay_probes.tempo_seq.matched true`, `targeted_panel.matched true`, `wgs_wxs.matched false` |
| `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md` (§ lines 192-194, 856-871) | per-deposit EMC counts and the "17 other deposits, 0 EMC in every one, read at sample level" census |
| `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-SI.md` | Filion 2009 = 3 fusion-positive EMC vs 137 sarcomas |
| `research/manuscripts/emc_fusion_partner_pooling.py` | Davis 2017 `design: "molecular profiling series (6 EMC)"`; Sjögren 2003 registered as a *fusion-prevalence* source only |
| `research/manuscripts/aso_coverage_ladder.py:188` | Urbini 2018 `n=5` |
| `research/manuscripts/aso/fusion-junction-aso-paper-redteam-round5.md:142` | Mod Pathol 2023: RNA exome sequencing on **three** of the 58-case denominator |
| `research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md:174` | the competing prose claim "GSE43632 (1), GSE80126 (1)" EMC |
| `research/autonomy/opus-capacity-campaign-20260908/WAVE-LOG.md:80-86` | the owner's Brenca closure, transcribed |

Tool: `python3` (3.11.15) under `/tmp/claude-0/w01e/`. No network, no MCP, no WebSearch, no WebFetch.

## Result

### R1 — Per-study re-derivation, W01c vs committed data at `b9a0257e`

Machine output of `/tmp/claude-0/w01e/rederive.py` (exit 0, assertions passed):

| # | study | n W01c | n re-derived | W01c class | re-derived class | grade |
|---|---|---|---|---|---|---|
| 1 | Sjögren 2003 (12598313) | 2 | — | PRE-DEPOSITION ERA | **NOT RE-DERIVABLE** | UNKNOWN |
| 2 | Subramanian 2005 (15920699) | 10 | **10** | PUBLIC GSE4303 | PUBLIC GSE4303 | PRIMARY (artifact) |
| 3 | Filion 2009 (18855877) | 3 | **3** | UNKNOWN (no DAS) | UNKNOWN (no DAS) | PRIMARY (n) / UNKNOWN (class) |
| 4 | Möller 2011 (21536545) | 6 | **6** | PUBLIC GSE24369 | PUBLIC GSE24369 | PRIMARY (artifact) |
| 5 | Brunner 2012 (22929540) | 4 | **4** | PUBLIC GSE28866 | PUBLIC GSE28866 | PRIMARY (artifact) |
| 6 | Davis 2017 (28423517) | 6 | **6** | BY REQUEST ONLY | BY REQUEST — n confirmed, class not re-derivable | PRIMARY (n) / SECONDARY (class) |
| 7 | Urbini 2018 (29937513) | 5 | **5** | UNKNOWN (no DAS) | UNKNOWN (no DAS) | PRIMARY (n) / UNKNOWN (class) |
| 8 | Brenca 2019 (31020999) | 12 | **12** | DEPOSITED, ACCESSION UNRECOVERABLE | ⭐ **PUBLIC — PRJNA692081 / SRP301712** | SECONDARY (owner closure) |
| 9 | *Genes Chrom Cancer* 2022 (35932215) | 1 | — | UNKNOWN | **NOT RE-DERIVABLE** | UNKNOWN |
| 10 | *Mod Pathol* 2023 (36948401) | 3 | **3** | UNKNOWN | UNKNOWN | PRIMARY (n) |
| 11 | Chaiboonchoe 2026 (42465974) | 12 | **12** | PUBLIC PRJNA1357027 | ⚠ PUBLIC PRJNA1357027 — **TARGETED PANEL, not transcriptome-wide** | PRIMARY (artifact) |
| 12 | Unnamed GEO cartilaginous series | 19 | — | PUBLIC, ACCESSION UNRESOLVED | ⚠ **NOT CORROBORATED by the committed GEO census** | UNKNOWN |
| 13 | Hofvander TAF15 case | 1 | — | CONTROLLED ACCESS (EGA) | **NOT RE-DERIVABLE** | UNKNOWN |

**Reproducibility verdict: 8 of 13 rows have a specimen count reproducible from committed data; 4 of 13 have a deposit class reproducible from committed data.** The four are rows 2, 4, 5, 11 — precisely the "PUBLIC, accession known" class. **Every one of the 52 non-obtainable specimens rests on a class that committed data cannot reproduce.** That is the direct answer to the dispatched question: what makes the 32 obtainable is that a GEO/SRA accession with EMC-labelled sample records is held in this repository's own artifacts; what makes the other 52 not obtainable is, in every case, a statement in an article's prose (or its absence) that no committed artifact independently attests.

### R2 — The five disagreements with W01c

**D1 (material, moves the band). Row 12, the unnamed 19-EMC GEO cartilaginous-tumour series, is not corroborated by this repository's own sample-level GEO census — and is in tension with it.** `emc-cohort-search-inputs.json` was built from the full disease name (`"extraskeletal myxoid chondrosarcoma"[All Fields]`) and holds sample-level GSM reads for 21 series. Machine census (`/tmp/claude-0/w01e/geo_census.txt`):

```
acc          n_samples  gsm_read emc_titled  title
GSE4303             36        36         10  Gene expression profile of extraskeletal myxoid chondrosarco
GSE24369            42        42          6  Gene expression profiling of low-grade fibromyxoid sarcoma (
GSE28866            99        99          4  Transcriptional profiling of lncRNAs and novel transcribed r
...
series with >=100 samples: ['GPL1261', 'GPL570', 'GPL8300', 'GPL96']   # platforms, not series
```

**No series carries 19 EMC-titled samples; the largest EMC-bearing series carries 10; and no GSE record in the census has ≥100 samples**, whereas row 12 requires 19 + 128 = **147**. This is UNKNOWN, not proof of absence — the census is one bounded query set and cannot see an SRA-only or differently-titled deposit — but it removes the only independent support row 12 could have had inside this repository, and it is consistent with W01b's separate arithmetic objection (`E-MTAB-7264` ≈ 102 ≠ 147).

**D2 (material, asymmetric inclusion criterion). Row 11 is a targeted panel by this repository's own measurement.** `emc-sra-study.json` records `targeted_panel.matched: true` / `tempo_seq.matched: true` / `wgs_wxs.matched: false`, and `emc-atr-vulnerability-assessment.md:872` states it verbatim: *"whole-transcriptome **targeted TempO-Seq** rather than transcriptome-wide."* W01c excluded **PMID 41644428 (16 EMC)** on the ground that whole-transcriptome status "was not established", while including row 11 under the vendor product name "TempO-Seq Human Whole Transcriptome 2.0". **The criterion is applied asymmetrically**, and it is applied in the direction that favours the obtainable numerator: row 11 supplies 12 of the 32.

**D3 (non-material, but a committed-data contradiction worth recording).** `emc-mtap-prmt5-hypothesis.md:174` states five GEO series carry EMC-titled samples including *"GSE43632 (1), GSE80126 (1)"*. The artifact refutes this: GSE43632's 18 GSMs are titled `Sample <id>` with summaries `Patient <id>` (no EMC token), GSE80126's 29 GSMs are cell lines and normal organs — **0 EMC-titled in each**, matching `nr4a3-fusion-transcriptional-output.md:858` (*"0 in every one … read at sample level"*). **Resolved conservatively against adding**: I do not add 2 specimens to the inventory. Reported because two committed documents disagree.

**D4 (non-material). Row 13's EGA class has no committed anchor.** The only EGA accession anywhere in the tree is `EGAS00001002795`, which is **Haller 2019 acinic cell carcinoma (native NR4A3), not EMC**. Row 13 rests entirely on one line of `CLOSED-WORK.md`. W01c already graded it SECONDARY; I confirm there is nothing behind it in the repository.

**D5 (non-material, flagged not resolved). Possible two-paper conflation at row 10.** The repository carries PMID 36948401 as **Huang 2023** (`repurposing-hypotheses.md:591`, `n=58`, TAF15::NR4A3), while the "pan-Trk-expressing cases → RNA exome sequencing" material is attributed to **`warmke2023`** in `research/hypotheses/candidates.json:485`; `emc-post-degrader-options.md:359` records an attribution correction here in 2026-08-08. n = 3 is confirmed either way and the class is UNKNOWN either way, so the band does not move. Flagged for the lane, not resolved.

**Explicitly NOT a disagreement:** W01c's arithmetic corroboration of row 4 (6 EMC + 36 comparators = 42) **holds** — the artifact records GSE24369 at 42 samples with 6 EMC-titled. (The manuscript's prose breakdown names only 31 of the 36 comparators; that is an incomplete description, not an error in the count.)

### R3 — Brenca's inventory row: CORRECTED, and it is a DUPLICATE recovery

**W01c's row 8 status `DEPOSITED, ACCESSION UNRECOVERABLE` is NO LONGER ACCURATE.** Corrected status: **`DEPOSITED — accession known and public: PRJNA692081 / SRP301712`**, established by the correction to *J Pathol* (DOI `10.1002/path.5737`, PMID `34216030` / `PMC8451045`) and retained in `research/autonomy/nr4a3-patient-junction-source-2026-09-07/`.

- **Provenance class: DUPLICATE.** This corrects an inventory row. It adds no source, and I recovered nothing — I attempted no route. Graded **SECONDARY (owner closure, transcribed from `WAVE-LOG.md:80-86`)**, and explicitly **not re-derivable at this HEAD**, where the directory is absent. W01b's fourteen-route negative stands as an accurate record of what was reachable *before* the correction was known.
- **⚠ Specimen count deliberately left at 12, the paper-stated EMC case count.** The deposit reportedly holds **23 paired libraries / 46 FASTQ links**, of which **8 are engineered E-N/T-N aliases** and **15 are biological-origin-unresolved**. I do **not** enter 23, and I do **not** enter 15. **15 unresolved libraries are not 15 patients, and libraries are not specimens.** Counting anything above 12 here would inflate the numerator on exactly the assumption the owner's closure forbids.
- **This supports no cohort, independence or patient claim.** W01d's tier-D UNKNOWN on Urbini-vs-Brenca nesting is untouched: an accession does not resolve case identity, which remains CLOSED-unresolved.

### R4 — Corrected band

```
W01c point total (specimens)                              : 84
W01c obtainable band                                      : 32 - 51

[A] Brenca reclassified PUBLIC (owner closure)            : obtainable = 44
    band, row 12 unresolved -> resolved+open              : 44 - 63
[C] if the 'established whole-transcriptome' criterion is applied to row 11 as W01c applied
    it to PMID 41644428, row 11 (targeted panel) leaves   : 32 - 51
```

> ### W01c's and W01d's headline "32–51 obtainable" is CORRECTED to **44–63 obtainable**, out of an unchanged **60–84** generated.

W01d's stated reason for leaving the obtainable number untouched — *"neither Urbini nor Brenca contributes a single specimen to the obtainable class"* — was true of Urbini and is **now false of Brenca**. The correction is +12 specimens, roughly **+27 % on the floor**, and it raises the share of the world's EMC expression specimens this program can reach without writing to a human from ~38 % to ~52 % of the 84-specimen point estimate.

Note the coincidence, which is not an argument for either value: applying D2's criterion consistently would take the band back to exactly 32–51 by a different route (44 − 12). The two corrections are independent and happen to cancel.

### R5 — The single highest-leverage classification decision

**Row 12 — the unidentified 19-EMC GEO cartilaginous-tumour series.** Specimens moved by a single reclassification:

| decision | specimens moved |
|---|---|
| **row 12 (unnamed 19-EMC GEO series)** | **19** |
| row 8 Brenca | 12 |
| row 11 whole-transcriptome vs targeted-panel criterion | 12 |
| row 6 Davis | 6 |

Row 12 alone is the entire width of the obtainable band (44 → 63) and, in W01c's original framing, was the entire width of 32 → 51. It is also the only row that is simultaneously (a) the largest single EMC specimen block in the inventory, (b) claimed public by a third party's Methods, and (c) contradicted by nothing but supported by nothing in this repository. **That is where the next real work is** — and, unlike W01d's successor, it does not require mdpi.com.

## Validation evidence

**RUN.** Environment: Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]; Linux 6.18.44-fc-v24 x86_64; cwd `/tmp/claude-0/w01e`, outside the repository. No network in any command.

| # | command | exit | key output |
|---|---|---|---|
| 1 | `date -u`; `env \| grep -i -E 'claude\|anthropic\|model' \| sed …`; `git rev-parse HEAD`; `git status --porcelain` | 0 | start `02:27:55 UTC`; HEAD `b9a0257e…`; env above |
| 2 | `git ls-files \| grep -i -E 'junction-source\|brenca'` | 0 | one file (W01b's report). **The Brenca correction directory is absent at this HEAD** |
| 3 | `rg -n -i --glob '!.git' -e 'PRJNA692081' -e 'SRP301712' -e 'path\.5737' …` | 0 | 4 hits; the accessions appear only in `WAVE-LOG.md:82-84` |
| 4 | `for p in 12598313 … 42465974; do rg -c -i "$p" …` | 0 | every PMID except `35932215` is cited in the tree outside the campaign directory (6–73 files); `35932215` → **0** |
| 5 | `python3` walk of `emc-cohort-search-inputs.json` `series` / `series_samples` | 0 | GSE4303 36/10 EMC; GSE24369 42/6; GSE28866 99/4; GSE43632 18/**0**; GSE80126 29/**0** |
| 6 | `python3 … geo census` → `/tmp/claude-0/w01e/geo_census.txt` | 0 | 56 records, 21 series with sample reads; **no series ≥100 samples; max EMC-titled = 10** (verbatim excerpt in D1) |
| 7 | `python3 -c` probe of `emc-sra-study.json` | 0 | `"runs": {"n_runs": 12, "n_distinct_experiments": 12, "n_distinct_samples": 12 …}`; `"targeted_panel": {"matched": true, "matched_text": "Targeted"}`; `"wgs_wxs": {"matched": false}` |
| 8 | `cd /tmp/claude-0/w01e && python3 rederive.py; echo "EXIT=$?"` | **0** | the full table in R1 and the band in R4; **`ASSERTIONS PASSED`** (5 assertions: W01c total = 84, 32+19 = 51, corrected obtainable = 44, corrected ceiling = 63, row 12 is the max-leverage decision) |
| 9 | `date -u`; `git rev-parse HEAD`; `git status --porcelain \| grep -v opus-capacity-campaign` | grep 1 (no match) | end `02:32:20 UTC`; HEAD moved to `47aac85f…` by the coordinator; **no tree writes by me** |

**PROPOSED (NOT RUN):**
- Resolve row 12 by querying GEO for a ~147-sample cartilaginous-tumour expression series. **Not run** — no network was used in this run at all, and the reliable route is the Actions escape hatch, not this sandbox.
- Re-read the PeerJ reference list to identify row 12's accession. **Not run, deliberately** — W01b and W01c both established the PMC renderer strips it, and W01c's R4 established the WebSearch-summarizer route is *demonstrably untrustworthy for identifier recovery*. Replaying it would replay a route already recorded as unreliable.
- Any Brenca accession or route recovery. **Not run** — DUPLICATE per the owner's binding closure.

**No test suite was run** and `scripts/preflight.sh` was not invoked: this run changes no code, no manuscript and no shared state, and the dispatch does not call for it. Nothing here is a skipped check reported as a pass.

## Limitations

- **Specimens, not patients. Arrays are not patients. Runs are not patients. Libraries are not specimens.** Every number in R1 and R4 counts profiled specimens as stated by a publication or an archive record. **No cohort is asserted, and no patient-level deduplication exists** for any pair except GSE4303 / GSE28866.
- **The re-derivation's "obtainable" class is a ceiling on availability, not on usability.** 44 counts specimens whose accession is public; it does not assert that a usable expression matrix, or any fusion-type annotation, comes with them. For Brenca specifically the deposit's biological composition is *unresolved by the owner's own gate* — 8 engineered, 15 unresolved of 23 libraries — so at most 15 of the 12 counted specimens could correspond to tumour material, and even that correspondence is UNKNOWN.
- **Brenca's corrected row is SECONDARY and cannot be verified at this HEAD.** The supporting directory is not in this checkout. I accept the owner's closure as authoritative and flag that the coordinator should re-verify the row against `retrieval.json` when the two branches are integrated.
- **D1 is a non-corroboration, not a refutation.** The committed GEO census is one bounded query set from 2026-08; a series titled without the disease name, or an SRA-only or ArrayExpress deposit, is invisible to it. **An absent record is UNKNOWN, not zero.**
- **Rows 1, 9 and 13 could not be re-derived at all** — their specimen counts and classes are W01c's readings, transferred, and this run neither confirms nor disputes them.
- **D2 identifies an inconsistency; it does not settle which side is right.** I do not assert that row 11 should leave the inventory, only that the criterion currently admits it and excludes PMID 41644428 on the same evidential footing.
- **D5 is flagged, not resolved.** Settling the Huang/Warmke attribution needs a full text this run did not fetch.
- **No clinical claim.** Nothing here bears on EMC efficacy, safety, selectivity, prognosis or clinical readiness. Deposit availability is a data-access fact, not a scientific result.

## Stop condition

**Set:** a per-study re-derived classification with disagreements against W01c named explicitly, Brenca's inventory row corrected or confirmed, and the single highest-leverage classification decision identified.

**MET.** All 13 rows re-derived from committed data with the reproducibility of each stated (8/13 counts, 4/13 classes); **five disagreements named** (D1 row 12 non-corroboration, D2 row 11 asymmetric assay criterion, D3 a committed-data contradiction over GSE43632/GSE80126, D4 row 13's absent EGA anchor, D5 a possible row 10 attribution conflation), with one candidate disagreement checked and **withdrawn** (row 4's arithmetic corroboration holds); **Brenca's row corrected** to `PUBLIC — PRJNA692081 / SRP301712`, classified DUPLICATE, count held at 12; **band corrected 32–51 → 44–63**; and **row 12 identified as the single highest-leverage decision at 19 specimens**. Returning immediately; no padding.

## Tool-call and wall-clock count actually used

**15 tool calls** (all Bash; zero MCP, zero WebSearch, zero WebFetch, zero network) against the ~40 target. **Wall clock 4 min 25 s** (`02:27:55` → `02:32:20` UTC) against the ~40-minute target.

## Next concrete action

**Identify row 12 — the publicly deposited cartilaginous-tumour expression series containing 19 EMC tumours — by an archive query rather than by reading the PeerJ reference list.** The bibliographic route is closed twice over (PMC strips the reference list; the WebSearch summarizer is proven unreliable for identifiers by W01c's own control), but the *archive* route has never been tried for this row: a GEO/ArrayExpress query for a ~147-sample cartilaginous-tumour expression series, cross-checked against the committed census's 56 records, would either name the accession or establish that no such series is reachable. This is worth roughly 19 specimens — the whole width of the corrected band, and more than any other single decision in the inventory — and it needs the GitHub Actions escape hatch (~15 min, no spending), where it can share a runner job with the Europe PMC `accessionIds` query W01b already queued. **It does not require mdpi.com and is therefore not blocked by W01d's blocker.**

A cheap second item for whoever holds the lane, requiring no network: **settle D2 by deciding, once, whether a targeted probe panel counts as "whole-transcriptome" in this inventory, and apply that decision to row 11 and PMID 41644428 together.** As it stands the inventory admits a 12-specimen targeted panel and excludes a 16-specimen series on the same evidential footing, in the direction that flatters the obtainable number.
