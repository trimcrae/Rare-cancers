> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: inventory script re-runs at exit 0 with assertions passing, all 13 rows trace to a PubMed record I retrieved this session, no writes to the Git tree (`git status` shows only other workers' campaign reports), disk 24 GiB free, nothing downloaded. Report follows.

---

# W01c — Literature-derived inventory of EMC whole-transcriptome datasets and their availability

## Worker

- **Worker:** W01c, Lane 1 refill (public EMC tumour expression / multiomics resources).
- **Model identity: SELF-REPORT, not independently verified.** I report myself as Claude Opus 5 (`claude-opus-5`). No served-model identity was observed; `env` exposes no variable naming a model. The coordinator must extract the actual runtime model from the transcript.
- **`date -u` start:** `Tue Sep  8 02:07:58 UTC 2026`. **End:** `Tue Sep  8 02:12:30 UTC 2026`.
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** (exit 0). No variable names a model. Full literal output, long proxy lines marked:

```
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1
CLAUDE_CODE_ACCOUNT_UUID=4c503081-e4c3-45a1-8002-1cb705f46605
CLAUDE_CODE_CHILD_SESSION=1
no_proxy=<long host list, elided — no model named>
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
JAVA_TOOL_OPTIONS=<proxy/truststore flags, elided — no model named>
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

- **Disk, checked first:** start `252G / 12G used / 27G avail / 30%`; end `24G avail / 36%`. Far above the ≥10 GiB floor. **Nothing was downloaded.**
- **Write isolation honoured:** zero writes to the Git tree. `git status --porcelain` filtered of the campaign directory returned empty. Note HEAD has moved during my run (`92abbcb9` → `103ff76f`) and three new untracked files appeared (`W02b`, `W06b`, `W19b` reports) — those are the coordinator and sibling workers, not me. Execution and both scratch files were under `/tmp/claude-0/W01c/`.
- **No archive or bibliographic API was contacted.** Per the dispatch, the transport branch is closed; I did not re-probe a single one of W01b's fourteen routes. Channels used: PubMed MCP and WebSearch only.

## Question

**Pursued exactly as dispatched:** *Using the published literature rather than the archives, what is the complete inventory of EMC whole-transcriptome / genome-wide expression datasets that have ever been **generated**, and for each, what does the literature itself say about its availability?* And the pair of numbers the program needs: how many EMC tumours have ever been whole-transcriptome profiled worldwide, and how many of those are obtainable without correspondence?

**Why it is open.** W01 built an inventory of what this repository *retains*; W01b proved the archives cannot be asked. Neither built the inventory of what was ever *generated*. That denominator has never existed in this project, and it is the quantity that decides whether the program's expression evidence is near-complete or is missing most of the world's data. It is answerable from papers alone, because a methods section states that a dataset exists and a data-availability section states what became of it.

## Prior-work check

Read in full before acting: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `reports/W01-expression-multiomics-resources.md`, `reports/W01b-brenca-accession-recovery.md`.

Commands run (read-only) and what they showed:

| command | result |
|---|---|
| `for t in 18855877 12598313 29937513 36948401 35932215 41315062 Filion Sjogren Sjögren Urbini; do rg -c -i --glob '!.git' "$t" . ; done` | Every one of these PMIDs is **already cited somewhere in the tree** (17–71 files each). None is new literature. |
| `rg -n -i "29937513\|18855877\|12598313" --glob '!.git' .` | **The decisive finding.** `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output-SI.md:123` cites Filion 2009 as *"Affymetrix U133A microarray, 3 fusion-positive EMC vs 137 other sarcomas"* — a gene-level read. `research/manuscripts/aso_coverage_ladder.py:188` cites Urbini 2018 as a fusion-exon cohort, *"PMID 29937513, n=5"*. `aso_coverage_ladder.py:59` even asks whether *"cohorts that COUNT a TCF12 tumour (PMID 12598313, 24746215, 36948401) deposited anything"* — the question was framed and never answered. |
| `git rev-parse HEAD`; `git status --porcelain` | Isolation check, above. |

**What this establishes:** every study in my inventory is a **known citation of this repository whose dataset was never recorded as a data resource** — the identical pattern W01 found for Brenca. This is not new literature; it is a new *reading* of literature already in the corpus. I say that plainly rather than claiming discovery.

**Closed items confirmed not replayed.** I did not re-probe any archive or bibliographic API (all fourteen W01b routes untouched). I did not attempt Brenca's case identities or Hofvander's EGA access. I did not re-read GSE4303/GSE28866 headers or re-derive W01's `STT` overlap. I did not touch the NR4A Perspective refusal. Methylation (`GSE140686`) is excluded from the inventory as deprioritized *and* because it is not expression.

## Method / inputs

- **Tools:** PubMed MCP (`search_articles`, `get_article_metadata`, `get_full_text_article`); WebSearch; Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0] on Linux 6.18.44-fc-v24 x86_64; ripgrep 14.x; `jq`.
- **PubMed queries run:** `extraskeletal myxoid chondrosarcoma gene expression profiling` (53 records); `extraskeletal myxoid chondrosarcoma transcriptome RNA sequencing` (15); `extraskeletal myxoid chondrosarcoma cDNA microarray molecular pathogenesis` (2); `Davis extraskeletal myxoid chondrosarcoma sequencing` (1).
- **Full texts retrieved and swept:** `PMC13374579` (Chaiboonchoe 2026), `PMC6073125` (Urbini 2018), `PMC4429309` (Filion 2009), `PMC5400622` (Davis 2017).
- **Attribution.** According to PubMed: Sjögren *et al.*, *Am J Pathol* 2003, PMID 12598313, PMC1868116 [DOI](https://doi.org/10.1016/S0002-9440(10)63875-8); Subramanian *et al.*, *J Pathol* 2005, PMID 15920699 [DOI](https://doi.org/10.1002/path.1792); Filion *et al.*, *J Pathol* 2009, PMID 18855877, PMC4429309 [DOI](https://doi.org/10.1002/path.2445); Möller *et al.*, *Clin Cancer Res* 2011, PMID 21536545 [DOI](https://doi.org/10.1158/1078-0432.CCR-11-0145); Brunner *et al.*, *Genome Biol* 2012, PMID 22929540 [DOI](https://doi.org/10.1186/gb-2012-13-8-r75); Davis *et al.*, *Oncotarget* 2017, PMID 28423517, PMC5400622 [DOI](https://doi.org/10.18632/oncotarget.15568); Urbini *et al.*, *Int J Mol Sci* 2018, PMID 29937513, PMC6073125 [DOI](https://doi.org/10.3390/ijms19071855); Brenca *et al.*, *J Pathol* 2019, PMID 31020999, PMC6766969 [DOI](https://doi.org/10.1002/path.5284); *Genes Chromosomes Cancer* 2022, PMID 35932215 [DOI](https://doi.org/10.1002/gcc.23086); *Mod Pathol* 2023, PMID 36948401 [DOI](https://doi.org/10.1016/j.modpat.2023.100162); *Virchows Arch* 2025, PMID 41315062 [DOI](https://doi.org/10.1007/s00428-025-04252-w); Chaiboonchoe *et al.*, *PeerJ* 2026, PMID 42465974, PMC13374579 [DOI](https://doi.org/10.7717/peerj.21497).
- **Counting:** `inventory.py`, returned inline below, run in `/tmp/claude-0/W01c/`. No network, no repository write.

## Result

### R1. The inventory — every EMC genome-wide expression dataset the literature says was generated

`n EMC` is the number of EMC specimens each paper states were **profiled**, never the number diagnosed or FISH-confirmed. Sorted by year.

| # | Study | Year | n EMC profiled | Platform | Availability class | Justifying evidence | Grade |
|---|---|---|---|---|---|---|---|
| 1 | Sjögren *et al.*, *Am J Pathol* (PMID 12598313) | 2003 | **2** (of a 10-EMC clinical series) | cDNA microarray | `STATED UNAVAILABLE / PRE-DEPOSITION ERA` | Abstract, verbatim: *"cDNA microarray analysis of the gene expression patterns of **two EMCs** and a myxoid liposarcoma reference tumor…"*. Availability class rests on the PeerJ sentence quoted in R2, plus the absence of any GEO-era deposit statement | PRIMARY (n); SECONDARY (availability) |
| 2 | Subramanian *et al.*, *J Pathol* (PMID 15920699) | 2005 | **10** | 42,000-spot two-colour cDNA, GPL3290 | `PUBLICLY DEPOSITED (accession known)` — **GSE4303** | Repository-retained deposit (W01 R1); heavily analysed here. **RETAINED** | PRIMARY |
| 3 | Filion *et al.*, *J Pathol* (PMID 18855877) | 2009 | **3** | Affymetrix U133A (22,215 probe sets) | `UNKNOWN` | Methods, verbatim: *"**Three** snap-frozen EMC tumor samples were obtained with institutional review board approval from patients operated at Memorial Sloan-Kettering Cancer Center (MSKCC)."* A whole-text sweep for *available / deposit / accession / GEO / SRA / repository / Availability / upon request* found **no data-availability statement of any kind** — every "available" hit is about drugs or cell lines | PRIMARY |
| 4 | Möller *et al.*, *Clin Cancer Res* (PMID 21536545) | 2011 | **6** | Affymetrix Gene ST, GPL6244 | `PUBLICLY DEPOSITED (accession known)` — **GSE24369** | Repository-retained (W01 R1). Independently corroborated this session: the PeerJ Methods describe their first external cohort as *"EMC tumors (= 6) against other soft-tissue sarcoma (STS) subtypes (= 36)"*, and 6 + 36 = 42 = GSE24369's deposited sample count. **RETAINED** | PRIMARY |
| 5 | Brunner *et al.*, *Genome Biol* (PMID 22929540) | 2012 | **4** | 3SEQ, GPL10999 | `PUBLICLY DEPOSITED (accession known)` — **GSE28866** | Repository-retained (W01 R1). **RETAINED** | PRIMARY |
| 6 | Davis *et al.*, *Oncotarget* (PMID 28423517) | 2017 | **6** | MI-ONCOSEQ: exome + PolyA+ and capture transcriptome | `OBTAINED ONLY BY REQUEST` | Two sentences carry this. Davis's own Results: *"Additional detailed molecular profiling information is available in **Supplementary Materials**."* — no accession anywhere in the full text. And the PeerJ Methods, verbatim: *"**Through a formal request to the journal editors, we obtained** both the whole-transcriptome expression matrices and the matched clinical data for the six EMC cases profiled using the MI-ONCOSEQ platform by[Davis]."* | PRIMARY |
| 7 | Urbini *et al.*, *Int J Mol Sci* (PMID 29937513) | 2018 | **5** | Illumina WTS, 2 × 80 bp paired-end | `UNKNOWN` | Results, verbatim: *"**WTS was performed on five cases of EMC** positive for-fusion."* Whole-text sweep for deposit/accession/repository/availability terms: **every hit is a software URL** ("AdapterRemoval (available online:)", "Samtools (available online:)"…). **No data-availability statement exists in this article.** MDPI's own "Supplementary Materials" section carries no deposit | PRIMARY |
| 8 | Brenca *et al.*, *J Pathol* (PMID 31020999) | 2019 | **12** (7 `EWSR1::NR4A3`, 5 `TAF15::NR4A3`) | Illumina HiSeq 1000 WTS, ~70M PE reads/sample | `DEPOSITED BUT ACCESSION UNRECOVERABLE FROM HERE` | Data-availability sentence, verbatim and complete as rendered: *"Raw and processed sequencing data are available at."* The identifier is stripped by the PMC renderer. **Fourteen routes exhausted by W01b.** **RETAINED** as candidate | PRIMARY (paper) / UNKNOWN (deposit) |
| 9 | *Genes Chromosomes Cancer* (PMID 35932215) | 2022 | **1** (case report, `LSM14A::NR4A3`) | whole-transcriptome sequencing | `UNKNOWN` | Abstract states whole-transcriptome sequencing of the case; not in PMC, no data-availability text retrievable from here | PRIMARY (n) / UNKNOWN (availability) |
| 10 | *Mod Pathol* (PMID 36948401) | 2023 | **3** (of 58 FISH-confirmed EMCs) | RNA exome sequencing | `UNKNOWN` | Abstract, verbatim: *"**Three** challenging pan-Trk-expressing cases … were subjected to **RNA exome sequencing (RES)**, unveiling different NR4A3-associated fusions."* The other 55 had FISH/IHC only, not expression. Not in PMC | PRIMARY (n) / UNKNOWN (availability) |
| 11 | Chaiboonchoe *et al.*, *PeerJ* (PMID 42465974) | 2026 | **12** | TempO-Seq Human Whole Transcriptome 2.0, FFPE | `PUBLICLY DEPOSITED (accession known)` — **PRJNA1357027 / SRP640302** | Methods, verbatim: *"Raw sequencing data have been deposited in the NCBI Sequence Read Archive (SRA) under BioProject accession."* (identifier stripped by the renderer; resolved by W01/W01b). **RETAINED** | PRIMARY |
| 12 | **Unidentified GEO microarray series of cartilaginous tumours** | — | **19** | microarray | `PUBLICLY DEPOSITED` **but accession UNRESOLVED from here** — see R3 | PeerJ Methods, verbatim: *"we performed cross-study analyses using two independent, **publicly available** microarray datasets from the Gene Expression Omnibus (GEO)… The second dataset,[accession], directly compares **EMC tumors (= 19)** against a broad background of other chondrosarcomas (= 128)."* | PRIMARY (existence + public status) / UNKNOWN (identity) |
| 13 | Hofvander — one `TAF15` case | — | **1** | sequencing | `DEPOSITED, CONTROLLED ACCESS (EGA)` | Repository record only (`CLOSED-WORK.md`: *"Hofvander: one TAF15 case, raw data controlled-access via EGA"*). Not re-derived; explicitly left as it stands | SECONDARY (repository record) |

**Excluded, with reasons:** `GSE140686` (methylation, not expression; deprioritized); `SRP445369` / PMID 39086683 (whole **genome**, not transcriptome); `GSE243553` and `GSE11185` (engineered HEK293/HEK293T cells, no patients); PMID 41644428 (16 EMC, Chinese multi-centre 2026 — NGS stated but not established as whole-transcriptome, so counting it would inflate the numerator on an assumption); PMID 41315062 (*Virchows Arch* 2025 `HSPA8::NR4A2`, 1 case — comprehensive genomic profiling reported, whole-transcriptome not established). **These two exclusions are conservative and are a known source of under-count; see Limitations.**

### R2. The verbatim availability sentence that governs the whole inventory

The PeerJ paragraph, retrieved in full this session from `PMC13374579`. Citation markers are stripped by the PMC renderer and are shown as `[…]`:

> "**Cross-study comparison and external cohort evaluation.** To contextualize the identified prognostic candidates within the existing extraskeletal myxoid chondrosarcoma (EMC) transcriptomic literature, we reviewed prior molecular profiling efforts. Early studies by[…]and[…]utilized cDNA microarrays; however, **these datasets were generated prior to routine public deposition and are unavailable for reanalysis**. While[…]and[…]also conducted molecular profiling of EMC, **whole-transcriptome expression matrices were not readily accessible in public repositories** (;;;).
>
> **Through a formal request to the journal editors, we obtained** both the whole-transcriptome expression matrices and the matched clinical data for the six EMC cases profiled using the MI-ONCOSEQ platform by[Davis]. Although overall survival data were available for this cohort, the cases exhibited profound clinical heterogeneity…"

This is a published third party's account of systematically attempting to obtain exactly the datasets in R1, and it is the strongest availability evidence in the inventory — stronger than any archive query, because it reports an *outcome of trying*, not an absence of a record.

### R3. Following the PeerJ trail — what resolved, and what did not

**Resolved, with the evidence:**

| PeerJ reference | Resolved to | How |
|---|---|---|
| The MI-ONCOSEQ study, "six EMC cases … by[Davis]" | **Davis EJ, Wu Y-M, Robinson D, Schuetze SM, Baker LH, Athanikar J, Cao X, Kunju LP, Chinnaiyan AM, Chugh R. "Next generation sequencing of extraskeletal myxoid chondrosarcoma." *Oncotarget* 2017;8(13):21770–7. PMID 28423517, PMC5400622** [DOI](https://doi.org/10.18632/oncotarget.15568) | PubMed search returned exactly **one** record for Davis + EMC + sequencing. Its abstract states *"six patients with EMC participated in the clinical sequencing research study"*, University of Michigan / Michigan Center for Translational Pathology (the MI-ONCOSEQ home institution), *"tumor PolyA+ and capture transcriptome"*. Every particular matches. **Unambiguous.** |
| First external GEO dataset, "EMC (= 6) vs other STS (= 36)" | **GSE24369** (Möller 2011) | Arithmetic identity with the repository-retained deposit: 6 EMC + 36 comparators = 42 deposited samples, exactly W01 R1's record for GSE24369. |

**NOT resolved, and I will not guess:**

- **The two "early cDNA microarray" studies `[X]` and `[Y]`.** Sjögren 2003 is a near-certain fit on platform and era. The obvious second candidate, Subramanian 2005, **contradicts the sentence** — it used 42,000-spot cDNA microarrays *and* is deposited as GSE4303, so it cannot be one of the datasets called "unavailable for reanalysis". Either PeerJ's characterisation is imprecise or `[Y]` is a study I have not identified. **Unresolved.**
- **The two studies `[Z]` and `[W]` whose "whole-transcriptome expression matrices were not readily accessible".** Four citations `(;;;)` sit at that sentence. Brenca 2019, Urbini 2018 and Davis 2017 all fit the description on independent grounds (R1 rows 6, 7, 8 each lack a usable public matrix). **But I did not verify it and I do not assert it.**
- **Why they cannot be resolved.** The PeerJ reference list is **absent from the PMC rendering entirely** — I dumped the full 81,024-character text and its tail is the supplementary-figure legends, with no bibliography. Matched context fails because the renderer strips the markers themselves, not just the entries. W01b already established that peerj.com and every bibliographic API are blocked. **The branch is closed by the same renderer defect W01b diagnosed, and I confirm that diagnosis independently.**

### R4. ⚠ A negative control that matters — the WebSearch accession is NOT usable

I attempted to recover the second GEO accession (R1 row 12) via WebSearch, on the reasoning that the search summarizer reads the pmc.ncbi.nlm.nih.gov HTML that the MCP renderer strips. Two searches — including one that did **not** name any accession in the query — both returned *"GSE24369 and **GSE6481**"* as the two accessions in the PeerJ Methods, and GSE24369 is independently verifiable as correct, which looked like a strong internal control.

**So I ran a control query on the accession alone.** It returned an incompatible description:

> "The series title is *'Undifferentiated pleomorphic sarcoma recapitulates the expressional profile of Subtype II Leiomyosarcoma'*. Selected samples from GSE6481 included synovial sarcoma (16) and malignant peripheral nerve sheath tumor (3)… Platform: GPL96."

⛔ **A soft-tissue-sarcoma series on GPL96 is not a 147-specimen cartilaginous-tumour series.** The two summaries of the same accession are mutually inconsistent, so **GSE6481 is NOT established** and must not enter any inventory as the identity of row 12. The WebSearch summarizer is demonstrably capable of attaching a plausible accession to a description it was handed. **I report the accession as unresolved.** Recording this control is more valuable than the accession would have been: it means the "read the PMC HTML through the search summarizer" route, which looked like a way around the renderer, is **not trustworthy for identifier recovery** and should not be used by a successor worker for that purpose.

What survives, and is solid, is the *dataset's existence and public status*, which comes from PeerJ's own Methods sentence and not from any search summary: a publicly available GEO microarray dataset contains **19 EMC tumours**. That is larger than any EMC expression cohort this repository holds.

### R5. The two headline numbers

Measured by `inventory.py` (exit 0, assertions passed):

> **How many EMC tumours have ever been whole-transcriptome or genome-wide expression profiled worldwide, according to the published literature?**
> ### **84 specimens** (point estimate) — plausible range **60 – 84+**
>
> **How many of those are obtainable without correspondence?**
> ### **32 specimens** (accession known and public) — plausible range **32 – 51**

Decomposition:

| class | n specimens | studies |
|---|---|---|
| `PUBLICLY DEPOSITED (accession known)` | **32** | GSE4303 (10), GSE24369 (6), GSE28866 (4), PRJNA1357027 (12) |
| `PUBLIC per literature, accession UNRESOLVED here` | **19** | the unidentified GEO cartilaginous-tumour series |
| `DEPOSITED, ACCESSION UNRECOVERABLE` | 12 | Brenca 2019 |
| `OBTAINED ONLY BY REQUEST` | 6 | Davis 2017 |
| `UNKNOWN (no data-availability statement in the article)` | 8 | Filion 2009 (3), Urbini 2018 (5) |
| `UNKNOWN (full text unreachable)` | 4 | Mod Pathol 2023 (3), GCC 2022 (1) |
| `STATED UNAVAILABLE / PRE-DEPOSITION ERA` | 2 | Sjögren 2003 |
| `CONTROLLED ACCESS (EGA)` | 1 | Hofvander |
| **total** | **84** | 13 studies |

**Uncertainty, stated as bounds rather than an interval:**

- **Lower bound on the total, 60.** Obtained by assuming the worst case for the two largest correlations: Urbini 2018's 5 WTS cases are fully nested inside Brenca 2019's 12 (same senior author, Maestro; same Italian centres; both from the CRO Aviano / INT Milan axis — this is a *real* risk, not a hypothetical), **and** the unresolved 19-EMC GEO series is discounted entirely.
- **The total is a lower bound on the world, not an estimate of it.** It excludes two 2025–26 series (16 and 1 EMC) whose platform I could not establish as whole-transcriptome, any study without an English PubMed record, and any unpublished or commercial profiling. **84 is what the literature I could read says was generated; the true worldwide figure is ≥ 60 and unbounded above.**
- **⛔ These are specimens, not patients.** No deduplication across studies was possible for any pair except GSE4303 / GSE28866, where W01 computed a specimen-level intersection of zero. Patient-level overlap across all 13 studies is **UNKNOWN**.
- **The obtainable number is a ceiling on availability, not on usability.** 32 counts specimens whose accession is public; it does not assert that a usable expression matrix, or fusion-type annotation, comes with them.

### R6. What the pair of numbers means for the program

**At best 51 of 84, and quite possibly only 32 of 60, of the EMC tumours ever expression-profiled worldwide can be obtained without writing to a human being.** Between a third and a half of the world's EMC transcriptome evidence sits behind correspondence — one editor request (Davis), one stripped hyperlink (Brenca), and two papers that simply never wrote a data-availability sentence at all (Filion, Urbini).

That last category is the one this run adds and it is worth naming precisely: **for 8 of the 84 specimens, the barrier is not a paywall, not controlled access, and not a proxy — it is that the article contains no statement about the data.** A networked runner would not fix those; there is nothing to query.

⚠ And the corrective: `nr4a3-fusion-transcriptional-output.md` Limitation 7 says fusion type is unrecorded in every available series. **That remains exactly correct.** But this inventory shows the program is not merely missing a fusion-annotated series — it is holding roughly **38% of the world's EMC expression specimens** (32 of 84), a fraction it has never previously stated.

## Validation evidence

**RUN.** Environment: Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]; Linux 6.18.44-fc-v24 x86_64; cwd `/tmp/claude-0/W01c`, outside the repository. No network.

```
$ cd /tmp/claude-0/W01c && python3 inventory.py; echo "EXIT=$?"
rows: 13
    2  Sjogren 2003 (PMID 12598313)           PRE-DEPOSITION ERA
   10  Subramanian 2005 (PMID 15920699)       PUBLIC: GSE4303
    3  Filion 2009 (PMID 18855877)            UNKNOWN (no DAS in text)
    6  Moller 2011 (PMID 21536545)            PUBLIC: GSE24369
    4  Brunner 2012 (PMID 22929540)           PUBLIC: GSE28866
    6  Davis 2017 (PMID 28423517)             BY REQUEST ONLY
    5  Urbini 2018 (PMID 29937513)            UNKNOWN (no DAS in text)
   12  Brenca 2019 (PMID 31020999)            DEPOSITED, ACCESSION UNRECOVERABLE
    3  ModPathol 2023 (PMID 36948401)         UNKNOWN (full text not in PMC)
    1  GenesChromCancer 2022 (35932215)       UNKNOWN
   12  Chaiboonchoe 2026 (PMID 42465974)      PUBLIC: PRJNA1357027
   19  Unnamed GEO chondrosarcoma series      PUBLIC per PeerJ, ACCESSION UNRESOLVED HERE
    1  Hofvander (repo CLOSED-WORK)           CONTROLLED ACCESS (EGA)

TOTAL EMC specimens genome-wide expression-profiled, literature-stated : 84
  obtainable, accession KNOWN and public                              : 32
  public per literature but accession UNRESOLVED from here            : 19
  NOT obtainable without correspondence                               : 33

Uncertainty band on the TOTAL:
  lower (Urbini 5 fully nested in Brenca 12; the 19-EMC GEO set excluded) : 60
  point  (all rows additive, 19-EMC set included)                         : 84
Uncertainty band on the OBTAINABLE-WITHOUT-CORRESPONDENCE number:
  lower (19-EMC accession never resolves)                                 : 32
  upper (19-EMC accession resolves and the deposit is open)               : 51
ASSERTIONS PASSED
EXIT=0
$ python3 -VV
Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]
$ uname -srm
Linux 6.18.44-fc-v24 x86_64
```

**RUN — data-availability sweep** over the three PMC full texts, exit 0. Key verbatim outputs already quoted in R1 rows 3, 6, 7. The negative for Urbini 2018 is the load-bearing one: every hit for `available|deposit|accession|GEO|SRA|dbGaP|repository|Availability|upon request` in `PMC6073125` resolves to a software URL — `"AdapterRemoval (available online:)"`, `"TopHat/BowTie (available online:)"`, `"rmdup of Samtools (available online:)"`, `"htseq-count function (Python package Htseq—available online:)"` — and to `"available online: cancer.sanger.ac.uk/cosmic"`. **No sentence in that article concerns its own data.**

**RUN — disk, as instructed.** `df -h /` at start: `/dev/vda 252G 12G used 27G avail 30%`. At end: `24G avail 36%`. ≥10 GiB floor respected throughout. **Nothing downloaded.**

**RUN — write-isolation compliance.**
```
$ git rev-parse HEAD
103ff76f1d66426420c56a4d49752eb84f5f5c39
$ git status --porcelain | grep -v "opus-capacity-campaign" | head
(empty)
$ ls /tmp/claude-0/W01c
inventory.py  peerj.txt
```
HEAD advanced from `92abbcb9` during my run and three sibling reports appeared untracked; those are the coordinator's and other workers'. Nothing outside the campaign directory is modified. No git write operation of any kind was run.

**No content-policy refusal was encountered.** No network block was encountered either, because I contacted no blocked host — the closed transport branch was respected, not re-probed.

**PROPOSED (NOT RUN)** — the one query that would convert the 19 from a range into a number, for a networked runner: GEO free-text search for a cartilaginous-tumour expression series containing 19 EMC samples, then read its sample titles. It must carry a positive control (GSE24369, whose composition is known) so an empty result is distinguishable from a broken query. **Do not use WebSearch for this** — R4 shows why.

### Code (inline, per the write-isolation correction) — intended filename `code/W01c/inventory.py`

```python
"""W01c EMC whole-transcriptome / genome-wide expression inventory, built from the
published literature only (PubMed + WebSearch). No archive was queried; none is reachable.

Each row is a DISTINCT PUBLISHED STUDY that generated a genome-wide expression measurement
on EMC tumour specimens. n_emc is the number of EMC specimens the paper itself states were
PROFILED (not the number diagnosed/FISH-confirmed). Availability is the class justified by
the paper's own data-availability text, or by a third party's published account of trying
to obtain it. Nothing here is inferred from an archive query.
"""
S = [
 # key, year, n_emc, platform, availability_class, obtainable_without_correspondence
 ("Sjogren 2003 (PMID 12598313)",      2003,  2, "cDNA microarray",              "PRE-DEPOSITION ERA",        False),
 ("Subramanian 2005 (PMID 15920699)",  2005, 10, "42k-spot two-colour cDNA",     "PUBLIC: GSE4303",           True),
 ("Filion 2009 (PMID 18855877)",       2009,  3, "Affymetrix U133A",             "UNKNOWN (no DAS in text)",  False),
 ("Moller 2011 (PMID 21536545)",       2011,  6, "Affymetrix Gene ST GPL6244",   "PUBLIC: GSE24369",          True),
 ("Brunner 2012 (PMID 22929540)",      2012,  4, "3SEQ GPL10999",                "PUBLIC: GSE28866",          True),
 ("Davis 2017 (PMID 28423517)",        2017,  6, "MI-ONCOSEQ capture transcr.",  "BY REQUEST ONLY",           False),
 ("Urbini 2018 (PMID 29937513)",       2018,  5, "Illumina WTS 2x80bp",          "UNKNOWN (no DAS in text)",  False),
 ("Brenca 2019 (PMID 31020999)",       2019, 12, "Illumina HiSeq 1000 WTS",      "DEPOSITED, ACCESSION UNRECOVERABLE", False),
 ("ModPathol 2023 (PMID 36948401)",    2023,  3, "RNA exome sequencing",         "UNKNOWN (full text not in PMC)", False),
 ("GenesChromCancer 2022 (35932215)",  2022,  1, "whole-transcriptome, 1 case",  "UNKNOWN",                   False),
 ("Chaiboonchoe 2026 (PMID 42465974)", 2026, 12, "TempO-Seq Human WT 2.0",       "PUBLIC: PRJNA1357027",      True),
 ("Unnamed GEO chondrosarcoma series", None, 19, "microarray (per PeerJ Methods)","PUBLIC per PeerJ, ACCESSION UNRESOLVED HERE", None),
 ("Hofvander (repo CLOSED-WORK)",      None,  1, "sequencing, TAF15 case",       "CONTROLLED ACCESS (EGA)",   False),
]
tot = sum(r[2] for r in S)
pub_certain = sum(r[2] for r in S if r[5] is True)
pub_maybe   = sum(r[2] for r in S if r[5] is None)
notpub      = sum(r[2] for r in S if r[5] is False)
print("rows:", len(S))
for r in S:
    print(f"  {r[2]:>3}  {r[0]:<38} {r[4]}")
