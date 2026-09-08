<!-- collected by the OPUS-CAPACITY-CAMPAIGN-20260908 parent collector at 2026-09-08T03:20:24Z UTC
     agent id a7b5090ee145a858b ; transcript /root/.claude/projects/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/subagents/agent-a7b5090ee145a858b.jsonl
     OBSERVED runtime model set in that transcript: ["claude-opus-5"] (asserted exactly [claude-opus-5])
     the worker was read-only on the tree; this file is the parent's write -->

Stop condition met. Report follows.

---

# W01h — The transcriptome-wide criterion applied to the FULL inventory: rows 8, 12 and the nine off-table rows, and what each ruling actually costs

## Worker

- **Worker:** W01h, lane 1 refill (public EMC tumour expression / multiomics resources), OPUS-CAPACITY-CAMPAIGN-20260908. Successor to W01g.
- **Model identity: SELF-REPORT, NOT INDEPENDENTLY VERIFIED.** I report myself as Claude Opus 5 (`claude-opus-5`). No environment variable names a model. The coordinator must extract the served model from the transcript.
- **`date -u` start:** `Tue Sep  8 03:11:41 UTC 2026`. **`date -u` end:** `Tue Sep  8 03:15:38 UTC 2026`.
- **`git rev-parse HEAD` start:** `98a0833f1ede2cf9cef13790388260567a32e868`. **end:** `98a0833f1ede2cf9cef13790388260567a32e868` (unchanged; every reading below is against `98a0833f`, which differs from W01g's `fc6ed929` and W01f's `4d950cf0`).
- **`git status --porcelain` start** (exit 0) — eight untracked collector-written reports, none mine:

```
?? research/autonomy/opus-capacity-campaign-20260908/reports/W01g-transcriptome-wide-criterion.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W02f-fibro-ecm-decomposition.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W04e-delay-attribution-route.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W06f-coherent-share-readout.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W07f-emc-only-cohort-full-texts.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W09f-publications-false-absence-audit.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W12e-subprocess-env-residual.md
?? research/autonomy/opus-capacity-campaign-20260908/reports/W20g-published-denominator-consistency.md
```

- **`git status --porcelain` end** (exit 0) — the same eight lines **plus** `?? research/autonomy/opus-capacity-campaign-20260908/executed-artifacts/`, a directory created by coordinator activity during my run. **I wrote nothing to the Git tree**; all execution was under `/tmp/claude-0/w01h/`. **No network and no retrieval of any kind** — no WebFetch, no WebSearch, no PubMed MCP, no accession or archive query.
- **`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** (exit 0), literal. Start and end outputs were identical except that at end I filtered out five long proxy/JVM host-list variables (`no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `npm_config_noproxy`, `JAVA_TOOL_OPTIONS`) — they name no model. Full start output:

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

Pursued exactly as dispatched. Two parts:

1. **Settle W01g's flag.** W01g held rows 8 (Brenca, 12 specimens) and 12 (unnamed GEO series, 19) fixed at baseline as out of scope, while flagging that **D2 applied consistently would put row 8's platform in the UNKNOWN column too**, moving the floor below any figure in its table. Settle that from committed evidence only.
2. **Extend the matrix.** For rows 8 and 12 and for every other W01c inventory row absent from W01g's five-row platform table, record what assay/platform the committed record **establishes**, what it merely **states**, and what is **UNKNOWN** — then run W01g's D1, D2a, D2b, D3, D4a, D4b, D5 over the **full** inventory and report the floor, ceiling and total each produces.

It is open because W01g priced the criterion over five rows out of thirteen and deliberately froze the two largest contested rows. A criterion that is a ruling about *what counts as transcriptome-wide profiling* cannot be priced on the subset of rows that happen to be deposited: it gates the 84-specimen headline total as much as it gates the obtainable band. **I do not pick a winner. The criterion is the lane owner's to set.**

## Prior-work check

Read in full at `98a0833f`: `COMMON-BRIEF.md`, `CLOSED-WORK.md`, `CORPUS-CONTEXT.md`, and `reports/W01g-transcriptome-wide-criterion.md` (the report I succeed). Read to the extent needed and cited by line: `reports/W01c-…` R1–R5 (the 13-row inventory at `:115`–`:128`, the exclusions at `:129`, the R3 negative control at `:156`–`:166`, the R5 class decomposition at `:180`–`:190`), `reports/W01f-…` R1–R4 (the floor/ceiling construction at `:112`–`:132`, the leave-one-out table at `:138`–`:150`, S-PARITY, the stable core at `:172`).

Commands run and what they showed:

