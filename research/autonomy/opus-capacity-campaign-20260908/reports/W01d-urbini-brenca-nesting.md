> Collected by the campaign coordinator from this worker's in-response draft.
> Per-child runtime model evidence from the child transcript: `"model":"claude-opus-5"` (OBSERVED).

---

Sanity check: recount script exit 0 with all assertions passing, `git status --porcelain` shows only two other workers' untracked reports and nothing authored by me, and both papers' key sentences are quoted directly from the PMC renders I retrieved. Report follows.

---

# W01d — Urbini 2018 ⊆ Brenca 2019? A rubric-graded nesting test

## Worker

- **Worker:** W01d, LANE 1 refill (EMC expression/multiomic resources), successor to W01 / W01b / W01c.
- **Model identity — SELF-REPORT, NOT INDEPENDENTLY VERIFIED:** I report myself as Claude Opus 5 (`claude-opus-5`) under Claude Code 2.1.42, remote cloud. I did not and cannot observe the served model; the coordinator must extract the runtime model from the transcript. No finding below depends on which model produced it.
- **Write discipline:** READ-ONLY on the Git tree, honoured. All execution under `/tmp/claude-0/W01d/` and the session scratchpad. `git status --porcelain` at end shows only `?? .../reports/W01c-...md` and `?? .../reports/W13b-...md` — both other workers' files, pre-existing. **No file was created, modified or deleted by me inside `/home/user/Rare-cancers`.** No git write operation of any kind.
- **⚠ Frozen-commit discrepancy, reported not hidden:** COMMON-BRIEF names frozen read commit `92abbcb905cacf07f14b238db50d1b98f6590374`; `git rev-parse HEAD` at the end of my run returned **`b9a0257e6acff53ad22535cf2adf261313e0b250`**. The coordinator has committed to this checkout during the campaign. Everything I read from the tree is report text (W01c, W05, CLOSED-WORK, COMMON-BRIEF) whose content is unaffected, and my scientific conclusions derive from PubMed full texts, not from tree state. Flagging it so the coordinator knows the "frozen" commit is no longer frozen.

**`date -u` at end:** `Tue Sep  8 02:19:20 UTC 2026`. **Start:** I did not capture `date -u` as my first command — an honest procedural miss. The earliest timestamped artifact of this run is the scratch write of `urbini.txt`/`brenca.txt` at `Sep 8 02:17` UTC, so the run is ~5 minutes of wall clock, not a longer window reconstructed after the fact.

**`env | grep -i -E 'claude|anthropic|model' | sed -E 's/(TOKEN|KEY|SECRET)[^=]*=.*/\1=<redacted>/I'`** (verbatim, with five long proxy-exclusion variables — `no_proxy`, `NO_PROXY`, `GLOBAL_AGENT_NO_PROXY`, `JAVA_TOOL_OPTIONS`, `npm_config_noproxy` — filtered out for length; they match on the `anthropic` substring inside host lists and carry no model identity):

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

## Question

**Are Urbini 2018's five whole-transcriptome EMC cases a subset of Brenca 2019's twelve — and what is the corrected worldwide EMC specimen total under the answer?**

Open because W01c set its lower bound of 60 by *assuming* the worst case (full nesting) on a documented but never-tested risk, and W03 independently could not show Urbini's five distinct from the same group's sunitinib series. Two workers flagged the same risk from different directions; nobody tested it.

## Prior-work check