print()
print("TOTAL EMC specimens genome-wide expression-profiled, literature-stated :", tot)
print("  obtainable, accession KNOWN and public                              :", pub_certain)
print("  public per literature but accession UNRESOLVED from here            :", pub_maybe)
print("  NOT obtainable without correspondence                               :", notpub)
assert tot == pub_certain + pub_maybe + notpub
# Overlap-adjusted lower bound: Urbini 2018 (n=5, Maestro/CRO Aviano) may be a subset of
# Brenca 2019 (n=12, same senior author, same centres). Worst case they are not additive.
print()
print("Uncertainty band on the TOTAL:")
print("  lower (Urbini 5 fully nested in Brenca 12; the 19-EMC GEO set excluded) :", tot - 5 - 19)
print("  point  (all rows additive, 19-EMC set included)                         :", tot)
print("Uncertainty band on the OBTAINABLE-WITHOUT-CORRESPONDENCE number:")
print("  lower (19-EMC accession never resolves)                                 :", pub_certain)
print("  upper (19-EMC accession resolves and the deposit is open)               :", pub_certain + pub_maybe)
print("ASSERTIONS PASSED")
```

## Limitations

1. **⛔ Specimens, not patients.** Every count is specimens as stated by each paper. No cross-study patient deduplication was possible. The Urbini/Brenca nesting risk (same senior author, same Italian centres) is real and is the reason for the 60 lower bound; there may be others I cannot see. **No patient-level denominator is established by this run.**
2. **The total is a floor, not an estimate.** Two 2025–26 series (PMID 41644428, n=16; PMID 41315062, n=1) were excluded because I could not establish their platform as whole-transcriptome from the abstract. Including them on assumption would inflate the numerator; excluding them under-counts. Unpublished, non-English-indexed and commercial profiling are entirely outside this count.
3. **Two availability classes rest on an absence.** Filion 2009 and Urbini 2018 are `UNKNOWN` because a whole-text sweep found no data-availability sentence. **An absent sentence is UNKNOWN, not proof that no deposit exists** — a deposit could have been made and never stated, or stated only in a supplementary file I cannot reach.
4. **Two rows rest on abstracts alone** (PMID 36948401, 35932215): neither is in PMC, so their availability is unexamined rather than examined-and-inconclusive.
5. **Row 12's identity is unresolved and R4 explains why the obvious answer is unsafe.** Its *existence and public status* are PRIMARY (PeerJ's own Methods); its accession is not.
6. **The `[X] [Y] [Z] [W]` citation markers are unresolved** and I have not assumed which studies they are, even where the fit is strong.
7. **Row 13 (Hofvander) is a repository record I did not re-derive**, per CLOSED-WORK. It carries no PMID in this report because I did not retrieve one.
8. **No expression value was read and no archive was contacted.** Nothing here bears on EMC efficacy, safety, selectivity or clinical readiness, and nothing here is a wet-lab or clinical claim.
9. **External correspondence — the route the PeerJ group used — was not attempted and must not be.** It is outside every authority this campaign holds and remains a user decision, exactly as W01b recorded.

## Stop condition

**Set:** a literature-derived availability inventory with a per-study classification and the two headline numbers, **or** a precise statement of what the literature cannot settle.

**Outcome: MET, on the first branch, with two components honestly on the second.** Thirteen studies are inventoried with a classification and a justifying sentence for each; the two headline numbers are computed with explicit bounds. What the literature could **not** settle is stated precisely rather than guessed: the identity of the 19-EMC GEO series (with a negative control showing why the apparent answer is unsafe), and the `[X]/[Y]/[Z]/[W]` citation markers (with the reason: the PeerJ reference list is absent from the PMC rendering entirely). **No accession was guessed. No archive was re-probed. No dataset was downloaded.**

## Tool-call and wall-clock count actually used

**19 tool calls, ~5 minutes measured wall clock** (`02:07:58Z` → `02:12:30Z`), plus context reading before the first timestamp — under 15 minutes total. Well inside the ~40-call / ~40-minute self-observed target.

## Next concrete action

**One bounded successor, and it is now sharply targeted rather than a general sweep.** From the repository's GitHub Actions escape hatch (not authorised to a read-only worker), run a **GEO free-text search for a cartilaginous-tumour expression series containing 19 EMC samples**, carrying GSE24369 as a positive control, and read its sample titles. That single query resolves R1 row 12 and moves the obtainable number from `32–51` to a point value — the largest single reduction in uncertainty available to this lane, and it needs no correspondence and no spending. **It must not be attempted via WebSearch; R4 shows that channel fabricates accessions.**

**And the honest framing for the user's decision, unchanged from W01b but now quantified.** Three of the four unobtainable groups — Brenca's 12, Davis's 6, and the 8 specimens in papers with no data-availability statement at all — are reachable only by writing to authors or editors. That is 26 of 84 specimens, roughly a third of the world's EMC expression evidence, sitting behind a single class of action this repository has no authority to take. The numbers in R5 are what that decision should be weighed against.

result: Built the first literature-derived inventory of every EMC genome-wide expression dataset ever generated — 13 studies, 84 tumour specimens (range 60–84+), of which only 32 (range 32–51) are obtainable without correspondence; identified two datasets the repository cites but never treated as data resources (Urbini 2018 n=5 WTS and Filion 2009 n=3, both with NO data-availability statement anywhere in their full text), resolved the PeerJ trail's MI-ONCOSEQ study to Davis 2017 PMID 28423517 (6 EMC, obtained only by formal request to journal editors) and its first GEO cohort to GSE24369, and recorded a negative control showing the WebSearch summarizer fabricates GEO accessions so the unresolved 19-EMC series is reported unresolved rather than guessed.