| command | result |
|---|---|
| `git ls-files research/autonomy/opus-capacity-campaign-20260908/reports/` | W01c, W01e, W01f **are tracked**; W01g is **untracked at this HEAD** — so W01g's own text is not yet a committed artifact, and I flag every consumption of it as such |
| `rg -n -i --glob '!.git' -e 'HiSeq 1000' -e '70M' -e '70 ?million' .` | 3 hits; row 8's platform statement at `W01-…:94` and `W01c-…:122`, `:287` |
| `rg -n --glob '!.git' -e 'U133A' -e 'MI-ONCOSEQ' -e 'RNA exome' -e 'LSM14A' -e '2 × 80' .` | 24 hits; the load-bearing ones pinned in R1 |
| `rg -n --glob '!.git' -e 'GPL96' -e '22215' -e '22,215' .` | the only non-simulation hits are `emc-cohort-search.json:104` (platform **title** only) and `prmt5-…-2026-08-10.json:21` (verbatim probe-set count). **No committed gene-space measurement exists for U133A.** |
| `rg -n -i --glob '!.git' 'hofvander' .` | 8 hits, all campaign reports plus `CLOSED-WORK.md:21`. **No committed source names row 13's assay, platform or even its RNA/DNA modality.** |
| `rg -n -i 'Sjögren\|Sjogren\|12598313' research/manuscripts research/modalities research/literature` | `fusion-junction-aso-references.md:67` carries the 2003 title verbatim (*"…cytogenetic, molecular genetic, and cDNA microarray analyses"*) |

**Confirmed not replayed.** No retrieval of any kind was attempted — no accession, no route, no PubMed, no WebSearch, no archive. `PRJNA692081` / `SRP301712` are treated throughout as **ALREADY RECOVERED**; I did not touch them. **I made no attempt to identify row 12** and record no candidate accession for it. PUB-EMC-CLASSIFICATION is not reopened. `GSE4303` / `GSE28866` are `CLOSED-WORK.md` "heavily retained" data; I re-read no deposit and claim no new data. **I did not re-derive W01f's leave-one-out table or W01g's five-row platform table — both are consumed as inputs.** No cohort, independence or patient claim is made or implied: **libraries are not specimens, arrays are not patients, runs are not patients, and fifteen unresolved libraries are not fifteen patients.** Row 8's count stays at the paper-stated 12.

**Novelty statement, plainly:** this run adds **no source and no data**. It is arithmetic plus a citation audit over committed artifacts. Genuinely new content: (a) the nine-row assay-evidence table that nobody had built (R1), (b) the settlement of W01g's row-8 flag (R2), (c) the full-inventory admission matrix and the finding that the **total**, not just the core, is criterion-sensitive across a 10-fold range (R3), and (d) the demonstration that D1's own text, applied uniformly, **inverts** the stable core (R4).

## Method / inputs

All inputs are artifacts read at `98a0833f`; no paper was retrieved and no platform record was read.

| input | supplies |
|---|---|
| `reports/W01c-emc-deposit-literature-inventory.md` `:115`–`:129` | the 13-row inventory: per-row `n EMC profiled`, Platform column, availability class, exclusions |
| `reports/W01f-obtainable-band-stability.md` `:112`–`:132` | the floor/ceiling construction (floor = accession known and public; ceiling = floor + row 12) — **consumed, not re-derived** |
| `reports/W01g-transcriptome-wide-criterion.md` R1–R4 (untracked at this HEAD) | the five-row platform table and the definitions D1/D2/D3/D4/D5 with their `file:line` quotes — **consumed, not re-derived** |
| `reports/W01-expression-multiomics-resources.md:94` | row 8's platform statement |
| `research/literature/prmt5-ewing-expression-panel-composition-2026-08-10.json:21` | Filion's platform, verbatim |
| `research/manuscripts/aso/fusion-junction-aso-references.md:67` | Sjögren 2003's title, verbatim |
| `reports/W02-singlecell-spatial-microenvironment.md:109` | the only committed assay statement for PMID 41644428 |
| `research/autonomy/opus-capacity-campaign-20260908/CLOSED-WORK.md:21` | the only committed statement about row 13 |

Tool: `python3` 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0] on Linux 6.18.44-fc-v24 x86_64, cwd `/tmp/claude-0/w01h/`, outside the repository. Script `full_inventory_matrix.py`, returned in full in Validation evidence.

## Result

### R1 — The nine rows W01g did not put on a platform table: established / stated / UNKNOWN

W01g tabulated rows 2, 4, 5, 11 and the excluded PMID 41644428. These are the remaining nine inventory rows. The three columns are deliberately separated, because the whole dispute is what "established" means.

**"Established"** = a committed measurement or an independent verbatim platform record in this checkout. **"Stated"** = an author's, depositor's or third party's self-description transcribed into a committed artifact. The repository's own precedent for refusing a self-description as establishing is `research/modalities/emc-fourth-cohort-quant.json:18` (*"the depositors' own words in their own deposit… not an independent measurement"*), quoted by W01g R2.