| command | what it showed |
|---|---|
| `grep -n -i -E "urbini\|brenca\|29937513\|31020999" -r reports/ CLOSED-WORK.md WAVE-LOG.md` | 40+ hits across W01, W01b, W01c, W03, W05, W05b, W06, W12, W13b, W20, W20b. **No worker has compared the two case sets.** W01b pursued Brenca's *accession* (14 routes, unrecovered); W03 pursued Urbini's *breakpoints*; W01c *assumed* nesting rather than testing it. The nesting question itself is unasked in the tree. |
| `sed -n '1,200p' reports/W05-patient-independence-audit.md` | The four-tier rubric, applied below unrelaxed. W05's row 8 records "Brenca case identities — CLOSED, unresolved." |
| `cat CLOSED-WORK.md` (41.9 KB, read in full) | "Brenca: case identities unresolved." |
| `sed -n '105,200p' reports/W01c-emc-deposit-literature-inventory.md` | The 13-study/84-specimen table and the 60–84 / 32–51 bands, transcribed exactly into my recount script. |

**Closed items I confirm I am not replaying.** I made **no** archive or bibliographic API call — Europe PMC, Crossref, ELink, ArrayExpress, ENA, GEO, mdpi.com, peerj.com all untouched; that branch is closed by W01b and re-probing it is waste. I did not attempt Brenca's or Urbini's **case identities** (names, records, hospital IDs) — I tested only whether the two *published case sets* intersect, which is a distinct question about dataset provenance and is what the dispatch authorises. I did not touch Hofvander/EGA, the Davis negative, promoter transfer, methylation, or the retained NR4A Perspective refusal. **No content-policy refusal was encountered in this run.**

## Method / inputs

According to PubMed, both full texts were retrieved this session with the PubMed MCP `get_full_text_article` tool, and both metadata records with `get_article_metadata`:

- Urbini M, Indio V, Astolfi A, *et al.* *Identification of an Actionable Mutation of KIT in a Case of Extraskeletal Myxoid Chondrosarcoma.* **Int J Mol Sci** 2018;19(7):1855. PMID 29937513, PMC6073125. [DOI](https://doi.org/10.3390/ijms19071855) — full text 9,244 characters.
- Brenca M, Stacchiotti S, Fassetta K, *et al.* *NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas.* **J Pathol** 2019;249(1):90–101. PMID 31020999, PMC6766969. [DOI](https://doi.org/10.1002/path.5284) — full text 35,201 characters.

Both saved to scratch (`/tmp/.../scratchpad/urbini.txt`, `brenca.txt`) and swept with `grep`. Counting in `/tmp/claude-0/W01d/nesting_recount.py`, Python 3.11.15, no network. **Throughout, `[…]` marks a gene name or citation the PMC renderer strips; I never fill one in silently.**

## Result

### R1 · Case-identifying particulars, from each paper's own words

| particular | **Urbini 2018 (n=5 WTS)** | **Brenca 2019 (n=12 WTS)** | disjoint? |
|---|---|---|---|
| **n profiled** | *"WTS was performed on five cases of EMC positive for[…]-fusion."* Methods: *"Five[…]-positive EMCs were collected for WTS analysis."* | *"The study was conducted on a series of 12 EMC…"*; *"seven EWSR1‐NR4A3 and five TAF15‐NR4A3 EMC were transcriptionally profiled by RNA‐Seq"* | n/a |
| **Institutions (tissue source)** | Ethics: *"approved by the local ethics committee… (27 May 2014, **Prot. INT 54/13**)."* `INT` = Istituto Nazionale dei Tumori. Author affiliations: Renne, Pilotti, Collini, Dagrada, Colombo, Gronchi, Casali, Stacchiotti — **Fondazione IRCCS Istituto Nazionale dei Tumori, Milan**; Dei Tos — **Treviso General Hospital**; Maestro — **CRO Aviano**; Astolfi/Indio/Pantaleo — Bologna | *"12 EMC retrieved from the pathology files of **Fondazione IRCCS Istituto Nazionale dei Tumori (Milano)**, the **Treviso Regional Hospital** and the IRCCS Istituto Ortopedico Rizzoli (Bologna)"* | 🔴 **NO — INT Milano and Treviso appear in both.** Rizzoli is the only source unique to Brenca. |
| **Pathologists handling the material** | Pilotti, Collini, Dagrada, Renne (INT); Dei Tos (Treviso) | *"centrally reviewed by two expert pathologists (**APDT** and **SP**)"* = **A**ngelo **P**aolo **D**ei **T**os and **S**ilvana **P**ilotti — both Urbini co-authors | 🔴 **NO — the same two pathologists.** |
| **Accrual window** | **Not stated.** Only the ethics approval date, 27 May 2014, which bounds nothing on its own | **Not stated anywhere in the article.** | ⚠ **UNKNOWN both sides** — cannot be disjoint |
| **Fusion partner per case** | All five described in EWSR1/NR4A3 exon terms; the partner gene name is stripped. #2,#3,#5 exon12/exon3; #4 exon13/exon3; #1 exon7/exon2 | **Table 1, complete:** cases 1–7 `EWSR1`, cases 8–12 `TAF15`. **No exon-level breakpoint reported for any case.** | ⚠ non-comparable — the two papers report fusion at **different resolutions**, so no case can be matched on architecture |
| **Age / sex / site per case** | ⛔ *"Sample characteristics are shown in[…]."* — **Urbini's Table 1 is not rendered in the PMC full text.** Zero demographics retrievable | **Table 1, complete:** F48 upper leg, M48 groin, M55 upper leg, M57 upper leg, F60 upper leg, M71 buttock, M76 upper leg (EWSR1); M50 buttock, M62 lower leg, M58 buttock, M39 lower leg, M50 (TAF15) | ⛔ **cannot be compared — one side is empty** |
| **Specimen type** | WTS RNA by RNeasy **Mini** Kit; DNA *"from fresh frozen tissue"* (Mini) vs *"for FFPE"* (Micro) for the separate 15-case cohort; Western blot on *"Frozen tumor samples"* → the five WTS cases read as **fresh-frozen** (inference, not stated) | **FFPE primary**: *"Total RNA was isolated from FFPE EMC as in[…] and from frozen samples as in[…]"*; *"For **five samples (four EWSR1 and one TAF15)** frozen material was also profiled"* | ⚠ partly overlapping |
| **Case numbering** | `#1`–`#5`, article-local | `CASE #1`–`#12`, article-local | ⛔ **not an identifier space** — two bare 1..n indices cannot be intersected |
| **Explicit non-overlap statement** | **None.** | **None.** | — |

**Author overlap (context, not evidence):** nine authors are shared — Astolfi, Indio, Pantaleo, Dagrada, Collini, Colombo, Gronchi, Casali, Stacchiotti — plus Dei Tos, Pilotti and Maestro. Maestro is senior author on both. Per W05's rubric and the dispatch, **shared authorship is not shared patients**; it is recorded because it establishes that the two papers draw on the *same institutional pathology files*, which is what defeats tier B.

### R2 · The positive-match hunt — the cheap direction, run hard, and what it found

I looked for a direct match on fusion architecture plus a demographic particular. **Four attempts, one interesting negative:**

1. **Fusion architecture.** Impossible in principle here: Urbini reports exon-level breakpoints and no partner-gene name (stripped); Brenca reports partner-gene names and no exon breakpoints. **The two papers' fusion descriptions do not share a coordinate system.** There is no case on which they can be compared.
2. **Demographics.** Impossible: Urbini's Table 1 is absent from the PMC render, so Urbini contributes zero ages, sexes or sites.
3. **Urbini case #1 — the one case with clinical particulars** (KIT p.D579del exon 11, epithelioid morphology with cords and strands, diffuse KIT IHC positivity, *"the same patient had been treated with sunitinib with a prolonged response"*). Brenca reports **no** mutation, treatment, or morphology data for any of its twelve, so #1 has nothing to match against. It ties Urbini #1 to the INT-Milano sunitinib series of 10 — corroborating W03 — but not to Brenca.
4. ⭐ **The seductive numeric coincidence, and its refutation.** Brenca profiled frozen material for exactly **five** samples, and says *"For fresh‐frozen samples libraries were prepared and analyzed as in[…]"* — a stripped citation to a prior method — while Astolfi, Indio and Pantaleo, the Bologna trio who performed Urbini's WTS, are Brenca co-authors. 5 = 5, same people, "as in [prior paper]". This looks like set identity. **It is not.** Brenca's five frozen samples are *"four EWSR1 and one TAF15"*; Urbini's five are stated as *"[…]-positive"* with breakpoints (exon12/exon3 ×3, exon13/exon3, exon7/exon2) that are the canonical EWSR1::NR4A3 architectures W03 already transcribed. **If Urbini's five are all EWSR1, the two five-sets cannot be the same five specimens** — Brenca's frozen five contains a TAF15 case that Urbini's cannot. Marked SECONDARY: the partner-gene name is stripped from Urbini's text, so "all five EWSR1" is an inference from breakpoint architecture and from the paper's framing against the known EWSR1 exon12/exon3 hotspot, not a quoted statement.

**No positive match was found. No stated non-overlap sentence exists in either paper.**

### R3 · Rubric verdict (W05's four tiers, unrelaxed)

| tier | requirement | met? |
|---|---|---|
| **A** | explicit non-overlap statement, **or** non-intersecting per-case identifiers published by both | ⛔ **NO.** Neither paper says anything about the other's series. Neither publishes a persistent identifier; both use article-local indices `#1..n`, which are not an identifier space. |
| **B** | disjoint institution **AND** disjoint accrual window **AND** disjoint identifier space — all three | ⛔ **NO, fails all three.** Institutions **overlap** (INT Milano + Treviso in both; same two central pathologists). Accrual windows are **stated by neither paper**. Identifier spaces are **not intersectable**. |
| **C** | disjoint demographics or a strict subset of B — **falsifier only** | one tier-C *mismatch* found (the frozen-set composition in R2.4), which under the rubric **licenses nothing**. No tier-C *match* found either, so overlap is not established. |
| **D** | no evidence | — this is where the pair sits. |

> ## Verdict: **UNKNOWN** — tier **D**
> Urbini 2018's five WTS cases are **neither shown to be nested inside Brenca 2019's twelve nor shown to be distinct from them.** Overlap is not established; independence is not established. The two papers draw on the *same institutional pathology files, reviewed by the same two pathologists*, which affirmatively **defeats** any independence claim; but no case can be matched, so nesting is not demonstrated.

**The specific missing evidence, named** (any one of these settles it):

1. ⭐ **Urbini 2018's Table 1** ("Sample characteristics"), which the PMC renderer drops. If it carries age/sex/site per case, a direct intersection against Brenca's Table 1 — 12 fully specified rows already in hand — decides the question in one step, in either direction. **This is the single highest-value missing item and it is one table.**
2. An accrual window in either paper (neither states one).
3. Brenca's per-case exon-level breakpoints, or Urbini's per-case partner-gene assignment, so the two fusion descriptions share a coordinate system.
4. A non-overlap sentence from either author group.

⚠ Under W05's asymmetry, **UNKNOWN here is not symmetric with "probably independent."** Overlap is the cheap verdict and it was not reached only because Urbini's demographics are unrendered — not because the evidence points away from it. The institutional and personnel evidence points *toward* overlap; it simply cannot carry a verdict on its own.

### R4 · Recomputed headline

| scenario | worldwide specimens profiled | obtainable without correspondence | grade |
|---|---|---|---|
| W01c point estimate, no deduplication | **84** | **32** | SECONDARY (transcribed from W01c) |
| Urbini ∩ Brenca = ∅ (EVIDENCED-INDEPENDENT) | 84 | 32 | not reached |
| Urbini ⊆ Brenca, full nesting (OVERLAPPING) | 79 | 32 | not reached |
| **UNKNOWN — the verdict actually reached** | **60 – 84** | **32 – 51** | **UNKNOWN** |

**Obtainable is unchanged at 32–51 in every scenario**, because neither Urbini (`UNKNOWN — no data-availability statement`) nor Brenca (`DEPOSITED, ACCESSION UNRECOVERABLE`) contributes a single specimen to the obtainable class. The nesting question moves only the numerator of the *generated* total.

> ### **W01c's headline STANDS UNCORRECTED: 60–84 specimens generated worldwide, 32–51 obtainable without correspondence.**

That is the honest result, and it is a complete one. What has changed is the *status* of the band, and this is the substantive product of the run: W01c's lower bound of 60 rested on an **untested assumption** flagged as "a real risk, not a hypothetical." It is now a **tested assumption that survived testing** — the worst case remains admissible under a rubric applied unrelaxed, the two case sets are confirmed to share institutions and pathologists rather than merely a senior author, and the one route that would have collapsed the band (a per-case match) is precisely characterised as blocked by one missing table. The band is the same; it is no longer a guess.

One arithmetic refinement, offered and then **declined**: if Urbini's five are all EWSR1 and all fresh-frozen, and Brenca profiled frozen material for only four EWSR1 cases, then at most four could coincide and the lower bound would rise 60 → 61. I do **not** apply this. Brenca says frozen material *"was also profiled"* for five samples — it does not say the other seven had no frozen material, and Urbini's specimen type is my inference from extraction kits, not a quoted statement. Two soft inferences do not move a published bound by one specimen.

## Validation evidence

**RUN.** Environment: Linux 6.18.44-fc-v24 x86_64, Python 3.11.15 (main, Mar 3 2026), bash. Working dir `/tmp/claude-0/W01d/` (execution) and the session scratchpad (text extraction). No network in any script.

| # | command | exit | key output |
|---|---|---|---|
| 1 | PubMed MCP `get_full_text_article(["PMC6073125","PMC6766969"])` | ok | Urbini 9,244 chars; Brenca 35,201 chars. Both saved to scratch. |
| 2 | PubMed MCP `get_article_metadata(["29937513","31020999"])` | ok (`count: 2`) | Full author lists with affiliations — the INT-Milano/Treviso/CRO-Aviano/Bologna overlap in R1 |
| 3 | `python3 -c` JSON split of the MCP result into `urbini.txt` / `brenca.txt` | **0** | `len 35201`, `len 9244` |
| 4 | `sed -n '17,150p' brenca.txt` | 0 | Brenca Table 1 **rendered in full** — 12 rows, partner/sex/age/site, transcribed verbatim in R1 |
| 5 | `cat urbini.txt` | 0 | Full article. Contains *"Sample characteristics are shown in."* — **Table 1 absent**, confirming W03's finding independently |
| 6 | `grep -n -i -E "ethic\|consent\|Helsinki\|INT \|institut\|frozen\|FFPE\|..." brenca.txt` | 0 | The pathology-files sentence, the APDT/SP central-review sentence, the "four EWSR1 and one TAF15" frozen sentence |
| 7 | `grep -n -iE "Urbini\|previously profiled\|not include\|distinct from\|..." brenca.txt urbini.txt` | 0 | **Two hits, both in urbini.txt, neither an overlap statement.** Brenca's reference list is absent from the PMC render (tail is supplementary-figure legends), so I could not check whether Brenca cites Urbini. Recorded as UNKNOWN, not as absence. |
| 8 | `python3 /tmp/claude-0/W01d/nesting_recount.py` | **0** | `total=84 obtainable=32`; `84 - 5 - 19 = 60`; `Band under UNKNOWN verdict: total 60-84; obtainable 32-51`; **`ALL ASSERTIONS PASSED`** (4 assertions on W01c's transcribed figures + 1 arithmetic-possibility check) |
| 9 | `git rev-parse HEAD; git status --porcelain` | 0 | `b9a0257e…` (≠ the brief's `92abbcb9…`, see Worker); porcelain lists only W01c's and W13b's untracked reports — nothing of mine |

**PROPOSED (NOT RUN):** fetch Urbini 2018 Table 1 from `mdpi.com` or the PMC HTML. **Not run, deliberately** — W03 recorded mdpi.com blocked, and my dispatch closes the archive/bibliographic transport branch. Re-probing it would replay a denied route.

**No test suite was run** — this changes no code and no shared state; per the brief I did not run `scripts/preflight.sh`. Nothing here is a skipped check reported as a pass.

## Limitations

- **This establishes neither overlap nor independence.** "Not shown distinct" is not "shown to be the same." I assert no duplication between the two series.
- **One side of the comparison is empty.** Brenca's per-case table is complete; Urbini's is unrendered. The verdict is therefore partly an artifact of a PMC renderer, not solely of what the authors published — Urbini's Table 1 exists in the published article and I could not read it. **An unread table is UNKNOWN, not absent.**
- **"All five Urbini cases are EWSR1" is an inference** from exon architecture and framing, since the gene name is stripped. R2.4's refutation of the 5=5 identity depends on it and is graded SECONDARY.
- **Specimens, not patients**, throughout. 84, 79 and 60 count profiled specimens. No cohort was added or invented; no patient-level claim is made.
- **No clinical claim.** Urbini case #1's sunitinib response and KIT mutation are quoted as published case particulars used for matching; they establish nothing about EMC treatment.
- **Case identity was not attempted** and remains CLOSED-unresolved per `CLOSED-WORK.md`. I tested dataset nesting only.
- The recount's inputs are **transcribed from W01c's table**, not re-derived from the 13 primary sources; its assertions verify my transcription reproduces W01c's published totals, not that those totals are correct.

## Stop condition

**Set:** a rubric-graded nesting verdict with quoted evidence from both papers, and W01c's headline either corrected or explicitly left standing.
**MET.** Verdict **UNKNOWN at tier D**, with per-case particulars quoted from both articles, the four missing-evidence items named, a positive-match hunt run in four directions and reported as negative (including one refuted numeric coincidence), and W01c's 60–84 / 32–51 headline **explicitly left standing** with its lower-bound assumption converted from untested to tested-and-surviving.

## Tool-call and wall-clock count actually used

**11 tool calls** (2 PubMed MCP, 1 ToolSearch, 8 Bash) against the ~40 target. **Wall clock ~5 minutes** (earliest artifact 02:17 UTC, end 02:19:20 UTC) against the ~40-minute target. Returning immediately on stop condition; no padding.

## Next concrete action

**Recover Urbini 2018's Table 1 and intersect it against Brenca 2019's Table 1 — which is already fully transcribed in R1 above and needs no further retrieval.** This is a single-table fetch that converts a tier-D UNKNOWN into a tier-A or tier-C-falsifier verdict in one step, and it is the *only* action that can do so. It is **not** available to a read-only sandbox worker (mdpi.com blocked, PMC render strips the table), so it belongs on the GitHub Actions escape hatch alongside the Europe PMC `accessionIds` query W01b already queued — one runner job serves both, roughly 15 minutes, no spending. **If that route is not authorised, this lane's honest position is that the question is closed as UNKNOWN from here** and the 60–84 band should be reported with its lower bound labelled "worst-case nesting, tested and not excluded" rather than silently.

result: Urbini 2018's five EMC transcriptomes vs Brenca 2019's twelve graded **UNKNOWN at tier D** — the two draw on the same INT-Milano/Treviso pathology files reviewed by the same two pathologists (so tier B fails on all three conditions and no independence claim survives), yet no case can be matched because Urbini's demographics table is unrendered and the two papers report fusions at incompatible resolutions; the tempting 5-frozen=5-WTS coincidence is refuted by partner composition; **W01c's 60–84 specimen / 32–51 obtainable headline stands uncorrected**, with its lower-bound nesting assumption now tested rather than assumed, and one missing table named as the single item that would settle it.