| # | study | n | **established** by committed evidence | **stated** but not established | **UNKNOWN** | grade |
|---|---|---:|---|---|---|---|
| 1 | Sjögren 2003 (PMID 12598313) | 2 | Nothing about the platform. The paper's own **title** is committed verbatim: *"…cytogenetic, molecular genetic, and **cDNA microarray** analyses"* (`fusion-junction-aso-references.md:67`) | that the assay was a cDNA microarray; that 2 EMC were profiled (`W01c-…:115`) | array identity, spot count, gene space, transcriptome fraction — **all UNKNOWN** | SECONDARY (assay class) / **UNKNOWN** (scope) |
| 3 | Filion 2009 (PMID 18855877) | 3 | **Platform verbatim, independent of W01c:** *"Samples were hybridized to Affymetrix U133A microarrays containing 22,215 probes sets"* (`prmt5-ewing-expression-panel-composition-2026-08-10.json:21`; corroborated `nr4a3-fusion-targets.json:699`, `…-SI.md:123`). A **fixed manufactured probe set** — established | — | **gene space never measured here.** `emc-cohort-search.json:104` holds only the platform *title* `"[HG-U133A] Affymetrix Human Genome U133A Array"`; no probe→symbol resolution and no gene count exists in this tree | PRIMARY (probe count) / **UNKNOWN** (gene space) |
| 6 | Davis 2017 (PMID 28423517) | 6 | Nothing measured. Two committed transcriptions: *"MI-ONCOSEQ: exome + PolyA+ and capture transcriptome"* (`W01c-…:120`) and *"tumor PolyA+ and capture transcriptome"* (`W01c-…:147`) | a third party's description of what they received: *"**whole-transcriptome expression matrices**… for the six EMC cases profiled using the MI-ONCOSEQ platform"* (`W01c-…:120`, `:137`) | which arm produced the matrices; capture bait-set size; gene space. **Mixed assay: the PolyA+ arm has no pre-selected target set, the capture arm does.** Not resolvable here | PRIMARY (n) / **UNKNOWN** (scope) |
| 7 | Urbini 2018 (PMID 29937513) | 5 | Nothing measured. Read length is transcribed: *"Illumina WTS, 2 × 80 bp paired-end"* (`W01c-…:121`) | the author's own scope word, **WTS = whole transcriptome sequencing**; *"WTS was performed on five cases of EMC"* | library protocol, depth, gene space, transcriptome fraction | PRIMARY (n) / SECONDARY (scope word) |
| **8** | **Brenca 2019 (PMID 31020999)** | **12** | **Nothing measured.** The strongest committed record is a transcription of the paper's Methods: *"Illumina HiSeq 1000, whole-transcriptome RNA-Seq, ~70M paired-end reads/sample; FFPE (+5 matched frozen)"* (`W01-…:94`; repeated `W01c-…:122`, `:287`) | **the authors' own scope word, "whole-transcriptome".** Read count and instrument are equally author-stated | **gene space never measured. No probe/target census, no symbol resolution, no coverage figure anywhere in this checkout.** Whether the deposit's libraries can be resolved to the 12 stated specimens is separately UNKNOWN (`W01f-…:145`) | PRIMARY (paper's n) / **UNKNOWN** (measured scope) |
| 9 | *Genes Chrom Cancer* 2022 (PMID 35932215) | 1 | Nothing. Not in PMC (`W01c-…:123`) | abstract states *"whole-transcriptome sequencing"* of one case | platform, instrument, depth, gene space, availability | PRIMARY (n) / **UNKNOWN** |
| 10 | *Mod Pathol* 2023 (PMID 36948401) | 3 | Nothing measured, but the assay **name is committed verbatim twice**: *"subjected to **RNA exome sequencing (RES)**"* (`W01c-…:124`; `no-wet-lab-archetypes-2026-08-12.json:752`). RNA **exome** = a capture assay with a pre-selected bait set — established as a class | that only 3 of the 58 FISH-confirmed EMC were sequenced | bait-set identity and size, gene space, availability. Not in PMC | PRIMARY (n, assay class) / **UNKNOWN** (scope) |
| **12** | **unnamed GEO cartilaginous series** | **19** | **Nothing.** No accession, no platform record, no sample census. W01c's R4 negative control (`:156`–`:164`) established that the one candidate accession a search summarizer offered is **NOT usable** and must not enter any inventory | a third party's Methods: *"two independent, publicly available microarray datasets from GEO… The second dataset,[accession], directly compares EMC tumors (= 19) against… other chondrosarcomas (= 128)"* (`W01c-…:126`) | **identity, platform, spot/probe count, gene space, one-colour vs two-colour, everything except the word "microarray" and the stated counts.** I made no attempt to identify it | PRIMARY (existence + public status per that Methods sentence) / **UNKNOWN** (all platform facts) |
| 13 | Hofvander TAF15 case | 1 | **Nothing.** The only committed statement in the tree is `CLOSED-WORK.md:21`: *"Hofvander: one `TAF15` case, raw data controlled-access via EGA."* W01e found no committed anchor; the tree's only EGA accession is Haller's, not EMC (`W01f-…:128`) | that the data are sequencing data of some kind (W01c's Platform cell reads *"sequencing"*, `:127`, sourced to that same repository line) | **assay, platform, even RNA vs DNA modality — UNKNOWN.** This row cannot be scored on any transcriptome criterion | **SECONDARY / UNKNOWN throughout** |
| X1 | PMID 41644428 (excluded) | 16 | Nothing. Consumed from W01g R1: no PMC, `isOpenAccess: N` | *"IHC + FISH + NGS, 16 EMC cases"* (`W02-…:109`) | **whether the NGS is RNA or DNA, and its target space** | **UNKNOWN** |
| X2 | PMID 41315062 (excluded) | 1 | Nothing | *"comprehensive genomic profiling reported, whole-transcriptome not established"* (`W01c-…:129`) | modality and target space | **UNKNOWN** |

**The single most consequential line on this table:** **not one row here has a measured gene space.** The only rows in the whole 13-row inventory with a committed gene-space measurement are the three W01g already tabulated — `GSE24369` (20,324 symbols), `GSE28866` (14,120 genes), `PRJNA1357027` (862 genes) — and of those the third *fails* a transcriptome-wide threshold. Nine of thirteen rows rest on an author's or a third party's scope word alone.

### R2 — Settling W01g's flag on row 8: CONFIRMED

W01g flagged, without asserting, that D2 applied consistently would put row 8's platform in the UNKNOWN column. **The committed record confirms the flag.** The argument is three checkable steps, no inference beyond them:

1. **D2's own text** demands the scope be *established*, not merely stated: W01c excluded PMID 41644428 because *"NGS **stated but not established** as whole-transcriptome"* and PMID 41315062 because *"whole-transcriptome **not established**"* (`W01c-…:129`).
2. **The repository's own artifact refuses author/depositor self-description as establishing:** `emc-fourth-cohort-quant.json:18` — the assay description is *"the depositors' own words in their own deposit. It is **not an independent measurement**"* (quoted W01g R2). That refusal is what makes row 11's nominal admission a D1 act rather than a D2 one.
3. **Row 8's entire scope claim is an author self-description.** `W01-…:94` transcribes *"whole-transcriptome RNA-Seq"* from Brenca's Methods; no committed measurement of its gene space, target space or symbol resolution exists anywhere in this checkout (R1 above, and the `rg` sweeps in Prior-work check).

Therefore **row 8 stands on exactly the footing D2 was written to reject.** Under **D2a** (UNKNOWN excluded) row 8 is out; under **D2b** (UNKNOWN retained) it is in, on the same terms as `GSE4303`.

**The arithmetic cost, which is the point of the flag.** W01g's D2a row read floor 22 (= core 10 + row 8's 12 held fixed). Releasing the hold:

> **D2a floor = 10, not 22.** The floor loses row 8's 12 specimens, **and** it loses the ceiling adder as well, so **D2a's band collapses to 10 – 10**.

**10 is below every figure in W01g's R3 table** (whose minimum floor was 12 and minimum ceiling 31). W01g's prediction that the flag "would move the floor further than any figure in R3" is **correct, and the magnitude is −12 on the floor and −21 on the ceiling** relative to its own D2a row.

**Row 12 needs no separate settlement:** it has no platform evidence at all, so it is admitted only by the definitions that retain UNKNOWN (D2b, D4a) or that gate nothing (D5). Under D1n, D2a, D3 and D4b its 19 specimens are simply absent — and since it is the *sole* member of the ceiling adder (`W01f-…:164`), **the floor and the ceiling are equal under four of the seven rulings.** The band stops being a band.

### R3 — The full-inventory admission matrix

Machine output, `full_inventory_matrix.py`, exit 0, assertions passed. Definitions are W01g's, verbatim in intent; the admit-sets are R1's row-by-row verdicts. Floor and ceiling use W01f's construction unchanged (floor = accession-known-and-public rows {2, 4, 5, 8, 11}; ceiling adder = row 12), intersected with each definition's admit-set.

**One change of scope from W01g must be stated openly.** W01g held the **total** at the inventory size (84, or 100 under D5) regardless of which rows the assay criterion excluded. That is not sustainable once the criterion is applied to the whole inventory: the total answers *"how many EMC specimens have ever been transcriptome-wide profiled"*, so the same ruling that gates the band must gate it. **My totals are definition-gated; W01g's were not.** Both are shown so nothing is silently altered.

| definition | admits (of 14 scoreable rows) | core | **floor** | **ceiling** | **total** | W01g's total, for contrast |
|---|---|---:|---:|---:|---:|---:|
| **D1n** nominal — the definition's own text, applied uniformly | 6, 7, 8, 9, 11 | **0** | **24** | **24** | **36** | 84 |
| **D2a** established by evidence, UNKNOWN excluded | 4, 5 | **10** | **10** | **10** | **10** | 84 |
| **D2b** established, UNKNOWN retained | all but 11 (and X1) | **20** | **32** | **51** | **72** | 84 |
| **D2b-consistent** — X1 is UNKNOWN, so it is retained too | all but 11 | **20** | **32** | **51** | **88** | — |
| **D3** no fixed pre-selected target set | 5, 6, 7, 8, 9 | **4** | **16** | **16** | **28** | 84 |
| **D3-strict** — Davis's capture arm read as fixed | 5, 7, 8, 9 | **4** | **16** | **16** | **22** | — |
| **D4a** measured gene space ≥10k, unmeasured retained | all but 11 (and X1) | **20** | **32** | **51** | **72** | 84 |
| **D4a-consistent** — X1 unmeasured, so retained too | all but 11 | **20** | **32** | **51** | **88** | — |
| **D4b** measured gene space ≥10k, unmeasured excluded | 4, 5 | **10** | **10** | **10** | **10** | 84 |
| **D5** modality only (RNA expression, any target space) | all 14 | **20** | **44** | **63** | **100** | 100 |

**Ranges across the definitions actually in the record:**

- **stable core: 0 – 20** — **unchanged** from W01g. The core is defined over rows 2/4/5 only, so extending the inventory cannot move it. **This is the one number W01g quoted that the extension leaves exactly where it was.**
- **floor: 10 – 44** (W01g reported 12 – 44 over five rows). The new minimum is 10, from releasing row 8 under D2a/D4b — see R2.
- **ceiling: 10 – 63** (W01g reported 31 – 63). The new minimum is 10: under D2a, D4b, D1n and D3 the ceiling adder is not admitted at all, so **ceiling = floor**.
- **total: 10 – 100.** W01g's totals spanned 84 – 100. **Definition-gated, the headline "84 specimens ever profiled" ranges from 10 to 100 — a factor of ten.**

**Answering the dispatch's conditional directly: the range is wider than 0 – 20, and the other rows are emphatically NOT criterion-insensitive.** The arithmetic:

- The **core** stays 0 – 20 (structurally; it is a three-row quantity).
- The **band** widens on the floor by 2 (12 → 10) and on the ceiling by 21 (31 → 10 as a minimum), because row 8's 12 and row 12's 19 both become criterion-dependent instead of fixed.
- The **total** widens from a 16-specimen spread (84 – 100) to a **90-specimen spread (10 – 100)**. Nine rows carrying **62 specimens** (rows 1, 3, 6, 7, 8, 9, 10, 12, 13 = 2+3+6+5+12+1+3+19+1) were held constant by W01g and are in fact gated by six of the seven rulings. **That is the true cost W01g's five-row table could not show.**

### R4 — Two structural findings the extension exposes

**(a) D1, applied to its own text, inverts the stable core.** W01g defined D1 as *"the assay's own name asserts the scope"*, and admitted rows 2, 4, 5, 11. But of those four, **only row 11's name asserts anything** — *"TempO-Seq Human Whole Transcriptome 2.0"* (`W01c-…:125`). Row 2's committed name is *"42,000-spot two-colour cDNA, GPL3290"* (`:116`), row 4's is *"Affymetrix Gene ST, GPL6244"* (`:118`), row 5's is *"3SEQ, GPL10999"* (`:119`) — **none asserts transcriptome-wideness.** Meanwhile four rows W01g never scored *do* assert it in their committed names: Urbini's **WTS** (`:121`), Brenca's *"whole-transcriptome RNA-Seq"* (`W01-…:94`), GCC 2022's *"whole-transcriptome sequencing"* (`:123`), and Davis's *"whole-transcriptome expression matrices"* (`:120`).

So D1 applied uniformly **drops all three stable-core rows and keeps the sequencing rows**: core **0**, floor **24**, total **36**. D1-as-applied and D1-as-written are different rules, and the difference is not marginal — it is a complete swap of which studies count. **The plainest reading is that D1-as-applied was never a transcriptome-wideness test at all: it did work on exactly one row (row 11) and, on the other three, it was doing the job of "publicly deposited expression dataset" — i.e. D5.** I state this as a property of the committed table, not as a recommendation.

**(b) Two definitions have an UNKNOWN policy that W01g's totals did not carry through.** D2b and D4a both retain UNKNOWN rows. PMID 41644428's platform is UNKNOWN (`W02-…:109`, and no PMC). **Retaining UNKNOWN therefore admits it**, taking those totals from 72 to 88. W01g named this exact asymmetry in R4 (*"D2b applied to `GSE4303` and D2a applied to 41644428 is the same asymmetry one level down"*) and left the total at 84. The extension prices it: **+16 specimens.** PMID 41315062 (n = 1) is equally UNKNOWN and would add 1 more under the same policy; it is footnoted rather than tabulated because W01g did not score it and I am not silently changing its baseline.

**(c) Three rows are criterion-insensitive, and only three.** Rows 4 (`GSE24369`) and 5 (`GSE28866`) are admitted by every one of the seven definitions — they are the only rows with a measured gene space above any plausible threshold and no fixed-panel or UNKNOWN objection. Row 11 is *rejected* by every definition except D1-as-applied and D5. Everything else moves.

### R5 — What this does and does not tell the lane owner

- **The 20-specimen stable core survives the extension untouched.** It remains the only quotable number, and the extension strengthens rather than weakens that: adding nine rows and eight rulings does not move it.
- **Every other number in lane 1's package is criterion-dependent, including the one that reads most like a fact.** "84 specimens have ever been genome-wide expression profiled" is not a measurement; it is the D5 answer minus PMID 41644428. Under the strictest rule in the record it is 10.
- **Four of the seven rulings collapse the band to a point** (floor = ceiling), because row 12 is the sole ceiling adder and has no platform evidence to admit.
- **The cheapest thing that would shrink this spread is still a measurement, not a ruling** — and R1 identifies eight new candidates, not one: no row except 4, 5 and 11 has a measured gene space anywhere in this checkout. **I did not run any of them; each requires retrieval, which this dispatch forbids.**

## Validation evidence

**RUN.** Environment: Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0]; Linux 6.18.44-fc-v24 x86_64; cwd `/tmp/claude-0/w01h`, outside the repository. **No network in any command.**

| # | command | exit | key output |
|---|---|---|---|
| 1 | `date -u`; `git rev-parse HEAD`; `git status --porcelain`; `env \| grep -i -E 'claude\|anthropic\|model' \| sed …` | 0 | start `03:11:41 UTC`; HEAD `98a0833f…`; 8 untracked collector reports; env block quoted above |
| 2 | `ls -la …/opus-capacity-campaign-20260908/ …/reports/` | 0 | 4 briefs + 100+ reports; W01c 38,028 B, W01e 25,331 B, W01f 24,988 B, W01g 33,147 B |
| 3 | `cat COMMON-BRIEF.md CLOSED-WORK.md CORPUS-CONTEXT.md` | 0 | read in full |
| 4–5 | `cat -n W01g-…md`; `awk 'NR>=75 && NR<=280'` in two passes | 0 | R1 five-row table, R2 five definitions with `file:line`, R3 admission matrix, R4 self-consistency, Limitations incl. the row-8 flag |
| 6 | `grep -n "" W01c-…md \| sed -n '90,150p'` | 0 | the 13-row inventory `:115`–`:128`, exclusions `:129` |
| 7 | `grep -n "" W01f-…md \| sed -n '60,175p'` | 0 | floor/ceiling construction `:112`–`:132`; **"Floor 44 = 10+6+4+12+12. Ceiling 63 = 44+19. Total 84."** (`:130`); stable core `:172` |
| 8 | `grep -n "" W01c-…md \| sed -n '150,200p'` | 0 | R4 negative control (`GSE6481` **NOT established**, `:164`); R5 class decomposition summing to **84 / 13 studies** (`:190`) |
| 9 | `git ls-files …/reports/`; `rg -n -i -e 'HiSeq 1000' -e '70M' …` | 0 | W01g untracked; row 8 platform at `W01-…:94` |
| 10 | `rg -n -e 'U133A' -e 'MI-ONCOSEQ' -e 'RNA exome' -e 'LSM14A' …` | 0 | 24 hits; `prmt5-…:21`, `…-SI.md:123`, `no-wet-lab-archetypes…:752` |
| 11 | `sed -n '95,120p' emc-cohort-search.json`; `rg -i 'Sjögren\|Sjogren\|12598313' …` | 0 | U133A platform **title only**, no gene count; Sjögren title at `fusion-junction-aso-references.md:67` |
| 12 | `grep -n -i hofvander …`; `rg -n -e 'GPL96' -e '22,215' .` | 0 | `CLOSED-WORK.md:21` is the **only** committed Hofvander statement; no U133A gene-space measurement in the tree |
| 13 | `cd /tmp/claude-0/w01h && python3 full_inventory_matrix.py; echo "EXIT=$?"` | **0** | the R3 table verbatim; `core range: 0 - 20`; `floor range: 10 - 44`; `ceil range: 10 - 63`; **`TOTAL range: 10 - 100`**; **`ASSERTIONS PASSED`** |
| 14 | `sed -n '107,111p' W02-…md`; `sed -n '21p' CLOSED-WORK.md`; `sed -n '21p' prmt5-…json` | 0 | *"41644428 \| IHC + FISH + NGS, 16 EMC cases"*; the Hofvander line; *"…U133A microarrays containing 22,215 probes sets"* |
| 15 | `date -u`; `git rev-parse HEAD`; `git status --porcelain`; `env \| grep …` | 0 | end `03:15:38 UTC`; HEAD **unchanged** `98a0833f…`; status gained only `?? …/executed-artifacts/` (coordinator, not mine); env unchanged |

`full_inventory_matrix.py`, in full — it does arithmetic only; every admit-set entry is an R1 verdict traced to a `file:line` above:

```python
"""W01h - extend W01g's admission matrix from 5 rows to the FULL 13-row W01c inventory
(+ the excluded PMID 41644428). Arithmetic only. Every per-row admission verdict is a
transcribed reading of a committed artifact, cited file:line in the report."""

# n, in W01f floor set?, is the ceiling adder?
ROWS = {
 "r1  Sjogren 2003":        (2,  False, False),
 "r2  GSE4303":             (10, True,  False),
 "r3  Filion 2009":         (3,  False, False),
 "r4  GSE24369":            (6,  True,  False),
 "r5  GSE28866":            (4,  True,  False),
 "r6  Davis 2017":          (6,  False, False),
 "r7  Urbini 2018":         (5,  False, False),
 "r8  Brenca 2019":         (12, True,  False),
 "r9  GCC 2022":            (1,  False, False),
 "r10 ModPathol 2023":      (3,  False, False),
 "r11 PRJNA1357027":        (12, True,  False),
 "r12 unnamed GEO series":  (19, False, True),
 "r13 Hofvander":           (1,  False, False),
 "X1  PMID 41644428":       (16, False, False),   # outside W01c's 84; enters TOTAL only
}
assert sum(v[0] for k,v in ROWS.items() if not k.startswith("X")) == 84

A = {  # admit-sets over the FULL inventory
 "D1n nominal, definition's own text":      ["r6","r7","r8","r9","r11"],
 "D2a established, UNKNOWN excluded":       ["r4","r5"],
 "D2b established, UNKNOWN retained":       ["r1","r2","r3","r4","r5","r6","r7","r8","r9","r10","r12","r13"],
 "D2b-consistent (X1 also retained)":       ["r1","r2","r3","r4","r5","r6","r7","r8","r9","r10","r12","r13","X1"],
 "D3  no fixed pre-selected target set":    ["r5","r6","r7","r8","r9"],
 "D3  same, Davis capture arm strict":      ["r5","r7","r8","r9"],
 "D4a measured >=10k, unmeasured retained": ["r1","r2","r3","r4","r5","r6","r7","r8","r9","r10","r12","r13"],
 "D4a-consistent (X1 also retained)":       ["r1","r2","r3","r4","r5","r6","r7","r8","r9","r10","r12","r13","X1"],
 "D4b measured >=10k, unmeasured excluded": ["r4","r5"],
 "D5  modality only (RNA expression)":      ["r1","r2","r3","r4","r5","r6","r7","r8","r9","r10","r11","r12","r13","X1"],
}
CORE3 = ["r2","r4","r5"]
def key(name): return name.split()[0]
print(f"{'definition':44s} {'core':>4s} {'floor':>5s} {'ceil':>4s} {'total':>5s}")
res={}
for name, admit in A.items():
    core  = sum(ROWS[k][0] for k in ROWS if key(k) in CORE3 and key(k) in admit)
    floor = sum(ROWS[k][0] for k in ROWS if ROWS[k][1] and key(k) in admit)
    ceil  = floor + sum(ROWS[k][0] for k in ROWS if ROWS[k][2] and key(k) in admit)
    tot   = sum(ROWS[k][0] for k in ROWS if key(k) in admit)
    res[name]=(core,floor,ceil,tot)
    print(f"{name:44s} {core:4d} {floor:5d} {ceil:4d} {tot:5d}")
v=list(res.values())
print()
print("core  range:", min(x[0] for x in v), "-", max(x[0] for x in v))
print("floor range:", min(x[1] for x in v), "-", max(x[1] for x in v))
print("ceil  range:", min(x[2] for x in v), "-", max(x[2] for x in v))
print("TOTAL range:", min(x[3] for x in v), "-", max(x[3] for x in v))
assert res["D5  modality only (RNA expression)"] == (20,44,63,100), "must reproduce W01g D5"
assert res["D2a established, UNKNOWN excluded"][1] == 10
assert res["D1n nominal, definition's own text"][0] == 0
print("ASSERTIONS PASSED")
```

Verbatim output (exit 0):

```
definition                                   core floor ceil total
D1n nominal, definition's own text              0    24   24    36
D2a established, UNKNOWN excluded              10    10   10    10
D2b established, UNKNOWN retained              20    32   51    72
D2b-consistent (X1 also retained)              20    32   51    88
D3  no fixed pre-selected target set            4    16   16    28
D3  same, Davis capture arm strict              4    16   16    22
D4a measured >=10k, unmeasured retained        20    32   51    72
D4a-consistent (X1 also retained)              20    32   51    88
D4b measured >=10k, unmeasured excluded        10    10   10    10
D5  modality only (RNA expression)             20    44   63   100

core  range: 0 - 20
floor range: 10 - 44
ceil  range: 10 - 63
TOTAL range: 10 - 100
ASSERTIONS PASSED
```

The `D5` assertion is a regression check against W01g: my pipeline reproduces its `(core 20, floor 44, ceiling 63, total 100)` exactly, which is why the divergences elsewhere are attributable to the extension and not to a re-derivation.

**PROPOSED (NOT RUN):**
- **Measure the gene space of rows 1, 3, 6, 7, 8, 9, 10, 12** (eight rows, 51 specimens). Each needs a platform record or a deposit and a symbol bridge. **Not run:** every route is a retrieval, forbidden by this dispatch. This is what would collapse the D2a/D2b and D4a/D4b splits.
- **Establish PMID 41644428's and PMID 41315062's modality.** **Not run:** no PMC, `isOpenAccess: N`; any route is a retrieval.
- **Resolve row 12's identity.** **Not attempted by dispatch**, and W01c's R4 control shows the one apparently-available route is untrustworthy for identifier recovery.

**No test suite and no `scripts/preflight.sh`** — this run changes no code, manuscript or shared state, and the dispatch forbids preflight. Nothing here is a skipped check reported as a pass.

## Limitations

- **This is an audit of committed artifacts, not of platforms.** I read no GEO platform record, no vendor manifest, no paper. Where a committed transcription is wrong, I am wrong identically. In particular, **rows 1, 6, 7, 9, 10, 12, 13 and X1/X2 reach me only through W01c's and W01's transcriptions** of texts they retrieved and I did not.
- **W01g is untracked at `98a0833f`.** Its five-row table and its five definitions are consumed as inputs but are **not yet committed artifacts**, so every number I inherit from it carries that caveat. My own arithmetic is independently re-runnable from the script above.
- **The admit-sets encode judgements, not measurements.** D3's verdicts rest on assay *class* entailments — a spotted cDNA array and an Affymetrix array have fixed probe sets; RNA exome capture has a fixed bait set; PolyA+ shotgun does not. Those entailments follow from the assay names in the committed record, but **no committed source states them as rulings**, and Davis's mixed assay (PolyA+ **and** capture) is genuinely ambiguous — hence the D3-strict sensitivity row (total 28 vs 22).
- **"Fraction of the transcriptome addressed" remains UNKNOWN for every row in the inventory**, as W01g established. The D4 threshold of 10k is W01g's, applied to four heterogeneous proxies measured by different pipelines against different denominators. **It is approximate and it is not comparable across rows.**
- **My totals are definition-gated and W01g's were not.** That is a deliberate, declared change of scope, shown side by side. A lane owner who prefers W01g's convention should read the core/floor/ceiling columns and ignore mine.
- **The definition set is not exhaustive** — it is W01g's enumeration of what the committed record uses. A rule nobody has written down would add rows and could widen the ranges further.
- **No cohort, independence or patient claim is made anywhere.** Specimens are not patients; arrays are not patients; runs are not patients; libraries are not specimens. No patient-level deduplication exists across any pair of these studies except the one W01 computed. Row 8's count stays at the paper-stated 12 and row 12's at the third-party-stated 19. **Row 12 was not identified and no candidate accession is recorded.**
- **There is no wet lab and no clinical claim here.** This report concerns bookkeeping over published dataset descriptions and establishes nothing about EMC biology, therapy or care.

## Stop condition

**Set up front:** return the moment (a) every W01c inventory row absent from W01g's five-row table — rows 1, 3, 6, 7, 8, 9, 10, 12, 13, plus the excluded PMIDs — has an established / stated / UNKNOWN assay record with `file:line`, **and** (b) W01g's seven definitions have been extended to the full inventory with floor, ceiling and total computed by a script that asserts its own consistency against W01g's D5 row.

**Met.** R1 covers all nine off-table rows plus both exclusions; R2 settles the row-8 flag; R3 reports the extension with `ASSERTIONS PASSED` at exit 0. I did not pick a winner among the definitions. Returning immediately.

## Tool-call and wall-clock count actually used

- **Tool calls: 9** (all `Bash`; no Read/Write/Edit, no MCP, no network tool). Target was ~40.
- **Wall clock: 3 min 57 s** — `03:11:41 UTC` → `03:15:38 UTC`. Target was ~40 min.

## Next concrete action

**One successor task, in lane 1: price the eight unmeasured rows' gene-space measurements as a retrieval work order, and rank them by how much of the 10–100 spread each one closes.** R1 shows eight inventory rows (51 specimens) whose scope rests on an author's word alone; R3 shows that the D2a/D2b and D4a/D4b splits — worth 62 specimens on the total — exist *only* because those measurements are absent. A worker with retrieval authority should, for each of rows 1, 3, 6, 7, 8, 9, 10 and 12, name the single artifact that would settle its scope (platform record, deposit manifest or Methods paragraph), state whether a route to it is already recorded as denied in `CLOSED-WORK.md`, and compute the residual spread after each hypothetical resolution — so the lane owner spends retrieval budget on the rows that actually move the number. **Row 8 ranks first on 12 specimens and row 12 first on 19, but row 12's route is the one W01c's R4 control already showed to be untrustworthy; that ordering is exactly what the successor must settle, and it must not be done by replaying a denied route.**
